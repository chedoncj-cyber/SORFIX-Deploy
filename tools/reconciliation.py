# tools/reconciliation.py
"""
Daily reconciliation — compares in-memory order_store vs SQLite records.
SOC 2 Processing Integrity PI1 requirement.
"""
import logging, sqlite3, time
from pathlib import Path

logger = logging.getLogger("reconciliation")

def run(order_store: dict, db_path: str) -> dict:
    """
    Compare in-memory order_store against SQLite orders table.
    Returns a summary with any discrepancies.
    """
    result = {"run_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "in_memory": 0, "in_db": 0, "matched": 0,
              "only_in_memory": [], "only_in_db": [], "discrepancies": []}
    mem_ids = set(order_store.keys())
    result["in_memory"] = len(mem_ids)
    db_ids = set()
    try:
        with sqlite3.connect(db_path) as conn:
            for (oid,) in conn.execute("SELECT order_id FROM orders"):
                db_ids.add(oid)
    except Exception as exc:
        logger.warning("DB read error during reconciliation: %s", exc)
        result["error"] = str(exc)
        return result
    result["in_db"] = len(db_ids)
    result["matched"] = len(mem_ids & db_ids)
    result["only_in_memory"] = list(mem_ids - db_ids)[:50]
    result["only_in_db"] = list(db_ids - mem_ids)[:50]
    if result["only_in_memory"] or result["only_in_db"]:
        logger.warning("Reconciliation discrepancy: %d only in memory, %d only in DB",
                       len(result["only_in_memory"]), len(result["only_in_db"]))
    else:
        logger.info("Reconciliation PASSED: %d orders matched", result["matched"])
    return result
