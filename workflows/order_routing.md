# Order Routing Workflow

## Objective
Route a client order to the optimal exchange venue(s) and execute all legs in parallel.
Covers standard limit/market orders, algo strategies, and institutional order types
(Iceberg, Basket, Block Trade, Dark Pool crossing).

## Required Inputs (standard order)
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

After every successful submission, two hooks fire automatically:
- **Drop Copy** — pushes `ORDER_SUBMITTED` event to all registered compliance endpoints (`tools/drop_copy.py`)
- **Best Execution** — records a MiFID II audit report for the order (`tools/best_execution.py`)

### 4. Handle partial fills
- If `total_filled < quantity`, retry with remaining quantity
- Check circuit breaker state at `/health` before retrying
- If a venue shows `open` state, it is temporarily excluded from routing

## Venue Scoring Logic
Scores are normalized 0–1, weighted per the PDF spec:

| Factor      | Weight | Higher is better when...              |
|-------------|--------|---------------------------------------|
| Liquidity   | 28%    | More shares available at top 3 levels |
| Spread      | 18%    | Bid/ask spread is tighter             |
| FX cost     | 18%    | No currency conversion needed         |
| Fee         | 16%    | Taker fee is lower                    |
| Latency     | 10%    | Exchange round-trip is faster         |
| Reliability | 10%    | Circuit breaker success history       |

Weights configurable in `configs/sor_config.yaml`.

## Edge Cases
- **No order book found**: SOR falls back to first enabled venue with no price check
- **All venues circuit-broken**: Returns 422 "No venues available"
- **Market order**: Price derived from best ask (buy) or best bid (sell) at routing time
- **Order too large**: Split across up to `max_splits` venues (default 5)

## Institutional Order Types

### Iceberg Orders
Large orders sliced so only `display_qty` is visible to the market at any time.
Each filled slice triggers a refill from the hidden remainder.
FIX 5.0 wire: `DisplayQty (tag 1138)` on the NewOrderSingle (35=D).
See `tools/iceberg_manager.py` and `POST /iceberg/create`.

### Basket / Portfolio Orders
Multiple symbols submitted as one instruction; each leg is routed independently via SOR.
Useful for index rebalancing or multi-stock strategies.
FIX 5.0 wire: `NewOrderList (35=E)` — `build_new_order_list()` in `tools/fix_engine.py`.
See `tools/basket_engine.py` and `POST /basket/submit`.

### Block Trades
Large negotiated trades (>= 5,000 shares) between two named counterparties.
Workflow: submit → respond → accept (optionally fires a SOR order for execution).
See `tools/block_trade.py` and `POST /block-trade/submit`.

### Dark Pool Crossing
Orders are first attempted in the internal dark pool at the mid-price.
Only the unmatched remainder routes to a lit exchange, minimising market impact.
See `tools/dark_pool.py` and `POST /dark-pool/cross`.

## Tools Used
- `tools/smart_order_router.py` — venue scoring and order splitting
- `tools/execution_engine.py` — parallel FIX order submission
- `tools/circuit_breaker.py` — venue health gating
- `tools/fix_engine.py` — FIX message construction
- `tools/drop_copy.py` — real-time compliance webhook push (fires on every submit)
- `tools/best_execution.py` — MiFID II per-order audit trail (fires on every submit)
- `tools/iceberg_manager.py` — display-slice management
- `tools/basket_engine.py` — multi-leg portfolio execution
- `tools/block_trade.py` — large-order negotiation workflow
- `tools/dark_pool.py` — internal crossing engine
