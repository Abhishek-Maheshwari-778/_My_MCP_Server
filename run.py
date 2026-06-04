"""
run.py -- Clean launcher for the AI Sales Analytics pipeline.
Sets UTF-8 encoding ONCE before all imports.
Usage:
    python run.py            # full pipeline + email
    python run.py --no-email # skip email
    python run.py --csv path/to/file.csv
"""
import sys
import io
import os

# Set UTF-8 ONCE here — before any other imports
os.environ["PYTHONIOENCODING"] = "utf-8"
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from main import run_pipeline

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Sales Analytics Pipeline")
    parser.add_argument("--csv",      type=str, default=None, help="Path to sales CSV")
    parser.add_argument("--no-email", action="store_true",    help="Skip email step")
    args = parser.parse_args()

    run_pipeline(csv_path=args.csv, send_mail=not args.no_email)
