# protection_contract_claims (warranty) — instantiation worklog

## Step 0 — draws (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=2, factor_counts=[4, 6, 6]
- task 1: prerequisite_problems=1, factor_counts=[5, 6]

## Base pre-check / constraints found
- warranty_claim_payout rows trigger service:service_coverage_credit / install:install_credit for every payout_component,
  so no task tool may write a payout row; claim decisions are written as decision rows only (approved amount),
  the payout posting stays with the invoice back office (out of every tree).
- warranty_transfer subject drags in transfer_window (authority mixed, single-field correlation group) which the
  solvability gate cannot bind; the transfer problem constrains the transfer_carryover limit grant (subject
  warranty_limit_grant), which is exactly the quantity it computes.
- warranty_register subject would demand post_install_window and aftermarket_age_limit at once: no purchase problem.
- base: the original decision is made on the filing date -> an undecided claim is one filed on the date of handling.
- empty FK fields are null (replay FK check treats "" as dangling).

## Policy space (5 policies, pairwise exclusive)
| task | problem | policy | tool | owner | factors |
|---|---|---|---|---|---|
| 0 | root | warranty_ext_cancellation_refund | confirm_protection_cancellation_57f0aac4 | user | 6 |
| 0 | prereq | warranty_ext_labor_plan_claim_decision | decide_labor_plan_claim_66c3e056 | agent | 6 |
| 0 | prereq | warranty_ext_visit_claim_service_fee | charge_claim_service_fee_b62a9756 | agent | 4 |
| 1 | root | warranty_ext_transfer_benefit_carryover | confirm_protection_transfer_64743e30 | user | 5 |
| 1 | prereq | warranty_ext_parts_labor_claim_decision | decide_parts_labor_claim_22401446 | agent | 6 |

Claim decisions split by tier family (labor-only tiers vs parts-and-labor tiers): each family's payout refinements are
its own law; the shared base payout rule is each one's baseline.

Task 0 tree: cancellation <-(value_input: claims deducted) labor-plan decision; cancellation <-(state_gate: fee owed on
every approved visit stands on the contract) fee; fee <-(value_input: approved amount on the visit) decision.
Task 1 tree: transfer carryover <-(value_input: approved-unpaid reserve + claims count) parts-and-labor decision.

## Progress log
- (written as each piece lands)
- task_tools.py: 3 Task-0 tools written; check_task_tools OK
- tasks/0.json: frozen_time + initial_state seeded (ids in _ids0.json, temp)
- tasks/0.json: user_scenario + evaluation_criteria (19 actions) written
- task 0: computations/closure/solvability/tracing written; gates extended/compute/replay/solvability/grounding/scope/task_tools OK (decision 394.69, fee 19.64, refund 89.49)
- extended: parts-and-labor decision + transfer carryover policies appended
- tasks/1.json: seed, persona, evaluation_criteria written
- task 1: seed/persona/eval/computations/closure/solvability/tracing written; per-task gates all OK (decision 3158.28, carried 6787.86)
- temporary authoring scripts and __pycache__ removed; final difficulty-wide gate block run next
- final gate block: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK (check_traceability skipped: KB not yet published)
- round 2 (audit rework) started: items T0-1, T0-2, F-1..F-4, O-1..O-8
- P1 rewritten: label sentence overwrite (F-1/T0-1), lead-claim selection (overwrite of first-claim), member-line-only discounts, maintenance measure aligned (F-4 P1 a,b), complete replaced_by blocks (O-1)
- P2/P3 edited: active-agreement reads, round-1 counts, notice-date full refund, pending contract share, with-installation credit, claims-deducted wording, anchor relabelled parameter, gate sentence 'approved or partially approved'
- P4: premium ladder scoped to covering tiers (F-3), member-line discounts, leak-search sentence moved into refrigerant replaced_by (O-1), active-agreement reads; P5: maintenance measure wording aligned with compute (F-4 P5)
- task 0 reworked (T0-1, T0-2): igniter claim of Saturday's call seeded as approved 2026-02-14 without fee; figures re-run 394.69 / 19.64 / 24.08 (payout 4.44); per-task gates OK
- task 1: figures unchanged after charter fixes; rationale labels corrected (O-T1-a), revision note added
- round 2 observations kept as-is with reasons: O-2 (tool enum must list every schema denial reason or the tool-contract gate fails), O-5 (realism of timing/age/transfer shares: no business rule replaced; P2 repeat-visit share reworded as fee relief for repeated repairs), O-6 (no base eligibility exists for the fee gate; the field locator is the honest gate), O-8 (base cross-problem orders ground no edge in either tree)
- round 2 final gate block: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK (check_traceability skipped)
- round 3 (audit revision_2) started: T0-3, N-1, N-2, request-status latent point, observations N-O1..N-O3, O-T0-r2a
- T0-3: P2 rule names the first approved claim of the call; fee tool docstring neutral; gold step 16 claim_id -> igniter claim. N-1: post-failure maintenance takes the lowest recency share. N-2: pending share moved out of the day-count factor (unused_share_applied). P3 request reads limited to the pending request. Rationale O-T0-r2a explained.
- round 3: N-O1/N-O2/N-O3 kept as observations (disjoint tier families; edge cases latent; post-closing continuity is genuine). Final gate block all OK (check_traceability skipped).
- round 4 (audit revision_3) started: N-1′
- round 4: N-1′ closed — P1 maintenance recency now reads the latest record completed on or before the failure (per-season Comfort Club tune-ups + precision tune-up line, each counting only if dated on or before the failure); task values unchanged; final gate block all OK (check_traceability skipped)
