# Architecture Decision Records — UBA Value Factors

**Handbook on Environmental Value Factors, MC 4.0 (December 2025)**

---

## Index

| ADR | Title | Status |
|-----|-------|--------|
| ADR-001 | Three-file pipeline pattern (config + pipeline + orchestrator) | Accepted |
| ADR-002 | Hard-code value factor data rather than parsing the PDF | Accepted |
| ADR-003 | Use CSV as primary output format (not HDF5) | Accepted |
| ADR-004 | Add Excel output with formatted header and Metadata sheet | Accepted |
| ADR-005 | Single orchestrator instead of per-table-group subprocesses | Accepted |
| ADR-006 | Provide individual tables/ entry-point scripts alongside orchestrator | Accepted |
| ADR-007 | One row per (substance × PRTP scenario) rather than wide format | Accepted |
| ADR-008 | Use extrasaction="ignore" in DictWriter for schema flexibility | Accepted |
| ADR-009 | Write timestamped execution log on each orchestrator run | Accepted |
| ADR-010 | Store source PDF in root; converted Markdown alongside it | Accepted |

---

## ADR-001 — Three-file pipeline pattern (config + pipeline + orchestrator)

**Status:** Accepted
**Date:** 2026-03-05

### Context

A clean separation of concerns is needed between table group metadata,
data definitions, and execution orchestration.

### Decision

Three core files implement the pipeline:

| File | Role |
|---|---|
| `config.py` | Table group metadata, output paths |
| `pipeline.py` | Data definitions + builder functions + public API |
| `extract_uba_values.py` | Orchestrator with argparse |

### Consequences

- Clear separation: configuration, data, and execution are in distinct files.
- Function signature `run_table(key) → Path` is the stable public API.

---

## ADR-002 — Hard-code value factor data rather than parsing the PDF

**Status:** Accepted
**Date:** 2026-03-05

### Context

The UBA handbook is a static, published document. Its tables have complex
multi-level headers (e.g. nested PRTP × component breakdowns) that are difficult
to parse programmatically from a PDF or Markdown conversion. The number of
distinct values is manageable (~546 rows across 10 table groups).

### Decision

All value factors are hard-coded as Python data structures (`list`, `dict`, `tuple`)
in `pipeline.py`. Builder functions (`_build_ghg_rows()`, etc.) convert these
structures to `list[dict]` for CSV/Excel writing.

Hard-coded data structures are verified once against the source PDF, eliminating
parsing errors at runtime.

### Consequences

- Zero parsing errors: data is verified once against the source PDF.
- Update procedure is manual (see DATA_UPDATES.md).
- Data and code are co-located in `pipeline.py` — a new reader can see exactly
  where each value comes from.

---

## ADR-003 — Use CSV as primary output format (not HDF5)

**Status:** Accepted
**Date:** 2026-03-05

### Context

UBA MC 4.0 data is fundamentally flat: each table group is a simple 2-D table
with O(10–150) rows and O(7–14) columns. No country or sector dimension is
present (UBA factors are Germany-specific, not disaggregated by region/sector).

### Decision

CSV is used as the primary output format. UTF-8 encoding, comma delimiter,
standard `csv.DictWriter` output.

### Consequences

- Output files are human-readable and importable into any tool (Excel, R, Python,
  LibreOffice).
- No dependency on PyTables / HDF5 libraries.
- Full data is always in the CSV; no truncation needed.

---

## ADR-004 — Add Excel output with formatted header and Metadata sheet

**Status:** Accepted
**Date:** 2026-03-05

### Context

Users working in Excel benefit from formatted headers and a Metadata sheet that
shows the publication source, unit, and scope of each table group.

### Decision

`pipeline._write_excel()` produces an `.xlsx` file alongside each CSV:
- Sheet 1 `"Value Factors"`: data with frozen header row and blue header fill.
- Sheet 2 `"Metadata"`: publication fields, table group description, unit, notes.

Implementation uses `openpyxl`.

### Consequences

- Both `.csv` and `.xlsx` are written on every `run_table()` call.
- Excel files are in `output/` alongside CSVs.
- Adding a third output format (e.g. Parquet) follows the same pattern in
  `_write_excel()`.

---

## ADR-005 — Single orchestrator instead of per-table-group subprocesses

**Status:** Accepted
**Date:** 2026-03-05

### Context

UBA table groups call in-memory builder functions (no file I/O per group) and
complete in < 0.1 s each. Total wall time is < 0.5 s for all 10 groups sequentially.

### Decision

`extract_uba_values.py` runs table groups sequentially in a simple `for` loop.
No `ThreadPoolExecutor`, no subprocess spawning.

### Consequences

- Simpler code; no race conditions or subprocess timeout edge cases.
- If groups were to become I/O-bound in a future version (e.g. reading from a live
  API), parallelism can be added without changing the `pipeline.run_table()` API.

---

## ADR-006 — Provide individual tables/ entry-point scripts alongside orchestrator

**Status:** Accepted
**Date:** 2026-03-05

### Context

Thin per-table-group wrapper scripts allow running a single table in isolation,
which is useful for development and debugging.

### Decision

`tables/NN_{key}.py` scripts are created for each of the 10 table groups,
each a four-line wrapper:

```python
sys.path.insert(0, str(Path(__file__).parent.parent))
import pipeline

if __name__ == "__main__":
    pipeline.run_table("{key}")
```

A `_template.py` is included for adding future table groups.

### Consequences

- Both `python tables/01_ghg.py` and `python extract_uba_values.py --only ghg`
  produce identical output.
- No code duplication: both paths call `pipeline.run_table()`.

---

## ADR-007 — One row per (substance × PRTP scenario) rather than wide format

**Status:** Accepted
**Date:** 2026-03-05

### Context

For GHG and many other table groups, UBA presents two columns: value at 0 % PRTP
and value at 1 % PRTP. A wide format would have both in one row (two value columns);
a long format adds a `prtp_pct` column and has two rows per substance.

### Decision

Long (tidy) format is used: each combination of `(substance, emission_year, prtp_pct)`
is a separate row. A `prtp_pct` column holds `0`, `1`, or `""` (for factors where PRTP
is not applicable, e.g. air pollutant health impacts).

### Consequences

- Easier filtering in Python/R: `df[df.prtp_pct == 0]`.
- Consistent column structure across all table groups even when PRTP does not apply.
- Slightly more rows, but all 10 CSVs remain well under 200 rows.

---

## ADR-008 — Use extrasaction="ignore" in DictWriter for schema flexibility

**Status:** Accepted
**Date:** 2026-03-05

### Context

Builder functions return `list[dict]` where rows may contain keys not present in
the `fieldnames` list (e.g. internal computation intermediates). Without
`extrasaction="ignore"`, `csv.DictWriter` raises `ValueError` on extra keys.

### Decision

All `csv.DictWriter` instances in `run_table()` use `extrasaction="ignore"`.
The explicit `fieldnames` list in `_BUILDERS` is the authoritative column schema.

### Consequences

- Builder functions can include debug/intermediate keys without breaking the writer.
- The CSV output is always governed by the `fieldnames` declaration in `_BUILDERS`,
  making column schema easy to inspect.

---

## ADR-009 — Write timestamped execution log on each orchestrator run

**Status:** Accepted
**Date:** 2026-03-05

### Context

A timestamped execution log creates an audit trail: which groups succeeded, which
failed, and when the extraction was last run.

### Decision

`extract_uba_values.py` writes `execution_log_{YYYYMMDD_HHMMSS}.txt` to the
project root at the end of each run:

```
UBA MC 4.0 Execution Log — 2026-03-05T...
────────────────────────────────────────────────────────────
[OK]   ghg
[OK]   air_pollutants
...
────────────────────────────────────────────────────────────
Total: 10/10 succeeded  wall-clock 0.3s
```

### Consequences

- Multiple log files accumulate over time. Add `execution_log_*.txt` to `.gitignore`
  to avoid committing them.
- The log file name is printed to stdout at the end of each run.

---

## ADR-010 — Store source PDF in root; converted Markdown alongside it

**Status:** Accepted
**Date:** 2026-03-05

### Context

The UBA source is a single PDF; the converted Markdown is a derived file used for
reference and QA.

### Decision

Both `UBA_Handbook on Environmental Value Factors.pdf` and the `.md` conversion
are stored in the project root. A `data/` subfolder is not created for a single file.

### Consequences

- Simple structure for a single-source project.
- If additional source files are added in the future (e.g. supplementary tables),
  a `data/` subfolder can be introduced without breaking any existing paths.

---

*Scripts: Dr Dimitrij Euler, Greenings (dimitrij.euler@greenings.org), with support of Claude Code (Anthropic) |
Handbook: Nadia Eser, Dr. Astrid Matthey, Dr. Björn Bünger — German Environment Agency (UBA), December 2025 | Document Version 1.0 | Last Updated 2026-03-05*
