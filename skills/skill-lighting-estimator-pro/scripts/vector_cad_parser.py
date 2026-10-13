import pymupdf
import math
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from collections import defaultdict

try:
    import ezdxf
    HAS_EZDXF = True
except ImportError:
    HAS_EZDXF = False

LIGHTING_KEYWORDS = ["electro", "electrica", "lighting", "lumini", "iluminat", "lamp", "sviet", "track", "свет", "электр"]
SOCKET_KEYWORDS = ["prize", "socket", "rozet", "розет"]
ARCH_KEYWORDS = ["stena", "peregorodka", "wall", "dveri", "door", "beam", "xref", "mob", "mebel", "стен", "двер"]
NOISE_KEYWORDS = ["strih", "hatch", "штрих"]
DIM_KEYWORDS = ["razmer", "dim", "cota", "размер"]


def classify_layer_name(name):
    """
    Классифицирует имя слоя CAD/PDF по семантической роли.
    """
    n = name.lower()
    if any(k in n for k in LIGHTING_KEYWORDS):
        return "lighting"
    if any(k in n for k in SOCKET_KEYWORDS):
        return "socket"
    if any(k in n for k in NOISE_KEYWORDS):
        return "noise"
    if any(k in n for k in DIM_KEYWORDS):
        return "dimension"
    if any(k in n for k in ARCH_KEYWORDS):
        return "architecture"
    return "other"


import re

def detect_drawing_scale(page):
    """
    Автоматическое считывание масштаба чертежа из штампа/аннотаций (1:20, 1:25, 1:50, 1:75, 1:100, 1:200).
    Возвращает (pts_per_meter, scale_str).
    1 pt = 1/72 дюйма = 25.4 / 72 мм = 0.352778 мм.
    При масштабе 1:N: 1 м в реальности = (1000 / N) мм на листе = (1000 / N) * (72 / 25.4) pt.
    """
    text = page.get_text()
    
    # 1. Поиск по ключевым словам штампа чертежа
    match = re.search(r'(?:масштаб|scale|scara|ech|м|m)[\s.:]*1\s*[:/]\s*(\d+)', text, re.IGNORECASE)
    if not match:
        # 2. Поиск стандартных соотношений 1:50, 1:100 и т.д.
        match = re.search(r'\b1\s*[:/]\s*(20|25|50|75|100|200)\b', text)
        
    if match:
        scale_denom = int(match.group(1))
        if scale_denom > 0:
            pts_per_m = (1000.0 / scale_denom) * (72.0 / 25.4)
            return round(pts_per_m, 2), f"1:{scale_denom}"
            
    # Fallback по умолчанию 1:50
    return 56.69, "1:50 (по умолчанию)"


def analyze_pdf_with_layer_isolation(pdf_path, output_clean_render=None, pts_per_meter=None):
    """
    Автономный парсер PDF-чертежей с разделением OCG-слоев, фильтрацией паразитного шума,
    автоматическим распознаванием масштаба и детерминированным подсчетом светотехники.
    """
    doc = pymupdf.open(pdf_path)
    report = {
        "format": "pdf",
        "file_path": os.path.abspath(pdf_path),
        "pages_count": len(doc),
        "pages": []
    }

    # Анализ OCG слоев
    layer_configs = doc.layer_ui_configs()
    has_ocg_layers = len(layer_configs) > 0

    ocg_map = {}
    lighting_layer_names = set()
    noise_layer_names = set()

    if has_ocg_layers:
        for c in layer_configs:
            num = c["number"]
            name = c["text"]
            cat = classify_layer_name(name)
            ocg_map[name] = {"number": num, "category": cat, "initial_on": c.get("on", 1)}
            if cat == "lighting":
                lighting_layer_names.add(name)
            elif cat in ["noise", "dimension", "architecture"]:
                noise_layer_names.add(name)

    # Обработка страниц
    for pno, page in enumerate(doc):
        current_pts_m, scale_label = (pts_per_meter, "вручную") if pts_per_meter is not None else detect_drawing_scale(page)
        drawings = page.get_drawings()
        words = page.get_text("words")

        # 1. Фильтрация векторных объектов по слоям
        lighting_drawings = []
        if has_ocg_layers and lighting_layer_names:
            lighting_drawings = [d for d in drawings if d.get("layer") in lighting_layer_names]
        
        # Fallback: если слои не заданы или освещение не выделено в слои
        if not lighting_drawings:
            for d in drawings:
                lay = d.get("layer", "")
                if lay and classify_layer_name(lay) in ["noise", "architecture"]:
                    continue
                lighting_drawings.append(d)

        # 2. Выделение треков (длинные пути) и примитивов символов
        tracks_raw = []
        symbol_primitives = []

        for d in lighting_drawings:
            r = d["rect"]
            diag = math.hypot(r.width, r.height)
            if diag > 30.0:  # > ~10 мм на чертеже — шинопровод / фидер
                tracks_raw.append(d)
            else:
                symbol_primitives.append(d)

        # 3. Кластеризация примитивов символов по пространственной близости (r < 12 pt)
        clusters = []
        used = set()
        for i, p1 in enumerate(symbol_primitives):
            if i in used:
                continue
            cluster = [p1]
            used.add(i)
            queue = [p1]
            while queue:
                curr = queue.pop(0)
                r1 = curr["rect"]
                c1 = ((r1.x0 + r1.x1)/2, (r1.y0 + r1.y1)/2)
                for j, p2 in enumerate(symbol_primitives):
                    if j not in used:
                        r2 = p2["rect"]
                        c2 = ((r2.x0 + r2.x1)/2, (r2.y0 + r2.y1)/2)
                        dist = math.hypot(c1[0] - c2[0], c1[1] - c2[1])
                        if dist < 12.0:
                            used.add(j)
                            cluster.append(p2)
                            queue.append(p2)
            clusters.append(cluster)

        # 4. Классификация символов
        classified_symbols = defaultdict(list)
        for c in clusters:
            min_x = min(d["rect"].x0 for d in c)
            max_x = max(d["rect"].x1 for d in c)
            min_y = min(d["rect"].y0 for d in c)
            max_y = max(d["rect"].y1 for d in c)
            width = max_x - min_x
            height = max_y - min_y
            center = ((min_x + max_x)/2, (min_y + max_y)/2)

            has_curves = any(any(it[0] == "c" for it in d.get("items", [])) for d in c)
            has_lines = any(any(it[0] == "l" for it in d.get("items", [])) for d in c)
            is_filled = any(d.get("fill") is not None for d in c)

            if is_filled:
                classified_symbols["cable_outlet_or_switch"].append({
                    "pos": [round(center[0], 2), round(center[1], 2)],
                    "bbox": [round(min_x, 2), round(min_y, 2), round(round(max_x, 2)), round(max_y, 2)]
                })
            elif has_curves and has_lines:
                if max(width, height) < 8.0:
                    classified_symbols["track_spot"].append({
                        "pos": [round(center[0], 2), round(center[1], 2)],
                        "bbox": [round(min_x, 2), round(min_y, 2), round(max_x, 2), round(max_y, 2)]
                    })
                else:
                    classified_symbols["pendant_or_track_spot"].append({
                        "pos": [round(center[0], 2), round(center[1], 2)],
                        "bbox": [round(min_x, 2), round(min_y, 2), round(max_x, 2), round(max_y, 2)]
                    })
            elif has_lines and not has_curves:
                classified_symbols["recessed_cross_luminaire"].append({
                    "pos": [round(center[0], 2), round(center[1], 2)],
                    "bbox": [round(min_x, 2), round(min_y, 2), round(max_x, 2), round(max_y, 2)]
                })
            else:
                classified_symbols["other_symbol"].append({
                    "pos": [round(center[0], 2), round(center[1], 2)],
                    "bbox": [round(min_x, 2), round(min_y, 2), round(max_x, 2), round(max_y, 2)]
                })

        # 5. Классификация трековых линий
        track_systems = defaultdict(lambda: {"total_linear_pt": 0.0, "total_linear_m": 0.0, "segments": 0})
        for t in tracks_raw:
            r = t["rect"]
            col = t.get("color")
            sys_name = "Track_Standard"
            if col:
                rc, gc, bc = round(col[0], 2), round(col[1], 2), round(col[2], 2)
                if rc > 0.8 and gc < 0.3:
                    sys_name = "Track_Main_Red"
                elif bc > 0.8 and rc < 0.3:
                    sys_name = "Track_Perimeter_Blue"
                elif rc > 0.4 and bc > 0.4:
                    sys_name = "Track_Secondary_Purple"

            length_pt = max(r.width, r.height)
            length_m = length_pt / current_pts_m if current_pts_m > 0 else 0.0

            track_systems[sys_name]["total_linear_pt"] += length_pt
            track_systems[sys_name]["total_linear_m"] += length_m
            track_systems[sys_name]["segments"] += 1

        # Округление метров
        formatted_tracks = {}
        for sname, sdata in track_systems.items():
            formatted_tracks[sname] = {
                "total_linear_m": round(sdata["total_linear_m"], 2),
                "total_linear_pt": round(sdata["total_linear_pt"], 1),
                "segments": sdata["segments"]
            }

        # 6. Извлечение цепей управления (номера групп: 6, 6.1, 9 и т.д.)
        circuit_tags = defaultdict(int)
        for w in words:
            tag = w[4].strip()
            if any(ch.isdigit() for ch in tag) and len(tag) <= 6:
                circuit_tags[tag] += 1

        # 7. Генерация чистого рендера (при запросе)
        clean_render_file = None
        if output_clean_render:
            # Отключаем все паразитные слои
            if has_ocg_layers:
                for c in layer_configs:
                    num = c["number"]
                    name = c["text"]
                    if name in lighting_layer_names:
                        doc.set_layer_ui_config(num, 0) # ON
                    else:
                        doc.set_layer_ui_config(num, 1) # OFF
            
            pix = page.get_pixmap(dpi=150)
            os.makedirs(os.path.dirname(os.path.abspath(output_clean_render)), exist_ok=True)
            pix.save(output_clean_render)
            clean_render_file = os.path.abspath(output_clean_render)

        # Формирование результатов страницы
        page_summary = {
            "page_no": pno + 1,
            "detected_scale": scale_label,
            "pts_per_meter": round(current_pts_m, 2),
            "has_ocg_layers": has_ocg_layers,
            "detected_layers_count": len(layer_configs),
            "lighting_layers": list(lighting_layer_names),
            "filtered_noise_layers": list(noise_layer_names),
            "total_raw_paths": len(drawings),
            "lighting_paths_count": len(lighting_drawings),
            "noise_eliminated_pct": round((1.0 - len(lighting_drawings)/max(1, len(drawings))) * 100, 1),
            "fixtures_counts": {
                "recessed_cross_luminaires": len(classified_symbols["recessed_cross_luminaire"]),
                "pendant_and_track_spots": len(classified_symbols["pendant_or_track_spot"]) + len(classified_symbols["track_spot"]),
                "cable_outlets_switches": len(classified_symbols["cable_outlet_or_switch"]),
                "total_fixtures": (
                    len(classified_symbols["recessed_cross_luminaire"]) +
                    len(classified_symbols["pendant_or_track_spot"]) +
                    len(classified_symbols["track_spot"]) +
                    len(classified_symbols["cable_outlet_or_switch"])
                )
            },
            "track_systems": formatted_tracks,
            "circuit_control_tags": dict(sorted(circuit_tags.items(), key=lambda x: x[1], reverse=True)[:15]),
            "clean_render_path": clean_render_file
        }
        report["pages"].append(page_summary)

    return report


def analyze_dxf_blueprint(dxf_path, unit_scale=0.001):
    """
    Извлекает слои, линии, полилинии, блоки светильников и размеры из 2D DXF чертежа.
    unit_scale: множитель перевода координат в метры (0.001 для мм чертежей, 1.0 для м).
    """
    if not HAS_EZDXF:
        raise RuntimeError("ezdxf is required for DXF blueprint analysis. Install via 'pip install ezdxf'.")

    doc = ezdxf.readfile(dxf_path)
    msp = doc.modelspace()

    layers_summary = {}
    blocks_summary = {}
    lines_by_layer = {}
    texts = []
    dimensions = []

    for entity in msp:
        layer = entity.dxf.layer.upper()
        etype = entity.dxftype()

        if layer not in layers_summary:
            layers_summary[layer] = {
                "entity_count": 0,
                "total_linear_m": 0.0,
                "entity_types": set()
            }
            lines_by_layer[layer] = []

        layers_summary[layer]["entity_count"] += 1
        layers_summary[layer]["entity_types"].add(etype)

        if etype == "LINE":
            start = entity.dxf.start
            end = entity.dxf.end
            dx = (end.x - start.x) * unit_scale
            dy = (end.y - start.y) * unit_scale
            length_m = math.hypot(dx, dy)
            layers_summary[layer]["total_linear_m"] += length_m
            lines_by_layer[layer].append({
                "type": "LINE",
                "length_m": round(length_m, 3),
                "start": [round(start.x * unit_scale, 3), round(start.y * unit_scale, 3)],
                "end": [round(end.x * unit_scale, 3), round(end.y * unit_scale, 3)]
            })

        elif etype in ["LWPOLYLINE", "POLYLINE"]:
            try:
                points = entity.get_points(format="xy") if etype == "LWPOLYLINE" else [v.dxf.location[:2] for v in entity.vertices]
                poly_len = 0.0
                for i in range(len(points) - 1):
                    p1, p2 = points[i], points[i+1]
                    dx = (p2[0] - p1[0]) * unit_scale
                    dy = (p2[1] - p1[1]) * unit_scale
                    poly_len += math.hypot(dx, dy)
                if getattr(entity, "is_closed", False) and len(points) > 2:
                    p1, p2 = points[-1], points[0]
                    poly_len += math.hypot((p2[0] - p1[0]) * unit_scale, (p2[1] - p1[1]) * unit_scale)

                layers_summary[layer]["total_linear_m"] += poly_len
                lines_by_layer[layer].append({
                    "type": etype,
                    "length_m": round(poly_len, 3),
                    "vertices_count": len(points),
                    "is_closed": getattr(entity, "is_closed", False)
                })
            except Exception:
                pass

        elif etype == "INSERT":
            block_name = entity.dxf.name
            insert_pt = [round(entity.dxf.insert.x * unit_scale, 3), round(entity.dxf.insert.y * unit_scale, 3)]
            if block_name not in blocks_summary:
                blocks_summary[block_name] = {
                    "layer": layer,
                    "count": 0,
                    "instances": []
                }
            blocks_summary[block_name]["count"] += 1
            blocks_summary[block_name]["instances"].append(insert_pt)

        elif etype in ["TEXT", "MTEXT"]:
            text_val = entity.dxf.text if etype == "TEXT" else entity.text
            texts.append({
                "layer": layer,
                "text": text_val.strip(),
                "pos": [round(entity.dxf.insert.x * unit_scale, 3), round(entity.dxf.insert.y * unit_scale, 3)]
            })

        elif etype.startswith("DIMENSION"):
            try:
                actual_measurement = entity.dxf.actual_measurement * unit_scale
                dimensions.append({
                    "layer": layer,
                    "measurement_m": round(actual_measurement, 3),
                    "text": getattr(entity.dxf, "text", "")
                })
            except Exception:
                pass

    formatted_layers = {}
    for l_name, l_data in layers_summary.items():
        formatted_layers[l_name] = {
            "entity_count": l_data["entity_count"],
            "total_linear_m": round(l_data["total_linear_m"], 2),
            "entity_types": list(l_data["entity_types"])
        }

    return {
        "format": "dxf",
        "file_path": os.path.abspath(dxf_path),
        "dxf_version": doc.dxfversion,
        "layers": formatted_layers,
        "blocks_symbols": blocks_summary,
        "dimensions_count": len(dimensions),
        "text_annotations_count": len(texts),
        "total_fixtures_from_blocks": sum(b["count"] for b in blocks_summary.values())
    }


def parse_blueprint(file_path, output_clean_render=None):
    """
    Универсальная точка входа: автоопределение формата (PDF / DXF) и извлечение геометрии.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return analyze_pdf_with_layer_isolation(file_path, output_clean_render=output_clean_render)
    elif ext == ".dxf":
        return analyze_dxf_blueprint(file_path)
    else:
        raise ValueError(f"Unsupported blueprint format '{ext}'. Supported formats: .pdf, .dxf")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        clean_img = sys.argv[2] if len(sys.argv) > 2 else None
        res = parse_blueprint(sys.argv[1], output_clean_render=clean_img)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print("Usage: python vector_cad_parser.py <path_to_pdf_or_dxf> [output_clean_png]")
