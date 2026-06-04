"""
Multi-Model AI Engine
Fallback chain: NVIDIA NIM -> Groq -> DeepSeek -> Rule-Based (offline)
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    NVIDIA_API_KEY, NVIDIA_MODEL, NVIDIA_BASE_URL, NVIDIA_TEMP, NVIDIA_TOP_P, NVIDIA_MAX_TOKENS,
    GROQ_API_KEY, GROQ_MODEL,
    DEEPSEEK_API_KEY, DEEPSEEK_MODEL,
)


# ─────────────────────────────────────────────────────────────────────
#  1. NVIDIA NIM  (exact implementation as per nvidia docs)
# ─────────────────────────────────────────────────────────────────────
def _try_nvidia(prompt: str):
    if not NVIDIA_API_KEY:
        print("  [NVIDIA] No API key set -- skipping.")
        return None
    try:
        from openai import OpenAI
        client = OpenAI(
            base_url=NVIDIA_BASE_URL,
            api_key=NVIDIA_API_KEY,
        )
        completion = client.chat.completions.create(
            model=NVIDIA_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=NVIDIA_TEMP,
            top_p=NVIDIA_TOP_P,
            max_tokens=NVIDIA_MAX_TOKENS,
            stream=False,
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"  [NVIDIA] Failed: {e}")
        return None


# ─────────────────────────────────────────────────────────────────────
#  2. GROQ  (free, super fast)
# ─────────────────────────────────────────────────────────────────────
def _try_groq(prompt: str):
    if not GROQ_API_KEY:
        print("  [Groq] No API key set -- skipping.")
        return None
    try:
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            timeout=20,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"  [Groq] Failed: {e}")
        return None


# ─────────────────────────────────────────────────────────────────────
#  3. DEEPSEEK  (OpenAI-compatible)
# ─────────────────────────────────────────────────────────────────────
def _try_deepseek(prompt: str):
    if not DEEPSEEK_API_KEY:
        print("  [DeepSeek] No API key set -- skipping.")
        return None
    try:
        from openai import OpenAI
        client = OpenAI(
            base_url="https://api.deepseek.com",
            api_key=DEEPSEEK_API_KEY,
        )
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful business analyst."},
                {"role": "user",   "content": prompt},
            ],
            max_tokens=1024,
            timeout=20,
            stream=False,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"  [DeepSeek] Failed: {e}")
        return None


# ─────────────────────────────────────────────────────────────────────
#  4. RULE-BASED (100% offline -- always works)
# ─────────────────────────────────────────────────────────────────────
def _rule_based_insights(data: dict) -> str:
    total_sales  = data.get("total_sales", 0)
    total_profit = data.get("total_profit", 0)
    top_product  = data.get("top_product", "N/A")
    top_region   = data.get("top_region", "N/A")
    best_month   = data.get("best_month", "N/A")
    orders       = data.get("total_orders", 0)
    profit_pct   = (total_profit / total_sales * 100) if total_sales else 0
    avg_order    = total_sales / orders if orders else 0

    lines = [
        f"[Revenue]        Total sales: Rs.{total_sales:,.0f}  |  " +
        ("Strong performance!" if total_sales > 1_000_000 else "Keep growing."),

        f"[Profit]         Margin: {profit_pct:.1f}%  |  " +
        ("Excellent!" if profit_pct >= 20 else "Healthy." if profit_pct >= 10 else "Needs improvement."),

        f"[Top Product]    '{top_product}' is your best seller -- increase marketing budget here.",

        f"[Top Region]     '{top_region}' generates highest revenue -- expand inventory & distribution.",

        f"[Peak Month]     '{best_month}' is your peak sales month -- plan campaigns around it.",

        f"[Orders]         {orders:,} total orders  |  Avg order value: Rs.{avg_order:,.0f}",

        f"[Recommendation] " + (
            "Reduce discounts to improve margins."
            if profit_pct < 15
            else "Scale campaigns for top product & region to maximize growth."
        ),
    ]
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────
#  MAIN: Try providers in order, auto-fallback
# ─────────────────────────────────────────────────────────────────────
def generate_ai_insights(data: dict, prompt: str = None) -> dict:
    """
    Smart fallback:
      NVIDIA NIM -> Groq -> DeepSeek -> Rule-Based (offline)
    Returns {"text": "...", "source": "..."}
    """
    if prompt is None:
        profit_pct = (data.get("total_profit", 0) / max(data.get("total_sales", 1), 1) * 100)
        prompt = (
            f"You are a senior business analyst. Analyze this sales data and give "
            f"6-8 specific, actionable bullet-point insights:\n\n"
            f"Total Sales   : Rs.{data.get('total_sales', 0):,.2f}\n"
            f"Total Profit  : Rs.{data.get('total_profit', 0):,.2f}\n"
            f"Profit Margin : {profit_pct:.1f}%\n"
            f"Total Orders  : {data.get('total_orders', 0):,}\n"
            f"Top Product   : {data.get('top_product', 'N/A')}\n"
            f"Top Region    : {data.get('top_region', 'N/A')}\n"
            f"Best Month    : {data.get('best_month', 'N/A')}\n"
            f"Top Category  : {data.get('top_category', 'N/A')}\n\n"
            f"Be specific with numbers. Give actionable recommendations."
        )

    providers = [
        ("NVIDIA NIM", _try_nvidia),
        ("Groq",       _try_groq),
        ("DeepSeek",   _try_deepseek),
    ]

    for name, fn in providers:
        print(f"  [AI] Trying {name}...", flush=True)
        try:
            result = fn(prompt)
            if result and len(result.strip()) > 20:
                print(f"  [AI] SUCCESS -- {name} responded!", flush=True)
                return {"text": result.strip(), "source": name}
        except Exception as e:
            print(f"  [AI] {name} error: {e}", flush=True)

    print("  [AI] All APIs failed -- using offline rule-based insights.", flush=True)
    return {"text": _rule_based_insights(data), "source": "Rule-Based (Offline)"}


# ─────────────────────────────────────────────────────────────────────
#  Quick self-test
# ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n=== Testing AI Engine ===\n")
    print(f"NVIDIA key set : {'YES' if NVIDIA_API_KEY else 'NO'}")
    print(f"Groq key set   : {'YES' if GROQ_API_KEY else 'NO'}")
    print(f"DeepSeek key   : {'YES' if DEEPSEEK_API_KEY else 'NO'}")
    print()

    test_data = {
        "total_sales":   4_500_000,
        "total_profit":    900_000,
        "total_orders":       3200,
        "top_product":  "Laptop Pro X",
        "top_region":   "West",
        "best_month":   "December",
        "top_category": "Technology",
    }
    result = generate_ai_insights(test_data)
    print(f"\n--- Result (via {result['source']}) ---\n")
    print(result["text"])
