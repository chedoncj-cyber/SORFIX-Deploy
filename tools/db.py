"""
SQLite persistence layer — orders survive server restarts.
Uses WAL mode for concurrent read performance; single writer thread via Lock.
"""
import json
import logging
import sqlite3
import threading
import time
from pathlib import Path
from typing import Optional

logger = logging.getLogger("order_db")

_DEFAULT_PATH = Path(__file__).parent.parent / "data" / "orders.db"


def _dict_factory(cursor, row):
    return {col[0]: val for col, val in zip(cursor.description, row)}


class OrderDB:
    def __init__(self, db_path: Path = None):
        self._path = Path(db_path or _DEFAULT_PATH)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn = self._connect()
        self._create_schema()
        logger.info("OrderDB initialized at %s", self._path)

    # ------------------------------------------------------------------ #
    # Public API                                                           #
    # ------------------------------------------------------------------ #

    def save(self, order_id: str, order_data: dict):
        """Insert or replace a completed order record."""
        with self._lock:
            symbol = order_data.get("routing", {}).get("symbol", "")
            side   = order_data.get("side", "")
            ts     = order_data.get("timestamp", time.time())
            total_filled  = order_data.get("total_filled", 0.0)
            total_cost    = order_data.get("total_cost", 0.0)
            success       = int(order_data.get("success", False))
            fill_ratio    = order_data.get("fill_ratio", 0.0)
            vwap          = order_data.get("vwap")
            primary_venue = order_data.get("routing", {}).get("primary_venue", "")
            is_split      = int(order_data.get("routing", {}).get("is_split", False))
            routing_lat   = order_data.get("routing", {}).get("routing_latency_us", 0.0)
            blob          = json.dumps(order_data)

            self._conn.execute(
                """
                INSERT OR REPLACE INTO orders
                  (order_id, symbol, side, timestamp, total_filled, total_cost,
                   success, fill_ratio, vwap, primary_venue, is_split,
                   routing_latency_us, payload)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (order_id, symbol, side, ts, total_filled, total_cost,
                 success, fill_ratio, vwap, primary_venue, is_split,
                 routing_lat, blob),
            )
            self._conn.commit()

    def get(self, order_id: str) -> Optional[dict]:
        with self._lock:
            cur = self._conn.execute(
                "SELECT payload FROM orders WHERE order_id=?", (order_id,)
            )
            row = cur.fetchone()
            return json.loads(row["payload"]) if row else None

    def recent(self, limit: int = 50) -> list:
        with self._lock:
            cur = self._conn.execute(
                "SELECT payload FROM orders ORDER BY timestamp DESC LIMIT ?", (limit,)
            )
            return [json.loads(r["payload"]) for r in cur.fetchall()]

    def count(self) -> int:
        with self._lock:
            cur = self._conn.execute("SELECT COUNT(*) AS n FROM orders")
            return cur.fetchone()["n"]

    def tca(self, symbol: str = None, limit: int = 200) -> list:
        """Return TCA-relevant columns for analytics; optionally filter by symbol."""
        with self._lock:
            if symbol:
                cur = self._conn.execute(
                    """
                    SELECT order_id, symbol, side, timestamp, total_filled,
                           total_cost, fill_ratio, vwap, primary_venue,
                           is_split, routing_latency_us, success
                    FROM orders
                    WHERE symbol=?
                    ORDER BY timestamp DESC LIMIT ?
                    """,
                    (symbol.upper(), limit),
                )
            else:
                cur = self._conn.execute(
                    """
                    SELECT order_id, symbol, side, timestamp, total_filled,
                           total_cost, fill_ratio, vwap, primary_venue,
                           is_split, routing_latency_us, success
                    FROM orders ORDER BY timestamp DESC LIMIT ?
                    """,
                    (limit,),
                )
            rows = cur.fetchall()
            return [dict(r) for r in rows]

    def close(self):
        with self._lock:
            self._conn.close()

    # ------------------------------------------------------------------ #
    # Internal                                                             #
    # ------------------------------------------------------------------ #

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._path), check_same_thread=False)
        conn.row_factory = _dict_factory
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn

    def _create_schema(self):
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS orders (
                order_id          TEXT PRIMARY KEY,
                symbol            TEXT NOT NULL,
                side              TEXT NOT NULL,
                timestamp         REAL NOT NULL,
                total_filled      REAL NOT NULL,
                total_cost        REAL NOT NULL,
                success           INTEGER NOT NULL,
                fill_ratio        REAL NOT NULL,
                vwap              REAL,
                primary_venue     TEXT NOT NULL,
                is_split          INTEGER NOT NULL,
                routing_latency_us REAL NOT NULL,
                payload           TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_orders_ts     ON orders(timestamp DESC);
            CREATE INDEX IF NOT EXISTS idx_orders_symbol ON orders(symbol, timestamp DESC);
            CREATE INDEX IF NOT EXISTS idx_orders_venue  ON orders(primary_venue, timestamp DESC);
            """
        )
        self._conn.commit()
