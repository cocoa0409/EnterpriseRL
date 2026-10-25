# plan — store_card_billing_and_disputes (env_0080), M=2

Draws (draw_counts.py --tasks 2):
- task 0: prerequisite_problems=2, factor_counts=[4,5,5]
- task 1: prerequisite_problems=1, factor_counts=[6,4]

Inventory reasoning (worklog has detail): only five card writes carry rich, record-decidable computations:
credit line increase (agent, on request), cardholder catch-up payment (user, ruling c/b),
final credit of a confirmed duplicate-posting dispute (agent, owed), credit-balance refund (user, ruling a),
automatic first-late-fee courtesy reversal (agent, owed). Fee caps/re-bills/dispute openings are single-number
reads or cannot be located by the DSL without literals, so they are not claimed.

Task 0 (3 problems) — root: card_ext_line_increase (agent, card_change_limit, credit_limit_usd, 5 factors)
  <- card_ext_catch_up_payment (user, card_post_payment, amount_usd, 4 factors)   [value_input: balance/utilization]
  <- card_ext_duplicate_final_credit (agent, card_dispute_credit final + card_resolve_dispute, amount_usd, 5 factors) [value_input]
  Persona: card declined at register, asks for a higher limit. Store Card, GA.
Task 1 (2 problems) — root: card_ext_credit_balance_refund (user, card_refund_credit_balance, amount_usd, 4 factors)
  <- card_ext_first_late_fee_courtesy (agent, card_reverse_fee courtesy_waiver, amount_usd, 6 factors) [value_input]
  Persona: overpaid, wants credit balance sent back. FL.

Cross-difficulty reads: membership holding (tier/status) and order holding (duplicate confirmation / spend).
Trigger rule: every card event has triggers: [] in base -> no task tool write lands in another category.
Scratch: /tmp/store_card_billing_and_disputes_0080/

## Revision 1 (before any asset): final allocation
Task 0 [4,5,5] root card_ext_credit_balance_refund (user, 5) <- card_ext_duplicate_final_credit (agent, 4) & <- card_ext_first_late_fee_courtesy (agent, 5)
Task 1 [6,4] root card_ext_line_increase (agent, 6) <- card_ext_catch_up_payment (user, 4)

## Revision 2 (supersedes rev 1) — reason: a Store Card world cannot exercise >2 real refund holds
(provisional credits and outside rewards exist only on Mastercard tiers), while the final credit needs a
closed-loop tier (no provisional credit). So the refund moves to a World Mastercard world (task 1) and the
final credit stays with the Store Card FCBA world (task 0).
Task 0 [4,5,5] (Store Card, GA, Gwendolyn Easterly): root card_ext_line_increase (agent, 5)
   <- card_ext_catch_up_payment (user, 5)  <- card_ext_duplicate_final_credit (agent, 4)   [chain or fan-out, decided at design]
Task 1 [6,4] (World Mastercard, FL, Felicia Hargrove): root card_ext_credit_balance_refund (user, 4)
   <- card_ext_first_late_fee_courtesy (agent, 6)
