"""Pass/fail evaluation and result logging for the validation sequence.

Compares acquired voltage samples against the setpoint, tolerance and limit
window defined in config/test_config.json, evaluates output ripple, and writes
a traceable, timestamped record to the results log.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.helpers import (  # noqa: E402
    ensure_results_dir,
    load_config,
    mean,
    peak_to_peak,
    timestamp,
)


def validate(config, readings_volts):
    """Evaluate readings against the setpoint, tolerance and limit window.

    Returns a result dict describing the mean reading and whether the rail is
    within tolerance of the setpoint and inside the absolute min/max limits.
    """
    supply = config["supply"]
    measurement = config["measurement"]
    limits = config["limits"]

    setpoint_volts = supply["voltage_setpoint_volts"]
    tolerance_volts = measurement["tolerance_volts"]
    voltage_min_volts = limits["voltage_min_volts"]
    voltage_max_volts = limits["voltage_max_volts"]

    mean_volts = round(mean(readings_volts), 4)
    error_volts = round(mean_volts - setpoint_volts, 4)

    within_tolerance = abs(error_volts) <= tolerance_volts
    within_limits = all(
        voltage_min_volts <= reading <= voltage_max_volts
        for reading in readings_volts
    )
    passed = within_tolerance and within_limits

    return {
        "setpoint_volts": setpoint_volts,
        "mean_volts": mean_volts,
        "error_volts": error_volts,
        "tolerance_volts": tolerance_volts,
        "within_tolerance": within_tolerance,
        "within_limits": within_limits,
        "passed": passed,
    }


def check_ripple(config, readings_volts):
    """Compare peak-to-peak ripple against the configured ripple limit.

    Ripple is reported in millivolts to match how the limit is specified.
    """
    ripple_max_millivolts = config["limits"]["ripple_max_millivolts"]
    ripple_millivolts = round(peak_to_peak(readings_volts) * 1000.0, 2)
    passed = ripple_millivolts <= ripple_max_millivolts

    return {
        "ripple_millivolts": ripple_millivolts,
        "ripple_max_millivolts": ripple_max_millivolts,
        "passed": passed,
    }


def write_log(config, validation_result, ripple_result):
    """Append a timestamped, human-readable record of the run to the log.

    The log line mirrors typical bench output so results are easy to audit.
    """
    log_config = config["logging"]
    results_dir = ensure_results_dir(log_config["results_dir"])
    log_path = os.path.join(results_dir, log_config["log_file"])

    overall = "PASS" if (validation_result["passed"] and ripple_result["passed"]) else "FAIL"
    record = (
        f"[{timestamp()}] result={overall} "
        f"setpoint={validation_result['setpoint_volts']:.3f}V "
        f"mean={validation_result['mean_volts']:.3f}V "
        f"error={validation_result['error_volts']:+.3f}V "
        f"tol=+/-{validation_result['tolerance_volts']:.3f}V "
        f"ripple={ripple_result['ripple_millivolts']:.1f}mV "
        f"(limit {ripple_result['ripple_max_millivolts']:.1f}mV)\n"
    )

    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(record)
    return log_path


if __name__ == "__main__":
    # Standalone end-to-end check using the bundled configuration.
    from measure_voltage import measure_samples, power_off, power_on

    config_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "config",
        "test_config.json",
    )
    cfg = load_config(config_path)
    power_on(cfg)
    samples = measure_samples(cfg)
    power_off(cfg)

    validation = validate(cfg, samples)
    ripple = check_ripple(cfg, samples)
    path = write_log(cfg, validation, ripple)
    print(f"Validation: {'PASS' if validation['passed'] else 'FAIL'}")
    print(f"Ripple:     {'PASS' if ripple['passed'] else 'FAIL'}")
    print(f"Logged to:  {path}")
