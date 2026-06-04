"""
=============================================================
  🤖  AI Agent Chat Interface
  Talk to the system naturally.
  
  Examples:
    "analyze today's sales"
    "clean the data"
    "show me insights"
    "send report to boss"
    "what's the status?"
=============================================================
"""

import sys
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

BANNER = """
╔══════════════════════════════════════════════════════════╗
║   🤖  AI SALES ANALYTICS AGENT — Chat Interface           ║
╚══════════════════════════════════════════════════════════╝

  Available commands (just type naturally):
  ─────────────────────────────────────────
  📊  "analyze sales"       → Run full pipeline
  🧹  "clean data"          → Clean CSV only
  💡  "get insights"        → Generate AI insights
  🎨  "show dashboard"      → Open dashboard in browser
  📄  "export pdf"          → Generate PDF report
  📧  "send report"         → Email the report
  📋  "status"              → Check system status
  ❓  "help"                → Show this menu
  🚪  "exit" / "quit"       → Exit agent

  Type your request below ↓
"""


def match(text: str, patterns: list) -> bool:
    text = text.lower().strip()
    return any(re.search(p, text) for p in patterns)


def run_agent():
    print(BANNER)

    while True:
        try:
            user_input = input("\n  You → ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n  👋 Agent stopped. Goodbye!")
            break

        if not user_input:
            continue

        print(f"\n  🤖 Agent → Processing: \"{user_input}\"\n")

        # ── Route commands ─────────────────────────────────

        if match(user_input, [r"exit|quit|bye|goodbye|stop"]):
            print("  👋 Goodbye!")
            break

        elif match(user_input, [r"help|\?"]):
            print(BANNER)

        elif match(user_input, [
            r"status|check|what.*files|ready|done"
        ]):
            _cmd_status()

        elif match(user_input, [
            r"analyze|full.*pipeline|run.*all|everything|today.*sales|sales.*today|start"
        ]):
            _cmd_full_pipeline()

        elif match(user_input, [
            r"clean|cleaning|preprocess|prepare.*data|fix.*data"
        ]):
            _cmd_clean()

        elif match(user_input, [
            r"insight|kpi|metrics|analysis|analys|numbers|stats"
        ]):
            _cmd_insights()

        elif match(user_input, [
            r"dashboard|chart|visual|graph|browser|html|open"
        ]):
            _cmd_dashboard()

        elif match(user_input, [
            r"pdf|report|export|download"
        ]):
            _cmd_pdf()

        elif match(user_input, [
            r"email|mail|send|deliver"
        ]):
            _cmd_email()

        else:
            # Unknown command → ask AI for interpretation
            _cmd_ai_interpret(user_input)


# ── Command Implementations ────────────────────────────────

def _cmd_status():
    from config import DATA_DIR, CLEANED_CSV, INSIGHTS_JSON, DASHBOARD_HTML, REPORT_PDF
    import json

    print("  📋 SYSTEM STATUS")
    print("  " + "─"*40)

    files = {
        "📂 sales.csv":      DATA_DIR / "sales.csv",
        "🧹 cleaned_sales":  CLEANED_CSV,
        "💡 insights.json":  INSIGHTS_JSON,
        "🌐 dashboard.html": DASHBOARD_HTML,
        "📄 report.pdf":     REPORT_PDF,
    }
    for label, path in files.items():
        exists = Path(path).exists()
        status = "✅ Ready" if exists else "❌ Not generated"
        print(f"  {label:<22} {status}")

    if INSIGHTS_JSON.exists():
        with open(INSIGHTS_JSON, encoding="utf-8") as f:
            data = json.load(f)
        print(f"\n  📊 Last Run KPIs:")
        print(f"     Sales      : ₹{data.get('total_sales', 0):>14,.2f}")
        print(f"     Profit     : ₹{data.get('total_profit', 0):>14,.2f}")
        print(f"     Margin     : {data.get('profit_margin', 0):>14}%")
        print(f"     Orders     : {data.get('total_orders', 0):>15,}")
        print(f"     Top Product: {data.get('top_product', 'N/A')}")
        print(f"     Top Region : {data.get('top_region', 'N/A')}")
        print(f"     Best Month : {data.get('best_month', 'N/A')}")
        print(f"     AI Source  : {data.get('ai_insights_source', 'N/A')}")


def _cmd_full_pipeline():
    print("  🚀 Running FULL PIPELINE (clean → insights → dashboard → pdf → email)...")
    from main import run_pipeline
    run_pipeline()


def _cmd_clean():
    print("  🧹 Running data cleaning...")
    from src.clean_data import clean_data
    result = clean_data()
    print(f"\n  ✅ Done! {result['clean_rows']:,} rows cleaned.")


def _cmd_insights():
    print("  💡 Generating AI insights (multi-model)...")
    from src.insights import generate_insights
    result = generate_insights()
    print(f"\n  ✅ Insights generated via: {result['ai_insights_source']}")
    print(f"\n  📊 Key Metrics:")
    print(f"     Sales  : ₹{result['total_sales']:,.2f}")
    print(f"     Profit : ₹{result['total_profit']:,.2f} ({result['profit_margin']}%)")
    print(f"\n  🤖 AI Insights:")
    print("  " + "\n  ".join(result["ai_insights"].split("\n")))


def _cmd_dashboard():
    print("  🎨 Creating interactive dashboard...")
    from src.dashboard import create_dashboard
    path = create_dashboard()
    print(f"\n  ✅ Dashboard ready!")
    # Auto-open in browser
    import webbrowser
    url = f"file:///{str(path).replace(chr(92), '/')}"
    print(f"  🌐 Opening: {url}")
    webbrowser.open(url)


def _cmd_pdf():
    print("  📄 Generating PDF report...")
    from src.export_pdf import export_pdf
    path = export_pdf()
    print(f"\n  ✅ PDF ready: {path}")
    # Auto-open
    import os
    os.startfile(str(path)) if sys.platform == "win32" else None


def _cmd_email():
    print("  📧 Sending email report...")
    from src.send_email import send_email
    success = send_email()
    if success:
        print("  ✅ Email delivered!")
    else:
        print("  ⚠️  Email skipped — configure email in config.py")


def _cmd_ai_interpret(text: str):
    """Use AI to interpret unclear commands."""
    print(f"  🤔 Hmm, let me understand: \"{text}\"")
    print()

    lower = text.lower()
    # Try keyword detection
    if any(w in lower for w in ["sale", "revenue", "profit", "data", "csv", "report"]):
        print("  💡 Sounds like you want to analyze sales data.")
        print("  🚀 Running full pipeline...")
        _cmd_full_pipeline()
    else:
        print("  ❓ I didn't understand that. Here's what I can do:")
        print()
        cmds = [
            "  analyze sales       → Full pipeline",
            "  clean data          → Data cleaning",
            "  get insights        → AI insights",
            "  show dashboard      → Open dashboard",
            "  export pdf          → Generate PDF",
            "  send report         → Email report",
            "  status              → Check files",
        ]
        for c in cmds:
            print(c)


if __name__ == "__main__":
    run_agent()
