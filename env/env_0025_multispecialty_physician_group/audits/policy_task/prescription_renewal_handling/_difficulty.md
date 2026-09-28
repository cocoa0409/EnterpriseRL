# Policy-task audit — prescription_renewal_handling / charter-global

## charter_global_frozen

- Freeze time: 2026-09-24T23:34Z (written before any task's GT was revealed; nothing in this charter-global section is derived from a revealed GT).
- Auditor: independent audit agent (erl-task-policy-audit), revision 1. It is not the authoring agent.
- Frozen inputs:
  - `tasks/prescription_renewal_handling/rx.extended.yaml` sha256 `31f55822806fcc9188580bb733992099eb4dcf454ec9d0865b16477f28451bce`
  - `tasks/prescription_renewal_handling/task_tools.py` sha256 `8d4278870c4b4b7be9c6e3f90459304285b13c9039f895f9612279cfc86619b7`
  - Both match the coordinator's charter hashes.
- Fields I was allowed to read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/*.yaml` (rx plus the cross-read categories billing, appointment and telehealth), the extended charter, `task_tools.py`, and the coordinator's masked views (`frozen_time`, `user_scenario`, `initial_state` only).
- Fields masked and not read before the freeze: `tasks/*.json` in whole, meaning `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract` and `prerequisite_closure`. `tasks/prescription_renewal_handling/worklog.md` and the scenario-level `worklog.md` were never opened.
- Entry conditions (Step 0): the coordinator supplied the gate snapshot. All seven gates were green: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK and SCOPE OK. check_traceability is deferred until the KB is published. The masked views came with sha256 hashes, and I re-verified both (0.view `5c2bcd83…`, 1.view `b4697415…`). The input is complete.
- Base copy: the top-level keys `category`, `display_name`, `binding`, `lifecycle`, `accounts`, `parameter_schema`, `variants`, `events`, `measures` and `policies` of `rx.extended.yaml` are structurally equal to `blueprint/products/rx.yaml`. I checked this by YAML-load equality on each key. The base copy is verbatim.
- DSL semantics used below come from `skills/erl-task-instantiate/scripts/check_compute.py`:
  - `DAYS(a,b)` = (b − a) in days.
  - `within_months=n` keeps a row when 0 ≤ MONTHS(row_date, NOW) < n. MONTHS counts whole months and decrements when the day of the month has not been reached.
  - `XLATEST`/`XCOUNT` scope rows to the customer.
  - `appointments` holds in-person visits only; virtual visits live in `telehealth_visits` (db_schema). So "a virtual visit not counting" is carried by the table choice.

### policy_conflict_scan

The extended charter has four policies. Their prerequisite edges split them into two trees:

| Tree | Root (subject / target tool / owner) | Prerequisite (subject / target tool / owner) |
| --- | --- | --- |
| A | `rx_ext_replacement_fill_days` (rx_fills_authorized / `authorize_replacement_fill_7c6c01e8` / agent) | `rx_ext_retail_move_fill_days` (rx_pharmacy_changed / `move_prescription_pharmacy_221e1a97` / user) |
| B | `rx_ext_controlled_renewal_fills` (rx_renewed / `approve_prescription_renewal_192bec69` / agent) | `rx_ext_agreement_fill_interval` (rx_compliance_updated / `sign_controlled_agreement_46ef2e3a` / user) |

- **Overlapping subjects.** Each extended policy writes a different event with a different tool. The subjects are rx_pharmacy_changed, rx_fills_authorized (reason replacement_fill), rx_compliance_updated and rx_renewed. None writes the same quantity as another extended policy.
- **Overlap with base on the same event.** rx_fills_authorized is shared with base `rx_fill_authorization` (new/renewal fills) and `rx_lost_stolen_replacement`. The replacement policy writes only the replacement_fill branch and its days' supply, which base leaves unstated. rx_renewed is shared with base `rx_fill_authorization`, and the fill count is overridden with a declaration (see override_declarations).
- **Triggers.** All four are `on_request`, and neither tree's root trigger overlaps the other's.
- **Eligibility and time anchors.** Every policy evaluates on the handling day (NOW):
  - move: the day of the move;
  - replacement: the day of the replacement;
  - agreement: the signing day;
  - renewal: the renewal date.
  Base eligibility is inherited, never weakened:
  - transfer status active/renewal_requested, transfer_allowed and one-time transfer;
  - replacement: class allows, fewer than 1 in the rolling 12 months, never controlled, police report by class;
  - controlled renewal: agreement, drug screen and PDMP currency, plus visit currency, with hold lapse after hold_resolution_days.
- **Cross-category read boundaries.** billing is read through `CFIELD('billing','variant_name')`, which picks the customer's single billing account. appointment and telehealth are read through `XLATEST`/`XCOUNT` filtered by the prescription's `prescribing_department`. No policy reads another rx holding: every `SUM/COUNT/LATEST` on `rx_events` is scoped to the target prescription by primary key.
- **Scope exclusivity.** By the prerequisite graph, trees A and B share no policy and no target tool, and together they cover all four extended policies. Each task's claimed scope (`charter_scope`) is masked until the reveal. The coordinator's SCOPE OK gate is cited, not re-run.
- **Claim coverage (observation O7).** The difficulty's claimed event types are rx_renewal_requested, rx_renewed, rx_renewal_held, rx_bridge_supply_authorized, rx_pharmacy_changed, rx_fills_authorized and rx_fills_voided.
  - The subject of `rx_ext_agreement_fill_interval` is `rx_compliance_updated`, which is not in that claim, and no other difficulty claims the rx category.
  - rx_renewal_requested, rx_renewal_held and rx_bridge_supply_authorized carry no extended policy.
  - Neither fact produces a second answer in either task world.

No conflict with a demonstrable consequence was found between extended policies. The one base/extended conflict is reported under override_declarations (F2).

### rule_compute_equivalence

For every binding, the `compute_basis` quotation is a verbatim substring of the policy's `rule`. I checked each binding against the rule text, and whitespace-normalised containment of `baseline.rule`, every `policy_source` and every `overwrite.replaced_by` was checked by script: all True.

**rx_ext_retail_move_fill_days**
- `billing_class` → payer tiers 34/60/90/else 30. This matches "a Medicaid Managed Care Account allows 34 days; … any other financial class allows the retail standard of 30 days".
- `days_dispensed_year` = SUM of rx_fill_dispensed `days_supply_per_fill` within 12 months, which is "every dispensing whose date falls inside that window". The tiers are ≥330 → 90, ≥270 → 60, else 30.
- `span_allowance`: fills ≥2 → days//fills ("rounded down"); fills = 1 → days; else 30. `days_to_expiry` = DAYS(NOW, expiration_date), "calendar days from the day of the move to its expiration date".
- `visit_allowance`: XLATEST completed appointment in the prescribing department; ≤183 → 90, ≤365 → 60, else or none → 30.
- `result` = MN of the four, "the shortest of four allowances".
- Sweep back: every rule sentence is implemented or is scope ("A move to a mail-order pharmacy … outside this policy"), and the recording sentence is carried by the tool argument `days_supply`. No empty promise, and compute invents no basis.

**rx_ext_replacement_fill_days**
- `lost_days`:
  - ≤14 → ceil(latest_fill_days·share/100) − elapsed, written as `-((-x)//100)` = "rounded up to a whole day";
  - ≤60 → latest_fill_days − elapsed;
  - else → fill_days = "one regular fill".
- `early_share`: 85/80/70/else `P('early_refill_threshold_pct')` = "the early-refill percentage of the prescription's class".
- `credit_days`:
  - fills ≥1 and days_to_expiry > fill_days → fills·fill_days;
  - fills ≥1 otherwise → MN(days_to_expiry, fill_days);
  - else → 0.
- `replaced_share`: prior replacement_fill authorizations in 24 months, crossed with no_show appointments in the prescribing department in 12 months, gives 75/50/100.
- `followup_trim`: last completed in-person visit >270 days, crossed with booked + confirmed count, gives 21/7/0.
- `result` = MX(0, int((lost − credit)·share/100) − trim). This is "any fraction of a day is dropped … never below zero". `int` truncates toward zero, which is how I read "dropped".
- The eligibility sentences (class allows, 12-month limit, never controlled, police report) carry no compute and are not scored quantities.

**rx_ext_agreement_fill_interval**
- `screening_allowance`: ≤183 → 30, ≤365 → 21, else or none → 14.
- `attendance_allowance`: (no_show == 0 and in-person ≤183) → 30; (no_show == 1 and in-person ≤183) → 21; else 14. "exactly one" is implemented as `== 1`.
- `regularity_allowance`: COUNT of dispensings in 12 months; 11–12 → 28, 9–10 → 21, else 14.
- `cadence_allowance`:
  - next booked/confirmed visit at 1–60 days → d // ceil(d / max_days_supply_per_fill);
  - else, if span_left = 183 − days_since_visit > 0, the same division on span_left;
  - else 14.
  "fewer than 183 days before" ⇔ span_left > 0.
- `coverage_allowance`: 30/28/21/14.
- `result` = MN of the five.

**rx_ext_controlled_renewal_fills**
- `class_fills` = MN(refills+1, total_days // fill_days).
- `reach_fills`:
  - next visit ≥1 day away → ceil(d / fill_days);
  - else, if the last in-person visit was <183 days ago → ceil((183 − since) / fill_days);
  - else class_fills.
- `reserve_fills`: 2/1/0.
- `pdmp_withhold`: >60 → 2, >30 → 1, else 0; no check on file → 100000 → 2.
- `adherence_adjust`: 170–190 → +1, >190 → −1, else 0.
- `followup_adjust`:
  - completed telehealth ≥1 and in-person ≥1 in 6 months → +1;
  - telehealth ≥1 and in-person 0 → −1;
  - else 0.
- `result` = MX(1, MN(refills+1, sum)), which is "never more than … plus one and never fewer than one".

**Factor ladders against rule and compute.** Every `factors[].ladder` tier of all four policies is a sentence of its `rule`, and every tier is a branch of its `decides` binding. No tier exists in only one of the two.

**Rule/compute conclusion:** equivalent in both directions. No SOURCE-POLICY finding here. The flat-statement shape of the baseline sentences is recorded as observation O2 below.

### action_binding_and_uuids

- **`(target_tool, computes)` pairs.** Each is claimed by exactly one policy:

  | Tool | Computes | Policy |
  | --- | --- | --- |
  | `move_prescription_pharmacy_221e1a97` | days_supply | move |
  | `authorize_replacement_fill_7c6c01e8` | days_supply_per_fill | replacement |
  | `sign_controlled_agreement_46ef2e3a` | days_supply | agreement |
  | `approve_prescription_renewal_192bec69` | fills | renewal |

  The move and the agreement both compute `days_supply`, but through different tools on disjoint subjects (a retail move versus a controlled agreement). A given prescription meets at most one of them in either tree.
- **Owners.**
  - move: `@tool(owner="user")`, consistent with "the patient moves it";
  - sign: owner `user`, consistent with base "Signing the agreement is the patient's own act; nobody signs it for the patient";
  - replacement and approve: owner `agent`.
- **Docstrings.** I grepped for before/after/first/then/once/until/prior/next inside the tool docstrings and found no hit. The only hit is the module docstring's generic "before calling". No docstring names another tool or states a sequence. The phrase "the initial fill included" in approve's `fills` argument is a count definition, not an ordering.
- **Tool bodies.** None checks status, eligibility, prerequisite or timing:
  - move: find → update pharmacy/transfer_count/days_supply.
  - replacement: find → create rx_events → update refills_remaining.
  - sign: update signed date/days_supply.
  - approve: find → optional void → create authorization → update.
  Nothing returns an error or a hint when a prerequisite is unresolved.
- **uuid8s.** The four are `221e1a97`, `7c6c01e8`, `46ef2e3a` and `192bec69`: distinct, with no shared prefix, no sequence and no adjacent values, and none reused within this module or `share_tools.py` (share tools carry no uuid suffix). Other difficulties' modules are outside my read domain.
- Conclusion: PASS.

### prerequisite_graph

| Policy | `prerequisite` | problem → | kind / gate | form | policy_source in own rule | resolved_by = depended-on target_tool |
| --- | --- | --- | --- | --- | --- | --- |
| rx_ext_retail_move_fill_days | `[]` | — | — | — | — | — |
| rx_ext_replacement_fill_days | 1 edge | rx_ext_retail_move_fill_days | value_input / `fill_days` (exists in compute) | state (no fallback_reason, correct) | verbatim, True | `move_prescription_pharmacy_221e1a97` ✓ |
| rx_ext_agreement_fill_interval | `[]` | — | — | — | — | — |
| rx_ext_controlled_renewal_fills | 1 edge | rx_ext_agreement_fill_interval | value_input / `fill_days` (exists in compute) | state (no fallback_reason, correct) | verbatim, True | `sign_controlled_agreement_46ef2e3a` ✓ |

- Every `problem` names an extended policy in this file, none names a base policy or itself, and the graph (2 edges, 2 disjoint trees) is acyclic.
- **`effect`.**
  - The move tool writes `days_supply`, so the replacement's `fill_days = F('days_supply')` changes. The edge is real.
  - The sign tool writes `controlled_agreement_signed_date = today` and `days_supply`. That satisfies the agreement-current requirement of `rx_controlled_safeguards` and changes the renewal's `fill_days`. The edge is real.
- No authoring-viewpoint phrasing ("in this task", "at the opening") appears in any `prerequisite` field.
- **`condition` against the sentence (observation O1).** Both edges' `condition` adds a clause the sentence does not carry:
  - replacement: "and prescriptions.days_supply carries the retail fill length recorded when the prescription was moved there";
  - renewal: "and prescriptions.days_supply carries the agreed fill interval recorded at that signature".

  Each sentence's state (the prescription stands at a retail pharmacy; the prescription shows an agreement signed within the class's months) can hold without that clause. Examples: a prescription first written to a retail pharmacy, or an agreement signed before this policy set any interval. So each `condition` is stricter than its sentence. Neither task world contains such a record (both opening states make the sentence's state itself false), so no consequence can be demonstrated. Recorded as an observation.

### prerequisite_sentences

**Edge A: replacement ← move.** Sentence: "A replacement fill's days' supply is fixed only after the prescription stands at a retail pharmacy rather than at a mail-order pharmacy."
1. Ordering connective: "only after" joins the policy's own result (the replacement's days' supply) to what it waits on. ✓
2. State form: "the prescription stands at a retail pharmacy rather than at a mail-order pharmacy". It is record-visible through `prescriptions.pharmacy_name` ("pharmacy the prescription is at"), and it names no action, performer or tool. ✓
3. It names no tool, no policy id, no snake_case token and no row id. ✓
4. Strength: it is a single-valued state, matching the first clause of `condition` (see O1 for the extra clause).
- **The one write that brings it about.** Among this difficulty's writes, only `move_prescription_pharmacy_221e1a97` changes `pharmacy_name`. Replacement, sign and approve do not touch it, and no share tool writes prescriptions. Unique.
- **Derivation.** The sentence says the replacement waits on the prescription standing at a retail pharmacy. The records show `pharmacy_name` naming a mail-order pharmacy. The only rule that moves a prescription to a retail pharmacy is `rx_ext_retail_move_fill_days` ("A prescription the patient moves to a retail pharmacy is dispensed there in fills of …"), whose target is the move tool (owner user). That rule also says the per-fill days' supply at the retail pharmacy becomes the retail fill length, which is what the replacement's "per-fill days' supply recorded on the prescription" then reads. This is one reading.
- The depended-on rule (move) does not restate the sentence. The replacement rule carries no second wording, no tool name and no other problem's id. ✓
- **Pharmacy type (observation O12).** The charter defines "retail" versus "mail-order" pharmacy only through names. The pharmacy-directory reference in the schema is not a queryable table. In both task worlds the names are self-describing ("… Mail Order Pharmacy", "Kroger Pharmacy #…"), so no second reading arises.

**Edge B: renewal ← agreement.** Sentence: "A controlled renewal's fills are not fixed until the prescription shows a controlled-substance agreement the patient signed within the class's agreement renewal months before the renewal date."
1. Connective: "not until". ✓
2. State form: record-visible through `prescriptions.controlled_agreement_signed_date` against `controlled_agreement_renewal_months`, with no action or tool named. ✓
3. No tool, id or snake_case token. ✓
4. Strength matches the base agreement-current requirement (see O1).
- **The one write that brings it about.** Only `sign_controlled_agreement_46ef2e3a` writes `controlled_agreement_signed_date` among this difficulty's tools. The base event rx_compliance_updated has no other tool. Unique.
- **Derivation.** The sentence names the agreement-signed state. The records show the signed date outside the class months. The rule that records a patient's agreement signature is `rx_ext_agreement_fill_interval` ("When the patient signs a new controlled-substance agreement … recorded on the prescription as its per-fill days' supply on the day the patient signs"), whose target is the sign tool (owner user, consistent with base "nobody signs it for the patient"). This is one reading.
- **Other text in the renewal rule about the dependency (observation O9).** The rule also carries "Completing the missing requirement lets the held renewal be approved from hold, and every other requirement of the class must still be current on the renewal date." This is a generic restatement of base `rx_hold_lapse` ("Completing the requirement … lets the renewal be approved from hold"). It names no specific requirement, grounds the same order as edge B, and grounds no different order.
- **Base order sentence (O9).** Base `rx_controlled_safeguards` states an order: "a controlled prescription is renewed only when a controlled-substance agreement signed by the patient within controlled_agreement_renewal_months … is on file". Tree B does not rest on it alone, because the extended rule carries its own prerequisite sentence. Observation.
- **Undeclared cross-problem orders.** None found in the four extended rules. The replacement's eligibility sentence ("no replacement fill was posted on it in the rolling 12 months") is a same-policy eligibility, not a cross-problem order.
- Conclusion: PASS, with observations O1, O9 and O12.

### override_declarations

**rx_ext_retail_move_fill_days vs `rx_pharmacy_transfer`**, sentence by sentence:
- "A patient may move the remaining fills … where transfer_allowed is true": followed.
- "the prescription keeps its fills and expiration and only the pharmacy changes": handled differently, since days_supply also changes. This is **declared** in `overwrite`, and the merged meaning is unique.
- "Where one_time_transfer_only is true … cannot be transferred again": inherited, not contradicted.
- "The prescription status is active or renewal_requested when the pharmacy is changed": inherited.
- "A Schedule II prescription is not transferred": inherited.
- "A specialty prescription can move only between designated specialty pharmacies": inherited.
- "… transferred_care": not touched.

**Finding F2 (SOURCE-POLICY RED, charter-level, latent).** The retail fill length can exceed base `rx_fill_authorization` "one fill never exceeds max_days_supply_per_fill", and no `overwrite` names that sentence. The move policy's `base_policy_refs` does not list `rx_fill_authorization`. See findings.

**rx_ext_replacement_fill_days vs `rx_fill_authorization`, `rx_lost_stolen_replacement`, `rx_fill_timing`** (`overwrite: []`):
- Replacement rules followed: one fill; authorization_reason replacement_fill; limit of 1 per rolling 12 months; police report where the class requires one; never controlled; damaged counts as lost.
- `rx_fill_authorization`: "Fills are authorized only while the prescription status is active" is inherited.
- `rx_fill_authorization`: "one fill never exceeds max_days_supply_per_fill" is respected, because lost_days ≤ the latest dispensing's supply or fill_days, and credit ≥ 0.
- `rx_fill_timing`: "an earlier fill is refused unless … an authorized replacement or bridge fill" is consistent.
- No base sentence states the replacement's days' supply, so no override exists to declare. `overwrite: []` stands.

**rx_ext_agreement_fill_interval vs `rx_controlled_safeguards`, `rx_specialty_access`** (`overwrite: []`):
- Agreement currency, the patient's own signature, and the safeguards by schedule are followed.
- No base sentence fixes `days_supply` at signing. The base rx_compliance_updated field list does not include days_supply, but no base sentence says "nothing else changes", so nothing contradicts it.
- `rx_specialty_access` is listed but governs no quantity this policy writes (O8).

**rx_ext_controlled_renewal_fills vs `rx_renewal_eligibility`, `rx_fill_authorization`, `rx_controlled_safeguards`, `rx_hold_lapse`**:
- The fill-count sentence of `rx_fill_authorization` is replaced, and this is **declared**. The replacement cap "never more than refills+1" drops the total-days term. For every controlled class, refills+1 fills of at most max_days_supply_per_fill still fit the class total (III-V: 6 × 30 = 180; II: 1 × 30 ≤ 90), so no second value arises.
- Void as superseded, new expiration, and every requirement current on the renewal date: followed.
- Hold order: followed. Lapse after hold_resolution_days: inherited.
- Nurse protocol only where `prescriber_review_required` is false: inherited, and it bears on who approves (O10).

**Three disguised forms:**
- No anonymous intermediate factor overrides a base quantity.
- No 0/1 multiplier zeroes a base-fixed amount.
- No base branch is dropped: the replacement's eligibility branches are carried in prose.
- No author note calls base output a "wrong value".

### factor_ladders

| Policy | Factor | Effect | decides | Tiers (fall-through last) | Multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| move | payer_retail_allowance | parameter | payer_allowance | 34 / 60 / 90 / 30 | no | billing |
| move | dispensing_adherence_allowance | parameter | adherence_allowance | 90 / 60 / 30 | no | — |
| move | authorization_span_allowance | method | span_allowance | days÷fills (≥2) / all days (=1) / 30 | no (one prescription row) | — |
| move | visit_recency_allowance | parameter | visit_allowance | 90 / 60 / 30 | no | appointment |
| replacement | lost_supply_count | method | lost_days | ⌈supply·share⌉−elapsed / supply−elapsed / one fill | yes (rx_events + billing via share) | — |
| replacement | payer_early_refill_share | parameter | early_share | 85 / 80 / 70 / class % | no | billing |
| replacement | standing_fill_credit | method | credit_days | fills·fill_days / min(days_to_exp, fill_days) / 0 | no (one prescription row) | — |
| replacement | repeat_loss_share | parameter | replaced_share | 75 / 50 / 100 | yes (rx_events replacement rows ∧ appointment no_shows) | appointment |
| replacement | followup_trim | parameter | followup_trim | 21 / 7 / 0 | yes (completed visit ∧ booked/confirmed visit, distinct records) | appointment |
| agreement | screening_allowance | parameter | screening_allowance | 30 / 21 / 14 | no | — |
| agreement | attendance_allowance | parameter | attendance_allowance | 30 / 21 / 14 | yes (no_show rows ∧ completed row) | appointment |
| agreement | dispensing_regularity_allowance | parameter | regularity_allowance | 28 / 21 / 14 | no | — |
| agreement | visit_cadence_allowance | method | cadence_allowance | d÷⌈d/max⌉ to booked visit / same on 183-day horizon / 14 | yes (booked/confirmed ∧ completed) | appointment |
| agreement | coverage_allowance | parameter | coverage_allowance | 30 / 28 / 21 / 14 | no | billing |
| renewal | visit_reach_fills | method | reach_fills | ⌈d/fill⌉ to booked visit / ⌈(183−since)/fill⌉ / class fills | yes | appointment |
| renewal | screening_reserve_fills | parameter | reserve_fills | 2 / 1 / 0 | yes (no_show rows ∧ prescription drug-screen date) | appointment |
| renewal | database_check_withholding | parameter | pdmp_withhold | 2 / 1 / 0 | no | — |
| renewal | adherence_adjustment | parameter | adherence_adjust | +1 / −1 / 0 | no | — |
| renewal | followup_adjustment | parameter | followup_adjust | +1 / −1 / 0 | yes (telehealth ∧ appointments) | telehealth (O6) |

- **Binding sets.** Within each policy they are disjoint, and every `decides` is an input binding, never `result`.
- **Tiers in the rule.** Every tier's condition and value/method is stated in the `rule` prose. Every ladder has at least three tiers, and the tiers are pairwise disjoint as stated.
- **Baselines.** Each policy's `baseline.rule` is a sentence of its `rule` and names its `params`:
  - move: `retail_standard_days` = 30;
  - replacement: one regular fill, no params;
  - agreement: `start_interval_days` = 14;
  - renewal: the class fills.

  Every factor's fall-through equals the value its baseline gives:
  - move: all four fall-throughs are 30 = baseline;
  - replacement: lost_days → fill_days, credit → 0, share → 100, trim → 0; early_share → class % (see O5);
  - agreement: all 14;
  - renewal: reach → class_fills, others 0.
- **Counts per policy, as declared.** Each set is within 4–6, with ≥2 parameter and ≥1 method:
  - move: 4 (3 parameter, 1 method);
  - replacement: 5 (3 parameter, 2 method);
  - agreement: 5 (4 parameter, 1 method);
  - renewal: 5 (4 parameter, 1 method).
- **Tree-level coverage.** Tree A has multi-source factors (repeat_loss_share, followup_trim) and cross-difficulty billing/appointment factors. Tree B has multi-source factors (attendance, reserve, followup) and cross-difficulty appointment/billing factors.
- **Tier distinctness. Finding F1 (SOURCE-FACTOR RED).** `authorization_span_allowance` tiers 1 and 2 select the same method. "the calendar days from the move to the expiration date divided evenly among the fills remaining, rounded down" applied to exactly one remaining fill is `days // 1 = days`, which is "all the calendar days from the move to the expiration date". One tier is written as two. The ladder has two distinct methods (divide by fills; standard 30), so the factor is struck. That leaves `rx_ext_retail_move_fill_days` with 3 surviving factors (all `parameter`) and **no `method` factor**, below the 4-factor and 1-method floors. See findings.
- **Label honesty and business realism.**
  - `lost_supply_count` tiers 1 and 2 are the same "share of supply less elapsed" shape with share = early-refill % against 100 %. Tier 3 is a different algorithm (a constant fill), so the `method` label holds (O4).
  - `visit_cadence_allowance` and `visit_reach_fills` apply one division to two different anchors: the booked visit, and the 183-day horizon from the last in-person visit. The quantity divided differs, so I do not count them as the same method (O3).
  - Payer tiers are realistic: Medicaid 34-day supply limits and payer refill-too-soon percentages of 85/80/70.
  - The other conditions (visit recency, dispensing regularity, drug-screen age, PDMP age, missed visits for controlled prescriptions) are ones that primary-care and behavioural-health prescribing actually weighs.
  - The replacement's `repeat_loss_share` (tied to missed visits) and `followup_trim` are unusual for a lost-medication replacement. Still, I cannot show that no practice weighs visit adherence when deciding how much to replace. Observation O11.
- **Other structural observations.**
  - `payer_early_refill_share`: for a Specialty Medication Prescription the class % is 80, the same value as the Medicare tier. No task world is a specialty prescription (O5).
  - `followup_adjustment` is labelled `cross_difficulty: telehealth`, but no difficulty in `blueprint.yaml` claims the telehealth category (the five difficulties claim appointment, billing, referral, rx and payplan). The renewal still has appointment-reading factors (O6).

### findings

**F1: SOURCE-FACTOR RED (charter structure). Demonstrated in task 0.**
- **Symptom:** in `rx_ext_retail_move_fill_days`, the `authorization_span_allowance` ladder has two tiers that select one method.
- **Root cause:** the tier "exactly one fill remains → all the calendar days from the move to the expiration date" is the tier-1 method "those days divided evenly among the fills remaining, rounded down" evaluated at fills = 1.
- **Evidence:** rx.extended.yaml, `rx_ext_retail_move_fill_days.rule`: "where two or more fills remain, it is those days divided evenly among the fills remaining, rounded down to a whole day; where exactly one fill remains, it is all of those days". The compute is `span_allowance: "(days_to_expiry // fills_left) if fills_left >= 2 else (days_to_expiry if fills_left == 1 else K('retail_standard_days'))"`. For fills_left = 1, `days_to_expiry // 1 == days_to_expiry`.
- **Consequence:** the ladder has two distinct outcomes, not three. The factor fails the tier test and is struck. The policy is left with 3 factors and 0 `method`.
- **Affected:** the `factors` and `rule` of `rx_ext_retail_move_fill_days`, and task 0 (whose tree contains this policy).

**F2: SOURCE-POLICY RED (charter-level, latent). Bears on no task world of this difficulty.**
- **Symptom:** the retail fill length can exceed the class's `max_days_supply_per_fill`, and no override is declared.
- **Evidence:**
  - Base `rx_fill_authorization`: "… and one fill never exceeds max_days_supply_per_fill."
  - Extended `rx_ext_retail_move_fill_days`: "its per-fill days' supply at the retail pharmacy becomes the retail fill length set out in this policy. The retail fill length is the shortest of four allowances …", with allowances up to 90.
  - The overwrite names only the `rx_pharmacy_transfer` clause.
- **Same situation, two conclusions:**
  - A Schedule III-V Controlled Prescription (transfer_allowed true, one-time; max_days_supply_per_fill 30), patient on a Commercial PPO/POS Account, 12 monthly 30-day dispensings in 12 months (360 ≥ 330 → 90), a completed in-person visit 60 days ago (→ 90), one fill left with 100 days to expiration (→ 100). The extended policy gives MN(90, 90, 100, 90) = 90. Base caps one fill at 30.
  - The same holds for an Acute Short-Course Prescription (max 14, transfer allowed): one fill, 29 days to expiration, commercial, visit recent, under 270 days dispensed gives MN(90, 30, 29, 90) = 29 > 14.
- **Consequence in this difficulty's worlds:** none. Task 0 is a Standard Maintenance prescription with a result of 34 ≤ 90.
- **Affected:** the `overwrite` and `base_policy_refs` of `rx_ext_retail_move_fill_days`.

**Observations** (none of these demonstrates a consequence in a task world):
- **O1:** both edges' `condition` is stricter than its prerequisite sentence (the extra `days_supply` clause).
- **O2:** each extended rule opens with its baseline sentence stated flatly, with no "by default" connective:
  - move: "dispensed there in fills of the retail standard of 30 days";
  - replacement: "dispenses one regular fill … the per-fill days' supply recorded on the prescription";
  - renewal: "A controlled renewal approved from hold authorizes the smaller of …", which is the very base clause its `overwrite` supersedes;
  - agreement: "sets the starting fill interval of 14 days".

  The later procedural text in each rule computes the governing number and refers back to the baseline ("the class fills of the first sentence", "the retail standard of 30 days" as each fall-through). A reader of the whole rule reaches one number. Whether the rendered KB keeps that reconciliation is a question for the KB audit.
- **O3:** the reach/cadence tiers 1 and 2 are one division on two anchors.
- **O4:** the `lost_supply_count` tiers 1 and 2 differ by a percentage.
- **O5:** the Specialty class % equals the Medicare tier (80).
- **O6:** the telehealth "cross_difficulty" category is claimed by no difficulty.
- **O7:** `rx_compliance_updated` is outside the difficulty's claimed event types; three claimed events have no extended policy.
- **O8:** `rx_ext_agreement_fill_interval` lists the unrelated `rx_specialty_access` in `base_policy_refs`.
- **O9:** there is a base order sentence (`rx_controlled_safeguards`) and a generic hold-completion restatement in the renewal rule. Both ground the same order as edge B.
- **O10 (charter fact; bears on task 1).** The charter does not say who may approve a renewal when `prescriber_review_required` is true:
  - `parameter_schema.prescriber_review_required` reads "Whether each renewal needs the prescriber's own signature (false = nurse refill protocol may approve)", and Schedule III-V = true.
  - `rx_fill_authorization` reads "A renewal approved under the nurse refill protocol (only where prescriber_review_required is false) …".
  - The lifecycle gives `on_hold → active` `by: agent`: "The missing requirement is met and the renewal is approved."
  - `rx_hold_lapse` and the extended renewal rule read "Completing the missing requirement lets the held renewal be approved from hold".
  - The approve tool is owner `agent`, and no schema field records a prescriber sign-off.

  Task 1 carries the demonstration attempt.
- **O11:** the business realism of the replacement's missed-visit share and follow-up trim.
- **O12:** retail versus mail-order is known only from pharmacy names.

## closing_checklist

(Written after the reveals. See the appended section below.)

### closing_checklist (written after the reveals, 2026-09-24T23:38Z onward)

- **Per-task files.** `0.md` and `1.md` match tasks 0 and 1 one-to-one, and this file sits alongside them. This is revision 1, with no older revisions. Each frozen section was on disk before any GT was read (mtimes 23:36:10Z, 23:37:08Z and 23:38:01Z; reveal 23:38:06Z). Every task file has a `source_gt_comparison` section.
- **Scope and closure.** The revealed `charter_scope` values are:
  - task 0: {rx_ext_retail_move_fill_days, rx_ext_replacement_fill_days} with tools {move…221e1a97, authorize…7c6c01e8};
  - task 1: {rx_ext_agreement_fill_interval, rx_ext_controlled_renewal_fills} with tools {sign…46ef2e3a, approve…192bec69}.

  They are pairwise disjoint, each spans its whole tree, and together they cover all four extended policies. Task tools and GT are closed, since every gold write uses a tool of its own scope. The uuid8s are independent (see `### action_binding_and_uuids`).
- **Trees.** Each tree has 1 prerequisite problem, 1 value_input edge and one `owner=user` write (the move; the signature), with no cycle. The difficulty-wide graph (2 edges, disjoint) is acyclic.
- **Factors: NOT CLOSED.** Task 0's move computation fails the factor structure (F1): 3 surviving factors and 0 `method` after the span ladder is struck. Every other computation (task 0 replacement; task 1 agreement and renewal) declares a self-sufficient baseline and 4–6 factors. Each of those factors bears weight against an honest baseline, and each baseline-only number (34, 14, 6) differs from gold.
- **Gates.** The instantiation-stage gates were not re-run on a final form, because the difficulty does not close in this revision. The coordinator's pre-audit snapshot (all green) is cited in `## charter_global_frozen`.

**Per-task verdicts:**

| Task | Policy self-consistency | Problem tree | Factors | Unique solution | Overall |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | **SOURCE-FACTOR RED** (F1) | PASS | **SOURCE-FACTOR RED** |
| 1 | PASS | PASS | PASS | PASS | **PASS** |

**Difficulty result:** it does **not** pass the source-layer audit in revision 1, because of task 0's SOURCE-FACTOR RED (F1). Charter-level F2 (SOURCE-POLICY, latent: no `max_days_supply_per_fill` cap on the retail fill length, undeclared) bears on no task world of this difficulty. It stays recorded as a charter defect.

## revision_2

### charter_global_frozen (revision 2)

- **Audit round:** re-audit round 2 by the same independent auditor.
- **Freeze time:** 2026-09-24T23:45Z. Check this against the file mtime, not the typed header. Nothing in this charter-global section is derived from the round-2 task JSONs, which had not been opened when it was written.
- **Input hashes:**
  - `rx.extended.yaml` sha256 `72a2a68440b15754061ac2169df9c73e1efd6df42968bf33cc72b67cc3709cb0`, **changed** from r1 `31f55822…`, so every charter-global section is re-derived below.
  - `task_tools.py` sha256 `8d4278870c4b4b7be9c6e3f90459304285b13c9039f895f9612279cfc86619b7`, unchanged.
  - Masked views `r2/0.view.json` `5c2bcd83…` and `r2/1.view.json` `b4697415…`: re-verified, and identical to r1. `frozen_time`, `user_scenario` and `initial_state` are therefore unchanged.
- **Base copy.** All ten base keys are still YAML-equal to `blueprint/products/rx.yaml`.
- **Gate snapshot.** The coordinator's post-rework run is cited, not re-run: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. Traceability is deferred.
- **contamination_disclosure.** The auditor has read round-1 GT: `tasks/0.json` and `tasks/1.json` as they stood at 23:38Z, including expected values 34/21 and 21/5. That is inherent to a same-auditor re-audit, and it is disclosed here. The round-2 task JSONs, the rewritten `worklog.md` and the reworker's reasons were **not** opened before the freeze. Round-1 text is preserved untouched above.
- **Charter changes found by re-reading the four extended policies against my round-1 reading:**
  1. **move:**
     - `base_policy_refs` gains `rx_fill_authorization`;
     - the rule gains "…and it never exceeds the largest days' supply per fill of the prescription's class", with `result` now `MN(…, P('max_days_supply_per_fill'))`;
     - the authorization-span allowance is rewritten, with new binding `written_fill_days = F('days_supply')` and ladder: fits past expiration → days ÷ fills; fits within → keep the written per-fill supply; none → 30.
  2. **replacement:** the edge `condition` is reduced to the sentence's state.
  3. **agreement:** no change found.
  4. **renewal:**
     - new sentence: "For a class whose renewals need the prescriber's own signature, that review is the one that placed the renewal on hold naming its single missing requirement, so the approval from hold is recorded without a second signature once that requirement is complete.";
     - the edge `condition` is reduced to the agreement-date state;
     - `followup_adjustment.cross_difficulty` goes from `telehealth` to `appointment`.

### policy_conflict_scan (revision 2)

The trees, subjects, target tools, triggers, time anchors and cross-category reads are unchanged from revision 1. The move cap is a new reading of the class parameter, and it narrows the move's value range without touching any other policy. The new renewal sentence governs only who records a from-hold approval for prescriber-review classes. It does not touch the fill count or any other policy's subject. **No conflict. The O7 claim-coverage observation still holds**: the agreement subject `rx_compliance_updated` remains outside the difficulty claim.

### rule_compute_equivalence (revision 2)

- **Script checks.** Each check normalised whitespace and split `compute_basis` quotes on "...".
  - Every `baseline.rule`, `policy_source` and `overwrite.replaced_by` is verbatim in its rule.
  - Every `compute_basis` quote is verbatim, **except** renewal `compute_basis.missed_visits`: "missed visits with the prescribing department in the last 12 calendar months …". The rule says "no missed visit with the prescribing department in the last 12 calendar months" and "one or more missed visits with that department in those 12 months".
- **About that quote (observation N2).** The text is identical in the r1 charter. My r1 section said it had been checked, but my r1 script covered only baseline, policy_source and replaced_by. This is an **r1 audit miss, disclosed**. The quantity it names (no_show appointments of the prescribing department, 12 months) is stated in the rule in two verbatim sentences, so compute invents no basis. No consequence can be shown: N2 is an observation.
- **Move, new bindings:**
  - `written_fill_days` ⇐ "the per-fill days' supply the prescription carries before the move";
  - `span_allowance` ⇐ the three-branch sentence. Its conditions `fills_left >= 1 and fills_left * written_fill_days > days_to_expiry` implement "at least one fill remains and those fills, each at the per-fill days' supply the prescription carries, would run past the expiration date", and the else-branch implements "would end on or before";
  - `result` ⇐ "…and it never exceeds the largest days' supply per fill of the prescription's class" via `P('max_days_supply_per_fill')`.

  Both directions hold.
- **Other policies:** no compute change. The r1 conclusions stand.

### action_binding_and_uuids (revision 2)

`task_tools.py` is unchanged (same hash), and each `(target_tool, computes)` pair is still claimed once. The r1 section is carried forward on the hash. **PASS.**

### prerequisite_graph (revision 2)

- The two edges have the same problem, kind, gate, form and `resolved_by` as r1. The graph is acyclic.
- **`condition` now matches its sentence (O1 closed):**
  - replacement: "prescriptions.pharmacy_name names a retail pharmacy rather than a mail-order pharmacy";
  - renewal: "prescriptions.controlled_agreement_signed_date falls within controlled_agreement_renewal_months calendar months before the renewal date".

  Neither strengthens nor weakens its sentence.
- `effect` still describes the `fill_days` change. That is an effect of the resolving write, not a condition, and it is true of both tools' bodies.

### prerequisite_sentences (revision 2)

- Both prerequisite sentences are unchanged and verbatim. The four-point tests and the single-write derivations of r1 hold.
- **New sentence in the renewal rule** ("…so the approval from hold is recorded without a second signature once that requirement is complete"):
  - It carries an ordering connective ("once") on the generic "missing requirement". In task-1-shaped worlds that is the same dependency as edge B.
  - It names no tool or id, and it grounds no different order: the approval still follows completion of the requirement.
  - Like the r1 sentence "Completing the missing requirement lets the held renewal be approved from hold", it is a generic second wording. **O9 is extended to cover it, as an observation.**

### override_declarations (revision 2)

- **Move vs `rx_fill_authorization` "one fill never exceeds max_days_supply_per_fill":** now followed. The rule states the cap and compute applies `MN(…, P('max_days_supply_per_fill'))`.
  - Replaying the r1 F2 situations: Schedule III-V / Commercial / 360 dispensed / visit 60 days back / 1 fill with 100 days left gives MN(90, 90, …, 30) ≤ 30. Acute gives ≤ 14.
  - No base sentence is contradicted, so no `overwrite` is needed. `rx_fill_authorization` is now listed in `base_policy_refs`. **F2 closed.**
- **Baseline sentence against the cap (observation N1, new).** The move's `baseline.rule` and first rule sentence say "dispensed there in fills of the retail standard of 30 days". For an Acute Short-Course Prescription (max_days_supply_per_fill 14, transfer allowed), that sentence gives 30, while the rule's cap and base give 14.
  - This is the same flat-baseline shape as O2. The full rule resolves it, because the cap sentence governs.
  - Neither task world is an Acute prescription.
- **Renewal: new prescriber-review sentence vs the base texts:**
  - `parameter_schema.prescriber_review_required` ("Whether each renewal needs the prescriber's own signature") is not contradicted. The sentence identifies the prescriber's review with the review that placed the hold, and adds no nurse-protocol approval.
  - `rx_fill_authorization`'s nurse-protocol sentence is not contradicted.
  - Base `rx_renewal_eligibility` says a held renewal names "the first missing requirement in this order". The new sentence says "naming its single missing requirement". Where a held renewal lacks two requirements, the sentence's premise ("single") does not describe the hold, and it does not say whether a second signature is then needed. **Observation N3 (latent):** in task 1's world exactly one requirement (the agreement) is missing, so there is no consequence.
- The other r1 sentence-by-sentence conclusions are unchanged. **No undeclared override with a demonstrable consequence.**

### factor_ladders (revision 2)

- **Move, `authorization_span_allowance`** (method):
  - Tier 1 is `days_to_expiry // fills_left` when `fills_left × written > days_to_expiry`. Under that condition the value is strictly less than `written`.
  - Tier 2 is `written_fill_days`.
  - Tier 3 is 30.

  These are three distinct methods: fit-to-expiration, keep-as-written and standard. No two tiers can select the same method or value by construction (tier 1 < written = tier 2). Business reading: fitting the remaining fills to the time left on the authorization, or else keeping the written fill length, is what a pharmacy transfer actually does. The fall-through is 30, which equals the baseline. The tier conditions are all in the rule.

  **F1 closed.** The move now keeps 4 factors (3 parameter, 1 method).
- **Renewal, `followup_adjustment`:** `cross_difficulty: appointment`. The factor's compute reads `XCOUNT('appointment','appointments', …, status='completed')` (`inperson_visits`) as one conjunct, so the label is honest. **O6 closed.**
- **Other ladders:** unchanged. The r1 conclusions and observations O3, O4, O5 and O11 stand.
- **Counts:**

  | Policy | Factors | parameter | method |
  | --- | --- | --- | --- |
  | move | 4 | 3 | 1 |
  | replacement | 5 | 3 | 2 |
  | agreement | 5 | 4 | 1 |
  | renewal | 5 | 4 | 1 |

  Tree A has multi-source factors (repeat_loss_share, followup_trim) and cross-difficulty billing/appointment factors. Tree B has multi-source factors (attendance, reserve, followup) and cross-difficulty appointment/billing factors.

### findings (revision 2)

| Item | Status | Evidence |
| --- | --- | --- |
| F1 | **closed** | new span ladder (above) |
| F2 | **closed** | cap stated and computed; `rx_fill_authorization` referenced |
| O1 | **closed** | both conditions reduced to their sentences' states |
| O6 | **closed** | the label now names appointment, and the factor reads appointments |
| O10 | **closed as a charter question** | the renewal rule now says how a from-hold approval of a prescriber-review class is recorded; its latent premise gap is N3 |
| O2, O3, O4, O5, O7, O8, O9 (extended), O11, O12 | **unchanged, still observations** | I checked each against the r2 charter; none now demonstrates a consequence |
| N1 (new, observation) | — | move baseline sentence (30) above the cap for classes whose cap is under 30 |
| N2 (observation; present in r1, missed by the r1 audit) | — | the renewal `compute_basis.missed_visits` quote is not verbatim |
| N3 (new, observation, latent) | — | "naming its single missing requirement" versus base "the first missing requirement" |

No charter-global RED in revision 2.

### closing_checklist (revision 2, written after the round-2 reveals at 23:46:03Z)

- **Files and freezes.** `0.md` and `1.md` each carry `## revision_2` with a frozen derivation (mtime 23:45:57Z), then a comparison. This file's revision_2 charter-global section was frozen at 23:45:24Z, before either reveal. Revision 1 text is untouched.
- **Scope.** Round-2 `charter_scope`: task 0 {move, replacement}, task 1 {agreement, renewal}. Pairwise disjoint, each spanning its whole tree, jointly covering all four extended policies. The task tools are unchanged, with independent uuid8s.
- **Trees.** Each has 1 prerequisite problem, 1 value_input edge and one `owner=user` write, and is acyclic. The difficulty-wide graph is acyclic.
- **Factors.** Every computation has a self-sufficient baseline and 4–5 factors:
  - move: 3 parameter / 1 method;
  - replacement: 3 / 2;
  - agreement: 4 / 1;
  - renewal: 4 / 1.

  Every ladder has ≥3 tiers stated in its rule, with distinct outcomes; F1 is closed. Every factor bears weight on its task's world. The baseline-only numbers (30, 34, 14, 6) all differ from gold (34, 21, 21, 5). Multi-source and cross-difficulty factors are present in both tasks.
- **Round-1 REDs:**
  - F1 (SOURCE-FACTOR, task 0): **closed**;
  - F2 (SOURCE-POLICY, latent): **closed**.
- **Other r1 items:** O1, O6 and O10 closed. O2, O3, O4, O5, O7, O8, O9, O11 and O12 remain observations.
- **New observations:** N1 (baseline sentence above the cap for sub-30 classes, latent), N2 (non-verbatim `compute_basis` quote, present since r1) and N3 (single versus first missing requirement, latent). None demonstrates a consequence.
- **Gates.** Not re-run by the auditor. The coordinator's post-rework snapshot (all green; traceability deferred to KB publication) is cited as the final-form gate run.

**Per-task verdicts, revision 2:**

| Task | Policy self-consistency | Problem tree | Factors | Unique solution | Overall |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | **PASS** |
| 1 | PASS | PASS | PASS | PASS | **PASS** |

**Difficulty result, revision 2:** passes the source-layer audit.

## revision_3

### charter_global_frozen (revision 3)

- **Audit round:** re-audit round 3 by the same independent auditor. This section was written before the round-3 task JSONs were opened; the file mtime is authoritative.
- **Inputs:**
  - views `audits/_coordinator/views/policy_task/prescription_renewal_handling/r3/0.view.json` `5c2bcd83…` and `r3/1.view.json` `b4697415…`: re-verified, byte-identical to r1/r2;
  - `rx.extended.yaml` sha256 `72a2a68440b15754061ac2169df9c73e1efd6df42968bf33cc72b67cc3709cb0`, **unchanged since r2**;
  - `task_tools.py` sha256 `2b72c5b4f7c630aa95109c8bb2d1b859230b6514856742f5d344d1c1b24ebe6e`, **changed** from `8d4278870c4b…`.
- **contamination_disclosure.** This auditor has read the r1 and r2 GT of both tasks. The round-3 task JSONs were not opened before this freeze. The difficulty's `worklog.md` was never opened in any round.
- **Gate snapshot** (coordinator's run, cited not re-run): REPLAY OK (`--check`), EXTENDED OK, TASK TOOL CONTRACT OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK, LINT OK.

**Carried forward on unchanged hashes.** The charter hash `72a2a684…` equals the one revision 2 was derived from. These sections of `## revision_2` are therefore carried forward by reference, with no re-derivation:
- `policy_conflict_scan`
- `rule_compute_equivalence`
- `prerequisite_graph`
- `prerequisite_sentences`
- `override_declarations`
- `factor_ladders`

Their observations (O2, O3, O4, O5, O7, O8, O9, O11, O12, N1, N2, N3) stand unchanged. Base-copy equality was re-checked and still holds.

### action_binding_and_uuids (revision 3, re-derived because `task_tools.py` changed)

**Exact extent of the change.** I reverted exactly two edits in the r3 file:
1. restoring `from datetime import date, timedelta` above `from erlbench import ToolContext, tool`;
2. replacing the new integer block (from `# Last date to fill …` to just before the final `ctx.update(...)` of `approve_prescription_renewal_192bec69`) with the r2 line `expires = (date.fromisoformat(today) + timedelta(days=days - 1)).isoformat()`.

The result hashes to **`8d4278870c4b4b7be9c6e3f90459304285b13c9039f895f9612279cfc86619b7`**, the r1/r2 file byte for byte. So:
- every docstring, signature, owner decorator, parameter, default, receipt key, `ctx.find`/`ctx.create`/`ctx.update` field set and make_id seed is byte-identical to r2;
- `move_prescription_pharmacy_221e1a97`, `authorize_replacement_fill_7c6c01e8` and `sign_controlled_agreement_46ef2e3a` are entirely unchanged;
- the uuid8s (`221e1a97`, `7c6c01e8`, `46ef2e3a`, `192bec69`) are unchanged, and the `(target_tool, computes)` bindings are unchanged.

**Date semantics.** The new block is the standard proleptic-Gregorian days-from-civil / civil-from-days integer conversion. It computes today + validity − 1 and formats the result as `YYYY-MM-DD`.
- I lifted the block verbatim into a test function and compared it with `date.fromisoformat(t) + timedelta(days=v − 1)`. The test covered every day from 1900-03-01 through 2200-12-31 and v ∈ {1, 2, 28, 29, 30, 31, 59, 60, 61, 90, 180, 365, 366, 730, 1461}. That set includes all six class validity values (30/365/365/180/90/365) and the 365 fallback.
- **1,648,185 cases, 0 mismatches.** These cover leap days, century years (1900 and 2100 are not leap years; 2000 is) and month and year rollovers.
- Task 1's world: 2026-09-17 with 180 days gives **2027-03-15**, the same as r1/r2.
- The date semantics are identical across the charter's domain.

**Other contract checks.**
- The new file contains none of `erlbench/validate.py` `_FORBIDDEN_TOKENS`. Its only import is `from erlbench import ToolContext, tool`.
- The added text is a code comment ("Last date to fill = today + validity - 1 …"), not a docstring. It names no other tool and states no sequence.
- The tool still checks no status, agreement, hold or other prerequisite.

**PASS. No regression.**

### findings (revision 3)

- **No RED.**
- The single change (the forbidden-token removal) is proven confined, and it is semantically identical to r2.
- r2 status is carried forward: F1 and F2 closed; O1, O6 and O10 closed; the remaining observations unchanged.

### closing_checklist (revision 3, written after the round-3 reveals at 05:05:24Z)

- **Files and freezes.** Each of `0.md` and `1.md` carries `## revision_3`: a frozen section (05:05:13Z), then a comparison. Revisions 1 and 2 are untouched.
- **Charter.** Unchanged (`72a2a684…`). All charter-global r2 conclusions are carried forward on that hash. Coverage, disjoint scopes, trees (1 prerequisite, 1 value_input edge, 1 user write each; acyclic) and factor structure (4/5/5/5 factors, all bearing weight, baseline-only numbers differing from gold) are unchanged.
- **Tool module.** Changed (`2b72c5b4…`), and the change is proven confined:
  - reverting the two edits reproduces the r2 hash `8d427887…` byte for byte;
  - the date arithmetic is proven identical to r2's `date + timedelta` on 1,648,185 cases (1900–2200 × 15 validities, including every class value);
  - the file contains none of the forbidden tokens;
  - the contract (docstrings, parameters, receipts, owners, uuid8s) is unchanged;
  - no tool checks a prerequisite.
- **Task JSONs.** View fields and every scored field are equal to r2. `db_closure` equals the initial-state rows, with ordering-only differences.
- **Gates.** `replay_tasks.py --check` was re-run by the auditor (REPLAY OK, 2 tasks). The other gates are cited from the coordinator's r3 snapshot (all OK, including LINT OK).
- **Round-2 REDs to verify:** none existed. No new defect, no regression.

**Per-task verdicts, revision 3:**

| Task | Policy self-consistency | Problem tree | Factors | Unique solution | Overall |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | **PASS** |
| 1 | PASS | PASS | PASS | PASS | **PASS** |

**Difficulty result, revision 3:** passes the source-layer audit.
