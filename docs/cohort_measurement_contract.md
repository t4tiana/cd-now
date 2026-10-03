# Phase 2  - cohort measurement contract

This defines the descriptive measures before calculating them. The source is the [CDnow file](../CDNOW_data/read_me_CDNOW_master.txt), identified by the [source manifest](source_manifest.json), through **June 30, 1998 inclusive**. Analyze the typed rows in `cdnow_analysis.stg_cdnow_transactions`; retain all source rows under the [phase 1 exception decisions](exception_review.md). Reconcile any downstream output to 69,659 transaction rows, 23,570 customers, and $2,500,315.63 of **reported transaction dollars**. These are observed file totals, not cash collected, profit, a forecast, or repayment-eligible revenue.

## Population and event definitions

| Measure | Definition and limit |
| --- | --- |
| Customer | Distinct text `customer_id`. The file does not establish whether IDs are unique real people or merge activity across identities. |
| Cohort entry | Each customer's earliest recorded `transaction_date`, including a zero-dollar row if it is the earliest. All entries are in Q1 1997. This is a first recorded purchase date, not a marketing acquisition date. |
| Transaction row | One physical source line in staging. It is not a verified distinct order; keep same-day and identical-looking rows. |
| Reported dollars | Sum `transaction_dollars` in exact cents. Zero-dollar rows contribute zero but remain in counts and cohort-entry assignment. Do not infer refunds, cancellations, cash collection, or contract eligibility. |
| Purchasing customer in a period | Distinct customer with at least one recorded transaction row in that period, including a zero-dollar row. Where useful, also report customers with positive reported dollars as a sensitivity. |
| Observed repeat buyer | Customer with a transaction on a calendar date later than their first recorded date. Same-day additional rows count as rows, but do not establish a later-date repeat. A zero-dollar later-date row counts under the recorded-transaction definition; check positive-dollar repeats separately. No later-date row by the cutoff is **no repeat observed**, not permanent churn. |
| Purchase frequency | Recorded transaction rows per customer and distinct purchase dates per customer. Do not label either as a verified number of orders. |

## Time and denominators

- **Calendar view:** group each recorded transaction by its calendar quarter; report reported dollars, rows, and distinct purchasing customers. All cohort entrants first appear in Q1 1997. Later quarters have unequal time since entry across customers, so calendar results describe timing and seasonality rather than like-aged retention.
- **Customer-age view:** for a customer entering on date `d`, age period `k` covers dates `d + 30k` through `d + 30(k+1) - 1` inclusive. Period 0 is days 0–29 and includes the entry transaction and all other same-day rows. All customers must be observed through the end of a period to enter its **full-window denominator**. Age-zero activity is 100% by definition and must not be presented as evidence of retention.
- **Censoring:** a customer-period is incomplete when its end date is after June 30, 1998. Keep any recorded rows and dollars from that partial period in full-file and calendar reconciliations. Exclude that customer-period's activity and dollars from full-window rates, averages, and comparable age-period totals; report the eligible customer count beside each age-period result. Do not fill unobserved dates with zeros.
- **Age-period outputs:** show eligible customer count, recorded rows, distinct purchasing customers, reported dollars, purchasing-customer share (`purchasing customers / eligible customers`), and reported dollars per eligible customer. Calculate all age-period numerators from the same fully observed customer-periods as the denominator. Period-0 purchasing share is definitional; interpret repeat behavior using later-date measures.
- **Repeat by horizon:** for a 30-, 60-, or 90-day horizon `H`, include only customers whose entry date plus `H` days is on or before the cutoff. The numerator is those with a recorded transaction on days 1 through `H` after entry. State the numerator and denominator; this is an observed cumulative repeat rate, not a lifetime retention or churn estimate.
- **Window choice:** 30-day periods are the main revenue-timing view; 60-day periods are a check on repeat-buying interpretation. The short [method note in the analysis plan](../notes/analysis.md#agreed-measurement-assumptions-and-output) explains the choice. Neither period is an asserted CDnow buying cycle.

## Customer distribution

Sum each customer's reported dollars and transaction rows over their observed history, including customers with zero reported dollars. Report simple distribution summaries and the shares of all reported dollars produced by the top 1% and top 10% of customers, ranking by observed dollars. For 23,570 customers, use the top **236** and **2,357**, respectively (round a fractional customer count upward). Observed totals reflect unequal follow-up time. Describe large transactions and repeated-looking rows as possible influences without deleting them.

## Deliverable boundary

The phase 2 result is a compact, investment-facing findings note with a few tables or charts, backed by reproducible code and machine-readable outputs. It reports **what this one cohort did through the cutoff**. Future revenue, future-cohort size or behavior, contribution, and the financing repayment base belong to later phases and require labeled assumptions or CDnow information.
