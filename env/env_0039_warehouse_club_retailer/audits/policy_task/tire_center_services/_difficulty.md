# Policy-task audit — tire_center_services / charter-global

## charter_global_frozen

- Scenario: env/env_0039_warehouse_club_retailer; difficulty `tire_center_services`; category `tire`; M=2.
- Freeze hashes (sha256, verified on disk at audit start, equal to the brief):
  - `tasks/tire_center_services/tire.extended.yaml` beba27825a23785527f5696a7e9c71fa7683e9ceb9b4be2ee2181e15a6d5d7ab
  - `tasks/tire_center_services/task_tools.py` 9c222360a1fe7c45adedf6038cb5f189797b4c122cca1de7716ad093c1322481
  - masked views `audits/views/policy_task/tire_center_services/0.view.json` 638bdf8af819b1a07988c365c85112b8d7388c8bc4a0d95c43cc0071b05550f1; `1.view.json` f6c0863bf24a21dfa2fa18c51f3298a4bde18ec4a6b1b842f7f07d7965903f0e
- Freeze time: 2026-10-05T21:32Z. Auditor: Claude (erl-task-policy-audit, independent of the authoring agent).
- Fields read for this section: blueprint/blueprint.yaml, blueprint/products/tire.yaml, blueprint/products/membership.yaml (variant parameters only), blueprint/products/order.yaml (price_adjustment_window_days only), blueprint/db_schema.json (tire tables), blueprint/share_tools.py, the extended charter, task_tools.py, and `skills/erl-task-instantiate/scripts/check_compute.py` for the DSL primitive semantics (MONTHS/DAYS/LATEST/COUNT within_months/XCOUNT).
- Masked and unread at the time this section was written: tasks/tire_center_services/tasks/{0,1}.json in full (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), worklog.md (never opened), any earlier audit (none exists).
- This section contains nothing derived from a revealed GT.

### Entry conditions (Step 0)

Supplied with the brief and cited, not re-run: check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cross_fire SCOPE OK; check_traceability NOT OK, declared as expected because the KB docs/ are not rendered yet (outside this audit's four artifacts). Masked views with hashes supplied. Entry conditions complete.

### policy_conflict_scan

Five extended policies, each with a distinct written quantity:

| policy | subject / component | target_tool (owner) | computes |
| --- | --- | --- | --- |
| tire_ext_claim_fitting_charge | tire_service_charged / installation_package, source = treadwear claim entry | post_claim_fitting_charge_0bdb2547 (agent) | amount |
| tire_ext_treadwear_credit | tire_service_credited / treadwear_credit | post_treadwear_credit_0e44552f (agent) | amount |
| tire_ext_road_hazard_credit | tire_service_credited / road_hazard_credit | accept_road_hazard_credit_d64b14f0 (user) | amount |
| tire_ext_service_rotation_charge | tire_service_charged / rotation_balance | authorize_rotation_charge_d4760d29 (user) | amount |
| tire_ext_flat_repair_charge | tire_service_charged / flat_repair | post_flat_repair_charge_9a2582c0 (agent) | amount |

- Overlapping subjects: three policies write `tire_service_charged`, but on disjoint `charge_component` values; two write `tire_service_credited` on disjoint components. The base `tire_installation_charges` also writes `installation_package`, but only on the installation date for the whole set (`tire_installed` trigger, `tire_position: all_positions`); the claim fitting charge is per wheel and carries the claim entry as `source_event_id`. No overlap of object.
- Triggers/eligibility/time anchors: every extended policy inherits the base `tire_service_eligibility` gates (package installed, membership active) and, for the credits, the base road-hazard gates (term, tread above coverage end, replacement limit) and the treadwear gates (worn before warranty miles, rotation gap). No extended policy restates or weakens them. The rate ladders that read the same inputs (Plus status, tender) in different policies reach different values for different quantities (fitting vs rotation vs road hazard); no two govern one quantity.
- Cross-category read boundaries: every extended policy reads the membership presented on the tires' purchase (`order_holdings.membership_id`) and/or the purchase's tender and lines; none writes outside `tire_services`.
- Terminal states: each write adds exactly one `tire_services` row; no status changes. No conflict.
- Scope partition (derived from the prerequisite graph alone, see prerequisite_graph): component A = {claim_fitting → treadwear_credit → road_hazard_credit}; component B = {rotation_charge → flat_repair_charge}. Two tasks, two components: mutually exclusive and jointly complete provided task 0 claims A and task 1 claims B (confirmed per task from its world in the task files; the masked `charter_scope` is compared after reveal).
- Conflicts with base found here: see override_declarations (finding D-F1).

### rule_compute_equivalence

Swept per policy, binding by binding against `compute_basis` and back against every rule sentence.

- tire_ext_claim_fitting_charge: claim entry = LATEST tire_treadwear_adjusted by service_date ("most recent treadwear claim entry"); membership via CFIELD(order.membership_id); Plus = CPARAM plus_premium_usd > 0 ("plus_premium_usd above zero"); tenure MONTHS(opened_date, claim service_date) with the day-of-month rule (MONTHS implements "a month counts once its day of the month is reached"); replacement count = COUNT(road hazard) + COUNT(treadwear) ("together"); tender branch; one combined product ("multiplied together into one combined rate … multiplied once"); usage share = (claim odometer − install_odometer)/treadwear_warranty_miles; three-way usage method; single RND at the end. Every rule sentence has a binding and every binding a quotation. PASS.
- tire_ext_treadwear_credit: price paid (four tiers over XSUM of order_price_adjusted / order_rebate_credited unit_price on the purchase line for the item), replacement charge SUM(replacement_tire, source = claim), claim months, price-basis method, mileage factor (Plus / non-Plus with annual_fee_usd ≥ 65 / other), extended warranty miles and remaining share with zero guard ("zero for a tire model whose treadwear_warranty_miles is zero"), rotation count vs int(miles/5000) and int(miles/7500) ("rounded down to a whole number"), tread factor vs P(treadwear_claim_max_tread_32nds), DAYS(claim date, NOW) ("to the day the credit is booked"; the tool dates the credit today), single product then additive allowance then one RND. PASS.
- tire_ext_road_hazard_credit: latest road-hazard entry and its position/odometer/tread; wear % and usable tread share; treadwear count/id/charge/credit by wheel position; price basis three-way; mount odometer/date; warranty miles share; months on wheel; proration method; credit share full vs prorated at road_hazard_full_credit_max_wear_pct; sequence count "the current one included"; term left = term − MONTHS(install_date, replacement date); member share (Plus × visa); one product, one RND. The rule does not state the miles share for a zero-warranty tire, but the proration method never uses it there (tier 3 takes the tread share), so the compute guard is not an invented basis. PASS.
- tire_ext_service_rotation_charge: latest rotation entry; previous odometer = LATEST rotation_balance charge else install_odometer; work method three-way with rebalance_fee_per_tire_usd × tire_count or × tire_count/half_set; member rate (Plus ≥ 60 months; non-Plus business ≥ 60 months; other); loyalty COUNT(rotation_balance, within_months=12) with 0 ≤ MONTHS(date, NOW) < 12 ("a charge dated 12 or more whole months ago does not count"); tender; package age; one product; one RND. PASS.
- tire_ext_flat_repair_charge: latest flat-repair entry; earlier count = COUNT(same position) − 1 ("the current repair not counted"); work method three-way; bundle: SUM(rotation_balance, service_date = repair date) > 0 with tread ≥ 4; member: XCOUNT(membership_fee_charged on the presented membership); mileage from install_odometer; one product; one RND. PASS.
- Every declared factor's ladder tiers appear both as a rule sentence and as a branch of its `decides` binding, and vice versa (checked for all 24 factors). PASS.

### action_binding_and_uuids

- Each `(target_tool, computes)` is claimed by exactly one policy (table above). PASS.
- Tool bodies (task_tools.py lines 40-49, 76-85, 112-121, 148-156, 183-191) only round the amount and `ctx.create` one `tire_services` row; none reads policy state, refuses, errors or hints on an unmet prerequisite. PASS.
- Docstrings name no other tool, state no position in a sequence of writes, and add no confirmation/review/wait. They carry the phrase "read from … before the call" (lines 26, 30, 64, 66, 170) about where an argument is looked up — an ordering word about a read, not about another write (observation O-1).
- uuid8s: 0bdb2547, 0e44552f, d64b14f0, d4760d29, 9a2582c0. All distinct; no shared prefix beyond one hex digit, no sequence; none equals the first 8 hex of md5/sha1/sha256 of its verb_object name (checked). No evidence of reuse or batch derivation. PASS.

### prerequisite_graph

| blocked policy | problem | kind | gate | form | resolved_by |
| --- | --- | --- | --- | --- | --- |
| tire_ext_treadwear_credit | tire_ext_claim_fitting_charge | state_gate | tire_services.charge_component | state | post_claim_fitting_charge_0bdb2547 |
| tire_ext_road_hazard_credit | tire_ext_treadwear_credit | value_input | rh_tw_credit | state | post_treadwear_credit_0e44552f |
| tire_ext_flat_repair_charge | tire_ext_service_rotation_charge | value_input | fl_rotation_paid | state | authorize_rotation_charge_d4760d29 |

- `prerequisite` present on all five policies (`[]` on claim fitting and rotation). Every `problem` is an extended policy id of this file, never base, never self. Graph: two chains, acyclic. PASS.
- Every `policy_source` is a verbatim sentence of the blocked policy's own rule (treadwear rule last sentence; road hazard rule last sentence; flat repair rule last sentence). PASS.
- `form: state` on all three; no `fallback_reason` (none required). PASS.
- `condition` vs sentence strength: each condition names exactly the row the sentence's state denotes (installation_package charge with source = the claim entry; treadwear_credit with source = the damaged wheel's latest claim entry; rotation_balance charge dated on the repair's service date). Neither strengthened nor weakened. PASS.
- `resolved_by` equals the depended-on policy's `target_tool`, and that tool's effect creates exactly the row the condition names. `value_input` gates `rh_tw_credit` and `fl_rotation_paid` are bindings in the blocked compute. The `state_gate` gate names a column (`tire_services.charge_component`) rather than an eligibility id — the extended policies carry no eligibility list, and the column is where the state is visible (observation O-2). No authoring-viewpoint phrasing in any `prerequisite`. PASS.

### prerequisite_sentences

1. Treadwear credit ← claim fitting. Sentence: "A treadwear credit is not booked until the wheel replaced under that claim carries its claim fitting charge on the package." Connective "not … until"; waited-on = a record-visible state (a charge on the package for that wheel); no tool, id or snake_case token; scope "that claim" = the claim entry being credited. Derivation: reader of the treadwear rule needs "claim fitting charge"; the only rule that defines it is tire_ext_claim_fitting_charge ("the installation_package charge member services books for the one wheel whose tire was replaced under the treadwear mileage warranty … booked against that claim entry"); its target write is the only write of this difficulty that books an installation_package row against a claim entry. Single reading. PASS.
2. Road hazard credit ← treadwear credit. Sentence: "The road hazard credit on a tire fitted under a treadwear claim is fixed only after that claim's treadwear credit stands on the package." Connective "only after"; state = a treadwear credit row on the package; scope limited to a tire fitted under a treadwear claim (open/closed sets stated correctly: the edge fires only when the damaged wheel has a claim entry, matching `rh_tw_count > 0`). Only post_treadwear_credit creates a treadwear_credit row. Single reading. PASS.
3. Flat repair ← rotation charge. Sentence: "The flat repair charge for a work order is fixed only after the rotation logged on that same work order carries its rotation charge on the package." Connective "only after"; state = a rotation charge on the same work order date; only authorize_rotation_charge creates rotation_balance rows. Single reading. PASS.
- No rule carries a second wording of these dependencies, a tool name or another policy id; the depended-on rules do not restate the sentences. No rule states any other cross-problem order (swept all five rules: the remaining references — "replacement_tire charge booked against the claim entry", "last rotation charge booked on the package" — read seeded rows or the policy's own prior writes, not another problem's write). PASS.
- Base order sentence: tire_service_eligibility "a member whose membership has lapsed renews it before the Tire Center will rotate, repair, replace or adjust a tire" states a cross-problem order; no extended edge rests on it (observation O-3; per-task files confirm the membership is active in both worlds).

### override_declarations

Sentence-by-sentence sweep of every `base_policy_refs` entry.

- tire_ext_claim_fitting_charge (refs installation_charges, lifetime_services, road_hazard_protection, treadwear_warranty). tire_treadwear_warranty "…the replacement of the same item is charged at tire_msr_current_tire_price and installed at the package's per-tire price" — the fitting quantity — declared in `overwrite` (clause "installed at the package's per-tire price"). tire_installation_charges sentences govern the installation-date charges (different object); tire_road_hazard_protection "Mounting, balancing and a valve stem for the replacement are free where road_hazard_replacement_install_included…" governs road-hazard replacements only; lifetime_services sentences govern rotation/rebalance/flat. Followed. The `replaced_by` text describes only the rate product, not the usage-share method; the clause is named and the rule gives the merged semantics, so no second answer arises (observation O-4).
- tire_ext_treadwear_credit (refs road_hazard_protection, treadwear_warranty, package_end). The credit sentence of tire_treadwear_warranty is declared. Eligibility sentences (worn ≤ 2/32 while miles < warranty; max rotation gap ≤ 7500; zero-warranty model; road-hazard-replaced tires excluded; "A credit is applied only to the replacement") are inherited unweakened. road_hazard_protection cash-out sentence followed. package_end not touched.
- tire_ext_road_hazard_credit (refs road_hazard_protection, treadwear_warranty, package_end). The credit sentence of tire_road_hazard_protection is declared (it names tire_unit_price, the full-credit wear test and the usable fraction — the extended price basis, proration method and multipliers all act on that quantity). Term, coverage-end, replacement-limit, causes, replacement-price, cash-out, spare and remaining-term sentences inherited.
- tire_ext_service_rotation_charge (refs installation_charges, lifetime_services, road_hazard_protection, treadwear_warranty). "Rotations are free where lifetime_rotation_included is true and otherwise cost rotation_fee_usd per visit" declared. **"Rebalancing is free where lifetime_rebalance_included is true and otherwise costs rebalance_fee_per_tire_usd per tire." — NOT declared**, yet the extended rotation work method charges rebalancing inside the rotation work charge and then multiplies it by the four rates, so a rebalanced tire on a non-included package costs rebalance_fee_per_tire_usd × combined rate, not rebalance_fee_per_tire_usd (finding D-F1).
- tire_ext_flat_repair_charge (refs installation_charges, lifetime_services, road_hazard_protection, treadwear_warranty). "repairable flats are free where flat_repair_included is true and otherwise cost flat_repair_fee_usd" declared. **"Each fee is its own entry on the visit's service date." — NOT declared**, yet the flat repair work method books tpms_service_kit_fee_usd (a fee the base books as its own `tpms_service_kit` entry, tire_installation_charges; `tpms_service_kit` is its own `charge_component` in db_schema) and, at two or more earlier repairs, rebalance_fee_per_tire_usd inside the one flat_repair entry and scales them by the rates; and the rebalance sentence above is again not declared (finding D-F1).
- Disguised forms: no anonymous intermediate (every multiplier is named and declared or in the findings above), no 0/1 multiplier on a base-fixed amount, no dropped branch (every base branch — full credit at low wear, zero warranty, zero fee packages — is still produced by an extended selector).

### factor_ladders

Per policy (effect label; decides; tiers; multi-source; cross_difficulty):

- tire_ext_claim_fitting_charge — 4 factors (3 parameter, 1 method).
  - claim_fitting_member_rate (parameter; fit_member_rate; 3 tiers 0.5/0.75/1.0; Plus status from membership × tenure measured to the claim entry date → multi-source; membership).
  - claim_fitting_replacement_rate (parameter; 3 tiers 0.8/0.9/1.0; history; single-source).
  - claim_fitting_tender_rate (parameter; 3 tiers 0.9/0.95/1.0; order tender; order).
  - claim_fitting_usage_share (method; three distinct algorithms: × share, × (1+share)/2, in full; single-source history).
  - Disjoint bindings; tiers distinct; all tiers in the rule; fall-throughs equal `baseline` and the baseline rule (package per-tire price, the base treadwear clause). Labels honest.
- tire_ext_treadwear_credit — 6 declared (5 parameter, 1 method).
  - treadwear_price_paid (parameter; 4 tiers; order lines; order). **Unreal ladder** — finding D-F3.
  - treadwear_price_basis (method; higher-of / replacement charge / price paid; distinct; history+date).
  - treadwear_mileage_factor (parameter; 1.1/1.05/1.0; membership tier and fee — one record; membership).
  - treadwear_rotation_factor (parameter; 1.1/1.05/1.0). **Unreal ladder** — finding D-F2.
  - treadwear_tread_factor (parameter; 0.8/0.9/1.0 at ≤0, 1, ≥2 32nds; each reachable by an eligible claim since eligible tread is 0–2).
  - treadwear_late_settlement_allowance (parameter; +10/+5/0).
  - Surviving after D-F2/D-F3: 4 factors (price_basis method; mileage, tread, late parameters) — inside 4–6, ≥2 parameter, ≥1 method; cross_difficulty membership survives.
- tire_ext_road_hazard_credit — 5 declared (3 parameter, 2 method).
  - road_hazard_price_basis (method; 3 tiers). **Tiers 2 and 3 select the same method** — finding D-F3.
  - road_hazard_proration_method (method; max(tread, miles) / miles / tread; distinct).
  - road_hazard_sequence_share (parameter; 0.8/0.9/1.0; ≥3 reachable on Premium Tire Care, max 4).
  - road_hazard_term_share (parameter; 0.85/0.95/1.0).
  - road_hazard_member_share (parameter; 1.1/1.05/1.0; membership Plus × order tender → multi-source; membership).
  - Surviving after D-F3: 4 factors (1 method, 3 parameter), multi-source and cross_difficulty present.
- tire_ext_service_rotation_charge — 5 factors (4 parameter, 1 method).
  - rotation_work_method (method; + full rebalance / + half-set rebalance / fee alone; distinct algorithms). Its rebalance terms are the subject of D-F1 (an override question, not a ladder defect).
  - rotation_member_rate (parameter; 0.6/0.8/1.0; membership tier, segment and tenure to the rotation entry date → multi-source; membership).
  - rotation_loyalty_rate (parameter; 0.75/0.9/1.0).
  - rotation_tender_rate (parameter; 0.9/0.95/1.0; order).
  - rotation_package_age_rate (parameter; 0.5/0.75/1.0).
- tire_ext_flat_repair_charge — 4 factors (3 parameter, 1 method).
  - flat_repair_work_method (method; + tpms + rebalance / + tpms / fee alone).
  - flat_repair_bundle_rate (parameter; rotation charge on the same date × tread ≥ 4 → multi-source; 0.5/0.75/1.0).
  - flat_repair_member_rate (parameter; membership fee-charge count; membership).
  - flat_repair_mileage_rate (parameter; 0.5/0.8/1.0).
- Per task component: A (claim fitting, treadwear, road hazard) has multi-source (road_hazard_member_share, claim_fitting_member_rate) and cross_difficulty (membership, order); B (rotation, flat) has multi-source (flat_repair_bundle_rate, rotation_member_rate) and cross_difficulty (membership, order).
- Business realism: member, tender, loyalty, tenure, package-age, mileage, term-remaining and sequence ladders are discounts or proration steps a warehouse club's tire centre could publish; their fall-throughs (full rate / full share / no allowance) are the ordinary customer's treatment. The exceptions are D-F2 and D-F3.

### findings

**D-F1 — SOURCE-POLICY RED (undeclared override). Bears on task 1.**
- Symptom: two base sentences of `tire_lifetime_services` govern quantities the rotation and flat repair extended policies settle differently, and neither policy's `overwrite` names them.
- Root cause: `tire_ext_service_rotation_charge.overwrite` names only "Rotations are free where lifetime_rotation_included is true and otherwise cost rotation_fee_usd per visit"; `tire_ext_flat_repair_charge.overwrite` names only "repairable flats are free where flat_repair_included is true and otherwise cost flat_repair_fee_usd".
- Evidence: base (tire.extended.yaml line 686-687) "Rebalancing is free where lifetime_rebalance_included is true and otherwise costs rebalance_fee_per_tire_usd per tire." and (line 693-694) "Each fee is its own entry on the visit's service date."; extended rotation rule (lines 1608-1612) "… charged as rotation_fee_usd plus rebalance_fee_per_tire_usd for tire_count divided by half_set tires …" followed by "The rotation work charge is multiplied once by the product of the rotation member rate, the rotation loyalty rate, the rotation tender rate and the rotation package-age rate"; extended flat rule (lines 1800-1804) "exactly one_earlier is charged as flat_repair_fee_usd plus tpms_service_kit_fee_usd" inside "one flat_repair charge for the repaired wheel"; db_schema `charge_component` lists `tpms_service_kit` separately from `flat_repair`.
- Consequence: demonstrated against task 1's world in `1.md` (second reading of the rotation_balance amount and of the flat_repair amount).
- Affected: tire.extended.yaml `tire_ext_service_rotation_charge.overwrite`, `tire_ext_flat_repair_charge.overwrite`; base `tire_lifetime_services` rule.

**D-F2 — SOURCE-FACTOR RED (unreal ladder: a condition that holds of every customer who reaches the write; unreachable fall-through). Bears on task 0.**
- Symptom: `treadwear_rotation_factor`'s middle-tier condition "at least the miles driven divided by treadwear_rotation_max_interval_miles, rounded down" is guaranteed by the base treadwear eligibility, so the fall-through `no_uplift` (= the factor's baseline) is a treatment no eligible claim receives.
- Evidence and proof: base `tire_treadwear_warranty` (eligibility `rotation_records`, measure `tire_msr_max_rotation_gap_miles`): every gap in the sequence install_odometer, each rotation odometer, claim odometer is ≤ treadwear_rotation_max_interval_miles = 7500 (all six variants). With c rotations between installation and the claim there are c+1 gaps, so miles m ≤ 7500(c+1), hence floor(m/7500) ≤ c+1, with floor(m/7500) = c+1 only when m = 7500(c+1) exactly and every gap is exactly 7500. The rule's count also includes any rotation after the claim, which only raises c. So "count ≥ floor(m/7500)" holds for every recorded (eligible) treadwear claim except that single boundary; the ladder is in effect two tiers (kept_uplift / regular_uplift), and its baseline `no_uplift` is a straw man.
- Consequence: demonstrated in `0.md` (the customer is on the middle tier because of the gaps that made the claim eligible).
- Affected: tire.extended.yaml `tire_ext_treadwear_credit.factors[treadwear_rotation_factor]` and the matching rule sentence (lines 1130-1134).

**D-F3 — SOURCE-FACTOR RED (unreal ladder: tiers selecting the same method). Bears on task 0.**
- Symptom: `treadwear_price_paid`'s four tiers ("tire_unit_price less both per-unit credits" / "less the per-unit price adjustment" / "less the per-unit rebate" / "tire_unit_price") are one method — tire_unit_price less whatever per-unit price-adjustment and rebate credits are recorded — written as four tiers; the conditions only test whether each subtrahend is zero. Likewise `road_hazard_price_basis` tier 2 ("tire_unit_price less those per-unit credits") and tier 3 ("tire_unit_price as recorded on the package") are the same method, leaving that ladder two distinct tiers (treadwear-net vs unit-less-credits).
- Demonstration: the single expression `F('tire_unit_price') - tw_adj_unit - tw_rebate_unit` returns, for every input, the value of whichever tier the compute at line 1175 selects (absent credits sum to 0.0 by XSUM); the same holds for `F('tire_unit_price') - rh_adj_unit - rh_rebate_unit` on the domain of tiers 2 and 3 at line 1431. No tier selects a value the others would not compute on its own domain.
- Count effect: striking both leaves treadwear credit 4 factors (1 method) and road hazard credit 4 factors (1 method, cross_difficulty membership) — the 4–6 bounds still hold; the defect is the ladders themselves. Per-task demonstration in `0.md`.
- Affected: tire.extended.yaml `tire_ext_treadwear_credit.factors[treadwear_price_paid]` (lines 1219-1235, rule lines 1115-1119); `tire_ext_road_hazard_credit.factors[road_hazard_price_basis]` (lines 1479-1493, rule lines 1364-1369).

**Observations (no demonstrated consequence at charter level)**
- O-1: docstrings carry "read from … before the call" (task_tools.py lines 26, 30, 64, 66, 170) — an ordering word about an argument lookup, not about another write.
- O-2: the state_gate edge's `gate` names a column (`tire_services.charge_component`) rather than an eligibility id.
- O-3: base `tire_service_eligibility` states a cross-problem order (renew a lapsed membership before service); no extended edge rests on it.
- O-4: `tire_ext_claim_fitting_charge.overwrite.replaced_by` summarises only the rate product, not the usage-share method; clause named, merged semantics unique.
- O-5: "rounded to the cent" leaves half-up vs half-even unstated; checked per task whether any scored value lands on a half cent.
- O-6: `tire_ext_claim_fitting_charge` counts road hazard and treadwear entries "recorded on the package" with no as-of date while its tenure is explicitly measured to the claim's service date; where a road hazard entry postdates the claim this invites a second reading (demonstrated with numbers in `0.md`).

## closing_checklist

Written after both reveals (2026-10-05T21:35:10Z). The charter-global section above was written before any reveal and is unchanged.

- Per-task files: `0.md`, `1.md` correspond one-to-one with tasks/0.json, tasks/1.json; `_difficulty.md` alongside; first revision (no older revision exists). Comparison sections present in both; **not every comparison carries PASS** — task 0 SOURCE-FACTOR RED, task 1 SOURCE-POLICY RED.
- Coverage and scope: charter_scope task 0 = {tire_ext_claim_fitting_charge, tire_ext_treadwear_credit, tire_ext_road_hazard_credit}, task 1 = {tire_ext_service_rotation_charge, tire_ext_flat_repair_charge} — equal to the two components of the prerequisite graph derived blind; pairwise disjoint; jointly cover all five extended policies and all five task tools. Each task tool carries an independent uuid8 (§ action_binding_and_uuids). PASS.
- Problem trees: task 0 — 2 prerequisite problems, 1 value_input edge (≥ 1), owner=user root, acyclic; task 1 — 1 prerequisite problem, 1 value_input edge, owner=user prerequisite, acyclic; whole-difficulty graph two disjoint chains, acyclic. PASS.
- Factors: every computation declares a self-sufficient baseline giving a definite number different from gold (31.99, 78.57, 112.49, 19.99, 15.00) and 4-6 factors; every factor bears weight on its world. **Not closed**: D-F2 (treadwear_rotation_factor) and D-F3 (treadwear_price_paid, road_hazard_price_basis) are unreal ladders.
- Policy self-consistency: **not closed** — D-F1 undeclared override of tire_lifetime_services (rebalance price; each fee its own entry), demonstrated on task 1.
- Gates on the final form: no artifact changed during the audit (tire.extended.yaml beba2782…d7ab and task_tools.py 9c222360…2481 unchanged; tasks/0.json fc1e931a…43e3, tasks/1.json bdb6751d…ead58 at close), so the coordinator's gate snapshot of 2026-10-05 stands for the final form; check_traceability remains NOT OK pending the KB render, outside this audit.
- Difficulty result: **does not pass the source-layer audit** (task 0 SOURCE-FACTOR RED; task 1 SOURCE-POLICY RED).

## revision_2

### charter_global_frozen (revision 2)

- Trigger: coordinator re-audit round 2 (verify round-1 REDs closed, no new defect, no regression).
- Hashes: tire.extended.yaml **e61a4a2fb751436b753fa4d545f54321668c2cd031e660c3b05fe9d1fc1fd8bd** (changed from beba2782…d7ab → charter-global sections re-derived in full below); task_tools.py 9c222360…2481 (unchanged → § action_binding_and_uuids carried forward by reference); masked views 0.view.json 63857239…30ab, 1.view.json a75c4e1f…9870 (both verified on disk). Base section lines 1-906 still verbatim equal to blueprint/products/tire.yaml (diff empty).
- Freeze time: 2026-10-05T22:28:36Z, before any round-2 task JSON was opened. Auditor: Claude (erl-task-policy-audit).
- Masked and unread at freeze: round-2 tasks/{0,1}.json (all GT fields); worklog.md (never opened). Nothing below derives from a round-2 GT.
- contamination_disclosure: this auditor read the round-1 GT of both tasks during round 1 (scored values recorded in `0.md`/`1.md` revision 1). That knowledge cannot be unlearned; the round-2 charter-global section is built from the charter, schema and tool module only, and per-task derivations are recomputed from the charter compute on the rebuilt worlds. Where a round-2 value equals a round-1 GT value, that agreement is not independent evidence.
- What changed in the charter (located by re-reading every extended policy): (1) `tire_ext_claim_fitting_charge` rule/compute_basis: replacement count now "whatever their service dates, entries dated after the claim entry included"; (2) `tire_ext_treadwear_credit`: factor `treadwear_price_paid` removed — the net price paid (tire_unit_price less every per-unit adjustment and rebate) moved into the rule and `baseline.rule`; rotation factor re-based on the average rotation interval (miles ÷ (rotations + 1)) with new param fair_interval_miles 7000; new factor `treadwear_membership_years_allowance` (count of membership fee charges: ≥15 → +12.00, 10-14 → +6.00, else 0); overwrite replaced_by updated; (3) `tire_ext_road_hazard_credit`: price basis tier 2 now "exactly one earlier road hazard replacement on that wheel, no treadwear claim → that wheel's replacement_tire charges less the current one, less the road hazard credits on it"; tier 3 "every other case → road hazard price paid per tire" (net of credits); `baseline.rule` now uses that net price; (4) `tire_ext_service_rotation_charge`: two added overwrite entries (base "Rebalancing … per tire" and "Each fee is its own entry …") and a matching rule sentence; (5) `tire_ext_flat_repair_charge`: three added overwrite entries ("Each fee is its own entry …", "Rebalancing … per tire", and tire_installation_charges "a tpms_service_kit entry of tpms_service_kit_fee_usd for each wheel with a pressure sensor when that fee is not zero") and a matching rule sentence. Prerequisite fields, prerequisite sentences, target tools and the other policies' ladders are unchanged.

### policy_conflict_scan (revision 2)

Unchanged in structure: five policies, five distinct (subject, component) writes, same two prerequisite components A = {claim fitting → treadwear credit → road hazard credit}, B = {rotation → flat repair}. New overlap introduced: the base sentence "Each fee is its own entry on the visit's service date" and the base rebalance sentence are each superseded by two policies (rotation and flat repair), each with a replacement scoped to its own visit kind ("Rebalancing done on a rotation visit …" / "On a repeat repair …"). The two scopes are disjoint (a rotation_balance entry vs a flat_repair entry), so they never govern one quantity; outside both scopes no extended policy writes, so no conflict on any write of this difficulty. See observation R2-O1 on the breadth of the superseded clauses.

### rule_compute_equivalence (revision 2)

Re-swept every policy. New/changed bindings:
- fit_replacements ↔ "…recorded on the package together, whatever their service dates, entries dated after the claim entry included" — COUNT has no date filter. PASS.
- tw_price_paid = F(tire_unit_price) − tw_adj_unit − tw_rebate_unit ↔ "tire_unit_price less every price adjustment and every mail-in rebate credited per unit …, and is tire_unit_price where none was credited". PASS.
- tw_avg_interval = tw_miles / (tw_rotations + 1); tw_rotation_factor ≤ 5000 / ≤ 7000 / above ↔ rule sentence. PASS. (The count is of all rotation entries on the package, including any dated after the claim; the rule says the same — observation R2-O2.)
- tw_fee_years = XCOUNT(membership_fee_charged on the presented membership); tw_member_allowance ladder; tw_credit adds it ↔ rule and overwrite. PASS.
- rh_price_paid, rh_det_id, rh_pos_rh_count, rh_pos_repl_charges, rh_cur_charge, rh_pos_rh_credits, rh_price_basis ↔ the new price-basis sentence: tier 2 is taken when `rh_tw_count == 0 and rh_pos_rh_count == 2` (the current entry plus exactly one other on that position), matching "exactly one road hazard replacement entry other than the current one". PASS.
- Rotation and flat repair compute unchanged; the added rule sentences describe what the compute already does (rebalance/kit fees inside the one entry, scaled by the rates). PASS.
- Every factor's ladder tiers are rule sentences and `decides` branches and vice versa (23 factors). PASS.

### action_binding_and_uuids (revision 2)

task_tools.py hash unchanged (9c222360…2481) and every policy keeps its round-1 target_tool; carried forward from revision 1 § action_binding_and_uuids on that ground. PASS.

### prerequisite_graph and prerequisite_sentences (revision 2)

The three `prerequisite` entries and their `policy_source` sentences are byte-identical to revision 1 and each sentence is still verbatim in its blocked rule (treadwear rule last sentence; road hazard rule last sentence; flat repair rule last sentence). The rule edits add no ordering connective about another problem (the new rotation/flat sentences concern the composition of their own entry; the new road hazard tier 2 reads seeded replacement_tire charges and road_hazard_credit rows on the wheel, i.e. prior road hazard settlements — the credit being computed is never one of them at handling time). Revision 1 conclusions carried forward: acyclic, state form, one resolving write per state, single-reading derivations. PASS.

### override_declarations (revision 2)

Re-swept every `base_policy_refs` sentence.
- D-F1 (rebalance price; each fee its own entry): now declared. Rotation `overwrite` names "Rebalancing is free where lifetime_rebalance_included is true and otherwise costs rebalance_fee_per_tire_usd per tire" and "Each fee is its own entry on the visit's service date", replaced by "Rebalancing done on a rotation visit is neither a separate per-tire charge nor an entry of its own: it is part of the rotation work charge booked in the one rotation_balance entry, and the rotation rates below scale it together with the rotation fee." Flat `overwrite` names the same two sentences plus the tire_installation_charges tpms clause, replaced by "On a repeat repair the sensor seal kit and the rebalancing are neither booked as entries of their own nor charged at their own fees: they are part of the one flat repair entry for the wheel, and the flat repair rates below scale them together with the repair fee." The replacements state exactly the readings round 1 found undeclared, so the base-price / own-entry readings are no longer inherited for those quantities. **Closed.**
- Treadwear credit: the declared superseded clause still covers the whole base credit quantity; the net price paid and the membership-years allowance act on that quantity and the replaced_by names the allowance. Eligibility sentences inherited unweakened. PASS.
- Road hazard credit: the declared clause (credited at tire_unit_price / usable fraction) covers the new price-paid and tier-2 basis. PASS.
- Claim fitting: unchanged. PASS.
- No new undeclared override found.

### factor_ladders (revision 2)

- tire_ext_claim_fitting_charge: unchanged (4 factors; 3 parameter, 1 method). PASS.
- tire_ext_treadwear_credit: 6 factors — treadwear_price_basis (method), treadwear_mileage_factor, treadwear_rotation_factor, treadwear_tread_factor, treadwear_late_settlement_allowance, treadwear_membership_years_allowance (parameters; cross_difficulty membership on mileage and membership-years). Bounds met.
  - **D-F2 re-check**: the new rotation condition is the average interval m/(c+1). The base eligibility bounds every gap by 7500, hence the average by 7500 — but not by 7000: a claim whose gaps average anywhere in (7000, 7500] (e.g. six gaps of 7400) is admitted and falls through to `no_uplift`. Each tier is reachable by admitted claims; none restates the eligibility; the fall-through is a real treatment (no uplift for intervals near the limit). **Closed.**
  - **D-F3 re-check (treadwear)**: the four-tier price-paid ladder is gone; net price paid is now one stated method inside the baseline, not a factor. **Closed.**
  - treadwear_membership_years_allowance: 3 tiers (+12 / +6 / 0) over the presented membership's fee ledger; distinct values; tenure is something a warehouse club weighs for goodwill credits; fall-through equals baseline (no allowance). PASS.
- tire_ext_road_hazard_credit: 5 factors (2 method, 3 parameter).
  - **D-F3 re-check (road hazard)**: tiers now (1) treadwear-fitted tire → replacement charge less treadwear credit; (2) one earlier road hazard replacement on the wheel → that replacement's charge less its road hazard credit; (3) otherwise → net price paid. Three different source quantities and computations; no two tiers select the same method. **Closed.** The fall-through's second disjunct ("more than one earlier road hazard replacement on it" → original net price paid) is an unusual treatment — observation R2-O3.
  - Others unchanged. Multi-source: road_hazard_member_share; cross_difficulty: membership (road_hazard_price_basis is now `cross_difficulty: null`; its tier 3 still reads order lines through the baseline price paid).
- tire_ext_service_rotation_charge, tire_ext_flat_repair_charge: ladders unchanged. PASS.
- Per component: A has multi-source (road_hazard_member_share, claim_fitting_member_rate) and cross_difficulty (membership, order); B unchanged.

### findings (revision 2)

- D-F1: closed (declared overrides with scoped replacements; demonstration of the round-1 second readings no longer stands — see `1.md` revision_2).
- D-F2: closed.
- D-F3: closed (both ladders).
- O-6: closed (count explicitly includes entries dated after the claim).
- O-1 … O-5: unchanged, remain observations.
- New observations (no demonstrated consequence on any write of this difficulty):
  - R2-O1: the superseded clauses are whole base sentences ("Each fee is its own entry on the visit's service date"; the rebalance sentence; tire_installation_charges' tpms-kit-at-installation clause) while each replacement is scoped to one visit kind. Read literally, the installation-date tpms kit charge loses its governing sentence; read by scope (the natural reading) it is untouched. No write of this difficulty books installation charges, so no scored value moves.
  - R2-O2: the treadwear average rotation interval divides miles to the claim by rotations recorded on the package at any date; a rotation logged after the claim would shorten the computed average. Neither world has one.
  - R2-O3: road hazard price basis sends a wheel with two or more earlier road hazard replacements back to the original net price paid rather than the last replacement's net cost; only reachable on Premium Tire Care (max 4 replacements); neither world reaches it.
- No new RED at charter level.

### closing_checklist (revision 2)

Written after the round-2 reveals (2026-10-05T22:29:30Z); the revision_2 charter-global sections above were written before them and are unchanged.

- Files: `0.md`, `1.md` each carry revision 1 untouched plus revision_2 (frozen derivation, comparison, findings); `_difficulty.md` revision 1 untouched plus this revision_2.
- Round-1 REDs: D-F1 closed (task 1), D-F2 closed (task 0), D-F3 closed (task 0); O-6 closed; task-1 observation 3 closed; task-0 observation 4 kept (harmless); O-1…O-5 and T1-O1 remain observations. New charter observations R2-O1…R2-O3 (no consequence on any write here).
- Coverage/scope: charter_scope task 0 = {claim fitting, treadwear credit, road hazard credit}, task 1 = {rotation charge, flat repair charge} — equal to the graph components; disjoint; complete; tools and uuid8s unchanged. PASS.
- Problem trees: unchanged shapes (task 0: 2 prerequisites, 1 value_input, user root; task 1: 1 prerequisite, 1 value_input, user prerequisite); acyclic. PASS on the charter and worlds.
- Factors: every computation 4–6 factors with ≥2 parameter and ≥1 method, honest self-sufficient baselines (31.99, 69.84, 99.99, 19.99, 15.00 — all ≠ gold), every factor bears weight, ladders real; multi-source and cross-difficulty present per task with seeded rows. PASS on the charter and worlds.
- Scored solutions: both tasks' GT equals the independent derivation argument for argument.
- **Not closed — proof-field regressions introduced by the rework**: task 0 design_rationale (stale 92.96, true value 104.96; write steps cited as 9/11/13, actually 10/12/14) and task 1 (rotation write cited as step 8 in prerequisite_closure, computations[1].factor_trace, evaluation_criteria[11].argument_uniqueness_tracing and design_rationale; actually step 9). Details in `0.md` / `1.md` revision_2 findings.
- Gates: the coordinator's round-2 snapshot covers the final form (no artifact changed during this audit; at close tire.extended.yaml e61a4a2f…fc1fd8bd, task_tools.py 9c222360…c1322481, tasks/0.json 270a63f4…6fd55f07, tasks/1.json 27387181…672a230f); check_traceability deferred (KB not rendered).
- Difficulty result (revision 2): **does not yet pass** — the charter-level defects are closed and both scored solutions are uniquely entailed, but each task file carries false assertions in its proof fields.

## revision_3

### charter_global_frozen (revision 3)

- Trigger: coordinator re-audit round 3 (verify round-2 REDs closed, no new defect, no regression).
- Hashes: tire.extended.yaml **449ec6cbed4e4a75ed6b23b49aa8bf7092d248ea4da1630e840270f78e0551cd** (changed from e61a4a2f…fc1fd8bd → charter-global sections re-derived); task_tools.py 9c222360…c1322481 unchanged (§ action_binding_and_uuids carried forward); masked views 63857239…30ab and a75c4e1f…9870 unchanged since round 2 (verified). Base lines 1-906 still verbatim to blueprint/products/tire.yaml. A copy of this charter revision is kept outside the repo for later diffs.
- Freeze time: 2026-10-05T22:44:32Z, before any round-3 task JSON was opened. Auditor: Claude (erl-task-policy-audit).
- contamination_disclosure: the auditor has seen the round-1 and round-2 GT of both tasks. This section is built from the charter, schema and tool module only.
- What changed (each extended policy re-read in full): (1) rotation and flat repair `overwrite.replaced_by` and the matching rule sentences now end with a universal clause — rotation: "every other Tire Center fee, outside the rebalancing of a rotation visit, remains its own entry at its own fee"; flat repair: "every other Tire Center fee, including the sensor kits charged when a set is installed, remains its own entry at its own fee" (R2-O1 rework); (2) treadwear rotation factor sentence now says the rotation count is taken "whatever their dates (a rotation entry dated after the claim entry counts too)" (R2-O2 rework; compute unchanged); (3) road hazard price basis tier 2 is now "one or more road hazard replacement entries other than the current one … the average net cost of those earlier replacements … divided by the number of those earlier road hazard replacement entries", tier 3 "where no earlier replacement is recorded on that wheel" (R2-O3 rework; compute `rh_price_basis` changed to match). Nothing else changed: claim fitting policy, prerequisites, prerequisite sentences, params, other ladders and computes are as revision 2.

### rule_compute_equivalence (revision 3)

- rh_price_basis tier 2: `(rh_pos_repl_charges - rh_cur_charge - rh_pos_rh_credits) / (rh_pos_rh_count - 1)` when `rh_tw_count == 0 and rh_pos_rh_count >= 2` ↔ "one or more … other than the current one … divided by the number of those earlier road hazard replacement entries". PASS.
- tw_rotations / tw_avg_interval unchanged; the rule now states the undated count the compute always used. PASS.
- The added universal clauses have no compute counterpart (they concern entries other than the one each policy writes). Every compute binding has a compute_basis entry and vice versa (checked for all five policies). PASS otherwise.

### action_binding_and_uuids, prerequisite_graph, prerequisite_sentences (revision 3)

Tool module unchanged; prerequisite entries and sentences byte-identical to revision 2 and still verbatim in their rules. Carried forward. PASS.

### override_declarations and policy_conflict_scan (revision 3)

- R2-O1 (whole base sentences superseded with only scoped replacements): addressed — each replacement now says what happens outside its scope.
- **New conflict between the two replacements (R3-D-F4).** The two clauses added to address R2-O1 are each universal and each contradicts the other policy's exception:
  - tire_ext_service_rotation_charge (rule and `overwrite[1..2].replaced_by`): "every other Tire Center fee, outside the rebalancing of a rotation visit, remains its own entry at its own fee." The sensor seal kit and rebalancing on a repeat flat repair are Tire Center fees outside the rebalancing of a rotation visit, so by this sentence they stay their own entries at their own fees.
  - tire_ext_flat_repair_charge (rule and `overwrite[1..3].replaced_by`): "On a repeat repair the sensor seal kit and the rebalancing are neither booked as entries of their own nor charged at their own fees … every other Tire Center fee, including the sensor kits charged when a set is installed, remains its own entry at its own fee." The rebalancing of a rotation visit is a Tire Center fee outside the repeat-repair kit and rebalancing, so by this sentence it stays its own entry at its own fee — contradicting the rotation rule's "Rebalancing done on a rotation visit is neither a separate per-tire charge nor an entry of its own".
  - Both texts declare a supersession of the same base sentences ("Each fee is its own entry on the visit's service date"; "Rebalancing is free … per tire"), so the merged semantics after declaration are not unique on the text: each policy's universal clause re-imposes, for the other policy's quantity, exactly the base reading round 1 found undeclared (D-F1). A precedence of the specific exception over the other policy's general clause would reconcile them, but no sentence of the charter states that precedence. Demonstrated against task 1's world in `1.md` revision_3. → **SOURCE-POLICY RED** (charter-global; bears on task 1).
- Other policies: unchanged conclusions from revision 2.

### factor_ladders (revision 3)

- road_hazard_price_basis: tiers now (1) treadwear-fitted tire net; (2) average net cost of the earlier road hazard replacements on the wheel; (3) no earlier replacement → net price paid. Three distinct methods, pairwise disjoint conditions (tier 3 now exactly "no earlier replacement", so the R2-O3 disjunct is gone). The averaging in tier 2 credits a tire against the mean net cost of all earlier replacements on the wheel rather than the net cost of the tire actually mounted there — unusual, reachable only with two or more earlier replacements on one wheel (Premium Tire Care), reached by neither world: observation R3-O1.
- treadwear_rotation_factor: unchanged ladder; R2-O2 now explicit in text ("a rotation entry dated after the claim entry counts too") — a rotation after the claim shortens the computed average for miles driven before it; stated, not hidden: observation closed as a disclosure, kept as R3-O2 for realism only.
- All other ladders unchanged; counts as revision 2 (4 / 6 / 5 / 5 / 4 factors; ≥2 parameter, ≥1 method each; multi-source and cross_difficulty per component). PASS.

### findings (revision 3)

- R2-O1: addressed, but the fix introduces **R3-D-F4 (SOURCE-POLICY RED, bears on task 1)** above.
- R2-O2: closed (stated in the rule); realism note R3-O2.
- R2-O3: closed (disjunct removed); new realism note R3-O1 on the averaging.
- D-F1, D-F2, D-F3, O-6: remain closed except that R3-D-F4 re-opens the D-F1 consequence through a different text.
- O-1 … O-5: unchanged observations.

### closing_checklist (revision 3)

Written after the round-3 reveals (2026-10-05T22:45Z); the revision_3 charter-global sections above precede them and are unchanged.

- Files: `0.md`, `1.md`, `_difficulty.md` each carry revisions 1 and 2 untouched plus revision_3.
- Round-2 items: R2-T0-1 closed; R2-T0-2 closed; R2-T1-1 closed; R2-O2 closed (stated in text); R2-O3 closed (disjunct removed; realism note R3-O1); R2-O1 addressed but **its fix introduces R3-D-F4 (SOURCE-POLICY RED, task 1)**.
- Newly reported, pre-existing: task 1 design_rationale §9 near-miss figure 17.09 (true 17.10) — SOURCE-FACTOR RED; missed by this audit's earlier revisions.
- Scope, trees, factor structure, baselines and factor weight: unchanged and PASS on the charter and both worlds; both GTs equal the independent derivations argument for argument.
- Gates: coordinator's round-3 snapshot covers the final form; check_traceability deferred.
- Per-task: task 0 PASS; task 1 SOURCE-POLICY RED + SOURCE-FACTOR RED.
- **Difficulty result (revision 3): does not pass.**

## revision_4

### charter_global_frozen (revision 4)

- Trigger: coordinator re-audit round 4. Hashes: tire.extended.yaml **f9551bba8abd7c702032bb7d38a06ed7ab5cad37185bfe609c6624c59e13bd45** (changed from 449ec6cb…0551cd); task_tools.py 9c222360…c1322481 unchanged; views 63857239…30ab, a75c4e1f…9870 unchanged since round 2. Base lines 1-906 verbatim. Freeze time 2026-10-05T22:49:25Z, before any round-4 task JSON was opened. Auditor: Claude.
- contamination_disclosure: the auditor has seen the round-1 to round-3 GT of both tasks; this section uses the charter, schema and tool module only.
- What changed: a line diff against the round-3 charter copy kept outside the repo shows exactly eight changed lines, all in the closing clause of the rotation and flat repair replacement sentences (rotation rule, compute_basis.rot_work_charge, overwrite[1..2].replaced_by; flat rule, compute_basis.fl_work_charge, overwrite[1..3].replaced_by). No compute, param, ladder, baseline, prerequisite or other policy changed. Recomputing every policy on both worlds gives figures identical to revision 3.

### override_declarations and policy_conflict_scan (revision 4)

- R3-D-F4 re-check. Rotation clause now: "this exception governs only the rotation_balance entry this rule books, the make-up of every other entry is settled by the rule that books that entry, and a fee that no rule folds into another entry stays its own entry at its own fee." Flat repair clause now: "this exception governs only the flat_repair entry this rule books, the make-up of any other entry follows the rule that books it, and any fee that no rule folds into another entry, such as the sensor kits charged when a set is installed, remains a separate entry at its own fee."
  - The repeat-repair sensor kit and rebalancing: folded by the flat repair rule, so the rotation clause's residual "a fee that no rule folds" does not reach them, and the rotation clause expressly leaves the flat_repair entry to its own rule. Single reading: inside the flat_repair entry.
  - Rotation-visit rebalancing: folded by the rotation rule, so the flat clause's residual does not reach it, and the flat clause leaves the rotation_balance entry to its own rule. Single reading: inside the rotation_balance entry.
  - Installation-date sensor kits: folded by no rule → their own entry at their own fee (the base tire_installation_charges reading), as both clauses now say. R2-O1's concern stays addressed.
  - The two clauses now agree; each defers to the other for the other's entry. The round-3 alternatives (rotation 10.25, flat repair 4.80) have no textual ground. **R3-D-F4 closed.**
- Other policies unchanged; no new undeclared override or cross-policy conflict.

### rule_compute_equivalence, action_binding_and_uuids, prerequisite_graph, prerequisite_sentences, factor_ladders (revision 4)

The changed sentences have no compute counterpart (each concerns entries other than the one its policy writes) and add no ordering connective about another problem ("the rule that books that entry" names no tool, id or order). Everything else is byte-identical to revision 3; the revision-3 conclusions are carried forward on that ground. R3-O1 (averaging of earlier replacement costs) and R3-O2 (undated rotation count) remain observations. PASS.

### findings (revision 4)

- R3-D-F4: closed.
- No new charter-level RED. O-1 … O-5, R3-O1, R3-O2 remain observations.

### closing_checklist (revision 4)

Written after the round-4 reveals (2026-10-05T22:49:40Z); the revision_4 charter-global sections above precede them.

- Files: `0.md`, `1.md`, `_difficulty.md` each carry revisions 1–3 untouched plus revision_4; every comparison section of revision 4 carries PASS.
- Coverage and scope: task 0 = {tire_ext_claim_fitting_charge, tire_ext_treadwear_credit, tire_ext_road_hazard_credit}, task 1 = {tire_ext_service_rotation_charge, tire_ext_flat_repair_charge}; pairwise disjoint, jointly complete; five task tools, each with an independent uuid8, unchanged.
- Problem trees: task 0 — 2 prerequisites, 1 value_input edge (≥ max(n−1,1) = 1), owner=user root, acyclic; task 1 — 1 prerequisite, 1 value_input edge, owner=user prerequisite, acyclic; difficulty graph two disjoint chains, acyclic. Every edge unmet at the opening and load-bearing (112.33 / gate; 14.07).
- Factors: claim fitting 4, treadwear 6, road hazard 5, rotation 5, flat repair 4 — each ≥2 parameter and ≥1 method; multi-source and cross-difficulty (membership, order; seeded) in both tasks; every ladder ≥3 distinct, reachable tiers stated in its rule; every factor bears weight against an honest baseline; all-baseline numbers 31.99 / 69.84 / 99.99 / 19.99 / 15.00 definite and ≠ gold.
- Policy self-consistency: all overrides declared (D-F1 closed in revision 2; the cross-policy conflict R3-D-F4 closed in revision 4); prerequisite sentences in state form, verbatim in the blocked rules, single reading.
- Unique solution: both GTs equal the independent derivation argument for argument; persona raises only the root and closes at the last gold write.
- Remaining observations (no consequence on any scored write): O-1 … O-5, R3-O1 (road hazard tier-2 averaging, reason stated by the author), R3-O2 (undated rotation count, stated in the rule), T1-O1.
- Gates: coordinator's round-4 snapshot all OK on this final form (tire.extended.yaml f9551bba…13bd45, task_tools.py 9c222360…c1322481); check_traceability deferred to the KB render (step 3), outside this audit.
- Contamination note across rounds: from revision 2 on, the derivations are recomputations by an auditor who had seen earlier GT; the revision-1 blind derivations were clean and matched GT.
- **Difficulty result (revision 4): PASS — the source-layer audit passes for all four relationships in both tasks.**
