# worklog — cpi_insurance_verification_and_force_placement (env_0072)

## Draws
- task 0: prerequisite_problems=2, factor_counts=[4,4,6]; task 1: prerequisite_problems=1, factor_counts=[4,6]

## Design decisions (see plan.md for the feasibility finding)
- Trigger rule forces mailed refunds only (contract paid off, record closed) and no capitalised billing.
- Re-review problems compute proof_result (string result) from the proof already on file; refunds compute amount_usd.
- Scoped overwrites: closed-record re-review (refund purposes only), per-channel acceptance tests, closing-month /
  closing-period refund amounts (premium part + contract accrual interest + delay interest + notice credit).

## Task 0
- Policies: cpi_ext_feed_proof_rereview, cpi_ext_upload_proof_rereview, cpi_ext_closing_month_refund (root, user tool).
- Expected: accepted / accepted / 96.55; baseline_results rejected_no_lienholder / rejected_no_lienholder / 41.21.
- Edge skips: feed skipped -> 64.75; upload skipped -> 67.40.
- Revisions: (1) restricted DSL has no str()/tuples/`is` -> rewrote membership as or-chains and None tests as ==;
  (2) value-only ladders failed "tier from records" -> added contract model-year reads (feed/upload collision,
  fax comprehensive) and moved notice counts into the credit factors; (3) multi-source failed because coverage
  bindings forked on None -> replaced with `or` sentinels; (4) review history not load-bearing -> channel COUNT
  gives not_applicable when no proof; (5) replay closure mismatch -> dropped unread dealer/servicing rows.
- Per-task gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.

## Task 1
- Policies: cpi_ext_fax_proof_rereview, cpi_ext_closing_period_refund (root, user tool).
- Expected: accepted / 86.67; baseline_results rejected_no_lienholder / 37.84; edge skip -> 48.33.
- Revision: state_due refund's request binding cited caller intent -> now cites the closed record and the charge
  running past the closed date (initial_state).

## Difficulty-level closing
- compute_basis sweep: every quote verbatim in its rule (ladder sentences placed contiguously, baseline sentences
  adjacent where shared); no factor binding read by another factor or by a plain binding; no factor id is a
  substring of a tool name.
- Coverage: 5 extended policies, 5 tools; task 0 {feed, upload, closing-month}, task 1 {fax, closing-period}; disjoint.
- Known residual risks for the audits: re-review problems exist only because the base gives this difficulty no other
  scored write that stays in-category; per-channel acceptance ladders and the refund remediation components
  (accrual interest, delay interest, notice credit) are company schedules declared as scoped overwrites; RND uses
  Python rounding (no half-cent ties occur in either world).
- Final gates: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK.
REWORK round 1: gates 7/7 green

## Rework round 2 (audits/policy_task r1: CW-1..CW-7, task REDs)
- Redesign recorded in plan.md ("Round 2 redesign") with the adversarial probe table ("Round 2 probe table").
- Refunds now unearned premium + finance charge only; shared refund schedule; shared acceptance schedule for the
  three re-review rules; scoped overwrites with self-naming tails; sentinel reads; ties stated.
- Contracts re-seeded within tier limits; personas no longer comment on figures; T1 lien release seeded and read.
- All task proof text regenerated from replayed bindings (no hand-written figures left in traces).
- Item-by-item closure: rework_claims_r2.md.
- Gates: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK.
REWORK round 2: gates 7/7 green

## Rework round 3 (audits/policy_task r2: R2-A..R2-G + coordinator ruling on real rules only)
- Struck every company-chosen schedule (lienholder/deductible shares, binder cap, tenure grace, finance part,
  lienholder waiver tiers, post-closing offset). Refund = unearned premium only.
- Held-premium route checked and not adopted (no record evidences a received-but-unreviewed proof; held release
  is always full) — plan.md "Round 3".
- Re-reviews: lienholder back to the base own-flag test; seeds re-seeded with listed lienholders and first
  rejections for deductibles; sibling tails fixed; scope edge fixed; article typo fixed.
- Refunds: proof-span ladder (expiring inside period / reinstated policy on file over the whole period / latest
  effective date onward); binder days and post-closing days plain; no contract or servicing reads.
- Probe table: plan.md "Round 3 probe table". Item closure: rework_claims_r3.md.
- Gates: EXTENDED NOT OK (factor counts 3/3/1 and 3/1 below the drawn 4..6; refunds have no parameter factor) /
  TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE NOT OK (same count shortfall) / GROUNDING OK /
  SCOPE OK. The shortfall is the honest limit of real CPI rules on this charter; no invented schedule was added.
REWORK round 3: gates 5/7 green

## Rework round 4 (coordinator ruling: drawn counts fixed, 7/7, real lender/vendor schedules)
- Draw placement: T0 feed 6 / upload 4 / closing-month refund 4; T1 fax 6 / closing-period refund 4.
- Re-review schedule shared by all three rules; refund schedule shared by both refund rules (plan.md "Round 4 design").
- Refund = unearned premium only; struck schedules stay out.
- Seeds: proof dates/deductibles re-seeded; contracts within tier limits.
- Probe table: plan.md "Round 4 probe table". Item closure: rework_claims_r4.md.
- Gates: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK.
REWORK round 4: gates 7/7 green

## Rework round 5 (audits/policy_task revision_3: R3-A..R3-D; coordinator route)
- Struck: closing-day adjustment, state day basis, minimum policy terms; credit tier no longer keys a refund ladder. Funds-final coverage end considered and dropped (business-day clearance not exactly reproducible per channel).
- Re-reviews: feed/fax 6 (model-year, loan-to-value, book-value, credit-tier allowances; reach date method; state expiry buffer), upload 4; upload compute enforces the binder-only scope; tails restate open-record-only review for long uploads.
- Refunds (one schedule): coverage counting (method), replacement grace by plan, renewal grace by state, refund basis method (full_no_lapse / pro_rata_from_proof_effective / standard pro_rata_from_closure); named-channel reads only; counts/reaches stated in rule; refund tools take refund_basis.
- Seeds: month-to-month feed/fax policies and short binders re-seeded inside the refunded periods; T1 carries an accepted binder re-review from 2026-10-06; contracts unchanged.
- Probe table: plan.md "Round 5 probe table". Item closure: rework_claims_r5.md.
- Gates: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK.
REWORK round 5: gates 7/7 green

## Rework round 6 (audits/policy_task revision_4: R4-A, R4-B, R4-C; coordinator route)
- Refund-basis method removed as a factor; basis is a plain branch; standard = base accepted-proof basis by actual days (never 0.00 in scope).
- Refund factors: coverage counting (method) + replacement-gap grace allowances by plan, state and model year (summed); renewal-stretch grace dropped.
- Seeds: every accepted proof starts inside the refunded period, so no other charge is refundable under the kept base rule; T1 payoff 2026-10-08 (payoff row re-simulated), frozen 2026-10-22.
- Solo substitution of every factor moves the result on both worlds (plan.md "Round 6 probe table"). Item closure: rework_claims_r6.md.
- Gates: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK.
REWORK round 6: gates 7/7 green

## Rework round 7 (audits/render_source r1: R1-R7 + trigger note)
- Gap plain; first grace allowance keyed on contract book value (same bands/values); span counts and overlap moved into the coverage-counting factor; standard sentence no longer defers to a retired clause.
- Re-review overwrite: accepted re-reviews record an entry only on every record (matches tools); base status-return retired for them and restated for first reviews; binder_accepted restated; upload rule names no sibling factor quantity.
- Charge pick keyed on latest billing_period_start; closing-period trigger on_request.
- Figures unchanged; probe table plan.md "Round 7 probe table"; item closure rework_claims_r7.md.
- Gates: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK.
REWORK round 7: gates 7/7 green

## Rework round 8 (audits/policy_task revision_6: R6-A, R6-B, R6-C)
- Re-review rules scoped to closed records (not_applicable on open records; base lifecycle in force there); reach ladder re-keyed on paid-off / repossessed / otherwise.
- Shared refund hand-off conditioned on an accepted proof counting for the latest charge; base closure basis restated for every other case.
- Refunds read accepted proofs of every channel alike (union over the four channels); channel decides only which rule reviewed a proof.
- Figures unchanged; probe table plan.md "Round 8 probe table"; item closure rework_claims_r8.md.
- Gates: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK.
REWORK round 8: gates 7/7 green

## Rework round 9 (audits/policy_task revision_7: R7-A)
- Refunds scoped (scope sentence + shared hand-off) to records where no arrival channel holds more than one accepted proof (exact per-channel COUNT); otherwise base, restated and computed as base.
- T0 original 2025 proof re-seeded as an insurance agent call; both worlds inside the scope; figures unchanged.
- Probe table plan.md "Round 9 probe table"; item closure rework_claims_r9.md.
- Gates: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK.
REWORK round 9: gates 7/7 green

## Rework round 10 (audits/policy_task revision_8: R8-A, R8-B)
- Scope stated as a plain record test (no verification_source holds more than one accepted proof entry), no purpose clause.
- Tail restates the base refund clauses verbatim plus one stated reading; out-of-scope compute reproduces it exactly whenever the hand-off condition fails (probe table B: all cases agree).
- Figures unchanged; item closure rework_claims_r10.md.
- Gates: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK.
REWORK round 10: gates 7/7 green

## Rework round 11 (audits/policy_task revision_9: R9-A)
- Out-of-scope reading in both refunds now states the tie rule the compute implements (equal latest effective date: the one recorded first counts); tie sweep of all picks found no other gap.
- No figure change; item closure rework_claims_r11.md.
- Gates: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK.
REWORK round 11: gates 7/7 green
