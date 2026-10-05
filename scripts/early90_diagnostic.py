"""Compare early customer signals with later dollars at equal follow-up."""

import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import duckdb
from source_manifest import measure_source

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "CDNOW_data" / "CDNOW_master.txt"
MANIFEST = ROOT / "docs" / "source_manifest.json"
COHORT_REPORT = ROOT / "reports" / "cohort_analysis.json"
DATABASE = ROOT / "data" / "cdnow.duckdb"
OUTPUT = ROOT / "reports" / "early90_diagnostic.json"
STAGED = "cdnow_analysis.stg_cdnow_transactions"
CUSTOMERS = 23570


def customer_records(connection: duckdb.DuckDBPyConnection) -> list[tuple]:
    """Use only days 0–89 to define signals and days 90–449 for outcomes."""
    return connection.execute(
        f"WITH entry AS (SELECT customer_id, min(transaction_date) AS first_date "
        f"FROM {STAGED} GROUP BY customer_id), events AS ("
        f"SELECT s.customer_id, s.transaction_dollars, "
        f"date_diff('day', entry.first_date, s.transaction_date) AS age_days "
        f"FROM {STAGED} AS s JOIN entry USING (customer_id)) "
        f"SELECT customer_id, "
        f"coalesce(sum(transaction_dollars) FILTER (WHERE age_days BETWEEN 0 AND 89), 0) AS early_dollars, "
        f"count(*) FILTER (WHERE age_days BETWEEN 1 AND 89 AND transaction_dollars > 0) AS early_positive_later_rows, "
        f"coalesce(sum(transaction_dollars) FILTER (WHERE age_days BETWEEN 90 AND 449), 0) AS later_dollars, "
        f"count(*) FILTER (WHERE age_days BETWEEN 90 AND 449 AND transaction_dollars > 0) AS later_positive_rows, "
        f"coalesce(sum(transaction_dollars) FILTER (WHERE age_days BETWEEN 90 AND 269), 0) AS first_half_later_dollars, "
        f"coalesce(sum(transaction_dollars) FILTER (WHERE age_days BETWEEN 270 AND 449), 0) AS second_half_later_dollars "
        f"FROM events GROUP BY customer_id ORDER BY customer_id"
    ).fetchall()


def nearest_rank(values: list[Decimal], percentile: int) -> Decimal:
    """Return the observed value at the nearest-rank percentile."""
    ordered = sorted(values)
    index = (len(ordered) * percentile + 99) // 100 - 1
    return ordered[index]


def summarize(records: list[tuple]) -> dict:
    """Summarize dollars without treating an early signal as known at funding."""
    if len(records) != CUSTOMERS:
        raise ValueError("Diagnostic does not include every original customer")
    by_repeat = {
        "positive_dollar_later_date_purchase_during_days_1_89": [],
        "no_positive_dollar_later_date_purchase_during_days_1_89": [],
    }
    early_values = [row[1] for row in records]
    cuts = [nearest_rank(early_values, percentile) for percentile in (25, 50, 75)]
    by_spend: dict[str, list[tuple]] = {f"Q{i}": [] for i in range(1, 5)}
    by_spend_and_repeat: dict[str, list[tuple]] = {
        f"Q{i}_{repeat}": [] for i in range(1, 5) for repeat in ("repeat", "no_repeat")
    }
    for row in records:
        early_dollars, early_repeat_rows = row[1], row[2]
        repeat_label = (
            "positive_dollar_later_date_purchase_during_days_1_89"
            if early_repeat_rows > 0
            else "no_positive_dollar_later_date_purchase_during_days_1_89"
        )
        by_repeat[repeat_label].append(row)
        group_number = next(
            (index for index, cut in enumerate(cuts, start=1) if early_dollars <= cut),
            4,
        )
        spend_group = f"Q{group_number}"
        by_spend[spend_group].append(row)
        repeat_suffix = "repeat" if early_repeat_rows > 0 else "no_repeat"
        by_spend_and_repeat[f"{spend_group}_{repeat_suffix}"].append(row)

    def group_summary(rows: list[tuple], label: str) -> dict:
        count = len(rows)
        early = sum((row[1] for row in rows), Decimal("0.00"))
        later = sum((row[3] for row in rows), Decimal("0.00"))
        first_half = sum((row[5] for row in rows), Decimal("0.00"))
        second_half = sum((row[6] for row in rows), Decimal("0.00"))
        later_buyers = sum(row[4] > 0 for row in rows)
        return {
            "group": label,
            "customers": count,
            "share_of_original_cohort_percent": round(100 * count / CUSTOMERS, 1),
            "observed_early_days_0_89_reported_dollars": str(early),
            "observed_later_days_90_449_reported_dollars": str(later),
            "observed_days_90_269_reported_dollars": str(first_half),
            "observed_days_270_449_reported_dollars": str(second_half),
            "observed_later_dollars_per_group_customer": str(
                (later / count).quantize(Decimal("0.01"))
            ),
            "observed_days_90_269_dollars_per_group_customer": str(
                (first_half / count).quantize(Decimal("0.01"))
            ),
            "observed_days_270_449_dollars_per_group_customer": str(
                (second_half / count).quantize(Decimal("0.01"))
            ),
            "customers_with_positive_dollar_purchase_days_90_449": later_buyers,
            "later_purchasing_share_of_group_percent": round(
                100 * later_buyers / count, 1
            ),
        }

    return {
        "early_positive_later_date_repeat_signal": [
            group_summary(rows, label) for label, rows in by_repeat.items()
        ],
        "early_spend_nearest_rank_cutoffs": [str(cut) for cut in cuts],
        "early_spend_group_rule": "Q1 <= 25th-percentile observed value; Q2 <= median; Q3 <= 75th-percentile observed value; Q4 above; tied dollar values stay together, so counts may differ from 25%",
        "early_spend_groups": [
            group_summary(rows, label) for label, rows in by_spend.items()
        ],
        "early_spend_by_repeat_groups": [
            group_summary(rows, label) for label, rows in by_spend_and_repeat.items()
        ],
        "reconciliation": {
            "original_customers": CUSTOMERS,
            "early_days_0_89_reported_dollars": str(
                sum((row[1] for row in records), Decimal("0.00"))
            ),
            "later_days_90_449_reported_dollars": str(
                sum((row[3] for row in records), Decimal("0.00"))
            ),
            "days_90_269_reported_dollars": str(
                sum((row[5] for row in records), Decimal("0.00"))
            ),
            "days_270_449_reported_dollars": str(
                sum((row[6] for row in records), Decimal("0.00"))
            ),
        },
    }


def build_report(connection: duckdb.DuckDBPyConnection) -> dict:
    """Check source identity and emit both early-signal diagnostics."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if measure_source(SOURCE) != manifest:
        raise ValueError("Source differs from recorded manifest")
    observed = json.loads(COHORT_REPORT.read_text(encoding="utf-8"))
    if observed["source_manifest"] != manifest:
        raise ValueError("Phase 2 report does not match the source")
    periods = observed["customer_age_periods"]["periods"]
    if any(p["eligible_customers"] != CUSTOMERS for p in periods[:15]):
        raise ValueError("Diagnostic needs full exposure through age window 14")
    data = summarize(customer_records(connection))
    expected_early = sum(Decimal(p["reported_dollars"]) for p in periods[:3])
    expected_later = sum(Decimal(p["reported_dollars"]) for p in periods[3:15])
    if (
        Decimal(data["reconciliation"]["early_days_0_89_reported_dollars"])
        != expected_early
        or Decimal(data["reconciliation"]["later_days_90_449_reported_dollars"])
        != expected_later
    ):
        raise ValueError("Early and later dollars do not reconcile to phase 2")
    if (
        Decimal(data["reconciliation"]["days_90_269_reported_dollars"])
        + Decimal(data["reconciliation"]["days_270_449_reported_dollars"])
        != expected_later
    ):
        raise ValueError("Two equal later periods do not reconcile")
    return {
        "status": "early positive-dollar later-date repeat used as the lead diagnostic; early spend retained as secondary check",
        "headline_signal": "positive-dollar later-date purchase during customer-age days 1-89",
        "historical_decision_date": date(1998, 7, 15).isoformat(),
        "source_manifest": manifest,
        "population": "same 23,570 Q1 1997 first-purchase customers",
        "signal_window": "customer-age days 0-89; repeat signal requires positive-dollar row on a later date, days 1-89",
        "outcome_window": "customer-age days 90-449, fully observable for all 23,570 customers",
        "interpretation_limit": "descriptive within one cohort; early group cannot be known when an initial advance is made at first purchase; association is not causal or a future-cohort forecast",
        **data,
        "repayment_eligible_revenue": None,
    }


def main() -> None:
    """Write both early signals for comparison."""
    with duckdb.connect(str(DATABASE), read_only=True) as connection:
        report = build_report(connection)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}; repeat signal leads diagnostic")


if __name__ == "__main__":
    main()
