"""
OMS/EMS Integration Bridge.
Closes the gap with Bloomberg EMSX, Charles River, Fidessa, and similar
buy-side Order Management Systems.

Two connectivity modes:
  1. REST bridge  — OMS POSTs a JSON order to POST /oms/inbound.
                    Response includes full execution details.
                    Optional webhook: register a callback URL to receive
                    async ExecutionReport pushes.

  2. FIX acceptor — OMS connects as FIX initiator to SORFIX's acceptor port
                    (default 9095 for World SORFIX, 9094 for Pan SORFIX).
                    SORFIX receives 35=D (NewOrderSingle), routes it via SOR,
                    and sends 35=8 (ExecutionReport) back to the OMS.

Usage (REST):
    bridge = OMSBridge(execution_engine=engine)
    result = await bridge.inbound_order(oms_id="bloomberg", payload={...})

Usage (FIX acceptor):
    bridge = OMSBridge(execution_engine=engine)
    bridge.start_acceptor(host="0.0.0.0", port=9095)
"""
import asyncio
import json
import logging
import socket
import ssl
import threading
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

import httpx

logger = logging.getLogger("oms_bridge")


# ── OMS connection registry ───────────────────────────────────────────────────

@dataclass
class OMSConnection:
    oms_id:        str
    oms_type:      str              # "bloomberg_emsx" | "charles_river" | "fidessa" | "generic"
    display_name:  str
    webhook_url:   Optional[str]    # async execution report push endpoint
    api_key:       str = ""
    registered_at: float = field(default_factory=time.time)
    orders_sent:   int = 0
    last_activity: float = field(default_factory=time.time)


class OMSRegistry:
    """Thread-safe registry of connected OMS systems."""

    def __init__(self):
        self._connections: Dict[str, OMSConnection] = {}
        self._lock = threading.Lock()

    def register(self, conn: OMSConnection) -> str:
        with self._lock:
            self._connections[conn.oms_id] = conn
        logger.info("OMS registered: %s (%s)", conn.oms_id, conn.oms_type)
        return conn.oms_id

    def get(self, oms_id: str) -> Optional[OMSConnection]:
        return self._connections.get(oms_id)

    def all(self) -> List[OMSConnection]:
        with self._lock:
            return list(self._connections.values())

    def touch(self, oms_id: str):
        with self._lock:
            if oms_id in self._connections:
                self._connections[oms_id].last_activity = time.time()
                self._connections[oms_id].orders_sent += 1


# ── Field mappers per OMS dialect ────────────────────────────────────────────

class BloombergEMSXMapper:
    """
    Maps Bloomberg EMSX FIX tags to SORFIX internal order fields.
    Bloomberg extends standard FIX with custom tags in the 9000–9999 range.
    """
    # Bloomberg custom tags
    TAG_EMSX_SEQUENCE  = 9003   # Bloomberg order sequence number
    TAG_EMSX_FILL_ID   = 9004
    TAG_EMSX_BROKER    = 9013   # preferred broker hint (ignored — SORFIX routes direct)
    TAG_EMSX_NOTES     = 9015
    TAG_EMSX_PORTFOLIO = 9016   # portfolio name (mapped to account field)
    TAG_EMSX_TRADER    = 9017

    @classmethod
    def from_fix(cls, fix_fields: Dict[int, str]) -> Dict[str, Any]:
        """Convert Bloomberg EMSX FIX NewOrderSingle to SORFIX order dict."""
        return {
            "symbol":        fix_fields.get(55, ""),
            "side":          "buy" if fix_fields.get(54) == "1" else "sell",
            "quantity":      float(fix_fields.get(38, 0)),
            "price":         float(fix_fields[44]) if 44 in fix_fields else None,
            "base_currency": fix_fields.get(15, "USD"),
            "cl_ord_id":     fix_fields.get(11, str(uuid.uuid4())),
            # Bloomberg extras → metadata
            "oms_meta": {
                "emsx_sequence":  fix_fields.get(cls.TAG_EMSX_SEQUENCE),
                "emsx_portfolio": fix_fields.get(cls.TAG_EMSX_PORTFOLIO),
                "emsx_trader":    fix_fields.get(cls.TAG_EMSX_TRADER),
                "emsx_notes":     fix_fields.get(cls.TAG_EMSX_NOTES),
            },
        }

    @classmethod
    def from_json(cls, payload: dict) -> Dict[str, Any]:
        """Convert Bloomberg EMSX REST/JSON payload to SORFIX order dict."""
        return {
            "symbol":        payload.get("EMSX_TICKER") or payload.get("symbol", ""),
            "side":          (payload.get("EMSX_SIDE") or payload.get("side", "buy")).lower(),
            "quantity":      float(payload.get("EMSX_AMOUNT") or payload.get("quantity", 0)),
            "price":         float(p) if (p := payload.get("EMSX_LIMIT_PRICE") or payload.get("price")) else None,
            "base_currency": payload.get("EMSX_CURRENCY") or payload.get("base_currency", "USD"),
            "cl_ord_id":     str(payload.get("EMSX_SEQUENCE") or uuid.uuid4()),
            "oms_meta":      {k: v for k, v in payload.items() if k.startswith("EMSX_")},
        }


class GenericFIXOMSMapper:
    """
    Maps standard FIX 5.0 SP2 NewOrderSingle to SORFIX internal order.
    Works for Charles River (CRD), Fidessa, FlexTrade, and any standard-compliant OMS.
    """

    @classmethod
    def from_fix(cls, fix_fields: Dict[int, str]) -> Dict[str, Any]:
        ord_type = fix_fields.get(40, "2")
        return {
            "symbol":        fix_fields.get(55, ""),
            "side":          "buy" if fix_fields.get(54) == "1" else "sell",
            "quantity":      float(fix_fields.get(38, 0)),
            "price":         float(fix_fields[44]) if (ord_type == "2" and 44 in fix_fields) else None,
            "base_currency": fix_fields.get(15, "USD"),
            "cl_ord_id":     fix_fields.get(11, str(uuid.uuid4())),
            "account":       fix_fields.get(1, ""),
            "oms_meta":      {"fix_fields": fix_fields},
        }

    @classmethod
    def from_json(cls, payload: dict) -> Dict[str, Any]:
        return {
            "symbol":        payload.get("symbol", ""),
            "side":          payload.get("side", "buy").lower(),
            "quantity":      float(payload.get("quantity", 0)),
            "price":         float(p) if (p := payload.get("price")) else None,
            "base_currency": payload.get("base_currency", "USD"),
            "cl_ord_id":     payload.get("cl_ord_id", str(uuid.uuid4())),
            "account":       payload.get("account", ""),
            "oms_meta":      payload.get("meta", {}),
        }


MAPPER_MAP = {
    "bloomberg_emsx":  BloombergEMSXMapper,
    "bloomberg":       BloombergEMSXMapper,
    "charles_river":   GenericFIXOMSMapper,
    "fidessa":         GenericFIXOMSMapper,
    "flextrade":       GenericFIXOMSMapper,
    "generic":         GenericFIXOMSMapper,
}


# ── OMS Bridge ───────────────────────────────────────────────────────────────

class OMSBridge:
    """
    Central OMS/EMS integration bridge.
    Inject an async callable `execution_fn` that accepts an order dict and
    returns an execution result dict — typically wrapping the SOR + execution engine.
    """

    def __init__(self, execution_fn: Callable):
        self.registry     = OMSRegistry()
        self._execute     = execution_fn  # async fn(order_dict) -> result_dict
        self._acceptor_thread: Optional[threading.Thread] = None
        self._running     = False

    # ── REST inbound ─────────────────────────────────────────────────

    async def inbound_order(
        self,
        oms_id:   str,
        payload:  dict,
        fix_mode: bool = False,
    ) -> dict:
        """
        Accept an order from an OMS system (REST path).
        Returns execution result + ExecutionReport for the OMS.
        """
        conn = self.registry.get(oms_id)
        if not conn:
            return {"error": f"OMS '{oms_id}' not registered. Call POST /oms/register first."}

        oms_type = conn.oms_type
        mapper   = MAPPER_MAP.get(oms_type, GenericFIXOMSMapper)

        try:
            order = mapper.from_json(payload) if not fix_mode else mapper.from_fix(payload)
        except Exception as exc:
            logger.warning("[%s] Order mapping failed: %s", oms_id, exc)
            return {"error": f"Order mapping error: {exc}"}

        self.registry.touch(oms_id)
        logger.info("[OMS:%s] Inbound order: %s %s qty=%.0f",
                    oms_id, order["side"].upper(), order["symbol"], order["quantity"])

        try:
            result = await self._execute(order)
        except Exception as exc:
            logger.error("[OMS:%s] Execution error: %s", oms_id, exc)
            result = {"success": False, "error": str(exc)}

        # Push async ExecutionReport to OMS webhook if registered
        if conn.webhook_url and result.get("success"):
            asyncio.create_task(self._push_exec_report(conn, order, result))

        return {
            "oms_id":        oms_id,
            "cl_ord_id":     order.get("cl_ord_id"),
            "execution":     result,
            "timestamp":     time.time(),
        }

    # ── FIX acceptor ─────────────────────────────────────────────────

    def start_acceptor(self, host: str = "0.0.0.0", port: int = 9095,
                       use_tls: bool = False):
        """Start a FIX acceptor in a background thread."""
        self._running = True
        self._acceptor_thread = threading.Thread(
            target=self._acceptor_loop,
            args=(host, port, use_tls),
            daemon=True,
            name="oms-fix-acceptor",
        )
        self._acceptor_thread.start()
        logger.info("OMS FIX acceptor started on %s:%d (TLS=%s)", host, port, use_tls)

    def stop_acceptor(self):
        self._running = False

    def _acceptor_loop(self, host: str, port: int, use_tls: bool):
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((host, port))
        srv.listen(10)
        srv.settimeout(1.0)
        if use_tls:
            ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            srv = ctx.wrap_socket(srv, server_side=True)

        while self._running:
            try:
                conn_sock, addr = srv.accept()
                t = threading.Thread(
                    target=self._handle_fix_client,
                    args=(conn_sock, addr),
                    daemon=True,
                )
                t.start()
            except socket.timeout:
                continue
            except Exception as exc:
                if self._running:
                    logger.error("Acceptor error: %s", exc)
        srv.close()

    def _handle_fix_client(self, sock: socket.socket, addr):
        """Handle one incoming FIX OMS session."""
        logger.info("OMS FIX client connected from %s", addr)
        buf = b""
        try:
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                buf += chunk
                while b"\x0110=" in buf:
                    end = buf.find(b"\x01", buf.index(b"\x0110=") + 1)
                    if end == -1:
                        break
                    msg = buf[:end + 1]
                    buf = buf[end + 1:]
                    self._dispatch_fix_message(sock, msg)
        except Exception as exc:
            logger.debug("OMS FIX client disconnected: %s", exc)
        finally:
            sock.close()

    def _dispatch_fix_message(self, sock: socket.socket, raw: bytes):
        from tools.fix_engine import parse_fix_message, build_raw_fix, MSG_EXECUTION_REPORT
        fields = parse_fix_message(raw)
        msg_type = fields.get(35, "")

        if msg_type == "A":   # Logon — send back Logon
            logon_ack = build_raw_fix(b"A", "SORFIX", fields.get(49, "OMS"), [
                (98, 0), (108, 30), (1137, 9),
            ])
            sock.sendall(logon_ack)

        elif msg_type == "D":  # NewOrderSingle — map and execute async
            order  = GenericFIXOMSMapper.from_fix(fields)
            sender = fields.get(49, "OMS")
            target = fields.get(56, "SORFIX")
            seq    = int(fields.get(34, 1))

            loop = asyncio.new_event_loop()
            try:
                result = loop.run_until_complete(self._execute(order))
            finally:
                loop.close()

            # Send ExecutionReport back
            exec_status = "2" if result.get("success") else "8"  # Filled | Rejected
            er = build_raw_fix(MSG_EXECUTION_REPORT, target, sender, [
                (37,  str(uuid.uuid4())[:8]),   # OrderID
                (11,  order["cl_ord_id"]),       # ClOrdID
                (17,  str(uuid.uuid4())[:8]),    # ExecID
                (150, exec_status),              # ExecType
                (39,  exec_status),              # OrdStatus
                (55,  order["symbol"]),
                (54,  "1" if order["side"] == "buy" else "2"),
                (38,  int(order["quantity"])),
                (14,  int(result.get("total_filled", 0))),  # CumQty
                (6,   f"{result.get('vwap', 0) or 0:.4f}"), # AvgPx
            ], seq_num=seq + 1)
            sock.sendall(er)

        elif msg_type == "5":  # Logout
            logout = build_raw_fix(b"5", "SORFIX",
                                   fields.get(49, "OMS"), [])
            sock.sendall(logout)

    # ── webhook push ─────────────────────────────────────────────────

    @staticmethod
    async def _push_exec_report(conn: OMSConnection, order: dict, result: dict):
        payload = {
            "oms_id":    conn.oms_id,
            "cl_ord_id": order.get("cl_ord_id"),
            "symbol":    order.get("symbol"),
            "side":      order.get("side"),
            "filled_qty": result.get("total_filled", 0),
            "vwap":       result.get("vwap"),
            "status":    "filled" if result.get("success") else "rejected",
            "timestamp": time.time(),
        }
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.post(conn.webhook_url, json=payload)
                logger.info("[OMS:%s] Webhook push → %d", conn.oms_id, r.status_code)
        except Exception as exc:
            logger.warning("[OMS:%s] Webhook push failed: %s", conn.oms_id, exc)
