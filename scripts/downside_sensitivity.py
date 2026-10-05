"""Illustrative downside grid for the observed cohort's remaining dollars."""

import json
from decimal import Decimal
from pathlib import Path

import duckdb
from early90_diagnostic import (
    COHORT_REPORT,
    CUSTOMERS,
    DATABASE,
    MANIFEST,
    SOURCE,
    customer_records,
)
from source_manifest import measure_source

ROOT = Path(__file__).resolve().parent.parent
FORECAST = ROOT / "reports" / "forecast_extensions.json"
OUTPUT = ROOT / "reports" / "downside_sensitivity.json"
STRESS_LEVELS = (Decimal("0.10"), Decimal("0.20"), Decimal("0.30"))


def money(value: Decimal) -> str:
    """Round an illustrative dollar result to cents."""
    return str(value.quantize(Decimal("0.01")))


def stressed_periods(base: dict, factor: Decimal) -> dict:
    """Apply one constant factor to both forecast periods and each quarter."""
    result = {}
    for period, data in base.items():
        result[period] = {
            "forecast_reported_dollars": money(
                Decimal(str(data["forecast_reported_dollars"])) * factor
            ),
            "quarters": [
                {
                    "calendar_quarter": row["calendar_quarter"],
                    "forecast_reported_dollars": money(
                        Decimal(str(row["forecast_reported_dollars"])) * factor
                    ),
                }
                for row in data["quarters"]
            ],
        }
    return result


def build_report(records: list[tuple], forecast: dict, cohort: dict) -> dict:
    """Vary early-repeat prevalence and high-spender contribution separately."""
    if len(records) != CUSTOMERS or len({row[0] for row in records}) != CUSTOMERS:
        raise ValueError("Expected one record per original customer")
    anchor_total = sum((row[6] for row in records), Decimal("0.00"))
    expected = sum(
        Decimal(p["reported_dollars"])
        for p in cohort["customer_age_periods"]["periods"][9:15]
    )
    if anchor_total != expected or anchor_total <= 0:
        raise ValueError("Anchor dollars do not reconcile to complete age windows")
    base = forecast["scenarios"]["declining"]
    repeaters = [row for row in records if row[2] > 0]
    nonrepeaters = [row for row in records if row[2] == 0]
    p = Decimal(len(repeaters)) / CUSTOMERS
    rate_r = sum((row[6] for row in repeaters), Decimal("0.00")) / len(repeaters)
    rate_n = sum((row[6] for row in nonrepeaters), Decimal("0.00")) / len(nonrepeaters)
    baseline_rate = p * rate_r + (1 - p) * rate_n

    cases = []
    for stress in STRESS_LEVELS:
        new_p = p * (1 - stress)
        factor = (new_p * rate_r + (1 - new_p) * rate_n) / baseline_rate
        cases.append({
            "driver": "early_repeat_prevalence",
            "assumed_relative_reduction": str(stress),
            "implied_repeat_share_of_original_cohort_percent": round(float(new_p * 100), 1),
            "forecast_factor": round(float(factor), 6),
            "periods": stressed_periods(base, factor),
        })

    # Fixed group sizes make the top 25% and top 10% reproducible even at ties.
    ranked = sorted(records, key=lambda row: (-row[1], row[0]))
    groups = {}
    for label, count in (("top_25_percent", CUSTOMERS // 4), ("top_10_percent", CUSTOMERS // 10)):
        selected = ranked[:count]
        group_anchor = sum((row[6] for row in selected), Decimal("0.00"))
        share = group_anchor / anchor_total
        groups[label] = {
            "customers": count,
            "rank_rule": "first-90-day reported dollars descending; customer ID ascending breaks ties",
            "observed_anchor_days_270_449_dollars": money(group_anchor),
            "share_of_all_anchor_dollars_percent": round(float(share * 100), 1),
            "lowest_included_first_90_day_dollars": money(selected[-1][1]),
        }
        for stress in STRESS_LEVELS:
            factor = 1 - share * stress
            cases.append({
                "driver": label + "_future_contribution",
                "assumed_reduction_to_group_forecast": str(stress),
                "forecast_factor": round(float(factor), 6),
                "periods": stressed_periods(base, factor),
            })

    return {
        "status": "illustrative grid; 20% early-repeat and early-top-quarter cases used separately as decision gates",
        "historical_decision_date": "1998-07-15",
        "observed_cutoff": "1998-06-30",
        "source_manifest": forecast["source_manifest"],
        "population": "Q1 1997 first-purchase cohort; 23,570 customer IDs",
        "forecast_object": "remaining reported transaction dollars for this observed cohort",
        "baseline": "provisional three-window declining extension",
        "baseline_periods": base,
        "anchor": {
            "customer_age_days": "270-449; fully observed for all original customers",
            "observed_reported_dollars": money(anchor_total),
            "early_repeat_customers": len(repeaters),
            "early_repeat_share_percent": round(float(p * 100), 1),
            "repeat_group_anchor_dollars_per_customer": money(rate_r),
            "no_repeat_group_anchor_dollars_per_customer": money(rate_n),
            "high_spender_groups": groups,
        },
        "method": "Each stress changes one anchor component, then multiplies every provisional forecast quarter by the same resulting factor. The early-repeat case transfers removed customers to the no-early-repeat group and holds each group's observed anchor rate fixed. The high-spender cases reduce only that group's forecast contribution. Other assumptions and timing shape are held fixed.",
        "limits": "Groups use days 0-89 information unavailable at initial funding. Anchor group shares may change at older customer ages. Constant factors do not test a change in forecast decay or calendar timing. Cases are separate, not additive, and are not probabilities, floors, eligible repayment revenue, or cash receipts.",
        "cases": cases,
        "repayment_eligible_revenue": None,
    }


def main() -> None:
    """Check report provenance and write reproducible sensitivities."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if measure_source(SOURCE) != manifest:
        raise ValueError("Source differs from recorded manifest")
    forecast = json.loads(FORECAST.read_text(encoding="utf-8"))
    cohort = json.loads(COHORT_REPORT.read_text(encoding="utf-8"))
    if forecast["source_manifest"] != manifest or cohort["source_manifest"] != manifest:
        raise ValueError("Inputs do not match the source")
    with duckdb.connect(str(DATABASE), read_only=True) as connection:
        report = build_report(customer_records(connection), forecast, cohort)
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}; decision-gate cases recorded")


if __name__ == "__main__":
    main()
