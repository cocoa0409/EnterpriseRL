# Worklog — flight_credits_and_vouchers (category credit), M=2

## Step 0 — difficulty pre-check and draw
- Base charter credit.yaml read in full; copied verbatim as the base section of credit.extended.yaml.
- Draw (scripts/draw_counts.py --tasks 2):
  - task 0: prerequisite_problems=1, factor_counts=[6, 5]
  - task 1: prerequisite_problems=2, factor_counts=[5, 5, 5]
- Constraints found in the gates / charter:
  - compute anchors on one existing credit holding (F/P/SUM/COUNT/LATEST are HID-scoped); a value_input edge must therefore be
    carried by a write on the same credit (ledger entry or holding field).
  - the DSL cannot add months to a date, so every scored write is a number (fee amounts, month counts).
  - lifecycle: the only user transition is voucher acceptance, which carries no number; the customer's own numeric write
    chosen for both tasks is paying a credit service fee by card (a payment is the customer's own affair).
- Budget: 5 extended policies in all (2 for task 0, 3 for task 1), 5 task tools, 2 of them owner=user.
  - task 0 claims reinstatement (expired credit) + reinstatement fee.
  - task 1 claims the telephone redemption fee + extension fee + extension, leaving nothing idle.

## Task 0 — closed
- Tree: credit_ext_reinstatement_fee (root, owner=user, 6 factors) <- credit_ext_reinstated_validity (agent, 5 factors),
  value_input on rf_restored_value, state-form sentence "The reinstatement fee is fixed only after the credit carries the
  restore entry that brings back the value written off at its expiry."
- Tools: reinstate_credit_8e2d0d7d (agent), pay_credit_reinstatement_fee_177d2025 (user).
- Gold: validity_months 9 (all-baseline 6), fee_amount 58.95 (all-baseline 150.00); skipping the reinstatement gives fee 0.00.
- Revisions: (a) flight accruals carry no qualifying dollars; (b) near-misses sharpened (uncontrollable cancellation,
  many_redemptions 2), fee 49.13 -> 58.95; (c) frozen_time 2026-09-24 -> 2026-09-15 so the lateness near-miss bites
  (15 days from the recorded expiry vs 14 from the write-off); (d) the fee rule's first sentence no longer restates the
  dependency ("once reinstated" removed; the overwrite's replaced_by now quotes the prerequisite sentence).
- Per-task gates: EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK.
- Manual values gates: length (goal -> fee rule's restore-entry sentence -> reinstatement -> fee) and breadth (loyalty,
  ticket, companion, ledger) checked; persona names no prerequisite and raises no extra ask; reinstatement window
  anchored on the recorded expiry date (90 days, last day inclusive); every factor off its fall-through; blind draft
  from visible context reproduces 9 and 58.95.

## Task 1 — closed
- Snapshot at claim: task 0 holds the reinstatement pair; task 1 claims the telephone fee, the extension fee and the
  extension, which leaves no policy or tool idle.
- Tree (chain): credit_ext_extension_term (root, agent, 5) <- credit_ext_extension_fee (owner=user, 5), state_gate on
  credit_ledger.fee_type, sentence "... recorded only after the credit carries an extension fee entry dated on the day of
  the extension."; credit_ext_extension_fee <- credit_ext_telephone_fee (agent, state_due, 5), value_input on
  xf_recent_fee_entries, sentence "The extension fee is not worked out until every call-center redemption on the credit
  that owes a telephone fee carries its own linked telephone fee entry."
- Tools: charge_credit_phone_fee_f43f310b (agent), pay_credit_extension_fee_5a6cc7fd (user), extend_credit_f94665bb (agent).
- Gold: telephone fee 10.27 (all-baseline 25.00), extension fee 14.25 (all-baseline 75.00; 19.00 without the telephone
  fee), extension 8 months (all-baseline 6), expiry 2026-11-09 -> 2027-07-09.
- Revisions: persona reactions made generic (no fee named, booking channel removed); accrual miles at the Silver rate.
- Per-task gates all OK.

## Difficulty close
- Coverage: 5 extended policies, 2 tasks, disjoint scopes (task 0: 2 policies / 2 tools; task 1: 3 policies / 3 tools).
- Prerequisite sentences in both directions ("fixed only after", "recorded only after", "not worked out until").
- Final gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (branches mean 43, steps mean 14,
  history max 11, branch max 50), GROUNDING OK, SCOPE OK; CACHE-DIFF info only (it sums a field named amount_usd, while this
  schema's ledger field is amount, so its "true" total reads 0.0; the seeded remaining values equal the ledger).
- check_traceability skipped: it needs the published KB, which does not exist yet.

## Rework round 2 (audits/policy_task/flight_credits_and_vouchers: _difficulty.md, 0.md, 1.md)
- G-1 / T0-F1 / T1-F1 (RED, unreal ladders): member_standing_term and tenured_member_term reworked so no Summit tier
  gets less than a tier below it: upper tier = Platinum/Diamond/Chairman, or Gold meeting the Gold condition (8);
  middle tier = any other Gold, or Silver meeting its condition (7); otherwise the standard term. Params renamed
  upper_/middle_*_term_months. Both task customers keep their tier; gold values unchanged (9, 8).
- G-2: both cardmember rates now read EXISTS (any active pass, else any active co-branded certificate) instead of the
  first active companion row.
- G-3: telephone fee is owed only for the latest call-center redemption while unbilled (earlier unbilled ones lapse);
  compute adds tp_redemption_entry / tp_already_billed guard; extension-fee edge condition aligned.
- G-4 / T0-O2 / T1-O1: each windowed rule defines its rolling window ("fewer than that many whole calendar months
  before the date ... not a count of completed calendar months"); count bindings' compute_basis quote it.
- G-8 / T0-O4 / T1-O4: triggered loyalty_mqd_accrual rows seeded for every flight accrual; a 2026 premium trip added
  per task so the 2026 mqd rows sum to qualifying_dollars_ytd (9860.00 / 5120.00); counts in tier-sensitive windows
  unchanged in tier.
- T0-O1: persona reaction to "it ran out" is now a question about the money, not about saving the credit.
- T0-O3 / T1-O3: multi-source labels in the dossiers corrected (same-record conjunctions not claimed as multi-source).
- G-5, G-6 / T1-O2, G-7: accepted observations, no change.
- All scored values and factor sensitivities unchanged; full gate block re-run green.
