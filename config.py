"""
AI-Powered Sales Analytics -- Configuration File
"""
import os
import pathlib
from dotenv import load_dotenv

# Load .env file (so API keys are read automatically)
load_dotenv(pathlib.Path(__file__).parent / ".env")

# ─────────────────────────────────────────────
#  API KEYS
# ─────────────────────────────────────────────

# 1. NVIDIA NIM (Free -- 1000 credits)
#    Get key: https://build.nvidia.com -> API Keys -> Create
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")

# 2. GROQ (FREE)
GROQ_API_KEY   = os.getenv("GROQ_API_KEY", "")

# 3. DEEPSEEK
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

# ─────────────────────────────────────────────
#  MODEL SELECTION
# ─────────────────────────────────────────────
NVIDIA_MODEL   = "meta/llama-3.3-70b-instruct"   # NVIDIA NIM model (exact as per their docs)
GROQ_MODEL     = "llama-3.3-70b-versatile"        # Best free Groq model
DEEPSEEK_MODEL = "deepseek-chat"                   # DeepSeek chat model

# ─────────────────────────────────────────────
#  NVIDIA NIM - API PARAMS (from your code)
# ─────────────────────────────────────────────
NVIDIA_BASE_URL   = "https://integrate.api.nvidia.com/v1"
NVIDIA_TEMP       = 0.2
NVIDIA_TOP_P      = 0.7
NVIDIA_MAX_TOKENS = 1024

# ─────────────────────────────────────────────
#  EMAIL SETTINGS
# ─────────────────────────────────────────────
EMAIL_SENDER   = os.getenv("EMAIL_SENDER",   "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")   # Gmail App Password (16 chars)
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER", "")  # Send to yourself for test

# ─────────────────────────────────────────────
#  PATHS
# ─────────────────────────────────────────────
BASE_DIR       = pathlib.Path(__file__).parent
DATA_DIR       = BASE_DIR / "data"
INCOMING_DIR   = BASE_DIR / "incoming"
REPORTS_DIR    = BASE_DIR / "reports"
DASHBOARD_DIR  = BASE_DIR / "dashboard"

for _d in [DATA_DIR, INCOMING_DIR, REPORTS_DIR, DASHBOARD_DIR]:
    _d.mkdir(exist_ok=True)

CLEANED_CSV    = DATA_DIR    / "cleaned_sales.csv"
INSIGHTS_JSON  = REPORTS_DIR / "insights.json"
DASHBOARD_HTML = REPORTS_DIR / "dashboard.html"
REPORT_PDF     = REPORTS_DIR / "report.pdf"
