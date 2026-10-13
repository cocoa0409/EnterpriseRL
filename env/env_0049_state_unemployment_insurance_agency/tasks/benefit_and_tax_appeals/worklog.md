# benefit_and_tax_appeals — instantiate worklog (category: appeal, M=2)

## Step 0 — difficulty pre-check
- draw_counts.py --tasks 2:
  - task 0: prerequisite_problems=1, factor_counts=[5, 5]
  - task 1: prerequisite_problems=1, factor_counts=[5, 6]
- Base (appeal.yaml) writes: appeal_filed (user), appeal_docketed (agent), appeal_hearing_scheduled,
  appeal_postponement_decided (agent), exhibit/interpreter records (agent), appeal_withdrawn (user),
  appeal_reopened (agent). Decision/dismissal/closure are system events (never a task write).
- Schema constraint discovered: the appeal tables carry NO numeric field; the only quantities a write
  can carry are dates (hearing_date, notice_mailed_date, request_date, received_date, filed_date,
  closed_date). The one genuinely policy-computed quantity in appeals practice is the hearing date of a
  setting (scheduling target, notice minimum, reschedule window, lead times). Every scored parameter is
  therefore a whole number of calendar days from today (the notice mailing date) to a hearing date, and
  the task tool turns it into the date with a pure ordinal-day helper (no datetime import).
- Consequence for the user-owned problem: filing, withdrawing and asking for reopening carry no
  computable quantity (all their dates are "today" or copied facts). The only party act that fixes a
  date is the party's own election of a different hearing mode for a hearing already set (base
  appeal_evt_scheduling: "set ... in the docket's default mode, and a party may ask for an in-person
  hearing"; schema appeal_events.hearing_mode carries telephone / video / in_person). The party books
  the session on the Department calendar; the booking replaces (resets) the telephone setting
  (schedule_reason postponement = a reset of the hearing on the party's request).
- Tree shape chosen per task (1 prerequisite each, value_input edge): agent setting (prerequisite)
  -> party's session booking (root). The booking is counted from the set telephone date, so skipping
  the setting changes the root's value.
- Tool uuid8s (uuid4().hex[:8], one per tool): docket a28520da, video 16bf8e4f, reopen 6a7f532d,
  in-person 05d44a0a.

## Space budget
- task 0: appeal_ext_first_hearing_setting (agent, docket filed->scheduled) + appeal_ext_video_session
  (user, root). Claimant (deaf UCFE claimant), separation docket.
- task 1: appeal_ext_reopened_hearing_setting (agent, dismissed->scheduled) + appeal_ext_in_person_session
  (user, root). Employer (contributory, deficit reserve), Employer Contribution Rate docket. (Revised from the
  benefit-charge docket: a charge appeal names the claimant's claim, whose rows the employer call cannot
  legitimately read, so the closure gate could not be met without god's-eye reads.)
- Disjoint: 4 policies, 4 tools; task 1 needs no asset of task 0.

## Task 0 — closed (per-task gates)
- Tree: appeal_ext_video_session (root, user, 5 factors) -> appeal_ext_first_hearing_setting (agent, 5 factors); value_input edge on video_set_days; state-form prerequisite sentence ("only after").
- Verification (_authoring/verify.py, COMPUTE-gate engine): first setting 33 (baselines 29/48/22/26/22, all-baseline 19); video session 57 (baselines 55/55/55/55/56, all-baseline 40); skipping the docketing write leaves no hearing date (recompute raises).
- Per-task gates: TASK TOOL CONTRACT OK, REPLAY OK (closure 20/20), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. EXTENDED fails only on the two task-1 tools not yet named by a policy (expected until task 1 lands).

## Task 1 — closed (per-task gates)
- Tree: appeal_ext_in_person_session (root, user, 6 factors) -> appeal_ext_reopened_hearing_setting (agent, 5 factors);
  value_input edge on in_person_set_days; state-form prerequisite sentence in the negated direction ("not ... until").
- World: employer (contributory deficit reserve) rate appeal dismissed for non-appearance (mailed 2026-10-09),
  owner's timely reopening request (2026-10-19, illness) + hospital letter (2026-10-20); reopening window to 2026-10-24.
- Verification: reopened setting 34 (baselines 33/41/27/27/27, all-baseline 19); in-person 63 (baselines 56 x5 / 57,
  all-baseline 40); without the reopening write the in-person recompute is 14.
- Per-task gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (20/20), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.

## Difficulty-level closure
- Full suite (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK
  (suite means branches 37.5 / steps 12.5; history_rows_max 12; branches_max 39), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK.
- check_traceability not run: the KB is not rendered yet.
- validate_scenario: no frozen_time / forbidden-token / rw / replay error; the only ERRORs are "required document ... not
  found" for the four policy ids (KB-dependent; they clear once erl-kb-doc-render publishes docs with meta.policy_id).
- Verification code: authoring scripts (policy builders, seeds, a verifier calling check_compute's build_env /
  eval_compute / substitute over a real tool replay) were removed from the bundle after use; check_compute.py
  reproduces every scored figure, per-factor baseline and fall-back recorded in the tasks.
- Known design stretches for the auditors: (1) the party's own mode election (video / in person) is booked by the
  party and recorded as a reset setting (schedule_reason postponement), since the schema has no other reason value;
  (2) video on request is added by a declared overwrite of the base mode sentence (hearing_mode already lists video);
  (3) scored values are day counts that the tools convert to dates (appeal tables carry no numeric field).

## Rework round 2 (audits/policy_task/benefit_and_tax_appeals: _difficulty.md, 0.md, 1.md)
- G1 (SOURCE-POLICY RED, both tasks — undeclared override of appeal_evt_postponement): video and in-person rules now call the
  booking "a change of hearing mode made at that party's request" and add "A change of hearing mode booked as a video/in-person
  session is not a postponement: it needs no postponement request or decision, is not subject to the postponement lead time, does
  not count toward the party's postponements and is not held to the reschedule window; its date is the ... session date this
  section gives." appeal_evt_postponement added to both policies' base_policy_refs; its lead-time, per-party-maximum and
  reschedule-window sentences declared in overwrite (3 entries each). Both user tools now write schedule_reason "not_applicable"
  (was "postponement"); docstrings say "entered as a change of hearing mode ... (not a postponement ...)". Also closes O8.
- G2 (SOURCE-FACTOR RED — first_setting_target 21 = A&A target 21): priority_target_days 21 -> 18 (distinct from 14 and from every
  docket target 21/30/45/60). Task 0 takes the expedited tier: figures unchanged (33 / 57).
- G3 (SOURCE-FACTOR RED — reopened_setting_window 14 = reschedule window 14 on four dockets): current_account_window_days 14 -> 10
  (distinct from 14/21 and from 17). Task 1 takes this tier: reopened 34 -> 30 (2026-11-20). Knock-on: long_room_block_days 8 -> 12 so
  the in-person candidate is again a Thursday and every factor still moves the result; in-person stays 63 (2026-12-23). All task-1
  figures, traces, closure texts, evaluation argument (step 9 notice_period_days 30) and computations updated; new per-factor baselines
  reopened 29/41/23/23/23 (fall-back 19), in-person 49/56/56/56/56/57 (fall-back 34); skip-reopening 14.
- G4 (latent — identity read): video identity rule now reads "the appellant holds an identity verification case on the appealed claim",
  matching the compute's customer-scoped CFIELD; ladders updated. Task 0 figures unchanged.
- G5 (latent — prerequisite sentence broader than condition): sentence now "On an appeal at filed status, a video session is booked
  only after the appeal stands at scheduled status with its first hearing setting on record."; condition carries the same status and
  scope; added scope sentence "A video session is booked only for an appeal that stands at filed or scheduled status." (no dismissed
  appeal can feed a past hearing date). Exactly one write (first docketing) brings the state about on a filed appeal.
- O1: kept — Args must say where an id is read before the call (task-tool contract); no edge or order is stated.
- O2: kept as observation — no world seeds a linked appeal; the per-appeal compute cannot read another appeal, so a consolidation
  branch could not be implemented in compute without a rule/compute domain gap; the base consolidation clause stays in force.
- O4: reopened window now states its business reason (tax unit certifies an employer's account before a reopened hearing; a paid-up,
  reporting account is certified without review) and no longer attaches an account-review reason to claimant appellants.
  Large-room tier kept (headcount combined with a subpoenaed witness).
- O5: kept — tier 2 changes the clock's anchor (presumed receipt date) as well as tier 1 (today); recorded.
- O6: video_identity_check.cross_difficulty -> null (idv is cross-category only); task 0 keeps two claim cross-difficulty factors.
- O7: "weekly benefit payment" -> "benefit payment" (first setting); "contribution payments" -> "payments received", voluntary
  contributions stated as excluded (reopened) — wording now equals the compute filters.
- O8: closed with G1 (no postponement reason recorded by the session tools).
- Task 0 persona observation: removed the unconditional "You are happy for the agent to take care of whatever the Department itself
  has to record."; the conditional go-ahead line remains.
- Task 1 trace observation: in_person_tax_calendar no longer labelled multi-source.
- Both tasks' design_rationale carry a "[Rework round 2]" section with the same per-item changes and the re-verification figures.
- Gates after rework (per-task 0 and 1, then full): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK
  (suite means branches 37.50 / steps 12.50; history_rows_max 12; branches_max 39), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK.
  validate_scenario: only pre-render "required document ... not found" errors; no forbidden tokens; frozen_time format unchanged.
- Authoring helpers lived in /tmp/rw49 (removed).

## Rework round 3 (audits/policy_kb/benefit_and_tax_appeals/{0,1}.md "policy-side notes"; audits/runtime_context/benefit_and_tax_appeals/{0,1}.md)
- KB note 1 / coordinator item (postponement clauses retired wholesale): the three round-2 overwrite entries on
  appeal_evt_postponement (lead time, per-party maximum, reschedule window) are removed from both session policies, so those
  base clauses stay in force for genuine postponements (and clauses 3/4's "the lead time" again has its referent). Each
  session policy now declares one overwrite on that base policy: superseded_clause "A party may ask to postpone a set
  hearing." -> replaced_by (new sentence in its rule) "A party may ask to postpone a set hearing, and the postponement rules,
  with their lead time, per-party maximum and reschedule window, govern that request; a party's request to hold its set
  hearing as a video [in-person] session instead is a change of hearing mode and is not a request to postpone." The
  existing "A change of hearing mode booked as a ... session is not a postponement: ..." sentence stays (explanatory, now
  consistent with clauses in force). This keeps the G1 closure of round 2: the override that makes a mode change not a
  postponement is still declared. No scored value moved (0: 33/57; 1: 30/63; all per-factor and fall-back figures unchanged).
- KB note 2 (base parameter_schema descriptions of scheduling_target_days / postponement parameters): base text, frozen,
  recorded by the coordinator as known. With note 1 closed the postponement parameter descriptions are again in-force law;
  the scheduling-target description vs the first-setting overwrite remains a base-text tension (not editable).
- Task 1 runtime / KB observation (record field for the dismissal mailing date): the reopened-setting rule now states "A
  reopening request is timely when it is received no later than the docket's reopening window after the mailing date of
  the dismissal, and the appeal record carries the dismissal's mailing date as its decision mailing date." (entailment of
  base anchor_source appeals.decision_mailed_date; not in compute; baseline unchanged).
- Task dossiers: round-2 sentences claiming the three clauses were superseded were corrected and a "[Rework round 3]"
  section added to both design_rationale fields.
- Tools: task_tools.py untouched in round 3 — no tool name, signature or docstring changed.
- Gates: per-task 0/1 and full suite all OK (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING,
  TRACEABILITY 0.json 14 0 True / 1.json 15 0 True, CACHE-DIFF INFO, SCOPE). The render gate check_docs.py now reports DOCS NOT
  OK because the published hearing_postponement doc still marks clauses 2/5/6 retired and no doc declares clause 1 retired —
  the appeal KB needs re-rendering against this charter (docs/ is outside this write domain).
- Scratch in /tmp/rw49c (removed).
