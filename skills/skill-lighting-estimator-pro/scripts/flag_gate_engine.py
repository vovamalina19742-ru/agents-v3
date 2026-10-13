class FlagGateEngine:
    """
    Шаг 0: Поднимает флаги и формирует список вопросов до начала расчетов.
    """
    @staticmethod
    def audit_project_inputs(project_data):
        flags = []
        questions_to_designer = []

        # 1. Проверка трековых спотов (если в плане только метры)
        for track in project_data.get("tracks", []):
            if not track.get("spots_count"):
                flags.append({
                    "type": "UNQUANTIFIED_TRACK_SPOTS",
                    "target": track["name"],
                    "length_m": track["length_m"],
                    "recommendation": f"На длину {track['length_m']}м при высоте H={project_data.get('height_m', 2.8)}м заложить {math.ceil(track['length_m'] * 1.6)} спотов 15W 34°"
                })
                questions_to_designer.append(f"Уточнить количество и тип спотов для трека '{track['name']}' (длина {track['length_m']}м)")

        # 2. Проверка мокрых зон (Санузел / Ванная)
        wet_zones = [r for r in project_data.get("rooms", []) if any(k in r["name"].lower() for k in ["baie", "ванн", "сануз", "душ", "spalatorie", "постирочн"])]
        for wz in wet_zones:
            flags.append({
                "type": "WET_ZONE_IP_CHECK",
                "zone": wz["name"],
                "recommendation": "Использовать точечные светильники IP65 (модули MR16 7W 700mA) вместо открытых ламп 220V"
            })

        # 3. CCT & CRI Гейт
        cct = project_data.get("cct_k", 3000)
        cri = project_data.get("min_cri", 90)
        flags.append({
            "type": "QUALITY_GATE",
            "cct_k": cct,
            "min_cri": cri,
            "rule": "Все позиции должны быть строго единой цветовой температуры (3000K) и CRI >= 90 (отсекать CRI 80)"
        })

        return {
            "flags_count": len(flags),
            "flags": flags,
            "questions_to_designer": questions_to_designer
        }

import math
