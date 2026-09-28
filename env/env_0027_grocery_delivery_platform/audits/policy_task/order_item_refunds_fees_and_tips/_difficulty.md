# Policy-task audit — order_item_refunds_fees_and_tips / charter-global

## charter_global_frozen

- Freeze time: 2026-09-24T23:59Z (UTC). Auditor: independent erl-task-policy-audit agent (not the instantiator).
- Frozen inputs (sha256, re-hashed at audit start and matching the brief):
  - `env/env_0027_grocery_delivery_platform/tasks/order_item_refunds_fees_and_tips/order.extended.yaml` = `51a2f063f359f8ecc665ac75f3534b036a6d98fd2dfae3be67af5ba2ef9731b1`
  - `env/env_0027_grocery_delivery_platform/tasks/order_item_refunds_fees_and_tips/task_tools.py` = `26c1029685fb91b6525dfe9c8462f0db46eb0367e0663bcb62a684f3345978ea`
- Also read: `blueprint/blueprint.yaml`, `blueprint/products/order.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, the parameter lines of `blueprint/products/membership.yaml` (`billing_cycle`, `member_service_fee_rate_pct`). To learn the restricted-expression primitives' semantics (`MONTHS`, `DAYS`, `within_months`, `RND`, `CPARAM`), lines 225-390 of `skills/erl-task-instantiate/scripts/check_compute.py` were read (tooling code with no task content).
- Permitted: the charter (base + `extended_policies`), the tool contracts, the schema. Masked, never opened before this section was written: `tasks/0.json`, `tasks/1.json`, `tasks/order_item_refunds_fees_and_tips/worklog.md`, the scenario `worklog.md`, every field listed as masked in the brief. This section contains nothing taken from a revealed GT.
- Gate snapshot supplied with the brief (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all rc=0; check_traceability deferred because the KB is not published yet). Masked views with their hashes supplied, and the hashes re-checked. Entry conditions are met. The traceability gate being deferred is noted and is not a problem for this audit.

### policy_conflict_scan

Base section: verified verbatim (the parsed `category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies` of the extended file equal `blueprint/products/order.yaml` key for key).

Eight extended policies, and the tool each one writes:

| id | target_tool (owner) | computes | trigger | prerequisite -> |
|---|---|---|---|---|
| order_ext_wrong_item_kept_refund | refund_wrong_item_79d6dec9 (agent) | amount_usd | state_due | [] |
| order_ext_unfound_line_refund | refund_unfound_item_93423917 (agent) | amount_usd | state_due | wrong_item (value_input) |
| order_ext_over_cap_review_amount | register_over_cap_review_9b0d89a0 (agent) | requested_amount_usd | state_due | unfound (value_input) |
| order_ext_limit_review_claim_amount | submit_limit_review_claim_079a4c96 (user) | requested_amount_usd | on_request | over_cap (value_input), unfound (state_gate) |
| order_ext_weight_overage_refund | refund_weight_overage_a9b70a98 (agent) | amount_usd | state_due | [] |
| order_ext_substitution_price_protection | refund_substitution_overcharge_0e292d66 (agent) | amount_usd | state_due | [] |
| order_ext_service_fee_share_refund | refund_service_fee_share_1e350a8d (agent) | amount_usd | state_due | weight_overage (value_input), price_protection (value_input) |
| order_ext_photo_review_claim_amount | submit_photo_review_claim_a5aac31c (user) | requested_amount_usd | on_request | weight_overage (value_input), service_fee_share (value_input) |

The graph gives two components: {wrong_item, unfound, over_cap, limit_review} and {weight_overage, price_protection, service_fee_share, photo_review}. With M=2 each task presumably claims one component. That is inferred from the graph only; the claimed scopes are masked in `charter_scope` and get checked at reveal. The two components share no write, so the scopes can be pairwise disjoint, and together they cover all eight policies.

Overlap and conflict findings:

1. **The per-order self-service cap has no single meaning after the merge (see override_declarations O-2).** Two extended policies supersede the base cap sentence of `order_evt_item_refunds`, but each replacement covers only a line recorded as not found. The cap that applies to any other issue refund on an order (a quality or damaged refund on an as-ordered line, for example) is left undetermined.
2. **The base sentence "A not_found_refunded line is never billed, so it has nothing to refund." (`order_evt_substitutions`) conflicts with `order_ext_unfound_line_refund` and `order_ext_over_cap_review_amount`, and no overwrite declares it (O-1).**
3. **State-due triggers cross the two components.** `order_ext_service_fee_share_refund` fires "When item refunds stand on an order whose service level has service_fee_refund_on_item_refund true". That is true of every service level, so the policy fires on any order where the component-1 refunds (wrong_item, missing) have been booked. Its basis ("the sum of the item refunds standing on the order for missing, damaged, wrong_item and quality issues") reads those refunds as a value. No edge links component 1 to the fee share. So the fee share's value depends on whether it is written before or after the wrong-item and unfound refunds, and the charter states nothing about that order. The same holds for the "order already carries an item refund for a missing, damaged, wrong_item or quality issue" uplift of weight_overage and price_protection. A consequence can only be shown against a world where both components fire, so each task file checks its own world for this.
4. Eligibility, time anchors and terminal states are otherwise compatible. Every item refund stays inside the base completed-order and issue-window gates. The base rolling limits (`order_agg_refund_review`, restated by `order_ext_limit_review_claim_amount`) still apply to the wrong_item and missing refunds that component 1 books, and the charter leaves weight_overage and price_protection out of both caps, consistent with base. Cross-category reads are limited to the membership holding and its ledger, both reachable through `find_memberships` and `find_membership_events` plus the membership charter's plan parameters.

### rule_compute_equivalence

Each binding of each policy was swept against its `compute_basis` quote and back. Every quantity, filter, tier and branch has a verbatim quote, and every factor ladder appears in both the rule and the `decides` binding. The exceptions:

- **E-1 (SOURCE-POLICY RED): the month-window counting convention appears only in `compute`.** Seven policies decide tiers with "within the last N whole calendar months" (N = 6 / 12 / 36): the keep share, unfound cap share, over-cap loyalty, limit-review goodwill, price-protection guarantee, fee-share goodwill and photo-review goodwill. The compute implements this as `XCOUNT(..., within_months=N)`, which keeps a row when `0 <= MONTHS(event_date, NOW) < N`. `MONTHS` counts anniversary months: whole months elapsed from the row date to today, with the current partial month included. No rule sentence and no `compute_basis` quote states this convention. The base charter gives an explicit counting rule for every window it declares (for example "counted in calendar days from the date part of completed_at as day 0 ... inclusive"). Taken literally, "the last 6 whole calendar months" also reads as the six complete calendar months before the current month, which leaves out a fee charged earlier in the current month. The two readings differ whenever a fee falls in the current month, and the tier boundary sits exactly at "at least 6 fees in 6 months". Each task file demonstrates the consequence against its own world.
- E-2 (observation): the rules name "the line" (the claimed line, the line recorded as not found, the approved line, the unapproved replacement, the line sold by weight). The compute aggregates over every line of the order that matches the class filter: `SUM(... item_category='weighted')`, `SUM(... substitution_decision='approved_by_customer')`, `SUM(... item_category='perishable', line_outcome='as_ordered', substitution_decision=None)`. The two agree whenever the order has exactly one line of that class. Each task file checks this.
- E-3 (observation): the over-cap and limit-review fee-part tier 1 in `compute` also requires `oc_plan_rate` / `lr_plan_rate` to be truthy, and the ladder text says "AND a Cartwise+ plan is recorded on the order". The rule only says "when the order carries a service-fee waiver from the member service-fee rate". The plan condition is implied because the rate is "of the Cartwise+ plan recorded on the order".
- E-4 (observation): the rules say "rounded to the cent", and base `order_evt_service_fee` says "Every amount is rounded to the cent, half up". `RND` is Python `round` on a binary float, which is not guaranteed half up on an exact .xx5. Each task file checks whether a scored figure sits on a .xx5 boundary.
- E-5 (observation): the weight-overage rule says "Produce, meat and seafood sold by weight" where base says "Produce, meat and deli". Both select `item_category weighted`, so the scored quantity is the same.
- E-6 (observation): the wrong-item rule caps the refund at "the line's billed charge minus the wrong-item refunds already standing on the order". The inherited base sentence caps it at "the line's charge minus what was already refunded on it" (any reason). The two differ only when another reason is already refunded on that line.

### action_binding_and_uuids

- `(target_tool, computes)`: eight distinct pairs, one per policy. No tool is claimed twice.
- uuid8 tails: 79d6dec9, 93423917, 9b0d89a0, 079a4c96, a9b70a98, 0e292d66, 1e350a8d, a5aac31c. All distinct, with no shared prefix, no sequence and no adjacent values. They look independently generated.
- Tool bodies (`task_tools.py`): each creates exactly one row (`order_events` refund / fee-refund row, or `order_review_requests` row) and checks no policy condition. There is no `ctx.find` on refunds, no guard and no error path. The tool layer does not judge any prerequisite.
- Docstrings: none names another tool or a position in a sequence. Observation: every docstring carries "read from the ... lookup before the call". That is an ordering word, but it refers only to where an argument's value comes from, not to another write. The four refund tools taking `refund_reason` share one enum listing every reason, so the tool does not fix the reason. The policy fixes it.
- Observation: `refund_weight_overage_a9b70a98` and `refund_substitution_overcharge_0e292d66` have identical signatures and effects and differ only in docstring. The binding is unique at policy level.

### prerequisite_graph

- `prerequisite` is filled in on all eight policies (`[]` on wrong_item, weight_overage and price_protection). Every `problem` names another extended id, never a base policy and never the policy itself. The graph is acyclic (two DAGs, see the table above).
- Every `policy_source` was located verbatim in its own policy's `rule`:
  - unfound: "The unfound-line refund is fixed only after every wrong-item refund owed on the order's approved replacements stands on the order." (rule line 2)
  - over_cap: "The over-cap amount is not registered until the refund of the unfound line stands on the order up to the room left under the per-order cap." (rule line 2)
  - limit_review (x2): "A limit-review claim is weighed against the rolling limits only after the refund of every line billed although recorded as not found stands on the order." / "A limit-review claim is registered only once every amount above the per-order self-service cap on the order stands as a submitted over-cap review request."
  - service_fee_share (x2): "... fixed only after the weight-overage refund owed on every line sold by weight and billed above its overage allowance stands on the order." / "... fixed only after the price-protection refund owed on every unapproved replacement billed above its protected price stands on the order."
  - photo_review (x2): "A photo-review claim on a line sold by weight is not registered until any weight-overage refund owed on that line stands on the order." / "A photo-review claim is registered only after the service-fee share owed for the item refunds already standing on the order has been returned as a fee refund."
- Every edge is `form: state` and none carries a `fallback_reason`, which is consistent.
- `kind`/`gate`: each value_input gate is a real compute binding of the blocked policy (`m_granted_on_order`, `oc_missing_granted`, `lr_over_cap_requests`, `sf_wo_refunded`, `sf_pp_refunded`, `ph_line_refunded`, `ph_fee_returned`). The single state_gate (`order_events.refund_reason`, limit_review <- unfound) points at the rolling-limit eligibility test that the rule restates.
- `resolved_by` is the depended-on policy's `target_tool` on every edge, and the tool's effect (a refund row of the named reason, a submitted refund_over_cap request, an item_refund_share fee refund) is exactly the state the condition names.
- `condition` against sentence: see prerequisite_sentences, edge L2, where the sentence is broader than the condition.
- Observation: the `effect` of limit_review <- unfound says "with it the customer's rolling count reaches the limit and the claim can only go to review as the customer's own limit-review claim". General text is asserting a fact about one customer's world, which is true only of a customer with exactly the right number of prior refunds. No literal "in this task / at the opening" phrasing appears. It is recorded as an observation because the field is not rendered to the reader.

### prerequisite_sentences

Four-point test per edge. Every sentence joins the blocked result to what it waits on with an ordering connective ("only after", "not ... until", "only once"), names the waited-on state in record words ("refund ... stands on the order", "stands as a submitted over-cap review request", "has been returned as a fee refund"), and names no tool, no policy id, no snake_case token and no row id.

| edge | sentence -> state | the one write of this difficulty that brings it about | scope vs `condition` |
|---|---|---|---|
| U1 unfound <- wrong_item | every wrong-item refund owed on approved replacements stands | only `order_ext_wrong_item_kept_refund` books refund_reason wrong_item | equal |
| O1 over_cap <- unfound | refund of the unfound line stands up to the room | only `order_ext_unfound_line_refund` books missing on a not-found line | equal |
| L1 limit_review <- unfound | refund of every line billed although recorded as not found stands | same | equal |
| **L2 limit_review <- over_cap** | **"every amount above the per-order self-service cap on the order stands as a submitted over-cap review request"** | `order_ext_over_cap_review_amount` (for the not-found line only) | **broader: the condition names only "the part of the unfound line's value above the per-order room"** |
| S1 fee_share <- weight_overage | weight-overage refund owed on every weighted line billed above its allowance stands | only `order_ext_weight_overage_refund` books weight_overage | equal |
| S2 fee_share <- price_protection | price-protection refund owed on every unapproved replacement above its protected price stands | only `order_ext_substitution_price_protection` | equal |
| P1 photo <- weight_overage | any weight-overage refund owed on that line stands | only weight_overage | equal |
| P2 photo <- fee_share | service-fee share owed for item refunds standing has been returned as a fee refund | only `order_ext_service_fee_share_refund` books item_refund_share | equal |

Derivations, reading only the prerequisite sentence, the records and the depended-on rule:
- U1: the sentence names "wrong-item refund owed on the order's approved replacements". The only rule that owes a wrong_item refund on an approved replacement is the wrong-item kept-refund rule ("When the order entries show that the replacement handed over on a line whose substitution the customer approved is a different product ..."). One reading.
- O1 / L1: "the refund of the unfound line" / "the refund of every line billed although recorded as not found". The unfound-line rule is the only rule that refunds such a line (refund_reason missing, up to the room). One reading.
- **L2 (SOURCE-POLICY RED, finding F-3):** the sentence requires *every amount above the per-order self-service cap on the order* to stand as a submitted over-cap review request. The depended-on rule registers an over-cap request only for "a line recorded as not found". Once the per-order room is used up, any further issue refund on the same order (the very claim the limit-review rule prices, a perishable line handed over as ordered) is also an amount above the per-order cap. Read literally, the sentence then requires an over-cap request for that amount too, and no policy prices one. The sentence says more than the edge's condition. Task 0 demonstrates the consequence.
- S1, S2, P1, P2: each names the refund kind that only one rule books. One reading each.
- No rule restates another policy's prerequisite sentence. No rule names a tool or policy id. The depended-on rules do not restate the sentences.
- Observation: `order_ext_over_cap_review_amount` also opens with "When the refund of a line recorded as not found stops at the room left under the per-order self-service cap, ...". That is the policy's trigger, and it doubles as a second wording of edge O1. It adds no new order.
- Observation (undeclared-order candidates, no ordering connective): the fee-share basis and the weight_overage / price_protection "order already carries an item refund" uplifts read issue refunds that component-1 writes produce, with no declared edge (see policy_conflict_scan item 3).

### override_declarations

Swept sentence by sentence against each `base_policy_refs` entry.

- `order_evt_item_refunds`:
  - The sentence "pays back that line's charge for the affected units at the billed unit price" is overridden for wrong-item and declared (wrong_item overwrite). The unfound refund follows it (the line charge), capped by its room.
  - The cap sentence "The agent may grant item refunds on one order only up to the lower of ...; the part above the cap is registered for review with request_type refund_over_cap and is not booked." is superseded twice, by unfound ("The unfound-line refund is booked only up to the unfound-line room ...") and by over_cap ("When the refund of a line recorded as not found stops at the room ..., the agent registers the over-cap amount this rule computes ..."). **O-2 (SOURCE-POLICY RED, F-2):** both replacements speak only of the line recorded as not found. After the merge, the cap on any other issue refund has two readings: (a) the superseded sentence is gone, so nothing caps it, or (b) the base sentence still governs every line the replacements do not cover, so the part above the cap goes to an agent-registered refund_over_cap review. The merged semantics are not unique. Declaring an override does not make several solutions legal.
  - The photo sentence is superseded by photo_review (declared). The window, completed-order, once-per-reason and destination sentences are inherited unchanged.
- `order_evt_substitutions`:
  - The price-protection billing sentence is superseded by price_protection (declared). The replacement baseline refunds only the excess above original × (1 + cap%), where base refunds the whole excess above the original price. That deviation is declared.
  - "A customer-approved replacement is never price-protected" and "A line whose decision is approved_by_customer cannot be rejected afterwards" are inherited. Observation: a wrong-item refund on an approved line is not a rejection, so the two are compatible.
  - **O-1 (SOURCE-POLICY RED, F-1): "A not_found_refunded line is never billed, so it has nothing to refund."** `order_ext_unfound_line_refund` refunds exactly such a line ("A line that the order entries show as billed although the shopper's substitution decision for it records the product as not found ... its charge is refunded with refund_reason missing"), and `order_ext_over_cap_review_amount` prices a review of its remainder. Neither policy's `overwrite` names this base sentence. The quantity it governs, the refund on a not_found_refunded line, is 0 under base and positive under extended. This is an undeclared override. It hides because the base sentence rests on a premise ("never billed") that the extended world breaks.
- `order_agg_refund_review`: both limit sentences are superseded by limit_review with the same test re-worded (declared). "Substitution price protection, weight overage, ... do not count toward or depend on these limits" is inherited and consistent with the weight_overage rule's last sentence.
- `order_evt_weighted_items`: the overage sentence is superseded (declared). The shortfall and no-cap sentences are inherited. E-5 wording noted.
- `order_evt_service_fee`: the proportional-refund sentence is superseded by fee_share (declared). Bounds and "half up" rounding are inherited (E-4).
- `order_evt_cancellation` and `order_evt_on_time_guarantee` (fee_share refs): no sentence is handled differently.
- `order_evt_alcohol_and_returns`: no sentence is handled differently (no alcohol or returned order is priced).
- Disguised forms: no anonymous intermediate, 0/1 multiplier or dropped branch was found beyond O-1 and O-2. The authors never call base output a "wrong value".

### factor_ladders

Per policy: factor, label, `decides`, tiers (all three stated in the rule and implemented in `decides`), whether it is multi-source, and whether it reads another difficulty (xd).

| policy | factor | label | tiers (fall-through = baseline?) | multi-source | xd |
|---|---|---|---|---|---|
| wrong_item | keep_share | parameter | 60 / 75 / 40 (yes) | yes (plan row + ledger) | membership |
| | value_basis | method | orig x units / avg x units / line charge (yes) | no | - |
| | class_points | parameter | 10 / 5 / 0 (yes) | yes (line category + service level) | - |
| | basket_uplift | parameter | 5 / 2 / 0 (yes) | no (both item-line aggregates) | - |
| | standing_credit | parameter | 0.40 / 0.20 / 0 (yes) | yes (completed_at + refund rows) | - |
| unfound | cap_share | parameter | 55 / 60 / cap_pct (yes) | yes | membership |
| | cap_basis | method | +waived / +billed / subtotal (yes) | yes (waiver rows + fee rows) | - |
| | room_topup | parameter | 5.00 / 2.50 / 0 (yes) | yes | - |
| | tenure_allowance | parameter | 3.00 / 1.50 / 0 (yes) | no | membership |
| over_cap | claim_value | method | as wrong_item value (yes) | no | - |
| | fee_part | method | plan rate / billed-fee ratio / none (yes) | yes | membership |
| | loyalty_raise | parameter | 5 / 2 / 0 (yes) | no | membership |
| | days_credit | parameter | 1.00 / 0.50 / 0 (yes) | yes | - |
| | handling_credit | parameter | 0.75 / 0.50 / 0 (yes) | yes | - |
| limit_review | claim_value | method | (yes) | no | - |
| | fee_part | method | (yes) | yes | membership |
| | goodwill_raise | parameter | 10 / 15 / 0 (yes) | yes | membership |
| | days_credit | parameter | 1.50 / 1.00 / 0 (yes) | yes | - |
| | order_load | parameter | 2.00 / 1.00 / 0 (yes) | yes (refund rows + review rows) | - |
| | basket_credit | parameter | 0.75 / 0.50 / 0 (yes) | no | - |
| weight_overage | tolerance | parameter | 0 / 5 / tol_pct (yes) | no (plan and enrolled_date are one row) | membership |
| | price_basis | method | original / average / billed (yes) | no | - |
| | order_uplift | parameter | 10 / 5 / 0 (yes) | yes | - |
| | standing_allowance | parameter | 1.00 / 0.50 / 0 (yes) | yes | - |
| price_protection | margin | parameter | 0 / 10 / cap_pct (yes) | no | membership |
| | **guarantee** | **method (declared)** | x2 / x1.5 / x1 (yes) | no | membership |
| | order_uplift | parameter | 10 / 5 / 0 (yes) | yes | - |
| | standing_allowance | parameter | 1.00 / 0.50 / 0 (yes) | yes | - |
| | handling_credit | parameter | 0.50/unit / 0.25/unit / 0 (yes) | yes | - |
| fee_share | refund_basis | method | all refunds / issue+pp / issue (yes) | yes | membership |
| | method | method | pre-saving fee ratio / basis x rate / billed-fee ratio (yes) | yes | - |
| | goodwill_raise | parameter | 20 / 10 / 0 (yes) | yes | membership |
| | order_uplift | parameter | 10 / 5 / 0 (yes) | yes | - |
| | days_credit | parameter | 0.50 / 0.25 / 0 (yes) | yes | - |
| | tenure_credit | parameter | 0.30 / 0.15 / 0 (yes) | no | membership |
| photo_review | line_value | method | (yes) | no | - |
| | fee_part | method | standing-rate / billed ratio / none (yes) | yes | membership |
| | goodwill_raise | parameter | 10 / 5 / 0 (yes) | yes | membership |
| | **spoilage_credit** | parameter | **2.00 (charge above threshold) / 1.00 (not above) / 0** | yes | - |
| | order_issue_credit | parameter | 1.50 / 0.75 / 0 (yes) | yes | - |
| | tenure_credit | parameter | 2.00 / 1.00 / 0 (yes) | no | membership |

- Bindings are pairwise disjoint within each policy, and each `decides` is an input, never `result`. No two tiers of any ladder select the same value or method. Where a fall-through is a service-level parameter (cap_pct 40/50 against 55/60, tolerance 10 against 0/5, margin 15/20/25 against 0/10), it differs from every other tier on every service level.
- Baselines: each `baseline.rule` is a verbatim subset of its rule, is self-sufficient (it gives a definite number with no factor applied), and its fall-through tiers equal it.
- **F-4 (SOURCE-FACTOR RED): `price_protection_guarantee` is mislabelled `method`.** Its tiers are "the excess is returned twice over / one and a half times / once", which in compute is `pp_excess * pp_guarantee_mult` with `pp_guarantee_mult` in {2.0, 1.5, 1}. That is one formula with a different constant substituted, which is a `parameter` by definition. With the label corrected, `order_ext_substitution_price_protection` has 5 parameter factors and **0 method factors**, below the floor of 1. The other method labels change the inputs or operations (which price is used as the valuation basis, which sum forms the cap basis, a nominal plan rate against a ratio derived from the records, which refund kinds enter the basis) and pass.
- **F-5 (SOURCE-FACTOR RED): `photo_review_spoilage_credit` tier 2 is unreachable, so its ladder is not real.** The photo-review rule applies only to "A damaged or quality issue on a line charged above damaged_photo_required_over_usd of the order's service level". Tier 1 ("the claimed line's charge is above damaged_photo_required_over_usd") therefore holds for every customer who reaches this write: it restates the policy's scope. Tier 2 ("it is not above", 1.00) can never be taken. The live ladder is {2.00 when at least 2 days, 0 otherwise}, which is two tiers, below the floor of three. With this factor struck, the photo policy keeps 5 factors (3 parameter, 2 method), still inside the bounds.
- Ladder-realism observations (no consequence shown, so not red): (i) Five policies carry a credit that grows with the calendar days since completion (standing credit / room top-up / days credit / standing allowance / spoilage credit). This pays more the later an issue is settled inside the report window, and no grocery refund policy is shown to price that way. (ii) Several credits added to a review-claim amount (basket credit, order-load credit, handling credit) have no business counterpart in how a claim's requested amount is formed. (iii) The keep share, room top-up and standing allowance have a part condition, "no <same-reason> refund stands on the order yet". Where the order has a single line of that class, the base once-per-line-per-reason rule makes that condition hold for every customer who reaches the write. With more than one such line it can divide customers, so it is not struck.
- Per-policy bounds after these tests: every policy declares 4 to 6 factors with at least 2 parameter. Every policy has at least 1 honest method except price_protection (F-4). Cross-difficulty factors all read membership (`memberships.variant_name`/`enrolled_date` through CPARAM/CFIELD, `membership_events` through XCOUNT). Component 1 has multi-source factors (keep_share, cap_share, ...), and so does component 2 (fee_share refund_basis, goodwill_raise, ...).

### findings

| id | verdict | summary | bears on |
|---|---|---|---|
| F-1 | SOURCE-POLICY RED | undeclared override of base "A not_found_refunded line is never billed, so it has nothing to refund." by unfound / over_cap | task(s) whose tree has the unfound line (component 1) |
| F-2 | SOURCE-POLICY RED | the base per-order cap is superseded by replacements covering only the not-found line, so the cap on every other issue refund has two readings | component 1 worlds where another issue refund follows the unfound refund |
| F-3 | SOURCE-POLICY RED | the L2 prerequisite sentence ("every amount above the per-order self-service cap on the order") is broader than its condition | component 1 (limit_review) |
| E-1 | SOURCE-POLICY RED | the "within the last N whole calendar months" counting convention lives only in compute (MONTHS anniversary), with no rule or basis quote | every task whose ledger has a fee in the current calendar month or near a boundary |
| F-4 | SOURCE-FACTOR RED | price_protection_guarantee is labelled method but only substitutes a multiplier, so price_protection has 0 honest method factors | component 2 (price_protection) |
| F-5 | SOURCE-FACTOR RED | photo_review_spoilage_credit tier 2 is unreachable (the tier-1 condition restates the policy scope) | component 2 (photo_review) |
| X-1 | observation (demonstrated per task) | state-due fee share fires on any order carrying issue refunds, with no edge to component 1 | worlds where component-1 refunds stand and a service fee is billed |
| E-2..E-6 | observations | single-line aggregation, implied plan condition, float rounding, deli/seafood wording, wrong-item cap base | per task where applicable |

## closing_checklist

Written 2026-09-25, after both reveals, and kept outside the pre-reveal charter-global section above. **The difficulty does not close:** not every task passes all four relationships.

| item | status |
|---|---|
| per-task files one-to-one with tasks (`0.md`, `1.md`), with `_difficulty.md` alongside | yes (first revision; no older revisions) |
| every comparison section carries a PASS | **no**: task 0 is SOURCE-POLICY / SOURCE-CHAIN / SOURCE-TASK RED; task 1 is SOURCE-CHAIN / SOURCE-FACTOR RED |
| extended policies fully covered; scopes pairwise disjoint | yes. `charter_scope` of task 0 = {wrong_item, unfound, over_cap, limit_review}; task 1 = {price_protection, weight_overage, service_fee_share, photo_review}. Disjoint, and together they cover all 8. **But** fee_share's `state_due` trigger fires in task 0's world anyway (task 0 finding T0-T1) |
| task tools and GT closed; uuid8 independently generated | yes (§ action_binding_and_uuids) |
| each tree: 1–3 prerequisite problems, >= max(n−1,1) value_input edges, an owner=user problem, acyclic; whole difficulty a DAG | yes: task 0 n=3 with 3 VI, root user-owned; task 1 n=3 with 4 VI, root user-owned; two disjoint DAGs |
| every computation: self-sufficient baseline, 4–6 factors with >= 2 parameter and >= 1 method, per task multi-source and cross-difficulty, real ladders, every factor bearing weight against an honest baseline, baseline alone ≠ gold | **no**: price_protection has 0 honest method factors (F-4); photo spoilage ladder not real (F-5); task 1 lacks a tier-deciding near-miss (T1-F3). Every factor of both tasks bears weight and every baseline differs from gold |
| instantiation-stage gates re-run on the final form | not re-run: the artifacts are unchanged since the gate snapshot (the extended yaml and task_tools hashes match the brief), and this audit does not re-run gates itself |

Summary of findings to carry forward:
- Charter-global RED: F-1, F-2, F-3, E-1 (SOURCE-POLICY); F-4, F-5 (SOURCE-FACTOR).
- Per-task RED: task 0 T0-C1, T0-T1, T0-T2, T0-T3, T0-P1; task 1 T1-C1, T1-F1, T1-F2, T1-F3.

## revision_2

### charter_global_frozen (revision 2)

- Freeze time: 2026-09-25T00:20Z (UTC), before either round-2 task file was opened. Auditor: same independent auditor as revision 1.
- Inputs:
  - `order.extended.yaml` sha256 `0cb9c353410b591d898faad3643be353b58b76b2b7941170dd326115395d4f1d`. This is **changed** from revision 1's `51a2f063…`, so every charter-global section below was re-derived in full.
  - `task_tools.py` sha256 `26c1029685fb91b6525dfe9c8462f0db46eb0367e0663bcb62a684f3345978ea`. **Unchanged**, so § action_binding_and_uuids carries forward on the strength of this hash (re-checked below only where the charter's use of the tools changed).
- Base section: re-verified verbatim against `blueprint/products/order.yaml` (all ten top-level keys equal).
- The round-2 gate snapshot (all rc=0, traceability deferred) and the masked views `views_r2/.../task_0.view.json` = `00298784…a59` and `task_1.view.json` = `fc05b0f3…834` were supplied and their hashes re-checked. Entry conditions are met.
- The reworker's closure claims were not treated as evidence. Every item below was checked against the artifact text.
- contamination_disclosure (revision 2): round-1 GT (both `tasks/*.json`, revision 1) was revealed during revision 1, so round-1 gold figures and conventions are known to this auditor. The round-2 `tasks/*.json` were not opened before this section and the two per-task revision-2 derivations were frozen. There was no recursive search into `tasks/`. The anniversary-month convention is now part of the rule text itself, so knowing round-1 GT's convention gives no advantage on it.

### policy_conflict_scan (revision 2)

- Same eight policies, `target_tool`s, triggers and prerequisite graph as revision 1. Changes found in the charter text:
  - wrong_item: added an anniversary counting sentence.
  - unfound: second overwrite of the base not-found sentence; a new sentence keeping the base cap for every other issue refund; the counting sentence.
  - over_cap: second overwrite of the not-found sentence; a new sentence pricing the over-cap part of other refunds "at that part's amount"; the counting sentence.
  - limit_review: replacement text now says "no part of the issue is registered as an over-cap request"; the L2 sentence narrowed to not-found lines; the fee-part plan condition added to the rule; the counting sentence.
  - weight_overage: "deli" restored; the counting sentence.
  - price_protection: margin factor replaced by a method factor "protected unit price" (original / average of original and billed / original x (1+cap)); guarantee relabelled parameter; the counting sentence.
  - service_fee_share (**X-1**): the trigger narrowed to "only once a price-protection or weight-overage refund stands on the order ... an order carrying only missing, damaged, wrong_item or quality refunds keeps its service fee", declared as the replacement of base `order_evt_service_fee`'s proportional-refund sentence. The basis ladder is rewritten (plan & weight-overage refund -> every refund / plan & no weight-overage -> issue + price-protection / no plan -> issue). `result` returns 0 unless a price-protection or weight-overage refund stands.
  - photo_review: spoilage tiers now split on whether the claimed line was billed on more weight than requested; the fee-part plan condition is in the rule; the counting sentence.
- Scopes: still two disjoint components covering all eight policies.
- **Cross-component trigger (revision-1 X-1 observation, the root of T0-T1):** under the narrowed trigger, component-1 refunds (wrong_item, missing) alone no longer make the fee share due. The state-due crossing into component-1 worlds is **closed**.
- Per-order cap (revision-1 F-2): the unfound rule now says "The unfound-line room governs only a line recorded as not found; every other missing, damaged, wrong_item or quality refund the agent books on the order stays within the lower of self_service_refund_cap_usd and self_service_refund_cap_pct of the order's item subtotal, counting the item refunds already granted, and the part of it above that cap is registered for review with request_type refund_over_cap". The over-cap rule prices that part "at that part's amount". The limit-review replacement says that when a rolling limit is crossed "nothing is booked by the agent and no part of the issue is registered as an over-cap request".
  - For a refund the agent books: the base cap governs, with its part above the cap registered at face amount.
  - For an issue that crosses a rolling limit: nothing is booked and there is no over-cap request, so the whole issue goes to the customer's claim.
  - The two cases do not overlap, because the over-cap sentence speaks only of refunds "the agent books". The merged semantics are unique. **F-2 closed.**
- No new cross-policy conflict was found.

### rule_compute_equivalence (revision 2)

- **E-1 closed.** Every one of the eight rules now carries: "Months are counted by anniversary: between an earlier date and a later date as many whole months have passed as there are monthly anniversaries of the earlier date falling on or before the later date, so a period fee counts as charged within the last N whole calendar months when fewer than N such months have passed from its charge date to today, and a fee charged earlier in the current month is 0 months old."
  - This equals `MONTHS` (whole months, minus one when the later day-of-month is smaller) together with `within_months` (`0 <= MONTHS < N`).
  - The `compute_basis` of every month-window or tenure binding (`wi_plan_fees_6m`, `m_plan_fees_6m`, `m_tenure_months`, `oc_plan_fees_6m`, `lr_plan_fees_6m`, `wo_tenure_months`, `pp_tenure_months`, `pp_plan_fees_36m`, `sf_plan_fees_6m`, `ph_plan_fees_6m`) quotes it, joined by "..." to the tier sentence. Each joined part was located verbatim in its rule.
  - The 12-month bindings quote only the tier sentence. The convention they use is stated once per rule and applies to them.
- E-3 closed: the over-cap and limit-review fee-part tier 1 now reads "... and a Cartwise+ plan is recorded on the order" in the rule.
- E-5 closed: the weight-overage rule reads "Produce, meat and deli".
- E-4 (float `RND` against half up): the rules still say only "rounded to the cent", and `RND` is unchanged. It stays an observation. The worlds are checked for .xx5 boundaries per task.
- E-2 (class aggregation against "the line") and E-6 (wrong-item cap base) were left as they were. They remain observations and are re-checked per world.
- **New observation R2-O1 (a regression introduced by the rework):** `compute_basis.sf_all_refunded` = "the basis is every item refund standing on the order, those included". The rewritten rule reads "... the basis is every item refund standing on the order;" and no longer contains "those included". The quote is no longer verbatim. Its meaning is unchanged because the retained prefix is in the rule and `sf_all_refunded` sums every `order_item_refunded` row, so no consequence can be shown.
- New bindings checked in both directions:
  - `pp_protected_price` against its three tier sentences;
  - `sf_basis` against the new three tiers;
  - `sf` `result`'s `if (sf_pp_refunded + sf_wo_refunded) > 0 else 0` against the trigger sentence;
  - `ph_billed_weight` / `ph_requested_weight` / `ph_spoilage_credit` against the new spoilage sentence.
  All match.

### action_binding_and_uuids (revision 2)

- Carried forward: the `task_tools.py` hash is unchanged. Eight distinct `(target_tool, computes)` pairs, unchanged. No tool body judges a prerequisite.
- Observation R2-O2: `register_over_cap_review_9b0d89a0` now serves two amounts under one policy: the not-found line's computed over-cap amount, and "that part's amount" for any other booked refund above the base cap. The binding is still unique at policy level, and the second use does not arise in either world.

### prerequisite_graph (revision 2)

- The graph is unchanged: the same eight edges, kinds, gates, `resolved_by`, all `form: state`, and acyclic. Every `policy_source` was re-located verbatim in its own rule.
- L2's condition now reads "order_review_requests carries a submitted refund_over_cap request on the order for the part of every line recorded as not found that lies above its unfound-line room", and its sentence is "A limit-review claim is registered only once the part of every line recorded as not found that lies above its unfound-line room stands as a submitted over-cap review request." Sentence and condition now have equal scope. **F-3 closed.**
- The world-specific phrasing in the limit_review <- unfound `effect` ("the customer's rolling count reaches the limit") is unchanged. It stays an observation.

### prerequisite_sentences (revision 2)

- Revision-1 table rows U1, O1, L1, S1, S2, P1 and P2 are unchanged and pass. L2 now passes (above).
- **New observation R2-O3 (X-1 surface):** the fee-share rule's new first sentence, "The service fee billed on an order is shared back with its item refunds only once a price-protection or weight-overage refund stands on the order", joins the fee share to price-protection / weight-overage refund states with "only once". That is a second wording of the dependencies S1 and S2 already carry, and a weaker one (a disjunction, where S1+S2 require every owed refund of each kind).
  - Read alone, it would let the fee share be fixed once either kind stands. But S1 and S2 sit in the same rule and are stricter, and a reader applies both. It reaches the same resolving writes and the same order, so no second terminal state can be shown.
  - Recorded as an observation (a second wording of a declared dependency, with no demonstrable consequence).

### override_declarations (revision 2)

- **F-1 closed.** Both the unfound and the over-cap `overwrite` lists now name `order_evt_substitutions`: "A not_found_refunded line is never billed, so it has nothing to refund." The replacements ("... was never handed over, and its charge is refunded with refund_reason missing ..." / "... carries a charge to refund despite that decision, and the part of it above the room is carried to review by this rule") agree with each other and with the two rules. The merged semantics are unique.
- F-2 closed (see policy_conflict_scan).
- **X-1 (new declared override): legal and unique.** Base `order_evt_service_fee`'s sentence "When items are refunded and service_fee_refund_on_item_refund is true, the service fee is refunded in proportion ..." is named and replaced. After the merge, an order with only issue refunds keeps its fee, and an order with a price-protection or weight-overage refund gets the fee-share refund this rule computes. One reading in every situation.
  - Observation R2-O4: this reverses the treatment the scenario's own base publishes, where the service fee attributable to refunded items goes back on every service level (`service_fee_refund_on_item_refund: true`). It is now withheld exactly for missing / damaged / quality refunds and returned for pricing corrections. Being declared, it is not a policy conflict, and the four relationships give no ground to rule on it beyond noting it.
- The remaining sentence-by-sentence conclusions of revision 1 stand. No other base sentence is newly handled differently: the new "every other refund ... stays within the lower of ..." sentence restates base's cap for non-not-found lines, and the limit-review replacement adds only the "no over-cap request" clause.

### factor_ladders (revision 2)

Changes from revision 1 (every other row is carried forward unchanged and re-checked against the new rule text):

| policy | factor | label | tiers | fall-through = baseline | verdict |
|---|---|---|---|---|---|
| price_protection | protected_price (new) | method | original / avg(original, billed) / original x (1+cap) | yes (`baseline.rule` "The protected unit price is the original unit price times (1 + substitution_price_cap_pct ...)") | method honest: tier 2 draws on a different input (the replacement's billed price), not a new constant |
| price_protection | guarantee | parameter (was method) | x2 / x1.5 / x1 | yes | label now honest |
| service_fee_share | refund_basis (rewritten) | method | plan & wo refund -> all / plan & no wo -> issue + pp / no plan -> issue | yes | all three tiers reachable under the narrowed trigger (tier 2 = plan with only pp standing; tier 3 = no plan); distinct |
| photo_review | spoilage_credit (rewritten) | parameter | >= 2 days & billed weight > requested: 2.00 / >= 2 days & billed <= requested: 1.00 / otherwise 0 | yes | tier 2 now reachable (a weighted line billed at or under its requested weight can still be charged above the photo threshold); the condition no longer restates the policy scope |

- **F-4 closed:** price_protection now has 1 honest method factor (protected_price) and 4 parameter factors.
- **F-5 closed:** the spoilage ladder has three reachable, distinct tiers.
- Observation R2-O5 (realism, no consequence shown): a "spoilage credit" that is higher because more weight was billed than requested has no clear business counterpart. That joins the days-based-credit observations of revision 1.
- Counts: all eight policies have 4–6 factors, at least 2 parameter and at least 1 honest method. Cross-difficulty factors (membership) are present in both components, and so are multi-source factors.

### findings (revision 2 status of revision-1 items; charter-global)

| id | revision-1 verdict | revision-2 status |
|---|---|---|
| F-1 | SOURCE-POLICY RED | **closed** (declared in two overwrites, unique) |
| F-2 | SOURCE-POLICY RED | **closed** (cap on other lines restated; limit-review excludes over-cap) |
| F-3 | SOURCE-POLICY RED | **closed** (L2 narrowed to its condition) |
| E-1 | SOURCE-POLICY RED | **closed** (anniversary convention in every rule and basis) |
| F-4 | SOURCE-FACTOR RED | **closed** |
| F-5 | SOURCE-FACTOR RED | **closed** |
| X-1 (rev-1 observation) | cross-component state-due trigger | **closed** by the narrowed trigger; the narrowing itself is a legal declared override (R2-O3, R2-O4 observations) |
| E-2, E-6 | observations | left; unchanged |
| E-3, E-5 | observations | closed |
| E-4 | observation | unchanged in the charter; per-world check |
| R2-O1..R2-O5 | new | observations only (stale basis quote; dual-use over-cap tool; second wording of S1/S2 in the X-1 trigger; reversal of base service-fee treatment; spoilage realism) |

No new charter-global RED.

### closing_checklist (revision 2)

Written after the revision-2 reveals. **The difficulty still does not close:** task 1 remains SOURCE-FACTOR RED on a residual of T1-F3.

| item | status |
|---|---|
| per-task files one-to-one, `_difficulty.md` alongside, revision 1 preserved verbatim with revision 2 appended | yes |
| every comparison carries a PASS | **no**: task 0 passes all four; task 1 is SOURCE-FACTOR RED (T1-F3 residual on the weight_overage and price_protection computations) |
| extended policies covered; scopes disjoint | yes; the cross-component fee-share trigger is now closed (X-1) |
| tools and GT closed; uuid8 independent | yes (tools unchanged) |
| trees: 1–3 prerequisites, value_input floor, owner=user problem, acyclic | yes for both tasks |
| factors: bounds, honest labels, real ladders, weight, honest baseline, baseline ≠ gold | yes for all eight policies; **near-miss missing for two task-1 computations** |
| gates re-run | the orchestrator's round-2 snapshot (all rc=0) matches the artifacts audited here (hashes checked); not re-run by the auditor |

Per-item status of every revision-1 RED:
- Closed: F-1, F-2, F-3, E-1, F-4, F-5, T0-C1, T0-T1, T0-T2, T0-T3, T0-P1, T1-C1, T1-F1, T1-F2.
- **Not closed: T1-F3**, narrowed to the weight_overage and price_protection computations.

New defects: none at RED level. New observations: R2-O1 (stale `sf_all_refunded` basis quote), R2-O2 (dual-use over-cap tool), R2-O3 (the X-1 trigger restates S1/S2 as a weaker disjunction), R2-O4 (X-1 reverses the base service-fee treatment, declared), R2-O5 (spoilage realism).

Regressions: none in scored values or trees. The only textual regression is R2-O1, which has no consequence.

## revision_3

### charter_global_frozen (revision 3)

- Freeze time: 2026-09-25T04:05Z (UTC), before the round-3 `tasks/*.json` were opened.
- Inputs:
  - `order.extended.yaml` sha256 `a1d2bc84019dc582b84bac45dd58691fa566284c6f4a3c8deb306f9e1cdcd6de`. **Changed** from revision 2's `0cb9c353…`, so the charter-global sections were re-checked.
  - `task_tools.py` `26c10296…`. **Unchanged**, so § action_binding_and_uuids carries forward on the strength of this hash.
- Base section re-verified verbatim.
- Views: `views_r3/.../task_0.view.json` `00298784…` (unchanged from revision 2) and `task_1.view.json` `a3fe7630…` (changed). Both hashes re-checked.
- Gate snapshot supplied (7 × rc=0, traceability deferred).
- contamination_disclosure: round-1 and round-2 GT of both tasks are known from revisions 1–2. The round-3 task files were unopened at this freeze.
- A temporary extract of the extended policies was written into this report directory to support the re-check, and was deleted before this section was written.

### What changed in the charter (re-checked by content, not by the reworker's list)

- All eight extended policies keep the same ids, target tools, triggers, params (identical key/value sets to revision 2), factor lists and labels, and prerequisite edges, kinds, gates and `policy_source` sentences.
- Every revision-2 load-bearing sentence is still present verbatim:
  - the anniversary convention (all 8 rules);
  - "The unfound-line room governs only a line recorded as not found ...";
  - "nothing is booked by the agent and no part of the issue is registered as an over-cap request";
  - the narrowed L2 sentence;
  - the X-1 trigger and the three-tier fee-share basis;
  - the spoilage weight tiers;
  - the protected-unit-price tiers;
  - "Produce, meat and deli";
  - the fee-part plan condition.
- The weight-overage and price-protection rules and `compute` were read in full and are unchanged from revision 2.
- **R2-O1 closed.** `compute_basis.sf_all_refunded` now reads "the basis is every item refund standing on the order", which is verbatim in the rule. A full sweep splitting every `compute_basis` quote on "..." finds every part verbatim in its own rule, for all eight policies.
- **Limit_review <- unfound `effect` observation closed.** It now reads "The rolling-limit test of the claim is taken with the unfound-line refund counted among the customer's issue refunds of the rolling 90 days, which can carry the count or the amount across the limit." That is general text with no world fact.
- Observations carried forward, unchanged in the text:
  - E-2 (class aggregation against "the line");
  - E-4 (`RND` float against half-up; the rules still say "rounded to the cent");
  - E-6 (wrong-item cap base);
  - R2-O2 (dual-use over-cap tool);
  - R2-O3 (the X-1 trigger restates S1/S2 as a weaker disjunction);
  - R2-O4 (X-1 reverses the base service-fee treatment, declared);
  - R2-O5 (spoilage-credit realism).
- New charter-global defects: none. Every revision-2 charter-global closure (F-1, F-2, F-3, E-1, F-4, F-5, X-1 crossing) still holds on the current text.

### closing_checklist (revision 3)

Written after the revision-3 reveals. **The difficulty passes the source-layer audit:** both tasks are PASS on all four relationships.

| item | status |
|---|---|
| per-task files one-to-one, `_difficulty.md` alongside, revisions 1–2 preserved verbatim, revision 3 appended | yes |
| every comparison section carries a PASS | yes (task 0 and task 1, revision 3) |
| extended policies fully covered; scopes pairwise disjoint (trees included); no cross-component state-due trigger | yes |
| task tools and GT closed; independent frozen uuid8 | yes (`task_tools.py` unchanged since revision 1) |
| trees: 1–3 prerequisite problems, value_input floor, owner=user problem, acyclic; the whole difficulty a DAG | yes (task 0: n=3, 3 VI; task 1: n=3, 4 VI; both roots user-owned) |
| factors: 4–6 per computation, >= 2 parameter and >= 1 honest method, multi-source and cross-difficulty per task, real three-tier ladders, weight-bearing against honest baselines, baseline ≠ gold, a tier-deciding near-miss per computation | yes |
| instantiation-stage gates on the final form | the orchestrator's round-3 snapshot (7 × rc=0, traceability deferred until the KB is published) matches the audited hashes; not re-run by the auditor |

Per-item status over all revisions:
- **Closed:** F-1, F-2, F-3, E-1, F-4, F-5, X-1 (crossing), T0-C1, T0-T1, T0-T2, T0-T3, T0-P1, T1-C1, T1-F1, T1-F2, T1-F3 (revision 3), R2-O1, and the effect-wording observation.
- **Standing observations (not grounds for rework):** E-2, E-4, E-6, R2-O2, R2-O3, R2-O4, R2-O5, plus the revision-1 ladder-realism notes.
- New defects in revision 3: none. Regressions: none.
