# KB doc-policy audit — retail_payment_servicing (product retail), difficulty close-out

## revision_1 (2026-10-16, fresh auditor)

### Entry conditions (Step 0), cited from the coordinator brief
- Policy-side verdict, taken from the tail line of audits/policy_task/retail_payment_servicing/_difficulty.md: `VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN`.
- Gate snapshot: `[check_docs retail] DOCS OK`; `[check_traceability retail_payment_servicing] TRACEABILITY OK` (post-publication). The auditor ran neither.
- The corpus hash of docs/retail (fcba2936fcfbc3a2) was identical at the blind freeze and at close. The gate lines therefore still describe the final form, and no re-run was needed.
- Runtime views 0.runtime.json and 1.runtime.json match the brief hashes (216f95f20acf2d44 / 33bfe3ae11463c6e).
- DB access was through `db_query.py` only. The blind phase is blind on the DB side.
- The account cut mid-audit happened after the blind freeze. The freeze hashes re-verified OK before the reveal resumed.

### Part verdicts per task

| Task | runtime (blind + gt_comparison) | bijection | dependency_form |
|---|---|---|---|
| 0 (extension: re-opened late charge → arrears ∥ good-faith → grant) | PASS (all 4 writes identical to GT) | PASS | PASS |
| 1 (catch-up: late-posted ∥ unpaid late charges → catch-up) | PASS (all 3 writes identical to GT) | PASS | PASS |

Reports:
- audits/runtime_context/retail_payment_servicing/{0,1}.md
- audits/policy_kb/retail_payment_servicing/{0,1}.md

### Closing checklist
- Every normative atom of the 7 extended policies (rules, overwrites, 7 prerequisites, 34 factor ladders with every tier, 7 baselines) and of the governing base policies is entailed by docs/retail, with nothing unborne and nothing added. The retired surface is exact:
  - late-charge formula clause and min/deferred/paid-in-grace clause
  - allocation clause
  - extension good-faith clause and fee clause
- Every prerequisite sentence is verbatim, in its declared form, in the blocked hub only, and resolvable from the depended-on hub and the records. No tool, route or chain is stated beyond the sentences.
- Every factor doc is findable from record words: lease, Care, mailed check, returned payment, the counts. Every computation doc yields a definite fall-back that differs from the answer:
  - task 0: 25.00 / 646.04 / 323.02 / 35.00
  - task 1: 15.00 / 15.00 / 590.82
- Cross-product:
  - docs/care is published and is consistent with the retail Care factors, which read `financed_account_number` and active status.
  - docs/balloon appeared during the audit. No retail figure depends on it.
  - docs/lease is NOT yet published. The lease-reading factors (seven lessee/lease cards) are rendered inside docs/retail and read lease records through find_lease_* share tools, so **no scored figure is conditional on docs/lease**.
  - A lease-side definition of "lease late charge" or "lease payment" that conflicts with these cards cannot be detected until docs/lease is published. This is out of range and stated explicitly.

### Renderer notes (audits/render_source/retail_payment_servicing/render_r1.md), judged against the published docs and the source

1. **Interest bindings (per_diem, interest_cover / interest_carried) listed under the computation document.**
   - The prose of `good_faith_amount_computation` and `catch_up_amount_computation` says nothing about interest. The per diem and day rules are carried in full in the overdue-interest factor docs.
   - **No KB defect.** On the source side this is placement only (XF recipe point 4, ownership: a quantity only one factor uses sits as a plain binding).
   - Not raised as an SRC id: it changes no semantics, and placement-only notes are not routed.
2. **Payment tools post with today's date regardless of cutoff.**
   - Confirmed in task_tools.py: `txn_date=ctx.now()[:10]` in all three payment tools, and the docstrings agree with the bodies.
   - The rules say "the posting day follows the cutoff rule"; base clause 2 says a later or weekend payment "posts the next business day".
   - The KB carries both faithfully, so this is **SOURCE-side → SRC-1**. It is latent, and neither task is affected (Mon and Thu, 10:20 EDT).
3. **Base payoff per diem sentence omits "divided by 100".**
   - Source `retail_payoff_and_refunds` reads "principal_balance times apr divided by per_diem_day_basis". The KB `payoff_quotes_and_overpayment_refunds` clause 3 reads "(the APR being a percentage, it enters as the APR divided by 100)".
   - The APR is a percentage, so the two readings are equivalent at the level of entailment, and the KB parenthesis is a provable derivation.
   - **No KB defect.** Source wording note N-3 (inconsistent with the other base rules, which write "divided by 100"). No semantic gap, so it is not raised as SRC. The policy is not in this difficulty's extended tree.
4. **The good-faith overwrite drops "Before the extension is granted".**
   - Confirmed. The replaced_by keeps "must still post since the most recent installment due date" and "where the good-faith amount … is 0.00 no good-faith payment is required". The grant's action-form sentence "The extension fee is fixed only after the customer has made the good-faith payment toward the extension" carries the ordering for a positive amount.
   - The 0.00 branch is left contradictory (see SRC-2). The KB is faithful, so this is **SOURCE-side → SRC-2**.

### XF_recipe.md, point by point (published docs and source)

1. **Assembly sentences.** Each rule has one generic assembly sentence ("assembled in this order: …") that names no factor quantity. The KB distributes the same order through each factor's stated moment, which is entailment-equivalent. PASS.
2. **Non-commuting order.** The orders where steps do not commute (relief/graduated/mail-float before the cap, deductions after the cap, share replacement before points, fee method before reductions) are each fixed in words and entailed by the KB. The two dollar deductions with a floor of 0 commute. PASS.
3. **Factor independence.** No factor tier reads another factor's output. Shared selections (lease counts, the 12-month late-charge count) are plain bindings. PASS.
4. **Ownership.** per_diem and interest_cover are plain bindings used only by one factor. Placement-only (renderer note 1). No KB effect. Note only.
5. **compute_basis quotes.** A script sweep of all 7 policies: every quote is verbatim in its own rule. PASS.
6. **Ties.** Arrears: same creation time → first recorded (matches LATEST). Lapsed grace: returns on the same date share that date. Both are in the rule and the KB. PASS.
7. **Counting conventions.** Whole months, the "last N months" window and the day-count conventions are stated in every rule and every factor doc, and match MONTHS() and DAYS(). PASS.
8. **Every branch both ways.** One gap: the good-faith 0.00 branch against the grant's action-form prerequisite (**SRC-2**). Everything else holds: the no-agreement, out-of-scope late-charge, absent-lease and absent-Care branches are stated.
9. **Base clauses.** The three late-charge and three payment replaced_by texts are scoped and name their siblings. The late-posted min clause restates the still-in-force part. Exception: the good-faith replaced_by drops the "Before the extension is granted" anchor (**SRC-2**).
10. **Rounding.** Every rounding sentence matches its RND/int() placement. PASS.
11. **Tools.** The docstrings of all 7 tools match their bodies. There are no concrete example values and no ordering words that restate another problem's dependency. The posting-day contract against the rule is SRC-1, a tool-against-rule issue rather than docstring-against-body. PASS on the docstring hygiene itself.
12. **Proof text.**
    - The closure's skipped-effect equations recompute: 444.93, 370.51, 13.00, 878.40, 879.40.
    - The step numbers ("Step 10/12/14") are 0-based indices into evaluation_criteria and are consistent.
    - One overreach in a non-scored read's "necessity" text (task 1 `find_care_transactions`, note N-4).
    - PASS with that note.

### Source-side items (routed to the source; the KB is a faithful translation in both)

- **SRC-1 (latent; tool contract against rule).** The tools `post_arrears_payment_6321a7ae`, `submit_extension_good_faith_payment_c7575c9b` and `submit_catch_up_payment_af77047e`:
  - Docstring: "posts one installment payment to the contract today".
  - Body: `txn_date=today`.
  - Rule (base `retail_payment_posting`, restated in each hub): "the posting day follows the cutoff rule"; "a payment received later, or on a weekend or US federal holiday, posts the next business day".
  - On that branch the agent cannot comply. Not reachable in task 0 (Mon 2026-09-28 10:20 EDT) or task 1 (Thu 2026-10-22 10:20 EDT).
- **SRC-2 (untriggered branch; overwrite hygiene).** Policy `retail_ext_good_faith_payment`, overwrite of `retail_extensions`:
  - The superseded clause "Before the extension is granted, a good-faith payment … must have posted …" is replaced by "… the payment must still post since the most recent installment due date, and where the good-faith amount figured below is 0.00 no good-faith payment is required", which drops the grant anchor.
  - `retail_ext_extension_grant`'s action-form prerequisite reads "The extension fee is fixed only after the customer has made the good-faith payment toward the extension."
  - The grant tool reads "good_faith_amount … 0.00 when none was received".
  - When the good-faith amount figures to 0.00, the source both waives the payment and makes the fee wait on it. This is reachable: no returned payment or late charge in 12 months, Tier 1/1+/2 or enough point deductions, and ≤10 days past due. Task 0 is unaffected (467.41).

Notes, not routed: N-3 (payoff base wording), N-4 (task 1 read-step necessity text), renderer note 1 (placement).

### KB defects
None. kb=CLEAN.

KBVERDICT round 1: task0=PASS task1=PASS kb=CLEAN src=SRC-1,SRC-2

## revision_2 (round 2 re-audit, 2026-10-16)

### Gating and gates
- `tail -1 /tmp/render_retail_0066/RENDER.log` gives `RENDER round 2: DOCS OK`.
- Tail of audits/policy_task/retail_payment_servicing/_difficulty.md: `VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN`.
- Re-run by this auditor:
  - `.venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/env_0066_captive_auto_finance_company retail` ends with `DOCS OK`.
  - `.venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py env/env_0066_captive_auto_finance_company/tasks/retail_payment_servicing` ends with `TRACEABILITY OK`.
- The corpus hash of docs/retail went from fcba2936fcfbc3a2 to 862bbed29b175a58 (75 docs). Runtime views are unchanged (216f95f20acf2d44 / 33bfe3ae11463c6e).

### Procedure
- The round-2 visible re-derivation was written and frozen before the reworked source was read: runtime_context/{0,1}.md revision_2, sha256 d6a42ad9fcc8245c / 400a95a0a852d400 at freeze.
- Contamination disclosure: this is the same auditor as round 1, so the re-derivation is not strictly blind. It is recorded as such.

### Round-1 items
- **SRC-1: CLOSED.**
  - Source: the three payment tools now compute the posting day with `_PostingDay.posting_date` (20:00 CT cutoff, weekends, US federal holidays with observance, next business day). Docstring and body agree.
  - Docs: all three hubs carry the new contract word for word, and base clause 2 is unchanged.
  - Both frozen times give today, so there is no change to the scored writes.
- **SRC-2: CLOSED.**
  - The good-faith replaced_by restores "before the extension is granted".
  - The grant's action-form prerequisite now reads "…, wherever the good-faith amount for the extension is above 0.00", and its condition is scoped the same way.
  - The 0.00 branch is now consistent in the source and is carried verbatim in the docs.
- **Notes N-3 and N-4 and renderer note 1:** unchanged and still not routed.

### Two-way scan on everything that changed
- Lossless (details in policy_kb/0.md and 1.md revision_2).
- Unchanged atoms were re-verified with no regression: all baseline and factor docs re-read, params identical, quote sweep clean, all 7 prerequisite sentences verbatim and single-homed.

### Scored solution
- Unchanged:
  - task 0: 4.00 / 545.83 / 467.41 / grant (2026-08-20, 1, 467.41, 4.00)
  - task 1: 5.00 / 4.00 / 1056.10
- Still uniquely entailed by the visible materials, re-derived through db_query.py on the unchanged worlds.

### New observation
- **N-5** (policy-side note, not routed): the good-faith hub carries the restored base-law anchor "before the extension is granted …". It is the source's own replaced_by text, it uses the declared action form, it names no tool or route, and it is not a KB-EXPLICIT finding.

### Cross-product
- docs/lease is now published. There is no conflict with the retail lease-reading factors.
- No figure is conditional any more: docs/balloon, care, fleet, floorplan and lease are all published.

### Verdicts
| Task | runtime | bijection | dependency_form |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

KBVERDICT round 2: task0=PASS task1=PASS kb=CLEAN src=NONE

## re-judge (all products final)

### Gates (re-run)
- `check_docs.py env/env_0066_captive_auto_finance_company retail` ends with `DOCS OK`.
- `check_traceability.py …/tasks/retail_payment_servicing` ends with `TRACEABILITY OK`.
- The docs/retail hash is unchanged at 862bbed29b175a58. All seven products are published, 373 docs in total.

### (1) Factors that read another product's records, against that product's published docs
- **Lease factors.** These are the seven lessee and lease-lateness cards. They read three things: the lease status "active", lease_payment entries and lease_late_charge entries.
  - docs/lease `payment_posting_and_allocation` lists "Active" among the lease statuses.
  - `late_charges_and_returned_payments` books one late charge per due date after the 10-day grace period, at 5 % of the unpaid portion capped at the lower of $30 and the state maximum.
  - `payment_and_term_fee_schedule` gives the same figures.
  - These are the same entry kinds and meanings the retail cards count. No conflict.
- **Care factors.** These are `care_plan_points_on_unpaid_installment_charge` and `care_holder_points_on_late_posted_charge`. They read the Care plan's active status and its financing account number.
  - docs/care `vehicle_term_and_price_eligibility` says "the plan records the Kestrel product that financed it and that account's number".
  - Activation per `activation_and_aggregate_limit` makes a plan active on dealer remittance.
  - These match the retail reading of "financed in this contract". No conflict.

### (2) Seeded cross-category rows, checked through db_query.py against the owning product's rules
- **Task 0, lease 578d0e16** (Tier 2, NC, monthly 371.94, state max 25):
  - Late charge of 18.60 on 2025-06-07 for due date 2025-05-27. That date is the first permissible day after the 10-day grace, and 5 % × 371.94 = 18.60 is under 25.
  - The May installment was paid 2025-06-09. The June payment of 390.54 on 2025-06-25 carries fees_applied 18.60, matching the use tax → rent → depreciation → fees order.
  - payments_made_count 30 and next due 2026-10-27 match the ledger.
  - Producible.
- **Task 0, balloon 5236a606 and pre-owned ac22c5a0**, both closed with liens released electronically.
  - Pre-owned was paid off 2024-11-08 (the retail contract date, consistent with a dealer trade-in payoff, which carries no hold) and closed 2024-11-13.
  - Balloon was paid off 2023-06-12 with pay_balloon elected and closed 2023-06-16.
  - No funding-channel rows are seeded, so no hold rule is contradicted. Their only role is the extension relationship clause (closed is not a blocking status).
  - Producible.
- **Task 1, lease ad6b0a1e** (Tier 3, MI, monthly 398.88, state max 15):
  - Late charge of 15.00 on 2026-05-01 for due date 2026-04-20. That is the first permissible day, and 5 % × 398.88 = 19.94 is capped at 15.
  - The April installment was paid 2026-05-05 for 413.88, including fees 15.00.
  - payments_made_count 18 and next due 2026-11-20 match the ledger.
  - Producible.
- **Task 1, Care Platinum 90e5d900:**
  - Vehicle age 0 is within 6 years, and odometer 14 is within 75000.
  - The 72-month / 100000-mile term is on Platinum's term list, and expiration odometer 100014 = 14 + 100000.
  - Deductible 100.00 is one of Platinum's options (0/50/100).
  - Price 2895.00 is within the 1895.00-4495.00 range.
  - The limit was established 2024-03-19 at 38350.00, below Platinum's 40000.00 maximum. The plan is financed in retail account 1173405298.
  - Producible.

### (3) Searches a rollout would run (KB_search through db_query.py, 9 queries across both tasks)
- Generic queries rank docs from other products high:
  - "extension agreement signed defer payment extension fee" returns the Balloon tier table and the Pre-Owned extension terms at ranks 1-4, ahead of the retail docs.
  - Pre-Owned and Balloon late-charge and payment-processing docs also appear.
- Every one of these names its own product in title and text: "Kestrel Advantage Balloon", "Kestrel Pre-Owned Retail Installment Sale Contract". The customers' records name "Kestrel New Vehicle Retail Tier 4" and "Kestrel New Vehicle Retail Tier 2", and each product has its own find_* lookups and hidden tools.
- The Pre-Owned extension doc still carries its own in-force good-faith-percentage clause. That clause governs the Pre-Owned product only and offers no reading of the retail answer.
- No other product's doc states a rule over a Kestrel New Vehicle Retail contract that changes a retail figure, a prerequisite or a tool argument. Product-scoped cross-references do mention retail, for example lease's relationship relief and fleet's excess-mileage reduction, but they govern their own products' figures only.

### Re-judge result
No new KB or source item. SRC-1 and SRC-2 remain closed. Notes N-3, N-4 and N-5 are unchanged and not routed.

KBVERDICT rejudge: task0=PASS task1=PASS kb=CLEAN src=NONE
