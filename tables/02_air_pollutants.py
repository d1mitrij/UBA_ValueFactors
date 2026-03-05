"""02_air_pollutants.py — UBA MC 4.0 table group: air_pollutants

Run directly to extract this table group to CSV + Excel:
    python tables/02_air_pollutants.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import pipeline

if __name__ == "__main__":
    out = pipeline.run_table("air_pollutants")
    print(f"[OK] air_pollutants → {out}")
