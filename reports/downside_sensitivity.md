# P3.4: illustrative downside grid for the observed cohort

**Historical decision date:** July 15, 1998. **Observation cutoff:** June 30,
1998. The source is the supplied Q1 1997 first-purchase cohort: 23,570 customer
IDs and $2,500,315.63 of **observed reported transaction dollars** through the
cutoff. The grid concerns only its *future* reported dollars. The provisional
three-window declining extension forecasts **$825,907** for July 1998–June
1999 and a separate **$615,338** for July 1999–June 2000. These forecasts are
not observed revenue, contribution, cash receipts, or repayment-eligible
revenue. I use the 20% early-repeat and early-top-quarter reductions as separate decision gates in the committee memo. This grid shows each stress independently.

## What the observed groups contribute

Groups are defined from each customer's first 90 days only. Their measured
outcome is customer-age days **270–449**, a 180-day span fully observable for
all **23,570 original customers**. Its $516,248.77 of reported dollars
reconciles to the [complete age windows](cohort_analysis.json). It anchors the
forecast; it does not prove that the same group shares persist after day 449.

| First-90-day group | Customers (share of 23,570) | Observed days 270–449 dollars | Share of $516,249 anchor |
| --- | ---: | ---: | ---: |
| Positive-dollar purchase on a later date by day 89 | 6,864 (29.1%) | $341,367 | 66.1% |
| No such early repeat | 16,706 (70.9%) | $174,882 | 33.9% |
| Top 25% by first-90-day reported dollars | 5,892 (25.0%) | $326,432 | 63.2% |
| Top 10% by first-90-day reported dollars | 2,357 (10.0%) | $206,592 | 40.0% |

The high-spender groups overlap each other and the early-repeat group; these
are alternative views, not additive segments. Ranking uses early dollars
descending and customer ID to break ties, so the group sizes are fixed and
reproducible. A future cohort's group memberships are unknown when its initial
advance is made.

## How the stresses work

The early-repeat stress reduces the **29.1% share of original customers** who
repeat in days 1–89 by 10%, 20%, or 30% *relative to that share*. Customers
removed from this group are assigned the observed no-early-repeat anchor rate:
$10.47 per group customer in days 270–449, versus $49.73 for early repeaters.
For example, a 20% relative reduction changes the early-repeat share to
23.3% of original customers. This is an assumed future mix change, not a
measured deterioration in the supplied cohort.

The high-spender stresses reduce the selected group's assumed future dollar
contribution by 10%, 20%, or 30%, keeping everyone else's contribution fixed.
Each resulting anchor ratio multiplies every provisional forecast quarter,
including the separate second-year tail. This holds the **timing shape and
decline rate fixed**. A different aging pattern, seasonality, or late change
in group mix could move both the amount and the timing. Stresses are applied
separately; adding their losses would double-count overlapping customers.

| One-at-a-time stress | Assumed reduction | July 1998–June 1999 forecast | Change from $825,907 | Separate July 1999–June 2000 tail |
| --- | ---: | ---: | ---: | ---: |
| Fewer early repeaters | 10% relative | $782,790 | −$43,117 | $583,214 |
| Fewer early repeaters | 20% relative | $739,673 | −$86,234 | $551,090 |
| Fewer early repeaters | 30% relative | $696,555 | −$129,351 | $518,965 |
| Top 25% contribute less | 10% | $773,684 | −$52,223 | $576,430 |
| Top 25% contribute less | 20% | $721,461 | −$104,446 | $537,521 |
| Top 25% contribute less | 30% | $669,237 | −$156,669 | $498,612 |
| Top 10% contribute less | 10% | $792,856 | −$33,051 | $590,714 |
| Top 10% contribute less | 20% | $759,805 | −$66,102 | $566,089 |
| Top 10% contribute less | 30% | $726,754 | −$99,153 | $541,465 |

The top-25% stress has the larger effect at the same percentage reduction
because it covers more observed anchor dollars. The early-repeat stress tests
how many customers enter a historically higher-spending group; the
high-spender stresses test how much that group of customers contributes.
Neither identifies a causal mechanism. The top-10% case tests whether a
narrower concentration of spending changes the conclusion.

These percentages are **illustrative severity levels**, not measured
probabilities or lower bounds. The provisional forecast's two-window
declining alternative ($718,883 for the main year) is a separate test of the
decay rule. It should not be combined mechanically with this table. More
cohorts, especially by acquisition channel, would show whether a change in
early-repeat mix or high-spender contribution is plausible and whether either
persists at older ages.

The source file does not establish acquisition costs, contribution margins,
refunds, cash collection, or contractually eligible revenue. These dollar
scenarios therefore do not determine an advance or investor return. The
analysis does not account for large-scale changes in how media is distributed,
shared, or consumed. No external source or later historical outcome informed
this mechanical sensitivity.

Rebuild the [machine-readable grid](downside_sensitivity.json), including
unrounded factors and quarterly amounts, with
`.\.venv\Scripts\python.exe scripts\downside_sensitivity.py`. The
[script](../scripts/downside_sensitivity.py) checks the source manifest and
anchor reconciliation.
