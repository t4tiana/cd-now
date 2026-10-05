"""Check that the benchmark recovers a known geometric revenue profile."""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from trend_benchmark import log_linear_forecast


def test_log_linear_forecast_recovers_geometric_profile() -> None:
    rates = [100.0 * 0.9**age for age in range(15)]
    fitted = log_linear_forecast(rates, 14, 4)
    assert math.isclose(fitted["slope_per_30_days"], math.log(0.9), rel_tol=1e-10)
    for index, predicted in enumerate(fitted["profile"], start=15):
        assert math.isclose(predicted, rates[0] * 0.9**index, rel_tol=1e-10)
