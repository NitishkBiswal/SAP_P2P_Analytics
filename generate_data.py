"""
generate_data.py
Generates synthetic SAP-style Procure-to-Pay (P2P) transaction data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

random.seed(42)
np.random.seed(42)

# ── Master data ──────────────────────────────────────────────────────────────
VENDORS = {
    "V001": "TechSupply Pvt Ltd",
    "V002": "GlobalProcure Inc",
    "V003": "SwiftLogistics Co",
    "V004": "PrimeMaterials Ltd",
    "V005": "NexaVendors Corp",
    "V006": "AlphaGoods Pvt Ltd",
    "V007": "ZenithSupplies Ltd",
    "V008": "CoreTrade Inc",
    "V009": "BrightSource Co",
    "V010": "Pinnacle Supplies",
}

CATEGORIES = [
    "IT Equipment", "Office Supplies", "Raw Materials",
    "Logistics", "Maintenance", "Professional Services",
    "Software Licenses", "Utilities", "Marketing", "Consumables"
]

DEPARTMENTS = [
    "Finance", "IT", "Operations", "Procurement",
    "HR", "Marketing", "R&D", "Logistics"
]

UNIT_PRICE_RANGE = {
    "IT Equipment": (15000, 150000),
    "Office Supplies": (200, 5000),
    "Raw Materials": (1000, 50000),
    "Logistics": (5000, 80000),
    "Maintenance": (3000, 40000),
    "Professional Services": (20000, 200000),
    "Software Licenses": (10000, 100000),
    "Utilities": (5000, 30000),
    "Marketing": (8000, 120000),
    "Consumables": (500, 10000),
}

PAYMENT_TERMS = {
    "V001": 30, "V002": 45, "V003": 30, "V004": 60,
    "V005": 30, "V006": 45, "V007": 30, "V008": 60,
    "V009": 45, "V010": 30,
}


def random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


def generate_p2p_transactions(n: int = 500) -> pd.DataFrame:
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)

    records = []
    vendor_ids = list(VENDORS.keys())

    for i in range(1, n + 1):
        # ── PR ────────────────────────────────────────────────────────────────
        pr_date = random_date(start_date, end_date - timedelta(days=90))
        category = random.choice(CATEGORIES)
        department = random.choice(DEPARTMENTS)
        vendor_id = random.choice(vendor_ids)
        qty = random.randint(1, 50)
        lo, hi = UNIT_PRICE_RANGE[category]
        unit_price = round(random.uniform(lo, hi), 2)
        total_amount = round(qty * unit_price, 2)

        # ── PO (PR + 1–10 days) ───────────────────────────────────────────────
        pr_to_po = random.randint(1, 10)
        po_date = pr_date + timedelta(days=pr_to_po)

        # ── Agreed delivery (PO + 7–30 days) ─────────────────────────────────
        lead_time = random.randint(7, 30)
        expected_delivery = po_date + timedelta(days=lead_time)

        # ── Actual GR (some late, some on-time) ──────────────────────────────
        delay = random.choices([-2, 0, 2, 5, 10], weights=[10, 40, 25, 15, 10])[0]
        gr_date = expected_delivery + timedelta(days=delay)
        on_time = delay <= 0

        # ── Invoice (GR + 1–7 days) ───────────────────────────────────────────
        inv_delay = random.randint(1, 7)
        invoice_date = gr_date + timedelta(days=inv_delay)

        # ── Invoice exception ─────────────────────────────────────────────────
        invoice_exception = random.random() < 0.12   # 12% exception rate

        # ── Payment (Invoice + payment_terms ± variance) ─────────────────────
        terms = PAYMENT_TERMS[vendor_id]
        pay_variance = random.randint(-5, 10)
        payment_date = invoice_date + timedelta(days=max(terms + pay_variance, 1))

        # ── Cycle times (days) ────────────────────────────────────────────────
        po_cycle = (po_date - pr_date).days
        delivery_cycle = (gr_date - po_date).days
        invoice_cycle = (invoice_date - gr_date).days
        payment_cycle = (payment_date - invoice_date).days
        e2e_cycle = (payment_date - pr_date).days

        records.append({
            "Transaction_ID": f"TXN{i:04d}",
            "PR_ID": f"PR{i:04d}",
            "PO_ID": f"PO{i:04d}",
            "GR_ID": f"GR{i:04d}",
            "Invoice_ID": f"INV{i:04d}",
            "Vendor_ID": vendor_id,
            "Vendor_Name": VENDORS[vendor_id],
            "Category": category,
            "Department": department,
            "Quantity": qty,
            "Unit_Price": unit_price,
            "Total_Amount": total_amount,
            "PR_Date": pr_date.date(),
            "PO_Date": po_date.date(),
            "Expected_Delivery": expected_delivery.date(),
            "GR_Date": gr_date.date(),
            "Invoice_Date": invoice_date.date(),
            "Payment_Date": payment_date.date(),
            "PO_Cycle_Days": po_cycle,
            "Delivery_Cycle_Days": delivery_cycle,
            "Invoice_Cycle_Days": invoice_cycle,
            "Payment_Cycle_Days": payment_cycle,
            "E2E_Cycle_Days": e2e_cycle,
            "On_Time_Delivery": on_time,
            "Invoice_Exception": invoice_exception,
            "Month": pr_date.strftime("%b"),
            "Month_Num": pr_date.month,
            "Quarter": f"Q{(pr_date.month - 1) // 3 + 1}",
        })

    df = pd.DataFrame(records)
    df.to_csv("data/p2p_transactions.csv", index=False)
    print(f"[✓] Generated {n} P2P transactions → data/p2p_transactions.csv")
    return df


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    df = generate_p2p_transactions(500)
    print(df.head())
