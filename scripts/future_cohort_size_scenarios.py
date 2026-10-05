"""Scale the Q4 1998 first-purchaser illustration without changing behavior."""

import json
from pathlib import Path

from financing_scenarios import (
    DOWNSIDE,
    END,
    ROOT,
    full_age_profile,
    model_scenario,
)

OUTPUT = ROOT / "reports" / "future_cohort_size_scenarios.json"
SIZES = (40000, 62000, 90000)
ILLUSTRATIVE_ADVANCE_PER_PURCHASER = 50
PROPOSED_CEILING = 1_200_000


def build_report() -> dict:
    """Keep purchaser count, repeat behavior, and eligibility independent."""
    downside = json.loads(Path(DOWNSIDE).read_text(encoding="utf-8"))
    cases = {
        "provisional": 1.0,
        "early_repeat_20pct": next(
            c["forecast_factor"] for c in downside["cases"]
            if c["driver"] == "early_repeat_prevalence"
            and c["assumed_relative_reduction"] == "0.20"
        ),
        "top_25_spend_20pct": next(
            c["forecast_factor"] for c in downside["cases"]
            if c["driver"] == "top_25_percent_future_contribution"
            and c["assumed_reduction_to_group_forecast"] == "0.20"
        ),
    }
    profile = full_age_profile()
    rows = []
    proposed_ceiling_rows = []
    for size in SIZES:
        illustrative_advance = size * ILLUSTRATIVE_ADVANCE_PER_PURCHASER
        for name, factor in cases.items():
            for eligible_fraction in (1.0, 0.8):
                result = model_scenario(
                    profile, factor, eligible_fraction,
                    cohort_customers=size,
                    advances=(illustrative_advance,),
                )
                investment = result["illustrative_advances"][0]
                rows.append({
                    "first_purchasers": size,
                    "illustrative_advance": illustrative_advance,
                    "behavior_case": name,
                    "eligible_collected_fraction_assumed": eligible_fraction,
                    "forecast_reported_dollars_q4_1998": result["forecast_reported_dollars_by_quarter"]["1998Q4"],
                    "forecast_reported_dollars_h1_1999": round(
                        result["forecast_reported_dollars_by_quarter"]["1999Q1"]
                        + result["forecast_reported_dollars_by_quarter"]["1999Q2"], 2
                    ),
                    "forecast_reported_dollars_through_2000": result["reported_dollars_through_2000"],
                    "assumed_eligible_collected_dollars_through_2000": result["eligible_dollars_through_2000"],
                    "repayments_on_illustrative_advance_through_2000": investment["capped_repayments_through_2000"],
                    "cap_date_if_reached": investment["cap_date"],
                    "minimum_eligible_collected_fraction_to_cap_by_end": round(
                        2.4 * illustrative_advance / result["reported_dollars_through_2000"], 4
                    ),
                })
            ceiling_result = model_scenario(
                profile, factor, 0.8,
                cohort_customers=size,
                advances=(PROPOSED_CEILING,),
            )
            ceiling_investment = ceiling_result["illustrative_advances"][0]
            proposed_ceiling_rows.append({
                "first_purchasers": size,
                "behavior_case": name,
                "eligible_collected_fraction_assumed": 0.8,
                "proposed_ceiling": PROPOSED_CEILING,
                "forecast_reported_dollars_through_2000": ceiling_result["reported_dollars_through_2000"],
                "assumed_eligible_collected_dollars_through_2000": ceiling_result["eligible_dollars_through_2000"],
                "repayments_through_2000": ceiling_investment["capped_repayments_through_2000"],
                "cap_date_if_reached": ceiling_investment["cap_date"],
            })
    joint_result = model_scenario(
        profile,
        cases["top_25_spend_20pct"],
        0.6,
        cohort_customers=30000,
        advances=(PROPOSED_CEILING,),
        initial_factor=0.85,
    )
    joint_investment = joint_result["illustrative_advances"][0]
    return {
        "decision_date": "1998-07-15",
        "future_cohort": "Q4 1998 first purchasers, evenly entering October 1 through December 31",
        "forecast_end": END.isoformat(),
        "observed_q1_1997_transaction_dollars": 2500315.63,
        "illustrative_advance_per_purchaser_not_selected": ILLUSTRATIVE_ADVANCE_PER_PURCHASER,
        "repayment_share": 0.5,
        "cap_multiple": 1.2,
        "size_scenarios": list(SIZES),
        "rows": rows,
        "proposed_ceiling_rows": proposed_ceiling_rows,
        "joint_downside": {
            "first_purchasers": 30000,
            "first_90_day_dollars_factor_assumed": 0.85,
            "age_90_and_later_dollars_factor_from_top_25_stress": cases["top_25_spend_20pct"],
            "eligible_collected_fraction_assumed": 0.6,
            "advance": PROPOSED_CEILING,
            "forecast_reported_dollars_q4_1998": joint_result["forecast_reported_dollars_by_quarter"]["1998Q4"],
            "forecast_reported_dollars_through_2000": joint_result["reported_dollars_through_2000"],
            "assumed_eligible_collected_dollars_through_2000": joint_result["eligible_dollars_through_2000"],
            "repayments_through_2000": joint_investment["capped_repayments_through_2000"],
            "unrepaid_principal_at_end": joint_investment["unrepaid_principal_at_end"],
            "cap_date_if_reached": joint_investment["cap_date"],
        },
    }


if __name__ == "__main__":
    OUTPUT.write_text(json.dumps(build_report(), indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")
