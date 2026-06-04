"""
Data Cleaning Module
- Removes nulls & duplicates
- Fixes date formats
- Normalizes column names
- Validates data types
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from config import DATA_DIR, CLEANED_CSV


def clean_data(input_path=None, output_path=None) -> dict:
    input_path  = input_path  or DATA_DIR / "sales.csv"
    output_path = output_path or CLEANED_CSV

    print(f"\n{'='*50}")
    print("  DATA CLEANING STARTED")
    print(f"  Input: {input_path}")

    df = pd.read_csv(input_path, encoding="utf-8", on_bad_lines="skip")
    raw_rows = len(df)
    print(f"  Loaded {raw_rows:,} rows x {len(df.columns)} columns")

    # Normalize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace(r"[^\w]", "_", regex=True)
    )

    # Map common column name variants
    rename_map = {}
    col_variants = {
        "sales":    ["sales", "revenue", "amount", "sale_amount", "total_amount", "net_sales"],
        "profit":   ["profit", "net_profit", "earnings", "margin"],
        "quantity": ["quantity", "qty", "units", "quantity_ordered"],
        "order_id": ["order_id", "orderid", "order_number", "id"],
        "date":     ["order_date", "date", "sale_date", "transaction_date", "ship_date"],
        "product":  ["product_name", "product", "item", "item_name", "description"],
        "category": ["category", "product_category", "sub_category", "subcategory"],
        "region":   ["region", "state", "city", "area", "location", "country"],
        "customer": ["customer_name", "customer", "client", "buyer"],
        "discount": ["discount", "discount_pct", "discount_percent"],
    }
    for std_name, variants in col_variants.items():
        for v in variants:
            if v in df.columns and std_name not in df.columns:
                rename_map[v] = std_name
    df.rename(columns=rename_map, inplace=True)
    print(f"  Columns: {list(df.columns)}")

    # Remove duplicates
    before_dedup = len(df)
    df.drop_duplicates(inplace=True)
    dupes_removed = before_dedup - len(df)

    # Remove nulls in key columns
    before_null = len(df)
    null_cols = [c for c in ["sales", "profit"] if c in df.columns]
    if null_cols:
        df.dropna(subset=null_cols, inplace=True)
    nulls_removed = before_null - len(df)

    # Fix date column
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df.dropna(subset=["date"], inplace=True)
        df["year"]      = df["date"].dt.year
        df["month"]     = df["date"].dt.strftime("%B")
        df["month_num"] = df["date"].dt.month

    # Numeric cleaning
    for col in ["sales", "profit", "quantity", "discount"]:
        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(r"[Rs.$,\s]", "", regex=True),
                errors="coerce"
            ).fillna(0)

    # Fill remaining NaN
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].fillna("Unknown")

    clean_rows = len(df)
    df.to_csv(output_path, index=False)

    print(f"  Cleaning complete: {raw_rows:,} -> {clean_rows:,} rows")
    print(f"  Duplicates removed: {dupes_removed} | Nulls removed: {nulls_removed}")
    print(f"  Saved: {output_path}\n")

    return {
        "raw_rows":      raw_rows,
        "clean_rows":    clean_rows,
        "dupes_removed": dupes_removed,
        "nulls_removed": nulls_removed,
        "columns":       list(df.columns),
        "output_path":   str(output_path),
    }


if __name__ == "__main__":
    print(clean_data())
