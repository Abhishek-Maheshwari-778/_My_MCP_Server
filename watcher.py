"""
=============================================================
  👁️  Folder Watcher
  Monitors the  incoming/  folder.
  When a .csv file is dropped → triggers full pipeline.
=============================================================
"""

import sys
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import time
import shutil
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from config import INCOMING_DIR, DATA_DIR

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_OK = True
except ImportError:
    WATCHDOG_OK = False


class SalesCSVHandler(FileSystemEventHandler):
    """Handles new CSV files dropped into the incoming folder."""

    def __init__(self, send_mail=True):
        self.send_mail    = send_mail
        self.processing   = set()   # avoid double-trigger

    def on_created(self, event):
        if event.is_directory:
            return
        path = Path(event.src_path)
        if path.suffix.lower() != ".csv":
            return
        if str(path) in self.processing:
            return

        self.processing.add(str(path))
        self._handle_csv(path)
        self.processing.discard(str(path))

    def _handle_csv(self, csv_path: Path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        print(f"\n{'='*56}")
        print(f"  📥  NEW CSV DETECTED: {csv_path.name}")
        print(f"  ⏰  {datetime.now().strftime('%d %b %Y, %I:%M:%S %p')}")
        print(f"{'='*56}")

        # Small delay to ensure file is fully written
        time.sleep(1.5)

        # Copy to data/ as sales.csv (overwrite previous)
        dest = DATA_DIR / "sales.csv"
        try:
            shutil.copy2(csv_path, dest)
            # Also keep a timestamped backup
            backup = DATA_DIR / f"sales_{timestamp}.csv"
            shutil.copy2(csv_path, backup)
            print(f"  📂 Copied to: {dest}")
        except Exception as e:
            print(f"  ❌ Copy failed: {e}")
            return

        # Run the full pipeline
        from main import run_pipeline
        run_pipeline(csv_path=str(dest), send_mail=self.send_mail)

        # Move processed file to data/processed/
        processed_dir = INCOMING_DIR / "processed"
        processed_dir.mkdir(exist_ok=True)
        try:
            shutil.move(str(csv_path), str(processed_dir / f"{timestamp}_{csv_path.name}"))
            print(f"  ✅ Moved to processed: {processed_dir}")
        except Exception:
            pass


def start_watcher(send_mail: bool = True):
    """Start the folder watcher — blocks until Ctrl+C."""

    INCOMING_DIR.mkdir(exist_ok=True)

    print(f"""
╔══════════════════════════════════════════════════════════╗
║   👁️   AI SALES ANALYTICS — FOLDER WATCHER ACTIVE        ║
╚══════════════════════════════════════════════════════════╝

  📂  Watching folder:
      {INCOMING_DIR}

  🚀  Drop any  .csv  file here to trigger the pipeline!

  Pipeline: CSV → Clean → AI Insights → Dashboard → PDF → Email
  Press  Ctrl+C  to stop.

{'='*56}
""")

    if not WATCHDOG_OK:
        # Fallback: polling mode
        print("  ⚠️  watchdog not installed → using polling mode (checks every 5s)")
        _polling_watcher(send_mail)
        return

    handler  = SalesCSVHandler(send_mail=send_mail)
    observer = Observer()
    observer.schedule(handler, str(INCOMING_DIR), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n  🛑  Watcher stopped.")
    observer.join()


def _polling_watcher(send_mail: bool):
    """Fallback watcher that polls every 5 seconds."""
    seen = set()
    handler = SalesCSVHandler(send_mail=send_mail)

    while True:
        try:
            for f in INCOMING_DIR.glob("*.csv"):
                if str(f) not in seen:
                    seen.add(str(f))
                    handler._handle_csv(f)
            time.sleep(5)
        except KeyboardInterrupt:
            print("\n  🛑  Watcher stopped.")
            break
        except Exception as e:
            print(f"  ⚠️  Watcher error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AI Sales Analytics Folder Watcher")
    parser.add_argument("--no-email", action="store_true", help="Skip email step")
    args = parser.parse_args()
    start_watcher(send_mail=not args.no_email)
