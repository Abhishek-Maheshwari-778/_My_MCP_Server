"""
Insights Generator
- Computes KPIs from cleaned data
- Calls AI engine (multi-model fallback)
- Saves insights.json
"""
import sys
import os
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from config import CLEANED_CSV, INSIGHTS_JSON
from src.ai_engine import generate_ai_insights


def generate_insights(input_path=None, output_path=None) -> dict:
    input_path  = input_path  or CLEANED_CSV
    output_path = output_path or INSIGHTS_JSON

    print(f"\n{'='*50}")
    print("  INSIGHTS GENERATION STARTED")

    df = pd.read_csv(input_path)

    # Core KPIs
    total_sales   = float(df["sales"].sum())  if "sales"  in df.columns else 0
    total_profit  = float(df["profit"].sum()) if "profit" in df.columns else 0
    total_orders  = int(len(df))
    profit_margin = round((total_profit / total_sales * 100), 2) if total_sales else 0

    # Top Product
    if "product" in df.columns and "sales" in df.columns:
        top_product = df.groupby("product")["sales"].sum().idxmax()
    else:
        top_product = "N/A"

    # Top Region
    if "region" in df.columns and "sales" in df.columns:
        top_region = df.groupby("region")["sales"].sum().idxmax()
    else:
        top_region = "N/A"

    # Best Month
    if "month" in df.columns and "sales" in df.columns:
        best_month = df.groupby("month")["sales"].sum().idxmax()
    elif "month_num" in df.columns and "sales" in df.columns:
        import calendar
        best_month_num = df.groupby("month_num")["sales"].sum().idxmax()
        best_month = calendar.month_name[best_month_num]
    else:
        best_month = "N/A"

    # Top Category
    if "category" in df.columns and "sales" in df.columns:
        top_category = df.groupby("category")["sales"].sum().idxmax()
    else:
        top_category = "N/A"

    # Monthly trend
    monthly_trend = {}
    if "month" in df.columns and "month_num" in df.columns and "sales" in df.columns:
        monthly = (
            df.groupby(["month_num", "month"])["sales"]
            .sum().reset_index().sort_values("month_num")
        )
        monthly_trend = dict(zip(monthly["month"], monthly["sales"].round(2)))

    # Top 10 Products
    top_products = {}
    if "product" in df.columns and "sales" in df.columns:
        top_products = df.groupby("product")["sales"].sum().nlargest(10).round(2).to_dict()

    # Region Sales
    region_sales = {}
    if "region" in df.columns and "sales" in df.columns:
        region_sales = df.groupby("region")["sales"].sum().round(2).to_dict()

    # Category breakdown
    category_sales = {}
    if "category" in df.columns and "sales" in df.columns:
        category_sales = df.groupby("category")["sales"].sum().round(2).to_dict()

    data_summary = {
        "total_sales":    round(total_sales, 2),
        "total_profit":   round(total_profit, 2),
        "total_orders":   total_orders,
        "profit_margin":  profit_margin,
        "top_product":    top_product,
        "top_region":     top_region,
        "top_category":   top_category,
        "best_month":     best_month,
        "monthly_trend":  monthly_trend,
        "top_products":   top_products,
        "region_sales":   region_sales,
        "category_sales": category_sales,
    }

    print(f"  Total Sales   : Rs.{total_sales:,.2f}")
    print(f"  Total Profit  : Rs.{total_profit:,.2f}")
    print(f"  Profit Margin : {profit_margin}%")
    print(f"  Orders        : {total_orders:,}")
    print(f"  Top Product   : {top_product}")
    print(f"  Top Region    : {top_region}")
    print(f"  Best Month    : {best_month}")

    domain = os.environ.get("DATA_DOMAIN", "Sales")
    
    # Custom prompt based on domain
    prompt = f"""You are a senior {domain} data analyst. Analyze this {domain} data and give 6-8 specific, actionable bullet-point insights:

Data Summary:
- Total Value 1 (Sales/Volume/Cost): Rs.{total_sales:,.2f}
- Total Value 2 (Profit/PnL/Recovery): Rs.{total_profit:,.2f}
- Margin/Rate: {profit_margin}%
- Total Records: {total_orders:,}
- Top Item/Condition/Ticker: {top_product}
- Top Region/Hospital/Exchange: {top_region}
- Best Month: {best_month}
- Top Category: {top_category}

Give actionable bullet-point insights tailored to the {domain} industry. Be specific and reference the numbers."""

    print(f"\n  Calling AI engine (multi-model fallback) for {domain}...")
    ai_result = generate_ai_insights(data_summary, prompt=prompt)
    data_summary["ai_insights"]        = ai_result["text"]
    data_summary["ai_insights_source"] = ai_result["source"]
    data_summary["domain"]             = domain

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data_summary, f, indent=2, ensure_ascii=False)

    print(f"  Insights saved -> {output_path}\n")
    return data_summary


if __name__ == "__main__":
    result = generate_insights()
    print(f"\n[AI Source]: {result['ai_insights_source']}")
    print(result["ai_insights"])
