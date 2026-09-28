# Policy-task audit — prior_authorization_services / charter-global

## charter_global_frozen

- Freeze time: 2026-09-24T17:08Z (round 1). Auditor: erl-task-policy-audit subagent (Claude Opus 5.5), independent of the instantiating agent; no answer supplied by the coordinator was used.
- `tasks/prior_authorization_services/auth.extended.yaml` sha256 `12359401d501c485896c2061c0f3ac2f0fe37f1eabf0816e3fda887dc88c207a` (matches brief).
- `tasks/prior_authorization_services/task_tools.py` sha256 `5a86fdc8390204e22f409052935186b178267fd53378a99a54f6cd34e3b6e1e8` (matches brief).
- Read: `blueprint/blueprint.yaml`, `blueprint/products/auth.yaml` (and `appeal.yaml` subject enums only), `blueprint/db_schema.json` (appeal_cases enums), `blueprint/share_tools.py`, the two files above, and the evaluator semantics of `skills/erl-task-instantiate/scripts/check_compute.py` (`MONTHS`/`DAYS`/`within_months`/`X*` scoping). Masked views of 0.json and 1.json (hashes 34a79380…, cf2b86eb…, verified).
- Masked / unread at the time of writing this section: every task JSON under `tasks/prior_authorization_services/tasks/`, `worklog.md` (scenario and difficulty), `__pycache__`, any other audit directory. This section contains nothing derived from a revealed GT.
- Entry conditions: gate snapshot supplied with the brief (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all rc=0; check_traceability deferred until KB publication). Masked views and hashes supplied. Entry conditions satisfied.

### policy_conflict_scan

- Base copy: lines 1-1681 of `auth.extended.yaml` are byte-identical to `blueprint/products/auth.yaml` (`diff` empty). Base is verbatim.
- Seven extended policies, seven distinct subjects/target tools:

| policy | subject | computes | target_tool | owner |
| --- | --- | --- | --- | --- |
| auth_ext_expiry_release | auth_units_released (expired) | units_released | release_expired_units_43b7942e | agent |
| auth_ext_transition_units | auth_submit (TOC) | units_requested | record_transition_of_care_request_bf098d50 | agent |
| auth_ext_member_review_extension | auth_timeline_extension | extension_days | request_review_time_extension_2522d00e | user |
| auth_ext_void_release | auth_void + auth_units_released (voided) | units_released | void_authorization_7849b1e5 | agent |
| auth_ext_provider_carryover | auth_provider_update | units_carried | change_servicing_provider_0d360835 | agent |
| auth_ext_member_extension_request | auth_extension_request | requested_units | file_extension_request_1d826295 | user |
| auth_ext_extension_units | auth_extend | units_added | record_extension_d36e0acf | agent |

- Overlapping subjects: expiry release and void release both post `auth_units_released` with a computed `units_released`; they are separated by status/reason (ended approval, release_reason expired vs. approved approval being voided, release_reason voided). Residual overlap (observation O-3): an approval whose end date has passed but whose status is still `approved` satisfies the expiry rule's trigger ("Once an approval's end date has passed") and could also be voided; the charter does not say which applies. Neither task world contains such a row.
- Base event `auth_expire` still carries the trigger `auth:auth_units_released {release_reason: expired, posted_date: closed_date}` (auth.yaml lines 655-669), i.e. the system posts the expiry release on the closed date; the extended overwrite of `auth_validity_units` replaces the policy sentence but not this event trigger (observation O-2).
- Time anchors: TOC window (base `toc_window`, 90 days from day after coverage start) is compatible with the extended late-request cut and transition-window cut, both counting `DAYS(coverage_start_date, NOW)` = "from the day after" convention. Compatible.
- Cross-category read boundaries: every extended policy's `cross_category` list matches its compute's X*/CFIELD reads (plan, appeal, care, pcp, ride). Reads only; no cross-category write.
- Scope claims (from the task files' masked views + user_scenario only, not from `charter_scope`): task 0's persona raises a review-time extension on a transition-of-care matter (tree: member_review_extension <- transition_units <- expiry_release); task 1's persona raises an extension of a therapy approval (tree: extension_units <- {member_extension_request, provider_carryover, void_release}; member_extension_request <- provider_carryover). Derived scopes are disjoint and jointly cover all seven extended policies. (Confirmed against `charter_scope` only after the reveal; see each task file.)

### rule_compute_equivalence

Swept every compute binding against its `compute_basis` quotation and back against the rule, for all seven policies.

- auth_ext_expiry_release: every binding quoted; lag hold (`int(used*days/weeks/7)`, `int(used/weeks)`, `0`) equals the rule's three tiers; 2-month window = `within_months=2` = "fewer than two whole months separate it"; appeal count over filed/acknowledged/under_review with subject claim_denial matches. No invented basis; no empty promise.
- auth_ext_transition_units: all six adjustments and the standard match. **Divergence (observation O-1):** the rule caps the standard figure itself ("never below zero and never more than the class's most units per approval") and then caps the adjusted total; compute `toc_standard = MX(0, toc_prior_left - (toc_granted - toc_released))` does not cap the standard, only the final `result`. The two faces differ only when the standard exceeds `max_units_per_auth` and the net adjustments are negative (e.g. standard 25, BH max 20, net -4: rule 16, compute 20). Not reachable on task 0's world (standard 9 < 20).
- auth_ext_member_review_extension: all bindings quoted; `MX(1, MN(max, …))` matches "limits of one day and of the class's most review-extension days". Equivalent.
- auth_ext_void_release: equivalent; `vd_active_weeks` = 1 when no use is posted is covered by "never fewer than one week".
- auth_ext_provider_carryover: equivalent, with two minor gaps (observation O-4): `pc_use_gap` falls back to `start_date` when no use is posted, which the rule does not state; the attendance rule's top tier reads "more takes off nothing" where compute's boundary is `>= 4*cap`. Neither is reachable on task 1's world (uses posted; 2 uses).
- auth_ext_member_extension_request: equivalent (late pickup + provider no-show = "picked up late or at which the ride did not show").
- auth_ext_extension_units: all bindings quoted. **Empty promise (observation O-5):** rule sentence 1 says the extension adds units "within the extension count and the annual limit the class sets", and base `auth_agg_annual_limit` says "An approval or extension that would pass the limit is granted only up to the units left"; compute has no annual-limit bound (only `MN(P('extension_max_units'), …)`). Consequence is world-dependent; see task 1 (non-binding there by exact equality).
- Every declared factor's ladder tiers appear both as rule sentences and as branches of the `decides` binding, and vice versa, in all seven policies. No tier lives only in compute.

### action_binding_and_uuids

- Each `(target_tool, computes)` is claimed by exactly one policy (table above); `task_tools.py` defines exactly those seven tools.
- uuid8s: 43b7942e, bf098d50, 2522d00e, 7849b1e5, 0d360835, 1d826295, d36e0acf — distinct, no shared prefix or sequence, no adjacent values. PASS.
- Docstrings: no docstring names another tool, states its position in a sequence, or uses before/after/first as an ordering between actions (grep over the module: the only hits are "prior authorization", "prior health plan", "then see …" as the consequence of the same call, and "carries no prior-plan authorization number until one is supplied", which describes its own field). PASS.
- No tool judges eligibility, timing, amounts or prerequisites: every body does `ctx.find` / `ctx.create` / `ctx.update` unconditionally and returns a confirmation; none refuses or hints (task_tools.py lines 36-48, 88-105, 130-148, 176-189, 222-226, 253-264, 291-305). PASS.

### prerequisite_graph

- `prerequisite` filled on all seven policies (`[]` on expiry_release, void_release, provider_carryover).
- Edges: A transition_units -> expiry_release (value_input, gate `toc_released`); B member_review_extension -> transition_units (state_gate, gate `auth_authorizations.request_origin`); C member_extension_request -> provider_carryover (value_input, gate `xr_remaining`); D extension_units -> member_extension_request (value_input, `ex_asked`); E extension_units -> provider_carryover (value_input, `ex_remaining`); F extension_units -> void_release (state_gate, gate `auth_authorizations.status`).
- Every `problem` is an extended policy id of this file, none is base, none self. Graph acyclic (two components: expiry -> TOC -> review-ext; carryover -> member-ext-request -> extension_units <- carryover, void).
- Every `policy_source` located verbatim in its own policy's `rule` (checked string-by-string). `form: state` on all six; no `fallback_reason` present, none required.
- value_input gates name real compute bindings (`toc_released`, `xr_remaining`, `ex_asked`, `ex_remaining`); `resolved_by` equals the depended-on policy's `target_tool` in all six, and the tool's effect produces the gated state (release row with release_reason expired; new row with request_origin transition_of_care, status submitted; servicing_provider_npi + units_remaining update; auth_actions auth_extension_request requested_by member; status voided).
- Observation O-6: the two `state_gate` edges name a table field as `gate` rather than an eligibility-gate id (the extended policies carry no `eligibility` list); semantics are carried by the prerequisite sentence and `condition`, so no reader-visible consequence.
- No authoring-viewpoint phrasing ("in this task", "at the opening") in any `prerequisite` field.

### prerequisite_sentences

Four-point test per edge (connective / state named in record words / no tool, id or snake_case / strength equals `condition`):

- A: "The units a transition-of-care request asks for are fixed only after every earlier approval of the member for the same service code whose end date has passed carries an expiry release entry." — "only after"; state = an expiry release entry on each ended approval of the same service code (auth_units released, reason expired); no tool/id; closed set "every earlier approval … whose end date has passed" = condition. Exactly one write of this difficulty produces an expiry release entry (release_expired_units; the void tool posts reason `voided`). Derivation: sentence -> records show an ended approval without such an entry -> the expiry-release rule ("Once an approval's end date has passed … booked as one expiry release entry") is the only rule that books one. Single reading. PASS.
- B: "The days a member-requested deadline extension adds are not fixed until a transition-of-care request for the member stands on file undecided." — "not … until"; state = a TOC request on file, undecided (request_origin/status); exactly one write creates one (record_transition_of_care_request). Single reading. PASS.
- C: "The units an extension request asks for are worked out only once the authorization names, as its servicing provider, the provider who will deliver the extended units." — "only once"; state = servicing provider on the authorization; exactly one write sets it (change_servicing_provider). The identity of "the provider who will deliver" is a customer fact (persona). PASS.
- D: "The units an extension adds are fixed only after the authorization carries the member's extension request stating the additional units asked for." — "only after"; state = auth_actions extension request by the member; one write (file_extension_request). PASS.
- E: "The units an extension adds are not worked out before the authorization names, as its servicing provider, the in-network provider who will deliver them." — "not … before"; same state as C; one write. PASS.
- F: "The units an extension adds are not recorded until no other approval of the member for the same therapy discipline stands approved over dates that overlap the period the extension adds." — "not … until"; state = no overlapping approved row of the same discipline; the only write of this difficulty that takes an approval out of `approved` is void_authorization (withdraw applies only to undecided requests and has no tool here; carryover and extension keep status). PASS. Observation O-7: for classes whose `therapy_discipline` is `not_applicable`, "the same therapy discipline" is ill-defined (all non-therapy approvals would share the value); irrelevant to task 1 (physical_therapy).
- No rule carries a second wording of any of these dependencies, a tool name or another problem's id; no depended-on rule restates the sentence. No extended rule states a cross-problem order grounding no declared edge. Base sentence "In a class that does not allow the change, or to an out-of-network provider, the member may have the approval voided and the new provider submits a new request" (auth_provider_change) relates void and a new submission, grounds no edge used by either tree — no finding.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry:

- auth_ext_expiry_release vs auth_validity_units: "Units left on end_date are released the next day and cannot be used later where expired_units_forfeited is true" — handled differently (released less hold-backs, dated the booking day) — declared in `overwrite`, replaced_by carries "less the hold-backs set out below". Other auth_validity_units sentences (validity window, max units, usage window, weekly cap) followed. vs auth_void_withdraw: not touched. Unique merged semantics. PASS.
- auth_ext_transition_units vs auth_transition_of_care: "…honored without a new medical necessity review for the units the prior authorization had left…" — declared; **but the declared `replaced_by` reads "the units a transition-of-care request asks for are the units requested on that earlier approval, less the units Prairie Ridge covered on it, which are the units granted on it less the units released from it, never below zero and never more than the class's most units per approval." — a categorical statement of the quantity equal to the extended rule's *standard* figure, with no "as the standard method" and no "adjusted as set out below".** The extended rule then states "Six adjustments are added to or subtracted from that standard figure". The merged base sentence and the extended rule assign two different values to the same quantity whenever any adjustment is non-zero (finding F-1). The three sibling overwrites (expiry, void, carryover) each carry the hedge ("less the hold-backs set out below", "worked out as set out below"); this one does not. Other base sentences (TOC window, end date = earlier of prior end and transition end, prior auth number requirement, after-period ordinary request) are followed. vs auth_agg_duplicate_request, auth_agg_multi_holding, auth_out_of_network, auth_service_scope: followed.
- auth_ext_member_review_extension vs auth_turnaround (`overwrite: []`): "may be extended once by up to review_extension_max_days when the member asks" — extended pins a value in 1..max: follows. "written notice of the extension and of the right to file a grievance" — tool mails the extension notice: follows. "taken no later than standard_decision_days after received date" — follows. PASS.
- auth_ext_void_release vs auth_void_withdraw: "the units left are released the same day where void_releases_units is true" — declared, hedged. "units already used are never reversed", "never reopened" — followed. vs auth_provider_change: followed. PASS.
- auth_ext_provider_carryover vs auth_provider_change: "the units left and the end_date carry over unchanged" — declared, hedged ("worked out as set out below"); in-network / approved-status / class-allowed sentences followed. PASS.
- auth_ext_member_extension_request vs auth_extension (`overwrite: []`): requested end date = end date + extension_days follows; requested units are not bounded by extension_max_units, but base bounds units *added*, not units *asked* — no conflict. PASS.
- auth_ext_extension_units vs auth_extension (`overwrite: []`): "each adding at most extension_max_units and moving end_date forward by extension_days" — followed. vs auth_agg_annual_limit: "An approval or extension that would pass the limit is granted only up to the units left" — rule sentence 1 claims to follow it, compute does not implement it (O-5). Not an override in the rule text; a rule/compute gap whose consequence depends on the world.

### factor_ladders

| policy | factors (effect) | param / method | multi-source factors | cross-difficulty reads |
| --- | --- | --- | --- | --- |
| expiry_release | claims_lag_holdback (method), reprocessing_holdback, appeal_holdback, discharge_session_holdback (parameter) | 3 / 1 | discharge_session (care tier AND follow-up) | plan (claims), appeal*, care* |
| transition_units | hospital_stay_credit (method), late_request_cut, step_down_addition, population_addition, attendance_cut, referral_addition | 5 / 1 | hospital_stay (plan claim AND care follow-up), step_down (tier AND update) | plan, care*, pcp |
| member_review_extension | gathering_days, transition_window_cut, referral_cut, appeal_addition, risk_cut (parameter), mailing_days (method) | 5 / 1 | gathering_days (tier AND contact) | care*, plan, pcp, appeal* |
| void_release | late_billing_holdback (method), rebilling, hand_off, booked_ride | 3 / 1 | hand_off (tier AND update) | plan, care*, ride |
| provider_carryover | delivery_weeks (method), unposted_visit, re_evaluation, attendance | 3 / 1 | delivery_weeks (plan update AND latest contact), unposted (plan claims AND auth uses) | care*, plan |
| member_extension_request | weekly_rate (param), request_weeks (method), remaining_units_deduction (method), make_up, population, risk | 4 / 2 (see F-2) | weekly_rate (auth uses AND care update), request_weeks (end date AND remaining) | care*, pcp, ride, plan |
| extension_units | asked_share, referral, grievance, prior_grant, population (param), remaining_units_deduction (method) | 5 / 1 (see F-2) | remaining_units_deduction (care update AND remaining) | care*, pcp, appeal*, plan |

(* `care` and `appeal` are products of this scenario but are not difficulties in `blueprint.yaml`'s `difficulties` list; factors tagged `cross_difficulty: care|appeal` read another *category*, not another *difficulty* — observation O-8. Every policy nevertheless has at least one factor reading plan, pcp or ride, which are difficulties.)

- Every factor declares a `decides` input binding (never `result`); binding sets within one policy are disjoint; every ladder has exactly three tiers, pairwise disjoint as stated, fall-through last; every factor's `baseline` equals its fall-through tier, and each policy's `baseline.rule` is a verbatim sentence of its `rule`.
- No two tiers of one ladder select the same value for the therapy / BH classes the tasks use. (Degenerate classes: in member_extension_request `weekly_rate`, a class with `weekly_frequency_cap` 0 (Imaging, DME) makes the fall-through rate 0 and the "fewer than twice the cap" conditions unsatisfiable — observation O-9, not reachable in either task.)
- Label honesty:
  - Honest `method`: claims_lag / late_billing (pro-rated by elapsed days vs. flat week vs. none — the first tier introduces a new input), hospital_stay_credit (class cap vs. history pace vs. none), mailing_days (business->calendar conversion vs. flat 1 vs. identity), delivery_weeks (ceil vs. daily pro-rate vs. floor), request_weeks (counted from today to the asked end date vs. extension weeks less one vs. extension weeks).
  - **Mislabelled `method` (finding F-2):** `remaining_units_deduction` in auth_ext_extension_units (tiers "nothing is deducted" / "half of the units remaining, rounded down" / "all of the units remaining") and the same-named factor in auth_ext_member_extension_request (tiers "not deducted" / "half … rounded down" / "all"). Every tier is one formula `floor(f × units_remaining)` with f = 0, 1/2, 1: the tiers substitute a different rate into the same formula, which is the skill's definition of a `parameter`. In auth_ext_member_extension_request request_weeks remains an honest method (count 1 holds). In auth_ext_extension_units this is the only `method` factor, so the policy has **0 honest method factors** against a floor of 1.
- Realism (observations, not demonstrated to fail): grievance_addition (a Quality of Care Grievance filed in 3 months adds extension units), referral_cut in the review-time extension (a PCP referral shortens the days a member gets to gather papers), prior_grant_cut, and the population additions are business rationales an MCO could publish but that sit outside the class's stated clinical criteria set; recorded as O-10 without a red light.

### findings

- **F-1 — SOURCE-POLICY (bears on task 0).** Symptom: the declared override of auth_transition_of_care states the TOC units as the standard figure alone. Root cause: `overwrite[0].replaced_by` of auth_ext_transition_units (auth.extended.yaml lines 1841-1845) omits the "standard method / adjustments set out below" hedge that the rule (lines 1866-1873) relies on. Evidence: quotations above. Consequence: two values for `units_requested` on any world with a non-zero adjustment; demonstrated in `0.md`.
- **F-2 — SOURCE-FACTOR (bears on task 1; observation for the member-extension-request computation).** Symptom: `remaining_units_deduction` labelled `method` is a rate substitution. Root cause: factor declarations at auth.extended.yaml lines 2674-2688 and 2885-2899; compute `xr_deduction` (line 2618) and `ex_deduction` (line 2840). Consequence: auth_ext_extension_units has no honest `method` factor; demonstrated in `1.md`.
- O-1 standard not capped in TOC compute (non-reachable in task 0). O-2 base `auth_expire` trigger vs. extended booked expiry release (bears on task 0's seed; see `0.md`). O-3 expiry/void overlap on end-passed-but-approved rows. O-4 carryover minor gaps. O-5 annual limit promised in extension_units rule, absent from compute (see `1.md`). O-6 state_gate `gate` names a field. O-7 "same therapy discipline" for non-therapy classes. O-8 `cross_difficulty: care|appeal` labels a non-difficulty category. O-9 degenerate weekly_rate for cap-0 classes. O-10 realism of several additions.

## closing_checklist

Written after both reveals (2026-09-24T17:11Z onward). **The difficulty does not close in this round**: not every task PASSes all four relationships.

| item | status |
| --- | --- |
| one audit file per task (`0.md`, `1.md`) plus this file; every comparison section present | done; task 0 carries SOURCE-POLICY RED (F-1), task 1 carries SOURCE-FACTOR RED (F-2) |
| extended policies fully covered; scopes pairwise disjoint | confirmed against `charter_scope`: task 0 = {expiry_release, transition_units, member_review_extension}, task 1 = {void_release, provider_carryover, member_extension_request, extension_units}; disjoint, union = all 7 |
| task tools and GT closed; uuid8s independent | yes (§ action_binding_and_uuids); every GT write uses exactly the claimed tools |
| trees: 1–3 prerequisite problems, ≥ max(n−1,1) value_input, ≥1 owner=user, acyclic; difficulty graph acyclic | task 0: n=2, 1 value_input, user root; task 1: n=3, 2 value_input into root (+1 inner), user extension request; whole graph acyclic |
| computations: self-sufficient baseline, 4–6 factors, ≥2 parameter and ≥1 honest method, ≥1 multi-source and ≥1 cross-difficulty per task, every factor bears weight | all hold except `auth_ext_extension_units` (0 honest method — F-2) |
| gates re-run on the final form | not applicable until F-1 and F-2 are resolved and the artifacts re-audited |

Per-task verdicts: task 0 — SOURCE-POLICY RED (F-1); problem tree PASS; factors PASS; unique solution PASS apart from the F-1 second reading. Task 1 — SOURCE-FACTOR RED (F-2); policy PASS; problem tree PASS; unique solution PASS.

## revision_2

Re-audit round 2, 2026-09-24 (after rework). Auditor: same erl-task-policy-audit subagent; derivation is no longer blind (round-1 reveal already happened), so this revision checks closure item by item, looks for new defects and regressions, and recomputes every scored value on the reworked charter.

### inputs and carry-forward grounds
- `auth.extended.yaml` sha256 `fc7fae82d87118fcab9bab5ee959f165f704a5f0cc401f7e00121acdf1d65439` (changed from `12359401…`) -> every charter-global section re-derived below.
- `task_tools.py` sha256 `5a86fdc8…` (unchanged) -> § action_binding_and_uuids carried forward from round 1 by reference (uuids, docstrings, non-judging bodies unchanged).
- Base copy: lines 1-1681 still byte-identical to `blueprint/products/auth.yaml` (the only diff is the trailing blank separator line).
- Masked views round2: 0.json `34a79380…` (unchanged), 1.json `60ec2c1f…` (only `user_scenario` changed; `frozen_time` and `initial_state` identical to round 1). Task JSONs now `b691f114…` (0) and `23aad17f…` (1).
- Gate snapshot supplied in `scratchpad/brief_auth_r2.md`: check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all rc=0.
- Recomputation: `scratchpad/audit/recompute_r2.py` (the round-1 harness pointed at the round-2 views and reading the reworked charter from disk).

### item-by-item closure

| id | round-1 finding | round-2 evidence | status |
| --- | --- | --- | --- |
| F-1 | TOC overwrite `replaced_by` stated the standard figure categorically | `replaced_by` (lines 1845-1846) now reads "As the standard method, … Six adjustments are added to or subtracted from that standard figure, … before the ceiling … is applied; the total is never below zero." — the merged base clause and the extended rule give one value | **closed** |
| F-2 | extension-units `remaining_units_deduction` labelled `method` was a rate substitution | ladder tier 2 now "only the units the weekly frequency cap cannot deliver before the current end date are deducted: units remaining less the cap times the whole weeks to the current end date, never below zero" (rule line 2786, compute `ex_deduction` line 2850 with new binding `ex_weeks_to_end`). Tiers are now 0 / `max(0, R − cap × W)` / `R`: tier 2 brings in a new input (weeks to end date) and a different formula. It is no longer one formula with a different fraction. Honest `method` | **closed** |
| F-2 (2nd) | member-extension-request deduction labelled `method` | renamed `remaining_units_share`, `effect: parameter`, deciding `xr_deduct_halves` ∈ {0, 1, 2} halves, with `xr_deduction = xr_remaining * xr_deduct_halves // halves` stated in the rule (lines 2579, 2582, 2624-2625); `request_weeks` keeps the method count at 1 | **closed** |
| O-1 | TOC standard not capped in compute | `toc_standard: MX(0, MN(P('max_units_per_auth'), …))` (line 1904) | **closed** |
| O-2 | base `auth_expire` trigger vs. booked expiry release on the seed | new expiry sentence (line 1711): "An approval whose end date has passed owes this expiry release whatever its status shows, including an approval whose expiry was recorded without a release entry; …". Base event trigger remains in the verbatim base copy (cannot be edited), but the extended rule now states the seed's case explicitly | **closed** (at the extended layer) |
| O-3 | expiry/void overlap on end-passed-but-approved rows | expiry sentence above ("it is the expiry release, never a void, that returns the unused units of such an approval") + void sentence (line 2271) "A void applies only to an approval whose end date has not yet passed; …" — disjoint | **closed** |
| O-4 | carryover start-date fallback / "more" boundary | rule line 2429 "(or from the approval's start date where no use is posted)"; line 2430 "four times the weekly frequency cap or more takes off nothing" — both match compute | **closed** |
| O-5 | extension rule promised the annual limit, compute lacks it | the extended rule no longer mentions the annual limit (line 2779), so the empty promise is gone. Base `auth_agg_annual_limit` is still inherited (`base_policy_refs`, `overwrite: []`), and compute still does not bound `units_added` by the units left. On task 1 the bound is exactly non-binding (see `1.md` revision_2) | **closed as a rule/compute gap; residual observation O-5′** (inherited base cap not implemented; no consequence on either world) |
| O-6 | state_gate `gate` names a field | unchanged (as the reworker declared) | open observation |
| O-7 | "same therapy discipline" ill-defined for non-therapy classes | sentence F now "…no other approval of the member in the same class and, for therapy, the same therapy discipline stands approved…"; `condition` updated to "same variant_name and, for therapy, the same therapy_discipline"; `policy_source` verbatim in rule | **closed** |
| O-8 | `cross_difficulty: care/appeal` labels | every care/appeal factor now `cross_difficulty: null` (appeal_holdback, discharge_session_holdback, step_down_addition, gathering_days, appeal_addition, risk_cut, hand_off_holdback, delivery_weeks, weekly_rate, risk_addition, remaining_units_deduction, grievance_addition); each task still has plan/pcp/ride-tagged factors reading seeded rows | **closed** |
| O-9 | degenerate weekly_rate for cap-0 classes | new sentence (rule line 2578 and baseline.rule) "In a class that sets no weekly frequency cap, the units an extension request asks for are the class's extension allotment."; compute `result: P('extension_max_units') if P('weekly_frequency_cap') == 0 else …`; `baseline.params` gains `extension_max_units` | **closed** |
| O-10 | realism of several additions | unchanged | open observation |

### re-derived charter-global checks (on hash `fc7fae82…`)
- **policy_conflict_scan:** the seven subjects, target tools and owners are unchanged. The O-3 overlap is gone. There are no new overlaps between policies.
- **rule_compute_equivalence:** swept every changed binding (`toc_standard`, `xr_deduct_halves`, `xr_deduction`, cap-0 `result`, `ex_weeks_to_end`, `ex_deduction`) against its basis quotation and back. All are equivalent. Unchanged policies carry forward (their rule/compute text is identical to round 1 apart from the added expiry/void scope sentences, which bind no quantity).
- **prerequisite_graph / prerequisite_sentences:** edges A–E identical. Edge F's sentence and condition are reworded as above; the connective is "not … until"; it is still state form, still names no tool or id, is still verbatim in the rule, and still has exactly one resolving write (void). Graph acyclic. PASS.
- **override_declarations:** F-1 closed. The new void sentence narrows voiding to approvals not yet ended; base `auth_void_withdraw` ("The member may have an approval voided when the service will not be used") permits voiding only from `approved`, and base lifecycle expires approvals at end date. The two are compatible, so there is no undeclared override. All other conclusions carry forward.
- **factor_ladders:** counts are now expiry 3P/1M, TOC 5P/1M, review extension 5P/1M, void 3P/1M, carryover 3P/1M, member extension request 5P/1M, extension units 5P/1M. Every ladder has 3 tiers, each factor's baseline equals its fall-through, and each label is honest (F-2 closed). Cross-difficulty tags now name only plan, pcp and ride.

### new observations (no red light)
- **O-11:** the expiry sentence "owes this expiry release whatever its status shows" reads literally over a *voided* approval whose end date later passes (voids already release; the held-back units would then be released again by an expiry entry). Combined with edge A ("every earlier approval … whose end date has passed carries an expiry release entry"), a TOC request built after such a void would wait on an expiry entry on the voided row. Neither world has a voided approval with a passed end date, so there is no scored consequence.
- **O-12:** typo in `auth_ext_member_extension_request.rule` and its `compute_basis.result`: "…divided by two, rounded down,, and three additions…" (double comma). Cosmetic.
- **O-13:** task 1 `design_rationale` PERSONA card still says the persona "volunteers … that he moved", while the reworked `user_scenario` says "You do not bring up the move or name any clinic unless the agent asks". This is a stale author description of the persona; it supports no relationship and the persona itself is the stricter one.

### closing_checklist (revision_2)
| item | status |
| --- | --- |
| one audit file per task plus this file; revision_2 appended in each; round-1 text untouched | done |
| every comparison PASS | task 0 PASS, task 1 PASS (see revision_2 of each file) |
| extended policies fully covered; scopes pairwise disjoint | unchanged `charter_scope`: task 0 {expiry_release, transition_units, member_review_extension}, task 1 {void_release, provider_carryover, member_extension_request, extension_units} |
| task tools and GT closed; uuid8s independent and frozen | unchanged module; GT writes use exactly the claimed tools |
| trees: 1–3 prerequisite problems, ≥ max(n−1,1) value_input, ≥ 1 owner=user, acyclic | task 0 n=2 / 1 value_input / user root; task 1 n=3 / 2 value_input into root / user extension request; whole graph acyclic |
| every computation: self-sufficient baseline, 4–6 factors, ≥ 2 parameter and ≥ 1 honest method; per task ≥ 1 multi-source and ≥ 1 cross-difficulty; every factor bears weight; fall-back ≠ gold | holds for all 7 computations (figures in the task files) |
| instantiation-stage gates re-run on the final form | coordinator snapshot after the rework (brief_auth_r2.md): 7/7 green |

The difficulty passes the source-layer audit in revision 2. Open observations: O-5′, O-6, O-10, O-11, O-12, O-13, and 0.md observation 3.
