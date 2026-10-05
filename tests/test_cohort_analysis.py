"""Focused checks for observed-cohort definitions and source reconciliation."""

import json
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import duckdb
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import cohort_analysis
from cohort_analysis import (
    age_window_partition,
    build_report,
    customer_age_periods,
    customer_distribution,
    customer_observations,
    repeat_purchasing,
)


def test_repeats_exclude_same_day_rows_and_show_zero_dollar_sensitivity() -> None:
    connection = duckdb.connect(":memory:")
    connection.execute("CREATE SCHEMA cdnow_analysis")
    connection.execute(
        "CREATE TABLE cdnow_analysis.stg_cdnow_transactions "
        "(source_line_number INTEGER, customer_id VARCHAR, "
        "transaction_date DATE, transaction_dollars DECIMAL(12, 2))"
    )
    connection.executemany(
        "INSERT INTO cdnow_analysis.stg_cdnow_transactions VALUES (?, ?, ?, ?)",
        [
            (1, "A", "1997-01-01", Decimal("0.00")),
            (2, "A", "1997-01-01", Decimal("10.00")),
            (3, "A", "1997-01-31", Decimal("5.00")),
            (4, "A", "1997-03-02", Decimal("20.00")),
            (5, "B", "1997-01-01", Decimal("0.00")),
            (6, "C", "1997-01-01", Decimal("10.00")),
            (7, "C", "1997-01-01", Decimal("20.00")),
            (8, "D", "1997-03-31", Decimal("5.00")),
            (9, "D", "1997-04-01", Decimal("0.00")),
        ],
    )

    customers = customer_observations(connection)
    repeats = repeat_purchasing(customers)
    distribution = customer_distribution(connection, customers)

    assert repeats["later_date_repeaters"] == 2
    assert repeats["positive_dollar_later_date_repeaters"] == 1
    assert repeats["later_date_only_zero_dollar_repeaters"] == 1
    assert repeats["customers_with_multiple_rows_but_no_later_date"] == 1
    assert repeats["entry_date_transaction_rows"] == 6
    assert repeats["later_date_reported_dollars"] == "25.00"
    assert repeats["cumulative_repeat_horizons"][0]["later_date_repeaters"] == 2
    assert distribution["customers_with_zero_reported_dollars"] == 1
    assert distribution["top_customer_shares"][0]["reported_dollars"] == "35.00"
    assert distribution["top_customer_shares"][0]["customer_count_rounded_up"] == 1
    assert distribution["largest_transaction_rows"]["reported_dollars"] == "20.00"
    connection.close()


def test_first_date_and_complete_age_windows_exclude_partial_followup(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A cutoff-day row counts only when its entire customer-age window is visible."""
    monkeypatch.setattr(cohort_analysis, "CUTOFF", date(1997, 4, 30))
    monkeypatch.setattr(cohort_analysis, "AGE_PERIOD_COUNT", 4)
    connection = duckdb.connect(":memory:")
    connection.execute("CREATE SCHEMA cdnow_analysis")
    connection.execute(
        "CREATE TABLE cdnow_analysis.stg_cdnow_transactions "
        "(source_line_number INTEGER, customer_id VARCHAR, "
        "transaction_date DATE, transaction_dollars DECIMAL(12, 2))"
    )
    connection.executemany(
        "INSERT INTO cdnow_analysis.stg_cdnow_transactions VALUES (?, ?, ?, ?)",
        [
            (1, "A", "1997-01-31", Decimal("3.00")),  # day 30
            (2, "A", "1997-01-01", Decimal("0.00")),  # entry, out of row order
            (3, "A", "1997-01-01", Decimal("10.00")),
            (4, "A", "1997-01-30", Decimal("2.00")),  # day 29
            (5, "A", "1997-04-01", Decimal("4.00")),  # day 90
            (6, "A", "1997-04-30", Decimal("5.00")),  # day 119, full window
            (7, "B", "1997-04-30", Decimal("7.00")),  # day 30, partial window
            (8, "B", "1997-03-31", Decimal("11.00")),
            (9, "B", "1997-04-29", Decimal("13.00")),  # day 29, full window
        ],
    )

    customers = {row["customer_id"]: row for row in customer_observations(connection)}
    periods = customer_age_periods(connection)
    partition = age_window_partition(connection)

    assert customers["A"]["first_date"] == date(1997, 1, 1)
    assert customers["A"]["entry_date_rows"] == 2
    assert customers["A"]["entry_date_dollars"] == Decimal("10.00")
    assert customers["B"]["first_date"] == date(1997, 3, 31)
    assert [p["eligible_customers"] for p in periods] == [2, 1, 1, 1]
    assert [p["transaction_rows"] for p in periods] == [5, 1, 0, 2]
    assert [p["reported_dollars"] for p in periods] == ["36.00", "3.00", "0.00", "9.00"]
    assert periods[1]["purchasing_customers"] == 1
    assert periods[1]["purchasing_customer_percent"] == "100.0"
    assert periods[1]["dollars_per_eligible_customer"] == "3.00"
    assert partition == {
        "full_window_transaction_rows": 8,
        "full_window_reported_dollars": "48.00",
        "partial_window_transaction_rows": 1,
        "partial_window_reported_dollars": "7.00",
    }
    connection.close()


def test_report_reconciles_staged_rows_to_source_baseline() -> None:
    """The committed cohort report must use every source row and exact cents."""
    with duckdb.connect(str(cohort_analysis.DATABASE), read_only=True) as connection:
        report = build_report(connection)

    totals = report["reconciliation"]["staged"]
    assert totals["transaction_rows"] == 69_659
    assert totals["distinct_customers"] == 23_570
    assert totals["reported_dollars"] == "2500315.63"
    assert totals["conversion_issue_rows"] == 0
    for field in ("transaction_rows", "distinct_customers", "reported_dollars"):
        assert totals[field] == report["reconciliation"]["phase1_baseline"][field]
    assert (
        sum(p["transaction_rows"] for p in report["calendar_quarters"]["periods"])
        == 69_659
    )
    partition = report["customer_age_periods"]["source_row_partition"]
    assert (
        partition["full_window_transaction_rows"]
        + partition["partial_window_transaction_rows"]
        == 69_659
    )
    assert Decimal(partition["full_window_reported_dollars"]) + Decimal(
        partition["partial_window_reported_dollars"]
    ) == Decimal("2500315.63")


def test_report_rejects_a_changed_phase1_baseline(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A mismatch must stop the report before publishing misleading totals."""
    baseline = json.loads(cohort_analysis.PHASE1_REPORT.read_text(encoding="utf-8"))
    baseline["baseline_and_chosen_analysis_input"]["transaction_rows"] += 1
    changed_report = tmp_path / "changed_phase1.json"
    changed_report.write_text(json.dumps(baseline), encoding="utf-8")
    monkeypatch.setattr(cohort_analysis, "PHASE1_REPORT", changed_report)

    with (
        duckdb.connect(str(cohort_analysis.DATABASE), read_only=True) as connection,
        pytest.raises(ValueError, match="Staging transaction_rows differs"),
    ):
        build_report(connection)
