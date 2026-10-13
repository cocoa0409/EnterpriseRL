# Worklog — income_annuity_payouts_and_survivorship (M=2)

Draws (draw_counts.py --tasks 2): task 0 prerequisite_problems 2, factor_counts [4,6,6]; task 1 prerequisite_problems 2, factor_counts [6,4,4].

## Task 0 — period-certain commutation (Claire Brennan-Ortiz, contract IA50731846)
- Policies: income_ext_beneficiary_arrears (6 factors, agent), income_ext_commutation_election (6, owner=user), income_ext_commuted_value_payout (4, agent, root).
- Tools: pay_beneficiary_arrears_076c3375, elect_commuted_value_be644418, pay_commuted_value_cb4f45b9.
- Chain: payout -> election (value_input, state form) -> arrears (value_input, state form).
- Gold: arrears 538.88 gross / 477.90 net; commuted value 11932.61; payout net 8949.46.
- Per-task gates: extended, task_tools, replay, solvability, compute, grounding, cross_fire all OK.
- Revision: payout trace figures corrected to the handling-time recovered amount (71386.86, after the arrears write lowered unreturned_premium) — symptom: rationale quoted the opening figure 71027.96; fixed in trace and rationale, re-written.

## Task 1 — joint-and-survivor first death (Dorothy Ann Lindqvist)
- Policies: income_ext_survivor_held_release (6, agent, root), income_ext_post_death_excess_repayment (4, owner=user), income_ext_held_survivor_forfeiture (4, agent).
- Tools: release_survivor_share_80ea435e, settle_post_death_deposit_f655a739, forfeit_held_installment_e717f459.
- Tree: release -> forfeiture (value_input, state form); release -> repayment (state_gate, state form).
- Gold: forfeiture 506.24; repayment 454.40 (excess 516.36 x 0.879998); release gross 506.24 / net 433.31.
- Revision 1: history floor failed for forfeiture and repayment (LATEST-only reads); switched the held amount and the deposit's withheld tax to SUM over the keyed entries; figures unchanged; COMPUTE OK.
- Parallel prerequisites (forfeiture, repayment) replayed in both orders: identical terminal DB.
- Final: all difficulty-level gates run without --task (check_traceability skipped: no published KB yet).

## Round 2 — policy-task audit (audits/policy_task/income_annuity_payouts_and_survivorship/)
- F1: payout declares the base exclusion-ratio sentence as superseded (replaced by its taxable-part sentence).
- F3: arrears tier 1 raises the last annuitant installment by the cost-of-living rate once per anniversary between the death and the first payment date after it (matches the base cost-of-living sentence); task 0 value unchanged (538.88, zero anniversaries).
- F5: every state-tax tier is a rate on the taxable part (0.05 IA/MN/NC/VT, 0.04 DE/NY/OK); task 0 arrears net 469.81, payout net 9068.79.
- F6: arrears interest-period tier 2 now runs from the date the death was first reported (when that precedes proof) instead of from a late approval date.
- F7: task 0 source contract moved from an indexed annuity to Harold's Ashgrove Flexible Premium Deferred Annuity FA50218837 (fixed — claimed by deferred_annuity_withdrawals_and_death_benefits); cross_difficulty labels now `fixed`.
- F2: the task 1 settlement declares the base "Ashgrove first asks the bank ..." sentence (a deposit paid to the surviving payee after continuation is recovered from the payee).
- F4: survivor-percentage ladders removed; forfeiture policy and tool (forfeit_held_installment_e717f459) retired, the forfeiture now happens in the release's single settlement; new prerequisite income_ext_returned_installment_reissue (tool reissue_returned_installment_7c2be31a) for the returned pre-death 2026-08-01 installment; the settlement's fourth factor is the offset left to the release (base overpayment_offset_max_pct).
- Task 1 gold: reissue 851.51; settlement overpayment 454.40 / repayment 327.84; release gross 506.24, forfeited 506.24, offset 126.56, net 303.75.
- Observations closed: O-1, O-4, O-5, O-11 and the persona's cutoff-preview line.

## Round 3 — audit revision_2
- F3 residual: arrears installment = earliest post-death certain installment with no issued payment; tier 1 raises the last annuitant installment once per anniversary up to that installment's own payment date (base cost-of-living rule). Probe: two-arrears case gives 538.88 then 544.27; task 0 figures unchanged.
- O-1(a): held-amount tier reads only what is still held for the arrears installment's payment date.
- O-11: release names "Held installments falling due after the death are forfeited …"; repayment names "… is an overpayment, recorded once per installment" (new rule sentence keeps one entry per deposit). Task 1 figures unchanged.

## Round 4 — audit revision_3
- F3: arrears tier 1 counts anniversaries after the payment date of the last installment issued to the annuitant (not after the death) up to the arrears installment's own date, rounding after each increase; the base cost-of-living sentence is now declared in the arrears overwrite (residual: more than twelve increases are compounded in one step). Probes: task 0 538.88; two-arrears 538.88 then 544.27; revision_3 counter-example 544.27. The false round-3 claim in task 0's notes is corrected.
- O-20: position search covers six post-death dates and only dates already due.
- O-19: record-once sentence covers every tier; release adds "no part of a held installment is ever counted as an overpayment". Task 1 figures unchanged.

## Round 5 — audit revision_4
- F8: arrears scoped to installments falling due between the death and the death claim's approval (payments stopped pending the claim); the installment paid is the first post-death date plus those already issued in the span (exact, no cap, no fallback); 0 when the span stands issued. Election prerequisite sentence and unpaid-past count use the same span. Task 0 figures unchanged; probes: revision-2 case 538.88 then 544.27, revision-3 case 544.27 twice, F8 case no arrears.
