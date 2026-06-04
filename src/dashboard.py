"""
Premium Interactive HTML Dashboard Generator
Single-page Power BI-style layout with Slicers, Cross-Filtering, and AI Insights.
All charts on ONE page. Opens in any browser -- NO login needed.
"""
import sys
import json
import os
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
    domain        = data.get("domain", os.environ.get("DATA_DOMAIN", "Sales"))
    top_product   = data.get("top_product", "N/A")
    top_region    = data.get("top_region", "N/A")
    best_month    = data.get("best_month", "N/A")

    def fmt(v):
        v = float(v)
        if v >= 1_00_00_000: return f"{v/1_00_00_000:.1f}Cr"
        if v >= 1_00_000:    return f"{v/1_00_000:.1f}L"
        if v >= 1_000:       return f"{v/1_000:.1f}K"
        return f"{v:,.0f}"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>AI Analytics Dashboard - {domain}</title>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet"/>
<style>
  :root{{
    --bg:#060a13;--surface:#0d1117;--card:#111827;--card-hover:#161f2e;
    --accent:#818cf8;--accent2:#a78bfa;--accent3:#38bdf8;--accent4:#c084fc;
    --green:#34d399;--red:#f87171;--yellow:#fbbf24;--cyan:#22d3ee;--pink:#f472b6;
    --text:#f1f5f9;--text2:#e2e8f0;--muted:#64748b;--border:rgba(255,255,255,0.06);
    --glow:rgba(99,102,241,0.15);
  }}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{
    background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;
    min-height:100vh;overflow-x:hidden;
    background-image:radial-gradient(ellipse at 20% 0%,rgba(99,102,241,0.07) 0%,transparent 50%),
                     radial-gradient(ellipse at 80% 100%,rgba(56,189,248,0.05) 0%,transparent 50%);
  }}
  
  /* ── Header ── */
  .header{{
    background:linear-gradient(135deg,rgba(15,10,40,0.95),rgba(13,17,23,0.95));
    backdrop-filter:blur(20px);
    border-bottom:1px solid var(--border);
    padding:14px 28px;display:flex;align-items:center;justify-content:space-between;
    position:sticky;top:0;z-index:100;
  }}
  .header-left{{display:flex;align-items:center;gap:14px}}
  .logo-icon{{
    width:38px;height:38px;border-radius:10px;
    background:linear-gradient(135deg,#6366f1,#8b5cf6);
    display:flex;align-items:center;justify-content:center;font-size:1.2rem;
    box-shadow:0 4px 15px rgba(99,102,241,0.3);
  }}
  .header-left h1{{font-size:1.3rem;font-weight:800;color:var(--text)}}
  .header-left h1 span{{
    background:linear-gradient(90deg,var(--accent),var(--accent4),var(--accent3));
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  }}
  .header-meta{{display:flex;gap:16px;align-items:center}}
  .meta-badge{{
    font-size:.72rem;padding:4px 10px;border-radius:20px;font-weight:600;
    background:rgba(99,102,241,0.12);color:var(--accent);border:1px solid rgba(99,102,241,0.2);
  }}
  .meta-badge.ai{{background:rgba(52,211,153,0.12);color:var(--green);border-color:rgba(52,211,153,0.2)}}
  .meta-badge.time{{background:rgba(100,116,139,0.12);color:var(--muted);border-color:rgba(100,116,139,0.15)}}

  /* ── Slicer Bar ── */
  .slicer-bar{{
    display:flex;gap:14px;padding:12px 28px;
    background:rgba(13,17,23,0.6);backdrop-filter:blur(10px);
    border-bottom:1px solid var(--border);align-items:center;flex-wrap:wrap;
  }}
  .slicer-group{{display:flex;align-items:center;gap:6px}}
  .slicer-group label{{font-size:.72rem;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:.5px}}
  .slicer-select{{
    background:var(--card);color:var(--text);border:1px solid var(--border);
    padding:7px 14px;border-radius:8px;font-family:'Inter';outline:none;font-size:.82rem;
    min-width:160px;cursor:pointer;transition:all .2s;
  }}
  .slicer-select:hover{{border-color:rgba(99,102,241,0.3)}}
  .slicer-select:focus{{border-color:var(--accent);box-shadow:0 0 0 2px var(--glow)}}
  .reset-btn{{
    background:transparent;border:1px solid var(--border);color:var(--muted);
    padding:7px 14px;border-radius:8px;font-size:.8rem;cursor:pointer;font-family:'Inter';
    transition:all .2s;
  }}
  .reset-btn:hover{{background:rgba(255,255,255,0.04);color:var(--text)}}

  /* ── Main Layout ── */
  .main-content{{padding:20px 28px;}}

  /* ── KPI Grid ── */
  .kpi-grid{{
    display:grid;grid-template-columns:repeat(6,1fr);gap:14px;margin-bottom:20px;
  }}
  .kpi-card{{
    background:var(--card);border:1px solid var(--border);
    border-radius:14px;padding:18px;position:relative;overflow:hidden;
    transition:all .25s ease;
  }}
  .kpi-card:hover{{transform:translateY(-2px);border-color:rgba(99,102,241,0.2);box-shadow:0 8px 25px rgba(0,0,0,0.3)}}
  .kpi-card::after{{
    content:'';position:absolute;top:0;left:0;right:0;height:2px;
    background:linear-gradient(90deg,var(--accent),var(--accent4));opacity:0;transition:opacity .2s;
  }}
  .kpi-card:hover::after{{opacity:1}}
  .kpi-top{{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}}
  .kpi-icon{{font-size:1.6rem;filter:drop-shadow(0 2px 4px rgba(0,0,0,0.3))}}
  .kpi-trend{{font-size:.7rem;font-weight:700;padding:2px 6px;border-radius:4px}}
  .kpi-trend.up{{background:rgba(52,211,153,0.12);color:var(--green)}}
  .kpi-trend.down{{background:rgba(248,113,113,0.12);color:var(--red)}}
  .kpi-label{{font-size:.68rem;color:var(--muted);text-transform:uppercase;letter-spacing:.8px;font-weight:600}}
  .kpi-value{{font-size:1.5rem;font-weight:800;margin:4px 0 2px;letter-spacing:-.5px}}
  .kpi-sub{{font-size:.72rem;color:var(--muted)}}

  /* ── Charts Grid ── */
  .charts-row{{display:grid;gap:16px;margin-bottom:16px}}
  .charts-row.two{{grid-template-columns:1.4fr 1fr}}
  .charts-row.three{{grid-template-columns:1fr 1fr 1fr}}
  .charts-row.one{{grid-template-columns:1fr}}
  
  .chart-card{{
    background:var(--card);border:1px solid var(--border);
    border-radius:14px;padding:18px;transition:all .25s ease;position:relative;
  }}
  .chart-card:hover{{border-color:rgba(99,102,241,0.15)}}
  .chart-header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}}
  .chart-title{{font-size:.88rem;font-weight:700;color:var(--text2);display:flex;align-items:center;gap:8px}}
  .chart-subtitle{{font-size:.7rem;color:var(--muted)}}
  .plotly-chart{{width:100%;height:300px}}

  /* ── AI Insights (Sidebar-style within a chart row) ── */
  .ai-panel{{
    background:linear-gradient(160deg,rgba(99,102,241,0.06),rgba(139,92,246,0.04),rgba(56,189,248,0.03));
    border:1px solid rgba(99,102,241,0.15);border-radius:14px;padding:20px;
    position:relative;overflow:hidden;
  }}
  .ai-panel::before{{
    content:'';position:absolute;top:0;left:0;width:3px;height:100%;
    background:linear-gradient(180deg,var(--accent),var(--accent4),var(--accent3));
    border-radius:3px;
  }}
  .ai-badge{{
    display:inline-flex;align-items:center;gap:5px;font-size:.68rem;font-weight:700;
    padding:3px 8px;border-radius:20px;margin-bottom:10px;text-transform:uppercase;letter-spacing:.5px;
    background:rgba(52,211,153,0.1);color:var(--green);border:1px solid rgba(52,211,153,0.2);
  }}
  .ai-title{{font-size:1rem;font-weight:700;color:var(--text);margin-bottom:10px}}
  .ai-text{{color:var(--text2);line-height:1.75;font-size:.84rem;white-space:pre-line;opacity:0.9}}

  /* ── Data Table ── */
  .table-section{{margin-top:16px}}
  .table-header{{
    display:flex;align-items:center;justify-content:space-between;
    padding:14px 18px;background:var(--card);border:1px solid var(--border);
    border-radius:14px 14px 0 0;
  }}
  .table-title{{font-size:.9rem;font-weight:700;color:var(--text2)}}
  .table-count{{font-size:.75rem;color:var(--muted)}}
  .table-wrap{{
    overflow-x:auto;background:var(--card);
    border:1px solid var(--border);border-top:none;border-radius:0 0 14px 14px;
    max-height:400px;overflow-y:auto;
  }}
  table{{width:100%;border-collapse:collapse;font-size:.8rem}}
  th{{
    padding:10px 14px;text-align:left;color:var(--muted);font-weight:600;font-size:.7rem;
    text-transform:uppercase;letter-spacing:.5px;background:var(--surface);
    position:sticky;top:0;z-index:1;border-bottom:1px solid var(--border);
  }}
  td{{padding:9px 14px;border-bottom:1px solid var(--border);color:var(--text2)}}
  tr:hover td{{background:rgba(99,102,241,0.03)}}
  
  /* ── Footer ── */
  .footer{{
    text-align:center;padding:20px;color:var(--muted);font-size:.75rem;
    border-top:1px solid var(--border);margin-top:30px;
  }}
  .footer a{{color:var(--accent);text-decoration:none}}

  /* ── Responsive ── */
  @media(max-width:1200px){{
    .kpi-grid{{grid-template-columns:repeat(3,1fr)}}
    .charts-row.two,.charts-row.three{{grid-template-columns:1fr}}
  }}
  @media(max-width:768px){{
    .kpi-grid{{grid-template-columns:repeat(2,1fr)}}
    .slicer-bar{{flex-direction:column;align-items:stretch}}
    .header{{flex-direction:column;gap:10px;align-items:flex-start}}
  }}
</style>
</head>
<body>

<!-- ══════ HEADER ══════ -->
<div class="header">
  <div class="header-left">
    <div class="logo-icon">&#9889;</div>
    <h1><span>AI Analytics</span> &mdash; {domain}</h1>
  </div>
  <div class="header-meta">
    <span class="meta-badge ai">&#129302; AI: {ai_source}</span>
    <span class="meta-badge">&#128202; {total_orders:,} Records</span>
    <span class="meta-badge time">{generated_at}</span>
  </div>
</div>

<!-- ══════ SLICER BAR ══════ -->
<div class="slicer-bar">
  <div class="slicer-group">
    <label>Region</label>
    <select class="slicer-select" id="regionFilter" onchange="applyFilters()">
      <option value="ALL">All Regions</option>
    </select>
  </div>
  <div class="slicer-group">
    <label>Category</label>
    <select class="slicer-select" id="categoryFilter" onchange="applyFilters()">
      <option value="ALL">All Categories</option>
    </select>
  </div>
  <div class="slicer-group">
    <label>Month</label>
    <select class="slicer-select" id="monthFilter" onchange="applyFilters()">
      <option value="ALL">All Months</option>
    </select>
  </div>
  <button class="reset-btn" onclick="resetFilters()">&#x21bb; Reset All</button>
</div>

<!-- ══════ MAIN CONTENT (Single Scrollable Page) ══════ -->
<div class="main-content">

  <!-- KPI Cards -->
  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-top"><div class="kpi-icon">&#128176;</div><span class="kpi-trend up">&#9650;</span></div>
      <div class="kpi-label">Total Revenue</div>
      <div class="kpi-value" id="kpi-revenue">{fmt(total_sales)}</div>
      <div class="kpi-sub">All-time cumulative</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-top"><div class="kpi-icon">&#128200;</div><span class="kpi-trend {'up' if profit_margin >= 15 else 'down'}">{'&#9650;' if profit_margin >= 15 else '&#9660;'} {profit_margin:.1f}%</span></div>
      <div class="kpi-label">Net Profit</div>
      <div class="kpi-value" id="kpi-profit">{fmt(total_profit)}</div>
      <div class="kpi-sub">Margin: {profit_margin:.1f}%</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-top"><div class="kpi-icon">&#128230;</div></div>
      <div class="kpi-label">Total Orders</div>
      <div class="kpi-value" id="kpi-orders">{total_orders:,}</div>
      <div class="kpi-sub">Avg: Rs.{fmt(avg_order)}/order</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-top"><div class="kpi-icon">&#127942;</div></div>
      <div class="kpi-label">Top Product</div>
      <div class="kpi-value" style="font-size:1rem" id="kpi-top-prod">{top_product}</div>
      <div class="kpi-sub">Highest revenue item</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-top"><div class="kpi-icon">&#127759;</div></div>
      <div class="kpi-label">Top Region</div>
      <div class="kpi-value" style="font-size:1.1rem" id="kpi-top-region">{top_region}</div>
      <div class="kpi-sub">Best performing area</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-top"><div class="kpi-icon">&#128197;</div></div>
      <div class="kpi-label">Peak Month</div>
      <div class="kpi-value" style="font-size:1.1rem" id="kpi-best-month">{best_month}</div>
      <div class="kpi-sub">Highest sales month</div>
    </div>
  </div>

  <!-- Row 1: Monthly Trend + Region Donut -->
  <div class="charts-row two">
    <div class="chart-card">
      <div class="chart-header">
        <div class="chart-title">&#128200; Monthly Sales Trend</div>
        <div class="chart-subtitle">Revenue over time</div>
      </div>
      <div id="monthlyChart" class="plotly-chart"></div>
    </div>
    <div class="chart-card">
      <div class="chart-header">
        <div class="chart-title">&#127759; Region Distribution</div>
        <div class="chart-subtitle">Click to drill-down</div>
      </div>
      <div id="regionChart" class="plotly-chart"></div>
    </div>
  </div>

  <!-- Row 2: Top Products + Category Bar + AI Insights -->
  <div class="charts-row three">
    <div class="chart-card">
      <div class="chart-header">
        <div class="chart-title">&#127942; Top Products</div>
        <div class="chart-subtitle">By revenue</div>
      </div>
      <div id="productChart" class="plotly-chart" style="height:340px"></div>
    </div>
    <div class="chart-card">
      <div class="chart-header">
        <div class="chart-title">&#128230; Category Breakdown</div>
        <div class="chart-subtitle">Revenue per category</div>
      </div>
      <div id="categoryChart" class="plotly-chart" style="height:340px"></div>
    </div>
    <div class="ai-panel">
      <div class="ai-badge">&#129302; {ai_source}</div>
      <div class="ai-title">AI-Generated Insights</div>
      <div class="ai-text">{ai_insights}</div>
    </div>
  </div>

  <!-- Row 3: Profit vs Sales Scatter + Payment Mode -->
  <div class="charts-row two">
    <div class="chart-card">
      <div class="chart-header">
        <div class="chart-title">&#128201; Profit vs Revenue by Product</div>
        <div class="chart-subtitle">Bubble size = quantity</div>
      </div>
      <div id="scatterChart" class="plotly-chart"></div>
    </div>
    <div class="chart-card">
      <div class="chart-header">
        <div class="chart-title">&#128179; Payment Mode</div>
        <div class="chart-subtitle">Distribution by mode</div>
      </div>
      <div id="paymentChart" class="plotly-chart"></div>
    </div>
  </div>

  <!-- Data Table -->
  <div class="table-section">
    <div class="table-header">
      <div class="table-title">&#128203; Data Explorer</div>
      <div class="table-count" id="tableCount">Showing 0 rows</div>
    </div>
    <div class="table-wrap">
      <table>
        <thead><tr id="tableHead"></tr></thead>
        <tbody id="tableBody"></tbody>
      </table>
    </div>
  </div>
</div>

<!-- Footer -->
<div class="footer">
  Built by <strong>Abhishek Maheshwari</strong> &middot; Mentor: <a href="https://www.linkedin.com/in/harshit-varshney-google-ibm-and-hubspot-certified-28b78818b/" target="_blank">Harshit Varshney</a> &middot; AI Analytics MCP Pipeline &middot; No Power BI Login Required
</div>

<script>
// ══════ Interactive Data Engine ══════
const rawData = {raw_data_json};
const LAYOUT = {{
  paper_bgcolor:'transparent',plot_bgcolor:'transparent',
  font:{{color:'#e2e8f0',family:'Inter',size:11}},
  margin:{{t:10,b:35,l:45,r:15}},
  xaxis:{{gridcolor:'rgba(255,255,255,0.04)',zerolinecolor:'rgba(255,255,255,0.04)'}},
  yaxis:{{gridcolor:'rgba(255,255,255,0.04)',zerolinecolor:'rgba(255,255,255,0.04)'}},
  showlegend:false,
  hoverlabel:{{bgcolor:'#1e293b',font:{{color:'#f1f5f9',family:'Inter'}}}},
}};
const COLORS = ['#818cf8','#a78bfa','#38bdf8','#34d399','#fbbf24','#f87171','#f472b6','#22d3ee','#fb923c','#c084fc'];

let val1Col="sales",val2Col="profit",regionCol="region",catCol="category",prodCol="product",dateCol="month",qtyCol="quantity",payCol="payment_mode";

if(rawData.length>0){{
  const k=Object.keys(rawData[0]);
  // Auto-detect columns for any domain
  if(!k.includes("sales")){{
    if(k.includes("volume")) val1Col="volume";
    else if(k.includes("cost")) val1Col="cost";
    else if(k.includes("bill_amount")) val1Col="bill_amount";
    else if(k.includes("revenue")) val1Col="revenue";
  }}
  if(!k.includes("profit")){{
    if(k.includes("pnl")) val2Col="pnl";
    else if(k.includes("recovery_rate")) val2Col="recovery_rate";
    else if(k.includes("net_gain")) val2Col="net_gain";
  }}
  if(!k.includes("region")){{
    if(k.includes("hospital")) regionCol="hospital";
    else if(k.includes("exchange")) regionCol="exchange";
    else if(k.includes("city")) regionCol="city";
  }}
  if(!k.includes("category")){{
    if(k.includes("department")) catCol="department";
    else if(k.includes("asset_class")) catCol="asset_class";
    else if(k.includes("sector")) catCol="sector";
  }}
  if(!k.includes("product")){{
    if(k.includes("condition")) prodCol="condition";
    else if(k.includes("ticker")) prodCol="ticker";
    else if(k.includes("treatment")) prodCol="treatment";
  }}
  if(!k.includes("quantity")){{
    if(k.includes("patients")) qtyCol="patients";
    else if(k.includes("shares")) qtyCol="shares";
  }}
  if(!k.includes("payment_mode")){{
    if(k.includes("ship_mode")) payCol="ship_mode";
    else if(k.includes("type")) payCol="type";
  }}

  // Populate slicers
  const addOpts = (id, col) => {{
    const vals=[...new Set(rawData.map(d=>d[col]))].filter(Boolean).sort();
    const sel=document.getElementById(id);
    vals.forEach(v=>sel.add(new Option(v,v)));
  }};
  addOpts("regionFilter",regionCol);
  addOpts("categoryFilter",catCol);
  addOpts("monthFilter",dateCol);

  renderAll(rawData);
}}

function resetFilters(){{
  document.getElementById("regionFilter").value="ALL";
  document.getElementById("categoryFilter").value="ALL";
  document.getElementById("monthFilter").value="ALL";
  applyFilters();
}}
function applyFilters(){{
  let f=rawData;
  const rv=document.getElementById("regionFilter").value;
  const cv=document.getElementById("categoryFilter").value;
  const mv=document.getElementById("monthFilter").value;
  if(rv!=="ALL") f=f.filter(d=>d[regionCol]==rv);
  if(cv!=="ALL") f=f.filter(d=>d[catCol]==cv);
  if(mv!=="ALL") f=f.filter(d=>d[dateCol]==mv);
  renderAll(f);
}}

function renderAll(data){{
  const fmt=n=>{{if(n>=1e7)return(n/1e7).toFixed(1)+'Cr';if(n>=1e5)return(n/1e5).toFixed(1)+'L';if(n>=1e3)return(n/1e3).toFixed(1)+'K';return n.toLocaleString()}};
  const sum=(arr,col)=>arr.reduce((s,d)=>s+(Number(d[col])||0),0);
  const agg=(arr,key,valCol)=>{{const r={{}};arr.forEach(d=>{{const k=d[key]||'Unknown';r[k]=(r[k]||0)+(Number(d[valCol||val1Col])||0)}});return r}};

  const tRev=sum(data,val1Col), tProf=sum(data,val2Col), tOrd=data.length;
  document.getElementById("kpi-revenue").innerText=fmt(tRev);
  document.getElementById("kpi-profit").innerText=fmt(tProf);
  document.getElementById("kpi-orders").innerText=tOrd.toLocaleString();

  // ── Monthly Trend (Area Chart) ──
  const mD=agg(data,dateCol);
  const monthOrder=['January','February','March','April','May','June','July','August','September','October','November','December'];
  const sortedMonths=Object.keys(mD).sort((a,b)=>monthOrder.indexOf(a)-monthOrder.indexOf(b));
  Plotly.react('monthlyChart',[{{
    x:sortedMonths,y:sortedMonths.map(m=>mD[m]),type:'scatter',mode:'lines+markers',
    line:{{color:'#818cf8',width:3,shape:'spline'}},marker:{{size:7,color:'#a78bfa'}},
    fill:'tozeroy',fillcolor:'rgba(129,140,248,0.08)'
  }}],{{...LAYOUT}},{{responsive:true,displayModeBar:false}});

  // ── Region Donut ──
  const rD=agg(data,regionCol);
  Plotly.react('regionChart',[{{
    labels:Object.keys(rD),values:Object.values(rD),type:'pie',hole:0.55,
    marker:{{colors:COLORS}},textfont:{{color:'white',size:11}},
    textposition:'inside',textinfo:'label+percent',hoverinfo:'label+value'
  }}],{{...LAYOUT,margin:{{t:5,b:5,l:5,r:5}},showlegend:false}},{{responsive:true,displayModeBar:false}});
  // Click drilldown on pie
  document.getElementById('regionChart').on('plotly_click',d=>{{
    document.getElementById("regionFilter").value=d.points[0].label;applyFilters();
  }});

  // ── Top Products (Horizontal Bar) ──
  const pD=agg(data,prodCol);
  const sP=Object.entries(pD).sort((a,b)=>b[1]-a[1]).slice(0,12);
  Plotly.react('productChart',[{{
    y:sP.map(x=>x[0]).reverse(),x:sP.map(x=>x[1]).reverse(),
    type:'bar',orientation:'h',
    marker:{{color:sP.map((_,i)=>COLORS[i%COLORS.length]).reverse(),
    cornerradius:4}},
  }}],{{...LAYOUT,margin:{{t:5,b:25,l:120,r:15}}}},{{responsive:true,displayModeBar:false}});

  // ── Category Bar ──
  const cD=agg(data,catCol);
  Plotly.react('categoryChart',[{{
    x:Object.keys(cD),y:Object.values(cD),type:'bar',
    marker:{{color:Object.keys(cD).map((_,i)=>COLORS[i%COLORS.length]),cornerradius:6,opacity:0.9}}
  }}],{{...LAYOUT,margin:{{t:5,l:50,r:15,b:60}},xaxis:{{...LAYOUT.xaxis,tickangle:-30}}}},{{responsive:true,displayModeBar:false}});

  // ── Profit vs Revenue Scatter ──
  const prodAgg={{}};
  data.forEach(d=>{{
    const p=d[prodCol]||'Unknown';
    if(!prodAgg[p]) prodAgg[p]={{rev:0,prof:0,qty:0}};
    prodAgg[p].rev+=(Number(d[val1Col])||0);
    prodAgg[p].prof+=(Number(d[val2Col])||0);
    prodAgg[p].qty+=(Number(d[qtyCol])||0);
  }});
  const scatterEntries=Object.entries(prodAgg).filter(([_,v])=>v.rev>0);
  Plotly.react('scatterChart',[{{
    x:scatterEntries.map(e=>e[1].rev),y:scatterEntries.map(e=>e[1].prof),
    text:scatterEntries.map(e=>e[0]),mode:'markers',type:'scatter',
    marker:{{size:scatterEntries.map(e=>Math.max(8,Math.min(40,e[1].qty/5))),
    color:scatterEntries.map((_,i)=>COLORS[i%COLORS.length]),opacity:0.8,
    line:{{width:1,color:'rgba(255,255,255,0.1)'}}}},
    hovertemplate:'<b>%{{text}}</b><br>Revenue: %{{x:,.0f}}<br>Profit: %{{y:,.0f}}<extra></extra>'
  }}],{{...LAYOUT}},{{responsive:true,displayModeBar:false}});

  // ── Payment Mode Donut ──
  const pmD=agg(data,payCol);
  Plotly.react('paymentChart',[{{
    labels:Object.keys(pmD),values:Object.values(pmD),type:'pie',hole:0.5,
    marker:{{colors:['#38bdf8','#34d399','#fbbf24','#f87171','#c084fc','#f472b6']}},
    textfont:{{color:'white',size:10}},textposition:'inside',textinfo:'label+percent'
  }}],{{...LAYOUT,margin:{{t:5,b:5,l:5,r:5}},showlegend:false}},{{responsive:true,displayModeBar:false}});

  // ── Data Table ──
  if(data.length>0){{
    const headers=Object.keys(data[0]);
    document.getElementById("tableHead").innerHTML=headers.map(h=>`<th>${{h.replace(/_/g,' ').toUpperCase()}}</th>`).join('');
    const show=data.slice(0,150);
    document.getElementById("tableBody").innerHTML=show.map(row=>`<tr>${{headers.map(h=>`<td>${{row[h]!==null&&row[h]!==undefined?row[h]:''}}</td>`).join('')}}</tr>`).join('');
    document.getElementById("tableCount").innerText=`Showing ${{show.length}} of ${{data.length}} rows`;
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
