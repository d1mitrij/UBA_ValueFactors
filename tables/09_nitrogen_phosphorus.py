"""09_nitrogen_phosphorus.py — UBA MC 4.0 table group: nitrogen_phosphorus

Run directly to extract this table group to CSV + Excel:
    python tables/09_nitrogen_phosphorus.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import pipeline

if __name__ == "__main__":
    out = pipeline.run_table("nitrogen_phosphorus")
    print(f"[OK] nitrogen_phosphorus → {out}")
