"""Verify phase 1 artifacts against the unchanged source and DuckDB tables."""

import json
from decimal import Decimal
from pathlib import Path

import duckdb
from load_raw import iter_source_records
from source_manifest import measure_source

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "CDNOW_data" / "CDNOW_master.txt"
MANIFEST = ROOT / "docs" / "source_manifest.json"
RAW_REPORT = ROOT / "reports" / "raw_load.json"
QUALITY_REPORT = ROOT / "reports" / "data_quality.json"
IMPACT_REPORT = ROOT / "reports" / "exception_impact.json"
DATABASE = ROOT / "data" / "cdnow.duckdb"


def verify() -> None:
    """Raise on a hash, line, count, traceability, or amount mismatch."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    raw_report = json.loads(RAW_REPORT.read_text(encoding="utf-8"))
    quality = json.loads(QUALITY_REPORT.read_text(encoding="utf-8"))
    impact = json.loads(IMPACT_REPORT.read_text(encoding="utf-8"))
    assert measure_source(SOURCE) == manifest
    assert raw_report["source_sha256"] == manifest["sha256"]
    assert quality["source_sha256"] == manifest["sha256"]
    assert impact["source_sha256"] == manifest["sha256"]

    with duckdb.connect(str(DATABASE), read_only=True) as connection:
        raw_lines = connection.execute(
            "SELECT source_line_number, original_line FROM cdnow_raw.source_lines "
            "ORDER BY source_line_number"
        ).fetchall()
        source_lines = list(iter_source_records(SOURCE))
        assert len(raw_lines) == len(source_lines) == manifest["line_count"]
        for stored, source in zip(raw_lines, source_lines, strict=True):
            assert stored == (source["source_line_number"], source["original_line"])

        staged = connection.execute(
            "SELECT count(*), count(DISTINCT source_line_number), "
            "count(DISTINCT customer_id), count(*) FILTER "
            "(WHERE conversion_issue IS NOT NULL), sum(transaction_dollars) "
            "FROM cdnow_analysis.stg_cdnow_transactions"
        ).fetchone()
        assert staged is not None
        rows, distinct_lines, customers, exceptions, dollars = staged
        assert rows == distinct_lines == raw_report["raw_rows"]
        assert customers == quality["step_4_7_reconciliation"]["distinct_customers"]
        assert exceptions == quality["step_4_7_reconciliation"]["conversion_failures"]
        baseline = impact["baseline_and_chosen_analysis_input"]
        assert rows == baseline["transaction_rows"]
        assert customers == baseline["distinct_customers"]
        assert Decimal(str(dollars)) == Decimal(baseline["reported_dollars"])

        verified_queries = 0
        for section in quality.values():
            if not isinstance(section, dict):
                continue
            for result in section.values():
                if (
                    not isinstance(result, dict)
                    or "all_source_lines_query" not in result
                ):
                    continue
                count_row = connection.execute(
                    "SELECT count(*) FROM (" + result["all_source_lines_query"] + ")"
                ).fetchone()
                assert count_row is not None
                expected = result.get("count", result.get("rows_in_groups"))
                if expected is not None:
                    assert count_row[0] == expected
                verified_queries += 1

    print(
        f"Verified source hash, {rows} exact source lines, {customers} customers, "
        f"{exceptions} conversion exceptions, reported dollars {dollars}, "
        f"and {verified_queries} source-line queries."
    )


if __name__ == "__main__":
    verify()
