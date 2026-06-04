"""
Export PDF Report
Creates a professional styled PDF from insights data.
"""
import sys
import json
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import INSIGHTS_JSON, REPORT_PDF


def export_pdf(insights_path=None, output_path=None) -> str:
    insights_path = insights_path or INSIGHTS_JSON
    output_path   = output_path   or REPORT_PDF

    print(f"\n{'='*50}")
    print("  PDF REPORT GENERATION STARTED")

    with open(insights_path, encoding="utf-8") as f:
        data = json.load(f)

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer,
            Table, TableStyle, HRFlowable
        )
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER

        doc = SimpleDocTemplate(
            str(output_path), pagesize=A4,
            rightMargin=2*cm, leftMargin=2*cm,
            topMargin=2*cm,   bottomMargin=2*cm
        )
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "Title", parent=styles["Heading1"],
            fontSize=22, textColor=colors.HexColor("#6366f1"),
            spaceAfter=4, alignment=TA_CENTER, fontName="Helvetica-Bold"
        )
        sub_style = ParagraphStyle(
            "Sub", parent=styles["Normal"],
            fontSize=10, textColor=colors.HexColor("#94a3b8"),
            spaceAfter=20, alignment=TA_CENTER
        )
        section_style = ParagraphStyle(
            "Section", parent=styles["Heading2"],
            fontSize=13, textColor=colors.HexColor("#818cf8"),
            spaceBefore=16, spaceAfter=8, fontName="Helvetica-Bold"
        )
        body_style = ParagraphStyle(
            "Body", parent=styles["Normal"],
            fontSize=10, textColor=colors.HexColor("#374151"),
            spaceAfter=6, leading=16
        )
        footer_style = ParagraphStyle(
            "Footer", parent=styles["Normal"],
            fontSize=8, textColor=colors.HexColor("#94a3b8"),
            alignment=TA_CENTER, spaceBefore=8
        )

        story = []

        story.append(Spacer(1, 0.5*cm))
        story.append(Paragraph("AI Sales Analytics Report", title_style))
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}  |  "
            f"AI Source: {data.get('ai_insights_source', 'Rule-Based')}",
            sub_style
        ))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#6366f1")))
        story.append(Spacer(1, 0.5*cm))

        def fmt(v):
            v = float(v) if v else 0
            if v >= 1_00_00_000: return f"Rs.{v/1_00_00_000:.2f} Cr"
            if v >= 1_00_000:    return f"Rs.{v/1_00_000:.2f} L"
            if v >= 1_000:       return f"Rs.{v/1_000:.1f}K"
            return f"Rs.{v:,.2f}"

        total_s = data.get("total_sales", 0)
        total_p = data.get("total_profit", 0)
        orders  = data.get("total_orders", 0)
        avg_ord = round(total_s / orders, 2) if orders else 0

        story.append(Paragraph("Key Performance Indicators", section_style))
        kpi_data = [
            ["Metric", "Value"],
            ["Total Sales",       fmt(total_s)],
            ["Total Profit",      fmt(total_p)],
            ["Profit Margin",     f"{data.get('profit_margin', 0)}%"],
            ["Total Orders",      f"{orders:,}"],
            ["Avg Order Value",   fmt(avg_ord)],
            ["Top Product",       str(data.get("top_product", "N/A"))],
            ["Top Region",        str(data.get("top_region", "N/A"))],
            ["Best Month",        str(data.get("best_month", "N/A"))],
        ]
        t = Table(kpi_data, colWidths=[8*cm, 8*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND",     (0,0), (-1,0), colors.HexColor("#6366f1")),
            ("TEXTCOLOR",      (0,0), (-1,0), colors.white),
            ("FONTNAME",       (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",       (0,0), (-1,0), 11),
            ("ALIGN",          (0,0), (-1,-1), "CENTER"),
            ("ROWBACKGROUNDS", (0,1), (-1,-1),
             [colors.HexColor("#f8fafc"), colors.white]),
            ("GRID",           (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ("FONTSIZE",       (0,1), (-1,-1), 10),
            ("TOPPADDING",     (0,0), (-1,-1), 8),
            ("BOTTOMPADDING",  (0,0), (-1,-1), 8),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.8*cm))

        story.append(Paragraph("AI-Generated Business Insights", section_style))
        story.append(HRFlowable(width="100%", thickness=1,
                                color=colors.HexColor("#c7d2fe")))
        story.append(Spacer(1, 0.3*cm))
        for line in data.get("ai_insights", "No insights available.").split("\n"):
            line = line.strip()
            if line:
                story.append(Paragraph(line, body_style))

        story.append(Spacer(1, 0.8*cm))

        top_prods = data.get("top_products", {})
        if top_prods:
            story.append(Paragraph("Top 10 Products by Sales", section_style))
            prod_data = [["#", "Product", "Sales"]]
            for i, (prod, val) in enumerate(
                sorted(top_prods.items(), key=lambda x: x[1], reverse=True)[:10], 1
            ):
                prod_data.append([str(i), str(prod), fmt(val)])
            pt = Table(prod_data, colWidths=[1.5*cm, 11*cm, 4*cm])
            pt.setStyle(TableStyle([
                ("BACKGROUND",     (0,0), (-1,0), colors.HexColor("#818cf8")),
                ("TEXTCOLOR",      (0,0), (-1,0), colors.white),
                ("FONTNAME",       (0,0), (-1,0), "Helvetica-Bold"),
                ("ALIGN",          (0,0), (0,-1), "CENTER"),
                ("ALIGN",          (2,0), (2,-1), "RIGHT"),
                ("ROWBACKGROUNDS", (0,1), (-1,-1),
                 [colors.HexColor("#f8fafc"), colors.white]),
                ("GRID",           (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
                ("FONTSIZE",       (0,0), (-1,-1), 9),
                ("TOPPADDING",     (0,0), (-1,-1), 6),
                ("BOTTOMPADDING",  (0,0), (-1,-1), 6),
            ]))
            story.append(pt)

        story.append(Spacer(1, 1*cm))
        story.append(HRFlowable(width="100%", thickness=1,
                                color=colors.HexColor("#6366f1")))
        story.append(Paragraph(
            "AI Sales Analytics | Python MCP Server | Auto-generated Report",
            footer_style
        ))

        doc.build(story)
        print(f"  PDF ready: {output_path}")
        return str(output_path)

    except ImportError:
        print("  reportlab not installed. Run: pip install reportlab")
        txt_path = str(output_path).replace(".pdf", ".txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write("AI SALES ANALYTICS REPORT\n")
            f.write(f"Generated: {datetime.now()}\n{'='*50}\n\n")
            f.write(f"Total Sales   : {data.get('total_sales', 0):,.2f}\n")
            f.write(f"Total Profit  : {data.get('total_profit', 0):,.2f}\n")
            f.write(f"Profit Margin : {data.get('profit_margin', 0)}%\n")
            f.write(f"Total Orders  : {data.get('total_orders', 0):,}\n")
            f.write(f"Top Product   : {data.get('top_product', 'N/A')}\n")
            f.write(f"Top Region    : {data.get('top_region', 'N/A')}\n")
            f.write(f"Best Month    : {data.get('best_month', 'N/A')}\n\n")
            f.write("AI INSIGHTS:\n" + "-"*30 + "\n")
            f.write(data.get("ai_insights", "N/A"))
        print(f"  Saved as text: {txt_path}")
        return txt_path


if __name__ == "__main__":
    export_pdf()
