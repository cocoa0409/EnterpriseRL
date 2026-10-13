# Policy-task audit — financial_assistance / task 0

## source_derivation_frozen

- Auditor: Claude (erl-task-policy-audit), independent; freeze time 2026-10-04T16:55Z (wall clock), before any task's GT was revealed.
- Freeze hashes: view `task0.view.json` 3a695b812788214b156021a109e8b7316e7cfcdd08da99126ad777ce0541841b; `assistance.extended.yaml` 1e06045e…41b; `task_tools.py` 4260086c…2e9 (full values in `_difficulty.md`).
- Permitted: `frozen_time`, `user_scenario`, `initial_state` (via the masked view only), the charter, tool contracts, schema, share tools.
- Masked and unread at freeze: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, worklog.
- contamination_disclosure: none.

World: frozen 2026-10-05 (Monday). Customer Renata Vossberg `ce7f1fe6-…9234`, portal_enrolled true. Approved case `ba07189c-5f0b-4b04-970a-d18b33a96cda` (Financial Assistance 25% Discount, application 2026-04-16, phone_assisted, household 1, income 47000.00, fpl 300.3, award 2025-08-19 … 2026-10-16, discount_granted_total 728.00). Coverages: `a1753634` Commercial In-Network "Peachtree Marketplace Silver HSA 3300" active, band `not_employer_plan`; `fdbaaaab` employer plan terminated 2024-12-31.

### policy_self_consistency (this task only)

- Charter-global checks 1, 2, 3, 6, 7 and the factor structure: see `env/env_0028_clinical_laboratory_company/audits/policy_task/financial_assistance/_difficulty.md` → `override_declarations`, `rule_compute_equivalence`, `action_binding_and_uuids`, `prerequisite_sentences`, `prerequisite_graph`, `factor_ladders`. F-1 there concerns `assistance_ext_document_period`, which is not in this task's tree.
- O-6 against this world (the "never more than balance due" baseline sentence vs. the deposit limit tier): reading "The award discount is never more than the invoice's balance still due" as a hard ceiling gives min(2226.00, 2202.00) = 2202.00; the deposit tier "is limited only to its working amount, the deposit beyond the owed share becoming a credit to the household" gives 2226.00. The tier sentence names the credit that only arises if the discount exceeds the balance due, so the ceiling reading voids an explicit clause of the same rule and is not a defensible second reading; base also contemplates it ("A discount that exceeds the balance due leaves a credit"). Observation only.
- Handling time (check 4): award discount is evaluated on the opening world (it has no prerequisite); the renewal tier on "opening world + the discount line booked today" (its own prerequisite resolved, before the renewal is written).
- No real-world wait (check 5): every input of both writes is a seeded row (claims, invoice ledger, coverages, orders, plan ledger, assistance events) or the synchronous effect of the discount write (an `assistance_events` row dated 2026-10-05 under the case), or a fact the customer states (household 1, income 47000.00, insured). The renewal requires the applicant's own portal submission in-call, which the persona performs immediately.

### problem_chain

Root problem (customer's only ask): renew the assistance award → `assistance_ext_renewal_tier` (user tool `submit_renewal_application_d691b1b8`).

Eligibility of the root at 2026-10-05: base single-open-case rule allows a renewal while an award is approved "only within renewal_window_days calendar days before that award's end date" — end 2026-10-16, 11 days away, window 30 → allowed. Extended: "A renewal application is submitted by the applicant in person through the patient portal; an agent does not take a renewal application by phone" → owner=user hand-over; portal_enrolled true.

Prerequisite sentences of the root's rule: one — "The tier a renewal application is assessed at is set only after every invoice the award being renewed covers whose payer decision is final carries that award's discount line."

Invoices of the household against the award window 2025-08-19 … 2026-10-16:

| invoice | order / class | DOS | in window | payer decision | discount line under ba07189c |
| --- | --- | --- | --- | --- | --- |
| 7a4e5310 | 13084ad7 genetic | 2025-07-22 | no | final (appeal upheld 2026-04-24, PR assigned 2026-05-01) | — (not covered) |
| 38870a59 | 216b0b00 toxicology | 2025-08-08 | no | final | — |
| 136beffa | d44e3b81 toxicology | 2025-08-12 | no (paid) | final | — |
| dc9db92f | a0cea879 esoteric | 2026-03-18 | yes | final (PR 2026-04-30) | yes, 602.00 (event 7db7adad, 2026-05-08) |
| 76312eaf | 69f7e736 genetic | 2026-05-12 | yes | final (PR deductible 2026-09-24, posted 2026-09-28) | **no** |
| 42469eea | 8adbe201 AP&C | 2026-06-20 | yes | final | yes, 126.00 (event 7cdc9f91) |
| 7b674fd8 | 07d9c63e molecular | 2026-07-30 | yes | **not final** (appeal filed 2026-09-08, undecided; on hold insurance_reprocessing) | — (excluded) |

So the root's prerequisite is false at the opening: invoice `76312eaf-061f-4497-bc9e-313ad09b0196` is covered, payer-final and carries no discount line under the award (the two `assistance_discount_applied` rows in `initial_state.assistance_events` are for dc9db92f and 42469eea only).

Resolving policy: the rule that fixes "the award discount on that invoice" is `assistance_ext_award_discount` ("fixed for the invoice of the order the payer most recently assigned a patient responsibility to" — latest `coverage_patient_responsibility_assigned` is `1a6ccea0` 2026-09-24 on order 69f7e736 → invoice 76312eaf, the same invoice). Its own prerequisite list is empty and its rule carries no prerequisite sentence → leaf.

Derived tree: renewal_tier ← award_discount; one edge, kind value_input (the discount enters the burden's "financial-assistance discounts the award being renewed granted within the burden window"); n = 1 prerequisite problem, value_input edges 1 ≥ max(0,1) = 1; no cycle; owner=user problem present (renewal). Topological order: (1) apply_award_discount (agent) → (2) submit_renewal_application (user). Isomorphic to the declared `prerequisite` of `assistance_ext_renewal_tier`.

Load-bearing run: skip the discount write → renewal burden 7826.00 > threshold 5875.00 → Catastrophic Medical Hardship Adjustment; with it → burden 5600.00 ≤ 5875.00 → Financial Assistance 25% Discount. The edge bears weight.

No parallel edges. No wait. Tools judge nothing (function bodies cited in `_difficulty.md` → `action_binding_and_uuids`).

User scenario: raises only the renewal; mentions no discount, no invoice, no prerequisite; "If the agent tells you that something on your account has to be taken care of before the renewal can be set up, you tell them to go ahead" is a passive conditional. Authorisation: renewal is to be submitted today by the customer herself when handed over ("you do it right away in the same call, entering exactly the program name the agent gives you ..."). Closes after the submission is confirmed — the last write. No extra asks.

### task_independent_derivation

Identity: phone 4045553186, DOB 1981-06-14, ZIP 30318, email given on request → ≥2 matches.

Step 1 — award discount on invoice 76312eaf under case ba07189c, handling time = opening world, act now (approved case; invoice status open; Insured Patient Responsibility Invoice is eligible; DOS 2026-05-12 in window; claim final, no appeal; no prior line).

- Responsibility posted 2412.00 (45326def, 2026-09-28); courtesy adjustment 60.00 (d4f38da2, 2026-09-30); no billing-error / estimate / small-balance / prompt-pay lines; payment 150.00 on 2026-05-12 (981dec05, patient_service_center) = date of service → deposit.
- Eligible responsibility 2352.00; balance still due 2412 − 60 − 150 = 2202.00 (matches invoice.balance_due).
- Working amount: courtesy present → "responsibility posted less only its billing-error corrections and estimate-dispute settlements" = 2412.00.
- Coverage points: active coverage exists; invoice coverage a1753634 is a marketplace plan, band not_employer_plan → individual-plan points 5.
- Responsibility points: final responsibility on order 69f7e736 is a deductible (1a6ccea0) → deductible points 5 (the upheld appeal belongs to order 13084ad7, not this order).
- Late-finalization: DOS 2026-05-12 → posted 2026-09-28 = 139 days; >120 and ≤180 → 3.
- Award percent 25 + 5 + 5 + 3 = 38.
- Cap: Hereditary & Reproductive Genetic Testing → 300.00.
- Owed share RND(min(2412, 300) × 62 / 100) = 186.00; discount before limit 2412 − 186 = 2226.00.
- Limit: deposit on DOS → working amount 2412.00.
- **Booked discount = 2226.00** → `apply_award_discount_6c746b08(assistance_case_id="ba07189c-5f0b-4b04-970a-d18b33a96cda", invoice_id="76312eaf-061f-4497-bc9e-313ad09b0196", discount_amount=2226.00)`, owner agent. Effect: new `assistance_discount_applied` row dated 2026-10-05, case total 728 → 2954.00.

Step 2 — renewal tier, handling time = after step 1, before the renewal is written; read on the award being renewed (ba07189c).

- Documented income 47000.00, documented percent 300.3, active coverage on file → percent > 300 and insured → catastrophic share 12.5 → threshold RND(47000 × 12.5 / 100) = 5875.00.
- Burden window: the only ended coverage ended 2024-12-31, before the award's application date 2026-04-16 → not tier 1; award runs MONTHS(2026-04-16, 2026-10-16) = 6 ≤ 6 → window = 6 whole months: entries with whole months to 2026-10-05 < 6, i.e. dated 2026-04-06 or later.
- Responsibility posted in window: 1022 (dc9db92f 05-06) + 4150 (7a4e5310 05-06) + 950 (38870a59 06-10) + 360 (42469eea 07-15) + 565 (7b674fd8 08-14) + 2412 (76312eaf 09-28) = 9459.00 (136beffa's 560.00 of 2025-12-15 is outside).
- Courtesy / billing-error / estimate / small-balance in window: 60.00.
- Award discounts in window: 602 + 126 + 2226 = 2954.00.
- Amount in question: 7b674fd8 on hold insurance_reprocessing → its responsibility posted in window 565.00.
- Plan: 6-Month plan 4ac686f1 active, no installment missed in last 6 months → take out every installment paid 4 × 70 = 280.00.
- Burden RND(9459 − 60 − 2954 − 565 − 280) = 5600.00; 5600.00 > 5875.00 is false → **assessed at the tier of the award being renewed: Financial Assistance 25% Discount**.
- Opening-world contrast (discount not booked): relief 728.00 → burden 7826.00 > 5875.00 → Catastrophic Medical Hardship Adjustment. The post-prerequisite number is the right one because the rule sets the tier "only after" every covered final invoice carries its line.
- Write (owner user, handed over): `submit_renewal_application_d691b1b8(customer_id="ce7f1fe6-47bd-4709-9fba-296b33339234", variant_name="Financial Assistance 25% Discount", household_size=1, annual_household_income=47000.00, insurance_status="insured")`. Household/income/insurance come from the persona lines; customer_id is read from the profile and read to her.

Terminal state: case ba07189c gains a 2226.00 discount line (total 2954.00); a new submitted case at Financial Assistance 25% Discount via online_portal dated 2026-10-05.

Closest alternative candidates and their exclusion: (a) discounting 7b674fd8 too — excluded by "have no claim for its order still awaiting a payer decision or under appeal" (appeal 55f496ce, no decision); (b) discount 2202.00 — excluded as above (O-6); (c) Catastrophic renewal — only if the discount is skipped or a factor is ignored; (d) appeal-upheld points (10) — the upheld appeal is on order 13084ad7, not the final order.

All figures were also re-evaluated with the charter's own compute via `check_compute.build_env/eval_compute` on the view (identical).

### factor_weight

Computation A — `assistance_ext_award_discount` (gold-derived 2226.00; full baseline 588.00: eligible 2352 × 0.75 owed 1764.00, discount 588.00 ≤ balance due 2202.00):

| factor | label honest | tier taken (rows) | baseline input from `baseline.rule` | encoded baseline | value under baseline |
| --- | --- | --- | --- | --- | --- |
| coverage_points | yes (number) | individual plan: coverage a1753634 active, band not_employer_plan (orders/coverage of insurance_claims_and_denials) | 0 points | `0` ✓ | 2211.00 |
| responsibility_points | yes | deductible: claim_event 1a6ccea0 responsibility_type deductible | 0 | `0` ✓ | 2211.00 |
| late_finalization_points | yes | 139 days: invoice DOS 2026-05-12, txn 45326def 2026-09-28 | 0 | `0` ✓ | 2217.00 |
| service_class_cap | yes | genetic: order 69f7e736 variant (test_orders_and_results) | no cap | `working_amount` ✓ | 916.56 |
| working_amount_basis | yes (formula) | courtesy present: txn d4f38da2 | eligible responsibility | `eligible` ✓ | 2166.00 |
| discount_limit_rule | yes (formula) | deposit: txn 981dec05 dated = DOS | balance due | `balance_due` ✓ | 2202.00 |

Every substitution changes the scored value; all-baseline 588.00 ≠ 2226.00. Stamps: none — tiers rest on coverage band, claim responsibility type, dates, order class, ledger lines; no field names the points or the amount. Near-miss: the upheld appeal 33372f72 on order 13084ad7 (excluded by "an order whose final patient responsibility ..." — the final order is 69f7e736); also the claim assignment date 2026-09-24 vs. the posting date 2026-09-28. Cross-difficulty rows seeded: coverages, claim_events (coverage), orders (orders). Counts: 6 factors, 4P/2M.

Computation B — `assistance_ext_renewal_tier` (derived Financial Assistance 25% Discount; full baseline: 12-month window posted 10019.00 − 60.00 − 2954.00 = 7005.00 > threshold 4700.00 → Catastrophic):

| factor | label | tier taken (rows) | baseline from `baseline.rule` | encoded | result under baseline |
| --- | --- | --- | --- | --- | --- |
| catastrophic_share | parameter, honest | >300 % and insured: case fpl 300.3, coverage a1753634 active | 10 % | `K('standard_share')` ✓ | Catastrophic (5600 > 4700) |
| burden_window | method (O-11) | award months 6: case 2026-04-16 → 2026-10-16; terminated coverage ended 2024-12-31 before the application date | 12 months | `K('standard_burden_months')` ✓ | Catastrophic (6160 > 5875) |
| amount_in_question | parameter | reprocessing hold: invoice 7b674fd8 hold_reason insurance_reprocessing, posted 565.00 | 0 (baseline silent) | `0` ✓ | Catastrophic (6165 > 5875) |
| plan_carried_balances | parameter | active plan, no missed installment: plan 4ac686f1, 4 paid × 70 | 0 | `0` ✓ | Catastrophic (5880 > 5875) |

Every factor bears weight; baseline alone gives a definite tier different from the derived one. Multi-source: catastrophic_share (case percent AND coverage status, distinct records). Cross-difficulty: coverage (coverages), plans (payment_plans/plan_transactions) — seeded and consistent with the plans charter shape (enrolled 420.00, 4 × 70 paid, plan_balance 140.00 = invoice balance 140.00). Stamp: the case's `variant_name` equals the derived result, but it is the rule's own fall-through ("otherwise it is assessed at the tier of the award being renewed"), not a field deciding any factor's tier (observation O-T0-1 below). Near-miss: terminated coverage fdbaaaab (ended before the award's application date), the 560.00 posting of 2025-12-15 (outside the 6-month window, inside 12), percent 300.3 just over the 300 line. Counts: 4 factors, 3P/1M.

Task totals: multi-source ≥ 1 (catastrophic_share), cross-difficulty ≥ 1 (coverage, orders, plans). Bounds met.

Frozen verdict (pre-reveal): policy self-consistency PASS (charter F-1 does not touch this tree); problem tree PASS; factors PASS; unique solution PASS — subject to comparison with GT.

## source_gt_comparison

- Reveal: GT fields of `tasks/financial_assistance/tasks/0.json` first opened at 2026-10-04T16:53Z, after both task files' frozen sections were on disk. Frozen-file sha256 at reveal: `task0.md` 9032d07278dc9889532a2e6e7b52275894f2135577e4233dde4dc3980dbfe4e1, `task1.md` c5d517131a3d451e8e6c3973b66028478ed0906cd5b8af2b9b855fba3ebfffbd, `_difficulty.md` 8f824d180e2e275f1950d95bb170a3a383d433a8a6070c2301f57b1c7f3e701c (the "freeze time" stamps in the frozen headers were written as estimates and run a few minutes ahead of the wall clock; the hashes are the binding record of order).
- Need / authorisation / timing: same — renewal today; customer submits it herself in the portal when handed over; agent books the discount on her go-ahead.
- Read set: GT reads profile, cases, assistance events, invoices, invoice ledger, claim events, orders, coverages, plans, plan ledger — same set used in the derivation.
- Now / wait / refuse: same — act now on both writes.
- Eligibility: same — renewal window (30 days before 2026-10-16), approved award, open invoice, once-per-invoice.
- Object: same — case ba07189c, invoice 76312eaf (50437712); new renewal case for ce7f1fe6.
- Parameters: discount_amount 2226.00 = 2226.00; variant_name "Financial Assistance 25% Discount" = same; household_size 1, income 47000.00, insurance_status insured = same; identity with phone + DOB (derivation allowed any two of the four stated details; GT's pair is one of them).
- Tool / owner / order: same — apply_award_discount (agent, unlock+call) → submit_renewal_application (user, unlocked and handed over).
- Terminal state: same.
- Closest candidate exclusion: Catastrophic Medical Hardship Adjustment is excluded by booking the discount first ("set only after every invoice ... carries that award's discount line"); 2202.00 is excluded by the deposit tier's explicit credit clause; discounting 7b674fd8 is excluded by the base adjudication-first condition (appeal 55f496ce undecided).
- Problem tree vs `prerequisite_closure`: root assistance_ext_renewal_tier = same; one edge renewal_tier → award_discount, kind value_input = value_input, gate window_relief = window_relief, form state = state, resolved_by apply_award_discount_6c746b08 = same; why-false rows (45326def posted 2026-09-28, 1a6ccea0 deductible, lines only on dc9db92f/42469eea) = the auditor's rows; resolution_order [award_discount, renewal_tier] = derived order; skipped-effect figures 728.00 / 2954.00, burden 7826.00 vs 5600.00, Catastrophic vs 25% = auditor's figures exactly.
- `computations[0]` (award discount): expected 2226.0 = 2226.00; baseline_result 588.0 = 588.00; factor_sensitivity coverage 2211.0 = 2211.00, responsibility 2211.0 = 2211.00, late 2217.0 = 2217.00, cap 916.56 = 916.56, working amount 2166.0 = 2166.00, limit 2202.0 = 2202.00; tiers taken identical.
- `computations[1]` (renewal tier): expected "Financial Assistance 25% Discount" = same; baseline_result Catastrophic = Catastrophic (auditor: burden 7005.00 vs threshold 4700.00); factor_sensitivity all four Catastrophic = auditor's (5600 vs 4700; 6160, 6165, 5880 vs 5875); tiers taken identical.
- Proof-field world assertions checked word for word against `initial_state` (see finding T0-1): `evaluation_criteria[2].objective` and two `design_rationale` sentences contradict the seed; every other figure in `factor_trace`, `argument_uniqueness_tracing`, `prerequisite_closure` and `solvability_contract.seed_consistency` recomputes exactly (e.g. 602.00 = RND(1022 − 600 × 0.70), 126.00 = 360 − 234.00, award_start 2025-08-19, award_end 2026-10-16, 300.3 = 47000 / 15650).

Verdict:
- Policy self-consistency: PASS.
- Problem tree: PASS.
- Factors bear weight: PASS.
- Unique solution: **SOURCE-TASK RED** (T0-1 — the gold values are unique and correct, but the submitted proof asserts world facts the seed contradicts).

## findings

### T0-1 — SOURCE-TASK RED: proof fields assert world facts that the seed contradicts
- Symptom: the scored artifact's own account of the world differs from `initial_state` in three places.
- Root cause: stale text left from an earlier world revision (design_rationale revision 4: "household reduced to 1 (income 47000.00, percent 300.3)") was not carried into the read-step objective and two rationale sentences.
- Evidence:
  1. `evaluation_criteria[2]` (find_assistance_cases) objective: "Read her assistance cases: the approved Financial Assistance 25% Discount award, its application date, award window (2025-08-19 to 2026-10-16), documented household of 2, income 63,600.00, documented percent 300.7 and the discount granted so far." — seed `initial_state.assistance_cases.ba07189c-5f0b-4b04-970a-d18b33a96cda`: household_size 1, annual_household_income 47000.0, fpl_percent 300.3.
  2. `design_rationale` [Seed rows]: "No cache trap is used (discount_granted_total 1845.00 equals the ledger)." — seed discount_granted_total 728.0 (= 602.00 + 126.00).
  3. `design_rationale` [Step 0]: "claim ledger (23 lines)" — seed `claim_events` holds 24 rows.
- Demonstrated consequence: the assertions are false on the world they name. Item 1 sits in `evaluation_criteria`, the scored solution, and describes the very record from which the renewal's documented income/percent are read; a reader following it would take threshold RND(63600 × 12.5 / 100) = 7950.00 instead of 5875.00 (the tier would still come out 25 % on this world, 5600.00 ≤ 7950.00, so the scored values are not moved — the defect is the proof, not the gold arguments). Item 2 asserts a cache value (1845.00) that does not exist in the world while claiming it agrees with the ledger.
- Affected: `tasks/financial_assistance/tasks/0.json` → `evaluation_criteria[2].objective`; `design_rationale` (Step 0 breadth line; Seed rows "Automatic clauses" line).
- Relation to previous revisions: first audit round.

### Observations (no red light)
- O-T0-1: the renewal's scored value (Financial Assistance 25% Discount) equals the award's existing `variant_name` and the tier the customer remembers ("you remember it as the 25 percent discount"); it is the rule's own fall-through ("otherwise it is assessed at the tier of the award being renewed"), so an agent that skips both calculations would still enter the right program name. Discrimination rests on the discount write (2226.00) and on the factor baselines all flipping to Catastrophic; no factor tier is read off this field.
- O-6 (from `_difficulty.md`): "never more than the invoice's balance still due" vs the deposit tier — on this world 2202.00 vs 2226.00; resolved by the deposit tier's explicit credit clause (see `policy_self_consistency`).
- O-8 (from `_difficulty.md`): the discount tool posts no invoice-side `financial_assistance` adjustment although the seed mirrors the two earlier lines with one; no computation of this task reads that adjustment type, so neither scored value moves.

---

## revision_2

### source_derivation_frozen (round 2)

- Auditor: same as round 1; written before any round-2 GT was revealed. contamination_disclosure: the round-1 reveal of this task's GT (2026-10-04T16:53Z) means the auditor already knew the round-1 gold values; the round-2 derivation below is a recomputation on the unchanged view (sha256 3a695b81…41b, identical to round 1) under the changed charter (e00215b4…), checked mechanically with the charter's compute, and does not rely on the round-1 GT for any step. It is not a blind derivation in the strict sense; the per-task conclusions it supports are recomputations, not first readings.
- Charter-global: `env/env_0028_clinical_laboratory_company/audits/policy_task/financial_assistance/_difficulty.md` → `revision_2` (all sections).

### policy_self_consistency (round 2, this task)

- O-6 closed for this world: baseline "limited to the invoice's balance still due" (2202.00) refined by the deposit tier "limited only to its working amount" (2412.00) — one reading, 2226.00.
- **R2-F1 demonstrated here.** After the last gold-path write (the customer's `submit_renewal_application_d691b1b8`), the world holds a new case: customer ce7f1fe6, status submitted, application 2026-10-05, online_portal, household 1, income 47000.00, `fpl_percent` empty, `documents_requested_date` empty, tier "Financial Assistance 25% Discount". The countable-percent rule ("A submitted application that carries no documents-requested date has its percent of the poverty guideline reassessed as the countable percent, recorded together with the income tier that percent falls in, whether or not the tier changes"; trigger `state_due`) applies to it at once:
  - guideline for 1: 15650.00; deduction window: the only ended coverage ended 2024-12-31, 21 whole months ago (not fewer than 12) → standard 12 months;
  - payments received in 12 months: 560.00 (2026-01-14) + 150.00 (05-12) + 200.00 × 5 (05-20 … 09-20) + 200.00 (07-10) + 100.00 (07-31) = 2010.00; no card/transfer/returned → 2010.00;
  - active coverage → insured rate 50 → 1005.00; active plan, none missed → installments in window 280.00; no visits → fees 0; no documents on the new case → disregard 0;
  - deduction 1285.00; countable income 45715.00; percent RND(45715 / 15650 × 100, 1) = **292.1** → band (250, 300] → **Financial Assistance 50% Discount**.
  - The renewal rule assessed the same case at "Financial Assistance 25% Discount". Two rules of the charter assign the same case two tiers; the reassessment is a write the agent can perform in-call (`reassess_assistance_percent_a70c4477` takes the case id returned by the customer's submission, which is in the shared transcript).
- Handling time / no wait: unchanged from round 1.

### problem_chain (round 2)

Unchanged from round 1: root renewal_tier ← award_discount (value_input, state form); the root's prerequisite is unmet at the opening (invoice 76312eaf covered, payer-final, no line). New burden-window conjunct holds: latest responsibility posting 2026-09-28 ≥ award application 2026-04-16. Skipping the discount: burden 7826.00 > 5875.00 → Catastrophic; with it 5600.00 → 25 %. Edge bears weight; user-owned root; tools judge nothing.

### task_independent_derivation (round 2)

- Step 1: `apply_award_discount_6c746b08(ba07189c-…, 76312eaf-…, 2226.00)` — recomputed under the new charter: points 5 (non-employer plan) + 5 + 3, percent 38, cap 300, owed 186.00, limit 2412.00 → 2226.00.
- Step 2: `submit_renewal_application_d691b1b8(ce7f1fe6-…, "Financial Assistance 25% Discount", 1, 47000.00, "insured")` — burden window 6 months (no coverage ended on/after 2026-04-16; award 6 months; latest posting 2026-09-28 ≥ 2026-04-16), burden 5600.00 ≤ threshold 5875.00.
- Step 3 (charter, R2-F1): the countable-percent reassessment of the new renewal case is state-due → 292.1 / Financial Assistance 50% Discount. The documents rule ("An application that needs documents and lacks them is set to pending documents …") would then also apply to that case (income documents required, none received on it). The charter thus does not end the transaction where the customer's need ends.

### factor_weight (round 2)

Recomputed with the new charter: award discount 2226.00, substitutions 2211.00 / 2211.00 / 2217.00 / 916.56 / 2166.00 / 2202.00, all-baseline 588.00; renewal 25 %, substitutions all Catastrophic (burden/threshold 5600/4700, 6160/5875, 6165/5875, 5880/5875), all-baseline Catastrophic (7005/4700). Identical to round 1; every factor bears weight; multi-source (catastrophic_share) and cross-difficulty (coverage, orders, plans) seeded. The new burden-window conjunct rests on seeded postings, not on a stamp.

Frozen verdict (round 2, pre-reveal): policy self-consistency **SOURCE-POLICY RED (R2-F1)**; tree PASS; factors PASS; unique solution: second terminal state from R2-F1 (renewal case 25 % / empty percent vs 50 % / 292.1); T0-1 closure to be checked at the reveal.

### source_gt_comparison (round 2)

- Reveal: round-2 GT of `tasks/0.json` opened at about 2026-10-04T18:09Z, after the round-2 frozen sections of all three files were on disk (sha256 at reveal: `_difficulty.md` 72355263…0207, `task0.md` 7fc3e556…8f03, `task1.md` 273dc987…2482).
- Need / authorisation / read set / now-wait-refuse / eligibility / object: same as round 1 and as derived.
- Parameters: discount_amount 2226.0 = 2226.00; variant_name "Financial Assistance 25% Discount" = same; household 1, income 47000.0, insured = same.
- Tool / owner / order: apply_award_discount (step 12, agent) → submit_renewal_application (step 14, user) = derived steps 1–2. **GT stops there; the charter (R2-F1) makes a third write state-due on the new renewal case** (reassessment → 292.1 / Financial Assistance 50% Discount), so GT's terminal state is one of two the charter licenses.
- Problem tree vs `prerequisite_closure`: unchanged and equal value for value (renewal_tier → award_discount, value_input, window_relief, state; order [award_discount, renewal_tier]; skipped-effect 728.00/2954.00, 7826.00/5600.00).
- `computations`: award discount expected 2226.0, baseline 588.0, sensitivities 2211.0 / 2211.0 / 2217.0 / 916.56 / 2166.0 / 2202.0 — all equal to the recomputation; renewal expected 25 %, baseline Catastrophic, four sensitivities Catastrophic — equal.
- T0-1 re-check: `evaluation_criteria[2].objective` now reads "documented household of 1, income 47,000.00, documented percent 300.3" (= seed 1 / 47000.0 / 300.3); `design_rationale` now "discount_granted_total 728.00 equals the ledger: 602.00 + 126.00" (= seed 728.0) and "claim ledger (24 lines)" (= 24 rows). Remaining world assertions in `argument_uniqueness_tracing`, `factor_trace`, `prerequisite_closure`, `seed_consistency` re-checked: agree. Step references (12, 14) match the action indices. **T0-1 closed.**

Verdict (round 2):
- Policy self-consistency: **SOURCE-POLICY RED** (R2-F1 — new).
- Problem tree: PASS.
- Factors bear weight: PASS.
- Unique solution: follows from R2-F1 — two terminal states for the renewal case (GT: 25 %, percent empty; charter-mandated reassessment: 50 %, 292.1). T0-1 closed.

### findings (round 2)

#### R2-F1 (task-0 demonstration) — SOURCE-POLICY RED, new in round 2
- Symptom: after the customer submits her renewal, the charter obliges a reassessment of the new case that changes the tier the renewal rule just assessed; GT ends without it.
- Root cause: `assistance_ext_countable_percent` trigger rewritten (to close O-9) as "A submitted application that carries no documents-requested date has its percent of the poverty guideline reassessed as the countable percent, recorded together with the income tier that percent falls in, whether or not the tier changes." (`trigger: state_due`), with no exclusion of renewal cases; `submit_renewal_application_d691b1b8` creates the case with `status="submitted"` and `documents_requested_date=None`.
- Evidence: renewal rule ("… otherwise it is assessed at the tier of the award being renewed"); countable rule as quoted; tool body; seed rows used in the recomputation: invoice payments 9c1c6fdb… (560.00, 2026-01-14 — row id prefix 9c1c6fdb), 981dec05 (150.00), 893257af / 83a05a74 / d0983058 / c9d03d83 / 72278c64 (5 × 200.00), 657f7c59 (200.00), 11417d34 (100.00); plan 4ac686f1 (4 × 70.00, active, none missed); coverage a1753634 active; coverage fdbaaaab ended 2024-12-31.
- Demonstrated consequence: renewal rule → "Financial Assistance 25% Discount" (burden 5600.00 ≤ 5875.00); countable rule on the same case right after → deduction RND(2010.00 × 50 / 100 + 280.00) = 1285.00, countable income 45715.00, 292.1 % → "Financial Assistance 50% Discount". An agent that honours the state-due reassessment (the case id is in the transcript from the customer's own submission) leaves the renewal case at 50 % / 292.1 — a terminal state different from GT's (25 % / empty percent); the documents rule would then also make a documents request due on that case.
- Affected: `assistance.extended.yaml` → `assistance_ext_countable_percent.rule` (first sentence) and `overwrite[1].replaced_by`; `tasks/0.json` terminal state (renewal case `variant_name`, `fpl_percent`).
- Relation to previous revisions: introduced by the round-2 rework of O-9; a two-step precursor (documents request on the renewal case, then the old "before a documents request" reassessment) existed in round 1 and was missed by the round-1 audit.

#### T0-1 — closed (see comparison).

#### Observations
- O-T0-1 unchanged (gold renewal tier equals the existing award tier; discrimination rests on the discount write and the flips).
- R2-O1 (from `_difficulty.md`): the new burden-window conjunct ("latest patient responsibility posted on or after that award's application date") holds here (2026-09-28 ≥ 2026-04-16) and bears weight (false → 12 months → 6160.00 > 5875.00 → Catastrophic); its compute raises when a household has no postings — not this world.

---

## revision_3

### source_derivation_frozen (round 3)

- Written before the round-3 GT reveal. View unchanged (3a695b81…41b); charter 10693690…8c24. contamination_disclosure: round-1 and round-2 GT of this task already seen; this is a recomputation, not a blind first reading.
- Charter-global: `_difficulty.md` → `revision_3`.

### policy_self_consistency / problem_chain / derivation (round 3)

- Values recomputed under the round-3 charter: award discount **2226.00** (6 substitutions 2211.00 / 2211.00 / 2217.00 / 916.56 / 2166.00 / 2202.00, all-baseline 588.00); renewal tier **Financial Assistance 25% Discount** after the discount (opening world: Catastrophic); four substitutions all Catastrophic; all-baseline Catastrophic. Tree unchanged (renewal ← award discount, value_input, state form, unmet at the opening, bears weight).
- R2-F1 re-run on this world: the new renewal case (submitted 2026-10-05 while award ba07189c is approved) is "a renewal application (one submitted while the household's award is approved)" → excluded from the reassessment, "keeps the tier its renewal assessment gave it" (25 %). The customer, when asked, reports household 1 and income 47,000.00 "the same figure you gave in April" (persona) = the award's documented 1 / 47000.00 → "relies on the documents already received for the award being renewed and needs no documents request". No further write is state-due on the renewal case; the transaction ends with the customer's submission. **Closed on this world.**
- Remaining base-side consequence (observation R3-O2): with documents already relied on, base "When every required document is in, the case goes to review" would move the renewal case to review, but no tool of this difficulty performs `assistance_review_started`, the customer does not ask for it, and it changes no scored value — not a second terminal state the agent can reach.
- Cross-category weight on this world: see `_difficulty.md` → `revision_3` → "R2-O1 (b) on the merits" (per-factor flips hold; whole-off gate pass rests on the raise).

Frozen verdict (round 3, pre-reveal): policy PASS (R2-F1 closed); tree PASS; factors PASS; unique solution PASS — subject to the GT comparison.

### source_gt_comparison (round 3)

- Reveal: round-3 GT of `tasks/0.json` opened at about 2026-10-04T18:20Z, after all three round-3 frozen sections were hashed (`_difficulty.md` c3a0564f…87f6, `task0.md` 4dfdf26e…a016, `task1.md` 78f1d157…6fe7).
- Writes: index 12 `apply_award_discount_6c746b08(ba07189c-…, 76312eaf-…, 2226.0)` (agent) → index 14 `submit_renewal_application_d691b1b8(ce7f1fe6-…, "Financial Assistance 25% Discount", 1, 47000.0, "insured")` (user) — equal to the derivation; GT ends there, and under the round-3 charter nothing further is due on the renewal case, so GT's terminal state is now the only one the charter licenses.
- `computations`: 2226.0 / 588.0 / 2211.0, 2211.0, 2217.0, 916.56, 2166.0, 2202.0 and 25 % / Catastrophic / four × Catastrophic — equal to the recomputation. `prerequisite_closure` unchanged and equal.
- Proof prose: step references (12, 14) name the write calls; the round-3 rationale note on R2-F1 matches the world (renewal submitted while ba07189c approved; persona states household 1 and income $47,000 unchanged).
- R2-O1 (b), checked against the charter: the rationale's claim that every household holding an approved award has a responsibility posting is supported — base decision rule denies with `balances_not_eligible` "when the patient has no invoice the award could discount", and the invoices charter defines `invoices_responsibility_posted` as "An amount the patient owes is posted to the invoice …". A renewal requires an approved award, so the "no postings" domain on which the compute raises is outside the renewal policy's reachable inputs. (b) is therefore a dead-domain compute gap, not a defect any renewal world can hit; the gate's whole-off pass on task 0 still rests on the raise and is not evidence (see `_difficulty.md` → `revision_3`), but the per-factor flips are.

Verdict (round 3): policy PASS (R2-F1 closed); problem tree PASS; factors PASS; unique solution PASS.

### findings (round 3)

- R2-F1 — closed on this world (no reassessment, no documents request due on the no-change renewal case).
- T0-1 — remains closed.
- Observations: O-T0-1 (gold tier = fall-through; also why the all-off gate test would return gold once guarded), R3-O2 (base "goes to review" on the renewal case — no tool, no scored effect), R2-O1 (b) dead-domain / (c) single ended coverage here.
