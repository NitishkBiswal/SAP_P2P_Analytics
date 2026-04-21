# SAP Procure-to-Pay (P2P) Data Analytics

**KIIT University | SAP Data Analytics Capstone Project**
**Student:** Nitish Kumar Biswal | **Roll:** 2305950 | **Batch:** CSE-46

---

## Overview

A complete end-to-end **SAP Procure-to-Pay (P2P) Data Analytics** solution built in Python.
The project simulates 500 SAP MM/FI procurement transactions across the full P2P cycle
(Purchase Requisition → Purchase Order → Goods Receipt → Invoice → Payment) and delivers
an interactive analytical dashboard with 10 visualisation panels.

## Project Structure

```
SAP_P2P_Analytics/
├── generate_data.py        # Synthetic SAP P2P transaction data generator
├── analytics.py            # KPI computation & aggregation engine
├── dashboard.py            # Interactive Plotly HTML dashboard builder
├── main.py                 # End-to-end pipeline orchestrator
├── requirements.txt        # Python dependencies
├── data/
│   └── p2p_transactions.csv   # Generated dataset (500 rows, 25 columns)
└── output/
    ├── P2P_Dashboard.html          # Interactive analytics dashboard
    └── SAP_P2P_Analytics_Report.pdf  # Project documentation
```

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the full pipeline
python main.py

# 3. Open the dashboard
open output/P2P_Dashboard.html   # macOS
# or: start output/P2P_Dashboard.html  (Windows)
```

## Key KPIs (FY 2024)

| KPI | Value |
|-----|-------|
| Total Procurement Spend | ₹51.42 Crore |
| Total Purchase Orders | 500 |
| Active Vendors | 10 |
| Avg PO Value | ₹10.28 Lakhs |
| On-Time Delivery Rate | 47.2% |
| Invoice Exception Rate | 10.4% |
| Avg End-to-End Cycle | 74.7 days |

## Dashboard Panels

1. **KPI Cards** — 6 headline metrics
2. **Monthly Spend Trend** — Bar + cumulative line
3. **Spend by Department** — Donut chart
4. **Top 10 Vendors by Spend** — Horizontal bar
5. **Spend by Category** — Category bar chart
6. **Quarterly Overview** — Grouped bar
7. **Vendor Performance Scatter** — On-time rate vs spend (bubble size = order count)
8. **P2P Cycle Time Box Plots** — Per-stage distribution
9. **Payment Cycle by Vendor** — Horizontal bar
10. **E2E Cycle Histogram** + **On-Time Rate** + **Pareto Analysis**

## Tech Stack

- **Python 3.10+** — Core language
- **Pandas / NumPy** — Data processing & KPI computation
- **Plotly** — Interactive visualisations
- **ReportLab** — PDF documentation
- **SAP Domain** — MM (Materials Management) / FI (Financial Accounting)

## SAP P2P Process Flow

```
Purchase         Purchase       Goods          Invoice        Payment
Requisition  →   Order     →   Receipt    →   Receipt    →   (FI-AP)
(PR / ME51N)    (PO / ME21N)  (GR / MIGO)   (IV / MIRO)   (F-53)
```

## License
Academic project — KIIT University, 2026.
