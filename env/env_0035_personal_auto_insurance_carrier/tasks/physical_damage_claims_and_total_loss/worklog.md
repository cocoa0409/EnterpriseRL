# worklog — physical_damage_claims_and_total_loss (category physdmg), M=2

## Step 0 — difficulty pre-check
- Read: skill references (product_extended.yaml, task_tools.py, task.json), blueprint.yaml, products/physdmg.yaml,
  db_schema.json, share_tools.py (verify K=2 credentials; finders take no claim_number filter).
- Draws (draw_counts.py --tasks 2):
  - task 0: prerequisite_problems=2, factor_counts=[4, 6, 4]
  - task 1: prerequisite_problems=1, factor_counts=[5, 6]
- Constraints found:
  - Customer-owned decisions in this difficulty (blueprint): accepting a total-loss settlement offer, and choosing to
    keep the salvage. These are the only owner=user acts; each task takes one of them.
  - Events with cross-category triggers (coverage_add/remove, storage_start/end, deductible_change, inspection_lapse)
    are never written by a task tool. Writable: claim events, payments (no trigger except subrogation recovery,
    which stays inside physdmg), physdmg_total_loss_settlements.
  - Compute can read only this coverage's fields/events/settlement rows and other categories' holdings/ledgers;
    vehicles/drivers/customers tables are not readable, so every factor rests on physdmg history, auto policy /
    auto_transactions, telematics, billing.
- Problem/space plan (5 extended policies, pairwise disjoint per task):
  - task 0 (financed vehicle surrendered, loan payoff option): coverage acceptance deductible (agent, 4 factors)
    -> surrender settlement accepted by customer (user, 6) -> loan/lease payoff benefit (agent, 4; root).
  - task 1 (customer keeps the hail-totaled vehicle): Deductible Rewards claim-free credit (agent, 5)
    -> kept-vehicle settlement accepted by customer (user, 6; root).
- Tool names (uuid4().hex[:8], one call per tool):
  record_claim_acceptance_ec9cfb06, accept_total_loss_settlement_c07cd979, pay_loan_lease_payoff_8a830e94 (task 0);
  grant_claim_free_credit_c23d8d33, keep_total_loss_vehicle_b04c3b51 (task 1).

## Task 0 — loan/lease payoff benefit on a surrendered total loss (closed)
- Tree: physdmg_ext_accident_deductible (agent, 4f) -> physdmg_ext_surrender_settlement (user, 6f) -> physdmg_ext_loan_payoff_benefit (agent, 4f, root).
- Revisions: (1) `in (tuple)` not allowed by the compute grammar -> chained `==`/`or`; (2) `bool()` not allowed -> plain `and` chain;
  (3) empty-string id fields counted as dangling FKs -> id fields dropped when empty; (4) `_claim_owner` helper counted as an
  unnamed task tool -> inlined into each tool; (5) weighting factor wrongly labelled cross_difficulty (reads `package` of another factor)
  -> null; (6) total-loss waiver partial share 50 -> 75 so the Deductible Rewards weighting stays load-bearing (net deductible > 0);
  (7) seed tables never read by gold (driving record, telematics score rows, billing account) removed for closure.
- Handling-time results (evalx.py, then check_compute): 275.00 / 31,113.78 / 4,605.26; all-baseline 750.00 / 29,635.83 / 5,024.02;
  every factor baseline differs (see task dossier §4).
- Gates (per task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK.
- Manual values gates: prerequisite sentences pass the four-point test (one negated "not paid until", one affirmative "fixed only after");
  each state is brought about by exactly one tool; persona raises only the root and never hints; the user tool is the customer's own
  acceptance (blueprint decision) and completes synchronously; no real-world wait (title receipt governs the later settlement payment,
  which is not part of this tree); history rows (earlier decision 500, repair payment 1,765, claim-free credit 150) agree with the
  charter's own rules.

## Task 1 — kept-vehicle settlement after a hail total loss (closed)
- Draw (draw_counts.py --task 1): prerequisite_problems=1, factor_counts=[5, 6].
- Tree: physdmg_ext_claim_free_credit (agent, 6f, state_due) -> physdmg_ext_kept_vehicle_settlement (user, 5f, root).
- Revisions: (1) kept-vehicle baseline no longer mentions the retitling allowance (baseline silent about factors); (2) ACV read via
  MAX so the history floor bears weight; (3) retained-equipment and retitling factors own their evidence bindings (drivable/estimate,
  policy state); (4) the base once-per-period dedup clause is superseded (declared) because the extended rule redefines which paid
  claims restart the claim-free year and fixes the credited year's end date.
- Handling-time results: credit 235.00 (all-baseline 0.00), kept-vehicle settlement 11,036.10 (all-baseline 12,189.00); edge skip ->
  10,956.10. Every factor baseline differs.
- Task-0 history consistency re-checked under this charter: Teresa's 2026-04-18 claim-free credit 150 = 100 + 25 DriveSense + 25 tenure
  (no billing account seeded -> payment-record bonus 0), cap 750 (Premier).
- Manual values gates: negated prerequisite sentence, record-visible, one resolving write; persona raises only the root; the customer's
  keep-the-salvage decision is the user write and completes synchronously (owner-retained paperwork governs the later payment, not part
  of the tree); seeded decisions/credits/ledger agree with the charter.

## Final run (no --task)
- EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (history_rows_max=16, branches_max=62), GROUNDING OK,
  CACHE-DIFF INFO, SCOPE OK. check_traceability not run (KB not yet published).
- Coverage: task 0 = {accident_deductible, surrender_settlement, loan_payoff_benefit}; task 1 = {claim_free_credit,
  kept_vehicle_settlement}; disjoint; all 5 extended policies covered; 5 tools, none shared.
- Scratch authoring scripts and __pycache__ removed from the write domain.

## Round 2 — policy-task audit rework (audits/policy_task/physical_damage_claims_and_total_loss/)
- P-1: kept-vehicle settlement now declares the override of the base new-car-replacement sentence ("A vehicle the customer keeps is
  valued at its actual cash value in every case ... applies only to a vehicle surrendered to Cardinal"), also stated in its rule.
- F-1: repeat-claim surcharge removed from the accepted-claim deductible; replaced by a tenure loyalty reduction (120 / 60 months).
- F-2: uninsured-driver waiver relabelled parameter; DriveSense reduction is now the method factor (percentage for 90+, flat amount
  for 75-89, none otherwise). A fault-determination count guards the waiver (keeps the history aggregate load-bearing).
- F-3: Deductible Rewards weighting relabelled parameter (surrender settlement keeps replacement_cost_value as its method factor).
- F-4: package custom equipment tiers now raise the option's limit (+2,000 Premier, +1,000 Preferred), never cut it.
- F-5: payoff_to_loss_date is now a day-count convention (whole-month rent charge for a leasing company, daily actual/365 interest for a
  lender, as stated within a 10-day grace).
- F-6: option seasoning and tenure share removed; replaced by assumed contract rate (new <= 24 months / new older / used) and the state
  lien-release charge added outside the cap.
- F-7: kept-vehicle tax basis rebuilt on replacement purchase (full kept value when a replacement was added after the loss; none within
  30 days without one; kept value less salvage otherwise).
- T-1: retitling allowance worded "added to the kept-vehicle settlement".
- C-1 (tasks 0 and 1): persona guard lines no longer name settlements, deductibles or credits; no_user_hint rewritten.
- K-NM: task 1 inception moved to 2016-09-20: 119 months to the loss (kept-vehicle loyalty mid tier) vs 120 months to the grant
  (claim-free credit long tier) — the near-miss; package Preferred (credit cap now 75 percent of the collision deductible).
- O-10: "(half up)" dropped from the deductible combination sentence. O-9 disappears with the seasoning factor. O-1/O-3/O-4/O-5/O-6/O-8/
  O-11/O-12 left as observations (no defect demonstrated); O-2 is blueprint-level; O-7 unchanged (Premier tier excludes nothing).
- Seeds: task 0 earlier decision 400.00 and repair payment 1,865.00; task 1 hail decision 560.00 — both follow the revised deductible rule.
- New figures: task 0 262.50 / 31,003.53 / 5,165.29; task 1 250.00 / 11,244.00. Every factor baseline differs; all-baseline
  750.00 / 29,648.33 / 5,146.77 / 0.00 / 11,982.50.

## Round 3 — policy-task audit revision 2 (N-1, N-2, N-3; O-13, O-14)
- N-1: loan payoff baseline.rule now removes the finance charge accrued since the loss by daily actual/365 simple interest at the
  used-vehicle rate (used_vehicle_rate_pct, listed in baseline.params). The convention factor now decides `finance_charge`: leasing
  company -> whole-month rent charge; within the 10-day grace -> none; otherwise the daily convention (fall-through = baseline). The
  contract-rate factor's fall-through (9.4 percent) is now the baseline figure.
- N-2: claim-free credit Preferred cap = option maximum credit + preferred_cap_uplift 250 (always above the basic cap); task 1 unchanged.
- N-3: task 0 Outback is now leased from Fifth Third Auto Leasing Trust, added/PD effective 2024-09-05 (persona: "leased through Fifth
  Third"); convention takes the rent-charge tier; contract-rate near-miss 23 months to the loss vs 25 to the acceptance.
- O-13: lien-release charge only where a shortfall exists. O-14: "the loss date not counted" and the vehicle-add fallback written into
  the rule.
- Task 0 benefit 5,165.29 -> 5,245.24 (all-baseline 4,734.16); other figures unchanged. Task 1 figures unchanged.
