# Policy-task audit — benefit_and_tax_appeals / charter-global

## charter_global_frozen

- Scenario: `env/env_0049_state_unemployment_insurance_agency`; difficulty `benefit_and_tax_appeals`; category `appeal`; M=2.
- Freeze hashes (sha256, verified by the auditor at the start of the audit, equal to the coordinator's brief):
  - `tasks/benefit_and_tax_appeals/appeal.extended.yaml` = `2e1765294071c99f7b861eb538ffaabbae0e3d9c99376857aeec24a722fbe6b4`
  - `tasks/benefit_and_tax_appeals/task_tools.py` = `2a572cdc28b01e7fab36defea7f80ccb05e927df6e3105e77c411b698ce2bab6`
- Freeze time: 2026-10-09T04:15Z (written before any task's GT was revealed). Auditor: erl-task-policy-audit agent, independent of the instantiator (no instantiator transcript, no `worklog.md` read).
- Fields permitted for this section: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/appeal.yaml` (and the claim/taxacct product charters, read only to judge the cross-difficulty evidence), the extended charter, `task_tools.py`, and the expression semantics in `~/.claude-sub/skills/erl-task-instantiate/scripts/check_compute.py` (`build_env`, `eval_compute`).
- Fields masked for this section: every task's `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`; `worklog.md`. Nothing in this charter-global section is derived from a revealed GT.

### entry_conditions (Step 0)

- Gate snapshot supplied with the brief: check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all rc=0; check_cache_diff informational; check_traceability deferred to the render stage (KB not published) and validate_scenario reporting only pre-render "required document not found" errors. Accepted as the entry qualification; the deferred traceability check is a stage-ordering fact, not missing input.
- Masked views supplied with hashes; the auditor re-hashed `/tmp/coord0049/views/benefit_and_tax_appeals/task_0.blind.json` (`35f23338fab529b2ee91c36a2551019b98df1e18225658e5c67afc1080d9313f`) and `task_1.blind.json` (`c5aa4779d5a0c6162156e471d806a32451c0bedc0da362d45354b5320fb88c36`), and the sources `tasks/0.json` (`f1bc0a54be1ad978ce5c8b3c4c0c36656201d5516f60833897115ab982e4a7e7`) and `tasks/1.json` (`7fe63f024c27808d745c10315e18e747b87d586511be657c41de025eb513bb4d`) — all equal to the brief. Each view holds exactly `frozen_time`, `user_scenario`, `initial_state`.
- Base copy: the base section of `appeal.extended.yaml` (lines 1–1240) parses to an object equal, key by key (`category … policies`), to `blueprint/products/appeal.yaml`; the only extra key is `extended_policies`. Base copy is verbatim-compatible.

### policy_conflict_scan

Extended policies (4): `appeal_ext_first_hearing_setting` (agent, `docket_appeal_hearing_a28520da`, computes `notice_period_days`), `appeal_ext_video_session` (user, `book_video_hearing_session_16bf8e4f`, `session_days`), `appeal_ext_reopened_hearing_setting` (agent, `reopen_dismissed_appeal_6a7f532d`, `notice_period_days`), `appeal_ext_in_person_session` (user, `book_in_person_hearing_session_05d44a0a`, `session_days`).

| Subject / boundary | Finding |
| --- | --- |
| Overlapping subjects among extended policies | All four write `appeal_hearing_scheduled`; they are separated by the appeal's state at the write (first setting on a filed appeal / reopening setting on a dismissed appeal / party-requested reset of a set hearing in video or in-person mode). Between extended policies: compatible. |
| Overlap with base `appeal_evt_postponement` | **Conflict (finding G1).** Video and in-person rules call their write "a reset of the hearing made at that party's request", and both tools record `schedule_reason="postponement"`, `requested_by=<appellant_role>`, `request_date=today` (task_tools.py L103–107, L190–194). In the base vocabulary a party-requested reset is a postponement: base event `appeal_hearing_scheduled` "(first setting, reset after postponement, or setting after reopening)", trigger `appeal_postponement_decided → appeal_hearing_scheduled {schedule_reason: postponement}`; base rule "A granted postponement resets the hearing within the reschedule window, with a new notice that again meets the notice minimum days." plus the per-party maximum and the lead-time gate. Neither extended policy cites `appeal_evt_postponement` in `base_policy_refs` nor names any of its sentences in `overwrite`. |
| Overlap with base `appeal_agg_linked_dockets` consolidation | "Appeals of the same parties that arise from the same facts … are heard together on one hearing date where the dockets allow consolidation" — none of the four per-appeal date computations says how a consolidated pair's dates are reconciled. Latent; no audited world seeds a linked appeal (observation O2). |
| Triggers / eligibility | First setting: base status gate `hearing_on_open_appeal` (filed/scheduled/dismissed) inherited; reopened: base `reopening_window` (15 days after dismissal mailing, good cause) inherited by "grants an appellant's timely reopening request". No extended eligibility weakens a base gate. |
| Time anchors | All four computations count calendar days from today (the notice mailing date); the weekend/weekday roll is anchored by `DAYS('2026-01-05', NOW)` (2026-01-05 is a Monday; 0=Mon … 6=Sun) — correct. |
| Terminal states | First setting: filed→scheduled; reopened: dismissed→scheduled + request granted; video/in-person: hearing_date moved, status unchanged. Consistent with the base lifecycle. |
| Cross-category read boundaries | first setting reads `claim` (ledger, certifications, program); video reads `idv`; reopened reads `taxacct` (ledger, wage reports); in-person reads `taxacct` (wage reports, account). All X-reads are scoped by the engine to the appellant (`_cross`/`_xrows` filter `customer_id = CUST`). |
| Scope exclusivity of the M tasks | Two prerequisite trees exist in the graph: {video ← first setting} and {in-person ← reopened}. Two disjoint scopes that together cover all four extended policies (the per-task files confirm which tree each task's world instantiates). |

### rule_compute_equivalence

Every `compute_basis` quotation was checked programmatically to be a verbatim sentence of its policy's `rule`; every `baseline.rule` sentence is a verbatim `rule` sentence; every `factors[].ladder` tier is a sentence-level clause of the rule and a branch of the `decides` binding (and conversely). Rule sentences not quoted in `compute_basis` are only the procedural sentences (mode, who books, the prerequisite sentence) and the baseline sentences whose content is carried by the factor's `baseline` binding.

Per policy, the quantities and their implementation:

- **first setting**: clock (late reason ≠ none → today; mail → filed + `mail_receipt_days`; else filed) = `first_clock_offset`; target (claimant ∧ no `claim_benefit_paid` in `within_months=2` ∧ certified ≥ 3 → 14; claimant ∧ no payment ∧ < 3 → 21; else `P(scheduling_target_days)`); leads (latest interpreter language ASL 10 / other non-Spanish 7 / 0; open `received` subpoenas ≥2 10 / 1 7 / 0; claim program UCFE 10 / UCX 7 / 0); `MX(notice_min, clock+target+leads)`; Sat→+2, Sun→+1. The "two months" window ("later than the same day of the month two months before today, up to and including today") equals the engine's `0 <= MONTHS(d, NOW) < 2`. Equivalent.
- **video**: `DAYS(NOW, hearing_date)` + block gap (non-Spanish ∧ hearing ≥ 60 → 10; non-Spanish ∧ < 60 → 7; else 5) + accommodation (ASL ∧ medical ≥1 → 5; medical ≥1 ∧ not ASL → 3; else 0) + identity (case status ≠ verified → 6; verified ∧ pathway ≠ Video Trusted Referee → 3; else 0) + appellant exhibits (≥2 → 5; 1 → 3; 0) then docket weekday roll (Sep/A&A → Tue/Thu; Overpayment → Wed; else weekend→Mon). Equivalent **except** the identity read (finding G4).
- **reopened**: clock (latest reopening reason illness ∧ medical exhibit → latest medical exhibit date; did_not_receive_notice → today; else latest reopening request date); window (employer ∧ payments ≥ 2500 in 3 months ∧ latest report on time → 14; … ∧ late → 17; else `P(reschedule_window_days)`); late exhibits (≥2 → 7; 1 → 4; 0); interpreter (ASL 10 / non-Spanish 7 / 0); granted subpoenas (≥2 → 10; 1 → 7; 0); `MX(notice_min, …)`; weekend roll. Equivalent.
- **in-person**: `DAYS(NOW, hearing_date)` + room block (appellant exhibits ≥ 3 ∧ hearing ≥ 60 → 8; ≥ 3 ∧ < 60 → 6; else 4) + on-site interpreter (ASL 5 / non-Spanish 3 / 0) + witness (granted subpoenas ≥2 → 4; 1 → 2; 0) + large room (latest report month-3 employees ≥ 100 ∧ granted subpoena ≥1 → 5; ≥100 ∧ none → 2; else 0) + tax calendar (reserve ratio < −0.04 ∧ rate ≥ 0.06 → 5; ratio < 0 ∧ rate < 0.06 → 2; else 0), then docket weekday roll (rate/charge → Wed; Sep/A&A → Tue/Thu; else weekend→Mon). `XLATEST(...employee_count_month3, date_field='quarter')` carries no account filter but is customer-scoped by the engine, matching "the appellant's latest quarterly report". Equivalent.

Wording-level ambiguities recorded as observations (O7): first-setting "weekly benefit payment" vs the compute's count of every `claim_benefit_paid` row (weekly, supplemental, reissue); reopened "contribution payments" vs the compute's sum of every `taxacct_payment_received` row regardless of `component`, and excluding `taxacct_voluntary_contribution_paid`.

### action_binding_and_uuids

- `(target_tool, computes)` pairs are unique: (`docket_appeal_hearing_a28520da`, notice_period_days), (`book_video_hearing_session_16bf8e4f`, session_days), (`reopen_dismissed_appeal_6a7f532d`, notice_period_days), (`book_in_person_hearing_session_05d44a0a`, session_days). Each tool is claimed by exactly one policy.
- uuid8 tails `a28520da`, `16bf8e4f`, `6a7f532d`, `05d44a0a`: pairwise distinct, no shared prefix, no sequence pattern; read as independently generated.
- Tool bodies: each is one atomic write (create one `appeal_events` row + update `appeals`; reopen also updates the request to `granted`). None reads status, hearing date, ownership or timing; none refuses or hints — **the tool layer judges no prerequisite**.
- Docstrings: no docstring names another write tool or states a write's position in a sequence. They do name the share read tools for argument provenance ("read from the appeal lookup (find_appeals) before the call", "find_appeal_requests") and the user tools say "as the agent reads it to you from the appeal record before you book"; the video/in-person docstrings say the session "replaces the telephone hearing set on your appeal". Observation O1 (no demonstrable consequence: it states no edge and no order between problems).

### prerequisite_graph

| Policy | Edge | kind / gate | form | policy_source verbatim in own rule | resolved_by = depended-on target_tool |
| --- | --- | --- | --- | --- | --- |
| first setting | `[]` | — | — | — | — |
| reopened | `[]` | — | — | — | — |
| video | → `appeal_ext_first_hearing_setting` | value_input / `video_set_days` (exists in compute) | state, no `fallback_reason` | yes | yes (`docket_appeal_hearing_a28520da`) |
| in-person | → `appeal_ext_reopened_hearing_setting` | value_input / `in_person_set_days` (exists in compute) | state, no `fallback_reason` | yes | yes (`reopen_dismissed_appeal_6a7f532d`) |

Graph acyclic; every `problem` is an extended policy id of this file, never a base policy, never self. `effect` holds: both depended-on tools write `appeals.hearing_date`, which the gate binding reads. No authoring-viewpoint phrasing ("in this task", "at the opening") in any `prerequisite` field.

`condition` vs sentence strength:
- in-person: sentence "not booked on a dismissed appeal until the appeal stands reopened at scheduled status with its reopened hearing date on record" ↔ condition (status scheduled, reopening setting on record, hearing_date holds it): same strength and scope.
- video: sentence "only after the appeal's first hearing setting stands on record with its hearing date" ↔ condition additionally requires "its status is scheduled". The sentence does not carry the status; see finding G5.

### prerequisite_sentences

- **video**: "A video session is booked only after the appeal's first hearing setting stands on record with its hearing date." — ordering connective "only after"; state form (a setting record with schedule_reason initial and the appeal's hearing date — words the tables and `find_appeal_events`/`find_appeals` use); no tool, policy id, snake_case token or row id. The one write of this difficulty that brings a *first* setting about is the first-setting docketing (`schedule_reason="initial"`); the reopening write records `reopening`, the session writes record `postponement`. Derivation: sentence → records (filed appeal, empty hearing_date, no `appeal_hearing_scheduled` row) → the first-setting rule ("When the appeals office dockets an appeal filed on a docket that holds hearings, it sets the first hearing…") → docket the appeal. Single reading on a filed appeal. The first-setting rule does not restate the sentence. Breadth defect on dismissed appeals: G5.
- **in-person**: "An in-person session is not booked on a dismissed appeal until the appeal stands reopened at scheduled status with its reopened hearing date on record." — connective "not … until"; state form; no tool/id. Exactly one write brings "reopened at scheduled status" about (the reopening grant; the docketing write requires a filed appeal and records `initial`). Derivation: sentence → records (status dismissed, reopening request `received`) → the reopened-setting rule ("When the appeals office grants an appellant's timely reopening request on a dismissed appeal…") → grant and set. Single reading. The reopened rule does not restate it.
- No rule carries a second wording of either dependency; no rule states an undeclared cross-problem order. Base `appeal_agg_linked_dockets` states "a dismissed lower-authority appeal reaches the Board only after its reopening was denied" — a base cross-problem order grounding no edge of this difficulty (observation only).

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry:

- **first setting** (refs `appeal_evt_scheduling`, `appeal_agg_linked_dockets`): scheduling S1 (default mode) followed — telephone is every hearing docket's default; S2 (status gate) followed; **S3 "The first hearing is set within the docket's scheduling target after filing…" handled differently and declared in `overwrite`** (replaced by "…on the first hearing date that the first-setting rules of this section give…", merged semantics unique); S4 (phone registration), S5 (delivery) untouched. linked_dockets S1/S2 (Board) not reached (hearing dockets only); S3 consolidation not addressed (O2); S4 priority order non-quantitative.
- **video** (refs `appeal_evt_scheduling`, `appeal_agg_linked_dockets`): scheduling **S1 overridden and declared** (adds the video request); S2 followed (scheduled status); S3 notice-minimum clause followed (session ≥ set date + 5); S4/S5 untouched. **Uncited `appeal_evt_postponement` handled differently and undeclared** — G1.
- **reopened** (refs `appeal_evt_default_and_reopening`, `appeal_evt_scheduling`, `appeal_agg_linked_dockets`), `overwrite: []`: reopening S2–S5 followed ("timely", good cause stated, combined hearing); scheduling S1 (telephone), S2 (dismissed allowed), notice minimum (the `MX`) followed; the base `reschedule_window_days` is reused as the reopened window's fall-through, which no base sentence assigns to another meaning for reopenings. No undeclared override.
- **in-person** (refs `appeal_evt_scheduling`, `appeal_agg_linked_dockets`), `overwrite: []`: scheduling S1 ("a party may ask for an in-person hearing where the docket allows it") followed; S2, notice minimum followed. **Uncited `appeal_evt_postponement` handled differently and undeclared** — G1.

No anonymous intermediate factor, 0/1 multiplier or dropped branch found.

### factor_ladders

| Policy | Factor | Label | Tiers (fall-through last) | Distinct outcomes? | Multi-source tiers | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| first setting | first_setting_clock | method | today / filed+3 / filed | yes | no | — |
| | first_setting_target | parameter | 14 / 21 / P(scheduling_target_days) | **no on the Able and Available docket: 21 = 21 (G2)** | yes (appeal role + claim_ledger + claim_certifications) | claim |
| | first_setting_interpreter_lead | parameter | 10 / 7 / 0 | yes | no | — |
| | first_setting_subpoena_lead | parameter | 10 / 7 / 0 | yes | no | — |
| | first_setting_federal_records_lead | parameter | 10 / 7 / 0 | yes | no | claim |
| video | video_block_gap | parameter | 10 / 7 / 5 | yes | yes (interpreter row + docket hearing length) | — |
| | video_accommodation_review | parameter | 5 / 3 / 0 | yes | yes (interpreter row + medical exhibit row) | — |
| | video_identity_check | parameter | 6 / 3 / 0 | yes | no (one idv case) | declared `idv` — idv belongs to no difficulty (O6) |
| | video_exhibit_preparation | parameter | 5 / 3 / 0 | yes | no | — |
| | video_calendar_day | method | Tue/Thu / Wed / weekend→Mon | yes | no | — |
| reopened | reopened_setting_clock | method | medical-exhibit date / today / request date | yes | yes (request reason + exhibit row) | — |
| | reopened_setting_window | parameter | 14 / 17 / P(reschedule_window_days) | **no on the Separation, Able and Available, Monetary and Overpayment dockets: 14 = 14 (G3)** | yes (role + tax ledger + wage report) | taxacct |
| | reopened_setting_exhibit_exchange | parameter | 7 / 4 / 0 | yes | no | — |
| | reopened_setting_interpreter_lead | parameter | 10 / 7 / 0 | yes | no | — |
| | reopened_setting_subpoena_reissue | parameter | 10 / 7 / 0 | yes | no | — |
| in-person | in_person_room_block | parameter | 8 / 6 / 4 | yes | yes (exhibit rows + docket length) | — |
| | in_person_on_site_interpreter | parameter | 5 / 3 / 0 | yes | no | — |
| | in_person_witness_appearance | parameter | 4 / 2 / 0 | yes | no | — |
| | in_person_large_room | parameter | 5 / 2 / 0 | yes | yes (wage report + subpoena requests) | taxacct |
| | in_person_tax_calendar | parameter | 5 / 2 / 0 | yes | no (one account row) | taxacct |
| | in_person_calendar_day | method | Wed / Tue/Thu / weekend→Mon | yes | no | — |

- Counts per policy: first setting 5 (1 method, 4 parameter); video 5 (1, 4); reopened 5 (1, 4); in-person 6 (1, 5). All within 4–6 with ≥2 parameter and ≥1 method.
- Every ladder has three pairwise-disjoint tiers, each stated in the rule with its condition and value/method and implemented in `compute`; the fall-through of every ladder is the baseline binding, and every baseline binding equals what `baseline.rule` states for that input.
- `decides` is an input, never `result`; binding sets are disjoint within each policy.
- Labels: the four calendar/clock `method` factors change the algorithm (which date anchors the clock / which weekday rule rolls the date). `first_setting_clock` tiers 2 and 3 share the filing-date anchor and differ only by the 3-day presumed-receipt number; tier 1 changes the anchor — label partially honest (O5).
- Realism: interpreter, subpoena, federal-records, exhibit, identity, accommodation, room and weekday-calendar conditions are ones appeal tribunals weigh. The reopened window's tax-account conditions and the in-person large-room headcount condition are weak (O4), recorded as observations, not demonstrated as outside practice.
- Per-task multi-source and cross-difficulty availability: the {video ← first setting} tree carries multi-source factors (first_setting_target, video_block_gap, video_accommodation_review) and claim-reading cross-difficulty factors (first_setting_target, first_setting_federal_records_lead); the {in-person ← reopened} tree carries multi-source factors (reopened_setting_clock, reopened_setting_window, in_person_room_block, in_person_large_room) and taxacct-reading cross-difficulty factors (reopened_setting_window, in_person_large_room, in_person_tax_calendar). Whether each bears weight is in the task files.

### findings

**G1 — SOURCE-POLICY RED (undeclared override of `appeal_evt_postponement` by the video and in-person session policies).** Bears on every task whose tree contains `appeal_ext_video_session` or `appeal_ext_in_person_session`; the per-task files demonstrate the consequence on their own worlds.
- Symptom: a party-requested session date far beyond the docket's reschedule window is the scored answer.
- Root cause: the extended rules define their write as "a reset of the hearing made at that party's request" and the tools record it with `schedule_reason="postponement"`, but neither policy cites or overwrites the base postponement policy.
- Evidence: video rule "…and the session replaces the telephone setting on the appeal as a reset of the hearing made at that party's request." (appeal.extended.yaml L1458); in-person rule the same words (L1850); task_tools.py `schedule_reason="postponement"` (L104, L191); base `appeal_evt_postponement` rule "A party may ask to postpone a set hearing. … A granted postponement resets the hearing within the reschedule window, with a new notice that again meets the notice minimum days." and `reschedule_window_days` "Calendar days after a granted postponement within which the hearing is reset" (Separation 14, A&A 14, Monetary 14, Overpayment 14, Benefit Charge 21, Contribution Rate 21); base event `appeal_hearing_scheduled` "(first setting, reset after postponement, or setting after reopening)" and the trigger from `appeal_postponement_decided {postponement_outcome: granted}` to `{schedule_reason: postponement}`. `overwrite` of video names only `appeal_evt_scheduling` S1; in-person `overwrite: []`; neither lists `appeal_evt_postponement` in `base_policy_refs`.
- Consequence (generic): whenever the extended date lies more than the reschedule window after the set hearing (the block gap alone is 5–10 days and the additive factors up to 26 more), the base clause forbids the date the extended rule computes; a reader honouring the base clause caps the reset or treats the request as a postponement that must first be decided (an `appeal_postponement_decided` write no tool of this difficulty performs). Demonstrated per task.
- Affected: `appeal_ext_video_session.rule`/`overwrite`/`base_policy_refs`; `appeal_ext_in_person_session.rule`/`overwrite`/`base_policy_refs`; both user tools' `schedule_reason`.

**G2 — SOURCE-FACTOR RED (first_setting_target: two tiers select the same value on one docket).** Bears on the task whose tree contains `appeal_ext_first_hearing_setting`.
- Evidence: tier 2 value `K('priority_target_days')` = 21 (L1259); fall-through `P('scheduling_target_days')`; base Able and Available docket `scheduling_target_days: 21` (products/appeal.yaml L150).
- Consequence: for a claimant appellant on the Able and Available docket with no payment and fewer than 3 certified weeks in two months, the priority tier and the fall-through give the same 21 — on that docket the tier is one tier written as two, and the factor is decoration for every such customer.
- Affected: `appeal_ext_first_hearing_setting.params.priority_target_days` vs base variant parameter; `factors[first_setting_target].ladder`.

**G3 — SOURCE-FACTOR RED (reopened_setting_window: two tiers select the same value on four dockets).** Bears on the task whose tree contains `appeal_ext_reopened_hearing_setting`.
- Evidence: tier 1 value `K('current_account_window_days')` = 14 (L1632); fall-through `P('reschedule_window_days')` = 14 on the Separation, Able and Available, Monetary and Overpayment dockets (products/appeal.yaml L108, L160, L212, L264). Employer appellants reach the Separation (separating employer) and Monetary (base-period employer) dockets per their `entry_gate`s.
- Consequence: an employer appellant on those dockets that paid ≥ 2,500 in three months and filed its latest report on time gets 14 from tier 1 and 14 from the baseline — the current-account tier is decoration there.
- Affected: `appeal_ext_reopened_hearing_setting.params.current_account_window_days`; `factors[reopened_setting_window].ladder`.

**G4 — SOURCE-POLICY RED, latent (video identity check: rule and compute read different cases for an employer appellant).** Bears on the task whose tree contains `appeal_ext_video_session`; no consequence on a world whose appellant is the claimant who owns the case.
- Evidence: rule "The video identity check days are the unverified identity check days when an identity verification case on the appealed claim stands in any status other than verified…" vs compute `verification_status: CFIELD('idv', 'status', claim_id=F('claim_id'))`, which the engine scopes to `customer_id = CUST` (the appellant) (`check_compute.py` `_cross`). idv cases belong to the claimant (`idv_cases.customer_id` = "Claimant whose identity is verified").
- Consequence: an employer appellant on a Separation appeal whose claim's idv case stands `in_progress`: rule → 6 days; compute → `None` → 0 days.

**G5 — SOURCE-POLICY RED, latent (video prerequisite sentence broader than its condition).** Bears on the task whose tree contains `appeal_ext_video_session`; no consequence on a world where the appeal is filed with no setting.
- Evidence: sentence "A video session is booked only after the appeal's first hearing setting stands on record with its hearing date." vs `condition` "…its status is scheduled, and appeals.hearing_date holds that first setting's date." Base `hearing_on_open_appeal` allows a setting on a `dismissed` appeal; unlike the in-person rule, the video rule has no dismissed-appeal sentence.
- Consequence: on a dismissed appeal whose initial setting is on record (hearing_date = the missed date), the sentence is satisfied and the video date would be counted from a past hearing date; under the condition the agent must first have the appeal reopened. Two conclusions.

Observations (no demonstrated consequence on the audited worlds):
- O1 docstrings cite share read tools and "before the call/before you book" for argument provenance; video/in-person docstrings presuppose "the telephone hearing set on your appeal".
- O2 base consolidation sentence of `appeal_agg_linked_dockets` is not reconciled with any per-appeal date computation.
- O4 realism: the reopened window's tier conditions (≥ 2,500 contribution payments in three months; latest report on time) are not inputs an appeals calendar ordinarily weighs, and the stated reason "because the tax unit must first review that account" is attached to "every other appellant", including claimants who hold no tax account; in-person large-room days keyed to the employer's month-3 headcount rather than to attendees.
- O5 `first_setting_clock` tiers 2/3 differ by a number on one anchor.
- O6 `video_identity_check.cross_difficulty: idv` — idv is claimed by no difficulty in blueprint.yaml (cross-category, not cross-difficulty).
- O7 wording-level filters ("weekly benefit payment", "contribution payments") broader/narrower than the compute filters in worlds that seed supplemental/reissue payments or penalty-component payments.
- O8 the session tools write `schedule_reason=postponement` without an `appeal_postponement_decided` row, so `appeal_msr_postponements_by_party` would not count a session reset toward the per-party maximum.

## closing_checklist

Written after both reveals (2026-10-09T04:21Z); nothing above this heading was changed by a reveal. The difficulty is **not closed**: the four relationships do not all PASS.

| Check | Status |
| --- | --- |
| Per-task audit files 1:1 with tasks (`0.md`, `1.md`) alongside this file; each has a frozen derivation and a `source_gt_comparison` | done; neither comparison carries an all-PASS verdict |
| Extended policies fully covered, scopes pairwise disjoint | task 0 = {first setting, video}, task 1 = {reopened, in-person} (`charter_scope` of each, matching the frozen derivations); disjoint and complete |
| Task tools and GT closed; uuid8s independent and frozen | yes (`action_binding_and_uuids`) |
| Each tree: 1–3 prerequisite problems, ≥ max(n−1,1) value_input, an owner=user write, acyclic; whole-difficulty graph a DAG | yes (n = 1, one value_input edge, user booking, in both tasks) |
| Every computation: self-sufficient baseline, 4–6 factors (≥2 parameter, ≥1 method), per task ≥1 multi-source and ≥1 cross-difficulty, ladders real, every factor bearing weight against an honest baseline, baseline ≠ gold | on-world weight PASS for all 21 factors (baselines 19/40 and 19/40 vs gold 33/57 and 34/63); **ladder reality fails for `first_setting_target` (G2) and `reopened_setting_window` (G3)** |
| Policy self-consistency | **fails: G1 (both tasks, demonstrated on each world); latent G4, G5 (video policy)** |
| Instantiation-stage gates on the final form | the audited artifacts are byte-identical to the gate snapshot's inputs (hashes re-checked at close: extended `2e176529…fbe6b4`, task_tools `2a572cdc…2bab6`, tasks `f1bc0a54…`/`7fe63f02…`); the brief's snapshot (all rc=0, traceability deferred to render) therefore stands for the final form; this audit did not re-run gates |

Per-task verdicts:
- task 0: SOURCE-POLICY RED (G1; latent G4, G5) + SOURCE-FACTOR RED (G2, charter-global); problem tree PASS; derivation = GT.
- task 1: SOURCE-POLICY RED (G1) + SOURCE-FACTOR RED (G3, charter-global); problem tree PASS; derivation = GT.

## revision_2

### charter_global_frozen (round 2)

- Round-1 text above is preserved unchanged. Both shared inputs changed, so every charter-global section is re-derived in full below.
  - `appeal.extended.yaml` round 1 `2e1765294071c99f7b861eb538ffaabbae0e3d9c99376857aeec24a722fbe6b4` → round 2 `71c07481dda9eced400447dd1d5f2f970740a81de793fca989a1fa807786884c`
  - `task_tools.py` round 1 `2a572cdc28b01e7fab36defea7f80ccb05e927df6e3105e77c411b698ce2bab6` → round 2 `d7fe120e70a164c5c044e3042e9e545109ae2791ca86c86f0181faa5349c4f27`
  - Blueprint unchanged (file times 2026-10-08; `products/appeal.yaml` `721e5b16…36f8`). The base copy still parses equal to `products/appeal.yaml` key by key; the only extra key is `extended_policies`.
- Freeze time: 2026-10-10T13:08Z, written before either round-2 task GT was revealed. Auditor: erl-task-policy-audit agent, independent of the instantiator and the reworker.
- Masked and unread at this point: every task's GT fields (round 2), `worklog.md`.
- Entry conditions:
  - The round-2 gate snapshot came with the brief (all rc=0; traceability deferred).
  - The rebuilt views were re-hashed and equal the brief: `task_0.blind.json` `ed8c6147…bf8e`, `task_1.blind.json` `c5aa4779…6b88c36`.
  - The task-1 view hash is identical to round 1, so its world and persona are unchanged. Only its masked GT file changed (`a396968f…7aec`).
  - The task-0 view changed (`9cfa784e…f826`). The only difference the auditor finds is in the persona (see 0.md revision_2).
- Reworker's claims were taken as item ids only. Each was checked against the artifacts below.

### policy_conflict_scan (round 2)

- **Overlap with base `appeal_evt_postponement` (round-1 G1).**
  - The video and in-person rules now call their write "a change of hearing mode made at that party's request".
  - Each rule now carries the sentence "A change of hearing mode booked as a video session [an in-person session] is not a postponement: it needs no postponement request or decision, is not subject to the postponement lead time, does not count toward the party's postponements and is not held to the reschedule window; its date is the video session [in-person session] date this section gives."
  - Both policies list `appeal_evt_postponement` in `base_policy_refs`. Each declares three `overwrite` entries naming the base lead-time, maximum and reschedule-window sentences verbatim; the auditor checked that each `superseded_clause` is a substring of the base rule and each `replaced_by` a substring of the extended rule.
  - Both user tools now record `schedule_reason="not_applicable"` (task_tools.py L108, L187) and their docstrings say "(not a postponement, so no postponement reason is recorded)".
  - Merged semantics: for a mode change, no postponement rule applies. The base sentences still govern genuine postponements, which no extended policy touches. One reading only. **Conflict resolved.**
- Other subjects, triggers, time anchors, terminal states and cross-category boundaries are as in round 1.
- New status sentence in the video rule: "A video session is booked only for an appeal that stands at filed or scheduled status."
  - It is narrower than the base gate ("A hearing is set only while the appeal status is filed, scheduled or dismissed."). The base sentence states a necessary condition and grants no right to a setting on a dismissed appeal, so the two are compatible.
- Scope exclusivity: the two trees are unchanged ({video ← first setting}, {in-person ← reopened}). They are disjoint and together cover all four policies.

### rule_compute_equivalence (round 2)

- Mechanical checks, re-run on the round-2 file:
  - every `compute_basis` sentence is a verbatim rule sentence;
  - every `baseline.rule` sentence is in the rule;
  - every ladder tier is a rule clause and a branch of its `decides` binding.
- Changes since round 1, each checked against the compute:
  - **first setting**
    - The rule now reads "no benefit payment was issued", which matches `XCOUNT(… event_type='claim_benefit_paid')` over every payment kind (round-1 O7 resolved).
    - `priority_target_days` 21 → 18.
  - **video identity (round-1 G4)**
    - The rule now reads "when the appellant holds an identity verification case on the appealed claim …", "the appellant's case on that claim …" and "the appellant holds no identity verification case on the appealed claim".
    - That is exactly the appellant-scoped `CFIELD('idv', …, claim_id=F('claim_id'))` (the engine's `_cross` filters `customer_id = CUST`). For an employer appellant both faces now give 0. **Equivalent; G4 closed.**
  - **reopened**
    - The rule now says "recorded payments received of at least the paid-contribution floor" and "Payments received are the payments recorded as received on the account; voluntary contributions are not payments received for this purpose."
    - That matches `XSUM(… event_type='taxacct_payment_received')` over every component, excluding `taxacct_voluntary_contribution_paid` (round-1 O7 resolved).
    - The added rationale sentence ("Before a reopened hearing on an employer's appeal the tax unit certifies the employer's account …") is quoted in `compute_basis` for the window bindings. It states no quantity of its own.
    - `current_account_window_days` 14 → 10.
  - **in-person**
    - Only `long_room_block_days` 8 → 12.
    - The carve-out sentence is procedural and carries no quantity.
- No new divergence between rule and compute was found.

### action_binding_and_uuids (round 2)

- `(target_tool, computes)` pairs are unchanged and unique.
- The uuid8s are unchanged: `a28520da`, `16bf8e4f`, `6a7f532d`, `05d44a0a`.
- Tool bodies changed only in the `schedule_reason` value of the two user tools. They still read no status, date, ownership or timing and refuse nothing, so the tool layer judges no prerequisite.
- Docstrings: the share-read-tool mentions and "replaces the telephone hearing set on your appeal" remain (O1, kept). No docstring names another write tool or orders the writes.

### prerequisite_graph (round 2)

| Policy | Edge | kind / gate | form | Verbatim in own rule | resolved_by |
| --- | --- | --- | --- | --- | --- |
| first setting | `[]` | — | — | — | — |
| reopened | `[]` | — | — | — | — |
| video | → first setting | value_input / `video_set_days` (exists) | state, no `fallback_reason` | yes | `docket_appeal_hearing_a28520da` |
| in-person | → reopened | value_input / `in_person_set_days` (exists) | state, no `fallback_reason` | yes | `reopen_dismissed_appeal_6a7f532d` |

- The graph is acyclic and each `effect` holds.
- The video edge was rewritten:
  - New `policy_source`: "On an appeal at filed status, a video session is booked only after the appeal stands at scheduled status with its first hearing setting on record."
  - New `condition`: "On an appeal that stood at filed status: the appeal's status is scheduled, an appeal_hearing_scheduled record with schedule_reason initial stands on it, and appeals.hearing_date holds that first setting's date."
  - The sentence now carries both the status and the filed-appeal scope that the condition carries. It is the same strength and scope.

### prerequisite_sentences (round 2)

- **video**
  - Connective: "only after". Form: state ("stands at scheduled status with its first hearing setting on record"). It names no tool or id.
  - Exactly one write moves a filed appeal to scheduled with an initial setting: the docketing write.
  - The dismissed-appeal case (round-1 G5) is now closed. The new status sentence refuses video on a dismissed appeal, and the edge sentence no longer reaches one, so the sentence and the condition no longer diverge. **G5 closed.**
  - Wording note: "On an appeal at filed status … only after the appeal stands at scheduled status" reads as "for an appeal filed and not yet docketed". That is a single reading and no defect.
  - The first-setting rule does not restate the sentence.
- **in-person**: unchanged from round 1; single reading.
- No rule states an undeclared cross-problem order. The video status sentence is a refusal gate with no ordering connective.

### override_declarations (round 2)

- **first setting**: as round 1 (scheduling S3 override declared).
- **video**:
  - Scheduling S1 override declared.
  - `appeal_evt_postponement` swept sentence by sentence:
    - S1 "A party may ask to postpone a set hearing": compatible.
    - S2 lead time: overridden, declared.
    - S3 lead-time counting rule and S4 "A later request is granted only for a documented emergency": moot under the declared carve-out ("needs no postponement request or decision, is not subject to the postponement lead time"). They are not separately named; no second reading results.
    - S5 maximum: overridden, declared.
    - S6 reschedule window: overridden, declared.
    - S7 non-appearance: not affected.
- **in-person**: same sweep as video with the in-person carve-out. `appeal_evt_scheduling` S1 is followed (in-person "where the docket allows it"), so `overwrite` needs no scheduling entry.
- **reopened**: `overwrite: []`. As round 1, no undeclared override.

### factor_ladders (round 2)

The round-1 table stands. The changes and their checks:

- **first_setting_target**: tiers 14 / 18 / `P(scheduling_target_days)`. The docket targets are 30, 21, 30, 30, 45, 60 (Board 0, which has no hearing). No docket value equals 14 or 18, so **G2 is closed**.
- **reopened_setting_window**: tiers 10 / 17 / `P(reschedule_window_days)`. The reschedule windows are 14, 14, 14, 14, 21, 21 (Board 0, which has no hearing). No docket value equals 10 or 17, so **G3 is closed**.
- **in_person_room_block**: 12 / 6 / 4, distinct.
- **video_identity_check**: `cross_difficulty` is now `null`, and the note says idv is claimed by no difficulty (**round-1 O6 resolved**). The video tree still carries claim-reading cross-difficulty factors in the first-setting policy.
- Counts per policy are unchanged: 5 / 5 / 5 / 6 factors, with ≥ 2 parameter and ≥ 1 method in each. Every ladder has three pairwise-disjoint tiers stated in the rule. Every fall-through is the baseline.

### findings (round 2)

- **G1 closed.** Evidence is in `policy_conflict_scan` (round 2). The per-task files confirm the base reading no longer contests either scored date.
- **G2 closed.** Priority 18 is disjoint from every docket target.
- **G3 closed.** Current-account 10 is disjoint from every reschedule window.
- **G4 closed.** The rule now names the appellant's own case, matching the appellant-scoped compute.
- **G5 closed.** The video edge sentence is scoped to filed appeals and carries the scheduled status; video on a dismissed appeal is refused by its own sentence.
- No new SOURCE-* defect was found in the charter, the tool module or the graph.

Observations, round 2:

- O1 kept.
- O2 kept: consolidation is not reconciled with the per-appeal date computations, and no audited world seeds a linked appeal.
- O5 kept.
- O4 narrowed:
  - The stated rationale now covers employers (tax-unit certification), and claimants are named in the fall-through explicitly.
  - Remaining: on the four dockets with a 14-day reschedule window, an employer that paid ≥ 2,500 but filed late gets 17 days, while an employer that paid nothing gets the docket's 14. The paid-but-late account waits longer than the unpaid one.
  - The rule's rationale fixes only the current-account tier as shorter. It does not order the other two, so this is a realism observation, not a demonstrated contradiction.
  - The in-person large-room headcount driver is unchanged.
- O6 resolved.
- O7 resolved.
- O8 superseded: the session tools no longer write `postponement`, and the carve-out says a mode change "does not count toward the party's postponements".
- O10 (new): each postponement `overwrite` entry is a scoped carve-out. Its `replaced_by` does not restate the base sentence for genuine postponements; the base sentence keeps governing those. No audited task requests a postponement.
- O11 (new): a session setting is recorded with `schedule_reason="not_applicable"`. The schema enum offers no mode-change value, and `not_applicable` otherwise marks non-setting rows. No rule reads `schedule_reason` of a session row, so this is a data-model oddity with no consequence.

### closing_checklist (round 2)

Written after both round-2 reveals (2026-10-10T13:09Z). Nothing in `revision_2` above this heading was changed by a reveal.

| Check | Status |
| --- | --- |
| Per-task files 1:1 with tasks, each carrying round-2 frozen derivation and comparison; round-1 text preserved | done |
| Extended policies covered; scopes disjoint | task 0 {first setting, video}, task 1 {reopened, in-person}, per `charter_scope`; disjoint and complete |
| Tools and GT closed; uuid8s independent and frozen | yes |
| Trees: 1 prerequisite problem each, value_input, an owner=user write, acyclic; difficulty graph a DAG | yes |
| Computations: self-sufficient baselines (19 / 40; 19 / 34) differing from gold (33 / 57; 30 / 63); 4–6 factors with ≥ 2 parameter and ≥ 1 method; per task ≥ 1 multi-source and ≥ 1 cross-difficulty (claim; taxacct); ladders real; every factor bears weight | yes (21 / 21 factors bear weight; G2 and G3 closed) |
| Policy self-consistency | yes (G1, G4, G5 closed; no new defect) |
| Gates on the final form | the brief's round-2 snapshot covers exactly the audited hashes (extended `71c07481…`, task_tools `d7fe120e…`, tasks `9cfa784e…` / `a396968f…`; re-hashed at close); traceability deferred to render; this audit ran no gates |

**Round-2 per-task verdicts: task 0 PASS; task 1 PASS.** All round-1 REDs (G1–G5) are closed, with nothing regressed. The difficulty passes the source-layer audit.

Remaining observations, none grounds for rework:

- O1 docstring provenance wording;
- O2 consolidation not reconciled;
- O4 narrowed (paid-but-late 17 against unpaid 14 on 14-day dockets; large-room headcount driver);
- O5 clock label;
- O10 scoped carve-out overwrites;
- O11 `schedule_reason="not_applicable"` on session rows;
- task 0's stale `video_identity_check` trace label.

## revision_3

### charter_global_frozen (round 3)

- Earlier revisions above are preserved.
- Hashes:
  - `appeal.extended.yaml` changed (`71c07481…884c` → `9f55faa8a486f20fc89589672a3d0e39aba4e0d3fae5b89519f0de8e667dc117`), so every charter-global section is re-derived below.
  - `task_tools.py` is unchanged (`d7fe120e70a164c5c044e3042e9e545109ae2791ca86c86f0181faa5349c4f27`). Its round-2 conclusions (`action_binding_and_uuids`) carry forward on that hash: no tool-layer gate, uuid8s unchanged, `schedule_reason="not_applicable"` on session rows.
  - Blueprint unchanged (file times 2026-10-08; `products/appeal.yaml` `721e5b16…`). The base copy is still equal key by key.
- Views re-hashed and equal to the brief (`task_0.blind.json` `ed8c6147…`, `task_1.blind.json` `c5aa4779…`), both unchanged from round 2. The views directory also holds `task_*.runtime.json`, which this audit did not read.
- Freeze time: 2026-10-10T19:11:52Z (append completed), before either round-3 task GT and before the render-layer audit was read.
- Auditor: erl-task-policy-audit agent, independent of the instantiator and reworker.

### policy_conflict_scan / override_declarations (round 3)

**Postponement overwrites in the video and in-person policies.**

- The three round-2 entries (lead time, per-party maximum, reschedule window) are gone. Each session policy now declares one entry against base `appeal_evt_postponement` S1.
  - Superseded: "A party may ask to postpone a set hearing."
  - Replaced by: "A party may ask to postpone a set hearing, and the postponement rules, with their lead time, per-party maximum and reschedule window, govern that request; a party's request to hold its set hearing as a video session [an in-person session] instead is a change of hearing mode and is not a request to postpone."
  - Both strings were checked: the superseded clause is a substring of the base rule, and the replacement is a substring of the extended rule (video rule sentence 2; in-person rule sentence 1).
- Base S2–S7 (lead time, counting rule, emergency exception, maximum, reschedule window, non-appearance) are no longer named in any `overwrite`. They therefore stay in force, unchanged, for genuine postponements. The replacement sentence restates that explicitly.
- The retained carve-out ("A change of hearing mode booked as a video session is not a postponement: … is not held to the reschedule window; its date is the video session date this section gives.") follows from the declared classification. Each base postponement sentence has a postponement as its subject, and a mode change is now declared not to be one, so no base sentence reaches the session date. The carve-out is not an override.
- **Merged semantics:**
  - A genuine postponement request is governed by the full base postponement policy.
  - A video or in-person mode change is not a postponement and is dated by its own section.
  - One reading in each case. **The source-side defect is closed.**
- Other subjects, triggers, eligibility, anchors and terminal states are unchanged from round 2.
- Scopes are unchanged: {first setting, video}, {in-person, reopened}. They are disjoint and complete.
- Sweep of the other cited base policies: unchanged from round 2.
  - first setting: scheduling S3 override declared.
  - video: scheduling S1 override declared.
  - reopened: `overwrite: []`, with no undeclared override; see the new sentence below.

**New reopened-rule sentence (rule sentence 1).** "A reopening request is timely when it is received no later than the docket's reopening window after the mailing date of the dismissal, and the appeal record carries the dismissal's mailing date as its decision mailing date."

- This restates base `appeal_evt_default_and_reopening` ("Reopening is granted only when it is requested no later than the reopening window after the mailing date of the dismissal.").
- It names the base `temporal_basis.anchor_source` (`appeals.decision_mailed_date`).
- "The docket's reopening window" is `reopening_request_days`, which is 15 on every docket. The base counting rule ("starting the day after the mailing date … a request on the last day is in time") is not contradicted.
- It follows base, needs no declaration and carries no quantity of the computation. It also states no cross-problem order.

### rule_compute_equivalence (round 3)

- Re-run mechanically:
  - every `compute_basis` sentence is a verbatim rule sentence;
  - every `baseline.rule` sentence is in the rule;
  - compute bindings, params and factors (effects, `decides`, ladders, baselines, `cross_difficulty`) are identical to round 2.
- The only rule changes are the procedural video sentence 2, the in-person sentence 1 and the reopened sentence 1. None of them carries a quantity.
- Equivalence as in round 2.

### prerequisite_graph / prerequisite_sentences (round 3)

- Both edges are unchanged in every field.
  - Video: "On an appeal at filed status, a video session is booked only after the appeal stands at scheduled status with its first hearing setting on record."
  - In-person: "An in-person session is not booked on a dismissed appeal until the appeal stands reopened at scheduled status with its reopened hearing date on record."
- Both sentences are verbatim in their own rules, in state form with no `fallback_reason`, acyclic, with gates `video_set_days` and `in_person_set_days`.
- Each has a single resolving write, as in round 2. No rule adds an undeclared cross-problem order: the new sentences are a classification and a timeliness restatement.

### factor_ladders (round 3)

- Unchanged from round 2: 5 / 5 / 5 / 6 factors; ladders 14 / 18 / P and 10 / 17 / P, disjoint on every docket; all tiers distinct and stated in the rule.

### findings (round 3)

- **Render-layer source-side item (round-2 postponement overwrites retired the base clauses outright): closed.** Evidence is in `policy_conflict_scan` (round 3).
- **Correction to my round-2 classification.** My round-2 O10 described exactly this shape: each `replaced_by` "does not restate the base sentence for genuine postponements". I recorded it as an observation on the premise that "the base sentence keeps governing those". That premise was wrong. A declared `superseded_clause` is retired by the charter's own override mechanism, so in round 2 genuine postponements lost their lead-time, maximum and reschedule-window rule. That is a demonstrable gap in the merged semantics, and it should have been a charter-global SOURCE-POLICY finding in round 2. The round-2 text is left as written; this note supersedes O10.
- G1–G5 remain closed; the re-checks are above.
- **No new SOURCE-* defect.**
- Observations carried: O1, O2, O4 (narrowed), O5, O11. O10 is resolved by this rework.

### render-layer source-side items, read after the freeze (round 3)

Source: `audits/policy_kb/benefit_and_tax_appeals/0.md` and `1.md`, "Policy-side notes".

1. **"Postponement clauses 2, 5 and 6 are retired wholesale while the replacements cover only mode changes."**
   - **Closed.** No `overwrite` names those clauses any more.
   - The single S1 entry's `replaced_by` keeps "the postponement rules, with their lead time, per-party maximum and reschedule window" in force for genuine postponements.
   - Base clauses 3 and 4 ("the lead time") again refer to an in-force clause.
2. **`parameter_schema` descriptions still stating retired semantics.**
   - **Postponement parameters** (`postponement_request_min_business_days`, `max_postponements_per_party`, `reschedule_window_days`): their clauses are back in force, so the descriptions are accurate again. **Closed.**
   - **`scheduling_target_days`** ("Calendar days after filing within which the first hearing is set") still restates base scheduling S3, which the first-setting policy declares superseded. The base copy must stay verbatim, and the overwrite mechanism operates on rule sentences, so this tension cannot be removed at source. The declared override makes the extended reading the governing one.
   - On task 0 the first hearing is 45 days after filing against a 30-day description. Recorded as **O12** (observation). It was present unchanged in rounds 1 and 2, and the render audit also judged it non-blocking.

### closing_checklist (round 3)

Written after the round-3 reveals (2026-10-10T19:12Z).

| Check | Status |
| --- | --- |
| Per-task files 1:1, each with round-3 freeze and comparison; earlier revisions preserved | done |
| Scopes disjoint and complete; tools / GT closed; uuid8s unchanged and independent | yes |
| Trees: one prerequisite each, value_input, owner=user write, acyclic; difficulty DAG | yes |
| Factor bounds and weight | 21 / 21 bear weight; baselines 19 / 40 and 19 / 34 against gold 33 / 57 and 30 / 63; ladders real (G2, G3 stay closed) |
| Policy self-consistency | yes; the round-2 postponement-overwrite gap is closed, G1–G5 remain closed, no new defect |
| Gates on the final form | the brief's round-3 snapshot covers exactly the audited hashes (extended `9f55faa8…`, task_tools `d7fe120e…`, tasks `9423914f…` / `eec5678e…`); traceability deferred to render; this audit ran no gates |

**Round-3 per-task verdicts: task 0 PASS; task 1 PASS** (all four relationships each). Nothing regressed.

Observations, none grounds for rework:

- O1;
- O2;
- O4 (narrowed);
- O5;
- O11;
- O12 (new: `scheduling_target_days` description);
- task 0's stale `video_identity_check` trace label.

O10 is resolved, and is re-classified in hindsight as a round-2 miss (see the findings in round 3 above).
