"""
exporter.py — Модуль экспорта сметы освещения в форматы Excel (XLSX) с живыми формулами
и чистовой оферты (PDF) в фирменном стиле Smart Light.
"""

import os
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

import pymupdf

def export_to_excel(project_data, bom_items, output_filepath, client_name="Andreea", quote_meta=None):
    """
    Создает файл Excel с формулами (=I*J, =SUM, =TVA 20%, скидка) и таблицей электротехники.
    """
    wb = openpyxl.Workbook()
    
    # ------------------ ЛИСТ 1: Смета оборудования ------------------
    ws = wb.active
    ws.title = "Смета оборудования"
    ws.views.sheetView[0].showGridLines = True

    # Цветовая палитра Smart Light
    header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid") # Dark Slate
    subtotal_fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid") # Light Slate
    accent_fill = PatternFill(start_color="EA580C", end_color="EA580C", fill_type="solid")   # Smart Light Orange
    zebra_fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")

    font_title = Font(name="Arial", size=14, bold=True, color="1E293B")
    font_sub = Font(name="Arial", size=10, italic=True, color="64748B")
    font_header = Font(name="Arial", size=10, bold=True, color="FFFFFF")
    font_data = Font(name="Arial", size=10, color="0F172A")
    font_bold = Font(name="Arial", size=10, bold=True, color="0F172A")
    font_total = Font(name="Arial", size=11, bold=True, color="EA580C")

    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    # Шапка документа
    passport = project_data.get("passport", {})
    obj_name = passport.get("name", "Apartament Chisinau")
    date_str = quote_meta.get("date", "29.09.2026") if quote_meta else "29.09.2026"
    
    ws["A1"] = "SMART LIGHT — СПЕЦИФИКАЦИЯ ОСВЕЩЕНИЯ И ОБОРУДОВАНИЯ"
    ws["A1"].font = font_title
    ws["A2"] = f"Объект: {obj_name} · Клиент: {client_name} · Дата: {date_str} · Менеджер: Andrei Mahotchin (+373 62 180001)"
    ws["A2"].font = font_sub

    headers = [
        "№", "Артикул", "Наименование оборудования", "Бренд", 
        "Цвет", "CCT, K", "IP", "Ед. изм.", "Кол-во", "Цена EUR", "Сумма EUR"
    ]
    
    start_row = 4
    for col_num, h_text in enumerate(headers, 1):
        cell = ws.cell(row=start_row, column=col_num, value=h_text)
        cell.font = font_header
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border
    ws.row_dimensions[start_row].height = 28

    current_row = start_row + 1
    item_start_row = current_row

    for idx, it in enumerate(bom_items, 1):
        ws.cell(row=current_row, column=1, value=idx).alignment = Alignment(horizontal="center")
        ws.cell(row=current_row, column=2, value=it.get("article", "—")).alignment = Alignment(horizontal="center")
        ws.cell(row=current_row, column=3, value=it.get("name", "")).alignment = Alignment(horizontal="left")
        ws.cell(row=current_row, column=4, value=it.get("brand", "Smart Light")).alignment = Alignment(horizontal="center")
        ws.cell(row=current_row, column=5, value=it.get("color", "black")).alignment = Alignment(horizontal="center")
        ws.cell(row=current_row, column=6, value=it.get("cct", "3000")).alignment = Alignment(horizontal="center")
        ws.cell(row=current_row, column=7, value=it.get("ip", "IP20")).alignment = Alignment(horizontal="center")
        ws.cell(row=current_row, column=8, value=it.get("unit", "шт.")).alignment = Alignment(horizontal="center")
        
        # Количество (число)
        qty_cell = ws.cell(row=current_row, column=9, value=float(it.get("qty", 1)))
        qty_cell.alignment = Alignment(horizontal="right")
        qty_cell.number_format = "#,##0.0" if isinstance(it.get("qty"), float) and it.get("qty") % 1 != 0 else "#,##0"

        # Цена за единицу EUR
        price_val = float(it.get("price_eur", 0.0))
        price_cell = ws.cell(row=current_row, column=10, value=price_val)
        price_cell.alignment = Alignment(horizontal="right")
        price_cell.number_format = '#,##0.00 €'

        # Живая формула Excel: Сумма = Кол-во * Цена
        sum_cell = ws.cell(row=current_row, column=11, value=f"=I{current_row}*J{current_row}")
        sum_cell.alignment = Alignment(horizontal="right")
        sum_cell.number_format = '#,##0.00 €'
        sum_cell.font = font_bold

        # Стилизация строки
        row_fill = zebra_fill if idx % 2 == 0 else None
        for col_idx in range(1, 12):
            c = ws.cell(row=current_row, column=col_idx)
            c.font = font_data if col_idx != 11 else font_bold
            if row_fill:
                c.fill = row_fill
            c.border = thin_border

        ws.row_dimensions[current_row].height = 20
        current_row += 1

    item_end_row = current_row - 1

    # Блок итогов с формулами Excel
    ws.cell(row=current_row, column=10, value="ИТОГО БЕЗ НДС:").font = font_bold
    ws.cell(row=current_row, column=10).alignment = Alignment(horizontal="right")
    subtotal_cell = ws.cell(row=current_row, column=11, value=f"=SUM(K{item_start_row}:K{item_end_row})")
    subtotal_cell.font = font_bold
    subtotal_cell.number_format = '#,##0.00 €'
    subtotal_cell.border = thin_border
    current_row += 1

    ws.cell(row=current_row, column=10, value="НДС (TVA 20.00%):").font = font_bold
    ws.cell(row=current_row, column=10).alignment = Alignment(horizontal="right")
    tva_cell = ws.cell(row=current_row, column=11, value=f"=K{current_row-1}*0.20")
    tva_cell.font = font_bold
    tva_cell.number_format = '#,##0.00 €'
    tva_cell.border = thin_border
    current_row += 1

    ws.cell(row=current_row, column=10, value="ИТОГО С НДС (TVA):").font = font_bold
    ws.cell(row=current_row, column=10).alignment = Alignment(horizontal="right")
    total_tva_cell = ws.cell(row=current_row, column=11, value=f"=K{current_row-2}+K{current_row-1}")
    total_tva_cell.font = font_bold
    total_tva_cell.number_format = '#,##0.00 €'
    total_tva_cell.fill = subtotal_fill
    total_tva_cell.border = thin_border
    current_row += 1

    ws.cell(row=current_row, column=10, value="СКИДКА КЛИЕНТУ (10%):").font = font_bold
    ws.cell(row=current_row, column=10).alignment = Alignment(horizontal="right")
    discount_cell = ws.cell(row=current_row, column=11, value=f"=K{current_row-1}*0.10")
    discount_cell.font = font_bold
    discount_cell.number_format = '#,##0.00 €'
    discount_cell.border = thin_border
    current_row += 1

    ws.cell(row=current_row, column=10, value="ИТОГО СО СКИДКОЙ 10%:").font = font_total
    ws.cell(row=current_row, column=10).alignment = Alignment(horizontal="right")
    final_cell = ws.cell(row=current_row, column=11, value=f"=K{current_row-2}-K{current_row-1}")
    final_cell.font = font_total
    final_cell.number_format = '#,##0.00 €'
    final_cell.fill = PatternFill(start_color="FEF3C7", end_color="FEF3C7", fill_type="solid")
    final_cell.border = thin_border
    current_row += 2

    # Условия
    ws.cell(row=current_row, column=1, value="Условия: Цены в EUR, НДС 20% включён. Срок действия предложения: 14 дней. Поставка: 20 дней. Гарантия: 3 года.").font = font_sub

    # Авто-ширина колонок
    col_widths = {1: 6, 2: 18, 3: 45, 4: 16, 5: 12, 6: 10, 7: 8, 8: 10, 9: 10, 10: 14, 11: 16}
    for c_idx, w in col_widths.items():
        ws.column_dimensions[get_column_letter(c_idx)].width = w

    # Сохранение
    os.makedirs(os.path.dirname(os.path.abspath(output_filepath)), exist_ok=True)
    wb.save(output_filepath)
    return output_filepath


def export_to_pdf(project_data, bom_items, output_filepath, client_name="Andreea", quote_meta=None):
    """
    Генерирует чистовой PDF-документ коммерческого предложения Smart Light через PyMuPDF.
    """
    doc = pymupdf.open()
    
    font_path = "C:/Windows/Fonts/arial.ttf" if os.path.exists("C:/Windows/Fonts/arial.ttf") else None
    
    # Геометрия листа A4 (595.3 x 841.9 pt)
    page_w, page_h = 595.3, 841.9
    margin = 30.0
    usable_w = page_w - (2 * margin)

    page = doc.new_page(width=page_w, height=page_h)
    
    # 1. Шапка бренда Smart Light
    # Оранжевый акцентный лого-блок
    page.draw_rect(pymupdf.Rect(margin, 25, margin + 110, 48), color=(0.92, 0.35, 0.05), fill=(0.92, 0.35, 0.05))
    page.insert_text(pymupdf.Point(margin + 8, 41), "smart | light", fontsize=14, color=(1, 1, 1), fontfile=font_path)
    page.insert_text(pymupdf.Point(margin + 8, 46), "lighting solutions", fontsize=6, color=(1, 1, 1), fontfile=font_path)

    # Контакты менеджера
    mgr_text = "ANDREI MAHOTCHIN\nPROJECT LIGHTING MANAGER\n+373 62 180001 | sales@smartlight.md\nChisinau | Pajurii 11"
    page.insert_text(pymupdf.Point(page_w - margin - 170, 32), mgr_text, fontsize=8, color=(0.2, 0.2, 0.2), fontfile=font_path)

    # Разделитель
    page.draw_line(pymupdf.Point(margin, 58), pymupdf.Point(page_w - margin, 58), color=(0.8, 0.8, 0.8), width=0.8)

    # Название документа и метаданные
    date_str = quote_meta.get("date", "29.09.2026") if quote_meta else "29.09.2026"
    doc_header = f"Anexa la Contractul nr. ___ din data: {date_str}"
    page.insert_text(pymupdf.Point(margin, 75), doc_header, fontsize=11, color=(0.1, 0.15, 0.25), fontfile=font_path)
    
    client_box = f"Client: {client_name}   |   Obiect: {project_data.get('passport', {}).get('name', 'Apartament Chisinau')}"
    page.insert_text(pymupdf.Point(margin, 88), client_box, fontsize=9, color=(0.4, 0.4, 0.4), fontfile=font_path)

    # 2. Таблица
    col_x = [
        margin,                  # 0: №
        margin + 20,             # 1: Артикул (65)
        margin + 85,             # 2: Наименование (215)
        margin + 300,            # 3: CCT (35)
        margin + 335,            # 4: IP (30)
        margin + 365,            # 5: Ед. (30)
        margin + 395,            # 6: Кол-во (35)
        margin + 430,            # 7: Цена EUR (50)
        page_w - margin          # 8: Сумма EUR (55)
    ]

    header_y = 100
    row_h = 16
    page.draw_rect(pymupdf.Rect(margin, header_y, page_w - margin, header_y + row_h), color=(0.92, 0.35, 0.05), fill=(0.92, 0.35, 0.05))

    th = ["№", "Articol", "Denumire echipament / Model", "CCT", "IP", "Unit", "Q-ty", "Pret €", "Total €"]
    for i in range(len(th)):
        page.insert_text(pymupdf.Point(col_x[i] + 2, header_y + 11), th[i], fontsize=7.5, color=(1, 1, 1), fontfile=font_path)

    y = header_y + row_h
    total_eur = 0.0

    for idx, it in enumerate(bom_items, 1):
        if y > page_h - 75:  # Переход на новую страницу
            page = doc.new_page(width=page_w, height=page_h)
            y = 40
            # Рисуем заголовок на новой странице
            page.draw_rect(pymupdf.Rect(margin, y, page_w - margin, y + row_h), color=(0.92, 0.35, 0.05), fill=(0.92, 0.35, 0.05))
            for i in range(len(th)):
                page.insert_text(pymupdf.Point(col_x[i] + 2, y + 11), th[i], fontsize=7.5, color=(1, 1, 1), fontfile=font_path)
            y += row_h

        # Чередование фона
        if idx % 2 == 0:
            page.draw_rect(pymupdf.Rect(margin, y, page_w - margin, y + row_h), color=(0.96, 0.97, 0.98), fill=(0.96, 0.97, 0.98))

        qty = float(it.get("qty", 1))
        price = float(it.get("price_eur", 0.0))
        sum_val = round(qty * price, 2)
        total_eur += sum_val

        # Печать ячеек
        page.insert_text(pymupdf.Point(col_x[0] + 2, y + 11), str(idx), fontsize=7, color=(0.2, 0.2, 0.2), fontfile=font_path)
        
        art_short = str(it.get("article", "—"))[:14]
        page.insert_text(pymupdf.Point(col_x[1] + 2, y + 11), art_short, fontsize=7, color=(0.2, 0.2, 0.2), fontfile=font_path)
        
        name_short = str(it.get("name", ""))[:48]
        page.insert_text(pymupdf.Point(col_x[2] + 2, y + 11), name_short, fontsize=7, color=(0.1, 0.1, 0.1), fontfile=font_path)
        
        page.insert_text(pymupdf.Point(col_x[3] + 2, y + 11), str(it.get("cct", "3000")), fontsize=7, color=(0.3, 0.3, 0.3), fontfile=font_path)
        page.insert_text(pymupdf.Point(col_x[4] + 2, y + 11), str(it.get("ip", "IP20")), fontsize=7, color=(0.3, 0.3, 0.3), fontfile=font_path)
        page.insert_text(pymupdf.Point(col_x[5] + 2, y + 11), str(it.get("unit", "шт.")), fontsize=6.5, color=(0.3, 0.3, 0.3), fontfile=font_path)
        
        qty_str = f"{qty:.1f}" if qty % 1 != 0 else f"{int(qty)}"
        page.insert_text(pymupdf.Point(col_x[6] + 4, y + 11), qty_str, fontsize=7, color=(0.1, 0.1, 0.1), fontfile=font_path)
        page.insert_text(pymupdf.Point(col_x[7] + 2, y + 11), f"{price:.2f} €", fontsize=7, color=(0.2, 0.2, 0.2), fontfile=font_path)
        page.insert_text(pymupdf.Point(col_x[8] - 50, y + 11), f"{sum_val:.2f} €", fontsize=7, color=(0.1, 0.1, 0.1), fontfile=font_path)

        # Тонкая разделительная черта
        page.draw_line(pymupdf.Point(margin, y + row_h), pymupdf.Point(page_w - margin, y + row_h), color=(0.9, 0.9, 0.9), width=0.4)
        y += row_h

    # 3. Блок сумм и скидки
    y += 8
    page.draw_rect(pymupdf.Rect(page_w - margin - 220, y, page_w - margin, y + 48), color=(0.95, 0.95, 0.95), fill=(0.95, 0.95, 0.95))
    
    total_discount = total_eur * 0.90
    page.insert_text(pymupdf.Point(page_w - margin - 210, y + 16), f"TOTAL PRICE (with TVA):", fontsize=9, color=(0.2, 0.2, 0.2), fontfile=font_path)
    page.insert_text(pymupdf.Point(page_w - margin - 75, y + 16), f"{total_eur:,.2f} €", fontsize=9, color=(0.1, 0.1, 0.1), fontfile=font_path)

    page.insert_text(pymupdf.Point(page_w - margin - 210, y + 36), f"TOTAL (TVA & discount 10%):", fontsize=9, color=(0.92, 0.35, 0.05), fontfile=font_path)
    page.insert_text(pymupdf.Point(page_w - margin - 75, y + 36), f"{total_discount:,.2f} €", fontsize=10, color=(0.92, 0.35, 0.05), fontfile=font_path)

    # 4. Юридический футер
    footer_text = "Prețuri în EUR, TVA 20.00% inclus. Oferta este valabilă timp de 14 zile. Livrare: 20 zile. Garanție: 3 ani.\nЦены в EUR, НДС 20% включён. Срок действия предложения: 14 дней. Поставка: 20 дней. Гарантия: 3 года."
    page.insert_text(pymupdf.Point(margin, page_h - 35), footer_text, fontsize=6.5, color=(0.5, 0.5, 0.5), fontfile=font_path)

    os.makedirs(os.path.dirname(os.path.abspath(output_filepath)), exist_ok=True)
    doc.save(output_filepath)
    doc.close()
    return output_filepath
