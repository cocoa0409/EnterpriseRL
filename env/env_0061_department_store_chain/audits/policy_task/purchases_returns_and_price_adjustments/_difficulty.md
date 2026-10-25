# Policy-task audit — purchases_returns_and_price_adjustments / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (erl-task-policy-audit), revision 1. Frozen 2026-10-13T15:58Z, before any task JSON was opened.
- Freeze hashes (sha256[:16], checked on disk at audit start and matching the brief):
  - `tasks/purchases_returns_and_price_adjustments/order.extended.yaml` 592d61bbe4402769
  - `tasks/purchases_returns_and_price_adjustments/task_tools.py` f185b76d932fd485
  - masked views `.audit_views/policy/purchases_returns_and_price_adjustments/0.json` 77b814c768942ba4, `1.json` a5771591cb78cc62
- Read: `blueprint/blueprint.yaml`, `blueprint/products/order.yaml` (plus loyalty/registry/giftcard/card product charters for cross-category semantics), `blueprint/db_schema.json` (field lookups), `blueprint/share_tools.py` (tool list), the extended charter, `task_tools.py`, the DSL evaluator `skills/erl-task-instantiate/scripts/check_compute.py` (to read `MONTHS`/`DAYS`/`within_months`/`CFIELD`/`X*` semantics).
- Masked and not read for this section: every `tasks/*/tasks/*.json`, every task GT field (`evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`), other difficulties' tasks and audits. Nothing in this section is derived from a revealed GT.
- Entry conditions (Step 0): the gate snapshot (check_extended / check_task_tools / replay --check / check_solvability / check_compute / check_grounding / check_cross_fire all OK; check_traceability NOT OK only on unpublished-KB `unlock_*` misses; validate_scenario only "required document not found") and the masked views with hashes were supplied in the brief. Accepted as entry qualification only; not re-run.

### policy_conflict_scan

- Base copy: lines 1–1001 of the extended file are byte-identical to `blueprint/products/order.yaml` (`diff` empty).
- Seven extended policies, all `subject: [order_price_adjustment]`, `computes: amount`, `trigger: on_request`, `base_policy_refs: [order_price_adjustment_rules]`:
  | policy | target_tool (owner) | prerequisite |
  | --- | --- | --- |
  | order_ext_shelf_price_correction (P1) | correct_shelf_price_8a80c6f7 (agent) | [] |
  | order_ext_registry_credit_shortfall_refund (P2) | refund_registry_credit_shortfall_17a5cd98 (agent) | [] |
  | order_ext_registry_price_protection_claim (P3) | claim_registry_price_protection_38d04d45 (user) | P1, P2 |
  | order_ext_note_shortfall_refund (P4) | refund_note_shortfall_1f084e1e (agent) | [] |
  | order_ext_bonus_card_shortfall_refund (P5) | refund_bonus_card_shortfall_1f1335fb (agent) | [] |
  | order_ext_duplicate_capture_refund (P6) | refund_duplicate_capture_6e7f744e (agent) | [] |
  | order_ext_gift_card_shortfall_claim (P7) | claim_gift_card_shortfall_5b13f7c5 (user) | P4, P5, P6 |
- Overlapping subject: every policy writes an `order_price_adjustment` row on one purchase record. The six register-error policies (P1, P2, P4–P7) each carve out one error kind ("only for such ...; every other register error ... stays under the base rule or the rule written for it"); their scopes are disjoint by error kind (shelf ticket / registry credit / Finch Note / Bonus Card / non-Bonus gift card / second capture). P3 is a price-drop claim, disjoint from the register-error kinds.
- Interaction of co-applicable policies on one unit: P2/P4/P5/P7 each cap their shortfall against the gross payment captures (`SUM(order_payment)`) and the record's selling price/tax/applied notes; none reads `net_paid_amount` or another correction's amount, so the register-error writes commute with one another. P3 reads P1's `new_unit_price` and the existence of a no-new-price correction; P7 reads the count of register-error corrections. No two policies fix the same quantity.
- Triggers / eligibility / time anchors: all are `on_request`; base `within_adjustment_window` (applies_to order_price_adjustment) and `unit_not_returned` are inherited by every extended policy except where P3 overrides the status condition (see override_declarations). Both task units are 11 and 9 days from purchase (inside the 14-day Home & Kitchen window), so the base window is not tested by either task.
- Cross-category read boundaries: reads of loyalty (membership tier, enrolled_date, points/note ledgers), card (variant, status, opened_date, `card_transactions` M&F purchases), registry (status, type, `registry_events`), giftcard (cards, registration, ledger) — all read-only; no extended policy writes another category.
- Claimed scope: blueprint claims event_types [order_return_start, order_refund, order_price_adjustment, order_cancellation, order_comfort_exchange]; the seven extended policies all sit under `order_price_adjustment`. Coverage by the two tasks (from the prerequisite graph alone): a tree rooted at P3 = {P1, P2, P3} and a tree rooted at P7 = {P4, P5, P6, P7}; jointly complete and mutually exclusive (to be confirmed against `charter_scope` after reveal; see closing_checklist).

### rule_compute_equivalence

Mechanical sweep (`/tmp/audit_order_0061/chk.py`, whitespace-normalised substring test) of every `compute_basis` value against its own `rule`, every `baseline.rule` sentence against the `rule`, every `prerequisite.policy_source` against the `rule`, every `overwrite.superseded_clause` against the base rule and every `replaced_by` against the extended rule; K-params used vs declared.

- `superseded_clause` verbatim in base, `replaced_by` verbatim in rule, `policy_source` verbatim in rule, all `baseline.rule` sentences in rule, params used == params declared: all policies PASS.
- **FAIL — `compute_basis` not a quotation of the rule (P1, P3).** The rule of P1 reads "A customer whose Finch Circle qualifying spend posted in the twelve calendar months before the request date (**earn entries** whose posting date falls less than twelve whole months before it) reaches the upper spend threshold ..."; its `compute_basis.t0_member_spend` / `t0_spend_bonus` quote "(**purchase earn entries** whose posting date ...)", a sentence that does not occur in the rule, and `t0_member_spend` = `XSUM('loyalty','loyalty_points_ledger','qualifying_amount', ..., event_type='loyalty_points_earn', earn_source='purchase_base')`. P3 has the identical defect for `d0_member_spend` / `d0_spend_bonus` (rule: "(earn entries whose posting date ...)"). The loyalty charter's earn event lists earn_source "purchase_base, card_bonus, card_outside_spend, bonus_event, tier_bonus or enrollment_bonus" with `qualifying_amount` "Net qualifying dollars the points were computed on" (non-zero for card_bonus / card_outside_spend). So the rule counts card-bonus earn rows that the compute drops. P4–P7 rules say "purchase earn entries" (P6, P7) or do not use the measure, and are consistent. See finding CG-1.
- Every other quantity (shortfalls and their caps, tax sentences, held/standing/service-day conventions, caps, goodwill ladders, rounding points, `within_months=12` = "less than twelve whole months" under `MONTHS` with day-of-month carry) has a verbatim basis and a matching expression; tiers named in `factors[].ladder` are each a sentence of the rule and a branch of the `decides` binding, and vice versa.
- Rounding: rules say "rounded half up"; the DSL `RND` is Python `round` (half-even on binary floats). No rounding tie occurs in either task world (all intermediate quotients are non-tie), so this is recorded only as an observation (CG-O5).
- Two latent wording/compute gaps, observations only (no world in this difficulty exercises them):
  - P6: scope sentence "A unit whose payment records show **its tender** captured more than once" vs `dc_captures = COUNT('order_events', event_type='order_payment')` with no tender filter, while base `order_agg_order_allocation` records "one order_payment row per tender per unit" for mixed tender. On a mixed-tender unit with one duplicated tender the latest capture may be the other tender's (CG-O2).
  - P7: "A unit whose largest gift card redemption entry reaches the large redemption size" vs `g1_largest_redemption = XMAX(... giftcard_redeem, purchase_id=HID)` with no Bonus Card exclusion, while the same rule defines its gift card as "other than a Bonus Card" and excludes Bonus Card redemptions explicitly only in the shortfall sentence (CG-O3).

### action_binding_and_uuids

- Each `(target_tool, computes=amount)` is claimed by exactly one policy (7 tools, 7 policies). Each docstring describes one business action whose effect is one `order_price_adjustment` row + `net_paid_amount` decrement; no confirmation/review/wait step is added.
- Docstrings: no tool names another tool, no position in a sequence is stated; the only "before" occurrences are "rounded half up to the cent before it is passed" (argument formatting) and "a guest later bought" (narrative). No concrete numeric example appears in any docstring or parameter description, so no gold value can leak through a published docstring.
- Tool bodies validate nothing beyond `ctx.find("purchases", purchase_id=...)[0]` (record existence); no tool checks a prerequisite, refuses, or hints.
- uuid8s: 8a80c6f7, 17a5cd98, 38d04d45, 1f084e1e, 1f1335fb, 6e7f744e, 5b13f7c5 — all distinct, no reuse, no sequential or common-tail pattern. 1f084e1e and 1f1335fb share the two-character prefix "1f" (chance ~1/256 per pair); not evidence of batch derivation — observation CG-O6.

### prerequisite_graph

- `prerequisite` filled in on all seven policies (`[]` on P1, P2, P4, P5, P6).
- Edges: P3→P1 (value_input, gate d0_base_price), P3→P2 (value_input, gate d0_store_value), P7→P4, P7→P5, P7→P6 (value_input, gate g1_corrections). Every `problem` is an extended policy id of this file, none self-referential, none a base policy. Graph is two disjoint stars: acyclic.
- `form: state` on all five edges; no `fallback_reason` (correct, none is action form).
- `resolved_by` = the depended-on policy's `target_tool` on all five edges; each tool's body writes the row the `effect` names (P1 tool writes `adjustment_reason=register_price_error, new_unit_price=<arg>`; P2/P4/P5/P6 tools write `register_price_error` with no `new_unit_price`), so each effect is genuinely produced.
- `kind` vs `gate`: d0_base_price, d0_store_value, g1_corrections are bindings of the blocked policy's compute and genuinely change with the write (`d0_shelf_count`, `d0_correction_count`, `g1_corrections`).
- `condition` vs sentence strength:
  - P3→P2: sentence "for any registry credit spent on the unit **and left undeducted**"; `condition` "Whenever the registry's ledger carries a registry_credit_use entry naming the unit, the unit's order_events carry an order_price_adjustment with adjustment_reason register_price_error and no new_unit_price" — the "left undeducted" qualifier is dropped, so the condition is stronger than the sentence. See finding CG-2.
  - P3→P1, P7→P4, P7→P5, P7→P6: conditions match the sentences' strength and scope.
- No authoring-viewpoint wording ("in this task", "at the opening") in any `prerequisite` text.

### prerequisite_sentences

Four-point test per edge (connective / state named in record words / no tool, id or snake_case / strength):

| edge | sentence (verbatim in blocked rule) | connective | state named | tokens | strength |
| --- | --- | --- | --- | --- | --- |
| P3→P1 | "The registry price protection refund on a unit is fixed only after the unit's records carry a register-error correction to its shelf ticket price for any amount the unit was rung above that ticket." | only after | register-error correction to the shelf ticket price (adjustment_reason register_price_error, new_unit_price = regular_price) | none | matches |
| P3→P2 | "The registry price protection refund is not worked out until the unit's records carry a register-error correction recording no new unit price for any registry credit spent on the unit and left undeducted." | not ... until | register-error correction recording no new unit price | none | condition stronger (CG-2) |
| P7→P4 | "The gift card shortfall refund is fixed only after the unit's records carry a register-error correction for every Finch Note recorded as redeemed on the unit but left undeducted." | only after | register-error correction | none | matches |
| P7→P5 | "The gift card shortfall refund is not settled until every Bonus Card redemption recorded against the unit and left undeducted carries its register-error correction on the unit's records." | not ... until | register-error correction | none | matches |
| P7→P6 | "Before the gift card shortfall refund is fixed, every second capture of the unit's payment must carry its register-error correction on the unit's records." | before | register-error correction | none | matches |

- Derivation sentence + records + depended-on rule → resolving action (single reading each): P3→P1: the only rule whose write records a register-error correction with the shelf ticket as new unit price is P1 ("The new unit price recorded on the correction is the shelf ticket price"). P3→P2: the qualifier "registry credit spent on the unit and left undeducted" matches only P2's scope sentence ("registry's ledger shows registry credit spent on a purchase record but the unit's payment was captured in full"). P7→P4 / P5 / P6: qualifiers "Finch Note ... left undeducted", "Bonus Card redemption ... left undeducted", "second capture" each match exactly one scope sentence (P4, P5, P6).
- Shared record state: the record a P2/P4/P5/P6 write leaves (`register_price_error`, `new_unit_price` empty) is identical across those four tools and P7's own claim tool; the record does not say which error kind it corrected. The hop resolves through the qualifier (error kind) rather than the record alone, and the blocked computes test the bare state (`d0_correction_count` counts any no-new-price correction; `g1_corrections` counts every register-error correction). On a unit carrying two error kinds, a correction of the wrong kind would satisfy P3's store-value gate. No world in this difficulty has a second qualifying error kind on the P3 unit, so recorded as observation CG-O1.
- No rule restates another problem's sentence; depended-on rules (P1, P2, P4, P5, P6) carry no sentence about P3/P7. No tool name, policy id or route is written in any rule. No rule states a cross-problem order that grounds no declared edge (the P3 sentences on base price and store value, and P7's "incident escalation credit is set once for the whole incident, on the gift card claim, from the register-error corrections standing on the unit", are the value side of the declared edges). No base rule sentence is used to ground an edge.

### override_declarations

Sentence-by-sentence against the single `base_policy_refs` entry, `order_price_adjustment_rules` (sentences S1–S10):

| base sentence | P1, P2, P4, P5, P6, P7 (register-error kinds) | P3 (registry price protection) |
| --- | --- | --- |
| S1 "When Marlowe & Finch ... sells the identical item (same sku) at a lower price within the price-adjustment window, the customer may ask for the difference." | not the governed quantity (register error, not a price drop) | followed: the guest gift of the same item number at a lower net price is that lower M&F price |
| S2–S3 request date within window; window = class days + tier extension, day 0 = purchase_date | inherited (base eligibility `within_adjustment_window` applies to every order_price_adjustment; S9 says register errors are made "at any time") — base-internal tension, not exercised (both task units are in window) | inherited unchanged |
| S4 class price_adjustment_eligible | inherited | inherited |
| S5 exclusions; clearance/final_sale units never adjusted | inherited | inherited |
| S6 "The unit is in ordered, shipped or completed status." | inherited | overridden, declared (overwrite #3: completed only) |
| S7 count below per-item max; difference from `order_msr_effective_unit_price` >= min | n/a (S9: counts toward no limit) | overridden, declared (overwrite #2: measured from the protection base price) |
| S8 refund = difference + tax on it, to original tender, never as a gift card | n/a | overridden, declared (overwrite #1: capped protected difference + tax + goodwill) |
| S9 register_price_error "made at any time while the unit is not returned, refunds the overcharge, and counts toward no limit" | overridden, declared by each (each `replaced_by` keeps "any time", "not returned", "no limit" and replaces "refunds the overcharge" by its own amount) | n/a |
| S10 "A price adjustment does not change Finch Circle points or qualifying spend." | followed (tools touch no loyalty row) | followed |

- Disguised forms checked: anonymous intermediate (P3's paid-share step deducts store value from the difference — covered by overwrite #1's "protected difference"); 0/1 multiplier (none: no existence condition zeroes a base-fixed amount); dropped branch (P3's base-price selector keeps the base "latest adjustment" branch as its first tier; no base branch is dropped).
- Outside `base_policy_refs`: base `order_payment_capture` ("Finch Notes are not a tender and are never refunded as money"; amount = unit_price + tax − finch_notes_applied) — P4 refunds card money captured for the note's part, not the note, and computes "what the card should have paid" by the same formula: consistent. Registry charter `registry_credit_rules` ("Registry credit is never paid out in cash or to a card account") — P2 keeps the credit spent and returns only card money captured: consistent. The base event-field gloss of `order_price_adjustment.amount` ("the per-unit price difference plus the sales tax on it") is not a policy sentence and is not named by any overwrite although every extended amount adds credits/goodwill — observation CG-O4.
- Result: no undeclared override found.

### factor_ladders

Per policy (P=parameter, M=method; "multi" = every non-fall-through tier is a conjunction over two or more distinct records; xd = cross_difficulty):

| policy | factors (label, tiers, xd) | P/M | multi-source factors |
| --- | --- | --- | --- |
| P1 | shelf_accuracy_share (P,3,loyalty); shelf_accuracy_cap (P,3,card); shelf_accuracy_spend_bonus (P,3,loyalty); shelf_standing_day_count (M,3,–) | 3/1 | shelf_accuracy_share (tier ∧ membership_linked on the purchase) |
| P2 | rcs_daily_rate (P,3,registry); rcs_held_day_count (M,3,card); rcs_held_cap (P,3,card); rcs_type_goodwill (P,3,registry); rcs_tenure_courtesy (P,3,loyalty) | 4/1 | rcs_daily_rate (registry status ∧ loyalty tier) |
| P3 | rpp_paid_share_method (M,3,loyalty); rpp_tenure_uplift (P,3,loyalty); rpp_card_spend_cap (P,3,card); rpp_card_goodwill (P,3,card); rpp_registry_status_goodwill (P,3,registry); rpp_member_spend_bonus (P,3,loyalty) | 5/1 | rpp_paid_share_method (tier ∧ store value on unit); rpp_registry_status_goodwill only nominally (CG-3) |
| P4 | nsr_service_rate (P,3,loyalty); nsr_service_day_count (M,3,loyalty); nsr_service_cap (P,3,card); nsr_lapsed_goodwill (P,3,loyalty); nsr_habit_courtesy (P,3,loyalty) | 4/1 | nsr_service_rate (membership_linked ∧ enrolment), nsr_lapsed_goodwill (note expiry ∧ card) |
| P5 | bcs_service_rate (P,3,card); bcs_service_day_count (M,3,card); bcs_service_cap (P,3,card); bcs_earner_goodwill (P,3,giftcard) | 3/1 | bcs_service_rate (card variant ∧ tier) |
| P6 | dcr_held_rate (P,3,loyalty); dcr_held_day_count (M,3,loyalty); dcr_held_cap (P,3,card); dcr_bank_fee_allowance (P,3,–); dcr_member_spend_goodwill (P,3,loyalty); dcr_capture_size_goodwill (P,3,–) | 5/1 | dcr_held_rate (tender ∧ tier), dcr_bank_fee_allowance (tender ∧ capture age) |
| P7 | gcs_incident_escalation (P,4,–); gcs_service_day_count (M,3,giftcard); gcs_service_rate (P,3,loyalty); gcs_service_cap (P,3,loyalty); gcs_tenure_courtesy (P,3,loyalty); gcs_redemption_size_goodwill (P,3,giftcard) | 5/1 | gcs_service_rate (tier ∧ active card) |

- Counts: every policy has 4–6 factors, >= 2 parameter, exactly 1 method; every policy has >= 1 multi-source and >= 1 cross-difficulty factor, so each task tree (P1–P3; P4–P7) satisfies the per-task floors on its own policies.
- `decides` is an input binding (never `result`) in every factor; binding sets within one policy are disjoint; tiers within each ladder are pairwise disjoint as stated (threshold ladders "at or above upper / at or above middle and below upper / otherwise"; enumerated variant/tier sets disjoint; P7 escalation ">= high / exactly middle / exactly low / otherwise" with high 3, middle 2, low 1).
- No two tiers of any ladder select the same value or method (checked value by value against `params`); every fall-through equals the factor's `baseline`, and each policy's `baseline.rule` names exactly those defaults (`baseline.params`).
- Every tier is stated in the rule with its condition and value/method, and implemented in compute (rule_compute_equivalence, above).
- Labels: all `method` factors change the algorithm (day-count conventions "counting both dates" / "not counting the start date" / "rounded down to whole weeks × 7"; P3's paid-share "proportional to uncovered share" / "less half the store value" / "less the whole store value"); all `parameter` factors substitute numbers. Each method tier is a computation the rule itself states. Labels honest.
- Realism (what a national department store would weigh / publish):
  - **P3 rpp_registry_status_goodwill — a compound-condition part that holds for every claimant.** Both non-fall-through tiers require that the registry "lists the item" (`d0_item_listed = XCOUNT(... registry_item_add, sku=F('sku'))`), while P3's scope sentence admits only "A registrant who bought an item that is listed on her own gift registry". Every customer who reaches this write satisfies that part; the ladder divides customers only by registry status. Finding CG-3.
  - **P6 dcr_bank_fee_allowance — "cash" in a bank-fee tier.** "A unit paid by debit card or cash whose latest capture is at least the bank-fee days old on the request date earns the debit bank-fee allowance" (fee_debit 35.00). A bank-fee allowance compensates fees a bank charges on an account a duplicate capture drew down; a cash tender draws on no bank account, so no retailer publishes a bank-fee allowance for a cash payment. Finding CG-4.
  - Observations (judgement calls, no single condition demonstrably unreal): every day-count method ladder is keyed to an attribute unrelated to how long money was held — card product (P2), loyalty tier (P4), card spend (P5), membership tenure (P6), whether any gift card is registered to the profile (P7); P1's per-day "standing accrual" on a price-accuracy credit and P2's registry-type goodwill are compensation forms with no common department-store analogue; P1/P6 put cash beside debit for "money left the customer's account" (P1) / a held-capture rate (P6). Recorded as CG-O7.
  - Tier resting on the conversation's own writes: P7 gcs_incident_escalation ("from the register-error corrections standing on the unit") and P3 rpp_paid_share_method (its tiers require store value on the unit, which counts the registry credit only once a no-new-price correction exists) take their tier from the prerequisite writes rather than from seeded records. They are the value channel of the declared edges, not a stamp. Observation CG-O8.

### findings

**CG-1 — SOURCE-POLICY RED (rule/compute non-equivalence; P1, P3). Bears on: task 0.**
- Symptom: `compute_basis` of `t0_member_spend`, `t0_spend_bonus` (P1) and `d0_member_spend`, `d0_spend_bonus` (P3) quotes "(purchase earn entries whose posting date falls less than twelve whole months before it)"; the rules say "(earn entries whose posting date ...)".
- Root cause: the compute filters `earn_source='purchase_base'` but the rule sentence names all earn entries; the basis was edited away from the rule.
- Evidence: order.extended.yaml P1 rule and `compute_basis.t0_member_spend`; P3 rule and `compute_basis.d0_member_spend`; loyalty.yaml `loyalty_points_earn.fields.earn_source` / `qualifying_amount`.
- Demonstrated consequence: in a world where a member's purchase_base earn rows in the window total 1,800.00 and card_bonus earn rows total another 1,800.00, P1's rule gives spend 3,600.00 → upper bonus 10.00, P1's compute gives 1,800.00 → middle bonus 5.00 (P3: 8.00 vs 4.00). On task 0's own world the two readings give 6,668.99 vs 3,564.49, both above the 2,500 upper thresholds, so the scored values do not move there (see 0.md).
- Affected: P1 `rule`/`compute_basis`/`compute.t0_member_spend`; P3 `rule`/`compute_basis`/`compute.d0_member_spend`.

**CG-2 — SOURCE-POLICY RED (prerequisite condition stronger than its sentence; P3→P2). Bears on: task 0 (not exercised).**
- Symptom: the sentence waits only on registry credit "spent on the unit and left undeducted"; `condition` demands a no-new-price register-error correction whenever any `registry_credit_use` names the unit.
- Evidence: P3 `prerequisite[1].policy_source` vs `prerequisite[1].condition`.
- Demonstrated consequence: unit with 100.00 registry credit spent and correctly deducted (captures = selling price + tax − notes − 100.00): sentence → no correction required, P3 may be settled now; condition → unmet until a P2 write (whose shortfall would be 0.00 plus courtesies). Task 0's credit is undeducted, so both agree there.
- Affected: P3 `prerequisite[1].condition`.

**CG-3 — SOURCE-FACTOR RED (unreal ladder: tier condition part restates scope; P3 rpp_registry_status_goodwill). Bears on: task 0.**
- Evidence: P3 rule "A registrant who bought an item that is listed on her own gift registry ..." and "A registrant whose registry is in its completion period and lists the item receives the completion registry status goodwill; one whose registry is still active before its completion period and lists the item receives the pre-event registry status goodwill"; compute `d0_item_listed`, `d0_registry_goodwill`.
- Consequence: "lists the item" holds of every customer who reaches this write; the factor is in substance a two-condition registry-status ladder with a decorative conjunct, and does not count as multi-source.
- Affected: P3 rule, `factors[rpp_registry_status_goodwill]`, compute `d0_item_listed`.

**CG-4 — SOURCE-FACTOR RED (unreal ladder: cash in a bank-fee tier; P6 dcr_bank_fee_allowance). Bears on: task 1 (tier taken there is the bank-card tier).**
- Evidence: P6 rule "A unit paid by debit card or cash whose latest capture is at least the bank-fee days old on the request date earns the debit bank-fee allowance"; `params.fee_debit: 35.00`; compute `dc_fee`.
- Consequence: the first tier pays a 35.00 bank-fee allowance to a cash payer, a treatment no department store publishes (no bank account, no bank fee).
- Affected: P6 rule, `factors[dcr_bank_fee_allowance].ladder[0]`, compute `dc_fee`.

Observations (no consequence demonstrable on either task world):
- CG-O1 — the record left by P2/P4/P5/P6 (and P7's own claim) is the same `register_price_error` row with no new unit price; P3's `d0_correction_count` and P7's `g1_corrections` test only that bare state, so the error kind of a correction is not record-visible.
- CG-O2 — P6 tender wording vs untendered capture count (see rule_compute_equivalence).
- CG-O3 — P7 redemption-size goodwill: Bonus Card inclusion is ambiguous in the rule; compute includes it.
- CG-O4 — base event-field gloss of `order_price_adjustment.amount` not reconciled by any overwrite.
- CG-O5 — "rounded half up" vs DSL `round` (half-even); no tie arises in either world.
- CG-O6 — uuid8 pair 1f084e1e / 1f1335fb share prefix "1f".
- CG-O7 — day-count methods keyed to unrelated attributes; per-day accrual / registry-type goodwill realism (factor_ladders).
- CG-O8 — P7 escalation and P3 paid-share tiers rest on the prerequisite writes, not on seeded records.

## closing_checklist

Written after both reveals (2026-10-13T16:01:15Z). The difficulty is **not closed**: not every task passes all four relationships.

| item | status |
| --- | --- |
| per-task files 1:1 with tasks (0.md, 1.md) beside this file; revision 1, no older revisions | yes |
| every comparison section carries PASS | **no** — task 0: SOURCE-POLICY RED (CG-1, CG-2), SOURCE-FACTOR RED (CG-3, T0-F1), SOURCE-TASK RED (T0-F2); task 1: SOURCE-FACTOR RED (CG-4) |
| extended policies fully covered; scopes pairwise disjoint | yes — `charter_scope` task 0 = {P1, P2, P3}, task 1 = {P4, P5, P6, P7}; union = all seven; intersection empty; each scope = its whole tree |
| task tools and GT closed; uuid8s independent and frozen | yes — each task's writes use only its own scope's tools; uuid8s distinct (CG-O6 noted) |
| each tree: 1–3 prerequisite problems, >= max(n−1,1) value_input, >= 1 user write, acyclic | yes — task 0: n=2, 2 value_input, user write P3; task 1: n=3, 3 value_input, user write P7; difficulty graph = two disjoint stars, acyclic, no cross-task edge |
| every computation: self-sufficient baseline, 4–6 factors (>= 2 parameter, 1 method), per task >= 1 multi-source and >= 1 cross-difficulty, ladders >= 3 tiers stated in the rule, distinct outcomes, real conditions/outcomes, every factor bears weight, all-baseline number definite and ≠ gold | counts, statements, weight and fall-back numbers: yes (all seven computations; see 0.md / 1.md factor_weight). Real ladders: **no** — CG-3 (P3) and CG-4 (P6). Rule/compute equivalence of the P1/P3 spend factor: **no** (CG-1) |
| instantiation-stage gates re-run on the final form | not re-run by this audit (outside the auditor's write/run scope per brief); the coordinator's snapshot above is the last gate state; artifacts unchanged since (hashes 592d61bbe4402769 / f185b76d932fd485) |

Per-task verdicts:
- task 0 — SOURCE-POLICY RED (charter CG-1, CG-2; scored values unchanged on its world) + SOURCE-FACTOR RED (CG-3; T0-F1 false "3277.29" card-spend figure in proof fields) + SOURCE-TASK RED (T0-F2 uniqueness proof cites a non-existent 2026-09-12 guest gift). Problem tree PASS. All scored arguments independently re-derived and equal to GT.
- task 1 — SOURCE-FACTOR RED (CG-4). Policy self-consistency, problem tree and unique solution PASS. All scored arguments independently re-derived and equal to GT.

## revision_2

### charter_global_frozen (r2)

- Re-audit round 2, same auditor; written before either r2 task JSON was opened. Gate snapshot: `/tmp/erl0061_coord/snapshot.sh purchases_returns_and_price_adjustments 2` (2026-10-13T19:55:06Z, saved as `.audit_views/policy/purchases_returns_and_price_adjustments/snapshot_r2.txt`): extended / task-tool contract / replay --check / solvability / compute / grounding / cross_fire all OK; traceability non-tool_name misses 0; validate_scenario errors all of the form "required document '…' not found" (counted by category: 24 across 4 difficulties, 7 of them this difficulty's). Entry conditions met; `rework_r2_claims.md` present (read in full before deriving; it carries no figures).
- Hashes: `order.extended.yaml` **f618d8f25844672d** (changed from 592d61bbe4402769) → every charter-global section re-derived in full below; `task_tools.py` f185b76d932fd485 (unchanged) → action_binding_and_uuids carried forward by reference to round 1. Masked views 0.json b80b78f4e88521d6, 1.json 9f3a466a8dbcd3a5. Blueprint files untouched (mtimes 12:09–12:11 local, before round 1). Base copy lines 1–1001 still byte-identical to `blueprint/products/order.yaml`.

### policy_conflict_scan (r2)
Same seven policies, targets, owners and prerequisite stars as round 1. Register-error kinds still disjoint by error kind; no policy reads `net_paid_amount` or another correction's amount; P3 reads P1's new price and the existence of a no-new-price correction, P7 the correction count. New conflicts introduced by the rework: R2-N1 (Bonus Card "in active status" in P5 and P7) and R2-N2 (P6 scope vs base mixed-tender capture rows) — see findings (r2).

### rule_compute_equivalence (r2)
`/tmp/audit_order_0061/chk.py` on the r2 charter: every `compute_basis` value is a verbatim substring of its rule; every `baseline.rule` sentence, `policy_source`, `replaced_by` in the rule; every `superseded_clause` in the base; params used == declared — all seven PASS. CG-1 wording: P1, P3 (and P5, P6, P7) rules now read "(purchase earn entries whose posting date …)", matching `earn_source='purchase_base'`. P6 scope now "more than one payment capture" = untendered `dc_captures` (CG-O2 wording gap closed, but see R2-N2). P7 size goodwill now "Bonus Card entries included" = `XMAX` over all redemptions (CG-O3 closed). Rounding observation CG-O5 unchanged (no tie in either world).

### action_binding_and_uuids (r2)
`task_tools.py` hash unchanged → round-1 section carried forward (7 tools, 1:1 with policies; no ordering words, no other tool named, no numeric examples; bodies validate nothing; CG-O6 unchanged).

### prerequisite_graph (r2)
Edges, kinds, gates, forms, `resolved_by` unchanged and acyclic. P3→P2 `condition` now: "Whenever the registry's ledger carries registry_credit_use entries naming the unit and the unit's order_payment captures exceed its unit_price plus tax_amount, less its finch_notes_applied and less that credit (the credit left undeducted), …" — same strength as the sentence (CG-2 closed). P3→P1 condition dropped "regular-price" (a unit_price above regular_price is the same set; no strength change). P7 edge conditions unchanged.

### prerequisite_sentences (r2)
All five sentences unchanged verbatim; four-point test and single-reading derivations as in round 1. CG-O1 unchanged (shared record shape). The P7→P5 sentence ("every Bonus Card redemption recorded against the unit and left undeducted") is now wider than what P5 computes for (active-status Bonus Card only) — R2-N1.

### override_declarations (r2)
Overwrite blocks unchanged in content and coverage (P1/P2/P4–P7 replace base S9; P3 replaces S6/S7/S8); `replaced_by` sentences still verbatim in the rules. Undeclared conflict outside `base_policy_refs`: R2-N2 (base `order_agg_order_allocation`).

### factor_ladders (r2)
| policy | factors (label, tiers, xd) | multi-source |
| --- | --- | --- |
| P1 | shelf_accuracy_share (P,3,loyalty); shelf_accuracy_cap (P,3,card); shelf_accuracy_spend_bonus (P,3,loyalty); shelf_standing_day_count (M,3,–, tender) | shelf_accuracy_share |
| P2 | rcs_daily_rate (P,3,registry: status of the registry holding the credit ∧ active card); rcs_held_day_count (M,3,–, tender); rcs_held_cap (P,3,card); rcs_registrant_courtesy (P,3,loyalty: registry type's `loyalty_bonus_applies` ∧ tier; percent of shortfall); rcs_tenure_courtesy (P,3,loyalty) | rcs_daily_rate, rcs_registrant_courtesy |
| P3 | rpp_paid_share_method (M,3); rpp_tenure_uplift; rpp_card_spend_cap; rpp_card_goodwill; rpp_registry_status_goodwill (P,3,registry: status of the registry recording the guest gift); rpp_member_spend_bonus | rpp_paid_share_method |
| P4 | nsr_service_rate; nsr_service_day_count (M, tender); nsr_service_cap; nsr_lapsed_goodwill; nsr_member_courtesy (P,3,loyalty tier) | nsr_service_rate, nsr_lapsed_goodwill |
| P5 | bcs_service_rate; bcs_service_day_count (M, tender); bcs_service_cap (P,3,card spend); bcs_member_spend_goodwill (P,3,loyalty spend) | bcs_service_rate |
| P6 | dcr_held_rate (P,3,loyalty: tier ∧ active card); dcr_held_day_count (M, tender); dcr_held_cap; dcr_bank_fee_allowance (P,3: debit / bank card only); dcr_member_spend_goodwill; dcr_capture_size_goodwill | dcr_held_rate, dcr_bank_fee_allowance |
| P7 | gcs_incident_escalation (P,4); gcs_service_day_count (M, tender); gcs_service_rate; gcs_service_cap; gcs_tenure_courtesy; gcs_redemption_size_goodwill | gcs_service_rate |
- Counts 4/5/6/5/4/6/6, each >= 2 parameter and exactly 1 method; every policy has >= 1 multi-source and >= 1 cross-difficulty factor. No two tiers of any ladder share a value or method; fall-through = baseline everywhere; every tier in rule and compute.
- CG-3 closed: rpp_registry_status_goodwill now divides claimants by the status (completion / active / other) of the registry recording the guest gift; no conjunct restates P3's scope.
- CG-4 closed: dcr_bank_fee_allowance tiers are "unit paid by debit card …" and "unit paid by bank credit card …"; cash falls to the 0.00 fall-through.
- CG-O7: every day-count method now keyed to the unit's tender (debit/cash counting both dates, bank card not counting the start date, other tenders weeks × 7) — closed as an observation. The registry-type goodwill is gone; its replacement (percent courtesy for registry types that carry the Finch Circle registry bonus, by tier) uses a charter parameter (`registry.yaml` `loyalty_bonus_applies`: Housewarming, Baby, Anniversary, Wedding true). No new unreal tier found.
- CG-O8 unchanged (escalation / paid-share tiers take value from the prerequisite writes).

### findings (r2)

Round-1 items: CG-1 **closed**; CG-2 **closed**; CG-3 **closed**; CG-4 **closed** (task-file proof items T0-F1/T0-F2 are judged in 0.md after reveal). Observations: CG-O2, CG-O3, CG-O7 closed; CG-O1, CG-O4, CG-O5, CG-O6, CG-O8 stand.

**R2-N1 — SOURCE-POLICY RED (new; P5 and P7: Bonus Card "in active status"). Bears on: task 1 (not exercised on its world).**
- Symptom: P5 "The Bonus Card shortfall is the total of the redemption entries naming the unit made with the customer's Bonus Card in active status …" (`b1_bonus_card = CFIELD('giftcard','gift_card_id', variant_name='Marlowe & Finch Bonus Card', status='active')`); P7 "The gift card shortfall is the total of the gift card redemption entries naming the unit, less those made with the customer's Bonus Card in active status …" — while P7's scope sentence covers only "a Marlowe & Finch gift card other than a Bonus Card" and its prerequisite sentence waits on "every Bonus Card redemption recorded against the unit and left undeducted".
- Root cause: the first-match probe guard ("the Bonus Card only when active") was written into the rules as a business condition.
- Demonstrated consequence: unit as in task 1 but the Bonus Card that paid 20.00 has since moved to `expired` (giftcard.yaml states include expired; its expiry passes): P5 → Bonus Card shortfall 0.00 (only courtesies refunded); P7's sentence still requires a Bonus Card correction; P7's formula no longer subtracts the 20.00, so gift card value = 170.00 and the Bonus Card part is paid on the gift card claim (without tax) although P7's scope excludes Bonus Cards. Two passages of P7 (scope vs formula) and P5 vs P7's prerequisite sentence reach different conclusions on one world. A customer holding two Bonus Cards (old one closed, new one active) gives the same split.
- Affected: P5 rule + `compute.b1_bonus_card`; P7 rule + `compute.g1_bonus_redeemed`.

**R2-N2 — SOURCE-POLICY RED (new, regression from the CG-O2 change; P6 scope vs base mixed tender). Bears on: task 1 (not exercised).**
- Symptom: P6 now reads "A unit whose payment records show more than one payment capture for the unit carries a second capture: the customer paid twice for one unit"; base `order_agg_order_allocation` (inherited, not overwritten): "A mixed-tender transaction is recorded with tender_type mixed on its purchase records and one order_payment row per tender per unit".
- Demonstrated consequence: a mixed-tender unit with a gift-card capture 150.00 and a bank-card capture 434.36 (one payment, two tenders) — base: nothing paid twice; P6: "paid twice", second capture = latest capture 434.36 refunded with credits. Round 1's wording ("its tender captured more than once") did not say this.
- Affected: P6 rule (scope sentence) and `compute.dc_captures` / `dc_second_capture`.

### closing_checklist (r2)

Written after the r2 reveal (2026-10-13T19:59:36Z). **Not closed.**
| item | status |
| --- | --- |
| per-task files 1:1, revision_2 appended, round-1 text untouched | yes |
| every comparison PASS | no — task 1 SOURCE-POLICY RED (R2-N1, R2-N2) |
| coverage / disjoint scopes | yes — `charter_scope` unchanged: task 0 {P1, P2, P3}, task 1 {P4, P5, P6, P7} |
| tools closed, uuid8s | yes (tools unchanged) |
| trees: 2 and 3 prerequisite problems, all value_input, user write each, acyclic | yes |
| factors: counts, baselines, ladders stated, distinct, real, bearing weight, all-baseline ≠ gold | yes for all seven computations (CG-3, CG-4 closed; no new unreal tier) |
| rule/compute equivalence | yes (CG-1 closed) |
| gates on the final form | coordinator snapshot r2 (above), not re-run by the auditor |

Round-1 RED status: CG-1 closed, CG-2 closed, CG-3 closed, CG-4 closed, T0-F1 closed, T0-F2 closed. No regression in task 0. New charter REDs: R2-N1, R2-N2 (both latent, both in task 1's tree).
Per-task verdicts r2: task 0 PASS; task 1 SOURCE-POLICY RED (R2-N1, R2-N2).

## revision_3

### charter_global_frozen (r3)
- Re-audit round 3; revision_2 was complete on disk before this round (closing_checklist (r2) present in all three files). Written before either r3 task JSON was opened.
- Gate snapshot `/tmp/erl0061_coord/snapshot.sh purchases_returns_and_price_adjustments 3` (2026-10-14T00:38:08Z, `snapshot_r3.txt`): extended / task-tool contract / replay --check / solvability / compute / grounding / cross_fire OK; traceability non-tool_name misses 0; validate_scenario errors only "required document '…' not found" (categorised). `rework_r3_claims.md` present, read before deriving, carries no figures.
- Hashes: `order.extended.yaml` **f3219e6e2c53ced1** (changed), `task_tools.py` **e71872c2b22813df** (changed) → every charter-global section re-derived. Views: 0.json b80b78f4e88521d6 (unchanged since r2), 1.json **0c78644c4f56db69** (changed). Copies frozen in `/tmp/audit_order_0061/r3/`. Base lines 1–1001 still identical to `blueprint/products/order.yaml`; blueprint untouched.

### policy_conflict_scan (r3)
Seven extended policies: P1 shelf correction, P2 registry credit shortfall, P3 registry price protection (user), P4 note shortfall, **P5′ order_ext_note_tax_refund → refund_note_tax_482f19cd (agent, new; the Bonus Card shortfall policy and tool are retired)**, P6 duplicate capture, P7 gift card shortfall claim (user, now covering Bonus Card redemptions too). Every carve-out sentence now lists the six sibling kinds. Caps of P2/P4/P7 measure "money captured on the unit by tenders other than gift cards" (`SUM(order_payment) − SUM(order_payment, tender_type='gift_card')`). P6 scope keyed to the tender of the latest capture captured more than once; one capture per tender on a mixed-tender unit is a single payment. Interactions: P4 and P5′ both arise from the same undeducted Finch Note but refund different quantities (the note's money vs the tax on the note's part) and read nothing of each other; writes still commute. New conflict: R3-N1 (below).

### rule_compute_equivalence (r3)
`chk.py` on the r3 charter: all `compute_basis` verbatim, all baseline sentences / prerequisite sentences / `replaced_by` in their rules, every `superseded_clause` in the base, params used == declared — PASS for all seven. P6 `dc_capture_tender`, `dc_captures` (tender-filtered), `dc_held_days`, `dc_fee` follow the latest capture's tender exactly as the rule states. P7 gift value = all redemptions naming the unit (scope, formula and size goodwill all say "Bonus Card entries included"). CG-O5 unchanged.

### action_binding_and_uuids (r3)
7 tools, 1:1 with policies; the retired `refund_bonus_card_shortfall_1f1335fb` is gone from the module and from the charter. New `refund_note_tax_482f19cd`: body = purchase lookup, one `register_price_error` row with no new price, `net_paid_amount` decrement; no check, no refusal; docstring names no other tool, no order word, no numeric example. uuid8 482f19cd unrelated to the other six. Other six tools' bodies/docstrings unchanged in substance.

### prerequisite_graph (r3)
Stars: P3 ← P1, P2 (unchanged); P7 ← P4, **P5′**, P6, all `value_input` on `g1_corrections`, `form: state`, acyclic; `resolved_by` = each target tool; conditions match sentence strength (P7→P5′ "loyalty_note_redeem entries naming the unit whose value exceeds the unit's finch_notes_applied … refunding the sales tax charged on that excess"; P7→P6 "the tender of the unit's latest order_payment was captured more than once").

### prerequisite_sentences (r3)
New P7 sentence: "The gift card shortfall refund is not settled until the sales tax charged on the part paid by every Finch Note recorded as redeemed on the unit but left undeducted carries its register-error correction on the unit's records." — connective "not … until", state named, no token, strength matches → resolves to P5′ (its scope: "sales tax charged on the part a Finch Note paid"). The P7→P4 sentence ("a register-error correction for every Finch Note recorded as redeemed … left undeducted") now sits beside a second write that is also a correction concerning that same note (P5′); the hop resolves to P4 only because the P5′ sentence names the tax separately — observation R3-O2 (CG-O1 class). P7→P6 sentence unchanged; resolves to the revised P6.

### override_declarations (r3)
Each extended policy still overrides base S9 only (P3 S6/S7/S8); `replaced_by` verbatim. No undeclared override of `order_price_adjustment_rules`. R2-N2's conflict with base `order_agg_order_allocation` is removed (mixed-tender single capture per tender is now a single payment). New conflict outside the refs: R3-N1.

### factor_ladders (r3)
P1–P4, P6, P7 as revision_2 (P4 unchanged except its amount no longer adds tax; P7 unchanged ladders). P5′: ntr_service_rate (P,3: Mastercard ∧ Gold+ / store card only ∧ Gold+ / other — multi-source), ntr_service_day_count (M,3, tender), ntr_service_cap (P,3, card spend 1,500/500), ntr_member_spend_goodwill (P,3, purchase earn 2,000/1,000). Counts 4/5/6/5/4/6/6; >= 2 parameter, 1 method, >= 1 multi-source and >= 1 cross-difficulty per policy; distinct tier values; fall-through = baseline; no unreal tier found.

### findings (r3)
- **R2-N1 closed**: no "active status" restriction on Bonus Cards anywhere; P7 scope/formula/size goodwill/overwrite all include Bonus Card redemptions; the Bonus Card shortfall problem no longer exists.
- **R2-N2 closed**: P6 scope "the tender of its latest payment capture captured more than once … whereas the one capture per tender recorded for a mixed-tender unit is a single payment" agrees with base `order_agg_order_allocation`.

**R3-N1 — SOURCE-POLICY RED (new). Bears on: task 1 (P4, P5′, P7; exercised in its world's records, scored values unchanged) and task 0 (P2's sentence; not exercised).**
- Symptom: P5′ rule: "the register figured sales tax on the full selling price; under the Marlowe & Finch tax schedule a Finch Note is a store discount that lowers the taxable price, so the tax charged on the part the note paid was charged in error." P2, P4 and P7 rules: "… less what those tenders should have paid (the unit's selling price plus its tax, less its applied Finch Notes …)", with "its tax" the recorded `tax_amount` on the full selling price (`F('tax_amount')` in `r0/n1/g1_credit…shortfall`). Base field: `unit_price` is "before Finch Notes and tax", capture = `unit_price + tax_amount − finch_notes_applied`.
- Root cause: P5′ introduces a tax schedule stated nowhere else, which makes the tax on any note-paid part an error, while the sibling policies and the base capture data treat the full-price tax as owed.
- Demonstrated consequence: task 1's own seed holds correctly applied notes taxed on the full price — `32ffba02…` unit 640.00, notes 10.00, tax 40.00 (6.25 % of 640.00; on 630.00 it would be 39.38) and `3ca59038…` unit 85.00, notes 10.00, tax 5.31 (on 75.00: 4.69). Under P5′'s schedule both carry tax "charged in error" that no policy addresses; under P2/P4/P7 they are correct. On the task-1 unit, P4's "should have paid" is 549.99 + 34.37 − 0.00 − 10.00 = 574.36, whereas P5′'s schedule gives 539.99 + 33.75 = 573.74. The caps do not bind on either task world, so no scored amount moves.
- Affected: P5′ rule (tax-schedule sentence); P2/P4/P7 "should have paid" sentences; task 1 seed rows `32ffba02…`, `3ca59038…`.

Observations: R3-O1 — splitting one undeducted Finch Note into two separate register-error corrections (money, then tax) has no evident department-store practice behind it; it reads as a split made to supply a prerequisite. R3-O2 — see prerequisite_sentences. CG-O1, CG-O5, CG-O6, CG-O8 stand.

### closing_checklist (r3)
Written after the r3 reveal (2026-10-14T00:41:25Z). **Not closed.**
| item | status |
| --- | --- |
| files 1:1, revision_3 appended, earlier revisions untouched; revision_2 found complete | yes |
| every comparison PASS | no — R3-N1 open (task 1 exercised in seed records; task 0 by citation of P2's sentence) |
| coverage / disjoint scopes | yes — task 0 {P1, P2, P3}; task 1 {P4, P5′, P6, P7}; seven policies, no overlap, no orphan |
| tools closed, uuid8s independent | yes (refund_note_tax_482f19cd new; retired Bonus Card tool removed) |
| trees | task 0: n=2, 2 value_input, user write; task 1: n=3, 3 value_input, user write; acyclic |
| factors | counts, baselines, ladders, weight, all-baseline ≠ gold: yes for all seven |
| gates on final form | coordinator snapshot r3; not re-run by the auditor |

Round-2 RED status: R2-N1 closed, R2-N2 closed. Task 0: no regression in world, tree or figures. Open charter RED: R3-N1.
Per-task verdicts r3: task 0 SOURCE-POLICY RED (R3-N1 by citation, not exercised); task 1 SOURCE-POLICY RED (R3-N1).

## revision_4

### charter_global_frozen (r4)
- Re-audit round 4; written before either r4 task JSON was opened. Snapshot `/tmp/erl0061_coord/snapshot.sh … 4` (2026-10-14T19:59:42Z, `snapshot_r4.txt`): all gates OK; traceability non-tool_name misses 0; validate_scenario errors only "required document '…' not found". `rework_r4_claims.md` present, read first, no figures.
- Hashes: `order.extended.yaml` **c48dc7f1c6a70bc3** (changed) → charter-global sections re-derived; `task_tools.py` e71872c2b22813df (unchanged, byte-identical to the r3 copy) → action_binding_and_uuids carried forward from revision_3; view 0.json b80b78f4e88521d6 (byte-identical to r3); view 1.json **18695baf2db29a8b** (changed). Copies in `/tmp/audit_order_0061/r4/`. Base lines 1–1001 identical to blueprint.

### delta and re-derivation (r4)
Mechanical r3→r4 diff of the seven extended policies: only tax-related rule sentences, their compute bindings and `baseline.rule` text changed; factors, params, overwrites and prerequisites are unchanged.
- P1, P3: tax on the overcharge / protected difference now divides by "the unit's selling price less the Finch Notes applied on its record … nothing when that divisor is zero, Finch Notes being a store discount under the Marlowe & Finch sales tax schedule".
- P2, P4, P7: "should have paid" is now a per-policy due amount: "the unit's selling price less the larger of the Finch Notes applied on its purchase record and the notes the ledger shows redeemed on it, plus the tax due on that taxed price, which is the tax recorded on the unit times that taxed price divided by the unit's selling price less the Finch Notes applied on its record".
- P5′: "Under the Marlowe & Finch sales tax schedule a Finch Note is a store discount, so sales tax is due only on a unit's selling price less the Finch Notes it was paid with …"; refund = recorded tax − tax due on the note-taxed price.
- `chk.py`: all bases verbatim, baseline/prerequisite/replaced_by sentences in rules, superseded clauses in base, params used == declared — PASS. Factor tables, prerequisite graph and sentences, and overwrite coverage as revision_3 (unchanged objects).

### findings (r4)
- **R3-N1 closed.** Every passage that uses a tax base now states one schedule (notes are a store discount); no sibling treats the full-price tax as owed on a note-paid part; task 1's applied-note purchases are re-seeded on that schedule (`32ffba02…` tax 39.38 = 6.25 % × 630.00, capture/card charge/payment 669.38; `3ca59038…` tax 4.69 = 6.25 % × 75.00, 79.69), so the rationale's "correct captures" is now true.
- **R4-N1 — SOURCE-POLICY RED (new; extended tax schedule vs base `order_price_adjustment_rules` S8). Bears on: task 0 and task 1 (not exercised in either world).**
  - Symptom: base S8 (in force for every ordinary price-drop adjustment; P3's overwrite says "every other price-drop adjustment remains under the base rule"): "The adjustment refunds that difference plus the sales tax charged on it (the unit's tax_amount times the difference divided by unit_price, rounded half up to the cent)". The extended charter now asserts, as a company-wide fact (P5′, and in the P1–P4/P7 tax sentences), that sales tax is due "only on a unit's selling price less the Finch Notes it was paid with", and P1/P3 changed exactly this divisor from the selling price to the selling price less applied notes for that reason.
  - Root cause: the schedule is introduced in extended text only; the base S8 apportionment, which divides by the full selling price, cannot be rewritten and is overwritten only for P3's claim.
  - Demonstrated consequence: unit 640.00 with a 10.00 note applied and tax 39.38 (task 1's `32ffba02…`), M&F price drops to 600.00 (difference 40.00). Base S8: tax refunded 39.38 × 40 / 640 = 2.46. Schedule (as P1/P3 apply it): 39.38 × 40 / 630 = 2.50, equal to 39.38 − 6.25 % × 590.00 = 2.50. Two passages, one situation, two refunds.
  - Affected: base S8 (read-only) against P5′'s schedule sentence and the P1/P3 tax sentences.
- Realism of the replacement prerequisite (P5′ note-tax refund): treating a loyalty reward note as a store discount that lowers the taxable price matches common US practice for retailer-issued rewards (e.g. Massachusetts treats store coupons as reducing the sales price), and booking a sales-tax correction as its own adjustment is plausible accounting. What is synthetic is the customer-facing layer: a per-day service credit (up to 8.00) and a spend goodwill (up to 6.00) attached to a 0.62 tax correction, and a second service credit for the same undeducted note already compensated by P4. No single tier is unreal by the skill's test, so this stays an observation (R4-O1, replacing R3-O1).
- Observations standing: CG-O1, CG-O5, CG-O6, CG-O8, R3-O2.

### closing_checklist (r4)
Written after the r4 reveal (2026-10-14T20:01:42Z). **Not closed.**
| item | status |
| --- | --- |
| files 1:1; revision_4 appended; earlier revisions untouched | yes |
| every comparison PASS | no — R4-N1 open (both tasks by citation, not exercised) |
| coverage / disjoint scopes; tools; uuid8s | yes (unchanged from r3) |
| trees (n=2 / n=3, all value_input, user write, acyclic, edges bear weight) | yes |
| factors (counts, baselines, ladders, weight, all-baseline ≠ gold) | yes |
| gates on final form | coordinator snapshot r4; not re-run by the auditor |

Round-3 RED status: R3-N1 closed. Task 0: no regression (world byte-identical, figures identical). Open charter RED: R4-N1.
Per-task verdicts r4: task 0 SOURCE-POLICY RED (R4-N1, by citation); task 1 SOURCE-POLICY RED (R4-N1, by citation).

## revision_5

### charter_global_frozen (r5)
- Re-audit round 5; written before either r5 task JSON was opened. Snapshot `/tmp/erl0061_coord/snapshot.sh … 5` (2026-10-14T20:42:59Z, `snapshot_r5.txt`): all gates OK; traceability non-tool_name misses 0; validate_scenario errors only "required document '…' not found". `rework_r5_claims.md` present, read first, no figures.
- Hashes: `order.extended.yaml` **ad9c8cf8d2e6c7fb** (changed) → charter-global re-derived; `task_tools.py` e71872c2b22813df and both views (0.json b80b78f4e88521d6, 1.json 18695baf2db29a8b) byte-identical to the r4 copies → tool section and both worlds carried forward. Copies in `/tmp/audit_order_0061/r5/`. Base lines 1–1001 identical to blueprint.

### delta and re-derivation (r5)
r4→r5 diff: only tax sentences, their bindings, `baseline.rule` text and P5′'s params changed; factors (ids, labels, ladders' conditions), prerequisites and overwrites unchanged.
- P1, P3: tax divided by the unit's selling price again — the base S8 apportionment.
- P2, P4, P7 due amounts: "the unit's selling price plus the tax recorded on it, less the larger of the Finch Notes applied … and the notes the ledger shows redeemed on it, and less the tax recorded on the part of the price paid by redeemed notes beyond those applied, which is the tax recorded on the unit times that part divided by the unit's selling price".
- P5′: scope "the unit was charged sales tax on the part of its price the note had already paid; … refunds the tax recorded on that part, apportioned the way price adjustments apportion tax"; refund = recorded tax × undeducted note value / selling price. Params rescaled (rates 0.10 / 0.05 / 0.02; caps 1.00 / 0.50 / 0.25; goodwill 1.00 / 0.50 / 0.00).
- Sweep: no passage contains "store discount", "tax schedule" or "taxable" (grep over the extended file). `chk.py`: bases verbatim, baseline/prerequisite/replaced_by sentences in rules, superseded clauses in base, params used == declared — PASS. Factor counts 4/5/6/5/4/6/6 unchanged; P5′ tier values pairwise distinct; fall-through = baseline.

### findings (r5)
- **R4-N1 closed.** Every extended tax figure now apportions recorded tax by the selling price, exactly as base S8 does; no company-wide schedule is asserted. Ordinary price drop on `32ffba02…` (−40.00): base S8 2.46; no extended passage gives another figure.
- R3-N1 stays closed: P5′'s case statement (tax on the note-paid part of an undeducted note is refunded) and the P2/P4/P7 due amounts (which subtract the same apportioned tax) give one figure for that part (task 1 unit: 34.37 × 10.00 / 549.99 = 0.62); applied-note purchases are untouched records with no passage judging them.
- Realism R4-O1: P5′'s courtesy layer now tops out at 1.00 credit + 1.00 goodwill on a 0.62 correction — proportionate; observation closed.
- No new defect found. Observations standing: CG-O1, CG-O5, CG-O6, CG-O8, R3-O2.

### closing_checklist (r5)
Written after the r5 reveal (2026-10-14T20:44:10Z). **Closed at the source layer.**
| item | status |
| --- | --- |
| per-task files 1:1 with tasks; `_difficulty.md` beside them; revisions 1–5 appended in order, earlier text untouched | yes |
| every comparison section carries PASS | yes — task 0 PASS, task 1 PASS (revision_5) |
| extended policies fully covered; scopes pairwise disjoint over whole trees | yes — task 0 {shelf correction, registry credit shortfall, registry price protection}; task 1 {note shortfall, note tax refund, duplicate capture, gift card shortfall claim}; seven policies, no overlap |
| task tools and GT closed; uuid8s independently generated and frozen | yes — 7 tools 1:1 with policies (CG-O6 noted) |
| trees: 1–3 prerequisite problems, >= max(n−1,1) value_input, >= 1 user write, acyclic; difficulty graph a DAG | yes — n=2 (2 value_input, user write) and n=3 (3 value_input, user write); two disjoint stars |
| computations: self-sufficient baseline, 4–6 factors (>= 2 parameter, 1 method; per task >= 1 multi-source, >= 1 cross-difficulty), ladders >= 3 tiers stated in the rule, distinct and realistic tiers, every factor bears weight, all-baseline definite and ≠ gold | yes — all seven computations (fall-backs 41.38, 100.70, 0.00, 10.70, 0.76, 588.11, 150.70) |
| instantiation-stage gates on the final form | coordinator snapshot r5 (2026-10-14T20:42:59Z): all OK; traceability misses only unlock tool_name (KB-side); validate only "required document not found"; not re-run by the auditor |

Round-4 RED status: R4-N1 closed. No open charter RED. Open observations: CG-O1, CG-O5, CG-O6, CG-O8, R3-O2, R5-O1.
Per-task verdicts r5: task 0 PASS; task 1 PASS.

## revision_6

### charter_global_frozen (r6)
- Re-audit round 6, triggered by the order renderer's source report `audits/render_source/purchases_returns_and_price_adjustments/render_r1_order.md` (read in full: 4 items, no figures). Written before either r6 task JSON was opened.
- Snapshot `/tmp/erl0061_coord/snapshot.sh … 6` (2026-10-14T21:22:54Z, `snapshot_r6.txt`): all gates OK; **traceability OK** (KB now published); **validate_scenario VALID** (352 documents). `rework_r6_claims.md` present, read first, no figures.
- Hashes: `order.extended.yaml` **cf849136c6d43f83**, `task_tools.py` **7b0884208f2ff063** (both changed) → charter-global and tool sections re-derived; views 0.json b80b78f4e88521d6 / 1.json 18695baf2db29a8b byte-identical to r5 → worlds carried forward. Copies in `/tmp/audit_order_0061/r6/`. Base lines 1–1001 identical to blueprint.

### auditor_miss_disclosure (r6)
Renderer items 1–3 were present in the charter my revisions 2–5 passed, and item 4 since revision 1:
- Item 1 (`rcs_registrant_courtesy` reading `r0_credit_registry`, a binding then owned by `rcs_daily_rate`) entered in r2. My revision_2 `factor_ladders` restated "binding sets within one policy are disjoint" from round 1 without re-running the dependency check on the new bindings.
- Item 2 (`n1_rate` linked tier without an active membership): I saw this in r2 and judged it "fine" without comparing it to the rule's "whose active membership was enrolled fewer than the veteran months" — a wrong call.
- Item 3 (`dc_fee` with no second-capture test): not compared against the rule's "a second capture made by …" wording after r3.
- Item 4 (`correct_shelf_price_8a80c6f7` docstring "the corrected price on the order"): my action_binding checks covered ordering words, other tool names and example values, not effect claims against the body.
None of these moved a scored value on either task world (all four are absent-record or single-record cases, or docstring text). Revision_6 adds three mechanical checks: factor-dependency closure, tier-vs-compute on absent/single-record cases, and docstring effect vs body.

### delta and re-derivation (r6)
r5→r6 mechanical diff:
- P2: `rcs_daily_rate` bindings now [r0_registry_status, r0_any_card, r0_held_rate]; `r0_credit_registry` is a non-factor binding with basis "A registrant whose registry holding the spent credit is in its completion period …" (verbatim in rule).
- P3: prerequisite[0].effect now "records the shelf ticket price as the new unit price on its entry".
- P4: `n1_rate` linked tier adds `EXISTS('loyalty', status='active')`.
- P6: rule day-count and bank-fee sentences now end "… in every other case, including a unit with no second capture …"; `dc_held_days` and `dc_fee` require `dc_captures > 1`. The ladders read "second capture made by …".
- Tools: only the docstrings of `correct_shelf_price_8a80c6f7` and `claim_registry_price_protection_38d04d45` changed (corrected/lower price "recorded only on the new price adjustment entry"; "the unit's selling price on the purchase record is left as rung/charged"); bodies byte-identical.

Checks:
- `chk.py`: bases verbatim, baseline/prerequisite/replaced_by sentences in rules, superseded clauses in base, params used == declared — PASS.
- Factor-dependency closure (each factor's bindings followed transitively through non-factor bindings): no factor reads a binding owned by another factor, and no binding is owned by two factors, in any of the seven policies.
- Tier vs compute on absent/single-record cases (no active membership / card / registry credit or gift / expired note / redemption / correction; single capture): every compute branch takes the tier the rule names; P6's rate, cap and goodwill tiers name no second-capture condition and the compute applies none, so the two agree.
- Docstring effect vs body (all 7 tools): each body creates one `order_price_adjustment` row, copies the refund tender, lowers `net_paid_amount`, and touches nothing else. Every stated effect matches. No ordering word (beyond "before it is passed"), no other tool name, no numeric example.

### findings (r6)
- Renderer item 1 **closed**; item 2 **closed**; item 3 **closed** (fee and day count); item 4 **closed** (both price docstrings and the P3 effect sentence).
- No new defect. Factor counts, ladders, baselines, prerequisite graph and sentences, overwrites unchanged from revision_5. Observations standing: CG-O1, CG-O5, CG-O6, CG-O8, R3-O2; R5-O1 is judged in 1.md after reveal.

### closing_checklist (r6)
Written after the r6 reveal (2026-10-14T21:24:23Z). **Closed at the source layer.**
| item | status |
| --- | --- |
| files 1:1; revisions 1–6 appended in order, earlier text untouched; auditor misses of r2–r5 disclosed above | yes |
| every comparison PASS | yes — task 0 PASS, task 1 PASS |
| coverage / disjoint scopes; tools closed; uuid8s | yes (unchanged from r5) |
| trees (n=2 and n=3, all value_input, user write each, acyclic, edges bear weight) | yes |
| factors (4–6, >= 2 parameter / 1 method, multi-source and cross-difficulty per task, ladders in rule, distinct and realistic, bearing weight, all-baseline ≠ gold, no cross-factor binding reads) | yes |
| rule/compute and docstring/body equivalence including absent- and single-record cases | yes |
| gates on final form | coordinator snapshot r6: all OK, traceability OK, validate_scenario VALID; not re-run by the auditor |

Renderer items 1–4 closed; R5-O1 closed. No open charter RED. Open observations: CG-O1, CG-O5, CG-O6, CG-O8, R3-O2.
Per-task verdicts r6: task 0 PASS; task 1 PASS.
