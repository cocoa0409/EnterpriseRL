# prepaid_maintenance_plans — worklog (env_0075, band 3, M=2)

## Round 1
- Read XF_recipe.md, blueprint (maintenance charter, schema, share tools, cross charters as needed), references.
- Draw: task 0 = 3 prerequisites, factors [4,6,6,5]; task 1 = 1 prerequisite, factors [4,4].
- Domain finding: only sale price, cancellation refund and the (re-based) fleet transfer odometer carry a
  policy-variable number; redemption / reinstatement / expiry / refund payment are not used as problems.
  User tools are the plan contracts the customer signs (fleet addendum, retail contract).
- DSL finding (check_extended): no reads of the primary category's other holdings; COUNT/SUM/LATEST are
  scoped to the computation's own plan. Value_input edges therefore chain on one plan (task 0: plan
  KC-329804 moved -> total-loss cancelled -> proxy of the addendum price; fleet cancel of KC-360347 as a
  state_gate). Recorded in plan.md.
- Policies (6): fleet_addendum_price (6 f), fleet_cancel_refund (6), fleet_transfer_odometer (5),
  total_loss_refund (4), retail_plan_price (4), retail_cancel_refund (4). Tools (6, fresh uuid8 each).
- Revisions:
  - check_extended: retail_refund_basis had no record-reading binding -> moved the unused-visit sum into it.
  - Replaced a purchase-transactions volume credit (would need unread deal ledgers incl. trade booking)
    by a credit-utilisation credit read from the service account.
  - replay: empty-string FKs counted as dangling -> seeds and tools now write None for empty FKs.
  - solvability: evidence lists now cover every eligibility evidence field; transfer intent from records
    (trigger state_due).
  - check_compute: total-loss history not load-bearing under a greater-of pick -> tier now averages the
    unused-visit share with the mile/day share (583.34 -> 495.67); propagated to rationale, tracing,
    closure, plan.md.
  - Transfer rule: removed a framing clause asserting a trade link no record holds (XF 11).
- Gold figures: task 0 transfer 42650, total-loss refund 495.67, fleet refund 311.89, addendum 756.03;
  task 1 retail refund 421.05, retail price 472.39. Every factor moves its result; whole baselines
  35514 / 343.00 / 448.34 / 1029.00 / 214.20 / 699.00.
- Mechanical sweeps: compute_basis quotes verbatim in rules; factor ids not substrings of tool names;
  no factor reads another factor's binding; no datetime/random/uuid in task_tools.py; VIN check digits
  computed; frozen_time `2026-10-21 10:15:00 EDT`.
- Final gates (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK,
  GROUNDING OK, SCOPE OK (CACHE-DIFF info only).

REWORK round 1: gates 7/7 green

## Round 2 (policy audit revision_1: task0 RED, task1 RED; charter F-MLABEL, F-DUPTIER, F-WINDOW, F-REAL, F-EFF, F-REIN, F-FALLBACK, F-ANCHOR, F-FIRST, F-TRADEID, F-MOVED-READING)
Plan of closure (written before edits):
- F-MLABEL: P1/P5 basis -> factory-coverage overlap proration with record inputs (FCM expiration date and miles left vs the unit's delivery odometer); D becomes a Toyota with ToyotaCare.
- F-DUPTIER: P6 method -> financed plan pro rata / unfinanced plan past half term lesser-of(retail value, day share) / retail value.
- F-WINDOW: P5 delivery_window -> new-owner enrollment allowance in dollars (variant-independent, monotone).
- F-REAL: P1 credit_utilisation -> 12-month customer-pay service spend credit; P2 recent_visit removed -> unit service-history credit; P2 fee re-keyed on net-terms tier; P2 standing credit -> tenure-only credit.
- F-EFF: every cancellation policy scoped to a request processed on its own request date (plain record test); spans then end on the effective date exactly; negative lag impossible (guards added).
- F-REIN: readings stated as "latest odometer on the plan's redemption entries, reinstated or not"; filter allowance on net visits used (redeemed less reinstated).
- F-FALLBACK: P2 rule states odometer_at_sale when no redemption entry.
- F-ANCHOR: P1 credit reads the customer's most recent total-loss cancellation (the anchor plan by rule); P5 scoped to the same plan name as the replaced plan (the retail plan cancelled for a vehicle sold or traded).
- F-FIRST: P1/P5 scoped to the single agreement/deal in delivered status; P4 to the single fleet agreement in closed status; P3 unit deal read by vehicle + status; P3 bonus counts vehicle price charges (exact); P2/P6 fees no longer read deals.
- F-TRADEID: trade appraisal tier removed; P3 prerequisite re-keyed on the covered unit's recorded title brand (salvage/rebuilt/flood); replacement named by the holder (persona on request) inside P4's closed-agreement scope; closing reading tiers = retired-unit check-in / Factory Basic warranty claim odometer / latest redemption reading.
- F-MOVED-READING: P3 reading = greater of the unit's highest check-in and its delivery odometer on its Kessler deal.
Closure (round 2), item by item:
- F-MLABEL: unit_basis / retail_basis now prorate plan_price_usd by the plan term left after the vehicle's Factory Complimentary Maintenance (max of months and miles shares for a mileage-limited coverage; months share without a limit; list without coverage) — record inputs in every non-fall-through tier. Task 0 unit is now a Toyota Tacoma (ToyotaCare 24 months / 25000 miles).
- F-DUPTIER: retail_refund_basis tiers = financed plan pro rata / unfinanced past half term min(retail value, day share) / retail value.
- F-WINDOW: delivery_window replaced by new_owner_enrollment (30.00 / 15.00 / 0 by days since delivery).
- F-REAL: credit_utilisation -> service_spend (12-month customer-pay labor + parts); recent_visit removed; fleet fee now by net-terms tier; fleet_standing -> fleet_tenure_refund; new unit_service_history credit.
- F-EFF: the three cancellation policies apply only to a request processed on its own request date (later requests stay on base terms); spans therefore end on the effective date; delivery spans clamped at 0 (no negative lag).
- F-REIN: readings and the 12-month activity test are stated on redemption entries "reinstated or not"; filter deduction on net visits used; transfer reading uses MAX odometer with the odometer_at_sale floor.
- F-FALLBACK: fleet cancel rule states odometer_at_sale where higher or where no redemption entry exists.
- F-ANCHOR: addendum credit reads "the customer's most recent cancellation of a Fleet plan for a total loss" (a single named plan = the computation's holding); sold tier dropped so the skip-total-loss figure is 575.57 under rule and compute alike; retail price scoped to a replacement purchase of the same plan name as the replaced plan.
- F-FIRST: addendum, retail price and transfer scoped to the customer's single agreement/deal of that status (plain record test; others outside the policy); total-loss unit deal read by vehicle + delivered/closed status; bonus and retail fee count vehicle price charges net of reversals (deal ledgers seeded and read); fleet fee no longer reads a deal.
- F-TRADEID: trade-appraisal tier and the "taken in trade" trigger removed; total-loss gate keyed on the covered unit's recorded title brand; replacement named by the holder inside the single-closed-agreement scope; closing reading from the retired unit's RO check-in (RO 364520, 53640) / Factory Basic claim / last recorded visit reading.
- F-MOVED-READING: total-loss reading = max(unit's highest check-in, its delivery odometer on its Kessler deal).
New gold: task 0 move 43130, total-loss 498.96, fleet cancel 331.89, addendum 515.57; task 1 retail cancel 421.05, retail price 269.50. Proof text (rationale, closure, tracing, necessity, computations, plan.md) swept.
Gates (full block, no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.

REWORK round 2: gates 7/7 green

## Round 3 (policy audit revision_2: task0 PASS, task1 RED; charter F-PAYTYPE, F-UNREACH, F-FIRST)
- F-PAYTYPE: fleet addendum spend credit and fleet refund unit-service credit now count only pay_type customer_pay lines (rule + compute filters); probes with deductible lines leave 331.89 / 575.57 unchanged. Other service-line reads swept (check-ins, relationship lines, late fees count any line and say so).
- F-UNREACH: retail trade_cycle now combines the replaced plan's sold-or-traded cancellation entry with how the replaced plan was bought (Kessler deal 50.00 / on its own 25.00 / none 0); all tiers reachable in scope; task 1 keeps a multi-source factor and 4 factors. Other scoped policies swept: no tier restates its scope.
- F-FIRST: the replaced plan is the plan named on the customer's most recent signed sold-or-traded request; a same-date tie or none takes the purchase out of the policy.
- Coordinator lines: rule rounding sentences, docstrings and tool bodies all say/enforce half up to the cent (pure-Python half-up helper class, no float round; odometers half-up whole miles; dates YYYY-MM-DD). Defining-sentence table (XF A4) and round-3 probe table added to plan.md. Proof text swept (task 1 traced replaced-plan definition and trade-cycle tiers, RAV4 "sold" wording; task 0 pay-type wording; revision logs).
- Gold unchanged: 43130, 498.96, 331.89, 515.57, 421.05, 269.50. Task 0 (PASS in revision_2) not regressed.
- Gates (full block): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.

REWORK round 3: gates 7/7 green

## Round 4 (policy audit revision_3: both tasks PASS; charter F-HALFUP)
- F-HALFUP: all 12 money rounding bindings (P1 result; P2 share_amount, recapture_amount, result; P3 standard_refund x2, loss_refund x2, result; P5 result; P6 basis_day_amount, method_amount pro rata, bundle_recapture, result) now use RND(x + 0.000001, 2), so they round half up as the rules state. Exact-tie probe: 332.025 -> 332.03, refund 338.05 = rule. Tool bodies keep the _Fmt half-up helper.
- No gold, baseline or sensitivity figure moved (COMPUTE OK against the recorded values). Proof text swept: two trace lines show the offset; revision logs added; plan.md round-3 residue note corrected; ROUND 4 section added, with the zero-amount check (no wait depends on a refusable 0.00 write).
- Gates (full block): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.

REWORK round 4: gates 7/7 green

## Round 5 (policy audit revision_4: both tasks PASS; charter F-EPS)
- F-EPS: all 12 money RND points use RND(x + 0.000000001, 2) per the coordinator ruling: exact ties round up, and non-ties within 1e-6 of a half cent no longer move (526.9849996 -> 526.98). Tool bodies keep the exact half-up helper.
- Distance check by replaying gold for both tasks: every rounded argument behind the scored, baseline and factor-sensitivity figures sits at least 0.00139 from a half cent.
- Zero-amount ruling checked: no floor creates an amount where nothing is owed; no wait depends on a refusable 0.00 write (cancellations book 0.00 refunds as legal rows).
- Gold unchanged. Proof text swept: trace lines and revision logs show the 1e-9 offset; plan.md ROUND 5 added.
- Gates (full block): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.

REWORK round 5: gates 7/7 green

## Round 6 (render scan findings F1-F5, render_r1.md; both tasks PASS)
- F1: fleet addendum and retail plan price: rate, then credits, then a floor at 0.00, then half-up rounding at the end (rule + compute MX(0, ...)); probe 0.00 where credits exceed the reduced price.
- F2: total-loss refund combination sentence now fixes the order: credits added to the rounded refund, then floored at 0.00, then capped at purchase_price (matches compute).
- F3: replacement credit reads the total-loss entry of the plan named on the customer's most recent signed total-loss request (request date, then registration time) — a record test naming the computation's holding.
- F4 + class: "keeps the base price" replaced by the restated price; every scoped overwrite restates the in-force out-of-scope price or refund (fleet sale, fleet cancel, total loss, retail cancel; retail price and transfer already did).
- F5: last_visit_reading added to usage_share bindings; class swept mechanically.
- Gold unchanged; proof text swept (task 0 traces, closure, rationale; plan.md probe row; revision logs).
- Gates (full block): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.

REWORK round 6: gates 7/7 green

## Round 7 (KB revision_2 seed-only items S-0a, S-0b, S-1a; maintenance.extended.yaml 19abc6277d2f and task_tools.py 8d7ce9149aa2 untouched)
- S-0a: the early-payment discount credit of 4.17 on RO 362877 is booked, and the open balance is 672.60.
- S-0b: the KCV-26-30418 ledger is seeded in full, and its trade-in fields are cleared.
- S-1a: the RAV4 deal's hold_expires_date is now 2023-03-16.
- Same-class members swept: no others. No scored value moved. Proof text swept: the task 0 world rows, the bonus traces and the transactions read; revision logs and plan.md ROUND 7 added.
- Gates (full block): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.

REWORK round 7: gates 7/7 green