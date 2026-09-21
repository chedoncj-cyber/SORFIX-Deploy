"""
World SORFIX — Export Global Listed Top 100 Companies to Excel.
Generates a formatted .xlsx on the user's Desktop.
"""

import sys
import os
from pathlib import Path
from datetime import date

# Ensure app root on path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.companies_data import COMPANIES
import openpyxl
from openpyxl.styles import (
    PatternFill, Font, Alignment, Border, Side, GradientFill
)
from openpyxl.utils import get_column_letter

# ── Exchange metadata ──────────────────────────────────────────────────────────
EXCHANGE_META = {
    "NYSE":     {"flag": "🇺🇸", "full": "New York Stock Exchange",     "currency": "USD", "color": "1B5E20", "light": "E8F5E9", "text": "FFFFFF"},
    "LSE":      {"flag": "🇬🇧", "full": "London Stock Exchange",       "currency": "GBP", "color": "0D47A1", "light": "E3F2FD", "text": "FFFFFF"},
    "HKEX":     {"flag": "🇭🇰", "full": "Hong Kong Exchanges",         "currency": "HKD", "color": "B71C1C", "light": "FFEBEE", "text": "FFFFFF"},
    "TSE":      {"flag": "🇯🇵", "full": "Tokyo Stock Exchange",        "currency": "JPY", "color": "4A148C", "light": "F3E5F5", "text": "FFFFFF"},
    "SSE":      {"flag": "🇨🇳", "full": "Shanghai Stock Exchange",     "currency": "CNY", "color": "B71C1C", "light": "FFF3E0", "text": "FFFFFF"},
    "SZSE":     {"flag": "🇨🇳", "full": "Shenzhen Stock Exchange",     "currency": "CNY", "color": "E65100", "light": "FFF3E0", "text": "FFFFFF"},
    "TADAWUL":  {"flag": "🇸🇦", "full": "Saudi Exchange (Tadawul)",    "currency": "SAR", "color": "1B5E20", "light": "F1F8E9", "text": "FFFFFF"},
    "NSE_IN":   {"flag": "🇮🇳", "full": "National Stock Exchange India","currency": "INR", "color": "E65100", "light": "FFF8E1", "text": "FFFFFF"},
    "EURONEXT": {"flag": "🇪🇺", "full": "Euronext (Pan-European)",     "currency": "EUR", "color": "1A237E", "light": "E8EAF6", "text": "FFFFFF"},
}

# Row colors per exchange (alternating light shades)
ROW_COLORS = {
    "NYSE":     ("D6EAD7", "EBF5EB"),
    "LSE":      ("C5D9F1", "DCE9F8"),
    "HKEX":     ("F4CCCC", "FAE3E3"),
    "TSE":      ("D9C8EB", "EBE0F5"),
    "SSE":      ("FCE5CD", "FEF2E4"),
    "SZSE":     ("F9E1C0", "FCF0DC"),
    "TADAWUL":  ("D3EAD3", "E9F5E9"),
    "NSE_IN":   ("FEF0CC", "FEF8E6"),
    "EURONEXT": ("C9D3F1", "DDE3F8"),
}

# ── Company selection: 100 total across 9 exchanges ───────────────────────────
PICKS = {
    "NYSE":     12,
    "LSE":      12,
    "HKEX":     11,
    "TSE":      11,
    "SSE":      11,
    "SZSE":     11,
    "TADAWUL":  11,
    "NSE_IN":   10,
    "EURONEXT": 11,
}
assert sum(PICKS.values()) == 100, f"Total={sum(PICKS.values())}"

# ── Build rows ─────────────────────────────────────────────────────────────────
rows = []
for exchange, n in PICKS.items():
    meta = EXCHANGE_META[exchange]
    co_dict = COMPANIES.get(exchange, {})
    selected = list(co_dict.items())[:n]
    for symbol, info in selected:
        rows.append({
            "exchange":  exchange,
            "flag":      meta["flag"],
            "full_name": meta["full"],
            "currency":  meta["currency"],
            "symbol":    symbol,
            "name":      info["name"],
            "sector":    info["sector"],
            "price":     info["price"],
            "vol_pct":   round(info["vol"] * 100, 2),
        })

# ── Create workbook ────────────────────────────────────────────────────────────
wb = openpyxl.Workbook()

# ════════════════════════════════════════════════════════════════════════════════
# Sheet 1 — Master List
# ════════════════════════════════════════════════════════════════════════════════
ws = wb.active
ws.title = "Global Top 100"

def _fill(hex_color):
    return PatternFill("solid", fgColor=hex_color)

def _font(bold=False, color="000000", size=11, name="Calibri"):
    return Font(bold=bold, color=color, size=size, name=name)

def _border():
    s = Side(style="thin", color="D0D0D0")
    return Border(left=s, right=s, top=s, bottom=s)

def _center():
    return Alignment(horizontal="center", vertical="center", wrap_text=False)

def _left():
    return Alignment(horizontal="left", vertical="center")

# ── Title block ────────────────────────────────────────────────────────────────
ws.merge_cells("A1:K1")
title_cell = ws["A1"]
title_cell.value = "WORLD SORFIX  —  Global Listed Top 100 Companies"
title_cell.font  = Font(bold=True, color="FFFFFF", size=16, name="Calibri")
title_cell.fill  = _fill("0D1B4B")
title_cell.alignment = Alignment(horizontal="center", vertical="center")
ws.row_dimensions[1].height = 34

ws.merge_cells("A2:K2")
sub_cell = ws["A2"]
sub_cell.value = (
    f"NYSE · LSE · HKEX · TSE · SSE · SZSE · TADAWUL · NSE_IN · EURONEXT  |  "
    f"Generated: {date.today().strftime('%d %B %Y')}  |  FIX 4.2 Smart Order Router"
)
sub_cell.font  = Font(italic=True, color="A0A8C0", size=10, name="Calibri")
sub_cell.fill  = _fill("111936")
sub_cell.alignment = Alignment(horizontal="center", vertical="center")
ws.row_dimensions[2].height = 20

# Blank spacer
ws.row_dimensions[3].height = 6

# ── Column headers ─────────────────────────────────────────────────────────────
HEADERS = ["#", "Flag", "Exchange", "Exchange Full Name", "Symbol",
           "Company Name", "Sector", "Currency", "Price (Local)", "Daily Vol %", "SOR Status"]
HDR_ROW = 4

for col_idx, h in enumerate(HEADERS, 1):
    cell = ws.cell(row=HDR_ROW, column=col_idx, value=h)
    cell.font      = Font(bold=True, color="FFFFFF", size=10, name="Calibri")
    cell.fill      = _fill("1C2E6B")
    cell.alignment = _center()
    cell.border    = _border()

ws.row_dimensions[HDR_ROW].height = 24

# ── Data rows ──────────────────────────────────────────────────────────────────
for i, row in enumerate(rows, 1):
    data_row = HDR_ROW + i
    alt      = i % 2
    c1, c2   = ROW_COLORS[row["exchange"]]
    bg_hex   = c1 if alt == 1 else c2

    values = [
        i,
        row["flag"],
        row["exchange"],
        row["full_name"],
        row["symbol"],
        row["name"],
        row["sector"],
        row["currency"],
        row["price"],
        row["vol_pct"],
        "ACTIVE",
    ]

    for col_idx, val in enumerate(values, 1):
        cell = ws.cell(row=data_row, column=col_idx, value=val)
        cell.fill   = _fill(bg_hex)
        cell.border = _border()

        if col_idx == 1:   # rank
            cell.font      = Font(bold=True, color="555555", size=10, name="Calibri")
            cell.alignment = _center()
        elif col_idx == 2:  # flag emoji
            cell.font      = Font(size=13, name="Segoe UI Emoji")
            cell.alignment = _center()
        elif col_idx == 3:  # exchange code
            ex_color = EXCHANGE_META[row["exchange"]]["color"]
            cell.font      = Font(bold=True, color=ex_color, size=10, name="Calibri")
            cell.alignment = _center()
        elif col_idx == 5:  # symbol
            cell.font      = Font(bold=True, color="1A2766", size=10, name="Courier New")
            cell.alignment = _center()
        elif col_idx == 9:  # price
            cell.number_format = '#,##0.00'
            cell.font          = Font(bold=True, color="1B5E20", size=10, name="Calibri")
            cell.alignment     = Alignment(horizontal="right", vertical="center")
        elif col_idx == 10:  # vol %
            cell.number_format = '0.00"%"'
            vol = row["vol_pct"]
            color = "C62828" if vol >= 3.0 else ("E65100" if vol >= 2.0 else "2E7D32")
            cell.font      = Font(bold=True, color=color, size=10, name="Calibri")
            cell.alignment = Alignment(horizontal="right", vertical="center")
        elif col_idx == 11:  # status
            cell.font      = Font(bold=True, color="1B5E20", size=9, name="Calibri")
            cell.fill      = _fill("DFFFDF") if alt == 1 else _fill("C8F5C8")
            cell.alignment = _center()
        else:
            cell.font      = Font(color="1A1A2E", size=10, name="Calibri")
            cell.alignment = _left()

    ws.row_dimensions[data_row].height = 18

# ── Column widths ──────────────────────────────────────────────────────────────
col_widths = [5, 6, 10, 34, 14, 42, 22, 10, 14, 12, 12]
for col_idx, w in enumerate(col_widths, 1):
    ws.column_dimensions[get_column_letter(col_idx)].width = w

# Freeze panes below header
ws.freeze_panes = "A5"

# Auto-filter on header row
ws.auto_filter.ref = f"A{HDR_ROW}:K{HDR_ROW + len(rows)}"

# ════════════════════════════════════════════════════════════════════════════════
# Sheet 2 — Exchange Summary
# ════════════════════════════════════════════════════════════════════════════════
ws2 = wb.create_sheet("Exchange Summary")

ws2.merge_cells("A1:H1")
ws2["A1"].value     = "World SORFIX — Exchange Summary"
ws2["A1"].font      = Font(bold=True, color="FFFFFF", size=14, name="Calibri")
ws2["A1"].fill      = _fill("0D1B4B")
ws2["A1"].alignment = Alignment(horizontal="center", vertical="center")
ws2.row_dimensions[1].height = 30

ws2.merge_cells("A2:H2")
ws2["A2"].value     = f"FIX 4.2 · 9 Exchanges · {date.today().strftime('%d %B %Y')}"
ws2["A2"].font      = Font(italic=True, color="A0A8C0", size=10)
ws2["A2"].fill      = _fill("111936")
ws2["A2"].alignment = Alignment(horizontal="center", vertical="center")
ws2.row_dimensions[2].height = 18

SUM_HDRS = ["Exchange", "Full Name", "Flag", "Currency", "# Companies", "Avg Price", "Avg Vol %", "Settlement"]
SETTLEMENT = {
    "NYSE": "T+2", "LSE": "T+2", "HKEX": "T+2", "TSE": "T+2",
    "SSE": "T+1", "SZSE": "T+1", "TADAWUL": "T+2", "NSE_IN": "T+1", "EURONEXT": "T+2",
}

for ci, h in enumerate(SUM_HDRS, 1):
    c = ws2.cell(row=4, column=ci, value=h)
    c.font      = Font(bold=True, color="FFFFFF", size=10, name="Calibri")
    c.fill      = _fill("1C2E6B")
    c.alignment = _center()
    c.border    = _border()
ws2.row_dimensions[4].height = 22

for ri, (ex, n) in enumerate(PICKS.items(), 1):
    meta    = EXCHANGE_META[ex]
    ex_rows = [r for r in rows if r["exchange"] == ex]
    avg_p   = sum(r["price"] for r in ex_rows) / len(ex_rows)
    avg_v   = sum(r["vol_pct"] for r in ex_rows) / len(ex_rows)
    bg      = ROW_COLORS[ex][0] if ri % 2 == 1 else ROW_COLORS[ex][1]

    vals = [ex, meta["full"], meta["flag"], meta["currency"], n,
            round(avg_p, 2), round(avg_v, 3), SETTLEMENT[ex]]
    for ci, v in enumerate(vals, 1):
        c = ws2.cell(row=4 + ri, column=ci, value=v)
        c.fill   = _fill(bg)
        c.border = _border()
        if ci == 1:
            c.font = Font(bold=True, color=meta["color"], size=11, name="Calibri")
            c.alignment = _center()
        elif ci == 3:
            c.font = Font(size=13, name="Segoe UI Emoji")
            c.alignment = _center()
        elif ci == 6:
            c.number_format = '#,##0.00'
            c.font = Font(bold=True, color="1B5E20", size=10, name="Calibri")
            c.alignment = Alignment(horizontal="right", vertical="center")
        elif ci == 7:
            c.number_format = '0.000"%"'
            c.font = Font(bold=True, color="C62828", size=10, name="Calibri")
            c.alignment = Alignment(horizontal="right", vertical="center")
        else:
            c.font = Font(color="1A1A2E", size=10, name="Calibri")
            c.alignment = _center()
    ws2.row_dimensions[4 + ri].height = 20

# Totals row
tot_row = 4 + len(PICKS) + 1
ws2.merge_cells(f"A{tot_row}:D{tot_row}")
tc = ws2.cell(row=tot_row, column=1, value="TOTAL  (all 9 exchanges)")
tc.font = Font(bold=True, color="FFFFFF", size=11, name="Calibri")
tc.fill = _fill("0D1B4B")
tc.alignment = Alignment(horizontal="center", vertical="center")
tot_n = ws2.cell(row=tot_row, column=5, value=100)
tot_n.font = Font(bold=True, color="FFFFFF", size=12, name="Calibri")
tot_n.fill = _fill("0D1B4B")
tot_n.alignment = _center()
for ci in [6, 7, 8]:
    ws2.cell(row=tot_row, column=ci).fill = _fill("0D1B4B")
ws2.row_dimensions[tot_row].height = 22

# Column widths sheet 2
for ci, w in enumerate([12, 36, 7, 10, 14, 14, 12, 12], 1):
    ws2.column_dimensions[get_column_letter(ci)].width = w

# ════════════════════════════════════════════════════════════════════════════════
# Sheet 3 — Sector Breakdown
# ════════════════════════════════════════════════════════════════════════════════
ws3 = wb.create_sheet("Sector Breakdown")

from collections import Counter
sector_counts = Counter(r["sector"] for r in rows)
sector_ex     = {}  # sector -> list of exchanges
for r in rows:
    sector_ex.setdefault(r["sector"], set()).add(r["exchange"])

ws3.merge_cells("A1:E1")
ws3["A1"].value     = "World SORFIX — Sector Breakdown (Top 100 Companies)"
ws3["A1"].font      = Font(bold=True, color="FFFFFF", size=13, name="Calibri")
ws3["A1"].fill      = _fill("0D1B4B")
ws3["A1"].alignment = Alignment(horizontal="center", vertical="center")
ws3.row_dimensions[1].height = 28

for ci, h in enumerate(["Sector", "# Companies", "% of 100", "Exchanges Present", "Bar"], 1):
    c = ws3.cell(row=3, column=ci, value=h)
    c.font = Font(bold=True, color="FFFFFF", size=10, name="Calibri")
    c.fill = _fill("1C2E6B")
    c.alignment = _center()
    c.border = _border()
ws3.row_dimensions[3].height = 22

SECTOR_COLORS = {
    "Technology":        "E8F0FE", "Financials":        "FFF9C4",
    "Healthcare":        "FCE4EC", "Consumer Discret.": "F3E5F5",
    "Consumer Staples":  "E8F5E9", "Industrials":       "FFF3E0",
    "Energy":            "F9FBE7", "Materials":         "EFEBE9",
    "Communication":     "E3F2FD", "Automotive":        "FAFAFA",
    "Real Estate":       "FFF8E1", "Utilities":         "E0F7FA",
    "Conglomerate":      "EDE7F6", "Transport":         "F1F8E9",
}

for ri, (sector, cnt) in enumerate(sorted(sector_counts.items(), key=lambda x: -x[1]), 1):
    bg = SECTOR_COLORS.get(sector, "F5F5F5")
    pct = round(cnt / 100 * 100, 1)
    ex_list = ", ".join(sorted(sector_ex[sector]))
    bar = "█" * cnt + "░" * (20 - min(cnt, 20))

    for ci, v in enumerate([sector, cnt, pct, ex_list, bar], 1):
        c = ws3.cell(row=3 + ri, column=ci, value=v)
        c.fill   = _fill(bg)
        c.border = _border()
        if ci == 1:
            c.font = Font(bold=True, color="1A1A2E", size=10, name="Calibri")
            c.alignment = _left()
        elif ci in (2, 3):
            c.font = Font(bold=True, color="1B5E20", size=10, name="Calibri")
            c.alignment = _center()
        elif ci == 5:
            c.font = Font(color="1C6EAA", size=9, name="Courier New")
            c.alignment = _left()
        else:
            c.font = Font(color="333333", size=9, name="Calibri")
            c.alignment = _left()
    ws3.row_dimensions[3 + ri].height = 18

for ci, w in enumerate([26, 14, 12, 44, 28], 1):
    ws3.column_dimensions[get_column_letter(ci)].width = w

# ── Save ───────────────────────────────────────────────────────────────────────
import subprocess, ctypes
try:
    import winreg
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders")
    desktop_raw = winreg.QueryValueEx(key, "Desktop")[0]
    desktop = Path(os.path.expandvars(desktop_raw))
except Exception:
    desktop = Path.home() / "OneDrive" / "Desktop"
out_path = desktop / f"WorldSORFIX_Global_Top100_Companies_{date.today().strftime('%Y%m%d')}.xlsx"
wb.save(out_path)
print(f"Saved: {out_path}")
print(f"Rows : {len(rows)} companies across {len(PICKS)} exchanges")
