# Policy-task audit — delivery_claims / charter-global

## charter_global_frozen

- freeze time: 2026-10-05T00:55Z (written before any task GT was revealed; contains nothing derived from a revealed GT)
- auditor: erl-task-policy-audit (independent of the instantiation agent)
- `tasks/delivery_claims/claims.extended.yaml` sha256 `d82fcfd965e04e29ee922ffe4e30388654702b387dc6cba9ce8570aadeea5f7e` (matches HASHES.txt)
- `tasks/delivery_claims/task_tools.py` sha256 `b308df1a097f38bb8535e5528bf13f8de706805e44857dc2646f22314d06a17a` (matches HASHES.txt)
- views: `0.view.json` `7066c748…cc795`, `1.view.json` `2a717ddd…3b115` (match HASHES.txt; each carries only frozen_time, user_scenario, initial_state)
- permitted: blueprint/ (blueprint.yaml, db_schema.json, share_tools.py, products/*.yaml of this scenario), the extended charter, task_tools.py, the two masked views, erlbench/, and the DSL evaluator of the instantiation gate (`skills/erl-task-instantiate/scripts/check_compute.py`, read for primitive semantics only).
- masked / unread: tasks/delivery_claims/tasks/*.json (all fields), worklog, any other scenario, sibling difficulty task dirs and sibling audit dirs.

### entry_conditions (Step 0)
- Gate snapshot `audits/_views/policy_task/delivery_claims/GATES.txt`: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK, CACHE-DIFF INFO; check_traceability deferred to KB stage. Masked views + hashes supplied. Entry conditions satisfied; cited, not re-run.

### policy_conflict_scan
Charter = 12 base policies (verbatim copy: `diff` of the extended file's head against `blueprint/products/claims.yaml` shows only the appended `extended_policies:` key) + 6 extended policies:

| extended policy | subject | target_tool (owner) | claim types it acts on |
|---|---|---|---|
| claims_ext_late_delivery_refund | compensation_issued | book_late_delivery_charge_refund_805d7478 (agent) | Late Delivery |
| claims_ext_late_goodwill | compensation_issued | book_late_delivery_goodwill_699f3402 (agent) | Late Delivery |
| claims_ext_found_parcel_charge | compensation_recovered | authorize_found_parcel_charge_f3b6f0d4 (user) | DNR / Lost in Transit (resolved) |
| claims_ext_wrong_shipment_delivery_refund | compensation_issued | book_wrong_shipment_delivery_refund_014b5564 (agent) | Wrong Item |
| claims_ext_undelivered_parcel_delivery_refund | compensation_issued | book_undelivered_parcel_delivery_refund_8864d5c2 (agent) | DNR / Lost in Transit |
| claims_ext_wrong_item_keep_charge | compensation_recovered | authorize_wrong_item_keep_charge_d92bb3d2 (user) | Wrong Item (approved or resolved) |

- Overlapping subjects: three policies book a `shipping_fee_refund` entry, but each is restricted by claim type in its rule and its tool docstring (Late / Wrong Item / DNR-Lost) — disjoint objects, no two policies decide the same quantity on the same claim.
- Two policies (wrong_shipment, undelivered) supersede the same base clause ("plus the order's shipping fee and surcharge where `refund_includes_shipping_fee`"), each with a claim-type-specific replacement; merged semantics remain unique per claim type (Damaged/Missing keep `refund_includes_shipping_fee: false` and get nothing).
- Two policies (found_parcel, wrong_item_keep) act on recoveries; wrong_item_keep supersedes the base sentences "A recovery is booked only while the claim is in status resolved." and "Goodwill Credit and shipping fee refunds are never recovered." with wrong-item-specific replacements. For found-parcel recoveries the base sentences are then textually superseded but not replaced (see finding O-4); no task world reaches the gap (task 0's found-parcel claim is resolved, and the found-parcel rule restates the no-recovery of goodwill/delivery refunds itself).
- Time anchors: every extended policy counts against `frozen_time` (NOW) or seeded dates; no future-dated or waiting condition.
- Cross-category reads: orders, loyalty, pass, credit, returns — all declared in `cross_category`, all read-only.
- Scope exclusivity (derived from the prerequisite graph, task scopes not yet revealed): tree A = {found_parcel ← late_goodwill ← late_delivery_refund}, tree B = {wrong_item_keep ← wrong_shipment, wrong_item_keep ← undelivered}. The two trees are pairwise disjoint and together cover all 6 extended policies. Verified against each task's `charter_scope` only after reveal (in the task files).

### rule_compute_equivalence
Every compute binding of all 6 policies carries a `compute_basis` quotation that is a substring of its rule; sweep back sentence by sentence:

- late_delivery_refund: tiers of lateness/day-count/basis/repeat/report/tax all present in rule and compute; the multiply-once order ("The shares are multiplied together and applied once") = `refunded_charge`; rounding once at `result`. Weekday/six-day formulas verified: f(d)=5·⌊(n+1)/7⌋+min((n+1) mod 7,5) with n = days since Mon 2024-01-01 counts Mon–Fri days in [2024-01-01, d], so f(delivered)−f(promised) = Mon–Fri days after promised up to and including delivered — matches the rule. **Gap (F-2):** the rule's tier condition "because a free-shipping credit was taken off" has no compute counterpart (`fee_paid > 0 and fee_paid < list_fee`).
- late_goodwill: lateness amount, plan/value/service supplements, relationship and frequency multipliers, refund offset, caps (`annual_issue_cap_usd`, `annual_issue_cap_count`, `min_issue_value_usd` all in the credit charter's Goodwill Credit variant and in `credit_evt_goodwill_issue`) — both directions complete.
- found_parcel_charge: charge base, three courtesies added into one rate, recovery share, label saving, floor 0, rounding — complete. Note (O-5): rule "for the units kept" vs compute `compensated_units` (units compensated on the line); diverges only when fewer units are kept than were compensated.
- wrong_shipment_delivery_refund: covered share (`claimed_units*2 >= order_units and claimed_units < order_units` = "at least half … but not all"), basis, repeat share, tax — complete. Same F-2 gap on "because a free-shipping credit was taken off".
- undelivered_parcel_delivery_refund: trace basis, counted report days, report share, other-order history share (`XCOUNT(all) − XCOUNT(this order)` = "on the customer's other orders … each refund entry counted once"), tax — complete.
- wrong_item_keep_charge: keep base, four courtesies into one rate, label, carried-back delivery share, floor, rounding — complete. Note (O-5): `settled_returns_12m` filters `status='settled'`, rule says "returns settled in the trailing 12 calendar months" (a settled-then-closed return would differ); `kept_units` = compensated units as in found_parcel.
- All factor ladders: every `factors[].ladder` tier is a sentence of the rule and a branch of its `decides` binding, and vice versa (checked per factor; see factor_ladders).
- Rounding: `RND` = Python `round(float, 2)` while docstrings and rules say "half up"; diverges only on exact half-cent floats (O-6).

### action_binding_and_uuids
- 6 policies ↔ 6 tools, each `(target_tool, computes=amount_usd)` claimed exactly once.
- uuid8s: 805d7478, 699f3402, f3b6f0d4, 014b5564, 8864d5c2, d92bb3d2 — no shared prefix, no sequence, no reuse across tools.
- Docstrings: no tool names another tool, carries a sequence position or an ordering word (before/after/first); "has turned up", "has been approved" describe the object's state, not an order among writes. No docstring adds a confirmation, review or wait.
- Function bodies (all six): `ctx.make_id` → `ctx.find("delivery_claims", claim_id=…)` only to copy `customer_id` ("no check") → `ctx.create("claim_events", …)`. No branch refuses, errors or hints on any prerequisite; none writes `order_payments`, `credit_instruments` or changes claim status.

### prerequisite_graph
- `prerequisite` present on all 6 (three `[]`).
- Edges: late_goodwill → late_delivery_refund (value_input, gate `delivery_refund_booked`, form state); found_parcel_charge → late_goodwill (state_gate, gate `claim_events.compensation_type`, form action); wrong_item_keep_charge → wrong_shipment_delivery_refund (value_input, gate `delivery_refund_booked`, form state); wrong_item_keep_charge → undelivered_parcel_delivery_refund (state_gate, form action).
- Every `problem` is an extended policy id of this file, none a base policy, none self. Graph acyclic (two trees, depth 2 and 1).
- Each `policy_source` located verbatim in its own policy's rule (string search over the folded rule text: all four found).
- `form`/`fallback_reason`: present exactly on the two action-form edges.
- value_input gates name real compute bindings (`delivery_refund_booked` exists in both late_goodwill and wrong_item_keep compute). state_gate gates name a field (`claim_events.compensation_type`) rather than an `eligibility` id — the extended policies carry no eligibility block (O-3, no consequence: the gate is stated by the rule sentence).
- `resolved_by` = the depended-on policy's `target_tool` on all four edges; `effect` is consistent with the tool body (a `claims_compensation_issued` row is created on the named claim, which raises `SUM(... shipping_fee_refund)` for the value_input edges).
- No authoring-viewpoint phrasing ("in this task", "at the opening") in any prerequisite field.

### prerequisite_sentences
1. late_goodwill: "The Goodwill Credit on a Late Delivery Claim is fixed only after any delivery-charge refund owed on the claim stands on it as a compensation entry." — connective "only after"; state form (a compensation entry standing on the claim — `claim_events` row of type shipping_fee_refund, which the docstrings call the "delivery-charge refund … shipping-fee-refund compensation entry"); no tool/id/snake_case; strength "any … owed" = condition (including the fee-0 none-owed case). Exactly one write of this difficulty books a delivery-charge refund on a Late Delivery Claim: late_delivery_refund (the other two refund tools are restricted to Wrong Item and DNR/Lost by rule and docstring). The depended-on rule does not restate the sentence. Derivation: sentence → "which write puts a delivery-charge refund on a Late Delivery Claim?" → claims_ext_late_delivery_refund's first sentence ("An approved Late Delivery Claim on an order whose effective shipping fee was above 0.00 is owed a delivery-charge refund, booked as one shipping fee refund entry on the claim") → single reading.
2. found_parcel_charge: "A found-parcel charge is not taken until the compensation owed on each of the customer's other approved claims has been booked." — connective "not taken until"; action form; fallback_reason tested: a state form would have to name "each other approved claim carries the entries owed on it", which more than one write brings about (for a Late claim both the refund and the goodwill), so it would fail the one-write test of the state form — the fallback is justified. Derivation: sentence + `delivery_claims.status = approved` rows + each depended-on rule's "is owed" first sentence → the set of owed bookings, unique per world.
3. wrong_item_keep_charge (a): "The keep charge for a wrong item is fixed only after any delivery-charge refund owed on its claim stands on the claim." — as 1; the unique write on a Wrong Item Claim is wrong_shipment_delivery_refund.
4. wrong_item_keep_charge (b): "A wrong-item keep charge is taken only after the compensation owed on each of the customer's other approved claims has been booked." — as 2; fallback justified on the same ground.
- No rule carries a second wording, tool name or other policy id for its dependency; no depended-on rule restates the sentence.
- Undeclared cross-problem orders: none in extended rules. Base rules carry cross-problem orders ("the agent opens a carrier trace before the claim can be decided"; "Every type in `required_evidence` must be logged on the claim before it goes to decision") that ground no edge and no task tree rests on them — observation O-2.

### override_declarations
Sentence-by-sentence against each `base_policy_refs` entry:

- late_delivery_refund vs claims_evt_compensation: "made whole by its `default_resolution`" (Late: shipping_fee_refund) — follows; "A Late Delivery Claim refunds the effective shipping fee and surcharge paid on the order;" — handled differently, **declared** (overwrite 1); "when that fee was 0.00 … Goodwill Credit … instead" — follows (fee 0 → no refund); "Compensation is booked only while … approved" — follows; tender/timing — follows. vs claims_evt_decision: approval criteria, cap 1500 — follows (refund never approaches the cap).
- late_goodwill vs claims_evt_compensation: "when that fee was 0.00 because of …, it gives a Goodwill Credit of `late_delivery_goodwill_usd` instead," — handled differently (goodwill also when a fee was paid, amount = make-good top-up) — **declared**; "within the credit charter's Goodwill Credit caps … `goodwill_cap_fallback`" — follows and is restated with `credit_evt_goodwill_issue`'s caps and min issue value. vs claims_evt_decision — follows.
- found_parcel_charge vs claims_evt_recovery: first sentence (charged "for the units kept") — **declared** (amount now worked out); "Charges go to the original card" — follows; "A recovery is booked only while … resolved" — inherited (not overwritten by this policy); "Goodwill Credit and shipping fee refunds are never recovered" — follows (restated in its own rule).
- wrong_shipment_delivery_refund vs claims_evt_compensation: "plus the order's shipping fee and surcharge where `refund_includes_shipping_fee`" — **declared**; all other sentences followed.
- undelivered_parcel_delivery_refund vs claims_evt_compensation: same clause **declared**; the rule also grants the delivery refund "apart from its merchandise refund or reshipment", i.e. on reshipment-resolved claims, which base never paid — covered by the declared replacement text ("The delivery charge of a parcel that never reached the customer is refunded as its own compensation entry"); observation O-4. vs claims_evt_carrier_trace: trace-result semantics followed (delivered_confirmed tier reachable only by DNR claims, which base does not deny on that result).
- wrong_item_keep_charge vs claims_evt_recovery: three sentences replaced, all **declared** (return-or-charge; resolved-only → approved-or-resolved; never-recovered → carried-back delivery share).
- Disguised forms: no anonymous intermediate (every intermediate is quoted in compute_basis to the extended rule); no 0/1 multiplier zeroing a base-fixed amount (wrong_shipment's covered-share 0 tier reproduces base's "no shipping refund on a Wrong Item Claim", it does not zero a base amount); no dropped branch. No author note calls a base output a "wrong value".

### factor_ladders
| policy | factors (effect) | param / method | multi-source factor | cross_difficulty |
|---|---|---|---|---|
| late_delivery_refund | lateness_share (P), delivery_day_count (M), guarantee_refund_basis (M), repeat_refund_share (P), reporting_share (P), refunded_delivery_tax (M) | 3 / 3 | guarantee_refund_basis (orders fee vs list fee AND loyalty tier) | loyalty |
| late_goodwill | lateness_amount (M), unlimited_plan_supplement (P), order_value_supplement (P), service_supplement (P), shopping_relationship (P), goodwill_frequency (P) | 5 / 1 | shopping_relationship (order_lines spend AND orders count) | credit |
| found_parcel_charge | seasonal_charge_base (M), loyalty_courtesy (P), engagement_courtesy (P), service_courtesy (P), recovery_share (P), label_saving (P) | 5 / 1 | seasonal_charge_base (order age AND line price type) | loyalty (×2) |
| wrong_shipment_delivery_refund | covered_share (P), wrong_shipment_refund_basis (M), wrong_shipment_repeat_share (P), wrong_shipment_tax (M) | 2 / 2 | wrong_shipment_refund_basis | loyalty |
| undelivered_parcel_delivery_refund | trace_refund_basis (M), report_day_count (M), report_share (P), claim_history_share (P), parcel_charge_tax (M) | 2 / 3 | none (tax tier 1 single-source) | none |
| wrong_item_keep_charge | seasonal_keep_base (M), keep_discount (P), return_record_courtesy (P), express_keep_courtesy (P), unlimited_keep_courtesy (P), keep_label_saving (P) | 5 / 1 | seasonal_keep_base | loyalty, returns |

- All ladders have ≥3 tiers stated in the rule and implemented in compute; bindings disjoint within each policy; every `decides` is an input, never `result`; every fall-through equals the factor's `baseline`; every `baseline` matches what `baseline.rule` states (or is silent on, with the fall-through as default) for that input.
- Labels: `method` factors change the formula (calendar vs weekday counting; list fee vs fee+half-credit vs fee; per-day accrual vs multiplied default; unit-price-less-markdown-without-tax vs compensation-less-markdown vs compensation; no tax vs proportional tax). `parameter` factors substitute numbers. Honest.
- Distinct outcomes: no ladder has two tiers selecting the same value or method.
- **F-1 (unreal ladder, delivery_day_count of late_delivery_refund):** tier 2 "the service delivers on Saturdays and is not Same-Day Courier" is empty for every claim reaching this write — see findings.
- **F-3 (unreal ladder, the three tax factors refunded_delivery_tax / wrong_shipment_tax / parcel_charge_tax):** the fall-through gives no tax to orders shipped to a `taxable_share_states` state that carried no gift-card lines — see findings.
- Realism observations (not demonstrable as unreal): the list-fee basis tiers (guarantee_refund_basis, wrong_shipment_refund_basis, trace_refund_basis lost_confirmed) can make a "refund" of a delivery charge exceed the charge actually paid (O-7); found_parcel's service_courtesy discounts a recovery charge by the speed of the original service — weak business motive but not demonstrably unpublished (O-7).

### findings

**F-1 — SOURCE-FACTOR RED (charter-global; bears on task 0)**
- symptom: `claims_ext_late_delivery_refund.factors[delivery_day_count]` declares three tiers, but only two can ever be taken.
- root cause: tier 2 ("the service delivers on Saturdays and is not Same-Day Courier") is a condition no approved Late Delivery Claim can satisfy.
- evidence: orders charter variant parameters — `weekend_delivery: true` only for Economy Ground and Same-Day Courier; `delivery_date_guaranteed: true` only for Expedited 2-Day, Next Business Day, Same-Day Courier. Claims base `variants[Late Delivery Claim].entry_gate.service: "a service with delivery_date_guaranteed"` and `claims_evt_decision`: "A Late Delivery Claim is approved only for a service whose `delivery_date_guaranteed` is true". The only Saturday, non-Same-Day service (Economy Ground) is not guaranteed.
- demonstrated consequence: for the population reaching this write the ladder is {Expedited 2-Day, Next Business Day → Mon–Fri count; Same-Day Courier → calendar count}: two live tiers, below the three-tier floor; the "Monday-to-Saturday" method is never applied. (The same ladder in `claims_ext_undelivered_parcel_delivery_refund.report_day_count` is live: DNR/Lost claims can be on Economy Ground.)
- affected: claims.extended.yaml, `claims_ext_late_delivery_refund` rule sentence "for a service that delivers on Saturdays other than Same-Day Courier …", `factors[delivery_day_count].ladder[1]`, compute `counted_days_late`.

**F-2 — SOURCE-POLICY (charter-global rule/compute non-equivalence; no consequence in tasks 0/1)**
- symptom: rule tier condition "where the order's effective shipping fee is above 0.00 but below the list fee of its delivery service because a free-shipping credit was taken off" is implemented as `fee_paid > 0 and fee_paid < list_fee`.
- evidence: `claims_ext_late_delivery_refund.compute.refund_basis`, `claims_ext_wrong_shipment_delivery_refund.compute.shipment_basis`. Orders charter `orders_evt_shipping_fee`: "a plan with a `same_day_discount_pct` takes that percentage off the Same-Day Courier fee"; pass charter: Unlimited Next-Day Annual `same_day_discount_pct: 50`; Same-Day Courier `free_shipping_credit_usd: 0.0`.
- consequence (hypothetical world, not either task's): a Platinum customer on Unlimited Next-Day Annual with a late Same-Day Courier order pays 14.98; rule → "every other case" → basis 14.98; compute → list fee 29.95. Not reachable in task 0 or task 1 (fees there are reduced by exactly the 7.95 free-shipping credit) — recorded as a charter defect, no task RED.

**F-3 — SOURCE-FACTOR RED (charter-global; bears on tasks 0 and 1)**
- symptom: the tax ladders (`refunded_delivery_tax`, `wrong_shipment_tax`, `parcel_charge_tax`) give a taxable-share-state order with no gift-card lines zero tax, but give the same order with any gift-card line almost the full proportional tax.
- evidence: rule text (identical in the three policies): "where the order went to a state in `taxable_share_states` and carried gift-card lines, that same amount is further multiplied by the order's net merchandise less its gift-card lines, divided by its net merchandise; in every other case no tax is added." Compute: `… if ship_state in K('taxable_share_states') and gift_card_merchandise > 0 else 0`.
- demonstrated consequence: a CO order, net merchandise 100.00, no gift-card line → tax 0; the same order plus a 1.00 gift-card line → tax = full proportional amount × 100/101. Tier 2's own method applied to a no-gift-card order gives the full proportional amount (factor 1), so the fall-through treatment for that customer group is not a published business practice: a retailer that taxes delivery in proportion to taxable merchandise does not exempt orders whose merchandise is entirely taxable. The condition "carried gift-card lines" thus divides the taxable-share states arbitrarily; the ladder is unreal for that group.
- affected: claims.extended.yaml — the tax sentence and `factors[refunded_delivery_tax|wrong_shipment_tax|parcel_charge_tax]` of three policies; computes `delivery_tax`, `shipment_tax`, `parcel_tax`.

**Observations (no demonstrable consequence in either task world)**
- O-1 (late_delivery_refund): first sentence says the refund is owed "on an order whose effective shipping fee was above 0.00"; last sentence says a claim whose fee "and surcharge were 0.00" is owed none. An order with fee 0.00 and an Alaska/Hawaii surcharge > 0 sits between the two sentences (compute would book the surcharge). Not reachable in either task (surcharge 0.00 everywhere).
- O-2: base rules state cross-problem orders (trace before decision; evidence before decision) that ground no edge; no task tree rests on them.
- O-3: state_gate edges name a field as `gate`, not an eligibility id; the gate is stated by the rule sentence itself.
- O-4: wrong_item_keep supersedes the general base recovery sentences with wrong-item-only replacements, leaving the found-parcel case textually without the resolved-only sentence; undelivered pays the delivery refund on reshipments too. Neither reachable in task 0 (claim resolved) or task 1 (merchandise_refund resolution).
- O-5: "units kept" vs `compensated_units`/`kept_units`; `status='settled'` filter vs "returns settled". Single-unit lines and no closed returns in both worlds.
- O-6: `RND` is Python float rounding while rules/docstrings say half-up; no derived value lies on a half-cent boundary.
- O-7: list-fee basis tiers can refund more than the delivery charge paid; service_courtesy motive weak. Judgement only.
- O-8: baseline sentences are stated in the rules as unconditional ("The delivery-charge refund … is the order's effective shipping fee and surcharge paid") ahead of the factor sentences that refine them; this is the declared baseline-in-rule structure, and the intro sentence "worked out from … as set out below" resolves it.
- O-9: base event `claims_compensation_issued` declares a trigger to `orders:orders_payment_refunded` (refund_component delivery_claim) for shipping_fee_refund rows, but no task tool writes `order_payments`; a reader who applies the declared trigger to a booking made in the same call would change later repeat/history counts — task-level demonstration in 1.md.

## closing_checklist
Written 2026-10-05 after both task files carry `source_gt_comparison` (reveal 00:58:11Z, after the frozen files were hashed: 0.md `3a093ff3…`, 1.md `0a6cb2cd…`, this file `19941ee3…`; the sections above this heading are unchanged since that hash).

- Task files ↔ tasks: `0.md`, `1.md` one-to-one with tasks/0.json, tasks/1.json; this file alongside; no previous revision exists. Comparison sections: both independent derivations equal GT on every write, owner, order, argument and terminal state — but neither task carries an overall PASS (see below).
- Coverage and scope: 6 extended policies fully covered; task scopes {late_delivery_refund, late_goodwill, found_parcel_charge} and {wrong_shipment_delivery_refund, undelivered_parcel_delivery_refund, wrong_item_keep_charge} pairwise disjoint (checked against each `charter_scope`); task tools and GT closed; uuid8s independent — OK.
- Problem trees: each has 2 prerequisite problems, 1 value_input edge (≥ max(1,1)), a user-owned root write, no cycle; the whole difficulty graph is acyclic — OK.
- Factors: every computation declares a self-sufficient baseline giving a definite non-gold number, and every declared factor bears weight on its task's world — but ladder reality fails: F-1 (late refund delivery_day_count, task 0), F-3 (the three tax ladders, tasks 0 and 1; the task 1 wrong-shipment computation drops to 3 honest factors), F-4 (task 0 cross-difficulty Goodwill Credit history contradicts the orders/claims/credit charters). NOT MET.
- Policy: F-2 is a charter-level rule/compute gap with no consequence in either task world.
- Gates re-run on the final form: not performed — the difficulty does not close (and the audit edits nothing, so the final form is the form gated in GATES.txt).

**Difficulty verdict: does not pass the source-layer audit.** Task 0: SOURCE-FACTOR RED (F-1, F-3, F-4). Task 1: SOURCE-FACTOR RED (F-3). Policy self-consistency, problem tree and unique solution PASS for both tasks.

## revision_2

### charter_global_frozen (r2)
- written 2026-10-05, before any r2 task JSON was opened; nothing here is derived from a revealed GT. Auditor: erl-task-policy-audit.
- `claims.extended.yaml` sha256 `b50dce2e8dae43c53ffcee3e750349a24ef85e98fc85b3e4f2840f000a1638bd`; `task_tools.py` sha256 `4bf6074721f9265eac4bc70fbd1b507d07388610212c0d19beab670724453e81` (both match r2/HASHES.txt; both changed since round 1 → every charter-global section re-derived, nothing carried forward by reference).
- views: r2/0.view.json `a8ec6872…c433`, r2/1.view.json `ffac297c…cbd` (match r2/HASHES.txt). Gate snapshot r2/GATES.txt: all 7 green, traceability deferred — cited, not re-run.
- base section: still verbatim (diff against blueprint/products/claims.yaml shows only the appended key).

### re-derived charter-global checks (r2)
- **policy_conflict_scan:** unchanged structure — 6 policies, 6 tools, claim-type-disjoint objects; scopes of the two trees disjoint and jointly complete. Undelivered refund now restricted to claims "made whole by merchandise refund" ("a claim made whole by reshipment is owed none") — consistent with base `claims_evt_compensation` (delivery charge refunded only alongside a merchandise refund). Found-parcel rule now carries its own "A found-parcel charge is booked only while the claim is in status resolved." — the round-1 gap (O-4) is closed.
- **rule_compute_equivalence:** all compute_basis quotations are substrings of their rules **except two stale ones in `claims_ext_late_delivery_refund`**: `promised_date` → "The days the guarantee was missed by are counted only on the days the delivery service delivers:" and `delivered_date` → "after the promised delivery date up to and including the delivered date;" — the rule was reworded ("are counted on the carrier's delivery days, with the island transit allowance …"; "… up to and including the delivered date, less `island_allowance_days` …"), and neither quoted string occurs in the rule any more (new finding N-1). The bindings themselves remain grounded by live rule text ("from the promised delivery date to the delivered date"), so no quantity is unbased. Everything else: guarantee/wrong-shipment basis now tests `ABS(list_fee − free_credit − fee_paid) < 0.005`, matching "equals the list fee of its delivery service less that service's free-shipping credit (… and nothing else)" (F-2 closed); island tier implemented as `MX(0, weekday_days_late − K('island_allowance_days'))` for Expedited 2-Day to AK/HI = rule; tax tier 2 no longer requires gift-card lines in either face; "units compensated on that line, all of which the customer keeps" = `compensated_units`/`kept_units`; "returns in status settled whose settled date falls in the trailing 12 calendar months" = `status='settled'`, `date_field='settled_date'`; repeat/history counts "as they stand on the orders' payment records" = `XCOUNT` over seeded `order_payments`.
- **action_binding_and_uuids:** unchanged pairs and uuid8s; tool bodies unchanged in effect (create one claim_events row, no prerequisite check, no order_payments write). Docstrings now say "rounded to 2 decimal places (to the nearest cent, on the final figure)" — the half-up wording that RND (Python round) did not honour is gone (O-6 closed). No ordering word, no other tool named.
- **prerequisite_graph / prerequisite_sentences:** the four edges, their sentences, forms, fallback reasons, gates and resolved_by are unchanged; all four `policy_source` strings still locate verbatim in their rules; graph acyclic. Round-1 conclusions stand.
- **override_declarations:** all superseded clauses still verbatim in base, all replacements in the rules. New text checked sentence by sentence: late refund "fee and surcharge together were above 0.00" / "both 0.00" — complementary, closes O-1; undelivered reship exclusion follows base; found-parcel resolved-only restates base. No undeclared override found.
- **factor_ladders (r2):**
  - delivery_day_count (late refund): tiers now {Expedited 2-Day to AK/HI → Mon–Fri less 1, floor 0; any other non-Saturday service → Mon–Fri; otherwise → calendar}. Reachability from orders charter: Expedited 2-Day `available_to_alaska_hawaii: true`, guaranteed, `weekend_delivery: false`; NBD guaranteed, non-Saturday; Same-Day Courier guaranteed, Saturday → all three tiers are taken by approved Late Delivery Claims. Distinct methods; an extended-transit allowance for Alaska/Hawaii is a condition carriers and retailers do weigh for guaranteed delivery. **F-1 closed.**
  - tax ladders (three policies): {delivery-taxing state → proportional tax; taxable-share state → proportional tax × taxable (non-gift-card) share; other → none}. A taxable-share order without gift cards now gets the full proportional amount (share = 1); no discontinuity. **F-3 closed.** Tier 2 is now single-source; the multi-source requirement is still met per task (guarantee/wrong-shipment basis, shopping_relationship, seasonal bases).
  - counts unchanged: late refund 6 (3P/3M), goodwill 6 (5P/1M), found 6 (5P/1M), wrong-shipment 4 (2P/2M), undelivered 5 (2P/3M), keep 6 (5P/1M); every fall-through = its baseline; labels honest.
- **findings (r2):**
  - F-1 closed; F-2 closed; F-3 closed; O-1, O-4, O-5 (rule/compute), O-6, O-9 (rule text now pins the counts to the payment records) closed. O-2, O-3, O-8 unchanged (observations). O-7 judgement unchanged (observation).
  - **N-1 (new, observation — regression introduced by the rework):** two stale compute_basis quotations in `claims_ext_late_delivery_refund` (above). No scored value or tier depends on them, so no RED is demonstrable; it breaks the verbatim-quotation property of check 2 and is likely to fail the deferred traceability gate.
  - **N-2 (new, observation):** the "all of which the customer keeps" wording makes the found-parcel and keep charges defined only for a full keep, while both user-tool docstrings still accept "how many units of that line you keep"; a partial keep has no policy answer. Not reachable in either task (single-unit lines).

### closing_checklist (r2)
Written after both r2 task comparisons (reveal after the r2 freeze hashes recorded in 0.md §revision_2).
- Task files ↔ tasks: 0.md, 1.md one-to-one; round-1 text untouched, revision_2 appended in each file and here.
- Coverage/scope: 6 extended policies covered; scopes pairwise disjoint and checked against each `charter_scope`; tools and GT closed; uuid8s unchanged and independent — OK.
- Problem trees: 2 prerequisite problems each, 1 value_input edge each, user-owned root write, acyclic; difficulty graph acyclic — OK.
- Factors: every computation has a self-sufficient baseline giving a definite non-gold number; 4–6 factors with ≥2 parameter / ≥1 method; per task ≥1 multi-source and ≥1 cross-difficulty (loyalty/credit; loyalty/returns) with seeded, charter-consistent rows; ladders ≥3 reachable, distinct tiers; every factor bears weight on its task's world — OK.
- Policy: no SOURCE-POLICY RED; N-1 and N-2 are observations (N-1 is a regression of the verbatim-quotation property introduced by this rework, expected to surface at the deferred traceability gate).
- Gates on the final form: r2/GATES.txt (coordinator snapshot over the same charter/tool hashes as audited) — 7 green, traceability deferred. Not re-run by the auditor.

**Difficulty verdict (r2): passes the source-layer audit.** Task 0: PASS (F-1, F-3, F-4 closed). Task 1: PASS (F-3 closed). All four relationships PASS for both tasks; open items are observations only (N-1, N-2, O-2, O-3, O-7, O-8, missing pass_plan_changed row, task 1 points ledger).
