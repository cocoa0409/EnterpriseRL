# Policy-task audit — extended_day_care_billing / charter-global

## revision_1

## charter_global_frozen
- Frozen: 2026-10-24T18:45Z, auditor = independent policy-task auditor (not the instantiator), coordinator brief /tmp/erl0078_coord/audit_common.txt.
- Hashes (sha256, first 16): care.extended.yaml = 33463bf8e3171674, task_tools.py = a001eba4a12f1c92 (recomputed; equal to the gate snapshot). Views 0.view.json = f8e6f971cf83ed1f, 1.view.json = 96b747cbab561650 (recomputed; equal).
- Read for this section: blueprint/blueprint.yaml, blueprint/products/care.yaml (base), blueprint/products/meals.yaml (cross-product reads), blueprint/share_tools.py (finder signatures), tasks/extended_day_care_billing/care.extended.yaml, task_tools.py, audits/render_source/XF_recipe.md, audits/render_source/owner_ruling.md.
- Masked / unread at this point: tasks/*.json (all GT keys: evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure*), plan.md, worklog.md, other audits. No recursive grep was run over the difficulty directory.
- Entry conditions (step 0): gate snapshot /tmp/erl0078_coord/snap_extended_day_care_billing_r1.txt supplied — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (--check), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; masked views with hashes supplied. Inputs complete.
- Base copy: lines 1-1120 of care.extended.yaml are byte-identical to blueprint/products/care.yaml (`diff` empty).
- Scratch: /tmp/audit_extended_day_care_billing_0078/ (basis_sweep.txt, recompute.py).

### policy_conflict_scan
Six extended policies: P1 care_ext_meal_rate_tuition_credit (care_credit billing_correction on a tuition charge), P2 care_ext_late_pickup_fee_schedule (care_late_pickup_fee), P3 care_ext_late_fee_reassessment (care_credit billing_correction on a late payment fee), P4 care_ext_account_settlement_payment (care_payment, owner=user), P5 care_ext_notice_period_credit (care_credit notice_period_adjustment), P6 care_ext_prior_year_installment_payment (care_payment, owner=user).
- Overlapping subjects: care_credit is written by P1, P3, P5. P1/P3 share credit_reason billing_correction but differ by source charge type (tuition charge vs late payment fee); P5 uses notice_period_adjustment. Base grain "one row per credited source charge per credit reason" keeps them apart. No conflict.
- care_payment is written by P4 and P6. P6 is scoped to an earlier-school-year enrollment by its rule. P4 is scoped to no enrollment status at all ("A family that asks to settle a Creek Kids Club enrollment"). On a closed (withdrawn) enrollment its advance clause still fires, though base care_tuition_rate says "Tuition charges post only to an enrollment in status active or suspended_nonpayment". See finding C-SCOPE-1.
- Triggers / time anchors: P2 re-prices the base trigger care_evt_late_pickup → care_late_pickup_fee. P3 re-prices the base late payment fee. P1 changes base tuition pricing (overwrite of the starting point and of the rate-basis sentence). P1 also leaves the base sentence "A School Nutrition status change recorded during a month affects the next posting, never a tuition charge already posted" in force, which its own target contradicts. See C-OVR-1.
- Cross-category read boundary: every policy reads meals (meal_accounts via CPARAM/CFIELD status='active', meal_benefit_applications via XLATEST). These are declared in cross_category. meals belongs to difficulty meal_account_and_benefits, so the reads are cross-difficulty. No write touches meals. Trigger rule (D4): none of the six tools writes an event whose base triggers land in another category (care_credit, care_late_pickup_fee and care_payment have `triggers: []`).
- Scope partition (inferred from the prerequisite graph, before any reveal): component A = {P1, P2, P3, P4} with root P4, and component B = {P5, P6} with root P6. Together they cover all 6 policies, with no shared node. Whether tasks 0 and 1 claim exactly A and B is checked after the reveal.

### rule_compute_equivalence
- Verbatim sweep (B5, /tmp/audit_extended_day_care_billing_0078/basis_sweep.txt): every compute_basis quote, every baseline.rule sentence, every overwrite replaced_by and every prerequisite policy_source is a substring of its own rule (whitespace-normalised). No tool name or policy id appears in any rule.
- P1: charge selection, posting date, sibling position, proration, recorded rate basis, holiday share, meal-status ladder, status-count ladder, MX(status, recorded), single RND at the end, and the not-above-zero floor all map one-to-one. Exception: tier 1 of status_count_date. The rule says "a status resting on an approved household application filed with a SNAP, TANF or FDPIR case number". Compute tests only the household's most recently submitted application for the school year (`application_basis == K('case_number_basis') and application_determination in K('approved_determinations')`). It never tests whether the account's status rests on that application, although meal_accounts.meal_benefit_application_id records exactly that. See C-A9-1.
- P2: per-minute ladder, billed-minutes ladder, after-hours ladder, hardship ladder, notice ladder and the single rounding all map. The compute for "the second or later chargeable late pickup of that semester" counts every chargeable row of the semester. This equals the rank of the priced pickup only because the priced pickup is the latest one.
- P3: corrected unpaid part, base fee, scale, repeat addition, hardship, the ordered assembly and the two roundings map. "at least two late payment fees for earlier billing months of the school year" is implemented as COUNT(all late payment fees on the enrollment) − 1. That is equivalent only while the priced fee is the latest billing month and the enrollment spans one school year (observation O5).
- P4: the open-balance list of event types equals the rule's list. Advance share, advance base, hardship, autopay and the single rounding map.
- P5: the final charge, the notice request (latest by created_at), tenure, the weekday via reference_monday 2025-12-01 (a Monday, checked), the counting shift, the billing end, the refund ladder, the uplift and the rounding map. The baseline sentence of the rule contradicts two sentences of the same rule (C-OVR-2).
- P6: open balance, size scale, hardship, returned-payment rule, up-front rule, older-balance addition, MX(1, …) floor, MN(open balance, …) cap and the single rounding map.

### action_binding_and_uuids
- (target_tool, computes): (post_meal_rate_tuition_credit_43720724, credit_amount) P1; (post_late_pickup_fee_6e670263, fee_amount) P2; (post_late_fee_review_credit_38483e38, credit_amount) P3; (pay_extended_day_settlement_f9b88247, payment_amount) P4; (post_notice_period_credit_667047da, credit_amount) P5; (pay_prior_year_installment_d4311e53, payment_amount) P6. Each pair is claimed once.
- uuid8s 43720724 / 6e670263 / 38483e38 / f9b88247 / 667047da / d4311e53 share no prefix or suffix and form no sequence. Each looks independently generated.
- Tool bodies: each checks only argument format (positive, cent-exact, YYYY-MM-DD, payment-method enum) and that the enrollment exists, then calls ctx.create once. None reads the ledger, the attendance log or another tool's rows, so no tool judges a prerequisite. Rounding uses a Decimal ROUND_HALF_UP static method (B4/B6 satisfied).
- Docstrings: none names another tool or a sequence position. One ordering word is present: post_late_fee_review_credit_38483e38 says "…a late payment fee … after the fee has been re-assessed." It refers to the tool's own computation, not to another problem, so it is observation O2.
- Owner: P4 and P6 are owner=user payments. Each rule states that the family pays personally through the portal or the cashier and that the desk never takes card details. That is ruling (b) of owner_ruling.md. No base sentence assigns payment posting to staff, so no overwrite is needed.

### prerequisite_graph
| edge | blocked → depends on | kind / gate | form | fallback | resolved_by = target_tool | acyclic |
|---|---|---|---|---|---|---|
| E1 | P3 → P1 | value_input / corrected_unpaid (exists) | action | present | yes | yes |
| E2 | P4 → P1 | value_input / open_balance (exists) | action | present | yes | yes |
| E3 | P4 → P2 | value_input / open_balance | state | n/a | yes | yes |
| E4 | P4 → P3 | value_input / open_balance | action | present | yes | yes |
| E5 | P6 → P5 | value_input / open_balance_now (exists) | action | present | yes | yes |
P1, P2 and P5 declare `prerequisite: []`. Every `problem` is an extended id of this file, none points at itself or at a base policy, and the graph is a DAG. Every policy_source is located verbatim in its own rule (sweep). No authoring-viewpoint wording appears. Each condition matches the derived handling-time state.

### prerequisite_sentences
- E1, "A late payment fee is re-assessed only after the tuition charge of its billing month has been re-priced for the meal status that counts on that charge's posting date." Connective: only after. Business-language action. No tool or id. Fallback tested: P1 books nothing when the difference is not above zero, so no state singles the write out, and the fallback is justified. **Second wording:** the same rule also says "This policy re-assesses the enrollment's most recently posted late payment fee once the tuition charge of that fee's billing month carries a billing correction credit". That is a state-form statement of the same dependency, and it is narrower (it says nothing is re-assessed when the re-pricing booked nothing). See C-PRE-1. Derivation: "re-priced for the meal status that counts on that charge's posting date" → P1's rule ("credits back the part of a posted … tuition charge that the student's School Nutrition meal status should have taken off it") → post the P1 credit. This reading is unique, but P1 re-prices only "the enrollment's most recently posted tuition charge" (C-PRE-2).
- E2, "The settlement amount is fixed only after the enrollment's most recently posted tuition charge has been re-priced for the meal status that counts on its posting date." Connective: only after. The action is P1, and the scope matches P1's scope exactly. Fallback justified as for E1. No second wording.
- E3, "The settlement amount is not fixed until every late pickup recorded as chargeable on the enrollment carries its late pickup fee entry." Connective: not until. State form, record-visible (care_attendance_log fee_status chargeable; care_ledger care_late_pickup_fee service_date). Exactly one write of the difficulty creates a care_late_pickup_fee row (P2's tool). The sentence covers every chargeable pickup, but P2 prices only "the enrollment's most recent late pickup recorded chargeable" (C-PRE-2).
- E4, "The settlement amount is fixed only after every late payment fee whose billing month's tuition charge carries a billing correction credit has been re-assessed on the corrected tuition." Connective: only after. Action → P3. Fallback justified (nothing is booked when the whole fee stands). The sentence scopes "every" such fee while P3 re-assesses only the most recent one (C-PRE-2, observation-level here).
- E5, "The first installment is not fixed until the enrollment's final billed month has been credited for the part of its tuition that the notice period does not reach." Connective: not until. Action → P5. Fallback justified (nothing is booked when the refund share is 0). No second wording.
- The depended-on rules (P1, P2, P3, P5) do not restate any of these sentences. No docstring states an order (see O2).

### override_declarations
Sentence-by-sentence against each base_policy_refs entry (findings only):
- P1 vs care_tuition_rate:
  - S1/S2 (posting day, open-seat gate): followed.
  - S3 "The starting point is the plan's monthly_tuition.": declared, replaced by the 2026-27 holiday share (scope restated).
  - S4 rate basis: declared, replaced.
  - S5 sibling: followed.
  - S6 proration: followed.
  - S7 rounding: followed.
  - **S8 "A School Nutrition status change recorded during a month affects the next posting, never a tuition charge already posted"**: NOT declared, and P1's whole effect contradicts it. P1 credits back a tuition charge already posted, because of a status recorded later. See C-OVR-1.
  - S9 subsidy: followed (no CCS rows).
  - P1 vs care_agg_sibling_billing, care_evt_registration_fee, care_evt_day_fees, care_billing_and_late_payment, care_withdrawal_and_refunds: followed. Credits are linked to their source charge, which is consistent with base care_credit grain.
- P2 vs care_evt_late_pickup:
  - S3 fee formula: declared.
  - S6 no discounts: declared. The replaced_by keeps "not discounted by rate basis" while adding a meal-benefit-level share (realism, C-REAL).
  - S1, S2, S4, S5, S7: followed.
- P3 vs care_billing_and_late_payment:
  - S2 flat fee: declared.
  - S1 oldest-first allocation: followed.
  - S3/S4 courtesy waiver: separate reason, followed.
  - S5–S7 suspension and withdrawal: followed.
  - P3 vs care_payments_and_returns: "a returned payment never counts as paid" is honoured by payment_counted. Other refs: followed.
- P4: overwrite []. Against care_payments_and_returns S1–S4 and care_billing_and_late_payment S1–S7: no sentence is handled differently, and the certified-funds rule is inherited. The advance has no base counterpart. On a closed enrollment it collides with care_tuition_rate S2 (C-SCOPE-1).
- P5 vs care_withdrawal_and_refunds:
  - S2 and S3: declared.
  - S1 (family's own act), S4 (district withdrawal), S5 (refund) and S6 (registration fee never refunded): followed.
  - The rule restates the retired S2/S3 content as its own baseline sentence (C-OVR-2).
- P6 vs care_admission:
  - S4 prior-year block: declared with its scope restated.
  - Other sentences: followed.
  - P6 vs care_payments_and_returns: followed.

### factor_ladders
| policy | factor | label | tiers | multi-source | cross_difficulty | distinct outcomes | real (line of business) | label honest / shape (A6) | own-binding only (A1) | embedded in recorded amount (A8) |
|---|---|---|---|---|---|---|---|---|---|---|
| P1 | meal_status_discount | parameter | 3 | yes (account ∨ application) | meals | yes | yes | yes | yes | no |
| P1 | status_count_date | method | 3 | yes | meals | yes | yes (USDA lets an LEA date eligibility from submission) | yes (different date input / added upper bound) | **no**: status_counts reads application_determination, a binding of meal_status_discount | no |
| P1 | holiday_month_share | parameter | 4 | no | – | yes | plausible | yes | yes | **yes**: posted 2026-27 charges already carry the share (care_tuition_rate S3 overwrite) |
| P1 | recorded_sibling_discount | parameter | 3 | no | – | yes | restates base sibling ladder | yes | yes | **yes**: the posted charge already carries the sibling position; baseline 0 is a straw man |
| P2 | per_minute_rate_ladder | parameter | 3 | yes (warning row ∧ chargeable count) | – | yes | yes | yes | yes | no |
| P2 | billing_increment | method | 3 | no | – | yes | plausible | **no**: quarter-hour vs 5-minute block are the same ceil(m/b)·b with a constant b | yes | no |
| P2 | after_hours_charge | parameter | 3 | no | – | yes | plausible | yes | yes | no |
| P2 | pickup_hardship_share | parameter | 3 | no (one meal account) | meals | yes | **no** | yes | yes | no |
| P2 | notice_stage_charge | parameter | 3 | no | – | yes | **no** | yes | yes | no |
| P3 | charge_size_base_fee | parameter | 3 | no | – | yes | plausible | yes | yes | **yes** (the posted fee is already priced by it) |
| P3 | unpaid_amount_scale | method | 3 | no | – | yes | observation (proportional tier) | yes (data-proportional tier) | yes | no |
| P3 | repeat_month_addition | parameter | 3 | no | – | yes | plausible | yes | yes | **yes** |
| P3 | late_fee_hardship_share | parameter | 3 | no | meals | yes | **no** | yes | yes | **yes** |
| P4 | advance_share | parameter | 3 | yes (late fees ∧ warning) | – | yes | **no** (late-pickup warning is not a payment-risk condition) | yes | yes | no |
| P4 | advance_base_rule | method | 3 | no | – | yes | plausible | yes | yes | no |
| P4 | advance_hardship_share | parameter | 3 | no | meals | yes | **no** (double-counts the meal rate already in the advance base) | yes | yes | yes (base already at the meal rate) |
| P4 | autopay_relief | parameter | 3 | no | – | yes | **no** | yes | yes | no |
| P5 | tenure_notice_length | parameter | 3 | no (one span) | – | yes | plausible (observation) | yes | yes | no |
| P5 | notice_counting_day | method | 3 | no | – | **no**: Saturday and Sunday tiers both select "counted from the Monday after it" | next-business-day idea real | **no**: every tier is notice date + constant shift | yes | no |
| P5 | withdrawal_refund_share | parameter | 5 | no | – | yes | yes | yes | **no**: refund_end_offset reads notice_length and counting_shift | no |
| P5 | withdrawal_hardship_uplift | parameter | 3 | yes (application ∧ notice date) | meals | yes | **no** (credit can exceed the charge) | yes | yes | no |
| P6 | balance_size_scale | parameter | 3 | no | – | yes | yes | yes | yes | no |
| P6 | hardship_installment_scale | parameter | 3 | no | meals | yes | yes | yes | yes | no |
| P6 | returned_payment_rule | parameter | 3 | no | – | yes | plausible | yes | yes | no |
| P6 | up_front_rule | method | 3 | yes (tier 2: no late fee ∧ returned fee) | – | yes | plausible | **no**: tiers 1 and 2 are the same "LATEST amount up front" on one field | yes | no |
| P6 | older_balance_addition_rule | parameter | 3 | no | – | yes | **no** | yes | yes | no |

Declared counts: P1 4 (3 parameter, 1 method), P2 5 (4/1), P3 4 (3/1), P4 4 (3/1), P5 4 (3/1), P6 5 (4/1). All ladders are stated in full in their rules, and every tier is implemented in compute.

Counts surviving the tests (struck: A1, A6, A8 and realism failures):

| policy | surviving factors | parameters | methods | multi-source |
|---|---|---|---|---|
| P1 | meal_status_discount | 1 | 0 | 1 |
| P2 | per_minute_rate_ladder, after_hours_charge | 2 | 0 | – |
| P3 | unpaid_amount_scale | 0 | 1 | – |
| P4 | advance_base_rule | 0 | 1 | – |
| P5 | tenure_notice_length | 1 | 0 | – |
| P6 | balance_size_scale, hardship_installment_scale, returned_payment_rule | 3 | 0 | none |

Every policy falls below the 4–6 / 2-parameter / 1-method bound (C-COUNT).

### findings
Charter-global, each naming the tasks it bears on (the consequence is demonstrated in the task file).

**C-OVR-1 — SOURCE-POLICY RED (undeclared override; bears on task 0).**
- Symptom: P1 credits back part of a tuition charge already posted, because of a meal status determined after posting.
- Root cause: base care_tuition_rate keeps "A School Nutrition status change recorded during a month affects the next posting, never a tuition charge already posted". No overwrite of P1 names this sentence; P1's overwrite list retires only the starting-point and rate-basis sentences. P1's own replaced_by also keeps "The rate basis is still decided once per billing month from the records on the posting date". On the posting date no approved application exists in the records, yet P1 counts the status retroactively from submission.
- Consequence: two defensible values for the same credit (no credit under the base sentence, a credit under P1). Demonstrated in 0.md. Artifact: care.extended.yaml P1 `overwrite`.

**C-OVR-2 — SOURCE-POLICY RED (C3, rule reinstates the clause its own overwrite retires; bears on task 1).**
- The P5 rule states "the notice period now runs for the length the notice-length schedule below sets, counted in calendar days from the notice's counting day as day 0". It also states "a billing month in which the billing end falls is no longer always billed in full".
- The same rule then states "The billing end is the later of the requested last day and the last day of the notice period, the notice period being withdrawal_notice_days calendar days counted from the notice date as day 0; a month any day of which falls on or before the billing end is billed in full". That is the content of the retired base clause.
- The same situation therefore gets two conclusions: the final month billed in full, or partly credited. Demonstrated in 1.md.
- The same pattern, in softer form, appears in P1 ("The re-priced charge is the plan's monthly_tuition…" vs the 2026-27 starting point), P2 ("The standard late pickup fee is …", labelled standard) and P3 ("The fee the corrected tuition supports is late_payment_fee…" vs "instead of at the flat late_payment_fee"). There each rule's assembly sentence states that the schedules act on that amount, so one reading remains: observation O1.

**C-PRE-1 — SOURCE-POLICY RED (check 6: second wording of an edge; bears on task 0).**
- P3's rule carries E1 twice: as the declared action-form sentence ("only after … has been re-priced"), and as a state-form trigger ("re-assesses … once the tuition charge of that fee's billing month carries a billing correction credit").
- The two have different scope. When the re-pricing books nothing, the state wording says no re-assessment happens, while the action wording and the edge's condition ("or the re-pricing has shown that none is owed") say the re-assessment proceeds.
- On task 0's world the credit is booked, so both wordings agree there (see 0.md). The defect is charter-level.

**C-PRE-2 — SOURCE-POLICY RED (D1: resolvers cannot satisfy their edges in every engaged world).**
- (a) E3 waits until "every late pickup recorded as chargeable … carries its late pickup fee entry". P2 prices only "the enrollment's most recent late pickup recorded chargeable", and asserts "fees post in service-date order" (a framing clause no record guarantees, B8).
  - Producible world: two chargeable pickups without fees.
  - The older one can never get a fee, so P4 waits forever.
- (b) E1 waits for the re-pricing of "the tuition charge of its billing month". P1 re-prices only "the enrollment's most recently posted tuition charge".
  - Producible world: frozen 1–10 December, with the latest late fee for November and the latest charge December.
  - The November charge can never be re-priced, so P3 is blocked.
- Neither world is task 0's (one unposted pickup; latest fee and latest charge both November), so it is an observation in 0.md.

**C-SCOPE-1 — SOURCE-POLICY RED (omission in P4's scope; bears on no scored task).**
- P4 applies to "a Creek Kids Club enrollment" of any status. Its advance clause adds "the next billing month's tuition" whenever ≥ 2 late payment fees are carried.
- Base care_tuition_rate: "Tuition charges post only to an enrollment in status active or suspended_nonpayment".
- Producible world: task 1's household (withdrawn 2025-26 enrollment, 2 late payment fees, no warning, free status, no ACH payments in the last 3 months) asking to settle in full. P4 gives open balance + 64.00 × 50% × 50% × 100% = +16.00 in advance for a month that can never post. The amount then becomes a credit balance refundable under care_withdrawal_and_refunds. The policy gives a definite but contradictory treatment of closed enrollments.

**C-A1 — SOURCE-FACTOR RED (A1, factor reads factor; bears on tasks 0 and 1).**
- P1: status_counts (factor status_count_date) reads application_determination, a binding of factor meal_status_discount.
- P5: refund_end_offset (factor withdrawal_refund_share) reads notice_length (factor tenure_notice_length) and counting_shift (factor notice_counting_day).
- Evidence: compute lines of status_counts and refund_end_offset in care.extended.yaml.

**C-A2 — SOURCE-FACTOR RED (A2, assembly sentences name factor quantities; bears on tasks 0 and 1).**
- P3: "the base late fee is first multiplied by the share the unpaid-amount scale sets, the repeat-month addition is then added, and that sum is then multiplied by the hardship share".
- P4: "the advance is the advance base, multiplied in turn by the advance share, by the hardship share and by the part of the advance that the autopay relief leaves".
- P5: "the notice-length schedule and the counting-day rule decide …, the withdrawal refund schedule turns …, and the hardship uplift then raises …".
- P6: "the installment count is the count the balance-size scale sets plus the extra installments of the hardship scale less the installments the returned-payment rule takes away … the amount paid up front … the older-balance addition is then added".
- P1 and P2 state the combination generically, so they comply.

**C-A6 — SOURCE-FACTOR RED (A6 method shape / mislabelled method; bears on tasks 0 and 1).**
- P2 billing_increment: tier 1 "whole quarter hours of quarter_hour_minutes" and tier 2 "whole blocks of block_minutes" are the same operation ⌈m/b⌉·b with constant b (15 vs 5).
- P5 notice_counting_day: the Saturday and Sunday tiers both select "counted from the Monday after it" (two tiers, one method). All three tiers are notice date + a constant shift (2/1/0), which is a parameter labelled method.
- P6 up_front_rule: tier 1 (LATEST amount of care_late_payment_fee) and tier 2 (LATEST amount of care_returned_payment_fee) are one input (field amount, different filter) in the same combination.

**C-A8 — SOURCE-FACTOR RED (A8, factor already embedded in a recorded amount; straw-man baseline; bears on task 0).**
- P1 holiday_month_share and recorded_sibling_discount. The posted charge was priced with the holiday share (P1's own overwrite of care_tuition_rate S3) and with the recorded sibling position. baseline.rule re-prices without them, to a figure above what the standard method posted.
- P3 charge_size_base_fee, repeat_month_addition and late_fee_hardship_share. The posted late payment fee was priced by this same schedule. baseline.rule re-assesses at the flat late_payment_fee, above the posted fee.
- P4 advance_hardship_share. The advance base (the corrected charge) already carries the free/reduced-meal rate, and the share discounts it again.

**C-A9-1 — SOURCE-FACTOR RED (A9, ladder text vs compute; bears on task 0 structurally).**
- status_count_date tier 1 text: "the status rests on an approved household application filed with a SNAP, TANF or FDPIR case number". Compute: the household's latest application for the school year is case-number based and approved, with no link to meal_accounts.meal_benefit_application_id.
- Producible world: account Free Meal Status (Direct Certification), application id empty, effective after the charge's posting date; household's latest application case-number based, approved_reduced, submitted before posting.
- Compute counts the status (tier 1) and grants the free discount. The text gives tier 3, so the status does not count and no credit is due.

**C-REAL — SOURCE-FACTOR RED (F1/F2, tiers no Texas district publishes; bears on tasks 0 and 1).**
- P2 notice_stage_charge: a 5.00 / 15.00 "notice charge" for issuing a warning letter.
- P2 pickup_hardship_share: a late-pickup penalty halved or cut by a quarter by meal status. Base says late pickup fees are not discounted by rate basis, and the meal status is that same basis under another name.
- P3 late_fee_hardship_share: a late payment fee cut by meal status, the same 50/75 share pasted onto a third charge type.
- P4 advance_share: a prepayment requirement whose size turns on a late-pickup warning letter, which is not a payment-risk condition.
- P4 advance_hardship_share: see C-A8.
- P4 autopay_relief: a 25 % / 50 % waiver of the prepayment counted from manual ACH portal payments. No autopay record exists (B7).
- P5 withdrawal_hardship_uplift: raises a notice-period credit by 25 % / 10 %. With credited share 100 % and an approved_free household, the credit is 125 % of the charge, contradicting base event care_credit "Credit amount, positive USD, never more than the source charge".
- P6 older_balance_addition_rule: adds 15.00 / 5.00 to the first installment by the age of the balance. It is a payment-plan surcharge that is not a fee, and it pushes the "first installment" toward the whole balance.

**C-COUNT — SOURCE-FACTOR RED (bounds after strikes; bears on tasks 0 and 1).** See the surviving-counts table above. Every policy has fewer than 4 surviving factors. P1, P2, P5 and P6 have no surviving method, and P3 and P4 have fewer than 2 surviving parameters. Task 1's surviving factors (P5 tenure_notice_length; P6 balance_size_scale, hardship_installment_scale, returned_payment_rule) contain no multi-source factor.

Observations (not grounds for rework):
- O1: the P1/P2/P3 baseline-sentence pattern described in C-OVR-2.
- O2: docstring ordering word "after" in post_late_fee_review_credit_38483e38.
- O3: meals base meals_benefit_effective_dates dates a new status from its determination date, while P1 counts a case-number application's status from submission for tuition. This is a cross-product divergence the KB will show side by side.
- O4: base care_withdrawal event field says end_date is "the notice's requested last day or the end of the notice period, whichever is later", while base care_withdrawal_and_refunds S2 (and P5) say the last day of care is the requested last day. This is a base-internal inconsistency; seeds follow the policy sentence.
- O5: P3 repeat-month count is COUNT − 1 with no billing-month or school-year filter.
- O6: plausible-but-padded ladders: P5 tenure_notice_length (7/10/14-day notice by tenure), P3 unpaid_amount_scale (proportional tier between 5 and 25 USD), P2 three-tier billing increment.
- O7: P2 framing clause "fees post in service-date order".
- O8: P4 "autopay" names no autopay record.

## closing_checklist
Written after both reveals.
- Audit files 0.md and 1.md correspond one-to-one to tasks 0 and 1, alongside this file. This is revision_1.
- Coverage and scope:
  - charter_scope task 0 = {P1, P2, P3, P4} and task 1 = {P5, P6}. They are disjoint, together cover all 6 extended policies, and each spans its whole tree.
  - Tools are closed and GT uses only them.
  - uuid8s are independent.
- Trees: task 0 has 3 prerequisites with 4 value_input edges; task 1 has 1 with 1 value_input edge. Each has an owner=user root. The difficulty-wide graph is acyclic.
- Factors: NOT met. See C-COUNT, C-A1, C-A2, C-A6, C-A8, C-A9-1 and C-REAL. Every declared factor does move its scored value on its task's world, and every baseline gives a definite number different from gold.
- Policy self-consistency: NOT met (C-OVR-1, C-OVR-2, C-PRE-1, C-PRE-2, C-SCOPE-1).
- Gates were not re-run on a final form, because the difficulty does not close in this revision.
- **The difficulty does not pass the source-layer audit in revision_1.**

VERDICT revision_1: task0=RED task1=RED charter=C-OVR-1,C-OVR-2,C-PRE-1,C-PRE-2,C-SCOPE-1,C-A1,C-A2,C-A6,C-A8,C-A9-1,C-REAL,C-COUNT

## revision_2

## charter_global_frozen (revision_2)
- Frozen 2026-10-24T21:30Z by the same independent auditor. Brief: the coordinator message for round 2, audits/render_source/realism_bar.md (new ruling, read in full), owner_ruling.md, XF_recipe.md.
- Entry checks:
  - Last non-empty worklog line is `REWORK round 2: gates 7/7 green` (checked).
  - Gate snapshot /tmp/erl0078_coord/snap_extended_day_care_billing_r2.txt, produced by running snapshot.sh (execute-only): all 7 gates OK.
- Hashes and views:
  - care.extended.yaml d109b94b74fc0bc5 and task_tools.py 38804948550844e6 (recomputed; both CHANGED from r1, so every charter-global section is re-derived below and nothing is carried forward).
  - Views r2/0.view.json 1b1b5f0ea1773bf5 and r2/1.view.json a899300bfd4e10e1 (recomputed).
  - Base prefix (lines 1-1120) is still byte-identical to blueprint/products/care.yaml.
- Read: the worklog section "REWORK round 2 claims" by item id only (lines truncated). The worklog's "Round 2 rebuild" section and plan.md were not read.
- tasks/*.json were not read before the freezes below.
- Scratch: /tmp/audit_extended_day_care_billing_0078/basis_sweep_r2.txt and recompute_r2.py.

### policy_conflict_scan (r2)
New charter, six policies:
- Q1 care_ext_late_pickup_fee_schedule → post_late_pickup_fee_6e670263
- Q2 care_ext_late_payment_fee_schedule → post_late_payment_fee_d20db65b (new tool)
- Q3 care_ext_booked_day_fee_schedule → post_booked_day_fee_4f9449e5 (new tool)
- Q4 care_ext_current_year_payment_plan → pay_extended_day_settlement_f9b88247, owner=user
- Q5 care_ext_notice_period_credit → post_notice_period_credit_667047da
- Q6 care_ext_prior_year_installment_payment → pay_prior_year_installment_d4311e53, owner=user

Findings:
- Subjects: Q1 writes care_late_pickup_fee; Q2 care_late_payment_fee; Q3 care_day_fee; Q5 care_credit (notice_period_adjustment); Q4 and Q6 write care_payment, Q4 scoped by its rule to current-school-year enrollments and Q6 to earlier-year ones. No subject overlap.
- Triggers: all written events have base `triggers: []`, so the D4 trigger rule is met.
- Cross-category reads: Q1 and Q3 read enroll (grade on the school-year record); Q4 reads meals; Q5 reads enroll (status and withdrawal_date); Q6 reads meals and enroll. All are other difficulties' categories, and none is written.
- Inferred components: A = {Q1, Q2, Q3, Q4} with root Q4; B = {Q5, Q6} with root Q6. Disjoint and jointly complete.
- Conflict: Q2's unpaid-part measurement contradicts in-force base sentences (C-OVR-3).

### rule_compute_equivalence (r2)
- Verbatim sweep (basis_sweep_r2.txt): every compute_basis quote, baseline sentence, replaced_by and policy_source is in its own rule. No tool name or policy id appears in any rule.
- Q1:
  - The 2026-27 schedule vs the other-year standard is implemented by `F('school_year') == K('schedule_year')`.
  - Grade, repeat, billed minutes and after-hours each map one-to-one, with a single rounding.
- Q2:
  - Fee method, base fee, stage and repeat map. `days_past_due` = DAYS(month start, NOW) + 1 − due day, i.e. days past due on the posting day, which is what the rule says.
  - The unpaid part counts only the single most recent payment in the window. That matches the rule text but contradicts the base allocation (C-OVR-3).
- Q3: selection, grade supplement, lead days, frequent count, the MX(0, …) floor and the "no fee when no rate" gate map. The rule's "latest by the time it was received" is LATEST by created_at.
- Q4: balance scale, semester limit (MONTHS + 1 to Dec/May), hardship, returned-payment rule, the MX(1, MN(scale, cap) + hardship − returned) count, the payment rule and the MN(open, …) cap map.
- Q5:
  - notice_length additionally requires `notice_on_file >= 1`. The text does not state this, and it is inert, because the result is 0 without a notice (observation R2-O3).
  - Convention tier 2 compute differs from its text (C-A9-2).
  - The rest maps.
- Q6: size, hardship, returned-payment, residence, installment rule, floor and cap map.

### action_binding_and_uuids (r2)
- Six distinct (target_tool, computes) pairs, each claimed once.
- New uuid8s d20db65b and 4f9449e5 share nothing with each other or with 6e670263 / f9b88247 / 667047da / d4311e53.
- Every body checks format, enum and existence only, then calls ctx.create once. No tool judges a prerequisite.
- Docstrings carry no cross-tool sequence. "then shows in the billing history" describes the effect, and "first payment / first installment" is a business term. The r1 tool carrying "after" is retired, so O2 is closed.
- Owner: Q4 and Q6 rules state that the family pays itself through the portal or the cashier and that the desk never takes card details (owner_ruling (b)). No base sentence assigns payment posting to staff.

### prerequisite_graph (r2)
| edge | blocked → depends on | kind / gate | form | resolved_by | condition matches |
|---|---|---|---|---|---|
| F1 | Q4 → Q1 | value_input / open_balance | state | post_late_pickup_fee_6e670263 | yes (latest chargeable pickup) |
| F2 | Q4 → Q2 | value_input / open_balance | state | post_late_payment_fee_d20db65b | yes (latest charge, de-minimis carve-out) |
| F3 | Q4 → Q3 | value_input / open_balance | state | post_booked_day_fee_4f9449e5 | yes (latest booking, "owes a fee") |
| F4 | Q6 → Q5 | value_input / open_balance_now | action + fallback_reason | post_notice_period_credit_667047da | yes |

Q1, Q2, Q3 and Q5 declare `[]`. The graph is acyclic.

### prerequisite_sentences (r2)
- F1, "The first plan payment is not fixed until the enrollment's most recently recorded chargeable late pickup carries its late pickup fee entry." Connective: not until. State form, record-visible. Only Q1's tool creates care_late_pickup_fee. Q1 prices exactly "the enrollment's most recently recorded chargeable late pickup", so D1 is satisfiable in every engaged world.
- F2, "The first plan payment is fixed only after the enrollment's most recently posted tuition charge carries its late payment fee entry whenever the part of it left unpaid on its due day owes one." Connective: only after. State form. The zero case is carved out by "whenever … owes one" (D2). Only Q2's tool creates care_late_payment_fee. Q2 prices exactly the latest charge's fee.
- F3, "The first plan payment is fixed only after the enrollment's most recent drop-in booking request carries its booked-day fee entry whenever the booked day owes a fee." Connective: only after. State form, with the zero case carved out. Only Q3's tool creates care_day_fee. Q3 prices exactly the latest booking.
- F4: unchanged from r1 (E5). The fallback is justified (nothing is booked when the share is 0).
- No second wording of any edge. No depended-on rule restates a sentence. C-PRE-1 and C-PRE-2 are closed.
- Q1, Q2 and Q3 each carry a normative order framing ("the fee of a late pickup is posted before the fee of any later late pickup"; "a month's late payment fee is posted before the next month's tuition charge posts"; "a booked day's fee is posted before the next booking request is received"). None orders two problems of this charter, so it grounds no undeclared edge. Each asserts that older items were always posted: observation R2-O1, the successor of O7.

### override_declarations (r2)
- Q1 vs care_evt_late_pickup:
  - S3: declared, with scope and other-year content restated (C1 met).
  - S6 (no rate-basis discount, no CCS coverage): in force and respected (no hardship share now).
  - Other sentences: followed.
- Q2 vs care_billing_and_late_payment:
  - S2: declared for 2026-27, with other-year content restated.
  - **S1 "payments, remittances and credits are applied to the enrollment's oldest open charge first": not declared, and contradicted by Q2's measurement sentence.**
  - Q2 vs care_subsidy_funding S3 ("the household owes the rest of that month's charges, which is billed, made late … like any other balance"): Q2 does not cite this policy and ignores remittances.
  - See C-OVR-3.
  - For 2026-27, the replaced_by drops the base posting time (late_payment_fee_offset_days after the due day) without replacement, leaving "on the day it posts" unanchored (feeds C-REAL).
- Q3 vs care_evt_day_fees:
  - The drop-in fee sentence and the holiday-camp sentence: declared, with scope and other-year content restated.
  - **The early-release sentence ("otherwise a booked early-release afternoon is charged early_release_day_fee") stays in force, and Q3's standard sentence "The standard booked-day fee is drop_in_day_fee for the requested date, booked as a drop-in day" contradicts it for an early-release date.** See C-A6 (Q3 member).
  - Other sentences (active only, lead days, monthly cap, no rate-basis discount, closure credit): followed.
- Q4 vs care_billing_and_late_payment:
  - Suspension sentence: declared, with its exception scoped.
  - Q4 vs care_payments_and_returns: followed, certified funds inherited.
- Q5 vs care_withdrawal_and_refunds:
  - S2 and S3: declared. The baseline is now labelled "standard", and replaced_by says "billed in full only where that convention credits nothing". C-OVR-2 is closed.
  - S4 (district withdrawal ends care, no notice period): honoured by the daily convention.
  - Q5 vs care_subsidy_funding: the family-share credit base is consistent with S3.
- Q6 vs care_admission: unchanged, declared.

### factor_ladders (r2) — each factor judged against realism_bar.md
| policy | factor | label | tiers | multi-source | cross-difficulty | realism (bar) | XF tests | survives |
|---|---|---|---|---|---|---|---|---|
| Q1 | grade_band_minute_rate | parameter | 3 | no | enroll | R1 (grade band) | ok | yes |
| Q1 | semester_repeat_multiplier | parameter | 3 | yes (warning row ∧ chargeable count) | – | R1 (semester-keyed escalation) | ok | yes |
| Q1 | minute_billing_convention | method | 3 | no | – | R3 | A6 passes (ceil / minimum block / identity). Observation R2-O2: the minimum-block tier equals quarter-hour rounding on its whole reachable domain (6–15 minutes → 15) | yes |
| Q1 | after_hours_charge | parameter | 3 | no | – | R1 | ok (X2 considered: a per-minute fee plus a flat late surcharge is a published handbook shape) | yes |
| Q2 | unpaid_size_fee_method | method | 3 | no | – | R1/R5 (percentage with a floor, de minimis) | **A1/A3 fail**: tiers 1 and 2 take "the base late fee", which is the output of factor charge_size_base_fee; the term is defined only by that factor's sentence, not by the baseline | **no** |
| Q2 | charge_size_base_fee | parameter | 3 | no | – | R1 | ok | yes |
| Q2 | days_past_due_stage | parameter | 3 | no | – | **X1/X4**: keyed on how many days past due the fee *posts*, i.e. on the desk's posting delay. The unpaid part is fixed on the due day and the 2026-27 overwrite removed the posting time. A family that paid on day 12 still owes the +20 stage if the desk posts on day 21. R2 accepts days-past-due schedules keyed on the balance staying unpaid, not on when staff post. | struck | **no** |
| Q2 | repeat_late_month_addition | parameter | 3 | no | – | R1 (escalation by repeat late months) | ok | yes |
| Q3 | booked_day_selection | method | 3 | no | – | R1 (base day types) | **mislabel**: every tier substitutes a fee value (holiday_camp_day_fee / early_release_day_fee or 0 / drop_in_day_fee) into the same sum. Its baseline books a holiday-camp or early-release date as a drop-in at drop_in_day_fee, contradicting in-force base pricing (straw man, C3) | **no** |
| Q3 | grade_band_day_supplement | parameter | 3 | no | enroll | R1 | ok | yes |
| Q3 | booking_lead_adjustment | parameter | 3 | no | – | R2 (booked N days ahead) | ok | yes |
| Q3 | frequent_booking_adjustment | parameter | 3 | no | – | **X1** (volume or loyalty discount for days already booked) | struck | **no** |
| Q4 | balance_payment_scale | parameter | 4 | no | – | R5 | ok; A7 T1 checked on task 0 | yes |
| Q4 | semester_payment_limit | parameter | 3 | no | – | R5 | ok; lesser-of with the scale, A7 T1/T2 checked | yes |
| Q4 | plan_hardship_terms | parameter | 3 | no | meals | R1 (meal status; extends plan length, not a penalty cut) | ok | yes |
| Q4 | plan_returned_payment_rule | parameter | 3 | no | – | R5 | ok | yes |
| Q4 | plan_payment_rule | method | 3 | yes (tier 2: no late fee ∧ balance < 50) | – | R5 | A6 ok | yes |
| Q5 | withdrawal_proration_convention | method | 3 | yes (district status ∧ withdrawal date ≤ requested day) | enroll | R3 | A6 ok; **A9 fail** on tier 2 text (C-A9-2) | yes (bears weight; A9 recorded separately) |
| Q5 | plan_notice_length | parameter | 3 | no | – | R1 (plan / days per week) | ok | yes |
| Q5 | notice_counting_day | parameter | 3 | no | – | R2 (next-business-day convention) | ok; distinct values 2/1/0, honest label (r1 mislabel closed) | yes |
| Q5 | subsidy_credit_base | parameter | 3 | no | – | R1 (CCS family share; base subsidy_billing_basis) | ok. Observation R2-O4: the tiers pick different expressions, closer to a method | yes |
| Q6 | arrangement_size_scale | parameter | 3 | no | – | R5 | ok | yes |
| Q6 | arrangement_hardship_terms | parameter | 3 | no | meals | R1 | ok | yes |
| Q6 | arrangement_returned_payment_term | parameter | 3 | no | – | R5 | ok | yes |
| Q6 | arrangement_residence_term | parameter | 3 | no | enroll | R1 key (residence) on an R5 limit | ok (observation R2-O5: borderline, accepted under the bar) | yes |
| Q6 | arrangement_installment_rule | method | 3 | yes (tier 2) | – | R5 | A6 ok | yes |

Surviving counts:

| policy | surviving factors | parameters | methods | bound |
|---|---|---|---|---|
| Q1 | 4 | 3 | 1 | ok |
| Q2 | 2 | 2 | 0 | **fail** |
| Q3 | 2 | 2 | 0 | **fail** |
| Q4 | 5 | 4 | 1 | ok |
| Q5 | 4 | 3 | 1 | ok |
| Q6 | 5 | 4 | 1 | ok |

### findings (r2)
Status of round-1 REDs (re-checked here, not taken from the claims):
- C-OVR-1 **closed**: the re-pricing policy is retired, and no remaining policy re-prices a posted charge.
- C-OVR-2 **closed**: see override_declarations.
- C-PRE-1 **closed**.
- C-PRE-2 **closed**: F1–F3 scopes equal their resolvers' scopes.
- C-SCOPE-1 **closed**: the advance is removed, and Q4 is scoped to the current school year.
- C-A8 **closed**: no factor re-applies a component of a posted amount. Q2 and Q4 read posted amounts only as inputs to new charges or payments.
- C-A9-1 **closed**: the policy is retired.
- C-A1 **not closed**: the class has a new member, Q2.
- C-A2 **not closed**: Q4, Q5 and Q6 still name factor quantities.
- C-A6 **not closed**: the class has a new member, Q3.
- C-REAL **not closed**: the class has new members in Q2 and Q3.
- C-COUNT **not closed**: Q2 and Q3.

RED findings in revision_2 (each class swept over the whole charter in one pass):

**C-OVR-3 — SOURCE-POLICY RED (new; undeclared override; bears on task 0 structurally, not on its world).**
- Q2 says "The unpaid part of a month's tuition on its due day is the month's tuition charge, less the family's most recent payment on the enrollment when that payment posted on or after the charge's posting date and on or before the due day and has not been returned".
- Q2's own replaced_by keeps "When the amounts applied by the due day leave at least no_fee_below_amount … unpaid". In-force base care_billing_and_late_payment S1 applies "payments, remittances and credits … to the enrollment's oldest open charge first". care_subsidy_funding S3 makes a CCS household owe only the rest after the remittance.
- Producible worlds:
  - An older charge still open 50.00 and a payment of the full new month's tuition before the due day. Base: 50.00 of the new month is unpaid, so a fee is owed. Q2: unpaid 0.00, so no fee.
  - Two payments in the window. Q2 counts only the latest.
  - A CCS month whose remittance posts by the due day. Q2 ignores it, so the fee is priced on the full charge.
- On task 0's world no payment, remittance or credit falls in the November window, so both readings agree (see 0.md).

**C-A1 — SOURCE-FACTOR RED (all members):**
- Q2 unpaid_size_fee_method: tier 1 "never less than the base late fee" and tier 2 "the base late fee is taken" read the output of factor charge_size_base_fee. "Base late fee" is defined only in that factor's sentence (A3), and its document cannot name its result without naming the other factor (A10).
- Only this member. The other chains (Q4/Q6 "equal share" over the assembled count, Q5 convention over the billing end) act on quantities that the baseline sentences define ("the plan having one payment", "The billing end is the later of …"), so they comply.

**C-A2 — SOURCE-FACTOR RED (all members):**
- Q4: "the payment count is first limited by the semester limit, the extra payments of the hardship terms are then added and the payments the returned-payment rule takes away are then taken off … the first payment is then worked out by the payment rule".
- Q5: "the counting-day rule and the notice-length schedule fix the billing end, the proration convention turns the billing end into the share of the month credited, that share is taken of the credit base".
- Q6: "the installment count is the count the size scale sets, with the hardship installments added and the installments of the returned-payment and residence terms taken off … worked out by the installment rule".
- Not members: Q1 states the combination by kind ("multiplying quantities … flat charges"). Q2 ("the amount the fee method takes … the schedule's additions") and Q3 ("the day rate the selection rule sets … the schedule's supplements and adjustments") name only the policy's method part by role (observation R2-O6).

**C-A6 — SOURCE-FACTOR RED (all members):**
- Q3 booked_day_selection is labelled method, but every tier only substitutes a fee value into the same sum.
- Its baseline ("The standard booked-day fee is drop_in_day_fee for the requested date, booked as a drop-in day") contradicts the in-force base early-release sentence and books holiday-camp dates as drop-ins (straw man, C3).
- No other method factor fails: Q1, Q2, Q4, Q5 and Q6 method tiers differ by an operation or an input.

**C-A9-2 — SOURCE-FACTOR RED (new member of the A9 class; bears on task 1 structurally):**
- Q5 convention tier 2 text: "the family withdrew the enrollment by its written notice". Compute: `F('status') == 'withdrawn'`. Base care_nonpayment_withdrawal also leaves status withdrawn.
- Producible world: a family sends a notice, then the enrollment is withdrawn for nonpayment before the requested last day. Compute uses the weekly convention, while the text gives tier 3 (standard). The credits differ.
- On task 1's world the enrollment was withdrawn by notice, so the readings agree.

**C-REAL — SOURCE-FACTOR RED (all members, judged per realism_bar.md):**
- Q2 days_past_due_stage (X1/X4, reasoning in the table above).
- Q3 frequent_booking_adjustment (X1).
- All other factors are R1–R5 as tabled. The r1 members are all retired.

**C-COUNT — SOURCE-FACTOR RED:**
- Q2 has 2 surviving factors (charge_size_base_fee, repeat_late_month_addition) and no method.
- Q3 has 2 surviving factors (grade_band_day_supplement, booking_lead_adjustment) and no method.
- Both are in task 0's tree.

Observations (r2):
- R2-O1: order framings (successor of O7).
- R2-O2: Q1 minimum-block tier coincides with quarter-hour rounding on its domain.
- R2-O3: Q5 notice_on_file guard.
- R2-O4: Q5 subsidy_credit_base tiers are expressions.
- R2-O5: Q6 residence term is borderline.
- R2-O6: Q2/Q3 assembly sentences name the method part by role.
- r1 O1–O8: O1 closed (baselines labelled standard); O2 closed; O3 closed; O4 base-internal, still present but inert (nothing reads end_date now); O5 closed (Q2/Q4/Q6 count fees directly); O6 retired; O7 → R2-O1; O8 closed.

## closing_checklist (revision_2)
- Files: 0.md, 1.md and _difficulty.md each carry revision_2 appended below an untouched revision_1.
- Scope: task 0 = {Q1, Q2, Q3, Q4}, task 1 = {Q5, Q6}. Disjoint and complete.
- uuid8s are independent. Tools are closed.
- Trees: task 0 has 3 prerequisites (3 value_input edges), task 1 has 1 (1 value_input edge). Owner=user roots. The graph is acyclic.
- Derivations equal GT in both tasks.
- NOT met:
  - factor bounds for Q2 and Q3 (C-COUNT);
  - the classes C-A1 (Q2), C-A2 (Q4, Q5, Q6), C-A6 (Q3), C-A9-2 (Q5) and C-REAL (Q2, Q3);
  - policy self-consistency for Q2 (C-OVR-3).
- Gates were not re-run on a final form (the difficulty does not close).
- Final sweep, in one pass over the whole charter, of every class raised in r1 or r2:
  - Classes swept: C-OVR (undeclared override / C3), C-PRE (second wording, D1), C-SCOPE, A1, A2, A6, A8, A9, REAL, COUNT.
  - Members found are exactly those listed in findings (r2); no other member exists.
- **The difficulty does not pass the source-layer audit in revision_2.**

VERDICT revision_2: task0=RED task1=RED charter=C-OVR-3,C-A1,C-A2,C-A6,C-A9-2,C-REAL,C-COUNT

## revision_3

## charter_global_frozen (revision_3)
- Frozen 2026-10-24T22:20Z by the same independent auditor.
- Entry checks:
  - Worklog last non-empty line is `REWORK round 3: gates 7/7 green` (checked).
  - /tmp/erl0078_coord/snap_extended_day_care_billing_r3.txt (snapshot.sh run execute-only): 7/7 gates OK.
- Hashes:
  - care.extended.yaml eaec3557434d6820 (CHANGED, so every charter-global section below is re-derived).
  - task_tools.py 38804948550844e6 (unchanged from r2, so the r2 action_binding_and_uuids section is carried by reference).
  - Views: r3/0.view.json 4d03d19a61465c81 (rebuilt); r3/1.view.json a899300bfd4e10e1, identical to r2.
  - Base prefix is still byte-identical.
- Read: realism_bar.md including AMENDMENT 1 (R6) in full; "REWORK round 3 claims" by item id only. No factor carries an R6 tag; the worklog states that no R6 factor is used.
- Scratch: charter_r3.txt, basis_sweep_r3.txt, recompute_r3.py.

### policy_conflict_scan (r3)
- Same six policies, tools and subjects as r2:
  - Q1 late pickup fee
  - Q2 late payment fee
  - Q3 booked day fee
  - Q4 payment plan (user)
  - Q5 notice credit
  - Q6 prior-year installment (user)
- Same components A = {Q1–Q4}, B = {Q5, Q6}.
- No subject overlap. Trigger rule met.
- Cross-category reads: enroll (Q1, Q3, Q5, Q6) and meals (Q4, Q6). These are other difficulties' categories, and none is written.

### rule_compute_equivalence (r3)
- Verbatim sweep: 0 misses for compute_basis, baseline, replaced_by and policy_source. No tool or policy id appears in any rule.
- Q2:
  - Base late fee by plan, fee form, repeat addition, sibling share, and the single rounding map.
  - "for a month that owes one under the late-fee sentence below" is not implemented in compute (the result is positive whatever the month owes). The owe test is carried by Q4's F2 sentence and by the base sentence (observation R3-O1).
- Q3: day rate (standard), rate-basis rule, grade and plan supplements, and lead adjustment map. The lead boundary "at least advance_lead_days days" maps to `>=`.
- Q5: convention tier 2 now states its record test ("status withdrawn with no suspension date recorded and a withdrawal notice on file"), and compute tests exactly that (`suspended_date == ''`, `conv_notice >= 1`). notice_length's guard is stated in the rule ("of the withdrawal notice on file").
- Q1, Q4, Q6: map as in r2, except the Q1 minimum block, which is now 10 minutes.

### action_binding_and_uuids (r3)
Tools are unchanged (same hash). The r2 section stands: unique (target_tool, computes) pairs, independent uuid8s, no prerequisite checks in tool bodies, owner=user payments per ruling (b).

### prerequisite_graph and prerequisite_sentences (r3)
- Same graph: F1–F3 (Q4 ← Q1, Q2, Q3; state form) and F4 (Q6 ← Q5; action form). Acyclic.
- F2 now reads "…carries its late payment fee entry whenever any part of that month's tuition was left unpaid on its due day". This is the base owe-test (oldest-first allocation, returned payments never paid), and Q2's resolver prices exactly that month. The zero case is carved out by the same test.
- Each edge has one wording. No sentence is restated in a depended-on rule.
- R2-O1's order framings remain normative posting rules and order no two problems (observation).

### override_declarations (r3)
- Q2 vs care_billing_and_late_payment:
  - S2: declared. The replaced_by now keeps the base posting time and the base owe-test, and prices only the amount for 2026-27; other years are restated.
  - S1 is honoured ("Whether a month owes a late payment fee is decided as the base billing rules decide it: payments, remittances and credits are applied to the enrollment's oldest open charge first"). **C-OVR-3 closed.**
- Q3 vs care_evt_day_fees: four sentences declared (drop-in fee, holiday-camp fee, early-release fee, the no-rate-basis/no-sibling-discount sentence), each with scope restated. The standard sentence is now the base day-type pricing, so the r2 C3 contradiction is closed.
- Q1, Q4, Q5, Q6: as in r2. Q5's baseline is labelled standard.

### factor_ladders (r3) — judged against realism_bar.md R1–R6 / X1–X4
| policy | factor | label | realism | XF | survives |
|---|---|---|---|---|---|
| Q1 | grade_band_minute_rate | parameter | R1 | ok | yes |
| Q1 | semester_repeat_multiplier | parameter | R1 | ok | yes |
| Q1 | minute_billing_convention | method | R3 | A6 ok; the 10-minute minimum block differs from quarter-hour rounding, so R2-O2 is closed | yes |
| Q1 | after_hours_charge | parameter | R1 | ok | yes |
| Q2 | plan_base_late_fee | parameter | R1 (plan days per week) | A1/A3 ok: "base late fee" is defined by the baseline sentence | yes |
| Q2 | late_fee_form | method | R1/R3 (charge size / half-month proration) | A6 ok (greater-of / percentage / flat) | yes |
| Q2 | repeat_late_month_addition | parameter | R1 | ok | yes |
| Q2 | sibling_late_fee_share | parameter | **X1**: a percentage cut on a penalty fee (50 % / 25 % of the late payment fee by sibling position) | **X3/X2**: the fee form takes 10 % of the month's tuition charge, which already carries the sibling discount; the share then cuts the fee again on the same sibling dimension. Untagged; would also fail R6 conditions 4 and 5. | **no** |
| Q3 | rate_basis_day_rate | method | R1 (sliding-fee by meal status, read from the recorded rate basis) | A6 ok (flat / greater-of share / identity); base no-rate-basis sentence retired by declared overwrite | yes |
| Q3 | grade_band_day_supplement | parameter | R1 | ok | yes |
| Q3 | plan_day_supplement | parameter | R1 (plan) | ok; X2 not engaged (different key from grade) | yes |
| Q3 | booking_lead_adjustment | parameter | R2 | ok | yes |
| Q4 | the five factors of r2 | | R5 / R1 | assembly now by kind, so A2 is closed | yes (5) |
| Q5 | four factors | | R3 / R1 / R2 / R1 | assembly by kind (A2 closed); convention tier text equals compute (A9 closed) | yes (4) |
| Q6 | five factors | | R5 / R1 / R5 / R1-on-R5 / R5 | assembly by kind (A2 closed) | yes (5) |

Surviving counts:

| policy | surviving factors | parameters | methods | bound |
|---|---|---|---|---|
| Q1 | 4 | 3 | 1 | ok |
| Q2 | 3 | 2 | 1 | **fail (< 4)** |
| Q3 | 4 | 3 | 1 | ok |
| Q4 | 5 | 4 | 1 | ok |
| Q5 | 4 | 3 | 1 | ok |
| Q6 | 5 | 4 | 1 | ok |

R6-WAIVED: none (no R6 factor is declared, and none is needed for the ones that survive).

### findings (r3)
Round-2 RED status, re-checked on the charter:
- C-OVR-3: **closed**.
- C-A1: **closed**. The base late fee is baseline-defined, and no factor tier reads another factor's decides-binding.
- C-A2: **closed**. All six combination sentences name parts only by kind.
- C-A6: **closed**. Q3 day-type pricing is now the standard; rate_basis_day_rate is a real method.
- C-A9-2: **closed**.
- C-REAL: r2 members (stage, frequent booking) **removed**. **New member**: Q2 sibling_late_fee_share.
- C-COUNT: Q3 **closed**; Q2 **not closed** (3 surviving after the new C-REAL strike).

RED (revision_3), each class swept over the whole charter in one pass:

**C-REAL — SOURCE-FACTOR RED.** All members:
- Q2 sibling_late_fee_share (X1 percentage cut on a penalty fee; X3/X2 sibling dimension already in the charge its 10 % form reads). No other factor of any policy is X1–X4.

**C-COUNT — SOURCE-FACTOR RED.**
- Q2 has 3 surviving factors (plan_base_late_fee, late_fee_form, repeat_late_month_addition), against the floor of 4.
- No other policy is below bound.

Observations (r3):
- R3-O1: Q2 owe-test is not in compute.
- R3-O2: on task 0 the November late payment fee was due to post on 11-11 under the base timing Q2 keeps. It is unposted at 11-12 and books with today's date. This is a one-day desk lag; the amount does not depend on the posting date.
- R2-O1: framings kept.
- R2-O4 and R2-O5: kept, accepted.
- O4: inert.

## closing_checklist (revision_3)
- Files: revision_3 is appended in all three files; earlier revisions are untouched.
- Scope: task 0 = {Q1–Q4}, task 1 = {Q5, Q6}. Disjoint and complete.
- Tools are unchanged and closed, with independent uuid8s.
- Trees: 3 and 1 prerequisites, all value_input, owner=user roots, acyclic.
- Derivations equal GT for both tasks.
- Task 1 passes all four relationships.
- Task 0 fails only on the factor relationship: Q2 has 3 surviving factors after the X1 strike.
- Final sweep, in one pass over the whole charter, of every class raised in r1–r3:
  - Classes: C-OVR / C3, C-PRE (second wording, D1), C-SCOPE, A1, A2, A3, A6, A7, A8, A9, B1–B8, X1–X4 / R6, COUNT.
  - The only members are Q2 sibling_late_fee_share (X1, plus X3/X2) and the resulting Q2 count.
  - No regression: every r1/r2 closure re-verified on eaec3557434d6820.
- Gates were not re-run on a final form (the difficulty does not close).

VERDICT revision_3: task0=RED task1=PASS charter=C-REAL,C-COUNT

## revision_4

## charter_global_frozen (revision_4)
- Frozen 2026-10-24T23:05Z.
- Entry checks:
  - Worklog last line is `REWORK round 4: gates 7/7 green` (checked).
  - /tmp/erl0078_coord/snap_extended_day_care_billing_r4.txt: 7/7 OK.
- Hashes:
  - care.extended.yaml b144db2173e2ef9e (changed).
  - task_tools.py 38804948550844e6 (unchanged).
  - Views: r4/0.view.json c5be7f693c8d01bf (rebuilt); r4/1.view.json a899300bfd4e10e1 (unchanged since r2).
  - Base prefix is byte-identical.
- Read: realism_bar.md incl. AMENDMENT 1; the "REWORK round 4 claims" ids, plus the R6 tag line, which the amendment requires the claims to carry.
- Change scope: a structural diff of all six extended policies against r3 (/tmp/audit_extended_day_care_billing_0078/charter_r3.txt vs charter_r4.txt) shows that only care_ext_late_payment_fee_schedule (Q2) changed:
  - sibling_late_fee_share and its rule sentence and bindings were removed;
  - returned_payment_late_addition was added, with params returned_months, one_return_addition and two_return_addition;
  - the combination sentence now reads "…come first, the parts that add a fixed amount are then added to it, and the fee is rounded once at the end…".
- Sections not touched by the change are carried by reference to revision_3 on the ground that the other five policies are byte-identical in that diff: policy_conflict_scan, action_binding_and_uuids, prerequisite_graph/sentences, and the Q1/Q3–Q6 override and factor rows.
- Q2 is re-derived in full below.

### Q2 re-derivation (rule_compute_equivalence, override_declarations, factor_ladders)
- Verbatim sweep: 0 misses for Q2's compute_basis.
- Each ladder's tier text equals its compute:
  - "two or more family payments on the enrollment were returned by the bank in the returned_months months before the day the fee posts" maps to `COUNT(…, within_months=12, event_type='care_returned_payment')` at NOW;
  - the other three ladders are as in r3.
- Combination: by kind (fixed-amount parts → additions → single rounding). A2 is met. With no multiplying share left, the parts commute except for the form's greater-of, which comes first as stated.
- Overrides: unchanged from r3 (S2 declared, S1 owe-test honoured). The base sentence "posts one returned_payment_fee for that payment" stays in force. The new addition is part of the late payment fee, not a second returned-payment fee, so it is no override.
- Factors:

| factor | label | realism | XF | survives |
|---|---|---|---|---|
| plan_base_late_fee | parameter | R1 | ok | yes |
| late_fee_form | method | R1/R3 | ok | yes |
| repeat_late_month_addition | parameter | R1 | ok | yes |
| returned_payment_late_addition | parameter | **R6**, graded below | ok | **R6-WAIVED** |

- R6 conditions for returned_payment_late_addition:
  1. Keyed on a recorded status (care_returned_payment rows in the 12 months before posting). Holds.
  2. 5.00 / 10.00 are round district figures. Holds.
  3. No in-force base clause is contradicted. The base returned-payment fee and certified-funds rule stand, and Texas Bus. & Com. Code §3.506's $30 cap concerns the dishonored-check processing fee, which this is not. Holds.
  4. Not a named X1 mechanism. Holds.
  5. A1–A10 and B1–B8 pass. No other factor of this computation uses returned payments, so X2 does not apply, and nothing is already in a recorded amount, so X3 does not apply. Holds.
  6. Minimal: 3 honest factors against a draw of 4 leaves exactly 1 slot, and the tag, key and reason are listed in the claims. Holds.
  - Result: **R6-WAIVED (BLUEPRINT-KNOWN)**, an observation, not a RED.
  - Note R4-O1: on a world with a returned payment, the return is penalised by the base 30.00 fee, by the late fee its month incurs (counted again by repeat_late_month_addition in later months), and by this addition. These are different factors on different records; the observation is recorded for the KB renderer's realism read.
- Counts: Q2 has 4 factors (3 R1–R5 + 1 R6-waived): 3 parameters and 1 method. Within bound.

### findings (r4)
- C-REAL: **closed**. sibling_late_fee_share is removed and not reworded; no Q2 factor reads sibling position.
- C-COUNT: **closed**. Q2 is at 4 with one R6-waived factor.
- Final sweep, in one pass over the whole charter, of every class raised in r1–r4 (C-OVR / C3, C-PRE, C-SCOPE, A1, A2, A3, A6, A7, A8, A9, B1–B8, X1–X4 / R6, COUNT): no member found.
- No regression: the five other policies are unchanged from r3, and Q2's r3 closures (C-OVR-3, C-A1, C-A2) still hold on b144db2173e2ef9e.

Observations (r4):
- R6-WAIVED: Q2 returned_payment_late_addition.
- R4-O1.
- Carried: R3-O1, R3-O2, R2-O1, R2-O4, R2-O5, O4.

## closing_checklist (revision_4)
- Per-task audit files 0.md and 1.md and this file carry revisions 1–4; old revisions are untouched.
- Every comparison section of the final revision carries PASS. Task 1 carries forward r3 by reference (unchanged view and policies).
- All 6 extended policies are covered. Scopes are disjoint and span whole trees: task 0 = {Q1 late pickup fee, Q2 late payment fee, Q3 booked-day fee, Q4 current-year payment plan}, task 1 = {Q5 notice credit, Q6 prior-year installment}.
- Task tools and GT are closed. Each tool has an independently generated, frozen uuid8.
- Trees:
  - task 0 has 3 prerequisite problems with 3 value_input edges; task 1 has 1 with 1.
  - Each root is an owner=user payment (owner_ruling (b)).
  - The difficulty-wide graph is acyclic.
- Factors:
  - Every computation has a self-sufficient, honest baseline giving a definite non-gold number.
  - Counts per computation: 4 / 4 / 4 / 5 / 4 / 5, each with ≥ 2 parameters and 1 method.
  - Each task has ≥ 1 multi-source and ≥ 1 cross-difficulty factor (task 0: enroll and meals; task 1: enroll and meals).
  - Every ladder has ≥ 3 distinct tiers stated in full in its rule, and is R1–R5, or R6-WAIVED for the single Q2 slot.
  - Every factor bears weight on its task's world.
- Gates on this final form: /tmp/erl0078_coord/snap_extended_day_care_billing_r4.txt, a 7/7 OK snapshot taken on care.extended.yaml b144db2173e2ef9e and task_tools.py 38804948550844e6, the hashes audited here. check_traceability is deferred to the KB stage per the brief.
- **The difficulty passes the source-layer audit in revision_4.**

VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN

## revision_5

## charter_global_frozen (revision_5)
- Frozen 2026-10-25 by the same independent auditor. This round's items are the renderer scan-first findings in audits/render_source/extended_day_care_billing/render_r1.md (F1, F2, O1, O2), read in full.
- Entry checks:
  - Worklog last line is `REWORK round 5: gates 7/7 green` (checked).
  - /tmp/erl0078_coord/snap_extended_day_care_billing_r5.txt (snapshot.sh run execute-only): 7/7 OK.
- Hashes:
  - care.extended.yaml 68b91fbd698717dc (changed).
  - task_tools.py 38804948550844e6 (unchanged).
  - Views: r5/0.view.json c5be7f693c8d01bf and r5/1.view.json a899300bfd4e10e1, both identical to r4.
  - Base prefix is byte-identical.
- Read: realism_bar.md AMENDMENTS 1 and 2; "REWORK round 5 claims"; owner_ruling.md; XF_recipe.md.
- An earlier turn on this round was cut by an account limit before anything was written to these files (no revision_5 text existed at resumption). This section is written fresh.
- Change scope: a sentence-level structural diff r4 → r5 (/tmp/audit_extended_day_care_billing_0078/charter_r4.txt vs charter_r5.txt, sdiff.py) shows only the following changes:
  - Q1: the rate sentence and its ladder tier 3 add "and for a student with no such record".
  - Q3:
    - the scope sentence selects "the most recent drop-in booking request that is received or completed (latest by the time it was received; a declined or cancelled request is never priced)";
    - the grade-supplement sentence and its ladder tier 3 add "or for a student with no such record";
    - four bindings (requested_date, plan_request_date, request_received, lead_request_date) are status-filtered.
  - Q4: the F3 prerequisite sentence and its condition add "that is received or completed".
  - Q5:
    - the notice-request selection is status-filtered in both rule and compute (requested_last_day, notice_received, notice_on_file, conv_notice);
    - the credit-base sentence and its tier 2 add "the whole charge being the base when no board remittance has posted on the enrollment at all".
  - No factor, param, combination sentence, overwrite or other binding changed. Q2 and Q6 are byte-identical.
- Verbatim sweep: 0 misses for compute_basis, baseline and policy_source in all six policies.

### render findings (F/O) — verified
- **F1 closed.**
  - Q1 rule: "…late_pickup_fee_per_minute for grades 01 through 05 and for a student with no such record". Ladder tier 3: "it shows grade 01 through 05, or the student holds no such record".
  - Q3 rule: "…nothing for grades 01 through 05 or for a student with no such record". Ladder tier 3: the same.
  - Compute is unchanged; its fall-through (district_grade None) now has a stated tier.
  - No new fourth tier was created and the outcomes stay distinct, so no regression on A6 or count.
- **F2 closed.**
  - Q5 credit-base sentence and tier 2 now state "…or the whole charge when no board remittance has posted on the enrollment at all". This equals compute's `recent_remittance if recent_remittance != None else 0`.
  - The tier-2 value and the tier-3 value (whole charge) coincide only on that sub-case. Tier 2 otherwise differs, so A6 does not apply (parameter).
- **O1 accepted** as a stated scope test ("…of an enrollment of the 2026-27 school year, and only of such an enrollment"). The other-year sentences restate in-force base fees and are not priced here (C4, small scoped surface). This agrees with the renderer's own reading.
- **O2 closed.**
  - The booked-day selection, the notice selection, notice_on_file / conv_notice, and Q4's F3 sentence and condition now admit only received or completed requests. Each rule says so ("…received or completed (latest by the time it was received; a declined or cancelled request is never priced/used)"), and compute filters request_status the same way.
  - F3 still names exactly the object Q3 prices, so D1 is satisfiable.
  - Observation R5-O1: compute resolves an exact created_at tie between a completed and a received request in favour of the received one (`>` comparison). No rule sentence states that tie-break. created_at is a timestamp to the second, so a tie is not a producible business world. The same implicit tie behaviour applies to every LATEST read accepted since r1. Not demonstrable, so an observation.
  - Observation R5-O2: Q5 tier text "a withdrawal notice on file" is read by compute as a received or completed notice. When none such exists, requested_last_day is None and the result is 0 whatever the convention, so no world separates the readings.

### regression sweep (r5)
Every class raised in r1–r5, swept once more over the whole charter in one pass:
- C-OVR / C3: Q1 and Q3 overwrites unchanged; the added clauses contradict no in-force base sentence.
- C-PRE / D1 / D2: F3 wording single and scoped to Q3's object.
- C-SCOPE.
- A1: the new bindings are plain reads inside their own factors or plain bindings; no factor reads another's output.
- A2: combination sentences unchanged, by kind.
- A3, A6, A7, A8.
- A9: ladder text now equals compute at the absent-record and no-remittance edges.
- B1–B8: the F1/F2 edges are now stated; B2 status filter added; R5-O1 noted.
- X1–X4 / R6: factors unchanged; Q2's R6-WAIVED stands.
- COUNT: unchanged (4 / 4 / 4 / 5 / 4 / 5).

No member was found, and every revision_4 closure still holds.

### findings (r5)
- No RED.
- Observations:
  - R5-O1, R5-O2.
  - O1 (renderer) accepted.
  - Carried: R6-WAIVED Q2 returned_payment_late_addition, R4-O1, R3-O1, R3-O2, R2-O1, R2-O4, R2-O5, O4.

## closing_checklist (revision_5)
- Files: all three carry revisions 1–5, with old text untouched.
- Every comparison in revision_5 is PASS.
- Coverage and scope: unchanged from r4 (6 policies; task 0 = {Q1–Q4}, task 1 = {Q5, Q6}; disjoint, whole trees).
- Tools and uuid8s are unchanged and closed.
- Trees: 3 prerequisites and 1, all value_input, owner=user roots, acyclic.
- Factors:
  - Counts 4 / 4 / 4 / 5 / 4 / 5, each with ≥ 2 parameters and 1 method, and honest definite baselines that differ from gold.
  - Multi-source and cross-difficulty factors in each task.
  - Every factor bears weight.
  - Q2's single R6 slot is waived.
- Gates on the final form: /tmp/erl0078_coord/snap_extended_day_care_billing_r5.txt, 7/7 OK on care.extended.yaml 68b91fbd698717dc and task_tools.py 38804948550844e6. check_traceability is deferred per the brief.
- **The difficulty passes the source-layer audit in revision_5.**

VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

## revision_6

## charter_global_frozen (revision_6)
- Frozen 2026-10-25 by the same independent auditor.
- This round's item is SRC-1 of audits/policy_kb/extended_day_care_billing/_difficulty.md (the KB auditor's source item, the same boundary question the renderer raised after r5), plus O-4 from that file.
- Entry checks:
  - Worklog last line is `REWORK round 6: gates 7/7 green` (checked).
  - /tmp/erl0078_coord/snap_extended_day_care_billing_r6.txt (snapshot.sh run execute-only): 7/7 OK.
- Hashes:
  - care.extended.yaml 8e283b9ed3a5e94d (changed).
  - task_tools.py 38804948550844e6 (unchanged).
  - Views r6/0.view.json c5be7f693c8d01bf and r6/1.view.json a899300bfd4e10e1 (unchanged since r4).
  - Base prefix is byte-identical.
- Read: "REWORK round 6 claims"; realism_bar.md AMENDMENTS 1–2; owner_ruling.md; XF_recipe.md.
- Change scope: a sentence-level diff r5 → r6 (charter_r5.txt vs charter_r6.txt; the remaining diff lines are extract-format only) shows exactly three rule sentences changed:
  - Q2 returned_payment_late_addition;
  - Q4 plan_returned_payment_rule;
  - Q6 arrangement_returned_payment_term.
- Each also changed its compute_basis quotes and ladder tier text. No compute, param, factor, overwrite, prerequisite sentence or combination sentence changed.
- Verbatim sweep: 0 misses in all six policies. No stale "counted back to the same day of the month" wording remains in any extended rule.

### SRC-1 — verified closed
- New wording (Q2; Q4 and Q6 identical with "the day of the payment"): "…returned by the bank, the return posting after the same day of the month returned_months months before the day the fee posts (the last day of that month when it has no such day) and on or before the day the fee posts".
- The compute is unchanged: `COUNT(…, within_months=12, date_field='posted_date', event_type='care_returned_payment')`.
- DSL semantics, read in skills/erl-task-instantiate/scripts/check_compute.py `_within` / `MONTHS`: a row is in the window iff 0 ≤ MONTHS(posted, NOW) < 12, where MONTHS subtracts one when NOW's day-of-month is earlier than the posted day's.
- Edge checks against the new text:

| case | compute | text | agree |
|---|---|---|---|
| posted on NOW | m = 0, in | "on or before" | yes |
| posted after NOW | m < 0, out | — | yes |
| posted on the same day 12 months earlier | m = 12, out | "after" | yes |
| posted on the next day after that | m = 11, in | — | yes |
| NOW 2028-02-29, posted 2027-02-28 | m = 12, out | "the last day of that month when it has no such day", not after | yes |
| NOW 2028-02-29, posted 2027-03-01 | m = 11, in | — | yes |
| NOW day 30, posted day 31 of the month 12 months earlier | m = 11, in | after the 30th | yes |

- Both ends are now stated, and compute matches on every edge. **SRC-1 closed.**
- Not engaged in either task world:
  - task 0: return 2026-10-09 vs NOW 2026-11-12;
  - task 1: return 2025-11-10 vs NOW 2026-08-04.
- The base measure care_msr_returned_payments_lookback keeps its BLUEPRINT-KNOWN base wording. No extended compute reads it.

### O-4 (KB auditor, source, unreached) — judged
- Booking gates are not re-tested in Q3 compute. Base care_evt_day_fees eligibility (active status, holiday_camp_access, drop-in allowance) stays in force and is not retired. This is a gate the agent applies before posting, not a priced quantity. Observation.
- Q2 `earlier_fees` counts every late-fee row. It equals "earlier billing months" whenever the priced month's fee is not yet posted, which is the only state in which Q2 prices (the fee is priced before it posts). Observation, as O5/R3 earlier.

### regression sweep (r6)
Every class raised in r1–r6, swept once over the whole charter:
- C-OVR / C3.
- C-PRE / D1 / D2.
- C-SCOPE.
- A1, A2 (combination sentences unchanged), A3, A6, A7, A8.
- A9 (ladder text = compute on the window edges).
- B1–B3 (the window ends are now stated; same convention in all three look-backs).
- B4–B8.
- X1–X4 / R6 (Q2's R6 factor: key and figures unchanged, wording exact; still R6-WAIVED).
- COUNT (4 / 4 / 4 / 5 / 4 / 5).

No member was found, and every r1–r5 closure holds.

### findings (r6)
- No RED.
- Observations:
  - O-4 above.
  - Carried: R5-O1, R5-O2, R6-WAIVED Q2 returned_payment_late_addition, R4-O1, R3-O1, R3-O2, R2-O1, R2-O4, R2-O5, O4.

## closing_checklist (revision_6)
- Files: all three carry revisions 1–6, with old text untouched. Every revision_6 comparison is PASS.
- Coverage and scope: unchanged (task 0 = {Q1–Q4}, task 1 = {Q5, Q6}; disjoint, whole trees, all 6 policies).
- Tools and uuid8s are unchanged and closed.
- Trees: 3 prerequisites and 1, all value_input, owner=user roots, acyclic.
- Factors:
  - Counts 4 / 4 / 4 / 5 / 4 / 5, each with ≥ 2 parameters and 1 method, and honest definite non-gold baselines.
  - Multi-source and cross-difficulty factors in each task.
  - Every factor bears weight.
  - Q2's single R6 slot is waived.
- Gates on the final form: /tmp/erl0078_coord/snap_extended_day_care_billing_r6.txt, 7/7 OK on care.extended.yaml 8e283b9ed3a5e94d and task_tools.py 38804948550844e6. check_traceability is deferred per the brief.
- **The difficulty passes the source-layer audit in revision_6.**

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN

## revision_7

## charter_global_frozen (revision_7)
- Frozen 2026-10-25. This is a seed-only round for the KB auditor's SRC-2 (audits/policy_kb/extended_day_care_billing/_difficulty.md, KB-VERDICT revision_2).
- Entry checks:
  - Worklog last line is `REWORK round 7: gates 7/7 green` (checked).
  - /tmp/erl0078_coord/snap_extended_day_care_billing_r7.txt (snapshot.sh run execute-only): 7/7 OK.
- Byte identity: care.extended.yaml 8e283b9ed3a5e94d and task_tools.py 38804948550844e6 equal the required prefixes. Every charter-global section of revision_6 is therefore carried by reference, with these two hashes as grounds.
- Views: r7/0.view.json c5be7f693c8d01bf (unchanged since r4); r7/1.view.json 32680b09abcd9ae0 (rebuilt).
- Read: "REWORK round 7 claims"; the SRC-2 entry; the published docs/enroll documents transfer_request_calendar_and_placement_terms, transfer_and_choice_requests_and_placement_acceptance, enrollment_type_admission_schedule, registration_document_deadlines, registration_residency_and_required_documents and effects_of_enrollment_type_on_district_programs.
- Task 1 view diff, r6 → r7:
  - transfer_requests 3599d17c: created_at 2026-05-04 → 2026-01-20; decision_date 2026-06-18 → 2026-04-14.
  - enrollments d621266b: registration_date 2026-06-22 → 2026-04-20.
  - user_scenario: "moved just outside the district this summer" → "moved just outside the district in January … applied for a transfer that winter".
  - Nothing else changed, including frozen_time.

### SRC-2 — verified closed (re-seed against the published enroll corpus)

| published rule (docs/enroll) | seeded value | holds |
|---|---|---|
| Non-Resident Transfer window opens 01-11 and closes 02-26, both days included | request filed 2026-01-20 | yes |
| decisions on window requests issued by 04-16 | decision_date 2026-04-14, status approved | yes |
| acceptance within 10 calendar days, decision date day 0, so the last day is 04-24 | 2026-27 registration 2026-04-20 carries approved_transfer_request_id 3599d17c | yes |
| admits KG–12 when the household profile shows no in-district residence and an approved non-resident request is on file; campus = the requested campus | grade 01; in_district_residence false; campus Cypress Hollow Elementary | yes |
| campuses closed to new Non-Resident placements: Live Oak Elementary and Calloway Creek High School | Cypress Hollow is not listed | yes |
| no residency proof required, so residency_verified_date is left empty | empty | yes |
| a placement lasts a single school year and must be requested again each year | request_school_year 2026-27 | yes |

- The published enroll corpus has no rule ending an Attendance Zone enrollment on a mid-year move out of the district. The 2025-26 record 62acb243 (year_completed, withdrawal_date 2026-05-28) after the January move is therefore not contradicted.
- The persona's January move and winter application now agree with the records. **SRC-2 closed.**
- The claimed exhaustive cross-product pass was spot-checked independently on both worlds. All rows are consistent with their owning product's published rules:
  - meals: task 0's two Reduced-Price accounts, effective 2026-07-15 = the determination date; task 1's Free Meal Status (Prior-Year Carryover), effective 2026-07-01, read before 2026-09-23;
  - enroll: task 0's KG Attendance Zone record; task 1's 2025-26 and 2026-27 records.
  - No transport, activity, device or music rows are seeded.

### regression sweep (r7)
- The charter and tools are byte-identical, so no class raised in r1–r6 can have moved at charter level. Every r6 closure stands.
- Per-task only task 1's seed moved, and the arrangement_residence_term tier is unchanged (Non-Resident Transfer, enrolled → −1).

### findings (r7)
- No RED.
- Observations carried from r6.

## closing_checklist (revision_7)
- Files: all three carry revisions 1–7, with old text untouched. Every revision_7 comparison is PASS.
- The charter and tools are byte-identical to r6 (8e283b9ed3a5e94d / 38804948550844e6), so coverage, scope, trees, factors and uuid8s are as closed in revision_6.
- Seeds:
  - Task 1's transfer history is now producible under docs/enroll.
  - Cross-product rows of both worlds are consistent with their owning products' published docs.
  - No scored figure moved.
- Gates on the final form: /tmp/erl0078_coord/snap_extended_day_care_billing_r7.txt, 7/7 OK. check_traceability is deferred per the brief.
- **The difficulty passes the source-layer audit in revision_7.**

VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN
