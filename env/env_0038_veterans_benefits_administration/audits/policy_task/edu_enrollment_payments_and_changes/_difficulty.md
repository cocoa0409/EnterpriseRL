# Policy-task audit — edu_enrollment_payments_and_changes / charter-global

## charter_global_frozen

- Auditor: erl-task-policy-audit (independent of the instantiating agent), revision 1.
- Freeze time: 2026-10-06T03:31:51Z (file mtime; written before any task's GT was revealed; nothing in this section derives from a revealed GT).
- Frozen inputs (sha256, re-checked against the orchestrator's MANIFEST.sha256.txt):
  - `tasks/edu_enrollment_payments_and_changes/edu.extended.yaml` = `81d1b54ba1089cffc0cf123a696e9ba863852ddda1ef1983323cbc86e9976cbe`
  - `tasks/edu_enrollment_payments_and_changes/task_tools.py` = `73fea3eb3be887b7ab05281ef454515351a0dc9390a7ebcb6dcdc8b75416c7a6`
- Read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json` (field enums only), `blueprint/share_tools.py`, `blueprint/products/edu.yaml` (base), `products/comp.yaml` and `products/debt.yaml` (enum/variant lookups only), the extended charter, the tool module, and the DSL evaluator in `skills/erl-task-instantiate/scripts/check_compute.py` (`build_env`: SUM/COUNT/LATEST scoped to the target holding; X* and CFIELD scoped to the customer).
- Masked (not read before the reveal): every task's `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`; no prior audit exists for this difficulty.
- Base copy: every top-level key of the extended file except `extended_policies` is byte-for-byte equal (parsed) to `blueprint/products/edu.yaml` (checked: category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies all equal).
- Entry conditions (Step 0): gate snapshot supplied (`/tmp/erl0038/views/policy_task/edu_enrollment_payments_and_changes/GATES.txt`: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; traceability deferred); masked views with hashes supplied (task_0 `10d41535…`, task_1 `ba5ff59b…`, both re-verified). Entry conditions met.

### policy_conflict_scan

Four extended policies:

| policy | subject | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- | --- |
| edu_ext_verified_rate_of_pursuit | edu_enrollment_verified | verify_enrollment_month_96d675a6 (user) | rate_of_pursuit_pct | [] |
| edu_ext_flat_monthly_release | edu_monthly_benefit_payment | release_monthly_benefit_payment_750f9b6a (agent) | amount | ← verified_rate_of_pursuit (value_input, state) |
| edu_ext_amended_entitlement_restoration | edu_entitlement_restored | restore_amended_entitlement_47573840 (agent) | days | [] |
| edu_ext_post911_election_entitlement | edu_benefit_relinquished | elect_post911_in_place_of_chapter_2e090e13 (user) | post911_entitlement_days | ← amended_entitlement_restoration (value_input, state) |

- Overlapping subjects: none between extended policies (four distinct event types). Overlaps with base: monthly payment (base `edu_flat_rate_monthly`, `edu_evt_delimiting`, `edu_entitlement_charging`), verification (base `edu_evt_monthly_verification`), restoration (base `edu_evt_enrollment_change`, `edu_entitlement_charging`), election (base `edu_excl_chapter_election`). Conflicts found there are in `override_declarations` below.
- Triggers / time anchors: all four act "today" (`ctx.now()`); verification requires a completed month (base `verification_open_day` 31 → last day of month) — no conflict.
- Eligibility: base `flat_month_verified` (monthly payment only after the month is verified) and base `verify_once` dedup apply; base `charge_active` applies to charges only; there is no base status gate on monthly payments, so an `exhausted` benefit is not barred from a monthly payment by base.
- Terminal states: release creates one `edu_payments` row; restoration creates one ledger row and raises `entitlement_days_remaining`; election flips the chapter to `relinquished` and creates a Chapter 33 benefit. No two policies write the same field.
- Cross-category read boundaries: release reads comp (`comp_decisions`, award `tdiu_granted`/`variant_name`/`effective_date`); restoration reads debt (`debt_transactions`, `debt_requests`); election reads debt (`debt_accounts`). All read-only.
- Scope partition (to be confirmed against `charter_scope` at reveal): the two trees {verify → release} and {restore → elect} are disjoint and together cover all four extended policies. The orchestrator's claimed event_types additionally list `edu_housing_payment`, `edu_books_stipend_payment`, `edu_enrollment_amended`, `edu_school_profile_updated`, which no extended policy has as subject (observation only).

### rule_compute_equivalence

Every compute binding carries a `compute_basis` quotation that is a verbatim substring of its rule (checked mechanically for the prerequisite sentences and baseline sentences; the remaining quotations checked by reading). Sweep back, rule → compute:

- **verified_rate_of_pursuit**: resident cert = latest non-online certification (LATEST by term_start_date, `online_only=False`) ✓; reduction = latest `amendment_reason='reduction'` on the benefit ✓; LDA-inside-term test ✓; mitigating / non-mitigating weighted credits ✓; allowance first/second/none ✓; term measure by weeks (<10 → 6, <15 → 9, else 12) ✓; DL latest online cert, wholly-inside / partial (overlap/term days, both ends) / none ✓; DL measure ✓; sum ×100 once, round half up (`int(x+0.5)`), cap 100 ✓. No invented basis found.
- **flat_monthly_release**: month paid = latest verification_month ✓; verified ROP thresholds 100/75/50/>0 ✓; certified-rate mapping and less-than-half tuition limit (tuition × 30 / term days) ✓; extension tiers ✓ (compute does not check that the decision ending the TT period ends *that* TT grant, only `tt_end > tt_start`; no consequence on the audited worlds); delimiting cut ✓; entitlement cut (granted + restored − charged; last charged day) ✓; first day paid (term start in month / school correction / first of month) ✓; `MX(0, …)` ✓; round once ✓.
  - Gap (observation): rule is silent on a verification that confirms 0 percent; compute pays the certified rate for it (`verified_rop > 0 else certified_rate`). Rule is silent on the month paid when no verification exists; compute uses `NOW` (a full date, not a month start). Neither is reached in task 0.
  - Gap (observation): the rule never cuts the days paid at a term end inside the month (only start, delimiting and entitlement cut-offs) — see override_declarations O4.
- **amended_entitlement_restoration**: latest reduction, its term start/end, LDA, mitigating ✓; term/through/after days ✓; restored measure by weeks ✓; certified credits = SUM of certifications whose term began within 12 months ✓; charge scale ✓ (compute re-uses the constants `half_charge`/`three_quarter_charge` as the threshold fractions 0.5/0.75 — numerically identical to the rule's "half"/"three quarters"); exclusion first/second/none ✓; days_given_back three branches ✓; forgiven waiver/compromise ✓ — compute does not restrict the waiver/compromise credits to an *education* debt as the rule says ("posted on an education debt"); observation, no non-education debt in task 1's world.
  - Wording divergence (finding D5): the rule converts the forgiven amount "at the flat monthly rate of the training time certified"; compute maps it from the *measured* `certified_charge`, not from the certification's recorded `training_time`.
- **post911_election_entitlement**: ledger days left ✓; carried tiers ✓; released days from latest certification and latest charge entry (whole / proportional / none) ✓; held amount tiers (repayment_plan|active with balance → balance; on_hold → original; else 0) ✓; paid monthly rate over 12 months and conversion tiers ✓; round once, cap at full grant ✓.

### action_binding_and_uuids

- `(target_tool, computes)` pairs are four distinct pairs, each claimed by exactly one extended policy; no base policy names a task tool.
- Docstrings: none names another tool, none states a sequence position or uses before/after/first about another action ("Once recorded, the verification shows on…" describes the tool's own effect). None adds a confirmation, review or wait.
- Function bodies: none checks eligibility, verification, status, dates, debt or any prerequisite; each performs its write unconditionally (`ctx.create`/`ctx.update`). The tool layer judges no prerequisite.
- uuid8s `96d675a6`, `750f9b6a`, `47573840`, `2e090e13`: pairwise unrelated (no shared prefix/suffix, no sequence), no reuse. PASS.
- Owners: verification `user` (base: "Verifying is the student's own statement … never given on their behalf") ✓; election `user` (base: "only the beneficiary can make that election") ✓; release and restoration `agent` ✓.

### prerequisite_graph

- Every extended policy has `prerequisite` filled in (two `[]`, two single edges). Each `problem` names another extended policy in this file, never a base policy, never itself. Graph: release → verify; elect → restore. Acyclic.
- `policy_source` of both edges is verbatim in the blocked policy's own rule (mechanically checked).
- Both edges `form: state`, no `fallback_reason` field present (correct for state form).
- `kind: value_input`; `gate` names a real binding: `verified_rop` (release compute) and `ch30_days_left` (election compute). ✓
- `resolved_by` = the depended-on policy's `target_tool` in both edges ✓; effect holds: the verification row's `rate_of_pursuit_pct` and `verification_month` feed `verified_rop`/`month_start`; the restoration row's `days` feeds `restored` → `ch30_days_left` → `carried_days`.
- `condition` vs sentence: release condition adds "for the resident certification … with the rate of pursuit the student confirmed" — consistent with the rule's own definition of the certification and the ROP; election condition is the sentence restated with the event name. Neither strengthened nor weakened in a way that changes the gate. No authoring-viewpoint wording ("in this task", "at the opening").

### prerequisite_sentences

Edge 1 — release ← verification. Sentence: "The monthly benefit for a month is fixed only after the certification carries the student's own verification entry for that month, because the rate of pursuit confirmed there is the one the month is paid at."
- Ordering connective "only after" ✓; waited-on state "the certification carries the student's own verification entry for that month" — record-visible (an `edu_enrollment_verified` row with `source_enrollment_id`/`verification_month`) ✓; no tool, policy id, snake_case token or row id ✓; strength matches the condition ✓.
- Writes in this difficulty that create that state: only `verify_enrollment_month_96d675a6` (the only tool creating `edu_enrollment_verified`). Unique.
- Derivation: sentence → look for the policy whose rule produces "the student's own verification entry" → `edu_ext_verified_rate_of_pursuit` ("A student who verifies a month of enrollment confirms the rate of pursuit read back to them…") → its target tool, owner user. Single reading.
- Depended-on rule does not restate the sentence ✓. Release rule carries no second wording of the dependency; "The month paid is the month covered by the student's most recent verification" and "The rate paid follows the rate of pursuit confirmed on the student's most recent verification" are value definitions, not order statements.
- Base sentence also stating this order: `edu_flat_rate_monthly` "A monthly payment is released only after the student has verified enrollment for that month" (and base `edu_evt_monthly_verification` "payments to the student stop until the missing months are verified"). The extended rule carries its own sentence, so this is an observation only.
- Internal tension (observation): the same rule's tier "a benefit with no verification on file is paid at the rate for the training time certified" describes paying without any verification; it cannot be reached for a month that lacks a verification while older verifications exist, so it opens no second order.

Edge 2 — election ← restoration. Sentence: "The Post-9/11 entitlement credited on an election is not fixed until the relinquished chapter's entitlement ledger carries a restoration entry for every amended certification whose dropped days were charged."
- Connective "not … until" ✓; state = a ledger restoration entry per amended certification — record-visible ✓; no tool/id/snake_case ✓; scope "every amended certification whose dropped days were charged" matches the condition ✓.
- Writes creating the state: only `restore_amended_entitlement_47573840` (only tool creating `edu_entitlement_restored`). Unique.
- Derivation: sentence → policy whose rule gives back entitlement for an amended (reduced) certification → `edu_ext_amended_entitlement_restoration` → its tool, owner agent. Single reading. Restoration rule does not mention the election ✓.
- No undeclared cross-problem order found in any extended rule.

### override_declarations

Swept sentence by sentence over each policy's `base_policy_refs`. "follows" = no conflict on the scored quantity.

**edu_ext_verified_rate_of_pursuit** (`overwrite: []`)
- `edu_evt_monthly_verification`: verify monthly / online-text-phone / student's own statement / once per month / suspension / tuition independent — follows. The extension adds a read-back ROP; the base has no sentence about the quantity, so no conflict.
- `edu_evt_enrollment_change` S1 "the change is effective on the term start date unless VA accepts mitigating circumstances, in which case … last date of attendance" — follows (non-mitigating: excess dropped credits count from term start; mitigating: from LDA).
- `edu_evt_enrollment_change` S1b "the first mitigating_excused_credits credit hours a student ever drops are accepted as mitigating without evidence" — **conflict, undeclared (O3)**: the extended ladder gives a flat `second_drop_excused_credits` = 3 credit allowance to any student with exactly one earlier reduction, regardless of how many credits that earlier reduction used, while the base gives a lifetime first-6-credits exclusion (and the parameter_schema describes it as "one time only"). E.g. a first reduction of 6 credits then a second reduction: base allowance 0, extended 3. Not reached in either audited world (both are first reductions) → charter finding, no task consequence.
- `edu_entitlement_charging`: not about ROP of a verification — follows.

**edu_ext_flat_monthly_release** (`overwrite`: `edu_evt_delimiting` straddle sentence)
- `edu_flat_rate_monthly` S1 "pay the student a flat monthly rate by training time … prorated by the days of the month inside the term" — **conflict, undeclared (O2)**: the extended rate is selected by the verified ROP, explicitly distinguished in the same rule from "the rate for the training time certified" (its fall-through). Where the certification/amendment records a training time below the verified ROP band, base and extended pay different rates. Also the extended days never stop at a term end inside the month (O4).
- `edu_flat_rate_monthly` S2 "less-than-half-time amount never exceeds tuition and fees charged for the month" — follows.
- `edu_flat_rate_monthly` S3 "released only after the student has verified" — follows.
- `edu_excl_chapter_election` — follows (no concurrent payment).
- `edu_evt_delimiting` S1 "A benefit with a delimiting date pays nothing for training after that date" and S3 "The delimiting date of Chapter 30 runs delimiting_years years from the last release from active duty" — **conflict, undeclared (O1)**: the extended rule moves the delimiting date later by a total-disability extension and pays training after the recorded delimiting date; only S4 ("A term that straddles the delimiting date is paid only through that date") is named in `overwrite`. For a term that begins after the recorded delimiting date (no straddle of the recorded date), S1 still governs under the base and pays nothing.
- `edu_entitlement_charging` "a flat-rate chapter stops paying on the day entitlement runs out" — follows (and is restated by the `entitlement_stop_day` factor; see factor_ladders).

**edu_ext_amended_entitlement_restoration** (`overwrite`: `edu_evt_enrollment_change` "Entitlement charged for days no longer certified is restored")
- Declared override: forgiven overpayment days taken off. Merged semantics unique.
- `edu_evt_enrollment_change` S1b (first 6 credits ever) — **same undeclared conflict O3** via `restoration_exclusion_left` (second reduction → 3).
- `edu_entitlement_charging` "under the training_time basis each day is charged at 1 … 0.75 … 0.5 … 0.25" — scale followed; but the extended rule decides the training time by its own credits-over-term-length measurement, while certification records carry a `training_time` field. Where the two differ (task 1's world), base-scale-on-the-record and the extended measurement disagree; recorded as D5 and demonstrated in task 1's file.

**edu_ext_post911_election_entitlement** (`overwrite`: `edu_excl_chapter_election` "receives Post-9/11 entitlement equal to the Chapter 30 months remaining at the election")
- Declared override replaced by carried + released − held. Merged semantics unique.
- "relinquishes that chapter irrevocably, and only the beneficiary can make that election" — followed (user tool).
- `edu_entitlement_charging` — not contradicted.
- `edu_agg_combined_cap` (48 months across chapters) — not in `base_policy_refs`; the extended "never more than the full grant" does not conflict.

### factor_ladders

| policy | factor | label | tiers | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| verified_rate_of_pursuit | reduced_resident_credits | method | 3 | yes (amendment LDA × certification term × mitigating) | — |
| | excused_credit_allowance | parameter | 3 | no | — |
| | resident_term_measure | parameter | 3 | no | — |
| | distance_learning_credits_added | method | 3 | yes (online cert term × resident cert term) | — |
| | distance_learning_term_measure | parameter | 3 | no | — |
| flat_monthly_release | verified_rate_paid | parameter | 5 | no | — |
| | total_disability_extension | parameter | 3 | yes (TT grant × ending decision × award fields) | comp |
| | entitlement_stop_day | method | 3 | yes (ledger balance × last charge date) | — |
| | first_day_paid | method | 3 | yes (cert term start × correction amendment) | — |
| amended_entitlement_restoration | restoration_start_point | method | 3 | no (one amendment row) | — |
| | restoration_exclusion_left | parameter | 3 | no | — |
| | restored_term_measure | parameter | 3 | no | — |
| | certified_daily_charge | parameter | 4 | no | — |
| | remaining_daily_charge | parameter | 5 | no | — |
| | forgiven_overpayment | parameter | 3 | yes (waiver credit × waiver decision) | debt |
| post911_election_entitlement | carried_chapter_days | parameter | 3 | no | — |
| | certified_term_release | method | 3 | no | — |
| | unpaid_overpayment_holdback | parameter | 3 | no (one debt record) | debt |
| | holdback_conversion_rate | parameter | 3 | no | — |

Counts per policy: 5 (3p/2m), 4 (2p/2m), 6 (5p/1m), 4 (3p/1m) — all within 4–6, ≥2 parameter, ≥1 method. Per tree: task tree {verify, release} has multi-source and a comp cross-difficulty factor; tree {restore, elect} has multi-source (`forgiven_overpayment`) and two debt cross-difficulty factors.

Structural checks: `decides` is an input binding (never `result`) for all 19; binding sets disjoint within each policy; every tier is stated in its rule (condition and value/method) and implemented in the `decides` binding; no tier exists only in compute; fall-through of every ladder equals the factor's `baseline`; no two tiers of a ladder select the same value or method as stated.

Labels: `entitlement_stop_day` and `first_day_paid` pick the anchor date of the paid span from different records (ledger end, term start, correction date) — borderline between method and parameter; accepted as method (the business genuinely varies how the paid span is bounded). `certified_term_release` (whole / proportional / none) is an honest method. Observation only.

Realism (judged against VA education practice):
- **R1 — unreal tier (finding F1)**: `excused_credit_allowance` and `restoration_exclusion_left` tier 2 "exactly one earlier reduction → 3 credit hours". VA's six-credit-hour exclusion is a one-time exclusion applied to the first reduction/withdrawal (up to six credits); VA publishes no fixed three-credit allowance for a second reduction, and the charter's own base describes the exclusion as "the first mitigating_excused_credits credit hours a student ever drops" / "one time only". A flat 3 regardless of what the first reduction used is a treatment no VA office applies.
- **R2 — method applied outside its period**: `distance_learning_credits_added` measures overlap against the whole resident term, and the result is the ROP "for a verified month". VA combines concurrent enrollments only for the period in which they overlap; a distance course that starts after the verified month ends does not change that month's training time. Whether the tier fires for a month the DL course does not touch depends on the world → demonstrated per task (task 0).
- **R3 — stamp/base restatement**: `entitlement_stop_day` tier 1 restates base `edu_entitlement_charging` "a flat-rate chapter stops paying on the day entitlement runs out", and the base lifecycle stamps the outcome on the benefit (`status: exhausted`, `closed_date` = "Date entitlement ran out"). Whether that bites depends on the world → per task (task 0).
- Observation: `total_disability_extension` tier 2 ("paid for individual unemployability or rated 100 percent today → days from the award's current effective date to today") — VA extends a Chapter 30 delimiting date only for a period in which a disability actually prevented training, on application; a current total rating by itself is not that test. Not reached in the audited world.
- Observation: `holdback_conversion_rate` fall-through lumps "below half-time paid rate" with "at least full-time" into the full-time rate; unusual but not reached in an absurd way in task 1.
- Observation: `certified_credits` "the certifications whose term began in the twelve months before today" stands in for "the credits certified for that term"; it would sum two terms' credits if two began in the window. Not reached in task 1.
- Observation: `unpaid_overpayment_holdback` (unrecovered Chapter 30 debt keeps entitlement charged) and `forgiven_overpayment` (waived amounts stay charged) are consistent with VA's practice of charging entitlement for waived/unrecovered education overpayments; accepted.

Baselines: verify baseline (certified credits / 12) — self-sufficient. Release baseline — self-sufficient (rate for certified training time; days through 30th or recorded delimiting date; none when before the month). Election baseline (full grant 36 × 30) — self-sufficient. **Restoration baseline (finding F4)**: "the daily charge of the training time certified less the daily charge of the training time remaining … The daily charge of a training time is 1 for full time, as for any term charged day for day, and nothing for training no longer certified." It defines a charge only for full time and for training no longer certified; the training *remaining* after a reduction is still certified and not full time, and the baseline gives it no charge — "day for day" (1), the base `edu_entitlement_charging` scale on its recorded training time, or the factor's declared `remaining_charge: 0` are all available readings. The factor `remaining_daily_charge.baseline = 0` treats still-certified remaining training as "no longer certified". Consequence demonstrated in task 1's file.

### findings

| id | verdict | summary | bears on |
| --- | --- | --- | --- |
| O1 | SOURCE-POLICY RED (demonstrated in task 0) | Delimiting extension displaces base `edu_evt_delimiting` S1 ("pays nothing for training after that date") and S3 (Chapter 30 date = 10 years from release); only S4 (straddle) is declared in `overwrite`. | task 0 |
| O2 | SOURCE-POLICY RED (demonstrated in task 0) | Rate selected by verified ROP displaces base `edu_flat_rate_monthly` "flat monthly rate by training time"; undeclared. | task 0 |
| O3 | observation (no audited world reaches it) | Second-reduction 3-credit allowance contradicts base "first … credit hours a student ever drops"; undeclared in both `edu_ext_verified_rate_of_pursuit` and `edu_ext_amended_entitlement_restoration`. | none demonstrated |
| O4 | observation | Release days never stop at a term end inside the month, against base "prorated by the days of the month inside the term"; undeclared; task 0's term ends 2026-11-30. | none demonstrated |
| D5 | wording root cause of a SOURCE-TASK RED (demonstrated in task 1) | "training time certified" means the certification's recorded `training_time` in the release policy (`res_training_time`) but the measured class in the restoration policy's forgiven-days conversion; with a record that says half_time and a measurement that says three-quarter time, two rates are defensible. | task 1 |
| F1 | SOURCE-FACTOR RED (charter-global, ladder unreal) | Tier "exactly one earlier reduction → 3 credit hours" in `excused_credit_allowance` and `restoration_exclusion_left` is not VA practice and contradicts the base one-time exclusion. | task 0 (verify computation), task 1 (restoration computation) |
| F4 | SOURCE-FACTOR RED (demonstrated in task 1) | Restoration baseline is not self-sufficient for a reduction that leaves training; `remaining_daily_charge.baseline = 0` is not what `baseline.rule` states for still-certified remaining training. | task 1 |
| R2 | per-task | DL credits applied to a month they do not overlap. | task 0 |
| R3 | per-task | Stop-day tier restated by base and stamped on the benefit. | task 0 |

## closing_checklist

Written after both reveals (2026-10-06T03:33:39Z onward). Nothing above this heading was changed by the reveals except the freeze-time line of § charter_global_frozen (accuracy correction of an estimated timestamp).

The difficulty does **not** close: not every task PASSes all four relationships.

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | SOURCE-POLICY RED (O1, O2) | SOURCE-CHAIN RED (persona names the prerequisite) | SOURCE-FACTOR RED (R2, R3, F1) | follows the policy RED (base readings 0.00 / 671.47 remain defensible); otherwise GT = blind derivation |
| 1 | PASS on this world | PASS | SOURCE-FACTOR RED (F4, F5, F1) | SOURCE-TASK RED (D5: 14/560 vs 7/553) |

Checklist status:
- Per-task files `0.md`, `1.md` correspond one-to-one with tasks 0 and 1; `_difficulty.md` alongside; no older revisions exist (revision 1).
- Scope: `charter_scope` task 0 = {verified_rate_of_pursuit, flat_monthly_release}, task 1 = {amended_entitlement_restoration, post911_election_entitlement} — pairwise disjoint, jointly cover all four extended policies; tool sets disjoint; uuid8s independent (§ action_binding_and_uuids).
- Trees: each has 1 prerequisite problem, 1 value_input edge, a user-owned problem, no cycle; the difficulty graph (release→verify, elect→restore) is acyclic.
- Computations: every baseline definite except the restoration baseline (F4); factor counts within bounds; every factor bears weight on its world; realism/stamp defects as listed.
- Blind derivations matched GT on every scored argument in both tasks; the REDs concern the artifacts' consistency, the persona, the ladders/baselines and a second defensible reading — not arithmetic.
- Instantiation-stage gates were not re-run by this audit (the skill does not run them; the supplied snapshot is all green).

## revision_2

### charter_global_frozen (revision 2)

- Auditor: erl-task-policy-audit, re-audit round 2. Written before any round-2 GT was revealed; nothing here derives from a round-2 GT.
- Hashes: `edu.extended.yaml` round 1 `81d1b54b…` → round 2 `576882531cf16c740c7a7d0118a51f691678669f90ec9eaca0101b19961f4b9c` (**changed → every charter-global section re-derived in full below**); `task_tools.py` `73fea3eb3be887b7ab05281ef454515351a0dc9390a7ebcb6dcdc8b75416c7a6` (**unchanged** → § action_binding_and_uuids of revision 1 carried forward by reference: four unique (target_tool, computes) pairs, no ordering/tool names in docstrings, no prerequisite judged in any function body, uuid8s independent). Hashes match the round-2 MANIFEST.
- Base copy still parsed-equal to `blueprint/products/edu.yaml` on every non-extended key.
- Entry conditions: round-2 GATES.txt all green (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING OK; CACHE-DIFF INFO; SCOPE OK); masked views re-verified (task_0 `2028d4f9…`, task_1 `109a0cfc…`). Same masking as round 1.
- The reworker's closure claims were not used as evidence; every item was re-checked against the artifacts.

### policy_conflict_scan (revision 2)

Subjects, owners, target tools, prerequisite edges and cross-category reads are unchanged from revision 1. New content: release now carries a term cut-off and a half-term extension of the entitlement cut-off; verification and restoration replace the 6/3 excused-credit allowance with a once-per-student exclusion; restoration's baseline sentence and forgiven-days conversion are reworded; release declares four more superseded base sentences. No new overlap between extended policies.

### rule_compute_equivalence (revision 2)

Mechanical check (every `compute_basis` quotation verbatim in its own rule): all pass **except** `edu_ext_flat_monthly_release.compute_basis.res_start` and `.res_training_time`, which still quote "the training time certified on the student's resident term certification" — the rule now says "the training time recorded on the student's resident term certification". The meaning (the certification's recorded field) is unchanged and no second conclusion follows, so this is an **observation (new, regression of quotation)**. Same lag in the `verified_rate_paid` ladder: its fall-through `when` still reads "otherwise (no verification on file)" and its value "the rate for the training time certified", while the rule now says "no verification on file, or whose most recent verification confirms 0 percent, … the training time recorded"; the compute (`verified_rop > 0 else certified_rate`) matches the rule; observation.
Sweep of the new sentences:
- verify `excused_allowance`: first reduction ≤ 6 dropped → every credit dropped; first > 6 → 6; otherwise 0 ✓ quoted and implemented.
- release `term_cut` = min(30, day of month of the resident term end) ✓; `entitlement_cut` four branches (more than half the term passed by the last charged day → through min(30, term end); not more than half → last charged day; before month → 0; else 30) ✓; `days_paid` = min of three cut-offs − offset ✓. Round-1 gaps closed: 0-percent verification now stated in the rule; term end now bounds the paid days (O4). Still silent: month paid when no verification exists (compute `NOW`) — unreached, observation carried.
- restoration: baseline "1 a day while any credits are certified, and nothing … once no credits remain" ✓ = factor baseline `remaining_charge: "0 if remaining_credits <= 0 else K('full_charge')"` and `certified_charge: K('full_charge')`; exclusion ✓; forgiven conversion "at the flat monthly rate matching the daily charge of the credits certified worked out above … whatever training time the certification itself records" ✓ = `certified_monthly_rate` (D5 wording closed). Waiver/compromise credits still not restricted to an education debt (observation carried; unreached).
- election: unchanged.

### prerequisite_graph and prerequisite_sentences (revision 2)

Unchanged in substance: both edges, `policy_source` verbatim in the blocked rule (re-checked mechanically), state form, no fallback, value_input gates `verified_rop` / `ch30_days_left` exist, single creating write per state, acyclic; no new cross-problem order sentence in any rule (the new stop-day and term cut-off sentences are internal to the release). PASS.

### override_declarations (revision 2)

- `edu_ext_flat_monthly_release` now declares: `edu_evt_delimiting` straddle sentence, "A benefit with a delimiting date pays nothing for training after that date" (**O1 S1 closed**), "The delimiting date of Chapter 30 runs delimiting_years years from the last release from active duty." (**O1 S3 closed**), `edu_flat_rate_monthly` "Chapter 30, Chapter 35 and Chapter 1606 pay the student a flat monthly rate by training time" (**O2 closed**), and `edu_entitlement_charging` "while a flat-rate chapter stops paying on the day entitlement runs out" (replaced by the half-term extension). Each superseded clause is verbatim in the base rule; each `replaced_by` is verbatim in the extended rule. Merged semantics unique: the extended rule states the full cut-off method. **O4 closed** (term cut-off now stated and implemented; the base proration "days of the month inside the term" is followed).
- `edu_ext_verified_rate_of_pursuit` and `edu_ext_amended_entitlement_restoration`: the one-time exclusion now follows base "the first mitigating_excused_credits credit hours a student ever drops are accepted as mitigating without evidence" (first reduction: up to six credits; any later reduction: none). **O3 closed.** The mitigating branches now read "accepted mitigating circumstances … on the student's evidence", which reconciles the seed's `mitigating_circumstances: false` with the base's evidence-free six-credit acceptance (the exclusion is carried as excused credits) — round-1 mitigating-flag observation closed.
- Restoration baseline sentence "Under the standard measurement a credit load is charged day for day, 1 a day while any credits are certified" sits beside base `edu_entitlement_charging` "under the training_time basis each day is charged at 1 for full time, 0.75 …, 0.5 …, 0.25 …"; in the extended rule it is immediately superseded by "The restored term's daily charges follow its own measurement", so the merged extended semantics are unique; observation only (the baseline is a weaker "standard" than VA's own training-time scale — see factor_ladders).
- `edu_ext_post911_election_entitlement`: unchanged, declared override unique.

### factor_ladders (revision 2)

Counts unchanged: verify 5 (3 parameter / 2 method), release 4 (2 / 2), restoration 6 (5 / 1), election 4 (3 / 1); multi-source and cross-difficulty per tree unchanged (comp; debt ×2). `entitlement_stop_day` now 4 tiers; `remaining_daily_charge` 5 tiers with values 0 / 0.75 / 0.5 / 0.25 / 1 (fall-through = baseline for that input).

- **F1 (round 1) closed**: the flat second-reduction 3-credit tier is gone from both ladders.
- **NEW — F6, padded ladder (SOURCE-FACTOR RED, charter-global)**: `excused_credit_allowance` and `restoration_exclusion_left` now read: tier 1 "first reduction, drops no more than 6 → every credit dropped", tier 2 "first reduction, drops more than 6 → 6", fall-through "otherwise → 0". The allowance is consumed only through `excused_credits = MN(credits_dropped, excused_allowance)` / `excused = MN(MX(0, dropped), exclusion_left)`. Under tier 1, MN(dropped, dropped) = dropped = MN(dropped, 6) because dropped ≤ 6; under tier 2, MN(dropped, 6) = 6. So tiers 1 and 2 are one treatment — VA's one-time exclusion of up to six credits on the first reduction — written as two; substituting tier 2's value (6) into tier 1 leaves every possible outcome unchanged (re-run on both worlds: identical results). The real ladder has two tiers (first reduction → up to 6; otherwise → 0), below the three-tier floor. Striking both factors still leaves verify 4 factors (2 parameter / 2 method) and restoration 5 (4 / 1), so the counts survive; the defect is the ladder itself.
- **R3 (round 1) closed at charter level**: the base "stops paying on the day entitlement runs out" is now superseded and the stop-day tier decision depends on the half-term test (records: term start/end and the last charged day), which no stamp names. The new tier (extension to the end of the term when entitlement runs out after the middle of a term) matches VA's Chapter 30 end-of-term extension practice.
- Restoration baseline (**F4 closed**): `baseline.rule` now yields a definite number (any certified load 1 a day; remaining load 1 a day while any credits remain, 0 when none) and the factor baselines encode exactly that. Realism observation: a "standard measurement" charging 1 a day for any credit load is not VA's Chapter 30 training-time scale; it is the baseline, not a tier, and is superseded inside the rule.
- R2 (DL credits applied to a month they do not overlap): the method text is unchanged (overlap still measured against the whole resident term); whether it bites is a per-world question — see task 0.
- Unchanged, still unreached (observations carried; reworker's "no change needed" accepted on the evidence that no audited world reaches them): `total_disability_extension` tier 2 realism; `holdback_conversion_rate` fall-through lumping; `certified_credits` 12-month window; waiver/compromise credits not restricted to the education debt.

### findings (revision 2)

| id | round-1 verdict | round-2 status |
| --- | --- | --- |
| O1 | SOURCE-POLICY RED | closed (S1, S3 declared) |
| O2 | SOURCE-POLICY RED | closed (declared) |
| O3 | observation | closed (one-time exclusion matches base) |
| O4 | observation | closed (term cut-off) |
| D5 | SOURCE-TASK root cause | closed at charter level (conversion tied to the measured charge "whatever training time the certification itself records") — confirm per task 1 |
| F1 | SOURCE-FACTOR RED | closed |
| F4 | SOURCE-FACTOR RED | closed |
| R2, R3, C1, F5 | per-task | see task files |
| mitigating-flag obs. | observation | closed |
| 0-percent obs. | observation | closed in the rule; ladder `when` text lags (observation) |
| **F6** | — | **NEW SOURCE-FACTOR RED** (padded exclusion ladders, both computations that carry them: task 0 verification, task 1 restoration) |
| quotation lag | — | new observation (`compute_basis` res_start/res_training_time) |

### closing_checklist (revision 2)

Written after the round-2 reveals (2026-10-06T05:57:35Z). The difficulty does **not** close.

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | SOURCE-FACTOR RED (F6) | PASS |
| 1 | PASS | PASS | SOURCE-FACTOR RED (F6) | PASS |

- Every round-1 RED (O1, O2, C1, R2, R3, F1, F4, F5, D5) and the claimed observations (O3, O4, mitigating flag, 0-percent verification) were re-verified against the round-2 artifacts and are closed; the four "no change needed" observations are unchanged and unreached by either world (accepted).
- Open: **F6** (new, charter-global): both excused-credit ladders split the one-time six-credit exclusion into two tiers with one effect, leaving two real tiers.
- New observations: `compute_basis` quotation lag (`res_start`, `res_training_time`) and `verified_rate_paid` fall-through text lag; restoration baseline realism.
- No regression in the tree, prerequisite sentences, tool module (unchanged hash), scope partition (`charter_scope` unchanged and disjoint), or any scored argument (blind derivations equal GT on every argument in both tasks).
- Gates: round-2 snapshot all green as supplied; not re-run by this audit.

## revision_3

### charter_global_frozen (revision 3)

- Re-audit round 3, written before any round-3 GT was revealed; nothing here derives from a round-3 GT. Reworker's claims not used as evidence.
- Hashes: `edu.extended.yaml` round 2 `57688253…` → round 3 `f29232967db8f2c38c0b3c4599d21c1f9d064759f003d02b2dd86cdaeaf2ab2c` (**changed → charter-global sections re-derived**); `task_tools.py` `73fea3eb…` (**unchanged** → revision-1 § action_binding_and_uuids carried forward by reference). Masked views unchanged since round 2 (task_0 `2028d4f9…`, task_1 `109a0cfc…`). GATES.txt all green. Base copy still parsed-equal to `blueprint/products/edu.yaml`.

### What changed (re-read in full)

- Verification: the excused-credit exclusion is now "six semester hours or the equivalent on the resident term's own full-time measure": first reduction on a term measured on 6 credits → `short_term_excused_credits` 3; on 9 credits → `mid_term_excused_credits` 4.5; on the 12-credit standard → `first_drop_excused_credits` 6; earlier reduction on the benefit → 0. Excused credits = credits dropped up to that exclusion.
- Restoration: the same structure (`shortest_session_allowance` 3, `accelerated_session_allowance` 4.5, `first_reduction_allowance` 6, else 0).
- Release: new sentence "When no verification is on file at all, the day of the call stands in for the first day of the month paid."; `compute_basis` quotations now say "training time recorded"; `verified_rate_paid` fall-through reads "otherwise (no verification on file, or the most recent verification confirms 0 percent) → the rate for the training time recorded".
- Election: unchanged.

### rule_compute_equivalence (revision 3)

Every `compute_basis` quotation is verbatim in its own rule (mechanical check, no misses) — **quotation-lag observation closed**. `verified_rate_paid` ladder text now matches the rule — **fall-through wording observation closed**. Month paid with no verification is now stated and matches compute `NOW` — **observation closed** (unreached in either world). New exclusion ladders: each tier quoted and implemented (`excused_allowance`, `exclusion_left` keyed on the term measure the same rule already computes). Still unrestricted to the education debt: waiver/compromise credits (observation, unreached).

### prerequisite_graph / prerequisite_sentences (revision 3)

Unchanged; both `policy_source` sentences verbatim in the blocked rules; state form; single creating write; acyclic. PASS.

### override_declarations (revision 3)

- `edu_ext_flat_monthly_release`: five declared supersessions as in revision 2, verbatim on both sides. No new conflict.
- **NEW — O5, undeclared override (SOURCE-POLICY RED; demonstrated in task 0)**: base `edu_evt_enrollment_change` "the first mitigating_excused_credits credit hours a student ever drops are accepted as mitigating without evidence", with `mitigating_excused_credits = 6` on the Chapter 30 tier (parameter_schema: "Credit hours dropped for the first time that VA excuses as mitigating circumstances without evidence, credit hours (one time only)"). Both `edu_ext_verified_rate_of_pursuit` (`overwrite: []`) and `edu_ext_amended_entitlement_restoration` (overwrite names only the restoration sentence) now excuse 3 or 4.5 credit hours on a first reduction in a short or mid-length term. Where a first reduction drops more than the shortened exclusion, base and extended excuse different numbers of credits. This re-opens what O3 closed in revision 2 (regression).
- Election: unchanged.

### factor_ladders (revision 3)

- **F6 closed in form**: `excused_credit_allowance` and `restoration_exclusion_left` now have four tiers with four distinct values (3 / 4.5 / 6 / 0); because the credits dropped can exceed 3 or 4.5, the tiers produce different outcomes, so no tier is a restatement of another. Each tier beyond the fall-through is a conjunction over distinct records (reduction count on the amendments × term length on the certification) — multi-source.
- **NEW — F7, unreal tier values (SOURCE-FACTOR RED, charter-global)**: VA's one-time exclusion is "up to six semester hours or the equivalent", where the equivalent converts the unit of measure (quarter or clock hours); it is not prorated by the length of a semester-hour term. VA publishes no 3-credit or 4.5-credit exclusion for a short or 12-week term; the charter's own base fixes it at 6 credit hours "one time only". The tiers "first reduction, term measured on 6 credits → 3" and "first reduction, term measured on 9 credits → 4.5" are treatments no VA office applies.
- Counts unchanged and within bounds (verify 5: 3 parameter / 2 method; release 4: 2 / 2; restoration 6: 5 / 1; election 4: 3 / 1); multi-source and cross-difficulty per tree unchanged.
- Observations carried, reworker's "no change needed" re-checked and accepted (no world reaches them; no demonstrable consequence): restoration-baseline realism ("1 a day while any credits are certified", superseded inside the rule); waiver-credit scope; 12-month certification window; conversion-rate fall-through; extension tier 2 realism.

### findings (revision 3)

| id | round-2 status | round-3 status |
| --- | --- | --- |
| F6 | SOURCE-FACTOR RED | closed (distinct, outcome-changing tiers) |
| quotation lag (res_start / res_training_time) | observation | closed |
| verified_rate_paid fall-through text | observation | closed |
| month paid with no verification | observation | closed (new sentence) |
| **O5** | — | **NEW SOURCE-POLICY RED** (undeclared override of base six-credit exclusion; regression of O3) — demonstrated in task 0; no consequence in task 1 |
| **F7** | — | **NEW SOURCE-FACTOR RED** (3 / 4.5 exclusion tiers unreal) — both computations carrying the ladders (task 0 verification, task 1 restoration) |
| restoration-baseline realism, waiver scope, 12-month window, conversion fall-through, extension tier 2 | observation | unchanged, accepted |

### closing_checklist (revision 3)

Written after the round-3 reveals (2026-10-06T06:58:53Z). The difficulty does **not** close.

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | SOURCE-POLICY RED (O5) | PASS | SOURCE-FACTOR RED (F7) | follows O5 (two defensible values of the verification's scored argument) |
| 1 | PASS | PASS | SOURCE-FACTOR RED (F7) | PASS |

- Closed this round (re-verified): F6, the `compute_basis` quotation lag, the `verified_rate_paid` fall-through wording, the no-verification month start.
- Open: **O5** (new; undeclared override of the base six-credit exclusion, regression of O3) and **F7** (new; 3 / 4.5-credit exclusion tiers are not VA practice). Both stem from the F6 rework.
- Accepted as no change needed (unchanged, unreached by either world): restoration-baseline realism, waiver/compromise scope, 12-month window, conversion-rate fall-through, extension tier 2 realism.
- No other regression: trees, prerequisite sentences, tool module (unchanged hash), scope partition, and every other scored argument are unchanged; blind derivations equal GT on every argument in both tasks.
- Gates: round-3 snapshot all green as supplied; not re-run by this audit.

## revision_4

### charter_global_frozen (revision 4)

- Re-audit round 4, written before any round-4 GT was revealed. Reworker's claims not used as evidence.
- Hashes: `edu.extended.yaml` round 3 `f2923296…` → round 4 `41edf4b0966420866cbeb9f3af12bf30ff53f5adab8ebbe9eeee45264fdef2b1` (**changed → charter-global re-derived**); `task_tools.py` `73fea3eb…` (**unchanged** → revision-1 § action_binding_and_uuids carried forward). Masked views unchanged since round 2 (`2028d4f9…`, `109a0cfc…`). GATES.txt all green. Base copy parsed-equal to `blueprint/products/edu.yaml`.

### What changed (re-read)

- Verification: `reduced_resident_credits` ladder is now (1) latest reduction's LDA inside the resident term → remaining + excused credits through the LDA, remaining after; (2) latest reduction belongs to the resident term but its LDA is before the term start → remaining credits for the whole term; (3) otherwise → credits certified. `excused_credit_allowance` is now (1) VA accepted mitigating circumstances on evidence → every credit dropped; (2) not accepted, first reduction ever → credits dropped up to the tier's `mitigating_excused_credits` (base parameter, 6 on Chapter 30); (3) otherwise → 0. The term-length-scaled 3 / 4.5 values and their params are gone.
- Restoration: `restoration_start_point` is now (1) LDA inside its term → through-days at certified − kept, after-days at certified − remaining; (2) no reduction on file → nothing restored; (3) otherwise → every day at certified − remaining. `restoration_exclusion_left` mirrors the new excused ladder (evidence → all; first without evidence → up to `mitigating_excused_credits`; otherwise 0).
- Release and election: no change found (all mechanical checks and recomputations identical to revision 3).

### rule_compute_equivalence (revision 4)

Every `compute_basis` quotation verbatim in its rule (mechanical, no misses); every baseline sentence in its rule; every `policy_source` verbatim. New bindings: `red_term_start` and the three-branch `resident_credits` match the rule's three cases; `excused_allowance` / `exclusion_left` match the rule's three cases and read the base parameter via `P('mitigating_excused_credits')`; `days_given_back` three branches match the rule. No invented basis, no empty promise.

### prerequisite_graph / prerequisite_sentences (revision 4)

Unchanged; PASS.

### override_declarations (revision 4)

- **O5 closed**: the exclusion is now the base's own parameter (`mitigating_excused_credits`, 6 on Chapter 30) applied once on the first reduction without accepted evidence; with accepted evidence every dropped credit takes the LDA; otherwise the change dates from the term start. This is sentence-for-sentence the base `edu_evt_enrollment_change` ("effective on the term start date unless VA accepts mitigating circumstances, in which case … last date of attendance; the first mitigating_excused_credits credit hours a student ever drops are accepted as mitigating without evidence"). **O3 stays closed.**
- Release: five declared supersessions unchanged and verbatim. Restoration and election: declared overrides unchanged and unique.

### factor_ladders (revision 4)

- **F7 closed**: no term-length-scaled exclusion values remain; tier values (all dropped / up to 6 / 0) are VA's treatment (evidence-accepted mitigating circumstances; one-time six-credit exclusion; otherwise from term start).
- **F6 stays closed**: in both exclusion ladders tiers 1 and 2 differ in outcome whenever more than six credits are dropped (all vs six), and both differ from the fall-through; I also confirmed tier 1 is consumed — with the reduction flagged as evidence-accepted on task 0's world, replacing tier 1's value by 0 moves the result (consumed through `excused_credits` in the single LDA-inside branch).
- `reduced_resident_credits`: three real tiers (LDA in term / dropped before the term start / no reduction affecting the term); the second is VA's "reduction before the term begins — effective the term start". Honest method label.
- **NEW — F8, vacuous tier (SOURCE-FACTOR RED, charter-global)**: `restoration_start_point` tier 2 "no reduction is on file → nothing is restored". The policy's own rule opens "When a school reports a reduction of a Chapter 30, Chapter 35 or Chapter 1606 term, VA gives back the entitlement charged for the training no longer certified on the latest reduction reported on the benefit", and the write it scores (`restore_amended_entitlement_47573840` with reason `amended_enrollment`) exists only for a reported reduction; no customer who reaches this write has no reduction on file. The tier divides no customer, so the ladder has two real tiers (LDA inside the term; LDA outside it) — below the three-tier floor. Disclosure: in revisions 1–3 this ladder's fall-through ("when no reduction is on file, every day of the term is restored") was equally vacuous and I did not report it; the defect predates round 4 and was missed by me, not introduced by this rework. Striking the factor leaves restoration with 5 factors (5 parameter / **0 method**) — below the one-`method` floor, so the policy's factor set fails as well.
- Counts as declared: verify 5 (3 parameter / 2 method), release 4 (2 / 2), restoration 6 (5 / 1, see F8), election 4 (3 / 1).
- Standing unreached observations (restoration-baseline realism, waiver/compromise scope, 12-month window, conversion fall-through, extension tier 2 realism): unchanged; accepted as no change needed.

### findings (revision 4)

| id | round-3 status | round-4 status |
| --- | --- | --- |
| O5 | SOURCE-POLICY RED | closed |
| F7 | SOURCE-FACTOR RED | closed |
| F6, O3 | closed | stay closed (re-verified) |
| **F8** | (missed in revisions 1–3) | **SOURCE-FACTOR RED** — vacuous tier in `restoration_start_point`; restoration left with no honest `method` factor — bears on task 1 |

### closing_checklist (revision 4)

Written after the round-4 reveals (2026-10-06T07:20:55Z). The difficulty does **not** close.

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | SOURCE-FACTOR RED (F8) | PASS |

- Closed (re-verified, not on claim): O5, F7. F6 and O3 stay closed. Standing unreached observations accepted as no change needed.
- Open: **F8** — `restoration_start_point`'s "no reduction on file" tier is vacuous for the restoration write; the restoration computation then has no honest `method` factor. Present since revision 1 in the fall-through position and missed by me in revisions 1–3; disclosed, not attributed to this rework.
- Id-valued gold arguments in both tasks replayed: each resolves to an earlier action's output; none depends on a write-minted id.
- No regression: tool module unchanged; trees, prerequisite sentences, scope partition (`charter_scope` disjoint, all four extended policies covered) and every other scored argument unchanged; blind derivations equal GT on every argument in both tasks.
- Gates: round-4 snapshot all green as supplied; not re-run by this audit.

## revision_5

### charter_global_frozen (revision 5)

- Re-audit round 5, written before any round-5 GT was revealed; reworker's claims not used as evidence.
- Hashes: `edu.extended.yaml` round 4 `41edf4b0…` → round 5 `be00e196adc7a864736baef95a559824c78eaeff585f6845c526e0abc253be50` (**changed → charter-global re-derived**); `task_tools.py` `73fea3eb…` unchanged (revision-1 § action_binding_and_uuids carried forward). Views unchanged since round 2. GATES.txt all green. Base copy parsed-equal to `blueprint/products/edu.yaml`.

### What changed (re-read)

- Only `edu_ext_amended_entitlement_restoration`: `restoration_start_point` is now (1) LDA inside the term and the term's charge (charge entries for training begun in the twelve months before today) covers every day at the certified charge → through-days at certified − kept, after-days at certified − remaining; (2) LDA inside the term but the charge ran out before the term end → after-days counted only up to the last day the charge covers (charge ÷ certified daily charge); (3) otherwise (LDA not inside the term) → every day at certified − remaining. New bindings `term_charge`, `covered_days`. The "no reduction on file" tier is gone.
- Verification, release, election: no change found — the verification's `excused_allowance` and `resident_credits` compute strings are byte-identical to revision 4's, all mechanical checks pass identically, and every value and sensitivity recomputes to the revision-4 figures.

### rule_compute_equivalence / prerequisites / overrides (revision 5)

- Every `compute_basis` quotation verbatim in its rule (incl. the new `term_charge`, `covered_days`); baseline sentences in rule; `policy_source` verbatim. `days_given_back` three branches implement the three rule cases, with `MX(0, …)` for "never fewer than none" on the capped after-days.
- Prerequisite graph and sentences unchanged — PASS. Overrides: unchanged and declared; the new "a restoration never giving back days that were never charged" is consistent with base "Entitlement charged for days no longer certified is restored" (as declared-overridden) — no new conflict. O3, O5 stay closed.

### factor_ladders (revision 5)

- **F8 closed**: `restoration_start_point` now has three real tiers — every customer reaching the restoration write has a reported reduction, and can have its LDA inside the term with a full charge, inside the term with a charge that ran out (entitlement exhausted mid-term), or outside the term (dropped before the term began). The cap at the charged days is VA logic (nothing is restored that was never charged). Honest `method`; restoration again has 1 method / 5 parameter factors.
- F6, F7 stay closed (verification and restoration exclusion ladders unchanged since revision 4).
- Observation (new, same family as the standing 12-month-window observation): the term's charge is found as "the charge entries for training that began in the twelve months before today" rather than the entry for the amended certification; it would sum two terms' charges if two began in the window. Unreached in task 1's world (the spring-2027 charge has not begun).
- Standing unreached observations unchanged; accepted.

### findings (revision 5)

| id | round-4 status | round-5 status |
| --- | --- | --- |
| F8 | SOURCE-FACTOR RED | closed |
| F6, F7, O3, O5 | closed | stay closed |
| term-charge 12-month window | — | observation (unreached) |

### closing_checklist (revision 5)

Written after the round-5 reveals (2026-10-06T07:28:30Z). **The difficulty closes at the source layer.**

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

- Per-task files `0.md`, `1.md` correspond one-to-one with the tasks; `_difficulty.md` alongside; revisions 1–5 preserved in order, each comparison section carrying its verdicts; the latest carries PASS for both tasks.
- Coverage and scope: `charter_scope` task 0 = {verified_rate_of_pursuit, flat_monthly_release}, task 1 = {amended_entitlement_restoration, post911_election_entitlement}; pairwise disjoint, jointly covering all four extended policies; tool sets disjoint; uuid8s `96d675a6`, `750f9b6a`, `47573840`, `2e090e13` independent (tool module unchanged since revision 1).
- Trees: each has 1 prerequisite problem, 1 value_input edge, a user-owned problem (verification; election), no cycle; the difficulty graph (release → verify, elect → restore) is acyclic.
- Computations: every one declares a definite baseline different from gold and 4–6 factors (verify 5: 3 p / 2 m; release 4: 2 / 2; restoration 6: 5 / 1; election 4: 3 / 1); every ladder has ≥ 3 real, outcome-distinct tiers stated in its rule; each task has a multi-source factor and a cross-difficulty factor (comp; debt) with seeded evidence; every factor bears weight on its world against an honest baseline.
- Id-valued gold arguments replayed (round 4, actions unchanged since): all resolve to earlier read outputs.
- Remaining observations (no consequence on either world): term-charge and certification 12-month windows; waiver/compromise credits not restricted to the education debt; conversion-rate fall-through; restoration-baseline realism; total-disability-extension tier 2 realism; base verification-order sentence duplicating the extended prerequisite sentence.
- Gates: the round-5 snapshot supplied by the orchestrator is all green (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING OK; CACHE-DIFF INFO; SCOPE OK); traceability deferred to the KB step. This audit did not re-run them.

## revision_6

### charter_global_frozen (revision 6)

- Re-audit round 6, written before any round-6 GT was revealed and before the render-layer audit files (`audits/policy_kb/…`, `audits/runtime_context/…`) were opened; the item ids PS-0 / PS-1 and their one-line descriptions in the brief are the only render-layer input used. Reworker's claims not used as evidence.
- Hashes: `edu.extended.yaml` round 5 `be00e196…` → round 6 `f878e49e2d1ccf619bc7b0cfc01a9c0792994ff1e3b1497ce5ebb83678038c24` (**changed → re-derived**); `task_tools.py` `73fea3eb…` unchanged; views unchanged since round 2. GATES.txt 9/9 green (incl. TRACEABILITY OK). Base copy parsed-equal to `blueprint/products/edu.yaml`.
- Per-policy canonical hashes: verification `984141c2…`, release `3be13305…`, election `08d9d40b…` — identical to round 5 (unchanged); restoration `34c986f1…` → `3258ea8f…` (the only change).

### What changed (restoration only)

1. New rule sentence (timing gate): "The entitlement is given back once the reduced term has ended and its enrollment is final: while the term end carried on the amendment is today or a later day, nothing is given back yet and no restoration entry is booked for that term." Compute: `result = 0 if (red_count == 0 or DAYS(red_end, NOW) <= 0) else …`; `compute_basis.result` quotes the sentence verbatim.
2. New rule sentence (entry period): "The restoration entry records as its first day of training the term start when the days through the last date of attendance are restored at a difference above none, or when the last date of attendance is not inside the term, and otherwise the day after the last date of attendance; it records as its last day of training the term end, or, when the term's charge ran out before the term end, the last day that charge covers, counting the term start as the first day covered."
- Everything else in the restoration (ladders, baseline, overrides, factors) is unchanged from revision 5.

### Checks (revision 6)

- rule ↔ compute: every `compute_basis` quotation verbatim; the gate is implemented; the period sentence governs tool arguments (`charge_period_start`/`charge_period_end`) that are not a compute output — stated in the rule, so derivable; no invented basis.
- prerequisites: graph and sentences unchanged — PASS. The timing gate is a condition on the restoration itself, not a cross-problem order.
- overrides: the gate and the period sentence add timing/recording detail to the declared-overridden base "Entitlement charged for days no longer certified is restored"; base states no timing, so no conflict. O3, O5 stay closed.
- factors: unchanged; F6, F7, F8 stay closed. The gate is not a factor tier (it decides whether a write is due, not a value).
- realism: holding an amended term's restoration until the term has ended and the enrollment is final is a plausible processing rule (VA finalises an amended enrollment period before adjusting the entitlement charge); accepted.

### Disclosure — two source-layer misses in my revisions 1–5

- **PS-0** (restoration due in task 0's world but absent from gold): under the revision-1…5 charters, task 0's world (`6514c202`, a reported reduction of the Chapter 30 term `cd1da4c7` whose days were charged, `7f7a3ecc`) met the restoration policy's `state_due` trigger, and the persona's "you are fine with the representative doing whatever they need to do on their end" authorised it. Recomputed on the revision-5 charter, that restoration would have given back days (the reduced 12-week term at a non-zero charge difference), leaving entitlement on the ledger and moving the release's entitlement cut-off off the last charged day — i.e. both an out-of-scope gold write and a changed scored amount. I walked only the trees each task claimed and never checked the sibling policy's trigger against each world. Missed; reported now.
- **PS-1** (task 1's `charge_period_start` defined by no source sentence): in revision 1 I noted "The rule never states what period a restoration entry carries" and treated it as an observation; it was a scored argument with no defining sentence, i.e. a unique-solution defect. Under-classified; reported now.

### findings (revision 6)

| id | status |
| --- | --- |
| PS-0 | closed by the timing gate — verified per task 0 (term end 2026-11-30 is after today → nothing due, no entry booked) |
| PS-1 | closed by the period sentence — verified per task 1 |
| F6, F7, F8, O3, O5 | stay closed (policies unchanged except the two sentences) |
| N-1 / N-2 | render-layer items, not part of this audit's four relationships; not assessed here |

### closing_checklist (revision 6)

Written after the round-6 reveals (2026-10-06T10:08:03Z). **The difficulty closes at the source layer.**

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

- PS-0 and PS-1 closed (verified on each world, not on claim); F6, F7, F8, O3, O5 stay closed; verification, release and election policies byte-identical to round 5.
- Added to the checklist from the PS-0 lesson: for each task, every `state_due` / on-request policy of the charter was checked against that task's world for being due outside its gold — none is (task 0: restoration gated by term end, no unverified complete month, no debt to establish; task 1: all months verified and paid, debt already established, single reduction restored in gold).
- Scope, trees, factor counts, baselines, cross-difficulty evidence and id-argument replay as in revision 5's checklist.
- Remaining observations (no consequence on either world as gold stands): term-charge and certification 12-month windows (they would have mis-summed task 0's online certification had the restoration been due — it is not); waiver/compromise scope; conversion-rate fall-through; restoration-baseline realism; extension tier 2 realism; base verification-order sentence duplication. N-1 / N-2 are render-layer items outside this audit.
- Gates: round-6 snapshot 9/9 green as supplied (incl. TRACEABILITY OK); not re-run by this audit.
