"""
Email Sender -- Gmail SMTP with App Password
"""
import sys
import smtplib
import json
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER, REPORT_PDF, INSIGHTS_JSON


def send_email(pdf_path=None, receiver=None, sender=None, password=None) -> bool:
    pdf_path = pdf_path or REPORT_PDF
    receiver = receiver or EMAIL_RECEIVER
    sender   = sender   or EMAIL_SENDER
    password = password or EMAIL_PASSWORD

    print(f"\n{'='*50}")
    print("  EMAIL SENDER STARTED")

    if not all([sender, password, receiver]):
        print("  [SKIP] Email not configured -- set EMAIL_SENDER/PASSWORD/RECEIVER in config.py")
        return False

    # Remove spaces from app password if any
    password = password.replace(" ", "")

    print(f"  From: {sender}")
    print(f"  To  : {receiver}")

    # Load insights for email body
    try:
        with open(INSIGHTS_JSON, encoding="utf-8") as f:
            data = json.load(f)
        total_sales   = data.get("total_sales", 0)
        total_profit  = data.get("total_profit", 0)
        profit_margin = data.get("profit_margin", 0)
        top_product   = data.get("top_product", "N/A")
        top_region    = data.get("top_region", "N/A")
        best_month    = data.get("best_month", "N/A")
        ai_source     = data.get("ai_insights_source", "Rule-Based")
        ai_insights   = data.get("ai_insights", "")
    except Exception:
        total_sales = total_profit = profit_margin = 0
        top_product = top_region = best_month = "N/A"
        ai_source = "Rule-Based"
        ai_insights = ""

    subject = f"AI Sales Report -- {datetime.now().strftime('%d %b %Y')}"

    # Build beautiful HTML email body
    insights_html = "".join(
        f"<li style='margin-bottom:6px'>{line.strip()}</li>"
        for line in ai_insights.split("\n") if line.strip()
    )

    html_body = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"/>
<style>
  body {{font-family:Arial,sans-serif;background:#f8fafc;margin:0;padding:20px}}
  .wrap {{max-width:620px;margin:0 auto;background:white;border-radius:12px;
          border:1px solid #e2e8f0;overflow:hidden}}
  .hdr  {{background:linear-gradient(135deg,#6366f1,#8b5cf6);padding:28px;text-align:center}}
  .hdr h1 {{color:white;margin:0;font-size:22px;font-weight:800}}
  .hdr p  {{color:rgba(255,255,255,.8);margin:8px 0 0;font-size:13px}}
  .body   {{padding:28px}}
  .kpi-grid {{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin:16px 0}}
  .kpi  {{background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;
          padding:14px;text-align:center}}
  .kpi-label {{font-size:11px;color:#6b7280;text-transform:uppercase;font-weight:600}}
  .kpi-value {{font-size:18px;font-weight:800;color:#6366f1;margin-top:4px}}
  .section-title {{font-weight:700;color:#374151;margin:20px 0 10px;
                   font-size:14px;border-left:3px solid #6366f1;padding-left:10px}}
  .kpi-row {{border-collapse:collapse;width:100%}}
  .kpi-row td {{padding:8px 12px;border:1px solid #e2e8f0;font-size:13px}}
  .kpi-row tr:nth-child(odd) td {{background:#f8fafc}}
  .insights-list {{color:#374151;font-size:13px;line-height:1.8;
                   padding-left:20px;margin:8px 0}}
  .badge {{display:inline-block;background:#ede9fe;color:#7c3aed;
           border-radius:20px;padding:4px 12px;font-size:11px;font-weight:600}}
  .footer {{background:#f8fafc;padding:14px 24px;text-align:center;
            border-top:1px solid #e2e8f0;font-size:11px;color:#94a3b8}}
</style>
</head>
<body>
<div class="wrap">
  <div class="hdr">
    <h1>AI Sales Analytics Report</h1>
    <p>{datetime.now().strftime('%d %B %Y, %I:%M %p')} &nbsp;|&nbsp;
       <span>Powered by {ai_source}</span></p>
  </div>

  <div class="body">
    <!-- KPI Grid -->
    <div class="kpi-grid">
      <div class="kpi">
        <div class="kpi-label">Total Sales</div>
        <div class="kpi-value">Rs.{total_sales/1e5:.1f}L</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Total Profit</div>
        <div class="kpi-value">Rs.{total_profit/1e5:.1f}L</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Profit Margin</div>
        <div class="kpi-value">{profit_margin}%</div>
      </div>
    </div>

    <!-- Details table -->
    <div class="section-title">Key Highlights</div>
    <table class="kpi-row">
      <tr><td><b>Top Product</b></td><td>{top_product}</td></tr>
      <tr><td><b>Top Region</b></td><td>{top_region}</td></tr>
      <tr><td><b>Best Month</b></td><td>{best_month}</td></tr>
      <tr><td><b>AI Provider</b></td><td><span class="badge">{ai_source}</span></td></tr>
    </table>

    <!-- AI Insights -->
    <div class="section-title">AI-Generated Insights</div>
    <ul class="insights-list">
      {insights_html}
    </ul>

    <p style="color:#6b7280;font-size:12px;margin-top:20px">
      The full PDF report with interactive charts is attached.
    </p>
  </div>

  <div class="footer">
    AI Sales Analytics &nbsp;|&nbsp; Python MCP Server &nbsp;|&nbsp;
    Auto-generated &nbsp;|&nbsp; No Power BI Required
  </div>
</div>
</body>
</html>
"""

    try:
        msg = MIMEMultipart("alternative")
        msg["From"]    = sender
        msg["To"]      = receiver
        msg["Subject"] = subject

        msg.attach(MIMEText("AI Sales Report - see HTML version", "plain"))
        msg.attach(MIMEText(html_body, "html"))

        # Attach PDF if it exists
        pdf_path = Path(pdf_path)
        if pdf_path.exists():
            with open(pdf_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={pdf_path.name}")
            msg.attach(part)
            print(f"  PDF attached: {pdf_path.name}")
        else:
            print(f"  [WARN] PDF not found at {pdf_path} -- sending without attachment")

        print("  Connecting to Gmail SMTP...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())

        print(f"  [OK] Email sent successfully to: {receiver}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("  [ERROR] Gmail auth failed!")
        print("  Make sure you are using App Password (16 chars), NOT your regular Gmail password.")
        print("  Steps: myaccount.google.com -> Security -> App passwords")
        return False
    except Exception as e:
        print(f"  [ERROR] Email failed: {e}")
        return False


if __name__ == "__main__":
    print("Testing email send...")
    send_email()
