"""Render the observed-cohort JSON as readable Markdown tables."""

import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "reports" / "cohort_analysis.json"
DESTINATION = ROOT / "reports" / "cohort_tables.md"


def money(value: str) -> str:
    """Format an exact-dollar JSON value for a display table."""
    return f"${Decimal(value):,.2f}"


def table(headers: list[str], rows: list[list[object]]) -> list[str]:
    """Build a plain Markdown table with consistent columns."""
    return [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
        *("| " + " | ".join(str(value) for value in row) + " |" for row in rows),
        "",
    ]


def render(report: dict) -> str:
    """Keep the visible report tied to the checked machine-readable output."""
    totals = report["reconciliation"]["staged"]
    quarters = report["calendar_quarters"]["periods"]
    ages = report["customer_age_periods"]["periods"]
    repeats = report["repeat_purchasing"]
    distribution = report["customer_distribution"]
    timing = report["revenue_timing"]["periods"]
    groups = report["top_customer_timing"]["groups"]

    lines = [
        "# Observed Q1 1997 CDnow cohort: table view",
        "",
        (
            "**Observation cutoff:** June 30, 1998, inclusive. **Population:** "
            f"{totals['distinct_customers']:,} customers and "
            f"{totals['transaction_rows']:,} retained transaction rows. "
            f"**Reported dollars:** {money(totals['reported_dollars'])}."
        ),
        "",
        (
            "These are recorded sales amounts for one first-purchase cohort. They are "
            "not cash collected, profit, a forecast, customer lifetime value, or "
            "repayment-eligible revenue. Source, definitions, and reconciliations "
            "are in [cohort_analysis.json](cohort_analysis.json) and the "
            "[measurement contract](../docs/cohort_measurement_contract.md)."
        ),
        "",
        "## Calendar quarters",
        "",
        (
            "Customers can appear in several quarters, so customer counts do not add "
            "to the cohort size. All customers first appear in 1997Q1 by definition."
        ),
        "",
    ]
    lines += table(
        ["Quarter", "Rows", "Customers", "Reported dollars"],
        [
            [
                q["calendar_quarter"],
                f"{q['transaction_rows']:,}",
                f"{q['purchasing_customers']:,}",
                money(q["reported_dollars"]),
            ]
            for q in quarters
        ],
    )
    lines += [
        "## Customer age: complete 30-day windows",
        "",
        (
            "Age 0 is days 0–29 and includes each customer's entry purchase. "
            "Only customers observable through an entire window enter its "
            "denominator and numerators. Partial-window transactions remain in "
            "the full and calendar totals above."
        ),
        "",
    ]
    lines += table(
        ["Age", "Days", "Eligible", "Purchasers", "Purchase %", "Reported dollars"],
        [
            [
                a["age_period"],
                f"{a['first_day_after_entry']}–{a['last_day_after_entry']}",
                f"{a['eligible_customers']:,}",
                f"{a['purchasing_customers']:,}",
                f"{a['purchasing_customer_percent']}%",
                money(a["reported_dollars"]),
            ]
            for a in ages
        ],
    )
    lines += [
        "## Repeat purchasing and frequency",
        "",
        (
            "A repeat requires a recorded row on a *later calendar date*. "
            "A row is not a verified distinct order. No later-date purchase "
            "observed by the cutoff does not mean permanent churn."
        ),
        "",
    ]
    lines += table(
        ["Measure", "Observed result"],
        [
            [
                "Later-date repeaters",
                f"{repeats['later_date_repeaters']:,} ({repeats['later_date_repeat_percent']}%)",
            ],
            [
                "Positive-dollar later-date repeaters",
                f"{repeats['positive_dollar_later_date_repeaters']:,}",
            ],
            [
                "No later date observed by cutoff",
                f"{repeats['no_later_date_observed_by_cutoff']:,}",
            ],
            [
                "Median days to first later date, among repeaters",
                f"{repeats['time_to_first_later_date_days_among_repeaters']['median']:g}",
            ],
            [
                "Multiple rows but no later date",
                f"{repeats['customers_with_multiple_rows_but_no_later_date']:,}",
            ],
            [
                "Later-date reported dollars",
                money(repeats["later_date_reported_dollars"]),
            ],
            [
                "Customers with one recorded row",
                f"{distribution['customers_with_one_transaction_row']:,}",
            ],
            [
                "Median recorded rows per customer",
                f"{distribution['transaction_rows_per_customer']['median']:g}",
            ],
            [
                "90th percentile recorded rows",
                distribution["transaction_rows_per_customer"]["p90_nearest_rank"],
            ],
        ],
    )
    lines += table(
        [
            "Horizon after entry",
            "Fully observed customers",
            "Repeated by horizon",
            "Repeat %",
        ],
        [
            [
                f"{h['days_after_entry_inclusive']} days",
                f"{h['eligible_customers']:,}",
                f"{h['later_date_repeaters']:,}",
                f"{h['repeat_percent']}%",
            ]
            for h in repeats["cumulative_repeat_horizons"]
        ],
    )
    lines += [
        "## When observed dollars arrived",
        "",
        (
            "This dollar split uses elapsed days and retains partial windows. "
            "It describes recorded timing; unlike the complete-window table, "
            "it does not compare equal customer exposure."
        ),
        "",
    ]
    lines += table(
        ["Days since entry", "Rows", "Customers", "Reported dollars", "Share of total"],
        [
            [
                p["age_bucket"],
                f"{p['transaction_rows']:,}",
                f"{p['purchasing_customers']:,}",
                money(p["reported_dollars"]),
                f"{p['share_of_all_reported_dollars_percent']}%",
            ]
            for p in timing
        ],
    )
    lines += [
        "## Customer-dollar distribution and concentration",
        "",
        (
            "Customers are ranked by the **sum of their recorded dollars** through "
            "the cutoff, not by number of transactions. The ranking includes 68 "
            "customers with zero recorded dollars. Observed histories have unequal "
            "lengths. High spenders are identified in hindsight; their future "
            "presence cannot be assumed."
        ),
        "",
    ]
    spend = distribution["reported_dollars_per_customer"]
    lines += table(
        ["Measure", "Observed dollars"],
        [
            [
                "Mean per customer",
                money(
                    str(
                        Decimal(totals["reported_dollars"])
                        / Decimal(totals["distinct_customers"])
                    )
                ),
            ],
            ["Median per customer", money(spend["median"])],
            ["90th percentile", money(spend["p90_nearest_rank"])],
            ["99th percentile", money(spend["p99_nearest_rank"])],
            ["Largest customer total", money(spend["maximum"])],
        ],
    )
    lines += table(
        [
            "Rank by observed customer dollars",
            "Customers",
            "Lowest group total",
            "Group dollars",
            "Share of cohort",
        ],
        [
            [
                f"Top {s['top_customer_percent']}%",
                f"{s['customer_count_rounded_up']:,}",
                money(s["minimum_observed_customer_dollars_in_group"]),
                money(s["reported_dollars"]),
                f"{s['share_of_all_reported_dollars_percent']}%",
            ]
            for s in distribution["top_customer_shares"]
        ],
    )
    large = distribution["largest_transaction_rows"]
    lines += [
        (
            f"The largest {large['row_count_top_one_percent_rounded_up']:,} "
            "individual transaction rows (top 1% of rows) total "
            f"{money(large['reported_dollars'])}, or "
            f"{large['share_of_all_reported_dollars_percent']}% of recorded dollars. "
            "This checks whether a small set of unusually large *rows* dominates "
            "the cohort total; it does not identify who placed the transactions."
        ),
        "",
        "## Timing among observed spending groups",
        "",
        (
            "The top 1% and next 9% are selected by **total observed dollars**, "
            "not row count, using their *entire observed* history. This table "
            "tests an opening-stock-up explanation for their recorded totals, "
            "but does not forecast which new customers will join those groups."
        ),
        "",
    ]
    lines += table(
        [
            "Group",
            "Customers",
            "Total dollars",
            "Entry-date dollars",
            "Entry %",
            "After day 90",
            "After day 90 %",
        ],
        [
            [
                g["customer_group"],
                f"{g['customers']:,}",
                money(g["reported_dollars"]),
                money(g["entry_date_dollars"]),
                f"{g['entry_date_share_of_group_percent']}%",
                money(g["after_day_90_dollars"]),
                f"{g['after_day_90_share_of_group_percent']}%",
            ]
            for g in groups
        ],
    )
    lines += [
        "## Interpretation for the decision meeting",
        "",
        (
            "The cohort generated substantial later-date sales, but most were "
            "not within 30 days of entry. Its top observed spenders bought "
            "repeatedly rather than deriving most recorded dollars from their "
            "entry date. These findings support examining persistent revenue; "
            "they do not establish why customers returned, whether other cohorts "
            "will behave similarly, or what remains after acquisition and "
            "service costs. Future-cohort and repayment scenarios need explicit "
            "downside assumptions and separate eligibility rules."
        ),
        "",
        (
            "A [January 1998 Amazon release](https://press.aboutamazon.com/1998/1/amazon-com-announces-financial-results-for-fourth-quarter-and-1997-year-end) "
            "reported that repeat customers placed over 58% of Q4 1997 *orders*. "
            "A [May 22, 1998 CDnow interview](https://www.worldradiohistory.com/Archive-All-Music/Archive-RandR/1990s/1998/RR-1998-05-22.pdf) "
            "reported that existing customers generated 51% of Q1 1998 "
            "*company-wide sales*. Neither measure is comparable to this "
            "cohort's 48.9% share of customers with a later-date row. "
            "Comparable CDnow cohorts with the same definition and follow-up "
            "would be more useful."
        ),
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    """Write the table view from the latest checked JSON analysis."""
    report = json.loads(SOURCE.read_text(encoding="utf-8"))
    DESTINATION.write_text(render(report), encoding="utf-8")
    print(f"Wrote {DESTINATION.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
