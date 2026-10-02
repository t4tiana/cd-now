"""Quantify the chosen phase 1 treatment of flagged CDnow rows."""

import json
from decimal import Decimal
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
DATABASE = ROOT / "data" / "cdnow.duckdb"
REPORT = ROOT / "reports" / "exception_impact.json"
STAGED = "cdnow_analysis.stg_cdnow_transactions"


def totals(
    connection: duckdb.DuckDBPyConnection, relation: str, condition: str
) -> dict:
    """Count rows, customers, and exact reported dollars for a chosen set of lines."""
    result = connection.execute(
        f"SELECT count(*), count(DISTINCT customer_id), "
        f"coalesce(sum(transaction_dollars), 0) FROM {relation} WHERE {condition}"
    ).fetchone()
    if result is None:
        raise ValueError("Totals query returned no row")
    rows, customers, dollars = result
    return {
        "transaction_rows": rows,
        "distinct_customers": customers,
        "reported_dollars": str(dollars),
    }


def build_report(connection: duckdb.DuckDBPyConnection) -> dict:
    """Keep all source rows; show two unadopted exclusion sensitivities."""
    baseline = totals(connection, STAGED, "true")
    zero_removed = totals(connection, STAGED, "transaction_dollars <> 0")
    ranked = (
        "(SELECT *, row_number() OVER (PARTITION BY customer_id_raw, "
        "transaction_date_raw, cd_count_raw, dollar_value_raw "
        f"ORDER BY source_line_number) AS occurrence FROM {STAGED}) AS ranked"
    )
    exact_repeat_removed = totals(connection, ranked, "occurrence = 1")
    return {
        "source_sha256": json.loads(
            (ROOT / "docs" / "source_manifest.json").read_text(encoding="utf-8")
        )["sha256"],
        "chosen_treatment": "retain every source line; no exclusions or corrections",
        "baseline_and_chosen_analysis_input": baseline,
        "applied_change": {
            "transaction_rows": 0,
            "distinct_customers": 0,
            "reported_dollars": "0.00",
        },
        "unadopted_sensitivities": {
            "remove_all_zero_dollar_rows": {
                "result": zero_removed,
                "change_from_baseline": {
                    "transaction_rows": zero_removed["transaction_rows"]
                    - baseline["transaction_rows"],
                    "distinct_customers": zero_removed["distinct_customers"]
                    - baseline["distinct_customers"],
                    "reported_dollars": str(
                        Decimal(zero_removed["reported_dollars"])
                        - Decimal(baseline["reported_dollars"])
                    ),
                },
                "reason_not_adopted": "Their business meaning is unknown; 68 customers have no other recorded row.",
            },
            "keep_one_of_each_exact_four_field_combination": {
                "result": exact_repeat_removed,
                "change_from_baseline": {
                    "transaction_rows": exact_repeat_removed["transaction_rows"]
                    - baseline["transaction_rows"],
                    "distinct_customers": exact_repeat_removed["distinct_customers"]
                    - baseline["distinct_customers"],
                    "reported_dollars": str(
                        Decimal(exact_repeat_removed["reported_dollars"])
                        - Decimal(baseline["reported_dollars"])
                    ),
                },
                "reason_not_adopted": "No order ID or other evidence proves these are duplicate transactions.",
            },
        },
    }


if __name__ == "__main__":
    with duckdb.connect(str(DATABASE), read_only=True) as database:
        report = build_report(database)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT.relative_to(ROOT)}")
