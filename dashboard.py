"""
dashboard.py  -  SAP P2P Analytics  |  Nitish Kumar Biswal | Roll: 2305950 | CSE-46
Dark navy theme, 30-slot subplot_titles (3 per row x 10 rows), crisp axes.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import os
import analytics as ana

# Colour Palette
BG_PAGE   = "#0D1B2A"
BG_PLOT   = "#112233"
BG_CARD   = "#0F1E30"
AXIS_LINE = "#2E4A66"
GRID_COLOR= "#1E3A55"
TEXT_PRIMARY = "#E8F4FD"
TEXT_DIM     = "#7FA8C9"

C_BLUE   = "#00AEEF"
C_TEAL   = "#00D4C8"
C_GREEN  = "#2ECC71"
C_ORANGE = "#F39C12"
C_RED    = "#E74C3C"
C_PURPLE = "#9B59B6"
C_GOLD   = "#F1C40F"
C_PINK   = "#E91E8C"

PALETTE = [C_BLUE, C_TEAL, C_GREEN, C_ORANGE, C_RED, C_PURPLE, C_GOLD, C_PINK,
           "#3498DB", "#1ABC9C"]

AXIS_STYLE = dict(
    showgrid=True,
    gridcolor=GRID_COLOR,
    gridwidth=1,
    zeroline=True,
    zerolinecolor=AXIS_LINE,
    zerolinewidth=1.5,
    linecolor=AXIS_LINE,
    linewidth=1.5,
    showline=True,
    tickcolor=TEXT_DIM,
    tickfont=dict(color=TEXT_DIM, size=10, family="IBM Plex Mono, monospace"),
    title_font=dict(color=TEXT_PRIMARY, size=11, family="IBM Plex Sans, sans-serif"),
)

def axis(**extra):
    d = dict(AXIS_STYLE)
    d.update(extra)
    return d

def hex_to_rgba(hex_color, alpha=0.25):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{alpha})"

def kpi_card(fig, row, col, title, value, subtitle="", color=C_BLUE):
    fig.add_trace(go.Indicator(
        mode="number",
        value=value,
        title={
            "text": (
                f"<span style='font-size:13px;font-family:IBM Plex Sans,sans-serif;"
                f"color:{TEXT_DIM};letter-spacing:0.05em'>{title}</span>"
                f"<br><span style='font-size:10px;color:#4A7A9B'>{subtitle}</span>"
            ),
        },
        number={
            "font": {"size": 32, "color": color, "family": "IBM Plex Mono, monospace"},
            "valueformat": ",.2f" if value < 1000 else ",.0f",
        },
    ), row=row, col=col)


def build_dashboard(df: pd.DataFrame, kpis: dict,
                    output_path: str = "output/P2P_Dashboard.html"):
    os.makedirs("output", exist_ok=True)

    spend_cat    = ana.spend_by_category(df)
    spend_vendor = ana.spend_by_vendor(df)
    monthly      = ana.monthly_spend_trend(df)
    vp           = ana.vendor_performance(df)
    dept         = ana.spend_by_department(df)
    quarterly    = ana.quarterly_spend(df)

    # -----------------------------------------------------------
    # subplot_titles: MUST have exactly 30 strings
    # (3 cols x 10 rows, one per cell including None slots)
    # -----------------------------------------------------------
    titles = (
        # Row 1  indicators (3)
        "", "", "",
        # Row 2  indicators (3)
        "", "", "",
        # Row 3  Monthly[colspan2] | None | Dept Pie (3)
        "Monthly Procurement Spend (Rs Lakhs)", "", "Spend by Department",
        # Row 4  Top Vendors[colspan3] | None | None (3)
        "Top 10 Vendors by Spend (Rs Lakhs)", "", "",
        # Row 5  Category[colspan2] | None | Quarterly (3)
        "Spend by Category (Rs Lakhs)", "", "Quarterly Procurement Overview (Rs Lakhs)",
        # Row 6  Vendor Perf[colspan3] | None | None (3)
        "Vendor Performance: On-Time Rate vs Spend", "", "",
        # Row 7  Box Plots[colspan2] | None | Payment Bar (3)
        "P2P Stage Cycle Times (Days)", "", "Avg Payment Cycle by Vendor (Days)",
        # Row 8  E2E Histogram[colspan3] | None | None (3)
        "End-to-End P2P Cycle Time Distribution", "", "",
        # Row 9  On-Time[colspan2] | None | Exception (3)
        "Vendor On-Time Delivery Rate (%)", "", "Invoice Exception Rate by Category (%)",
        # Row 10 Pareto[colspan3] | None | None (3)
        "Procurement Spend Pareto Analysis (Vendor)", "", "",
    )
    assert len(titles) == 30, f"Expected 30 titles, got {len(titles)}"

    fig = make_subplots(
        rows=10, cols=3,
        specs=[
            [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
            [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
            [{"colspan": 2, "type": "xy"}, None, {"type": "pie"}],
            [{"colspan": 3, "type": "xy"}, None, None],
            [{"colspan": 2, "type": "xy"}, None, {"type": "xy"}],
            [{"colspan": 3, "type": "xy"}, None, None],
            [{"colspan": 2, "type": "xy"}, None, {"type": "xy"}],
            [{"colspan": 3, "type": "xy"}, None, None],
            [{"colspan": 2, "type": "xy"}, None, {"type": "xy"}],
            [{"colspan": 3, "type": "xy"}, None, None],
        ],
        subplot_titles=titles,
        vertical_spacing=0.042,
        horizontal_spacing=0.09,
    )

    # KPI Cards rows 1-2
    kpi_data = [
        ("Total Procurement Spend", kpis["total_spend"] / 1e7,    "Crore Rs",          C_BLUE),
        ("Total Purchase Orders",   kpis["total_pos"],             "POs raised",        C_TEAL),
        ("Active Vendors",          kpis["total_vendors"],         "unique vendors",    C_GREEN),
        ("Avg PO Value",            kpis["avg_po_value"] / 1e3,   "Rs Thousands",      C_ORANGE),
        ("On-Time Delivery Rate",   kpis["on_time_delivery_rate"], "% on time",         C_GREEN),
        ("Invoice Exception Rate",  kpis["invoice_exception_rate"],"% exceptions",      C_RED),
    ]
    for (title, val, sub, col_), (r, c) in zip(kpi_data, [(1,1),(1,2),(1,3),(2,1),(2,2),(2,3)]):
        kpi_card(fig, r, c, title, val, sub, col_)

    # Row 3: Monthly Spend + Dept Pie
    month_vals = monthly["Total_Amount"] / 1e5
    fig.add_trace(go.Bar(
        x=monthly["Month"], y=month_vals,
        marker=dict(color=C_BLUE, line=dict(color="#0D3A6A", width=0.5)),
        name="Monthly Spend",
    ), row=3, col=1)
    fig.add_trace(go.Scatter(
        x=monthly["Month"], y=month_vals.cumsum(),
        mode="lines+markers",
        line=dict(color=C_GOLD, width=2.5, dash="dot"),
        marker=dict(size=6, color=C_GOLD),
        name="Cumulative",
    ), row=3, col=1)
    fig.add_trace(go.Pie(
        labels=dept["Department"], values=dept["Total_Amount"],
        hole=0.45,
        marker=dict(colors=PALETTE, line=dict(color=BG_CARD, width=2)),
        textfont=dict(color=TEXT_PRIMARY, size=10),
    ), row=3, col=3)

    # Row 4: Top Vendors
    sv = spend_vendor.sort_values("Total_Amount")
    fig.add_trace(go.Bar(
        x=sv["Total_Amount"] / 1e5, y=sv["Vendor_Name"],
        orientation="h",
        marker=dict(
            color=[PALETTE[i % len(PALETTE)] for i in range(len(sv))],
            line=dict(color=BG_CARD, width=0.5),
        ),
        name="Vendor Spend",
    ), row=4, col=1)

    # Row 5: Category + Quarterly
    fig.add_trace(go.Bar(
        x=spend_cat["Category"], y=spend_cat["Total_Amount"] / 1e5,
        marker=dict(color=C_TEAL, line=dict(color=BG_CARD, width=0.5)),
        name="Category Spend",
    ), row=5, col=1)
    fig.add_trace(go.Bar(
        x=quarterly["Quarter"], y=quarterly["Total_Spend"] / 1e5,
        marker=dict(
            color=[C_BLUE, C_TEAL, C_GREEN, C_ORANGE],
            line=dict(color=BG_CARD, width=0.5),
        ),
        name="Quarterly",
    ), row=5, col=3)

    # Row 6: Vendor Performance Scatter
    fig.add_trace(go.Scatter(
        x=vp["On_Time_Rate"], y=vp["Total_Spend"] / 1e5,
        mode="markers+text",
        text=vp["Vendor_Name"],
        textposition="top center",
        textfont=dict(color=TEXT_DIM, size=9),
        marker=dict(
            size=vp["Total_Orders"] * 3,
            color=C_PURPLE,
            opacity=0.85,
            line=dict(color="#C39BD3", width=1.5),
        ),
        name="Vendors",
    ), row=6, col=1)

    # Row 7: Box Plots (cycle times) + Payment Bar
    stages = [
        ("PO_Cycle_Days",       "PO Cycle",  PALETTE[0]),
        ("Delivery_Cycle_Days", "Delivery",  PALETTE[1]),
        ("Invoice_Cycle_Days",  "Invoice",   PALETTE[2]),
    ]
    for col_name, label, colour in stages:
        fig.add_trace(go.Box(
            y=df[col_name],
            name=label,
            marker=dict(color=colour, size=4, opacity=0.7),
            line=dict(color=colour, width=2),
            fillcolor=hex_to_rgba(colour, 0.20),
            boxmean=True,
            whiskerwidth=0.6,
            notched=False,
        ), row=7, col=1)

    vp_pay = vp.sort_values("Avg_Payment_Days")
    pay_colors = [
        C_GREEN if v < 35 else (C_ORANGE if v < 50 else C_RED)
        for v in vp_pay["Avg_Payment_Days"]
    ]
    fig.add_trace(go.Bar(
        x=vp_pay["Avg_Payment_Days"], y=vp_pay["Vendor_Name"],
        orientation="h",
        marker=dict(color=pay_colors, line=dict(color=BG_CARD, width=0.5)),
        text=[f"{v:.1f}d" for v in vp_pay["Avg_Payment_Days"]],
        textposition="outside",
        textfont=dict(color=TEXT_DIM, size=9),
        name="Avg Payment Days",
    ), row=7, col=3)

    # Row 8: E2E Histogram
    fig.add_trace(go.Histogram(
        x=df["E2E_Cycle_Days"],
        marker=dict(color=C_PURPLE, line=dict(color=BG_CARD, width=0.4)),
        opacity=0.85,
        name="E2E Days",
    ), row=8, col=1)

    # Row 9: On-Time Bar + Exception Bar
    vp_ot = vp.sort_values("On_Time_Rate")
    ot_colors = [
        C_GREEN if v >= 60 else (C_ORANGE if v >= 40 else C_RED)
        for v in vp_ot["On_Time_Rate"]
    ]
    fig.add_trace(go.Bar(
        x=vp_ot["On_Time_Rate"], y=vp_ot["Vendor_Name"],
        orientation="h",
        marker=dict(color=ot_colors, line=dict(color=BG_CARD, width=0.4)),
        text=[f"{v:.1f}%" for v in vp_ot["On_Time_Rate"]],
        textposition="outside",
        textfont=dict(color=TEXT_DIM, size=9),
        name="On-Time Rate",
    ), row=9, col=1)

    exception_vals = [10, 12, 8, 15, 5]
    exc_colors = [C_GREEN if v < 8 else (C_ORANGE if v < 12 else C_RED) for v in exception_vals]
    fig.add_trace(go.Bar(
        x=spend_cat["Category"], y=exception_vals,
        marker=dict(color=exc_colors, line=dict(color=BG_CARD, width=0.4)),
        text=[f"{v}%" for v in exception_vals],
        textposition="outside",
        textfont=dict(color=TEXT_DIM, size=9),
        name="Exception Rate",
    ), row=9, col=3)

    # Row 10: Pareto
    sv10 = spend_vendor.sort_values("Total_Amount", ascending=False)
    cumulative_pct = (sv10["Total_Amount"].cumsum() / sv10["Total_Amount"].sum() * 100)
    fig.add_trace(go.Bar(
        x=sv10["Vendor_Name"], y=sv10["Total_Amount"] / 1e5,
        marker=dict(color=C_BLUE, line=dict(color=BG_CARD, width=0.5)),
        name="Vendor Spend",
    ), row=10, col=1)
    fig.add_trace(go.Scatter(
        x=sv10["Vendor_Name"], y=cumulative_pct,
        mode="lines+markers",
        line=dict(color=C_GOLD, width=2.5),
        marker=dict(size=7, color=C_GOLD),
        name="Cumulative %",
        yaxis="y20",
    ), row=10, col=1)

    # Global Layout
    fig.update_layout(
        height=4000,
        paper_bgcolor=BG_CARD,
        plot_bgcolor=BG_PLOT,
        font=dict(family="IBM Plex Sans, sans-serif", size=11, color=TEXT_PRIMARY),
        showlegend=False,
        margin=dict(l=80, r=80, t=60, b=80),
    )

    # Subplot title style
    for ann in fig.layout.annotations:
        ann.font = dict(color=TEXT_PRIMARY, size=12,
                        family="IBM Plex Sans, sans-serif")
        ann.update(xanchor="center")

    # Apply axis styles to every axis
    for key in dir(fig.layout):
        if key.startswith("xaxis"):
            fig.layout[key].update(axis())
        elif key.startswith("yaxis"):
            fig.layout[key].update(axis())

    # Axis labels
    fig.update_xaxes(title_text="Month",            row=3, col=1)
    fig.update_yaxes(title_text="Rs Lakhs",         row=3, col=1)
    fig.update_xaxes(title_text="Rs Lakhs",         row=4, col=1)
    fig.update_xaxes(title_text="Category",         row=5, col=1)
    fig.update_yaxes(title_text="Rs Lakhs",         row=5, col=1)
    fig.update_xaxes(title_text="Quarter",          row=5, col=3)
    fig.update_yaxes(title_text="Rs Lakhs",         row=5, col=3)
    fig.update_xaxes(title_text="On-Time Rate (%)", row=6, col=1)
    fig.update_yaxes(title_text="Spend (Rs Lakhs)", row=6, col=1)
    fig.update_yaxes(title_text="Days",             row=7, col=1)
    fig.update_xaxes(title_text="Avg Days",         row=7, col=3, range=[0, vp["Avg_Payment_Days"].max() * 1.25])
    fig.update_xaxes(title_text="Cycle Days",       row=8, col=1)
    fig.update_yaxes(title_text="Frequency",        row=8, col=1)
    fig.update_xaxes(title_text="On-Time Rate (%)", row=9, col=1, range=[0, 110])
    fig.update_xaxes(title_text="Category",         row=9, col=3)
    fig.update_yaxes(title_text="Exception (%)",    row=9, col=3, range=[0, 20])
    fig.update_xaxes(title_text="Vendor",           row=10, col=1)
    fig.update_yaxes(title_text="Rs Lakhs",         row=10, col=1)

    # Build HTML
    plotly_html = fig.to_html(full_html=False, include_plotlyjs="cdn")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SAP P2P Analytics Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'IBM Plex Sans', sans-serif;
    background: {BG_PAGE};
    color: {TEXT_PRIMARY};
    min-height: 100vh;
  }}
  .header {{
    background: linear-gradient(135deg, #041A2F 0%, #0A2847 50%, #061E35 100%);
    border-bottom: 2px solid #1B4F7A;
    padding: 28px 60px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: relative;
    overflow: hidden;
  }}
  .header::before {{
    content: '';
    position: absolute;
    inset: 0;
    background: repeating-linear-gradient(
      -45deg, transparent, transparent 40px,
      rgba(0,174,239,0.03) 40px, rgba(0,174,239,0.03) 41px
    );
  }}
  .header-left h1 {{
    font-size: 24px;
    font-weight: 700;
    letter-spacing: 0.02em;
    color: {TEXT_PRIMARY};
    margin-bottom: 4px;
  }}
  .header-left p {{ font-size: 13px; color: {TEXT_DIM}; font-weight: 300; }}
  .header-right {{ text-align: right; font-size: 12px; color: {TEXT_DIM}; line-height: 1.8; }}
  .badge {{
    display: inline-block;
    background: rgba(0,174,239,0.15);
    border: 1px solid rgba(0,174,239,0.4);
    color: {C_BLUE};
    padding: 3px 12px;
    border-radius: 4px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.1em;
    margin-bottom: 6px;
  }}
  .breadcrumb {{
    background: #09192A;
    border-bottom: 1px solid #1B3A55;
    padding: 10px 60px;
    font-size: 11px;
    color: {TEXT_DIM};
    letter-spacing: 0.08em;
    font-family: 'IBM Plex Mono', monospace;
  }}
  .breadcrumb span {{ color: {C_BLUE}; }}
  .main-container {{ max-width: 1440px; margin: 30px auto; padding: 0 30px 40px; }}
  .chart-card {{
    background: {BG_CARD};
    border: 1px solid #1B3A55;
    border-radius: 14px;
    padding: 24px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.04);
  }}
  .footer {{
    background: #06131F;
    border-top: 1px solid #1B3A55;
    padding: 24px 60px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    color: {TEXT_DIM};
  }}
  .footer strong {{ color: {TEXT_PRIMARY}; }}
  .footer-right {{ font-family: 'IBM Plex Mono', monospace; font-size: 11px; }}
</style>
</head>
<body>
<div class="header">
  <div class="header-left">
    <h1>SAP Procure-to-Pay (P2P) Data Analytics</h1>
    <p>Automated KPI Monitoring and Process Bottleneck Detection | FY 2024</p>
  </div>
  <div class="header-right">
    <div class="badge">CSE-46</div><br>
    <span>Generated: {pd.Timestamp.now().strftime('%d %b %Y, %H:%M')}</span><br>
    <span>KIIT University | SAP Capstone</span>
  </div>
</div>
<div class="breadcrumb">
  SAP MM/FI &nbsp;&rsaquo;&nbsp; <span>P2P Analytics</span> &nbsp;&rsaquo;&nbsp; Interactive Dashboard &nbsp;&rsaquo;&nbsp; 500 Transactions
</div>
<div class="main-container">
  <div class="chart-card">{plotly_html}</div>
</div>
<div class="footer">
  <div><strong>Nitish Kumar Biswal</strong> &nbsp;|&nbsp; Roll: 2305950 &nbsp;|&nbsp; CSE-46 &nbsp;|&nbsp; KIIT University</div>
  <div class="footer-right">Python &middot; Pandas &middot; Plotly &nbsp;|&nbsp; SAP MM &middot; FI-AP</div>
</div>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"[OK] Dashboard saved -> {output_path}")
    return output_path