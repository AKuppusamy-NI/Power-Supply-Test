#!/usr/bin/env python3
"""Parse and "execute" a ``.seq`` text sequence (simulation stub).

This is a demo runner.  It parses the plain-text sequence into key/value
pairs, prints the global settings, then walks each step in order and prints
what it *would* do.  No real instruments are touched.

Usage::

    python scripts/run_sequence.py sequences/conducted_test.seq
"""

from __future__ import annotations

import argparse
import sys
from typing import Dict, List, Optional

from seq_parser import parse_sequence


def _ordered_steps(settings: Dict[str, str]) -> List[str]:
    """Return step prefixes (e.g. ``step1``, ``cal2``) in execution order."""
    prefixes = []
    seen = set()
    for key in settings:
        head = key.split(".", 1)[0]
        if head in seen:
            continue
        # A step head looks like <letters><digits>, e.g. step1 or cal3.
        digits = "".join(ch for ch in head if ch.isdigit())
        letters = "".join(ch for ch in head if not ch.isdigit())
        if digits and letters:
            seen.add(head)
            prefixes.append((letters, int(digits), head))
    prefixes.sort(key=lambda item: (item[0], item[1]))
    return [head for _, _, head in prefixes]


def run_sequence(path: str) -> int:
    settings = parse_sequence(path)

    name = settings.get("sequence_name", path)
    version = settings.get("sequence_version", "?")
    print(f"=== Running sequence: {name} (v{version}) ===\n")

    steps = _ordered_steps(settings)
    step_keys = set()

    print("Global settings:")
    for key, value in settings.items():
        head = key.split(".", 1)[0]
        if head in steps:
            step_keys.add(key)
            continue
        print(f"  {key} = {value}")

    print("\nExecuting steps:")
    for step in steps:
        prefix = step + "."
        action = settings.get(prefix + "action", "(no action)")
        step_name = settings.get(prefix + "name", step)
        print(f"  [{step}] {step_name}: action={action}")
        for key, value in settings.items():
            if key.startswith(prefix) and not key.endswith(("name", "action")):
                field = key[len(prefix):]
                print(f"        {field} = {value}")

    print("\nDone (stub execution; no hardware accessed).")
    return 0


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sequence", help="Path to a .seq text sequence file")
    args = parser.parse_args(argv)
    return run_sequence(args.sequence)


if __name__ == "__main__":
    sys.exit(main())
