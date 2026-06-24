"""Shared helpers for parsing the plain-text ``.seq`` sequence format.

The ``.seq`` files in ``sequences/`` are intentionally *not* the proprietary
TestStand binary format.  They are plain UTF-8 text with one ``key = value``
setting per line so that ordinary line-by-line diff tools can read them.
Lines that are blank or start with ``#`` are ignored.
"""

from __future__ import annotations

from typing import Dict


def parse_sequence(path: str) -> Dict[str, str]:
    """Parse a ``.seq`` text file into an ordered dict of key/value pairs.

    Parameters
    ----------
    path:
        Path to the ``.seq`` file.

    Returns
    -------
    dict
        Mapping of setting name to its (string) value.  Comment and blank
        lines are skipped.
    """
    settings: Dict[str, str] = {}
    with open(path, "r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                # Not a key = value line; skip it rather than crash.
                continue
            key, value = line.split("=", 1)
            settings[key.strip()] = value.strip()
    return settings
