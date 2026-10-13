# Policy-task audit — workers_comp_referrals_and_billing / charter-global

## charter_global_frozen

- Auditor: independent erl-task-policy-audit agent (not the author of the artifacts); unattended run.
- Freeze time: 2026-10-05T05:19Z (written before any task's GT was revealed; contains nothing derived from a revealed GT).
- Frozen inputs (sha256, re-verified against the source files at audit start):
  - `wc.extended.yaml` 558b3e06ea479ba06a302efb9eac8f70ad0d2ad0c1a3f9f1b7184080002d8213 (identical to `env/env_0032_physical_therapy_clinic_network/tasks/workers_comp_referrals_and_billing/wc.extended.yaml`)
  - `task_tools.py` c39f615eaf81cf92a650bdff43838a5eec3d3a678d8982b6aecab467d28889be (identical to the source)
- Fields permitted: the blueprint (`blueprint.yaml` difficulty entry, `db_schema.json`, `share_tools.py`, `products/wc.yaml`, and `products/series.yaml` for the cross-difficulty fields), the extended charter and tool module above, and the masked views `/tmp/erl0032_views/workers_comp_referrals_and_billing/task{0,1}.visible.json` (frozen_time, user_scenario, initial_state only).
- Fields masked until every task's derivation is frozen: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure` and closure fields of `tasks/0.json` and `tasks/1.json`; no earlier audit exists for this difficulty.
- Entry conditions (Step 0): the orchestrator's brief supplies the gate snapshot (check_extended EXTENDED OK, check_task_tools TASK TOOL CONTRACT OK, replay_tasks REPLAY OK, check_solvability SOLVABILITY OK, check_compute COMPUTE OK, check_grounding GROUNDING OK, check_cross_fire SCOPE OK; check_traceability deferred pending the published KB; blueprint gates BLUEPRINT OK, SHARE TOOLS OK, VALID), the masked views and their hashes. All four view hashes matched on disk. check_traceability being deferred is recorded, not treated as a failure of this audit (it is a KB-side gate).
- Base copy: lines 1-657 of `wc.extended.yaml` are byte-identical to `blueprint/products/wc.yaml` (diff differs only by the trailing blank line before `extended_policies`).

### policy_conflict_scan

Extended policies (5) and what they write:

| Policy | subject / tool | computes | program scope |
| --- | --- | --- | --- |
| `wc_ext_program_day_hours` | `wc_visit_billed` / `record_program_day_6fda50ae` (agent) | units | Work Conditioning, Work Hardening |
| `wc_ext_program_day_charge` | `wc_charge_posted` charge_kind program_hours / `post_program_day_charge_5325d445` (agent) | amount | Work Conditioning, Work Hardening |
| `wc_ext_program_extension_days` | `wc_authorization_received`, `wc_auth_recorded` / `record_program_extension_8df51c57` (user) | visits | Work Conditioning, Work Hardening |
| `wc_ext_fce_authorization_hours` | `wc_authorization_received`, `wc_auth_recorded` / `record_fce_authorization_83d13911` (user) | hours | Functional Capacity Evaluation |
| `wc_ext_fce_missed_fee` | `wc_charge_posted` charge_kind fce_no_show / `post_fce_missed_fee_9edc6261` (agent) | amount | Functional Capacity Evaluation |

- Overlapping subjects: two policies write `wc_charge_posted` (program_hours vs fce_no_show charge kinds; disjoint programs) and two write `wc_authorization_received` (hour-billed programs vs FCE; disjoint programs). No two policies reach different conclusions on one situation.
- Shared quantity: both `wc_ext_program_day_hours` (re-test hours added to the day) and `wc_ext_program_day_charge` (re-test hours split out of the day) use the same condition ("at least twice the program's progress-report interval ... one where at least one interval but less than two ... none otherwise") with the same anchor (latest progress report, else the evaluation date of service). They are compatible: the hours policy adds them, the charge policy prices them, capped by the recorded hours.
- Triggers / time anchors: all evaluated on frozen_time; base time anchors (Form 63 window, suspension aging, payment lateness) are not touched by any extended policy.
- Terminal states: no extended policy changes status; all are history appends plus account moves (`wc_authorized_visits`, `wc_receivable`).
- Cross-category read boundary: every cross-category read is the `series` category (appointment series funded by the referral, `appointment_series.wc_case_id`), which is owned by the `appointment_booking_and_missed_visits` difficulty — a read, never a write.
- Scopes (derived blind from the two worlds, see task files): task 0 = {hours, charge, extension}; task 1 = {FCE authorization hours, FCE missed fee}. Pairwise disjoint; jointly cover all 5 extended policies.

### rule_compute_equivalence

Swept every compute binding against its `compute_basis` quotation and the rule, and every rule sentence back to a binding.

- `wc_ext_program_day_hours`: eval_date, eval_days, susp_days/prog_days (≤21 / 22-42 / else; "less seven"), phase_hours (<14 / <28 / else), missed_month/makeup (≥2 / ==1 / 0), last_report/report_days/retest (≥2× / ≥1× / 0, fallback to evaluation), late_minutes/late_hours (≥10 ceil; 1-9 round-half-up; 0), modified_cut (modified_duty ∧ ≥28 days → 1; modified_duty ∧ <28 → 2; else 0), result (order, floor 0, cap at max). All quoted and implemented; boundaries match ("no more than twenty-one" ↔ `<=21`, "under fourteen" ↔ `<14`, etc.). No empty promise.
- `wc_ext_program_day_charge`: day_hours (SUM of recorded units on the date of service), test_hours (MN with recorded hours), retest_age/test_rate (≥42 → 115; ≥21 → 96; else / no report → unit_rate), series_format/hour_rate (Specialty One-on-One 72; Extended 60-Minute 68; else unit_rate), cond_hours, cond_amount (≥6: 140 + (h−2)·rate; 3-5: min(300, h·rate); <3: h·rate), result (one rounding). Equivalent.
- `wc_ext_program_extension_days`: series_no_shows (XCOUNT series_no_show, last month), missed_reported, week_days (2 / 3 / visits_per_week_max), weeks_left, window_weeks, days_to_end/netted, update_days/transition_days, discharge_days, susp_days/reentry_days, result. Equivalent.
- `wc_ext_fce_authorization_hours`: injury_days, protocol_hours, hours_done/credit, order_days/rescreen (>120 / >90), missed_month/core_only, result. Equivalent for the computed quantity. **Observation O-G1**: the rule's last sentence "The authorization is recorded with the sessions of the protocol." and the protocol tiers' "in two sessions" / "in one session" have no compute binding and no `compute_basis` line; the `sessions` argument of `record_fce_authorization_83d13911` is therefore entailed by the rule alone (two-day protocol → 2, otherwise 1). It is uniquely readable, so no second answer is demonstrated; recorded as an observation (and it is load-bearing downstream: the missed-fee `auth_sessions` binding reads it).
- `wc_ext_fce_missed_fee`: auth_hours/auth_sessions (LATEST by auth_start_date), reserved_fee, notice/notice_share, reason/reason_share, missed_reports/missed_date/rebooked_on/rebook_gap/courtesy, result. **Observation O-G2**: the pro-rated branch of `reserved_fee` carries its own `RND(...,2)` while the rule says the fee is "rounded half up to the cent once, at the end". For the only program in scope (FCE: fee 250.00, max 4 hours) the pro-rated values for 0-2 hours are 0.00 / 62.50 / 125.00 — exact cents — so the extra rounding can never change a figure; no consequence demonstrable.
- Every declared factor's ladder tiers appear both in the rule prose and as branches of its `decides` binding, and every branch of each binding is a tier the rule states. No tier lives in only one face.

### action_binding_and_uuids

- `(target_tool, computes)` pairs are all distinct; each tool is claimed by exactly one policy.
- uuid8 suffixes: 6fda50ae, 5325d445, 8df51c57, 83d13911, 9edc6261 — five distinct values, no shared prefix or tail, no sequence; consistent with independent generation.
- Docstrings: no docstring states a position in a sequence or names another write tool; the ordering words found (`before it is passed`, `after this charge`, `first and last dates`) are intra-call. "as returned by the referral lookup" names the source of an id (a read), not a step order — not a defect.
- Tool bodies: none checks status, eligibility, authorization coverage or any prerequisite (module docstring and bodies confirm); each lands exactly what it is given.
- Owners: `record_program_extension_8df51c57` and `record_fce_authorization_83d13911` are `owner="user"` (the adjuster records in person); the other three are `owner="agent"`.

### prerequisite_graph

- `prerequisite` filled in on every extended policy: hours `[]`, charge → hours, extension → charge, FCE authorization `[]`, missed fee → FCE authorization.
- Every `problem` names another extended policy id of this file; none points at a base policy or itself. The graph (hours → charge → extension; FCE auth → fee) is acyclic.
- Each `policy_source` is verbatim in its own policy's `rule` (charge rule: "A program day's charge is fixed only after the referral carries the recorded program day for that date of service, with its program hours."; extension rule: "An extension is not recorded until the referral carries a program-hours charge for every program day the worker attended in the appointment series funded by the referral."; fee rule: "A missed-evaluation fee is not fixed until the referral carries an adjuster authorization whose dates cover the missed appointment.").
- All three edges declare `form: state` with no `fallback_reason` — correct pairing.
- `condition` restates each sentence at the same strength and scope (the charge: the recorded program-day entry for that date of service with its hours; the extension: every attended appointment of the funded series has a program-hours charge with the same date of service; the fee: an authorization whose first and last covered dates include the missed appointment's date).
- `resolved_by` is the depended-on policy's `target_tool` in each case; the tool effect really produces the gated state (a `wc_visit_billed` row for the date; a `wc_charge_posted` row with charge_kind program_hours for the date; a `wc_authorization_received` row with auth_start_date/auth_end_date).
- `kind`/`gate`: `value_input` → `day_hours` (a real binding of the charge compute); `state_gate` → `wc_events.charge_kind` (the gate the extension rule states); `value_input` → `reserved_fee` (a real binding of the fee compute). No authoring-viewpoint wording ("in this task", "at the opening") in any prerequisite field.

### prerequisite_sentences

Four-point test, per edge:

1. Charge ← hours. Connective "only after"; waited-on state "the referral carries the recorded program day for that date of service, with its program hours" — record-visible (`wc_events` row of the recorded program day with `units`), no action, no tool, no id; strength equals the condition. Exactly one write of this difficulty creates a recorded program day (`record_program_day_6fda50ae`, the only tool emitting `wc_visit_billed`). Derivation: the sentence + "no recorded program day for the date" in the history + the hours rule ("Every program day a worker attends ... is recorded on the referral against the adjuster authorization in force ...") → record the day first, with the hours the hours rule works out. One reading.
2. Extension ← charge. Connective "not until"; waited-on state "the referral carries a program-hours charge for every program day the worker attended in the appointment series funded by the referral" — record-visible (charge rows vs `series_visit_attended` rows), no action/tool/id. The only program-hours charge writer is `post_program_day_charge_5325d445` (`post_fce_missed_fee_9edc6261` writes charge_kind fce_no_show, which is not a program-hours charge). Derivation: compare attended dates in the funded series against program-hours charges → for each missing date, the charge rule bills that day ("Each recorded program day ... is billed ... on its date of service") → which itself waits on the recorded day (edge 1). One reading.
3. Fee ← FCE authorization. Connective "not until"; waited-on state "the referral carries an adjuster authorization whose dates cover the missed appointment" — record-visible. Two tools of the difficulty write `wc_authorization_received` (`record_program_extension_8df51c57`, `record_fce_authorization_83d13911`), but the extension policy and tool are confined to "an hour-billed program (Work Conditioning or Work Hardening)" while the missed-evaluation fee exists only on a Functional Capacity Evaluation referral, whose authorization the FCE policy records ("An adjuster authorizing a Functional Capacity Evaluation records the authorization in person ..."). On any referral the fee can reach, exactly one write brings the state about. One reading.

- No rule carries a second wording of its dependency, a tool name, or another policy id; the depended-on rules (hours, charge, FCE authorization) do not restate the blocked side's sentence.
- No extended rule states a cross-problem order that grounds no declared edge.
- **Observation O-G3 (base ordering sentence)**: base `wc_authorization` says "An extension is requested once remaining visits fall to auth_renewal_trigger_visits or fewer and no later than auth_extension_lead_days calendar days before the authorization end date". It is a base sentence with an ordering connective whose first clause a program-day record (which draws one authorized day) can bring about. No task tree rests on it (the extension's own prerequisite sentence carries the dependency, and the recorded day precedes the extension transitively), so per check 6 it is an observation, not a red.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry:

- `wc_ext_program_day_hours` (refs `wc_agg_claim_frequency`, `wc_authorization`; `overwrite: []`): it follows the weekly-frequency cap and one-referral-per-date sentence (no quantity changed), and the billable-status / authorization-coverage sentences ("drawing one authorized program day, while the referral is in referral_received or active status"). Neither base policy governs the recorded hours, so no override is needed. **Observation O-G4**: the base sentence that bounded hour-billed units "between program_hours_per_day_min and program_hours_per_day_max" lives in `wc_evt_charges` and is superseded by the charge policy's declared overwrite; the hours policy itself floors at zero, not at the program minimum, without citing `wc_evt_charges`. No task world reaches below the minimum (task 0 records 7 of a 4-8 band), so no consequence is demonstrable.
- `wc_ext_program_day_charge` (refs `wc_evt_charges`, `wc_employer_direct`): the replaced sentence ("each later date of service is billed as unit_rate times the billing units, with units counted in billing_unit and capped at max_billable_units_per_day (and, for hour-billed programs, between program_hours_per_day_min and program_hours_per_day_max).") is named verbatim in `overwrite` and replaced by a rule sentence; "Charges follow fee_basis", the carrier-as-payer sentence, the worker-never-billed sentence and the submission-deadline sentence are followed ("submitted that day and so within the program's bill submission deadline"). `wc_employer_direct` does not reach hour-billed programs. Declared; merged semantics unique.
- `wc_ext_program_extension_days` (ref `wc_authorization`; `overwrite: []`): follows "The referral's authorization reference, end date and weekly frequency follow the newest authorization received" and the extension-timing sentence; base fixes no number of days to request. No override.
- `wc_ext_fce_authorization_hours` (ref `wc_authorization`; `overwrite: []`): same; base fixes no number of evaluation hours. No override.
- `wc_ext_fce_missed_fee` (refs `wc_evt_charges`, `wc_employer_direct`): the replaced sentence ("A missed Functional Capacity Evaluation is billed to the carrier at fce_no_show_fee only where fce_no_show_billable_to_carrier is true.") is named verbatim; the base formula branch `fce_no_show_fee if charge_kind == "fce_no_show"` falls with it. `wc_reporting`'s "no fee is charged to the worker while injured_worker_missed_fee_billable is false" is respected (the payer is the carrier). Declared; merged semantics unique.
- No anonymous intermediate factor, 0/1 multiplier or dropped branch found against any base sentence.

### factor_ladders

| Policy | Factor | Label | Tiers (distinct?) | Multi-source | Cross-difficulty |
| --- | --- | --- | --- | --- | --- |
| hours | progression_clock | method | 3 anchors (since suspension; since evaluation − 7; since evaluation) — distinct | no | — |
| hours | graded_phase | parameter | min / 6 / max — see F-G3 | no | — |
| hours | makeup_hours | parameter | 2 / 1 / 0 | no | — |
| hours | retest_hours | parameter | 2 / 1 / 0 | no | — |
| hours | late_arrival | method | ceil / round-nearest / none — **tier 2 ≡ tier 3, see F-G1** | no | series |
| hours | modified_duty_shortening | parameter | 1 / 2 / 0 | yes (work status ∧ evaluation date) | — |
| charge | retest_split | parameter | 2 / 1 / 0 (capped by hours) | no | — |
| charge | retest_rate | parameter | 115 / 96 / unit_rate | no | — |
| charge | conditioning_rate | parameter | 72 / 68 / unit_rate | no | series |
| charge | day_length_pricing | method | block / capped per-hour / per-hour — distinct (O-G5) | no | — |
| extension | requested_frequency | parameter | 2 / 3 / visits_per_week_max | yes (series no-shows ∧ reported misses) | series |
| extension | request_window | method | weeks remaining ≥1 / interval weeks ≥1 / 2 — **collapses, see F-G2** | yes on tier 2 (weeks left ∧ report age) | — |
| extension | unused_day_netting | method | min(unused, days left) / none / all unused — distinct | no | — |
| extension | transition_days | parameter | 2 / 1 / 0 | yes (work status ∧ update date) | — |
| extension | discharge_retest_days | parameter | 1 / 2 / 0 (O-G6) | yes (weeks left ∧ FCE on file) | — |
| extension | reentry_reduction | parameter | 2 / 1 / 0 | no | — |
| FCE auth | evaluation_protocol | method | 1.5×max (2 sessions) / max − 1 / max — **numbers, see F-G4** | yes (work status ∧ injury date; work status ∧ job description) | — |
| FCE auth | partial_attempt_credit | parameter | 2 / 1 / 0 | no | — |
| FCE auth | order_rescreen | parameter | 2 / 1 / 0 | no | — |
| FCE auth | core_only_reduction | parameter | 2 / 1 / 0 | no | — |
| fee | reserved_time | method | per session / pro-rated / once — distinct | no | — |
| fee | notice_share | parameter | 0 / 0.5 / 1 | no | series |
| fee | reason_share | parameter | 0 / 0.8 / 1 | no | series |
| fee | first_miss_courtesy | parameter | 50 / 25 / 0 | yes (reported misses ∧ series rebooking date) | series |

- Declared counts: hours 6 (4 parameter, 2 method); charge 4 (3 / 1); extension 6 (5 / 1 per labels, request_window being method); FCE auth 4 (3 / 1); fee 4 (3 / 1). All within 4-6 as declared.
- Every factor's `decides` is an input binding (never `result`); binding sets within each policy are disjoint; every ladder has three tiers stated in full in the rule prose and implemented in compute; every fall-through equals that factor's `baseline`, and every policy `baseline.rule` is a sentence of its rule from which a definite number follows (hours: the program's maximum daily hours; charge: unit_rate × recorded hours; extension: visits_per_week_max × 2 − unused; FCE: max daily billable hours in one session; fee: the missed-evaluation fee once).
- Cross-difficulty reads: only `series` (difficulty `appointment_booking_and_missed_visits`). Field names used exist in `db_schema.json` (`series_events.minutes_late`, `notice_hours`, `cancel_reason` enum incl. transportation/weather/patient_illness/family_emergency, `appointment_series.variant_name` incl. "Specialty One-on-One Visit Series", "Extended 60-Minute Visit Series").
- Struck by the tests (charter-global): `late_arrival` (F-G1) and `request_window` (F-G2), `evaluation_protocol` (F-G4) as a `method`. After striking: hours 5 factors (4 parameter, 1 method) — within bounds; extension 5 (5 parameter, 1 method = unused_day_netting) — within bounds; FCE authorization 3 surviving honest factors and **0 method** — below both floors (see F-G4).

### findings

**F-G1 — SOURCE-FACTOR RED (unreal ladder) — `wc_ext_program_day_hours` / factor `late_arrival`. Bears on: task 0.**
- Symptom: the middle tier and the fall-through select the same value for every input the middle tier admits.
- Root cause: the rule sentence "where one to nine minutes late, the late minutes are rounded to the nearest whole hour, half an hour rounding up; where on time, no hours are lost." Rounding 1-9 minutes to the nearest whole hour is always 0 hours.
- Evidence: rule (`wc.extended.yaml` line 701-702); compute `late_hours: "... ((int(late_minutes) + 30) // 60 if int(late_minutes) >= 1 else 0)"`; for m = 1..9, (m+30)//60 = 0 (checked exhaustively), identical to the fall-through's 0.
- Demonstrated consequence: the ladder has only two distinct outcomes (ceil to whole hours for ≥10 minutes; 0 otherwise), below the three-tier floor; a reader who ignores the 1-9-minute tier entirely always scores the same. The factor is struck from the count (hours keeps 5 factors, 1 method — bounds still hold).
- Affected artifact: `wc.extended.yaml` → `wc_ext_program_day_hours.rule` (late-arrival sentence), `.compute.late_hours`, `.factors[late_arrival].ladder[1]`.

**F-G2 — SOURCE-FACTOR RED (unreal ladder / mislabelled effect) — `wc_ext_program_extension_days` / factor `request_window`. Bears on: task 0.**
- Symptom: in each program the policy reaches, two of the three tiers select the same window; every tier evaluates to a constant.
- Root cause: tier 1 "the whole weeks remaining ..., at least one week, where fewer than two whole weeks remain" can only be max(1, w) with w ≤ 1, i.e. always 1 week; tier 2 "one progress-report interval in whole weeks, at least one" is 7//7 = 1 for Work Hardening (progress_report_interval_days 7) and 14//7 = 2 for Work Conditioning (14); the fall-through is 2.
- Evidence: rule lines 1049-1053; compute `window_weeks`; variant parameters (Work Hardening progress_report_interval_days 7, Work Conditioning 14) at `wc.extended.yaml` lines 134, 147.
- Demonstrated consequence: Work Hardening — tier 1 = tier 2 = 1 week; Work Conditioning — tier 2 = fall-through = 2 weeks. No program has three distinct outcomes; and since each tier is a fixed number per program, the `method` label is not honest (the charter labels the structurally identical `graded_phase` ladder — program parameter / constant / program parameter — as `parameter`). Struck from the count (extension keeps 5 factors with `unused_day_netting` as its one method — bounds hold).
- Affected artifact: `wc_ext_program_extension_days.rule` (request-window sentence), `.compute.window_weeks`, `.factors[request_window]`.

**F-G3 — SOURCE-FACTOR RED (unreal tier value, latent) — `wc_ext_program_day_hours` / factor `graded_phase`. Bears on: no task of this bundle (both tasks avoid it: task 0 is Work Hardening, task 1 is FCE).**
- Symptom: the middle phase is a fixed "six hours" for both hour-billed programs; for Work Conditioning (program_hours_per_day_min 2, program_hours_per_day_max 4) the mid phase exceeds the program's own daily maximum and the late phase (4).
- Evidence: rule "from fourteen to twenty-seven days they are six hours, and from twenty-eight days on they are the program's maximum daily program hours"; Work Conditioning parameters at line 131-133 (`program_hours_per_day_min: 2, program_hours_per_day_max: 4`).
- Demonstrated consequence: for a Work Conditioning worker on progression day 14-27, the published graded phase (6 h) is above the program's daily maximum and higher than the phase that follows — a graded progression no Work Conditioning program publishes; the final cap then silently reduces it. No task's score is moved here.
- Affected artifact: `wc_ext_program_day_hours.params.mid_phase_hours` / rule graded-phase sentence.

**F-G4 — SOURCE-FACTOR RED (mislabelled effect; method floor not met) — `wc_ext_fce_authorization_hours` / factor `evaluation_protocol`. Bears on: task 1.**
- Symptom: the computation's only `method` factor selects a number, not an algorithm.
- Root cause: the policy reaches only Functional Capacity Evaluation referrals, whose `max_billable_units_per_day` is fixed at 4 (line 158); the three protocol tiers therefore always evaluate to 6, 3 and 4 hours. Each tier substitutes a different number for `protocol_hours` into the same formula `protocol_hours + rescreen − credit − core_only`. The charter's own `graded_phase` ladder, of the same shape (program parameter / constant / program parameter), is labelled `parameter`.
- Demonstrated consequence: counting honestly, the FCE-authorization computation has 0 `method` factors (floor 1). The session count attached to the protocol (2 vs 1) is a second output of the same tier choice, not a different way of computing the hours. (Counter-reading recorded: the protocols are clinically different evaluation formats; this does not change that, for the scored hours, the tiers are three constants.)
- Affected artifact: `wc_ext_fce_authorization_hours.factors[evaluation_protocol].effect`, its rule protocol sentence.

**O-G1 … O-G6 — observations** (no demonstrable consequence):
- O-G1 sessions of the FCE authorization stated in the rule without a compute binding (see rule_compute_equivalence).
- O-G2 double rounding in the pro-rated reserved-time branch, a no-op for the FCE figures.
- O-G3 base `wc_authorization` extension-timing sentence carries an ordering connective; no tree rests on it.
- O-G4 the hours policy floors at zero, not at the program minimum.
- O-G5 `day_length_pricing`: tiers 2 and 3 differ only through the $300 cap, which on tier 2 binds only at 5 conditioning hours (5 × 64/68/72 > 300); the tiers are nevertheless distinct methods.
- O-G6 `discharge_retest_days`: for Work Hardening a completed FCE is an entry requirement (`entry_requires_fce_baseline: true`), so the "no completed FCE on file" tier is unreachable on an active Work Hardening referral; it remains reachable for Work Conditioning, so the condition does not hold of every customer reaching this write.
- O-G7 `evaluation_protocol` tier 2 "the employer's job description is on file" holds of every activated FCE referral (`entry_requires_job_description: true`); it is not universal only because an authorization can be recorded on a referral still in referral_received.

## closing_checklist

Written after both reveals (about 2026-10-05 05:23Z); everything above this heading was frozen at 05:21:05Z before any reveal and is untouched.

- Per-task files: `0.md`, `1.md` correspond one-to-one with tasks 0 and 1; this is the first audit (no older revision). Both comparison sections are on file. **Not every comparison carries PASS on all four relationships**, so the difficulty does **not** close the source-layer audit:
  - task 0: policy PASS / chain PASS / **SOURCE-FACTOR RED** (F-G1 late_arrival, F-G2 request_window; plus a false near-miss assertion in design_rationale, T0-F3) / unique solution PASS.
  - task 1: policy PASS / chain PASS / **SOURCE-FACTOR RED** (F-G4 evaluation_protocol mislabel → no honest method factor in the FCE-authorization computation) / unique solution PASS.
  - charter-global, no task affected: F-G3 (graded_phase mid value 6 h above the Work Conditioning daily maximum).
- Coverage and scopes: task 0 charter_scope {hours, charge, extension}, task 1 {FCE authorization hours, FCE missed fee} — equal to the blind-derived trees, pairwise disjoint, together all 5 extended policies; task tools closed (5 tools, each used by exactly one task); uuid8s independent (see action_binding_and_uuids).
- Problem trees: task 0 — 2 prerequisite problems, 1 value_input edge, user write (extension); task 1 — 1 prerequisite problem, 1 value_input edge, user write (FCE authorization); the difficulty-wide graph (hours → charge → extension; FCE authorization → fee) is acyclic with no cross-task references.
- Computations: every declared baseline is self-sufficient and gives a definite number different from gold (8 vs 7; 448.00 vs 508.00; 7 vs 3; 4 vs 5; 250.00 vs 150.00); every factor bears weight on its task's world (all figures match GT `factor_sensitivity`); per task at least one multi-source and one cross-difficulty (series) factor. Ladder realism/labelling fails on F-G1, F-G2, F-G4 (and latent F-G3).
- Instantiation-stage gates: not re-run by this auditor (the skill takes them from the brief); the brief's snapshot is all green with check_traceability deferred to the KB stage. No artifact was edited, so the snapshot still describes the final form.

## revision_2

### charter_global_frozen (revision 2)

- Auditor: the same independent auditor as round 1; unattended. Written 2026-10-05 ~06:31Z, before any round-2 task file was revealed; contains nothing derived from a revealed GT.
- Inputs: `/tmp/erl0032_views/workers_comp_referrals_and_billing_r2/` — `wc.extended.yaml` ddf643c8cf29faba5836b2bac2bb0458fe27e82141005694304c100663a12bc8 (changed from round 1's 558b3e06…, so every charter-global section is re-derived), `task_tools.py` c39f615eaf81cf92a650bdff43838a5eec3d3a678d8982b6aecab467d28889be (unchanged; action_binding_and_uuids carried forward on that hash). Both match the source files under `tasks/workers_comp_referrals_and_billing/`. The base section (lines 1-657) is still byte-identical to `blueprint/products/wc.yaml`.
- Masked until both round-2 task derivations are frozen: the same fields as round 1, in `tasks/0.json` (cb3aa24c…) and `tasks/1.json` (30f0a9b7…).
- Text diff against round 1 (complete): `wc_ext_program_day_hours` (new overwrite of `wc_evt_charges`; graded mid phase now the midpoint of min and max; `late_arrival` removed and `reconditioning_cut` added; cross_category now []); `wc_ext_program_extension_days` (request-window ladder rewritten; label now `parameter`); `wc_ext_fce_authorization_hours` (protocol tier 2 condition; sessions now a compute binding; partial-attempt credit rewritten as a `method`; protocol label now `parameter`); `wc_ext_fce_missed_fee` (inner rounding removed from `reserved_fee`). `wc_ext_program_day_charge` and every `prerequisite` block are byte-identical.

### policy_conflict_scan (revision 2)

- Subjects, tools, programs and charge kinds are as in round 1. No overlap gives two conclusions on one situation.
- New: two extended policies now name the same base clause in `overwrite` (`wc_evt_charges` "each later date of service is billed as unit_rate times the billing units … between program_hours_per_day_min and program_hours_per_day_max."). The charge policy replaces it with the billing sentence (billed on the hours recorded for the date). The hours policy replaces it with the recording bound (never below zero, never above the maximum; a day under the minimum is recorded at the hours worked out). These are two halves of the same clause, on two different subjects (`wc_charge_posted` amount vs `wc_visit_billed` units). They compose to one semantics: a day may be recorded and billed below the program minimum. No contradiction.
- Scopes (derived blind; see the task files): task 0 = {hours, charge, extension}; task 1 = {FCE authorization, FCE missed fee}. Disjoint and complete.

### rule_compute_equivalence (revision 2)

- hours: `phase_hours` middle branch `(min + max) // 2` ↔ "the midpoint of the program's minimum and maximum daily program hours, rounded down to a whole hour". `last_day` ↔ the `wc_visit_billed` row with visits = 1, i.e. a recorded program day; the evaluation row carries visits 0 and is not a program day, matching "the worker's latest program day already recorded on the referral". `gap_days` falls back to the evaluation date ("or since the initial evaluation where none is recorded"). `gap_cut` (≥8 → 2; ≥4 → 1; else 0) ↔ "eight or more … four to seven … none otherwise". `result` order and bounds match the rule. The new clause "a day that works out below the program's minimum … recorded at the hours worked out" is what `MX(0, …)` with no minimum floor implements. Equivalent; no empty promise.
- extension: `window_weeks` = 1 if fewer than 2 whole weeks remain; else 3 if (≥2 weeks ∧ no missed program day reported in the last month ∧ latest progress report ≤ one interval old); else 2. Each branch has its quoted rule sentence. Equivalent. (The `weeks_left >= 2` test in branch 2 is redundant with branch 1 and harmless.) Report age where no progress report exists: "the latest progress report was sent … no more than one progress-report interval before the request" has no stated fallback, while compute uses days since the evaluation. On a referral with no progress report and two or more weeks left, a reader could take tier 2 as unmet. No task world reaches this (task 0 has a progress report), so it is **observation O2-G1**.
- FCE authorization: `protocol_hours` tier 2 is now "modified duty ∧ more than 120 days since injury" in rule and compute. `protocol_sessions` (protocol hours above max → 2, else 1) ↔ "two for a two-day protocol and one for any other protocol"; only the two-day protocol exceeds the maximum (6 > 4, while 3 and 4 do not). **O-G1 closed.** `last_attempt`/`attempt_age`/`credit_hours` (≤7 → all recorded hours; ≤30 → half, rounded down; else 0) ↔ rule. Equivalent.
- fee: `reserved_fee` pro-rated branch is now unrounded, and the single `RND` sits at the end, matching "rounded half up to the cent once, at the end". **O-G2 closed.**
- charge: unchanged, equivalence carried from round 1 (identical text).

### action_binding_and_uuids (revision 2)

Carried forward unchanged: the `task_tools.py` hash is identical, and each policy's `target_tool`/`computes` pair is unchanged in the diff.

### prerequisite_graph / prerequisite_sentences (revision 2)

All three `prerequisite` blocks are byte-identical. Each `policy_source` is still verbatim in its own rule:
- the charge rule is unchanged;
- the extension rule's "An extension is not recorded until …" is untouched;
- the fee rule's "A missed-evaluation fee is not fixed until …" is untouched.

The `day_hours` and `reserved_fee` bindings still exist. No rewritten rule (hours, extension, FCE) adds a cross-problem order, a tool name or another policy's id. The hours rule's new "latest program day already recorded" reads the policy's own history and is not an order on another problem's write. The round-1 conclusions of both sections therefore stand, and O-G3 stands.

### override_declarations (revision 2)

- hours: `wc_evt_charges` is now in `base_policy_refs`, and its units-bound clause is declared in `overwrite`, verbatim, with a replacement that is a sentence of the rule. **O-G4 closed.** The other base sentences (`wc_agg_claim_frequency`, `wc_authorization`) are followed as in round 1.
- extension and FCE authorization: `overwrite: []` remains correct. Base fixes no number of days, hours or sessions to request.
- charge and fee: as in round 1.

### factor_ladders (revision 2)

| Policy | Factor | Label | Tiers (outcomes) | Distinct? | Multi-source | Cross-difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| hours | progression_clock | method | three anchors | yes | no | — |
| hours | graded_phase | parameter | min / ⌊(min+max)/2⌋ / max → WH 4/6/8, WC 2/3/4 | yes, monotone in both programs | no | — |
| hours | makeup_hours | parameter | 2/1/0 | yes | no | — |
| hours | retest_hours | parameter | 2/1/0 | yes | no | — |
| hours | reconditioning_cut | parameter | 2/1/0 | yes | no | — |
| hours | modified_duty_shortening | parameter | 1/2/0 | yes | yes | — |
| charge | (unchanged: retest_split, retest_rate, conditioning_rate, day_length_pricing) | 3 p / 1 m | as round 1 | yes | — | series (conditioning_rate) |
| extension | requested_frequency | parameter | 2/3/max | yes | yes | series |
| extension | request_window | parameter | 1 / 3 / 2 weeks | yes | yes (tier 2: weeks left ∧ reported misses ∧ report age) | — |
| extension | unused_day_netting | method | min / none / all | yes | no | — |
| extension | transition_days, discharge_retest_days, reentry_reduction | parameter | as round 1 | yes | as round 1 | — |
| FCE auth | evaluation_protocol | parameter | 6 / 3 / 4 h (FCE max 4) | yes | yes (work status ∧ injury age) | — |
| FCE auth | partial_attempt_credit | method | all recorded hours / half rounded down / none | yes as functions (see O2-G2) | yes (recorded hours ∧ latest day's age) | — |
| FCE auth | order_rescreen, core_only_reduction | parameter | 2/1/0 | yes | no | — |
| fee | (unchanged: reserved_time m; notice_share, reason_share, first_miss_courtesy p) | | | yes | courtesy | series |

Counts per computation:

| Computation | Factors | Parameter | Method |
| --- | --- | --- | --- |
| hours | 6 | 5 | 1 |
| charge | 4 | 3 | 1 |
| extension | 6 | 5 | 1 |
| FCE authorization | 4 | 3 | 1 |
| fee | 4 | 3 | 1 |

All are within the bounds.

Status of the round-1 findings:
- **F-G1 closed.** `late_arrival` is gone, and its replacement `reconditioning_cut` has three distinct values (2/1/0).
- **F-G2 closed.** The window ladder now selects 1 / 3 / 2 weeks in every program. It is labelled `parameter`, and its outcomes are numbers, so the label is honest.
- **F-G3 closed.** The middle phase is the midpoint (WC 3, WH 6), between min and max in both programs.
- **F-G4 closed.** `evaluation_protocol` is now labelled `parameter`. The FCE computation's method is `partial_attempt_credit`, whose tiers are different functions of the recorded hours (identity, halving, zero): a change of algorithm, not a substituted constant. Realism: crediting a very recent partial attempt in full, an older one by half, and retesting a stale one in full is a recognisable FCE practice.

Observations:
- **O-G7 closed.** Tier 2 no longer rests on the job description, which is an FCE entry requirement.
- **O-G5 kept** (author's reason accepted: the tiers are distinct methods).
- **O-G6 kept**, unchanged (the "no completed FCE on file" tier is unreachable for Work Hardening).
- **New O2-G2.** For `partial_attempt_credit`, tier 2 (half, rounded down) and the fall-through (none) give the same 0 when at most one hour is recorded. That part of the domain is not the whole tier: from 2 recorded hours they differ (1 vs 0). This is not the F-G1 shape, where a tier could never differ. It matters only for a world with 8-30 days and 1 recorded hour.

### findings (revision 2)

- No new charter-global SOURCE-POLICY / SOURCE-FACTOR red. F-G1, F-G2, F-G3 and F-G4 are closed as stated above.
- Observations: O2-G1 (no fallback anchor for report age in the window tier 2), O2-G2 (credit tier 2 vs fall-through at one recorded hour); O-G3, O-G5, O-G6 stand.

### closing_checklist (revision 2)

- Written after both round-2 reveals (06:32:29Z). Everything above in revision_2 was on disk before that time:
  - `_difficulty.md` at 06:31:26Z;
  - `0.md` at 06:31:59Z;
  - `1.md` at 06:32:24Z.
- Round-1 text is untouched.
- Per-task files `0.md` and `1.md` each carry a revision_2 with a frozen derivation and a comparison. Both comparisons carry PASS on all four relationships:
  - task 0: PASS / PASS / PASS / PASS;
  - task 1: PASS / PASS / PASS / PASS.
- Round-1 REDs: F-G1/T0-F1, F-G2/T0-F2, F-G3, F-G4/T1-F1 and T0-F3 are all closed.
- Observations closed: O-G1, O-G2, O-G4, O-G7, O-T1-1.
- Observations narrowed: O-T0-2, O-T0-3.
- Observations kept (reasons accepted): O-G3/O-T0-1, O-G5, O-G6, O-T1-2.
- New observations: O2-G1 and O2-G2.
- There are no new red findings and no regressions.
- Coverage and scope:
  - 5 extended policies are covered exactly once by the two task scopes (task 0: hours, charge, extension; task 1: FCE authorization, fee).
  - The scopes are disjoint and each spans its whole tree.
  - The tools are closed. The uuid8s are independent; the tool module is unchanged.
- Problem trees:
  - task 0: 2 prerequisite problems, 1 value_input edge, a user write.
  - task 1: 1 prerequisite problem, 1 value_input edge, a user write.
  - The graph across the difficulty is acyclic, with no cross-task references.
- Computations:
  - Every baseline is self-sufficient and gives a definite number different from gold: 8 vs 7; 448.00 vs 508.00; 6 vs 3; 4 vs 5; 250.00 vs 150.00.
  - Each computation has 4-6 factors, with at least 2 parameter and 1 method.
  - Each task has multi-source and cross-difficulty (series) factors.
  - Every ladder has three distinct outcomes that this line of business would use.
  - Every factor bears weight on its task's world, and every figure matches GT `factor_sensitivity`.
- Gates: the orchestrator's post-rework snapshot is green (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE). Traceability is deferred to post-render. This auditor did not re-run the gates.
- **The difficulty passes the source-layer audit in revision 2.**
