# Policy-task audit — travel_protection_desk / charter-global

## charter_global_frozen

- auditor: independent source-layer auditor (not the instantiating agent)
- freeze time: 2026-09-16, written **before any task's GT fields were revealed**; nothing in this
  section is derived from a revealed GT field.
- frozen inputs and their hashes:
  - `env/online_travel_agency/tasks/travel_protection_desk/care.extended.yaml`
    sha256 `bd6d1e61d8f5d1101b92948a68d43f9d8e3d53cc2402399915d1bf7878282e4d`
  - `env/online_travel_agency/tasks/travel_protection_desk/task_tools.py`
    sha256 `9261c84cbbdbc88b40d1362dbe8b09b3804ce979e1966302064bd9ae2ce8a9b1`
  - `env/online_travel_agency/blueprint/products/care.yaml`, `blueprint.yaml`,
    `db_schema.json`, `share_tools.py` (read in full; permitted)
- fields permitted while this section was written: the whole extended charter (base copy +
  `extended_policies`), the tool module, the blueprint, the DB schema, the share-tool schemas,
  and each task's `frozen_time` / `user_scenario` / `initial_state` through the coordinator's
  masked views.
- fields explicitly masked and not read: `evaluation_criteria`, `computations`, `charter_scope`,
  `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`,
  `db_closure`, `db_closure_matches_initial_state`.
- entry conditions cited, not re-run: the coordinator supplied the seven instantiation gates all
  green (`check_extended`, `check_task_tools`, `replay_tasks`, `check_solvability`,
  `check_compute`, `check_grounding`, `check_cross_fire`) together with their output lines, and
  the two masked views with view/source hashes. Input is complete. A machine green light is
  entry qualification only.

### policy_conflict_scan

The structured policy in force for `care` in this difficulty is the base section of
`care.extended.yaml` (lines 1–1747, byte-identical to `blueprint/products/care.yaml` — verified
by `diff`; the only difference is one trailing blank line) plus six `extended_policies`.

Base policies and the extended policies that touch them:

| extended policy | subject | computes | target_tool | base_policy_refs |
| --- | --- | --- | --- | --- |
| care_ext_third_party_recovery | care_claim_recovery | recovered_amount_usd | book_benefit_recovery_c1be7196 | care_subrogation |
| care_ext_claim_head_filing | care_claim_file | claimed_amount_usd | file_benefit_claim_dde0dff5 | care_claim_filing |
| care_ext_claim_payment_release | care_claim_payout | paid_amount_usd | release_claim_payment_9edda418 | care_claim_settlement, care_agg_benefit_coordination, care_subrogation |
| care_ext_declared_cost_correction | care_insured_amend | corrected_trip_cost_usd | correct_declared_trip_cost_b35383d2 | care_policy_amendment |
| care_ext_premium_rerating | care_premium_adjustment | rerating_amount_usd | raise_premium_rerating_6e8395e4 | care_premium_rating |
| care_ext_cover_release_return | care_cancel, care_premium_refund | returned_premium_usd | release_cover_and_return_premium_07b45938 | care_free_look, care_midterm_cancellation |

Overlapping subjects: no two extended policies share a `subject` event type; no two share a
`computes` name; no two share a target tool. Triggers: five `state_due`, one `on_request`
(`care_ext_cover_release_return`, the only one the customer asks for) — consistent with each
policy's rule.

Time anchors in use: `care_policies.issued_date` (free-look span, cover-bought span),
`care_policies.trip_start_date` / `trip_end_date` (journey span), `care_claims.decided_date`
(latest decision / latest payment), `care_claims.incident_date` (the day the journey was broken
into), `care_policy_requests.submitted_at` / `decided_at` (the day a change takes effect),
`air_booking_events.posted_date` (carrier ledger window and the day an earlier return was
bought), `bundle_ledger_entries` / `stay_folio_entries` (no windows). `care_ext_premium_rerating`
and `care_ext_cover_release_return` both bind `days_of_cover_bought` and both define it by the
same three-tier convention with the same fall-through — no conflict between them.

Cross-category read boundaries declared: `care_ext_third_party_recovery` → air;
`care_ext_claim_head_filing` → air, stay; `care_ext_claim_payment_release` → air;
`care_ext_declared_cost_correction` → bundle, air; the other two declare `cross_category: []`.
Each declaration matches the `XSUM`/`XLATEST`/`CFIELD` calls actually present in that policy's
`compute` and the `inputs.cross_category` list. All reads are read-only history/branch
conditions; every write lands in `care`.

Terminal states: recovery adds a `care_claim_recovery` row; filing adds a `care_claim_file` row;
payment adds a `care_claim_payout` row; correction updates `care_policies.trip_cost_usd`;
re-rating adds a `care_premium_adjustment` row; release sets `care_policies.status='cancelled'`
and adds a `care_premium_refund` row. No two writes touch the same field of the same row.

Task scopes (derived independently from the `prerequisite` graph, not from any masked field):
two disjoint trees that jointly exhaust the six extended policies —

- tree A (root `care_ext_claim_payment_release`) ← `care_ext_third_party_recovery` (value_input)
  and ← `care_ext_claim_head_filing` (state_gate);
- tree B (root `care_ext_cover_release_return`) ← `care_ext_premium_rerating` (value_input)
  ← `care_ext_declared_cost_correction` (value_input).

Pairwise disjoint, jointly complete. No cross-tree edge, so the whole-difficulty `prerequisite`
graph is acyclic.

**No `SOURCE-POLICY RED` was found in this scan.** The undeclared-override and
rule/compute findings below are recorded as observations because their consequence is not
demonstrable on either of this difficulty's two worlds; each names the tasks it bears on.

### rule_compute_equivalence

Check 2 was run over all six extended policies by machine plus a sentence-by-sentence sweep.

Mechanical result (normalised whitespace, substring of the policy's own `rule`):

- every entry of every policy's `compute_basis` is a verbatim substring of that policy's `rule`
  — 0 exceptions across all six policies;
- every sentence of every policy's `baseline.rule` is a verbatim substring of that policy's
  `rule` — 0 exceptions across all six policies;
- every `factors[].ladder[].when` other than `otherwise` is a verbatim substring of the `rule` —
  1 exception (below);
- every `factors[].ladder[].value` / `.method` is a verbatim substring of the `rule` — 5
  exceptions (below).

Every quantity, window, filter, tier, branch, cross-category read, acting base, cap/floor and
rounding point named in a rule has a `compute_basis` quotation and a restricted-expression
binding, and the sweep back found no binding whose basis is absent from the rule.

Rounding: each policy states "rounded to two decimal places once, at the end, and no
intermediate figure is rounded", with the single declared exception in
`care_ext_claim_head_filing` ("no intermediate figure being rounded except the value of the days
not taken") which `compute` honours with `unused_value: RND(..., 2)`. `RND` in the gate
evaluator is Python `round`, i.e. banker's rounding, while the tool docstrings say "rounded half
up to the cent"; no value in this difficulty falls on a .xx5 boundary, so nothing turns on it.

Observation R1 (ladder wording drifts from the rule sentence in six places): the following
ladder entries paraphrase rather than quote the rule sentence that states the tier — pronoun
expansions and one dropped qualifier. Each names a tier the rule does state, so no tier lives
only in `compute` and no branch of a `decides` binding is unstated:

| policy | factor | ladder text | rule text |
| --- | --- | --- | --- |
| care_ext_claim_head_filing | return_home_charges_counted | "the carrier's ledger carries such a fare but no such change fee" | "where it carries such a fare but no such change fee" |
| care_ext_claim_payment_release | benefit_consumed_basis (3 tiers) | "the benefit consumed is worked out from the claim record as the payments made less the recoveries received against them" | "the benefit the policy has consumed is worked out from that record as the payments made under the policy less the recoveries received against them" |
| care_ext_declared_cost_correction | returned_money_excluded | "the money paid back" | "what has been returned is that money" |
| care_ext_premium_rerating | effective_day_anchor | "the day the change takes effect is the day the request was submitted" | "it is the day the request was submitted" |
| care_ext_cover_release_return | collected_lines_scope | "the whole of the lines charged and the re-ratings raised together with the lines already returned" | "the whole of the lines charged and the re-ratings raised on the policy together with the lines already returned on it" |

Bears on: both tasks. No consequence: the tiers themselves are stated in full in each rule.

Observation R2 (`care_ext_third_party_recovery`: a general rule term implemented as one fixed
head). Rule: "Where a deductible was withheld from **the settlement the compensation answers**
and the compensation counted is more than that deductible, what is set aside for the traveller
is the deductible withheld from that settlement". `compute` implements it as
`deductible_on_settlement: "SUM('care_claims','deductible_applied_usd',
event_type='care_claim_payout', claim_type='missed_connection')"` — the missed-connection head
regardless of which of the three tiers `settlement_answered` took. Where `settlement_answered`
is the travel-delay payment or the payment standing last, the deductible read is still the
missed-connection one. Bears on: task 0. Consequence not demonstrable there: on task 0's world
`settlement_answered` takes tier 1 (the missed-connection payment), so the two readings
coincide; recorded as an observation, not a red light.

Observation R3 (`care_ext_third_party_recovery`: `money_counted` tier conditions do not test
what the rule says). Rule: "Where **the settlement the compensation answers was made on a missed
connection** and the carrier's ledger carries payouts raised on an involuntary schedule change,
the money counted is …; where **the settlement was made on a baggage head** and the carrier's
ledger carries payouts raised on an airline cancellation, …". `compute` tests
`missed_connection_payments > 0` and `baggage_payments > 0` — the existence of a payment on that
head, not that `settlement_answered` is that payment. Tier 1 happens to be equivalent (both
limbs require `carrier_schedule_change_payouts > 0`, which is exactly when
`settlement_answered` is the missed-connection payment); tier 2 is not — a world with
`carrier_schedule_change_payouts == 0`, a travel-delay payment (so `settlement_answered` is the
travel-delay payment), a baggage payment and cancellation payouts fires tier 2 although the
settlement was not made on a baggage head. Bears on: task 0. Consequence not demonstrable
there: tier 1 fires. Observation.

Observation R4 (`care_ext_declared_cost_correction`: two compute conditions narrower than the
rule sentence). `holiday_prepaid` tier 2 adds `and pkg_deposits > 0` to the rule's "where the
holiday's final payment has not been taken"; `insured_share` tier 2 tests
`party_adults > F('insured_count')` where the rule says "the party is larger than the travellers
named **and children travel in it**" (party size being adults plus children). A party of two
adults and two children with two named insured satisfies the rule's tier 2 and falls through to
1.0 in `compute`. Bears on: task 1. Consequence not demonstrable there: the seeded party is
three adults and no children, so tier 1 fires on both readings. Observation.

### action_binding_and_uuids

Each `(target_tool, computes)` pair is claimed by exactly one policy — the six pairs in the
table above are pairwise distinct in both coordinates. No policy's subject, base refs, target
tool, docstring and terminal state admit a second business reading, and no docstring adds a
confirmation, review or wait.

Docstring ordering scan (`before|after|first|then|next|subsequently|prior to|once you`): 11
hits, all inside the eleven-head `claim_type` enum gloss ("the journey was called off before it
began", "a journey already begun was cut short"), inside an object description ("a settlement
already paid", "the decision already made on the claim is untouched", "the money claimed before
any limit or deductible") or inside the effect description of the release tool ("no incident
after that moment is covered"). **No docstring states an action's position in a sequence, names
another tool, or carries a cross-call ordering word.**

uuid8s: `c1be7196`, `dde0dff5`, `9edda418`, `b35383d2`, `6e8395e4`, `07b45938`. Six distinct
8-hex tails, no shared prefix, no arithmetic or lexical progression, none a re-tailed copy of
another. Each is frozen with its tool (it appears in the policy's `target_tool`, in the
prerequisite `resolved_by` fields and nowhere else). PASS.

### prerequisite_graph

Check 7 over the whole graph. All six policies fill in `prerequisite` (three carry `[]`).

| blocked policy | problem | kind | gate | form | resolved_by | acyclic |
| --- | --- | --- | --- | --- | --- | --- |
| care_ext_claim_payment_release | care_ext_third_party_recovery | value_input | benefit_consumed | state | book_benefit_recovery_c1be7196 | yes |
| care_ext_claim_payment_release | care_ext_claim_head_filing | state_gate | care_claims.claim_status | state | file_benefit_claim_dde0dff5 | yes |
| care_ext_premium_rerating | care_ext_declared_cost_correction | value_input | rated_premium | state | correct_declared_trip_cost_b35383d2 | yes |
| care_ext_cover_release_return | care_ext_premium_rerating | value_input | premium_ledger | state | raise_premium_rerating_6e8395e4 | yes |

- every `problem` points at another extended policy id in this file; none points at a base
  policy and none at itself;
- the graph is `{recovery, filing} → payment` and `correction → rerating → release`: two
  disjoint DAGs, no cycle, no cross-tree reference;
- every `policy_source` is verbatim locatable in the **blocked** policy's own `rule` — machine
  check, 4/4 located;
- every `form` is `state`; no edge is action-form, so no `fallback_reason` is required and none
  is present. Correct.
- `kind`/`gate` agreement: `benefit_consumed`, `rated_premium` and `premium_ledger` are all real
  binding names in the blocked policy's own `compute` (value_input, correct);
  `care_claims.claim_status` is the record state the filing write leaves and the blocked rule's
  own gate sentence names (state_gate, correct);
- every `resolved_by` is the depended-on policy's own `target_tool`; each genuinely makes the
  described `effect` hold (demonstrated per task in the task files);
- no `prerequisite` field contains authoring-viewpoint phrasing ("in this task", "at the
  opening", "the current world") — scanned, 0 hits.

PASS.

### prerequisite_sentences

Check 6, four-point test on each of the four edges.

**E1 — care_ext_claim_payment_release ← care_ext_third_party_recovery.**
Sentence (verbatim in the blocked rule): "The money paid on a decided claim is worked out only
after the policy's claim record carries the recovery owed for every compensation a liable third
party has paid the traveller on a settlement already made under this policy."
(1) ordering connective: "only after". (2) form: state — what it waits on is "the policy's claim
record carries the recovery owed …", a record-visible state in the words `care_claims` and the
`find_care_claims` finder use; no performer, no action verb applied to the desk. (3) names no
tool, no policy id, no snake_case token, no row id. (4) strength: the `condition` field says
"carries a recovery row against **every** settlement for which a liable third party has paid the
traveller compensation" — the same open set the sentence states, neither narrowed nor widened.
State-form derivation, single reading: exactly one write in this difficulty puts a
`care_claim_recovery` row on `care_claims` — `book_benefit_recovery_c1be7196`, the target tool of
`care_ext_third_party_recovery`, whose own rule opens "Where a liable third party has paid the
traveller for a loss this policy has already settled, the insurer recovers what it paid, and the
recovery restores the benefit that settlement consumed." No other policy's rule describes a
write that leaves that state, so the reader resolves the hop in one way.

**E2 — care_ext_claim_payment_release ← care_ext_claim_head_filing.**
Sentence: "A payment is released on a decided claim only once every benefit the same incident
has touched stands filed on the policy, because one incident is settled as one case."
(1) "only once". (2) state form — "every benefit … stands filed on the policy" is a record state
of `care_claims`. (3) no tool, id or token. (4) the `condition` restates it as "Every benefit the
incident behind the decided claim has touched stands on the policy's claim record as a claim
filed under the reference the insurer quoted for that incident" — the same scope; the reference
clause adds no strength beyond what `care_ext_claim_head_filing`'s own first rule sentence
already fixes. Single write bringing the state about: `file_benefit_claim_dde0dff5` is the only
tool that creates a `care_claim_file` row.

**E3 — care_ext_premium_rerating ← care_ext_declared_cost_correction.**
Sentence: "The re-rating owed on a correction is worked out only after the certificate carries
the declared particulars the underwriting desk has approved for it."
(1) "only after". (2) state form — "the certificate carries the declared particulars … approved".
(3) clean. (4) `condition` narrows the general "declared particulars" to "the declared trip cost
standing on the certificate", which is the only declared particular this difficulty's charter
lets any write change; not a strengthening in substance. Single write:
`correct_declared_trip_cost_b35383d2` is the only tool that updates
`care_policies.trip_cost_usd`.

**E4 — care_ext_cover_release_return ← care_ext_premium_rerating.**
Sentence: "The premium returned is fixed only after the policy's premium record carries the
re-rating owed on every correction of the certificate's declared particulars."
(1) "only after". (2) state form — "the policy's premium record carries the re-rating owed …".
(3) clean. (4) `condition` states the same open set ("a re-rating line for every correction").
Single write: `raise_premium_rerating_6e8395e4` is the only tool that creates a
`care_premium_adjustment` row.

**No second wording, no tool name and no other problem's id appears in any of the four blocked
rules about its dependency; no depended-on rule restates its blocker's sentence.** Checked by
reading all six rules end to end. `care_ext_claim_head_filing`'s own first sentence ends
"because one incident is settled as one case", the same clause that closes E2's sentence, but it
states that policy's own one-head-per-reference rule and carries no ordering connective and no
reference to a payment — it is not a restatement of the blocked side's sentence.

Observation P1 (a base rule carries a cross-problem order that grounds no declared edge).
`care_agg_benefit_coordination` (base) states "A recovery from a liable third party is applied
first to the policy that paid last, restoring its benefit before the primary's." — an ordering
sentence over recoveries across two policies. No declared edge rests on it and neither task's
tree uses it (each task's customer has at most one policy answering the incident), so per check 6
this is recorded as an observation rather than a red light. Bears on: task 0.

### override_declarations

Check 1, sentence by sentence against every `base_policy_refs` entry, run once over all six
extended policies. Findings only; the demonstration of what each costs a particular task lives
in that task's file.

**Declared and sound (2 overwrites in the charter):**

- `care_ext_claim_head_filing` names `care_claim_filing`'s "A claim is filed only when no claim
  carrying the same claim reference has already been filed on this policy." and replaces it with
  the one-head-per-benefit-per-reference rule. Verbatim match on the superseded clause; the
  merged semantics are unique (a second claim under one reference is permitted iff it is against
  a different benefit).
- `care_ext_cover_release_return` names `care_free_look`'s "A free-look cancellation is handled
  at the full refund only when frozen time is not after the moment the certificate of insurance
  was issued to the policyholder plus the free-look period of the plan held." and replaces it
  with the three-tier share ladder. Verbatim match; merged semantics unique.

**Sentence-by-sentence conclusions on the remaining base sentences.** Every base provision not
hit by an `overwrite` was read and a conclusion reached on it. The ones extended follows are not
listed; the ones extended handles differently and does **not** declare are:

Observation O1 — `care_subrogation` → `care_ext_third_party_recovery` (`overwrite: []`).
Base: "A traveller who has been compensated for the same loss by the airline, the property or
another supplier must say so, **and the settlement is reduced by what they received rather than
recovered afterwards**." The extended policy recovers afterwards, out of the carrier's payouts in
the twelve months before the recovery is booked — the route base names as the one not taken.
Bears on: task 0. Consequence not demonstrable there: every carrier payout and credit the
extended computation counts posted *after* the settlement it answers (see task 0 file), so base's
"reduce the settlement instead" is inapplicable and the two never produce two answers on that
world. Observation.

Observation O2 — `care_claim_settlement` → `care_ext_claim_payment_release` (`overwrite: []`),
the fall-through limb. Base: "Each benefit has its own limit: **cancellation and interruption are
shares of the declared trip cost**, medical, evacuation and accident benefits are amounts per
insured traveller, and baggage, delay and rental benefits are amounts per traveller …". The
extended ladder's fall-through is "the benefit limit that applies is the declared trip cost
standing on the certificate" — the whole declared trip cost, not the plan's
`trip_cancellation_limit_pct` / `trip_interruption_limit_pct` share of it (75/75 to 150/150
across the plans). Bears on: task 0. Consequence not demonstrable there: the head decided is a
travel delay, so tier 1 (`travel_delay_limit_usd`) fires and the fall-through is never reached.
Observation.

Observation O3 — `care_policy_amendment` → `care_ext_declared_cost_correction`
(`overwrite: []`). Base: "An increase in the declared trip cost is accepted only up to the plan's
ceiling, and **a trip whose cost has grown beyond it is upgraded to a higher plan rather than
amended**." Extended silently caps at the ceiling instead (`MN(journey_prepaid,
P('max_trip_cost_usd'))`). Bears on: task 1. Consequence not demonstrable there: the corrected
figure sits far below the TripGuard Plus ceiling of 20 000.00, so the cap never binds.
Observation.

Observation O4 — `care_premium_rating` → `care_ext_premium_rerating` (`overwrite: []`), a
**dropped branch**. Base: "Where a declared particular changes after issue, the premium is
re-rated from the day the change takes effect and the difference is **charged or returned** pro
rata over the remaining days of cover." Extended states "The difference is never less than
nothing" and implements `MX(rated_premium - collected_premium, 0)`; the return branch base
declares is never produced by extended's selector. Bears on: task 1. Consequence not
demonstrable there: the corrected trip cost is higher than the one rated at issue, so the
difference is positive on that world. Observation.

Observation O5 — `care_premium_rating` → `care_ext_premium_rerating` (`overwrite: []`), the
fall-through rate. Base: the premium is "loaded for the age of the oldest insured traveller **and**
for the declared destination region … the two loadings are added to one another and not
compounded." Extended's fall-through tier is "the plan's base rate together with the plan's
destination loading percentage" — the age loading is absent, and that tier can be reached with an
age-loading line on the record (the selector's second limb requires `age_loading_lines == 0`, so
a record with an age loading but no destination loading falls through). Bears on: task 1.
Consequence not demonstrable there: tier 1 fires. Observation.

Observation O6 — `care_free_look` → `care_ext_cover_release_return` (`overwrite` names only the
window sentence), an **anonymous intermediate**. Base: "**Inside the free-look period the whole
premium is returned** to the original form of payment, the policy fee excepted, and the agency's
commission is recovered in full." Extended multiplies the free-look share by
`days_of_cover_remaining / days_of_cover_bought`, so inside the free-look period it returns less
than the whole premium, with no new parameter name and no declaration. Bears on: task 1.
Consequence not demonstrable there: the cancellation is 22 days after issue against a 14-day
free-look period, so tier 1 (the mid-term share) fires and the free-look limb is never reached.
Observation.

Observation O7 — `care_free_look` → `care_ext_cover_release_return`, the lost-right sentence.
Base: "The free-look right is lost as soon as **the journey has begun** or a claim has been
filed, whichever comes first". The extended share ladder carries the claim half ("where a claim
stands filed on the policy, nothing is returned") and drops the journey half: a policy inside its
free-look days whose journey has begun still takes the 100 % free-look share under extended.
Bears on: task 1. Consequence not demonstrable there: the journey begins 2026-10-10, after
frozen time. Observation.

Observation O8 — `care_free_look` → `care_ext_cover_release_return`, the refund-line shape.
Base: "A returned premium is raised against the premium lines that collected it, so **a policy
with several premium lines returns as several refund lines**." `release_cover_and_return_premium_07b45938`
takes one `source_entry_id` and writes one refund line. Bears on: task 1 — and unlike O1–O7 this
one does bite on that world, because it leaves the `source_entry_id` argument without a
policy-entailed value among the four premium lines that collected the premium. The demonstration
is in `1.md`.

Observation O9 — `care_claim_filing`'s dedup block survives the declared override. The
`overwrite` in `care_ext_claim_head_filing` names the rule sentence verbatim, and the same
sentence is also the `condition` of the base eligibility entry `one_claim_per_reference`, whose
`dedup_contract` (`duplicate_filters.claim_status: [filed, in_assessment, approved,
partly_approved, paid]`) is left standing untouched in the base copy. Naming the sentence
supersedes it wherever the sentence appears, so this is not an undeclared override; but the
structured dedup block is a second carrier of the superseded prohibition. Bears on: task 0.

### factor_ladders

Charter-global structure only; whether each factor bears weight is in each task's `factor_weight`.

| policy | factors | parameter | method | tiers each | multi-source tiers | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| care_ext_third_party_recovery | 4 | money_counted_ground, traveller_share_rule | settlement_answered_rule, credit_valuation | 3,3,3,3 | settlement_answered_rule, money_counted_ground, traveller_share_rule | air (3 factors) |
| care_ext_claim_head_filing | 5 | journey_value_basis, return_home_charges_counted, supplier_returned_rule | unused_days_anchor, return_home_credit_offset | 3,3,3,3,3 | journey_value_basis, unused_days_anchor, supplier_returned_rule | air (4), stay (1) |
| care_ext_claim_payment_release | 4 | benefit_limit_by_head, deductible_withheld_rule, third_party_offset | benefit_consumed_basis | 4,3,4,3 | deductible_withheld_rule, third_party_offset | air (1) |
| care_ext_declared_cost_correction | 6 | returned_money_excluded, credit_settlement_excluded, party_share, flights_bought_apart | holiday_cost_basis, prepaid_scope | 3,3,3,3,3,3 | holiday_cost_basis, returned_money_excluded, party_share, flights_bought_apart | bundle (5), air (1) |
| care_ext_premium_rerating | 4 | rate_applied_source, collected_premium_scope | effective_day_anchor, cover_span_convention | 3,3,3,3 | rate_applied_source, collected_premium_scope, effective_day_anchor | none |
| care_ext_cover_release_return | 4 | collected_lines_scope, share_allowed_by_plan | cover_bought_convention, cover_remaining_convention | 3,3,3,3 | collected_lines_scope, share_allowed_by_plan | none |

- every policy declares 4 to 6 factors, at least 2 `parameter` and at least 1 `method`;
- every ladder has at least three pairwise-disjoint tiers as stated, the fall-through counted
  (the two four-tier ladders, `benefit_limit_by_head` and `deductible_withheld_rule`, are
  disjoint on the head decided and on the ceiling remaining respectively);
- every factor's `bindings` list is disjoint from every other factor's within its policy
  (checked policy by policy; no binding name appears in two factor binding sets);
- every `decides` is an intermediate input of the computation, never `result`;
- every tier's value or method is drawn from the charter — plan parameters (`travel_delay_limit_usd`,
  `baggage_delay_limit_usd`, `medical_emergency_limit_usd`, `medical_deductible_usd`,
  `rental_damage_deductible_usd`, `deductible_per_claim_usd`, `deductible_per_policy_usd`,
  `free_look_days`, `free_look_refund_pct`, `mid_term_cancel_refund_pct`,
  `premium_base_rate_pct`, `destination_loading_pct`, `max_trip_cost_usd`), holding fields, or
  aggregates over the declared tables;
- per task, the factors of the task's policies include at least one multi-source factor and at
  least one `cross_difficulty` factor (tree A: air and stay; tree B: bundle and air through
  `care_ext_declared_cost_correction`);
- every `method` tier names a computation rule the charter states, and every `parameter` tier a
  number the charter fixes.

Observation F1 (two `method` labels are arguable). `credit_valuation`
(`care_ext_third_party_recovery`) and `return_home_credit_offset`
(`care_ext_claim_head_filing`) both reduce, on any world, to substituting one of two ledger
aggregates or zero into an otherwise fixed expression (`compensation_counted = money_counted +
credit_counted`; `return_home_cost = MX(return_home_charges − X, 0)`). They select which records
are read and aggregated rather than a plan constant, which is why they are not recorded as
mislabels; but a strict reading of "changes the algorithm" would call them `parameter`. Even
under that strict reading both policies still hold 2+ `parameter` and 1 `method`
(`settlement_answered_rule` and `unused_days_anchor` are unarguably `method`), so the counts do
not move. Bears on: task 0. No consequence.

### findings

| id | kind | bears on | one line |
| --- | --- | --- | --- |
| R1 | observation | 0, 1 | six ladder entries paraphrase rather than quote the rule sentence that states the tier |
| R2 | observation | 0 | `deductible_on_settlement` is hard-wired to the missed-connection head where the rule says "that settlement" |
| R3 | observation | 0 | `money_counted` tiers test the existence of a payment on a head, not that the settlement was made on it |
| R4 | observation | 1 | two `care_ext_declared_cost_correction` compute conditions are narrower than their rule sentence |
| P1 | observation | 0 | base `care_agg_benefit_coordination` states a cross-policy recovery order that grounds no declared edge |
| O1 | observation | 0 | base care_subrogation says reduce the settlement "rather than recovered afterwards"; extended recovers afterwards, undeclared |
| O2 | observation | 0 | extended's fall-through benefit limit is the whole declared trip cost where base makes cancellation/interruption a share of it, undeclared |
| O3 | observation | 1 | extended caps the declared trip cost at the plan ceiling where base upgrades the plan instead, undeclared |
| O4 | observation | 1 | dropped branch: base re-rating is "charged or returned", extended never returns, undeclared |
| O5 | observation | 1 | extended's fall-through rate drops the age loading base requires, undeclared |
| O6 | observation | 1 | anonymous intermediate: extended pro-rates the free-look return base gives in full, undeclared |
| O7 | observation | 1 | extended's share ladder drops base's "free-look right lost once the journey has begun" |
| O8 | observation | 1 | base returns "several refund lines"; the tool writes one, leaving `source_entry_id` unentailed — demonstrated in `1.md` |
| O9 | observation | 0 | the superseded dedup sentence also survives as a structured `dedup_contract` in the base copy |
| F1 | observation | 0 | two `method` labels are arguable; the per-policy counts hold under either reading |

**No charter-global `SOURCE-POLICY RED`.** Per-task verdicts are in `0.md` and `1.md`.

## closing_checklist

Written after both tasks reached PASS on all four relationships; this section, unlike everything
above it, is post-reveal by construction and is therefore kept below the charter-global section.

- **Per-task files correspond one-to-one with the tasks.** `0.md` and `1.md` sit alongside this
  file in `env/online_travel_agency/audits/policy_task/travel_protection_desk/`, one per task file
  in `tasks/`. This is revision 1, so there are no older revisions to preserve; both comparison
  sections carry a **PASS**.
- **The difficulty's extended policies are fully covered and the two task scopes are pairwise
  disjoint.** Task 0 spans `{care_ext_claim_payment_release, care_ext_third_party_recovery,
  care_ext_claim_head_filing}` and task 1 spans `{care_ext_cover_release_return,
  care_ext_premium_rerating, care_ext_declared_cost_correction}` — the whole problem tree in each
  case, root and prerequisites. Their union is the six extended policies, their intersection is
  empty, and the six task tools split the same way. GT's `charter_scope` agrees with the scopes I
  derived from the `prerequisite` graph alone.
- **Task tools and GT are closed.** Every tool a gold step calls is one of the six in
  `task_tools.py` (plus the shared finders, `verify_traveller_identity` and the unlock/call meta
  tools); every gold argument's value is a row id, a field value or a persona statement present in
  that task's world; no gold step reaches outside the declared read set.
- **Each task tool uses an independently generated, frozen uuid8** — `c1be7196`, `dde0dff5`,
  `9edda418`, `b35383d2`, `6e8395e4`, `07b45938`; six distinct tails, no shared prefix, no
  progression, none re-tailed from another (see `action_binding_and_uuids`).
- **Problem trees.** Each task has exactly 2 prerequisite problems (within the 1–3 bound); task 0
  has 1 `value_input` edge and task 1 has 2, against a floor of `max(n−1, 1) = 1`; each tree has at
  least one problem resolved by an `owner=user` tool (`file_benefit_claim_dde0dff5` in task 0,
  `release_cover_and_return_premium_07b45938` — the root itself — in task 1); neither tree has a
  cycle. Taken together, the difficulty's four `prerequisite` edges form two disjoint chains with
  no cross-task reference, so the whole-difficulty graph remains a DAG.
- **Computations, baselines and factors.** Six computations, each declaring a self-sufficient
  `baseline` whose every sentence is verbatim in its policy's `rule` and whose whole-baseline value
  is definite and different from gold (100.00 / 1772.73 / 700.00 for task 0; 10300.00 / 119.39 /
  777.52 for task 1). Twenty-seven declared factors in all (4+5+4 and 6+4+4), each policy within
  4–6, each with at least 2 `parameter` and 1 `method`, every ladder at least three
  pairwise-disjoint tiers stated in full in its own `rule`; each task carries multi-source factors
  in all three of its computations and cross-difficulty factors reading air and stay (task 0) and
  bundle and air (task 1), with every row those reads touch seeded in `initial_state`. All
  twenty-seven were independently recomputed under their own `baseline` bindings and every one
  moved the scored value.
- **Instantiation gates re-run on the final form** from the repository root with
  `DIFF=env/online_travel_agency/tasks/travel_protection_desk`:
  `check_extended` **EXTENDED OK**; `check_task_tools` **TASK TOOL CONTRACT OK**;
  `replay_tasks` **REPLAY OK** (0.json 15 acts / 37 closure rows, 1.json 16 acts / 18 closure rows,
  both deterministic, non-vacuous, no errors, closure matching `initial_state`);
  `check_solvability` **SOLVABILITY OK**; `check_compute` **COMPUTE OK**
  (branches 59 / 53, steps 15 / 16, suite means 56.00 and 15.50, `history_rows_max` 15);
  `check_grounding` **GROUNDING OK**; `check_cross_fire` **SCOPE OK**. Unchanged from the snapshot
  the coordinator supplied, as expected — this audit edited no artifact.

**Difficulty verdict: PASS.** Policy self-consistency, the problem trees, the factors' weight and
the unique solution all hold for both tasks. Fifteen charter-global observations (R1–R4, P1, O1–O9,
F1) and four per-task observations (0-A, 0-B, 1-A, and the withdrawn 1-B) are on record; none of
them meets the demonstrated-consequence bar for a red light on either of this difficulty's worlds,
and the most substantive of them — **O8 / Finding 1-A**, `source_entry_id` left unentailed by the
charter — is recorded as an observation only because the charter says nothing that would make a
different line wrong, not because it is harmless.

---

# revision_2 — re-audit of the reworked charter

Revision 1 above is left exactly as written. Nothing in it has been altered.

## charter_global_frozen (revision 2)

- auditor: the same independent source-layer auditor; freeze time 2026-09-16, written **before any
  GT field of either task was read in this round**.
- re-derivation decision, taken against the rule "a re-audit re-derives a charter-global section
  only when its shared inputs can have moved it":
  - `care.extended.yaml` sha256 `4e2fa251fbe432245cfa5843ecf5f2cb411e25bcf986ee4df05b49a1df880cf5`
    — **CHANGED** from revision 1's `bd6d1e61d8f5d1101b92948a68d43f9d8e3d53cc2402399915d1bf7878282e4d`.
    Every charter-global section is therefore re-derived in full below.
  - `task_tools.py` sha256 `9261c84cbbdbc88b40d1362dbe8b09b3804ce979e1966302064bd9ae2ce8a9b1`
    — **UNCHANGED**. `action_binding_and_uuids`' tool half (docstrings, uuid8s, the absence of
    ordering words and of eligibility logic in the function bodies) is carried forward by reference
    on the strength of that hash; the `(target_tool, computes)` half is re-derived because the
    charter moved.
- masked views: task 0 `29955e8e…` **unchanged**; task 1 `d56b3804…` **changed** from `9033dc57…`.
- **contamination_disclosure (revision 2).** This is a re-audit by the auditor who performed
  revision 1, so I carry revision 1's revealed GT — the six `expected` values, the six
  `baseline_result` values, the 27 factor-sensitivity figures, the gold write order and both
  round-1 `source_entry_id` values — into this round's derivation. That knowledge cannot be
  unlearned and I do not pretend otherwise. What I have done instead: every figure in this revision
  was **recomputed from the round-2 charter and the round-2 masked worlds** by the same evaluator,
  and every one is reported as computed rather than as remembered; the entailment question this
  round turns on (which premium line the rule now names) was decided by reading the new rule
  sentence against the seeded rows, not by consulting the round-1 gold value — and I record below
  that the round-1 gold value would have been no help, because the question is whether the *rule*
  now reaches it. No round-2 GT field was read before this section and both per-task revision_2
  freezes were on disk.

### what moved, item by item (verified against the artifacts, not the reworker's report)

The reworker's claims were treated as claims. Verified:

| claimed change | verified? | evidence |
| --- | --- | --- |
| base copy still verbatim | **yes** | `diff` of `care.yaml` lines 1–1747 against `care.extended.yaml` lines 1–1747: no difference |
| `care_ext_premium_rerating.rule` gained a sentence naming the line | **yes** | new third paragraph, quoted below |
| `care_ext_cover_release_return.rule` gained the same, plus a second `overwrite` | **yes** | new third paragraph; `overwrite` now has 2 entries |
| `care_ext_declared_cost_correction` gained an `overwrite` against `care_club_and_bundle_interaction`, added to `base_policy_refs` | **yes** | `base_policy_refs: [care_policy_amendment, care_club_and_bundle_interaction]`, `overwrite` has 1 entry |
| four declared overrides, up from two | **yes** | 1 (head_filing) + 1 (declared_cost_correction) + 2 (cover_release_return) = 4 |
| one seeded `charge_category` changed | **yes** | `bundle_ledger_entries["4411594c-0e6a-425c-af10-c4629845ff11"].charge_category`: `flight_upgrade` → `excursion_component`; `diff` of the two masked worlds shows that field and nothing else |
| task 0's world byte-identical | **yes** | view sha256 unchanged; `diff` of the round-1 and round-2 `initial_state` dumps is empty |
| all six `expected` and `baseline_result` unchanged | **yes** | recomputed: 130.00 / 2335.45 / 390.00 and 8806.67 / 108.36 / 127.99; fall-backs 100.00 / 1772.73 / 700.00 and 10300.00 / 119.39 / 777.52 |
| "the gap is task 1's `source_entry_id`, not task 0's" | **yes** | task 0's three writes take `source_claim_id`, and each is pinned by a rule sentence — re-derived in `0.md` revision_2 |

Task 0's three extended policies (`care_ext_third_party_recovery`, `care_ext_claim_head_filing`,
`care_ext_claim_payment_release`) are byte-identical in effect: their `rule`, `compute`,
`compute_basis`, `factors`, `baseline` and `prerequisite` all re-pass every mechanical check below
and re-produce every revision-1 figure. Nothing regressed there.

### policy_conflict_scan (revision 2)

Six extended policies, unchanged in identity, subject, `computes` and `target_tool`; the two trees
and their scopes are unchanged (tree A = {payment_release ← recovery, head_filing}, tree B =
{cover_release ← rerating ← correction}); pairwise disjoint, jointly complete, acyclic. No new
overlapping subject, trigger, time anchor, action parameter or terminal state was introduced: the
three added sentences fix a **tool argument** (which premium line a derived line is raised against),
not a computed quantity, and touch no `compute` binding, no ladder and no eligibility.

Cross-category declarations re-checked against the `compute` calls and `inputs.cross_category`: the
correction still declares `[bundle, air]`, the recovery and the payment `[air]`, the filing
`[air, stay]`, the re-rating and the release `[]`. All agree.

### rule_compute_equivalence (revision 2)

Re-run mechanically over all six policies on the round-2 file:

- every `compute_basis` entry is a verbatim substring of its policy's `rule` — **0 exceptions**;
- every sentence of every `baseline.rule` is a verbatim substring of its `rule` — **0 exceptions**;
- every ladder `when` other than `otherwise` is verbatim in the `rule` — **1 exception**, the same
  one as revision 1 (`return_home_charges_counted`);
- every ladder `value`/`method` is verbatim in the `rule` — **5 exceptions**, the same five as
  revision 1.

So **R1 is unchanged** — neither widened nor narrowed by the rework — and remains an observation.
**R2, R3 and R4 are unchanged** in text and, on the round-2 worlds, unchanged in consequence (each
is re-tested in the per-task files). The three added sentences introduced no new `compute` binding
and no new empty promise: each is a norm about which row a write points at, which is the same kind
of sentence as the base sentence it replaces (`care_free_look`'s "raised against the premium lines
that collected it"), and the argument it fixes is checked by the grounding gate rather than by a
compute binding.

**The added sentences did not break what they sit beside.** Verified explicitly, because that was a
stated risk of the fix:

- `care_ext_premium_rerating.baseline.rule` is still a verbatim subset of its `rule` and still
  contains none of the new sentence — the new sentence sits *after* the baseline block and the
  prerequisite sentence, so a reader of the computation document alone still computes the same
  definite fall-back (119.39 on task 1's world, recomputed);
- all four of that policy's ladders (`rate_applied_source`, `collected_premium_scope`,
  `effective_day_anchor`, `cover_span_convention`) still have every tier verbatim in the `rule`
  and still select the same tier on task 1's world;
- `care_ext_cover_release_return.baseline.rule` is likewise still a verbatim subset, its fall-back
  is still 777.52, and all four of its ladders still resolve as before;
- the **fall-back clause inside the new sentence itself** ("where the premium record carries no
  such line it is raised against the earliest line charged on the policy") is a genuine
  fall-through, not a dead limb: it fires exactly when no `base_premium` line exists, which is a
  reachable world (an annual multi-trip plan is charged a flat annual premium rather than a base
  rate on a trip cost, per base `care_premium_rating`), and it is not reached on task 1's world;
- the **two original declarations are intact**: `care_ext_claim_head_filing`'s overwrite against
  `care_claim_filing` and `care_ext_cover_release_return`'s first overwrite against `care_free_look`
  are still verbatim on both sides (machine-checked below).

### action_binding_and_uuids (revision 2)

`(target_tool, computes)` re-derived on the round-2 charter: the same six pairs, each claimed by
exactly one policy, pairwise distinct in both coordinates. The tool module is unchanged by hash, so
the docstring ordering scan, the uuid8 independence check (`c1be7196`, `dde0dff5`, `9edda418`,
`b35383d2`, `6e8395e4`, `07b45938`) and the function-body check are carried forward from revision 1
by reference on the strength of `9261c84c…`. PASS.

One point re-checked rather than carried, because the charter moved around it: the three added
sentences name **no tool**, no policy id and no snake_case token, and carry **no ordering
connective** — "because", "where … no such line", and "are never the line" are causal, conditional
and exclusionary respectively. They therefore create no undeclared cross-problem order and add no
second wording to any declared dependency.

### prerequisite_graph and prerequisite_sentences (revision 2)

Re-derived on the round-2 file. The four edges, their `kind`, `gate`, `form`, `condition`,
`policy_source` and `resolved_by` are unchanged; every `policy_source` is still verbatim locatable
in the **blocked** policy's own `rule` (machine check, 4/4); every `form` is still `state`, so no
`fallback_reason` is required and none is present; the graph is still two disjoint chains and still
acyclic; `benefit_consumed`, `rated_premium` and `premium_ledger` are still real bindings of their
blocked policies' `compute`, and `care_claims.claim_status` is still the state the filing write
leaves. No authoring-viewpoint phrasing. The four-point test on each of the four prerequisite
sentences is unchanged from revision 1 and re-passes; **P1** (base `care_agg_benefit_coordination`'s
cross-policy recovery order grounding no edge) is unchanged and remains an observation.

Specifically checked, because a new sentence was inserted into two blocked rules: neither added
sentence states an order between problems, neither names the depended-on policy's tool, and neither
restates the policy's prerequisite sentence in a second wording. The depended-on rules
(`care_ext_declared_cost_correction`, `care_ext_premium_rerating`) still do not restate their
blockers' sentences.

### override_declarations (revision 2)

Four declarations now. Each was machine-checked for (a) `superseded_clause` verbatim in the named
**base** policy's `rule`, (b) `replaced_by` verbatim in the **declaring extended** policy's `rule`,
and (c) whether the superseded clause is also the `condition` of a base eligibility entry:

| declaring policy | base policy | superseded verbatim in base rule | replaced_by verbatim in extended rule | also a base eligibility condition? |
| --- | --- | --- | --- | --- |
| care_ext_claim_head_filing | care_claim_filing | **yes** | **yes** | yes — `one_claim_per_reference` (pre-existing, revision 1) |
| care_ext_declared_cost_correction | care_club_and_bundle_interaction | **yes** | **yes** | **no** — that base policy's `eligibility` is `[]` |
| care_ext_cover_release_return | care_free_look (window sentence) | **yes** | **yes** | yes — `inside_free_look` (pre-existing, revision 1) |
| care_ext_cover_release_return | care_free_look (plural-lines sentence) | **yes** | **yes** | **no** — `care_free_look`'s only eligibility entry is `inside_free_look`, whose condition is the *other* sentence |

**Neither of the two new declarations retires a gate.** That was the specific risk named for this
round and it is not realised.

The two pre-existing declarations that *do* quote an eligibility condition were re-examined rather
than assumed, because retiring a gate is exactly the failure mode in question:

- `one_claim_per_reference` is a `dedup` gate. Its replacement is not a removal but a narrowing —
  "no more than one claim is filed against the same benefit under that reference on the policy" —
  so a duplicate of the *same* head under the same reference is still refused. The gate's work
  survives in a weaker but still-binding form. (Observation **O9** — the structured
  `dedup_contract` block remains untouched in the base copy — is unchanged.)
- `inside_free_look` is a `time` gate. Its replacement legislates the whole domain the gate divided
  (inside the period, outside it, and the claim-filed case), so no situation is left ungoverned.
  The gate's work survives as the first and third tiers of the share ladder.

**O8 is closed.** The base sentence that left `source_entry_id` unentailed —
"A returned premium is raised against the premium lines that collected it, so a policy with several
premium lines returns as several refund lines." — is now named verbatim in
`care_ext_cover_release_return.overwrite[1].superseded_clause` and replaced by a sentence that names
one line and excludes three kinds. The plural reading no longer stands beside a single-line tool.
The entailment this buys is tested on task 1's own world in `1.md` revision_2.

**A ninth divergence I missed in revision 1 is now declared.** The new
`care_ext_declared_cost_correction` overwrite supersedes base `care_club_and_bundle_interaction`'s
"Cover bought alongside an air booking or a vacation package is rated on the same declared trip cost
as that booking, and the two are corrected together where the booking's price changes." — a
divergence task 1 genuinely reaches, because the correction computes 8806.67 against a package
standing at `package_price_usd 11400.00`. I did not check `care_club_and_bundle_interaction` in
revision 1 because it was not in `base_policy_refs`, which was a hole in my sweep: a base policy can
govern a quantity without being cited. This revision's sweep was run over **all thirteen** base
policies against each extended policy rather than over the declared refs alone. Result: no further
undeclared divergence was found. In particular —
`care_underwriting` ("the declared trip cost is at or below the plan's ceiling" — 8806.67 ≤
20000.00, agrees), `care_coverage_term` ("cancellation cover runs from the moment the certificate is
issued" — agrees with, and is the stated reason for, the extended cover-bought convention),
`care_premium_rating` ("the policy fee … is never returned" — agrees with the extended exclusion of
the fee), `care_agg_multi_holding` (one live policy in each task), `care_claim_assessment` ("the
decision is the insurer's alone" — no gold write re-decides) and `care_midterm_cancellation` (every
clause agrees, as in revision 1) all bear without conflicting.

**The seven left undeclared are still undeclared, and I re-tested each on the round-2 worlds rather
than accepting the argument.** Task 0's world is byte-identical, so O1 and O2 are unchanged by
construction; O3–O7 were re-evaluated against the moved task-1 world:

| id | re-tested on the round-2 world | still unreached? | the tier that keeps it unreached |
| --- | --- | --- | --- |
| O1 | task 0 | yes | every carrier item counted postdates the settlement it answers (2026-08-28 / 08-30 / 09-03 against a settlement of 2026-08-12) |
| O2 | task 0 | yes | `head_settled = travel_delay`, so `benefit_limit` takes tier 1 (1000.00) and the fall-through is never evaluated |
| O3 | task 1 | yes | `journey_prepaid = 8806.67` against `P('max_trip_cost_usd') = 20000.00`; `MN` does not bind |
| O4 | task 1 | yes | `rated_premium 778.51 > collected_premium 654.16`, so `MX(·, 0)` does not clip |
| O5 | task 1 | yes | `age_loading_lines = 1` **and** `destination_loading_lines = 1`, so `rate_applied` takes tier 1 |
| O6 | task 1 | yes | `days_since_issue 22 > free_look_days 14` and `claims_filed = 0`, so the share ladder takes tier 1 |
| O7 | task 1 | yes | `trip_start_date 2026-10-10` is after `frozen_time 2026-09-21` |

The moved seed (`flight_upgrade` → `excursion_component`) touches none of the seven: it changes
`pkg_flight_components` from 0.00 to 0.00 (the round-1 value was already 0.00, because
`flight_upgrade` is not `flight_component`) and leaves `pkg_components` at 1100.00, so no ladder
anywhere changes tier. Verified by recomputation, not by inspection of the reworker's note.

**My standing position on the seven is unchanged and is not an endorsement.** Each is a real
undeclared divergence between a base sentence and the extended treatment; each is recorded as an
observation only because its consequence cannot be demonstrated on either of the two worlds this
difficulty actually contains. The reworker's decision to leave them undeclared rests on exactly that
contingency, and the contingency is a property of two seeds, not of the charter. O8 became
demonstrable the moment a second auditor looked at it from the render side; O3–O7 would each become
demonstrable under a seed this difficulty does not happen to hold (a package above the plan ceiling;
a correction that lowers the declared cost; a record with an age loading and no destination loading;
a cancellation inside the free-look window; a cancellation after departure). I record that as the
standing risk rather than as a red light, because a red light requires a consequence on a world that
exists.

### factor_ladders (revision 2)

Re-derived. The factor structure is **unchanged in every respect**: the same 27 factors across six
policies (4, 5, 4 / 6, 4, 4), the same effect labels, the same `decides` bindings, the same disjoint
binding sets, the same tier counts (3 everywhere except the two four-tier ladders
`benefit_limit_by_head` and `deductible_withheld_rule`), the same multi-source and
`cross_difficulty` distribution, the same per-policy counts of ≥ 2 `parameter` and ≥ 1 `method`, and
the same per-task coverage of at least one multi-source and at least one cross-difficulty factor.
Every tier's value or method is still drawn from the charter. **F1** (the two arguable `method`
labels) is unchanged and remains an observation.

The one factor whose *world* moved is `flights_bought_apart`: its tier-1 condition "an air booking
departing on the first date of the journey stands ticketed and the holiday's ledger carries no
flight component" now holds by plain inspection rather than against a distractor. The structural
requirement is untouched (the ladder still has three disjoint tiers, all stated in the rule); what
changed is the *evidential* difficulty, which is a fact about one world and is judged in `1.md`
revision_2 under `factor_weight`.

### findings (revision 2)

| id | status after the rework | note |
| --- | --- | --- |
| **O8** | **CLOSED** | declared verbatim on both sides; entailment tested per task in `1.md` |
| R1 | unchanged — observation | the same six ladder paraphrases; neither fixed nor worsened |
| R2, R3 | unchanged — observation | task 0's policies did not move |
| R4 | unchanged — observation | still unreached on the round-2 world |
| P1 | unchanged — observation | |
| O1, O2 | unchanged — observation | task 0's world byte-identical |
| O3–O7 | unchanged — observation, **re-tested** | each re-evaluated on the moved world; each still unreached |
| O9 | unchanged — observation | the base `dedup_contract` block still stands |
| F1 | unchanged — observation | |
| **N1** | **new — observation** | the replacement for the plural-lines sentence is contradicted at face value by a seeded row: see `1.md` revision_2, finding 1-D |
| **N2** | **new — observation** | the seed change removed the near-miss the round-1 worklog nominated for `flights_bought_apart`: see `1.md` revision_2, finding 1-E |
| **N3** | **new — observation** | my revision-1 override sweep ran over `base_policy_refs` rather than over all base policies, which is why the `care_club_and_bundle_interaction` divergence was missed; recorded against my own work, and the sweep is widened in this revision |

**No charter-global `SOURCE-POLICY RED` in revision 2.**

## closing_checklist (revision 2)

Written after both tasks reached PASS on all four relationships in this round; post-reveal by
construction, and kept below revision 2's charter-global section, which is pre-reveal.

- **Every revision-1 item is accounted for.** Revision 1 raised **no RED**, so there is no closed-RED
  list to verify; the item that sent the charter back was observation **O8 / finding 1-A**. It is
  **closed**, on the entailment standard rather than the agreement standard: the new sentence names
  `charge_category = base_premium` positively and strikes out the loading lines, the issue-fee line
  and any line raised to correct another line, leaving exactly one of the five (six at the return's
  handling time) candidate rows, with the deciding field visible on the transcript. Derived by
  elimination before gold was consulted. Revision 1's other seventeen observations are re-tested
  above; none has worsened, one (O1) is answered by a better argument than mine, and one (0-B) is
  answered and accepted.
- **No new defect of the four relationships.** Three new observations are recorded — **N1 / 1-D**
  (the replacement sentence is unqualified where the base sentence it retired was general, and a
  seeded refund row contradicts it at face value), **N2 / 1-E** (the seed change removed the record
  that made `flights_bought_apart`'s tier condition a judgement), **N3** (my own revision-1 sweep
  ran over `base_policy_refs` instead of over all base policies) — plus **1-F** (two proof fields
  not brought forward with the rework). None produces a second defensible value, a missing solution,
  a real-world wait, an unmet-prerequisite failure or a decorative factor on either world.
- **Nothing regressed.** All six `expected` (130.00 / 2335.45 / 390.00 and 8806.67 / 108.36 /
  127.99), all six `baseline_result` (100.00 / 1772.73 / 700.00 and 10300.00 / 119.39 / 777.52) and
  all twenty-seven factor-sensitivity figures were **recomputed** on the round-2 charter and the
  round-2 worlds and are unchanged; every gold argument, owner and order is unchanged; both problem
  trees, their kinds, gates, forms, conditions and flip figures are unchanged; the base copy is
  still verbatim identical to `blueprint/products/care.yaml`.
- **The added sentences did not break what they sit beside.** Both touched `baseline.rule` blocks
  are still verbatim subsets of their rules and still yield 119.39 and 777.52; all eight ladders in
  the two touched policies still have every tier verbatim in the rule and still select the same
  tier; the fall-back limb inside each new sentence is reachable in principle and unreached here;
  the two original declarations are still verbatim on both sides.
- **The two new declarations are sound.** `superseded_clause` verbatim in the named base rule and
  `replaced_by` verbatim in the declaring extended rule, for all four declarations; neither new one
  quotes a base eligibility condition, so no gate was silently retired. The two pre-existing ones
  that do quote an eligibility condition were re-examined: each replacement legislates the domain
  its gate divided, so neither gate's work was dropped.
- **Scope, trees and tools.** Task scopes still pairwise disjoint and jointly complete over the six
  extended policies; each tree still has 2 prerequisite problems, ≥ 1 `value_input` edge (1 and 2),
  an `owner=user` write, and no cycle; the difficulty graph is still a DAG; `task_tools.py` is
  unchanged by hash, so the six independently generated uuid8s stand.
- **Computations and factors.** Six computations, six self-sufficient baselines each giving a
  definite number different from gold, 27 factors (4+5+4 / 6+4+4), each policy within 4–6 with ≥ 2
  `parameter` and ≥ 1 `method`, every ladder ≥ 3 disjoint tiers stated in its own rule, multi-source
  and cross-difficulty coverage unchanged, and every one of the 27 re-substituted and still moving
  the scored value.
- **Instantiation gates re-run on the round-2 form** from the repository root with
  `DIFF=env/online_travel_agency/tasks/travel_protection_desk`: `EXTENDED OK`,
  `TASK TOOL CONTRACT OK`, `REPLAY OK`, `SOLVABILITY OK`, `COMPUTE OK` (branches 59/53, steps 15/16,
  suite means 56.00 and 15.50, `history_rows_max` 15), `GROUNDING OK`, `SCOPE OK`. This audit edited
  no artifact.

**Difficulty verdict (revision 2): PASS.** Task 0 PASS on all four relationships, task 1 PASS on all
four. The item that sent the charter back is closed at the charter level and on task 1's own world.
The standing risk I will not soften: the seven divergences left undeclared are undeclared because of
a contingency about two seeds, not because base and extended agree in general, and one seed moved
this round.
