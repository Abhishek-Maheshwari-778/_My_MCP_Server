"""
Power BI Export Module
Generates a highly optimized dataset and a .pbids connection file.
"""
import sys
import json
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import CLEANED_CSV, REPORTS_DIR

def generate_pbi_export(input_path=None, output_pbids=None):
    input_path   = input_path   or CLEANED_CSV
    output_pbids = output_pbids or REPORTS_DIR / "analytics.pbids"
    domain       = os.environ.get("DATA_DOMAIN", "Sales")
    
    print(f"\n{'='*50}")
    print("  POWER BI EXPORT GENERATION STARTED")
    
    # Generate PBIDS content
    pbids_content = {
        "version": "0.1",
        "connections": [
            {
                "details": {
                    "protocol": "file",
                    "address": {
                        "path": str(Path(input_path).resolve())
                    }
                },
                "options": {},
                "mode": "Import"
            }
        ]
    }
    
    with open(output_pbids, "w", encoding="utf-8") as f:
        json.dump(pbids_content, f, indent=4)
        
    print(f"  Power BI Connector (.pbids) generated!")
    print(f"  Path: {output_pbids}")
    print(f"  (Double click to open instantly in Power BI)")
    print(f"{'='*50}\n")
    
    return str(output_pbids)

if __name__ == "__main__":
    generate_pbi_export()
