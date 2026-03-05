"""
Template for a per-table-group entry-point script.

Copy this file, rename it (e.g. 01_ghg.py), change the KEY constant,
and run it directly to extract that table group to CSV + Excel.

Usage:
    python tables/01_ghg.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import pipeline

KEY = "CHANGE_ME"   # e.g. "ghg", "air_pollutants", …

if __name__ == "__main__":
    out = pipeline.run_table(KEY)
    print(f"[OK] {KEY} → {out}")
