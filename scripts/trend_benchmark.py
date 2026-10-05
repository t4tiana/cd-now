"""Compare a log-linear age-revenue trend with the provisional extension."""

import json
import math
from datetime import date

from forecast_extensions import (
    COHORT_REPORT,
    CUSTOMERS,
    ROOT,
    calendar_forecast,
    extensions,
    first_date_counts,
)

OUTPUT = ROOT / "reports" / "trend_benchmark.json"
TRAINING_START = 3  # Exclude the unusually high entry and early purchase windows.
FINAL_ORIGIN = 14  # Last window complete for all original customers.


def log_linear_forecast(
    rates: list[float], origin: int, steps: int, training_start: int = TRAINING_START
) -> dict:
    """Fit log(rate) = intercept + slope * age by ordinary least squares."""
    ages = list(range(training_start, origin + 1))
    if len(ages) < 3 or any(rates[age] <= 0 for age in ages):
        raise ValueError("At least three positive, fully observed training rates are needed")
    x_mean = sum(ages) / len(ages)
    logs = [math.log(rates[age]) for age in ages]
    y_mean = sum(logs) / len(logs)
    slope = sum((age - x_mean) * (value - y_mean) for age, value in zip(ages, logs)) / sum(
        (age - x_mean) ** 2 for age in ages
    )
    intercept = y_mean - slope * x_mean
    profile = [math.exp(intercept + slope * age) for age in range(origin + 1, origin + steps + 1)]
    return {"intercept": intercept, "slope_per_30_days": slope, "profile": profile}


def build_report() -> dict:
    """Score identical held-out windows and map both methods to calendar time."""
    observed = json.loads(COHORT_REPORT.read_text(encoding="utf-8"))
    periods = observed["customer_age_periods"]["periods"]
    if any(period["eligible_customers"] != CUSTOMERS for period in periods[:15]):
        raise ValueError("Age windows 0–14 must have complete cohort exposure")
    rates = [float(period["reported_dollars"]) / period["eligible_customers"] for period in periods[:15]]
    holdouts = []
    for origin, steps in ((8, 3), (8, 6), (11, 3), (12, 2)):
        actual = sum(rates[origin + 1 : origin + steps + 1]) * CUSTOMERS
        trend = log_linear_forecast(rates, origin, steps)
        provisional = extensions(rates, origin, steps, 3)["declining"]
        candidates = {}
        for label, profile in (("log_linear", trend["profile"]), ("three_window_decline", provisional)):
            predicted = sum(profile) * CUSTOMERS
            candidates[label] = {
                "forecast_reported_dollars": round(predicted, 2),
                "error_percent": round((predicted / actual - 1) * 100, 1),
                "absolute_error_percent": round(abs(predicted / actual - 1) * 100, 1),
            }
        holdouts.append({
            "training_age_windows": f"{TRAINING_START}-{origin} for log-linear; {origin-5}-{origin} for three-window",
            "held_out_age_windows": f"{origin + 1}-{origin + steps}",
            "actual_observed_reported_dollars": round(actual, 2),
            "log_linear_slope_per_30_days": round(trend["slope_per_30_days"], 6),
            "candidates": candidates,
        })
    entry_dates = first_date_counts()
    candidates = {}
    profiles = {
        "log_linear": log_linear_forecast(rates, FINAL_ORIGIN, 28)["profile"],
        "three_window_decline": extensions(rates, FINAL_ORIGIN, 28, 3)["declining"],
    }
    for label, profile in profiles.items():
        main, main_quarters = calendar_forecast(profile, entry_dates, date(1998, 7, 1), date(1999, 6, 30))
        tail, tail_quarters = calendar_forecast(profile, entry_dates, date(1999, 7, 1), date(2000, 6, 30))
        candidates[label] = {
            "main_july_1998_june_1999_reported_dollars": round(main, 2),
            "main_dollars_per_original_customer": round(main / CUSTOMERS, 2),
            "main_quarters": main_quarters,
            "separate_july_1999_june_2000_tail_reported_dollars": round(tail, 2),
            "tail_quarters": tail_quarters,
        }
    final_trend = log_linear_forecast(rates, FINAL_ORIGIN, 28)
    training_start_sensitivity = []
    for start in range(1, 7):
        alternative = log_linear_forecast(rates, FINAL_ORIGIN, 28, start)
        main, _ = calendar_forecast(
            alternative["profile"], entry_dates, date(1998, 7, 1), date(1999, 6, 30)
        )
        tail, _ = calendar_forecast(
            alternative["profile"], entry_dates, date(1999, 7, 1), date(2000, 6, 30)
        )
        training_start_sensitivity.append({
            "training_age_windows": f"{start}-14",
            "rate_ratio_per_30_days": round(math.exp(alternative["slope_per_30_days"]), 6),
            "main_july_1998_june_1999_reported_dollars": round(main, 2),
            "separate_july_1999_june_2000_tail_reported_dollars": round(tail, 2),
        })
    return {
        "status": "diagnostic only; neither method selected as final forecast",
        "historical_decision_date": "1998-07-15",
        "observed_cutoff": "1998-06-30",
        "observed_reported_dollars_through_cutoff": observed["reconciliation"]["staged"]["reported_dollars"],
        "source_manifest": observed["source_manifest"],
        "method": "ordinary least squares on log of reported dollars per original customer in each fully observed 30-day age window 3 through origin; extrapolate the fitted line and exponentiate. Age 0 contains first purchases; ages 1–2 are excluded to focus on repeat-era trend. The comparison uses the provisional three-window geometric decline on the same holdouts and calendar mapping.",
        "log_linear_final_slope_per_30_days": round(final_trend["slope_per_30_days"], 6),
        "log_linear_final_rate_ratio_per_30_days": round(math.exp(final_trend["slope_per_30_days"]), 6),
        "holdouts": holdouts,
        "training_start_sensitivity": training_start_sensitivity,
        "forecasts": candidates,
        "limitations": "The holdouts overlap and are much shorter than the decision horizon. Fifteen fully observed age windows from one cohort cannot identify seasonality, future acquisition mix, or a long-run decay law. These are reported transaction dollars, not eligible or collected revenue.",
    }


def main() -> None:
    """Write the reproducible benchmark without selecting a decision case."""
    OUTPUT.write_text(json.dumps(build_report(), indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
