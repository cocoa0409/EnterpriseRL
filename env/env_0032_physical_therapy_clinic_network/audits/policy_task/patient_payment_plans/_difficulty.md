# Policy-task audit — patient_payment_plans / charter-global

## charter_global_frozen

- Scenario: `env/env_0032_physical_therapy_clinic_network`; difficulty `patient_payment_plans` (category `payplan`); M = 2 (tasks 0, 1).
- Frozen at 2026-10-05T05:20Z (revision 1; no earlier revision exists in this directory). Auditor: Claude (erl-task-policy-audit subagent), independent of the instantiating agent.
- Inputs and freeze hashes (sha256, re-checked against the orchestrator's list before reading):
  - `tasks/patient_payment_plans/payplan.extended.yaml` = `/tmp/erl0032_views/patient_payment_plans/payplan.extended.yaml` — `1f256e19021daa1ace75d74569a2a93593875c17ddf76021546f0284b7cbee5b`
  - `tasks/patient_payment_plans/task_tools.py` = view copy — `fd596264f3ddb11b253aae9f28b0b039eef7e8f05480ce0442128a407a4b069d`
  - blueprint read: `blueprint/blueprint.yaml` (difficulty entry `patient_payment_plans`), `blueprint/products/payplan.yaml`, `blueprint/db_schema.json` (payment_plan_events enums), `blueprint/share_tools.py`, and `products/plan.yaml` / `products/hardship.yaml` only for the event-type and state names the cross reads use.
  - Runtime semantics of the restricted expressions (MONTHS, DAYS, COUNT/SUM/LATEST `within_months`, XCOUNT customer scoping, CFIELD/EXISTS) taken from `skills/erl-task-instantiate/scripts/check_compute.py` (`MONTHS`, `DAYS`, `build_env._within`, `_xrows`).
- Permitted: the charter (base + extended), task tool contracts, schema, share tools. Masked and unread while this section was written: every task's `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`; existing audit conclusions of any other difficulty. Nothing in this section is derived from a revealed GT.
- Entry conditions (Step 0): the brief carries the gate snapshot (check_extended EXTENDED OK, check_task_tools TASK TOOL CONTRACT OK, replay_tasks REPLAY OK, check_solvability SOLVABILITY OK, check_compute COMPUTE OK, check_grounding GROUNDING OK, check_cross_fire SCOPE OK; blueprint BLUEPRINT OK, SHARE TOOLS OK, VALID; check_traceability deferred pending the published KB) and the masked views with hashes. Complete; cited, not re-run.
- Base copy: lines 1-679 of the extended file are byte-identical to `blueprint/products/payplan.yaml` (`diff` shows only the trailing `extended_policies` banner comment added). Base section verbatim: OK.

### policy_conflict_scan

Extended policies and claimed writes:

| policy | trigger | target_tool (owner) | computes | base refs | prerequisite |
| --- | --- | --- | --- | --- | --- |
| `payplan_ext_missed_installment_late_fee` | state_due | `assess_payment_plan_late_fee_b662389f` (agent) | fee `amount` | `payplan_evt_delinquency` | [] |
| `payplan_ext_past_due_catch_up` | on_request | `pay_payment_plan_past_due_400c78cb` (user) | payment `amount` | `payplan_evt_payments`, `payplan_evt_delinquency` | late_fee (value_input, state) |
| `payplan_ext_returned_draft_fee` | state_due | `book_payment_plan_returned_fee_3086fcb8` (agent) | fee `amount` | `payplan_evt_delinquency` | [] |
| `payplan_ext_term_modification` | on_request | `accept_payment_plan_modification_53d89fa9` (user) | `monthly_payment` (+ term in rule) | `payplan_payment_schedule`, `payplan_add_ons_and_holidays` | returned_draft_fee (value_input, state) |

- Overlapping subjects: the two fee policies both write `payplan_fee_assessed`, separated by `fee_kind` (late_fee vs returned_payment_fee) and by trigger object (latest `payplan_installment_missed` vs latest `payplan_autopay_failed`). No two policies compute the same field on the same object.
- Triggers / eligibility / time anchors: late fee and returned fee are state_due obligations keyed to an unbooked entry; catch-up is on request on a `past_due` plan; modification is on request with base eligibility `modification_allowed`, `modifications_per_plan`. Windows all use the same "fewer than N whole calendar months" convention, matching the runtime `_within` (0 <= MONTHS < N). No conflicting anchors found.
- Cross-category read boundaries: late fee and modification read `plan` history (`plan_visit_billed`, `plan_statement_issued`), returned fee reads `plan` history (`plan_patient_payment`, `plan_statement_issued`), catch-up reads `hardship` holding (`status`, `expiry_date`). All read-only; event types and states exist in `products/plan.yaml` (lines 340, 374, 424) and `products/hardship.yaml` (line 18).
- Terminal states: catch-up sets status `active` (lifecycle past_due -> active "The past-due amount is paid"); modification changes `monthly_payment`, `term_months`, `modifications_used`; fees raise `plan_balance`. Compatible.
- Scope partition (from the policies the visible worlds make due/requested; confirmed after reveal in each task file): task 0 = {late_fee, catch_up}; task 1 = {returned_draft_fee, term_modification}. Pairwise disjoint, jointly complete over the four extended policies.

### rule_compute_equivalence

Swept every binding against `compute_basis` and back against the rule, for all four policies.

- `payplan_ext_missed_installment_late_fee`: every binding (l_due, l_age, l_miss_recent, l_fees_narrow/wide/life, l_prior, l_step, l_reason, l_collections, l_lapse, l_paid, l_paid_last, l_effort, l_visits, l_statements, l_treatment, result) has a verbatim basis; date placement ("an installment being placed by its due date and any other entry by the date it was recorded") matches `date_field='installment_due_date'` on missed/fee rows and the default `event_date` on payments; the three-way partitions of l_prior, l_lapse, l_effort, l_treatment are exhaustive in both faces; the single final rounding is stated and implemented. Equivalent.
- `payplan_ext_past_due_catch_up`: c_last_collected ("or the signing date where none was"), c_span, c_missed_n, c_paid_against (payment_kind installment, by due date), c_late_fees, c_returned_fees, c_missed_year, c_collected_year, c_late_share, c_age, c_returned_year, c_returned_share, c_extra_in/c_extra_window/c_credit (MN to one installment, `not P('extra_payment_shortens_term')`), c_days/c_returned_latest/c_pull, c_missed_life/c_goodwill, c_pending/c_approved_expiry/c_assist, c_core (floor at zero), c_fees, result (one rounding) all quoted and implemented. Equivalent.
- `payplan_ext_returned_draft_fee`: r_due .. result quoted and implemented; r_bank encodes "nothing for a card draft where nsf_fee_applies_to_card is false". Equivalent, with observation O4 below.
- `payplan_ext_term_modification`: m_due_count/m_remaining, m_history, m_treatment, m_ext (MN cap), m_last_auto/m_days, m_deferred, m_adjust, m_held, m_recent_fees, m_collected, m_carve, m_spread, m_count, ceiling-to-cent and floor at min_monthly_payment all quoted and implemented. Two compute-side gaps recorded as observations O5, O6 (no scored consequence in either task world).
- Factor ladders vs rule vs `decides` branches: every tier named in `factors[].ladder` is a sentence of the rule and a branch of its binding, and every branch is a stated tier, for all 20 factors. No tier lives in one face only.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (table above). Tool bodies (`task_tools.py`) perform one unconditional write each: create one `payment_plan_events` row and update `plan_balance` (fees, payment — the payment also sets `status='active'`), or update `monthly_payment`/`term_months`/`modifications_used` (modification). None checks eligibility, status, prior entries or amounts; none refuses or hints.
- Docstrings: no sequence position, no other tool named; the only ordering-like words are "once the payment is recorded" / "once the new terms are recorded" describing the return value (lines 84, 169) and the module docstring's generic "before the call" (line 6). Not a sequencing statement about another problem. OK.
- uuid8s: `b662389f`, `400c78cb`, `3086fcb8`, `53d89fa9` — no shared prefix, no sequence, no adjacent values, none reused. OK.

### prerequisite_graph

- `prerequisite` filled on all four policies (`[]` on the two fee policies).
- Edges: catch_up -> missed_installment_late_fee; term_modification -> returned_draft_fee. Both `problem` ids are extended policies of this file, neither self nor base. Graph acyclic (two disjoint chains of length 1).
- `policy_source` verbatim in the blocked rule: catch-up rule sentence 3 "The catch-up amount is fixed only after the installment most recently recorded as missed carries its late-fee entry on the plan." (yaml line 941-942); modification rule sentence 3 "The modified installment is not worked out until the installment whose automatic draft most recently came back unpaid carries its returned-payment fee entry on the plan." (lines 1397-1398). Both found.
- `form: state` on both, no `fallback_reason` — consistent.
- `condition` equals the sentence's scope (a late_fee row on the latest missed installment's due date; a returned_payment_fee row on the latest failed draft's due date) — neither strengthened nor weakened.
- `resolved_by` = the depended-on policy's `target_tool`; each tool creates exactly the row the condition names (fee_kind and installment_due_date passed through).
- `kind: value_input`, `gate` = `c_late_fees` / `m_returned_year`, both real bindings of the blocked compute; the effect text is true of the compute (c_late_fees rises by the fee; m_returned_year rises by one, plan_balance and m_recent_fees rise by the fee).
- No authoring-viewpoint wording in either `prerequisite` block.

### prerequisite_sentences

Four-point test, both edges:

| edge | ordering connective | waited-on state, record words | no tool / id / snake_case / row id | strength = condition |
| --- | --- | --- | --- | --- |
| catch_up -> late_fee | "only after" | "the installment most recently recorded as missed carries its late-fee entry on the plan" — plan history "missed installments", "late ... fees" (finder docstring) | yes | yes |
| modification -> returned_fee | "not until" | "the installment whose automatic draft most recently came back unpaid carries its returned-payment fee entry on the plan" — "failed automatic payments", "returned-payment fees" | yes | yes |

- Exactly one write of this difficulty brings each state about: only `assess_payment_plan_late_fee_b662389f` creates a `fee_kind='late_fee'` row; only `book_payment_plan_returned_fee_3086fcb8` creates a `fee_kind='returned_payment_fee'` row.
- Reader's derivation, single reading: (1) catch-up sentence + plan history (latest `payplan_installment_missed` row, no `late_fee` row with that due date) -> the waited-on entry is missing -> the late-fee policy's own rule ("A late-fee entry is booked once for the installment most recently recorded as missed on the plan; it carries that installment's due date and adds its amount to the plan balance") is the one write that creates it. (2) modification sentence + history (latest `payplan_autopay_failed` row, no `returned_payment_fee` row with that due date) -> the returned-fee rule ("A returned-payment fee entry is booked once for the installment whose automatic draft most recently came back unpaid ...") is the one write that creates it.
- Neither depended-on rule restates the sentence or mentions the blocked problem. Neither blocked rule carries a second wording, a tool name or another problem's id.
- No rule of the charter states a cross-problem order that grounds no declared edge (the "worked out in this order" sentences of catch-up and modification order intermediates of one computation). Base sentence "After an adjustment the installment is recomputed only by the patient's request under payplan_payment_schedule." (`payplan_evt_adjustments`) concerns `payplan_balance_adjusted`, which no task of this difficulty writes; it grounds no edge here — observation only.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (finding half only).

`payplan_ext_missed_installment_late_fee` vs `payplan_evt_delinquency`:
- "An installment not paid ... is missed, and the plan becomes past due." — followed.
- "A failed automatic payment is retried ... before the installment is treated as unpaid." — followed.
- "Each missed installment adds late_fee, up to late_fees_max_per_plan late fees in the plan's life (payplan_msr_late_fees)," — handled differently (windowed count, step, three shares); **declared** in `overwrite`.
- "and the first late fee is waived on request where late_fee_first_waiver is true." — not overwritten; inherited as a separate on-request waiver (via `payplan_evt_adjustments` fee_waiver); does not compete with the booked amount.
- "A returned ACH or check payment adds nsf_fee; a declined card adds it only where nsf_fee_applies_to_card is true." / cure sentence — not this policy's quantity.

`payplan_ext_returned_draft_fee` vs `payplan_evt_delinquency`:
- "A returned ACH or check payment adds nsf_fee;" — handled differently (step 15/20/nsf_fee, shares); **declared**. "a declined card adds it only where nsf_fee_applies_to_card is true" — followed (r_bank). Other sentences not this quantity.

`payplan_ext_past_due_catch_up` vs `payplan_evt_payments`, `payplan_evt_delinquency`:
- "Payments are accepted only on a plan in active, past_due or defaulted status." — followed.
- "... where autopay_required is true installments are collected automatically and manual payments are extra." — the catch-up records a manual phone payment as an installment payment and counts the manual portal payment recorded `payment_kind='installment'` as an installment payment. Not declared. See O1 (no scored consequence demonstrated).
- "A payment is applied first to the oldest unpaid installment, then to plan fees, then as principal; an amount above what is due is applied by overpayment_handling" — followed (the credit sentence states the same application).
- "and extra principal shortens the remaining term where extra_payment_shortens_term is true and otherwise lowers the installment." — handled differently (extra-principal credit); **declared**.
- "An installment counts as paid when at least partial_payment_threshold_percent ..." — followed.
- "A past-due plan becomes current when every missed installment is paid in full where cure_requires_full_past_due is true," — not overwritten; the catch-up's credit tier can declare a plan current with the missed installment not paid in full by installment payments. See O2 (latent; not exercised in task 0).
- "or when the latest missed installment is paid where it is false." — **declared**, but `replaced_by` is the catch-up amount sentence, which does not govern the cure condition the superseded clause governed. See O2.
- Fee sentences (late_fee, nsf_fee) — the catch-up does not compute fees; it reads booked ones.

`payplan_ext_term_modification` vs `payplan_payment_schedule`, `payplan_add_ons_and_holidays`:
- "No interest is charged where interest_rate_percent is 0." — followed.
- Down-payment sentences — not this quantity.
- **"The monthly installment is the remaining balance divided by term_months, rounded up to the next cent, but never below min_monthly_payment; when the minimum applies the number of installments is the remaining balance divided by min_monthly_payment, rounded up."** — `payplan_payment_schedule` has `subject: [payplan_enrolled, payplan_terms_modified]`, and base `payplan_evt_adjustments` routes a patient-requested recomputation of the installment to this policy ("After an adjustment the installment is recomputed only by the patient's request under payplan_payment_schedule."). The extended policy computes the modified installment differently (plan balance less a held installment and less carved fees, divided by installments-not-yet-due adjusted by the count adjustment plus extension months), and fixes the modified term at term_months + extension months even where the minimum applies. **Not named in `overwrite`** — undeclared override. Finding F1.
- "The due day is one of due_day_choices ..." — not this quantity.
- "Where modification_allowed is true the patient may change the installment and term up to modifications_per_plan times," — followed (on request, user-accepted).
- "never adding more than max_term_extension_months to term_months" — handled differently; **declared**.
- "and never going below min_monthly_payment." — followed (floor).
- `payplan_add_ons_and_holidays`: "under extend_term the installment stays and months are added, never more than max_term_extension_months in total" — followed (cap); "A payment holiday defers one installment to the end of the plan ..." — followed by the deferral tier. Other sentences not this quantity.

### factor_ladders

| policy | factor | effect | decides | tiers (values / methods) | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| late_fee | late_fee_count_window | method | l_prior | narrow 12m / wide 24m / whole life | yes (plan age, recent misses) | — |
| late_fee | late_fee_step | parameter | l_step | 0.00 / first_late_fee 7.50 / late_fee | no (count + tier param) | — |
| late_fee | draft_lapse_share | parameter | l_lapse | 0.5 / 0.8 / 1.0 | yes (failure reason, autopay collections) | — |
| late_fee | payment_effort_share | parameter | l_effort | 0.6 / 0.9 / 1.0 | yes (sum paid, date paid) | — |
| late_fee | active_treatment_share | parameter | l_treatment | 0.8 / 0.9 / 1.0 | yes (visits, statements) | plan |
| catch_up | late_fee_collection_share | parameter | c_late_share | 0.5 / 0.75 / 1.0 | yes (misses, collections) | — |
| catch_up | returned_fee_collection_share | parameter | c_returned_share | 0.6 / 0.8 / 1.0 | yes (plan age, returned fees) | — |
| catch_up | extra_principal_credit | method | c_credit | full credit / credit capped at one installment / no credit | yes (in-delinquency extra, lookback extra, tier param) | — |
| catch_up | next_installment_pull | parameter | c_pull | 1.0 / 0.5 / 0 | yes (days since due, returned fee) | — |
| catch_up | goodwill_principal_share | parameter | c_goodwill | 0.1 / 0.05 / 0 | yes (lifetime, year and delinquency miss counts) | — |
| catch_up | assistance_share | parameter | c_assist | 0.5 / 0.75 / 1.0 | yes (approved expiry, pending case) | hardship |
| returned_fee | returned_fee_count_window | method | r_counted | clean 6m / year 12m / whole life | yes (plan age, misses) | — |
| returned_fee | returned_fee_step | parameter | r_step | 15.00 / 20.00 / nsf_fee | no | — |
| returned_fee | draft_recovery_share | parameter | r_recovery | 0.6 / 0.8 / 1.0 | yes (retry collection, collections) | — |
| returned_fee | prepayment_share | parameter | r_prepay | 0.8 / 0.9 / 1.0 | no (extra principal vs installment) | — |
| returned_fee | care_account_standing_share | parameter | r_standing | 0.8 / 0.9 / 1.0 | yes (care-plan payments, statements) | plan |
| modification | history_extension_months | parameter | m_history | 1 / 2 / max_term_extension_months | no | — |
| modification | treatment_extension_months | parameter | m_treatment | 2 / 1 / 0 | yes (visits, statements) | plan |
| modification | request_timing_count_adjustment | method | m_adjust | hold next installment / add deferred installments / none | yes (days since last autopay due date, holidays) | — |
| modification | fee_carve_share | parameter | m_carve | 1.0 / 0.5 / 0 | yes (recent fees, collections) | — |

- Counts per policy: late_fee 5 (4 parameter, 1 method); catch_up 6 (5 parameter, 1 method); returned_fee 5 (4 parameter, 1 method); modification 4 (3 parameter, 1 method). All within 4-6 with >= 2 parameter and >= 1 method.
- Per task (scope above): task 0 policies carry multi-source factors and cross_difficulty `plan` (late fee) and `hardship` (catch-up); task 1 policies carry multi-source factors and cross_difficulty `plan` (returned fee, modification).
- Binding sets pairwise disjoint within each policy; every `decides` is an input binding, never `result`.
- Every ladder has three pairwise-disjoint tiers as stated (fall-through counted); no two tiers of any ladder share a value or method.
- Every tier (condition and value/method) is stated in the rule prose and implemented in compute (see rule_compute_equivalence).
- Labels: the three `method` factors change the algorithm (which window is counted; full vs capped vs no credit; held/added/none count adjustment); the 16 `parameter` factors substitute a number. Honest. Each method tier names a rule the charter states.
- Fall-through = baseline for every factor (e.g. late_fee_count_window fall-through "whole life" = `baseline.rule` "over its whole life"; returned_fee_step fall-through nsf_fee = `baseline.rule` "the tier's nsf_fee"; history_extension_months fall-through max_term_extension_months = `baseline.rule` "plus max_term_extension_months").
- `baseline.rule` of each policy is a verbatim sentence of its `rule` and names the `baseline.params` keys it uses.
- Business realism: conditions weigh payment history, autopay track record, partial/prompt payment, active therapy, hardship standing, request timing — none holds of every customer reaching the write. Two naming/semantics points recorded as observations (O7, O8); neither is shown to be a treatment no such business would publish.

### findings

**F1 — SOURCE-POLICY RED (charter-global; bears on task 1).**
- Symptom: the term-modification policy computes the modified installment by a formula that differs from the base installment sentence of `payplan_payment_schedule`, and its `overwrite` names only the extension-cap clause.
- Root cause: `payplan_ext_term_modification.overwrite` = [{base_policy: payplan_payment_schedule, superseded_clause: "never adding more than max_term_extension_months to term_months"}]; the base sentence "The monthly installment is the remaining balance divided by term_months, rounded up to the next cent, but never below min_monthly_payment; when the minimum applies the number of installments is the remaining balance divided by min_monthly_payment, rounded up." governs the installment of `payplan_terms_modified` (in the policy's `subject`) and is the policy `payplan_evt_adjustments` names for a patient-requested recomputation. It is neither followed nor declared superseded.
- Evidence: base `payplan_payment_schedule` rule (extended yaml lines 480-488) and subject (line 478); `payplan_evt_adjustments` rule (lines 667-668); extended rule sentences "The modified installment is the plan balance divided by the installments not yet due plus max_term_extension_months, ... and the modified term is the current term_months plus the extension months used." and "The modified installment is worked out in this order: first the plan balance less any held installment and less the carved fees; then that amount divided by the installments not yet due, adjusted by the count adjustment, plus the extension months; ..." (lines 1399-1401, 1425-1428); `overwrite` (lines 1365-1371).
- Demonstrated consequence: two passages give two installments for the same request — see `1.md` (task 1 handling world: extended 150.78 vs base reading 162.26). Where the minimum binds, the base sentence also gives a different term (ceil(remaining balance / min_monthly_payment)) from the extended's term_months + extension months.
- Affected artifact: `tasks/patient_payment_plans/payplan.extended.yaml`, `extended_policies[payplan_ext_term_modification].overwrite`; scored `monthly_payment` (and, where the floor binds, `term_months`) of `accept_payment_plan_modification_53d89fa9`.

**Observations (no scored consequence demonstrated in either task world):**
- O1 (catch-up vs `payplan_evt_payments`): "where autopay_required is true installments are collected automatically and manual payments are extra" is neither followed nor declared; the catch-up tool records its manual payment as `payment_kind='installment'`. On task 0's world the alternative classification (the 60.00 manual portal payment as extra) leaves c_core unchanged (149.35 − 0 − 85.00 = 64.35 = 149.35 − 60.00 − 25.00), so no second number. Bears on task 0 only as an observation.
- O2 (catch-up vs `payplan_evt_delinquency`): the declared `overwrite` pairs the superseded cure clause "or when the latest missed installment is paid where it is false." with an amount formula that does not govern the cure condition; and the unsuperseded clause "A past-due plan becomes current when every missed installment is paid in full where cure_requires_full_past_due is true" can disagree with "A catch-up payment brings a past-due plan current in one payment" whenever the extra-principal credit carries the installment (installment payments then fall short of the installment). On task 0's world the catch-up payment recorded against the installment (60.00 + catch-up) exceeds the 149.35 installment, so both clauses agree.
- O3 (all four policies): each rule carries its baseline sentence and its full composition sentence as two definitions of the same quantity (e.g. late fee: "The missed-installment late fee is the tier's late_fee, rounded to the cent, except ..." and "The missed-installment late fee is the late-fee step multiplied once by the product of ..."). Mandated by the factor design (baseline sentences must be rule sentences); the later composition sentence is explicit. Not recorded as a conflict.
- O4 (returned fee): rule "the installment whose automatic draft most recently came back unpaid" orders by when the draft failed; `r_due` orders `payplan_autopay_failed` rows by `installment_due_date`. Identical on both task worlds.
- O5 (modification): the modified term ("the modified term is the current term_months plus the extension months used", plus deferred installments) is a scored argument with no compute binding; derivable from the rule, so no second reading.
- O6 (modification): `m_days: DAYS(m_last_auto, NOW) if m_last_auto else 0` supplies a default for a plan with no autopay collection that the rule does not state. Not exercised.
- O7 (catch-up): `goodwill_principal_share` adds an extra principal amount to a repeat delinquent's catch-up; the word "goodwill" reads as a concession while the effect is a charge. Wording only.
- O8 (catch-up): `pull_share_card` is named for card drafts while its tier condition is "no returned-payment fee was booked on that installment"; and the pulled installment is recorded against the missed installment and taken off principal (`overpayment_handling: apply_to_principal`), so the coming automatic draft still runs. Not shown to change any scored value.
- O9 (`payplan_evt_adjustments`): base sentence "After an adjustment the installment is recomputed only by the patient's request under payplan_payment_schedule." states an order between an adjustment and a recomputation; it grounds no edge of this difficulty and no task writes an adjustment.

Tasks affected: F1 -> task 1. O1, O2, O7, O8 -> task 0 (observations). O4, O5, O6 -> task 1 (observations). O3, O9 -> both (observations).

## closing_checklist

Written after both reveals (05:24Z onward); the charter-global section above was written at 05:22:22Z, before any reveal, and is unchanged (its hash before this append: `5064ccd7c5442660c806cd9677f05ad8c1ab020d04ba66785039844ea72d46b6`).

- Per-task files: `0.md`, `1.md` correspond one-to-one with `tasks/0.json`, `tasks/1.json`; each carries a frozen section and a comparison. First revision; no older revision to preserve.
- Verdicts: task 0 **PASS**; task 1 **SOURCE-POLICY RED** (F1 / T1-1) and **SOURCE-TASK RED** on its proof field (T1-2). The comparison sections do not both carry PASS, so **this difficulty does not pass the source-layer audit**.
- Coverage and scope (confirmed against `charter_scope` of both tasks): task 0 {missed_installment_late_fee, past_due_catch_up}, task 1 {returned_draft_fee, term_modification}; pairwise disjoint, union = all four extended policies; task tools disjoint and closed; uuid8s independent (§ action_binding_and_uuids).
- Problem trees: each task has 1 prerequisite problem, 1 value_input edge, an owner=user root, no cycle; the difficulty's graph (two disjoint one-edge chains) is acyclic.
- Factors: every computation declares a self-sufficient baseline and 4-6 factors (>= 2 parameter, 1 method), each task carries multi-source and cross-difficulty factors with seeded rows, every ladder has three distinct tiers stated in the rule, every factor bears weight against an honest baseline, and each baseline gives a definite number different from gold (10.00 / 118.67 / 25.00 / 144.23 vs 4.32 / 234.04 / 6.48 / 150.78).
- Gates: not re-run by the auditor (the skill assigns that to the orchestrator); the audited artifacts are unchanged since the brief's snapshot (`payplan.extended.yaml` and `task_tools.py` hashes match the frozen ones; `tasks/0.json` and `tasks/1.json` hashes match the brief at reveal), so that snapshot stands for the final form.

## revision_2

### charter_global_frozen (revision 2)

- Re-audit round 2, written 2026-10-05T06:28Z, before any round-2 GT was opened. Auditor: Claude (erl-task-policy-audit subagent). Revision 1 text above is left untouched.
- Inputs (sha256, re-checked against the orchestrator's list and the source files):
  - `payplan.extended.yaml` `0723cdf025facb1413dc6696797d5d0f479e37819f534423695fc098538b1925` (round 1: `1f256e19…`) — **changed**, so every charter-global section is re-derived below.
  - `task_tools.py` `69b961642f36740ab4350c1b9b4ecb50b95669dc1ca988cd072990f5cf95f86a` (round 1: `fd596264…`) — **changed**.
  - Views read: `/tmp/erl0032_views/patient_payment_plans_r2/` (charter, tools, `task0.visible.json` unchanged `24988b7b…`, `task1.visible.json` `161f3108…`).
- Method: full `diff` of round-1 vs round-2 charter and tools (the change set is listed below), then every check re-run on the round-2 text; unchanged text was re-read where a change could reach it.
- Masked and unread: everything masked in round 1, in the round-2 task files (`tasks/0.json` `8a22dc1f…`, `tasks/1.json` `ff643167…`). The round-1 reveals are a known prior exposure of round-1 GT; they are disclosed in each task file's revision_2 section.
- Gate snapshot after rework, from the brief: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK; traceability deferred. Cited, not re-run.
- Base copy: lines 1-679 still byte-identical to `blueprint/products/payplan.yaml`.

Change set (round 1 -> round 2):
1. `l_due`, `c_due_latest`, `r_due`: `LATEST` now orders by `event_date` (the default) instead of `installment_due_date`; both prerequisite `condition`s now read "… the … row of the plan with the latest event_date".
2. Catch-up `overwrite`: new entry superseding `payplan_evt_payments` "where autopay_required is true installments are collected automatically and manual payments are extra." with a sentence added to the rule ("The catch-up payment is taken by hand and counts as an installment payment toward the missed installments, never as an extra payment, …"); the cure entry now supersedes the whole cure sentence of `payplan_evt_delinquency` (both branches), replaced by the new rule sentence "A past-due plan is current again when its catch-up amount is paid in one payment, the extra-principal credit standing for the part of the missed installments it covers, whatever the tier's cure_requires_full_past_due."
3. Catch-up renames: `pull_share_card` -> `pull_share_unreturned`; `goodwill_principal_share`/`c_goodwill`/`goodwill_share_*` -> `repeat_delinquency_principal_share`/`c_repeat_principal`/`repeat_share_*`; new rule sentence "The pulled amount, being above what the missed installments call for, is applied by overpayment_handling like any other amount above what is due, and the coming installment is still collected on its own due date."
4. Modification `overwrite`: new entry superseding the `payplan_payment_schedule` installment sentence, replaced by the existing "The modified installment is worked out in this order: …" sentence; new rule sentences "Where no installment has yet been collected by automatic payment, no installment is held." and "The modified term is the current term_months plus the extension months and any deferred installment added by the count adjustment, and it stays so where min_monthly_payment applies."; new binding `m_term_new: "F('term_months') + m_ext + (m_adjust if m_adjust > 0 else 0)"`; `m_days` basis re-pointed to the new hold sentence.
5. `task_tools.py`: module docstring "before the call" -> "for each call"; `accept_payment_plan_modification_53d89fa9` docstring adds "An installment already queued for automatic collection is still drafted at the amount it was scheduled at, and the new installment applies to the installments that follow it." Function bodies unchanged.

### policy_conflict_scan (revision 2)

Same four policies, tools, owners, triggers and `computes` as round 1; no new subject or written field. The new catch-up sentences (manual payment counts as installment; cure on payment of the catch-up amount; pulled amount by overpayment_handling, coming installment still drafted) and the new modification sentences touch no other policy's quantity. Cross-category reads unchanged. Scope partition unchanged: {late_fee, catch_up} / {returned_fee, modification}, disjoint and complete.

### rule_compute_equivalence (revision 2)

- `l_due`/`c_due_latest` by `event_date` now match "the installment most recently recorded as missed"; `r_due` by `event_date` matches "whose automatic draft most recently came back unpaid" — **O4 closed**.
- `m_term_new` implements the new term sentence (extension months plus deferred installments; no change where the floor binds) — **O5 closed**. It is quoted in `compute_basis` and is consistent with the baseline sentence "the modified term is the current term_months plus the extension months used" (the deferral tier adds the deferred installments, as the count-adjustment sentence also says).
- `m_days: … if m_last_auto else 0` now rests on "Where no installment has yet been collected by automatic payment, no installment is held." (0 < hold_days, so no hold; the deferral tier stays reachable) — **O6 closed**.
- Renamed catch-up bindings/params are renamed consistently in rule, `params`, `compute`, `compute_basis` and `factors` (no residue of `pull_share_card` or `goodwill` in the file).
- All other bindings unchanged and re-confirmed equivalent.

### action_binding_and_uuids (revision 2)

- Pairs and uuid8s unchanged (`b662389f`, `400c78cb`, `3086fcb8`, `53d89fa9`); bodies unchanged, none judges a prerequisite.
- New modification docstring sentence names no tool and no other problem; "already queued" and "follow it" describe the write's effect, not a call order. It does describe a draft behaviour the body does not implement (the body still only sets `monthly_payment`, `term_months`, `modifications_used`; nothing records the queued amount), and it does not say when an installment counts as "queued" while the policy holds one only after hold_days. Observation R2-O1; no scored consequence (task 1 is on the hold tier).

### prerequisite_graph (revision 2)

Unchanged structure (two disjoint one-edge chains, acyclic, `form: state`, `kind: value_input`, gates `c_late_fees` / `m_returned_year` exist, `resolved_by` = target tools). `policy_source` sentences unchanged and still verbatim in the blocked rules. The rewritten `condition`s ("with the latest event_date") match the sentences' "most recently recorded as missed" / "most recently came back unpaid" and the compute's `LATEST` ordering — neither strengthened nor weakened.

### prerequisite_sentences (revision 2)

Four-point test unchanged and passing for both edges; exactly one write creates each waited-on entry; depended-on rules do not restate the sentences. The new rule sentences state no cross-problem order (the cure sentence ties the plan's status to its own payment; the pull sentence says the coming installment is drafted on its own date, which is no write of this difficulty). O9 (`payplan_evt_adjustments` order sentence) stands as an observation, unchanged.

### override_declarations (revision 2)

- Late fee, returned fee: unchanged; declarations as in round 1.
- Catch-up vs `payplan_evt_payments`: "where autopay_required is true installments are collected automatically and manual payments are extra." is now **declared** — **O1 closed**. Remaining sentences followed as in round 1.
- Catch-up vs `payplan_evt_delinquency`: the whole cure sentence is now **declared** and replaced by a rule sentence that governs the same quantity (when the plan is current) — **O2 closed**.
- Modification vs `payplan_payment_schedule`: the installment sentence "The monthly installment is the remaining balance divided by term_months, … rounded up." is now **declared**, replaced by the rule's own order-of-work sentence; the floor case's term is fixed by the new sentence "… and it stays so where min_monthly_payment applies." The patient-requested recomputation that `payplan_evt_adjustments` routes to `payplan_payment_schedule` therefore meets a superseded installment sentence for this policy, leaving one formula — **F1 closed** (task-level confirmation in `1.md` revision_2). Remaining sentences ("No interest …", "the patient may change the installment and term up to modifications_per_plan times", "never going below min_monthly_payment"; `payplan_add_ons_and_holidays` cap and holiday sentences) followed.
- No other base sentence of the referenced policies is handled differently without a declaration.

### factor_ladders (revision 2)

Same 20 factors, labels, `decides`, bindings, tier counts, values and baselines; only names changed for two catch-up factors (`next_installment_pull` tier 2 value `K('pull_share_unreturned')`; `repeat_delinquency_principal_share` with `repeat_share_recent` 0.1 / `repeat_share_older` 0.05 / 0). Counts per policy unchanged (5/6/5/4; 1 method each); multi-source and cross-difficulty coverage per task unchanged. The renames make the names describe the effect (an added principal share for a repeat delinquency; a pull share where no returned fee was booked) — **O7, O8 (naming) closed**. The new pull sentence makes explicit that the pulled amount goes to principal and the coming draft still runs; no tier or value changed, and it is not shown to be a treatment no such business would publish — the substance of O8 remains an observation (R2-O2).

### findings (revision 2)

- Round-1 F1 (SOURCE-POLICY RED): **closed** at charter level (declared overwrite + floor-case term sentence).
- O1, O2, O4, O5, O6, O7: closed. O8: naming closed; semantics retained as R2-O2. O3, O9: kept (observations, unchanged).
- R2-O1 (new, observation): modification docstring describes a queued-draft behaviour that the body does not implement and that the policy conditions on hold_days. Bears on task 1, no scored consequence there.
- R2-O2 (carried, observation): the next-installment pull collects one more installment as principal while the coming draft still runs. Bears on task 0, no scored consequence.
- No new RED at charter level.

### closing_checklist (revision 2)

Written after the round-2 reveals (06:28:36Z onward); the revision_2 charter-global sections above were on disk before them (file hash then `ce5c31ec38086da198bc12ab164e00f269492132ea7d9232e35d8e775f2caa30`).

- Per-task files `0.md`, `1.md` each carry a revision_2 frozen section and comparison; revision 1 text is untouched in all three files.
- Round-1 REDs: F1/T1-1 closed (charter overwrite + term sentence; task 1 has no second installment); T1-2 closed (rationale sentence true of the seed). No new RED; task 0 not regressed by the shared-policy edits.
- Verdicts: task 0 **PASS**; task 1 **PASS**. All four relationships PASS for both tasks.
- Coverage and scope unchanged: {late_fee, catch_up} / {returned_fee, modification}, disjoint and complete; tools closed; uuid8s unchanged and independent.
- Problem trees: 1 prerequisite problem and 1 value_input edge each, owner=user root, acyclic graph across the difficulty.
- Factors: 5/6/5/4 factors with 1 method each, multi-source and cross-difficulty (plan, hardship, plan, plan) per task, all bearing weight; baselines 10.00 / 118.67 / 25.00 / 144.23 differ from 4.32 / 234.04 / 6.48 / 150.78.
- Gates: the orchestrator's post-rework snapshot (all OK, traceability deferred) is for the same hashes I audited (`0723cdf0…`, `69b96164…`, `8a22dc1f…`, `ff643167…`); not re-run by the auditor.
- Open observations (not grounds for rework): O3, O9 (kept with reasons), R2-O1 (modification docstring vs body / hold_days), R2-O2 (pull semantics), persona consent lines.
- **This difficulty passes the source-layer audit at revision 2.** The KB-dependent check_traceability remains deferred to post-render, outside this skill.
