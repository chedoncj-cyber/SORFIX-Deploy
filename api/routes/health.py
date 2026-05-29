"""Health and readiness endpoints (used by Kubernetes liveness/readiness probes)."""
import time
from fastapi import APIRouter, HTTPException, Response

from api.models import HealthResponse, VenueStatusResponse

router = APIRouter(tags=["Health"])

_start_time = time.time()


def _get_state():
    from app_state import get_app_state
    return get_app_state()


@router.get("/health", response_model=HealthResponse, summary="Liveness probe")
async def health():
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {exc}")

    cb_stats = {s["name"]: s for s in state.sor.get_circuit_breaker_stats()}
    ex_stats = state.execution.get_stats()
    pd_stats = state.pipeline.get_stats()

    venues = [
        VenueStatusResponse(
            venue=name,
            enabled=vcfg.enabled,
            currency=vcfg.currency,
            taker_fee_bps=vcfg.taker_fee * 10_000,
            latency_ms=vcfg.latency_ms,
            circuit_breaker_state=cb_stats.get(name, {}).get("state", "unknown"),
        )
        for name, vcfg in state.sor.venues.items()
    ]

    return HealthResponse(
        status="healthy",
        uptime_seconds=round(time.time() - _start_time, 1),
        market_data_updates=pd_stats["updates_processed"],
        executions=ex_stats["executions"],
        failures=ex_stats["failures"],
        cache_books=state.cache.stats()["total_books"],
        venues=venues,
    )


@router.get("/ready", summary="Readiness probe")
async def ready(response: Response):
    try:
        state = _get_state()
    except RuntimeError:
        response.status_code = 503
        return {"status": "not_ready", "reason": "app state not initialized"}

    stats = state.pipeline.get_stats()
    if not stats["running"] or stats["updates_processed"] == 0:
        response.status_code = 503
        return {"status": "not_ready", "reason": "market data pipeline not yet populated"}
    return {"status": "ready"}


@router.get("/metrics/prometheus", response_class=Response, summary="Prometheus text format metrics")
async def prometheus_metrics():
    from tools.monitoring import metrics
    text = metrics.prometheus_text()
    return Response(content=text, media_type="text/plain; version=0.0.4; charset=utf-8")
