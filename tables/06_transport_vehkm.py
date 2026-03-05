"""06_transport_vehkm.py — UBA MC 4.0 table group: transport_vehkm

Run directly to extract this table group to CSV + Excel:
    python tables/06_transport_vehkm.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import pipeline

if __name__ == "__main__":
    out = pipeline.run_table("transport_vehkm")
    print(f"[OK] transport_vehkm → {out}")
