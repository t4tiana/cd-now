# Opportunity cost of the illustrative $1.2 million Q4 advance

**Decision date: July 15, 1998.** Compare alternatives over **October 1, 1998 through December 22, 1999**, the modeled cap date in the restrained Q4 illustration. This is a prospective calculation using only a rate published by the decision date, not actual returns subsequently earned. It does not revise the unselected advance or the investment recommendation.

## Same dollars, same 447 days

The hypothetical financing advances **$1.2 million on October 1, 1998** for **40,000 Q4 first purchasers**. It transfers the Q1 1997 cohort's age-based transaction pattern, applies the separate **20% reduction in later spending by the early top-spending quarter**, and supposes **80% of forecast transaction dollars are eligible, collected, and remitted on the transaction day**. That fraction is an arbitrary sensitivity, not evidence. At a 50% repayment share and 1.2× cap, the model pays **$1.44 million by December 22, 1999**: **$240,000 gross nominal gain** before collection costs, loss risk, and taxes. The Q1 1997 cohort's $2,500,315.63 through June 30, 1998 remains observed transaction dollars; all Q4 figures are forecasts or repayment assumptions.

For an alternative known at the decision date, the Federal Reserve's **[H.15 release of July 13, 1998](https://www.federalreserve.gov/releases/h15/19980713/)** reports a **5.34% annual yield** as the **weekly average for July 6–10, 1998 on one-year Treasury securities at constant maturity** (table row “Treasury constant maturities,” “1-year,” “Week Ending Jul 10”; its footnote 13 and definition at the bottom). The Federal Reserve Board is the publisher and release attribution; no individual author is named. A constant-maturity yield is an interpolated market reference, **not an actual 447-day Treasury available to lock in on October 1**. The calculation holds 5.34% flat through the end date and applies annual compounding as an approximation. Future rates, reinvestment prices, fees, and taxes are unknown.

| Use of the same $1.2m on October 1 | Value at December 22, 1999 | Gain above $1.2m |
| --- | ---: | ---: |
| Treasury-rate proxy: 5.34% held flat for 447 days | $1,278,940 | $78,940 |
| Cohort: add nominal remittances received by cap date, without reinvesting interim cash | $1,440,000 | $240,000 |
| Cohort: reinvest each modeled remittance at the same assumed 5.34% until December 22 | $1,502,357 | $302,357 |

The **like-for-like end-date comparison** is the first and third rows: the cohort produces **$223,417 more terminal value** if every modeled payment arrives on time and interim receipts can earn the assumed Treasury rate. The middle row answers the simpler “$240,000 versus what?” question, but understates the value of early cohort remittances because it leaves them idle. The Treasury figure is a relatively low-risk reference, not a risk-matched required return for lending to CDnow; the family office's actual alternative opportunities are unknown.

## Why doubling the advance does not automatically double the gain

At a fixed 50% share and 1.2× cap, doubling the advance to **$2.4 million** raises the *maximum* gross gain to **$480,000**, but also raises the eligible-revenue hurdle from **$2.88 million to $5.76 million**. It does not itself double the number of purchasers or their spending. Holding the same weaker-top-spender behavior and illustrative 80% eligibility, the model shows:

| Assumed Q4 first purchasers | Forecast transaction dollars through Dec. 2000 | Repayments on $2.4m through Dec. 2000 | Cap date |
| ---: | ---: | ---: | --- |
| 40,000 (same restrained cohort) | $4.949m | $1.980m | Not reached; $420,350 of principal still unrepaid |
| 62,000 (reference count) | $7.671m | $2.880m | September 28, 2000 |
| 80,000 (double the restrained count) | $9.898m | $2.880m | December 22, 1999 |

The 80,000-row simply doubles the **assumed** 40,000 purchasers while holding first spend, repeat behavior, channel mix, and cost per acquisition fixed. It shows the arithmetic required to double the modeled $240,000 gain on the same date; it does not show that another $1.2 million would acquire another 40,000 equally valuable purchasers. Higher marketing spend could buy fewer purchasers, and a different channel could bring weaker repeat buying. The proposed advance is fixed up front, while the actual Q4 purchaser count would only be known later. At 40,000 purchasers, even making **100%** of the forecast transaction dollars eligible produces only about **$2.475 million** of payments by December 2000 on $2.4 million advanced, below its $2.88 million cap.

## What the apparent premium buys

The extra $223,417 is compensation for purchaser-count, repeat-spending, eligibility, collection, timing, and CDnow payment risk. It is **not** expected profit: this file supplies no defensible probabilities for those outcomes. As a stark illustration only, if the cohort either follows the modeled payment path in full or loses the entire advance with no recovery, the probability of full success must exceed **85.1%** to beat the Treasury proxy in end-date value (`$1,278,940 / $1,502,357`). Partial recoveries and delayed payments would change that threshold. The model's assumptions cannot establish an 85.1% success probability.

If the future cohort has only the original **23,570 purchasers**, while holding the same weaker-spender behavior and 80% eligibility, the [same model](../scripts/opportunity_cost.py) projects only **$1,166,509 of repayments through December 31, 2000** on a $1.2 million advance; principal is not yet fully recovered within that longer displayed horizon. Revenue beyond it is unmodeled, not zero. This is why the Treasury spread cannot be treated as a margin of safety.

The conditional investment case would need CDnow's recent first-purchaser counts, cost to acquire them, cohort-level cash contribution, reconciliation from transaction dollars to eligible collected revenue, and enforceable collection rights. If those cannot support a high likelihood of payment and show CDnow can afford the 50% share, the apparently larger nominal return is not enough reason to invest. This assessment does not account for large-scale changes in how media is distributed, shared, or consumed.

**Investment-mandate fit:** The family office's stated mission is to use capital to accelerate productive people. On the evidence available, a large advance to expand CDnow's marketing and physical-CD distribution has **weak demonstrated fit with that mandate**: the analysis shows possible sales growth, but no specific mechanism by which the financed activity advances the mission. CDnow may still belong in a separate return-seeking allocation if its risk-adjusted return clears that bar; the case has not established that return either. This is an assessment of fit with the proposed financing, not a claim that CDnow or music retailing has no social value.

Reproduce the daily cash-flow and flat-rate comparison with `.\.venv\Scripts\python.exe scripts\opportunity_cost.py`; [JSON output](opportunity_cost.json) records all inputs and results.
