# Power-Supply-Test

Internal validation project for the **PS-3000 bench power supply**. It defines a
TestStand-driven workflow that programs the supply, acquires output voltage,
checks the result against engineering limits, and logs a traceable record for
every run.

## Overview

The goal of this repository is to give the validation team a single, consistent
definition of the DC output test: one sequence, one configuration file, and a
small set of self-contained Python action scripts. All parameters (voltage
setpoint, tolerance, sample count, ripple limit) live in
`config/test_config.json` so the sequence and scripts never drift out of sync.

The scripts use only the Python standard library, so any test station can run
them without additional setup.

## Repository structure

```
.
├── config/
│   └── test_config.json        # Setpoint, tolerance, sample and limit settings
├── sequences/
│   └── power_supply_test.seq   # TestStand workflow (step order and run modes)
├── src/
│   ├── measure_voltage.py      # Supply control and voltage acquisition
│   └── validate_results.py     # Pass/fail evaluation, ripple check, logging
├── utils/
│   └── helpers.py              # Config loading and shared math helpers
├── results/
│   └── power_supply_test.log   # Timestamped run history
└── docs/
    └── architecture.md         # How sequence, scripts and config interact
```

## Workflow description

The sequence `sequences/power_supply_test.seq` runs these steps in order:

1. **Load Configuration** — read `config/test_config.json`.
2. **Power On and Warm Up** — apply the setpoint and current limit, then settle.
3. **Measure Output Voltage** — acquire `sample_count` readings on the channel.
4. **Validate Results** — compare the mean reading against setpoint ± tolerance
   and confirm every sample is inside the min/max limit window.
5. **Check Output Ripple** — evaluate peak-to-peak ripple against the limit.
6. **Log Results** — append a timestamped record to the results log.
7. **Power Down** — cleanup step that returns the output to 0 V.

The cleanup step always runs, so the device under test is left in a safe state
even when an earlier step fails.

## Configuration

Edit `config/test_config.json` to change the test point. Key fields:

- `supply.voltage_setpoint_volts` — programmed output voltage.
- `supply.current_limit_amps` — output current limit.
- `measurement.sample_count` / `measurement.sample_interval_seconds` — acquisition.
- `measurement.tolerance_volts` — allowed deviation from the setpoint.
- `limits.voltage_min_volts` / `limits.voltage_max_volts` — absolute pass window.
- `limits.ripple_max_millivolts` — peak-to-peak ripple limit.

See `docs/architecture.md` for the full data flow between the sequence, scripts
and configuration.
