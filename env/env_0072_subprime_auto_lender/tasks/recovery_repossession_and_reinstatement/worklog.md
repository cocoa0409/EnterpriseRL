# worklog: recovery_repossession_and_reinstatement (env_0072), M=2

## Step 0 (difficulty pre-check)
- Draws: task 0 prerequisite_problems=2 factor_counts=[4,4,5]; task 1 prerequisite_problems=1 factor_counts=[4,4].
- Writable trigger-free events: notice_sent, expense_posted, expense_waived (full amount only), expense_settled,
  reinstatement_quoted, property_released. Never written (unconditional cross-category triggers): recovery_reinstated,
  recovery_redeemed, recovery_vehicle_recovered, recovery_vehicle_sold.
- Only borrower-own numeric write: recovery_expense_settled paid_by_borrower (expense portion of a reinstatement or redemption).
  Its variable part is storage accrued and not posted, so both user policies carry the storage factors.
- DSL limits: no date addition, so a quote's good-through window cannot drive an installment count; the reinstatement
  quote was dropped and replaced (task 1) by a voluntary-surrender fee posting. No list literals: lists live in params.
- Trigger rule: tools write recovery_expense_posted (triggers []), recovery_notice_sent (triggers []), recovery_expense_settled (triggers []).

## Task 0
- Claimed: recovery_ext_agency_fee (4), recovery_ext_sale_notice_period (5), recovery_ext_redemption_expense_payment (4, root, user).
- Seed: generated once by /tmp scratch generator (contract simulated from origination; SCRA cap 2023-08-13..2025-03-12;
  2025 reinstated case; 2026 returns; current case recovered Sunday 2026-10-04, short notice 8 days).
- Fixes during gates:
  - check_extended: keyless and lot-grace factors read only holding fields -> keyless tier now also requires no
    key_replacement_fee posted (COUNT); lot grace tiers carry the lot contract's effective date (DAYS). Prerequisite
    sentences carried code tokens -> reworded in business words.
  - replay: closure missed prior-case activity and the SCRA request -> activity read by contract, service-request read added.
    Dealer rows cannot enter the closure (find_customers allowed once) -> dealer rows dropped, contract dealer_agreement_id null.
  - solvability: intent_source kinds, gate-field evidence, recovery_evt_recovery_and_noi scope entry, recovery_disposition
    scope entry for the settlement, seed_consistency for every activity row, phone verbatim 4145550142.
  - XF review: assembly sentences made generic with fixed order (fee, payment, sale period).
- Gate results task 0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Values: agency fee 570.00 (all-baseline 600.00); sale period 46 days (baseline 15); redemption expense payment 1133.00
  (baseline 1495.00). Edge sensitivity: skip fee -> 563.00; skip notice -> 973.00.
- Final-run fix (suite history depth 5 < 8): task 0's open case gained realistic history rows: a duplicate transport fee
  (2026-10-07) removed once as assessed_in_error (2026-10-08) and two reconditioning invoices (420.00 on 2026-10-15,
  310.00 on 2026-10-16, total within the Class 6 cap 850.00). expenses_outstanding_usd 1005.00. Redemption expense payment
  recomputed to 1863.00 (all-baseline 2225.00; skip fee 1293.00; skip notice 1703.00). The duplicate and its removal are the
  posted-open decoy pair. history_rows_max now 9.

## Task 1
- Claimed: recovery_ext_surrender_fee (4), recovery_ext_reinstatement_expense_payment (4, root, user).
- Seed: contract simulated from origination 2023-06-20; voluntary surrender requested 2026-10-06, delivered keyless Saturday
  2026-10-10 to the company drop-off lot Peachtree Auto Holding - Forest Park; first notice 2026-10-13 -> 2026-10-28 (15 days,
  consistent with the sale-period rule for GA with no additions).
- Values: surrender fee 65.00 (all-baseline 175.00); reinstatement expense payment 261.00 (all-baseline 275.00); skip fee -> 196.00.
- Gates task 1 (per task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.

## Difficulty closing
- Coverage: task 0 {agency_fee, sale_notice_period, redemption_expense_payment}, task 1 {surrender_fee,
  reinstatement_expense_payment}; pairwise disjoint; all 5 extended policies covered; every task calls an owner=user tool.
- Known limits recorded for audit: (1) storage-factor ladders appear in both borrower-payment policies, named after each act;
  (2) the reinstatement payment declares only the voluntary-surrender fee edge and the redemption payment only the
  involuntary agency-fee and sale-notice edges (each sentence scoped by recovery method); (3) contract dealer_agreement_id is
  null in both seeds because the dealer profile cannot enter the closure (customers finder allowed once).
- Final gate run (no --task): EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK.
REWORK round 1: gates 7/7 green

## Rework round 2 (policy audit revision_1: CG-U1, CG-U2, CG-S1, CG-S2, CG-S3, CG-P1, CG-T1, CG-Z1, CG-M1, CG-R1, CG-R2; T0-F1, T0-F2, T0-P1; T1-F1, T1-P1)
- Charter: sale-notice overwrites of the base earliest-sale-date clauses; stated-amount sentence realigned with base; business-day tier at least the minimum;
  latest-stated-date reads (tie-safe) and the E2 sentence realigned; quote expense portion assigned to the payment rule; explicit
  unlimited class fee in the low-value tiers; fee minimums; taper method tiers; late-mailing factor replaces prior-reinstatement days;
  grace window and staffed/after-hours drop-off tiers replace program-start dates; SCRA left-service tier covers ended >= applied.
- Seeds: task 0's 2025 case fee, settlement and notice date re-priced under the current rules; task 1's notice stated amount set
  to the same-day quote amount. Personas use certified channels only.
- Tasks: values, sensitivities, baselines, traces, closure texts and design_rationale regenerated with tier text copied from the charter.
- Probe table recorded in plan.md; rework_claims_r2.md lists each audit item.
- Full gate run: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK.
REWORK round 2: gates 7/7 green

## Rework round 3 (policy audit revision_2: CG2-E1, CG2-Q1, T0-R2-S1)
- Charter: one-reading earliest sale date (record test on each notice's own fields); E2 sentence/condition carried by at least one
  compliant notice; reinstatement payment overwrite moved to the base settlement clause (quotes keep base expenses); self-contained
  sibling storage sentence; self-contained mailing-date formula for the notice's stated amount, declared as an overwrite.
- Seeds: task 0 2025 notice stated amount re-priced (all 2025 rows re-checked as of their dates); task 1 notice stated amount re-priced.
  Scored values of both tasks unchanged.
- Probes: notice-sequence table appended to plan.md; rework_claims_r3.md lists each item.
- Full gate run: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK.
REWORK round 3: gates 7/7 green

## Rework round 4 (render_r1: S1 + docstring note)
- Storage-charging sentence rewritten in both payment policies (rule + overwrite[3], identical); docstrings trimmed; no compute/value change.
- Full gate run: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK.
REWORK round 4: gates 7/7 green

## Rework round 5 (policy audit revision_4: CG4-N1)
- Low-value reduction sentences of both fee policies compare against the baseline-defined standard fee; factor-cross-mention sweep over all five policies clean; no compute/value change.
- Full gate run: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK.
REWORK round 5: gates 7/7 green

## Rework round 6 (seed-only: kb_round2 S1)
- Re-priced every contract late charge and returned-payment fee of both worlds under the published contract fee documents as of each row date; rebuilt fee settlements, payment amounts, fees_due, right-to-cure and notice stated amounts; proof text swept. No scored value moved; yaml and task_tools byte-identical.
- Full gate run: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK.
REWORK round 6: gates 7/7 green
