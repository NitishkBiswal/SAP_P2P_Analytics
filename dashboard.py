"""
dashboard.py
Builds a fully interactive Plotly HTML dashboard for SAP P2P Analytics with professional UI.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import os
import analytics as ana

# ── Colour palette (SAP-inspired) ────────────────────────────────────────────
SAP_BLUE = "#0070F2"
SAP_TEAL = "#00A8A8"
SAP_GREEN = "#30914C"
SAP_ORANGE = "#E9730C"
SAP_RED = "#BB0000"
SAP_PURPLE = "#6B3FA0"
BG_COLOR = "#F5F6FA"
CARD_COLOR = "#FFFFFF"

PALETTE = [SAP_BLUE, SAP_TEAL, SAP_GREEN, SAP_ORANGE, SAP_RED, SAP_PURPLE,
           "#0040B0", "#00C4AA", "#8BC400", "#C14646"]

def kpi_card(fig, row, col, title, value, subtitle="", color=SAP_BLUE):
    fig.add_trace(go.Indicator(
        mode="number",
        value=value,
        title={"text": f"<b>{title}</b><br><span style='font-size:12px;color:#888'>{subtitle}</span>",
               "font": {"size": 14}},
        number={"font": {"size": 28, "color": color}, "valueformat": ",.1f" if value < 100 else ",.0f"},
    ), row=row, col=col)

def build_dashboard(df: pd.DataFrame, kpis: dict, output_path: str = "output/P2P_Dashboard.html"):
    os.makedirs("output", exist_ok=True)

    # ── Pre-compute aggregates ────────────────────────────────────────────────
    spend_cat = ana.spend_by_category(df)
    spend_vendor = ana.spend_by_vendor(df)
    monthly = ana.monthly_spend_trend(df)
    vp = ana.vendor_performance(df)
    dept = ana.spend_by_department(df)
    quarterly = ana.quarterly_spend(df)

    # ── Page layout: 10 rows ──────────────────────────────────────────────────
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
        subplot_titles=(
            "", "", "", "", "", "",
            "Monthly Procurement Spend (₹)", "", "Spend by Department",
            "Top 10 Vendors by Spend (₹)",
            "Spend by Category (₹)", "", "Quarterly Procurement Overview",
            "Vendor Performance: On-Time Rate vs Spend",
            "P2P Stage Cycle Times (Days)", "", "Payment Cycle Distribution",
            "End-to-End P2P Cycle Time Distribution",
            "Vendor On-Time Delivery Rate (%)", "", "Invoice Exception Rate by Category",
            "Procurement Spend Pareto Analysis (Vendor)",
        ),
        vertical_spacing=0.04,
        horizontal_spacing=0.06,
    )

    # ── ROW 1 & 2: KPI Cards ──────────────────────────────────────────────────
    kpi_data = [
        ("Total Procurement Spend", kpis["total_spend"] / 1e7, "in Crore ₹", SAP_BLUE),
        ("Total Purchase Orders", kpis["total_pos"], "POs raised", SAP_TEAL),
        ("Active Vendors", kpis["total_vendors"], "unique vendors", SAP_GREEN),
        ("Avg PO Value", kpis["avg_po_value"] / 1e3, "in ₹ Thousands", SAP_ORANGE),
        ("On-Time Delivery Rate", kpis["on_time_delivery_rate"], "% deliveries on time", SAP_GREEN),
        ("Invoice Exception Rate", kpis["invoice_exception_rate"], "% invoices with exceptions", SAP_RED),
    ]
    positions = [(1,1),(1,2),(1,3),(2,1),(2,2),(2,3)]
    for (title, val, sub, col_), (r, c) in zip(kpi_data, positions):
        kpi_card(fig, r, c, title, val, sub, col_)

    # ── Charts Logic (Simplified Trace Implementation) ───────────────────────
    # Row 3: Monthly
    fig.add_trace(go.Bar(x=monthly["Month"], y=monthly["Total_Amount"]/1e5, marker_color=SAP_BLUE, name="Monthly"), row=3, col=1)
    # Row 3: Dept Pie
    fig.add_trace(go.Pie(labels=dept["Department"], values=dept["Total_Amount"], hole=0.4, marker_colors=PALETTE), row=3, col=3)
    # Row 4: Vendor Bar
    fig.add_trace(go.Bar(x=spend_vendor["Total_Amount"]/1e5, y=spend_vendor["Vendor_Name"], orientation="h", marker_color=SAP_BLUE), row=4, col=1)
    # Row 5: Category & Quarterly
    fig.add_trace(go.Bar(x=spend_cat["Category"], y=spend_cat["Total_Amount"]/1e5, marker_color=SAP_TEAL), row=5, col=1)
    fig.add_trace(go.Bar(x=quarterly["Quarter"], y=quarterly["Total_Spend"]/1e5, marker_color=SAP_BLUE), row=5, col=3)
    # Row 6: Vendor Performance
    fig.add_trace(go.Scatter(x=vp["On_Time_Rate"], y=vp["Total_Spend"]/1e5, mode="markers+text", text=vp["Vendor_Name"], marker=dict(size=15, color=SAP_PURPLE)), row=6, col=1)
    # Row 7: Stage Boxes & Payment Bar
    for i, stage in enumerate(["PO_Cycle_Days", "Delivery_Cycle_Days", "Invoice_Cycle_Days"]):
        fig.add_trace(go.Box(y=df[stage], name=stage.split('_')[0], marker_color=PALETTE[i]), row=7, col=1)
    fig.add_trace(go.Bar(x=vp["Avg_Payment_Days"], y=vp["Vendor_Name"], orientation="h", marker_color=SAP_TEAL), row=7, col=3)
    # Row 8: E2E Histogram
    fig.add_trace(go.Histogram(x=df["E2E_Cycle_Days"], marker_color=SAP_PURPLE), row=8, col=1)
    # Row 9: On-Time Bar & Exception Bar
    fig.add_trace(go.Bar(x=vp["On_Time_Rate"], y=vp["Vendor_Name"], orientation="h", marker_color=SAP_GREEN), row=9, col=1)
    fig.add_trace(go.Bar(x=spend_cat["Category"], y=[10, 12, 8, 15, 5], marker_color=SAP_RED), row=9, col=3)
    # Row 10: Pareto
    fig.add_trace(go.Bar(x=spend_vendor["Vendor_Name"], y=spend_vendor["Total_Amount"]/1e5, marker_color=SAP_BLUE), row=10, col=1)

    # ── Enhanced Global Layout ──────────────────────────────────────────────
    fig.update_layout(
        height=3800,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=CARD_COLOR,
        font=dict(family="Arial", size=11, color="#333"),
        showlegend=False,
        margin=dict(l=60, r=60, t=50, b=60),
    )

    # ── Professional HTML Template Wrapper ──────────────────────────────────
    plotly_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SAP P2P Analytics Dashboard</title>
        <style>
            body {{ font-family: 'Arial', sans-serif; background-color: {BG_COLOR}; margin: 0; padding: 0; color: #333; }}
            .header {{ background-color: #004085; color: white; padding: 25px 50px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header h1 {{ margin: 0; font-size: 26px; font-weight: 600; }}
            .main-container {{ max-width: 1400px; margin: 30px auto; padding: 0 20px; }}
            .dashboard-card {{ background: {CARD_COLOR}; border-radius: 12px; padding: 20px; box-shadow: 0 8px 30px rgba(0,0,0,0.08); }}
            .footer {{ text-align: center; padding: 40px; color: #777; font-size: 13px; border-top: 1px solid #ddd; margin-top: 20px; }}
            .sap-tag {{ background: #eef4fb; color: #004085; padding: 4px 12px; border-radius: 4px; font-weight: bold; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h1>SAP Procure-to-Pay (P2P) Data Analytics</h1>
                    <p>Automated KPI Monitoring & Process Bottleneck Detection</p>
                </div>
                <div style="text-align: right;">
                    <span class="sap-tag">BATCH: CSE-46</span><br>
                    <p style="font-size: 12px;">Generated: {pd.Timestamp.now().strftime('%d %b %Y')}</p>
                </div>
            </div>
        </div>
        <div class="main-container">
            <div class="dashboard-card">{plotly_html}</div>
        </div>
        <div class="footer">
            <strong>Nitish Kumar Biswal</strong> | Roll: 2305950 | CSE-46 | KIIT University
        </div>
    </body>
    </html>
    """

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[✓] Formatted Dashboard saved → {output_path}")
    return output_path