# CDnow transaction amounts and contemporary CD prices

**Decision-date frame: July 15, 1998.** The supplied file contains the Q1 1997 customer cohort's transactions through June 30, 1998. It records a CD count and total dollars on each row, but no album title, individual item price, discount, shipping charge, or tax field. This report measures **reported transaction dollars divided by recorded CD count**, which is an *implied amount per CD on a row*, not a verified CDnow shelf price. All 69,659 source rows are retained under the [measurement contract](../docs/cohort_measurement_contract.md) and [exception review](../docs/exception_review.md). The calculation is reproducible with `python scripts/cd_price_comparison.py`; its [JSON output](cd_price_comparison.json) identifies the source file and gives the exact row counts and source-line examples.

## What the transaction file shows

Each row gets one value: its reported dollars divided by its number of CDs. The **median** is the middle row value when rows are sorted, so a five-CD row has the same weight as a one-CD row. The middle half of rows lies between the stated 25th and 75th percentiles. These are distributions of *recorded transaction amounts*, not distributions of album list prices.

| Rows included | Rows | Minimum implied dollars/CD | Median | Maximum | Middle half |
| --- | ---: | ---: | ---: | ---: | ---: |
| All rows, January 1997–June 1998 | 69,659 | $0.00 | $13.99 | $305.99 | $12.27–$15.49 |
| Positive-dollar rows, same period | 69,579 | $0.99 | $13.99 | $305.99 | $12.28–$15.49 |
| Positive-dollar **one-CD** rows, same period | 31,374 | $1.63 | $14.37 | $305.99 | $11.88–$15.96 |
| Positive-dollar **one-CD** rows, June 1998 only | 787 | $2.99 | $13.99 | $95.49 | $11.89–$16.49 |

There are **80 zero-dollar rows**, each recording one CD. The lowest positive implied amount across *all* rows comes from **two CDs for $1.98** (source line 12,553, September 9, 1997). The lowest positive one-CD row reports **$1.63** (line 34,739, May 16, 1997). The maximum is **one CD for $305.99** (line 57,537, March 24, 1998). Among positive one-CD rows, 404 are below $5 and 69 are above $100. The file does not identify whether these reflect promotions, special products or sets, fees, coding conventions, or errors. We retain them and do not describe the minimum or maximum as an ordinary CD price. The one-CD subset avoids averaging several recorded CDs together, but it still does not identify the product or explain what the dollar field includes.

The June 1998 one-CD median of **$13.99** is the closest transaction-file comparison to the June market check below. It covers only purchases by this **Q1 1997 cohort**, not all CDnow sales in June, and its products need not match the products in that check. The file cannot establish whether transaction dollars include shipping or tax.

## What a buyer could observe by July 15, 1998

On **June 12, 1998**, CBSNews.com staff published [“Online CD Stores Offer Discounts”](https://www.cbsnews.com/news/online-cd-stores-offer-discounts/), with research credited to Laurie Kulikowski. They priced the *same selected basket of ten bestselling album titles* at five online sellers and one Manhattan Tower Records store. The online figures **include shipping**. Dividing each basket total by ten gives the following cost per selected title; it is not a median price or an estimate for every album each store sold.

| Retailer in CBS check | Ten-title basket total | Cost per selected title |
| --- | ---: | ---: |
| CDnow | $151.59 | $15.16 |
| Amazon | $156.61 | $15.66 |
| Music Boulevard | $158.78 | $15.88 |
| K-tel | $159.11 | $15.91 |
| Tower Records Online | $169.89 | $16.99 |
| Tower Records, Manhattan store | $176.90 | $17.69 |

CDnow had the lowest **delivered ten-title basket cost in this check**. This supports the narrower claim that CDnow could price competitively on those titles at that time. The selected bestsellers, basket size, shipping treatment, and single store location prevent a claim that CDnow was cheapest across its whole catalog or for every buyer. The in-store figure has no shipping charge. We also cannot directly subtract the dataset's $13.99 June median from CBS's $15.16: the former is a one-cohort distribution of one-CD transaction amounts, while the latter is the mean delivered cost of a selected ten-title basket.

**Checkout charges remain an open question.** The transaction file does not separate item price, postage, or tax. Dated order receipts or a contemporaneous CDnow checkout policy would be needed to determine those amounts for actual orders.

## What this can change in the investment judgment

The observed amounts are consistent with many transactions implying amounts in the teens per CD, while the CBS check shows that CDnow was pricing competitively for one selected basket. **This is evidence about the customer-facing price environment, not CDnow's gross margin or profit.** Discounts might help attract buyers while leaving less cash after buying and delivering each CD. The transaction file cannot resolve that tradeoff. Before using price to size a cohort advance, ask CDnow for item-level sale prices and discounts, whether transaction dollars include shipping and tax, product costs, fulfillment and shipping costs, returns, and any change in product mix or pricing across cohorts. Test whether a lower selling price raises cohort volume enough to offset weaker contribution per sale; do not assume the June comparison applies to future customers.

### Source checks and limits

- **Dataset:** [CDNOW_master.txt](../CDNOW_data/CDNOW_master.txt), described by its [readme](../CDNOW_data/read_me_CDNOW_master.txt), through June 30, 1998. The script checks the saved SHA-256 [manifest](../docs/source_manifest.json) and reconciles 69,659 rows and $2,500,315.63 before writing results. The readme names the four fields but does not define shipping, tax, item identity, or promotional treatment.
- **CBSNews.com staff, “Online CD Stores Offer Discounts,” June 12, 1998:** original dated [CBS page](https://www.cbsnews.com/news/online-cd-stores-offer-discounts/), price table and album list; research credit to Laurie Kulikowski. It is CBS's observed ten-title comparison, not CDnow company data or a representative market survey. Shipping is included for online sellers; the Manhattan store is one location.

The [historical source audit](../docs/historical_source_audit.md) records the article's original date, attribution, supporting passage, and exclusions made during review.
