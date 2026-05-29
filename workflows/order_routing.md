# Order Routing Workflow

## Objective
Route a client order to the optimal African exchange venue(s) and execute all legs in parallel.

## Required Inputs
- `symbol` — ticker (e.g. `GCB`, `MTNGH`)
- `side` — `buy` or `sell`
- `quantity` — number of shares
- `price` — limit price in USD (omit for market order)
- `base_currency` — client's currency (default `USD`)

## Steps

### 1. Validate the order
- Symbol must exist in at least one enabled venue (see `configs/venues.yaml`)
- Quantity > 0; price > 0 if limit order
- If symbol is unknown, return 422 with list of valid symbols per venue

### 2. Call POST /orders/route (dry-run)
```bash
curl -X POST http://localhost:9090/orders/route \
  -H "Content-Type: application/json" \
  -d '{"symbol":"GCB","side":"buy","quantity":5000,"price":5.80}'
```
Inspect the routing decision:
- `primary_venue` — best-scored exchange
- `legs` — allocation per venue (only >1 if split)
- `routing_latency_us` — should be <500µs per PDF §5

### 3. Execute via POST /orders/submit
Same payload as `/route`. Engine executes all legs in parallel threads.
Response includes:
- `executions[].status` — `filled` | `partial` | `rejected` | `failed`
- `total_filled` — shares actually filled
- `success` — true if any quantity was filled

### 4. Handle partial fills
- If `total_filled < quantity`, retry with remaining quantity
- Check circuit breaker state at `/health` before retrying
- If a venue shows `open` state, it is temporarily excluded from routing

## Venue Scoring Logic
Scores are normalized 0–1, weighted per the PDF spec:

| Factor        | Weight | Higher is better when...               |
|---------------|--------|----------------------------------------|
| Liquidity     | 30%    | More shares available at top 3 levels  |
| Spread        | 20%    | Bid/ask spread is tighter              |
| Fee           | 20%    | Taker fee is lower                     |
| FX cost       | 20%    | No currency conversion needed          |
| Latency       | 10%    | Exchange round-trip is faster          |

Weights configurable in `configs/sor_config.yaml`.

## Edge Cases
- **No order book found**: SOR falls back to first enabled venue with no price check
- **All venues circuit-broken**: Returns 422 "No venues available"
- **Market order**: Price derived from best ask (buy) or best bid (sell) at routing time
- **Order too large**: Split across up to `max_splits` venues (default 5)

## Tools Used
- `tools/smart_order_router.py` — venue scoring and order splitting
- `tools/execution_engine.py` — parallel FIX order submission
- `tools/circuit_breaker.py` — venue health gating
- `tools/fix_engine.py` — FIX message construction
