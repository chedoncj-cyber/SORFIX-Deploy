# OMS/EMS Integration Workflow

## Objective
Connect buy-side Order Management Systems (Bloomberg EMSX, Charles River CRD, Fidessa, FlexTrade) to SORFIX so that their order flow is routed through the Smart Order Router instead of going directly to venues.

## Architecture

```
OMS/EMS  ──────────────────────────────────────────────────────────
  │                                                                │
  │  FIX 5.0 initiator (acceptor port 9095 / 9094)                │
  │  OR REST  POST /oms/inbound                                    │
  │                                                                ▼
  └──────────────► OMSBridge ──► SORFIX SOR ──► Venues ──► Fill ──► ExecReport
                                                                    │
                                               Webhook push ◄───────┘
                                               POST callback_url
```

## Supported OMS Types

| oms_type         | Protocol                   | Notes                                              |
|------------------|----------------------------|----------------------------------------------------|
| bloomberg_emsx   | FIX 5.0 + custom tags 9003–9061 | EMSX_SEQUENCE, EMSX_PORTFOLIO, EMSX_ASSET_CLASS |
| charles_river    | Standard FIX 5.0 SP2       | GenericFIXOMSAdapter                               |
| fidessa          | Standard FIX 5.0 SP2       | GenericFIXOMSAdapter                               |
| flextrade        | Standard FIX 5.0 SP2       | GenericFIXOMSAdapter                               |
| generic          | Standard FIX 5.0 SP2 / JSON| GenericFIXOMSAdapter                               |

## Setup Steps

### 1. Register the OMS
```http
POST /oms/register
{
  "oms_id":       "bloomberg-prod",
  "oms_type":     "bloomberg_emsx",
  "display_name": "Bloomberg EMSX Production",
  "webhook_url":  "https://emsx.client.com/sorfix-callback"
}
```

### 2a. Submit order via REST
```http
POST /oms/inbound
{
  "oms_id": "bloomberg-prod",
  "payload": {
    "EMSX_TICKER":      "AAPL",
    "EMSX_SIDE":        "BUY",
    "EMSX_AMOUNT":      5000,
    "EMSX_LIMIT_PRICE": 185.50,
    "EMSX_CURRENCY":    "USD",
    "EMSX_PORTFOLIO":   "GLOBAL_EQ",
    "EMSX_SEQUENCE":    "887234",
    "EMSX_ASSET_CLASS": "EQT"
  }
}
```

### 2b. Submit order via FIX acceptor
World SORFIX FIX acceptor: **port 9095**
Pan SORFIX FIX acceptor:   **port 9094**

OMS connects as FIX initiator. SORFIX expects:
- BeginString = FIXT.1.1
- ApplVerID (1128) = 9
- 35=A (Logon with DefaultApplVerID 1137=9)
- 35=D (NewOrderSingle)

SORFIX replies with 35=8 ExecutionReport (or 35=3 Reject on risk block).

## Order Mapping

### Bloomberg EMSX → SORFIX
| EMSX Field        | SORFIX Field   |
|-------------------|----------------|
| EMSX_TICKER       | symbol         |
| EMSX_SIDE         | side           |
| EMSX_AMOUNT       | quantity       |
| EMSX_LIMIT_PRICE  | price          |
| EMSX_CURRENCY     | base_currency  |
| EMSX_PORTFOLIO    | account        |
| EMSX_ASSET_CLASS  | asset_class    |
| EMSX_SEQUENCE     | cl_ord_id      |

### Generic FIX → SORFIX (Charles River / Fidessa)
| FIX Tag   | Field          |
|-----------|----------------|
| 55        | symbol         |
| 54        | side (1=buy)   |
| 38        | quantity       |
| 44        | price          |
| 15        | base_currency  |
| 167       | asset_class (SecurityType) |
| 11        | cl_ord_id      |

## Risk Checks
All OMS-inbound orders pass through the standard RiskEngine:
- max_order_qty, max_order_notional, price_band_pct, max_daily_notional
- Bond orders: notional = face_value × clean_price_pct / 100
- FX orders: notional = base_amount

## Execution Report Webhook
When `webhook_url` is registered, SORFIX pushes async callbacks after each fill:
```json
{
  "oms_id":     "bloomberg-prod",
  "cl_ord_id":  "887234",
  "symbol":     "AAPL",
  "side":       "buy",
  "filled_qty": 5000,
  "vwap":       185.48,
  "status":     "filled",
  "timestamp":  1728134400.0
}
```

## Monitoring
- `GET /oms/connections` — list registered OMS systems with activity stats
- `GET /health` — includes OMS bridge status

## Key Files
| File                                    | Purpose                             |
|-----------------------------------------|-------------------------------------|
| `tools/oms_bridge.py`                   | Core bridge: REST + FIX acceptor    |
| `tools/oms_adapters/bloomberg_emsx.py`  | Bloomberg EMSX field mapper         |
| `tools/oms_adapters/generic_fix_oms.py` | CRD / Fidessa / FlexTrade mapper    |
| `api/routes/oms_routes.py`              | REST endpoints                      |
| `app_state.py`                          | Bridge initialization               |
