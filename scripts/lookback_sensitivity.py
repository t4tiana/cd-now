"""Compare 2-, 3-, 4-, and 6-window age-revenue lookbacks fairly."""

import json
from datetime import date

from forecast_extensions import (
    COHORT_REPORT,
    CUSTOMERS,
    ROOT,
    calendar_forecast,
    extensions,
    first_date_counts,
)

OUTPUT = ROOT / "reports" / "lookback_sensitivity.json"
LENGTHS = (2, 3, 4, 6)
COMMON_ORIGIN = 12
HOLDOUT_STEPS = 2
FORECAST_ORIGIN = 14


def build_report() -> dict:
    """Score all lengths on ages 13–14, then project identical calendar periods."""
    observed = json.loads(COHORT_REPORT.read_text(encoding="utf-8"))
    periods = observed["customer_age_periods"]["periods"]
    if any(p["eligible_customers"] != CUSTOMERS for p in periods[:15]):
        raise ValueError("Common holdout needs complete cohort exposure")
    entry_dates = first_date_counts()
    manifest = json.loads((ROOT / "docs" / "source_manifest.json").read_text())
    if observed["source_manifest"] != manifest:
        raise ValueError("Phase 2 output does not match the source manifest")
    rates = [float(p["reported_dollars"]) / p["eligible_customers"] for p in periods]
    holdout_actual = sum(rates[COMMON_ORIGIN + 1 : COMMON_ORIGIN + 1 + HOLDOUT_STEPS])
    additional_backtests = []
    for origin, steps in ((8, 6), (11, 3)):
        actual = sum(rates[origin + 1 : origin + 1 + steps])
        predictions = []
        for lookback in LENGTHS:
            if origin < 2 * lookback:
                continue
            trial = extensions(rates, origin, steps, lookback)
            predictions.append(
                {
                    "lookback_30_day_windows": lookback,
                    "training_age_windows": f"{origin - 2 * lookback + 1}-{origin}",
                    "flat_forecast_reported_dollars": round(
                        sum(trial["flat"]) * CUSTOMERS, 2
                    ),
                    "flat_error_percent": round(
                        (sum(trial["flat"]) / actual - 1) * 100, 1
                    ),
                    "declining_forecast_reported_dollars": round(
                        sum(trial["declining"]) * CUSTOMERS, 2
                    ),
                    "declining_error_percent": round(
                        (sum(trial["declining"]) / actual - 1) * 100, 1
                    ),
                }
            )
        additional_backtests.append(
            {
                "held_out_age_windows": f"{origin + 1}-{origin + steps}",
                "fully_eligible_original_customers_in_each_window": CUSTOMERS,
                "actual_observed_reported_dollars": round(actual * CUSTOMERS, 2),
                "predictions": predictions,
            }
        )
    comparisons = []
    for lookback in LENGTHS:
        test = extensions(rates, COMMON_ORIGIN, HOLDOUT_STEPS, lookback)
        future = extensions(rates, FORECAST_ORIGIN, 28, lookback)
        backtest = {}
        scenarios = {}
        for name in ("flat", "declining"):
            predicted = sum(test[name])
            main, _ = calendar_forecast(
                future[name], entry_dates, date(1998, 7, 1), date(1999, 6, 30)
            )
            tail, _ = calendar_forecast(
                future[name], entry_dates, date(1999, 7, 1), date(2000, 6, 30)
            )
            backtest[name] = {
                "predicted_reported_dollars": round(predicted * CUSTOMERS, 2),
                "error_percent": round((predicted / holdout_actual - 1) * 100, 1),
                "absolute_error_percent": round(
                    abs(predicted / holdout_actual - 1) * 100, 1
                ),
            }
            scenarios[name] = {
                "main_july_1998_june_1999_forecast_reported_dollars": round(main, 2),
                "main_dollars_per_original_customer": round(main / CUSTOMERS, 2),
                "separate_july_1999_june_2000_tail_forecast_reported_dollars": round(
                    tail, 2
                ),
            }
        comparisons.append(
            {
                "lookback_30_day_windows": lookback,
                "backtest_training_age_windows": f"{COMMON_ORIGIN - 2 * lookback + 1}-{COMMON_ORIGIN}",
                "backtest_earlier_block_age_windows": f"{COMMON_ORIGIN - 2 * lookback + 1}-{COMMON_ORIGIN - lookback}",
                "backtest_recent_block_age_windows": f"{COMMON_ORIGIN - lookback + 1}-{COMMON_ORIGIN}",
                "backtest_decline_factor_per_block": round(
                    test["decline_factor_per_block"], 4
                ),
                "backtest_predictions": backtest,
                "forecast_earlier_block_age_windows": f"{FORECAST_ORIGIN - 2 * lookback + 1}-{FORECAST_ORIGIN - lookback}",
                "forecast_recent_block_age_windows": f"{FORECAST_ORIGIN - lookback + 1}-{FORECAST_ORIGIN}",
                "forecast_recent_dollars_per_customer_per_30_days": round(
                    future["recent_block_mean"], 4
                ),
                "forecast_decline_factor_per_block": round(
                    future["decline_factor_per_block"], 4
                ),
                "forecast_scenarios": scenarios,
            }
        )
    return {
        "status": "lookback sensitivity; three-window declining extension is the working scenario; other lookbacks remain sensitivities",
        "provisional_working_case": {
            "lookback_30_day_windows": 3,
            "extension": "declining",
            "not_final_base_case": True,
        },
        "historical_decision_date": "1998-07-15",
        "observed_cutoff": "1998-06-30",
        "source_manifest": manifest,
        "observed_reported_dollars_through_cutoff": observed["reconciliation"][
            "staged"
        ]["reported_dollars"],
        "common_backtest": {
            "held_out_age_windows": "13-14",
            "fully_eligible_original_customers_in_each_window": CUSTOMERS,
            "actual_observed_reported_dollars": round(holdout_actual * CUSTOMERS, 2),
            "limitation": "only two 30-day windows remain fully observable for all lookbacks without training on the entry window; one short holdout cannot establish a long-run rule",
        },
        "additional_backtests": additional_backtests,
        "method": "for each lookback L, compare mean dollars per fully eligible customer in the most recent L 30-day age windows with the preceding L windows; flat holds the recent mean, declining applies min(1, recent/prior) once per L windows with geometric interpolation; calendar mapping uses observed first-purchase dates and uniform daily spending within each forecast age window",
        "comparisons": comparisons,
        "repayment_eligible_revenue": None,
    }


def main() -> None:
    """Write reproducible sensitivity without selecting a lookback or case."""
    report = build_report()
    OUTPUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}; lookback cases recorded")


if __name__ == "__main__":
    main()
