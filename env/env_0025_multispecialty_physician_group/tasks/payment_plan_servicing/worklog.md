# worklog — payment_plan_servicing (erl-task-instantiate, round 1, M=2)

- 2026-09-24 resumed after cut-off: directory was empty. Base copied verbatim into payplan.extended.yaml.
- draw_counts --tasks 2:
  - task 0: prerequisite_problems=2, factor_counts=[5, 5, 4]
  - task 1: prerequisite_problems=3, factor_counts=[5, 5, 4, 5]
- Gates read: check_extended, check_compute, check_solvability, check_task_tools, replay_tasks, check_grounding, check_cross_fire, prereq_utils.

## Difficulty design (Step 0, fixed before writing)
Constraints found in the charter that shape the design:
- payplan_installment_paid and payplan_extra_payment both trigger billing:billing_payment_posted with no `when`
  -> no task tool may write a payment row; every tree avoids payments (down payment must be 0 where a signing happens).
- Counselor-reviewed tiers (18/24-Month, Hardship) cannot be proposed synchronously -> a signing task uses a proposal
  that already exists in the seed (prepared by the counselor before the call).
- Patient's own acts: signing the agreement (base) and accepting a new payment obligation ("accepting a payment
  obligation is the patient's own act and is never done for them", payplan_agreement_and_activation) -> the add-on
  task hands the acceptance of the re-spread installment to the patient.
Tool names (uuid8 generated one per tool):
- sign_installment_agreement_b4bb7ade (user)   task 0 root
- enroll_setup_fee_08ffaf93 (agent)            task 0
- enroll_encounter_charge_372696d1 (agent)     task 0
- accept_add_on_installment_27cdd630 (user)    task 1 root
- enroll_add_on_charge_102110ed (agent)        task 1
- extend_plan_term_6d1d2771 (agent)            task 1
- enroll_add_on_fee_792da8e6 (agent)           task 1
Headroom plan: task 0 = 24-Month Extended Plan signing (root + setup fee + late-posted encounter charge; draw 5/5/4 ->
setup fee 5, encounter charge 5, signing installment 4). Task 1 = 18-Month Extended Plan add-on (root + add-on charge +
add-on fee + term extension; draw 5/5/4/5 -> accept 4, the three prerequisites 5 each). Scopes disjoint by construction.
- Task 0 policies written (signing_setup_fee, encounter_charge_enrollment, signing_installment).
- Task 0 written and per-task gates green (extended/tools/replay/solvability/compute/grounding/scope).
- Task 1 design fixed: 18-Month Extended Plan (active, HDHP account) add-on. Problems: add-on charge amount (5 factors),
  add-on term extension (5), add-on fee (5), root = patient's acceptance of the re-spread installment (4).
  Edges: root <- charge (value), root <- fee (value), root <- extension (value); extension <- charge (value); fee <- charge (value).
  Prerequisite problems = 3 (draw), value_input edges = 5 (>= 2).
- Task 1 policies written (add_on_charge_amount, add_on_term_extension, add_on_fee, add_on_installment).
- Task 1 written; per-task gates green. Revision: add-on standing tiers require >= standing_min_paid paid installments (history load-bearing).
- Final difficulty-wide gates (no --task): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 37/37, 1.json 33/33);
  SOLVABILITY OK; COMPUTE OK (branches mean 65.00, steps mean 13.00, history_rows_max 28, branches_max 67);
  GROUNDING OK; CACHE-DIFF INFO (diagnostic only); SCOPE OK. Traceability deferred until the KB is published.
- Temporary authoring scripts (scratchpad) and __pycache__ removed.

## Round 2 rework (audits/policy_task/payment_plan_servicing r1)
Items: T1-R1 (RED), T1-O1, T1-O2, T0-O1, T0-O2, O-1..O-11.
Plan: task 1's root becomes what the customer raises (lower monthly installment, patient's acceptance); the add-on
becomes a state-due obligation (a later-posted charge of an encounter already on the active plan), discovered from the
root's prerequisite sentence; extension/fee become state_due follow-ons of the add-on. Charter wording fixes for O-1,
O-2, O-3, O-4 (B), O-8, O-9, O-10; T0-O1 persona examples removed.
Changes made (round 2), by audit item:
- T1-R1 (RED): task 1 re-rooted on the customer's actual ask (lower monthly payment -> patient's acceptance of a
  re-spread installment). Add-on charge policy now state_due ("an active plan carries every eligible charge of the
  encounters enrolled on it"; selector = most recent charge of the encounter the plan enrolled at its proposal); world
  gained the knee encounter's later-posted charge (960.00, 2026-10-10); heart-test charge kept open as selector near-miss.
  Extension and add-on fee -> state_due. Re-spread basis tier 2 changed to a split spread (pre-add-on balance over the
  installments left + add-on and fee over the tier's term_months). Root prerequisite sentences reworded to the new states.
  New gold: add-on 777.50, extension 5, fee 5.00, installment 167.11 (down from 186.39). Persona rewritten; no
  prerequisite named.
- T1-O1: the $2,230 figure left with the old persona.
- T1-O2 / O-2: signing setup-fee rule now "at most one signing setup-fee entry ...; any add-on fee an active plan carries
  later is a separate entry" (rule + overwrite replaced_by).
- T0-O1: task 0 persona conditional line no longer names example prerequisites.
- T0-O2 / O-4: encounter-charge result rounds half up (RND(x + 0.000001, 2)); rule says an exact half cent goes up;
  sensitivities 833.63 / 463.13; gold unchanged.
- O-1: encounter-charge and add-on rules label the flat case "standard" (rule + baseline).
- O-3: add-on selector filtered by encounter; encounter-charge selector kept (LATEST-based filter would leave no
  SUM/COUNT for the history floor); rule and selector agree on task 0's world.
- O-5: no change (down payment 0.00 on the only signing world; base obligation kept verbatim).
- O-6: no change (governs the billing-side adjustment; enrolled-amount sentence is declared overwritten).
- O-7: no change (commute proved: size share 0.90 either order, same terminal).
- O-8: encounter-charge rule no longer limited to charges posted after the proposal date.
- O-9: setup-fee, add-on-fee, add-on and acceptance docstrings reworded; no other problem's occasion named.
- O-10: extension rule excludes the Financial Hardship Plan ("an add-on restarts the term instead and earns no
  extension"), compute branch hardship_tier -> 0.
- O-11: no change (ladder notes; neither world sits on a zero-discount class; labels within bounds).
- Final gate block re-run (round 2): all green; scratch scripts removed.
