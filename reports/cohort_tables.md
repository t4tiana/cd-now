# Observed Q1 1997 CDnow cohort: table view

**Observation cutoff:** June 30, 1998, inclusive. **Population:** 23,570 customers and 69,659 retained transaction rows. **Reported dollars:** $2,500,315.63.

These are recorded sales amounts for one first-purchase cohort. They are not cash collected, profit, a forecast, customer lifetime value, or repayment-eligible revenue. Source, definitions, and reconciliations are in [cohort_analysis.json](cohort_analysis.json) and the [measurement contract](../docs/cohort_measurement_contract.md).

## Calendar quarters

Customers can appear in several quarters, so customer counts do not add to the cohort size. All customers first appear in 1997Q1 by definition.

| Quarter | Rows | Customers | Reported dollars |
| --- | --- | --- | --- |
| 1997Q1 | 31,798 | 23,570 | $1,071,805.47 |
| 1997Q2 | 9,730 | 5,376 | $359,153.66 |
| 1997Q3 | 7,558 | 4,263 | $292,395.37 |
| 1997Q4 | 7,816 | 4,221 | $300,806.76 |
| 1998Q1 | 6,851 | 3,817 | $262,823.89 |
| 1998Q2 | 5,906 | 3,317 | $213,330.48 |

## Customer age: complete 30-day windows

Age 0 is days 0–29 and includes each customer's entry purchase. Only customers observable through an entire window enter its denominator and numerators. Partial-window transactions remain in the full and calendar totals above.

| Age | Days | Eligible | Purchasers | Purchase % | Reported dollars |
| --- | --- | --- | --- | --- | --- |
| 0 | 0–29 | 23,570 | 23,570 | 100.0% | $990,452.48 |
| 1 | 30–59 | 23,570 | 3,088 | 13.1% | $154,774.60 |
| 2 | 60–89 | 23,570 | 2,375 | 10.1% | $116,597.64 |
| 3 | 90–119 | 23,570 | 2,149 | 9.1% | $103,575.54 |
| 4 | 120–149 | 23,570 | 2,110 | 9.0% | $108,724.32 |
| 5 | 150–179 | 23,570 | 2,024 | 8.6% | $100,862.03 |
| 6 | 180–209 | 23,570 | 1,868 | 7.9% | $93,711.16 |
| 7 | 210–239 | 23,570 | 1,772 | 7.5% | $84,962.66 |
| 8 | 240–269 | 23,570 | 1,930 | 8.2% | $101,734.74 |
| 9 | 270–299 | 23,570 | 1,824 | 7.7% | $96,452.69 |
| 10 | 300–329 | 23,570 | 1,721 | 7.3% | $90,425.65 |
| 11 | 330–359 | 23,570 | 1,622 | 6.9% | $80,682.50 |
| 12 | 360–389 | 23,570 | 1,741 | 7.4% | $89,983.28 |
| 13 | 390–419 | 23,570 | 1,724 | 7.3% | $83,562.62 |
| 14 | 420–449 | 23,570 | 1,560 | 6.6% | $75,142.03 |
| 15 | 450–479 | 18,841 | 1,185 | 6.3% | $56,014.40 |
| 16 | 480–509 | 9,758 | 646 | 6.6% | $35,605.27 |
| 17 | 510–539 | 1,574 | 107 | 6.8% | $4,831.10 |

## Repeat purchasing and frequency

A repeat requires a recorded row on a *later calendar date*. A row is not a verified distinct order. No later-date purchase observed by the cutoff does not mean permanent churn.

| Measure | Observed result |
| --- | --- |
| Later-date repeaters | 11,516 (48.9%) |
| Positive-dollar later-date repeaters | 11,515 |
| No later date observed by cutoff | 12,054 |
| Median days to first later date, among repeaters | 57 |
| Multiple rows but no later date | 146 |
| Later-date reported dollars | $1,715,755.02 |
| Customers with one recorded row | 11,908 |
| Median recorded rows per customer | 1 |
| 90th percentile recorded rows | 6 |

| Horizon after entry | Fully observed customers | Repeated by horizon | Repeat % |
| --- | --- | --- | --- |
| 30 days | 23,570 | 4,115 | 17.5% |
| 60 days | 23,570 | 5,929 | 25.2% |
| 90 days | 23,570 | 6,887 | 29.2% |

## When observed dollars arrived

This dollar split uses elapsed days and retains partial windows. It describes recorded timing; unlike the complete-window table, it does not compare equal customer exposure.

| Days since entry | Rows | Customers | Reported dollars | Share of total |
| --- | --- | --- | --- | --- |
| day 0 | 23,951 | 23,570 | $784,560.61 | 31.4% |
| days 1-30 | 5,806 | 4,115 | $212,089.77 | 8.5% |
| days 31-90 | 7,186 | 4,504 | $268,599.37 | 10.7% |
| days 91-180 | 8,247 | 4,644 | $312,184.99 | 12.5% |
| days 181-365 | 14,790 | 6,134 | $564,083.00 | 22.6% |
| days 366+ | 9,679 | 4,528 | $358,797.89 | 14.4% |

## Customer-dollar distribution and concentration

Customers are ranked by the **sum of their recorded dollars** through the cutoff, not by number of transactions. The ranking includes 68 customers with zero recorded dollars. Observed histories have unequal lengths. High spenders are identified in hindsight; their future presence cannot be assumed.

| Measure | Observed dollars |
| --- | --- |
| Mean per customer | $106.08 |
| Median per customer | $43.40 |
| 90th percentile | $242.33 |
| 99th percentile | $919.24 |
| Largest customer total | $13,990.93 |

| Rank by observed customer dollars | Customers | Lowest group total | Group dollars | Share of cohort |
| --- | --- | --- | --- | --- |
| Top 1% | 236 | $919.24 | $396,944.17 | 15.9% |
| Top 10% | 2,357 | $242.35 | $1,273,728.95 | 50.9% |

The largest 697 individual transaction rows (top 1% of rows) total $176,850.01, or 7.1% of recorded dollars. This checks whether a small set of unusually large *rows* dominates the cohort total; it does not identify who placed the transactions.

## Timing among observed spending groups

The top 1% and next 9% are selected by **total observed dollars**, not row count, using their *entire observed* history. This table tests an opening-stock-up explanation for their recorded totals, but does not forecast which new customers will join those groups.

| Group | Customers | Total dollars | Entry-date dollars | Entry % | After day 90 | After day 90 % |
| --- | --- | --- | --- | --- | --- | --- |
| top 1% | 236 | $396,944.17 | $23,197.25 | 5.8% | $285,745.07 | 72.0% |
| next 9% | 2,121 | $876,784.78 | $133,590.92 | 15.2% | $547,000.48 | 62.4% |
| bottom 90% | 21,213 | $1,226,586.68 | $627,772.44 | 51.2% | $402,320.33 | 32.8% |

## Interpretation for the decision meeting

The cohort generated substantial later-date sales, but most were not within 30 days of entry. Its top observed spenders bought repeatedly rather than deriving most recorded dollars from their entry date. These findings support examining persistent revenue; they do not establish why customers returned, whether other cohorts will behave similarly, or what remains after acquisition and service costs. Future-cohort and repayment scenarios need explicit downside assumptions and separate eligibility rules.

Comparable CDnow cohorts with the same definition and follow-up would be more useful than comparisons with differently defined company-wide measures.
