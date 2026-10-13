# Worklog — folio_charges_and_adjustments (M=2)

## Step 0 — difficulty pre-check (done)
- Read references (product_extended.yaml, task_tools.py, task.json), blueprint.yaml, products/folio.yaml,
  db_schema.json, share_tools.py, and the gate scripts' contracts.
- Draw (draw_counts.py --tasks 2):
  - task 0: prerequisite_problems=1, factor_counts=[4,5]
  - task 1: prerequisite_problems=2, factor_counts=[4,5,5]

## Key scoping decisions (recorded because the skill gives no explicit route)
1. Every gold write must carry a computation (check_solvability). folio_reopen / folio_resettle carry no
   numeric parameter, and folio_refund's amount is pinned by base to the credit balance (no factor can move
   it without contradicting base). A settled folio would force reopen/refund/resettle into gold with no
   computation -> both task worlds are IN-HOUSE stays whose folio is `open` (blueprint summary: guests call
   "after or during a stay"). Event types used: folio_adjustment and folio_breakfast_benefit_credit.
2. folio_adjustment triggers a loyalty points reversal for charge codes room/breakfast/food_beverage/spa;
   no tool may write such a row, so adjustments are restricted to parking lines.
3. Value couplings that survive factor-sensitivity (caps kill the factors on the other side of a min):
   - task 0: the day's elite dining allowance (Titanium/Ambassador) is drawn first by the elite breakfast
     credit of that business date; what remains is carried to a food and beverage line of that day.
   - task 1: the weekly parking maximum caps the parking lines of a stay net of the corrections they
     carry, so each nightly parking correction changes the excess the weekly maximum takes off.
4. Customer's own writes (owner=user): task 0 — the member applies the carried dining allowance to her
   dinner check herself (a benefit election over her own membership); task 1 — the guest elects the
   weekly parking maximum for the stay (a package election).

## Task 0 — closed
- Tree: root folio_ext_dining_allowance_carryover (user tool apply_dining_allowance_ccaea779) <- value_input
  folio_ext_breakfast_credit (agent tool post_breakfast_credit_af6b7bed). Factors 5 / 4 (draw [4,5]).
- Gold: credit_amount 210.00 (baseline 90.00), carry_amount 78.00 (baseline 0.00; 286.00 if the breakfast credit is skipped).
- Revisions: inlined tool helpers; dropped empty FK strings and booking_charges; added find_loyalty_transactions read;
  breakfast line read via MAX over the latest breakfast day.
- Per-task gates: EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK.

## Task 1 — closed
- Tree: root folio_ext_weekly_parking_cap (user tool elect_weekly_parking_5ade5692) <- value_input
  folio_ext_self_parking_savings (correct_self_parking_29958fbc) and <- value_input folio_ext_valet_parking_savings
  (correct_valet_parking_0a0ec721). Factors 4 / 5 / 5 (draw [4,5,5]).
- Gold: 37.80 (baseline 6.72), 48.00 (baseline 9.28), 32.05 (baseline 0.00; 69.85 / 80.05 if a prerequisite is skipped).
- Prerequisite sentences in both directions (affirmative "applied only after", negated "not worked out until").
- Revision: added a hotel-corrected duplicate minibar posting so the one-adjustment-per-line gate has evidence.

## Difficulty closure
- Coverage: task 0 {breakfast_credit, dining_allowance_carryover}, task 1 {self_parking_savings, valet_parking_savings,
  weekly_parking_cap}; disjoint; all 5 extended policies and all 5 tools used.
- Decision: folio_reopen / folio_resettle / folio_refund are not claimed by any policy (no computable parameter that
  base does not already pin); recorded here for the policy audit.
- Traceability gate deferred until the KB is published.

## Round 2 — policy-task audit closure (audits/policy_task/folio_charges_and_adjustments/)
- F-1: breakfast credit now declares the override of base "When the outlet did not apply the credit, guest services posts it later ..." (reason and desk limit kept; the desk's own posting is limited to the most recent morning, and an earlier missed morning goes to the hotel as a billing dispute).
- F-2: removed the over-broad overrides of base's late-check-out elite_benefit_not_applied clause (self, valet) and room incorrect_rate clause (weekly). Both base corrections stay in force; the parking corrections add cases under those reason codes. The only override still declared is the parking-charge sentence of folio_incidental_rules.
- F-3 / T1-F1: self-parking method is now tier_parking_benefit (Ambassador scaled x2, Titanium supplemented +4 points, otherwise as it stands); member_rate_multiplier relabelled parameter and made multi-source (rate plan AND tier).
- F-4 / T1-F2: weekly_basis_rate relabelled parameter; fall-through changed from "valet rate" to "rate of the service parked on the most recent night".
- F-5 / T1-F3: nights_counted replaced by maximum_method (pro-rated / full weeks plus remainder capped at weeks rounded up / full weeks plus remainder) chosen by tier AND direct channel; future reservation nights are no longer counted; the GDS-favouring tier is gone.
- F-6 / T0-F3: dining_persons no longer carries the direct-channel conjunct.
- F-7 / T0-F2 / T1-F4: multi-source factors over distinct records: dining_allowance_method (tier AND channel, both tiers compound) in task 0; member_rate_multiplier (rate plan AND tier) and maximum_method (tier AND channel) in task 1.
- F-8 / T0-F4 / T1-F5: memberships follow loyalty_elite_qualification (Titanium earned the day the 2025 count reached 75; guaranteed through 2027-02-28; year-end reset on 2026-01-01; card anniversary nights; card floor below the earned tier). Task 0 card is now the Ashbury Rewards Card.
- T0-F1: the valet lines were removed from the task 0 world (no parking at all; the persona says the family came by rideshare), so no valet savings are due there.
- O-2 largest breakfast line stated; O-3 carry-over deducts "elite credits already standing for that business date"; O-4 nights parked defined as parking lines; T1 observation: election covers the nights parked so far. O-5 / O-6 (base cross-problem orders; base event wording for the credit) need no change: no edge rests on them, and the declared supersession covers the carry-over.
- New gold: task 0 credit 201.00, carry-over 87.00 (terminal 2687.60); task 1 37.80 / 48.00 / 55.48 (terminal 3227.33).

## Round 3 — revision_2 audit closure
- N-1 / T1-N1: maximum_method's Gold/Platinum tier now caps the remaining nights at half the weekly rate. The old cap ("never more than the weekly rate for the weeks rounded up") could never bind. Grid check: the tier differs from the fall-through in 105 of 245 cases and is never higher. The task 1 rationale sentence is corrected; gold is unchanged (the customer takes tier 1).
- O-8: same-night tie-break stated in the rule, the baseline.rule and compute_basis (valet wins, as the compute does).
- O-7: kept as an observation. The reuse of reason codes is additive, and no base amount exists for parking lines under those codes.
- Task 0 untouched (PASS in revision_2).
