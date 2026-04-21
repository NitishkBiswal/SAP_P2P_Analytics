"""
analytics.py
Computes all P2P KPIs and analytics from transaction data.
"""

import pandas as pd
import numpy as np


def load_data(path: str = "data/p2p_transactions.csv") -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=[
        "PR_Date", "PO_Date", "Expected_Delivery",
        "GR_Date", "Invoice_Date", "Payment_Date"
    ])
    return df


def compute_kpis(df: pd.DataFrame) -> dict:
    kpis = {}

    kpis["total_spend"] = df["Total_Amount"].sum()
    kpis["total_pos"] = df["PO_ID"].nunique()
    kpis["total_vendors"] = df["Vendor_ID"].nunique()
    kpis["avg_po_value"] = df["Total_Amount"].mean()

    kpis["avg_po_cycle"] = df["PO_Cycle_Days"].mean()
    kpis["avg_delivery_cycle"] = df["Delivery_Cycle_Days"].mean()
    kpis["avg_invoice_cycle"] = df["Invoice_Cycle_Days"].mean()
    kpis["avg_payment_cycle"] = df["Payment_Cycle_Days"].mean()
    kpis["avg_e2e_cycle"] = df["E2E_Cycle_Days"].mean()

    kpis["on_time_delivery_rate"] = df["On_Time_Delivery"].mean() * 100
    kpis["invoice_exception_rate"] = df["Invoice_Exception"].mean() * 100

    return kpis


def spend_by_category(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Category")["Total_Amount"]
        .sum()
        .reset_index()
        .sort_values("Total_Amount", ascending=False)
    )


def spend_by_vendor(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    return (
        df.groupby(["Vendor_ID", "Vendor_Name"])["Total_Amount"]
        .sum()
        .reset_index()
        .sort_values("Total_Amount", ascending=False)
        .head(top_n)
    )


def monthly_spend_trend(df: pd.DataFrame) -> pd.DataFrame:
    monthly = (
        df.groupby(["Month_Num", "Month"])["Total_Amount"]
        .sum()
        .reset_index()
        .sort_values("Month_Num")
    )
    monthly["Cumulative_Spend"] = monthly["Total_Amount"].cumsum()
    return monthly


def vendor_performance(df: pd.DataFrame) -> pd.DataFrame:
    vp = df.groupby(["Vendor_ID", "Vendor_Name"]).agg(
        Total_Orders=("PO_ID", "count"),
        Total_Spend=("Total_Amount", "sum"),
        On_Time_Rate=("On_Time_Delivery", lambda x: x.mean() * 100),
        Invoice_Exception_Rate=("Invoice_Exception", lambda x: x.mean() * 100),
        Avg_Delivery_Days=("Delivery_Cycle_Days", "mean"),
        Avg_Payment_Days=("Payment_Cycle_Days", "mean"),
    ).reset_index()
    return vp


def spend_by_department(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Department")["Total_Amount"]
        .sum()
        .reset_index()
        .sort_values("Total_Amount", ascending=False)
    )


def quarterly_spend(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Quarter")["Total_Amount"]
        .agg(["sum", "count", "mean"])
        .reset_index()
        .rename(columns={"sum": "Total_Spend", "count": "Num_POs", "mean": "Avg_PO_Value"})
    )


def cycle_time_stats(df: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "PO_Cycle_Days", "Delivery_Cycle_Days",
        "Invoice_Cycle_Days", "Payment_Cycle_Days", "E2E_Cycle_Days"
    ]
    labels = ["PR→PO", "PO→GR", "GR→Invoice", "Invoice→Payment", "End-to-End"]
    stats = []
    for col, label in zip(cols, labels):
        stats.append({
            "Stage": label,
            "Min": df[col].min(),
            "Avg": round(df[col].mean(), 1),
            "Median": df[col].median(),
            "Max": df[col].max(),
            "Std": round(df[col].std(), 1),
        })
    return pd.DataFrame(stats)


if __name__ == "__main__":
    df = load_data()
    kpis = compute_kpis(df)
    print("\n── KPI Summary ──────────────────────────────────")
    for k, v in kpis.items():
        if "spend" in k or "value" in k:
            print(f"  {k:<30} ₹{v:>15,.0f}")
        elif "rate" in k or "cycle" in k.lower() or "days" in k.lower():
            print(f"  {k:<30} {v:>10.2f}")
        else:
            print(f"  {k:<30} {v:>10}")

    print("\n── Cycle Time Stats ─────────────────────────────")
    print(cycle_time_stats(df).to_string(index=False))
