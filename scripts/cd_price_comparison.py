"""Summarize reported transaction dollars per CD without calling them item prices."""

import json
from collections import defaultdict
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction
from pathlib import Path
from statistics import median

from source_manifest import measure_source

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "CDNOW_data" / "CDNOW_master.txt"
MANIFEST = ROOT / "docs" / "source_manifest.json"
REPORT = ROOT / "reports" / "cd_price_comparison.json"
CENT = Decimal("0.01")


def money(cents: int | Fraction) -> str:
    """Format exact cents or a fractional cent as dollars to two decimals."""
    amount = (
        Decimal(cents.numerator) / Decimal(cents.denominator)
        if isinstance(cents, Fraction)
        else Decimal(cents)
    )
    return str((amount / 100).quantize(CENT, rounding=ROUND_HALF_UP))


def summarize(rows: list[dict]) -> dict:
    """Give equal weight to each transaction row in the implied-dollar median."""
    if not rows:
        return {"rows": 0}
    ranked = sorted(
        rows, key=lambda row: (row["cents_per_cd"], row["source_line_number"])
    )
    amounts = [row["cents_per_cd"] for row in ranked]
    total_cents = sum(row["cents"] for row in rows)
    total_cds = sum(row["cd_count"] for row in rows)

    def example(row: dict) -> dict:
        return {
            "source_line_number": row["source_line_number"],
            "transaction_date": row["transaction_date"],
            "cd_count": row["cd_count"],
            "reported_dollars": money(row["cents"]),
            "implied_dollars_per_cd": money(row["cents_per_cd"]),
        }

    return {
        "rows": len(rows),
        "cds": total_cds,
        "reported_dollars": money(total_cents),
        "rows_below_5_dollars_per_cd": sum(amount < 500 for amount in amounts),
        "rows_above_50_dollars_per_cd": sum(amount > 5000 for amount in amounts),
        "rows_above_100_dollars_per_cd": sum(amount > 10000 for amount in amounts),
        "minimum_implied_dollars_per_cd": money(amounts[0]),
        "p25_implied_dollars_per_cd_nearest_rank": money(
            amounts[(len(amounts) - 1) // 4]
        ),
        "median_implied_dollars_per_cd": money(median(amounts)),
        "p75_implied_dollars_per_cd_nearest_rank": money(
            amounts[(3 * len(amounts) - 1) // 4]
        ),
        "maximum_implied_dollars_per_cd": money(amounts[-1]),
        "total_reported_dollars_divided_by_total_cds": money(
            Fraction(total_cents, total_cds)
        ),
        "minimum_example": example(ranked[0]),
        "maximum_example": example(ranked[-1]),
    }


def main() -> None:
    """Check source identity, calculate row-based summaries, and write JSON."""
    saved_manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if measure_source(SOURCE) != saved_manifest:
        raise ValueError("Source file differs from docs/source_manifest.json")

    rows = []
    with SOURCE.open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            customer, date_text, count_text, dollars_text = line.split()
            transaction_date = date.fromisoformat(
                f"{date_text[:4]}-{date_text[4:6]}-{date_text[6:]}"
            )
            count = int(count_text)
            cents = int((Decimal(dollars_text) * 100).to_integral_exact())
            if count <= 0 or cents < 0 or not customer:
                raise ValueError(f"Unexpected source values on line {line_number}")
            rows.append(
                {
                    "source_line_number": line_number,
                    "transaction_date": transaction_date.isoformat(),
                    "cd_count": count,
                    "cents": cents,
                    "cents_per_cd": Fraction(cents, count),
                }
            )

    if len(rows) != 69659 or sum(row["cents"] for row in rows) != 250031563:
        raise ValueError("Rows or dollars do not reconcile to phase 1")

    by_quarter = defaultdict(list)
    for row in rows:
        day = date.fromisoformat(row["transaction_date"])
        by_quarter[f"{day.year} Q{(day.month - 1) // 3 + 1}"].append(row)

    report = {
        "source_sha256": saved_manifest["sha256"],
        "definition": "transaction dollars / number of CDs on each source row; not a verified album price",
        "median_weighting": "one value per transaction row, regardless of CD count",
        "all_rows": summarize(rows),
        "positive_dollar_rows": summarize([row for row in rows if row["cents"] > 0]),
        "one_cd_rows": summarize([row for row in rows if row["cd_count"] == 1]),
        "positive_one_cd_rows": summarize(
            [row for row in rows if row["cd_count"] == 1 and row["cents"] > 0]
        ),
        "june_1998_positive_one_cd_rows": summarize(
            [
                row
                for row in rows
                if row["transaction_date"].startswith("1998-06")
                and row["cd_count"] == 1
                and row["cents"] > 0
            ]
        ),
        "positive_one_cd_by_quarter": {
            quarter: summarize(
                [
                    row
                    for row in quarter_rows
                    if row["cd_count"] == 1 and row["cents"] > 0
                ]
            )
            for quarter, quarter_rows in sorted(by_quarter.items())
        },
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
