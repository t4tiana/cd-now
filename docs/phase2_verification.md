# Phase 2 numerical verification

The input is the tracked `CDNOW_data/CDNOW_master.txt` file, identified by SHA-256
`61fd6f7bf3497187a7ec0d9ff6a99b7568f1fe911a9f3665e02efecd6b34ed07`.
This verification concerns the observed Q1 1997 cohort through June 30, 1998.
It does not validate external market claims, forecast future revenue, or establish
which reported dollars would be eligible for an investor repayment.

## Focused checks

`tests/test_cohort_analysis.py` checks that the earliest recorded date determines
cohort entry even when source rows are out of order and the first date includes
a zero-dollar row. A small fixture tests days 29 and 30, days 90 and 119, and
one transaction on the cutoff date in a partially observable window. The latter
stays in the full-file totals but is excluded from the like-aged rate and dollar
numerator. An integration check rebuilds the report against the staged source
and phase 1 baseline, and a negative check confirms that a changed phase 1 row
count stops report generation.

## Rebuild from the tracked source

Run these commands in order from the repository root after installing the
dependencies in `README.md`:

```powershell
.\.venv\Scripts\python.exe scripts\source_manifest.py --check
.\.venv\Scripts\python.exe scripts\load_raw.py
.\.venv\Scripts\dbt.exe run --project-dir dbt --profiles-dir dbt
.\.venv\Scripts\dbt.exe test --project-dir dbt --profiles-dir dbt
.\.venv\Scripts\python.exe scripts\verify_phase1.py
.\.venv\Scripts\python.exe scripts\cohort_analysis.py
.\.venv\Scripts\python.exe scripts\render_cohort_tables.py
.\.venv\Scripts\python.exe scripts\cd_price_comparison.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\pyright.exe
.\.venv\Scripts\ruff.exe check scripts tests
.\.venv\Scripts\ruff.exe format --check scripts tests
```

Verification run: the manifest matched; the raw load contained 69,659 lines
and no malformed rows; both dbt models and all 7 dbt tests passed. Phase 1
verification matched all 69,659 exact source lines, 23,570 customers,
$2,500,315.63 in reported transaction dollars, zero conversion exceptions,
and all 19 source-line queries. All 7 Python tests passed; Pyright reported
zero errors or warnings, and Ruff checks passed.

The cohort report reconciled 69,659 staged rows, 23,570 customers, and
$2,500,315.63 to phase 1. The complete age windows contain 68,776 rows and
$2,468,094.71; the partially observed windows contain 883 rows and
$32,220.92. Together they equal the full observed file. A second run of the
three phase 2 output scripts produced byte-identical outputs (SHA-256):

| Output | SHA-256 |
| --- | --- |
| `reports/cohort_analysis.json` | `a63c753a83e6022b0b2cc5bad3e95a53bfd32e2146fe8c3c2c21010fd2b20d1d` |
| `reports/cohort_tables.md` | `6a6e1d7204c1e8995b8ebf4e5089e7a7587866e805529f9f7e7e193be67c4a87` |
| `reports/cd_price_comparison.json` | `c3f02eb87eb98f073c714406848a35f69f03fb3aad90e6f340b797e5e4d00b82` |

These checks establish reproducible numerical summaries of the supplied file.
They do not settle the open questions about customer identity, refunds,
acquisition cost, contribution, or eligible repayment revenue.
