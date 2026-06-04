"""
=============================================================
  Sample Data Generator
  Creates a realistic sales.csv with 1200 rows.
  Run this once to get test data immediately.
=============================================================
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

# ── Master data ────────────────────────────────────────────
PRODUCTS = [
    ("Laptop Pro X",       "Technology",   45000, 55000),
    ("Wireless Mouse",     "Technology",    800,   1500),
    ("Mechanical Keyboard","Technology",   2500,   4500),
    ("USB-C Hub",          "Technology",   1200,   2200),
    ("Monitor 27inch",     "Technology",  18000,  25000),
    ("Office Chair",       "Furniture",   8000,  15000),
    ("Standing Desk",      "Furniture",  12000,  22000),
    ("Bookshelf",          "Furniture",   4000,   8000),
    ("Notebook A4",        "Office Supplies", 150,  400),
    ("Ballpoint Pen Set",  "Office Supplies",  80,  200),
    ("Whiteboard",         "Office Supplies", 2500, 4500),
    ("Stapler",            "Office Supplies",  300,  700),
    ("Running Shoes",      "Sports",       2500,  5000),
    ("Yoga Mat",           "Sports",        800,  1800),
    ("Water Bottle",       "Sports",        400,   900),
    ("Dumbbell Set",       "Sports",       3500,  7000),
    ("T-Shirt",            "Clothing",      400,   900),
    ("Jeans",              "Clothing",     1200,  2500),
    ("Formal Shirt",       "Clothing",     1500,  3000),
    ("Winter Jacket",      "Clothing",     3000,  6500),
    ("Novel - Bestseller", "Books",         200,   600),
    ("Python Programming", "Books",         350,   800),
    ("Self Help Book",     "Books",         250,   550),
    ("Cookbook",           "Books",         300,   700),
    ("Blender",            "Appliances",   3500,  6000),
    ("Air Fryer",          "Appliances",   4500,  8000),
    ("Coffee Maker",       "Appliances",   2800,  5500),
    ("Microwave Oven",     "Appliances",   6000, 12000),
]

REGIONS    = ["North", "South", "East", "West", "Central"]
CITIES     = {
    "North":   ["Delhi", "Chandigarh", "Amritsar", "Jaipur", "Lucknow"],
    "South":   ["Bangalore", "Chennai", "Hyderabad", "Kochi", "Coimbatore"],
    "East":    ["Kolkata", "Bhubaneswar", "Patna", "Guwahati", "Ranchi"],
    "West":    ["Mumbai", "Pune", "Ahmedabad", "Surat", "Nagpur"],
    "Central": ["Bhopal", "Indore", "Raipur", "Jabalpur", "Gwalior"],
}
CUSTOMERS = [
    "Rajesh Kumar", "Priya Singh", "Amit Sharma", "Sunita Patel",
    "Vikram Gupta", "Neha Verma", "Rahul Joshi", "Kavya Nair",
    "Arjun Reddy", "Meera Iyer", "Suresh Menon", "Anita Das",
    "Deepak Yadav", "Pooja Mishra", "Kiran Bose", "Rohit Shah",
    "Anjali Pillai", "Sanjay Tiwari", "Divya Pandey", "Manoj Rao",
]
PAYMENT   = ["Credit Card", "UPI", "Cash", "Debit Card", "Net Banking"]
SHIP_MODE = ["Standard", "Express", "Same Day", "Economy"]

# Peak months (higher sales)
PEAK_MONTHS = {10, 11, 12, 1}   # Oct, Nov, Dec, Jan


def generate_sales_csv(output_path: str, rows: int = 1200):
    base_date = datetime(2024, 1, 1)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Order_ID", "Order_Date", "Customer_Name", "Product_Name",
            "Category", "Region", "City", "Quantity",
            "Sales", "Discount", "Profit", "Payment_Mode", "Ship_Mode"
        ])
        writer.writeheader()

        for i in range(1, rows + 1):
            # Random date in 2024-2025
            offset_days = random.randint(0, 540)
            order_date  = base_date + timedelta(days=offset_days)
            month       = order_date.month

            # Peak season multiplier
            season_mult = 1.4 if month in PEAK_MONTHS else 1.0

            product_name, category, price_low, price_high = random.choice(PRODUCTS)
            region   = random.choice(REGIONS)
            city     = random.choice(CITIES[region])
            customer = random.choice(CUSTOMERS)
            qty      = random.randint(1, 5)

            unit_price = random.uniform(price_low, price_high) * season_mult
            discount   = round(random.choice([0, 0, 0, 5, 10, 15, 20]) / 100, 2)
            sales      = round(unit_price * qty * (1 - discount), 2)
            profit     = round(sales * random.uniform(0.08, 0.32), 2)

            writer.writerow({
                "Order_ID":     f"ORD-{10000 + i}",
                "Order_Date":   order_date.strftime("%Y-%m-%d"),
                "Customer_Name": customer,
                "Product_Name": product_name,
                "Category":     category,
                "Region":       region,
                "City":         city,
                "Quantity":     qty,
                "Sales":        sales,
                "Discount":     discount,
                "Profit":       profit,
                "Payment_Mode": random.choice(PAYMENT),
                "Ship_Mode":    random.choice(SHIP_MODE),
            })

    print(f"  [OK] Generated {rows} rows -> {output_path}")
    return output_path


if __name__ == "__main__":
    out = Path(__file__).parent / "data" / "sales.csv"
    out.parent.mkdir(exist_ok=True)
    generate_sales_csv(str(out))
    print(f"\n  [DONE] Sample data ready! Run: python main.py")
