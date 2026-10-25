# Policy-task audit — alignment_plan_service / charter-global

## charter_global_frozen
- Freeze time: 2026-10-14T23:12Z (written before any task's GT was revealed; contains nothing derived from a revealed GT).
- Auditor: erl-task-policy-audit subagent (independent of the instantiator).
- Frozen inputs (sha256 re-verified against the gate snapshot `env/env_0062_tire_and_auto_service_chain/.audit_views/policy/alignment_plan_service/snapshot_r1.txt`):
  - `tasks/alignment_plan_service/alignment.extended.yaml` c33bfed5de39c6df78aaeaa2e7766a724044cf37df49e6cd84cc5acea7964522
  - `tasks/alignment_plan_service/task_tools.py` 8714dd33cb69f9eb9dffcc6d772d469e1532a5681cee8edaf79fbafaea6e759d
  - masked views `.audit_views/policy/alignment_plan_service/0.json` 8434f633…, `1.json` ef0cf8d8… (match)
- Read: blueprint (`products/alignment.yaml`, `products/tires.yaml` alignment_check_included lines, `products/hazard.yaml` variant names, `share_tools.py` tool list, `db_schema.json`), the extended charter, `task_tools.py`, the two masked views, `skills/erl-task-instantiate/scripts/check_compute.py` (DSL semantics only).
- Not read: tasks/*/tasks/*.json, worklog.md, plan.md, docs/, any sibling difficulty, any /tmp/*_0062 instantiator scratch. No recursive grep over env/.
- Entry conditions: gate snapshot supplied (all d_gates green; validate_scenario / check_traceability red only on pre-render items, out of scope). Masked views and hashes supplied. Complete.

### policy_conflict_scan
- Base copy: the base section of `alignment.extended.yaml` is key-for-key equal to `blueprint/products/alignment.yaml` (yaml-load compare: category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies all equal; only `extended_policies` added). Verbatim.
- Six extended policies, each its own subject/compute/target tool:
  | policy | subject | computes | target_tool (owner) |
  |---|---|---|---|
  | alignment_ext_open_visit_labor | alignment_service_performed | charge_amount | price_alignment_work_order_228c355b (agent) |
  | alignment_ext_open_visit_parts | alignment_service_performed | parts_charge | price_work_order_parts_2c1ce050 (agent) |
  | alignment_ext_cancellation_settlement | alignment_cancellation, alignment_refund | refund_amount | confirm_alignment_cancellation_b0865de9 (user) |
  | alignment_ext_household_enrollment | alignment_purchase | purchase_price | enroll_household_alignment_plan_f0fe3800 (user) |
  | alignment_ext_term_renewal | alignment_purchase | purchase_price | renew_alignment_plan_418ab11e (user) |
  | alignment_ext_readjustment_parts | alignment_readjustment | parts_charge | price_alignment_readjustment_e00d4c5e (agent) |
- Overlaps: labor and parts share subject alignment_service_performed but compute different fields of the same row (charge_amount/service_basis vs parts_charge); household and renewal share alignment_purchase and both restate the base price rule for "every plan that is neither a household plan nor a renewal" identically, so their carve-outs are mutually consistent. Labor excludes commercial-use visits ("a vehicle in commercial use on the visit date is priced under the commercial-use rule"), consistent with base `alignment_commercial_use_exclusion`. No two policies reach different conclusions on the same quantity (but see F6 for a base sentence the labor policy overrides without naming it).
- Scope partition (derived blind from the masked worlds; to be compared with charter_scope after reveal): task 0 = {household_enrollment (root), cancellation_settlement, open_visit_labor, open_visit_parts}; task 1 = {term_renewal (root), readjustment_parts}. Pairwise disjoint, jointly cover all six extended policies. Claimed event types alignment_appointment_booked and alignment_vehicle_retirement are carried by no extended policy (observation O5).

### rule_compute_equivalence
Check 2 swept sentence-by-sentence in both directions for all six policies; every binding's `compute_basis` quotation is a sentence (or clause) of that policy's `rule`, and every rule sentence carrying a quantity is implemented. DSL semantics taken from `check_compute.py` (`SUM/COUNT/MAX/LATEST` scoped to the target holding's pk; `within_months` measured with `MONTHS(row_date, NOW)`, `0 <= m < W`; `MONTHS` = whole months with day-of-month adjustment; `X*` reads scoped to the customer).
- labor: wo_* = LATEST open (service_basis none) WO ✓; anchor (latest plan_included, or later member_early_price when early_price_counts_as_interval) ✓; interval test `MONTHS >= min_interval_months or miles >= min_interval_miles`, single service never ✓; pending request / readjusted-latest-included / pricing base ✓; type share ✓; tire credit vs `wo_date` ✓; hazard credit vs `wo_date` ✓; rounding/floor ✓. **Mismatch F7**: rule "no late fee posted to it in the 12 calendar months up to the visit" — compute `XCOUNT(... within_months=12 ...)` is anchored on NOW, not on the visit (`wo_date`).
- parts: latest WO by date ✓; purchase-visit kit = parts of plan_included alignment dated purchase_date ✓; kit lock / lower-of / listed ✓; install labor ✓; visit-basis rate ✓; card "up to the pricing" = NOW ✓; `+ steering_angle_reset_charge` after rates ✓.
- refund: deductions with tire-day value and type share (`P*(share_sum - n_td*td_share) + td_value*n_td*td_share`) ✓; age anchor ✓; fee ladder ✓; card fee share "up to the cancellation" = NOW ✓; forfeit ✓; open labor/parts = SUM of the plan's alignment_service_performed rows dated NOW ✓; single rounding, floor 0 ✓.
- household: tenure `MONTHS(purchase_date, NOW)` ✓; windowed loyalty count ✓; rate ladder ✓; card ✓; protection credit at customer level ("the customer holds") ✓; purchase credit on the household plan's own purchase_price (LATEST scoped to the household holding) ✓; combined rate applied once ✓.
- renewal: inc_term, final-stretch tests `MONTHS(x, expiration_date) < 6`, grace tests ✓; readjustment-day credit counts guarantee_readjustment rows only ✓; hazard at vehicle level ✓; renewal tire bundle ✓.
- readjustment: open readjustment (basis none) ✓; warranty path (source WO parts > 0, months < parts_warranty_months, miles thresholds, prorate `listed*miles/parts_warranty_miles`) ✓; slip share by `DAYS(src_date, rj_date)` ✓; tire credit vs `rj_date` ✓; hazard ✓. **Mismatch F7**: rule "in the 12 calendar months up to the readjustment" — compute card window anchored on NOW.
- Every `factors[].ladder` tier is a rule sentence and a branch of its `decides` binding, and vice versa (no tier lives only in compute).

### action_binding_and_uuids
- Each `(target_tool, computes)` is claimed by exactly one policy (table above).
- Tool bodies (`task_tools.py`) judge no eligibility, ordering or amount: labor tool validates only the enum of service_basis; parts tool none; readjustment tool none; confirm tool validates only the tender enum; enroll validates tender enum and that the household plan reference is a lifetime tier (argument validity, not a prerequisite: it does not check the target vehicle's active plans); renew validates tender and that the plan id exists (does not check status). No tool reads another problem's state.
- Docstrings: no ordering word (before/after/first used as sequencing), no other tool named, no concrete example value equal to a scored value (only "0.00 when nothing is charged", "T- followed by 8 digits", "always 0.0"); "before tax" is a price qualifier, not sequencing. Minor wording: confirm docstring says refund_amount "positive (0.00 when nothing is refunded)" — observation only.
- uuid8s: 228c355b, 2c1ce050, e00d4c5e, b0865de9, f0fe3800, 418ab11e — distinct, no shared prefix/suffix, no sequence pattern. ✓
- Factor id ⊂ tool name: none of the 31 factor ids is a substring of any of the 6 tool names (scripted check). ✓

### prerequisite_graph
Edges (all `prerequisite` fields present; `[]` on labor and readjustment):
| id | blocked | problem | kind | gate | form | resolved_by |
|---|---|---|---|---|---|---|
| E1 | open_visit_parts | open_visit_labor | value_input | visit_parts_rate (binding exists) | state | price_alignment_work_order_228c355b |
| E2 | cancellation_settlement | open_visit_labor | value_input | open_labor (exists) | state | price_alignment_work_order_228c355b |
| E3 | cancellation_settlement | open_visit_parts | value_input | open_parts (exists) | action + fallback_reason | price_work_order_parts_2c1ce050 |
| E4 | household_enrollment | cancellation_settlement | state_gate | alignment_agg_one_per_vehicle.one_active_per_vehicle (real eligibility id) | state | confirm_alignment_cancellation_b0865de9 |
| E5 | term_renewal | readjustment_parts | value_input | readjustment_day_credit (exists) | state | price_alignment_readjustment_e00d4c5e |
- Every `problem` is an extended policy id of this file, none a base policy, none self. Graph acyclic (household→cancel→{labor, parts}, parts→labor; renewal→readjustment).
- Each `policy_source` is verbatim in its own policy's `rule` (string-located). `fallback_reason` present exactly on E3. `condition`s match the sentences' scope (E2 "every work order … dated the cancellation day" ↔ "No alignment work order on the plan dated the cancellation day carries service basis none"; E5 likewise). `resolved_by` tools genuinely produce the effect (E1/E2: labor tool writes service_basis+charge_amount; E3: parts tool rewrites parts_charge; E4: confirm sets plan status cancelled; E5: readjustment tool sets guarantee_readjustment). No authoring-viewpoint phrasing.

### prerequisite_sentences
- E1 "The parts charge of a work order is not fixed until the work order carries its service basis." — connective "not … until"; waited-on state = the record's `service_basis` field ("service basis", the finder's word); no tool/id/snake_case token. Writes of this difficulty that set a service basis on an alignment work order: only the labor write (the readjustment write sets a basis on readjustment rows, which the parts rule's "alignment work order with the latest work-order date" excludes). One reading.
- E2 "The refund of a cancelled plan is fixed only after every work order on the plan dated the cancellation day carries its service basis." — "only after"; same state; same single writer. Labor rule does not restate it.
- E3 "The refund of a cancelled plan is not paid until the parts on the plan's work orders of the cancellation day have been priced by the plan desk." — action form; fallback tested: the parts write only rewrites the numeric `parts_charge` (store's listed figure → priced figure); no status/basis field records it. Justified.
- E4 "A household plan is sold only after the vehicle it is bought for carries no active alignment service or plan." — state form; in this difficulty only the confirm-cancellation write moves a plan out of `active` (share tools contain no alignment write; expiry/retirement have no tool). One reading. (Base `alignment_agg_one_per_vehicle` also states "buys the new plan only after the first has expired or been cancelled"; the extended rule carries its own sentence, so this base order grounds nothing — observation O6.)
- E5 "A renewal is priced only after every readjustment under the expired plan dated the renewal day carries its guarantee basis." — state form; single writer = readjustment write.
- Derivations: E1/E2: reader sees open WO (service_basis none) → labor rule says the plan desk sets labor and basis on the open work order → labor write. E3: rule names the action (plan desk prices parts) → parts rule. E4: vehicle's other plan active → refund rule (cancellation completed when holder confirms the registered request) → confirm write. E5: open readjustment (basis none) → readjustment rule (plan desk books it as a guarantee readjustment) → readjustment write.
- No extended rule states an undeclared cross-problem order (the refund rule's "the holder confirms the cancellation request the agent registered" refers to request registration, which is not a problem of this charter).

### override_declarations
Sentence-by-sentence over each `base_policy_refs` entry:
- labor ← alignment_evt_service: active/term/month-counting/lifetime/type-covered/worn-parts sentences followed; "On a plan the alignment is plan_included … restarts the interval …" declared superseded. **F6 (undeclared override)**: base sentence "A single service includes only its purchase-day alignment; any later alignment on it is charged member_early_alignment_price." is not named in `overwrite`, yet the extended rule prices single-service open work orders ("a single service never reaches it"; pricing base = member_early_alignment_price, then × type share × (1 − card rate) − credits). ← alignment_commercial_use_exclusion: followed (commercial-use visits carved out). Observation O3: the ext anchor sentence takes "the plan's latest member_early_price alignment" without excluding commercial-use alignments, which base says do not restart the interval (same latent gap exists inside base `alignment_evt_service`; no row in either world).
- parts ← alignment_evt_service: parts sentence declared superseded; rest followed.
- refund ← alignment_evt_cancellation_refund: window/active/holder-confirms/tender sentences followed; refund formula declared superseded; "member early price and readjustments not deducted" kept.
- household / renewal ← multi_holding, one_per_vehicle, purchase_pricing, commercial_use: price clause and purchase-visit-alignment clause declared superseded in both; entry gate / personal use / one-per-vehicle / lifetime-no-expiry kept. In task 0 the base tire bundle would apply to the Civic (tire set installed 22 days earlier) — the declared household carve-out removes it, merged semantics unique.
- readjustment ← alignment_evt_readjustment: labor/parts sentence declared superseded; guarantee window/miles/condition/exclusions/citation/any-status sentences kept.

### factor_ladders
Structure per policy (labels as declared; tiers 3 each; disjoint bindings; `decides` is an input, never `result`; every tier in the rule):
| policy | factors (effect) | P/M | cross_difficulty |
|---|---|---|---|
| labor | member_pricing_path (M), alignment_type_share (P), cardholder_labor_rate (P, multi-source: card account + card transactions), new_tire_visit_credit (P), road_hazard_impact_credit (P) | 4/1 | card, tires, hazard |
| parts | purchase_kit_reference (M), kit_installation_labor (P), visit_basis_parts_rate (P), cardholder_parts_rate (P, multi-source) | 3/1 | card |
| refund | tire_day_alignment_value (P), deduction_type_share (P), request_age_anchor (M), cancellation_age_fee (P), cardholder_fee_share (P, multi-source), protection_package_forfeit (P) | 5/1 | tires, card, hazard |
| household | household_loyalty_rate (P, multi-source tenure+count), loyalty_count_window (M), cardholder_household_rate (P, multi-source), road_hazard_protection_credit (P), household_plan_price_credit (P) | 4/1 | card, hazard |
| renewal | renewal_grace_rate (P), grace_period_anchor (M), readjustment_day_credit (P), cardholder_renewal_rate (P, multi-source), road_hazard_renewal_credit (P), renewal_tire_bundle (P) | 5/1 | card, hazard, tires |
| readjustment | parts_warranty_path (M, multi-source), guarantee_slip_share (P), cardholder_readjust_rate (P, multi-source), new_tire_readjust_credit (P), road_hazard_readjust_credit (P) | 4/1 | card, tires, hazard |
No two tiers of any ladder select the same value/method. Every fall-through equals the factor's `baseline`. Every policy has a `baseline.rule` whose sentences are in its `rule` and which yields a definite number.

Ladders that fail the reality / label tests (each is a charter object; consequences demonstrated in the task files):
- **F1 member_pricing_path tier 2 (unreal outcome)**: "On a plan with no cancellation request awaiting confirmation whose latest plan_included alignment has already been readjusted under its guarantee, the open work order is priced from the tier's member_early_alignment_price whether or not the interval is reached." Because the visit so priced is booked member_early_price (amount > 0), the plan's latest plan_included alignment stays the readjusted one, so every later visit on that plan hits the same tier: one free guarantee readjustment permanently ends the plan's included alignments. Demonstration on task 0's own seed: the Highlander Lifetime plan's latest plan_included alignment 77ea9ed3 (2026-03-21) was readjusted by b40b79e7 (2026-04-04); an open work order on that plan on 2026-10-14 (interval reached: 6 whole months) would be charged 49.99 × share × (1 − card) − credits instead of 0.00, and so would every subsequent visit. No tire & auto chain publishes "using your readjustment guarantee forfeits your plan's included alignments for good"; it also defeats base `alignment_evt_readjustment` ("never counts as an included alignment or restarts the plan interval") in effect. With the tier struck, labor has no `method` factor.
- **F2 visit_basis_parts_rate fall-through unreachable**: fall-through "0 while its service basis is still open". The same rule says "The parts charge of a work order is not fixed until the work order carries its service basis", so at this write's handling time every customer is on tier 1 or 2; the fall-through (= the baseline) is not a treatment any customer is given, only the out-of-order value. Effective ladder 2 tiers → factor struck → parts has 3 surviving factors (< 4).
- **F3 request_age_anchor: a condition that holds of every customer reaching the write; fall-through unreachable**: a cancellation is completed only "when the holder confirms the cancellation request the agent registered" and the confirm tool takes a pending request id, so "a request awaits the holder's confirmation" (part of tiers 1 and 2) holds of every customer at this write and the fall-through "in every other case the age runs to the cancellation date" (= baseline `NOW`) is never selected. Effective 2 tiers → struck → refund loses its only `method` factor.
- **F4 protection_package_forfeit (condition/outcome no business holds)**: deducts 15.00 when the vehicle's road hazard certificate was sold on the plan's ticket and 7.50 when sold on another ticket within 30 days. No charter in this scenario grants any alignment+road-hazard package price (no "package"/bundle term in hazard.yaml, tires.yaml or the alignment charter beyond the tire bundle), so the forfeit claws back a benefit never given; the customer keeps the certificate. A road hazard purchase is not something a tire chain weighs when refunding an alignment plan. Struck.
- **F5 loyalty_count_window mislabelled `method`**: its tiers count the same thing (plan_included alignments on the household plan) with the same formula over a lookback of 24 months / 12 months / unbounded — only a window length changes, i.e. a number substituted into `COUNT(..., within_months=W)`. It is a `parameter`; household then has 0 `method` factors.
- Borderline, recorded as observations: O1 purchase_kit_reference tier 1 bills "the purchase-visit kit price whatever the listed price", i.e. above current list when list fell (a two-way price lock — unusual for parts, not impossible); O2 request_age_anchor's label (selects which recorded date the age runs to) — honest enough as an evidence-anchor choice, moot given F3; O4 household_plan_price_credit gives a larger credit to customers whose first plan was bought at full price (loyalty logic is unusual but publishable).
- All other ladders: conditions are things a tire/auto chain weighs (card standing, recent tire purchase and line, recent road-hazard impact replacement, alignment type, kit installation scope, cancellation age, tenure/loyalty, grace period, readjustment timing, parts-warranty mileage, slip timing) and outcomes are publishable treatments.

### findings
| id | class | finding | bears on |
|---|---|---|---|
| F1 | SOURCE-FACTOR (unreal ladder) | labor member_pricing_path tier 2 permanently forfeits included alignments after one guarantee readjustment | task 0 (labor) |
| F2 | SOURCE-FACTOR (unreachable fall-through / ordering-artifact tier) | parts visit_basis_parts_rate fall-through "basis still open" | task 0 (parts) |
| F3 | SOURCE-FACTOR (same class as F2: scope-restating condition, unreachable fall-through) | refund request_age_anchor | task 0 (refund) |
| F4 | SOURCE-FACTOR (unreal condition/outcome) | refund protection_package_forfeit with no package in any charter | task 0 (refund) |
| F5 | SOURCE-FACTOR (mislabelled effect) | household loyalty_count_window is a window-length parameter | task 0 (household) |
| F6 | SOURCE-POLICY (undeclared override) | labor policy re-prices single-service later alignments without naming base sentence "any later alignment on it is charged member_early_alignment_price". Two passages, same situation (a Four-Wheel single-service holder's open thrust work order, clean card, no credits): base → 109.99; ext → 109.99 × 0.80 × 0.90 = 79.19. | no scored value in task 0 or 1 (both labor WOs are on multi-year plans; task 1 has none) |
| F7 | SOURCE-POLICY (rule/compute window anchor) | labor and readjustment card windows: rule "12 calendar months up to the visit / the readjustment", compute anchored on NOW. Same situation (open WO dated 2026-10-10, late fee 2025-10-12, handled 2026-10-14): rule counts the fee (late tier), compute does not (clean tier). | no scored value in task 0 or 1 (visit / readjustment dated the handling day in both) |
Class sweep (one rework closes the class):
- Unreachable fall-through / condition true of every customer at the write: F2 (parts), F3 (refund). Checked and clear: every other factor's fall-through is occupied by real customers (e.g. renewal readjustment_day_credit "otherwise" = customers with no readjustment).
- Unreal tier outcome / condition: F1, F4 (plus borderline O1, O4).
- Mislabelled method: F5 (borderline O2). Others honest: member_pricing_path (interval test vs fixed figure), purchase_kit_reference (lock / lower-of / list), grace_period_anchor (months-from-alignment vs days-from-expiry), parts_warranty_path (free / prorate / full).
- Card-window anchor mismatch: F7 covers labor and readjustment; parts, refund, household, renewal anchor on the handling day both in rule and compute.
- Undeclared override: F6 only.
Observations: O1–O4 above; O5 claimed event types without an extended policy; O6 base cross-problem order sentence in alignment_agg_one_per_vehicle (grounds no edge); O7 parts "listed parts" also carries the ADAS recalibration charge, so the kit lock / lower-of would apply to a recalibration figure too (rule's "kit price of the listed parts" conflates them; no ADAS row in either world).

## closing_checklist
Written 2026-10-14T23:20Z, after both reveals. **Difficulty not closed.**
- Per-task files 0.md, 1.md correspond one-to-one with tasks/0.json, tasks/1.json; this is revision 1 (no older revisions).
- Scopes: charter_scope of task 0 {labor, parts, cancellation_settlement, household_enrollment} and task 1 {readjustment_parts, term_renewal} are disjoint and cover all six extended policies; task tools and GT closed; uuid8s independent.
- Trees: task 0 n=3 with 3 value_input edges and two owner=user writes; task 1 n=1 with 1 value_input edge and one owner=user write; difficulty graph acyclic.
- Factors: task 1 passes; task 0 fails (F1–F5 strike factors from all four of its computations).
- Open charter items: F1, F2, F3, F4, F5 (SOURCE-FACTOR, all bearing on task 0), F6, F7 (SOURCE-POLICY, no scored value moved in either task).
- Gates not re-run by this audit (coordinator's responsibility on the final form).

## revision_2

### charter_global_frozen (round 2)
- Freeze time: 2026-10-15 (written before any round-2 GT reveal; nothing derived from a revealed GT). Auditor: same subagent.
- Inputs re-verified against `.audit_views/policy/alignment_plan_service/snapshot_r2.txt`: `alignment.extended.yaml` ce8941527123afc787c7b32675d327b14d0a32388983de0177fcf2e1f2146d50 (changed → every charter-global section re-derived below); `task_tools.py` 8714dd33… (unchanged → tool-module conclusions of round 1 carried forward on that hash); views 0.json 974e0521… (changed), 1.json ef0cf8d8… (unchanged).
- Base copy: still key-for-key equal to `blueprint/products/alignment.yaml`.

### policy_conflict_scan (round 2)
- Same six policies, same targets/computes. Task-0 partition now {household (root), cancellation_settlement, open_visit_labor, open_visit_parts}; task 1 {term_renewal (root), readjustment_parts}. Disjoint, complete.
- Labor now limits itself to "the open work order of a 1-Year, 3-Year or lifetime plan … a later alignment on a single service is charged under the base single-service rule … outside this policy" — no longer overlaps base single-service pricing.
- Parts now leaves "a work order on which the vehicle requires a recalibration" to the base rule.

### rule_compute_equivalence (round 2)
Swept again sentence by sentence for all six policies.
- labor: new sentences (lifetime sliding scale; advance-booking credit "read from the latest appointment booked on the plan for the visit's date": `bk_made` LATEST booking with appointment_date = wo_date, `bk_lead` DAYS) each quoted and implemented; card window "12 calendar months up to the plan desk's pricing" = NOW ✓ (F7 closed for labor).
- parts: lower-of / listed-less-half-excess / listed, new-set parts rate (tire set within 30 days × line check) ✓.
- refund: fee bands now in the base text "calendar days from the purchase_date to the cancellation date"; hold-window anchor (`pending_hold = DAYS(pending_at, NOW) <= 7`) and "the fee is read from the same age bands at whichever date applies" ✓; usage charge "from the plan's purchase odometer to the odometer of its latest alignment work order" (`LATEST odometer - purchase_odometer`, strict > 2000 / ≥ 500) ✓.
- household: fixed trailing-24-month loyalty count ✓; per-tire / flat / none protection credit (`covered_tire_count`) ✓; service-currency credit by whole months since the household plan's latest plan_included ✓.
- renewal: rate by included count (≥5 / ≥3 / else 0) and the separate "given only to a renewal inside its grace period" (`granted_rate`) ✓.
- readjustment: card window "up to the plan desk's booking of the readjustment" = NOW ✓ (F7 closed for readjustment).
- Every ladder tier is a rule sentence and a branch of its binding, and conversely.

### action_binding_and_uuids (round 2)
Carried forward (task_tools.py hash unchanged; `(target_tool, computes)` pairs unchanged). Factor-id ⊂ tool-name re-checked for the new ids (advance_booking_credit, new_set_parts_rate, plan_mileage_usage_charge, protection_credit_basis, household_service_currency): none.

### prerequisite_graph and prerequisite_sentences (round 2)
- E1 (parts ← labor) removed; the parts rule no longer carries "not fixed until … service basis", and no parts binding reads the basis. E2–E5 unchanged and still verbatim in their own rules; acyclic; E3 fallback still justified (parts write leaves no state field).
- New consequence: labor and parts are now independent parallel prerequisites of the refund (labor reads only basis-none rows and never parts_charge; parts reads the latest work order's listed parts/type/date and never basis/charge). Either order leaves the same terminal state — no two-solution risk.
- No rule states an undeclared cross-problem order.

### override_declarations (round 2)
- labor ← alignment_evt_service: the single-service sentence is now explicitly left to base (scope carve-out) → **F6 closed**.
- parts ← alignment_evt_service: superseded parts sentence declared; replaced_by restates base for recalibration work orders → round-1 O7 addressed (residual observation O8: nothing in the records marks "the vehicle requires a recalibration"; no such row in either world).
- refund, household, renewal, readjustment: as round 1; new terms all inside the declared replaced formulas.

### factor_ladders (round 2)
| policy | factors (effect) | P/M |
|---|---|---|
| labor | member_pricing_path (M: standard labor / lifetime sliding scale / interval-tested pricing base), alignment_type_share, cardholder_labor_rate (multi-source), new_tire_visit_credit, road_hazard_impact_credit, advance_booking_credit | 5/1 |
| parts | purchase_kit_reference (M: lower-of / listed-less-half-excess / listed), kit_installation_labor, new_set_parts_rate, cardholder_parts_rate (multi-source) | 3/1 |
| refund | tire_day_alignment_value, deduction_type_share, request_age_anchor (M), cardholder_fee_share (multi-source), plan_mileage_usage_charge | 4/1 |
| household | household_loyalty_rate (multi-source tenure + count), cardholder_household_rate (multi-source), protection_credit_basis (M: per covered tire / flat / none), household_plan_price_credit, household_service_currency | 4/1 |
| renewal | renewal_grace_rate, grace_period_anchor (M), readjustment_day_credit, cardholder_renewal_rate (multi-source), road_hazard_renewal_credit, renewal_tire_bundle | 5/1 |
| readjustment | parts_warranty_path (M, multi-source), guarantee_slip_share, cardholder_readjust_rate (multi-source), new_tire_readjust_credit, road_hazard_readjust_credit | 4/1 |
Round-1 items:
- **F1 closed**: the "readjusted latest included → member price forever" tier is gone; tier 2 is now a lifetime-plan sliding early price (member_early_alignment_price × whole months still to run / min_interval_months), a publishable proration; every tier reachable.
- **F2 closed**: visit_basis_parts_rate removed; new_set_parts_rate (10 % / 5 % / 0 off parts when a Crestline tire set went on within 30 days, by line) — every tier occupied by real customers.
- **F3 closed**: request_age_anchor now divides by the pending request's age (≤ 7 days → its registration date, or the latest withdrawn request's; > 7 days → the cancellation date). The fall-through is reachable (a request left pending more than a week), and a "date honoured if confirmed within a week" rule is publishable. Its label stays borderline (O2: it chooses which recorded date the age runs to; carried as observation, consistent with round 1).
- **F4 closed**: protection_package_forfeit removed; plan_mileage_usage_charge (7.50 / 15.00 by miles run under the plan) is a normal service-contract usage charge.
- **F5 closed**: loyalty_count_window removed (count fixed at trailing 24 months inside the loyalty rate); protection_credit_basis is an honest method (count × per-tire credit vs a flat credit vs none).
- New/changed factors checked for realism, reachable tiers, honest labels: advance_booking_credit (scheduling incentive; walk-in fall-through reachable), new_set_parts_rate, plan_mileage_usage_charge, household_service_currency (credit for a recently used household plan), renewal_grace_rate (now count-only; grace applied outside the factor) — all pass. O1 (two-way price lock) closed by the lower-of tier.
- Factor independence: no factor binding reads another factor's binding (checked for every binding of all 31 factors; shared reads are only non-factor bindings such as wo_date, listed_parts, t_install, src_date, fee_*), and no factor binding assembles `result`. Renewal's grace gate moved from inside renewal_rate to the non-factor `granted_rate`.

### findings (round 2)
- F1–F7: closed (F7: labor and readjustment card windows now worded "up to the plan desk's pricing / booking", = NOW in compute; the other four card ladders already anchored on the handling day).
- New charter-level defects: none found.
- Observations still open (no rework required): O2 (request_age_anchor label borderline), O3 (commercial-use alignment as interval anchor — latent in base too), O5 (claimed event types without extended policy), O6 (base order sentence in one_per_vehicle), O8 (recalibration carve-out not record-visible).

### closing_checklist (round 2)
Written 2026-10-15 after both round-2 reveals. **Difficulty closes at the source layer.**
- 0.md, 1.md carry revision_1 (untouched) and revision_2, each with a PASS comparison.
- All six extended policies covered; task scopes disjoint (task 0: labor, parts, cancellation, household; task 1: readjustment, renewal); tools/GT closed; uuid8s independent (tool module unchanged).
- Trees: task 0 n = 3, value_input 2, user writes 2, labor/parts commute with identical terminal state; task 1 n = 1, value_input 1, user write 1; difficulty graph acyclic.
- Every computation: 4–6 factors, ≥ 2 parameter and 1 method, self-sufficient baseline giving a definite non-gold number; per task ≥ 1 multi-source and ≥ 1 cross-difficulty factor with seeded rows; every factor bears weight; ladders realistic, tiers reachable, labels honest (O2 borderline, observation); factors independent.
- Round-1 items F1–F7 closed; no new defect; open observations only (O2, O3, O5, O6, O8).
- Gates on the final form: coordinator's round-2 snapshot (all d_gates green; validate_scenario / traceability red only on pre-render items, out of scope); not re-run by the auditor.

## revision_3

### charter_global_frozen (round 3)
- Inputs (snapshot_r3.txt): charter ed09e0e1eeb33ad79c8c7aa28b1595d0f8e2b2f225a287a66841fdd6b9cee8fe (changed → all sections re-derived), task_tools.py 04e41c28… (changed: only the confirm docstring), views unchanged (974e0521…, ef0cf8d8…). Base copy still verbatim. Written before the round-3 reveal.
- Also read (as allowed by the brief): `audits/render_source/alignment/notes.md` and the source-side/XF parts of `audits/policy_kb/alignment_plan_service/{0,1}.md`. contamination_disclosure: the KB file 1.md shows a round-2 readjustment figure (16.25, already known from round 2); no round-3 figure was seen before the freeze.

### item closure (source)
| item | status | evidence |
|---|---|---|
| note 1 / SS-1 (overwrite keeps retired clause) | closed | labor replaced_by now restates in full "the purchase-day alignment is plan_included with charge_amount 0.00, and every other alignment … plan_included … when alignment_msr_interval_reached is true … charged member_early_alignment_price … before the interval is reached"; readjustment replaced_by restates "every other readjustment has free labor (charge_amount 0.00) and charges the parts it needs … under the parts warranty only when the part itself failed within parts_warranty_months and parts_warranty_miles" |
| note 2 / XF-i,j,k (grace gates the renewal rate) | closed | grace_period_anchor now decides its own `reinstatement` (0 inside grace, reinstatement_charge outside), added in `result`; renewal_usage_rate reads only the included count; no `granted_rate` |
| note 3 / XF-a..h, XF-l (assembly sentences naming other factors) | closed | each policy now ends "Every reduction and credit [deduction, fee and charge / rate and credit / reduction, credit and charge] this policy states is worked out on its own and taken off [applied to] the pricing base / kit charge / purchase_price / plan_price / parts amount"; percentage reductions are additive percentages of one base quantity (`reductions = base * (a + b)`), credits subtracted in `result` |
| XF-d, XF-f | closed | new-set reduction is "a percentage of the kit charge" (no installation labor); installation labor "is charged on the work order as part of the parts charge" |
| XF-S | closed | readjustment replaced_by no longer says "as this policy provides" |
| note 4 | closed | "the Plus 36-Month certificate's tires counting when the customer holds both kinds" (= compute) |
| note 5 | closed | rule "a withdrawn request registered on or before the day the request awaiting confirmation was registered" + compute `DAYS(withdrawn_at, pending_at) >= 0`. Residual O9: compute reads the latest withdrawn request overall, the rule "the latest such"; they differ only if a withdrawn request is registered after the pending one while an earlier one exists — no such row in any world |
| note 6 | closed | `td_share_sum` counts tire-day alignments per type |
| note 7 | closed | readjustment baseline.params = [] |
| note 8 | partly | docstring now "positive; the amount is never negative and is 0.00 when the refund works out to nothing" — "positive" still sits beside 0.00 (observation O10; moves nothing) |
| SS-3 | to be checked after reveal (GT prose) |
| SS-4 | kept, base law = O6 |
| CP-1 | kept; tires.yaml states alignment_check_included true for Grand Touring 60K (line 306) and Highway Terrain LT 65K (line 370) — source-consistent |

### factor structure and independence (round 3)
- Counts: labor 6 (5 P / 1 M), parts 4 (3/1), refund 5 (4/1), household 5 (4/1), renewal 6 (5/1: renewal_usage_rate, readjustment_day_credit, cardholder, road hazard, tire bundle / grace_period_anchor M), readjustment 5 (4/1). Ladders 3 tiers, distinct, fall-through = baseline, all reachable; labels honest (O2 unchanged).
- Independence: no factor binding reads another factor's binding; every combination happens in a plain binding (`reductions`, `deduction`) or `result`. The rule sentences of the percentage reductions name only the computation's own base quantity (pricing base, kit charge, parts amount, processing fee, plan_price, each defined in baseline.rule); where a method factor changes how that base quantity is reached, the reduction still reads only the quantity's name — accepted as the computation's common vocabulary, not a reference to another factor.
- Realism of the changed pieces: reinstatement charge for a renewal outside the grace period (a late-renewal fee); renewal rate by usage alone; additive percentage reductions on one base — all publishable.
- Baselines: renewal baseline now "plan_price, plus a reinstatement charge … when the renewal comes more than grace_days_after_expiry calendar days after the expiration_date"; readjustment "parts amount … the parts charge is the parts amount"; parts "kit charge … plus steering_angle_reset_charge" — each sentence in its rule, each self-sufficient.
- Prerequisite graph/sentences: unchanged (E2–E5 verbatim; acyclic; labor and parts still independent).
- Override declarations: as round 2, plus the two restated complements above. No new undeclared override.
- New defects: none found. Open observations: O2, O3, O5, O6, O8, O9, O10.

### closing_checklist (round 3)
- Both tasks PASS on revision_3 with blind = GT on every write, factor figure and closure figure; notes 1–7, XF-a..l, XF-S, SS-1, SS-3 closed; note 8 partly (O10, docstring wording only); SS-4 / CP-1 kept as stated (no defect).
- Scopes disjoint and complete; trees valid; every computation 4–6 factors with ≥ 2 P and 1 M, honest baselines, all factors bearing weight, independent, realistic.
- Open observations only: O2, O3, O5, O6, O8, O9, O10. Gates: coordinator's snapshot_r3 (7/7 OK, traceability OK); not re-run by the auditor.
VERDICT revision_3: task0=PASS task1=PASS charter=CLEAN
