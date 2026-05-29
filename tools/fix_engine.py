"""
FIX protocol message builder and session manager.
Implements FIX 4.2 encoding natively — no C dependencies required.
To use simplefix instead, install it and replace build_raw_fix with simplefix.FixMessage.
"""
import logging
import time
import threading
from typing import Optional, Dict

FIX_VERSION = b"FIX.4.2"

MSG_LOGON            = b"A"
MSG_LOGOUT           = b"5"
MSG_HEARTBEAT        = b"0"
MSG_NEW_ORDER_SINGLE = b"D"
MSG_EXECUTION_REPORT = b"8"
MSG_ORDER_CANCEL     = b"F"
MSG_MARKET_DATA_REQ  = b"V"
MSG_MARKET_DATA_SNAP = b"W"

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
    """Minimal FIX encoder that works without simplefix installed."""
    body = b""
    body += _encode_pair(35, msg_type)
    body += _encode_pair(49, sender)
    body += _encode_pair(56, target)
    body += _encode_pair(34, seq_num)   # MsgSeqNum — required by FIX protocol
    body += _encode_pair(52, time.strftime("%Y%m%d-%H:%M:%S", time.gmtime()))
    for tag, value in fields:
        body += _encode_pair(tag, value)
    header = _encode_pair(8, FIX_VERSION) + _encode_pair(9, len(body))
    raw = header + body
    checksum = sum(raw) % 256
    raw += _encode_pair(10, f"{checksum:03d}")
    return raw


def build_logon(sender: str, target: str, heartbeat_interval: int = 30, seq_num: int = 1) -> bytes:
    return build_raw_fix(MSG_LOGON, sender, target, [
        (108, heartbeat_interval),
        (98, 0),
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
) -> bytes:
    fields = [
        (11, cl_ord_id),
        (21, b"1"),      # HandlInst = Automated execution — required in FIX 4.2 NewOrderSingle
        (55, symbol),
        (54, side),
        (60, time.strftime("%Y%m%d-%H:%M:%S", time.gmtime())),  # TransactTime
        (38, int(quantity)),
        (40, ord_type),
        (59, tif),
        (15, currency),
    ]
    if price is not None:
        fields.append((44, f"{price:.4f}"))
    return build_raw_fix(MSG_NEW_ORDER_SINGLE, sender, target, fields, seq_num=seq_num)


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
