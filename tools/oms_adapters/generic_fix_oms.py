"""
Generic FIX OMS adapter.
Standard FIX 5.0 SP2 / FIXT.1.1 mapping for Charles River (CRD), Fidessa,
FlexTrade, Linedata Longview, and any other OMS that sends standard FIX
NewOrderSingle (35=D) without proprietary tag extensions.

Behaviour:
  - Reads standard FIX tags only (no vendor extensions)
  - Detects asset class from SecurityType (tag 167)
  - Routes equity, bond, and FX orders to the appropriate SORFIX handler
  - Returns standard FIX ExecutionReport (35=8)
"""
import logging
import uuid
from typing import Any, Dict

logger = logging.getLogger("generic_fix_oms_adapter")

# FIX tag 167 SecurityType → SORFIX asset class
SECURITY_TYPE_MAP: Dict[str, str] = {
    "CS":    "equity",   # Common Stock
    "PS":    "equity",   # Preferred Stock
    "CORP":  "bond",
    "GOVT":  "bond",
    "MUNI":  "bond",
    "MBS":   "bond",
    "ABS":   "bond",
    "CD":    "bond",
    "FOR":   "fx",       # Foreign Exchange
    "FXNDF": "fx",
    "FUT":   "futures",
    "OPT":   "futures",
}


class GenericFIXOMSAdapter:
    """
    Standard FIX 5.0 SP2 OMS adapter.
    Compatible with Charles River CRD, Fidessa, FlexTrade, and any vendor
    that follows the FIX specification without proprietary extensions.
    """

    OMS_TYPE = "generic"

    @classmethod
    def map_new_order(cls, fix_fields: Dict[int, str]) -> Dict[str, Any]:
        """Map standard FIX NewOrderSingle to SORFIX order dict."""
        sec_type    = fix_fields.get(167, "CS")
        asset_class = SECURITY_TYPE_MAP.get(sec_type, "equity")
        ord_type    = fix_fields.get(40, "2")   # 1=Market, 2=Limit
        side_raw    = fix_fields.get(54, "1")
        side        = "buy" if side_raw == "1" else "sell"

        order: Dict[str, Any] = {
            "symbol":        fix_fields.get(55, ""),
            "side":          side,
            "quantity":      float(fix_fields.get(38, 0)),
            "price":         float(fix_fields[44]) if (ord_type == "2" and 44 in fix_fields) else None,
            "base_currency": fix_fields.get(15, "USD"),
            "cl_ord_id":     fix_fields.get(11) or f"OMS-{uuid.uuid4().hex[:8]}",
            "asset_class":   asset_class,
            "account":       fix_fields.get(1, ""),
            "oms_meta": {
                "oms_type":        cls.OMS_TYPE,
                "sender_comp_id":  fix_fields.get(49, ""),
                "security_type":   sec_type,
                "fix_ord_type":    ord_type,
                "tif":             fix_fields.get(59, "0"),   # TimeInForce
                "hand_inst":       fix_fields.get(21, ""),
            },
        }

        # Bond-specific fields
        if asset_class == "bond":
            order["bond"] = {
                "isin":          fix_fields.get(107, "") or fix_fields.get(48, ""),
                "bond_type":     sec_type,
                "yield_to_mat":  float(fix_fields[236]) if 236 in fix_fields else None,
                "maturity_date": fix_fields.get(541),
                "coupon_rate":   float(fix_fields[223]) if 223 in fix_fields else 0.0,
                "factor":        float(fix_fields[228]) if 228 in fix_fields else 1.0,
            }

        # FX-specific fields
        if asset_class == "fx":
            order["fx"] = {
                "pair":           fix_fields.get(55, ""),
                "quote_currency": fix_fields.get(120, ""),
                "settle_date":    fix_fields.get(64, ""),
                "forward_pts":    float(fix_fields[37]) if 37 in fix_fields else None,
                "tenor":          "SPOT",
            }

        logger.info(
            "[FIX-OMS] Mapped order: %s %s %s qty=%.0f asset=%s from=%s",
            order["cl_ord_id"], side.upper(), order["symbol"],
            order["quantity"], asset_class, fix_fields.get(49, "?"),
        )
        return order

    @classmethod
    def map_json_order(cls, payload: dict) -> Dict[str, Any]:
        """Map a standard JSON payload to a SORFIX order dict."""
        asset_class = payload.get("asset_class", "equity").lower()
        order: Dict[str, Any] = {
            "symbol":        payload.get("symbol", ""),
            "side":          payload.get("side", "buy").lower(),
            "quantity":      float(payload.get("quantity", 0)),
            "price":         float(p) if (p := payload.get("price")) else None,
            "base_currency": payload.get("base_currency", "USD"),
            "cl_ord_id":     payload.get("cl_ord_id") or f"OMS-{uuid.uuid4().hex[:8]}",
            "asset_class":   asset_class,
            "account":       payload.get("account", ""),
            "oms_meta":      {"oms_type": cls.OMS_TYPE, **payload.get("meta", {})},
        }
        if asset_class == "bond" and "bond" in payload:
            order["bond"] = payload["bond"]
        if asset_class == "fx" and "fx" in payload:
            order["fx"] = payload["fx"]
        return order

    @classmethod
    def build_exec_report(
        cls,
        sorfix_result: dict,
        original_order: dict,
        seq_num: int = 1,
    ) -> bytes:
        """Build a standard FIX 5.0 ExecutionReport (35=8)."""
        from tools.fix_engine import build_raw_fix, MSG_EXECUTION_REPORT
        filled    = sorfix_result.get("total_filled", 0)
        vwap      = sorfix_result.get("vwap") or 0.0
        success   = sorfix_result.get("success", False)
        exec_type = "2" if success else "8"
        target    = original_order.get("oms_meta", {}).get("sender_comp_id", "OMS")

        return build_raw_fix(
            MSG_EXECUTION_REPORT,
            sender="SORFIX",
            target=target,
            fields=[
                (37,  f"SORFIX-{uuid.uuid4().hex[:8]}"),
                (11,  original_order.get("cl_ord_id", "")),
                (17,  f"EXEC-{uuid.uuid4().hex[:6]}"),
                (150, exec_type),
                (39,  exec_type),
                (55,  original_order.get("symbol", "")),
                (54,  "1" if original_order.get("side") == "buy" else "2"),
                (38,  int(original_order.get("quantity", 0))),
                (14,  int(filled)),
                (6,   f"{vwap:.4f}"),
            ],
            seq_num=seq_num,
        )
