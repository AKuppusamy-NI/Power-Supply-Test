# Architecture

This document describes how the test sequence, Python action scripts and the
shared configuration interact during a power supply validation run.

## Components

| Layer          | Location                          | Responsibility                                              |
|----------------|-----------------------------------|-------------------------------------------------------------|
| Sequence       | `sequences/power_supply_test.seq` | Defines step order, run modes and failure handling.         |
| Configuration  | `config/test_config.json`         | Single source of truth for setpoint, tolerance and limits.  |
| Action scripts | `src/measure_voltage.py`, `src/validate_results.py` | Instrument control, acquisition, evaluation, logging. |
| Utilities      | `utils/helpers.py`                | Config loading and shared math (mean, peak-to-peak).        |
| Results        | `results/power_supply_test.log`   | Timestamped, auditable record of each run.                  |

## Data flow

```
config/test_config.json
          |
          v
  utils/helpers.load_config()
          |
          v
  sequences/power_supply_test.seq  (step orchestration)
          |
   +------+-----------------------------+
   |                                     |
   v                                     v
src/measure_voltage.py            src/validate_results.py
  power_on()                        validate()
  measure_samples()  -- readings --> check_ripple()
  power_off()                        write_log() --> results/power_supply_test.log
```

## How the pieces stay consistent

- Every step reads parameters from `config/test_config.json`, so the voltage
  setpoint, tolerance and sample count are defined once and reused everywhere.
- Parameter names in the sequence (`voltage_setpoint_volts`, `tolerance_volts`,
  `sample_count`, `ripple_max_millivolts`) match the keys in the configuration
  file and the variable names used in the Python scripts.
- `measure_voltage.py` owns instrument state; `validate_results.py` consumes the
  readings it produces and never talks to the supply directly.

## Run lifecycle

1. **Load Configuration** — read and validate `test_config.json`.
2. **Power On and Warm Up** — program the rail and let it settle.
3. **Measure Output Voltage** — acquire `sample_count` readings.
4. **Validate Results** — compare against setpoint, tolerance and limits.
5. **Check Output Ripple** — evaluate peak-to-peak ripple in millivolts.
6. **Log Results** — append a timestamped record to the results log.
7. **Power Down** — cleanup step that always returns the output to 0 V.

The shutdown step runs as a cleanup action so the DUT is left in a safe state
even if an earlier step fails.
