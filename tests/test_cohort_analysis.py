"""Focused checks for later-date repeats and customer-dollar concentration."""

import sys
from decimal import Decimal
from pathlib import Path

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from cohort_analysis import (
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
