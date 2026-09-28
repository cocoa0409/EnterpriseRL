# condo_coverage_changes — difficulty worklog (erl-task-instantiate)

## Step 0 — difficulty pre-check
- Base read: products/condo.yaml (policies condo_endorsements, condo_association_changes, condo_cancellation_and_reinstatement,
  condo_claim_settlement, condo_loss_assessment, ...), db_schema condo_* tables, share_tools finders + verify (K=2).
- Draw (`draw_counts.py --tasks 2`):
  - task 0: prerequisite_problems=1, factor_counts=[5, 4]
  - task 1: prerequisite_problems=1, factor_counts=[5, 4]
- Gate facts that shaped the design:
  - `no_backdated_change` (condo_endorsements) is a `mixed` gate with a single-field correlation group, which a structured
    binding cannot satisfy; every endorsement policy therefore declares, sentence by sentence, the override that pins the
    effective date to the day the named insured requests it (a stricter, single-valued refinement of base's "no earlier
    than"), which retires that gate by overwrite.
  - compute is holding-scoped, so every problem is a policy-level endorsement premium (no claim-number-scoped quantity).
- Space budget (4 policies, 4 tools, 2 per task):
  - task 0: root = unit rental endorsement charge (owner=user), prereq = personal liability raise charge (owner=agent);
    edge value_input (rental charge carries a landlord liability load read from the declared liability limit).
  - task 1: root = deductible raise credit (owner=user), prereq = Coverage A realignment charge after an association
    change (owner=agent); edge value_input (the credit acts on the annual premium in force, which carries the Coverage A
    endorsement's annual change).
- Owner doctrine: voluntary coverage elections (renting the unit out, electing a higher deductible) are the named
  insured's signed election, run by the customer; the service/compliance endorsements the desk books (liability raise
  required for a rented unit, Coverage A realignment required by the master-policy change) are agent actions.

## Tools (uuid8 generated once each with uuid.uuid4().hex[:8])
- raise_liability_limit_70984c5d (agent) — condo_ext_liability_raise_charge
- add_unit_rental_endorsement_60a857ee (user) — condo_ext_unit_rental_charge
- raise_coverage_a_minimum_ec3d8a44 (agent) — condo_ext_coverage_a_realignment_charge
- elect_deductible_raise_c9f31846 (user) — condo_ext_deductible_raise_credit

## Progress log
- [task 0] design fixed; writing extended policies, tools, seed.
- [task 0] closed. Root condo_ext_unit_rental_charge (user, 5 factors) <- condo_ext_liability_raise_charge (agent, 4 factors),
  value_input edge on landlord_liability_load. Gold: liability 5.95 (annual 11.90), rental 47.84 (annual 95.68);
  baselines 7.79 / 50.05; without the liability raise the rental figure is 40.40. All --task 0 gates OK.
- [task 1] closed. Root condo_ext_deductible_raise_credit (user, 5 factors) <- condo_ext_coverage_a_realignment_charge
  (agent, 4 factors), value_input edge on annual_in_force. Gold: realignment 135.61 (annual 232.48), deductible credit
  42.65 (annual 63.98); baselines 150.36 / 101.55; without the realignment the credit is 36.79. Revision: month-count
  share reworded to "plus one for the month of the raise, never more than twelve" (MN cap) to match compute exactly.
- [final] full-suite gates (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK
  (suite means branches 33 / steps 11, history_rows_max 16, branches_max 33), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK.
  check_traceability deferred until the KB is published. Coverage: 4 policies / 4 tools, disjoint across tasks 0 and 1.
- [rework round 2 — audits/policy_task/condo_coverage_changes round 1]
  - F0-1 (task 0, SOURCE-FACTOR RED, rounding ties): every rounding binding of all four policies now computes exact
    half-up, int(round(x*100, 6) + 0.5)/100, and each rule states "... half-up in exact decimal: a figure lying exactly
    halfway between two cents goes to the higher cent" (quoted in the result basis). rental_loss_history 38.27 -> 38.28,
    rental_payment_history 45.56 -> 45.57; every gold figure and all other proof figures unchanged (re-run).
  - F1-1 (task 1, SOURCE-FACTOR RED, flood row vs flood charter): FG-3371-6045 reconciled with products/flood.yaml
    (building 150000 >= Standard min 100000, contents 40000, RC 180000, term premium 485.79 from flood_premium_rating
    with the 5% companion discount). Factor reads unchanged; figures unchanged.
  - Observations: O-3 docstrings "Afterwards" -> "On success"; home row Coverage C 206000 -> 289000 (70% rounded up);
    O-T1-a multi-source labels removed from flood_companion / deductible_reraise traces; O-1, O-2, O-4, O-5, O-6
    answered in the task dossiers (no demonstrable consequence; kept by design).
  - Full gate block re-run green (per task and full suite).
