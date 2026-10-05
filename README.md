# CDnow cohort assessment

This repository contains my investment recommendation and reproducible analysis for a proposed revenue-share advance to CDnow. The decision is framed as of **July 15, 1998**. The supplied transaction file covers 23,570 customers whose first CDnow purchase was in Q1 1997, through June 30, 1998. It does not contain acquisition spend, customer-serving costs, refunds, or confirmed repayment-eligible revenue.

## Read the assessment

Start with the [investment committee memo](final_deliverables/investment_committee_memo.md) or its [PDF](final_deliverables/investment_committee_memo.pdf). It gives the recommendation, observed revenue quality, future-cohort scenarios, repayment model, downside cases, and questions for CDnow. The memo includes a clearly separated afterword about information published after the historical decision date; that information does not enter the July 15 recommendation. The analysis does not account for large-scale changes in how media is distributed, shared, or consumed.

Supporting material is organized by purpose:

| Purpose | Main files |
| --- | --- |
| Observed Q1 1997 cohort | [Findings](reports/cohort_findings.md), [tables](reports/cohort_tables.md), [measurement definitions](docs/cohort_measurement_contract.md) |
| Forecast and sensitivities | [Extension comparison](reports/forecast_extensions.md), [early-90-day diagnostic](reports/early90_diagnostic.md), [downside cases](reports/downside_sensitivity.md), [Q4 purchaser-count scenarios](reports/future_cohort_size_scenarios.md) |
| Financing and alternative use of capital | [Repayment scenarios](reports/financing_scenarios.md), [opportunity-cost comparison](reports/opportunity_cost.md) |
| Data and external evidence | [Data contract](docs/data_contract.md), [quality checks](docs/validity_checks.md), [exception decisions](docs/exception_review.md), [company disclosures](docs/company_financial_evidence_1998.md), [market context](docs/historical_market_context.md), [source audit](docs/historical_source_audit.md) |
| Methods and verification | [Forecast definitions](docs/forecast_contract.md), [methodology literature](docs/methodology_literature.md), [numerical verification](docs/phase2_verification.md) |

The `reports/*.json` files record inputs, definitions, and calculations. The scripts that generate them are in `scripts/`; focused checks are in `tests/` and `dbt/tests/`. The [source manifest](docs/source_manifest.json) identifies the unchanged transaction file by size, line count, and SHA-256.

## Rebuild the analysis

Use Python 3.12 or newer and run these commands from the repository root in PowerShell. The dbt profile and scripts use the local `data/cdnow.duckdb` database; `data/` and `.venv/` are ignored.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dbt.txt
.\.venv\Scripts\python.exe scripts\source_manifest.py --check
.\.venv\Scripts\python.exe scripts\load_raw.py
.\.venv\Scripts\dbt.exe run --project-dir dbt --profiles-dir dbt
.\.venv\Scripts\dbt.exe test --project-dir dbt --profiles-dir dbt
.\.venv\Scripts\python.exe scripts\check_quality.py
.\.venv\Scripts\python.exe scripts\exception_impact.py
.\.venv\Scripts\python.exe scripts\verify_phase1.py
.\.venv\Scripts\python.exe scripts\cohort_analysis.py
.\.venv\Scripts\python.exe scripts\render_cohort_tables.py
.\.venv\Scripts\python.exe scripts\cd_price_comparison.py
.\.venv\Scripts\python.exe scripts\forecast_extensions.py
.\.venv\Scripts\python.exe scripts\lookback_sensitivity.py
.\.venv\Scripts\python.exe scripts\early90_diagnostic.py
.\.venv\Scripts\python.exe scripts\downside_sensitivity.py
.\.venv\Scripts\python.exe scripts\financing_scenarios.py
.\.venv\Scripts\python.exe scripts\future_cohort_size_scenarios.py
.\.venv\Scripts\python.exe scripts\trend_benchmark.py
.\.venv\Scripts\python.exe scripts\opportunity_cost.py
.\.venv\Scripts\python.exe scripts\render_memo_chart.py
```

Run the raw loader before dbt because the staging models read its tables. Each report distinguishes observed transaction dollars from forecasts and, where applicable, assumed eligible and collected revenue. Source-line queries and row-treatment sensitivities are in [data_quality.json](reports/data_quality.json) and [exception_impact.json](reports/exception_impact.json).

For development checks, install `requirements-dev.txt` and run `python -m pytest -q`, or run the configured local hooks after building the database:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\pre-commit.exe run --all-files
```

The source file and 1998 filing copies are in `CDNOW_data/`. The [late-July 10-Q note](docs/post_cutoff_financing_note.md) supports only the memo's separated afterword. The tracked [analysis context](notes/analysis.md) records the assessment's evidence limits and completed work but was used mostly for internal tracking and note taking.
