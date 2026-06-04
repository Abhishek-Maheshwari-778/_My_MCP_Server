"""
=============================================================
  🔌  MCP Server — Model Context Protocol
  Exposes all pipeline tools so ANY AI agent can call them.
  
  Tools exposed:
    • clean_data()
    • generate_insights()
    • create_dashboard()
    • export_pdf()
    • send_email()
    • run_full_pipeline()
    • get_status()
=============================================================
"""

import sys
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp import types
    MCP_OK = True
except ImportError:
    MCP_OK = False
    print("⚠️  mcp package not found. Run: pip install mcp")


def create_mcp_server():
    if not MCP_OK:
        return None

    app = Server("ai-sales-analytics")

    # ─────────────────────────────────────────────────────
    #  📋  LIST TOOLS
    # ─────────────────────────────────────────────────────
    @app.list_tools()
    async def list_tools() -> list[types.Tool]:
        return [
            types.Tool(
                name="clean_data",
                description=(
                    "Cleans a sales CSV file. Removes nulls, duplicates, fixes date formats, "
                    "normalizes column names. Returns cleaning stats."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "csv_path": {
                            "type": "string",
                            "description": "Optional path to CSV file. Defaults to data/sales.csv"
                        }
                    },
                    "required": []
                }
            ),
            types.Tool(
                name="generate_insights",
                description=(
                    "Generates AI-powered business insights from cleaned sales data. "
                    "Uses multi-model fallback: NVIDIA NIM → Groq → DeepSeek → Rule-based. "
                    "Returns KPIs and insights text."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            types.Tool(
                name="create_dashboard",
                description=(
                    "Creates a beautiful interactive HTML dashboard with Plotly charts. "
                    "No Power BI needed — opens in any browser. "
                    "Returns path to the HTML file."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            types.Tool(
                name="export_pdf",
                description=(
                    "Exports a professional PDF report with KPIs, charts summary, and AI insights. "
                    "Returns path to the PDF file."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            types.Tool(
                name="send_email",
                description=(
                    "Sends the PDF report via email. Requires EMAIL_SENDER, EMAIL_PASSWORD, "
                    "EMAIL_RECEIVER to be configured in config.py. Returns success status."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "receiver": {
                            "type": "string",
                            "description": "Optional override for recipient email address"
                        }
                    },
                    "required": []
                }
            ),
            types.Tool(
                name="run_full_pipeline",
                description=(
                    "Runs the COMPLETE pipeline end-to-end: "
                    "clean_data → generate_insights → create_dashboard → export_pdf → send_email. "
                    "Just say 'analyze today\\'s sales' and this does everything!"
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "csv_path": {
                            "type": "string",
                            "description": "Optional path to CSV file"
                        },
                        "send_email": {
                            "type": "boolean",
                            "description": "Whether to send email. Default: true",
                            "default": True
                        }
                    },
                    "required": []
                }
            ),
            types.Tool(
                name="get_status",
                description=(
                    "Returns the current status: what files exist, last run time, "
                    "latest KPIs, and which AI provider was used."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
        ]

    # ─────────────────────────────────────────────────────
    #  🔧  CALL TOOLS
    # ─────────────────────────────────────────────────────
    @app.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:

        try:
            if name == "clean_data":
                from src.clean_data import clean_data
                from config import DATA_DIR, CLEANED_CSV
                csv_path = arguments.get("csv_path") or DATA_DIR / "sales.csv"
                result   = clean_data(input_path=csv_path, output_path=CLEANED_CSV)
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "status":        "success",
                        "raw_rows":      result["raw_rows"],
                        "clean_rows":    result["clean_rows"],
                        "dupes_removed": result["dupes_removed"],
                        "nulls_removed": result["nulls_removed"],
                        "columns":       result["columns"],
                        "output":        result["output_path"],
                    }, indent=2)
                )]

            elif name == "generate_insights":
                from src.insights import generate_insights
                from config import CLEANED_CSV, INSIGHTS_JSON
                result = generate_insights(input_path=CLEANED_CSV, output_path=INSIGHTS_JSON)
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "status":        "success",
                        "total_sales":   result["total_sales"],
                        "total_profit":  result["total_profit"],
                        "profit_margin": result["profit_margin"],
                        "total_orders":  result["total_orders"],
                        "top_product":   result["top_product"],
                        "top_region":    result["top_region"],
                        "best_month":    result["best_month"],
                        "ai_source":     result["ai_insights_source"],
                        "insights":      result["ai_insights"],
                    }, indent=2)
                )]

            elif name == "create_dashboard":
                from src.dashboard import create_dashboard
                from config import INSIGHTS_JSON, DASHBOARD_HTML
                path = create_dashboard(insights_path=INSIGHTS_JSON, output_path=DASHBOARD_HTML)
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success",
                        "dashboard_path": path,
                        "message": f"Open in browser: file:///{path.replace(chr(92),'/')}"
                    }, indent=2)
                )]

            elif name == "export_pdf":
                from src.export_pdf import export_pdf
                from config import INSIGHTS_JSON, REPORT_PDF
                path = export_pdf(insights_path=INSIGHTS_JSON, output_path=REPORT_PDF)
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"status": "success", "pdf_path": path}, indent=2)
                )]

            elif name == "send_email":
                from src.send_email import send_email
                from config import REPORT_PDF
                receiver = arguments.get("receiver")
                success  = send_email(pdf_path=REPORT_PDF, receiver=receiver)
                return [types.TextContent(
                    type="text",
                    text=json.dumps({
                        "status": "success" if success else "skipped",
                        "sent":   success,
                        "note":   "Configure EMAIL_SENDER/PASSWORD/RECEIVER in config.py to enable"
                    }, indent=2)
                )]

            elif name == "run_full_pipeline":
                from main import run_pipeline
                csv_path   = arguments.get("csv_path")
                do_email   = arguments.get("send_email", True)
                result     = run_pipeline(csv_path=csv_path, send_mail=do_email)
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"status": "success", **result}, indent=2)
                )]

            elif name == "get_status":
                from config import DATA_DIR, CLEANED_CSV, INSIGHTS_JSON, DASHBOARD_HTML, REPORT_PDF
                status = {
                    "files": {
                        "sales_csv":      (DATA_DIR / "sales.csv").exists(),
                        "cleaned_csv":    CLEANED_CSV.exists(),
                        "insights_json":  INSIGHTS_JSON.exists(),
                        "dashboard_html": DASHBOARD_HTML.exists(),
                        "report_pdf":     REPORT_PDF.exists(),
                    }
                }
                if INSIGHTS_JSON.exists():
                    with open(INSIGHTS_JSON, encoding="utf-8") as f:
                        data = json.load(f)
                    status["last_run"] = {
                        "total_sales":   data.get("total_sales"),
                        "total_profit":  data.get("total_profit"),
                        "profit_margin": data.get("profit_margin"),
                        "total_orders":  data.get("total_orders"),
                        "top_product":   data.get("top_product"),
                        "top_region":    data.get("top_region"),
                        "best_month":    data.get("best_month"),
                        "ai_source":     data.get("ai_insights_source"),
                    }
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"status": "success", **status}, indent=2)
                )]

            else:
                return [types.TextContent(
                    type="text",
                    text=json.dumps({"error": f"Unknown tool: {name}"})
                )]

        except Exception as e:
            import traceback
            return [types.TextContent(
                type="text",
                text=json.dumps({
                    "status": "error",
                    "error":  str(e),
                    "trace":  traceback.format_exc()
                })
            )]

    return app


async def main():
    app = create_mcp_server()
    if app is None:
        print("❌ Cannot start MCP server — install mcp: pip install mcp")
        return

    print("""
╔══════════════════════════════════════════════════════════╗
║   🔌  AI SALES ANALYTICS — MCP SERVER RUNNING            ║
║   Tools: clean_data · generate_insights · create_dashboard║
║          export_pdf · send_email · run_full_pipeline      ║
╚══════════════════════════════════════════════════════════╝
""")
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream, write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
