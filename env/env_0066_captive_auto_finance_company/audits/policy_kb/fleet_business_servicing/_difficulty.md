# KB-doc policy audit — fleet_business_servicing (product fleet), difficulty close-out

## revision_1

**Entry conditions (Step 0).**
- Policy side: `VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN` (only the tail line of audits/policy_task/fleet_business_servicing/_difficulty.md was read).
- Gate snapshot from the brief: `[check_docs fleet] DOCS OK`, `[check_traceability fleet_business_servicing] TRACEABILITY OK`. Re-run on the final form by this auditor: DOCS OK (mechanical gates PASS) and TRACEABILITY OK (tasks 0 and 1).
- Runtime view hashes: d55748a531761f87 / a0332f312c863127, matched.
- DB access path: db_query.py (tool-shaped). Task-tool schemas came from the engine registry's openai_schema only. The blind phase is clean; there was no contamination.

**Per-task part verdicts.**

| Task | KB-RUNTIME (runtime_context/…/N.md) | KB-BIJECTION (policy_kb/…/N.md) | KB-EXPLICIT (dependency_form) |
|---|---|---|---|
| 0 | PASS (blind 290.00 / 1451.83 / 27.87 / 1965.25 = GT) | PASS | PASS |
| 1 | PASS (blind 3907.90 / 1257.31 = GT; SRC-5 noted) | PASS | PASS |

**Closing checklist.**
- Audit files exist one-to-one per task (runtime_context/0.md, 1.md; policy_kb/0.md, 1.md). The blind answers were frozen before the reveal (sha256 prefixes 00b4fb3d4e16774d, 629b26617b6e160c at freeze); gt_comparison was appended afterwards.
- Every normative atom of the six extended policies and their governing base policies is entailed by docs/fleet. All retirements are rendered as retired, with the scoped remainders in force. All four prerequisite sentences are verbatim on their blocked side in state form, appear in no other policy's documents, and each hop is resolvable from the depended-on document's own "once billed, the unit's ledger carries…" sentence plus the records.
- All 31 declared factor ladders are carried in full, one document each, and are findable from record words, using official product names for cross-product reads.
- No tool name, route or aggregated chain beyond the sentences.
- Cross-product: only retail/fleet/care/floorplan docs are published (balloon and lease are not). No scored figure depends on an unpublished product's docs (balloon/lease facts are read from records via finders; every ladder lives in fleet docs), so nothing is conditional.
- Coverage gap stated per skill: cross-product contradictions and unclaimed base-only products are outside this audit.

**Policy-side note (no id, not a KB verdict).**
- N-1: each computation document carries the source rule's generic combination sentence ("Any holdback is subtracted…", "any multiplier… any credit… any addition", "any relief percentage…", "Any schedule replaces only the standard figure it names"). This is the source's own text (compute_basis.result; XF recipe item 2). It announces that kinds of adjustment exist, which loosens the skill's "baseline silent about any variation" ideal. It names no factor, condition or document; the blind auditor found every factor from record words.

## Renderer notes (audits/render_source/fleet_business_servicing/render_r1.md) — classification

| Renderer point | Judgement | Class |
|---|---|---|
| Retail product name ("Kestrel retail installment contract" vs compute reading only the retail category) | The KB uses the official name "Kestrel New Vehicle Retail Installment Sale Contract", which is what the compute reads; the docs are faithful. In the source rules, the phrase also fits the Kestrel Pre-Owned Retail Installment Sale Contract and the Kestrel Advantage Balloon Retail Installment Sale Contract (blueprint display names), so the rule text alone under-determines what the compute pins. | **SRC-1** (rule-vs-compute naming) |
| Two Kestrel Care plans on one VIN | Rules in et_care_coverage_credit and em_maintained_unit_scale ("$60 / 0.95 where it is covered by an active Kestrel Care Platinum contract") do not say which tier wins when Platinum and Platinum Plus/Elite are both active on the VIN. The compute takes the upper tier first, and the KB adds "(and no active Platinum Plus or Platinum Elite)" to match the compute. The KB matches the compute; the rule text is silent. Not seeded in either task. | **SRC-2** (rule-vs-compute branch) |
| Zero deficiency vs "a positive number" | fleet_ext_trac_shortfall_charge: "A settlement whose recorded result is a deficiency stays within this policy even where the figure below comes to nothing, and the charge is then zero". bill_trac_deficiency_eb6903d6 docstring: "a positive number with 2 decimal places". The KB carries both faithfully (trac_deficiency_billing table "zero where the figure comes to nothing" vs tool section "a positive number"). A zero-figure deficiency therefore cannot be booked, and the arrangement's Term 3 state ("ledger carries the deficiency charge") is unreachable in that branch. Not seeded. | **SRC-3** (docstring-vs-rule) |
| Fund movement in docstrings | request_credit_refund_a747b6b6: "receives the funds by the chosen channel"; remit_arrangement_payment_506aa8ae: "the funds leave its account by the chosen channel". The bodies only insert the posting and update charges_due_balance (task_tools.py ll. 161–163, 240–242). XF recipe 11 says "A docstring claims only effects the tool body has". The KB copies the docstring faithfully. Low severity: no scored or checked state depends on it. | **SRC-4** (docstring-vs-body) |

## XF_recipe.md (audits/render_source/XF_recipe.md) — point-by-point against source and docs

1. Assembly sentences: holds. The only assembly is the generic result sentence, which names no factor quantity; the KB is the same. 
2. Non-commuting order: holds. The order is fixed generically in all six policies and carried verbatim in meaning in each computation document (N-1 note).
3. Factor independence: holds. No factor reads another factor's output. lc_relationship_rate, rf_clearing_holdback and d_payment_history_credit read late-charge postings (records), and pa_minimum_down_schedule reads deficiency postings (records).
4. Ownership: holds. lc_inv_tax/dep/lease are owned by lc_invoice_part_basis, lc_inv_due by lc_lateness_scale, and rf_returnable by rf_clearing_holdback.
5. compute_basis quotes: holds (script sweep: all quotes verbatim in their own rule, 6/6 policies).
6. Ties: holds. The latest-invoice and latest-settlement ties ("posted first") are stated and match LATEST, and are carried in the KB.
7. Counting conventions: holds. Whole-month, day, "within the last N whole months" and negative-month conventions are stated, match MONTHS/DAYS, and are carried with boundary examples.
8. Every branch both ways: **members found**. The Care double-coverage precedence lives only in the compute (SRC-2). The zero-deficiency branch is stated but unbookable by the tool contract (SRC-3). All other branches are fine.
9. Base clauses: holds. Eight scoped overwrites each restate the still-in-force remainder and are rendered as retired plus scoped replacement.
10. Rounding: holds. Each rule's "rounded once, at the end" matches the single RND.
11. Tools: **member found**. The fund-movement claims are not in the bodies (SRC-4); positive-only vs zero (SRC-3). There are no example values and no ordering words in the docstrings.
12. Proof text: holds for the scored figures. Every expected/baseline value recomputes from the visible records (blind = GT). **Realism member:** task 1's seed dropped the completed termination-notice request row (worklog: "dropped both seed rows (termination-notice request …)"), yet the unit keeps termination_notice_date 2026-07-02. Visible base Clause T1 says "A termination notice takes effect only when a named authorized signer has completed the termination notice request for the unit. The evidence is the system record of that request", and `find_fleet_requests` returns "No matching entries". The GT's $200 deficiency notice credit is still entailed by deficiency_notice_credit ("The days run from the termination notice date on the unit"). A strict reader carrying T1 into the factor could instead take "no termination notice": deficiency 4107.90 and first payment 1301.76. This is a source/seed realism defect, not a KB defect. → **SRC-5**

## SOURCE-side items (routed back to the source; the KB is a faithful translation of each)
- SRC-1: rule term "Kestrel retail installment contract" (et_relationship_holdings_credit, em_relationship_free_miles, em_rate_relief, lc_cross_account_addition, rf_retail_delinquency_reserve, d_relationship_remarketing, pa_upfront_count_schedule) fits three products; only the compute pins the retail category.
- SRC-2: Care double-coverage precedence (Platinum vs Platinum Plus/Elite on the same VIN) is in the compute but not in the rule text of et_care_coverage_credit / em_maintained_unit_scale.
- SRC-3: zero-figure deficiency ("the charge is then zero") vs bill_trac_deficiency_eb6903d6 "a positive number".
- SRC-4: refund / arrangement-payment docstrings claim fund movement the tool bodies do not perform.
- SRC-5: task 1 world has termination_notice_date without the completed termination_notice request that visible Clause T1 makes the evidence of an effective notice (PLAUSIBLE second reading of the deficiency notice credit).

KB defects: none.

KBVERDICT round 1: task0=PASS task1=PASS kb=CLEAN src=SRC-1,SRC-2,SRC-3,SRC-4,SRC-5

## revision_2

**Gating.**
- `tail -1 /tmp/render_fleet_0066/RENDER.log` = `RENDER round 2: DOCS OK`.
- policy_task tail = `VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN`.
- Gates re-run by this auditor: check_docs last line `DOCS OK`; check_traceability last line `TRACEABILITY OK` (0.json 22, 1.json 16, 0 misses).

**Round-1 item closure (checked in source, task_tools.py, docs, and the DB via db_query.py).**

| Item | Source | Docs | Closed? |
|---|---|---|---|
| SRC-1 retail naming | every rule sentence names "Kestrel New Vehicle Retail Installment Sale Contract"; scripted sweep finds no bare phrase | 7 factor docs carry the full name in Rule/Records/tables | yes |
| SRC-2 Care double coverage | middle tier "…but by no active Kestrel Care Platinum Plus or Kestrel Care Platinum Elite contract" in rule and ladder, matching compute order | termination_maintenance_credit, mileage_maintenance_multiplier carry it verbatim | yes |
| SRC-3 zero deficiency | rule "booked at zero, which settles the terminal rental adjustment"; docstring "a number of zero or more"; body has no positivity check | trac_deficiency_billing scope, table and parameter line | yes |
| SRC-4 fund-movement docstrings | refund and arrangement docstrings claim only the recorded posting, channel and balance change; bodies match | both tool sections match | yes |
| SRC-5 task-1 notice evidence | seeded completed termination_notice request (signer Megan Zielinski, 2026-07-02); GT reads find_fleet_requests | no doc change needed | yes: db_query.py returns the request, so Clause T1 and the notice credit agree on a single reading ($200) |

**Regression check.**
- Scored solutions are unchanged and re-derived from the visible surface: task 0 = 290.00 / 1451.83 / 27.87 / 1965.25 ach_credit; task 1 = 3907.90 / 1257.31 ach_debit.
- The newly seeded rows (delivery_acceptance requests in both tasks; closed 2019 balloon election, payoff and release in task 1) feed no scored input and create no decoy that changes a tier.
- The prerequisite sentences are verbatim on their blocked side only, and each hub names only its own tool.
- All 61 documents are present with unchanged structure. The 12 documents with changed text were re-read in full, and every change maps to a source change.
- docs/balloon and docs/lease are now published. No fleet figure depends on them, so nothing is conditional. Cross-product contradictions remain outside this skill's range.

**Part verdicts (revision_2).**
- task 0: KB-RUNTIME PASS, KB-BIJECTION PASS, KB-EXPLICIT PASS.
- task 1: KB-RUNTIME PASS, KB-BIJECTION PASS, KB-EXPLICIT PASS.
- Policy-side note N-1 (the generic combination sentence in computation documents) is unchanged and is not a verdict item.

KBVERDICT round 2: task0=PASS task1=PASS kb=CLEAN src=NONE

## re-judge (all products final)

**Gates (re-run by this auditor).**
- `check_docs.py … fleet` ends `DOCS OK`.
- `check_traceability.py … tasks/fleet_business_servicing` ends `TRACEABILITY OK`.
- Published products: retail 75 docs, lease, preowned 70, balloon 83, fleet 61, care 18, floorplan.

**(1) Fleet figures and factors that read other products' records, against those products' published docs.**
- **Retail "status active".** Retail status values used by the retail docs are active, repossession assigned, paid in full, closed. "Active" is read the same way by the fleet relationship, remarketing and up-front factors. Consistent.
- **Retail / balloon "days past due zero".** db_schema defines `days_past_due` for both as "calendar days the oldest unpaid installment is past its due date as of the last nightly cycle; 0 when current". The fleet factors test only zero vs non-zero. Seeds: retail 35 (task 0, next due 2026-10-04) and 44 (task 1, next due 2026-09-28) are both non-zero under any day-count convention. Balloon 0 with next due in the future. No tier depends on the convention.
- **Retail funding entries and retail late-charge postings** (dates and counts only; fleet never reads amounts). These match the retail ledger event types, and the retail late-charge rule's grace-period timing (10 days for every tier) and one-charge-per-due-date limit.
- **Balloon funding entries, open or closed.** The balloon docs book funding at contract funding. Task 1 closed 2019 contract:
  - maturity election 2022-03-10 while active ("A maturity election can be recorded only while the contract status is active");
  - wire payoff 2022-04-08 (no hold for wire);
  - electronic lien release 2022-04-11 (within 3 business days);
  - closed on release ("Once the release is completed the title status is updated and the account is closed").

  Consistent with the balloon tenure credit's "open or closed".
- **Care "active", plan name and VIN.** Care's "One Plan per VIN" rule ("A plan may be sold on a VIN only when no other plan on that VIN is pending activation or active") makes the double-coverage branch of SRC-2 unreachable in a lawful world. The fleet ladders stay consistent with it.

  Task 0 van plan Kestrel Care Platinum checks against the published Care sale rules:
  - age 0, odometer 37;
  - term 60 months / 100000 miles, both in the Platinum rows;
  - deductible 100 (options 0/50/100);
  - price 3295 (range 1895–4495);
  - commercial use allowed on Platinum;
  - bought for cash;
  - aggregate limit 40000 = the Platinum maximum.

  Sedan plan Platinum Elite checks out too:
  - age 1, odometer 21;
  - 84 months / 100000 miles;
  - deductible 0;
  - price 3495;
  - financed in balloon 5419283376;
  - limit 36950 (vehicle price).

  All producible.
- **Conditional figures.** None remain: no fleet figure depends on another product's docs, and every ladder lives in docs/fleet.

**(2) Seeded cross-category rows (read through db_query.py), checked against the owning product's published rules.**
- **Producible:**
  - retail and balloon contract states (payments made match installments elapsed: 54, 41 retail; 32, 41 balloon; past-due amounts = 2 × monthly payment; fees due = unpaid late charges);
  - Care plans as above;
  - the closed balloon chain;
  - retail late-charge **dates** (due + 10 grace + 1).
- **Not producible: retail late-charge amounts** (SRC-6 below).

**SRC-6 (cross-category seed realism; no scored effect).** Every seeded retail late charge is 30.00:
- task 0: 2026-03-15, 06-15, 10-15 on contract 5307716482 (monthly 949.72);
- task 1: 2026-04-08, 10-09, 11-08 on contract 5124409863 (monthly 815.70).

The published retail docs retire the flat rule ("The late charge is the late-charge percentage of the unpaid installment portion, capped at…" is listed under "Retired clauses … no longer in force"). The current rule for an installment left unpaid past its grace period works as follows:
- **Starting rate:** 3.5 percent when "the contract shows at least 30 installments satisfied and no returned payment in the last 24 calendar months", otherwise as scheduled. The point factors only take percentage points off.
- **Graduated factor:** "When the days beyond grace are from 1 through 7, the charge figured at the rate is halved and the result rounded down to the whole dollar". A charge posted on due + 11 is 1 day beyond grace.

For the charges posted 1 day beyond grace, even the full product rate of 5 percent gives at most 23.00 on the task-0 contract (half of 47.49, rounded down) and at most 20.00 on the task-1 contract (2026-04-08, 2026-10-09). The task-1 charge of 2026-11-08 is not halved, since it falls 41 days after the next due date 2026-09-28. Even so, the records' starting rate of 3.5 percent (41 installments satisfied, no returned payment) caps it at 28.55 before any points are taken off. The figures under the published starting rate and points are about 13.00 (task 0, 2026-10-15) and 12.00 (task 1, 2026-10-09). 30.00 is not reachable. The late-posted schedule (3.0 / 4.0 percent starting rates on one monthly payment) also stays below 30.00. The amounts follow the retired base rule (worklog: "5 percent capped at the 30.00 company maximum").

Fleet reads only the count and dates of these charges (lc_cross_account_addition, rf_retail_delinquency_reserve, pa_upfront_count_schedule), and the retail fees-due balance is not read by any fleet factor. So no fleet scored value or tier changes, and no competing reading arises. This is routed to the source as seed realism.

**(3) KB_search / grep competition with all products published.** Queries a rollout would run returned other-product documents next to the fleet ones:
- task 0: "refund credit balance overpayment", "late charge most recent invoice", "excess mileage charge turned in", "early termination charge", "holdback refund", "Kestrel Care Platinum credit";
- task 1: "deficiency payment arrangement first payment", "sold at auction less than book value deficiency", "auction sale expenses remarketing fee deficiency".

The other-product documents include:
- Pre-Owned / Balloon / New Vehicle Retail overpayment refunds ("An overpayment refund can be issued only when the contract status is paid in full or closed");
- Kestrel Closed-End Consumer Lease early termination and excess mileage;
- Balloon return excess mileage;
- Pre-Owned deficiency settlement and auction expense allowance;
- New Vehicle Retail repossession deficiency.

Each names its own official product in its title and rule sentences, and none speaks of a Kestrel Commercial Fleet Lease unit, a TRAC sale settlement or a closed-end commercial unit. Neither customer holds a pre-owned contract or a consumer lease (lookups return no entries). No other-product document offers a competing formula, holdback, credit or order for 1965.25, 290.00, 1451.83, 27.87, 3907.90 or 1257.31. The fleet documents remain reachable for every query.

**Re-judge verdicts.** task 0 PASS; task 1 PASS. The KB has no defect (kb=CLEAN). Source item: SRC-6.

KBVERDICT rejudge: task0=PASS task1=PASS kb=CLEAN src=SRC-6

## revision_3

**Gating.** policy_task tail = `VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN`.

**Gates re-run by this auditor.**
- `check_docs.py … fleet` ends `DOCS OK`.
- `check_traceability.py … tasks/fleet_business_servicing` ends `TRACEABILITY OK`.
- docs/fleet concatenated sha256 prefix is 3586154320e076af, unchanged since revision_2.

**SRC-6 closure (via db_query.py, against the published docs/retail rules).**

The unpaid-installment late-charge rule as published in docs/retail:
- the starting rate from the Unpaid Installment Rate Schedule (3.5 percent at ≥30 installments satisfied and no returned payment in 24 months);
- less the points from Care Plan, Clean-Schedule, Lessee Rate and Partial-Effort;
- applied to the unpaid installment portion (Calculation Sheet) and rounded to the cent;
- then the Graduated factor (1–7 days beyond grace: half, rounded down to the whole dollar; 15 or more: kept to the cent);
- then the cap of the lower of 30.00 and the state maximum of 35.00.

| Task / posting | Inputs read (records) | Published-rule figure | Seeded |
|---|---|---|---|
| 0: 2026-03-15, 06-15, 10-15 (installments 03-04, 06-04, 10-04) | 54 satisfied, no returned payment → 3.5; active Care plan financed some other way (Platinum on the van: cash; Platinum Elite financed in the balloon) → −0.25; no extension or due-date change → −0.5; no lease; no recent payment → 0. Rate 2.75 × 949.72 = 26.12; 11 days from next due = 1 beyond grace → half 13.06 → 13 | 13.00 | 13.00 ×3 |
| 1: 2026-04-08, 10-09 (installments 03-28, 09-28) | ≥30 satisfied → 3.5; no Care; −0.5 clean; no lease; no recent payment. 3.0 × 815.70 = 24.47; 11 days → half → 12 | 12.00 | 12.00 ×2 |
| 1: 2026-11-08 (installment 10-28) | the same rate of 3.0; past due 1631.40 → unpaid portion 815.70; 41 days from next due 2026-09-28 = 31 beyond grace → kept to the cent | 24.47 | 24.47 |

The fees-due balances also agree:
- task 0: 13.00 (only the 10-15 charge is unpaid; fee payments of 13.00 on 03-27 and 06-26);
- task 1: 36.47 = 12.00 + 24.47 (the 04-08 charge was paid 04-20).

SRC-6 is **closed**: every seeded retail late charge is now a figure the published retail rules produce.

**Scored solution.** Unchanged:
- task 0: 290.00 / 1451.83 / 27.87 / 1965.25 ach_credit;
- task 1: 3907.90 / 1257.31 ach_debit.

The fleet factors that read retail late charges (lc_cross_account_addition, rf_retail_delinquency_reserve, pa_upfront_count_schedule) read only their count and dates within 6 whole months. Those are unchanged: two in the window in each task, one outside. No fleet document, charter line or tool changed, so the round-2 two-way scan and dependency-form verdicts carry over. Nothing regressed.

KBVERDICT confirm: task0=PASS task1=PASS kb=CLEAN src=NONE
