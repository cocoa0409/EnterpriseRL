# plan.md — garden_cancellations_and_termination_fees (env_0082), M=2

## Draw (scripts/draw_counts.py --tasks 2)
- task 0: prerequisite_problems=3 (4 problems), factor_counts=[4, 6, 6, 5]
- task 1: prerequisite_problems=3 (4 problems), factor_counts=[4, 5, 6, 5]
=> 8 extended policies, each tree needs >= 2 value_input edges and >= 1 owner=user tool.

## Inputs read
- coordinator inst_common.md, XF_recipe.md, realism_bar.md, owner_ruling.md (all in force)
- blueprint.yaml, products/garden.yaml (base), db_schema.json, share_tools.py (verify K=2)
- claimed events: garden_notice_given, garden_notice_withdrawn, garden_closed, garden_preactivation_cancelled,
  garden_etf_assessed, garden_allocation_reduced, garden_successor_assigned, garden_transfer_lapsed, garden_charge_billed
- numeric write fields available: garden_billing.amount (charge, ETF), garden_allocations.kw (reduction lines)
- identifier band: phones 6515550180-6515550199; surnames Kellerman, Obi-Laurent, Haugland, Petrakis, Whitcombe,
  Yamashiro; businesses Stonegate Hardware Inc., Larkfield Floral Studio, Elm Creek Family Chiropractic; prefix 25;
  house numbers 5500-5599

## Status log (append)
- step 0: plan written; design in progress (see worklog.md)
- task 0 closed, per-task gates 7/7 green (traceability deferred); next: task 1 residential siblings

## Design decision (step 0, after exhausting in-claim options) — DECISION D1
- Numeric write fields of claimed events: garden_billing.amount (charge, ETF) and garden_allocations.kw. Every
  removal line on a closing (cancellation/move/successor/preactivation) must equal allocation_kw (schema invariant:
  allocation_kw = filed - reduced, 0.00 after removal) -> no closing/removal can carry a factor-bearing computation.
- No claimed owner=user garden event carries a computed amount next to an ETF (notice/withdrawal: dates only;
  successor/preactivation: removal kW = allocation_kw). Owner ruling (b) admits a holder-completed payment.
- Route: closings already recorded by the system at the opening (closing and its removal line seeded); the tree
  books the owed money lines and ends in the subscriber's own settlement payment:
    root  = settlement payment (owner=user, garden_payment_received; ruling (b); event claimed by no difficulty)
    prereq= ETF (garden_etf_assessed), trailing-credit charge (garden_charge_billed), late fee
            (garden_late_fee_assessed; claimed by no difficulty) — all value_input into the payment.
- task 0: residential Garden Fixed 20, subscriber cancellation closed on its scheduled end date.
  draw [4,6,6,5] -> payment 4, ETF 6, trailing charge 6, late fee 5.
- task 1: small-business Garden Business Fixed 15, move transfer lapsed (transfer_not_completed).
  draw [4,5,6,5] -> payment 4, ETF 6, trailing charge 5, late fee 5.
- sibling policies (same line, other closure scope) mirror; trailing-charge pair differs by one scope-specific
  factor (documented).
- cross-difficulty factor: ETF conversion clause (kW moved to another Meadowlark line on the same utility account;
  precedent home_cancellation converted_to_access) reading home (t0) / biz (t1).
- task 0 closed (per-task gates green); task 1 in progress (residential siblings)
- task 1 closed; final gate block 7/7 green; ROUND 1 line appended to worklog
- rework round 2 done; full gate block green; settlement factor floor flagged for coordinator ruling
