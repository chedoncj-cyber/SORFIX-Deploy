"""Market data and order book endpoints."""
from fastapi import APIRouter, HTTPException, Query
from typing import List

from api.models import OrderBookResponse, OrderBookLevel, MetricsResponse

router = APIRouter(prefix="/market-data", tags=["Market Data"])


def _get_state():
    from app_state import get_app_state
    return get_app_state()


def _check_venue(state, venue: str):
    """Raise 404 if venue is unknown or disabled."""
    vcfg = state.sor.venues.get(venue)
    if vcfg is None:
        raise HTTPException(status_code=404, detail=f"Venue '{venue}' not found")
    if not vcfg.enabled:
        raise HTTPException(status_code=404, detail=f"Venue '{venue}' is disabled")


def _book_to_response(book) -> OrderBookResponse:
    return OrderBookResponse(
        symbol=book.symbol,
        venue=book.venue,
        bids=[OrderBookLevel(price=l.price, quantity=l.quantity, venue=l.venue) for l in book.bids],
        asks=[OrderBookLevel(price=l.price, quantity=l.quantity, venue=l.venue) for l in book.asks],
        spread=book.spread,
        best_bid=book.best_bid.price if book.best_bid else None,
        best_ask=book.best_ask.price if book.best_ask else None,
    )


@router.get("/book/{venue}/{symbol}", response_model=OrderBookResponse,
            summary="Get order book for a venue:symbol")
async def get_order_book(venue: str, symbol: str):
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {exc}")
    venue  = venue.upper()
    symbol = symbol.upper()
    _check_venue(state, venue)
    book = state.cache.get(venue, symbol)
    if book is None:
        raise HTTPException(status_code=404, detail=f"No order book for {venue}:{symbol}")
    return _book_to_response(book)


@router.get("/books/{symbol}", response_model=List[OrderBookResponse],
            summary="Get order books across all enabled venues")
async def get_all_books(symbol: str):
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {exc}")
    symbol = symbol.upper()
    enabled = {name for name, v in state.sor.venues.items() if v.enabled}
    books = [b for b in state.cache.get_all_venues_for_symbol(symbol) if b.venue in enabled]
    if not books:
        raise HTTPException(status_code=404, detail=f"No order books found for {symbol}")
    return [_book_to_response(b) for b in books]


@router.get("/pipeline/stats", summary="Market data pipeline statistics")
async def pipeline_stats():
    try:
        return _get_state().pipeline.get_stats()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {exc}")


@router.get("/metrics", response_model=MetricsResponse, summary="System-wide metrics snapshot")
async def metrics_snapshot():
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {exc}")
    return MetricsResponse(
        market_data=state.pipeline.get_stats(),
        execution=state.execution.get_stats(),
        cache=state.cache.stats(),
        fx_rates=state.fx.get_all_rates(),
    )


@router.get("/symbols", summary="All tradeable symbols by venue")
async def list_symbols():
    """Return the full symbol catalog — static set defined in the market data pipeline."""
    from tools.market_data_pipeline import VENUE_SYMBOLS
    return {venue: sorted(syms.keys()) for venue, syms in VENUE_SYMBOLS.items()}


@router.post("/inject-price", summary="Override a venue price (testing only)")
async def inject_price(venue: str, symbol: str, price: float = Query(..., gt=0)):
    """Force a specific mid-price into the simulation pipeline for SOR routing tests."""
    try:
        state = _get_state()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=f"Service unavailable: {exc}")
    venue  = venue.upper()
    symbol = symbol.upper()
    _check_venue(state, venue)
    valid = state.pipeline.get_valid_symbols(venue)
    if symbol not in valid:
        raise HTTPException(status_code=404, detail=f"Symbol '{symbol}' not found on venue '{venue}'")
    state.pipeline.inject_price(venue, symbol, price)
    return {"ok": True, "venue": venue, "symbol": symbol, "price": price}
