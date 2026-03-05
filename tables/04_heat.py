"""04_heat.py — UBA MC 4.0 table group: heat

Run directly to extract this table group to CSV + Excel:
    python tables/04_heat.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import pipeline

if __name__ == "__main__":
    out = pipeline.run_table("heat")
    print(f"[OK] heat → {out}")
