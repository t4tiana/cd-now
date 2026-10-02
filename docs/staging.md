# Typed staging: CDnow transactions

Run from the repository root after loading raw lines:

```powershell
.\.venv\Scripts\dbt.exe run --project-dir dbt --profiles-dir dbt
```

`cdnow_analysis.stg_cdnow_transactions` is a table with **one row per physical source line**. It never filters a line or replaces an invalid value with zero. `cdnow_analysis.stg_cdnow_rejections` is a view of its rows with a non-null `conversion_issue`; it carries the original line, raw strings, line number, and each issue column. The raw table remains `cdnow_raw.source_lines`.

| Staged column | Source | DuckDB type | Rule |
| --- | --- | --- | --- |
| `source_record_id` | File name and `source_line_number` | `VARCHAR` | `CDNOW_master.txt:` followed by the one-based line number; identifies the input record, not an order. |
| `source_line_number` | Raw loader | `BIGINT` | Copied unchanged. |
| `original_line` | Raw loader | `VARCHAR` | Copied unchanged, including line terminator. |
| `field_count` | Raw loader | `INTEGER` | Copied unchanged. |
| `parse_status`, `parse_reason` | Raw loader | `VARCHAR` | Copied unchanged; describe the four-field format check. |
| `customer_id_raw`, `transaction_date_raw`, `cd_count_raw`, `dollar_value_raw` | Corresponding source fields | `VARCHAR` | Copied unchanged where four fields exist. |
| `customer_id` | `customer_id_raw` | `VARCHAR` | Copied as text to preserve leading zeroes. Expected ID form is checked in step 4. |
| `transaction_date` | `transaction_date_raw` | `DATE` | Parse only an eight-digit `YYYYMMDD` string that represents a real calendar date; otherwise `NULL`. |
| `cd_count` | `cd_count_raw` | `INTEGER` | Accept an optional sign and digits, within the integer range; otherwise `NULL`. Positivity is checked in step 4. |
| `transaction_dollars` | `dollar_value_raw` | `DECIMAL(18,2)` | Accept an optional sign, digits, and up to two decimal digits; otherwise `NULL`. This avoids rounding sub-cent input into cents. Amount sign and zero are checked in step 4. |
| `structure_issue`, `customer_id_issue`, `transaction_date_issue`, `cd_count_issue`, `transaction_dollars_issue` | Format and conversion checks | `VARCHAR` | Each has a reason when that check fails, otherwise `NULL`. Structural failures do not create redundant field issues. |
| `conversion_issue` | Issue columns | `VARCHAR` | All reasons joined with semicolons; `NULL` when there is no structural or conversion failure. |

After `dbt run` on the supplied file, the staging table has **69,659 rows**, **69,659 distinct source record IDs**, **69,659 distinct source line numbers**, and **0 conversion exceptions**. The raw table also has **69,659 rows**. These are conversion results only. They do not establish that IDs have the expected form, dates are within the stated observation window, CD counts and dollars are positive, or that the cohort definition and readme customer count hold. Those checks are reported separately in [step 4](validity_checks.md).

To reproduce the row and exception counts:

```sql
select count(*) as staged_rows,
       count(distinct source_record_id) as distinct_record_ids,
       count(distinct source_line_number) as distinct_source_lines,
       count(*) filter (where conversion_issue is not null) as exception_rows
from cdnow_analysis.stg_cdnow_transactions;
```
