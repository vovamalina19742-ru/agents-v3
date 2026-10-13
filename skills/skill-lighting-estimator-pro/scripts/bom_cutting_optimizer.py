import math

class BOMOptimizer:
    """
    Инженерный калькулятор раскроя трековых профилей, фурнитуры, профилей CABI12/OMNI10 и 5м бобин LED ленты.
    """
    @staticmethod
    def calculate_track_bom(track_lines, extra_spots_from_photometry=0):
        profiles_2m = 0
        profiles_3m = 0
        power_feeds = 0
        end_caps = 0
        straight_connectors = 0
        corner_connectors = 0
        total_net_length = sum(l["length_m"] for l in track_lines)

        for line in track_lines:
            L = line["length_m"]
            power_feeds += 1
            end_caps += 2
            
            if line.get("has_corner_90", False):
                corner_connectors += 1

            if L <= 2.0:
                profiles_2m += 1
            elif L <= 3.0:
                profiles_3m += 1
            elif L <= 4.0:
                profiles_2m += 2
                straight_connectors += 1
            elif L <= 5.0:
                profiles_3m += 1
                profiles_2m += 1
                straight_connectors += 1
            elif L <= 6.0:
                profiles_2m += 3
                straight_connectors += 1
            else:
                n3 = int(L // 3.0)
                rem = L % 3.0
                profiles_3m += n3
                if rem > 0:
                    if rem <= 2.0:
                        profiles_2m += 1
                    else:
                        profiles_3m += 1
                straight_connectors += (n3 + (1 if rem > 0 else 0) - 1)

        # Рекомендуемое число спотов 15W при H > 3.0м (базово 1.6 спота на 1м)
        base_spots = math.ceil(total_net_length * 1.6)
        total_spots = base_spots + extra_spots_from_photometry

        return {
            "total_net_m": total_net_length,
            "profiles_2000mm": profiles_2m,
            "profiles_3000mm": profiles_3m,
            "total_purchase_m": (profiles_2m * 2.0) + (profiles_3m * 3.0),
            "power_feeds": power_feeds,
            "end_caps": end_caps,
            "straight_connectors": straight_connectors,
            "corner_connectors_90": corner_connectors,
            "recommended_spots_15w": total_spots
        }

    STANDARD_WASTE_FACTORS = {
        "profile_straight": 1.05,       # 5% отход при прямых резах
        "profile_miter_corners": 1.10,  # 10% отход при запилах под 45°
        "led_tape": 1.08,               # 8% технологический запас на пайку и кратность реза
        "cable_runs": 1.15,             # 15% запас на провисы и спуски
        "driver_safety_margin": 1.35    # 35% запас мощности блоков питания
    }

    @classmethod
    def calculate_takeoff_summary(cls, net_val, gross_val, unit="m"):
        """
        Расчет коэффициента перерасхода и отходов раскроя (Quantity Takeoff Waste Analysis).
        """
        waste_qty = round(gross_val - net_val, 2)
        waste_pct = round((waste_qty / net_val * 100) if net_val > 0 else 0.0, 1)
        return {
            "net_quantity": round(net_val, 2),
            "gross_quantity": round(gross_val, 2),
            "waste_quantity": waste_qty,
            "waste_percentage": waste_pct,
            "unit": unit
        }

    @staticmethod
    def calculate_led_tape_and_profiles_bom(rooms_led, waste_factor_profile=1.10):
        """
        Разделяет профили на мебельные CABI12 и нишевые OMNI10 + считает бобины по 5м и блоки питания.
        waste_factor_profile: инженерный коэффициент запаса на подрезку (по умолчанию 1.10 = +10%).
        """
        total_net_m = sum(r["length_m"] for r in rooms_led)
        total_rolls_5m = 0
        cabi12_m = 0.0
        omni10_m = 0.0
        drivers = []

        for r in rooms_led:
            L = r["length_m"]
            rolls = math.ceil(L / 5.0)
            total_rolls_5m += rolls
            
            # Разделение по типу монтажа с учетом нормированного коэффициента отхода
            if r.get("is_cove_or_step", False):
                omni10_m += L * waste_factor_profile
            else:
                cabi12_m += L * waste_factor_profile

            w_m = r.get("power_w_per_m", 9.6)
            p_load = L * w_m
            p_driver_min = p_load * 1.35 # 35% запас
            
            standard_driver_ratings = [50, 60, 75, 100, 150, 200, 240, 300, 320, 350]
            driver_w = next((d for d in standard_driver_ratings if d >= p_driver_min), math.ceil(p_driver_min / 50) * 50)
            
            drivers.append({
                "room": r["room"],
                "length_m": L,
                "rolls_5m": rolls,
                "load_w": round(p_load, 1),
                "driver_w": driver_w
            })

        cabi12_sticks_2m = math.ceil(cabi12_m / 2.0)
        omni10_sticks_2m = math.ceil(omni10_m / 2.0)

        return {
            "total_net_m": total_net_m,
            "total_rolls_5m": total_rolls_5m,
            "total_purchase_tape_m": total_rolls_5m * 5.0,
            "cabi12_profile_2m_sticks": cabi12_sticks_2m,
            "cabi12_total_m": cabi12_sticks_2m * 2.0,
            "omni10_profile_2m_sticks": omni10_sticks_2m,
            "omni10_total_m": omni10_sticks_2m * 2.0,
            "drivers": drivers
        }

