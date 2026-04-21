import os
import sys

def main():
    print("=" * 60)
    print("  SAP Procure-to-Pay (P2P) Data Analytics")
    print("  KIIT University | SAP Data Analytics Capstone")
    print("=" * 60)

    # Step 1: Generate data
    print("\n[1/3] Generating synthetic SAP P2P transaction data...")
    from generate_data import generate_p2p_transactions
    df = generate_p2p_transactions(500)

    # Step 2: Compute KPIs
    print("\n[2/3] Computing KPIs and analytics...")
    import analytics as ana
    df = ana.load_data()
    kpis = ana.compute_kpis(df)

    print("\n── KPI Summary ──────────────────────────────────────")
    print(f"  Total Procurement Spend   : ₹{kpis['total_spend']:>15,.0f}")
    print(f"  Total Purchase Orders     : {kpis['total_pos']:>15,}")
    print(f"  Active Vendors            : {kpis['total_vendors']:>15,}")
    print(f"  Avg PO Value              : ₹{kpis['avg_po_value']:>15,.0f}")
    print(f"  Avg E2E Cycle Time        : {kpis['avg_e2e_cycle']:>14.1f} days")
    print(f"  On-Time Delivery Rate     : {kpis['on_time_delivery_rate']:>14.1f}%")
    print(f"  Invoice Exception Rate    : {kpis['invoice_exception_rate']:>14.1f}%")

    print("\n── Cycle Time Breakdown ─────────────────────────────")
    ct = ana.cycle_time_stats(df)
    print(ct.to_string(index=False))

    print("\n── Top Vendors by Spend ─────────────────────────────")
    vend = ana.spend_by_vendor(df, top_n=5)
    for _, row in vend.iterrows():
        print(f"  {row['Vendor_Name']:<28} ₹{row['Total_Amount']:>12,.0f}")

    # Step 3: Build dashboard
    print("\n[3/3] Building interactive dashboard...")
    from dashboard import build_dashboard
    build_dashboard(df, kpis)

    print("\n" + "=" * 60)
    print("  ✓ Pipeline complete!")
    print("  → Dashboard: output/P2P_Dashboard.html")
    print("  → Data:      data/p2p_transactions.csv")
    print("=" * 60)


if __name__ == "__main__":
    main()
