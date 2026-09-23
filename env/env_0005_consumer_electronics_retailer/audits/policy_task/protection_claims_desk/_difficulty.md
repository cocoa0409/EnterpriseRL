# Policy-task audit — protection_claims_desk / charter-global

## charter_global_frozen

| item | value |
| --- | --- |
| `protection.extended.yaml` | sha256_16 = `39a422fbedfb1378` (verified by re-hash at audit time) |
| `task_tools.py` | sha256_16 = `5f5dd14dd046c9e8` (verified by re-hash at audit time) |
| masked view 0.json | sha256_16 = `b82a2214ef16b110` |
| masked view 1.json | sha256_16 = `4bebe8a93bfc76c2` |
| freeze time | 2026-09-18, before any task's GT fields were read |
| auditor | independent policy-task auditor (not the instantiating agent) |

**Fields permitted while this section was written:** `blueprint/blueprint.yaml`, `blueprint/db_schema.json`,
`blueprint/share_tools.py`, `blueprint/products/*.yaml`, this difficulty's `protection.extended.yaml`
(base section + `extended_policies`, including `rule` / `compute_basis` / `compute` / `overwrite` /
`prerequisite` / `factors` / `baseline` / `inputs`), `task_tools.py` in full, and `erlbench/` plus the
compute-DSL evaluator in `skills/erl-task-instantiate/scripts/check_compute.py`.

**Fields explicitly masked and not read while this section was written:** every task's
`evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`,
`solvability_contract`, `prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state`. This
section contains nothing derived from a revealed GT; it was completed and written to disk before the
reveal of either task.

**Entry conditions (checked, not re-run).** The instantiation-stage gate snapshot was supplied with the
brief (`check_extended`, `check_task_tools`, `check_solvability`, `check_compute`, `check_grounding`,
`check_cross_fire`, `replay_tasks --check`, all green). `check_traceability` is deferred to the render
step by design and its absence is not treated as a defect. The masked views were constructed
mechanically by the caller; the three hashes above were independently re-computed at audit time and
match the masking report byte for byte, and each masked view was confirmed to carry exactly
`['frozen_time', 'initial_state', 'user_scenario']`. Entry conditions are complete.

### policy_conflict_scan

The base section of `protection.extended.yaml` was diffed key by key against
`blueprint/products/protection.yaml`: `category`, `display_name`, `binding`, `lifecycle`, `accounts`,
`parameter_schema`, `variants`, `events`, `measures` and `policies` are **identical objects**; the only
extra top-level key is `extended_policies`. The base copy has not been rewritten.

**Subjects and claims.** The 15 base policies and 8 extended policies were cross-tabulated on subject
event type:

| extended policy | subject | `computes` | target tool | trigger |
| --- | --- | --- | --- | --- |
| `protection_ext_premium_late_fee_scale` | `protection_premium_charge` | `late_fee_amount` | `bill_premium_late_fee_5ae6a6af` | state_due |
| `protection_ext_fleet_instalment_billing` | `protection_premium_charge` | `instalment_amount` | `bill_premium_instalment_3dd4c03b` | state_due |
| `protection_ext_premium_arrears_settlement` | `protection_premium_payment` | `settlement_amount` | `settle_premium_arrears_c5640f60` | on_request |
| `protection_ext_fleet_invoice_settlement` | `protection_premium_payment` | `settlement_amount` | `settle_fleet_invoice_2818623b` | on_request |
| `protection_ext_claim_repair_settlement` | `protection_claim_payout` | `payout_amount` | `book_claim_payout_542e239c` | state_due |
| `protection_ext_spoilage_allowance` | `protection_claim_payout` | `allowance_amount` | `book_spoilage_allowance_79e3e314` | on_request |
| `protection_ext_claim_excess_charge` | `protection_deductible_charge` | `deductible_amount` | `bill_claim_deductible_d5a520f4` | state_due |
| `protection_ext_claim_excess_settlement` | `protection_deductible_payment` | `settlement_amount` | `settle_claim_deductible_46d57fef` | on_request |

Two policies share each of `protection_premium_charge`, `protection_premium_payment` and
`protection_claim_payout`, but each pair is separated by `premium_kind` / `settlement_basis` /
opening-clause trigger and by a distinct `computes` name, so no two policies decide the same quantity
on the same row. See finding **F-07** for the one place where this separation is thin.

**Claimed scopes.** Derived from the two worlds and the `prerequisite` graph alone (not from
`charter_scope`, which was masked): task 0's tree is
`{late_fee_scale, premium_arrears_settlement, claim_repair_settlement, spoilage_allowance}` and task 1's
is `{fleet_instalment_billing, claim_excess_charge, claim_excess_settlement, fleet_invoice_settlement}`.
The two sets are **pairwise disjoint** and **jointly complete** over the 8 extended policies.

**Cross-category read boundaries.** Every `cross_category` declaration is matched by the categories
actually read in `compute` (`membership` for late_fee_scale and arrears_settlement; `service` for
repair_settlement, spoilage_allowance and excess_charge; `credit` for excess_settlement,
fleet_instalment_billing and fleet_invoice_settlement; `credit` + `orders` for
fleet_instalment_billing). No compute reads a category its policy does not declare.

**Eligibility and time anchors.** Every base `eligibility` entry of kind `time` was enumerated with its
`applies_to`:

| base policy | eligibility | kind | applies_to |
| --- | --- | --- | --- |
| `protection_plan_admission` | `item_age_inside_limit` | time | `protection_plan_purchase` |
| `protection_premium_delinquency` | `premium_grace_run` | time | `protection_plan_terminate_nonpayment` |
| `protection_claim_intake` | `report_window_open` | time | `protection_claim_file` |
| `protection_claim_review_hold` | `review_days_not_exceeded` | time | `protection_claim_hold_release` |
| `protection_cancellation_refund` | `free_look_open` | time | `protection_plan_cancel` |

None of `protection_plan_purchase`, `protection_plan_terminate_nonpayment`, `protection_claim_file`,
`protection_claim_hold_release`, `protection_plan_cancel` appears among the eight extended write
subjects. **The instantiating agent's third claim — that no base eligibility of kind `time` governs any
of the eight write subjects — is independently confirmed**, and an empty `temporal_feasibility` is the
correct consequence of that fact rather than a concealment. The report-window and grace clocks were
then checked by hand against both worlds in the per-task files; see finding **F-06** for the one place
where a base *rule sentence* (not a declared eligibility) does impose a clock on an extended write
subject, and the per-task files for the arithmetic showing it is satisfied in both worlds.

**Terminal states.** No conflict found between base lifecycle transitions and the terminal state any
extended policy leaves: every task tool writes one `protection_events` row and moves exactly one
cached figure on `protection_plans` (`premium_outstanding`, `coverage_remaining` or
`deductible_outstanding`), and no tool changes `status`. `protection_premium_billing`'s
`billable_plan_state` (application_received / active / claim_hold) and
`protection_claim_settlement`'s `payable_plan_state` (active / claim_hold) are both satisfied by a
plan standing `active`, which is the state of the plan in both worlds.

### rule_compute_equivalence

Checked mechanically and then by hand over all eight policies.

**Forward (compute -> rule): clean.** For every one of the eight policies, every binding in `compute`
has a `compute_basis` key, no `compute_basis` key names a non-existent binding, and **every
`compute_basis` value is a verbatim substring of that policy's own `rule`** (whitespace-normalised).
150 bindings checked across the eight policies; zero exceptions. Compute invents no basis of its own at
the level of named quantities.

**Backward (rule -> compute): two sentences make a promise no binding keeps.** See findings **F-04**
and **F-05**.

**Every `baseline.rule` sentence is present in the policy's own `rule`**: checked sentence by sentence
for all eight policies; zero exceptions. Each `baseline.rule` is also self-sufficient — a reader can
compute a definite number from it and the records with no factor applied (verified by computing the
whole-baseline fall-back number for all eight computations across the two worlds; every one is
definite and every one differs from the value the full rule gives — figures in the two task files).

**Ladder text.** Every tier's *substance* was confirmed present in the `rule` by reading each rule in
full. Mechanically, however, 46 of the `factors[].ladder` `when` / `value` / `method` strings are
**paraphrases** rather than verbatim rule substrings (e.g. `parts_entries_met` tier 1 renders the
rule's "The parts met are every parts entry booked on the job inside the window read where two or more
parts entries stand on the job in that window and..." as "every parts entry booked on the job inside
the window read is taken"). Recorded as observation **O-01**: the correspondence holds in substance
but cannot be established by text match, so the "each tier is a sentence of the rule" relation rests on
manual reading alone.

### action_binding_and_uuids

- **Unique action binding.** Eight policies, eight distinct `target_tool` values, eight distinct
  `computes`/tool pairs. No `(target_tool, computes)` pair is claimed twice. PASS.
- **Docstrings.** No docstring names another tool (checked by substring against all eight tool names:
  zero hits). No docstring states an action's position in a sequence. The regex sweep for ordering
  words returned `first` in four docstrings and `next` in one; every hit was read in context and is
  benign — "the **first** day of the unpaid premium period", "the **first** day of the premium period
  being billed", "applied from the oldest unpaid premium period **first**" (which restates base
  `protection_premium_billing`'s own allocation rule, not a tool order), "on the **next** statement of
  what is owed". PASS.
- **No tool adds a confirmation, review or wait.** Each body is `ctx.make_id` -> `ctx.find` ->
  `ctx.create` -> `ctx.update` -> return. PASS.
- **UUID8s.** `5ae6a6af`, `c5640f60`, `542e239c`, `79e3e314`, `3dd4c03b`, `d5a520f4`, `46d57fef`,
  `2818623b`. Eight distinct values; no shared prefix; no sequence or adjacency; no two differ only in
  a tail; hex characters spread across the full range. Independently generated and frozen. PASS.

### prerequisite_graph

All eight policies fill in `prerequisite` (`[]` on the four roots-of-nothing). Six edges declared:

| blocked policy | `problem` | `kind` | `gate` | `form` | `resolved_by` |
| --- | --- | --- | --- | --- | --- |
| `protection_ext_premium_arrears_settlement` | `protection_ext_premium_late_fee_scale` | value_input | `fees_taken` | state | `bill_premium_late_fee_5ae6a6af` |
| `protection_ext_claim_repair_settlement` | `protection_ext_premium_arrears_settlement` | state_gate | `protection_plans.premium_outstanding` | state | `settle_premium_arrears_c5640f60` |
| `protection_ext_spoilage_allowance` | `protection_ext_claim_repair_settlement` | value_input | `allowance_ceiling` | state | `book_claim_payout_542e239c` |
| `protection_ext_claim_excess_settlement` | `protection_ext_claim_excess_charge` | value_input | `owed_measure` | state | `bill_claim_deductible_d5a520f4` |
| `protection_ext_fleet_invoice_settlement` | `protection_ext_fleet_instalment_billing` | value_input | `invoice_items` | state | `bill_premium_instalment_3dd4c03b` |
| `protection_ext_fleet_invoice_settlement` | `protection_ext_claim_excess_settlement` | state_gate | `protection_events.deductible_amount` | state | `settle_claim_deductible_46d57fef` |

- Every `problem` points at another **extended** policy id in this file; none points at a base policy
  or at itself. PASS.
- The graph is two disjoint chains/trees and is **acyclic**; no cycle is created by any cross-task
  reference. PASS.
- Every `policy_source` is **verbatim locatable in the blocked policy's own `rule`** (checked by
  whitespace-normalised substring: 6/6) and **absent from the depended-on policy's `rule`** (0/6
  present). PASS.
- `form` is `state` on all six; no `fallback_reason` is present and none is required. The state form's
  priority is honoured everywhere and there is no action-form edge to test. PASS.
- `resolved_by` is the depended-on policy's `target_tool` in all six cases. PASS.
- `kind` vs `gate`: each of the four `value_input` edges names a binding that genuinely exists in the
  blocked policy's `compute` (`fees_taken`, `allowance_ceiling`, `owed_measure`, `invoice_items` —
  all four confirmed present). The two `state_gate` edges name a *field path* rather than an
  eligibility id; see observations **O-02** and finding **F-08**.
- No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears in
  any `prerequisite` field. PASS.

### prerequisite_sentences

The four-point test, edge by edge.

1. **`arrears_settlement` <- `late_fee_scale`** — "The amount the customer settles is fixed only after
   every fee owed for a period that has run past grace stands billed on the plan."
   Ordering connective **"only after"** ✓. Waited-on thing is a record-visible state ("every fee owed …
   stands billed on the plan") with no performer or tool ✓. No tool name, policy id, snake_case token
   or row id ✓. Strength matches the edge's `condition` ✓. **One write brings it about:** only
   `bill_premium_late_fee_5ae6a6af` creates a `protection_premium_charge` with
   `premium_kind="late_fee"`; `bill_premium_instalment_3dd4c03b` writes `premium_kind="monthly_instalment"`.
   Derivation in one reading: sentence -> "fees standing on the plan" -> the plan's premium history
   shows no `late_fee` row -> the policy whose own rule books a late fee is
   `protection_ext_premium_late_fee_scale` ("A late fee falls due on a plan whose premium instalments
   have run past grace") -> its write. PASS.
2. **`claim_repair_settlement` <- `arrears_settlement`** — "The amount the plan pays on the claim is
   released only once no premium period covering the day the failure happened stands unpaid on the
   plan." Connective **"only once"** ✓; state form ✓; no tool/id/snake_case ✓. **Two writes of this
   difficulty could bring the state about** — see observation **O-03**; the hop is resolvable, but only
   by reading the two depended-on policies' opening clauses, not from the sentence and the records
   alone.
3. **`spoilage_allowance` <- `claim_repair_settlement`** — "The allowance for spoiled food is worked
   out only after every cost the claim has already been approved for stands booked as paid against the
   plan's cover." Connective **"only after"** ✓; state form ✓. Two tools write
   `event_type="protection_claim_payout"` (`book_claim_payout_542e239c` and
   `book_spoilage_allowance_79e3e314`), but the second is the blocked problem itself and hard-codes
   `settlement_basis="reimbursement"`, whereas the sentence speaks of "the cost the claim has already
   been approved for" and the approval on record carries `settlement_basis="repair"`. Unique. PASS.
4. **`claim_excess_settlement` <- `claim_excess_charge`** — "What the account settles on a claim excess
   is fixed only after that excess stands billed on the plan." Connective ✓; state form ✓; only
   `bill_claim_deductible_d5a520f4` writes `protection_deductible_charge`. Unique. PASS.
5. **`fleet_invoice_settlement` <- `fleet_instalment_billing`** — "The amount the account settles is
   fixed only after every premium period the plan has reached stands billed on it." Connective ✓;
   state form ✓; only `bill_premium_instalment_3dd4c03b` writes a `monthly_instalment` charge. Unique.
   PASS.
6. **`fleet_invoice_settlement` <- `claim_excess_settlement`** — "The premium on the plan is taken only
   once a payment stands received against every claim excess billed on it." Connective ✓; state form ✓;
   only `settle_claim_deductible_46d57fef` writes `protection_deductible_payment`. The sentence passes
   the four-point test **as a sentence**, but the state it names is **universally quantified over a set
   that is empty at task 1's opening**, so it identifies no blocker. That is a problem-tree defect, not
   a sentence-form defect; it is raised as **F-08** here and demonstrated against task 1's world in
   `1.md`.

**No rule carries a second wording of its own dependency**, no other problem's id or tool name, and no
depended-on rule restates the blocked rule's sentence (0/6 present in the depended-on rule). **One
base rule sentence states a cross-problem order**: see **F-06**.

### override_declarations

Sentence-by-sentence sweep of each extended policy against every entry of its `base_policy_refs`.
All six `superseded_clause` strings are **verbatim locatable in the named base policy's `rule`**, and
all six `replaced_by` strings are **verbatim present in the extended policy's own `rule`** (6/6 each).
The declarations are therefore well formed. What follows is whether each is a *genuine* retirement and
whether any *undeclared* conflict remains.

**The six declared overwrites.**

| # | extended policy | base policy | verdict |
| --- | --- | --- | --- |
| 1 | `late_fee_scale` | `protection_premium_delinquency` | genuine conflict, but **under-scoped** — see **F-01** |
| 2 | `claim_repair_settlement` | `protection_excl_duplicate_coverage` (warranty bar) | **genuine**, load-bearing |
| 3 | `claim_repair_settlement` | `protection_excl_duplicate_coverage` (asking clause) | genuine but leaves an orphan — see **F-04** |
| 4 | `claim_repair_settlement` | `protection_claim_settlement` (cap clause) | **not a conflict at all** — see **F-02** |
| 5 | `claim_excess_charge` | `protection_claim_settlement` (deductible billed once) | genuine, but **under-scoped** — see **F-03** |
| 6 | `fleet_instalment_billing` | `protection_premium_billing` (instalment clause) | genuine conflict, but **under-scoped** — see **F-01** |

**On the instantiating agent's second claim.** Overwrite #2 retires
"A ShieldCare plan and a manufacturer's warranty are never both settled for the same repair, and a plan
does not pay while the manufacturer's warranty on that item is still running unless the peril is one
the manufacturer excludes." This is a **genuine, load-bearing retirement, not a convenience**: the
base clause is an absolute bar on paying, the replacement lets the plan pay the non-warranty share, and
the two reach different conclusions in the same situation. Task 0's covered item was bought
2025-11-08 and the repair entries are dated 2026-09-10 — inside the twelve months a manufacturer's
warranty ordinarily runs on a major appliance, on a peril (`mechanical_failure`) such a warranty
ordinarily covers — so under the base clause the plan would pay **nothing** and under the extended rule
it pays the computed share. The retirement carries real weight. The base eligibility entry
`no_overlapping_warranty_settlement` (kind `caller_fact`) carries that exact clause as its `condition`,
so naming the clause retires the eligibility with it. **Confirmed.**
Overwrite #4, by contrast, is exactly the convenience the agent suspected it might have written: see
**F-02**.

**Undeclared conflicts found.** Two base provisions bearing on a scored quantity are not named in any
`overwrite` and are not implemented in any `compute`: the **aggregate payout cap** (**F-09**) and the
**deductible waiver on repair** (**F-03**). Both are recorded with the situation in which they bite.

**Base provisions confirmed inherited in full and not weakened** (checked sentence by sentence and found
either untouched by extended or consistent with it): `protection_premium_billing`'s oldest-period-first
allocation and surplus rule; `protection_premium_delinquency`'s "the premium already owed stays owed"
and "settles everything outstanding on or before the day of termination leaves the plan in force";
`protection_claim_settlement`'s per-claim-limit and coverage-remaining caps, its default settlement
method, and "the food spoilage allowance … paid outside the per-claim limit but inside the term
coverage limit"; `protection_coverage_ledger`'s "coverage remaining is the credited coverage less the
payouts booked"; `protection_combo_membership_interaction`'s "a business fleet plan takes its pricing
from the contract price book and no membership discount applies to it at all" (respected —
`fleet_instalment_billing` and `fleet_invoice_settlement` read no membership discount, and Fleet's
`membership_discount_applies` is `false`); `protection_claim_intake`'s report window;
`protection_claim_adjudication`'s repair-attempts rule.

### factor_ladders

Structure only. Whether each factor bears weight is a fact about one world and lives in that task's
`factor_weight` section.

| policy | factors | `parameter` | `method` | cross-difficulty (categories) |
| --- | --- | --- | --- | --- |
| `late_fee_scale` | 4 | 3 | 1 | 1 (`membership`) |
| `premium_arrears_settlement` | 5 | 3 | 2 | 1 (`membership`) |
| `claim_repair_settlement` | 5 | 3 | 2 | 3 (`service`) |
| `spoilage_allowance` | 5 | 3 | 2 | 1 (`service`) |
| `fleet_instalment_billing` | 4 | 3 | 1 | 2 (`credit`, `orders`) |
| `claim_excess_charge` | 6 | 4 | 2 | 1 (`service`) |
| `claim_excess_settlement` | 5 | 3 | 2 | 2 (`credit`) |
| `fleet_invoice_settlement` | 5 | 3 | 2 | 3 (`credit`) |

Every policy declares **4 to 6 factors, at least 2 `parameter` and at least 1 `method`**. PASS.
Every task's four policies together carry at least one `cross_difficulty` factor and at least one
multi-source factor (per-task confirmation in the task files). PASS.

- **`decides` is an input, never `result`**, on all 39 factors. PASS.
- **Binding sets are pairwise disjoint within each policy** on all eight policies. PASS.
- **Every ladder has exactly three pairwise-disjoint tiers, the fall-through counted**, and every
  fall-through tier is exactly the policy's `baseline` value for that binding (39/39 checked against
  `baseline.params` and `baseline.rule`). PASS.
- **No two tiers of one ladder select the same value or method** — all 39 ladders checked, including
  the cases where a collision depends on a variant parameter:
  `fee_per_unpaid_period` (4 / 8 / `premium_late_fee_usd`) is safe because
  `premium_late_fee_usd` is 9.0, 9.0, 15.0, 12.0 and 25.0 on the five instalment-capable variants and
  never 4 or 8 (Essential's 0.0 is unreachable: Essential is `single payment only`);
  `loading_window_counted` (reinstatement-anchored / 12 months / `plan_term_months`) is safe because no
  variant has `plan_term_months == 12`. PASS, with one conditional collapse recorded as **O-04**.
- **Label honesty.** Every `method` tier changes an algorithm — a window (`repairer_bill_window`,
  `trading_record_window`, `loading_window_counted`), an anchor (`outage_clock`,
  `billing_delay_clock`), a counting rule (`periods_counted_toward_fee`), a candidate selection
  (`parts_entries_met`, `invoice_entries_carried`, `advance_period_pricing`, `excess_owed_measure`,
  `arrears_measurement_basis`, `fees_taken_with_settlement`, `allowance_ceiling_basis`) or a scaling of
  the base figure (`base_excess_basis`). Every `parameter` tier substitutes a number into a fixed
  formula. No `method` tier names a computation rule the charter does not state. PASS.
- **Ladder realism.** Two ladders state a condition or produce an outcome that the line of business
  does not: see **F-10** and **F-11**. All other ladders' conditions genuinely divide the customers
  who reach the write and all other outcomes are ones such a business would publish.

### findings

Ordered by how much of the artefact they bear on. "Bears on" names the tasks whose files carry the
demonstration against a world.

---

**F-01 — `SOURCE-POLICY RED`. Two overwrites retire the only base clause that fixes the *period* of a
premium charge, and replace only its *amount*, leaving scored date arguments with no policy ground.**
*Bears on: task 0 (demonstrated in `0.md`), task 1 (observation only in `1.md`).*

*Symptom.* `bill_premium_late_fee_5ae6a6af` takes a scored `period_start`, and
`bill_premium_instalment_3dd4c03b` takes scored `period_start` and `period_end`. After the two
overwrites below, no sentence of the charter — base or extended — says which period either entry is
stamped with.

*Root cause.* Each overwrite names a base clause that carries **two** provisions (an amount and a
period/day) and supplies a `replaced_by` that speaks only to the amount.

*Evidence.*
`protection_ext_premium_late_fee_scale.overwrite[0]`:
```
base_policy: protection_premium_delinquency
superseded_clause: The plan's late fee is billed once when grace runs out
replaced_by: The fee billed is the fee for each unpaid period multiplied by the periods counted and
  by the rate at which it is billed, less anything written off, taken to the cent and never below
  nothing.
```
The superseded clause is the only place in the charter that ties a late fee to a period ("**when grace
runs out**", i.e. the period whose grace has just run). The replacement fixes an amount across
*several* periods and says nothing about which period the entry belongs to. The extended `rule`
likewise never mentions the fee entry's period. Meanwhile the tool's contract demands one:
```
period_start: Fixed-format class — the first day of the unpaid premium period the fee is billed
    against, written as YYYY-MM-DD …; there is no empty value.
```
`protection_ext_fleet_instalment_billing.overwrite[0]`:
```
base_policy: protection_premium_billing
superseded_clause: an instalment plan bills the monthly premium of the plan on the same day of each month
replaced_by: The instalment billed is the plan's monthly premium adjusted once by the loadings and
  discounts combined into a single rate, taken to the cent and never below nothing.
```
The superseded clause is the charter's only statement of the instalment billing day; the remainder of
that base sentence ("with a month-end day falling back to the last day of a shorter month") hangs off
the retired clause and is left governing nothing. The replacement speaks only to the amount.

*Demonstrated consequence.* Task 0: the plan has **four** unpaid premium periods (2026-06-08,
2026-07-08, 2026-08-08, 2026-09-08) of which **three** have run past the plan's 30 grace days and are
the periods the fee is computed over; the charter contains no sentence selecting one of them for
`period_start`. Two defensible readings give two different scored arguments — 2026-06-08 (the oldest
unpaid period, by analogy with base's payment-allocation rule, which however governs *payments*, not
fees) and 2026-08-08 (the most recent period whose grace has run, which is what the retired base clause
"billed once when grace runs out" pointed at). Task 1: the same gap exists for
`bill_premium_instalment`'s `period_start`/`period_end`, but exactly one period has been reached and
not billed, so the records pin it down and there is no second answer; recorded there as an observation.

*Affected artefact and location.* `protection.extended.yaml`,
`extended_policies[protection_ext_premium_late_fee_scale].overwrite[0]` and
`extended_policies[protection_ext_fleet_instalment_billing].overwrite[0]`; `task_tools.py`,
`bill_premium_late_fee_5ae6a6af(period_start=…)` and
`bill_premium_instalment_3dd4c03b(period_start=…, period_end=…)`.

*Relation to previous revisions.* First revision; no prior audit of this difficulty exists.

---

**F-02 — observation. One of the six `overwrite` entries declares a conflict that does not exist.**
*Bears on: task 0.*

*Symptom.* `protection_ext_claim_repair_settlement.overwrite[2]` retires a base clause and replaces it
with a sentence of the same meaning.

*Evidence.*
```
base_policy: protection_claim_settlement
superseded_clause: where the approved cost is above either cap the plan pays the cap and the customer
  pays the rest, and the claim is not split into two to get round the cap
replaced_by: Where the covered bill is above that ceiling the plan pays the ceiling and the customer
  meets the rest, and the claim is not split in two to get round it.
```
"the approved cost" becomes "the covered bill" and "either cap" becomes "that ceiling", but the
cap behaviour is word-for-word the same, and the extended's `claim_ceiling = MN(P('per_claim_limit_usd'),
cover_left)` is exactly base's "capped at the plan's per-claim limit, and further capped at the
coverage remaining on the plan".

*Consequence.* None demonstrable: the merged semantics are identical, so no second answer arises. This
is recorded as an observation rather than a red light, and specifically as the answer to the
instantiating agent's own question — **this is the one declaration among the six that is a convenience
rather than a retirement**. It costs nothing in either world but it inflates the apparent override
count and it retires a base sentence that was never in conflict.

*Affected artefact.* `protection.extended.yaml`,
`extended_policies[protection_ext_claim_repair_settlement].overwrite[2]`.

---

**F-03 — `SOURCE-POLICY RED` (undeclared override, dormant in both worlds). The deductible-waiver
clause survives the excess-charge overwrite un-retired, and neither the extended rule nor its compute
carries a waiver branch.**
*Bears on: task 1 (demonstrated as dormant in `1.md`).*

*Symptom.* `protection_ext_claim_excess_charge` retires only the first half of a base sentence.

*Evidence.* Base `protection_claim_settlement.rule`:
> "The plan's deductible is billed once per approved claim, **and it is waived where the plan waives it
> on a claim settled by repair**; a deductible is never billed on a denied or withdrawn claim."

`protection_ext_claim_excess_charge.overwrite[0].superseded_clause` is only
`"The plan's deductible is billed once per approved claim"`. The waiver half is not named, so it is
inherited in full. The extended `rule` never mentions a waiver and its `compute` has no waiver branch:
`result: MX(0.0, RND(base_excess + frequency_loading - prompt_report_reduction - care_allowance + age_adjustment, 2))`.

*Demonstrated consequence.* `deductible_waiver_on_repair` is `true` on four of the six variants
(Essential, Total Device Protection, Home Theatre Premium, Business Fleet Protection). On any of those
four, on a claim whose decision carries `settlement_basis: repair`, the base clause gives **0** and the
extended formula gives a positive figure — two defensible answers on the scored `deductible_amount`.
In task 1 the conflict is dormant because the claim on record (`SC-2026-70431`, decision 2026-08-12)
carries `settlement_basis: replacement`, so the waiver does not engage; the figures are in `1.md`. The
defect is in the charter, not in task 1's world, and it is recorded here because the KB renders base and
extended together.

*Affected artefact.* `protection.extended.yaml`,
`extended_policies[protection_ext_claim_excess_charge].overwrite[0]`, and that policy's `rule` and
`compute`.

---

**F-04 — observation. The extended rule promises a warranty exclusion that no compute binding applies,
and the base clause supplying the only route to the fact it needs was retired alongside it.**
*Bears on: task 0.*

*Symptom.* Two normative sentences of `protection_ext_claim_repair_settlement.rule` have no
`compute_basis` key and no binding.

*Evidence.* The rule's closing sentence —
> "The plan meets no entry the repairer has booked for work the manufacturer's warranty on the covered
> item was still running to meet, and the entries the plan meets are read from the repairer's own
> ledger on the job."

— is the `replaced_by` of overwrites #2 and #3, yet it appears in no `compute_basis` key (the full key
list runs `diagnoses_recorded … result` and contains nothing for it), and `compute` sums every
`service_labour_charge`, `service_parts_charge` and `service_fee_charge` in the window without
consulting any warranty field. Separately, overwrite #3 retires
`"the customer is asked what has already been paid rather than being paid twice"` while leaving the
first half of that base sentence — "Where the item also carries cover from a card issuer or a household
insurer, the retailer settles only the part of the loss those have not met" — in force. The reduction
therefore stands as policy while its only stated means of discovery has been withdrawn, and no compute
binding implements it either.

*Consequence.* Not demonstrable in task 0: the job record carries `warranty_work_flag: false`, so no
entry is excluded on either reading, and the persona answers the other-cover question directly ("Asked
whether anyone else has paid her for the spoiled food, a household policy or the like, she says no,
nobody has and she has claimed nowhere else"). The sentences are therefore inert here rather than
contradictory. They would bite on a world where the repairer had booked a warranty line or where a
card issuer had met part of the loss. Recorded as an observation.

*Affected artefact.* `protection.extended.yaml`,
`extended_policies[protection_ext_claim_repair_settlement].rule` / `compute_basis` / `compute` /
`overwrite[0..1]`.

---

**F-05 — observation. `claim_excess_settlement`'s "delay in billing" states an opening anchor but no
closing anchor; `compute` supplies `NOW`.**
*Bears on: task 1.*

*Evidence.* The rule says only
> "The delay in billing is counted **from** the day the amount settled on the claim was paid out … it is
> counted from the day the claim was decided … and for every other claim the delay in billing is
> counted from the day the loss was reported."

and never says what it is counted *to*. `compute` closes it at `NOW`:
`billing_delay_days: DAYS(payout_date, NOW) if … else (DAYS(decision_date, NOW) if … else DAYS(loss_report_date, NOW))`.

*Consequence.* Not demonstrable: because this policy's own prerequisite requires the excess to be
billed first, and that write happens at `frozen_time`, `NOW` *is* the billing day, so "the delay in
billing" and `DAYS(anchor, NOW)` coincide. Recorded as an observation because a reader must infer the
closing anchor rather than read it.

---

**F-06 — observation. A base rule sentence states a cross-problem order that grounds a declared
edge.**
*Bears on: tasks 0 and 1.*

*Evidence.* Base `protection_premium_delinquency.rule` contains
> "A claim whose incident day falls inside an unpaid period is not paid until that period is settled,
> and a claim whose incident day falls after termination is not paid at all."

This is a cross-problem order (a payout waits on a premium settlement) stated in a **base** rule. Under
the audit's own rule such a sentence may not ground an edge; here it does not have to, because the
blocked extended policy carries its own prerequisite sentence — "The amount the plan pays on the claim
is released only once no premium period covering the day the failure happened stands unpaid on the
plan." The base sentence is therefore a second, redundant statement of the same dependency rather than
its only source, and is recorded as an observation rather than a red light.

Separately, base `protection_premium_delinquency` carries the only clock that bears on an extended
write subject: "The plan's late fee is billed once **when grace runs out**", with grace counted as
calendar days from the first day of the unpaid period, day zero, inclusive. The arithmetic showing the
clock is satisfied in task 0 (oldest unpaid period 2026-06-08, `premium_grace_days` 30, 99 days elapsed
at `frozen_time`) is in `0.md`. Task 1 books no late fee.

---

**F-07 — observation. The extended `rule` treats "grace has fully run" as a proxy that does not agree
with base's counting rule at the boundary.**
*Bears on: task 0.*

*Evidence.* Base `protection_premium_delinquency.temporal_basis` counts grace as calendar days from
the period's first day, **day zero, boundary inclusive**, so grace has run in full when
`days_elapsed >= premium_grace_days`. `protection_ext_premium_late_fee_scale.compute` treats
`days_since_newest_period <= P('premium_grace_days')` as "still inside the plan's grace days", so at
exactly `days_elapsed == premium_grace_days` the base rule says grace has run while the extended rule
says the period is still inside it. Separately, the extended rule defines "the unpaid periods whose
grace has fully run" structurally as "the unpaid periods less the most recent one" rather than by any
day count.

*Consequence.* Not demonstrable in either world: in task 0 `days_since_newest_period` is 7 against a
grace of 30, nowhere near the boundary. Recorded as an observation.

---

**F-08 — `SOURCE-CHAIN RED`. The `fleet_invoice_settlement <- claim_excess_settlement` edge is
universally quantified over a set that is empty at the opening, so it gates nothing.**
*Bears on: task 1 — demonstrated in full against task 1's world in `1.md`.*

*Symptom.* The declared `condition` of the edge is already true at `frozen_time`.

*Evidence.* `policy_source`:
> "The premium on the plan is taken only once a payment stands received against **every claim excess
> billed on it**."

and the declared `condition`:
> "the plan's history carries an excess payment entry against every excess billed on it, and the
> outstanding excess figure on the plan has fallen by that payment".

Both are universally quantified over the excesses billed on the plan. Task 1's world contains **zero**
rows with `event_type == "protection_deductible_charge"` among 49 `protection_events`, and
`protection_plans[a4c4c25e-dec2-4e4a-a8bf-92e8f129e72d].deductible_outstanding == 0.0`. The universal
is therefore vacuously satisfied, and the second conjunct ("the outstanding excess figure … has fallen
by that payment") cannot be evaluated at all on a figure of 0.0 that has nothing to fall from.

*Demonstrated consequence.* A reader applying the root policy's own rule to the records concludes that
nothing on the excess side blocks taking the premium, and proceeds straight to
`bill_premium_instalment` -> `settle_fleet_invoice`. Two of the three declared prerequisite problems
(`claim_excess_charge` and `claim_excess_settlement`, which hangs off this edge) drop out of the tree,
which falls from four problems to two. The root policy's rule contains no other sentence making the
excess a blocker. The full demonstration, including what each of the two readings pays, is in `1.md`.

*Root cause.* The sentence presupposes that the excesses have been billed and then requires them paid;
it does not require that an excess which has *fallen due but never been billed* be billed. The problem
the task actually wants discovered — that an approved theft claim carries an unbilled excess — is
reachable only from `protection_ext_claim_excess_charge`'s own `trigger: state_due`, which is a
separate obligation the root's prerequisite sentence does not point at.

*Affected artefact.* `protection.extended.yaml`,
`extended_policies[protection_ext_fleet_invoice_settlement].prerequisite[1]` and the corresponding
sentence of that policy's `rule`.

---

**F-09 — observation. The aggregate payout cap is dropped by both payout policies with no `overwrite`
declaring it.**
*Bears on: tasks 0 and 1.*

*Evidence.* `protection_agg_payout_cap` is listed in `base_policy_refs` of both
`protection_ext_claim_repair_settlement` and `protection_ext_spoilage_allowance`, and its rule says
> "the rolling twelve-month total read from protection_msr_payouts_12m is compared with the aggregate
> cap of the plan the claim sits on, and the payout is cut back to whatever room the cap leaves … The
> aggregate cap is applied after the per-claim limit and the coverage remaining, and never before them."

Neither policy's `overwrite` names any clause of `protection_agg_payout_cap`, and neither `compute`
contains any binding reading `aggregate_payout_cap_per_12m_usd` or a twelve-month payout total for the
cap. This is a dropped branch: base declares a cut-back the extended selector never produces.

*Consequence.* Not demonstrable in either world. Task 0: the aggregate cap on
`ShieldCare Major Appliance Extended Service` is 12000.00 and payouts inside the rolling twelve months
come to 5030.00 (1180.00 + 3500.00 + 350.00), leaving 6970.00 of room against writes of 1248.90 and
206.10 — the cap never binds, so base and extended give the same number. Task 1 books no payout.
Recorded as an observation; it would become a red light on any world where the rolling total
approached the cap.

---

**F-10 — `SOURCE-FACTOR RED` (ladder realism). `spoilage_allowance.outage_share_met` tier 1 carries a
conjunct that is true of every plan on which this write can pay anything.**
*Bears on: task 0.*

*Evidence.* Tier 1 reads
> "the appliance stood out of use for more than ten days **and the plan carries attendance at the
> address**"

implemented as `onsite_included == True`. But `food_spoilage_cover_usd` is **0.0 on five of the six
variants** and 350.0 only on `ShieldCare Major Appliance Extended Service`, and the allowance is
`MN(P('food_spoilage_cover_usd'), …)` throughout, so on any other variant the ceiling is 0 and the
whole write pays nothing. On the one variant where the write is not vacuous,
`on_site_service_included` is `true`.

*Demonstrated consequence.* The conjunct never divides the customers who reach this write: it restates
the policy's own scope. Tier 1 therefore turns on "more than ten days" alone, and a reader who ignores
the attendance conjunct entirely scores identically on every world this policy can be applied to.
(Contrast `claim_repair_settlement.attendance_share_met`, whose identical conjunct does divide, because
`on_site_service_included` is true on three variants and false on three.)

*Affected artefact.* `protection.extended.yaml`,
`extended_policies[protection_ext_spoilage_allowance].factors[outage_share_met].ladder[0]` and the
corresponding rule sentence.

---

**F-11 — `SOURCE-FACTOR RED` (ladder realism). `claim_excess_charge.prompt_report_reduction_allowed`
publishes a treatment that penalises the faster reporter.**
*Bears on: task 1.*

*Evidence.* The rule states
> "The reduction for a prompt report is fifty dollars where the loss was reported inside three days of
> it happening **and a police report stands received on the claim**; it is twenty-two dollars and fifty
> cents where the loss was reported more than three days but no more than seven days after it happened;
> and for every other claim no reduction for a prompt report is allowed."

Tier 1 adds a police-report conjunct that tier 2 does not carry, and tier 2's condition is bounded
below by "more than three days".

*Demonstrated consequence.* A customer who reports a non-theft loss on **day 2** satisfies neither
tier 1 (no police report — one is required only for theft, per base
`protection_claim_adjudication`: "A theft claim additionally needs a police report on file") nor tier 2
(2 is not "more than three days"), and falls through to **no reduction**. The same customer reporting
the same loss on **day 5** receives **$22.50**. Reporting the loss three days sooner costs the customer
$22.50 on their excess. No insurer publishes a promptness discount that pays less for a prompter
report; the ladder is not one that line of business holds. The defect is in the ladder's structure, so
it stands whatever tier a given world lands on — task 1's own claim reports on day 6 with a police
report on file and lands on tier 2, so its scored value is not itself wrong.

*Affected artefact.* `protection.extended.yaml`,
`extended_policies[protection_ext_claim_excess_charge].factors[prompt_report_reduction_allowed]` and
the corresponding rule sentence.

---

**F-12 — observation. The seed of task 0 contradicts `db_schema.json`'s declared identity for
`premium_outstanding`, and one factor's ladder exists to exploit that contradiction.**
*Bears on: task 0.*

*Evidence.* `blueprint/db_schema.json`:
```
"premium_outstanding": {"type": "fixed_format", "format": "USD, 2 decimal places",
  "meaning": "premium billed and not yet settled, identically the sum of the premium_receivable
              account deltas"}
```
The charter's `events` section puts `protection_premium_charge` on `premium_receivable` `direction: in`
and `protection_premium_payment` on `premium_receivable` `direction: out`, so the declared identity is
`SUM(charges) - SUM(payments)`. In task 0 that is `142.89 - 90.93 = 51.96`, while
`protection_plans[d9cb7845-…].premium_outstanding` is `38.97` — short by exactly one 12.99 instalment
(the 2026-09-08 charge). `coverage_remaining` (1470.00) and `deductible_outstanding` (0.00) both
satisfy their own identities, so the divergence is deliberate and confined to one field.

*Consequence.* **Not a second answer.** `protection_ext_premium_arrears_settlement`'s
`arrears_measurement_basis` ladder settles authority explicitly: tier 1 fires "where the premium
entries booked on the plan add up to more than the outstanding premium recorded on it and the plan
stands active", and both quantities are readable by the agent through `find_protection_events` and
`find_protection_plans`. **The instantiating agent's first claim is therefore upheld: the policy alone
decides which figure is authoritative, and the task has one answer.** What is recorded here is the
narrower point that the world breaks an invariant the scenario constitution states as an identity, and
that tier 1 of this ladder is reachable *only* on a world that breaks it. Recorded as an observation.

---

**O-01 — observation.** 46 `factors[].ladder` strings are paraphrases rather than verbatim rule
sentences (see `rule_compute_equivalence`). Substance verified by hand in all 46 cases.

**O-02 — observation.** The two `state_gate` edges name a *field path* (`protection_plans.premium_outstanding`,
`protection_events.deductible_amount`) as `gate`, whereas the four `value_input` edges name a compute
binding. Neither field path is the id of a base `eligibility` entry — the gate each edge relies on is
created by the blocked policy's own rule sentence, not by an inherited eligibility. This is coherent
but the `gate` field then carries a different kind of referent on the two edge kinds. On the
`claim_repair_settlement` edge the named field is also the one `F-12` shows to be stale, and the field
the declared `condition` speaks of is the premium *history*, not that field.

**O-03 — observation.** For the `claim_repair_settlement <- arrears_settlement` edge, **two** writes of
this difficulty produce the waited-on state: `settle_premium_arrears_c5640f60` and
`settle_fleet_invoice_2818623b` both create `event_type="protection_premium_payment"` and lower
`premium_outstanding`. The hop is resolvable — the two depended-on policies' opening clauses describe
different requests ("Where the customer asks to bring the premium on a plan back into order" vs "Where
a customer asks to settle the premium invoice standing on a plan held on instalments") — but not from
the prerequisite sentence and the records alone. The cost of resolving it wrongly on task 0's world is
quantified in `0.md`.

**O-04 — observation.** `premium_arrears_settlement.advance_period_discount`'s three tiers are the
membership tier's plan discount, half that discount, and no discount. On a profile holding
`Circle Free Membership` (`protection_plan_discount_pct: 0`) all three tiers select 0 and the ladder
collapses to a single outcome. Not reachable in either world audited here (task 0 holds
`Circle Plus Annual`, 5%; task 1 holds no membership).

**O-05 — observation.** Several cross-category reads are scoped to the **customer** rather than to the
job or holding the rule names. `check_compute.build_env._xrows` scopes `XSUM`/`XCOUNT`/`XMAX`/`XLATEST`
by `customer_id` (or by the category holding's primary key) and `CFIELD`/`CPARAM` return `hs[0]` — the
first matching holding in dict order. So `XCOUNT('service','service_events', …)` for "a diagnosis
stands recorded **on the job for the covered item**" counts diagnostics across every one of the
customer's service jobs, and `CFIELD('service','completed_date', status='completed')` for "the day the
repairer completed the work **on the covered item**" returns whichever completed agreement the seed
happens to list first. Task 0 seeds two completed service agreements; the reading and the rule coincide
there only because the fridge job is listed first and is the only one carrying a diagnosis (figures in
`0.md`). Likewise `largest_part: XMAX(…)` and `latest_part: XLATEST(…)` carry **no `within_months`**
while the rule scopes the covered bill to "the window read", and
`police_report_on_file: COUNT('protection_claim_intakes', documents_supplied='police_report')` uses an
exact enum match that would miss an intake recorded as `both`, and is not scoped to the claim
reference. None of these produces a divergent number on either world audited; all are recorded so that
a seed change cannot silently turn them into red lights.

**O-06 — observation.** Task 1's `protection_coverage_reinstate` row credits `640.00`, whereas base
`protection_coverage_ledger` states that "on the plans that reinstate, **the full term limit** is
credited again at each coverage anniversary and the unused remainder of the previous year is not
carried forward" — for `ShieldCare Business Fleet Protection` that is 45000.00. The seed instead puts
back exactly the prior payout. The world is arranged so that both readings agree on the cover left
(45640.00 − 3240.00 = 42400.00 and 45000.00 − 2600.00 = 42400.00), and no computation in task 1's tree
reads `cover_left` at all, so nothing is demonstrable. Recorded because the credited total (45640.00)
exceeds the plan's term limit, which base's "Coverage is never credited above the plan's term limit by
way of a correction" is written to prevent.

**O-07 — observation.** `fleet_invoice_settlement.invoice_raising_charge` charges $15.00 (or $7.50)
"where no premium payment stands on the plan inside the last month". Because this policy's own
prerequisite requires the newest period to be billed immediately before the write, and because a
monthly plan settled on its billing day has its most recent payment one full cycle back, the condition
holds of essentially every customer who reaches this write — task 1's customer has paid **19 of 19**
instalments on the day each was billed and still attracts the charge. It is not *structurally*
impossible for a payment to fall inside the last month (a customer paying twice in a month would), so
this is recorded as an observation rather than as a sibling of F-10.

## closing_checklist

*Written after both reveals. Everything above this heading is pre-reveal and is left untouched.*

**This difficulty does not close out.** Step 4's checklist is reached only when all M tasks
carry a `source_gt_comparison` with a PASS on all four relationships. Task 0 and task 1 each carry at
least one red light (see `0.md` and `1.md`), so the difficulty remains open and the instantiation-stage
gates have not been re-run on a final form.

Step 4's checklist is reached only when all M tasks carry a `source_gt_comparison` with a PASS on all
four relationships. Both tasks carry at least one red light, so the difficulty remains open and the
instantiation-stage gates have **not** been re-run on a final form.

Where the difficulty stands against Step 4's list:

| Step 4 item | status |
| --- | --- |
| per-task audit files one-to-one with the tasks, `_difficulty.md` alongside | **met** — `0.md`, `1.md`, `_difficulty.md`; first revision, no older revisions to preserve |
| every comparison section carries a PASS | **not met** — `0.md`: SOURCE-POLICY/SOURCE-TASK + SOURCE-FACTOR; `1.md`: SOURCE-CHAIN + SOURCE-TASK on the write set |
| extended policies fully covered, M scopes pairwise disjoint over the whole tree | **met** — `charter_scope` confirms the partition I derived blind: 4 + 4 over 8, disjoint |
| task tools and GT closed | **met** — each policy computes one argument of one call; `required_documents` = `charter_scope.extended_policies` in both tasks |
| each task tool an independently generated, frozen uuid8 | **met** — see `action_binding_and_uuids` |
| 1–3 prerequisite problems, ≥ max(n−1,1) `value_input`, ≥ 1 `owner=user`, acyclic; whole-difficulty DAG | **met as declared** (3 / 2 / 1 / acyclic in each task, and the six edges form two disjoint acyclic chains with no cross-task reference). **Not met as the policy supports it in task 1**, where one edge is vacuous and the tree it actually supports is two problems — finding **F-08** |
| self-sufficient baseline + 4–6 factors (2 `parameter`, 1 `method`; ≥ 1 multi-source, ≥ 1 cross-difficulty per task), every ladder ≥ 3 tiers stated in full, tiers distinct in outcome, conditions and outcomes ones the business holds, every factor bearing weight against an honest baseline, baseline alone definite and ≠ gold | **met except ladder realism** — 39 factors all in bounds, all labels honest, all tiers distinct, all 39 bearing weight, all 8 whole-baseline figures definite and ≠ gold. Two ladders fail the realism test: **F-10** and **F-11** |
| instantiation-stage gates re-run on the final form | **not done** — the form is not final |

**Post-reveal note on the audit's own agreement with GT.** The blind derivations were compared against the
revealed fields figure by figure: **8 of 8** scored computation results, **8 of 8** `baseline_result`
figures, **39 of 39** `factor_sensitivity` figures, **21 of 21** scored tool arguments, and both
`prerequisite_closure.resolution_order` lists agree with the frozen sections — 78 independent quantities,
zero disagreements. That agreement is recorded because it is what makes the red lights above findings
about the artefacts rather than about a mis-derivation: **the numbers are right, and the defects are in
what the policy entails, not in what it computes.** The two structural disagreements are (i) task 1's
derivable tree has two problems where three are declared (**F-08**), and (ii) two scored date arguments
have no policy ground (**F-01**), one of which is genuinely ambiguous on task 0's world.

**On the three points the instantiating agent flagged.** All three were tested independently and the
conclusions are recorded where their evidence lives:

1. *The stale cached premium-outstanding field.* **Upheld — the policy alone settles authority and the
   task has one answer**, through `protection_ext_premium_arrears_settlement`'s
   `arrears_measurement_basis` tier 1, whose condition compares two quantities the agent can read
   (`0.md`, T0-05). The residue is that the world breaks `db_schema.json`'s declared identity for the
   field and that tier 1 is reachable only on a world that breaks it (**F-12**).
2. *The six `overwrite` entries and whether each retirement is genuine.* **Four are genuine, one is a
   convenience, and two of the genuine ones are under-scoped.** The duplicate-coverage retirement the
   agent singled out is genuine and load-bearing (`override_declarations`). The convenience is
   `claim_repair_settlement.overwrite[2]`, which replaces a cap clause with a sentence of the same
   meaning (**F-02**). The under-scoped pair retire clauses that also fixed a premium period and replace
   only the amount (**F-01**). Separately, two base provisions that bear on a scored quantity are
   retired by nobody and implemented by nothing: the aggregate payout cap (**F-09**) and the
   deductible waiver on repair (**F-03**).
3. *The empty `temporal_feasibility`.* **Upheld.** All five base eligibilities of kind `time` govern
   write subjects none of the eight extended policies writes (`policy_conflict_scan`), so the empty field
   is the correct consequence rather than a concealment. Every clock that does bite was recomputed by
   hand on both worlds and every one is satisfied (`0.md` and `1.md`, `policy_self_consistency`). The one
   thing hiding in this area is not a time gate but a boundary disagreement between base's inclusive
   day-count and the extended rule's "still inside the grace days" (**F-07**), which is nowhere near the
   boundary on either world.

---

# revision_2 — re-audit of the reworked charter

## revision_2 scope and freeze

| item | round 1 | round 2 | re-derived? |
| --- | --- | --- | --- |
| `protection.extended.yaml` | `39a422fbedfb1378` | **`bf803ef58485ef6d`** | **yes, in full** |
| `task_tools.py` | `5f5dd14dd046c9e8` | **`c3ffcef028963f84`** | **yes, in full** |
| `tasks/0.json` | `34e063fd9a0e153e` | `5b80502f31aae6bb` | per-task, in `0.md` |
| `tasks/1.json` | `cc622518cf79e46b` | `dc66111896c3c882` | per-task, in `1.md` |

Both shared inputs moved, so **every charter-global section is re-derived rather than carried forward by
reference**, as the re-audit rule requires. Round 1's text above is untouched.

### A correction to the brief's own evidence, before anything rests on it

The brief offers, as verified fact, that the masked views are "byte-identical to round 1", citing
`0.json: 4e4dd72f900bf0c9 (round 1: 4e4dd72f900bf0c9)` and
`1.json: 90d60f37ed68e8be (round 1: 90d60f37ed68e8be)`.

**Those are not round 1's masked-view hashes.** Round 1's masking report, which I re-computed myself at
the time and recorded in `charter_global_frozen` above, gave `b82a2214ef16b110` and `4bebe8a93bfc76c2`.
I re-hashed the current files: they are `4e4dd72f900bf0c9` and `90d60f37ed68e8be` — i.e. the brief's
"round 1" column reproduces the **current** files, so the comparison it offers compares the new views
against themselves and establishes nothing. The masked views were **rebuilt**, not preserved.

The underlying claim is nonetheless **true**, and I established it the only way now available — by
content, not by hash:

- each masked view is byte-faithful to its source task for all three kept keys, and carries exactly
  `['frozen_time', 'initial_state', 'user_scenario']`;
- `frozen_time` is unchanged in both tasks (2026-09-15 10:40 / 2026-09-16 09:25);
- every table's row count is unchanged (task 0: 1/1/3/34/1/2/7; task 1: 1/5/1/3/3/49/1/3/1/3);
- **66 individual `initial_state` values that round 1 quoted and relied on were re-read and compared
  one by one — 34 in task 0, 32 in task 1 — and every one is identical** (figures in `0.md` and `1.md`);
- every distinctive `user_scenario` phrase round 1 quoted is still present in both personas.

So the world did not move, the reworker's claim about it stands, and the world-side facts are not
re-derived. Recorded because an orchestrator-supplied hash comparison was the one entry condition this
round rested on, and it did not hold as stated.

### Base copy, structure and graph, re-derived

- **Base section still verbatim identical** to `blueprint/products/protection.yaml`, key by key; the only
  extra top-level key is `extended_policies`. The base copy has not been rewritten. PASS.
- **`rule`/`compute` equivalence, forward:** 160 bindings (was 150) across the eight policies; every
  binding has a `compute_basis` key, no key names a non-binding, and **every `compute_basis` value is
  verbatim in its own policy's `rule`**. Zero exceptions. PASS.
- **Every `baseline.rule` sentence is present in its policy's `rule`.** Zero exceptions. PASS.
- **Factor structure:** 39 factors, unchanged per-policy counts (4/5/5/5/4/6/5/5), every policy ≥ 2
  `parameter` and ≥ 1 `method`, every `decides` an input never `result`, every factor binding present in
  `compute`, bindings pairwise disjoint within each policy, every ladder exactly three tiers. PASS.
- **`prerequisite` graph:** the same six edges, all `form: state` with no `fallback_reason`, every
  `problem` an extended id in this file, no self-edge, **acyclic**, every `resolved_by` the depended-on
  policy's `target_tool`, no tool name or snake_case token in any `policy_source`, every `policy_source`
  verbatim in the blocked policy's own rule and absent from the depended-on rule. PASS.
- **Action binding and uuid8s:** eight policies, eight distinct target tools, eight distinct
  `(target_tool, computes)` pairs. **The uuid8 set is unchanged** — `2818623b 3dd4c03b 46d57fef 542e239c
  5ae6a6af 79e3e314 c5640f60 d5a520f4` — so no uuid was regenerated, reused or batch-derived. Owners
  unchanged (agent/user/agent/agent/agent/agent/user/user). No docstring names another tool or states a
  sequence position. PASS.
- **Scopes** still pairwise disjoint and jointly complete, 4 + 4 over 8, same partition. PASS.

### The overwrite cluster, re-derived clause by clause

Seven overwrites now (was six). All seven `superseded_clause` strings are verbatim in the named base
policy's rule, and all seven `replaced_by` strings are verbatim in the extended policy's own rule.

| # | policy | base clause retired | verdict |
| --- | --- | --- | --- |
| 1 | `late_fee_scale` | "The plan's late fee is billed once" | genuine (amount) |
| 2 | `late_fee_scale` | "when grace runs out" | **new** — genuine (period); closes F-01's task-0 half |
| 3 | `claim_repair_settlement` | `agg_payout_cap`'s compare-and-cut-back clause | **new** — genuine (basis: direct aggregate, not the measure), and now implemented |
| 4 | `claim_repair_settlement` | `excl_duplicate_coverage`'s warranty bar | genuine, load-bearing, unchanged |
| 5 | `spoilage_allowance` | `agg_payout_cap`'s compare-and-cut-back clause | **new** — genuine, now implemented |
| 6 | `fleet_instalment_billing` | "an instalment plan bills the monthly premium of the plan on the same day of each month" | **unchanged from round 1 — still over-scoped** (finding R2-01) |
| 7 | `claim_excess_charge` | "The plan's deductible is billed once per approved claim" | genuine, and the waiver half is now implemented rather than retired |

**Two round-1 overwrites are gone, and both removals are correct.** The restatement overwrite (round-1
**F-02**) is deleted together with its sentence — I confirmed the repair rule no longer contains
"Where the covered bill is above that ceiling the plan pays the ceiling and the customer meets the rest"
— which puts base's own cap clause back in force, where it never conflicted. The ask-the-customer
overwrite (round-1 **F-04**) is **withdrawn**, so base's "Where the item also carries cover from a card
issuer or a household insurer, the retailer settles only the part of the loss those have not met, and
the customer is asked what has already been paid rather than being paid twice" is wholly in force again,
and the persona answers it outright.

**Nothing is now retired by nobody.** I re-checked the two round-1 undeclared conflicts: the aggregate
payout cap is now declared on **both** payout policies and implemented in both (`payouts_rolling_12m`,
`cap_room`, cut back last); the deductible waiver on repair is no longer retired at all and is instead
implemented (`claim_settlement_basis`, `excess_waived`, plus a baseline sentence and
`deductible_waiver_on_repair` in `baseline.params`). Base `agg_payout_cap`'s un-retired clauses (the
highest-ranked-plan rule, the expired-plan counting rule, the record-the-approval-with-nothing-to-pay
rule, and the apply-after-the-other-caps ordering) are all either inert on these worlds or restated
consistently by the extended rules.

### Ladder realism, re-derived

Both round-1 realism red lights are genuinely repaired **in the rule as well as in the ladder**, and
neither repair moved a tier boundary on either world:

- **F-10** — `spoilage_allowance.outage_share_met`: the conjunct "and the plan carries attendance at the
  address" is gone from the ladder **and** from the rule sentence, and the `onsite_included` binding is
  gone from the policy. The ladder is now `days > 10 → 100`, `3 < days ≤ 10 → 70`, else `40` — a
  monotone partition in the one quantity it is about. It is also strictly better than round 1, which sent
  a >10-day outage on a non-attendance plan down to the 40% tier.
- **F-11** — `claim_excess_charge.prompt_report_reduction_allowed`: the police-report conjunct is gone
  from the ladder **and** the rule, and the `police_report_on_file` binding is removed. The ladder is now
  `days ≤ 3 → 50.00`, `3 < days ≤ 7 → 22.50`, else `0.00` — **monotone**. The round-1 inversion is
  eliminated: a loss reported on day 2 now earns 50.00 where it earned nothing.

**No two tiers of any ladder select the same value or method**, re-checked across all 39 ladders,
including the two variant-dependent cases (`fee_per_unpaid_period` against `premium_late_fee_usd`;
`loading_window_counted` against `plan_term_months`). Round-1 **O-04** is closed by change: both
non-fall-through tiers of `advance_period_discount` now require "its tier carries a plan discount of more
than nothing", and `compute` enforces `> 0`, so the three-way collapse on a `Circle Free Membership`
profile can no longer occur. Round-1 **O-07** is closed by a change of basis rather than of wording:
`invoice_raising_charge` now turns on "no automatic payment instruction stands on the store credit
account" (`autopay_on = CFIELD('credit','autopay_flag', status='active')`, with `autopay_flag` duly added
to that policy's declared `cross_category.reads`) instead of on a premium-payment recency test that held
by construction. `autopay_flag` genuinely divides customers.

**Every label is still honest** and every `method` tier still names a window, an anchor, a counting rule,
a candidate selection or a scaling the charter states.

### findings — revision_2

**R2-01 — `SOURCE-POLICY` residual observation, and a false closure claim. The fleet-instalment
overwrite was not narrowed; `design_rationale` asserts in both tasks that it was.**

*Symptom.* The reworker reports F-01 closed on both sides. Its task-0 half is genuinely closed. Its
task-1 half is not: the overwrite is **byte-identical to round 1**.

*Evidence.* `extended_policies[protection_ext_fleet_instalment_billing].overwrite[0].superseded_clause`
is still:
```
an instalment plan bills the monthly premium of the plan on the same day of each month
```
which still retires base's billing-day provision; the trailing base phrase "with a month-end day falling
back to the last day of a shorter month" modifies the retired clause and so now qualifies nothing. I
read that policy's `rule` sentence by sentence (12 sentences): **none fixes the period of the instalment
entry**, in contrast to `late_fee_scale`, which gained exactly such a sentence ("The fee is billed
against the first day of the oldest premium period standing unpaid on the plan…").

Both tasks' `design_rationale` nevertheless assert the opposite, in the same words:
> "The instalment overwrite of task 1 was narrowed to 'an instalment plan bills the monthly premium of
> the plan', leaving base's billing-day provision and its month-end fallback in force to fix that
> entry's period."

and
> "the instalment overwrite was narrowed to 'an instalment plan bills the monthly premium of the plan',
> so base's billing-day provision and its month-end fallback stay in force and fix the period this entry
> is stamped with"

The quoted `superseded_clause` is not the one in the charter.

*Consequence.* Unchanged from round 1 and **not a red light**: `bill_premium_instalment`'s `period_start`
and `period_end` still have no policy ground, but task 1's records leave exactly one period reached and
unbilled against a nineteen-charge cycle on the tenth, so 2026-09-10 / 2026-10-09 remains the only
reading and the task keeps one answer. What is new is that a proof field asserts an artefact fact the
artefact contradicts, and that assertion is the sole basis offered for closing this half of F-01. So:
**F-01 is closed as a RED** — its red-light demonstration was task 0's three competing periods, and that
is fixed — **while its task-1 observation stands, un-remedied and now mis-described.**

*Affected artefact.* `protection.extended.yaml`,
`extended_policies[protection_ext_fleet_instalment_billing].overwrite[0]` and that policy's `rule`;
`tasks/0.json` and `tasks/1.json`, `design_rationale`.

---

**R2-02 — observation. O-05 is partially closed: the reads that select a tier are now job-scoped, the
reads that build the covered bill are not.**

*Closed half.* `claim_repair_settlement` gained `covered_item_job =
CFIELD('service','service_agreement_id', item_serial=F('covered_item_serial'))`, and
`diagnoses_recorded`, `latest_diagnosis` and `visits_drawn` are now filtered by it;
`spoilage_allowance` gained the same binding and `work_completed_date` is now resolved by the covered
serial instead of by `status='completed'` (which round 1 showed returned whichever completed agreement
the seed happened to list first); `claim_excess_charge` scopes `care_visits_drawn` to a care-agreement
job. The two parts tiers that deliberately read outside the window now say so in the rule — "the largest
single parts entry booked on the job, **whenever it was booked**" and "the most recent parts entry booked
on the job, **whenever it was booked**" — which closes round 1's complaint that `XMAX`/`XLATEST` carried
no `within_months` while the rule scoped the bill to the window.

*Open half.* In the same policy, `labour_billed`, `parts_entries`, `attendance_billed` and the tier-1
`XSUM` inside `parts_base` are **still customer-scoped**, carrying no `service_agreement_id` filter,
while the rule says the covered bill is "the labour, the parts and the attendance charges booked against
**the job on the covered item** inside the window read". Now that `covered_item_job` exists as a binding
three lines above them, the omission is conspicuous.

*Consequence.* None on either world — task 0's second job is a television whose rows fall outside the
six-month window the rule selects, so both readings give 385.00 / 2 entries / 861.00 / 89.00 and the
payout is 1248.90 either way. The exposure is that a seed change bringing a second job's charges inside
the window would silently change the covered bill without any rule sentence sanctioning it.

---

**R2-03 — observation. `compute` names a product the `rule` does not.**

`claim_excess_charge` now scopes the drawn-visit count with
`care_agreement_job = CFIELD('service','service_agreement_id', variant_name='TechWorks Managed IT Care Annual')`
— a hard-coded variant-name literal. Its `compute_basis` quotes the rule sentence "The allowance for a
managed care agreement is sixty dollars where the profile holds a care agreement whose included visits
run to twelve or more in its term…", which names **no product**. Separately, `care_visits` is still
`CPARAM('service','included_visits_per_term', status='scheduled')`, keyed on status, so the two reads are
not tied to the same holding and could in principle select different ones.

*Consequence.* None on task 1, which holds exactly one service agreement, of that variant, with
`status: scheduled` and `included_visits_per_term: 12`, so both reads land on it and
`care_visits_drawn` stays 2. Recorded as a check-2 residue: a basis in `compute` that the `rule` does not
state.

---

**R2-04 — observation. The late-fee overwrite retires "billed once" without restating it.**

Overwrite #1 retires `"The plan's late fee is billed once"` and the extended rule nowhere says the fee is
billed once — I checked: the string does not occur. The parallel overwrite on
`claim_excess_charge` retires `"The plan's deductible is billed once per approved claim"` and **does**
restate it ("…billed once for that claim and never below nothing"), so the asymmetry is visible within
the same charter.

*Consequence.* None demonstrable: the rule's singular phrasing and the single `period_start` it now fixes
entail one entry, and no second reading produces two. Recorded because the split that closed F-01's
task-0 half is what exposed the word.

---

**R2-05 — observation. A robustness trade in the `work_completed_date` fix.**

Round 1's `CFIELD('service','completed_date', status='completed')` guaranteed a non-empty date but could
select the wrong job; the new `CFIELD('service','completed_date', item_serial=F('covered_item_serial'))`
selects the right job but can return `""` on a job that is not finished. The `outage_clock` tiers test
`work_completed_date != None`, which `""` satisfies, so an unfinished job would take a completion-anchored
tier with an empty anchor. Inert on task 0, whose fridge job is `completed` with `completed_date
2026-09-10`. Net a correctness improvement; recorded because the guard was not carried over.

---

**R2-06 — observation. The `factor_sensitivity` staleness class recurs after being fixed.**

Round-1 **T1-02** named two `tier_taken` strings in `claim_excess_settlement` that misquoted their
ladders; both are now correct. But the O-04 fix reworded
`arrears_measurement_basis`'s sibling `advance_period_discount` ladder, and **that factor's `tier_taken`
was not regenerated**: `tasks/0.json`,
`computations[protection_ext_premium_arrears_settlement].factor_sensitivity[advance_period_discount].tier_taken`
still reads
> "the plan applies the membership discount and the Circle membership on the profile stands active"

against the charter's
> "the plan applies the membership discount, the Circle membership on the profile stands active **and its
> tier carries a plan discount of more than nothing**".

*Consequence.* None numeric — the figure (88.45) is correct and the omitted conjunct also holds on this
world (the Circle Plus tier carries 5%). One mismatch now, against two in round 1, but in a different
policy: the named instances are closed and the class is not. A `tier_taken` string is part of the proof,
so the ladder and its sensitivity record should move together.

---

**R2-07 — observation. The F-12 declaration is half-delivered.**

The reworker reports the stale-cache declaration added "to `design_rationale` **and** to the plan row's
`seed_consistency`". The `design_rationale` half is delivered — it now quotes the schema's identity
sentence and states that `arrears_measurement_basis` tier 1 is reachable only on a world that breaks it.
The `seed_consistency` half is not: `tasks/0.json`,
`solvability_contract.seed_consistency` for
`initial_state.protection_plans.d9cb7845-045b-4398-b837-b71f554aa281` is **unchanged from round 1** and
contains neither the schema quote nor the reachability statement; it still says only "the recorded
premium outstanding of 38.97 is deliberately one instalment short of the 51.96 the ledger carries, the
single stale figure in this world."

---

### Ruling on F-12

**F-12 remains an observation. I decline to hold it RED.** The grounds, in the order that decides it:

1. **The standard this audit applies.** A red light "arises only from these four relationships, and its
   consequence must be demonstrated on the spot"; what cannot be demonstrated is an observation. I could
   not demonstrate a consequence in round 1 and cannot now. The second reading — treating the ledger's
   51.96 as the field's true value because the schema says the two are identical — requires the agent to
   **disbelieve a row the finder returns**, which it has no means to do; and
   `arrears_measurement_basis` tier 1 puts both quantities side by side ("where the premium entries
   booked on the plan add up to more than the outstanding premium recorded on it and the plan stands
   active") and tells the reader which governs. The task has one answer.
2. **I re-verified that, rather than relying on round 1.** The ladder text, the compute branch and the
   two compared quantities are unchanged; the world is unchanged; and all 55 computation figures
   including `arrears_measurement_basis`'s own sensitivity (98.31 against gold 87.80) recompute
   identically. The reworker citing my round-1 conclusion back at me is legitimate only because that
   conclusion survives independent re-checking this round, which it does.
3. **Holding it RED would trade an unprovable defect for a provable one.** Correcting the seed so that
   `premium_outstanding` equals the ledger would make tier 1's condition unsatisfiable — the two compared
   quantities would coincide — so the ladder would collapse onto its fall-through and
   `arrears_measurement_basis` would become decorative on this world. A factor that does not bear weight
   **is** a demonstrable `SOURCE-FACTOR` failure, of exactly the kind round 1 spent nineteen
   substitutions ruling out. I will not require a change whose predictable effect is a red light.
4. **The divergence is not one of the four relationships.** It is a seed-versus-constitution
   inconsistency: `db_schema.json` says the field is "identically the sum of the premium_receivable
   account deltas", and this world's seed is one instalment short on that one field. That is a statement
   about what a field *means*, not about whether the policy is self-consistent, whether the tree holds,
   whether the factors bear weight, or whether the policy entails one solution. Treating it as a red
   light would be erecting a third set of rules, which this audit is directed not to do.
5. **The schema is out of the reworker's write domain, and it was right not to touch it.** So the only
   actionable form of a RED here would have been to break the device. Recording the divergence, where a
   future reviewer will find it if the schema's language is ever tightened or a cached-field identity
   gate is added, is the response that fits the evidence.

**What stays on the record, permanently:** this world breaks a stated identity of the frozen schema on
one field by design, and tier 1 of `arrears_measurement_basis` is reachable **only** on a world that
breaks it. That is the honest residue, and it is not erased by the declaration — the declaration makes
the device visible, which is what was missing, and visibility is the remedy proportionate to an
observation. The declaration is also only half where it was said to be (**R2-07**).

## closing_checklist — revision_2

**This difficulty now closes out.** Both tasks carry a `source_gt_comparison` and a revision_2
verification with **PASS on all four relationships**; the per-task evidence is in `0.md` and `1.md`.

| Step 4 item | status after revision_2 |
| --- | --- |
| per-task files one-to-one, `_difficulty.md` alongside, **old revisions traceable** | **met** — round 1's text is untouched in all three files; revision_2 is appended |
| every comparison section carries a PASS | **met** — task 0 PASS ×4, task 1 PASS ×4 |
| extended policies fully covered, scopes pairwise disjoint over the whole tree | **met** — same 4 + 4 partition over 8 |
| task tools and GT closed | **met** — each policy computes one argument of one call; `required_documents` = `charter_scope.extended_policies` in both |
| each task tool an independently generated, frozen uuid8 | **met** — the eight uuid8s are unchanged from round 1, so none was regenerated |
| 1–3 prerequisite problems, ≥ max(n−1,1) `value_input`, ≥ 1 `owner=user`, acyclic; whole-difficulty DAG | **met** — 3 / 2 / 1 / acyclic in each task, six edges forming two disjoint acyclic chains. Task 1's tree is now genuinely three-deep: the rescoped root sentence is false at `frozen_time` over a non-empty set (`1.md`, R2-T1-01) |
| self-sufficient baselines, 4–6 factors (2 `parameter`, 1 `method`; ≥ 1 multi-source, ≥ 1 cross-difficulty per task), ladders ≥ 3 tiers stated in full, tiers distinct, conditions and outcomes ones the business holds, every factor bearing weight against an honest baseline, baseline alone definite and ≠ gold | **met** — 39 factors, structure unchanged and in bounds; both realism red lights repaired in rule and ladder; all 39 sensitivities and all 8 baseline figures recompute to round 1's values |
| instantiation-stage gates re-run on the final form | **met, by the coordinator** — snapshot cited: `check_extended`, `check_task_tools`, `check_solvability`, `check_compute`, `check_grounding`, `check_cross_fire`, `replay --check` all OK. `check_traceability` remains deferred to step 3 by design. I did not re-run them and did not write to `tasks/` |

**Aggregate agreement with round 1.** 55 computation quantities (8 `expected`, 8 `baseline_result`, 39
`factor_sensitivity`) and 7 of 8 gold write-argument sets are **identical**; the eighth differs only by
the two arguments the payout tool gained, both of which I verified are uniquely derivable from seeded
records. 66 `initial_state` values and both personas are unchanged. The reworker's claim that all 78
quantities recompute identically is **upheld**, now on my own recomputation rather than on its word.

**Residual open items, all observations, none blocking:** R2-01 (fleet-instalment period ungrounded and
mis-described), R2-02 (job scoping half-applied), R2-03, R2-04, R2-05, R2-06, R2-07, plus the standing
F-12 residue and round 1's O-01 and F-06, whose arguments I accept as sound — O-01 re-verified in
substance across all 54 paraphrases this round, F-06 still grounding no edge because the blocked policy
carries its own sentence.

---

# revision_3 — re-audit of the KB-driven source fix

## revision_3 scope and freeze

| item | revision 2 | revision 3 | re-derived? |
| --- | --- | --- | --- |
| `protection.extended.yaml` | `bf803ef58485ef6d` | **`7f4c1c3168438698`** | **yes, in full** |
| `task_tools.py` | `c3ffcef028963f84` | `c3ffcef028963f84` | **unchanged** — carried forward by hash |
| `tasks/0.json` | `5b80502f31aae6bb` | `ee638ee574a8dad3` | per-task, in `0.md` |
| `tasks/1.json` | `dc66111896c3c882` | `63ca7f3e6d9c9192` | per-task, in `1.md` |
| masked view 0 / 1 | — | `31dc80ca36970e00` / `5b4959938797cd4f` | **both moved — worlds re-derived** |

All five entry hashes re-computed and matching the brief. `task_tools.py` is byte-identical to the file I
audited at revision 2, so the tool-contract section — eight distinct frozen uuid8s, owners, docstring
silence about sequence, no prerequisite judgement in any body — **is carried forward by hash** and was not
re-derived. Everything else in this section is re-derived. Revisions 1 and 2 above are untouched.

Unlike revision 2, the brief's hash figures were internally consistent and all five verified on first
re-computation. `check_traceability` now runs and passes (0.json 30 copied / 0 missing, 1.json 28 / 0);
I cite the coordinator's gate snapshot and did not re-run the gates.

### First: what I got wrong at revision 2

The render-layer auditor's **P1** is the same defect I recorded at revision 2 as **R2-02**, and I
classified it as an observation with "no consequence on either world". That classification was **wrong**,
and the error is worth stating precisely because it is a lesson about how I tested, not a close call.

I had the mechanism from round 1 — my own frozen text reads: "the baseline fall-back number 721.95 is
itself computed on a basis that contradicts the rule's own 'booked against the job on the covered item'."
I then tested factor weight by substituting each factor's baseline **into the compute**, which is what the
harness does and what `factor_sensitivity` records. Because the job-scoping inconsistency was present on
both sides of that substitution, it cancelled out of every one of my nineteen tests. What I failed to do
was compute the aggregates **from `baseline.rule` alone**, as my own rubric requires. Had I done so I would
have found what the render auditor found:

- the declared `baseline_result` of 721.95 was **not** what the rule's own baseline yields — job-scoped
  that is `385.00 × 0.90 + 248.60 × 0.75 = 532.95`, a gap of 189.00; and
- `repairer_bill_window` bore **no weight** on task 0's scored number, because job-scoped every entry on
  the covered item's job fell inside both the six-month and the twelve-month window, so the declared
  1470.00 sensitivity existed only under the customer-scoped read.

Both are demonstrable consequences under the **factors bear weight** relationship — a dishonest baseline
and a factor that does not bear weight are two of the failure modes that relationship names explicitly. So
R2-02 should have been recorded as `SOURCE-FACTOR RED` at revision 2, not as an observation, and this
difficulty should not have closed out at revision 2. The scored answer was never wrong; the proof of it
was. Recorded here rather than by editing revision 2, which stands as written.

### Charter-global checks, re-derived on `7f4c1c3168438698`

- **Base section still verbatim identical** to `blueprint/products/protection.yaml`, key by key. PASS.
- **`rule`/`compute` equivalence, forward:** 160 bindings; every binding has a `compute_basis` key, no key
  names a non-binding, **every `compute_basis` value verbatim in its own policy's `rule`**. Zero
  exceptions. PASS.
- **Every `baseline.rule` sentence is a sentence of its own `rule`** — all eight policies, zero
  exceptions. PASS.
- **Factor structure unchanged and in bounds:** 39 factors, per-policy 4/5/5/5/4/6/5/5, each ≥ 2
  `parameter` and ≥ 1 `method`; every `decides` an input never `result`; every factor binding present in
  `compute`; bindings pairwise disjoint within each policy; every ladder exactly three tiers; **every
  ladder's three outcomes distinct** (39/39). PASS.
- **`prerequisite` graph unchanged:** the same six edges with the same `kind`, `gate`, `form`,
  `policy_source` and `resolved_by`; all `form: state`; acyclic; every `policy_source` verbatim in the
  blocked policy's own rule and absent from the depended-on rule. PASS.
- **Overwrites unchanged in shape:** seven, distributed 2/0/2/1/1/1/0/0 exactly as at revision 2, every
  `superseded_clause` verbatim in the named base rule and every `replaced_by` verbatim in the extended
  rule. PASS.
- **Scopes** still pairwise disjoint and jointly complete, 4 + 4 over 8; `charter_scope.extended_policies`
  equals `required_documents` in both tasks; `temporal_feasibility` still `[]` in both, correctly, since
  the five base `time` eligibilities still govern subjects neither task writes. PASS.

**New: no added sentence collides with a prerequisite sentence.** Six policies gained rule text this
round, so I swept every sentence of all eight rules against all six prerequisite sentences for exact
duplication, containment and reverse containment: **clean**. No added sentence restates, swallows or is
swallowed by any dependency sentence, so the dependency-form topology the render layer passed is intact on
the source side.

### The cross-product sweep, spot-checked

Both shapes the coordinator named hold where I checked them.

1. **No `baseline.params` key declares a factor constant.** Checked all eight policies: every
   `baseline.params` entry is either a variant parameter or a `K` constant that the factor's own
   **fall-through** tier selects, and **no** entry names a `K` that a non-fall-through tier selects. So no
   baseline document can quote a figure that belongs to a variation. Clean.
2. **Every binding's `compute_basis` is verbatim in its own rule** — 160/160, as above. Clean.
3. **Going further than asked, I swept for unstated *figures*:** for every `K` constant used in every
   compute, is its numeric value expressed in that policy's own rule in business words? One apparent hit —
   `protection_ext_premium_arrears_settlement`'s `fee_share_part_pct = 50` — turned out to be a gap in my
   own word list, not in the charter: the rule states it as "it is **half of them**". Every other constant
   is stated. So **B1's threshold of one was indeed the only unstated figure in the eight policies**, and
   it is gone.

### findings — revision_3

**R3-01 — B1 verified CLEAN, including the parts the brief flagged as load-bearing.**

The resolution went the right way — the prose was judged business-true and the **binding** was changed to
match it, rather than the text being loosened to match the binding. Both paying tiers of
`managed_care_allowance` now require `care_visits >= K('care_visits_threshold')`, i.e. twelve or more, and
differ only on `care_visits_drawn`:

| tier | condition | value |
| --- | --- | --- |
| 1 | included visits twelve or more **and** a visit drawn inside the last twelve months | 60.00 |
| 2 | included visits twelve or more **and** no visit drawn inside that time | 30.00 |
| 3 | "otherwise, including a profile holding a care agreement whose term carries fewer than twelve included visits" | nothing |

Checked, item by item against what the brief asked:

- **Both paying tiers reachable on a scorable world.** `included_visits_per_term` is 0/1/2/1/4/**12**
  across the six TechWorks variants, so the qualifying holding is `TechWorks Managed IT Care Annual`.
  Tier 1 is reachable and taken on task 1 (two `service_visit_consume` rows). Tier 2 is reachable on the
  same holding with no visit drawn. The threshold still **divides** customers — those holding managed IT
  care against those holding any other agreement or none — so it is not a scope restatement.
- **The ladder still partitions.** `(≥12 ∧ drawn≥1)`, `(≥12 ∧ drawn≤0)`, otherwise: disjoint and
  exhaustive.
- **The fall-through is still the baseline.** `baseline: {care_allowance: '0.0'}` and `baseline.rule`
  carries "No allowance for a managed care agreement is allowed."
- **The factor still bears weight.** Substituting 0.00 moves task 1's excess from 202.50 to **262.50**,
  which is the declared sensitivity unchanged.
- **Tier 2 spells out its antecedent** — the "such an agreement" whose nearest antecedent caused B1 is
  gone, replaced by the full phrase — and the fall-through **names the excluded case**, so the
  fewer-than-twelve reading can no longer be inferred either way.

Two further improvements fall out of it, and they close a revision-2 observation of mine in both halves.
**R2-03** recorded that `care_agreement_job` hard-coded `variant_name='TechWorks Managed IT Care Annual'`
— a basis the rule never stated — and that it was keyed differently from `care_visits`, so the two reads
could select different holdings. Both are fixed: the binding is now
`CFIELD('service','service_agreement_id', status='scheduled')`, the same key `care_visits` uses, so the two
reads are tied to one holding; and a new rule sentence states the basis — "The care agreement read is the
one standing scheduled on the profile, and the included visits it carries are the visits its own term
allows rather than the visits left on it." I confirmed the variant string occurs **zero** times in the
charter; the single remaining "TechWorks" is prose inside a `cross_category` note. **R2-03 CLOSED.**

That new sentence also forecloses a reading the seed correction made possible: it says outright that the
ladder reads the term's allowance and not `visits_remaining`, which P8 changed from 9 to 10.

---

**R3-02 — P1 verified CLEAN, and the world move is safe.**

All six job-scoped reads in `claim_repair_settlement` now carry `service_agreement_id=covered_item_job`:
`labour_billed`, `parts_entries`, `largest_part`, `latest_part`, the tier-1 `XSUM` inside `parts_base` and
`attendance_billed`, joining the three that already did. The rule and its executable basis now agree on
scope, so **R2-02 is closed at its root** rather than left as the observation I wrongly settled for.

The re-seeding is the risky half and it holds. The January labour of 210.00 and parts of 155.00 moved from
the television job onto the covered item's own job, and the television job was given its **own** entries
inside the six-month window (labour 168.00, parts 96.50, both 2026-06-18). Three things follow, each
verified by hand on the new world:

- **`baseline_result` now genuinely equals what the baseline yields.** Job-scoped, twelve-month window,
  parts = the most recent entry on the job whenever booked: `595.00 × 0.90 + 248.60 × 0.75 = 535.50 +
  186.45 = **721.95**`, which is the declared figure. The 189.00 gap the render auditor demonstrated is
  gone, and 721.95 is now earned on the rule's own scope instead of coinciding with the customer-scoped
  read.
- **`repairer_bill_window` bears weight again.** Job-scoped with the baseline twelve-month window the
  January entries come in: labour 595.00, parts 155.00 + 612.40 + 248.60 = 1016.00, attendance 89.00 →
  covered bill 1598.40, capped to **1470.00** against the scored 1248.90. That is the declared sensitivity,
  now genuinely load-bearing.
- **The job filter is itself load-bearing.** Removing it and keeping everything else: labour 385.00 +
  168.00 = 553.00, parts 612.40 + 248.60 + 96.50 = 957.50, attendance 89.00 → 1503.75, capped to
  **1470.00**. So the filter moves the scored number by 221.10, which is what makes the television job a
  real discriminator rather than decoration.

The computation now carries **two** near-misses where revision 2 had one: the January entries on the right
job but outside the window, and the June entries inside the window but on the wrong job. Each is excluded
by a sentence of the rule ("inside the window read"; "booked against the job on the covered item").

**Nothing else in the computation moved:** the other four sensitivities are identical (697.74 / 1119.75 /
1159.90 / 1210.40), and the scored payout is 1248.90.

---

**R3-03 — P2 and P3 verified CLEAN by one definition, and the seed split reconciles.**

The rule gained a definition in the product's own words:

> "The attendance charges are the trip charge, the after hours surcharge and the mileage beyond the covered
> radius booked on that job; a no-show fee, a reschedule fee, a cancellation fee, a haul-away fee and a
> diagnostic fee are not attendance charges and the plan meets none of them under this head."

`attendance_billed` now sums exactly those three `charge_kind` values (`trip_charge`,
`after_hours_surcharge`, `out_of_radius_fee`) on the covered item's job inside the window, instead of every
`service_fee_charge` row. All eight kinds the sentence names exist in the schema's `charge_kind` enum; the
enum's remaining four values are labour and parts kinds, which the rule handles under their own heads, so
the definition partitions the fee vocabulary completely.

**It narrows no eligibility and widens none.** It governs which rows enter one computation input. The base
eligibilities that bear on `protection_claim_payout` are `payable_plan_state` (plan status) and the retired
`no_overlapping_warranty_settlement`; neither mentions charges. `attendance_share_met`'s own ladder
conditions (`onsite_included`, `visits_drawn`) are untouched, and its three outcomes are unchanged.

**The seed split reconciles against the published schedule**, which is what P3 said the old figure did not:
the single 89.00 `trip_charge` became a 59.00 `trip_charge` and a 30.00 `out_of_radius_fee`, and
`TechWorks Appliance Install and Haul Away` publishes `trip_charge_usd: 59.0`, `travel_radius_miles: 35`
and `out_of_radius_fee_usd_per_mile: 2.5` — so 30.00 is exactly twelve miles beyond the radius. The total
is preserved at 89.00, which is why no figure moved. The split also removes a numeric collision the old
seed carried: 89.00 was simultaneously the booked trip charge and that variant's published
`diagnostic_fee_usd`.

---

**R3-04 — observation. The new definition has no discriminating record on either world.**

The covered item's job carries two fee rows and both are named *in*-kinds, so no seeded row is excluded by
the definition. The sentence is normatively necessary — it is what makes the binding's three-kind sum
derivable rather than invented — but neither task exercises it, so a future change that widened the binding
again would not be caught by either task's figures. Recorded as a determinacy note, not a defect.

---

**R3-05 — observation. Two revision-2 items were out of this round's scope and are unchanged.**

- **R2-01** stands in full: `protection_ext_fleet_instalment_billing.overwrite[0].superseded_clause` is
  still "an instalment plan bills the monthly premium of the plan on the same day of each month", still
  retiring base's billing-day provision, and that policy's rule still contains no sentence fixing the
  period of the instalment entry — I re-read all twelve sentences. Both tasks' `design_rationale` still
  assert the narrowing was applied. Consequence unchanged: `bill_premium_instalment`'s `period_start` and
  `period_end` have no policy ground but are pinned uniquely by the records, so it remains an observation.
- **R2-06** stands: exactly one `factor_sensitivity[].tier_taken` string is still stale — task 0's
  `advance_period_discount`, which omits the "and its tier carries a plan discount of more than nothing"
  conjunct its ladder gained at revision 2. Figure 88.45 correct, quotation stale.

Neither was in this round's remit and neither regressed. **R2-04** and **R2-05** likewise stand
unchanged, R2-05 still inert (the covered item's job is completed, now with `completed_date 2026-09-12`).

---

**R3-06 — nothing regressed.**

- **No scored value moved.** All **55** declared computation quantities — 8 `expected`, 8
  `baseline_result`, 39 `factor_sensitivity` — are identical to revision 2, and all **8** gold write
  argument sets are identical, including the payout tool's two arguments added at revision 2. Task 0:
  23.50 / 87.80 / 1248.90 / 206.10. Task 1: 41.34 / 202.50 / 127.50 / 136.54.
- **The only narration change is the one claimed:** days out of use 11 → 13, following the covered job's
  completion day moving from 2026-09-10 to 2026-09-12. Still above the ten-day boundary, so
  `outage_share_met` stays on tier 1 and the allowance stays 206.10; `outage_clock`'s baseline still
  gives 139.77.
- **Every prerequisite is still genuinely unmet at `frozen_time`** on the moved worlds — six edges
  re-checked against the new rows in `0.md` and `1.md`. Task 0's `protection_events` are untouched (34
  rows, every aggregate identical), which is why the premium and payout edges could not have been
  disturbed by a service-side re-seed.
- **`frozen_time` unchanged** in both tasks; both personas unchanged.
- Structure unchanged throughout: factors, overwrites, prerequisite graph, scopes, `temporal_feasibility`,
  `db_closure_matches_initial_state`, and — by hash — the tool module and its uuid8s.

## closing_checklist — revision_3

**The difficulty closes out again, and this time the factors relationship closes on the rule rather than
on the compute.** Both tasks PASS ×4; per-task evidence in `0.md` and `1.md`.

The revision-2 checklist stands with three lines restated on stronger ground:

| item | status after revision_3 |
| --- | --- |
| every comparison section carries a PASS | **met** — and the revision-2 PASS on task 0's factors is now sound rather than accidental: see the self-assessment above and R3-02 |
| baselines self-sufficient, every factor bearing weight against an honest baseline, baseline alone definite and ≠ gold | **met on the rule's own scope** — `baseline_result` 721.95 is now what the baseline document yields, and `repairer_bill_window` bears weight (1470.00 against 1248.90) |
| ladders' conditions and outcomes ones that line of business actually holds | **met** — B1's unstated threshold of one is gone; both paying tiers of the care allowance require the twelve-visit agreement the prose always named |
| old revisions traceable | **met** — revisions 1 and 2 are verbatim in all three files; revision_3 is appended |
| gates re-run on the final form | **met, by the coordinator**, and `check_traceability` now runs and passes (30/0 and 28/0) |

**Residual open items, all observations, none blocking:** R2-01, R2-04, R2-05, R2-06, R3-04, plus the
standing F-12 residue and round 1's O-01 and F-06. The render layer's own P4 (illustrations sitting close
to the seeded world, including a factor document showing 41.34 beside task 1's monthly premium), P5, P7 and
P9 belong to the render layer's report and to its remit; I note P4 only because it is the one of them whose
subject matter — a published figure equal to a scored value of the same task — could bear on a future
source-layer judgement about whether a computation remains genuinely derivable.
