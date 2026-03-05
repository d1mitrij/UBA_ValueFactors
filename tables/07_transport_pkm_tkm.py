"""07_transport_pkm_tkm.py — UBA MC 4.0 table group: transport_pkm_tkm

Run directly to extract this table group to CSV + Excel:
    python tables/07_transport_pkm_tkm.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import pipeline

if __name__ == "__main__":
    out = pipeline.run_table("transport_pkm_tkm")
    print(f"[OK] transport_pkm_tkm → {out}")
