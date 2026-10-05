"""Build reproducible phase 2 summaries with source-to-staging reconciliation."""

import hashlib
import json
from datetime import date
from decimal import Decimal
from pathlib import Path
from statistics import median

import duckdb
from source_manifest import measure_source

ROOT = Path(__file__).resolve().parent.parent
DATABASE = ROOT / "data" / "cdnow.duckdb"
SOURCE = ROOT / "CDNOW_data" / "CDNOW_master.txt"
MANIFEST = ROOT / "docs" / "source_manifest.json"
CONTRACT = ROOT / "docs" / "cohort_measurement_contract.md"
PHASE1_REPORT = ROOT / "reports" / "exception_impact.json"
REPORT = ROOT / "reports" / "cohort_analysis.json"
STAGED = "cdnow_analysis.stg_cdnow_transactions"
CUTOFF = date(1998, 6, 30)
COHORT_START = date(1997, 1, 1)
AGE_PERIOD_DAYS = 30
AGE_PERIOD_COUNT = (CUTOFF - COHORT_START).days // AGE_PERIOD_DAYS + 1


def percent(numerator: int | Decimal, denominator: int | Decimal) -> str:
    """Express a count or dollar share to one decimal place."""
    return str(
        (Decimal(numerator) * 100 / Decimal(denominator)).quantize(Decimal("0.1"))
    )


def nearest_rank(values: list[int | Decimal], percentile: int) -> int | Decimal:
    """Return an observed value at the stated nearest-rank percentile."""
    ordered = sorted(values)
    rank = (len(ordered) * percentile + 99) // 100
    return ordered[max(rank - 1, 0)]


def customer_observations(connection: duckdb.DuckDBPyConnection) -> list[dict]:
    """Keep one row per customer, distinguishing later dates from extra entry-day rows."""
    rows = connection.execute(
        f"WITH entry AS (SELECT customer_id, min(transaction_date) AS first_date "
        f"FROM {STAGED} GROUP BY customer_id) "
        f"SELECT s.customer_id, entry.first_date, count(*) AS transaction_rows, "
        f"count(DISTINCT s.transaction_date) AS distinct_transaction_dates, "
        f"sum(s.transaction_dollars) AS reported_dollars, "
        f"count(*) FILTER (WHERE s.transaction_date = entry.first_date) "
        f"AS entry_date_rows, "
        f"sum(s.transaction_dollars) FILTER "
        f"(WHERE s.transaction_date = entry.first_date) AS entry_date_dollars, "
        f"max(s.transaction_dollars) AS largest_transaction_row_dollars, "
        f"min(s.transaction_date) FILTER "
        f"(WHERE s.transaction_date > entry.first_date) AS first_later_date, "
        f"min(s.transaction_date) FILTER "
        f"(WHERE s.transaction_date > entry.first_date "
        f"AND s.transaction_dollars > 0) AS first_positive_later_date "
        f"FROM {STAGED} AS s JOIN entry USING (customer_id) "
        f"GROUP BY s.customer_id, entry.first_date ORDER BY s.customer_id"
    ).fetchall()
    return [
        {
            "customer_id": customer_id,
            "first_date": first_date,
            "transaction_rows": transaction_rows,
            "distinct_transaction_dates": distinct_dates,
            "reported_dollars": dollars,
            "entry_date_rows": entry_date_rows,
            "entry_date_dollars": entry_date_dollars,
            "largest_transaction_row_dollars": largest_row_dollars,
            "first_later_date": first_later_date,
            "first_positive_later_date": first_positive_later_date,
        }
        for (
            customer_id,
            first_date,
            transaction_rows,
            distinct_dates,
            dollars,
            entry_date_rows,
            entry_date_dollars,
            largest_row_dollars,
            first_later_date,
            first_positive_later_date,
        ) in rows
    ]


def repeat_purchasing(customers: list[dict]) -> dict:
    """Describe observed later-date activity without treating censoring as churn."""
    total = len(customers)
    repeaters = [c for c in customers if c["first_later_date"] is not None]
    positive_repeaters = [
        c for c in customers if c["first_positive_later_date"] is not None
    ]
    gaps = [(c["first_later_date"] - c["first_date"]).days for c in repeaters]
    horizons = []
    for days in (30, 60, 90):
        eligible = [c for c in customers if (CUTOFF - c["first_date"]).days >= days]
        repeated = sum(
            c["first_later_date"] is not None
            and (c["first_later_date"] - c["first_date"]).days <= days
            for c in eligible
        )
        horizons.append(
            {
                "days_after_entry_inclusive": days,
                "eligible_customers": len(eligible),
                "later_date_repeaters": repeated,
                "repeat_percent": percent(repeated, len(eligible)),
            }
        )
    return {
        "definition": "at least one recorded transaction on a date after the first recorded date; no later-date row by cutoff is not permanent churn",
        "later_date_repeaters": len(repeaters),
        "later_date_repeat_percent": percent(len(repeaters), total),
        "no_later_date_observed_by_cutoff": total - len(repeaters),
        "positive_dollar_later_date_repeaters": len(positive_repeaters),
        "positive_dollar_later_date_repeat_percent": percent(
            len(positive_repeaters), total
        ),
        "later_date_only_zero_dollar_repeaters": len(repeaters)
        - len(positive_repeaters),
        "customers_with_multiple_entry_date_rows": sum(
            c["entry_date_rows"] > 1 for c in customers
        ),
        "customers_with_multiple_rows_but_no_later_date": sum(
            c["transaction_rows"] > 1 and c["first_later_date"] is None
            for c in customers
        ),
        "entry_date_transaction_rows": sum(c["entry_date_rows"] for c in customers),
        "entry_date_reported_dollars": str(
            sum((c["entry_date_dollars"] for c in customers), Decimal("0.00"))
        ),
        "later_date_reported_dollars": str(
            sum(
                (c["reported_dollars"] - c["entry_date_dollars"] for c in customers),
                Decimal("0.00"),
            )
        ),
        "time_to_first_later_date_days_among_repeaters": {
            "minimum": min(gaps),
            "p25_nearest_rank": nearest_rank(gaps, 25),
            "median": median(gaps),
            "p75_nearest_rank": nearest_rank(gaps, 75),
            "p90_nearest_rank": nearest_rank(gaps, 90),
            "maximum": max(gaps),
        },
        "cumulative_repeat_horizons": horizons,
    }


def customer_distribution(
    connection: duckdb.DuckDBPyConnection, customers: list[dict]
) -> dict:
    """Measure observed customer totals and the influence of large transactions."""
    total_dollars = sum((c["reported_dollars"] for c in customers), Decimal("0.00"))
    dollars = [c["reported_dollars"] for c in customers]
    row_counts = [c["transaction_rows"] for c in customers]
    date_counts = [c["distinct_transaction_dates"] for c in customers]
    ranked = sorted(customers, key=lambda c: c["reported_dollars"], reverse=True)
    shares = []
    for pct in (1, 10):
        count = (len(customers) * pct + 99) // 100
        amount = sum((c["reported_dollars"] for c in ranked[:count]), Decimal("0.00"))
        shares.append(
            {
                "top_customer_percent": pct,
                "customer_count_rounded_up": count,
                "minimum_observed_customer_dollars_in_group": str(
                    ranked[count - 1]["reported_dollars"]
                ),
                "reported_dollars": str(amount),
                "share_of_all_reported_dollars_percent": percent(amount, total_dollars),
                "transaction_rows": sum(c["transaction_rows"] for c in ranked[:count]),
                "largest_row_per_customer_dollars": str(
                    sum(
                        (c["largest_transaction_row_dollars"] for c in ranked[:count]),
                        Decimal("0.00"),
                    )
                ),
            }
        )
    large_rows = connection.execute(
        f"SELECT transaction_dollars FROM {STAGED} "
        f"ORDER BY transaction_dollars DESC, source_line_number LIMIT "
        f"{(sum(row_counts) + 99) // 100}"
    ).fetchall()
    largest_amount = sum((row[0] for row in large_rows), Decimal("0.00"))
    return {
        "definition": "per-customer totals over observed histories of unequal length; all customers and recorded rows retained",
        "top_customer_ranking": "rank customers by sum of all reported transaction dollars through June 30, 1998, descending; not by transaction count",
        "customers_with_zero_reported_dollars": sum(value == 0 for value in dollars),
        "customers_with_one_transaction_row": sum(value == 1 for value in row_counts),
        "customers_with_two_or_more_transaction_rows": sum(
            value >= 2 for value in row_counts
        ),
        "reported_dollars_per_customer": {
            "p25_nearest_rank": str(nearest_rank(dollars, 25)),
            "median": str(median(dollars)),
            "p75_nearest_rank": str(nearest_rank(dollars, 75)),
            "p90_nearest_rank": str(nearest_rank(dollars, 90)),
            "p99_nearest_rank": str(nearest_rank(dollars, 99)),
            "maximum": str(max(dollars)),
        },
        "transaction_rows_per_customer": {
            "median": median(row_counts),
            "p90_nearest_rank": nearest_rank(row_counts, 90),
            "p99_nearest_rank": nearest_rank(row_counts, 99),
            "maximum": max(row_counts),
        },
        "distinct_transaction_dates_per_customer": {
            "median": median(date_counts),
            "p90_nearest_rank": nearest_rank(date_counts, 90),
            "maximum": max(date_counts),
        },
        "top_customer_shares": shares,
        "largest_transaction_rows": {
            "row_count_top_one_percent_rounded_up": len(large_rows),
            "reported_dollars": str(largest_amount),
            "share_of_all_reported_dollars_percent": percent(
                largest_amount, total_dollars
            ),
            "largest_single_row_dollars": str(large_rows[0][0]),
        },
    }


def revenue_timing(
    connection: duckdb.DuckDBPyConnection, total_dollars: Decimal
) -> dict:
    """Split observed dollars by elapsed days without implying equal follow-up."""
    rows = connection.execute(
        f"WITH entry AS (SELECT customer_id, min(transaction_date) AS first_date "
        f"FROM {STAGED} GROUP BY customer_id), events AS ("
        f"SELECT s.customer_id, s.transaction_dollars, "
        f"date_diff('day', entry.first_date, s.transaction_date) AS age_days "
        f"FROM {STAGED} AS s JOIN entry USING (customer_id)) "
        f"SELECT CASE WHEN age_days = 0 THEN 'day 0' "
        f"WHEN age_days <= 30 THEN 'days 1-30' "
        f"WHEN age_days <= 90 THEN 'days 31-90' "
        f"WHEN age_days <= 180 THEN 'days 91-180' "
        f"WHEN age_days <= 365 THEN 'days 181-365' "
        f"ELSE 'days 366+' END AS age_bucket, "
        f"min(age_days) AS first_age_day, count(*) AS transaction_rows, "
        f"count(DISTINCT customer_id) AS purchasing_customers, "
        f"sum(transaction_dollars) AS reported_dollars "
        f"FROM events GROUP BY 1 ORDER BY first_age_day"
    ).fetchall()
    periods = [
        {
            "age_bucket": bucket,
            "transaction_rows": transaction_rows,
            "purchasing_customers": purchasing_customers,
            "reported_dollars": str(dollars),
            "share_of_all_reported_dollars_percent": percent(dollars, total_dollars),
        }
        for bucket, _, transaction_rows, purchasing_customers, dollars in rows
    ]
    if (
        sum((Decimal(p["reported_dollars"]) for p in periods), Decimal("0.00"))
        != total_dollars
    ):
        raise ValueError("Revenue-timing dollars do not reconcile")
    return {
        "definition": "elapsed days from first recorded date; descriptive observed-dollar split, including partial age windows, not like-aged rates",
        "periods": periods,
    }


def top_customer_timing(
    connection: duckdb.DuckDBPyConnection, total_dollars: Decimal, customer_count: int
) -> dict:
    """Check whether top observed spenders' dollars came only on their entry date."""
    top_one = (customer_count + 99) // 100
    top_ten = (customer_count * 10 + 99) // 100
    rows = connection.execute(
        f"WITH entry AS (SELECT customer_id, min(transaction_date) AS first_date "
        f"FROM {STAGED} GROUP BY customer_id), events AS ("
        f"SELECT s.customer_id, s.transaction_dollars, "
        f"date_diff('day', entry.first_date, s.transaction_date) AS age_days "
        f"FROM {STAGED} AS s JOIN entry USING (customer_id)), ranked AS ("
        f"SELECT customer_id, row_number() OVER "
        f"(ORDER BY sum(transaction_dollars) DESC, customer_id) AS spend_rank "
        f"FROM events GROUP BY customer_id) "
        f"SELECT CASE WHEN spend_rank <= {top_one} THEN 'top 1%' "
        f"WHEN spend_rank <= {top_ten} THEN 'next 9%' "
        f"ELSE 'bottom 90%' END "
        f"AS customer_group, min(spend_rank) AS first_rank, "
        f"count(DISTINCT events.customer_id) AS customers, "
        f"count(*) AS transaction_rows, "
        f"sum(transaction_dollars) AS reported_dollars, "
        f"sum(transaction_dollars) FILTER (WHERE age_days = 0) "
        f"AS entry_date_dollars, "
        f"sum(transaction_dollars) FILTER (WHERE age_days > 0) "
        f"AS later_date_dollars, "
        f"sum(transaction_dollars) FILTER (WHERE age_days > 90) "
        f"AS after_day_90_dollars "
        f"FROM events JOIN ranked USING (customer_id) "
        f"GROUP BY 1 ORDER BY first_rank"
    ).fetchall()
    groups = [
        {
            "customer_group": group,
            "customers": customers,
            "transaction_rows": transaction_rows,
            "reported_dollars": str(dollars),
            "share_of_all_reported_dollars_percent": percent(dollars, total_dollars),
            "entry_date_dollars": str(entry_dollars),
            "entry_date_share_of_group_percent": percent(entry_dollars, dollars),
            "later_date_dollars": str(later_dollars),
            "after_day_90_dollars": str(after_90_dollars),
            "after_day_90_share_of_group_percent": percent(after_90_dollars, dollars),
        }
        for (
            group,
            _,
            customers,
            transaction_rows,
            dollars,
            entry_dollars,
            later_dollars,
            after_90_dollars,
        ) in rows
    ]
    if (
        sum((Decimal(g["reported_dollars"]) for g in groups), Decimal("0.00"))
        != total_dollars
    ):
        raise ValueError("Customer-group dollars do not reconcile")
    return {
        "definition": "customers ranked by all reported dollars through cutoff; groups describe observed high spenders and must not be treated as known future types",
        "groups": groups,
    }


def staged_totals(connection: duckdb.DuckDBPyConnection) -> dict[str, int | str]:
    """Count the full typed input without filtering flagged source rows."""
    result = connection.execute(
        f"SELECT count(*), count(DISTINCT customer_id), "
        f"coalesce(sum(transaction_dollars), 0), "
        f"count(*) FILTER (WHERE conversion_issue IS NOT NULL) FROM {STAGED}"
    ).fetchone()
    if result is None:
        raise ValueError("Staging totals query returned no row")
    rows, customers, dollars, conversion_issues = result
    return {
        "transaction_rows": rows,
        "distinct_customers": customers,
        "reported_dollars": str(dollars),
        "conversion_issue_rows": conversion_issues,
    }


def calendar_quarters(connection: duckdb.DuckDBPyConnection) -> list[dict]:
    """Summarize every staged row by transaction calendar quarter."""
    rows = connection.execute(
        f"SELECT date_trunc('quarter', transaction_date)::DATE AS quarter_start, "
        f"count(*) AS transaction_rows, "
        f"count(DISTINCT customer_id) AS purchasing_customers, "
        f"count(DISTINCT customer_id) FILTER (WHERE transaction_dollars > 0) "
        f"AS customers_with_positive_dollars, "
        f"count(*) FILTER (WHERE transaction_dollars = 0) AS zero_dollar_rows, "
        f"coalesce(sum(transaction_dollars), 0) AS reported_dollars "
        f"FROM {STAGED} GROUP BY 1 ORDER BY 1"
    ).fetchall()
    return [
        {
            "calendar_quarter": f"{start.year}Q{(start.month - 1) // 3 + 1}",
            "quarter_start": start.isoformat(),
            "transaction_rows": transaction_rows,
            "purchasing_customers": purchasing_customers,
            "customers_with_positive_dollars": positive_dollar_customers,
            "zero_dollar_transaction_rows": zero_dollar_rows,
            "reported_dollars": str(dollars),
        }
        for (
            start,
            transaction_rows,
            purchasing_customers,
            positive_dollar_customers,
            zero_dollar_rows,
            dollars,
        ) in rows
    ]


def customer_age_periods(connection: duckdb.DuckDBPyConnection) -> list[dict]:
    """Compare customers only when their entire 30-day age window is observed."""
    rows = connection.execute(
        f"WITH entry AS (SELECT customer_id, min(transaction_date) AS first_date "
        f"FROM {STAGED} GROUP BY customer_id), "
        f"eligible AS (SELECT entry.customer_id, age_period "
        f"FROM entry CROSS JOIN range(0, {AGE_PERIOD_COUNT}) AS periods(age_period) "
        f"WHERE entry.first_date + CAST((age_period * {AGE_PERIOD_DAYS} "
        f"+ {AGE_PERIOD_DAYS - 1}) AS INTEGER) <= DATE '{CUTOFF.isoformat()}'), "
        f"events AS (SELECT source_line_number, s.customer_id, transaction_dollars, "
        f"date_diff('day', entry.first_date, transaction_date) "
        f"// {AGE_PERIOD_DAYS} AS age_period "
        f"FROM {STAGED} AS s JOIN entry USING (customer_id)) "
        f"SELECT eligible.age_period, count(DISTINCT eligible.customer_id), "
        f"count(events.source_line_number), "
        f"count(DISTINCT events.customer_id), "
        f"count(DISTINCT events.customer_id) FILTER "
        f"(WHERE events.transaction_dollars > 0), "
        f"coalesce(sum(events.transaction_dollars), 0) "
        f"FROM eligible LEFT JOIN events ON eligible.customer_id = events.customer_id "
        f"AND eligible.age_period = events.age_period "
        f"GROUP BY eligible.age_period ORDER BY eligible.age_period"
    ).fetchall()
    return [
        {
            "age_period": age_period,
            "first_day_after_entry": age_period * AGE_PERIOD_DAYS,
            "last_day_after_entry": (age_period + 1) * AGE_PERIOD_DAYS - 1,
            "eligible_customers": eligible,
            "transaction_rows": transaction_rows,
            "purchasing_customers": purchasing,
            "customers_with_positive_dollars": positive_dollar_customers,
            "reported_dollars": str(dollars),
            "purchasing_customer_percent": str(
                (Decimal(purchasing) * 100 / Decimal(eligible)).quantize(Decimal("0.1"))
            ),
            "dollars_per_eligible_customer": str(
                (dollars / Decimal(eligible)).quantize(Decimal("0.01"))
            ),
        }
        for (
            age_period,
            eligible,
            transaction_rows,
            purchasing,
            positive_dollar_customers,
            dollars,
        ) in rows
    ]


def age_window_partition(connection: duckdb.DuckDBPyConnection) -> dict:
    """Split all recorded rows between full and cutoff-censored age windows."""
    result = connection.execute(
        f"WITH entry AS (SELECT customer_id, min(transaction_date) AS first_date "
        f"FROM {STAGED} GROUP BY customer_id), classified AS ("
        f"SELECT s.transaction_dollars, entry.first_date + CAST("
        f"((date_diff('day', entry.first_date, s.transaction_date) "
        f"// {AGE_PERIOD_DAYS} + 1) * {AGE_PERIOD_DAYS} - 1) AS INTEGER) "
        f"<= DATE '{CUTOFF.isoformat()}' AS full_window "
        f"FROM {STAGED} AS s JOIN entry USING (customer_id)) "
        f"SELECT count(*) FILTER (WHERE full_window), "
        f"coalesce(sum(transaction_dollars) FILTER (WHERE full_window), 0), "
        f"count(*) FILTER (WHERE NOT full_window), "
        f"coalesce(sum(transaction_dollars) FILTER (WHERE NOT full_window), 0) "
        f"FROM classified"
    ).fetchone()
    if result is None:
        raise ValueError("Age-window partition query returned no row")
    full_rows, full_dollars, partial_rows, partial_dollars = result
    return {
        "full_window_transaction_rows": full_rows,
        "full_window_reported_dollars": str(full_dollars),
        "partial_window_transaction_rows": partial_rows,
        "partial_window_reported_dollars": str(partial_dollars),
    }


def build_report(connection: duckdb.DuckDBPyConnection) -> dict:
    """Record the source, definitions, and exact phase 1 reconciliation."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if measure_source(SOURCE) != manifest:
        raise ValueError("Source file differs from docs/source_manifest.json")

    phase1 = json.loads(PHASE1_REPORT.read_text(encoding="utf-8"))
    if phase1["source_sha256"] != manifest["sha256"]:
        raise ValueError("Phase 1 report does not match the source manifest")

    totals = staged_totals(connection)
    baseline = phase1["baseline_and_chosen_analysis_input"]
    for field in ("transaction_rows", "distinct_customers", "reported_dollars"):
        if totals[field] != baseline[field]:
            raise ValueError(f"Staging {field} differs from the phase 1 baseline")
    if totals["conversion_issue_rows"]:
        raise ValueError("Staging contains conversion issues; review before analysis")

    quarters = calendar_quarters(connection)
    if (
        sum(period["transaction_rows"] for period in quarters)
        != totals["transaction_rows"]
    ):
        raise ValueError("Calendar-quarter transaction rows do not reconcile")
    if sum(
        (Decimal(period["reported_dollars"]) for period in quarters), Decimal("0.00")
    ) != Decimal(totals["reported_dollars"]):
        raise ValueError("Calendar-quarter reported dollars do not reconcile")
    if not quarters or quarters[0]["calendar_quarter"] != "1997Q1":
        raise ValueError("Expected the cohort's entry quarter to be 1997Q1")
    if quarters[0]["purchasing_customers"] != totals["distinct_customers"]:
        raise ValueError("Not every customer appears in the entry quarter")

    age_periods = customer_age_periods(connection)
    age_partition = age_window_partition(connection)
    if (
        not age_periods
        or age_periods[0]["eligible_customers"] != totals["distinct_customers"]
    ):
        raise ValueError("Age zero does not include every cohort customer")
    if age_periods[0]["purchasing_customers"] != totals["distinct_customers"]:
        raise ValueError("Age-zero purchase count does not include every customer")
    if any(
        period["purchasing_customers"] > period["eligible_customers"]
        for period in age_periods
    ):
        raise ValueError("An age-period purchase count exceeds its denominator")
    if (
        sum(period["transaction_rows"] for period in age_periods)
        != age_partition["full_window_transaction_rows"]
    ):
        raise ValueError("Full age-period transaction rows do not reconcile")
    if sum(
        (Decimal(period["reported_dollars"]) for period in age_periods),
        Decimal("0.00"),
    ) != Decimal(age_partition["full_window_reported_dollars"]):
        raise ValueError("Full age-period reported dollars do not reconcile")
    if age_partition["full_window_transaction_rows"] + age_partition[
        "partial_window_transaction_rows"
    ] != totals["transaction_rows"] or Decimal(
        age_partition["full_window_reported_dollars"]
    ) + Decimal(age_partition["partial_window_reported_dollars"]) != Decimal(
        totals["reported_dollars"]
    ):
        raise ValueError("Full and partial age windows do not cover all source rows")

    customers = customer_observations(connection)
    if (
        len(customers) != totals["distinct_customers"]
        or sum(customer["transaction_rows"] for customer in customers)
        != totals["transaction_rows"]
    ):
        raise ValueError("Customer-level counts do not reconcile")
    if sum(
        (customer["reported_dollars"] for customer in customers), Decimal("0.00")
    ) != Decimal(totals["reported_dollars"]):
        raise ValueError("Customer-level dollars do not reconcile")
    if any(
        not COHORT_START <= customer["first_date"] <= date(1997, 3, 31)
        for customer in customers
    ):
        raise ValueError("A customer enters outside Q1 1997")

    entry_quarter_dollars = Decimal(quarters[0]["reported_dollars"])
    return {
        "phase": "2: observed cohort",
        "status": "Phase 2 observed-cohort analysis verified; external claims audited separately",
        "source_manifest": manifest,
        "measurement_contract": {
            "path": CONTRACT.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
        },
        "observation_window": {
            "start": "1997-01-01",
            "cutoff_inclusive": "1998-06-30",
            "cohort_entry": "first recorded transaction in Q1 1997",
        },
        "analysis_input": {
            "relation": STAGED,
            "row_treatment": "retain all source rows, including zero-dollar and repeated-looking rows",
            "revenue_definition": "reported transaction dollars; not cash collected, profit, forecast or repayment-eligible revenue",
            "customer_age_period_days": 30,
            "age_zero": "days 0-29 from each customer's first recorded date, including entry",
            "full_window_denominator": "only customers observable through the end of the age period",
        },
        "reconciliation": {
            "staged": totals,
            "phase1_baseline": baseline,
            "matches_phase1": True,
        },
        "calendar_quarters": {
            "definition": "transaction calendar quarters; purchasing customers include zero-dollar rows; customer counts are not additive across quarters",
            "periods": quarters,
            "entry_quarter": {
                "calendar_quarter": "1997Q1",
                "reported_dollars": str(entry_quarter_dollars),
            },
            "later_calendar_quarters": {
                "reported_dollars": str(
                    Decimal(totals["reported_dollars"]) - entry_quarter_dollars
                ),
            },
            "interpretation": "All cohort members entered in Q1 1997; entry-quarter dollars include first and later purchases made that quarter. Later calendar quarters mix customers at different ages since entry.",
        },
        "customer_age_periods": {
            "definition": "consecutive 30-day periods from each customer's first recorded date; only fully observable customer-periods enter rates, averages, and comparable age totals",
            "periods": age_periods,
            "source_row_partition": age_partition,
            "interpretation": "Age zero includes the first recorded purchase, so its purchasing share is 100% by definition. Partial-window rows remain in overall and calendar totals but are excluded from like-aged measures.",
        },
        "repeat_purchasing": repeat_purchasing(customers),
        "customer_distribution": customer_distribution(connection, customers),
        "revenue_timing": revenue_timing(
            connection, Decimal(totals["reported_dollars"])
        ),
        "top_customer_timing": top_customer_timing(
            connection,
            Decimal(totals["reported_dollars"]),
            len(customers),
        ),
    }


def main() -> None:
    """Write deterministic observed-cohort summaries and reconciliations."""
    with duckdb.connect(str(DATABASE), read_only=True) as database:
        report = build_report(database)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT.relative_to(ROOT)}; phase 1 totals reconciled")


if __name__ == "__main__":
    main()
