# Policy-task audit — referrals_and_authorizations / charter-global

## charter_global_frozen

- Frozen: 2026-10-11T13:12Z, before any task's GT was revealed. Auditor: independent policy-task auditor (not the instantiating agent).
- `referral.extended.yaml` sha256 `4595c60295052b4c516dcabf5a052adfef4ee443d06226c8725bd811955be673` (matches brief).
- `task_tools.py` sha256 `55d3d700dd62a796c2d08fbd0a4d2f21dc3f8b30a4dac568f927bdf4f1952e07` (matches brief).
- Read: `blueprint/{blueprint.yaml, db_schema.json, share_tools.py, products/*.yaml}`, the extended charter, `task_tools.py`, the two masked views (hashes match the brief), and the restricted-expression evaluator semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (`build_env`: `MONTHS`, `DAYS`, `within_months`, `XLATEST`, `CFIELD`).
- Masked / not read: every task JSON field except `frozen_time`, `user_scenario`, `initial_state`; the difficulty `worklog.md`; `/tmp/erl55ra/`; any other scenario; no recursive grep was run over `tasks/`.
- Entry conditions: the gate snapshot (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire green; check_cache_diff info; check_traceability deferred) and the masked-view hashes came with the brief. Cited, not re-run.
- Base section: lines 1-984 of the extended charter are byte-identical to `blueprint/products/referral.yaml` (`diff` differs only in the trailing blank line).

### policy_conflict_scan

Seven extended policies, seven target tools, one `computes` each:

| policy | subject | target_tool | owner | computes |
| --- | --- | --- | --- | --- |
| referral_ext_facility_day_posting | referral_units_consume | post_facility_day_use_bc338a65 | agent | units |
| referral_ext_lapse_closeout | referral_expire | close_lapsed_authorization_515f616b | agent | units_released |
| referral_ext_overturned_issue | referral_approve_on_appeal | issue_overturned_authorization_2ad92a55 | agent | units_authorized |
| referral_ext_outpatient_cancellation | referral_cancel | confirm_outpatient_cancellation_09e1d470 | user | units_released |
| referral_ext_inpatient_closure | referral_cancel | confirm_inpatient_closure_5bde1317 | user | units_released |
| referral_ext_rofr_lapse_approval | referral_approve | approve_pending_authorization_775ce183 | agent | units_authorized |
| referral_ext_stay_extension | referral_units_extend, referral_validity_update | extend_authorization_stay_203c17fe | agent | units |

- Overlapping subject `referral_cancel` (outpatient_cancellation vs inpatient_closure) is split by object: "an approved authorization counted in visits, hours or rental months" vs "an approved skilled nursing facility or inpatient mental health authorization whose stay has ended". The two sets are disjoint by unit of measure (inpatient_days vs the rest). No overlap.
- Expiry: lapse_closeout covers SNF/IMH expiry only; base `referral_cancellation_and_expiry` keeps governing other tiers. Compatible.
- Approvals: overturned_issue (denied -> approved on appeal) and rofr_lapse_approval (submitted -> approved) act on disjoint source states. Compatible.
- Cross-category read boundaries: facility_day_posting / lapse_closeout / overturned_issue / outpatient_cancellation read `select` (+ `appeal`, `dme`); inpatient_closure / rofr_lapse_approval / stay_extension read `prime`. Writes stay in `referral_*` tables. But see finding F-6: the first two policies' rules cover IMH authorizations, yet their compute reads only Select lines.
- Scope (derived from the prerequisite graph, since `charter_scope` is masked): the graph has two connected components: {facility_day_posting -> lapse_closeout -> overturned_issue -> outpatient_cancellation} and {inpatient_closure -> rofr_lapse_approval -> stay_extension}. With M=2, a disjoint and complete partition is possible only as these two components. Task 0's opening (home-health cancellation) and task 1's opening (IMH stay extension) match the two roots. Compared against `charter_scope` in each task's reveal section.
- Blueprint claim: `event_types` for this difficulty omit `referral_approve` and `referral_approve_on_appeal`, which rofr_lapse_approval and overturned_issue subject. No other difficulty claims them either (grep of blueprint.yaml), and the `referral` category is claimed whole. This is an observation and not one of the four relationships (OBS-C1).

### rule_compute_equivalence

Sentence by sentence against `compute_basis` (all `compute_basis` texts are verbatim in their rule, checked by script) and against each binding:

- **facility_day_posting.** `line_days`/`line_start` are read from the most recently *posted* line (`XLATEST ... date_field='posted_date'`), which matches "the facility line most recently posted for it". `window_cut` matches the three window tiers (`lead_days>=0 and posted_days>lead_days` is "on or after the span's first day and posted days reach that billed day"). `ed_cut` matches 0<offset<last. `away_cut` matches tiers 1/2. `units_left` cap is as stated. Defects:
  - `close_cut` tier 1 carries an extra `line_days > 1` guard the rule does not state. The rule's two tiers overlap as stated (see F-4).
  - The rule covers "skilled nursing facility **or inpatient mental health** authorization", but every read is `XLATEST('select', ...)`. `prime_claim_lines` carries no `inpatient_days` (db_schema), so for a Prime IMH authorization the rule gives a number the compute cannot read (F-6).
- **lapse_closeout.** `x_end_gap = DAYS(line_start,NOW) - line_days` equals the "days from the day after the last billed day to today". `x_lateness = DAYS(valid_through,NOW) - 1` equals "days after the day it fell due". bill/dispute/bedhold/ed tiers match. Observations:
  - `x_dispute`/`x_dispute_filed` use `CFIELD`, which reads the *first* matching case only, while the rule says "such a case" (OBS-C2).
  - The rule covers IMH too, but reads are Select-only (F-6).
- **overturned_issue.** basis / addback / frontload / timing (`hh_3m-hh_1m`, `hh_12m-hh_3m`) / training / risk / cap all match their sentences. The validity-span sentence has no compute (not a computed quantity) and is consistent with base `referral_validity_and_units` ("starts its span on the effectuation date unless the care was already given ..."). `case_status`, `dme_class` and `dme_delivered` read the first matching holding only (OBS-C2).
- **outpatient_cancellation.** counted / open_units cap / closing / equip / period tiers match. Defect: `lag_hold` tier 2. The rule says "fewer than three of its lines are dated in the last month", which includes zero, but the compute requires `k_delivered > 0` (F-7).
- **inpatient_closure.** These map to their sentences:
  - `i_gap = DAYS(last_use, readmit) - days + 1` is "days from the day after the last covered day through the readmission day".
  - `i_dc_gap = ... - days` is "day after last covered day falls before readmission".
  - `i_op_after` is "days after the last covered day".
  - line, repeat and step tiers match.

  No mismatch.
- **rofr_lapse_approval.** block / engage / crisis / repeat / anchor / result bounds match. The validity span ("starts under the tier's start rule") is not computed. No mismatch.
- **stay_extension.** These map to their sentences:
  - `paced` is "fewer than half of validity days have passed" (`e_days_in*2 < validity_days`) or "the last day is today or has passed" (`DAYS(NOW,vt)<=0`).
  - `e_ahead = DAYS(NOW,vt)+1` is "span days still ahead counting today".
  - `e_interval = DAYS(prev_imh, valid_from)`.
  - `room` is the cap.

  No mismatch.
- Every factor's ladder tiers appear in the rule prose and as branches of its `decides` binding. There is no tier that lives only in compute, apart from the `close_cut` guard noted above.

### action_binding_and_uuids

- Each `(target_tool, computes)` is claimed by exactly one policy (table above).
- Docstrings carry no sequence words tying one tool to another and name no other tool. "after the posting" / "after the extension" describe the tool's own returned balance.
- Tool bodies (`task_tools.py` lines 38-52, 78-89, 117-131, 158-175, 212-226, 254-269, 294-311) perform unconditional `ctx.create`/`ctx.update`. None reads another authorization's status, a ledger entry or an appeal case, and none refuses or hints. **The tool layer judges no prerequisite.**
- uuid8s `bc338a65`, `515f616b`, `2ad92a55`, `09e1d470`, `775ce183`, `203c17fe`, `5bde1317` are distinct, share no prefix or tail and show no sequence. PASS.

### prerequisite_graph

| blocked policy | problem | kind | gate | form | policy_source verbatim in own rule | resolved_by = problem's target_tool |
| --- | --- | --- | --- | --- | --- | --- |
| lapse_closeout | facility_day_posting | value_input | x_used (binding exists) | state | yes | yes |
| overturned_issue | lapse_closeout | state_gate | referral_authorizations.status | state | yes | yes |
| outpatient_cancellation | overturned_issue | value_input | k_granted (binding exists) | state | yes | yes |
| rofr_lapse_approval | inpatient_closure | state_gate | referral_authorizations.status | state | yes | yes |
| stay_extension | rofr_lapse_approval | value_input | e_granted (binding exists) | state | yes | yes |

- Every policy fills `prerequisite`: `[]` for facility_day_posting and inpatient_closure. Every `problem` is an extended id, never a base id or self. The graph is two chains, so it is acyclic. All edges are state form, so no `fallback_reason` is required and none is present. There is no authoring-viewpoint phrasing.
- `condition` vs sentence strength:
  - overturned_issue edge: the sentence says "shows as **expired**"; the condition says "no ... still has status approved" (weaker). See F-8.
  - rofr_lapse_approval edge: the sentence says "shows as **cancelled**"; the condition says "no other ... still has status approved" (weaker). See F-8.
  - stay_extension edge: the condition adds "and its status is approved". Base `referral_extension` already limits extension to approved authorizations, so this is harmless (OBS-C3).

### prerequisite_sentences

Four-point test, one row per edge:

| sentence | connective | state named (record words) | no tool/id/snake_case | strength |
| --- | --- | --- | --- | --- |
| "The days a lapsed facility authorization releases are fixed only after every facility claim line billed under the authorization carries its use entry in the unit history." | only after | use entry in unit history per billed line | yes | = condition |
| "A home health care authorization overturned on reconsideration is not issued until every skilled nursing facility authorization of the patient whose validity span has ended shows as expired." | not ... until | status expired | yes | narrower than condition (F-8) |
| "The units a cancellation releases are figured only after any reconsideration of the authorization's denial that was decided overturned or partially overturned shows as a grant on an appeal overturn in the authorization's unit history." | only after | grant on appeal overturn | yes | = condition |
| "A pending inpatient mental health request is not approved until every other inpatient mental health authorization of the patient with the same facility whose validity span is still running shows as cancelled." | not ... until | status cancelled | yes | narrower than condition (F-8) |
| "The days an extension adds are fixed only after the authorization's unit history shows a grant on an initial approval." | only after | grant on initial approval | yes | = condition (+ approved, OBS-C3) |

One write per state, derived as a reader would from the other policies' rules:

- "carries its use entry": only facility_day_posting's rule enters a use. Single reading.
- "shows as expired": only lapse_closeout's rule closes a lapsed SNF/IMH authorization as expired. inpatient_closure cancels, so it does not produce "expired". Single reading.
- "shows as a grant on an appeal overturn": only overturned_issue issues on a reconsideration. Single reading.
- "shows as cancelled" for an IMH authorization: two cancel policies exist, but outpatient_cancellation's rule is confined to "visits, hours or rental months", so only inpatient_closure's rule cancels an inpatient-days authorization. Single reading.
- "shows a grant on an initial approval": only rofr_lapse_approval approves a submitted request. Single reading.

Further checks:

- No rule restates another policy's sentence, and none names a tool or policy id.
- Each blocked policy's object state is also implied by its own base precondition (for example "cancellation of an approved authorization" depends on the overturned issue making the denied HH authorization approved). This grounds the same pair as the declared edge, so it adds no undeclared order.
- No base sentence grounds an edge.

### override_declarations

Sentence by sentence against each `base_policy_refs` entry. Only conflicts and notable inherits are listed. Every other cited base sentence is followed.

- **facility_day_posting** (`overwrite: []`), refs agg_duplicate_requests, unit_consumption, continuity_on_changes.
  - `referral_unit_consumption`: "One unit is used per the tier's units_used_definition." For SNF and IMH the definition is `one_day_per_inpatient_day_excluding_the_discharge_day`. The extended closing-day ladder replaces that by:
    - "where the line bills a single day, the patient was admitted and discharged the same day and that one day is posted" (base: the discharge day is excluded, so 0);
    - "otherwise every billed day stays as billed" (base: the discharge day is excluded even when the stay did not end in a discharge home).

    This is an **undeclared override** (F-1).
  - agg_duplicate_requests (line-to-authorization matching) is followed via `prior_authorization_id`. continuity_on_changes is not touched.
- **lapse_closeout.** The release clause is declared. "An authorization expires on the day after valid_through" is followed ("closed as expired on that day"). Release-after-end and never-reopened are followed. PASS.
- **overturned_issue.** The units clause and the "approval takes the validity span and units the reconsideration decided" clause are declared. However, the base eligibility sentence "The denial is approved on appeal only when a Medical Necessity Reconsideration or Expedited Medical Necessity Reconsideration case for this authorization is decided overturned." is **not** superseded. The extended rule nonetheless issues on "decided partially overturned" (reversal_extent tier 2 and care_under_appeal tier 2) and opens with "decided in the patient's favour". This is an **undeclared override, the dropped-branch form in reverse** (F-2).
- **outpatient_cancellation.** The release clause is declared. "only by their own confirmation" is followed (user tool). PASS.
- **inpatient_closure.** The release clause is declared. PASS.
- **rofr_lapse_approval.** The units clause and plan clause are declared. `referral_agg_duplicate_requests` is cited and **not** overwritten. Its sentence is: "a new request that would duplicate an approved, unexpired authorization is denied as duplicate_request and the patient is pointed to the authorization already on file." The extended policy resolves the same duplicate pair the opposite way: the *older* authorization is cancelled and the *new* request approved ("not approved until every other inpatient mental health authorization ... still running shows as cancelled", plus the state_due "the region approves it"). This is an **undeclared override** of which member of a duplicate pair survives (F-3).
- **stay_extension.** The declared superseded clause includes "up to max_extensions extensions ... and never beyond max_units_per_authorization in total". The replacement states a room cap but no extension-count cap, while the inherited base sentence "A late request, or one beyond the extension limits, is a new request under reauthorization_basis" still refers to "the extension limits". The merged count limit is not unique (OBS-C4).

### factor_ladders

Policy by policy. A factor is "struck" when a skill test removes it: two tiers that select the same value or method, overlapping tiers, or a tier condition that holds for every customer reaching the write.

**facility_day_posting** (declared 4: 2 method, 2 parameter)
- posted_boundary_window (method): 3 distinct tiers (start after last posted / span's first day / own first day). Kept. Multi-source: tier 1 combines line date with ledger posted days.
- emergency_night (parameter): tier 2 "no day dropped for the visit" = fall-through "no day dropped" (`ed_cut` 0 in both). **Struck** (two tiers, same value).
- acute_transfer_days (parameter): tier 1 (inpatient days) and tier 2 (days from start to last billed day) are the two branches of one clipped quantity, min(acute_days, last_offset - acute_offset). Kept for counting, but it is noted as one method split in two (OBS-C5).
- discharge_day (method): tier 2 "single day posted as one day" and fall-through "every billed day posted as billed" both give `close_cut` 0, so **same value**. Tiers 1 and 2 also overlap as stated (a single-day line followed by home-health visits). **Struck** (F-4).
- Surviving: 2 (1 method, 1 parameter). Fails the 4-factor and 2-parameter floors (F-5).

**lapse_closeout** (declared 5: 1 method, 4 parameter)
- readmission_window_reserve (method; min(left,1) / floor(left/2) / 0): real. Multi-source: window from the facility line and home-health lines.
- closing_bill_hold (parameter; 1/2/0): real. Multi-source: line posted date and lapse date.
- open_reconsideration_hold (parameter; 1/2/0): real. Cross-difficulty: appeal.
- bed_hold_reserve (parameter): tier 2 "nothing reserved" = fall-through 0. **Struck**.
- emergency_night_closure (parameter): tier 2 "nothing closed" = fall-through 0. **Struck**.
- Surviving: 3. Below 4 (F-5).
- `baseline.params` names `admission_within_days_of_discharge`, which the baseline rule never uses (OBS-C6).

**overturned_issue** (declared 6: 1 method, 5 parameter)
- reversal_extent (parameter): tier 1 is decided overturned, tier 2 partially overturned, fall-through otherwise. Under the unoverwritten base eligibility (F-2), only "decided overturned" can reach this write. Tier 1 then holds for every customer who reaches it, and tiers 2 and 3 are unreachable. The tier outcomes also change the formula (min vs floor-half vs min-with-default), so the label is questionable (OBS-C7).
- care_under_appeal (method): its tier 2 is likewise reachable only if partial issuance is legal.
- institutional_source, episode_sequence, home_equipment_training, readmission_risk (parameter): constants 6/3/0, 4/2/0, 2/1/0, 4/2/0. Real and distinct. institutional_source is multi-source (SNF + acute lines).
- If F-2 is resolved for base: reversal_extent and care_under_appeal are struck, leaving 4 parameter factors and 0 method, which fails. If resolved for extended: 6 factors survive, but F-2 is a SOURCE-POLICY defect.

**outpatient_cancellation** (declared 6: 2 method, 4 parameter)
- delivered_unposted_visits (method): tier 1 "every such line counts" (`counted = k_delivered`, with k_used = 0) and tier 2 "the lines beyond the posted uses count" (`k_delivered - k_used`) are the same method: tier 1 is tier 2 at k_used = 0. The fall-through is the same quantity clipped at 0. **Struck**.
- appeal_issue_cap (method): its tier 2 (partial grant) depends on F-2.
- closing_visit, equipment_followup, billing_lag, first_period_minimum (parameter): distinct outcomes. first_period_minimum's tier 1 is a formula (8 - lines), which makes its label questionable (OBS-C7).
- Surviving: 5 (1 method) if partial issuance is legal; 4 parameter factors and 0 method otherwise.

**inpatient_closure** (declared 5: 1 method, 4 parameter)
- readmission_split (method): tier 2 "the days left count in full" = fall-through "the days left count in full". **Struck**.
- discharge_day_closure (parameter): tier 2 "0 (the patient was back that day)" = fall-through 0. **Struck**.
- fresh_facility_line, repeat_admission_reserve, outpatient_step_down (parameter): real and distinct.
- Surviving: 3, all parameter, 0 method. Fails (F-5).

**rofr_lapse_approval** (declared 5: 1 method, 4 parameter)
- refusal_window_anchor (method) is **struck** on two counts:
  - Tier 2 "count the block from the admission; nothing added" = fall-through (same method).
  - Tier 1's conditions ("right of first refusal applies, not moved to the military clinic, and more calendar days since the request than the clinic's response business days") hold for every customer who reaches this write. The policy's own trigger is "a TRICARE Prime request of a tier whose military clinic has the right of first refusal is still submitted after the clinic's response window has passed with no answer". A window of B business days that has passed implies more than B calendar days have elapsed, and "no answer" means not moved to the clinic.
- readmission_initial_block (multi-source: IMH line + ED date), aftercare_engagement, emergency_frequency, repeat_admissions (parameter): real.
- Surviving: 4, all parameter, 0 method. Fails (F-5).

**stay_extension** (declared 6: 2 method, 4 parameter)
- unit_span_netting (method): tier 1 "take the excess off" (-(left - ahead)), tier 2 "add the shortfall" (ahead - left) and the fall-through (0 when equal) are all `ahead - left`. One method written as three. **Struck**.
- readmission_block (multi-source: IMH line + earlier-extension count), review_timing (method: halve / +1 / as set), aftercare_step_down, readmission_interval, emergency_frequency_block: real and distinct.
- Surviving: 5 (1 method, 4 parameter). PASS.

Counts per task (cross-difficulty: task 0 reads select/appeal/dme; task 1 reads prime):

| task | multi-source factor surviving | cross-difficulty factor surviving |
| --- | --- | --- |
| task 0 | yes (readmission_window_reserve, institutional_source) | yes |
| task 1 | yes (readmission_initial_block, readmission_block) | yes |

### findings

- **F-1 SOURCE-POLICY RED — undeclared override of the base unit definition (facility_day_posting).**
  - Symptom: the closing-day ladder posts the discharge day in its single-day tier and fall-through, but `overwrite: []`.
  - Root cause: base `referral_unit_consumption` "One unit is used per the tier's units_used_definition", with SNF/IMH `units_used_definition: one_day_per_inpatient_day_excluding_the_discharge_day`. Extended: "where the line bills a single day ... that one day is posted; otherwise every billed day stays as billed".
  - Demonstration: take a 1-day facility line, admit and discharge the same day. Base posts 0 (the only day is the discharge day). Extended posts 1. Take a 5-day line ending in a transfer, with no home-health visits after it. Base posts 4; extended posts 5.
  - Bears on: task 0. No change to task 0's scored value (see 0.md).
- **F-2 SOURCE-POLICY RED — undeclared override of the base appeal eligibility (overturned_issue, outpatient_cancellation).**
  - Base `referral_appeal_effectuation`: "The denial is approved on appeal only when a Medical Necessity Reconsideration or Expedited Medical Necessity Reconsideration case for this authorization is decided overturned." This sentence is not in any `overwrite`. Extended overturned_issue: "where it is decided partially overturned, the basis is half of that figure, rounded down".
  - Demonstration: a denied HH authorization whose MNR is `decided_partially_overturned`. Base: not approved on appeal. Extended: issued with floor(min(req,max)/2) plus add-backs.
  - If base stands instead, reversal_extent's tier-1 condition holds for every customer reaching the write, and reversal_extent/care_under_appeal (and appeal_issue_cap downstream) lose their third tier. overturned_issue and outpatient_cancellation then have no surviving `method` factor (SOURCE-FACTOR).
  - Bears on: task 0. Its case is `decided_overturned`, so the scored value is unchanged.
- **F-3 SOURCE-POLICY RED — undeclared override of base duplicate control (rofr_lapse_approval).**
  - Base `referral_agg_duplicate_requests` (cited in base_policy_refs, not overwritten): "a new request that would duplicate an approved, unexpired authorization is denied as duplicate_request and the patient is pointed to the authorization already on file."
  - Extended: the new request is approved once the *existing* authorization "shows as cancelled".
  - Same situation: a new IMH request at the same facility while an earlier IMH authorization's span is running. Base: deny the new request and use the one on file. Extended: cancel the one on file and approve the new request.
  - Bears on: task 1, with a demonstrated second terminal state (see 1.md).
- **F-4 SOURCE-FACTOR RED — overlapping tiers, rule/compute disagreement (facility_day_posting.discharge_day).**
  - The rule's tier 1 ("home health visits are dated after the line's last billed day") and tier 2 ("the line bills a single day") overlap as stated. In that overlap the rule's first-listed tier drops the only day (0 posted), while the compute's `line_days > 1` guard sends it to tier 2 (1 posted).
  - Tier 2 and the fall-through also give the same `close_cut` (0).
  - Bears on: task 0. Its line is 7 days, so there is no overlap on its world.
- **F-5 SOURCE-FACTOR RED — ladders with two tiers of one outcome, leaving computations below the factor floors.**
  - Tiers that duplicate one another, as listed in factor_ladders: emergency_night, discharge_day, bed_hold_reserve, emergency_night_closure, readmission_split, discharge_day_closure, refusal_window_anchor (also universal tier 1), delivered_unposted_visits (tier 1 = tier 2 method), unit_span_netting (one signed formula).
  - Resulting counts:
    - facility_day_posting: 2 factors.
    - lapse_closeout: 3 factors.
    - inpatient_closure: 3 factors, 0 method.
    - rofr_lapse_approval: 4 factors, 0 method.
  - Bears on: task 0 (posting, closeout) and task 1 (closure, approval).
- **F-6 SOURCE-POLICY RED — rule broader than compute (facility_day_posting, lapse_closeout).**
  - The rules cover "skilled nursing facility or inpatient mental health" authorizations. The compute reads only `select_claim_lines`, and `prime_claim_lines` has no `inpatient_days` column.
  - Demonstration: a Prime IMH authorization with a posted facility line and no use entry. The rule gives "the inpatient days that line carries", which cannot be read from any Prime record. The compute yields `line_days = 0`, result 0.
  - Bears on no task's world: task 1's Prime IMH line already carries its use.
- **F-7 SOURCE-POLICY RED — rule/compute mismatch (outpatient_cancellation.billing_lag tier 2).**
  - Rule: "where its most recent line was posted no more than three days ago and fewer than three of its lines are dated in the last month, two units are held". Compute: `k_bill_age <= 3 and k_delivered > 0`.
  - Demonstration: the servicing provider's only line is dated 40 days ago but posted yesterday. Rule: 2 held. Compute: 0.
  - Bears on: task 0, where `k_delivered = 6` (no consequence).
- **F-8 SOURCE-POLICY RED — prerequisite sentence narrower than its `condition` (overturned_issue edge, rofr_lapse_approval edge).**
  - The sentences require "shows as expired" and "shows as cancelled". The conditions only require "no longer approved".
  - Demonstration 1: an SNF authorization whose span has ended with status `exhausted` never becomes expired (lapse_closeout acts only on approved authorizations). The sentence blocks HH issuance forever; the condition passes.
  - Demonstration 2: an `exhausted` same-facility IMH authorization whose span is still running cannot be cancelled (base cancels only approved authorizations). The sentence blocks approval; the condition passes.
  - Bears on: tasks 0 and 1 (no consequence on either world).
- Observations:
  - OBS-C1: event_types claim omits referral_approve and referral_approve_on_appeal.
  - OBS-C2: `CFIELD` takes the first matching record where the rule says "such a case" or "an item".
  - OBS-C3: the extension edge's condition adds "approved".
  - OBS-C4: the extension-count limit is left non-unique by the overwrite.
  - OBS-C5: acute_transfer_days' two tiers are branches of one min.
  - OBS-C6: lapse_closeout `baseline.params` names a key the baseline does not use.
  - OBS-C7: parameter labels on tiers that change the formula (reversal_extent, first_period_minimum, acute_transfer_days).

## closing_checklist

Written 2026-10-11T13:18Z, after both reveals. The charter-global section above is unchanged since its pre-reveal freeze (sha256 `19c83ec0…`).

The difficulty does **not** close: neither task has all four relationships PASS.

- Per-task files: `0.md` and `1.md` correspond one-to-one with `tasks/0.json` and `tasks/1.json`. This is the first revision.
- Coverage and scope: the revealed `charter_scope`s are {facility_day_posting, lapse_closeout, overturned_issue, outpatient_cancellation} and {inpatient_closure, rofr_lapse_approval, stay_extension}. They are pairwise disjoint, jointly cover all seven extended policies and their seven tools, and the uuid8s are independent. PASS.
- Trees:
  - task 0 is a 3-prerequisite chain with 2 value_input edges.
  - task 1 is a 2-prerequisite chain with 1 value_input edge.

  Each has an `owner=user` write, and the whole graph is acyclic. PASS. Task 1's tree depends on the extended reading of F-3.
- Factors: FAIL. F-5 floors:
  - task 0: posting 2 factors, closeout 3, and, if F-2 resolves for base, no method in issue or cancel.
  - task 1: closure 3 factors with no method, approval no method.
- Unique solution: task 0's scored arguments are unique and equal to GT, but its proof text contradicts the seed (0.md finding 3). Task 1 is SOURCE-TASK RED (second complete solution, 1.md finding 1).
- Gates: not re-run by the auditor. The brief's snapshot is cited above, and no artifact changed.

Per-task verdict lines:

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| task 0 | SOURCE-POLICY RED | PASS | SOURCE-FACTOR RED | SOURCE-TASK RED (proof text only; scored arguments match GT) |
| task 1 | SOURCE-POLICY RED | PASS (extended reading) | SOURCE-FACTOR RED | SOURCE-TASK RED |

## revision_2

### charter_global_frozen (revision 2)

- Frozen: 2026-10-11, before any revision-2 GT was revealed. Auditor: same independent auditor as round 1.
- `referral.extended.yaml` sha256 `d71da01cfde647a3332aa4e10ecf67ae1b5669ba3eab8ae1c0d63ec8292c31ab` (changed), so every charter-global section below is **re-derived in full**.
- `task_tools.py` sha256 `55d3d700…` (unchanged), so action_binding_and_uuids is carried forward by reference to revision 1 on the strength of the unchanged hash.
- The base section is still byte-identical to `blueprint/products/referral.yaml`.
- Read: the charter, `task_tools.py`, the blueprint, the rebuilt views (`0.view.json` `46e76593…`, `1.view.json` `07be4d03…`, matching the brief) and the check_compute evaluator semantics.
- Not read: task JSON, worklog, `/tmp/erl55ra/`.
- Entry: the brief's gate snapshot (all green; traceability deferred) is cited.

### policy_conflict_scan (r2)

- Seven policies, seven tools, unchanged bindings (target_tool, computes, owner as in revision 1).
- Scope boundaries now split by plan:
  - facility_day_posting and lapse_closeout cover "... authorization covered under TRICARE Select".
  - inpatient_closure covers "... covered under TRICARE Prime".
  - outpatient_cancellation still covers visits/hours/rental months.
- The `referral_cancel` subjects stay disjoint (inpatient days vs the rest; Prime only for inpatient closure).
- Gaps, observation **OBS-R2-1**:
  - An ended Prime SNF authorization can satisfy the overturned_issue gate only through base system expiry. No extended write closes it, because lapse_closeout is Select-only.
  - A running Select IMH authorization has no extended cancel write, because inpatient_closure is Prime-only.
  - Neither case occurs in any task world.
- Scope partition: unchanged (two chains). The blueprint event_types omission (OBS-C1) is unchanged.

### rule_compute_equivalence (r2)

Swept sentence by sentence again. All `compute_basis` entries are verbatim in their rule (script).

- **facility_day_posting.**
  - `window_cut` is the three window tiers (now clipped by `MN(line_days, …)`).
  - `span_end_cut` is "a covered day that falls after the last day of the authorization's validity span is not posted".
  - `ed_cut` is "on a covered day after its first covered day" plus admission next day (1) or second day (min(2, days to the line end)).
  - `away_cut` matches its two tiers (the covered days are start..start+days-1).
  - `return_adj` tier 1 is min(transport-1, line end) - discharge + 1; tier 2 is discharge - transport.
  - Observation **OBS-R2-2**: both return tiers carry `acute_offset > 0` in compute, while the rule says only "that acute admission". The divergence needs an acute admission that starts before the line yet is discharged inside it, which contradicts the patient being at the facility on the line's first covered day. There is no consequence.
- **lapse_closeout.**
  - `x_dispute` is now `XLATEST(... date_field='filing_date')`, matching "the patient's most recent such case" (OBS-C2 closed here).
  - `interruption_hold`: rule "dated on or after the span's first day and on or before the facility line's last covered day" matches the compute.
  - `final_bill_hold` tier 1 is tail-1 ("up to, but not counting, the span's last day"), tier 2 is tail ("through the span's last day"), and the tier conditions match.
  - `baseline.params` is now `[]` (OBS-C6 closed).
- **overturned_issue.**
  - `case_status`/`case_id` use the most recent case by filing date.
  - `case_lmn` counts letter-of-medical-necessity documents on that case.
  - `basis` tier 1 requires both. The rule ("the patient's most recent reconsideration of the authorization is decided overturned and a letter of medical necessity is on that case") matches.
  - `dme_*` use the most recently delivered item in rental, matching "the patient's most recently delivered item in rental". OBS-C2 is closed.
- **outpatient_cancellation.**
  - `counted` tier 1 (appeal grant) is MX(0, lines in month - used). Tier 2 (no grant, lines outnumber uses) is lines_all - used.
  - `lag_hold` tier 2 is now `k_lines_month < 3`, which includes zero, matching "fewer than three". **F-7 closed.**
  - `period_hold` is now constant 2/1/0.
- **inpatient_closure.**
  - `basis` tier 2 is `i_span_after` (span days after the last covered day), applied when it is fewer than the days left. The extra compute guard `i_span_after >= 0` covers the case where the last covered day lies past the span end, which the rule does not contemplate. No consequence (OBS-R2-3).
  - `crisis_hold` is 2/1/0 on emergency visits in the month. The others are unchanged and match.
- **rofr_lapse_approval.**
  - `paced` is: gap 1-7 days from the most recent IMH line to the request date, so the block is halved and rounded up; 8-30 days, so the block is rounded up to a multiple of `concurrent_review_interval_days`; otherwise the block.
  - The result bounds match. The "block counted from the decision date" sentence is gone (revision-1 task-1 observation closed).
- **stay_extension.**
  - `net` tier 2 rounds the shortfall up to whole review intervals.
  - `room` is 0 once `e_ext_count >= max_extensions`, matching "nothing once the authorization has had the tier's maximum extensions" (OBS-C4 closed).

### action_binding_and_uuids (r2)

Carried forward from revision 1 (the `task_tools.py` hash is unchanged): PASS.

### prerequisite_graph (r2)

| blocked | problem | kind | gate | form | verbatim | condition vs sentence |
| --- | --- | --- | --- | --- | --- | --- |
| lapse_closeout | facility_day_posting | value_input | x_used | state | yes | equal |
| overturned_issue | lapse_closeout | state_gate | status | state | yes | "expired or exhausted" = "status expired or exhausted". **F-8 closed** |
| outpatient_cancellation | overturned_issue | value_input | k_granted | state | yes | equal |
| rofr_lapse_approval | inpatient_closure | state_gate | status | state | yes | "every other IMH ... still running shows as cancelled or exhausted" = "valid_through on or after today ... cancelled or exhausted". **F-8 closed** |
| stay_extension | rofr_lapse_approval | value_input | e_granted | state | yes | equal; the "approved" add-on is dropped (OBS-C3 closed) |

- The graph is acyclic.
- One write per state:
  - "expired" comes only from lapse_closeout.
  - "exhausted" has no write in this difficulty (base system transition), so the hop resolves uniquely to the expiry write.
  - IMH "cancelled" comes only from inpatient_closure (see OBS-R2-1 for the plan split).

### override_declarations (r2)

- **F-1 closed.** facility_day_posting now states "the discharge day is never a covered day, as the tier's unit definition requires", and the closing-day ladder is gone. It agrees with base `units_used_definition` with no override.
- **F-2 closed.** overturned_issue now supersedes both base appeal-effectuation eligibility sentences ("A denied authorization is approved without a new review only when its reconsideration is decided overturned." and "The denial is approved on appeal only when ... decided overturned."). Both appear verbatim in base, and the replacement admits partial overturns.
- **F-3: charter-level conflict persists (SOURCE-POLICY RED, no task consequence in revision 2).**
  - rofr_lapse_approval now declares an overwrite of `referral_agg_multi_holding` ("A patient holds only one open inpatient mental health authorization at a time, whatever the facility").
  - `referral_agg_duplicate_requests` is still cited and still not overwritten: "a new request that would duplicate an approved, unexpired authorization is denied as duplicate_request and the patient is pointed to the authorization already on file."
  - Situation: a pending IMH request at the **same** facility while an earlier IMH authorization at that facility is approved with its span running. Base denies the new request and keeps the old one. Extended (state_due "the region approves it" plus "not approved until every other ... shows as cancelled or exhausted") cancels the old one and approves the new one.
  - For different facilities, base says "never a duplicate" and the declared one-open rule governs, so there is no conflict. Task 1's re-seed moved the readmission to a different facility (see 1.md revision_2).
- **OBS-C4 closed.** The extension-count cap is restated in rule and compute.
- Other policies: no new conflict found.
  - lapse_closeout and outpatient_cancellation keep only the declared release overwrite.
  - inpatient_closure's new readmission tier 2 governs the release figure under its declared overwrite.
  - stay_extension follows base `extension_on_time`.

### factor_ladders (r2)

| policy | factors (effect) | struck | surviving: total / param / method |
| --- | --- | --- | --- |
| facility_day_posting | posted_boundary_window (M), emergency_night (P: 1 / min(2,…) / 0), acute_transfer_days (P), return_transport_anchor (M: extra drop / add-back / none) | none | 4 / 2 / 2 |
| lapse_closeout | readmission_window_reserve (M), closing_bill_hold (P 1/2/0), open_reconsideration_hold (P 1/2/0), interrupted_stay_hold (P 2/1/0), final_bill_days (M: tail-1 / tail / 0) | none | 5 / 3 / 2 |
| overturned_issue | reversal_extent (M, relabelled), care_under_appeal (M), institutional_source, episode_sequence, home_equipment_training, readmission_risk (P) | none (partial overturn now declared legal, so tiers 2 are reachable) | 6 / 4 / 2 |
| outpatient_cancellation | billed_visit_window (M: month window less uses / all lines beyond uses / none, distinct windows), appeal_issue_cap (M), closing_visit, equipment_followup, billing_lag, first_period_minimum (P, now constants 2/1/0) | none | 6 / 4 / 2 |
| inpatient_closure | readmission_split (M: gap / span days after last covered / full; tier 2 ≠ fall-through now), crisis_frequency_hold (P 2/1/0), fresh_facility_line, repeat_admission_reserve, outpatient_step_down (P) | none | 5 / 4 / 1 |
| rofr_lapse_approval | readmission_initial_block, aftercare_engagement, emergency_frequency, repeat_admissions (P), readmission_pacing (M: halve / round up to review intervals / as set) | none (no tier condition restates the trigger) | 5 / 4 / 1 |
| stay_extension | readmission_block (P), review_timing (M), aftercare_step_down (P), unit_span_netting (M: excess off / shortfall rounded up to review intervals / none, now distinct), readmission_interval (P), emergency_frequency_block (P) | none | 6 / 4 / 2 |

- **F-5 closed**: no two tiers of any ladder select the same value or method. **F-4 closed**: the discharge_day factor is removed, so there are no overlapping tiers.
- OBS-C5 (acute_transfer_days' tiers are the two branches of one clipped count) is unchanged by the reworker. It stays an observation: the tier-1 and tier-2 formulas give different values in each other's regions, so the tiers are not one method written twice.
- OBS-C7: reversal_extent is relabelled and first_period_minimum is now constants. acute_transfer_days keeps `parameter` (it ties to OBS-C5).
- Multi-source factors survive in both components: readmission_window_reserve, institutional_source, interrupted_stay_hold, readmission_initial_block, readmission_block. Cross-difficulty reads: select / appeal / dme for task 0's component and prime for task 1's.

### findings (r2)

- Round-1 F-1, F-2, F-4, F-5, F-6, F-7, F-8: **closed** (evidence above).
- Round-1 OBS-C2, OBS-C3, OBS-C4, OBS-C6: closed. OBS-C7: mostly closed. OBS-C1, OBS-C5: unchanged, as the reworker declared.
- **F-3 (residual): SOURCE-POLICY RED, charter-level.** The undeclared override of base duplicate denial for same-facility IMH pairs remains, with the demonstration as stated under override_declarations. It bears on no task world in revision 2 (task 1's pair spans two facilities).
- New observations:
  - OBS-R2-1: the plan split leaves gate states with no extended write (Prime SNF expiry, Select IMH cancel).
  - OBS-R2-2: the return-transport tiers carry an `acute_offset > 0` guard the rule does not state (no realistic world diverges).
  - OBS-R2-3: readmission_split tier 2 carries a `>= 0` guard the rule does not state.
- No regression found in the charter-global checks.

### closing_checklist (revision 2)

Written after both r2 reveals. The revision_2 charter-global section above is unchanged since its freeze (`8980e0d8…`).

- Files: 0.md and 1.md each carry revision_1 and revision_2. The older text is untouched.
- Scope: disjoint and complete (4 + 3 policies, 7 tools); uuid8s carried forward. PASS.
- Trees:
  - task 0: 3 prerequisites, 2 value edges, user write present.
  - task 1: 2 prerequisites, 1 value edge, user write present.
  - The graph is acyclic. PASS.
- Factors: every computation has 4-6 factors with at least 2 parameter and at least 1 method; every ladder has distinct outcomes; each task has a multi-source and a cross-difficulty factor; every factor bears weight against an honest baseline, and the fall-backs differ from gold. PASS.
- Unique solution: both tasks' blind r2 derivations equal GT, and no second reading survives. PASS.
- Policy self-consistency: **not closed**. Residual F-3 (an undeclared override of the base duplicate-denial sentence for same-facility IMH pairs) remains in rofr_lapse_approval. It has no consequence on either task world.
- Gates: the coordinator's r2 snapshot is cited and was not re-run by the auditor.

The difficulty does **not** close on revision 2, solely because of residual F-3.

Per-task verdict lines (revision 2):

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| task 0 | PASS | PASS | PASS | PASS |
| task 1 | SOURCE-POLICY RED (charter residual F-3, no world consequence) | PASS | PASS | PASS |

## revision_3

### charter_global_frozen (revision 3)

- Frozen: 2026-10-11, before any revision-3 GT was revealed. Auditor: the same independent auditor.
- `referral.extended.yaml` sha256 `f3d39fde2387e13bb7cbc1e2538de0a4d9f058e694ea9f16972a6be9e6fb2541` (changed), so the charter-global checks are re-run in full. A snapshot copy is kept at `/tmp/erl55_audit_referral/ext_r3.yaml` for later rounds.
- `task_tools.py` `55d3d700…` is unchanged, so action_binding_and_uuids is carried forward on the hash.
- The views are unchanged (`46e76593…`, `07be4d03…`, matching the brief). The base section is still byte-identical to the blueprint.
- No task JSON, worklog or `/tmp/erl55ra/` was read before this freeze.

### what changed (located by re-reading every policy's rule, overwrite, prerequisite, compute and factors against the revision-2 audit text)

1. **rofr_lapse_approval.**
   - The trigger now requires "and it duplicates no approved, unexpired authorization of the patient".
   - New rule sentence: "A request that would duplicate an approved, unexpired authorization of the same type for the same patient and the same servicing provider is not approved under this rule: it is denied as duplicate_request and the patient is pointed to the authorization already on file, as the duplicate rule requires."
   - The prerequisite sentence and condition are narrowed to "every other inpatient mental health authorization of the patient **with a different servicing provider** whose validity span is still running shows as cancelled or exhausted" / "a servicing_provider_id different from the request's".
2. **facility_day_posting.** Both return-transport tiers in the rule now carry "where that acute admission began after the line's first covered day", matching the compute's `acute_offset > 0` guard. The factor ladder text is updated to match.
3. **inpatient_closure.** `basis` tier 2 is now `MX(0, i_span_after) if i_span_after < i_left`, so a negative span remainder counts as none. This matches the rule's "only those span days count".
4. The rule, overwrite, prerequisite and factor text of lapse_closeout, overturned_issue, outpatient_cancellation and stay_extension is unchanged from revision 2. Their computes reproduce the revision-2 figures on both worlds (replay below).

### policy_conflict_scan / rule_compute_equivalence / prerequisite_graph / prerequisite_sentences (r3)

- Every `compute_basis` entry, prerequisite sentence and superseded clause is verbatim (script `verbatim.py`, all True). Bindings are disjoint, and no factor decides `result`.
- rofr_lapse_approval's prerequisite edge: the sentence and condition match one for one (different servicing provider, span running, cancelled or exhausted).
- Writes that bring the waited-on state about: only inpatient_closure (Prime) cancels an IMH authorization, and exhausted has no write. One reading. The graph is acyclic. The other four edges are unchanged from revision 2.
- **Residual F-3 closed.** In the same-facility case the extended rule now follows base `referral_agg_duplicate_requests` verbatim in effect: the new request is denied as duplicate_request and the patient is pointed to the authorization on file. The gate applies only to other-facility authorizations, under the declared one-open overwrite of `referral_agg_multi_holding`. No situation is left where base and extended reach different conclusions.
- New sentence check: the restated duplicate-denial sentence names an outcome (deny) for which this difficulty has no task tool. It is a base outcome restated, not a new procedure, and it changes no scored quantity. Observation **OBS-R3-1**, no consequence.
- **OBS-R2-2 closed**: the rule now states the guard. **OBS-R2-3 closed**: the compute now clips at zero, matching the rule.
- OBS-R2-1, OBS-C1 and OBS-C5 are unchanged, as the reworker declared. OBS-R2-T1 is a task-1 observation, carried in 1.md.

### override_declarations (r3)

- rofr_lapse_approval's undeclared override of the base duplicate denial is removed (see above). The other declarations are as in revision 2. No new conflict.

### factor_ladders (r3)

- Unchanged structure: posting 4 (2 parameter / 2 method), lapse 5 (3/2), issue 6 (4/2), cancellation 6 (4/2), closure 5 (4/1), approval 5 (4/1), extension 6 (4/2).
- No two tiers of any ladder share an outcome, no tier condition restates a policy's trigger, and tiers 1/2 of return_transport_anchor are now stated with the guard in both faces. PASS.

### findings (r3)

- Residual F-3: **closed**. OBS-R2-2 and OBS-R2-3: **closed**.
- New: OBS-R3-1 (observation only).
- No new RED. No regression.

### closing_checklist (revision 3)

Written after the r3 reveals. The revision_3 charter-global section is unchanged since its freeze (`20244bb5…`).

- Files: 0.md and 1.md each carry revisions 1-3. The older text is untouched.
- Coverage and scope: 4 + 3 policies, disjoint and complete, 7 tools with independent frozen uuid8s (tool module unchanged since revision 1). PASS.
- Trees:
  - task 0: 3 prerequisites, 2 value_input edges, user cancellation.
  - task 1: 2 prerequisites, 1 value_input edge, user closure.
  - The graph is acyclic across the difficulty. Every edge is unmet at its task's opening and bears weight. PASS.
- Factors: every computation has 4-6 factors with at least 2 parameter and at least 1 method. Every ladder has at least 3 distinct-outcome tiers, all stated in its rule. Each task has a multi-source factor and a cross-difficulty factor (select, appeal and dme for task 0; prime for task 1). Every factor bears weight against an honest baseline, and the fall-backs (7/8/30/52; 6/7/3) all differ from gold. PASS.
- Unique solution: the blind derivations equal GT in both tasks, and no second reading survives. PASS.
- Policy self-consistency: all round-1 and round-2 REDs are closed, with no new RED. PASS.
- Remaining observations (no relationship affected): OBS-C1, OBS-C5, OBS-R2-1, OBS-R2-T1, OBS-R3-1.
- Gates: the coordinator's r3 snapshot is cited. The traceability gate is deferred to after the KB render, and the auditor did not re-run the gates.

**The difficulty passes the source-layer policy-task audit at revision 3.**

Per-task verdict lines (revision 3):

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| task 0 | PASS | PASS | PASS | PASS |
| task 1 | PASS | PASS | PASS | PASS |

## revision_4

### charter_global_frozen (revision 4)

- Frozen: 2026-10-12, before any r4 GT reveal.
- `referral.extended.yaml` sha256 `498011d718b4c9b3cbb4e711153a74cd19beaab79832a525b43d1918bd08a799` (changed). A full textual diff against my frozen r3 snapshot (`/tmp/erl55_audit_referral/ext_r3.yaml` -> `ext_r4.yaml`) shows **only** these edits:
  1. inpatient_closure step-down: the rule sentence, its three `compute_basis` copies and its ladder text; `step_adj` gains `and i_gap > 0`.
  2. rofr_lapse_approval pacing: the rule sentence, its three `compute_basis` copies and its ladder text; `paced` tier 2 gains `and P('concurrent_review_interval_days') > 0`.
  3. stay_extension netting: the rule sentence, its `compute_basis` copies and its ladder text; `net` tier 2 gains `if P('concurrent_review_interval_days') > 0 else (e_ahead - e_left)`.

  Nothing else changed.
- `task_tools.py` is unchanged (`55d3d700…`), so action_binding_and_uuids is carried forward. The views are unchanged (`46e76593…`, `07be4d03…`).
- All `compute_basis` entries, prerequisite sentences and superseded clauses are verbatim (30/30 checks True). Bindings are disjoint.

### audit-miss disclosure

Both defects the coordinator surfaced at render time were present in the charter I audited in revisions 1-3 and were not caught:

- **Revisions 2 and 3 stated "the others are unchanged and match" for inpatient_closure's step-down tier.** Revision 1 also stated the step tiers match. That was wrong. Rule tier 2 required "the readmission is inside the span" (ED after the last covered day and on or before the span's last day), while compute tested only `i_inside >= 0`.
- **The revision-2 sweep of rofr_lapse_approval `paced` and stay_extension `net` checked the tier conditions but not the domain of the rounding formula.** For tiers with `concurrent_review_interval_days: 0` (Specialty Care, Rehabilitative Therapy, DME, ABA) the formula divided by zero, and no rule sentence defined the outcome.

The earlier conclusions on those two checks are superseded by this revision. The text of earlier revisions is left as written.

### verification of the round-4 fixes

- **(1) inpatient_closure step-down — fix verified, residual mismatch found (F-9 below).**
  - Compute now requires `i_op_after > 7 and i_inside >= 0 and i_gap > 0`. That is "the patient's most recent emergency visit is after the last covered day and on or before the span's last day", which is the same readmission test as readmission_split tier 1.
  - The rule's new parenthetical defines the condition existentially: "there is a readmission inside the span (**an** emergency department visit dated after the last covered day and on or before the span's last day)". Compute tests only the **most recent** ED visit. See F-9.
- **(2) rofr_lapse_approval pacing — closed.**
  - Rule: "where it is dated eight to thirty days before the request date and the tier sets a concurrent review interval ...; otherwise, including a tier that sets no concurrent review interval, the block stands as set".
  - Compute guards the condition with `P('concurrent_review_interval_days') > 0`. Python's conditional expression evaluates only the selected branch, so no division by zero is reachable.
  - The ladder states the same. The three tiers stay pairwise distinct (halve / round up to intervals / as set).
- **(3) stay_extension netting — closed.**
  - Rule: "rounded up to a whole number of the tier's concurrent review intervals, or added as it stands where the tier sets no concurrent review interval".
  - Compute: `... if P('concurrent_review_interval_days') > 0 else (e_ahead - e_left)`. The ladder is updated.
  - Tier 2 still differs from tier 1 (excess taken off vs shortfall added) and from the fall-through (0).

### same-shape sweep across the whole charter (coordinator request)

- **Undefined division.** Every `/` in every compute was enumerated with each divisor checked against all seven tiers' parameters (script):

  | divisor | where | status |
  | --- | --- | --- |
  | constant 2 | lapse reserve, overturned basis/addback, cancellation cap, both `paced` halvings | safe |
  | `concurrent_review_interval_days` | rofr_lapse_approval `paced`, stay_extension `net` | now guarded |

  No other parameter or field divisor exists. Zero-valued parameters used in comparisons rather than divisions are defined:
  - `admission_within_days_of_discharge` is 0 for IMH in lapse_closeout's reserve window, so the tier condition `gap <= 0` is simply rarely true.
  - `max_extensions` is 0 for DME and ABA in stay_extension's room, giving room 0 and an extension of 0 for tiers the rule already excludes ("a tier that allows extensions").
- **Rule-vs-compute condition drift.** Every tier condition of every factor in all seven policies was re-read against its compute conjuncts. Matches: the posting window, ED, acute and return tiers; the lapse reserve, bill, dispute, interruption and final-bill tiers; all six overturned_issue tiers; all six cancellation tiers; the closure split, crisis, line and repeat tiers and step tier 1; all approval tiers (block tier 1's "an emergency visit ... no more than seven days ago" is equivalent to the latest ED being within 7 days); all extension tiers.
- **One mismatch remains: the step-down tier 2 existential, F-9.**

### findings (r4)

- Coordinator item (2) (the rofr pacing and stay-extension netting division): **closed**.
- Coordinator item (1) (the step-down conjunct): **compute fixed, but F-9 is open**.
- **F-9 SOURCE-POLICY RED — rule/compute mismatch in inpatient_closure `outpatient_step_down` tier 2 (charter-level).**
  - Rule: "where it falls more than seven days after the last covered day and there is a readmission inside the span (an emergency department visit dated after the last covered day and on or before the span's last day), one more day is held". The same rule's readmission split uses "the patient's **most recent** emergency department visit".
  - Compute: `... and i_inside >= 0 and i_gap > 0`, where both bindings read only `i_readmit` = the latest ED (`XLATEST ... service_class='emergency_room_visit'`).
  - Demonstration (`/tmp/erl55_audit_referral/r4_demo.py`): task 1's world plus a hypothetical ED line on 2026-10-09 and OP visit on 2026-10-10, evaluated at 2026-10-12.
    - Rule: the 10-05 ED visit lies after the last covered day 10-01 and on or before the span's last day 10-07, and the OP visit is 9 days after the last covered day. So one day is held, giving release **2**.
    - Compute: the latest ED is 10-09, so `i_inside = -2`, `step_adj = 0`, giving release **3**.
  - It bears on task 1's closure computation. There is no consequence on task 1's world: its only post-coverage ED (10-05) is also the latest, and its step tier is tier 1 (OP 1 day after).
- Carried observations: OBS-C1, OBS-C5, OBS-R2-1, OBS-R3-1. No other new defect and no regression.

### closing_checklist (revision 4)

Written after the r4 reveals. The revision_4 charter-global section is unchanged since its freeze (`794c8d4a…`).

| check | result |
| --- | --- |
| scope / tools / uuid8s | PASS (unchanged) |
| trees | PASS (unchanged; edge texts byte-equal to charter) |
| factors | PASS (structure unchanged; every fixed ladder keeps three distinct-outcome tiers; all factors bear weight on both worlds) |
| unique solution | PASS (GT unchanged and equal to blind recomputation) |
| policy self-consistency | **not closed**: F-9 (inpatient_closure step-down tier 2, existential rule vs latest-ED compute) |
| gates | coordinator r4 snapshot cited (all OK incl. traceability); not re-run by the auditor |

The difficulty does **not** close on revision 4, solely because of F-9.

Per-task verdict lines (revision 4):

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| task 0 | PASS | PASS | PASS | PASS |
| task 1 | SOURCE-POLICY RED (F-9, charter-level, no world consequence) | PASS | PASS | PASS |

## revision_5

### charter_global_frozen (revision 5)

- Frozen: 2026-10-12, before any r5 GT reveal.
- `referral.extended.yaml` sha256 `e3f5aae40aaefdc2f313e608f7a23830dd82c6785ebf2942b43c811644b4e21f` (changed). A full diff against my r4 snapshot (`ext_r4.yaml` -> `ext_r5.yaml`) shows only these edits:
  1. **lapse_closeout.**
     - New rule sentence: "In these rules the facility line is the facility claim line most recently posted under the authorization, and its last covered day is its service date plus its covered inpatient days, less one day."
     - It replaces the `compute_basis` of `x_line_start`, `x_line_days` and `x_last_offset`, which previously quoted the reserve and final-bill sentences.
  2. **inpatient_closure step-down.** The rule sentence, its three `compute_basis` copies and the ladder tier-2 text now read "the patient's most recent emergency department visit is dated after the last covered day and on or before the span's last day, the same test the readmission split uses".

  No compute expression changed.
- `task_tools.py` is unchanged and the views are unchanged. Verbatim checks: 30/30 True, 0 False.

### verification

- **F-9 closed.**
  - Rule, `compute_basis` and ladder now all name the most recent ED visit, which is what `i_readmit` (`XLATEST ... emergency_room_visit`) feeds into `i_gap > 0 and i_inside >= 0`.
  - Re-running the revision-4 demonstration world (`r4_demo.py`: extra ED 10-09, OP 10-10, NOW 10-12): the rule now reads that the most recent ED (10-09) is after the span's last day (10-07), so nothing is held. That gives release 3, which equals the compute's 3. There is no divergence.
  - The wording is also now consistent with readmission_split tier 1 in the same rule.
- **lapse_closeout "facility line" definition.**
  - "most recently posted under the authorization" = `XLATEST(... date_field='posted_date', prior_authorization_id=HID)`.
  - "service date plus covered inpatient days, less one" = `x_last_offset = x_line_days - 1` offset from `x_line_start`.
  - Exact match. Every other sentence of the rule still backs its bindings: the reserve sentence backs `x_end_gap`/`x_home_count`/`reserve`, and the final-bill sentence backs `x_tail_days`/`final_bill_hold`.
- **Quantifier sweep (re-run on r5).** The revision-4 all-tier sweep stands; the only tier text changed since is the step-down, now aligned.
  - Every remaining existential ("an emergency department visit ... in the last month", "home health visits ... dated in the last month", "claim lines from the servicing provider are dated in the last month") is implemented by a count over all rows, so existential and compute agree.
  - Every definite reference ("the patient's most recent ...") is implemented by `XLATEST`.
  - The other existential, approval block tier 1 ("an emergency department visit is dated no more than seven days ago" vs the latest ED), was shown equivalent in revision 4.
- **Rule-sentence coverage (new script check).** Every rule sentence that states a computed quantity appears in some `compute_basis`. The sentences that do not are prerequisite sentences, trigger/eligibility sentences, the overturned_issue validity-span sentence (a scored date argument, not a `computes` quantity), and the baseline standard-method sentences, whose values enter compute through the factor baselines and the final cap sentence. No empty promise.
- **Undefined division.** Unchanged since revision 4: only the constant 2 and the guarded `concurrent_review_interval_days` are used as divisors.
- **Factor structure.** Unchanged (4/5/6/6/5/5/6). No ladder outcome changed.

### findings (r5)

- F-9: **closed**.
- No new RED. No regression.
- Carried observations: OBS-C1, OBS-C5, OBS-R2-1, OBS-R2-T1, OBS-R3-1.

### closing_checklist (revision 5)

Written after the r5 reveals. The revision_5 charter-global section is unchanged since its freeze (`2278bd86…`).

- Files: 0.md and 1.md carry revisions 1-5. Older text is untouched; the one exception is the missing `## revision_5` heading in 1.md, inserted after the reveal and noted in place.
- Scope, tools and uuid8s: PASS.
- Trees:
  - task 0: 3 prerequisites, 2 value_input edges, user cancellation.
  - task 1: 2 prerequisites, 1 value_input edge, user closure.
  - The graph is acyclic and every edge bears weight. PASS.
- Factors: 4-6 per computation, at least 2 parameter and 1 method each, distinct three-tier ladders stated in their rules, multi-source and cross-difficulty factors in each task, every factor bearing weight against an honest baseline, and fall-backs different from gold. PASS.
- Unique solution: GT equals the blind derivations in both tasks. PASS.
- Policy self-consistency: F-1..F-9 are closed, with no RED outstanding. The all-tier quantifier, division and rule-coverage sweeps are clean. PASS.
- Observations only: OBS-C1, OBS-C5, OBS-R2-1, OBS-R2-T1, OBS-R3-1.
- Gates: the coordinator's r5 snapshot is cited (all OK, including traceability). The auditor did not re-run them.

**The difficulty passes the source-layer policy-task audit at revision 5.**

Per-task verdict lines (revision 5):

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| task 0 | PASS | PASS | PASS | PASS |
| task 1 | PASS | PASS | PASS | PASS |
