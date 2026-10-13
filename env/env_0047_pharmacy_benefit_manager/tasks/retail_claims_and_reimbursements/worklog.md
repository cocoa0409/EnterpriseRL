# worklog — retail_claims_and_reimbursements (M=2)

## Draw (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=2, factor_counts=[4,4,5]
- task 1: prerequisite_problems=1, factor_counts=[6,5]

## Difficulty-level pre-check (Step 0)
- Base retail charter closes; retail events with cross-category triggers: retail_claim_paid / retail_claim_reversed /
  retail_dmr_approved (plan ded/oop postings when amounts != 0). Task tools may only write rows whose values do not
  satisfy those `when`s -> a paper-claim approval is only writable with member_cost_share = 0 and deductible = 0.
- Trigger-free retail writes: retail_override_granted (4 types), retail_dmr_submitted/denied/paid,
  maintenance choice, lock-in pharmacy change.
- Member-owned writes with a computable number do not exist in base retail (maintenance choice and lock-in change carry
  no policy-computed quantity). Decision: the member's own writes are the self-service override requests whose
  essence is the member's attestation (vacation travel; lost/stolen report); granting the bridge, dose change and
  paper-claim decision stay agent actions. Recorded as the one semantic stretch of this difficulty.
- 5 problems (2 tasks): vacation (user), lost/stolen (user), dose change (agent), review bridge = emergency supply
  (agent), paper-claim approval at zero cost share (agent).
- Task 0 tree: vacation supply (root, user, 5 factors) <- review bridge (agent, 4) <- paper-claim approval (agent, 4);
  vacation <- approval as well (diamond). Drug Ubrelvy 100 mg (PA under Northbridge Clinical Advanced).
- Task 1 tree: lost/stolen replacement (root, user, 6) <- dose change (agent, 5). Titration story.

## Tool names (uuid8 generated once each)
- approve_paper_claim_1f52e397 (agent)
- grant_review_bridge_supply_635c815d (agent)
- request_vacation_supply_35815dad (user)
- grant_dose_change_override_e9e89c2d (agent)
- report_lost_stolen_replacement_dcea41b5 (user)

## Task 0 — CLOSED (per-task gates all OK)
- Ubrelvy; Open Choice network; Plus plan (OOP met 2500 via medical feed); Clinical Advanced review (approval expired 2026-09-30,
  member-opened renewal pending with 2 info requests); Home Delivery Standard with Ubrelvy Rx on file.
- Gold: approve paper claim 520.27 (step 15) -> bridge 14 days (step 17) -> member vacation request 16 days (step 19).
- Baselines: approval 853.40; bridge 5; vacation 90. Edge skips: approval -> bridge 22 / vacation 31; bridge -> vacation 30.
- Revisions: closure (added ledger + formulary reads, dropped sponsor row), replaced_by narrowed, date helper inlined.
- Authoring scripts were temporary and have been deleted.

## Task 1 — CLOSED (per-task gates all OK)
- Nurtec ODT via home delivery (shipment 2026-08-26, 90 days); National network; Value plan; Clinical Advanced QL approval 16/30
  effective 2026-09-14; reversed Walgreens auto-refill 2026-09-02; prior sumatriptan lost/stolen 2025-12-02.
- Gold: dose-change override 39 days (step 15) -> member lost/stolen report 9 days (step 17). Skip dose change -> 52.
- Revisions: fill-source ladder reworded + reversed auto-refill seeded (history floor); contract row ids fixed.

## Final difficulty run (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
## CACHE-DIFF INFO, SCOPE OK. check_traceability deferred until the KB is rendered.

## Round 2 rework (audit audits/policy_task/retail_claims_and_reimbursements) — 2026-10-08
- CG-1: dose change / lost-stolen shipping offset now standard_arrival_days = 9 calendar days (policy param), stated as calendar days;
  task 1 gold 39/9 -> 40/10; edge skip 52 -> 54; factor figures re-run (re_dosing_date 29, end share 17, dosing_on_record 40, share 14).
- CG-2/CG-8: review bridge netting made fixed plumbing in a self-sufficient baseline; new method factor bridge_supply_anchor (baseline 22).
- CG-3: paper-claim cost share now includes the deductible portion; >60-day multiple honours retail_90_allowed (declared overwrite of
  retail_claim_cost_share). Task 0 approval unchanged 520.27.
- CG-4: pending-review vacation ceiling = vacation max x 0.67 (rounded down) — never above the base maximum. Task 0 vacation unchanged 16.
- CG-5: urgent bridge tier = emergency_supply_days - 2 (min 1).
- CG-6/CG-7: re_dosing_date and dosing_on_record relabelled parameter; sentences spelled out (no "the same way").
- O-2 quote case; O-3 sentence narrowed to quantity-limit approvals; O-4 offset tier 2 explicit; O-5 docstrings without before/after.
- Task 1 items 4/5: tier_taken grounds and read objectives now name the 2026-09-02 reversal.

## Round 3 rework (audit revision 2) — 2026-10-08
- R2-1: task 1 factor_trace figures 29R/17L corrected to 40/12 (placeholder-prefix slip).
- CG-9: paper-claim deductible = member's own remaining (individual - met); deviation from plan family/preventive logic stated
  and declared as overwrite of retail_claim_cost_share "(after any deductible portion, which the plan's deductible rule sets)".
- CG-10: coinsurance tier cost share honours per-fill min/max and the allowed-less-deductible cap.
- O-7: vacation closing sentence reconciled with the ceiling's rounding down.
- O-8: kept (distinct quantities from one review record); O-9: arrival = program business days + weekend_allowance_days (2), calendar.
- Values unchanged: task 0 520.27/14/16, task 1 40/10.

## Round 4 (validator) — 2026-10-08
- task_tools.py: removed 'from datetime' (forbidden token); the 7-day validity date now comes from a pure-Python _Calendar.plus_days helper
  (class, so no new module-level def). Tool names, signatures, decorators, owners and docstrings byte-identical (AST-checked);
  helper equals datetime arithmetic over 2023-2027. Full gate block + check_traceability OK; validate_scenario: no retail errors.
