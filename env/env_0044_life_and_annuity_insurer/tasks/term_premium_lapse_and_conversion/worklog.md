# worklog — term_premium_lapse_and_conversion (erl-task-instantiate, M=2)

## Step 0 draws (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=3, factor_counts=[6, 4, 4, 4]
- task 1: prerequisite_problems=3, factor_counts=[4, 5, 6, 4]

## Difficulty-level design (frozen)
Constraints found while reading the blueprint:
- term_policy_converted always triggers whole/ul issuance -> no task tool may write a conversion (cross-category write). Conversion is left out.
- service requests carry no rider/mode details -> only record-derivable pending items are usable: EFT privilege termination (ledger), rider expiries by age (waiver 65, ADB 70), approved face decrease (new_face_amount), approved reinstatement, approved acceleration claim.
- one universal record-based premium method is shared by every premium-writing policy (band on aggregate Ashgrove life coverage, multi-policy fee share, age-graded ADB rate, unit-banded child rate, issue-age waiver rate/base, record mode factor) so the charter gives one answer for an installment premium; expiry policies apply the age test and flip the record.

Task 0 (Harold Whitcombe, LT25, grace after 2nd returned EFT draft, waiver expiry anniversary passed, approved face decrease on file):
  switch (agent, EFT privilege ended -> quarterly)  --value-->  cure
  waiver expiry (agent)                              --value-->  cure
  cure (USER, owner remits overdue premium)           --state-->  face decrease (root, agent, 6 factors)
Task 1 (Lorraine Petrakis, LT25 lapsed, approved reinstatement, ADB expiry anniversary passed during lapse, approved acceleration claim):
  back-installment billing (agent, 5f) --value--> reinstatement (USER, 4f) --state--> ADB expiry (agent, 4f) --value--> acceleration advance (root, agent, 6f); reinstatement --state--> advance

## Task 0 — closed
- policies: term_ext_eft_quarterly_conversion (4f), term_ext_waiver_expiry_repricing (4f), term_ext_grace_cure_remittance (4f, user tool), term_ext_face_decrease_repricing (6f, root)
- tools: convert_to_quarterly_billing_2bfb08af, end_expired_waiver_rider_bcdc46e8, remit_grace_premium_a5ae3e41 (owner=user), apply_face_decrease_78b62126
- gold: conversion 457.71 | waiver ending 402.64 | remittance 578.77 (paid-to 2026-10-15) | decrease 225.84
- prerequisite sensitivity: skip conversion -> remittance 309.08; skip waiver ending -> remittance 633.84, decrease 256.35; skip remittance -> status stays grace_period
- revisions: waiver_end_method lacked a record-derived binding -> added waiver_end_age (MONTHS); waiver ending / decrease history not load-bearing -> waiver ending uses the record mode (no COUNT), decrease reads the requested face by MAX over the approved request
- per-task gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK (traceability deferred: no KB)

## Task 1 — closed
- policies: term_ext_lapse_installment_billing (4f), term_ext_reinstatement_collection (5f, user tool), term_ext_adb_expiry_repricing (4f), term_ext_accelerated_lien (6f, root)
- tools: bill_back_installment_903386f9, pay_reinstatement_amount_3f8d4404 (owner=user), end_expired_adb_rider_b05b3f4a, pay_accelerated_advance_7c43a05b
- gold: billing 247.09 (due 2026-08-01) | reinstatement 534.66 (paid-to 2026-11-01) | rider ending 247.09 | lien 105124.60
- prerequisite sensitivity: skip billing -> reinstatement 287.00; skip rider ending -> lien 105167.53; skip reinstatement -> status stays lapsed
- revisions: lien_charge_method / admin_charge_level lacked own record-derived bindings -> life expectancy read bound to each factor
- per-task gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK

## Difficulty closure
- 8 extended policies, 8 task tools, scopes pairwise disjoint, every policy covered; frozen_time format 'YYYY-MM-DD HH:MM:SS EDT' in both tasks
- final suite: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (branches mean 105.00, steps mean 15.50, history max 42, branches max 121), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; check_traceability deferred until the KB is published
- known audit risks to watch: the record-based premium method is restated in five premium-writing policies (band / fee share ladders recur across their documents); the extended overrides (aggregate band, fee size/share, age-graded accidental death rate, issue-age waiver rate/base, returned-item charge, tiered reinstatement interest, lien built from charge + fee + premium set aside) are declared in each policy's overwrite

## Rework round 2 (audit: audits/policy_task/term_premium_lapse_and_conversion/) — plan
- F-P1 / F-F4 (mode factors keyed to premium_mode; undeclared installment override): remove mode_in_force, billing_frequency_mode, billed_frequency_mode, installment_months; every premium policy uses the base installment sentence (modal factor of the premium mode on record) as plumbing.
- F-P2: grace remittance intro reworded to the single newly-due rule.
- F-P3 / 0.md#5: grace remittance declares overwrites of term_evt_premium_application ("one installment per payment record ..." and the unapplied-money refund sentence) with its own application sentence fixing the paid-to date per covered installment.
- F-C1 + 0.md#1 (parallel premium writers overwritten): waiver ending now follows the conversion (new edge) and removes the waiver charge from the installment on record; the face decrease releases premium from the installment on record — every premium write is read by a later scored write.
- F-F1/F-F2/F-F5/F-F7 (unreal ladders): conversion_method, waiver_end_method, premium_in_effect, adb_end_rate removed; replacements: waiver_charge_base (method), band_measurement (method), fee_concession (parameter), adb_due_rate (parameter, real at billing).
- F-F3: fee before sharing tiers are deductions from the product fee (distinct on ART too).
- F-F6: reinstatement rate/anchor cut points moved to 15 / 90-120 days so evidence_type no longer names the tier.
- 0.md#3: lapsed UL on Harold's life seeded as near-miss. 1.md obs 6: whole service request seeded for the whole advance. 1.md obs 7: premium months relabelled parameter.
- size_band evidence: band ladder chooses the renewable (ART) ladder past the level premium period (record date span), making band its own record-derived factor.
- r2 task 0 closed: conversion 456.39 -> waiver ending 401.32 (from the installment on record) -> remittance 577.23 (user, paid-to 2026-10-15) -> decrease 224.52 (from the installment on record). Propagation run: every conversion/waiver factor baseline moves the terminal modal_premium (370.61 / 232.47 / 212.72 / 220.51 / 206.58 / 224.96 / 236.32 / 228.52 vs 224.52). Per-task gates all OK.
- r2 task 1 closed: billing 245.76 -> reinstatement 533.29 (user) -> rider ending 245.76 -> lien 104,874.85. Added read find_whole_life_service_requests (step 7; later steps shifted +1) so the newly seeded whole claim enters the closure. Revisions during r2: billing's due date now reads the paid-to date (LATEST-only history was not load-bearing); the elected amount is read by MAX over the approved claim (history load-bearing); waiver ending declares its override of the base installment sentence.
- r2 final suite: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK.

## Rework round 3 (audit revision_2) — plan
- N-1: back-installment due date advances with each billed unpaid installment (paid-to date + one modal period per billed installment still unpaid, i.e. one period after the latest billed due date); count read by COUNT so history stays load-bearing.
- N-2: conversion rule drops the "modal factor of the mode on record" sentence and unused binding; declares override of the base installment sentence by its quarterly-factor sentence.
- N-3: waiver ending drops adb_age_rate (scope at age 65) for band_measurement (method, cross whole); dead fee/annual sentences removed (O-7).
- N-4: premium months ladder by life-expectancy band reachable within 12 (<=6 -> LE, 7-12 -> 12, waiver claim -> none); paid-ahead offset tiers all reachable at an in-force write (covered fully / partly / not ahead).
- 1.md new#1: lapsed UL on Lorraine's life seeded as near-miss for the rider-ending computation (band measurement, fee share).
- O-8: decrease's waiver sentence aligned to "has reached the waiver rider expiry age".
- r3 closed. Charter: N-1 (billing due date via unpaid billed count), N-2 (conversion modal sentence/binding removed, installment override declared), N-3 (waiver ending: band_measurement replaces adb_age_rate; dead fee/annual sentences and bindings dropped; overwrite of the annual-premium clause dropped as no longer applicable), N-4 (premium months none / 6 / LE; paid-ahead offset none / partial / as is), O-8 (decrease waiver sentence). Tasks: task 0 values unchanged (456.39 / 401.32 / 577.23 / 224.52), waiver ending factors 397.18 / 383.38 / 413.12 / 405.32; task 1 lapsed UL near-miss seeded, values unchanged (245.76 / 533.29 / 245.76 / 104,874.85), lien factor baselines 157,041.52 / 107,041.52 / 104,899.85 / 104,924.85 / 104,383.33 / 105,120.61. First try of the premium-months ladder (12 months above 6) left paid_ahead_offset decorative (4 installments either way) — changed to the life expectancy above 6, which bites.
- r3 final suite: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK.

## Rework round 4 (audit revision_3)
- N-5: lapse-billing sentence rewritten — "that due date is the paid-to date on record advanced by one modal period of the premium mode on record for every billed installment still unpaid on the ledger (...), which is the due date one modal period after the latest billed due date." Compute unchanged; the due_age basis now also quotes it; task 1 bill tracing quotes the new sentence with its arithmetic (2026-05-01 + 3 months x 1 = 2026-08-01). Task 0 untouched. Scored values unchanged.
