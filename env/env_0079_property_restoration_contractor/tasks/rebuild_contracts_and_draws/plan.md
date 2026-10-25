# plan.md — rebuild_contracts_and_draws (env_0079), M=2

## Draws (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=1, factor_counts=[6,6]
- task 1: prerequisite_problems=2, factor_counts=[5,5,5]

## DSL constraint that shaped the design
P('draw_schedule') is a mapping and the compute DSL has no subscript, so a milestone-percentage draw
cannot be computed without restating tier data. Draw-type computations are therefore limited to the
substantial_completion draw (remainder of the current contract sum, base rule) — DSL-KNOWN route.

## Task 0 — final draw after a late code item (Full Structural Rebuild, insurance_claim, carrier_direct)
Surface goal: homeowner (TX), final walkthrough done, asks that the final (substantial completion) draw be
requested so the carrier-funded close-out can proceed.
Tree: root rebuild_ext_final_draw (agent, request_final_draw_*)  <- value_input --
      rebuild_ext_change_order_signature (user, sign_change_order_*): a code-required change order
      (Type X drywall the inspector required) is pending signature at the opening.
Prerequisite sentence (state form, on final draw): the final draw's amount is fixed only after no change
order proposal on the contract stands awaiting the customer's signature (only the signature write brings it about;
no decline/void event exists in this difficulty).
Factors (6) change order: co_markup (param, cross claims O&P, multi-source), co_unit_price (param),
co_quantity (method, sheet/yard/waste conventions), co_preclose (param, cross water/fire/mold, multi-source),
co_lead_safe (param, multi-source), co_plan_review (param).
Factors (6) final draw: fd_retainage (param, cross claims TX statutory 10%), fd_code_hold (param, cross O&L
limit, multi-source), fd_carrier_hold (param, cross depreciation/deductible, multi-source), fd_punch_hold
(param, multi-source), fd_deductive_basis (method), fd_upgrade_deposit (param).

## Task 1 — past-due draw payoff (self-pay residential, customer-funded draws)
Surface goal: crew stopped (work suspended for a past-due draw); customer wants to pay what is owed on it.
Tree: root rebuild_ext_draw_payoff (user, pay_draw_*) <- value_input -- rebuild_ext_overdue_draw_charge (agent)
                                                   <- value_input -- rebuild_ext_deductive_credit (agent)
Factors 5/5/5 (designed in worklog).

## Scope budget
5 extended policies, 5 task tools, task 0 claims {change_order_signature, final_draw}, task 1 claims
{overdue_draw_charge, deductive_credit, draw_payoff}; pairwise disjoint.

## Round 2 revision (audit revision_1)
- Task 0 factors: change order — co_billing_unit (method), co_price_basis (approved supplement / quantity), co_overhead_profit,
  co_wall_treatment, co_drying_verification, co_regulated_materials; final draw — fd_state_retainage (method), fd_code_upgrade_hold,
  fd_depreciation_hold, fd_owner_share_hold, fd_mitigation_first, fd_pass_through.
- Task 1 tree: root rebuild_ext_draw_payoff (user) <- rebuild_ext_overdue_draw_charge (agent) <- rebuild_ext_deductive_signature (user,
  sign_deductive_change_order_5bfd6b95); payoff also <- deductive signature. The credit-posting policy and its tool were removed.
- Details and per-item dispositions: worklog.md, section "REWORK round 2".

## Round 3 revision (audit revision_2)
- Task 0: pending proposal is insurance_scope (carrier price from its approved supplement); final draw holds = Texas retention,
  covered and uncovered code holds, deductible hold, owner-item hold, pass-through (depreciation and mitigation-first holds removed).
- Task 1: deductive credit priced through the insurance_scope change order of the same scope; overdue charge factors = day-weighted
  balance, credit application, owner retention, claim-pending set-off, period anchor; payment factors = overdue carried, credit,
  owner retention, remobilization (base resumption sentence overwritten), claim-pending set-aside. Account agreement removed.
- Details: worklog.md "REWORK round 3".
