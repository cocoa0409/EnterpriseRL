# Policy-task audit — workshop_service_desk / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (not the instantiating agent).
- Freeze time (charter-global section written): 2026-09-17, before any task's GT was revealed.
- Frozen inputs and hashes (sha256, first 16 hex):
  - `env/env_0001_fine_jewelry_retailer/tasks/workshop_service_desk/service.extended.yaml` — `5a6301bdf93243ce` (166746 bytes)
  - `env/env_0001_fine_jewelry_retailer/tasks/workshop_service_desk/task_tools.py` — `da81aace2a821ece` (13637 bytes)
  - `env/env_0001_fine_jewelry_retailer/blueprint/blueprint.yaml`, `db_schema.json`, `share_tools.py`, `products/service.yaml`
- Masked views consumed for the per-task work (constructed by the coordinator, not by self-discipline):
  - `…/scratchpad/masked/workshop_service_desk/0.json` — `f0dc75c3e0a0b027`
  - `…/scratchpad/masked/workshop_service_desk/1.json` — `0a862c54c36c0f6c`
  - kept: `frozen_time`, `user_scenario`, `initial_state`
  - DROPPED (not hidden — absent from the file): `design_rationale`, `db_closure`, `db_closure_matches_initial_state`, `solvability_contract`, `evaluation_criteria`, `computations`, `prerequisite_closure`, `charter_scope`, `required_documents`
  - verified by key enumeration: both masked files expose exactly `['frozen_time','initial_state','user_scenario']`.
- Entry conditions (Step 0): the instantiation gate block was supplied with the brief as actual output lines (EXTENDED / TASK-TOOL-CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE, all OK; `check_traceability` legitimately excluded pending the published KB). The auditor cites them and did not re-run them. Nothing is missing from the input.
- Nothing in this section is derived from any revealed GT field.

### policy_conflict_scan

The structured policy in force for category `service` at this difficulty is the base section of
`service.extended.yaml` (12 base policies, verbatim) plus 5 `extended_policies`.

**Base copy is verbatim identical.** A key-by-key comparison of
`blueprint/products/service.yaml` against the base section of
`tasks/workshop_service_desk/service.extended.yaml` shows zero differences across
`category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies`;
the only extra top-level key in the extended file is `extended_policies`. The base copy has not been rewritten.

**Overlapping subjects.** The five extended policies take these subjects, each claimed once:

| extended policy | subject event | target tool | computes |
| --- | --- | --- | --- |
| `service_ext_claim_coverage_credit` | `service_coverage_applied` | `apply_claim_coverage_f28c459e` | `covered_amount` |
| `service_ext_revised_authorization` | `service_work_authorized` | `confirm_authorized_ceiling_b1b9df84` | `authorized_ceiling` |
| `service_ext_expedited_surcharge` | `service_rush_fee_charged` | `charge_expedite_surcharge_af83d9eb` | `surcharge_amount` |
| `service_ext_carried_release_value` | `service_order_details_updated` | `confirm_stone_release_3a8d360e` | `carried_value` |
| `service_ext_insured_return_shipping` | `service_shipping_charged` | `charge_insured_shipping_16f801d8` | `shipping_amount` |

No two extended policies share a subject event, a target tool or a computed quantity. Each base
policy whose subject overlaps one of these (`service_protection_coverage`, `service_authorization`,
`service_expedited_handling`, `service_intake_admission`, `service_settlement`) is named in the
corresponding `base_policy_refs`.

**Triggers, eligibility, time anchors, terminal states.** `trigger` is `state_due` for the two
policies whose write follows from the record's own state (`…claim_coverage_credit`,
`…carried_release_value`) and `on_request` for the three the customer asks for
(`…revised_authorization`, `…expedited_surcharge`, `…insured_return_shipping`). Every
extended policy anchors its time reckoning on the handling date (`NOW`) and on dated fields of
`service_orders` (`intake_date`, `estimate_date`, `authorized_date`, `promised_date`) or on dated
ledger rows; no two policies read the same anchor to opposite effect. All four business-day→calendar
conversions in the charter use the same stated convention — "counted in calendar days at five working
days to the week", implemented uniformly as `P('…_business_days') * K('calendar_days_per_week') / K('working_days_per_week')`
with `calendar_days_per_week: 7`, `working_days_per_week: 5`. No conflict.

**Cross-category read boundaries.** Declared reads are `protection` (3 policies), `circle` (3), and
`appraisal` (2). All are read `as: branch` — they decide a tier, never a write. No extended policy
writes outside `service_ledger` / `service_orders` / `service_intake`; the tool module confirms this
(`ctx.create` on `service_ledger` ×3, `ctx.create` on `service_intake` ×1, `ctx.update` on
`service_orders` ×1).

**Scope exclusivity and completeness across the M=2 tasks.** The two problem trees the `prerequisite`
graph induces are:

- Tree A (root `service_ext_expedited_surcharge`) → `service_ext_revised_authorization` → `service_ext_claim_coverage_credit`
- Tree B (root `service_ext_insured_return_shipping`) → `service_ext_carried_release_value`

The two node sets are disjoint and their union is all five extended policies. So the tasks' scopes
are pairwise disjoint and jointly complete over this difficulty's extended policy space.

**Conflicts found.** Two base provisions are handled differently by an extended policy without being
named in that policy's `overwrite`; both are written up in `### override_declarations` below and both
bear on task 0.

### rule_compute_equivalence

Check 2, run over every extended policy of the charter, in both directions.

**Forward (every quantity of the `rule` has a `compute_basis` quotation and a restricted-expression
implementation).** Each of the five policies carries a `compute_basis` entry for every one of its
`compute` bindings; the mapping is complete (no binding without a basis) and every basis string is a
substring of that policy's own `rule` modulo whitespace. Specifically checked and found present in
both faces:

- Quantities and bases: `labour_booked` / `booked_charges` (bench labour standing priced on the work
  order), `net_bench_total` (priced lines less amounts taken off less what coverage answered for),
  `ceiling` (the ceiling on the most recent confirmed authorisation), `basis_value` (the papers on the
  piece), `base_charge` (the level's own insured shipping rate).
- History windows: the twelve-month windows (`claims_filed_12m`, `member_workshop_spend_12m`,
  `member_benefits_used_12m`, `member_benefits_12m`) each carry the rule phrase "in the twelve months
  to the handling date" and are implemented `within_months=12, date_field='posted_date'`.
- Filters: `member_amounts_taken_off` restricts to `discount_reason_code='loyalty_tier_benefit'`
  against "the amounts taken off under a member benefit alone"; `recovery_credits` restricts to
  `discount_reason_code='goodwill_service_recovery'` against "taken off the work order as a goodwill
  recovery"; `largest_bench_line` restricts to `charge_code='bench_labor'` against "the largest line
  priced under the bench labour charge code"; `member_workshop_spend_12m` restricts to
  `earn_category='workshop_service'` against "qualifying workshop spend".
- Tiers and branches: every tier of every declared ladder appears as a sentence of the `rule` AND as a
  branch of the `decides` binding — verified factor by factor below in `### factor_ladders`; no tier
  lives only in `compute`, and no branch of a `decides` binding lacks a rule sentence.
- Cross-category reads: each `CFIELD`/`XSUM`/`XCOUNT` has a matching `cross_category[].reads` entry
  (`protection.status`, `protection.claims_settled_count`, `protection.remaining_benefit_allowance`,
  `protection.item_value_at_purchase`, `protection_ledger.event_type`, `appraisal.appraised_value`,
  `appraisal.valid_until`, `appraisal.status`, `circle.status`, `circle_ledger.qualifying_spend`,
  `circle_ledger.event_type`).
- Acting bases / grouping: the rate-sum grouping of `…revised_authorization`
  (`contingency + stale + member + covered`, all applied to one `net_bench_total`) and the
  step-sum grouping of `…insured_return_shipping`
  (`100 + value + promise + paperwork − leg`, all applied to `insured_shipping_charge`) are each
  stated in one rule sentence and implemented as one expression.
- Caps/floors: `MN(answered, line_cap, allowance_left)`, `MN(relieved_amount, cap_amount)`,
  `MN(stated_value, value_ceiling)` each quote "it is never more than …".
- Rounding mode and point: every policy's rule says "rounded to the nearest cent" / "every figure is
  rounded to the nearest cent" and every monetary binding is wrapped in `RND(…, 2)`. Rounding points
  are stated where they are intermediate (the allowance, the uplifted allowance, the base charge).
- Interval counting: "counted in calendar days from the day it was taken in over the counter" /
  "counted in calendar days at five working days to the week" are both stated and both implemented.

**Sweep back (compute invents no basis; the rule makes no empty promise).** Every binding in all five
`compute` lists was walked against its `compute_basis` sentence and no binding was found that
introduces a filter, a window, a threshold or a branch the rule does not state. In the other
direction, every normative sentence of each `rule` was mapped to at least one binding; no rule
sentence promises a treatment that `compute` never realises. Two wording notes that are **not**
equivalence failures, recorded as observations in `### findings` (F-3, F-4).

### action_binding_and_uuids

Check 3, over the whole charter and the one tool module.

**`(target_tool, computes)` uniqueness.** The five pairs listed in `### policy_conflict_scan` are
pairwise distinct in both components; no tool is claimed by two policies and no computed quantity is
claimed twice.

**Single business reading.** Each policy's `subject`, `base_policy_refs`, `target_tool`, the tool's
docstring and the terminal state it leaves agree on one reading:

- `apply_claim_coverage_f28c459e` → one `service_ledger` row, `event_type='service_coverage_applied'`,
  `amount` negated, `source_entry_id` set to the one priced line. Matches
  "taken off the order as a single credit recorded against one priced line".
- `confirm_authorized_ceiling_b1b9df84` → one `service_intake` row,
  `request_type='estimate_authorization'`, `request_status='customer_confirmed'`,
  `effective_date = today`. Matches "the authorisation itself is given by the customer on the
  workshop service request record".
- `charge_expedite_surcharge_af83d9eb` → one `service_ledger` row,
  `event_type='service_rush_fee_charged'`, `charge_code='rush_surcharge'`, positive.
- `confirm_stone_release_3a8d360e` → `ctx.update` on `service_orders` setting
  `stone_release_signed=True` and `declared_value=<carried_value>`.
- `charge_insured_shipping_16f801d8` → one `service_ledger` row,
  `event_type='service_shipping_charged'`, `charge_code='shipping_insured'`, positive.

No tool adds a confirmation, a review, a wait or a procedure the policy does not state; none reads
policy, aggregates history or judges eligibility (see `### findings` F-8 for the function-body
citation relied on per task).

**uuid8s.** `f28c459e`, `b1b9df84`, `af83d9eb`, `3a8d360e`, `16f801d8`. All five are 8 lowercase hex
characters, pairwise distinct, share no common prefix or suffix, are not sequential, are not
near-neighbours of one another, and none is a re-tailed copy of another. Each is frozen into its
function name and into the `resolved_by`/`policy.target_tool` references that point at it. No
evidence of batch derivation.

**Docstring silence about sequence.** No docstring names another tool or another policy. One
observation (F-6) about the shared Args boilerplate "read from the … lookup before the call" and
about `confirm_stone_release_3a8d360e`'s summary line; neither names another problem's tool or a
route, and neither is a red.

### prerequisite_graph

Check 7, over the whole graph.

`prerequisite` is filled in on all five policies (`[]` on `service_ext_claim_coverage_credit` and
`service_ext_carried_release_value`; one edge each on the other three). Three edges in all:

| blocked policy | problem | kind | gate | form | resolved_by |
| --- | --- | --- | --- | --- | --- |
| `service_ext_revised_authorization` | `service_ext_claim_coverage_credit` | `value_input` | `coverage_taken_off` | `state` | `apply_claim_coverage_f28c459e` |
| `service_ext_expedited_surcharge` | `service_ext_revised_authorization` | `value_input` | `ceiling` | `state` | `confirm_authorized_ceiling_b1b9df84` |
| `service_ext_insured_return_shipping` | `service_ext_carried_release_value` | `value_input` | `carried_value` | `state` | `confirm_stone_release_3a8d360e` |

- Every `problem` points at another policy id **in this file**; none points at a base policy and none
  at itself.
- **Acyclic.** The edge set is `{C→A, E→C, S→R}` over five distinct nodes; it forms two rooted chains
  (A-C-E of length 3 and R-S of length 2) with no back-edge. Verified by walking both chains.
- Each `policy_source` is verbatim locatable in **that policy's own** `rule` (machine-checked,
  whitespace-normalised: all three `True`), and none is restated in the depended-on policy's rule
  (all three `False`).
- `form` is `state` on all three; no edge carries `fallback_reason`, which is correct — the field is
  required exactly when `form: action`, and no edge is action-form. The state form's priority is
  therefore honoured throughout, and there is no `fallback_reason` to test.
- `condition` in each case names the handling-time record state that check 6 derives below, neither
  strengthened nor weakened relative to the sentence. No authoring-viewpoint phrasing
  ("in this task", "at the opening", "the current world") appears anywhere in the three
  `prerequisite` blocks.
- `resolved_by` equals the depended-on policy's own `target_tool` in all three cases
  (machine-checked, all `True`), and each tool's runnable body genuinely brings the gate about:
  `apply_claim_coverage…` creates the `service_coverage_applied` row that `coverage_taken_off` sums;
  `confirm_authorized_ceiling…` creates the `customer_confirmed` `service_intake` row that `ceiling`'s
  `LATEST(…)` selects; `confirm_stone_release…` writes `declared_value` on `service_orders`, which is
  literally what `carried_value: F('declared_value')` reads.
- `kind` matches `gate` on all three: every `gate` names a binding that genuinely exists in the
  blocked policy's own `compute` (machine-checked, all `True`), and all three are `value_input` —
  a value entering the calculation, not a status flip. No `state_gate` edge is declared, so there is
  no `state_gate` pointing at a non-gate.
- Per-tree shape: tree A has n=2 prerequisite problems with 2 `value_input` edges
  (floor `max(n−1,1)=1`); tree B has n=1 with 1 `value_input` edge (floor 1). Both within the
  one-to-three bound.
- At least one `owner=user` write per tree: `confirm_authorized_ceiling_b1b9df84` (`owner="user"`) in
  tree A; `confirm_stone_release_3a8d360e` (`owner="user"`) in tree B. Verified from the `@tool`
  decorators in `task_tools.py`.

### prerequisite_sentences

Check 6, over every edge of the charter. The four-point test on each sentence:

**Edge 1 — `service_ext_revised_authorization` → `service_ext_claim_coverage_credit`.**
Sentence: *"The ceiling is fixed only after every amount a protection claim answers for on the work
order stands recorded against the priced line it answers for."*
(1) It joins this policy's own result (*the ceiling is fixed*) to what it waits on with the ordering
connective *only after*. (2) Declared `form: state`; what it waits on is a record-visible state —
a credit entry standing on the work order against the priced line it answers for — named in the words
the tables use (`service_ledger` rows carry `source_entry_id` pointing at a priced line), with no
performer and no tool. (3) It names no tool, no policy id, no snake_case token and no row id.
(4) Its strength matches the edge's `condition` ("the work order carries a credit entry recording what
the protection claim answers for, pointed at the priced line it answers for") — neither broader nor
narrower; both are closed and both are about this one work order.
**The one write that brings the state about:** only `apply_claim_coverage_f28c459e` creates a
`service_ledger` row with `event_type='service_coverage_applied'`; no other tool in the module, and no
other policy of the charter, produces that state. Unique.
**Derivation in one reading:** the sentence says the ceiling waits on the claim amount standing
recorded against a priced line → the records show no `service_coverage_applied` row on the order →
the reader looks for the policy whose own rule describes producing that state and finds
`service_ext_claim_coverage_credit` ("taken off the order as a single credit recorded against one
priced line") → its `target_tool` is the resolving action. No second reading.

**Edge 2 — `service_ext_expedited_surcharge` → `service_ext_revised_authorization`.**
Sentence: *"The charge for expedited handling is priced only after the work order carries an
authorisation the customer has confirmed on the day the expedited handling is taken on."*
(1) Own result (*the charge for expedited handling is priced*) joined by *only after*. (2) `form: state`;
the waited-on thing is the record state "the work order carries an authorisation the customer has
confirmed" — and *customer has confirmed* is the table's own word (`service_intake.request_status`
takes the value `customer_confirmed`), plus a date qualifier ("on the day the expedited handling is
taken on") that maps to `effective_date`. No tool, no performer beyond the record's own vocabulary.
(3) No tool name, no policy id, no snake_case, no row id. (4) Matches the edge's `condition`
("the work order carries an authorisation the customer has confirmed whose effective date is the
handling date, with the ceiling agreed standing on it") at the same strength.
**The one write:** only `confirm_authorized_ceiling_b1b9df84` creates a `service_intake` row with
`request_status="customer_confirmed"`. Unique.
**Derivation:** the sentence says the surcharge waits on a confirmed authorisation effective today →
the records show the only confirmed authorisation effective on an older date → the reader finds the
policy whose own rule produces a confirmed ceiling (`service_ext_revised_authorization`, "The ceiling
a customer agrees for work already at the bench …") → its `target_tool`. One reading.

**Edge 3 — `service_ext_insured_return_shipping` → `service_ext_carried_release_value`.**
Sentence: *"The charge for sending the piece back is worked out only after the work order carries a
signed release naming the value the piece is held at."*
(1) Own result (*the charge for sending the piece back is worked out*) joined by *only after*.
(2) `form: state`; the waited-on thing is "the work order carries a signed release naming the value
the piece is held at" — `service_orders.stone_release_signed` plus `service_orders.declared_value`, in
the tables' own words, with no action, performer or tool. (3) Clean of tool names, ids and tokens.
(4) Matches the edge's `condition` ("the work order shows the release signed and carries the value the
piece is held at while the chain has it") exactly.
**The one write:** only `confirm_stone_release_3a8d360e` sets `stone_release_signed`. Unique.
**Derivation:** the sentence says the shipping charge waits on a signed release carrying the held-at
value → the records show `stone_release_signed: false` → the reader finds the policy whose own rule
describes the release and the value it names (`service_ext_carried_release_value`, "The release a
customer signs for a piece the bench has in hand names the value the chain carries that piece at")
→ its `target_tool`. One reading.

**Nothing else about the dependency in any rule.** No blocked rule carries a second wording of its
edge, another problem's tool name, another policy's id, or an aggregated chain; no depended-on rule
restates the blocked policy's sentence (machine-checked). No extended rule states a cross-problem
order that grounds no declared edge.

**Base rule sentences stating cross-problem orders.** `service_intake_admission` carries *"A piece
whose declared value exceeds the level's stone release threshold is worked on only once the customer
has signed the stone release"* and `service_authorization` carries *"No bench work begins above the
level's authorisation threshold until the customer has authorised it"*. Neither grounds an edge here:
both extended rules carry their own prerequisite sentence, so per check 6 these are recorded as
observations (F-5), not as red lights.

### override_declarations

Check 1's finding half, once over all five extended policies, sentence by sentence against each
`base_policy_refs` entry. Findings only — each affected task's file demonstrates the consequence
against its own world.

**`service_ext_claim_coverage_credit`** (refs `service_protection_coverage`, `service_estimate_pricing`,
`service_discounts_and_goodwill`).

| base sentence (`service_protection_coverage`) | extended handling |
| --- | --- |
| "Work carried out under an accepted protection claim is taken off the work order rather than billed to the customer, and the amount taken off is recorded against the claim it was answered under." | **Declared** in `overwrite` (first clause), replaced by the measurement formula. |
| "Coverage is applied only against the priced line it answers for, identified by the claim reference and the work order entry the claim was accepted for." | Extended applies the credit against a line chosen by the `line_of_record_selection` ladder, not against "the work order entry the claim was accepted for". **Not declared.** See finding **F-1**. |
| "Coverage is applied only at the service levels that admit protection work…" | Followed (inherited; no contrary sentence). |
| "Anything the coverage does not answer for stays on the work order… and the deductible under the plan is collected at the counter rather than netted off here." | Followed verbatim in the extended rule ("The deductible under the coverage is collected at the counter and is never taken off here"). |
| "Where no protection claim has been accepted the desk does not take the amount off in anticipation of one, because the claim decision is the protection desk's to make and not this one's." | Extended's own trigger sentence admits a claim "that stands filed against the covered piece **and has not been refused**". Filed-and-undecided is not accepted. **Not declared.** See finding **F-1**. |

Base sentences of `service_estimate_pricing` and `service_discounts_and_goodwill` that this policy
touches (the estimate charge booked under its own charge code; "never twice off the same priced line";
the member discount applied to labour before goodwill) are each followed — the extended rule's
net-of-amounts-already-taken-off measurement is consistent with "nothing is answered for twice".

**`service_ext_revised_authorization`** (refs `service_authorization`, `service_protection_coverage`,
`service_discounts_and_goodwill`, `service_estimate_pricing`).

| base sentence (`service_authorization`) | extended handling |
| --- | --- |
| "the authorisation names a ceiling the bench may not pass" | **Declared** in `overwrite`, replaced by "The ceiling is the bench total the customer is answering for plus the allowance, rounded to the nearest cent." |
| "No bench work begins above the level's authorisation threshold until the customer has authorised it" | Followed (inherited). |
| "Above the level's written authorisation threshold the authorisation is taken in writing on the workshop service request record, and a verbal agreement over the telephone does not stand in for it." | Followed — `confirm_authorized_ceiling_b1b9df84` writes to `service_intake`, the request record, and is `owner="user"`. |
| "Where the bench finds during the work that the ceiling will be passed, it stops and a fresh authorisation is taken for **the higher figure**…" | Extended's formula can produce a fresh ceiling **below** the standing one. Recorded as observation **F-2** (the extended trigger is `on_request`, not "the ceiling will be passed", so the two sentences do not in fact address the same situation). |
| "A deposit is taken before work starts at the levels that require one, calculated as the level's share of the authorised total, and it is credited against the final balance." | Followed (inherited; extended is silent and adds nothing contrary). |

**`service_ext_expedited_surcharge`** (refs `service_expedited_handling`, `service_authorization`,
`service_discounts_and_goodwill`).

| base sentence (`service_expedited_handling`) | extended handling |
| --- | --- |
| "Expedited handling shortens the promised date to the level's rush turnaround and carries the level's surcharge on the authorised bench total." | **Declared** in `overwrite`, replaced by the ceiling-based formula. |
| "Expedited handling is promised only where the workshop has at least the level's minimum notice in hours before the piece is needed, and a shorter notice is refused rather than promised and missed." | Followed (inherited). |
| "Where the level carries no surcharge for expedited handling, none is charged and the shorter turnaround is simply what that level runs at." | Extended's `rush_rate_pct` subtracts a step from `P('rush_surcharge_pct')`, which is `0.0` at Atelier White-Glove Service, so the rate can go negative there. Not declared; recorded as observation **F-7** (no task of this difficulty runs at that level, so no consequence is demonstrable). |
| "An out-of-hours finish carries the level's overtime charge on top of the surcharge, and it is **charged only where the bench was actually held open**." | Extended's `out_of_hours_share` ladder decides the overtime charge from turnaround overrun and the presence of a rework check, and never asks whether the bench was held open — no field of `service_orders` or `service_ledger` records that at all. **Not declared.** See finding **F-9**. |
| "Same-day service is offered only at the levels that run it…" | Not touched. |

**`service_ext_carried_release_value`** (refs `service_intake_admission`, `service_settlement`).

| base sentence (`service_intake_admission`) | extended handling |
| --- | --- |
| "the declared value is what the chain answers for while the piece is in its care" | **Declared** in `overwrite`, replaced by the papers-based carried value. |
| "A piece is taken in only at a service level whose ceiling on declared value covers what the piece is worth" | Inherited. The extended write raises `declared_value`, so the raised figure must still sit under `maximum_declared_value`; the extended rule's own cap is `care_custody_cover_cap`, a different (per level, equal-or-lower) figure. No conflict in the abstract; each task file checks its own world. |
| "A piece whose declared value exceeds the level's stone release threshold is worked on only once the customer has signed the stone release, and their saying they are happy for the bench to proceed is not the signed release." | Followed — the resolving tool is `owner="user"`. |
| "Antique and estate pieces are taken in only at the levels that admit restoration work…" | Not touched. |
| `service_settlement`: "the declared value shipped never exceeds the level's shipping insurance ceiling. Where the piece is shipped at a declared value above the ceiling the desk does not ship it…" | Inherited and **not** superseded. Because this policy can raise `declared_value`, the raised figure must be checked against `shipping_insurance_cap` in any task that then ships. Checked per task. |

**`service_ext_insured_return_shipping`** (refs `service_settlement`, `service_intake_admission`).

| base sentence (`service_settlement`) | extended handling |
| --- | --- |
| "Insured shipping is charged per leg at the level's rate" | **Declared** in `overwrite`, replaced by the stepped rate. |
| "the declared value shipped never exceeds the level's shipping insurance ceiling. Where the piece is shipped at a declared value above the ceiling the desk does not ship it and the customer collects in person instead." | Inherited; an eligibility gate the extended policy must respect. Checked per task. |
| "Payment is taken at the counter when the piece is collected, or earlier as a deposit…" / "A payment is taken against a work order only while that order stands in the workshop, ready for pickup, returned unrepaired or already delivered." | About payments, not shipping charges. Not touched. |
| "An updated appraisal is prepared with the finished work at the levels that include it…" | Not touched. |
| `service_intake_admission` sentences | Not touched by this policy. |

**Summary.** Three extended policies declare their override cleanly and completely
(`…revised_authorization`, `…carried_release_value`, `…insured_return_shipping`). Two carry
undeclared overrides: `service_ext_claim_coverage_credit` (**F-1**) and
`service_ext_expedited_surcharge` (**F-9**). Both bear on task 0 only.

### factor_ladders

The charter-global half of the factors relationship, over all five extended policies. Structure only.

**Counts and labels** (machine-checked):

| policy | factors | `parameter` | `method` | tiers per ladder | binding sets disjoint | `cross_difficulty` declared |
| --- | --- | --- | --- | --- | --- | --- |
| `service_ext_claim_coverage_credit` | 4 | 2 | 2 | 3,3,3,3 | yes | protection ×2 |
| `service_ext_revised_authorization` | 6 | 4 | 2 | 3,3,3,3,3,3 | yes | circle, protection |
| `service_ext_expedited_surcharge` | 5 | 4 | 1 | 3,3,3,3,3 | yes | circle ×2 |
| `service_ext_carried_release_value` | 4 | 3 | 1 | 3,3,3,3 | yes | protection |
| `service_ext_insured_return_shipping` | 6 | 5 | 1 | 3,3,3,3,3,3 | yes | protection, circle ×2 |

Every policy is inside the 4–6 bound with at least 2 `parameter` and at least 1 `method`. Every
ladder has exactly three tiers, the fall-through counted. No binding name appears in two factors of
the same policy.

**`decides` is an input, never `result`.** The fifteen+five `decides` targets are
`labour_base`, `coverage_share_pct`, `frequency_step_pct`, `line_cap`; `contingency_pct`,
`stale_step_pct`, `member_step_pct`, `covered_step_pct`, `bench_clock_days`, `uplifted_allowance`;
`rush_rate_pct`, `overtime_share_pct`, `relief_pct`, `relieved_amount`, `cap_share_pct`;
`basis_value`, `cover_step_pct`, `hold_step_pct`, `cap_share_pct`;
`value_band_step_pct`, `leg_step_pct`, `promise_step_pct`, `paperwork_step_pct`, `relief_pct`,
`relieved_charge`. None is `result`.

**Tiers pairwise disjoint as stated, and distinct in outcome.** Every ladder is written as
"condition A / condition B / otherwise" with A and B mutually exclusive by construction (either
"both hold" vs "exactly one of those two holds", or two contradictory predicates on one quantity, or
`>=2` vs `==1`). No two tiers of any one ladder select the same constant or the same method, with one
qualification recorded as observation **F-10** (`line_of_record_selection`, whose first two tiers
select different methods that coincide numerically on some worlds).

**Every tier stated in the `rule` and implemented in `compute`.** Walked factor by factor: for each of
the 25 factors, all three tiers (including the fall-through, which is always stated as a flat
declarative sentence in the baseline block of the rule — "The bench labour is measured as booked",
"No step is added for coverage held on the piece", "The relief the member is allowed is nothing",
"The ceiling share is the narrow ceiling share", and so on) appear as rule prose AND as branches of
the `decides` binding. No tier lives only in `compute`; no branch lacks a sentence.

**Labels honest.** Each `method` factor's tiers change the algorithm, not a number:
`labour_measurement_basis` (which rows the labour base nets against), `line_of_record_selection`
(which line the cap is measured on), `bench_clock_anchor` (which date the clock starts from),
`delay_allowance_uplift` (which multiple the allowance is taken at), `relief_application` ×2 (which
part of the charge the relief is applied to), `valuation_basis` (whether the report, the intake figure,
or the greater of the two is the basis). Each `parameter` factor's tiers substitute a rate, a share,
a step or a threshold-selected constant into an unchanged formula. No `method` tier names a
computation rule the charter does not state.

**`baseline` block per policy.** Each of the five policies carries a `baseline.rule` that is a
contiguous run of sentences of its own `rule` (verified substring-wise), naming the standard method
and the default value of every factor, and a `baseline.params` list. Every factor's fall-through tier
is exactly what that `baseline.rule` states for its input. Whether each `baseline.rule` yields a
definite number that differs from gold on a given world is a per-task fact and lives in each task's
`factor_weight`.

**Multi-source and cross-difficulty counts.** Multi-source factors (every tier other than the
fall-through a conjunction or disjunction of two or more conditions over distinct records) are present
in every policy: e.g. `delay_contingency_rate` (a `service_orders` date and a `service_ledger` row),
`bench_clock_anchor` (two different `service_ledger` event types), `member_standing_step` /
`member_relief_rate` / `member_shipping_relief_rate` (the `circle_memberships` holding and the
`circle_ledger` rows), `holding_exposure_step` (a `service_orders` date and a `service_ledger` row),
`carried_value_band_step` (a `service_orders` field and the `protection_plans` holding),
`evidenced_ceiling_share` (the `appraisal_orders` holding and the `protection_plans` holding).
`cross_difficulty` is declared on 8 factors: `protection` ×4, `circle` ×4. The categories read are
`protection`, `circle` and `appraisal`. Observation **F-11**: of these, only `protection` is the
claimed category of another difficulty in `blueprint.yaml`; `circle` and `appraisal` are product
categories no difficulty owns.

### findings

Charter-global findings, one by one. Each names the tasks it bears on so their files can pick up the
demonstration.

**F-1 — `SOURCE-POLICY RED` (undeclared override): extended admits a merely-filed claim where base
requires an accepted one.**
*Symptom.* Two clauses in force decide the same question — may coverage be taken off a work order
for a claim that stands filed and undecided — in opposite directions.
*Root cause.* `service_ext_claim_coverage_credit.overwrite` names exactly one superseded base
sentence, the one about *the amount* ("Work carried out under an accepted protection claim is taken
off the work order rather than billed to the customer…"), and its `replaced_by` is a pure measurement
formula that says nothing about eligibility. The two base sentences that fix *when* coverage may be
applied are therefore inherited in full, and the extended rule's own opening sentence weakens them.
*Evidence.*
- base, `service_protection_coverage.rule`: *"Where no protection claim has been accepted the desk
  does not take the amount off in anticipation of one, because the claim decision is the protection
  desk's to make and not this one's."*
- base, same rule: *"Coverage is applied only against the priced line it answers for, identified by
  the claim reference and the work order entry the claim was accepted for."*
- extended, `service_ext_claim_coverage_credit.rule`, opening: *"Where a work order runs under a
  protection claim that stands filed against the covered piece **and has not been refused**, what the
  coverage answers for is worked out on the bench labour standing priced on that work order…"*
- `service_ext_claim_coverage_credit.overwrite` (whole list): one entry, `base_policy:
  service_protection_coverage`, `superseded_clause: "Work carried out under an accepted protection
  claim is taken off the work order rather than billed to the customer"`.
*Demonstrated consequence.* Demonstrated against task 0's world in
`env/env_0001_fine_jewelry_retailer/audits/policy_task/workshop_service_desk/0.md`, `### policy_self_consistency`.
*Affected artifact and location.*
`env/env_0001_fine_jewelry_retailer/tasks/workshop_service_desk/service.extended.yaml`,
`extended_policies[0] service_ext_claim_coverage_credit` — `overwrite` (incomplete) and `rule`
(first sentence). Bears on **task 0**.
*Relation to previous revisions.* First revision; no prior audit of this difficulty exists.

**F-9 — `SOURCE-POLICY RED` (undeclared override): the out-of-hours charge is levied on conditions
base does not admit.**
*Symptom.* Base charges the level's overtime fee only where the bench was actually held open;
extended charges it (in full or at half) whenever the turnaround has been overrun and/or a rework
check stands, with no reference to the bench having been held open, and no record in the schema
evidences that fact at all.
*Root cause.* `service_ext_expedited_surcharge.overwrite` names only the first sentence of
`service_expedited_handling`; the out-of-hours sentence is untouched and inherited, while the
`out_of_hours_share` ladder replaces its condition wholesale.
*Evidence.*
- base, `service_expedited_handling.rule`: *"An out-of-hours finish carries the level's overtime
  charge on top of the surcharge, and it is **charged only where the bench was actually held open**."*
- extended, `service_ext_expedited_surcharge.rule`: *"Nothing is added for holding the bench open out
  of hours. Where the time since the customer authorised the work has run past the level's target
  turnaround and a check stands on the work order that found rework needed, the charge for holding
  the bench open out of hours is the level's own out-of-hours charge in full; where exactly one of
  those two holds, it is that charge at the part share."*
- extended, `compute`: `overtime_share_pct` reads only `bench_days`, `turnaround_target_business_days`
  and `rework_checks`; `overtime_amount: RND(P('overtime_expedite_fee') * overtime_share_pct / 100, 2)`.
- `service_ext_expedited_surcharge.overwrite` (whole list): one entry, `superseded_clause:
  "Expedited handling shortens the promised date to the level's rush turnaround and carries the
  level's surcharge on the authorised bench total."`
- `blueprint/db_schema.json` / the `events` block of `service.yaml`: no field of `service_orders` or
  `service_ledger` records that the bench was held open out of hours.
*Demonstrated consequence.* Demonstrated against task 0's world in
`env/env_0001_fine_jewelry_retailer/audits/policy_task/workshop_service_desk/0.md`, `### policy_self_consistency`.
*Affected artifact and location.*
`service.extended.yaml`, `extended_policies[2] service_ext_expedited_surcharge` — `overwrite`
(incomplete) and the `rule`/`compute` for `overtime_share_pct`. Bears on **task 0**.
*Relation to previous revisions.* First revision.

**F-2 — Observation: base's "fresh authorisation for the higher figure" versus a revised ceiling that
may fall.**
`service_authorization.rule` says *"Where the bench finds during the work that the ceiling will be
passed, it stops and a fresh authorisation is taken for the higher figure"*. The extended formula can
produce a fresh ceiling lower than the one standing. The two are not in fact addressing the same
situation — the extended policy's `trigger` is `on_request`, not "the ceiling will be passed" — so no
contradictory conclusion in one situation can be demonstrated, and this is recorded as an observation
rather than an undeclared override. Bears on task 0.

**F-3 — Observation: `service_ext_expedited_surcharge` states the ceiling's provenance twice.**
The rule opens *"The charge for expedited handling is worked out on the ceiling standing on the most
recent authorisation the customer has confirmed on the work order"* and later carries the prerequisite
sentence *"The charge for expedited handling is priced only after the work order carries an
authorisation the customer has confirmed on the day the expedited handling is taken on."* The first
is the `compute_basis` for the `ceiling` binding and carries no ordering connective, so it is not a
second wording of the dependency; but a reader meets the same record twice. No consequence
demonstrable. Bears on task 0.

**F-4 — Observation: `service_ext_insured_return_shipping` names "a finished piece" in a rule whose
factors presuppose an unfinished one.**
The rule opens *"Sending a finished piece back to its owner insured is charged on…"* while the
`promise_proximity_step` ladder reads `days_to_promise = DAYS(NOW, F('promised_date'))` and tiers on
the promised date falling inside the rush or target turnaround *counted from the handling date* —
which is only meaningful before the bench has finished. The only stated timing gate is the
prerequisite sentence's "only after … a signed release", and the trigger is `on_request`, so the
dominant reading is act-now; but the opening phrase invites a "wait until it is finished" reading.
No second *value* is produced by that reading, so it is an observation. Bears on task 1.

**F-5 — Observation: base rule sentences state cross-problem orders that ground no declared edge.**
`service_intake_admission.rule`: *"A piece whose declared value exceeds the level's stone release
threshold is worked on only once the customer has signed the stone release…"*;
`service_authorization.rule`: *"No bench work begins above the level's authorisation threshold until
the customer has authorised it."* Neither grounds an edge — both blocked extended policies carry
their own prerequisite sentence — so per check 6 these are observations. Bears on both tasks.

**F-6 — Observation: ordering words in tool docstrings.**
Every task tool's `Args` block carries the boilerplate "read from the work order lookup **before** the
call" / "read from the customer profile lookup **before** the call", and
`confirm_stone_release_3a8d360e`'s summary line reads *"Sign in person the release the workshop needs
**before** it handles a piece…"*. None names another tool, another policy, or another problem's route;
the first is about where an argument is sourced and the second restates that tool's own gate from
`service_intake_admission`. Recorded as an observation, not as a check-3 failure. Bears on both tasks.

**F-7 — Observation: `rush_rate_pct` can go negative at Atelier White-Glove Service.**
`P('rush_surcharge_pct')` is `0.0` at that level, and `recovery_rush_rate_step`'s first two tiers
subtract `K('recovery_step_pct')=8` or `K('standing_step_pct')=4` from it, giving −8 or −4 — while
base `service_expedited_handling` says *"Where the level carries no surcharge for expedited handling,
none is charged."* Neither task of this difficulty runs at that level, so no consequence is
demonstrable on any world here. Bears on neither task's score.

**F-8 — The tool layer judges no prerequisite (charter-global fact, cited per task).**
Read function body by function body in `task_tools.py`: `apply_claim_coverage_f28c459e` calls
`ctx.make_id` then `ctx.create` and returns; `confirm_authorized_ceiling_b1b9df84` calls `ctx.make_id`
then `ctx.create` and returns; `charge_expedite_surcharge_af83d9eb` likewise; `confirm_stone_release_3a8d360e`
calls `ctx.update` and returns; `charge_insured_shipping_16f801d8` calls `ctx.make_id` then `ctx.create`
and returns. There is no branch, no raise, no status read, no lookup of another table, and no
conditional string in any of the five. No tool refuses a call, errors, or hints while a prerequisite
stands unresolved.

**F-10 — Observation: `line_of_record_selection`'s first two tiers can coincide numerically.**
Tier 1 selects `largest_line = MAX(service_ledger.amount, event_type='service_labor_charged')`;
tier 2 selects `largest_bench_line = MAX(…, charge_code='bench_labor')`. As methods they differ (all
labour lines versus only those coded `bench_labor`), which satisfies the distinct-outcome test as
stated; but on any world whose largest labour line happens to be coded `bench_labor` the two tiers
return the same number, so the condition that separates them — whether a check found rework needed —
does no work there. A separate concern about the same ladder: its fall-through ("the most recent bench
labour line") is systematically the least favourable of the three options, which is the shape a
straw-man baseline takes; it is nevertheless a coherent reading of "the line the claim was accepted
for", so it is recorded here as an observation rather than a red. Bears on task 0.

**F-11 — Observation: two `cross_difficulty` labels name categories no difficulty owns.**
`blueprint.yaml` declares five difficulties claiming the categories `financing`, `protection`,
`service`, `custom` and `tradein`. Four factors declare `cross_difficulty: circle`
(`member_standing_step`, `member_relief_rate`, `relief_application` in `…expedited_surcharge`,
`member_shipping_relief_rate` and `relief_application` in `…insured_return_shipping`), and
`evidenced_ceiling_share` and `travelling_papers_step` read `appraisal` while declaring
`cross_difficulty: null`. `circle` and `appraisal` are genuine product categories of the scenario with
their own holding and ledger tables, but neither is any difficulty's claimed category, so a factor
labelled `cross_difficulty: circle` does not in fact read *another difficulty's* records. Both tasks
independently meet the "at least one cross-difficulty factor" floor through `protection`, which **is**
`protection_claims_desk`'s claimed category, so no consequence follows. Bears on both tasks.

**F-12 — Observation: `bench_clock_anchor`'s discriminating conjunct is thin.**
Both of its non-fall-through tiers require "a check that found rework needed stands on the work
order"; what separates them is whether "amounts have already been taken off it". Whether a goodwill
or member credit has been given has no evident bearing on *when the clock measuring time at the bench
starts*, which is what the factor decides. A charitable reading is available (the chain stops counting
the period before its own recovery gesture), and the conjunct does draw on a second, distinct record,
so it is recorded as an observation naming the concern rather than as an unreal-ladder red. Bears on
task 0.

## closing_checklist

Written after both tasks' `source_gt_comparison` sections were complete. **This difficulty is NOT
closed out.** Step 4 permits closure only once all M tasks carry a PASS on all four relationships;
task 0 does not. The checklist is nevertheless recorded item by item, so that the items that do hold
are on record and the two that do not are named precisely.

| Step 4 item | status |
| --- | --- |
| The per-task audit files correspond one-to-one with the tasks (`0.md`, `1.md`) and `_difficulty.md` sits alongside them; old revisions traceable (none — first revision); every comparison section carries a verdict | **files and verdicts present, but task 0's verdict is not a PASS** — see `0.md` `## source_gt_comparison` |
| This difficulty's extended policies are fully covered and the M tasks' scopes are pairwise disjoint, each scope spanning the whole problem tree | **holds.** Task 0 claims `{service_ext_claim_coverage_credit, service_ext_revised_authorization, service_ext_expedited_surcharge}`; task 1 claims `{service_ext_carried_release_value, service_ext_insured_return_shipping}`. Disjoint; union = all five |
| Task tools and GT are closed | **holds.** `charter_scope.task_tools` of task 0 is the three tools its three writes call; of task 1, the two its two writes call; the union is the five tools of `task_tools.py`, with none unused and none shared between tasks |
| Each task tool uses an independently generated, frozen uuid8 | **holds** — `### action_binding_and_uuids` |
| Every task's problem tree has one to three prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 problem resolved by an `owner=user` tool, and no cycle | **holds.** Task 0: n=2, 2 `value_input`, `confirm_authorized_ceiling_b1b9df84` (`owner="user"`). Task 1: n=1, 1 `value_input`, `confirm_stone_release_3a8d360e` (`owner="user"`). Both acyclic |
| The `prerequisite` edges of the whole difficulty together are still a DAG, with no cycle created by cross-task references | **holds.** Three edges over five nodes forming two disjoint rooted chains; no edge crosses between the two trees, so no cross-task cycle is possible |
| Every computation declares a self-sufficient baseline and 4–6 factors (≥2 `parameter`, ≥1 `method`; per task ≥1 multi-source and ≥1 cross-difficulty), every ladder ≥3 tiers stated in full in its rule, tiers distinct in outcome, conditions and outcomes ones the line of business actually holds | **holds structurally** (`### factor_ladders`) with observations **F-10**, **F-11** and **F-12** |
| Every factor proved to bear weight on its task's world against an honest baseline, with the baseline alone giving a definite number different from gold | **holds.** All 15 factors of task 0 and all 10 of task 1 bear weight; whole-baseline fall-backs 101.40 / 1031.05 / 355.64 and 6800.00 / 55.00, each definite and each different from gold. One one-cent divergence in a counterfactual figure, observation **T0-4** in `0.md` |
| This difficulty's instantiation-stage gates re-run once on the final form | **not applicable yet.** The gate block supplied with the brief is cited in `## charter_global_frozen`; there is no final form to re-run it on while task 0 stands RED, and per Step 0 the auditor does not run the gates itself |

**Why closure is withheld.** Three red lights, all on task 0:

1. `SOURCE-POLICY RED` — finding **F-1**, demonstrated as `0.md` **T0-1**: the charter applies
   protection coverage on a claim that stands filed and undecided, while an inherited and
   unsuperseded base sentence forbids taking the amount off before a claim is accepted. Two
   defensible readings, and all three of task 0's scored parameters move between them.
2. `SOURCE-POLICY RED` — finding **F-9**, demonstrated as `0.md` **T0-2**: the out-of-hours charge is
   levied on turnaround overrun and a rework check, where base levies it only where the bench was
   actually held open — a fact no field in the schema records. Two defensible values for
   `surcharge_amount`.
3. `SOURCE-CHAIN RED` — `0.md` **T0-3**: the closure's demonstration that the
   `revised_authorization → claim_coverage_credit` edge bears weight asserts figures that are not what
   the world gives and that contradict one another. The edge does bear weight, but the proof the
   artifact submits for it does not hold.

Task 1 carries PASS on all four relationships.

**Per-task verdicts.**

| task | policy self-consistency | problem tree | factors bear weight | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | **SOURCE-POLICY RED** | **SOURCE-CHAIN RED** | PASS | PASS | **SOURCE-POLICY RED / SOURCE-CHAIN RED** |
| 1 | PASS | PASS | PASS | PASS | **PASS** |

## revision_2

### charter_global_frozen (round 2)

- Re-audit round 2, 2026-09-17, same auditor. Every `revision_1` text above is preserved untouched.
- Inputs and hashes: `service.extended.yaml` `976fd37e66d26f1d` (169908 bytes; round 1 `5a6301bdf93243ce`);
  `task_tools.py` `71f4ffa837da5e6d` (13511 bytes; round 1 `da81aace2a821ece`). **Both moved**, so every
  charter-global section is re-derived in full below rather than carried forward.
- Masked views `0.json` `f0dc75c3e0a0b027` and `1.json` `0a862c54c36c0f6c` — byte-identical to round 1;
  key enumeration again returns exactly `['frozen_time','initial_state','user_scenario']`.
- Entry conditions: the round-2 gate block was supplied with the brief (EXTENDED / TASK-TOOL-CONTRACT /
  REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK; `check_traceability` excluded). Cited, not re-run.
- Blindness in a re-audit: this auditor read round-1 GT in round 1, so the round-2 derivations cannot be
  blind to round-1 values. They are blind to round-2 GT — this whole section and both tasks' round-2
  freeze sections were on disk before any round-2 field outside the whitelist was read — and they are
  recomputed from the round-2 charter and the seeds, not copied. No search touched `tasks/*/tasks/*.json`.
- The base copy is still verbatim identical to `blueprint/products/service.yaml` (zero key differences).

### policy_conflict_scan (round 2)

Subjects, target tools, computed quantities, triggers, time anchors, calendar conversion, cross-category
`as: branch` reads and tool write targets are all as in round 1 (re-verified from the round-2 file):
five pairwise-distinct `(target_tool, computes)` pairs; two disjoint trees whose union is all five
policies; tool module still writes only `service_ledger` ×3, `service_intake` ×1, `service_orders` ×1.
Scope exclusivity and joint completeness over M=2 hold. No conflicting conclusion between any two
clauses now in force was found — the two found in round 1 are closed (below).

### rule_compute_equivalence (round 2)

Re-run sentence by sentence on the round-2 file. Every `compute` binding of every policy has a
`compute_basis` entry, every `compute_basis` sentence is a sentence of that policy's own `rule`
(machine-checked at sentence granularity: zero misses in all five policies), and every sentence of each
`baseline.rule` is in the `rule`. Changes since round 1 and their equivalence:
- `service_ext_expedited_surcharge.rush_rate_pct` now reads `MX(0, …)`; the rule carries the matching
  sentence *"Where the level carries no rush share, or the step taken off the rush share would take it
  below nothing, the rush rate is nothing."* — a floor stated on both faces. The ladder tiers of
  `recovery_rush_rate_step` are unchanged and the floor sits outside them as a clamp, which is the
  cap/floor case, not a hidden tier.
- `service_ext_expedited_surcharge` rule gained *"The bench is held open out of hours … and the charge
  for holding it open is decided on those two records alone."* It names the same two records
  (`bench_days` vs target turnaround; a `rework_required` check) that `overtime_share_pct` reads; compute
  is untouched and still implements exactly the three-tier ladder.
- `service_ext_claim_coverage_credit` rule gained the eligibility sentence *"…has been sent to the
  workshop under that work order's reference…"* and *"The credit is recorded against the priced line it
  is measured against, and that line is fixed by the standing of the work order rather than named by the
  protection desk."* Neither is a computed quantity; the first rests on
  `protection_ledger.service_order_reference`, the second restates what `line_cap`/`source_entry_id`
  already do. Compute untouched.
- `service_ext_insured_return_shipping`: "a finished piece" → "a piece at the bench" in `rule`,
  `baseline.rule`, `compute_basis.base_charge` and `overwrite.replaced_by`, all four aligned.
Sweep back: no binding introduces a basis the rule lacks; no rule sentence promises a treatment compute
never realises.

### action_binding_and_uuids (round 2)

Same five pairs, same five uuid8s (`f28c459e`, `b1b9df84`, `af83d9eb`, `3a8d360e`, `16f801d8`) —
unchanged, distinct, non-sequential. Tool bodies re-read line by line: each is still `make_id` →
`create` → `return` (or `update` → `return`), with no branch, raise, status read or `ctx.find`.
Docstrings: every `Args` line now reads *"as returned by the … lookup"*; the `confirm_stone_release_3a8d360e`
summary now reads *"the release the workshop needs for handling a piece"*. No `before`/`after`/`first`/
`prior` remains in any tool docstring. The only surviving ordering word is in the **module** docstring
(*"works the figure out from the published rules and the records first, then passes it in"*), which
describes no tool's position relative to another — observation R2-O2.

### prerequisite_graph and prerequisite_sentences (round 2)

Three edges, unchanged in `problem`, `kind`, `gate`, `form`, `condition`, `resolved_by` and
`policy_source`. Machine-checked on the round-2 file: each `policy_source` verbatim in its own rule
(3/3 `True`), absent from the depended-on rule (3/3 `False`), `resolved_by` equals the depended-on
`target_tool` (3/3), each `gate` is a compute binding of the blocked policy (3/3), all `form: state`,
no `fallback_reason` (correct). Acyclic: two disjoint chains. The four-point test and the one-write
derivations of round 1 stand word for word, because none of the three sentences, none of the three
`condition`s and none of the resolving tools' effects changed. The new eligibility sentences added to
`…claim_coverage_credit` and `…expedited_surcharge` carry no ordering connective and name no other
problem's result, so they ground no edge and restate none.

### override_declarations (round 2)

Re-swept sentence by sentence against every `base_policy_refs` entry.

`service_ext_claim_coverage_credit` — `overwrite` now has **three** entries against
`service_protection_coverage`: (1) the amount sentence (as before); (2) *"Where no protection claim has
been accepted the desk does not take the amount off in anticipation of one…"* → replaced by the
filed-and-sent-under-this-reference-and-not-refused trigger; (3) *"Coverage is applied only against the
priced line it answers for, identified by the claim reference and the work order entry the claim was
accepted for."* → replaced by "recorded against the priced line it is measured against … fixed by the
standing of the work order". These are exactly the two sentences round-1 **F-1** named. The remaining
base sentences (levels that admit protection work; the deductible collected at the counter; "recorded
against the claim it was answered under") are followed. Merged semantics after replacement: coverage is
applied when a claim stands filed against the piece, carries this work order's reference, and has not
been refused; the line is the one the ladder selects. One reading. **F-1 closed.**

`service_ext_expedited_surcharge` — `overwrite` now has **three** entries against
`service_expedited_handling`: (1) the promised-date/surcharge sentence (as before); (2) *"An out-of-hours
finish carries the level's overtime charge on top of the surcharge, and it is charged only where the
bench was actually held open."* → replaced by the two-records sentence; (3) *"Where the level carries no
surcharge for expedited handling, none is charged…"* → replaced by the floor sentence. (2) is exactly the
sentence round-1 **F-9** named; (3) is round-1 **F-7**. Minimum-notice and same-day sentences remain
inherited and untouched. Merged semantics unique. **F-9 closed; F-7 closed.**

`service_ext_revised_authorization`, `service_ext_carried_release_value`,
`service_ext_insured_return_shipping` — `overwrite` unchanged and still complete; the base sentences each
inherits are the same as in round 1 and are followed. The `service_settlement` shipping-insurance ceiling
remains inherited and live for task 1 (re-checked there).

No new undeclared override was found.

### factor_ladders (round 2)

Counts unchanged: 4/6/5/4/6 factors; `parameter`/`method` 2/2, 4/2, 4/1, 3/1, 5/1; every ladder three
tiers; binding sets disjoint; every `decides` a compute binding; every tier in both `rule` and `compute`;
labels honest; every fall-through equals its `baseline`. **Changed:** `cross_difficulty` now reads
`protection` on exactly five factors (`coverage_carried_share`, `claim_frequency_step`,
`covered_work_step`, `coverage_cover_step`, `carried_value_band_step`) and `null` on all circle- and
appraisal-reading factors — the round-1 **F-11** relabelling. Each tree still carries ≥1
`protection`-deciding factor (tree A: three; tree B: two), so the floor is met through a category that a
difficulty (`protection_claims_desk`) actually owns. **F-11 closed.** One new structural note on the
floor: at a level whose `rush_surcharge_pct` is 0, all three tiers of `recovery_rush_rate_step` now
resolve to 0 — the same value — so on such a world that ladder would be unreal; no task of this
difficulty runs at such a level, so it is observation R2-O1, not a red.

### findings (round 2)

Round-1 REDs, item by item on the artifacts as they now stand:

- **F-1 / T0-1 — CLOSED.** Both weakened base sentences are named in `overwrite` with a `replaced_by`
  that is verbatim in the rule; the trigger names a record-visible state
  (`protection_ledger.service_order_reference` on the filed row) that task 0's seed carries
  (`7bdd809f-…`, `service_order_reference: "WO-441907"`, no settlement, no denial). Only one reading
  remains.
- **F-9 / T0-2 — CLOSED.** The out-of-hours base sentence is named and replaced; the replacement names
  the two records the ladder reads and nothing else. Compute untouched, so the scored value is unmoved.
- **F-7 — CLOSED** (was an observation): floor stated in rule and compute, base sentence declared.
- **F-11 — CLOSED** (was an observation): relabelled; floors still met through `protection`.
- **F-6 — CLOSED** (was an observation): no ordering word remains in any tool docstring.
- **F-4 — CLOSED** (was an observation): "finished" → "at the bench", aligned on all four faces.
- **T0-3** and **T0-4** are task-level and are settled in `0.md` `## revision_2` after the reveal.
- **F-2, F-3, F-5, F-8, F-10, F-12** — unchanged, remain observations; re-read on the round-2 file and
  still accurate (F-8's function-body description re-verified).

New observations this round (none is a red; none carries a demonstrable consequence):

- **R2-O1** — `recovery_rush_rate_step` collapses to a single value (0) at any level with
  `rush_surcharge_pct: 0.0` (Atelier White-Glove Service) because of the new floor. Charter-global
  latent shape; no task here reaches it.
- **R2-O2** — the module docstring of `task_tools.py` still reads "…first, then passes it in". Not a tool
  docstring, names no tool, states no inter-tool order.
- **R2-O3** — `service_ext_claim_coverage_credit.cross_category[protection].reads` lists `status`,
  `claims_settled_count`, `remaining_benefit_allowance`, `protection_ledger.event_type` but not
  `protection_ledger.service_order_reference`, which the new trigger sentence ("sent to the workshop
  under that work order's reference") now rests on. The EXTENDED gate checks compute bindings, not
  eligibility prose, so it passed. The field is reachable through `find_protection_ledger`, so no
  reachability consequence follows; the declaration is merely incomplete.

### closing_checklist (round 2)

Written after both tasks' round-2 comparison sections were complete. **Both tasks PASS on all four
relationships; the difficulty is closed out on the round-2 artifacts.**

| Step 4 item | status |
| --- | --- |
| Per-task files one-to-one with tasks, `_difficulty.md` alongside, `revision_1` preserved untouched under `revision_2`, every comparison section carrying a verdict | holds — both round-2 comparisons carry PASS |
| Extended policies fully covered; task scopes pairwise disjoint, each spanning its whole tree | holds — unchanged from round 1 (`{coverage, authorisation, surcharge}` / `{release, shipping}`) |
| Task tools and GT closed; each tool an independently generated, frozen uuid8 | holds — five tools, five uuid8s unchanged, none shared, none unused |
| Every tree 1–3 prerequisite problems, ≥ max(n−1,1) `value_input`, ≥1 `owner=user` write, no cycle; whole-difficulty graph a DAG | holds — n=2/2 `value_input`/`confirm_authorized_ceiling_b1b9df84`; n=1/1/`confirm_stone_release_3a8d360e`; two disjoint chains |
| Self-sufficient baselines and 4–6 factors per computation (≥2 `parameter`, ≥1 `method`; per task ≥1 multi-source, ≥1 cross-difficulty), ladders of ≥3 tiers stated in full, distinct in outcome, realistic | holds structurally (`## revision_2` `### factor_ladders`); cross-difficulty now genuinely `protection` on every labelled factor; observations F-10, F-12, R2-O1 |
| Every factor proved load-bearing against an honest baseline; baseline alone definite and ≠ gold | holds — 15 + 10 factors; fall-backs 101.40 / 1031.05 / 355.64 and 6800.00 / 55.00; one one-cent tie observation (T0-4) |
| Instantiation-stage gates re-run once on the final form | the coordinator's round-2 gate block on these exact hashes is cited in `### charter_global_frozen (round 2)`; per Step 0 the auditor does not run them |

**Per-task verdicts, round 2.**

| task | policy self-consistency | problem tree | factors bear weight | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | **PASS** |
| 1 | PASS | PASS | PASS | PASS | **PASS** |

Open observations carried (none a red, none with a demonstrable consequence): F-2, F-3, F-5, F-8,
F-10, F-12, T0-4, T1-1, T1-3, R2-O1, R2-O2, R2-O3, R2-T0-a, R2-T1-a, R2-T1-b.

## revision_3

### charter_global_frozen (round 3)

- Re-audit round 3, 2026-09-17, same auditor. All `revision_1` and `revision_2` text above is preserved untouched.
- Inputs: `service.extended.yaml` `001fe8b097c2ea6e` (170691 bytes; round 2 `976fd37e66d26f1d`) — **moved**;
  `task_tools.py` `71f4ffa837da5e6d` — **unchanged from round 2**.
- Re-derivation discipline, per the skill's rule about moved inputs: the charter moved, so every
  charter-global section is re-checked against the round-3 file. The tool module did not move, so
  `### action_binding_and_uuids`'s tool half and finding **F-8** are carried forward by reference on the
  strength of the identical hash, and only the `(target_tool, computes)` half is re-run.
- Masked views `f0dc75c3e0a0b027` / `0a862c54c36c0f6c` — byte-identical to rounds 1 and 2; key
  enumeration again returns exactly `['frozen_time','initial_state','user_scenario']`. Worlds, personas
  and `frozen_time` are unchanged for a third round.
- Entry conditions: the round-3 gate block came with the brief, this time including TRACEABILITY
  (0.json 23 copied / 0 missing; 1.json 20 / 0). Cited, not re-run.
- Blindness: this auditor has seen rounds 1 and 2 GT. The round-3 derivations below were recomputed from
  the round-3 charter on the unchanged seeds and were on disk before any round-3 field outside the
  whitelist was read. No search touched `tasks/*/tasks/*.json`.
- Base copy still verbatim identical to `blueprint/products/service.yaml` (zero key differences).

### what moved, exactly

A whole-file diff of the round-3 charter against the round-2 dump shows changes in **one policy only**,
`service_ext_revised_authorization`, at four places:

1. `rule` — "every priced line standing on the work order" → "every **bench labour** line standing priced
   on the work order"; and one new sentence inserted after "The allowance is taken as it stands.":
   *"Whatever multiple the allowance is taken at, the figure it comes to is rounded to the nearest cent
   before it is added to the bench total."*
2. `baseline.rule` — the same two changes.
3. `factors[delay_allowance_uplift].ladder` — each of the three `method` strings gains
   ", and the figure it comes to is rounded to the nearest cent before it is added to the bench total".
4. `compute_basis` — `booked_charges` and `net_bench_total` quote the narrowed sentence;
   `uplifted_allowance` now quotes the new rounding sentence.

`compute` is byte-identical. `overwrite`, `prerequisite`, `params`, every other policy, and the whole
base section are byte-identical. Tool module byte-identical.

### policy_conflict_scan / action_binding_and_uuids / prerequisite_graph / prerequisite_sentences (round 3)

Re-run on the round-3 file; all as at revision 2. Five pairwise-distinct `(target_tool, computes)` pairs;
two disjoint trees covering all five policies; scopes disjoint and jointly complete. Three prerequisite
edges, each `policy_source` verbatim in its own rule (3/3) and absent from the depended-on rule (3/3),
`resolved_by` = depended-on `target_tool` (3/3), each `gate` a compute binding of the blocked policy
(3/3), all `form: state`, no `fallback_reason`. Acyclic. The edge out of
`service_ext_revised_authorization` is untouched — its `policy_source` sentence sits before the edited
region and is still verbatim. uuid8s unchanged and still distinct, non-sequential, unshared.

### rule_compute_equivalence (round 3) — and a correction to revisions 1 and 2

**Correction first, because it is mine.** At `revision_1` `### rule_compute_equivalence` I wrote, under
"Rounding mode and point", that rounding points "are stated where they are intermediate (the allowance,
the **uplifted allowance**, the base charge)", and I carried that forward at revision 2. That was
**false** for `uplifted_allowance`: through rounds 1 and 2 the rounding of the uplifted figure lived only
in the `compute` binding `RND(allowance * K('…_uplift'), 2)` and appeared in neither `rule` nor
`baseline.rule`. I asserted the equivalence held where it did not, and both of my earlier
`rule_compute_equivalence` PASSes were wrong on that point. The render-layer audit found it; I did not.
Weighed as evidence rather than inherited, its demonstration reproduces independently:
a reader of the round-2 prose computes the allowance 359.90, takes it a quarter as much again to
449.875, and — the prose naming no rounding at that moment — adds it whole, reaching
`RND(972.69 + 449.875)` = a tie at 1422.565, which resolves to **1422.56** under half-to-even (the mode
the materials name) and **1422.57** under half-up. The source gives 1422.57. Carried into the third
write, 1422.56 yields `base_amount` 312.96, `relieved` 448.16, `cap` 569.02 and a surcharge of
**448.16** against 448.17. Two scored parameters of task 0 were underdetermined by rule + compute_basis
+ baseline.rule. Under the four relationships that is `SOURCE-POLICY RED` (rule/compute equivalence
broken in the rule→compute direction: the rule made an incomplete promise and only compute carried the
missing moment), and it is recorded retrospectively as **F-13** below.

**Is F-13 closed on the round-3 charter?** Yes.

- The new sentence is present in `rule` and in `baseline.rule` (both checked verbatim), and is quoted in
  `compute_basis[uplifted_allowance]` (checked verbatim). All three faces now carry it.
- It is **general**, not a restatement of this task's arithmetic: *"Whatever multiple the allowance is
  taken at, the figure it comes to is rounded to the nearest cent before it is added to the bench
  total."* It contains no digit, names no tier, no rate and no world; "whatever multiple" quantifies over
  all three tiers including the fall-through multiple of one, and "before it is added to the bench total"
  is what pins the moment rather than merely the mode.
- All three tier `method` strings of `delay_allowance_uplift` now carry the same clause, so the factor
  document that renders from any one tier carries the moment too — which is where the render layer lost it.
- **One reading survives.** Allowance 359.90 → taken a quarter as much again → 449.875 → rounded at that
  moment → 449.88 under half-to-even (hundredths digit 7 is odd, so it rises), under half-up, and under
  float rounding alike (the double nearest 449.875 is exactly 449.875) → ceiling
  `RND(972.69 + 449.88)` = 1422.57 with no tie left to resolve. The rival 1422.565 reading is no longer
  admissible, because the prose now forbids adding the unrounded product.
- Sentence-level machine check across all five policies: every `compute_basis` sentence is a sentence of
  its own policy's `rule` (zero misses) and every `baseline.rule` sentence is in the `rule` (zero misses).
  The fall-through tier "the allowance is taken as it stands" is in the rule (as a sentence-initial
  capital, hence the case-insensitive match).

**The narrowed bench-total domain.** `booked_charges` is
`SUM('service_ledger','amount', event_type='service_labor_charged')`. The base `events` block defines
`service_labor_charged` as "bench labour is priced onto the work order". So "every bench labour line
standing priced on the work order" now names exactly the event family the binding sums, where "every
priced line" named a strictly larger set (it would have taken in `service_rush_fee_charged`,
`service_shipping_charged` and any storage or cancellation line). The narrowing is a fix in the
rule→compute direction, not a new gap:

- It creates no gap in the business sense. The quantity is a ceiling on **bench work** —
  base `service_authorization` says "No bench work begins above the level's authorisation threshold until
  the customer has authorised it, and the authorisation names a ceiling the bench may not pass" — so
  resting it on bench labour is what the base policy governs. A rush fee, a postage line, a storage or a
  cancellation charge is not bench work the bench could overrun, and each is separately priced by its own
  policy and separately agreed; task 0's own gold sequence prices the rush fee *after* the ceiling is
  fixed, which is only coherent on the narrow reading.
- It moved no figure. On task 0's order every positive line is a labour line
  (1924.00 `bench_labor`, 296.40 `prong_rebuild`, 435.50 `stone_setting`, 101.40 `bench_labor`; no
  non-labour positive line stands on the order), so the broad and narrow readings both give 2757.30. The
  reworker's claim that the two coincided is verified, not accepted.
- Two residues are recorded as observations, neither with a consequence on either task: **R3-O1**
  (an `estimate_fee`-coded line sits inside the `service_labor_charged` family, so on a world carrying
  one the prose and the binding could part company) and **R3-O2** (the additions are now labour-only
  while the subtractions — amounts taken off, coverage — remain order-wide).

### factor_ladders (round 3)

Counts, labels, tier counts, binding disjointness, `decides`-is-an-input and `cross_difficulty` are all
exactly as at revision 2 (4/6/5/4/6 factors; 2·2, 4·2, 4·1, 3·1, 5·1 parameter·method; every ladder three
tiers; `protection` on five factors, `null` elsewhere; each tree carrying ≥1 `protection` factor). The
only factor text that moved is `delay_allowance_uplift`'s three method strings, which gained the rounding
clause; the tiers still select three distinct multiples (1.5 / 1.25 / 1.0), so the ladder stays real and
the added clause — being identical across all three — discriminates nothing and cannot be a hidden tier.
Its `baseline` is unchanged and still equals the fall-through.

### findings (round 3)

- **F-13 — `SOURCE-POLICY RED` at revisions 1–2, now CLOSED.** Rule/compute equivalence broken in the
  rule→compute direction on `service_ext_revised_authorization.uplifted_allowance`: the rounding moment
  lived only in `compute`, leaving `authorized_ceiling` and, through it, `surcharge_amount`
  underdetermined for task 0 (1422.56/448.16 against 1422.57/448.17). Missed by this auditor at both
  earlier revisions and recorded here retrospectively; found by the render-layer audit as its B-1.
  Closed on the round-3 charter by a general sentence carried in `rule`, `baseline.rule`,
  `compute_basis` and all three tier strings, with `compute` untouched. Bears on **task 0**.
- **F-14 — Observation: the bench-total domain.** Narrowed from "every priced line" to "every bench
  labour line standing priced on the work order", matching the binding. No figure moved on either task;
  no business gap created; residues **R3-O1** and **R3-O2** above.
- **The three deferred tensions, judged against the base-freeze rule rather than on the reworker's
  justification.** The rule is that the base section is verbatim and may not be rewritten, and that an
  override holds only by being declared on the extended side in that policy's `overwrite`, which keys on
  a `base_policy` and a `superseded_clause` drawn from that policy's own rule.
  - **R3-T1 — the stale `rush_surcharge_pct` descriptor.** `blueprint/products/service.yaml`
    `parameter_schema` line 81 glosses it as "surcharge for expedited handling as a percentage of the
    authorised bench total", while the in-force basis is the confirmed ceiling. **Correctly deferred**,
    and for the reason the reworker gives but on my own check: the base *sentence* naming that basis is
    already declared superseded in `service_ext_expedited_surcharge.overwrite[0]`, and what remains is a
    `parameter_schema` description, which belongs to no base policy and therefore has no
    `superseded_clause` slot to be declared through — there is no mechanism on the extended side to
    close it, and the base may not be rewritten. It is nonetheless the sharpest of the three, because it
    is the only one that names a rival basis for a scored quantity: a reader taking it literally would
    price on `authorized_total` 3200.00 and reach a surcharge of 800.10 against 448.17. Containment rests
    wholly on the declared override being visible alongside it, which is a render-layer question and is
    already recorded there. **Observation, not a red**, because a parameter gloss is not a normative
    clause and the audit may not erect a third set of business rules; bears on **task 0**.
  - **R3-T2 — per-level goodwill allowance against no per-level parameter.** Base
    `service_discounts_and_goodwill.rule` promises "each service level carries its own allowance for how
    often that may be done", but `parameter_schema` carries no such per-level parameter and the only
    related artifact is the policy-level measure `service_msr_goodwill_12m`. This is an internal
    inconsistency of the frozen base (a rule making an empty promise), not an extended-weakens-base
    conflict. **Correctly deferred**: no extended policy claims `service_goodwill_discount_applied` as
    its subject, so no policy owns the sentence and none can declare it. Neither task writes a goodwill
    entry — task 0 only reads two that already stand — so no consequence on either world.
    **Observation.**
  - **R3-T3 — `state_contract` wider than its own condition.** Base
    `service_authorization.eligibility[order_in_workshop]` has
    `state_contract.allowed: [in_workshop, ready_for_pickup]` while its `condition` reads "Bench labour
    is charged, and the piece worked on, only while the work order stands in the workshop or has come
    back to the workshop under the guarantee" — and a piece come back under the guarantee is
    `in_workshop` again (the `service_rework_opened` transition is `delivered → in_workshop`), so
    `ready_for_pickup` is admitted by the contract and by no words of the prose. Again an internal
    inconsistency of the frozen base. **Correctly deferred**, and inconsequential here: both tasks' work
    orders stand `in_workshop`, which both readings admit. **Observation.**
- Carried forward unchanged from revision 2, all still accurate on the round-3 file: **F-2**, **F-3**,
  **F-5**, **F-8** (by identical tool hash), **F-10**, **F-12**, **R2-O1**, **R2-O2**, **R2-O3**.
  **F-1**, **F-4**, **F-6**, **F-7**, **F-9**, **F-11** remain closed.

### closing_checklist (round 3)

Written after both tasks' round-3 comparison sections were complete. **Both tasks PASS on all four
relationships; the difficulty is closed out on the round-3 artifacts.**

This supersedes the revision-2 closing checklist, which was reached on a charter that still carried
**F-13**. The revision-2 close was premature: task 0's `authorized_ceiling` and `surcharge_amount` were
each admitting two values from the materials a solver can see, and this audit did not catch it at either
of the two earlier rounds. The close below rests on a charter where that no longer holds.

| Step 4 item | status |
| --- | --- |
| Per-task files one-to-one with tasks; `revision_1` and `revision_2` preserved untouched beneath `revision_3`; every comparison section carrying a verdict | holds — both round-3 comparisons carry PASS |
| Extended policies fully covered; task scopes pairwise disjoint, each spanning its whole tree | holds — unchanged through three rounds |
| Task tools and GT closed; each tool an independently generated, frozen uuid8 | holds — tool module byte-identical to round 2 |
| Every tree 1–3 prerequisite problems, ≥ max(n−1,1) `value_input`, ≥1 `owner=user` write, no cycle; whole-difficulty graph a DAG | holds — n=2 / 2 `value_input` / `confirm_authorized_ceiling_b1b9df84`; n=1 / 1 / `confirm_stone_release_3a8d360e`; two disjoint chains |
| Self-sufficient baselines and 4–6 factors per computation (≥2 `parameter`, ≥1 `method`; per task ≥1 multi-source, ≥1 cross-difficulty); ladders of ≥3 tiers stated in full, distinct in outcome | holds — and `baseline.rule` is now genuinely self-sufficient for `service_ext_revised_authorization`, which it was not before F-13 was closed: a reader of the baseline paragraph alone now reaches a definite 1031.05 with the rounding moment named |
| Every factor load-bearing against an honest baseline; baseline alone definite and ≠ gold | holds — 15 + 10 factors; fall-backs 101.40 / 1031.05 / 355.64 and 6800.00 / 55.00 |
| Instantiation-stage gates re-run once on the final form | the coordinator's round-3 block on these exact hashes, TRACEABILITY included, is cited in `### charter_global_frozen (round 3)`; per Step 0 the auditor does not run them |

**Per-task verdicts, round 3.**

| task | policy self-consistency | problem tree | factors bear weight | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | **PASS** |
| 1 | PASS | PASS | PASS | PASS | **PASS** |

**Open observations carried** (none a red, none with a demonstrable consequence on either task's scored
solution): F-2, F-3, F-5, F-8, F-10, F-12, T0-4 (now documented and accurate at source), T1-1, T1-3,
R2-O1, R2-O2, R2-O3, R2-T0-a, R2-T1-a, R2-T1-b, R3-O1, R3-O2, and the three deferred base-freeze
tensions R3-T1, R3-T2, R3-T3 — each judged in `### findings (round 3)` against the base-freeze rule and
each found to have no declaration mechanism available on the extended side.

**Note on this audit's own reliability.** Three of the eight items this difficulty needed were found by
other passes, not by this one: F-13 came from the render-layer audit. The pattern in the miss is worth
recording for whoever reads these files next — at revisions 1 and 2 I checked that every rounding
*mode* was stated and that every monetary binding was wrapped in `RND`, and treated that as establishing
the rounding half of rule/compute equivalence. It does not: a binding can round at a moment the prose
never names, and the prose is what a solver has. The check that would have caught it is to evaluate the
prose alone, end to end, and compare the number with the binding's, which is what `### rule_compute_equivalence (round 3)`
now does for this policy.
