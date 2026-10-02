# Raw load: CDnow transaction file

This is the result of phase 2, **Build a lossless raw load**. It preserves every physical source line and splits records with exactly four whitespace-separated fields. It does not validate customer IDs, dates, CD counts, or transaction amounts. A `four_fields` status means only that the line has four fields.

## Run locally on Windows

From the repository root:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dbt.txt
.\.venv\Scripts\python.exe scripts\load_raw.py
```

In an editor, choose `C:\Users\tiana\Software\cd-now\.venv\Scripts\python.exe` as this project's interpreter. The single requirements file installs DuckDB for the loader and dbt for typed staging. We tried a dlt load first; its pipeline initialization was unusually slow in this environment, so this fixed local file uses DuckDB's bulk JSON import. The source parser and its output remain independent of that loading choice.

The script checks the source against [`source_manifest.json`](source_manifest.json), creates a local `data/cdnow.duckdb`, and writes [`reports/raw_load.json`](../reports/raw_load.json). The database and temporary `data/raw_lines.ndjson` transfer file are derived and ignored by Git. Rerunning replaces the raw table instead of appending to it.

## Queryable outputs

| Relation | Contents |
| --- | --- |
| `cdnow_raw.source_lines` | Every physical input line, its one-based line number, original text including its line terminator, field count, parse status and reason, and four raw field strings where present. |
| `cdnow_raw.four_field_lines` | View of rows with exactly four fields; their field values are not yet validated. |
| `cdnow_raw.malformed_lines` | View of blank, short, and extra-field rows; retains the original text, line number, and format issue. |

Example DuckDB query:

```sql
SELECT source_line_number, original_line, parse_reason
FROM cdnow_raw.malformed_lines
ORDER BY source_line_number;
```

## Reconciliation from the supplied file

The [raw-load report](../reports/raw_load.json) records 69,659 input lines, 69,659 raw rows, 69,659 distinct source-line numbers, 69,659 four-field rows, and **0 structurally malformed lines**. We ran the loader twice and got the same counts. A separate comparison confirmed that all 69,659 stored original lines match the source file exactly. These are physical-format results only, not evidence that every transaction value is valid or that the readme's customer count is correct. Later checks may find invalid values among the four-field rows.
