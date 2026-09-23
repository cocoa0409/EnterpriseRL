# Policy-task audit — medicare_advantage_member_services / charter-global

## charter_global_frozen

- freeze time: 2026-09-21 (session clock), written **before any task's GT fields were read**.
- auditor: independent policy-task auditor (erl-task-policy-audit), no part in authoring these artifacts.
- frozen inputs and their hashes (sha256[:16], recomputed from disk at freeze time, all three matching the brief):
  - `env/env_0006_medicare_advantage_plan_sponsor/tasks/medicare_advantage_member_services/advantage.extended.yaml` = `65ff4b9d0b99f56d`
  - `env/env_0006_medicare_advantage_plan_sponsor/tasks/medicare_advantage_member_services/task_tools.py` = `e1816f63751c242e`
  - `.../audits/policy_task/medicare_advantage_member_services/_masked_views/0.masked.json` = `9f36aead56dd0e4d`
  - `.../audits/policy_task/medicare_advantage_member_services/_masked_views/1.masked.json` = `14e53192420be62f`
- also read in full: `blueprint/blueprint.yaml`, `blueprint/products/advantage.yaml` (via the verbatim base section of the extended file), `blueprint/db_schema.json`, `blueprint/share_tools.py`, `skills/erl-task-instantiate/scripts/check_compute.py` (for the restricted-expression semantics of `SUM/COUNT/MAX/LATEST/XSUM/XCOUNT/CFIELD/MONTHS`).
- fields explicitly masked and NOT read while this file was written: `evaluation_criteria`, `computations` (including `expected`, `factor_trace`, `factor_sensitivity`, `baseline_result`, every step/arg), `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`. No prior audit revision exists for this difficulty.
- entry conditions (Step 0): the brief carried the instantiation gate snapshot with actual output lines for `check_extended`, `check_task_tools`, `replay_tasks`, `check_solvability`, `check_compute`, `check_grounding` and `check_cross_fire`, all green, plus the two masked views with hashes. `check_traceability` is legitimately deferred to the render stage and `check_cache_diff` is informational. **Entry conditions met**; the gates are cited, not re-run, and their green light is treated as qualification to enter, not as proof of correctness.
- contamination: none. No task JSON was opened, and no search was run whose match domain could include `tasks/*.json`.

### policy_conflict_scan

Scope of the scan: the 17 base policies carried verbatim in the base section plus the 5 `extended_policies`
(`advantage_ext_premium_subsidy_relief`, `advantage_ext_disenrollment_closing_balance`,
`advantage_ext_pending_election_withdrawal_credit`, `advantage_ext_reinstatement_restored_premium`,
`advantage_ext_corrected_claim_cost_share`).

- **Subjects / target tools / computed quantities.** Each extended policy claims a distinct `subject` event type
  (`advantage_premium_credit_adjustment`, `advantage_voluntary_disenrollment`, `advantage_application_withdrawal`,
  `advantage_reinstatement`, `advantage_claim_adjudication`), a distinct `target_tool` and a distinct `computes`
  name. No `(target_tool, computes)` pair is claimed twice. PASS.
- **Triggers.** `state_due` (subsidy relief, withdrawal credit, reinstatement) and `on_request` (closing balance,
  corrected claim) do not collide: no two policies fire on the same subject.
- **Eligibility / time anchors.** The base gates in force and not overwritten anywhere are
  `advantage_premium_posting.account_open_for_posting` (status ∈ active / premium_grace_period /
  terminated_for_nonpayment on the posting day), `advantage_disenrollment_and_withdrawal.member_request_recorded`
  (an intake with `request_action=voluntary_disenrollment` and `intake_status` ∈ recorded /
  awaiting_member_signature / submitted_to_cms), `advantage_reinstatement_for_good_cause.reinstatement_window_open`
  (`late_payment_reinstatement_window_days` counted from `coverage_end_date`) and `.good_cause_determined`,
  and `advantage_claim_cost_share.coverage_in_force_on_service_date` / `.authorization_on_record`. They are mutually
  compatible and each is anchored on `frozen_time`.
- **Terminal states.** `disenrolled`, `cancelled_before_effective` and `active` are reached by three different
  tools on three different lifecycle edges declared in `lifecycle.transitions`; no two policies drive the same
  holding to different terminal states.
- **Cross-category read boundaries.** Declared reads are `pdp` (subsidy relief: `low_income_subsidy_applied`,
  `pdp_premium_ledger.adjustment_reason_code`) and `allowance` (withdrawal credit: `status`, `current_balance`,
  `allowance_card_ledger.amount`). Both are reads only; no extended policy writes outside `advantage`. PASS.
- **Claimed task scopes.** Derived from the permitted fields alone (the two `user_scenario`s, the two
  `initial_state`s and the `prerequisite` graph), the two tasks partition the five extended policies:
  task 0 = {`advantage_ext_disenrollment_closing_balance` (root), `advantage_ext_premium_subsidy_relief`};
  task 1 = {`advantage_ext_corrected_claim_cost_share` (root), `advantage_ext_reinstatement_restored_premium`,
  `advantage_ext_pending_election_withdrawal_credit`}. Pairwise disjoint and jointly complete. PASS.
- **Conflicts found**: three, all against *base* sentences and all undeclared — see `override_declarations` and
  findings **F1**, **F2**, **F3**.

### rule_compute_equivalence

Swept sentence by sentence in both directions over all five extended policies. Quantities, windows, filters,
tiers, branches, cross-category reads, acting bases, caps/floors and the single end-of-calculation rounding all
carry a verbatim `compute_basis` quotation and a restricted expression; each `factors[].ladder` tier is a
sentence of the `rule` and a branch of the `decides` binding, and each branch of those bindings is a stated tier.
Exceptions found:

1. **`MONTHS(...) + 1` is not "both months included"** (finding **F4**). `advantage_ext_premium_subsidy_relief`
   binds `months_in_force: MONTHS(F('coverage_effective_date'), NOW) + 1` to *"The coverage months reckoned as
   owed are counted from the coverage effective date to the handling date, both months included."*, and
   `advantage_ext_reinstatement_restored_premium` binds `restored_months: (months_since_end + 1) ...` to *"the
   coverage months restored are counted from the coverage end date to the handling date, both months included"*.
   The evaluator's `MONTHS(d1,d2)` is a **whole-month** count that decrements when `day2 < day1`
   (`skills/erl-task-instantiate/scripts/check_compute.py:229-235`), so `MONTHS+1` equals the calendar span
   "both months included" only when the handling day-of-month is not earlier than the anchor day-of-month.
   Where it is earlier the prose and the expression give different integers. Consequence demonstrated on task 1
   in `1.md` (3 vs 4 restored months; two defensible scored values).
2. **"in the contract year" is implemented as "every row on the account"** (observation **O1**).
   `charges_in_year`, `credits_in_year`, `payments_in_year`, `relief_in_year`, `relief_all`, `payments_all`,
   `charges_all` and `advance_payments_all` are `SUM(...)` with **no** `within_months` argument, which the
   evaluator reads as every matching row of that holding whatever its date, while the quoted rule sentences say
   *"posted on it in the contract year"*. `inputs.history` separately declares `within_months: 12`. No consequence
   on either task's world (every seeded ledger row of the target holding is a 2026 row), so this is recorded as an
   observation, not a red light.
3. **A rule class narrower in compute than in prose** (observation **O2**).
   `advantage_ext_corrected_claim_cost_share` states *"where the line the correction restates is an out-of-network
   line whose benefit category is one the plan always covers at the in-network cost share, that share is the
   coinsurance the tier fixes for outpatient dialysis"*, and the base policy it refs defines that class as three
   categories: *"except for emergency, urgently needed and renal dialysis services, which are always covered at
   the in-network cost share"* (`advantage_claim_cost_share.rule`). The expression tests one literal value,
   `line_category != 'dialysis'`. For an out-of-network emergency or urgent-care line prose and compute diverge,
   and the tier's stated outcome (the *dialysis* coinsurance) could not be right for those two categories anyway.
   Neither task's restated line is emergency or urgent care, so no consequence is demonstrable here.
4. **A ladder tier whose stated outcome is not a value of the quantity it decides** (observation **O3**).
   In the same policy, `maximum_out_of_pocket_basis` `decides: moop_limit`, and its second tier reads
   *"where the line the correction restates is an out-of-network line on a tier that pays nothing for
   out-of-network care, nothing further is charged to the member on the line"* — a statement about the result,
   implemented as `moop_limit = 0`. Its condition also overlaps the first tier's (a tier with
   `out_of_network_coinsurance = 100` that also carries an adjudicated out-of-network line satisfies both), the
   compute resolving the overlap by position only. Not reachable on either task's world (Signature PPO = 35,
   Elite Choice PPO = 30).
5. **Two tiers of one ladder that cannot be told apart, as stated** (observation **O4**).
   `advantage_ext_pending_election_withdrawal_credit.card_value_measure` tier 2 reads *"where the member's
   supplemental benefit allowance card carries no balance and the card has been loaded at least once in the last
   six months, the supplemental benefit value measured on the member's card is the balance standing on the
   card"* — i.e. the measure is the balance, which that very tier asserts to be nothing; tier 3 says *"nothing"*.
   The compute (`card_balance if (card_balance <= 0 and card_loads_window > 0) else 0`) makes them identical for
   every card whose balance is zero. Related structural finding **F7**.
6. `advantage_ext_disenrollment_closing_balance.settlement_premium_basis` tier 1, read in the stated order, also
   catches the "no plan premium charge stands" world that tier 2 names (a spread of nothing is not the monthly
   premium); the compute gives tier 2 priority via `premium_charge_count >= 1`. Both readings yield 0 here, so
   this is noted for completeness only.

Otherwise the correspondence is lossless in both directions: no `compute` binding invents a basis absent from the
`rule`, and no `rule` sentence promises a quantity `compute` never forms.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: `post_premium_relief_credit_3acf64b3`/`credit_amount`,
  `end_plan_membership_007ca425`/`closing_premium_balance`,
  `withdraw_pending_election_40acc444`/`premium_standing_to_credit`,
  `reinstate_terminated_coverage_2c8af1d8`/`restored_premium_balance`,
  `post_corrected_claim_line_a6b381de`/`member_cost_share`. Each claimed by exactly one policy. PASS.
- Each tool's subject, base refs, docstring and terminal state admit one business reading; no docstring adds a
  confirmation, review or wait, names another tool, or places its action in a sequence. The recurring Args phrase
  *"read from the member's enrollment record before the call"* orders reading against the call itself, not one
  business action against another, and is uniform across all five tools — not a sequence statement. PASS.
- uuid8s `3acf64b3`, `007ca425`, `40acc444`, `2c8af1d8`, `a6b381de`: five distinct values, no shared prefix, no
  arithmetic or lexical adjacency, no common tail, none reused. Independently generated and frozen with their
  tools. PASS.

### prerequisite_graph

Three edges over five policies, all `prerequisite` fields present (`[]` on the two roots of their own subtrees):

| blocked policy | depends on | kind | gate | form |
| --- | --- | --- | --- | --- |
| `advantage_ext_disenrollment_closing_balance` | `advantage_ext_premium_subsidy_relief` | `value_input` | `credits_allowed` | state |
| `advantage_ext_reinstatement_restored_premium` | `advantage_ext_pending_election_withdrawal_credit` | `state_gate` | `advantage_enrollments.status` | state |
| `advantage_ext_corrected_claim_cost_share` | `advantage_ext_reinstatement_restored_premium` | `value_input` | `accumulated_share` | state |

- every `problem` names another **extended** policy id in this file, never a base policy and never itself; PASS.
- the graph is acyclic (two disjoint chains, 1→2 and 3→4→5); PASS.
- `form: state` on all three, so no `fallback_reason` is required and none is present; PASS.
- `resolved_by` is in each case the depended-on policy's own `target_tool`, and each genuinely makes its `effect`
  hold: `post_premium_relief_credit_3acf64b3` creates the `advantage_premium_credit_adjustment` row that
  `credits_allowed` aggregates; `withdraw_pending_election_40acc444` sets `status='cancelled_before_effective'`,
  vacating `enrollment_submitted`/`cms_transaction_pending`; `reinstate_terminated_coverage_2c8af1d8` sets
  `status='active'` and `coverage_end_date=''`, which is exactly the switch `accumulated_share` branches on. PASS.
- `kind` matches `gate`: `credits_allowed` and `accumulated_share` are real binding names in the blocked
  policies' `compute` (value_input), and `advantage_enrollments.status` is a real eligibility gate (state_gate). PASS.
- no authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears in any
  `prerequisite` field. PASS.

### prerequisite_sentences

Each edge's `policy_source`, tested on the four points, plus the single-reading derivation.

**Edge 1 — closing balance waits on the relief credit.**
> "The closing premium balance is not struck before the premium relief the member is owed stands on the premium account as a credit entry."

Verbatim sentence 2 of `advantage_ext_disenrollment_closing_balance.rule` (its own rule). Ordering connective
*"before"*. State form: what it waits on is a record-visible entry on the premium account, with no performer,
action or tool named; no snake_case, no policy id, no row id. Scope matches the edge `condition`. Exactly one
write of this difficulty brings that state about: `post_premium_relief_credit_3acf64b3` is the only tool that
creates an `advantage_premium_credit_adjustment` row (`task_tools.py:63-91`); `end_plan_membership_007ca425`,
`withdraw_pending_election_40acc444` and `reinstate_terminated_coverage_2c8af1d8` write only
`advantage_enrollments` / `advantage_enrollment_requests`, and `post_corrected_claim_line_a6b381de` only
`advantage_medical_claims`. Derivation in one reading: the sentence names a *premium relief* credit standing on
the premium account → the reader looks for the policy whose result is exactly that, and finds
`advantage_ext_premium_subsidy_relief` (*"The premium relief credited to a member is what the plan gives back on
the plan premium account of a Medicare Advantage enrollment…"*) → its write is the resolving action. The
depended-on rule does not restate the sentence, and no second wording, tool name or other problem id appears.
**One reservation, recorded as observation O5:** the state named is not readable off the record on its own — whether
a credit entry standing on the account *is* "the premium relief the member is owed" can only be settled by
performing the depended-on computation first. Task 0's account carries a credit adjustment at the opening
(`billing_error_correction`, 147.00), so this is not academic; see `0.md`.

**Edge 2 — reinstatement waits on the pending election being gone.**
> "Coverage terminated for non-payment is restored only once no other Medicare Advantage election for the member stands awaiting the transaction reply."

Verbatim last sentence of `advantage_ext_reinstatement_restored_premium.rule`. Ordering connective *"only once"*.
State form, naming a status a reader can see on the enrollment record; no tool, id or performer. Exactly one write
brings it about: `withdraw_pending_election_40acc444` (`status='cancelled_before_effective'`). `end_plan_membership`
also leaves an enrollment out of those statuses, but the charter does not permit it on a pre-effective
application — `lifecycle.transitions` admits `disenrolled` only from `active` and `premium_grace_period`, while
`enrollment_submitted` and `cms_transaction_pending` may only go to `cancelled_before_effective` "by: user", and
base `advantage_disenrollment_and_withdrawal` distinguishes ending an enrollment from withdrawing an application.
So the hop resolves uniquely from the policy surface. Derivation in one reading: sentence → an election of this
member is awaiting the transaction reply → the only policy whose result removes a not-yet-effective election is
`advantage_ext_pending_election_withdrawal_credit` (*"…when an application for a Medicare Advantage plan is
withdrawn before coverage has begun"*). **Reservation, observation O6:** the edge `condition` names a closed set of
two statuses (`enrollment_submitted` **or** `cms_transaction_pending`) while the sentence names one business
state, "awaiting the transaction reply", which reads most naturally onto `cms_transaction_pending` alone — per
`lifecycle`, `enrollment_submitted` is the state *before* the election is placed on the CMS file, so it is
awaiting transmission rather than a reply. The sentence is arguably narrower than the condition. No consequence on
task 1's world (the pending election is `cms_transaction_pending`).

**Edge 3 — the corrected liability waits on coverage standing in force.**
> "A corrected liability is not fixed on a claim line before the enrollment it was rendered under stands in force with no coverage end date recorded on it."

Verbatim sentence 2 of `advantage_ext_corrected_claim_cost_share.rule`. Ordering connective *"before"*; state form
naming two record-visible things in the tables' own words (in force; no coverage end date recorded); no tool,
performer or id; the edge `condition` repeats it at the same strength. Exactly one write brings it about:
`reinstate_terminated_coverage_2c8af1d8` is the only tool that sets `status='active'` **and** clears
`coverage_end_date` (`task_tools.py:200-206`); the other two enrollment writes set an end date or cancel.
Derivation in one reading: sentence → the enrollment must stand in force with no end date → the only policy whose
result restores a terminated enrollment without a break is `advantage_ext_reinstatement_restored_premium` (*"what
a member must pay for the coverage months a terminated enrollment is brought back for… The restoration keeps the
original coverage effective date so that the coverage period is continuous again"*) → its write. PASS with no
reservation.

No rule of this difficulty states a cross-problem order that grounds no declared edge, and no base rule sentence
is being used to ground one of the three edges.

### override_declarations

Sentence-by-sentence sweep of each extended policy against every entry in its `base_policy_refs`. Findings only;
each affected task file demonstrates the cost against its own world.

- **`advantage_ext_premium_subsidy_relief` → `advantage_premium_posting`.** One override declared, and correctly
  named: the base clause *"may never exceed the amount of that charge; a credit larger than one charge is split
  across the charges it relieves"* is replaced by the single-entry rule. The merged semantics are unique, and the
  base sentences not hit — posting order, the dedup gate, *"A credit adjustment always names the single premium
  charge it relieves and the reason it was granted"*, and the `account_open_for_posting` status gate — are
  inherited in full and respected by the extended rule and by the tool. PASS.
- **`advantage_ext_pending_election_withdrawal_credit` → `advantage_disenrollment_and_withdrawal`, `overwrite: []`
  — UNDECLARED OVERRIDE (F1).** Base: *"An application withdrawn before the coverage effective date leaves no
  coverage period at all: the enrollment is cancelled before effective, the disenrollment reason recorded is
  withdrawn_before_effective, **and any premium already paid is refunded in full**."* Extended computes
  `result = money_returned − premium_set_against − benefit_recovery`, i.e. the money paid **less** a plan-premium
  offset and **less** a supplemental-benefit recovery. Two clauses now fight over the same scored quantity and
  nothing in `overwrite` names the base sentence. The extended rule is additionally at war with itself: its own
  first sentence gives the ground *"because a withdrawn application leaves no coverage period at all and nothing
  was ever owed on it"*, and it then subtracts the premium charged on that application as *"the plan premium set
  against it"*. Consequence demonstrated on task 1 in `1.md`.
- **`advantage_ext_corrected_claim_cost_share` → `advantage_claim_cost_share`, `overwrite: []` — UNDECLARED
  OVERRIDE (F2), three distinct sentences.**
  (a) Base: *"Cost share stops at the tier's in-network maximum out-of-pocket"*. Extended's
  `maximum_out_of_pocket_basis` caps an out-of-network line against `combined_moop` instead. `combined_moop`
  appears nowhere in any base **rule** — only in the per-tier parameter list — so base's only normative sentence
  about the cap is the in-network one. Consequence demonstrated on task 1 in `1.md`.
  (b) Base: *"Member cost share on an adjudicated line is taken from the plan allowed amount for the line's
  benefit category at the tier held… Where the category's cost share is a copay the member owes the copay or the
  plan allowed amount, whichever is lower."* Extended fixes the member's share at a coinsurance in every branch
  (`outpatient_surgery_coinsurance`, `out_of_network_coinsurance`, `dialysis_coinsurance`) whatever the restated
  line's category, so for any copay category — primary care, specialist, urgent care, emergency, laboratory,
  ambulance — the two give different numbers. Not demonstrable on either task (both restated lines are
  `outpatient_surgery`), so recorded as a finding of the charter with observation-grade consequence here.
  (c) Base: *"Where the member's Medicaid status gives them cost-share protection on a tier that carries it, the
  member owes nothing on the line and the cost share is billed to the state instead."* The extended policy is
  silent on `dual_eligible_cost_share_protection`. No consequence on task 1 (Signature PPO carries
  `dual_eligible_cost_share_protection: false` and the member's `medicaid_status` is `none`); noted so that it is
  not mistaken for coverage.
- **`advantage_ext_corrected_claim_cost_share` → `advantage_rider_and_allowance_interaction`.** The second base
  ref governs dental/vision/hearing lines and card opening; the extended policy touches neither. No conflict.
- **`advantage_ext_disenrollment_closing_balance` → `advantage_disenrollment_and_withdrawal`, `overwrite: []`.**
  Base's authorisation sentence, the last-day-of-month effective rule and the Original-Medicare warning are
  carried into the extended rule verbatim in substance; the closing-balance arithmetic governs a quantity base
  does not fix. No undeclared override. PASS.
- **`advantage_ext_reinstatement_restored_premium` → `advantage_reinstatement_for_good_cause`, `overwrite: []`.**
  Base's window, the reviewer's recorded determination, the continuity of the effective date, *"the member must
  pay every premium owed for the months the coverage is restored for"* and the once-only rule are all inherited;
  extended fixes how much is owed, which base leaves open, and its `good_cause_excused_months` ladder *excuses*
  some of those months — a narrowing of *"every premium owed"* that is arguable rather than contradictory, but
  see **F6** for what that ladder's conditions rest on. No undeclared override recorded.
- **Undefined term shared by three policies — "relief credit" (F3).** `advantage_ext_premium_subsidy_relief`
  (*"the relief already set off is every relief credit posted on the account"*),
  `advantage_ext_disenrollment_closing_balance` (*"the relief allowed against the settlement is every relief
  credit posted on the account"*) and `advantage_ext_reinstatement_restored_premium` (*"the relief allowed
  against it is every relief credit posted on the account"*) all turn on a term the charter never defines, and
  each binds it to `COUNT/SUM('advantage_premium_ledger', event_type='advantage_premium_credit_adjustment')` —
  **every** credit adjustment whatever its `adjustment_reason_code`. The charter's own tool enumerates seven
  reasons of which only `low_income_subsidy_premium_reduction` is the relief these policies grant, and the same
  rules qualify the *PDP-side* credit by its reason (*"a low income premium subsidy credit"*), which makes the
  narrow reading of the unqualified advantage-side term at least as defensible as the broad one. Both task worlds
  seed credit adjustments carrying other reasons, so the two readings produce different scored values on both
  tasks; demonstrations in `0.md` and `1.md`.

### factor_ladders

Structure only. Per policy: declared factors, effect labels, `decides` bindings, disjointness of binding sets,
tier counts, whether every tier is stated in the `rule` and implemented in `compute`, whether any two tiers of one
ladder select the same value or method, and whether each condition and outcome is one this line of business holds.

| policy | factors | labelled param / method | ladder tiers | binding sets disjoint | every tier in `rule` + `compute` |
| --- | --- | --- | --- | --- | --- |
| `advantage_ext_premium_subsidy_relief` | 5 | 2 / 3 | 3,4,3,3,3 | yes | yes |
| `advantage_ext_disenrollment_closing_balance` | 5 | 2 / 3 | 3,3,3,3,3 | yes | yes |
| `advantage_ext_pending_election_withdrawal_credit` | 4 | 2 / 2 | 3,3,3,3 | yes | yes |
| `advantage_ext_reinstatement_restored_premium` | 6 | 3 / 3 | 3,3,3,3,3,3 | yes | yes |
| `advantage_ext_corrected_claim_cost_share` | 5 | 2 / 3 | 3,3,3,3,3 | yes | yes |

Counts are within 4–6 everywhere, every `decides` names an input rather than `result`, every ladder has at least
three tiers stated in full in the `rule`, and every tier's value or method is drawn from the charter
(`K(...)`, `P(...)` or an aggregate the rule names). Multi-source and cross-difficulty coverage per task, as
declared: task 0's policies carry `member_premium_share` and `subsidy_award_reachback` reading `pdp`, and several
conjunctive tiers over distinct records (`owed_month_count`, `premium_reckoned_selection`,
`settlement_payment_selection`); task 1's carry `card_value_measure` and `card_recovery_rate` reading
`allowance`, and conjunctive tiers in `returned_payment_selection`, `restored_month_count` and
`restated_line_selection`. Whether those seeded rows exist, and whether each factor bears weight, is decided in
the task files.

Three structural defects:

- **F5 — the effect labels are not honest, and the honest `parameter` count then falls below the floor.**
  A tier that substitutes a different *number* into one fixed formula selects a value (`parameter`); a tier that
  changes *which rows are aggregated* or *which formula computes the quantity* selects a method. The charter
  applies that distinction inconsistently to ladders of identical shape:
  - `advantage_ext_premium_subsidy_relief.relief_set_off_selection` — "every relief credit posted in the contract
    year" / "the relief credits posted in the last three months" / "nothing" — is labelled **method**;
  - `advantage_ext_disenrollment_closing_balance.settlement_relief_allowance` and
    `advantage_ext_reinstatement_restored_premium.restoration_relief_allowance` — the *same* three-way window
    selection over the *same* credit rows — are labelled **parameter**;
  - `advantage_ext_premium_subsidy_relief.premium_reckoned_selection`,
    `advantage_ext_disenrollment_closing_balance.settlement_payment_selection`,
    `advantage_ext_reinstatement_restored_premium.owed_premium_reckoning` and `.recognised_payment_selection` —
    year-window / three-month-window / most-recent — are labelled **method**, while
    `advantage_ext_pending_election_withdrawal_credit.plan_premium_offset` — sum-all / most-recent / nothing — is
    labelled **parameter**.
  - `advantage_ext_disenrollment_closing_balance.settlement_premium_basis` (**parameter**) selects between
    `P('monthly_plan_premium') × billed_month_span`, `0` and `SUM(charges)` — three different formulas.
  - `advantage_ext_reinstatement_restored_premium.restored_month_rate` (**parameter**) selects between
    `SUM(charges)/span`, the most recent charge and `P('monthly_plan_premium')`.
  Counting only the ladders that select a number — `member_premium_share` (1.0/0.5/0.25/0.0),
  `subsidy_award_reachback` (3/1/0 months), `card_recovery_rate` (1.0/0.5/0.0),
  `good_cause_excused_months` (2/1/0), `member_share_rate` (three tier coinsurances) and
  `maximum_out_of_pocket_basis` (two tier MOOP figures) — the honest per-policy `parameter` counts are:
  subsidy relief **2**, corrected claim **2**, withdrawal credit **1**, reinstatement **1**, closing balance **0**,
  against a floor of 2. The gates count labels, so the shortfall is invisible to them.
- **F6 — two ladders divide their customers by a condition that holds of every customer who reaches the write.**
  - `advantage_ext_reinstatement_restored_premium.good_cause_excused_months` keys tiers 1 and 2 on *"a request for
    reinstatement stands recorded on the enrollment"* (`COUNT('advantage_enrollment_requests',
    request_action='reinstatement_for_good_cause') >= 1`) and its fall-through on the negation. But base
    `advantage_reinstatement_for_good_cause.good_cause_determined` *requires* that determination to be recorded on
    the enrollment intake before the reinstatement is processed — *"without the reviewer's recorded decision the
    reinstatement is refused"* — and `db_schema.json` gives `advantage_enrollment_requests` no status or field
    that could record the determination other than the row itself (`intake_status` ∈ recorded /
    awaiting_member_signature / submitted_to_cms / completed / cancelled). The tool moreover takes
    `advantage_enrollment_request_id` as a required argument. So the condition restates the policy's own
    eligibility gate: the fall-through tier is unreachable, the ladder has two live tiers against a floor of
    three, and its baseline (`standard_excused_months` = 0) is the value of a tier no customer can ever be on.
  - `advantage_ext_pending_election_withdrawal_credit.returned_payment_selection` splits tiers 1 and 2 on
    *"at least one recorded request stands on the application"* vs *"no recorded request stands on the
    application"* (`COUNT('advantage_enrollment_requests', request_action='voluntary_disenrollment')`). Base
    `advantage_disenrollment_and_withdrawal.member_request_recorded` `applies_to` **both**
    `advantage_voluntary_disenrollment` **and** `advantage_application_withdrawal` and demands an intake with
    `request_action=voluntary_disenrollment` before the enrollment is ended — and the schema offers no separate
    withdrawal action. Tier 2 is therefore unreachable too, leaving two live tiers.
- **F7 — a ladder with two tiers that select the same value.**
  `advantage_ext_pending_election_withdrawal_credit.card_value_measure` tiers 2 and 3 both evaluate to nothing for
  any card whose balance is zero (tier 2 measures the value as *"the balance standing on the card"* under the
  condition that the card *"carries no balance"*; tier 3 says *"nothing"*), and an allowance card balance is never
  negative. One tier written as two; see `rule_compute_equivalence` item 5.

### findings

Each names the tasks it bears on, so that their files pick up the demonstration rather than restate the finding.

- **F1 — SOURCE-POLICY RED (undeclared override).** `advantage_ext_pending_election_withdrawal_credit` deviates
  from base *"any premium already paid is refunded in full"* with `overwrite: []`, and contradicts its own stated
  ground (*"nothing was ever owed on it"*) by subtracting the plan premium charged. Bears on **task 1**.
  Artifact: `advantage.extended.yaml` (extended policy 3: `rule`, `compute.premium_set_against`, `overwrite`).
- **F2 — SOURCE-POLICY RED (undeclared override, three base sentences).**
  `advantage_ext_corrected_claim_cost_share` with `overwrite: []` supersedes base's in-network MOOP cap (a),
  base's per-category copay/coinsurance rule (b), and is silent on base's Medicaid cost-share protection (c).
  Bears on **task 1** (a demonstrated there; b and c observation-grade on that world).
  Artifact: `advantage.extended.yaml` (extended policy 5: `rule`, `compute.moop_limit`, `compute.share_rate`, `overwrite`).
- **F3 — SOURCE-POLICY RED (undefined term, two defensible readings).** "relief credit" in three extended
  policies is bound to every `advantage_premium_credit_adjustment` row irrespective of `adjustment_reason_code`.
  Bears on **task 0** and **task 1**; both worlds seed credit adjustments with other reasons.
  Artifact: `advantage.extended.yaml` (extended policies 1, 2, 4: the `relief_set_off` / `credits_allowed` /
  `relief_allowed` sentences and bindings).
- **F4 — SOURCE-POLICY RED (rule/compute equivalence).** *"both months included"* is implemented as
  `MONTHS(...) + 1`, which is a whole-month count. Bears on **task 1** (demonstrated); harmless on task 0.
  Artifact: `advantage.extended.yaml` (extended policy 1 `months_in_force`, extended policy 4 `restored_months`).
- **F5 — SOURCE-FACTOR RED (dishonest effect labels; `parameter` floor missed).** Bears on **task 0** (closing
  balance: 0 honest `parameter` factors) and **task 1** (withdrawal credit and reinstatement: 1 each).
  Artifact: `advantage.extended.yaml` (`factors[].effect` in extended policies 2, 3, 4).
- **F6 — SOURCE-FACTOR RED (unreal ladders: a tier condition that restates the write's own eligibility gate).**
  Bears on **task 1** (both affected ladders are in task 1's policies).
  Artifact: `advantage.extended.yaml` (extended policy 4 `good_cause_excused_months`, extended policy 3
  `returned_payment_selection`), against base `advantage_reinstatement_for_good_cause.good_cause_determined` and
  `advantage_disenrollment_and_withdrawal.member_request_recorded`.
- **F7 — SOURCE-FACTOR RED (two tiers, one outcome).** `card_value_measure` tiers 2 and 3. Bears on **task 1**.
  Artifact: `advantage.extended.yaml` (extended policy 3 `card_value_measure`, `compute.benefit_value`).
- **O1–O6 — observations** (no consequence demonstrable on either world): the "contract year" windows that are
  implemented unwindowed; the narrowed always-covered-at-in-network class; the `moop_limit` tier whose outcome is
  a statement about the result and whose condition overlaps its neighbour; `card_value_measure`'s
  as-stated tier collision; the state named by edge 1 not being readable off the record without first performing
  the depended-on computation; and "awaiting the transaction reply" being arguably narrower than the two statuses
  the edge condition names.

## closing_checklist

Written after both tasks' `source_gt_comparison` (reveal: 2026-09-21, after all three files were frozen).
**The difficulty does not close.** Step 4's checklist is recorded item by item with its actual state.

- **Per-task files correspond one-to-one with the tasks** — `0.md` and `1.md` alongside this file; no prior
  revision exists, so nothing needed preserving. Both carry a frozen `source_derivation_frozen` written before
  any reveal and a `source_gt_comparison` written after. **Neither comparison carries a PASS**: task 0 is
  SOURCE-POLICY / SOURCE-FACTOR / SOURCE-TASK RED with the problem tree PASS; task 1 is SOURCE-POLICY /
  SOURCE-FACTOR / SOURCE-TASK RED with the problem tree PASS. ✗
- **Coverage and scope exclusivity** — the five extended policies are fully covered, and `charter_scope` confirms
  the partition derived blind: task 0 {`advantage_ext_premium_subsidy_relief`,
  `advantage_ext_disenrollment_closing_balance`}, task 1 {`advantage_ext_pending_election_withdrawal_credit`,
  `advantage_ext_reinstatement_restored_premium`, `advantage_ext_corrected_claim_cost_share`}. Each scope spans a
  whole problem tree, root and prerequisites. Task tools and GT are closed: five tools, each claimed by exactly
  one policy and called in exactly one task. Each uuid8 (`3acf64b3`, `007ca425`, `40acc444`, `2c8af1d8`,
  `a6b381de`) is independently generated, frozen, unreused and not batch-derived. ✔
- **Problem trees** — task 0: 1 prerequisite problem, 1 `value_input` edge (floor 1), the root itself an
  `owner=user` write, no cycle. Task 1: 2 prerequisite problems, 1 `value_input` edge (floor 1), one
  `owner=user` write (the withdrawal), no cycle. The difficulty's three `prerequisite` edges together form a
  directed acyclic graph — two disjoint chains, no cross-task reference, no cycle. ✔
- **Computations, baselines and factors** — every computation declares a self-sufficient baseline yielding a
  definite number different from gold (0.00 / 793.00 on task 0; 63.40 / 229.30 / 0.00 on task 1 — two of those
  five are the degenerate floor, recorded as observations `0-O2` and `1-O2`), every declared factor bears weight
  on its own world against a baseline that is what `baseline.rule` states, and the auditor's 27 baseline
  recomputations match `factor_sensitivity` figure for figure. Factor **counts** are within 4–6 and every ladder
  states three or more tiers in its rule. **But** the effect labels are not honest (**F5**: three policies fall
  below the floor of 2 `parameter` factors once ladders that choose rows or formulas are counted as `method`),
  two ladders have an unreachable fall-through (**F6**), one ladder has two tiers with the same outcome
  (**F7**), one tier of task 1's root computation agrees with a cached field on the holding (`1-R1`), and two
  tier outcomes are treatments this line of business does not give (`0-R3`, `1-R3`). ✗
- **Instantiation-stage gates** — cited from the brief's snapshot, not re-run (Step 0 forbids the auditor running
  them, and Step 4's re-run belongs to a close-out that is not happening): `check_extended`, `check_task_tools`,
  `replay_tasks`, `check_solvability`, `check_compute`, `check_grounding` and `check_cross_fire` were all green
  on the artifacts whose hashes this audit froze (`65ff4b9d0b99f56d`, `e1816f63751c242e`). Every defect above
  sits in the space those gates do not reach: an undeclared override is invisible to a gate that does not read
  base prose, an `effect` label is counted rather than tested, a tier whose condition restates an eligibility
  gate still parses, and a cached field that agrees with a tier is just another number in the seed.

**Difficulty verdict: FAIL.** Policy self-consistency fails (F1, F2, F3, F4); factors bear weight numerically but
fail structurally and on realism (F5, F6, F7, `0-R3`, `1-R1`, `1-R3`); the unique-solution relationship fails on
both tasks, with second and third defensible values written out for four of the five scored parameters. The
problem-tree relationship passes on both tasks. Both independent derivations reproduced GT exactly at every item
and every figure, so none of this is a disagreement about the answer: it is that the published material does not
entail that answer alone.

---

# revision_2 — charter-global re-audit

## charter_global_frozen (revision 2)

- freeze time: 2026-09-21 (session clock), written **before any reworked task JSON was opened**.
- auditor: the same independent policy-task auditor. **This round is not blind and is not presented as one:**
  revision 1's reveal put this difficulty's round-1 GT in my hands. What is preserved is the weaker but still
  meaningful ordering — every figure below was derived from the reworked charter and the rebuilt masked worlds and
  written to disk *before* `tasks/0.json` and `tasks/1.json` were read at revision 2. Where a round-1 value
  survives unchanged into round 2 I say so rather than implying I rediscovered it.
- hashes recomputed from disk, all six matching the brief:
  - `advantage.extended.yaml` `477d67e46794e35c` (revision 1: `65ff4b9d0b99f56d` — **CHANGED**, 3964 → 4040 lines)
  - `task_tools.py` `e1816f63751c242e` (revision 1: identical — **UNCHANGED**)
  - `tasks/0.json` `d0daadc5d8767219`, `tasks/1.json` `03a44b42e6040bf1` (both CHANGED; unread at freeze)
  - `_masked_views/0.masked.json` `d024af4f53ffa78a`, `_masked_views/1.masked.json` `ee68227ba28e4f12` (both CHANGED)
- **carry-forward rule applied:** the charter hash moved, so this section is re-derived in full rather than carried
  forward. `task_tools.py` is byte-identical, so the uuid8 and docstring conclusions of revision 1
  (`### action_binding_and_uuids`) are carried forward by hash and re-stated only where the charter's side of the
  pairing moved.
- entry conditions: the brief carried the re-run gate snapshot (all seven green on the reworked form) and both
  rebuilt masked views with hashes. Cited, not re-run.
- contamination: none beyond the disclosed revision-1 knowledge above.

### base_section_integrity (revision 2)

Parsed both files and compared structurally: the extended file's base section is equal to
`blueprint/products/advantage.yaml` key for key and policy for policy, with `extended_policies` the only extra
top-level key. **The base copy has not been rewritten.** The four base sentences this audit argues from are all
present verbatim: *"No premium is charged for a coverage month beginning after the coverage end date…"*,
*"Cost share stops at the tier's in-network maximum out-of-pocket…"*, *"…and any premium already paid is refunded
in full"*, *"…except for emergency, urgently needed and renal dialysis services, which are always covered at the
in-network cost share"*, *"A quarterly billing frequency bills three coverage months in one charge…"* and
*"Where the member's Medicaid status gives them cost-share protection…"*.

### policy_conflict_scan (revision 2)

Subjects, target tools and computed quantities are unchanged and still claimed by exactly one policy each;
triggers, eligibility gates, time anchors and terminal states remain mutually compatible; the two task scopes are
still the same partition of the five extended policies. Cross-category reads moved from two policies to four:
`advantage_ext_premium_subsidy_relief` (pdp), `advantage_ext_disenrollment_closing_balance` (pdp, **new**),
`advantage_ext_pending_election_withdrawal_credit` (**osb, replacing allowance**) and
`advantage_ext_reinstatement_restored_premium` (pdp, **new**).

One conflict found, recorded as **N3** below.

### cross_category_declaration_field_level (revision 2)

Tested directly, on the sibling difficulty's lead rather than on faith: every `CFIELD` / `CPARAM` / `XSUM` /
`XCOUNT` / `XMAX` / `XLATEST` / `EXISTS` call in all five policies' `compute` was extracted and matched against
that policy's `cross_category[].reads`.

| policy | declared reads | calls actually made | field-level match |
| --- | --- | --- | --- |
| subsidy relief | pdp: `low_income_subsidy_applied`, `pdp_premium_ledger.adjustment_reason_code` | `CFIELD('pdp','low_income_subsidy_applied')`, `XCOUNT('pdp','pdp_premium_ledger', … adjustment_reason_code=…)` | ✔ |
| closing balance | pdp: `low_income_subsidy_applied` | `CFIELD('pdp','low_income_subsidy_applied')` | ✔ |
| withdrawal credit | osb: `status`, `rider_premium_balance_due`, `osb_rider_premium_ledger.amount` | `CFIELD('osb','rider_premium_balance_due')`, `CFIELD('osb','status')`, `XSUM('osb','osb_rider_premium_ledger','amount',…)`, `XCOUNT('osb','osb_rider_premium_ledger',…)` ×2 | ✔ |
| restored premium | pdp: `low_income_subsidy_applied` | `CFIELD('pdp','low_income_subsidy_applied')` | ✔ |
| corrected claim | — | none | ✔ |

**The sibling difficulty's defect does not reproduce here.** Every field a policy reads from another category is
named in that policy's own `reads` list, and `inputs.cross_category` / `inputs.history` name the same categories
and tables. The only undeclared thing any cross-category call touches is the `event_type` filter that selects the
event family within a declared table, which is uniform across the charter and is how the round-1 form also stood.

### rule_compute_equivalence (revision 2)

Re-swept in both directions over all five reworked policies. **Two of revision 1's three equivalence defects are
genuinely closed, and one new one has been introduced.**

- **F4 closed.** Every "both months included" phrase is gone. `months_in_force` is now quoted by *"The coverage
  months reckoned as owed are the whole months that have passed since the coverage effective date, and one more
  for the month in hand"*, and `restored_months` tier 1 by *"the whole months that have passed since the coverage
  end date, and one more for the month in hand"*. Both are exactly `MONTHS(anchor, NOW) + 1` under the
  evaluator's day-adjusted whole-month count, so prose and expression now agree for every day-of-month. Checked
  on both worlds: task 0 gives 9 by prose and 9 by expression; task 1 gives 3 by prose and 3 by expression —
  where revision 1's prose gave 4 against the expression's 3.
- **O2 closed, and closed properly rather than narrowed.** The dialysis tier now reads *"that share is the
  coinsurance the tier fixes for outpatient dialysis, **that being the only such benefit category the tier prices
  by a coinsurance**"*, and the rule's opening sentence scopes the whole policy to coinsurance-priced categories.
  The base class is {emergency, urgently needed, renal dialysis}; of those, emergency and urgent care are priced
  by `emergency_room_copay` / `urgent_care_copay` and only dialysis by `dialysis_coinsurance`, so the compute's
  `line_category != 'dialysis'` now implements exactly what the rule says. Verified against the tier parameter
  list.
- **O3 closed.** `maximum_out_of_pocket_basis` tier 2 now states a value of the quantity it decides (*"the
  maximum out-of-pocket the line is capped against is nothing"*) instead of a statement about the result, and its
  condition is now the exclusive complement of tier 1 (*"pays for covered out-of-network care"* versus *"pays
  nothing for covered out-of-network care"*), so the old positional overlap is gone.
- **O1 persists** (unwindowed `SUM` behind "in the contract year"); not claimed closed, no consequence on either
  world, still an observation.
- **N1 (new, three policies).** See `### findings`.

### action_binding_and_uuids (revision 2)

`task_tools.py` is byte-identical to the round-1 artifact (`e1816f63751c242e`), so revision 1's conclusions on
uuid8 independence, docstring silence about sequence and one-policy-per-tool are carried forward on that hash.
Re-checked on the charter's side only: the five `(target_tool, computes)` pairs are unchanged and each is still
claimed by exactly one policy. The reworker's stated ground for leaving the module untouched — that no round-1
finding turned on a tool contract — matches revision 1's record: none of F1–F7, 0-R1–0-R3 or 1-R1–1-R8 named a
tool contract as its affected artifact.

### prerequisite_graph and prerequisite_sentences (revision 2)

Re-derived; the graph is unchanged in shape and all three edges re-verify mechanically.

| blocked | depends on | kind | gate | gate is a real binding | `policy_source` verbatim in own rule | restated in depended rule | `resolved_by` = depended `target_tool` |
| --- | --- | --- | --- | --- | --- | --- | --- |
| closing balance | subsidy relief | value_input | `relief_allowed` (**renamed** from `credits_allowed`) | ✔ | ✔ | ✗ (correct) | ✔ |
| restored premium | withdrawal credit | state_gate | `advantage_enrollments.status` | n/a (eligibility field) | ✔ | ✗ (correct) | ✔ |
| corrected claim | restored premium | value_input | `accumulated_share` | ✔ | ✔ | ✗ (correct) | ✔ |

All three are `form: state` with no `fallback_reason`, which is correct for the state form. The three sentences
are unchanged in wording; the restoration's has moved from the end of its rule to its second sentence, which
changes nothing about the four-point test. Every state is still brought about by exactly one write of this
difficulty (the tool module is unchanged). Every other ordering word in the five rules was extracted and checked:
*"withdrawn before coverage has begun"*, *"applied first to the rider premium"*, *"cancelled before it ever takes
effect"*, *"at least one whole month before the handling date"*, *"the amount after the deductible"* — none states
an order between two problems, so no undeclared dependency has been introduced. O5 and O6 persist unchanged and
are still observations.

### override_declarations (revision 2)

Re-swept sentence by sentence against each `base_policy_refs` entry.

- **F1 closed.** `advantage_ext_pending_election_withdrawal_credit.overwrite` now names the base clause
  *"and any premium already paid is refunded in full"* and states what replaces it. The rule's self-contradiction
  is gone with it: the plan-premium offset has been removed entirely, so the policy no longer subtracts a premium
  from a refund it calls *"nothing was ever owed on it"* — what it now subtracts is a rider premium the member
  genuinely owes on a separate account.
- **F2(a) closed.** `advantage_ext_corrected_claim_cost_share.overwrite` now names *"Cost share stops at the
  tier's in-network maximum out-of-pocket"* and states the combined-MOOP replacement.
- **F2(b) closed, by scoping rather than by override.** The rule now opens *"…and it is fixed this way on a line
  whose benefit category the tier held prices by a coinsurance; a line whose benefit category the tier held prices
  by a copay is outside this rule and is restated on the copay basis the plan's cost-share rules already fix for
  it"*. That leaves base's per-category copay sentence in force rather than overriding it, which is the stronger
  fix.
- **F2(c) declined, and the decline holds on both worlds.** The extended policy is still silent on base's Medicaid
  cost-share protection. Neither reseeded member has Medicaid (`customers.medicaid_status = "none"` on task 1;
  task 1 is the only task that adjudicates a claim), and the tier held carries
  `dual_eligible_cost_share_protection: false`, so no consequence is demonstrable. Observation, as in revision 1.
- **F3 closed.** The undefined term is gone from all three policies that used it: *"relief credit"* is now
  *"credit adjustment … **whatever reason each of them carries**"* in `relief_set_off`, `relief_allowed`
  (closing balance) and `relief_allowed` (restored premium), in the rule, the `compute_basis` and the ladder
  alike. The compute was always `event_type='advantage_premium_credit_adjustment'` with no reason filter; the
  prose now says exactly that, so the narrow reading is no longer available.
- **N3 (new).** `advantage_ext_disenrollment_closing_balance` still carries `overwrite: []` while its new
  `final_period_months` tier conflicts with a base sentence. See `### findings`.

### factor_ladders (revision 2)

| policy | factors | labelled param / method | honest param (a tier selects a figure) | ladders ≥ 3 tiers, all stated in rule | binding sets disjoint |
| --- | --- | --- | --- | --- | --- |
| subsidy relief | 5 | 2 / 3 | **2** (`member_premium_share` 0.0/0.75/0.5/1.0, `subsidy_award_reachback` 3/1/0) | ✔ | ✔ |
| closing balance | 5 | 2 / 3 | **2** (`final_period_months` 3/1/0, `unbilled_month_share` 0.0/0.75/0.5/1.0) | ✔ | ✔ |
| withdrawal credit | 4 | 2 / 2 | **2** (`rider_arrears_offset` 1.0/0.5/0.0, `rider_offset_ceiling` 150/75/0) | ✔ | ✔ |
| restored premium | 6 | 2 / 4 | **2** (`restored_month_share` 0.0/0.75/0.5/1.0, `arrears_collection_share` 0.5/0.75/1.0) | ✔ | ✔ |
| corrected claim | 5 | 2 / 3 | **2** (`maximum_out_of_pocket_basis` combined/nothing/in-network, `member_share_rate` three tier coinsurances) | ✔ | ✔ |

- **F5 closed.** Every ladder that merely chooses which rows to aggregate is now labelled `method`
  (`settlement_relief_allowance` and `restoration_relief_allowance` have both been relabelled; the old
  `settlement_premium_basis`, `restored_month_rate` and `plan_premium_offset` are gone). Every policy now carries
  two ladders that genuinely select a figure, so the floor of 2 `parameter` factors is met in substance and not
  only in label. Checked by reading each ladder's outcomes, not its `effect` string.
- **F6 closed, both instances.** `good_cause_excused_months` has been removed from the restoration policy
  altogether; `returned_payment_selection` no longer keys on "a recorded request stands on the application" and
  now divides on payment counts alone (three or more / exactly two / fewer than two). Neither surviving ladder
  restates its write's own base eligibility gate.
- **F7 closed.** `card_value_measure`, whose tiers 2 and 3 selected the same value, is gone with the rest of the
  allowance-card machinery.
- **N1, N2, N4, N5 (new).** See `### findings`.

### findings (revision 2)

Revision-1 items are settled in the two task files where their consequences were demonstrated, and summarised in
`## closing_checklist (revision 2)` below. The charter-global items below are **new in this round**.

- **N1 — SOURCE-POLICY RED (rule/compute contradiction; a regression). The seventy-five-per-cent subsidy tier
  selects 0.75 where its own rule sentence says a quarter.** In three policies the rule reads *"where that record
  shows a seventy-five per cent subsidy, the member meets **a quarter** of it"* (subsidy relief), *"…a quarter of
  it is charged"* (closing balance) and *"…the member meets a quarter of it"* (restored premium), while the
  ladder value and the binding for that tier are `K('three_quarter_member_share')` = **0.75** and
  `K('three_quarter_share')` = **0.75**:
  `member_share: … K('three_quarter_member_share') if subsidy_award == 'partial_subsidy_75' …`,
  `unbilled_share: … K('three_quarter_share') if subsidy_award == 'partial_subsidy_75' …`,
  `restored_share: … K('three_quarter_share') if subsidy_award == 'partial_subsidy_75' …`.
  *Demonstrated consequence, in the same situation:* for a member whose drug-plan record shows
  `partial_subsidy_75`, the rule makes one coverage month cost `monthly_plan_premium × 0.25` and the compute makes
  it `monthly_plan_premium × 0.75` — on task 0's tier, 11.90 against 35.70 a month, and on task 1's, 22.33
  against 66.98. It is also the wrong way round as business: a seventy-five per cent subsidy that leaves the
  member paying seventy-five per cent is not a subsidy. **This is a regression**: revision 1's charter carried
  `quarter_member_share: 0.25` bound to that tier and was correct. Neither reseeded world carries a
  `partial_subsidy_75` member, so no scored value moves — but the defect is in the published rule that the KB will
  render, and `partial_subsidy_75` is a seeded-enum value (`db_schema.json` `pdp_enrollments.low_income_subsidy_applied`).
  *Affected artifact:* `advantage.extended.yaml`, the `params`, `rule`, `compute_basis`, `compute` and
  `factors[].ladder` of `advantage_ext_premium_subsidy_relief.member_premium_share`,
  `advantage_ext_disenrollment_closing_balance.unbilled_month_share` and
  `advantage_ext_reinstatement_restored_premium.restored_month_share`.

- **N2 — SOURCE-FACTOR RED (a tier outcome that line of business does not give). A twenty-five per cent subsidy
  is given no effect at all.** The same three ladders end *"where that record shows a **twenty-five per cent
  subsidy or no subsidy at all**, the member meets the whole of it"*, mapping the real enum value
  `partial_subsidy_25` onto the member paying one hundred per cent of the premium. A plan sponsor that records a
  twenty-five per cent low-income subsidy for a member and then charges the member the whole premium has not
  applied the subsidy; the value that belongs to that case is exactly the 0.75 the rework has misfiled on the
  seventy-five per cent tier, which is what makes N1 and N2 one mistake seen from two sides. Four tiers are
  stated, but only three of the enum's five states are given their own treatment.
  *Affected artifact:* as N1.

- **N3 — SOURCE-POLICY RED (undeclared conflict with a base sentence).** `advantage_ext_disenrollment_closing_balance`
  carries `overwrite: []` and its new `final_period_months` tier 1 reads *"Where the enrollment is billed
  quarterly and the plan premium charges standing on the account cover fewer coverage months than the enrollment
  has been in force, the coverage months the settlement still charges for are **the three coverage months of the
  quarter in hand**"*. Base `advantage_premium_billing` says *"No premium is charged for a coverage month
  beginning after the coverage end date, and a charge already posted for such a month is relieved by a credit
  adjustment rather than left outstanding"*, and base `advantage_disenrollment_and_withdrawal` fixes the coverage
  end date at *"the last day of the month in which the plan received their request"*.
  *Demonstrated consequence, in the same situation:* a quarterly-billed member whose unbilled quarter has just
  begun — say the quarter in hand is October–December and the plan receives the request in October — is charged
  three coverage months by the extended rule and one by the base rule, because November and December begin after
  the coverage end date. Two defensible closing balances differing by two months' premium. Neither reseeded world
  instantiates it: task 0's member leaves in the last month of her unbilled quarter, so all three months of the
  quarter in hand fall inside her coverage. The conflict is in the rule, not in the seed.
  *Affected artifact:* `advantage.extended.yaml`, `advantage_ext_disenrollment_closing_balance.overwrite` (empty),
  `.rule` (the coverage-months-still-charged-for paragraph), `compute.final_months`.

- **N4 and N5 — SOURCE-FACTOR REDs in the replacement withdrawal-credit factors.** Both are facts about task 1's
  world and are demonstrated in `1.md § factor_weight (revision 2)`: `rider_offset_ceiling`'s two live tiers are
  score-identical there, and `rider_owing_measure`'s tier taken is reproduced exactly by a seeded field, which is
  the shape of revision 1's `1-R1` reappearing in the factor that replaced the one it was found in.

## closing_checklist (revision 2)

Written after both tasks' revision-2 comparisons. **The difficulty still does not close**, on a much shorter list
than revision 1's: three charter-level defects, two of which are new-in-this-round and one of which is a
regression, plus two task-level factor defects and one proof defect.

**Every round-1 RED is genuinely closed, verified against the artifacts.** I checked each against the reworked
charter and the reseeded rows rather than against the reworker's account; the per-item verdicts and evidence are
in `0.md § findings (revision 2)` and `1.md § findings (revision 2)`.

| round-1 item | verdict at revision 2 | how it was closed |
| --- | --- | --- |
| F1 | closed | base clause named in `overwrite`; the contradicting offset removed |
| F2(a) | closed | base clause named in `overwrite` |
| F2(b) | closed | the policy scopes itself to coinsurance-priced categories, leaving base in force |
| F2(c) | declined, accepted | no consequence demonstrable on either world |
| F3 | closed | "credit adjustment … whatever reason each of them carries", in rule, basis and ladder |
| F4 | closed | "the whole months that have passed … and one more for the month in hand" — exactly `MONTHS+1` |
| F5 | closed | relabelling plus three ladders replaced; every policy now has two ladders that select a figure |
| F6 | closed (both) | one ladder removed, one re-keyed off the write's own eligibility gate |
| F7 | closed | the ladder with two identical outcomes removed with the allowance machinery |
| 0-R1, 0-R2, 0-R3 | closed | see `0.md` |
| 1-R1 … 1-R8 | closed | see `1.md`; `1-R1` closed by reseeding and verified by recomputing all three readings |
| O2, O3 (revision 1) | closed | the dialysis class now stated as the rule means it; the MOOP tier now states a value and its condition is exclusive |
| O1, O5, O6 (revision 1) | persist | unwindowed "contract year"; the relief gate's state not readable without the depended-on computation; "awaiting the transaction reply" against a two-status condition |

**Nothing already closed has regressed — with one exception, which is the sharpest finding of this round.**
Revision 1's charter bound the seventy-five-per-cent subsidy tier to `quarter_member_share: 0.25` and was
correct. Revision 2 renamed the parameter and changed its value to 0.75 while leaving all three rule sentences
saying "a quarter", so a tier that was right is now wrong in three policies at once (**N1**), and the enum value
`partial_subsidy_25` has been swept into the no-subsidy fall-through (**N2**). The revealed
`design_rationale` of `tasks/1.json` confirms the direction of the error rather than excusing it: it describes
the ladder as *"`restored_month_share` (none, **a quarter**, half, the whole of the monthly plan premium)"* — the
author's own account of the ladder agrees with the rule and disagrees with the parameter their compute reads. Two
of the three faces say 0.25; only the binding says 0.75.

**Checklist items.**

- per-task files correspond one-to-one with the tasks; `revision_1` is preserved intact above and untouched, with
  `revision_2` appended to all three files; every revision-2 comparison section carries per-relationship verdicts.
- this difficulty's five extended policies are fully covered and the two task scopes are pairwise disjoint and
  jointly complete, each spanning a whole problem tree (confirmed against `charter_scope` after the reveal).
- task tools and GT are closed; `task_tools.py` is byte-identical to revision 1, so the uuid8s remain
  independently generated, frozen and unreused, and the reworker's ground for not touching it holds — no round-1
  finding named a tool contract.
- problem trees: task 0 has one prerequisite problem and one `value_input` edge (floor 1) with the root the
  customer's own write; task 1 has two prerequisite problems, one `value_input` edge (floor 1) and one
  `owner=user` write; no cycle in either, and the three edges together are still a DAG.
- computations: every one declares a self-sufficient baseline giving a definite number different from gold
  (0.00 / 160.00 on task 0; 63.40 / 229.30 / 0.00 on task 1 — two of the five still the degenerate floor,
  observations 0-O2 and 1-O2, both accepted with reasons), four to six factors each with two that genuinely
  select a figure, every ladder three or more tiers stated in full in its rule, and **every factor bears weight
  against an honest baseline on its own world** — all 27 substitutions recomputed and matching
  `factor_sensitivity` figure for figure.
- cross-category reads verified at **field** level, not only category level, on the sibling difficulty's lead: no
  undeclared field in any of the four policies that read another category.
- instantiation-stage gates: cited from the brief's re-run snapshot (all seven green on the reworked form), not
  re-run here. N1, N2, N3, 2-R1 and 2-R2 all sit in the space those gates do not reach — a parameter value that
  contradicts its own rule sentence still parses, a tier that no seeded member occupies is still a tier, a
  conflict with a base policy that is not in `base_policy_refs` is not compared, and a ceiling that never binds
  still moves the number when its baseline is substituted.

**Difficulty verdict: FAIL (second round).** Open items: **N1** (SOURCE-POLICY RED, regression, three policies),
**N2** (SOURCE-FACTOR RED, three policies), **N3** (SOURCE-POLICY RED, one policy), **2-R1** and **2-R2**
(SOURCE-FACTOR REDs on task 1), **2-R3** (false proof assertion on task 0). Both tasks' problem trees hold, both
tasks' scored solutions are uniquely entailed on their own worlds, and both independent derivations reproduced GT
at every item and every figure.

---

# revision_3 — charter-global re-audit

## charter_global_frozen (revision 3)

- **This is verification, not a blind audit, and is recorded as such.** I have seen this difficulty's GT twice.
  The ordering actually observed this round, which is the honest account: every scored figure below was
  recomputed from the reworked charter (`1ed09f2279094bff`) and the rebuilt masked worlds **before**
  `tasks/0.json` or `tasks/1.json` were opened; the task files were then opened for the proof-field sweep the
  brief asked for, and the comparison and the stale-declaration findings come after that point. Nothing is
  presented as independently rediscovered.
- hashes recomputed from disk, all six matching the brief: `advantage.extended.yaml` **`1ed09f2279094bff`**
  (revision 2: `477d67e46794e35c` — CHANGED, 4040 → 4067 lines); `task_tools.py` **`e1816f63751c242e`**
  (UNCHANGED across all three rounds); `tasks/0.json` `ee74394804e26c97`; `tasks/1.json` `990c5bbcf26a021a`;
  `_masked_views/0.masked.json` `d024af4f53ffa78a` (UNCHANGED); `_masked_views/1.masked.json`
  `057308995e4e9406` (CHANGED).
- carry-forward: the charter moved, so this section is re-derived. `task_tools.py` is byte-identical for the
  third round running, so `### action_binding_and_uuids` from revision 1 carries forward on that hash; the five
  `(target_tool, computes)` pairs are unchanged and still one-per-policy.
- `replay_tasks.py` was **not** run, per the coordinator's note that it rewrites `db_closure` from a set
  iteration and would unpin the hashes above. Gate results are cited from the brief's snapshot.
- entry conditions met: gate snapshot supplied (seven green), both masked views supplied with hashes.

### base_section_integrity (revision 3)

Re-parsed and compared key for key against `blueprint/products/advantage.yaml`: **equal**, with
`extended_policies` the only extra top-level key. The base copy has not been rewritten in any of the three
rounds.

### policy_conflict_scan (revision 3)

Subjects, target tools, computed quantities, triggers, eligibility gates, time anchors and terminal states are
unchanged and mutually compatible; the two task scopes are still the same partition of the five extended
policies; `cross-cat` is still 4 (pdp ×3, osb ×1). **One round-2 conflict is closed (N3) and no new
cross-policy conflict was introduced.** The remaining finding of this round (3-R3) is an internal coverage
defect of one policy's ladders rather than a conflict between policies.

### cross_category_declaration_field_level (revision 3)

Confirmed once, as the brief suggested, rather than re-derived: every `CFIELD` / `XSUM` / `XCOUNT` /
`XLATEST` call in all five policies was extracted and matched against that policy's declared `reads`.
`advantage_ext_premium_subsidy_relief` → `low_income_subsidy_applied`, `pdp_premium_ledger.adjustment_reason_code`;
`advantage_ext_disenrollment_closing_balance` and `advantage_ext_reinstatement_restored_premium` →
`low_income_subsidy_applied`; `advantage_ext_pending_election_withdrawal_credit` → `status`,
`rider_premium_balance_due`, `osb_rider_premium_ledger.amount` (the new `XLATEST` over that ledger reads the
same declared `amount` field). **No undeclared field.** The sibling difficulty's defect still does not
reproduce here. `inputs.cross_category` and `inputs.history` name the same categories and tables the compute
aggregates, with no table declared that is never aggregated.

### rule_compute_equivalence (revision 3)

Re-swept in both directions. **The round-2 equivalence defect (N1) is closed, and closed on every face.**

- **N1 / N2 — closed, verified on five faces in all three policies.** This defect existed because a change
  reached some faces and not others, so I checked each face separately and mechanically:

  | face | `member_premium_share` | `unbilled_month_share` | `restored_month_share` |
  | --- | --- | --- | --- |
  | `params` | `quarter_member_share` **0.25**, `three_quarter_member_share` **0.75** | `quarter_share` **0.25**, `three_quarter_share` **0.75** | `quarter_share` **0.25**, `three_quarter_share` **0.75** |
  | `rule` sentence | 75 % → "the member meets **a quarter** of it"; 25 % → "**three quarters** of it" | 75 % → "**a quarter** of it is charged"; 25 % → "**three quarters** of it are charged" | 75 % → "**a quarter** of it"; 25 % → "**three quarters** of it" |
  | `compute` | 75 % → `K('quarter_member_share')`; 25 % → `K('three_quarter_member_share')` | 75 % → `K('quarter_share')`; 25 % → `K('three_quarter_share')` | 75 % → `K('quarter_share')`; 25 % → `K('three_quarter_share')` |
  | `compute_basis` | all five states quoted | all five states quoted | all five states quoted |
  | `ladder` | 5 tiers, values as above | 5 tiers | 5 tiers |

  All three ladders now carry **five** tiers, one per value of the seeded enum
  (`db_schema.json` `pdp_enrollments.low_income_subsidy_applied` = no_subsidy / full_subsidy / partial_subsidy_75
  / partial_subsidy_50 / partial_subsidy_25), the lumped wording *"a twenty-five per cent subsidy **or no
  subsidy at all**"* is gone from all three rules, and the five values 0.0 / 0.25 / 0.5 / 0.75 / 1.0 are
  pairwise distinct with the fall-through equal to each factor's baseline. `arrears_collection_share`, which
  shares the `*_collection_share` key space, is untouched and still correct (0.5 / 0.75 / 1.0).
- **3-R3 (new).** Two ladders of the withdrawal-credit policy are not pairwise disjoint and not exhaustive as
  stated, and the compute carries branches no tier states. See `### findings`.
- Revision-1 observation **O1** persists (unwindowed `SUM` behind "in the contract year"); no consequence.

### prerequisite_graph and prerequisite_sentences (revision 3)

Re-derived mechanically on the new charter. All three edges hold: `policy_source` verbatim in the blocked
policy's own rule, absent from the depended-on rule, `form: state` with no `fallback_reason`, `gate` a real
compute binding (`relief_allowance` → `relief_allowed`, `accumulated_share`) or a real eligibility field
(`advantage_enrollments.status`), and `resolved_by` equal to the depended-on policy's `target_tool`. The graph
is the same acyclic chain pair. Every other ordering word in the five rules was re-extracted and none states an
order between two problems. O5 and O6 persist as observations.

### override_declarations (revision 3)

- **N3 — closed, and closed the right way.** The tier was re-keyed rather than the base clause overridden.
  It now reads *"Where the enrollment is billed quarterly and the plan premium charges standing on the account
  leave **at least three coverage months the enrollment has been in force** uncovered, the coverage months the
  settlement still charges for are three"*, with `final_months` bound to
  `served_months - billed_span >= K('quarterly_final_months')`. Since `served_months` counts only months
  through the month in hand, and base fixes the coverage end date at the last day of that month, **every month
  the settlement can charge for is a month the enrollment has already been in force for**, so base's *"No
  premium is charged for a coverage month beginning after the coverage end date"* is never crossed. The rule
  now says so itself, in a sentence that makes the harmony explicit rather than leaving it to be inferred:
  *"No coverage month beginning after the coverage end date is ever charged into the closing settlement,
  because the coverage months the settlement still charges for are only ever coverage months the enrollment has
  already been in force for."* `overwrite: []` is therefore now an **honest** declaration: nothing of base is
  superseded. I checked the tier-2 boundary as well — the compute's `served_months > billed_span` fall-through
  matches the stated "fewer than three are left uncovered or the enrollment is billed monthly".
- F1 (withdrawal credit) and F2(a) (corrected claim) still carry their declared `overwrite` entries naming the
  base clauses they supersede; F2(b)'s scoping sentence and the dialysis clause from O2 are still in place;
  F2(c) remains inapplicable on both worlds.
- F3's *"whatever reason each of them carries"* is present in all three policies that reckon credit
  adjustments; F4's *"one more for the month in hand"* is present in all three that count coverage months, and
  *"both months included"* appears nowhere in the charter.

### factor_ladders (revision 3)

| policy | factors | param / method | tier counts | honest param | binding sets disjoint | cross-difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| subsidy relief | 5 | 2 / 3 | 3,5,3,3,3 | 2 | ✔ | pdp ×2 |
| closing balance | 5 | 2 / 3 | 3,3,5,3,3 | 2 | ✔ | pdp |
| withdrawal credit | 4 | 2 / 2 | 3,3,3,3 | 2 | ✔ | osb ×3 |
| restored premium | 6 | 2 / 4 | 3,5,3,3,3,3 | 2 | ✔ | pdp |
| corrected claim | 5 | 2 / 3 | 3,3,3,3,3 | 2 | ✔ | — |

F5, F6 and F7 remain closed: every `parameter` ladder selects a figure, no ladder divides on a condition its
write's own eligibility gate already forces, and no ladder has two tiers with the same outcome. The
withdrawal-credit policy's factor set was rebuilt again this round — `rider_offset_ceiling` removed,
`rider_owing_measure` replaced by `rider_rate_measure` (a per-month rate) and `rider_months_reckoned` added —
and the chain is now a pure product, `rider_monthly × rider_months_owed × offset_share`, with no `MN`.

**On the reworker's argument for removing the ceiling rather than reseeding under it: it is sound.** With
`met = MN(owing × share, ceiling)`, a single evaluation point lies in exactly one regime. In the uncapped
regime every non-zero ceiling tier gives the same number, which was 2-R1; in the capped regime the result is
`money_returned − ceiling` and the rate, months and share ladders all stop moving it. So at one world point a
cap and the multipliers feeding it cannot both be tested, and eliminating one of them is the only fix that does
not merely move the defect onto the other factors. Removing the cap was the better of the two choices here,
because the three surviving ladders are all cross-difficulty reads of the rider and the cap was not.

### findings (revision 3)

**3-R3 — SOURCE-POLICY RED (ladders not disjoint and not exhaustive as stated; a partial regression).**

- *Symptom.* Two of the three rider ladders in `advantage_ext_pending_election_withdrawal_credit` leave
  reachable cases matching no tier, and one leaves a case matching two.
- *Evidence, enumerated over `osb_riders.status` × "rider premium charged":*
  - `rider_arrears_offset` — tier 1 *"stands suspended for unpaid rider premium **and** rider premium has been
    charged to its account"*; tier 2 *"stands in force or in its waiting period **and** rider premium has been
    charged"*; tier 3 *"**no** rider premium has been charged …, or the member holds no … rider"*. A rider that
    **stands terminated and has been charged** matches no tier at all. The compute's else-branch silently
    returns `K('no_offset_share')`, a branch the rule states nowhere. `rider_requested` and
    `cancelled_before_effective` with charges fall in the same hole.
  - `rider_months_reckoned` — tier 1 *"stands suspended for unpaid rider premium"* (unconditional); tier 3
    *"…, the rider stands terminated, **or no rider premium has been charged to its account in the last six
    months**"*. A rider **suspended with no charge inside six months** matches tier 1 **and** tier 3, which say
    three coverage months and one coverage month respectively; the compute resolves it by position, which the
    rule does not license.
- *Demonstrated consequence, in the same situation.* For a terminated rider carrying arrears — the commonest
  way a rider ends, and exactly the case where a plan would most want to recover from a refund — the rule
  yields no share at all while the compute yields none-of-it; and for a suspended rider last charged more than
  six months ago the rule yields both three months and one month.
- *Partial regression.* Revision 2's `rider_arrears_offset` tier 3 read *"where the member holds no optional
  supplemental benefit rider, **or the rider stands terminated**, the share the plan meets is none of it"* —
  it decided the terminated case. This round moved "terminated" out of that ladder into
  `rider_months_reckoned` and added a "charged" conjunct to tiers 1 and 2, and the terminated-with-charges case
  fell through the gap that opened. The behaviour is unchanged (the compute returned 0 then and returns 0 now);
  what regressed is the rule's coverage of it.
- *Not instantiated.* Task 1's rider is `active` with charges, so no scored value moves; the defect is in the
  published rule the KB will render.
- *Supporting note.* The three ladders of this one policy also disagree about the no-rider case:
  `rider_months_reckoned` and `rider_arrears_offset` each name *"the member holds no optional supplemental
  benefit rider"* in a tier, while `rider_rate_measure` does not, and its binding `rider_balance > 0` would be
  a comparison against the absent value `CFIELD` returns for a member with no rider.
- *Affected artifact.* `advantage.extended.yaml`,
  `advantage_ext_pending_election_withdrawal_credit.rule` (the two ladder paragraphs), `compute.offset_share`,
  `compute.rider_months_owed`, and the corresponding `factors[].ladder` entries.

**N1, N2, N3, 2-R1 and 2-R2 are verified closed**; the evidence is in the sections above and, for the two
task-level ones, in `1.md § revision_3`. **2-R3 is verified closed** in `0.md § revision_3`. The two new
task-level findings of this round, **3-R1** and **3-R2**, are stale proof declarations and are recorded in the
task files where their consequences are demonstrated.

## closing_checklist (revision 3)

**The difficulty does not close.** Three rounds in, the list is down to one policy defect and two stale proof
declarations; no figure is in dispute and both trees and both unique solutions hold.

**Every round-2 RED is genuinely closed, verified against the artifacts.**

| round-2 item | verdict | how verified |
| --- | --- | --- |
| **N1** | closed | five faces × three policies checked separately (`params`, `rule`, `compute`, `compute_basis`, `ladder`): `quarter_*` = 0.25 bound to the seventy-five-per-cent tier, `three_quarter_*` = 0.75 to the twenty-five-per-cent tier, everywhere |
| **N2** | closed | all three ladders rebuilt to five tiers, one per enum value; the lumped "or no subsidy at all" gone; five distinct outcomes 0.0/0.25/0.5/0.75/1.0 |
| **N3** | closed | the tier re-keyed onto in-force months; base's clause untouched and `overwrite: []` now honest; checked that no month the settlement can charge for begins after the coverage end date |
| **2-R1** | closed | ceiling removed entirely, no `*_ceiling` key in the charter, replacement multiplies, nine distinct outcomes across the three rider ladders; the cap-versus-multiplier argument assessed and sound |
| **2-R2** | closed | tier value 31.00 carried by no seeded field; the balance that reproduced it gives 65.30; near-miss now moves the figure (96.05); the "latest charge" coincidence judged a rule, not a leak |
| **2-R3** | closed | the object-and-rows paragraph rewritten to what the rows show, clause by clause |
| 2-O1, 2-O3 | accepted | reasons given are accurate for 2-O1; for 2-O3 the substance stands but its restatement is stale (3-R2) |

**Nothing regressed, with one partial exception.** All nineteen round-1 items (F1–F7, 0-R1…0-R3, 1-R1…1-R8) and
the round-1 observations were re-checked on the round-3 charter and remain closed or accepted: the base section
is still verbatim, `task_tools.py` is byte-identical for the third round, the three prerequisite edges still
verify mechanically, every `parameter` ladder still selects a figure, no ladder divides on its write's own
eligibility gate, and `1-R1`'s stamp is still absent (`moop_accumulated` 12040.00 still matches only the
baseline). The exception is **3-R3**: revision 2's `rider_arrears_offset` decided the terminated-rider case and
revision 3's does not, because "terminated" moved to another ladder while a "charged" conjunct was added here.

**Checklist items.** Revisions 1 and 2 are preserved intact with revision 3 appended to all three files; the
five extended policies are fully covered by two pairwise-disjoint scopes; both problem trees hold with a
`value_input` edge at or above the floor and a customer's own write in each; every computation declares a
self-sufficient baseline giving a definite number different from gold (0.00 / 160.00 · 63.40 / 229.30 / 0.00)
and four to six factors of which two select figures; **all 25 factor-baseline substitutions and both whole
baselines were recomputed and match `factor_sensitivity` figure for figure**; cross-category reads confirmed at
field level; `baseline.params` and `inputs.history` swept for stale keys and clean. Gates cited from the
brief's snapshot; `replay_tasks.py` deliberately not run so the audited hashes stay pinned.

**Difficulty verdict: FAIL (third round).** Open items: **3-R3** (SOURCE-POLICY RED — two rider ladders not
disjoint and not exhaustive as stated, with a terminated-and-charged rider matching no tier while the compute
silently returns none-of-it, a case revision 2's rule decided), **3-R1** and **3-R2** (SOURCE-FACTOR REDs —
stale proof declarations left behind by the N3 and 2-R1 fixes: a `factor_trace` and an
`argument_uniqueness_tracing` still grounding a tier in the removed "quarter in hand" sentence and its
superseded condition, an `evaluation_criteria[].necessity` still justifying a read by a removed ceiling, and a
`design_rationale` describing the reseeded rider with revision 2's count and figure). Observations 3-O1, 2-O1,
2-O3, O1, O5 and O6 stand.

**A note on where the remaining defects live.** Three of this round's four findings are in proof fields rather
than in the policy, and every one of them is an instance of the same pattern — a change correct at its site
that did not reach a field pointing at it. The counts across rounds are: round 1 one instance (1-R2), round 2
one (2-R3), round 3 two (3-R1, 3-R2), each time in a field the previous sweep had not covered. The policy
surface itself is now in good order: one coverage defect in one policy's two ladders, and nothing else.

---

# revision_4 — charter-global re-audit

## charter_global_frozen (revision 4)

- **Verification, not a blind audit, and recorded as such.** I have seen this difficulty's GT in three previous
  rounds. Sequence this round: the partition enumeration, the five recomputations and the 25 factor
  substitutions were run from the reworked charter (`856382e54eee5c11`) and the masked worlds **before** the
  task files were opened; the task files were then opened for the three-pass proof sweep; the GT comparison
  follows. No figure below is presented as independently rediscovered.
- hashes recomputed from disk, all six matching the brief: `advantage.extended.yaml` **`856382e54eee5c11`**
  (round 3: `1ed09f2279094bff` — CHANGED, 4067 → 4204 lines); `task_tools.py` **`e1816f63751c242e`**
  (UNCHANGED across all four rounds); `tasks/0.json` `a23a501929324a1d`; `tasks/1.json` `dde318940c61a4e8`;
  both masked views **unchanged** from round 3.
- **Carry-forward judgement, made rather than assumed.** Both worlds are byte-identical, but the charter moved
  and the change was to the *stated domains of three ladders*, which is precisely where a world-dependent
  conclusion can shift without the world moving: a re-partition can change which tier a given customer falls
  in, and a factor's baseline is itself a ladder tier. So the per-task factor conclusions were **re-derived in
  full, not carried forward** — every tier-taken re-determined and all 25 sensitivities recomputed. The
  conclusions that were carried forward, on the grounds that both their inputs are byte-identical, are the
  seeded-row facts underlying each problem tree (the masked worlds) and the tool-contract conclusions
  (`task_tools.py`, unchanged for four rounds).
- `replay_tasks.py` was not run, per the coordinator's note; gates cited from the brief's snapshot.

### base_section_integrity, prerequisite graph, cross-category (revision 4)

Re-derived: the base section is still equal to `blueprint/products/advantage.yaml` key for key with
`extended_policies` the only extra key; all three prerequisite edges still verify mechanically (`policy_source`
verbatim in the blocked policy's own rule, absent from the depended-on rule, `form: state`, gate a real binding
or eligibility field, `resolved_by` the depended-on `target_tool`); every cross-category call is declared at
field level in all four reading policies. Five factor sets, 2 honest `parameter` factors each, no binding-set
overlap, tier counts 3 or 5.

### the 3-R3 partition, enumerated rather than read

The claim under test is a partition claim, so I tested it as one, independently of the reworker's enumeration.
I encoded each of the three rider ladders' **stated** tier conditions from the rule prose, and each ladder's
**compute** branch separately, then enumerated every reachable combination of `osb_riders.status` (six enum
values plus "the member holds no rider") × charges inside six months (0/1/2/3) × charged ever × carries owing,
dropping the incoherent combinations (charged inside six months but never charged; a no-rider member with
charges or a balance).

```
combinations enumerated: 61        ladder-checks: 183
gaps: 0        overlaps: 0        rule/compute disagreements: 0
```

Every one of the 183 checks matches **exactly one** tier, and that tier's stated outcome is the value the
compute produces. The three cases that failed in revision 3 were re-tested by name:

| case | revision 3 | revision 4 |
| --- | --- | --- |
| `rider_arrears_offset`, rider **terminated** and charged | **no tier** (compute silently returned none-of-it) | tier 3 — *"the rider stands in any state other than suspended for unpaid rider premium, in force or in its waiting period"* |
| `rider_arrears_offset`, `rider_requested` / `cancelled_before_effective` and charged | no tier | tier 3 |
| `rider_months_reckoned`, rider **suspended** with no charge inside six months | **tiers 1 and 3** (three months and one) | tier 1 only — tier 3's "no charge in six months" disjunct is now qualified by *"that rider stands in force or in its waiting period"* |

Two further repairs in the same policy, which I checked because revision 3 recorded them as supporting notes:

- `rider_rate_measure`'s tier 2 now carries its own sub-clause — *"and is nothing where no rider premium charge
  stands on it at all"* — which closes the owing-but-never-charged case the rule previously left to the
  compute. My first enumeration flagged six apparent rule/compute disagreements there; on resolving that
  sub-clause they are not disagreements but agreements, and the re-run returns zero.
- the no-rider crash path is gone: `rider_monthly`'s branches now read
  `rider_charge_count >= … and rider_ledger_count >= 1 and rider_balance > 0` and
  `rider_ledger_count >= 1 and rider_balance > 0`, so the count test short-circuits before the comparison
  against the absent value `CFIELD` returns for a member with no rider. `rider_rate_measure`'s third tier also
  now names *"or the member holds no optional supplemental benefit rider"*, which is the inconsistency across
  the policy's three ladders that revision 3 noted.

**3-R3 is closed.**

### regression: the sensitivity question

The brief is right that a partition fix is where an unnoticed sensitivity shift would hide, so I did not accept
the "same tier before and after" argument on its face. Two things had to hold, and both were checked
separately: that the **tier taken** is unchanged for task 1's rider (rate tier 1, months tier 2, offset tier 2 —
`active`, three charges inside six months, four ever, balance 123.00 > 0), and that each factor's **baseline is
still exactly its ladder's fall-through tier** after the tiers were re-stated (`rider_monthly` 0,
`rider_months_owed` `K('standard_months_owed')` = 1, `offset_share` `K('no_offset_share')` = 0 — all three
still the third tier's value). Both hold, and the empirical re-run agrees:

```
ALL FIVE COMPUTATIONS IDENTICAL TO ROUND 3: True
  228.60 / 102.80 · 95.80 / 185.05 / 1834.00
  whole baselines 0.00 / 160.00 · 63.40 / 229.30 / 0.00
  all 25 factor sensitivities identical
  edge weights identical: 391.40 (task 0), 1330.00 and gate-only (task 1)
```

Nothing regressed elsewhere either: F3's *"whatever reason each of them carries"* is in all three policies that
reckon credit adjustments, F4's *"one more for the month in hand"* likewise with *"both months included"*
nowhere in the charter, the three declared `overwrite` entries are intact, F2(b)'s scoping sentence and N3's
harmony sentence are in place with `overwrite: []` still honest, and N1's mapping is still
`quarter_* = 0.25` on the seventy-five-per-cent tier in all three ladders.

### findings (revision 4)

**No new defect.** Three independent passes over every string at every path of both task files, keyed on what a
field asserts rather than on what was edited:

- **Pass A — removed-concept assertions.** An 18-term denylist of concepts the charter no longer contains
  (ceiling, quarter in hand, both months included, the allowance-card machinery, `good_cause_excused_months`,
  `settlement_premium_basis`, `restored_month_rate`, `plan_premium_offset`, `rider_owing_measure`,
  `rider_offset_ceiling`, "or no subsidy at all", `three_quarter_member_share` on the 75 % tier, …), each first
  confirmed absent from the charter. **Zero hits in any live proof field** in either task; all 19 hits are
  inside `design_rationale`, which is the rework log and legitimately names what it removed.
- **Pass B — figure assertions.** Every decimal figure asserted anywhere in `evaluation_criteria`,
  `computations`, `prerequisite_closure`, `solvability_contract`, `charter_scope`, `required_documents` and
  `design_rationale` was extracted and tested against the set the world produces — every compute binding
  evaluated at that write's own handling time with the preceding gold writes replayed, plus the seed, the tier
  parameters and the declared sensitivities. 29 figures fell outside that set and **all 29 were adjudicated
  individually and are correct**: revision-1/2 history correctly labelled as history in the log (370.95,
  517.95, 20.90, 39.30, 246.10); counterfactuals the artifact computes correctly (11,970.00 for the
  pre-restoration accumulator; 92.80 / 80.30 / 111.30 / 64.80 / 126.80 for the rider ladders' untaken tiers,
  each matching my own probe); and true unnamed intermediates (71.40 = 3 × 23.80, 133.95 = 3 × 44.65,
  428.40 = 9 × 47.60).
- **Pass C — quotation assertions.** All 29 true quotations of 40 characters or more (alternating quote pairs,
  case-insensitive) were matched against the extended rules, the base rules, the ladders, the tool docstrings
  and the persona. 26 match verbatim; the 3 that do not are each labelled in the text as the affirmative
  contrapositive of a prerequisite sentence, and I verified each is exact — *"the closing premium balance is
  struck only once the premium relief … stands … as a credit entry"*, *"a corrected liability is fixed on a
  claim line only once the enrollment … stands in force with no coverage end date recorded on it"*,
  *"coverage terminated for non-payment is not restored until no other Medicare Advantage election … stands
  awaiting the transaction reply"* — same result, same waited-on state, same scope in all three.

**There is no fifth site.** I found the sites the round-1, round-2 and round-3 sweeps missed, and this sweep's
four sites are the four I named; three independent passes over every string in both task files surface nothing
further.

**One claimed closure is not closed: 3-O1.** The reworker reports it closed. It is not, and the dossier does
not in fact claim it is — `3-O1` appears nowhere in either `design_rationale`. The coincidence persists:
`rider_months_owed × offset_share` is still 2 × 0.5 = 1, so the baseline months with the top share tier
(1 × 1.0) still yields exactly gold. The full 3 × 3 grid of tier pairs, recomputed this round:

```
months=3: share 1.0 -> 33.80   share 0.5 -> 80.30    share 0.0 -> 126.80
months=2: share 1.0 -> 64.80   share 0.5 -> 95.80 *  share 0.0 -> 126.80
months=1: share 1.0 -> 95.80 * share 0.5 -> 111.30   share 0.0 -> 126.80
```

One off-diagonal collision, marked. This remains what revision 3 called it — an **observation, not a red
light**: each factor is properly tested on its own (substituting either baseline alone moves the figure, to
111.30 and 126.80 respectively), the rule forces 2 and 0.5 for this rider with no second defensible reading,
and the artifact asserts nothing false about it — its claim, *"Each ladder's tiers are told apart by the
score"*, is a per-ladder claim and is true. It does not block the verdict; it is recorded because a closure was
claimed for it that the artifacts do not support.

## closing_checklist (revision 4)

### the difficulty PASSES

All four relationships hold on both tasks, and the difficulty closes at the source layer.

| relationship | task 0 | task 1 |
| --- | --- | --- |
| policy self-consistency | **PASS** | **PASS** |
| the problem tree holds | **PASS** | **PASS** |
| factors bear weight | **PASS** | **PASS** |
| unique solution | **PASS** | **PASS** |

**Every round-3 RED is closed, verified against the artifacts rather than the reworker's account.**

| item | verdict | how verified |
| --- | --- | --- |
| **3-R3** | closed | the partition claim re-enumerated independently: 61 combinations × 3 ladders = 183 checks, **zero gaps, zero overlaps, zero rule/compute disagreements**; the three revision-3 failure cases each now match exactly one tier; the owing-but-never-charged case and the no-rider comparison path also repaired |
| **3-R1** | closed | tested for **entailment**, not for the absence of the old phrase: the replacement reason instantiates the rule's real condition (9 − 6 = 3, "which is at least three") and excludes the one-month-gap counterexample that broke the old one; present in both proof fields |
| **3-R2** | closed | both sites repaired and the replacements checked for truth: the necessity field now rests on quantities the policy computes, and the rider description's four figures all verify |
| 3-O1 | **not closed**, though claimed | the coincidence persists (2 × 0.5 = 1 × 1.0 → 95.80 both ways); it remains an observation, not a red light, and the artifact asserts nothing false about it |

**Nothing regressed.** All five scored figures, both whole-baseline figures, all 25 factor sensitivities and
all three edge weights are identical to round 3 and to my own recomputation; the tier taken is unchanged in
every ladder; every factor's baseline is still its ladder's fall-through tier after the re-partition; the base
section is still verbatim; `task_tools.py` has never moved; the three prerequisite edges still verify; all
nineteen round-1 items, the six round-2 items and the round-3 items remain closed.

**No new defect.** Three independent passes over every string at every path of both task files — removed-concept
assertions against an 18-term denylist, figure assertions against the set the world produces with every binding
evaluated at its own handling time, and quotation assertions requiring a verbatim match in a rule, ladder,
docstring or persona — surfaced **zero live proof fields carrying a removed concept, zero false figures (all 29
out-of-set figures adjudicated and correct) and zero unsupported quotations (the three non-verbatim ones are
labelled contrapositives, each verified exact)**. The stale-declaration pattern that produced one finding in
each of rounds 1, 2 and 3 produced none in round 4.

**Closing checklist.** Revisions 1–3 preserved intact with revision 4 appended to all three files; the five
extended policies fully covered by two pairwise-disjoint scopes spanning whole problem trees; task tools and GT
closed, five uuid8s independently generated and frozen since before round 1; task 0's tree with one
prerequisite problem, one `value_input` edge and the root as the customer's own write, task 1's with two
prerequisite problems, one `value_input` edge and the withdrawal as the customer's own write, both acyclic and
jointly a DAG; every computation with a self-sufficient baseline giving a definite number different from gold
and four to six factors of which two select figures; every ladder three or five pairwise-disjoint tiers stated
in full in its rule with distinct outcomes; every factor proved to bear weight against an honest baseline;
cross-category reads declared at field level; `baseline.params` and `inputs.history` clean. Gates cited from the
brief's re-run snapshot (seven green); `replay_tasks.py` deliberately not run so the audited hashes stay pinned;
`check_traceability` remains properly deferred to the KB render.

**Residual observations, none of them grounds for rework**, carried on the record for the KB-render and merge
stages: 3-O1 (two tier pairs of the withdrawal credit multiply to the same figure); 2-O1 (task 0's near-miss
does not discriminate — a record the rule excludes exists, but miscounting it does not move a tier); 2-O3 (the
persona understates the rider arrears, hedged and deferred to the record); 0-O2 and 1-O2 (two whole baselines
land on the 0.00 floor, a definite wrong business conclusion rather than a wrong figure); 0-O3 (a seeded
premium account raised at a superseded rate, declared as such in `solvability_contract`); O1, O5, O6 (the
unwindowed "contract year" aggregates; the relief gate's state not readable without performing the depended-on
computation; "awaiting the transaction reply" against a two-status condition).

**Verdict: the medicare_advantage_member_services difficulty passes the source-layer audit.** Four rounds:
revision 1 found 7 charter defects and 11 task defects, revision 2 found 5, revision 3 found 3, revision 4
finds none. The source layer is closed; `check_traceability` and the KB-document audit remain outstanding
against the published documents, and are not this skill's to judge.
