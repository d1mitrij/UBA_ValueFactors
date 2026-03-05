# Validation Report — UBA Value Factors

**Handbook on Environmental Value Factors, MC 4.0 (December 2025)**

---

## Summary

All 10 table groups extracted successfully. The pipeline produced 10 CSV files
and 10 Excel files in `output/`.

| Total table groups | 10 |
|---|---|
| Successfully completed | 10 |
| Failed | 0 |
| Total rows extracted | 546 |

---

## Known-Good Reference Values

The following values can be used to validate a fresh pipeline run against the source PDF.
Any deviation from these figures indicates either a change in the source data or a
regression in `pipeline.py`.

### Table group 01 — ghg

| Substance | Emission year | PRTP % | Value | Unit |
|---|---|---|---|---|
| CO₂/CO₂-eq | 2020 | 0 | 935 | EUR_2025/t |
| CO₂/CO₂-eq | 2025 | 0 | **990** | EUR_2025/t |
| CO₂/CO₂-eq | 2025 | 1 | **345** | EUR_2025/t |
| CO₂/CO₂-eq | 2050 | 0 | 1,240 | EUR_2025/t |
| CH₄ | 2025 | 0 | 9,220 | EUR_2025/t |
| N₂O | 2025 | 0 | 282,300 | EUR_2025/t |
| N₂O | 2025 | 1 | 118,700 | EUR_2025/t |

### Table group 02 — air_pollutants

| Substance | Context | Component | Value | Unit |
|---|---|---|---|---|
| PM₂.₅ | unknown_source | health | **128,200** | EUR_2025/t |
| NOₓ | unknown_source | total | **37,740** | EUR_2025/t |
| SO₂ | unknown_source | total | 35,325 | EUR_2025/t |
| NH₃ | unknown_source | total | 30,275 | EUR_2025/t |
| PM₂.₅ | road_traffic, urban | health | 511,600 | EUR_2025/t |

### Table group 03 — electricity

| Energy source | Component | PRTP % | Value | Unit |
|---|---|---|---|---|
| German_electricity_mix_2024 | total_env_impacts | 0 | 34.76 | EUR-cent_2025/kWh_el |
| Lignite | total_env_impacts | 0 | 107.27 | EUR-cent_2025/kWh_el |
| Wind_energy | total_env_impacts | 0 | 1.95 | EUR-cent_2025/kWh_el |

### Table group 05 — refrigerants

| Refrigerant | GWP100 | PRTP % | Value | Unit |
|---|---|---|---|---|
| R-32 | 675 | 0 | 670 | EUR_2025/kg |
| R-410A | 2,088 | 0 | 2,070 | EUR_2025/kg |
| R-717 (NH₃) | 0 | 0 | 0 | EUR_2025/kg |

### Table group 06 — transport_vehkm

| Route | PRTP % | Vehicle | Specification | Total | Unit |
|---|---|---|---|---|---|
| all_routes | 0 | Car | Petrol | 30.91 | EUR-cent_2025/vehicle_km |
| all_routes | 0 | Car | Electric | 21.79 | EUR-cent_2025/vehicle_km |
| urban | 0 | Car | Diesel | 34.19 | EUR-cent_2025/vehicle_km |

### Table group 09 — nitrogen_phosphorus

| Substance | Pathway | PRTP % | Value | Unit |
|---|---|---|---|---|
| NOₓ | air | — | 124 | EUR_2025/kg N |
| Phosphorus | inland_waters | — | 437 | EUR_2025/kg |

### Table group 10 — agriculture

| Item | PRTP % | Value | Unit |
|---|---|---|---|
| Beef_slaughter_weight | 0 | 52.40 | EUR_2025/kg |
| Milk | 0 | 1.35 | EUR_2025/kg |
| Nitrogen (surplus) | 0 | 28.82 | EUR_2025/kg |

---

## Row Counts by Table Group

These counts are verified against the source PDF and should not change between
runs on the same `pipeline.py` data.

| Script | Table group | Expected rows |
|---|---|---|
| `01_ghg.py` | ghg | 54 |
| `02_air_pollutants.py` | air_pollutants | 133 |
| `03_electricity.py` | electricity | 45 |
| `04_heat.py` | heat | 45 |
| `05_refrigerants.py` | refrigerants | 16 |
| `06_transport_vehkm.py` | transport_vehkm | 142 |
| `07_transport_pkm_tkm.py` | transport_pkm_tkm | 38 |
| `08_noise.py` | noise | 42 |
| `09_nitrogen_phosphorus.py` | nitrogen_phosphorus | 11 |
| `10_agriculture.py` | agriculture | 20 |
| **Total** | | **546** |

---

## Validation Procedure

### Step 1 — Run all table groups

```bash
python extract_uba_values.py
```

Expected output: `Done: 10/10 succeeded, 0 failed`.

### Step 2 — Verify CO₂ reference value in Python

```python
import pandas as pd

ghg = pd.read_csv("output/01_uba4_ghg.csv")
co2_2025_0pct = ghg.query(
    "substance == 'CO2_CO2eq' and emission_year == 2025 and prtp_pct == 0"
)["value_factor"].iloc[0]
print(co2_2025_0pct)
# Expected: 990
assert co2_2025_0pct == 990, f"Reference value mismatch: {co2_2025_0pct}"
```

### Step 3 — Verify PM₂.₅ reference value

```python
ap = pd.read_csv("output/02_uba4_air_pollutants.csv")
pm25_health = ap.query(
    "substance == 'PM2.5' and context == 'unknown_source' and impact_component == 'health'"
)["value_factor"].iloc[0]
print(pm25_health)
# Expected: 128200
assert pm25_health == 128200, f"Reference value mismatch: {pm25_health}"
```

### Step 4 — Verify row counts

```python
import pandas as pd
from pathlib import Path

expected = {
    "01_uba4_ghg.csv": 54,
    "02_uba4_air_pollutants.csv": 133,
    "03_uba4_electricity.csv": 45,
    "04_uba4_heat.csv": 45,
    "05_uba4_refrigerants.csv": 16,
    "06_uba4_transport_vehkm.csv": 142,
    "07_uba4_transport_pkm_tkm.csv": 38,
    "08_uba4_noise.csv": 42,
    "09_uba4_nitrogen_phosphorus.csv": 11,
    "10_uba4_agriculture.csv": 20,
}
for fname, n in expected.items():
    actual = len(pd.read_csv(f"output/{fname}"))
    status = "OK" if actual == n else f"MISMATCH (got {actual})"
    print(f"  {fname:<45} {status}")
```

### Step 5 — Verify Excel output

```python
import openpyxl
wb = openpyxl.load_workbook("output/01_uba4_ghg.xlsx")
print(wb.sheetnames)           # → ['Value Factors', 'Metadata']
ws = wb["Value Factors"]
print(ws.max_row - 1)          # → 54 data rows
```

### Step 6 — Check execution log

Verify the `execution_log_*.txt` file shows all `[OK]` entries and the
expected wall-clock time (< 1 s for all 10 groups).

---

## QA Checks Built Into the Pipeline

| Check | Where | Action on failure |
|---|---|---|
| `key` exists in `_BUILDERS` | `run_table()` | `KeyError` raised |
| Output directory created if missing | `run_table()` | `mkdir(parents=True)` |
| Excel Metadata sheet written | `_write_excel()` | Sheet present in every xlsx |
| Execution log written | `extract_uba_values.py` | Log created even on partial failure |

---

*Scripts: Dr Dimitrij Euler, Greenings (dimitrij.euler@greenings.org), with support of Claude Code (Anthropic) |
Handbook: Nadia Eser, Dr. Astrid Matthey, Dr. Björn Bünger — German Environment Agency (UBA), December 2025 | Document Version 1.0 | Last Updated 2026-03-05*
