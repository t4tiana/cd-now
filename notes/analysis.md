# CDnow Cohort Data: What We Can and Cannot Conclude

## Evidence and falsification standard

Guide all analysis by the principle: **try to falsify beliefs rather than confirm them**. Treat conclusions as claims to test, not as premises to defend.

- State material assumptions explicitly and distinguish them from facts directly observed in the data or documented by a source.
- Support factual claims with evidence. Record enough source information to trace each material claim back to its dataset field, calculation, document, or contemporaneous reference; cite or name that source when presenting the claim.
- For calculations, make the inputs, definitions, time period, and method clear enough that another reader can reproduce or challenge the result.
- Actively look for evidence and plausible cases that would weaken or overturn the current interpretation. Include credible alternative explanations and downside scenarios, not only evidence consistent with the preferred conclusion.
- Label forecasts and inferences as such, show the assumptions they depend on, and avoid presenting them as established facts. If evidence is unavailable or insufficient, say so rather than filling the gap with an unsupported assertion.
- Keep the historical decision frame: use information available at the time for the investment judgment. Any later source used for general analytical methods must be identified as later and must not introduce hindsight about subsequent market outcomes.

## Available evidence and follow-up

Assume the supplied Q1 1997 transaction file is the only CDnow dataset available for this assessment. Proceed with analysis and a conditional recommendation using it; do not wait for further company data. Place missing decision-critical company inputs in a prioritized follow-up list in the written output, stating which conclusion each could change. Public sources may provide contemporaneous market context or clearly labeled proxies, but cannot establish CDnow's own acquisition costs, margins, refunds, or contractually eligible revenue. Apply the historical source rule above to all public research.

## Scope of the investment memo

The interview deliverable should demonstrate judgment with limited evidence, not imitate a legal agreement. Define the proposed cohort and the repayment-base assumption clearly enough to model the 50% share and 1.2x cap. Discuss a contract ambiguity in the memo when it could change the forecast, advance, repayment timing, or recommendation; state the assumption, show a sensitivity if useful, and add the unresolved point to follow-up. Leave detailed clauses and immaterial edge cases out of the main recommendation. Keep the emphasis on revenue quality, future-cohort scenarios, whether and how much to advance, and the missing facts most likely to change that view.

## Validate and document the data

Progress tracker for the first phase of the assessment. The supplied transaction file is the only CDnow dataset available. Update each row when its work starts, reaches an intermediate state, or is complete. Use **Done** only when its completion evidence exists; link to that evidence or explain a blocker in the progress cell. Keep the raw file unchanged. No analysis of cohort behavior should rely on records silently dropped or altered during this phase.

### 1. Establish the raw-data contract

| ID | Task and completion evidence | Progress |
| --- | --- | --- |
| 1.1 | Document the source and its meaning: one record is a reported transaction for a customer in the Q1 1997 first-purchase cohort, observed through June 1998. Cite the dataset readme. | Done — [data contract](../docs/data_contract.md#source-and-scope) |
| 1.2 | Document the four fields, their order, and the source format: customer ID, `YYYYMMDD` transaction date, CD count, dollar value; no header and variable whitespace. Preserve leading zeroes in IDs. | Done — [field contract](../docs/data_contract.md#physical-format-and-fields) |
| 1.3 | Record the readme's expected 69,659 transactions and 23,570 customers, and the expected first-purchase and last-observation date ranges. Label these as source claims to verify. | Done — [source claims](../docs/data_contract.md#source-and-scope); validation remains in section 4 |
| 1.4 | Record the raw file's byte size, line count, and cryptographic hash in a reproducible source manifest. | Done — [manifest](../docs/source_manifest.json) and [reproduction script](../scripts/source_manifest.py); `--check` passed |
| 1.5 | State the preservation rule: never edit the supplied file; all parsed, cleaned, and rejected records are derived outputs traceable to source lines. | Done — [preservation rule](../docs/data_contract.md#preservation-and-traceability) |
| 1.6 | State the transaction-grain caveat: no order ID is supplied, so identical-looking rows or multiple purchases on one day are not automatically duplicates. | Done — [grain caveat](../docs/data_contract.md#physical-format-and-fields) |

### 2. Build a lossless raw load

| ID | Task and completion evidence | Progress |
| --- | --- | --- |
| 2.1 | Implement a Python 3.12+ reader that processes each physical line and retains its one-based line number and original text. | Done — [loader](../scripts/load_raw.py); all 69,659 stored lines matched the source exactly |
| 2.2 | Split each line on whitespace into four original field strings when possible; mark blank, short, or extra-field lines with a parse status and reason. | Done — [parser](../scripts/load_raw.py) and [raw-load notes](../docs/raw_load.md); malformed-line cases checked |
| 2.3 | Load the raw records into local DuckDB, using a small dlt pipeline if it remains straightforward. Retain source-line traceability and raw strings in the stored data. | Done — [DuckDB raw table](../docs/raw_load.md#queryable-outputs); direct bulk import used after dlt initialization proved slow here |
| 2.4 | Make reruns idempotent: rebuilding the raw table must not append a second copy of the same file. | Done — loader replaces the table; two runs returned the same [counts](../reports/raw_load.json) |
| 2.5 | Retain lines that fail the four-field format check in a separate queryable table or report with line number, original text, and reason. Do not silently skip them. | Done — `cdnow_raw.malformed_lines` view; [query and fields](../docs/raw_load.md#queryable-outputs) |
| 2.6 | Reconcile physical input lines to four-field records plus malformed lines, and report the three counts. | Done — [raw-load report](../reports/raw_load.json): 69,659 = 69,659 + 0 structurally malformed lines; field values remain unvalidated |

### 3. Convert fields into a typed staging model

| ID | Task and completion evidence | Progress |
| --- | --- | --- |
| 3.1 | Create a dbt staging model on DuckDB that preserves the source-line number and identifies the input record. | Done — [staging model](../dbt/models/staging/stg_cdnow_transactions.sql) and [input identifier](../docs/staging.md); `dbt run` passed |
| 3.2 | Preserve `customer_id` as a string so leading zeroes are not lost. | Done — [column rule](../docs/staging.md); first source ID staged as `00001` |
| 3.3 | Parse `transaction_date` from `YYYYMMDD` to a real calendar date, with an identifiable failure when parsing is impossible. | Done — [conversion and issue columns](../docs/staging.md) |
| 3.4 | Convert CD count to an integer and transaction dollars to an exact decimal type, without floating-point rounding of cents. | Done — [types and conversion rules](../docs/staging.md); DuckDB reports `INTEGER` and `DECIMAL(18,2)` |
| 3.5 | Make failed conversions visible in raw data and in a rejection or exception output; do not replace missing or invalid values with zero. | Done — raw strings remain in [staging](../dbt/models/staging/stg_cdnow_transactions.sql), with [queryable rejection view](../dbt/models/staging/stg_cdnow_rejections.sql); 0 conversion exceptions in current file |
| 3.6 | Document each staged column, its source field, its type, and any conversion rule. | Done — [staging column contract and reconciliation](../docs/staging.md) |

### 4. Run validity checks

| ID | Task and completion evidence | Progress |
| --- | --- | --- |
| 4.1 | Check each nonblank line has exactly four fields; report malformed and blank lines with source-line numbers. | Done — [structure results](../docs/validity_checks.md) and [source-line queries](../reports/data_quality.json): 0 malformed or blank |
| 4.2 | Check customer IDs are present and have the expected form; count distinct IDs. Do not assume gaps in ID numbering are bad records. | Done — [ID results](../docs/validity_checks.md): 23,570 distinct, 0 missing or wrong-form |
| 4.3 | Check dates parse and fall within January 1, 1997 through June 30, 1998; report out-of-range dates. | Done — [date results](../docs/validity_checks.md): 0 unparseable or out-of-range |
| 4.4 | Check every customer's earliest recorded purchase falls in Q1 1997, using the stated cohort definition. | Done — [cohort entry result](../docs/validity_checks.md): 0 outside Q1 1997 |
| 4.5 | Check CD counts are valid positive integers; report zero, negative, fractional, or unparseable values. | Done — [CD-count results](../docs/validity_checks.md): 0 in each invalid category |
| 4.6 | Check dollar values parse as decimals; report zero, negative, non-cent precision, or unparseable values for review rather than automatically deleting them. | Done — [dollar results](../docs/validity_checks.md): 80 zero-dollar rows retained; other invalid categories 0 |
| 4.7 | Reconcile typed transaction count and distinct customer count against the raw load and the readme's expected counts. | Done — [reconciliation](../docs/validity_checks.md): 69,659 rows and 23,570 customers match |
| 4.8 | Check that the load has not repeated any source line or transaction through reruns. | Done — [load-identity check](../docs/validity_checks.md): unique source lines and record IDs, 0 raw/staged mismatches after rerun; source-level repeated-looking rows remain flagged in 4.9 |
| 4.9 | Profile exact repeated rows and multiple records for the same customer on the same date; flag them without automatic deduplication. | Done — [repeat profiles](../docs/validity_checks.md) and [line queries](../reports/data_quality.json); no rows removed |
| 4.10 | Profile unusually large CD counts and dollar values, plus gaps in transaction dates and customer IDs; document thresholds and counts without automatic exclusions. | Done — [thresholds and profiles](../docs/validity_checks.md) and [line queries](../reports/data_quality.json) |

### 5. Decide and document every exception

| ID | Task and completion evidence | Progress |
| --- | --- | --- |
| 5.1 | Produce a data-quality report listing every check, its result, affected line numbers or a reproducible query for them, and any unresolved question. | Done — [readable report](../docs/validity_checks.md), [all results and line queries](../reports/data_quality.json), and [open questions](../docs/exception_review.md) |
| 5.2 | Assign a disposition to each finding: retain, exclude from typed analysis, correct with a documented rule, or unresolved. Explain the reason. | Done — [disposition table](../docs/exception_review.md); all current rows retained, business interpretations unresolved |
| 5.3 | Preserve plausible transactions, including identical-looking records, unless evidence supports a different treatment. | Done — [repeat-row decision](../docs/exception_review.md); no deduplication applied |
| 5.4 | Isolate structurally invalid records without erasing them from the raw load or reconciliation. | Done for current file — 0 structural failures; [raw malformed view](../docs/raw_load.md#queryable-outputs) and [staging rejection view](../docs/staging.md) preserve the isolation path for future input |
| 5.5 | Do not infer missing purchases, refunds, or cancellations from the transaction file. Record these as data limits. | Done — [unresolved data limits](../docs/exception_review.md) |
| 5.6 | Show the effect of each exclusion or correction on transaction count, customer count, and revenue totals used later. | Done — [impact report](../reports/exception_impact.json) and [explanation](../docs/exception_review.md); no applied change, two unadopted sensitivities quantified |

### 6. Make it repeatable

| ID | Task and completion evidence | Progress |
| --- | --- | --- |
| 6.1 | Organize the loader, dbt staging model and tests, pytest tests, quality report, configuration, and documentation into clear project files. Adjust the layout as needed rather than forcing a single-file solution. | Done — [scripts](../scripts), [dbt models and tests](../dbt), [pytest cases](../tests/test_raw_parser.py), [reports](../reports), and [README](../README.md) |
| 6.2 | Declare and pin or constrain the Python dependencies needed for the pipeline; use a local DuckDB file and avoid requiring MotherDuck credentials. | Done — [pipeline dependencies](../requirements-dbt.txt), [development checks](../requirements-dev.txt), and [local profile](../dbt/profiles.yml); no MotherDuck credentials |
| 6.3 | Write README setup and run commands that rebuild the derived data and quality report from the committed source file. | Done — [setup, rebuild, and check commands](../README.md) |
| 6.4 | Add focused pytest cases for parsing and malformed inputs, and dbt tests for staged data invariants. | Done — [3 pytest cases](../tests/test_raw_parser.py) and [7 passing dbt tests](../dbt/tests) |
| 6.5 | Configure and run applicable ruff, pyright, sqlfmt, and pre-commit checks; record any tool intentionally deferred and why. | Done — [local hook configuration](../.pre-commit-config.yaml), [Pyright config](../pyrightconfig.json); Ruff, Pyright, sqlfmt, pytest, and dbt passed in pre-commit; no tool deferred |
| 6.6 | Perform a clean rerun and verify that counts, source hash, exceptions, and quality report are reproducible, and that every reported record traces to a source line. | Done — rebuilt after removing the derived DuckDB file; [verification script](../scripts/verify_phase1.py) matched all 69,659 stored original lines to source, checked 19 line queries, and all three [reports](../reports) regenerated byte-for-byte identically |

## Dataset described by the readme

The dataset contains the purchase history through the end of June 1998 for 23,570 customers whose first-ever CDnow purchase was in Q1 1997. It has 69,659 transaction records. Each record contains a customer ID, transaction date, number of CDs purchased, and transaction dollar value.

This is a single acquisition cohort with a finite observation window. It supports analysis of this cohort's observed purchasing behavior, but it is not a complete set of inputs for cohort profitability or the proposed financing decision.

## What we can calculate from this file

- **Observed cohort revenue over time:** Sum transaction dollar values by calendar period or by time since each customer's first purchase.
- **Repeat purchasing and retention patterns:** Count customers who make another purchase, how many transactions they make, and when purchases occur. Define “active” carefully—for example, a purchase during a quarter—because the data does not say whether a customer was still engaged between purchases.
- **Revenue and purchase frequency distributions:** Measure observed spend, transaction counts, CDs purchased, and how these vary across customers and over time.
- **Observed revenue concentration:** See how much revenue comes from repeat buyers or other segments defined from purchase behavior. This describes the observed cohort, not necessarily future customers.
- **A limited historical forecast for this cohort:** Use its purchase history to estimate future purchases or revenue, with explicit assumptions and uncertainty. The window is finite, so longer-term lifetime value is not directly observed.

## What we cannot establish from this file alone

- **Comparisons across acquisition cohorts or channels:** There is only one first-purchase cohort and no acquisition-channel information. We cannot tell whether Q1 1997 customers were better or worse than other CDnow cohorts or marketing sources.
- **Customer acquisition cost or marketing efficiency:** No marketing spend or channel cost is included. So we cannot calculate CAC, compare customer value with acquisition cost, or judge whether the proposed advance is appropriately sized.
- **Contribution margin or profitability:** Transaction dollars are not profit. The file lacks CD costs, shipping and fulfillment costs, payment fees, returns/refunds, support expense, overhead, and other relevant costs.
- **Cash payback or investor return:** Transaction dates and amounts show sales recorded, but not necessarily when cash was collected or how refunds and adjustments were handled. The file also does not establish which sales are contractually eligible for repayment, or the advance amount and date needed to model repayment timing and the 1.2x cap.
- **Whether this cohort represents future customers or CDnow overall:** A single cohort cannot establish future-cohort behavior or company-wide economics. We need results for other cohorts and business context.

## Interpretation limits

The file covers every purchase for the specified 23,570-person cohort through June 1998, but each customer has a different effective follow-up period depending on when their first purchase occurred. Also, “first-ever purchase” is how the dataset defines cohort entry; it does not show when or how those customers were acquired through marketing.

The analysis can therefore describe **observed cohort revenue and repeat-purchase behavior**, and support a **conditional forecast**. It cannot by itself show whether the cohort generated enough contribution to repay an advance or whether future cohorts will behave similarly.

## Highest-impact follow-up requests for the written recommendation

- Acquisition spend by cohort and marketing channel, plus channel mix.
- Gross margin and costs of CDs, fulfillment, shipping, payment processing, and customer support.
- Returns, refunds, cancellations, and how those are reflected in the transaction file.
- Comparable purchase histories and economics for other acquisition cohorts.
- Cohort attribution rules, revenue eligibility under the financing agreement, and cash collection mechanics.
- Proposed advance amount and timing, to model repayment timing against the 50% revenue share and 1.2x repayment cap.

These inputs could change the investment decision. Include them as follow-up requests in the output, prioritized by how much they could alter estimated cohort contribution, repayment timing, or likelihood of reaching the cap. Continue the analysis with explicit assumptions and downside cases rather than waiting for them.
