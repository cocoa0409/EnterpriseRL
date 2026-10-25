# plan — project_waitlist_reservations (env_0082), M=2 (revision 2)

## Draws (scripts/draw_counts.py --tasks 2, fixed)
- task 0: prerequisite_problems=1, factor_counts=[5, 4]
- task 1: prerequisite_problems=3, factor_counts=[6, 5, 6, 4]

## Binding DSL constraint (recorded decision)
The frozen compute DSL reads only: the target reservation (F/P), its own waitlist_offers / waitlist_notices rows,
the customer's holdings in other categories (EXISTS/CPARAM/CFIELD) and their event tables (X*). It can NOT
read projects (expected_yield_kwh_per_kw, est_credit_rate_per_kwh, commercial_operation_date, unallocated_kw)
or utility_accounts (annual_usage_kwh). No extended computation rests on a project or utility-account figure
and no proxy stands in for one. Route: every extended computation is defined over the reservation, its own
offers, and the household's Residential shares (the share on the same project, the share on the reservation's
utility account, the closed out-of-territory share): their allocation filings, credit statements and annual
true-ups. Offers are scoped (self-naming kWh and savings overwrites with sibling tails) to full offers on a
project where the household already holds a share; every other offer stays under the base rule verbatim.
Account headroom is a scope condition of each request change (never a compute term).

## Task 0 — Relocation Priority (tree: restore -> offer)
- Root (agent): waitlist_ext_relocation_offer_estimate (extend_relocation_offer_f94b15ad) — first-year kWh and
  savings estimate of a full Relocation Priority offer from the household share on the project; 5 factors
  (output_history_basis, guarantee_output_floor, young_share_blend, credit_value_recency, credit_rate_trend).
- Prerequisite (user): waitlist_ext_relocation_restore_size (set_relocation_request_cdb5c762) — request set to
  the output of the share given up converted at the project's yield; 4 factors (prior_output_history,
  prior_output_guarantee_floor, kept_share_of_output, restore_yield_basis). Edge value_input on offered_kw.

## Task 1 — Residential Standard + Residential Add-On on one project (tree: two fits, Standard offer -> add-on offer)
- Root (agent): waitlist_ext_addon_offer_estimate (extend_addon_offer_d026003c), 6 factors (offer family + banked allowance).
- waitlist_ext_standard_offer_estimate (extend_standard_offer_cf280a13), 6 factors; state_gate into the root
  (no Standard reservation on the project that can receive a valid offer left in queued status).
- waitlist_ext_standard_request_fit (fit_standard_request_b636e3b6, user), 5 factors (usage averaging,
  banking margin, existing output, kept share, target yield) -> Standard offer, value_input.
- waitlist_ext_addon_request_fit (fit_addon_request_598035d1, user), 4 factors (usage averaging, banking
  margin, existing output, target yield) -> root, value_input.

## Order
plan.md -> policies -> tools -> seed -> persona -> verify -> GT -> gates per task; final gate block.
Scratch: /tmp/project_waitlist_reservations_0082/
