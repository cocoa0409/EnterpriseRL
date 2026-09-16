# Policy-task audit — air_ticketing_desk / charter-global

## charter_global_frozen

- Freeze time: 2026-09-16 (session clock), written before any GT field of either task was read.
- Auditor: independent policy-task auditor (erl-task-policy-audit), not the author of these artifacts.
- Frozen inputs and hashes:
  - `env/online_travel_agency/tasks/air_ticketing_desk/air.extended.yaml` sha256 `95e3b19c06bb09e5bb3c2730254bd257c15c52465856b1db7796224ea5d8ade3`
  - `env/online_travel_agency/tasks/air_ticketing_desk/task_tools.py` sha256 `93dfab46c2168e5c5337a057305d1174b301d69fb38a6dfabecbdfd15d5b4390`
  - `env/online_travel_agency/blueprint/{blueprint.yaml,db_schema.json,share_tools.py,products/*.yaml}`
- Fields permitted here: the whole extended charter (base section + `extended_policies`), the tool module, the
  blueprint. Fields explicitly masked while this section was written: every task file's `evaluation_criteria`,
  `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`,
  `prerequisite_closure`, `db_closure*`. Nothing in this section is derived from a revealed GT field.
- Entry condition: the coordinator supplied the verbatim output of `check_extended`, `check_task_tools`,
  `replay_tasks`, `check_solvability`, `check_compute`, `check_grounding` and `check_cross_fire`, all green,
  together with the two masked views and their sha256 (`0.json` view `029234ec…`, `1.json` view `3b4c0b60…`).
  The entry condition is complete. `check_traceability.py` is correctly deferred to the KB stage.

### policy_conflict_scan

Scope of the charter: 15 base policies (`policies:`) + 6 extended policies. The base section of
`air.extended.yaml` was compared against `blueprint/products/air.yaml` by parsing both and diffing key by key:
`extra keys ['extended_policies'], missing [], differing keys []`. The base copy is therefore semantically
verbatim (the only textual difference is YAML line re-wrapping). No base sentence has been rewritten.

Subjects, triggers and terminal states across the six extended policies:

| policy | trigger | subject | computes | target_tool | owner |
| --- | --- | --- | --- | --- | --- |
| air_ext_no_show_penalty | state_due | air_penalty_charge | penalty_amount_usd | withhold_no_show_penalty_8882d2a1 | agent |
| air_ext_unflown_tax_return | state_due | air_refund_payout | payout_amount_usd | return_unflown_taxes_e343d675 | agent |
| air_ext_cancelled_ticket_credit | state_due | air_credit_issue | voucher_value_usd | issue_travel_credit_599fe29f | agent |
| air_ext_credit_release | on_request | air_credit_redeem | credit_applied_usd | apply_travel_credit_e74c9b2a | user |
| air_ext_outstanding_service_charge | state_due | air_fare_charge | service_charge_usd | settle_agency_service_charge_b626effa | user |
| air_ext_cabin_upgrade_copay | on_request | air_ancillary_charge | upgrade_copay_usd | charge_cabin_upgrade_d9ccb8ec | agent |

No two extended policies share a `(subject, computes)` pair and no two share a target tool. Cross-category read
boundaries are declared per policy (`cross_category`) and each declared category is actually read by that
policy's `compute` (club/care/biz via CPARAM/CFIELD/XSUM/XCOUNT); no policy reads a category it does not declare.

Inherited base eligibility gates that bear on the extended writes, and where they are satisfied:
`air_refund_settlement.refund_stage_reached` (applies_to `air_refund_payout`, status in cancelled/refund_pending/
refunded), `air_credit_validity.cancelled_before_issue` (applies_to `air_credit_issue`, same statuses),
`air_agg_credit_pooling.credit_still_valid` (applies_to `air_credit_redeem`), `air_baggage_fee.
booking_open_for_extras` (applies_to `air_ancillary_charge`, status held or ticketed).
`air_cancel_refund.refund_review_approved` applies only to `air_refund_open` and therefore does **not** gate
`air_ext_unflown_tax_return`; no task needs an `air_service_requests` row for it.

Task scopes (derived from the two masked worlds and the policy trees, not from `charter_scope`):
task 0 = {air_ext_credit_release, air_ext_cancelled_ticket_credit, air_ext_no_show_penalty,
air_ext_unflown_tax_return}; task 1 = {air_ext_cabin_upgrade_copay, air_ext_outstanding_service_charge}.
The two sets are pairwise disjoint and together cover all six extended policies.

Conflicts found in this scan are recorded in `### override_declarations` and `### findings` below.

### rule_compute_equivalence

Machine sweep of all six policies (`compute_basis` key → verbatim substring of that policy's own `rule`;
every `baseline.rule` sentence → verbatim substring of the `rule`; every `factors[].ladder[].when` → present in
the `rule`):

- Every `compute_basis` value is a verbatim substring of its policy's `rule`. No `compute_basis` key names a
  binding that does not exist.
- Every sentence of every `baseline.rule` is a verbatim sentence of the corresponding `rule`.
- Every ladder tier is stated in the `rule`; the sweep flagged 12 tiers whose `when` text is an expanded or
  elided paraphrase of the rule sentence (e.g. rule "and where the tier bonus is twenty-five percent or more…"
  vs ladder "the traveller's club tier carries a tier bonus of twenty-five percent or more…"). Each was checked
  by hand and is the same tier with the same boundary; no tier lives only in `compute`, and no branch of a
  `decides` binding lacks a tier in the rule.
- Gaps found (each recorded in `### findings`): four compute bindings carry no `compute_basis` entry
  (`brand_penalty`, `travellers_ticketed` in four policies, `brand_copay`); one history window is invented by
  `compute` with no basis in the rule (`air_ext_unflown_tax_return.change_line_count`, `within_months=12`, while
  the rule says only "at least one voluntary change line stands on it"); one acting base is invented by `compute`
  (`air_ext_cabin_upgrade_copay.covered_travellers`, threshold `P('agency_service_fee_usd') * travellers_ticketed`,
  stated nowhere in the rule); one rule sentence promises a movement no tool performs and no table records
  (`air_ext_cabin_upgrade_copay`: "the rest is billed to the company").
- `RND` is specified in every rule as "rounded half away from zero to two decimal places". The evaluator's `RND`
  is Python `round`, i.e. round-half-to-even. Recorded as an observation; no value in either task's world falls on
  a half-cent tie, so no consequence is demonstrable.

### action_binding_and_uuids

Each `(target_tool, computes)` pair is claimed by exactly one policy (table above). Each policy's subject, its
`base_policy_refs`, its target tool and that tool's docstring admit one business reading of what is written; no
tool adds a confirmation, review, wait or procedure of its own.

uuid8 suffixes, read one by one out of `task_tools.py`:
`8882d2a1`, `e343d675`, `599fe29f`, `e74c9b2a`, `b626effa`, `d9ccb8ec`.
All six are distinct, none is a prefix or tail variant of another, none carries a sequence number or a shared
prefix, and none looks batch-derived. Each is frozen into its function name and into the `resolved_by` of the
edge that names it.

Docstring sequence check: no docstring contains before / after / first / then / next, no docstring names another
tool, and no docstring states a position in a sequence. One borderline case, recorded as an observation:
`apply_travel_credit_e74c9b2a`'s Args say the voucher code and `source_event_id` are "read from the confirmation
that minted the voucher", which implies a prior act without naming a tool or an ordering word.

### prerequisite_graph

Four edges, all `form: state`, all `kind: value_input`, no `fallback_reason` (correctly absent on state-form
edges). Machine check of every edge:

| blocked policy | problem | gate | gate is a real binding | resolved_by == dep target_tool | policy_source verbatim in own rule | sentence restated in dep rule |
| --- | --- | --- | --- | --- | --- | --- |
| air_ext_cancelled_ticket_credit | air_ext_no_show_penalty | penalty_lines | yes | yes | yes | no |
| air_ext_cancelled_ticket_credit | air_ext_unflown_tax_return | payout_lines | yes | yes | yes | no |
| air_ext_credit_release | air_ext_cancelled_ticket_credit | standing_credit | yes | yes | yes | no |
| air_ext_cabin_upgrade_copay | air_ext_outstanding_service_charge | covered_travellers | yes | yes | yes | no |

Every policy has `prerequisite` filled in (`[]` on the four roots of no edge). Every `problem` points at another
**extended** policy id in this file, never at a base policy and never at itself. The graph
`no_show → credit`, `tax → credit`, `credit → release`, `service → upgrade` is acyclic. No blocked rule contains
the depended-on policy's tool name or id. `kind=value_input` matches `gate` in all four cases: each gate is a
binding whose value the depended-on write moves (`penalty_lines` 0 → the sum withheld, `payout_lines` 0 → minus
the sum returned, `standing_credit` 0 → the voucher value, `covered_travellers` the covered count → every
traveller ticketed). No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world")
appears anywhere in the four `prerequisite` blocks.

One `condition` is not the state its own sentence names, recorded in `### findings` as an observation:
`air_ext_cabin_upgrade_copay`'s condition reads "the agency service lines standing on the booking come to at
least **the fare brand's own service fee** taken for every traveller ticketed on it", while the sentence it
quotes says "the agency service charge **owed** for every traveller ticketed on it" — and under
`air_ext_outstanding_service_charge` that owed charge is taken at the corporate programme's unit, not the brand's.

### prerequisite_sentences

Four-point test, edge by edge.

1. air_ext_cancelled_ticket_credit ← air_ext_no_show_penalty.
   *"The value placed on a travel credit voucher is settled only after the booking's ledger carries the penalty
   entry owed for every traveller recorded as not having flown, and that entry is taken off the fare, tax and
   service lines standing on the booking."*
   Ordering connective: "only after". Form: state — "the booking's ledger carries the penalty entry owed for
   every traveller recorded as not having flown" is a record-visible state in the words the ledger uses, with no
   performer and no action. No tool name, no policy id, no snake_case token, no row id. Strength: the condition
   ("a penalty line for the travellers who did not fly stands on the booking's ledger at the moment the voucher
   value is worked out") is exactly that state. Exactly one write of this difficulty brings it about:
   `withhold_no_show_penalty_8882d2a1` is the only tool in the module that creates an `air_penalty_charge` row.
   Derivation, single reading: the sentence names a penalty entry on the ledger; the records show no
   `air_penalty_charge` row; `air_ext_no_show_penalty`'s own rule is the only rule in the charter that says what
   a no-show penalty entry is and how it is measured; therefore its write must land first.
2. air_ext_cancelled_ticket_credit ← air_ext_unflown_tax_return.
   *"Before that value is worked out the booking's ledger must already carry the payout entry owed for the
   carrier-imposed taxes on an unflown ticket, and whatever that entry has returned to the form of payment used
   is taken off as well."*
   Connective "Before"; state form; no tool, id or token; condition matches. `return_unflown_taxes_e343d675` is
   the only tool creating an `air_refund_payout` row. Single reading, as above.
3. air_ext_credit_release ← air_ext_cancelled_ticket_credit.
   *"Value is taken off a traveller's credit only once a voucher carrying that value stands on the booking whose
   cancellation produced it."*
   Connective "only once"; state form; condition matches. `issue_travel_credit_599fe29f` is the only tool
   creating an `air_credit_issue` row. Single reading.
4. air_ext_cabin_upgrade_copay ← air_ext_outstanding_service_charge.
   *"The co-payment for moving into a higher cabin is worked out only after the booking's lines carry the agency
   service charge owed for every traveller ticketed on it, and until that charge is complete only the travellers
   whose tickets the standing lines already cover are counted into the move."*
   Connective "only after"; state form; no tool, id or token. `settle_agency_service_charge_b626effa` is the only
   tool creating an `air_fare_charge` row with `charge_category='agency_service_fee'`. Single reading. The
   `condition` operationalises "the charge owed" as the brand's own fee times travellers — see the observation
   above; the sentence itself passes the four-point test.

No blocked rule carries a second wording of its dependency, and no depended-on rule restates the blocked policy's
sentence (machine-checked, table in `### prerequisite_graph`).

Cross-problem orders stated in **base** rules that ground no declared edge (each an observation, since every task
tree rests on the extended rule's own prerequisite sentence rather than on these):
- `air_credit_validity`: "A travel credit is issued for the value the cancelled ticket still carried **after any
  penalty has been withheld**."
- `air_penalty`: "the return is treated as cancelled on the brand's own terms **once** the no-show penalty has
  been withheld."
- `air_ticketing`: "Ticketing collects the fare, the taxes and carrier fees, and the agency service fee together;
  a partly collected booking is never ticketed." (This one is not merely an order — see finding F.)

### override_declarations

Sentence-by-sentence sweep of every extended policy against each `base_policy_refs` entry, at the granularity of
"the quantity that ultimately gets scored". Findings only; each affected task's file demonstrates the cost.

| extended policy | `overwrite` | base sentences it follows | base sentences it handles differently | declared? |
| --- | --- | --- | --- | --- |
| air_ext_no_show_penalty | `[]` | "A traveller who neither flies nor cancels … is recorded as a no-show"; "A penalty is never withheld where the traveller could not travel because the airline did not operate the flight"; "The infant share of a fare and the child discount are applied before the penalty is measured" | `air_penalty.formula` `min(no_show_penalty_usd, amount_paid_usd)` → extended multiplies the brand penalty by travellers counted, by a relief share, subtracts a rework offset and applies a club softening; "the penalty is limited to that value" where *that value* is `amount_paid_usd` → extended's ceiling is `SUM(air_fare_charge)+SUM(air_ancillary_charge)`; `air_club_benefit_interaction` "the fare brand's own rates apply to everything the club does not cover" → extended lets a club tier halve or three-quarter the penalty | **no** |
| air_ext_unflown_tax_return | one entry: `air_refund_settlement` "Each payout line is raised against the original fare line it reverses…" | "A payout line is raised only while the booking record stands at cancelled, refund pending or refunded"; `air_cancel_refund` "Taxes and carrier fees that the airline itself refunds are returned even on a non-refundable brand, and the agency service fee is not" | `air_refund_settlement` "A lodged claim settles in the form the fare brand prescribes and in no other form: money to the card, or value on a voucher, never both and never a mixture" — this policy pays money to the card on a booking whose brand refund form is a voucher and on which air_ext_cancelled_ticket_credit then raises the voucher | partly (the lump-sum clause is declared; the never-both clause is not) |
| air_ext_cancelled_ticket_credit | `[]` | `air_credit_validity` "carries an expiry set by the credit validity term of the fare brand that produced it"; "issued in the name of the traveller the ticket was issued to"; "A voucher is issued only while the booking record stands at cancelled, refund pending or refunded" | `air_credit_validity` "A travel credit is issued **for the value the cancelled ticket still carried after any penalty has been withheld**" → extended additionally deducts a share of the service lines, scales by a promptness share, by a brand credit share and by a membership uplift; `air_club_benefit_interaction` "the club benefit is not converted into value" → `membership_credit_uplift` converts a club tier into a percentage uplift of voucher value | **no** |
| air_ext_credit_release | `[]` | `air_agg_credit_pooling` "the movement is the traveller's own"; "A travel credit is applied to a new itinerary only when frozen time is not after … the credit validity term" | `air_credit_validity` "A voucher **that has lapsed** may be reissued once onto a fresh voucher against the brand's reissue fee" → extended's baseline takes the brand's reissue fee off **every** release, lapsed or not; `air_agg_credit_pooling` "Travel credits … form one pool in that traveller's name" → extended reads only the vouchers raised against one booking; "Where the pooled value exceeds the price of the new itinerary the remainder stays on the last voucher touched" and "Where the pooled value falls short the difference is collected in the original form of payment" → extended never compares the release with the new itinerary's price | **no** |
| air_ext_outstanding_service_charge | `[]` | `air_biz_exclusion` "a booking that carries a corporate programme reference is priced entirely on the programme's negotiated terms" | `air_service_fee.formula` `agency_service_fee_usd * passenger_count` → extended charges `unit_fee * travellers_uncovered`; `air_service_fee` "charged once per traveller on the booking **at the moment the ticket is issued**" → extended settles it on an already-ticketed booking; `air_service_fee` "the conversion markup **of the fare brand held** is added" → extended applies `K('domestic_markup_pct')=1.0` when the contracting company is US-registered, which is neither the brand's markup nor the programme's | **no** |
| air_ext_cabin_upgrade_copay | `[]` | `air_seat_and_cabin_extras` "sold only on a brand that allows it"; "never converts the booking to the higher cabin's brand terms" | `air_seat_and_cabin_extras` "at the brand's co-payment **per traveller per segment**" → extended then applies a programme discount, a lead-time share (including a 1.15 **loading**), an extras credit, an approval share and a traveller share; `air_baggage_fee` "A bag line already charged is refunded in full when the traveller cancels the whole itinerary inside the void window, and is **otherwise refunded only where the flight itself did not operate**" → `bought_extras_credit` credits standing checked-bag lines against the co-payment on a flown-nothing, uncancelled booking | **no** |

Five of the six extended policies carry `overwrite: []` while changing the scored quantity the base policy's own
rule or formula fixes. The 0/1-multiplier and dropped-branch disguises were looked for specifically:
`air_ext_no_show_penalty.relief_share` can take the value `0.0` (an existence condition zeroing a penalty base
has already fixed) and `air_ext_cabin_upgrade_copay.discount_pct` collapses two of its three tiers to
`K('no_discount_pct')`; neither is declared.

### factor_ladders

| policy | factors | parameter / method | ladders ≥3 tiers | fall-through == baseline | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| air_ext_no_show_penalty | 4 | 3 / 1 | 4/4 | 3/4 — `fare_weighted_travellers`'s fall-through is "the base-fare lines standing on the booking" while its `baseline` is `travellers_ticketed` | yes (fare_weighted_travellers, airline_disruption_relief, member_penalty_softening) | club |
| air_ext_unflown_tax_return | 5 | 4 / 1 | 5/5 | 5/5 | yes (tax_basis_selection, protection_recovery_share, member_handling_charge) | care, club |
| air_ext_cancelled_ticket_credit | 5 | 4 / 1 | 5/5 | 5/5 | yes (service_line_carry, optional_extra_measure, membership_credit_uplift) | club |
| air_ext_credit_release | 5 | 4 / 1 | 5/5 | 5/5 | yes (lapse_horizon_release, member_reissue_treatment, protection_deductible_offset) | club, care |
| air_ext_outstanding_service_charge | 6 | 5 / 1 (the one `method` is mislabelled — see finding G) | 6/6 | 6/6 | yes (programme_fee_schedule, programme_volume_rebate, programme_transaction_overage) | biz |
| air_ext_cabin_upgrade_copay | 6 | 5 / 1 | 6/6 | 6/6 | yes (segments_moved_measure, programme_approval_share, programme_settlement_share) | biz |

Every tier is stated in the `rule` with its condition and its value or method, and implemented as a branch of the
`decides` binding; every `decides` names an input binding, never `result`; each factor's `bindings` sets are
disjoint from every other factor's within its policy. Every method tier names a rule the charter states.

Label honesty, factor by factor: `tax_basis_selection` (sum / largest×n / latest×n), `optional_extra_measure`
(sum / largest×n / nothing), `credit_idle_clock_anchor` (three date anchors), `segments_moved_measure` (a measure
taken from the ledger vs two fixed counts) and `member_penalty_softening` (two truncate-to-the-dollar treatments
vs carry-to-the-cent) each change how the quantity is computed, not merely which number enters it — honest
`method` labels. `programme_fee_schedule` does not: its three tiers substitute three scalar fees (5.50 / 29.00 /
the brand's `agency_service_fee_usd`) into the same `unit_fee × travellers_uncovered` product — see finding G.

Ladder disjointness: eleven ladders are nested rather than partitioned as stated (tier 1's condition is a strict
subset of tier 2's — e.g. `programme_volume_rebate` "reaches its volume rebate threshold" ⊂ "reaches half of that
threshold"), and are resolved only by reading the rule's "instead … and where …" cascade top-down, the order the
`compute` if-else chain also takes. Recorded as an observation: neither task's world falls inside any overlap
region, so no second value is derivable (checked tier by tier against both worlds).

### findings

**A — SOURCE-POLICY RED (charter-global): `air_ext_no_show_penalty` overrides `air_penalty` with `overwrite: []`.**
- Symptom: two clauses of the merged charter fix the same scored quantity — the sum withheld as a no-show penalty
  — and give different numbers.
- Root cause: the extended policy rewrote the base measurement (one brand penalty, capped at the booking's amount
  paid) into a per-traveller product with a relief share, a rework offset and a club softening, and declared no
  `overwrite` entry naming the base sentence or formula it replaces.
- Evidence: base `air_penalty.formula: no_show_penalty_charged_usd: min(no_show_penalty_usd, amount_paid_usd)`
  and base rule "the no-show penalty of the fare brand held is withheld from whatever value the ticket still
  carries" / "Where the value still on the ticket is smaller than the penalty, the penalty is limited to that
  value"; extended rule "taken once for every traveller ticketed on the booking" and
  `value_ceiling: SUM('air_booking_events','amount_usd', event_type='air_fare_charge') + SUM(… 'air_ancillary_charge')`;
  `air.extended.yaml` line 2112 `overwrite: []`.
- Demonstrated consequence: task 0 — see `0.md`.
- Affected artifact: `env/online_travel_agency/tasks/air_ticketing_desk/air.extended.yaml`,
  `extended_policies[air_ext_no_show_penalty].overwrite` / `.rule` / `.compute`.

**B — SOURCE-POLICY RED (charter-global): `air_ext_outstanding_service_charge` overrides `air_service_fee` with
`overwrite: []`.**
- Symptom: three clauses fix the agency service charge owed on one booking and give three different numbers.
- Root cause: the extended policy replaced the base multiplier (`passenger_count`) with the uncovered-traveller
  count, replaced the unit with the corporate programme's booking fee, moved the charge off the ticketing moment,
  and replaced the brand's conversion markup with a constant `domestic_markup_pct`, declaring none of it.
- Evidence: base `air_service_fee.formula: agency_service_fee_charged_usd: agency_service_fee_usd *
  passenger_count`; base rule "charged once per traveller on the booking at the moment the ticket is issued" and
  "the conversion markup of the fare brand held is added to the converted total"; extended
  `travellers_uncovered: MX(0, travellers_ticketed - service_line_count)`,
  `unit_fee: programme_online_fee if … else (programme_offline_fee if … else P('agency_service_fee_usd'))`,
  `markup_pct: P('currency_conversion_markup_pct') if … else (K('domestic_markup_pct') if … else …)`;
  `overwrite: []`.
- Demonstrated consequence: task 1 — see `1.md`.
- Affected artifact: `extended_policies[air_ext_outstanding_service_charge]`.

**C — SOURCE-POLICY RED (charter-global): `air_ext_cabin_upgrade_copay` overrides `air_seat_and_cabin_extras` and
`air_baggage_fee` with `overwrite: []`.**
- Symptom: the base charter fixes the upgrade co-payment as the brand's co-payment per traveller per segment and
  forbids refunding a standing bag line except on two named events; the extended policy multiplies that base by
  five further shares and credits the bag line against it.
- Root cause: undeclared override of both cited base policies.
- Evidence: base `air_seat_and_cabin_extras` "An upgrade into a higher cabin is sold only on a brand that allows
  it, at the brand's co-payment per traveller per segment"; base `air_baggage_fee` "A bag line already charged is
  refunded in full when the traveller cancels the whole itinerary inside the void window, and is otherwise
  refunded only where the flight itself did not operate"; extended
  `result: RND(MX(0.0, after_extras * approval_share * traveller_share), 2)` with
  `extras_credit: (bag_lines * K('credit_full')) if …`; `overwrite: []`.
- Demonstrated consequence: task 1 — see `1.md`.
- Affected artifact: `extended_policies[air_ext_cabin_upgrade_copay]`.

**D — SOURCE-POLICY RED (charter-global): `air_ext_credit_release` overrides `air_credit_validity` and
`air_agg_credit_pooling` with `overwrite: []`.**
- Symptom: the base charter makes the brand's reissue fee payable only on reissuing a **lapsed** voucher and
  measures the value applied against the new itinerary's price; the extended policy takes the reissue fee off
  every release and never looks at the new itinerary's price.
- Root cause: undeclared override.
- Evidence: base `air_credit_validity` "A voucher that has lapsed may be reissued once onto a fresh voucher
  against the brand's reissue fee"; base `air_agg_credit_pooling` "Travel credits issued from a traveller's
  cancelled bookings form one pool in that traveller's name" / "Where the pooled value exceeds the price of the
  new itinerary the remainder stays on the last voucher touched" / "Where the pooled value falls short the
  difference is collected in the original form of payment"; extended rule "The brand's reissue fee is taken off
  the gross release in full" and `baseline.params` containing `credit_reissue_fee_usd`; `overwrite: []`.
- Demonstrated consequence: task 0 — see `0.md`.
- Affected artifact: `extended_policies[air_ext_credit_release]`.

**E — SOURCE-POLICY RED (charter-global): `air_ext_cancelled_ticket_credit` overrides `air_credit_validity` and
`air_club_benefit_interaction` with `overwrite: []`.**
- Symptom: base fixes the voucher value as "the value the cancelled ticket still carried after any penalty has
  been withheld"; the extended policy reduces it by a service-line deduction, a promptness share and a brand
  credit share, and raises it by a club uplift the base charter says the club never gives.
- Root cause: undeclared override.
- Evidence: base `air_credit_validity` first sentence; base `air_club_benefit_interaction` "the club tier held on
  the day the ticket is issued decides whether the agency service fee is waived and whether the first checked bag
  is carried free, and the fare brand's own rates apply to everything the club does not cover" and "A club benefit
  and a fare-brand inclusion never stack into a payment to the traveller … the club benefit is not converted into
  value"; extended `result: RND(subtotal * lead_share * brand_share * (1 + uplift_pct / 100), 2)`;
  `overwrite: []`. `air_club_benefit_interaction` is not even listed in this policy's `base_policy_refs`.
- Demonstrated consequence: task 0 — see `0.md`.
- Affected artifact: `extended_policies[air_ext_cancelled_ticket_credit]`.

**F — SOURCE-POLICY RED (charter-global, bites task 1): the state the task-1 tree needs is one base forbids.**
- Symptom: `air_ext_outstanding_service_charge` exists to settle an agency service charge still outstanding on a
  booking; base `air_ticketing` says a booking in that condition can never have been ticketed.
- Root cause: the extended policy's trigger state contradicts an inherited base provision that no `overwrite`
  touches.
- Evidence: base `air_ticketing` "Ticketing collects the fare, the taxes and carrier fees, and the agency service
  fee together; a partly collected booking is never ticketed"; extended rule "where the booking's lines cover
  fewer travellers than are ticketed on it the charge is owed for the travellers the lines do not yet cover";
  `overwrite: []`.
- Demonstrated consequence: task 1 — see `1.md`.
- Affected artifact: `extended_policies[air_ext_outstanding_service_charge].rule`, and the world it is
  instantiated on.

**G — SOURCE-FACTOR RED (charter-global): `air_ext_outstanding_service_charge` has no honest `method` factor.**
- Symptom: the policy declares one `method` factor; its tiers change no algorithm.
- Root cause: `programme_fee_schedule` is labelled `method`, but each of its three tiers only substitutes a
  different scalar fee into the same product.
- Evidence: `factors[programme_fee_schedule].effect: method`, `decides: unit_fee`, tiers "the unit is taken from
  the programme's own online booking fee" (5.50) / "…offline booking fee" (29.00) / "…the fare brand's own agency
  service fee" (14.95, `P('agency_service_fee_usd')`); `compute` uses the selected scalar unchanged in
  `gross_charge: unit_fee * travellers_uncovered`. The rubric's own test — "a factor labelled `method` whose tiers
  only substitute a different number into the same formula (a rate, a fee, a threshold)" — is met exactly.
- Demonstrated consequence: striking the mislabelled factor leaves the policy with 5 `parameter` factors and 0
  `method` factors, below the floor of 1; and task 1 is then a task whose declared method variation is a fee
  lookup. Numbers in `1.md`.
- Affected artifact: `extended_policies[air_ext_outstanding_service_charge].factors[0].effect`.

**H — observation (charter-global): one factor's fall-through tier is not its baseline.**
`air_ext_no_show_penalty.factors[fare_weighted_travellers]` declares `baseline: {travellers_counted:
travellers_ticketed}` — which is what `baseline.rule` states ("The travellers counted are the travellers ticketed
on the booking") — while its ladder's "otherwise" tier is "the base-fare lines standing on the booking". A reader
of the computation document and a reader of the factor document therefore fall through to different values. No
consequence is demonstrable on either task's world (task 0 sits on tier 1), so this is an observation.

**I — observation (charter-global): compute invents bases the rule does not state.**
(i) `air_ext_unflown_tax_return.change_line_count: COUNT('air_booking_events', within_months=12, …)` while the
rule says only "at least one voluntary change line stands on it" — a twelve-month window with no sentence behind
it. (ii) `air_ext_cabin_upgrade_copay.covered_travellers: travellers_ticketed if (service_lines >=
P('agency_service_fee_usd') * travellers_ticketed) else service_line_count` — the threshold
"the brand's own service fee times travellers ticketed" appears in no sentence of the rule, and is not the unit
the charge owed is taken at for a corporate booking. (iii) `air_ext_outstanding_service_charge.
programme_transactions: XSUM(… within_months=1 …)` while the rule says "counted in the current month"; a
`within_months=1` window is `0 <= MONTHS(posted, NOW) < 1`, which can reach into the previous calendar month.
(iv) four compute bindings carry no `compute_basis` entry: `brand_penalty`, `brand_copay`, and
`travellers_ticketed` in four policies. None of (i)–(iv) changes a value on either task's world.

**J — observation (charter-global): a rule sentence promises a movement nothing performs.**
`air_ext_cabin_upgrade_copay`: "only the long-terms traveller share is collected from the traveller **and the rest
is billed to the company** instead". `charge_cabin_upgrade_d9ccb8ec` posts one `air_ancillary_charge` line for
the collected share and touches no `biz_billing_entries` row; no tool in the module or in `share_tools.py` bills a
corporate programme. The rule makes a promise the charter cannot keep.

**K — observation (charter-global): base's "never both and never a mixture" versus the task-0 design.**
`air_refund_settlement` says "A lodged claim settles in the form the fare brand prescribes and in no other form:
money to the card, or value on a voucher, never both and never a mixture", and `air_ext_unflown_tax_return`'s
`overwrite` names only the per-line clause of that policy. Task 0's tree raises both a payout to the card and a
voucher on the same booking. The reconciling sentence is in another base policy — `air_cancel_refund`: "Taxes and
carrier fees that the airline itself refunds are returned even on a non-refundable brand, and the agency service
fee is not" — so the combination is defensible; but the two base sentences are left to fight in the merged text
with no `overwrite` entry naming the first.

**L — observation (charter-global): ladder nesting, rounding mode, and an Args hint.**
Eleven ladders are nested rather than partitioned as stated (see `### factor_ladders`); `RND` is round-half-even
while every rule says "half away from zero"; `apply_travel_credit_e74c9b2a`'s Args say the voucher code is "taken
from the confirmation that minted it", which implies a prior act without naming a tool. None has a consequence on
either task's world.

**M — observation (charter-global): `air_club_benefit_interaction` is cited where it is not used and not cited
where it is.** It is listed in `base_policy_refs` of `air_ext_outstanding_service_charge` and
`air_ext_cabin_upgrade_copay`, neither of which reads the club category at all, and is absent from the refs of
`air_ext_no_show_penalty`, `air_ext_cancelled_ticket_credit` and `air_ext_credit_release`, all three of which turn
a club tier into money.

## closing_checklist

Written after both tasks' `source_derivation_frozen` and `source_gt_comparison` were on disk. **This difficulty
does not close at the source layer**: policy self-consistency fails on both tasks and the factors relationship
fails on both, so the Step 4 sign-off cannot be given. What the checklist's items do and do not establish:

- **Audit files and revisions.** `0.md` and `1.md` correspond one-to-one with `tasks/0.json` and `tasks/1.json`;
  `_difficulty.md` sits alongside them. This is revision 1 — there is no earlier revision to preserve. Both
  comparison sections carry an explicit verdict; neither carries an unqualified PASS.
- **Coverage and exclusivity.** All six extended policies are covered: task 0 claims
  {air_ext_credit_release, air_ext_cancelled_ticket_credit, air_ext_no_show_penalty, air_ext_unflown_tax_return},
  task 1 claims {air_ext_cabin_upgrade_copay, air_ext_outstanding_service_charge}. The two scopes are pairwise
  disjoint in policies, in tools and in the cross-difficulty product they read (club + care against biz), and each
  scope spans its whole problem tree. The six task tools are closed over the two scopes and each carries an
  independently generated, frozen, unreused uuid8 (§`action_binding_and_uuids`). **Holds.**
- **Problem trees.** Task 0: 3 prerequisite problems, 3 `value_input` edges against a floor of 2, one problem
  resolved by an `owner=user` tool, no cycle. Task 1: 1 prerequisite problem, 1 `value_input` edge against a floor
  of 1, the prerequisite problem resolved by an `owner=user` tool, no cycle. The four `prerequisite` edges of the
  difficulty together form a DAG with no cross-task reference. Both trees were derived independently from the
  policy and the world and are isomorphic to the declared ones; every edge was shown to bear weight by
  recomputation. **Holds structurally** — but task 0 carries `SOURCE-CHAIN RED` (finding 0-3) because one edge's
  own proof sentence states a figure the world does not produce, and task 1's tree rests on an opening state base
  `air_ticketing` forbids (finding 1-3).
- **Computations, baselines and factors.** Six computations, 4 to 6 declared factors each (4/5/5/5/6/6), every
  ladder of at least three tiers stated in full in its rule, every baseline self-sufficient and giving a definite
  number different from gold (585.00, 44.90, 1459.21, 1360.76, 29.90, 977.50), and all 31 declared factors shown
  by recomputation to bear weight against an honest baseline. **Does not hold**: finding G leaves
  `air_ext_outstanding_service_charge` with 0 honest `method` factors; finding 0-4 shows task 0's three club
  ladders can be read off a seeded holding field and that no computation of task 0 carries a
  score-discriminating near-miss; finding 1-5 shows task 1's root computation carries no near-miss at all.
- **Unique solution.** Both tasks' scored solutions were reproduced item for item from the policy, the world and
  the tool contracts alone — every tool, owner, order, argument and terminal field (task 0: 97.00, 155.76,
  1827.36 with expiry 2027-09-16, 1703.31; task 1: 75.22, 1406.25). **Holds** in the sense that the intended
  reading is derivable and reaches gold; it is compromised only by the undeclared overrides of findings A–F,
  which leave a second derivable answer standing beside it in five of the six policies.
- **Gates on the final form.** The audited artifacts were not touched by this audit; the write domain was
  `env/online_travel_agency/audits/policy_task/air_ticketing_desk/` only. The hashes recorded in
  `## charter_global_frozen` and in each task file are the hashes of the artifacts as audited and are unchanged
  from the coordinator's entry-condition snapshot, so the instantiation-stage gates cited there are the gates of
  the final form. They remain green; as §`charter_global_frozen` notes, a green gate qualifies these artifacts for
  a manual audit and does not establish that the structured policy is self-consistent.

**Per-task verdicts.**

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | `SOURCE-POLICY RED` (0-1, 0-2) | `SOURCE-CHAIN RED` (0-3) | `SOURCE-FACTOR RED` (0-4) | PASS |
| 1 | `SOURCE-POLICY RED` (1-1, 1-2, 1-3) | PASS | `SOURCE-FACTOR RED` (1-4, 1-5) | PASS |

Charter-global red lights: A, B, C, D, E, F (`SOURCE-POLICY`) and G (`SOURCE-FACTOR`). Charter-global
observations: H, I, J, K, L, M.

---

## revision_2

Re-audit round 2. Revision 1 above is left exactly as written; nothing in it has been rewritten to
accommodate the reworked form.

### revision_2 / re-derivation grounds

Both shared inputs moved, so **every charter-global section of revision 1 was re-derived in full** rather than
carried forward by reference:

| artifact | round 1 | round 2 |
| --- | --- | --- |
| `air.extended.yaml` | `95e3b19c06bb09e5bb3c2730254bd257c15c52465856b1db7796224ea5d8ade3` | `70fe60e97de6bd809964e0cbb0f972f79e2e0e19dbc8c0848878c7dc13b9a9ad` |
| `task_tools.py` | `93dfab46c2168e5c5337a057305d1174b301d69fb38a6dfabecbdfd15d5b4390` | `1e103f68264da40816081e32a8e34658857f82e716dee30556e56102ad5223ab` |
| masked view `0.json` | `029234ec…` | `aaa9e960b9964f77f96c822f602c581cf04264fb700a4b11b679887468aad5e4` |
| masked view `1.json` | `3b4c0b60…` | `b0e8d9f96ab42dfed8285a55581103ed1a959cd6e1d2a622f71fec5a2881d2f9` |

All four re-verified on disk. Entry condition: the coordinator's re-run gate snapshot is complete and green on
the reworked form. **This round is not blind** — round 1's GT was already seen — and is recorded as such: it
verifies closure, non-regression and the absence of new defects, and does not present itself as an independent
blind derivation. Both tasks were nevertheless re-derived end to end from the new charter and the new seeds
before any round-2 GT field was read, and the per-task files record that.

The base section of `air.extended.yaml` is still semantically verbatim against
`blueprint/products/air.yaml` (parsed diff: `extra ['extended_policies']`, `missing []`, `differing keys []`).

### revision_2 / override_declarations, re-derived

`overwrite` has gone from 1 entry across the charter to **17**, and two base policies were added to lineages so
they could be declared (`air_club_benefit_interaction` to three policies, `air_ticketing` to
`air_ext_outstanding_service_charge`). Machine check of all 17, each on three tests — `superseded_clause`
verbatim in the named base policy's `rule`, `replaced_by` verbatim in the declaring extended policy's `rule`, and
`superseded_clause` not a base eligibility condition:

```
air_ext_no_show_penalty[0..2]            air_penalty ×2, air_club_benefit_interaction ×1   all three tests pass
air_ext_unflown_tax_return[0..1]         air_refund_settlement ×2                          all three tests pass
air_ext_cancelled_ticket_credit[0..1]    air_credit_validity ×1, air_club_benefit_… ×1     all three tests pass
air_ext_credit_release[0..4]             air_credit_validity ×1, air_agg_credit_pooling ×3, air_club_benefit_… ×1   all pass
air_ext_outstanding_service_charge[0..2] air_service_fee ×3                                all three tests pass
air_ext_cabin_upgrade_copay[0..1]        air_seat_and_cabin_extras ×1, air_baggage_fee ×1  all three tests pass
problems: 0
```

No `superseded_clause` touches any of the ten base eligibility conditions
(`refund_stage_reached`, `cancelled_before_issue`, `credit_still_valid`, `booking_open_for_extras`,
`inside_void_window`, `inside_free_change_window`, `booking_is_ticketed`, `whole_itinerary_cancelled`,
`refund_review_approved`, `one_correction_per_booking`), so no eligibility has been silently retired. The two
base `formula` fields that revision 1's findings A and B turned on are covered sentence by sentence:
`air_penalty`'s `min(no_show_penalty_usd, amount_paid_usd)` by the two `air_penalty` entries (the value clause
and the ceiling clause), and `air_service_fee`'s `agency_service_fee_usd * passenger_count` by the
"charged once per traveller … at the moment the ticket is issued" entry.

**Findings A, B, C, D and E are closed.** One member of their family is not — see finding R2-1.

### revision_2 / factor_ladders, re-derived

| policy | factors | parameter / method | fall-through == baseline | ladders ≥3 tiers |
| --- | --- | --- | --- | --- |
| air_ext_no_show_penalty | 4 | 3 / 1 | 4/4 | yes |
| air_ext_unflown_tax_return | 5 | 4 / 1 | 5/5 | yes |
| air_ext_cancelled_ticket_credit | 5 | 4 / 1 | 5/5 | yes |
| air_ext_credit_release | 5 | 4 / 1 | 5/5 | yes |
| air_ext_outstanding_service_charge | 6 | 5 / 1 | 6/6 | yes |
| air_ext_cabin_upgrade_copay | 6 | 5 / 1 | 6/6 | yes |

- **Finding G closed.** `programme_fee_schedule` is now labelled `parameter`, which is the honest label for a
  three-way fee substitution. `programme_seat_shortfall` was retired, and a new `programme_billing_window`
  (`effect: method`, `decides: programme_billing`) takes the sixth slot. Its three tiers select three different
  **windows** over the same ledger — the whole of the current contract term, the last twelve months, or the
  current billing period alone — which is a window convention and so a genuine method, not a number
  substitution. Its tier rests on seeded records (`biz_programs.billing_frequency`,
  `biz_programs.contract_start_date`) and it bears weight on task 1's world (see `1.md` revision_2). The
  computation therefore has 5 honest `parameter` factors and 1 honest `method` factor.
- **Finding H closed.** Every one of the 31 factors now falls through to exactly its declared `baseline`.
  `fare_weighted_travellers`'s ladder was reordered so that its "otherwise" tier is "the travellers ticketed on
  the booking", which is what `baseline.rule` states and what `baseline` encodes.
- **Ladder nesting (revision 1's observation L) closed.** Eleven ladders were re-stated as partitions — "reaches
  half of the threshold **but not the whole of it**", "twice that largest move reaches the brand's threshold
  **while the move itself does not**", "within thirty days … **but not within seven**", "more than seven days …
  **but not more than thirty**", "carries one approval level **and no more**", and the club ladders' "**while
  either that bonus is below seventy-five percent or those points are fewer than sixty thousand**".

### revision_2 / rule_compute_equivalence, re-derived

- **Finding I closed on all four strands.** (i) `air_ext_unflown_tax_return`'s twelve-month change-line window is
  now stated in the rule ("at least one voluntary change line was posted to it **in the last twelve months**") and
  keyed to `K('change_window_months')`. (ii) `air_ext_cabin_upgrade_copay`'s acting base is now a sentence of its
  rule: "Those lines carry that charge for every traveller the booking carries only where they come to at least
  the fare brand's own agency service fee taken once for each of them; short of that they carry it for as many
  travellers as there are such lines." (iii) `air_ext_outstanding_service_charge` now says "counted **over the
  last month**", which is what `within_months=1` computes. (iv) The sweep now reports **no** compute binding
  without a `compute_basis` entry, in any of the six policies; every `compute_basis` value is verbatim in its
  rule and every `baseline.rule` sentence is verbatim in its rule.
- **Finding J closed.** The clause "and the rest is billed to the company" is gone from
  `air_ext_cabin_upgrade_copay`'s rule; the traveller-share sentence now promises only what the tool performs.
- **Finding K closed.** `air_ext_unflown_tax_return` now declares `air_refund_settlement`'s "A lodged claim
  settles in the form the fare brand prescribes and in no other form: money to the card, or value on a voucher,
  never both and never a mixture" superseded, replaced by "That return of taxes to the form of payment used
  stands alongside whatever the fare brand returns on its own terms, whether money or value on a voucher…".
- **Finding L closed.** Every rule and every tool `Args` entry now says "rounded to the nearest cent", which is
  what `RND` computes; the ladder nesting is addressed above; and
  `apply_travel_credit_e74c9b2a`'s Args now read the voucher code and `source_event_id` "as the booking's credit
  lines record it" / "read from that line on the booking's ledger" rather than "from the confirmation that minted
  it", so no Arg implies a prior act.

### revision_2 / action_binding_and_uuids and prerequisite_graph, re-derived

The six uuid8s are unchanged and still distinct, unreused and not batch-derived: `8882d2a1`, `e343d675`,
`599fe29f`, `e74c9b2a`, `b626effa`, `d9ccb8ec`. Owners are unchanged (`apply_travel_credit_e74c9b2a` and
`settle_agency_service_charge_b626effa` remain `owner="user"`), so both tasks still hand a write to the customer.
Every `(target_tool, computes)` pair is still claimed by exactly one policy. Every function body is still
create-then-update with existence guards only — no status test, no refusal, no hint.

The four `prerequisite` edges are unchanged in shape and all four still pass every structural test: `policy_source`
verbatim in the blocked policy's own rule, never restated in the depended-on rule, `form: state` with no
`fallback_reason`, `gate` a real binding, `resolved_by` the depended-on policy's `target_tool`, `kind:
value_input`, graph acyclic, and no tool name or policy id anywhere in a blocked rule. `air_ext_cabin_upgrade_copay`'s
`condition` was rewritten to quote the threshold its rule now states — **finding 1-6 closed**.

- **Finding M partially closed.** `air_club_benefit_interaction` was added to the `base_policy_refs` of
  `air_ext_no_show_penalty`, `air_ext_cancelled_ticket_credit` and `air_ext_credit_release`, each with a declared
  `overwrite`. It was **not** added to `air_ext_unflown_tax_return`, whose `member_handling_charge` factor also
  turns a club tier into money — see finding R2-1. Revision 1's finding M named three policies and missed that
  fourth; the rework closed exactly the three named.

### revision_2 / findings

**R2-1 — SOURCE-POLICY RED (charter-global, bites task 0): the club override in `air_ext_unflown_tax_return` is
still undeclared.**
- *Symptom.* `member_handling_charge` waives a 25.00 USD handling charge because the traveller's club tier waives
  the agency service fee, while `air_club_benefit_interaction` is neither in that policy's `base_policy_refs`
  nor named in its `overwrite: [2 entries, both air_refund_settlement]`.
- *Root cause.* The rework declared the club override in the three policies revision 1's finding M named and left
  the fourth club-using policy untouched.
- *Evidence.* Base `air_club_benefit_interaction`: "A club benefit and a fare-brand inclusion never stack into a
  payment to the traveller: a bag already included in the brand is simply free, and **the club benefit is not
  converted into value**", and "the club tier held on the day the ticket is issued decides whether the agency
  service fee is waived and whether the first checked bag is carried free, and the fare brand's own rates apply
  to everything the club does not cover". `air_ext_unflown_tax_return`'s own rule distinguishes the two
  quantities — "the agency service fee is never paid back under this rule" — and then waives the **handling
  charge** on the strength of `CPARAM('club','agency_service_fee_waiver')`. Its `base_policy_refs` are
  `[air_refund_settlement, air_price_drop_guarantee]` and its `overwrite` names only `air_refund_settlement`.
  The three parallel policies show the author's own standard: each names this base sentence and replaces it.
- *Demonstrated consequence.* On task 0's world — see `0.md` revision_2 for the recomputation.
- *Affected artifact.* `air.extended.yaml` `extended_policies[air_ext_unflown_tax_return].base_policy_refs` and
  `.overwrite`; `tasks/0.json` `computations[1]` and the three scored parameters that move with it.

**R2-2 — observation (both tasks): the base-invariant cards in `design_rationale` were not updated.**
Task 0's card still says of `air_penalty` "Its clauses that stay in force: **the penalty is withheld from the
value the ticket still carries** … The extended policy keeps all three — **its ceiling is the ticket's own fare
and extra lines**", while `overwrite[0]` and `overwrite[1]` of the same policy now declare exactly those two base
clauses superseded. Task 1's card still says of `air_service_fee` "every one of their clauses stays in force …
the fee is charged once per traveller and follows the fare brand held", while three of that base policy's clauses
are now in `overwrite`. Both cards also omit the base policies added to their lineages (`air_club_benefit_interaction`
on task 0, `air_ticketing` on task 1). No consequence on the merged semantics: `overwrite` is the normative
declaration and `design_rationale` is an authoring worklog that no rollout reads.

**R2-3 — observation: one `replaced_by` points at the sentence that agrees with the clause it replaces.**
`air_ext_cancelled_ticket_credit.overwrite[1]` names base's "the club benefit is not converted into value" and
gives `replaced_by: "No membership uplift is added."` — the fall-through sentence of the uplift ladder, which
says the same thing as the base clause. The sentences that actually conflict are the two tier sentences that
follow it. The base sentence is named, so the override is declared and the merged semantics is unique (the ladder
governs), but the declaration does not display the conflict the way the parallel declarations in
`air_ext_no_show_penalty.overwrite[2]` and `air_ext_credit_release.overwrite[4]` do, both of which quote the tier
sentence.

**R2-4 — observation: ticket-shaped wording survives on a booking that is now a hold.**
`air_ext_cabin_upgrade_copay`'s prerequisite sentence still reads "only the travellers whose **tickets** the
standing lines already cover are counted into the move", and its compute binding is still named
`travellers_ticketed`, while the rest of the rule and `air_ext_outstanding_service_charge` now say "every
traveller the booking **carries**" and task 1's booking stands as an unticketed hold. No value turns on it.

**R2-5 — observation: two sentences about what a lapsed hold costs.**
`air_ext_outstanding_service_charge` now says "A booking that stands as an uncollected hold carries that charge
until it is settled", while base `air_ticketing` — newly added to its `base_policy_refs` with no `overwrite` —
says "An unticketed hold stands for the brand's hold window and is **released without charge** when it lapses".
Task 1's hold has not lapsed (Premium Economy Select `hold_window_hours` 48, `booked_date` 2026-09-15, frozen
2026-09-16 14:05), so no value turns on it and no second answer is derivable here.

**Items confirmed closed and not regressed:** A, B, C, D, E, F, G, H, I, J, K, L, 0-1, 0-2, 0-3, 0-4, 0-5, 0-6,
0-7, 1-1, 1-2, 1-3, 1-4, 1-5, 1-6, 1-7. **M is partially closed** (see R2-1).

## revision_2 / closing_checklist

**The difficulty still does not close at the source layer**, on one red light rather than seven.

- **Audit files and revisions.** `0.md`, `1.md` and `_difficulty.md` each carry revision 1 intact and a
  `revision_2` appended below it. No round-1 derivation was rewritten.
- **Coverage and exclusivity.** Unchanged and still holding: task 0 claims the four cancellation/credit policies,
  task 1 the two service-charge/upgrade policies, pairwise disjoint in policies, tools and cross-difficulty
  product (club + care against biz), jointly covering all six. Six tools, six frozen uuid8s. **Holds.**
- **Problem trees.** Unchanged in shape and re-derived from the new worlds. Task 0: 3 prerequisite problems, 3
  `value_input` edges (floor 2), root resolved by an `owner=user` tool, acyclic. Task 1: 1 prerequisite problem,
  1 `value_input` edge (floor 1), prerequisite resolved by an `owner=user` tool, acyclic. Every edge re-shown to
  bear weight by recomputation on the new seeds, and both `flips_to_true_by` proofs now state figures the world
  produces. **Holds.**
- **Computations, baselines and factors.** Six computations, 4–6 factors each (4/5/5/5/6/6), every ladder three
  pairwise-disjoint tiers stated in full in its rule, every fall-through equal to its baseline, every baseline
  self-sufficient and giving a definite number different from gold (585.00, 44.90, 1449.06, 1351.81, 29.90,
  977.50), all 31 factors re-shown to bear weight, at least one discriminating near-miss now present in **every**
  one of the six computations, and no stamp that agrees with a tier. **Holds.**
- **Unique solution.** Both tasks re-derived from the reworked charter and the new seeds reproduce the scored
  solution item for item. **Holds**, subject to the second reading R2-1 leaves standing on three of task 0's four
  parameters.
- **Gates on the final form.** The coordinator's re-run snapshot is green on all seven. The audited artifacts
  were not touched by this audit; the write domain remained
  `env/online_travel_agency/audits/policy_task/air_ticketing_desk/`.

**Per-task verdicts, revision 2.**

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | `SOURCE-POLICY RED` (R2-1) | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

Charter-global red lights outstanding: **R2-1** only. Charter-global observations: R2-2, R2-3, R2-4, R2-5.

---

## revision_3

Re-audit round 3. Revisions 1 and 2 above are left exactly as written.

### revision_3 / re-derivation grounds

| artifact | round 2 | round 3 | re-derived? |
| --- | --- | --- | --- |
| `air.extended.yaml` | `70fe60e9…` | `9826becf80c3c39d06c51bc7b0b685a51677ea0db7c1155739c1642300eaf27c` | **yes, in full** |
| `task_tools.py` | `1e103f68264da40816081e32a8e34658857f82e716dee30556e56102ad5223ab` | **unchanged** | carried forward by reference on the hash |
| masked view `0.json` | `aaa9e960…` | `05f9643c4062af664d0f540d20285764195ba37e76182ac8d057ded1b7883b4f` | yes |
| masked view `1.json` | `b0e8d9f9…` | **unchanged** (`b0e8d9f96ab42dfed8285a55581103ed1a959cd6e1d2a622f71fec5a2881d2f9`) | world carried forward; its **derivation** re-run, because the charter moved |

All four re-verified on disk. The charter moved, so every charter-global section is re-derived in full below.
`task_tools.py` is byte-identical to round 2, so revision_2's conclusions on owners, uuid8s, docstrings and
function bodies are carried forward on that hash rather than re-derived — the six uuid8s are still
`8882d2a1`, `e343d675`, `599fe29f`, `e74c9b2a`, `b626effa`, `d9ccb8ec`, and
`apply_travel_credit_e74c9b2a` and `settle_agency_service_charge_b626effa` are still `owner="user"`.
This round is **not blind**; it verifies closure, non-regression and the absence of new defects.

The base section of `air.extended.yaml` is still semantically verbatim against `blueprint/products/air.yaml`
(parsed diff: `extra ['extended_policies']`, `missing []`, `differing keys []`).

### revision_3 / override_declarations, re-derived

`overwrite` has gone from 17 entries to **21**. All 21 re-tested on the same three tests applied in revision 2:

```
air_ext_no_show_penalty            3 → 3   air_penalty ×2, air_club_benefit_interaction ×1
air_ext_unflown_tax_return         2 → 4   air_refund_settlement ×2, air_club_benefit_interaction ×2   [+2 NEW]
air_ext_cancelled_ticket_credit    2 → 2   air_credit_validity ×1, air_club_benefit_interaction ×1
air_ext_credit_release             5 → 5   air_credit_validity ×1, air_agg_credit_pooling ×3, air_club_… ×1
air_ext_outstanding_service_charge 3 → 4   air_service_fee ×3, air_biz_exclusion ×1                    [+1 NEW]
air_ext_cabin_upgrade_copay        2 → 3   air_seat_and_cabin_extras ×1, air_baggage_fee ×1, air_biz_exclusion ×1  [+1 NEW]
total 21   verbatim_base 21/21   verbatim_ext 21/21   gate_hit 0/21   problems: 0
```

**The gate question, which the brief puts hardest.** No `superseded_clause` — none of the 21, new or old —
matches or contains any of the ten base eligibility conditions (`credit_still_valid`,
`inside_free_change_window`, `booking_is_ticketed`, `whole_itinerary_cancelled`, `inside_void_window`,
`refund_review_approved`, `refund_stage_reached`, `booking_open_for_extras`, `cancelled_before_issue`,
`one_correction_per_booking`). Two of them sit in policies whose gate is the one being reasoned around —
`air_refund_settlement.refund_stage_reached` and `air_agg_credit_pooling.credit_still_valid` — and in both the
quotations taken are the per-line clause, the single-form clause, the one-pool sentence and the two
itinerary-price sentences, none of which is the gate's condition. **No eligibility has been retired.**

**Do the added lineages add preconditions?** Checked directly rather than assumed. The three base policies added
to lineages across rounds 2 and 3 — `air_club_benefit_interaction`, `air_biz_exclusion` and `air_ticketing` —
each carry `eligibility: []` and no `formula`. Adding them therefore adds no base precondition and no competing
machine form; it adds only clauses that must be honoured or declared. That is the right outcome, and it is what
both base-invariant cards now claim.

The four new entries, one by one:

1. `air_ext_unflown_tax_return[2]` — `air_club_benefit_interaction`, "the fare brand's own rates apply to
   everything the club does not cover", replaced by the handling-waiver tier.
2. `air_ext_unflown_tax_return[3]` — same base policy, "A club benefit and a fare-brand inclusion never stack
   into a payment to the traveller: a bag already included in the brand is simply free, and the club benefit is
   not converted into value.", replaced by the member-handling tier. Together these are **finding R2-1's fix**,
   and `air_club_benefit_interaction` is now in that policy's `base_policy_refs`.
3. `air_ext_outstanding_service_charge[3]` — `air_biz_exclusion`, "a booking that carries a corporate programme
   reference is priced entirely on the programme's negotiated terms", replaced by the conversion-markup sentence.
   The departure is real: `K('domestic_markup_pct') = 1.0` is neither the programme's negotiated markup (2.0) nor
   the brand's (2.5).
4. `air_ext_cabin_upgrade_copay[2]` — `air_biz_exclusion`, "none of the consumer concessions in this charter
   apply to it", replaced by the lead-time share sentence. The departure is real: the early/standard lead-time
   share is a consumer-side concession applied to a corporate booking. `air_biz_exclusion` is now in that
   policy's `base_policy_refs`, where it was not before.

**Was the sweep exhaustive on its own terms?** Tested independently, not accepted.

- *Are there only two cross-product interaction policies in this charter?* Yes. All sixteen base policies were
  scanned for language governing another product. Only **`air_club_benefit_interaction`** (the traveller club)
  and **`air_biz_exclusion`** (the corporate programme) govern how another product changes an air answer; the
  other fourteen mention another product only incidentally ("minimum stay", "a claim", "does not cover"). There
  is **no** base air policy governing the travel-protection (`care`) interaction at all, which is why the two
  `care`-reading factors — `protection_recovery_share` and `protection_deductible_offset` — have no interaction
  policy to depart from and correctly declare nothing against one.
- *Does every extended policy that turns another product into money declare against the right one?*

| extended policy | product read | turns it into money at | interaction policy | declared? |
| --- | --- | --- | --- | --- |
| air_ext_no_show_penalty | club | `member_penalty_softening` | air_club_benefit_interaction | yes, `[2]` |
| air_ext_unflown_tax_return | club, care | `member_handling_charge` / `protection_recovery_share` | air_club_benefit_interaction / — | yes, `[2]`,`[3]` / n.a. |
| air_ext_cancelled_ticket_credit | club | `membership_credit_uplift` | air_club_benefit_interaction | yes, `[1]` |
| air_ext_credit_release | club, care | `member_reissue_treatment`, `release_record_share` / `protection_deductible_offset` | air_club_benefit_interaction / — | yes, `[4]` / n.a. |
| air_ext_outstanding_service_charge | biz | unit, window, rebate, overage, markup | air_biz_exclusion | yes, `[3]` |
| air_ext_cabin_upgrade_copay | biz | discount, approval, settlement, lead-time | air_biz_exclusion | yes, `[2]` |

Six of six. **The sweep is exhaustive and finding R2-1 is closed at the shape, not at the one policy.**

### revision_3 / factor_ladders, rule_compute_equivalence and prerequisite_graph, re-derived

Re-run in full on the new charter:

| policy | factors | parameter / method | ladders ≥3 tiers, all ending "otherwise" | fall-through == baseline | compute_basis gaps |
| --- | --- | --- | --- | --- | --- |
| air_ext_no_show_penalty | 4 | 3 / 1 | yes | 4/4 | none |
| air_ext_unflown_tax_return | 5 | 4 / 1 | yes | 5/5 | none |
| air_ext_cancelled_ticket_credit | 5 | 4 / 1 | yes | 5/5 | none |
| air_ext_credit_release | 5 | 4 / 1 | yes | 5/5 | none |
| air_ext_outstanding_service_charge | 6 | 5 / 1 | yes | 6/6 | none |
| air_ext_cabin_upgrade_copay | 6 | 5 / 1 | yes | 6/6 | none |

31 factors. Every `compute_basis` value verbatim in its rule, every `baseline.rule` sentence verbatim in its
rule, no orphan `compute_basis` key, no compute binding without one. The four prerequisite edges are unchanged
and all four still pass every structural test (`policy_source` verbatim in the blocked rule and absent from the
depended-on rule, `form: state` with no `fallback_reason`, `gate` a real binding, `resolved_by` the depended-on
`target_tool`, acyclic, no tool name or policy id in a blocked rule). Six distinct target tools, one policy each.

Swept the rules for sentences that promise a movement nothing performs: the sentences carrying no
`compute_basis` entry are the ladder fall-through heads ("No volume rebate is taken off the gross charge.", "The
whole of the brand's penalty is withheld.", and so on), the scope sentences and the four prerequisite sentences —
each implemented as the fall-through branch of the binding whose tier sentence the `compute_basis` quotes. None
promises a record or a movement that no tool produces. Revision 1's finding J stays closed.

### revision_3 / findings

**R2-1 — CLOSED, at the shape.** Verified above: `air_ext_unflown_tax_return` now carries
`air_club_benefit_interaction` in its lineage and declares both of that policy's operative clauses; the sweep was
re-run independently across all six extended policies and both interaction policies, and the claim that this
charter contains only two such base policies is true. The second reading that moved three of task 0's four
scored parameters in revision 2 (payout 142.76, voucher 1839.69, release 1715.40) is no longer derivable: the
base clauses it rested on are declared replaced.

**R2-2 — CLOSED.** Both base-invariant cards were rewritten from scratch and were checked **against the
charter** rather than for internal consistency. Task 0's card lists all six base policies appearing in its four
lineages and accounts for all **14** `overwrite` entries those four policies carry (air_penalty 2, club 5,
air_refund_settlement 2, air_credit_validity 2, air_agg_credit_pooling 3, air_price_drop_guarantee 0); task 1's
lists all five in its two lineages and accounts for all **7** (air_service_fee 3, air_biz_exclusion 2,
air_baggage_fee 1, air_seat_and_cabin_extras 1, club 0). 14 + 7 = 21, the full count. Both cards also state
that no superseded quotation is a gate condition and that the added lineages add no precondition — both of which
my own machine tests confirm independently. No base policy in any lineage is omitted from either card.

**R2-3 — CLOSED.** `air_ext_cancelled_ticket_credit.overwrite[1]` now gives `replaced_by` as the tier sentence
("Where the traveller's club tier earns five points or more per dollar and the membership has counted sixty
thousand qualifying points or more over the last twelve months, the high membership uplift is added instead"),
not the fall-through sentence that agreed with the base clause.

**R2-4 — CLOSED.** "whose tickets" no longer appears anywhere in the charter. `air_ext_cabin_upgrade_copay`'s
prerequisite sentence, its added threshold sentence and its edge `condition` all now say "every traveller the
booking **carries**", and the compute binding is renamed `travellers_carried`.

**R2-5 — CLOSED.** The extended sentence now reads "A booking that stands as an uncollected hold carries that
charge **for as long as the hold stands**, and it is not ticketed while any part of the collection is still
outstanding." It no longer says "until it is settled", so it no longer competes with base `air_ticketing`'s
"released without charge when it lapses": while the hold stands the charge stands, and when it lapses base
governs.

**R3-o1 — observation: three declarations quote a clause rather than a sentence.**
`air_ext_unflown_tax_return.overwrite[2]` and `[3]` and `air_ext_cancelled_ticket_credit.overwrite[1]` give
`replaced_by` strings that are verbatim substrings of their rules but are mid-sentence clauses, one of them
opening "and where the traveller's club tier does not waive…". All three pass the verbatim test and the merged
semantics is unique; the other eighteen quote whole sentences.

**R3-o2 — observation: the club sweep names different clauses in different policies.**
`air_ext_unflown_tax_return` supersedes both of `air_club_benefit_interaction`'s operative clauses;
`air_ext_no_show_penalty` supersedes only "the fare brand's own rates apply to everything the club does not
cover"; `air_ext_cancelled_ticket_credit` and `air_ext_credit_release` supersede only "the club benefit is not
converted into value". Each names a clause its policy genuinely contradicts and each merged semantics is unique,
so no second number is derivable in any of the four; the asymmetry is recorded because a reader comparing the
four declarations will notice it.

**R3-o3 — observation: one loose sentence in task 1's card.** It says the programme's negotiated terms are
"where the air discount, the approval share and the traveller share come from". The air discount is a programme
rate (`negotiated_air_discount_pct`); the approval and traveller shares are the policy's own `K` constants whose
**tier** the programme's fields select. No value turns on it.

**R3-o4 — observation: one claim in the round-3 addendum lies outside my read domain.** `tasks/0.json`'s
`design_rationale` asserts that the new name collides with no other customer seeded anywhere in this scenario,
and lists them. Read isolation forbids me the other difficulties' task directories, so I verified uniqueness
only within this difficulty (Rosalind Achterberg in task 0, Delia Kastellanos in task 1 — no collision, in given
name or surname). The coordinator's merge check is the authority for the rest of that list.

## revision_3 / closing_checklist

**The difficulty closes at the source layer.** All four relationships PASS on both tasks; no red light is
outstanding.

- **Audit files and revisions.** `0.md`, `1.md` and `_difficulty.md` each carry revision 1, revision 2 and
  revision 3 in order, none rewritten. Every comparison section carries an explicit verdict.
- **Coverage and exclusivity.** All six extended policies covered; task 0 claims the four cancellation/credit
  policies and task 1 the two service-charge/upgrade policies; pairwise disjoint in policies, in tools, in base
  lineage and in the cross-difficulty product read (club + care against biz); each scope spans its whole problem
  tree, root and prerequisites. Six task tools, closed over the two scopes, each carrying an independently
  generated, frozen, unreused uuid8. **Holds.**
- **Problem trees.** Task 0: 3 prerequisite problems, 3 `value_input` edges against a floor of 2, one problem
  resolved by an `owner=user` tool, no cycle. Task 1: 1 prerequisite problem, 1 `value_input` edge against a
  floor of 1, resolved by an `owner=user` tool, no cycle. The four edges of the difficulty together are a DAG
  with no cross-task reference. Each edge re-shown load-bearing by recomputation, each `flips_to_true_by` and
  `edge_load_bearing` figure re-checked against the world. **Holds.**
- **Computations, baselines and factors.** Six computations, 4–6 factors each (4/5/5/5/6/6), each with at least
  2 `parameter` and 1 honest `method`; every ladder three pairwise-disjoint tiers stated in full in its rule;
  every fall-through equal to its baseline; every baseline self-sufficient and giving a definite number
  different from gold (585.00, 44.90, 1449.06, 1351.81, 29.90, 977.50); all 31 factors re-proved to bear weight;
  at least one score-discriminating near-miss in every one of the six computations; no stamp agreeing with a
  tier. Per task, at least one multi-source and at least one cross-difficulty factor — task 0 reads club and
  care, task 1 reads biz, all seeded. **Holds.**
- **Unique solution.** Both tasks re-derived from the reworked charter and the current seeds reproduce the
  scored solution item for item, with no second defensible reading left standing. **Holds.**
- **Gates on the final form.** The coordinator's re-run snapshot is green on all seven. The audited artifacts
  were not touched by this audit in any round; the write domain remained
  `env/online_travel_agency/audits/policy_task/air_ticketing_desk/`.

**Per-task verdicts, revision 3.**

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

No charter-global red light outstanding. Observations carried forward for the record: R3-o1, R3-o2, R3-o3,
R3-o4. The cross-difficulty merge surface and the scenario-level check are not this skill's to run and no
verdict here rests on them.
