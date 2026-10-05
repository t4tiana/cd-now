"""Compare two age-revenue extensions without selecting a forecast base case."""

import json
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

from source_manifest import measure_source

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "CDNOW_data" / "CDNOW_master.txt"
MANIFEST = ROOT / "docs" / "source_manifest.json"
COHORT_REPORT = ROOT / "reports" / "cohort_analysis.json"
OUTPUT = ROOT / "reports" / "forecast_extensions.json"
CUTOFF = date(1998, 6, 30)
CUSTOMERS = 23570


def extensions(rates: list[float], origin: int, steps: int, lookback: int = 3) -> dict:
    """Extend a recent age-rate mean flat or at its preceding-block trend."""
    if lookback < 1 or origin < 2 * lookback or len(rates) <= origin:
        raise ValueError("Two post-entry training blocks are required")
    earlier = sum(rates[origin - 2 * lookback + 1 : origin - lookback + 1]) / lookback
    recent = sum(rates[origin - lookback + 1 : origin + 1]) / lookback
    ratio = min(1.0, recent / earlier)
    return {
        "earlier_block_mean": earlier,
        "recent_block_mean": recent,
        "decline_factor_per_block": ratio,
        "flat": [recent] * steps,
        "declining": [
            recent * ratio ** ((step + 1) / lookback) for step in range(steps)
        ],
    }


def first_date_counts() -> Counter[date]:
    """Read cohort entry dates only, checking the tracked source and population."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if measure_source(SOURCE) != manifest:
        raise ValueError("Source differs from the recorded manifest")
    first: dict[int, date] = {}
    for line in SOURCE.read_text(encoding="utf-8").splitlines():
        customer, yyyymmdd, _, _ = line.split()
        day = date.fromisoformat(f"{yyyymmdd[:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:]}")
        key = int(customer)
        if key not in first or day < first[key]:
            first[key] = day
    if len(first) != CUSTOMERS or any(
        not date(1997, 1, 1) <= day <= date(1997, 3, 31) for day in first.values()
    ):
        raise ValueError("Entry dates do not match the defined cohort")
    return Counter(first.values())


def calendar_forecast(
    profile: list[float], entry_dates: Counter[date], start: date, end: date
) -> tuple[float, list[dict]]:
    """Spread each 30-day customer-age amount uniformly over its calendar days."""
    quarters: dict[str, float] = {}
    day = start
    while day <= end:
        amount = 0.0
        for entry, count in entry_dates.items():
            age = (day - entry).days // 30
            if age < 15 or age >= 15 + len(profile):
                raise ValueError("Forecast profile does not cover the calendar day")
            amount += count * profile[age - 15] / 30
        quarter = f"{day.year}Q{(day.month - 1) // 3 + 1}"
        quarters[quarter] = quarters.get(quarter, 0.0) + amount
        day += timedelta(days=1)
    return sum(quarters.values()), [
        {"calendar_quarter": quarter, "forecast_reported_dollars": round(value, 2)}
        for quarter, value in quarters.items()
    ]


def build_report() -> dict:
    """Backtest complete windows, then calculate unselected calendar scenarios."""
    observed = json.loads(COHORT_REPORT.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if observed["source_manifest"] != manifest:
        raise ValueError("Phase 2 output does not match the source manifest")
    if observed["reconciliation"]["staged"]["distinct_customers"] != CUSTOMERS:
        raise ValueError("Unexpected cohort size")
    periods = observed["customer_age_periods"]["periods"]
    rates = [float(p["reported_dollars"]) / p["eligible_customers"] for p in periods]
    if any(p["eligible_customers"] != CUSTOMERS for p in periods[:15]):
        raise ValueError("Backtest windows do not have full-cohort exposure")
    backtests = []
    for origin, steps in ((8, 3), (8, 6), (11, 3)):
        model = extensions(rates, origin, steps)
        actual = sum(rates[origin + 1 : origin + steps + 1])
        forecasts = {
            name: {
                "dollars_per_original_customer": round(sum(model[name]), 2),
                "cohort_dollars": round(sum(model[name]) * CUSTOMERS, 2),
                "error_percent": round((sum(model[name]) / actual - 1) * 100, 1),
            }
            for name in ("flat", "declining")
        }
        backtests.append(
            {
                "training_age_windows": f"{origin - 5}-{origin}",
                "held_out_age_windows": f"{origin + 1}-{origin + steps}",
                "held_out_eligible_customers_each_window": CUSTOMERS,
                "decline_factor_per_three_windows": round(
                    model["decline_factor_per_block"], 4
                ),
                "actual_observed_dollars_per_customer": round(actual, 2),
                "actual_observed_cohort_dollars": round(actual * CUSTOMERS, 2),
                "predictions": forecasts,
            }
        )
    entry_dates = first_date_counts()
    model = extensions(rates, 14, 28)
    scenarios = {}
    for name in ("flat", "declining"):
        main, quarters = calendar_forecast(
            model[name], entry_dates, date(1998, 7, 1), date(1999, 6, 30)
        )
        tail, tail_quarters = calendar_forecast(
            model[name], entry_dates, date(1999, 7, 1), date(2000, 6, 30)
        )
        scenarios[name] = {
            "main_july_1998_june_1999": {
                "forecast_reported_dollars": round(main, 2),
                "forecast_dollars_per_original_customer": round(main / CUSTOMERS, 2),
                "quarters": quarters,
            },
            "separate_tail_july_1999_june_2000": {
                "forecast_reported_dollars": round(tail, 2),
                "forecast_dollars_per_original_customer": round(tail / CUSTOMERS, 2),
                "quarters": tail_quarters,
            },
        }
    return {
        "status": "three-window declining extension is the selected working case; compare with the documented downside and trend sensitivities",
        "provisional_working_case": {
            "lookback_30_day_windows": 3,
            "extension": "declining",
            "scope": "observed Q1 1997 cohort remaining reported-dollar forecast only",
            "not_final_base_case": True,
        },
        "historical_decision_date": "1998-07-15",
        "observed_cutoff": CUTOFF.isoformat(),
        "cohort": "Q1 1997 first recorded purchase; 23,570 customer IDs",
        "observed_reported_dollars_through_cutoff": observed["reconciliation"][
            "staged"
        ]["reported_dollars"],
        "source_manifest": manifest,
        "method": {
            "rate": "reported dollars divided by fully eligible customers in each 30-day age window; age zero includes entry and is not used to fit the extension",
            "flat": "hold the mean of the latest three complete age-window rates",
            "declining": "multiply that mean by min(1, latest three-window mean / prior three-window mean) once per three 30-day windows, interpolated geometrically by window",
            "calendar_mapping": "spread each forecast 30-day age-window rate uniformly across its 30 days and weight by observed Q1 1997 first-purchase dates",
            "anchor": "age windows 9-14 only; all 23,570 customers have complete exposure through age window 14; later observed windows with shrinking denominators do not set the extension",
        },
        "backtests": backtests,
        "anchor": {
            "earlier_age_windows": "9-11",
            "recent_age_windows": "12-14",
            "earlier_dollars_per_customer_per_30_days": round(
                model["earlier_block_mean"], 4
            ),
            "recent_dollars_per_customer_per_30_days": round(
                model["recent_block_mean"], 4
            ),
            "decline_factor_per_three_windows": round(
                model["decline_factor_per_block"], 4
            ),
        },
        "scenarios": scenarios,
        "repayment_eligible_revenue": None,
        "repayment_eligibility_note": "not established by the transaction file; neither scenario is a repayment forecast",
    }


def main() -> None:
    """Write exploratory results without choosing a base case."""
    report = build_report()
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}; provisional case recorded")


if __name__ == "__main__":
    main()
