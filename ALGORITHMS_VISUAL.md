# Algorithms and Pipeline Visualisation — UBA Value Factors

**Handbook on Environmental Value Factors, MC 4.0 (December 2025)**

---

## 1. End-to-End Pipeline Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    UBA Value Factors Pipeline                        │
└─────────────────────────────────────────────────────────────────────┘

  SOURCE                    STAGE                    OUTPUT
  ──────                    ─────                    ──────

  config.py            ─→  [1] CONFIGURATION     ─→  cfg dict
  TABLE_GROUPS dict         get_table_config()        key, title, chapter,
                                                      tables, unit, notes,
                                                      csv_path, excel_path

  pipeline.py          ─→  [2] DATA BUILDER      ─→  rows: list[dict]
  _DATA structures          _build_*_rows()           one dict per
  (hard-coded tuples)       e.g. _build_ghg_rows()    observation
                            _BUILDERS dispatch

  rows                 ─→  [3] CSV EXPORT        ─→  NN_uba4_{key}.csv
  fieldnames                csv.DictWriter            UTF-8, comma-delim

  rows + cfg           ─→  [4] EXCEL EXPORT      ─→  NN_uba4_{key}.xlsx
                            _write_excel()            "Value Factors" sheet
                                                      "Metadata" sheet

  results / errors     ─→  [5] EXECUTION LOG     ─→  execution_log_{ts}.txt
                            datetime stamp            [OK]/[FAIL] per group
```

---

## 2. Configuration Stage Detail

```
  config.TABLE_GROUPS["ghg"]
        │
        ├─── id:          "01"
        ├─── title:       "Greenhouse Gas Emissions"
        ├─── chapter:     2
        ├─── tables:      ["Table 1"]
        ├─── description: "Social cost of CO2/CO2-eq, CH4 and N2O …"
        ├─── unit:        "EUR_2025/t"
        └─── notes:       "Two PRTP scenarios …"

  get_table_config("ghg")
        │
        └─── adds:
             ├─── key:        "ghg"
             ├─── csv_path:   output/01_uba4_ghg.csv
             ├─── excel_path: output/01_uba4_ghg.xlsx
             └─── publication: {title, subtitle, authors, …}
```

---

## 3. Data Builder Stage Detail

### 3a. Builder dispatch table

```
  _BUILDERS = {
      "ghg":               (_build_ghg_rows,            fieldnames_ghg),
      "air_pollutants":    (_build_air_rows,             fieldnames_air),
      "electricity":       (_build_electricity_rows,     fieldnames_elec),
      "heat":              (_build_heat_rows,            fieldnames_heat),
      "refrigerants":      (_build_refrigerant_rows,     fieldnames_refrig),
      "transport_vehkm":   (_build_transport_vehkm_rows, fieldnames_tvk),
      "transport_pkm_tkm": (_build_transport_pkm_rows,   fieldnames_tpkm),
      "noise":             (_build_noise_rows,           fieldnames_noise),
      "nitrogen_phosphorus":(_build_np_rows,             fieldnames_np),
      "agriculture":       (_build_agriculture_rows,     fieldnames_agri),
  }
```

### 3b. GHG builder flow

```
  _GHG_DATA  →  list of 9 tuples
  (year, co2_0, co2_1, ch4_0, ch4_1, n2o_0, n2o_1)

  _build_ghg_rows():
        │
        └── for each tuple:
              ├── row(CO2_CO2eq, prtp=0, value=co2_0)
              ├── row(CO2_CO2eq, prtp=1, value=co2_1)
              ├── row(CH4, prtp=0, value=ch4_0)
              ├── row(CH4, prtp=1, value=ch4_1)
              ├── row(N2O, prtp=0, value=n2o_0)
              └── row(N2O, prtp=1, value=n2o_1)

  9 emission years × 6 rows = 54 rows
```

### 3c. Air pollutant builder flow

```
  _AIR_TABLE2 (7 substances)  →  4 rows each (health, crop, material, total)
                                 = 28 rows

  _AIR_TABLE3 (11 source configs × 7 substances)
              →  1 row each (health only)
              = 77 rows

  _AIR_TABLE4 (4 surroundings × 7 substances)
              →  1 row each (health only, incl. PM10_abrasion)
              = 28 rows

  Total: 28 + 77 + 28 = 133 rows
```

### 3d. Transport vehkm builder flow

```
  _TRANSPORT_VEHKM  →  list of tuples
  (route, prtp, vehicle, spec, ghg, ap_ex, ap_ab, infra, energy, total)

  table_map:
      (all_routes, 0) → "Table 9"
      (all_routes, 1) → "Table 10"
      (motorway,   0) → "Table 11"
      (motorway,   1) → "Table 12"
      (rural,      0) → "Table 13"
      (rural,      1) → "Table 14"
      (urban,      0) → "Table 15"
      (urban,      1) → "Table 16"

  _build_transport_vehkm_rows():
        └── for each tuple:
              └── one row with all 6 components exploded as columns

  23 vehicles × 2 routes groups × 2 PRTP (approx) = 142 rows
  (air/waterway modes only in all_routes; fewer in route-specific tables)
```

---

## 4. CSV Export Stage

```
  run_table(key)
        │
        ├── cfg = config.get_table_config(key)
        ├── out_path = cfg["csv_path"]
        ├── out_path.parent.mkdir(parents=True, exist_ok=True)
        │
        ├── builder_fn, fieldnames = _BUILDERS[key]
        ├── rows = builder_fn()
        │
        └── open(out_path, "w", newline="", encoding="utf-8")
              └── csv.DictWriter(fieldnames, extrasaction="ignore")
                    ├── writeheader()
                    └── writerows(rows)
```

`extrasaction="ignore"` allows builder functions to include extra keys
without raising `ValueError` — the `fieldnames` list is the authoritative schema.

---

## 5. Excel Export Stage

```
  _write_excel(rows, fieldnames, cfg)
        │
        ├── wb = openpyxl.Workbook()
        │
        ├── ws "Value Factors"
        │     ├── row 1: header (blue fill, white bold font, frozen)
        │     └── rows 2+: data (ws.cell per field per row)
        │
        └── ws "Metadata"
              ├── publication fields (title, subtitle, authors, …)
              ├── table group fields (title, chapter, tables, unit)
              └── notes / description

  wb.save(excel_path)
```

---

## 6. Orchestrator Flow

```
  extract_uba_values.py
        │
        ├── [argparse]   --only KEY [KEY ...]   (optional filter)
        │                --list                  (list and exit)
        │
        ├── [header]     print publication metadata
        │
        ├── [loop]       for key in keys:
        │                    t1 = time.time()
        │                    out = pipeline.run_table(key)
        │                    print [OK] / [FAIL]
        │
        ├── [summary]    Done: N/10 succeeded, M failed  (Xs)
        │                Output files: name → rows
        │
        └── [log]        execution_log_{YYYYMMDD_HHMMSS}.txt
                         [OK]   key
                         [FAIL] key — exception message
                         Total: N/10 succeeded  wall-clock Xs
```

---

## 7. Individual Table Script Flow

```
  tables/01_ghg.py
        │
        ├── sys.path.insert(0, parent_dir)
        ├── import pipeline
        └── pipeline.run_table("ghg")
              │
              └── (same as orchestrator loop body above)
```

Identical output to `python extract_uba_values.py --only ghg`.

---

## 8. Per-Table-Group Summary

| ID | Key | Rows | Source structures | Builder |
|----|-----|------|-------------------|---------|
| 01 | ghg | 54 | `_GHG_DATA` (9 tuples) | `_build_ghg_rows` |
| 02 | air_pollutants | 133 | `_AIR_TABLE2/3/4` | `_build_air_rows` |
| 03 | electricity | 45 | `_ELECTRICITY_DATA` (9 tuples) | `_build_electricity_rows` |
| 04 | heat | 45 | `_HEAT_DATA` (9 tuples) | `_build_heat_rows` |
| 05 | refrigerants | 16 | `_REFRIGERANT_DATA` (8 tuples) | `_build_refrigerant_rows` |
| 06 | transport_vehkm | 142 | `_TRANSPORT_VEHKM` (~142 tuples) | `_build_transport_vehkm_rows` |
| 07 | transport_pkm_tkm | 38 | `_OCCUPATION_DATA`, `_PKTKM_DATA` | `_build_transport_pkm_rows` |
| 08 | noise | 42 | `_NOISE_ANNOYANCE`, `_NOISE_COGNITIVE_CHILDREN` | `_build_noise_rows` |
| 09 | nitrogen_phosphorus | 11 | `_NP_DATA` | `_build_np_rows` |
| 10 | agriculture | 20 | `_AGRI_PRODUCTS`, `_AGRI_FERTILIZER`, `_AGRI_SURPLUS` | `_build_agriculture_rows` |

---

## 9. Data Structure Formats

### GHG (tuple list)

```python
_GHG_DATA = [
    # (year, co2_0pct, co2_1pct, ch4_0pct, ch4_1pct, n2o_0pct, n2o_1pct)
    (2025, 990, 345, 9_220, 5_800, 282_300, 118_700),
]
```

### Air pollutants — Table 2 (dict)

```python
_AIR_TABLE2 = {
    # substance: (health, crop, material_building, total)
    "PM2.5": (128_200, 0, 0, 128_200),
}
```

### Air pollutants — Table 3 (nested dict)

```python
_AIR_TABLE3 = {
    # (sector, surroundings, height): {substance: value}
    ("power_station", "unspecified", ">100"): {
        "PM2.5": 66_900, "NOx": 28_800, ...
    },
}
```

### Transport vehkm (tuple list)

```python
_TRANSPORT_VEHKM = [
    # (route, prtp, vehicle, spec, ghg, ap_ex, ap_ab, infra, energy, total)
    ("all_routes", 0, "Car", "Petrol", 16.09, 0.46, 0.20, 8.00, 6.15, 30.91),
]
```

---

*Scripts: Dr Dimitrij Euler, Greenings (dimitrij.euler@greenings.org), with support of Claude Code (Anthropic) |
Handbook: Nadia Eser, Dr. Astrid Matthey, Dr. Björn Bünger — German Environment Agency (UBA), December 2025 | Document Version 1.0 | Last Updated 2026-03-05*
