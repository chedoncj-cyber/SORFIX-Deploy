"""
FIX protocol message builder and session manager.
Implements FIX 5.0 SP2 / FIXT.1.1 encoding natively — no C dependencies required.
Wire format: BeginString=FIXT.1.1, ApplVerID=9 (FIX50SP2) on every application message.
To use simplefix instead, install it and replace build_raw_fix with simplefix.FixMessage.
"""
import logging
import time
import threading
from typing import Optional, Dict, List

# ── Transport / Application version ───────────────────────────────────
FIX_VERSION  = b"FIXT.1.1"   # tag 8  — FIXT transport layer (FIX 5.0+)
APPL_VER_ID  = b"9"           # tag 1128 — FIX50SP2 application version

# ── Session-level message types ────────────────────────────────────────
MSG_LOGON            = b"A"
MSG_LOGOUT           = b"5"
MSG_HEARTBEAT        = b"0"
MSG_TEST_REQUEST     = b"1"
MSG_RESEND_REQUEST   = b"2"
MSG_REJECT           = b"3"
MSG_SEQUENCE_RESET   = b"4"

# ── Application message types ──────────────────────────────────────────
MSG_NEW_ORDER_SINGLE = b"D"
MSG_NEW_ORDER_LIST   = b"E"   # basket / portfolio orders
MSG_EXECUTION_REPORT = b"8"
MSG_ORDER_CANCEL     = b"F"
MSG_ORDER_CANCEL_REPLACE = b"G"
MSG_IOI              = b"6"   # Indication of Interest
MSG_TRADE_CAPTURE    = b"AE"  # Trade Capture Report (FIX 5.0)
MSG_MARKET_DATA_REQ  = b"V"
MSG_MARKET_DATA_SNAP = b"W"
MSG_MARKET_DATA_INC  = b"X"   # incremental refresh (FIX 5.0)

SIDE_BUY  = b"1"
SIDE_SELL = b"2"

ORD_TYPE_MARKET = b"1"
ORD_TYPE_LIMIT  = b"2"

TIF_DAY = b"0"
TIF_GTC = b"1"
TIF_IOC = b"3"
TIF_FOK = b"4"


def _encode_pair(tag: int, value) -> bytes:
    if isinstance(value, bytes):
        v = value
    elif isinstance(value, str):
        v = value.encode()
    else:
        v = str(value).encode()
    return f"{tag}=".encode() + v + b"\x01"


def build_raw_fix(msg_type: bytes, sender: str, target: str, fields: list, seq_num: int = 1) -> bytes:
    """FIX 5.0 SP2 / FIXT.1.1 encoder — no external dependencies required."""
    body = b""
    body += _encode_pair(35, msg_type)
    body += _encode_pair(49, sender)
    body += _encode_pair(56, target)
    body += _encode_pair(34, seq_num)
    body += _encode_pair(52, time.strftime("%Y%m%d-%H:%M:%S", time.gmtime()))
    # FIX 5.0: ApplVerID (1128) identifies the application-layer version on every message
    body += _encode_pair(1128, APPL_VER_ID)
    for tag, value in fields:
        body += _encode_pair(tag, value)
    header = _encode_pair(8, FIX_VERSION) + _encode_pair(9, len(body))
    raw = header + body
    checksum = sum(raw) % 256
    raw += _encode_pair(10, f"{checksum:03d}")
    return raw


def build_logon(sender: str, target: str, heartbeat_interval: int = 30, seq_num: int = 1) -> bytes:
    return build_raw_fix(MSG_LOGON, sender, target, [
        (98, 0),            # EncryptMethod = None
        (108, heartbeat_interval),
        (1137, APPL_VER_ID), # DefaultApplVerID — required by FIXT.1.1 Logon
    ], seq_num=seq_num)


def build_new_order_single(
    cl_ord_id: str,
    symbol: str,
    side: bytes,
    quantity: float,
    price: Optional[float],
    sender: str,
    target: str,
    currency: str = "GHS",
    ord_type: bytes = ORD_TYPE_LIMIT,
    tif: bytes = TIF_DAY,
    seq_num: int = 1,
    display_qty: Optional[float] = None,  # FIX 5.0 tag 1138 — iceberg visible qty
) -> bytes:
    fields = [
        (11, cl_ord_id),
        # HandlInst (21) is optional in FIX 5.0 — omitted
        (55, symbol),
        (54, side),
        (60, time.strftime("%Y%m%d-%H:%M:%S", time.gmtime())),
        (38, int(quantity)),
        (40, ord_type),
        (59, tif),
        (15, currency),
    ]
    if price is not None:
        fields.append((44, f"{price:.4f}"))
    if display_qty is not None:
        fields.append((1138, int(display_qty)))  # DisplayQty — iceberg reserve
    return build_raw_fix(MSG_NEW_ORDER_SINGLE, sender, target, fields, seq_num=seq_num)


def build_new_order_list(
    list_id: str,
    orders: List[dict],
    sender: str,
    target: str,
    seq_num: int = 1,
) -> bytes:
    """FIX 5.0 NewOrderList (35=E) — basket / portfolio execution.

    Each dict in orders must have: cl_ord_id, symbol, side, quantity, price, currency.
    Optional keys: ord_type, tif.
    """
    fields: list = [
        (66, list_id),          # ListID
        (394, 1),               # BidType = Disclosed (1)
        (68, len(orders)),      # TotNoOrders
    ]
    for i, o in enumerate(orders, start=1):
        fields += [
            (67, i),                                        # ListSeqNo
            (11, o["cl_ord_id"]),
            (55, o["symbol"]),
            (54, o["side"]),
            (38, int(o["quantity"])),
            (40, o.get("ord_type", ORD_TYPE_LIMIT)),
            (59, o.get("tif", TIF_DAY)),
            (44, f"{o['price']:.4f}"),
            (15, o.get("currency", "USD")),
            (60, time.strftime("%Y%m%d-%H:%M:%S", time.gmtime())),
        ]
    return build_raw_fix(MSG_NEW_ORDER_LIST, sender, target, fields, seq_num=seq_num)


def build_ioi(
    ioi_id: str,
    symbol: str,
    side: bytes,
    quantity: float,
    sender: str,
    target: str,
    price: Optional[float] = None,
    ioi_qty_type: bytes = b"0",  # 0=Units, 1=Percent, 2=Undisclosed
    seq_num: int = 1,
) -> bytes:
    """FIX 5.0 IOI message (35=6) — Indication of Interest for the IOI Board."""
    fields = [
        (23, ioi_id),           # IOIID
        (28, b"N"),             # IOITransType = New
        (55, symbol),
        (54, side),
        (27, ioi_qty_type),     # IOIQty type
        (53, int(quantity)),    # Quantity
        (60, time.strftime("%Y%m%d-%H:%M:%S", time.gmtime())),
    ]
    if price is not None:
        fields.append((44, f"{price:.4f}"))
    return build_raw_fix(MSG_IOI, sender, target, fields, seq_num=seq_num)


def build_quote_request(
    req_id: str,
    symbol: str,         # FX pair e.g. "EUR/USD"
    currency: str,       # base currency e.g. "EUR"
    quantity: float,
    sender: str,
    target: str,
    settle_date: Optional[str] = None,
    seq_num: int = 1,
) -> bytes:
    """FIX 5.0 QuoteRequest (35=R) — used to request FX spot/forward quotes."""
    fields = [
        (131, req_id),           # QuoteReqID
        (146, 1),                # NoRelatedSym
        (55,  symbol),           # Symbol
        (167, "FOR"),            # SecurityType = Foreign Exchange
        (38,  int(quantity)),    # OrderQty (base currency amount)
        (15,  currency),         # Currency (base)
        (63,  "0"),              # SettlType = Regular
    ]
    if settle_date:
        fields.append((64, settle_date))
    return build_raw_fix(b"R", sender, target, fields, seq_num=seq_num)


def build_quote(
    quote_id: str,
    req_id: str,
    symbol: str,
    bid_px: Optional[float],
    ask_px: Optional[float],
    sender: str,
    target: str,
    currency: str = "USD",
    settle_date: Optional[str] = None,
    seq_num: int = 1,
) -> bytes:
    """FIX 5.0 Quote (35=S) — sends a two-way FX price quote back to the OMS."""
    fields = [
        (117, quote_id),         # QuoteID
        (131, req_id),           # QuoteReqID
        (55,  symbol),           # Symbol
        (167, "FOR"),            # SecurityType
        (15,  currency),         # Currency
    ]
    if bid_px is not None:
        fields.append((132, f"{bid_px:.5f}"))  # BidPx
    if ask_px is not None:
        fields.append((133, f"{ask_px:.5f}"))  # OfferPx
    if settle_date:
        fields.append((64, settle_date))
    return build_raw_fix(b"S", sender, target, fields, seq_num=seq_num)


def build_market_data_request(
    req_id: str,
    symbol: str,
    sender: str,
    target: str,
    depth: int = 5,
    seq_num: int = 1,
) -> bytes:
    return build_raw_fix(MSG_MARKET_DATA_REQ, sender, target, [
        (262, req_id),   # MDReqID
        (263, 1),        # SubscriptionRequestType = Snapshot+Updates
        (264, depth),    # MarketDepth
        (146, 1),        # NoRelatedSym
        (55, symbol),    # Symbol
    ], seq_num=seq_num)


def build_heartbeat(sender: str, target: str, test_req_id: Optional[str] = None, seq_num: int = 1) -> bytes:
    fields = [(112, test_req_id)] if test_req_id else []
    return build_raw_fix(MSG_HEARTBEAT, sender, target, fields, seq_num=seq_num)


_parse_logger = logging.getLogger("fix_engine.parse")

def parse_fix_message(raw: bytes) -> Dict[int, str]:
    result = {}
    try:
        for field in raw.split(b"\x01"):
            if b"=" in field:
                tag_b, val_b = field.split(b"=", 1)
                result[int(tag_b)] = val_b.decode(errors="replace")
    except Exception as exc:
        _parse_logger.debug("Failed to parse FIX message: %s", exc)
    return result


class FIXSession:
    def __init__(self, sender: str, target: str, heartbeat_interval: int = 30):
        self.sender = sender
        self.target = target
        self.heartbeat_interval = heartbeat_interval
        self.seq_num = 1
        self.logged_on = False
        self._lock = threading.Lock()
        self._last_heartbeat = time.time()

    def next_seq(self) -> int:
        with self._lock:
            num = self.seq_num
            self.seq_num += 1
            return num

    def is_heartbeat_due(self) -> bool:
        return time.time() - self._last_heartbeat >= self.heartbeat_interval

    def record_heartbeat(self):
        self._last_heartbeat = time.time()

    def logon_message(self) -> bytes:
        return build_logon(self.sender, self.target, self.heartbeat_interval, seq_num=self.next_seq())

    def heartbeat_message(self) -> bytes:
        return build_heartbeat(self.sender, self.target, seq_num=self.next_seq())
