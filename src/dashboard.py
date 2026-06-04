"""
Beautiful HTML Dashboard Generator -- Advanced Interactive Edition
Creates an interactive dark-mode dashboard with Tabs, Slicers, and Cross-Filtering.
Uses Plotly for charts. Opens in any browser -- NO login needed.
"""
import sys
import json
import pandas as pd
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import INSIGHTS_JSON, DASHBOARD_HTML, CLEANED_CSV


def create_dashboard(insights_path=None, output_path=None) -> str:
    insights_path = insights_path or INSIGHTS_JSON
    output_path   = output_path   or DASHBOARD_HTML
    csv_path      = CLEANED_CSV

    print(f"\n{'='*50}")
    print("  DASHBOARD GENERATION STARTED (Interactive)")
    print(f"{'='*50}")

    with open(insights_path, encoding="utf-8") as f:
        data = json.load(f)

    # Load raw data for client-side cross-filtering
    try:
        df = pd.read_csv(csv_path)
        # Convert to records format (list of dicts)
        raw_data_json = df.to_json(orient="records")
    except Exception as e:
        print(f"  [WARN] Could not load raw data for interactive slicers: {e}")
        raw_data_json = "[]"

    from datetime import datetime
    generated_at  = datetime.now().strftime("%d %b %Y, %I:%M %p")
    total_sales   = data.get("total_sales",  0)
    total_profit  = data.get("total_profit", 0)
    total_orders  = data.get("total_orders", 0)
    profit_margin = data.get("profit_margin", 0)
    avg_order     = round(total_sales / total_orders, 0) if total_orders else 0
    ai_source     = data.get("ai_insights_source", "Rule-Based")
    ai_insights   = data.get("ai_insights", "No insights available.")
    domain        = data.get("domain", "Sales")

    def fmt(v):
        v = float(v)
        if v >= 1_00_00_000: return f"{v/1_00_00_000:.1f}Cr"
        if v >= 1_00_000:    return f"{v/1_00_000:.1f}L"
        if v >= 1_000:       return f"{v/1_000:.1f}K"
        return f"{v:,.0f}"

    profit_class  = "" if profit_margin >= 0 else "neg"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>AI Analytics Dashboard - {domain}</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet"/>
<style>
  :root{{
    --bg:#0a0e1a;--card:#111827;--card2:#1a2234;
    --accent:#6366f1;--accent2:#8b5cf6;--accent3:#06b6d4;
    --green:#10b981;--red:#ef4444;--yellow:#f59e0b;
    --text:#f1f5f9;--muted:#94a3b8;--border:#1e293b;
  }}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;min-height:100vh;overflow-x:hidden;}}
  
  /* Header */
  .header{{
    background:linear-gradient(135deg,#1e1b4b 0%,#1a1040 50%,#0f172a 100%);
    border-bottom:1px solid var(--border);
    padding:16px 32px;display:flex;align-items:center;justify-content:space-between;
    position:sticky;top:0;z-index:100;
  }}
  .header-left h1{{font-size:1.6rem;font-weight:800;
    background:linear-gradient(90deg,#818cf8,#c084fc,#38bdf8);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent}}
  .header-left p{{color:var(--muted);font-size:.85rem;margin-top:2px}}
  
  /* Navigation Tabs */
  .tabs{{
    display:flex;gap:12px;background:var(--card);padding:12px 32px;
    border-bottom:1px solid var(--border);
  }}
  .tab-btn{{
    background:transparent;border:none;color:var(--muted);font-size:.95rem;
    font-weight:600;padding:8px 16px;cursor:pointer;border-radius:8px;
    transition:all 0.2s;font-family:'Inter';
  }}
  .tab-btn:hover{{color:var(--text);background:rgba(255,255,255,0.05);}}
  .tab-btn.active{{
    background:linear-gradient(135deg,rgba(99,102,241,0.2),rgba(139,92,246,0.2));
    color:var(--accent-1);border:1px solid rgba(99,102,241,0.3);
  }}
  
  /* Slicer / Filters Bar */
  .slicer-bar{{
    display:flex;gap:20px;padding:16px 32px;background:rgba(17,24,39,0.5);
    border-bottom:1px solid var(--border);align-items:center;
  }}
  .slicer-label{{font-size:.85rem;color:var(--muted);font-weight:600;display:flex;align-items:center;gap:6px;}}
  .slicer-select{{
    background:var(--card);color:var(--text);border:1px solid var(--border);
    padding:8px 16px;border-radius:8px;font-family:'Inter';outline:none;
    min-width:180px;cursor:pointer;
  }}
  .slicer-select:focus{{border-color:var(--accent);}}

  /* Page Containers */
  .page{{display:none;animation:fadeIn 0.4s ease;}}
  .page.active{{display:block;}}
  @keyframes fadeIn{{from{{opacity:0;transform:translateY(10px);}}to{{opacity:1;transform:translateY(0);}}}}

  /* KPI Grid */
  .kpi-grid{{
    display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));
    gap:16px;padding:24px 32px 0;
  }}
  .kpi-card{{
    background:var(--card);border:1px solid var(--border);
    border-radius:16px;padding:20px;transition:transform .2s;
    position:relative;overflow:hidden;
  }}
  .kpi-card::before{{
    content:'';position:absolute;top:0;left:0;right:0;height:3px;
    background:linear-gradient(90deg,var(--accent),var(--accent2));
  }}
  .kpi-card:hover{{transform:translateY(-3px);box-shadow:0 15px 30px rgba(99,102,241,.15)}}
  .kpi-icon{{font-size:1.5rem;margin-bottom:6px}}
  .kpi-label{{font-size:.72rem;color:var(--muted);text-transform:uppercase;font-weight:600}}
  .kpi-value{{font-size:1.4rem;font-weight:800;margin:4px 0;}}
  .kpi-sub{{font-size:.75rem;color:var(--green)}}
  .kpi-sub.neg{{color:var(--red)}}

  /* Charts */
  .charts-grid{{
    display:grid;grid-template-columns:repeat(auto-fit,minmax(450px,1fr));
    gap:20px;padding:20px 32px;
  }}
  .chart-card{{
    background:var(--card);border:1px solid var(--border);
    border-radius:16px;padding:20px;
  }}
  .chart-title{{font-size:.95rem;font-weight:600;margin-bottom:12px;color:var(--text);display:flex;align-items:center;gap:8px}}
  .plotly-chart{{width:100%;height:320px;}}

  /* AI Panel */
  .insights-panel{{
    margin:20px 32px;background:linear-gradient(135deg,rgba(30,27,75,.3),rgba(26,18,48,.3));
    border:1px solid rgba(79,70,229,.4);border-radius:16px;padding:24px;
  }}
  .insights-title{{font-size:1.1rem;font-weight:700;color:var(--accent2);margin-bottom:8px}}
  .insights-text{{color:#cbd5e1;line-height:1.8;font-size:.9rem;white-space:pre-line}}

  /* Data Table */
  .data-container{{padding:24px 32px;overflow-x:auto;}}
  table{{width:100%;border-collapse:collapse;font-size:.85rem;}}
  th,td{{padding:12px;text-align:left;border-bottom:1px solid var(--border);}}
  th{{background:var(--card2);color:var(--muted);font-weight:600;position:sticky;top:0;}}
  tr:hover{{background:rgba(255,255,255,0.02);}}

</style>
</head>
<body>

<!-- Header -->
<div class="header">
  <div class="header-left">
    <h1>&#9889; Interactive Analytics - {domain}</h1>
    <p>Auto-generated &middot; {generated_at} &middot; 🤖 AI: {ai_source}</p>
  </div>
</div>

<!-- Navigation Tabs -->
<div class="tabs">
  <button class="tab-btn active" onclick="openTab('page-overview')">📊 Executive Overview</button>
  <button class="tab-btn" onclick="openTab('page-deepdive')">🔍 Deep Dive Analysis</button>
  <button class="tab-btn" onclick="openTab('page-data')">📋 Raw Data View</button>
</div>

<!-- Slicer Bar (Filters) -->
<div class="slicer-bar">
  <div class="slicer-label">🔬 Global Filters:</div>
  <select class="slicer-select" id="regionFilter" onchange="applyFilters()">
    <option value="ALL">All Regions</option>
  </select>
  <select class="slicer-select" id="categoryFilter" onchange="applyFilters()">
    <option value="ALL">All Categories</option>
  </select>
  <button class="tab-btn" onclick="resetFilters()">Reset Filters</button>
</div>

<!-- PAGE 1: Overview -->
<div id="page-overview" class="page active">
  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-icon">&#128176;</div>
      <div class="kpi-label">Total Value 1</div>
      <div class="kpi-value" id="kpi-val1">{fmt(total_sales)}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-icon">&#128201;</div>
      <div class="kpi-label">Total Value 2</div>
      <div class="kpi-value" id="kpi-val2">{fmt(total_profit)}</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-icon">&#128722;</div>
      <div class="kpi-label">Total Records</div>
      <div class="kpi-value" id="kpi-records">{total_orders:,}</div>
    </div>
  </div>

  <div class="insights-panel">
    <div class="insights-title">&#129302; AI-Generated Business Insights</div>
    <div class="insights-text">{ai_insights}</div>
  </div>
  
  <div class="charts-grid">
    <div class="chart-card">
      <div class="chart-title">Trend Overview</div>
      <div id="monthlyChart" class="plotly-chart"></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">Distribution</div>
      <div id="regionChart" class="plotly-chart"></div>
    </div>
  </div>
</div>

<!-- PAGE 2: Deep Dive -->
<div id="page-deepdive" class="page">
  <div class="charts-grid" style="grid-template-columns:1fr;">
    <div class="chart-card">
      <div class="chart-title">Top Items Performance</div>
      <div id="productChart" class="plotly-chart" style="height:500px;"></div>
    </div>
    <div class="chart-card">
      <div class="chart-title">Category Breakdown</div>
      <div id="categoryChart" class="plotly-chart"></div>
    </div>
  </div>
</div>

<!-- PAGE 3: Raw Data -->
<div id="page-data" class="page">
  <div class="data-container">
    <table id="dataTable">
      <thead>
        <tr id="tableHead"></tr>
      </thead>
      <tbody id="tableBody"></tbody>
    </table>
  </div>
</div>

<script>
// Tab Logic
function openTab(tabId) {{
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById(tabId).classList.add('active');
  event.currentTarget.classList.add('active');
  // Trigger resize so Plotly charts render correctly if they were hidden
  window.dispatchEvent(new Event('resize'));
}}

// --- Interactive Data Logic ---
const rawData = {raw_data_json};
const DARK = {{
  paper_bgcolor:'#111827', plot_bgcolor:'#111827',
  font:{{color:'#f1f5f9',family:'Inter'}},
  gridcolor:'#1e293b', zerolinecolor:'#1e293b'
}};
const COLORS = ['#6366f1','#8b5cf6','#06b6d4','#10b981','#f59e0b','#ef4444','#ec4899','#14b8a6','#f97316','#a855f7'];

// Detect dynamic columns based on domain
let val1Col = "sales";
let val2Col = "profit";
let regionCol = "region";
let catCol = "category";
let prodCol = "product";
let dateCol = "month";

if(rawData.length > 0) {{
  const keys = Object.keys(rawData[0]);
  if(!keys.includes("sales") && keys.includes("volume")) val1Col = "volume";
  if(!keys.includes("profit") && keys.includes("pnl")) val2Col = "pnl";
  if(!keys.includes("profit") && keys.includes("recovery_rate")) val2Col = "recovery_rate";
  
  // Populate Slicers
  const regions = [...new Set(rawData.map(d=>d[regionCol]))].filter(Boolean).sort();
  const categories = [...new Set(rawData.map(d=>d[catCol]))].filter(Boolean).sort();
  
  const rSelect = document.getElementById("regionFilter");
  regions.forEach(r => rSelect.add(new Option(r, r)));
  
  const cSelect = document.getElementById("categoryFilter");
  categories.forEach(c => cSelect.add(new Option(c, c)));
  
  // Initial render
  renderAll(rawData);
}}

function resetFilters() {{
  document.getElementById("regionFilter").value = "ALL";
  document.getElementById("categoryFilter").value = "ALL";
  applyFilters();
}}

function applyFilters() {{
  const rVal = document.getElementById("regionFilter").value;
  const cVal = document.getElementById("categoryFilter").value;
  
  let filtered = rawData;
  if(rVal !== "ALL") filtered = filtered.filter(d => d[regionCol] == rVal);
  if(cVal !== "ALL") filtered = filtered.filter(d => d[catCol] == cVal);
  
  renderAll(filtered);
}}

function renderAll(data) {{
  // Update KPIs
  const tVal1 = data.reduce((sum, d) => sum + (Number(d[val1Col])||0), 0);
  const tVal2 = data.reduce((sum, d) => sum + (Number(d[val2Col])||0), 0);
  
  const formatNum = (num) => {{
    if(num>=1e7) return (num/1e7).toFixed(1)+'Cr';
    if(num>=1e5) return (num/1e5).toFixed(1)+'L';
    if(num>=1e3) return (num/1e3).toFixed(1)+'K';
    return num.toFixed(0);
  }};
  
  document.getElementById("kpi-val1").innerText = formatNum(tVal1);
  document.getElementById("kpi-val2").innerText = formatNum(tVal2);
  document.getElementById("kpi-records").innerText = data.length.toLocaleString();

  // Aggregate functions
  const agg = (key) => {{
    const res = {{}};
    data.forEach(d => {{
      const k = d[key] || "Unknown";
      res[k] = (res[k]||0) + (Number(d[val1Col])||0);
    }});
    return res;
  }};

  // Render Region Pie
  const regData = agg(regionCol);
  Plotly.react('regionChart', [{{
    labels: Object.keys(regData), values: Object.values(regData),
    type: 'pie', hole: 0.5, marker: {{colors: COLORS}},
    textfont: {{color: 'white'}}, hoverinfo: 'label+value'
  }}], {{...DARK, margin:{{t:10,b:10,l:10,r:10}}, showlegend:true}});

  // Click event on Region Pie -> updates Slicer
  document.getElementById('regionChart').on('plotly_click', function(data){{
      const clickedRegion = data.points[0].label;
      document.getElementById("regionFilter").value = clickedRegion;
      applyFilters();
  }});

  // Render Month Line
  const mData = agg(dateCol);
  // Sort months properly if possible, but for simplicity rely on agg order or keep as is
  Plotly.react('monthlyChart', [{{
    x: Object.keys(mData), y: Object.values(mData),
    type: 'scatter', mode: 'lines+markers',
    line: {{color: '#6366f1', width: 3, shape: 'spline'}},
    marker: {{size: 8, color: '#8b5cf6'}}, fill: 'tozeroy', fillcolor: 'rgba(99,102,241,0.1)'
  }}], {{...DARK, margin:{{t:20,l:50,r:20,b:40}}, xaxis:{{...DARK}}, yaxis:{{...DARK}}}});

  // Render Category Bar
  const cData = agg(catCol);
  Plotly.react('categoryChart', [{{
    x: Object.keys(cData), y: Object.values(cData),
    type: 'bar', marker: {{color: COLORS, opacity: 0.9}}
  }}], {{...DARK, margin:{{t:20,l:50,r:20,b:50}}, xaxis:{{...DARK}}, yaxis:{{...DARK}}}});

  // Render Top 10 Products
  const pData = agg(prodCol);
  const sortedP = Object.entries(pData).sort((a,b)=>b[1]-a[1]).slice(0, 15);
  Plotly.react('productChart', [{{
    y: sortedP.map(x=>x[0]).reverse(), x: sortedP.map(x=>x[1]).reverse(),
    type: 'bar', orientation: 'h', marker: {{color: '#06b6d4'}}
  }}], {{...DARK, margin:{{t:20,l:150,r:20,b:40}}, xaxis:{{...DARK}}, yaxis:{{...DARK}}}});

  // Render Data Table (first 100 rows max to avoid lag)
  if(data.length > 0) {{
    const tableHead = document.getElementById("tableHead");
    const tableBody = document.getElementById("tableBody");
    
    // Headers
    const headers = Object.keys(data[0]);
    tableHead.innerHTML = headers.map(h => `<th>${{h.toUpperCase().replace('_',' ')}}</th>`).join('');
    
    // Rows
    const rowsHtml = data.slice(0, 100).map(row => 
      `<tr>${{headers.map(h => `<td>${{row[h]}}</td>`).join('')}}</tr>`
    ).join('');
    tableBody.innerHTML = rowsHtml;
  }}
}}

</script>
</body>
</html>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    url = "file:///" + str(output_path).replace("\\", "/")
    print(f"  Dashboard ready -> {output_path}")
    print(f"  Open in browser: {url}\n")
    return str(output_path)


if __name__ == "__main__":
    create_dashboard()
