"""
Dar es Salaam Stock Exchange (DSE) FIX 4.2 adapter.

Exchange details:
  Trading hours: 10:00–14:00 EAT (UTC+3)
  Settlement:    T+3
  Currency:      TZS (Tanzanian Shilling)
  FIX gateway:   fix.dse.co.tz:9888
  Taker fee:     30 bps
"""
import logging
import threading
from typing import Optional

from tools.venue_adapters.base_adapter import BaseExchangeAdapter, VenueAdapterConfig
from tools.fix_engine import (
    FIXSession, build_new_order_single, build_market_data_request,
    SIDE_BUY, SIDE_SELL, ORD_TYPE_LIMIT, ORD_TYPE_MARKET,
)

logger = logging.getLogger("dse_adapter")

DSE_CONFIG = VenueAdapterConfig(
    name="DSE",
    host="fix.dse.co.tz",
    port=9888,
    sender_comp_id="BROKER_TZ",
    target_comp_id="DSE_TRADING",
    currency="TZS",
    taker_fee=0.0030,
    latency_ms=18.0,
    enabled=True,
)

# TZS is a high-nominal currency; prices typically 100–15000
_TICK_TABLE = [
    (100.0,       1.0),
    (500.0,       5.0),
    (2000.0,      10.0),
    (10000.0,     50.0),
    (float("inf"), 100.0),
]


def dse_tick_size(price: float) -> float:
    for threshold, tick in _TICK_TABLE:
        if price < threshold:
            return tick
    return 100.0


def _round_to_tick(price: float) -> float:
    tick = dse_tick_size(price)
    return round(round(price / tick) * tick, 6)


class DSEAdapter(BaseExchangeAdapter):
    def __init__(self, config: VenueAdapterConfig = None):
        super().__init__(config or DSE_CONFIG)
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
        logger.info("DSE: Connecting to %s:%s", self.config.host, self.config.port)
        self._session.logged_on = True
        self._connected = True
        self._hb_stop.clear()
        self._hb_thread = threading.Thread(
            target=self._heartbeat_loop, name="hb-dse", daemon=True
        )
        self._hb_thread.start()
        logger.info("DSE: Session established")
        return True

    def disconnect(self):
        self._hb_stop.set()
        self._session.logged_on = False
        self._connected = False
        logger.info("DSE: Disconnected")

    def _heartbeat_loop(self):
        interval = self._session.heartbeat_interval
        while not self._hb_stop.wait(timeout=interval):
            try:
                self.send_heartbeat()
            except Exception as exc:
                logger.warning("DSE: Heartbeat error: %s", exc)

    def subscribe_market_data(self, symbol: str) -> bool:
        if not self._connected:
            logger.warning("DSE: Cannot subscribe %s — not connected", symbol)
            return False
        msg = build_market_data_request(
            req_id=f"MDR-{symbol}",
            symbol=symbol,
            sender=self._session.sender,
            target=self._session.target,
            seq_num=self._session.next_seq(),
        )
        self._subscribed_symbols.add(symbol)
        logger.info("DSE: Subscribed market data for %s", symbol)
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
            logger.warning("DSE: Cannot send order — not connected")
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
        logger.info(
            "DSE: Order [%s] %s %dx%s @ %s TZS",
            order_id, side.upper(), int(quantity), symbol, "MKT" if price is None else price,
        )
        return True

    def send_heartbeat(self):
        if self._session.is_heartbeat_due():
            hb = self._session.heartbeat_message()
            self._session.record_heartbeat()

    @property
    def is_connected(self) -> bool:
        return self._connected

    def get_status(self) -> dict:
        return {
            "venue": "DSE",
            "connected": self._connected,
            "session_logged_on": self._session.logged_on,
            "host": self.config.host,
            "subscribed_symbols": list(self._subscribed_symbols),
            "currency": self.config.currency,
            "taker_fee_bps": self.config.taker_fee * 10_000,
        }
