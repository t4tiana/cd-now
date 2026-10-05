"""Check the early-signal and equal-follow-up age boundaries."""

import sys
from datetime import date, timedelta
from pathlib import Path

import duckdb

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from early90_diagnostic import customer_records


def test_early_and_later_windows_do_not_leak() -> None:
    """Day 89 is early; days 90–449 are outcomes; day 450 is excluded."""
    connection = duckdb.connect(":memory:")
    connection.execute("CREATE SCHEMA cdnow_analysis")
    connection.execute(
        "CREATE TABLE cdnow_analysis.stg_cdnow_transactions "
        "(customer_id INTEGER, transaction_date DATE, transaction_dollars DECIMAL(12,2))"
    )
    entry = date(1997, 1, 1)
    rows = [
        (1, entry + timedelta(days=age), dollars)
        for age, dollars in (
            (0, 10),
            (0, 5),
            (89, 20),
            (90, 30),
            (449, 40),
            (450, 50),
        )
    ]
    connection.executemany(
        "INSERT INTO cdnow_analysis.stg_cdnow_transactions VALUES (?, ?, ?)", rows
    )
    result = customer_records(connection)
    connection.close()
    assert result[0][1:] == (35, 1, 70, 2, 30, 40)
