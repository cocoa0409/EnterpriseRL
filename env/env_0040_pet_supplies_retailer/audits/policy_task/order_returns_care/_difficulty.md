# Policy-task audit — order_returns_care / charter-global

## charter_global_frozen

- Freeze time: 2026-10-06T06:01Z (written before any task's GT was revealed; nothing in this section derives from a revealed GT).
- Auditor: Claude (Opus 5.5), erl-task-policy-audit, independent of the instantiating agent.
- Frozen inputs (sha256, re-verified against the orchestrator's freeze-hashes before reading):
  - `tasks/order_returns_care/order.extended.yaml` 62e343659abe5d297ecff8485f10b65462f2f8be1bcd2456d8ddedca368145ad
  - `tasks/order_returns_care/task_tools.py` 886a2ac1055ac771f7654b7a5d0326ab62e5580a80b51ede74c0b759e53b7262
- Permitted: `blueprint/` (blueprint.yaml, db_schema.json, share_tools.py, products/order.yaml, products/autoship.yaml, products/member.yaml for cross-reads), the extended charter, task_tools.py, the two masked views.
- Masked and unread at the time of writing: `tasks/order_returns_care/tasks/*.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), `env/env_0040_pet_supplies_retailer/worklog.md`, every other `env/` scenario, every sibling difficulty's tasks directory and every other audit directory.
- Entry conditions (Step 0): gate snapshot `/tmp/e40views/policy_task/order_returns_care/gate_snapshot.txt` supplied — check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all `OK`/exit 0; check_traceability deferred by the orchestrator until the KB is published (recorded, not run by the auditor). Masked views supplied with sha256 e32d3ead…0472 (task_0) and 4a9ebf32…6e52 (task_1); both re-hashed and matching.
- Base-copy check: `head -1344 order.extended.yaml` vs `blueprint/products/order.yaml` — identical except one trailing blank line (diff `1343a1344 > ""`). Base section is verbatim.

### policy_conflict_scan

Extended policies (5): P1 `order_ext_freight_missed_appointment_refund` (agent, order_fee_refund, refund_freight_service_failure_8da9af3d), P2 `order_ext_freight_rebooked_redelivery_fee` (user, order_fee_charge, book_paid_freight_redelivery_0935dc22), P3 `order_ext_error_return_refund` (agent, order_return_refund, refund_error_return_9d87fcb3), P4 `order_ext_returnless_damage_credit` (user, order_damage_credit, accept_returnless_damage_refund_2d82d69e), P5 `order_ext_late_delivery_fee_refund` (agent, order_fee_refund, refund_order_fulfillment_fee_03b15c6d).

- Overlapping subject `order_fee_refund`: P1, P5, base `order_cancellation`, base `order_delivery_promises`. Domains are disjoint: P1 requires a Large Item Freight Delivery order "not yet completed"; P5 requires "an order whose method has late_delivery_fee_refund true, that was completed after its promised date" and freight has `late_delivery_fee_refund: false` (order.yaml l.455); base cancellation refunds a fee only on a cancel before ship/ready. No overlapping order state reaches two of them.
- Overlapping subject `order_return_refund`: P3 vs base `order_returns`. P3 narrows to received authorizations with a waived reason and declares the replaced amount sentence (see override_declarations).
- Overlapping subject `order_damage_credit`: P4 vs base `order_damage_missing_claims` (amount not stated in base; see override_declarations).
- `order_fee_charge` (P2) overlaps base `order_agg_fees` and `order_delivery_promises`; the redelivery fee is a separate fee kind from the fulfillment fee; the base redelivery sentence is declared superseded.
- Time anchors: P1/P2 count days from `placed_on` to today; P3 from `received_on`; P4 from `completed_date` to report date and `promised_date`→`completed_date`; P5 `promised_date`→`completed_date`. No anchor is shared with a contradictory reading.
- Cross-category read boundaries: P1 member+autoship, P2 member, P3/P4/P5 autoship; all declared in `cross_category`.
- Scope exclusivity (derived from the policy graph and the two masked worlds, before reveal): task 0 world is a shipped freight order (P2 root, P1 prerequisite); task 1 world is a completed Expedited order (P5 root, P3 + P4 prerequisites). The two trees {P1,P2} and {P3,P4,P5} are disjoint and jointly cover all 5 extended policies.
- Difficulty claim: blueprint.yaml l.122-126 claims event_types `[order_update, order_cancel, order_line_cancel, order_fee_refund, order_return_refund, order_damage_credit, order_replacement_ship]`. P2's subject `order_fee_charge` is not among them (and no other difficulty claims it). Recorded as observation O-7.

### rule_compute_equivalence

Swept each `compute` binding against its `compute_basis` quotation and back over each rule sentence.

- P1: every quantity is quoted (freight fee, refunds already booked, redelivery count, attempts beyond `carrier_attempts_before_return`, the "less one more while the order's promised date … is today or later", days from placed date, the three added shares, the Autoship window ladder, the member multiplier, cap and single half-up rounding). Sweep-back gap: the rule's scope sentence "A Large Item Freight Delivery order that is not yet completed …" has no compute counterpart (`result` gates only on `missed_paid_appointments >= 1`) — observation O-1.
- P2: all bindings quoted; scope sentence "whose included delivery attempts have failed" not encoded — observation O-1.
- P3: `units_received_back`/`received_reason`/`received_method`/`received_date` use `LATEST(..., status='received')` with no reason filter while the rule settles "the latest such authorization" = in status received AND reason in `return_fee_waived_reasons`; they diverge when a later received non-error authorization sits on the same order — observation O-2. `unit_list_price` is `MAX(unit_price_usd)` over all line charges while the rule says "the unit list price on the line charge" — diverges on multi-line orders (O-3). Everything else (allowance, wait, drop-off, repeat-issue = all error-reason authorizations − 1, Autoship tenure, half-up once at end, `result` gated on waived reason) matches.
- P4: all bindings quoted; `line_unit_list_price` same MAX issue (O-3); the cap compares the unrounded sum with `returnless_refund_max_usd`, as the rule ("Where that sum is above …").
- P5: all bindings quoted; lateness ladder 4 tiers (≥5, 3–4, exactly 2, else standard). The rule clause "a delay caused by the customer's absence or a changed address is never late" is represented only by `delivery_attempts == 0` (O-10).
- Factor ladders vs rule: every `factors[].ladder` tier of every policy is a sentence of the rule and a branch of its `decides` binding; no compute branch lacks a rule tier.
- Rounding: rules say "rounded half up"; the runtime `RND` is Python `round` on floats (skills/erl-task-instantiate/scripts/check_compute.py l.388). No gold-relevant value in either world lands on a half-cent tie (checked in the task files), so observation O-8 only.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: (refund_freight_service_failure_8da9af3d, amount_usd) P1; (book_paid_freight_redelivery_0935dc22, amount_usd) P2; (refund_error_return_9d87fcb3, amount_usd) P3; (accept_returnless_damage_refund_2d82d69e, amount_usd) P4; (refund_order_fulfillment_fee_03b15c6d, amount_usd) P5. Each claimed by exactly one policy.
- Docstrings: `grep -w -i "before|after|first|then|prior|until|once"` over task_tools.py returns nothing; no docstring names another tool or a sequence position.
- Tool bodies: each only `find`s the order, books one ledger row, updates `billed_total_usd` (P2 also `promised_date`, P3 also the RMA status). No body validates eligibility, timing or any prerequisite and none returns an error or hint.
- uuid8s: 8da9af3d, 0935dc22, 9d87fcb3, 2d82d69e, 03b15c6d — pairwise distinct, no shared prefix/suffix, no sequence pattern. PASS.
- Business-reading note: `refund_order_fulfillment_fee_03b15c6d` accepts `fee_kind=freight`, so it could physically book a freight fee refund; P5's scope (late_delivery_fee_refund true) excludes freight orders, so it never competes with P1 under the policy.

### prerequisite_graph

Edges: P2 → P1 (`value_input`, gate `carrier_fault_rate`); P5 → P3 (`value_input`, gate `error_units_settled`); P5 → P4 (`value_input`, gate `error_units_settled`). P1, P3, P4 have `prerequisite: []`.
- Every `problem` is an extended policy id of this file, none self-referential; graph acyclic.
- Each `policy_source` verbatim locatable in its own policy's rule (whitespace-normalised substring check) — 3/3; none restated in the depended-on rule.
- All `form: state`, no `fallback_reason` — consistent.
- `resolved_by` equals the depended-on policy's `target_tool` — 3/3. Each gate binding exists in the blocked policy's compute.
- `condition`s: P2 edge "freight service-failure refund total on the order is above zero" — narrower than the sentence's "the service-failure refund owed for each paid appointment the carrier did not keep" when two or more appointments are missed (O-5); P5 edges state "no return authorization … left in status received" and "each declined damage report … has a damage credit entry", matching their sentences.
- No authoring-viewpoint phrasing ("in this task", "at the opening") in any `prerequisite` field.

### prerequisite_sentences

1. P2 ← P1: "The fee for a rebooked freight redelivery is fixed only after the order's freight fee carries the service-failure refund owed for each paid appointment the carrier did not keep." Connective "only after"; state form (freight fee carries a refund — visible as an `order_fee_refund` row, fee_kind freight); no tool, id or snake_case token. Writers that bring the state about: only P1's tool books a "service-failure refund" (P1's own term); P5's tool cannot apply to a freight order under P5's scope. Derivation: sentence → reader looks for the policy whose rule produces "a service-failure refund against its freight fee" → P1 ("… receives a service-failure refund against its freight fee") → P1's tool. Single reading. Strength caveat O-5.
2. P5 ← P3: "The fulfillment fee refund is not worked out until every return authorization on the order that has been received carries its refund entry." Connective "not … until"; state form; record-visible (RMA received, `order_return_refund` row with that rma_id). Writers: within this difficulty only `refund_error_return_9d87fcb3` books an `order_return_refund` (share_tools.py has no write besides identity and transfer). For a received authorization with a waived reason the single reading is P3. For a received non-error authorization no writer exists (P3: "a return for any other reason is outside it and is refunded under the base return rule", and no tool performs the base refund) — O-6.
3. P5 ← P4: "Before the fulfillment fee refund is worked out, every damage report on the order that was declined because the damaged item stays with the customer must carry its returnless damage credit." Connective "Before"; state form; P4's own definition ("A damage report on file is a return authorization request with reason damaged that was declined (status rejected) because the damaged item stays with the customer") makes the hop single-reading; only `accept_returnless_damage_refund_2d82d69e` books `order_damage_credit`. The sentence is unconditional while P4's credit exists only "Where the customer chooses a refund rather than a free replacement" and the sum is not above `returnless_refund_max_usd` — O-6.
- No rule states a cross-problem order outside these three sentences. No base sentence is used to ground an edge.

### override_declarations

- P1 (refs order_cancellation, order_delivery_promises, order_agg_fees): declares superseding the late-delivery clause of order_delivery_promises. No base sentence forbids a service-failure refund on a not-completed freight order; cancellation sentences ("A shipped order cannot be cancelled") are followed; order_agg_fees followed. The same base clause is also declared superseded by P5 with a different `replaced_by` — O-4.
- P2 (refs order_agg_fees, order_delivery_promises): "A freight order whose included attempts failed may be redelivered for redelivery_fee_usd" declared superseded. `delivery_signature_required` sentence followed. order_agg_fees concerns the fulfillment fee only — followed.
- P3 (refs order_returns, order_evt_rewards): sentence by sentence — authorization on one line (follow), completed status (inherit), return window (inherit), 0-day/final-sale (inherit), units not over-refunded (inherit), allowed return method (inherit), received in time within `rma_validity_days` (inherit), refund amount = price paid after allocated discounts × units (declared superseded), deductions only on changed-mind / waived reasons no deduction (follow — P3 books deduction 0 on waived reasons only), fulfillment fee on full error return (superseded by P5's declaration), refund_method (follow). order_evt_rewards points reversal inherited (no task write books points; fees never earn).
- P4 (refs order_damage_missing_claims, order_evt_rewards; `overwrite: []`): completed-order responsibility (follow), report window `damage_report_days` (inherit), wrong item as return (follow), customer's choice replacement vs refund (follow — rule: "Where the customer chooses a refund rather than a free replacement"), returnless only up to `returnless_refund_max_usd` (follow — P4 compares the whole credit), units not over-refunded (inherit). The base states no amount for a damage credit (`refund_price_basis` is defined as "amount refunded for a returned unit" and used only by order_returns), so P4's amount fills an unstated quantity rather than overriding a base sentence. No undeclared override found.
- P5 (refs order_cancellation, order_delivery_promises, order_returns): late-delivery clause and "The fulfillment fee is refunded only when every line is returned for a Tailwise error …" both declared superseded; "a delay caused by the customer's absence or a changed address is never late" kept verbatim in P5's rule; return-to-sender sentence follows.
- Disguised forms: no anonymous intermediate, 0/1 multiplier or dropped branch that contradicts an undeclared base sentence found. No author text calls a base output "wrong".

### factor_ladders

| Policy | Factor | Label | Ladder tiers | Cross-diff | Multi-source | Label honest? |
|---|---|---|---|---|---|---|
| P1 | undelivered_days | parameter | 3 (0.40/0.30/0.20) | – | no | yes |
| P1 | item_value | parameter | 3 (0.10/0.05/0) | – | no | yes |
| P1 | rewards_tenure | parameter | 3 (0.05/0.025/0) | member | no | yes |
| P1 | autoship_window | method | 3 (24/18/12 months) | autoship | no | **no** — tiers substitute a window length (a number) into the same shipment count |
| P1 | autoship_volume | parameter | 3 (0.04/0.02/0) | autoship | no | yes |
| P1 | plus_member_multiplier | method | 3 (×2.0/×1.5/×1) | member | yes (tier+status on membership AND fee row in member_events) | **no** — tiers substitute a multiplier into the same product |
| P2 | repeat_booking | parameter | 3 (69/59/49) | – | no | yes |
| P2 | crew_handling | parameter | 3 (25/15/0) | – | no | yes |
| P2 | plus_rebooking_rate | parameter | 3 (0.50/0.75/1) | member | yes | yes |
| P2 | carrier_fault | parameter | 3 (0.25/0.50/1) | – | yes (fee-refund rows AND redelivery count/attempts/promised date) | yes |
| P2 | open_order_age | method | 3 (×0.6/×0.8/×1) | – | no | **no** — a multiplier substituted into the same product |
| P3 | autoship_price_basis | method | 3 (list price / paid + half discounts / paid) | autoship | no | yes |
| P3 | error_kind, refund_wait, return_dropoff, repeat_issue, autoship_tenure | parameter ×5 | 3 each | autoship_tenure | no | yes |
| P4 | prompt_report_value | method | 3 (list / paid + half discounts / paid) | autoship | yes (report date vs completed date AND Autoship shipments) | yes |
| P4 | damage_severity, late_arrival, multi_issue, subscriber_tenure | parameter ×4 | 3 each | subscriber_tenure | no | yes |
| P5 | lateness | parameter | 4 (0.80/0.40/0.30/0.25) | – | no | yes |
| P5 | error_settled, repeat_issue_count, autoship_patron, basket_value | parameter ×4 | 3 each | autoship_patron | no | yes |
| P5 | autoship_claims | method | 3 (×1.10/×1.05/×1) | autoship | yes (claim refunds AND shipments, distinct rows) | **no** — a multiplier substituted into the same product |

- Counts per policy (declared): P1 6 (4 param, 2 method), P2 5 (4/1), P3 6 (5/1), P4 5 (4/1), P5 6 (5/1). All within 4–6, ≥2 parameter.
- Counting only honest labels: P1 has 0 `method`, P2 has 0 `method`, P5 has 0 `method`; P3 and P4 each keep 1. See finding G-1.
- Every ladder has ≥3 pairwise-disjoint tiers, every tier stated in the rule with its condition and value/method, every tier implemented in compute; no two tiers of one ladder share a value or method; every fall-through equals the factor's `baseline` and the policy's `baseline.rule` (P1's `autoship_window` is nested inside `autoship_volume` and `baseline.rule` is silent on the window — O-9).
- `decides` is never `result`; binding sets are disjoint within each policy.
- Realism: every condition is something a pet retailer's care/fee policy plausibly weighs (delay length, basket/item value, loyalty tenure, membership tier, carrier fault, order age, error kind, refund wait, drop-off channel, repeat issues). P1's tenure-dependent look-back window is contrived (O-9) but I cannot demonstrate that no business would use it. No condition holds of every customer reaching its write.
- Per task (detailed in the task files): task 0 has multi-source (plus_member_multiplier, plus_rebooking_rate, carrier_fault) and cross-difficulty (member, autoship) factors; task 1 has multi-source (prompt_report_value, autoship_claims) and cross-difficulty (autoship) factors.

### findings

**G-1 — SOURCE-FACTOR RED (charter-global structure; demonstrated in 0.md for P1/P2 and 1.md for P5).**
- Symptom: P1, P2 and P5 each satisfy the "at least 1 `method`" floor only through factors whose tiers change a number, not the algorithm.
- Root cause: multipliers and a window length labelled `method`.
- Evidence: P1 `plus_member_multiplier` ladder — "the freight fee times the summed share is multiplied by premier_multiplier before rounding" / "… by plus_multiplier …" / "… taken as it stands" = ×2.0 / ×1.5 / ×1 in `result` (`freight_fee_charged * service_failure_share * member_multiplier`). P1 `autoship_window` — "Autoship shipments are counted over the last window_long_months / window_mid_months / window_standard_months months" = 24/18/12 substituted into `XCOUNT(..., within_months=autoship_window_months, ...)`. P2 `open_order_age` — "multiplied by age_factor_long / age_factor_mid … / taken as it stands" = ×0.6/×0.8/×1 in `(booking_fee + crew_surcharge) * member_rate * carrier_fault_rate * open_order_factor`. P5 `autoship_claims` — ×1.10/×1.05/×1 in `fulfillment_fee_charged * refund_share * claims_multiplier`. The skill's own test: "a factor labelled `method` whose tiers only substitute a different number into the same formula (a rate, a fee, a threshold)".
- Demonstrated consequence: counting only honestly-labelled factors, P1, P2 and P5 have 0 `method` factors (floor 1); in each case the formula is identical across tiers and only one numeric constant moves.
- Affected: order.extended.yaml `extended_policies[0].factors[3,5]`, `[1].factors[4]`, `[4].factors[5]`; task 0 (P1, P2), task 1 (P5).

**Observations (no demonstrated consequence on either task's world; recorded, not grounds for rework):**
- O-1: P1 scope "Large Item Freight Delivery order that is not yet completed" and P2 scope "whose included delivery attempts have failed" not encoded in compute; would diverge on a completed freight order or one with attempts below the included count.
- O-2: P3 `LATEST(..., status='received')` lacks the waived-reason filter the rule's "latest such authorization" carries.
- O-3: P3/P4 "unit list price on the line charge" computed as `MAX` over all line charges; diverges on multi-line orders.
- O-4: P1 and P5 both declare the same base clause ("Where late_delivery_fee_refund is true and the order is completed after promised_date, or for Same-Day Delivery …") superseded, with different `replaced_by`; domains are disjoint, so no world gets two answers, but a reader sees one base clause with two replacements.
- O-5: P2 edge sentence "owed for each paid appointment the carrier did not keep" vs condition "refund total … above zero"; P1 books one refund whose amount does not scale with the count, so with two or more missed appointments the sentence suggests more than one refund. Not reachable in task 0 (one missed appointment).
- O-6: P5's two edges are unconditional, but the resolving writes are conditional: a received non-error authorization has no writer in this difficulty, and a declined damage report whose customer chooses a replacement (or whose credit would exceed `returnless_refund_max_usd`) never carries a credit — P5 would then be blocked. Not reachable in task 1.
- O-7: P2's subject `order_fee_charge` is outside the difficulty's claimed event_types (blueprint.yaml l.125-126); P4 makes the damage credit an `owner=user` write while blueprint.yaml l.136-138 says "crediting damage, sending replacements and refunding fees are agent service actions".
- O-8: "rounded half up" vs runtime Python `round` on floats; no tie in either world.
- O-9: P1 `autoship_window` is a factor nested inside another factor's input; `baseline.rule` says nothing about the window. The ladder (look-back length set by subscription tenure) is contrived.
- O-10: P5's "a delay caused by the customer's absence or a changed address is never late" has only `delivery_attempts == 0` as its record proxy.

## closing_checklist

(Appended after reveal; see below.)

### closing_checklist — written 2026-10-06 after both reveals (post-reveal; the charter-global section above was frozen before any reveal and is unchanged, sha256 e20d9032…8549 at freeze)

The difficulty is **not closed**: both tasks carry SOURCE-FACTOR RED, so the four-relationship PASS required for closing is not met.

- Per-task files correspond one-to-one with tasks: `0.md` ↔ tasks/0.json, `1.md` ↔ tasks/1.json; `_difficulty.md` alongside. First revision; no older revisions exist.
- Coverage and scope: charter_scope task 0 = {P1, P2} + tools {8da9af3d, 0935dc22}; task 1 = {P3, P4, P5} + tools {9d87fcb3, 2d82d69e, 03b15c6d}. All 5 extended policies and 5 task tools covered, pairwise disjoint, matching the auditor's pre-reveal derivation. uuid8s independent (§ action_binding_and_uuids).
- Trees: task 0 one prerequisite, 1 value_input, user write P2; task 1 two prerequisites, 2 value_input, user write P4; whole-difficulty graph P2→P1, P5→P3, P5→P4 acyclic. PASS.
- Factors: every computation declares 5–6 factors with ≥2 parameter, self-sufficient baselines whose fall-back numbers (15.80, 49.00, 16.49, 16.49, 3.75) differ from gold, and every factor bears weight on its world. **Fails**: P1, P2, P5 have no honestly labelled `method` factor (G-1; T0-1, T1-1); task 1's claims-ladder near-miss row contradicts the autoship charter (T1-2); false world assertions in the factor proofs (T0-2, T1-3).
- Gates: not re-run by the auditor (the skill assigns the gate run to the orchestrator; the brief's snapshot is all green with check_traceability deferred).

Per-task verdicts:
- task 0: SOURCE-POLICY PASS · SOURCE-CHAIN PASS · SOURCE-TASK PASS · **SOURCE-FACTOR RED** (T0-1 = G-1 on P1/P2; T0-2 false "7 charges" count).
- task 1: SOURCE-POLICY PASS · SOURCE-CHAIN PASS · SOURCE-TASK PASS · **SOURCE-FACTOR RED** (T1-1 = G-1 on P5; T1-2 impossible autoship claim row 5e4f2462; T1-3 false "five factors" counterfactual).

## revision_2

### charter_global_frozen (revision_2)

- Freeze time: 2026-10-06 (written before either round-2 task file was opened; nothing here derives from a round-2 GT). Auditor: Claude (Opus 5.5), erl-task-policy-audit (same auditor as round 1).
- Inputs: order.extended.yaml **e5a6ac9c148281947101f1e10a57ee939c009d5aa710cb865535e3bf127cf829** (changed from 62e34365…) → every charter-global section re-derived below. task_tools.py 886a2ac1…7b7262 (unchanged) → § action_binding_and_uuids carried forward by reference on that hash (tool bodies, docstrings and uuid8s are byte-identical).
- Gate snapshot `/tmp/e40views/policy_task/order_returns_care/gate_snapshot_r2.txt`: the 7 gates exit 0 (replay now 25/25 rows for task 1); check_traceability deferred. Rebuilt views: task_0.r2 96e36e32…6d88, task_1.r2 d8984aac…fc4e (re-hashed, match).
- Base copy: `head -1344` still identical to blueprint/products/order.yaml.
- Masked/unread at freeze: round-2 `tasks/*.json`, worklog.md. Prior contact disclosed: the auditor read the round-1 task files after the round-1 freeze, so the round-1 GT values are known (see the task files' contamination_disclosure). The round-1 text above is left untouched.

### What changed in the charter (diffed against the round-1 text quoted in this report)

- P1: `overwrite` now `[]`; rule gains "An order of another method, a completed order and an order with no missed paid appointment receive no service-failure refund"; `result` now gates on `F('variant_name') == 'Large Item Freight Delivery' and F('status') != 'completed'`. Factor `rewards_tenure` removed; new `delay_clock_anchor` (method, member): Pals Rewards tenure picks the date the delay days count from (placed date / latest redelivery fee date / promised date). `autoship_window` and `plus_member_multiplier` relabelled `parameter`. Shares: value 0.08/0.04, Autoship 0.06/0.02; three shares now summed. Baseline rule adds "The days … run … from the date of the missed appointment, which is the order's promised date."
- P2: scope clause added to rule, overwrite `replaced_by` and `result` ("its failed attempts on record being at least carrier_attempts_before_return"; `F('delivery_attempts') >= P('carrier_attempts_before_return')`). The carrier-fault *rate* is replaced by `carrier_fault` (method) deciding `effective_booking_fee`: waive the booking fee (≥2 kept-not appointments) / credit the latest redelivery fee against it, floor 0 (exactly 1) / as it stands. `open_order_age` relabelled `parameter`. Prerequisite sentence now reads "… owed for the paid appointments the carrier did not keep"; gate `effective_booking_fee`.
- P3: settlement sentence rewritten: "The authorization settled is the latest one on the order in status received, by received date … This settlement applies when that authorization's reason is one of return_fee_waived_reasons". Compute unchanged.
- P4: unchanged.
- P5: claims multiplier removed; new `basket_valuation` (method, autoship): Autoship claim refund in 12 months AND shipments in 12 months pick the basket valuation (billed + all discounts / billed + half discounts / billed); `basket_mid_usd` 50 → 70. Edge A sentence now "… received back for a Tailwise error carries its refund entry"; edge B sentence adds "wherever the customer takes the money back rather than a replacement"; both conditions narrowed to match.

### policy_conflict_scan (revision_2)

- `order_fee_refund` overlap P1 / P5 / base cancellation / base delivery promises: domains still disjoint, now also enforced in P1's compute (freight, not completed) and P5's (late_delivery_fee_refund true, completed late, no attempts). Only P5 now declares the base late-delivery clause superseded (O-4 closed).
- P1 with `overwrite: []`: swept order_delivery_promises / order_cancellation / order_agg_fees sentence by sentence — no base sentence states anything about a service-failure refund on a not-completed freight order (return-to-sender fee sentence applies only when the carrier returns the order). No undeclared override.
- Scope: the two trees {P1,P2} and {P3,P4,P5} remain disjoint and jointly complete. O-7 unchanged (documented).

### rule_compute_equivalence (revision_2)

- P1: new anchor ladder implemented exactly (`delay_anchor_date`), quoted in compute_basis; scope sentence now implemented (O-1 closed for P1).
- P2: scope implemented (O-1 closed for P2); `effective_booking_fee` = 0 / MX(0, booking_fee − latest redelivery fee) / booking_fee matches the rule's three tiers; "the redelivery fee charged for that appointment (the latest redelivery fee on the order)" ↔ `LATEST(... fee_kind='redelivery')`.
- P3: rule now says the settled authorization is the latest received regardless of reason, then gated on the waived reason — identical to compute (O-2 closed).
- P3/P4 `MAX(unit_price_usd)` vs "the unit list price on the line charge": unchanged (O-3 stays open as documented).
- P5: `basket_value_measured` implements the three valuation tiers; `result` no longer multiplies; rule/overwrite text no longer mention the multiplier. O-10 unchanged (documented).
- Rounding (O-8): unchanged; no tie in either round-2 world (checked in task files).

### action_binding_and_uuids (revision_2)

Carried forward from round 1 by reference on task_tools.py sha256 886a2ac1…7b7262 (unchanged). Each `(target_tool, computes)` still claimed by exactly one policy (targets unchanged in the yaml).

### prerequisite_graph (revision_2)

- Edges unchanged in shape: P2 → P1 (value_input, gate `effective_booking_fee`, exists in P2 compute), P5 → P3 and P5 → P4 (value_input, gate `error_units_settled`). Acyclic; `policy_source` verbatim in own rule (3/3, script check); not restated in the depended-on rules; `resolved_by` = target_tool (3/3); all `form: state`, no fallback.
- Conditions: P2 edge "refund total … above zero" now matches the sentence's "the service-failure refund owed for the paid appointments" (O-5 closed). P5 edges: "No return authorization … with a reason in return_fee_waived_reasons is left in status received" and "Each declined damage report … whose customer takes the money back has a damage credit entry" — match their sentences.

### prerequisite_sentences (revision_2)

1. P2 ← P1: "The fee for a rebooked freight redelivery is fixed only after the order's freight fee carries the service-failure refund owed for the paid appointments the carrier did not keep." Four-point test passes; single writer P1 (unchanged reasoning).
2. P5 ← P3: "… not worked out until every return authorization on the order that has been received back for a Tailwise error carries its refund entry." Single writer `refund_error_return_9d87fcb3`. Residual (observation O-6r): P3 settles only "the latest one on the order in status received"; if a later-received non-error authorization sits on the same order, the earlier Tailwise-error one cannot be settled by P3 until the non-error one leaves status received, and no tool in this difficulty refunds it — P5 would stay blocked. Not reachable in task 1 (one received authorization).
3. P5 ← P4: "… must carry its returnless damage credit wherever the customer takes the money back rather than a replacement." Now conditional on the customer's choice (replacement case closed). Residual (O-6r): a money-back choice whose credit sum is above `returnless_refund_max_usd` gives no credit (P4: "no returnless damage credit is given and the item comes back under a return authorization instead"), so the state can never hold. Not reachable in task 1 (23.99 ≤ 25.00).

### override_declarations (revision_2)

- P1 `overwrite: []` — acceptable (see conflict scan). P2 declaration updated, clause verbatim in base, `replaced_by` verbatim in rule. P3, P5 declarations verbatim in base and rule (script check). P4 unchanged (`[]`, base fixes no credit amount). No undeclared override found.

### factor_ladders (revision_2)

| Policy | Factors (label) | Honest method | Cross-diff | Multi-source |
|---|---|---|---|---|
| P1 | undelivered_days (p), delay_clock_anchor (m), item_value (p), autoship_window (p), autoship_volume (p), plus_member_multiplier (p) | delay_clock_anchor — yes: tiers choose which record's date the day count runs from (placed_on / latest redelivery fee event_date / promised_date), a different computation, not a number | member ×2, autoship ×2 | plus_member_multiplier |
| P2 | repeat_booking (p), crew_handling (p), plus_rebooking_rate (p), carrier_fault (m), open_order_age (p) | carrier_fault — yes: waive / subtract the latest redelivery fee floored at 0 / take as is | member | plus_rebooking_rate, carrier_fault |
| P3 | unchanged (1 m, 5 p) | autoship_price_basis — yes | autoship ×2 | — |
| P4 | unchanged (1 m, 4 p) | prompt_report_value — yes | autoship ×2 | prompt_report_value |
| P5 | lateness (p), error_settled (p), repeat_issue_count (p), autoship_patron (p), basket_value (p), basket_valuation (m) | basket_valuation — yes: billed + all discounts / billed + half discounts / billed | autoship ×2 | basket_valuation (claim refunds AND shipments) |

- Every policy 5–6 factors, ≥2 parameter, ≥1 honest method → G-1 closed at charter level. Labels previously dishonest are now `parameter` (autoship_window, plus_member_multiplier, open_order_age) — honest.
- Every ladder ≥3 disjoint tiers, stated in the rule, implemented in compute; no two tiers share a value/method; bindings disjoint within each policy (script check); every fall-through equals its `baseline`. P1 `baseline.rule` now states the default anchor (promised date).
- Realism (observations, not demonstrated):
  - O-11 (new): P5 `basket_valuation` — whether the customer had an Autoship claim refund in the last 12 months decides how the order's basket is valued for the late-fee refund share. The same condition fed a goodwill multiplier in round 1, which is plausible as service recovery; tying it to the method of *valuing a basket* is contrived. I cannot show that no retailer would publish it, so it is not a RED.
  - O-12 (new): P1 `delay_clock_anchor` — loyalty tenure moving the start of the delay count is contrived but defensible as tiered goodwill.
  - O-9 (P1 nested window factor): the nesting persists, and `baseline.rule` is still silent on the window. The window label is now honest.

### findings (revision_2, charter-global)

- G-1: **closed** at charter level (each of P1, P2, P5 now has one honest `method` factor; relabels honest). Per-task weight demonstrated in the task files.
- O-1 closed; O-2 closed; O-4 closed; O-5 closed; O-6 partially closed (residual O-6r above, observation); O-3, O-7, O-8, O-10 unchanged as documented; O-9 persists (observation); new observations O-11, O-12. No new SOURCE-POLICY finding.

### closing_checklist (revision_2) — written after both round-2 reveals; the revision_2 charter-global section above was frozen before them (sha256 63b360f9…8477)

- Per-task files ↔ tasks one-to-one (`0.md`, `1.md`); round-1 text untouched, revision_2 appended in each file. Every revision_2 comparison carries PASS on all four relationships.
- Coverage/scope: charter_scope {P1, P2} + {8da9af3d, 0935dc22} and {P3, P4, P5} + {9d87fcb3, 2d82d69e, 03b15c6d}; all 5 policies and 5 tools covered, pairwise disjoint; uuid8s unchanged and independent.
- Trees: task 0 n=1 (1 value_input, user write P2); task 1 n=2 (2 value_input, user write P4); difficulty graph acyclic.
- Factors: every computation 5–6 factors, ≥2 parameter, ≥1 honest method; per task ≥1 multi-source and ≥1 cross-difficulty with seeded rows; every factor bears weight against an honest baseline; all-baseline numbers 15.80 / 49.00 / 16.49 / 16.49 / 3.75 differ from gold 47.40 / 15.60 / 27.74 / 23.99 / 12.59.
- Gates: the orchestrator's r2 snapshot shows all 7 green; check_traceability is still deferred until the KB is published. The auditor did not re-run them.
- Round-1 item closure:
  - Closed: G-1 / T0-1 / T1-1, T0-2, T1-2, T1-3, O-1, O-2, O-4, O-5, {RB}.
  - Partly closed: O-6 (residual O-6r, observation) and Autoship seed realism (implied seq-1 pricing, observation).
  - Unchanged as documented: O-3, O-7, O-8, O-10.
  - Still present: O-9.
  - New observations: O-11, O-12, O-6r.
  - No new RED; no regression.
- **Difficulty order_returns_care passes the source-layer audit at revision_2.** Every remaining item is an observation, not grounds for rework.
