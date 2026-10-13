# Policy-task audit — insured_plan_authorizations_and_balances / charter-global

## charter_global_frozen

- Freeze time: 2026-10-05T05:40Z (written before any task's GT was revealed). Auditor: independent erl-task-policy-audit run (Claude Opus 5.5); not the instantiating agent.
- Frozen inputs (sha256, re-checked against the source files on disk at the start of the audit, identical):
  - `plan.extended.yaml` ae5aaba08bb4a9cf709f11b23278e24eaad0b4c2bd5b6ca01cb20abe7a23b849
  - `task_tools.py` bd2438c18b7d1b0a2f500f106f464e80cbab43782e289ac9bbc9d0695e468898
- Read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/plan.yaml` (base), and the cross-category charters `series.yaml`, `membership.yaml`, `payplan.yaml` (only their bindings, accounts, events and variant parameters that the extended compute reads). Masked views `/tmp/erl0032_views/insured_plan_authorizations_and_balances/{task0,task1}.visible.json` (frozen_time, user_scenario, initial_state only).
- Masked and unread at this freeze: every task's `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`; no other audit directory; no other scenario.
- Base copy: lines 1-866 of `plan.extended.yaml` are byte-identical to `blueprint/products/plan.yaml` (`diff` gives only the trailing blank line 867). Verbatim compatibility holds.
- Recomputation aid: a temporary script outside the repo evaluated each policy's `compute` with `skills/erl-task-instantiate/scripts/check_compute.py:build_env` on the visible seeds; every figure quoted in the task files was also derived by hand. The script has been deleted.

### Entry conditions (Step 0)

Supplied with the brief, cited not re-run: check_extended EXTENDED OK, check_task_tools TASK TOOL CONTRACT OK, replay_tasks REPLAY OK, check_solvability SOLVABILITY OK, check_compute COMPUTE OK, check_grounding GROUNDING OK, check_cross_fire SCOPE OK; blueprint gates BLUEPRINT OK, SHARE TOOLS OK, VALID. Masked views and their hashes were supplied and verified. `check_traceability` is deferred by the brief because the KB is not yet rendered; recorded here as an open entry item, not as a lowered standard (it does not bear on the four relationships audited here).

### policy_conflict_scan

Seven extended policies, each bound to one write tool:

| policy | subject / target_tool | computes | prerequisite |
| --- | --- | --- | --- |
| plan_ext_coinsurance_correction | plan_patient_adjustment / correct_overposted_coinsurance_fd44d809 (agent) | amount | [] |
| plan_ext_noncovered_visit_charge | plan_patient_charge_posted / post_noncovered_visit_charge_a3bfc726 (agent) | amount | [] |
| plan_ext_credit_refund | plan_patient_refund / issue_credit_refund_cc5fc5ad (agent) | amount | coinsurance_correction (value_input), noncovered_visit_charge (value_input) |
| plan_ext_previsit_payment | plan_patient_payment / pay_previsit_amount_3bf14ac0 (user) | amount | credit_refund (state_gate) |
| plan_ext_retro_authorization | plan_auth_requested(retro) / submit_retro_authorization_d347b3c8 (agent) | requested_visits | [] |
| plan_ext_auth_extension | plan_auth_requested(extension) / submit_auth_extension_019a16d0 (agent) | requested_visits | [] |
| plan_ext_noncovered_waiver | plan_waiver_signed / sign_noncovered_waiver_5d672975 (user) | visit_date | retro_authorization (value_input), auth_extension (state_gate) |

Overlap scan:
- Subjects: retro and extension share `plan_auth_requested` but split by `auth_kind` (tool writes retro vs extension); noncovered_visit_charge shares `plan_patient_charge_posted` with base TOS collection but only for `non_covered_service`; refund and previsit share base `plan_evt_payment_application` but write different event types. No two extended policies write the same (event, kind).
- Triggers / eligibility: all extended policies inherit the base status gates (charges/payments on a not-closed plan; auth requests on intake/active/on_hold; retro window; waiver before the non-covered visit). No extended rule weakens one.
- Time anchors: retro counts days from "today less the retroactive window days", matching base `retro_request_window` (day zero = visit date, inclusive). Refund holds count days from payment receipt (day zero). No conflicts found.
- Terminal states: none of the seven changes `care_plans.status`; tools only move `patient_due_balance` in step with the ledger entry they book.
- Cross-category reads: series (noncovered charge, refund, previsit, retro, extension, waiver), membership (noncovered charge), payplan (previsit). All are reads; no extended policy writes another category.
- One conflict with a base clause on a scored quantity was found: see findings F-D1 (plan_ext_previsit_payment vs base plan_evt_time_of_service_collection).
- Scope partition (derived from the prerequisite graph, before reveal): the graph has exactly two connected components, {previsit <- refund <- (coinsurance_correction, noncovered_visit_charge)} and {waiver <- (retro, extension)}. With M=2 and one tree per task, these two components are mutually exclusive and jointly cover all seven policies. Whether each task claims exactly one component is compared against `charter_scope` after reveal.

### rule_compute_equivalence

Check 2, policy by policy. Every compute binding carries a `compute_basis` quotation that is a verbatim sentence of its rule; every ladder tier in `factors[].ladder` is a rule sentence and a branch of the `decides` binding. Divergences found:

- plan_ext_coinsurance_correction: all bindings match (most-recent coinsurance charge by posting date; reviewed visit by its date of service; prorate when units exceed `max_timed_units_per_visit`; deductible charge, else estimate, else 0; copay charge, else copay on file, only where the tier collects copay at TOS; office-visit component 45.00 / whole allowed / 0; one subtraction, floor 0, coinsurance % applied once, half-up to the cent). No invented basis, no empty promise.
- plan_ext_noncovered_visit_charge: matches (slot length <=37 or telehealth -> 88.00; >=53 in-clinic -> 156.00; else tier self-pay rate; minutes delivered = slot - minutes late within grace where the series shortens late visits / telehealth units x 15 / slot; CMS whole-unit ratio vs AMA minutes ratio, 4 dp, evaluations in full; membership active pct / frozen pct x 50% / 0; credit copay payments else estimate payments; one rounding at the end). Note: `minutes_late` is an XLATEST over all of the customer's series by `appointment_date`, not limited to the plan's series (observation O9; not hit in either world).
- plan_ext_credit_refund: matches (ledger credit floor 0; 1-month vs 2-month pending window keyed on `credit_refund_days <= 30`; overdue visits 1<=months<3, not evaluations, no coinsurance/non-covered charge, 1-2 -> 20.00 each, >=3 -> whole credit; check < 10 days else ACH < 5 days; overdue series fee (> fee_due_days) else small credit <= 10.00; returned payment: card within window, else latest check, else latest payment). `unposted_overdue_visits` subtracts counts of charges rather than counting distinct visits (observation O9; equal in task 0's world).
- plan_ext_previsit_payment: one divergence — rule tier 1 of the payment-plan cap requires "an active Patient Payment Plan whose most recent installment payment was received on or before that installment's due date"; compute `estimate_cap` takes tier 1 whenever status is active and `paid_late == 0`, which includes an active plan with no installment yet (rule: fall-through). Observation O3: not hit in task 0 (an on-time installment exists). `compute_basis` of `last_visit_units` and `last_visit_allowed` quotes the baseline sentence rather than the ladder sentence (observation O2).
- plan_ext_retro_authorization: matches. `compute_basis.planned` quotes the baseline sentence ("the payer program's weekly visit maximum") while the expression multiplies by `per_week` (the plan's frequency); the ladder sentence is under `planned_visits` and `per_week`, so the rule carries the implemented sentence (observation O2). `latest_attended` reads the customer's insurance-funded attendances across all series (O9).
- plan_ext_auth_extension: matches; same `compute_basis.planned` labelling as retro (O2).
- plan_ext_noncovered_waiver: matches. `first_booked` is an XLATEST over booking batches by event_date (latest batch's first appointment, not the series' first booking) — equal when one batch exists (O9).

No rule tier is absent from compute and no compute branch is absent from the rule.

### action_binding_and_uuids

- `(target_tool, computes)` pairs are pairwise distinct (table above); each tool is claimed by exactly one policy.
- Docstrings: each describes one atomic write; none names another tool, none states a position in a sequence. Business timing words that occur ("ahead of a visit", "until the day's visit is posted", "can be billed once the payer approves it", "covers no visit dated before that first date") describe real-world timing of the booked entry, not tool order. `submit_auth_extension_019a16d0`'s `visit_date` arg mentions "a retroactive request" to say an extension passes "" (observation O8; no tool name, no order).
- No tool checks eligibility, status, prerequisites or amounts (module docstring and bodies: each body does find -> create one row -> update `patient_due_balance` where it is a money entry -> return).
- uuid8s: fd44d809, a3bfc726, cc5fc5ad, 3bf14ac0, d347b3c8, 019a16d0, 5d672975 — seven distinct values, no shared prefix or tail, no arithmetic sequence. Pass.

### prerequisite_graph

- `prerequisite` is filled on all seven policies (`[]` on four).
- Edges: refund -> coinsurance_correction (value_input, gate `adjustments_total`), refund -> noncovered_visit_charge (value_input, gate `charges_total`), previsit -> refund (state_gate, gate `care_plan_events.event_type`), waiver -> retro (value_input, gate `retro_asked`), waiver -> extension (state_gate, gate `care_plan_events.auth_kind`). Every `problem` is an extended id of this file, none a base policy or itself; the graph is acyclic (two trees of depth 2 and 1).
- `policy_source` of each edge is verbatim in the blocked policy's own rule (checked by string match). All `form: state`; no `fallback_reason` (correct for state form).
- value_input gates exist as compute bindings (`adjustments_total`, `charges_total` in refund; `retro_asked` in waiver). state_gate `gate` values are column names (`care_plan_events.event_type`, `care_plan_events.auth_kind`) rather than eligibility-gate ids; neither policy declares an `eligibility` block, so the gate lives only in the prerequisite sentence (observation O1; no consequence: the sentence is in the rule).
- `resolved_by` equals the depended-on policy's `target_tool` on all five edges; each `effect` is what that tool's row does to the blocked computation or gate.
- `condition` strength vs sentence: equal on all five (closed sets named by kind: "every coinsurance charge ... higher than the share its EOB supports", "each visit ... ran past the visit limit under a signed waiver", "each discharged plan ... whose ledger shows a credit", "every visit attended without authorization within the payer's retroactive window", "an extension request submitted since its current authorization was approved"). No authoring-viewpoint phrasing.

### prerequisite_sentences

Four-point test, per edge:

1. refund <- coinsurance_correction: "The refundable credit is fixed only after every coinsurance charge on the plan that is higher than the share its explanation of benefits supports carries a billing error correction." Connective "only after"; waited-on state = a coinsurance charge carrying a billing error correction (record-visible: `plan_patient_adjustment` `billing_error_correction` with `source_event_id` = the charge); no tool, id or snake_case. Exactly one write of the difficulty books a billing_error_correction (`correct_overposted_coinsurance_fd44d809`). Derivation: sentence -> find coinsurance charges above their supported share -> the coinsurance-correction rule defines the supported share and books the correction -> one reading.
2. refund <- noncovered_visit_charge: "The refundable credit is not worked out until each visit on the plan that ran past the payer's visit limit under a signed waiver carries its non-covered service charge." Connective "not ... until"; state = non_covered_service charge for that visit date; one write books it (`post_noncovered_visit_charge_a3bfc726`). One reading.
3. previsit <- refund: "A pre-visit amount is not taken from a patient until each discharged plan of care of that patient whose ledger shows a credit carries a refund issued since its discharge." Connective "not ... until"; state = a refund entry dated on/after discharge on a credit-bearing discharged plan; one write (`issue_credit_refund_cc5fc5ad`). One reading.
4. waiver <- retro: "The first date of service a waiver covers is fixed only after every visit attended without authorization within the payer's retroactive window carries a retroactive authorization request." Connective "only after"; state = retro request covering the visits; one write (`submit_retro_authorization_d347b3c8`). One reading.
5. waiver <- extension: "A waiver is not signed until the plan carries an extension request submitted since its current authorization was approved." Connective "not ... until"; state = an extension request dated on/after the current approval; one write (`submit_auth_extension_019a16d0`). One reading.

The depended-on rules do not restate any of these sentences. The waiver rule's value text ("Appointments attended on the active series without a billed visit count against the limit only through a retroactive request ...") describes how the computation reads retro rows; it names no tool or policy and adds no second ordering (recorded as observation O4b for completeness). No base sentence grounds any declared edge.

Cross-problem orders stated in rules that ground no declared edge: plan_ext_noncovered_visit_charge's rule charges "a visit ... rendered under a waiver signed before that visit" — a dependency on the waiver policy's write, inherited from base `waiver_before_noncovered_visit`. It is a real-world precondition on a past visit (cannot be resolved in-call) and grounds no edge; in neither task world is a waiver write needed for a charge. Observation O4.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry:

- plan_ext_coinsurance_correction (refs balance_adjustments, TOS collection, visit_authorization; overwrite []): base "A charge posted above what the payer's explanation of benefits or the benefits on file support is corrected by a billing_error_correction for the excess" — followed; the extended rule defines "supported". Base TOS coinsurance-after-EOB sentence posts what the EOB shows; it fixes no coinsurance formula the extended contradicts. Base "Timed units are ... capped at max_timed_units_per_visit" — followed (prorating to the cap). No undeclared override.
- plan_ext_noncovered_visit_charge (refs benefit_visit_limit, TOS collection): "the patient is then charged self_pay_visit_rate as a non_covered_service charge" — declared superseded. Waiver-before-visit, tier-allows, not-against-authorization and "A non_covered_service charge is posted only under plan_agg_benefit_visit_limit" — followed. No undeclared override.
- plan_ext_credit_refund (refs payment_application, TOS collection): "any remaining credit is refunded within credit_refund_days ..." — declared superseded ("less the holds"). Credit offset to other open charges on the same plan — followed (the ledger nets them). Card-within-window / check otherwise; "A refund never exceeds the payment it returns" — followed. No undeclared override.
- plan_ext_previsit_payment (refs payment_application, TOS collection; overwrite []): "applied to the oldest open charge" — followed. Base TOS: "Where collect_deductible_estimate_at_tos is true and deductible remains on file, a deductible_estimate charge of the lower of the visit's allowed amount, the deductible remaining and tos_deductible_estimate_cap is posted" and "Where coinsurance_billed_after_eob is true, the coinsurance ... [is] posted ... after the explanation of benefits arrives" — the extended "deductible part of the coming visit" is the same lower-of-three with its cap replaced by the payment-plan standing (75.00 / full expected allowed) and its deductible reconciled from the ledger, and the extended adds a coinsurance share collected before the visit. Neither change is named in `overwrite`. **Undeclared override — finding F-D1.**
- plan_ext_retro_authorization (refs authorization_requests, visit_authorization): window sentence followed; weekly maximum respected (series frequency <= tier max). No override.
- plan_ext_auth_extension (same refs): trigger/lead-day sentences followed; base fixes no requested-visit count. No override.
- plan_ext_noncovered_waiver (refs benefit_visit_limit, authorization_requests, visit_authorization): "so the visits used are benefit_visits_used_elsewhere plus plan_msr_dos_visits_cy" — declared superseded, scoped by its replacement to "the visits counted against the visit limit ahead of a waiver"; the base coverage sentence ("A visit whose date of service would make the visits used exceed the limit is not covered") keeps the base count for coverage decisions. The tier's waiver form (`non_covered_waiver_form`) — followed. No undeclared override.

Disguised forms: no anonymous intermediate, no 0/1 multiplier and no dropped base branch found beyond F-D1.

### factor_ladders

| policy | factor | label | tiers | multi-source tier(s) | cross_difficulty | baseline == fall-through |
| --- | --- | --- | --- | --- | --- | --- |
| coinsurance_correction | unit_maximum_base | method | 3 | yes (visit kind/units + tier param) | - | yes |
| | deductible_taken_first | parameter | 3 | no (two charge rows of one visit) | - | yes |
| | copay_taken_first | parameter | 3 | yes (tier param + charge row) | - | yes |
| | office_visit_component | parameter | 3 | no | - | yes |
| noncovered_visit_charge | slot_rate | parameter | 3 | yes (visit kind + series format) | series | yes |
| | minutes_delivered | method | 3 | yes (visit kind + series event + series params) | series | yes |
| | time_ratio | method | 3 | yes (tier param + visit kind) | - | yes |
| | member_pricing | parameter | 3 | no | membership | yes |
| | time_of_service_credit | parameter | 3 | yes (charge + payment rows) | - | yes |
| credit_refund | pending_eob_hold | method | 3 | yes (two tier params) | - | yes |
| | overdue_eob_hold | parameter | 3 | yes (visit + charge rows + date) | - | yes |
| | uncleared_funds | parameter | 3 | yes (payment method + date) | - | yes |
| | other_hold | parameter | 3 | yes (series fee balance + fee event date + series param) | series | yes |
| | returned_payment | method | 3 | yes (payment method + date + tier param) | - | yes |
| previsit_payment | expected_units | method | 3 | no | series | yes |
| | allowed_per_unit | method | 3 | no | - | yes |
| | deductible_still_to_meet | method | 3 | no | - | yes |
| | payment_plan_cap | parameter | 3 | yes (payplan status + installment dates) | payplan | yes |
| | share_beyond_deductible | method | 3 | yes (deductible vs allowed + coinsurance on file + copay rows) | - | yes |
| | carried_balance | parameter | 3 | yes (charge count + ledger) | - | yes |
| retro_authorization | gap_start | method | 3 | yes (draws vs approvals) | - | yes |
| | gap_end | method | 3 | yes (approval id + start date) | - | yes |
| | retro_window | method | 3 | yes (tier param + gap + series attendance) | - | yes |
| | gap_frequency | parameter | 3 | no | series | yes |
| | already_asked_retroactively | parameter | 3 | no | - | yes |
| auth_extension | period_start | method | 3 | yes (auth span + undrawn + series start) | series | yes |
| | period_end | method | 3 | no | series | yes |
| | planned_frequency | parameter | 3 | no | series | yes |
| | visits_not_yet_drawn | parameter | 3 | no | - | yes |
| | visits_still_to_draw | parameter | 3 | yes (series end vs auth end) | series | yes |
| noncovered_waiver | unbilled_appointments | parameter | 3 | yes (retro requests vs retro approvals) | - (reads series) | yes |
| | visits_outside_series | parameter | 3 | no | - | yes |
| | appointments_booked_ahead | parameter | 3 | yes (series history vs plan billing) | series | yes |
| | next_series_opening | method | 3 | yes (reschedule + booking + series start) | series | yes |

Counts as declared: every policy has 4-6 factors, >=2 parameter and >=1 method; every ladder has three pairwise-disjoint tiers stated in full in the rule and implemented in compute; no two tiers of one ladder select the same value or method as written; `decides` is never `result`; binding sets are disjoint. Each tree has cross-difficulty factors (tree 1: series, membership, payplan; tree 2: series).

Structural defects (independent of any world):
- `plan_ext_noncovered_waiver.visits_outside_series`: the tier condition "where an evaluation has been billed on the plan" holds of every plan that can reach this write — base event `plan_opened` "triggers: - event: plan:plan_visit_billed map: {visit_kind: evaluation}" and base `plan_visit_authorization` "The initial evaluation is billed in intake". The ladder's second and third tiers are unreachable for any waiver customer, so the factor restates the policy's scope, and its baseline (`outside_counted: '0'`, dropping the evaluation every plan has) is a straw man. **Finding F-D2.**
- `plan_ext_previsit_payment.carried_balance` and `plan_ext_noncovered_waiver.appointments_booked_ahead` each split one quantity into "read the holding's own event history" vs "read the holding's record field", where the record field is by its charter's definition that same history: plan `binding.quantity_fields.patient_due_balance: patient_due`, `accounts.patient_due` = "copays, coinsurance, deductible and waived non-covered charges less payments and adjustments", each money event declaring `account: patient_due` with a direction; series `quantity_fields.booked_visits_remaining: scheduled_visits`, `accounts.scheduled_visits` = "Future appointments booked on the series that have not yet been attended, cancelled, missed or released", with `series_visits_booked` in and attended/cancelled/no-show/released out. On any seed consistent with those charters the tier and the fall-through select the same number, so the factor can bear weight only on a seed that contradicts the charter. **Finding F-D3** (demonstrated per task).
- Label concerns (observation O5): `credit_refund.pending_eob_hold` is labelled method but its first two tiers are one expression with `within_months=1` vs `within_months=2` (a number); `auth_extension.visits_still_to_draw` is labelled parameter but its tiers are two algorithms (count rows of series history vs frequency x days / 7). Relabelling either leaves its policy within the >=2 parameter / >=1 method bounds (refund keeps `returned_payment` as method; extension keeps 2 parameters), so no count consequence follows.
- Business-realism observations without a demonstrable consequence (O6): the membership charter scopes `member_package_discount_percent` to "a Self-Pay Visit Package bought while the membership is active", while the noncovered charge applies it to a non-covered insured visit; the fixed 45.00 "office-visit component" on re-evaluations; prorating a self-pay rate by the payer's unit-counting method; previsit adds every billing error correction on the plan (including coinsurance corrections) back to the deductible still to be met.
- `plan_ext_retro_authorization.baseline.rule` says "The gap begins the day after the last approval's end date"; "last approval" reads either as the newest approval received or the last approval drawn on (the binding uses the latter). Observation O7; per-task consequence in task 1.

### findings

- **F-D1 — SOURCE-POLICY RED (undeclared override).** Symptom: two charter clauses fix the deductible amount collected for a coming HDHP visit differently. Root cause: plan_ext_previsit_payment replaces base plan_evt_time_of_service_collection's cap and timing with `overwrite: []`. Evidence: base "a deductible_estimate charge of the lower of the visit's allowed amount, the deductible remaining and tos_deductible_estimate_cap is posted"; base "Where coinsurance_billed_after_eob is true, the coinsurance ... [is] posted ... within eob_patient_charge_days calendar days after the explanation of benefits arrives"; extended "The cap on the deductible part follows the patient's Patient Payment Plan standing: ... capped at the current-payment-plan cap; ... capped at the full expected allowed amount; any other patient is capped at the payer program's time-of-service deductible estimate cap" and "the pre-visit amount also includes that coinsurance percentage of the part of the expected allowed amount above the deductible still to be met". Affected: plan.extended.yaml plan_ext_previsit_payment (`overwrite`, `rule`, `compute.estimate_cap`, `compute.beyond_deductible`). Bears on task 0 (demonstration there).
- **F-D2 — SOURCE-FACTOR RED (unreal ladder).** plan_ext_noncovered_waiver.visits_outside_series, as above. Affected: plan.extended.yaml plan_ext_noncovered_waiver `factors[visits_outside_series]`, `baseline.rule`, `compute.outside_counted`. Bears on task 1.
- **F-D3 — SOURCE-FACTOR RED where a seed contradicts the charter (record-vs-history ladders).** plan_ext_previsit_payment.carried_balance (bears on task 0) and plan_ext_noncovered_waiver.appointments_booked_ahead (bears on task 1). Demonstrated per task.
- Observations O1-O9 as listed in the sections above (O1 state_gate `gate` names a column; O2 compute_basis of `planned`/`last_visit_*` quotes baseline sentences; O3 previsit cap tier-1 broader in compute; O4/O4b undeclared waiver dependency of the noncovered charge, retro wording in the waiver value text; O5 label concerns; O6 realism; O7 retro baseline "last approval"; O8 docstring mentions; O9 customer-wide XLATEST and count-based approximations, plus the DSL's `RND` being Python `round` rather than half-up — no tie case arises in either world).

## closing_checklist

Written after both tasks' derivations were frozen (mtimes 0.md 05:42:23Z, 1.md 05:43:20Z) and revealed (05:43:24Z). Nothing above this heading was edited after the reveal. The difficulty is **not closed**: not every task passes all four relationships.

| item | status |
| --- | --- |
| Per-task files 1:1 with tasks, `_difficulty.md` alongside | yes: `0.md`, `1.md` (first revision; no older revision exists) |
| Every comparison section PASS | **no**: task 0 SOURCE-POLICY / SOURCE-CHAIN (proof figures) / SOURCE-FACTOR / SOURCE-TASK RED; task 1 SOURCE-CHAIN (proof figure) / SOURCE-FACTOR / SOURCE-TASK (proof text) RED |
| Extended policies fully covered, scopes pairwise disjoint | yes: `charter_scope` task 0 = {coinsurance_correction, noncovered_visit_charge, credit_refund, previsit_payment}, task 1 = {retro_authorization, auth_extension, noncovered_waiver}; disjoint, union = all 7, each equal to one connected component of the prerequisite graph (as derived before reveal) |
| Task tools and GT closed; uuid8s independent and frozen | yes (§ action_binding_and_uuids); every GT write uses a tool of its task's scope |
| Trees: 1-3 prerequisite problems, >= max(n-1,1) value_input edges, a user-owned write, acyclic, difficulty graph acyclic | yes: task 0 n=3, 2 value_input, root user-owned; task 1 n=2, 1 value_input, root user-owned; graph acyclic. Tree proofs carry false figures (task 0 F0-3, task 1 F1-3) |
| Every computation: self-sufficient baseline, 4-6 factors (>=2 parameter, >=1 method) surviving the tests, every factor bears weight against an honest baseline, baseline != gold | **no**: plan_ext_previsit_payment drops to 1 surviving parameter factor (F-D3 / F0-2); plan_ext_noncovered_waiver drops to 2 surviving factors (F-D2 / F1-1, F-D3 / F1-2). All other computations pass; every full baseline is definite and differs from gold (27.40, 118.00, 25.00, 113.10, 4, 10, "") |
| Base/extended override declarations complete | **no**: F-D1 (plan_ext_previsit_payment vs plan_evt_time_of_service_collection) |
| Instantiation-stage gates re-run on the final form | not applicable — the artifacts are unchanged and the difficulty is not closed; the gate snapshot supplied with the brief (all green, check_traceability deferred) stands as the entry record |

Charter-global findings and the tasks they bear on: F-D1 -> task 0; F-D2 -> task 1; F-D3 -> tasks 0 and 1. Per-task proof-text findings (F0-3, F0-4, F1-3, F1-4) live only in the task files.

## revision_2

### charter_global_frozen (revision 2)

- Written 2026-10-05T06:38Z, before any round-2 task GT was opened. Auditor: the same independent erl-task-policy-audit run as round 1 (Claude Opus 5.5).
- Inputs (sha256, matching the brief and the source files on disk): `plan.extended.yaml` e9728f01910155737c5917c019fc8e49acebdfa41efe3378ab4770386101e80c; `task_tools.py` 15327da452e49c53cfbbb64fde749673e5ee5d5e4386e86112fc6e49b9d906dd. Both changed since round 1, so every charter-global section is re-derived below rather than carried forward. Masked views: `/tmp/erl0032_views/insured_plan_authorizations_and_balances_r2/`.
- contamination_disclosure: in round 1 this auditor read the round-1 GT of both tasks (`evaluation_criteria`, `computations`, `prerequisite_closure`, `solvability_contract`, `design_rationale`), after freezing the round-1 blind derivations. The charter-global checks below do not depend on GT. The task files disclose what this means for each task.
- Entry conditions: the gate snapshot after the rework came with the brief (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; traceability still deferred to post-render). The masked views and their hashes were supplied and verified. Base lines 1-866 are still byte-identical to `blueprint/products/plan.yaml`.
- What changed (diff of the round-1 and round-2 views):
  - plan_ext_previsit_payment: two `overwrite` entries; two declaring sentences added to the rule; the `carried_balance` ladder and compute replaced; `estimate_cap` tier 1 now requires an installment.
  - plan_ext_noncovered_waiver: rule, compute, baseline and two factors rewritten.
  - Label changes: refund `pending_eob_hold` method -> parameter; extension `visits_still_to_draw` parameter -> method.
  - Retro "last approval" now reads "last approval drawn on".
  - `compute_basis` of `planned` (retro, extension) and of `last_visit_units`/`last_visit_allowed` (previsit) re-pointed to the ladder sentences.
  - `submit_auth_extension_019a16d0` `visit_date` docstring reworded.
  - No function body, uuid8, `prerequisite` block or other policy changed.

### policy_conflict_scan (revision 2)

Same seven policies and bindings; the subjects, triggers, terminal states and cross-category reads are unchanged, apart from the waiver's new read of the series `variant_name` (finding a telehealth series). Two components, {previsit <- refund <- (coinsurance, noncovered)} and {waiver <- (retro, extension)}, still partition the charter. One new tension was found inside plan_ext_noncovered_waiver's own rule (O10 below). No new conflict between policies.

### rule_compute_equivalence (revision 2)

- previsit `carried_balance` matches its new sentence:
  - tier 1 = deductible estimates + copays - all payments, floor 0, where an EOB deductible or coinsurance charge stands and no statement has been issued;
  - tier 2 = 0 where the record shows a credit;
  - fall-through = the record balance.
- previsit `estimate_cap` now matches the rule (tier 1 requires an installment to exist). **O3 closed.**
- Waiver: `counted_used` = used elsewhere + billed evaluations + billed series appointments + unbilled counted through retro + telehealth. Telehealth = billed telehealth visits, else sessions attended on a Telehealth 30-Minute series the plan funds, else 0. `waiver_date` = next-series opening where 0 < left = record remaining; '' where left > remaining; otherwise today. All of these match the rule.
- `compute_basis.result` of the waiver quotes the baseline sentence ("The waiver's first date of service is today...") while `result` = `waiver_date`; the implemented sentence sits under `waiver_date` (O2-type, observation O2b). The other O2 items are re-pointed. **O2 otherwise closed.**
- Unchanged elsewhere (coinsurance, non-covered charge, refund, retro, extension), as in round 1.

### action_binding_and_uuids (revision 2)

Unchanged pairs and uuid8s. The tool bodies are byte-identical to round 1 (the diff touches only the `submit_auth_extension_019a16d0` docstring, which now reads "the earliest past visit the request asks the payer to cover ... an extension request covers only visits still to come, so pass ''"). It names no other request kind, tool or order. **O8 closed.** No tool checks a prerequisite.

### prerequisite_graph and prerequisite_sentences (revision 2)

The `prerequisite` blocks are byte-identical to round 1. All five `policy_source` sentences are still verbatim in their blocked rules (string-checked), and the four-point tests and one-write-per-state derivations of round 1 still hold. O1 (state_gate `gate` names a column) is kept. No new cross-problem order appears in any rule (the waiver's added sentences concern counting and dating only).

### override_declarations (revision 2)

- plan_ext_previsit_payment now declares both supersessions of plan_evt_time_of_service_collection. Each `superseded_clause` is a verbatim substring of the base rule, and each `replaced_by` is verbatim in the extended rule.
- Each replacement is scoped "When a patient pays ahead of a visit", so the base clauses keep governing the charges posted at the visit, and the merged semantics give one reading for the scored pre-visit amount. **F-D1 closed.**
- plan_ext_noncovered_waiver: its overwrite is unchanged and its new count (which includes the billed evaluation and telehealth) stays within the declared replacement. No other policy's base relation changed.

### factor_ladders (revision 2)

| policy | factors | parameter | method | cross_difficulty |
| --- | --- | --- | --- | --- |
| coinsurance_correction | 4 | 3 | 1 | - |
| noncovered_visit_charge | 5 | 3 | 2 | series, membership |
| credit_refund | 5 | 4 | 1 | series |
| previsit_payment | 6 | 2 | 4 | series, payplan |
| retro_authorization | 5 | 2 | 3 | series |
| auth_extension | 5 | 2 | 3 | series |
| noncovered_waiver | 4 | 2 | 2 | series |

- Labels: `pending_eob_hold` is now a parameter (its tiers differ by a window length) and `visits_still_to_draw` is now a method (count of history rows vs frequency formula). **O5 closed.** Every policy still meets the bounds.
- previsit `carried_balance` (new ladder):
  - Tier 1 is conditioned on EOB charges standing without a statement and carries only time-of-service charges. That is a distinction a practice actually draws (EOB-driven balances are billed on the statement), and it remains distinct from the record balance on a charter-consistent seed: the record includes the EOB charge, tier 1 excludes it.
  - Tier 2 (record credit -> 0) and the fall-through (record balance) are distinct.
  - The record/history split that F-D3 objected to is gone from this ladder. **F-D3 closed for previsit at charter level** (seed checked per task).
- Waiver:
  - `visits_outside_series` (whose tier condition was universal) is replaced by `telehealth_visits` (billed telehealth / attended sessions on a funded telehealth series / 0). Its tier condition divides customers, and the billed evaluation is now part of the base count rather than a factor. **F-D2 closed.**
  - `appointments_booked_ahead` (record vs history) is replaced by `waiver_timing` (method), which reads the record's remaining appointments as one input. No ladder now splits a quantity between a record and its own history. **F-D3 closed for the waiver at charter level.**
  - Each new ladder has three distinct tiers stated in the rule, and its fall-through equals its baseline (`telehealth_counted: '0'`; `waiver_date: NOW`).
- `baseline.rule` of the waiver is now "The waiver's first date of service is today, the day the patient signs it."; it is self-sufficient (gives a definite date). The retro baseline now names "the last approval drawn on". **O7 closed.**

### findings (revision 2)

- F-D1, F-D2 and F-D3 are closed at charter level (above). F-D3's seed half is verified per task.
- O1, O4, O4b, O6 and O9 are kept as in round 1. O2, O3, O5, O7 and O8 are closed (O2 except O2b).
- **O10 (new, observation).** The waiver rule states three things about the first date of service:
  - S1, the first sentence: "its first date of service is the date of the first booked visit expected to run past that limit".
  - The fall-through tier: "otherwise the waiver covers from today".
  - The baseline sentence: "The waiver's first date of service is today, the day the patient signs it."

  Where 0 < visits left < appointments still booked on the active series, S1 gives a future appointment of the active series and the fall-through gives today. Neither task world reaches that tier (task 1 takes tier 1, where S1 and the ladder agree), so no score consequence can be demonstrated. The baseline sentence follows the charter-wide baseline-then-ladder pattern accepted in round 1.
- **O11 (new, observation).** The waiver's `telehealth_visits` tier 2 counts every attended session on a funded telehealth series in full. Unbilled in-clinic appointments, by contrast, count only through retroactive requests. The two classes of unbilled visit are treated inconsistently. Not reached in task 1 (tier 1 applies).

### closing_checklist (revision 2)

Written after both revision_2 derivations were frozen (mtimes 06:38:21Z and 06:38:44Z) and revealed (06:38:49Z). Nothing above this heading was edited after the reveal. The difficulty is **still not closed**: task 0 fails the unique-solution relationship (F0-5).

| item | status |
| --- | --- |
| Per-task files 1:1 with tasks, old revision kept | yes: `0.md` and `1.md` each hold the round-1 text unchanged plus `## revision_2` |
| Every comparison section PASS | **no**: task 0 SOURCE-TASK RED (F0-5, new); task 1 PASS |
| Round-1 REDs closed | yes: F-D1/F0-1, F-D2/F1-1, F-D3/F0-2/F1-2, F0-3, F0-4, F1-3, F1-4 all verified closed |
| Regressions | none in the four relationships for the unchanged computations (all round-1 figures reproduce). One new defect (F0-5) was introduced by the rework's new seeded row against an unchanged persona need |
| Scopes disjoint and complete; tools/GT closed; uuid8s | yes (charter_scope unchanged: 4 + 3 policies) |
| Trees: 1-3 prerequisite problems, value_input floor, user-owned write, acyclic | yes (task 0 n=3 with 2 value_input; task 1 n=2 with 1 value_input; both roots user-owned) |
| Factors: 4-6 per computation, >=2 parameter / >=1 method, all bear weight against honest baselines, baseline != gold | yes for all 7 computations (full baselines 27.40, 118.00, 25.00, 269.60, 4, 10, 2026-12-09, each different from gold) |
| Override declarations complete | yes |
| Instantiation gates on the final form | the orchestrator's post-rework snapshot (all green, traceability deferred) is cited; not re-run by the auditor, since the difficulty is not closed |

New charter observations: O10, O11 and O2b (no score consequence).

## revision_3

### charter_global_frozen (revision 3)

- Written 2026-10-05, before any round-3 task GT was opened. Same auditor.
- Inputs:
  - `plan.extended.yaml` 8269cfc6da0b4c577d3a2e6c60fc2e9dea4ababf78292626ae1fe56615eabee3 (changed since r2).
  - `task_tools.py` 15327da452e49c53cfbbb64fde749673e5ee5d5e4386e86112fc6e49b9d906dd (unchanged since r2).
  - Masked views in `/tmp/erl0032_views/insured_plan_authorizations_and_balances_r3/`; hashes verified against the brief and the source files.
- Base lines 1-866 are still byte-identical to `blueprint/products/plan.yaml`; blueprint mtimes are 2026-10-04 19:31-19:41.
- contamination_disclosure: this auditor read round-1 and round-2 GT after freezing each round's derivations. The charter-global checks below do not depend on GT.
- Entry conditions: the post-rework gate snapshot came with the brief (all green; traceability deferred to post-render).

### Re-derivation scope

Because the charter hash changed, every charter-global section was re-checked against the r2->r3 diff.
- **The diff touches only plan_ext_noncovered_waiver:**
  - the rule's opening sentence;
  - the telehealth sentence and the `telehealth_counted` compute;
  - its tier-2 ladder entry and fall-through value;
  - four `compute_basis` quotations of the telehealth sentence;
  - `compute_basis.result`.
- **For the other six policies,** the § revision_2 conclusions carry forward on the evidence of a byte-identical diff:
  - their rules, compute, factors, prerequisite blocks and overwrites;
  - the tool module, which is unchanged.

### Waiver re-check (revision 3)

- **Rule:** the opening sentence now reads "it covers every visit from its first date of service onward that runs past the limit, and that first date is set as described below". It no longer fixes a first date on its own, so it cannot conflict with the dating ladder. **O10 closed.**
- **Telehealth tier 2:**
  - New wording: "none has been billed and no retroactive request stands on the plan, while sessions have been attended on a telehealth series the plan funds". The compute adds `retro_asked == 0`.
  - The fall-through value now says unbilled sessions then count only through the retroactive requests, which `unbilled_counted` (retro asked less granted) already carries. Unbilled telehealth and unbilled in-clinic visits are now treated the same way. **O11 closed.**
  - The ladder keeps three distinct tiers. The fall-through still equals the baseline `'0'`. Tier 2 is now a three-part conjunction, each part weighed for a visit count, so none is universal.
  - Rule <-> compute: matches in both directions.
- **`compute_basis.result`:** now quotes the dating sentence that `waiver_date` implements. **O2b closed.**
- **Unchanged:** the factor set and labels (4 factors: 2 parameter, 2 method; cross-difficulty series), the baseline rule, the prerequisite sentences and the overwrite.
- **New coupling:** telehealth tier 2 now reads `retro_asked`, the value the retro prerequisite writes. This adds no edge and no order; the value_input edge already feeds the same computation.

### findings (revision 3)

No new charter-global defect.
- Closed: O2b, O10 and O11.
- Kept: O1, O4, O4b, O6 and O9.
- Closed earlier and still closed: F-D1, F-D2 and F-D3 (re-verified: their policies' text is unchanged since r2).

### closing_checklist (revision 3)

- **Order:** written after both revision_3 derivations were frozen (06:52:26Z) and revealed (06:52:32Z). Nothing above this heading was edited after the reveal.
- **Outcome:** both tasks pass all four relationships, so **the difficulty passes the source-layer audit**.

| item | status |
| --- | --- |
| Per-task files 1:1 with tasks; older revisions preserved | yes. `0.md` and `1.md` hold the round-1 text plus `## revision_2` and `## revision_3`, unedited |
| Every comparison section PASS | yes: task 0 PASS, task 1 PASS (revision 3) |
| All prior REDs closed | yes: F-D1/F0-1, F-D2/F1-1, F-D3/F0-2/F1-2, F0-3, F0-4, F1-3, F1-4 (round 2); F0-5 (round 3) |
| Regressions | none. Every scored value and factor figure reproduces under r3 and equals GT |
| Extended policies covered; scopes disjoint and complete | yes. Task 0 = {coinsurance_correction, noncovered_visit_charge, credit_refund, previsit_payment}; task 1 = {retro_authorization, auth_extension, noncovered_waiver} |
| Task tools and GT closed; uuid8s independent and frozen | yes (7 distinct uuid8s; tool bodies unchanged since round 1) |
| Trees | task 0: n=3, 2 value_input. Task 1: n=2, 1 value_input. Both roots are customer-owned writes; the graph is acyclic; every edge is unmet at the opening and bears weight |
| Factors | all 7 computations have 4-6 factors (>=2 parameter, >=1 method); tiers are distinct and stated in the rule; every factor bears weight against an honest baseline. Full baselines (27.40, 118.00, 25.00, 269.60, 4, 10, 2026-12-09) are definite and differ from gold. Each task has multi-source and cross-difficulty factors on seeded rows that agree with their own charters |
| Override declarations | complete |
| Instantiation gates on the final form | the orchestrator re-ran them on the r3 artifacts (hashes above): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. `check_traceability` remains deferred to post-render and is carried as an open item for the KB-doc audit stage |

Open observations, with no score consequence and not grounds for rework:
- O1, O4, O4b, O6 and O9 (charter level).
- O-T0-2, O-T0-4 and O-T0-5 (task 0).
- O-T1-1 and O-T1-3 (task 1).

## revision_4

### basis (written before the round-4 task files were opened)

- **Inputs, verified 2026-10-05T07:51Z:**
  - `plan.extended.yaml` 8269cfc6da0b4c577d3a2e6c60fc2e9dea4ababf78292626ae1fe56615eabee3 and `task_tools.py` 15327da452e49c53cfbbb64fde749673e5ee5d5e4386e86112fc6e49b9d906dd, both identical to revision 3.
  - Base lines 1-866 still byte-identical to `blueprint/products/plan.yaml` (mtime 2026-10-04 19:41).
  - Sources `tasks/0.json` b9c7229142ba85b09ab283c04946c323838f1fbfd43e0cc1c64508949306f765 and `tasks/1.json` d4397265bc7f27849e2abc7c21f62581471abcd29be7cd1f510a448aa0b941f0, matching the brief.
- **No new masked view was supplied, and none is needed:**
  - The charter and tools are unchanged.
  - The brief states that task 0's `frozen_time`, `user_scenario` and `initial_state` are byte-identical to the r3 view, and that 1.json moved only through the `db_closure` write-back.
  - Under the re-audit rule, the revision_3 charter-global sections and per-task derivations therefore carry forward by reference. This audit re-derives nothing; it confirms the inputs are identical after opening the files (below).
- **contamination_disclosure:** the GT of rounds 1-3 is already known to this auditor, so revision 4 is a verification of what moved, not a blind derivation.

### closing_checklist (revision 4)

- **Charter-global sections:** carried forward from revision 3 on unchanged hashes (`plan.extended.yaml` 8269cfc6..., `task_tools.py` 15327da4...; base still identical).
- **Task results:** task 0 PASS (the narration fix is confirmed; nothing else moved) and task 1 PASS (only `db_closure` moved, and it equals the seed).
- **Gates:** the instantiation-stage gate snapshot on this final form (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, TRACEABILITY, SCOPE all OK) closes the traceability item left open in revision 3.
- **Outcome:** the difficulty **passes the source-layer audit**.
- **Open observations** (unchanged; none with a score consequence): O1, O4, O4b, O6, O9, O-T0-2, O-T0-4, O-T0-5, O-T1-1, O-T1-3.
