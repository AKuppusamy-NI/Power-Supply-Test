"""Shared helpers for the power supply validation workflow.

Self-contained: only the Python standard library is used so the scripts run
on any test-station Python install without setup.
"""

import json
import os
from datetime import datetime


def load_config(config_path):
    """Load the JSON test configuration and return it as a dict.

    The same configuration object is shared by every step in the sequence so
    that the voltage setpoint, tolerance and sample settings stay consistent.
    """
    with open(config_path, "r", encoding="utf-8") as config_file:
        config = json.load(config_file)
    return config


def timestamp():
    """Return an ISO-8601 timestamp string for log records."""
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def mean(values):
    """Return the arithmetic mean of a list of readings (volts)."""
    if not values:
        return 0.0
    return sum(values) / len(values)


def peak_to_peak(values):
    """Return the peak-to-peak spread of the readings (volts)."""
    if not values:
        return 0.0
    return max(values) - min(values)


def ensure_results_dir(results_dir):
    """Create the results directory if it does not already exist."""
    os.makedirs(results_dir, exist_ok=True)
    return results_dir
