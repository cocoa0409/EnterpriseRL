# plan — business_allocation_changes_and_trueups (category biz), M=2

Draws (draw_counts.py --tasks 2):
- task 0: prerequisite_problems=1, factor_counts=[6, 5]
- task 1: prerequisite_problems=1, factor_counts=[6, 6]

DSL constraint found at Step 0: compute can read only the biz holding, its own event/intake rows, variant params,
and other categories' holdings/events. projects.* (expected_yield_kwh_per_kw, unallocated_kw, program) and
utility_accounts.* (annual_usage_kwh) are NOT readable. So increase sizing / annual resize cannot be machine
recomputed; computations are put on writes priced from biz ledger rows (filings, credits, billing, reviews,
requests) and garden/waitlist rows of the same customer.

Policies (each = one problem, one tool):
- P_TRUEUP (agent): complete the annual true-up of an ended contract year on a production-guarantee plan;
  computes guarantee_credit (review row + production_guarantee billing credit). Guaranteed kWh carried from the
  previous review (scoped: years after the first with unchanged allocation; self-naming overwrite).
- P_DECFEE (user): the business accepts the decrease amendment for its pending decrease request; acceptance bills the
  excess-decrease fee; computes the fee. The usage-decline allowance reads the latest true-up -> value_input edge from
  P_TRUEUP (state form: fee fixed only after a completed true-up for every ended contract year).
- P_ESTIMATE (agent): bill the estimated charge for a statement month the utility has not reported after the
  estimate waiting period; computes estimated_charge.
- P_DEPOSIT (user): the business pays the security deposit its pending increase needs (secure portal, ACH/check);
  computes deposit_amount; waits (state form, negated direction) on a charge for every month past its waiting period.

Task 0: P_TRUEUP (5 factors, prerequisite) -> P_DECFEE (6 factors, root, owner=user).
Task 1: P_ESTIMATE (6 factors, prerequisite) -> P_DEPOSIT (6 factors, root, owner=user).

Scratch: /tmp/business_allocation_changes_and_trueups_0082/
Identifier band: phones 6515550120-6515550139; surnames Castellanos, Oyelaran, Lindqvist, Pemberton, Takahara,
Rourke; businesses Ironwood Machining Inc., Cedar Hollow Veterinary Clinic, Northstar Print & Sign LLC,
Bluffside Brewing Co.; prefix 22; house numbers 2200-2299.
