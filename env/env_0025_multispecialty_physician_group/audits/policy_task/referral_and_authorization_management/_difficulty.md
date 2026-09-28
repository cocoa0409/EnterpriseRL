# Policy-task audit — referral_and_authorization_management / charter-global

## charter_global_frozen

- Auditor: Claude (erl-task-policy-audit). Independent of the author; no answer was accepted from the coordinator.
- Freeze time: 2026-09-25 00:05 UTC. This section was written before any task's GT was revealed and contains nothing derived from a GT.
- Frozen inputs:
  - `tasks/referral_and_authorization_management/referral.extended.yaml`, sha256 `cecaa253ab7006bf490b3dd8e5c587beca3fcbb6dd4ac7eb441a62da27a2e675` (matches the brief)
  - `tasks/referral_and_authorization_management/task_tools.py`, sha256 `9c86ee358fe1bb3a3733805dc2006c63496bfd2db2f4c53fc8b28b7225607a1e` (matches the brief)
  - `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/referral.yaml`. Also read for cross-category parameters only: `blueprint/products/billing.yaml` and `blueprint/products/appointment.yaml`.
  - The expression semantics (`within_months`, `DAYS`, `XCOUNT`, `XLATEST`, `CFIELD`, `CPARAM`) come from `skills/erl-task-instantiate/scripts/check_compute.py::build_env`, which I read and did not modify.
- Fields I was allowed to read: the charter (base and extended), the tool contracts, and each masked view (`frozen_time`, `user_scenario`, `initial_state`).
- Fields masked until every task was frozen: all of `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`; `tasks/*/worklog.md`; the scenario-level `worklog.md`; every other `audits/` subdirectory.
- Base-copy check: the charter text from `category: referral` up to `extended_policies:` is byte-identical to `blueprint/products/referral.yaml` from `category: referral` to EOF (60594 characters each, compared programmatically). The base copy is verbatim.

### policy_conflict_scan

There are five extended policies over one base section:

| id | subject | target_tool (owner) | computes | tier scope stated in the rule |
|---|---|---|---|---|
| referral_ext_study_site_estimate | referral_provider_changed | confirm_imaging_site_change_a21d40f9 (user) | estimated_patient_share_usd | "an approved imaging or procedure prior authorization" |
| referral_ext_study_validity | referral_validity_extended | extend_study_authorization_f1ccb059 (agent) | added_validity_days | "whose tier adds no units on extension (the Advanced Imaging Prior Authorization and the Outpatient Procedure Prior Authorization)" |
| referral_ext_oon_visit_share | referral_validity_extended | sign_oon_cost_share_acknowledgement_95eb7797 (user) | acknowledged_cost_share_usd | "an Out-of-Network Referral" |
| referral_ext_visit_validity | referral_validity_extended | lengthen_referral_validity_fab859e3 (agent) | added_validity_days | "whose tier adds units on extension (In-Group, HMO, Out-of-Network, PT)" |
| referral_ext_extension_visits | referral_validity_extended | grant_extension_visits_d2c34b29 (agent) | extension_visits | "a visit referral whose tier adds units on extension" |

- **Overlapping subjects.** Four policies share `referral_validity_extended`.
  - The two `added_validity_days` policies are split by tier. `extension_units` is 0 for imaging and procedure, and above 0 for In-Group, HMO, OON and PT. Standing also has `extension_units` 0, but base says "The Standing Specialist Referral cannot be extended". The split is therefore disjoint.
  - `oon_visit_share` and `extension_visits` compute different quantities with different tools.
  - There is no overlap on any `(tool, quantity)` pair.
- **Eligibility and time anchors.** Every extended policy inherits base `referral_validity_extension` (status approved or exhausted; `extension_count` < `max_extensions`) and `referral_provider_change` (status submitted or approved; `provider_change_allowed`). No extended policy weakens them.
- **Terminal states.**
  - `grant_extension_visits` returns an exhausted referral to approved and counts the extension.
  - `lengthen_referral_validity` moves only `valid_through`, which is the declared overwrite "this lengthening is not counted as an extension decision of its own".
  - When both run, the combined state is one extension decision with added validity and added visits. They do not conflict.
- **Cross-category read boundaries.**
  - `site_estimate` and `oon_visit_share` read billing's `copay_collect_at_checkin`, `deductible_estimate_collect_pct`, `pos_estimate_cap_usd` and `coverage_reverification_days`, plus account fields.
  - `site_estimate`, `study_validity` and `extension_visits` read the appointment ledger and visit-type parameters.
  - Billing's own `billing_time_of_service_collection` and `billing_hardship_adjustment` govern neighbouring real quantities (see O-7). Neither gives a definite competing figure in either task world, so both are observations.
- **Claimed scopes.** Without reading `charter_scope`, the structure divides the five policies into two trees:
  - imaging: `study_validity` blocked by `site_estimate`;
  - OON visits: `extension_visits` blocked by `oon_visit_share` and `visit_validity`.
  - The graph has no edge between the trees. With M = 2, one tree per task covers all five policies with no overlap. The actual claims are checked in each task's `source_gt_comparison`.

### rule_compute_equivalence

Check 2, every policy, binding by binding. Each binding's `compute_basis` quotation is verbatim in its rule unless noted.

- **referral_ext_study_site_estimate**
  - `site_copay`, `site_rate`, `site_deductible`, `site_relieved`, `site_deposit`, `site_credit` and `result`: each branch has a rule sentence and each sentence has a branch.
  - Rounding points: `RND(deductible_left*site_rate/100,2)` matches "rounded half up to the cent". The relief tier-2 expression `RND(site_copay + site_deductible*(1-pct/100),2)` rounds the sum rather than only the reduced figure. That is equivalent because the copay has two decimals.
  - Final `RND(MX(0, …))` matches "never below zero, rounded half up".
  - `RND` is Python `round` (banker's rounding on exact ties), not half-up. No tie occurs in either world, so this is an observation.
  - `booked_date`'s basis quotes the site-given sentence rather than a date sentence. The rule's "on the study date" covers the date, so there is no empty promise.
  - No compute invention found.
- **referral_ext_study_validity**
  - The `study_span` branches match the three rule clauses.
  - The margin and allowance ladders match.
  - `roll_weekday` anchors on 2026-01-05 (a Monday), so 5 = Saturday and 6 = Sunday. This matches "the day on which valid_through moved forward by that sum would fall".
  - The rule names the tier values only by name ("the repeat no-show margin", "the payer re-check allowance"). The numbers 14/7/6/3/5/3/7/5 live only in `params`, and the key `repeat_miss_margin_days` differs in wording from "repeat no-show margin". Observation O-2.
- **referral_ext_oon_visit_share**
  - `share_copay`, `share_basis`, `share_rate`, `share_deductible_part` (the MN with the cap equals "never more than the … cap"), `share_relieved` and `result` all match.
  - `latest_deductible_charge` = `XLATEST(... event_type='billing_charge_posted', line_category='deductible')`, which matches "most recent deductible charge". `or 0` implements "no deductible charge is on the ledger".
- **referral_ext_visit_validity**
  - `course_span` tier 2 adds `F('status') == 'approved'` where the rule says only "where the referral still has units remaining". Within the extendable domain (approved or exhausted, and exhausted means 0 units) the two are equal, so this is observation O-3.
  - `anchored_span`, `course_recheck`, `course_roll` and `result` match.
  - Tier values are again named, not stated (O-2).
- **referral_ext_extension_visits**
  - `visit_net_uses` (uses minus restorations over 3 months) and `carry_forward` (`(n+1)//2` = "half … rounded up") match.
  - `window_adjustment` thresholds 84/42, `pace_adjustment` thresholds 60/90 and both trims match. The floor `MX(1, …)` matches "never fewer than one".
  - The ack gate `COUNT('referral_requests', within_months=1, …)` matches "within the past month".
  - Numbers are stated in the rule.
- **Factor tiers against compute.** Every tier each `factors[].ladder` names is a rule sentence and a branch of its `decides` binding, and the reverse holds too. No tier exists in only one face.

**Result: no SOURCE-POLICY red under check 2.**

### action_binding_and_uuids

- **(target_tool, computes) pairs.** There are five distinct pairs and each is claimed once.
- **UUID tails.** The uuid8 tails are `a21d40f9`, `f1ccb059`, `95eb7797`, `fab859e3` and `d2c34b29`. They share no prefix, no suffix and no sequence, and none is reused. They show no sign of batch derivation.
- **Docstrings.**
  - No docstring names another tool.
  - "Afterwards …" (confirm, sign) and "The patient can then see …" (extend, grant) describe the post-state of the same call, not a position among tools.
  - `lengthen_referral_validity_fab859e3`'s docstring says "as part of a visit extension, without recording a separate extension decision" and returns `previous_valid_through` "as it stood when the call was made". This alludes to a companion write without naming it or ordering it. Observation O-4.
- **Tool bodies.** No function body checks status, timing, eligibility or any other tool's effect. Each writes unconditionally, so the tool layer judges no prerequisite.
- **Ownership.** `blueprint.yaml`'s difficulty summary lists "changing the provider on … a referral" among agent actions, but `confirm_imaging_site_change_a21d40f9` is `owner="user"`. The extended rule makes the site change the patient's signed act, and the summary is not the policy surface. Observation O-5.

### prerequisite_graph

Check 7.

- **Filled everywhere.** `site_estimate: []`, `oon_visit_share: []` and `visit_validity: []`. `study_validity` has 1 edge and `extension_visits` has 2.
- **Edges:**
  1. `referral_ext_study_validity → referral_ext_study_site_estimate`: `value_input`, gate `named_site_match` (a binding of study_validity), form `state`, `resolved_by` `confirm_imaging_site_change_a21d40f9`, which is the target tool of `site_estimate`.
  2. `referral_ext_extension_visits → referral_ext_oon_visit_share`: `value_input`, gate `recent_signed_ack` (a binding), form `state`, `resolved_by` `sign_oon_cost_share_acknowledgement_95eb7797`, the target tool.
  3. `referral_ext_extension_visits → referral_ext_visit_validity`: `value_input`, gate `visit_days_left` (a binding), form `state`, `resolved_by` `lengthen_referral_validity_fab859e3`, the target tool.
- **Structure.** Every `problem` is an extended id, none is self or base, and the graph is acyclic (two disjoint stars). No action-form edge exists, so no `fallback_reason` is required and none is present.
- **`policy_source`** is verbatim in the blocked rule for all three edges (string-matched).
- **`condition`** agrees in strength with the sentence on all three edges.
- **`effect`** of edge 3 reads "visit_days_left grows past the window thresholds and the window adjustment moves from taking one visit away to adding one". That describes one particular world's movement as though it were general. It holds only when the pre-lengthening days left are under 42 and the post-lengthening days left are 84 or more. Observation O-6. The skill's banned phrases ("in this task / at the opening") are absent.

### prerequisite_sentences

Check 6, the four-point test, per edge.

**Edge 1.** "The added validity is fixed only after the site named on the authorization is the site where the booked study will be performed."

- Connective: "only after".
- State form: `referrals.rendering_provider` equals `appointments.clinic_location` of the booked study, in table and finder words.
- No tool, id or snake_case.
- Strength equals `condition`.
- **Which write brings it about.** The only writes in this difficulty that change `rendering_provider` are `confirm_imaging_site_change_a21d40f9`, whose rule reads "the site change is recorded together with that estimate; the site given is the clinic location of the study booked against the authorization, copied exactly". The share tools have no referral write.
- **Derivation.** Sentence plus records (rendering_provider ≠ clinic_location) plus site_estimate's rule gives the site change with estimate as the only reading.

**Edge 2.** "Extension visits on an out-of-network referral are not posted until a cost-share acknowledgement signed by the patient within the past month stands on the referral."

- Connective: "not … until".
- State form: a `referral_requests` row of `oon_acknowledgement`, `patient_signed`, whose `created_at` falls within the month.
- No tool or id.
- Strength equals `condition`.
- **Which write brings it about.** Only `sign_oon_cost_share_acknowledgement_95eb7797` creates `oon_acknowledgement` rows. One reading.
- **Second wording (finding F-2).** The depended-on rule `referral_ext_oon_visit_share` itself says "Before an Out-of-Network Referral is extended, the patient signs a fresh cost-share acknowledgement …". The dependency is therefore restated in the depended-on policy's rule, in a different wording and with a broader scope.

**Edge 3.** "The extension visits are fixed only after the referral's valid-through date lies at least the tier's extension validity days beyond the handling date."

- Connective: "only after".
- State form: `valid_through` − handling date ≥ `extension_validity_days`.
- No tool or id.
- Strength equals `condition`.
- **Which write brings it about.**
  - Two writes move `valid_through`: `lengthen_referral_validity_fab859e3` and `extend_study_authorization_f1ccb059`.
  - The latter's rule is confined to "an approved or exhausted prior authorization whose tier adds no units on extension". For a visit referral whose tier adds units only visit_validity's rule applies, so the reading is single.
- **Charter-global reachability defect (observation O-1).** For the In-Group and HMO tiers (`extension_validity_days` = 90), the active-course span is 84. For an exhausted referral the lengthened date is handling date + 84 + allowance (≤3) + roll (≤2) ≤ handling date + 89 < handling date + 90. For those tiers the only resolving write can never make the waited-on state hold, so the extension visits can never be "fixed". Neither task in this difficulty is on those tiers, so no consequence is demonstrable here.

**Other checks.**

- **Undeclared orders in rules.** I swept every extended rule for cross-problem ordering words. Only F-2 (oon_visit_share's "Before … is extended") states an order that grounds no declared edge.
- **Base orders.** The base "Before submission the patient must sign the cost-share acknowledgement" governs submission, not extension, and grounds no edge. The base "a completed re-evaluation visit must precede the request" applies only where `reevaluation_before_extension` is true (PT only), and grounds no edge.

### override_declarations

Check 1, finding half, sentence by sentence against each `base_policy_refs` entry.

- **referral_ext_study_site_estimate** (refs: `referral_provider_change`, `referral_submission_and_decision`; `overwrite: []`)
  - provider_change: "may move an open referral to another rendering provider … (for imaging and procedures, another site) without a new request; the units and validity carry over" is followed, and the tool leaves units and dates alone. "status is submitted or approved" is inherited. "rendering_in_group_required" is false for imaging and procedure. "site_of_service_restricted … not covered" is consistent.
  - submission_and_decision: "a cost estimate given to the patient where pre_service_estimate_required is true" names no amount, and the extended rule supplies one. No conflict.
  - **No undeclared override.**
- **referral_ext_study_validity** (ref: `referral_validity_extension`; overwrite names "Each extension adds extension_validity_days … (an exhausted referral returns to approved on that grant)")
  - The replacement is declared.
  - Every other base sentence (status approved or exhausted; `extension_count` below `max_extensions`; notices; lead days; Standing not extendable) is inherited.
  - The units side is moot because `extension_units` = 0 for both scoped tiers, and base `referral_unit_accounting` ("an extension grants extension_units (none where that is 0)") agrees.
  - **No undeclared override.**
- **referral_ext_oon_visit_share** (refs: `referral_validity_extension`, `referral_out_of_network`, `referral_submission_and_decision`; `overwrite: []`)
  - The base OON "billed … under the payer's in-network cost share" is followed.
  - The base "Before submission the patient must sign the cost-share acknowledgement" concerns submission, and the extended rule adds a fresh one before extension. That is an addition, not a conflict.
  - **No undeclared override.**
- **referral_ext_visit_validity** (ref: `referral_validity_extension`; overwrite names the same clause)
  - Declared. The remaining base sentences are inherited.
- **referral_ext_extension_visits** (refs: `referral_validity_extension`, `referral_unit_accounting`, `referral_out_of_network`; overwrite names only `referral_validity_extension`'s clause)
  - **Undeclared override, finding F-1.** Base `referral_unit_accounting` states: "An initial or appeal approval grants the tier's units_per_approval, an extension grants extension_units (none where that is 0), and a retroactive authorization grants exactly the units of the services it covers."
    - That sentence governs the scored quantity (the units an extension grants). The extended rule replaces it with the carry-forward/adjustment/trim computation ("The extension visits are the carry-forward plus the window and exhaustion-pace adjustments less the two trims, never fewer than one").
    - `referral_unit_accounting` is in this policy's own `base_policy_refs`, yet the `overwrite` list does not name it.
    - The base clause of `referral_validity_extension` that *is* named ("grants those units") is a different sentence in a different policy. Declaring that one does not declare this one.

### factor_ladders

Structure only. Whether each factor bears weight lives in each task's `factor_weight`.

**referral_ext_study_site_estimate**: 6 factors (5 `parameter`, 1 `method`).

- **`site_copay_class`** (parameter; `decides` = `site_copay`; 3 tiers: specialist / none / office): **failed, finding F-4.**
  - The policy's object is "the study booked against" an approved imaging or procedure prior authorization.
  - In `appointment.yaml`, the only visit types with `prior_auth_required: true` are `In-Office Procedure Visit` and `Advanced Imaging Appointment`, and both have `copay_class: specialist`.
  - So tier 1's condition ("the booked study's visit type draws the specialist copay") holds of every customer who reaches this write. It restates the policy's scope instead of dividing its customers.
  - Tiers 2 and 3 describe an Annual Preventive Exam or a primary-care visit booked as the "study" against an imaging or procedure authorization, which no imaging or procedure business does.
  - The fall-through value, the office-visit (primary) copay, is not a treatment any imaging center publishes as its estimate for an MRI or procedure. That fall-through is also the policy's whole baseline ("The estimate is the office-visit copay …").
- **`site_deductible_rate`** (parameter; 100 / class pct / 0; tiers 1 and 2 are multi-source: class parameter plus account verification date plus appointment study date).
  - Distinct values.
  - Business-real: stale eligibility means collecting as unverified; otherwise the class share.
  - `cross_difficulty` billing.
- **`site_deductible_part`** (parameter; cap / figure / 0). Distinct outcomes; cap-and-floor structure.
- **`site_hardship_relief`** (method; reduce the sum / reduce only the deductible / none). Honest method; multi-source (account approval plus appointment study date).
- **`site_missed_visit_deposit`** (parameter; no-show fee / late-cancel fee / 0). Distinct. The gradation (a late-cancel-sized deposit after one no-show) is unusual but not demonstrably unreal. Observation O-8.
- **`site_credit_offset`** (parameter; the whole amount due / the credit / 0). Distinct, business-real.
- **Counts.** Multi-source ≥ 1; `cross_difficulty` covers appointment and billing. If F-4 strikes `site_copay_class`, 5 factors remain (4 parameter, 1 method), still within bounds.
- **Baseline.** `baseline.rule` = "The estimate is the office-visit copay recorded on the patient's financial account." It is self-sufficient and is a rule sentence. `params: []`.

**referral_ext_study_validity**: 6 factors (4 `parameter`, 2 `method`).

- **`study_span`** (method; days from `valid_through` to the study / 0 / `extension_validity_days`). Honest method (date arithmetic, constant, parameter); multi-source (booked site plus authorization site plus dates); cross appointment.
- **`no_show_margin`, `late_cancel_margin`** (parameter; 14/7/0 and 6/3/0). Distinct values; cross appointment. Business realism: extending an authorization's validity because the patient has missed visits is not a documented payer practice, but I cannot show it is unreal. Observation O-8.
- **`recheck_allowance`** (parameter; 5/3/0). Multi-source (tier parameter, class parameter, verification date, study date); cross billing.
- **`reschedule_allowance`** (parameter; 7/5/0). Cross appointment; reads `appointments.reschedule_count`, the schema's "number of patient-requested reschedules". Not an outcome stamp.
- **`weekend_roll`** (labelled method): **failed, finding F-3.**
  - Tier 1's method is "two more days are added so the authorization runs through the following Monday".
  - Tier 2's method is "one more day is added so the authorization runs through the following Monday".
  - Read as methods, tiers 1 and 2 select the same method (roll to the following Monday), so the ladder has two methods over three tiers.
  - Read as what the compute does (`weekend_roll` = 2 | 1 | 0 added into `result = days_before_roll + weekend_roll`), each tier substitutes a number into one formula. That makes it a `parameter` mislabelled as `method`.
  - Either reading fails a factor test.
- **Counts if F-3 strikes it.** 5 remain (4 parameter, 1 method via `study_span`), within bounds.
- **Baseline.** `baseline.rule` = "An extension adds the tier's extension_validity_days to valid_through."; `params` = [`extension_validity_days`]. Self-sufficient; a rule sentence.

**referral_ext_oon_visit_share**: 4 factors (3 `parameter`, 1 `method`).

- **`share_copay`** (specialist / nothing / office). Tier 1 is multi-source (class parameter plus account copay field). All three tiers are reachable for insured tiers:
  - HDHP and Medicaid do not collect → nothing;
  - a class that collects with no specialist copay recorded → office.
- **`share_deductible_basis`** (latest deductible charge / remaining deductible / 0). Multi-source (ledger plus account).
- **`share_collection_rate`** (100 / pct / 0).
- **`share_hardship_relief`** (method). All billing `cross_difficulty`; within bounds.
- **Baseline.** "The out-of-network visit share is the office-visit copay …". Self-sufficient; a rule sentence.

**referral_ext_visit_validity**: 4 factors (2 `parameter`, 2 `method`).

- **`course_span`** (parameter; 84 / 56 / `extension_validity_days`). Tier 1 is a conjunction of status and use history.
- **`course_anchor`** (method; span − days left / span + lead − days left / span). Honest method.
- **`course_recheck`** (parameter; 3/2/0; cross billing).
- **`course_roll`** (labelled method): **failed, finding F-3.** Tiers 1 and 2 both read "… so the referral runs through the following Monday"; the compute is `course_roll` = 2 | 1 | 0 added into `course_sum`. The same defect as `weekend_roll`.
- **Counts if F-3 strikes it.** Only 3 factors remain (`course_span`, `course_anchor`, `course_recheck`), **below the floor of 4**.
- **Baseline.** "A lengthening adds the tier's extension_validity_days to valid_through."; `params` = [`extension_validity_days`]. Self-sufficient; a rule sentence.

**referral_ext_extension_visits**: 5 factors (4 `parameter`, 1 `method`).

- **`carry_forward`** (method; net uses / half rounded up / `extension_units`). Honest method; tier 1 is a conjunction of net count and recency.
- **`window_adjustment`** (+1/−1/0).
- **`exhaustion_pace`** (+2/+1/0). Multi-source: referral status and decision date plus event dates.
- **`no_show_trim`, `late_cancel_trim`** (−2/−1/0; cross appointment). Business realism of trimming authorized visits for missed appointments is questionable but not demonstrably unreal. Observation O-8.
- **Baseline.** "An extension adds the tier's extension_units."; `params` = [`extension_units`].

**Per-task structural counts, by tree:**

- **Imaging tree** (site_estimate + study_validity): at least 1 multi-source factor (`site_deductible_rate`) and at least 1 `cross_difficulty` factor (appointment, billing).
- **OON tree** (oon_visit_share + visit_validity + extension_visits): at least 1 multi-source factor (`share_deductible_basis`, `exhaustion_pace`) and at least 1 `cross_difficulty` factor (billing, appointment).

### findings

**F-1 — SOURCE-POLICY RED (undeclared override).**

- Symptom: `referral_ext_extension_visits` grants a computed visit count on extension, while base `referral_unit_accounting` states "an extension grants extension_units (none where that is 0)". Its `overwrite` names only `referral_validity_extension`.
- Root cause: `referral_unit_accounting` is listed in `base_policy_refs` but its sentence is not declared as superseded.
- Evidence:
  - referral.extended.yaml, `policies[referral_unit_accounting].rule`, first sentence;
  - `extended_policies[referral_ext_extension_visits].overwrite` (one entry, `base_policy: referral_validity_extension`);
  - `.base_policy_refs` = [`referral_validity_extension`, `referral_unit_accounting`, `referral_out_of_network`].
- Bears on: every task whose tree contains `referral_ext_extension_visits`. The OON tree; the demonstration is in task 1.

**F-2 — SOURCE-POLICY (second wording and undeclared order).**

- Symptom: the depended-on rule `referral_ext_oon_visit_share` states "Before an Out-of-Network Referral is extended, the patient signs a fresh cost-share acknowledgement …". This restates edge 2 in the depended-on policy. Its scope ("is extended") also reaches the lengthening, because `referral_ext_visit_validity`'s rule reads "When a visit referral … is extended, its validity is lengthened …".
- There is no declared edge `visit_validity → oon_visit_share` (`visit_validity.prerequisite: []`).
- Evidence: the two rule sentences quoted, and `referral_ext_visit_validity.prerequisite: []`.
- Consequence: an order (ack before lengthen) that the graph leaves free. Whether this costs a task anything depends on that task's terminal state and scored order, so it is demonstrated or dismissed in task 1's file.
- Bears on: the OON tree (task 1).

**F-3 — SOURCE-FACTOR RED (unreal or mislabelled ladder).**

- Symptom: `weekend_roll` (study_validity) and `course_roll` (visit_validity) are labelled `method`. Their tiers 1 and 2 select the same stated method (run through the following Monday), and their compute adds a number (2/1/0) into one sum.
- Evidence:
  - `factors[weekend_roll].ladder[0..1].method`; `factors[course_roll].ladder[0..1].method`;
  - compute `weekend_roll: "2 if roll_weekday == 5 else (1 if roll_weekday == 6 else 0)"` and `result: "days_before_roll + weekend_roll"`;
  - likewise `course_roll` and `course_sum + course_roll`.
- Consequence:
  - For study_validity the factor is struck and 5 honest factors remain.
  - For visit_validity it is struck and **3 remain, below the floor of 4**.
- Bears on: both trees (tasks 0 and 1).

**F-4 — SOURCE-FACTOR RED (ladder condition restates scope; fall-through not a real treatment).**

- Symptom: `site_copay_class` in `referral_ext_study_site_estimate`, as shown above.
- Evidence: `appointment.yaml` variants, where `prior_auth_required: true` holds only for In-Office Procedure Visit and Advanced Imaging Appointment, both `copay_class: specialist`; the extended rule's object ("the study booked against the authorization").
- Consequence: the tier-1 condition holds of every customer reaching this write, and tiers 2 and 3 divide no real customer. The factor is struck; 5 factors remain.
- Bears on: the imaging tree (task 0).

**Observations** (not grounds for rework):

- **O-1.** Edge 3's waited-on state cannot be reached by the resolving write for In-Group and HMO exhausted referrals (84 + ≤3 + ≤2 < 90). No task in this difficulty is on those tiers.
- **O-2.** `study_validity` and `visit_validity` rules name tier values ("the repeat no-show margin", "the active-course span") without stating the numbers, which live only in `params`. The key wording `repeat_miss_margin_days` differs from "repeat no-show margin".
- **O-3.** `visit_validity` `course_span` tier 2 compute adds `status == 'approved'`, which the rule does not state. It is equivalent on the extendable domain.
- **O-4.** The lengthen docstring alludes to a companion extension write ("as part of a visit extension, without recording a separate extension decision").
- **O-5.** The blueprint difficulty summary lists provider change as an agent action; the tool is `owner=user`.
- **O-6.** Edge 3's `effect` generalises one world's movement ("moves from taking one visit away to adding one").
- **O-7.** Cross-category neighbours: `billing_time_of_service_collection` (percentage of the encounter `estimate_amount`, which is absent for an unbilled future study) and `billing_hardship_adjustment` (capped at `hardship_adjustment_max_pct`, 75 for PPO/POS). Neither yields a definite competing figure in either task world.
- **O-8.** The no-show and late-cancel margins, trims and deposit gradation are business-questionable but not demonstrably unreal.
- **O-9.** `RND` is Python `round` rather than half-up. No tie occurs in either world.
- **O-10.** Each extended validity rule opens with its baseline sentence stated unconditionally ("An extension adds the tier's extension_validity_days to valid_through.") and later supersedes it within the same rule. This is the skill's baseline-in-rule contract, recorded only because a hasty reader could stop at the first sentence.
- **O-11.** "No-show fees assessed" does not say whether a later-waived fee counts. In both worlds the waived fees fall outside the 12-month window, so there is no consequence.
- **O-12.** Base lifecycle marks `exhausted → approved` as `by: system` ("The payer approves an extension …"). The extended tools record the extension decision on the spot. The difficulty claim designates extending as an agent action, so this is recorded as an observation, not as a real-world wait.
- **O-13.** Base `referral_unit_accounting` eligibility `grant_only_when_approved` ("Units are granted only when the referral status is approved.", `state_contract.allowed: [approved]`, `applies_to: [referral_units_granted]`) is not named in `referral_ext_extension_visits.overwrite`. That policy grants units on an exhausted referral in the same call that returns it to approved. Base `referral_validity_extension` itself says "(an exhausted referral returns to approved on that grant)", and base `referral_unit_accounting` says "Restoring a unit on an exhausted referral returns it to approved only through an extension decision", so base already anticipates an extension grant on an exhausted referral. I cannot demonstrate a definite second answer (a refusal reading is weaker than the base's own extension clause), so this is recorded as an observation next to F-1.

## closing_checklist

Written after both tasks were frozen and revealed (reveal at about 2026-09-25 00:05 UTC). Nothing above this heading was changed after the reveal.

**Per-task verdicts:**

| task | policy self-consistency | problem tree | factors | unique solution |
|---|---|---|---|---|
| 0 (`0.md`) | PASS | PASS | **SOURCE-FACTOR RED** (F-3 `weekend_roll`; F-4 `site_copay_class`) | PASS |
| 1 (`1.md`) | **SOURCE-POLICY RED** (F-1) | **SOURCE-CHAIN RED** (proof field `prerequisite_closure.edges[0].condition`) | **SOURCE-FACTOR RED** (F-3 `course_roll` puts `visit_validity` below 4 factors; no near-miss in `visit_validity`) | **SOURCE-TASK RED** (F-1: `extension_visits` 2 vs 4) |

**Step 4 checklist:**

- **Files.** The per-task files correspond one-to-one with tasks 0 and 1, and `_difficulty.md` sits alongside them. This is revision 1; there are no older revisions. Not every comparison section carries a PASS.
- **Coverage and scopes.** `charter_scope`: task 0 = {site_estimate, study_validity}; task 1 = {oon_visit_share, visit_validity, extension_visits}. Coverage is complete (5/5) and the scopes are pairwise disjoint across whole trees. Task tools and GT are closed; the uuid8 tails are independent (§ action_binding_and_uuids).
- **Trees.**
  - Task 0: 1 prerequisite, 1 `value_input`, 1 `owner=user`.
  - Task 1: 2 prerequisites, 2 `value_input`, 1 `owner=user`.
  - No cycles. The difficulty-wide graph is two disjoint stars, which is a DAG.
- **Factors.**
  - Every declared factor bears weight on its task's world against an honest baseline.
  - Every baseline-alone figure differs from gold: 25.00 vs 285.00; 30 vs 33; 30.00 vs 198.75; 60 vs 65; 2 vs 4.
  - Every task has multi-source and cross-difficulty factors.
  - **Not met:** F-3 (both weekend-roll ladders), F-4 (`site_copay_class`), the `visit_validity` factor floor, and the `visit_validity` near-miss.
- **Post-reveal status of F-2.** GT follows the order the second wording dictates, and the other order replays to the same terminal hash. F-2 therefore stands as a structural check-6 defect with no demonstrated consequence on either task, so it is an observation.
- **Instantiation-stage gates.** Not re-run: this is not the final form. The coordinator's gate snapshot in the brief (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK; traceability deferred) was cited, not re-run, per Step 0.

**Conclusion.** The difficulty **does not pass** the source-layer audit. Tasks 0 and 1 both carry red verdicts. The fixes are the author's to arrange; this audit edits no artifact.

---

## revision_2

### charter_global_frozen (r2)

- Auditor: Claude (erl-task-policy-audit), the same auditor as revision 1.
- Written at about 2026-09-25 00:19 UTC, from the system clock. It was written before any revised task JSON was read, and contains nothing derived from a revised GT.
- Frozen inputs:
  - `referral.extended.yaml` sha256 `878f6728ba0c8cb122a687a52052c6b3a16d26791bff1d1067900af7404f955d`
  - `task_tools.py` sha256 `48fef27f06927dfb6d6f988e5b2f5e30ecb85e882ed2def84232eb55078b8099`
  - Both match the coordinator's message.
- **Re-audit rule.** Both hashes differ from revision 1 (`cecaa253…`, `9c86ee35…`), so every charter-global section below is re-derived in full, not carried forward. Revision 1 above is left untouched.
- The base section is still byte-identical to `blueprint/products/referral.yaml` (compared programmatically).
- Masked until both r2 task derivations were frozen: every GT field of the revised `tasks/*.json`; the worklogs; other `audits/` subdirectories.
- **Contamination disclosure (r2).** In revision 1 I read the round-1 GT of both tasks (task 0: 285.00 / 33; task 1: 198.75 / 65 / 4) and the round-1 `design_rationale`. That knowledge predates this revision and cannot be unlearned. The r2 derivations were nevertheless recomputed from the charter's own compute on the r2 views. The changed figures (340.00; 129.00) could not have come from the round-1 GT.

### policy_conflict_scan (r2)

- The five policies, their target tools, owners, computed quantities and tier scopes are unchanged from revision 1.
- The subject overlap on `referral_validity_extended` is still split by tier and by quantity, with no `(tool, quantity)` overlap.
- Terminal states are compatible, as in revision 1.
- **Cross-category** (see N-2 below):
  - `site_estimate` now reads the billing class's `copay_collect_at_checkin` instead of the booked visit type's `copay_class`.
  - Its tier "collects copays but no specialist copay above zero is recorded → office-visit copay" diverges from `billing_time_of_service_collection`, which for a specialist-class visit collects `copay_specialist_usd`.
  - Neither task sits on that tier, so this is an observation.
- **Scopes by structure:** two disjoint trees (imaging: `site_estimate` ← `study_validity`; OON: `oon_visit_share`, `visit_validity` ← `extension_visits`), covering 5/5.

### rule_compute_equivalence (r2)

- **`referral_ext_study_site_estimate`**
  - `site_copay` = `0 if not site_class_collects_copay else (copay_office if copay_specialist <= 0 else copay_specialist)`. This matches the three rule clauses ("does not collect … nothing; collects … but no specialist copay above zero … office-visit copay; otherwise … specialist copay").
  - The other bindings are unchanged from revision 1 and still match.
  - The waived-fee clause "(a fee later waived still counts as assessed)" matches `XCOUNT` over `appointment_fee_assessed` rows, which does not look at waivers.
  - The new `compute_basis` for `site_class_collects_copay` is a verbatim rule fragment.
- **`referral_ext_study_validity`**
  - Every tier value is now stated in the rule (14/7, 6/3, 5/3, 7/5, 2/1 days) and equals `params`. The keys are renamed `repeat_no_show_margin_days` etc., and the weekend roll reads `K('saturday_roll_days')` / `K('sunday_roll_days')`.
- **`referral_ext_oon_visit_share`**
  - The rule's opening sentence changed from "Before an Out-of-Network Referral is extended, the patient signs a fresh cost-share acknowledgement …" to "The cost-share acknowledgement a patient signs on an Out-of-Network Referral states the out-of-network visit share …".
  - Compute is unchanged and matches.
- **`referral_ext_visit_validity`**
  - `course_span` = `P('extension_validity_days') + K('active_course_extra_days')` (24) matches "the tier's extension_validity_days plus 24 days".
  - Tier 2 compute (`status == 'approved' and units_remaining > 0`) now matches the rule's "where the referral is approved and still has units remaining".
  - Allowances 5/2 and rolls 2/1 are stated in the rule and equal `params`.
- **`referral_ext_extension_visits`**
  - Compute is unchanged.
  - The rule adds "An extension grant may be posted on an exhausted referral, which returns to approved with that grant." That is a behavioural statement mirrored by the tool and by the third `overwrite` entry, with no compute binding needed.
  - The waived-fee clause is added to both trims and matches `XCOUNT`.
- Every factor tier is a rule sentence and a branch of its binding, in both directions.

**Result: no red under check 2.**

### action_binding_and_uuids (r2)

- The five `(target_tool, computes)` pairs are unique. The uuid8 tails are unchanged and independent (`a21d40f9`, `f1ccb059`, `95eb7797`, `fab859e3`, `d2c34b29`).
- `lengthen_referral_validity_fab859e3`'s docstring now reads "Move the last valid date of a visit referral … later by a given number of calendar days. One call changes only the referral's last valid date …", and `previous_valid_through` is "the last valid date the referral carried until this call". The allusion to a companion extension write is gone.
- No docstring names another tool or places an action in a sequence.
- No function body judges a prerequisite; the bodies of all five tools are unchanged in logic from revision 1.
- O-5 (the blueprint summary lists provider change as an agent action; the tool is `owner=user`) still holds as an observation.

### prerequisite_graph (r2)

- The same three edges, all `value_input`, form `state`.
- Gates `named_site_match`, `recent_signed_ack` and `visit_days_left` are bindings.
- `resolved_by` values are the depended-on target tools. The graph is acyclic.
- Every `policy_source` is verbatim in its blocked rule (string-matched).
- Edge 2's `condition` still reads "created_at within the month before the handling date".
- Edge 3's `effect` now reads "visit_days_left grows by the added days and the window adjustment is read on the lengthened date, so its tier can change". That is a general statement.

### prerequisite_sentences (r2)

- The four-point test passes for all three edges, as in revision 1.
- **Single resolving write per state-form edge** (unchanged reasoning):
  - edge 1: the site change;
  - edge 2: the acknowledgement tool;
  - edge 3: the lengthening; the study extension is excluded by its tier scope.
- **Ordering sweep over all five rules** (before / after / until / first / once / then / prior to). The only cross-problem orders are the three declared prerequisite sentences. The acknowledgement rule no longer restates edge 2 and no longer orders the acknowledgement relative to "is extended".
- **Reachability of edge 3.**
  - Exhausted referrals: the new active-course span of `extension_validity_days` + 24 gives a lengthened date of handling date + ext + 24 + allowance, which is at least ext. The exhausted case is now reachable for every visit tier.
  - Approved referrals with units remaining still use the flat open-course span of 56:
    - with fewer days left than `extension_request_lead_days`, the lengthened date is at most handling date + 56 + lead + 5 + 2;
    - otherwise it is at most days_left + 63.
  - For the In-Group tier (ext 90, lead 14) and the HMO tier (ext 90, lead 10), an approved referral with fewer than about 27 days left can never reach "at least the tier's extension validity days beyond the handling date". Observation N-1: a narrowed residue of O-1, with no task on those tiers.

### override_declarations (r2)

- **`referral_ext_extension_visits`** now declares three overwrites:
  1. `referral_validity_extension` "Each extension adds … grants those units …";
  2. `referral_unit_accounting` "An initial or appeal approval grants the tier's units_per_approval, an extension grants extension_units (none where that is 0), and a retroactive authorization grants exactly the units of the services it covers.";
  3. `referral_unit_accounting` "Units are granted only when the referral status is approved."
  - Each quoted clause is verbatim in base (checked).
  - The merged semantics are unique: for an extension grant on a visit tier, the units are the computed extension visits, and an exhausted referral may receive the grant and return to approved.
  - The superseded clause in (2) also covers initial, appeal and retroactive grants, which this policy never performs, so replacing it within this policy's subject leaves those untouched. No second answer.
  - **Sentence sweep of the three `base_policy_refs`.**
    - Nothing else conflicts; the other `referral_unit_accounting` sentences (unit use, weekly cap, restore window) govern other events.
    - `referral_out_of_network`'s "telehealth visits … do not use its units" is unaffected.
- `referral_ext_study_site_estimate`, `referral_ext_study_validity`, `referral_ext_oon_visit_share` and `referral_ext_visit_validity`: same conclusions as revision 1.
  - `site_estimate`'s base `referral_submission_and_decision` names no estimate amount, so the new specialist-copay baseline conflicts with nothing.

**No undeclared override.**

### factor_ladders (r2)

- **`referral_ext_study_site_estimate`**: 6 factors, 5 `parameter` and 1 `method`.
  - `site_copay_by_class` (parameter; nothing / office / specialist; `cross_difficulty` billing):
    - All three tiers are reachable by customers at this write. The class may or may not collect copays (HDHP and Medicaid do not), and an account may carry a zero specialist copay.
    - The fall-through, the specialist copay, is what a copay-collecting class asks at check-in for a specialist-class study, and it equals the policy's baseline "The estimate is the specialist copay recorded on the patient's financial account."
    - Distinct outcomes; condition and outcome are business-real. Tier 2's office-copay substitution is the one departure from billing's own rule (N-2).
  - The other five factors are unchanged from revision 1 and pass.
- **`referral_ext_study_validity`**: 6 factors.
  - `weekend_roll` is now `parameter` with values 2 / 1 / 0 days: distinct values, honestly labelled.
  - Count: 5 parameter, 1 method (`study_span`).
- **`referral_ext_oon_visit_share`**: 4 factors (3 parameter, 1 method), unchanged and passing.
- **`referral_ext_visit_validity`**: 4 factors.
  - `course_span` (parameter): ext + 24 / 56 / ext. Distinct for every visit tier: OON 84/56/60, PT 54/56/30, In-Group and HMO 114/56/90.
  - `course_anchor` (method).
  - `course_recheck` (parameter, 5/2/0).
  - `course_roll` (parameter, 2/1/0).
  - Count: 3 parameter, 1 method. At the floor, and passing.
- **`referral_ext_extension_visits`**: 5 factors (4 parameter, 1 method), unchanged and passing.
- Per tree, at least 1 multi-source and at least 1 cross-difficulty factor, as in revision 1.

### findings (r2) — charter-global status of revision-1 items

**Closed:**

| item | status in r2 | evidence |
|---|---|---|
| F-1 undeclared override | **closed** | `extension_visits.overwrite[1]` names the `referral_unit_accounting` sentence verbatim |
| F-2 second wording / undeclared order | **closed** | the acknowledgement rule's "Before an Out-of-Network Referral is extended …" is removed; the ordering sweep finds only the three declared sentences |
| F-3 roll ladders | **closed** | `weekend_roll` and `course_roll` are `parameter` with distinct 2/1/0 values, stated in the rules; `visit_validity` keeps 4 factors |
| F-4 `site_copay_class` | **closed** | replaced by `site_copay_by_class` (tiers by the financial class's copay collection); all tiers reachable; the fall-through equals a real check-in treatment and the baseline |
| O-2 values named, not stated | closed | numbers in both rules |
| O-3 `course_span` status condition | closed | the rule now states "approved and still has units remaining" |
| O-4 lengthen docstring | closed | rewritten |
| O-6 edge-3 effect | closed | general wording |
| O-11 waived fees | closed | "(a fee later waived still counts as assessed)" in every fee ladder |
| O-13 `grant_only_when_approved` | closed | `overwrite[2]` |

**Partially closed or still open:**

| item | status in r2 | evidence |
|---|---|---|
| O-1 edge-3 reachability | **partially closed** | the exhausted case is fixed; the approved-with-units case remains unreachable for In-Group and HMO (N-1) |
| O-5, O-7, O-8, O-9, O-10, O-12 | unchanged, re-verified as still true and still observations | O-7 now also involves `billing_time_of_service_collection` against the HDHP world of task 0: 50% of an encounter `estimate_amount` that does not exist for the unbilled study, so there is still no definite competing figure |

**New charter-global observations** (not red; no demonstrated consequence on either task):

- **N-1.** O-1 residue: an approved In-Group or HMO referral with fewer than about 27 days left cannot be lengthened to 90 days beyond the handling date by the 56-day open-course span, so edge 3's state is unreachable for it.
- **N-2.** `site_copay_by_class` tier 2 ("collects copays at check-in but no specialist copay above zero is recorded → the office-visit copay") departs from `billing_time_of_service_collection`, which collects `copay_specialist_usd` for a specialist-class visit (so 0 in that case). This is a second defensible figure for any future world on that tier. Neither task is on it.

**No new charter-global red.**

## closing_checklist (r2)

Written after both r2 task derivations were frozen and the revised task JSONs revealed (about 00:21 UTC). Revision 1's `closing_checklist` above is left untouched.

**Per-task verdicts:**

| task | policy self-consistency | problem tree | factors | unique solution |
|---|---|---|---|---|
| 0 (`0.md` § revision_2) | PASS | PASS | PASS | PASS |
| 1 (`1.md` § revision_2) | PASS | PASS | PASS | PASS |

**Step 4 checklist:**

- **Files.** One file per task plus `_difficulty.md`. Revision 1 is preserved verbatim in all three files, and revision 2 is appended under `## revision_2` / `(r2)` headings. Every r2 comparison section carries PASS.
- **Coverage and scopes.** 5/5 extended policies are covered. Scopes are pairwise disjoint over whole trees: task 0 = {site_estimate, study_validity}; task 1 = {oon_visit_share, visit_validity, extension_visits}. Task tools and GT are closed. The uuid8 tails are independent and unchanged.
- **Trees.**
  - Task 0: 1 prerequisite, 1 `value_input`, 1 `owner=user`.
  - Task 1: 2 prerequisites, 2 `value_input`, 1 `owner=user`.
  - The difficulty graph is two disjoint stars and acyclic.
- **Factors.**
  - Each computation has 4–6 honestly labelled factors: 6/6 and 4/4/5, with at least 2 `parameter` and at least 1 `method` each.
  - Every task has multi-source and cross-difficulty factors, seeded.
  - Every factor bears weight against an honest baseline.
  - The baseline-alone figures differ from gold: 50.00 vs 340.00; 30 vs 33; 30.00 vs 129.00; 60 vs 65; 2 vs 4.
  - Every computation has a near-miss.
- **Gates on the final form.** I did not run them myself (Step 0). I cite the coordinator's post-rework snapshot on this exact charter (`878f6728…`) and tool module (`48fef27f…`): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. Traceability is deferred to KB publication.

**Reworker's item list, verified against the artifacts:**

- **Closed:** F-1, F-2, F-3, F-4, task-1 finding 2(a), finding 2(b), finding 3, O-2, O-3, O-4, O-6, O-11, O-13, O-T0-1, O-T1-1.
- **Partially closed:** O-1 (exhausted case fixed; approved-with-units residue N-1 for In-Group and HMO).
- **Unchanged, re-verified as still observations:** O-5, O-7, O-8, O-9, O-10, O-12.

**New observations r2 (none red):** N-1, N-2 (charter); N-T0-2, O-R2-T0-1 (task 0); N-T1-1, O-R2-T1-1 (task 1).

**Conclusion.** Policy self-consistency, problem tree, factors and unique solution all PASS for both tasks. **The difficulty passes the source-layer audit at revision 2.**

---

## revision_3

### charter_global_frozen (r3)

- Auditor: Claude (erl-task-policy-audit). Written at 2026-09-25 05:06 UTC, from the system clock.
- **Trigger.** The frozen runtime validator (`erlbench/validate.py` `_FORBIDDEN_TOKENS`, which lists "from datetime" as "real clock") rejected `task_tools.py`. The reworker replaced the `datetime` arithmetic in two tools with a static integer-calendar helper, `_Calendar.shift`.
- **Inputs.**
  - `referral.extended.yaml` sha256 `878f6728ba0c8cb122a687a52052c6b3a16d26791bff1d1067900af7404f955d`: **unchanged since r2**.
  - `task_tools.py` sha256 `853e1ebb04635682cad223e3d9903c4b19f080aa7a257024afeed127692838c5`: **changed** from r2's `48fef27f…`.
  - r3 views are byte-identical to r2 (`cmp`): `2684033b…`, `6ba0991f…`.
  - Task JSONs: `0.json` `d7f701cb…`, `1.json` `5090195b…`.
- **Re-audit rule.**
  - The charter hash is unchanged, so § policy_conflict_scan, § rule_compute_equivalence, § prerequisite_graph, § prerequisite_sentences, § override_declarations and § factor_ladders of revision 2 are **carried forward by reference**. The grounds are the charter hash `878f6728…`, identical to r2.
  - Those sections' tool-facing claims (the docstrings' silence about sequence; "the tool layer judges no prerequisite") are re-checked in § action_binding_and_uuids (r3) below, because the tool module moved.
  - § action_binding_and_uuids is **re-derived**.
- **Contamination.** I already knew the r2 GT (disclosed in revision 2). Nothing new was needed or read blind this round, because no world, charter or scored field moved (verified below).

### action_binding_and_uuids (r3)

**What changed in the tool module, proved by reconstruction.**

- Take the r3 file and reverse only the three described edits:
  1. restore `from datetime import date, timedelta` in place of the `_Calendar` class;
  2. restore `extend_study_authorization_f1ccb059`'s two-line `date.fromisoformat(…) + timedelta(…)` body in place of the `_Calendar.shift(…)` line;
  3. restore `lengthen_referral_validity_fab859e3`'s `(date.fromisoformat(str(before)[:10]) + timedelta(…)).isoformat()` line.
- The result hashes to `48fef27f06927dfb6d6f988e5b2f5e30ecb85e882ed2def84232eb55078b8099`, **exactly r2's hash**.
- Therefore every docstring, signature, parameter description, return receipt, owner, `rw` and every other body line is byte-identical to r2. The change is exactly the import removal, the helper class and two computation lines.

**Tool set.**

- `erlbench.tools.collect_specs` on the r3 module yields exactly five tools, with owners and parameters as in r2:
  - `confirm_imaging_site_change_a21d40f9` (user; referral_id, new_rendering_site, estimated_patient_share_usd)
  - `extend_study_authorization_f1ccb059` (agent; referral_id, added_validity_days)
  - `grant_extension_visits_d2c34b29` (agent; referral_id, extension_visits)
  - `lengthen_referral_validity_fab859e3` (agent; referral_id, added_validity_days)
  - `sign_oon_cost_share_acknowledgement_95eb7797` (user; referral_id, acknowledged_cost_share_usd)
- `_Calendar` is not collected. `collect_specs` takes only callables carrying `__toolmeta__` (`erlbench/tools.py` line 275ff), and the class is undecorated.

**Date semantics.**

- `_Calendar.shift(day, days)` was compared with proleptic-Gregorian reference arithmetic (`date + timedelta`, in a scratch script outside the artifacts, since removed).
- Coverage: every start date from 1900-01-01 to 2200-12-31 × shifts {0, 1, 2, 27, 28, 29, 30, 31, 59, 60, 65, 90, 365, 366, 400, 1000, −1, −60}. That is **1,978,884 checks, 0 mismatches**, including leap days and century years.
- Input handling is the same: `str(day)[:10]`, so a timestamp `valid_through` behaves as before. The `ctx.now()[:10]` fallback is unchanged.
- The only behavioural difference is on malformed input: `fromisoformat` raised, while `shift` either raises (on non-integer parts) or normalises an impossible date such as 02-30. The charter's domain (valid `YYYY-MM-DD` in `referrals.valid_through`; positive integer days per the docstrings) never reaches that case.
- On this difficulty's gold calls: `shift('2026-10-07', 33)` = 2026-11-09 and `shift('2026-10-17', 65)` = 2026-12-21, identical to r2.

**Prerequisites and the helper.**

- No body judges a prerequisite. The helper reads no status, date gate or other tool's effect.
- No docstring names another tool or orders an action.
- The five `(target_tool, computes)` pairs are unique. The uuid8 tails are unchanged and independent.
- `_Calendar` computes no policy figure: it only applies the day count the agent supplies. The module docstring's "no tool computes a policy figure" still holds.

**Gate evidence.**

- I re-ran `replay_tasks.py … --check` myself: **REPLAY OK** (0.json: 12 acts, deterministic, closure matches; 1.json: 15 acts, same).
- The task and tool hashes are identical before and after (`--check` wrote nothing).
- The coordinator's other gates (EXTENDED, TASK TOOL CONTRACT, SOLVABILITY, COMPUTE, GROUNDING, SCOPE, LINT) are cited, not re-run.

### findings (r3)

- No red and no new observation.
- Revision-2 observations are carried forward unchanged, since their inputs did not move: N-1, N-2, O-5, O-7, O-8, O-9, O-10, O-12.

## closing_checklist (r3)

| task | policy self-consistency | problem tree | factors | unique solution |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

- **Files.** Revisions 1 and 2 are preserved verbatim; revision 3 is appended to all three files.
- **Coverage and scopes.** 5/5 policies covered, disjoint scopes, tool set closed at five. Trees and factors are carried forward from r2, whose inputs (charter, views and scored JSON content) did not move.
- **Final-form gates.** REPLAY OK (re-run by me with `--check`); the rest are cited from the coordinator's r3 snapshot, including LINT OK.
- **Conclusion.** The forbidden-token removal regressed nothing. **The difficulty passes the source-layer audit at revision 3.**
