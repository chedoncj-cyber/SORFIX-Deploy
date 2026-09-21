"""Order submission, routing, and history endpoints."""
import time
from fastapi import APIRouter, HTTPException, Query

from api.models import (
    OrderRequest, OrderResponse, RoutingDecisionResponse,
    RoutingLegResponse, ExecutionReportResponse, VenueScoreResponse,
)
from tools.smart_order_router import Order, OrderSide

router = APIRouter(prefix="/orders", tags=["Orders"])


def _check_halted(state):
    if state.halted:
        raise HTTPException(status_code=503, detail="System halted — order routing disabled")


def _get_state():
    from app_state import get_app_state
    return get_app_state()


def _routing_response(decision) -> RoutingDecisionResponse:
    return RoutingDecisionResponse(
        order_id=decision.order_id,
        symbol=decision.symbol,
        total_quantity=decision.total_quantity,
        primary_venue=decision.primary_venue,
        legs=[
            RoutingLegResponse(
                venue=leg.venue,
                symbol=leg.symbol,
                quantity=leg.quantity,
                price=leg.price,
                currency=leg.currency,
                estimated_cost=leg.estimated_cost,
            )
            for leg in decision.legs
        ],
        routing_latency_us=decision.routing_latency_us,
        is_split=decision.is_split,
        timestamp=decision.timestamp,
        venue_scores=[
            VenueScoreResponse(
                venue=s.venue,
                score=round(s.total, 6),
                liquidity=round(s.liquidity, 6),
                spread=round(s.spread, 6),
                fee=round(s.fee, 6),
                fx_cost=round(s.fx_cost, 6),
                latency=round(s.latency, 6),
                available_qty=s.available_qty,
                reliability=round(s.reliability, 6),
            )
            for s in decision.venue_scores
        ],
    )


def _build_order(req: OrderRequest, state) -> Order:
    return Order(
        symbol=req.symbol.upper(),
        side=OrderSide(req.side.value),
        quantity=req.quantity,
        price=req.price,
        base_currency=req.base_currency,
        max_splits=req.max_splits if req.max_splits is not None else state.sor.config.max_splits,
        min_split_qty=req.min_split_qty if req.min_split_qty is not None else state.sor.config.min_split_qty,
    )


@router.post("/route", response_model=RoutingDecisionResponse, summary="Get routing decision (no execution)")
async def route_order(req: OrderRequest):
    """Compute the optimal routing plan without executing the order."""
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {exc}")
    _check_halted(state)
    # Pre-trade risk check (no fill recorded — this is routing only)
    violation = state.risk.check(
        symbol=req.symbol, side=req.side.value,
        quantity=req.quantity, price=req.price,
        base_currency=req.base_currency,
    )
    if violation:
        raise HTTPException(
            status_code=422,
            detail=f"Risk check failed [{violation.check}]: {violation.detail}",
        )
    try:
        decision = state.sor.route(_build_order(req, state))
    except RuntimeError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return _routing_response(decision)


@router.post("/submit", response_model=OrderResponse, summary="Route and execute an order")
async def submit_order(req: OrderRequest):
    """Route the order across venues and execute all legs in parallel."""
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {exc}")
    _check_halted(state)

    # Pre-trade risk check
    pos = state.positions.get_position(req.symbol)
    current_qty = pos.net_qty if pos else 0.0
    violation = state.risk.check(
        symbol=req.symbol, side=req.side.value,
        quantity=req.quantity, price=req.price,
        base_currency=req.base_currency,
        current_position_qty=current_qty,
    )
    if violation:
        raise HTTPException(
            status_code=422,
            detail=f"Risk check failed [{violation.check}]: {violation.detail}",
        )

    order = _build_order(req, state)
    try:
        decision = state.sor.route(order)
    except RuntimeError as e:
        raise HTTPException(status_code=422, detail=str(e))
    try:
        result = state.execution.execute(decision, order.side)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution error: {e}")

    fill_ratio = result.total_filled / decision.total_quantity if decision.total_quantity > 0 else 0.0
    vwap = result.total_cost / result.total_filled if result.total_filled > 0 else None

    response = OrderResponse(
        order_id=decision.order_id,
        side=order.side.value,
        routing=_routing_response(decision),
        executions=[
            ExecutionReportResponse(
                leg_venue=r.leg.venue,
                status=r.status.value,
                filled_qty=r.filled_qty,
                avg_price=r.avg_price if r.filled_qty > 0 else None,
                message=r.message,
                attempts=r.attempts,
            )
            for r in result.reports
        ],
        total_filled=result.total_filled,
        total_cost=result.total_cost,
        success=result.success,
        fill_ratio=round(fill_ratio, 6),
        vwap=round(vwap, 6) if vwap is not None else None,
        timestamp=time.time(),
    )
    data = response.model_dump()
    state.order_store.save(decision.order_id, data)
    state.db.save(decision.order_id, data)
    # Update positions and risk counters after confirmed fill
    if result.total_filled > 0 and vwap is not None:
        state.positions.record_fill(req.symbol.upper(), order.side.value,
                                    result.total_filled, vwap)
        state.risk.record_fill(result.total_filled, vwap)
    return response


@router.get("/{order_id}", response_model=OrderResponse, summary="Look up a submitted order by ID")
async def get_order(order_id: str):
    """Retrieve a previously submitted order from the in-memory history store."""
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {exc}")
    data = state.order_store.get(order_id.upper())
    if data is None:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")
    return data


@router.get("/", summary="List recent submitted orders")
async def list_orders(limit: int = Query(default=20, ge=1, le=200)):
    """Return the most recent submitted orders (up to limit, newest last)."""
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {exc}")
    orders = state.order_store.recent(limit)
    return {"count": len(orders), "total_stored": state.order_store.count(), "orders": orders}
