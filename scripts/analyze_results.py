#!/usr/bin/env python3
"""Load measurement results and print a simple summary.

Reads a CSV of results (columns: ``step, value, limit_low, limit_high,
pass``) using only the standard library, computes basic statistics, and
prints a human-readable summary including the overall pass rate.

Usage::

    python scripts/analyze_results.py data/sample_results.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from typing import List, Optional


def _to_float(value: str) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def analyze_results(path: str) -> int:
    rows = []
    with open(path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(row)

    if not rows:
        print(f"No results found in {path}")
        return 0

    values: List[float] = [
        v for v in (_to_float(r.get("value", "")) for r in rows) if v is not None
    ]

    def _is_pass(raw: str) -> bool:
        return str(raw).strip().lower() in ("1", "true", "pass", "yes")

    passes = sum(1 for r in rows if _is_pass(r.get("pass", "")))
    total = len(rows)

    print(f"Results file: {path}")
    print(f"Total measurements: {total}")
    print(f"Passed: {passes}")
    print(f"Failed: {total - passes}")
    print(f"Pass rate: {100.0 * passes / total:.1f}%")

    if values:
        mean = sum(values) / len(values)
        print("\nValue statistics:")
        print(f"  count = {len(values)}")
        print(f"  min   = {min(values):.4f}")
        print(f"  max   = {max(values):.4f}")
        print(f"  mean  = {mean:.4f}")

    print("\nPer-step:")
    for r in rows:
        status = "PASS" if _is_pass(r.get("pass", "")) else "FAIL"
        print(
            f"  {r.get('step', '?'):<22} value={r.get('value', '?'):>8}  "
            f"limits=[{r.get('limit_low', '?')}, {r.get('limit_high', '?')}]  "
            f"-> {status}"
        )

    return 0


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "results",
        nargs="?",
        default="data/sample_results.csv",
        help="Path to a results CSV file",
    )
    args = parser.parse_args(argv)
    return analyze_results(args.results)


if __name__ == "__main__":
    sys.exit(main())
