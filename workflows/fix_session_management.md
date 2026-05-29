# FIX Session Management Workflow

## Objective
Establish, maintain, and gracefully close FIX 4.2 sessions with each African exchange.

## FIX Session Lifecycle
```
Logon (A) → [Active: Heartbeat/Orders] → Logout (5)
     ↑               ↓
     └── Reconnect ← Session Drop / Timeout
```

## Per-Venue Session Config

| Venue | Host                  | Port | SenderCompID | TargetCompID  |
|-------|-----------------------|------|--------------|---------------|
| GSE   | fix.gse.com.gh        | 9876 | BROKER_GH    | GSE_TRADING   |
| JSE   | fix.jse.co.za         | 9877 | BROKER_ZA    | JSE_TRADING   |
| NGX   | fix.ngxgroup.com      | 9878 | BROKER_NG    | NGX_TRADING   |
| NSE   | fix.nse.co.ke         | 9879 | BROKER_KE    | NSE_TRADING   |

All connections require TLS 1.3 in production.

## Steps

### 1. Configure credentials
Add to `.env`:
```
GSE_FIX_PASSWORD=<your_password>
JSE_FIX_PASSWORD=<your_password>
NGX_FIX_PASSWORD=<your_password>
NSE_FIX_PASSWORD=<your_password>
```

### 2. Enable a venue
Edit `configs/venues.yaml`: set `enabled: true` for the target venue.
Then update the adapter stub in `tools/venue_adapters/{venue}_adapter.py` to open a real socket:
```python
import ssl, socket
ctx  = ssl.create_default_context()
sock = ctx.wrap_socket(socket.create_connection((host, port)), server_hostname=host)
sock.sendall(self._session.logon_message())
```

### 3. Heartbeat maintenance
`FIXSession.is_heartbeat_due()` returns True after `heartbeat_interval` seconds (default 30s).
Call `gse.send_heartbeat()` from a background thread every 5s to check:
```python
while True:
    gse.send_heartbeat()
    time.sleep(5)
```

### 4. Check session health
```bash
curl http://localhost:9090/health
```
Look at `venues[].circuit_breaker_state`:
- `closed` — healthy, orders routing normally
- `half_open` — recovering, limited orders allowed
- `open` — tripped, venue excluded from routing (circuit opens after 5 failures)

### 5. Circuit breaker thresholds (configurable in sor_config.yaml)
| Parameter          | Default | Meaning                                      |
|--------------------|---------|----------------------------------------------|
| failure_threshold  | 5       | Failures before circuit opens                |
| success_threshold  | 3       | Successes in half-open to close circuit      |
| timeout_seconds    | 30      | Seconds before half-open probe attempt       |

## Tools Used
- `tools/fix_engine.py` — `FIXSession`, `build_logon()`, `build_heartbeat()`
- `tools/circuit_breaker.py` — exchange health gating
- `tools/venue_adapters/gse_adapter.py` — GSE-specific TLS + tick-size logic
