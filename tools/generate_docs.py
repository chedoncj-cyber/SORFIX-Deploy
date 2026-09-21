"""
Generate Pan SORFIX — Version 3 Technical Documentation (.docx)
Run: python tools/generate_docs.py
"""
import subprocess
import sys
from datetime import datetime
from pathlib import Path

try:
    from docx import Document
    from docx.shared import Pt, RGBColor, Inches, Cm
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
    from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    import docx.opc.constants
except ImportError:
    print("pip install python-docx"); sys.exit(1)


# ── Colour palette ────────────────────────────────────────────────────────────
NAVY      = RGBColor(0x1A, 0x23, 0x7E)
BLUE      = RGBColor(0x28, 0x35, 0x93)
TEAL      = RGBColor(0x00, 0x69, 0x8A)
GREEN     = RGBColor(0x1B, 0x5E, 0x20)
GOLD      = RGBColor(0xF5, 0x9E, 0x0B)
DARK_GREY = RGBColor(0x21, 0x21, 0x21)
MID_GREY  = RGBColor(0x55, 0x55, 0x55)
LIGHT_BG  = RGBColor(0xE8, 0xEA, 0xF6)
GSE_GREEN = RGBColor(0x1B, 0x5E, 0x20)
JSE_BLUE  = RGBColor(0x0D, 0x47, 0xA1)
NGX_RED   = RGBColor(0xB7, 0x1C, 0x1C)
NSE_PURP  = RGBColor(0x4A, 0x14, 0x8C)
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
ROW_LIGHT = RGBColor(0xF5, 0xF5, 0xF5)
ROW_BLUE  = RGBColor(0xE3, 0xF2, 0xFD)


def set_cell_bg(cell, hex_color: str):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement("w:shd")
    shd.set(qn("w:val"),   "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"),  hex_color)
    tcPr.append(shd)


def set_cell_border(cell, top=None, bottom=None, left=None, right=None):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for side, val in [("top", top), ("bottom", bottom), ("left", left), ("right", right)]:
        if val:
            el = OxmlElement(f"w:{side}")
            el.set(qn("w:val"),   val.get("val",   "single"))
            el.set(qn("w:sz"),    val.get("sz",    "4"))
            el.set(qn("w:space"), val.get("space", "0"))
            el.set(qn("w:color"), val.get("color", "auto"))
            tcBorders.append(el)
    tcPr.append(tcBorders)


def add_page_break(doc):
    doc.add_page_break()


def styled_heading(doc, text, level=1, color=None, space_before=18, space_after=6):
    p = doc.add_heading(text, level=level)
    run = p.runs[0] if p.runs else p.add_run(text)
    run.font.color.rgb = color or NAVY
    run.font.bold = True
    run.font.name = "Calibri"
    if level == 1:
        run.font.size = Pt(22)
    elif level == 2:
        run.font.size = Pt(16)
    elif level == 3:
        run.font.size = Pt(13)
    else:
        run.font.size = Pt(11)
    pf = p.paragraph_format
    pf.space_before = Pt(space_before)
    pf.space_after  = Pt(space_after)
    return p


def body_para(doc, text, bold=False, italic=False, color=None,
              size=10.5, space_after=4, indent=None, align=None):
    p   = doc.add_paragraph()
    run = p.add_run(text)
    run.font.name   = "Calibri"
    run.font.size   = Pt(size)
    run.font.bold   = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = color
    pf = p.paragraph_format
    pf.space_after  = Pt(space_after)
    pf.space_before = Pt(0)
    if indent:
        pf.left_indent = Inches(indent)
    if align:
        p.alignment = align
    return p


def bullet(doc, text, level=0, color=None):
    p   = doc.add_paragraph(style="List Bullet")
    run = p.add_run(text)
    run.font.name = "Calibri"
    run.font.size = Pt(10.5)
    if color:
        run.font.color.rgb = color
    p.paragraph_format.left_indent   = Inches(0.25 * (level + 1))
    p.paragraph_format.space_after   = Pt(2)
    p.paragraph_format.space_before  = Pt(2)
    return p


def add_table(doc, headers, rows, header_bg="1A237E", alt_color="F5F5F5",
              col_widths=None):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.LEFT

    # Header row
    hdr = table.rows[0]
    for i, h in enumerate(headers):
        cell = hdr.cells[i]
        set_cell_bg(cell, header_bg)
        p   = cell.paragraphs[0]
        run = p.add_run(h)
        run.font.bold  = True
        run.font.size  = Pt(9)
        run.font.color.rgb = WHITE
        run.font.name  = "Calibri"
        p.alignment    = WD_ALIGN_PARAGRAPH.CENTER
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

    # Data rows
    for ri, row in enumerate(rows):
        tr = table.rows[ri + 1]
        bg = alt_color if ri % 2 == 0 else "FFFFFF"
        for ci, val in enumerate(row):
            cell = tr.cells[ci]
            set_cell_bg(cell, bg)
            p   = cell.paragraphs[0]
            run = p.add_run(str(val))
            run.font.size = Pt(9)
            run.font.name = "Calibri"
            run.font.color.rgb = DARK_GREY
            p.alignment   = WD_ALIGN_PARAGRAPH.CENTER

    if col_widths:
        for i, w in enumerate(col_widths):
            for row in table.rows:
                row.cells[i].width = Inches(w)

    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    return table


def divider(doc, color="1A237E"):
    p  = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_before = Pt(4)
    pf.space_after  = Pt(4)
    border = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"),   "single")
    bottom.set(qn("w:sz"),    "6")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), color)
    border.append(bottom)
    p._p.get_or_add_pPr().append(border)
    return p


def build_doc() -> Document:
    doc = Document()

    # Page margins
    for section in doc.sections:
        section.top_margin    = Cm(2.0)
        section.bottom_margin = Cm(2.0)
        section.left_margin   = Cm(2.5)
        section.right_margin  = Cm(2.5)

    now = datetime.now()

    # ── COVER PAGE ────────────────────────────────────────────────────────────
    doc.add_paragraph().paragraph_format.space_after = Pt(40)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = title.add_run("Pan SORFIX")
    r.font.name  = "Calibri"
    r.font.size  = Pt(32)
    r.font.bold  = True
    r.font.color.rgb = NAVY

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = sub.add_run("Pan-African Smart Order Router")
    r2.font.name  = "Calibri"
    r2.font.size  = Pt(18)
    r2.font.color.rgb = TEAL

    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    divider(doc)

    ver = doc.add_paragraph()
    ver.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rv = ver.add_run("Version 3.0  ·  Technical Documentation")
    rv.font.name = "Calibri"; rv.font.size = Pt(13); rv.font.color.rgb = BLUE

    dt = doc.add_paragraph()
    dt.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rd = dt.add_run(f"Date: {now.strftime('%d %B %Y')}  ·  Classification: Confidential")
    rd.font.name = "Calibri"; rd.font.size = Pt(10); rd.font.color.rgb = MID_GREY

    doc.add_paragraph().paragraph_format.space_after = Pt(12)
    divider(doc)
    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    # Exchange badges on cover
    exch = doc.add_paragraph()
    exch.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for label, col in [
        ("  🇬🇭 GSE · Ghana  ", GSE_GREEN),
        ("  🇿🇦 JSE · South Africa  ", JSE_BLUE),
        ("  🇳🇬 NGX · Nigeria  ", NGX_RED),
        ("  🇰🇪 NSE · Kenya  ", NSE_PURP),
    ]:
        r = exch.add_run(label)
        r.font.name = "Calibri"; r.font.size = Pt(11)
        r.font.bold = True; r.font.color.rgb = col

    doc.add_paragraph().paragraph_format.space_after = Pt(20)

    # Stats summary box
    body_para(doc, "Key Statistics — Version 3.0", bold=True, color=NAVY, size=11)
    add_table(doc,
        ["Metric", "Value"],
        [
            ["Listed Companies",      "284 across 4 exchanges"],
            ["Active Order Books",    "284 live (GBM price model, 10-level depth)"],
            ["Average Fill Rate",     "99.7% – 100% (improved from 96%)"],
            ["Routing Latency",       "36–130 µs end-to-end"],
            ["Execution Latency",     "2–10 ms (venue-aware)"],
            ["Slippage",              "0.5 – 1.5 bps (inverse-square-root model)"],
            ["Rejection Rate",        "1.5% (reduced from 8%)"],
            ["Venue Scoring Factors", "6 (liquidity, spread, fee, FX, latency, reliability)"],
            ["API Endpoints",         "35+ REST + WebSocket streaming"],
            ["Simulation Mode",       "Full GBM price simulation (SIMULATE=true)"],
        ],
        header_bg="283593",
        col_widths=[2.5, 3.5],
    )

    add_page_break(doc)

    # ── 1. EXECUTIVE SUMMARY ─────────────────────────────────────────────────
    styled_heading(doc, "1. Executive Summary", 1)
    divider(doc)
    body_para(doc,
        "The Pan SORFIX (Smart Order Router) is a production-grade, low-latency order routing "
        "platform purpose-built for Pan-African equity markets. It routes institutional orders across four "
        "major African exchanges — the Ghana Stock Exchange (GSE), Johannesburg Stock Exchange (JSE), "
        "Nigerian Exchange Group (NGX), and Nairobi Securities Exchange (NSE) — using a real-time "
        "multi-factor venue scoring engine, FIX 4.2 protocol adapters, and a parallel execution pipeline.")
    body_para(doc,
        "Version 3 introduces significant improvements across the full stack: a six-dimensional venue "
        "scoring model, Geometric Brownian Motion price simulation, 10-level order book depth, an improved "
        "execution engine with 99.7%+ fill rates, a comprehensive company registry of 284 listed securities, "
        "and a fully redesigned portal with Live Roles employment integration.")

    styled_heading(doc, "1.1 Core Capabilities", 2)
    for item in [
        "Real-time venue scoring across 6 dimensions with configurable weights summing to 1.0",
        "FIX 4.2 session management for GSE, JSE, NGX, NSE with TLS 1.3 encryption",
        "Parallel multi-leg execution with idempotency, exponential backoff, and circuit breakers",
        "Pre-trade risk engine: fat-finger, notional, price-band, position, and daily limit checks",
        "TWAP and VWAP algorithmic execution with configurable duration and slice count",
        "SQLite order persistence with full TCA (Transaction Cost Analysis) reporting",
        "284-company live market data pipeline with Geometric Brownian Motion price model",
        "REST API (35+ endpoints) + WebSocket live order book streaming",
        "Interactive portal with Live Book, Order Entry, Order History, Positions, TCA, Algo, Live Roles",
        "Excel export of all listed companies with live bid/ask/spread data",
    ]:
        bullet(doc, item)

    add_page_break(doc)

    # ── 2. SYSTEM ARCHITECTURE ────────────────────────────────────────────────
    styled_heading(doc, "2. System Architecture", 1)
    divider(doc)
    body_para(doc,
        "The application follows a layered architecture separating market data ingestion, order routing, "
        "execution, and persistence. All layers communicate through well-defined Python interfaces; "
        "no shared mutable state crosses layer boundaries except through the app_state singleton.")

    styled_heading(doc, "2.1 Layer Overview", 2)
    add_table(doc,
        ["Layer", "Component", "Responsibility"],
        [
            ["API Gateway",      "api/gateway.py",              "FastAPI app, auth, rate-limiting, WebSocket, TCA"],
            ["Routes",           "api/routes/*.py",             "Orders, market data, positions, health, admin, algo"],
            ["Smart Order Router","tools/smart_order_router.py","6-factor venue scoring, proportional allocation"],
            ["Execution Engine", "tools/execution_engine.py",   "FIX submission, retries, idempotency, circuit breakers"],
            ["Market Data",      "tools/market_data_pipeline.py","GBM price simulation, 10-level order book generation"],
            ["Risk Engine",      "tools/risk_engine.py",        "Pre-trade checks: qty, notional, price-band, position"],
            ["FX Optimizer",     "tools/fx_optimizer.py",       "Per-pair PAPSS conversion costs (8–20bps)"],
            ["Algo Engine",      "tools/algo_engine.py",        "TWAP/VWAP slice scheduling in daemon threads"],
            ["Order Book Cache", "tools/order_book_cache.py",   "Sharded in-memory cache (256 shards, O(1) lookup)"],
            ["Circuit Breaker",  "tools/circuit_breaker.py",    "CLOSED/OPEN/HALF_OPEN state machine per venue"],
            ["Persistence",      "tools/db.py + order_store.py","SQLite durability + in-memory LRU order store"],
            ["Position Tracker", "tools/position_tracker.py",   "Real-time net position, avg cost, realised P&L"],
            ["Companies Data",   "tools/companies_data.py",     "Master registry: 284 companies, prices, sectors"],
            ["Venue Adapters",   "tools/venue_adapters/*.py",   "Exchange-specific FIX session handlers"],
        ],
        header_bg="1A237E",
        col_widths=[1.5, 2.2, 3.3],
    )

    styled_heading(doc, "2.2 Data Flow", 2)
    body_para(doc, "Order lifecycle (Submit → Route → Execute → Persist):", bold=True)
    steps = [
        "1.  Client POSTs to /orders/submit — request validated by Pydantic models",
        "2.  Risk Engine runs pre-trade checks (qty, notional, price band, daily limit, position)",
        "3.  SOR scores all enabled venues for the symbol using 6 real-time factors",
        "4.  Proportional allocation distributes quantity across top-N venues by score × capacity",
        "5.  Execution Engine fires all legs in parallel threads; retries with exponential backoff",
        "6.  Circuit breakers update success/failure counts; reliability feeds back into next score",
        "7.  Fills recorded to Position Tracker and Risk Engine daily notional counter",
        "8.  Order persisted to SQLite (durable) and in-memory LRU store (fast lookup)",
        "9.  Response returned: fill ratio, VWAP, venue scores, execution reports per leg",
    ]
    for s in steps:
        body_para(doc, s, indent=0.3, size=10)

    add_page_break(doc)

    # ── 3. VENUE SCORING ENGINE ───────────────────────────────────────────────
    styled_heading(doc, "3. Venue Scoring Engine", 1)
    divider(doc)
    body_para(doc,
        "The Smart Order Router scores each venue on six factors before every routing decision. "
        "All factors are normalised to [0, 1]. The final score is the weighted sum multiplied by a "
        "staleness multiplier — stale order books are automatically penalised. Weights are read from "
        "sor_config.yaml and must sum exactly to 1.0.")

    styled_heading(doc, "3.1 Scoring Weights (v3)", 2)
    add_table(doc,
        ["Factor", "Weight", "Formula", "Description"],
        [
            ["Liquidity",    "28%", "min(1, depth/qty) − impact",
             "Side-aware (ask for buys, bid for sells), 5 levels, sqrt market impact"],
            ["FX Cost",      "18%", "1 − pair_cost / 0.030",
             "Per-pair PAPSS costs: ZAR 8bps, GHS 12bps, KES 15bps, NGN 20bps"],
            ["Spread",       "18%", "exp(−bps / 100)",
             "Exponential decay — eliminates hard cliff of previous linear model"],
            ["Fee",          "16%", "1 − fee / 0.005",
             "Taker fee normalised against 50bps ceiling"],
            ["Latency",      "10%", "exp(−ms / 20)",
             "Exponential: JSE 2ms→0.90, GSE 8ms→0.67, NSE 15ms→0.47"],
            ["Reliability",  "10%", "max(0.3, 1 − failures × 0.15)",
             "Circuit breaker failure count feeds back into next routing decision"],
        ],
        header_bg="283593",
        col_widths=[1.2, 0.8, 2.0, 3.0],
    )

    styled_heading(doc, "3.2 Book Staleness Multiplier", 2)
    body_para(doc,
        "The raw weighted score is multiplied by exp(−age_s / 10). A book updated 1 second ago "
        "receives a 0.99× multiplier; a 30-second-old book receives 0.05×. This prevents routing to "
        "a venue whose feed has silently died.")

    styled_heading(doc, "3.3 Version 2 → Version 3 Improvements", 2)
    add_table(doc,
        ["Dimension", "V2 (Old)", "V3 (New)"],
        [
            ["Liquidity",  "Avg bid+ask, 3 levels",       "Side-aware (ask/bid), 5 levels, stronger impact coeff 0.20"],
            ["Spread",     "Linear cliff at 5%",           "Exponential decay exp(−bps/100), no cliff"],
            ["FX Cost",    "Flat 15bps all pairs",         "Per-pair: ZAR 8, GHS 12, KES 15, NGN 20bps"],
            ["Latency",    "Linear 1 − ms/100",            "Exponential exp(−ms/20), log-scale differentiation"],
            ["Reliability","Not scored",                   "CB failure count → score penalty, floor 0.3"],
            ["Staleness",  "Not scored",                   "exp(−age/10) multiplier on full score"],
            ["Weights",    "5 factors summing to 1.0",     "6 factors: liq 28, spread 18, fee 16, fx 18, lat 10, rel 10"],
        ],
        header_bg="1A237E",
        col_widths=[1.4, 2.3, 3.3],
    )

    add_page_break(doc)

    # ── 4. EXECUTION ENGINE ───────────────────────────────────────────────────
    styled_heading(doc, "4. Execution Engine", 1)
    divider(doc)

    styled_heading(doc, "4.1 Simulation Parameters (v3)", 2)
    add_table(doc,
        ["Parameter", "V2", "V3", "Impact"],
        [
            ["Rejection rate",       "8%",          "1.5%",        "Far fewer wasted retries"],
            ["Fill rate",            "95–100%",      "99.8% ± 0.1%","Virtually all orders fully fill"],
            ["FILLED threshold",     "≥ 98%",        "≥ 99.5%",     "Fewer spurious PARTIAL statuses"],
            ["Slippage model",       "Linear 0–3bps","ISR 0.5–1.5bps","Tighter, more realistic"],
            ["Latency — JSE",        "1–10ms (flat)","1.5–3.5ms",   "Venue-aware profile"],
            ["Latency — GSE",        "1–10ms (flat)","3.0–7.0ms",   "Venue-aware profile"],
            ["Latency — NGX",        "1–10ms (flat)","4.0–9.0ms",   "Venue-aware profile"],
            ["Latency — NSE",        "1–10ms (flat)","5.0–10.0ms",  "Venue-aware profile"],
        ],
        header_bg="283593",
        col_widths=[1.8, 1.2, 1.4, 2.6],
    )

    styled_heading(doc, "4.2 Retry & Idempotency", 2)
    for item in [
        "Max 3 retries per leg with exponential backoff + full jitter (base 100ms, cap 5s)",
        "Idempotency cache: bounded LRU OrderedDict (50,000 entries) — duplicate calls return cached result",
        "All legs of a split order execute in parallel daemon threads against a shared deadline",
        "Circuit breaker updates on every success/failure; OPEN state blocks further retries immediately",
        "Order timeout: 30 seconds wall-clock before a timed-out FAILED report is synthesised",
    ]:
        bullet(doc, item)

    styled_heading(doc, "4.3 SOR Allocation (v3 — Proportional)", 2)
    body_para(doc,
        "Version 3 replaces the greedy top-venue allocation with proportional distribution. "
        "Each candidate venue receives a share of total quantity proportional to score × capacity:")
    body_para(doc, "    alloc_i = total_qty × (score_i × min(depth_i, qty)) / Σ (score_j × min(depth_j, qty))",
              italic=True, color=BLUE, indent=0.4)
    body_para(doc,
        "This means a venue with twice the score and equal depth gets twice the allocation. "
        "The last leg absorbs any rounding remainder to ensure 100% of quantity is always routed.")

    add_page_break(doc)

    # ── 5. MARKET DATA PIPELINE ───────────────────────────────────────────────
    styled_heading(doc, "5. Market Data Pipeline", 1)
    divider(doc)

    styled_heading(doc, "5.1 Price Model — Geometric Brownian Motion", 2)
    body_para(doc,
        "Version 3 upgrades the flat random walk to a proper GBM log-normal process, "
        "the standard model for equity price simulation:")
    body_para(doc, "    S(t+dt) = S(t) × exp( (μ − ½σ²)dt  +  σ√dt · Z )",
              italic=True, color=BLUE, indent=0.4)
    body_para(doc,
        "Parameters: μ = 0 (zero drift), σ = per-symbol daily volatility from companies_data.py, "
        "dt = 0.1 seconds, Z ~ N(0,1). This produces stationary, mean-reverting price paths "
        "that are log-normally distributed — the same statistical property as real equity prices.")

    styled_heading(doc, "5.2 Order Book Generation (v3)", 2)
    add_table(doc,
        ["Parameter", "V2", "V3"],
        [
            ["Depth levels",    "5",                            "10"],
            ["Tick size",       "0.1% of mid (10bps)",          "0.005% of mid (0.5bps)"],
            ["Quantity model",  "Uniform random 500–10,000",    "Exponential decay: base × exp(−0.25i)"],
            ["Base qty",        "500–10,000",                   "8,000–25,000 × venue multiplier"],
            ["Venue multiplier","1×",                           "JSE 3×, NGX 2×, GSE 1.2×, NSE 1×"],
            ["Timestamp",       "time.perf_counter_ns()",       "time.perf_counter_ns() (unchanged)"],
        ],
        header_bg="1A237E",
        col_widths=[1.8, 2.1, 3.1],
    )

    styled_heading(doc, "5.3 Coverage", 2)
    add_table(doc,
        ["Exchange", "Currency", "Companies", "Fee (bps)", "Latency (ms)", "FX Cost (bps)"],
        [
            ["🇬🇭 GSE — Ghana Stock Exchange",        "GHS", "39",  "15", "8",  "12"],
            ["🇿🇦 JSE — Johannesburg Stock Exchange", "ZAR", "97",  "20", "2",  "8"],
            ["🇳🇬 NGX — Nigerian Exchange Group",     "NGN", "93",  "30", "12", "20"],
            ["🇰🇪 NSE — Nairobi Securities Exchange", "KES", "55",  "21", "15", "15"],
            ["TOTAL",                                  "—",   "284", "—",  "—",  "—"],
        ],
        header_bg="283593",
        col_widths=[2.8, 0.8, 1.2, 1.1, 1.3, 1.3],
    )

    add_page_break(doc)

    # ── 6. RISK ENGINE ────────────────────────────────────────────────────────
    styled_heading(doc, "6. Pre-Trade Risk Engine", 1)
    divider(doc)
    body_para(doc,
        "All orders are validated synchronously before routing. A single failed check returns HTTP 422 "
        "with a structured error payload identifying the specific check and breach values.")

    add_table(doc,
        ["Check", "Default Limit", "Configurable", "Description"],
        [
            ["Max Order Quantity",    "1,000,000",   "Yes", "Fat-finger guard on share count"],
            ["Max Order Notional",    "$10,000,000", "Yes", "USD notional limit per order"],
            ["Price Band",            "±5%",         "Yes", "Deviation from last trade price"],
            ["Daily Notional",        "$50,000,000", "Yes", "Cumulative daily USD notional"],
            ["Max Position Quantity", "5,000,000",   "Yes", "Absolute net position per symbol"],
        ],
        header_bg="1A237E",
        col_widths=[2.0, 1.5, 1.1, 2.4],
    )

    body_para(doc,
        "Limits are hot-updatable via PUT /admin/risk/config at runtime without restart. "
        "Daily notional resets automatically at UTC midnight and can be manually reset via "
        "POST /admin/risk/reset-daily.")

    add_page_break(doc)

    # ── 7. REST API REFERENCE ─────────────────────────────────────────────────
    styled_heading(doc, "7. REST API Reference", 1)
    divider(doc)
    body_para(doc, "Base URL: http://localhost:9090   ·   Auth: X-API-Key header (disabled by default)")
    body_para(doc, "Rate limit: 300 requests/minute per IP (sliding window)  ·  Docs: /docs (Swagger UI)")

    styled_heading(doc, "7.1 Orders", 2)
    add_table(doc,
        ["Method", "Endpoint", "Description"],
        [
            ["POST",  "/orders/route",     "Compute optimal routing plan (no execution)"],
            ["POST",  "/orders/submit",    "Route and execute order across venues in parallel"],
            ["GET",   "/orders/{id}",      "Retrieve a specific order by ID"],
            ["GET",   "/orders/",          "List recent orders (limit 1–200)"],
        ],
        header_bg="283593", col_widths=[0.8, 2.2, 4.0],
    )

    styled_heading(doc, "7.2 Market Data", 2)
    add_table(doc,
        ["Method", "Endpoint", "Description"],
        [
            ["GET",    "/market-data/symbols",          "All active symbols per venue"],
            ["GET",    "/market-data/book/{venue}/{sym}","Full order book (10 levels bid/ask)"],
            ["WS",     "/ws/book/{venue}/{sym}",         "Live order book WebSocket stream (500ms push)"],
            ["GET",    "/tca",                           "Transaction Cost Analysis (filter by symbol)"],
        ],
        header_bg="283593", col_widths=[0.8, 2.6, 3.6],
    )

    styled_heading(doc, "7.3 Algo Orders", 2)
    add_table(doc,
        ["Method", "Endpoint", "Description"],
        [
            ["POST", "/algo/twap",      "Start a TWAP execution (duration + slices)"],
            ["POST", "/algo/vwap",      "Start a VWAP execution (volume-weighted slicing)"],
            ["GET",  "/algo/",          "List all algo orders"],
            ["POST", "/algo/{id}/cancel","Cancel a running algo order"],
        ],
        header_bg="283593", col_widths=[0.8, 2.2, 4.0],
    )

    styled_heading(doc, "7.4 Admin & Risk", 2)
    add_table(doc,
        ["Method", "Endpoint", "Description"],
        [
            ["GET",  "/health",                 "Venue status, uptime, execution counts"],
            ["GET",  "/admin/status",            "System state, halt flag, metrics"],
            ["POST", "/admin/halt",              "Emergency halt — stops all new order routing"],
            ["POST", "/admin/resume",            "Resume routing after halt"],
            ["GET",  "/admin/risk/config",       "Current risk limits"],
            ["PUT",  "/admin/risk/config",       "Hot-update risk limits at runtime"],
            ["POST", "/admin/risk/reset-daily",  "Reset daily notional counter"],
            ["GET",  "/positions/",              "All net positions with avg cost and P&L"],
            ["GET",  "/positions/stats",         "Aggregate position statistics"],
        ],
        header_bg="283593", col_widths=[0.8, 2.4, 3.8],
    )

    add_page_break(doc)

    # ── 8. PORTAL UI ─────────────────────────────────────────────────────────
    styled_heading(doc, "8. Portal UI", 1)
    divider(doc)
    body_para(doc,
        "The portal is a single-page application served at http://localhost:9090/portal. "
        "It connects to the live API for all data; no static snapshots. Auto-refreshes health "
        "every 5 seconds. All tabs share the same API base URL.")

    add_table(doc,
        ["Tab", "Key Features"],
        [
            ["Dashboard",      "Venue status cards, execution count, MD update rate, Symbol Catalog with exchange filter dropdowns"],
            ["Live Book",      "Real-time 10-level bid/ask depth with depth bars, WebSocket push every 500ms"],
            ["Submit Order",   "Exchange → Company cascading dropdown (284 companies), live Bid/Ask/Spread info bar, Preview Route"],
            ["Order History",  "Last 200 orders with fill%, VWAP, latency, venue, expandable routing details"],
            ["Positions",      "Net qty, avg cost, realised P&L, total volume per symbol"],
            ["Algo Orders",    "TWAP/VWAP submission with exchange/company selection, live progress, cancel"],
            ["TCA",            "Transaction cost analysis: spread cost, fill ratio, VWAP vs arrival price"],
            ["Live Roles",     "Employment tab: 284 companies as cards, filter by exchange, click to open careers page"],
            ["Apply",          "Company careers iframe with fallback direct-link, grouped by exchange"],
            ["Admin",          "Risk config editor, halt/resume, daily reset, circuit breaker states"],
        ],
        header_bg="1A237E",
        col_widths=[1.5, 5.5],
    )

    add_page_break(doc)

    # ── 9. CONFIGURATION ─────────────────────────────────────────────────────
    styled_heading(doc, "9. Configuration", 1)
    divider(doc)
    body_para(doc, "All runtime parameters are in configs/sor_config.yaml. The app validates on startup; "
              "malformed or out-of-range values abort with a descriptive error.")

    styled_heading(doc, "9.1 sor_config.yaml — Key Sections", 2)
    add_table(doc,
        ["Section", "Key Parameters"],
        [
            ["routing",        "liquidity_weight, spread_weight, fee_weight, fx_weight, latency_weight, reliability_weight (must sum to 1.0)"],
            ["circuit_breaker","failure_threshold (5), success_threshold (3), timeout_seconds (30)"],
            ["execution",      "max_retries (3), retry_delay_ms (100), order_timeout_seconds (30), simulate (true)"],
            ["risk",           "max_order_qty, max_order_notional, price_band_pct, max_daily_notional, max_position_qty"],
            ["fx_rates",       "USD base + GHS/ZAR/NGN/KES spot rates (updated from PAPSS API in production)"],
            ["api",            "host (0.0.0.0), port (9090), workers (1)"],
            ["market_data",    "update_interval_seconds (0.1), use_kafka (false)"],
            ["auth",           "enabled (false), api_keys list"],
            ["rate_limit",     "enabled (true), requests_per_minute (300)"],
        ],
        header_bg="283593",
        col_widths=[1.5, 5.5],
    )

    styled_heading(doc, "9.2 Environment Variables (.env)", 2)
    add_table(doc,
        ["Variable", "Default", "Description"],
        [
            ["APP_PORT",    "9090",      "API server port"],
            ["APP_HOST",    "0.0.0.0",   "Bind address"],
            ["LOG_LEVEL",   "INFO",      "Logging level (DEBUG/INFO/WARNING/ERROR)"],
            ["SIMULATE",    "true",      "Set false to enable live FIX socket connections"],
            ["GSE_HOST",    "fix.gse.com.gh",   "GSE FIX gateway host"],
            ["JSE_HOST",    "fix.jse.co.za",    "JSE FIX gateway host"],
            ["NGX_HOST",    "fix.ngxgroup.com", "NGX FIX gateway host"],
            ["NSE_HOST",    "fix.nse.co.ke",    "NSE FIX gateway host"],
            ["PAPSS_API_KEY","",         "PAPSS FX API key (replaces mock rates in production)"],
        ],
        header_bg="1A237E",
        col_widths=[1.8, 1.6, 3.6],
    )

    add_page_break(doc)

    # ── 10. DEPLOYMENT ────────────────────────────────────────────────────────
    styled_heading(doc, "10. Running the Application", 1)
    divider(doc)

    styled_heading(doc, "10.1 Quick Start", 2)
    for step in [
        "git clone <repo>  (or extract ZIP)",
        "cd FIX_Aggregator_SOR_Complete\\ APP",
        "pip install -r requirements.txt",
        "cp .env.example .env  # fill in FIX credentials for live mode",
        "python main.py                    # start API server on port 9090",
        "python main.py --demo             # run demo mode (no server)",
        "python main.py --port 8080        # custom port",
    ]:
        body_para(doc, f"    {step}", italic=True, color=TEAL, indent=0.2, size=10)

    styled_heading(doc, "10.2 Demo Mode", 2)
    body_para(doc,
        "Running python main.py --demo executes 12 representative orders across all 4 exchanges "
        "(3 per venue), prints full routing + execution detail to stdout, and exits. No server is "
        "started. Useful for CI validation and quick smoke-testing.")

    styled_heading(doc, "10.3 Excel Export", 2)
    body_para(doc,
        "python tools/export_companies.py generates a formatted .xlsx workbook on the Desktop "
        "containing 6 sheets: All Companies (284 rows with live prices), per-exchange tabs (GSE/JSE/NGX/NSE), "
        "Sector Breakdown, and Exchange Summary. Requires the API server to be running for live data.")

    styled_heading(doc, "10.4 Dependencies", 2)
    add_table(doc,
        ["Package", "Version", "Purpose"],
        [
            ["fastapi",       "≥ 0.111",  "REST API framework"],
            ["uvicorn",       "≥ 0.29",   "ASGI server"],
            ["pydantic",      "≥ 2.7",    "Request/response validation"],
            ["pyyaml",        "≥ 6.0",    "Config file parsing"],
            ["python-dotenv", "≥ 1.0",    "Environment variable loading"],
            ["openpyxl",      "≥ 3.1",    "Excel export"],
            ["python-docx",   "≥ 1.2",    "Documentation generation"],
            ["websockets",    "≥ 12.0",   "WebSocket support"],
        ],
        header_bg="283593",
        col_widths=[1.8, 1.2, 4.0],
    )

    add_page_break(doc)

    # ── 11. CHANGELOG ─────────────────────────────────────────────────────────
    styled_heading(doc, "11. Version History", 1)
    divider(doc)

    add_table(doc,
        ["Version", "Date", "Changes"],
        [
            ["3.0", "Jun 2026",
             "6-factor scoring; GBM price model; 10-level books; 99.8% fill rate; "
             "proportional SOR allocation; 284-company registry; Live Roles tab; "
             "Exchange→Company cascading dropdowns; venue-aware execution latency; "
             "per-pair FX costs; book staleness multiplier; reliability scoring"],
            ["2.0", "May 2026",
             "5-factor scoring; pre-trade risk engine; TWAP/VWAP algos; "
             "SQLite persistence; position tracking; TCA endpoint; circuit breakers; "
             "idempotent execution; WebSocket book streaming"],
            ["1.0", "Mar 2026",
             "Initial release: FIX 4.2 adapters for GSE/JSE/NGX/NSE; "
             "basic venue scoring; REST API; portal dashboard"],
        ],
        header_bg="1A237E",
        col_widths=[0.8, 1.0, 5.2],
    )

    add_page_break(doc)

    # ── 12. GLOSSARY ─────────────────────────────────────────────────────────
    styled_heading(doc, "12. Glossary", 1)
    divider(doc)
    add_table(doc,
        ["Term", "Definition"],
        [
            ["SOR",    "Smart Order Router — logic that decides which venue(s) receive each order"],
            ["FIX",    "Financial Information eXchange protocol — industry standard for order messaging"],
            ["GBM",    "Geometric Brownian Motion — log-normal stochastic process for price simulation"],
            ["TWAP",   "Time-Weighted Average Price — equal-sized slices spread evenly over duration"],
            ["VWAP",   "Volume-Weighted Average Price — slices weighted by a bell-curve volume profile"],
            ["TCA",    "Transaction Cost Analysis — comparison of execution price vs pre-trade benchmark"],
            ["PAPSS",  "Pan-African Payment and Settlement System — continental FX settlement infrastructure"],
            ["CB",     "Circuit Breaker — state machine that blocks a venue after repeated failures"],
            ["bps",    "Basis points — 1/100th of 1%; 10bps = 0.1%"],
            ["Slippage","Adverse price movement between order arrival and execution fill"],
            ["Participation rate", "Order quantity as a fraction of available book depth at the venue"],
        ],
        header_bg="283593",
        col_widths=[1.8, 5.2],
    )

    # ── FOOTER ────────────────────────────────────────────────────────────────
    body_para(doc, "")
    divider(doc)
    footer = doc.add_paragraph()
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    rf = footer.add_run(
        f"Pan SORFIX v3.0  ·  Confidential  ·  "
        f"Generated {now.strftime('%d %B %Y %H:%M')}  ·  "
        f"© {now.year} SecVerse Ltd. All rights reserved."
    )
    rf.font.name = "Calibri"; rf.font.size = Pt(8.5); rf.font.color.rgb = MID_GREY

    return doc


def main():
    print("Generating Pan SORFIX v3 documentation...")
    doc = build_doc()

    candidates = [
        Path.home() / "OneDrive" / "Desktop",
        Path.home() / "Desktop",
        Path.cwd(),
    ]
    out_dir = next((p for p in candidates if p.exists()), Path.cwd())
    out_path = out_dir / f"FIX_SOR_v3_Documentation_{datetime.now().strftime('%Y%m%d')}.docx"
    doc.save(str(out_path))
    print(f"Saved: {out_path}")

    import platform
    if platform.system() == "Windows":
        import subprocess
        subprocess.Popen(["start", "", str(out_path)], shell=True)

    return str(out_path)


if __name__ == "__main__":
    main()
