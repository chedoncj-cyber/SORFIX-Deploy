# tools/admin_audit_log.py
"""
Append-only admin audit log — SOC 1 CO-5 requirement.
Every /admin/risk change is written as a JSON line to logs/admin_audit.log.
"""
import json, logging, os, threading, time
from pathlib import Path

_lock = threading.Lock()
_log_path: Path = None

def init(log_dir: str = None):
    global _log_path
    d = Path(log_dir) if log_dir else Path(__file__).parent.parent / "logs"
    d.mkdir(exist_ok=True)
    _log_path = d / "admin_audit.log"

def record(actor_ip: str, endpoint: str, old_value: dict, new_value: dict, note: str = ""):
    global _log_path
    if _log_path is None:
        init()
    entry = {"ts": time.time(), "iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
             "actor_ip": actor_ip, "endpoint": endpoint,
             "old": old_value, "new": new_value, "note": note}
    with _lock:
        with open(_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

def tail(n: int = 100) -> list:
    if _log_path is None or not _log_path.exists():
        return []
    with _lock:
        lines = _log_path.read_text(encoding="utf-8").strip().splitlines()
    return [json.loads(l) for l in lines[-n:]]
