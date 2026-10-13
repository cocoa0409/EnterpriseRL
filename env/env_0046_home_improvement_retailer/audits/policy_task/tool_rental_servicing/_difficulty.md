# Policy-task audit — tool_rental_servicing / charter-global

## charter_global_frozen

- Freeze time: 2026-10-08T07:39Z (written before any task's derivation and before any GT reveal; nothing in this section is derived from a revealed GT field).
- Auditor: independent policy-task auditor (Claude agent, erl-task-policy-audit); not the author of the artifacts.
- Frozen inputs (sha256, verified on disk at 2026-10-08T07:33Z, equal to the coordinator's brief):
  - `tasks/tool_rental_servicing/rental.extended.yaml` cf7b46b069ad88537eb4df19ba813c174b2eeaf750a9370820a0766e8112393b
  - `tasks/tool_rental_servicing/task_tools.py` 713af9217501b56d6f83b5f524f3dfbfb4f110f978cd2faee151d8da32f6d033
  - masked views `/tmp/e46/views/tool_rental_servicing/task_0.blind.json` 46bd63fc…5dbbe, `task_1.blind.json` f24dc0b7…a85e
- Fields permitted for this section: blueprint (`blueprint.yaml`, `db_schema.json`, `share_tools.py`, `products/rental.yaml`, and the parameter / event declarations of `products/pro.yaml`, `trade.yaml`, `card.yaml` read by the cross-category bindings), the extended charter, `task_tools.py`, the erlbench DSL evaluator in `skills/erl-task-instantiate/scripts/check_compute.py` (to fix what CFIELD / XCOUNT / MONTHS / DAYS / RND mean).
- Fields masked: every field of `tasks/*.json` other than `frozen_time`, `user_scenario`, `initial_state` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure); no existing audit of any difficulty was opened.

### Entry conditions (Step 0)

Gate snapshot supplied with the brief: check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cross_fire SCOPE OK; check_cache_diff INFO; check_traceability NOT OK (explained by the coordinator as depending on the unrendered KB — only hidden tool names fail). Masked views supplied with hashes. Inputs complete. Traceability NOT OK is recorded as an entry observation: it is outside the four relationships of this audit and is re-judged after KB rendering.

Base section verbatim check: `diff blueprint/products/rental.yaml` against lines 1-1058 of the extended charter — identical (only the extended header follows). Base copy is verbatim.

### policy_conflict_scan

Extended policies (7) and their claims:

| id | target_tool (owner) | computes | subject | task |
| --- | --- | --- | --- | --- |
| rental_ext_probuild_rental_discount (A) | post_probuild_rental_discount_391bfaed (agent) | discount_amount | rental_pro_discount_applied | 0 |
| rental_ext_engine_overtime_charge (B) | bill_engine_overtime_13bb4269 (agent) | overtime_amount | rental_fee_charged / overtime_hours | 0 |
| rental_ext_downtime_credit (C, root) | accept_downtime_credit_2dc14db7 (user) | credit_amount | rental_malfunction_credit_issued | 0 |
| rental_ext_damage_deductible (D) | bill_damage_deductible_c7701c46 (agent) | deductible_amount | rental_fee_charged / damage_deductible | 1 |
| rental_ext_missing_accessory_charge (E) | bill_missing_accessories_12fefdd6 (agent) | accessory_amount | rental_fee_charged / missing_accessory | 1 |
| rental_ext_refuelling_charge (F) | bill_refuelling_charge_2bf37336 (agent) | fuel_amount | rental_fee_charged / fuel_charge | 1 |
| rental_ext_protected_damage_adjustment (G, root) | accept_damage_adjustment_c3a91d5f (user) | adjustment_amount | rental_charge_adjusted | 1 |

(Task assignment read from the charter's own `# task 0` / `# task 1` section comments and the `prerequisite` graph, not from any task file.)

- Overlapping subjects: B, D, E, F all write `rental_fee_charged` but each on a distinct `fee_type` (overtime_hours / damage_deductible / missing_accessory / fuel_charge); no two policies set the same quantity.
- Triggers: all `state_due`; none conflicts with another's eligibility.
- Two extended policies supersede the same base clause (rental_damage_protection sentence 2, "With damage protection, accidental damage found at inspection is covered up to …"): D replaces its deductible half, G its above-limit-repair half. They govern different quantities (the deductible line vs. the adjustment of the damage_repair line), so the merged semantics are unique; recorded as an observation (O-1), not a conflict.
- Cross-category read boundaries: A reads pro + trade; B reads trade + pro; C reads trade + pro; D, E, F, G read card. All reads are of other categories' holdings / ledgers through the declared `cross_category` entries; no policy writes outside `rental_*`.
- Terminal states: each tool books one line and moves `balance_due`; none changes agreement `status`, so no two policies reach incompatible terminal states.
- Scope: task 0 ⇒ {A, B, C}; task 1 ⇒ {D, E, F, G}. Pairwise disjoint; jointly complete over the 7 extended policies; every subject event type is in the blueprint claim for tool_rental_servicing (rental_fee_charged, rental_pro_discount_applied, rental_malfunction_credit_issued, rental_charge_adjusted). PASS.

### rule_compute_equivalence

Swept every compute binding against its `compute_basis` quotation and every rule sentence back to a binding. Each quotation is verbatim a sentence of the policy's own `rule` (checked for all 7 policies). Each declared factor's ladder tiers are sentences of the rule and branches of its `decides` binding; no tier lives only in compute and no branch of a `decides` binding is absent from the rule.

Findings (charter-global; demonstrated on a stated situation; each task file checks whether its own world reaches the divergence):

- **F-A1 (SOURCE-POLICY RED, charter-global): A's compute gates every point on a non-zero tier percentage, which no rule sentence states.** Compute: `rate_pct: "(tier_pct + pc_points + tenure_points + late_points + spend_points + lead_points) if tier_pct > 0 else 0"` and `result: "RND(discount_raw, 2) if rate_pct > 0 else 0"`. Rule: "The ProBuild discount rate of the agreement is the rental discount percentage of the ProBuild tier the membership holds. Points added or taken away by the rules below change the ProBuild discount rate of the agreement point for point." Situation: active ProBuild Bronze member (pro.yaml `rental_discount_pct: 0`) active on the checkout date, class with `pro_discount_eligible: true`, active Pro Credit account with no returned payment (+1 point), 400.00 of daily-only rental time. Rule ⇒ rate 0 + 1 = 1 %, discount 4.00. Compute ⇒ tier_pct 0 ⇒ rate_pct 0 ⇒ 0.00. Two conclusions in one situation; the compute invents a basis ("points only apply above a 0 % tier"). Bears on task 0 only if its renter's tier is Member or Bronze (see 0.md).
- **F-A2 (SOURCE-POLICY RED, charter-global): A's eligibility reads the membership's *current* status, the rule its status *on the checkout date*.** Compute: `member_ok: "1 if (EXISTS('pro', status='active') and P('pro_discount_eligible') and DAYS(CFIELD('pro','enrolled_date'), F('checkout_at')) >= 0) else 0"`. Rule: "A renter whose ProBuild membership was active on the checkout date …"; "A renter without a ProBuild membership active on the checkout date … receives no discount." Situation: membership active at checkout, suspended since (pro_suspended after checkout) ⇒ rule grants the discount, compute gives 0; or membership suspended at checkout and reinstated since ⇒ rule 0, compute grants. Bears on task 0 only if its membership history crosses the checkout date (see 0.md).
- Single-account readings (observation O-2, charter-global; becomes a RED only where a task world seeds two accounts): CFIELD returns the first holding of the category (`hs[0]`, check_compute.py `CFIELD`), and XCOUNT/XSUM read every holding the customer owns. Rules speak of "the renter's Ridgeline Pro Credit account" (A, B, C) and "the renter's Ridgeline Consumer Credit account" (D, E, F, G; the card category includes Project Loans). With one account per category the readings coincide.
- A's "ProBuild spend credited to the membership from tool rentals" and C's "tool rental spend postings" are computed over `pro_spend_posted` only, ignoring `pro_spend_reversed` rows (observation O-3; bites only where a tool_rental reversal is seeded inside the window).
- D's "shows one or more late fees assessed in the last 12 months" counts `card_fee_assessed/late_fee` rows irrespective of a later `card_fee_reversed` with `reversal_reason posting_error` (observation O-4; bites only where such a reversal is seeded).
- G's inherited base window (rental_damage_disputes "The dispute must be filed no later than damage_dispute_days calendar days after the equipment was returned") is not tested in G's compute (`result` gates only on `approved_disputes >= 1`, DP elected and `already_adjusted == 0`); G's rule also selects the disputed charge as "a damage repair charge named by a damage dispute" while compute takes `MAX('rental_charges','amount', event_type='rental_fee_charged', fee_type='damage_repair')` without reading `disputed_charge_id` (observation O-5; bites only where the world seeds a late filing or two damage_repair lines).
- No other divergence: windows ("fewer than 12 whole calendar months before the day the … is posted/billed/booked") map to `_within` = `0 <= MONTHS(date, NOW) < 12`; calendar-day comparisons map to `DAYS` on date parts; caps/floors (`MX(0, …)`, `MN(…, repair_cost_d)`) each have a sentence; rounding is "once at the end" everywhere and each compute rounds only in `result`.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (table above). PASS.
- Docstrings: each describes one business action on one agreement; none names another tool, none states a position in a sequence relative to another action, none validates a condition. The word "after" occurs only in the receipt description ("the agreement's balance after the posting / after billing / after the credit / after the adjustment"), describing this call's own result, not a sequence among actions — observation O-6.
- Tool bodies: every function does `round(float(amount),2)`, `ctx.find` the agreement, `ctx.create` one `rental_charges` row, `ctx.update` balance_due — no status check, no refusal, no hint, no aggregate (verified by reading all 7 bodies in task_tools.py lines 11-295). The tool layer judges no prerequisite and no eligibility. PASS.
- uuid8s: 391bfaed, 13bb4269, 2dc14db7, c7701c46, 12fefdd6, 2bf37336, c3a91d5f — seven distinct values, no shared prefix or suffix, no sequential pattern, no copy-with-new-tail. PASS.

### prerequisite_graph

- `prerequisite` filled on all 7 policies (A, B, D, E, F: `[]`; C: 2 edges; G: 3 edges). PASS.
- Every `problem` is an extended policy id in this file, none a base policy, none self. Edges: C←A, C←B, G←D, G←E, G←F. Acyclic (A, B, D, E, F have no out-edges). PASS.
- `policy_source` verbatim in the blocked policy's own rule: C←A "The downtime credit is fixed only after the agreement carries the ProBuild rental discount entry owed on its rental time." (C rule sentence 2); C←B "The downtime credit is not worked out until the agreement carries the engine overtime charge owed for its hour meter reading at return." (C rule s3); G←D "The adjustment on an approved damage dispute is fixed only after the agreement carries the damage deductible line owed for the incident." (G s2); G←E "No adjustment on an approved damage dispute is booked until the agreement carries the missing-accessory charge owed from the return inspection." (G s3); G←F "Before the adjustment on an approved damage dispute is worked out, the agreement must carry the refuelling charge owed for its fuel reading at return." (G s4). All locatable. PASS.
- `form: state` on all 5 edges; no `fallback_reason`, correctly. PASS.
- `kind: value_input` on all 5; `gate` bindings exist in the blocked compute: `disc_posted`, `ot_posted` (C), `ded_b`, `acc_b`, `fuel_b` (G); each enters the blocked result arithmetically (`net_daily`, `protected_cost`). PASS.
- `resolved_by` equals the depended-on policy's `target_tool` on every edge, and that tool creates exactly the row the gate binding sums (event_type / fee_type match: rental_pro_discount_applied; fee_type overtime_hours; damage_deductible; missing_accessory; fuel_charge). PASS.
- `condition` vs sentence strength: each condition is scoped ("For a renter whose ProBuild membership was active…", "For metered equipment…", "When the return inspection counted accessories not returned…", "When the fuel level at return is below…") exactly as the sentence's "owed" qualifier scopes it. Neither strengthened nor weakened. No authoring-viewpoint phrasing. PASS.

### prerequisite_sentences

Four-point test, each edge:

| edge | connective | waited-on state (record-visible) | no tool / id / snake_case | strength = condition | writers of that state in this difficulty |
| --- | --- | --- | --- | --- | --- |
| C←A | "only after" | agreement carries the ProBuild rental discount entry (rental_charges row event_type rental_pro_discount_applied) | yes | yes ("owed on its rental time") | only post_probuild_rental_discount_391bfaed |
| C←B | "not … until" | agreement carries the engine overtime charge (fee line overtime_hours) | yes | yes ("owed for its hour meter reading at return") | only bill_engine_overtime_13bb4269 |
| G←D | "only after" | agreement carries the damage deductible line (fee line damage_deductible) | yes | yes ("owed for the incident") | only bill_damage_deductible_c7701c46 |
| G←E | "not … until" | agreement carries the missing-accessory charge (fee line missing_accessory) | yes | yes ("owed from the return inspection") | only bill_missing_accessories_12fefdd6 among agent/user writes; see O-7 |
| G←F | "Before … must" | agreement carries the refuelling charge (fee line fuel_charge) | yes | yes ("owed for its fuel reading at return") | only bill_refuelling_charge_2bf37336 |

Derivations (sentence + records + depended-on rule → resolving action, single reading):
- C←A: the reader of C finds "ProBuild rental discount entry"; the only policy whose rule produces "one ProBuild discount line" is A ("The discount is posted once per agreement as one ProBuild discount line"); the record check is a rental_charges row of event_type rental_pro_discount_applied on the agreement. One reading.
- C←B: "engine overtime charge … for its hour meter reading at return" ↔ B ("billed once per agreement at return as one overtime line"). One reading.
- G←D / G←E / G←F: "damage deductible line" ↔ D ("billed once per agreement as one deductible line"); "missing-accessory charge … from the return inspection" ↔ E ("billed once per agreement as one missing-accessory line"); "refuelling charge … for its fuel reading at return" ↔ F ("billed a refuelling charge once per agreement as one refuelling line"). One reading each.
- No second wording, tool name or other problem's id in C's or G's rule; A, B, D, E, F's rules do not restate the sentences. PASS.
- Undeclared cross-problem orders in rules: none. "before" in G ("so they are taken off before the coverage limit applies"), C ("The extra days are added to the lost days before the multiplication") and B/C/D/E/F/G ("one after the other") are intra-computation orders, not cross-problem. The base rule rental_damage_protection ("charged on rental_msr_time_charges (rental time after the ProBuild discount and malfunction credits …)") states a value ordering between the damage-protection charge and the discount / malfunction credit; it grounds no edge and no task tree rests on it — observation O-8 (its per-task bearing is checked in 0.md).
- O-7: the base event `rental_inspection_recorded` carries a system trigger `rental:rental_fee_charged when {inspection_outcome: missing_accessory} map {fee_type: missing_accessory}`. A seeded inspection with that outcome could therefore already carry a system-posted missing_accessory line, satisfying G←E at the opening. Checked per task (1.md).

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (finding half only; per-task consequence in each task file):

- A vs rental_agg_pro_relationship: s1 (holdings change deposit and rate) followed; s2 (deposit waiver) not touched; s3 ("at the discount percentage of the ProBuild tier held on that date") superseded and declared. vs rental_pro_discount: s1 superseded and declared; s2 (rental time only, never DP/fees/deposits/lost equipment) followed (A rule s-last); s3 (weekend special exclusive) followed (A s1 "leaving out any rental time billed at the weekend special"); s4 (no active membership on checkout date, incl. enrolling after, ⇒ none) followed (A s3). vs rental_time_billing: no sentence handled differently. Declared replacement "The ProBuild discount rate of the agreement is the rental discount percentage of the ProBuild tier the membership holds" drops "on that date" — whether "holds" means now or at checkout is a second reading only where the tier changed after checkout (checked in 0.md).
- B vs rental_return_fees: s4 (engine overtime) superseded and declared; s1-s3, s5 untouched. vs rental_reservations, rental_damage_protection, rental_delivery, rental_overdue_and_conversion, rental_time_billing: no sentence governs the overtime quantity; followed.
- C vs rental_malfunction: s1, s2 followed; s3 (full-credit hours / report-to-return credit at the same rates) superseded and declared — the replacement changes both the full-credit trigger (within malfunction_full_credit_hours hours → "on the checkout date") and the valuation (rental time → lost days × net daily cost incl. overtime less discount); both lie inside the superseded sentence. s4 (misuse ⇒ none; one report ⇒ at most one credit) followed (C s1 "found no damage caused by misuse … booked once per agreement"). vs rental_time_billing, rental_pro_discount, rental_return_fees: followed.
- D vs rental_damage_protection: s2 superseded and declared; s3 exclusions (theft, tires/tracks, misuse) followed by D's restriction to "accidental damage" (damage_cause enum separates accidental / misuse / theft_or_loss / tires_tracks); s4 (without DP the full repair cost) followed; s5 followed. vs rental_return_fees s5 followed; others untouched.
- E vs rental_return_fees: s2 superseded and declared; its cleaning half restated verbatim in substance in E s1 ("still incurs the class cleaning fee"). vs rental_damage_protection s5 ("never covers … missing accessories") followed.
- F vs rental_return_fees: s3 superseded and declared; others untouched.
- G vs rental_damage_disputes: s1-s3 followed (s2 window inherited; see O-5), s4 ("for the amount approved …") superseded and declared. vs rental_damage_protection s2 superseded and declared (see O-1); s3 (misuse / theft / tires-tracks billed in full, not covered) is not restated in G's rule and is not overwritten, so it is inherited: an approved dispute on a misuse charge would be adjusted under G's compute but not under the inherited base sentence (bites only where the disputed repair is not accidental; checked in 1.md). vs rental_return_fees: followed.
- Disguised forms: anonymous intermediate — none found beyond those inside declared superseded sentences; 0/1 multiplier — none on a base-fixed amount (A's `tier_pct > 0` gate is a rule/compute divergence, F-A1, not a base override); dropped branch — none (no base branch that an extended selector fails to produce).
- Undeclared overrides: none found. PASS (findings half).

### factor_ladders

| policy | factor | label | decides | tiers (fall-through last) | distinct outcomes | multi-source | cross_difficulty | stated in rule |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A | pro_credit_standing_points | parameter | pc_points | +1 / +0.5 / 0 | yes | yes (trade account status ∧ trade_transactions count) | trade | yes |
| A | membership_tenure_points | parameter | tenure_points | +1 / +0.5 / 0 | yes | no (enrolled_date vs checkout) | (pro holding, labelled null) | yes |
| A | late_return_points | parameter | late_points | −1 / −0.5 / 0 | yes | no | null | yes |
| A | rental_spend_points | parameter | spend_points | +1 / +0.5 / 0 | yes | no | pro | yes |
| A | booking_ahead_points | parameter | lead_points | +0.5 / +0.25 / 0 | yes | no | null | yes |
| A | long_rental_bands | method | discount_raw | cliff / marginal bands / flat | yes (three algorithms) | no | null | yes |
| B | shift_allowance_convention | method | allowance | per-period shift hours / calendar-day count / per billed day | yes | yes (period rows ∧ agreement dates) | null | yes |
| B | pro_credit_volume_hours | parameter | bonus_hours | 8 / 4 / 0 | yes | no | trade | yes |
| B | malfunction_diagnostic_hours | parameter | diag_hours | 4 / 2 / 0 | yes | yes (rental_requests ∧ inspection row) | null | yes |
| B | account_overtime_percentage | parameter | ot_pct | 9 / 11 / class pct | yes (class pct 12.50 on both metered classes) | yes (trade status ∧ pro tier) | trade | yes |
| B | late_return_multiplier | parameter | late_mult | 1.5 / 1.25 / 1 | yes | no | null | yes |
| B | rental_spend_multiplier | parameter | spend_mult | 0.90 / 0.95 / 1 | yes | no | pro | yes |
| C | lost_day_counting | method | lost_days | inclusive count / to due-back / report-to-return | yes | delivery flag ∧ dates (same agreement row) | null | yes |
| C | account_goodwill_days | parameter | goodwill_days | 1 / 0.5 / 0 | yes | yes (trade status, pro tier — disjunction/conjunction) | trade | yes |
| C | long_outage_days | parameter | disruption_days | 0.5 / 0.25 / 0 | yes | no | null | yes |
| C | repeat_failure_multiplier | parameter | repeat_mult | 1.20 / 1.10 / 1 | yes | no | null | yes |
| C | probuild_rental_activity_multiplier | parameter | loyalty_mult | 1.10 / 1.05 / 1 | yes | no | pro | yes |
| C | pro_credit_rental_volume_multiplier | parameter | volume_mult | 1.05 / 1.02 / 1 | yes | no | trade | yes |
| D | repair_size_method | method | sev_amount | class ded + 2 % above 10,000 / 25 % of repair / class ded | yes | no | null | yes |
| D | consumer_credit_standing_multiplier | parameter | card_mult_d | 0.60 / 0.85 / 1 | yes | yes (card status ∧ card_transactions) | card | yes |
| D | cardholder_tenure_multiplier | parameter | tenure_mult_d | 0.90 / 0.95 / 1 | yes | no | card | yes |
| D | usage_intensity_multiplier | parameter | usage_mult | 0.90 / 1.10 / 1 | yes | metered flag ∧ meter/period rows | null | yes |
| D | booking_ahead_deductible_multiplier | parameter | lead_mult_d | 0.95 / 0.975 / 1 | yes | no | null | yes |
| E | accessory_counting | method | charged_count | ceil(n/2) / n−1 / n | yes | no | null | yes |
| E | consumer_credit_tier_multiplier | parameter | card_mult_a | 0.75 / 0.90 / 1 | yes | no (status ∧ variant of one row) | card | yes |
| E | attachment_length_surcharge | parameter | length_mult | 1.20 / 1.10 / 1 | yes | no | null | yes |
| E | heavy_repair_multiplier | parameter | bundle_mult | 0.50 / 0.75 / 1 | yes | no | null | yes |
| F | refuel_pricing_method | method | fuel_core | 85 % full-tank + fee / eighths no fee / eighths + fee | yes | yes (fuel readings ∧ dates) | null | yes |
| F | consumer_credit_fuel_multiplier | parameter | card_mult_f | 0.90 / 0.95 / 1 | yes | no | card | yes |
| F | contract_fuel_multiplier | parameter | contract_mult | 0.90 / 0.95 / 1 | yes | no | null | yes |
| F | return_schedule_multiplier | parameter | schedule_mult | 0.90 / 0.95 / 1 | yes | no | null | yes |
| G | card_tier_protection_limit | parameter | tier_cover | +2,500 / +1,000 / 0 | yes | no | card | yes |
| G | protection_paid_limit | parameter | dp_cover | +1,000 / +500 / 0 | yes | no | null | yes |
| G | card_spend_limit | parameter | spend_cover | +1,500 / +500 / 0 | yes | no | card | yes |
| G | excess_sharing_method | method | kept_share | banded / 75 % / whole | yes | no | card | yes |
| G | prompt_dispute_reduction | parameter | prompt_credit | 100 / 50 / 0 | yes | no | null | yes |
| G | on_schedule_return_reduction | parameter | schedule_credit | 150 / 75 / 0 | yes | no | null | yes |

Counts per policy (factors / parameter / method): A 6/5/1, B 6/5/1, C 6/5/1, D 5/4/1, E 4/3/1, F 4/3/1, G 6/5/1 — all within 4-6, ≥2 parameter, ≥1 method. Per task: task 0 (A, B, C) has multi-source factors (A pc standing, B ot_pct, C goodwill) and cross-difficulty factors on trade and pro; task 1 (D, E, F, G) has a multi-source factor (D card standing) and cross-difficulty factors on card. PASS structurally.

- Bindings disjoint within each policy; every `decides` is an input, never `result`. PASS.
- Each factor's `baseline` equals its fall-through tier and equals what the policy's `baseline.rule` states for that input (A: no points, flat rate; B: class hours × billed days, class pct, no multipliers; C: report-to-return lost days or all rental days on a checkout-date report, no extra days, no multipliers; D: class deductible capped at repair cost; E: each missing accessory × class fee; F: eighths × price + fee; G: class coverage limit, whole excess kept). Each `baseline.rule` is a set of verbatim sentences of the rule and yields a definite number. PASS structurally.
- Labels honest: every `method` factor switches an algorithm (cliff vs marginal vs flat; per-period vs calendar-day vs per-billed-day allowance; three lost-day counts; three deductible formulas; three counting rules; three refuelling formulas; three excess-sharing rules); every `parameter` factor substitutes a number into a fixed formula. PASS.
- Real ladders (observations, no demonstrated consequence): D's small-repair tier (25 % of repair cost) puts a positive deductible on classes whose class deductible is 0.00 (Hand and Power Tools, Floor and Surface Care, Lawn and Landscape, Concrete and Masonry) — reachable only on those classes (O-9); B's calendar-day allowance gives a late returner more included hours than an on-time one (O-10); F's on-schedule multiplier discounts refuelling for an early return (O-11). Each is a coherent published convention a rental business could hold; none is shown to be a treatment no such business would publish, so none is a RED.

### findings

- **F-A1 — SOURCE-POLICY RED (charter-global, rule/compute equivalence)**: A's compute nullifies every point when the tier percentage is 0 (`rate_pct … if tier_pct > 0 else 0`); no rule sentence says so. Evidence and demonstrated two-way conclusion above. Affected: `rental.extended.yaml` → `rental_ext_probuild_rental_discount.compute.rate_pct` / `.result` vs `.rule` sentence 4. Bears on: task 0 (consequence judged in 0.md against its world).
- **F-A2 — SOURCE-POLICY RED (charter-global, rule/compute equivalence)**: A's compute tests the membership's present status, the rule its status on the checkout date. Affected: `rental_ext_probuild_rental_discount.compute.member_ok` / `tier_pct` vs `.rule` sentences 2-3. Bears on: task 0.
- Observations O-1 … O-11 as stated in the sections above (O-2 single-account reads, O-3 spend reversals ignored, O-4 reversed late fees counted, O-5 G's inherited filing window and disputed-charge selector not in compute, O-6 "after" in receipt descriptions, O-7 base system trigger for missing_accessory, O-8 base DP-after-discount ordering, O-9..O-11 ladder realism notes). Each becomes a per-task RED only where that task's world reaches it; each task file checks.
- Entry observation: check_traceability NOT OK pending KB render (outside this audit's four relationships).

## closing_checklist

Written 2026-10-08T07:52Z, after both tasks' frozen derivations and comparisons were on disk. This is the only section of this file derived after a reveal.

- Per-task files correspond one-to-one with the tasks: `0.md` (tasks/0.json sha256 aa3e7542…32e5), `1.md` (tasks/1.json sha256 947b412d…6ae7); this file alongside. First audit round; no older revision exists. Each comparison section carries its verdicts: task 0 PASS on all four relationships for its world; task 1 PASS on all four relationships.
- Coverage and scope: the 7 extended policies are covered (task 0: A, B, C; task 1: D, E, F, G); scopes, each spanning the whole problem tree, are pairwise disjoint; task tools and GT closed (each task's `charter_scope.task_tools` equals the target tools of its tree); seven independent, frozen uuid8s.
- Problem trees: task 0 — 2 prerequisite problems, 2 value_input edges, one user write, acyclic; task 1 — 3 prerequisite problems, 3 value_input edges, one user write, acyclic. The difficulty-wide graph (C←A, C←B, G←D, G←E, G←F) is a DAG with no cross-task edge.
- Factors: every computation declares a self-sufficient baseline and 4-6 factors with ≥2 parameter and ≥1 method; each task has a multi-source factor and a cross-difficulty factor (task 0: trade, pro; task 1: card); every ladder has three tiers stated in its rule with distinct outcomes; every factor bears weight on its task's world against an honest baseline, and each whole baseline gives a definite number ≠ gold (task 0: 212.00 / 0.00 / 1095.82; task 1: 500.00 / 120.00 / 105.00 / 10421.13), all equal to the GT `baseline_result` figures.
- Instantiation-stage gates: not re-run by the auditor (Step 0: the auditor cites the supplied snapshot). The audited artifacts are unchanged since that snapshot (extended yaml cf7b46b0…393b and task_tools 713af921…d033 re-hashed at close, equal to the brief), so the snapshot stands for the final form: all gates OK except check_traceability NOT OK, which the coordinator attributes to the not-yet-rendered KB and re-judges after KB render.
- Difficulty-level status: **not fully green at charter level.** Two charter-global SOURCE-POLICY RED findings stand in policy `rental_ext_probuild_rental_discount` (F-A1: compute zeroes every point when the tier percentage is 0, which no rule sentence states; F-A2: compute tests the membership's present status where the rule tests its status on the checkout date). Neither reaches either task's world, so neither task's scored solution is affected; they are defects of the shared charter that any future world with a ProBuild Member/Bronze renter, or a membership whose status changed across the checkout date, would expose. All other charter-global checks pass; per-task observations are listed in each task file.

## revision_2

### charter_global_frozen (revision 2)

- Written 2026-10-08T12:09Z, before either round-2 task view's derivation and before any round-2 GT reveal; nothing here is derived from a revealed GT field. Auditor: same independent auditor as round 1 (resumed after an account cut; nothing of revision 2 had been written before this section).
- Inputs (re-hashed on disk 2026-10-08T12:06Z, equal to the coordinator's brief): `rental.extended.yaml` 9276b1c2e6286734ceef1f9ffc6b1d67b77c9e3dad539fe7405eb09a0aa98ce9 (round 1: cf7b46b0…); `task_tools.py` 4c6ad7e1060660c656e17ebd964662cce7013ec02d7074174b2c4c217481b03b (round 1: 713af921…). Both changed, so every charter-global section is re-derived in full below (no carry-forward by reference).
- Entry conditions: gate snapshot supplied (all OK except TRACEABILITY NOT OK, pending KB render; CACHE-DIFF INFO); masked views supplied with hashes (`r2/task_0.blind.json` b5b66039…fa9, `r2/task_1.blind.json` 2b175828…f93b). Complete.
- Masked: all of `tasks/*.json` beyond the views; the reworker's claims were received by item id only and are verified here, not accepted.
- Base section: lines 1-1058 still verbatim equal to `blueprint/products/rental.yaml` (diff empty). Mechanical re-checks (`/tmp/e46audit/struct.py`, reads only the charter): every `compute_basis` quotation is a verbatim rule sentence of its policy; every `superseded_clause` is verbatim in its base policy's rule and every `replaced_by` verbatim in the extended rule; every `prerequisite.policy_source` verbatim in the blocked rule; every `baseline.rule` sentence is a rule sentence; compute bindings and `compute_basis` keys coincide (except the arithmetic intermediate `time_base`, unchanged from round 1).

### policy_conflict_scan (revision 2)

Unchanged in structure: same 7 extended policies, target tools, owners, computes, subjects and task partition (task 0 ⇒ A, B, C; task 1 ⇒ D, E, F, G); pairwise disjoint and jointly complete. B, C, D, E, F rules and computes are textually the round-1 ones (no edit found). Edits are confined to A (rule sentences 4-5, overwrite `replaced_by` of rental_agg_pro_relationship, compute `member_ok`, `tier_pct`, `member_months`, `rate_pct`, `result`) and G (three new rule sentences, the rounding clause, compute `disputed_charge`, new `in_window_j`, `accidental_j`, and `result`). No new overlap of subjects, triggers or terminal states. PASS.

### rule_compute_equivalence (revision 2)

Round-1 RED re-checks:
- **F-A1 — closed.** Rule now: "The ProBuild discount rate of the agreement is the rental discount percentage of the ProBuild tier the membership's record shows on the day the discount is posted, a percentage of zero included. Points added or taken away by the rules below change the ProBuild discount rate of the agreement point for point, whatever the tier's own percentage, and the rate never goes below zero." Compute: `rate_pct: "MX(0, tier_pct + … + lead_points) if member_ok == 1 else 0"`, `result: "RND(discount_raw, 2) if member_ok == 1 else 0"`. Round-1 situation re-run (active Bronze 0 %, +1 Pro Credit point, 400.00 daily-only): rule 1 % → 4.00; compute member_ok 1, tier_pct 0, rate 1 → 4.00. Agree. The `MX(0, …)` floor has its sentence ("the rate never goes below zero").
- **F-A2 — closed.** New rule sentence: "A membership counts as active on the checkout date when it was enrolled on or before the checkout date and its record shows it active, or shows it suspended or closed with the suspension or closing dated after the checkout date; a membership whose record shows it pending verification, or suspended or closed on or before the checkout date, does not count." Compute `member_ok` tests enrolled ≤ checkout and (status active, or suspended with `DAYS(checkout, suspended_date) > 0`, or closed with `DAYS(checkout, closed_date) > 0`). Round-1 situations re-run: active at checkout and suspended since → both grant; suspended before checkout → both refuse. Agree. Residual (observation R2-O1): a membership suspended on the checkout date and reinstated since shows `active` with no suspended_date, so the record-based definition counts it while base rental_pro_discount s4 ("A renter without an active membership on the checkout date … receives no discount", not superseded) would not; the pro schema keeps no reinstatement history (pro_activity has no lifecycle rows; `suspended_date` is "empty unless suspended"), so no seedable world can make the two readings differ. Not a RED.
- Observation **O-5 — closed.** G's rule now states "The disputed charge is the damage repair line the approved dispute names." and compute selects `rental_charge_id = LATEST('rental_requests','disputed_charge_id', …, request_type='damage_dispute', status='approved')`; the inherited window and the inherited misuse/theft/tires-tracks exclusion are now stated ("No adjustment is due under this rule when the approved dispute was filed more calendar days after the return date than the class's dispute window allows, or when the return inspection recorded a damage cause other than accidental, since misuse, loss or theft and tire or track damage stay billed in full.") and implemented (`in_window_j: DAYS(returned_at, approved dispute created_at) <= P('damage_dispute_days')` — inclusive, matching base "filing on the last day qualifies"; `accidental_j >= 1` in `result`). Agree.

New finding:
- **N-1 (SOURCE-POLICY RED, charter-global, rule/compute equivalence): G's rule now fixes the tie-break as half-up, its compute does not implement half-up.** Rule: "The adjustment is the disputed damage repair charge less the excess the renter keeps, rounded to the nearest cent once at the end, half a cent rounding up." Compute: `result: "RND(disputed_charge - kept_excess, 2) …"`, where RND is Python `round(float(x), n)` (check_compute.py `"RND": lambda x, n=2: round(float(x), n)`), i.e. round-half-to-even on the binary value. Situation: excess 1418.75 with the banded method → kept share 500 + 0.5 × 918.75 = 959.375, less 200.00 credits → kept excess 759.375; disputed charge 15840.00 → 15080.625, exactly representable in binary. Rule (half-up) ⇒ 15080.63; compute `round(15080.625, 2)` ⇒ 15080.62 (verified). Two conclusions in one situation. A tie at an odd-cent .xx5 that is not exactly representable may go either way under the compute depending on its binary value, so the compute matches the rule only by accident. The same holds for every other policy's `RND`, but only G's rule now states a tie-break, so only G's two faces conflict. Bears on task 1 only if its adjustment lands on a tie whose binary value rounds down (checked in 1.md revision_2).
- Other observations O-2, O-3, O-4 unchanged (texts unchanged). New minor observation R2-O2: G's `dispute_filed_at` (prompt-dispute factor) takes LATEST over all damage disputes while `in_window_j` and `disputed_charge` take the approved one; they coincide unless an agreement carries a later non-approved dispute.

### action_binding_and_uuids (revision 2)

- `(target_tool, computes)` unique per policy; uuid8s unchanged (391bfaed, 13bb4269, 2dc14db7, c7701c46, 12fefdd6, 2bf37336, c3a91d5f) — independent, unreused. PASS.
- Docstrings: the receipt wording is now "the agreement's resulting balance" / "the amount now owed on the agreement"; `grep -w -i 'after|before|first|then|once'` over task_tools.py returns no match. **O-6 closed.** No other tool named, no sequence stated.
- Tool bodies: unchanged logic in all 7 (round, find agreement, create one row, update balance_due; no check, refusal or hint). PASS.

### prerequisite_graph (revision 2)

Unchanged edges (C←A, C←B, G←D, G←E, G←F), unchanged `policy_source`, `form: state`, `kind: value_input`, gates (`disc_posted`, `ot_posted`, `ded_b`, `acc_b`, `fuel_b`), `resolved_by`, `condition`, `effect` (re-printed and compared). Acyclic; all sources verbatim in the blocked rules. PASS.

### prerequisite_sentences (revision 2)

The five sentences are unchanged and pass the four-point test as in round 1; each waited-on state still has exactly one writer in the difficulty. G's three new sentences state an eligibility (window, damage cause), the disputed-charge selector and the tie-break; none states a cross-problem order, names a tool or another problem. No depended-on rule restates a sentence. O-7 (base missing_accessory system trigger) and O-8 unchanged as observations. PASS.

### override_declarations (revision 2)

- A: the `replaced_by` of rental_agg_pro_relationship s3 now reads "… the ProBuild tier the membership's record shows on the day the discount is posted, a percentage of zero included." — declared; it makes explicit the posting-day tier reading that round 1 noted as a potential second reading (tier change after checkout). The new "counts as active" sentence operationalises "active on the checkout date" of rental_pro_discount s4 / the superseded s1 without changing it on any seedable world (R2-O1).
- G: base rental_damage_protection s3 (exclusions billed in full) is now followed explicitly; base rental_damage_disputes s2-s3 (window, counting) now followed explicitly. The superseded s4 and the superseded rental_damage_protection s2 unchanged.
- No undeclared override found. PASS (finding half).

### factor_ladders (revision 2)

Factor declarations of all 7 policies (ids, labels, decides, bindings, ladders, baselines, cross_difficulty) are textually as in round 1 (re-printed and compared); A's `baseline.rule` gained the "counts as active" sentence and the posting-day/zero-included rate sentence, both rule sentences, and still yields a definite number (flat tier percentage). Counts unchanged (A 6/5/1, B 6/5/1, C 6/5/1, D 5/4/1, E 4/3/1, F 4/3/1, G 6/5/1); multi-source and cross-difficulty coverage per task unchanged. Ladder-realism observations O-9 … O-11 unchanged. PASS structurally.

### findings (revision 2)

- F-A1 — closed (verified above). F-A2 — closed (verified above; residual R2-O1 observation).
- O-5 — closed; inherited misuse exclusion now stated and implemented. O-6 — closed.
- **N-1 — SOURCE-POLICY RED (new, charter-global)**: G's rule fixes a half-up tie-break that its `RND` compute does not implement (demonstrated above with 15080.625 ⇒ rule 15080.63, compute 15080.62). Affected: `rental.extended.yaml` → `rental_ext_protected_damage_adjustment.rule` (sentence "The adjustment is … half a cent rounding up.") vs `.compute.result`. Bears on task 1.
- Left as observations (verified unchanged): O-1, O-2, O-3, O-4, O-7, O-8, O-9, O-10, O-11; new R2-O1, R2-O2.

### closing_checklist (revision 2)

Written 2026-10-08T12:11Z, after both revision-2 task derivations and comparisons were on disk; the only post-reveal part of revision 2 in this file.

- Files: `0.md`, `1.md` each carry `revision_2` (frozen derivation, comparison, findings) below their untouched round-1 text; this file's round-1 text is untouched. Task files at round 2: tasks/0.json dc197c58…77aa, tasks/1.json 0372e7b4…94db.
- Round-1 REDs: F-A1 closed, F-A2 closed (verified by re-running round 1's demonstrating situations against the new rule and compute). Round-1 observations claimed closed and verified closed: O-5 (with the inherited misuse/theft/tires-tracks exclusion), O-6, T0-O1, T1-O2, T1-O3, T1-O4, T1-O5. Left as observations, verified unchanged: T1-O1, O-1, O-2, O-3, O-4, O-7 … O-11.
- No regression: every round-1 scored value, factor sensitivity, whole baseline and edge-skip figure is reproduced on the round-2 worlds and equals the round-2 GT.
- New defect: **N-1 (SOURCE-POLICY RED, charter-global)** — introduced by the T1-O2 rework: `rental_ext_protected_damage_adjustment`'s rule now says "rounded to the nearest cent once at the end, half a cent rounding up" while its compute rounds with `RND` (Python round, half-to-even on the binary value); on an exactly representable tie such as 15080.625 the rule gives 15080.63 and the compute 15080.62. It does not reach task 1's world (15080.565 rounds up under both). New observations R2-O1, R2-O2, R2-O3.
- Coverage, scope disjointness, tree shapes (task 0: 2 prerequisites / 2 value_input; task 1: 3 / 3; one user write each; difficulty graph a DAG), factor counts and weights, uuid8s: as in round 1, all PASS.
- Gates: not re-run by the auditor; coordinator's round-2 snapshot cited (all OK except TRACEABILITY NOT OK pending KB render; CACHE-DIFF INFO).
- Per-task verdicts (revision 2): task 0 **PASS**; task 1 **PASS**. Difficulty-level status: not fully green at charter level while N-1 stands (no task consequence).

## revision_3

### charter_global_frozen (revision 3)

- Written 2026-10-08T13:39Z, before any round-3 reveal; nothing here derives from a revealed GT field. Auditor: same independent auditor.
- Inputs re-hashed 2026-10-08T13:38Z, equal to the brief: `rental.extended.yaml` 74ca83c42c75053e68868b7c13c0776cb454e0185aa9a5611c9c55df1a668ad2 (round 2: 9276b1c2…) — changed, so re-derived below; `task_tools.py` 4c6ad7e1…03b — unchanged since round 2, so `action_binding_and_uuids (revision 2)` is carried forward by reference on that hash. Masked views `r3/task_0.blind.json` b5b66039…fa9 and `r3/task_1.blind.json` 2b175828…f93b are byte-identical to the round-2 views (`cmp`).
- Gate snapshot cited (all OK except TRACEABILITY NOT OK pending KB render; CACHE-DIFF INFO). Inputs complete.
- Base lines 1-1058 verbatim equal to `blueprint/products/rental.yaml`. Mechanical re-checks (`/tmp/e46audit/struct.py`): all `compute_basis` quotations, `replaced_by` sentences, `policy_source` sentences and `baseline.rule` sentences verbatim in their rules; every `superseded_clause` verbatim in its base rule; bindings ⇔ basis keys coincide.

### policy_conflict_scan / prerequisite_graph / prerequisite_sentences / override_declarations / factor_ladders (revision 3)

- Re-read in full. Policies A-F (rules, params, computes, factors, baselines, prerequisites, overwrites) are textually identical to revision 2. In G the only edits are: the prompt-dispute rule sentence now reads "A prompt dispute lowers the excess the renter keeps: when the approved dispute was filed within 3 calendar days of the return date, 100.00 dollars are taken off it; when the approved dispute was filed 4 to 7 calendar days after the return date, 50.00 dollars are taken off; when it was filed later, nothing is taken off." (its ladder's first tier now "the approved dispute was filed within 3 calendar days of the return date"); `dispute_filed_at` now filters `status='approved'`; `result` now rounds as `RND(int((disputed_charge - kept_excess) * 100 + 0.5 + 0.000001) / 100, 2)`.
- Consequently the revision-2 conclusions of `policy_conflict_scan`, `prerequisite_graph`, `prerequisite_sentences` (five edges, same sentences, single writers, no new cross-problem order — the new prompt sentence states none), `override_declarations` (no undeclared override) and `factor_ladders` (same factors, labels, tiers, baselines; G's prompt ladder still three disjoint tiers, stated in the rule, fall-through = baseline 0) hold unchanged. PASS.

### rule_compute_equivalence (revision 3)

- **N-1 — closed.** Rule: "… rounded to the nearest cent once at the end, half a cent rounding up." Compute now adds half a cent and truncates (`int(x × 100 + 0.5 + 0.000001) / 100`). Round-2 demonstrating situation re-run: 15080.625 ⇒ int(1508063.000001) / 100 = 15080.63 = rule (round-2 compute gave 15080.62). Task 1's tie 15080.565 ⇒ 15080.57 under both. Non-ties unchanged (15080.57 ⇒ 15080.57; 14870.00 ⇒ 14870.00; 0.29 ⇒ 0.29, guarding the float `0.29 × 100 = 28.999…`). The 10⁻⁶-cent guard cannot move a non-tie: every input of G is on the cent grid and its only fractions are ×0.50 and ×0.75 of cent amounts, so the unrounded adjustment is a multiple of 0.0025 dollars and never lies within 10⁻⁶ cent below a half cent except at an exact tie; the argument of `int` is positive because the kept excess never exceeds the disputed charge. No invented basis.
- **R2-O2 — closed.** `dispute_filed_at` now reads the approved dispute, matching `in_window_j` and `disputed_charge`, and the rule sentence and ladder now name "the approved dispute".
- R2-O1 unchanged (observation). Other policies' `RND` remain Python round under rules that state no tie-break ("rounded to the nearest cent") — no conflict of the two faces; observation as in round 1 (T1-O2 form), no task world reaches a tie in A-F.
- No new divergence found.

### findings (revision 3)

- N-1 — closed. R2-O2 — closed. R2-O3 concerns task 1's design_rationale (verified in 1.md revision_3 after reveal).
- R2-O1, O-1 … O-4, O-7 … O-11, T1-O1 remain observations.
- No new charter-global defect.

### closing_checklist (revision 3)

Written 2026-10-08T17:04Z (resumed after a session cut), after both revision-3 task comparisons were on disk.

- Files: `0.md`, `1.md` each carry `revision_3` (frozen derivation pre-reveal, comparison post-reveal) under untouched earlier text; this file's earlier revisions untouched. Task files at round 3: tasks/0.json 0b01b147…, tasks/1.json c19b0796….
- Round-2 RED: **N-1 closed** (rule half-up = compute half-up; demonstrating tie 15080.625 ⇒ 15080.63 under both; task 1's scored 15080.57 unchanged). R2-O2 closed; R2-O3 closed; R2-O1 left as observation (not seedable).
- No regression of any scored value: task 0 298.60 / 526.79 / 1491.69; task 1 284.78 / 24.75 / 111.60 / 15080.57; every `computations` sensitivity and baseline figure reproduced.
- **New defect R3-1 (SOURCE-CHAIN RED, task 1 proof fields)**: the N-1 fix moved two of task 1's edge-skip figures (skip deductible 14,938.17 → 14,938.18; skip refuelling 15,024.76 → 15,024.77, both half-cent ties now rounded up), but `prerequisite_closure.edge_load_bearing`, design_rationale and `argument_uniqueness_tracing` still state the old figures. Edges still bear weight. No charter-global defect is new in revision 3.
- Coverage, scope, tree shapes, factor structure, uuid8s: unchanged, PASS. Gates: coordinator's round-3 snapshot cited (all OK except TRACEABILITY NOT OK pending KB render); not re-run by the auditor.
- Per-task verdicts (revision 3): task 0 **PASS**; task 1 **SOURCE-CHAIN RED** (R3-1 only). Difficulty status: not yet passing the source-layer audit — charter-global checks are all green after N-1's closure; the one open item is R3-1 in task 1's proof fields.

## revision_4

### charter_global_frozen (revision 4)

- Written 2026-10-08T17:40Z, before any round-4 reveal. Auditor: same independent auditor.
- Inputs re-hashed 2026-10-08T17:39Z: `rental.extended.yaml` 74ca83c42c75053e68868b7c13c0776cb454e0185aa9a5611c9c55df1a668ad2 (byte-identical to the round-3 copy `/tmp/e46audit/ext_r3.yaml`); `task_tools.py` 4c6ad7e1060660c656e17ebd964662cce7013ec02d7074174b2c4c217481b03b (unchanged since round 2). Both shared inputs unchanged, so every charter-global section is carried forward by reference: `revision_3` (policy_conflict_scan / prerequisite_graph / prerequisite_sentences / override_declarations / factor_ladders, rule_compute_equivalence, findings) and, for the tool module, `revision_2` → `action_binding_and_uuids`. Grounds: the two hashes above.
- Masked views `r4/task_0.blind.json` b5b66039…fa9 and `r4/task_1.blind.json` 2b175828…f93b are byte-identical to the round-3 views. Gate snapshot cited (all OK except TRACEABILITY NOT OK pending KB render). Inputs complete.
- Task files changed: tasks/0.json 0b01b147… → 13dbd2a1…; tasks/1.json c19b0796… → 168c132c…. The reworker states only tasks/1.json proof fields changed; tasks/0.json's hash also moved, so both are re-compared after the reveal.
- Charter-global status carried forward: no open charter-global RED (N-1 closed in revision 3); observations R2-O1, O-1 … O-4, O-7 … O-11 unchanged.

### closing_checklist (revision 4)

Written 2026-10-08T17:41Z, after both revision-4 comparisons were on disk.

- Files: `0.md`, `1.md` each carry `revision_4` (frozen pre-reveal, compared post-reveal) under untouched earlier text; this file's earlier revisions untouched.
- Round-3 RED **R3-1 closed**: task 1's edge-skip figures now read 14,938.18 / 15,068.19 / 15,024.77 in every proof field, equal to the revision-3 compute through the framework evaluator.
- No regression: all scored values (task 0 298.60 / 526.79 / 1491.69; task 1 284.78 / 24.75 / 111.60 / 15080.57), every `computations` sensitivity and baseline, and every edge-skip figure reproduced. No new defect. New observation R4-O1: tasks/0.json's hash changed without a disclosed edit; every assertion in it re-verified.
- Charter and tools unchanged since round 3 (hashes above); no open charter-global RED; observations R2-O1, O-1 … O-4, O-7 … O-11, T1-O1 remain.
- Step-4 list: per-task files one-to-one with the tasks, every comparison section carrying PASS; 7 extended policies covered by pairwise-disjoint scopes; task tools and GT closed; seven independent uuid8s; trees of 2 and 3 prerequisites with 2 and 3 value_input edges, one user write each, difficulty graph acyclic; every computation with a self-sufficient baseline and 4-6 weight-bearing factors (≥2 parameter, ≥1 method; multi-source and cross-difficulty present per task), each whole baseline definite and ≠ gold. Gates: coordinator's round-4 snapshot cited (all OK except TRACEABILITY NOT OK, pending the KB render); not re-run by the auditor.
- Per-task verdicts (revision 4): task 0 **PASS**; task 1 **PASS**. **Difficulty status: passes the source-layer policy-task audit** (all four relationships PASS for both tasks, no open RED), with traceability still to be re-judged after the KB is rendered.
