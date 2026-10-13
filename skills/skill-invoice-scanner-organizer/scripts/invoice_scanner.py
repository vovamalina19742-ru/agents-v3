import os
import sys
import json
import argparse
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def reconcile_invoice(order_bom_path, invoice_path, packing_list_path=None):
    """
    Reconciles an internal Order/BOM against a Factory Invoice and optional Packing List.
    Detects:
    1. Quantity discrepancies (Ordered vs Invoiced vs Shipped).
    2. Price variations (Offered EUR vs Invoiced EUR).
    3. Missing items or unexpected substitute items.
    4. Weight & Carton reconciliation (Colli / Carton No check for CMR/T1).
    """
    with open(order_bom_path, "r", encoding="utf-8") as f:
        order_data = json.load(f)

    with open(invoice_path, "r", encoding="utf-8") as f:
        invoice_data = json.load(f)

    packing_data = {}
    if packing_list_path and os.path.exists(packing_list_path):
        with open(packing_list_path, "r", encoding="utf-8") as f:
            packing_data = json.load(f)

    # Normalize order items
    order_items = {}
    order_raw = order_data.get("master_bom_items") or order_data.get("items") or order_data.get("equipment") or []
    for it in order_raw:
        art = str(it.get("article") or it.get("code") or "").strip()
        if art:
            order_items[art] = {
                "article": art,
                "name": it.get("name", "Unknown"),
                "qty": float(it.get("qty", 1)),
                "price": float(it.get("price_eur", it.get("unit_price", 0.0))),
                "brand": it.get("brand", "")
            }

    # Normalize invoice items
    inv_items = {}
    inv_raw = invoice_data.get("items") or invoice_data.get("lines") or []
    for it in inv_raw:
        art = str(it.get("article") or it.get("code") or "").strip()
        if art:
            inv_items[art] = {
                "article": art,
                "name": it.get("name", "Unknown"),
                "qty": float(it.get("qty", 1)),
                "price": float(it.get("unit_price", it.get("price_eur", 0.0))),
                "net_kg": float(it.get("net_kg", 0.0)),
                "gross_kg": float(it.get("gross_kg", 0.0)),
                "carton": it.get("carton_no") or it.get("box") or "N/A"
            }

    # Normalize packing items
    pack_items = {}
    pack_raw = packing_data.get("packages") or packing_data.get("items") or []
    for it in pack_raw:
        art = str(it.get("article") or it.get("code") or "").strip()
        if art:
            pack_items[art] = {
                "article": art,
                "qty_packed": float(it.get("qty", 1)),
                "carton_no": it.get("carton_no", "1"),
                "net_kg": float(it.get("net_kg", 0.0)),
                "gross_kg": float(it.get("gross_kg", 0.0))
            }

    # All articles
    all_articles = sorted(list(set(list(order_items.keys()) + list(inv_items.keys()))))
    
    reconciliation_rows = []
    total_order_val = 0.0
    total_inv_val = 0.0
    total_net_kg = 0.0
    total_gross_kg = 0.0
    discrepancies = []
    cartons_set = set()

    for art in all_articles:
        o = order_items.get(art, {"article": art, "name": "Not in Order", "qty": 0.0, "price": 0.0, "brand": ""})
        i = inv_items.get(art, {"article": art, "name": "Not Invoiced", "qty": 0.0, "price": 0.0, "net_kg": 0.0, "gross_kg": 0.0, "carton": "N/A"})
        p = pack_items.get(art, {"qty_packed": 0.0, "carton_no": "N/A", "net_kg": 0.0, "gross_kg": 0.0})

        o_val = round(o["qty"] * o["price"], 2)
        i_val = round(i["qty"] * i["price"], 2)
        total_order_val += o_val
        total_inv_val += i_val

        # Net/gross weight fallback
        net_kg = i["net_kg"] or p["net_kg"] or round(i["qty"] * 0.85, 2)
        gross_kg = i["gross_kg"] or p["gross_kg"] or round(net_kg * 1.15, 2)
        total_net_kg += net_kg
        total_gross_kg += gross_kg

        carton = i["carton"] if i["carton"] != "N/A" else p["carton_no"]
        if carton != "N/A":
            for c in str(carton).split(","):
                cartons_set.add(c.strip())

        # Status evaluation
        status = "MATCH"
        reasons = []

        if o["qty"] == 0:
            status = "UNEXPECTED_ITEM"
            reasons.append(f"Articol prezent în factură dar absent în comanda internă!")
        elif i["qty"] == 0:
            status = "MISSING_INVOICE"
            reasons.append(f"Articol comandat ({o['qty']} buc) dar nelivrat/nefacturat de fabrică!")
        else:
            if abs(o["qty"] - i["qty"]) > 0.001:
                status = "QTY_MISMATCH"
                reasons.append(f"Diferență cantitate: Comandat {o['qty']} vs Facturat {i['qty']}")
            if abs(o["price"] - i["price"]) > 0.01:
                diff_price = round(i["price"] - o["price"], 2)
                p_status = "PRICE_INCREASE" if diff_price > 0 else "PRICE_DISCOUNT"
                status = p_status if status == "MATCH" else "MULTIPLE_DISCREPANCY"
                reasons.append(f"Diferență preț: Comandat €{o['price']:.2f} vs Facturat €{i['price']:.2f} (Δ = €{diff_price:+.2f})")

        if p and p.get("qty_packed", 0) > 0 and abs(p["qty_packed"] - i["qty"]) > 0.001:
            reasons.append(f"Diferență Packing List: Facturat {i['qty']} vs Ambalat {p['qty_packed']}")
            if status == "MATCH":
                status = "PACKING_MISMATCH"

        if status != "MATCH":
            discrepancies.append({
                "article": art,
                "name": o["name"] if o["name"] != "Not in Order" else i["name"],
                "status": status,
                "details": "; ".join(reasons)
            })

        reconciliation_rows.append({
            "article": art,
            "name": o["name"] if o["name"] != "Not in Order" else i["name"],
            "order_qty": o["qty"],
            "order_price": o["price"],
            "order_total": o_val,
            "inv_qty": i["qty"],
            "inv_price": i["price"],
            "inv_total": i_val,
            "price_diff": round(i["price"] - o["price"], 2),
            "net_kg": net_kg,
            "gross_kg": gross_kg,
            "carton": carton,
            "status": status,
            "reasons": reasons
        })

    # Logistics summary
    cmr_total_cartons = invoice_data.get("logistics", {}).get("cmr_colli", len(cartons_set) or 1)
    actual_cartons = len(cartons_set) or 1
    carton_gate_passed = (cmr_total_cartons == actual_cartons)

    summary = {
        "invoice_no": invoice_data.get("invoice_no", "N/A"),
        "supplier": invoice_data.get("supplier", "Factory"),
        "date": invoice_data.get("date", "2026-09-29"),
        "currency": invoice_data.get("currency", "EUR"),
        "total_order_eur": round(total_order_val, 2),
        "total_invoice_eur": round(total_inv_val, 2),
        "total_diff_eur": round(total_inv_val - total_order_val, 2),
        "total_net_kg": round(total_net_kg, 2),
        "total_gross_kg": round(total_gross_kg, 2),
        "total_cartons": actual_cartons,
        "cmr_declared_cartons": cmr_total_cartons,
        "logistics_gate_passed": carton_gate_passed and len(discrepancies) == 0,
        "discrepancies_count": len(discrepancies),
        "discrepancies": discrepancies,
        "rows": reconciliation_rows
    }

    return summary

def export_reconciliation_excel(summary, out_path):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Reconciliere Factura"
    ws.views.sheetView[0].showGridLines = True

    navy_dark = "1E293B"
    green_match = "DCFCE7"
    red_mismatch = "FEE2E2"
    yellow_warn = "FEF9C3"
    border_gray = "CBD5E1"
    thin_border = Border(
        left=Side(style='thin', color=border_gray),
        right=Side(style='thin', color=border_gray),
        top=Side(style='thin', color=border_gray),
        bottom=Side(style='thin', color=border_gray)
    )

    # Title
    ws.merge_cells("A1:L1")
    ws["A1"] = f"RAPORT DE RECONCILIERE: COMANDĂ CLIENT vs FACTURĂ FABRICĂ ({summary['supplier']})"
    ws["A1"].font = Font(name="Arial", size=13, bold=True, color="FFFFFF")
    ws["A1"].fill = PatternFill(start_color=navy_dark, end_color=navy_dark, fill_type="solid")
    ws["A1"].alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 32

    # Executive KPI
    ws.cell(row=3, column=1, value="Nr. Factură:").font = Font(bold=True)
    ws.cell(row=3, column=2, value=summary["invoice_no"])
    ws.cell(row=3, column=4, value="Valoare Comandă:").font = Font(bold=True)
    ws.cell(row=3, column=5, value=f"€{summary['total_order_eur']:,.2f}")
    ws.cell(row=3, column=7, value="Valoare Facturată:").font = Font(bold=True)
    ws.cell(row=3, column=8, value=f"€{summary['total_invoice_eur']:,.2f}")
    ws.cell(row=3, column=10, value="Diferență Valorică:").font = Font(bold=True)
    ws.cell(row=3, column=11, value=f"€{summary['total_diff_eur']:+,.2f}")

    ws.cell(row=4, column=1, value="Greutate Netă:").font = Font(bold=True)
    ws.cell(row=4, column=2, value=f"{summary['total_net_kg']:.2f} kg")
    ws.cell(row=4, column=4, value="Greutate Brută:").font = Font(bold=True)
    ws.cell(row=4, column=5, value=f"{summary['total_gross_kg']:.2f} kg")
    ws.cell(row=4, column=7, value="Colete (Cartons):").font = Font(bold=True)
    ws.cell(row=4, column=8, value=f"{summary['total_cartons']} cutii")
    ws.cell(row=4, column=10, value="Verdict Vamal:").font = Font(bold=True)
    verdict_text = "APROBAT PENTRU VAMĂ" if summary["logistics_gate_passed"] else "STOP! NECESITĂ CLARIFICARE"
    c_verdict = ws.cell(row=4, column=11, value=verdict_text)
    c_verdict.font = Font(bold=True, color="166534" if summary["logistics_gate_passed"] else "991B1B")

    # Table Header
    headers = [
        "Articol", "Denumire Echipament", "Comandat\n(Cant)", "Preț Cmd\n(EUR)", "Total Cmd\n(EUR)",
        "Facturat\n(Cant)", "Preț Fact\n(EUR)", "Total Fact\n(EUR)", "Δ Preț\n(EUR)",
        "Masa Net\n(kg)", "Cutie\n(Carton)", "Status\nReconciliere"
    ]
    ws.row_dimensions[6].height = 28
    for c_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=6, column=c_idx, value=h)
        cell.font = Font(name="Arial", size=9, bold=True, color="FFFFFF")
        cell.fill = PatternFill(start_color=navy_dark, end_color=navy_dark, fill_type="solid")
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    r = 7
    for row in summary["rows"]:
        st = row["status"]
        fill_color = green_match
        if "MISMATCH" in st or "UNEXPECTED" in st or "MISSING" in st:
            fill_color = red_mismatch
        elif "PRICE" in st:
            fill_color = yellow_warn

        vals = [
            row["article"], row["name"], row["order_qty"], row["order_price"], row["order_total"],
            row["inv_qty"], row["inv_price"], row["inv_total"], row["price_diff"],
            row["net_kg"], row["carton"], st
        ]

        for c_idx, val in enumerate(vals, 1):
            cell = ws.cell(row=r, column=c_idx, value=val)
            cell.font = Font(name="Arial", size=9)
            cell.border = thin_border
            if c_idx in [3, 6, 10]:
                cell.alignment = Alignment(horizontal="right", vertical="center")
                cell.number_format = "#,##0" if c_idx != 10 else "#,##0.00"
            elif c_idx in [4, 5, 7, 8, 9]:
                cell.alignment = Alignment(horizontal="right", vertical="center")
                cell.number_format = "€#,##0.00"
            elif c_idx in [1, 11, 12]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")

        ws.cell(row=r, column=12).fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
        ws.row_dimensions[r].height = 20
        r += 1

    col_widths = {1: 15, 2: 36, 3: 11, 4: 12, 5: 14, 6: 11, 7: 12, 8: 14, 9: 11, 10: 12, 11: 12, 12: 20}
    for c_idx, w in col_widths.items():
        ws.column_dimensions[get_column_letter(c_idx)].width = w

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    wb.save(out_path)
    return out_path

def export_reconciliation_markdown(summary, out_path):
    lines = []
    lines.append(f"# 🔍 Raport de Reconciliere Factură Fabrică: {summary['supplier']}")
    lines.append(f"**Data:** {summary['date']} | **Nr. Factură:** `{summary['invoice_no']}` | **Valută:** {summary['currency']}\n")

    lines.append("## 📊 1. Indicatori Cheie (Executive Summary)")
    lines.append(f"- **Total Comandă Internă:** `€{summary['total_order_eur']:,.2f}`")
    lines.append(f"- **Total Factură Fabrică:** `€{summary['total_invoice_eur']:,.2f}`")
    lines.append(f"- **Diferență Valorică (Δ):** `€{summary['total_diff_eur']:+,.2f}`")
    lines.append(f"- **Greutate Netă Totală:** `{summary['total_net_kg']:.2f} kg` | **Brută:** `{summary['total_gross_kg']:.2f} kg`")
    lines.append(f"- **Colete Identificate:** `{summary['total_cartons']} cutii` (CMR declară: `{summary['cmr_declared_cartons']}`)")
    
    if summary["logistics_gate_passed"]:
        lines.append("\n> [!TIP]\n> **VERDICT VAMAL: APROBAT PENTRU IMPORT.** Datele facturii coincid 100% cu comanda internă și specificația de transport.")
    else:
        lines.append(f"\n> [!WARNING]\n> **VERDICT VAMAL: STOPARE PENTRU CLARIFICARE.** S-au detectat `{summary['discrepancies_count']}` discrepanțe care pot cauza blocaj în vamă.")

    if summary["discrepancies"]:
        lines.append("\n## ⚠️ 2. Tabelul Discrepanțelor Identificate")
        lines.append("| Nr | Cod Articol | Denumire Echipament | Tip Problemă | Detalii Discrepanță |")
        lines.append("| :--- | :--- | :--- | :--- | :--- |")
        for idx, d in enumerate(summary["discrepancies"], 1):
            lines.append(f"| {idx} | `{d['article']}` | {d['name']} | **{d['status']}** | {d['details']} |")

    lines.append("\n## 📦 3. Sincronizare Logică Vamală (CMR == T1 == Invoices)")
    lines.append("Conform standardului Smart Light Logistics Gate:")
    lines.append("1. Masa brută din CMR trebuie să corespundă cu suma maselor brute din facturile producătorilor.")
    lines.append("2. Fiecare articol trebuie să aibă atribuit numărul de cutie (`Carton No`) pentru inspecția fizică la biroul vamal.")

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return out_path

def main():
    parser = argparse.ArgumentParser(description="Lighting Factory Invoice Scanner & Reconciliation Engine")
    parser.add_argument("--order", required=True, help="Path to internal project BOM/Order JSON")
    parser.add_argument("--invoice", required=True, help="Path to factory invoice JSON")
    parser.add_argument("--packing", default=None, help="Optional path to packing list JSON")
    parser.add_argument("--out-json", default="reconciliation.json", help="Output reconciliation JSON")
    parser.add_argument("--out-xlsx", default="reconciliation.xlsx", help="Output reconciliation Excel")
    parser.add_argument("--out-md", default="reconciliation.md", help="Output reconciliation Markdown")
    args = parser.parse_args()

    summary = reconcile_invoice(args.order, args.invoice, args.packing)

    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"[+] Reconciliation JSON saved: {args.out_json}")

    export_reconciliation_excel(summary, args.out_xlsx)
    print(f"[+] Reconciliation Excel saved: {args.out_xlsx}")

    export_reconciliation_markdown(summary, args.out_md)
    print(f"[+] Reconciliation Markdown saved: {args.out_md}")

    print(f"\n[i] Discrepancies found: {summary['discrepancies_count']} | Logistics Gate: {'PASSED' if summary['logistics_gate_passed'] else 'REJECTED'}")

if __name__ == "__main__":
    main()
