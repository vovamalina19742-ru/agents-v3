"""
logistics_matrix.py — Модуль логистического контроля, матрицы условий европейских фабрик,
стоп-факторов Pre-Flight и протоколов защиты проектных решений для Smart Light.
"""

# ----------------- 1. МАТРИЦА УСЛОВИЙ ЕВРОПЕЙСКИХ ФАБРИК -----------------
MANUFACTURER_MATRIX = {
    "lombardo": {
        "brand": "Lombardo",
        "country": "Italy (Villongo, Bergamo)",
        "discount_pct": 40.0,
        "payment_terms": "100% предоплата (Advanced payment)",
        "incoterms": "EXW (Villongo, Bergamo)",
        "lead_time_weeks": "3-4 недели",
        "notes": "Самовывоз со склада фабрики в провинции Бергамо. Требуется экспедитор с забором в Италии."
    },
    "louis_poulsen": {
        "brand": "Louis Poulsen",
        "country": "Denmark",
        "discount_pct": 35.0,
        "showroom_threshold_eur": 5000.0,
        "conditions": "Проверка соцсетей (Instagram), согласование концепции шоурума",
        "order_type": "Project-based (под конкретные проекты)",
        "notes": "Дилерский статус требует экспозиции от 5 000 €. Разовые поставки согласуются по проектной спецификации."
    },
    "neko": {
        "brand": "NEKO Lighting",
        "country": "Switzerland / China",
        "order_type": "Консолидированные поставки",
        "logistics_check": "Строгая проверка маркировки коробок (Carton No / Box ID)",
        "packing_rule": "Сверка каждой коробки с упаковочным листом фабрики во избежание пересорта оптики 24°/36°"
    },
    "kraab": {
        "brand": "KRAAB Systems",
        "country": "Estonia / International",
        "catalog_focus": ["KRAAB GIPPS (потолочный теневой)", "SLK01 (теневой плинтус)", "KN01 (скрытый карниз)"],
        "stock": "Локальный склад или экспресс-доставка 7-10 дней"
    },
    "nova_luce": {
        "brand": "Nova Luce",
        "country": "Greece",
        "discount_pct": 45.0,
        "lead_time_days": 20,
        "warranty_years": 3,
        "notes": "Регулярные прямые поставки в Кишинев. Позиции складской программы."
    }
}


# ----------------- 2. ЛОГИСТИЧЕСКИЙ ШЛЮЗ СВЕРКИ (LOGISTICS CROSS-CHECK GATE) -----------------
def audit_logistics_cargo(cmr_places, t1_places, packing_list_places, invoices_places_sum):
    """
    Формула тройной сверки:
    Места в CMR == Места в T1 == Места в Пакинг-листе == Сумма мест по инвойсам.
    """
    matches = (cmr_places == t1_places == packing_list_places == invoices_places_sum)
    diffs = {
        "cmr_places": cmr_places,
        "t1_places": t1_places,
        "packing_list_places": packing_list_places,
        "invoices_sum": invoices_places_sum
    }
    
    warnings = []
    if not matches:
        warnings.append(
            f"КРИТИЧЕСКОЕ НЕСООТВЕТСТВИЕ МЕСТ: CMR={cmr_places}, T1={t1_places}, "
            f"Packing List={packing_list_places}, Сумма по инвойсам={invoices_places_sum}. "
            "Риск ареста/задержки груза на молдавской таможне!"
        )

    # Контроль языкового шлюза для молдавской таможни
    customs_doc_status = {
        "proforma_ro_needed": True,
        "document_name": "FACTURĂ PROFORMĂ",
        "language": "Romanian (Limba Română)",
        "deadline": "До прибытия автотранспорта на таможенный терминал в Кишиневе"
    }

    return {
        "status": "APPROVED" if matches else "BLOCKED_DISCREPANCY",
        "is_safe_for_customs": matches,
        "diffs": diffs,
        "warnings": warnings,
        "customs_language_gate": customs_doc_status
    }


# ----------------- 3. ЧЕК-ЛИСТ СТОП-ФАКТОРОВ (PRE-FLIGHT SAFETY GATE) -----------------
def check_preflight_blockers(project_data):
    """
    Проверяет наличие обязательных исходных данных перед началом светотехнического расчета.
    Запрещает расчетчику тратить время на работу «на глазок».
    """
    blockers = []
    warnings = []

    # 1. Высота чистового потолка
    passport = project_data.get("passport", {})
    h = passport.get("height_m") or project_data.get("height_m")
    if not h:
        blockers.append("СТОП: Не указана точная высота чистового потолка (H). Невозможно рассчитать люксы и длину подвесов!")

    # 2. Тип конструктива потолка
    c_type = passport.get("ceiling_construction") or project_data.get("ceiling_construction")
    if not c_type:
        warnings.append("ВНИМАНИЕ: Не указан тип конструктива потолка (ГКЛ, натяжной, теневой KRAAB, бетон). Риск ошибки в выборе профиля.")

    # 3. План мебели
    has_furniture = project_data.get("furniture_plan_confirmed", False)
    if not has_furniture:
        warnings.append("ВНИМАНИЕ: План расстановки мебели не утвержден дизайнером. Риск установки спотов в габариты шкафов.")

    # 4. Бюджетная планка клиента
    budget_tier = project_data.get("budget_tier", "optimal")
    if budget_tier not in ["basic", "optimal", "premium"]:
        warnings.append(f"Бюджетная планка '{budget_tier}' не определена (выберите: basic / optimal / premium).")

    return {
        "can_proceed": len(blockers) == 0,
        "blockers": blockers,
        "warnings": warnings,
        "readiness_score_pct": 100 if len(blockers) == 0 and len(warnings) == 0 else (70 if len(blockers) == 0 else 30)
    }


# ----------------- 4. ПРОТОКОЛ ЗАЩИТЫ ПРОЕКТНЫХ РЕШЕНИЙ (CLIENT DEFENSE PROTOCOL) -----------------
def generate_client_objection_defense(objection_topic):
    """
    Выдает 4-шаговый дипломатичный ответ на типовые претензии клиентов и дизайнеров.
    """
    templates = {
        "bathroom_ip20": {
            "title": "Претензия: 'Ленту в ванной замкнет, почему заложена IP20, а не IP65 в силиконе?'",
            "step_1_diplomacy": "Благодарим за внимание к безопасности влажных зон.",
            "step_2_standard_and_physics": (
                "По международному стандарту IEC 60364-7-701 потолочные ниши выше 2.25 м относятся к Зоне 3 (вне зон прямого попадания воды). "
                "В них нормативно разрешена лента IP20 при установке в алюминиевый профиль с рассеивателем. "
                "Инженерный факт: толстый силикон (IP65) ухудшает теплоотвод, вызывает перегрев кристаллов до 80°C и за 2 года желтеет, теряя до 30% света. "
                "Профиль с матовым поликарбонатным экраном отсекает пар и конденсат, сохраняя идеальный теплоотвод."
            ),
            "step_3_flexibility": "В зонах прямого контакта со струями воды (ниша в душе) мы монтируем герметичную ленту IP68.",
            "step_4_action": "При желании заказчика можем залить силиконом, но профессионально рекомендуем профиль + IP20."
        },
        "mirror_cct_4000k": {
            "title": "Претензия: 'Светильник у зеркала 4000K — это ошибка, у меня вся квартира 3000K!'",
            "step_1_diplomacy": "Прекрасно понимаем ваше стремление к единому теплому уюту во всем доме.",
            "step_2_standard_and_physics": (
                "Нейтральный свет 4000K с высоким CRI >= 90 закладывается у макияжного зеркала осознанно. "
                "Теплый свет 3000K дает паразитный желтый оттенок на коже, искажая цветовосприятие при нанесении макияжа и уходе за лицом. "
                "4000K у зеркала — общепринятый стандарт визажистов и косметологов."
            ),
            "step_3_flexibility": "Если зеркало носит исключительно декоративный характер для вечернего релакса — мы в один клик меняем модуль на 3000K.",
            "step_4_action": "Решение принимается клиентом: профессиональный свет для макияжа (4000K) или единый релакс (3000K)."
        },
        "missing_profiles": {
            "title": "Претензия: 'В вашей смете нет алюминиевого профиля для ленты!'",
            "step_1_diplomacy": "Полностью разделяем ваше требование: монтаж ленты на дерево или ГКЛ без алюминия недопустим.",
            "step_2_standard_and_physics": (
                "Алюминиевый профиль — это обязательный радиатор охлаждения диодов. "
                "Традиционно профили теневого шва заказываются вместе с потолочными системами, а мебельные — с гарнитуром."
            ),
            "step_3_flexibility": "Мы поставляем полный комплект оригинальных профилей KLUS / KRAAB / Topmet единым пакетом.",
            "step_4_action": "В обновленную редакцию сметы полный метраж профилей с рассеивателями уже включен отдельным прозрачным разделом."
        }
    }
    return templates.get(objection_topic, {})
