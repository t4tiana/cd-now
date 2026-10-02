# Step 5: exception decisions

This review uses the [step 4 validity results](validity_checks.md). A disposition here decides how to handle a **source row for typed analysis**; it does not establish cash collected, economic contribution, or revenue eligible for the proposed repayment agreement. Every row remains traceable by one-based source line in `cdnow_analysis.stg_cdnow_transactions`.

| Finding | Source-row disposition | Reason and unresolved question |
| --- | --- | --- |
| 80 rows with a positive CD count and $0.00 | **Retain** with reported dollars equal to zero | They parse correctly. A promotion, adjustment, or recording convention is possible; CDnow must explain them and whether they count as purchases or eligible repayment revenue. Do not impute a price. |
| 215 exact four-field repeat groups (470 rows), including 255 rows beyond one per group | **Retain all** | Four matching fields do not identify an order. Ask for order IDs or ledger records before calling them duplicates. |
| 1,774 customer/date groups with multiple rows | **Retain all** | Multiple same-day purchases or lines may be real. These groups overlap the exact-repeat groups. |
| 1,113 rows with at least 10 CDs; 464 with at least $200 | **Retain all** | Thresholds are review flags only. Ask about large orders, especially source line 27633 (99 CDs, $1,286.01); no evidence currently supports correction. |
| Blank, malformed, or failed-conversion lines | **No current finding** | The count is zero. If later input has one, keep it in `cdnow_raw.source_lines` and the malformed or staging-rejection view; exclude it from typed behavior calculations until reviewed. |
| Missing purchases, refunds, and cancellations | **Unresolved data limit** | This file cannot show omitted activity or explain whether adjustments are included. Do not invent records or infer a refund from a zero-dollar line. Request the transaction and refund conventions. |

No source row was corrected, excluded, or deduplicated. The [impact script](../scripts/exception_impact.py) writes [exact totals and sensitivities](../reports/exception_impact.json):

| Scenario | Transaction rows | Customers | Sum of reported transaction dollars |
| --- | ---: | ---: | ---: |
| **Chosen: retain all source rows** | 69,659 | 23,570 | $2,500,315.63 |
| Change actually applied | 0 | 0 | $0.00 |
| Unadopted: remove all zero-dollar rows | 69,579 | 23,502 | $2,500,315.63 |
| Unadopted: keep one row per exact four-field combination | 69,404 | 23,570 | $2,495,982.75 |

The zero-dollar exclusion would remove **68 customers with no other recorded row**. The hypothetical exact-match deduplication would remove 255 rows and $4,332.88 of reported revenue. Neither exclusion is justified by the available fields. The scenarios are separate and should not be combined by adding their differences.

For later cohort analysis, use the staged table with source lines retained and explicitly report the chosen treatment. If CDnow supplies evidence warranting a correction, make a new derived model, preserve the original source line, and regenerate this impact report. The $2,500,315.63 is **observed reported transaction value through June 1998**, not cash collected, profit, a forecast, or the contractual repayment base.
