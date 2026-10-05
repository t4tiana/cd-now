# Phase 2 findings: the Q1 1997 CDnow cohort

**Decision-date frame: July 15, 1998.** This note describes the 23,570 customers whose first recorded CDnow purchase was in Q1 1997, using their 69,659 transaction rows through **June 30, 1998**. The file reports **$2,500,315.63 in transaction dollars**. Those dollars are recorded sales amounts, not cash collected, profit, forecast revenue, or revenue eligible for the proposed investor repayment. A transaction row is not a verified distinct order. Definitions, source identity, and full calculations are in the [measurement contract](../docs/cohort_measurement_contract.md), [machine-readable output](cohort_analysis.json), and [detailed tables](cohort_tables.md).

## What the cohort shows

Recorded purchases continued well after customers' first purchase. That supports further study of repeat revenue, but the file ends before any customer's full buying life is known.

| Measure through June 30, 1998 | Observed result | Denominator or definition |
| --- | ---: | --- |
| Customers with a transaction on a later **date** | 11,516 (48.9%) | All 23,570 customers; extra rows on the first date do not count as repeats. |
| Reported dollars on dates after each customer's first date | $1,715,755.02 (68.6%) | All $2,500,315.63 of reported cohort dollars. |
| Reported dollars more than 90 days after first date | $1,235,065.88 (49.4%) | All $2,500,315.63 of reported cohort dollars; this timing split includes partially observed windows. |
| Dollars from the 2,357 highest-spending customers (top 10%) | $1,273,728.95 (50.9%) | All $2,500,315.63; customers are ranked using their *entire observed history*. |

Among the 11,516 customers with a later-date transaction, the median time to the first such date was 57 days. The other 12,054 had **no later-date transaction observed by the cutoff**; they should not be called permanently lost customers. Only one later-date repeater had no positive-dollar later-date row. Zero-dollar and repeated-looking rows remain in the analysis because the file does not establish that they are errors.

The like-aged view also shows activity well beyond entry. Each row below counts only customers whose **entire** 30-day window was observable by June 30; all 23,570 qualify for these selected windows. The percentages count customers with at least one recorded row in that window, including a zero-dollar row. They do not count the same set of buyers in every window.

| Days after first recorded date | Customers with a row | Share of 23,570 |
| --- | ---: | ---: |
| 30–59 | 3,088 | 13.1% |
| 180–209 | 1,868 | 7.9% |
| 360–389 | 1,741 | 7.4% |
| 420–449 | 1,560 | 6.6% |

**Concentration limits the inference.** The top 236 customers by total recorded dollars (top 1%) contributed $396,944.17, or 15.9% of all cohort dollars. The largest 1% of individual transaction rows contributed only 7.1%, so a few unusually large *rows* do not explain the whole cohort total. But we identified the highest-spending customers using purchases made throughout the observation period. We could not have known at entry who would join that group, or whether a future cohort would contain a similar group. Their observed spending is therefore not a forecast.

## How to interpret this in July 1998

One explanation is that customers valued CDnow's catalog or service enough to return. Another is that promotions, acquisition channels, or a small number of unusually active buyers account for much of the repeat spending. Customer IDs may also combine different buying patterns. The transaction file cannot separate these explanations. The top-spender concentration makes a weaker future cohort a serious case to test, even though repeat purchases in this cohort are real recorded observations.

The company's broader trajectory does not settle that question. A [May 3, 1998 report](https://www.stereophile.com/content/cdnow-tops-chart-expands-europe) relayed CDnow's $10 million Q1 1998 company-wide revenue and 135,000 added **registered** customers since January 1. Registration does not establish a purchase, and neither number measures this cohort's acquisition cost. Separately, [February 1998 reporting of the RIAA's 1997 figures](https://www.stereophile.com/content/riaa-releases-1997-year-end-music-sales-statistics) found retail shipments of full-length CDs up 2.3%; manufacturer shipments are a different measure from CDnow customer purchases. The [historical source audit](../docs/historical_source_audit.md) records provenance and supporting passages for these and the other external claims below.

The [CD price comparison](cd_price_comparison.md) finds a **$13.99 median in the 787 positive-dollar, one-CD rows from June 1998**. This is a transaction amount from the supplied cohort, not a verified album price. In a [June 12 CBS comparison](https://www.cbsnews.com/news/online-cd-stores-offer-discounts/), CDnow had the lowest delivered cost for a selected ten-title basket among five online stores. The file does not identify titles or separate item price, shipping, and tax, so the two differently defined measures cannot establish CDnow's catalog-wide pricing advantage or its margin.

**Distribution agreements matter for later cohorts.** Lycos was a substantial source of potential customer exposure in early 1998. A [report published April 6](https://www.wired.com/1998/04/search-engine-stocks-rev-up/) cited RelevantKnowledge's February count of **10.3 million monthly unique visitors to Lycos**, eighth among the websites it ranked; Yahoo/Four11 led that measure with 31.9 million. The same report cited a *different* firm, Media Metrix, estimating that **22.6% of measured web users visited Lycos at least once in a month**, versus 42.9% for Yahoo and 24.8% for Excite. These are estimates of audience reach, not music shoppers or CDnow customers; the firms' measures should not be combined.

An [April 10 report by Jennifer Sullivan](https://www.wired.com/1998/04/dealing-for-dollars/) described CDnow's **three-year, $18.5 million** Lycos agreement and a further **$5.5 million** for Lycos Bertelsmann in Europe, plus an expanded Yahoo promotion. [May 3 reporting](https://www.stereophile.com/content/cdnow-tops-chart-expands-europe) described the Lycos/Tripod relationship as exclusive music retail placement. These are multi-year company commitments, **not** the cost of acquiring the Q1 1997 cohort or an amount to assign to one future quarter. Prominent placement could bring more first-time buyers, but the reports do not establish how many will buy, return, or generate enough revenue after product and service costs to justify the spending.

CDnow had other important distribution relationships. A [February 11 report](https://www.wired.com/1998/02/cdnow-goes-to-market/) named Yahoo, Excite, GeoCities, Pathfinder, and The Globe as CDnow traffic sources and described Music Boulevard's competing exclusive placement within AOL's MusicSpace. [April 10 reporting](https://www.wired.com/1998/04/dealing-for-dollars/) confirms that CDnow expanded its Yahoo promotion, but does not establish that CDnow was Yahoo's exclusive music retailer across the whole site. A [May 20 CBS MarketWatch report by Frank Barnako](https://www.cbsnews.com/news/cdnow/) described a separate three-year MTV/VH1 marketing agreement worth about **$22 million** in cash and stock. That report does not establish how many customers the agreement would bring or how much they would spend. Test the return from each channel rather than infer sales from a partner's name or total audience.

The supplied cohort first bought in Q1 1997, before the Lycos agreement, and its file has no source-of-customer field. The later forecast should therefore treat portal-driven cohort size and repeat behavior as explicit, uncertain assumptions. The financing analysis should examine the timing and allocation of these marketing commitments and the revenue actually eligible for repayment. Neither the announcements nor the observed Q1 1997 purchases show that a later cohort can repay an advance.

## Information most likely to change the judgment

1. **Comparable quarterly cohorts, at the same customer ages, with acquisition channel and promotion mix.** Include customers arriving through Lycos, Yahoo, MTV, and other partners, with referred visits, first purchases, and later purchases where available. These would test whether the observed repeat pattern and high-spender share carried into customers acquired later. Without them, transferring this cohort's behavior into a future-cohort forecast is an assumption.
2. **Acquisition spending by cohort and channel, including each partnership's payment schedule and allocation, plus product cost, shipping, fulfillment, payment, support, and return costs.** These would show what remains after acquiring and serving customers. The transaction file cannot establish customer acquisition cost, contribution, or a sensible advance size.
3. **Order and refund records, customer-ID rules, collected-cash timing, and the proposed eligible-revenue and advance-timing rules.** These could change recorded sales and the timing or amount of the investor's 50% share. The 1.2× cap cannot be assessed from reported dollars alone.

This is an **observed-cohort finding**, not a recommendation to invest or a forecast. The later forecast must test a materially weaker repeat or high-spender case and state any assumption that applies this cohort to future customers. This historical assessment does not account for large-scale changes in how media is distributed, shared, or consumed.

The [early-90-day diagnostic](early90_diagnostic.md) now groups customers using only purchases visible in their first 90 days and compares days 90–449 at equal follow-up. It tests whether an early signal is associated with later spending in this cohort. Other cohorts and acquisition-channel data would be needed before using that signal to size a future advance.
