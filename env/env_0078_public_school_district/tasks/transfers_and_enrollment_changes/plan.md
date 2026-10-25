# plan — transfers_and_enrollment_changes (enroll), M=2  (instantiator worklog, unattended run)

## Draw (draw_counts.py --tasks 2)
- task 0: prerequisite_problems=2, factor_counts=[6,5,4]
- task 1: prerequisite_problems=3, factor_counts=[6,4,4,4]

## Hard constraints found while reading (Step 0)
- Only numeric fields of the claimed events live in enrollment_ledger (tuition charge / late fee / payment /
  credit / refund).  Registration, verification, documents, placements and the Pre-K eligibility change carry
  no amount -> every problem of every tree is a Pre-K (Tuition-Based) ledger write.
- DSL: F() reads only the enrollment row; SUM/COUNT/LATEST scoped to this enrollment; cross reads only of
  OTHER categories (meals/care/...); no own-category sibling reads -> sibling discount / employee flag are not
  computable; ledger stamps (sibling_discount_applied, proration) may not be evidence.
- Trigger rule: enroll_withdrawal (meals/transport/care triggers) and enroll_transfer_placement
  (meals_campus_change) are never written.  enroll_registration only with entry_type != new_to_district.
- owner=user: only a tuition payment through the parent portal (owner_ruling (b)); its amount must be a
  priced quote of UNPOSTED months (a payment equal to the posted balance carries no honest factor).
- Eligibility credit / withdrawal credit trees would moot any prepayment -> not used.

## Tree design (v1)
- task 0 (Quintanilla): root = parent pays the rest of the school year in one online payment (user);
  prerequisites = first-month re-rating credit (agent) and combined Pre-K + Creek Kids Club Pre-K Wraparound
  credit (agent, care cross).  value_input x2.
- task 1 (Haverford): root = parent pays the departure settlement through the end of the notice period (user);
  prerequisites = December late fee (agent), late-fee reversal of an earlier month (agent), a fourth credit (agent).
Details/factor cards: design_rationale of each task + worklog below.

## Worklog
- 2026-10-24 resume: tree design settled (v2). Tools: t0 user pay_prek_tuition_in_advance_058a705f; t0 late fee
  post_prek_late_fee_f766f23b; t0 combined credit credit_prek_combined_program_abf513c1; t1 uuids reserved
  43743e06 1e1e8562 2a81de73 decba573.
- task0 (Quintanilla, frozen 2026-12-08 09:40:00 CST): root enroll_ext_advance_payment (user, 5 factors) <-
  enroll_ext_late_fee_assessment (agent, 6) and enroll_ext_combined_program_credit (agent, 4; care cross).
  value_input x2; the two prerequisites commute (late fee ignores credits; credit ignores fees/payments).
- 2026-10-24: wrote enroll_ext_combined_program_credit, enroll_ext_late_fee_assessment, enroll_ext_advance_payment to the extended yaml (task 0 policies).
- task0 seed + evaluation_criteria written (builder /tmp/transfers_and_enrollment_changes_0078/build_t0.py)
- task0 computations, prerequisite_closure, tracing written
- task0 per-task gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK
- task0 design_rationale written
- task1 design (Haverford, frozen 2027-01-04 10:15:00 CST): household application approved_reduced 2026-12-15 reaches
  Rowan (PK4); registrar already moved him to Pre-K (State-Eligible) effective 2027-01-01. Root = parent's first
  installment of a payment plan for the remaining balance (user, 6) <- eligibility-month credit on December (4,
  meals cross) <- December late-fee share reversal (4) <- hardship waiver on the rest of that fee (4).
  Chain E1 -> R1 -> N1 -> P1 plus P1 <- E1, P1 <- R1. Tools: credit_prek_eligibility_month_43743e06,
  credit_prek_late_fee_reversal_2a81de73, credit_prek_late_fee_waiver_decba573, pay_prek_plan_installment_1e1e8562.
  REALISM RISK (recorded honestly): the charter's numeric surface is one tuition ledger with flat fees, so several
  account-standing allowances are board-schedule inventions; listed in the task-1 dossier.
- task1 policies written (E1,R1,N1,P1)
- task1 seed+criteria written (builder /tmp/.../build_t1.py); task1 tree is a chain E1 -> R1 -> N1 -> P1
- task1 computations/closure/tracing written
- task1 per-task gates green (after Oct-05 payment -> card, Dec late fee 28.00, N1 arrears factor)
- task1 design_rationale written.

## XF_recipe pre-green record (all 7 policies)
- A1 factor-reads table (transitive, scratch xf.py): every factor's bindings read only their own evidence bindings ("reads-other-bindings: none" for all 33 factors); assembly (shared_*/credit_total/first_share/result/scoped_*) is plain.
- A3 defining sentences: each factor's ladder sentence is used only by that factor's bindings; baseline paragraphs carry only the default (late fee whole, wraparound credit_standard, advance rate monthly_tuition, basis-month credit 0.00, reversal 0.00, waiver 0.00 on the whole fee, plan 2 installments + plan_fee_standard).
- A6 method tiers (pairwise): unpaid_portion_share none/pro rata(adds unpaid,charge)/whole; wraparound_start_share none/pro rata on 30 days (adds days)/whole; advance_rate_basis charge-less-credits/charge/monthly_tuition (distinct inputs); advance_offer_terms one month/percent of months (adds months)/none; basis_month_share whole/pro rata (adds days)/none; credited_share_reversal whole/pro rata (adds credits,charge)/none; standing_part_rule none/fee-less-credits/whole; down_payment_terms pct of balance/latest late fee/none. No pair is the same combination.
- A7 lesser-of: MN caps (credit <= charge, reversal <= fee, waiver <= part) do not bind on either world (T1: substituting each factor alone moves the result, see factor_sensitivity; T2: a cap binds only in worlds whose additions exceed the source charge); one cap per computation.
- B2 first-match reads + probes: CFIELD care/meals filtered by student_id (absent -> None -> fall-through tier, guarded); LATEST charge/late fee/payment by posted_date (no same-day ties in either seed); XLATEST approval letter (absent -> guarded by XCOUNT > 0).
- B4 rounding: RND(x + 1e-9, 2) on non-negative totals; tools use Decimal ROUND_HALF_UP (_Fmt.money); scored/baseline/sensitivity figures checked > 1e-6 from a half cent (closest: 342.356, 16.0578, 17.951807).
- B5 compute_basis verbatim sweep (scratch sweep.py): 0 non-verbatim quotes, 0 unquoted bindings, 0 factor ids inside tool names, all prerequisite sentences verbatim in their own rules.
- D2: every wait is action form with a fallback_reason because each depended-on schedule can owe 0.00 (no 0.01 floors).
- D3/D4 events written with base triggers: enroll_tuition_late_fee, enroll_tuition_credit, enroll_tuition_payment — all triggers [] (no cross-category write); no withdrawal, placement or registration is written. Owed-at-once: no other category's base rule makes a write owed mid-call that moves a scored read (care CCS remittances are not care_payment rows; meals owe nothing).
- E1 cross rows: care (task 0) priced per care charter (registration fee 40.00 on a Paid-status registration, seat confirmed on payment, first month 384.00 standard_rate CCS, full month); meals (task 1) Reduced from 2026-12-15 on an approved household application with same-day approval letters. Residue: meal accounts without transaction history (unread rows cannot be seeded).
- Residue (A2): several assembly sentences name the structure's own terms (down payment, plan fee, share); recorded for the KB audit.
- FINAL gate block (no --task): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0: closure 20=20, 1: 19=19); SOLVABILITY OK;
  COMPUTE OK (suite means branches 50.00, steps 15.00; history_rows_max 37; branches_max 55); GROUNDING OK;
  TRACEABILITY NOT OK only for the 7 unlock tool names (no KB published yet — expected); CACHE-DIFF INFO; SCOPE OK.
- frozen_time: task 0 = 2026-12-08 09:40:00 CST; task 1 = 2027-01-04 10:15:00 CST. Authoring scripts live only in
  /tmp/transfers_and_enrollment_changes_0078/; no __pycache__ in the write domain.

## Superseded by rework round 3
The factor lists, figures and the P6 framing above are the round-1 plan. The current design (factor sets with realism tags, the eligibility-transition waiver, the due-day rule, seeds) is in each task's design_rationale and in worklog.md "REWORK round 3".
