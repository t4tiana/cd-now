# Forecast benchmark before selecting a decision case

**As of July 15, 1998.** I compared the provisional three-window decline with a simple statistical benchmark. Both use only the supplied Q1 1997 first-purchase cohort through June 30, 1998. The $2,500,315.63 already recorded is observed transaction dollars. All amounts below are forecasts of transaction dollars, before any eligibility, collection, cost, or financing assumptions.

## What I fitted and checked

For each fully observed 30-day customer-age window, I divided reported dollars by the original 23,570 customers. The benchmark fits a straight line to the **logarithm** of that rate for age windows 3–14, then extends the line. A straight line on a log scale implies a constant percentage change per 30 days. The fitted final ratio is in [`trend_benchmark.json`](trend_benchmark.json). I excluded the entry window, which contains everyone's first purchase, and windows 1–2, where early repeat spending is materially higher. This is a modeling choice, so I tested other starting windows below.

Exponentiating a log-scale prediction gives a typical rate rather than, strictly, its arithmetic mean. The [forecasting text's bias-adjustment discussion](https://otexts.com/fpp2/transformations.html#bias-adjustments) explains the distinction. A simple average of the 12 fitted-window retransformation factors here is **1.0018**, changing the $788,475 first-year benchmark by about **$1,442**. I leave the unadjusted version visible as a benchmark; that small correction does not address long-horizon model risk.

I fitted each method using only earlier complete windows and compared its prediction with the same later observed windows. Every customer had a full opportunity to buy in each tested window. The tests overlap, and the longest is six 30-day windows, so they cannot validate a two-year extension.

| Hidden age windows | Actual dollars | Log-linear forecast (error) | Three-window decline (error) |
| --- | ---: | ---: | ---: |
| 9–11 | $267,561 | $263,489 (−1.5%) | $260,617 (−2.6%) |
| 9–14 | $516,249 | $507,353 (−1.7%) | $493,976 (−4.3%) |
| 12–14 | $248,688 | $244,638 (−1.6%) | $259,346 (+4.3%) |
| 13–14 | $158,705 | $166,038 (+4.6%) | $167,159 (+5.3%) |

Error is `(forecast / observed − 1) × 100`. The log-linear benchmark has smaller absolute error on these four checks, but they reuse much of the same data. I read this as a reason to keep both methods in view, rather than claim a statistically established winner.

## Forecast impact for the observed cohort

| Method | July 1998–June 1999 | Per original customer | Separate July 1999–June 2000 tail |
| --- | ---: | ---: | ---: |
| Log-linear benchmark, trained on ages 3–14 | $788,475 | $33.45 | $579,019 |
| Provisional three-window decline, trained on ages 9–14 | $825,907 | $35.04 | $615,338 |

The benchmark is $37,432 (4.5%) below the provisional method in the first year. Choosing the start of the benchmark's fitting period has a larger effect: training on ages 1–14 yields **$690,947** for the first year, whereas ages 6–14 yield **$813,931**. The corresponding separate tail spans **$443,143–$619,576**. The earliest post-entry windows contain faster decline; including them steepens the extrapolated trend. These are model sensitivities, not a probability interval or observed range of future outcomes.

## What this changes in the investment discussion

The two main methods give similar forecasts for the *existing* cohort, but the similarity does not establish how a Q4 1998 acquisition cohort will behave. The February [IPO prospectus](../CDNOW_data/SEC_424B1.txt) reported about **209,000 first purchasers in all of 1997**, compared with **23,570 first purchasers in the supplied Q1 1997 cohort**. If the definitions match exactly, the other three 1997 quarters together contributed about **185,430**; the filing does not give their individual counts. Contemporary reporting describes larger marketing alliances and rising company sales, while the reported **135,000 Q1 1998 additions were registrations, not verified first purchasers**. None gives a measured Q4 1998 new-purchaser count or shows that newly acquired customers repeat like the supplied cohort. I therefore have evidence to test larger cohort-size scenarios, but no sound single count to insert as fact.

The same prospectus's unaudited quarterly table reports that company net sales rose from **$2.582 million in Q1 1997 to $7.920 million in Q4**, while sales and marketing rose from **$0.430 million to $5.836 million**. Company gross margin fell from **18.6% to 14.0%** across those two quarters. This establishes neither how many new purchasers arrived nor what they cost or earned; holiday sales and existing customers may also matter. It does show why extrapolating purchaser growth without marketing spend and customer quality would be unsafe.

The forecast and any advance should remain conditional on three missing measurements: actual quarterly first purchasers and acquisition channels, cohort-level acquisition spend and variable contribution, and the fraction and timing of sales that would be eligible and collected for the 50% repayment share. Company-wide gross margin cannot substitute for this cohort's margin. These inputs can change the advance more than the $37,432 difference between the two forecast methods.

The script [`trend_benchmark.py`](../scripts/trend_benchmark.py) reproduces the tables. It uses the same first-purchase-date distribution and within-window calendar mapping as the provisional forecast. The forecast does not account for large-scale changes in how media is distributed, shared, or consumed.
