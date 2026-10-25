# plan — marketplace_orders_and_guarantee (category market), M=2

Draws (draw_counts.py --tasks 2):
- task 0: prerequisite_problems 3, factor_counts [6, 6, 5, 4]
- task 1: prerequisite_problems 2, factor_counts [5, 5, 4]

Hard constraints taken from the brief / XF_recipe / owner_ruling:
- Trigger rule: market_seller_refund and market_guarantee_reimburse trigger card:card_post_credit when
  payment_method_type = northgate_card -> every order whose refunds/reimbursements my tools write is paid with
  external_card, and the tools write payment_method_type external_card only (body-enforced: the order must be an
  external-card order). market_decide_claim triggers market:market_guarantee_reimburse (same category, allowed).
- owner=user writes = guarantee claim filing (owner ruling (a)). Third-party claims filed in-call cannot be
  decided in-call (seller gets 3 business days) -> in task 0 the user claim is the ROOT. Fulfilled by Northgate
  claims have no seller response period -> in task 1 the user claim feeds a same-call grant + reimbursement.
- Cross-difficulty evidence: gift charter account-wide rule gift_promo_expiry_and_clawback ("value already spent
  is deducted from the return's refund") — a Northgate Promotional Gift Card earned by the marketplace order
  (gift_load_value initial_load, source_record_id = the marketplace order) and already spent (gift_redeem rows).
  Promo cards seeded fully spent (depleted) so no gift-side void is owed at the opening (owed-write check).
- No datetime/random/uuid imports in task_tools.py; half-up via Decimal in a class static method; frozen_time
  'YYYY-MM-DD HH:MM:SS TZ'.

## Task 0 — Freight Seller order, buyer files a claim on the remaining dining chairs (root = user claim)
Problems (policy -> tool, owner, factors):
- P_claim  market_ext_item_claim_amount -> file_item_guarantee_claim_<u> (USER) 6 factors  [ROOT]
- P_unit   market_ext_authorized_unit_refund -> refund_authorized_units_<u> (agent) 5 factors
- P_reimb  market_ext_due_claim_reimbursement -> grant_due_guarantee_claim_<u> (agent) 6 factors
- P_ship   market_ext_seller_fault_shipping_refund -> refund_seller_fault_shipping_<u> (agent) 4 factors
Edges: P_claim <- P_unit (value: units still unrefunded on the claimed line);
       P_claim <- P_reimb (value: room left under the per-order maximum — pending claims reserve their claimed
                           amount, decided claims count what was reimbursed);
       P_reimb <- P_ship (value: shipping not yet refunded, spread over merchandise not yet refunded);
       P_reimb <- P_unit (value: merchandise not yet refunded).
Order: P_unit, P_ship (commute) -> P_reimb -> P_claim.

## Task 1 — Fulfilled by Northgate order, box arrived short; store drop-off refund owed
- Q_claim  market_ext_missing_unit_claim_amount -> file_missing_item_claim_<u> (USER) 5 factors
- Q_reimb  market_ext_missing_unit_reimbursement -> grant_missing_item_claim_<u> (agent) 5 factors [ROOT]
- Q_drop   market_ext_store_dropoff_refund -> refund_store_dropoff_<u> (agent) 4 factors
Edges: Q_reimb <- Q_claim (value: amount claimed); Q_reimb <- Q_drop (value or state, decided at design).

Scratch: /tmp/marketplace_orders_and_guarantee_0080/ (verification scripts). Worklog: worklog.md.
