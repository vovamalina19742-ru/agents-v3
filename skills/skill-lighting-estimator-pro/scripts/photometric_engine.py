"""
photometric_engine.py — Фотометрический модуль по EN 12464-1 с раздельным учетом прямого света
и скрытого света в нишах/карнизах (Cove lighting) с обратной связью (Closed Loop to BOM).
"""

import math

class PhotometricEngine:
    """
    Фотометрический расчет освещенности с раздельными коэффициентами использования:
    - Прямой свет (споты на треке, даунлайты, подвесы): eta = 0.70 (70% в рабочую зону)
    - Скрытый свет в нишах/карнизах/теневом шве (Cove): eta = 0.30 (25-35% в рабочую зону из-за отражения)
    """
    STANDARDS_LUX = {
        "kitchen": 500,
        "living": 300,
        "bedroom": 200,
        "bathroom": 300,
        "hallway": 150,
        "corridor": 150,
        "laundry": 250,
        "terrace": 100,
        "office": 500
    }

    ETA_DIRECT = 0.70   # Прямой свет
    ETA_COVE = 0.30     # Скрытый свет в нишах/карнизах/Barisol (потери на отражение 70%)

    @staticmethod
    def calculate_room_photometry_and_feedback(room_area_sqm, height_m, room_type="living", current_fixtures=[]):
        """
        Разделяет приборы на прямой свет и скрытый (cove/strip), предотвращая завышение люксов от лент.
        """
        target_lux = PhotometricEngine.STANDARDS_LUX.get(room_type.lower(), 300)
        
        direct_lumens = 0.0
        cove_lumens = 0.0

        for f in current_fixtures:
            lm = float(f.get("lumens", 0))
            is_cove = (
                f.get("is_cove", False) or 
                f.get("type", "") in ["strip", "cove", "recessed_strip", "barisol", "shelf", "tape"] or
                any(k in str(f.get("name", "")).lower() for k in ["лент", "strip", "теневой", "barisol", "карниз", "полк", "cove"])
            )
            if is_cove:
                cove_lumens += lm
            else:
                direct_lumens += lm

        # Коэффициент высоты потолка (при H > 3.0м потери рассеяния увеличиваются)
        height_factor = 0.85 if height_m <= 3.0 else 0.70

        # Эффективный полезный световой поток в рабочей плоскости (лк = лм / м2)
        effective_direct_lm = direct_lumens * PhotometricEngine.ETA_DIRECT * height_factor
        effective_cove_lm = cove_lumens * PhotometricEngine.ETA_COVE * height_factor
        total_effective_lm = effective_direct_lm + effective_cove_lm

        area = max(float(room_area_sqm), 1.0)
        lux_direct = effective_direct_lm / area
        lux_cove = effective_cove_lm / area
        total_lux = total_effective_lm / area

        needed_additional_spots = 0

        if total_lux < target_lux:
            deficit_lux = target_lux - total_lux
            # Восполняем дефицит прямым светом (спот 15W ~ 1350 лм при CRI90)
            needed_direct_lm = (deficit_lux * area) / (PhotometricEngine.ETA_DIRECT * height_factor)
            needed_additional_spots = math.ceil(needed_direct_lm / 1350.0)

        return {
            "room_type": room_type,
            "area_sqm": room_area_sqm,
            "height_m": height_m,
            "target_lux": target_lux,
            "current_lux": round(total_lux, 1),
            "lux_breakdown": {
                "direct_lux": round(lux_direct, 1),
                "cove_lux": round(lux_cove, 1),
                "direct_lumens_raw": round(direct_lumens, 0),
                "cove_lumens_raw": round(cove_lumens, 0),
                "eta_direct": PhotometricEngine.ETA_DIRECT,
                "eta_cove": PhotometricEngine.ETA_COVE
            },
            "is_sufficient": total_lux >= target_lux,
            "needed_additional_spots_15w": needed_additional_spots,
            "feedback_action": (
                f"Дефицит {round(target_lux - total_lux, 1)} лк! Добавить {needed_additional_spots} спотов 15W прямого света"
                if needed_additional_spots > 0 else "Освещенность в норме по EN 12464-1"
            )
        }
