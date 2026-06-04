"""
Data Cleaning Module (Multi-Domain & Excel Support)
- Reads CSV or Excel
- Normalizes column names based on selected domain
- Fixes date formats, numeric casting, removes nulls
"""
import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from config import DATA_DIR, CLEANED_CSV

def clean_data(input_path=None, output_path=None) -> dict:
    input_path  = Path(input_path or DATA_DIR / "sales.csv")
    output_path = Path(output_path or CLEANED_CSV)
    domain      = os.environ.get("DATA_DOMAIN", "Sales")

    print(f"\n{'='*50}")
    print(f"  DATA CLEANING STARTED ({domain} Domain)")
    print(f"  Input: {input_path}")

    # 1. Read File (CSV or Excel)
    if input_path.suffix.lower() in [".xlsx", ".xls"]:
        df = pd.read_excel(input_path)
    else:
        df = pd.read_csv(input_path, encoding="utf-8", on_bad_lines="skip")
        
    raw_rows = len(df)
    print(f"  Loaded {raw_rows:,} rows x {len(df.columns)} columns")

    # 2. Base Normalization
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^\w]", "_", regex=True)
    )

    # 3. Domain-Specific Column Mapping
    rename_map = {}
    if domain == "Sales":
        col_variants = {
            "sales":    ["sales", "revenue", "amount", "net_sales"],
            "profit":   ["profit", "net_profit", "earnings", "margin"],
            "quantity": ["quantity", "qty", "units"],
            "date":     ["order_date", "date", "sale_date"],
            "product":  ["product_name", "product", "item"],
            "category": ["category", "sub_category"],
            "region":   ["region", "state", "city", "country"],
        }
    elif domain == "Health":
        col_variants = {
            "sales":    ["cost", "bill_amount", "revenue", "charges"],     # Map to sales for standard metrics
            "profit":   ["recovery_rate", "outcome_score"],               # Map to profit for standard metrics
            "quantity": ["patients", "count", "admissions", "days_stayed"], # Map to quantity
            "date":     ["admission_date", "date", "visit_date"],
            "product":  ["condition", "disease", "treatment", "diagnosis"],
            "category": ["department", "ward", "specialty"],
            "region":   ["hospital", "clinic", "region", "city"],
        }
    elif domain == "Trading":
        col_variants = {
            "sales":    ["volume", "total_traded", "turnover"],           # Map to sales
            "profit":   ["pnl", "profit", "net_gain", "return"],          # Map to profit
            "quantity": ["shares", "contracts", "qty", "size"],
            "date":     ["trade_date", "date", "execution_time"],
            "product":  ["ticker", "symbol", "asset", "instrument"],
            "category": ["asset_class", "sector", "type"],
            "region":   ["exchange", "market", "region"],
        }
    else:
        col_variants = {}

    for std_name, variants in col_variants.items():
        for v in variants:
            if v in df.columns and std_name not in df.columns:
                rename_map[v] = std_name
                break
                
    df.rename(columns=rename_map, inplace=True)
    print(f"  Columns after mapping: {list(df.columns)}")

    # 4. Clean Data (Dedup, Nulls)
    before_dedup = len(df)
    df.drop_duplicates(inplace=True)
    dupes_removed = before_dedup - len(df)

    # 5. Fix Dates
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df.dropna(subset=["date"], inplace=True)
        df["year"]      = df["date"].dt.year
        df["month"]     = df["date"].dt.strftime("%B")
        df["month_num"] = df["date"].dt.month

    # 6. Numeric Cleaning
    numeric_cols = ["sales", "profit", "quantity"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(r"[Rs.$,\s]", "", regex=True),
                errors="coerce"
            ).fillna(0)

    # 7. Fill object NaNs
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].fillna("Unknown")

    clean_rows = len(df)
    df.to_csv(output_path, index=False)

    print(f"  Cleaning complete: {raw_rows:,} -> {clean_rows:,} rows")
    print(f"  Saved: {output_path}\n")

    return {
        "raw_rows":      raw_rows,
        "clean_rows":    clean_rows,
        "dupes_removed": dupes_removed,
        "columns":       list(df.columns),
        "output_path":   str(output_path),
        "domain":        domain
    }

if __name__ == "__main__":
    print(clean_data())
