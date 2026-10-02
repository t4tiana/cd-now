"""Run source-line-traceable validity checks on the raw and staged CDnow data."""

import json
from pathlib import Path
from typing import Any

import duckdb

ROOT = Path(__file__).resolve().parent.parent
DATABASE = ROOT / "data" / "cdnow.duckdb"
REPORT = ROOT / "reports" / "data_quality.json"
MANIFEST = ROOT / "docs" / "source_manifest.json"
RAW = "cdnow_raw.source_lines"
STAGED = "cdnow_analysis.stg_cdnow_transactions"
EXPECTED_TRANSACTIONS = 69659
EXPECTED_CUSTOMERS = 23570


def query_one(connection: duckdb.DuckDBPyConnection, sql: str) -> tuple[Any, ...]:
    """Fetch the one row expected from a scalar or aggregate query."""
    row = connection.execute(sql).fetchone()
    if row is None:
        raise ValueError(f"Query returned no row: {sql}")
    return row


def flagged(
    connection: duckdb.DuckDBPyConnection, relation: str, condition: str
) -> dict:
    """Count flagged records and give a query for every affected source line."""
    line_query = (
        f"SELECT source_line_number FROM {relation} WHERE {condition} "
        "ORDER BY source_line_number"
    )
    return {
        "count": query_one(
            connection, f"SELECT count(*) FROM {relation} WHERE {condition}"
        )[0],
        "sample_source_lines": [
            row[0] for row in connection.execute(line_query + " LIMIT 10").fetchall()
        ],
        "all_source_lines_query": line_query,
    }


def duplicate_profile(connection: duckdb.DuckDBPyConnection, fields: str) -> dict:
    """Profile groups with repeated field values without deleting any row."""
    groups = query_one(
        connection,
        f"SELECT count(*), coalesce(sum(n), 0), coalesce(sum(n - 1), 0) "
        f"FROM (SELECT count(*) AS n FROM {STAGED} GROUP BY {fields} "
        "HAVING count(*) > 1)",
    )
    line_query = (
        "SELECT source_line_number FROM ("
        f"SELECT source_line_number, count(*) OVER (PARTITION BY {fields}) AS n "
        f"FROM {STAGED}) WHERE n > 1 ORDER BY source_line_number"
    )
    return {
        "groups": groups[0],
        "rows_in_groups": groups[1],
        "rows_beyond_first_in_group": groups[2],
        "sample_source_lines": [
            row[0] for row in connection.execute(line_query + " LIMIT 10").fetchall()
        ],
        "all_source_lines_query": line_query,
    }


def run_checks(connection: duckdb.DuckDBPyConnection) -> dict:
    """Return step 4 checks with counts, thresholds, and traceability queries."""
    source_hash = json.loads(MANIFEST.read_text(encoding="utf-8"))["sha256"]
    raw_rows, raw_distinct_lines = query_one(
        connection, f"SELECT count(*), count(DISTINCT source_line_number) FROM {RAW}"
    )
    staged_rows, staged_distinct_lines, staged_distinct_ids, customers = query_one(
        connection,
        f"SELECT count(*), count(DISTINCT source_line_number), "
        f"count(DISTINCT source_record_id), count(DISTINCT customer_id) FROM {STAGED}",
    )
    first_dates = (
        f"SELECT customer_id, min(transaction_date) AS first_date FROM {STAGED} "
        "WHERE customer_id IS NOT NULL GROUP BY customer_id"
    )
    first_outside_query = (
        "WITH first_dates AS (" + first_dates + ") "
        f"SELECT s.source_line_number FROM {STAGED} s JOIN first_dates f "
        "ON s.customer_id = f.customer_id AND s.transaction_date = f.first_date "
        "WHERE f.first_date < DATE '1997-01-01' "
        "OR f.first_date > DATE '1997-03-31' "
        "ORDER BY s.source_line_number"
    )
    first_outside = query_one(
        connection,
        "SELECT count(*) FROM (SELECT customer_id FROM (" + first_dates + ") "
        "WHERE first_date < DATE '1997-01-01' "
        "OR first_date > DATE '1997-03-31')",
    )[0]
    earliest, latest = query_one(
        connection, f"SELECT min(transaction_date), max(transaction_date) FROM {STAGED}"
    )
    first_earliest, first_latest = query_one(
        connection, "SELECT min(first_date), max(first_date) FROM (" + first_dates + ")"
    )
    day_gap_query = (
        "SELECT calendar_day::DATE FROM generate_series(DATE '1997-01-01', "
        "DATE '1998-06-30', INTERVAL 1 DAY) AS days(calendar_day) "
        f"WHERE calendar_day::DATE NOT IN (SELECT transaction_date FROM {STAGED} "
        "WHERE transaction_date IS NOT NULL) ORDER BY calendar_day"
    )
    id_gap_query = (
        "SELECT lpad(cast(n AS VARCHAR), 5, '0') AS missing_customer_id "
        "FROM generate_series(1, 23570) AS numbers(n) "
        f"WHERE lpad(cast(n AS VARCHAR), 5, '0') NOT IN "
        f"(SELECT customer_id FROM {STAGED} WHERE customer_id IS NOT NULL) ORDER BY n"
    )
    dollar_noncent = "regexp_full_match(dollar_value_raw, '[+-]?[0-9]+\\.[0-9]{3,}')"
    cd_fractional = "regexp_full_match(cd_count_raw, '[+-]?[0-9]+\\.[0-9]+')"

    return {
        "source_sha256": source_hash,
        "database": "data/cdnow.duckdb",
        "step_4_1_structure": {
            "blank": flagged(connection, RAW, "parse_status = 'blank'"),
            "short": flagged(connection, RAW, "parse_status = 'short'"),
            "extra": flagged(connection, RAW, "parse_status = 'extra'"),
            "four_field_rows": query_one(
                connection,
                f"SELECT count(*) FROM {RAW} WHERE parse_status = 'four_fields'",
            )[0],
        },
        "step_4_2_customer_ids": {
            "expected_form": "exactly five ASCII digits, as in the supplied source",
            "missing": flagged(
                connection, STAGED, "customer_id IS NULL OR customer_id = ''"
            ),
            "wrong_form": flagged(
                connection,
                STAGED,
                "customer_id IS NOT NULL AND NOT regexp_full_match(customer_id, '[0-9]{5}')",
            ),
            "distinct_customers": customers,
        },
        "step_4_3_dates": {
            "unparseable": flagged(
                connection,
                STAGED,
                "parse_status = 'four_fields' AND transaction_date IS NULL",
            ),
            "out_of_observation_window": flagged(
                connection,
                STAGED,
                "transaction_date < DATE '1997-01-01' "
                "OR transaction_date > DATE '1998-06-30'",
            ),
            "earliest": str(earliest),
            "latest": str(latest),
            "distinct_transaction_dates": query_one(
                connection, f"SELECT count(DISTINCT transaction_date) FROM {STAGED}"
            )[0],
        },
        "step_4_4_cohort_entry": {
            "definition": "earliest recorded purchase per customer in 1997-01-01 through 1997-03-31",
            "customers_outside_q1_1997": first_outside,
            "all_source_lines_query": first_outside_query,
            "earliest_first_purchase": str(first_earliest),
            "latest_first_purchase": str(first_latest),
        },
        "step_4_5_cd_counts": {
            "zero": flagged(connection, STAGED, "cd_count = 0"),
            "negative": flagged(connection, STAGED, "cd_count < 0"),
            "fractional_string": flagged(connection, STAGED, cd_fractional),
            "other_unparseable": flagged(
                connection,
                STAGED,
                "parse_status = 'four_fields' AND cd_count IS NULL "
                f"AND NOT coalesce({cd_fractional}, false)",
            ),
            "maximum": query_one(connection, f"SELECT max(cd_count) FROM {STAGED}")[0],
        },
        "step_4_6_dollars": {
            "zero": flagged(connection, STAGED, "transaction_dollars = 0"),
            "negative": flagged(connection, STAGED, "transaction_dollars < 0"),
            "non_cent_precision_string": flagged(connection, STAGED, dollar_noncent),
            "other_unparseable": flagged(
                connection,
                STAGED,
                "parse_status = 'four_fields' AND transaction_dollars IS NULL "
                f"AND NOT coalesce({dollar_noncent}, false)",
            ),
            "maximum": str(
                query_one(connection, f"SELECT max(transaction_dollars) FROM {STAGED}")[
                    0
                ]
            ),
        },
        "step_4_7_reconciliation": {
            "raw_rows": raw_rows,
            "staged_rows": staged_rows,
            "conversion_failures": query_one(
                connection,
                f"SELECT count(*) FROM {STAGED} WHERE conversion_issue IS NOT NULL",
            )[0],
            "distinct_customers": customers,
            "readme_expected_transactions": EXPECTED_TRANSACTIONS,
            "readme_expected_customers": EXPECTED_CUSTOMERS,
        },
        "step_4_8_load_identity": {
            "raw_distinct_source_lines": raw_distinct_lines,
            "staged_distinct_source_lines": staged_distinct_lines,
            "staged_distinct_record_ids": staged_distinct_ids,
            "raw_to_staged_line_or_text_mismatches": query_one(
                connection,
                f"SELECT count(*) FROM {RAW} r FULL OUTER JOIN {STAGED} s "
                "ON r.source_line_number = s.source_line_number "
                "WHERE r.source_line_number IS NULL OR s.source_line_number IS NULL "
                "OR r.original_line IS DISTINCT FROM s.original_line",
            )[0],
        },
        "step_4_9_repeated_looking_records": {
            "exact_four_field_values": duplicate_profile(
                connection,
                "customer_id_raw, transaction_date_raw, cd_count_raw, dollar_value_raw",
            ),
            "same_customer_and_date": duplicate_profile(
                connection, "customer_id, transaction_date"
            ),
            "interpretation": "No order ID exists; neither pattern proves duplicated transactions.",
        },
        "step_4_10_profile": {
            "large_cd_threshold": "10 or more CDs on one source line",
            "large_cd_rows": flagged(connection, STAGED, "cd_count >= 10"),
            "large_dollar_threshold": "200.00 dollars or more on one source line",
            "large_dollar_rows": flagged(
                connection, STAGED, "transaction_dollars >= 200.00"
            ),
            "cd_count_99th_percentile": query_one(
                connection, f"SELECT quantile_cont(cd_count, 0.99) FROM {STAGED}"
            )[0],
            "dollars_99th_percentile": str(
                query_one(
                    connection,
                    f"SELECT quantile_cont(transaction_dollars, 0.99) FROM {STAGED}",
                )[0]
            ),
            "missing_calendar_dates": {
                "count": query_one(
                    connection, "SELECT count(*) FROM (" + day_gap_query + ")"
                )[0],
                "all_dates_query": day_gap_query,
            },
            "missing_customer_ids_between_00001_and_23570": {
                "count": query_one(
                    connection, "SELECT count(*) FROM (" + id_gap_query + ")"
                )[0],
                "all_ids_query": id_gap_query,
            },
            "gap_interpretation": "A gap would be a profile finding, not proof of a bad record or missing purchase.",
        },
    }


if __name__ == "__main__":
    with duckdb.connect(str(DATABASE), read_only=True) as database:
        report = run_checks(database)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT.relative_to(ROOT)}")
