# plan — income_eligible_move_transfers (category access), M=2

Draw (draw_counts.py --tasks 2):
- task 0: prerequisite_problems 3 (4 problems), factor_counts [6, 6, 6, 6]
- task 1: prerequisite_problems 2 (3 problems), factor_counts [6, 4, 6]

Status: round 1 delivered (both tasks written, full gate block green). Design notes and revisions in worklog.md.

Claimed scope (final, worklog REVISION 5):
- task 0: access_ext_move_reassignment_sizing (root) <- access_ext_move_settlement_payment (owner=user) <- access_ext_move_pending_estimate, access_ext_move_partial_reversal_credit
- task 1: access_ext_move_closing_payment (root, owner=user) <- access_ext_move_closing_estimate, access_ext_move_closed_reversal_credit

Binding inputs read: /tmp/erl0082_coord/inst_common.md, audits/render_source/{XF_recipe.md, realism_bar.md, owner_ruling.md},
blueprint.yaml, products/access.yaml (+ waitlist/home schemas), db_schema.json, share_tools.py, skill references.

Key frozen limits found at step 0 (recorded as BLUEPRINT-KNOWN in worklog):
- compute DSL reads only this holding, its own event/intake tables, and other categories' holdings/event tables;
  utility_accounts and projects (usage, yield, program, utility, designation) are unreadable by compute -> they can
  only act as agent-checked record tests / prerequisites, never as factor evidence.
- the account-wide access_benefit_basis rule forbids any other line / promotion from changing a charge's price ->
  cross-difficulty factors sit on kW quantities, never on a subscription charge's rate.
- the only by:user transition in the claimed events is access_transfer_requested (no numeric field) -> customer-own
  computed writes are holder-completed payments through the secure payment flow (owner_ruling (b), base
  access_evt_payment_application).

Order of work: task 0 policies -> tools -> seed -> persona -> verify script -> GT -> gates; then task 1; then final gates.
