# Power-Supply-Test

Demo repository for a [TestStand](https://www.ni.com/teststand) power-supply
test workflow, showing how engineers manage and update test sequences and
measurement scripts using **Nigel + MCP**.

## Why text-based `.seq` files?

Real TestStand sequence files are a proprietary **binary** format that does
not diff or merge cleanly in Git. For this demo, every `.seq` file is instead
plain **UTF-8 text** in a simple, line-based `key = value` format. This makes
the sequences:

- **Human-readable** – open any `.seq` in a text editor and read it.
- **Diff-friendly** – a line-by-line diff tool shows exactly what changed.
- **Automation-friendly** – Nigel/MCP and the scripts here can read and edit
  them without special TestStand tooling.

### Format rules

- One setting per line, written as `key = value`.
- Lines starting with `#` are comments / headers.
- Blank lines are ignored.
- Step settings are namespaced with a step prefix and a dot, e.g.
  `step1.action = measure_voltage` or `cal2.set_voltage_v = 5.0`.
- Each sequence begins with a `#` header block describing the test.

Example:

```
# Sequence: conducted_test
sequence_name = conducted_test
settle_time_s = 0.5

step2.name = measure_vout
step2.action = measure_voltage
step2.limit_low_v = 11.4
step2.limit_high_v = 12.6
```

## Folder layout

```
Power-Supply-Test/
├── README.md                  # this file
├── sequences/                 # text-format .seq test sequences
│   ├── conducted_test.seq     # power-on, voltage measurement, limits, delays, logging
│   ├── power_calibration.seq  # vcc, current limits, settle times, cal points
│   ├── thermal_test.seq       # temp min/max, dwell, ramp rate, thresholds
│   └── rf_acpr_test.seq       # frequency, power_level, timeout, measurement = ACPR
├── scripts/                   # Python helpers (stdlib only)
│   ├── seq_parser.py          # shared .seq text parser
│   ├── measure_voltage.py     # simulate a voltage measurement, print pass/fail
│   ├── run_sequence.py        # parse a .seq file and "execute" steps (stub)
│   └── analyze_results.py     # load results, compute stats, print a summary
├── data/
│   └── sample_results.csv     # sample measurement results
└── requirements.txt           # Python deps (none required; stdlib only)
```

## Usage

The scripts use only the Python standard library, so no installation is
needed. Run them from the repository root.

Run (simulate) a sequence:

```bash
python scripts/run_sequence.py sequences/conducted_test.seq
```

Simulate voltage measurements and check limits:

```bash
python scripts/measure_voltage.py sequences/conducted_test.seq
```

Analyze recorded results:

```bash
python scripts/analyze_results.py data/sample_results.csv
```

> Note: these scripts are a demo/simulation. No physical instruments are
> accessed; measured values are generated deterministically.
