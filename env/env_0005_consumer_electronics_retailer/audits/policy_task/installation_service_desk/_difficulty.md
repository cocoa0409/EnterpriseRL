# Policy-task audit — installation_service_desk / charter-global

## charter_global_frozen

- freeze time: 2026-09-18 (session clock), written **before any task's GT was revealed**.
- auditor: independent policy-task auditor (not the instantiating agent).
- freeze hashes, recomputed here from the artifacts on disk:
  - `env/env_0005_consumer_electronics_retailer/tasks/installation_service_desk/service.extended.yaml` sha256_16 = `4791428acab8def1`
  - `env/env_0005_consumer_electronics_retailer/tasks/installation_service_desk/task_tools.py` sha256_16 = `4447a9f91273e801`
  - both agree with the hashes in the brief's masking report.
- verbatim-base check: the extended file's text up to `extended_policies:` is byte-identical to
  `env/env_0005_consumer_electronics_retailer/blueprint/products/service.yaml` (1769 lines, compared line by line; only a
  trailing-newline difference). The base copy has not been rewritten.
- fields permitted for this file: `blueprint.yaml`, `db_schema.json`, `share_tools.py`,
  `blueprint/products/service.yaml` (plus `membership.yaml` / `protection.yaml` for the cross-category tier figures the
  extended computes read), the whole of `service.extended.yaml`, the whole of `task_tools.py`.
- fields explicitly masked and not read while this file was written: every task's `evaluation_criteria`,
  `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`,
  `prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state`. Nothing in this file is derived from a
  revealed GT field.
- entry conditions (Step 0): the brief supplied the instantiation-gate snapshot (check_extended, check_task_tools,
  check_solvability, check_compute, check_grounding, check_cross_fire, replay_tasks --check — all reported OK) and the
  two mechanically masked views with their hashes. Entry conditions are **complete**; `check_traceability` is
  correctly deferred to the render step and was not run. The gates are cited, not re-run.

### policy_conflict_scan

Six extended policies, all `category: service`, over 15 base policies. Scan of overlapping subjects, triggers,
eligibility, time anchors, action parameters, terminal states and cross-category read boundaries:

| policy | trigger | subject | target_tool | computes | cross_category |
| --- | --- | --- | --- | --- | --- |
| service_ext_out_of_hours_surcharge | state_due | service_fee_charge | bill_out_of_hours_surcharge_9a215bff | surcharge_amount | — |
| service_ext_membership_service_relief | state_due | service_waiver | writeoff_service_charge_816a24da | waiver_amount | membership |
| service_ext_visit_settlement_payment | on_request | service_payment | settle_service_bill_ea31a412 | payment_amount | — |
| service_ext_declined_claim_labour_rebill | state_due | service_labour_charge | bill_uncovered_device_labour_51108cc0 | labour_amount | protection |
| service_ext_business_contract_relief | state_due | service_waiver | credit_contract_relief_ce7af535 | relief_amount | protection |
| service_ext_invoice_settlement_payment | on_request | service_payment | settle_deployment_invoice_642fded5 | payment_amount | protection |

- Subjects overlap in two pairs (`service_waiver` for policies 2 and 5; `service_payment` for policies 3 and 6), but
  each pair is separated by its own target tool and by a disjoint business ground (the membership ground / a term of a
  business contract; a consumer settlement at the desk / a business invoice settlement). No two policies compute the
  same quantity on the same tool.
- Eligibility: every write of the six falls inside the base state gates it inherits —
  `service_labour_pricing.billable_job_state` ("Labour is billed, and payments applied, only while the agreement
  stands dispatched, parts_hold or completed") and `service_attendance_and_cancellation.feeable_job_state`
  ("A no-show fee, cancellation fee, reschedule fee or trip charge is billed only while the agreement stands
  scheduled, dispatched, no_show or cancelled"). Note that `feeable_job_state` enumerates four fee kinds and does not
  name the out-of-hours surcharge, although `service_fee_charge` declares "a trip charge, a no-show fee, a reschedule
  fee, a cancellation fee, a haul-away fee, a diagnostic fee, a surcharge or a mileage charge" — the gate is narrower
  than the event it guards. Recorded as observation O-6.
- Time anchors: the six policies anchor on `F('scheduled_date')`, `F('dispatched_date')`,
  `F('parts_hold_started_date')`, `F('completed_date')` and `NOW`, all fields of the one holding row; no policy
  anchors on a date the customer supplies. Consistent.
- Terminal states: none of the six changes `service_agreements.status`; each lands one ledger row and moves
  `service_charges_outstanding`. No lifecycle transition is claimed twice.
- **One substantive conflict between two extended policies** (finding F-8 below): the out-of-hours surcharge is given
  two incompatible treatments. `service_ext_out_of_hours_surcharge` books it as a `service_fee_charge` of its own
  ("the surcharge that attendance adds is booked as a charge of its own against the line of work it belongs to"),
  while `service_ext_declined_claim_labour_rebill` folds the same surcharge into the labour rate
  (`P('base_labour_rate_usd_per_hour') * (1 + P('after_hours_surcharge_pct') / 100)`).
- Task scopes: the `prerequisite` graph has exactly two connected components —
  {service_ext_visit_settlement_payment -> service_ext_membership_service_relief -> service_ext_out_of_hours_surcharge}
  and
  {service_ext_invoice_settlement_payment -> service_ext_business_contract_relief -> service_ext_declined_claim_labour_rebill}.
  The two trees are pairwise disjoint and together cover all six extended policies, so the suite is jointly complete
  with disjoint scopes. (Derived from the `prerequisite` field alone; `charter_scope` was masked.)

### rule_compute_equivalence

Checked every quantity, window, filter, tier, branch, cross-category read, acting base, cap/floor and rounding point
of all six extended policies against `compute_basis` and `compute`, and swept back from `compute` to the rule.

Passing:
- Every `compute` binding of all six policies carries a `compute_basis` entry, and every entry I could locate as a
  verbatim (or near-verbatim, modulo the `>`-folded line wrapping) substring of that policy's own `rule`.
- Every rounding point is stated: `RND(..., 2)` against "rounded to the nearest cent" in all six; the floors
  (`MX(..., 0)`) against "never below nothing"; the caps (`MN(..., outstanding_all)` / `MN(..., unsettled)`) against
  "never exceeds the charges standing unsettled on the job, which are every charge booked on it less every payment
  received and every amount already written off".
- Every factor tier named in `factors[].ladder` is a sentence of the `rule` and a branch of the `decides` binding, and
  every branch of each `decides` binding is a tier the rule states. No tier lives only in `compute`, and no tier is
  promised in the rule and missing from `compute`.
- Interval counting: `MONTHS(...)`/`DAYS(...)` are used only where the rule says "the months since ..." /
  "the twelve months ending on the day ..." / "falls on a Saturday or a Sunday".
- Cross-category reads are confined to the categories each policy declares (`membership` for policy 2; `protection`
  for policies 4, 5, 6) and to fields those `cross_category.reads` lists.

Three places where `compute` implements a branch the `rule` does not state, or a quantity the rule does not name.
None of the three is realised on either task's world (see each task file), so all three are recorded as observations,
not as `SOURCE-POLICY RED`:

1. `service_ext_out_of_hours_surcharge.rate_pct` — rule: "it is the service's after-hours surcharge percent where
   that day falls **from Monday to Friday** and the slot booked for the attendance stood in the evening; and it is no
   surcharge at all in every other case." compute: `P('after_hours_surcharge_pct') if (attendance_dow > 0 and
   F('scheduled_window') == 'evening') else 0`. With the anchor `DAYS('2026-01-04', rate_day) % 7` (2026-01-04 is a
   Sunday, so 0 = Sunday and 6 = Saturday), `attendance_dow > 0` admits Saturday. On a Saturday-evening slot the rule
   gives no surcharge at all (the weekend branch requires a window "other than the evening"; the after-hours branch
   requires Monday to Friday) while compute gives the after-hours percent. Observation O-1.
2. `service_ext_visit_settlement_payment.reliefs_recognised` — rule: "it is the write-offs granted as goodwill where
   those **are the only write-offs** standing on the job"; compute: `goodwill_waivers if goodwill_waivers > 0 else 0`,
   i.e. "goodwill write-offs exist". Where a retailer_error write-off and a goodwill write-off both stand and no
   membership one does, the rule falls through to "nothing" and compute returns the goodwill figure. The same shape
   appears in `service_ext_invoice_settlement_payment.relief_recognised` (`plan_waivers if plan_waivers > 0`) against
   "where those are the only write-offs standing on the job". Observation O-2.
   (`service_ext_declined_claim_labour_rebill.writeoff_offset` does **not** have this defect: its `else` branch already
   excludes `plan_writeoffs > 0`, matching "and none granted on the plan's cover does".)
3. `service_ext_declined_claim_labour_rebill.line_attendances` = `labour_lines_all - labour_lines_completed` and
   `service_ext_business_contract_relief.attendances_rebilled` = `labour_rows_all - labour_rows_completed -
   labour_rows_today`. The rule names, respectively, "**the line the plan refused** carries labour for more than one
   attendance day" and "the attendances rebilled"; both compute expressions count labour rows across **every** line of
   the job, ignore `work_order_line_reference` entirely, and (in the second case) subtract out the very rows the
   rebill has just created. No sentence of either rule states this basis, and the `compute_basis` entries for the two
   bindings quote sentences about something else ("The hours rebilled are chosen as follows", "the visits creditable
   are set against the attendances rebilled"). Observation O-3.

One inherited defect of the base copy, recorded because it is part of the charter now in force:
`service_labour_pricing.rule` states "Chargeable labour is the hours actually worked, **rounded up as the service's
rounding basis states** and raised to the service's minimum hours, times the service's hourly rate", while its own
`formula` is `round(max(minimum_labour_hours, labour_hours) * base_labour_rate_usd_per_hour, 2)` — the rounding basis
is stated in the rule and implemented nowhere, and no extended policy reads `labour_rounding_basis` either. Origin:
`env/env_0005_consumer_electronics_retailer/blueprint/products/service.yaml`. Observation O-4.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: all six distinct, each tool claimed by exactly one policy (table above). No tool
  is the target of two policies and no policy names two tools.
- Each policy's subject, `base_policy_refs`, target tool, tool docstring and terminal state admit one business
  reading. No docstring adds a confirmation, a review, a wait or a procedure outside its policy.
- No docstring states an action's position in a sequence, names another tool, or names another policy. The word
  "before" appears 23 times across `task_tools.py`, in every case inside an `Args:` entry about where that one
  argument is read from ("read from the work orders held on the customer's profile before the call", "as the agent
  hands it over before the call") or about rounding it ("rounded half up to the cent before it is passed"). None of
  them orders one problem against another. Passes.
- uuid8s, checked one by one: `9a215bff`, `816a24da`, `ea31a412`, `ce7af535`, `51108cc0`, `642fded5`. All eight hex
  digits; no shared prefix or suffix, no sequence number, no adjacency, no reuse, no tail variation on a common stem.
  Independently generated and frozen. Passes.
- Tool bodies: all six create exactly one `service_events` row and update `service_agreements.service_charges_outstanding`
  by the amount passed. None of them reads a status, judges a prerequisite, refuses a call, raises an error, or emits a
  hint. `bill_out_of_hours_surcharge_9a215bff` hard-codes `charge_kind="after_hours_surcharge"`, which is the only
  surcharge value the `charge_kind` enum in `db_schema.json` carries, so a weekend surcharge is also filed under it —
  and policy 2's `surcharge_rows` / `surcharge_last_sent` filter on exactly that value, so the pair is consistent.
  Observation O-5 (naming only).

### prerequisite_graph

Four edges, all `kind: value_input`:

| blocked policy | depends on | gate | form | resolved_by | effect verified? |
| --- | --- | --- | --- | --- | --- |
| service_ext_membership_service_relief | service_ext_out_of_hours_surcharge | surcharge_scope | state | bill_out_of_hours_surcharge_9a215bff | yes |
| service_ext_visit_settlement_payment | service_ext_membership_service_relief | reliefs_recognised | state | writeoff_service_charge_816a24da | yes |
| service_ext_business_contract_relief | service_ext_declined_claim_labour_rebill | labour_rebilled_today | state | bill_uncovered_device_labour_51108cc0 | yes |
| service_ext_invoice_settlement_payment | service_ext_business_contract_relief | relief_recognised | state | credit_contract_relief_ce7af535 | yes |

- `prerequisite` is filled in on all six policies (`[]` on policies 1 and 4, which are the two chain roots).
- Every `problem` points at another **extended** policy id in this file; none points at a base policy or at itself.
- The graph is two disjoint chains of three nodes each; acyclic, and no cross-task reference creates a cycle.
- Every `policy_source` is verbatim locatable in the **blocked** policy's own `rule` (quoted in
  `prerequisite_sentences` below).
- `form: state` on all four; no `fallback_reason` is present, which is correct because no edge is action-form.
- `kind: value_input` on all four, and each `gate` names a binding that genuinely exists in that policy's `compute`:
  `surcharge_scope`, `reliefs_recognised`, `labour_rebilled_today`, `relief_recognised`. None is `result`.
- Each `resolved_by` is the depended-on policy's own `target_tool`, and each `effect` genuinely holds (verified
  numerically against each task's world in that task's file).
- No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears anywhere in the four
  `prerequisite` blocks.
- One scope note: the edge `service_ext_business_contract_relief -> service_ext_declined_claim_labour_rebill` carries
  `condition: "a chargeable labour entry for the line the plan refused stands on the job, **booked on the day the
  relief is granted**"`, while its `policy_source` sentence says only "stands billed on the job". The condition is
  strictly stronger than the sentence it is drawn from. The extra scope is recoverable from another sentence of the
  same rule ("That share is applied to the chargeable labour billed on the day the relief is granted"), so the agent
  can still discover it; recorded as observation O-7 rather than a red light.

### prerequisite_sentences

Four-point test on each of the four sentences. All four join the blocked policy's own result to what it waits on with
an explicit ordering connective, state a record-visible state in table words with no action / performer / tool, name no
tool, policy id, snake_case token or row id, and sit at the strength the edge's condition carries (with the one
exception noted as O-7).

1. `service_ext_membership_service_relief`: "The relief is worked out **only after** the surcharge entry owed for the
   attendance it covers stands on the job's account."
   Derivation to a single reading: the waited-on state is a surcharge entry standing on the job. Reading the other five
   policies' rules, exactly one describes booking a surcharge entry —
   `service_ext_out_of_hours_surcharge` ("the surcharge that attendance adds is booked as a charge of its own against
   the line of work it belongs to") — whose `target_tool` is `bill_out_of_hours_surcharge_9a215bff`, the only tool in
   the module that creates a `service_fee_charge` row. One write, one reading.
2. `service_ext_visit_settlement_payment`: "The figure the customer settles is worked out **only after** the write-off
   owed on the membership ground stands recorded against the job's charges."
   The waited-on state is a write-off on the membership ground. Exactly one policy describes granting one
   (`service_ext_membership_service_relief`: "A write-off granted on the membership ground sets the membership's
   service credit against the charges standing unsettled on the job"), target
   `writeoff_service_charge_816a24da`. One reading. (See O-8: at the *tool* layer the ground enum is shared with
   `credit_contract_relief_ce7af535`, so the hop is resolved by the policies' subject matter rather than by the tool
   contracts alone.)
3. `service_ext_business_contract_relief`: "The relief is fixed **only once** the chargeable labour the plan's refusal
   sends back to the customer stands billed on the job."
   The waited-on state is a chargeable labour entry for the refused line. Exactly one policy describes creating one
   (`service_ext_declined_claim_labour_rebill`: "the labour of that line is rebilled to the customer as chargeable
   work"), target `bill_uncovered_device_labour_51108cc0`, the only tool that creates a `service_labour_charge` row.
   One reading.
4. `service_ext_invoice_settlement_payment`: "The figure the invoice settles is worked out **only after** the relief
   the business contract owes stands recorded against the job's charges."
   The waited-on state is a write-off granted on a term of the business contract. Exactly one policy describes it
   (`service_ext_business_contract_relief`: "A business profile whose contract carries included visits is relieved of
   what those visits should have covered"), target `credit_contract_relief_ce7af535`. One reading (same O-8 caveat).

Nothing else about a dependency is carried in any rule: no second ordering sentence, no tool name, no other problem's
id. The depended-on policies' rules do **not** restate the sentence (policy 1 never mentions the relief, policy 2 never
mentions the settlement, policy 4 never mentions the contract relief, policy 5 never mentions the invoice settlement).
No base rule sentence states a cross-problem order that grounds one of these edges.

### override_declarations

Two `overwrite` clauses are declared in the whole charter, both named at base-sentence granularity, and both hold:

- `service_ext_membership_service_relief` supersedes `service_combo_plan_membership_interaction`'s "the membership
  tier's repair labour discount is taken off the chargeable labour before any surcharge is added", replaced by "Where
  the labour was billed before the discount had been taken off it, the relief covers the same share of the surcharge
  booked on that labour as it covers of the labour itself". Merged semantics unique.
- `service_ext_declined_claim_labour_rebill` supersedes `service_excl_warranty_or_chargeable`'s "A customer cannot be
  billed for labour on a line whose charge has been written off as plan covered", replaced by "Where a plan's decision
  refuses a claim after the work was carried out as plan work, the labour of that line is rebilled to the customer as
  chargeable work, and the write-off the plan's cover carried is not set against the rebilled figure". Merged semantics
  unique.

Sentence-by-sentence sweep of every `base_policy_refs` entry of all six policies (15 base policies, ~90 sentences).
Conclusions reached on each; the ones that are *not* simply inherited are:

**F-1 — undeclared override (`SOURCE-POLICY`), `service_ext_out_of_hours_surcharge`, `overwrite: []`.**
Base `service_appointment_scheduling`: "Work outside the service's ordinary hours or at a weekend carries the service's
surcharge on the labour, and the two surcharges are not both applied to the same hour." Base
`service_labour_pricing`: "Chargeable labour is the hours actually worked ... raised to the service's minimum hours,
times the service's hourly rate", `formula: round(max(minimum_labour_hours, labour_hours) *
base_labour_rate_usd_per_hour, 2)`. Base therefore fixes the surcharge base as the chargeable labour as billed.
The extended policy handles that same quantity differently, in two places, with no new parameter name (the
"anonymous intermediate factor" form — the deviation lives entirely in the intermediate `net_base`):
"where write-offs already stand on the job, **the write-offs recorded on it come off the labour before the surcharge is
worked out**", and "where no write-off stands on the job and the labour was booked at a rate other than the service's
own hourly rate, the labour is restated as the hours recorded on the latest labour entry multiplied by the service's
hourly rate". Neither is named in `overwrite`. The value an agent computes by following the base clause differs from the
value the extended policy computes. Bears on **task 0** (demonstration in `0.md`, §findings F-1).

**F-2 — undeclared override + internal contradiction (`SOURCE-POLICY`), `service_ext_membership_service_relief`.**
The declared `overwrite` covers only the discount-before-surcharge clause. Base
`service_combo_plan_membership_interaction` continues: "and the membership's service benefit credit may then be spent
against what is left." The extended policy handles that quantity differently: it first sets the credit as "the unspent
benefit credit standing on the membership" and then holds back from it "what the membership year has already taken"
(`spent_offset = credit_spent_window`, an `XSUM` of `membership_benefit_redeem` rows inside the window). The rule is
self-contradictory on its face — the *unspent* credit is by construction the granted credit less every redemption, so
subtracting a subset of those same redemptions a second time deducts them twice — and the deviation from base is not
declared. Bears on **task 0** (demonstration in `0.md`, §findings F-2).

**F-3 — undeclared deviation from base's chargeable-labour formula (`SOURCE-POLICY`, consequence not demonstrable on
either task's world → recorded as an observation).** `service_ext_declined_claim_labour_rebill`'s `overwrite` names
only the `service_excl_warranty_or_chargeable` clause. Base `service_labour_pricing` raises the hours to the minimum
once ("raised to the service's minimum hours"; `formula: max(minimum_labour_hours, labour_hours)`). The extended rule
handles the same quantity three ways — "the service's minimum hours are applied once to the total"; "the service's
minimum hours are **doubled** for that attendance"; "the service's minimum hours are applied to the attendance the crew
was dispatched for and to the remaining hours separately, and the two raised figures are added". The second and third
reach different numbers from base in the same situation, and neither is declared. On task 1's world the first branch is
taken and coincides with base, so no consequence is demonstrable there; recorded as observation O-9 with the branch
arithmetic in `1.md`.

Every other base provision — `service_agg_multi_holding`'s dedup, `service_parts_handling`'s deposit and hold-day
counting, `service_diagnostic_scope`'s diagnostic-fee credit ("where the customer goes ahead with the repair the fee is
credited against it in full", implemented faithfully by `diagnostic_fee_credit`),
`service_attendance_and_cancellation`'s notice/fee structure, `service_completion_and_workmanship`'s rework window and
liability cap, `service_visit_allowance` / `service_agg_visit_pool`'s pool arithmetic, `service_charge_waivers`'
recognised grounds and strongest-ground ordering, `service_excl_warranty_or_chargeable`'s one-basis-per-line rule — is
inherited in full and is neither weakened by an extended rule, by a tool body nor by a persona line. One granularity
drift is recorded as observation O-10: `service_charge_waivers` caps a write-off at "the charge outstanding on **the
line** it is granted against", while policies 2, 5 and 6 cap at the charges outstanding on **the job** ("every charge
booked on it less every payment received and every amount already written off").

### factor_ladders

32 factors over six policies. Counts, per policy:

| policy | factors | parameter | method | multi-source tiers | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| service_ext_out_of_hours_surcharge | 4 | 2 | 2 | surcharge_labour_figure | — |
| service_ext_membership_service_relief | 6 | 5 | 1 | labour_relief_share | membership ×4 |
| service_ext_visit_settlement_payment | 4 | 2 | 2 | money_already_held | — |
| service_ext_declined_claim_labour_rebill | 6 | 4 | 2 | rebilled_share_after_decision | protection |
| service_ext_business_contract_relief | 6 | 5 | 1 | creditable_included_visits, crew_attendance_charge_relief, distance_charge_relief, slot_move_fee_relief, labour_share_relieved | protection |
| service_ext_invoice_settlement_payment | 6 | 4 | 2 | invoice_fee_scope, next_invoice_deferral, plan_met_on_invoice | protection |

Every policy is inside the 4–6 bound with at least 2 `parameter` and at least 1 `method`. Each chain therefore carries
at least one multi-source factor and at least one `cross_difficulty` factor (chain A: membership, via policy 2;
chain B: protection, via policies 4, 5 and 6).

Structure checks that pass for all 32: every `decides` names an input binding and never `result`; the `bindings` sets
of the factors within one policy are disjoint; each ladder has exactly three tiers, the fall-through counted, and the
three are pairwise disjoint as stated; every tier's value or method is drawn from the charter (a `P(...)` tier
parameter, a `CPARAM(...)` cross-category tier parameter, or an aggregate over seeded rows); no two tiers of one ladder
select the same value or method as stated; every tier — its condition and its value or method — is a sentence of the
policy's own `rule` and a branch of the `decides` binding in `compute`.

Structure checks that **fail**:

**F-4 — dishonest baseline, systematic (`SOURCE-FACTOR`).** Three of the six policies' `baseline.rule` restate one
factor's *entire ladder* rather than that factor's fall-through alone, so the factor's declared `baseline` is not what
`baseline.rule` states for that input, and a reader of the computation document alone already lands on the scored
tier:

- `service_ext_membership_service_relief.baseline.rule` contains "The labour the relief is worked out on is chosen as
  follows: where a payment has already been received on the job and the job carries labour for two or more
  attendances, the labour booked for the day the crew was last sent out is the figure taken; where no payment has been
  received on the job, every labour charge standing on the job is the figure taken; and in every other case the labour
  standing on the job less the payments already received against it is the figure taken." — the complete ladder of the
  factor `relief_labour_figure`, whose declared `baseline` is only the third clause
  (`discount_base: "MX(labour_total - payments_total, 0)"`).
- `service_ext_visit_settlement_payment.baseline.rule` contains the complete ladder of `settlement_charge_scope`
  ("The charges the settlement covers are chosen as follows: ... only the charges booked for the day the crew was last
  sent out are covered; ... every charge standing on the job is covered; and in every other case every charge standing
  on the job less the payments already received against it is covered."), whose declared `baseline` is only
  `scope_total: "MX(charges_total - payments_total, 0)"`.
- `service_ext_declined_claim_labour_rebill.baseline.rule` contains the complete ladder of `rebilled_hours_selection`
  ("The hours rebilled are chosen as follows: ... the hours recorded on the job less the hours recorded for the day it
  was completed ...; ... the hours recorded on the job ...; and in every other case the hours recorded for the day the
  crew was dispatched ..."), whose declared `baseline` is only `hours_selected: "hours_dispatch_day"`.

Bears on **task 0** (first two) and **task 1** (third); the figure-by-figure demonstration that `baseline.rule` alone
yields the scored tier value is in each task file under `factor_weight`.

**F-5 — dishonest baseline, `minimum_hours_application` (`SOURCE-FACTOR`).**
`service_ext_declined_claim_labour_rebill.baseline.rule` carries **no sentence at all** about applying the service's
minimum hours — it goes straight from the hours ladder to "The hours and the rate are multiplied and the outcome
rounded to the nearest cent" — yet `baseline.params` lists `minimum_labour_hours`, and the factor
`minimum_hours_application` declares `baseline: hours_billed: "MX(hours_dispatch_day, P('minimum_labour_hours')) +
MX(hours_second, P('minimum_labour_hours'))"`. That figure cannot be derived from `baseline.rule` by any reading:
`baseline.rule` multiplies the *selected* hours by the rate directly (and base `service_labour_pricing` would raise
them to the minimum once, not twice). Bears on **task 1**.

**F-6 — incoherent baseline, three policies (`SOURCE-FACTOR`).** A `baseline.rule` must let a reader compute a
definite number from it and the records with no factor applied. Three do not:

- `service_ext_visit_settlement_payment.baseline.rule` subtracts and adds three components it never defines — "plus
  the older charges standing unsettled that are due with them, less the relief already recognised on the job and less
  the money already held against those charges" — while the three corresponding factors (`older_charges_due`,
  `relief_recognised_ground`, `money_already_held`) all have "nothing" as their fall-through. The document tells the
  reader to add and subtract quantities it gives no method for, and the intended baseline answer is that all three are
  zero, contradicting the sentence that they are added and subtracted.
- `service_ext_business_contract_relief.baseline.rule`: "To it are added the attendance charges the contract does not
  leave with the business." Which charges, and how much, is stated nowhere; the three fee factors
  (`crew_attendance_charge_relief`, `distance_charge_relief`, `slot_move_fee_relief`) all have `baseline: 0`, so the
  baseline adds nothing at all to the figure the sentence says it adds to.
- `service_ext_membership_service_relief.baseline.rule`: "adds to it the share of the job's chargeable labour that the
  membership's own discount should have taken off" — the share itself (`relief_rate`, baseline `0`) is never stated, so
  the sentence's own quantity is indeterminate from the baseline document.

**F-7 — a conjunct that divides no customer the policy admits (`SOURCE-FACTOR`), `next_invoice_deferral` in
`service_ext_invoice_settlement_payment`.** Tier 1 is "**the profile's invoices run to the service's payment terms**
and a write-off granted on a term of its business contract stands on the job"; tier 2 is "**those invoices run to the
service's payment terms** and no such write-off stands on the job"; the fall-through, on which the factor's
`baseline: terms_deferral: "charges_today + fees_in_scope"` rests, is everything else — i.e. `P('payment_terms_days')
== 0`. In the charter, `payment_terms_days` is 30 for TechWorks Business On Site Deployment and 45 for TechWorks
Managed IT Care Annual, and 0 on the four consumer services only. The policy's own scope is "When a business asks to
settle the invoice standing on a job", and the tool is `settle_deployment_invoice_642fded5` ("Let a **business**
customer settle the service charges invoiced on one of their TechWorks jobs"). The shared conjunct therefore holds of
every customer who reaches this write and restates the policy's scope instead of dividing its customers, and the tier
the baseline rests on is one the policy's scope excludes. The only thing that actually divides tiers 1 and 2 is whether
the contract write-off stands — which is precisely the state the declared prerequisite edge brings about. Bears on
**task 1**.

**F-8 — two treatments of one quantity in one charter (`SOURCE-POLICY`; consequence not demonstrable on either task's
world → observation O-11).** `service_ext_out_of_hours_surcharge` books the out-of-hours surcharge as a
`service_fee_charge` of its own, while `service_ext_declined_claim_labour_rebill.rebill_rate` tier 2 folds the same
surcharge into the hourly rate ("the service's own hourly rate raised by its after-hours surcharge percent"). On a job
to which both policies applied the same hour would carry the surcharge twice, against base
`service_appointment_scheduling`'s "the two surcharges are not both applied to the same hour". The two policies sit in
different chains, so no single task exercises both.

Realism of conditions and outcomes — the tiers I judge **not** to be what this line of business does:

- **O-12.** `service_ext_business_contract_relief.plan_met_of_same_work` tier 2 deducts "**the per-claim limit of the
  plan**" as "what the plan has met of the same work". A per-claim limit is a ceiling, not an amount paid; the
  structurally identical factor in the sibling policy (`plan_met_on_invoice` tier 2) deducts "what the plan has
  already **paid out** on the item" for the same situation. Two policies of one charter answer the same question two
  ways, and one of the two answers is a quantity no service business would net off an invoice.
- **O-13.** Both of those factors' **fall-through** tiers deduct "**the coverage still standing on the plan**" as
  "what the plan has met of the same work" — the coverage still standing is by definition the part the plan has *not*
  met. Since the fall-through is the baseline, the computation document alone tells a reader to deduct the plan's whole
  unused coverage pool from a service invoice.
- **O-14.** `service_ext_business_contract_relief.labour_share_relieved`'s fall-through is
  `pool_left / P('included_visits_per_term')`, which divides by zero on TechWorks In Store Bench Service
  (`included_visits_per_term: 0`). The policy's scope ("A business profile whose contract carries included visits")
  keeps that variant out in practice, but the baseline as written is not total.
- **O-15.** `service_ext_business_contract_relief`'s `creditable_included_visits` tier 1 and `distance_charge_relief`
  tier 1 both turn on "the job stands in the priority response queue". The two services the policy's scope admits are
  the two the charter gives `priority_response: true`, so on the policy's own domain that conjunct is close to
  universal; it remains a genuine divider only because `priority_flag` is a per-agreement field that a seed may set
  false.
- **O-16.** Effect labels are not applied consistently to structurally identical factors: `surcharge_labour_figure`
  ("pick one of three sums of labour rows by the same condition") is `parameter` while `settlement_charge_scope` (the
  same shape over charge rows) is `method`; `invoice_fee_scope` is `parameter` while `invoice_labour_scope`, its twin in
  the same policy, is `method`. The `method` floor of 1 per policy is met in every case by a factor whose label is
  honest on its own terms (an anchor, a window, or a share formula), so no count is broken by this.
- **O-17.** Two rule promises are not implemented and cannot be, because the scored quantity is a single amount:
  "the oldest of the charges it covers is cleared first" (policy 3) and "the payments already received are taken off
  the charges **in the order they came in**" (policy 6 / `money_already_held_on_invoice` tier 2, compute
  `payments_all`). Neither changes any number.

### findings

Charter-global findings, each naming the tasks whose files carry the demonstration.

| id | verdict | subject | bears on |
| --- | --- | --- | --- |
| F-1 | SOURCE-POLICY RED | undeclared override: write-offs and rate restatement moved the surcharge base away from base `service_appointment_scheduling` + `service_labour_pricing`, `overwrite: []` | task 0 |
| F-2 | SOURCE-POLICY RED | undeclared override + self-contradiction: already-spent benefit credit held back a second time from the unspent balance | task 0 |
| F-4 | SOURCE-FACTOR RED | dishonest baseline: `baseline.rule` restates a factor's whole ladder in policies 2, 3 and 4 (`relief_labour_figure`, `settlement_charge_scope`, `rebilled_hours_selection`) | tasks 0, 1 |
| F-5 | SOURCE-FACTOR RED | dishonest baseline: `minimum_hours_application`'s baseline is stated in no sentence of `baseline.rule` | task 1 |
| F-6 | SOURCE-FACTOR RED | incoherent baseline: `baseline.rule` of policies 2, 3 and 5 names components it gives no method for | tasks 0, 1 |
| F-7 | SOURCE-FACTOR RED | `next_invoice_deferral`: the shared conjunct holds of every customer the policy admits, and the baseline rests on a tier the scope excludes | task 1 |
| F-3 | observation (O-9) | undeclared deviation from base's minimum-hours formula (doubling, and applying it twice) | task 1 |
| F-8 | observation (O-11) | the charter charges the out-of-hours surcharge two ways | — |
| O-1 | observation | `rate_pct` gives the after-hours percent on a Saturday evening where the rule gives none | — |
| O-2 | observation | "the only write-offs" implemented as "write-offs exist" in policies 3 and 6 | — |
| O-3 | observation | `line_attendances` / `attendances_rebilled` count rows the rule does not name | tasks 1 |
| O-4 | observation | base `service_labour_pricing` states a rounding basis nothing implements (inherited) | — |
| O-5 | observation | a weekend surcharge is filed under `charge_kind="after_hours_surcharge"` | task 0 |
| O-6 | observation | `feeable_job_state` enumerates fewer fee kinds than `service_fee_charge` carries | task 0 |
| O-7 | observation | edge 5→4's `condition` is stronger than its `policy_source` sentence | task 1 |
| O-8 | observation | both waiver tools accept the whole ground enum, so either could bring a waited-on state about | tasks 0, 1 |
| O-10 | observation | write-off cap moved from the line (base) to the job (extended) | tasks 0, 1 |
| O-12..O-17 | observations | realism and labelling, listed in `factor_ladders` above | tasks 1, 0 |

## closing_checklist

Written after both task files carried a frozen `source_derivation_frozen` and a `source_gt_comparison`. This is the
one difficulty-level conclusion reached **after** the reveals; everything above it is pre-reveal by construction and
was not touched afterwards.

**The difficulty does not close out.** Not all four relationships PASS on both tasks.

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | **SOURCE-POLICY RED** (F-1, F-2) | **SOURCE-CHAIN RED** (F-10, F-11) | **SOURCE-FACTOR RED** (F-4, F-6) | PASS |
| 1 | PASS for this task | **SOURCE-CHAIN RED** (F-12, F-13, F-14) | **SOURCE-FACTOR RED** (F-4, F-5, F-7) | **SOURCE-TASK RED** (F-9) |

Checklist items, item by item:

- **Audit files correspond one-to-one with the tasks.** `0.md`, `1.md` and this `_difficulty.md` sit alongside one
  another in `env/env_0005_consumer_electronics_retailer/audits/policy_task/installation_service_desk/`. No previous revision
  exists, so nothing has been overwritten; both comparison sections carry a verdict, and neither carries PASS on all
  four relationships.
- **Extended policies fully covered, scopes pairwise disjoint.** Confirmed against the revealed `charter_scope`:
  task 0 claims {service_ext_out_of_hours_surcharge, service_ext_membership_service_relief,
  service_ext_visit_settlement_payment} with tools {bill_out_of_hours_surcharge_9a215bff,
  writeoff_service_charge_816a24da, settle_service_bill_ea31a412}; task 1 claims
  {service_ext_declined_claim_labour_rebill, service_ext_business_contract_relief,
  service_ext_invoice_settlement_payment} with tools {bill_uncovered_device_labour_51108cc0,
  credit_contract_relief_ce7af535, settle_deployment_invoice_642fded5}. Disjoint, and together all six policies and
  all six tools. This matches the two components of the `prerequisite` graph derived pre-reveal. **PASS.**
- **Task tools and GT closed; uuid8s independently generated and frozen.** Every gold write of both tasks calls one of
  the six tools through the unlock/call pair, and every argument traces to a seeded row, a preceding gold write or a
  persona line. The six uuid8s (`9a215bff`, `816a24da`, `ea31a412`, `ce7af535`, `51108cc0`, `642fded5`) share no
  prefix, sequence or tail pattern. **PASS.**
- **Problem trees.** Both are chains of three problems: one root and two prerequisite problems (n = 2), two
  `value_input` edges each (≥ max(n−1,1) = 1), one `owner=user` write per tree at the root, no cycle. The four edges of
  the difficulty together remain a directed acyclic graph, with no cross-task reference. Structurally **PASS**; but see
  the SOURCE-CHAIN findings above — three of the four edges have a `prerequisite_closure` proof field whose asserted
  figures are wrong (F-10, F-12, F-13), and one edge (task 1's rebill) leaves the root problem's own scored figure
  unchanged (F-14).
- **Computations, baselines and factors.** Six computations, 32 declared factors (6+4+4 on task 0, 6+6+6 on task 1),
  every policy inside the 4–6 bound with ≥ 2 `parameter` and ≥ 1 `method`, every ladder three pairwise-disjoint tiers
  stated in full in its own `rule`, and **all 32 proved to bear weight on their task's world** — I recomputed every one
  of the 32 `factor_sensitivity` figures and all six `baseline_result` figures independently and they agree with the
  artifacts to the cent, and each of the six whole-baseline figures is definite and differs from gold. Each task
  carries at least one multi-source and at least one cross-difficulty factor, and the cross-difficulty rows
  (membership for task 0, protection for task 1) are seeded. **However**: four factors rest on a baseline their own
  policy's `baseline.rule` contradicts (F-4), one rests on a baseline no published sentence states (F-5), three
  `baseline.rule`s are not self-sufficient (F-6), and one ladder divides no customer its policy admits (F-7). So the
  factor relationship **FAILS** on both tasks, on the honesty of the baselines rather than on the weight of the
  factors.
- **Instantiation-stage gates re-run on the final form.** Not applicable and not done: the artifacts are unchanged by
  this audit (write domain is this directory only), so the gate snapshot supplied with the brief still describes the
  form audited. The audit did not run `replay_tasks.py`, so no `db_closure` was rewritten.

**Summary of what must be answered before this difficulty can pass**, by relationship:

1. Policy self-consistency (task 0): the undeclared deviations F-1 (the surcharge base) and F-2 (the benefit credit
   deducted twice) each hand the task a second defensible figure from a base clause the KB publishes beside the
   extended one.
2. The problem tree (both tasks): five figures asserted in `prerequisite_closure` / `design_rationale` are false on
   their own worlds (F-10, F-11, F-12, F-13), and in both tasks the published order-uniqueness argument ("no other
   order reproduces the terminal state") is refuted by recomputation — both orders clear the job in both tasks.
   Task 1's rebill edge moves no figure the root problem produces (F-14).
3. Factors bear weight (both tasks): the baseline layer, not the factor layer — F-4, F-5, F-6, F-7.
4. Unique solution (task 1): the rebill entry's `visit_date` has two equally defensible values (F-9).

Nothing in this audit is attributed to a solving agent, and no fix is designed or arranged. The artifacts under
`tasks/` and `blueprint/` were not modified.

---

## revision_2

Re-audit of the charter-global relationships against the reworked artifacts. Revision 1 above is untouched.

### revision_2 / grounds for re-deriving

Hashes recomputed by me from the files on disk, not taken from the brief:

| artifact | sha256_16 now | relation to the revision-1 section |
| --- | --- | --- |
| `tasks/installation_service_desk/service.extended.yaml` | `5bf8b103571b5ea2` | **changed** — every charter-global section is re-derived in full below |
| `tasks/installation_service_desk/task_tools.py` | `4447a9f91273e801` | **unchanged by content** — this is the same value revision 1's `charter_global_frozen` records, computed the same way, so §`action_binding_and_uuids` is carried forward by reference and not re-derived |
| `tasks/installation_service_desk/tasks/0.json` | `cd12464539dbb86c` | changed |
| `tasks/installation_service_desk/tasks/1.json` | `7b4731fcee60c676` | changed |
| `blueprint/products/service.yaml` | `e673ca021b79484f` | base copy re-verified below |
| `blueprint/products/protection.yaml` | `e93deb59bd7503ab` | tier figures re-read below |
| `blueprint/products/membership.yaml` | `c6245922d2ecd6ff` | tier figures re-read below |

**Base copy still verbatim.** The extended file's text up to `extended_policies:` is 1769 lines and compares
line-for-line identical to `blueprint/products/service.yaml`, zero differences in the common prefix. The reworker
did not touch base, and base is still the clause set in force.

**Blueprint tier figures re-read by content** (no historical hash relied on): ShieldCare Business Fleet Protection
still `coverage_limit_usd 45000.0`, `per_claim_limit_usd 9000.0`, `monthly_premium_usd 39.0`; Circle Total Annual
still `repair_labour_discount_pct 25`, `service_benefit_credit_usd 50.0`, `max_benefit_redemptions_per_year 12`.
So the two corrected task-1 seed rows were corrected *towards* an unchanged blueprint, not by moving the blueprint.

**Note on the masked-view substitution disclosed by the coordinator.** Nothing in revision 1's record rests on row
order. The only order-sensitive primitive in the DSL is `LATEST`/`XLATEST`, which compares `date_field` values and
keeps the first row on a tie (`key > best[0]`); in both tasks every `LATEST` is taken over distinct dates
(`visit_date` 2026-09-04 / 2026-09-12 in task 0; `event_date` 2026-09-16 the sole `protection_claim_decision` in
task 1), so no tie exists and no figure in revision 1 or revision 2 depends on the order the rows were serialised
in. Revision 1 stands on that point.

### revision_2 / override_declarations — re-derived

Declaration counts per policy are now **2 / 3 / 0 / 2 / 2 / 0**, which matches what the reworker reports. Each of
the seven, checked against the clause actually in force:

| # | policy | superseded base clause | verdict |
| --- | --- | --- | --- |
| 1 | out_of_hours_surcharge | `service_appointment_scheduling`: "Work outside the service's ordinary hours or at a weekend carries the service's surcharge on the labour" | **correctly paired** — this is the clause that fixes the surcharge base, and the replacement is the write-off subtraction. Closes revision 1 F-1's first half |
| 2 | out_of_hours_surcharge | `service_labour_pricing`: "Chargeable labour is the hours actually worked, rounded up as the service's rounding basis states and raised to the service's minimum hours, times the service's hourly rate" | pairing correct in substance (the rate-restatement tier) but the superseded clause is **wider than the deviation** — see O-24 |
| 3 | membership_service_relief | `service_combo_plan_membership_interaction`: "the membership tier's repair labour discount is taken off the chargeable labour before any surcharge is added" | unchanged from revision 1, still correctly paired |
| 4 | membership_service_relief | `service_combo_plan_membership_interaction`: "and the membership's service benefit credit may then be spent against what is left" | **correctly paired** — exactly the clause revision 1 F-2 deviated from |
| 5 | membership_service_relief | `service_charge_waivers`: "A write-off never exceeds the charge outstanding on the line it is granted against" | **correctly paired** — closes revision 1 O-10 (cap moved from the line to the job) |
| 6 | declined_claim_labour_rebill | `service_excl_warranty_or_chargeable`: "A customer cannot be billed for labour on a line whose charge has been written off as plan covered" | unchanged from revision 1, still correctly paired |
| 7 | declined_claim_labour_rebill | `service_labour_pricing`: "raised to the service's minimum hours" | **correctly paired and narrowly scoped** to the fragment — closes revision 1 F-3/O-9 |
| 8 | business_contract_relief | `service_charge_waivers`: the same line cap | correctly paired |
| 9 | business_contract_relief | `service_agg_visit_pool`: "Included visits are pooled across the profile rather than counted job by job" | **correctly paired, and this is the deviation revision 1 missed** — see the sweep verdict below |

**The reworker's specific gate argument holds, and I verified it clause by clause rather than accepting it.** The
structured eligibility conditions of the base policies touched are:
`service_labour_pricing.billable_job_state` = "Labour is billed, and payments applied, only while the agreement
stands dispatched, parts_hold or completed"; `service_attendance_and_cancellation.feeable_job_state` = "A no-show
fee, cancellation fee, reschedule fee or trip charge is billed only while the agreement stands scheduled,
dispatched, no_show or cancelled"; `service_excl_warranty_or_chargeable.single_billing_basis_per_line` = "One line
of work is either warranty or plan work or chargeable work, never both, and the flag on the agreement decides which
before any charge is booked"; `service_appointment_scheduling.customer_confirmed_slot` and `.lead_time_respected`;
and `service_charge_waivers`, `service_combo_plan_membership_interaction`, `service_agg_visit_pool` carry
`eligibility: []`. **No superseded clause is the text of any of those conditions** — in particular the clause
superseded from `service_excl_warranty_or_chargeable` is a different sentence from
`single_billing_basis_per_line`'s condition, and the clause superseded from `service_labour_pricing` is a different
sentence from `billable_job_state`'s. Every gate stays in force. **Confirmed.**

**Provisions retired by nobody:** one, and it costs nothing. Declaration 2 supersedes the whole of base's
chargeable-labour sentence inside `service_ext_out_of_hours_surcharge`, which also retires the rounding basis and
the minimum-hours floor there, while the replacement restates only the rate. Recorded as **O-24**; no figure moves
(see `0.md` §revision_2).

**Verdict on the reported undeclared-deviation sweep: it holds where I spot-checked it, and its self-found fourth
deviation is real.** Base `service_agg_visit_pool` says "Included visits are pooled across the profile rather than
counted job by job: the visits used in the term ... are set against the visits included by **every agreement the
profile holds**", while `service_ext_business_contract_relief`'s `grants_term` / `uses_term` are
`SUM('service_events', ...)`, which the DSL scopes to the single target holding (`eq[holding_pk] = HID`), so the
pool is read from one job. That is a genuine deviation, it changes the quantity that ultimately gets scored, and
**revision 1 did not find it** — I record that as a miss of my own, not a credit to be quietly absorbed. It is now
declared at clause granularity. I also independently re-checked the two zero counts: policy 3 and policy 6 read
existing rows and settle an amount, base fixes only how a payment is *applied* ("a payment is applied to the oldest
unsettled charge first") and when a profile settles ("a business account settles within the service's payment
terms, and a consumer account settles on the day"), both of which the two policies restate or inherit without
conflict, and base `service_parts_handling`'s "that deposit is set against the final bill rather than refunded
separately" is implemented rather than deviated from. `overwrite: []` is right for both.

### revision_2 / rule_compute_equivalence — re-derived

Revision 1's three observations: **O-1 closed** — `rate_pct` now reads
`(attendance_dow > 0 and attendance_dow < 6 and F('scheduled_window') == 'evening')`, so a Saturday evening no
longer takes the after-hours percent, and rule and compute agree. **O-2 closed** — `reliefs_recognised` now reads
`goodwill_waivers if (goodwill_waivers > 0 and goodwill_waivers == waivers_total)` and `relief_recognised` reads
`plan_waivers if (plan_waivers > 0 and plan_waivers == waivers_all)`, both implementing "where those are the **only**
write-offs standing on the job". **O-3 closed** — both previously unstated bases are now stated verbatim in their
rules: "The attendances of the refused line are counted from the labour entries standing on the job other than those
booked for the day the job was completed" and "The attendances rebilled are counted from the labour entries standing
on the job other than those booked for the day it was completed and those booked on the day the relief is granted".
**O-17 closed** — "the oldest of the charges it covers is cleared first" and "taken off in the order they came in"
are gone from policies 3 and 6, so no rule now promises an ordering the scored quantity cannot carry.

New in revision 2:

- **O-26.** Three policies say the plan "**refused the claim**" and implement it as exactly
  `last_decision == 'denied_not_covered' or last_decision == 'denied_outside_term'`
  (`rebilled_share_after_decision`, `plan_met_of_same_work`, `plan_met_on_invoice`), while
  `db_schema.json.protection_events.claim_decision` carries eight values including `denied_no_proof_of_purchase`
  and `denied_pre_existing`, which are refusals the compute routes to the fall-through instead. Not realised on
  task 1's world (`denied_not_covered`). Present in revision 1 in the same form and not caught then.
- **O-29.** `minimum_hours_application` tier 1 says "the service's minimum hours are applied to the day the crew was
  dispatched and to **each later attendance** of the line that carries hours, and the raised figures are added",
  while the compute raises the later attendances as one lump:
  `MX(hours_dispatch_day, P('minimum_labour_hours')) + (MX(hours_second, P('minimum_labour_hours')) if hours_second > 0 else 0)`
  with `hours_second = MX(hours_selected - hours_dispatch_day, 0)`. Agrees on task 1 (one later attendance);
  diverges on a line with two.

### revision_2 / factor_ladders — re-derived

32 factors still, 4 / 6 / 4 / 6 / 6 / 6, `parameter` counts 2 / 5 / 3 / 4 / 5 / 5 and `method` counts
2 / 1 / 1 / 2 / 1 / 1 — every policy inside the 4–6 bound with at least 2 `parameter` and 1 `method`. One factor was
replaced (`credit_spent_offset` → `credit_year_allowance`, deciding the new binding `year_allowance`) and two were
relabelled (`settlement_charge_scope` and `invoice_labour_scope`, `method` → `parameter`), which **closes O-16**:
row-selection factors are now uniformly `parameter` and the surviving `method` factors are the anchor, window,
restatement, hours-selection, minimum-hours and share-formula ones, each honest on its own terms. Multi-source and
cross-difficulty floors still met on both tasks (task 0: four multi-source factors and four membership
cross-difficulty; task 1: five multi-source and three protection). **O-23 closed** — the corrected
`design_rationale` sentence now names factors whose upper tiers really are compound over distinct records.

**Baseline rewrite: mostly genuine, with one contradiction left standing and two new defects introduced.**
Each `baseline.rule` is now written as plain standard-method sentences with the variations split out behind them,
and I checked every one of the 32 declared `baseline` values against the sentence of its own `baseline.rule`:

- **F-4 closed** for `relief_labour_figure` ("The labour the relief is worked out on is the labour standing on the
  job less the payments already received against it" → `MX(labour_total - payments_total, 0)`),
  `settlement_charge_scope` ("The charges the settlement covers are every charge standing on the job less the
  payments already received against it" → the same shape) and `rebilled_hours_selection` ("The hours rebilled are
  the hours recorded for the day the crew was dispatched" → `hours_dispatch_day`). In each case the ladder is now
  *outside* `baseline.rule` and the declared baseline is exactly the sentence inside it.
- **F-4 NOT closed for `standing_writeoff_offset`** — see **F-15** below.
- **F-5 closed** — `minimum_hours_application`'s baseline is now `MX(hours_selected, P('minimum_labour_hours'))`,
  which is exactly `baseline.rule`'s new sentence "The service's minimum hours are applied once to the hours taken"
  and exactly base `service_labour_pricing`'s `max(minimum_labour_hours, labour_hours)`.
- **F-6 closed** — every component a `baseline.rule` subtracts or adds now has its own default sentence
  ("No relief is recognised against those charges", "No money is treated as already held against those charges",
  "Nothing older is due with the settlement", "Nothing of the charge for bringing the crew out is added", and so
  on), so each of the six baselines yields one definite number rather than the several readings revision 1 found.
- **F-7 closed** — `next_invoice_deferral` is retiered off the universal conjunct onto the job's age against the
  payment terms: `job_age_days = DAYS(F('requested_date'), NOW)` against `P('payment_terms_days')`, with the
  fall-through now "no charge was booked on the day of settlement". Both upper tiers genuinely divide business
  customers and the fall-through is reachable by one (a business settling a job with no same-day charge) and
  returns a number.
- **F-8/O-11 closed** — `rebill_rate` tier 2 now carries `and surcharge_rows_on_job == 0`, and the rule says "where
  such a surcharge does stand booked on the job the rate is not raised, so the same hour never carries the
  surcharge twice", so the charter no longer charges one surcharge two ways.
- **O-12 and O-13 closed** — `plan_met_of_same_work` tier 2 is now "what the plan has already paid out on the item"
  rather than the per-claim limit, and both that factor's and `plan_met_on_invoice`'s fall-throughs are now "what
  has been written off to the plan's cover on the job" (`plan_writeoffs` / `plan_writeoffs_job`) rather than the
  plan's unused coverage. `rebilled_share_after_decision` likewise replaced `coverage_remaining` with
  `payouts_item` and a `MN(..., claim_limit)` cap. Every one of those is now a quantity the plan has actually met.
- **O-14 closed** — `labour_share_relieved`'s fall-through is `pool_left / MX(P('included_visits_per_term'), 1)`
  with the rule's "counted as at least one visit"; no division by zero.
- **O-15 partly closed** — the priority-queue conjunct is gone from `distance_charge_relief` (its tier 1 is now "a
  charge for the distance travelled stands on the job for the day the crew was dispatched"), and remains in
  `creditable_included_visits` tier 1, where revision 1 already rated it an observation rather than a red light.

**Verdict on the reported ladder/rate sweep: it does NOT hold at the two places I spot-checked.** The sweep claims
"no quantity given a figure by two sentences" and "every fall-through reachable by a customer its policy admits".
F-15 is a counterexample to the first and F-17 to the second, and both are demonstrable from the artifacts alone.
A third claim — "no two tiers share an outcome" — I did check and did not falsify.

### revision_2 / new charter-global findings

**F-15 — SOURCE-FACTOR RED (revision 1 F-4 not closed for `standing_writeoff_offset`, and now a flat
contradiction).**
- Symptom: `service_ext_declined_claim_labour_rebill.baseline.rule` gives one quantity, the write-off offset, two
  different figures, and one of the two is the scored value.
- Root cause: the rewrite added a default sentence for the offset without removing the overwrite clause that
  already fixes it in the opposite direction. Revision 1's `baseline.rule` carried only the first of the two
  sentences; the second is new, so the defect has changed shape from "the baseline is not what `baseline.rule`
  says" to "`baseline.rule` says two things".
- Evidence, both sentences verbatim from `extended_policies[3].baseline.rule`:
  (a) "Where a plan's decision refuses a claim after the work was carried out as plan work, the labour of that line
  is rebilled to the customer as chargeable work, and **the write-off the plan's cover carried is not set against
  the rebilled figure**."
  (b) "**From the figure rebilled come the write-offs that already stand on the job.**"
  The factor declares `baseline: writeoff_offset: "all_writeoffs"`, and its fall-through tier is "the write-offs
  standing on the job".
- Demonstrated consequence on task 1's world: the job carries exactly one write-off,
  `waiver_reason = "protection_plan_covered"`, `waiver_amount = 1051.25`, and the claim was refused. Sentence (a)
  gives `writeoff_offset = 0.00`, which is the **scored** value (tier 1). Sentence (b) gives 1051.25, which is the
  declared baseline. A reader of the computation document alone reaches either the gold figure or the baseline
  figure depending on which of the two sentences is read last, and if they read (a) — the sentence the policy
  itself leads with — the factor's own document changes nothing, which is exactly the decorative-factor test.
- Affected artifact and location: `service.extended.yaml` `extended_policies[3].baseline.rule` (the two sentences)
  against `extended_policies[3].factors[4].baseline`; bears on **task 1**.
- Relation to previous revisions: revision 1 F-4, fourth instance, not closed; the contradiction is new.

**F-17 — SOURCE-FACTOR RED, and a regression introduced by the baseline rewrite.**
- Symptom: `service_credit_available`'s declared baseline names a tier on which
  `service_ext_membership_service_relief` returns no result at all.
- Root cause: the ladder was reordered so that the fall-through is "no Circle membership stands active", and the
  baseline moved with it from `tier_credit` (revision 1) to `0` (revision 2). On the worlds that fall-through
  selects, the policy's own `compute` raises.
- Evidence: the new ladder is tier 1 "a Circle membership stands active on the profile and its unspent benefit
  credit is at least the service visit credit its tier grants", tier 2 "... is below ...", tier 3 "otherwise" — so
  the fall-through is exactly `not membership_active`. On such a world
  `max_redemptions = CPARAM('membership','max_benefit_redemptions_per_year', status='active')` returns `None`
  (`check_compute.py` `CPARAM`: `if not hs: return None`), and `year_allowance` evaluates
  `redemptions_window >= max_redemptions` **before** the `and membership_active` short-circuit. I ran the exact
  expression: `TypeError: '>=' not supported between instances of 'int' and 'NoneType'`.
- Demonstrated consequence: the tier the baseline sits on is reachable in principle and returns a figure on no
  world whatever, so "substituting the baseline" names a standard method the policy cannot execute. Revision 1's
  baseline, `tier_credit`, sat on a tier ("otherwise" = an active membership whose balance is at or above the tier
  credit) that returns a number, and revision 1's whole-baseline for this computation was a bookable **50.00**;
  revision 2's is **0.00**, and `writeoff_service_charge_816a24da`'s contract requires `waiver_amount` "always
  positive", so the computation document now tells a reader to write off an amount the tool forbids.
  Independently: across the six Circle tiers the only one with `repair_labour_discount_pct == 0` is Circle Free
  Membership, whose `service_benefit_credit_usd` is `0.0`, so `relief_rate = 0` forces `credit_applied = 0` too —
  the fall-through of `labour_relief_share` returns 0.00 on every world of this scenario as well.
- Affected artifact and location: `service.extended.yaml` `extended_policies[1].factors[3]` (ladder order and
  `baseline`), `extended_policies[1].compute.year_allowance`; `tasks/0.json computations[1].baseline_result` (0.0)
  and `factor_sensitivity[3]` (75.48). Bears on **task 0**.
- Relation to previous revisions: **regression** against revision 1, which passed this factor.

**F-18 — SOURCE-FACTOR RED. `credit_year_allowance`'s fall-through restores an allowance the year has spent.**
- Symptom: the tier the baseline sits on hands a member the whole annual service credit precisely when the
  member's window spend has already reached or passed it.
- Root cause: the third branch of `year_allowance` returns `tier_credit` instead of nothing.
- Evidence: `compute.year_allowance = "0 if (redemptions_window >= max_redemptions and membership_active) else
  (MX(tier_credit - credit_spent_window, 0) if (redemptions_window < max_redemptions and credit_spent_window <
  tier_credit) else tier_credit)"`, and the matching rule sentence "The credit the membership year still allows for
  service work is the service visit credit the tier grants." The fall-through therefore fires exactly when
  `redemptions_window < max_redemptions` **and** `credit_spent_window >= tier_credit`.
- Demonstrated consequence: reachable and returning on an ordinary world — Circle Total Annual allows 12
  redemptions a year against a 50.00 service visit credit, so two redemptions of 30.00 give
  `redemptions_window = 2 < 12` and `credit_spent_window = 60.00 >= 50.00`, and the year is then declared to allow
  **50.00** where the policy's own governing sentence ("The credit set against what is left is the lower of the
  credit available on the membership and the credit the membership year still allows for service work, so no
  redemption already netted out of the membership's own balance is deducted from that balance a second time")
  entails nothing remains. No retailer publishes an annual credit that refills once it has been overspent, and the
  effect is to let the relief exceed the year's allowance — the substance revision 1's F-2 was fixed to prevent,
  re-entering through the tier the baseline names.
- Affected artifact and location: `service.extended.yaml` `extended_policies[1].compute.year_allowance`, its rule
  sentence, and `extended_policies[1].factors[5]`; `tasks/0.json computations[1].factor_sensitivity[5]` (113.48).
  Bears on **task 0**.
- Relation to previous revisions: new. Revision 1's `credit_spent_offset` had a different shape (the double
  deduction, F-2) and this is not that defect returning; it is a new one in the replacement factor.

**O-24 — observation. Declaration 2 is wider than the deviation it declares.**
`service_ext_out_of_hours_surcharge` supersedes the whole of base's "Chargeable labour is the hours actually
worked, **rounded up as the service's rounding basis states and raised to the service's minimum hours**, times the
service's hourly rate" and replaces it with a sentence about restating a wrongly rated line. Inside that policy the
rounding basis and the minimum-hours floor are therefore retired with nothing restating them, and the policy's own
restatement tier (`hours_recorded * P('base_labour_rate_usd_per_hour')`) in fact *implements* base's formula rather
than deviating from it. No figure moves on task 0's world (`minimum_labour_hours = 1.0` against 2.25 recorded hours,
and the restatement tier is not the tier taken). Compare declaration 7, which names only the fragment
"raised to the service's minimum hours" and is the right granularity.

**O-25 — observation. `rebilled_share_after_decision`'s fall-through raises on its no-plan sub-case.**
`claim_limit = CPARAM('protection','per_claim_limit_usd', status='active')` returns `None` when no plan stands
active, and the fall-through then evaluates `MN(MX(gross - payouts_item, 0), None)`; I ran it:
`TypeError: '<' not supported between instances of 'NoneType' and 'float'`. The tier as a whole is still reachable
on a returning world — an active plan whose latest decision is one of the five `claim_decision` values the two
upper tiers do not name — so this is a robustness hole rather than an unreachable tier, and it is not F-17's shape.
The sibling bindings in policies 5 and 6 are safe: their fall-throughs are `plan_writeoffs` / `plan_writeoffs_job`,
which are `SUM(...)` over the job's own rows and return `0.0`, and `plan_active` short-circuits the tiers above.

**O-30 — observation, and the correction to the O-8 disposition (see the base-layer ruling below).** The two
waiver-writing tools still produce rows that differ only in `channel`
(`writeoff_service_charge_816a24da` writes `channel="phone"`, `credit_contract_relief_ce7af535`
`channel="business_desk"`), as do the two payment tools, and **no compute binding in this charter reads `channel`** —
I checked all six policies' `compute` blocks and the base `formula`s. `erlbench/loader.py` loads every difficulty's
`task_tools.py` into one spec list and `engine.py`'s `unlock_agent_discoverable_tool` / `unlock_user_discoverable_tool`
resolve a name against that whole list with no per-task scoping, so a task's three tools are not the only ones
unlockable in it. The substitution is nonetheless excluded at the policy layer in both tasks (see the ruling).

**O-31 — observation. Two policies of this charter treat an in-allowance slot-move fee oppositely.**
`service_ext_visit_settlement_payment.older_charges_due` tier 1 adds a reschedule fee "in full" to what a consumer
settles whenever no retailer-error write-off stands against it, while
`service_ext_business_contract_relief.slot_move_fee_relief` tier 1 relieves a business of one "in full" where "the
slot was moved no more often than the service's allowance permits". Base
`service_appointment_scheduling` makes **notice**, not the move count, the test of whether the fee was owed at all
("A slot may be moved as often as the service's allowance permits with the service's notice hours given; beyond
that allowance, or with less notice, the service's reschedule fee is billed"). Neither task's seed states the
notice given, so neither treatment is contradicted on these worlds and no figure is at risk.

### revision_2 / the four items assigned to base — my ruling

The coordinator asked me to confirm or contradict the disposition that O-4, O-5, O-6 and O-8 move no figure, GT or
uniqueness. **On the two worlds this difficulty presents, none of the four moves a scored figure, changes GT, or
creates a second defensible solution.** The disposition holds. Three specifics and one correction:

- **O-4** (base states a `labour_rounding_basis` nothing implements). Does not move a figure. Every labour quantity
  either world presents is already an exact multiple of its service's rounding unit: task 0 records 1.5 h and
  2.25 h against "up to the next quarter hour"; task 1 records 6.0 h, 1.25 h and 2.5 h and bills 8.0 h against the
  same unit. Applying the rounding basis is a no-op at every point either task evaluates. Additionally, declarations
  2 and 7 now supersede the sentence (or its fragment) inside the two policies that compute hours, so within them
  the unimplemented clause is explicitly out of force.
- **O-5** (`db_schema.json` gives `charge_kind` a single surcharge value, so task 0's *weekend* surcharge is filed
  as `after_hours_surcharge`). Does not move a figure, and is in fact relied upon: policy 2's `surcharge_rows` /
  `surcharge_last_sent` / `surcharge_hold_day` and policy 4's new `surcharge_rows_on_job` all filter exactly that
  value, so the single value makes those reads unambiguous rather than ambiguous. Caveat for the record: the enum
  could not distinguish a weekend from an after-hours surcharge on one job, and policy 4's
  `surcharge_rows_on_job == 0` guard would be tripped by either — no task here needs that distinction.
- **O-6** (`feeable_job_state` enumerates four fee kinds and not the surcharge, though `service_fee_charge` carries
  "a surcharge"). Does not move a figure or change GT, on either reading. Task 0's job stands `dispatched`, which
  is in the gate's `allowed` list, so the surcharge write is legal whether or not the surcharge counts as one of
  the four enumerated fees; and if the narrow enumeration were read as putting the surcharge outside the gate
  entirely, the write would simply be ungated and still legal here. Task 1 books no `service_fee_charge`, so its
  `completed` status — which is *not* in that gate's allowed list — is never tested.
- **O-8** (both waiver tools accept the whole ground enum, so either could bring about a state a prerequisite
  sentence waits on). **Does not move a figure and does not change GT**, because `channel` is the only field that
  differs and no compute reads it (O-30), and because the hop is resolvable at the policy layer in both tasks: only
  `service_ext_membership_service_relief`'s rule describes a write-off "granted on the membership ground" and only
  `service_ext_business_contract_relief`'s describes relief "on a term of the customer's business contract", and
  the latter's tool contract asks for "the reference number of the **business** profile being relieved" against
  task 0's `account_type: "consumer"`. For the payment pair, policy 3's rule now ends "a **consumer** profile
  settles it on the day it is worked out" and policy 6's "a **business** profile settles it within the service's
  payment terms", so task 1's business profile selects policy 6 and its tool, and the two policies compute
  different amounts in any case. So: no second defensible solution.
  **But I contradict one part of the reworker's account.** It reports O-8 as a property of the frozen blueprint and
  "not routable inside its write domain". Only the `waiver_reason` enum is base
  (`db_schema.json.service_events.waiver_reason`); **which grounds each tool accepts is declared in
  `task_tools.py`, which is inside this difficulty's own write domain**, so narrowing
  `credit_contract_relief_ce7af535` to the contract/plan grounds and `writeoff_service_charge_816a24da` to the rest
  would be routable here. Since it moves no figure it need not be routed; the claim that it *could* not be is
  false, and the record should say so rather than carry it as an unavoidable base cost.

### revision_2 / policy_conflict_scan, prerequisite_graph, prerequisite_sentences — re-derived

- The six policies still map one-to-one onto six tools and six distinct `(target_tool, computes)` pairs; the two
  subject overlaps are still separated by tool and by business ground. The one substantive inter-policy conflict
  revision 1 found (F-8, the surcharge charged two ways) is closed.
- `prerequisite` graph unchanged in shape: four edges, all `value_input`, two disjoint chains of three, acyclic,
  each `gate` a real binding (`surcharge_scope`, `reliefs_recognised`, `labour_rebilled_today`,
  `relief_recognised`), each `resolved_by` the depended-on policy's own `target_tool`, `form: state` on all four
  with no `fallback_reason`, and no authoring-viewpoint phrasing.
- **O-7 closed.** The edge `business_contract_relief -> declined_claim_labour_rebill` now carries a
  `policy_source` that matches its `condition` in scope: "The relief is fixed only once the chargeable labour the
  plan's refusal sends back to the customer stands billed on the job **on the day the relief is granted**."
- All four prerequisite sentences still pass the four-point test, and each still names a state exactly one *policy*
  of this difficulty brings about; the tool-layer residue is O-30/O-8 above, ruled not to move a figure.
- Task scopes still the two chain components, pairwise disjoint and jointly covering all six policies, and the
  revealed `charter_scope` of both tasks agrees with the components I derive from the graph.

### revision_2 / closing checklist

**The difficulty still does not close out**, on four findings rather than nine.

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | **PASS** (F-1 and F-2 closed) | **SOURCE-CHAIN RED** (F-16) | **SOURCE-FACTOR RED** (F-17 regression, F-18) | **PASS** |
| 1 | **PASS** | **PASS** (F-12, F-13, F-14 closed) | **SOURCE-FACTOR RED** (F-15) | **PASS** (F-9 closed) |

- Per-task audit files still correspond one-to-one with the tasks, revision 1 is preserved verbatim above and in
  both task files, and each task file carries a `revision_2` comparison.
- All six extended policies covered, the two scopes pairwise disjoint, task tools and GT closed, uuid8s unchanged
  and still independently generated (`task_tools.py` content-identical, carried forward).
- Both problem trees still have two prerequisite problems, two `value_input` edges, one `owner=user` write at the
  root and no cycle; the difficulty's four edges are still a DAG. **F-14 is closed substantively** — task 1's
  rebill edge now moves the root's own scored figure, 1145.00 against 173.50.
- Every one of the 32 factors still bears weight against its declared baseline, and all six whole-baseline figures
  are definite and differ from gold; I recomputed all 38 figures independently and they agree with the artifacts to
  the cent. What fails is the honesty of three baselines, not the weight of any factor.
- Standing observation carried from revision 1: four of the six whole-baselines are now **0.00** (task 0's relief,
  and all three of task 1's), so the "definite wrong number" a computation document alone yields is a trivial zero
  in four of six cases. Revision 1 recorded this for task 1's three; the F-17 rewrite added task 0's.
- Instantiation gates: not run by me. The coordinator's re-run is cited; `check_traceability` is still correctly
  deferred to the render step.

---

## revision_3

Third-round re-audit. Revisions 1 and 2 above are untouched.

### revision_3 / grounds for re-deriving

Hashes recomputed by me from disk:

| artifact | sha256_16 now | relation to the revision-2 section |
| --- | --- | --- |
| `service.extended.yaml` | `1de1377416bc1921` | **changed** — charter-global sections re-derived below |
| `task_tools.py` | `4447a9f91273e801` | **unchanged by content** — the same value I computed in rounds 1 and 2, so §`action_binding_and_uuids` is carried forward by reference: six distinct `(target_tool, computes)` pairs, six independently generated uuid8s, no docstring naming another tool or a sequence position, no tool body judging a prerequisite |
| `tasks/0.json` | `2cf604f75d52874f` | changed (world and figures both) |
| `tasks/1.json` | `f94014cf31c4f797` | changed (one seed field and the persona; figures unchanged) |
| `blueprint/products/service.yaml` | `e673ca021b79484f` | base copy re-verified: 1769 lines, byte-identical to the extended file's prefix, zero diffs |
| `blueprint/products/protection.yaml` | `e93deb59bd7503ab` | identical to the value I computed in revision 2 — plan tier figures unmoved |
| `blueprint/products/membership.yaml` | `c6245922d2ecd6ff` | identical to revision 2 — Circle tier figures unmoved |
| `blueprint/db_schema.json` | `f001a91f53fe0923` | recorded for the enum checks below |

So the blueprint is again untouched, and every correction this round was made inside the difficulty's own write domain.

### revision_3 / per-item verdicts

| item | verdict | how I established it |
| --- | --- | --- |
| **F-15** | **closed** | The disputed clause is gone from `extended_policies[3].baseline.rule`, whose first sentence now ends "…is rebilled to the customer as chargeable work." It survives only in the policy's `rule` ladder ("Where a write-off granted on the plan's cover stands on the job, nothing comes off") and in the narrowed override (`replaced_by`: "The write-off the plan's cover carried is not set against the rebilled figure."). `baseline.rule` now contains exactly one sentence about that quantity — "From the figure rebilled come the write-offs that already stand on the job" — which is the declared baseline `all_writeoffs`. One quantity, one figure. |
| **F-16** | **closed, verified by recomputation** | See `0.md` §revision_3; I recomputed every figure in the closure rather than reading it. |
| **F-17** | **closed in both limbs** | Limb 1: `service_credit_available`'s fall-through is again "the service visit credit the tier grants" (`baseline: tier_credit`), a tier an active member with a balance at or above the tier credit sits on, and task 0's relief baseline is now a positive, bookable **31.00** (I derived 31.00 independently). Limb 2: every membership read is guarded (`CPARAM`/`CFIELD`/`MONTHS` each `if membership_active else 0`), the `max_redemptions` binding that caused the raise is removed outright, and I **ran** the no-membership bindings: `window_months = 1`, `credit_applied = 0`, result returns. The guard is stated in the rule, not only in compute: "Where no Circle membership stands active on the profile, the tier figures a membership would have supplied … are all taken as nothing, and the windows below are counted as one month." |
| **F-18** | **closed** | `credit_year_allowance` is gone as a factor; `year_allowance = MX(tier_credit - credit_spent_window, 0)` is a plain formula, so a member whose window spend has reached the tier credit now gets 0 rather than the full credit refilled. The rule states it: "The credit the membership year still allows for service work is the service visit credit the tier grants less the credit already spent inside the window, and never below nothing." The perverse tier is eliminated, not reworded. |
| **O-15** | **closed** | `creditable_included_visits` tier 1 is re-keyed from the priority queue to "visits granted under a plan covering the item stand among them" (`plan_grants > 0`). `priority_flag` now appears **once** in the whole extended file, at line 572 in the `events` field list — no compute, no ladder, no baseline reads it. The claim holds. |
| **O-24** | **closed by withdrawal** — see O-32 | Policy 1's over-wide second declaration is gone; counts are now 1/3/0/2/2/0, matching the report. My ruling on whether the withdrawal reopens anything is O-32 below. |
| **O-25** | **closed** | `claim_limit = CPARAM(...) if plan_active else 0`, and I ran the no-plan fall-through: `rebilled_base = 0`, `diag_credit = 0`, result **0.00**, no raise. Stated in the rule: "Where no plan stands active on the item there is no per-claim limit and no refused claim, so nothing is rebilled under this rule at all." |
| **O-26** | **closed** | All three plan-decision ladders now enumerate the four denial values the schema carries (`denied_not_covered`, `denied_outside_term`, `denied_no_proof_of_purchase`, `denied_pre_existing`), matching "refused the claim". |
| **O-27** | **closed** | Task 1's `service_visit_consume` row now carries `visit_grant_reason "plan_included"`, matching the grant. |
| **O-28** | **closed** | Task 0's persona line is now "she has no idea what is left on it" in place of "she has never spent it", so no persona sentence contradicts the seeded ledger. |
| **O-29** | **closed** | The override's `replaced_by` and the ladder tier both now read "to the hours of the line's later attendances **taken together**, and the two raised figures are added", matching `MX(hours_second, P('minimum_labour_hours'))` applied once to the lump. |
| **O-31** | **closed** | `slot_move_fee_relief` is re-keyed onto the retailer-error write-off, which is the same test `service_ext_visit_settlement_payment.older_charges_due` uses, so the two policies no longer treat one situation oppositely. |
| **O-30** | no action, per my own revision-2 ruling | See the O-8 note below. |
| **O-4 / O-5 / O-6 / O-8** | ruling stands | Nothing this round changes it. The reworker's replacement reason for leaving O-8 unrouted is **correct** — see below. |

### revision_3 / the O-8 reason, judged

The reworker now says O-8 cannot be routed because `check_task_tools` requires an enum argument's description to cover
the schema's closed set value by value. **That is right, and I checked the gate's source rather than the claim.**
`skills/erl-task-instantiate/scripts/check_task_tools.py` takes the closed set from the mapped schema field
(`enum_values(schemas)`) and `validate_enum` fails with "enum value {v!r} is missing from the description" for any
schema value absent from the docstring, then additionally requires per-value applicable-situation text. So a docstring
narrowing `waiver_reason` / `relief_ground` to a subset of `db_schema.json.service_events.waiver_reason` would fail the
tool-contract gate on every omitted value. One nuance for the record: the gate constrains the *description*, not the
body, so a tool could describe all seven grounds and reject some at runtime — but that would put a business judgement
into the tool layer, which is itself a `SOURCE-CHAIN` defect shape ("the tool layer judging the prerequisite"), so the
item is genuinely unrouted. The disposition is sound and the reason is checkable and true.

### revision_3 / the 96-tier scorable-world test, spot-checked

The count is arithmetically exact: 32 factors × 3 tiers = **96**, which I recomputed from the factor inventory
(4 / 6 / 4 / 6 / 6 / 6 factors, 12 / 18 / 12 / 18 / 18 / 18 tiers). I spot-checked seven tiers, chosen as the ones
revision 2 broke or rated riskiest, and the test **holds at every one**:

| tier | what I did | result |
| --- | --- | --- |
| `service_credit_available` tier 1 ("no Circle membership stands active") | evaluated policy 2's whole binding chain with `membership_active = False` | returns: `window_months 1`, `credit_applied 0`, result returns — the revision-2 `TypeError` is gone |
| same tier, on a **scorable** world | added a rework job with no membership (`rework_rows 1`, `work_type "rework"`) | `relief_rate 100`, result **301.91** — nonzero and bookable, so the tier is reachable on a world that scores, not merely on one that returns |
| `service_credit_available` fall-through | active member with a balance at or above the tier credit | returns `tier_credit`; this is the tier the baseline names |
| `labour_relief_share` fall-through | no discount tier, no rework | returns 0 |
| `rebilled_share_after_decision` fall-through, no-plan sub-case | evaluated with `plan_active = False` | returns **0.00**, matching the reworker's report exactly; the guard is what makes it total |
| `next_invoice_deferral` tier 1 | took task 1's world and mutated only the job age past the 30-day terms | `terms_deferral = 1275.00` → result `MX(−130.00, 0) = **0.00**`, which **reproduces the reported figure exactly** |
| `next_invoice_deferral` tier 3 | took task 1's world and moved the rebill off the day of settlement so `charges_today = 0` | `terms_deferral = 334.00` → result **811.00**; returns and scores |

Two caveats stated honestly. The reworker's tier-3 figure is 382.50 and mine is 811.00: the harness's mutation worlds
are not published, so the two are different worlds and I can confirm only the property (the tier selects and the
compute returns a definite, scorable figure), not their number. And a handful of tiers are reachable only on variants
other than the two these tasks use — `surcharge_percent_read`'s after-hours tier and `rebill_hourly_rate`'s
evening tier both need `scheduled_window == "evening"`, which TechWorks Standard Home Installation
(`appointment_windows_offered: "morning or afternoon"`) and TechWorks Business On Site Deployment
(`"business hours"`) never offer; they are reachable on Home Theatre Calibration and Managed IT Care Annual, which the
policies also admit, so the tiers pass the test policy-wide. That is a legitimate reading of "a customer its policy
admits" and not a finding.

**Verdict: unlike the revision-2 ladder sweep, which I falsified at two of the places I checked, this test holds
everywhere I checked it, and at one tier it reproduces the reported figure to the cent from a world I built myself.**

### revision_3 / override_declarations, re-derived

Counts 1 / 3 / 0 / 2 / 2 / 0. The six surviving declarations are the ones I rated correctly paired in revision 2
(policy 1's surcharge-base clause; policy 2's discount-before-surcharge, benefit-credit and line-cap clauses; policy 4's
plan-covered-billing and minimum-hours-fragment clauses; policy 5's line-cap and visit-pool clauses), with two textual
narrowings: policy 4's first `replaced_by` is now just "The write-off the plan's cover carried is not set against the
rebilled figure." (the F-15 fix) and its second now says "taken together" (O-29). I re-checked that no superseded clause
is the text of any base eligibility condition — `billable_job_state`, `feeable_job_state`,
`single_billing_basis_per_line`, `customer_confirmed_slot`, `lead_time_respected` are all untouched, and
`service_charge_waivers`, `service_combo_plan_membership_interaction` and `service_agg_visit_pool` carry
`eligibility: []`. Every gate stays in force.

**One new undeclared deviation, and it is this round's regression: F-19 below.** Policy 2's new sixth factor applies
base `service_charge_waivers`' bar on double relief to two write-offs base's own preceding sentence says are not the
same charge, and nothing in `overwrite` names it.

### revision_3 / rule_compute_equivalence and factor_ladders, re-derived

Floors all met: 4 / 6 / 4 / 6 / 6 / 6 factors, `parameter` 2 / 5 / 3 / 4 / 5 / 5, `method` 2 / 1 / 1 / 2 / 1 / 1, every
ladder three pairwise-disjoint-as-stated tiers. Cross-difficulty: task 0 now carries three membership factors
(`credit_year_allowance` was one and is gone; the new factor is not cross-category) and task 1 three protection ones —
both floors met. Multi-source: task 0 has `surcharge_labour_figure`, `money_already_held`, `older_charges_due` and
`labour_relief_share`; task 1 has five. Every baseline I checked is now the sentence of its own `baseline.rule`, and
each `baseline.rule` yields one definite figure (task 0: 0.00 / 31.00 / 429.91; task 1: 0.00 / 0.00 / 0.00), so F-4,
F-5, F-6 and F-15 are closed across all six policies.

New this round:

**O-33 — observation. A text splice leaves one tier's condition without its connective.**
`extended_policies[3].rule` reads, verbatim: "…the service's minimum hours are applied to the day the crew was
dispatched and to the hours of the line's later attendances taken together, and the two raised figures are added
**line carries labour for one attendance day and the service requires two people to attend**, the service's minimum
hours are doubled and applied to that attendance." The "; where the" that joined the two tiers in revision 2 has been
lost, so `minimum_hours_application`'s second tier is no longer stated as a condition — it trails off the first tier's
consequent as a fragment. I scanned all 96 tiers for the same fault by matching each ladder condition against its
rule sentence and checking for an introducing connective: **this is the only genuine instance** (the eight other
matches were my matcher failing on legitimate paraphrases such as "Where such a charge stands on the job…"). No figure
moves — task 1 takes tier 1, and both readings of the fragment give the same number on the worlds I could construct —
so this is not a red light, but the published rule is the surface a solver reads and that tier is no longer a
conditional in it.

**O-32 — observation. The withdrawn declaration leaves a narrow undeclared gap, and I judge the withdrawal
acceptable.** Policy 1 still restates a wrongly rated line as "the hours recorded on the latest labour entry
multiplied by the service's hourly rate" while base `service_labour_pricing` defines chargeable labour as
"the hours actually worked, rounded up as the service's rounding basis states and **raised to the service's minimum
hours**, times the service's hourly rate", and that sentence is no longer declared superseded anywhere in policy 1. On
balance the withdrawal is right rather than wrong: the restatement *applies* base's formula rather than departing from
it, so declaring the whole sentence superseded (revision 2) retired the rounding basis and the minimum floor with
nothing replacing them, which was the substance of O-24. The residue is that the restatement drops the minimum-hours
floor, which base would apply. No figure moves on task 0's world (`minimum_labour_hours 1.0` against 2.25 recorded
hours, and the restatement tier is not the tier taken), so there is no demonstrable consequence and no red light; but
the gap is real and should be on the record rather than treated as closed by the withdrawal.

### revision_3 / new charter-global finding

**F-19 — SOURCE-POLICY RED, with a SOURCE-FACTOR limb. The new sixth factor deducts a write-off the policy has
already netted out, and applies base's double-relief bar to charges base says are not the same charge.**

- Symptom: on task 0's world the membership relief is 69.48 where the same policy's other mechanism for preventing
  double relief has already removed the same 40.00, and where base's own reading of the clause the factor invokes
  gives 109.48.
- Root cause: `service_ext_membership_service_relief` now contains **two** mechanisms for one stated purpose and
  applies both. The purpose is stated once — "so that the same charge is not relieved twice on different grounds" —
  and discharged twice.
- Evidence, all verbatim from the artifacts:
  - The cap, which is itself a declared override (`overwrite[2].replaced_by`): "The relief … never exceeds the charges
    standing unsettled on the job, which are every charge booked on it less every payment received **and every amount
    already written off**", implemented as `outstanding_all = MX(charges_total - payments_total - waivers_total, 0)`.
    On task 0's world that is 719.41 − 289.50 − **40.00** = 389.91, so the goodwill write-off is already out.
  - The new factor: "What another ground has already relieved on the job then comes off the relief the membership
    ground may give, so that the same charge is not relieved twice on different grounds. … where write-offs granted as
    a goodwill gesture stand on the job and none granted on a plan's cover does, what goodwill has already relieved
    comes off instead", implemented as
    `ground_offset = ground_plan_waivers if ground_plan_waivers > 0 else (ground_goodwill_waivers if ground_goodwill_waivers > 0 else 0)`
    and `result = MN(MX(RND(discount_owed + credit_applied - ground_offset, 2), 0), outstanding_all)`.
    On task 0's world `ground_offset = 40.00` — the same write-off, subtracted a second time.
  - Base `service_charge_waivers`, the sentence the factor invokes, in full: "**Goodwill is granted for the
    inconvenience the retailer caused rather than for the price of the work**, and the same charge is not written off
    twice on different grounds." The membership relief is a share of the chargeable labour plus the tier's service
    credit — the price of the work. By base's own distinction the goodwill write-off and the membership relief are not
    the same charge, so base's bar does not reach between them. `overwrite` names three base clauses and not this one.
- Demonstrated consequence: two defensible answers in the same situation, from two clauses the KB publishes together.
  Extended: `discount_owed 75.48 + credit_applied 34.00 − ground_offset 40.00` = **69.48**, which is gold, and the
  settlement that follows is 320.43. Base's reading of the same clause takes nothing off between two different charges:
  `75.48 + 34.00` = **109.48**, and the settlement becomes
  `MX(RND(456.91 + 35.00 − (40.00 + 109.48) − 62.00, 2), 0)` = **280.43**. Both figures clear the job, so nothing in
  the world discriminates them; only the undeclared clause does.
- SOURCE-FACTOR limb: the tier taken is an outcome no retailer publishes. The 40.00 was granted as goodwill for the
  wait on the part, and the factor withholds exactly 40.00 of the membership benefit this customer pays annual dues
  for, so the gesture is worth nothing to a member and a non-member in the same position would be no worse off. That
  is the "a tier's value … that no such business would publish as its treatment of customers in that situation"
  shape, and the tier is the one this task's world selects.
- Affected artifact and location: `service.extended.yaml` `extended_policies[1]` — the `rule` sentences quoted above,
  `compute.ground_offset`, `compute.result`, `factors[5] relief_already_given_on_other_grounds`, and `overwrite`
  (which does not name the base clause); `tasks/0.json` `computations[1].expected` (69.48),
  `computations[1].factor_sensitivity[5]` (109.48) and `computations[2].expected` (320.43). Bears on **task 0**.
- Relation to previous revisions: **new, and a regression of a relationship that passed in revision 2.** It arrived in
  the factor introduced to vacate the slot F-18's removal left, which is the risk the coordinator flagged before I
  looked. Note what is *not* wrong with the factor: it bears weight (by 40.00, the largest single mover in its
  computation), its ladder has three distinct outcomes, its baseline is the fall-through and is the sentence of
  `baseline.rule` ("Nothing comes off on that account"), and its fall-through is reachable and returning. The defect is
  what the tier does, not that the factor is decorative.

**O-34 — observation. The same factor's first tier departs from a second base clause, not exercised here.**
Tier 1 nets "what the plan's cover has already relieved" off the membership relief, while base
`service_combo_plan_membership_interaction` says "The plan cover and the membership discount are **never applied to
the same labour line**: covered labour is already free, so a discount on it is meaningless" — base's treatment is that
the discount does not apply to that labour at all, not that the plan's amount is netted off a relief computed on the
full labour. Task 0's job carries no plan write-off, so tier 2 is the tier taken and no consequence is demonstrable.

### revision_3 / closing checklist

**The difficulty does not close out.** Task 1 now passes all four relationships; task 0 fails two on one finding.

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | **SOURCE-POLICY RED** (F-19) | **PASS** (F-16 closed) | **SOURCE-FACTOR RED** (F-19's limb; F-17 and F-18 closed) | **PASS** |
| 1 | **PASS** | **PASS** | **PASS** (F-15 closed, O-25 closed) | **PASS** |

- Three report files, one per task plus this one; revisions 1 and 2 preserved verbatim; every round has a comparison
  section carrying a verdict.
- All six extended policies covered, the two scopes pairwise disjoint and agreeing with the revealed `charter_scope`,
  task tools and GT closed, uuid8s unchanged and carried forward on an unchanged `task_tools.py`.
- Both trees unchanged in shape: two prerequisite problems, two `value_input` edges, one `owner=user` write at the
  root, no cycle, four edges forming a DAG across the difficulty. Every figure in both `prerequisite_closure`
  blocks now agrees with my own recomputation, and both `order_uniqueness` arguments rest on the prerequisite
  sentences while stating plainly that both orders clear the job.
- All 32 factors bear weight against honest baselines; all six `baseline.rule`s yield one definite figure differing
  from gold; the 0.00-baseline concern I carried from revisions 1 and 2 is **partly relieved** — task 0's relief
  baseline is now a bookable 31.00, though task 1's three remain 0.00.
- The constructive 96-tier scorable-world test closes the defect class that cost revision 2, and holds everywhere I
  spot-checked it.
- Instantiation gates: not run by me; the coordinator's re-run is cited. `check_traceability` still correctly
  deferred to the render step.

**What stands between this difficulty and closing out is one finding, F-19, on one factor of one policy.**

---

## revision_4

Fourth-round re-audit. Revisions 1–3 above are untouched.

### revision_4 / grounds for re-deriving

Hashes recomputed by me from disk:

| artifact | sha256_16 now | relation to revision 3 |
| --- | --- | --- |
| `service.extended.yaml` | `d5a08859e53cbd8a` | **changed** — re-derived below |
| `task_tools.py` | `4447a9f91273e801` | **unchanged by content**, the same value I computed in rounds 1–3; §`action_binding_and_uuids` carried forward by reference |
| `tasks/0.json` | `7578390a4a0ce08f` | changed (charter-driven figures and proof fields; world unchanged) |
| `tasks/1.json` | `50fa5a9437459303` | changed (proof fields only; world and figures unchanged) |
| masked view `0.json` | `5e89e581c7227a99` | **byte-identical to the view I held in round 3** |
| masked view `1.json` | `0b41b4ba14a23338` | **byte-identical to the view I held in round 3** |
| `blueprint/products/service.yaml` | `e673ca021b79484f` | base copy re-verified: 1769 lines, zero diffs against the extended file's prefix |
| `blueprint/products/membership.yaml` | `c6245922d2ecd6ff` | identical to the value I computed in rounds 2 and 3 |
| `blueprint/products/protection.yaml` | `e93deb59bd7503ab` | identical to rounds 2 and 3 |

Both seeded worlds are therefore unmoved this round, established by content rather than by any hash I was handed, and
the blueprint is again untouched. Only the charter and the masked proof fields moved.

**What changed in the charter, policy by policy.** Policies 1, 3, 5 and 6 are unchanged: their factor `decides` lists,
every factor baseline and their overwrite counts are identical to what I recorded in revision 3. Policy 4 changed in
one character-level respect only — the restored connective (O-33). All the substance is in policy 2.

### revision_4 / per-item verdicts

| item | verdict | how I established it |
| --- | --- | --- |
| **F-19** | **closed, and closed by changing what the tier does** | Both limbs; the full argument is below because this is the finding that has been reopening. |
| **O-34** | **closed by carrying base** | The tier now states base's own treatment: "Where a write-off granted on a plan's cover stands on the job, **no part of that labour is taken into the share at all**, since labour a plan has covered is already free and a discount on it would mean nothing", against base `service_combo_plan_membership_interaction`'s "The plan cover and the membership discount are never applied to the same labour line: covered labour is already free, so a discount on it is meaningless" (verbatim in base, checked). Nothing is netted off a share taken on the full labour, so there is no deviation and no declaration is needed. |
| **O-33** | **closed** | `extended_policies[3].rule` now reads "…and the two raised figures are added**; where the** line carries labour for one attendance day…". I re-ran my revision-3 scan over all 96 tier conditions: the splice is gone and no genuine instance remains (the eight residual matches are my matcher failing on legitimate paraphrases — "where that day falls on a Saturday", "Where such a charge stands on the job", "Where visits stand in that pool", and the default sentence of `rebill_hourly_rate`). |
| **O-32** | no action, ruling stands | The withdrawn policy-1 declaration still leaves the restatement tier dropping base's minimum-hours floor; inert on both worlds, so no red light, and on the record. |
| **O-4 / O-5 / O-6 / O-8 / O-30** | rulings stand | Nothing this round touches them. |
| **O-15, O-24…O-29, O-31** | carried closed | Re-confirmed against the amended text where it moved. |

### revision_4 / F-19, judged limb by limb

**Limb 1 — is the double mechanism gone, or relocated?** Gone. I checked by deletion and by arithmetic, not by
reading the summary.

- The purpose sentence and its fall-through are absent from both faces. Substring search over
  `extended_policies[1].rule` and `.baseline.rule` for "same charge is not relieved twice", "Nothing comes off on that
  account" and "another ground has already relieved" returns **False in every case**.
- The three `ground_*` bindings are gone from `compute`, and `result` is now
  `MN(MX(RND(discount_owed + credit_applied, 2), 0), outstanding_all)` — no offset term.
- Two mechanisms still read existing write-offs, and they serve **two different purposes**, which is the whole point:
  `outstanding_all = MX(charges_total - payments_total - waivers_total, 0)` is a **ceiling on the total relief**
  (declared in overwrite 4), while `discount_base` fixes the **multiplicand the percentage is taken on** (declared in
  overwrite 1, widened). On task 0's world the 40.00 goodwill write-off reaches the answer through exactly one channel:
  it lowers the base from 267.75 to 227.75, costing 25% of 40.00 = **10.00** of discount. The cap stands at 389.91 and
  does not bind (99.48 is well inside it). In the world where the cap *does* bind it caps the total at what is actually
  owed — which is genuinely lower because of the write-off — rather than re-subtracting it. One purpose, one mechanism.
- Contrast with revision 3, where `ground_offset` removed the **whole** 40.00 from the relief after the percentage,
  which is exactly what the cap also does. The difference between the two rounds is 40.00 against 10.00, and 10.00 is
  precisely the discount on the labour the customer is no longer charged for.

**Limb 2 — is the treatment one a retailer publishes?** Yes, and the arithmetic bears the reworker's three claims out.
The member is billed 267.75 of labour, 40.00 is written off as goodwill for the wait on the part, and the discount is
25% of the 227.75 she is actually charged plus 25% of the surcharge, giving 65.48, plus 34.00 of benefit credit: total
**99.48**. The goodwill gesture keeps its full 40.00 of value to her. A non-member in the same position gets the 40.00
and no discount at all, so the member is better off by the whole 99.48 — where in revision 3 the factor withheld the
whole 40.00 and made the gesture worth nothing to a member. What is withheld now is a discount on money never charged,
which is what a percentage discount means.

**Limb 3 — is the deviation declared, against the clause in force, verbatim?** Yes. The widened `replaced_by` under
`service_combo_plan_membership_interaction` now reads: "Where the labour was billed before the discount had been taken
off it, the relief covers the same share of the surcharge booked on that labour as it covers of the labour itself, **and
the labour that share is worked out on is the labour the customer is actually charged for**." The superseded clause,
"the membership tier's repair labour discount is taken off the chargeable labour before any surcharge is added", is a
verbatim substring of base `service_combo_plan_membership_interaction.rule` (checked). It covers both deviations the
declaration now claims: the surcharge share (unchanged from revision 1) and the labour base. And the declared principle
is coherent across all three tiers of the new factor — plan-covered labour the customer is charged nothing for gives a
base of 0, labour net of other write-offs gives the net figure, and otherwise the labour as it stands.
Base's own reading gives 25% of 267.75 plus 25% of 34.16 = 75.48 and a relief of 109.48; the extended reading gives
65.48 and 99.48; the 10.00 between them is named on the extended side. **No undeclared override remains here**, and
base's goodwill sentence is now simply inherited — the policy no longer invokes it, and a write-off lowering what the
customer owes is not in tension with base's statement about the *ground* on which goodwill is granted.

**F-19: closed.**

### revision_4 / the sixth factor in its new subject, audited from scratch

The factor was renamed and re-subjected, so I audited it as new: `labour_the_share_is_worked_out_on`, `parameter`,
`decides: discount_base`, `bindings: [plan_cover_waivers, other_waivers, discount_base]`.

| test | result |
| --- | --- |
| `decides` an input, not `result` | ✓ `discount_base`, consumed by `discount_owed` |
| no two factors decide one binding | ✓ the displaced factor now decides `labour_scope` with `bindings: [labour_lines, payments_count, labour_total, labour_last_sent, labour_scope]` — disjoint from the new factor's set, and the six factors of the policy decide six distinct bindings (`relief_rate`, `labour_scope`, `surcharge_scope`, `credit_available`, `window_months`, `discount_base`) |
| three tiers, pairwise disjoint as stated | ✓ "a plan-cover write-off stands" / "write-offs on another ground stand **and none granted on a plan's cover does**" / otherwise |
| three distinct outcomes | ✓ on task 0's world the tiers give `discount_base` = 0 / 227.75 / 267.75, and discounts of 8.54 / 65.48 / 75.48 |
| every tier stated in the `rule` and implemented in `compute` | ✓ the three sentences quoted above against `discount_base = 0 if plan_cover_waivers > 0 else (MX(labour_scope - other_waivers, 0) if other_waivers > 0 else labour_scope)` |
| honest baseline that is its fall-through | ✓ `baseline: discount_base: "labour_scope"`, and `baseline.rule` carries exactly that sentence and no other for this quantity: "That labour is taken into the share as it stands." |
| tier rests on seeded records, not a stamp | ✓ the seeded `service_waiver` rows and their `waiver_reason`; nothing names the outcome |
| bears weight on this task's world | ✓ substituting the baseline gives **109.48** against the scored **99.48** — a definite 10.00 |
| label honest | ✓ the tiers select an amount, consistent with this charter's settled convention (O-16) that amount-selection factors are `parameter` |
| outcomes a retailer publishes | ✓ tier 1 is base's own rule, tier 2 is a percentage discount on what is billed, the fall-through is the discount on the labour as it stands |

It is not multi-source (tier 1 is a single condition), which costs nothing: task 0 still carries four multi-source
factors (`surcharge_labour_figure`, `money_already_held`, `older_charges_due`, `labour_relief_share`) and three
membership cross-difficulty factors. **So this is a factor with a real subject, not one kept to fill a slot.** One
check that mattered and passed: substituting `relief_labour_figure`'s baseline propagates correctly *through* the new
factor's tier — `labour_scope` 156.75 → `discount_base` MX(156.75 − 40.00, 0) = 116.75 → 71.73, which is the figure
the artifacts publish, so the two factors chain rather than each freezing the other's intermediate.

### revision_4 / the fourth declaration, judged

`service_ext_membership_service_relief` now declares four overrides (counts across the charter: **1 / 4 / 0 / 2 / 2 / 0**,
matching the report). The new one:

- superseded, from base `service_combo_plan_membership_interaction`: "A membership standing in grace on a tier that
  suspends benefits gives neither the discount nor the credit, and the charge stands in full" — **verbatim in base**,
  checked by substring.
- replaced by: "A Circle membership that does not stand active on the profile, whether it sits in grace with dues
  unpaid or has lapsed altogether, gives neither the discount nor the credit on this job, and the charge stands in
  full."

**The deviation is real, and the sweep's self-found gap is genuine.** Base conditions the loss of benefits in grace on
the tier's own suspension flag, and `blueprint/products/membership.yaml` sets `benefit_suspension_on_grace: False` on
three tiers — Circle Free Membership (which carries no discount and no service credit, so the flag is moot there) and
**Circle Business Pro** (`repair_labour_discount_pct 20`, `service_benefit_credit_usd 200.0`) and **Circle Business
Elite** (`40`, `750.0`). Base therefore leaves a Business Pro or Business Elite membership's benefits standing while it
sits in grace, whereas the policy's `membership_active = EXISTS('membership', status='active')` gives such a membership
nothing. That is exactly the "two Circle tiers whose suspension flag is false" the reworker reports, and it is a
deviation I did not find in three previous rounds. **The declaration is aimed at the clause in force and its
replacement is true to what the compute does** — every membership read is gated on `membership_active`, so the
replacement's "does not stand active … gives neither the discount nor the credit" is the compute's actual behaviour.
No compute or figure changed with it, as reported. One small imprecision recorded as O-36 below.

### revision_4 / the 96-tier scorable-world test

The count is again arithmetically exact: 32 factors × 3 = **96**, recomputed from the inventory (4 / 6 / 4 / 6 / 6 / 6
factors; 12 / 18 / 12 / 18 / 18 / 18 tiers). The three tiers of the new factor I checked directly and they select and
return distinct figures on task 0's world (`discount_base` = 0 / 227.75 / 267.75, giving discounts of
8.54 / 65.48 / 75.48). The tiers I spot-checked in revision 3 are unchanged in policies 1 and 3–6, and the
no-membership limb of policy 2 still returns: with `membership_active = False` the guarded reads give
`window_months = 1`, `credit_applied = 0` and a returning result, and on a no-membership rework world the policy
returns a nonzero, bookable figure. The test holds everywhere I checked it, for the second round running.

### revision_4 / new observations

**O-35 — observation. Under the new factor's first tier the surcharge stays in the share while the labour does not.**
`discount_owed = RND((discount_base + surcharge_scope) * relief_rate / 100, 2)`, so where a plan-cover write-off stands
`discount_base` is 0 and the relief is still a percentage of the surcharge. Read against the declared clause "the relief
covers the same share of the surcharge booked on that labour as it covers of the labour itself", two readings are
available: the *share* is the percentage, identical for both (consistent), or the share is the amount covered, which is
nothing of the labour and a quarter of the surcharge (inconsistent). Neither task's world selects that tier — task 0
carries no plan-cover write-off and task 1's chain does not use this policy — so no figure moves and no reading can be
excluded on the evidence. Recorded so it is on the file rather than rediscovered.

**O-36 — observation. The fourth declaration's replacement names two of the four non-active statuses.**
`db_schema.json.membership_holdings.status` carries `application_received, active, grace, lapsed, cancelled`. The
replacement sentence says "does not stand active on the profile, whether it sits in grace with dues unpaid or has
lapsed altogether", so `application_received` and `cancelled` are covered by the governing clause but not by the
illustration. The compute tests `status='active'` and so treats all four alike, which is what the governing clause
says; the "whether … or …" is illustrative rather than exhaustive. Task 0's membership stands active, so nothing moves.

### revision_4 / closing checklist

**The difficulty closes out.** Both tasks pass all four relationships.

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | **PASS** (F-19 closed) | **PASS** | **PASS** (F-17, F-18, F-19's limb closed) | **PASS** |
| 1 | **PASS** | **PASS** | **PASS** | **PASS** |

Step 4's checklist, item by item:

- **Per-task files correspond one-to-one with the tasks**, `_difficulty.md` sits alongside them, and old revisions are
  traceable: revisions 1, 2, 3 and 4 are preserved verbatim in each file, and `1.md`'s revision_3 record — lost to an
  interruption in round 3 — has been completed this round and is marked as such rather than back-dated. Every
  comparison section carries a verdict, and both tasks' revision_4 comparisons carry PASS on all four relationships.
- **This difficulty's extended policies are fully covered and the two tasks' scopes are pairwise disjoint**: the
  `prerequisite` graph's two components are {surcharge → relief → settlement} and {rebill → contract relief → invoice
  settlement}, they cover all six policies, and both agree with the revealed `charter_scope`. Each scope spans its
  whole tree, root and prerequisites.
- **Task tools and GT are closed, and each tool uses an independently generated, frozen uuid8**: six tools, six
  distinct `(target_tool, computes)` pairs, uuid8s `9a215bff`, `816a24da`, `ea31a412`, `ce7af535`, `51108cc0`,
  `642fded5` with no shared prefix, sequence or tail pattern, on a `task_tools.py` whose content has not changed since
  round 1. No docstring names another tool or a position in a sequence, and no function body judges a prerequisite.
- **Every task's problem tree has one to three prerequisite problems, at least max(n−1,1) `value_input` edges, at least
  one problem resolved by an `owner=user` tool, and no cycle**: both trees are chains of three with n = 2 and two
  `value_input` edges, rooted on `settle_service_bill_ea31a412` and `settle_deployment_invoice_642fded5` respectively,
  both `owner=user` and both handed over passively by the persona. The difficulty's four edges together remain a DAG
  with no cross-task reference.
- **Every computation declares a self-sufficient baseline and four to six factors** (2 `parameter`, 1 `method` per
  policy; per task at least 1 multi-source and 1 cross-difficulty), **every ladder three tiers stated in full in its
  rule, tiers distinct in outcome, conditions and outcomes ones the line of business actually holds, and every factor
  proved to bear weight against an honest baseline, with the baseline alone giving a definite number different from
  gold**: 32 factors, 96 tiers, all verified this round or carried on unchanged text; whole baselines 0.00 / 31.00 /
  429.91 on task 0 and 0.00 / 0.00 / 0.00 on task 1, each definite and each different from gold. I recomputed all six
  scored amounts, all 32 sensitivities and all six baselines independently and they agree with the artifacts to the
  cent.
- **The instantiation-stage gates were re-run on the final form** by the coordinator (all seven green, replay with
  `--check`); I did not run them, as instructed. `check_traceability` remains correctly deferred to the render step and
  is not a defect of this difficulty.

**Observations left open at close-out, none of which moves a scored figure, GT or the uniqueness of a solution:**
O-4, O-5, O-6, O-8 and O-30 (base-layer and tool-contract items, ruled on in revision 2 and confirmed in revision 3,
with the O-8 reason judged correct against `check_task_tools`' `validate_enum`); O-32 (policy 1's withdrawn
declaration leaves the rate-restatement tier dropping base's minimum-hours floor, inert on both worlds); O-35 and O-36
above. Each is recorded with its reasoning so the render step and any later audit inherit the judgement rather than
re-deriving it.

**Four rounds, nineteen findings, all closed.** For the record, because the pattern is the substance of this
difficulty's history: three times a fix opened a defect in whatever replaced it — F-2's rewrite produced F-17 and F-18,
F-18's removal produced F-19, and F-15's rewrite produced the contradiction I found in revision 2 — and this round is
the first in which the replacement itself survives audit. What made the difference is that the fix changed what the
mechanism does rather than what it is called, and that the reworker's own sweeps started finding gaps I had not
reported, which is the sweep working rather than being recited.
