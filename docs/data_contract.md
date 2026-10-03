# CDnow raw-data contract

## Source and scope

The source is [`CDNOW_data/CDNOW_master.txt`](../CDNOW_data/CDNOW_master.txt), described by [`CDNOW_data/read_me_CDNOW_master.txt`](../CDNOW_data/read_me_CDNOW_master.txt). The readme says the file contains the complete purchase history **through the end of June 1998** for people whose **first-ever CDnow purchase was in Q1 1997**. We interpret Q1 as the calendar period January 1–March 31, 1997; that interpretation should be stated when testing cohort membership. A line represents one reported transaction for one customer, not a customer summary.

The readme reports **69,659 transaction records** and **23,570 customers**. These are source claims to verify during data validation. The expected earliest cohort-entry window is January 1–March 31, 1997; the expected observation cutoff is June 30, 1998. Neither statement proves that every row or customer in the file meets those expectations.

The readme cites a 2001 paper. That citation documents the dataset's later use; the investment recommendation uses only external information published by July 15, 1998. The later paper is not a source for the historical judgment.

## Physical format and fields

Inspection of the supplied file shows no header and variable whitespace between four fields. The field order and meanings come from the readme. The displayed formats are observations of the source file; they are not yet validation results for every row.

| Position | Field | Source representation | Meaning and handling |
| --- | --- | --- | --- |
| 1 | Customer ID | Text such as `00001` | Identifies the customer within this file. Preserve leading zeroes; do not treat it as an order ID. |
| 2 | Transaction date | Eight digits such as `19970101` | Calendar date in `YYYYMMDD` form. The file provides no time of day or cash-collection date. |
| 3 | CDs purchased | Integer-looking text such as `1` | Number of CDs in the reported transaction. |
| 4 | Transaction dollar value | Decimal-looking text such as `11.77` | Reported transaction dollars, not profit or cash received. |

Example source line: `00001 19970101  1   11.77`.

The four fields do not include an order ID, acquisition channel, acquisition cost, product cost, fulfillment cost, refund status, or repayment eligibility. Multiple rows for a customer on one date, including identical-looking rows, may be separate transactions. Do not deduplicate them solely from these fields.

## Preservation and traceability

Do not edit or normalize the source file in place. Derived raw, staged, cleaned, and rejected outputs must retain a one-based source line number so each record can be traced to the original text. Keep malformed lines in a rejection or exception output; do not silently discard them. Any correction or exclusion must be documented with its reason and its effect on downstream totals.

[`source_manifest.json`](source_manifest.json) records the current file's byte size, physical line count, and SHA-256 digest. Reproduce or check it from the repository root with:

```powershell
python scripts/source_manifest.py
python scripts/source_manifest.py --check
```

These measurements identify the file used for this assessment. They do not establish that its contents satisfy the readme's claims; those checks belong to the later validation work.
