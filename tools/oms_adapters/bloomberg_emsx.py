"""
Bloomberg EMSX FIX adapter.
Handles Bloomberg's proprietary FIX extensions (tags 9003–9999) and maps
them to SORFIX's standard order model. Supports both inbound orders
(from EMSX to SORFIX) and outbound execution reports (SORFIX to EMSX).

Bloomberg EMSX FIX dialect reference:
  - SenderCompID:   "BLOOMBERG"
  - TargetCompID:   "SORFIX" (or your configured comp ID)
  - Custom tags:    9003 (EMSX_SEQUENCE), 9004 (EMSX_FILL_ID),
                    9013 (EMSX_BROKER), 9015 (EMSX_NOTES),
                    9016 (EMSX_PORTFOLIO), 9017 (EMSX_TRADER),
                    9022 (EMSX_SETTLE_DATE), 9061 (EMSX_ASSET_CLASS)
"""
import logging
import uuid
from typing import Any, Dict, Optional

logger = logging.getLogger("bloomberg_emsx_adapter")

# Bloomberg custom FIX tags
EMSX_SEQUENCE     = 9003
EMSX_FILL_ID      = 9004
EMSX_BROKER       = 9013
EMSX_NOTES        = 9015
EMSX_PORTFOLIO    = 9016
EMSX_TRADER       = 9017
EMSX_SETTLE_DATE  = 9022
EMSX_ASSET_CLASS  = 9061   # EQT | FI (fixed income) | FX | DERV

EMSX_ASSET_MAP = {
    "EQT":  "equity",
    "FI":   "bond",
    "FX":   "fx",
    "DERV": "futures",
}


class BloombergEMSXAdapter:
    """
    Adapter for Bloomberg EMSX <-> SORFIX order flow.

    Wiring:
        1. Register with OMSBridge as oms_type="bloomberg_emsx"
        2. EMSX sends NewOrderSingle (35=D) with Bloomberg custom tags
        3. This adapter maps to SORFIX OrderRequest
        4. SORFIX routes and fills, then sends ExecutionReport back to EMSX
    """

    OMS_TYPE = "bloomberg_emsx"

    # ── Inbound: EMSX → SORFIX ──────────────────────────────────────

    @classmethod
    def map_new_order(cls, fix_fields: Dict[int, str]) -> Dict[str, Any]:
        """Map a Bloomberg EMSX FIX NewOrderSingle to a SORFIX order dict."""
        asset_class_raw = fix_fields.get(EMSX_ASSET_CLASS, "EQT")
        asset_class     = EMSX_ASSET_MAP.get(asset_class_raw, "equity")

        order: Dict[str, Any] = {
            "symbol":        fix_fields.get(55, ""),
            "side":          "buy" if fix_fields.get(54) == "1" else "sell",
            "quantity":      float(fix_fields.get(38, 0)),
            "price":         float(fix_fields[44]) if 44 in fix_fields else None,
            "base_currency": fix_fields.get(15, "USD"),
            "cl_ord_id":     fix_fields.get(11) or f"EMSX-{uuid.uuid4().hex[:8]}",
            "asset_class":   asset_class,
            "account":       fix_fields.get(1, ""),
            "oms_meta": {
                "oms_type":       cls.OMS_TYPE,
                "emsx_sequence":  fix_fields.get(EMSX_SEQUENCE),
                "emsx_portfolio": fix_fields.get(EMSX_PORTFOLIO),
                "emsx_trader":    fix_fields.get(EMSX_TRADER),
                "emsx_broker":    fix_fields.get(EMSX_BROKER),   # preferred broker hint (advisory)
                "emsx_notes":     fix_fields.get(EMSX_NOTES),
                "emsx_settle":    fix_fields.get(EMSX_SETTLE_DATE),
                "emsx_asset_cls": asset_class_raw,
            },
        }

        # Bond-specific EMSX fields
        if asset_class == "bond":
            order["bond"] = {
                "isin":           fix_fields.get(107, ""),  # SecurityDesc
                "bond_type":      fix_fields.get(167, "CORP"),
                "yield_to_mat":   float(fix_fields[236]) if 236 in fix_fields else None,
                "accrued_int":    float(fix_fields[159]) if 159 in fix_fields else 0.0,
                "settlement_date": fix_fields.get(EMSX_SETTLE_DATE),
            }

        # FX-specific EMSX fields
        if asset_class == "fx":
            order["fx"] = {
                "pair":          fix_fields.get(55, ""),   # Symbol = "EUR/USD"
                "quote_currency": fix_fields.get(120, ""),  # SettlCurrency
                "tenor":          "SPOT",
                "forward_pts":   float(fix_fields[37]) if 37 in fix_fields else None,
            }

        logger.info(
            "[EMSX] Mapped order: %s %s %s qty=%.0f asset=%s portfolio=%s",
            order["cl_ord_id"], order["side"].upper(), order["symbol"],
            order["quantity"], asset_class,
            order["oms_meta"].get("emsx_portfolio", "N/A"),
        )
        return order

    @classmethod
    def map_json_order(cls, payload: dict) -> Dict[str, Any]:
        """Map a Bloomberg EMSX REST/JSON payload to a SORFIX order dict."""
        asset_raw   = payload.get("EMSX_ASSET_CLASS", "EQT")
        asset_class = EMSX_ASSET_MAP.get(asset_raw, "equity")

        return {
            "symbol":        payload.get("EMSX_TICKER")        or payload.get("symbol", ""),
            "side":          (payload.get("EMSX_SIDE")         or payload.get("side", "BUY")).lower(),
            "quantity":      float(payload.get("EMSX_AMOUNT")  or payload.get("quantity", 0)),
            "price":         float(p) if (p := payload.get("EMSX_LIMIT_PRICE") or payload.get("price")) else None,
            "base_currency": payload.get("EMSX_CURRENCY")      or payload.get("base_currency", "USD"),
            "cl_ord_id":     str(payload.get("EMSX_SEQUENCE")  or payload.get("cl_ord_id") or uuid.uuid4()),
            "asset_class":   asset_class,
            "account":       payload.get("EMSX_PORTFOLIO", ""),
            "oms_meta":      {k: v for k, v in payload.items() if k.startswith("EMSX_")},
        }

    # ── Outbound: SORFIX → EMSX ExecutionReport ──────────────────────

    @classmethod
    def build_exec_report(
        cls,
        sorfix_result: dict,
        original_order: dict,
        seq_num: int = 1,
    ) -> bytes:
        """
        Build a FIX ExecutionReport (35=8) to send back to Bloomberg EMSX.
        Includes Bloomberg custom tags for portfolio and sequence tracking.
        """
        from tools.fix_engine import build_raw_fix, MSG_EXECUTION_REPORT
        oms_meta  = original_order.get("oms_meta", {})
        filled    = sorfix_result.get("total_filled", 0)
        vwap      = sorfix_result.get("vwap") or 0.0
        success   = sorfix_result.get("success", False)
        exec_type = "2" if success else "8"   # Filled | Rejected

        fields = [
            (37,  f"SORFIX-{uuid.uuid4().hex[:8]}"),   # OrderID
            (11,  original_order.get("cl_ord_id", "")),  # ClOrdID
            (17,  f"EXEC-{uuid.uuid4().hex[:6]}"),      # ExecID
            (150, exec_type),                            # ExecType
            (39,  exec_type),                            # OrdStatus
            (55,  original_order.get("symbol", "")),
            (54,  "1" if original_order.get("side") == "buy" else "2"),
            (38,  int(original_order.get("quantity", 0))),
            (14,  int(filled)),                          # CumQty
            (6,   f"{vwap:.4f}"),                        # AvgPx
        ]

        # Bloomberg-specific fields on ExecutionReport
        if oms_meta.get("emsx_sequence"):
            fields.append((EMSX_SEQUENCE, oms_meta["emsx_sequence"]))
        if oms_meta.get("emsx_portfolio"):
            fields.append((EMSX_PORTFOLIO, oms_meta["emsx_portfolio"]))
        if oms_meta.get("emsx_trader"):
            fields.append((EMSX_TRADER, oms_meta["emsx_trader"]))

        return build_raw_fix(
            MSG_EXECUTION_REPORT,
            sender="SORFIX",
            target=oms_meta.get("sender_comp_id", "BLOOMBERG"),
            fields=fields,
            seq_num=seq_num,
        )
