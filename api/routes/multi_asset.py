"""Multi-asset order endpoints: bonds and FX."""
import time
import uuid
from fastapi import APIRouter, HTTPException

from api.models import (
    BondOrderRequest, BondOrderResponse,
    FXOrderRequest, FXOrderResponse,
)

router = APIRouter(prefix="/orders", tags=["Multi-Asset Orders"])


def _get_state():
    from app_state import get_app_state
    return get_app_state()


def _check_halted(state):
    if state.halted:
        raise HTTPException(status_code=503, detail="System halted — order routing disabled")


@router.post("/bond/submit", response_model=BondOrderResponse,
             summary="Submit a fixed-income (bond) order")
async def submit_bond_order(req: BondOrderRequest):
    """
    Route and execute a fixed-income order.
    Computes accrued interest, dirty price, and total consideration.
    Runs pre-trade risk check against bond notional before routing.
    """
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    _check_halted(state)

    # Pre-trade risk check — bond notional
    violation = state.risk.check(
        symbol=req.isin,
        side=req.side.value,
        quantity=1,
        price=req.clean_price_pct,
        base_currency=req.base_currency,
        asset_class="bond",
        face_value=req.face_value,
    )
    if violation:
        raise HTTPException(
            status_code=422,
            detail=f"Risk check failed [{violation.check}]: {violation.detail}",
        )

    from tools.asset_handlers.bond_handler import BondHandler, BondOrderSpec
    try:
        spec = BondOrderSpec(
            isin=req.isin,
            bond_type=req.bond_type,
            clean_price_pct=req.clean_price_pct,
            face_value=req.face_value,
            coupon_rate=req.coupon_rate,
            yield_to_mat=req.yield_to_maturity,
            maturity_date=req.maturity_date,
            settlement_days=req.settlement_days,
            day_count_conv=req.day_count_conv,
        )
        result = BondHandler().prepare(spec)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Bond preparation error: {exc}")

    order_id = f"BND-{uuid.uuid4().hex[:8].upper()}"
    state.risk.record_fill(1, result.total_consideration)

    return BondOrderResponse(
        order_id=order_id,
        isin=req.isin,
        side=req.side.value,
        face_value=req.face_value,
        clean_price_pct=req.clean_price_pct,
        accrued_interest=result.accrued_interest,
        dirty_price_pct=result.dirty_price_pct,
        total_consideration=result.total_consideration,
        settlement_date=result.settlement_date,
        yield_to_maturity=result.yield_to_maturity,
        success=True,
        message=f"Bond order {order_id} prepared — {req.bond_type} {req.isin}",
        timestamp=time.time(),
    )


@router.post("/fx/submit", response_model=FXOrderResponse,
             summary="Submit a foreign exchange (FX) order")
async def submit_fx_order(req: FXOrderRequest):
    """
    Route and execute an FX spot or forward order.
    Supports G10 pairs and African EM pairs (USDGHS, USDNGN, USDZAR, USDKES).
    Runs pre-trade risk check against base currency notional before routing.
    """
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    _check_halted(state)

    # Pre-trade risk check — FX notional = base amount
    violation = state.risk.check(
        symbol=req.pair,
        side=req.side.value,
        quantity=req.base_amount,
        price=req.spot_rate,
        base_currency=req.base_currency,
        asset_class="fx",
        base_amount=req.base_amount,
    )
    if violation:
        raise HTTPException(
            status_code=422,
            detail=f"Risk check failed [{violation.check}]: {violation.detail}",
        )

    from tools.asset_handlers.fx_handler import FXHandler, FXOrderSpec
    # Pull live FX rate from simulation if not provided
    live_rate = None
    try:
        live_rate = state.fx_md.get_rate(req.pair)
    except AttributeError:
        pass

    try:
        spec = FXOrderSpec(
            pair=req.pair,
            side=req.side.value,
            base_amount=req.base_amount,
            spot_rate=req.spot_rate,
            tenor=req.tenor,
            forward_points=req.forward_points,
            ndf=req.ndf,
            settlement_currency=req.settlement_currency,
        )
        result = FXHandler().prepare(spec, live_rate=live_rate)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"FX preparation error: {exc}")

    order_id = f"FX-{uuid.uuid4().hex[:8].upper()}"
    state.risk.record_fill(req.base_amount, result.spec.spot_rate or 1.0)

    return FXOrderResponse(
        order_id=order_id,
        pair=f"{result.base_ccy}/{result.quote_ccy}",
        side=req.side.value,
        base_ccy=result.base_ccy,
        quote_ccy=result.quote_ccy,
        base_amount=result.notional_base,
        notional_quote=result.notional_quote,
        spot_rate=result.spec.spot_rate,
        settlement_date=result.settlement_date,
        lot_type=result.lot_type,
        pip_size=result.pip_size,
        is_em_pair=result.is_em_pair,
        success=True,
        message=f"FX order {order_id} prepared — {result.base_ccy}/{result.quote_ccy} {req.tenor}",
        timestamp=time.time(),
    )
