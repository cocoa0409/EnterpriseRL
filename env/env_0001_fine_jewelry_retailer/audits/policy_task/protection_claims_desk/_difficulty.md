# Policy-task audit — protection_claims_desk / charter-global

## charter_global_frozen

- freeze time: 2026-09-17 10:01 UTC (revision_1, first audit of this difficulty)
- auditor: independent source-layer auditor (not the instantiating agent)
- frozen artefacts and hashes (verified by `sha256sum`, first 16 hex):
  - `env/env_0001_fine_jewelry_retailer/tasks/protection_claims_desk/protection.extended.yaml` — `67c9493c7707091d` (207531 bytes)
  - `env/env_0001_fine_jewelry_retailer/tasks/protection_claims_desk/task_tools.py` — `8a8fe4fd4102957b` (20724 bytes)
- masked views used for the task layer (constructed by the coordinator, not by self-discipline):
  - `…/scratchpad/masked/protection_claims_desk/0.json` — `c2fbba94062cf753`
  - `…/scratchpad/masked/protection_claims_desk/1.json` — `4bd0af746e2ef799`
  - kept: `frozen_time`, `user_scenario`, `initial_state` (verified: those three are the only top-level keys)
  - dropped: `design_rationale`, `db_closure`, `db_closure_matches_initial_state`, `solvability_contract`,
    `evaluation_criteria`, `computations`, `prerequisite_closure`, `charter_scope`, `required_documents`
- fields permitted for this section: the whole extended charter, `task_tools.py`, the blueprint
  (`blueprint.yaml`, `db_schema.json`, `share_tools.py`, `products/*.yaml`) and `erlbench/` +
  `skills/erl-task-instantiate/scripts/check_compute.py` (for the compute-DSL semantics only).
- **Everything in this section was written before any task's GT was revealed.** Nothing below the
  closing-checklist heading existed at that time.
- *Recovery note (post-reveal, 2026-09-17):* while appending the closing checklist, a text-split
  anchor matched the phrase above and truncated this file; the pre-reveal section was restored
  verbatim from the auditor's original write of 10:01 UTC, with no change to its content.

### entry conditions (Step 0)

Supplied with the brief and only cited here, not re-run: the instantiation-stage gate block
(EXTENDED, TASK-TOOL-CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING & DISCLOSURE, SCOPE — all
PASS; `check_traceability` excluded because the published KB does not yet exist), the two masked
views with their hashes, and the two charter hashes above. Entry conditions complete. A machine
green light qualifies this difficulty for a manual audit; it proves nothing about self-consistency
or unique entailment.

### policy_conflict_scan

The structured policy in force for `protection` at this difficulty is the base section of
`protection.extended.yaml` plus its five `extended_policies`.

**Base copy is verbatim.** Every top-level key of `protection.extended.yaml` other than
`extended_policies` was compared key-for-key against `blueprint/products/protection.yaml`
(canonical JSON dump, sorted keys): `category`, `display_name`, `binding`, `lifecycle`, `accounts`,
`parameter_schema`, `variants`, `events`, `measures`, `policies` — all identical, and the base file
carries no key the extended file lacks. No rewritten base sentence.

**Overlapping subjects.** The five extended policies and their `(target_tool, computes)` pairs:

| policy | subject | target_tool | computes |
| --- | --- | --- | --- |
| `protection_ext_claim_settlement` | `protection_claim_settled` | `record_claim_settlement_8eb9093c` | `benefit_amount` |
| `protection_ext_cancellation_refund` | `protection_plan_cancelled`, `protection_premium_refunded` | `confirm_plan_cancellation_48603509` | `refund_amount` |
| `protection_ext_claim_refusal` | `protection_claim_denied` | `record_claim_refusal_9dff8781` | `refused_amount` |
| `protection_ext_allowance_reinstatement` | `protection_allowance_reinstated` | `reinstate_benefit_allowance_e0b143ff` | `allowance_amount` |
| `protection_ext_transfer_carryover` | `protection_plan_transferred` | `confirm_coverage_transfer_42b50f64` | `allowance_carried_across` |

No event type is claimed by two policies; no tool is claimed by two policies; no computed quantity
is claimed by two policies.

**Triggers.** `state_due` for the three the desk discovers from the record (settlement, refusal,
reinstatement), `on_request` for the two the customer asks for (cancellation, transfer). This
matches the problem-tree design: every root is `on_request`, every prerequisite `state_due`.

**Eligibility.** Every extended policy inherits its base gate unchanged and none of them restates or
weakens one: claim intake/settlement inherit `coverage_in_force`, `proof_of_loss_window`,
`one_settlement_per_claim`; the allowance grant inherits `grantable_state`; the transfer inherits
`plan_transferable_state`; the cancellation inherits `full_refund_window` as a *time anchor* (see
`override_declarations` finding F-1 for the one base sentence that is not carried).

**Time anchors.** `NOW` is `frozen_time` in every policy. Every window is anchored on a record date:
`F('purchased_date')`, `F('effective_date')`, `LATEST(protection_ledger, posted_date, …)`. No policy
anchors on a value the customer states. Both day-count conventions used
(`DAYS` = calendar days, `MONTHS` = whole months with day-of-month carry) are the engine's, and both
appear verbatim in the rules ("in calendar days", "the whole months since …", "part years dropped").

**Cross-category read boundaries.** Declared reads: `service` (work order, its priced lines, its
level's parameters), `circle` (membership standing and tier maintenance spend), `appraisal` (the
report on the covered piece). Each appears in the reading policy's `cross_category` block with the
fields it reads, and no compute expression reads a category that block does not declare — checked
binding by binding across all five policies. `protection_ext_transfer_carryover` declares
`cross_category: []` and indeed uses no `CFIELD`/`CPARAM`/`X*` call.

**Terminal states.** `cancelled` / `transferred` are the two closing writes and they are in different
policies and different tasks; `protection_claim_settled` and `protection_claim_denied` both close a
claim but on disjoint conditions (the coverage answers for the peril, or it does not) and are never
both available for one claim reference — `record_claim_settlement_8eb9093c` and
`record_claim_refusal_9dff8781` each write exactly one entry against one claim reference, and base
`protection_claim_settlement`'s `one_settlement_per_claim` dedup gate is inherited.

**Task scope exclusivity and completeness.** Derived from the `prerequisite` graph alone (the two
`charter_scope` fields are masked): the graph has exactly two roots, and the closure of each root is

- root `protection_ext_cancellation_refund` → `{cancellation_refund, claim_settlement}`
- root `protection_ext_transfer_carryover` → `{transfer_carryover, allowance_reinstatement, claim_refusal}`

The two closures are **pairwise disjoint** and their union is **all five** extended policies.
With M = 2 this is the only partition the graph admits, so the two tasks' scopes are mutually
exclusive and jointly complete.

**Result: no policy conflict that reaches different conclusions in the same situation was found
between two extended policies.** The conflicts found are all base-vs-extended and are recorded under
`override_declarations`.

### rule_compute_equivalence

Check 2 was run mechanically and then read sentence by sentence.

**Forward (compute → rule).** For each of the five policies, every ordered binding in `compute` has
an entry in `compute_basis`, and every sentence of every `compute_basis` entry occurs **verbatim**
(whitespace-normalised) in that policy's own `rule`. Machine result, bindings counted:

```
protection_ext_claim_settlement          29 bindings   missing_basis=[]  extra=[]  not_in_rule=[]
protection_ext_cancellation_refund       18 bindings   missing_basis=[]  extra=[]  not_in_rule=[]
protection_ext_claim_refusal             22 bindings   missing_basis=[]  extra=[]  not_in_rule=[]
protection_ext_allowance_reinstatement   24 bindings   missing_basis=[]  extra=[]  not_in_rule=[]
protection_ext_transfer_carryover        15 bindings   missing_basis=[]  extra=[]  not_in_rule=[]
```

`compute` therefore invents no basis of its own. Likewise every sentence of every `baseline.rule` is
a verbatim sentence of the policy's `rule` (`not_in_rule=[]` for all five).

**Backward (rule → compute), sentence by sentence.** Each rule's quantities, windows, filters,
tiers, branches, cross-category reads, acting bases, groupings, caps/floors and rounding conventions
were traced to a restricted expression. All accounted for. Two remarks, both recorded as
observations below rather than as red lights because neither changes a scored value:

- O-1 (sign convention). `protection_ext_claim_settlement` says "*less the benefit consumed by the
  settlements booked in that window*" and implements it as `… + SUM('protection_ledger','amount', …,
  event_type='protection_claim_settled')`. The addition is a subtraction only because settlement
  rows carry a negative `amount` — the task tool writes `amount=-round(float(benefit_amount), 2)`
  and every seeded settlement row in both worlds is negative. The two faces agree; the reader must
  know the sign convention, which the `accounts` block states ("*consumed by each settlement*").
- O-2 (boundary of "the whole time it has been in force"). Three fall-through tiers encode "over the
  whole time the plan has been in force" as `within_months=MONTHS(F('effective_date'), NOW)`
  (`protection_ext_claim_refusal.services_window_months`,
  `protection_ext_transfer_carryover.allowance_window_months`, and the matching `baseline` bindings).
  The engine's window test is `0 <= MONTHS(row_date, NOW) < within_months`
  (`skills/erl-task-instantiate/scripts/check_compute.py:271-278`), so an entry booked **on the
  effective date itself** is excluded: the prose says "the whole time", the expression says "all but
  the first day". Demonstrated in task 1's transfer baseline (see `1.md` → `factor_weight`), where
  the reading a reader takes from `baseline.rule` (12899.95) and the encoded baseline (9399.95)
  differ by the 2022-03-14 grant of 5000.00 × 0.7. Neither figure is gold, and this fall-through
  tier is not the tier either task takes, so no scored value moves.

**Factor ladders in both faces.** For all 24 declared factors, every tier named in `factors[].ladder`
is a sentence of the `rule` and a branch of the `decides` binding, and every branch of each `decides`
binding is a tier the rule states. No tier lives only in `compute`; no tier is promised only in prose.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (table above). Each policy's
  subject, `base_policy_refs`, target tool, tool docstring and terminal state admit one business
  reading.
- No extended policy adds a confirmation, review, wait or procedure outside the policy. The two
  `owner="user"` tools carry the base charter's own reason for being the customer's
  ("*because ending coverage they paid for is theirs alone to do*",
  "*because giving coverage they paid for to another person is theirs alone to do*").
- uuid8 suffixes: `8eb9093c`, `48603509`, `9dff8781`, `e0b143ff`, `42b50f64`. Five distinct values,
  no shared prefix, no shared tail, no arithmetic or lexical sequence, no digit-only-versus-hex
  pattern that would suggest batch derivation from one seed. Each is frozen with its tool and
  appears nowhere else in the repository's protection artefacts.
- Docstring sequence check: no docstring names another tool, states this action's position in a
  sequence, or carries a cross-action ordering word. The only occurrences of "afterwards" are in the
  *Returns* paragraphs describing what the record shows once the write has landed, which is this
  framework's standard effect-visibility sentence and not an ordering claim about other actions. The
  single occurrence of "first" (`record_claim_settlement_8eb9093c`: "*the entry on which the loss was
  first entered*") identifies a row, not a step order.

### prerequisite_graph

Check 7 over the whole graph. Three edges, all declared on the blocked side:

| blocked policy | depended-on problem | kind | gate | form | resolved_by |
| --- | --- | --- | --- | --- | --- |
| `protection_ext_cancellation_refund` | `protection_ext_claim_settlement` | `value_input` | `returned_share` | `state` | `record_claim_settlement_8eb9093c` |
| `protection_ext_transfer_carryover` | `protection_ext_allowance_reinstatement` | `value_input` | `granted_in_window` | `state` | `reinstate_benefit_allowance_e0b143ff` |
| `protection_ext_transfer_carryover` | `protection_ext_claim_refusal` | `value_input` | `claims_share` | `state` | `record_claim_refusal_9dff8781` |

- `prerequisite` is filled in on all five policies (`[]` on the three that have none).
- Every `problem` points at another extended policy id **in this file**; none points at a base policy
  and none at itself.
- The graph is acyclic: `claim_settlement`, `allowance_reinstatement` and `claim_refusal` are sinks;
  `cancellation_refund` and `transfer_carryover` are roots; no back edge.
- Every `policy_source` is verbatim locatable in the **blocked** policy's own `rule` (machine-checked,
  all three `True`) and occurs in **no** depended-on policy's rule (all three `False`).
- `form: state` on all three; no `fallback_reason` is present, and none is required — see
  `prerequisite_sentences` for the state-form test on each.
- Every `gate` names a binding that genuinely exists in the blocked policy's `compute`
  (`returned_share`, `granted_in_window`, `claims_share` — all verified present), and `kind` is
  `value_input` in each case, which matches: none of the three is a status gate, each feeds a named
  value into the blocked computation.
- Every `resolved_by` is exactly the depended-on policy's `target_tool` (all three `True`), and each
  genuinely changes the binding named in `effect` — demonstrated per task in `0.md` / `1.md` under
  `problem_chain`.
- No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears in
  any `prerequisite` field; each `condition` is written as a general state of the record.

### prerequisite_sentences

Check 6 on each edge. The four-point test: (i) joins this policy's own result to what it waits on
with an explicit ordering connective; (ii) what it waits on is, in the declared form, a
record-visible state in the words the tables and finders use, with no action, performer or tool;
(iii) names no tool, policy id, snake_case token or row id; (iv) is at exactly the strength and
scope the edge's `condition` carries.

**E1 — `cancellation_refund` waits on `claim_settlement`.**
> "The premium returned is fixed only after the benefit consumed by every claim entered against the plan stands recorded against it."

(i) "only after" ✓. (ii) state form: "*the benefit consumed by every claim … stands recorded against
it*" — a record-visible state in the finder's own words (`find_protection_ledger`: "*what was settled
against them*"); no verb of performance, no performer, no tool ✓. (iii) no tool name, no policy id,
no snake_case, no row id ✓. (iv) `condition` = "*every claim entered against the plan carries a
settlement entry booked under its own claim reference recording the benefit it consumed*" — the same
scope, open set ("every claim"), neither narrowed nor widened ✓.
**One write brings that state about.** Across this difficulty exactly one write records benefit
consumed against a claim reference: `record_claim_settlement_8eb9093c` (`event_type=
protection_claim_settled`, `amount = -benefit_amount`, `claim_reference`). `record_claim_refusal_
9dff8781` writes `protection_claim_denied` and, in the tool's own words, "*No benefit allowance
moves*", so it cannot be mistaken for the write that records benefit consumed. No second candidate.
**Single reading.** Prerequisite sentence → look for claims on the plan whose benefit consumed is not
recorded → `find_protection_ledger` shows a `protection_claim_filed` entry with no settlement under
its reference → the policy whose own rule describes recording what a claim draws is
`protection_ext_claim_settlement` ("*A claim the coverage answers for is settled by drawing benefit
from the plan the covered piece stands on*") → its `target_tool`. Exactly one reading.

**E2 — `transfer_carryover` waits on `allowance_reinstatement`.**
> "What carries across to the new owner is fixed only after the allowance entries booked to the plan carry a grant for the coverage year in progress."

(i) "only after" ✓. (ii) state form: "*the allowance entries booked to the plan carry a grant for the
coverage year in progress*" — a state of the history rows, in the finder's own words
(`find_protection_ledger`: "*the benefit allowance granted at the start and reinstated on each
anniversary*") ✓. (iii)–(iv) ✓; `condition` = "*an allowance entry for the coverage year in progress
stands booked to the plan …*", the same scope.
**One write brings that state about.** `reinstate_benefit_allowance_e0b143ff` is the only write in
this difficulty that creates an allowance entry (`protection_allowance_reinstated`). No task tool
writes `protection_allowance_granted`; that event appears only as seeded history. No second
candidate. Single reading: the sentence sends the reader to the allowance entries; the policy whose
own rule describes booking one ("*the allowance for the coverage year in progress is booked to the
plan as one entry*") is `protection_ext_allowance_reinstatement`.

**E3 — `transfer_carryover` waits on `claim_refusal`.**
> "Coverage passes to a new owner only once every claim entered against the plan that the coverage does not answer for carries the ground on which it was refused."

(i) "only once" ✓. (ii) state form: "*carries the ground on which it was refused*" — a record-visible
state; `find_protection_ledger` says the history carries "*what was refused and on which single
ground*" ✓. (iii)–(iv) ✓; `condition` restates the same open set.
**One write brings that state about.** `record_claim_refusal_9dff8781` is the only write that sets
`denial_reason_code` / `claim_outcome` on a refusal entry. No second candidate. Single reading.

**State form honoured everywhere.** All three edges are `state`; no `fallback_reason` is claimed, so
the state-form priority rule is satisfied by construction and there is no fallback to test.

**Nothing else about the dependency is carried.** Each blocked rule states its prerequisite once,
in one wording; no rule names another problem's tool, id or route; no depended-on rule restates the
sentence (machine-checked above). Cross-problem ordering language elsewhere in the extended rules
was swept: "*taken off after the share the coverage answers for has been worked out and before the
benefit is drawn*", "*Neither of those limits is applied before the deductible has been taken off*",
"*the administration fee is taken off only after that share has been applied*", "*one after another
and each on the figure the one before it left*", "*The tenure share and the claims share both act on
the benefit standing, one after the other*" — every one of these orders steps **within one
computation**, not one problem against another, and none grounds an undeclared edge.

**Base rule sentences that state a cross-problem order.** Two exist in the inherited base and are
recorded here so that each task file can say whether its tree rests on them:

- `protection_transfer`: "*A transfer takes effect only once an inspection has been logged against the
  piece where the coverage requires one, and a transfer asked for without that inspection is held
  rather than refused.*" Every coverage that admits transfer requires the inspection
  (`transfer_requires_inspection: true` on Care Plan 3-Year, 5-Year, Lifetime, Heirloom).
- `protection_transfer`: "*A transfer is recorded only while the plan stands at active, and coverage
  that is suspended or out of good standing is put right before it is transferred.*"

Neither grounds a declared edge, and no write in this difficulty logs an inspection or restores
coverage, so neither can be a prerequisite problem here. Per check 6 these are observations unless a
task's tree rests on one; task 1's file records that its tree does not (the required inspection is
already in the seed and the plan already stands `active`).

### override_declarations

Check 1's **finding** half, run once, sentence by sentence against every entry in every
`base_policy_refs`. Each affected task file demonstrates (or fails to demonstrate) the consequence
against its own world.

**`protection_ext_claim_settlement`** (refs `protection_claim_settlement`,
`protection_agg_allowance_pooling`, `protection_included_services`) — three `overwrite` entries, each
naming a base sentence of `protection_claim_settlement` verbatim:

| base sentence | handled | declared? |
| --- | --- | --- |
| "An accepted claim is settled at the value the coverage sets, which is either what the piece originally sold for or what it would cost to replace today…" | differently (settled off the bench figure) | **yes**, overwrite #2 |
| "The settled value is reduced by the coverage's annual depreciation…and the result is capped at the coverage's share of the item value recorded at purchase." | differently (base is the priced bench work; the depreciation reduction and the cap are both retained) | **yes**, overwrite #1 |
| "The customer pays the coverage's deductible on each accepted claim before the settlement is released, and the deductible is recorded against the settlement rather than netted silently out of it." | differently (a three-tier deductible; still recorded separately, via the tool's `deductible_charged` argument) | **yes**, overwrite #3 |
| "A settlement is made only when the plan's remaining allowance covers it; where the allowance is short the claim is settled in part…" | followed (`allowance_standing` is a hard `MN` limit) | n/a |
| "A settlement is made only when no settlement already stands against that same claim reference." | followed (inherited dedup gate) | n/a |
| "No more claims are settled in a rolling twelve months than the coverage's cap allows, and a further claim inside the coverage's minimum interval between settlements is refused rather than queued." | followed | n/a |
| "Where the coverage answers by repairing first, the piece goes to the workshop on a bench work order and the settlement is recorded against that work order…" | followed | n/a |

From `protection_included_services`: "*Routine services consume no benefit allowance*" — followed.
From `protection_agg_allowance_pooling`: see **F-2**.

**`protection_ext_cancellation_refund`** (refs `protection_cancellation_refund`,
`protection_claim_settlement`) — three `overwrite` entries. See **F-1**.

| base sentence | handled | declared? |
| --- | --- | --- |
| "A plan cancelled inside the coverage's full-refund window is refunded in whole, and the cancellation takes effect on the day the customer confirms it." | **differently** — extended prorates by the months still to run and applies the claims share inside the window as well as outside | **NO** — **F-1** |
| "A merchandise protection plan is refunded in whole only when the cancellation reaches the desk within the full-refund window in calendar days, counted from the date the plan was bought." | differently | **yes**, overwrite #1 |
| "The full-refund window is counted in whole calendar days from the day the plan was bought, that day counting as day zero, weekends and store holidays included, and part days are never rounded up." | followed (`DAYS(F('purchased_date'), NOW)` against `P('cancellation_refund_full_window_days')`) | n/a |
| "After that window the coverage that prorates returns the premium in proportion to the months of the term not yet run, less the coverage's administration fee, and the coverage that does not prorate returns nothing." | differently (extended prorates for every coverage and re-tiers the fee) | **yes**, overwrite #3 |
| "A plan that has already settled a claim is not refunded at all, whatever window it is cancelled in, because the coverage has already answered." | differently (a two-tier claims share instead of nil) | **yes**, overwrite #2 |
| "The cancellation itself is confirmed by the customer on the protection service request record, because ending coverage they paid for is theirs alone to do." | followed (`owner="user"` tool, `request_status="customer_confirmed"`) | n/a |

**`protection_ext_claim_refusal`** (refs `protection_claim_intake`, `protection_included_services`) —
`overwrite: []`, held to the same sentence-by-sentence standard.

From `protection_claim_intake`: the peril test, the intake status gate, the theft/police-report rule,
the proof-of-loss window and its counting rule, and "*exactly one ground is recorded*" are all
followed; base fixes no monetary figure for a refusal, so `refused_amount` adds a quantity rather
than replacing one. From `protection_included_services`: "*Chain and clasp work is included on the
coverage that lists it*" is followed; "*A service visit that falls outside what the coverage includes
may be handled as goodwill up to the coverage's goodwill allowance*" is followed (the count of
goodwill already drawn is tested against `P('goodwill_service_visits_per_12_months')`). See **F-3**
for the one window that is handled differently.

**`protection_ext_allowance_reinstatement`** (refs `protection_allowance_grant`,
`protection_agg_allowance_pooling`, `protection_inspection_discipline`) — one `overwrite`.

| base sentence | handled | declared? |
| --- | --- | --- |
| "The benefit allowance is granted when coverage comes into force, in the amount the coverage sets for a coverage year." | followed — this sentence governs the grant **at inception**; the extended policy is scoped to the annual reinstatement ("*On coverage that grants its benefit allowance afresh each year…*") | n/a |
| "On the coverage that reinstates annually the allowance is granted afresh on each anniversary of the effective date, and any allowance unused in the year just ended does not carry forward." | differently (an appraisal-proportioned base, then four shares) | **yes**, overwrite #1 (the whole sentence is named, so everything the extended rule puts in its place is covered) |
| "An allowance grant or reinstatement is booked only while the plan stands at active, inspection overdue or exhausted, and never against a plan that has closed." | followed | n/a |
| "The lifetime allowance is a separate ceiling that no amount of annual reinstatement passes…" | followed (`lifetime_headroom` is a hard `MN` limit) | n/a |
| "Where the coverage does not reinstate, the allowance granted at the start is all the plan ever has." | followed (the policy's own first sentence scopes it to reinstating coverage) | n/a |

From `protection_inspection_discipline`, the interval, grace and restoration sentences are inherited
unchanged; the extended rule reads the inspection history only to set a share, never to relax a gate.

**`protection_ext_transfer_carryover`** (refs `protection_transfer`,
`protection_agg_allowance_pooling`) — one `overwrite`.

| base sentence | handled | declared? |
| --- | --- | --- |
| "Coverage may be transferred with the piece to a new owner only on the coverage that admits transfer, and the transfer carries the coverage's transfer fee." | followed as to eligibility; see **F-4** as to the fee | partly |
| "A transfer takes effect only once an inspection has been logged against the piece where the coverage requires one…" | followed | n/a |
| "A transfer is recorded only while the plan stands at active…" | followed | n/a |
| "The plan closes as transferred on the transferring customer's record and the new owner's cover begins on the same day, with the remaining allowance carried across as it stands." | differently (a tenure share and a claims share) | **yes**, overwrite #1 |
| "The transfer is confirmed by the customer on the protection service request record…" | followed (`owner="user"` tool) | n/a |
| "The transfer fee is taken at the counter and recorded against the coverage as a premium received in the period it was taken, so that what the customer has paid toward the plan stays a single running figure." | **not implemented** | **F-4** |

**Disguised forms.** Swept explicitly across all five policies: no anonymous intermediate factor (every
intermediate that moves a scored quantity has a `compute_basis` sentence in the rule); no 0/1
multiplier zeroing an amount base already fixed (`covered_share`, `returned_share`, `claims_share`,
`draw_share`, `late_share`, `inspection_share`, `member_share`, `tenure_share` are all strictly
positive in every tier); no dropped branch (every branch a base sentence declares is reachable from
some tier of the extended selector). No `rule`, `compute_basis` or note calls a base output a "wrong
value" or an "algorithm to avoid".

### factor_ladders

Structure only. Whether a factor bears weight is a fact about one world and lives in each task file.

| policy | factor | effect | decides | tiers | multi-source (non-fall-through tiers) | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| claim_settlement | `repair_figure_basis` | method | `repair_figure` | 3 | no (both conjuncts on the one work order) | service |
| claim_settlement | `loyalty_reduction` | parameter | `loyalty_pct` | 3 | no (membership record + tier parameter) | circle |
| claim_settlement | `wear_reduction_rate` | parameter | `wear_rate_pct` | 3 | **yes** (inspection ledger row ∧/∨ work-order row) | service |
| claim_settlement | `answered_share` | parameter | `covered_share` | 3 | no (two parameters) | service |
| claim_settlement | `deductible_borne_by_customer` | parameter | `deductible_borne` | 3 | **yes** (settlement rows ∧ inspection rows) | — |
| cancellation_refund | `premium_paid_basis` | method | `premium_base` | 3 | **yes** (holding field ∧ ledger give-back rows) | — |
| cancellation_refund | `months_still_to_run` | method | `months_left` | 3 | no (inspection row + purchase date, one record each way) | — |
| cancellation_refund | `unused_premium_share` | parameter | `returned_share` | 3 | no (one row set, count and sum) | — |
| cancellation_refund | `administration_fee_charged` | parameter | `admin_fee_charged` | 3 | **yes** (plan dates ∧ membership variant) | circle |
| claim_refusal | `recorded_figure_basis` | method | `claim_figure` | 3 | **yes** (filed row ∧ settlement rows) | — |
| claim_refusal | `piece_value_taken` | parameter | `value_basis` | 3 | no (one appraisal record) | appraisal |
| claim_refusal | `drawn_services_window` | method | `services_window_months` | 3 | no (parameter ∧ ledger rows) | — |
| claim_refusal | `included_work_credit` | parameter | `included_credit` | 3 | no (parameter ∧ ledger rows) | service |
| claim_refusal | `goodwill_met` | parameter | `goodwill_credit` | 3 | no (refusal rows ∧ parameter) | — |
| allowance_reinstatement | `yearly_allowance_basis` | method | `yearly_base` | 3 | **yes** (appraisal record ∧ plan record) | appraisal |
| allowance_reinstatement | `drawn_benefit_window` | method | `drawn_benefit` | 3 | no (allowance rows ∧ parameter) | — |
| allowance_reinstatement | `after_draw_share` | parameter | `draw_share` | 3 | **yes** (drawn-benefit aggregate ∧ life settlement count) | — |
| allowance_reinstatement | `late_grant_share` | parameter | `late_share` | 3 | no (one date span) | — |
| allowance_reinstatement | `inspection_year_share` | parameter | `inspection_share` | 3 | **yes** (inspection count ∧ latest inspection date) | — |
| allowance_reinstatement | `membership_uplift` | parameter | `member_share` | 3 | no (membership record + tier parameter) | circle |
| transfer_carryover | `allowance_entries_window` | method | `allowance_window_months` | 3 | no (parameter ∧ allowance rows) | — |
| transfer_carryover | `consumed_benefit_basis` | method | `consumed_benefit` | 3 | **yes** (settlement rows ∧ allowance rows) | — |
| transfer_carryover | `tenure_carry_share` | parameter | `tenure_share` | 3 | no (one date span) | — |
| transfer_carryover | `claims_carry_share` | parameter | `claims_share` | 3 | **yes** (refusal rows ∧ settlement rows) | — |

**Counts per policy (bounds 4–6 total, ≥2 `parameter`, ≥1 `method`).**

| policy | total | parameter | method | verdict |
| --- | --- | --- | --- | --- |
| claim_settlement | 5 | 4 | 1 | within bounds |
| cancellation_refund | 4 | 2 | 2 | within bounds |
| claim_refusal | 5 | 3 | 2 | within bounds |
| allowance_reinstatement | 6 | 4 | 2 | within bounds |
| transfer_carryover | 4 | 2 | 2 | within bounds |

**Counts per task** (over the policies its problem tree spans):

| task | policies | multi-source factors | cross_difficulty factors | categories read |
| --- | --- | --- | --- | --- |
| 0 | claim_settlement, cancellation_refund | 4 (`wear_reduction_rate`, `deductible_borne_by_customer`, `premium_paid_basis`, `administration_fee_charged`) | 5 | service, circle |
| 1 | transfer_carryover, allowance_reinstatement, claim_refusal | 6 | 4 | appraisal, service, circle |

Both tasks clear "≥ 1 multi-source" and "≥ 1 cross-difficulty".

**Disjoint binding sets.** Within each policy, no binding name appears in two factors' `bindings`
lists — checked exhaustively. Every `decides` names a genuine *input* to the result expression, never
`result` itself.

**Tier disjointness.** Every one of the 24 ladders is written as
`(A ∧ B) / (A ∧ ¬B)` or `(A ∧ B) / (¬A ∧ B)` or two thresholds on one ordered quantity, plus an
`otherwise`. Each was read as stated; all 24 are pairwise disjoint on their face.

**No two tiers of one ladder select the same value or method** — verified for all 24 on the parameter
values the coverage line actually carries. Two ladders degenerate on some *other* coverage than the
ones these tasks use, and this is recorded as an observation, not a red light, because neither
degenerate world is a world of this difficulty:
- `wear_reduction_rate` (0.5·d / 1.5·d / d) collapses to a single value when
  `depreciation_pct_per_year = 0`, which is the Lifetime Care Plan and the Heirloom Protection Plan.
- `deductible_borne_by_customer` (0 / 2·k / k) collapses when `deductible_per_claim = 0`, which is the
  Manufacturer Limited Warranty, the Lifetime Care Plan and the Heirloom Protection Plan.
- `loyalty_reduction` (p / 0.5·p / 0) collapses when the service level carries
  `loyalty_discount_pct = 0`, which is Standard Bench Service and Designer Authorized Repair Service.

**Conditions and outcomes the business actually holds.** Every non-fall-through conjunct was checked
against the charter's own parameter table to confirm it divides this line's customers rather than
restating the policy's scope:
`allowance_reinstates_annually` (false on the Manufacturer Limited Warranty, true on the other five),
`expedited_service_available` (false on two, true on four), `chain_repair_included` (false on one,
true on five), `goodwill_service_visits_per_12_months > 0` (0 on one, 1–4 on five),
`transfer_allowed` (false on two, true on four), `premium_payment_schedule` (single payment on four,
monthly on two), and every membership-tier maintenance floor (0 at Member, 1 500 – 150 000 above).
None holds of every customer who reaches the write. Every outcome — a prorated premium net of an
administration fee, a deductible waived on a clean inspection record and doubled on a repeat claim,
an allowance reproportioned to a current insurance-replacement appraisal, a carry-across share that
rises with tenure and falls after a refused claim — is a treatment a jewellery protection programme
does in fact publish.

**Label honesty.** Every `method` tier substitutes a different source, window or formula shape; every
`parameter` tier substitutes a number into an unchanged formula. One inconsistency is recorded as
an observation (**F-5**): `piece_value_taken` is labelled `parameter` although its tiers switch the
*source* of the value (the appraisal register's figure vs. the plan's purchase value), which is the
same shape as `repair_figure_basis`, labelled `method`.

**Baselines.** Each policy declares a `baseline` whose `rule` is drawn wholly from its own `rule`
(machine-checked above) and each factor's fall-through tier is that baseline. `baseline.params` was
compared against the keys each baseline actually needs; one mismatch is recorded as an observation
(**F-6**).

### findings

**F-1 — `SOURCE-POLICY` (observation on the evidence available: no task world demonstrates the
consequence). Undeclared override of `protection_cancellation_refund`'s first sentence.**
*Symptom.* Base and extended reach different refund figures for a plan cancelled inside the
full-refund window.
*Root cause.* `protection_ext_cancellation_refund.overwrite` names three base sentences; it does not
name the first: "*A plan cancelled inside the coverage's full-refund window is refunded in whole, and
the cancellation takes effect on the day the customer confirms it.*" That sentence is therefore
inherited in full, while the extended rule prorates ("*taken in proportion to the whole months of the
term still to run*") and applies a claims share regardless of the window, waiving only the
administration fee inside it.
*Evidence.* `blueprint/products/protection.yaml` → `policies[protection_cancellation_refund].rule`,
sentence 1; `protection.extended.yaml` → `extended_policies[protection_ext_cancellation_refund].
overwrite` (three entries, naming sentences 2, 4 and 5 of that base rule) and `.rule`.
*Demonstrated consequence.* None on the worlds of this difficulty. The only task that computes a
refund is task 0, whose plan was bought 2024-07-19 and whose cancellation reaches the desk
790 calendar days later against a `cancellation_refund_full_window_days` of 30, so the inherited
sentence never fires and both readings give one figure. Recorded as an observation because the
consequence the "Core constraints" table demands cannot be demonstrated here.
*Affected artefact.* `env/env_0001_fine_jewelry_retailer/tasks/protection_claims_desk/protection.extended.yaml`,
`extended_policies[1].overwrite`. Bears on task 0.

**F-2 — observation. `protection_agg_allowance_pooling`'s window is not the window
`protection_ext_claim_settlement` counts over, and no `overwrite` names it.**
*Symptom.* Base reads remaining allowance over "*the current coverage year*"; extended reads it over
a rolling twelve months to the handling date.
*Root cause.* `base_policy_refs` includes `protection_agg_allowance_pooling`, whose rule says "*The
benefit consumed in the current coverage year on one plan is read as the sum of the settlements
booked to that plan in that year, and the remaining allowance is the granted allowance less that
sum.*" The extended rule says "*the allowance granted and reinstated in the window the coverage counts
allowances over, less the benefit consumed by the settlements booked in that window*", and `compute`
fixes that window at `K('allowance_window_months') = 12` rolling months, not the anniversary year.
The same file's other policies *do* use the coverage year (`MONTHS(F('effective_date'), NOW) % 12`),
so the divergence is not a house convention. No `overwrite` entry names the pooling sentence.
*Evidence.* base `protection_agg_allowance_pooling.rule`; extended `protection_ext_claim_settlement.
compute` → `allowance_standing`, `.params.allowance_window_months: 12`, `.overwrite` (three entries,
all naming `protection_claim_settlement`).
*Demonstrated consequence.* None on task 0's world: the coverage year in progress opened 2026-07-19,
the only allowance entry in it is the 2 500.00 reinstatement of that date, and no settlement stands
in it, so both readings give 2 500.00; and the `MN` never binds (see `0.md`). Observation.
*Affected artefact.* same file, `extended_policies[0]`. Bears on task 0.

**F-3 — observation. `protection_included_services`' "rolling twelve months" is not the window
`protection_ext_claim_refusal` counts over, and its `overwrite` is empty.**
*Symptom.* Base counts what the coverage has already given over a rolling twelve months; extended's
`drawn_services_window` ladder counts over the coverage year so far, or twelve months, or the whole
time the plan has been in force.
*Root cause.* Base: "*Coverage includes a set number of routine services in a rolling twelve months*"
and "*A service visit that falls outside what the coverage includes may be handled as goodwill up to
the coverage's goodwill allowance*". Extended `protection_ext_claim_refusal.overwrite` is `[]`, yet
its rule opens the window to two other spans.
*Evidence.* base `protection_included_services.rule`; extended `protection_ext_claim_refusal.rule`
("*The routine work and the goodwill already drawn are counted over the whole time the plan has been
in force. Where the coverage grants its allowance afresh each year and a grant stands for the
coverage year in progress, they are counted instead over that coverage year so far…*") and
`.overwrite: []`.
*Demonstrated consequence.* None on task 1's world: the only chain-break settlement is dated
2024-11-19 (22 whole months back) and no refusal stands at the opening, so counting over 6, 12 or
54 months all give 0 chain repairs drawn and 0 refusals, and the refused amount is 10 061.00 on every
reading. Observation.
*Affected artefact.* same file, `extended_policies[2]`. Bears on task 1.

**F-4 — observation. The base transfer fee is inherited but nothing in this difficulty can record it.**
*Symptom.* Base promises a premium-received entry for the transfer fee; the transfer write does not
create one, and the coverage's `premium_paid_to_date` does not move.
*Root cause.* `protection_transfer` sentence 6 — "*The transfer fee is taken at the counter and
recorded against the coverage as a premium received in the period it was taken, so that what the
customer has paid toward the plan stays a single running figure*" — is named in no `overwrite`, so it
is inherited; but `confirm_coverage_transfer_42b50f64` writes only the intake request and the plan
update (`status`, `transferred_to_name`, `closed_date`, `remaining_benefit_allowance`), and no other
task tool books a premium.
*Evidence.* base `protection_transfer.rule`, last sentence; `task_tools.py` →
`confirm_coverage_transfer_42b50f64` body; the plan's `transfer_fee` is 45.00 on Care Plan 5-Year.
*Demonstrated consequence.* None on the scored surface: no policy computes the fee, and no second
value for any scored parameter follows, because the agent has no tool with which to act on the
inherited sentence. The terminal state is nevertheless narrower than base describes. Observation.
*Affected artefact.* `task_tools.py`; base sentence inherited into
`protection.extended.yaml` → `policies[protection_transfer]`. Bears on task 1.

**F-5 — observation. Inconsistent effect labels on two structurally identical factors.**
`protection_ext_claim_refusal.piece_value_taken` is `effect: parameter` although its tiers change
*which record the value is read from* (the appraisal register's `appraised_value` on tier 1, the
plan's `item_value_at_purchase` on tiers 2 and 3), while
`protection_ext_claim_settlement.repair_figure_basis` — tiers that likewise change which field of one
record the figure is read from — is `effect: method`. Both labels are defensible in isolation; they
cannot both be right in one charter. No scored value moves either way, and each policy independently
meets the ≥2 `parameter` / ≥1 `method` floor under either label, so this is an observation.
Bears on task 1.

**F-6 — observation. `baseline.params` on two policies names keys the baseline does not use.**
`protection_ext_claim_refusal.baseline.params` lists `coverage_year_months`,
`goodwill_service_visits_per_12_months` and `chain_repair_included`, but its `baseline.rule` says
"*Nothing is taken off the figure for work the coverage would have answered for without a claim.
Nothing is met as goodwill.*", so neither of the last two is read and `coverage_year_months` is a
policy constant (`K`), not a coverage parameter (`P`). `protection_ext_transfer_carryover.baseline.
params` likewise lists `coverage_year_months`. The baselines remain self-sufficient and each yields a
definite number (demonstrated per task), so this is an observation about the declaration, not about
the baseline. Bears on tasks 0 and 1.

**F-7 — `SOURCE-FACTOR` (charter-global half). Tiers 1 and 2 of
`protection_ext_cancellation_refund.premium_paid_basis` restate a declared account balance that the
holding table carries as a field.**
*Symptom.* The value the ladder's two non-fall-through tiers select is, by the charter's own
definition, the number already stored in `protection_plans.premium_paid_to_date`.
*Root cause.* The charter's `accounts` block declares `premium_account` as "*what the customer has
paid toward this plan, increased by each premium received and decreased by each refund returned to
them*". Tier 1 of the ladder is "*the premium entries booked to the plan net of the give-backs booked
against them*" and tier 2 is "*the premium entries booked to the plan as received*" — both are that
account balance. Only the fall-through (`F('premium_amount')`, the price the plan sold at) differs
from it. The field is served in full by `find_protection_plans`, whose docstring advertises "*the
premium and what has been paid toward it*".
*Evidence.* `protection.extended.yaml` → `accounts[1]`; `extended_policies[1].factors[0].ladder`;
`blueprint/share_tools.py:211-231` (`find_protection_plans` returns `str(rows)`, the unprojected row).
*Consequence.* Structural: on any world where the ladder takes tier 1 or tier 2, an agent that never
reads the ladder and simply takes the coverage record's premium-paid figure selects the same value,
so reading the field and reading the rule cannot be told apart by the score. Demonstrated against
task 0's world and scored solution in `0.md` → `factor_weight`. Bears on task 0.

---

## closing_checklist

Written 2026-09-17 after both tasks' `source_gt_comparison` were on disk. This section sits below the
pre-reveal charter-global section and contains the only difficulty-level conclusion reached after the
reveals.

**The difficulty does not close out in revision_1.** Step 4 closes a difficulty only when all four
relationships PASS on every task. Task 1 passes all four; task 0 passes three and carries one
`SOURCE-FACTOR RED` (`0.md` → `## findings` F-0, charter-global half at `### findings` F-7 above). The
checklist is recorded as it stands so that the next revision can carry forward what already holds:

| item | state |
| --- | --- |
| per-task audit files correspond one-to-one with `tasks/0.json`, `tasks/1.json`; `_difficulty.md` sits alongside; revision_1 is the first, so no older revision to trace | holds |
| every comparison section carries a verdict | holds — task 0: **SOURCE-FACTOR RED**; task 1: **PASS** |
| every comparison section carries a PASS | **does not hold** (task 0) |
| the five extended policies are fully covered and the two tasks' scopes are pairwise disjoint, each scope spanning its whole tree (root + prerequisite problems) | holds — `{cancellation_refund, claim_settlement}` and `{transfer_carryover, allowance_reinstatement, claim_refusal}`; matches both revealed `charter_scope` fields |
| task tools and GT are closed; each task tool uses an independently generated, frozen uuid8 | holds — `### action_binding_and_uuids` |
| every problem tree has 1–3 prerequisite problems, ≥ max(n − 1, 1) `value_input` edges, ≥ 1 `owner=user` problem, no cycle | holds — task 0: n = 1, 1 value_input, root is the user's write; task 1: n = 2, 2 value_input, root is the user's write |
| the difficulty's `prerequisite` edges together form a DAG with no cycle created by cross-task references | holds — three edges, two roots, three sinks, no edge between the two trees |
| every computation declares a self-sufficient baseline and 4–6 factors (≥ 2 `parameter`, ≥ 1 `method`); per task ≥ 1 multi-source and ≥ 1 cross-difficulty; every ladder ≥ 3 tiers stated in full in its rule, tiers distinct in outcome, conditions and outcomes ones the line of business holds | holds — `### factor_ladders`; per-task counts in `0.md` / `1.md` → `factor_weight` |
| every factor proved to bear weight on its task's world against an honest baseline, the baseline alone giving a definite number different from gold | holds numerically for all 24 factors and all 5 baselines (`0.md`: 781.60 / 353.89 vs 1 064.90 / 272.58; `1.md`: 5 000.00 / 12 900.00 / 9 399.95 vs 3 118.50 / 10 061.00 / 2 245.32) |
| no factor's tier is read off a stamp | **does not hold** — `premium_paid_basis` on task 0 (F-7 / `0.md` F-0) |
| instantiation-stage gates re-run once on the final form | not performed by this audit: the artefacts are unchanged since the coordinator's gate snapshot cited under `### entry conditions`, and the audit runs no gates itself; a re-run belongs to the revision that follows rework |

**Per-task verdicts on the four relationships.**

| task | policy self-consistency | problem tree | factors | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | **SOURCE-FACTOR RED** | PASS | **SOURCE-FACTOR RED** |
| 1 | PASS | PASS | PASS | PASS | **PASS** |

The cross-difficulty merge surface and the scenario-level check are outside this skill and were not
run.

---

## revision_2

### charter_global_frozen (revision_2)

- freeze time: 2026-09-17 10:34 UTC, before any round-2 GT was read
- charter hashes: `protection.extended.yaml` **`c4e15e625c156e84`** (213445 bytes; changed from
  `67c9493c7707091d`) — every charter-global section is re-derived below in full;
  `task_tools.py` `8a8fe4fd4102957b` (unchanged) — `### action_binding_and_uuids` carried forward by
  reference on that hash.
- masked views: `0.json` `c2fbba94062cf753` (unchanged); `1.json` **`c2ded5d1c9e1d794`** (changed).
  What actually differs in `1.json`, verified table by table: `initial_state` is row-for-row identical
  to round 1 (all seven tables re-dumped and compared against the round-1 dumps: same 16 ledger rows,
  same plan, appraisal, two work orders, four service lines, membership); `frozen_time` unchanged; in
  `user_scenario` exactly one clause moved — "*the man at the counter had said at the time that it
  would not be covered because of the missed check-up*" → "*the man at the counter had warned him at
  the time that it might well not be covered*". The reworker's claim ("only a persona line") is
  confirmed on the artefact.
- entry conditions: the coordinator's round-2 gate block is cited (all seven gates OK;
  `check_traceability` excluded). Not re-run here.

### what changed in the charter (diffed against the round-1 policy dumps)

- `protection_ext_claim_settlement`: one new `overwrite` naming `protection_agg_allowance_pooling`'s
  window sentence; one new rule sentence "*Settlements stand on the plan as movements out of the
  allowance, so the benefit they consumed is read as the size of those movements*", carried into
  `compute_basis.allowance_standing` and `baseline.rule`. No compute change.
- `protection_ext_cancellation_refund`: factor `premium_paid_basis` **removed**; `premium_base` is now
  a plain binding `SUM(premium_paid) + SUM(premium_refunded)` with the rule sentence "*The premium the
  customer has paid toward the plan is the premium entries booked to it, net of the give-backs booked
  against them*" (also in `baseline.rule`). New factor **`coverage_run_basis`** (`method`, decides
  `months_elapsed`, bindings `order_handed_back`, `order_promised`, `months_elapsed`,
  `cross_difficulty: service`) with a new `cross_category` block reading `service.delivered_date`,
  `service.promised_date`. New `overwrite` naming `protection_cancellation_refund` sentence 1, with a
  replacing sentence now in the rule.
- `protection_ext_claim_refusal`: two new `overwrite` entries naming both `protection_included_services`
  sentences; `piece_value_taken` relabelled `method` with its tiers rewritten as methods; the
  whole-life fall-through of `services_window_months` (rule tier and `baseline`) now
  `MONTHS(F('effective_date'), NOW) + 1`; `baseline.params: []`.
- `protection_ext_allowance_reinstatement`: **no change** (0 diff lines).
- `protection_ext_transfer_carryover`: new `overwrite` naming `protection_transfer`'s fee sentence, with
  a replacing rule sentence; whole-life fall-through of `allowance_window_months` (rule tier and
  `baseline`) now `+ 1`; `coverage_year_months` dropped from `baseline.params`.
- Base section: all ten non-extended keys still verbatim against `blueprint/products/protection.yaml`.

### policy_conflict_scan (revision_2)

Re-run in full. Subjects, tools, computed quantities, triggers, eligibility, time anchors and terminal
states as in revision_1 — unchanged. Cross-category reads: `protection_ext_cancellation_refund` now
also declares `service` (`delivered_date`, `promised_date`) and its compute reads exactly those two
fields via `CFIELD('service', …, protection_claim_reference=claim_ref)`; the declaration and the
reads match. Every other policy's declared reads unchanged and still matched binding by binding. The
`prerequisite` graph is unchanged, so the two roots' closures and the scope partition are unchanged
and still disjoint and complete. No extended-vs-extended conflict.

### rule_compute_equivalence (revision_2)

Machine re-run on the new charter: every binding has a `compute_basis` entry, every basis sentence
and every `baseline.rule` sentence and every `overwrite.replaced_by` sentence is verbatim in its
policy's rule —
```
claim_settlement        29 bindings  miss=[] extra=[] not_in_rule=[]
cancellation_refund     19 bindings  miss=[] extra=[] not_in_rule=[]
claim_refusal           22 bindings  miss=[] extra=[] not_in_rule=[]
allowance_reinstatement 24 bindings  miss=[] extra=[] not_in_rule=[]
transfer_carryover      15 bindings  miss=[] extra=[] not_in_rule=[]
```
Backward sweep of the new sentences: the `coverage_run_basis` ladder is stated in the rule tier by
tier and implemented branch by branch in `months_elapsed`; the "handed back" state is
`service.delivered_date == ""`, the promised date is `service.promised_date`, and "later than the
handling date" is `order_promised > NOW` (ISO-string comparison, correct for dates). **O-1 closed**:
the sign convention is now a rule sentence. **O-2 closed** on the two fall-throughs that had it: the
engine's `0 <= m < within_months` test with `within_months = MONTHS(effective_date, NOW) + 1` now
admits the entry booked on the effective date itself (demonstrated below: the transfer's whole-baseline
moves from 9 399.95 to 12 899.95, which is the figure a literal reader of `baseline.rule` obtained in
revision_1).

### prerequisite_graph / prerequisite_sentences (revision_2)

The three edges, their `policy_source`, `condition`, `gate`, `form`, `resolved_by` are byte-identical
to round 1; each `policy_source` still verbatim in its own rule and absent from the depended-on rule;
each `gate` still a binding of the blocked compute (machine-checked). The new rule sentences were
swept for ordering connectives: "*keeps answering for the piece until it comes back*" (an in-policy
window definition, not a cross-problem order); "*taken at the counter when the piece is handed over*"
(a statement about where the fee lives, grounding no edge and naming no write of this difficulty).
No new or undeclared dependency. Sections carried forward otherwise.

### override_declarations (revision_2)

Every `superseded_clause` in all thirteen `overwrite` entries is verbatim in the named base policy's
rule (machine-checked, 13/13). Re-examined sentence by sentence:

- **F-1 closed.** `protection_cancellation_refund` sentence 1 is now named, replaced by "*The
  cancellation takes effect on the day the customer confirms it, and where it reaches the desk within
  the full-refund window … what is returned is worked out on the same proportion with no
  administration fee charged.*" Declared. **Merged reading — one caveat, new observation N-1:** that
  replacing sentence says *no administration fee* inside the window unconditionally, while the same
  rule's `administration_fee_charged` ladder waives the fee inside the window only "*and the plan's
  count of claims settled stands at zero*", otherwise falling through to the published fee. On a plan
  cancelled inside its full-refund window **after** a settlement the two sentences give different
  fees. Not demonstrable on any world of this difficulty (task 0's cancellation is 790 days after
  purchase against a 30-day window; task 1 has no cancellation), so recorded as an observation.
- **F-2 closed.** `protection_agg_allowance_pooling`'s coverage-year sentence is named in
  `protection_ext_claim_settlement.overwrite`, replaced by the rolling-window sentence already in the
  rule. Merged reading unique.
- **F-3 closed.** Both `protection_included_services` sentences are named in
  `protection_ext_claim_refusal.overwrite`, replaced by the window ladder and the goodwill ladder
  respectively, both already in the rule. Merged reading unique.
- **F-4 closed.** `protection_transfer`'s fee sentence is named, replaced by "*The coverage's transfer
  fee is taken at the counter when the piece is handed over and is not booked against the coverage
  being passed on, so the entries on it stay the transferring customer's own*", which is now in the
  rule and agrees with what `confirm_coverage_transfer_42b50f64` does and does not write. Unique.
- All other rows of the revision_1 tables re-checked and unchanged. Disguised-form sweep re-run on the
  new sentences: `months_elapsed` is a declared factor with a basis sentence, not an anonymous
  intermediate; no 0/1 multiplier; no dropped branch.

### factor_ladders (revision_2)

- `protection_ext_cancellation_refund`: 4 factors — `coverage_run_basis` (method, service),
  `months_still_to_run` (method), `unused_premium_share` (parameter), `administration_fee_charged`
  (parameter, circle): 2 parameter / 2 method, within bounds. **New factor examined:** three tiers —
  (not handed back ∧ promised date > handling date) / (not handed back ∧ promised date ≤ handling
  date) / otherwise — pairwise disjoint on their face; three distinct algorithms (count to the
  promised date / count to the handling date + 1 / count to the handling date); every tier a rule
  sentence and a `months_elapsed` branch; `decides` an input, bindings disjoint from the other three
  factors; fall-through = `baseline` (`MONTHS(F('purchased_date'), NOW)`) = the baseline rule's
  "*counted to the handling date*". Not multi-source (both conjuncts sit on one work-order record);
  task 0 keeps three other multi-source factors. Conditions are ones the line weighs (a piece still
  at the bench under a live claim); outcomes — the coverage counting the months it keeps answering for
  the piece as run — are a treatment a protection programme can publish. **Observation N-2:** tier 2
  charges the customer one extra month for a bench that has *missed* its promised date; defensible
  under the same "still answering for it" logic, but it is the customer who bears the workshop's
  lateness. No red light: the tier is not taken on task 0's world and its outcome is not one no such
  business would publish.
- `protection_ext_claim_refusal`: 5 factors, now 2 parameter / 3 method (**F-5 closed**:
  `piece_value_taken` is `method`, tiers reworded as methods). **F-6 closed**: `baseline.params: []`
  matches a baseline that reads no coverage parameter; `transfer_carryover.baseline.params` now
  `[new_tenure_share]`, the one key its baseline uses.
- `premium_paid_basis` no longer exists; `premium_base` is claimed by no factor (**F-7 closed at the
  charter level**; the world-level demonstration is in `0.md` → revision_2).
- All other ladders unchanged. Per-task counts: task 0 — 9 factors, 3 multi-source
  (`wear_reduction_rate`, `deductible_borne_by_customer`, `administration_fee_charged`), 6
  cross-difficulty (service ×4, circle ×2); task 1 — 15 factors, 6 multi-source, 4 cross-difficulty.
  Both floors met.

### findings (revision_2)

- **F-1, F-2, F-3, F-4, F-5, F-6, F-7, O-1, O-2 — closed** on the artefacts as they stand (evidence
  above). F-8, F-9, W-2, W-3 remain observations as in round 1.
- **N-1 — observation (new).** Two sentences of `protection_ext_cancellation_refund.rule` disagree on
  the administration fee for a plan cancelled inside the full-refund window after a settlement (the
  replacing sentence for base sentence 1 vs. tier 1 of `administration_fee_charged`). Symptom: two
  fees on that world. Root cause: the replacing sentence was written unconditional. Evidence:
  `extended_policies[1].overwrite[0].replaced_by` and `.factors[3].ladder[0].when`. Consequence: none
  demonstrable on either task's world. Affected artefact: `protection.extended.yaml`,
  `extended_policies[1].rule`. Bears on task 0.
- **N-2 — observation (new).** `coverage_run_basis` tier 2 (see `### factor_ladders (revision_2)`).
  Bears on task 0.

### closing_checklist (revision_2)

Written 2026-09-17 10:40 UTC after both revision_2 comparisons were on disk.

| item | state |
| --- | --- |
| one-to-one task files, `_difficulty.md` alongside, revision_1 preserved untouched with revision_2 appended | holds |
| every comparison section carries a PASS | **holds** — task 0 PASS, task 1 PASS |
| five extended policies covered; scopes pairwise disjoint and spanning whole trees | holds (unchanged graph; matches both `charter_scope` fields) |
| task tools and GT closed; frozen independent uuid8s | holds (`task_tools.py` unchanged, `8a8fe4fd4102957b`) |
| every tree: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input`, ≥ 1 `owner=user` problem, no cycle; difficulty-wide DAG | holds |
| every computation: self-sufficient baseline, 4–6 factors (≥2 parameter, ≥1 method), per task ≥1 multi-source and ≥1 cross-difficulty, ladders of ≥3 disjoint tiers stated in full, outcomes distinct and business-real | holds — refund now 2p/2m with the new `coverage_run_basis`; refusal 2p/3m |
| every factor bears weight against an honest baseline; baseline alone definite and ≠ gold | holds — 24/24 recomputed on the round-2 charter (`0.md`: 781.60 / 320.56 vs 1 064.90 / 246.67; `1.md`: 5 000.00 / 12 900.00 / 12 899.95 vs 3 118.50 / 10 061.00 / 2 245.32) |
| no tier read off a stamp | **holds** — F-7 closed |
| instantiation gates re-run on the final form | cited from the coordinator's round-2 block (all OK; `check_traceability` excluded); not re-run by this audit |

Open observations, none a red light: N-1, N-2 (new, charter), F-8, F-9 (task 0), W-2, W-3 (task 1).

| task | policy self-consistency | problem tree | factors | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | **PASS** |
| 1 | PASS | PASS | PASS | PASS | **PASS** |

**The difficulty passes the source-layer audit in revision_2.** Cross-difficulty merge and the
scenario-level check remain outside this skill.
