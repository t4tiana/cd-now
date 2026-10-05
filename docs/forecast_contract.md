# Phase 3 revenue forecast contract

**Historical decision date:** July 15, 1998. **Observed transaction cutoff:**
June 30, 1998, inclusive. The only supplied CDnow transaction data cover
23,570 customers whose first recorded CDnow purchase was in Q1 1997. This
document defines what phase 3 will forecast; it does not yet contain a revenue
forecast. I selected the horizon and example future quarter
below before numeric forecasting.

## Two different forecast objects

1. **Remaining revenue from the observed cohort:** reported transaction
   dollars dated after June 30, 1998 from the same 23,570 recorded customer
   IDs. Their $2,500,315.63 through the cutoff is observed reported dollars,
   not part of the forecast. The remaining amount must be estimated.
2. **Revenue from a future quarterly cohort:** reported transaction dollars
   from customers whose **first recorded CDnow purchase** occurs from
   **October 1 through December 31, 1998 (Q4 1998)**, starting with that
   first purchase and followed by customer age. This is a hypothetical
   cohort, not a second supplied dataset. Its customer count, within-quarter entry dates, channel
   mix, and per-customer behavior must be assumptions or separately verified
   company inputs. A marketing contact before first purchase is not visible
   in this file and does not define entry here. Its forecast will use the
   same 30-day age units as the observed-cohort model, so revenue from its
   first purchase is shown separately from later-age revenue. Calendar dates
   will depend on the chosen future quarter and within-quarter entry timing.

The base forecast will use the Q1 1997 cohort's **overall** reported dollars
per original customer by 30-day age window. Each customer's age starts on
their first recorded transaction date; days 0–29 include entry and are not
evidence of retention. The 23,570 original customers remain the per-customer
denominator. Windows used to compare like-aged activity include only
customers observed through the entire window. The [phase 2 tables](../reports/cohort_tables.md)
show that all 23,570 customers qualify through days 420–449; eligible counts
then fall to 18,841, 9,758, and 1,574 in the next three windows. Those
oldest-window averages need explicit treatment before extrapolation. Rows in
partial windows remain in the full observed total and must not be silently
counted as zero future revenue.

An early-90-day customer cut may test whether early behavior helps explain
later reported dollars. It cannot use a customer's full observed history to
define an early group. For a future cohort funded at entry, the mix of
90-day groups is itself unknown until those 90 days have elapsed; it cannot
be presented as information available when sizing an initial advance.

## Measure and boundaries

- **Forecast measure:** reported transaction dollars under the supplied
  file's definition, before any unobserved refunds, shipping/tax separation,
  collection adjustment, or cost deduction. Forecasts must be labeled as
  assumptions, not observed revenue.
- **Attribution for the modeled customer cohort:** all recorded transaction
  dollars from the defined customer IDs on and after each ID's first recorded
  purchase date, including zero-dollar rows in activity counts but not dollar
  sums. The file provides no order ID, verified person identity, or acquisition
  channel. These rules define the analysis series; CDnow would need to confirm
  the actual repayment-eligible sales and any refund treatment.
- **Phase boundary:** phase 3 reports gross recorded-dollar scenarios and
  their timing. It does not call them contribution, cash collected, or
  repayment-eligible revenue. The proposed 50% share and 1.2× cap belong to
  phase 4, after an explicit eligible-revenue assumption.
- **Historical frame:** any external fact used to set a forecast assumption
  must have an original publication date no later than July 15, 1998 and pass
  the [source audit rule](../notes/analysis.md#external-source-gate).
  The forecast and final memo will state that they do not account for
  large-scale changes in how media is distributed, shared, or consumed.

## Approved horizon and future quarter

| Choice | My decision | Interpretation |
| --- | --- | --- |
| Remaining-revenue main period | **July 1, 1998–June 30, 1999** (12 months beyond the observed cutoff). | Show the Q1 1997 cohort's forecast reported dollars in this period separately from its $2,500,315.63 observed through June 30, 1998. |
| Additional tail sensitivity | **July 1, 1999–June 30, 2000**, shown separately from the main forecast. | This tests how a longer, entirely unobserved tail could change cumulative revenue and later financing outcomes. It is not part of the main 12-month result. Revenue after June 30, 2000 is unmodeled, not assumed to be zero. |
| Example future first-purchase quarter | **Q4 1998**, October 1–December 31, 1998. | It is the first full calendar quarter after the July 15 decision date. Q3 1998 had already begun; it is not the example financing cohort. |

The scenario analysis shows the future Q4 1998 cohort's revenue from its first recorded
purchase onward, using the same 30-day customer-age units as the observed
cohort. The exact age-to-calendar mapping and assumed distribution of entry
dates within Q4 are stated in the scenario model before any
future-cohort total or repayment timing is presented. A shorter age range
must not be compared with a longer observed-cohort range as if the totals
were like for like. Forecast revenue beyond each displayed horizon remains
unmodeled, not assumed to be zero.

The forecast and financing reports state the choices for the observed-age
extension, downside cases, and assumed future cohort size and mix.
