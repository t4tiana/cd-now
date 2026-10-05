# Q4 1998 first-purchaser count: decision scenarios

**Decision date: July 15, 1998.** These are scenarios for a *new* Q4 1998 first-purchase cohort. The supplied Q1 1997 cohort's $2,500,315.63 through June 30, 1998 is observed transaction dollars. Its remaining-revenue extension calibrates age-based behavior; none of its already observed sales repays a Q4 1998 advance.

## Count anchor and range

CDnow's [February 9, 1998 IPO prospectus](../CDNOW_data/SEC_424B1.txt) (filed February 11; pp. 3, 5–6) reports approximately **209,000 first purchasers during 1997**. The supplied dataset has **23,570 Q1 1997 first purchasers**. If those definitions align, about **185,430** first purchased across Q2–Q4 1997, averaging **61,810 per quarter**. This residual is approximate because the company count is rounded, and it is an *average*, not a measured Q4 count. It is the best available CDnow purchaser-count anchor, but CDnow's 1998 first-purchase counts are missing.

| Q4 1998 count scenario | Assumed first purchasers | Relationship to the 1997 anchor | Interpretation |
| --- | ---: | --- | --- |
| Restrained | 40,000 | 65% of the Q2–Q4 1997 quarterly average | CDnow acquires more than the supplied Q1 1997 count, but partner traffic or competition does not sustain the later-1997 average. |
| Reference | 62,000 | Approximately the Q2–Q4 1997 quarterly average | Carries the disclosed residual average into Q4 1998 without adding purchaser growth. This is a planning center, not a measured forecast. |
| Expansion | 90,000 | 146% of the residual average | Tests stronger conversion and acquisition from a larger business and paid partnerships; requires more spend and may change channel quality. |

The range is a judgmental bracket, not a statistical interval. It does not assign probabilities, extrapolate company sales into customer counts, or assume any partner yields a known number of buyers. *Stereophile*'s [May 3, 1998 report](https://www.stereophile.com/content/cdnow-tops-chart-expands-europe) by Barry Willis relays CDnow's **$10 million Q1 1998 revenue** and **135,000 new registrations** (paragraphs beginning “The numbers are up” and “CDnow has registered”). Registrations are not first purchasers. Jennifer Sullivan's [April 10, 1998 *Wired* report](https://www.wired.com/1998/04/dealing-for-dollars/) describes the Lycos agreement; it establishes reach and a spending commitment, not purchaser conversion or cohort acquisition cost. The [source inventory](../docs/company_financial_evidence_1998.md) records provenance and limitations.

As a market cross-check, Mike Romano's [July 22, 1997 *Wired* article](https://www.wired.com/1997/07/amazon-com-moves-toward-music-video-sales/) attributes **$18.3 million 1996 online CD sales** and a **$110 million 1998 market-sales forecast** to Jupiter Communications (paragraphs beginning “The online music industry” and “Tower Online”). Jennifer Sullivan's [June 3, 1998 *Wired* article](https://www.wired.com/1998/06/custom-discs-give-cdnow-new-spin/) relays Jupiter's **$49 million 1997 online music-retailing sales estimate** (paragraph beginning “Many figure”). The underlying Jupiter reports were unavailable and the two articles' market definitions are not reconciled. The $110 million is a contemporary *forecast*, not measured 1998 sales. More market dollars make the expansion case worth testing; sales can also rise through repeat orders, basket size, prices, or share shifts. The [historical market context](../docs/historical_market_context.md#online-music-growth-and-a-future-cohort) records the source checks and conflicting reported market-share figures. Neither market estimate is used as a first-purchaser multiplier.

## Revenue and repayment, holding other assumptions separate

Each assumed purchaser enters uniformly from October 1 through December 31, 1998. Per-purchaser initial and repeat transaction-dollar behavior copies the Q1 1997 cohort's complete customer-age pattern through day 449, then the provisional three-window declining extension. The two decision gates separately lower early-repeat prevalence by 20% relative or later spending from the first-90-day top-spending quarter by 20%; both leave days 0–89 unchanged. These groups overlap, so the stresses are not added. No Q4 seasonality, price, order-size, channel-mix, or acquisition-cost change is modeled. The historical pattern is a transfer assumption, not Q4 observed revenue.

| First purchasers | Provisional forecast reported dollars | Early-repeat gate | Top-quarter gate |
| ---: | ---: | ---: | ---: |
| 40,000 | $5.356m | $5.020m | $4.949m |
| 62,000 | $8.301m | $7.781m | $7.671m |
| 90,000 | $12.050m | $11.295m | $11.136m |

All figures forecast **Q4 1998 through December 31, 2000 transaction dollars** for the hypothetical cohort. October entrants have more follow-up than December entrants by that calendar end. Later revenue is unmodeled, not zero. The same per-purchaser behavior makes totals proportional to purchaser count by construction; real channel mix or cost could break that relationship.

The nearer periods matter for cash timing. At **40,000** purchasers, the provisional case forecasts **$1.803m in Q4 1998**, including first purchases, and **$1.115m in January–June 1999**. The top-quarter downside forecasts **$1.017m** for that first half. At **62,000** purchasers, provisional Q4 and first-half amounts are **$2.795m** and **$1.728m**. These remain transaction-dollar forecasts, not collections. The [JSON rows](future_cohort_size_scenarios.json) record Q4 and first-half amounts for every scenario.

For comparison only, suppose the advance is **$50 per assumed purchaser**: $2.0m, $3.1m, or $4.5m at the three sizes. This is **not a chosen advance or an observed acquisition cost**. It creates the same per-purchaser repayment hurdle at every size: $120 in eligible and collected revenue for a $60 capped payment. Under the provisional, early-repeat, and top-quarter cases, respectively, **89.6%, 95.6%, and 97.0%** of forecast reported dollars must become eligible and collected by December 31, 2000 to reach the 1.2× cap. If 100% qualifies and remits immediately, the three cases cap on **August 6, October 25, and November 14, 2000**, regardless of assumed size because the advance scales with it. Same-day collection is an optimistic timing assumption.

At an **illustrative 80% eligible-and-collected fraction**, none caps by the model end. Repayments equal half of eligible dollars; the table gives the top-quarter gate, which is the lower-revenue of the two separate behavior gates.

| First purchasers | $50-per-purchaser illustration | Top-quarter forecast transaction dollars | Assumed eligible and collected at 80% | Repayments by Dec. 31, 2000 | Difference from principal |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 40,000 | $2.000m | $4.949m | $3.959m | $1.980m | −$0.020m |
| 62,000 | $3.100m | $7.671m | $6.137m | $3.068m | −$0.032m |
| 90,000 | $4.500m | $11.136m | $8.908m | $4.454m | −$0.046m |

The 80% fraction is an arbitrary sensitivity, **not a measured or standard eligibility rate**. The full 100%/80% grid, including both behavior gates, is in the [machine-readable output](future_cohort_size_scenarios.json). Repayment is `min(50% × eligible collected revenue, 1.2 × advance)` over the modeled dates. Forecast transaction dollars are not collected cash; the model's eligible dollars are assumptions, and its repayments are conditional calculations, not investor returns. Delays, exclusions, returns, and counterparty risk can reduce or postpone payments. The model says nothing about whether CDnow can fund the marketing and service costs while remitting half of eligible revenue. Its company-wide gross margin is not a cohort margin.

The [committee memo](../final_deliverables/investment_committee_memo.md) now proposes **$1.2 million as a diligence ceiling**, fixed before the quarter, with **no disbursement on the current evidence**. At 80% illustrative eligibility, both separate 20% behavior downsides reach its $1.44 million cap in December 1999 with 40,000 assumed first purchasers; the 62,000 case caps in March 1999. These dates assume prompt collection and do not prove the cohort count, eligible fraction, or CDnow's capacity to remit. The [JSON output](future_cohort_size_scenarios.json) includes this fixed-ceiling comparison separately from the older $50-per-purchaser scale test.

The memo also tests one **joint downside**: 30,000 Q4 first purchasers, 15% less reported dollars at ages 0–89, the separate top-quarter stress factor of 0.873537 on all ages 90 and later, and 60% of reported dollars assumed eligible and collected. These are judgmental severities, not a measured Q4 case or a probability bound; the top-quarter stress is applied to later aggregate dollars and does not re-identify customers. The model yields **$3,470,936** in forecast transaction dollars, **$2,082,562** assumed eligible and collected, and **$1,041,281** in repayments by December 31, 2000 on a fixed $1.2 million advance. **$158,719 of principal remains unrepaid within that horizon**; later revenue is unmodeled rather than assumed zero. The `joint_downside` object in the [JSON](future_cohort_size_scenarios.json) records the inputs and exact outputs. It is a combined stress on count, initial spend, later spend, and eligibility, not the sum of overlapping customer-group stresses.

## Decision impact and missing proof

Purchaser count mainly determines the *scale* of both revenue and a plausible acquisition budget. A higher count does not by itself improve dollars per purchaser, cap timing at a fixed advance per purchaser, or CDnow's ability to afford the 50% share. The larger scenario therefore requires first-purchaser records by quarter and channel, channel acquisition spend and commitments, and like-aged repeat behavior for recent cohorts. The advance also requires a bridge from recorded orders to eligible collected revenue and cohort-level contribution after CDs, fulfillment, shipping, processing, refunds, and support. These are requests to test the judgment, not invented inputs.

Reproduce the grid with `.\.venv\Scripts\python.exe scripts\future_cohort_size_scenarios.py`. The script uses the same verified source profile and downside factors as [the original financing model](../scripts/financing_scenarios.py). This historical assessment does not account for large-scale changes in how media is distributed, shared, or consumed.
