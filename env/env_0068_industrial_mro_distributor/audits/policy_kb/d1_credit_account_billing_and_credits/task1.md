# Policy-KB bijection audit — d1_credit_account_billing_and_credits / task 1

## revision_1

Scope: credit_ext_permanent_increase_grant (root, decide_limit_request_85fdd39c; overwrite of credit_limit_review), credit_ext_permanent_request_figure (submit_limit_request_dcbbb504, user-owned), base credit_limit_review, the variants read, both task tools. Same source hashes and gate snapshot as task 0.

## source_to_kb

### credit_ext_permanent_request_figure
| Source atom | KB home | Judgement |
|---|---|---|
| Rule opening (customer submits own permanent request naming the supported limit) | permanent_limit_request_submission (hub) | verbatim |
| Baseline rule (base x coverage, final rounding; base = 12-whole-month invoice totals / 12; coverage = (net days + 30)/30) + whole-month convention | supported_limit_figure: quote block, Definitions, coverage table, worked figures | equivalent; defaults 12 and 30 carried |
| Assembly ("Every amount a schedule in this rule adds … every percentage a schedule sets multiplies …") | supported_limit_figure "Combination" | verbatim (SRC-1) |
| Factor purchase_base_measure (method; >=150 % / 120–150 % / otherwise / no invoice) | monthly_purchase_base_by_buying_pattern: clause, ladder, boundaries at exactly 1.5 and 1.2 | full ladder |
| Factor billing_lag_days (60 / 40 / 30) | billing_lag_in_terms_coverage: clause, 12-whole-month paper-fee window, schedule | full ladder |
| Factor finance_charge_haircut (70 / 85 / 100) | finance_charge_reduction_of_supported_limit | full ladder |
| Factor contracted_spend_support (quarter / eighth / nothing; monthly share = commitment / 12) | contracted_spend_in_purchase_base; names Contract Pricing Agreement tiers | full ladder |
| Tool contract submit_limit_request_dcbbb504 | hub parameter table, return, contract notes | equivalent |

### credit_ext_permanent_increase_grant
| Source atom | KB home | Judgement |
|---|---|---|
| Prerequisite sentence | permanent_limit_decision (hub) first line | verbatim, see below |
| Request decided = latest-dated permanent request; already decided or tie -> nothing | granted_permanent_limit "The request decided" | verbatim |
| Overwrite replaced_by (on-time gate, cap at step room and ceiling, approved / approved_reduced; step room replaces flat step) | granted_permanent_limit Grant 1 | verbatim |
| Baseline (step room = limit x (1 + tier largest step), rounded) | granted_permanent_limit Grant 2 + "lowest of" line + worked table | equivalent; ceiling and step named and in credit_limit_and_review_schedule |
| Assembly (points before increase; amounts after rounding) | granted_permanent_limit Grant 3 | verbatim (SRC-1) |
| Desk referral (>desk amount -> referred, nothing, unchanged) | granted_permanent_limit Grant 4; credit_limit_review_terms clause 4 | equivalent |
| Factor step_start_by_payment_and_review_marks (half / three quarters / whole) | step_percentage_starting_point (truth table, 12-month lookback, 24-month decision window) | full ladder |
| Factor review_age_points (10 / 5 / 0) | credit_review_age_step_points | full ladder with boundaries |
| Factor denied_dispute_deduction (-10 / -5 / 0) | denied_dispute_step_deduction | full ladder |
| Factor account_age_points (5 / 2 / 0 at 180 / 84) | account_age_step_points | full ladder with boundary |
| Factor stocksmart_program_allowance (method: billed-fee sum / billed + one minimum / three minimums or nothing) | stocksmart_allowance_in_step_room; names StockSmart Vendor-Managed Inventory Program, program fees, tier monthly minimum fee (found in docs/vmi monthly_program_fee_schedule) | full ladder |
| Factor vendpoint_model_allowance (whole / half / quarter at 3000 / 500) | vendpoint_allowance_in_step_room | full ladder |
| Tool contract decide_limit_request_85fdd39c (decision enum incl. "pending never passed"; effects) | permanent_limit_decision parameters + effect table | equivalent to docstring |
| Retired surface: credit_limit_review flat-step clause | credit_limit_review_terms clause 3, marked "Retired, no longer in force"; the other clauses (active only, interval with month-end boundary, desk referral, temporary increase, decision days, effect of decisions) carried in force | correct |

### prerequisite (grant -> request figure)
- policy_source (state form): "A permanent increase is not decided until the account carries a permanent limit request with no decision recorded on it."
- Carried verbatim as the first line of permanent_limit_decision (hub of the blocked policy) with a same-form restatement ("decided only on a permanent limit request in the account's limit review history that carries no decision; with no such request on the account, no permanent increase is decided"). Connective "not … until", strength and form intact.
- Resolution basis: permanent_limit_request_submission describes the write ("It is recorded with its decision marked pending", customer's own act) in the words of the state ("permanent limit request", "decision"); records show CLR-1310452, CLR-1310877, CLR-1314209 each with a decision entry.
- The sentence appears in no other policy's document (content grep "no decision recorded" hits only permanent_limit_decision). The submission hub's contract note "the request stays pending until it is decided" states the request's own record effect (tool docstring), not the waiting policy's gate.

## kb_to_source
- Every normative sentence traces to the rule, replaced_by, base rule, parameter_schema, variants or the tool docstring. Examples recomputed: granted table rows (55000 / 60000 / referred / 140000), supported limit worked figures (41000.00; 1111.11), boundaries in every factor doc. No example equals a scored value (191236.72, 149087.00, intermediates 147500.00, 1212.00, 64281.25 absent from docs/).
- Additions / rewrites / omissions: none found.
- Cross-problem operational guidance: none; decide_limit_request_85fdd39c named only in its own hub, submit_limit_request_dcbbb504 only in its own hub.
- Opening world state as policy fact: none.
- Unlock schemas carry no figure.

## bijection_verdict
KB-BIJECTION PASS (revision_1). Source-side items for the verdict line: SRC-1 (assembly sentences in supported_limit_figure "Combination" and granted_permanent_limit §3), SRC-2 (seed, gold-moving), SRC-4 (seed), SRC-5 (limit_increase_max_step_pct description survives the overwrite in credit_limit_and_review_schedule). See _verdict.md.

## dependency_form
- Prerequisite sentence verbatim on the blocked side in state form; same-form restatement only.
- No action restatement, no other problem's tool or policy named, no route, no aggregated chain, no cross-problem FAQ.
- Titles general ("Commercial Credit Account Permanent Credit Limit Requests", "… Permanent Limit Decisions — Credit Desk Reference", "Granted Limit on a Permanent Increase", "The Supported Credit Limit …"). None mirrors the task.
- Factor docs: none names another factor or the computation doc; none says which tier a customer sits on.
- Computation docs: generic assembly sentences (SRC-1) are verbatim source text; recorded as source-side placement, not a rendering addition.
- Verdict: KB-EXPLICIT PASS.

## Three part-verdicts
runtime=PASS, bijection=PASS, dependency_form=PASS.


## revision_2

### source_to_kb / kb_to_source
- Charter (96e73223…), task_tools (ab50360b…) and docs/credit (tree 2971b6b5ce969a27; listing e6336789…) are byte-unchanged since revision_1. So every revision_1 entry stands as recorded: the atom-by-atom forward scan, the reverse scan, the retired surface and the prerequisite carriage.
- New scored values (task 0 room payment 2619.61; task 1 granted 149075.00) and the new intermediates (15601.32, 0.077529, 4748.64, 2747.69) appear in no document example and no unlock schema. Grep restricted to docs/ was empty, and the unlock schemas carry no figures.

### Cross-product rows after the rework (producible by the owning product's published rules)
- **StockSmart:** the 12.00 par change fee row that no par change entry supported is removed. 19 monthly minimum fees of 400.00 run from go-live 2025-03-03; program spend 0 < 8000.00. **SRC-2 CLOSED.**
- **VendPoint Locker 24:** 17 usage bills from installation (2025-05), each equal to the month's vends, per cost center (cost center billing yes); ramp-up Jun–Jul 2025. Every tested month is at or above the 750.00 minimum (two months exactly at 750.00 carry no fee). Ethernet, so no cellular fee. Badges at most 6 against 50 included.
- **Order lines:** every invoice's shipped merchandise now exists. Priority Ship-To orders are all >= 100.00, so freight is free (invoice freight 0.00). **SRC-4 CLOSED for task 1.**
- Residual note as for task 0 (tax and item prices are free seed inputs).

### bijection_verdict
KB-BIJECTION PASS (revision_2); no regression.

### dependency_form
Docs unchanged; KB-EXPLICIT PASS (revision_2).

### Three part-verdicts
runtime=PASS, bijection=PASS, dependency_form=PASS.
