# CDnow Cohort Data: What We Can and Cannot Conclude

## Evidence and falsification standard

The analysis follows this principle: **try to falsify beliefs rather than confirm them**. Treat conclusions as claims to test, not as premises to defend.

- State material assumptions explicitly and distinguish them from facts directly observed in the data or documented by a source.
- Support factual claims with evidence. Record enough source information to trace each material claim back to its dataset field, calculation, document, or contemporaneous reference; cite or name that source when presenting the claim.
- For calculations, make the inputs, definitions, time period, and method clear enough that another reader can reproduce or challenge the result.
- Actively look for evidence and plausible cases that would weaken or overturn the current interpretation. Include credible alternative explanations and downside scenarios, not only evidence consistent with the preferred conclusion.
- Label forecasts and inferences as such, show the assumptions they depend on, and avoid presenting them as established facts. If evidence is unavailable or insufficient, say so rather than filling the gap with an unsupported assertion.
- Keep the historical decision frame: assume the memo is prepared on July 15, 1998. Use company, market, and case-economics information published by that date and verify each publication date. I clarified that general finance and statistics literature published after the cutoff may be used **for learning and method justification only**; it cannot import later facts or outcomes about CDnow or the case-study market. See the separate [methodology literature note](../docs/methodology_literature.md). The 2001 citation in the supplied readme is dataset provenance only, not a source of CDnow findings for the memo.

### External-source gate

The source notes record each cited publisher, title, available author or newsroom attribution, original publication date, URL, and passage or page supporting the exact claim. Company and market information must have been published by **July 15, 1998**; a URL date, archive date, or financial period end is not enough. Original company disclosures support company figures, and identifiable contemporaneous publications support market context. Third-party estimates remain labeled and separate from the supplied cohort.

Validate each **article's** provenance, not only the host's legitimacy. For a generic byline, uncertain syndication, or unclear original date, seek the original publication or another contemporaneous source; if none can be verified, omit or explicitly qualify the claim. Do not infer an author or wire service. For a claim that could change the investment judgment, corroborate it independently where possible and record any material disagreement. Recheck existing citations before the final recommendation. Later archive metadata can help locate a pre-cutoff source, but later reporting cannot supply CDnow or market facts for the historical judgment. General methodology literature may be newer for learning and method justification.

## Available evidence and follow-up

The supplied Q1 1997 transaction file is the only CDnow transaction dataset used in this assessment. The recommendation is conditional and lists missing decision-critical company inputs in priority order, with the conclusion each could change. CDnow disclosures and market sources published by July 15, 1998 add company-wide context or clearly labeled proxies, but cannot establish this cohort's acquisition costs, margins, refunds, or contractually eligible revenue. The observed cohort and company-wide disclosures retain distinct scopes.

## Scope of the investment memo

The investment memo should demonstrate judgment with limited evidence without imitating a legal agreement. Define the proposed cohort and the repayment-base assumption clearly enough to model the 50% share and 1.2x cap. Discuss a contract ambiguity in the memo when it could change the forecast, advance, repayment timing, or recommendation; state the assumption, show a sensitivity if useful, and add the unresolved point to follow-up. Leave detailed clauses and immaterial edge cases out of the main recommendation. Keep the emphasis on revenue quality, future-cohort scenarios, whether and how much to advance, and the missing facts most likely to change that view.

## Assessment roadmap

The five assessment phases are complete. Data validation, observed-cohort measurement, forecast sensitivities, financing scenarios, and the committee memo are linked below. The missing company inputs remain decision conditions, not unfinished analysis steps.

1. **Validate and document the data (phase 1, complete).** Use a reproducible pipeline to check record counts, dates, customer IDs, transaction values, repeated-looking rows, and Q1 1997 cohort entry. Record unresolved questions about refunds and customer identity.
2. **Measure the observed cohort (phase 2, complete).** Calculate revenue by calendar quarter and by time since first recorded purchase, repeat-purchase rates, purchase frequency, and revenue concentration. Account for different entry dates and the June 30, 1998 observation cutoff. The [numerical verification](../docs/phase2_verification.md) and [historical source audit](../docs/historical_source_audit.md) are recorded; I chose the phase 3 forecast horizon before numerical forecasting began.
3. **Build an assumption-driven forecast (phase 3).** Show a base case and credible downside cases for this cohort's remaining revenue. Treat applying its patterns to a future quarterly cohort, including cohort size and acquisition mix, as separate assumptions requiring evidence from CDnow.
4. **Model the financing and request missing inputs (phase 4).** For an advance `A`, reaching the 1.2× repayment cap requires `2.4A` of eligible cohort revenue. Model the 50% share, cap, and repayment timing. Prioritize requests for cohort acquisition spend and channel mix, variable costs and refunds, comparable cohorts, and revenue attribution and collection rules. Make any advance recommendation conditional on the missing inputs and explicit assumptions.
5. **Write the decision memo (phase 5).** Separate observations, forecasts, and contractual repayment estimates; state the conditional recommendation, proposed advance or decision threshold, and what would change the judgment. Keep the late-1990s frame explicit, including that the analysis does not account for large-scale changes in how media is distributed, shared, or consumed.

## Phase 1: Validate and document the data

Completion record for the first phase of the assessment. The supplied transaction file is the only CDnow dataset available. Each completed row links to its evidence. Keep the raw file unchanged. No analysis of cohort behavior should rely on records silently dropped or altered during this phase.

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

## Phase 2: Measure the observed cohort

This phase describes only the supplied Q1 1997 first-purchase cohort through June 30, 1998. It must not call observed sales a customer lifetime, treat a transaction row as a verified order, or use this cohort as evidence that future cohorts will have the same size or behavior. Update progress as work proceeds; use **Done** only when a reproducible output or documented result exists.

### Agreed measurement assumptions and output

- Use all 23,570 customers and all retained source rows. Each customer's earliest recorded transaction date is their cohort entry date, not an observed marketing acquisition date. Keep zero-dollar and repeated-looking rows as recorded; show interpretation or sensitivity where they affect a measure.
- Revenue means the sum of reported transaction dollars, with no inferred refunds or cash-collection adjustment. It is not profit, cash collected, forecast revenue, or revenue eligible for investor repayment. A row is a transaction record, not a verified distinct order.
- A repeat buyer has at least one recorded transaction on a date **later** than their first recorded date. Same-day additional rows can be counted as transaction rows but do not establish a later-date repeat purchase. Report customers with no later purchase as **no repeat observed by the cutoff**, not permanently churned.
- Use calendar quarters for the calendar view and consecutive **30-day periods** from each customer's entry date for the customer-age view. This is a transparent analysis convention, not a claim about CDnow buying cycles or a business-theory threshold. Equal-length windows make customers' exposure comparable; calendar-quarter results separately retain seasonality and reporting dates. **Age zero** covers days 0–29, including the first recorded purchase; age one covers days 30–59, and so on. Revisit the width if results prove too noisy or conceal a material pattern, and disclose any change.
- June 30, 1998 is the inclusive observation cutoff. A customer belongs in an age-period denominator only if that entire 30-day period falls on or before the cutoff. A partially observed period is **censored**: retain its recorded transactions in full observed-dollar reconciliations and calendar summaries, but exclude that customer-period from like-aged rates and averages. Show the number of fully observed customers for each age period.
- For revenue concentration, rank customers by their total observed reported dollars, including zero-revenue customers, and show the share of total observed dollars generated by the top 1% and top 10%. These are descriptive shares across unequal follow-up periods, not lifetime concentration estimates.
- Deliver a **compact investment-facing findings note** with a few useful tables or charts, backed by reproducible code and detailed machine-readable results. Keep observed findings separate from phase 3 forecasts.

**Why 30 days (presentation note).** Thirty days is an explicit, equal-length analysis convention that gives roughly monthly detail across this short observation window; it is not a claimed CDnow buying cycle. An exploratory read-only query of distinct customer purchase dates in `cdnow_analysis.stg_cdnow_transactions` found that, among 11,516 customers with a later-date purchase, the median gap from first to next purchase was 57 days; this excludes nonrepeaters and is limited by the June 1998 cutoff. Use 30-day windows to show revenue timing, and check 60-day windows for repeat-buying interpretation. No later methodological publication is needed to justify this choice.

For example, suppose 100 customers entered early enough to be observed for all of days 90–119 and 20 bought in that window. Another 100 entered late enough that the June 30 cutoff leaves days 90–119 only partly visible. The comparable full-window purchase rate is 20/100 = 20%; using all 200 customers as the denominator would make the rate look too low merely because half had less time to buy. Keep transactions observed in a partial window in overall reported-dollar totals, but leave those customer-periods out of the full-window rate.

| ID | Task and completion evidence | Progress |
| --- | --- | --- |
| P2.1 | Define the analysis population and measures before computing them: all 23,570 source customers; first recorded purchase date; reported transaction dollars; transaction rows versus customers; calendar quarter versus time since first purchase; June 30, 1998 cutoff. State the treatment of zero-dollar and repeated-looking rows. | Done — [measurement contract](../docs/cohort_measurement_contract.md) defines the population, events, windows, denominators, censoring, and retained-row rules; implementation and numerical verification are P2.2–P2.8 |
| P2.2 | Build a simple reproducible analysis from the typed staging table, with commands in the README and outputs that record definitions, source manifest, period, and assumptions. Reconcile included rows, customers, and reported dollars to the phase 1 totals; explain any difference. | Done — [analysis script](../scripts/cohort_analysis.py), [output](../reports/cohort_analysis.json), and [run command](../README.md#phase-2-observed-cohort-analysis); 69,659 rows, 23,570 customers, and $2,500,315.63 match phase 1 exactly; rerun byte-identical |
| P2.3 | Report observed cohort dollars, transaction rows, and purchasing customers by calendar quarter. Show entry-quarter revenue separately from later calendar quarters, without implying that a calendar quarter gives every customer equal follow-up. | Done — [calendar-quarter output](../reports/cohort_analysis.json) covers 1997Q1–1998Q2; Q1 entry-quarter dollars are $1,071,805.47 and later-quarter dollars are $1,428,510.16; quarter rows and dollars reconcile to phase 1; customer counts are not additive across quarters |
| P2.4 | Report revenue and purchasing activity by elapsed time since each customer's first recorded purchase, using a clearly defined age unit and age-zero rule. For each age period, report how many customers had the full chance to be observed through that period; do not treat censored periods as zero spending. | Done — [customer-age output](../reports/cohort_analysis.json) gives 30-day revenue, rows, purchasing customers, rates, and eligible customers; 68,776 rows and $2,468,094.71 fall in complete windows, while 883 rows and $32,220.92 in partial windows remain in full and calendar totals |
| P2.5 | Measure repeat purchasing with explicit definitions: customers with a purchase on a later date, time to first later-date purchase, and observed transaction-row frequency. Show how same-day rows and zero-dollar entries affect the interpretation; avoid calling nonrepeaters permanently churned. | Done — [repeat output](../reports/cohort_analysis.json) records 11,516 later-date repeaters (48.9%), median 57 days to first later date among those repeaters, 30/60/90-day full-exposure horizons, row/date frequency, same-day rows, and positive-dollar sensitivity; [focused test](../tests/test_cohort_analysis.py) checks the definitions. |
| P2.6 | Show the distribution and concentration of observed customer dollars and purchases, including zero-revenue customers and a few simple upper-tail shares. Label these as amounts accumulated over unequal follow-up windows, and identify whether large transactions materially drive the results. | Done — [distribution output](../reports/cohort_analysis.json) includes 68 zero-dollar customers, dollar and row-count percentiles, top 1%/10% customer shares (15.9%/50.9%), and largest 1% transaction-row share (7.1%); all are observed-to-cutoff measures over unequal follow-up. [Focused test](../tests/test_cohort_analysis.py) checks zero-dollar inclusion and top ranking. |
| P2.7 | Produce a compact investment-facing findings note with a few tables or charts, source and calculation references, unresolved data questions, and plausible alternative explanations. Pair relevant results with the [pre-cutoff company and market context](../docs/historical_market_context.md), keeping company-wide disclosures separate from this cohort's measured results. Separate what the cohort shows from what it cannot show about retention causes, future cohorts, margins, or repayment eligibility. | Done — [findings note](../reports/cohort_findings.md) states the observed result, denominators, alternative explanations, pre-cutoff context, and prioritized questions; it links to the [detailed tables](../reports/cohort_tables.md), [JSON output](../reports/cohort_analysis.json), measurement contract, and [historical source audit](../docs/historical_source_audit.md). The first-90-day diagnostic is linked in P3.3. |
| P2.8 | Verify the analysis with focused checks for the age-window denominator, first-purchase assignment, and reconciliation to source totals. Rebuild the outputs from the committed file and document the commands and results. | Done — [focused tests](../tests/test_cohort_analysis.py) cover first-date assignment, complete and partial age-window boundaries, source-baseline reconciliation, and rejection of a changed baseline; the [verification record](../docs/phase2_verification.md) gives rebuild commands, results, and matching output hashes. |

## Phase 3: Build an assumption-driven revenue forecast

Use the supplied cohort's overall like-aged revenue pattern for the headline
forecast. Treat an early-90-day customer cut as a diagnostic that can challenge
the forecast, not as a hindsight-defined base case. Forecast reported
transaction dollars separately for the observed cohort's defined future periods and a
hypothetical future quarterly cohort. Neither is observed revenue or confirmed
repayment-eligible revenue. The progress table links each completed step to its evidence. The scenario choices that materially change forecast revenue or timing are documented below.

| ID | Task and completion evidence | Progress |
| --- | --- | --- |
| P3.1 | Define the forecast contract: distinguish remaining revenue for the observed Q1 1997 cohort from revenue for a hypothetical future quarterly cohort. Agree on the main horizon, treatment beyond it, units, cutoff, and attribution rules. | Done — [forecast contract](../docs/forecast_contract.md) defines both objects, reported-dollar and cohort attribution rules, the June 30, 1998 observation cutoff, July 1998–June 1999 main forecast, a separate second-year tail sensitivity, and Q4 1998 as the example future first-purchase cohort. Revenue beyond displayed horizons remains unmodeled, not assumed zero. |
| P3.2 | Build a simple base forecast from the like-aged 30-day revenue pattern. Use only fully observable windows for comparisons; address the sharply shrinking denominator in the oldest windows. Provide reproducible code and a table of observed and forecast periods, dollars per original cohort customer, and extension assumptions. | Done — [comparison](../reports/forecast_extensions.md), [code](../scripts/forecast_extensions.py), [output](../reports/forecast_extensions.json), and [lookback sensitivity](../reports/lookback_sensitivity.json) test flat and declining extensions at 2, 3, 4, and 6-window lookbacks. I selected the three-window decline as the working scenario after comparing lookbacks and a trend benchmark; the alternatives remain sensitivities. |
| P3.3 | Test an early-90-day signal using only purchases visible in those 90 days. Compare later outcomes with equal follow-up and avoid defining groups from full observed histories. Make any decision-useful diagnostic reproducible with denominators and limits. | Done — I chose a positive-dollar later-date repeat by day 89 as the lead signal. The [diagnostic](../reports/early90_diagnostic.md), [code](../scripts/early90_diagnostic.py), and [output](../reports/early90_diagnostic.json) compare days 90–449 at equal follow-up for all 23,570 customers, with spend groups as a secondary check. This observed association is not an at-entry input for funding a future cohort. |
| P3.4 | Model credible downside cases for weaker repeat buying and a smaller contribution from high spenders. Show which assumption drives each change in a compact sensitivity table for the observed cohort's remaining revenue. Check in before selecting decision-driving case parameters. | Done — [downside note](../reports/downside_sensitivity.md), [code](../scripts/downside_sensitivity.py), and [JSON](../reports/downside_sensitivity.json). I selected 20% early-repeat and early-top-quarter spending reductions as **separate** decision gates. |
| P3.5 | Transfer the per-customer pattern to a future quarterly cohort only through explicit cohort-size, entry-timing, and channel-mix assumptions. Show separate future-cohort revenue scenarios and timing; identify unvalidated inputs and verify any pre-cutoff external source used. | Done as scenarios — [Q4 purchaser-count note](../reports/future_cohort_size_scenarios.md), [code](../scripts/future_cohort_size_scenarios.py), and [output](../reports/future_cohort_size_scenarios.json) test 40,000, 62,000, and 90,000 first purchasers. Channel mix remains an unvalidated constant, explicitly separated from count and behavior. |
| P3.6 | Reconcile observed inputs, rerun forecast outputs, and write a short investment-facing forecast note explaining the scenarios and what could change them. Keep acquisition cost, contribution, eligible repayment revenue, and the 50%/1.2× financing calculation for phase 4. | Done — the [committee memo](../final_deliverables/investment_committee_memo.md) and [opportunity-cost note](../reports/opportunity_cost.md) explain decision impact. The source-to-report pipeline, dbt tests, and Python tests were rerun successfully; the [source inventories](../docs/company_financial_evidence_1998.md) and [historical audit](../docs/historical_source_audit.md) record publication dates and claim limits. |

### Selected scenarios and decision limits

I selected the **three-window declining extension** as a
*provisional working case* for the observed Q1 1997 cohort's July 1998–June
1999 reported-dollar forecast: **$825,907**, or **$35.04 per original
customer**. Its separate July 1999–June 2000 tail sensitivity is **$615,338**.
The two-window declining extension gives **$718,883** for the main period and
is a lower-revenue sensitivity, not a floor. The three-window flat alternative
is **$1,008,568** for the main period. The future Q4 scenarios now vary
first-purchaser count, repeat behavior, and an illustrative eligible-collected
fraction separately. The recommendation is no present disbursement and
a **$1.2 million conditional ceiling** for one Q4 pilot; neither the fraction
nor the advance is a measured cohort cost. The supplied cohort has
**$2,500,315.63 observed reported dollars** through June 30, 1998; those
dollars are separate from all forecasts.

The [forecast comparison](../reports/forecast_extensions.md) explains the
30-day customer-age windows, complete-window denominators, lookback
backtests, calendar mapping, and why a short holdout cannot establish a
year-ahead rule. The [P3.3 diagnostic](../reports/early90_diagnostic.md)
finds that 6,864 customers (29.1% of the original 23,570) had a
positive-dollar purchase on a later date in days 1–89; they generated 68.3%
of observed days 90–449 dollars. This is an association within one cohort,
not a signal known when an initial advance is made to a future cohort or
proof of why customers bought again.

The [P3.4 grid](../reports/downside_sensitivity.md) tests weaker
early-repeat prevalence and reduced contribution from high early spenders.
I selected the 20% early-repeat and top-quarter cases as
separate gates; overlapping groups are not double-counted. The Q4 scenario
translation remains conditional on missing purchaser counts, acquisition
spend, cohort contribution, and eligible collected revenue. The source and output reconciliation keeps the July 15, 1998 historical gate intact.

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
