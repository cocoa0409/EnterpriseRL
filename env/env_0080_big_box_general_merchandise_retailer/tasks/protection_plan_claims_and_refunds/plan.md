# plan — protection_plan_claims_and_refunds (env_0080), M=2

Draws (draw_counts.py --tasks 2):
- task 0: prerequisite_problems=3 (4 problems), factor_counts [6, 6, 4, 5]; >= 2 value_input edges; >= 1 owner=user
- task 1: prerequisite_problems=1 (2 problems), factor_counts [6, 5]; >= 1 value_input edge; >= 1 owner=user

Identifier band: surnames I–L, TX/OK real ZIPs, phones 214555 01xx / 405555 01xx, DOB 1974–1981,
customer-facing refs start with digit 3.

Trigger constraints (base `triggers` of events my tools may write):
- plan_charge / plan_refund with payment_method_type northgate_card -> card (FORBIDDEN): tools fix external_card.
- plan_settle_claim with settlement_method reimbursement_egift_card -> gift (FORBIDDEN): tools never write it.
- plan_register_item / plan_file_claim / plan_decide_claim / plan_cancel / plan_fulfil: no triggers.

Status: both tasks closed; final 7-gate block green (see worklog.md).
