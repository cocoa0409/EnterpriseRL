# worklog — deferred_annuity_withdrawals_and_death_benefits (category fixed, M=2)

## Step 0 — difficulty pre-check
- Draws (draw_counts.py --tasks 2):
  - task 0: prerequisite_problems=2, factor_counts=[6, 5, 6]
  - task 1: prerequisite_problems=2, factor_counts=[5, 4, 6]
- Identifier band: phone 50255501NN, ssn_last4 7000-8499, policy/contract serial starts with 4.
- Base subjects and their eligibility gates (structural, from fixed.yaml):
  - fixed_interest_credited -> fixed_interest_crediting (policy_scope) — clean
  - fixed_surrender_charge_assessed -> fixed_evt_withdrawal, fixed_surrender (policy_scope both) — clean
  - fixed_contract_surrendered / fixed_surrender_paid -> fixed_surrender.signed_surrender_request,
    fixed_sc_waivers.approved_waiver_claim (the latter refined by an overwrite: a waiver claim is needed only where a
    waiver is relied on)
  - fixed_death_benefit_paid -> fixed_death_benefit.proof_and_approval + disbursement_status
  - fixed_annuitization_transfer triggers income:income_contract_issued -> no task tool may write it (cross-category write).
- DSL limits noted: no subscripts (ladder percentage for schedule year y is MX(ladder) - 0.01*(y-1), exact for all six
  tiers since every ladder steps down one point a year); contract-year windows are expressed through within_months
  counted back from the handling date, exact when the handling date falls on the contract's day of month.

## Task 0 — design thesis (surrender chain)
Surface goal: owner (traditional IRA, Ashgrove SecureRate 7, schedule year 6) wants to cash out the contract; her signed
surrender form is on file (received two days before the call). Scored core: the cash surrender value she confirms.
Tree (chain): A fixed_ext_surrender_value (user, root) <- B fixed_ext_surrender_part_year_interest (agent)
<- C fixed_ext_missed_withdrawal_charge (agent).
- C: an excess partial withdrawal of the prior contract year was paid without its surrender charge entry (the
  triggered fixed_surrender_charge_assessed row is missing). State-due correction; it lowers the contract value.
- B: interest for the part year since the last crediting must be credited up to the surrender; it acts on the contract
  value as corrected by C (value_input).
- A: surrender value = contract value (after B) - surrender charge - premium tax recovery (value_input from B).
Factor plan: A 6 (free %, RMD exclusion, senior cap, grading, Ashgrove whole life relationship [cross whole], premium
tax), B 5 (closing-years addition, income-annuity relationship [cross income], withdrawal-history adjustment,
crediting convention, crediting end date), C 6 (free %, RMD exclusion, cap, grading, relationship [cross whole],
late-correction share).
Tools: C assess_missed_withdrawal_charge_e9f9c059 (agent), B credit_surrender_interest_88d8dad0 (agent),
A confirm_full_surrender_fa1c6fc8 (user).

## Task 0 — closed (per-task gates green)
- Policies on disk: fixed_ext_missed_withdrawal_charge (C, 6 factors), fixed_ext_surrender_part_year_interest (B, 5),
  fixed_ext_surrender_value (A, 6). Tools: assess_missed_withdrawal_charge_e9f9c059, credit_surrender_interest_88d8dad0,
  confirm_full_surrender_fa1c6fc8 (user).
- Handling-time results: charge 60.38 (baseline 1,618.23), interest 3,284.82 (baseline 3,056.66), cash surrender value
  153,494.99 (baseline 148,860.91). Every factor moves its result (see tasks/0.json factor_sensitivity).
- Edge sensitivity: skip interest -> CSV 150,217.02; skip correction -> interest 3,286.13.
- r1: empty FK strings flagged dangling by replay -> null.
- Gates (--task 0): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- Manual value gates: persona raises only the surrender; prerequisite sentences checked by hand (state form, one
  writer each, directions mixed: negated for the surrender release, affirmative for the interest); no real-world wait
  (signed request already received, everything synchronous at 2026-10-16).

## Task 1 — design thesis (death benefit chain)
Occupied by task 0: the three surrender-line policies/tools above. Task 1 claims the death benefit line only.
Draw: prerequisite_problems=2, factor_counts=[5, 4, 6] -> renewal rate 4, valuation interest 5, settlement 6.
Surface goal: the deceased owner's daughter (a primary beneficiary, approved claim on file) asks to be paid her share
in a lump sum. Tree (chain): A fixed_ext_death_claim_settlement (user, root) <- B fixed_ext_death_valuation_interest
(agent) <- C fixed_ext_claim_renewal_rate (agent).
- C: the SecureRate 3 guarantee period ended 2026-08-20 while the owner's death was being reported; the default
  renewal (rate reset) was never booked. State-due; its rate feeds the valuation interest for days after renewal.
- B: interest from the last credit through the date due proof was received (the first certified certificate Ashgrove
  held, here on the owner's whole life claim), split at the renewal date; raises the contract value = death benefit.
- A: claim interest on the claimant's share of the death benefit (share reallocated because a co-primary predeceased the
  owner, shown by the term policy the owner held on that child's life).

## Task 1 — closed (per-task gates green)
- Policies: fixed_ext_claim_renewal_rate (C, 4 factors), fixed_ext_death_valuation_interest (B, 5),
  fixed_ext_death_claim_settlement (A, 6). Tools: renew_guarantee_period_14f04954, credit_death_valuation_interest_0cf0ffa2,
  settle_death_benefit_share_569ae0ca (user).
- Handling-time results: renewal rate 0.0480 (baseline 0.0455), valuation interest 16,630.71 (baseline 14,411.03),
  claim interest 1,789.58 (baseline 1,157.03) with share 215,467.59 (50/70 of 301,654.62).
- Edge sensitivity: skip valuation -> claim interest 1,690.92; skip renewal -> valuation interest 16,666.01.
- r1: valuation tool records the valuation date as the interest period end (arg valuation_date).
- r2: replay closure flagged the term death-benefit disbursement row as unread noise -> removed from the seed.

## Difficulty-level closing
- Coverage: task 0 {missed_withdrawal_charge, surrender_part_year_interest, surrender_value}, task 1 {claim_renewal_rate,
  death_valuation_interest, death_claim_settlement} = all six extended policies; scopes and tools pairwise disjoint.
- Final gates (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (branches mean 50.00,
  steps mean 16.50, history_rows_max 24, branches_max 56), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK.
  check_traceability deferred until the KB is published.

## Rework round 2 — policy-task audit (audits/policy_task/.../_difficulty.md, 0.md, 1.md)
- F-C1(a) [SOURCE-POLICY RED, task 0]: P2 overwrite now names base fixed_surrender "The surrender is effective on the date
  the signed request is received in good order; interest is credited to that date." and base fixed_interest_crediting
  "on the date of any withdrawal, surrender, death benefit payment or annuitization for the part year since the last
  crediting", both replaced by P2's end-date ladder sentence. P3's anchor sentence rewritten to "The surrender takes
  effect on the date it is handled, and the cash surrender value is worked out on that date." and declared as replacing
  the same fixed_surrender sentence (also aligns with the tool's termination_date = handling date, O-C3).
- F-C1(b) [SOURCE-POLICY RED, charter]: P1 and P3 free-amount sentences + compute restore the
  free_withdrawal_first_contract_year gate (nothing before it) and the first-year initial-premium base; new bindings
  c_cy_w / a_cy; baseline params list the key. No effect on task 0's world (contract years 5/6).
- F-C2 [SOURCE-POLICY RED, P6]: prerequisite sentence now "A beneficiary's death benefit share is not paid until the
  contract carries the valuation interest credited through the valuation date of the death benefit."; condition names the
  same date; task 1 prerequisite_closure copies updated.
- F-C3 [SOURCE-FACTOR RED, P6]: claim_interest_end_extension and claim_interest_day_count relabelled parameter, tiers
  now carry values (K('check_mail_days') / K('transfer_days') / 0; 360 / 366 / 365); task 1 traces relabelled.
- 0.md #2 [SOURCE-FACTOR RED stamp]: excess withdrawal row free_portion_amount set blank (charge processing never
  completed); seed_consistency and rationale updated.
- 0.md #3 [proof field]: P1 factor_trace baseline free amount corrected to 22,805.20.
- Observations closed cheaply: O-C7 (P4 "has an Ashgrove whole life policy on record, whatever its current status"),
  1.md #6 (historical-rate decomposition removed). Scored values unchanged in both tasks.

## Rework round 3 — validate_scenario token lint
- Symptom: "task_tools.py: forbidden 'from datetime' (real clock)". Cause: renew_guarantee_period_14f04954 used
  datetime for the new period's start/end dates. Change: pure-Python civil-calendar arithmetic (day after the old end,
  same month/day N years later, Feb 29 -> Feb 28 in a non-leap year). Body only; docstring and receipt unchanged.
  Verified identical to the old datetime logic for every end date 2019-01-01..2027-03-19 x 3/5/10-year tiers (0 mismatches).
- task_tools.py sha256 15a06086...3ca00 -> 377c9f8d...dce3e. Scored values, GT steps and seed rows unchanged; full gate
  block green; validate_scenario reports no deferred_annuity errors.
