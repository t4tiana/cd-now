# P3.3: early-90-day signal, equal later follow-up

**Decision date:** July 15, 1998. **Source:** the supplied Q1 1997
first-purchase cohort of 23,570 customer IDs, with reported transactions
through June 30, 1998. I chose an early **later-date,
positive-dollar repeat purchase** as the lead diagnostic. All groups below
use only information recorded in customer-age days **0–89** to assign the
early signal. The outcome is reported dollars in days **90–449**, a 360-day
follow-up that is fully observable for **every original cohort customer**.
No group is defined from its later outcome.

## Lead signal: bought again on a later date in days 1–89

The first purchase on day 0 does not count as a repeat. Additional rows on
that same date do not count either. A positive-dollar transaction on any later
date through day 89 does count. Zero-dollar rows remain in the source totals
but do not count as positive-dollar repeats.

| Early signal | Customers (% of 23,570) | Observed days 90–449 dollars | Later dollars per customer in group | Group members with a positive-dollar later purchase |
| --- | ---: | ---: | ---: | ---: |
| At least one positive-dollar later-date purchase by day 89 | 6,864 (29.1%) | $758,491 | $110.50 | 4,310 (62.8%) |
| None observed by day 89 | 16,706 (70.9%) | $351,329 | $21.03 | 4,457 (26.7%) |

The first group represents **29.1% of original customers** and **68.3% of
their combined $1,109,819 observed days 90–449 dollars**. Its later dollars
per member are about 5.3 times those of the second group. The result shows a
strong *association* between early repeat buying and later purchases within
this one cohort. It does not show that the early purchase caused the later
one, nor that either group will repeat its behavior in a future cohort.

The gap is visible in both equal 180-day halves of the later outcome:

| Early signal | Days 90–269 dollars per group member | Days 270–449 dollars per group member |
| --- | ---: | ---: |
| Early positive-dollar later-date repeat | $60.77 | $49.73 |
| No such early repeat | $10.56 | $10.47 |

The second half remains observed history, not a forecast of what follows day
449. Splitting the outcome also shows that the 360-day total is not driven
only by the first few months after the early signal.

## Secondary check: did early spending explain the association?

First-90-day reported dollars include the first purchase. Using observed
25th, 50th, and 75th-percentile cutoffs of **$15.36, $29.98, and $59.69**,
respectively, later dollars per group customer rose from **$12.52** in the
lowest spend group to **$123.14** in the highest. Identical dollar values
stay together at a cutoff, so these groups are not exactly 25% each.

Within the middle and higher early-spend groups, customers with an early
later-date repeat also had higher observed days 90–449 dollars per member:

| Early-spend band | With early repeat: customers; later dollars/member | Without early repeat: customers; later dollars/member |
| --- | ---: | ---: |
| Above $15.36 through $29.98 | 743; $28.80 | 4,675; $17.45 |
| Above $29.98 through $59.69 | 1,992; $48.65 | 3,871; $26.95 |
| Above $59.69 | 4,117; $155.36 | 1,775; $48.40 |

The lowest spend band had only **12** customers with an early repeat, too few
for a useful within-band comparison. These coarse bands do not isolate a
causal effect; customers can differ in many unrecorded ways, including the
channel through which they were acquired. They do show that the lead signal
is not solely a comparison between customers with small and large initial
spend.

## Forecast meaning and limits

This diagnostic does **not** change the provisional three-window declining
forecast or turn either group's observed dollars into a future forecast.
At the time an advance for a new cohort is made, its members' first 90 days
of repeat behavior are unknown. We cannot assume a Q4 1998 cohort will have
the same **29.1%** early-repeat mix, or that either group's later behavior will
match this one cohort. Those uncertainties matter for a downside case in
which fewer customers become repeat buyers or high spenders contribute less.
The transaction file still does not identify customer acquisition cost,
contribution, cash collected, or repayment-eligible revenue.

The first 90 days contain **$1,261,824.72 observed reported dollars** and
days 90–449 contain **$1,109,819.22**; both reconcile to the
[phase 2 age windows](cohort_analysis.json). Transactions after day 449 and
transactions in partially observed windows remain in the full
**$2,500,315.63** observed reported-dollar total. They are excluded from
the equal-follow-up comparison, not reclassified as zero purchases.

Rebuild the [machine-readable results](early90_diagnostic.json) with
`.\.venv\Scripts\python.exe scripts\early90_diagnostic.py`. The
[analysis code](../scripts/early90_diagnostic.py) records group rules,
denominators, cutoffs, and the source manifest. This historical diagnostic
does not account for large-scale changes in how media is distributed,
shared, or consumed.
