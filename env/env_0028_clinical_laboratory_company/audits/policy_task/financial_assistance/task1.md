# Policy-task audit — financial_assistance / task 1

## source_derivation_frozen

- Auditor: Claude (erl-task-policy-audit), independent; freeze time 2026-10-04T17:00Z (wall clock), before any task's GT was revealed (task 0's GT also unrevealed at this point).
- Freeze hashes: view `task1.view.json` 9aee0b1b5fe829c21433648f2dc78ce45946f63654a0a4376668895f8703ae01; `assistance.extended.yaml` 1e06045e…41b; `task_tools.py` 4260086c…2e9.
- Permitted: `frozen_time`, `user_scenario`, `initial_state` via the masked view; charter, tool contracts, schema, share tools.
- Masked and unread at freeze: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, worklog.
- contamination_disclosure: none.

World: frozen 2026-10-06 (Tuesday). Customer Calvin Yarborough `9c691564-…5a09e5a`, portal_enrolled false. Case `270f7c7f-d050-4a30-9f22-687bbb33ecc2`: Financial Assistance Full Discount, status submitted, application 2026-09-28 phone_assisted, household 4, income 44900.00, fpl 139.7, uninsured, no documents requested/due date, extension_count 0. Eight `assistance_document_received` rows (tax return dated 2024-12-31; pay stubs ×3; unemployment statements dated 2026-08-31 and 2026-09-28; Social Security letter; zero-income attestation). Coverages: employer plan 99ddd347 terminated 2026-06-30; Medicaid Managed Care Plan e12a2990 pending_verification. No active coverage.

### policy_self_consistency (this task only)

- Charter-global checks: `env/env_0028_clinical_laboratory_company/audits/policy_task/financial_assistance/_difficulty.md` → `override_declarations`, `rule_compute_equivalence`, `action_binding_and_uuids`, `prerequisite_sentences`, `prerequisite_graph`, `factor_ladders`. F-1 (`response_start` mislabelled; `assistance_ext_document_period` has no honest method factor) bears on this task's tree — consequence shown under `factor_weight`. O-9 (countable_percent's own rule restates the order of edge 2) points the same way as the declared edge on this world too: both say reassess, then issue the request — no second order arises.
- Handling time (check 4): countable percent on the opening world; document period on "opening + reassessed percent/tier"; extension on "opening + reassessment + documents request (requested 2026-10-06, due date set)".
- No real-world wait (check 5): all inputs are seeded rows, the synchronous effects of the two agent writes, or customer statements; the extension is the customer's own in-call portal action.

### problem_chain

Root problem (customer's only ask): more time to send documents → `assistance_ext_document_extension` (user tool `request_document_extension_ca0bff0a`). Customer: "I need more time to get my paperwork to you"; he knows no due date.

Root's prerequisite sentence: "The extended due date is not fixed until the case carries a documents-requested date and a documents due date." At 2026-10-06 the case has `documents_requested_date` null and `documents_due_date` null → false at the opening.

The write that brings that state about: the policy whose rule sets "a documents due date that falls the response days after the request date" — `assistance_ext_document_period` (`request_assistance_documents_a6db5abf`, agent). Is a documents request due? The application "needs documents" (Full Discount: income documentation required). Its prerequisite sentence: "The response period of a documents request is fixed only after the case's percent of the poverty guideline has been reassessed on the household's countable income." The recorded 139.7 is the intake figure; the countable percent is 133.1 (below) → not yet reassessed → false at the opening.

Resolving policy for that: `assistance_ext_countable_percent` (`reassess_assistance_percent_a70c4477`, agent), whose rule opens "Before a documents request is issued on a submitted application, the case's percent ... is reassessed as the countable percent and recorded together with the income tier ...". Its prerequisite list is empty → leaf.

After reassessment (133.1, uninsured, Full Discount screening line 138), base documentation rule: "An uninsured applicant whose fpl_percent is at or below a non-zero medicaid_screening_fpl_threshold_pct must also provide a Medicaid application or denial" — no `medicaid_application_or_denial` document is on file → the application lacks a required document → the documents request is due (act now).

Derived tree: extension ← document_period ← countable_percent; edges: (extension→document_period, value_input via `due`/`days_left`), (document_period→countable_percent, value_input via `recorded_pct`→`agency_days`). n = 2, value_input edges 2 ≥ max(1,1); owner=user problem: extension; acyclic. Topological order: (1) reassess (agent) → (2) documents request (agent) → (3) extension (user). Isomorphic to the declared `prerequisite` fields.

Load-bearing runs:
- Skip the reassessment, issue the request on 139.7: agency allowance 5 instead of 15 → response days 50 instead of 62 (and the extension becomes 40 instead of 38, because the due date moves to Wednesday 2026-11-25). Bears weight.
- Skip the documents request: the case has no due date; the extension has no current due date to count from (the rule's state is unmet; compute evaluation fails on `DAYS(NOW, None)`), and the tool would count from today. Bears weight.

No parallel edges; no wait; tools judge nothing (`_difficulty.md` → `action_binding_and_uuids`; `request_document_extension` silently counts from today when no due date exists).

User scenario: raises only the extension; mentions no reassessment and no request; the passive conditional "If the agent tells you that something has to be updated or sent out on your application before more time can be given, you tell them to go ahead" responds only after the agent says so. Customer facts on request: household 4, income 44900, coverage ended 2026-06-30, Medicaid applied 2026-10-01 and pending, no portal, pays by phone/mail. Closes after the new due date is confirmed — the last write. The 2025 tax-return remark is context for the ask, not a second ask.

### task_independent_derivation

Identity: phone 4045559024, DOB 1972-11-03, ZIP 30344 → 3 matches.

Step 1 — countable percent (opening world).
- Guideline for 4: 15650 + 3 × 5500 = 32150.00.
- Deduction window: coverage 99ddd347 ended 2026-06-30, whole months to 2026-10-06 = 3 < 12 → 3 + 1 = 4 months: entries dated 2026-06-07 or later.
- Payments received in window: 300 (06-12 credit card), 250 (07-09), 180 (07-28 hsa_fsa_card), 150 (08-14 check/mail), 100 (08-29 ACH), 104 (09-24) = 1084.00; returned 100.00 (e1063863, 09-03). HSA/FSA card used → count 1084 − 180 − 0 − 100 = 804.00. (30.00 of 2026-04-14 outside.)
- Recognition rate: no active coverage; test charges posted on orders in last 12 whole months = 11 (≥ 6) → full rate 100.
- Plan installments: plan de1208fd active, no missed installment in 6 months → every installment paid in window: 06-20, 07-20, 08-20, 09-20 = 200.00 (05-20 outside).
- Collection fees: no homebound certification; a trip fee paid 2026-09-21 → trip 75 + additional-patient 35 + weekend 0 = 110.00 (no-show fee 60 excluded).
- Disregard: unemployment statement dated 2026-09-28 (0 days before application) → job-loss disregard 1000.00.
- Deduction RND(804 × 100/100 + 200 + 110) = 1114.00; countable income 44900 − 1000 − 1114 = 42786.00; percent RND(42786 / 32150 × 100, 1) = **133.1**; band (0, 200] → **Financial Assistance Full Discount**.
- Write: `reassess_assistance_percent_a70c4477(assistance_case_id="270f7c7f-d050-4a30-9f22-687bbb33ecc2", fpl_percent=133.1, variant_name="Financial Assistance Full Discount")`, agent.

Step 2 — documents request (after step 1).
- Tier documents due days 30 (Full Discount).
- Agency: no active coverage, recorded 133.1 ≤ screening line 138 → Medicaid screening days 15 (opening world: 139.7 > 138 → 5).
- Tax return: only return received is dated 2024-12-31; whole months to the application date 2026-09-28 = 20 > 12 → stale-return days 10.
- Household earner: size 4 (≥ 3, < 5) with pay stubs and benefit statement/letter → two-earner days 7.
- File credit: 8 documents received ≥ 6 → 3 off.
- Response start: applied by phone; no portal payment in 12 months; mail/phone payments yes → mailed; issued Tuesday → next day, +1.
- Counted 30 + 15 + 10 + 7 − 3 + 1 = 60; 2026-10-06 + 60 = Saturday 2026-12-05 → +2.
- **Response days = 62** (due 2026-12-07, Monday). Write: `request_assistance_documents_a6db5abf(assistance_case_id="270f7c7f-…ecc2", response_days=62)`, agent. Effect: status pending_documents, requested 2026-10-06, due 2026-12-07.

Step 3 — extension (after step 2), customer's own act.
- Tier document extension days 15.
- Stay allowance: facility bedside collection c7778238 collected 2026-09-10 (26 days) → 7.
- Time-left credit: 2026-10-06 → 2026-12-07 = 62 days > 40 → 5 off.
- Household letter: Social Security letter received → 3 (zero-income attestation is the excluded near-miss).
- Coverage loss: ended 2026-06-30, 98 days ≤ 120 → 3.
- Pending coverage: Medicaid Managed Care Plan pending verification → 5.
- Adjusted 15 + 7 + 3 + 3 + 5 − 5 = 28.
- Counting: application taken by phone; no portal payment, mail/phone payments in 12 months → business days from the current due date (Monday): 28 = 5 × 5 + 3 → 35 + 3 = 38, remaining 3 days (Tue–Thu) do not run past Friday → +0.
- **Extension days = 38** (new due date 2027-01-14). Write, handed over: `request_document_extension_ca0bff0a(assistance_case_id="270f7c7f-…ecc2", extension_days=38)`, owner user. extension_count 0 < max 1 → allowed.

Terminal state: case 270f7c7f at fpl 133.1 / Full Discount, pending_documents, requested 2026-10-06, due 2027-01-14, extension_count 1.

Root contrast on the opening world: not computable (no current due date; the rule withholds the extended date "until the case carries ... a documents due date"); on the "request without reassessment" world it would be 40.

Closest alternatives and exclusion: (a) no documents request because the file looks complete at 139.7 — see observation O-T1-1 below; the reassessment the doc-period rule requires first puts the percent at 133.1 ≤ 138 for an uninsured applicant, making the Medicaid application/denial a required, missing document; (b) agency 0 by treating the pending Medicaid plan as coverage — excluded, "no active coverage on file" and the plan's status is pending_verification; (c) calendar counting (28) — excluded by the phone/payment-channel tier; (d) extension from today — excluded by the rule ("the current documents due date plus the extension days").

All figures re-evaluated with the charter's compute via `check_compute.build_env/eval_compute` on the view (identical).

### factor_weight

Computation A — `assistance_ext_countable_percent` (derived 133.1; full baseline: 12-month payments 1114 − 100 = 1014 × 50 % = 507.00 → 44393 / 32150 → 138.1):

| factor | label | tier (rows) | baseline | encoded | value under baseline |
| --- | --- | --- | --- | --- | --- |
| deduction_window | method (O-11) | coverage ended 2026-06-30 → 4 months (coverages, insurance_claims_and_denials) | 12 | ✓ | 132.8 |
| recognition_rate | parameter | no active coverage AND 11 test charges (coverages + order_events) | insured 50 | ✓ | 134.3 |
| payment_kinds | method | HSA/FSA card payment 330d77b7 | all − returned | ✓ | 132.5 |
| plan_installments | parameter | active plan, no misses (plans) | 0 | ✓ | 133.7 |
| collection_fees | parameter (O-11) | trip fee paid 99a84647 (visits) | 0 | ✓ | 133.4 |
| benefit_disregard | parameter | unemployment statement dated 2026-09-28 | 0 | ✓ | 136.2 |

All bear weight. Near-misses: 30.00 payment of 2026-04-14 and the 2026-05-20 installment (outside the 4-month window), no-show fee 60.00 (not a counted fee type), unemployment statement of 2026-08-31 (also qualifying, not decisive). Stamp: case `insurance_status = uninsured` agrees with "no active coverage on file" but the rule reads the coverages; it names a condition, not a tier outcome (no consequence). Counts: 6 (4P/2M). Multi-source: recognition_rate.

Computation B — `assistance_ext_document_period` (derived 62; full baseline 30):

| factor | label | tier (rows) | baseline | encoded | value under baseline |
| --- | --- | --- | --- | --- | --- |
| agency_allowance | parameter | no active coverage, 133.1 ≤ 138 | 0 | ✓ | 45 |
| tax_return_allowance | parameter | stale return (doc 14fd89bc dated 2024-12-31) | 0 | ✓ | 50 |
| household_earner_allowance | parameter | size 4 with stubs + benefit docs | 0 | ✓ | 55 |
| file_credit | parameter | 8 documents | 0 | ✓ | 63 |
| response_start | **labelled method; tiers are constants 3/1/0 (F-1)** | mailed, Tuesday → +1 | 0 | ✓ | 59 |
| weekend_move | parameter | 2026-12-05 Saturday → +2 | 0 | ✓ | 60 |

Every factor bears weight; baseline 30 ≠ 62. Near-miss: the pending Medicaid plan (not active coverage); the 2024 return (received, but stale). Cross-difficulty: coverage (agency). Counts as labelled 5P/1M; **as honestly labelled 6P/0M — below the bound of 1 method (F-1)**.

Computation C — `assistance_ext_document_extension` (derived 38; full baseline 15):

| factor | label | tier (rows) | baseline | encoded | value under baseline |
| --- | --- | --- | --- | --- | --- |
| stay_allowance | parameter | bedside c7778238 2026-09-10 (visits) | 0 | ✓ | 29 |
| time_left_credit | parameter | 62 days left | 0 | ✓ | 45 |
| household_letter_allowance | parameter | SS letter 3fac3589 | 0 | ✓ | 35 |
| coverage_loss_allowance | parameter | ended 2026-06-30, 98 days (coverages) | 0 | ✓ | 35 |
| pending_coverage_allowance | parameter | Medicaid MCP e12a2990 pending (coverages) | 0 | ✓ | 31 |
| counting_convention | method | phone application, phone/mail payments only (invoice_transactions) | calendar | ✓ | 28 |

All bear weight. Near-misses: mobile in-home collection 2026-09-21 (outranked by the bedside tier), zero-income attestation (outranked by the SS letter), no-show home visit. Counts 6 (5P/1M).

Task totals: multi-source ≥ 1 (recognition_rate), cross-difficulty ≥ 1 (coverage, orders, plans, visits), all seeded.

Frozen verdict (pre-reveal): policy self-consistency PASS; problem tree PASS; **factors SOURCE-FACTOR RED (F-1 on computation B)**; unique solution PASS subject to GT comparison.

## source_gt_comparison

- Reveal: GT fields of `tasks/financial_assistance/tasks/1.json` first opened at about 2026-10-04T16:54Z, after both task files' frozen sections were on disk (task 0's GT was opened first, at 16:53Z; nothing from it entered this file's frozen section, which was already hashed: `task1.md` c5d517131a3d451e8e6c3973b66028478ed0906cd5b8af2b9b855fba3ebfffbd). The "freeze time" stamp in the frozen header was an estimate a few minutes ahead of the wall clock; the hash is the binding record of order.
- Need / authorisation / timing: same — more time for documents; agent may update/send what is needed first; the customer files the extension himself in-call.
- Read set: GT reads profile, case, case documents, coverages, invoices, invoice ledger, orders, order events, plans, plan ledger, visits, visit events — same as the derivation.
- Now / wait / refuse: same — act now on all three writes.
- Eligibility: same — submitted case, no due date, extension_count 0 < 1.
- Object: same — case 270f7c7f.
- Parameters: fpl_percent 133.1 = 133.1; variant_name Financial Assistance Full Discount = same; response_days 62 = 62 (due 2026-12-07); extension_days 38 = 38 (due 2027-01-14).
- Tool / owner / order: reassess (agent) → request documents (agent) → extension (user, handed over) = same.
- Terminal state: same.
- Closest candidate exclusion: 50 (request on the unreassessed 139.7) excluded by "fixed only after ... reassessed"; 40 extension days (due date from the 50-day request) excluded with it; 28 calendar days excluded by the phone/payment-channel counting tier; agency 0 (pending Medicaid treated as coverage) excluded by "no active coverage on file".
- Problem tree vs `prerequisite_closure`: root assistance_ext_document_extension = same; edge 1 extension → document_period: value_input / days_left / state / request_assistance_documents_a6db5abf = same; edge 2 document_period → countable_percent: value_input / agency_days / action / reassess_assistance_percent_a70c4477 = same; why-false (requested/due null, status submitted; 139.7 vs 133.1) = same rows and values; resolution_order [countable_percent, document_period, document_extension] = derived; skipped effects: response 50 vs 62 (Wednesday 2026-11-25) = auditor's 50 and 2026-11-25; extension uncomputable without a due date = same.
- `computations` countable_percent: expected 133.1 = 133.1; baseline_result 138.1 = 138.1; sensitivity 132.8 / 134.3 / 132.5 / 133.7 / 133.4 / 136.2 = auditor's figures exactly; tiers identical.
- `computations` document_period: expected 62 = 62; baseline_result 30 = 30; sensitivity 45 / 50 / 55 / 63 / 59 / 60 = auditor's; tiers identical. GT's own trace for response_start ("tier 'mailed request on any other day' -> count from the next day (+1); baseline counts from the request date and gives 59") confirms the factor contributes a constant +1 — F-1.
- `computations` document_extension: expected 38 = 38; baseline_result 15 = 15; sensitivity 29 / 45 / 35 / 35 / 31 / 28 = auditor's; tiers identical.
- Proof-field world assertions (design_rationale, factor_trace, argument_uniqueness_tracing, prerequisite_closure, seed_consistency) checked against the seed: all recompute (e.g. 139.7 = 44900 / 32150; Medicaid plan added 2026-10-02 "two business days ago" = Mon 10-05 and Tue 10-06; eleven test charges; installments 06-20…09-20 = 200.00; no-show 60.00 excluded).

Verdict:
- Policy self-consistency: PASS.
- Problem tree: PASS.
- Factors bear weight: **SOURCE-FACTOR RED** (F-1 on computation B — every factor bears weight, but the computation has no honest `method` factor).
- Unique solution: PASS.

## findings

### T1-1 — SOURCE-FACTOR RED: the documents-request computation has no method factor (charter finding F-1, demonstrated here)
- Symptom: `assistance_ext_document_period`, scored at `request_assistance_documents_a6db5abf.response_days` = 62, declares `response_start` as its only `method` factor, but that factor only adds a constant number of days.
- Root cause: mislabelled effect — see `env/env_0028_clinical_laboratory_company/audits/policy_task/financial_assistance/_difficulty.md` → `findings` F-1.
- Evidence (this world): `start_days` = K('mail_start_days') = 1 (phone application, no portal payment, phone/mail payments, Tuesday), entering `counted_days = 30 + 15 + 10 + 7 − 3 + 1 = 60` exactly like `agency_days` 15, `tax_days` 10, `earner_days` 7 (all `parameter`); GT `computations[1].factor_trace` describes the same: "count from the next day (+1); baseline counts from the request date and gives 59".
- Demonstrated consequence: the three tiers of `response_start` select 3, 1 and 0 days into one unchanged sum, so the honest label is `parameter`; computation B then has 6 parameter factors and 0 method factors, below the bound of at least 1 method per computation. An agent that reads the request's computation document and its factor documents is never asked to change how the response period is computed, only to add numbers.
- Affected: `assistance.extended.yaml` → `assistance_ext_document_period.factors` (response_start `effect`; the policy's factor set); scored step: `request_assistance_documents_a6db5abf.response_days` in `tasks/1.json`.
- Relation to previous revisions: first audit round.

### Observations (no red light)
- O-T1-1 (documents request "owed"): the base rule issues a request only for an application that "needs documents ... and lacks them", and the charter names no required-document list beyond the Medicaid-screening and proof-of-enrollment sentences. On the opening percent 139.7 (> 138) the file holds accepted income documents (spouse's pay stubs, unemployment statements), so whether anything is lacking is not settled by the records; after the reassessment the doc-period rule requires first (133.1 ≤ 138, uninsured), the Medicaid application or denial becomes required and is absent, which makes the request due. Reading backwards from the customer's ask (extension ← due date ← request ← reassessment) gives one path; the alternative "file is complete, nothing to extend" would need the agent to judge completeness on a percent the charter says to reassess before any request, and contradicts the customer's stated outstanding 2025 return. No second defensible terminal state demonstrated.
- O-T1-2: both "Insured Patient Responsibility Invoice" rows (ba638273, f0eca26d) carry patient-responsibility postings with no `claim_events` at all (design_rationale revision 2 removed them); no computation of this task reads claims, so no scored value is affected.
- O-T1-3: the case's `insurance_status = uninsured` agrees with the "no active coverage on file" tier conditions of recognition_rate and agency_allowance; it names a condition, not a tier outcome, and the coverages it summarises are seeded, so reading either gives the same tier.
- O-9 (from `_difficulty.md`): countable_percent's own rule restates the reassess-before-request order; on this world it points the same way as the declared edge.

---

## revision_2

### source_derivation_frozen (round 2)

- Auditor: same as round 1; written before any round-2 GT was revealed. contamination_disclosure: the auditor saw this task's round-1 GT (2026-10-04T16:54Z); the round-2 derivation is a recomputation on the new view (sha256 856ff29f…e0) under the new charter (e00215b4…), not a strict blind first reading.
- View change found by comparison with the round-1 view content recorded in this file: `claim_events` now holds 6 rows (esoteric order b1133647: claim submitted 2026-05-12, denied PR-204 2026-06-02, patient-billable denial assigned 2026-06-04 → posting d157c3ab now links claim 8191b047; pathology order b2af2e02: submitted 2025-11-18, contractual 70.00 2025-12-01, deductible 330.00 assigned 2025-12-02 → posting b3c34704 links bccdc2e9). All other tables as in round 1 (same ids and values).
- Charter-global: `env/env_0028_clinical_laboratory_company/audits/policy_task/financial_assistance/_difficulty.md` → `revision_2`.

### policy_self_consistency (round 2, this task)

- F-1 closed for this computation: `response_count_convention` is an honest method factor; this world takes its phone tier ("calendar days from the next business day after the request date", Tuesday → +1).
- R2-F1 does not reach this task: after the extension the only case carries a documents-requested date, so the countable-percent trigger no longer applies; no other submitted case exists.
- The rewritten countable-percent trigger now makes the reassessment state-due at the opening by itself (case submitted, no documents-requested date), which settles O-T1-1's ordering question: reassess first (133.1), then the Medicaid application or denial is required and missing, so the documents request is due.
- O-T1-2 closed: both insured invoices now rest on seeded claim adjudications consistent with their postings (1022.00 = billed 1022.00 denied; 330.00 = 400.00 − 70.00). No computation reads claims.

### problem_chain (round 2)

Unchanged: extension ← documents request (state) ← reassessment (action); both edges value_input; unmet at the opening (no requested/due date; recorded 139.7 ≠ countable 133.1); user-owned root; skipping the reassessment → 50 response days (and 40 extension days); skipping the request → no due date to extend. Tools judge nothing.

### task_independent_derivation (round 2)

- Reassess: 133.1, Financial Assistance Full Discount (window 4 months, payments counted 804.00, rate 100, plan 200.00, fees 110.00, disregard 1000.00 — the most recently received unemployment statement, received 2026-10-01, dated 2026-09-28).
- Documents request: allowance 30 + 15 + 10 + 7 − 3 = 59; phone tier → calendar count from the next business day (+1) = 60; 2026-10-06 + 60 = Saturday → +2; **62** (due 2026-12-07).
- Extension (customer): 15 + 7 + 3 + 3 + 5 − 5 = 28 business days from Monday 2026-12-07 → **38** (due 2027-01-14).

### factor_weight (round 2)

- countable_percent: 133.1; substitutions 132.8 / 134.3 / 132.5 / 133.7 / 133.4 / 136.2; all-baseline 138.1.
- document_period: 62; substitutions agency 45, tax 50, earner 55, file credit 63, **response_count_convention 59** (baseline `allowance_days` = 59, Friday, no move), weekend 60; all-baseline 30. Honest counts 5 P / 1 M.
- document_extension: 38; substitutions 29 / 45 / 35 / 35 / 31 / 28; all-baseline 15.
- Every factor bears weight; multi-source (recognition_rate) and cross-difficulty (coverage, orders, plans, visits) seeded.

Frozen verdict (round 2, pre-reveal): policy PASS; tree PASS; factors PASS (F-1 closed); unique solution PASS — subject to the GT comparison.

### source_gt_comparison (round 2)

- Reveal: round-2 GT of `tasks/1.json` opened at about 2026-10-04T18:09Z, after all three round-2 frozen sections were hashed (`task1.md` 273dc987…2482 at reveal).
- Need / authorisation / timing / now-wait-refuse / eligibility / object: same as derived.
- Read set: GT adds `find_claim_events` (objective: pathology deductible assigned 2025-12-02, esoteric PR-204 denial transferred 2026-06-04, both on the employer plan ended 2026-06-30, neither appealed — matches the new seed rows).
- Parameters: fpl_percent 133.1 / Full Discount, response_days 62, extension_days 38 = derived.
- Tool / owner / order: reassess (agent, index 15) → request documents (agent, 17) → extension (user, 19) = derived.
- Terminal state: same.
- Problem tree vs `prerequisite_closure`: equal value for value (edges, kinds, gates, forms, resolved_by, why-false rows, order, skipped effects 50 vs 62 and "no due date").
- `computations`: countable 133.1 / baseline 138.1 / sensitivities 132.8, 134.3, 132.5, 133.7, 133.4, 136.2; document period 62 / 30 / 45, 50, 55, 63, **59 (response_count_convention)**, 60; extension 38 / 15 / 29, 45, 35, 35, 31, 28 — all equal to the recomputation. `computations[].step` = 15 / 17 / 19 = the call indices.
- F-1 / T1-1: closed (honest method factor `response_count_convention`, bears weight 62 → 59).
- O-T1-2: closed (claims seeded and consistent).
- Proof-field world assertions re-checked word for word: **four prose step references were not updated when the read `find_claim_events` shifted the write indices by one** (see R2-T1-1). Everything else agrees.

Verdict (round 2):
- Policy self-consistency: PASS (R2-F1 does not reach this world).
- Problem tree: PASS.
- Factors bear weight: PASS (F-1 / T1-1 closed).
- Unique solution: **SOURCE-TASK RED** (R2-T1-1 — new, introduced by the rework); the scored values themselves are unique and correct.

### findings (round 2)

#### R2-T1-1 — SOURCE-TASK RED (new, regression of the rework): proof prose names the wrong gold steps
- Symptom: after `find_claim_events` was inserted at index 7, the reassessment, request and extension calls moved to indices 15, 17, 19 (`computations[].step` and the `prior_step:` evidence were updated), but four prose assertions still name 14 and 16.
- Evidence:
  1. `solvability_contract.gold_actions[1].stage_provenance.fact` (step 17): "The request is issued by this write; the percent it reads was reassessed by step 14." — index 14 is `unlock_agent_discoverable_tool(reassess_assistance_percent_a70c4477)`, no DB effect; the reassessment is index 15 (its own `evidence` says `prior_step:15`).
  2. `solvability_contract.gold_actions[2].stage_provenance.fact` (step 19): "… established by the documents request at step 16." — index 16 is the unlock of `request_assistance_documents_a6db5abf`; the request is 17 (`evidence: prior_step:17`).
  3. `computations[1].factor_trace` (agency_allowance): "recorded percent 133.1 after step 14".
  4. `computations[2].factor_trace` (time_left_credit): "value from step 16".
- Demonstrated consequence: replaying the gold sequence, the case's `fpl_percent` is still 139.7 after index 14 (agency allowance would read 5, response 50) and `documents_due_date` is still empty after index 16 (the extension is uncomputable); the assertions are false on the world they name, and each contradicts the machine pointer in the same object. Scored arguments are not moved.
- Affected: `tasks/1.json` → `solvability_contract.gold_actions[1..2].stage_provenance.fact`, `computations[1].factor_trace` (agency_allowance line), `computations[2].factor_trace` (time_left_credit line).
- Relation to previous revisions: introduced in round 2 by the O-T1-2 rework (read inserted, indices shifted).

#### Observations
- O-T1-1 now resolved on the merits: the rewritten countable-percent trigger makes the reassessment state-due at the opening by itself, after which the Medicaid application or denial is required and missing, so the documents request is due — one path.
- The historical `[Revisions] 2)` note ("claim lines … removed, the responsibility postings carry no claim link") describes the round-1 state and is explicitly superseded by the `[Round 2 — audit items closed]` O-T1-2 note; recorded as a history line, not a current-world assertion.
- O-T1-3 unchanged.

---

## revision_3

### source_derivation_frozen (round 3)

- Written before the round-3 GT reveal. View unchanged (856ff29f…e0); charter 10693690…8c24. contamination_disclosure: round-1/2 GT already seen; recomputation.
- Charter-global: `_difficulty.md` → `revision_3`.

### derivation (round 3)

- The case (no award on file) is not a renewal application → the countable-percent trigger still applies at the opening; the document-period carve-out does not apply.
- Recomputed: reassessment **133.1 / Financial Assistance Full Discount**; documents request **62** (allowance 59, Tuesday phone tier +1 → 60, Saturday 2026-12-05 → +2); extension **38**. Substitutions: countable 132.8 / 134.3 / 132.5 / 133.7 / 133.4 / 136.2 (all 138.1); document period 45 / 50 / 55 / 63 / 59 / 60 (all 30); extension 29 / 45 / 35 / 35 / 31 / 28 (all 15). Tree, edges, load-bearing runs unchanged.
- The Saturday change does not touch this world (request on a Tuesday).

Frozen verdict (round 3, pre-reveal): policy PASS; tree PASS; factors PASS; unique solution: R2-T1-1 closure to be checked at the reveal.

### source_gt_comparison (round 3)

- Reveal: round-3 GT of `tasks/1.json` opened at about 2026-10-04T18:20Z, after the round-3 frozen sections were hashed (`task1.md` 78f1d157…6fe7).
- Writes: index 15 reassess (133.1, Full Discount, agent) → 17 request documents (62, agent) → 19 extension (38, user) — equal to the derivation; `computations[].step` 15/17/19; values, baselines and sensitivities equal (133.1/138.1/…; 62/30/45, 50, 55, 63, 59, 60; 38/15/29, 45, 35, 35, 31, 28); `prerequisite_closure` equal.
- R2-T1-1 re-check: `gold_actions[1].stage_provenance.fact` "reassessed by step 15", `gold_actions[2]` "documents request at step 17", agency trace "after step 15", time-left trace "value from step 17"; every `step N` in the file is now in {15, 17, 19} and names a write call; `prior_step` evidence 15/17 agrees. **Closed.**
- No new world assertion contradicts the seed.

Verdict (round 3): policy PASS; problem tree PASS; factors PASS; unique solution PASS.

### findings (round 3)

- R2-T1-1 — closed. F-1/T1-1 — remains closed. O-T1-1 resolved (round 2), O-T1-3 unchanged.
