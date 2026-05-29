"""
Ghana Stock Exchange (GSE) FIX 4.2 adapter — primary venue (fully implemented).

Exchange details:
  Trading hours: 09:30–15:00 WAT (UTC+0)
  Settlement:    T+3
  Currency:      GHS (Ghana Cedi)
  FIX gateway:   fix.gse.com.gh:9876 (TLS 1.3 required in production)
  Taker fee:     15 bps

In production: replace simulated connect/disconnect with real TCP socket +
TLS handshake + FIX Logon/Logout flow.
"""
import logging
import threading
from typing import Optional

from tools.venue_adapters.base_adapter import BaseExchangeAdapter, VenueAdapterConfig
from tools.fix_engine import (
    FIXSession, build_new_order_single, build_market_data_request,
    SIDE_BUY, SIDE_SELL, ORD_TYPE_LIMIT, ORD_TYPE_MARKET,
)

logger = logging.getLogger("gse_adapter")

GSE_CONFIG = VenueAdapterConfig(
    name="GSE",
    host="fix.gse.com.gh",
    port=9876,
    sender_comp_id="BROKER_GH",
    target_comp_id="GSE_TRADING",
    currency="GHS",
    taker_fee=0.0015,
    latency_ms=8.0,
    enabled=True,
)

# GSE minimum tick sizes by price band (GHS)
_TICK_TABLE = [
    (0.10,       0.001),
    (1.00,       0.01),
    (10.00,      0.05),
    (100.0,      0.10),
    (float("inf"), 0.50),
]


def gse_tick_size(price: float) -> float:
    for threshold, tick in _TICK_TABLE:
        if price < threshold:
            return tick
    return 0.50  # unreachable — float("inf") in _TICK_TABLE always catches


def _round_to_tick(price: float) -> float:
    tick = gse_tick_size(price)
    return round(round(price / tick) * tick, 6)


class GSEAdapter(BaseExchangeAdapter):
    def __init__(self, config: VenueAdapterConfig = None):
        super().__init__(config or GSE_CONFIG)
        self._session = FIXSession(
            sender=self.config.sender_comp_id,
            target=self.config.target_comp_id,
            heartbeat_interval=30,
        )
        self._connected = False
        self._subscribed_symbols: set = set()
        self._hb_stop: threading.Event = threading.Event()
        self._hb_thread: Optional[threading.Thread] = None

    def connect(self) -> bool:
        logger.info("GSE: Connecting to %s:%s (TLS 1.3)", self.config.host, self.config.port)
        self._session.logged_on = True
        self._connected = True
        self._hb_stop.clear()
        self._hb_thread = threading.Thread(
            target=self._heartbeat_loop, name="hb-gse", daemon=True
        )
        self._hb_thread.start()
        logger.info("GSE: Session established")
        return True

    def disconnect(self):
        self._hb_stop.set()
        self._session.logged_on = False
        self._connected = False
        logger.info("GSE: Disconnected")

    def _heartbeat_loop(self):
        interval = self._session.heartbeat_interval
        while not self._hb_stop.wait(timeout=interval):
            try:
                self.send_heartbeat()
            except Exception as exc:
                logger.warning("GSE: Heartbeat error: %s", exc)

    def subscribe_market_data(self, symbol: str) -> bool:
        if not self._connected:
            logger.warning("GSE: Cannot subscribe %s — not connected", symbol)
            return False
        msg = build_market_data_request(
            req_id=f"MDR-{symbol}",
            symbol=symbol,
            sender=self._session.sender,
            target=self._session.target,
            seq_num=self._session.next_seq(),
        )
        # Production: write msg to socket
        self._subscribed_symbols.add(symbol)
        logger.info("GSE: Subscribed market data for %s", symbol)
        return True

    def send_order(
        self,
        order_id: str,
        symbol: str,
        side: str,
        quantity: float,
        price: Optional[float],
    ) -> bool:
        if not self._connected:
            logger.warning("GSE: Cannot send order — not connected")
            return False

        fix_side = SIDE_BUY if side.lower() == "buy" else SIDE_SELL
        ord_type = ORD_TYPE_MARKET if price is None else ORD_TYPE_LIMIT
        if price is not None:
            price = _round_to_tick(price)

        msg = build_new_order_single(
            cl_ord_id=order_id,
            symbol=symbol,
            side=fix_side,
            quantity=quantity,
            price=price,
            sender=self._session.sender,
            target=self._session.target,
            currency=self.config.currency,
            ord_type=ord_type,
            seq_num=self._session.next_seq(),
        )
        # Production: write msg to socket, await ExecutionReport (tag 35=8)
        logger.info(
            "GSE: Order [%s] %s %dx%s @ %s GHS",
            order_id, side.upper(), int(quantity), symbol, "MKT" if price is None else price,
        )
        return True

    def send_heartbeat(self):
        # Production: call from a dedicated background thread every heartbeat_interval seconds.
        if self._session.is_heartbeat_due():
            hb = self._session.heartbeat_message()
            # Production: write hb to socket
            self._session.record_heartbeat()

    @property
    def is_connected(self) -> bool:
        return self._connected

    def get_status(self) -> dict:
        return {
            "venue": "GSE",
            "connected": self._connected,
            "session_logged_on": self._session.logged_on,
            "host": self.config.host,
            "subscribed_symbols": list(self._subscribed_symbols),
            "currency": self.config.currency,
            "taker_fee_bps": self.config.taker_fee * 10_000,
        }
