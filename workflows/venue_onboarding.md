# Venue Onboarding Workflow

## Objective
Add a new African exchange venue to the SOR routing pool.

## Checklist

### Step 1 — Gather exchange details
Confirm these from the exchange's FIX specification document:
- [ ] FIX version (must be 4.2 or compatible)
- [ ] Host / port
- [ ] SenderCompID and TargetCompID
- [ ] Taker fee (bps)
- [ ] Average round-trip latency (ms)
- [ ] Settlement cycle (T+2, T+3)
- [ ] Trading hours (UTC)
- [ ] Currency and ISO code
- [ ] Tick size schedule
- [ ] Market data subscription format (snapshot vs. incremental)

### Step 2 — Add to venues.yaml
```yaml
  NEWEX:
    name: New Exchange
    host: fix.newex.com
    port: 9880
    sender_comp_id: BROKER_XX
    target_comp_id: NEWEX_TRADING
    currency: XXX
    taker_fee: 0.002
    latency_ms: 10.0
    enabled: false          # keep false until adapter is tested
    symbols: [SYM1, SYM2]
```

### Step 3 — Add to app_state.py
```python
venues["NEWEX"] = VenueConfig(
    name="NEWEX", currency="XXX", taker_fee=0.002, latency_ms=10.0, enabled=False
)
```
Also add FX rate to `tools/fx_optimizer.py`:
```python
_BASE_RATES_USD["XXX"] = 45.0  # approximate
```

### Step 4 — Create the adapter
Copy `tools/venue_adapters/jse_adapter.py` → `tools/venue_adapters/newex_adapter.py`.
Implement:
- `connect()` — TLS socket + Logon message
- `disconnect()` — Logout + socket close
- `subscribe_market_data(symbol)` — MarketDataRequest (V)
- `send_order(...)` — NewOrderSingle (D) with venue tick-size rounding

### Step 5 — Add venue symbols to market data pipeline
In `tools/market_data_pipeline.py`, add to `VENUE_SYMBOLS`:
```python
"NEWEX": {
    "SYM1": {"price": 100.0, "vol": 0.002},
    "SYM2": {"price": 50.0,  "vol": 0.003},
},
```

### Step 6 — Enable and test
1. Set `enabled: true` in `configs/venues.yaml`
2. Run demo mode: `python main.py --demo`
3. Check routing includes the new venue: `curl /market-data/book/NEWEX/SYM1`
4. Submit a test order: `curl -X POST /orders/submit -d '{...}'`
5. Monitor circuit breaker: `curl /health`

### Step 7 — Production cut-over
- Add real credentials to `.env`
- Replace simulated `connect()` with real TLS socket
- Set `simulate: false` in `configs/sor_config.yaml`
- Run load test (K6 config from PDF §6.3):
  `k6 run load_test.js`
- Watch latency: p95 should stay <500µs

## Tools Used
- `tools/venue_adapters/base_adapter.py` — template interface
- `tools/fx_optimizer.py` — FX rate registry
- `tools/market_data_pipeline.py` — simulation symbols
- `configs/venues.yaml` — venue registry
- `app_state.py` — runtime wiring
