# Policy-task audit — host_payout_desk / charter-global

## charter_global_frozen

- freeze hash `payouts.extended.yaml` sha256:16 = `8ad43d7d7f1eef56`
- freeze hash `task_tools.py` sha256:16 = `6aabc488c8d1ee8c`
- masked view hashes: `0.json` `01ae985b52c8a6aa`, `1.json` `c4547dab5ae9f8e7`
- freeze time (UTC): 2026-09-22T09:09:13Z
- auditor: independent source-layer auditor (erl-task-policy-audit), not the instantiating agent
- fields permitted while this section was written: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`,
  `blueprint/share_tools.py`, `blueprint/products/payouts.yaml`, `blueprint/products/hostplan.yaml`
  (cross-category charter only, for the cross-difficulty reads), the whole of
  `tasks/host_payout_desk/payouts.extended.yaml` and `tasks/host_payout_desk/task_tools.py`, and the
  masked views (`frozen_time`, `user_scenario`, `initial_state` only).
- fields explicitly masked and not read before this section was frozen: `evaluation_criteria`,
  `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`,
  `prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state`, and every prior audit revision.
- contamination: none. No `tasks/*.json` file was opened at any point; only the coordinator's masked
  copies under the session scratchpad were read.

### entry conditions (Step 0)

The brief supplied the gate snapshot with the actual output lines for `check_extended.py`,
`check_task_tools.py`, `replay_tasks.py --check`, `check_solvability.py`, `check_compute.py`,
`check_grounding.py` and `check_cross_fire.py`, all green, and the masked-view hashes. The two masked
hashes and the two source hashes were re-computed above and agree with the brief. `check_traceability.py`
is correctly absent at this stage (no published KB). Entry conditions are complete; the gates were not
re-run by the auditor and are cited, not relied on as proof of correctness.

### policy_conflict_scan

Base section: `head -786 payouts.extended.yaml` is byte-identical to `blueprint/products/payouts.yaml`
(the only diff is a trailing blank line). The verbatim-copy requirement holds.

Five extended policies, five task tools, one-to-one:

| policy | subject | computes | target_tool | owner |
| --- | --- | --- | --- | --- |
| `payouts_ext_recovery_correction` | `payouts_adjustment_posted` | `correction_amount` | `post_recovery_correction_f20745c1` | agent |
| `payouts_ext_claim_reserve_release` | `payouts_reserve_released` | `release_amount` | `release_claim_reserve_fb50cb2e` | agent |
| `payouts_ext_requested_draw` | `payouts_transfer_released` | `draw_amount` | `release_host_payout_draw_8e4fb8ab` | user |
| `payouts_ext_negative_balance_recovery` | `payouts_deduction_posted` | `recovery_amount` | `post_balance_recovery_b10514b8` | agent |
| `payouts_ext_schedule_qualification` | `payouts_schedule_changed` | `payout_schedule_name` | `change_host_payout_schedule_75a33b7a` | user |

Subjects, target tools and computed quantities are pairwise disjoint; no two policies claim the same
`(target_tool, computes)` pair. The five together cover the whole extended charter and split cleanly into
two `prerequisite`-connected components — {recovery_correction → claim_reserve_release → requested_draw}
and {negative_balance_recovery → schedule_qualification} — so the two tasks' scopes (a scope spanning the
root and all of its prerequisite problems) are mutually exclusive and jointly complete. No task claims a
base policy as its root.

Overlapping-subject conflicts among the *extended* five: none. They write five different event families
and read one another only through the declared `prerequisite` edges.

Cross-category read boundaries: `payouts_ext_recovery_correction` declares `hostplan` (as history),
`payouts_ext_negative_balance_recovery` declares `hostplan` (as branch), `payouts_ext_schedule_qualification`
declares `hostplan` (as branch); the other two declare `cross_category: []` and their `compute` contains no
`CFIELD`/`X*` call. Every declared read is used, and no undeclared cross-category read appears in any
`compute` binding. The `hostplan` fields read (`protection_plan_name`, `claim_free_since_date`,
`vehicle_value_declared_amount`, `status`, `suspension_reason`, `liability_balance_due`,
`hostplan_claims.appraisal_amount`, `.amount_delta`, `.appraisal_channel`, `.liability_finding`) all exist in
`db_schema.json` and are all returned by `find_hostplan_enrollments` / `find_hostplan_claims`.

Base-versus-extended conflicts are the substance of this scan and are set out under
`override_declarations` below; three of them are load-bearing and are recorded as `SOURCE-POLICY RED`.

### rule_compute_equivalence

Sweep of every `compute` binding of all five policies against `compute_basis` and the `rule`. Every
binding carries a `compute_basis` quotation, and every quotation is locatable in that policy's `rule`.
Every ladder tier named in `factors[].ladder` is a sentence of the `rule` and a branch of the `decides`
binding, and every branch of each `decides` binding is a tier the rule states. No tier lives only in
`compute`, and no tier lives only in the rule. Rounding is stated ("rounded half to even to two decimal
places") and implemented (`RND(...,2)`) at the result of every computation.

Two failures of two-way equivalence, one of them load-bearing:

**F-EQ-1 (`SOURCE-POLICY RED`) — "the statement month up to that day" is implemented as a rolling
one-month window.** The phrase appears as a window in all five policies:
`payouts_ext_recovery_correction.compute_basis.recovered_month`, `..._claim_reserve_release.routine_hold_month`,
`..._requested_draw.ledger_net_month` / `available_month` / `reserve_held_month` / `reserve_released_month` /
`month_credits`, `..._negative_balance_recovery.earn_month` / `net_month`, and
`..._schedule_qualification.earn_month` / `trips_month`. Each is implemented with `within_months=1`, whose
runtime meaning (`skills/erl-task-instantiate/scripts/check_compute.py:271-278`, `MONTHS(row_date, NOW)` with
`0 <= m < within_months`) is a trailing calendar-month span anchored on the handling *day*, not the
statement month. The base charter defines the statement month twice as a different thing: the ledger field
`statement_period: The statement month the entry falls in.` (`payouts.extended.yaml:326`, `:347`, `:366`, …)
and the per-schedule parameter `statement_close_day: Day of the month the earnings statement closes on.`
(`:73`; 28 on Standard/Weekly/Express/Instant, 25 on Fleet/Reserve-Backed). The three readings pick out
different row sets: for a September handling date, a row carrying `statement_period: "2026-08"` is counted
by `within_months=1` whenever its day-of-month is at or after the handling day-of-month, and a row stamped
in the handling month is dropped when it is not. Consequence is demonstrated against task 0's world in
`0.md#policy_self_consistency`.

**F-EQ-2 (observation) — "the most recent appraisal" is implemented as the largest appraisal.**
`payouts_ext_recovery_correction.rule`: "The appraised sum of the loss is the appraisal recorded on the most
recent appraisal of the claim." `compute.appraised_sum`:
`XMAX('hostplan','hostplan_claims','appraisal_amount', event_type='hostplan_claim_appraised')` — a maximum,
not a latest. The same policy's `valuation_route` correctly uses `XLATEST(..., date_field='claim_date', ...)`
for "most recent", so the two faces of the same phrase disagree inside one policy. Neither task's world
carries two appraised rows whose latest is not also its maximum, so no consequence is demonstrable and this
stays an observation.

**F-EQ-3 (observation) — "every supplement added to the claim" is summed across every claim.**
`compute.supplement_sum` is `XSUM('hostplan','hostplan_claims','amount_delta', event_type='hostplan_supplement_added')`
with no claim scoping, while the rule says "the invoiced appraisal together with every supplement added to
the claim" (one claim). Same for `recovery_received`. Not demonstrable on either seeded world (one supplement
row, one recovery row, both on the same claim).

**F-EQ-4 (observation) — "set against" implemented as a signed addition.**
`payouts_ext_schedule_qualification.rule`: "The deductions and corrections booked to the account in the twelve
months up to that day are set against the qualifying monthly earnings at the offset share, spread evenly over
twelve months." `compute.qualifying_earnings` *adds* `RND(net_flows_year * offset_share / 12, 2)`. Where the
12-month net of deductions and adjustments is negative the two readings coincide; where corrections dominate
and the net is positive, "set against" would subtract and the compute would add. Not demonstrable on task 1's
world (`corrections_year = 0`).

**F-EQ-5 (observation) — the rule fixes no anchor for "how long the balance has stood short".**
`payouts_ext_negative_balance_recovery.rule` states the ladder on "how long the balance has stood short" but
never says from which day it is counted; `compute.shortfall_age_days` supplies one —
`DAYS(LATEST('payouts_ledger','entry_date', date_field='entry_date', entry_basis='chargeback_recovery'), NOW)`
— that the rule does not state, so `compute` invents a basis here. The base clause the policy supersedes
counted "in whole calendar days from the day the balance went negative", which is a different anchor in
general. Both anchors coincide on task 1's world, so this is an observation.

### action_binding_and_uuids

Each `(target_tool, computes)` pair is claimed by exactly one policy (table above); no tool is shared.
Each tool performs exactly one atomic `ctx.create`/`ctx.update`, adds no confirmation, review, wait or
procedure of its own, and validates no prerequisite: the four ledger-writing bodies are a single
`ctx.create` plus a formatted return, and `change_host_payout_schedule_75a33b7a` is a single `ctx.update`
(`task_tools.py:37-45, 76-83, 112-119, 148-155, 193-194`). No docstring names another tool, states this
action's position in a sequence, or carries an ordering word (`before`, `after`, `first`, `prior to`)
about another problem. "The call has completed when the confirmation … comes back" is a completion
criterion for the same call, not a cross-tool order.

uuid8s: `8e4fb8ab`, `f20745c1`, `fb50cb2e`, `b10514b8`, `75a33b7a`. Five distinct values, no shared
prefix, no shared tail, no adjacent or sequential relation, none the hex of a small integer. Independently
generated and frozen with their tools.

**F-TOOL-1 (`SOURCE-POLICY RED`) — three tool docstrings assert a holding-row effect the tool body does not
perform.** `release_claim_reserve_fb50cb2e` states "The account's reserve balance falls by the sum freed
while the total credited stays as it was, so the host sees the same money move from held to drawable"
(`task_tools.py:93-95`); `post_recovery_correction_f20745c1` states "the account's balance rises by the sum
put back" (`:56`); `release_host_payout_draw_8e4fb8ab` states "The balance the host may draw falls by the sum
sent" (`:20`); `post_balance_recovery_b10514b8` states "the balance free to be paid out falls by that sum"
(`:129-130`). All four bodies call only `ctx.create("payouts_ledger", …)`. `erlbench/tools.py:111` `create`
inserts a row; nothing in `erlbench/tools.py`, `erlbench/db.py` or `erlbench/engine.py` derives
`payouts_accounts.available_balance` / `.reserve_balance` from the ledger. The charter binds those two fields
as the account's quantities (`payouts.extended.yaml:8-12`, `accounts:` at `:30-36`). So after every gold
write the account row the host and the agent read is stale. Consequence is demonstrated against task 0's
world in `0.md#policy_self_consistency` (the terminal state the docstring promises is not the terminal state
the write produces, and the base transfer formula reads the stale fields).

### prerequisite_graph

Three declared edges across the charter; the two other policies carry `prerequisite: []` explicitly.

| blocked policy | problem | kind | gate | form | resolved_by | acyclic |
| --- | --- | --- | --- | --- | --- | --- |
| `payouts_ext_claim_reserve_release` | `payouts_ext_recovery_correction` | `value_input` | `settlement_booked` | state | `post_recovery_correction_f20745c1` | yes |
| `payouts_ext_requested_draw` | `payouts_ext_claim_reserve_release` | `value_input` | `reserve_standing` | state | `release_claim_reserve_fb50cb2e` | yes |
| `payouts_ext_schedule_qualification` | `payouts_ext_negative_balance_recovery` | `value_input` | `net_flows_year` | state | `post_balance_recovery_b10514b8` | yes |

- every `problem` points at another *extended* policy id in this file, never at a base policy and never at
  itself; the whole graph is two disjoint paths and is acyclic, with no cross-task reference;
- `form: state` on all three and no `fallback_reason` anywhere — correct, since `fallback_reason` is required
  exactly on action-form edges and no edge is action-form. The state form's priority is honoured on all three;
- `kind: value_input` on all three, and each `gate` names a binding that genuinely exists in the blocked
  policy's `compute`: `settlement_booked` (`payouts.extended.yaml:1059`), `reserve_standing` (`:1301`),
  `net_flows_year` (`:1753`). None is a `state_gate` masquerading as a value edge;
- each `resolved_by` is the depended-on policy's own `target_tool`, and each genuinely changes the named
  binding's value: `post_recovery_correction_f20745c1` creates an `entry_basis="adjustment_correction"` row,
  which is exactly `SUM('payouts_ledger','entry_amount', entry_basis='adjustment_correction')`;
  `release_claim_reserve_fb50cb2e` creates a `payouts_reserve_released` row, which enters every branch of
  `reserve_standing`; `post_balance_recovery_b10514b8` creates a `payouts_deduction_posted` row dated today,
  which enters `net_flows_year`'s 12-month deduction sum;
- each `condition` restates the `policy_source` sentence at the same strength and scope, neither narrowed
  nor broadened, and none carries authoring-viewpoint phrasing ("in this task", "at the opening",
  "the current world");
- each `policy_source` is verbatim locatable in the blocked policy's own `rule` (line references under
  `prerequisite_sentences`).

### prerequisite_sentences

Four-point test on each edge's `policy_source`.

**E1 — `payouts_ext_claim_reserve_release` ← `payouts_ext_recovery_correction`**
Sentence (`payouts.extended.yaml:999-1001`, quoted at `:1046-1047`): "The sum freed from a claim reserve is
worked out only after every deductible recovery standing on the account that was taken beyond what the
enrolment's records bear carries its own correcting entry."
1. ordering connective: "only after" — joins this policy's own result ("the sum freed from a claim reserve")
   to what it waits on. ✓
2. declared `form: state`; what it waits on is a record-visible state — a deductible recovery entry
   "carries its own correcting entry" — named in the words the tables and finders use (`payouts_ledger`
   entries, "correcting entry" is the base charter's own word at `:753`, `find_payouts_ledger` returns
   "corrections"). No action, no performer, no tool. ✓
3. names no tool, no policy id, no snake_case token, no row id. ✓
4. strength and scope match `condition` ("Every deductible recovery entry on the account that was taken
   beyond the deductible the enrolment's records bear is answered by a correcting entry naming it") — an
   open set stated open in both. ✓
State-form resolution: exactly one write in this difficulty produces an entry carrying the correction basis —
`post_recovery_correction_f20745c1` (`task_tools.py:77-81`, `entry_basis="adjustment_correction"`,
`event_type="payouts_adjustment_posted"`). No other tool creates an adjustment row. The reader's derivation:
the sentence says the release waits on every over-taken deductible recovery carrying its own correcting
entry → the records show `entry_basis="claim_deductible_recovery"` rows and, where one is answered, an
`adjustment_correction` row naming it through `source_ledger_id` → the only policy whose own rule describes
booking such an entry is `payouts_ext_recovery_correction` ("The correcting entry books the sum
over-recovered…", `:846-847`) → its `target_tool` is the resolving action. Single reading. ✓

**E2 — `payouts_ext_requested_draw` ← `payouts_ext_claim_reserve_release`**
Sentence (`:1214-1215`, quoted at `:1277-1278`): "The sum a host may draw is not fixed before every reserve
standing against a claim on the account carries the release entry that answering that claim calls for."
1. "before" in the negated shape ("is not fixed before"). ✓
2. `form: state`; "every reserve standing against a claim … carries the release entry" is record-visible
   (`payouts_ledger` reserve rows with `hold_reason` "claim_open", answered by a `payouts_reserve_released`
   row naming them). No action, performer or tool. ✓
3. no tool, id or token. ✓
4. matches `condition` exactly. ✓
State-form resolution: the only write producing a `payouts_reserve_released` row is
`release_claim_reserve_fb50cb2e` (`task_tools.py:113-117`). Single reading. ✓

**E3 — `payouts_ext_schedule_qualification` ← `payouts_ext_negative_balance_recovery`**
Sentence (`:1680-1681`, quoted at `:1732-1733`): "The schedule a host moves onto is settled only once every
ground on which the account stands short of money the marketplace is owed carries the recovery entry taken
against it."
1. "only once". ✓  2. `form: state`, record-visible. ✓  3. clean. ✓  4. matches `condition`. ✓
State-form resolution: the only write producing a recovery entry against an earlier entry is
`post_balance_recovery_b10514b8` (`task_tools.py:149-153`, `entry_basis="chargeback_recovery"`,
`source_ledger_id` set). The seeded chargeback row that leaves the account short carries
`source_ledger_id: None`, so "carries the recovery entry taken against it" is readable off the records and
the answering entry is distinguishable from the entry it answers. Single reading. ✓

No rule carries a second wording of its own edge, a tool name, or another problem's id. No depended-on
policy restates its dependant's sentence: `payouts_ext_recovery_correction.rule` says nothing about reserve
release, `payouts_ext_claim_reserve_release.rule` says nothing about a draw, and
`payouts_ext_negative_balance_recovery.rule` says nothing about schedules. Docstrings are silent about
sequence (see `action_binding_and_uuids`).

**F-PRE-1 (observation) — base rules that state a cross-problem order grounding no declared edge.**
`payouts_closure.rule` (`:728`): "An account with a reserve still held or a claim still open is not closed
either; the reserve is released or the claim settled first…" and `payouts_evt_transfer_failure.rule` (`:678`):
"Money that has come back does not go out again until the host has confirmed the deposit details…" Both are
base sentences stating a cross-problem order. Neither grounds a declared edge and neither task's tree rests
on one, so both are recorded as observations rather than red lights. (The second is *not* contradicted by
`payouts_ext_requested_draw`, whose `credited_sum_measure` tier 1 holds the returned money out of the
credited sum, so the merged semantics agree on the outcome.)

### override_declarations

Findings only. Each affected task's file demonstrates the consequence against its own world.

Sentence-by-sentence sweep of every `base_policy_refs` entry of every extended policy. Base sentences the
extended policies follow unchanged are not listed; every sentence whose governed quantity the extended
handles differently is listed, with whether it is named in that policy's `overwrite`.

**`payouts_ext_recovery_correction`** — refs `payouts_evt_adjustment`, `payouts_evt_deductions`.
Declared: `payouts_evt_adjustment` "Money reaching the account from a claim settlement is booked as a
correction on its own basis…" ✓.
- **F-OV-1 (`SOURCE-POLICY RED`) — undeclared override of the adjustment ceiling.** Base
  `payouts_evt_adjustment.rule` (`:755`): "A correction above the schedule's adjustment ceiling is not made
  by the service desk at all and goes to the settlements team, whatever the host says about the amount."
  `params.per_tier` binds `adjustment_max_amount` for every schedule (`:778-785`); the Instant schedule's
  value is 1000.00 (`:176`). The sentence is not named in `overwrite` and is therefore inherited in full,
  yet `payouts_ext_recovery_correction` computes and books `correction_amount` with no ceiling of any kind
  in `rule`, `compute` or `params`. Where the computed correction exceeds the schedule's ceiling, base
  forbids the service desk from making it at all and extended books it. Consequence demonstrated in
  `0.md#policy_self_consistency`.
- **F-OV-2 (`SOURCE-POLICY RED`) — undeclared override of the adjustment window.** Base
  `payouts_evt_adjustment.rule` (`:754`) and its `eligibility.adjustment_window` (`:759-777`, with a full
  `temporal_basis`: anchor `payouts_ledger.entry_date`, `duration_source: params.adjustment_window_days`,
  `relation: not_after`, `boundary: inclusive`): "A correction may be made inside the schedule's adjustment
  window counted in whole calendar days from the day the original entry was booked, and an entry older than
  that window is not corrected on the account but dealt with as a goodwill payment instead." Instant's
  `adjustment_window_days` is 90 (`:175`). Not named in `overwrite`. The extended's `recovered_taken`
  aggregates deductible recoveries over a twelve-month or three-month window (`:855-857`, `:861`), so the
  correcting entry books a sum that includes recoveries older than the correctable window. Consequence
  demonstrated in `0.md#policy_self_consistency`.
- Base `payouts_evt_deductions` "A deduction posted in error is corrected by a correcting entry and never by
  editing the entry that was wrong" (`:578`) — followed, not overridden. ✓

**`payouts_ext_claim_reserve_release`** — refs `payouts_evt_reserve`, `payouts_evt_transfer_failure`.
Declared: `payouts_evt_reserve` "An open claim holds the claimed amount multiplied by the schedule's claim
multiple, capped at the schedule's claim ceiling, and that hold stands until the claim is paid, refused or
withdrawn whatever the routine hold period says." ✓ (this is what licenses releasing against a claim whose
`hostplan_claims` rows show no payment, refusal or withdrawal).
- **F-OV-3 (`SOURCE-POLICY RED`) — undeclared override of the routine reserve's hold period and release
  trigger.** Base `payouts_evt_reserve.rule` (`:595`): "Every schedule that carries a routine reserve takes
  its stated share of each earning and holds it for the schedule's hold period in whole calendar days
  counted from the day the earning was posted, releasing it on the trigger the schedule names rather than on
  request." Instant carries `reserve_percent_of_earning: 10`, `reserve_hold_days: 7`,
  `reserve_release_trigger: hold_days_elapsed` (`:169-170`). The sentence is not named in `overwrite`, so it
  is inherited: on this schedule every routine reserve matures seven days after the earning that produced it
  and is released. `payouts_ext_claim_reserve_release` nonetheless treats routine reserves as still standing
  and subtracts them from the sum freed (`routine_standing`, `:1065-1068`; `result`, `:1071`). Consequence
  demonstrated in `0.md#policy_self_consistency`.
- **F-OV-4 (observation) — the declared override leaves a hole.** The `superseded_clause` deletes the base's
  *hold-sizing* rule (claimed amount × claim multiple, capped at the claim ceiling) and `replaced_by` supplies
  a *release* rule in its place. After the replacement the merged charter states no rule at all for how large
  a claim hold is. No task computes a hold, so no consequence is demonstrable; this is the "dropped branch"
  shape and is recorded as an observation.

**`payouts_ext_requested_draw`** — refs `payouts_evt_transfer`, `payouts_account_opening`,
`payouts_evt_reserve`, `payouts_evt_transfer_failure`, `payouts_evt_deductions`.
Declared: `payouts_evt_transfer` "A host on a schedule that pays on request asks for the money themselves…" ✓;
`payouts_account_opening` tax-withholding sentence ✓; `payouts_evt_reserve` new-host reserve sentence ✓;
`payouts_evt_transfer_failure` returned-transfer-fee sentence ✓.
- **F-OV-5 (`SOURCE-POLICY RED`) — undeclared override of what a transfer carries.** Base
  `payouts_evt_transfer.rule` (`:632`): "A sweep carries the payable balance only, which is the available
  balance less anything held in reserve, and where that balance is under the schedule's minimum nothing goes
  out and the money waits for the next run", implemented by base's own `formula` (`:669-672`):
  `payable_balance: available_balance - reserve_balance`,
  `entry_amount: min(max(payable_balance, 0), maximum_payout_amount_per_transfer)` under
  `when: entry_basis == "payout_transfer"` — which is exactly the basis `release_host_payout_draw_8e4fb8ab`
  writes (`task_tools.py:41`). The `overwrite` entry names a different base sentence (who may ask), so this
  sentence and this formula are inherited in full and fix the same scored quantity at a different figure from
  the extended's `result` (`:1313`). Consequence demonstrated in `0.md#policy_self_consistency`.
- Base `payouts_evt_transfer` "Money leaves the account only while it is active…" — inherited and satisfied,
  not overridden. ✓ "One transfer never carries more than the schedule's per-transfer ceiling" — inherited;
  the extended's result is below Instant's 5000.00, so no conflict is demonstrable. ✓
- Base `payouts_evt_deductions` "Transfer fees are deductions in their own right and are taken on the day the
  transfer goes out" (`:577`) — the extended instead nets the return fee off the drawable sum
  (`return_fee_due`, `:1309`, `:1313`) rather than posting it as a deduction. The `overwrite` names the
  *returned-transfer-fee* sentence of `payouts_evt_transfer_failure`, not this one. Recorded as an
  observation: the difference is in how the fee reaches the statement, and `evaluation_criteria` is masked at
  freeze time, so no second scored figure can be demonstrated from the source layer alone.

**`payouts_ext_negative_balance_recovery`** — refs `payouts_evt_deductions`, `payouts_evt_earnings`.
Declared: `payouts_evt_deductions` "A deduction never takes the account below zero on the entry that causes
it, but where it does the balance stands negative and the marketplace recovers the schedule's share of each
later earning until it is cleared, beginning only once the schedule's grace period … has run." ✓ — the whole
sentence, including its grace-period clause and the `negative_balance_recovery_percent` share, is named, so
the extended's own recovery-share ladder and its recovery inside the grace period are both licensed. No
undeclared override found. Base `payouts_evt_earnings` sentences are read-only inputs here and are followed.

**`payouts_ext_schedule_qualification`** — refs `payouts_schedule_change`, `payouts_account_opening`,
`payouts_evt_earnings`, `payouts_evt_deductions`.
Declared: `payouts_schedule_change` "A host must meet the target schedule's settled trip count, monthly
earnings floor and tenure before moving to it, and a host who has fallen below the floor of the schedule they
hold is moved down…" ✓.
- **F-OV-6 (observation) — undeclared override of what "tenure" is.** Base `payouts_account_opening.rule`
  (`:477`): "…a schedule is open only where the host meets its settled trip count, its monthly earnings floor
  and its tenure in whole calendar days counted from the day their member profile was opened…". Not named in
  `overwrite`. The extended's `tenure_anchor` ladder (`:1712-1720`, `:1853-1867`) offers three anchors — the
  payout account's `opened_date`, the account's `next_payout_date`, and the date of the most recent trip
  earning — none of which is `customers.account_opened_date`. Both readings clear every schedule floor on
  task 1's world, so no consequence on the scored schedule is demonstrable; recorded as an observation here
  and taken up again under `factor_ladders` (F-FAC-2), where the same ladder fails a different test.
- **F-OV-7 (observation) — undeclared override of what "settled trips" counts.** Base
  `payouts_account_opening.measures` is `payouts_msr_settled_trips_lifetime` (`:460-462`): "Count of settled
  trips across every vehicle this host lists", window "The whole life of the host's account, with no time
  window." The extended counts trip-earning ledger entries over a twelve-month, three-month (×4) or
  statement-month window (`:1703-1711`). Not named in `overwrite`. No consequence on task 1's scored schedule
  (both readings clear the Express and Weekly trip floors and fail the Instant one).
- **F-OV-8 (observation) — the base's notice and effective-date machinery is neither followed nor
  overridden.** Base `payouts_schedule_change.rule` (`:504-505`): "A host may move between payout schedules,
  and the move takes effect on a future date rather than the day it is asked for… the change then takes
  effect the schedule's effective period after the notice is recorded, counted in whole calendar days from
  the day the notice is taken, with the day of notice itself not counted", with eligibility
  `schedule_change_notice_elapsed` anchoring "the notice is recorded" on `payouts_accounts.next_payout_date`
  (`:521-529`). Neither sentence is named in `payouts_ext_schedule_qualification.overwrite`, the extended
  rule is silent on effective dates, and `change_host_payout_schedule_75a33b7a` sets the schedule at once
  ("from then on the account is swept on that schedule's rhythm"). Whether the write is permissible today
  therefore depends on reading `next_payout_date` as the day the notice was recorded — a meaning the base
  `events` section contradicts twice ("The first date the account is due to be swept", `:243`; "The next
  sweep date under the new schedule", `:267`) and which `payouts_ext_schedule_qualification.rule` glosses a
  third way ("the day the deposit details were last taken up", `:1718-1719`). On task 1's world every reading
  that admits acting at all admits acting today, so this is an observation; the field's three incompatible
  meanings are the root cause and are recorded here once.

### factor_ladders

Structure only. Whether a factor bears weight is a fact about one world and lives in that task's
`factor_weight`.

| policy | factor | effect | decides | tiers | multi-source beyond fall-through | `cross_difficulty` |
| --- | --- | --- | --- | --- | --- | --- |
| recovery_correction | `recovery_window` | method | `recovered_taken` | 3 | yes (account schedule × enrolment claim-free date) | null |
| recovery_correction | `valuation_route_measure` | method | `settlement_gross` | 3 | no | hostplan |
| recovery_correction | `deductible_share_carried` | parameter | `deductible_share` | 3 | yes (enrolment plan × enrolment claim-free date) | hostplan |
| recovery_correction | `deductible_refund_share` | parameter | `refund_rate` | 3 | yes (claim liability row × recovery rows) | hostplan |
| claim_reserve_release | `settlement_answering_basis` | method | `release_basis` | 3 | yes (correction rows × reserve rows × return rows) | null |
| claim_reserve_release | `claim_hold_residual` | parameter | `residual_rate` | 3 | yes (account schedule × reserve rows) | null |
| claim_reserve_release | `routine_reserve_measure` | method | `routine_standing` | 3 | yes (account schedule × release rows) | null |
| claim_reserve_release | `routine_reserve_hold_back` | parameter | `routine_hold_back_rate` | 3 | yes (account schedule × reserve rows) | null |
| requested_draw | `credited_sum_measure` | method | `payable_credit` | 3 | yes (account schedule × return rows) | null |
| requested_draw | `reserve_standing_measure` | method | `reserve_standing` | 3 | yes (account schedule × release rows) | null |
| requested_draw | `tax_withholding_share` | parameter | `withholding_rate` | 3 | yes (account tax field × earning rows) | null |
| requested_draw | `routine_reserve_share` | parameter | `routine_topup_rate` | 3 | yes (account schedule × earning rows) | null |
| requested_draw | `return_fee_owed` | parameter | `return_fee_due` | 3 | yes (account schedule × return rows) | null |
| requested_draw | `month_credit_holdback` | parameter | `month_holdback_rate` | 3 | yes (account schedule × transfer rows) | null |
| negative_balance_recovery | `shortfall_recovery_share` | parameter | `recovery_share` | 3 | yes (account schedule × chargeback rows) | null |
| negative_balance_recovery | `later_earnings_measure` | method | `later_earnings` | 3 | yes (account schedule × transfer rows) | null |
| negative_balance_recovery | `shortfall_measure` | method | `outstanding` | 3 | yes (account schedule × chargeback rows) | null |
| negative_balance_recovery | `host_bearing_of_shortfall` | parameter | `host_bearing_share` | 3 | yes (claim liability row × enrolment plan) | hostplan |
| schedule_qualification | `monthly_earnings_measure` | method | `monthly_basis` | 3 | yes (account schedule × transfer rows) | null |
| schedule_qualification | `flows_offset_share` | parameter | `offset_share` | 3 | yes (account schedule × return rows) | null |
| schedule_qualification | `enrolment_standing_reduction` | parameter | `reduction_share` | 3 | no (both conditions read one enrolment row) | hostplan |
| schedule_qualification | `settled_trips_measure` | method | `qualifying_trips` | 3 | yes (account schedule × correction rows) | null |
| schedule_qualification | `tenure_anchor` | method | `qualifying_tenure` | 3 | yes (account schedule × account tax field) | null |

Counts per computation: recovery_correction 4 (2 parameter, 2 method); claim_reserve_release 4 (2, 2);
requested_draw 6 (4, 2); negative_balance_recovery 4 (2, 2); schedule_qualification 5 (2, 3). All inside
4–6 with at least 2 `parameter` and at least 1 `method`. Per task: task 0's computations carry multi-source
factors and three `cross_difficulty: hostplan` factors; task 1's carry multi-source factors and two
`cross_difficulty: hostplan` factors. Bindings are pairwise disjoint within each policy, and every `decides`
names an input binding, never `result`. Every tier of every ladder is stated in the `rule` with its condition
and its value or method, and implemented as a branch of the `decides` binding; no tier lives in only one
face. Every tier's value is drawn from that policy's `params`, and every method tier names a computation the
rule states. Labels are honest: every `parameter` ladder selects among numbers (`0.05/0.10/0.20`,
`0.50/0.25/0.00`, `0.00/0.10/0.25`, `1.00/0.50/0.00`, `0.24/0.10/0.00`, `0.10/0.03/0.00`, `20/40/0`,
`0.50/0.00/0.25`, `0.25/0.50/1.00`, `0.80/0.90/1.00`, `0.10/0.05/0.00`, `0.25/0.10/0.00`) and every `method`
ladder selects among different aggregations, windows or formulas. No two tiers of any one ladder select the
same value or the same method (checked ladder by ladder), and the tiers of each ladder are pairwise disjoint
as stated.

Two ladders fail the reality tests.

**F-FAC-1 (`SOURCE-FACTOR RED`) — four of `payouts_ext_requested_draw`'s six ladders have an unreachable
fall-through, because their tier conditions restate the policy's own scope.** The policy's first rule
sentence fixes its scope: "A draw on a schedule that pays on request is made by the host in person on their
own account, and the sum that leaves is the drawable sum worked out as this rule sets out." (`:1212-1213`),
`trigger: on_request`, and the superseded base sentence is "A host on a schedule that pays on request asks for
the money themselves". `compute.settles_on_request` is
`F('payout_schedule_name') == 'Keyturn Instant Payout Schedule'` (`:1286`), and Instant is the only variant
with `payout_frequency: on_request` (`:163`). So "the account settles only when the host asks" holds of every
customer who reaches this write. In four ladders that conjunct appears in tier 1 and tier 2 while the
remaining conditions of those two tiers are exhaustive complements of each other:

- `credited_sum_measure`: "a transfer has come back unpaid … in the twelve months" / "no transfer has come
  back unpaid … in that period";
- `reserve_standing_measure`: "a reserve has been freed from it in the statement month" / "no reserve has been
  freed from it in the statement month";
- `routine_reserve_share`: "fewer trip earnings than the schedule's qualifying number" / "the schedule's
  qualifying number of trip earnings or more";
- `month_credit_holdback`: "a transfer has already been released from it in the statement month" / "no
  transfer has been released from it in that month".

Each of those four ladders therefore has two reachable tiers, not three, and its fall-through — which is its
declared `baseline` and the value the computation document publishes as the standard treatment
(`available_month`, `RND(reserve_held_month + reserve_released_month, 2)`, `K('topup_none')`,
`K('holdback_scheduled')=0.25`) — is a treatment no customer this policy governs ever receives. That is the
straw-man baseline in its exact form: the whole-computation baseline rests on four tiers that cannot occur.
(`tax_withholding_share` carries no schedule conjunct and `return_fee_owed`'s tiers are "exactly one" /
"two or more", leaving zero returns to fall through, so those two ladders are sound.) The same conjunct in
the other four policies *is* a genuine divider, because none of those policies is scoped to one schedule.
Consequence demonstrated in `0.md#factor_weight`.

**F-FAC-2 (`SOURCE-FACTOR RED`) — `payouts_ext_schedule_qualification.tenure_anchor` is an unreal ladder.**
The quantity is "the qualifying tenure", which the base charter defines as how long the host has been on the
marketplace ("its tenure in whole calendar days counted from the day their member profile was opened",
`:477`; `minimum_host_tenure_days: Calendar days a host must have been on the marketplace to hold this
schedule`, `:88`).
- Tier 2's condition — "the tax documentation on the account is not on file" — is not something any
  marketplace weighs when settling how long a host has been trading; and its outcome, "the qualifying tenure
  runs from the day the account records as its next sweep date", measures tenure from a *sweep date*, which
  no such business publishes as its treatment. The rule's own gloss for that field ("which is the day the
  deposit details were last taken up") contradicts the base `events` definition of the same field twice
  (`:243`, `:267`).
- The fall-through — "the qualifying tenure runs from the day of the most recent trip earning credited to the
  account" — inverts the quantity: the more recently a host earned, the shorter their tenure, so a host of
  several years who took a trip last week has a tenure of a few days. As the fall-through it is also the
  factor's `baseline`, so it is what the computation document publishes as the standard method. This is the
  straw-man baseline the reality test names ("a default no such business applies to its ordinary customer").
Consequence demonstrated in `1.md#factor_weight`.

**F-FAC-3 (observation) — `settled_trips_measure`'s dividing condition does not bear on the quantity.**
Whether "a correcting entry has been booked to it in the twelve months up to that day" has no bearing on how
many trips a host has settled, and tier 2's outcome annualises a quarter's count ("multiplied by four") to
stand in for a settled-trip count that tier 1 takes as a straight twelve-month count. Recorded as an
observation; on task 1's world tier 1 is taken and the factor bears weight, so no red-light consequence is
demonstrable.

**F-FAC-4 (observation) — `enrolment_standing_reduction` is not multi-source and its tier-2 state is one the
`hostplan` charter says does not persist.** Both conditions of every tier read fields of one
`hostplan_enrollments` row (`suspension_reason`, `liability_balance_due`), so no tier is a conjunction over
distinct records. Tier 2 — "the protection enrolment behind the account stands in good order and carries a
liability still owed" — is the state `hostplan_lifecycle.rule` says is not allowed to stand
(`blueprint/products/hostplan.yaml:632`: "Cover is suspended, never quietly ignored, where an inspection
falls overdue, a required document expires, a host liability goes unpaid, a fraud review opens or the host
asks for it"). `hostplan` supplies a lapse period (`lapse_after_unpaid_days`, `:85`) but no grace before
suspension, so the seeded combination is at best on the edge of that product's own charter. Each task carries
other multi-source factors, so the per-task floor is still met; recorded as an observation.

**F-FAC-5 (observation) — `routine_reserve_measure`'s baseline sentence is inert.**
`payouts_ext_claim_reserve_release.baseline.rule` contains "The routine reserve the account must go on
carrying is the routine reserves taken in the statement month up to that day, and none of it is kept back out
of the sum freed." The second half sets the companion factor's fall-through to zero, so under the baseline the
quantity this factor decides is multiplied by nothing. A reader of the baseline alone cannot tell that
`routine_reserve_measure` decides anything. Both factors still bear weight independently on task 0's world
(see `0.md#factor_weight`), so this is an observation.

### findings

| id | verdict | bears on |
| --- | --- | --- |
| F-EQ-1 | `SOURCE-POLICY RED` | task 0 (demonstrated), task 1 (same defect, no gold consequence) |
| F-EQ-2 | observation | task 0 |
| F-EQ-3 | observation | task 0 |
| F-EQ-4 | observation | task 1 |
| F-EQ-5 | observation | task 1 |
| F-TOOL-1 | `SOURCE-POLICY RED` | task 0 (demonstrated), task 1 (demonstrated) |
| F-OV-1 | `SOURCE-POLICY RED` | task 0 |
| F-OV-2 | `SOURCE-POLICY RED` | task 0 |
| F-OV-3 | `SOURCE-POLICY RED` | task 0 |
| F-OV-4 | observation | task 0 |
| F-OV-5 | `SOURCE-POLICY RED` | task 0 |
| F-OV-6 | observation | task 1 |
| F-OV-7 | observation | task 1 |
| F-OV-8 | observation | task 1 |
| F-FAC-1 | `SOURCE-FACTOR RED` | task 0 |
| F-FAC-2 | `SOURCE-FACTOR RED` | task 1 |
| F-FAC-3 | observation | task 1 |
| F-FAC-4 | observation | task 1 |
| F-FAC-5 | observation | task 0 |
| F-PRE-1 | observation | both |

Charter-global verdict at freeze: **policy self-consistency FAILS** (F-EQ-1, F-TOOL-1, F-OV-1, F-OV-2,
F-OV-3, F-OV-5) and **factor structure FAILS** (F-FAC-1, F-FAC-2). The prerequisite graph and the
prerequisite sentences PASS.

## closing_checklist

Written after both tasks' `source_gt_comparison` sections were completed. **The difficulty does not close.**
Step 4's list, assessed honestly:

- **per-task files correspond one-to-one with the tasks** — `0.md` and `1.md` alongside this file, and the
  difficulty has M = 2 tasks. ✓ Old revisions: none; this is revision 1. **Every comparison section carries
  a PASS: NO.** `0.md#source_gt_comparison` records SOURCE-POLICY RED, SOURCE-CHAIN RED, SOURCE-FACTOR RED
  and SOURCE-TASK RED; `1.md#source_gt_comparison` records SOURCE-FACTOR RED.
- **extended policies fully covered, task scopes pairwise disjoint, task tools and GT closed** — ✓. The five
  extended policies split 3 / 2 across the two tasks with no overlap; `charter_scope` in each task file
  matches the tree derived independently; each of the five task tools is claimed by exactly one policy and
  called by exactly one task.
- **each task tool uses an independently generated, frozen uuid8** — ✓ (`#action_binding_and_uuids`).
- **every problem tree has one to three prerequisite problems, at least max(n − 1, 1) `value_input` edges,
  at least one problem resolved by an `owner=user` tool, and no cycle; the difficulty's `prerequisite` edges
  together are a DAG with no cross-task cycle** — ✓. Task 0: n = 2, two `value_input` edges, root resolved by
  `release_host_payout_draw_8e4fb8ab` (owner user). Task 1: n = 1, one `value_input` edge, root resolved by
  `change_host_payout_schedule_75a33b7a` (owner user). Two disjoint chains, no cycle.
- **every computation declares a self-sufficient baseline and four to six factors (2 `parameter`,
  1 `method`; per task ≥ 1 multi-source and ≥ 1 cross-difficulty), every ladder of at least three tiers
  stated in full in its rule, its tiers distinct in outcome and its conditions and outcomes ones that line of
  business actually holds, and every factor proved to bear weight against an honest baseline, with the
  baseline alone giving a definite number different from gold** — **NO.** Counts, tier distinctness, rule
  coverage, weight and baseline-differs-from-gold all hold and were verified figure by figure against each
  task's `factor_sensitivity` and `baseline_result`. What fails is the reality half: **F-FAC-1** (four of
  `payouts_ext_requested_draw`'s six ladders have a fall-through no customer this policy governs can reach,
  because "the account settles only when the host asks" is the policy's own scope) and **F-FAC-2**
  (`tenure_anchor`'s tier-2 condition does not bear on the quantity and its fall-through inverts it). In
  both cases the unreal tier is the declared `baseline`, so the baselines the computation documents will
  publish — 2503.56 for task 0's draw and "Keyturn Standard Payout Schedule" for task 1's schedule — rest on
  states the world cannot produce. Additionally, "the statement month up to that day" (F-EQ-1) leaves every
  baseline that uses it with two definite numbers rather than one.
- **instantiation-stage gates re-run once on the final form** — ✓ re-run by the auditor, read-only, with
  `replay_tasks.py --check` so that no task file was rewritten:
  `check_extended.py` EXTENDED OK; `check_task_tools.py` TASK TOOL CONTRACT OK;
  `check_solvability.py` SOLVABILITY OK (`0.json` 3 base gates / 29 seed rows, `1.json` 2 / 35);
  `check_compute.py` COMPUTE OK (suite means branches 35.50, steps 11.00; depth 65 / 40);
  `check_grounding.py` GROUNDING OK; `check_cross_fire.py` SCOPE OK;
  `replay_tasks.py --check` REPLAY OK (`0.json` 12 acts / 36 closure rows / match True, `1.json` 10 / 40 /
  match True). All green and byte-identical to the entry snapshot — which is the point: every finding above
  is one no gate in this set inspects.

**Difficulty verdict.** `policy self-consistency` FAIL, `problem tree holds` FAIL (task 0 only; task 1 PASS),
`factors bear weight` FAIL (the structural half: both tasks carry an unreal ladder whose unreal tier is the
published baseline), `unique solution` FAIL (task 0 only; task 1 PASS). The difficulty does **not** pass the
source-layer audit.

Summary of red lights by task:

| task | policy self-consistency | problem tree | factors | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | SOURCE-POLICY RED (T0-3, T0-4, T0-5, T0-7, T0-8) | SOURCE-CHAIN RED (T0-2) | SOURCE-FACTOR RED (T0-6) | SOURCE-TASK RED (T0-1) | **FAIL** |
| 1 | PASS with observations (T1-2, T1-3 carried from the charter) | PASS | SOURCE-FACTOR RED (T1-1) | PASS | **FAIL** |

Note on what is *not* a defect here: the auditor's independent derivation reproduced every scored value of
both tasks exactly — 1107.25 / 2901.16 / 1444.98 and 1514.00 / "Keyturn Weekly Batch Payout Schedule" — along
with every `baseline_result` and every one of the twenty-three `factor_sensitivity` figures. The arithmetic
of these tasks is sound. The failures are entailment failures: base sentences that no `overwrite` names and
that fix the same scored quantity differently, a window phrase the rule and the compute read differently, a
proof field contradicted by recomputation, tool docstrings asserting effects their bodies do not perform, and
two ladders whose fall-through states no customer of the policy can occupy.

---

# revision_2

## charter_global_frozen (revision 2)

- freeze hash `payouts.extended.yaml` sha256:16 = `8faaf61fdd46267e` (revision 1: `8ad43d7d7f1eef56` — CHANGED)
- freeze hash `task_tools.py` sha256:16 = `901b819f029bd632` (revision 1: `6aabc488c8d1ee8c` — CHANGED)
- masked view hashes: `0.json` `f47b6a7f946968d8` (was `01ae985b52c8a6aa` — CHANGED),
  `1.json` `ea21c7f56dd67259` (was `c4547dab5ae9f8e7` — CHANGED)
- freeze time (UTC): 2026-09-22T09:58:13Z
- auditor: same independent source-layer auditor; revision 1 above is left untouched.
- **Both shared inputs moved, so this section is re-derived in full rather than carried forward by
  reference.** Both task worlds moved as well, so neither task's revision-1 per-task derivation is carried
  forward in any part.
- fields permitted / masked: as revision 1. contamination: none — no `tasks/*.json` file was opened before
  this section and both revision-2 task freezes were on disk.

### entry conditions (Step 0, revision 2)

The brief supplied the re-run gate snapshot on the reworked artifacts and the four new hashes. All four
recomputed hashes agree with the brief. The coordinator's independent statement that the base section is
key-for-key identical to `blueprint/products/payouts.yaml` was re-checked here: `head -786` of the extended
file differs from the blueprint product only by a trailing blank line, so **base was not edited, including
for the two items routed around**. Entry conditions complete.

### policy_conflict_scan (revision 2)

Same five extended policies, same five task tools, same one-to-one map and same two disjoint
`prerequisite` components as revision 1; subjects, target tools and computed quantities remain pairwise
disjoint and jointly cover the charter. Cross-category declarations moved and were re-checked against the
`compute` bodies:

| policy | `cross_category` declared | `CFIELD`/`X*` calls present | agree |
| --- | --- | --- | --- |
| `payouts_ext_recovery_correction` | hostplan (history) — now also reads the claim-progress rows | `XLATEST` ×3, `XSUM` ×2, `XCOUNT` ×2, `CFIELD` ×3 | yes |
| `payouts_ext_claim_reserve_release` | `[]` | none | yes |
| `payouts_ext_requested_draw` | `[]` | none | yes |
| `payouts_ext_negative_balance_recovery` | hostplan (branch) | `CFIELD` ×1, `XLATEST` ×1 | yes |
| `payouts_ext_schedule_qualification` | hostplan (branch) — `reads` changed from `[status, suspension_reason, liability_balance_due]` to `[suspension_reason, hostplan_claims.appraisal_amount]` | `CFIELD` ×1, `XCOUNT` ×1 | yes |

No undeclared cross-category read. No overlapping-subject conflict among the extended five.

### rule_compute_equivalence (revision 2)

Full re-sweep of every `compute` binding of all five policies against `compute_basis` and the `rule`.

**F-EQ-1 (revision 1 `SOURCE-POLICY RED`) — CLOSED.** `grep -c "statement month"` over the extended
section (lines 787-1958) returns **0**. Every window that revision 1 flagged is now written as "the month
up to that day" / "the twelve months up to that day" / "the three months up to that day", which is exactly
what `within_months=1` / `12` / `3` computes under `MONTHS(row_date, NOW)` with `0 <= m < within_months`.
Checked binding by binding: `payouts_ext_recovery_correction.recovered_taken` (`:861` vs rule `:816-817`),
`payouts_ext_claim_reserve_release.routine_hold_month` (`:1083` vs `:1037-1038`),
`payouts_ext_requested_draw.reserve_held_month` / `reserve_released_month` / `month_credits`
(`:1327-1328`, `:1350` vs `:1258-1259`, `:1290-1291`),
`payouts_ext_negative_balance_recovery.earn_month` / `net_month` (`:1580`, `:1585` vs `:1535-1536`,
`:1544-1545`), `payouts_ext_schedule_qualification.earn_month` / `trips_month` (`:1821`, `:1836` vs
`:1748-1749`, `:1781-1782`). The ledger's `statement_period` stamp is no longer invoked by any extended
sentence, so the three-way ambiguity is gone.

**F-EQ-2 — CLOSED.** `appraised_sum` is now
`XLATEST('hostplan','hostplan_claims','appraisal_amount', date_field='claim_date', event_type='hostplan_claim_appraised')`
(`:862`), a latest, matching "the appraisal recorded on the most recent appraisal made under the enrolment"
(`:822-823`). The `XMAX` is gone from the file.

**F-EQ-3 — CLOSED.** The rule's scope was widened to match the compute rather than the compute narrowed:
"every supplement added under the enrolment" (`:826`) and "money has been recovered under the enrolment"
(`:838-841`) now say what `XSUM(... hostplan_claims ...)` over the customer's enrolment actually sums.
The two faces agree.

**F-EQ-4 — CLOSED.** `payouts_ext_schedule_qualification.rule` now states the sign explicitly: "The
deductions and corrections booked to the account in the twelve months up to that day are netted, and that
net, taken at the offset share and spread evenly over twelve months, is **added** to the qualifying monthly
earnings; because deductions are booked as negative entries and corrections as positive ones, that net
lowers the qualifying monthly earnings whenever deductions outweigh corrections and lifts them whenever
corrections outweigh deductions" (`:1757-1761`), which is exactly `qualifying_earnings`'s `+ RND(net_flows_year * offset_share / 12, 2)` (`:1832`).

**F-EQ-5 — CLOSED.** The anchor is now in the rule: "How long the balance has stood short is counted in
whole calendar days from the day of the most recent entry on which money charged back by a guest was taken
off the account, up to that day" (`:1527-1528`), matching
`DAYS(LATEST(..., entry_basis='chargeback_recovery'), NOW)` (`:1575`).

New observations from this sweep:

- **N-1 (observation) — a dead binding.** `payouts_ext_requested_draw.ledger_net_month` (`:1326`) is
  computed and used by nothing (`available_month` was removed with the old ladder), and its
  `compute_basis` (`:1362`) quotes a sentence about the reserve standing rather than about a netting. No
  quantity moves; recorded as an observation.
- **N-2 (observation) — a justification clause that misstates the base window.**
  `payouts_ext_recovery_correction.rule` (`:816-819`) counts the recoveries "in the month up to the day
  the correction is worked out" and then gives as its reason "a recovery booked earlier than that stands
  outside the window within which an entry may be corrected on the account at all". Base
  `payouts_evt_adjustment` puts that window at `adjustment_window_days`, which is 90 on the Instant
  schedule (`:175`) and 60 on the entry schedule (`:112`), not one month. The operative clause and its
  stated reason therefore pick out different windows for any recovery between roughly 30 and 90 days old.
  Neither task's world carries such a recovery (task 0's three are 386, 176 and 8 days old), so no
  consequence is demonstrable and this is an observation, not a red light.
- **N-3 (observation) — the routine-reserve prose rule is now removed from the merged charter.** The second
  `overwrite` entry of `payouts_ext_claim_reserve_release` (`:992-996`) supersedes the whole base sentence
  "Every schedule that carries a routine reserve takes its stated share of each earning and holds it for the
  schedule's hold period …", and the replacement says only what is *kept back out of a release*. After the
  replacement no prose sentence in the merged charter states how large a routine reserve taken on an earning
  is. Base's `payouts_evt_reserve.formula` (`:625-627`) still fixes it at the schedule's share, and the
  seeded reserves obey that formula exactly (verified under `factor_ladders` below), so nothing moves.
- **N-4 (observation) — a vacuous conjunct survives in one ladder.** `return_fee_owed` still opens both of
  its non-fall-through tiers with "the account settles only when the host asks", which holds of every
  customer `payouts_ext_requested_draw` governs. Unlike the four ladders of revision 1's F-FAC-1, its
  fall-through is still reachable (zero returns in twelve months), so the ladder keeps three reachable
  tiers. Revision 1 explicitly exempted this ladder on the same grounds; the judgement is unchanged.
- **N-5 (observation) — `payouts_ext_recovery_correction` raises rather than degrades when the
  cross-category reads are absent.** With `hostplan` unavailable, `appraised_sum` is `None` and
  `settlement_gross`'s `RND(...)` raises `TypeError`. The other four policies return a number. Nothing an
  agent does produces this state; recorded for completeness.

### action_binding_and_uuids (revision 2)

Each `(target_tool, computes)` pair is still claimed by exactly one policy. uuid8s are unchanged and still
five distinct values with no shared prefix, tail, sequence or adjacency: `8e4fb8ab`, `f20745c1`, `fb50cb2e`,
`b10514b8`, `75a33b7a`. Exactly five tools are exported — the helper the reworker reports having added and
inlined is not present as a sixth `@tool` (`grep -c "@tool" task_tools.py` = 5). No docstring names another
tool or carries a cross-tool ordering word.

**F-TOOL-1 (revision 1 `SOURCE-POLICY RED`) — CLOSED.** All four ledger-writing tools now carry a
`ctx.update("payouts_accounts", …)` alongside their `ctx.create`, and each moves exactly the balance its
docstring names, in the direction it names:

| tool | docstring claim | body |
| --- | --- | --- |
| `release_host_payout_draw_8e4fb8ab` | "The balance the host may draw falls by the sum sent" | `available_balance = available_balance − draw_amount` (`:43-47`) |
| `post_recovery_correction_f20745c1` | "the account's balance rises by the sum put back" | `available_balance = available_balance + correction_amount` (`:87-91`) |
| `release_claim_reserve_fb50cb2e` | "The account's reserve balance falls by the sum freed while the total credited stays as it was" | `reserve_balance = reserve_balance − release_amount`, `available_balance` untouched (`:128-132`) |
| `post_balance_recovery_b10514b8` | "the balance free to be paid out falls by that sum" | `available_balance = available_balance − recovery_amount` (`:169-173`) |

Each re-reads the current row through `ctx.find` before adjusting, so successive calls compose. `ctx.find`,
`ctx.create`, `ctx.update` and `ctx.make_id` are all on `ToolContext` (`erlbench/tools.py:86, 111, 121, 80`).
The read is a single-row lookup used to move a balance, not an aggregate, an eligibility test or a branch:
no body compares, refuses, errors or hints, so the tool layer still judges no prerequisite.
`change_host_payout_schedule_75a33b7a` remains a single `ctx.update`.

Two points checked because a balance write is a path to fresh defects, and both are clean:
no computation reads `F('available_balance')` or `F('reserve_balance')`, and
`payouts_ext_requested_draw.rule` now says so outright — "neither of those two quantities is read off the
balances the account row carries" (`:1244-1246`) — so the new writes cannot feed back into any scored
figure; and the direction of each update matches the sign the corresponding ledger row carries.

### prerequisite_graph (revision 2)

Unchanged in every respect from revision 1: the same three `value_input` edges with the same gates
(`settlement_booked` `:1075`, `reserve_standing` `:1338`, `net_flows_year` `:1825`), all `form: state`, no
`fallback_reason` anywhere, every `problem` an extended policy id in this file, two disjoint chains, no
cycle, each `resolved_by` the depended-on policy's own `target_tool`, each `condition` at the sentence's
strength, no authoring-viewpoint phrasing. Each gate still names a binding that exists in the blocked
policy's `compute`.

### prerequisite_sentences (revision 2)

All three `policy_source` sentences are byte-identical to revision 1 and still verbatim locatable in the
blocked policy's own `rule` (`:1015-1017`, `:1242-1243`, `:1746-1747`), so the four-point test, the
state-form resolution to a single write, and the absence of second wordings, tool names and other problems'
ids all carry from `#prerequisite_sentences` above without change. Re-verified that no depended-on rule
restates its dependant's sentence and that the new overwrite entries introduced no cross-problem order.

**F-PRE-1 — NO CHANGE, accepted.** The two base sentences that state a cross-problem order grounding no
declared edge (`payouts_closure` `:728`, `payouts_evt_transfer_failure` `:678`) are in the base section,
which may not be edited, and neither task's tree rests on either. They remain observations.

### override_declarations (revision 2)

Full sentence-by-sentence re-sweep of every `base_policy_refs` entry of every extended policy.

**F-OV-1 (revision 1 `SOURCE-POLICY RED`, adjustment ceiling) — ROUTED AROUND, and the route holds.**
The base sentence is still not named in any `overwrite`, so it is still inherited in full: "A correction
above the schedule's adjustment ceiling is not made by the service desk at all and goes to the settlements
team" (`:755`), Instant's `adjustment_max_amount` = 1000.00 (`:176`). The route is that the computed
correction now falls below the ceiling. Verified, not assumed: the recoveries counted are narrowed from a
twelve-month window to "the month up to that day", the seeded claim is smaller, and a new instalment ladder
takes a share of the excess. The figure this produces on task 0's world is derived in `0.md#revision_2` and
is **542.50**, against a ceiling of 1000.00. The base clause is therefore satisfied, not moved out of sight
— the desk's own write is one the base rule permits it to make.

**F-OV-2 (revision 1 `SOURCE-POLICY RED`, adjustment window) — ROUTED AROUND, and the route holds.**
The base window sentence and its `adjustment_window` eligibility (`:754`, `:759-777`) are still inherited
unreplaced. The route is that `recovered_taken` now aggregates over `within_months=1` (`:861`) instead of
twelve months, and the `recovery_window` ladder that spanned twelve and three months has been removed
outright. One month is strictly inside the 90-day window Instant allows, so every recovery the correcting
entry's amount is built from is one the base rule permits to be corrected. On task 0's world the counted set
collapses to a single recovery, which is also the entry the correcting entry names, so the amount and the
named object are built from exactly the same row — the split that made revision 1's T0-1 a uniqueness
failure is gone. Residual: N-2 above, which is about the rule's stated *reason*, not its operative window.

**F-OV-3 (revision 1 `SOURCE-POLICY RED`, routine-reserve hold period) — CLOSED by a declared override.**
`payouts_ext_claim_reserve_release.overwrite` now carries a second entry (`:992-996`) naming the base
sentence verbatim and replacing it. The 7-day maturity that revision 1 showed would have released the
routine reserves is no longer in force, so the extended's treatment of them as standing is licensed.
Residual: N-3.

**F-OV-4 (revision 1 observation, the hole left by the first override) — CLOSED.** The first `overwrite`
entry's `superseded_clause` is narrowed from the whole base sentence to the fragment "that hold stands until
the claim is paid, refused or withdrawn whatever the routine hold period says" (`:988-989`), which is a
verbatim substring of base `:597`. The hold-sizing half of that base sentence therefore stands, and the
seeded claim reserve obeys it: 4650.00 = claim_amount 3100.00 × Instant's `claim_reserve_multiple` 1.5
(`:171`), under the 15000.00 ceiling. The merged charter no longer has a hole where the size of a claim hold
should be.

**F-OV-5 (revision 1 `SOURCE-POLICY RED`, what a transfer carries) — CLOSED by a declared override.**
`payouts_ext_requested_draw.overwrite` now carries a second entry (`:1195-1199`) naming base
`payouts_evt_transfer`'s payable-balance sentence verbatim — including its minimum clause — and replacing
it with "The drawable sum starts from the payable balance, which is the credited sum of the account less the
reserve standing on it, and neither of those two quantities is read off the balances the account row
carries." Base's `formula` for `entry_basis == "payout_transfer"` implements only that sentence, so
superseding the sentence supersedes the figure it fixed. The three-way split of revision 1's C-0-1 is gone.

**F-OV-6 and F-OV-7 (revision 1 observations, tenure and settled trips) — CLOSED by a declared override.**
`payouts_ext_schedule_qualification.overwrite` now carries a third entry (`:1705-1709`) naming base
`payouts_account_opening`'s whole qualification sentence verbatim and replacing it with "The qualifying
tenure is the whole calendar days from the day the payout account was opened up to that day, and the
qualifying settled trips are counted from the trip earnings the account itself carries rather than from the
trips the host has run over the whole life of their membership." That covers both the member-profile tenure
anchor and the lifetime settled-trips measure in one declaration, and the extended's `qualifying_tenure`
(`:1838`, `DAYS(F('opened_date'), NOW)`) and `qualifying_trips` (`:1837`) implement exactly it.

**F-OV-8 (revision 1 observation, the effective-date machinery) — CLOSED by a declared override.**
A second entry (`:1700-1704`) names base's "the move takes effect on a future date rather than the day it is
asked for" sentence verbatim and replaces it with "The move is recorded once the schedule's effective period
has run from the day the notice was taken, and the account settles on the schedule it has moved onto from
the day the move is recorded", which is a rule the immediate `ctx.update` of
`change_host_payout_schedule_75a33b7a` satisfies once the effective period has run. Residual observation:
base's own `schedule_change_notice_elapsed` still anchors "the notice is recorded" on
`payouts_accounts.next_payout_date` (`:521-529`) while base's `events` section defines that field as a
future sweep date (`:243`, `:267`). That contradiction lives entirely in the base section, which may not be
edited, and the extended no longer adds a third meaning of its own — the `tenure_anchor` gloss that carried
it was deleted. Whether it bites on task 1 is settled in `1.md#revision_2`.

No **new** undeclared override was found. Every remaining base sentence of every `base_policy_refs` entry
was reached: the inherited-and-followed set now includes `payouts_agg_multi_holding`'s single-account rule,
`payouts_account_opening`'s deposit-verification and host-only-deposit-details rules, `payouts_holds`'
ground rule, `payouts_closure`, `payouts_evt_earnings`' posting rules, `payouts_evt_deductions`' "never by
editing the entry that was wrong", `payouts_evt_reserve`'s dedup rule for releases, `payouts_evt_transfer`'s
state gate and per-transfer ceiling, and `payouts_evt_transfer_failure`'s "money that has come back does not
go out again until the host has confirmed the deposit details" — the last of which the extended's
`credited_sum_measure` tier 1 continues to honour by holding the returned money out.

### factor_ladders (revision 2)

| policy | factor | effect | tiers | fall-through reachable in this policy's scope | multi-source beyond fall-through | `cross_difficulty` |
| --- | --- | --- | --- | --- | --- | --- |
| recovery_correction | `valuation_route_measure` | method | 3 | yes | no | hostplan |
| recovery_correction | `deductible_share_carried` | parameter | 3 | yes | no (both conditions read one enrolment row) | hostplan |
| recovery_correction | `deductible_refund_share` | parameter | 3 | yes | yes (claim liability row × recovery rows) | hostplan |
| recovery_correction | **`recovery_instalment_share`** (new) | parameter | 3 | yes | yes (reimbursement rows × appraisal rows) | hostplan |
| claim_reserve_release | `settlement_answering_basis` | method | 3 | yes | yes | null |
| claim_reserve_release | `claim_hold_residual` | parameter | 3 | yes | yes | null |
| claim_reserve_release | `routine_reserve_measure` | method | 3 | yes | yes | null |
| claim_reserve_release | `routine_reserve_hold_back` | parameter | 3 | yes | yes | null |
| requested_draw | `credited_sum_measure` | method | 3 | **yes (was no)** | yes (return rows × transfer rows) | null |
| requested_draw | `reserve_standing_measure` | method | 3 | **yes (was no)** | yes (release rows × hold rows) | null |
| requested_draw | `tax_withholding_share` | parameter | 3 | yes | yes | null |
| requested_draw | `routine_reserve_share` | parameter | 3 | **yes (was no)** | yes (trip-earning rows × reserve rows) | null |
| requested_draw | `return_fee_owed` | parameter | 3 | yes | yes | null |
| requested_draw | `month_credit_holdback` | parameter | 3 | **yes (was no)** | yes (transfer rows × correction rows) | null |
| negative_balance_recovery | `shortfall_recovery_share` | parameter | 3 | yes | yes | null |
| negative_balance_recovery | `later_earnings_measure` | method | 3 | yes | yes | null |
| negative_balance_recovery | `shortfall_measure` | method | 3 | yes | yes | null |
| negative_balance_recovery | `host_bearing_of_shortfall` | parameter | 3 | yes | yes | hostplan |
| schedule_qualification | `monthly_earnings_measure` | method | 3 | yes | yes | null |
| schedule_qualification | `flows_offset_share` | parameter | 3 | yes | yes | null |
| schedule_qualification | **`cover_standing_reduction`** (replaces `enrolment_standing_reduction`) | parameter | 3 | yes | **yes (enrolment row × claim rows)** | hostplan |
| schedule_qualification | **`short_account_setaside`** (new, takes the deleted ladder's slot) | parameter | 3 | yes | yes (chargeback rows × whole-ledger netting) | null |
| schedule_qualification | `settled_trips_measure` | method | 3 | yes | yes | null |

Counts per computation: recovery_correction 4 (3 parameter, 1 method); claim_reserve_release 4 (2, 2);
requested_draw 6 (4, 2); negative_balance_recovery 4 (2, 2); schedule_qualification 5 (3, 2). All inside
4-6 with ≥ 2 `parameter` and ≥ 1 `method`. Bindings pairwise disjoint within each policy; every `decides`
names an input, never `result`; every tier is stated in the `rule` with its condition and its outcome and
implemented as a branch of the `decides` binding; no tier lives in only one face; no two tiers of any one
ladder select the same value or method; tiers pairwise disjoint as stated. Labels honest.

**F-FAC-1 (revision 1 `SOURCE-FACTOR RED`) — CLOSED.** The scope conjunct "the account settles only when
the host asks" is gone from the four ladders that carried it, and each replacement pair of conditions leaves
the fall-through reachable within `payouts_ext_requested_draw`'s own scope:

| factor | tier 1 | tier 2 | fall-through, now reachable when |
| --- | --- | --- | --- |
| `credited_sum_measure` | a return in twelve months **and** no transfer out since | a return in twelve months **and** a transfer out since | no return in twelve months |
| `reserve_standing_measure` | a reserve freed in the month | no release in the month **and** a hold taken in the month | neither in the month |
| `routine_reserve_share` | fewer than the qualifying trip earnings in twelve months | qualifying or more **and** a reserve taken in that period | qualifying or more **and** no reserve taken |
| `month_credit_holdback` | a transfer released in the month | no transfer released **and** a correcting entry booked in the month | neither in the month |

Each divider also bears on the quantity it decides, which the old ones did not: whether a transfer has gone
out since a return decides whether the returned money is still un-sent; whether a reserve moved in the month
decides which stretch of reserves is still standing; whether the account is still carrying reserves decides
whether a routine top-up is still owed; whether the month has already been drawn on or already corrected
decides how much of it is safe to release. Residual: N-4.

**F-FAC-2 — CLOSED by deletion, and the replacement is not itself decoration.** The `tenure_anchor` ladder
is gone; `qualifying_tenure` is now the plain binding `account_age_days` (`:1838`), which is exactly the
declared override's sentence. The slot is taken by `short_account_setaside`, a three-tier parameter ladder
over `chargeback_quarter` and `net_all`. Whether it bears weight is a fact about task 1's world and is
settled in `1.md#revision_2`. `settled_trips_measure` was also rebuilt: it now divides on how long the
payout account has been open (≥ a year / ≥ a quarter and under a year / under a quarter), which is a
condition that genuinely bears on whether a count should be read whole or annualised — **F-FAC-3 CLOSED**.

**F-FAC-4 — CLOSED.** `enrolment_standing_reduction` is replaced by `cover_standing_reduction`, whose tiers
now conjoin the enrolment's `suspension_reason` with a count of appraisals over `hostplan_claims` — two
distinct record sets, so the ladder is genuinely multi-source. The tier that revision 1 showed described a
state `hostplan_lifecycle` says does not persist (good order **and** an unpaid liability) is gone: the
condition is now "stands in good order and a claim has been appraised under it in the twelve months", which
`hostplan` allows without reservation, and `liability_balance_due` is 0.00 on both seeded enrolments.
The ladder order was also inverted (good-order tier first, suspended tier second) and both tiers now carry
the appraisal conjunct; re-checked for the reachability question the coordinator raised — with
`enrolment_suspension` absent the first tier's `== 'none'` fails and the second's `!= 'none'` would succeed,
but the shared `appraisals_year > 0` conjunct is 0 in that state, so both fail and the fall-through is
selected. All three tiers remain reachable, pairwise disjoint, and stated in the rule in the same order as
the compute (`:1769-1773` vs `:1828`). The reorder disturbed no other tier.

**F-FAC-5 — CLOSED.** `hold_back_matured` moved from 0.00 to 0.25 and the baseline sentence now reads "…and
a quarter of it is kept back out of the sum freed" (`:1037-1038`, `:1174-1175`), so the quantity
`routine_reserve_measure` decides is no longer multiplied by nothing under the baseline.

**Correction to revision 1.** Revision 1's `factor_ladders` table recorded `deductible_share_carried` as
multi-source while recording the structurally identical `enrolment_standing_reduction` as not multi-source.
The stricter reading — conditions over *distinct records* — is the right one, and under it
`deductible_share_carried` is not multi-source either, since `protection_plan_name` and
`claim_free_since_date` are two fields of one `hostplan_enrollments` row. This changes no revision-1
verdict: both tasks met the multi-source floor through other factors then, and do so again now. The
revision-1 text is left as written.

### findings (revision 2)

| revision-1 id | disposition verified here | verdict |
| --- | --- | --- |
| F-EQ-1 | every window reworded to what the primitive computes; 0 remaining "statement month" | CLOSED |
| F-EQ-2 | `XMAX` → `XLATEST` | CLOSED |
| F-EQ-3 | rule scope widened to "under the enrolment" to match the compute | CLOSED |
| F-EQ-4 | sign stated explicitly in the rule | CLOSED |
| F-EQ-5 | anchor stated in the rule | CLOSED |
| F-TOOL-1 | four tools now move the balance each docstring names, in the right direction | CLOSED |
| F-OV-1 | routed around; base ceiling genuinely satisfied (demonstrated in `0.md#revision_2`) | CLOSED |
| F-OV-2 | routed around; counted window strictly inside the base window; ladder removed | CLOSED (residual N-2) |
| F-OV-3 | declared overwrite | CLOSED (residual N-3) |
| F-OV-4 | superseded clause narrowed to a fragment; base hold sizing stands and the seed obeys it | CLOSED |
| F-OV-5 | declared overwrite naming the payable-balance sentence | CLOSED |
| F-OV-6 / F-OV-7 | declared overwrite naming `payouts_account_opening`'s qualification sentence | CLOSED |
| F-OV-8 | declared overwrite naming the effective-date sentence | CLOSED (residual: base-only anchor ambiguity) |
| F-FAC-1 | scope conjunct removed from four ladders; all fall-throughs reachable | CLOSED (residual N-4) |
| F-FAC-2 | ladder deleted; `qualifying_tenure` a plain binding under a declared override | CLOSED |
| F-FAC-3 | `settled_trips_measure` now divides on the account's age | CLOSED |
| F-FAC-4 | `cover_standing_reduction`; multi-source, and the impossible state is gone | CLOSED |
| F-FAC-5 | `hold_back_matured` 0.00 → 0.25 | CLOSED |
| F-PRE-1 | no change; base-only, grounds no edge, no task rests on it | ACCEPTED |

New charter-global observations this round: N-1 (dead binding `ledger_net_month`), N-2 (justification clause
misstating the base adjustment window), N-3 (routine-reserve prose rule removed by the new override), N-4
(vacuous conjunct in `return_fee_owed`), N-5 (`recovery_correction` raises when the cross reads are absent).
None is a red light: none can be shown to hand a task a second scored answer, a second action or an
unreachable tier.

**Charter-global verdict at the revision-2 freeze: policy self-consistency PASS with observations; factor
structure PASS.** Every revision-1 charter-global red light is closed, by a declared override where the
reworker claimed one and by a verified change of world or ladder where it claimed a route. No new
charter-global red light.

## closing_checklist (revision 2)

Written after both tasks' revision-2 `source_gt_comparison` sections were completed.
**The difficulty still does not close, by one item.**

- **per-task audit files correspond one-to-one with the tasks, old revisions traceable** — ✓. `0.md` and
  `1.md` each carry an untouched `revision 1` and an appended `revision_2`; this file carries both
  charter-global sections and both closing checklists. **Every comparison section carries a PASS: NO** —
  `0.md#source_gt_comparison` (revision 2) records one `SOURCE-TASK RED`. `1.md` is clean.
- **extended policies fully covered, task scopes pairwise disjoint, task tools and GT closed, uuid8s
  independently generated and frozen** — ✓, re-derived in `#policy_conflict_scan` and
  `#action_binding_and_uuids` (revision 2). Exactly five `@tool` functions are exported, so the helper the
  reworker inlined did not become a sixth task tool.
- **every problem tree has one to three prerequisite problems, at least max(n − 1, 1) `value_input` edges,
  at least one problem resolved by an `owner=user` tool, no cycle, and the difficulty's edges together a
  DAG** — ✓. Task 0: n = 2, two `value_input` edges, root on `release_host_payout_draw_8e4fb8ab`
  (owner user). Task 1: n = 1, one `value_input` edge, root on `change_host_payout_schedule_75a33b7a`
  (owner user). Two disjoint chains. Both trees re-derived on the reseeded worlds and both edges of task 0
  and the single edge of task 1 shown load-bearing against recomputed figures.
- **every computation declares a self-sufficient baseline and four to six factors (2 `parameter`,
  1 `method`; per task ≥ 1 multi-source and ≥ 1 cross-difficulty), every ladder of at least three tiers
  stated in full in its rule, tiers distinct in outcome, conditions and outcomes ones that line of business
  actually holds, every factor proved to bear weight against an honest baseline, and the baseline alone
  giving a definite number different from gold** — ✓ **this round**. Counts: 4 / 4 / 6 / 4 / 5. All
  twenty-three factor substitutions move their scored value; all five whole-computation baselines are
  definite and differ from gold (131.90, 0.00, 8116.00, 680.00, Keyturn Standard Payout Schedule). Both
  revision-1 reality failures are closed: the four `payouts_ext_requested_draw` ladders no longer restate
  the policy's scope and their fall-throughs are reachable, and the `tenure_anchor` ladder is gone with a
  weight-bearing replacement in its slot.
- **instantiation-stage gates re-run once on the final form** — ✓, re-run by the auditor read-only with
  `replay_tasks.py --check`: EXTENDED OK, TASK TOOL CONTRACT OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  SCOPE OK, REPLAY OK. The two `.cpython-312.pyc` files those runs created under `env/` were removed; the
  `.cpython-313.pyc` files predate this audit.

**Difficulty verdict (revision 2).** `policy self-consistency` **PASS**, `problem tree holds` **PASS**,
`factors bear weight` **PASS**, `unique solution` **FAIL on task 0 only** (T2-0-1). The difficulty does not
pass the source-layer audit, but it fails on one stale sentence rather than on any of the eight structural
red lights of revision 1.

| task | policy self-consistency | problem tree | factors | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | **SOURCE-TASK RED (T2-0-1)** | **FAIL** |
| 1 | PASS | PASS | PASS | PASS | **PASS** |

**Every revision-1 item id, with its verified disposition.** None was accepted on the reworker's word; each
was re-derived from the reworked charter, the reworked tools and the reseeded worlds.

| id | claim | verified |
| --- | --- | --- |
| F-EQ-1 | CLOSED by rewriting the windows | **CLOSED** |
| F-TOOL-1 | CLOSED; tools move the balances | **CLOSED** |
| F-OV-1 | ROUTED AROUND | **CLOSED** — 542.50 against a 1000.00 ceiling |
| F-OV-2 | ROUTED AROUND; one factor removed | **CLOSED** — one-month window strictly inside the base 90-day window; residual observation N-2 |
| F-OV-3 | CLOSED by a declared overwrite | **CLOSED**; residual observation N-3 |
| F-OV-5 | CLOSED by a declared overwrite | **CLOSED** |
| F-FAC-1 | CLOSED; conjunct removed from four ladders | **CLOSED**; residual observation N-4 |
| F-FAC-2 | CLOSED by deleting the ladder | **CLOSED**; the replacement bears weight |
| F-OV-4, F-OV-6, F-OV-7, F-OV-8 | ACTED ON | **CLOSED** (F-OV-8's residual is base-only) |
| F-EQ-2, F-EQ-3, F-EQ-4, F-EQ-5 | ACTED ON | **CLOSED** |
| F-FAC-3, F-FAC-4, F-FAC-5 | ACTED ON | **CLOSED** |
| F-PRE-1 | NO CHANGE, with reasoning | **ACCEPTED** — base-only, grounds no edge, merged semantics agree |
| T0-1 | closed | **CLOSED** |
| T0-2 | CORRECTED | **CORRECTED and verified** — every figure in the new `why_false` reproduces |
| T0-3, T0-4, T0-5, T0-6, T0-7, T0-8 | fold into the charter items | **CLOSED** |
| O0-1 … O0-5 | closed | **CLOSED** (including the routine reserves now at exactly 10% of the earnings they name) |
| O0-6 | no change | **ACCEPTED** |
| T1-1 | CLOSED by deleting the ladder | **CLOSED** |
| T1-2, T1-3 | fold into F-TOOL-1 and F-EQ-1 | **CLOSED** |
| O1-1 … O1-5 | fold into the charter items | **CLOSED** |
| O1-6 | no change | **CLOSED** (F-EQ-4 / F-EQ-5 were in fact fixed) |

**New in revision 2:** one red light, `0.md#findings` T2-0-1 — a regression introduced by the reseed, in
which `evaluation_criteria[9].argument_uniqueness_tracing.source_ledger_id` still states the revision-1
reserve amount 3912.40 where the reseeded row carries 4650.00, and where the same file states 4650.00
correctly in three other places. Five charter-global observations (N-1 … N-5) and three task-0
observations (O2-0-1 … O2-0-3), none of which can be shown to hand a task a second scored answer, a second
action or an unreachable tier.

Note on what is *not* a defect: the auditor's independent derivation reproduced every scored value of both
reseeded tasks exactly — 542.50 / 3043.13 / 1356.95 and 1703.00 / "Keyturn Weekly Batch Payout Schedule" —
together with all five `baseline_result`s and all twenty-three `factor_sensitivity` figures, the two
skip-edge replays (2554.88 and 0.00), the opening-world contrast (−1699.39 and 0.00) and task 1's
506.75-against-492.56. The rework is sound in substance; one sentence of its proof was not carried across
the reseed.

---

# revision_3

## charter_global_frozen (revision 3)

- freeze hash `payouts.extended.yaml` sha256:16 = `ea548e72010f4daa` (revision 2: `8faaf61fdd46267e` — CHANGED)
- freeze hash `task_tools.py` sha256:16 = `901b819f029bd632` (revision 2: identical — UNCHANGED)
- masked view hashes: `0.json` `f47b6a7f946968d8`, `1.json` `ea21c7f56dd67259` — both UNCHANGED
- freeze time (UTC): 2026-09-22T10:27:44Z
- auditor: same independent source-layer auditor; revisions 1 and 2 above are left untouched.
- **Re-derivation rule applied.** The charter moved, so this whole section is re-derived rather than carried
  forward. The tool module did not move, so `#action_binding_and_uuids` (revision 2) is carried forward **by
  reference on the strength of the identical hash** and re-derived only where a charter edit could bear on
  it. Both worlds stand still, but a charter edit can move a per-task conclusion with the world unchanged,
  so **both tasks were re-derived blind from scratch** rather than carried forward.
- fields permitted / masked: as revisions 1 and 2. contamination: none.

### entry conditions (Step 0, revision 3)

All four hashes recomputed and in agreement with the brief. Base section re-checked directly:
`head -786` of the extended file differs from `blueprint/products/payouts.yaml` only by a trailing blank
line, so base was not edited this round either. The coordinator's gate snapshot is cited; the gates were
re-run read-only at the close (below).

### what changed, and what it could reach

Four of the five policies' prose or compute moved; `payouts_ext_negative_balance_recovery` and
`payouts_ext_schedule_qualification` are unchanged in `rule`, `compute`, `compute_basis`, `factors`,
`baseline`, `overwrite` and `prerequisite`, which is why task 1's figures cannot move and are nonetheless
re-derived below. The edits:

| policy | edit | could it reach a scored value? |
| --- | --- | --- |
| `recovery_correction` | the false justification clause deleted from `rule`, `baseline.rule` and `compute_basis.recovered_taken` | no — `compute` untouched |
| `claim_reserve_release` | second `superseded_clause` narrowed from the whole base sentence to a fragment | no — prose only |
| `requested_draw` | `ledger_net_month` deleted; `settles_on_request` deleted; the schedule conjunct removed from `return_fee_owed`'s tiers, rule and overwrite; `reserve_standing` floored at nothing in all three tiers, in the factor baseline and in `baseline.rule` | **yes, in principle** — the floor and the fee ladder both feed `result` |
| `schedule_qualification` | none | no |

### policy_conflict_scan (revision 3)

Unchanged in structure: same five policies, same five tools, same one-to-one map, same two disjoint
`prerequisite` components, subjects and computed quantities still pairwise disjoint and jointly covering the
charter. `cross_category` declarations are unchanged and still agree with the `CFIELD`/`X*` calls present in
each `compute`; `payouts_ext_requested_draw` and `payouts_ext_claim_reserve_release` still declare `[]` and
still make no cross-category call.

### rule_compute_equivalence (revision 3)

Re-swept mechanically and by reading. Results:

- every `factors[].ladder` tier's `when` and `method` string is a **verbatim** sentence or clause of that
  policy's own `rule` (0 misses across all 23 factors), and every branch of each `decides` binding is a tier
  the rule states;
- every sentence of every `baseline.rule` is present in the policy's `rule` (0 misses across all five);
- **no dead bindings anywhere** (0 across all five policies) — **N-1 CLOSED**: `ledger_net_month` is gone
  from `payouts_ext_requested_draw.compute` and from `compute_basis`, and nothing else became dead in its
  place. `settles_on_request` was removed from the same policy with it and is referenced by no binding,
  factor or ladder there; it survives only in `payouts_ext_claim_reserve_release`, where 12 rule/ladder
  occurrences of "settles only when the host asks" are matched by the one binding that reads it;
- `grep -c "statement month"` over the extended section is still **0**, and
  `grep -c "stands outside the window"` over the whole file is **0**.

**N-2 — CLOSED.** The clause "; a recovery booked earlier than that stands outside the window within which
an entry may be corrected on the account at all, and is not counted" is deleted from all three places it
appeared: `payouts_ext_recovery_correction.rule` (now `:816-817`, ending at "…less the deductible the host
actually carries on the settled loss."), `baseline.rule` (`:963-965`) and
`compute_basis.recovered_taken` (`:879`). The operative window — "the deductible recoveries booked to the
account in the month up to the day the correction is worked out" — stands alone and is exactly
`within_months=1`, which is unchanged at `:859`. The rule no longer asserts anything about base's
`adjustment_window_days`, so the one-month aggregate and base's 90-day window no longer contradict each
other; base's window remains inherited and remains satisfied on task 0's world.

**O2-0-1 — CLOSED, and the floor is carried consistently.** `payouts_ext_requested_draw` now states
"Whichever stretch is measured, the reserve standing is never less than nothing, because freeing more in a
period than was taken in it leaves the account holding nothing back rather than owing the host more than it
holds" (`:1257-1259`), and the same sentence is carried in `baseline.rule` (`:1484-1486`) and prepended to
`compute_basis.reserve_standing` (`:1370`). `compute.reserve_standing` (`:1335`) applies `MX(…, 0)` to
**all three** branches, and `factors[reserve_standing_measure].baseline` is
`MX(RND(reserve_held_month + reserve_released_month, 2), 0)` (`:1412`), so the floor reaches the factor's
own baseline as well as the whole-computation one. The floor is a general sentence qualifying every tier
rather than a fourth tier, so the ladder still has exactly three tiers and each is still stated in the rule.

**N-5 — NO CHANGE, and the reasoning is accepted.** `payouts_ext_recovery_correction` still raises rather
than returning a number when the `hostplan` reads are absent (`appraised_sum` is `None`, and
`settlement_gross`'s `RND(...)` fails). The reworker declines to make the policy total on the ground that
the prose states no treatment for "no appraisal has been made under the enrolment", so a guard in `compute`
would be `compute` inventing a basis. **That reading is correct on this skill's own terms.** Check 2
requires the sweep back to "confirm that compute invents no basis of its own", and a
`if appraised_sum is None then 0` branch is precisely such an invention; the alternative — writing a prose
sentence for the no-appraisal case — would add a rule no task exercises, with no near-miss and no tier to
carry it, which is padding rather than policy. The state is unreachable by any rollout: it arises only when
the harness strips the category for its own cross-difficulty probe. The residual is that the policy is
partial — a host with an enrolment but no appraised claim has no defined `correction_amount` — which is a
constraint on how a future task of this difficulty may be seeded, not a defect of either task here (task 0's
enrolment carries an appraised row; task 1 does not use this policy). Recorded as an observation, carried
forward unchanged.

### action_binding_and_uuids (revision 3)

`task_tools.py` is byte-identical to revision 2 (`901b819f029bd632`), so revision 2's conclusions are
carried forward by reference: five tools, five independently generated uuid8s (`8e4fb8ab`, `f20745c1`,
`fb50cb2e`, `b10514b8`, `75a33b7a`), one atomic write plus one balance update each, no docstring naming
another tool or carrying a cross-tool ordering word, no body judging a prerequisite. Re-checked for the one
way a charter edit could reach the module: `payouts_ext_requested_draw`'s rule still says the payable
balance is not read off the account row's balances (`:1241-1243`), and no computation of any policy reads
`F('available_balance')` or `F('reserve_balance')`, so the tools' balance writes still cannot feed back into
a scored figure. `grep -c "@tool"` = 5, so no helper became a sixth task tool.

### prerequisite_graph and prerequisite_sentences (revision 3)

Unchanged. The three `policy_source` sentences are byte-identical to revisions 1 and 2 and each was
re-checked as a **verbatim** substring of the blocked policy's own `rule` (3/3 OK). Gates, kinds, forms,
conditions, `resolved_by` and acyclicity are all as before; the edits touched no `prerequisite` block.
**F-PRE-1** remains a base-only observation grounding no edge.

### override_declarations (revision 3)

Every `overwrite.superseded_clause` of every extended policy was re-checked as a **verbatim** substring of
the named base policy's `rule`: **16/16 OK**, including the two clauses that moved this round.

**N-3 — CLOSED.** `payouts_ext_claim_reserve_release.overwrite[1].superseded_clause` is narrowed from the
whole base sentence to the fragment "holds it for the schedule's hold period in whole calendar days counted
from the day the earning was posted, releasing it on the trigger the schedule names rather than on request"
(`:990-991`), which is the part the extended actually deviates from. Base's "Every schedule that carries a
routine reserve takes its stated share of each earning and …" therefore stays in the merged charter, so the
charter once again states how large a routine reserve is, and the seeded reserves obey it. **F-OV-3 stays
closed**: the 7-day hold period and the `hold_days_elapsed` release trigger are still superseded, so the
extended's treatment of the routine reserves as standing is still licensed.

**N-4 — CLOSED, and the removal did not cost anything.** The conjunct "the account settles only when the
host asks and" is gone from both non-fall-through tiers of `return_fee_owed`, from the rule sentence
(`:1283-1286`) and from the `payouts_evt_transfer_failure` `replaced_by` (`:1211`), all three now reading
"turns on how often the account's transfers have come back". The three faces still agree with
`compute.return_fee_due` (`:1344`). The ladder keeps three tiers — exactly one return / two or more / zero —
which are pairwise disjoint, all reachable, and distinct in value (20.00 / 40.00 / 0.00). The binding the
conjunct was the last reader of, `settles_on_request`, was removed with it and nothing else referenced it in
that policy. Whether the factor still bears weight is a fact about task 0's world and is settled in
`0.md#revision_3`.

No new undeclared override. The remaining base sentences of every `base_policy_refs` entry were reached
again and are either followed or named; in particular base `payouts_evt_adjustment`'s ceiling and window
remain inherited unreplaced, which is the route F-OV-1 and F-OV-2 were closed by and which task 0's figures
must therefore still satisfy.

**Observation N-6 (new, minor).** Narrowing `overwrite[1].superseded_clause` to a mid-sentence fragment
leaves the base sentence's residue ending in "and", so a document that renders base and extended together
produces "Every schedule that carries a routine reserve takes its stated share of each earning and
*<the replacement>*", which is ungrammatical. The semantics are unambiguous and nothing in the source layer
turns on it; recorded because the KB render will have to join those two halves.

### factor_ladders (revision 3)

Counts re-derived: recovery_correction 4 (3 `parameter`, 1 `method`, 4 `cross_difficulty`);
claim_reserve_release 4 (2, 2, 0); requested_draw 6 (4, 2, 0); negative_balance_recovery 4 (2, 2, 1);
schedule_qualification 5 (3, 2, 1). All inside 4-6 with ≥ 2 `parameter` and ≥ 1 `method`. Every ladder has
three tiers, pairwise disjoint as stated, distinct in value or method, every tier verbatim in the rule and
implemented as a branch. Bindings still pairwise disjoint within each policy; every `decides` names an
input.

One structural consequence of N-4 to record: `return_fee_owed`'s tiers are now single-condition, so that
ladder is **no longer multi-source**. The per-task floor is unaffected — task 0's computations still carry
`deductible_refund_share`, `recovery_instalment_share`, `settlement_answering_basis`,
`credited_sum_measure`, `reserve_standing_measure`, `routine_reserve_share` and `month_credit_holdback` as
conjunctions over distinct record sets, and task 1 is untouched.

**Observation N-7 (new, minor).** The floor on `reserve_standing` is a sentence that qualifies all three
tiers rather than a tier of the ladder, so `factors[reserve_standing_measure].ladder` does not mention it.
In a world where two of the three stretches both net below nothing, two tiers would select the same
*value* (nothing) while remaining distinct as *methods*. On task 0's world they do not (tier 1 gives a
positive figure and the fall-through gives the floor), and the tier test is about the value or method a
tier *selects*, which the three methods keep distinct. Recorded so that a later reseed does not collapse
the ladder without anyone noticing.

### findings (revision 3)

| item | claim | verified |
| --- | --- | --- |
| N-1 dead binding | REMOVED | **CLOSED** — 0 dead bindings across all five policies |
| N-2 false justification clause | DELETED from rule, baseline.rule, compute_basis | **CLOSED** — 0 occurrences; operative window stands alone and matches `within_months=1` |
| N-3 routine-reserve prose rule | superseded clause narrowed to the fragment | **CLOSED** — verbatim fragment; base's taking rule back in the merged charter; F-OV-3 still closed |
| N-4 vacuous conjunct | REMOVED, with its last reader | **CLOSED** — three faces agree, three tiers disjoint and reachable, fee unchanged; weight re-tested per task |
| N-5 partial policy | NO CHANGE, deliberately | **ACCEPTED** — the two-way-equivalence ground is the right one on this skill's terms; carried as an observation |
| O2-0-1 baseline above the account | floor carried in every tier | **CLOSED** — floor in rule, baseline.rule, compute_basis, all three branches and the factor baseline |
| O2-0-2, O2-0-3 | aliases | **CLOSED / carried** with N-2 and N-1/N-3/N-4/N-5 respectively |
| F-PRE-1 | base-only | **ACCEPTED**, unchanged |

New this round: N-6 (the fragment override leaves an ungrammatical residue for the renderer) and N-7 (the
floor sits outside the ladder and could collapse two tiers' values under a future reseed). Neither can be
shown to hand a task a second scored answer, a second action or an unreachable tier.

**Charter-global verdict at the revision-3 freeze: policy self-consistency PASS with observations; factor
structure PASS.** No revision-2 charter-global item is open, and no new charter-global red light.

## closing_checklist (revision 3)

Written after both tasks' revision-3 `source_gt_comparison` sections were completed.
**The difficulty closes. Both tasks PASS on all four relationships.**

- **per-task files correspond one-to-one with the tasks, old revisions traceable** — ✓. `0.md` and `1.md`
  each carry revisions 1, 2 and 3, each earlier revision untouched. **Every revision-3 comparison section
  carries a PASS**, for the first time in this audit.
- **extended policies fully covered, task scopes pairwise disjoint, task tools and GT closed, uuid8s
  independently generated and frozen** — ✓; the tool module is unchanged by hash and `grep -c "@tool"` = 5.
- **every problem tree has one to three prerequisite problems, at least max(n − 1, 1) `value_input` edges,
  at least one problem resolved by an `owner=user` tool, no cycle, and the difficulty's edges together a
  DAG** — ✓, both trees re-walked and both sets of edges re-shown load-bearing on recomputed figures.
- **every computation declares a self-sufficient baseline and four to six factors (2 `parameter`,
  1 `method`; per task ≥ 1 multi-source and ≥ 1 cross-difficulty), every ladder of at least three tiers
  stated in full in its rule, tiers distinct in outcome, conditions and outcomes ones that line of business
  actually holds, every factor proved to bear weight against an honest baseline, and the baseline alone
  giving a definite number different from gold** — ✓. Mechanically re-checked this round: 0 dead bindings,
  0 ladder tiers absent from their rule, 0 baseline sentences absent from their rule, 16/16 `overwrite`
  clauses verbatim in base, 3/3 prerequisite sentences verbatim in their own rules. All 23 factor
  substitutions move their scored value; all five whole-computation baselines are definite and differ from
  gold (131.90, 0.00, **5126.77**, 680.00, Keyturn Standard Payout Schedule).
- **instantiation-stage gates re-run once on the final form** — ✓, read-only with
  `replay_tasks.py --check`: EXTENDED OK, TASK TOOL CONTRACT OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  SCOPE OK, REPLAY OK (`0.json` 12 acts / 36 closure rows / match True; `1.json` 10 / 40 / match True).

**Difficulty verdict (revision 3).** `policy self-consistency` **PASS**, `problem tree holds` **PASS**,
`factors bear weight` **PASS**, `unique solution` **PASS**. The difficulty passes the source-layer audit.

| task | policy self-consistency | problem tree | factors | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | **PASS** |
| 1 | PASS | PASS | PASS | PASS | **PASS** |

### the independent stale-figure sweep, and why its result is not the reworker's

The reworker's sweep defines its own oracle, so a clean run from it proves nothing on its own. This audit
ran a separate one. Method: extract every decimal figure from every proof-bearing string field of both task
files (`evaluation_criteria`, `computations`, `prerequisite_closure`, `solvability_contract`,
`charter_scope`, `required_documents`; `design_rationale` excluded, since a worklog legitimately recounts
history), and test each against a closure built **only from this audit's own blind derivation** — the value
of every field of every seeded row, every `compute` binding evaluated at each handling moment under gold and
under every factor baseline and under the whole baseline, every declared `params` value, and every variant
parameter — then close that set under the arithmetic the rules actually perform (multiplication by a share,
addition, subtraction, division by twelve and by three).

Result: **38 figures fell outside the named-binding closure and all 38 were verified genuine.** Thirty-three
were products the rules compute but do not name as bindings (349.25 = 3492.50 × 0.10; 100.12 = 200.24 × 0.50;
50.06 = 200.24 × 0.25; 452.70 = 1886.24 × 0.24; 56.59 = 1886.24 × 0.03; 270.38 = 1081.50 × 0.25;
2989.23 = 53.90 − 3043.13; 1048.00 = 1310.00 × 0.80; 262.00 the remainder; 64.19 = 7703.00 × 0.10 ÷ 12;
65.50 = 655.00 × 0.10; 32.75 = 655.00 × 0.05; 506.75 = 655.00 − 50.00 − 65.50 − 32.75). Five needed direct
checking against the world and all five hold: task 0's −1699.39 is the root's `payable_base` on the opening
world (3150.85 − 4850.24, recomputed on the spot), and task 1's 13060.00 and 8370.00 are the all-time sums
of the 21 earning rows and the 6 transfer rows (recomputed from the 34 seeded rows).
**Zero stale figures in either file.** The reworker's clean result is corroborated by an oracle it did not
supply.

### dispositions

| item | claim | verified |
| --- | --- | --- |
| **T2-0-1** (round 2's only red light) | CLOSED | **CLOSED** — `evaluation_criteria[9].argument_uniqueness_tracing.source_ledger_id` reads "entry_amount 4650.00", which is the row's value and agrees with the three other fields that already stated it; the superseded 3912.40 has zero occurrences in either file |
| the stale-figure sweep | run mechanically, clean | **CORROBORATED** by an independent sweep with its own oracle, above |
| **N-1** dead binding | REMOVED | **CLOSED** — 0 dead bindings across all five policies; `settles_on_request` removed with it and referenced nowhere in that policy |
| **N-2** false justification clause | DELETED from three faces | **CLOSED** — 0 occurrences; the operative one-month window stands alone and still matches `within_months=1`; the counted set, the correction and base's inherited 90-day window are all unchanged |
| **N-3** routine-reserve prose rule | superseded clause narrowed | **CLOSED** — the fragment is verbatim in base; base's taking rule is back in the merged charter and the seeded reserves obey it; F-OV-3 stays closed |
| **N-4** vacuous conjunct | REMOVED with its last reader | **CLOSED, and it cost nothing** — three faces agree, three tiers disjoint and reachable, the fee is unchanged at 20.00, the factor still bears weight (1376.95 against gold 1356.95), and the task's multi-source and cross-difficulty floors are still met by other factors. Task 1, which passed in round 2, does not claim that policy and was re-derived from scratch to confirm it did not move |
| **N-5** partial policy | NO CHANGE, deliberately | **ACCEPTED** — the ground is correct on this skill's terms: a guard would be `compute` inventing a basis the prose does not state, and a prose sentence for the case would be a rule no task exercises. Carried as an observation, with the residual that a future task of this difficulty must not seed a host who holds an enrolment but no appraised claim |
| **O2-0-1** baseline above the account | floor in every tier | **CLOSED** — the draw's published baseline falls from 8116.00 to **5126.77**, below `available_all` of 5493.35; gold is unchanged at 1356.95 and `reserve_standing_measure`'s own baseline moved from 4858.28 to 2676.15 and still differs from gold |
| **O2-0-2, O2-0-3** | aliases | **CLOSED / CARRIED** with the items above |
| the no-regression claim | asserted | **VERIFIED** — gold unchanged in both tasks (542.50 / 3043.13 / 1356.95 and 1703.00 / Weekly Batch), the opening-world contrasts unchanged (0.00 and Express), both skip-edge replays unchanged (2554.88 and 0.00), base byte-identical, all 16 `overwrite` clauses verbatim on both sides, the tool module unchanged by hash, both terminal accounts still equal to the ledgers behind them (4136.40 / 1807.11 and −3013.00), every `tier_taken` a declared tier of the current charter, and 22 of the 23 factor substitutions identical — the one that moved, `reserve_standing_measure`, moved because O2-0-1 asked it to |

**New observations this round:** N-6 (narrowing an `overwrite` to a mid-sentence fragment leaves base's
residue ending in "and", which the KB render will have to join grammatically) and N-7 (the floor on
`reserve_standing` is a sentence qualifying all three tiers rather than a tier, so a future reseed in which
two stretches both net below nothing would give two tiers the same value while their methods stayed
distinct). Neither hands a task a second scored answer, a second action or an unreachable tier.

**A note on this audit's own conduct.** An ordering error was made this round on task 0: its
`source_gt_comparison` section was written in the same disk write as its frozen derivation, that is, before
the GT had been read. The blind derivation itself was unaffected and is unaltered; the comparison was
afterwards checked line by line against the revealed file and every entry in it proved correct, so nothing
was rewritten to fit. The error is recorded in full at `0.md#process_disclosure` rather than tidied away.
Task 1's comparison was written only after its GT had been read.
