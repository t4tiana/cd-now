"""Check lookback boundaries and customer-age to calendar mapping."""

import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from forecast_extensions import calendar_forecast, extensions


def test_six_window_training_starts_after_entry_window() -> None:
    """A common holdout must not let the entry purchase set the trend."""
    rates = [1000.0] + [6.0] * 6 + [3.0] * 6
    result = extensions(rates, origin=12, steps=2, lookback=6)
    assert result["earlier_block_mean"] == 6.0
    assert result["recent_block_mean"] == 3.0
    assert result["decline_factor_per_block"] == 0.5
    with pytest.raises(ValueError, match="Two post-entry"):
        extensions(rates, origin=11, steps=2, lookback=6)


def test_thirty_age_days_map_to_one_customer_period() -> None:
    """A $3 age-window amount contributes $3 across its 30 calendar days."""
    entry = date(1997, 1, 1)
    start = entry + timedelta(days=450)
    end = entry + timedelta(days=479)
    total, _ = calendar_forecast([3.0], Counter({entry: 1}), start, end)
    assert total == pytest.approx(3.0)
