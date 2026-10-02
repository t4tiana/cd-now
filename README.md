# CDnow assessment

## Local Python, DuckDB, and dbt setup

Use Python 3.12 or newer. Run these commands from the repository root in PowerShell;
the dbt profile resolves its database path from that directory. Create a
project-local environment **once** and install the analysis tools:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dbt.txt
```

The `.venv` directory is ignored by Git. Keep it between sessions; there is no
need to recreate or activate it each time. Call its executables directly:

```powershell
.\.venv\Scripts\python.exe scripts\source_manifest.py --check
.\.venv\Scripts\python.exe scripts\load_raw.py
.\.venv\Scripts\dbt.exe debug --project-dir dbt --profiles-dir dbt
.\.venv\Scripts\dbt.exe run --project-dir dbt --profiles-dir dbt
.\.venv\Scripts\dbt.exe test --project-dir dbt --profiles-dir dbt
.\.venv\Scripts\python.exe scripts\check_quality.py
.\.venv\Scripts\python.exe scripts\exception_impact.py
.\.venv\Scripts\python.exe scripts\verify_phase1.py
```

For an interactive PowerShell session, run
`.\.venv\Scripts\Activate.ps1` once per terminal, then use `python` and `dbt`
without their full paths. The environment itself persists after the terminal
closes. Run `pip install -r requirements-dbt.txt` again only when dependencies
change or when setting up a different machine.

Python scripts can `import duckdb` and use the local database at
`data/cdnow.duckdb`. The dbt project in `dbt/` points at that same database and
uses the `cdnow_analysis` schema for typed staging models. Run the raw loader before
building models from its tables. Do not hold the database open in another
process while dbt writes to it.

The [staging notes](docs/staging.md) define the typed fields, conversion rules,
and queryable exception output. The [validity-check report](docs/validity_checks.md)
summarizes step 4, with counts and source-line queries in
[`reports/data_quality.json`](reports/data_quality.json). The
[exception review](docs/exception_review.md) records row dispositions and the
effect of alternative treatments. For a short recap, see the
[phase 1 brief](notes/phase1_brief.md).

To run development checks, install the pinned test and formatting tools once:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\pre-commit.exe run --all-files
```

The local pre-commit hooks run Ruff, Pyright, sqlfmt, pytest, dbt tests, and
the phase 1 source-to-report reconciliation. Run the raw load and dbt build
before those hooks on a new checkout. The hooks use the project-local Windows
venv and do not download hook environments.

`requirements-dbt.txt` pins DuckDB for raw ingestion and the dbt DuckDB adapter
for transformations; `requirements-dev.txt` adds test and check tools. The transaction file supports observed behavior of one cohort; see
`notes/analysis.md` for the limits on investment conclusions.
