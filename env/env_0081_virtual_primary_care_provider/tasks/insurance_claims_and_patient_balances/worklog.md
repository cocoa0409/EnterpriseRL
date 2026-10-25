# worklog — insurance_claims_and_patient_balances (env_0081)

## Step 0 — difficulty pre-check (shared by both tasks)
- Read: references/{product_extended.yaml,task_tools.py,task.json}; blueprint.yaml; products/claim.yaml (full);
  visit.yaml (payment path, fee pricing, after-hours, cost share, billing corrections, GFE, booking eligibility,
  attendance, provider cancellation, measures); membership.yaml variants + credits/sponsor/billing corrections;
  lab payment path; db_schema (claim, visit, membership tables); audits/render_source/{XF_recipe,realism_bar,
  owner_ruling,identifier_bands}.md (in full).
- Claimed events: claim_coverage_added, claim_coverage_details_changed, claim_coverage_terminated,
  claim_coverage_order_changed, claim_corrected_submitted, claim_self_pay_rebill_posted,
  claim_time_of_service_applied, claim_patient_payment_posted, claim_prompt_pay_discount_applied,
  claim_small_balance_written_off, claim_credit_transferred, claim_credit_received, claim_credit_refunded.
- Base automatic clauses: claim_adjudicated triggers claim:claim_benefits_refreshed (inside claim); every other
  claim event has triggers []. No claimed event writes another category.
- draw_counts --tasks 2: task0 prerequisite_problems=2 factor_counts=[5,5,4]; task1 prerequisite_problems=1
  factor_counts=[5,6].
- owner=user: only owner_ruling (c) lies inside the claimed events (claim_patient_payment_posted, card read out
  because the stored card is expired / an HSA card is not on file). Hence both roots are patient payments.

## THIN-CHARTER NOTE (decision recorded, unattended run)
The claim charter's numeric writes are ledger entries. Genuine multi-tier (>=3 distinct outcomes) rules that
bear on them: the price-path rebill fee by membership tier in force on the service date (visit+membership
charters), denial-code settlement, payer-keyed filing windows, the corrected-claim/COB balance scope. The drawn
floor (25 factors over 5 computations) exceeds them. Closest established rule (env_0074/env_0078 thin-charter
handling): keep every amount equal to what the charters themselves produce (no invented perks, no courtesy cuts,
no invented prices), build factors from charter rules first; where a slot has no charter rule, use a rule keyed on
a recorded field that restates how the charter settles that component (tagged THIN below) rather than inventing a
business effect. Every THIN factor is listed per policy for the coordinator.

## Design decision (final, after exhausting charter-real ladders)
Roots must be patient payments (owner ruling (c)). A payment equals the claim balance, so its factors can only be
ledger-composition rules (which entry families the balance carries) — kept numerically exact (THIN: restates the
charter's balance measure). Prerequisites:
- task 0 (draw 2 prereqs, [5,5,4]): root claim_ext_cost_share_balance_payment (user, 5) <- claim_ext_open_balance_credit_transfer
  (agent, 5) <- claim_ext_small_balance_writeoff (agent, 4). Credit on an older adjudicated claim must first pay the patient's
  other open balances oldest service date first; a balance that falls due for a small-balance write-off is cleared first.
- task 1 (draw 1 prereq, [5,6]): root claim_ext_rebill_balance_payment (user, 6; pays a self-pay rebill balance in full inside
  the prompt-pay window, the discount posted with the payment) <- claim_ext_booking_collection_application (agent, 5; the
  booking collection of the rebilled visit was never applied; reads the visit's billing lines = cross-difficulty visit).
Tool names (uuid4 hex[:8], one per tool): post_small_balance_writeoff_bfef4ea9, transfer_claim_credit_12a8a2c0,
post_cost_share_payment_1adf649d, apply_booking_collection_b81aee5f, post_rebill_balance_payment_9bd5f69d.
- REVISION (before any task file): roots swapped to fit the worlds — task 0 root = claim_ext_rebill_balance_payment
  (post_rebill_balance_payment_9bd5f69d, owner=user, pays a self-pay rebill balance in full; prompt-pay discount posted with
  it) <- claim_ext_open_balance_credit_transfer <- claim_ext_small_balance_writeoff; task 1 root =
  claim_ext_cost_share_balance_payment (post_cost_share_payment_1adf649d, owner=user) <- claim_ext_booking_collection_application
  (apply_booking_collection_b81aee5f). task_tools.py written with all 5 tools: TASK TOOL CONTRACT OK.

## Task 0 — verification run (scratch /tmp/insurance_claims_and_patient_balances_0081/t0/verify.py, DSL of check_compute)
SBW {'result': 5.5, 'sbw_closing_rule': 0.0, 'sbw_booking_collection_count': 0.0, 'sbw_credit_count': 10.5, 'sbw_patient_money_count': 0.0, 'sbw_charge_count': 0.0, 'ALL_BASELINE': 0.0}
XFER {'result': 27.94, 'xfer_source_charge_count': 40.0, 'xfer_source_collection_count': 0.0, 'xfer_visit_refund_offset': 33.94, 'xfer_older_claim_first': 22.44, 'ALL_BASELINE': 0.0} skipSBW 22.44
PAY {'result': 49.91, 'rebill_payment_collection_take': 104.45, 'rebill_payment_credit_count': 75.06, 'rebill_payment_earlier_money_count': 72.41, 'rebill_payment_prompt_pay_rate': 55.46, 'rebill_payment_prompt_pay_window': 55.46, 'ALL_BASELINE': 169.0} skipXFER 75.06
Discount posted with the payment: RND(55.46*10/100)=5.55 (5.546, 0.004 from a half cent).
- REVISION (task 0 build): XFER visit-refund factor dropped (it left the crediting claim's ledger at -6.00 while the rule saw no credit — a state-form contradiction and a double-refund trap); replaced by xfer_receiving_charge_count. Empty FK fields seeded as null; membership dues lines dropped (no read node feeds them; closure rule). Final task-0 figures: write-off 5.50, move 33.94, payment 44.51 + discount 4.95.
- Task 0 per-task gates: check_extended OK, check_task_tools OK, replay OK, solvability OK, compute OK, grounding OK, cross_fire OK.
- Task 1 policies written: claim_ext_booking_collection_application (6 factors, cross-difficulty visit lines) and claim_ext_cost_share_balance_payment (5 factors). THIN: both are record-keyed compositions of the charter's measures (claim_msr_time_of_service_collected; claim_msr_claim_balance); the "applied once across a claim and the submission it replaced" rule and the 4-tier collection take are the charter-grounded parts.

## Task 1 — verification run (/tmp/insurance_claims_and_patient_balances_0081/t1/verify.py)
TOS {'result': 15.4, 'tos_copay_lines': 0.0, 'tos_estimate_lines': 0.0, 'tos_copay_error_refunds': 20.4, 'tos_copay_path_refunds': 40.4, 'tos_estimate_error_refunds': 21.4, 'tos_already_applied': 40.4, 'ALL_BASELINE': 0.0}
PAY {'result': 7.3, 'cost_share_charge_count': 0.0, 'cost_share_collection_take': 47.7, 'cost_share_credit_count': 11.3, 'cost_share_earlier_payment_count': 17.3, 'cost_share_adjustment_count': 30.0, 'ALL_BASELINE': 0.0} skipTOS 22.7
Task 1 per-task gates: extended, task_tools, replay, solvability (after mapping each seeded row to the base policy whose subject holds its event type), compute, grounding, cross_fire — all OK.

## XF recipe tables (all five policies)
- B5 compute_basis verbatim sweep (scratch sweep.py): every quote verbatim in its rule; every baseline.rule sentence in the rule; every binding has a basis — 0 misses in all 5 policies.
- Defining-sentence table: each ladder sentence ("... counts X as follows: ...") is owned by exactly one factor and quoted by that factor's bindings only; selection sentences (claim of latest third/first statement, latest claim_adjudicated remittance) and assembly sentences ("is the counted ... added together with their signs", "lesser of ...", rounding) are baseline/plumbing; baseline.params: SBW [small_balance_writeoff_threshold, statement_cycle_days]; others [] (their baseline paragraphs carry no parameter).
- A1 transitive factor-reads: no factor binding reads another factor's binding. Plumbing bindings that combine factor outputs: sb_balance, xf_credit, xf_tgt_bal, pr_balance/pr_discount, ts_collection, cs_balance, result. xf_ahead reads xf_credit (plumbing built from two factors) — recorded as the one A1-adjacent read: the older-claim-first method takes "the lesser of the credit and ..."; flagged for the auditor.
- A6 all-pairs method tiers: sbw_closing_rule (below collections minimum after cycle end | nothing | small-balance threshold rule): pairs differ by threshold parameter (collections_min_balance vs small_balance_writeoff_threshold) and by a zero rule; xfer_older_claim_first (ledger balance | nothing | statement amount_due): pairs differ by input (ledger SUM vs statement amount_due vs none); rebill_payment_collection_take / cost_share_collection_take: own entry | replaced submission's entry | both | none — distinct inputs (different claim ids); rebill_payment_prompt_pay_window: applied | not applied (two tiers share 'not applied' — flagged); tos_already_applied: own entries | replaced submission's entries | none.
- A7 T1/T2 (min/max shapes): XFER result MN(credit-ahead, receiving balance): T1 holds for all four factors (sensitivity run); T2: receiving-charge factor binds the min whenever receiving balance < credit (producible: small rebill). SBW limit: T1 holds. MX floors (credit, balance) bite only at <=0.
- B1 edge probes: absent records (only customer + coverage) -> every policy 0.00 (no error); 0.00 balances -> no write; same-day dates: DAYS(x,x)=0 inside every window (inclusive); third statement due date == frozen date -> 'not passed' tier (nothing written off), as the rule says ('after that statement's due_date'); balance exactly 25.00 -> not below collections minimum (limit 24.99 in cents); prompt-pay day 30 -> applied (inclusive).
- B2 probe table (first-match / selection reads): latest third statement (decoy: claims with only first/second statements; absent -> nothing); latest claim_adjudicated remittance (decoys: claim_denied remittances, older adjudications, same-day tie keeps the first row read — stated as the claim of the most recent remittance); latest first statement (decoy: older claim's first statement); original_claim_id chain (absent -> replaced branch never taken); credit SUMs filter by event_type (received vs transferred vs refunded); visit refund SUMs filter by refund_reason and original_charge_id.
- D4 events written with base triggers: claim_small_balance_written_off [], claim_credit_transferred [], claim_credit_received [], claim_patient_payment_posted [], claim_prompt_pay_discount_applied [], claim_time_of_service_applied [] — none lands in another category.
- D3 owed-at-once: at both openings nothing else is owed (no other credit, no statement falls due, no refund due, membership dues current).
- E1: frozen_time 'YYYY-MM-DD HH:MM:SS EDT'; task_tools.py has no forbidden import; rounding helper and claim lookup are static methods of class _Money; every write tool calls ctx.create in its own body. E2: no example values in docstrings. E3: no composite args.
- Realism / THIN register for the coordinator: charter-grounded factors — sbw_closing_rule, xfer_older_claim_first (oldest service date first, cross visit), rebill_payment_prompt_pay_rate / _window, tos_already_applied, cost_share_collection_take. Record-keyed restatements of the charter's balance and booking-collection measures (THIN, no invented business effect, every amount equals what the charters produce): sbw_*_count, xfer_source_*, xfer_receiving_charge_count, rebill_payment_credit_count / _earlier_money_count, tos_*_lines / *_refunds, cost_share_*_count.
- Traceability pre-docs (run once): only the five unlock tool-name misses (expected before rendering); no other miss.
ROUND 1: gates 7/7 green
