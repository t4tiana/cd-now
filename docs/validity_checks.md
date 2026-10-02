# Step 4: validity checks on the supplied CDnow file

This report describes the **Q1 1997 first-purchase cohort through June 30, 1998**. It checks the physical file and typed staging table; it does not estimate revenue persistence, acquisition economics, or repayment eligibility. The source is [`CDNOW_data/CDNOW_master.txt`](../CDNOW_data/CDNOW_master.txt), identified by SHA-256 `61fd6f7bf3497187a7ec0d9ff6a99b7568f1fe911a9f3665e02efecd6b34ed07` in the [manifest](source_manifest.json). The readme supplies the expected transaction and customer counts.

From the repository root, reproduce the results in this order:

```powershell
.\.venv\Scripts\python.exe scripts\source_manifest.py --check
.\.venv\Scripts\python.exe scripts\load_raw.py
.\.venv\Scripts\dbt.exe run --project-dir dbt --profiles-dir dbt
.\.venv\Scripts\python.exe scripts\check_quality.py
```

The script writes [`reports/data_quality.json`](../reports/data_quality.json). For each record-level finding, it includes a count, sample source-line numbers, and a SQL query returning **all** affected lines from `data/cdnow.duckdb`. The script itself is the reproducible definition of each check. No row is removed or changed by these checks.

| Check | Result | Interpretation |
| --- | --- | --- |
| 4.1 Physical structure | 69,659 four-field lines; 0 blank, short, or extra-field lines | Every input line has four whitespace-delimited fields. |
| 4.2 Customer IDs | 23,570 distinct IDs; 0 missing or outside the observed five-digit form | IDs are retained as strings, from `00001` through `23570`. Gaps are profiled separately, not treated as errors. |
| 4.3 Dates | 0 unparseable or outside January 1, 1997–June 30, 1998; earliest January 1, 1997; latest June 30, 1998 | The observed transaction dates match the stated file window. |
| 4.4 Cohort entry | 0 customers whose earliest recorded date falls outside Q1 1997; earliest first purchase January 1, latest March 25 | This checks **recorded** first purchase, not marketing acquisition date. |
| 4.5 CD counts | 0 zero, negative, fractional-string, or otherwise unparseable values; maximum 99 | Large positive counts are profiled in 4.10. |
| 4.6 Dollar values | **80 zero-dollar rows**; 0 negative, non-cent-precision, or otherwise unparseable values; maximum $1,286.01 | Zero-dollar purchases need a business explanation. They remain in staging. Source line 1549 is one example. |
| 4.7 Reconciliation | 69,659 raw and staged lines; 0 conversion failures; 23,570 distinct customers | Both counts equal the readme's claims. |
| 4.8 Load identity | 69,659 unique raw line numbers, staged line numbers, and staged record IDs; 0 raw/staged line-text mismatches | A loader and dbt rerun kept these counts. This checks load identity; it cannot determine whether similar-looking source rows were distinct orders. |
| 4.9 Repeated-looking rows | 215 groups have identical four field strings: 470 rows, or 255 beyond one per group. Separately, 1,774 customer/date groups have multiple rows: 3,842 rows, or 2,068 beyond one per group | The two categories overlap. Do not add their counts or automatically deduplicate. Source lines 1381–1382 are an exact-match example. |
| 4.10 Large values and gaps | 1,113 rows have at least 10 CDs; 464 have at least $200. Maximums are 99 CDs and $1,286.01, both on line 27633. No missing calendar days within the observation window and no missing five-digit IDs between `00001` and `23570` | The fixed thresholds are review flags, not exclusion rules. The 99th percentiles are 11 CDs and $173.12 per row. No date or ID gap proves complete customer histories. |

## Questions carried into exception review

- What creates a positive CD count with $0.00 transaction value: a promotion, adjustment, data convention, or error? Does it belong in reported revenue and in revenue eligible for repayment?
- Are identical four-field rows separate orders or duplicated records? The source has no order ID, so the pattern alone cannot decide.
- Are very large transactions genuine bulk purchases or recording errors? The largest row is source line 27633.
- How are refunds, cancellations, customer identities, and cash collection represented? The four-field file cannot answer these questions.

Step 5 will assign explicit dispositions and quantify any exclusion or correction before cohort behavior is analyzed. For now, **all 69,659 lines remain in staging**. The checks establish consistency with the readme and identify questions; they do not establish margin, customer acquisition cost, future-cohort behavior, or investor payback.
