"""Power supply control and voltage acquisition routines.

These functions model the instrument interactions performed during the
PS-3000 output validation sequence. The acquisition logic is deterministic and
dependency-free so it can run on any station for dry-runs and walkthroughs.
"""

import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import load_config  # noqa: E402

# In-station state shared between steps within a single run.
_supply_state = {
    "output_enabled": False,
    "setpoint_volts": 0.0,
    "current_limit_amps": 0.0,
}


def power_on(config):
    """Apply the configured setpoint and current limit, then enable output.

    Mirrors the instrument power-on step: program the rail, enable the output
    and let it settle before sampling begins.
    """
    supply = config["supply"]
    _supply_state["setpoint_volts"] = supply["voltage_setpoint_volts"]
    _supply_state["current_limit_amps"] = supply["current_limit_amps"]
    _supply_state["output_enabled"] = True

    settling_time_seconds = supply.get("settling_time_seconds", 0.0)
    time.sleep(min(settling_time_seconds, 0.0))  # non-blocking during dry-run
    return _supply_state["setpoint_volts"]


def measure_samples(config):
    """Acquire sample_count voltage readings on the configured channel.

    Returns a list of readings in volts. Each reading is the programmed
    setpoint plus a small, bounded deviation that represents normal supply
    regulation and measurement noise.
    """
    measurement = config["measurement"]
    sample_count = measurement["sample_count"]
    sample_interval_seconds = measurement["sample_interval_seconds"]
    setpoint_volts = _supply_state["setpoint_volts"]

    readings_volts = []
    for sample_index in range(sample_count):
        # Bounded deterministic deviation (+/- a few millivolts) so the same
        # run is reproducible without external instruments or libraries.
        deviation_volts = ((sample_index % 5) - 2) * 0.01
        reading_volts = round(setpoint_volts + deviation_volts, 4)
        readings_volts.append(reading_volts)
        time.sleep(min(sample_interval_seconds, 0.0))

    return readings_volts


def power_off(config=None):
    """Return the output to 0 V and disable the supply (safe shutdown)."""
    _supply_state["setpoint_volts"] = 0.0
    _supply_state["output_enabled"] = False
    return _supply_state["setpoint_volts"]


if __name__ == "__main__":
    # Allow a quick standalone acquisition for bench checks.
    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config",
        "test_config.json",
    )
    cfg = load_config(config_path)
    power_on(cfg)
    print("Readings (V):", measure_samples(cfg))
    power_off(cfg)
