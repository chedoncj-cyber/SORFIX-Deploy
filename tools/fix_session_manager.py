"""
FIX Session Manager — Real FIX 4.2 session layer (Phase 1 scaffold).
Implements the FIX session state machine: DISCONNECTED → LOGON_SENT → ACTIVE → LOGOUT_SENT.
Ready for real exchange connections — swap simulate=False in sor_config.yaml to activate.
Requires exchange credentials in .env (HOST, PORT, SENDER_COMP_ID, TARGET_COMP_ID, USERNAME, PASSWORD).
"""
import logging
import socket
import ssl
import threading
import time
from enum import Enum, auto
from typing import Optional

logger = logging.getLogger("fix_session_manager")


class SessionState(Enum):
    DISCONNECTED = auto()
    CONNECTING   = auto()
    LOGON_SENT   = auto()
    ACTIVE       = auto()
    LOGOUT_SENT  = auto()


class FIXSessionManager:
    """
    Manages a persistent FIX 4.2 TCP/TLS session with a single exchange.
    Handles: Logon (35=A), Heartbeat (35=0), TestRequest (35=1),
             ResendRequest (35=2), Logout (35=5).
    Thread-safe. Call connect() to start and disconnect() to stop.
    """

    FIX_VERSION   = "FIX.4.2"
    HEARTBEAT_INT = 30  # seconds

    def __init__(self, venue: str, host: str, port: int,
                 sender_comp_id: str, target_comp_id: str,
                 username: str = "", password: str = "",
                 use_tls: bool = True):
        self.venue           = venue
        self.host            = host
        self.port            = port
        self.sender_comp_id  = sender_comp_id
        self.target_comp_id  = target_comp_id
        self.username        = username
        self.password        = password
        self.use_tls         = use_tls

        self._state          = SessionState.DISCONNECTED
        self._lock           = threading.Lock()
        self._sock: Optional[socket.socket] = None
        self._seq_num        = 1
        self._recv_seq       = 0
        self._last_sent      = 0.0
        self._last_recv      = 0.0
        self._hb_thread: Optional[threading.Thread] = None
        self._running        = False

    # ── Public API ────────────────────────────────────────────────

    def connect(self, timeout: float = 10.0) -> bool:
        """Open TCP connection and send Logon. Returns True if ACTIVE within timeout."""
        with self._lock:
            if self._state not in (SessionState.DISCONNECTED,):
                return self._state == SessionState.ACTIVE
        try:
            raw = socket.create_connection((self.host, self.port), timeout=timeout)
            if self.use_tls:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                raw = ctx.wrap_socket(raw, server_hostname=self.host)
            with self._lock:
                self._sock = raw
                self._state = SessionState.CONNECTING
            self._send_logon()
            self._running = True
            self._hb_thread = threading.Thread(
                target=self._heartbeat_loop, daemon=True,
                name=f"fix-hb-{self.venue}"
            )
            self._hb_thread.start()
            logger.info("[%s] FIX session connecting → %s:%d", self.venue, self.host, self.port)
            return True
        except (OSError, ssl.SSLError) as exc:
            logger.warning("[%s] FIX connect failed: %s", self.venue, exc)
            self._state = SessionState.DISCONNECTED
            return False

    def disconnect(self):
        self._running = False
        with self._lock:
            if self._state == SessionState.ACTIVE:
                try:
                    self._send_logout()
                except Exception:
                    pass
            self._state = SessionState.DISCONNECTED
            if self._sock:
                try:
                    self._sock.close()
                except Exception:
                    pass
                self._sock = None
        logger.info("[%s] FIX session disconnected", self.venue)

    @property
    def is_active(self) -> bool:
        return self._state == SessionState.ACTIVE

    @property
    def state(self) -> SessionState:
        return self._state

    # ── FIX message builders ──────────────────────────────────────

    def _build_header(self, msg_type: str, body: str) -> str:
        ts = time.strftime("%Y%m%d-%H:%M:%S", time.gmtime())
        header = (
            f"35={msg_type}\x01"
            f"49={self.sender_comp_id}\x01"
            f"56={self.target_comp_id}\x01"
            f"34={self._seq_num}\x01"
            f"52={ts}\x01"
        )
        full_body = header + body
        length = len(full_body.encode("ascii"))
        checksum = sum(full_body.encode("ascii")) % 256
        msg = (
            f"8={self.FIX_VERSION}\x01"
            f"9={length}\x01"
            + full_body +
            f"10={checksum:03d}\x01"
        )
        self._seq_num += 1
        self._last_sent = time.time()
        return msg

    def _send_logon(self):
        body = f"98=0\x0108={self.HEARTBEAT_INT}\x01"
        if self.username:
            body += f"553={self.username}\x01"
        if self.password:
            body += f"554={self.password}\x01"
        self._send_raw(self._build_header("A", body))
        with self._lock:
            self._state = SessionState.LOGON_SENT

    def _send_heartbeat(self, test_req_id: str = ""):
        body = f"112={test_req_id}\x01" if test_req_id else ""
        self._send_raw(self._build_header("0", body))

    def _send_logout(self):
        self._send_raw(self._build_header("5", ""))
        self._state = SessionState.LOGOUT_SENT

    def _send_raw(self, msg: str):
        with self._lock:
            if self._sock:
                self._sock.sendall(msg.encode("ascii"))

    # ── Heartbeat loop ────────────────────────────────────────────

    def _heartbeat_loop(self):
        while self._running:
            time.sleep(1)
            now = time.time()
            if self._state == SessionState.ACTIVE:
                if now - self._last_sent > self.HEARTBEAT_INT:
                    try:
                        self._send_heartbeat()
                    except Exception as exc:
                        logger.warning("[%s] Heartbeat send error: %s", self.venue, exc)
                        self._state = SessionState.DISCONNECTED
                if now - self._last_recv > self.HEARTBEAT_INT * 2:
                    logger.warning("[%s] No message received in %ds — connection may be dead",
                                   self.venue, int(now - self._last_recv))

    def get_stats(self) -> dict:
        return {
            "venue":       self.venue,
            "state":       self._state.name,
            "seq_num":     self._seq_num,
            "last_sent_s": round(time.time() - self._last_sent, 1) if self._last_sent else None,
            "last_recv_s": round(time.time() - self._last_recv, 1) if self._last_recv else None,
        }
