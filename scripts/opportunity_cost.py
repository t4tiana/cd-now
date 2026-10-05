"""Compare one Q4 cohort illustration with a pre-cutoff Treasury yield proxy."""

import json
from datetime import timedelta

from financing_scenarios import (
    END,
    ENTRY_END,
    ENTRY_START,
    ROOT,
    full_age_profile,
    model_scenario,
)

OUTPUT = ROOT / "reports" / "opportunity_cost.json"
RATE = 0.0534  # 1-year Treasury constant-maturity weekly average, H.15 July 13, 1998
ADVANCE = 1_200_000
CUSTOMERS = 40_000
ELIGIBLE_FRACTION = 0.8  # illustration, not evidence of eligibility
FACTOR = 0.873537  # top-quarter later-spend downside, P3.4


def build_report() -> dict:
    """Use the original daily age profile and the same-day collection assumption."""
    profile = full_age_profile()
    entry_days = (ENTRY_END - ENTRY_START).days + 1
    payments = []
    reported = 0.0
    eligible = 0.0
    paid = 0.0
    cap = 1.2 * ADVANCE
    cap_date = None
    when = ENTRY_START
    while when <= END:
        amount = 0.0
        for offset in range(entry_days):
            entry = ENTRY_START + timedelta(days=offset)
            age = (when - entry).days
            if 0 <= age < len(profile):
                amount += CUSTOMERS / entry_days * profile[age] * (
                    FACTOR if age >= 90 else 1.0
                )
        reported += amount
        eligible += amount * ELIGIBLE_FRACTION
        payment = min(max(0.0, cap - paid), amount * ELIGIBLE_FRACTION * 0.5)
        if payment > 0:
            payments.append((when, payment))
            paid += payment
            if cap_date is None and paid >= cap - 0.000001:
                cap_date = when
        when += timedelta(days=1)
    if cap_date is None:
        raise ValueError("Illustration did not reach its modeled cap")
    horizon_days = (cap_date - ENTRY_START).days
    treasury_end = ADVANCE * (1 + RATE) ** (horizon_days / 365)
    reinvested_payments = sum(
        amount * (1 + RATE) ** ((cap_date - day).days / 365)
        for day, amount in payments
        if day <= cap_date
    )
    same_size_downside = model_scenario(
        profile, FACTOR, ELIGIBLE_FRACTION,
        cohort_customers=23570,
        advances=(ADVANCE,),
    )["illustrative_advances"][0]
    doubled_advance_cases = {}
    for customers in (40000, 62000, 80000):
        scenario = model_scenario(
            profile, FACTOR, ELIGIBLE_FRACTION,
            cohort_customers=customers,
            advances=(2 * ADVANCE,),
        )
        doubled_advance_cases[str(customers)] = {
            "forecast_reported_dollars_through_2000": scenario[
                "reported_dollars_through_2000"
            ],
            "assumed_eligible_collected_dollars_through_2000": scenario[
                "eligible_dollars_through_2000"
            ],
            "repayments_through_2000": scenario["illustrative_advances"][0][
                "capped_repayments_through_2000"
            ],
            "cap_date": scenario["illustrative_advances"][0]["cap_date"],
        }
    return {
        "decision_date": "1998-07-15",
        "comparison_start": ENTRY_START.isoformat(),
        "comparison_end": cap_date.isoformat(),
        "days": horizon_days,
        "advance": ADVANCE,
        "cohort_assumptions": {
            "first_purchasers": CUSTOMERS,
            "behavior_case": "top_25_spend_20pct",
            "eligible_collected_fraction": ELIGIBLE_FRACTION,
            "same_day_remittance": True,
            "payment_share": 0.5,
            "cap_multiple": 1.2,
        },
        "cohort_reported_dollars_through_2000": round(reported, 2),
        "assumed_eligible_collected_dollars_through_2000": round(eligible, 2),
        "capped_cohort_repayments_by_comparison_end": round(paid, 2),
        "cohort_gross_gain_without_reinvestment": round(paid - ADVANCE, 2),
        "treasury_proxy_annual_rate": RATE,
        "treasury_terminal_value_flat_rate_assumption": round(treasury_end, 2),
        "treasury_gain_flat_rate_assumption": round(treasury_end - ADVANCE, 2),
        "cohort_repayments_reinvested_at_same_rate": round(reinvested_payments, 2),
        "cohort_terminal_gain_with_reinvestment": round(reinvested_payments - ADVANCE, 2),
        "cohort_excess_terminal_value_over_treasury": round(
            reinvested_payments - treasury_end, 2
        ),
        "successful_collection_probability_needed_if_otherwise_total_loss": round(
            treasury_end / reinvested_payments, 4
        ),
        "same_23570_size_repayments_through_2000": same_size_downside[
            "capped_repayments_through_2000"
        ],
        "doubled_advance_2400000_cases": doubled_advance_cases,
        "rate_source": "Federal Reserve H.15 release July 13, 1998; 1-year Treasury constant-maturity weekly average for July 6–10, 1998",
        "rate_is_quoted_yield_not_a_guaranteed_15_month_investment": True,
    }


if __name__ == "__main__":
    OUTPUT.write_text(json.dumps(build_report(), indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
