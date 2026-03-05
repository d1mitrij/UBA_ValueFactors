# Input Files Methodology — UBA Value Factors

**Handbook on Environmental Value Factors, MC 4.0 (December 2025)**

---

## Overview

The single primary input is the official UBA handbook:

> Eser, N., Matthey, A., Bünger, B. (2025).
> *Handbook on Environmental Value Factors.
> Methodological Convention 4.0 for the Assessment of Environmental Impacts.*
> German Environment Agency (UBA), Dessau-Roßlau. ISSN 2363-832X.

The handbook is distributed as a PDF. A Markdown conversion is available as a
derived file for reference and QA.

| File | Role |
|------|------|
| `UBA_Handbook on Environmental Value Factors.pdf` | Primary source (1.7 MB, 75 pages) |
| `UBA_Handbook on Environmental Value Factors.md` | Derived Markdown conversion (for reference) |

---

## Handbook Structure

The handbook contains 12 chapters and 31 tables. The pipeline covers the
**31 tables across Chapters 2–7** (core value factor tables).

### Chapter 1 — Introduction
Overview of the methodological convention. Not parsed.

### Chapter 2 — Greenhouse Gas Emissions (Table 1)

**Table 1:** Social cost per tonne GHG by emission year and PRTP scenario.

| Column | Description |
|---|---|
| Emission year | 2020, 2025–2030 (annual), 2040, 2050 |
| CO₂/CO₂-eq — 0 % PRTP | Social cost in EUR_2025/t |
| CO₂/CO₂-eq — 1 % PRTP | Social cost in EUR_2025/t |
| CH₄ — 0 % PRTP | Social cost in EUR_2025/t |
| CH₄ — 1 % PRTP | Social cost in EUR_2025/t |
| N₂O — 0 % PRTP | Social cost in EUR_2025/t |
| N₂O — 1 % PRTP | Social cost in EUR_2025/t |

### Chapter 3 — Air Pollutant Emissions (Tables 2–4)

**Table 2:** Average value factors for unknown sources (7 substances × 4 components).

**Table 3:** Differentiated VF for stationary combustion (7 substances × 11 source
configurations defined by sector × surroundings × emission height).

**Table 4:** VF for road traffic emissions (7 substances + PM₁₀ abrasion ×
4 surroundings types).

### Chapter 4 — Energy and Refrigerants (Tables 5–7)

**Table 5:** Electricity generation — 9 energy sources × 5 components × 2 PRTP.
**Table 6:** Heat generation — 9 heat sources × 5 components × 2 PRTP.
**Table 7:** Refrigerants — 8 refrigerants × GWP100 × value factor at 2 PRTP.

### Chapter 5 — Transport (Tables 8–20)

**Table 8:** Overview (not parsed separately; subsumed in Tables 9–16 data).
**Tables 9–16:** Per-vehicle-km factors — 4 route types × 2 PRTP × ~14 vehicle types
× 6 components.
**Table 17:** Occupation/utilization rates.
**Table 18:** Per-Pkm/tkm factors.
**Table 19:** Noise annoyance value factors by dB class.
**Table 20:** Cognitive impairment in children by dB class.
**Table 21:** Not parsed (supplementary notes on noise methodology).

### Chapter 6 — Nitrogen and Phosphorus (Tables 22–24)

**Table 22:** N air emissions — 4 rows (NOₓ, NH₃, N₂O × 2 PRTP).
**Table 23:** N and P water emissions — 5 rows by water body type.
**Table 24:** N and P surface water (unknown limiting substance) — 2 rows.

### Chapter 7 — Agriculture (Tables 25–27)

**Table 25:** Animal products — 7 products × 2 PRTP.
**Table 26:** Fertilizer application — N × 2 PRTP + P.
**Table 27:** Nutrient surplus — N × 2 PRTP + P.

### Chapters 8–12 — Not parsed

| Chapter | Content | Why not parsed |
|---|---|---|
| 8 | Building materials (Tables 28–29) | Illustrative only; no standalone VF recommended by UBA |
| 9–10 | Methodology supplements | No tabulated VF |
| 11 | Literature | No tabulated VF |
| 12 | Appendix (Tables 30–31: Euronorm transport) | Appendix reference data, not primary VF |

---

## PDF Conversion

The PDF can be converted to Markdown using `pdf_to_md.py`:

```bash
# High quality (ML-based, marker-pdf):
python pdf_to_md.py

# Fast (pymupdf4llm):
python pdf_to_md.py --fast

# Custom paths:
python pdf_to_md.py path/to/input.pdf --out path/to/output.md
```

### Conversion quality notes

- **marker-pdf** (default): preserves table structure well; footnotes and
  multi-column layouts handled correctly.
- **pymupdf4llm** (fallback): faster; basic table support; some table merging
  artefacts in multi-column layouts.

Both converters may misread numeric values in tables with thin borders or merged
cells. Always verify extracted values against the original PDF.

---

## Data Extraction Methodology

Because PDF table parsing is imperfect, all value factors are **manually transcribed**
from the PDF into `pipeline.py` data structures. The transcription process:

1. Read the PDF (or its Markdown conversion) for each table.
2. Enter values into the appropriate `_DATA` structure in `pipeline.py`.
3. Cross-check row/column totals where available (e.g. total transport VF =
   sum of components).
4. Run `extract_uba_values.py` and verify output CSV against the PDF.

This approach mirrors steen-vf1's special-parser methodology for the three
non-standard EPS sheets (fossil resources, radionuclides, waste) where cell
positions are hard-coded.

---

## Source File Validation Checklist

Before a pipeline run, verify:

- [ ] PDF file name matches `pdf_to_md.DEFAULT_PDF` in `pdf_to_md.py`
- [ ] PDF title page reads "Methodological Convention 4.0" and "December 2025"
- [ ] ISSN on cover reads "2363-832X"
- [ ] CO₂ value factor for 2025 emission year, 0 % PRTP = 990 EUR_2025/t (Table 1)
- [ ] PM₂.₅ average health VF = 128,200 EUR_2025/t (Table 2)

---

*Document Version 1.0 | Last Updated 2026-03-05 | Maintained by Greenings | Contact: dimitrij.euler@greenings.org*
