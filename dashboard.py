"""
dashboard.py
Builds a fully interactive Plotly HTML dashboard for SAP P2P Analytics.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import os

import analytics as ana

# ── Colour palette (SAP-inspired) ────────────────────────────────────────────
SAP_BLUE = "#0070F2"
SAP_TEAL = "#00A8A8"
SAP_GREEN = "#30914C"
SAP_ORANGE = "#E9730C"
SAP_RED = "#BB0000"
SAP_PURPLE = "#6B3FA0"
SAP_GRAY = "#707070"
BG_COLOR = "#F5F6FA"
CARD_COLOR = "#FFFFFF"

PALETTE = [SAP_BLUE, SAP_TEAL, SAP_GREEN, SAP_ORANGE, SAP_RED, SAP_PURPLE,
           "#0040B0", "#00C4AA", "#8BC400", "#C14646"]


def fmt_inr(val: float) -> str:
    """Format value in Indian Rupees with Cr/L suffixes."""
    if val >= 1e7:
        return f"₹{val/1e7:.2f} Cr"
    elif val >= 1e5:
        return f"₹{val/1e5:.2f} L"
    else:
        return f"₹{val:,.0f}"


def kpi_card(fig, row, col, title, value, subtitle="", color=SAP_BLUE):
    fig.add_trace(go.Indicator(
        mode="number",
        value=value,
        title={"text": f"<b>{title}</b><br><span style='font-size:12px;color:#888'>{subtitle}</span>",
               "font": {"size": 14}},
        number={"font": {"size": 28, "color": color}, "valueformat": ",.0f"},
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
            [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],   # R1 KPIs
            [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],   # R2 KPIs
            [{"colspan": 2, "type": "xy"}, None, {"type": "pie"}],                   # R3 Monthly + Dept pie
            [{"colspan": 3, "type": "xy"}, None, None],                              # R4 Vendor spend bar
            [{"colspan": 2, "type": "xy"}, None, {"type": "xy"}],                    # R5 Category bar + Quarterly
            [{"colspan": 3, "type": "xy"}, None, None],                              # R6 Vendor perf scatter
            [{"colspan": 2, "type": "xy"}, None, {"type": "xy"}],                    # R7 Cycle box + Payment
            [{"colspan": 3, "type": "xy"}, None, None],                              # R8 E2E cycle histogram
            [{"colspan": 2, "type": "xy"}, None, {"type": "xy"}],                    # R9 On-time heatmap + inv exc
            [{"colspan": 3, "type": "xy"}, None, None],                              # R10 Spend Pareto
        ],
        subplot_titles=(
            "", "", "",
            "", "", "",
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
    kpi_cards = [
        ("Total Procurement Spend", kpis["total_spend"] / 1e7, "in Crore ₹", SAP_BLUE),
        ("Total Purchase Orders", kpis["total_pos"], "POs raised", SAP_TEAL),
        ("Active Vendors", kpis["total_vendors"], "unique vendors", SAP_GREEN),
        ("Avg PO Value", kpis["avg_po_value"] / 1e3, "in ₹ Thousands", SAP_ORANGE),
        ("On-Time Delivery Rate", kpis["on_time_delivery_rate"], "% deliveries on time", SAP_GREEN),
        ("Invoice Exception Rate", kpis["invoice_exception_rate"], "% invoices with exceptions", SAP_RED),
    ]
    positions = [(1,1),(1,2),(1,3),(2,1),(2,2),(2,3)]
    for (title, val, sub, col_), (r, c) in zip(kpi_cards, positions):
        kpi_card(fig, r, c, title, val, sub, col_)

    # ── ROW 3 Left: Monthly Spend Line ────────────────────────────────────────
    fig.add_trace(go.Bar(
        x=monthly["Month"], y=monthly["Total_Amount"] / 1e5,
        name="Monthly Spend (₹L)",
        marker_color=SAP_BLUE, opacity=0.8,
    ), row=3, col=1)
    fig.add_trace(go.Scatter(
        x=monthly["Month"], y=monthly["Cumulative_Spend"] / 1e7,
        name="Cumulative (₹Cr)",
        yaxis="y2", mode="lines+markers",
        line=dict(color=SAP_ORANGE, width=2.5),
        marker=dict(size=6),
    ), row=3, col=1)

    # ── ROW 3 Right: Department Pie ───────────────────────────────────────────
    fig.add_trace(go.Pie(
        labels=dept["Department"], values=dept["Total_Amount"],
        hole=0.4, marker_colors=PALETTE,
        textinfo="label+percent",
        showlegend=False,
    ), row=3, col=3)

    # ── ROW 4: Top Vendor Horizontal Bar ──────────────────────────────────────
    fig.add_trace(go.Bar(
        x=spend_vendor["Total_Amount"] / 1e5,
        y=spend_vendor["Vendor_Name"],
        orientation="h",
        marker=dict(color=PALETTE[:len(spend_vendor)]),
        text=[f"₹{v/1e5:.1f}L" for v in spend_vendor["Total_Amount"]],
        textposition="outside",
        showlegend=False,
    ), row=4, col=1)

    # ── ROW 5 Left: Category Spend Bar ───────────────────────────────────────
    fig.add_trace(go.Bar(
        x=spend_cat["Category"], y=spend_cat["Total_Amount"] / 1e5,
        marker_color=PALETTE[:len(spend_cat)],
        showlegend=False,
    ), row=5, col=1)

    # ── ROW 5 Right: Quarterly Grouped Bar ───────────────────────────────────
    fig.add_trace(go.Bar(
        x=quarterly["Quarter"], y=quarterly["Total_Spend"] / 1e5,
        name="Total Spend (₹L)", marker_color=SAP_BLUE,
    ), row=5, col=3)
    fig.add_trace(go.Bar(
        x=quarterly["Quarter"], y=quarterly["Num_POs"],
        name="No. of POs", marker_color=SAP_TEAL,
    ), row=5, col=3)

    # ── ROW 6: Vendor Performance Scatter ────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=vp["On_Time_Rate"], y=vp["Total_Spend"] / 1e5,
        mode="markers+text",
        marker=dict(
            size=vp["Total_Orders"] * 2.5,
            color=vp["Invoice_Exception_Rate"],
            colorscale="RdYlGn_r",
            showscale=True,
            colorbar=dict(title="Invoice<br>Exc. Rate %", x=1.02, len=0.3, y=0.38),
        ),
        text=vp["Vendor_Name"],
        textposition="top center",
        showlegend=False,
    ), row=6, col=1)

    # ── ROW 7 Left: Cycle Time Box Plots ─────────────────────────────────────
    stages = {
        "PR→PO": df["PO_Cycle_Days"],
        "PO→GR": df["Delivery_Cycle_Days"],
        "GR→Inv": df["Invoice_Cycle_Days"],
        "Inv→Pay": df["Payment_Cycle_Days"],
    }
    for i, (label, data) in enumerate(stages.items()):
        fig.add_trace(go.Box(
            y=data, name=label,
            marker_color=PALETTE[i], boxmean=True, showlegend=False,
        ), row=7, col=1)

    # ── ROW 7 Right: Payment Cycle by Vendor ─────────────────────────────────
    vp_sorted = vp.sort_values("Avg_Payment_Days", ascending=True)
    fig.add_trace(go.Bar(
        x=vp_sorted["Avg_Payment_Days"],
        y=vp_sorted["Vendor_Name"],
        orientation="h",
        marker_color=SAP_TEAL,
        showlegend=False,
    ), row=7, col=3)

    # ── ROW 8: E2E Cycle Histogram ───────────────────────────────────────────
    fig.add_trace(go.Histogram(
        x=df["E2E_Cycle_Days"],
        nbinsx=30,
        marker_color=SAP_PURPLE,
        opacity=0.8,
        name="E2E Cycle Days",
        showlegend=False,
    ), row=8, col=1)
    # Add mean line via shape annotation later

    # ── ROW 9 Left: On-Time Delivery by Vendor ───────────────────────────────
    vp_ot = vp.sort_values("On_Time_Rate", ascending=True)
    colors_ot = [SAP_GREEN if r >= 70 else SAP_ORANGE if r >= 50 else SAP_RED
                 for r in vp_ot["On_Time_Rate"]]
    fig.add_trace(go.Bar(
        x=vp_ot["On_Time_Rate"], y=vp_ot["Vendor_Name"],
        orientation="h",
        marker_color=colors_ot,
        text=[f"{r:.1f}%" for r in vp_ot["On_Time_Rate"]],
        textposition="outside",
        showlegend=False,
    ), row=9, col=1)

    # ── ROW 9 Right: Invoice Exception by Category ────────────────────────────
    inv_cat = df.groupby("Category")["Invoice_Exception"].mean().reset_index()
    inv_cat["Rate"] = inv_cat["Invoice_Exception"] * 100
    inv_cat = inv_cat.sort_values("Rate", ascending=False)
    fig.add_trace(go.Bar(
        x=inv_cat["Category"], y=inv_cat["Rate"],
        marker_color=[SAP_RED if r > 15 else SAP_ORANGE if r > 10 else SAP_GREEN
                      for r in inv_cat["Rate"]],
        showlegend=False,
    ), row=9, col=3)

    # ── ROW 10: Pareto Chart ──────────────────────────────────────────────────
    pareto = spend_vendor.sort_values("Total_Amount", ascending=False).copy()
    pareto["Cumulative_%"] = pareto["Total_Amount"].cumsum() / pareto["Total_Amount"].sum() * 100
    fig.add_trace(go.Bar(
        x=pareto["Vendor_Name"], y=pareto["Total_Amount"] / 1e5,
        marker_color=SAP_BLUE, name="Vendor Spend (₹L)", showlegend=True,
    ), row=10, col=1)
    fig.add_trace(go.Scatter(
        x=pareto["Vendor_Name"], y=pareto["Cumulative_%"],
        mode="lines+markers", name="Cumulative %",
        line=dict(color=SAP_RED, width=2), yaxis="y3", showlegend=True,
    ), row=10, col=1)

    # ── Global layout ─────────────────────────────────────────────────────────
    fig.update_layout(
        title={
            "text": (
                "<b>SAP Procure-to-Pay (P2P) Analytics Dashboard</b><br>"
                "<span style='font-size:13px;color:#555'>FY 2024 | 500 Transactions | 10 Vendors</span>"
            ),
            "x": 0.5, "xanchor": "center",
            "font": {"size": 22, "family": "Arial"},
        },
        height=3800,
        paper_bgcolor=BG_COLOR,
        plot_bgcolor=CARD_COLOR,
        font=dict(family="Arial", size=11),
        legend=dict(orientation="h", y=-0.01),
        margin=dict(l=60, r=60, t=120, b=60),
        barmode="group",
    )

    # Axis labels
    fig.update_xaxes(title_text="Month", row=3, col=1)
    fig.update_yaxes(title_text="Spend (₹ Lakhs)", row=3, col=1)
    fig.update_xaxes(title_text="Total Spend (₹ Lakhs)", row=4, col=1)
    fig.update_xaxes(title_text="Category", row=5, col=1, tickangle=30)
    fig.update_yaxes(title_text="Spend (₹ Lakhs)", row=5, col=1)
    fig.update_xaxes(title_text="On-Time Delivery Rate (%)", row=6, col=1)
    fig.update_yaxes(title_text="Total Spend (₹ Lakhs)", row=6, col=1)
    fig.update_yaxes(title_text="Days", row=7, col=1)
    fig.update_xaxes(title_text="Avg Payment Days", row=7, col=3)
    fig.update_xaxes(title_text="E2E Cycle Time (Days)", row=8, col=1)
    fig.update_yaxes(title_text="Number of Transactions", row=8, col=1)
    fig.update_xaxes(title_text="On-Time Rate (%)", row=9, col=1)
    fig.update_xaxes(title_text="Category", row=9, col=3, tickangle=30)
    fig.update_yaxes(title_text="Exception Rate (%)", row=9, col=3)
    fig.update_xaxes(title_text="Vendor", row=10, col=1)
    fig.update_yaxes(title_text="Spend (₹ Lakhs)", row=10, col=1)

    fig.write_html(output_path)
    print(f"[✓] Dashboard saved → {output_path}")
    return output_path


if __name__ == "__main__":
    df = ana.load_data()
    kpis = ana.compute_kpis(df)
    build_dashboard(df, kpis)
