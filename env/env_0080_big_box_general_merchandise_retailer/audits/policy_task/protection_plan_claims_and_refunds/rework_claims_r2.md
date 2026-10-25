# Rework claims — protection_plan_claims_and_refunds, round 2

| item | status | location changed |
| --- | --- | --- |
| C1 | closed | rule + compute_basis.result of all six extended policies (generic order sentence; each factor sentence states its own action) |
| C2 | closed | plan_ext_accident_claim_service_fee compute/factors (incident and filing dates plain); class sweep across all policies |
| C3 | closed | factors replacement_price_basis, delivery_charge_share (now parameter), starting_fee_method, repair_charge_method, spoilage_cause_allowance, coverage_count_start; tasks/0.json initial_state plan recorded price |
| C4 | closed | tie sentences in plan_ext_accident_claim_service_fee, plan_ext_repair_authorization_value, plan_ext_food_loss_payment; long_term_credit by coverage days; 12-month window wording (service fee, food loss) |
| C5 | closed | plan_ext_standard_cancellation_refund warranty_month_share (warranty at or above term_months; term_months denominator) |
| C6 | closed | plan_ext_accident_cancellation_refund unused_days cap at the coverage days counted |
| C7 | closed | both cancellation policies: refund held to no more than the price kept (rule, baseline, compute) |
| C8 | closed | plan_ext_repair_authorization_value replacement branch; authorize_claim_repair_5d8df043 settlement_method argument and fulfilment; edge sentences "repair or replacement settlement" |
| C9 | closed | task_tools.py: positive guards (register, repair, food loss); cancel tools refund only external-card charges and confirm the waiting request |
| C10 | closed | plan_ext_accident_cancellation_refund: denial credit removed, claim_administration_charge added |
| C11 | closed | plan_ext_limit_of_liability_registration accessory definition (general-merchandise class) and delivery_charge_share; tasks/0.json order line |
| T0-1 | closed | tasks/0.json initial_state (approved, unsettled battery claim; new open claim); prerequisite edges of the repair, decision and refund policies; prerequisite_closure |
| T0-2 | closed | tasks/0.json initial_state.plan_holdings covered_item_price_usd (net price paid) |
| T0-3 | closed | tasks/0.json initial_state.plan_requests (withdrawn request near-miss) |
| T1-2 | closed | tasks/1.json initial_state.plan_requests (withdrawn and waiting requests) |
| T1-3 | closed | plan_ext_standard_cancellation_refund: delivery-gap credit removed, request_waiting_addition added; tasks/1.json |
| O1 | disputed (base frozen) | none — base definitional text cannot be edited; extended rules scoped and explicit |
| O2, O4, O8, O9, O12, O15 | closed | tool docstrings; food-loss installation allowance; failure-claim types; repair baseline remaining share; fee wording |
| O3, O10, O11, O13, O14 | noted | no change (observations; worklog.md round-2 closure record) |
