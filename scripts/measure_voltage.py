#!/usr/bin/env python3
"""Simulate a voltage measurement for a sequence file.

Reads a ``.seq`` text sequence, finds the voltage measurement steps and the
limits defined for them, simulates a measured voltage (deterministic, derived
from the configured nominal/set voltage), and prints PASS/FAIL for each step.

Usage::

    python scripts/measure_voltage.py sequences/conducted_test.seq
"""

from __future__ import annotations

import argparse
import random
import sys
from typing import Dict, Optional

from seq_parser import parse_sequence


def _to_float(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _step_indices(settings: Dict[str, str], prefix: str) -> list:
    """Return the sorted numeric indices present for a given step prefix."""
    indices = set()
    for key in settings:
        if key.startswith(prefix) and key[len(prefix):].split(".", 1)[0].isdigit():
            indices.add(int(key[len(prefix):].split(".", 1)[0]))
    return sorted(indices)


def simulate_measurement(nominal_v: float, seed: str) -> float:
    """Return a deterministic pseudo-random voltage near ``nominal_v``."""
    rng = random.Random(seed)
    # +/- 2% noise around the nominal value.
    return round(nominal_v * (1.0 + rng.uniform(-0.02, 0.02)), 4)


def measure_voltage(path: str) -> int:
    settings = parse_sequence(path)
    nominal = _to_float(settings.get("vcc_nominal_v")) or 12.0

    overall_ok = True
    found = False

    for prefix in ("step", "cal"):
        for idx in _step_indices(settings, prefix):
            base = f"{prefix}{idx}."
            action = settings.get(base + "action", "")
            name = settings.get(base + "name", f"{prefix}{idx}")

            low = _to_float(settings.get(base + "limit_low_v"))
            high = _to_float(settings.get(base + "limit_high_v"))
            if low is None:
                low = _to_float(settings.get(base + "threshold_low_v"))
            if high is None:
                high = _to_float(settings.get(base + "threshold_high_v"))

            if low is None and high is None:
                # Not a measurement step with voltage limits.
                continue
            if action and "voltage" not in action and "measure" not in action:
                continue

            found = True
            set_v = _to_float(settings.get(base + "set_voltage_v"))
            target = set_v if set_v is not None else nominal
            measured = simulate_measurement(target, f"{path}:{base}")

            ok = True
            if low is not None and measured < low:
                ok = False
            if high is not None and measured > high:
                ok = False
            overall_ok = overall_ok and ok

            print(
                f"{name:<22} measured={measured:>8.4f} V  "
                f"limits=[{low}, {high}]  -> {'PASS' if ok else 'FAIL'}"
            )

    if not found:
        print(f"No voltage measurement steps found in {path}")
        return 0

    print(f"\nOverall: {'PASS' if overall_ok else 'FAIL'}")
    return 0 if overall_ok else 1


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sequence", help="Path to a .seq text sequence file")
    args = parser.parse_args(argv)
    return measure_voltage(args.sequence)


if __name__ == "__main__":
    sys.exit(main())
