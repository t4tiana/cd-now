"""Illustrate future-cohort revenue and capped investor repayments.

This is a scale example, not a claim about Q4 1998 acquisitions or cash receipts.
"""

import json
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from forecast_extensions import CUSTOMERS, SOURCE, extensions
from source_manifest import measure_source

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "docs" / "source_manifest.json"
COHORT = ROOT / "reports" / "cohort_analysis.json"
DOWNSIDE = ROOT / "reports" / "downside_sensitivity.json"
OUTPUT = ROOT / "reports" / "financing_scenarios.json"
ENTRY_START = date(1998, 10, 1)
ENTRY_END = date(1998, 12, 31)
END = date(2000, 12, 31)
SCALE_CUSTOMERS = 23570
ADVANCES = (250000, 500000, 1000000, 1500000)


def source_age_profile() -> list[float]:
    """Calculate dollars by exact day since first transaction, per original ID."""
    if measure_source(SOURCE) != json.loads(MANIFEST.read_text(encoding="utf-8")):
        raise ValueError("Supplied source changed")
    transactions = []
    first = {}
    for line in SOURCE.read_text(encoding="utf-8").splitlines():
        customer, raw_date, _, raw_dollars = line.split()
        day = date.fromisoformat(f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}")
        transactions.append((customer, day, int(Decimal(raw_dollars) * 100)))
        first[customer] = min(day, first.get(customer, day))
    if len(first) != CUSTOMERS:
        raise ValueError("Unexpected source population")
    cents = [0] * 450
    for customer, day, amount in transactions:
        age = (day - first[customer]).days
        if age < 450:
            cents[age] += amount
    return [amount / 100 / CUSTOMERS for amount in cents]


def full_age_profile(lookback: int = 3) -> list[float]:
    """Join fully observed daily ages with a selected declining tail rule."""
    observed = json.loads(COHORT.read_text(encoding="utf-8"))
    if observed["source_manifest"] != json.loads(MANIFEST.read_text(encoding="utf-8")):
        raise ValueError("Phase 2 output does not match source")
    profile = source_age_profile()
    periods = observed["customer_age_periods"]["periods"]
    for window in range(15):
        expected = float(periods[window]["reported_dollars"]) / CUSTOMERS
        actual = sum(profile[window * 30 : (window + 1) * 30])
        if abs(expected - actual) > 0.000001:
            raise ValueError(f"Age window {window} failed reconciliation")
    rates = [float(p["reported_dollars"]) / p["eligible_customers"] for p in periods]
    future = extensions(rates, 14, 14, lookback)["declining"]
    for thirty_day_dollars in future:
        profile.extend([thirty_day_dollars / 30] * 30)
    return profile


def model_scenario(
    profile: list[float], factor: float, eligible_fraction: float,
    cohort_customers: int = SCALE_CUSTOMERS,
    advances: tuple[int, ...] = ADVANCES,
    initial_factor: float = 1.0,
) -> dict:
    """Apply separate early and later spending factors before capped repayments."""
    entry_days = (ENTRY_END - ENTRY_START).days + 1
    amounts = defaultdict(float)
    day = ENTRY_START
    while day <= END:
        for entry_offset in range(entry_days):
            entry = ENTRY_START + timedelta(days=entry_offset)
            age = (day - entry).days
            if 0 <= age < len(profile):
                amounts[day] += (
                    cohort_customers
                    / entry_days
                    * profile[age]
                    * (factor if age >= 90 else initial_factor)
                )
        day += timedelta(days=1)
    quarter_revenue = defaultdict(float)
    for when, amount in amounts.items():
        quarter_revenue[f"{when.year}Q{(when.month - 1) // 3 + 1}"] += amount
    investments = []
    for advance in advances:
        cap = 1.2 * advance
        cumulative = 0.0
        cap_day = None
        repayment_quarters = defaultdict(float)
        for when in sorted(amounts):
            payment = min(cap - cumulative, amounts[when] * eligible_fraction * 0.5)
            if payment <= 0:
                continue
            cumulative += payment
            repayment_quarters[f"{when.year}Q{(when.month - 1) // 3 + 1}"] += payment
            if cap_day is None and cumulative >= cap - 0.000001:
                cap_day = when.isoformat()
        if cumulative > cap + 0.000001 or (
            cap_day and abs(cumulative - cap) > 0.000001
        ):
            raise ValueError("Repayment cap reconciliation failed")
        investments.append(
            {
                "advance": advance,
                "eligible_revenue_needed_to_cap": round(2.4 * advance, 2),
                "capped_repayments_through_2000": round(cumulative, 2),
                "unrepaid_principal_at_end": round(max(0, advance - cumulative), 2),
                "cap_date": cap_day,
                "repayment_by_quarter": {
                    quarter: round(repayment_quarters[quarter], 2)
                    for quarter in sorted(quarter_revenue)
                },
            }
        )
    return {
        "reported_dollars_through_2000": round(sum(amounts.values()), 2),
        "eligible_dollars_through_2000": round(
            sum(amounts.values()) * eligible_fraction, 2
        ),
        "forecast_reported_dollars_by_quarter": {
            quarter: round(quarter_revenue[quarter], 2)
            for quarter in sorted(quarter_revenue)
        },
        "illustrative_advances": investments,
    }


def build_report() -> dict:
    """Keep each unselected downside distinct and expose eligibility sensitivity."""
    profile = full_age_profile()
    downside = json.loads(DOWNSIDE.read_text(encoding="utf-8"))
    cases = {
        "provisional_base": 1.0,
        "early_repeat_20pct": next(
            c["forecast_factor"]
            for c in downside["cases"]
            if c["driver"] == "early_repeat_prevalence"
            and c["assumed_relative_reduction"] == "0.20"
        ),
        "top_25_spend_20pct": next(
            c["forecast_factor"]
            for c in downside["cases"]
            if c["driver"] == "top_25_percent_future_contribution"
            and c["assumed_reduction_to_group_forecast"] == "0.20"
        ),
    }
    report = {
        "status": "illustrative; downside and advance not selected",
        "decision_date": "1998-07-15",
        "source_manifest": json.loads(MANIFEST.read_text(encoding="utf-8")),
        "example_cohort": "Q4 1998 first-purchase IDs; hypothetical same 23,570-person scale as Q1 1997",
        "entry_assumption": "first purchases evenly distributed across October 1–December 31, 1998",
        "revenue_assumption": "Q1 1997 observed per-original-customer daily age profile through day 449; three-window declining extension thereafter; no explicit seasonality, mix or price change",
        "stress_assumption": "P3.4 anchor factor scales all age-90-and-later daily dollars; first 90 days stay at Q1 1997 levels. This future-cohort translation is illustrative and may understate downside to early dollars.",
        "repayment_assumption": "each calendar day's eligible, collected revenue equals the selected fraction of reported dollars and remits 50% immediately; cumulative repayment stops at 1.2 times advance",
        "forecast_end": END.isoformat(),
        "unmodeled_after_end_is_not_zero": True,
        "scenarios": {},
    }
    for label, factor in cases.items():
        report["scenarios"][label] = {
            "factor_from_p3_4": factor,
            "all_reported_dollars_eligible": model_scenario(profile, factor, 1.0),
            "80_percent_reported_dollars_eligible": model_scenario(
                profile, factor, 0.8
            ),
        }
    faster_profile = full_age_profile(2)
    report["scenarios"]["two_window_decay"] = {
        "factor_from_p3_4": None,
        "all_reported_dollars_eligible": model_scenario(faster_profile, 1.0, 1.0),
        "80_percent_reported_dollars_eligible": model_scenario(
            faster_profile, 1.0, 0.8
        ),
    }
    for scenario in report["scenarios"].values():
        full = scenario["all_reported_dollars_eligible"]["illustrative_advances"]
        reduced = scenario["80_percent_reported_dollars_eligible"][
            "illustrative_advances"
        ]
        for full_row, reduced_row in zip(full, reduced, strict=True):
            if (
                reduced_row["capped_repayments_through_2000"]
                > full_row["capped_repayments_through_2000"]
            ):
                raise ValueError("Lower eligibility produced more repayment")
    return report


if __name__ == "__main__":
    OUTPUT.write_text(json.dumps(build_report(), indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
