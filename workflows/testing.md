# Testing Workflow

## Objective
Verify the correctness and stability of all SORFIX components — core SOR, algo strategies,
institutional trading features, and cross-cutting concerns — using the local FastAPI server.

## Prerequisites
```bash
pip install -r requirements.txt
python main.py          # starts on http://localhost:9090
```
All tests below assume the server is running at `http://localhost:9090`.

---

## 1. Health & Startup

```bash
# Confirm all subsystems initialised
curl http://localhost:9090/health
```
Expected:
- `"status": "healthy"`
- `venues` list with `circuit_breaker_state: "closed"` for each venue
- `"pipeline_running": true`

```bash
# Import sanity check (run before committing)
python -c "from api.gateway import app; print('import OK')"
```

---

## 2. Market Data

```bash
# Order book for one symbol at one venue
curl http://localhost:9090/market-data/book/GSE/GCB

# All venues for a symbol
curl http://localhost:9090/market-data/books/MTN

# Pipeline statistics
curl http://localhost:9090/market-data/pipeline/stats
# Expect: "running": true, updates_processed incrementing

# Force a price (test only)
curl -X POST "http://localhost:9090/market-data/inject-price?venue=GSE&symbol=GCB&price=6.50"
```

---

## 3. Order Routing (Core SOR)

### 3a. Dry-run routing decision
```bash
curl -X POST http://localhost:9090/orders/route \
  -H "Content-Type: application/json" \
  -d '{"symbol":"GCB","side":"buy","quantity":500,"price":5.80}'
```
Expect: `primary_venue`, `legs`, `routing_latency_us < 500`.

### 3b. Submit a buy order
```bash
curl -X POST http://localhost:9090/orders/submit \
  -H "Content-Type: application/json" \
  -d '{"symbol":"GCB","side":"buy","quantity":500,"price":5.80,"base_currency":"USD"}'
```
Expect: `success: true`, `total_filled > 0`, `executions[].status: "filled"`.

### 3c. Sell order
```bash
curl -X POST http://localhost:9090/orders/submit \
  -H "Content-Type: application/json" \
  -d '{"symbol":"MTN","side":"sell","quantity":200,"price":150.00,"base_currency":"GHS"}'
```

### 3d. Market order (no price field)
```bash
curl -X POST http://localhost:9090/orders/submit \
  -H "Content-Type: application/json" \
  -d '{"symbol":"GCB","side":"buy","quantity":100}'
```

### 3e. Invalid symbol → 422
```bash
curl -X POST http://localhost:9090/orders/submit \
  -H "Content-Type: application/json" \
  -d '{"symbol":"INVALID","side":"buy","quantity":100,"price":1.00}'
```
Expect HTTP 422.

---

## 4. Pre-Trade Risk

```bash
# View current risk limits
curl http://localhost:9090/risk/limits

# Submit order that would breach notional limit (set limit low first)
curl -X POST http://localhost:9090/risk/limits \
  -H "Content-Type: application/json" \
  -d '{"max_order_notional": 100}'

curl -X POST http://localhost:9090/orders/submit \
  -H "Content-Type: application/json" \
  -d '{"symbol":"GCB","side":"buy","quantity":1000,"price":5.80}'
# Expect: rejected with risk breach message

# Reset limits
curl -X POST http://localhost:9090/risk/limits \
  -H "Content-Type: application/json" \
  -d '{"max_order_notional": 1000000}'
```

---

## 5. Positions

```bash
# View all positions after submitting orders
curl http://localhost:9090/positions

# View single symbol
curl http://localhost:9090/positions/GCB
```
Expect: `quantity`, `avg_cost`, `unrealised_pnl` fields.

---

## 6. Algo Strategies (TWAP / VWAP)

```bash
# Start a TWAP slice
curl -X POST http://localhost:9090/algo/twap \
  -H "Content-Type: application/json" \
  -d '{"symbol":"GCB","side":"buy","quantity":2000,"slices":4,"interval_seconds":2}'

# List running strategies
curl http://localhost:9090/algo/strategies

# Cancel a strategy (use id from above response)
curl -X DELETE http://localhost:9090/algo/strategies/<strategy_id>
```

---

## 7. Transaction Cost Analysis (TCA)

```bash
# Get TCA report for an executed order
curl http://localhost:9090/tca/<order_id>

# List recent TCA reports
curl http://localhost:9090/tca
```
Expect: `arrival_price`, `vwap`, `implementation_shortfall_bps`.

---

## 8. IOI Board

```bash
# Post an IOI (Indication of Interest)
curl -X POST http://localhost:9090/ioi/post \
  -H "Content-Type: application/json" \
  -d '{"symbol":"GCB","side":"buy","quantity":50000,"price":5.80,"firm_name":"FirmA","notes":"Block available"}'

# List active IOIs
curl http://localhost:9090/ioi/list

# List only sell-side IOIs for GCB
curl "http://localhost:9090/ioi/list?symbol=GCB&side=sell"

# Match two IOIs (buy + sell for same symbol)
curl -X POST http://localhost:9090/ioi/match \
  -H "Content-Type: application/json" \
  -d '{"id1":"<buy_ioi_id>","id2":"<sell_ioi_id>"}'

# Cancel an IOI
curl -X DELETE "http://localhost:9090/ioi/<ioi_id>?firm_name=FirmA"

# Board statistics
curl http://localhost:9090/ioi/stats
```
**Key checks:**
- Expired IOIs do not appear in default list
- Only the posting firm can cancel its own IOI
- Match fails if symbol or direction are incompatible

---

## 9. Dark Pool Crossing

```bash
# Add a buy order to the dark pool
curl -X POST http://localhost:9090/dark-pool/add \
  -H "Content-Type: application/json" \
  -d '{"symbol":"GCB","side":"buy","quantity":10000,"price":5.80,"firm_name":"FirmA"}'

# Add a matching sell order
curl -X POST http://localhost:9090/dark-pool/add \
  -H "Content-Type: application/json" \
  -d '{"symbol":"GCB","side":"sell","quantity":10000,"price":5.80,"firm_name":"FirmB"}'

# Attempt a crossing at midpoint
curl -X POST http://localhost:9090/dark-pool/cross \
  -H "Content-Type: application/json" \
  -d '{"symbol":"GCB","side":"buy","quantity":10000,"midpoint":5.80}'

# View dark pool order snapshot
curl http://localhost:9090/dark-pool/snapshot
curl "http://localhost:9090/dark-pool/snapshot?symbol=GCB"

# View crossing log
curl http://localhost:9090/dark-pool/crossing-log

# Statistics
curl http://localhost:9090/dark-pool/stats
```
**Key checks:**
- Cross response includes `crossed: true`, `cross_qty`, `cross_price == midpoint`
- `lit_qty` = quantity not crossed → should route to lit exchange
- Expired orders do not appear in snapshot

---

## 10. Block Trading

```bash
# Submit a block (minimum 5,000 shares)
curl -X POST http://localhost:9090/block-trade/submit \
  -H "Content-Type: application/json" \
  -d '{"symbol":"GCB","side":"buy","quantity":25000,"limit_price":5.85,"firm_name":"BuyFirm","contact":"trader@buyfirm.com"}'

# Attempt below minimum → 422
curl -X POST http://localhost:9090/block-trade/submit \
  -H "Content-Type: application/json" \
  -d '{"symbol":"GCB","side":"buy","quantity":100,"limit_price":5.85,"firm_name":"BuyFirm","contact":"trader@buyfirm.com"}'

# List open blocks
curl http://localhost:9090/block-trade/list
curl "http://localhost:9090/block-trade/list?symbol=GCB&status=open"

# Respond (counterparty)
curl -X POST http://localhost:9090/block-trade/<block_id>/respond \
  -H "Content-Type: application/json" \
  -d '{"firm_name":"SellFirm","quantity":25000,"counter_price":5.83,"notes":"Can fill all"}'

# Accept response (originating firm) — triggers SOR execution if agreed_price set
curl -X POST http://localhost:9090/block-trade/<block_id>/accept \
  -H "Content-Type: application/json" \
  -d '{"response_id":"<response_id>","agreed_price":5.84}'

# Cancel block
curl -X DELETE "http://localhost:9090/block-trade/<block_id>?firm_name=BuyFirm"
```
**Key checks:**
- Accept with `agreed_price` triggers a live SOR order; check `execution` field in response
- Only the originating firm can accept or cancel
- Status transitions: `open` → `negotiating` → `agreed` → `executed`

---

## 11. Iceberg Orders

```bash
# Create an iceberg: total 50,000 shares, show only 1,000 at a time
curl -X POST http://localhost:9090/iceberg/create \
  -H "Content-Type: application/json" \
  -d '{"symbol":"MTN","side":"buy","total_qty":50000,"display_qty":1000,"price":150.00,"base_currency":"GHS","firm_name":"FirmA"}'

# Simulate a fill of the displayed slice
curl -X POST http://localhost:9090/iceberg/<order_id>/fill \
  -H "Content-Type: application/json" \
  -d '{"filled_qty":1000,"avg_price":149.95}'

# After fill: remaining_qty decreases, a new display_qty slice is "released"
curl http://localhost:9090/iceberg/<order_id>

# List all icebergs
curl http://localhost:9090/iceberg/list
curl "http://localhost:9090/iceberg/list?status=active"

# Cancel an iceberg
curl -X DELETE http://localhost:9090/iceberg/<order_id>
```
**Key checks:**
- After each fill, `remaining_qty -= filled_qty`
- `display_qty` field in response always shows `min(display_qty, remaining_qty)`
- Status becomes `completed` when `remaining_qty == 0`
- Cancel sets status to `cancelled`

---

## 12. Basket / Portfolio Trading

```bash
# Submit a 3-stock basket
curl -X POST http://localhost:9090/basket/submit \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Africa Tech Basket",
    "legs": [
      {"symbol":"MTN","side":"buy","quantity":1000,"price":150.00},
      {"symbol":"GCB","side":"buy","quantity":5000,"price":5.80},
      {"symbol":"ECOBANK","side":"sell","quantity":2000,"price":8.50}
    ],
    "base_currency": "USD",
    "firm_name": "FirmA"
  }'

# Check basket status (each leg executed via SOR)
curl http://localhost:9090/basket/<basket_id>

# List all baskets
curl http://localhost:9090/basket/list

# Cancel a basket (only if status == pending)
curl -X DELETE http://localhost:9090/basket/<basket_id>
```
**Key checks:**
- `legs[].status` shows `filled` / `partial` / `failed` per symbol
- `overall_status` becomes `completed` when all legs processed
- Basket uses SOR for each leg — check `order_id` present per leg

---

## 13. Best Execution Reporting

```bash
# Submit an order and retrieve its best-execution report
curl -X POST http://localhost:9090/orders/submit \
  -H "Content-Type: application/json" \
  -d '{"symbol":"GCB","side":"buy","quantity":1000,"price":5.80}'
# Note the order_id in response

# Fetch best-exec report for that order
curl http://localhost:9090/best-execution/<order_id>
```
Expected fields: `venues_considered`, `venue_scores`, `primary_venue`, `vwap`,
`arrival_price`, `slippage_bps`, `fill_ratio`, `policy`, `quality_metric`,
`ts_received`, `ts_executed`.

```bash
# List recent reports
curl http://localhost:9090/best-execution/list
curl "http://localhost:9090/best-execution/list?symbol=GCB"

# Aggregate summary (avg slippage, fill rate)
curl http://localhost:9090/best-execution/summary
```
**Key checks:**
- Every `POST /orders/submit` automatically creates a best-exec record
- `slippage_bps` is negative (favourable) when filled below arrival price on a buy

---

## 14. Drop Copy

```bash
# Register a compliance webhook (use a test receiver, e.g. httpbin or ngrok)
curl -X POST http://localhost:9090/drop-copy/register \
  -H "Content-Type: application/json" \
  -d '{"url":"https://httpbin.org/post","label":"compliance-test"}'

# List registered endpoints
curl http://localhost:9090/drop-copy/endpoints

# Submit an order — drop copy fires automatically
curl -X POST http://localhost:9090/orders/submit \
  -H "Content-Type: application/json" \
  -d '{"symbol":"GCB","side":"buy","quantity":500,"price":5.80}'

# View drop copy delivery log
curl http://localhost:9090/drop-copy/log

# Statistics (delivery count, fail count)
curl http://localhost:9090/drop-copy/stats

# Remove an endpoint
curl -X DELETE "http://localhost:9090/drop-copy/remove?url=https://httpbin.org/post"
```
**Key checks:**
- Log entry shows `event: "ORDER_SUBMITTED"`, HTTP status 200 on delivery
- Failed deliveries logged with `status` and `error` — do not block order flow
- Disabled endpoint (`enabled: false`) skipped but stays in registry

---

## 15. Admin

```bash
# Halt all new orders
curl -X POST http://localhost:9090/admin/halt

# Verify orders are rejected while halted
curl -X POST http://localhost:9090/orders/submit \
  -H "Content-Type: application/json" \
  -d '{"symbol":"GCB","side":"buy","quantity":100,"price":5.80}'
# Expect 503 / halted error

# Resume
curl -X POST http://localhost:9090/admin/resume

# View audit log
curl http://localhost:9090/admin/audit-log
```

---

## 16. Cross-Feature Integration Tests

### 16a. IOI → Block Trade flow
1. Post a buy IOI for 50,000 GCB
2. Post a matching sell IOI
3. Match the two IOIs (`POST /ioi/match`)
4. Upgrade to a Block Trade (`POST /block-trade/submit`) for the agreed quantity
5. Accept the block and confirm SOR execution fires

### 16b. Dark Pool → Lit fallback
1. Add a buy to the dark pool (10,000 shares)
2. Cross with only 6,000 available on sell side
3. Verify `crossed_qty = 6000` and `lit_qty = 4000`
4. Submit a normal SOR order for the lit 4,000 remainder

### 16c. Iceberg auto-slice + best execution
1. Create an iceberg (total 20,000, display 2,000)
2. Record 5 consecutive fills of 2,000
3. After the 10th fill (final), confirm status = `completed`
4. Check that each fill's `POST /orders/submit` produced a best-execution record

### 16d. Basket + drop copy
1. Register a test drop-copy endpoint
2. Submit a 3-leg basket
3. Confirm 3 drop-copy entries appear in log (one per leg's SOR order)

---

## 17. Regression Checklist (run after any code change)

| # | Check | Command |
|---|-------|---------|
| 1 | Import clean | `python -c "from api.gateway import app"` |
| 2 | Health OK | `curl /health` → `"status":"healthy"` |
| 3 | Order submit | `POST /orders/submit` → `success:true` |
| 4 | Best exec auto-record | `GET /best-execution/<id>` after submit |
| 5 | Drop copy fires | log entry after submit (if endpoint registered) |
| 6 | IOI board round-trip | post → list → cancel |
| 7 | Dark pool cross | add buy+sell → cross → crossed_qty > 0 |
| 8 | Block trade lifecycle | submit → respond → accept → executed |
| 9 | Iceberg refill | create → fill slice → remaining_qty decreases |
| 10 | Basket all legs | submit 2-leg basket → both legs have order_id |
