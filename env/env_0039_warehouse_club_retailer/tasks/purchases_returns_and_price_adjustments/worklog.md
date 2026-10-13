# purchases_returns_and_price_adjustments — instantiate worklog (M=2)

## Step 0 draws (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=1, factor_counts=[4, 5]
- task 1: prerequisite_problems=2, factor_counts=[5, 6, 5]

## Difficulty-level pre-check
- Base order charter: the only member-owned (owner=user) write the base names is the member's confirmation of a
  return authorization; the only priced member actions on it are the Special Order changed-mind charges
  (return_pickup_fee, restocking_fee). Every other channel has changed_mind_pickup_fee_usd 0 and restocking 0.
- The compute DSL cannot read item_price_history (not an order binding table), so price adjustments and mail-in
  rebates cannot be scored computations; refunds/fees on order_lines + order_return_authorizations can.
- Writes must keep reward_eligible=false lines only (order_line_returned / order_price_adjusted trigger
  membership_reward_reversed when reward_eligible=true) -> every purchase used is bought without a Plus tier
  presented on the order date.
- Plan (claimed task by task):
  - task 0 (business member, Special Order): root = member confirms the changed-mind freight return and accepts
    the business restocking charge (user) <- member services invoices the route pickup fee (agent).
  - task 1 (consumer member, Special Order): root = member confirms the changed-mind freight pickup and pays the
    member pickup fee (user) <- restocking fee on an earlier received piece (agent) <- refund of that piece (agent).
- Tool names (uuid8 drawn once each): invoice_route_pickup_fee_16b23a12, confirm_business_return_92c81b09,
  post_changed_mind_refund_b29df74c, charge_restocking_fee_79f2f340, confirm_freight_pickup_4c90eb99.

## Log
- task 0 closed: policies order_ext_business_route_pickup_fee (4 factors, agent) -> order_ext_business_restocking_charge
  (5 factors, user, root). Gold: route_pickup_fee 123.75 (baseline 109.00), restocking_fee 92.25 (baseline 269.99);
  skipping the invoice -> 216.00. Fixes during gating: helper function in task_tools.py counted as an unnamed task
  tool (inlined); empty item_price_id on sale rows flagged as dangling FK (field omitted on sale rows).
  Per-task gates on --task 0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK,
  GROUNDING OK, CACHE-DIFF INFO, SCOPE OK.
- task 1 closed: order_ext_member_pickup_fee (6 factors, user, root) -[state_gate]-> order_ext_settlement_restocking_fee
  (5 factors, agent) -[value_input]-> order_ext_changed_mind_refund (5 factors, agent). Gold: refund 418.12 (baseline
  449.99), restocking 23.00 (baseline 62.72; 0.00 if the refund is skipped), pickup 72.80 (baseline 79.00).
  Per-task gates on --task 1: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  SCOPE OK.
- Final difficulty run (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK
  (branches mean 36.00, steps mean 15.00, history_rows_max 19, branches_max 44), GROUNDING OK, CACHE-DIFF INFO,
  SCOPE OK. check_traceability: NOT OK only because the published KB (docs/) does not exist yet - the hidden tool
  names reach the agent through the rendered policy documents; re-run after erl-kb-doc-render.
- Temporary authoring scripts (_author/) deleted after the final run.
