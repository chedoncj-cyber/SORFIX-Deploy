# Multi-Asset Trading Workflow

## Objective
Extend SORFIX beyond equities to support fixed-income bonds and foreign exchange (FX), with particular emphasis on African EM markets where SORFIX has a competitive advantage.

## Supported Asset Classes

| Asset Class | Status   | Key Markets                                 |
|-------------|----------|---------------------------------------------|
| Equity      | Live     | NYSE, LSE, HKEX, TSE, SSE, SZSE, TADAWUL, NSE_IN, EURONEXT |
| Bond        | Live     | US Treasury, UK Gilts, German Bunds, Ghana, Nigeria, South Africa, Kenya bonds |
| FX Spot     | Live     | G10 pairs + African EM (USDGHS, USDNGN, USDZAR, USDKES) |
| FX Forward  | Live     | Standard forward points via FX handler       |
| FX NDF      | Live     | Non-Deliverable Forwards for restricted EM CCYs |
| Futures     | Planned  | Equity index futures                         |

## Bond Orders

### FIX Wire Format (FIX 5.0 SP2)
```
35=D  NewOrderSingle
167   SecurityType = CORP | GOVT | MUNI | MBS
107   SecurityDesc = ISIN
64    SettlDate     = T+2 (YYYYMMDD)
159   AccruedInterestAmt
236   Yield
541   MaturityDate
228   Factor
```

### REST Endpoint
```http
POST /orders/bond/submit
{
  "isin":            "US912810TM85",
  "side":            "buy",
  "face_value":      1000000,
  "clean_price_pct": 98.75,
  "bond_type":       "GOVT",
  "coupon_rate":     4.5,
  "maturity_date":   "20340815",
  "settlement_days": 2,
  "day_count_conv":  "30/360"
}
```

### Bond Price Computation
```
dirty_price_pct = clean_price_pct + accrued_interest_pct
accrued_interest = face_value × (coupon_rate/100) × (days_since_last_coupon / period_days)
total_consideration = face_value × dirty_price_pct / 100
```

### African Bond Markets
| Country     | Typical Yield | Day Count | Notes                        |
|-------------|---------------|-----------|------------------------------|
| Ghana       | 15–18%        | 30/360    | Eurobonds + domestic GH¢ bonds |
| Nigeria     | 17–20%        | Actual/365| FGN bonds, Eurobonds          |
| South Africa| 8–10%         | Actual/365| ZAR-denominated, JSE-listed   |
| Kenya       | 13–16%        | Actual/365| Infrastructure bonds          |

## FX Orders

### FIX Wire Format (FIX 5.0 SP2)
```
35=D  NewOrderSingle (or 35=R QuoteRequest for two-way price)
167   SecurityType = FOR (spot) | FXNDF (NDF)
55    Symbol = "EUR/USD"
15    Currency = base currency (EUR)
120   SettlCurrency = quote currency (USD)
64    SettlDate = settlement date YYYYMMDD
44    Price = spot rate
37    ForwardPoints (for forwards)
```

### REST Endpoint
```http
POST /orders/fx/submit
{
  "pair":        "USDGHS",
  "side":        "buy",
  "base_amount": 500000,
  "tenor":       "SPOT",
  "spot_rate":   14.20
}
```

### Tenor Settlement
| Tenor | Settlement |
|-------|-----------|
| TOD   | T+0       |
| TOM   | T+1       |
| SPOT  | T+2       |
| 1W    | T+7 business days |
| 1M    | T+30 calendar days |
| 3M    | T+91 calendar days |

### African EM FX Pairs (SORFIX Advantage)
| Pair    | Note                              |
|---------|-----------------------------------|
| USDGHS  | Ghana Cedi — managed float        |
| USDNGN  | Nigerian Naira — FX controls      |
| USDZAR  | South African Rand — liquid EM    |
| USDKES  | Kenyan Shilling — EAC trading hub |

NDF mode (`"ndf": true`) is required for NGN where settlement is restricted.

## Risk Limits by Asset Class

| Check              | Equity              | Bond                        | FX                         |
|--------------------|---------------------|-----------------------------|----------------------------|
| Max order notional | qty × price         | face_value × price_pct/100  | base_amount                |
| Daily limit        | cumulative notional | cumulative bond principal   | cumulative base amount     |
| Price band         | ±5% from last trade | N/A (yield-driven)          | N/A (market rate)          |
| Max qty            | share count         | N/A                         | N/A                        |

## Market Data Simulation

| Source         | Class             | Update Interval |
|----------------|-------------------|-----------------|
| Equity books   | MarketDataPipeline| 100ms           |
| FX spot rates  | FXMarketData      | 500ms (GBM)     |
| Bond yields    | BondMarketData    | 5s (yield walk) |

In production, replace with:
- **FX**: EBS/Reuters Matching ECN feed or LMAX Digital
- **Bonds**: Bloomberg BVAL or Refinitiv evaluated pricing
- **African rates**: Stanbic, Standard Bank, or local central bank feeds

## Key Files

| File                                        | Purpose                            |
|---------------------------------------------|------------------------------------|
| `tools/asset_class.py`                      | AssetClass enum + per-asset config |
| `tools/asset_handlers/bond_handler.py`      | Bond accrued interest + FIX fields |
| `tools/asset_handlers/fx_handler.py`        | FX pip/lot + settlement + FIX      |
| `tools/fix_engine.py`                       | build_quote_request, build_quote   |
| `tools/market_data_pipeline.py`             | FXMarketData, BondMarketData       |
| `tools/risk_engine.py`                      | Asset-class-specific risk checks   |
| `api/routes/multi_asset.py`                 | Bond + FX REST endpoints           |
| `api/models.py`                             | BondOrderRequest/Response + FX     |
