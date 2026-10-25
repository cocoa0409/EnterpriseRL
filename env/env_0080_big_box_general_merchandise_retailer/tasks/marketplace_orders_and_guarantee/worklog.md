# worklog — marketplace_orders_and_guarantee (market), M=2

## Step 0 — pre-check and draws
- Read: references (product_extended.yaml, task_tools.py, task.json), blueprint.yaml, products/market.yaml (full),
  card.yaml (card_cardholder_benefits, card_billing_dispute, card_dispute_credits), membership.yaml
  (membership_delivery_benefit, tier params), order.yaml (order_evt_fees, order_returns), gift.yaml
  (gift_refunds_to_card, gift_promo_expiry_and_clawback, gift_issue_and_activation, promotional card variant),
  db_schema.json (market/card/gift/membership tables), share_tools.py (finders, verify threshold = 2 details),
  audits/render_source/XF_recipe.md, owner_ruling.md.
- Draws (draw_counts.py --tasks 2):
  - task 0: prerequisite_problems 3, factor_counts [6, 6, 5, 4]
  - task 1: prerequisite_problems 2, factor_counts [5, 5, 4]

### Difficulty-level decisions (recorded for the audit)
1. Trigger rule. market_seller_refund and market_guarantee_reimburse trigger card:card_post_credit when
   payment_method_type = northgate_card; market_decide_claim triggers market:market_guarantee_reimburse (same
   category). Decision: every order on which my tools book a refund or reimbursement is paid with an external
   card, and the tool bodies refuse an order paid with a Northgate Card (format/reference check, not a policy
   judgement) and always write payment_method_type external_card. market_open_claim and market_requests have no
   triggers.
2. owner=user writes (owner ruling (a)): filing a Northgate Marketplace Guarantee claim is the buyer's own
   decision. A claim on a non-Fulfilled-by-Northgate order filed in the call cannot be decided in the call (the
   seller gets guarantee_seller_response_business_days) -> the buyer's claim is the ROOT of each tree, and the
   prerequisite problems are the writes that must stand before its amount is fixed.
3. Cross-difficulty evidence: the gift charter's account-wide rule gift_promo_expiry_and_clawback ("value
   already spent is deducted from the return's refund") binds every refund of a purchase that earned a
   Northgate Promotional Gift Card. Marketplace orders can earn such a card (gift_events.source_record_id names
   "marketplace order"; nothing in market_fbn_benefits excludes promotions). Seeded cards are fully spent and
   depleted so no gift-side void is owed at the opening (owed-write check, XF 21).
4. Membership / card levers do not reach third-party seller programs (market_fbn_benefits); Fulfilled by
   Northgate refunds carry no restocking and no partial refunds (variant params), so the rich, record-based
   levers (restocking schedule, set-price saving, partial refunds, shipping allocation, promotional recovery,
   seller refunds after filing) live on seller programs; both trees use seller programs.
5. Thin charter vs draw: the draw ([6,6,5,4] / [5,5,4]) is not adjusted. Factor families used (each stated per
   policy in that policy's own words): set-price basis (method), changed-mind restocking schedule (parameter),
   seller partial-refund credit (parameter), promotional-card recovery (method, gift cross-difficulty,
   multi-source), shipping allocation (method), shipping already refunded (parameter), seller refunds booked
   after the claim was filed (parameter). Realism notes per family are in the factor cards below.

## Design (fixed after Step 0 exploration; persisted on coordinator request)
Factor families (each policy states its own ladder in its own words; tiers formula-distinct):
- A set-price basis [method]: (1) set-priced line (line amount below unit price x units bought) AND change-of-mind
  credit -> set price per unit less the set saving of the units still held, spread over the change-of-mind units of the
  line; (2) set-priced line AND the line carries an earlier unit refund -> what remains of the line amount after the
  merchandise already refunded on it, spread over the units still unrefunded; (3) set-priced otherwise -> set price per
  unit; (4) otherwise -> listed unit price. Baseline: listed unit price.
- B changed-mind restocking schedule [parameter, multi-source]: changed_mind AND requested within early_return_days (14)
  of delivery -> half the program maximum; changed_mind later -> program maximum; otherwise 0. Baseline 0.
- C seller partial-refund credit [parameter, multi-source]: partial refunds on the line AND units of the line stay with
  the buyer -> per-unit share x units credited; partials AND every unit asked back -> the whole partial; else 0.
- D promotional-card recovery [method, gift cross-difficulty, multi-source]: promo card earned by the order (gift load
  whose source_record_id is the order) with value spent AND every unit asked back for a change of mind -> whole spent
  value; spent AND units kept -> spent x price paid for the credited units / order merchandise; else 0.
- E shipping allocation [method, multi-source]: freight program AND part of the order -> per piece; other program AND
  part -> merchandise-value share; else whole charge. Baseline: whole charge.
- Y seller refunds set off [parameter]: latest unit refund on the claimed line dated on/after the claim (or request)
  date, plus the credited units' value share of shipping refunds; tiers: both / unit refund only / shipping only / none.

Task 0 (Seller-Fulfilled "Ridgeway Coffee Supply", café buyer Danielle Whitcomb, Wren & Willow Coffee House):
- ROOT  market_ext_return_refund_claim_amount -> file_return_refund_claim_24f7de0f (USER) A,B,C,D,E,Y = 6
- P     market_ext_return_refund_claim_reimbursement -> grant_return_refund_claim_d58e2e3e A,B,C,D,E,Y = 6
- P     market_ext_unresponsive_claim_reimbursement -> grant_unresponsive_seller_claim_064f9cf7 A,C,D,E,Y = 5
- P     market_ext_keepit_unit_refund -> refund_keepit_units_1db7244d A,B,C,D = 4
- Edges: root <- return-refund reimbursement (value: room left under the per-order maximum; undecided claims reserve
  their claimed amount), root <- unresponsive reimbursement (value: room), root <- keep-it refund (state_gate).
Task 1 (International Seller): user not-as-described claim (A,C,D,E,Y = 5, root), not-received reimbursement
  (A,C,D,E,Y = 5, value via room), restocking-shortfall top-up (A,B,C,D = 4, state). Tools 763dfc78 / 35c21a00 / 469f1911.

## Task 0 — status (per-task gates run)
- Files: market.extended.yaml (4 policies, generated from /tmp/marketplace_orders_and_guarantee_0080/gen_t0.py by
  build.py, base section = blueprint market.yaml verbatim), task_tools.py (4 tools), tasks/0.json (task0_build.py).
- Gold (frozen 2026-10-23 11:05:00 PDT): keep-it refund 19.80 -> return-refund grant 241.43 -> unresponsive grant
  1875.24 -> buyer files return-not-refunded claim 349.62 (units 2, line = cold brew systems).
- Baselines: keep-it 36.00, return-refund 483.67, unresponsive 2157.95, claim 383.33 (room).
- Edge runs: skip return-refund grant -> claim 159.77; skip unresponsive grant -> 242.24 (room binds); skip keep-it
  -> claim unchanged 349.62 (state gate; terminal differs by the refund row and net paid).
- Fixes during gates: empty FK card_account_id -> None (replay dangling FK); reimburse_once / claim_window evidence
  now cite the bound field paths; no_card_dispute retired for external-card orders by a self-scoped overwrite in the
  claim policy (no card_events row can carry source_record_id = an external-card order; the gate is restated in
  force for Northgate-Card orders).
- Half-cent sweep (halfcent.py): no scored/baseline/sensitivity figure within 1e-6 of a half cent.
- Trigger rule: tools write market_open_claim (no triggers), market_decide_claim granted (-> market:
  market_guarantee_reimburse, same category, written in the same call), market_guarantee_reimburse and
  market_seller_refund with payment_method_type external_card (card trigger condition northgate_card never met).

## Task 1 — status (per-task gates run)
- International Seller "Ravello Artisan Imports", buyer Marisol Trevino (Portland OR 97214), frozen 2026-10-22 14:20:00 PDT.
- Gold: restocking top-up 4.11 -> grant not-received claim 2097.33 -> buyer files not-as-described claim 367.20
  (line = platters, units 4). Baselines: 20.74 / 2329.00 / 402.67 (room).
- Edge runs: skip grant -> claim 334.19 (claim reserve 2165.81 makes the room bind); skip top-up -> claim unchanged
  (state gate). Both prerequisite orders replayed identical. Platter unit price tuned 88.00 -> 99.00 so the claim
  sits inside (room with the claim pending, room after the grant].
- Half-cent sweep: no hits.

## Difficulty-level closing records
- Coverage: task 0 = {return_refund_claim_amount, keepit_unit_refund, return_refund_claim_reimbursement,
  unresponsive_claim_reimbursement}; task 1 = {item_condition_claim_amount, restocking_topup,
  missing_item_reimbursement}; pairwise disjoint, union = all 7 extended policies; 7 tools each named by one
  target_tool.
- Trigger list (every event my tools write, with base triggers): market_open_claim [] ; market_decide_claim
  (granted) -> market:market_guarantee_reimburse (same category, written in the same grant call);
  market_guarantee_reimburse -> card:card_post_credit only when payment_method_type = northgate_card (tools write
  external_card and refuse Northgate-Card orders); market_seller_refund -> same card trigger, same guard;
  market_requests (intake) no triggers. Nothing lands in another category.
- Owed-write check: both promo cards are depleted (no unused value for a gift-side void); no Northgate Card on
  either order; membership/order/plan/trade categories untouched. No write another product calls owed at once can
  move a scored read.
- Defining-sentence table (per policy; generator keeps each sentence once and quotes it in compute_basis):
  scope sentence -> object selection bindings; line sentence -> held/kept units and price paid (plain, shared by
  pricing, partial and promo factors, XF A.4); order sentence -> merchandise total / order units (plain);
  standard-method sentence -> baseline; room sentence -> room (plain); final sentence -> result rounding/limit;
  assembly sentence (generic, names no factor quantity) -> owed; one ladder sentence per factor -> that factor's
  bindings only. No factor binding reads another factor's binding (checked by construction: factor bindings read
  only plain bindings and records).
- Probe table (DSL reads x {decoy, absent, second record}):
  - XLATEST gift load by source_record_id: decoy = a card loaded for another purchase is not selected (source
    filter); absent = None -> CFIELD variant None -> no recovery tier; second card for the same order: latest load
    wins (stated as "the promotional card whose initial load names the order").
  - LATEST claim (reason, undecided): decided claims are excluded by claim_decision filter (the grant tools set the
    claim row's claim_decision to granted); a second undecided claim of the same reason: latest wins (rule says
    "most recent"); absent -> None -> grant tool not applicable (state_due not lit).
  - LATEST unit refund on a line with date test: absent -> '' >= date false -> shipping-only or nothing; a refund
    dated before the reference date (task 0 espresso 2026-09-25) is not set off; ties keep the first row.
  - SUM partials on a line: other lines' partials excluded by original_event_id filter.
  - SUM change-of-mind requests: damaged-reason requests (partial offers) excluded by return_reason filter.
- Rounding: RND(x + 0.000000001, 2) on non-negative values; tools use a Decimal half-up class static method.
- Realism notes / residual risks recorded for the audit: (1) restocking schedule (half the program maximum within
  14 days of delivery, full maximum later) is Northgate's own changed-mind schedule, applied to keep-it refunds as
  well; (2) promotional recovery on guarantee reimbursements and claims extends the gift charter's "deducted from
  the return's refund" to guarantee money for the same purchase (Northgate's own rule, stated in each policy);
  (3) pending claims reserve their claimed amount against the per-order maximum (the base cap is "across all
  claims on the order"); (4) the keep-it / top-up prerequisite edges are state gates (procedural), the value edges
  run through the guarantee room; (5) record selections are coarse exact record tests (most recent request /
  claim of a reason), declared in each scope sentence.

ROUND 1: gates 7/7 green

## REWORK round 2 — plan (audit: audits/policy_task/marketplace_orders_and_guarantee/{_difficulty,0,1}.md, read in full)
Verdict r1: task0 RED, task1 RED; items CG-1..CG-17, T0-C1, T1-C1.
Plan (verify each, then close the CLASS):
- CG-1: drop the market_returns overwrite from the claim amount (u) and return-refund reimbursement (h) policies.
- CG-2: every money-booking policy (h, g, n, r, s) scoped by a payment record test (order paid with an external card);
  replaced_by restates the base tender rule for Northgate-Card orders; tools' refusals then match the scope.
- CG-3: top-up scope stated and tested as a record test (seller refunded every requested unit, restocking withheld
  above the schedule); zero figure settled with nothing booked; item-condition claim's wait on it -> action form.
- CG-4: claim waits scoped to earlier claims the seller has not refunded in full; reimbursement scopes exclude
  seller-resolved claims (base denies those).
- CG-5: "no decision" stated as the claim record's own decision field, which the grant also marks (sentence added).
- CG-6/CG-9: seller refunds set off = every unit refund entry on the claimed line (top-up entries, which refund no
  units, excluded), not only the latest; scope test: the line carries no unit refund dated before the anchor.
- CG-7: tie rule on every "most recent" selector (first recorded wins).
- CG-8: line-pricing tiers restated to cover every case.
- CG-15: refund tool docstrings/bodies aligned (request type checked in body; top-up receipt fixed).
- CG-17: claim units pinned (units of the request not yet covered by a unit refund) and recorded by the tool.
- CG-16: single-factor quantities moved into their factor's sentence/bindings.
- T0-C1/T1-C1: edge_load_bearing net-paid figures recomputed from the replay.
- CG-10/11/12/13/14: verify; close what the charter allows, dispute with evidence where it does not.


## REWORK round 2 — record (supersedes the round-1 figures and factor labels above)
- Generator: /tmp/marketplace_orders_and_guarantee_0080/gen_r2.py (all 7 policies, shared builders); build.py writes
  market.extended.yaml; task0_build.py / task1_build.py rebuild the task files from live recomputation and tool replay;
  rationales are templated from the recomputed figures (no hand-typed numbers).
- Item closures: see audits/policy_task/marketplace_orders_and_guarantee/rework_claims_r2.md (CG-1..9, 12, 13, 15..17,
  T0-C1, T1-C1 closed; CG-10, CG-14 disputed; CG-11 partly closed / disputed).
- Gold r2: task 0 keep-it 19.78, return-refund grant 246.09, unresponsive grant 1871.34, claim 356.39 (2 units);
  task 1 top-up 4.11, missing-item grant 2097.33, claim 367.20 (4 units). Edge runs: task 0 skip return-refund grant ->
  158.92, skip unresponsive grant -> 312.05, skip keep-it -> unchanged (state gate); task 1 skip grant -> 334.19, skip
  top-up -> unchanged (state gate, action form). Prerequisite permutations replayed identical in both tasks.
- Probe table r2 (probes_r2.py, scratch copies):
  - opening-world matrix: each world lights only its own state_due policies (task 0: keep-it, both grants; task 1:
    missing-item grant, top-up); the top-up is not engaged on task 0 (seller refunded only part of each return); every
    absent object evaluates to 0 without error (None guards on line, units, claimed amount).
  - decoy: a quantity-0 top-up on the claimed line does not move the claim; partial refunds and unit refunds on other
    lines never enter; damaged-reason requests are not change-of-mind units.
  - second record / tie: a same-day second authorization recorded later does not switch the claim's return.
  - both units refunded (claim and grinder reimbursement) -> 0 (out of scope; base denies seller-resolved claims).
  - top-up with a larger partial refund -> 0 (settled with nothing booked).
  - absent promotional card -> recovery 0.
- CG-10 evidence (dispute): gift charter gift_issue_and_activation issues a promotional card for issue reason
  "promotion" with no purchase-type restriction; gift_events.source_record_id names "Northgate order or marketplace
  order"; market_fbn_benefits excludes membership, cardholder discount, Northgate Cash, price match and Protect from
  non-FBN items, not promotions. Search for an alternative cross-category lever on seller-program orders: membership and
  card benefits are FBN-only (market_fbn_benefits); a Northgate-Card tender makes every refund/reimbursement trigger
  card:card_post_credit (forbidden write); a gift-card tender (allowed by gift_redemption) makes the gift credit-back
  (gift_refunds_to_card) an owed write in a category no difficulty claims; plan_purchase_eligibility_and_price excludes
  marketplace items; order price match excludes marketplace offers; trade has no marketplace tender. No writable,
  record-backed cross-category lever exists for these orders, so the promotional recovery stays; ruling requested.
- CG-11 / CG-14: no non-zero default exists for an absent partial refund or promotional card, and no record carries an
  offered keep-it amount; disputed with this evidence.
- Seeds: task 0 espresso line now has no unit refund before filing (scope test); shipping goodwill refund replaces
  the earlier full shipping refund; espresso unit price retuned (room non-binding in gold, binding when either earlier
  claim stays undecided). Seed claim amounts recomputed (return-refund claim under its own policy at the filing date;
  unresponsive claim gross per the base event meaning). Task 1 world unchanged.
- Tools: keep-it body checks the refund-without-return answer; top-up docstring/body name and check the return
  authorization; receipts match bodies.
- Sweeps after the change: compute_basis / replaced_by verbatim in their rules; no factor binding reads another
  factor's binding; no factor id inside a tool name; no forbidden substring in task_tools.py; no figure within 1e-6 of a
  half cent; task files swept for round-1 figures and wording (none left).

REWORK round 2: gates 7/7 green

## REWORK round 3 — plan (audit revision_2 + coordinator rulings CG-10 accepted w/ conditions, CG-14 upheld, CG-11 clarified)
- R2-1: every stated scope test computed (non-FBN program, external card, units still open, most recent unit refund on
  the line absent or dated on/after the anchor); out of scope the policy fixes nothing (figure zero), as each rule says.
- R2-2: scope and wait sentences worded in units ("has not refunded every unit"), matching the unit tests.
- R2-3: top-up nets every refund entry on the line, top-ups already booked included (second evaluation owes nothing).
- R2-4: claim policies scoped to external-card orders, matching the grants they wait on.
- R2-5 / CG-3: top-up docstring covers any reason; the item-condition claim's wait names the same request the top-up
  handles (most recently answered with a return authorization); engagement adds the anchor test.
- CG-10 conditions: promotion terms stated as Northgate's own (qualifying merchandise total, load names the order);
  recovery only of value spent, only when part of the order is returned or refunded (guarantee reimbursements stated as
  refunds under the promotion terms); depleted cards, nothing owed gift-side.
- CG-14: keep-it restocking deduction replaced by the returnless-refund shipping keep-back (units' allocated share of the
  order's shipping charge, changed-mind on buyer-pays programs; freight per piece).
- CG-11: shipping allocation's whole-order tier and the set-off sum tiers coincided -> shipping tiers become
  freight per piece / value share / no shipping charged (absent tier); seller set-off becomes shipping refunds with the
  same three-way key; unit-refund set-off becomes a plain binding. Pairwise tables below once rebuilt.


## REWORK round 3 — record (supersedes round-2 figures and factor ids above)
- Generator /tmp/marketplace_orders_and_guarantee_0080/gen_r3.py (build.py uses it); task builders and rationale templates
  updated for the new factor ids (shipping_refund_setoff, return_ship_keepback).
- Gold r3: task 0 keep-it 26.21, return-refund grant 246.09, unresponsive grant 1871.34, claim 356.39 (2 units);
  task 1 top-up 4.11, missing-item grant 2097.33, claim 367.20 (4 units). Edge runs unchanged in kind (task 0 skips:
  158.92 / 312.05 / unchanged; task 1: 334.19 / unchanged). Half-cent sweep clean.
- Probe table r3 (probes_r2.py): opening matrix — each world lights only its own state_due policies; unit refund dated
  before the request -> reimbursement and claim out of scope (0); top-up after its own booking -> 0; later authorized
  unrefunded request on the bowl line -> top-up not engaged (single-authorization test); Northgate-Card copy -> every
  policy 0 (out of scope); FBN copy -> 0; merchandise below the promotion's qualifying total -> no recovery; quantity-0
  top-up decoy -> claim unchanged; same-day second authorization recorded later -> claim unchanged; absent card -> 0.
- CG-11 pairwise table (tier pair -> distinguishing input; absent-record tiers are A8 tiers and coincide with no other
  tier over their whole domain):
  - line pricing (change-of-mind policies): withdrawal vs set price -> units kept at set price > 0; withdrawal vs list,
    set price vs list -> line amount below list x units.
  - line pricing (seller-fault policies): remaining-per-unrefunded vs set price -> unit refunds on the line at list
    price; set price vs list -> set pricing.
  - restocking schedule: half max / max / zero -> request days after delivery (14) and reason; on 0% programs all three
    are zero (observation O7, not a coincidence on programs with a maximum).
  - partial credit: share vs whole -> units kept or with the buyer; no-partial tier is the absent tier.
  - promotional recovery: whole vs prorated -> every unit refunded; no-card / nothing-spent tier is the absent tier.
  - shipping allocation and shipping-refund set-off: per piece vs value share -> freight program (unit share differs
    from value share); no-shipping-charged / no-refund tier is the absent tier.
  - return-shipping keep-back: per piece vs value share -> freight program; no-keep-back tier holds for other reasons
    or seller/Northgate-paid programs, where the other tiers would give a positive figure.
- Sweeps: compute_basis / replaced_by verbatim; no factor reads another factor's binding; no factor id inside a tool name;
  no forbidden substring; task files and rationales swept for round-2 wording (keep-it deduction, seller set-off,
  "every return ... refunded in full") — none left.

REWORK round 3: gates 7/7 green

## REWORK round 4 — verification before change (audit revision_3: R3-1..R3-4; coordinator routes)
- Base check for the R3-1/R3-2 route ("key on the request the refund references, an exact value match"): base event
  market_seller_refund defines original_event_id as "The market_post_line or market_charge_shipping row refunded"
  (market.yaml events; db_schema market_events.original_event_id). A seller refund references a LINE, never a return
  request, so no record links a unit refund to the request it settles; per-request netting by an exact value match is
  not expressible in the frozen schema. The DSL's filters are equality-only (check_compute _rows), so a LATEST cannot
  exclude "quantity != 0" rows either.
- Base check for the R3-4 route: gift_promo_expiry_and_clawback: "Where promo_clawback_on_return is true and the
  purchase that earned the promotional card is returned, any unused promotional value is voided as promo_clawback, and
  value already spent is deducted from the return's refund." The base text is silent on partial returns; the round-3
  ruling's condition (c) reads "the earning purchase (or that part of it) is returned/refunded".
- Floor analysis for the route "whole spent value once, only on the refund that un-qualifies the order, never prorated":
  a threshold is crossed by exactly one credit per order, so the recovery factor can move the figure of at most one
  computation per order. Genuine factor families per policy without the recovery factor (reachable, non-coinciding):
  claim/return-refund policies 5 (line pricing, restocking schedule, partial credit, shipping allocation, shipping-refund
  set-off); seller-fault policies 4; keep-it 3 (line pricing, return-shipping keep-back, partial credit); top-up 3.
  Draws: task 0 [6,6,5,4], task 1 [5,5,4] -> every one of the seven computations needs a load-bearing recovery
  factor; under the route at most one per task can have one, so five computations would fall below their draw (the
  gates reject that). No further record-backed lever exists in the charter (searched: delivery/ship dates, seller
  answer dates, item condition, signature thresholds, freight windows, customer type).
- Decision (recorded per the brief: closest established rule, push on): keep the prorated recovery (condition (c)'s
  "or that part of it"), state the recovery ONCE (the promotion-terms sentence no longer restates it, removing the
  second reading), and dispute the "never prorated" route with this analysis. R3-1: rule wording made exact to what
  the record test can check. R3-2: dispute exact per-request keying (no record link); scope test tightened where
  exact. R3-3: disputed together with R3-4 (the reachable whole-value tier needs the route's semantics).

## REWORK round 4 — record (supersedes the R3-1 / R3-2 lines of the plan above)
- Generator: /tmp/marketplace_orders_and_guarantee_0080/gen_r4.py (derived from gen_r3 by mk_gen_r4.py; every edit
  anchored and asserted). Charter rebuilt by build.py; tasks rebuilt by task0_build.py / task1_build.py.
- R3-1 + R3-2 (one class: "which refunds on the line belong to the policy's request or claim"):
  - the date anchor is removed everywhere (u, h, g, n, q scope; s engagement); no binding selects or dates refunds;
  - replaced by an exact count test on the line: return requests other than the policy's own (u, h, q, s) — or all
    return requests (g, n, which have no request of their own) — must be no more than the partial refunds on the line.
    Under the base return rule a partial-refund offer settles its request without a unit refund, so every unit refund on
    such a line belongs to the policy's request or claim. Exact per-request keying is impossible: market_seller_refund
    original_event_id is "The market_post_line or market_charge_shipping row refunded" (base event; db_schema);
  - h and q also test that their own request is not answered partial_refund_offer (h's request is the line's most
    recent request; q's the order's most recent not_as_described request);
  - the wait sentences of u (on h and g) and q (on n) and the edge conditions carry the same tests;
  - top-ups: unit-refund amounts exclude quantity=0 rows (exact equality filter); unit counts add 0 for them.
- R3-4: the separate promotion-terms sentence is removed from all seven rules. The promotional-recovery sentence is now
  the single statement of the promotion (issue on reaching promo_qualifying_total_usd, card load naming the order,
  recovery of spent value only, seller refunds and guarantee reimbursements alike, unused value only under the gift
  rules) and of its ladder. Counted: one occurrence per rule.
- Seed consistency for that sentence: the first promotional redemption in each world is re-dated after the seeded
  seller unit refunds (task 0: 10-17; task 1: 10-10), so the seller refunds, recorded without a recovery, are what
  the rule produces (nothing spent yet). Task 0's reserved claim amount for the grinder claim is recomputed on its
  filing-date world, with both redemptions absent.
- R3-3 / R3-4 routes ("whole spent value once, on the refund that un-qualifies the order; never prorated") — disputed,
  ruling requested. Proof:
  1. Prorated rule: in the six scopes that require unrefunded units, no third reachable tier with a distinct value
     exists. The refund that completes the order carries spent x paid / merchandise total, and "whole value less the
     earlier shares" is the same number. The un-netted "whole value" recovers the value twice, and no record carries
     earlier recoveries.
  2. Route: the only three-valued ladder is
     - whole value spent;
     - whole value capped at the merchandise refunded;
     - nothing.
     A threshold is crossed by one credit per order, and the prerequisite refunds commute (all orders replayed
     identical), so only the root can be the crossing write. Each non-crossing computation would then keep a
     promotional factor equal to its baseline (DECORATIVE), and gift reads that are not load-bearing; check_compute
     rejects both per computation.
  3. Dropping the factor there leaves u, h, g, r, n and s below their draws ([6,6,5,4] / [5,5,4]). The other
     cross-category levers were searched in rounds 2–4 (membership, card, plan, order, trade; delivery dates,
     signature thresholds, duties, item condition, customer type); none is record-backed for seller-program orders.
  4. Proration is also the only per-refund attribution that does not depend on the booking order of commuting refunds.
- Probe table (round-4 class probes; u and q on the handling-time world, the others on the opening world):

| policy | case | kind | figure | expected |
|---|---|---|---|---|
| h | R3-a top-up (0 units) on the claimed line | decoy | 246.09 -> 246.09 | unchanged: a 0-unit entry is no unit refund (amount and units excluded by quantity=0) |
| h | R3-a + seller unit refund dated before the request | date edge | 246.09 -> 246.09 | unchanged: no date test; the line's only non-partial request owns its unit refunds |
| u | R3-b second request on the line with its own unit refund | second rec | 356.39 -> 0 | 0: out of scope (3 requests - 1 > 1 partial refund); base governs |
| u | declined other request on the line (no refund) | decoy | 356.39 -> 0 | 0: counted, conservative out of scope |
| u | other request settled by a partial refund (+9.00 partial) | second rec | 356.39 -> 350.39 | in scope; partial credit share moves |
| h | most recent request on the claimed line answered partial_refund_offer | decoy | 246.09 -> 0 | 0: the request behind the claim must not be a partial-offer request |
| h | same-day second request on the claimed line, recorded later | tie | 246.09 -> 0 | first recorded kept as request behind the claim; count makes it out of scope (0) |
| g | return request on the claimed espresso line (not partial-settled) | second rec | 1871.34 -> 0 | 0: out of scope |
| g | seller refunds one claimed unit after filing (claim resolution) | second rec | 1871.34 -> 910.42 | in scope; one unit still unrefunded, set-price-with-refunds tier |
| n | return request on the claimed rug line (not partial-settled) | second rec | 2097.33 -> 0 | 0: out of scope |
| q | the not-as-described request answered partial_refund_offer | decoy | 367.2 -> 0 | 0: out of scope |
| s | declined second request on the returned bowl line | second rec | 4.11 -> 0 | 0: settled with nothing booked |
| s | top-up already booked (0-unit entry) on the bowl line | second rec | 4.11 -> 0.0 | 0.00: top-ups count among the refunds on the line |
| u | no promotional card (gift ledger absent) | absent | 356.39 -> 372.21 | promo tier 'otherwise' -> no recovery, no error |
| h | no undecided claim (selector None) | None | 246.09 -> 0 | 0, no error |
| g | no undecided claim (selector None) | None | 1871.34 -> 0 | 0, no error |
| r | no refund-without-return answer (selector None) | None | 26.21 -> 0 | 0, no error |
| q | line recorded with 0 units (division guard) | zero-div | 367.2 -> 342.03 | no division error |
| u | cold brew request dated 2026-09-28 | date edge | 356.39 -> 356.39 | day 14: half the maximum |
| u | cold brew request dated 2026-09-29 | date edge | 356.39 -> 276.78 | day 15: the maximum |
| n | order merchandise below the promotion's qualifying total | absent | 2097.33 -> 366.48 | no promotional recovery |

- Sweeps:
  - Stale text: no "most recent unit refund", "dated on or after", "when any part of that order", `*_last_refund_date`,
    `s_last_unit_refund` or `*_anchor` remains in the charter, the tools or the task files.
  - The rationale prerequisite quotes are now filled verbatim from policy_source.
  - Half-cent sweep: no hits on either task (result, per-factor baselines, all-baseline).
- Figures: every computation keeps its round-3 value. In particular, the re-dated redemptions leave every
  handling-time figure unchanged, and the drawn counts are unchanged.
- Gates: check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding and
  check_cross_fire all OK.
- Traceability (not a gate) reports the task tool names as unreachable before the KB is rendered. This is expected,
  because the published KB carries them.

REWORK round 4: gates 7/7 green

## REWORK round 5 — plan (audit revision_4: R3-2, R3-3, R3-4 open; coordinator rulings round 5)
- Verified:
  - R3-2 A2 holds. Two partial refunds on L3 (one a goodwill refund on the damaged request) let a defective-unit refund
    of another request pass the count test.
  - R3-2 A3 holds. A later partial-offer request on L2 becomes "the most recent request" behind h's claim.
  - The count proxy is withdrawn.
- R3-2 class (u, h, q, s request-based; g, n claim-based), per ruling:
  - exact count, no purpose clause: the line carries exactly one return request (u, h, q, s), or carries no return
    request (g, n: their claims carry no request of their own, so the same exact test reads zero); the
    partial-refund count and the h/q answer test are removed;
  - waits: u on h and g, q on n, with matching edge conditions;
  - out of scope each rule restates its base clause verbatim, with no extended figure:
    - decision clause: h, g, n;
    - return-rule clause: r, s;
    - base claim-record meaning of the amount claimed: u, q.
- Seeds for R3-2 (realism):
  - the seeded "damaged" return requests answered with partial-refund offers become buyer contacts to the seller
    (not_as_described) settled by the seller's partial refund on the line;
  - partial_refund_without_return_allowed is true on both programs, so every in-scope line carries only its own request;
  - contact distinguish_by (reason, date) is kept unique.
- R3-4 / R3-3 per the revised route, as ONE promotional sentence carrying terms and ladder:
  - proportional tier: value spent x price paid for the units / merchandise total;
  - un-qualifying tier: when the merchandise kept on the order after the refund falls below
    promo_qualifying_total_usd, the whole remaining value = value spent x (merchandise total - merchandise refunded on
    the order other than on the figure's units) / merchandise total;
  - otherwise 0;
  - merchandise refunded is recorded line by line: the set price per unit x the more of (units refunded by unit and
    cancellation refunds) and (units of granted claims). The order is scoped to at most ten lines so that the line
    enumeration is exact.
- Seeds for R3-4: the promotional cards are spent before any seeded unit refund (redemptions re-dated back), and the
  seeded seller unit refunds carry their proportional share. Each earlier refund therefore recovered exactly the share
  the rule's "remaining" subtracts.
- R3-3: three reachable tiers in every policy. Probes:
  - one producible scaled world per policy reaches the un-qualifying tier;
  - both sides of the threshold boundary.

## REWORK round 5 — record
- Generator: gen_r5.py, derived from gen_r4 by mk_gen_r5.py, with every edit anchored and asserted. Charter rebuilt
  with build.py; worlds rebuilt with world0/world1 and eval0/eval1; tasks rebuilt with task0_build/task1_build.
- R3-2 (u, h, q, s / g, n) — ruling applied.
  - Each scope is the exact count "the requested / claimed / returned line carries exactly one return request" (g, n:
    "the claimed line carries no return request"). The count reads COUNT market_request_return on the line. The
    partial-refund count and the h/q answer tests are deleted, and there is no purpose clause.
  - The same wording is in the wait sentences of u on h ("whose claimed line carries exactly one return request") and
    of u on g / q on n ("whose claimed line carries no return request"). The edge conditions match.
  - Out of scope, each rule says "elsewhere it fixes nothing, its figure is zero and the base rule stands: ..." and
    quotes the base text verbatim:
    - h, g, n: the market_guarantee_decision clause;
    - r, s: the market_returns clause;
    - u, q: the base claim record's field meaning "Amount claimed, the price of the affected items plus their
      shipping, positive.".
- Seeds for R3-2. The damaged-reason return requests answered partial_refund_offer are replaced by buyer contacts
  (market_contact_seller, not_as_described) that the seller settled with a partial refund on the line. Both programs
  allow a partial refund without a return (partial_refund_without_return_allowed true). Contact keys (reason, date)
  stay unique. Every in-scope line now carries only its own request.
- R3-4 / R3-3 — revised route applied as ONE sentence per rule, holding the terms and the ladder.
  - Tiers:
    - proportional: value spent x price paid for the units / merchandise total;
    - un-qualifying refund: when the merchandise kept after the refund is below promo_qualifying_total_usd, the whole
      remaining value = value spent x (merchandise total - merchandise refunded on the order other than on the
      figure's units) / merchandise total;
    - otherwise 0.
  - Merchandise refunded is counted line by line: set price per unit x the greater of (units of unit and cancellation
    refunds) and (units of claims whose claim record shows granted).
  - Kept after = merchandise total - merchandise refunded - price paid for the units not yet refunded.
  - The order scope is at most ten lines, which makes the line enumeration exact. It is in every policy's scope; the
    waits need no line test, because the waiting policies carry the same order test.
  - Covered units already refunded (not "other"): u and h, their line's unit-refunded units; s, the returned units
    the seller refunded; the others, none.
- Seeds for R3-4. Both promotional cards are fully spent before any seeded unit refund (task 0 redemptions 09-27 and
  10-05; task 1 10-01 and 10-05; closed on the last). Each seeded seller unit refund carries its proportional share
  (the merchandise kept stays above the qualifying total), so the earlier refunds recovered exactly what the
  remaining-value tier subtracts. The task 0 grinder claim amount is recomputed on its filing-date world.
- Figure changes, all from the seeded shares: the return-refund reimbursement, the root claim of task 0 and the
  top-up. The remaining figures are unchanged, and so are the drawn counts.
- Tier reachability (R3-3). Every policy reaches all three tiers:
  - the absent-card tier, by probe;
  - the proportional tier, on its own task world;
  - the un-qualifying tier, in a scaled copy of its world (merchandise just above the qualifying total). The tier
    depends only on lines, units and the card.
  - Threshold boundary on each policy's world: the qualifying total set equal to the merchandise kept gives the
    proportional tier; one cent above it gives the remaining-value tier.
- XF re-check on the changed parts:
  - A1: the promotional bindings read only plain bindings.
  - A7: the two non-zero tiers coincide only at kept = 0, a point.
  - A8: the ladder text equals the rule and the compute.
  - B10: probes below.
  - B12: the remaining-value sentence was reworded to one reading.
  - B13: the compute_basis / replaced_by / policy_source / baseline sweep is clean.
  - C19: coarse exact record test, base restated verbatim.
  - D20: gates OK.
  - F27: gift ledgers complete; seller refunds priced by the rule.
- Probe table (u and q on handling-time worlds, the others on opening worlds):

| policy | case | kind | figure | expected |
|---|---|---|---|---|
| u | A2: second request on the claimed line refunded + extra partial refund | second rec | 364.3 -> 0 | 0: two requests on the line, out of scope; base claim amount stands |
| h | A3: later partial-offer request on the claimed line | decoy | 251.54 -> 0 | 0: two requests on the line, out of scope; base decision clause stands |
| g | a return request on the claimed espresso line | second rec | 1871.34 -> 0 | 0: the claimed line must carry no request |
| g | seller refunds one claimed unit after filing | second rec | 1871.34 -> 910.42 | in scope; one unit open, set-price-with-refunds tier |
| n | a return request on the claimed rug line | second rec | 2097.33 -> 0 | 0: out of scope |
| q | a second request on the platter line | second rec | 367.2 -> 0 | 0: out of scope |
| s | declined second request on the returned bowl line | second rec | 5.98 -> 0 | 0: settled with nothing booked |
| s | top-up already booked (0-unit entry) | second rec | 5.98 -> 0.0 | 0.00 after its own booking |
| h | 0-unit top-up decoy on the claimed line | decoy | 251.54 -> 251.54 | unchanged: not a unit refund (amount filter quantity=0, 0 units) |
| u | same-day second authorization recorded later (other line) | tie | 364.3 -> 364.3 | unchanged: the first recorded counts |
| u | order with 10 lines (zero-priced filler lines) | boundary | 364.3 -> 364.3 | in scope (10 lines) |
| u | order with 11 lines | boundary | 364.3 -> 0 | 0: out of scope |
| u | cancellation refund of a dripper adds to merchandise refunded | second rec | 2900.35 -> 2934.55 | + one dripper at its set price |
| u | espresso claim decided other than granted | decoy | 2900.35 -> 981.35 | its units no longer count |
| u | threshold = merchandise kept after (1734.7) / one cent above | boundary | 364.3 -> 329.84 | at the threshold proportional; above it the whole remaining value |
| h | threshold = merchandise kept after (4085.95) / one cent above | boundary | 251.54 -> 170.36 | at the threshold proportional; above it the whole remaining value |
| g | threshold = merchandise kept after (2441.5) / one cent above | boundary | 1871.34 -> 1822.84 | at the threshold proportional; above it the whole remaining value |
| r | threshold = merchandise kept after (4326.3) / one cent above | boundary | 26.21 -> 0.0 | at the threshold proportional; above it the whole remaining value |
| q | threshold = merchandise kept after (2410.18) / one cent above | boundary | 367.2 -> 319.08 | at the threshold proportional; above it the whole remaining value |
| n | threshold = merchandise kept after (2786.38) / one cent above | boundary | 2097.33 -> 2041.7 | at the threshold proportional; above it the whole remaining value |
| s | threshold = merchandise kept after (4914.38) / one cent above | boundary | 5.98 -> 0.0 | at the threshold proportional; above it the whole remaining value |
| u | producible scaled world (merchandise total 1100.01, kept after 379.13) | tier reach | promo -> 50.28 | whole remaining value (un-qualifying tier) when kept after < 1000 |
| h | producible scaled world (merchandise total 1100.01, kept after 893.01) | tier reach | promo -> 92.09 | whole remaining value (un-qualifying tier) when kept after < 1000 |
| g | producible scaled world (merchandise total 1100.01, kept after 533.6) | tier reach | promo -> 86.64 | whole remaining value (un-qualifying tier) when kept after < 1000 |
| r | producible scaled world (merchandise total 1100.01, kept after 945.53) | tier reach | promo -> 86.64 | whole remaining value (un-qualifying tier) when kept after < 1000 |
| q | producible scaled world (merchandise total 1100.01, kept after 529.35) | tier reach | promo -> 55.63 | whole remaining value (un-qualifying tier) when kept after < 1000 |
| n | producible scaled world (merchandise total 1100.01, kept after 611.98) | tier reach | promo -> 98.12 | whole remaining value (un-qualifying tier) when kept after < 1000 |
| s | producible scaled world (merchandise total 1010.0, kept after 991.03) | tier reach | promo -> 100.0 | whole remaining value (un-qualifying tier) when kept after < 1000 |
| u | no promotional card | absent | 364.3 -> 377.12 | no recovery, no error |
| h | no undecided claim (selector None) | None | 251.54 -> 0 | 0, no error |
| r | no refund-without-return answer (selector None) | None | 26.21 -> 0 | 0, no error |
| q | line recorded with 0 units | zero-div | 367.2 -> 331.46 | no division error |
| u | cold brew request dated 2026-09-28 | date edge | 364.3 -> 364.3 | day 14: half the maximum |
| u | cold brew request dated 2026-09-29 | date edge | 364.3 -> 284.69 | day 15: the maximum |

- Sweeps:
  - Stale text: no partial-refund count, answer test, "in the shares this sentence fixes", "every unit bought on the
    order has already been refunded" or "units of the order still unrefunded" remains in the charter or the task files.
  - Builder tier texts, the near-miss line and the multi-source line in both rationales, and the keep-it uniqueness
    basis were all updated.
  - Half-cent sweep: no hits.
- Gates: all seven OK.

REWORK round 5: gates 7/7 green

## REWORK round 6 — audit revision_5 (R5-1, R5-2) and record
- Verified:
  - R5-1 holds. P1c reproduced on a task 1 copy: the claim recovered again after the order was already below the
    qualifying total.
  - R5-2 holds. r_order_units was defined in a plain sentence and read only by r_return_ship_keepback.
- R5-1, all seven policies (gen_r6.py, from gen_r5 via mk_gen_r6.py and mk_gen_r6b.py). One promotional sentence per
  rule, used by the rule and the ladder:
  - "the whole remaining spent value, that is the value spent less what the order's earlier refunds recovered under
    this sentence";
  - "a refund made when the merchandise kept on the order was already below promo_qualifying_total_usd recovers
    nothing, so that no more than the value spent is ever recovered on the order".
- Ladder, three tiers (XF A7: one zero tier):
  - kept before >= T > kept after: value spent x kept before / merchandise total;
  - kept after >= T: proportional;
  - otherwise, including already below before the refund: 0.
- What earlier refunds actually recovered, under the sentence, needs no history: while the kept merchandise is at or
  above T, every earlier refund recovered its proportional share; once it is below, the whole value has been taken.
- Figures that net earlier refunds of their own units (u, h, s):
  - each counts as the refund of those units, made after every other refund of the order ("kept before" leaves those
    units out of the merchandise refunded);
  - that convention is exact while the order still qualifies, or when those units' refunds are the order's most recent;
  - where the order is already below T and some of the units were refunded, the policy fixes the figure only if no
    seller refund and no guarantee reimbursement on the order is dated after the most recent return refund on the
    units' line. Otherwise it fixes nothing and the base rule stands. Bindings: *_cov_last, *_order_refund_last,
    *_order_reimb_last, *_settles; the result is gated by *_settles.
  - Without this guard, an interleaved history (unit A refunded, another refund crosses, then the claim) could recover
    more than the value spent.
- R5-2, in market_ext_keepit_unit_refund: "the order's units are the units bought across its lines" now sits in the
  return-shipping keep-back factor sentence, and r_order_units is that factor's binding. The plain order sentence is
  now "The order's merchandise total is the sum of its line amounts.".
  - A3 sweep, other policies: order units are read by both shipping factors (allocation and set-off), so they stay
    plain; merchandise total is read by promo, shipping and keep-back, so it stays plain; kept units are read by line
    pricing and partial credit in u, h, r and s, and owned by partial credit in g, n and q.
- Probes:
  - P1c: the claim now recovers nothing; the figure is the route's.
  - Mirror: platters cross first, the rug reimbursement recovers nothing, and the total equals the value spent.
  - Two-refund totals on a produced crossing world, with seeded unit refunds re-priced in date order under the
    sentence, in both grant orders: both totals equal the value spent.
  - Every earlier probe was re-run (table below).
- Scored figures: unchanged (every task computation takes the proportional tier).
- XF re-check:
  - A1/A3/A4: factor read-sets are clean; the guard reads only promo-factor and plain bindings.
  - A8: the ladder text equals the compute.
  - B12: one reading.
  - B13: verbatim sweep clean.
  - C19: guard out of scope restates base.
  - F27: seeds unchanged.
- Residual (not raised by the audit; noted for the coordinator): XF D20, zero figures inside waits.
  - In producible crossing worlds, a whole-remaining recovery or a full guarantee room can drive a prerequisite
    figure (keep-it refund, grant) to 0.00, and the positive-amount tools cannot book it.
  - It does not occur on either task world (all scored figures positive).
  - The room part predates this round.
- Probe table:

| policy | case | kind | figure | expected |
|---|---|---|---|---|
| u | A2: second request on the claimed line refunded + extra partial refund | second rec | 364.3 -> 0 | 0: two requests on the line, out of scope; base claim amount stands |
| h | A3: later partial-offer request on the claimed line | decoy | 251.54 -> 0 | 0: two requests on the line, out of scope; base decision clause stands |
| g | a return request on the claimed espresso line | second rec | 1871.34 -> 0 | 0: the claimed line must carry no request |
| g | seller refunds one claimed unit after filing | second rec | 1871.34 -> 910.42 | in scope; one unit open, set-price-with-refunds tier |
| n | a return request on the claimed rug line | second rec | 2097.33 -> 0 | 0: out of scope |
| q | a second request on the platter line | second rec | 367.2 -> 0 | 0: out of scope |
| s | declined second request on the returned bowl line | second rec | 5.98 -> 0 | 0: settled with nothing booked |
| s | top-up already booked (0-unit entry) | second rec | 5.98 -> 0.0 | 0.00 after its own booking |
| h | 0-unit top-up decoy on the claimed line | decoy | 251.54 -> 251.54 | unchanged: not a unit refund (amount filter quantity=0, 0 units) |
| u | same-day second authorization recorded later (other line) | tie | 364.3 -> 364.3 | unchanged: the first recorded counts |
| u | order with 10 lines (zero-priced filler lines) | boundary | 364.3 -> 364.3 | in scope (10 lines) |
| u | order with 11 lines | boundary | 364.3 -> 0 | 0: out of scope |
| u | cancellation refund of a dripper adds to merchandise refunded | second rec | 2900.35 -> 2934.55 | + one dripper at its set price |
| u | espresso claim decided other than granted | decoy | 2900.35 -> 981.35 | its units no longer count |
| u | threshold = merchandise kept after (1734.7) / one cent above | boundary | 364.3 -> 329.84 | at the threshold proportional; above it the whole remaining value |
| h | threshold = merchandise kept after (4085.95) / one cent above | boundary | 251.54 -> 170.36 | at the threshold proportional; above it the whole remaining value |
| g | threshold = merchandise kept after (2441.5) / one cent above | boundary | 1871.34 -> 1822.84 | at the threshold proportional; above it the whole remaining value |
| r | threshold = merchandise kept after (4326.3) / one cent above | boundary | 26.21 -> 0.0 | at the threshold proportional; above it the whole remaining value |
| q | threshold = merchandise kept after (2410.18) / one cent above | boundary | 367.2 -> 319.08 | at the threshold proportional; above it the whole remaining value |
| n | threshold = merchandise kept after (2786.38) / one cent above | boundary | 2097.33 -> 2041.7 | at the threshold proportional; above it the whole remaining value |
| s | threshold = merchandise kept after (4914.38) / one cent above | boundary | 5.98 -> 0.0 | at the threshold proportional; above it the whole remaining value |
| u | producible scaled world (merchandise total 1990.73, kept before 1001.0, after 686.12) | tier reach | promo -> 50.28 | whole remaining value: kept before >= 1000 > kept after |
| h | producible scaled world (merchandise total 1086.96, kept before 1001.0, after 882.41) | tier reach | promo -> 92.09 | whole remaining value: kept before >= 1000 > kept after |
| g | producible scaled world (merchandise total 1155.4, kept before 1001.0, after 560.47) | tier reach | promo -> 86.64 | whole remaining value: kept before >= 1000 > kept after |
| r | producible scaled world (merchandise total 1155.4, kept before 1001.0, after 993.15) | tier reach | promo -> 86.64 | whole remaining value: kept before >= 1000 > kept after |
| q | producible scaled world (merchandise total 1799.28, kept before 1001.0, after 865.85) | tier reach | promo -> 55.63 | whole remaining value: kept before >= 1000 > kept after |
| n | producible scaled world (merchandise total 1020.17, kept before 1001.0, after 567.56) | tier reach | promo -> 98.12 | whole remaining value: kept before >= 1000 > kept after |
| s | producible scaled world (merchandise total 1001.0, kept before 1001.0, after 982.2) | tier reach | promo -> 100.0 | whole remaining value: kept before >= 1000 > kept after |
| u | no promotional card | absent | 364.3 -> 377.12 | no recovery, no error |
| h | no undecided claim (selector None) | None | 251.54 -> 0 | 0, no error |
| r | no refund-without-return answer (selector None) | None | 26.21 -> 0 | 0, no error |
| q | line recorded with 0 units | zero-div | 367.2 -> 331.46 | no division error |
| u | cold brew request dated 2026-09-28 | date edge | 364.3 -> 364.3 | day 14: half the maximum |
| u | cold brew request dated 2026-09-29 | date edge | 364.3 -> 284.69 | day 15: the maximum |
| q | P1c: seller refunds both rugs (whole remaining taken); NAD claim kept before 658.38 | R5-1 | 367.2 -> 374.72 | promo 0: already below before the refund -> nothing |
| h,g | produced crossing world: grinder grant then espresso grant [('h', 92.09, 1081.08, 953.01, 0.0, True), ('g', 86.64, 1017.04, 569.46, 358.73, True)] | two-refund | seeded 13.36 -> 100.0 | total recovered on the order never above the value spent (100.00) |
| h,g | produced crossing world: espresso grant then grinder grant [('g', 86.64, 1017.04, 569.46, 358.73, True), ('h', 0, 633.49, 505.42, 0, False)] | two-refund | seeded 13.36 -> 100.0 | total recovered on the order never above the value spent (100.00) |
| n | P1c mirror: platter refund crossed first (seeded recoveries [1.88, 98.12]) | R5-1 | kept before 924.38 -> 0 | 0: already below before the rug reimbursement; total = value spent |

- Sweeps:
  - Rationales: the promotion line now adds "nothing on a refund made once it is already below"; the tier texts and
    quotes come from the generator.
  - Half-cent: no hits.
- Gates: all seven OK.

REWORK round 6: gates 7/7 green

## REWORK round 7 — XF D20, zero figures inside waits (self-flagged in round 6; audit revision_6 CLEAN)
- Verified:
  - Probe A: once the guarantee maximum is reimbursed, the two task 0 grants compute 0.00.
  - Probe B: in a produced crossing world, the whole remaining recovery drives the keep-it refund to 0.00.
  - Probe C: the task 1 not-received grant computes 0.00 once the maximum is reimbursed.
  - In each case the tools accept only a positive amount, so the root's state-form wait ("carries a granted decision
    and its guarantee reimbursement" / "carries its unit refund") could never be met.
- Routes checked:
  - (1) "A zero figure still records the decision and books no money entry." Blocked by the frozen base:
    - market_decide_claim with claim_decision granted triggers market_guarantee_reimburse, whose amount is "Amount
      reimbursed, positive.";
    - market_seller_refund's amount is "Amount refunded, positive, after any restocking fee.".

    So a zero grant cannot be recorded as granted, and a zero keep-it refund has no row to write. No tool is changed;
    every tool still rejects 0.00.
  - (2) Carving the zero case out with a record test. Room exhaustion has a record test, but the promotion-driven and
    partial-credit zeros do not: no record test equals "the figure computes to zero".
  - Applied: XF D20's action-form branch, as the charter already does for the top-up wait. Each resolver's rule now
    says how a settlement is made, zero included, and each wait waits on that settlement:
    - h, g, n: "Northgate settles such a claim by granting it with <the figure> this policy fixes, or, where <the
      figure> comes to zero, with nothing booked, its claim record then keeping no decision.";
    - r: "Northgate settles such a request by booking the keep-it refund this policy fixes, or, where the keep-it refund
      comes to zero, with nothing booked.";
    - waits rewritten in the action form ("... is fixed only after / not fixed until / not fixed before Northgate has
      settled ..."), with each wait's scope list unchanged: u on h, g and r; q on n;
    - fallback_reason on each, conditions and effects updated; a claim settled at zero keeps reserving its claimed amount
      under the room rule, since its record shows no decision.
- Probes, run in both task worlds and in the zero worlds:

| policy | case | kind | result | expected |
|---|---|---|---|---|
| h | A: guarantee maximum already reimbursed on the order | zero | 0.0 | 0.00: settled with nothing booked (claim keeps no decision) |
| g | A: same world | zero | 0.0 | 0.00: settled with nothing booked |
| h | A: the grant tool offered 0.00 | tool | Error: amount_reimbursed_usd must be positive with exactly two decimal | rejected: no 0.00 reimbursement row is written |
| u | A: after the keep-it refund, with both claims settled at zero, the root is computable | wait | 0.0 | figure defined (room exhausted -> 0.00); the waits are met by the settlements |
| r | B: produced crossing world, keep-it refund crosses (promo 86.64) | zero | 0.0 | 0.00: settled with nothing booked |
| r | B: the keep-it tool offered 0.00 | tool | Error: amount_refunded_usd must be positive with exactly two decimal p | rejected: no 0.00 seller refund row is written |
| u | B: root after the zero keep-it settlement and the two grants | wait | 0 | wait met by the zero settlement; the root itself is out of its scope here (its own units refunded before a later refund on an order already below the qualifying total), so it fixes nothing and the base rule stands |
| n | C: guarantee maximum already reimbursed on the order | zero | 0.0 | 0.00: settled with nothing booked |
| q | C: root after the zero not-received settlement and the top-up | wait | 0.0 | figure defined; the wait is met by the zero settlement |
| all | task worlds: prerequisite figures (t0 r,h,g; t1 s,n) | positive | [26.21, 251.54, 1871.34, 5.98, 2097.33] | all > 0: state of the records shows each settlement |

- Unchanged:
  - Scored figures are unchanged, and every prerequisite figure on both task worlds is positive, so each settlement
    books its grant or refund exactly as before.
  - The tools and their docstrings are unchanged.
- Sweeps:
  - Rationale edge lines now name the action form and its fallback; the quotes are filled from policy_source.
  - "Only the return-refund grant settles it" replaces "writes that state".
  - Verbatim and form check:
    - market_ext_return_refund_claim_amount: verbatim clean; forms ['action', 'action', 'action']
    - market_ext_return_refund_claim_reimbursement: verbatim clean; forms []
    - market_ext_unresponsive_claim_reimbursement: verbatim clean; forms []
    - market_ext_keepit_unit_refund: verbatim clean; forms []
    - market_ext_item_condition_claim_amount: verbatim clean; forms ['action', 'action']
    - market_ext_missing_item_reimbursement: verbatim clean; forms []
    - market_ext_restocking_topup: verbatim clean; forms []
- XF re-check:
  - D20: closed as above.
  - Every other point is unchanged by this edit: only prerequisite sentences, conditions, fallback reasons and one
    resolver sentence per prerequisite policy changed.
  - check_extended: action-form edges carry their fallback_reason; no resolver restates a wait sentence.
- Gates: all seven OK.

REWORK round 7: gates 7/7 green

## REWORK round 8 — plan (audit revision_7: R7-1, R7-2, R7-3; coordinator routes)
- Verified:
  - R7-1 holds. The in-force base sentence of market_guarantee_decision says "Northgate decides within
    guarantee_decision_business_days business days after that deadline"; the round-7 zero settlement left the claim
    undecided.
  - R7-2 holds. The h/g/n selectors take the most recent undecided claim of their reason and r takes the most recent
    keep-it answer, so a later out-of-scope or zero entry hides the waited-on one.
  - R7-3 holds. r does not net its own booking.
- R7-1 route:
  - Decision codes checked in db_schema market_events.claim_decision: granted, granted_pending_return,
    denied_not_covered, denied_window, denied_seller_not_contacted, denied_seller_resolved, closed_card_dispute.
  - A zero figure when the guarantee reimbursements already booked on the order reach the per-order maximum fits
    denied_not_covered (the guarantee covers nothing more on the order). This is a record test; the grant tool takes
    0.00 to record that decision and writes no money row.
  - Every other zero cause (promotional recovery, credits, room held by other claims' reservations) has no fitting code
    (denied_seller_resolved is "refunding in full first", which these are not). Such a claim is referred to a human
    representative.
  - The waits return to the state form ("carries a decision on its claim record").
  - Keep-it refund: a seller refund has no decision record. A zero figure because its unit refund already stands is met
    by that refund; any other zero is a referral.
- R7-2 route, coarse exact scope:
  - h, g, n: the order carries exactly one claim of the policy's reason whose claim record shows no decision.
  - r: the order carries exactly one return request answered with a refund without return, and the requested line
    carries exactly one return request. The selector is order-wide, so the exact count is order-level; the line test
    makes the netting exact.
  - The same wording goes in each waiting sentence; out of scope the base rule is quoted verbatim.
- R7-3: r nets every return refund already recorded on the requested line, so it owes nothing after its own booking.
- Sweep of all seven for the three classes: see the record below.

## REWORK round 8 — record
- Generator: gen_r8.py, from gen_r7 via mk_gen_r8.py with every edit anchored and asserted. task_tools.py also
  changed: the three grant tools.
- R7-1, zero-figure claims are decided (h, g, n).
  - The rule now reads: "Northgate decides such a claim by granting it with <the figure> this policy fixes; where <the
    figure> comes to zero and the guarantee reimbursements already booked on the order reach the program's guarantee
    maximum per order, Northgate decides the claim as not covered and books no reimbursement; where <the figure> comes
    to zero otherwise, the claim is not decided in this conversation and is referred to a human representative."
  - The not-covered case is carved out by a record test (booked reimbursements reach the maximum). The other zeros
    (promotional recovery, credits, room held by other claims) have no fitting code and are stated as a referral.
  - The grant tools now take 0.00. It writes claim_decision denied_not_covered on the claim row and one
    market_decide_claim row, and no reimbursement row: the decision trigger fires only for granted, so no 0.00 money row
    is written. Docstring Args and Returns are updated in all three grant tools.
  - The "settled with nothing booked / keeps no decision" sentences and the action-form waits of round 7 are gone. The
    waits are back in the state form ("carries a decision on its claim record"), so a decided claim stops reserving its
    claimed amount.
- R7-2, exact selectors.
  - h, g, n scope: "the order carries exactly one <reason> claim whose claim record shows no decision" (COUNT == 1).
  - r scope: "the order carries exactly one return request the seller answered with a refund without return" (COUNT ==
    1, the selector being order-wide), plus "the requested line carries exactly one return request".
  - The same wording is in each waiting sentence (u on h, g, r; q on n), which now opens "Where the order carries
    exactly one ...". Out of scope, each resolver quotes its base clause verbatim, as before.
  - Coordinator route note: "exactly one keep-it request on the line" would not make an order-wide selector exact, so
    the count is order-level and the one-request line test is kept for the netting.
- R7-3, keep-it once.
  - r nets "the return refunds already recorded on the requested line", in the standard method and in the compute.
  - The promotional factor counts those units as covered (cov = their units), so a re-run after its own booking owes
    0.00.
  - A zero caused by the netting is met by the refund already on the line; any other zero is referred.
- Sweep of all seven policies for the three classes:

| policy | zero-figure handling | selector exactness | booked once |
|---|---|---|---|
| u (claim filing, root) | "where the amount claimed comes to zero there is nothing to claim and no claim is filed" (the field meaning is positive) | root, not waited on; persona names the line | NEW: "the requested line carries no return-not-refunded claim" |
| h (grant) | decided not covered at the maximum reached; otherwise referral | NEW: exactly one undecided claim of its reason | decided claim leaves scope |
| g (grant) | same | NEW: same | same |
| r (keep-it) | netting zero met by the booked refund; otherwise referral | NEW: exactly one keep-it answer on the order, one request on the line | NEW: netting of the line's return refunds |
| q (claim filing, root) | same sentence as u | root | NEW: "the requested line carries no not-as-described claim" |
| n (grant) | as h | NEW: as h | as h |
| s (top-up) | settled with nothing booked; action-form wait unchanged (not a claim; no decision record exists for a top-up) | already exact: a single return authorization on the order | already nets top-ups |

- Probes (scratch copies; R7-2 cases include the auditor's four):

| policy | case | kind | figure | expected |
|---|---|---|---|---|
| h | R7-2: second undecided return-not-refunded claim on the order | second rec | 251.54 -> 0 | 0: two undecided claims of the reason, out of scope (base); u's wait 'where exactly one' does not apply |
| g | R7-2: second undecided seller-unresponsive claim | second rec | 1871.34 -> 0 | 0: out of scope; u's wait does not apply |
| n | R7-2: second undecided not-received claim | second rec | 2097.33 -> 0 | 0: out of scope; q's wait does not apply |
| r | R7-2: second keep-it answer on the order | second rec | 26.21 -> 0 | 0: two keep-it answers, out of scope; u's keep-it wait does not apply |
| h | decided decoy claim of the same reason (denied_window) | decoy | 251.54 -> 251.54 | unchanged: decided claims are not counted or selected |
| r | R7-3: keep-it refund re-evaluated after its own booking | once | 26.21 -> 0.0 | 0.00: the line's return refund is netted |
| h | grant re-evaluated after its own booking | once | 251.54 -> 0 | 0: no undecided claim of the reason |
| g | grant re-evaluated after its own booking | once | 1871.34 -> 0 | 0 |
| u | claim filing re-evaluated after its own filing | once | 364.3 -> 0 | 0: the requested line now carries a return-not-refunded claim |
| s | top-up re-evaluated after its own booking | once | 5.98 -> 0.0 | 0.00 |
| n | grant re-evaluated after its own booking | once | 2097.33 -> 0 | 0 |
| q | claim filing re-evaluated after its own filing | once | 367.2 -> 0 | 0: the requested line now carries a not-as-described claim |
| h | R7-1 A: guarantee maximum already reimbursed on the order | zero | - -> 0.0 | 0.00 with the maximum reached: decided not covered |
| h | A: grant tool given 0.00 | tool | - -> Claim e6c0ae8e-b7d0-4f3e-98b5-76a4a631ce90 decided denied_not_covered (deci | decision recorded, no reimbursement row |
| h | A: claim record after the not-covered decision | state | - -> denied_not_covered, reimburse rows 1 | denied_not_covered; only the seeded reimbursement |
| u | A: root after both claims are decided not covered and the keep-it refund | wait | - -> 0.0 | waits met (decisions recorded); room exhausted -> 0.00, nothing to claim |
| h | R7-1: room held by another undecided claim (no maximum reached) | zero | - -> 0.0 | 0.00 otherwise: referred to a human representative (handoff) |
| r | R7-1 B: produced crossing world, keep-it refund wiped by the whole remaining value | zero | - -> 0.0 | 0.00 with no return refund on the line: referred to a human representative |
| n | R7-1 C: guarantee maximum already reimbursed (task 1) | zero | - -> 0.0 | 0.00 with the maximum reached: decided not covered |
| all | task worlds: prerequisite figures (t0 r,h,g; t1 s,n) | positive | - -> [26.21, 251.54, 1871.34, 5.98, 2097.33] | all > 0: each resolver books its grant or refund |

- Scored figures, factor sensitivities, skips and the problem trees are unchanged.
- XF re-check:
  - C19: new scope tests are coarse exact record tests, with the base quoted out of scope.
  - D20: every wait is satisfiable or referred.
  - E23/E24: tool bodies create their own rows and enforce the documented 0.00 path.
  - E26: the denial writes no trigger-bearing event.
  - B13: verbatim sweep clean.
  - A1: the new plain bindings read no factor binding.
  - Half-cent: no hits.
- Gates: all seven OK.

REWORK round 8: gates 7/7 green

## REWORK round 9 — audit revision_8 (R8-1, R8-2; latent O-r8a) and record
- Verified:
  - R8-1 holds. Probe (a): a large partial refund drives the grinder grant to zero while the order's maximum is not
    reached, so it is a referral, and u's wait could never be met.
  - R8-2 holds. r_line_unit_qty was a plain binding read only by r_promo_recovery.
  - O-r8a holds. A large reservation made a grant's figure depend on the order of the grants.
- Generator: gen_r9.py, from gen_r8 via mk_gen_r9.py.
- R8-1. Each root waiting sentence now ends "; where that claim (that request) is referred to a human representative
  under its own policy, the filing is referred too and nothing is filed". The waits are u on h, g and r, and q on n.
  - The sentence names the referral, not the computed zero.
  - The referral conditions stay record-stated in the resolvers: "maximum reached" decides the claim not covered;
    otherwise the claim is referred.
  - The edge conditions say the same.
- R8-2. In market_ext_keepit_unit_refund, r_line_unit_qty is now a binding of r_promo_recovery. The promotional
  sentence of r carries ", the requested units already refunded being the units the return refund entries on the
  requested line refund". The plain sentence now defines only the return refunds on the line, which the result nets.
- O-r8a (pre-empted per the route). One sentence, verbatim in all three grant rules (room sentence): "claims on one
  order are decided in the order they were filed, earliest first, and of claims filed on the same day the one recorded
  first comes first".
  - Each grant's room now counts only the other undecided claims that come before it in that order, so a later claim
    never reduces an earlier claim's room.
  - Earlier: filed on an earlier date, or filed the same day and recorded first. "Recorded first" is read as the first
    undecided claim of that day (LATEST keeps the first row on ties).
  - For that read to be exact, the grant scopes and the waits carry, as coarse exact tests: "no two claims of one
    reason whose claim records show no decision and no three such claims filed on the day that claim was filed".
  - The task 0 trees still replay identically in all six orders. The grinder claim (recorded first on 10-14) comes
    first by the rule. The task 0 order_uniqueness text and the rationale were updated.
- Probes:

| policy | case | kind | figure | expected |
|---|---|---|---|---|
| h | R8-1 (a): 600.00 partial refund on the grinder line, maximum not reached | zero | 251.54 -> 0.0 | 0.00 with reimbursements below the maximum: referred; u's wait sentence refers the filing too (owed -148.46) |
| r | R8-2: owner of r_line_unit_qty | A3 | plain -> r_promo_recovery | r_promo_recovery |
| h | O-r8a: espresso claim filed for 2400.00; grinder grant before vs after the espresso grant | order | 251.54 -> 251.54 | equal: the espresso claim (same day, recorded later) comes after it and is not counted |
| g | O-r8a: espresso grant with the grinder claim undecided (reserved) vs decided (reimbursed) | order | 1871.34 -> 1871.34 | the grinder claim comes first; the room counts it reserved, then reimbursed (the rule decides it first) |
| h | same-day tie, espresso claim recorded first and filed for 2400.00 | tie | 251.54 -> 100.0 | the espresso claim now comes first: reserved 2400.0 counted in the grinder room (100.0) |
| h | two undecided claims of another reason (seller-unresponsive) | second rec | 251.54 -> 0 | 0: out of scope; u's wait (same words) does not apply |
| h | third undecided claim filed on the grinder claim's day | tie | 251.54 -> 0 | 0: three undecided claims on that day, out of scope |
| h | decided earlier claim of another reason (denied_window) | decoy | 251.54 -> 251.54 | unchanged: decided claims reserve nothing |
| h | earlier undecided not-received claim filed for 2400.00 | second rec | 251.54 -> 100.0 | room counts it (earlier): reimbursement limited by the room |
| n | task 1: earlier undecided not-as-described claim filed for 2000.00 | second rec | 2097.33 -> 500.0 | room counts it (earlier) |

- Scored figures, factor sensitivities and skips are unchanged.
- Sweeps:
  - Verbatim sweep: clean.
  - The order sentence appears once in each grant rule.
  - The referral clause appears in each of the four waits.
  - Half-cent: no hits.
- XF re-check:
  - A3: no single-factor plain quantity remains in r.
  - A2: the non-commuting grant order is now fixed in the rule.
  - D20: every wait is met or referred, and the root follows the referral.
  - C19: the new tests are coarse exact record tests.
- Gates: all seven OK.

REWORK round 9: gates 7/7 green

## REWORK round 10 — audit revision_9 (R9-1), coordinator route: withdraw the round-9 decision-order pre-emption
- Verified: R9-1 holds. The sentence "claims on one order are decided in the order they were filed …" fixes a
  cross-problem order between the grants without any declared edge, and the auditor's binding copy gives two terminal
  states. The coordinator withdrew the pre-emption that created it.
- Change: gen_r10.py, made by mk_gen_r10.py, is gen_r8 plus exactly the R8-1 and R8-2 edits.
  - R8-1: the referral clause in the four waits, and its edge conditions.
  - R8-2: r_line_unit_qty belongs to r_promo_recovery.
  - Removed:
    - the decision-order sentence;
    - the "come before it in the order of decision" room read and its bindings (*_filed, *_first_same, *_same_day,
      *_n_*, *_y_*, *_res_*);
    - the scope and wait tests "no two claims of one reason … no three such claims filed on the day …".
  - The grant rooms and scopes are again the round-8 reads: every other undecided claim reserves its claimed amount.
  - Checked by diffing gen_r8 against gen_r10: the only differences are the R8-1 and R8-2 lines.
- Task texts re-synced:
  - tasks/0.json order_uniqueness is back to "Each grant's guarantee room counts the other claim either as reserved
    (claimed amount) or as reimbursed, and neither room binds …".
  - rationale0's commute line is back to its round-8 wording.
  - A sweep finds no decision-order text in the charter or the task files.
- Gold: unchanged. Task builders replay all six task 0 orders and both task 1 orders identically; replay_tasks OK.
- Probes:
  - Round-8 probe table re-run: every row identical to round 8.
  - R8-1 probe (a): referral as in round 9.
  - R8-2: owner r_promo_recovery.
  - O-r8a is back to its round-8 latent state (non-binding on both gold worlds), as the coordinator's withdrawal
    intends.
- Gates: all seven OK.

REWORK round 10: gates 7/7 green

## REWORK round 11 — renderer scan STOP render_r1.md (M1, M2) + coordinator P1, P2
- Verified:
  - M1 holds. Both the keep-it and the top-up overwrites retire the same market_returns clause, and each tail ("every
    other seller refund … still follows the return rule") pulls the sibling's refund back under base.
  - M2 holds. Neither replaced_by restated the in-force refund deadline.
  - P1 holds. s_engaged compared against s_restock, which derives from the s_restock_schedule factor.
  - P2 holds. r_req_date was computed and never read.
- Generator: gen_r11.py, from gen_r10 via mk_gen_r11.py.
- M1 + M2: ret_overwrite now names the sibling and restates the deadline. "…; a restocking top-up (keep-it: a keep-it
  refund) on such an order follows its own policy; and every other seller refund, including every refund on an order
  paid with a Northgate Card, still follows the return rule: the seller must refund within seller_refund_business_days
  business days after the return is delivered the price of the returned units less a restocking fee …".
  - Applied to market_ext_keepit_unit_refund and market_ext_restocking_topup (overwrite.replaced_by and the rule).
- P1 (market_ext_restocking_topup):
  - the comparison "withheld above the allowance" moves into the s_restock_schedule factor as its binding
    s_over_allowance, read with its own rate plus the plain withheld amount and price paid;
  - its sentence now ends "; a top-up is owed only where the restocking the seller's unit refunds on the returned line
    withheld is above that percentage of the price paid for the returned units, and otherwise the top-up is settled
    with nothing booked.";
  - s_engaged (plain) no longer reads any factor-derived quantity, and its sentence drops the comparison;
  - the result gate reads s_over_allowance in the same way it reads s_settles (the accepted O-r6 pattern).
- P2 (market_ext_keepit_unit_refund): r_req_date and "and the request date" are removed from the scope sentence.
- Sweep of all seven policies:
  - Dead bindings: none left (scratch AST sweep).
  - Plain scope bindings reading a factor-derived quantity: none left. *_restock and *_owed are assembly.
  - Overwrite sibling tails: the claim-filing pair and the payout trio already name their siblings, and now so does
    the keep-it/top-up pair.
  - In-force content in replaced_by: the decision and card-dispute tails already restate their clauses, and the
    return-rule tails now carry the deadline.
- Probes:

| policy | case | kind | figure | expected |
|---|---|---|---|---|
| s | seller withheld 9.4 on the bowl refund | boundary | 5.98 -> 0 | 0: withheld at or below the allowance (half the maximum on the price paid), settled with nothing booked |
| s | seller withheld 9.41 on the bowl refund | boundary | 5.98 -> 0.0 | engaged (above the allowance); the refunds on the line already cover the refund owed, so 0.00 and settled with nothing booked |
| s | owner of the allowance comparison | A1/A4 | plain s_engaged -> s_restock_schedule | s_restock_schedule; s_engaged reads no factor quantity |
| r,s | keep-it answer on the rug line and the bowl top-up on one order | siblings | 5.98 -> [1918.2, 5.98] | each follows its own policy (tails name the sibling); the top-up unchanged |
| r | r_req_date binding present | dead | yes -> False | False |

  - The round-8 probe table re-run is identical.
- Scored figures, sensitivities and skips are unchanged. Gold replays unchanged.
- Sweeps: verbatim sweep clean; half-cent clean.
- Gates: all seven OK.

REWORK round 11: gates 7/7 green

## REWORK round 12 — audit revision_11 (R11-1, XF A3), bounded
- Verified: R11-1 holds. s_withheld was a plain binding, defined in the plain refunds sentence ("… with the units they
  refund and the restocking fees they withheld"), and read only by s_over_allowance in s_restock_schedule.
- Change: gen_r12.py, from gen_r11 via mk_gen_r12.py; 18 diff lines, all in market_ext_restocking_topup.
  - s_withheld is now a binding of s_restock_schedule.
  - Its definition moves into that factor's sentence: "the restocking the seller withheld is the restocking fees
    recorded on the return refund entries on the returned line, and a top-up is owed only where that restocking is
    above that percentage of the price paid for the returned units, and otherwise the top-up is settled with nothing
    booked."
  - The plain refunds sentence drops "and the restocking fees they withheld".
  - No plain binding or sentence uses the withheld fees any more.
- Mechanical A3 sweep (scratch) also lists *_req_date and *_unit. These are left as they are, per the bounded route:
  - *_req_date are attributes of the plain record selection, "the reason and request date the request records" (A4);
  - *_unit, the line's listed unit price, enters each policy's baseline formula ("the listed unit price of their line
    times …"), so it is baseline-defined.
  - The auditor's static sweep names R11-1 as the only member.
- Gold, factor sensitivities and skips are unchanged; both task files rebuilt; verbatim sweep clean.
- Gates: all seven OK.

REWORK round 12: gates 7/7 green
