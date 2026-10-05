# P3.2: exploratory 30-day revenue extensions

**Decision date:** July 15, 1998. **Observed cutoff:** June 30, 1998.
This compares extensions for the observed Q1 1997 first-purchase cohort of
23,570 customer IDs. I selected the **three-window declining
extension as a working case** after reviewing the forecast
diagnostics and use it in the scenario analysis. The source records
**$2,500,315.63 observed transaction dollars** through the cutoff. Every future
amount below is a **forecast of reported transaction dollars**, not observed
revenue, cash collected, economic contribution, or repayment-eligible revenue.
The actual repayment base remains unknown.

## How many age windows are in the file?

The earliest customer first bought on January 1, 1997. From that date through
June 30, 1998, the file spans 546 calendar days, enough to *touch* 19 numbered
30-day customer-age windows (0–18), but not enough to finish window 18 for
anyone. A later Q1 entrant reaches each age window later on the calendar.

| Customer-age windows | Days after each first purchase | Customers with all 30 days observable | Use here |
| --- | --- | ---: | --- |
| 0–2 | 0–89 | 23,570 in each | Observed total; excluded from extension fitting because window 0 contains the first purchase and early spending is much higher. |
| 3–8 | 90–269 | 23,570 in each | Earlier training windows in the backtests. |
| 9–11 | 270–359 | 23,570 in each | Backtest holdout; also the preceding three-window mean for the final extension. |
| 12–14 | 360–449 | 23,570 in each | Backtest holdout and the latest three-window mean for the final extension. |
| 15, 16, 17 | 450–539 | 18,841; 9,758; 1,574, respectively | Descriptive observed rates for those fully observable subsets; not used to fit or score the extensions. |
| 18 | 540–569 | 0 | Only a partial window is visible; no comparable full-window rate. |

Thus **windows 0–14 are complete for every original customer**. The
backtests use windows 3–14, while the proposed extension is fitted to 9–14.
No transaction dollars are removed from the $2,500,315.63 observed total:
transactions from partly visible windows are still counted there. Only the
*like-aged averages* omit incomplete customer-windows. The [phase 2 output](cohort_analysis.json)
records the eligible counts and the full-versus-partial dollar reconciliation.

## Method and check against observed windows

For each 30-day customer-age window, divide reported dollars by the number of
customers whose *entire* window is observable. The two extensions start with the
mean of the last three complete age-window rates. **Flat** repeats that rate.
**Declining** reduces it by the ratio of the latest three-window mean to the
preceding three-window mean, once per three windows, with a smooth geometric
change between windows. If the ratio is above one, it is capped at one. Age
window 0 includes the first purchase and is never used to fit these extensions.

The tests below hide later windows, fit only earlier windows, and compare with
the withheld observed dollars. Each withheld window has all **23,570 original
customers** eligible, so the changing denominator cannot explain the errors.
The age 9–11 row is included in the age 9–14 row; these are not three
independent samples.

| Training ages (30-day windows) | Held-out ages | Observed dollars | Flat forecast; error | Declining forecast; error |
| --- | --- | ---: | ---: | ---: |
| 3–8 | 9–11 | $267,561 | $280,409; +4.8% | $260,617; −2.6% |
| 3–8 | 9–14 | $516,249 | $560,817; +8.6% | $493,976; −4.3% |
| 6–11 | 12–14 | $248,688 | $267,561; +7.6% | $259,346; +4.3% |

Here, error is `(forecast / observed − 1) × 100`. These tests favor decline on
absolute percentage error for these limited held-out windows. They do not
validate a 12- or 24-month continuation, and they cannot separate aging from
calendar seasonality or changing customer behavior. A recent three-window
ratio is a modeling assumption, not an observed long-run decay law.

The main extension uses ages **9–11** ($3.7839 per original customer per
30 days) and **12–14** ($3.5170). All 23,570 customers are observable through
age window 14 (days 420–449); the inferred decline factor is **0.9295 per
three 30-day windows**. The later observed windows have only 18,841, 9,758,
and 1,574 fully eligible customers, respectively. Their rates are $2.97,
$3.65, and $3.07, but they describe progressively selected early entrants and
do not set the extension. Their partial-window transactions remain in the
$2,500,315.63 observed total.

To translate customer age into the approved calendar periods, the script uses
the cohort's actual Q1 1997 first-purchase date distribution and spreads each
forecast 30-day amount evenly across those 30 days. That within-window timing
and the absence of explicit seasonality are additional assumptions.

## Forecast impact; provisional working case

| Scenario | July 1998–June 1999 forecast | Per original customer | Separate July 1999–June 2000 tail |
| --- | ---: | ---: | ---: |
| Flat | $1,008,568 | $42.79 | $1,011,331 |
| Declining (provisional working case) | $825,907 | $35.04 | $615,338 |

The main-period difference is **$182,660**, or 18.1% of the flat forecast.
The tail difference is **$395,992**. The tail is shown separately because it
is entirely unobserved; revenue after June 2000 is unmodeled rather than
assumed zero. Neither scenario by itself determines an advance or investor
return. Eligibility, the 50% repayment share, 1.2× cap, advance timing, and
costs require separate phase 4 assumptions and company information.

## Sensitivity to the lookback length

The three-window grouping above is a modeling choice, **not an industry
standard or an independently validated forecast rule**. The same flat and declining
rules were also run with 2, 4, and 6 age windows in each comparison block. A
lookback of *L* compares the most recent *L* windows with the preceding *L*;
the decline factor is then applied once per *L* future windows. Thus the
lookback changes both the starting dollar rate and how quickly a decline
compounds.

For a fair short check, each length trained only through age window 12 and
predicted the **same held-out windows 13–14**. All 23,570 customers had complete
exposure in each held-out window. Their actual reported dollars were **$158,705**.
The six-window version has to begin its training at age window 1, just after
the entry window; only two fully comparable windows remain for its common
holdout. This is too little evidence to crown a lookback winner.

| Lookback (30-day windows) | Flat backtest error | Declining backtest error | Flat July 1998–June 1999 | Declining July 1998–June 1999 |
| ---: | ---: | ---: | ---: | ---: |
| 2 | +7.5% | +0.5% | $965,453 ($40.96/customer) | $718,883 ($30.50/customer) |
| 3 | +9.7% | +5.3% | $1,008,568 ($42.79/customer) | $825,907 ($35.04/customer) |
| 4 | +12.6% | +10.0% | $1,001,835 ($42.50/customer) | $775,138 ($32.89/customer) |
| 6 | +14.3% | +8.2% | $1,046,838 ($44.41/customer) | $865,014 ($36.70/customer) |

The common holdout is not the only possible test. Below, each shorter
lookback gets a longer test using as much fully comparable later history as
the file permits. In the six-window holdout, the 2-, 3-, and 4-window methods
all predict the same observed ages **9–14** ($516,249). In the three-window
holdout they all predict ages **12–14** ($248,688). Every tested window still
has all 23,570 customers eligible. The three-window holdout is part of the
six-window holdout, so these tests are not independent evidence.

| Held-out ages | Lookback | Training ages | Flat error | Declining error |
| --- | ---: | --- | ---: | ---: |
| 9–14 (six windows) | 2 | 5–8 | +8.5% | +1.0% |
| 9–14 (six windows) | 3 | 3–8 | +8.6% | −4.3% |
| 9–14 (six windows) | 4 | 1–8 | +10.8% | −9.6% |
| 12–14 (three windows) | 2 | 8–11 | +3.2% | −10.7% |
| 12–14 (three windows) | 3 | 6–11 | +7.6% | +4.3% |
| 12–14 (three windows) | 4 | 4–11 | +11.4% | +8.6% |

The six-window lookback cannot enter either longer test: its two six-window
training blocks need ages **1–12**, leaving only ages **13–14** fully observed
for all customers. The two-window declining rule is closest over the
six-window holdout but overshoots the decline in the later three-window
holdout. This is why the single common test's +0.5% error should not decide
the base case on its own.

The separate July 1999–June 2000 tail is more uncertain:

| Lookback | Flat tail forecast | Declining tail forecast |
| ---: | ---: | ---: |
| 2 | $968,098 | $463,053 |
| 3 | $1,011,331 | $615,338 |
| 4 | $1,004,580 | $529,653 |
| 6 | $1,049,706 | $653,340 |

The two-window declining rule fits this one short holdout most closely. It
also produces the lowest main-period forecast, **$718,883**, versus **$865,014**
for the six-window declining rule: a **$146,131** range caused solely by the
lookback choice. The flat main-period range is **$965,453–$1,046,838**. These
differences are large enough to keep the lookback and flat-versus-declining
choices visible as assumptions. The year-two tail is even more
sensitive. The common backtest measures two already observed age windows; it
does not validate a one- or two-year continuation. No future Q4 1998 cohort
forecast or repayment-eligible revenue is inferred from this comparison.

I selected the three-window decline as a **working
case** after reviewing the lookback sensitivity. The two-window decline is a
lower-revenue sensitivity, not a measured floor. This choice organizes the
scenario analysis; it does not assert that the $825,907 estimate is the most
likely outcome or that the proposed investment works at that revenue level.

The [methodology literature note](../docs/methodology_literature.md) explains
how the later-window holdouts relate to established forecast validation and
why the **three-window length itself is not an academic or industry norm**.
General methodological sources may postdate July 15, 1998 for learning and
method justification; they contribute no later CDnow facts to this historical forecast.

The [lookback comparison code](../scripts/lookback_sensitivity.py) writes
[`lookback_sensitivity.json`](lookback_sensitivity.json), including the exact
training blocks, holdout predictions, per-customer amounts, and both forecast
periods for each length.

This forecast does not account for large-scale changes in how media is
distributed, shared, or consumed. No external source or later historical
outcome was used to fit these mechanical extensions.

Rebuild from the source manifest, phase 2 output, and first-purchase dates with
`.\.venv\Scripts\python.exe scripts\forecast_extensions.py`. The machine-readable
[`forecast_extensions.json`](forecast_extensions.json) includes period and
quarter detail, inputs, and formulas. The analysis code is
[`forecast_extensions.py`](../scripts/forecast_extensions.py).
