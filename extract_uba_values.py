"""
extract_uba_values.py — UBA Methodological Convention 4.0 (December 2025)

Orchestrator script — extracts all value factors from the UBA Handbook on Environmental Value Factors
(MC 4.0, December 2025) and writes one CSV per table group to the output/ folder.

Usage:
    python extract_uba_values.py                    # extract all 10 table groups
    python extract_uba_values.py --only ghg air_pollutants
    python extract_uba_values.py --list             # list available table groups
"""

import argparse
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import config
import pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)-8s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _list_groups():
    print(f"\n{'ID':<4} {'Key':<25} {'Chapter':<9} {'Title'}")
    print("-" * 70)
    for key, cfg in config.TABLE_GROUPS.items():
        print(f"{cfg['id']:<4} {key:<25} ch.{cfg['chapter']:<6} {cfg['title']}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Extract UBA MC 4.0 value factors to CSV",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Output: uba1/output/NN_uba4_<key>.csv\n"
               "Source: UBA Handbook on Environmental Value Factors, MC 4.0, December 2025",
    )
    parser.add_argument(
        "--only", nargs="+", metavar="KEY",
        help="Extract only these table groups (space-separated keys)",
    )
    parser.add_argument(
        "--list", action="store_true",
        help="List all available table groups and exit",
    )
    args = parser.parse_args()

    if args.list:
        _list_groups()
        return

    keys = list(config.TABLE_GROUPS.keys())
    if args.only:
        unknown = [k for k in args.only if k not in config.TABLE_GROUPS]
        if unknown:
            logger.error("Unknown table group(s): %s", unknown)
            _list_groups()
            sys.exit(1)
        keys = args.only

    pub = config.PUBLICATION
    print(f"\n{pub['title']}")
    print(f"{pub['subtitle']}")
    print(f"Authors: {pub['authors']}")
    print(f"Publisher: {pub['publisher']}, {pub['month']} {pub['year']}")
    print(f"ISSN {pub['issn']}  |  Price base: {pub['price_base']}")
    print(f"\nExtracting {len(keys)} table group(s) → {config.OUTPUT_DIR}/\n")

    t0 = time.time()
    results = {}
    errors = {}

    for key in keys:
        try:
            t1 = time.time()
            out = pipeline.run_table(key)
            elapsed = time.time() - t1
            results[key] = out
            print(f"  [OK]   {key:<25}  {elapsed:.2f}s  →  {out.name}")
        except Exception as exc:
            errors[key] = exc
            print(f"  [FAIL] {key:<25}  {exc}")

    wall = time.time() - t0
    n_ok   = len(results)
    n_fail = len(errors)

    print(f"\n{'─'*60}")
    print(f"Done: {n_ok}/{len(keys)} succeeded, {n_fail} failed  ({wall:.1f}s)\n")

    if results:
        print("Output files:")
        for key, path in results.items():
            rows = sum(1 for _ in open(path, encoding="utf-8")) - 1  # minus header
            print(f"  {path.name:<45} {rows:>4} rows")
    if errors:
        print("\nFailed:")
        for key, exc in errors.items():
            print(f"  {key}: {exc}")

    # Write timestamped execution log
    log_path = config.THIS_DIR / f"execution_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(log_path, "w", encoding="utf-8") as lf:
        lf.write(f"UBA MC 4.0 Execution Log — {datetime.now().isoformat()}\n")
        lf.write(f"{'─'*60}\n")
        for key in keys:
            if key in results:
                lf.write(f"[OK]   {key}\n")
            else:
                lf.write(f"[FAIL] {key}  —  {errors[key]}\n")
        lf.write(f"{'─'*60}\n")
        lf.write(f"Total: {n_ok}/{len(keys)} succeeded  wall-clock {wall:.1f}s\n")
    print(f"\nExecution log: {log_path.name}")

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
