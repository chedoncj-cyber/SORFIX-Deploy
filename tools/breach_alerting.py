"""
Breach alerting — posts to a webhook when a pre-trade risk limit is triggered.
Set BREACH_WEBHOOK_URL in .env to enable (Slack incoming webhook or any HTTPS endpoint).
"""
import json, logging, os, threading, time, urllib.request
logger = logging.getLogger("breach_alerting")
_webhook_url: str = os.environ.get("BREACH_WEBHOOK_URL", "")

def alert(order_id: str, symbol: str, limit_type: str, current_value: float, limit_value: float):
    if not _webhook_url:
        logger.debug("Breach alert suppressed (BREACH_WEBHOOK_URL not set): %s %s", limit_type, symbol)
        return
    payload = {
        "text": (
            f":warning: *SORFIX Risk Breach*\n"
            f"Order `{order_id}` | Symbol `{symbol}`\n"
            f"Limit: `{limit_type}` | Value: `{current_value}` | Threshold: `{limit_value}`\n"
            f"Time: `{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}`"
        )
    }
    def _post():
        try:
            req = urllib.request.Request(
                _webhook_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5):
                pass
            logger.info("Breach alert sent: %s %s", limit_type, symbol)
        except Exception as exc:
            logger.warning("Breach alert failed: %s", exc)
    threading.Thread(target=_post, daemon=True, name="breach-alert").start()
