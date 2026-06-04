"""
Beautiful HTML Dashboard Generator
Creates an interactive dark-mode dashboard replacing Power BI.
Uses Plotly for charts. Opens in any browser -- NO login needed.
"""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import INSIGHTS_JSON, DASHBOARD_HTML


def create_dashboard(insights_path=None, output_path=None) -> str:
    insights_path = insights_path or INSIGHTS_JSON
    output_path   = output_path   or DASHBOARD_HTML

    print(f"\n{'='*50}")
    print("  DASHBOARD GENERATION STARTED")
    print(f"{'='*50}")

    with open(insights_path, encoding="utf-8") as f:
        data = json.load(f)

    from datetime import datetime
    generated_at  = datetime.now().strftime("%d %b %Y, %I:%M %p")
    total_sales   = data.get("total_sales",  0)
    total_profit  = data.get("total_profit", 0)
    total_orders  = data.get("total_orders", 0)
    profit_margin = data.get("profit_margin", 0)
    avg_order     = round(total_sales / total_orders, 0) if total_orders else 0
    ai_source     = data.get("ai_insights_source", "Rule-Based")
    ai_insights   = data.get("ai_insights", "No insights available.")

    def fmt(v):
        v = float(v)
        if v >= 1_00_00_000: return f"{v/1_00_00_000:.1f}Cr"
        if v >= 1_00_000:    return f"{v/1_00_000:.1f}L"
        if v >= 1_000:       return f"{v/1_000:.1f}K"
        return f"{v:,.0f}"

    # Serialize chart data
    monthly_json  = json.dumps(data.get("monthly_trend",  {}))
    products_json = json.dumps(data.get("top_products",   {}))
    region_json   = json.dumps(data.get("region_sales",   {}))
    category_json = json.dumps(data.get("category_sales", {}))

    profit_class  = "" if profit_margin >= 0 else "neg"

    # ── Build HTML (CSS braces doubled to escape from .format) ─────────
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>AI Sales Analytics Dashboard</title>
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
  body{{background:var(--bg);color:var(--text);font-family:'Inter',sans-serif;min-height:100vh}}
  .header{{
    background:linear-gradient(135deg,#1e1b4b 0%,#1a1040 50%,#0f172a 100%);
    border-bottom:1px solid var(--border);
    padding:24px 32px;display:flex;align-items:center;justify-content:space-between;
  }}
  .header-left h1{{font-size:1.8rem;font-weight:800;
    background:linear-gradient(90deg,#818cf8,#c084fc,#38bdf8);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent}}
  .header-left p{{color:var(--muted);font-size:.85rem;margin-top:4px}}
  .ai-badge{{
    background:linear-gradient(135deg,var(--accent),var(--accent2));
    padding:6px 16px;border-radius:20px;font-size:.78rem;font-weight:600;
    color:white;animation:pulse 2s infinite;
  }}
  @keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.7}}}}
  .kpi-grid{{
    display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));
    gap:16px;padding:24px 32px 0;
  }}
  .kpi-card{{
    background:var(--card);border:1px solid var(--border);
    border-radius:16px;padding:20px;
    transition:transform .2s,box-shadow .2s;position:relative;overflow:hidden;
  }}
  .kpi-card::before{{
    content:'';position:absolute;top:0;left:0;right:0;height:3px;
    background:linear-gradient(90deg,var(--accent),var(--accent2));
  }}
  .kpi-card:hover{{transform:translateY(-4px);box-shadow:0 20px 40px rgba(99,102,241,.2)}}
  .kpi-icon{{font-size:1.6rem;margin-bottom:8px}}
  .kpi-label{{font-size:.72rem;color:var(--muted);text-transform:uppercase;
    letter-spacing:.06em;font-weight:600}}
  .kpi-value{{font-size:1.5rem;font-weight:800;margin:6px 0;
    background:linear-gradient(135deg,#f1f5f9,#94a3b8);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent}}
  .kpi-sub{{font-size:.78rem;color:var(--green)}}
  .kpi-sub.neg{{color:var(--red)}}
  .charts-grid{{
    display:grid;grid-template-columns:repeat(auto-fit,minmax(460px,1fr));
    gap:20px;padding:20px 32px;
  }}
  .chart-card{{
    background:var(--card);border:1px solid var(--border);
    border-radius:16px;padding:20px;
  }}
  .chart-title{{font-size:1rem;font-weight:600;color:var(--text);
    margin-bottom:14px;display:flex;align-items:center;gap:8px}}
  .chart-title span{{color:var(--accent3);font-size:1.1rem}}
  .insights-panel{{
    margin:0 32px 32px;
    background:linear-gradient(135deg,rgba(30,27,75,.15),rgba(26,18,48,.15));
    border:1px solid rgba(79,70,229,.3);border-radius:16px;padding:24px;
  }}
  .insights-title{{font-size:1.1rem;font-weight:700;
    background:linear-gradient(90deg,#818cf8,#c084fc);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    margin-bottom:8px}}
  .insights-source{{
    display:inline-block;background:#1e293b;border:1px solid var(--border);
    border-radius:20px;padding:4px 14px;font-size:.72rem;color:var(--accent3);
    margin-bottom:16px;font-weight:600;
  }}
  .insights-text{{color:#cbd5e1;line-height:1.9;font-size:.9rem;white-space:pre-line}}
  .footer{{text-align:center;padding:16px;color:var(--muted);font-size:.78rem;
    border-top:1px solid var(--border)}}
  .plotly-chart{{width:100%;height:320px}}
</style>
</head>
<body>

<div class="header">
  <div class="header-left">
    <h1>&#9889; AI Sales Analytics</h1>
    <p>Powered by Multi-Model AI &middot; Auto-generated &middot; {generated_at}</p>
  </div>
  <div class="ai-badge">&#129302; AI: {ai_source}</div>
</div>

<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-icon">&#128176;</div>
    <div class="kpi-label">Total Sales</div>
    <div class="kpi-value">{fmt(total_sales)}</div>
    <div class="kpi-sub">All-time revenue</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-icon">&#128201;</div>
    <div class="kpi-label">Total Profit</div>
    <div class="kpi-value">{fmt(total_profit)}</div>
    <div class="kpi-sub {profit_class}">{profit_margin}% margin</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-icon">&#128722;</div>
    <div class="kpi-label">Total Orders</div>
    <div class="kpi-value">{total_orders:,}</div>
    <div class="kpi-sub">Avg {fmt(avg_order)} / order</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-icon">&#127942;</div>
    <div class="kpi-label">Top Product</div>
    <div class="kpi-value" style="font-size:.95rem">{data.get('top_product','N/A')}</div>
    <div class="kpi-sub">Best seller</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-icon">&#127758;</div>
    <div class="kpi-label">Top Region</div>
    <div class="kpi-value" style="font-size:.95rem">{data.get('top_region','N/A')}</div>
    <div class="kpi-sub">Highest revenue area</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-icon">&#128197;</div>
    <div class="kpi-label">Peak Month</div>
    <div class="kpi-value" style="font-size:.95rem">{data.get('best_month','N/A')}</div>
    <div class="kpi-sub">Highest sales month</div>
  </div>
</div>

<div class="charts-grid">
  <div class="chart-card">
    <div class="chart-title"><span>&#128200;</span> Monthly Sales Trend</div>
    <div id="monthlyChart" class="plotly-chart"></div>
  </div>
  <div class="chart-card">
    <div class="chart-title"><span>&#127885;</span> Top 10 Products by Sales</div>
    <div id="productChart" class="plotly-chart"></div>
  </div>
  <div class="chart-card">
    <div class="chart-title"><span>&#127758;</span> Sales by Region</div>
    <div id="regionChart" class="plotly-chart"></div>
  </div>
  <div class="chart-card">
    <div class="chart-title"><span>&#128230;</span> Sales by Category</div>
    <div id="categoryChart" class="plotly-chart"></div>
  </div>
</div>

<div class="insights-panel">
  <div class="insights-title">&#129302; AI-Generated Business Insights</div>
  <div class="insights-source">Powered by: {ai_source}</div>
  <div class="insights-text">{ai_insights}</div>
</div>

<div class="footer">
  &#128640; AI Sales Analytics Dashboard &middot; Python MCP Server &middot; No Power BI Required
</div>

<script>
const DARK = {{
  paper_bgcolor:'#111827', plot_bgcolor:'#111827',
  font:{{color:'#f1f5f9',family:'Inter'}},
  gridcolor:'#1e293b', zerolinecolor:'#1e293b'
}};
const COLORS = ['#6366f1','#8b5cf6','#06b6d4','#10b981','#f59e0b',
                '#ef4444','#ec4899','#14b8a6','#f97316','#a855f7'];

// Monthly Trend
const monthlyData = {monthly_json};
if(Object.keys(monthlyData).length > 0){{
  Plotly.newPlot('monthlyChart',[{{
    x:Object.keys(monthlyData), y:Object.values(monthlyData),
    type:'scatter', mode:'lines+markers',
    fill:'tozeroy', fillcolor:'rgba(99,102,241,0.12)',
    line:{{color:'#6366f1',width:3,shape:'spline'}},
    marker:{{color:'#818cf8',size:8}},
    name:'Sales'
  }}],{{
    ...DARK, margin:{{t:10,l:70,r:20,b:50}},
    xaxis:{{...DARK,showgrid:false}},
    yaxis:{{...DARK,tickprefix:'Rs.',tickformat:',.0s'}},
  }},{{responsive:true}});
}}

// Top Products
const productData = {products_json};
if(Object.keys(productData).length > 0){{
  const pKeys = Object.keys(productData).slice(0,10);
  const pVals = pKeys.map(k=>productData[k]);
  Plotly.newPlot('productChart',[{{
    x:pVals, y:pKeys, type:'bar', orientation:'h',
    marker:{{color:COLORS, opacity:0.9}},
  }}],{{
    ...DARK, margin:{{t:10,l:150,r:20,b:50}},
    xaxis:{{...DARK,tickprefix:'Rs.',tickformat:',.0s'}},
    yaxis:{{...DARK,showgrid:false,autorange:'reversed'}},
  }},{{responsive:true}});
}}

// Region
const regionData = {region_json};
if(Object.keys(regionData).length > 0){{
  Plotly.newPlot('regionChart',[{{
    labels:Object.keys(regionData), values:Object.values(regionData),
    type:'pie', hole:0.5,
    marker:{{colors:COLORS}},
    textinfo:'label+percent',
    textfont:{{color:'#f1f5f9',size:12}},
  }}],{{
    ...DARK, margin:{{t:10,l:20,r:20,b:10}},
    showlegend:true, legend:{{font:{{color:'#f1f5f9'}}}},
  }},{{responsive:true}});
}}

// Category
const catData = {category_json};
if(Object.keys(catData).length > 0){{
  Plotly.newPlot('categoryChart',[{{
    x:Object.keys(catData), y:Object.values(catData),
    type:'bar', marker:{{color:COLORS,opacity:0.9}},
  }}],{{
    ...DARK, margin:{{t:10,l:70,r:20,b:80}},
    xaxis:{{...DARK,showgrid:false}},
    yaxis:{{...DARK,tickprefix:'Rs.',tickformat:',.0s'}},
  }},{{responsive:true}});
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
