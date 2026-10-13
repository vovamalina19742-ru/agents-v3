"""
brand_catalog.py — База каталогов и аксессуаров реальных брендов для Lighting Estimator PRO.
Поддерживает: KRAAB Systems, Neko Lighting, KLUS, Smart Light Insight, Topmet.
"""

BRANDS_CATALOG = {
    "kraab": {
        "name": "KRAAB Systems",
        "description": "Системы теневого шва, плинтусов и скрытых карнизов",
        "items": {
            "GIPPS": {
                "article": "KRAAB-GIPPS-2000",
                "name": "Профиль теневого шва потолка KRAAB GIPPS (ГКЛ 12.5мм)",
                "length_m": 2.0,
                "unit": "шт.",
                "category": "ceiling_shadow_profile",
                "accessories": ["демпферная лента", "стыковочные штифты 2мм"]
            },
            "SLK01": {
                "article": "KRAAB-SLK01-2000",
                "name": "Теневой плинтус скрытого монтажа KRAAB SLK01 с пазом под LED",
                "length_m": 2.0,
                "unit": "шт.",
                "category": "baseboard_profile",
                "accessories": ["вставка плинтуса", "уголок внутренний/внешний"]
            },
            "KN01": {
                "article": "KRAAB-KN01-2000",
                "name": "Скрытый потолочный карниз для штор KRAAB KN01 (паз под LED)",
                "length_m": 2.0,
                "unit": "шт.",
                "category": "curtain_cornice",
                "accessories": ["крючки для штор", "торцевые заглушки", "стыковочные штифты"]
            }
        }
    },
    "neko": {
        "name": "Neko Lighting (Moduline 26 / Moduline 05)",
        "description": "Низковольтные магнитные трековые системы 48V",
        "items": {
            "ML26_R2000": {
                "article": "ML26-R2000",
                "name": "Магнитный трековый профиль Neko Moduline 26 врезной/накладной L=2000мм 48V",
                "length_m": 2.0,
                "unit": "шт.",
                "category": "track_profile"
            },
            "ML26_R3000": {
                "article": "ML26-R3000",
                "name": "Магнитный трековый профиль Neko Moduline 26 врезной/накладной L=3000мм 48V",
                "length_m": 3.0,
                "unit": "шт.",
                "category": "track_profile"
            },
            "ML26_TACM": {
                "article": "ML26-TACM",
                "name": "L-образный угловой коннектор Neko Moduline 26 90° (механический + токопровод)",
                "unit": "шт.",
                "category": "track_corner_90"
            },
            "ML26_CKF_C": {
                "article": "ML26-CKF-C",
                "name": "Гибкий угловой коннектор Neko Moduline 26 с кабелем 48V",
                "unit": "шт.",
                "category": "track_flexible_feed"
            },
            "ML26_RLC": {
                "article": "ML26-RLC",
                "name": "Прямой токопроводящий коннектор Neko Moduline 26 (межсекционный)",
                "unit": "шт.",
                "category": "track_straight_joint"
            },
            "ML26_TAIK": {
                "article": "ML26-TAIK",
                "name": "Комплект регулируемого монтажного крепежа/подвеса Neko Moduline 26",
                "unit": "комплект",
                "category": "track_mounting_kit"
            },
            "ML26_EC": {
                "article": "ML26-EC",
                "name": "Заглушки торцевые Neko Moduline 26 (пара)",
                "unit": "пара (2 шт.)",
                "category": "track_endcap"
            }
        }
    },
    "smart_light_insight": {
        "name": "Smart Light — Insight 48V",
        "description": "Встраиваемые магнитные шинопроводы и фурнитура",
        "items": {
            "profile_2m": {
                "article": "36.0002.03",
                "name": "Insight Profile 1 Recessed, L=2000mm, 48V/DC, for ceiling H=13mm, black RAL9005",
                "length_m": 2.0,
                "unit": "шт.",
                "category": "track_profile"
            },
            "endcap": {
                "article": "36.0051.03",
                "name": "Insight Endcap end cap for Profile 1 / Profile 2, black RAL9005",
                "unit": "шт.",
                "category": "track_endcap"
            },
            "feed_linear": {
                "article": "36.0031.03",
                "name": "Insight Feed Linear electrical connector / power terminal without cable 48V/DC, black RAL9005",
                "unit": "шт.",
                "category": "track_feed_direct"
            },
            "feed_cable_600": {
                "article": "36.0035.03",
                "name": "Insight Feed Cable power terminal with cable L=600mm 48V/DC, black RAL9005",
                "unit": "шт.",
                "category": "track_feed_cable"
            },
            "connector_linear": {
                "article": "36.0066.03",
                "name": "Insight Connector Linear mechanical connector + screw for Profile 1 / Profile 2, metal - black RAL9005",
                "unit": "шт.",
                "category": "track_straight_joint"
            },
            "corner_l_recessed": {
                "article": "36.0021.03",
                "name": "Insight Corner 1 Recessed, Łącznik L, mechanical, black RAL9005",
                "unit": "шт.",
                "category": "track_corner_90"
            },
            "feed_flexible_140": {
                "article": "36.0041.03",
                "name": "Insight Feed Connector Flexible electrical connector with cable L-140mm 48V/DC, black RAL9005",
                "unit": "шт.",
                "category": "track_flexible_feed"
            },
            "spot_15w_930": {
                "article": "36.0141.03.930",
                "name": "Insight Spot 15W/930, 34d., 48V/DC, black RAL9005 (CRI>=90, 3000K)",
                "unit": "шт.",
                "power_w": 15.0,
                "cct_k": 3000,
                "cri": 90,
                "category": "track_spot"
            }
        }
    },
    "klus": {
        "name": "KLUS Design",
        "description": "Архитектурные алюминиевые профили для светодиодных лент",
        "items": {
            "KOZEL": {
                "article": "KLUS-KOZEL-2000",
                "name": "Профиль под шпаклевку KLUS KOZEL скрытый L=2000мм",
                "length_m": 2.0,
                "unit": "шт.",
                "category": "recessed_trimless_profile"
            },
            "LOKOM": {
                "article": "KLUS-LOKOM-2000",
                "name": "Профиль накладной/подвесной KLUS LOKOM L=2000мм",
                "length_m": 2.0,
                "unit": "шт.",
                "category": "surface_profile"
            },
            "MICRO_ALU": {
                "article": "KLUS-MICRO-2000",
                "name": "Профиль мебельный узкий KLUS MICRO-ALU L=2000мм",
                "length_m": 2.0,
                "unit": "шт.",
                "category": "furniture_slim_profile"
            }
        }
    },
    "trimless_system": {
        "name": "Trimless Downlight Architecture",
        "description": "Разбивка встраиваемого безрамочного светильника на триаду компонентов",
        "triad": {
            "housing": {
                "article": "10105TR/B",
                "name": "BLACK TRIMLESS GU10 10W DARK LIGHT (Монтажная гипсовая/металлическая рамка)",
                "unit": "шт."
            },
            "module": {
                "article": "7307M/W",
                "name": "MR16 MODULE 7W WW 700mA IP65 DIMMABLE (3000K, 36°)",
                "unit": "шт.",
                "power_w": 7.0,
                "current_ma": 700,
                "ip": "IP65"
            },
            "driver": {
                "article": "89015A",
                "name": "DRIVER 700mA 7-15W 230V (Индивидуальный драйвер постоянного тока)",
                "unit": "шт.",
                "current_ma": 700,
                "power_w": 15.0
            }
        }
    }
}

def resolve_track_accessories(brand_key, total_lines, corners_count=0, bars_2m=0, bars_3m=0):
    """
    Автоматически подбирает полный комплект фурнитуры трека (заглушки, стыки, углы, токовводы).
    Правило заглушек: строго 2 на каждую независимую линию (total_lines * 2).
    """
    accessories = []
    
    endcaps_qty = total_lines * 2
    accessories.append({
        "role": "endcaps",
        "qty": endcaps_qty,
        "formula": f"{total_lines} линий * 2 торца = {endcaps_qty} шт."
    })
    
    # Прямые стыки = сумма хлыстов - число линий (если нет углов)
    total_bars = bars_2m + bars_3m
    straight_joints = max(0, total_bars - total_lines - corners_count)
    if straight_joints > 0:
        accessories.append({
            "role": "straight_joints",
            "qty": straight_joints,
            "formula": f"Хлыстов ({total_bars}) - Линий ({total_lines}) - Углов ({corners_count}) = {straight_joints} шт."
        })
        
    if corners_count > 0:
        accessories.append({
            "role": "corner_l",
            "qty": corners_count,
            "formula": f"{corners_count} шт. по чертежу"
        })
        accessories.append({
            "role": "flexible_feed_connector",
            "qty": corners_count,
            "formula": f"{corners_count} шт. для электрического перехода через угол"
        })
        
    accessories.append({
        "role": "power_feeds",
        "qty": total_lines,
        "formula": f"По 1 вводу питания на каждую линию ({total_lines} шт.)"
    })
    
    return accessories
