# Policy-task audit — cleaning_and_damage_fee_assessments / charter-global

## charter_global_frozen

- Auditor: erl-task-policy-audit (independent auditor; did not author these artifacts). Freeze time: 2026-10-11T11:51Z (written before any task's GT was revealed).
- Frozen inputs (sha256 re-checked against `.audit_views/policy_task/cleaning_and_damage_fee_assessments/HASHES.txt`, all match):
  - `tasks/cleaning_and_damage_fee_assessments/damage.extended.yaml` 0a0ad092c9da19de0932715048437f5d3dbf9604a53fbffdbcb899ad0f1faf57
  - `tasks/cleaning_and_damage_fee_assessments/task_tools.py` 17ea950d5a95b942d87aea9b2eb8f6a7cadf113b8a877753992da8234fa20f93
  - views 0.view.json ddc2bd1d…af22, 1.view.json 86b31050…e725
- Read: `blueprint/` (blueprint.yaml, db_schema.json, share_tools.py, products/damage.yaml; trip.yaml and pass.yaml only for seat/market/discount consistency of seeded cross-difficulty rows), the extended charter, task_tools.py, the two masked views. Masked and unread at this freeze: every task's `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`. No recursive grep over `tasks/` or the scenario was run.
- Entry conditions (Step 0): gate snapshot supplied with the brief — check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all rc=0; check_traceability deferred to render stage (needs the published KB). Masked views and hashes supplied. Entry conditions complete.
- Base copy: a structural compare of every top-level key of `blueprint/products/damage.yaml` (category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies) against the extended charter returns equal for all ten keys; the base copy is verbatim.

### policy_conflict_scan

Eight extended policies over one category:

| id | target_tool | owner | computes | prerequisite |
| --- | --- | --- | --- | --- |
| damage_ext_review_move_down_fee | move_down_report_level_d77023ae | agent | assessed_fee | [] |
| damage_ext_approval_photo_shortfall | upload_report_photos_a5022c03 | user | photos_in_upload | move_down (value_input) |
| damage_ext_partner_work_order_price | price_partner_work_order_4e0ef0e3 | agent | cleaning_cost_on_file | move_down (value_input) |
| damage_ext_cleaning_fee_on_approval | approve_cleaning_fee_charge_639a45e8 | agent | fee_charged | move_down (vi), price (vi), photo (state_gate) |
| damage_ext_repair_schedule_estimate | file_schedule_repair_estimate_16065485 | user | schedule_estimate_amount | [] |
| damage_ext_damage_fee_on_approval | approve_damage_fee_charge_55ca59de | agent | fee_charged | schedule (vi), level_correction_refund (state_gate, action form) |
| damage_ext_upheld_level_correction_fee | correct_upheld_fee_level_42a82f5f | agent | fee_standing | [] |
| damage_ext_level_correction_refund | refund_level_difference_30807e99 | agent | refund_amount | upheld_correction (vi) |

- Overlapping subjects. `damage_reclassify` is claimed by move_down (report `under_review`) and upheld_correction (fee already charged: "whether the charge stands undisputed, disputed or upheld"); the status scopes are disjoint, so a given assessment falls under exactly one. `damage_approve_charge` is claimed by the cleaning approval ("A cleaning fee report under review ... at the cleaning level it holds") and the damage approval ("A receipt-based damage report under review ... at the damage level it holds"); disjoint by fee_basis of the level. `damage_evidence_submit/update` is claimed by photo shortfall (photo_set), price (cost on file, no ledger row) and schedule estimate (repair_estimate); different evidence objects.
- Triggers / time anchors. All `state_due`; no extended policy introduces a time window of its own beyond the date reads in its factors. The base filing window, evidence deadline, dispute and reconsideration windows are inherited untouched.
- Eligibility inherited from base: completed trip, filing window, `evidence_open_status` (reported/under_review/denied) for the two evidence writes, `below_report_threshold` and `not_shared_trip` for both approvals, `reclassified_after_charge` (disputed/upheld) for the partial refund. No extended rule weakens any of them (the correction rule widens move-downs to undisputed charges, but its refund partner keeps "while it is disputed or after it was upheld").
- Terminal states. Approvals -> `charged`; moves/corrections keep status; refund keeps status, lowers `net_fee_billed`. No conflict.
- Cross-category reads. trip (variant_name, seats_requested, market, actual_minutes, dropoff_at, trip_charges fare rows) and pass (active membership variant_name, enrolled_date). All read-only.
- Scope exclusivity / completeness (derived from the prerequisite graph alone, pre-reveal): the graph has exactly two connected components — {move_down, photo_shortfall, partner_price, cleaning_approval} and {schedule_estimate, damage_approval, upheld_correction, level_correction_refund}. With M=2 these are the only two disjoint trees that cover all eight policies, so the scopes are pairwise disjoint and jointly complete provided task 0 claims the first and task 1 the second (the views' worlds fit exactly that split). To be confirmed against `charter_scope` at reveal.
- Conflict found: see finding F1 (base `damage_level_classification` vs the two extended move-down rules).

### rule_compute_equivalence

Per policy, every compute binding has a `compute_basis` quotation that is a verbatim substring of the rule; swept back sentence by sentence:

- move_down. `new_rank` implements "highest lower cleaning level whose entry gate lists that category" against the variants' entry gates (L1 food/trash/animal; L2 food/trash/smoke/animal; L3 food/smoke/animal/bodily; L4 bodily). `odor_component` tests `new_rank >= 2` instead of `P('odor_treatment_included')`; equivalent on the charter's values (L1 false, L2–L4 true) — observation O4. `odor_documents` counts `cleaning_receipt` rows; the reader maps "professional cleaning document" to that evidence type through the partner-price rule ("reaches the assessment's evidence ledger as a professional cleaning document"). All five ladders appear in the rule with condition and value. Result order (cabin multiply, then add four components, round once) matches.
- photo_shortfall. `row_photos`, `liquid_photos`, `trim_photos`, `vehicle_rows`, `photo_set` and `MX(0, set - on_file)` each match their rule sentence; the each-affected-surface tier omits the level minimum and the seat-row photos exactly as the rule says.
- partner_price. `service_basis`, `extraction_charge`, `metro_rate`, `rush_charge`, `conditioning_charge`, `weekend_charge` match; `weekday_index` anchors on 2026-01-03 (a Saturday; index 0 = Saturday, 1 = Sunday), equivalent to "the day of the week the work order was put on the evidence ledger". Result order matches.
- cleaning_approval. `fee_basis`, `lost_time` ("both days counted" = DAYS+1), `fee_cap`, `pass_goodwill`, `tenure_pct`, result order match.
- schedule_estimate. parts × tier multiplier × (1 + tax), hours × metro labor rate, paint method (blend = 0.8 h × 2 panels × labor rate), calibration; matches.
- damage_approval. settlement share, lost time, damage cap, Pass goodwill, trip-volume pct, result order match. Observation O5: the lost-time rule says "with a repair estimate or receipt on file" while `lost_estimates/lost_receipts` count ledger rows; a receipt submitted with the report itself (base `damage_report` field "repair_receipt_amount: Receipt total submitted with the report") is "on file" without a ledger row. No task world reaches that case.
- upheld_correction. `carried_fee`, `lost_removal` (uses `held_rank >= 3 and new_rank <= 2` for vehicle_offline_expected; equivalent on the charter's values — O4), `correction_pct`, `age_pct`, result order match.
- level_correction_refund. `from_level`, `refund_base` three tiers, goodwill ladders, `recontact_goodwill` ("dispute not yet closed, or no dispute" = empty closed_date) match.
- No compute binding invents a basis; no rule sentence is left unimplemented other than the scoped conditional "when the shop estimate on file is more than the schedule tolerance above the schedule estimate, the driver files ..." (an act-or-not condition, not a quantity), which the damage approval's prerequisite sentence carries.

Result: PASS (observations O4, O5).

### action_binding_and_uuids

- `(target_tool, computes)` pairs are unique across the eight policies.
- uuid8 tails: d77023ae, a5022c03, 4e0ef0e3, 639a45e8, 16065485, 55ca59de, 42a82f5f, 30807e99 — all distinct, no shared prefix, no sequence pattern, no tail reused with a different verb.
- Docstrings name no other tool and state no position in a sequence. Several use "Afterwards the assessment (lookup) shows ..." to describe the tool's own post-state (move_down, price, correct_upheld) — observation O1, not an ordering relative to another action.
- Function bodies: no tool checks a condition, a prerequisite or an eligibility; each does `ctx.find` + `ctx.update/create` only.
- Result: PASS.

### prerequisite_graph

- Every extended policy has `prerequisite` (four are `[]`). Every `problem` names another extended policy id; no base id, no self loop. Graph: photo→move_down, price→move_down, cleaning_approval→{move_down, price, photo}, damage_approval→{schedule, refund}, refund→upheld_correction. Acyclic.
- `policy_source` of every edge is a verbatim sentence of the blocked policy's own `rule` (checked by substring for all seven edges).
- `form`: six `state`; one `action` (damage_approval → level_correction_refund) with `fallback_reason` present; no state edge carries a fallback.
- `resolved_by` equals the depended-on policy's `target_tool` on every edge.
- `kind`/`gate`: value_input gates `set_minimum`, `level_package`, `level_flat`, `cost_on_file`, `amount_on_file`, `to_flat` all exist as compute bindings of the blocked policy; state_gates `damage_assessments.photo_count` and `damage_assessments.net_fee_billed` name record fields.
- Condition vs sentence: six edges' `condition` restate their sentence's state. The action-form edge does not — finding F2 (condition weaker than the sentence).
- No authoring-viewpoint phrasing ("in this task", "at the opening") inside any `prerequisite`.

### prerequisite_sentences

Four-point test per edge (ordering connective / state or action in record words / no tool, id, snake_case token / scope matches condition):

1. photo_shortfall ← move_down: "The photos still needed for approval are counted only after the fee level held on the assessment is one whose entry gate lists the incident category reported." — "only after"; state on `variant_name` vs `incident_category`; clean; matches condition. Writes that can bring the state about: move_down (report under review) and correct_upheld (fee already charged). The blocked policy's scope is "a cleaning or damage fee report under review", and the correction rule's scope is "A charged cleaning fee", so for any record reaching this policy only move_down applies — single reading (observation O9). Derivation: report under review held at a level whose gate omits its category -> the only rule that changes the level of a report under review is the move-down rule -> move it down first.
2. partner_price ← move_down: "A partner work order on file is not priced until the fee level held on the assessment lists the incident category reported in its entry gate." — "not ... until"; same state; same derivation. PASS.
3. cleaning_approval ← move_down: "The fee charged on approval is fixed only after the fee level held on the assessment is one whose entry gate lists the incident category reported." PASS (as 1).
4. cleaning_approval ← partner_price: "The fee charged on approval is not fixed until every partner work order on the assessment's evidence ledger carries its price in the cleaning cost on file." — state: cleaning cost on file (`repair_receipt_amount`) carries the price of the `cleaning_receipt` row(s); the only write of a cleaning report's cost on file is the partner-price rule's. PASS.
5. cleaning_approval ← photo_shortfall: "A cleaning fee is charged on approval only once the photos on file for the report reach the approval photo set for the level held." — state on `photo_count`; the only rule that adds photos is the photo-shortfall rule (driver's upload). PASS.
6. damage_approval ← schedule_estimate: "A damage fee charged on approval is fixed only after the repair amount on file is no more than the Wayfare repair schedule estimate for the repair increased by the schedule tolerance." — state on `repair_receipt_amount`; the schedule-estimate rule is the only one that replaces the repair amount of a damage report. PASS.
7. damage_approval ← level_correction_refund (action form): "A damage fee is not charged to a rider until any level-difference refund owed to that rider on an earlier fee assessment has been booked." — ordering "not ... until"; action in business words; no tool/id. Fallback test: the refund write leaves a record-visible state that only it produces — a `damage_fee_partial_refund` row (refund_reason level_reclassified) on the earlier assessment booked at the level that assessment is now held at; the author's own `condition` is phrased in exactly that state. The fallback is therefore unjustified (observation O6). Reading test: "owed" is not a record state. A refund becomes owed only when a charged fee "is moved down to a lower level while it is disputed or after it was upheld" (refund rule); a move that is due under the correction rule but not yet made leaves no refund owed on the record. Whether a due-but-unmade correction makes a refund "owed" is open — finding F3 (demonstration in 1.md).
- No rule restates another policy's prerequisite sentence; no rule names another policy's tool; no cross-problem order is stated that grounds no declared edge. Base sentences that state a cross-problem order (base `damage_evt_refunds` "A partial refund is made only when a charged assessment is moved to a lower level while it is disputed or after it was upheld") are backed by an extended prerequisite sentence of their own on the refund policy (edge refund ← upheld_correction), so no tree rests on a base sentence.

### override_declarations

Sentence-by-sentence over every `base_policy_refs` entry:

- move_down (refs: damage_level_classification, damage_evt_refunds, damage_evt_fee_charge; overwrite: fee_charge "At a flat level the fee is the level's flat_fee").
  - damage_level_classification: "Each level covers the incidents its level_definition ... and only the incident categories listed in its entry gate." followed. "A report is held at the lowest level whose definition matches the evidence on file; when the evidence matches a lower level than the one reported, the reviewer moves it down (reclassification_direction) and never up." — HANDLED DIFFERENTLY: extended moves to "the highest lower cleaning level whose entry gate lists that category", a different selector, and no `overwrite` names this base sentence -> F1. "The non_chargeable_conditions ... denied" followed.
  - damage_evt_refunds: not engaged (no refund at review). damage_evt_fee_charge: flat-fee clause declared overwritten; every other sentence (charge on approval once, payer, not split, Shared, unpaid handling) followed.
- photo_shortfall (ref damage_filing_and_evidence; overwrite []): the review-entry sentence ("enters review only when it has at least min_photos photos") governs entry to review; the extended "approval photo set" governs approval and does not change review entry; "photos must show photo_subjects_required" is used, not contradicted; max_evidence_submissions inherited. No undeclared override. (Observation O7: base `dispute_evidence_standard` judges a later dispute by "the level's photo and receipt requirements at approval"; with an approval photo set above min_photos the dispute standard has two candidate photo requirements. Not engaged by either task.)
- partner_price (ref damage_filing_and_evidence; overwrite []): records the cost on file; the base `repair_receipt_amount` meaning "Receipt total submitted" is extended to a priced partner work order; no base sentence fixes a different amount for a partner work order. No conflict.
- cleaning_approval (refs: damage_agg_driver_report_volume, damage_evt_fee_charge; overwrite flat-fee clause): driver-volume threshold followed; fee_charge's flat clause declared; the rest followed.
- schedule_estimate (ref damage_filing_and_evidence; overwrite []): adds a repair_estimate submission; inherits max_evidence_submissions and evidence_open_status. No conflict.
- damage_approval (refs: damage_agg_driver_report_volume, damage_evt_fee_charge; overwrite "at a receipt-based level it is the receipt or estimate amount on file (estimate_settles_fee), capped at receipt_fee_cap"): the following base clause "the part of a repair above the cap is never charged to the rider and the driver is referred to the insurance claim desk (excess_damage_route) through a POLICY_NOT_COVERED handoff" is not named; after the overwrite its referent "the cap" is either the vehicle damage cap or the base receipt_fee_cap — observation O10 (no consequence where the repair amount on file is below both).
- upheld_correction (refs: damage_level_classification, damage_evt_refunds, damage_evt_fee_charge, damage_dispute_rules; overwrite flat-fee clause): same undeclared selector change as move_down against damage_level_classification -> F1. damage_dispute_rules "When the evidence supports only a lower level, the assessment is moved down, the difference is refunded, and the fee is upheld at the lower level." — the fee upheld at the lower level is the flat-fee clause, declared.
- level_correction_refund (ref damage_evt_refunds; overwrite partial_refund_basis clause): declared. "Refunds return to the original payment method ... name the fee charge" followed; "When a refund is made for any reason other than a first-incident courtesy, the reporting driver's payout on the amount returned is taken back" inherited (the task tool does not write the earnings side — O3).

### factor_ladders

| policy | factor | effect | tiers | multi-source tiers | cross_difficulty | structural verdict |
| --- | --- | --- | --- | --- | --- | --- |
| move_down | cabin_size | parameter | 3 | ride option + seats (same trip row) | trip | ok |
| move_down | metro_cost | parameter | 3 | single (market) | trip | ok |
| move_down | liquid_exposure | parameter | 3 | incident (assessment) + actual_minutes (trip) | trip | ok |
| move_down | upholstery | parameter | 3 | single | trip | ok |
| move_down | odor_treatment | method | 3 | level moved to + cleaning docs | — | UNREAL — F4 |
| photo | seat_row_photos | parameter | 3 | ride option + seats | trip | ok |
| photo | liquid_close_ups | parameter | 3 | incident + trip minutes | trip | ok |
| photo | trim_close_ups | parameter | 3 | single | trip | ok |
| photo | set_assembly | method | 3 | level's photo subjects | trip | ok |
| price | service_basis | method | 3 | ride option + seats | trip | ok |
| price | extraction | parameter | 3 | incident + trip minutes | trip | ok |
| price | metro_rate | parameter | 3 | single | trip | ok |
| price | rush_turnaround | parameter | 3 | trip drop-off + ledger date | trip | ok |
| price | leather_conditioning | parameter | 3 | single | trip | ok |
| price | weekend_service | parameter | 3 | ledger date | — | ok |
| cleaning_approval | fee_basis | method | 3 | level param + ledger + cost | — | ok |
| cleaning_approval | lost_driving_time | method | 3 | level param + ledger (+trip date) | trip | ok |
| cleaning_approval | vehicle_fee_cap | parameter | 3 | single | trip | ok |
| cleaning_approval | pass_goodwill | parameter | 3 | single | pass | ok |
| cleaning_approval | member_tenure_goodwill | parameter | 3 | pass enrolled + approval date | pass | ok |
| schedule | parts_tier | parameter | 3 | single | trip | ok |
| schedule | metro_labor_rate | parameter | 3 | single | trip | ok |
| schedule | paint_method | method | 3 | level + ride option | trip | ok |
| schedule | parts_tax | parameter | 3 | single | trip | ok |
| schedule | sensor_calibration | parameter | 3 | level + ride option | trip | ok |
| damage_approval | estimate_settlement | parameter | 3 | receipts + estimates | — | ok (O8) |
| damage_approval | damage_lost_time | method | 3 | level + ride option + documents | trip | UNREAL — F5 |
| damage_approval | vehicle_damage_cap | parameter | 3 | single | trip | ok |
| damage_approval | damage_pass_goodwill | parameter | 3 | single | pass | ok |
| damage_approval | damage_trip_volume | parameter | 3 | trip charges window | trip | ok |
| upheld_correction | carried_fee | method | 3 | charge + refunds + two flats | — | ok |
| upheld_correction | lost_time_removal | method | 3 | two levels + ledger + trip date | trip | ok |
| upheld_correction | correction_credit | parameter | 3 | partial refunds / dispute date | — | ok |
| upheld_correction | overcharge_age_credit | parameter | 3 | charge date | — | ok |
| refund | refund_base | method | 3 | refunds + charge + flat | — | ok |
| refund | refund_pass_goodwill | parameter | 3 | single | pass | ok |
| refund | refund_trip_volume | parameter | 3 | trip charges window | trip | ok |
| refund | recontact_goodwill | parameter | 3 | closed date | — | ok |

- Counts as declared: move_down 5 (4p/1m), photo 4 (3p/1m), price 6 (5p/1m), cleaning_approval 5 (3p/2m), schedule 5 (4p/1m), damage_approval 5 (4p/1m), upheld_correction 4 (2p/2m), refund 4 (3p/1m). All within 4–6.
- Every ladder is stated in the rule (condition and value/method) and implemented in the `decides` binding; no tier lives only in compute; bindings disjoint within each policy; no `decides: result`. Within each ladder the tiers select distinct values/methods. Labels honest: each `method` factor changes the formula's shape (proportion vs fixed add vs none; per-row vs package+row vs package; max-of vs replace vs flat; scaled vs difference vs flat; blended labor vs none vs flat spot); each `parameter` factor substitutes a number.
- Baselines: every factor's fall-through equals its `baseline` binding and the policy `baseline.rule` is a sentence-for-sentence prefix of the rule, self-sufficient (flat fee of the level / package of the level / min_photos / standard parts+tax+labor+spot paint / repair amount capped at receipt_fee_cap / flat fee of level moved to / flat-fee difference).
- Unreal ladders: F4 (move_down odor_treatment) and F5 (damage_approval damage_lost_time) — each has a condition part that holds of every record reaching the write and a fall-through no such record can take. Striking them leaves move_down with 0 `method` factors and damage_approval with 0 `method` factors.
- Cross-difficulty reads: trip (every policy except the refund's trip read is via trip_charges history) and pass (cleaning_approval, damage_approval, refund). Seeded rows checked per task in its `factor_weight`.

### findings

**F1 — SOURCE-POLICY RED (undeclared override of the classification selector).** Bears on tasks 0 and 1.
- Symptom: two clauses pick the level a mis-levelled cleaning report is moved to by different selectors.
- Root cause: base `damage_level_classification` rule: "A report is held at the lowest level whose definition matches the evidence on file; when the evidence matches a lower level than the one reported, the reviewer moves it down (reclassification_direction) and never up." Extended `damage_ext_review_move_down_fee` rule: "A cleaning fee report under review that is held at a cleaning level whose entry gate does not list the incident category reported is moved down to the highest lower cleaning level whose entry gate lists that category". Extended `damage_ext_upheld_level_correction_fee` rule: "... is moved down to the highest lower cleaning level whose entry gate lists that category". Both list `damage_level_classification` in `base_policy_refs`; neither `overwrite` names this base sentence (both name only damage_evt_fee_charge "At a flat level the fee is the level's flat_fee").
- Demonstrated consequence (charter level): a report of a coffee spill on one seat (L1's own `level_examples`: "coffee spill on one seat"), incident `food_or_drink_spill`, reported at Level 4: base selects Cleaning Fee Level 1 (lowest level whose definition matches; L1's gate lists food_or_drink_spill); extended selects Cleaning Fee Level 3 (highest lower level whose gate lists it). Fees then differ (base L1 $25 flat vs extended L3-based figures).
- Affected: damage.extended.yaml, `extended_policies[damage_ext_review_move_down_fee].overwrite` and `[damage_ext_upheld_level_correction_fee].overwrite`. Per-task demonstration in 0.md and 1.md.

**F2 — SOURCE-POLICY RED (prerequisite condition weaker than its sentence).** Bears on task 1.
- Symptom: edge damage_ext_damage_fee_on_approval → damage_ext_level_correction_refund. Sentence: "A damage fee is not charged to a rider until any level-difference refund owed to that rider on an earlier fee assessment has been booked." Condition: "No earlier charged assessment of the rider (damage_assessments with the same customer_id) is held at a level whose entry gate leaves out its incident_category without a damage_fee_partial_refund booked for the move to the level it is now held at."
- Root cause: the condition's first conjunct ("held at a level whose entry gate leaves out its incident_category") is made false by the level correction itself, so once the earlier assessment has been moved to a gate-listing level the condition holds whether or not the refund the refund rule then owes ("When a charged fee is moved down to a lower level while it is disputed or after it was upheld, the rider is refunded the level difference") has been booked; and before the correction the conjunct "without a damage_fee_partial_refund booked for the move to the level it is now held at" is satisfied by any earlier level-difference refund at the current level.
- Demonstrated consequence: same situation, two conclusions — an upheld earlier assessment just moved down to a gate-listing level with no refund booked: sentence -> approval blocked (a refund is owed and unbooked); condition -> satisfied (approval free). Task 1's world demonstrates it on real rows (1.md).
- Affected: `extended_policies[damage_ext_damage_fee_on_approval].prerequisite[1].condition`.

**F3 — SOURCE-POLICY RED (action-form sentence admits two readings at the opening).** Bears on task 1.
- Symptom: "any level-difference refund owed to that rider on an earlier fee assessment" — "owed" is not a record state; under the refund rule a refund is owed only after a move-down is made. Where an earlier assessment is due a correction under `damage_ext_upheld_level_correction_fee` but the correction has not been made, reading A: no refund is owed yet, the gate holds, approve; reading B: the due correction makes the refund owed, correct + refund first.
- Demonstration on task 1's world in 1.md (two terminal states).
- Affected: `extended_policies[damage_ext_damage_fee_on_approval].rule` last sentence / `prerequisite[1].policy_source`.

**F4 — SOURCE-FACTOR RED (unreal ladder: move_down `odor_treatment`).** Bears on task 0.
- Symptom: tiers "the level moved to includes odor treatment and at least one professional cleaning document ..." / "... includes odor treatment and no professional cleaning document ..." / "otherwise (the level moved to does not include odor treatment)".
- Root cause / demonstration by enumeration of the charter's entry gates: a move-down happens only when the held level's gate omits the category and a lower level lists it — L4 with food_or_drink_spill/smoke_or_vape_odor/animal_hair_or_mess -> L3; L4 or L3 with trash_or_debris -> L2; no other combination has a lower gate-listing level (L1 lists nothing that L2 omits; bodily_fluids is on no level below L3; interior/exterior damage on no cleaning level). So the level moved to is always L2 or L3, both `odor_treatment_included: true`. The condition part "the level moved to includes odor treatment" holds of every report that reaches this write, and the fall-through tier is unreachable; the ladder divides customers only by "professional cleaning document on file", i.e. two real tiers.
- Consequence: striking it leaves move_down with 4 factors, 4 parameter, 0 method (< 1 method required).
- Affected: `extended_policies[damage_ext_review_move_down_fee].factors[odor_treatment]` and the rule's odor sentence.

**F5 — SOURCE-FACTOR RED (unreal ladder: damage_approval `damage_lost_time`).** Bears on task 1.
- Symptom: tiers "an exterior repair on Wayfare Black or Wayfare Black SUV with a repair estimate or receipt on file" / "any other repair with a repair estimate or receipt on file" / "a repair with no repair estimate or receipt on file".
- Root cause: the policy's scope is "A receipt-based damage report under review"; base `damage_filing_and_evidence`: "The report enters review only when it has at least min_photos photos and, for levels with receipt_required true, a document of a type in receipt_types_accepted"; both damage levels have `receipt_required: true`, `receipt_types_accepted: [repair_receipt, repair_estimate]`. The condition part "with a repair estimate or receipt on file" therefore holds of every report reaching this write and the fall-through is unreachable under the rule's own words (the compute's ledger-row count can only reach it through the O5 mismatch).
- Consequence: striking it leaves damage_approval with 4 factors, 4 parameter, 0 method.
- Affected: `extended_policies[damage_ext_damage_fee_on_approval].factors[damage_lost_time]` and the rule's lost-time sentence.

Observations (no demonstrated consequence; not grounds for rework):
- O1 Docstrings of move_down / price / correct_upheld say "Afterwards the assessment ... shows", describing the tool's own post-state, not an order relative to another action.
- O2 `db_schema.damage_assessments.assessed_fee` meaning "0.00 until approved" vs move_down writing `assessed_fee` on an unapproved report (base event `damage_reclassify` already writes "assessed_fee: Fee at the new level", so the schema meaning predates this difficulty).
- O3 The approve and refund task tools do not book the base event triggers `earnings:earnings_cleaning_credit` / `earnings:earnings_adjustment_debit`; driver-payout side effects are not written. Outside the four relationships of this difficulty.
- O4 Rank proxies for `odor_treatment_included` (move_down) and `vehicle_offline_expected` (correction) — equivalent on the charter's values.
- O5 damage_approval lost time: rule "on file" vs compute ledger-row counts (see rule_compute_equivalence).
- O6 Action-form fallback unjustified: the refund write leaves a `damage_fee_partial_refund` row at the level the earlier assessment is now held at, a record-visible state only that write produces (the edge's own `condition` is phrased in it).
- O7 Approval photo set vs base dispute evidence standard "the level's photo and receipt requirements at approval" — two candidate photo requirements for a later dispute; not engaged.
- O8 estimate_settlement: the "corroborated-estimate share" is taken whenever two estimate submissions are on the ledger, including when the second is the schedule estimate that replaced the first for exceeding tolerance — realism note; per-task figure in 1.md.
- O9 Two writes (move_down, correct_upheld) can make "the level held lists the incident category" true, but the blocked policies' status scopes select one; single reading.
- O10 After the damage-cap overwrite, the referent of base "the part of a repair above the cap ... POLICY_NOT_COVERED handoff" is unstated (vehicle damage cap vs receipt_fee_cap).

## closing_checklist

Written 2026-10-11 after both tasks' frozen derivations and GT comparisons were on disk. The difficulty is **not closed**: not every task passes all four relationships.

- Per-task files: 0.md, 1.md correspond one-to-one with tasks/0.json, tasks/1.json; `_difficulty.md` alongside. First audit; no earlier revision.
- Per-task verdicts:
  - task 0: policy self-consistency PASS (F1 cited, no consequence on its world); problem tree PASS; factors SOURCE-FACTOR RED (F4 -> move-down has 0 surviving method factors; no near-miss in move-down and photo-shortfall computations); unique solution PASS (blind = GT on all scored values: 202.00, 5, 327.00, 355.20).
  - task 1: SOURCE-POLICY RED (F2); SOURCE-CHAIN RED (R←F declared condition true at frozen_time); SOURCE-FACTOR RED (F5 -> damage approval has 0 surviving method factors; no near-miss in schedule estimate and damage approval); SOURCE-TASK RED (F3: reading A {S, R} vs GT reading B {S, C, F, R}). Blind reading B = GT on all scored values: 723.15, L2/31.87, 151.29, 923.43.
- Coverage and scopes: charter_scope task 0 = {move_down, photo_shortfall, partner_price, cleaning_approval}; task 1 = {schedule_estimate, upheld_correction, level_correction_refund, damage_approval}. Pairwise disjoint, jointly cover all eight extended policies, matching the pre-reveal derivation from the graph's two components. Task tools closed over the eight uuid8 tools, each independently generated.
- Trees: task 0 — 3 prerequisite problems, 4 value_input edges, owner=user upload, acyclic. Task 1 — 3 declared prerequisite problems, 2 value_input edges, owner=user schedule filing, acyclic; but its R←F edge fails the opening-unmet test (1.md finding 2). Whole-difficulty graph acyclic.
- Factors: every computation declares 4–6 factors with ≥2 parameter / ≥1 method as declared, every ladder ≥3 tiers stated in its rule, every factor bears weight on its task's world against an honest baseline, every whole-baseline gives a definite number different from gold (task 0: 100.00/0/140.00/100.00; task 1: 428.02/60.00/40.00/723.15). Failures: F4 and F5 (unreal ladders removing the only method factor of two computations); no near-miss in four computations (task 0 steps 9, 11; task 1 steps 11, 17).
- Charter-global RED outstanding: F1 (undeclared selector override vs base damage_level_classification), F2, F3, F4, F5.
- Gates: the instantiation-stage gate snapshot supplied with the brief is all green (traceability deferred); the auditor did not re-run gates (Step 0: cite, do not run). A re-run on a final form belongs to the next revision after rework.

## revision_2

### charter_global_frozen (revision_2)

- Re-audit round 2. Written before any round-2 task GT was read. Auditor: same independent auditor as round 1.
- Inputs (sha256 re-checked, all match HASHES.txt): damage.extended.yaml f8a0d17a284ec8081f989006c2b6c642929b53425665ce9678ebb4b874fa2748 (CHANGED from 0a0ad092…); task_tools.py 17ea950d5a95b942d87aea9b2eb8f6a7cadf113b8a877753992da8234fa20f93 (unchanged); 0.view.json 559a2506…a41a; 1.view.json 79ad6ae3…f5fd.
- Because the charter changed, every charter-global section is re-derived in full below; the tool-module section (§action_binding_and_uuids) rests on task_tools.py alone, whose hash is unchanged, and is carried forward by reference on that ground.
- Gate snapshot from the brief: EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all rc=0; traceability deferred. Entry conditions complete.
- Base copy: the ten base keys compare equal to `blueprint/products/damage.yaml` again (verbatim).
- contamination_disclosure: this auditor read the round-1 GT of both tasks during round 1 (recorded in round-1 `source_gt_comparison`). Round-2 GT has not been read at this freeze. The round-2 derivations below are recomputed from the round-2 charter and views; where a figure equals a round-1 GT figure, it is because the inputs it reads did not change, and that is stated.

### What changed in the charter (located by reading every extended policy afresh)

1. damage_ext_review_move_down_fee: `overwrite` gains `damage_level_classification` / "A report is held at the lowest level whose definition matches the evidence on file"; the odor ladder is rewritten — "smoke or vape odor ... takes the odor share of the cabin-adjusted fee; a food or drink spill, animal hair or mess or bodily fluids with at least one professional cleaning document on the assessment's evidence ledger takes the flat deodorizing charge; any other report, such as one of trash or debris or one cleaned without a professional cleaning document, takes no odor component"; compute `odor_component` follows it.
2. damage_ext_upheld_level_correction_fee: `overwrite` gains the same `damage_level_classification` clause.
3. damage_ext_repair_schedule_estimate: the filing sentence now reads "the driver files the schedule estimate as a second repair estimate, its amount replaces the shop estimate's amount as the repair amount on file (repair_receipt_amount), and both estimates stay on the evidence ledger".
4. damage_ext_damage_fee_on_approval: settlement tier 2 adds "(a shop estimate checked against a second estimate)"; the lost-time ladder is rewritten — exterior on Black/Black SUV: per day from drop-off "through the date of the latest repair estimate or receipt on the assessment's evidence ledger (the report date when none is on the ledger)"; exterior on any other option: one day; "an interior repair, which leaves the vehicle drivable, takes no lost driving time" (compute follows); new sentence "For an approved damage fee the cap beyond which the part of a repair is never charged to the rider and is referred to the insurance claim desk is the vehicle damage cap."; the refund prerequisite is now a state-form sentence: "A damage fee is charged to a rider only after each earlier charged fee assessment of that rider is held at a level whose entry gate lists its incident category and, where that level is below the level its fee was charged at, carries a level-difference refund booked at the level it is held at." with condition "For every other damage_assessments row of the rider (same customer_id) with a damage_fee_charge on its ledger: variant_name names a level whose entry gate lists incident_category, and if variant_name is below the fee_level of its damage_fee_charge, its ledger carries a damage_fee_partial_refund whose fee_level equals variant_name.", `form: state`, `gate: damage_events.fee_level`, no fallback.
5. photo_shortfall, partner_price, cleaning_approval, level_correction_refund: unchanged in rule, compute, factors and prerequisite.

### policy_conflict_scan (revision_2)

Same eight policies, same targets, owners, `computes`, status scopes and cross-category reads as round 1; the graph is unchanged in shape (the refund edge changes form only). Scope components unchanged: {move_down, photo, price, cleaning_approval} and {schedule, damage_approval, correction, refund}. New sentence on the excess-to-insurance cap removes the ambiguity recorded as O10. New residual (observation O11): the declared superseded clause is the prefix "A report is held at the lowest level whose definition matches the evidence on file"; the rest of that base sentence — "when the evidence matches a lower level than the one reported, the reviewer moves it down (reclassification_direction) and never up" — stays in force without its "lowest level" target. For a gate-excluded report the extended selector supplies the target, so the merged reading is single; for a gate-listing report whose evidence matches a lower definition, the merged charter names no target level. Neither task's world reaches that case.

### rule_compute_equivalence (revision_2)

- move_down odor: compute `cabin_fee * K('odor_share') if incident == 'smoke_or_vape_odor' else (K('odor_flat') if (food/animal/bodily) and odor_documents > 0 else 0.0)` = rule sentence 1 above. Rank-proxy O4 for odor no longer applies (the rule no longer reads odor_treatment_included).
- damage_approval lost time: compute uses `MX(latest estimate date, latest receipt date) if documents on ledger else F('reported_at')`, exterior/Black test, exterior-other one day, else 0 — matches the rewritten sentence. O5 (rule "on file" vs ledger rows) is closed: the rule now says "on the assessment's evidence ledger" and names the report-date fallback.
- All other policies: unchanged, round-1 conclusions stand (PASS; O4 still applies to the correction's `held_rank >= 3 and new_rank <= 2` proxy).

### action_binding_and_uuids (revision_2)

Carried forward from round 1 by reference: task_tools.py hash unchanged (17ea950d…fa20f93) and every `(target_tool, computes)` pair in the new charter is identical to round 1. PASS; O1 stands.

### prerequisite_graph (revision_2)

- Graph: photo→move_down, price→move_down, cleaning_approval→{move_down, price, photo}, damage_approval→{schedule, refund}, refund→correction. Acyclic. Every `policy_source` is a verbatim substring of its blocked policy's rule (re-checked for all seven). All seven edges `form: state`; no `fallback_reason` anywhere.
- New edge damage_approval → refund: condition and sentence now say the same thing (each earlier charged assessment at a gate-listing level, and where below its charge level, a partial refund at the level held). F2 closed: the round-1 situation (earlier assessment just moved to a gate-listing level, no refund booked) now gives the same conclusion under both — blocked. `gate: damage_events.fee_level` is a record field; `resolved_by` = refund_level_difference_30807e99 = the refund policy's target_tool.

### prerequisite_sentences (revision_2)

- Edges 1–6: unchanged sentences; round-1 PASS stands.
- Edge 7 (new state form): "A damage fee is charged to a rider only after each earlier charged fee assessment of that rider is held at a level whose entry gate lists its incident category and, where that level is below the level its fee was charged at, carries a level-difference refund booked at the level it is held at." — "only after"; state in record words (level held vs entry gate; level held vs charge level; partial refund booked at the level held); no tool, id or snake_case token; scope "each earlier charged fee assessment" = condition "every other ... row ... with a damage_fee_charge". The last conjunct is brought about by one write only (the refund rule's partial refund "booked as a partial refund against that charge at the level moved to"); the first conjunct is the correction rule's write, which the refund rule itself waits on. Derivation: earlier charged assessment at a gate-excluding level -> correction rule moves it -> refund rule books the level-difference refund at the new level -> approval. Single reading. F3 closed.
- Observation O12: the sentence's first conjunct also states, on the approval's own rule, the state the refund policy waits on (correction done), so the approval's rule carries the order "after the correction" with no declared approval→correction edge. The order is already forced through refund→correction, so the two candidate orders do not exist and no terminal state differs; recorded as an observation, not RED.
- Observation O13: under the new sentence, an earlier charged fee that is undisputed and stands at a gate-excluding level can be corrected (the correction rule covers "undisputed"), but then needs a level-difference refund that the refund rule and base `damage_evt_refunds` allow only "while it is disputed or after it was upheld"; such a rider's new damage fee waits indefinitely. Not engaged by task 1 (its earlier assessment is upheld).

### override_declarations (revision_2)

- move_down and upheld_correction now declare `damage_level_classification` "A report is held at the lowest level whose definition matches the evidence on file" with the extended selector as replacement. F1 closed (residual O11 above).
- damage_approval: the excess-to-insurance clause now has its cap named in the extended rule; O10 closed.
- schedule_estimate (overwrite []): "both estimates stay on the evidence ledger" adds to base evidence handling, contradicts no base sentence.
- All other sweeps unchanged from round 1.

### factor_ladders (revision_2)

- move_down `odor_treatment` (method): tiers "smoke or vape odor" -> share of cabin-adjusted fee; "food or drink spill, animal hair or mess or bodily fluids, and ≥1 professional cleaning document" -> flat deodorizing charge; otherwise -> none. Reachability over the move-down domain (L4 food/smoke/animal -> L3; L4/L3 trash -> L2): smoke reaches tier 1; food/animal with a work order reach tier 2; trash, or food/animal without a professional document, reach the fall-through. No condition holds of every report reaching the write; the three outcomes are distinct and plausible (whole-cabin odor treatment priced with the cabin, a flat deodorizing pass after a professional clean, nothing for litter). Label honest. F4 closed. move_down: 5 factors (4 parameter / 1 method).
- damage_approval `damage_lost_time` (method): tiers "exterior repair on Wayfare Black or Wayfare Black SUV" -> per-day count; "exterior repair on any other ride option" -> one day; "an interior repair" -> none. Both damage levels reach this write, so every tier is reachable; the condition no longer rests on document presence (the review-entry gate made that universal in round 1). Multi-source (level + trip ride option). Label honest. F5 closed. damage_approval: 5 factors (4 parameter / 1 method).
- estimate_settlement: tier 2 now glossed "(a shop estimate checked against a second estimate)" and the schedule rule keeps both estimates on the ledger, so the 0.95 reading is explicit. O8 closed.
- All other ladders unchanged; round-1 structural conclusions stand.

### findings (revision_2, charter-global, pre-reveal)

- F1 closed (both selector overrides declared); residual observation O11.
- F2 closed (condition = sentence; record-visible).
- F3 closed (state form; "owed" no longer used).
- F4 closed (odor ladder reachable in all tiers, no universal condition).
- F5 closed (lost-time ladder keyed on level and ride option; all tiers reachable).
- O5, O6, O8, O10 closed (rule text now names the ledger and report-date fallback; no action-form edge; second estimate explicit; insurance cap named).
- Open observations carried: O1, O2, O3, O4 (correction proxy only), O7.
- New observations: O11 (remnant base clause without target), O12 (approval rule also states the correction state; order forced transitively), O13 (undisputed mis-levelled earlier charge can block a new damage fee indefinitely).
- No new charter-global RED.

### closing_checklist (revision_2)

Written after both tasks' revision_2 frozen derivations and GT comparisons were on disk.

- Per-task files 0.md, 1.md carry revision_2 sections appended below the untouched round-1 text; `_difficulty.md` round-1 sections untouched, revision_2 appended.
- Round-1 RED disposition (reworker's claimed closures verified item by item): F1, F2, F3, F4, F5 closed; O5, O6, O8, O10 closed; task 0 findings 1–2 and observations 3, 5 closed; task 1 findings 1–5 closed. Left open as observations, as the reworker stated: O1, O2, O3, O4 (now only the correction's vehicle-offline proxy), O7, task 0 observation 4. New observations: O11, O12, O13. No new RED; no regression.
- Per-task verdicts (revision_2): task 0 — PASS on all four relationships (scored 187.00 / 5 / 327.00 / 355.20). Task 1 — PASS on all four relationships (723.15 / L2 31.87 / 151.29 / 923.43). Blind = GT on every scored value and every factor-sensitivity figure in both tasks.
- Coverage and scopes: task 0 {move_down, photo_shortfall, partner_price, cleaning_approval}; task 1 {schedule_estimate, upheld_correction, level_correction_refund, damage_approval}; disjoint, jointly complete; eight independently generated uuid8 tools (task_tools.py unchanged).
- Trees: each has 3 prerequisite problems, ≥ 2 value_input edges (task 0: 4; task 1: 2), an owner=user write (photo upload; schedule filing), every edge false at the opening and load-bearing; whole-difficulty graph acyclic.
- Factors: every computation 4–6 factors with ≥2 parameter / ≥1 method surviving; every ladder ≥3 reachable, distinct tiers stated in its rule; every factor bears weight against an honest baseline; whole-baselines definite and ≠ gold (task 0: 100.00 / 0 / 140.00 / 100.00; task 1: 428.02 / 60.00 / 40.00 / 723.15); each computation has a genuine near-miss (estimated vs actual minutes; L4 stamps; Friday drop-off; home_market LAS; cancelled Plus Annual).
- Gates: coordinator's post-rework snapshot all green (traceability deferred to render); not re-run by the auditor (Step 0).
- **Difficulty passes the source-layer audit at revision_2.**

## revision_3

### charter_global_frozen (revision_3)

- Re-audit round 3, written before any round-3 task GT was read. Reason given by the coordinator: the KB audit found factor tiers defined on sibling factors' outputs (D1/P4); the charter was reworked.
- Inputs (sha256 re-checked): damage.extended.yaml 7df9d512d8b07f499b464f5de2c22733b85a9b8b42dda7fa75ea2495ef252160 (CHANGED from f8a0d17a…); task_tools.py 17ea950d…fa20f93 (unchanged); 0.view.json 559a2506…a41a and 1.view.json 79ad6ae3…f5fd (both unchanged from round 2). Base copy still verbatim (ten keys equal).
- Gate snapshot from the brief: EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE / TRACEABILITY all rc=0; validate_scenario VALID.
- contamination_disclosure: round-1 and round-2 GT of both tasks were read in earlier rounds. Round-3 GT unread at this freeze.
- Method: policy-by-policy diff of rule, overwrite, params, prerequisite, compute and factors against the round-2 charter as dumped in round 2. Sections whose inputs did not move are carried forward by reference to §revision_2 on that ground.

### What changed (diff against round 2; nothing else differs)

1. damage_ext_review_move_down_fee / odor_treatment tier 1: "smoke or vape odor ... takes the odor share of the flat fee of the level moved to" (was "of the cabin-adjusted fee"); compute `new_flat_fee * K('odor_share')` (was `cabin_fee * ...`); ladder text matches.
2. damage_ext_approval_photo_shortfall: new param `overview_photos_per_passenger_row: 1`; rule restructured — "Where the adjustments below apply, the approval photo set is the core photo count of the level held plus the occupied-seat close-ups, the liquid close-ups and the trim close-ups. The core photo count ... : a level that requires a photo of each affected surface takes ... the per-row photo pair for each seat row ..., and its minimum photo count is not used; a level that requires close-up and in-context photos of the affected area takes its minimum photo count plus one overview photo of each passenger row, the seat rows behind the driver's row of the reported vehicle; any other level takes its minimum photo count." Seat-row photos renamed "occupied-seat close-ups" ("full-party" / "partial-party"), same conditions and values. Compute: `set_core` (3 tiers) then `photo_set = set_core + row_photos + liquid_photos + trim_photos`. `set_assembly` now `decides: set_core`, baseline `set_core: set_minimum`.
3. damage_ext_repair_schedule_estimate / paint_method tier 1: blended paint "at the schedule's refinish labor rate" (new param `refinish_labor_rate: 108.0`), was "at the labor rate of the estimate"; compute uses `K('refinish_labor_rate')`.
4. Policies partner_price, cleaning_approval, damage_approval, upheld_correction, level_correction_refund: identical to round 2.

### Self-containment of every factor (the D1/P4 question), whole charter

For each factor, the inputs its tiers and outcomes read (bindings plus non-factor inputs); "sibling output" = a binding decided by another factor of the same policy.

| policy | factor | reads | sibling output read? |
| --- | --- | --- | --- |
| move_down | cabin_size | trip ride option, seats | no |
| move_down | metro_cost | trip market | no |
| move_down | liquid_exposure | incident, trip actual minutes | no |
| move_down | upholstery | trip ride option | no |
| move_down | odor_treatment | incident, cleaning_receipt count, `new_flat_fee` (level flat fee, not a factor) | no (round 2 read `cabin_fee`, the cabin_size output — now removed) |
| photo | seat_row_photos | trip ride option, seats | no |
| photo | liquid_close_ups | incident, trip actual minutes | no |
| photo | trim_close_ups | trip ride option | no |
| photo | set_assembly | level's photo subjects, `set_minimum`, own `vehicle_rows`, overview param | no (round 2 tiers added row/liquid/trim outputs — now moved to `photo_set`, a non-factor sum) |
| price | service_basis | trip ride option, seats, level package/row price | no |
| price | extraction / metro_rate / rush / conditioning / weekend | own inputs | no |
| cleaning_approval | fee_basis | level param, cost on file, assessed fee, level flat, cleaning docs | no |
| cleaning_approval | lost_driving_time / vehicle_fee_cap / pass_goodwill / tenure | own inputs, level flat | no |
| schedule | paint_method | level, trip ride option, refinish rate param | no (round 2 read `labor_rate`, the metro_labor_rate output — now removed) |
| schedule | parts_tier / metro_labor_rate / parts_tax / sensor_calibration | own inputs | no |
| damage_approval | all five | own inputs, `level_cap` | no |
| upheld_correction | carried_fee / lost_time_removal / correction_credit / age | ledger, flats, dates | no |
| refund | refund_base / goodwill ×3 | ledger, flats, `standing`, pass, trip charges, closed date | no |

Every factor is now self-contained. PASS.

### rule_compute_equivalence (revision_3)

- move_down odor: rule "the odor share of the flat fee of the level moved to" = `new_flat_fee * K('odor_share')`. PASS.
- photo: `set_core` three branches = the core-count sentence (per-row pair × vehicle rows, minimum not used; minimum + overview × (rows − 1), "the seat rows behind the driver's row"; minimum); `photo_set` = "the core photo count of the level held plus the occupied-seat close-ups, the liquid close-ups and the trim close-ups"; `result` unchanged. All compute_basis entries are verbatim substrings of the rule (re-checked by script for all eight policies). PASS.
- schedule paint: rule "at the schedule's refinish labor rate" = `K('refinish_labor_rate')`. PASS.
- Others: carried from §revision_2 (inputs unchanged).

### factor_ladders (revision_3)

- odor_treatment (method): tiers unchanged in condition; outcome of tier 1 is now a share of the level-moved-to flat fee; tiers still distinct (share of flat / flat charge / none) and all reachable in the move-down domain (smoke L4→L3; food/animal with a work order; trash or no professional document). Method label honest (proportion vs fixed vs none). PASS.
- set_assembly (method, decides set_core): per-row pairs with the minimum discarded / minimum plus one overview per passenger row / minimum — three different computations of the core, each reachable (L4; L2–L3; L1 and both damage levels). Honest method. Baseline `set_core = set_minimum`, consistent with the standard count when the three parameter factors are also at baseline (0). PASS.
- seat_row_photos (parameter): relabelled text only, same tiers and values. PASS.
- paint_method (method): blended (hours × panels × refinish rate) / none / flat spot — still three distinct computations, all reachable. PASS.
- Counts unchanged: move_down 5 (4p/1m), photo 4 (3p/1m), price 6 (5p/1m), cleaning_approval 5 (3p/2m), schedule 5 (4p/1m), damage_approval 5 (4p/1m), correction 4 (2p/2m), refund 4 (3p/1m).

### Other charter-global sections (revision_3)

- policy_conflict_scan, override_declarations, prerequisite_graph, prerequisite_sentences: no rule sentence, overwrite or prerequisite field changed apart from items 1–3 above, none of which touches an edge or a base sentence; §revision_2 conclusions carried forward.
- action_binding_and_uuids: task_tools.py unchanged; carried forward.

### findings (revision_3, charter-global, pre-reveal)

- No round-2 RED existed; no new RED found.
- New observation O14: the photo rule now adds the occupied-seat, liquid and trim close-ups to the core of every level, including "any other level" (Level 1 and both damage levels). For a Damage Fee (Exterior Repair) report on a Wayfare Black, the approval set therefore asks for leather-trim close-ups and occupied-seat close-ups of the cabin as well as the exterior photos. No task's tree reaches it (task 1's damage approval carries no photo sentence).
- Carried observations: O1, O2, O3, O4 (correction proxy), O7, O11, O12, O13.

### closing_checklist (revision_3)

- revision_3 appended to all three files; earlier revisions untouched.
- Round-2 had no RED; the round-3 rework (D1/P4 from the KB audit) is verified: every factor in the charter now reads only its own bindings and non-factor inputs (table in §revision_3); the three reworked methods (odor_treatment, set_assembly, paint_method) remain genuine three-tier methods; every factor bears weight on its task's world (task 0 photo 5/5/5/5 vs 7; task 1 schedule 648.87/687.15/635.35/720.18/628.15 vs 723.15; all others unchanged and re-confirmed).
- Moved value: task 0 photos_in_upload 5 -> 7, uniquely entailed (core 3 + 2 passenger-row overviews, + 2 + 2 + 2; less 4).
- Per-task verdicts: task 0 PASS (187.00 / 7 / 327.00 / 355.20); task 1 PASS (723.15 / L2 31.87 / 151.29 / 923.43). Blind = GT on every scored value and factor figure.
- No new RED; no regression. New observation O14 (occupied-seat and trim close-ups now added to every level, including damage levels; not reached by any task). Carried observations O1, O2, O3, O4, O7, O11, O12, O13; task 0 observation 4.
- Gates: coordinator snapshot all green including TRACEABILITY; validate_scenario VALID; not re-run by the auditor.
- **Difficulty passes the source-layer audit at revision_3.**
