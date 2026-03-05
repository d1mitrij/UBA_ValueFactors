# Data Updates — UBA Value Factors

**Handbook on Environmental Value Factors, MC 4.0 (December 2025)**

---

## Overview

Updates to this dataset may arise from three sources:

1. **New MC version** — UBA publishes a revised Methodological Convention
   (e.g. MC 4.1 or MC 5.0) with updated value factors.
2. **Correction notice** — UBA issues an erratum or corrigendum to MC 4.0.
3. **Additional table groups** — a future MC version adds new impact categories
   (e.g. soil contamination, water scarcity).

---

## 1. Updating Value Factors (new MC version or correction)

### Step 1 — Identify changed tables

Compare the new handbook PDF against `pipeline.py`. UBA typically marks
revised values in the publication changelog or revision notes.

### Step 2 — Update pipeline.py data structures

Each table group has a clearly named data structure in `pipeline.py`:

| Table group | Data structure |
|---|---|
| ghg | `_GHG_DATA` |
| air_pollutants | `_AIR_TABLE2`, `_AIR_TABLE3`, `_AIR_TABLE4` |
| electricity | `_ELECTRICITY_DATA` |
| heat | `_HEAT_DATA` |
| refrigerants | `_REFRIGERANT_DATA` |
| transport_vehkm | `_TRANSPORT_VEHKM` |
| transport_pkm_tkm | `_OCCUPATION_DATA`, `_PKTKM_DATA` |
| noise | `_NOISE_ANNOYANCE`, `_NOISE_COGNITIVE_CHILDREN` |
| nitrogen_phosphorus | `_NP_DATA` |
| agriculture | `_AGRI_PRODUCTS`, `_AGRI_FERTILIZER`, `_AGRI_SURPLUS` |

Edit the relevant structure, preserving the tuple/dict format.

### Step 3 — Update publication metadata

Edit `config.py`, section `PUBLICATION`:

```python
PUBLICATION = {
    "title":      "Handbook on Environmental Value Factors",
    "subtitle":   "Methodological Convention 4.1 ...",  # ← update
    "year":       2026,                                  # ← update
    "month":      "June",                               # ← update
    "issn":       "2363-832X",
    "price_base": "EUR_2026",                           # ← update if price base changes
}
```

Also update `config.py` output filename pattern if the version identifier changes:

```python
filename = f"{cfg['id']:>02}_uba4_{key}.csv"   # keep "uba4" for MC 4.x; change to "uba5" for MC 5.0
```

### Step 4 — Re-run the pipeline

```bash
python extract_uba_values.py
```

### Step 5 — Validate reference values

Run the validation procedure from VALIDATION_REPORT.md:

```python
import pandas as pd
ghg = pd.read_csv("output/01_uba4_ghg.csv")
co2_2025 = ghg.query("substance=='CO2_CO2eq' and prtp_pct==0 and emission_year==2025")
print(co2_2025["value_factor"].iloc[0])
# MC 4.0 reference: 990 EUR_2025/t
# Update VALIDATION_REPORT.md if this changes
```

---

## 2. Adding a New Table Group

When a future MC version introduces a new impact category:

### Step 1 — Add to config.py

```python
TABLE_GROUPS = {
    ...
    "new_category": {
        "id":          "11",
        "title":       "New Impact Category",
        "chapter":     8,
        "tables":      ["Table 28"],
        "description": "Description of new category",
        "unit":        "EUR_2025/unit",
        "notes":       "Source and methodology notes.",
    },
}
```

### Step 2 — Add data and builder to pipeline.py

```python
_NEW_DATA = [
    # (field1, field2, value_factor)
    ("item_a", ..., 42.0),
]

def _build_new_rows() -> list[dict]:
    rows = []
    for rec in _NEW_DATA:
        f1, f2, vf = rec
        rows.append({"source_table": "Table 28", "chapter": 8,
                     "field1": f1, "field2": f2, "value_factor": vf,
                     "unit": "EUR_2025/unit"})
    return rows
```

Then register it in `_BUILDERS`:

```python
_BUILDERS = {
    ...
    "new_category": (_build_new_rows, ["source_table","chapter","field1","field2","value_factor","unit"]),
}
```

### Step 3 — Create the entry-point script

```bash
cp tables/_template.py tables/11_new_category.py
# Edit KEY = "new_category" inside the file
```

### Step 4 — Verify

```bash
python tables/11_new_category.py
python extract_uba_values.py --list
python extract_uba_values.py --only new_category
```

---

## 3. Replacing the Source PDF

If a new PDF is released (corrected or updated MC version):

1. Place the new PDF in the project root.
2. Run `pdf_to_md.py` to regenerate the Markdown conversion:
   ```bash
   python pdf_to_md.py "UBA_Handbook on Environmental Value Factors v2.pdf"
   ```
3. Use the Markdown file to verify value factor data in `pipeline.py`.
4. Keep the old PDF with a version suffix (e.g. rename to
   `UBA_Handbook_MC40_2025.pdf`) for audit purposes.

---

## 4. Update Checklist

Use this checklist before committing updated outputs:

- [ ] Source PDF version confirmed (title page, ISSN, year)
- [ ] `config.py` `PUBLICATION` dict updated
- [ ] All changed `_DATA` structures in `pipeline.py` updated
- [ ] All 10 table groups ran to completion (no `[FAIL]` in execution log)
- [ ] CO₂/2025/0%-PRTP value factor matches new handbook table
- [ ] VALIDATION_REPORT.md reference values table updated if values changed
- [ ] METHODOLOGY.md updated if methodology or sources changed
- [ ] Old execution logs archived or deleted

---

*Document Version 1.0 | Last Updated 2026-03-05 | Maintained by Greenings | Contact: dimitrij.euler@greenings.org*
