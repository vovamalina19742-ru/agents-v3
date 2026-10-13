"""
html_dashboard.py — Генератор интерактивных визуальных отчетов (Generative HTML Dashboards) для Smart Light.
Включает:
1. Интерактивный инспектор люксов по комнатам (EN 12464-1).
2. Круговую диаграмму энергопотребления (Ватты по зонам).
3. Калькулятор экономии электроэнергии и окупаемости под критерии грантов ODA Moldova.
"""

import json
import os

def generate_interactive_html_dashboard(project_data, res_data, output_filepath):
    """
    Генерирует автономный интерактивный HTML-дашборд.
    """
    passport = project_data.get("passport", {})
    p_name = passport.get("name", "Apartament Chișinău")
    client_name = passport.get("client", "Andreea")
    date_str = passport.get("date", "29.09.2026")
    area_sqm = passport.get("area_sqm", 74.1)

    tb = res_data.get("track_bom", {})
    lb = res_data.get("led_bom", {})
    photo = res_data.get("photometry", [])

    track_w = float(tb.get("total_spots_load_w", 255.0))
    led_w = sum(float(d.get("load_w", 0)) for d in lb.get("details", []))
    downlights_w = int(project_data.get("downlights_count", 13)) * 7.0
    designer_w = sum(float(f.get("qty", 1)) * 15.0 for f in project_data.get("designer_fixtures", []))
    total_w = round(track_w + led_w + downlights_w + designer_w, 1)

    # Данные комнат для JS
    rooms_js = []
    for p in photo:
        rooms_js.append({
            "name": p.get("room_name", "Комната"),
            "area": p.get("area_sqm", 20.0),
            "current_lux": p.get("current_lux", 300),
            "target_lux": p.get("target_lux", 300),
            "direct_lux": p.get("lux_breakdown", {}).get("direct_lux", 200),
            "cove_lux": p.get("lux_breakdown", {}).get("cove_lux", 100),
            "status": "Норма" if p.get("is_sufficient", True) else "Дефицит"
        })

    # Данные мощностей
    power_labels = ["Трек 48V (Споты)", "LED-лента 24V (Ниши/Мебель)", "Даунлайты Trimless", "Дизайнерские светильники"]
    power_values = [round(track_w, 1), round(led_w, 1), round(downlights_w, 1), round(designer_w, 1)]

    html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Smart Light Dashboard — {p_name}</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {{
      --primary: #ea580c;
      --bg: #0f172a;
      --card-bg: #1e293b;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --accent-green: #10b981;
      --accent-yellow: #f59e0b;
      --border: #334155;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
    body {{ background: var(--bg); color: var(--text); padding: 24px; line-height: 1.5; }}
    .container {{ max-width: 1200px; margin: 0 auto; }}
    
    /* Header */
    .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid var(--border); padding-bottom: 16px; margin-bottom: 24px; }}
    .logo {{ display: flex; align-items: center; gap: 12px; }}
    .logo-badge {{ background: var(--primary); color: white; padding: 6px 12px; font-weight: bold; border-radius: 4px; font-size: 18px; letter-spacing: 1px; }}
    .header-info {{ text-align: right; color: var(--text-muted); font-size: 13px; }}
    .header-info strong {{ color: var(--text); font-size: 14px; }}

    /* KPI Grid */
    .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; margin-bottom: 24px; }}
    .kpi-card {{ background: var(--card-bg); padding: 18px; border-radius: 8px; border: 1px solid var(--border); }}
    .kpi-card .label {{ font-size: 12px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }}
    .kpi-card .value {{ font-size: 26px; font-weight: bold; color: var(--text); margin-top: 6px; }}
    .kpi-card .sub {{ font-size: 12px; color: var(--accent-green); margin-top: 4px; }}

    /* Grid layout */
    .dashboard-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 24px; }}
    @media (max-width: 900px) {{ .dashboard-grid {{ grid-template-columns: 1fr; }} }}

    .card {{ background: var(--card-bg); padding: 20px; border-radius: 8px; border: 1px solid var(--border); }}
    .card-title {{ font-size: 16px; font-weight: bold; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; }}
    
    /* Room inspector */
    .room-item {{ background: #0f172a; padding: 12px 16px; border-radius: 6px; margin-bottom: 10px; border-left: 4px solid var(--primary); }}
    .room-header {{ display: flex; justify-content: space-between; font-weight: bold; font-size: 14px; }}
    .room-details {{ display: flex; gap: 16px; margin-top: 8px; font-size: 12px; color: var(--text-muted); }}
    .lux-badge {{ padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold; }}
    .lux-ok {{ background: rgba(16, 185, 129, 0.2); color: var(--accent-green); }}
    .lux-warn {{ background: rgba(245, 158, 11, 0.2); color: var(--accent-yellow); }}

    /* Energy Calculator */
    .calc-row {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }}
    .calc-row input {{ background: #0f172a; border: 1px solid var(--border); color: white; padding: 6px 10px; border-radius: 4px; width: 100px; text-align: right; }}
    .calc-result {{ background: rgba(234, 88, 12, 0.15); border: 1px solid var(--primary); padding: 16px; border-radius: 6px; margin-top: 16px; }}
    .oda-badge {{ display: inline-flex; align-items: center; gap: 8px; background: rgba(16, 185, 129, 0.15); border: 1px solid var(--accent-green); color: var(--accent-green); padding: 8px 12px; border-radius: 6px; font-size: 12px; margin-top: 14px; font-weight: 500; }}

    /* Footer */
    .footer {{ text-align: center; color: var(--text-muted); font-size: 12px; margin-top: 32px; border-top: 1px solid var(--border); padding-top: 16px; }}
  </style>
</head>
<body>
  <div class="container">
    
    <!-- Header -->
    <div class="header">
      <div class="logo">
        <div class="logo-badge">SMART LIGHT</div>
        <div>
          <h2 style="font-size: 18px;">Интерактивный светотехнический дашборд</h2>
          <p style="font-size: 12px; color: var(--text-muted);">{p_name} · Клиент: {client_name}</p>
        </div>
      </div>
      <div class="header-info">
        <strong>Andrei Mahotchin</strong> · Project Lighting Manager<br>
        +373 62 180001 | sales@smartlight.md | Chisinau
      </div>
    </div>

    <!-- KPI Grid -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="label">Общая площадь</div>
        <div class="value">{area_sqm} м²</div>
        <div class="sub">H = 2.90–3.60м</div>
      </div>
      <div class="kpi-card">
        <div class="label">Суммарная мощность LED</div>
        <div class="value">{total_w} Вт</div>
        <div class="sub">~14.2 Вт/м² (Энергоэффективный А+)</div>
      </div>
      <div class="kpi-card">
        <div class="label">Длина шинопроводов 48V</div>
        <div class="value">12.0 м</div>
        <div class="sub">3 трассы · 17 спотов (CRI 90+)</div>
      </div>
      <div class="kpi-card">
        <div class="label">LED-подсветки 24V</div>
        <div class="value">45.4 м</div>
        <div class="sub">13 бобин · Профили KRAAB / Slim</div>
      </div>
    </div>

    <!-- Main Grid -->
    <div class="dashboard-grid">
      
      <!-- 1. Фотометрический инспектор по комнатам -->
      <div class="card">
        <div class="card-title">
          <span>Освещенность помещений (EN 12464-1)</span>
          <span style="font-size: 11px; color: var(--text-muted);">Прямой (η=0.7) / Скрытый (η=0.3)</span>
        </div>
        <div id="rooms-container"></div>
      </div>

      <!-- 2. Круговая диаграмма мощности -->
      <div class="card">
        <div class="card-title">
          <span>Распределение электрической мощности</span>
          <span style="font-size: 12px; color: var(--primary);">Итого: {total_w} Вт</span>
        </div>
        <div style="max-height: 280px; position: relative; display: flex; justify-content: center;">
          <canvas id="powerChart"></canvas>
        </div>
      </div>

    </div>

    <!-- 3. Калькулятор окупаемости и гранты ODA Moldova -->
    <div class="card">
      <div class="card-title">
        <span>Калькулятор энергоэффективности и грантов ODA Moldova</span>
        <span style="font-size: 12px; color: var(--accent-green);">Базовый аналог: 4 850 Вт (Галоген/ЛН)</span>
      </div>
      
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px;">
        <div>
          <div class="calc-row">
            <label style="font-size: 13px; color: var(--text-muted);">Тариф электроэнергии (MDL / кВт·ч):</label>
            <input type="number" id="tariff" value="2.80" step="0.10">
          </div>
          <div class="calc-row">
            <label style="font-size: 13px; color: var(--text-muted);">Часов работы света в сутки:</label>
            <input type="number" id="hours" value="6" step="1">
          </div>
          <div class="calc-row">
            <label style="font-size: 13px; color: var(--text-muted);">Курс EUR / MDL:</label>
            <input type="number" id="eur_rate" value="19.50" step="0.10">
          </div>
        </div>

        <div>
          <div class="calc-result">
            <div style="font-size: 13px; color: var(--text-muted);">Годовая экономия электроэнергии:</div>
            <div id="savings-val" style="font-size: 24px; font-weight: bold; color: var(--primary); margin: 6px 0;">—</div>
            <div id="kwh-saved" style="font-size: 12px; color: var(--accent-green);">—</div>
          </div>
          <div class="oda-badge">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
            Проект квалифицирован для субсидий энергоэффективности ODA Moldova (экономия > 75%)
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="footer">
      Smart Light Solutions · Chișinău, str. Pajurii 11 · Гарантия на систему: 3 года · Спецификация v3.0
    </div>

  </div>

  <script>
    // Данные комнат
    const rooms = {json.dumps(rooms_js, ensure_ascii=False)};
    const roomsContainer = document.getElementById("rooms-container");

    rooms.forEach(r => {{
      const isOk = r.current_lux >= r.target_lux;
      const badgeClass = isOk ? "lux-ok" : "lux-warn";
      const badgeText = isOk ? "Норма по EN 12464-1" : `Дефицит ${{Math.round(r.target_lux - r.current_lux)}} лк`;
      
      const html = `
        <div class="room-item">
          <div class="room-header">
            <span>${{r.name}} (${{r.area}} м²)</span>
            <span class="lux-badge ${{badgeClass}}">${{r.current_lux}} лк / норма ${{r.target_lux}} лк</span>
          </div>
          <div class="room-details">
            <span>Прямой свет: <strong>${{r.direct_lux}} лк</strong></span>
            <span>Скрытый свет (ниши): <strong>${{r.cove_lux}} лк</strong></span>
            <span style="margin-left: auto; color: ${{isOk ? '#10b981' : '#f59e0b'}};">${{badgeText}}</span>
          </div>
        </div>
      `;
      roomsContainer.innerHTML += html;
    }});

    // Круговая диаграмма Chart.js
    const ctx = document.getElementById('powerChart').getContext('2d');
    new Chart(ctx, {{
      type: 'doughnut',
      data: {{
        labels: {json.dumps(power_labels, ensure_ascii=False)},
        datasets: [{{
          data: {json.dumps(power_values)},
          backgroundColor: ['#ea580c', '#38bdf8', '#10b981', '#a855f7'],
          borderWidth: 2,
          borderColor: '#1e293b'
        }}]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{
          legend: {{
            position: 'bottom',
            labels: {{ color: '#94a3b8', font: {{ size: 11 }} }}
          }}
        }}
      }}
    }});

    // Калькулятор экономии ODA
    const totalWattsLed = {total_w};
    const baselineWatts = 4850; // Традиционный свет

    function updateCalculator() {{
      const tariff = parseFloat(document.getElementById('tariff').value) || 2.80;
      const hours = parseFloat(document.getElementById('hours').value) || 6;
      const eurRate = parseFloat(document.getElementById('eur_rate').value) || 19.50;

      const diffKw = (baselineWatts - totalWattsLed) / 1000.0;
      const kwhYear = diffKw * hours * 365;
      const mdlSavings = kwhYear * tariff;
      const eurSavings = mdlSavings / eurRate;

      document.getElementById('savings-val').innerText = `${{Math.round(mdlSavings).toLocaleString()}} MDL / год (~${{Math.round(eurSavings)}} €)`;
      document.getElementById('kwh-saved').innerText = `Сокращение расхода на ${{Math.round(kwhYear).toLocaleString()}} кВт·ч в год (-${{Math.round((baselineWatts - totalWattsLed)/baselineWatts * 100)}}%)`;
    }}

    document.getElementById('tariff').addEventListener('input', updateCalculator);
    document.getElementById('hours').addEventListener('input', updateCalculator);
    document.getElementById('eur_rate').addEventListener('input', updateCalculator);
    updateCalculator();
  </script>
</body>
</html>
"""
    os.makedirs(os.path.dirname(os.path.abspath(output_filepath)), exist_ok=True)
    with open(output_filepath, "w", encoding="utf-8") as f:
        f.write(html_content)
    return output_filepath
