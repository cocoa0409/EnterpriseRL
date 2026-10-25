# plan — membership_fees_and_benefits (env_0080), M=2

Draw (draw_counts.py --tasks 2):
- task 0: prerequisite_problems=2 (3 problems), factor_counts [5,4,4]
- task 1: prerequisite_problems=3 (4 problems), factor_counts [6,5,6,6]

Constraints carried: XF_recipe.md (30 points), owner_ruling.md (user tool = member's own cancel/resume/trial-cancel
decision recorded+confirmed with grouped same-category consequence, or holder-completed secure payment with no
payment method on file, or own payment). Identifier band: surnames A-D, IL/WI, phones 312555 01xx / 608555 01xx,
DOB 1958-1965, minted customer-facing refs start with 1.
Trigger rule: membership_fee_charge / membership_fee_refund with payment_method_type=northgate_card trigger card
events -> my tools only ever write external_card on fee rows (or fee rows whose method is external_card).
membership_fee_decline attempt 0 -> place_payment_hold (same category, fine).

Status: both tasks written; final gate block 7/7 green (see worklog.md).
