# Policy-task audit — gift_registry_services / charter-global

## charter_global_frozen

- Freeze time: 2026-10-13T15:51Z (written before any task's GT was revealed; nothing below is derived from a revealed GT field).
- Auditor: independent policy-task auditor (erl-task-policy-audit), revision 1. No earlier revision exists in this directory.
- Frozen inputs (sha256[:16], re-computed at audit start, equal to the brief):
  - `tasks/gift_registry_services/registry.extended.yaml` 4ec3d14ccee4c3d6
  - `tasks/gift_registry_services/task_tools.py` da70fda2a1a6302e
  - `.audit_views/policy/gift_registry_services/0.json` 45730f479e694982, `1.json` 1fdb00c37ae6b1a1
- Read for this section: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py` (finder signatures), `blueprint/products/registry.yaml`, and the parts of `products/loyalty.yaml`, `products/order.yaml`, `products/card.yaml` that the extended policies read (tier params, order fields/triggers, card variant names); the extended charter; `task_tools.py`; the two masked views (`frozen_time`, `user_scenario`, `initial_state` only).
- Masked and unread: everything under `tasks/gift_registry_services/tasks/*.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure), other difficulties' audits, any KB.
- Entry conditions (Step 0): gate snapshot supplied in the brief — check_extended, check_task_tools, replay --check, check_solvability, check_compute, check_grounding, check_cross_fire all OK; check_traceability NOT OK only on `unlock_*_discoverable_tool:tool_name` (KB not rendered) and validate_scenario only "required document not found" (KB not rendered). Both residual reds are the expected pre-render state and are cited, not re-run. Masked views and hashes supplied. Entry conditions met.

### policy_conflict_scan

Policies in force: 12 base policies (verbatim copy, see override_declarations) + 4 extended policies:

| ext policy | subject (event) | target_tool (owner) | computes | base_policy_refs |
| --- | --- | --- | --- | --- |
| registry_ext_completion_redemption (P1) | registry_completion_purchase | redeem_completion_discount_f7189a88 (user) | discount_amount | registry_completion_discount, registry_agg_per_registry_balances |
| registry_ext_missed_rewards_accrual (P2) | registry_rewards_accrual | book_rewards_accrual_4ec6fd92 (agent) | rewards_amount | registry_rewards_rules |
| registry_ext_gift_return_credit (P3) | registry_return_credit | book_return_credit_c9fb6682 (agent) | credit_amount | registry_gift_returns |
| registry_ext_credit_redemption (P4) | registry_credit_use | apply_registry_credit_10dfa5f2 (user) | credit_amount | registry_credit_rules, registry_agg_per_registry_balances |

- Overlapping subjects: none — each extended policy owns one event type; no two policies (base or extended) compute the same scored quantity on the same tool. Base `registry_agg_per_registry_balances` also names registry_completion_purchase / registry_credit_use as subjects; its sentences are compatible with P1/P4 (per-registry counting; P1/P4 read `registry_events` of the one registry).
- Triggers / eligibility / time anchors: P1 inherits base `completion_status` (registry in completion); P3 inherits base `registry_return_deadline` (later-of deadline counted from event_date) and `one_credit_per_return`; P4 keeps "while the registry is active or in completion". P2 has no state gate of its own; the base reversal sentence ("When a linked gift is returned ... before the payout, its accrual is reversed in full") stays in force alongside it (see findings G-3).
- Cross-category read boundary: P1 reads order (registrant's line), card (account charged), loyalty (tier); P2 reads card; P3 reads order `return_requests` and loyalty tier params; P4 reads order and loyalty. All are reads; no extended policy writes outside `registry`.
- Cross-charter write path (observation): `products/order.yaml` declares `order_refund` with `refund_destination: registrant_credit` triggering `registry:registry_return_credit`. So in the scenario there are two writers of a registry credit entry — this difficulty's `book_return_credit_c9fb6682` and the order difficulty's refund. Only the former is in this difficulty's tool module; no conflict inside this difficulty.
- Claimed scope vs. written event types (the brief's question): the claim lists categories [registry] and event_types [registry_return_credit, registry_completion_purchase, registry_event_date_change, registry_visibility_change, registry_cancel, registry_gift_purchase, registry_item_add]. P2 writes `registry_rewards_accrual` and P4 writes `registry_credit_use`, which are registry-category event types not in that list. Judgement: **observation, not a RED.** The category `registry` is claimed by this difficulty alone (no other difficulty's claim lists the category or these event types, so no other difficulty can write them and exclusivity is intact — consistent with check_cross_fire SCOPE OK); the event_types list is a blueprint summary that under-enumerates what the difficulty writes. Conversely five listed event types (event_date_change, visibility_change, cancel, gift_purchase, item_add) have no extended policy; nothing requires every listed event type to be exercised. Affected artifact: `blueprint/blueprint.yaml` difficulties[gift_registry_services].claim.event_types.
- Task scopes (inferred from `user_scenario` only, pre-reveal): task 0 opens on a completion-discount redemption (P1 root), task 1 on applying registry credit (P4 root). Charter prerequisite graph P1→P2, P4→P3 makes the two trees {P1,P2} and {P4,P3}: pairwise disjoint and jointly covering all four extended policies. Final confirmation against `charter_scope` is a post-reveal item and is recorded only in the task files and closing_checklist.

### rule_compute_equivalence

Mechanical sweep (python over the YAML): every `compute_basis` value is a verbatim substring of its policy's `rule`; the compute keys and `compute_basis` keys are identical sets for all four policies; every `baseline.rule` sentence is in the `rule`. Sentence-level sweep back:

P1 registry_ext_completion_redemption
- line_* bindings: CFIELD on the registrant's order line `status='ordered'` — rule: "the registrant's purchase record of that item still in ordered status". If the registrant has more than one ordered line, CFIELD returns one of them; the rule singles out the line by the item the customer names. Per-task check.
- type_pct: `0 if days_on_registry < min else (post_event_item_pct if item_entry_date > event_date else completion_discount_pct)` = the three rule clauses. Equivalent.
- card_pct: three tiers as stated; equivalent.
- circle_pct: compute reads the membership's **current** `variant_name` and `CPARAM` of the current tier; the rule (and loyalty_tier_benefits) says "the tier it holds on the line's purchase date". Compute carries no date handling — an empty promise in the direction rule→compute whenever the tier changed between the purchase date and frozen_time. Observation at charter level (G-4); per-task check of `last_tier_change_date`.
- net_rewards / perk_pct: accruals less reversals, thresholds ≥550 → 4, ≥300 → 2, else 0. Equivalent.
- days_after_event / early_pct: `≤30 → 4, ≤60 → 2, else 0`; a negative day count also falls in "at most the first early window" — consistent with the literal rule.
- discount_found: clearance/doorbuster/final_sale → 0; `sale or unit_price < regular_price` → `MX(0, regular×pct/100 − markdown)`; else `unit_price×pct/100`. The rule's "because a coupon was allocated to it" is not separately testable from the record (any regular-priced line below its ticket) — equivalent on the data model (`unit_price` is defined as selling price after promotions and coupons).
- cap_left / result: `RND(MN(found if units_left ≥ 1 else 0, MX(0, cap − Σ completion entries)), 2)` = "unused part of the cap is applied before the rounding, done once". Equivalent.
- Base sentence inherited but absent from compute: "Items of completion_excluded_classes ... are never discounted" (Fine Jewelry & Watches, Designer Handbags & Luxury). Compute has no class branch; on a line of an excluded class compute returns a positive discount while the inherited base sentence gives none. Latent; per-task check of the line's `variant_name` (G-5).

P2 registry_ext_missed_rewards_accrual
- gift_amount / gift_date: LATEST `registry_gift_purchase` by entry_date — rule: "a registry's most recent guest gift entry when that entry carries no registry rewards accrual entry". Compute does not test "carries no accrual entry"; it is the policy's trigger, judged by the reader. Ties on entry_date are unresolved by both faces (per-task check).
- gift_type_pct, holder_pct, gift_total_pct, gift_pct, accrual_found (taper), result: each tier verbatim in the rule and implemented. `holder_pct` reads `CFIELD('card','variant_name',status='active')` — one row; with two active accounts (one elite, one not) the rule's ladder ("an active Store Card Elite or World Elite Mastercard adds the elite holder rewards bonus") selects elite, compute selects whichever row CFIELD returns. Per-task check (G-6).
- gift_total sums **all** gift entries (returned ones included), exactly as the rule says ("the sum of the amounts of all guest gift entries on the registry").

P3 registry_ext_gift_return_credit
- ret_*: XLATEST over the customer's `return_requests` with `return_status='received'`. Rule: "the registrant's return record in received status". If more than one received return exists, both faces resolve by latest `created_at`; the rule names no tie-break other than the trigger "carries no credit entry". Per-task check.
- waiver_reason, free_ship, restock_waived, return_fee, restock_pct, return_days, late_pct, deductions, taken, result: each implemented as the rule states.
- free_ship / restock_waived read the **active** tier's params; loyalty_tier_benefits says return-shipping benefits are read from "the tier held on the date of the occurrence ... the return date". Same date gap as P1 circle_pct (G-4).
- `restocking_fee_waived` is defined in loyalty.yaml parameter_schema as "Whether the **furniture and mattress** restocking fee is waived"; P3 reads it as a waiver of the registry opened-restocking charge on any class. Second reading available to a KB reader for a non-furniture opened gift with a Diamond/Icon registrant (G-7). Per-task check.
- Base eligibility (deadline, one credit per return) is inherited and not in compute — eligibility, not quantity. Per-task check.

P4 registry_ext_credit_redemption
- line_*, line_completion, payable, item_*, item_stretch, member_*, circle_stretch, days_from_event, period_stretch, stretch, available, result: each tier/clause in the rule and implemented. `available` = Σ return_credit − Σ credit_use − Σ credit_conversion (entries), replacing base "up to the registry_credit_balance" (declared, see override_declarations). Per-task check that the seeded `registry_credit_balance` field agrees with the entries (a reader of base would use the field).

No tier lives only in compute; no rule tier is missing from compute.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: (redeem_completion_discount_f7189a88, discount_amount), (book_rewards_accrual_4ec6fd92, rewards_amount), (book_return_credit_c9fb6682, credit_amount), (apply_registry_credit_10dfa5f2, credit_amount) — each claimed by exactly one policy.
- uuid8s f7189a88 / 4ec6fd92 / c9fb6682 / 10dfa5f2: pairwise distinct, no shared prefix or tail, not sequential; none appears in `blueprint/` (grep). Independently generated: PASS.
- Docstrings: no other tool name, no ordering word placing a call in a sequence (grep for before/after/first/until/prior/once/next: only "after the booking"/"after the payment" describing the returned balance, and "then sees"/"can then spend" describing the effect). No concrete example value in any docstring or Args description (grep for numerals: none beyond "8 digits", "2 decimal places"). Observation: `book_return_credit_c9fb6682` says the credit balance "the registrant can then spend on Marlowe & Finch purchases" — describes the effect, names no tool, not a sequence instruction.
- Tool bodies: none reads a prerequisite state, refuses or hints. `redeem_completion_discount` takes `status` as a free argument and writes nothing to `registries` (its docstring says "the registry's completion discounts used grow by that amount" — true of the measure, which is summed from entries). `book_rewards_accrual` / `book_return_credit` / `apply_registry_credit` update the `registries` balance field by ± the amount. No tool layer gating: PASS.
- No added confirmation/review/wait outside policy.

### prerequisite_graph

- `prerequisite` filled on all four: P1 → [registry_ext_missed_rewards_accrual]; P2 → []; P3 → []; P4 → [registry_ext_gift_return_credit]. Every `problem` names an extended policy of this file, never a base policy, never itself. Graph {P1→P2, P4→P3} is acyclic (two disjoint chains of depth 1).
- `policy_source` verbatim in the blocked policy's own rule: both edges located (python whitespace-normalised substring test: True); neither sentence is restated in the depended-on policy's rule (False for both).
- `form: state` on both edges, no `fallback_reason` — consistent.
- `kind: value_input` on both; `gate` names a real compute binding: P1 `perk_pct` (compute line `perk_pct`), P4 `available` (compute line `available`).
- `resolved_by` = depended-on policy's `target_tool`: book_rewards_accrual_4ec6fd92 (= P2.target_tool), book_return_credit_c9fb6682 (= P3.target_tool).
- `effect`: P2's write adds a `registry_rewards_accrual` row, which `net_rewards` sums → can move `perk_pct`; P3's write adds a `registry_return_credit` row, which `available` sums → bounds P4 `result`. Both effects are real in the compute; whether they move the scored value is per-task.
- `condition` vs the sentence: P1 "On a registry whose type has a registry rewards percent above zero, every registry_gift_purchase entry has a registry_rewards_accrual entry carrying the same purchase_id" = the sentence's "every guest gift entry on a registry whose type earns registry rewards carries its registry rewards accrual entry" — same strength and scope. P4 "Every return record of the registrant in received status for a purchase linked to the registry has a registry_return_credit entry carrying its return_id" = "every registry gift the registrant has returned and the store has received stands on the registry as a registry credit entry" — same.
- No authoring-viewpoint phrasing ("in this task", "at the opening") in any `prerequisite` field.
- Charter-level mismatch to watch per task (G-1, G-2): both conditions quantify over **every** entry/return, while the resolving policies are scoped to **one** object — P2 only to "a registry's most recent guest gift entry when that entry carries no registry rewards accrual entry", P3 to the latest received return (compute XLATEST). Where a world has more than one unmet instance, the edge cannot be closed by the declared resolver. Per-task check.

### prerequisite_sentences

Edge P1 → P2. Sentence: "The completion discount on an order line is fixed only after every guest gift entry on a registry whose type earns registry rewards carries its registry rewards accrual entry."
1. Joins this policy's result ("the completion discount on an order line is fixed") to what it waits on with "only after": PASS.
2. State form: names a record-visible state ("guest gift entry ... carries its registry rewards accrual entry"), in the words of the ledger (registry_gift_purchase = guest gift entry, registry_rewards_accrual = rewards accrual entry); no performer, no tool: PASS.
3. No tool name, policy id, snake_case token or row id: PASS.
4. Strength/scope equal to `condition`: PASS (see prerequisite_graph).
- Writes that can bring the state about in this difficulty: only `book_rewards_accrual_4ec6fd92` creates `registry_rewards_accrual` rows. Exactly one: PASS.
- Derivation (reader's path): the P1 rule says the discount waits on every guest gift entry carrying an accrual entry → the reader lists the registry's `registry_gift_purchase` rows and `registry_rewards_accrual` rows by `purchase_id` (find_registry_events) → finds a gift entry without one → looks for the policy whose rule books "the registry rewards accrual owed on a registry's most recent guest gift entry when that entry carries no registry rewards accrual entry" (P2) → books it → the state holds → P1 computes. Single reading provided exactly one gift entry lacks an accrual and it is the most recent one (G-1).
- No other wording of this dependency in P1's rule; P2's rule does not restate it: PASS.

Edge P4 → P3. Sentence: "Registry credit is not applied to a purchase until every registry gift the registrant has returned and the store has received stands on the registry as a registry credit entry."
1. "not ... until" joins P4's result (credit applied) to the state: PASS.
2. State form, record-visible: return record in received status (`return_requests.return_status = received`) and a registry credit entry (`registry_return_credit`): PASS.
3. No tool/policy id/snake_case/row id: PASS.
4. Scope = condition: PASS.
- Writes in this difficulty that bring it about: only `book_return_credit_c9fb6682` creates `registry_return_credit` rows: PASS (the order difficulty's refund-to-registrant-credit trigger is not in this difficulty's module; observation in policy_conflict_scan).
- Derivation: P4 rule → reader lists the registrant's return records in received status whose purchase is a registry gift (find_return_requests by customer, find_purchases registry_id) and the registry's `registry_return_credit` rows by `return_id` → a received return without a credit entry → P3's rule ("credits to the registry the registry credit owed for a registry gift the registrant has returned and the store has received") → book → P4 computes. Single reading provided exactly one such return is unmet and it is the latest received return (G-2).

Undeclared cross-problem orders in rules: P1 rule — none other. P2, P3 — none. P4 — the payable branch "a line with a completion purchase entry on the registry is paid at its selling price less that completion discount" reads a state P1 writes; it states a branch, not an order ("before/after/until" absent), so it is not an undeclared dependency at charter level. Per-task: if a task's line should carry a completion entry that is absent at the opening, that would be an unstated order (watch in task 1, whose persona says the blender was ordered "with your completion discount").
Base rules stating a cross-problem order: base registry_cancellation_rules ("takes effect when the registrant confirms it") and registry_event_date_rules ("The completion period ... follow the new date") — neither grounds an edge of this difficulty; no tree rests on them. Observation only.

### override_declarations

Sentence-by-sentence over each `base_policy_refs` entry (finding half only; consequences demonstrated per task).

registry_completion_discount (refs of P1):
- S1 "During the completion period the registrant or co-registrant (completion_purchaser) may buy items still on the registry at the completion discount, in the completion_channels." — followed (P1: registrant's own line, in completion status). Channel inherited.
- S2 "The registry is in completion status." — followed.
- S3 "The item was added ... at least completion_item_min_days_on_registry ... and the discount covers at most registry_msr_remaining_requested_quantity units" — handled differently (most recent item entry; post-event item percent; units-left counted over all guest gift entries rather than the measure's not-returned/not-cancelled ones) — **declared** (overwrite #3).
- S4 "Items of completion_excluded_classes, items at completion_excluded_price_types and gift cards are never discounted." — price types followed (clearance/doorbuster/final_sale → 0); classes inherited but unimplemented in compute (G-5). Not overridden, so inherited in full.
- S5 completion percent (type + card bonus + Finch Circle bonus) — handled differently (five-part sum, elite card bonus, active-card condition, registry perk, early bonus) — **declared** (overwrite #1). Finch Circle bonus as restricted to Icon/Platinum/Diamond reproduces base exactly given loyalty.yaml (Member/Silver/Gold registry_completion_bonus_pct = 0).
- S6 "taken on the unit's selling price ... better of coupon, never both" — handled differently (regular price less markdown for sale/coupon lines) — **declared** (overwrite #2).
- S7 cap and remainder — followed (cap_left).
- S8 completion purchase returns do not restore discount or cap — followed (cap_left sums all completion entries).
- S9 completion_quantity_basis / no gift cards — followed.
registry_agg_per_registry_balances (P1, P4): every sentence followed (per-registry counting; P4 draws only this registry's entries).
registry_rewards_rules (P2):
- S1 accrual percent — handled differently — **declared** (overwrite).
- S2 "When a linked gift is returned (by the guest or by the registrant) before the payout, its accrual is reversed in full ...; a return after the payout changes nothing." — not overridden → inherited. P2's trigger books on "the most recent guest gift entry" with no carve-out for a returned gift. If the most recent entry's purchase is returned before payout, the inherited sentence says its accrual nets to zero (accrual reversed in full), so P1's net_rewards would read the accrual minus the reversal. No reversal tool exists in this difficulty. Per-task check (G-3).
- S3–S6 payout test, forfeit, cancellation, payout statuses — untouched, not read by any extended compute.
registry_gift_returns (P3):
- S1 registrant returns a registry gift without a receipt — followed.
- S2/S3 deadline (later of event_date + window and class window from guest's completed_date; inclusive) — inherited as eligibility; not overridden.
- S4 "The return follows the class's condition, method and fee rules, and is credited ... equal to the price the guest paid ... less any fee the class rules deduct ... exchange" — handled differently (registry deductions replace class fee rules) — **declared**.
- S5 one credit per return — inherited.
- S6 completion-discount purchase refunded under ordinary order rules — inherited; per-task check that the return P3 credits is not of the registrant's own completion purchase.
registry_credit_rules (P4):
- S1 "spent ... while active or in completion, up to the registry_credit_balance" — handled differently (stretch division; "registry credit available" from entries) — **declared**.
- S2 conversion, S3 never cash — untouched.
No anonymous intermediate, 0/1 multiplier or dropped branch found beyond the declared overwrites; `units_left ≥ 1` is a 0/1 gate on the amount but it is base S3's own quantity rule restated and declared. No author language calling base output a "wrong value".
Undeclared overrides: none found.

### factor_ladders

Tier params used below: loyalty registry_completion_bonus_pct Member/Silver/Gold 0, Platinum 5, Diamond 5, Icon 10; free_return_shipping false for Member/Silver, true Gold+; restocking_fee_waived true only Diamond/Icon. Registry type params as in the charter `variants`.

P1 registry_ext_completion_redemption — 6 factors (5 `parameter`, 1 `method`); bindings pairwise disjoint; no `decides: result`.
| factor | label | tiers (value) | multi-source | cross_difficulty | in rule + compute |
| --- | --- | --- | --- | --- | --- |
| item_entry_percent | parameter | <min days → 0; entry after event_date → post_event_item_pct 10; else completion_discount_pct | yes (item entry row × order line date × registry event_date) | — | yes |
| elite_card_tier_bonus | parameter | active Elite/World Elite → 8; other active M&F card → completion_card_bonus_pct; else 0 | yes (order line card_account_id × card account) | card | yes |
| circle_tier_bonus | parameter | type grants & active Icon → 10; type grants & active Platinum/Diamond → 5; else 0 | yes (registry type × membership) | loyalty | yes |
| net_rewards_perk | parameter | net ≥ 550 → 4; ≥ 300 → 2; else 0 | aggregate of one ledger | — | yes |
| early_window_bonus | parameter | ≤30 d after event → 4; ≤60 → 2; else 0 | yes (order date × registry event_date) | — | yes |
| markdown_better_of | method | clearance/doorbuster/final_sale → none; sale or below-regular → pct × regular − markdown, floor 0; else pct × selling | single record | order | yes |
- Variant-dependent degeneracy (G-8): `item_entry_percent` tier 2 (10) equals its fall-through for Celebration and Graduation registries (completion_discount_pct 10); `elite_card_tier_bonus` tier 2 (completion_card_bonus_pct) equals its fall-through 0 for every type except Wedding (5). On a Wedding registry all tiers are distinct. Per-task check of the registry type.
- Honest labels: method tiers change the functional form (better-of against regular price vs plain percent on selling price vs none). Fall-through of every factor = its baseline; baseline.rule ("type percent on the selling price", cap, units left, one rounding) is self-sufficient.
- Realism: elite-card and tier bonuses, item-age gating, early-completion and guest-activity perks, and markdown-vs-completion better-of are treatments a department-store registry plausibly publishes. No condition holds of every customer reaching this write.

P2 registry_ext_missed_rewards_accrual — 4 factors (3 `parameter`, 1 `method`).
| factor | label | tiers | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- |
| post_event_gift_cut | parameter | >30 d after event → pct − 5; 1–30 d after → pct − 2; else pct (floor 0) | yes (gift entry date × registry event_date) | — |
| cardholder_rewards_bonus | parameter | active Elite/World Elite → 2; other active M&F card → 1; else 0 | single table | card |
| guest_gift_total_bonus | parameter | Σ gift entries ≥ 4500 → 2; ≥ 2000 → 1; else 0 | aggregate | — |
| large_gift_taper | method | ≥ 500 → full pct on 500 + half pct above; < 25 → none; else pct × amount | single | — |
- Distinct outcomes on every rewards-earning type (5%: 0/3/5; 10%: 5/8/10). Labels honest. Baseline.rule self-sufficient (type percent × gift amount, one rounding).

P3 registry_ext_gift_return_credit — 4 factors (3 `parameter`, 1 `method`).
| factor | label | tiers | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- |
| registry_return_fee | parameter | prepaid label & no free shipping & no waiver reason → 9.95; carrier pickup & no waiver reason → 99.00; else 0 | tier 1 yes (return record × membership), tier 2 no (one return record) → not multi-source | loyalty |
| registry_restock_charge | parameter | damaged & no waiver reason → 25%; opened_unused & no waiver & tier not waiving → 15%; else 0 | tier 1 single record → not multi-source | order |
| late_registry_return | parameter | > type window → 10%; > 30 d within window → 5%; else 0 | yes (return date × registry event_date) | order |
| deduction_shape | method | duplicate (gift entries of the sku > requested) → no deductions; ≥ 750 → deductions capped at 180; else full | yes (sku gift entries × item entry) | — |
- `deduction_shape` (observation, G-9): its tiers can be written as MN(deductions, c) with c ∈ {0, 180, unbounded}; accepted as `method` because the tiers are three distinct treatments (waive / cap / take in full), not one rate substituted.
- `restocking_fee_waived` semantic stretch (G-7). Realism (observation): a 5% "late" charge on a registry return made inside the published registry window is an unusual treatment; not demonstrable as one no such business publishes.

P4 registry_ext_credit_redemption — 4 factors as declared (3 `parameter`, 1 `method`).
| factor | label | tiers | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- |
| credit_payable_basis | method | completion entry → selling − completion discount; Finch Notes → selling − notes; else selling | tier 2 yes (registry entries × order line) | (declared null; reads order) |
| registry_item_stretch | parameter | open item → 5; fully given item → 2; not on registry → 0 | yes (item entry × gift entries) | — |
| circle_credit_stretch | parameter | Diamond/Icon active → 3; Silver/Gold/Platinum active → 1; else 0 | single record | loyalty |
| period_window_stretch | parameter | 0 ≤ days ≤ completion window → 2; days < 0 → 1; else 0 | yes (order date × registry event_date) | — |
- **Mislabelled `method` (G-10, SOURCE-FACTOR RED for any task rooted in P4):** every tier of `credit_payable_basis` computes the same formula `payable = line_price − d` and only substitutes the number d ∈ {completion discount amount, finch_notes_applied, 0}; compute `payable: "(line_price - line_completion) if line_completion != None else ((line_price - line_notes) if (line_notes or 0) > 0 else line_price)"`. The algorithm downstream (`payable / (1 + stretch/100)`, capped by `available`) is identical across tiers. Under the skill's test ("a factor labelled `method` whose tiers only substitute a different number into the same formula") this is a `parameter`; struck as a method, P4 has 0 `method` factors (bound: ≥ 1).
- Realism (observation): a "registry credit stretch" (each dollar of registry credit paying 1 + s % of the line) is an invented bonus-on-spend; its tiers (item open/given, Finch Circle tier, period) are plausible incentive conditions; no tier outcome is demonstrably one no department store would publish.

Per-task coverage (from the trees inferred above): tree {P1,P2} has multi-source factors (item_entry_percent, elite_card_tier_bonus, circle_tier_bonus, early_window_bonus, post_event_gift_cut) and cross-difficulty factors (card, loyalty, order). Tree {P4,P3} has multi-source factors (late_registry_return, deduction_shape, registry_item_stretch, period_window_stretch) and cross-difficulty factors (loyalty, order).

### findings

- G-1 (watch; bears on task 0): P1→P2 edge condition quantifies over every guest gift entry; P2 resolves only the most recent entry lacking an accrual. Holds only if the sole unmet entry is the most recent one.
- G-2 (watch; bears on task 1): P4→P3 edge condition quantifies over every received registry-gift return; P3 compute resolves the latest received return (XLATEST). Holds only if exactly one received return is uncredited and it is the latest.
- G-3 (watch; task 0): base registry_rewards_rules reversal sentence inherited alongside P2; if the gift P2 accrues is returned, P1's net_rewards is ambiguous.
- G-4 (observation; tasks 0, 1): P1 circle_pct and P3 free_ship/restock_waived read the current tier while rule/loyalty_tier_benefits say the tier held on the purchase/return date. Consequence only where the tier changed in between.
- G-5 (watch; task 0): base excluded-class sentence inherited, unimplemented in P1 compute.
- G-6 (watch; task 0): P2 holder_pct reads one active card row via CFIELD; two active accounts of different kinds can make compute and rule diverge.
- G-7 (watch; task 1): `restocking_fee_waived` defined for furniture and mattress restocking only; P3 applies it to every class.
- G-8 (watch; task 0): P1 ladders degenerate on non-Wedding registries.
- G-9 (observation): deduction_shape label borderline, accepted.
- G-10 (SOURCE-FACTOR RED, charter-global finding; consequence in task 1's file): `credit_payable_basis` labelled `method` but substitutes a number into one formula; P4 then has no honest `method` factor.
- G-11 (observation): claimed event_types omit registry_rewards_accrual and registry_credit_use (see policy_conflict_scan); exclusivity intact.

## closing_checklist

Written after both tasks' derivations were frozen (mtimes 0.md 15:55:15Z, 1.md 15:56:53Z) and GT was revealed (15:56:56Z). Nothing above this heading was derived from a revealed GT.

- Audit files: `0.md`, `1.md` one-to-one with tasks 0 and 1, `_difficulty.md` alongside; revision 1, no older revision.
- Scopes (now confirmed against `charter_scope`): task 0 = {registry_ext_completion_redemption, registry_ext_missed_rewards_accrual}, task 1 = {registry_ext_credit_redemption, registry_ext_gift_return_credit} — pairwise disjoint, jointly cover all four extended policies; task tools closed (each tool in exactly one task's scope).
- uuid8s independently generated and frozen (§ action_binding_and_uuids).
- Trees: each has 1 prerequisite problem, 1 value_input edge, an owner=user root, no cycle; whole-difficulty graph {P1→P2, P4→P3} acyclic.
- Factors: P1 6 (5 parameter / 1 method), P2 4 (3/1), P3 4 (3/1) — pass; **P4 4 declared (3/1) but honestly 4 parameter / 0 method — fail (G-10 → task 1 T1-1)**. Every factor of both tasks bears weight against an honest baseline; every computation's baseline gives a definite number ≠ gold (54.80, 65.80, 880.00, 650.00).
- Per-task verdicts:
  - Task 0: policy self-consistency PASS; problem tree PASS; factors PASS; unique solution **SOURCE-TASK RED** (T0-1, false assertions in `evaluation_criteria[3].objective` and `[7].necessity`; scored values 62.88 / 52.81 correct and unique).
  - Task 1: policy self-consistency PASS; problem tree PASS; factors **SOURCE-FACTOR RED** (T1-1, `credit_payable_basis` mislabelled `method`); unique solution PASS (700.00 / 499.54).
- Difficulty closure: **not closed** — two REDs open. Gate re-run on the final form is deferred to the post-rework round (the brief's snapshot is the gate state of this revision).

## revision_2

### charter_global_frozen (revision 2)

- Written before any round-2 task JSON was opened. Auditor: same independent auditor, revision 2. Round-1 text above is left untouched.
- Gate snapshot: `/tmp/erl0061_coord/snapshot.sh gift_registry_services 2` (coordinator-owned; output in `.audit_views/policy/gift_registry_services/snapshot_r2.txt`, 2026-10-13T16:38:42Z): check_extended, check_task_tools, replay --check, check_solvability, check_compute (branches 39.50, steps 12.00, history_rows_max 28, branches_max 45), check_grounding, check_cross_fire all OK; check_traceability only `unlock_*_discoverable_tool:tool_name` misses (non-tool_name misses: 0); validate_scenario prints INVALID with only "required document" lines (the script filters those lines and no other error line remains; tasks_ok 10/10). Entry conditions met; `tasks/gift_registry_services/rework_r2_claims.md` present → rework landed.
- Hashes (sha256[:16]): `registry.extended.yaml` **0ab95e7d4e25dbd0** (round 1: 4ec3d14ccee4c3d6 — changed → every charter-global section re-derived in full below); `task_tools.py` da70fda2a1a6302e (unchanged → § action_binding_and_uuids carried forward by reference: tool bodies, docstrings, uuid8s identical); masked views 0.json 45730f479e694982, 1.json 1fdb00c37ae6b1a1 (unchanged → frozen_time, user_scenario, initial_state identical to round 1).
- Read: the claims file (item ids → claimed change), the revised extended section (lines 950–2199), base copy diff (still verbatim; only the trailing blank line differs), db_schema `purchases.returned_date`.
- contamination_disclosure (revision 2): (a) the auditor carries round-1 knowledge of both tasks' round-1 GT (it equalled the round-1 blind derivations). (b) `rework_r2_claims.md` states "The scored values of task 0 are unchanged", i.e. it discloses that task 0's round-2 gold equals the round-1 gold (62.88 / 52.81). Task 0's round-2 derivation below is re-done from the revised charter, but its blindness is weakened by (a)+(b) and is recorded so. For task 1 the claims give no figure; its round-2 derivation is blind with respect to round-2 GT.

### policy_conflict_scan (revision 2)

- Same four extended policies, same subjects, target tools and computes; no new overlapping subject. Cross-category reads: P1 adds the order line's merchandise class (`variant_name`) — note its `cross_category[order].reads` list does not name `variant_name` (observation R2-O1, no consequence: compute and rule both read it). P3 drops loyalty `restocking_fee_waived`; keeps `free_return_shipping`. P4 unchanged reads.
- New P2 sentence "A guest gift entry whose gift already carries a registry rewards reversal entry is not accrued by this policy, since an accrual on a gift returned before the payout is reversed in full." — consistent with base registry_rewards_rules S2; no conflict with P1's prerequisite sentence (a reversal presupposes an accrual entry, so the "every gift entry carries its accrual" state is unaffected).
- Claimed scope vs written event types: unchanged (round-1 G-11 observation stands).

### rule_compute_equivalence (revision 2)

Mechanical: every compute_basis value verbatim in its rule; compute keys = basis keys; every baseline.rule sentence in the rule; every overwrite's superseded_clause verbatim in base and replaced_by verbatim in the extended rule — all True for P1–P4. Sentence-level:
- P1: `line_class` + discount_found's first branch implement the new class exclusion (closes G-5); `type_pct` tier 2 = completion_discount_pct × 50/100 ("post-event item share"); `card_pct` tier 2 = MX(type card bonus, 3). Equivalent. circle_pct still reads the current tier (G-4 unchanged, observation).
- P2: `elite_held`/`card_held` via EXISTS over active card accounts with "where no elite account is held" precedence — equivalent to the rule (closes G-6). The reversal carve-out is a trigger/scope sentence, not a compute quantity (as "carries no accrual entry" was in round 1).
- P3: return_fee unchanged; restock_pct 4-tier ladder (damaged 25 / opened > 30 d 15 / opened ≤ 30 d 5 / 0) on condition, reason and days event→authorization; insured_fee (≥ 750 → 15, ≥ 300 → 5, by label or pickup); restock_charge (duplicate → 0; ≥ 750 → p × 750 + p/2 × excess; else p × amount); result = gift − (restock + fee + insured), floor 0, one rounding. Equivalent; no late charge remains (round-1 realism observation removed).
- P4: payable unchanged; bonus_pct = circle (3/1/0) + period (0–30 d → 2; 31 d–completion window → 1; else 0); credit_drawn: open item → payable / (1 + b); fully given item → payable − b × MN(payable, 200); no entry → payable; result RND(MN(available, credit_drawn)). The rule's period fall-through is worded "otherwise, for a line bought before the event date" while compute's else also covers a line bought after the completion window; P4 only runs while the registry is active or in completion, and an ordered line's purchase date cannot be later than frozen_time, so a line after the window cannot reach this write — no consequence (observation R2-O2). Loyalty cross_category note still says "credit stretch" (stale label, observation R2-O3).

### action_binding_and_uuids (revision 2)

Carried forward by reference to round 1 (task_tools.py hash unchanged, da70fda2a1a6302e); `(target_tool, computes)` pairs unchanged and each claimed once.

### prerequisite_graph and prerequisite_sentences (revision 2)

Unchanged edges P1→P2 (value_input, gate perk_pct) and P4→P3 (value_input, gate available); policy_source verbatim in the blocked rule (True), not restated in the depended-on rule (True), resolved_by = depended-on target_tool (True), form state, no fallback_reason. The sentences are word-identical to round 1, so the four-point test and single-reading derivations of round 1 stand. G-1 / G-2 (every-instance condition vs single-object resolver) unchanged — watch items, checked per task.

### override_declarations (revision 2)

- P1: same three overwrites; overwrite #2 now also carries the excluded-class sentence, so base S4 ("Items of completion_excluded_classes ... are never discounted") is now implemented rather than merely inherited. Overwrite #3's replaced_by uses the "post-event item share". No undeclared override.
- P2: one overwrite as before; the new reversal sentence restates base S2 rather than changing it.
- P3: one overwrite (class fee rules → registry deductions); the new deductions (grace restocking, insured surcharge, marginal restocking) all fall within the declared replacement "the registry return deductions set out here instead of the fee rules of the gift's merchandise class". Base deadline, one-credit-per-return and completion-purchase sentences inherited.
- P4: one overwrite whose replaced_by now reads "on the amount of the line still to be paid, in the form the registry credit bonus takes, and never more than the registry credit available". Declared. No undeclared override found.

### factor_ladders (revision 2)

- P1 (6: 5 parameter, 1 method). item_entry_percent: 0 / type × 50 % / type — distinct on every type (Celebration/Graduation 5 vs 10; Wedding 10 vs 20) → G-8 closed for this factor. elite_card_tier_bonus: 8 / MX(type bonus, 3) / 0 → 8 / 5 / 0 on Wedding, 8 / 3 / 0 elsewhere — distinct → G-8 closed. Others unchanged. markdown_better_of now includes the class exclusion in its first tier; method tiers still differ in form.
- P2 (4: 3 parameter, 1 method). cardholder_rewards_bonus tiers now disjoint by account existence (2 / 1 / 0). Others unchanged.
- P3 (4: 3 parameter, 1 method). registry_return_fee (9.95 / 99 / 0); registry_restock_percent (25 / 15 / 5 / 0 — four distinct tiers; tiers 2–3 multi-source: return record × registry event_date); insured_return_surcharge (15 / 5 / 0; both tiers multi-source: gift entry × return record); restock_taper_shape (none / marginal / proportional — distinct functional forms; honest method). Realism: open-box grace for gifts opened after the occasion and an insured-shipping surcharge on valuable mailed returns are treatments a department store plausibly publishes; the round-1 "late charge inside the window" observation no longer applies.
- P4 (4: 3 parameter, 1 method). credit_payable_amount relabelled `parameter` (honest: selects d in `price − d`). circle_credit_bonus 3 / 1 / 0. period_credit_bonus 2 / 1 / 0 (tier conditions over order date × registry event_date). **credit_bonus_form (method)**: payable / (1 + b) vs payable − b × MN(payable, 200) vs payable — three distinct functional forms, each stated in the rule and implemented; honest method → round-1 G-10 closed at charter level. Realism: a bonus on registry credit spent on items still wanted, a small capped reduction for already-given items, none for off-registry items — plausible incentive design; observation only.
- Every ladder ≥ 3 tiers, pairwise-disjoint as stated, every tier in rule and compute, fall-through = baseline, bindings disjoint, no `decides: result`.

### findings (revision 2, charter-global)

- G-10 → **closed** (P4 has an honest method factor). G-3, G-5, G-6, G-7, G-8 → closed as claimed (verified above). G-9 → superseded (restock_taper_shape is an honest method). G-1, G-2 → watch, per task. G-4, G-11 → observations unchanged.
- New observations: R2-O1 (P1 cross_category reads list omits `variant_name`), R2-O2 (P4 period fall-through wording narrower than compute's else, unreachable difference), R2-O3 (stale "credit stretch" in P4 loyalty note). No new charter-global RED.

### closing_checklist (revision 2)

Written after both revision-2 derivations were frozen (appends completed 16:41:38Z) and round-2 GT revealed (16:41:43Z).
- Files: `0.md`, `1.md`, `_difficulty.md`, each with `## revision_1` text untouched and `## revision_2` appended.
- Scopes (`charter_scope` round 2): task 0 = {completion_redemption, missed_rewards_accrual}, task 1 = {credit_redemption, gift_return_credit} — disjoint, jointly cover all four extended policies; task tools closed; uuid8s unchanged and independent.
- Trees: one prerequisite each, one value_input edge each, owner=user root in each, acyclic difficulty graph.
- Factors: P1 6 (5/1), P2 4 (3/1), P3 4 (3/1), P4 4 (3/1); every ladder ≥ 3 distinct tiers, stated in rule and compute; per task ≥ 1 multi-source and ≥ 1 cross-difficulty factor with seeded rows; every factor bears weight against an honest baseline; baselines alone give 54.80 / 65.80 / 880.00 / 650.00, all ≠ gold (62.88 / 52.81 / 732.80 / 528.92).
- Round-1 REDs: T0-1 closed, T1-1 (G-10) closed. Charter watch items G-3, G-5, G-6, G-7, G-8 closed; G-9 superseded; G-1, G-2 hold on both worlds; G-4, G-11 observations.
- Gates: the coordinator's round-2 snapshot (`snapshot_r2.txt`, 16:38:42Z) on the final form — all OK apart from the pre-render traceability tool_name misses and validate_scenario's "required document" errors.
- Per-task verdicts (revision 2): **task 0 PASS** (policy / tree / factors / unique solution all PASS; blind derivation weakened by the claims file, disclosed); **task 1 PASS**.
- Difficulty: passes the source-layer audit at revision 2.

## revision_3

### charter_global_frozen (revision 3)

- Written before any round-3 task JSON was opened (task files mtime 2026-10-14 00:24:59Z). Auditor: same, revision 3; revision 1 and 2 text untouched.
- Gate snapshot `/tmp/erl0061_coord/snapshot.sh gift_registry_services 3` → `snapshot_r3.txt` (2026-10-14T00:25:18Z): check_extended, check_task_tools, replay --check, check_solvability, check_compute (branches 39.50, steps 12.00, history_rows_max 28, branches_max 45), check_grounding, check_cross_fire OK; **check_traceability OK** (0.json 16/0, 1.json 16/0; non-tool_name misses 0); validate_scenario prints INVALID with no error line left after the script's "required document" filter (tasks_ok 10/10, documents 217). `rework_r3_claims.md` present → rework landed.
- Hashes: `registry.extended.yaml` **351f7effd4fa826f** (round 2: 0ab95e7d4e25dbd0 — changed → charter sections re-derived); `task_tools.py` da70fda2a1a6302e (unchanged → action binding / uuids / docstrings carried forward); views 0.json 45730f479e694982, 1.json 1fdb00c37ae6b1a1 (unchanged → worlds and personas identical).
- Additional input read in full: `audits/render_source/gift_registry_services/render_r1_registry.md` (4 items).
- contamination_disclosure: the claims file states "no compute expression changed and no scored value moved in either task", and the auditor knows the round-2 GT of both tasks. Round-3 derivations below are recomputed from the revised charter on the unchanged worlds, but neither can be claimed blind to the expected values.

### rule_compute_equivalence (revision 3)

Mechanical (python): base copy still verbatim; every compute_basis value verbatim in its rule; compute keys = basis keys; every overwrite's superseded_clause verbatim in base and replaced_by verbatim in the rule; **every baseline.rule is now one contiguous passage of its rule** (True for P1–P4); factor bindings disjoint; prerequisite sources verbatim in the blocked rule, not restated in the depended-on rule, resolved_by = depended-on target_tool. Compute expressions compared against the revision-2 expressions recorded in this audit: unchanged in all four policies.

Render items (render_r1_registry.md):
1. Finch Circle tier date (P1) — rule now: "the tier it holds on the date the completion discount is redeemed, which is the date of the completion purchase entry"; ladder tiers say "on the date the discount is redeemed"; card bonus "active on the date the discount is redeemed". Compute reads the membership and card account at handling time, which is the redemption date (the redeem tool stamps `entry_date = ctx.now()[:10]`). Rule = compute. The change from base's "(tier held on the purchase date)" sits inside overwrite #1's superseded clause, so it is declared. Loyalty_tier_benefits' "the registry completion purchase date" reads naturally as the date of the completion purchase entry → consistent. **Closed.** (G-4 for P1 thereby closed.)
2. Coupon lines (P1) — rule, overwrite #2, compute_basis and ladder now: "any other line at a sale price, or whose selling price sits below its regular price for any reason such as a coupon or promotion allocated to it"; compute `line_price_type == 'sale' or line_price < line_regular`. Same width. **Closed.**
3. Period credit bonus fall-through (P4) — rule: "otherwise, for a line bought before the event date or more than the registry type's completion window after it, no registry period credit bonus is added"; ladder fall-through names both; compute else covers exactly days < 0 or days > window. **Closed** (R2-O2 closed with it).
4. Baseline not one passage (P1) — baseline.rule now contiguous in the rule; overwrite #2's replaced_by carries its own rounding clause ("the completion discount so found is rounded half up to the cent once, on the final amount"). With the cap applied after it, MN(RND(found), cap_left) = RND(MN(found, cap_left)) because cap_left is a whole number of cents, so the rule's two rounding statements and the single RND in compute give the same figure. **Closed.**

Own observations: R2-O1 — P1 `cross_category[order].reads` now includes `variant_name`, note names the merchandise class → closed. R2-O3 — P4 loyalty note says "credit bonus"; no "stretch" in any note → closed.

Class sweep claimed by the reworker, checked:
- P2: post-event fall-through "for a gift entered on or before the event date" = compute `gift_days_after_event > 0` else-branch. Equivalent.
- P3: "the registrant's most recently authorized return record in received status" = XLATEST by created_at; label tier "no active Finch Circle membership or the tier ... when the credit is booked does not include free return shipping" = `not CPARAM(..., status='active')` (absent → fee); grace tier "a return authorized before the event date included" = `return_days <= 30`; duplicate "against the requested quantity of the item's most recent item entry (an item without an item entry counting as requesting none)" = `int(sku_requested or 0)`. Equivalent.
- P4: circle bonus "the tier it holds when the credit is applied", fall-through "another tier or an inactive or absent membership" = compute; bonus form reads the most recent item entry's requested quantity = LATEST. Equivalent.
- P1: early window first tier "a line bought before the event date included" = `days_after_event <= 30`. Equivalent.

### policy_conflict_scan / override_declarations / prerequisite_graph / factor_ladders (revision 3)

- No new subject, tool, cross-category write or prerequisite edge; edges P1→P2 and P4→P3 word-identical to round 2. Overwrites unchanged in scope; no undeclared override.
- Factor structure unchanged from revision 2 (P1 6 = 5/1, P2 4 = 3/1, P3 4 = 3/1, P4 4 = 3/1); tier values unchanged; wording of fall-throughs now explicit. All method factors still change the functional form.
- New observation R3-O1: P3 now states that the free-return-shipping tier is read "when the credit is booked", while `products/loyalty.yaml` loyalty_tier_benefits reads return-shipping benefits from "the tier held on the date of the occurrence ... the return date". P3's overwrite names only base registry_gift_returns. The two dates differ only when the tier changed between the return authorization and the booking; no task world here has such a change (task 1: Silver since 2025-02-01), so no consequence can be demonstrated → observation, not RED. (Round 1/2 already read the current tier implicitly; round 3 made it explicit.)

### findings (revision 3, charter-global)

- render_r1 items 1–4 closed; R2-O1, R2-O2, R2-O3 closed; G-4 closed for P1 (P3/P4 tier dates now explicit, see R3-O1).
- New: R3-O1 (observation). No charter-global RED open.

### closing_checklist (revision 3)

- Files `0.md`, `1.md`, `_difficulty.md` carry revision_1, revision_2 and revision_3, older text untouched; freeze (00:26:51Z) before reveal (00:26:56Z) for both tasks.
- Scopes disjoint and jointly complete; task tools closed; uuid8s unchanged and independent.
- Trees: one prerequisite each, one value_input edge each, owner=user root each, acyclic.
- Factors: P1 6 (5/1), P2 4 (3/1), P3 4 (3/1), P4 4 (3/1); every ladder ≥ 3 distinct tiers stated identically in rule and compute; each task has ≥ 1 multi-source and ≥ 1 cross-difficulty factor with seeded rows; every factor bears weight; baselines 54.80 / 65.80 / 880.00 / 650.00 ≠ gold 62.88 / 52.81 / 732.80 / 528.92.
- Render items 1–4 closed; R2-O1–O3 closed; no round-2 RED was open; nothing regressed. Open observations: R3-O1 (P3 tier date vs loyalty_tier_benefits return date; not demonstrable on any task world), G-1/G-2 watch items hold on both worlds, G-11 (claim event_types list).
- Gates on the final form: `snapshot_r3.txt` — all OK including traceability; validate_scenario shows no error other than the filtered "required document" lines.
- Per-task verdicts (revision 3): **task 0 PASS**, **task 1 PASS**. Charter: no open RED.
