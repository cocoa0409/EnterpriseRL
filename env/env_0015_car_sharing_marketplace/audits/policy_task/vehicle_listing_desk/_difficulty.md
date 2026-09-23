# Policy-task audit — vehicle_listing_desk / charter-global

## charter_global_frozen

- Freeze time: 2026-09-22, written **before any task's GT fields were read**.
- Auditor: independent source-layer auditor (not the instantiating agent).
- Frozen inputs and their hashes (sha256, first 16 hex):
  - `env/env_0015_car_sharing_marketplace/tasks/vehicle_listing_desk/listings.extended.yaml` — `9d07c59a7b520be2`
  - `env/env_0015_car_sharing_marketplace/tasks/vehicle_listing_desk/task_tools.py` — `2a554fe87bc1ac0a`
  - masked task view `0.json` — `2b9a69b6a228b3a8`; masked task view `1.json` — `13351c5019d46571`
- Fields permitted at this stage: the blueprint (`blueprint.yaml`, `blueprint/products/listings.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`), the whole of `listings.extended.yaml` (base section + `extended_policies`), the whole of `task_tools.py`, and each task's `frozen_time`, `user_scenario`, `initial_state` only.
- Fields explicitly masked and not read before this file was written: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state`, and the scenario `worklog.md`.
- Entry conditions: the coordinator supplied the gate snapshot (`check_extended.py`, `check_task_tools.py`, `replay_tasks.py --check`, `check_solvability.py`, `check_compute.py`, `check_grounding.py`, `check_cross_fire.py`), all green, together with the masked-view hashes, which reproduce exactly as listed above. `check_traceability.py` is correctly deferred to the KB stage. **Entry conditions complete.** A green gate row is the qualification to enter this audit, not evidence of correctness.

### base_section_identity

The base section of `listings.extended.yaml` (`category`, `display_name`, `binding`, `lifecycle`, `accounts`, `parameter_schema`, `variants`, `events`, `measures`, `policies`) was compared key-by-key against `blueprint/products/listings.yaml` after YAML load: **every key identical**. The base copy has not been rewritten.

### policy_conflict_scan

Eight extended policies, all `category: listings`, subjects drawn from the 15 claimed event families:

| policy | subject | target_tool | computes | base_policy_refs | overwrite |
| --- | --- | --- | --- | --- | --- |
| `listings_ext_fault_intake` | listings_defect_reported | `log_vehicle_fault_a3e017f7` | attached_photo_count | listings_evt_defect | `[]` |
| `listings_ext_valuation_assessment` | listings_valuation_reassessed | `record_vehicle_valuation_559b4236` | assessed_value_amount | listings_evt_valuation | `[]` |
| `listings_ext_class_assignment` | listings_class_reassigned | `reassign_value_class_4bb6b10c` | governing_value_amount | listings_evt_valuation | 1 clause |
| `listings_ext_price_reset` | listings_price_updated | `set_daily_price_59fd8a00` | daily_price_amount | listings_price | `[]` |
| `listings_ext_document_verification` | listings_document_verified | `verify_listing_document_28456ce9` | verification_image_count | listings_evt_documents | `[]` |
| `listings_ext_interval_grant` | listings_inspection_completed | `record_vehicle_inspection_59fe0be1` | interval_miles_granted | listings_evt_inspection | 1 clause |
| `listings_ext_booked_consumption` | listings_odometer_reported | `record_booked_mileage_82af4bea` | booked_miles_consumed | listings_evt_inspection | `[]` |
| `listings_ext_reported_consumption` | listings_odometer_reported | `report_vehicle_mileage_90a8825c` | reported_miles_consumed | listings_evt_inspection | `[]` |

Overlapping subjects: `listings_odometer_reported` is claimed by two policies (`booked_consumption`, `reported_consumption`). They are separated cleanly — different target tools, different `computes` bindings, and different actors (marketplace-taken reading vs host-reported reading), and `report_vehicle_mileage_90a8825c` hard-codes `inspection_channel="self_photo"` while `record_booked_mileage_82af4bea` takes the channel as an argument. No conflict.

`listings_evt_valuation` is referenced by two extended policies (`valuation_assessment`, `class_assignment`); they compute different quantities (the assessed figure on the condition record vs the governing value written to the listing) against different tools. No conflict between them.

Triggers, time anchors and terminal states: every policy evaluates on `NOW` = the task's `frozen_time` date; no policy names a future date, a cooling-off period or an external approval. Cross-category reads are declared per policy in `cross_category` and confined to `service`, `roadside`, `hostplan`, `payouts` — all read-only aggregates through `XCOUNT`/`XSUM`/`CFIELD`. Seven cross-category declarations across the suite, matching the gate snapshot.

Scope exclusivity and completeness over the two tasks (derived from the prerequisite graph below, not from any masked field): the graph is two disjoint chains of four policies each, and each task's root problem sits at the head of one chain —

- chain A: `price_reset` → `class_assignment` → `valuation_assessment` → `fault_intake`
- chain B: `reported_consumption` → `booked_consumption` → `interval_grant` → `document_verification`

The two chains are **pairwise disjoint** and **jointly complete** over the eight extended policies.

**Conflicts found between the inherited base section and the extended section are recorded under `override_declarations` below.**

### rule_compute_equivalence

Check 2 was run binding-by-binding over all eight policies: every `compute` binding carries a `compute_basis` entry, and every `compute_basis` entry is a verbatim sentence (or contiguous sentence group) of that policy's own `rule`. Every factor tier named in `factors[].ladder` was matched against a `rule` sentence and against a branch of the `decides` binding; no tier lives only in `compute`, and no `compute` branch is absent from the rule. Rounding conventions (`RND(...,2)`, `RND(...,0)`, `RND(...,6)`), floors (`MX`), ceilings (`MN`) and window conventions (`within_months=3/12/24`, `DAYS`, `MONTHS`) each have a quoted sentence.

**One binding fails the sweep-back:** see finding **CG-2** (`listings_ext_price_reset.capped_price`). Its `compute_basis` sentence states the share is applied to the price the host is asking, while the expression applies it to `boundary_target`.

One further wording/expression gap that does **not** rise to a red light on its own: `listings_ext_class_assignment` rule r03 says the three adjustments are "each … a share applied to the figure the one before it produced, taken in the order mileage, service record and recovery history", while `compute` forms one product `marketplace_figure * mileage_share * service_share * roadside_share` with a single `RND(...,2)`. Multiplication is associative and no intermediate rounding is specified, so the two readings coincide for every input; recorded as an observation only (**CG-OBS-1**).

### action_binding_and_uuids

Each `(target_tool, computes)` pair in the table above is claimed by **exactly one** policy; there are eight tools in `task_tools.py` and eight extended policies, one-to-one. No policy adds a confirmation, review, wait or procedure outside its own rule.

`owner` assignment: six `owner="agent"` write tools and two `owner="user"` write tools (`set_daily_price_59fd8a00`, `report_vehicle_mileage_90a8825c`). Each chain's **root** problem is resolved by one of the two `owner="user"` tools, so each task's tree contains at least one write the customer must run.

Tool bodies were read in full. **No function validates a prerequisite**: `log_vehicle_fault`, `record_vehicle_valuation`, `verify_listing_document`, `record_vehicle_inspection` and `record_booked_mileage` call `ctx.create(...)` unconditionally; `reassign_value_class` and `set_daily_price` call `ctx.update(...)` and return a "no listing found" sentence only when the row id does not exist; `report_vehicle_mileage` calls `ctx.create(...)` unconditionally. None aggregates history, none recomputes a figure, none refuses, errors or hints while a prerequisite is unresolved.

uuid8 tails, one per tool: `a3e017f7`, `559b4236`, `4bb6b10c`, `59fd8a00`, `28456ce9`, `59fe0be1`, `82af4bea`, `90a8825c`. No tail is reused, none is a sequence number, none is an increment of another. One weak signal is recorded as an observation (**CG-OBS-2**): `59fd8a00` and `59fe0be1` share the three-character prefix `59f` with adjacent fourth characters (`d`, `e`); the remaining five characters are unrelated, and no consequence can be demonstrated.

Docstring silence about sequence: no docstring names another tool or states its action's position in a workflow. Two phrases were examined and cleared or downgraded:

- Every tool's Id-class argument notes say the value is "read from the … lookup before the call" — this locates the *argument's source*, not the action's place in a cross-problem order. Cleared.
- `record_booked_mileage_82af4bea.source_inspection_id` reads "read from the receipt of the call that filed it or from the vehicle condition record lookup." This presupposes that some earlier call filed the condition record. It names no tool and refuses nothing, so it is recorded as an observation (**CG-OBS-3**), not a red light.

### prerequisite_graph

Check 7, over the single `prerequisite` graph:

| blocked policy | problem | kind | gate | form | resolved_by | fallback_reason |
| --- | --- | --- | --- | --- | --- | --- |
| `listings_ext_fault_intake` | — (`[]`) | — | — | — | — | — |
| `listings_ext_valuation_assessment` | `listings_ext_fault_intake` | value_input | `condition_holdback` | state | `log_vehicle_fault_a3e017f7` | absent (correct) |
| `listings_ext_class_assignment` | `listings_ext_valuation_assessment` | value_input | `marketplace_figure` | state | `record_vehicle_valuation_559b4236` | absent (correct) |
| `listings_ext_price_reset` | `listings_ext_class_assignment` | value_input | `band_ceiling` | state | `reassign_value_class_4bb6b10c` | absent (correct) |
| `listings_ext_document_verification` | — (`[]`) | — | — | — | — | — |
| `listings_ext_interval_grant` | `listings_ext_document_verification` | value_input | `document_share` | state | `verify_listing_document_28456ce9` | absent (correct) |
| `listings_ext_booked_consumption` | `listings_ext_interval_grant` | value_input | `anchor_reading` | state | `record_vehicle_inspection_59fe0be1` | absent (correct) |
| `listings_ext_reported_consumption` | `listings_ext_booked_consumption` | value_input | `reported_stretch` | state | `record_booked_mileage_82af4bea` | absent (correct) |

- `prerequisite` is filled in on every policy (`[]` where there is none). Every `problem` points at another **extended** policy id in this file; none points at a base policy or at itself.
- **Acyclic**: the graph is two linear chains of length 3, no back edge, no cross-chain edge.
- Every `form` is `state`; no edge is action-form, so no `fallback_reason` is required and none is present. The state form's priority is therefore honoured everywhere by construction.
- Every `kind` is `value_input`, and every `gate` names a binding that genuinely exists in the blocked policy's `compute` (`condition_holdback`, `marketplace_figure`, `band_ceiling`, `document_share`, `anchor_reading`, `reported_stretch` — all present). No edge is a bare `state_gate`, so `max(n − 1, 1)` = 2 `value_input` edges per three-problem tree is satisfied with 3.
- Every `resolved_by` is the depended-on policy's own `target_tool`, and each names a tool whose `ctx.create`/`ctx.update` genuinely brings the gate state about (see the per-edge derivations in the task files).
- Two `effect` strings assert a *particular* tier transition rather than the general effect of the write — see **CG-4**.

### prerequisite_sentences

Check 6 on each of the six edges. Each `policy_source` was located verbatim in the **blocked** policy's own `rule`.

1. `valuation_assessment` ← `fault_intake` — r05: "The valuation the marketplace records is fixed only after every fault the vehicle's condition record has been advised of stands on that record as a fault report of its own." Connective "only after" ✓. State form: "stands on that record as a fault report of its own" — record-visible, no performer, no tool, no snake_case, no row id ✓. Exactly one write of this difficulty creates a `listings_defect_reported` row (`log_vehicle_fault_a3e017f7`) ✓. Derivation: the sentence + the condition records + `listings_ext_fault_intake`'s own rule ("A fault found on a Keyturn Vehicle Listing is opened on that vehicle's condition record …") lead to opening a fault record, one reading only. **Scope note:** the edge's `condition` adds "including any advisory carried on a completed inspection", a specification the sentence does not carry — recorded as **CG-3**.
2. `class_assignment` ← `valuation_assessment` — r04: "The value class a listing is moved into is not settled before a valuation dated within thirty calendar days of the handling date stands on the vehicle's condition record." Connective "not … before" ✓, state form ✓, one write (`record_vehicle_valuation_559b4236`) creates `listings_valuation_reassessed` ✓, condition neither strengthened nor weakened ✓.
3. `price_reset` ← `class_assignment` — r06: "The daily price a host may ask is fixed only once the vehicle value standing on the listing is the value the marketplace has settled on for it." Connective "only once" ✓, state form naming a listing field in table words ("the vehicle value standing on the listing") ✓. Exactly one write rewrites `listings_vehicles.market_value_amount` — `reassign_value_class_4bb6b10c`; `record_vehicle_valuation_559b4236` explicitly leaves the listing untouched ("Nothing on the listing itself moves"), so the hop resolves uniquely ✓.
4. `interval_grant` ← `document_verification` — r05: "The interval a completed inspection grants is fixed only after a verification of the vehicle's registration dated within thirty calendar days of the handling date stands on its condition record." Connective "only after" ✓, state form ✓, one write (`verify_listing_document_28456ce9`) creates `listings_document_verified` ✓.
5. `booked_consumption` ← `interval_grant` — r04: "The miles a reading the marketplace books takes off the interval are not counted before a completed inspection dated within seven calendar days of the handling date stands on the vehicle's condition record." Connective "not … before" ✓, state form ✓, one write (`record_vehicle_inspection_59fe0be1`) creates `listings_inspection_completed` ✓.
6. `reported_consumption` ← `booked_consumption` — r03: "The miles a reading the host reports take off the interval are not counted before an odometer record dated the handling date stands on the vehicle's condition record." Connective "not … before" ✓, state form ✓. **Two writes of this difficulty create a `listings_odometer_reported` row dated the handling date** — `record_booked_mileage_82af4bea` and the blocked policy's own `report_vehicle_mileage_90a8825c`. Recorded as **CG-OBS-4**; the self-referential candidate is excluded by the sentence itself (the reading whose miles are being worked out cannot be the record they wait on), so the hop is still resolvable in one reading.

No blocked rule carries a second wording of its dependency, a tool name, a policy id or another problem's id; no depended-on rule restates the blocked rule's sentence.

**Cross-problem orders stated in rules that ground no declared edge:** the base rule `listings_evt_defect` sentence b5 — "Putting a fault right is evidenced by a fresh inspection record, not by the host marking it resolved" — states an order between a fault and an inspection that grounds no declared edge. It is a **base** sentence and neither task's tree rests on it (chain A contains no inspection write; chain B contains no fault write), so it is recorded as an observation (**CG-OBS-5**) rather than a red light.

### override_declarations

Check 1's **finding half**, sentence by sentence against each `base_policy_refs` entry. Findings only; the demonstration of what each costs a task is in that task's file.

**Declared and sound:**

- `listings_ext_class_assignment` declares its supersession of `listings_evt_valuation` b3 ("A host's own declared value is accepted where it sits inside the class's tolerance of the marketplace valuation …") by the tiered declared-value settlement. The merged semantics are unique: base b3's tolerance rule is replaced wholesale, not layered.
- `listings_ext_interval_grant` declares its supersession of `listings_evt_inspection` b1 ("A completed inspection grants the class's mileage interval afresh and sets the next due date the class's day interval ahead …"). The whole sentence is quoted, including the next-due-date half, so the extended policy's silence about the due date is covered by the declaration.

**Inherited without conflict** (checked sentence by sentence, conclusion reached on each): `listings_evt_defect` b0–b4, b6, b7; `listings_evt_valuation` b0, b2; `listings_evt_documents` b0–b5; `listings_evt_inspection` b0, b2, b5, b6; `listings_price` b2–b5; `listings_agg_multi_holding` b0–b2; `listings_agg_host_fleet` b0–b4; `listings_onboarding` b0–b6.

**Undeclared overrides found** — each is a base sentence not named in any `overwrite` that reaches a different conclusion from an extended sentence on the same subject:

- **CG-1a** `listings_evt_valuation` b5 vs `listings_ext_price_reset`.
- **CG-1b** `listings_evt_inspection` b3 vs `listings_ext_reported_consumption`.
- **CG-1c** `listings_price` b0 vs `listings_ext_price_reset` r05/r13/r14.
- **CG-1d** `listings_price` b0/b1 (band and movement limit read off *the class the vehicle sits in*) vs `listings_ext_price_reset` r07–r12 (band read off the *standing vehicle value plus a valuation-in-window test*; movement rate read off *listing age and fault count*).

All four are written up in full under `findings`.

### factor_ladders

Charter-global structure of the factors. Whether each bears weight is a fact about one world and lives in that task's `factor_weight`.

| policy | factors | parameter | method | multi-source tiers present | cross_difficulty factors (category) |
| --- | --- | --- | --- | --- | --- |
| `fault_intake` | 6 | 5 | 1 | yes (`repeat_fault_standard` t1/t2/t3, `recall_standing_addition` t1/t2, `inspection_clock_addition` t1/t2) | `care_plan_documentation_basis` (service) |
| `valuation_assessment` | 6 | 4 | 2 | yes (`use_intensity_rate` t1/t2, `fault_pattern_holdback` t1/t2, `damage_history_holdback` t1/t2, `advisory_condition_holdback` t1/t2) | `damage_history_holdback` (hostplan), `maintained_vehicle_step_basis` (service) |
| `class_assignment` | 5 | 3 | 2 | yes (`marketplace_figure_basis` t2, `documented_service_share` t1/t2, `declared_value_settlement` t1/t2) | `documented_service_share` (service), `recovery_history_share` (roadside), `declared_value_settlement` (hostplan) |
| `price_reset` | 4 | 3 | 1 | yes (`value_band_boundaries` t1/t2, `daily_movement_rate` t1/t2, `out_of_band_correction_basis` t1/t2) | `cover_standing_band_share` (hostplan) |
| `document_verification` | 4 | 3 | 1 | yes (`registration_image_standard` t2, `check_pattern_addition` t1/t2, `registration_lapse_addition` t1) | **none** |
| `interval_grant` | 6 | 5 | 1 | yes (`overrun_reduction_step` t1/t2, `fault_standing_basis` t1/t2) | `serviced_vehicle_addition` (service), `recovery_history_reduction` (roadside) |
| `booked_consumption` | 5 | 4 | 1 | yes (`anchor_reading_basis` t2, `idle_listing_allowance` t1/t2) | `workshop_transit_allowance` (service), `recovery_transit_allowance` (roadside), `repair_transit_allowance` (hostplan) |
| `reported_consumption` | 4 | 3 | 1 | yes (`reported_stretch_basis` t1/t2, `registration_lapse_private_allowance` t1/t2, `idle_period_allowance_step` t1/t2) | `idle_period_allowance_step` (payouts) |

Bounds: every policy declares 4–6 factors, ≥2 `parameter` and ≥1 `method` ✓. Every ladder has exactly three or four tiers, the fall-through counted; every tier is stated in full in the policy's own `rule` (condition + value or method) and implemented as a branch of the `decides` binding; `decides` is always an input binding, never `result` — except `fault_intake.care_plan_documentation_basis` and `interval_grant.fault_standing_basis`, whose `decides` are `documented_requirement` and `granted_interval`, both of which are still inputs to a subsequent `MX(...)` floor, so neither names `result` ✓. Binding sets are disjoint within each policy ✓.

**Tier distinctness:** no ladder in the charter selects the same value or the same method in two tiers. Checked pairwise over all 40 factors.

**Label honesty:** every `method` factor changes an algorithm rather than a number — `care_plan_documentation_basis` and `maintained_vehicle_step_basis` (scaling of the figure/rate), `step_down_anchor_basis`, `marketplace_figure_basis`, `anchor_reading_basis`, `reported_stretch_basis` and `registration_image_standard` (anchor/candidate-source selection), `declared_value_settlement` and `out_of_band_correction_basis` and `fault_standing_basis` (which quantity is carried forward). Every `parameter` factor's tiers substitute a figure into an unchanged formula ✓. No `method` tier names a computation rule the charter does not state.

**Conditions and outcomes that line of business actually holds:** each tier's condition was read against what a peer-to-peer car sharing marketplace weighs when it settles that quantity. No condition holds of every customer who reaches the write; every tier condition splits the population (fault counts and their kind, inspection staleness, recall standing, odometer bands, valuation bands, workshop spend, claim counts, callout counts, registration lapse, listing age, payout history). Two ladder-shape observations are recorded — **CG-OBS-6** and **CG-OBS-7**.

**Baseline coherence** (per policy: is `baseline.rule` self-sufficient, is every sentence of it in the `rule`, do its default keys match `baseline.params`, and is each factor's fall-through tier the baseline):

| policy | `baseline.rule` self-sufficient | sentences all in `rule` | `baseline.params` matches its own defaults | every fall-through = baseline |
| --- | --- | --- | --- | --- |
| `fault_intake` | yes (4 photographs, floor 3) | yes | yes | yes |
| `valuation_assessment` | yes (0.006/month, anchor = last valuation) | yes | yes | yes |
| `class_assignment` | yes (figure = value on the listing, rounded) | yes | yes (`[]`, no constants named) | yes |
| `price_reset` | yes (entry band 95/22, movement 0.15, share 1) | yes | yes | yes |
| `document_verification` | yes (3 images, cap 16) | yes | yes | yes |
| `interval_grant` | yes (10 000 miles, floor 1 000) | yes | **names only the two miles keys, but the rule's "the whole of it is open" fixes the share at 1.0, which `paper_currency_share.baseline` contradicts** | **no — `paper_currency_share`** |
| `booked_consumption` | yes (anchor = odometer on the listing) | yes | yes (`[]`) | yes |
| `reported_consumption` | yes (stretch from the latest telematics reading) | yes | **no — `baseline.params` names `reading_variance_tolerance_miles` (75), which no sentence of `baseline.rule` uses** | yes |

The two failures are written up as **CG-5** and **CG-6**.

### findings

---

**CG-1a — `SOURCE-POLICY RED` (undeclared override): base `listings_evt_valuation` b5 and `listings_ext_price_reset` give different prices after a class change.**

- *Symptom.* Two clauses in force fix the daily price a listing carries after its class moves, and they produce different figures.
- *Root cause.* `listings_ext_price_reset.overwrite` is `[]` and its `base_policy_refs` is `["listings_price"]`, so `listings_evt_valuation` b5 is inherited in full and is never named as superseded — while the extended policy's `result` is not the boundary b5 names.
- *Evidence.* Base `listings_evt_valuation` rule, final sentence: "A class change moves the price floor and ceiling with it, and **a daily price outside the new class's band is brought to the nearer boundary** rather than left outside it." Extended `listings_ext_price_reset` `compute`: `capped_price: RND(boundary_target * cover_share, 2)`, `held_price: MX(capped_price, lowest_today)`, `result: RND(MX(MN(held_price, band_ceiling), band_floor), 2)` — the cover share multiplies the boundary, so the written price is strictly below the nearer boundary whenever `cover_share < 1`.
- *Demonstrated consequence.* Bears on **task 0**, where the class does move and the standing price is above the new band; the two figures are computed against that world in `0.md` § `policy_self_consistency`.
- *Affected artifact and location.* `blueprint/products/listings.yaml` policy `listings_evt_valuation` (inherited verbatim into `listings.extended.yaml`); `listings.extended.yaml` → `extended_policies` → `listings_ext_price_reset` → `overwrite`, `rule` r05/r13–r15, `compute.capped_price`/`result`.

---

**CG-1b — `SOURCE-POLICY RED` (undeclared override): base `listings_evt_inspection` b3 says a divergent host reading is not recorded; `listings_ext_reported_consumption` records it.**

- *Symptom.* For a host-reported odometer standing further from the telematics figure than the class's variance tolerance, base directs the reading to be queried instead of recorded, while the extended policy computes a consumption figure and files the reading.
- *Root cause.* `listings_ext_reported_consumption.base_policy_refs` is `["listings_evt_inspection"]` with `overwrite: []`; b3 is inherited in full and never named.
- *Evidence.* Base `listings_evt_inspection` rule: "A telematics reading is authoritative where one exists; **a host reading standing more than the class's variance tolerance away from the telematics figure is queried rather than recorded**, and the listing is not suspended while the query is open." Extended `listings_ext_reported_consumption` r04: "…the stretch is measured from that highest standing reading to the odometer standing on the listing" — the reading is charged in full, and only the *other* tier (r05) mentions querying, and then only as a 75-mile reduction, not as a refusal to record. The extended policy's own `params` carry `reading_variance_tolerance_miles: 75`, showing the same tolerance is in play.
- *Demonstrated consequence.* Bears on **task 1**, where the host's reading stands 770 miles from the latest telematics figure against a class tolerance of 75; the two terminal states are worked out in `1.md` § `policy_self_consistency`.
- *Affected artifact and location.* `listings.extended.yaml` → base `policies` → `listings_evt_inspection` rule sentence 4; → `extended_policies` → `listings_ext_reported_consumption` → `overwrite`, `rule` r04–r06, `compute.reported_stretch`.

---

**CG-1c — `SOURCE-POLICY RED` (undeclared override): base `listings_price` b0 forbids the very clamping `listings_ext_price_reset` performs.**

- *Symptom.* Base states the marketplace's treatment of an out-of-band price as refusal and explicitly rules out clamping; the extended policy clamps, twice.
- *Root cause.* `listings_ext_price_reset.overwrite` is `[]` although `listings_price` is its declared base ref.
- *Evidence.* Base `listings_price` rule, first sentence: "The host sets what they ask for their own vehicle, within the floor and ceiling of the class the vehicle sits in, and **a price outside that band is refused rather than quietly clamped**." Extended r05: "The figure so taken is finally **brought inside the band, being held to the ceiling** where it stands above it **and lifted to the floor** where it stands below it"; r13/r14: "…**the price is brought to the floor of the band** before the movement rule is applied; …**the price is brought to the ceiling of the band**."
- *Demonstrated consequence.* Bears on **task 0**, where the standing price sits above the band ceiling; demonstrated in `0.md`.
- *Affected artifact and location.* `listings.extended.yaml` → base `policies` → `listings_price` sentence 1; → `extended_policies` → `listings_ext_price_reset` → `overwrite`, `rule` r05/r13/r14.

---

**CG-1d — `SOURCE-POLICY RED` (undeclared override): base reads the price band and the movement limit off the class; `listings_ext_price_reset` reads them off the standing value, a valuation-in-window test, the listing's age and its fault count.**

- *Symptom.* The band and the daily movement limit have two different sources, and the extended selector can drop a class's band entirely.
- *Root cause.* Undeclared: `overwrite: []`.
- *Evidence.* Base `listings_price`: "…within the floor and ceiling of **the class the vehicle sits in**…" and "The daily price may not move by more than **the class's daily movement limit** in one day, and after a change the price is locked for the class's lockout period…". Extended r07–r09 select the band from `governing_value` **and** `valuations_12m >= 1`, so a listing carrying no valuation in the rolling twelve months is read against the entry band (95/22) however high its class — the Luxury, Exotic and Commercial Van bands are named by no tier at all (**dropped branch**). Extended r10–r12 set the movement rate from `listing_age_days` and `faults_12m`, with a top tier of 0.25 which exceeds the class movement limit of 0.20 that `Keyturn Premium Class Listing` and `Keyturn Commercial Van Class Listing` publish, and 0.15 which is below the 0.25 that `Keyturn Economy`/`Standard` publish. Extended's `price_change_lockout_hours` is nowhere carried.
- *Demonstrated consequence.* On **task 0** the two sources happen to agree on the band once the class has been reassigned, and the movement rate taken (0.20) sits inside the class limit (0.25), so no second figure follows on that world; the defect is charter-global and the demonstration in `0.md` records the agreement explicitly rather than claiming a consequence that world does not carry.
- *Affected artifact and location.* `listings.extended.yaml` → base `policies` → `listings_price` sentences 1–2; → `extended_policies` → `listings_ext_price_reset` → `overwrite`, `rule` r07–r12, `params`.

---

**CG-2 — `SOURCE-POLICY RED` (rule/compute equivalence): `listings_ext_price_reset.capped_price` applies the cover share to a different quantity from the one its own `compute_basis` sentence names.**

- *Symptom.* The rule says the share is taken on the price the host is asking; the expression takes it on the boundary-corrected figure. On any world where the boundary correction fires, the rule and the compute give different prices.
- *Root cause.* The rule prose never states the order of the boundary correction relative to the cover share. r02 says the price asked is "**first** taken through the share"; r13/r14 say the correction is applied "**before the movement rule** is applied" — which is silent about the share. The compute picks one order; the rule supports the other.
- *Evidence.* `compute`: `capped_price: RND(boundary_target * cover_share, 2)`. `compute_basis.capped_price` (verbatim): "The price the marketplace starts from is **the price the host is asking for the vehicle at the handling date**, and **that price** is first taken through the share of the band the vehicle's cover standing leaves open to it, the share being applied once and the product rounded half away from zero to two decimal places." `boundary_target` is not "the price the host is asking" whenever tier 1 or tier 2 of `out_of_band_correction_basis` is selected.
- *Demonstrated consequence.* Bears on **task 0**, where `boundary_target` ≠ `price_now`; the two figures are computed in `0.md`.
- *Affected artifact and location.* `listings.extended.yaml` → `extended_policies` → `listings_ext_price_reset` → `rule` r02 and r13–r15, `compute.capped_price`, `compute_basis.capped_price`.

---

**CG-3 — observation (prerequisite sentence scope): the `valuation_assessment ← fault_intake` edge's `condition` is narrower and more specific than the sentence that states it.**

- *Symptom.* The prerequisite sentence says "every fault the vehicle's condition record has been advised of"; the `condition` field says "Every fault the condition record has been advised of, **including any advisory carried on a completed inspection**, stands on that record as a fault report row of its own …".
- *Root cause.* The identification of *where* an un-opened fault lives (the `defect_code` carried on a `listings_inspection_completed` row whose outcome is `passed_with_advisories`) is stated only in `condition`, not in the rule sentence the agent reads.
- *Evidence.* `listings.extended.yaml` → `listings_ext_valuation_assessment` → `rule` r05 vs `prerequisite[0].condition`.
- *Why an observation and not a red light.* The hop is still derivable from the surface: `listings_inspections` carries `defect_code` on inspection rows as well as on fault rows, `log_vehicle_fault_a3e017f7` takes a `source_inspection_id` documented as "the earlier condition record the fault is carried across from", and `find_listings_inspections` returns both. A reader who compares the advisory codes on inspections against the fault reports standing reaches the same conclusion. No second answer is produced, so no consequence can be demonstrated.
- *Affected artifact and location.* as above.

---

**CG-4 — observation (authoring viewpoint in general text): two `prerequisite[].effect` strings assert a particular tier transition rather than the general effect of the write.**

- *Symptom.* `prerequisite` is part of the charter's general text, but two `effect` strings name the tier the binding moves *from*, which is true only of particular worlds.
- *Evidence.* `listings_ext_valuation_assessment.prerequisite[0].effect`: "…the condition holdback binding **takes the pattern rate in place of the single fault rate**" — true only where the fault count moves from one-or-two to three-or-more. `listings_ext_interval_grant.prerequisite[0].effect`: "…the document share binding **takes the current papers share in place of the stale papers share**" — true only where the standing registration verification is more than 365 days old; a listing whose last registration check is 200 days old moves from the *ageing* share instead.
- *Why an observation.* Both assertions happen to hold on the world of the task that uses them (verified in `0.md` and `1.md`), and `effect` is not a scored field, so no second answer follows.
- *Affected artifact and location.* `listings.extended.yaml` → `listings_ext_valuation_assessment.prerequisite[0].effect`; `listings_ext_interval_grant.prerequisite[0].effect`.

---

**CG-5 — `SOURCE-FACTOR RED` (dishonest baseline / fall-through is not the baseline): `listings_ext_interval_grant.paper_currency_share`.**

- *Symptom.* The policy's `baseline.rule` fixes the share of the standard interval at the whole of it; the factor declares its baseline as three quarters, and its fall-through tier is also three quarters. A reader of the computation document and the sensitivity the charter declares cannot both be right.
- *Root cause.* The ladder's fall-through (r08, `stale_papers_share`) was copied into `factors[].baseline` instead of the value the baseline rule states (`current_papers_share`, 1.0).
- *Evidence.* `baseline.rule` (verbatim): "The standard interval is ten thousand miles, and **the whole of it is open** to a vehicle whose own record calls for nothing further." `baseline.params`: `[standard_interval_miles, minimum_interval_miles]` — no share key. `factors[0].baseline`: `document_share: K('stale_papers_share')` = 0.75. Ladder fall-through r08: "and any other vehicle has three quarters of it open."
- *Demonstrated consequence.* Bears on **task 1**, whose `interval_grant` computation sits on tier 1 (`current_papers_share` = 1.0) once the prerequisite is resolved. Substituting the *honest* baseline the rule states leaves the tier's value unchanged, so the factor is decoration on that world; and the whole-baseline fall-back number differs depending on which of the two readings is taken. Both figures are computed in `1.md` § `factor_weight`.
- *Affected artifact and location.* `listings.extended.yaml` → `listings_ext_interval_grant` → `rule` r01 and r06–r08, `baseline.rule`, `baseline.params`, `factors[id=paper_currency_share].baseline`.

---

**CG-6 — `SOURCE-FACTOR RED` (incoherent baseline): `listings_ext_reported_consumption.baseline.params` names a default no sentence of its `baseline.rule` uses.**

- *Symptom.* `baseline.params` lists `reading_variance_tolerance_miles` (75), but the three sentences of `baseline.rule` never mention a tolerance; the 75 miles appear only in tier 2 of the `reported_stretch_basis` ladder (r05).
- *Root cause.* A factor-tier constant was listed among the baseline's defaults.
- *Evidence.* `baseline.rule` (verbatim, all three sentences): "When a host reports the odometer on their own Keyturn Vehicle Listing, the miles that reading takes off the vehicle's inspection interval are worked out before the reading is filed. The reading the host reports is the odometer standing on the listing, and the stretch is measured from the reading the vehicle's most recent telematics odometer record carries to it, a stretch of less than nothing being counted as nothing. The allowances the vehicle's record calls for are summed and taken off the stretch once, a result of less than nothing being counted as nothing, and the miles reported are a whole number of miles." `baseline.params: [reading_variance_tolerance_miles]`. The only rule sentence using it is r05: "…**then reduced by seventy-five miles**, the difference being queried rather than charged."
- *Demonstrated consequence.* Bears on **task 1**; the figure and the second reading it admits are worked out in `1.md` § `factor_weight`.
- *Affected artifact and location.* `listings.extended.yaml` → `listings_ext_reported_consumption` → `baseline.params`, `rule` r05.

---

**CG-OBS-1 — observation.** `listings_ext_class_assignment` r03 states the three adjustments are applied in a named order each to the figure the one before produced, while `compute.adjusted_figure` forms a single product. The readings coincide for every input (associativity, single rounding), so no consequence follows.

**CG-OBS-2 — observation.** `set_daily_price_59fd8a00` and `record_vehicle_inspection_59fe0be1` share the three-character uuid8 prefix `59f` with adjacent fourth characters. The remaining characters are unrelated and no tail is reused; no consequence can be demonstrated.

**CG-OBS-3 — observation.** `record_booked_mileage_82af4bea.source_inspection_id` is documented as "read from **the receipt of the call that filed it** or from the vehicle condition record lookup", which presupposes an earlier call. It names no tool, states no order between problems and refuses nothing.

**CG-OBS-4 — observation.** The `reported_consumption ← booked_consumption` edge's state — "an odometer record dated the handling date stands on the vehicle's condition record" — is brought about by **two** writes of this difficulty: `record_booked_mileage_82af4bea` and the blocked policy's own `report_vehicle_mileage_90a8825c`. The second is excluded by the sentence itself (the reading whose miles are being worked out cannot be the record it waits on), so the hop still resolves in one reading, but the state named is not unique to one write.

**CG-OBS-5 — observation.** Base `listings_evt_defect` b5 ("Putting a fault right is evidenced by a fresh inspection record, not by the host marking it resolved") states a cross-problem order between a fault and an inspection that grounds no declared edge. Neither task's tree rests on it.

**CG-OBS-6 — observation (ladder shape).** `listings_ext_document_verification.registration_lapse_addition` is non-monotone as stated: tier 1 requires "the registration on file **more than seven calendar days past its expiry and the listing suspended**" (4 images) and tier 2 "seven calendar days or fewer past its expiry" (2 images), so a registration twenty days lapsed on a listing that is *not* suspended falls to the fall-through and adds **none** — fewer than the shorter lapse adds. The tiers are disjoint as stated and no task world lands in the gap, so no consequence can be demonstrated.

**CG-OBS-7 — observation (ladder shape).** `listings_ext_reported_consumption.registration_lapse_private_allowance` gives the **larger** private-use allowance (60 miles) to the vehicle whose registration *has* been verified within seven days and the smaller (30) to the one that has not, while both tiers require the registration to be more than seven days past expiry. The reading is defensible (a renewal on file explains the miles driven), and both tiers are conditions a marketplace does weigh, so it is recorded as an observation only.

---

## closing_checklist

Written **after** both reveals, and therefore below the pre-reveal charter-global section, which has not been touched.

**This difficulty does not close.** Step 4's checklist is completed only where all M tasks PASS on all four relationships; both tasks carry a red light.

| item | state |
| --- | --- |
| per-task audit files correspond one-to-one with the tasks, `_difficulty.md` alongside them | ✓ `0.md`, `1.md`, `_difficulty.md` |
| old revisions traceable | ✓ first revision of this difficulty; nothing overwritten |
| every comparison section carries a PASS | **✗** — `0.md`: `SOURCE-POLICY RED`; `1.md`: `SOURCE-POLICY RED` + `SOURCE-FACTOR RED` |
| extended policies fully covered by the M tasks | ✓ 8 of 8: task 0 claims `{fault_intake, valuation_assessment, class_assignment, price_reset}`, task 1 `{document_verification, interval_grant, booked_consumption, reported_consumption}` |
| the M tasks' scopes pairwise disjoint (each spanning root + all prerequisite problems) | ✓ the two chains share no policy and no tool |
| task tools and GT closed | ✓ 8 tools, each claimed by exactly one policy and called by exactly one task; every GT argument traceable to a reachable read, a persona line or a prior call's receipt |
| each task tool uses an independently generated, frozen uuid8 | ✓ with the weak-signal observation **CG-OBS-2** |
| each problem tree: 1–3 prerequisite problems | ✓ 3 and 3 |
| each tree: ≥ `max(n − 1, 1)` `value_input` edges | ✓ 3 of 3 in each, floor 2 |
| each tree: ≥ 1 problem resolved by an `owner="user"` tool | ✓ `set_daily_price_59fd8a00` (task 0), `report_vehicle_mileage_90a8825c` (task 1), each the root |
| no cycle within a tree | ✓ |
| the difficulty's `prerequisite` edges together still a DAG, no cross-task cycle | ✓ two disjoint linear chains, no cross-chain edge |
| every computation declares a self-sufficient baseline | **✗** — `listings_ext_interval_grant` (**CG-5**) and `listings_ext_reported_consumption` (**CG-6**) |
| 4–6 factors, ≥2 `parameter`, ≥1 `method` per computation | ✓ every one (6/6/5/4 and 4/6/5/4) |
| per task ≥1 multi-source and ≥1 cross-difficulty factor | ✓ both tasks; cross-difficulty reads `service`, `roadside`, `hostplan` (task 0) and `service`, `roadside`, `hostplan`, `payouts` (task 1), every row seeded in `initial_state` |
| every ladder ≥3 tiers, stated in full in its rule, tiers distinct in outcome | ✓ all 40 factors |
| every tier's conditions and outcomes ones the line of business actually holds | ✓ with observations **CG-OBS-6** and **CG-OBS-7** |
| every factor proved to bear weight against an honest baseline | **✗** — `paper_currency_share` bears no weight against the baseline `listings_ext_interval_grant.baseline.rule` states (`1.md` **T1-F2**); the other 39 do |
| the baseline alone gives a definite number different from gold | **✗** for `listings_ext_interval_grant` (10 000 from the rule vs 7 500 published) and for `listings_ext_reported_consumption` (770 from the rule vs 695 if its published default is applied); ✓ for the other six |
| instantiation-stage gates re-run on the final form | **not applicable** — there is no final form; the audited artifacts are byte-identical to the entry snapshot (`listings.extended.yaml` sha256:16 `9d07c59a7b520be2`, `task_tools.py` sha256:16 `2a554fe87bc1ac0a`), so the entry gate snapshot supplied with the brief still describes them exactly. No gate was re-run by this auditor, and no artifact was edited. |

### verdicts

| task | policy self-consistency | problem tree holds | factors bear weight | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | **SOURCE-POLICY RED** (T0-F1, T0-F2, T0-F3) | PASS | PASS | FAIL, consequent on the above | **SOURCE-POLICY RED** |
| 1 | **SOURCE-POLICY RED** (T1-F1) | PASS | **SOURCE-FACTOR RED** (T1-F2, T1-F3) | FAIL, consequent on T1-F1 | **SOURCE-POLICY RED + SOURCE-FACTOR RED** |

Both tasks' blind derivations reproduced every scored value and every published `baseline_result` and `factor_sensitivity` figure exactly, with two one-cent exceptions recorded as `0.md` **T0-OBS-2**. The red lights are therefore not arithmetic disagreements and are in no part attributable to a solving agent: they are clauses of the charter that reach different conclusions on the same situation, and baselines the charter contradicts.

---

# revision_2

Round 1 above is preserved verbatim and is not rewritten anywhere below.

## charter_global_frozen (revision 2)

- Freeze time: 2026-09-22 (round 2), written **before any GT field of either task was read in this round**.
- Auditor: same independent source-layer auditor; no answer was accepted on this auditor's behalf, and the reworker's dispositions were treated as claims to be tested, never as evidence.
- Frozen inputs and their hashes (sha256, first 16 hex), re-measured by this auditor:
  - `listings.extended.yaml` — **`b625e5490c3a0812`** (round 1: `9d07c59a7b520be2` — **changed**)
  - `task_tools.py` — **`146cd9d26ad2a36d`** (round 1: `2a554fe87bc1ac0a` — **changed**)
  - masked `0.json` — `2b9a69b6a228b3a8` (**unchanged**); masked `1.json` — `13351c5019d46571` (**unchanged**)
- **Both charter-level hashes moved, so this section is re-derived in full rather than carried forward by reference.** Both masked views are byte-identical to round 1, which is a load-bearing fact used below.
- Fields permitted and fields masked: as in revision 1. `contamination_disclosure`: none — no scored value, gold parameter or intermediate reached this auditor before this freeze; the coordinator's brief relayed dispositions by item id only.

### base_section_identity (revision 2)

Re-checked independently: the base section of `listings.extended.yaml` is key-for-key identical to `blueprint/products/listings.yaml` after YAML load, across all ten keys. **Base was not edited.** Every base sentence quoted in revision 1 therefore still reads exactly as quoted there.

### what moved in the charter

Eight extended policies, same ids, same subjects, same `computes`, same eight target tools, same two chains. The changes this auditor located:

| policy | change |
| --- | --- |
| `listings_ext_price_reset` | `base_policy_refs` gains `listings_evt_valuation`; **three** `overwrite` entries added; r02 split into r02 + r03; three closing sentences r20–r22 added carrying the overwrites' replacements |
| `listings_ext_reported_consumption` | **one** `overwrite` entry added; r04 added carrying its replacement; `baseline.params` emptied; the prerequisite sentence r03 gains "and naming the condition record its reading was taken from" |
| `listings_ext_interval_grant` | the `paper_currency_share` factor **removed and replaced** by `paper_currency_addition`; `params` re-cut; `base_interval` becomes unconditional; r01–r08 and r04 rewritten; the `overwrite`'s `replaced_by` drops its "share" clause; the edge's `gate` moves from `document_share` to `paper_currency_addition` |
| `listings_ext_document_verification` | the `registration_lapse_addition` ladder's tiers 2 and 3 rewritten |
| `listings_ext_valuation_assessment` | the edge's `condition` loses "including any advisory carried on a completed inspection"; the edge's `effect` generalised |
| `listings_ext_interval_grant` (edge) | the edge's `effect` generalised |
| `task_tools.py` | `record_booked_mileage_82af4bea.source_inspection_id` docstring rewritten; everything else, including all eight uuid8 tails, unchanged |
| `listings_ext_fault_intake`, `listings_ext_class_assignment`, `listings_ext_booked_consumption` | no change located |

### policy_conflict_scan (revision 2)

The suite structure is unchanged: two disjoint chains of four, `price_reset → class_assignment → valuation_assessment → fault_intake` and `reported_consumption → booked_consumption → interval_grant → document_verification`, pairwise disjoint and jointly complete over the eight extended policies. `listings_odometer_reported` is still claimed by two policies, still separated by tool, `computes` and actor. Cross-category reads unchanged in category (`service`, `roadside`, `hostplan`, `payouts`).

Re-running the base-against-extended conflict scan sentence by sentence against the **new** `overwrite` sets: **every conflict revision 1 found is now declared, and no new undeclared conflict was found.** Details under `override_declarations (revision 2)`.

### rule_compute_equivalence (revision 2)

Re-run binding by binding over all eight policies. Every `compute` binding still carries a `compute_basis` entry that is a verbatim sentence or contiguous sentence group of that policy's own rule. Two results matter:

- **`listings_ext_price_reset.capped_price` now sweeps back cleanly.** `compute_basis.capped_price` is the *new* r03: "**That carried figure** is then taken through the share of the band the vehicle's cover standing leaves open to it, the share being applied once and the product rounded half away from zero to two decimal places." "That carried figure" refers back to r02 ("The figure the marketplace starts from is the price the host is asking for the vehicle at the handling date, **carried forward as it stands**"), whose variation is r14–r16, which is exactly `boundary_target`. The expression `RND(boundary_target * cover_share, 2)` now implements the sentence that bases it. The word "first", which carried the ambiguity in revision 1, is gone. **CG-2 closed** — see finding **R2-CG-2-CLOSED**.
- **Two new equivalence gaps appear**, both introduced by round-2 edits: **R2-NEW-1** (`listings_ext_document_verification`'s lapse ladder no longer states a tier for a registration 1–7 days past expiry, while `compute` has an else-branch that covers it) and **R2-NEW-2** (`listings_ext_interval_grant`'s rule promises "the share" twice, and the policy no longer defines any share).

### action_binding_and_uuids (revision 2)

Eight tools, eight extended policies, each `(target_tool, computes)` pair claimed by exactly one policy — re-checked and unchanged. Two `owner="user"` tools, one at the head of each chain.

Tool bodies re-read in full: **no function validates a prerequisite.** `log_vehicle_fault`, `record_vehicle_valuation`, `verify_listing_document`, `record_vehicle_inspection`, `record_booked_mileage` and `report_vehicle_mileage` all call `ctx.create(...)` unconditionally; `reassign_value_class` and `set_daily_price` return a row-existence sentence only.

uuid8 tails re-measured: `a3e017f7`, `559b4236`, `4bb6b10c`, `59fd8a00`, `28456ce9`, `59fe0be1`, `82af4bea`, `90a8825c` — **identical to round 1**, consistent with CG-OBS-2 being claimed no-change. The `59f` prefix observation therefore stands unchanged as **CG-OBS-2**.

Docstring silence re-checked. `record_booked_mileage_82af4bea.source_inspection_id` now reads "the reference number of the condition record the reading is taken from; **that reference number is carried on the record itself and is repeated in any receipt that reports it**", replacing round 1's "read from the receipt of **the call that filed it**". The presupposition of an earlier call is gone; the sentence now describes where the reference lives rather than which call produced it. **CG-OBS-3 acted on.**

### prerequisite_graph (revision 2)

| blocked policy | problem | kind | gate | form | resolved_by |
| --- | --- | --- | --- | --- | --- |
| `valuation_assessment` | `fault_intake` | value_input | `condition_holdback` | state | `log_vehicle_fault_a3e017f7` |
| `class_assignment` | `valuation_assessment` | value_input | `marketplace_figure` | state | `record_vehicle_valuation_559b4236` |
| `price_reset` | `class_assignment` | value_input | `band_ceiling` | state | `reassign_value_class_4bb6b10c` |
| `interval_grant` | `document_verification` | value_input | **`paper_currency_addition`** (was `document_share`) | state | `verify_listing_document_28456ce9` |
| `booked_consumption` | `interval_grant` | value_input | `anchor_reading` | state | `record_vehicle_inspection_59fe0be1` |
| `reported_consumption` | `booked_consumption` | value_input | `reported_stretch` | state | `record_booked_mileage_82af4bea` |

`prerequisite` filled everywhere (`[]` on the two leaves), every `problem` an extended policy id in this file, acyclic, every `form` `state` with no `fallback_reason` required or present, every `kind` `value_input` with a `gate` naming a binding that exists in the blocked policy's `compute` — `paper_currency_addition` is present in the reworked `listings_ext_interval_grant.compute` ✓. Every `resolved_by` is the depended-on policy's `target_tool`.

**Both `effect` strings revision 1 flagged are now general.** The valuation edge now reads "…the count of fault reports in the rolling twelve months **rises by that report** and the condition holdback binding **is read on the higher count**" (round 1: "takes the pattern rate in place of the single fault rate"). The interval edge now reads "…the paper currency addition binding **is read on that verification rather than on an older one**, and the standard interval is adjusted by **what that verification's own record carries**" (round 1: "takes the current papers share in place of the stale papers share"). Neither names a tier the world must be on. **CG-4 closed.**

### prerequisite_sentences (revision 2)

All six `policy_source` strings re-located verbatim in the blocked policy's own rule. Five are unchanged from round 1 and pass the four-point test as recorded there. The sixth changed:

**`reported_consumption ← booked_consumption`**, new r03: "The miles a reading the host reports take off the interval are not counted before an odometer record dated the handling date **and naming the condition record its reading was taken from** stands on the vehicle's condition record." Connective "not … before" ✓; state form, record-visible, no performer, no tool, no snake_case ✓. The added clause resolves round 1's **CG-OBS-4**: of the two writes of this difficulty that create a `listings_odometer_reported` row dated the handling date, only `record_booked_mileage_82af4bea` writes `source_inspection_id` (`ctx.create(..., source_inspection_id=source_inspection_id, ...)`); `report_vehicle_mileage_90a8825c` does not pass the field at all. **Exactly one write now brings the waited-on state about. CG-OBS-4 closed.**

**CG-3 closed.** The `valuation_assessment ← fault_intake` edge's `condition` is now "Every fault the condition record has been advised of stands on that record as a fault report row of its own at the moment the valuation is worked out" — the round-1 addition "including any advisory carried on a completed inspection" is gone, so the `condition` now carries exactly the strength and scope of the sentence, no wider and no narrower. The hop remains derivable from the surface by the route revision 1 recorded (the `defect_code` carried on a `passed_with_advisories` inspection row, and `log_vehicle_fault_a3e017f7`'s `source_inspection_id`).

`listings_evt_defect` b5 is unchanged in the base and still grounds no declared edge; **CG-OBS-5** stands as an observation.

### override_declarations (revision 2)

Sentence-by-sentence re-sweep against each `base_policy_refs` entry, against the new `overwrite` sets.

**Now declared, each quoting the base sentence verbatim** (each quotation was checked character-for-character against `blueprint/products/listings.yaml`):

| finding | base policy | superseded clause | declared in |
| --- | --- | --- | --- |
| CG-1c | `listings_price` | "The host sets what they ask for their own vehicle, within the floor and ceiling of the class the vehicle sits in, and a price outside that band is refused rather than quietly clamped." | `listings_ext_price_reset.overwrite[0]` |
| CG-1d | `listings_price` | "The daily price may not move by more than the class's daily movement limit in one day, and after a change the price is locked for the class's lockout period in whole elapsed hours, so that a vehicle's price cannot be moved around a booking in progress." | `listings_ext_price_reset.overwrite[1]` |
| CG-1a | `listings_evt_valuation` | "A class change moves the price floor and ceiling with it, and a daily price outside the new class's band is brought to the nearer boundary rather than left outside it." | `listings_ext_price_reset.overwrite[2]` |
| CG-1b | `listings_evt_inspection` | "A telematics reading is authoritative where one exists; a host reading standing more than the class's variance tolerance away from the telematics figure is queried rather than recorded, and the listing is not suspended while the query is open." | `listings_ext_reported_consumption.overwrite[0]` |

**Each `replaced_by` is carried as a sentence of the extended policy's own rule**, so the merged semantics are stated where a reader meets them and not only in a metadata field: `price_reset` r20, r21, r22 and `reported_consumption` r04 reproduce the three and one `replaced_by` strings respectively. `listings_ext_price_reset.base_policy_refs` was widened to `["listings_price", "listings_evt_valuation"]` so the `listings_evt_valuation` overwrite sits on a declared base ref ✓.

**Replaced rather than deleted** — checked on each:

- CG-1c: base refused an out-of-band price; the replacement states the band is settled from the standing value and "a price standing outside that band is **brought inside it** rather than refused". A treatment is named for the case base covered. ✓
- CG-1d: base capped movement by the class's limit and imposed a lockout; the replacement states the cap is settled from listing age and fault record, "and **no lockout period runs** against the listing after a price is changed". The cap survives in another form; the lockout is **dropped**, and the replacement says so outright rather than falling silent. That is a declared change of treatment, not a deletion by omission — but base's stated purpose ("so that a vehicle's price cannot be moved around a booking in progress") is now met by nothing in the charter. Recorded as **R2-OBS-1**.
- CG-1a: base brought an out-of-band price to the nearer boundary and left it there; the replacement states it "is carried forward, taken through the share of the band the vehicle's cover standing leaves open, held to the movement the day allows, and only then brought inside the band" — which is exactly the r02→r03→r05→r06 pipeline. ✓
- CG-1b: base held a divergent host reading back; the replacement states the reading "is recorded … whatever distance stands between it and the reading the most recent telematics odometer record carries, and that distance is **settled by the way the stretch is measured** rather than by holding the reading back". The treatment base gave the divergence survives — r06 still reduces the stretch by the seventy-five-mile tolerance and still says "the difference being **queried rather than charged**" — and base's "a telematics reading is authoritative" survives in substance as the fall-through anchor of r07 and of the policy's baseline. **Replaced, not deleted.** ✓

**No new undeclared override was found.** The two declared overwrites carried over from round 1 (`class_assignment` on `listings_evt_valuation` b3, `interval_grant` on `listings_evt_inspection` b1) still quote their base sentences verbatim; `interval_grant`'s `replaced_by` was rewritten to drop its "share" clause, and the rewritten text is still a faithful statement of what the reworked policy does.

### factor_ladders (revision 2)

| policy | factors | parameter | method | multi-source tiers | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| `fault_intake` | 6 | 5 | 1 | yes | service |
| `valuation_assessment` | 6 | 4 | 2 | yes | hostplan, service |
| `class_assignment` | 5 | 3 | 2 | yes | service, roadside, hostplan |
| `price_reset` | 4 | 3 | 1 | yes | hostplan |
| `document_verification` | 4 | 3 | 1 | yes | none |
| `interval_grant` | 6 | 5 | 1 | yes (`fault_standing_basis`) | service, roadside |
| `booked_consumption` | 5 | 4 | 1 | yes | service, roadside, hostplan |
| `reported_consumption` | 4 | 3 | 1 | yes | payouts |

Bounds all hold (4–6 factors, ≥2 `parameter`, ≥1 `method` per computation). Every ladder has three tiers, pairwise disjoint as stated, no two tiers of any ladder selecting the same value or method, every tier drawn from the charter's own `params` or from a named record.

**Baseline coherence, re-derived per policy:**

| policy | `baseline.rule` self-sufficient | sentences in `rule` | defaults match `baseline.params` | every fall-through = baseline |
| --- | --- | --- | --- | --- |
| `fault_intake` | yes (4, floor 3) | yes | yes | yes |
| `valuation_assessment` | yes (0.006, anchor = last valuation) | yes | yes | yes |
| `class_assignment` | yes | yes | yes (`[]`) | yes |
| `price_reset` | yes (entry band, 0.15, share 1, carried figure = price asked) | yes — including both halves of the split r02/r03 | yes | yes |
| `document_verification` | yes (3, cap 16) | yes | yes | yes |
| `interval_grant` | **yes — 10 000 with nothing added, floor 1 000** | yes | **yes** | **yes** |
| `booked_consumption` | yes | yes | yes (`[]`) | yes |
| `reported_consumption` | yes | yes | **yes (`[]`)** | yes |

The two round-1 failures are both repaired:

- **CG-5 closed.** `listings_ext_interval_grant.base_interval` is now `K('standard_interval_miles')` unconditionally — no share multiplies it — and the replacement factor `paper_currency_addition` is an *addition* whose fall-through and whose declared `baseline` are both `K('no_papers_addition')` = 0. `baseline.rule` still says "The standard interval is ten thousand miles, and the whole of it is open to a vehicle whose own record calls for nothing further", which with no addition gives 10 000: **the declared baseline and the baseline the rule states now agree.** Whether the rebuilt factor bears weight is a fact about one world and is demonstrated in `1.md` § revision_2 `factor_weight`.
- **CG-6 closed.** `listings_ext_reported_consumption.baseline.params` is now `[]`, and its three `baseline.rule` sentences name no constant. `reading_variance_tolerance_miles` remains in the policy's `params`, where the ladder's r06 uses it, and no longer appears among the baseline's defaults.

**CG-OBS-6 acted on, with a new gap.** `listings_ext_document_verification.registration_lapse_addition` was non-monotone in round 1. Its tiers now read: more than seven days past expiry **and** the listing suspended → 4; more than seven days past expiry **and** the listing not suspended → 2; "a vehicle whose registration on file **is not past its expiry**" → none. The non-monotonicity is gone. But see **R2-NEW-1**: a registration one to seven days past expiry now matches no tier the rule states.

### findings (revision 2)

**R2-CG-1a/1c/1d/1b-CLOSED — the four undeclared overrides are genuinely declared.** Each `overwrite` entry names its base policy, quotes the base sentence verbatim (checked character-for-character against the untouched `blueprint/products/listings.yaml`), and its `replaced_by` is carried as a sentence of the extended policy's own rule so a reader meets the replacement where the conflict arises. Each replacement states a treatment for the situation base covered rather than deleting one. The per-task demonstrations that the second answers are gone are in `0.md` and `1.md` under revision_2.

**R2-CG-2-CLOSED — the rule/compute split is genuine.** Round 1's single sentence carried two quantities and one ambiguous "first". It is now two sentences: r02 fixes the *carried figure* (whose variation is the `out_of_band_correction_basis` ladder, r14–r16), and r03 applies the cover share to "that carried figure". `compute_basis.capped_price` cites r03 and `compute_basis.boundary_target` cites r14–r16; `capped_price: RND(boundary_target * cover_share, 2)` implements exactly what r03 says of exactly what r02/r14–r16 define. No second reading of the order survives.

**R2-CG-5-CLOSED, R2-CG-6-CLOSED, R2-CG-3-CLOSED, R2-CG-4-CLOSED, R2-CG-OBS-3-CLOSED, R2-CG-OBS-4-CLOSED** — as set out in the sections above.

---

**R2-NEW-1 — observation (new, introduced by the CG-OBS-6 fix). `listings_ext_document_verification`'s lapse ladder states no tier for a registration one to seven days past expiry.**

- *Symptom.* The rule's three tiers are "more than seven calendar days past its expiry and the listing suspended", "more than seven calendar days past its expiry and the listing not suspended", and "a vehicle whose registration on file **is not past its expiry**". A registration three days past expiry is past its expiry and is not more than seven days past it, so it matches none of the three as the rule states them.
- *Root cause.* Round 1's tier 2 was "seven calendar days or fewer past its expiry", which covered that band. Fixing the non-monotonicity re-cut tier 2 on the suspension flag and re-cut tier 3 on "not past its expiry", and the one-to-seven-day band fell out of the stated ladder.
- *Evidence.* `rule` r13–r15 and `factors[id=registration_lapse_addition].ladder` (whose third tier says only "otherwise") against `compute.lapse_addition`: `K('long_lapse_addition') if (registration_lapse_days > 7 and listing_state == 'suspended') else (K('short_lapse_addition') if (registration_lapse_days > 7 and listing_state != 'suspended') else K('no_lapse_addition'))`. The `else` covers the one-to-seven-day band; r15 does not.
- *Why an observation and not a red light.* Neither task's world lands in the gap — task 1's vehicle is 24 days past expiry (`registration_expiry_date` 2026-02-28 against `frozen_time` 2026-03-24) and takes tier 1, and `document_verification` is out of task 0's scope. No consequence can be demonstrated against either scored solution.
- *Affected artifact and location.* `listings.extended.yaml` → `listings_ext_document_verification` → `rule` r15, `factors[id=registration_lapse_addition].ladder[2]`, `compute.lapse_addition`, `compute_basis.lapse_addition`.

---

**R2-NEW-2 — observation (new, introduced by the CG-5 fix). `listings_ext_interval_grant`'s rule promises "the share" twice, and the policy defines no share.**

- *Symptom.* r21 and r23 read "half of what **the share** and the adjustments give" and "the interval taken as **the share** and the adjustments give it". The rebuilt policy has no share: `base_interval` is `K('standard_interval_miles')` and `adjusted_interval` is `base_interval + paper_currency_addition - overrun_reduction + service_addition - mileage_reduction - recovery_reduction`. The same dangling phrase is carried into `factors[id=fault_standing_basis].ladder` in all three tiers and into `compute_basis.granted_interval`.
- *Root cause.* The `paper_currency_share` factor was replaced by an addition and r04 was rewritten to "summed and applied once to the standard interval", but the downstream sentences that referred back to the share were not re-cut with it.
- *Evidence.* `rule` r04 ("The additions and reductions the vehicle's record calls for are summed and applied once to **the standard interval**") against r21/r23; `compute.adjusted_interval`; `compute.granted_interval`. The word "share" appears twice in the rule with no antecedent anywhere in the policy.
- *Why an observation and not a red light.* "What the share and the adjustments give" reads naturally as "what the preceding steps give", which is `adjusted_interval`, and no alternative referent exists in the policy to produce a second number. This is an empty promise in the rule rather than a second answer, so no consequence can be demonstrated.
- *Affected artifact and location.* `listings.extended.yaml` → `listings_ext_interval_grant` → `rule` r21, r23; `factors[id=fault_standing_basis].ladder`; `compute_basis.granted_interval`.

---

**R2-NEW-3 — observation (new). `listings_ext_interval_grant.inputs.history` does not declare the `photo_count` read the rebuilt factor makes.**

`compute.latest_registration_images` is `LATEST('listings_inspections', 'photo_count', date_field='record_date', event_type='listings_document_verified', document_kind='registration')`, but `inputs.history` declares only the `latest record_date` read on that same filter, with no entry for the `photo_count` aggregate. Round 1's `listings_ext_document_verification.inputs` did declare its `latest photo_count` read, so the convention exists in the charter. No consequence follows for either scored value — the binding is computed from a reachable field either way (`find_listings_inspections` returns `photo_count`) — so this is recorded as an observation.

---

**R2-NEW-4 — observation (new, and the most serious of the four). The rebuilt `paper_currency_addition` sets a safety-inspection mileage interval from how many images of a registration certificate the desk filed minutes earlier.**

- *Symptom.* The ladder that decides how many miles a vehicle may run before its next marketplace inspection now turns, above the thirty-day currency test, on a count of photographs: "on a record carrying **twelve or more images** of it has one thousand five hundred miles added; … on a record carrying **fewer than twelve images** has seven hundred and fifty miles added".
- *Why this is worth recording.* The quantity being settled is a safety-inspection interval. What a peer-to-peer marketplace actually weighs for it — and what the other five factors of this very policy weigh — is the vehicle: its overrun standing, its service history, its odometer band, its recovery callouts, its fault reports. The number of images held of a registration certificate is not a fact about the vehicle at all; on this charter it is a figure the marketplace's **own** rule computes, in the **same** consultation, minutes before, and whose value the desk lands as an argument. The interval therefore moves with the desk's own paperwork rather than with the car.
- *Why an observation and not a red light.* Two reasons, both honest. First, a defensible business reading exists: a complete documentation pack can stand as a proxy for a well-kept vehicle, and a marketplace that trusts its documentation may extend the interval on it. Second — and decisively for consistency — the thirty-day half of the condition is guaranteed true by this policy's own prerequisite, so the fall-through is unreachable once the chain runs; but that same shape is carried by `listings_ext_reported_consumption.inspection_transit_allowance_step` and by `reported_stretch_basis`, which this auditor examined and **passed in revision 1**. Red-lighting it now would be a ruling this auditor did not apply to the identical shape a round earlier, and an old blind ruling is not rewritten to accommodate a new artifact. The concern is recorded in full here so the coordinator can weigh escalating it; this auditor does not escalate it on its own motion.
- *Affected artifact and location.* `listings.extended.yaml` → `listings_ext_interval_grant` → `rule` r06–r08, `params.documented_papers_addition`/`current_papers_addition`, `factors[id=paper_currency_addition]`, `compute.latest_registration_images`/`paper_currency_addition`.

---

**R2-OBS-1 — observation. The CG-1d overwrite drops the price lockout and replaces its purpose with nothing.**

`listings_ext_price_reset.overwrite[1]` supersedes base's "…after a change the price is locked for the class's lockout period in whole elapsed hours, **so that a vehicle's price cannot be moved around a booking in progress**" with "…and **no lockout period runs** against the listing after a price is changed". The movement cap survives in another form; the lockout does not, and the purpose base gave it is now served by nothing in the charter. The change is stated outright rather than left silent, which is what a declaration is for, so this is an observation on the treatment chosen and not an undeclared override. Base `listings_price` sentence 3 ("A price change never touches a booking already confirmed, since every booking carries the price locked in at its own confirmation…") is untouched and still protects the confirmed booking itself.

---

**CG-OBS-1, CG-OBS-2, CG-OBS-5, CG-OBS-7 — re-checked, unchanged, and still standing as observations.** `listings_ext_class_assignment` r03 still states the three adjustments sequentially while `compute` forms one product (readings coincide); the `59f` uuid8 prefix pair is unchanged; base `listings_evt_defect` b5 still states a cross-problem order grounding no declared edge, in an untouched base; and `registration_lapse_private_allowance` still gives the larger allowance to the host whose registration has been re-verified.

## closing_checklist (revision 2)

Written **after** both round-2 reveals. Revision 1's closing checklist is preserved above and is not rewritten; it recorded that the difficulty did not close, which was correct for the artifacts of that round.

**This difficulty now closes.**

| item | state |
| --- | --- |
| per-task audit files correspond one-to-one with the tasks, `_difficulty.md` alongside them | ✓ |
| old revisions traceable | ✓ revision 1 preserved verbatim in all three files; revision 2 appended below it |
| every comparison section carries a PASS | ✓ `0.md` revision 2: PASS; `1.md` revision 2: PASS |
| extended policies fully covered, scopes pairwise disjoint | ✓ 8 of 8, two disjoint chains of four |
| task tools and GT closed; each tool an independently generated, frozen uuid8 | ✓ 8 tools, tails unchanged from round 1, with observation **CG-OBS-2** |
| each tree: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner="user"` write, no cycle | ✓ 3 / 3 / root is the user write / acyclic, both tasks |
| difficulty-wide `prerequisite` graph still a DAG | ✓ two disjoint linear chains |
| every computation declares a self-sufficient baseline | ✓ **all eight**, where revision 1 had two failures (CG-5, CG-6) |
| 4–6 factors, ≥2 `parameter`, ≥1 `method` per computation | ✓ |
| per task ≥1 multi-source and ≥1 cross-difficulty factor, rows seeded | ✓ both tasks |
| every ladder ≥3 tiers stated in full, tiers distinct in outcome | ✓ with observation **R2-NEW-1** on one ladder's stated coverage |
| every factor bears weight against an honest baseline, baseline alone giving a definite number different from gold | ✓ **all 40**, where revision 1 had one failure (`paper_currency_share`) |
| instantiation-stage gates re-run on the final form | ✓ by the coordinator, read-only, all seven green on the reworked artifacts (`listings.extended.yaml` `b625e5490c3a0812`, `task_tools.py` `146cd9d26ad2a36d`); this auditor cites that snapshot and ran no gate itself |
| base section unedited | ✓ re-verified key-for-key against `blueprint/products/listings.yaml` |

### verdicts (revision 2)

| task | policy self-consistency | problem tree holds | factors bear weight | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | **PASS** |
| 1 | PASS | PASS | PASS | PASS | **PASS** |

### disposition of every round-1 item

| item | reworker's claim | this auditor's finding |
| --- | --- | --- |
| T0-F1 / CG-1a | closed by a declared overwrite | **CLOSED** — base sentence quoted verbatim in `price_reset.overwrite[2]`, replacement carried as rule r22, 165.00 reading excluded in terms on task 0's world |
| T0-F2 / CG-2 | closed by splitting the sentence | **CLOSED** — r02/r03 split, `compute_basis.capped_price` cites r03, "first" removed; the 162.00 reading has no sentence left |
| T0-F3 / CG-1c | closed by a declared overwrite | **CLOSED** — `overwrite[0]` + rule r20; the "refuse, write nothing" terminal state excluded |
| CG-1d | closed by two overwrite entries | **CLOSED** — `overwrite[0]` and `overwrite[1]`, `base_policy_refs` widened; one observation on the dropped lockout (**R2-OBS-1**) |
| T1-F1 / CG-1b | closed by a declared overwrite; errand and value survive | **CLOSED, and both assertions verified** — errand unchanged and still the hinge of the computation; the overwrite **replaced** rather than deleted (the query treatment survives in r06, telematics authority in r07 and the baseline); scored value 40 unmoved |
| T1-F2 / CG-5 | closed by rebuilding the factor; moved a scored value; re-minted a row id | **CLOSED, verified on all three tests** — baseline is now the fall-through **and** what `baseline.rule` states, and it bears weight (5 600 against a gold of 6 700). The moved value is `interval_miles_granted` 5 600 → 6 700, and its only downstream reader (`granted_interval_standing` against the 5 000 line) still holds. The re-minted id is a **tool-minted GT id**, not a seeded row (**R2-T1-OBS-1**) |
| T1-F3 / CG-6 | closed by emptying baseline params | **CLOSED** — `baseline.params` `[]`, no constant in `baseline.rule`, the 695 third number gone |
| CG-3 | acted on | **CLOSED** — the edge's `condition` no longer over-specifies; the hop still resolves in one reading from the surface |
| CG-4 | acted on | **CLOSED** — both `effect` strings now general, neither naming a tier the world must be on |
| CG-OBS-3 | acted on | **CLOSED** — the docstring no longer presupposes an earlier call |
| CG-OBS-4 | acted on | **CLOSED** — the prerequisite sentence now requires the record to name its source, which only `record_booked_mileage_82af4bea` writes |
| CG-OBS-6 | acted on | **ACTED ON** — the non-monotonicity is gone, but the fix left a stated-coverage gap (**R2-NEW-1**, observation) |
| CG-OBS-1, CG-OBS-2, CG-OBS-5, CG-OBS-7 / T1-OBS-4, T0-OBS-1 / T1-OBS-1, T0-OBS-3, T0-OBS-4, T1-OBS-3, T0-OBS-2, T1-OBS-2 | no change | **confirmed unchanged**; each re-checked this round and still standing as an observation, none of them grounds for rework |

### new items found this round

All four are observations; none is grounds for rework, and none changes a scored value.

| id | where | one line |
| --- | --- | --- |
| **R2-NEW-1** | `document_verification` lapse ladder | no tier stated for a registration 1–7 days past expiry, while `compute` has an else-branch covering it |
| **R2-NEW-2** | `interval_grant` r21/r23 | the rule promises "the share" twice and the rebuilt policy defines no share |
| **R2-NEW-3** | `interval_grant.inputs.history` | the `photo_count` read the rebuilt factor makes is not declared |
| **R2-NEW-4** | `interval_grant.paper_currency_addition` | a safety-inspection mileage interval is decided from how many images of a registration the desk filed minutes earlier; recorded with the reasoning on both sides and deliberately **not** escalated to a red light, because a defensible business reading exists and because red-lighting it would apply a test this auditor did not apply to the identical shape in revision 1 |
| **R2-OBS-1** | `price_reset.overwrite[1]` | the declared replacement drops the price lockout and leaves base's stated purpose for it served by nothing |
| **R2-T1-OBS-1** | the rework's own account | a re-minted **tool-minted** id was described as a re-minted **seeded** row id; the artifacts are correct, the description was not |

Both blind derivations of this round reproduced every scored value, every published `baseline_result` and every `factor_sensitivity` figure exactly — including the one quantity that moved, 6 700, and the two one-cent rounding figures of **T0-OBS-2**, which are unchanged and remain observations.

---

# revision_3

Revisions 1 and 2 above are preserved verbatim and are not rewritten anywhere below.

## charter_global_frozen (revision 3)

- Freeze time: 2026-09-22 (round 3), written **before any GT field of either task was read in this round**.
- Frozen inputs, re-measured by this auditor: `listings.extended.yaml` **`575c7743f1506770`** (round 2: `b625e5490c3a0812` — changed); `task_tools.py` **`146cd9d26ad2a36d`** (**unchanged** from round 2); masked `0.json` `2b9a69b6a228b3a8` (**unchanged**); masked `1.json` **`4cd2161d7939376e`** (round 2: `13351c5019d46571` — changed).
- The extended charter moved, so this section is **re-derived in full**. `task_tools.py` did not move, so the tool-contract and uuid8 conclusions of revision 2 hold on identical inputs and are re-stated only where this round's changes touch them.
- `contamination_disclosure`: none. The coordinator relayed the render auditor's finding and the reworker's claims **by item id and shape only**; no scored value, gold parameter or intermediate was supplied. The render-layer audit's own files were not read.
- **Context accepted as given, not as evidence:** the KB was rendered and a separate render-layer auditor passed task 0 and failed task 1. That judgement is not this auditor's and is not relied on; the finding traced to the source is re-tested here from the source alone.

### base_section_identity (revision 3)

Re-verified independently: all ten keys of the base section load key-for-key identical to `blueprint/products/listings.yaml`. **Base was not edited.** Every base sentence quoted in revisions 1 and 2 still reads as quoted.

### what moved in the charter

| policy | change located |
| --- | --- |
| `fault_intake` | rule gains r23, an argument-deciding sentence for the fault carried across from a standing record |
| `valuation_assessment` | rule gains r24, an argument-deciding sentence for the valuation's channel and odometer |
| `document_verification` | rule gains r16, the channel sentence; r15's fall-through re-worded from "a vehicle whose registration on file is not past its expiry" to "**any other vehicle**" |
| `interval_grant` | rule gains r24, an argument-deciding sentence for the inspection's odometer, finding and channel; r21/r23 "the share and the adjustments" → "**the additions and reductions**" |
| `booked_consumption` | rule gains r04, an argument-deciding sentence for the booked reading's channel; "the stretch" → "**the booked stretch**" throughout rule and baseline; each allowance now says "against the booked stretch" |
| `reported_consumption` | "the stretch" → "**the reported stretch**" throughout rule, baseline and `overwrite.replaced_by`; each allowance now says "against the reported stretch"; `params.reading_variance_tolerance_miles` renamed **`queried_reading_margin_miles`**, same value 75; r06 re-worded to "cut back by the seventy-five mile margin the marketplace queries rather than charges" |
| `class_assignment`, `price_reset` | no change located |
| `task_tools.py` | unchanged (hash identical) |

**No `compute` binding changed anywhere** except the renamed `K('queried_reading_margin_miles')` reference in `reported_consumption.reported_stretch`, which is the same constant under a new key. **No scored value can therefore move**, which is what this auditor's own recomputation finds (`0.md` and `1.md`, revision 3).

### the returned finding — a scored argument no rule decides

The render auditor's finding was `verify_listing_document_28456ce9.inspection_channel`: scored, but settled by nothing in the policy, recoverable only by copying an earlier verification record's channel, while the persona pointed the other way. Revision 1 raised the same shape as an observation (**T1-OBS-1**, and **T0-OBS-1** for its twin), and revision 2 left it there. **Revision 1's ruling was wrong to stop at an observation**, and this auditor records that plainly rather than re-reading its old answer: the skill's own unique-solution row requires the policy to entail "the object, **the parameters**, the owner, the order and the terminal state", so an argument the policy does not decide is a uniqueness failure whether or not a residual-exclusion argument can be built for it. Reading the documents alone is what made it unmissable; the standard it failed was already this auditor's.

**The new sentence, `listings_ext_document_verification` r16, verbatim:** "A document is checked by the marketplace's own inspector against the vehicle rather than on the host's word, and the verification is recorded under that channel whoever sent the document in."

- *Does it decide the value?* Yes, and by naming rather than by pointing at a record. The tool schema glosses `mobile_inspector` as "a marketplace inspector checked the document against the vehicle"; r16 says "checked by the marketplace's own inspector against the vehicle". The other three enum values are excluded on the face of the sentence: `self_photo` ("the host supplied photographs of the document themselves") by "rather than on the host's word … **whoever sent the document in**"; `partner_shop` and `telematics_report` because neither is the marketplace's own inspector. **The value is now read off a rule, not copied off a record** — which is the difference that matters, since copying a record is exactly what the render auditor found.
- *Does it fit the persona, which now also moved?* The persona line changed from "sent the certificate through the app the same week" to "sent the certificate in through the app the same week **for Keyturn to check, which he assumes it has**". The host's act is now unambiguously *submission*, not *checking*. The clause "whoever sent the document in" in r16 and the persona's "for Keyturn to check" meet exactly. **The pointer that pointed at the wrong value is gone.**
- *Does it invent a procedure?* No. It adds no step, no confirmation and no wait; it states who performs a check base already assigns to the marketplace.

### the no-`overwrite` claim — judged

**The claim holds. No `overwrite` is owed.** The test is whether extended reaches a *different conclusion from base on the same subject*, not whether extended says something base did not.

- Base `listings_evt_documents` sentence 1, verbatim: "A listing depends on documents that expire, and **each one is verified by the marketplace rather than accepted on the host's word**." r16 restates that proposition — "checked by the marketplace's own inspector … rather than on the host's word" — and then adds which marketplace channel records it. Base names **no** channel, so there is no base conclusion for r16 to contradict. This is a refinement of an inherited provision, not a replacement of one, and inherited provisions may be refined without being weakened.
- Checked against every other base sentence that could bear on a channel, not only the one the reworker names: `listings_evt_documents` sentences 2–6 govern notice, verification period, failed verification, lender-consent matching and out-of-state refusal, and none names a performer. `listings_evt_inspection` sentence 4 names "a telematics reading" but governs odometer readings, not document checks, and is in any case superseded by `reported_consumption.overwrite[0]`.
- Checked against the **class parameters**, which is where a channel restriction would live if one existed: `inspection_channel_allowed` for `Keyturn Commercial Van Class Listing` is `[partner_shop, mobile_inspector]`. The channel r16 names is **inside** that list, so r16 neither exceeds nor narrows a class restriction. Had r16 named `self_photo` or `telematics_report` for this class it would have conflicted with a base parameter and owed a declaration; it does not.

**Judgement: no `overwrite` owed, and the sentence does not weaken base.** Recorded as **R3-CLOSED-1**.

### the sweep of scored arguments — verified against this auditor's own oracle

The reworker reports covering all 38 scored arguments. This auditor enumerated them **independently, from `task_tools.py` alone**, before reading any GT: the eight task tools' parameters excluding `ctx` number 6 + 6 + 3 + 2 = **17** for task 0 and 5 + 6 + 6 + 4 = **21** for task 1, **38 in all**. The count is right.

Each was then asked the only question that matters — *what sentence, record or persona line fixes this value, and is a second value defensible?* The result, derived before any reveal:

| # | write.argument | what decides it | new this round? |
| --- | --- | --- | --- |
| 1–2 | `log_vehicle_fault`.{vehicle_id, customer_id} | the object of the call; one listing, one host | no |
| 3 | `log_vehicle_fault.source_inspection_id` | `valuation_assessment` r05 + `fault_intake` **r23** ("a fault carried across from a condition record already standing") | **yes** |
| 4 | `log_vehicle_fault.defect_code` | **r23** "recorded under the fault that record names" | **yes** |
| 5 | `log_vehicle_fault.inspection_channel` | **r23** "through the channel that record was produced under" | **yes** |
| 6 | `log_vehicle_fault.attached_photo_count` | the computation | no |
| 7–8 | `record_vehicle_valuation`.{vehicle_id, customer_id} | the object | no |
| 9 | `record_vehicle_valuation.odometer_reading` | **r24** "made on the odometer standing on the listing at the handling date" | **yes** |
| 10 | `record_vehicle_valuation.assessed_value_amount` | the computation | no |
| 11 | `record_vehicle_valuation.value_class_assessed` | the class whose `min/max_market_value_amount` band the figure falls in | no |
| 12 | `record_vehicle_valuation.inspection_channel` | **r24** "is its own inspector's assessment of the vehicle, is recorded under that channel" | **yes** |
| 13 | `reassign_value_class.vehicle_id` | the object | no |
| 14 | `reassign_value_class.value_class_name` | `class_assignment` r00, the band the governing value falls in | no |
| 15 | `reassign_value_class.governing_value_amount` | the computation | no |
| 16–17 | `set_daily_price`.{vehicle_id, daily_price_amount} | the object; the computation | no |
| 18–19 | `verify_listing_document`.{vehicle_id, customer_id} | the object | no |
| 20 | `verify_listing_document.document_kind` | the listing's `suspension_reason`/`registration_expiry_date`, the review case's `review_reason`, and the persona | no |
| 21 | `verify_listing_document.inspection_channel` | **r16** — *the returned finding* | **yes** |
| 22 | `verify_listing_document.verification_image_count` | the computation | no |
| 23–24 | `record_vehicle_inspection`.{vehicle_id, customer_id} | the object | no |
| 25 | `record_vehicle_inspection.odometer_reading` | **r24** "filed at the odometer the record of the inspection carries" | **yes** |
| 26 | `record_vehicle_inspection.inspection_outcome` | **r24** "with the finding that record reached" | **yes** |
| 27 | `record_vehicle_inspection.inspection_channel` | **r24** "through the channel the inspection was carried out under" | **yes** |
| 28 | `record_vehicle_inspection.interval_miles_granted` | the computation | no |
| 29–30 | `record_booked_mileage`.{vehicle_id, customer_id} | the object | no |
| 31 | `record_booked_mileage.source_inspection_id` | `booked_consumption` r01 + `reported_consumption` r03's "naming the condition record its reading was taken from" | no (r03 added round 2) |
| 32 | `record_booked_mileage.odometer_reading` | `booked_consumption` r01, "the reading the vehicle's most recent completed inspection carries" | no |
| 33 | `record_booked_mileage.inspection_channel` | **r04** "recorded through the channel the completed inspection it is taken from was carried out under" | **yes** |
| 34 | `record_booked_mileage.booked_miles_consumed` | the computation | no |
| 35–36 | `report_vehicle_mileage`.{vehicle_id, customer_id} | the object | no |
| 37 | `report_vehicle_mileage.odometer_reading` | `reported_consumption` r01 "the odometer standing on the listing", and the persona states the figure | no |
| 38 | `report_vehicle_mileage.reported_miles_consumed` | the computation | no |

**All 38 are now decided.** Ten were given a deciding sentence this round — the returned one (#21) plus **nine** others (#3, #4, #5, #9, #12, #25, #26, #27, #33), which matches the reworker's "three further groups, nine arguments" exactly, group for group: the fault-intake group of three, the valuation group of two, and the inspection-and-booking group of four.

**One arithmetic discrepancy to flag.** The reworker reports "**25** were already decided". This auditor counts **28** already decided (38 − 10). The enumeration above is the working; if the reworker's 25 excludes the three arguments this auditor judges decided by records and persona rather than by a rule sentence (#20 `document_kind`, #31 `source_inspection_id`, #37 the host's `odometer_reading`), the two counts reconcile at 25 + 3 + 10 = 38. Either way no argument is left undecided, so the discrepancy is in the bookkeeping, not in the coverage. Recorded as **R3-OBS-1**, to be settled against `argument_uniqueness_tracing` in the per-task comparisons.

**A caveat on one of the nine** — see **R3-NEW-1** below: #25, #26 and #27 are decided by a sentence whose referent lies in another category, and that category's read is not declared.

### rule_compute_equivalence (revision 3)

Re-run binding by binding over all eight policies. Every `compute` binding carries a `compute_basis` entry that is a verbatim sentence or contiguous group of that policy's own rule; every factor tier is a rule sentence and a branch of its `decides` binding; no branch is absent from the rule and no tier lives only in `compute`.

The five new argument-deciding sentences (r23, r24, r16, r24, r04) carry **no** `compute_basis` entry, correctly: they fix write arguments, not computed quantities, so there is no binding for them to base. They are checked instead under the sweep above.

**R2-NEW-2 closed.** `listings_ext_interval_grant` r21 and r23 now read "half of what **the additions and reductions** give" and "the interval taken as **the additions and reductions** give it", matching r04's "The additions and reductions the vehicle's record calls for are summed and applied once to the standard interval" and matching `compute.adjusted_interval` = `base_interval + paper_currency_addition − overrun_reduction + service_addition − mileage_reduction − recovery_reduction`. The dangling "the share" is gone from the rule, from `factors[id=fault_standing_basis].ladder` and from `compute_basis.granted_interval`. **The rule makes no empty promise.**

**R2-NEW-1 closed.** `listings_ext_document_verification` r15 now reads "and **any other vehicle** adds none on this ground", which is exactly the coverage of `compute.lapse_addition`'s `else` branch. The one-to-seven-day band that matched no stated tier in revision 2 is inside the fall-through as stated. The ladder's three tiers are exhaustive and pairwise disjoint in the prose as well as in the expression.

### the negative-restriction sweep — the sibling's shape, checked here

The sibling's shape is an aggregate whose restriction is an **absence**: no status or kind filter, where the prose implies one and neighbouring aggregates carry stated filters. This charter was swept for every aggregate carrying **no** `event_type`, `outcome`, `document_kind`, `defect_code` or `entry_basis` filter. Five hits, in two shapes:

**Shape A — `MAX('listings_inspections', 'odometer_reading')` with no `event_type` filter**, in `fault_intake`, `valuation_assessment`, `class_assignment` and `interval_grant`. Rows of every kind in `listings_inspections` carry an `odometer_reading`, so the unfiltered maximum ranges over inspections, odometer reports and valuations alike. **The absence is stated.** Each of the four says "the highest odometer reading standing **on the condition record**", and the charter's own contrasting form is right beside it: `booked_consumption` r06 and `reported_consumption` r05 say "the highest reading standing on that vehicle's **odometer records**" and their expressions *do* carry `event_type='listings_odometer_reported'`. The two scopes are named by two different phrases and the phrases track the filters. **Clear.** (It also makes no difference on either world: 35 820 and 88 540 are the maxima under both readings.)

**Shape B — `XSUM('service', 'service_visits', 'invoice_amount', within_months=24, date_field='visit_date')` in `valuation_assessment`, with neither an `event_type` nor an `outcome` filter. This is the sibling's shape, and here it is not stated.** Recorded as **R3-NEW-2**.

### action_binding_and_uuids, prerequisite_graph, prerequisite_sentences (revision 3)

`task_tools.py` is byte-identical to round 2, so the tool-contract conclusions carry on identical inputs: eight tools, each `(target_tool, computes)` pair claimed by exactly one policy, two `owner="user"` tools at the two chain roots, **no function validating a prerequisite**, and the eight uuid8 tails unchanged (with **CG-OBS-2** standing).

The `prerequisite` graph is unchanged in every field — same six edges, same kinds, same gates, same forms, same `resolved_by`, same `policy_source` strings — except that `reported_consumption`'s `policy_source` and `condition` now say "the reported stretch" where the rule does. Acyclic, two disjoint chains, every `gate` naming a binding that exists. All six prerequisite sentences re-located verbatim and re-tested against the four-point test: unchanged conclusions from revision 2.

### the renaming — judged

**Faithful, and it disturbs nothing.** The reworker renamed one quantity apart into two: `booked_consumption`'s "the stretch" → "**the booked stretch**", `reported_consumption`'s → "**the reported stretch**".

- *Is it faithful?* Yes. The renaming is lexical: no threshold, window, filter, rounding point or operand moved, and **no `compute` binding changed**. `booked_consumption.result` is still `MX(raw_stretch − total_allowance, 0)` and `reported_consumption.result` is still `MX(reported_stretch − total_allowance, 0)`. The baselines still assemble the same way from the same inputs.
- *Does it fix what it was aimed at?* Yes, and the diagnosis was right. In revision 2 the two baselines' assembly sentences were word-for-word identical — both read "The allowances the vehicle's record calls for are summed and taken off **the stretch** once, a result of less than nothing being counted as nothing" — on the very sentence that should tell a reader *which* computation an allowance belongs to. They now read "the allowances **against the booked stretch** … taken off the booked stretch once" and "the allowances **against the reported stretch** … taken off the reported stretch once", and every one of the seven allowance tiers across the two policies now ends "against the booked stretch" or "against the reported stretch". Each allowance now names **the quantity it is allowed against**, which is a fact about the business, rather than pointing at a document, which would be a rendering artefact leaking into policy. That distinction is the right one.
- *Does it disturb anything that passed?* No. Re-derived on both worlds: task 1's four scored values are unmoved (14, 6 700, 90, 40), every factor still bears weight against a baseline that is both its fall-through and what its `baseline.rule` states, and the two policies' `baseline.params` remain `[]`. One cosmetic residue: `booked_consumption`'s compute binding is still named `raw_stretch` while its prose now says "the booked stretch". Binding names are internal and `compute_basis.raw_stretch` quotes the right sentence, so this is noted and not counted against the charter.

**Judgement: the renaming is faithful, correctly aimed and inert with respect to every figure.** Recorded as **R3-CLOSED-2**.

### the two policy-side notes — judged

**The variance tolerance published twice — the *naming* diagnosis is correct.** Base carries `odometer_variance_tolerance_miles` as a **per-class** parameter (Economy 50, Standard 50, Premium 35, Luxury 25, Exotic 10, Commercial Van 75) and base `listings_evt_inspection` sentence 4 calls it "the class's variance tolerance". `reported_consumption` carried its own flat `reading_variance_tolerance_miles: 75`. These are two different quantities — one varies by class, one does not — that happened to coincide at 75 for the one class in play and shared a name that invited a reader to treat them as one. Renaming the extended constant to `queried_reading_margin_miles`, and re-wording r06 to "cut back by the **seventy-five mile margin the marketplace queries rather than charges**", separates them by name and by description. **The figures are unchanged (75 either way) and no computation moves**, which this auditor confirmed by recomputation. The diagnosis of *naming* rather than *arithmetic* is right: there was never a second number, only a second referent for one name. A residual worth noting is that the marketplace-wide margin is flat while the class tolerance is graded — defensible, since they are now expressly different quantities, and in any case base sentence 4 is superseded for host readings by `reported_consumption.overwrite[0]`. **Closed**; recorded as **R3-CLOSED-3**.

**The ladder gap whose prose disagreed with its `otherwise`** — this is **R2-NEW-1**, closed above under `rule_compute_equivalence (revision 3)`.

**The round-2 leftover "the share and the adjustments"** — this is **R2-NEW-2**, closed above.

### factor_ladders (revision 3)

No factor was added, removed, re-labelled, re-tiered or re-based this round. Counts per policy are unchanged (6/6/5/4/4/6/5/4; `parameter` 5/4/3/3/3/5/4/3; `method` 1/2/2/1/1/1/1/1), every ladder has three tiers stated in full and pairwise disjoint — now including `document_verification`'s lapse ladder, whose stated fall-through was widened to match its expression — no two tiers of any ladder select the same value or method, and every factor's declared `baseline` is both its own fall-through and what its policy's `baseline.rule` states for that input. Per-world weight is demonstrated in the task files.

### findings (revision 3)

**R3-CLOSED-1 — the returned finding is genuinely closed, and no `overwrite` is owed.** Reasoning above under *the returned finding* and *the no-`overwrite` claim*.

**R3-CLOSED-2 — the renaming is faithful and inert.** Reasoning above.

**R3-CLOSED-3 — the variance-tolerance collision was a naming collision and is resolved by name.** Reasoning above.

**R2-NEW-1, R2-NEW-2 — CLOSED.** Reasoning above.

---

**R3-NEW-1 — observation (new). `listings_ext_interval_grant` r24 decides three scored arguments from fields of another category that the policy does not declare it reads.**

- *Symptom.* r24, verbatim: "A completed inspection is filed at the odometer **the record of the inspection carries**, with **the finding that record reached**, and through **the channel the inspection was carried out under**." In the reachable context the only record of that inspection is a Keyturn Vehicle Care Plan visit — a `service_visits` row — and the three values are its `odometer_reading`, its `outcome` and its `shop_channel`.
- *Root cause.* `listings_ext_interval_grant.cross_category` declares its `service` reads as exactly `['service_visits.outcome', 'service_visits.visit_date']`, which the *aggregate* `care_visits_24m` needs. r24 additionally requires `service_visits.odometer_reading` and `service_visits.shop_channel`, and neither is declared. The four other new argument-deciding sentences (`fault_intake` r23, `valuation_assessment` r24, `document_verification` r16, `booked_consumption` r04) all point at records inside this category or name the value outright; r24 is the only one that points outside it.
- *Evidence.* `rule` r24; `cross_category[0].reads`; `compute.care_visits_24m`. The gate `check_extended` passes because it reads the declaration against `compute`/`inputs` bindings, not against rule prose.
- *Why an observation and not a red light.* The agent is not blocked — `find_service_visits` is a shared read tool that returns the whole row, including both fields — and r24's natural reading still lands on exactly one value for each of the three arguments, so no second answer can be demonstrated. The defect is that the policy's declaration of what it reads across a category boundary is now narrower than what its own rule requires.
- *Affected artifact and location.* `listings.extended.yaml` → `listings_ext_interval_grant` → `rule` r24, `cross_category[0].reads`.

---

**R3-NEW-2 — observation (new, and the sibling's shape). `listings_ext_valuation_assessment.workshop_spend_24m` carries neither an `event_type` nor an `outcome` filter, and its prose states no such breadth.**

- *Symptom.* `compute.workshop_spend_24m` is `XSUM('service', 'service_visits', 'invoice_amount', within_months=24, date_field='visit_date')` — every row of `service_visits` in the window, whatever kind of record it is and however the visit ended.
- *Root cause.* The absence of a filter is itself a fact the prose must state, and it does not. r21, verbatim: "A vehicle carrying **workshop invoices** of one thousand two hundred dollars or more **under a Keyturn Vehicle Care Plan** in the rolling twenty-four months counted back from the handling date steps down at three quarters of the rate that otherwise applies". Nothing there tells a reader the sum reaches past completed workshop visits.
- *Evidence that the breadth is material.* `db_schema.json` gives `service_visits.event_type` the values `service_visit_completed`, `service_credit_granted`, `service_excess_charged`, **`service_visit_missed`** and **`service_plan_billed`**, and `blueprint/products/service.yaml` carries `outcome` values including `completed`, `billed` and "Why the visit did not happen". So the unfiltered sum would add a monthly **plan billing run**'s `invoice_amount` and a **missed** visit's to the workshop spend — quantities no reader of "workshop invoices" would include.
- *Evidence that the prose implies a filter.* Every other cross-category `service` aggregate in this charter states one: `fault_intake.care_visits_12m`, `class_assignment.care_visits_24m`, `interval_grant.care_visits_24m` and `booked_consumption.care_visits_3m` all carry `outcome='completed'`, and all four rules say "**completed** Keyturn Vehicle Care Plan visits". A reader who has met that convention four times meets r21's bare "workshop invoices" and has every reason to supply the filter the other four state.
- *Why an observation and not a red light.* On task 0's world — the only world where this policy is scored — all `service_visits` rows are `service_visit_completed` with `outcome: completed`, so the filtered and unfiltered sums are both 860.00 and no second number can be demonstrated. The defect is a rule that does not state a restriction its expression relies on being absent.
- *Affected artifact and location.* `listings.extended.yaml` → `listings_ext_valuation_assessment` → `rule` r21–r23, `compute.workshop_spend_24m`, `compute_basis.workshop_spend_24m`, `inputs.history` (the `service` entry, `filters: {}`).

---

**R3-OBS-1 — observation. The sweep's "25 already decided" and this auditor's 28 differ by three.** The enumeration above is this auditor's working. The three most likely to be counted differently are `verify_listing_document.document_kind`, `record_booked_mileage.source_inspection_id` and `report_vehicle_mileage.odometer_reading`, each of which this auditor judges decided by records and the persona rather than by a rule sentence of its own. No argument is undecided on either count, so this bears on bookkeeping only; it is settled against `argument_uniqueness_tracing` in the per-task comparisons.

**R2-NEW-3, R2-NEW-4, R2-OBS-1, CG-OBS-1, CG-OBS-2, CG-OBS-5, CG-OBS-7 — re-checked and unchanged**, each still standing as an observation. `interval_grant.inputs.history` still omits the `photo_count` read (**R2-NEW-3**), and the same policy's cross-category declaration now also omits two argument reads (**R3-NEW-1**) — the two are the same kind of gap in the same block and are worth reading together.

## closing_checklist (revision 3)

Written **after** both round-3 reveals. The revision-1 and revision-2 checklists are preserved above and are not rewritten.

**This difficulty closes again, on a stronger footing than at round 2.**

| item | state |
| --- | --- |
| per-task files one-to-one with the tasks; old revisions traceable | ✓ three revisions preserved in all three files |
| every comparison section carries a PASS | ✓ `0.md` revision 3: PASS; `1.md` revision 3: PASS |
| extended policies covered, scopes pairwise disjoint | ✓ 8 of 8, two disjoint chains of four |
| task tools and GT closed; uuid8s frozen | ✓ `task_tools.py` byte-identical to round 2; **CG-OBS-2** stands |
| each tree: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner="user"` write, acyclic | ✓ 3 / 3 / root / acyclic, both tasks; difficulty-wide DAG intact |
| every computation declares a self-sufficient baseline | ✓ all eight |
| 4–6 factors, ≥2 `parameter`, ≥1 `method`; ≥1 multi-source and ≥1 cross-difficulty per task | ✓ |
| every ladder ≥3 tiers stated in full, exhaustive and pairwise disjoint in the prose as well as the expression | ✓ **now including `document_verification`'s lapse ladder** (R2-NEW-1 closed) |
| every factor bears weight against an honest baseline; baseline alone giving a definite number different from gold | ✓ all 40 |
| **every scored argument decided by the policy, the records or the persona** | ✓ **all 38**, nine of them by rule sentences added this round; verified against an oracle built from `task_tools.py` before any reveal |
| rule makes no empty promise | ✓ R2-NEW-2 closed |
| base section unedited | ✓ re-verified key-for-key |
| instantiation-stage gates re-run on the final form | ✓ by the coordinator, read-only, **all eight green** including `check_traceability`; this auditor ran no gate itself |

### verdicts (revision 3)

| task | policy self-consistency | problem tree | factors bear weight | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | **PASS** |
| 1 | PASS | PASS | PASS | PASS | **PASS** |

### disposition of every round-2 and returned item

| item | claim | this auditor's finding |
| --- | --- | --- |
| the returned undecided argument | closed by stating the deciding rule; no `overwrite` owed; persona aligned | **CLOSED.** r16 names the channel by mirroring the tool gloss and excludes `self_photo` in terms; the persona now says the host submitted and the marketplace checks. **The no-`overwrite` claim holds** — base names no channel, so there is no base conclusion to contradict, and the channel named sits inside the class's `inspection_channel_allowed` |
| the 38-argument sweep | all 38 covered; 9 in three further groups newly decided; 25 already decided | **COMPLETE.** 38 is the right total (verified from `task_tools.py` before any reveal), all 38 are traced, all 38 are decided, and 9 carry a deciding-rule citation. The "nine further" is the total cited (1 returned + 8 others) and the "25 already decided" leaves four unaccounted on its own arithmetic — **bookkeeping only; the coverage claim itself is verified** (**R3-OBS-1**, settled) |
| the variance tolerance published twice | a naming collision, constant renamed, figures unchanged | **CLOSED** — the diagnosis is right: base's is per-class, the extended one is flat, they coincided only on this class. No figure moves (**R3-CLOSED-3**) |
| the ladder gap (R2-NEW-1) | prose made to say what the ladder says | **CLOSED** — r15's fall-through is now "any other vehicle" |
| "the share and the adjustments" (R2-NEW-2) | corrected to "the additions and reductions" | **CLOSED** — rule, ladder and basis all corrected; no empty promise remains |
| the "the stretch" renaming | renamed apart so each allowance names its quantity | **FAITHFUL AND INERT** (**R3-CLOSED-2**). Lexical only; no compute binding changed; both worlds re-derived with every figure unmoved. The diagnosis was right — the two baselines' assembly sentences were word-for-word identical on the one point that should have distinguished them |
| the stale-figure sweep | caught a `solvability_contract` business effect quoting a superseded figure | **CONFIRMED** — step 16 now reads 6,700; every other occurrence of a superseded figure is a live sensitivity, an edge-skip figure or a narrative quotation |
| the negative-restriction question from the sibling | — | **SWEPT. One hit: R3-NEW-2.** `MAX('listings_inspections','odometer_reading')` states its breadth ("the condition record" against the charter's own contrasting "odometer records") and is clear; `XSUM('service','service_visits','invoice_amount', …)` in `valuation_assessment` does not |

### new items found this round

Both are observations; neither changes a scored value, and neither is grounds for rework on its own.

| id | where | one line |
| --- | --- | --- |
| **R3-NEW-1** | `interval_grant` r24 / `cross_category` | three scored arguments are decided from `service_visits.odometer_reading` and `.shop_channel`, neither declared in the policy's cross-category reads |
| **R3-NEW-2** | `valuation_assessment.workshop_spend_24m` | the sibling's shape: no `event_type` and no `outcome` filter, where the prose says only "workshop invoices … under a Keyturn Vehicle Care Plan" and the charter's four other `service` aggregates all state "completed"; a plan billing run's or a missed visit's `invoice_amount` would be summed |
| **R3-OBS-1** | the sweep's arithmetic | settled: coverage complete, counts mis-stated |
| **R3-T1-OBS-1** | the returned argument's tracing | leads with the corroborating record and reaches the deciding rule afterwards |

### a correction this auditor makes about its own earlier rounds

Revision 1 recorded the undecided-argument shape twice — **T0-OBS-1** and **T1-OBS-1** — and stopped at an observation both times, reasoning that a residual-exclusion argument made the value unique. Revision 2 carried that ruling forward. The skill's unique-solution row requires the policy to entail "the object, **the parameters**, the owner, the order and the terminal state", so an argument no rule decides is a uniqueness failure on this auditor's own standard, exclusion argument or not. Reading the published documents alone is what made it unmissable, but the standard it failed was already here. The revision-1 and revision-2 texts are left exactly as written; this correction is recorded rather than folded back into them.

Both blind derivations of this round reproduced every scored value, every `baseline_result`, every `factor_sensitivity` figure and every write argument exactly, and found no scored value moved anywhere — which is what an unchanged set of `compute` bindings requires.
