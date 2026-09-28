# renters_billing_and_cancellation — difficulty worklog

## Step 0 — draws (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=3, factor_counts=[6, 4, 6, 5]
- task 1: prerequisite_problems=1, factor_counts=[5, 5]

## Step 0 — pre-check of the claimed renters line
- Event types claimed by the difficulty: cancelled, reinstated, cancellation_rescinded, fee_assessed, fee_waived,
  payment_received, payment_returned, additional_premium, return_premium, refund_issued, balance_written_off,
  collection_referred, relocated, coverage_updated, billing_plan_changed.
- Hard constraint found: `renters_policy_cancelled` (and `renters_policy_expired`) declare an unconditional trigger
  into `umbrella:umbrella_underlying_lapsed`; no task tool may write that event, so no problem of this difficulty
  cancels a policy. Cancellations appear only as pre-existing records.
- Every gold write must carry a computation, so the customer's own write (owner=user) must carry a number: the
  only customer-owned write with a number is a payment of their own money (signing writes carry no number).
- `renters_cancellation_rescinded` carries no number, so a pending-cancellation tree cannot close on it; the
  reinstatement (whose fee is a number) can.

## Claims (pairwise disjoint)
- task 0 (root: catch-up payment by card, customer's own write):
  renters_ext_discount_stop_charge (6) -> renters_ext_discount_restart_credit (6) -> renters_ext_catch_up_amount (5)
  and renters_ext_late_charge (4) -> renters_ext_catch_up_amount.
  tools: post_discount_stop_charge_d8b9b7f1, post_discount_restart_credit_e779526e, assess_late_charge_664a192e,
  pay_catch_up_by_card_50a8e701 (user).
- task 1 (root: reinstatement after nonpayment cancellation):
  renters_ext_reinstatement_cure (5, customer's own card payment) -> renters_ext_reinstatement_fee (5).
  tools: pay_reinstatement_cure_5468a22a (user), reinstate_lapsed_policy_e7e59896.
- Headroom: task 0 occupies the in-force billing corrections (discount stop/restart, late charge) and the
  catch-up; task 1 occupies the ended-policy reinstatement path. Nothing is reserved.

## Log
- (design) cross-difficulty evidence: task 0 reads the customer's FloodGuard (flood difficulty) holding and
  ledger; task 1 reads the customer's LandlordGuard (dwelling difficulty) holding and ledger.

## Task 0 — closed
- Tree: stop charge (6) -> restart credit (6) -> catch-up (5, user); late charge (4) -> catch-up. Gold: 8.07, 17.57, 6.75, 51.79.
- Capability cards: post_discount_stop_charge (agent; +1 additional premium, restates term_premium, balance +); post_discount_restart_credit
  (agent; +1 return premium pro rata, restates term_premium, balance -); assess_late_charge (agent; +1 late fee on term/installment,
  balance +); pay_catch_up_by_card (user; +1 card payment, reference generated starting with 2, balance -). No tool checks anything.
- Revision: helper `_policy` in task_tools.py was read by check_extended as a tool -> inlined; EXTENDED OK.
- Per-task gates (--task 0): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Manual values gates: prerequisite sentences pass the four-point test (one negated, two affirmative); each state is booked by
  exactly one write; late charge commutes with the discount postings (same amounts, same hash); persona raises only the
  catch-up and never a prerequisite; baseline paragraphs are the business's standard methods.

## Task 1 — closed
- Tree: reinstatement cure (5, user card payment) -> reinstatement fee (5). Gold: cure 62.90, fee 22.87 (19.00 without the cure).
- Capability cards: pay_reinstatement_cure (user; +1 card payment, reference starting with 2, balance -); reinstate_lapsed_policy
  (agent; status in_force, reason/closed/pending cleared, +1 reinstatement fee, +1 reinstatement reversal referencing the credit,
  no-loss request completed, balance +). No tool checks anything.
- Per-task gates (--task 1): all OK on first run.

## Difficulty closure (final run, no --task)
- EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 36/36, 1.json 29/29); SOLVABILITY OK; COMPUTE OK (suite means
  branches 54.00, steps 14.50; history_rows_max 42; branches_max 79); GROUNDING OK; CACHE-DIFF INFO; SCOPE OK.
- check_traceability skipped: the published KB does not exist yet.
- Coverage: 6 extended policies, task 0 claims 4, task 1 claims 2, disjoint; 6 tools, 4 + 2, disjoint.
- Identifier band 2: phones 330-218-4467 / 330-274-9153; mailing ZIPs 43214 / 43302; policy numbers RG4-2417-3380, PU-2208-5147,
  VF-2630-7719, FG-2356-0418, RG4-2583-0716, LG3-2149-5832; claims RGC-23-204417, RGC-25-213860; payment references start with 2.
- Temporary authoring scripts lived in the session scratchpad only and were deleted; __pycache__ removed from the write domain.

## Rework round 2 (audits/policy_task/renters_billing_and_cancellation: _difficulty.md, 0.md, 1.md)
- F-1/F-T0-1: late charge declares overwrite of fees_and_waivers "The returned-payment fee ... tier amount is 0.00 is not charged at all." (no gate condition quoted).
- F-2: late_lateness_scaling -> late_lateness_method (percentage-only / flat+10% / flat). Late 6.75 -> 6.58.
- F-3 + O-FL2: catch_acceleration -> catch_ahead_of_billing (unbilled term premium / next installment + plan service charge / nothing);
  catch_accelerated_service_charge -> catch_early_service_charge_relief (baseline 0). Catch-up 51.79 -> 52.16.
- F-4: cure_late_charge_treatment decides cure_late_collected by selection (none / latest entry / every entry). Cure unchanged 62.90.
- F-5: fee_lapse_age_scaling relabelled parameter. Fee unchanged 22.87.
- F-T0-3: flood_relief_full_pct 25 -> 20 removes the 9.225 half-cent tie; tie detector over every RND: none. Stop 8.07 -> 8.61.
- Observations: O-RC1 latest-closed ending policy; O-RC2/O-RC3 overdue installment = latest billed already past due, its own
  service charge; O-T0-1 returned payment = never received; O-RC5/O-OV2 division stated in rule; O-PG1 condition trimmed;
  O-PG2 'at least'; O-PS1 catch-up sentence scoped to policies taking effect while no discount was carried; O-OV3 excess stays
  as credit; O-FL1 restart tier 2 counts from 7 days before effective date, capped at the term; O-AB1 cure docstring neutral;
  O-T1-1 persona pays only when told a payment is needed; O-RC4, O-FL3 no change.
- Gates re-run (final and per task): all OK; check_traceability skipped (no KB yet).
