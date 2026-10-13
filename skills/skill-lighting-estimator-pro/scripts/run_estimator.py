"""
run_estimator.py — Инженерный комплекс детерминированного расчета освещения (Lighting Estimator PRO v3).
Реализует 5 улучшений:
1. Поддержка реальных брендов (KRAAB Systems, Neko Moduline, KLUS, Smart Light Insight, Trimless-триада).
2. Реалистичный электротехнический расчет падения напряжения ΔU (кабель от щита cable_to_driver_m + лента).
3. Разделение фотометрии EN 12464-1: прямой свет (eta=0.70) и скрытый свет в нишах/карнизах (eta=0.30).
4. Экспорт сметы в Excel (.xlsx с живыми формулами =I*J, =SUM, НДС 20%, скидка) и чистовой PDF Smart Light.
5. Защитные инженерные гейты (паспорт, плотность спотов, IP-влагозащита санузлов, CRI >= 90).
"""

import sys
import os
import math
import json
import argparse

# Настройка среды исполнения
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from brand_catalog import BRANDS_CATALOG, resolve_track_accessories
from photometric_engine import PhotometricEngine
from exporter import export_to_excel, export_to_pdf
from html_dashboard import generate_interactive_html_dashboard
from logistics_matrix import check_preflight_blockers, audit_logistics_cargo, generate_client_objection_defense


def optimize_track_cut(L):
    """
    Детерминированный поиск минимума закупки хлыстов 2 м и 3 м (argmin).
    Минимизирует:
      1. Избыточный закупленный метраж (waste = total_m - L >= 0).
      2. При равном метраже — число стыков.
    """
    L = float(L)
    if L <= 0:
        return {"bars_2m": 0, "bars_3m": 0, "purchased_m": 0.0, "waste_m": 0.0, "joints": 0}

    best = None
    max_bars = int(math.ceil(L / 2.0)) + 3

    for b3 in range(max_bars + 1):
        for b2 in range(max_bars + 1):
            total_m = (b2 * 2.0) + (b3 * 3.0)
            if total_m >= L - 1e-6 and total_m > 0:
                waste = round(total_m - L, 4)
                bars = b2 + b3
                joints = max(0, bars - 1)
                score = (waste, joints, bars)
                if best is None or score < best["score"]:
                    best = {
                        "bars_2m": b2,
                        "bars_3m": b3,
                        "purchased_m": round(total_m, 2),
                        "waste_m": round(waste, 2),
                        "joints": joints,
                        "score": score
                    }
    return best


def calculate_track_bom(tracks, spots_default_w=15.0, brand_key="smart_light_insight"):
    """
    Расчет трековой системы 48V с правилом 2 заглушек на линию (total_lines * 2),
    проверкой L-углов, гибких коннекторов и адаптивной плотности спотов.
    """
    profiles_2m = 0
    profiles_3m = 0
    power_feeds = 0
    end_caps = 0
    straight_joints = 0
    corners_90 = 0
    total_spots = 0
    track_details = []

    total_lines = len(tracks)
    # ЗОЛОТОЕ ПРАВИЛО: У каждой независимой линии 2 торца!
    end_caps = total_lines * 2
    power_feeds = total_lines

    for t in tracks:
        L = float(t.get("length_m", t.get("length", 0)))
        has_corner = t.get("has_corner_90", False) or t.get("corner_l", False)
        corners = 1 if has_corner else int(t.get("corners_count", 0))
        corners_90 += corners

        opt = optimize_track_cut(L)
        b2 = opt["bars_2m"]
        b3 = opt["bars_3m"]
        purchased_m = opt["purchased_m"]
        waste_m = opt["waste_m"]

        profiles_2m += b2
        profiles_3m += b3

        # Стыки на линии
        line_bars = b2 + b3
        line_joints = max(0, line_bars - 1 - corners)
        straight_joints += line_joints

        # Подсчет спотов: если не задано или занижено на длинной трассе (>3м), рекомендуем плотность ~0.85 шт/м
        user_spots = t.get("spots_count", t.get("spots"))
        if user_spots is not None:
            spots = int(user_spots)
        else:
            spots = 4 if L <= 3.0 else int(round(L / 0.9))
        
        total_spots += spots
        density = spots / L if L > 0 else 0

        track_details.append({
            "name": t.get("name", "Трек"),
            "length_m": L,
            "bars_2m": b2,
            "bars_3m": b3,
            "purchased_m": purchased_m,
            "waste_m": waste_m,
            "joints": line_joints,
            "corners_90": corners,
            "spots_count": spots,
            "density_spots_per_m": round(density, 2)
        })

    total_spots_load_w = total_spots * spots_default_w
    driver_48v_min_w = total_spots_load_w * 1.35

    # Подбор модульных блоков питания 48V (75W, 100W, 150W, 200W)
    drivers_48v_plan = []
    if driver_48v_min_w > 0:
        rem_w = driver_48v_min_w
        if rem_w <= 75:
            drivers_48v_plan.append({"rating_w": 75, "qty": 1, "article": "89075X"})
        elif rem_w <= 100:
            drivers_48v_plan.append({"rating_w": 100, "qty": 1, "article": "89100X"})
        elif rem_w <= 150:
            drivers_48v_plan.append({"rating_w": 150, "qty": 1, "article": "89150X"})
        elif rem_w <= 200:
            drivers_48v_plan.append({"rating_w": 200, "qty": 1, "article": "89200X"})
        elif rem_w <= 300:
            drivers_48v_plan.append({"rating_w": 150, "qty": 2, "article": "89150X"})
        else:
            n200 = int(math.ceil(rem_w / 200.0))
            drivers_48v_plan.append({"rating_w": 200, "qty": n200, "article": "89200X"})

    accessories = resolve_track_accessories(brand_key, total_lines, corners_90, profiles_2m, profiles_3m)

    return {
        "bars_2m_total": profiles_2m,
        "bars_3m_total": profiles_3m,
        "total_purchased_m": round((profiles_2m * 2.0) + (profiles_3m * 3.0), 2),
        "power_feeds": power_feeds,
        "end_caps": end_caps,
        "straight_joints": straight_joints,
        "corners_90": corners_90,
        "flexible_feeds": corners_90,
        "total_spots": total_spots,
        "total_spots_load_w": round(total_spots_load_w, 1),
        "driver_48v_min_w": round(driver_48v_min_w, 1),
        "drivers_48v_plan": drivers_48v_plan,
        "accessories": accessories,
        "details": track_details
    }


def calculate_led_bom(rooms_led, default_wire_sqmm=1.5, profile_factor=1.05):
    """
    Реалистичный электротехнический расчет LED-ленты 24V:
    - Длина питающей кабельной трассы от электрощита/ниши: cable_to_driver_m (м).
    - Выбор сечения кабеля: cable_sqmm (0.75, 1.0, 1.5, 2.5 мм2).
    - Полное падение напряжения: dU_total = dU_кабель + dU_лента.
    - Ограничение: dU <= 3.0%. При превышении — расчет рекомендованного сечения и параллельных вводов.
    """
    rho = 0.0175  # удельное сопротивление меди, Ом*мм2/м
    U = 24.0
    results = []
    total_net_m = 0.0
    total_reels = 0
    total_slim_m = 0.0
    total_recessed_m = 0.0
    total_kraab_m = 0.0
    standard_drivers = [50, 60, 75, 100, 150, 200, 240, 250, 320]

    for r in rooms_led:
        L = float(r.get("length_m", r.get("length", 0)))
        w_m = float(r.get("power_w_per_m", 9.6))
        p_load = L * w_m
        reels = math.ceil(L / 5.0)
        total_reels += reels
        total_net_m += L

        # Кабельная трасса от электрощита до начала подсветки
        cable_m = float(r.get("cable_to_driver_m", r.get("cable_length_m", 0.0)))
        wire_sqmm = float(r.get("cable_sqmm", r.get("wire_sqmm", default_wire_sqmm)))
        
        # Ток в цепи
        i_load = p_load / U if U > 0 else 0.0

        # Падение напряжения в кабеле от щита до ленты (туда и обратно, 2L)
        delta_u_cable_v = (2.0 * cable_m * i_load * rho) / max(wire_sqmm, 0.5)

        # Падение напряжения на самой ленте (распределенная нагрузка, эквивалент 2-унцевой меди ~0.5 мм2)
        tape_cu_sqmm = 0.50
        delta_u_tape_v = (L * p_load * rho) / (U * tape_cu_sqmm)

        total_delta_u_v = delta_u_cable_v + delta_u_tape_v
        delta_u_pct = (total_delta_u_v / U) * 100.0
        delta_u_ok = delta_u_pct <= 3.0

        # Расчет числа вводов питания или рекомендованного сечения
        needed_feeds = 1
        rec_sqmm = wire_sqmm
        if not delta_u_ok:
            needed_feeds = max(2, int(math.ceil(math.sqrt(delta_u_pct / 3.0))))
            # Рекомендованное сечение для кабеля от щита
            rec_sqmm = round((2.0 * cable_m * i_load * rho) / (U * 0.015), 2)
            rec_sqmm = 2.5 if rec_sqmm > 1.5 else (1.5 if rec_sqmm > 1.0 else 1.0)

        # Классификация монтажа и профиля
        mount = r.get("mount", "slim").lower()
        if "kraab" in mount or "kraab" in r.get("room", "").lower():
            mount_type = "kraab_gipps"
            total_kraab_m += L
            profile_needed = True
        elif mount == "recessed" or "barisol" in r.get("room", "").lower():
            mount_type = "recessed_barisol"
            total_recessed_m += L
            profile_needed = False
        else:
            mount_type = "slim"
            total_slim_m += L
            profile_needed = True

        p_driver_min = p_load * 1.35
        driver_w = next((d for d in standard_drivers if d >= p_driver_min), math.ceil(p_driver_min / 50) * 50)

        ip = r.get("ip_rating", r.get("ip", "IP20")).upper()

        results.append({
            "room": r.get("room", r.get("name", "Зона")),
            "length_m": L,
            "ip": ip,
            "mount": mount_type,
            "profile_needed": profile_needed,
            "reels_5m": reels,
            "load_w": round(p_load, 1),
            "cable_to_driver_m": cable_m,
            "wire_sqmm": wire_sqmm,
            "driver_24v_w": driver_w,
            "delta_u_cable_v": round(delta_u_cable_v, 2),
            "delta_u_tape_v": round(delta_u_tape_v, 2),
            "delta_u_pct": round(delta_u_pct, 2),
            "delta_u_ok": delta_u_ok,
            "needed_feeds": needed_feeds,
            "recommended_cable_sqmm": rec_sqmm
        })

    slim_purchased_m = round(total_slim_m * profile_factor, 2)
    slim_sticks_2m = int(math.ceil(slim_purchased_m / 2.0))

    kraab_purchased_m = round(total_kraab_m * profile_factor, 2)
    kraab_sticks_2m = int(math.ceil(kraab_purchased_m / 2.0))

    barisol_sticks_2m = int(math.ceil((total_recessed_m * profile_factor) / 2.0))

    return {
        "total_net_m": round(total_net_m, 2),
        "total_reels_5m": total_reels,
        "total_purchased_reels_m": total_reels * 5.0,
        "total_linear_purchased_m": round(total_net_m * profile_factor, 2),
        "total_slim_profile_m": slim_purchased_m,
        "slim_sticks_2m": slim_sticks_2m,
        "total_kraab_profile_m": kraab_purchased_m,
        "kraab_sticks_2m": kraab_sticks_2m,
        "total_recessed_barisol_m": round(total_recessed_m, 2),
        "barisol_sticks_2m": barisol_sticks_2m,
        "details": results
    }


def run_pipeline(project_data):
    flags = []

    # 0. Pre-Flight Safety Gate (Стоп-факторы до начала расчёта)
    preflight = check_preflight_blockers(project_data)
    for blk in preflight.get("blockers", []):
        flags.insert(0, f"🛑 БЛОКЕР PRE-FLIGHT: {blk}")
    for wrn in preflight.get("warnings", []):
        flags.append(f"⚠️ ПРЕДУПРЕЖДЕНИЕ PRE-FLIGHT: {wrn}")

    # 1. Паспорт объекта
    passport = project_data.get("passport", {})
    if passport:
        declared_area = float(passport.get("area_sqm", 0))
        rooms = project_data.get("rooms", [])
        if rooms and declared_area > 0:
            calc_area = sum(float(rm.get("area_sqm", rm.get("area", 0))) for rm in rooms)
            if abs(calc_area - declared_area) > 0.1:
                flags.append(f"Паспорт объекта: сумма площадей помещений ({calc_area:.2f} м²) расходится с заявленной ({declared_area:.2f} м²).")

    # 1. Плотность спотов трека (< 0.60 шт/м)
    tracks = project_data.get("tracks", project_data.get("track", {}).get("lines", []))
    for t in tracks:
        L = float(t.get("length_m", t.get("length", 0)))
        spots = int(t.get("spots_count", t.get("spots", 0)))
        if L > 0 and spots > 0:
            density = spots / L
            if density < 0.60:
                rec_spots = int(round(L / 0.85))
                flags.append(f"Плотность спотов: линия '{t.get('name')}' ({L}м) имеет всего {spots} спота ({density:.2f} шт/м < 0.60). Рекомендуется {rec_spots} спотов для равномерного света.")

    # 2. Мокрые зоны и IP-гейт
    wet_keywords = ["baie", "spalatorie", "ванн", "санузел", "постирочн", "wc", "bath", "laundry"]
    led_zones = project_data.get("rooms_led", project_data.get("led_zones", []))
    for r in led_zones:
        r_name = r.get("room", r.get("name", "")).lower()
        is_wet = r.get("is_wet", False) or any(k in r_name for k in wet_keywords)
        ip = r.get("ip_rating", r.get("ip", "IP20")).upper()
        if is_wet:
            if ip in ["IP20", "IP33", ""]:
                flags.append(f"Влажная зона '{r.get('room', r.get('name'))}' заявлена как {ip} — ОБЯЗАТЕЛЬНО заменить ленту на IP65 (в силиконе).")

    # 3. CRI / CCT гейт
    min_cri = project_data.get("min_cri", 90)
    for art in project_data.get("articles", project_data.get("fixtures", [])):
        code = str(art.get("code", art.get("article", "")))
        cri = int(art.get("cri", 0))
        cct = int(art.get("cct", 3000))
        if ("830" in code or "840" in code or (0 < cri < min_cri)) and min_cri >= 90:
            flags.append(f"Артикул '{art.get('name', code)}' имеет низкий индекс CRI 80 (код {code}) — отклонить при требовании CRI >= {min_cri} (заменить на 930).")
        if cct == 4000:
            flags.append(f"Колористический диссонанс: светильник '{art.get('name', code)}' заявлен с 4000K (нейтральный) при общем теплом дизайне 3000K — согласовать с дизайнером.")

    # Расчет BOM
    track_bom = calculate_track_bom(tracks)
    led_bom = calculate_led_bom(led_zones)

    # 4. Фотометрия EN 12464-1 с раздельными коэффициентами прямого (0.70) и скрытого (0.30) света
    photo_results = []
    if project_data.get("photometry", True):
        for rm in project_data.get("rooms_photometry", project_data.get("rooms", [])):
            rm_name = rm.get("room", rm.get("name", "Помещение"))
            S = float(rm.get("area_sqm", rm.get("area", 1.0)))
            H = float(rm.get("height_m", rm.get("height", 2.9)))
            r_type = rm.get("type", "living")
            
            fixtures = rm.get("fixtures", [])
            res_photo = PhotometricEngine.calculate_room_photometry_and_feedback(S, H, r_type, fixtures)
            res_photo["room_name"] = rm_name
            photo_results.append(res_photo)
            if not res_photo["is_sufficient"]:
                flags.append(f"Фотометрия [{rm_name}]: {res_photo['feedback_action']}")

    # 5. Сборка Master BOM для экспорта в Excel и PDF
    master_bom_items = build_master_bom_items(project_data, track_bom, led_bom)

    return {
        "passport": passport,
        "flags": flags,
        "track_bom": track_bom,
        "led_bom": led_bom,
        "photometry": photo_results,
        "master_bom_items": master_bom_items,
        "extras": project_data.get("extras", [])
    }


def build_master_bom_items(project_data, track_bom, led_bom):
    """
    Формирует список позиций для сметы с точными артикулами, брендами, ценами и характеристиками.
    """
    items = []
    
    # 1. Трек 48V хлысты 2м и 3м
    if track_bom["bars_2m_total"] > 0:
        items.append({
            "article": "36.0002.03",
            "name": "Insight Profile 1 Recessed, L=2000mm, 48V/DC, black RAL9005",
            "brand": "Smart Light",
            "color": "black",
            "cct": "—",
            "ip": "IP20",
            "unit": "шт.",
            "qty": track_bom["bars_2m_total"],
            "price_eur": 96.67
        })

    if track_bom["bars_3m_total"] > 0:
        items.append({
            "article": "36.0003.03",
            "name": "Insight Profile 1 Recessed, L=3000mm, 48V/DC, black RAL9005",
            "brand": "Smart Light",
            "color": "black",
            "cct": "—",
            "ip": "IP20",
            "unit": "шт.",
            "qty": track_bom["bars_3m_total"],
            "price_eur": 145.00
        })

    # 2. Фурнитура трека
    items.append({
        "article": "36.0051.03",
        "name": "Insight Endcap торцевая заглушка для Profile 1 / 2, black",
        "brand": "Smart Light",
        "color": "black",
        "cct": "—",
        "ip": "IP20",
        "unit": "шт.",
        "qty": track_bom["end_caps"],
        "price_eur": 2.50
    })

    items.append({
        "article": "36.0031.03",
        "name": "Insight Feed Linear токоввод прямой без кабеля 48V",
        "brand": "Smart Light",
        "color": "black",
        "cct": "—",
        "ip": "IP20",
        "unit": "шт.",
        "qty": max(1, track_bom["power_feeds"] - track_bom["corners_90"]),
        "price_eur": 9.87
    })

    if track_bom["straight_joints"] > 0:
        items.append({
            "article": "36.0066.03",
            "name": "Insight Connector Linear механический соединитель + винты",
            "brand": "Smart Light",
            "color": "black",
            "cct": "—",
            "ip": "IP20",
            "unit": "шт.",
            "qty": track_bom["straight_joints"],
            "price_eur": 1.30
        })

    if track_bom["corners_90"] > 0:
        items.append({
            "article": "36.0021.03",
            "name": "Insight Corner 1 Recessed угловой коннектор L 90°",
            "brand": "Smart Light",
            "color": "black",
            "cct": "—",
            "ip": "IP20",
            "unit": "шт.",
            "qty": track_bom["corners_90"],
            "price_eur": 21.39
        })
        items.append({
            "article": "36.0041.03",
            "name": "Insight Feed Connector Flexible гибкий угловой токоввод L=140mm",
            "brand": "Smart Light",
            "color": "black",
            "cct": "—",
            "ip": "IP20",
            "unit": "шт.",
            "qty": track_bom["corners_90"],
            "price_eur": 24.30
        })

    # Споты трека
    items.append({
        "article": "36.0141.03.930",
        "name": "Insight Spot 15W/930, 34d., 48V/DC, black RAL9005 (CRI>=90, 3000K)",
        "brand": "Smart Light",
        "color": "black",
        "cct": "3000",
        "ip": "IP20",
        "unit": "шт.",
        "qty": track_bom["total_spots"],
        "price_eur": 76.48
    })

    # Блоки питания трека 48V
    for drv in track_bom["drivers_48v_plan"]:
        items.append({
            "article": drv.get("article", "89200X"),
            "name": f"DRIVER 48V 0-{drv['rating_w']}W 230V SELV",
            "brand": "Smart Light",
            "color": "—",
            "cct": "—",
            "ip": "IP20",
            "unit": "шт.",
            "qty": drv["qty"],
            "price_eur": 69.44
        })

    # 3. Встраиваемые светильники Trimless (Триада)
    downlights_count = int(project_data.get("downlights_count", 13))
    if downlights_count > 0:
        triad = BRANDS_CATALOG["trimless_system"]["triad"]
        items.append({
            "article": triad["housing"]["article"],
            "name": triad["housing"]["name"],
            "brand": "Smart Light",
            "color": "black",
            "cct": "—",
            "ip": "IP20",
            "unit": "шт.",
            "qty": downlights_count,
            "price_eur": 17.92
        })
        items.append({
            "article": triad["module"]["article"],
            "name": triad["module"]["name"],
            "brand": "Smart Light",
            "color": "black",
            "cct": "3000",
            "ip": "IP65",
            "unit": "шт.",
            "qty": downlights_count,
            "price_eur": 16.24
        })
        items.append({
            "article": triad["driver"]["article"],
            "name": triad["driver"]["name"],
            "brand": "Smart Light",
            "color": "—",
            "cct": "—",
            "ip": "IP20",
            "unit": "шт.",
            "qty": downlights_count,
            "price_eur": 11.20
        })

    # 4. LED-ленты 24V (разбивка на IP20 и IP65)
    ip65_reels = sum(d["reels_5m"] for d in led_bom["details"] if d["ip"] == "IP65")
    ip20_reels = sum(d["reels_5m"] for d in led_bom["details"] if d["ip"] != "IP65")

    if ip20_reels > 0:
        items.append({
            "article": "7829/W",
            "name": "LED STRIP 24V WW 5m ROLL 9,6W/m IP20 (3000K)",
            "brand": "Smart Light",
            "color": "—",
            "cct": "3000",
            "ip": "IP20",
            "unit": "шт.",
            "qty": ip20_reels,
            "price_eur": 44.80
        })

    if ip65_reels > 0:
        items.append({
            "article": "7829/W-IP65",
            "name": "LED STRIP 24V WW 5m ROLL 9,6W/m IP65 влагозащитная в силиконе (Baie)",
            "brand": "Smart Light",
            "color": "—",
            "cct": "3000",
            "ip": "IP65",
            "unit": "шт.",
            "qty": ip65_reels,
            "price_eur": 52.00
        })

    # Драйверы 24V (модульные)
    drv75_count = sum(1 for d in led_bom["details"] if d["driver_24v_w"] <= 75)
    drv150_count = sum(1 for d in led_bom["details"] if 75 < d["driver_24v_w"] <= 150)
    drv200_count = sum(1 for d in led_bom["details"] if d["driver_24v_w"] > 150)

    if drv75_count > 0:
        items.append({
            "article": "89075V",
            "name": "DRIVER 24V DC 75W 230V SELV",
            "brand": "Smart Light",
            "color": "—",
            "cct": "—",
            "ip": "IP20",
            "unit": "шт.",
            "qty": drv75_count,
            "price_eur": 28.00
        })
    if drv150_count > 0:
        items.append({
            "article": "89150V",
            "name": "DRIVER 24V DC 150W 230V SELV",
            "brand": "Smart Light",
            "color": "—",
            "cct": "—",
            "ip": "IP20",
            "unit": "шт.",
            "qty": drv150_count,
            "price_eur": 49.28
        })

    # Профили для ленты
    if led_bom["slim_sticks_2m"] > 0:
        items.append({
            "article": "KLUS-MICRO-2000",
            "name": "Профиль накладной узкий Slim Black с матовым экраном L=2000мм",
            "brand": "KLUS",
            "color": "black",
            "cct": "—",
            "ip": "IP20",
            "unit": "шт.",
            "qty": led_bom["slim_sticks_2m"],
            "price_eur": 14.50
        })

    if led_bom["kraab_sticks_2m"] > 0:
        items.append({
            "article": "KRAAB-GIPPS-2000",
            "name": "Профиль теневого шва потолка KRAAB GIPPS L=2000мм",
            "brand": "KRAAB Systems",
            "color": "black",
            "cct": "—",
            "ip": "IP20",
            "unit": "шт.",
            "qty": led_bom["kraab_sticks_2m"],
            "price_eur": 22.00
        })

    # 5. Дизайнерские светильники (Nova Luce)
    for fix in project_data.get("designer_fixtures", []):
        items.append({
            "article": str(fix.get("article", "—")),
            "name": str(fix.get("name", "")),
            "brand": fix.get("brand", "Nova Luce"),
            "color": fix.get("color", "black"),
            "cct": str(fix.get("cct", "3000")),
            "ip": fix.get("ip", "IP20"),
            "unit": "шт.",
            "qty": int(fix.get("qty", 1)),
            "price_eur": float(fix.get("price_eur", 0.0))
        })

    return items


def generate_markdown_report(res, project_name="Проект"):
    md = []
    md.append(f"# BOM-отчёт освещения — {project_name}")
    md.append("_Сгенерировано lighting-estimator-pro v3 · промышленный расчёт_\n")

    if res.get("passport"):
        p = res["passport"]
        md.append("## Паспорт объекта")
        md.append(f"- **Объект:** {p.get('name', project_name)}")
        md.append(f"- **Площадь:** {p.get('area_sqm', 'н/д')} м²")
        md.append(f"- **Высоты потолков:** {p.get('heights', 'н/д')}\n")

    md.append("## 0. Инженерные предписания и гейты (v3)")
    if res["flags"]:
        for f in res["flags"]:
            md.append(f"- [ ] {f}")
    else:
        md.append("- [x] Все ключевые параметры зафиксированы, замечаний нет.")
    md.append("")

    md.append("## 1. Трек 48V (Шинопроводы и фурнитура)")
    md.append("| Линия | Длина, м | Хлысты 2м | Хлысты 3м | Закупка | Стыки | Углы | Заглушки | Споты 15W | Плотность |")
    md.append("|---|---|---|---|---|---|---|---|---|---|")
    tb = res["track_bom"]
    for d in tb["details"]:
        md.append(f"| {d['name']} | {d['length_m']} | {d['bars_2m']} | {d['bars_3m']} | {d['purchased_m']} м | {d['joints']} | {d['corners_90']} | 2 | {d['spots_count']} | {d['density_spots_per_m']} шт/м |")
    md.append(f"\n**Итого по треку:** хлыстов 2м — {tb['bars_2m_total']}, 3м — {tb['bars_3m_total']}; вводов питания {tb['power_feeds']}; заглушек торцевых — **{tb['end_caps']} шт.** (по 2 на линию); стыков — {tb['straight_joints']}; углов L — {tb['corners_90']}; спотов — **{tb['total_spots']} шт.**")
    
    drv_str = " + ".join([f"{d['qty']}× {d['rating_w']}W" for d in tb['drivers_48v_plan']])
    md.append(f"**Питание трека 48V:** нагрузка {tb['total_spots_load_w']}W → БП 48V (запас ×1.35): {drv_str} (сумма ≥ {tb['driver_48v_min_w']}W).\n")

    md.append("## 2. Электротехнический расчет LED-ленты 24V (Падение напряжения ΔU)")
    md.append("| Зона | Длина, м | Монтаж | IP | Кабель от щита | Сечение | Нагрузка, W | БП 24V | ΔU кабель | ΔU лента | ΔU общ, % | Статус |")
    md.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    lb = res["led_bom"]
    for d in lb["details"]:
        mount_str = "KRAAB теневой" if "kraab" in d["mount"] else ("Barisol теневой" if "barisol" in d["mount"] else "Slim мебель")
        status_str = "✅ Норма" if d["delta_u_ok"] else f"⚠️ ΔU > 3% (петля/сечение {d['recommended_cable_sqmm']} мм²)"
        md.append(f"| {d['room']} | {d['length_m']} | {mount_str} | {d['ip']} | {d['cable_to_driver_m']} м | {d['wire_sqmm']} мм² | {d['load_w']} | {d['driver_24v_w']}W | {d['delta_u_cable_v']}V | {d['delta_u_tape_v']}V | **{d['delta_u_pct']}%** | {status_str} |")
    
    md.append(f"\n**Итоги закупки лент и профилей:**")
    md.append(f"- **Бобины 5м:** {lb['total_reels_5m']} шт. ({lb['total_purchased_reels_m']} м).")
    md.append(f"- **Профиль Slim Black (2м):** {lb['total_slim_profile_m']} м ({lb['slim_sticks_2m']} шт).")
    if lb['kraab_sticks_2m'] > 0:
        md.append(f"- **Профиль теневого шва KRAAB GIPPS (2м):** {lb['total_kraab_profile_m']} м ({lb['kraab_sticks_2m']} шт).")
    md.append("")

    if res.get("photometry"):
        md.append("## 3. Фотометрия EN 12464-1 (Прямой свет η=0.70 vs Скрытый η=0.30)")
        md.append("| Помещение | S, м² | Факт лк | Норма лк | Прямой свет | Скрытый свет | Статус |")
        md.append("|---|---|---|---|---|---|---|")
        for p in res["photometry"]:
            bk = p["lux_breakdown"]
            st = "✅ Норма" if p["is_sufficient"] else f"⚠️ {p['feedback_action']}"
            md.append(f"| {p['room_name']} | {p['area_sqm']} | **{p['current_lux']}** | {p['target_lux']} | {bk['direct_lux']} лк | {bk['cove_lux']} лк | {st} |")
        md.append("")

    return "\n".join(md)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lighting Estimator PRO v3 CLI")
    parser.add_argument("--project", default="../templates/project.json", help="Path to project.json")
    parser.add_argument("--quote", default=None, help="Path to quote.json for cross-auditing")
    parser.add_argument("--out", default=None, help="Output markdown report path")
    parser.add_argument("--out-json", default=None, help="Output BOM json path")
    parser.add_argument("--out-xlsx", default=None, help="Output Excel .xlsx path with live formulas")
    parser.add_argument("--out-pdf", default=None, help="Output Smart Light commercial offer .pdf path")
    parser.add_argument("--out-html", default=None, help="Output interactive HTML dashboard path")
    args = parser.parse_args()

    project_file = args.project
    if not os.path.exists(project_file):
        alt_p = os.path.join(os.path.dirname(__file__), "..", "templates", "project.json")
        if os.path.exists(alt_p):
            project_file = alt_p
        else:
            print(f"Error: Project file '{project_file}' not found.")
            sys.exit(1)

    with open(project_file, "r", encoding="utf-8") as f:
        proj_data = json.load(f)

    if args.quote and os.path.exists(args.quote):
        with open(args.quote, "r", encoding="utf-8") as f:
            proj_data["quote_data"] = json.load(f)

    res = run_pipeline(proj_data)
    p_name = proj_data.get("passport", {}).get("name", proj_data.get("project_name", "Проект"))
    md_report = generate_markdown_report(res, p_name)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(md_report)
        print(f"Report saved to {args.out}")
    else:
        print(md_report)

    if args.out_json:
        with open(args.out_json, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2)
        print(f"BOM JSON saved to {args.out_json}")

    client = proj_data.get("passport", {}).get("client", "Andreea")
    if args.out_xlsx:
        export_to_excel(proj_data, res["master_bom_items"], args.out_xlsx, client_name=client)
        print(f"Excel offer with live formulas saved to {args.out_xlsx}")

    if args.out_pdf:
        export_to_pdf(proj_data, res["master_bom_items"], args.out_pdf, client_name=client)
        print(f"Smart Light commercial offer PDF saved to {args.out_pdf}")

    if args.out_html:
        generate_interactive_html_dashboard(proj_data, res, args.out_html)
        print(f"Interactive HTML dashboard saved to {args.out_html}")
