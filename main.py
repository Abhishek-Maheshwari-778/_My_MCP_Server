"""
=============================================================
  Main Pipeline Runner
  Runs the complete pipeline in sequence:
  clean -> insights -> dashboard -> pdf -> email
  
  Use: python run.py  (not this file directly)
=============================================================
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from config import DATA_DIR, CLEANED_CSV, INSIGHTS_JSON, DASHBOARD_HTML, REPORT_PDF

BANNER = """
===========================================================
  AI SALES ANALYTICS  -  MCP AUTOMATION SYSTEM
  No Power BI Login  |  Multi-Model AI  |  Auto Report
===========================================================
"""


def run_pipeline(csv_path: str = None, send_mail: bool = True) -> dict:
    """
    Runs the full analytics pipeline.
    Returns dict with paths to all generated files.
    """
    print(BANNER)

    results = {}
    start   = time.time()

    # -- Determine input CSV
    if csv_path is None:
        csv_path = DATA_DIR / "sales.csv"

    if not Path(csv_path).exists():
        print(f"  [ERROR] CSV not found: {csv_path}")
        print(f"  [TIP]   Put your sales CSV in: {DATA_DIR / 'sales.csv'}")
        return {"error": "CSV not found"}

    # -- Step 1: Clean Data
    print("\n[STEP 1/5] DATA CLEANING")
    from src.clean_data import clean_data
    clean_result = clean_data(input_path=csv_path, output_path=CLEANED_CSV)
    results["cleaned_csv"] = clean_result.get("output_path")

    # -- Step 2: Generate Insights
    print("\n[STEP 2/5] AI INSIGHTS GENERATION")
    from src.insights import generate_insights
    insights = generate_insights(input_path=CLEANED_CSV, output_path=INSIGHTS_JSON)
    results["insights_json"] = str(INSIGHTS_JSON)
    results["ai_source"]     = insights.get("ai_insights_source", "Unknown")

    # -- Step 3: Create Dashboard
    print("\n[STEP 3/5] DASHBOARD CREATION")
    from src.dashboard import create_dashboard
    dash_path = create_dashboard(insights_path=INSIGHTS_JSON, output_path=DASHBOARD_HTML)
    results["dashboard_html"] = dash_path

    # -- Step 4: Export PDF
    print("\n[STEP 4/5] PDF REPORT EXPORT")
    from src.export_pdf import export_pdf
    pdf_path = export_pdf(insights_path=INSIGHTS_JSON, output_path=REPORT_PDF)
    results["report_pdf"] = pdf_path

    # -- Step 5: Send Email (optional)
    print("\n[STEP 5/5] EMAIL DELIVERY")
    if send_mail:
        from src.send_email import send_email
        results["email_sent"] = send_email(pdf_path=pdf_path)
    else:
        print("  [SKIP] Email skipped (--no-email flag)")

    elapsed = time.time() - start
    dash_url = "file:///" + str(DASHBOARD_HTML).replace("\\", "/")

    print(f"""
===========================================================
  [DONE] PIPELINE COMPLETE in {elapsed:.1f}s

  Cleaned CSV  : {results.get('cleaned_csv', '-')}
  AI Source    : {results.get('ai_source', '-')}
  Dashboard    : {results.get('dashboard_html', '-')}
  PDF Report   : {results.get('report_pdf', '-')}
  Email        : {'Sent' if results.get('email_sent') else 'Skipped'}
===========================================================

  Open dashboard in your browser:
  {dash_url}
""")
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AI Sales Analytics Pipeline")
    parser.add_argument("--csv",      type=str, default=None, help="Path to sales CSV file")
    parser.add_argument("--no-email", action="store_true",   help="Skip email step")
    args = parser.parse_args()

    run_pipeline(csv_path=args.csv, send_mail=not args.no_email)
