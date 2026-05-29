"""
Abstract base class for all exchange adapters.
Each venue adapter must implement connect/disconnect/subscribe/send_order.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class VenueAdapterConfig:
    name: str
    host: str
    port: int
    sender_comp_id: str
    target_comp_id: str
    currency: str
    taker_fee: float
    latency_ms: float
    enabled: bool = True


class BaseExchangeAdapter(ABC):
    def __init__(self, config: VenueAdapterConfig):
        self.config = config

    @property
    def venue_name(self) -> str:
        return self.config.name

    @abstractmethod
    def connect(self) -> bool:
        """Establish TCP connection and send FIX Logon."""

    @abstractmethod
    def disconnect(self):
        """Send FIX Logout and close connection."""

    @abstractmethod
    def subscribe_market_data(self, symbol: str) -> bool:
        """Send MarketDataRequest (V) for a symbol."""

    @abstractmethod
    def send_order(
        self,
        order_id: str,
        symbol: str,
        side: str,
        quantity: float,
        price: Optional[float],
    ) -> bool:
        """Send a NewOrderSingle (D) FIX message."""

    def get_venue_config(self) -> dict:
        return {
            "name": self.config.name,
            "host": self.config.host,
            "port": self.config.port,
            "currency": self.config.currency,
            "taker_fee": self.config.taker_fee,
            "latency_ms": self.config.latency_ms,
            "enabled": self.config.enabled,
        }
