# universal_life_account_service — instantiate worklog

- draw_counts --tasks 2: task 0 -> 2 prerequisite problems, factor counts [4,4,5]; task 1 -> 2 prerequisite problems, factor counts [6,5,5].
- Task 0 (overloan protection tree): ul_ext_loan_interest_settlement (4, agent) -> ul_ext_overloan_charge (5, agent) -> ul_ext_overloan_protected_face (4, user root). Per-task gates green.
- Task 1 (surrender tree): ul_ext_surrender_charge_assessment (5, agent), ul_ext_guideline_excess_refund (5, agent) -> ul_ext_surrender_payout (6, user root).
- Design notes: the DSL cannot index list parameters, so the surrender-charge schedule is carried as the per-tier/per-year K table copied verbatim from the tier ladders; premium-load computations were avoided because the policy-year premium window is not expressible exactly.
- Detailed per-task dossiers live in tasks/N.json design_rationale.
- Task 0 gold: interest 2466.39, overloan charge 5791.21, protected face 221373.34 (baselines 4234.81 / 7511.00 / 219249.23).
- Task 1 gold: guideline refund 13438.43, surrender charge 516.38, net surrender payment 71708.53 (baselines 13375.00 / 2500.00 / 71691.83); refund and charge commute (identical terminal tables in both orders).
- Final difficulty-wide gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK. check_traceability deferred until the KB is published.
- Rework round 2 (policy-task audit round 1): F-1 months-left wording now "monthly anniversaries still to fall due ... up to and including the next policy anniversary" (settlement discount, deduction reserve); F-2 refund compounding stated in thirty-day months; F-3 authoring wording removed from the charge edge condition; F-4 charge mid tier uses mid-duration attained age 78; F-5 loan margin middle tier from 0.96 so the fall-through is reachable; F-6 care margin removed, replaced by protected_value_carry (CareAssure rows removed from task 0); F-7 compounding baseline = no earnings; loan_type stamp removed from task 0 advances; O-3 payout declares the loan-rate override. Task 0 protected face now 219641.00; task 1 values unchanged. Full gate block green.
