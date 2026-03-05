"""05_refrigerants.py — UBA MC 4.0 table group: refrigerants

Run directly to extract this table group to CSV + Excel:
    python tables/05_refrigerants.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import pipeline

if __name__ == "__main__":
    out = pipeline.run_table("refrigerants")
    print(f"[OK] refrigerants → {out}")
