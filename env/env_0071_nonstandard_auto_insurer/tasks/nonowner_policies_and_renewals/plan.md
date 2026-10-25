# plan — nonowner_policies_and_renewals (env_0071), M=2

## Draws (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=1 (2 problems), factor_counts [5, 4]  -> >=1 value_input edge
- task 1: prerequisite_problems=3 (4 problems), factor_counts [6, 6, 4, 5] -> >=2 value_input edges
- 6 extended policies in all; every task needs one owner=user problem with a NUMERIC computed arg.

## Hard constraints carried (coordinator + XF recipe)
- write only tasks/nonowner_policies_and_renewals/; scratch /tmp/nonowner_policies_and_renewals_0071/
- frozen_time 'YYYY-MM-DD HH:MM:SS EDT'; task_tools.py: no datetime/time/random/uuid imports,
  date maths via class static ordinal helper; every write tool calls ctx.create/update itself
- no factor id substring of any tool name; no example values in docstrings
- identifier band k=5: phones <state area>5555###, DL last4 5xxx, surnames S-Z, policy 7-digit part 5..., BP-5..., PMT-5..., CLM-5..., VIN serial 5..., acct last4 5..., case numbers 5...
- tools write only nonowner tables; events written: nonowner_cancelled_insured_request (+ its trigger
  nonowner_return_premium), nonowner_limits_changed (triggers []), nonowner_additional_premium (triggers []),
  nonowner_return_premium (triggers []) ... all inside nonowner.

## Only numeric-capable user acts in the nonowner charter
- U1 nonowner_cancelled_insured_request (lifecycle in_force->cancelled by: user) with its triggered return premium amount
- U2 nonowner_limits_changed (insured's own package election, re-rated full_term_premium)
  (statement signings carry no numeric field)

## Design (draft; refined in worklog.md)
- task 0 (2 problems): U1 root (insured-request cancellation return, 5 factors) <- agent prerequisite booking an
  owed premium entry on the same term (4 factors, value_input into the return's ledger sum).
- task 1 (4 problems): FR-44 / package story around U2: user package change (re-rated premium) -> agent
  limits-increase additional premium (value_input) ; plus renewal-offer issuance owed on the same policy
  (renewal premium from the expiring term's re-rated premium: value_input) ; 4th problem TBD in worklog.

## Order of work
1 extended.yaml base copy + task-0 policies -> check_extended
2 task_tools.py task-0 tools -> check_task_tools
3 task 0 seed/persona/verification/GT -> per-task gates
4 task 1 same; final gates; worklog line.

## Final (as built)
- task 0 (TX): nonowner_ext_insured_cancel_return (root, user) <- nonowner_ext_late_renewal_written
- task 1 (FL): nonowner_ext_renewal_offer_premium (root) <- nonowner_ext_package_rerate (user), nonowner_ext_package_increase_premium
  <- nonowner_ext_reinstatement_rewritten ; details and verification in worklog.md
