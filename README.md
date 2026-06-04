# ⚡ AI Sales Analytics — MCP Automation System

> **No Power BI Login. No Manual Work. Just drop a CSV and AI does everything.**

---

## 🎯 What This Does

| You Do | System Does Automatically |
|--------|--------------------------|
| Drop a `.csv` file | Detects it instantly |
| Nothing | Cleans & validates data |
| Nothing | AI generates business insights |
| Nothing | Creates interactive HTML dashboard |
| Nothing | Exports professional PDF report |
| Nothing | Emails report to anyone |

---

## 🤖 Multi-Model AI Fallback Chain

The system automatically tries each AI provider and falls back if unavailable:

```
1. 🟢 NVIDIA NIM   → Free, 1000 credits (nvapi-...)
2. 🟢 Groq         → Free, no credit card (gsk_...)
3. 🟡 DeepSeek     → Near-free credits (sk-...)
4. 🔵 Rule-Based   → 100% offline, always works
```

**No internet? No API keys? → Rule-based insights still work perfectly!**

---

## 🚀 Quick Start (5 Minutes)

### Step 1 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Generate Sample Data (or use your own CSV)
```bash
python generate_sample_data.py
```

### Step 3 — Add API Keys (Optional but recommended)
Copy `.env.example` → `.env` and fill in your keys:
```bash
copy .env.example .env
# Edit .env with your keys
```

### Step 4 — Run the Pipeline!
```bash
# Option A: Run once on existing data
python main.py

# Option B: Watch folder (auto-trigger on CSV drop)
python watcher.py

# Option C: Chat with AI agent
python agent.py
```

---

## 🔑 How to Get FREE API Keys

### NVIDIA NIM (Recommended — Best free models)
1. Go to → **https://build.nvidia.com**
2. Click **Login / Sign Up** (free account)
3. Go to **API Keys** → **Create API Key**
4. Copy key (starts with `nvapi-`)
5. Add to `.env`: `NVIDIA_API_KEY=nvapi-xxxxx`

> **Free tier**: 1000 inference credits. Model: `meta/llama-3.3-70b-instruct`

### Groq (Fastest — No credit card)
1. Go to → **https://console.groq.com**
2. Sign up with Gmail or GitHub
3. Go to **API Keys** → **Create API Key**
4. Copy key (starts with `gsk_`)
5. Add to `.env`: `GROQ_API_KEY=gsk_xxxxx`

> **Free tier**: Generous rate limits, no card needed. Model: `llama-3.3-70b-versatile`

### DeepSeek (Very cheap)
1. Go to → **https://platform.deepseek.com**
2. Sign up → Go to **API Keys** → Create
3. Add to `.env`: `DEEPSEEK_API_KEY=sk-xxxxx`

---

## 📧 Email Setup (Gmail)

1. Go to **myaccount.google.com**
2. Security → **2-Step Verification** (enable)
3. Security → **App passwords** → Select "Mail" → **Generate**
4. Copy 16-char password (e.g. `abcd efgh ijkl mnop`)
5. Add to `.env`:
   ```
   EMAIL_SENDER=you@gmail.com
   EMAIL_PASSWORD=abcdefghijklmnop
   EMAIL_RECEIVER=boss@company.com
   ```

---

## 📁 Project Structure

```
AI-PowerBI-MCP-Automation/
│
├── 📂 data/
│   ├── sales.csv              ← Your input CSV
│   └── cleaned_sales.csv      ← Auto-generated
│
├── 📂 reports/                ← All outputs here
│   ├── dashboard.html         ← 🌐 Open in browser!
│   ├── report.pdf             ← 📄 Professional report
│   └── insights.json          ← Raw KPI data
│
├── 📂 incoming/               ← DROP CSV HERE for auto-trigger
│
├── 📂 src/
│   ├── ai_engine.py           ← Multi-model AI fallback
│   ├── clean_data.py          ← Data cleaning
│   ├── insights.py            ← KPI + AI insights
│   ├── dashboard.py           ← HTML dashboard (replaces Power BI)
│   ├── export_pdf.py          ← PDF report
│   └── send_email.py          ← Email automation
│
├── 📂 mcp_server/
│   └── server.py              ← MCP server (AI agent tools)
│
├── main.py                    ← Run full pipeline
├── watcher.py                 ← Folder auto-watcher
├── agent.py                   ← Chat interface
├── generate_sample_data.py    ← Generate test data
├── config.py                  ← All settings & API keys
├── .env.example               ← Key template
└── requirements.txt
```

---

## 💬 Agent Chat Examples

```bash
python agent.py
```
```
You → analyze today's sales
🤖  → Running FULL PIPELINE...
     ✅ Data cleaned (1200 rows)
     ✅ AI insights via NVIDIA NIM
     ✅ Dashboard created
     ✅ PDF exported
     ✅ Email sent

You → show dashboard
🤖  → Opening dashboard in browser...

You → status
🤖  → Total Sales: ₹45,23,400  |  Profit: 18.3%
     Top Product: Laptop Pro X  |  Region: West

You → send report
🤖  → Email delivered to boss@company.com ✓
```

---

## 🔌 MCP Server (For AI Agents like Claude)

Add to your Claude Desktop `mcp_settings.json`:
```json
{
  "mcpServers": {
    "ai-sales-analytics": {
      "command": "python",
      "args": ["C:/path/to/mcp_server/server.py"]
    }
  }
}
```

**Available MCP Tools:**
| Tool | Description |
|------|-------------|
| `run_full_pipeline` | Run everything end-to-end |
| `clean_data` | Clean CSV file |
| `generate_insights` | Get AI insights + KPIs |
| `create_dashboard` | Build HTML dashboard |
| `export_pdf` | Generate PDF report |
| `send_email` | Email the report |
| `get_status` | Check system status |

---

## 📊 Dashboard Preview

The HTML dashboard includes:
- 💰 KPI Cards (Sales, Profit, Orders, Avg Order Value)
- 📈 Monthly Sales Trend (interactive line chart)
- 🏅 Top 10 Products (horizontal bar chart)
- 🗺️ Region-wise Sales (donut chart)
- 📦 Category Breakdown (bar chart)
- 🧠 AI-Generated Insights Panel

**Opens in Chrome/Edge/Firefox — NO Power BI, NO Microsoft login!**

---

## 🎓 Resume Description

```
AI-Powered Sales Analytics Automation using MCP Server

• Built an end-to-end agentic AI pipeline using Python, MCP Server, and multi-model AI
• Implemented intelligent fallback: NVIDIA NIM → Groq → DeepSeek → Rule-based insights
• Automated CSV ingestion, data cleaning, KPI generation, and interactive dashboard creation
• Replaced Power BI with custom Plotly HTML dashboards (no login required)
• Integrated watchdog folder monitoring for zero-touch automation
• Delivered PDF reports and email notifications via SMTP automation
• Exposed pipeline as MCP tools enabling AI agents to analyze data through natural language
```

---

## 📞 Tech Stack

| Layer | Technology |
|-------|-----------|
| Data | Python + Pandas |
| AI | NVIDIA NIM / Groq / DeepSeek / Rule-based |
| Dashboard | Plotly (interactive HTML) |
| PDF | ReportLab |
| Email | SMTP (Gmail) |
| Automation | Watchdog |
| AI Protocol | MCP (Model Context Protocol) |

---

*Built with ❤️ — No Power BI login required. Works 100% locally.*
