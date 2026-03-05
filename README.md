# UBA Value Factors

**Handbook on Environmental Value Factors — Methodological Convention 4.0 (December 2025)**

Author: Dr Dimitrij Euler, [Greenings](https://greenings.org) — dimitrij.euler@greenings.org

---

## Overview

This repository extracts all monetary value factors from the German Environment Agency
(Umweltbundesamt, UBA) **Handbook on Environmental Value Factors, MC 4.0** (December 2025)
and writes them to structured CSV and Excel files in `output/`.

The pipeline architecture mirrors the
[steen-vf1/eps_value_factors](../steen-vf1/eps_value_factors) project:
a `config.py` → `pipeline.py` → orchestrator pattern, with individual per-table-group
entry-point scripts under `tables/`.

### Publication

| Field | Value |
|---|---|
| Title | Handbook on Environmental Value Factors |
| Subtitle | Methodological Convention 4.0 for the Assessment of Environmental Impacts |
| Authors | Nadia Eser, Dr. Astrid Matthey, Dr. Björn Bünger |
| Publisher | German Environment Agency (UBA), Dessau-Roßlau |
| Year | December 2025 |
| ISSN | 2363-832X |
| Price base | EUR_2025 |

---

## Table Groups

| ID | Key | Chapter | Tables | Title | Unit |
|----|-----|---------|--------|-------|------|
| 01 | `ghg` | 2 | Table 1 | Greenhouse Gas Emissions | EUR_2025/t |
| 02 | `air_pollutants` | 3 | Tables 2–4 | Air Pollutant Emissions | EUR_2025/t |
| 03 | `electricity` | 4 | Table 5 | Electric Power Generation | EUR-cent_2025/kWh_el |
| 04 | `heat` | 4 | Table 6 | Heat Generation | EUR-cent_2025/kWh_final_energy |
| 05 | `refrigerants` | 4 | Table 7 | Refrigerants | EUR_2025/kg_refrigerant |
| 06 | `transport_vehkm` | 5 | Tables 8–16 | Transport — per vehicle km | EUR-cent_2025/vehicle_km |
| 07 | `transport_pkm_tkm` | 5 | Tables 17–18 | Transport — per Pkm or tkm | EUR-cent_2025/Pkm_or_tkm |
| 08 | `noise` | 5 | Tables 19–20 | Traffic Noise | EUR_2025/person/year |
| 09 | `nitrogen_phosphorus` | 6 | Tables 22–24 | Nitrogen and Phosphorus Emissions | EUR_2025/kg |
| 10 | `agriculture` | 7 | Tables 25–27 | Agriculture | EUR_2025/kg |

---

## Output format

Each table group produces two files in `output/`:

| File | Contents |
|---|---|
| `NN_uba4_{key}.csv` | Full value factor table (UTF-8 CSV) |
| `NN_uba4_{key}.xlsx` | Same data with formatted header + Metadata sheet |

### Key value factors at a glance

| Substance | 0 % PRTP | 1 % PRTP | Unit |
|---|---|---|---|
| CO₂/CO₂-eq (2025 emission year) | 990 | 345 | EUR_2025/t |
| CH₄ (2025) | 9,220 | 5,800 | EUR_2025/t |
| N₂O (2025) | 282,300 | 118,700 | EUR_2025/t |
| PM₂.₅ (unknown source, health) | 128,200 | — | EUR_2025/t |
| NOₓ (unknown source, total) | 37,740 | — | EUR_2025/t |
| NH₃ (unknown source, total) | 30,275 | — | EUR_2025/t |

---

## Usage

### Run all table groups

```bash
python extract_uba_values.py
```

### Run a single table group

```bash
python tables/01_ghg.py
```

### Filter to specific groups

```bash
python extract_uba_values.py --only ghg air_pollutants noise
```

### List available table groups

```bash
python extract_uba_values.py --list
```

### Convert the source PDF to Markdown

```bash
python pdf_to_md.py          # marker-pdf (high quality, ML-based)
python pdf_to_md.py --fast   # pymupdf4llm (faster)
```

### Read output in Python

```python
import pandas as pd

ghg = pd.read_csv("output/01_uba4_ghg.csv")
# Filter: CO2, 0% PRTP, 2025 emission year
co2_2025 = ghg.query("substance == 'CO2_CO2eq' and prtp_pct == 0 and emission_year == 2025")
print(co2_2025["value_factor"].iloc[0])   # → 990
```

---

## Dependencies

```bash
pip install openpyxl          # Excel output
pip install marker-pdf        # PDF→MD (high quality)
pip install pymupdf4llm       # PDF→MD (fast fallback)
```

---

## Source

> Eser, N., Matthey, A., Bünger, B. (2025). *Handbook on Environmental Value Factors.
> Methodological Convention 4.0 for the Assessment of Environmental Impacts.*
> German Environment Agency (UBA), Dessau-Roßlau. ISSN 2363-832X.

---

## Relation to steen-vf1 / transitionvaluation

| steen-vf1 | uba1 | Note |
|---|---|---|
| `config.py` → `INDICATORS` dict | `config.py` → `TABLE_GROUPS` dict | Same pattern |
| `pipeline.run_indicator(key)` | `pipeline.run_table(key)` | Same signature |
| `indicators/NNN_*.py` | `tables/NN_*.py` | Same thin-wrapper pattern |
| `run_all_eps_factors.py` | `extract_uba_values.py` | Same orchestrator pattern |
| HDF5 + Excel output | CSV + Excel output | UBA data is flat (no country×sector matrix) |
| `execution_log_*.txt` | `execution_log_*.txt` | Same timestamped log format |

---

*Generated with [Claude Code](https://claude.ai/claude-code)*
