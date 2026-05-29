# Market Data Ingestion Workflow

## Objective
Continuously ingest order book updates from African exchanges into the in-memory
ShardedOrderBookCache, feeding real-time data to the Smart Order Router.

## Architecture
```
Exchange FIX Feed → Kafka Topic (per venue) → MarketDataPipeline → ShardedOrderBookCache
                                                      ↓
                                               SmartOrderRouter (reads cache)
```

In simulation mode (default), the pipeline generates realistic random-walk prices
without requiring a live Kafka cluster or exchange connection.

## Steps

### 1. Start the pipeline (automatic at server startup)
The pipeline starts automatically in `app_state.init_app_state()`.
Check it is running:
```bash
curl http://localhost:9090/market-data/pipeline/stats
```
Expected: `"running": true`, `updates_processed` incrementing.

### 2. Query a live order book
```bash
curl http://localhost:9090/market-data/book/GSE/GCB
```
Returns top-of-book bid/ask, full depth (5 levels), and mid-spread.

### 3. Query all venues for a symbol
```bash
curl http://localhost:9090/market-data/books/MTN
```
Returns order books from every venue that has the symbol (useful for cross-venue spread comparison).

### 4. Stream via WebSocket
```
ws://localhost:9090/ws/book/GSE/GCB
```
Pushes a JSON snapshot every 500ms with best_bid, best_ask, spread, and top 5 levels.

### 5. Inject a test price (testing only)
```bash
curl -X POST "http://localhost:9090/market-data/inject-price?venue=GSE&symbol=GCB&price=6.00"
```
Forces a price override — the SOR will route to a different venue if this creates arbitrage.

## Connecting to Real Kafka (Production)
1. Set `use_kafka: true` in `configs/sor_config.yaml`
2. Set `KAFKA_BROKERS=kafka:9092` in `.env`
3. Replace `_tick()` in `tools/market_data_pipeline.py` with a Kafka consumer loop:
   ```python
   from kafka import KafkaConsumer
   consumer = KafkaConsumer("market-data-gse", bootstrap_servers=KAFKA_BROKERS)
   for msg in consumer:
       book = parse_market_data(msg.value)
       self.cache.put(book)
   ```

## Cache Design
- 256 shards, keyed by `{venue}:{symbol}`
- Each shard has its own RLock — minimizes contention at 50k+ updates/sec
- Zero-allocation on read hot path (`cache.get()`)

## Tools Used
- `tools/market_data_pipeline.py` — price simulation and cache population
- `tools/order_book_cache.py` — sharded in-memory store
