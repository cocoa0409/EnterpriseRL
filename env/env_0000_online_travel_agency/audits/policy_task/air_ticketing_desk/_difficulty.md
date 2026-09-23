# Policy-task audit — air_ticketing_desk / charter-global

## charter_global_frozen

- freeze time: 2026-09-17 (session clock), written **before any task's GT was read**.
- auditor: independent source-layer auditor (not the agent that authored these artifacts).
- frozen inputs and their hashes (sha256, first 16 hex):
  - `env/env_0000_online_travel_agency/tasks/air_ticketing_desk/air.extended.yaml` — `5168f11ad8285f15` (207028 bytes)
  - `env/env_0000_online_travel_agency/tasks/air_ticketing_desk/task_tools.py` — `083ad6029813710d` (21849 bytes)
  - masked task views: `0.masked.json` `3d48dbd0c51356b7`, `1.masked.json` `3f4f489240f7e22d`
- fields permitted while this section was written: the blueprint (`blueprint.yaml`, `db_schema.json`,
  `share_tools.py`, `products/air.yaml` and, for cross-category reads only, `products/care.yaml` and
  `products/stay.yaml` variant parameters), the whole of `air.extended.yaml`, the whole of
  `task_tools.py`, and each task's `frozen_time` / `user_scenario` / `initial_state` through the
  masked views.
- fields explicitly masked and not read: `evaluation_criteria`, `computations`, `charter_scope`,
  `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`,
  `db_closure`, `db_closure_matches_initial_state` on both tasks. No `tasks/*.json` file was opened
  and no recursive grep was run over `tasks/`.
- entry conditions (Step 0): the coordinator supplied the instantiation-stage gate snapshot with the
  actual output lines of `check_extended.py`, `check_task_tools.py`, `replay_tasks.py`,
  `check_solvability.py`, `check_compute.py`, `check_grounding.py` and `check_cross_fire.py`, all
  green, and the two masked views with their hashes, which this audit re-computed and matched. Entry
  conditions are **complete**. The gates are cited, not re-run, and a machine green light is treated
  as the qualification to enter this audit rather than as proof of correctness.

### policy_conflict_scan

The structured policy in force for category `air` is the verbatim base section of
`blueprint/products/air.yaml` (16 policies) plus the 6 `extended_policies` of
`air.extended.yaml`. The base section of the extended file was compared key by key against the
blueprint product and is **verbatim identical** (`category`, `display_name`, `binding`, `lifecycle`,
`accounts`, `parameter_schema`, `variants`, `events`, `measures`, `policies` all equal; the only
added key is `extended_policies`). The base copy has not been rewritten.

Subjects, triggers and target tools of the six extended policies:

| policy | subject | computes | target_tool | trigger |
| --- | --- | --- | --- | --- |
| air_ext_cancellation_penalty | air_penalty_charge | penalty_amount_usd | withhold_cancellation_penalty_77ca3b84 | state_due |
| air_ext_airline_tax_return | air_refund_payout | tax_return_amount_usd | return_airline_refunded_taxes_4767edfd | state_due |
| air_ext_cancelled_ticket_credit | air_credit_issue | voucher_value_usd | issue_travel_credit_voucher_dd7ecc26 | state_due |
| air_ext_pooled_credit_release | air_credit_redeem | released_credit_usd | release_travel_credit_value_2b680572 | on_request |
| air_ext_credit_reissue_fee | air_fare_charge | reissue_fee_usd | charge_credit_reissue_fee_efe635ea | state_due |
| air_ext_lapsed_credit_carry_forward | air_credit_issue | carried_value_usd | reissue_lapsed_travel_credit_f544c035 | on_request |

Overlapping subjects: `air_credit_issue` is the subject of two extended policies
(`air_ext_cancelled_ticket_credit`, `air_ext_lapsed_credit_carry_forward`). They compute different
quantities (`voucher_value_usd` vs `carried_value_usd`) through different tools and are
distinguished by their trigger circumstance (an original voucher against a cancelled ticket vs a
fresh voucher replacing vouchers that have lapsed), so the pair of `(target_tool, computes)` claims
stays unique. The consequence of the two sharing one record-visible outcome is taken up in
`prerequisite_sentences` and in finding **CG-4** below.

Eligibility, time anchors and terminal states: no extended policy restates or relaxes a base
eligibility gate. The base gates that remain live over these six policies are
`air_cancel_refund.refund_review_approved` (an approved refund review on file before a claim is
lodged), `air_credit_validity.cancelled_before_issue` (a voucher is issued only at cancelled /
refund pending / refunded), `air_refund_settlement.refund_stage_reached` (same states for a payout)
and `air_agg_credit_pooling.credit_still_valid` (a credit is applied only inside its validity term).
All four are inherited unweakened; none is contradicted by an extended `rule`.

Cross-category read boundaries: `club` is read by all six policies, `care` by
`air_ext_cancelled_ticket_credit`, `stay` by `air_ext_lapsed_credit_carry_forward`. Every declared
`cross_category` entry is genuinely exercised by a `CFIELD`/`CPARAM`/`XSUM`/`XCOUNT` in the matching
`compute`, and no policy reads a category it does not declare.

**Conflicts found.** Four base sentences are handled differently by an extended policy that cites
the base policy in `base_policy_refs` while naming no `overwrite` against it. They are set out in
`override_declarations` and carried into findings **CG-1**, **CG-2** and **CG-3**. The M tasks'
claimed scopes are otherwise mutually exclusive and jointly complete: policies 1–4 form one
prerequisite-connected component and policies 5–6 the other, the two components share no policy and
together cover all six.

### rule_compute_equivalence

Check 2 was run over all six policies, binding by binding, in both directions.

**Forward (every `compute` binding has a verbatim `compute_basis` quotation that is a sentence of
that policy's own `rule`).** Every binding of all six policies carries a `compute_basis` entry, and
every quotation was located verbatim in the corresponding `rule`. Windows, filters, tiers, branches,
cross-category reads, acting bases, caps and rounding all carry a quotation: the rolling windows
(`within_months=12` in `prior_reworks_12m`, `within_months=6` in `notices_6m`, `within_months=12` in
`club_qualifying_spend_12m`, `club_air_accruals_12m` and `stay_room_spend_12m`), the caps
(`ticket_value`, `money_collected`, the `MX(...,0)` floors) and the rounding point ("rounded to two
decimal places at the end and never at any intermediate step", present once in every policy's rule
and implemented as a single outermost `RND(...,2)`).

**Backward (the rule makes no promise `compute` does not keep).** Two gaps were found, neither
demonstrable on the two seeded worlds and both recorded as observations **CG-5** and **CG-6**:

1. `air_ext_credit_reissue_fee` and `air_ext_lapsed_credit_carry_forward` speak throughout of
   "vouchers **standing lapsed** on the booking" (`voucher_count`, `lapsed_value`, `lapsed_total`,
   `largest_voucher`), but their compute counts and sums **every** `air_credit_issue` row of the
   holding with no test against `credit_expires_on`. A voucher still inside its validity term would
   be counted as lapsed.
2. `air_ext_cancellation_penalty.ticket_value` and `air_ext_airline_tax_return.money_collected` are
   both `SUM('air_booking_events','amount_usd')` with **no filter**, so they sum the credit ledger
   (`air_credit_issue`, `air_credit_redeem` — account `travel_credit`) together with the money ledger
   (account `fare_paid`), although the rule sentences they implement say "the money collected on the
   booking". `accounts` in the base section keeps the two accounts distinct.

Every declared factor's ladder was checked in both faces: for all 31 declared factors, each tier
named in `factors[].ladder` is a sentence of the `rule` and a branch of the `decides` binding, and
each branch of every `decides` binding is a tier the rule states. **No tier lives in only one face.**

### action_binding_and_uuids

Each `(target_tool, computes)` pair is claimed by exactly one policy (table above); no pair repeats.
Each policy's subject, base refs, target tool, tool docstring and terminal state admit one business
reading, and no docstring adds a confirmation, review, wait or procedure the policy does not carry.

Docstring sequence discipline: no docstring in `task_tools.py` names another tool, states a position
in a sequence, or carries `before` / `after` / `first` / `then` / `prior to` as an ordering
instruction. The one phrase worth naming is in
`release_travel_credit_value_2b680572` — "the voucher code as it was given when the travel credit
was issued" — which describes the provenance of a Verbatim-class argument rather than ordering the
agent's work; it is not recorded as a defect.

uuid8s, checked one by one: `77ca3b84`, `4767edfd`, `dd7ecc26`, `2b680572`, `efe635ea`, `f544c035`.
All six are 8 lowercase hex characters, all six are distinct, no two share a prefix or a tail, none
is a near neighbour of another, and none is a sequence number or a batch derivation from a common
stem. **PASS.**

Function bodies: all six tools perform one unconditional `ctx.create` into `air_booking_events` after
an owner lookup. **No tool tests a prerequisite, refuses a call, raises, or returns a hint while a
prerequisite is unresolved** — there is no branch in any body that could. This is the function-body
citation the per-task `problem_chain` sections rely on.

Owners: four `owner="agent"` tools and two `owner="user"` tools
(`release_travel_credit_value_2b680572`, `reissue_lapsed_travel_credit_f544c035`), one in each of the
two prerequisite-connected components, so each component can supply a customer's own write.

### prerequisite_graph

Check 7 over the whole graph. Every policy has `prerequisite` filled in; three declare `[]`
(`air_ext_cancellation_penalty`, `air_ext_airline_tax_return`, `air_ext_credit_reissue_fee`) and
three declare edges:

| blocked policy | problem | kind | gate | form | resolved_by |
| --- | --- | --- | --- | --- | --- |
| air_ext_cancelled_ticket_credit | air_ext_cancellation_penalty | value_input | penalty_withheld | state | withhold_cancellation_penalty_77ca3b84 |
| air_ext_cancelled_ticket_credit | air_ext_airline_tax_return | value_input | returned_to_card | state | return_airline_refunded_taxes_4767edfd |
| air_ext_pooled_credit_release | air_ext_cancelled_ticket_credit | value_input | pool_issued | state | issue_travel_credit_voucher_dd7ecc26 |
| air_ext_lapsed_credit_carry_forward | air_ext_credit_reissue_fee | value_input | reissue_fee_charged | state | charge_credit_reissue_fee_efe635ea |

- Every `problem` points at another extended policy id in this file, never at a base policy and
  never at itself. **PASS.**
- The graph is two directed trees, `pooled_credit_release -> cancelled_ticket_credit -> {cancellation_penalty, airline_tax_return}`
  and `lapsed_credit_carry_forward -> credit_reissue_fee`. **Acyclic. PASS.**
- Every `policy_source` is verbatim locatable in the **blocked** policy's own `rule` (each was
  matched as an exact substring). **PASS.**
- `form` is `state` on all four edges and no `fallback_reason` appears anywhere, which is correct:
  `fallback_reason` must be present exactly on action-form edges. The state form has priority and is
  the form used throughout. **PASS.**
- `kind` is `value_input` on all four, and each `gate` names a binding that genuinely exists in the
  blocked policy's `compute` and genuinely carries the depended-on write's value:
  `penalty_withheld` = `SUM(... 'air_penalty_charge')`, `returned_to_card` = `ABS(SUM(... 'air_refund_payout'))`,
  `pool_issued` = `SUM(... 'air_credit_issue')`, `reissue_fee_charged` =
  `SUM(... 'air_fare_charge', charge_category='credit_reissue_fee')`. Each `resolved_by` tool creates
  exactly a row of that event type and charge category, so each edge's `effect` genuinely holds after
  the write. **PASS.**
- `condition` on each edge states the same handling-time state the prerequisite sentence states,
  neither strengthened nor weakened.
- No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears in
  any `prerequisite` block. **PASS.**

### prerequisite_sentences

Check 6, the four-point test, on each of the four edges.

1. **air_ext_cancelled_ticket_credit -> air_ext_cancellation_penalty.** Sentence: *"The value placed
   on the voucher is fixed only after the cancellation penalty owed under the fare brand held stands
   as a withheld line on the booking."* Ordering connective: "only after" ✓. What it waits on is a
   record-visible state in the words the tables use — a withheld line standing on the booking — with
   no action, performer or tool ✓. Names no tool, policy id, snake_case token or row id ✓. Strength
   and scope match the edge's `condition` ✓. The one write of this difficulty that brings that state
   about is `withhold_cancellation_penalty_77ca3b84` (the only tool that creates
   `event_type="air_penalty_charge"`), and the reader finds it from
   `air_ext_cancellation_penalty`'s own rule, whose result is the cancellation penalty withheld.
   **Single reading. PASS.**
2. **air_ext_cancelled_ticket_credit -> air_ext_airline_tax_return.** Sentence: *"The value placed on
   the voucher is fixed only after the taxes and carrier fees the airline returns stand as a payout
   line on the booking."* Four points ✓ as above. The one write creating
   `event_type="air_refund_payout"` is `return_airline_refunded_taxes_4767edfd`, and
   `air_ext_airline_tax_return` is the only policy whose result is the taxes the airline returns.
   **Single reading. PASS.**
3. **air_ext_lapsed_credit_carry_forward -> air_ext_credit_reissue_fee.** Sentence: *"The value
   carried onto the fresh voucher is fixed only after the reissue fee owed under the fare brand that
   produced the lapsed voucher stands as a charged line on the booking."* Four points ✓. The one
   write creating an `air_fare_charge` row with `charge_category="credit_reissue_fee"` is
   `charge_credit_reissue_fee_efe635ea`. **Single reading. PASS.**
4. **air_ext_pooled_credit_release -> air_ext_cancelled_ticket_credit.** Sentence: *"Value is
   released from the traveller's pooled travel credit only after a travel credit voucher stands
   issued against the cancelled booking."* The four points pass on their face. **But the state-form
   uniqueness test fails:** two writes of this difficulty bring "a travel credit voucher stands
   issued against the booking" about, and they are indistinguishable in the records. See finding
   **CG-4**.

No rule carries a second wording of any dependency, no other problem's tool name or id, and no
aggregated chain; and no depended-on policy's rule restates the blocked policy's sentence (checked
by searching each depended-on `rule` for the sentence). Base rules were swept for cross-problem
ordering language that could ground an edge without an extended sentence: `air_cancel_refund` ("A
refund claim is lodged only when the back office has already recorded an approved refund review
against this booking") and `air_agg_credit_pooling` state orderings, but no task's tree rests on
them — every edge of this difficulty is grounded in an extended rule sentence of its own. Recorded as
nothing more than that observation.

### override_declarations

Check 1's finding half, run once, sentence by sentence against every entry in every
`base_policy_refs`.

**Declared overrides, all four of which quote a base sentence that was located verbatim in the base
policy, and whose merged semantics are unique:**

- `air_ext_cancellation_penalty` over `air_cancel_refund`: the cancellation ladder sentence, replaced
  by "the flat cancellation penalty of the fare brand held, taken in full". Located verbatim ✓.
- `air_ext_airline_tax_return` over `air_refund_settlement` (twice: the per-fare-line payout
  sentence, and the per-line/aggregate cap sentence), over `air_baggage_fee` (the bag-refund
  sentence), and over `air_service_fee` (the service-fee-not-refunded sentence). All four located
  verbatim ✓.
- `air_ext_cancelled_ticket_credit` over `air_credit_validity`: the voucher-value clause. Located ✓.
- `air_ext_pooled_credit_release` over `air_agg_credit_pooling`: the transferability sentence.
  Located ✓.
- `air_ext_credit_reissue_fee` and `air_ext_lapsed_credit_carry_forward` over `air_credit_validity`:
  the clause "A voucher that has lapsed may be reissued once onto a fresh voucher against the brand's
  reissue fee". Located verbatim as a **prefix** of the base sentence, whose remainder ("and the
  fresh voucher carries the same validity term counted from the day of reissue") is thereby inherited
  and is in fact honoured by `air_ext_lapsed_credit_carry_forward`'s own rule ✓.

**Undeclared overrides found (each cited in `base_policy_refs`, each handled differently, none named
in any `overwrite`):**

- **CG-1** — `air_evt_schedule_change_rights`, cited by `air_ext_airline_tax_return`.
- **CG-2** — `air_baggage_fee`, cited by `air_ext_cancelled_ticket_credit`.
- **CG-3** — `air_club_benefit_interaction`, cited by `air_ext_cancelled_ticket_credit`.

Each is set out in `findings`. The demonstration of what each costs a particular task is in that
task's file, not here.

The three disguised forms were looked for specifically. **The anonymous intermediate factor** is
present in CG-2 and CG-3, where the deviation from base hides inside `extras_carry_share` and
`member_uplift` with no new parameter name at the policy's surface. **The 0/1 multiplier** appears as
`extras_carry_share`, `extras_added`, `correction_carry` and `penalty_deduction`, each an existence
condition multiplied onto an amount the base has already fixed — this is the shape behind finding
**CG-7**. **The dropped branch**: none found; every branch of every base selector these policies
touch is still producible. No author's note calls a base output a "wrong value".

`overwrite: []` does not occur — every extended policy declares at least one override — so the
empty-list case did not need the separate sweep.

### factor_ladders

Structure only; whether a factor bears weight is in each task's `factor_weight`.

| policy | factors | parameter | method | multi-source tiers | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| air_ext_cancellation_penalty | 5 | 3 | 2 | member_penalty_relief | club |
| air_ext_airline_tax_return | 5 | 4 | 1 | optional_extras_treatment, currency_conversion_holdback | club |
| air_ext_cancelled_ticket_credit | 5 | 3 | 2 | money_collected_basis, optional_extras_carry, member_voucher_uplift, protection_offset | club, care |
| air_ext_pooled_credit_release | 4 | 3 | 1 | named_traveller_share, member_release_bonus, name_correction_carry | club |
| air_ext_credit_reissue_fee | 6 | 4 | 2 | lapse_clock_anchor, voucher_count_basis, member_fee_relief | club |
| air_ext_lapsed_credit_carry_forward | 6 | 5 | 1 | lead_traveller_share, card_carry_uplift, house_activity_uplift, service_fee_recovery | club, stay |

Counts as declared are inside the bounds everywhere: 4 to 6 factors per policy, at least 2
`parameter` and at least 1 `method` per policy. Every ladder has at least three tiers with the
fall-through counted (four on the club-tier ladders), and in every ladder the tiers are pairwise
disjoint as stated — each was checked by taking the conditions as written and confirming no world
satisfies two at once (the club ladders are disjoint because tiers 1 and 2 name disjoint tier sets
and tier 3 requires the aggregate on the other side of the threshold; the party ladders are disjoint
because they name `>= 3`, `== 2` and otherwise). Every `decides` binding is an input to `result`,
never `result` itself, and each factor's `bindings` sets are disjoint from the other factors' within
its policy.

**Two structural defects were found.**

- **CG-7 (effect labels).** Of the 9 factors labelled `method`, 5 do not change how the quantity is
  computed: their tiers substitute a different coefficient into one unchanged formula. They are
  `air_ext_cancellation_penalty.airline_disruption_transform` (`× 0.50 / × 0.90 / × 1.00`),
  `air_ext_airline_tax_return.optional_extras_treatment` (`extras × 1 / × 0.5 / × 0`),
  `air_ext_cancelled_ticket_credit.money_collected_basis` (`fare_and_taxes + rework × 1 / × 0.5 / × 0`),
  `air_ext_cancelled_ticket_credit.disrupted_penalty_treatment` (`penalty × 0 / × 0.5 / × 1`) and
  `air_ext_pooled_credit_release.name_correction_carry` (`correction × 1 / × 0.5 / × 0`). The four
  that survive the test are `party_charging_basis` (tier 1 reads `passenger_count`, tier 2
  `base_fare_lines`, tier 3 the constant 1 — three different quantities from three different places),
  `lapse_clock_anchor` (three different anchor dates), `voucher_count_basis` (a per-voucher multiple
  against a per-booking one) and `lapsed_set_selection` (three different selections of rows).
  **Consequence:** counting only the factors that survive, `air_ext_airline_tax_return`,
  `air_ext_cancelled_ticket_credit` and `air_ext_pooled_credit_release` each declare **zero**
  `method` factors against a floor of 1. All three belong to task 0's tree; the demonstration is in
  `0.md`.
- **CG-8 (a vacuous fall-through).** In `optional_extras_treatment`, `extras_added`,
  `optional_extras_carry` and `name_correction_carry` the fall-through tier is reached exactly when
  the amount being scaled is zero, so it cannot produce a number any other tier would not also
  produce on that same world. Recorded as an observation, not a red light: the tiers do differ as
  *stated* methods, and no task turns on it.

Business realism of conditions and outcomes was checked tier by tier. The club-tier ladders, the
notice-period ladder, the holding-period ladder, the lapse-age ladder, the value bands and the age
surcharges all state conditions an airline retail business genuinely weighs, with outcomes it would
publish. Three outcomes are questionable and are carried as findings **CG-9**
(`journey_staleness_share` shrinking a voucher's releasable value by 15–40% because the flown date
has passed, where a voucher's answer to time is its expiry), **CG-10** (the reissue/carry pair, whose
demonstration is in `1.md`) and **CG-11** (`lead_traveller_share`, likewise in `1.md`).

### findings

**CG-1 — SOURCE-POLICY RED. Undeclared override of `air_evt_schedule_change_rights`.**
*Symptom.* For a booking that has received an airline schedule move at or beyond the fare brand's
threshold, the base charter and the extended charter return value to the traveller in different forms
and different amounts.
*Root cause.* `air_ext_airline_tax_return` names `air_evt_schedule_change_rights` in
`base_policy_refs` but no `overwrite` entry anywhere in the file names that base policy, so the base
sentence is inherited in full while the extended tree prices the same situation its own way.
*Evidence.* Base `air_evt_schedule_change_rights.rule`, sentence 1: *"An airline schedule move at or
beyond the threshold of the fare brand held gives the traveller a right to be rebooked at no charge
onto any flight the airline will accept, or to be refunded in full to the original form of payment
whatever the brand's ordinary refund form."* Against it,
`air_ext_cancellation_penalty.rule`: *"Where the airline has recorded a move on the booking at or
beyond the schedule-change threshold of the fare brand held, the penalty owed is halved"* — a
withheld penalty where base withholds nothing — and the tree as a whole returns the balance on a
voucher where base gives money to the card "whatever the brand's ordinary refund form".
*Demonstrated consequence.* Two defensible answers in the same situation. Demonstrated against
task 0's world in `0.md` § `policy_self_consistency`.
*Affected artifact.* `air.extended.yaml`, `air_ext_cancellation_penalty.overwrite` (missing entry)
and `air_ext_airline_tax_return.overwrite` (missing entry); the scored parameters
`penalty_amount_usd`, `tax_return_amount_usd` and `voucher_value_usd`.
*Bears on:* task 0.

**CG-2 — SOURCE-POLICY RED. Undeclared override of `air_baggage_fee` by
`air_ext_cancelled_ticket_credit`.**
*Symptom.* An optional-extra line that base refunds in no amount is returned twice over.
*Root cause.* `air_ext_cancelled_ticket_credit` cites `air_baggage_fee` in `base_policy_refs` and
carries optional extras onto the voucher through `optional_extras_carry`, but its `overwrite` names
only `air_credit_validity`. `air_ext_airline_tax_return` *did* declare an override against the same
base sentence for its own half; the second policy's deviation was never declared.
*Evidence.* Base `air_baggage_fee.rule`, last sentence: *"A bag line already charged is refunded in
full when the traveller cancels the whole itinerary inside the void window, and is otherwise refunded
only where the flight itself did not operate."* Against it,
`air_ext_cancelled_ticket_credit.rule`: *"Where an optional extra stands on the booking and an
optional extra on it was sold after the day the booking was opened, half of what the optional extras
were charged is carried onto the voucher."*
*Demonstrated consequence.* Demonstrated against task 0's world in `0.md` § `policy_self_consistency`:
the same $45.00 bag line is returned as $22.50 of cash by one policy of the tree and a further
$22.50 of voucher value by another, so the traveller recovers the whole of a charge base refunds in
no amount.
*Affected artifact.* `air.extended.yaml`, `air_ext_cancelled_ticket_credit.overwrite`; the factor
`optional_extras_carry`; the scored parameter `voucher_value_usd`.
*Bears on:* task 0.

**CG-3 — SOURCE-POLICY RED. Undeclared override of `air_club_benefit_interaction` by
`air_ext_cancelled_ticket_credit`.**
*Symptom.* A club tier is converted into voucher value, which base forbids in terms.
*Root cause.* `air_ext_cancelled_ticket_credit` cites `air_club_benefit_interaction` in
`base_policy_refs` and declares no `overwrite` against it, while its `member_voucher_uplift` factor
multiplies the voucher value by `1 + uplift` on the strength of the traveller's club tier.
*Evidence.* Base `air_club_benefit_interaction.rule`: *"A club benefit and a fare-brand inclusion
never stack into a payment to the traveller: a bag already included in the brand is simply free, and
the club benefit is not converted into value."* Base also fixes what the tier may decide: *"the club
tier held on the day the ticket is issued decides whether the agency service fee is waived and
whether the first checked bag is carried free"* — an uplift on a voucher is neither. Against it,
`air_ext_cancelled_ticket_credit.rule`: *"Where the traveller holds an active traveller club card of
any tier and the card was enrolled within the long-membership term, the entry-member uplift is added
to the value placed on the voucher."*
*Demonstrated consequence.* Demonstrated against task 0's world in `0.md` § `policy_self_consistency`.
*Affected artifact.* `air.extended.yaml`, `air_ext_cancelled_ticket_credit.overwrite`; the factor
`member_voucher_uplift`; the scored parameter `voucher_value_usd`.
*Bears on:* task 0.

**CG-4 — SOURCE-POLICY RED. A state-form prerequisite whose state two writes of this difficulty
bring about.**
*Symptom.* The reader of `air_ext_pooled_credit_release` cannot resolve the hop from the waited-on
state to the write that produces it, because two writes produce records that are identical in the
fields the sentence names.
*Root cause.* The edge is declared `form: state` with
`policy_source: "Value is released from the traveller's pooled travel credit only after a travel
credit voucher stands issued against the cancelled booking."` Two tools of this difficulty bring that
state about.
*Evidence.* `task_tools.py`, `issue_travel_credit_voucher_dd7ecc26` creates
`event_type="air_credit_issue", charge_category="credit_issue"` and its docstring says it "mints one
voucher and posts the matching issue line to that booking's credit ledger, so the booking afterwards
carries an open travel credit". `task_tools.py`, `reissue_lapsed_travel_credit_f544c035` creates
`event_type="air_credit_issue", charge_category="credit_issue"` and its docstring says it "mints one
fresh voucher and posts the matching issue line to the booking's credit ledger, so the booking
afterwards carries an open travel credit". The two rows differ only in the voucher code prefix
(`WLTC` vs `WLTR`), which the prerequisite sentence does not name; both are subjects of a policy
whose `computes` is a voucher value against the booking.
*Demonstrated consequence.* Two candidate writes for one hop. The consequence for task 0's own world
— where only one of the two is in fact applicable, and why — is worked out in `0.md`
§ `problem_chain`.
*Affected artifact.* `air.extended.yaml`, `air_ext_pooled_credit_release.prerequisite[0]`, and the
two tool contracts named above.
*Bears on:* task 0.

**CG-5 — Observation. "Standing lapsed" is never tested.**
`air_ext_credit_reissue_fee.voucher_count` / `.lapsed_value` / `.latest_expiry` and
`air_ext_lapsed_credit_carry_forward.voucher_count` / `.lapsed_total` / `.largest_voucher` aggregate
every `air_credit_issue` row of the holding with no comparison of `credit_expires_on` against `NOW`,
while every rule sentence they implement says "vouchers stand **lapsed** on the booking". On a world
carrying one lapsed and one live voucher the fee would be charged twice and the live voucher's value
folded into a carry-forward. Not a red light: on task 1, the only world in which these policies act,
both vouchers have in fact lapsed (`credit_expires_on` `2025-11-20` and `2026-01-10`, both before
`2026-09-17`), so no consequence is demonstrable. *Bears on:* task 1.

**CG-6 — Observation. The two accounts are summed together in a cap.**
`air_ext_cancellation_penalty.ticket_value` and `air_ext_airline_tax_return.money_collected` are
unfiltered `SUM('air_booking_events','amount_usd')`, which adds rows of the `travel_credit` account
(`air_credit_issue`, `air_credit_redeem`) to rows of the `fare_paid` account, although the rule
sentences say "the money collected on the booking" and the base `accounts` block keeps the two
apart. Not a red light: on both seeded worlds neither cap binds, so the scored values are unchanged.

**CG-7 — SOURCE-FACTOR RED. Five factors labelled `method` only substitute a coefficient.**
*Symptom.* Three of the six policies declare a `method` factor but have none.
*Root cause and evidence.* Set out in `factor_ladders` above, with each of the five ladders and the
coefficient its tiers select. The test applied is the one the charter itself implies: a `method`
tier changes the algorithm, a `parameter` tier a number. In all five the records read, the rows
selected and the order of operations are identical across tiers; only a multiplier moves.
*Demonstrated consequence.* Counting only surviving factors, `air_ext_airline_tax_return` declares
4 `parameter` and **0** `method`; `air_ext_cancelled_ticket_credit` declares 5 `parameter` and
**0** `method`; `air_ext_pooled_credit_release` declares 4 `parameter` and **0** `method` — each
against a floor of 1. Demonstrated per computation in `0.md` § `factor_weight`.
*Affected artifact.* `air.extended.yaml`, the `factors[].effect` labels named above.
*Bears on:* task 0.

**CG-8 — Observation. Vacuous fall-through tiers.** See `factor_ladders`. The fall-through of
`optional_extras_treatment`, `optional_extras_carry` and `name_correction_carry` is reached exactly
when the amount it scales is nil, so it cannot yield a number the tier above it would not yield on
the same world. The three-tier count is met as stated, and no task turns on it.

**CG-9 — Observation. A voucher that shrinks with the calendar.**
`air_ext_pooled_credit_release.journey_staleness_share` releases 85% of the open pool once the
outbound date has passed and 60% once it is more than 90 days past, on top of the voucher's own
expiry term, which the base charter already makes the instrument's answer to the passage of time
(`air_agg_credit_pooling`: *"A travel credit is applied to a new itinerary only when frozen time is
not after the moment the voucher was issued ... plus the credit validity term"*, and *"the remainder
stays on the last voucher touched and keeps that voucher's original expiry; the expiry is never
extended by redemption"*). A voucher inside its validity term that is nonetheless worth 60 cents in
the dollar is not a treatment an agency publishes. Recorded as an observation because the tier does
change the scored number and the ladder is stated in full; its weight on task 0 is in
`0.md` § `factor_weight`. *Bears on:* task 0.

**CG-10 — SOURCE-FACTOR RED. Charged to reissue two vouchers, given one.**
*Symptom.* Within one problem tree, the policy that prices the reissue and the policy that performs
it count different numbers of vouchers as being put back into use.
*Root cause.* `air_ext_credit_reissue_fee.voucher_count_basis` tier 1 and
`air_ext_lapsed_credit_carry_forward.lapsed_set_selection` tier 1 are both keyed on "two or more
vouchers stand lapsed on the booking" and reach opposite conclusions about how many of them the
traveller is getting back.
*Evidence.* `air_ext_credit_reissue_fee.rule`: *"Where two or more vouchers stand lapsed on the
booking, the fee is taken once for each voucher standing lapsed on it."*
`air_ext_lapsed_credit_carry_forward.rule`: *"Where two or more vouchers stand lapsed on the booking
and the most recent of them lapsed longer ago than the long-lapse term, only the largest lapsed
voucher standing on the booking is carried forward."*
*Demonstrated consequence.* Demonstrated against task 1's world in `1.md` § `factor_weight`: the fee
is computed on two vouchers while the value carried is computed from one, and the second voucher's
value is extinguished. The outcome is not one a travel business publishes.
*Affected artifact.* `air.extended.yaml`, `air_ext_credit_reissue_fee.factors[voucher_count_basis]`
and `air_ext_lapsed_credit_carry_forward.factors[lapsed_set_selection]`; the scored parameters
`reissue_fee_usd` and `carried_value_usd`.
*Bears on:* task 1.

**CG-11 — SOURCE-FACTOR RED. A party share taken from a voucher already reduced to one traveller's
own.**
*Symptom.* `lead_traveller_share` takes a further share off a value from which the other traveller's
voucher has already been removed, on the stated ground that the fresh voucher stands in the lead
traveller's name alone — a ground already satisfied before the factor applies.
*Root cause.* `air_ext_lapsed_credit_carry_forward` applies `lapsed_set_selection` and
`lead_traveller_share` multiplicatively to the same quantity, and the second factor's stated reason
is the outcome of the first.
*Evidence.* `air_ext_lapsed_credit_carry_forward.rule*: *"Where the fare brand that produced the
lapsed voucher makes credits non-transferable and three or more base-fare lines stand on the booking,
the value carried is taken at the shared-lead share **because the fresh voucher stands in the lead
traveller's name alone**"*, and the preceding ladder sentence *"only the largest lapsed voucher
standing on the booking is carried forward"*. `compute`:
`result: RND(MX(value_standing * carry_share * party_share * (1 + card_uplift + house_uplift) - ...`,
where `value_standing` is already `largest_voucher`.
*Demonstrated consequence.* Demonstrated against task 1's world in `1.md` § `factor_weight`.
*Affected artifact.* `air.extended.yaml`, `air_ext_lapsed_credit_carry_forward.factors[lead_traveller_share]`;
the scored parameter `carried_value_usd`.
*Bears on:* task 1.

**CG-12 — Observation. `replaced_by` names a tier rather than the baseline.**
In `air_ext_airline_tax_return`, the `overwrite` against `air_service_fee` replaces *"The service fee
is not refunded when the traveller later cancels..."* with the **Blue/Silver/Gold** half-fee sentence,
while the policy's rule also returns the **whole** agency service fee to a Platinum, Titanium or
Ambassador member. A reader merging base and extended by the declaration alone finds the senior tier
undeclared. Not a red light here: neither seeded world carries a senior-tier card, so no task has a
second defensible answer on this account. The same shape appears in the `air_baggage_fee` override,
whose `replaced_by` names the half-extras tier rather than the policy's baseline.

**CG-13 — Observation. Rounding mode.** `RND` is implemented as Python `round`, which rounds half to
even, while every tool docstring requires the argument to be "already rounded half away from zero to
the cent". The two disagree only on an exact half-cent; neither seeded world produces one.


## closing_checklist

Written after both tasks had a frozen `source_derivation_frozen` and a `source_gt_comparison`. This
section is post-reveal; everything above it was written before any GT was read and has not been
altered since, apart from one arithmetic correction to a figure quoted in CG-3 (`47.71`, the scored
effect of the uplift, replacing a mis-multiplied `56.14` figure) made while verifying the audit's own
recomputations and before the reveal.

**The difficulty does NOT close out.** Step 4's checklist requires
"policy self-consistency PASS + problem tree holds PASS + factors bear weight PASS + unique solution
PASS" together, and three of the four fail. The checklist is recorded item by item so the state is
legible rather than merely refused.

| item | state |
| --- | --- |
| per-task audit files correspond one-to-one with the tasks; `_difficulty.md` alongside | ✔ `0.md`, `1.md`, `_difficulty.md` |
| old revisions traceable | ✔ first revision of this audit; the previous audit files for this difficulty were deleted before this run and nothing was rewritten to accommodate new GT |
| every comparison section carries a PASS | ✘ task 0 carries SOURCE-POLICY, SOURCE-CHAIN and SOURCE-FACTOR; task 1 carries SOURCE-FACTOR |
| extended policies fully covered; the M scopes pairwise disjoint | ✔ task 0 claims policies 1–4, task 1 claims 5–6; disjoint and jointly complete, each scope spanning a whole problem tree |
| task tools and GT closed | ✔ six tools, four claimed by task 0 and two by task 1, each `(target_tool, computes)` unique |
| each task tool uses an independently generated, frozen uuid8 | ✔ see § `action_binding_and_uuids` |
| every tree: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥ 1 `owner=user` write, no cycle | ✔ task 0: n=3, 3 `value_input`, user write at the root; task 1: n=1, 1 `value_input`, user write at the root |
| the difficulty's `prerequisite` edges together remain a DAG, no cycle from cross-task references | ✔ two disjoint trees, four edges, no cross-task reference |
| every computation declares a self-sufficient baseline giving a definite number different from gold | ✔ all six: 119.00/114.19, 637.20/661.81, 2429.20/2433.49, 2433.49/1161.29, 75.00/224.00, 2892.00/623.80 |
| 4–6 factors per computation, ≥ 2 `parameter`, ≥ 1 `method` | ✘ **as declared** yes; **as they behave**, `air_ext_airline_tax_return`, `air_ext_cancelled_ticket_credit` and `air_ext_pooled_credit_release` have no `method` factor at all — finding CG-7 |
| ≥ 1 multi-source and ≥ 1 cross-difficulty factor per task | ✔ task 0 reads `club` (all four computations) and `care`; task 1 reads `club` and `stay`; all cross-read rows are seeded in `initial_state` and consistent with their own product charters |
| every ladder ≥ 3 tiers, stated in full in its rule, tiers distinct in outcome | ✔ structurally; the fall-through of four ladders is vacuous in effect — observation CG-8 |
| every tier's condition and outcome one that line of business actually holds | ✘ CG-9, CG-10, CG-11 |
| every factor proved to bear weight on its task's world against an honest baseline | ✔ all 31 factors bear weight; all 31 declared `baseline` values match what each policy's `baseline.rule` states for that input |
| instantiation-stage gates re-run on the final form | ✔ see below |

**Gates re-run on the final form**, from the repository root, unchanged from the entry snapshot
(nothing under `tasks/` was edited by this audit; the write domain was
`env/env_0000_online_travel_agency/audits/policy_task/air_ticketing_desk/` only):

```
check_extended.py      EXTENDED OK          (extended_policies=6, cross-cat=6, task_tools=6, tasks=2)
check_task_tools.py    TASK TOOL CONTRACT OK (6 tools)
replay_tasks.py        REPLAY OK            (0.json 16 acts, 1.json 12 acts; det/nonvac True, errs 0, match True)
check_solvability.py   SOLVABILITY OK       (0.json 4 gates/15 rows, 1.json 2 gates/10 rows)
check_compute.py       COMPUTE OK           (branches mean 47.00, steps mean 14.00, history_rows_max 45)
check_grounding.py     GROUNDING OK
check_cross_fire.py    SCOPE OK             (policies=6, hard-fails=0)
```

All seven are green on the final form, exactly as at entry. That is the qualification to enter this
audit and not a contradiction of its verdict: the gates prove structure, references and parsability,
and none of them can prove that a base sentence left unoverridden reaches a different conclusion from
the extended one that supersedes it in practice (CG-1 to CG-3), that a factor labelled `method` only
moves a coefficient (CG-7), that a replay figure written into a closure is arithmetically wrong
(F0-1), or that a tier's outcome is one no business in this line publishes (CG-9 to CG-11).

**Summary of the four relationships across the difficulty**

| relationship | task 0 | task 1 |
| --- | --- | --- |
| policy self-consistency | **SOURCE-POLICY RED** (CG-1, CG-2, CG-3) | PASS (1 observation) |
| the problem tree holds | **SOURCE-CHAIN RED** (F0-1, a false proof assertion; the tree itself is sound) | PASS |
| factors bear weight | **SOURCE-FACTOR RED** (CG-7) | **SOURCE-FACTOR RED** (CG-10, CG-11) |
| policy ↔ task unique solution | **PASS** | **PASS** |

Both tasks' scored solutions were reproduced blind, value for value — 114.19, 661.81, 2433.49,
1161.29 and 224.00, 623.80, together with every argument, owner, order and terminal state, and every
one of the 31 factor baselines and 6 whole-baseline fall-backs. The unique-solution relationship is
the one relationship this difficulty satisfies outright.

### write-domain disclosure

This audit's write domain was
`env/env_0000_online_travel_agency/audits/policy_task/air_ticketing_desk/` and no artifact under
`blueprint/`, `tasks/` or `erlbench/` was edited by it. One side effect must nevertheless be
recorded, because it is visible in `git status` and an auditor should not leave an unexplained mark:

`skills/erl-task-instantiate/scripts/replay_tasks.py` **writes to the task files it checks** — at
line 303 it rebuilds each `tasks/<id>.json` with a freshly computed `db_closure` and
`db_closure_matches_initial_state`. Step 4 of this skill requires the instantiation-stage gates to be
re-run on the final form, so running it was unavoidable, and it rewrote `tasks/0.json` and
`tasks/1.json`.

The rewrite is semantically empty and was verified to be so. Before and after, `0.json`'s
`db_closure` holds the same 25 rows across the same seven tables
(`air_booking_events` 13, `club_points_entries` 6, `air_bookings` 2, `customers` 1,
`club_memberships` 1, `care_policies` 1, `air_service_requests` 1) and `1.json`'s the same 26, with
`db_closure_matches_initial_state: true` in both cases and `REPLAY OK` on every run. What changes
between runs is only the **iteration order of the `db_closure` dictionary keys**, because the closure
is accumulated in a Python `set` whose order is not stable across processes. Three consecutive runs
produced three different file hashes (`bd4c042190ab2ca3`, `d0e12704a1c704f3`, `0bb6dd55a8f5fd16`) and
identical closure contents.

Nothing an audit reads for its verdict moved: `air.extended.yaml` still hashes to
`5168f11ad8285f15` and `task_tools.py` to `083ad6029813710d`, exactly the values in the brief, and
`frozen_time`, `user_scenario`, `initial_state`, `evaluation_criteria`, `computations`,
`prerequisite_closure`, `charter_scope` and `design_rationale` are untouched in both task files.

**CG-14 — Observation (toolchain, not this difficulty's artifacts).** A gate that rewrites the
artifact it checks, with an unstable key order, makes every mandated gate re-run produce a spurious
diff on `tasks/*.json` and makes a content hash useless as a freeze marker for those files. It is
recorded here because this skill's Step 4 obliges every auditor to trigger it, and because an
unexplained modification to a scored artifact is exactly the kind of mark an audit trail must not
carry silently. It bears on no relationship of either task.

---

# revision_2

Re-audit round 2. Revision 1 above is left exactly as written and nothing in it has been altered to
accommodate this round.

## charter_global_frozen (revision 2)

- freeze time: 2026-09-17 (session clock), written **before any GT of either task was read in this
  round**.
- auditor: the same independent source-layer auditor; round-1 derivations stand on disk untouched.
- frozen inputs and their hashes (sha256, first 16 hex), all **re-derived in full**, nothing carried
  forward by reference:
  - `air.extended.yaml` — `07d3d5dd37f16e65` (216105 bytes); round 1 was `5168f11ad8285f15` — **CHANGED**
  - `task_tools.py` — `38f157f2f3e9b84f` (21753 bytes); round 1 was `083ad6029813710d` — **CHANGED**
  - `0.masked.json` — `014336befb1db19c`; round 1 was `3d48dbd0c51356b7` — **CHANGED**
  - `1.masked.json` — `3f4f489240f7e22d` — unchanged, but its task file moved, so its per-task
    sections are re-derived in full regardless
- masked and unread while this section was written: `charter_scope`, `computations`, `db_closure`,
  `db_closure_matches_initial_state`, `design_rationale`, `evaluation_criteria`,
  `prerequisite_closure`, `required_documents`, `solvability_contract` on both tasks.
- entry conditions: the coordinator supplied the rebuilt masked views with hashes (re-computed here
  and matched) and the gate snapshot on the reworked form, all seven green. Complete.
- **Round-1 golds are stale.** The reworker reports the scored values moved in both tasks, which this
  round confirms. The round-1 revealed numbers were therefore treated as carrying no information
  about the round-2 answers, and both chains were derived from the policy and the world alone.
- The reworker's own figures and reasoning were withheld from this audit by the coordinator and were
  not sought. Its three specific claims — that CG-1 was closed by moving the world, that CG-2 was
  closed by removing a binding, and that two CG-7 factors were replaced rather than relabelled — were
  treated as claims to test.

### policy_conflict_scan (revision 2)

The base section of `air.extended.yaml` was re-compared key by key against
`blueprint/products/air.yaml` and is **verbatim identical** (all ten keys equal; the only added key
is `extended_policies`). The base copy has still not been rewritten.

The six policies keep their ids, subjects, `computes` and `target_tool`s. `air_credit_issue` is still
the subject of two policies (`air_ext_cancelled_ticket_credit`, `air_ext_lapsed_credit_carry_forward`)
computing different quantities through different tools; the pair of `(target_tool, computes)` claims
remains unique. The four base eligibility gates (`refund_review_approved`, `cancelled_before_issue`,
`refund_stage_reached`, `credit_still_valid`) are still inherited unweakened and are still
uncontradicted by any extended rule.

Cross-category reads: `club` in all six, `care` in `air_ext_cancelled_ticket_credit`, `stay` in
`air_ext_lapsed_credit_carry_forward`. Each declared category is genuinely exercised in the matching
`compute`; none reads an undeclared category.

**One conflict survives the rework, in a changed form: CG-1 (see `findings (revision 2)`).** The M
tasks' scopes remain mutually exclusive and jointly complete — policies 1–4 in one
prerequisite-connected component, 5–6 in the other.

### rule_compute_equivalence (revision 2)

Re-run over all six policies, binding by binding, both directions.

**Forward.** Every `compute` binding of all six policies carries a `compute_basis` quotation, and
every quotation was located verbatim in that policy's own `rule`. The new bindings introduced by the
rework all carry one: `money_collected` (policies 1 and 2), `extras_count` and the rewritten
`extras_added` (policy 2), `rework_share` / `service_fee_lines` / `service_fee_retained` /
`penalty_share` (policy 3), `traveller_pool` / `release_limit_share` / `correction_share`
(policy 4), `set_lapsed` (policies 5 and 6), and the rewritten `value_standing` (policy 6).

**Backward.** The two round-1 gaps are closed:

- **CG-6 closed.** Both `ticket_value` (policy 1) and `money_collected` (policy 2) are no longer
  unfiltered sums. Each is now the sum of exactly four event types — `air_fare_charge`,
  `air_ancillary_charge`, `air_change_fee_charge`, `air_penalty_charge` — and each policy's rule now
  carries the matching sentence: *"The money collected on the booking is the total of its fare, tax
  and service lines, its optional extras, its rework lines and its penalty lines, and never includes
  the travel credit the booking has issued or redeemed."* The `travel_credit` account no longer
  leaks into a `fare_paid` cap. A welcome side effect, verified below in the task-0 file: the two
  sibling writes of task 0 are now order-independent **by construction**, because policy 1's cap
  excludes `air_refund_payout` altogether.
- **CG-5 closed.** Both credit policies now test lapse. A new rule sentence, carried by policy 5 and
  policy 6 alike — *"The travel credit vouchers standing on the booking are taken as one set, and the
  set stands lapsed when the voucher most recently issued on it has lapsed; where that voucher has
  not lapsed the set is still redeemable as it stands and nothing is owed under this rule"* — is
  implemented as `set_lapsed: 1 if (voucher_count > 0 and DAYS(latest_expiry, NOW) > 0) else 0`,
  multiplied into each `result`. A booking whose most recent voucher is still live now yields zero
  from both policies instead of being charged and carried as though lapsed. This also answers the
  forward-looking half of F1-4: after the root write mints a live voucher, `latest_expiry` becomes
  that voucher's and `set_lapsed` falls to 0.

Every declared factor's ladder was re-checked in both faces: for all 31 declared factors, each tier
named in `factors[].ladder` is a sentence of the `rule` and a branch of the `decides` binding, and
each branch of every `decides` binding is a tier the rule states. No tier lives in only one face.

**One new tidiness defect** (observation CG-15): two policy parameters are now registered but
referenced by nothing — `air_ext_airline_tax_return.params.half_extras_share` and
`air_ext_lapsed_credit_carry_forward.params.recent_set_share`, both leftovers of tiers the rework
replaced.

### action_binding_and_uuids (revision 2)

Each `(target_tool, computes)` pair is still claimed by exactly one policy. The six uuid8s are
unchanged and were re-checked individually — `77ca3b84`, `4767edfd`, `dd7ecc26`, `2b680572`,
`efe635ea`, `f544c035`: eight lowercase hex each, all distinct, no shared prefix or tail, no
sequence, no batch derivation. **PASS.**

Docstrings: no docstring names another tool, states a position in a sequence, or carries an ordering
word. **CG-13 is closed**: every amount argument now reads *"given to the cent exactly as the
published terms produce it"* in place of round 1's *"already rounded half away from zero to the
cent"*, so the tool contract no longer states a rounding mode that contradicts the `RND` the policies
actually use. The contract now defers to the published terms, which is where the rounding point is
fixed.

Function bodies: re-read in full. Each of the six is one `ctx.make_id`, one `ctx.find` for the owner
reference, one unconditional `ctx.create` and a confirmation string. The only conditional in the
module is `owner[0]["customer_id"] if owner else ""`. **No tool tests a prerequisite, refuses, raises
or hints.** Owners are unchanged: four agent tools, two user tools, one in each component.

### prerequisite_graph (revision 2)

| blocked policy | problem | kind | gate | form | resolved_by |
| --- | --- | --- | --- | --- | --- |
| air_ext_cancelled_ticket_credit | air_ext_cancellation_penalty | value_input | penalty_withheld | state | withhold_cancellation_penalty_77ca3b84 |
| air_ext_cancelled_ticket_credit | air_ext_airline_tax_return | value_input | returned_to_card | state | return_airline_refunded_taxes_4767edfd |
| air_ext_pooled_credit_release | air_ext_cancelled_ticket_credit | value_input | pool_issued | state | issue_travel_credit_voucher_dd7ecc26 |
| air_ext_lapsed_credit_carry_forward | air_ext_credit_reissue_fee | value_input | reissue_fee_charged | state | charge_credit_reissue_fee_efe635ea |

Same four edges, same kinds, same gates, same forms as revision 1. Every `problem` points at another
extended policy id in this file; the graph is the same two acyclic trees; every `policy_source` is
verbatim locatable in the blocked policy's own `rule`; `form` is `state` on all four with no
`fallback_reason` anywhere; each `gate` names a binding that exists in the blocked policy's compute
and genuinely carries the depended-on write's value; each `resolved_by` creates exactly the row that
makes `effect` hold; no authoring-viewpoint phrasing. **PASS.**

### prerequisite_sentences (revision 2)

The three edges that passed in revision 1 carry unchanged sentences and were re-tested against the
reworked rules; all four points still hold and each still has exactly one write of this difficulty
bringing its state about. The fourth edge was rewritten:

**CG-4 closed.** `air_ext_pooled_credit_release`'s sentence now reads *"Value is released from the
traveller's pooled travel credit only after a travel credit stands issued **against a fare line of
the cancelled booking**."* The added qualifier is the discriminator round 1 found missing, and it is
record-visible rather than nominal:

- `issue_travel_credit_voucher_dd7ecc26` takes `source_event_id` = *"the reference number of the
  original **fare line** on the same booking whose value the voucher replaces"*, so its
  `air_credit_issue` row points at an `air_fare_charge` row;
- `reissue_lapsed_travel_credit_f544c035` takes `source_event_id` = *"the reference number of the
  lapsed **travel credit line** on the same booking whose value is carried onto the fresh voucher"*,
  so its `air_credit_issue` row points at another `air_credit_issue` row.

A reader who follows the sentence to the records can therefore tell the two apart by what the issue
line is raised against, without needing the voucher-code prefix the sentence does not mention. The
four-point test still passes: the ordering connective is "only after"; the side waited on is a
record-visible state in the words the ledger uses, with no action, performer or tool; no tool name,
policy id, snake_case token or row id appears; and the strength and scope match the edge's
`condition`, which was widened in step with the sentence to *"A travel credit issue line raised
against a fare line of the cancelled booking stands on that booking…"*. **Single reading. PASS.**

No rule carries a second wording of any dependency, no other problem's tool name or id, and no
depended-on rule restates the blocked policy's sentence. The base-rule sweep for ungrounded
cross-problem orderings returns what it did in revision 1: no task's tree rests on a base sentence.

### override_declarations (revision 2)

Sentence by sentence against every entry in every `base_policy_refs`, re-run in full.

**Declared overrides — now eight, each quoting a base sentence located verbatim in the base policy:**

- `air_ext_cancellation_penalty` over `air_cancel_refund` (the ladder sentence) — unchanged.
- `air_ext_airline_tax_return` over `air_refund_settlement` ×2, `air_baggage_fee`, `air_service_fee`.
  **CG-12 closed**: the last two `replaced_by` texts are no longer single tiers. They now name the
  governing sentence the rework added to the rule — *"What comes back of the optional extras sold on
  the booking follows what the airline did to the itinerary"* and *"What comes back of the agency
  service fee follows the traveller club card the traveller holds"* — each of which covers its whole
  ladder including the senior-tier branch that revision 1 found undeclared.
- `air_ext_cancelled_ticket_credit` over `air_credit_validity` **and, new, over
  `air_club_benefit_interaction`**. **CG-3 closed**: the `superseded_clause` is the verbatim base
  sentence *"A club benefit and a fare-brand inclusion never stack into a payment to the traveller: a
  bag already included in the brand is simply free, and the club benefit is not converted into
  value."*, replaced by *"What the traveller club card adds to the value placed on the voucher
  follows the tier held and how long the card has stood."* The uplift is now a declared override
  rather than a silent one.
- `air_ext_pooled_credit_release` over `air_agg_credit_pooling` — the transferability sentence, with a
  `replaced_by` rewritten to match the reworked ladder.
- `air_ext_credit_reissue_fee` over `air_credit_validity` **and, new, over
  `air_club_benefit_interaction`**. **F1-3 closed**: the `superseded_clause` is the verbatim base
  fragment *"the club tier held on the day the ticket is issued decides whether the agency service fee
  is waived and whether the first checked bag is carried free"*, replaced by *"What the traveller
  club card takes off the fee follows the tier held and the points standing on the card."*
- `air_ext_lapsed_credit_carry_forward` over `air_credit_validity` — `replaced_by` rewritten to match
  the reworked `value_standing` ladder.

**Undeclared overrides remaining.**

- **CG-2 closed by removal, and the removal is real.** `air_ext_cancelled_ticket_credit` no longer
  cites `air_baggage_fee` in `base_policy_refs`, its rule contains no sentence about optional extras,
  its `compute` contains no `extras_collected`, `extras_latest_date` or `extras_carry_share` binding,
  and its `factors` no longer contains `optional_extras_carry`. The booking's bag line can no longer
  reach the voucher by any path. The claim checks out.
- **CG-1 NOT closed.** `air_ext_airline_tax_return` still cites `air_evt_schedule_change_rights` with
  no `overwrite` against it, and `air_ext_cancellation_penalty` still carries a disruption ladder
  that confers a concession the base policy says the event does not confer. Moving task 0's world
  retired one half of the clash and activated the other. Set out in full in `findings (revision 2)`.

The three disguised forms were looked for again. The **0/1 multiplier** persists as a shape in
`rework_share`, `penalty_share`, `correction_share` and `extras_added`, but all four are now labelled
`parameter` where they scale, and the one that remains a `method` genuinely changes the algorithm.
No **dropped branch** and no **anonymous intermediate** was found: the two round-1 instances (CG-2,
CG-3) are closed by removal and by declaration respectively.

### factor_ladders (revision 2)

| policy | factors | parameter | method | genuine method after test | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| air_ext_cancellation_penalty | 5 | 4 | 1 | **1** (party_charging_basis) | club |
| air_ext_airline_tax_return | 5 | 4 | 1 | **1** (optional_extras_treatment) | club |
| air_ext_cancelled_ticket_credit | 5 | 4 | 1 | **1** (service_fee_basis) | club, care |
| air_ext_pooled_credit_release | 4 | 3 | 1 | **1** (traveller_pool_basis) | club |
| air_ext_credit_reissue_fee | 6 | 4 | 2 | **2** (lapse_clock_anchor, voucher_count_basis) | club |
| air_ext_lapsed_credit_carry_forward | 6 | 5 | 1 | **1** (lapsed_set_selection) | club, stay |

**CG-7 closed.** Every policy now has at least one factor whose tiers genuinely change how the
quantity is computed. Each of the five round-1 offenders was checked individually:

- `airline_disruption_transform` → **relabelled**. Now `airline_disruption_share`, `effect:
  parameter`. Its ladder is unchanged and is honestly a parameter: three coefficients on an
  already-determined penalty.
- `optional_extras_treatment` → **rewritten, and now a genuine method.** Tier 1 adds the extras *"at
  what they were charged"* (`extras_collected`); tier 2 adds them *"at the first checked bag rate of
  the fare brand held, counted once for each optional extra sold"* — `P('first_bag_fee_usd') *
  extras_count`, a different algorithm reading a different quantity and a brand parameter, not a
  coefficient on the charged amount; tier 3 adds nothing. This is the change that keeps policy 2's
  method floor.
- `money_collected_basis` → **relabelled and split**. The scaling half is now `rework_carry_share`,
  `effect: parameter`, deciding `rework_share`; `collected_basis` is plain arithmetic over it.
- `disrupted_penalty_treatment` → **relabelled and split** the same way into `disrupted_penalty_share`
  (`parameter`, deciding `penalty_share`), with `penalty_deduction` as plain arithmetic.
- `name_correction_carry` → **relabelled** to `name_correction_share`, `effect: parameter`.

Two genuinely new method factors were added in the places the relabelling would otherwise have
emptied, and both survive the test:

- `air_ext_cancelled_ticket_credit.service_fee_basis` — tier 1 retains *"the total of the service fee
  lines standing on the booking"* (a ledger sum), tier 2 *"the agency service fee of the fare brand
  held taken once for each traveller"* (a brand rate × a count), tier 3 *"taken once"* (the brand
  rate). Three different computations of the same input from different sources. Its `baseline`,
  `P('agency_service_fee_usd')`, is exactly what the policy's `baseline.rule` states — *"The agency
  service fee retained is the agency service fee of the fare brand held, taken once."*
- `air_ext_pooled_credit_release.traveller_pool_basis` — replacing `named_traveller_share`. Tier 1
  divides the open pool by the number of base-fare lines, tier 2 subtracts a per-traveller service fee
  from it, tier 3 takes it whole. Three different algorithms, not three coefficients.

So the reworker's claim that "two of the five were replaced rather than relabelled" is accurate in
substance, though the arithmetic is better described as: three relabelled, one rewritten in place
(`optional_extras_treatment`), one replaced (`named_traveller_share` → `traveller_pool_basis`), plus
one wholly new method factor (`service_fee_basis`).

Ladder structure otherwise: every ladder still has at least three tiers with the fall-through
counted, every tier is stated in the rule with its condition and its value or method, the tiers of
each ladder are pairwise disjoint as stated, every `decides` binding is an input rather than
`result`, and each factor's `bindings` are disjoint from its policy-mates'.

Business realism of conditions and outcomes, re-checked tier by tier:

- **CG-9 closed.** `journey_staleness_share` is now `journey_release_limit`, and the rework changes
  what it does rather than only its name. The rule now reads *"no more than the stale-journey limit
  of the pool available to the traveller is released **onto one itinerary**"*, and a new sentence
  states what becomes of the rest: *"Whatever is not released stays on the voucher it came off and
  keeps that voucher's own expiry."* A per-itinerary redemption limit that leaves the balance on the
  voucher is a treatment travel businesses do publish; round 1's objection was that the value was
  shrinking with the calendar and going nowhere, and that is answered.
- **CG-10 closed.** `air_ext_lapsed_credit_carry_forward.lapsed_set_selection` is inverted: where two
  or more vouchers stand lapsed, tiers 1 and 2 now carry **every** lapsed voucher forward
  (`lapsed_total`), and only the single-voucher fall-through takes the largest. The traveller can no
  longer be charged a fee computed on two vouchers and handed one. Policy 5's `voucher_count_basis`
  is unchanged and is now coherent with it.
- **CG-11 closed, by the CG-10 change rather than by its own.** `lead_traveller_share` is textually
  unchanged, but the quantity it acts on is not: `value_standing` is now the party-wide total rather
  than the caller's own single voucher, so taking a lead-traveller share of it is a first haircut on
  a party amount instead of a second haircut on an already-individual one. The stated ground —
  *"because the fresh voucher stands in the lead traveller's name alone"* — is now true of the
  quantity when the factor reaches it.
- **One new realism defect, CG-16**, in the reworked `lapsed_set_selection` tier 1: it deducts the
  brand's reissue fee a second time for each voucher beyond the first, having already been charged
  for them by policy 5. Set out in `findings (revision 2)` and demonstrated in `1.md`.
- **CG-8 stands as an observation, unchanged and not required to change.** The fall-throughs of
  `optional_extras_treatment`, `rework_carry_share`, `correction_share` and `disrupted_penalty_share`
  are still reached exactly when the amount they govern is nil. The tiers remain distinct as stated,
  the three-tier count is met, and no task turns on it.

### findings (revision 2)

**CG-1 — SOURCE-POLICY RED. NOT CLOSED. The undeclared conflict with
`air_evt_schedule_change_rights` survives; moving the world swapped which half of it bites.**

*Symptom.* For a booking the airline has moved, the base charter and the extended charter still reach
different conclusions about what the traveller gets, and no `overwrite` anywhere names the base
policy.

*Root cause.* The rework changed task 0's seed — notice `0960d251…` went from `schedule_change_minutes:
155` to `95`, below Economy Classic's threshold of 120 — instead of declaring an override.
`air_ext_cancellation_penalty` still carries a three-tier disruption ladder, and
`air_ext_airline_tax_return` still cites `air_evt_schedule_change_rights` in `base_policy_refs` while
naming it in no `overwrite`. The base policy has two operative sentences, and the ladder contradicts
both; the world move retired the clash with the first and activated the clash with the second.

*Evidence.* Base `air_evt_schedule_change_rights.rule`, sentence 2, inherited in full and unweakened:
*"A move smaller than the brand's threshold gives no right: a traveller who still wants to move pays
the brand's disruption rebooking fee, and a traveller who still wants to cancel is treated as a
voluntary cancellation."* Against it, `air_ext_cancellation_penalty.rule`: *"Where the airline has
recorded a move on the booking short of the schedule-change threshold of the fare brand held, the
penalty owed is reduced by a tenth."* Base says a sub-threshold move confers **no right** and that a
cancelling traveller is treated as an ordinary voluntary cancellation; extended reduces that
traveller's penalty by a tenth **on the ground that the sub-threshold move was recorded**. The
`overwrite` blocks of all six policies were enumerated: not one names
`air_evt_schedule_change_rights`.

*Demonstrated consequence.* On task 0's reworked world the sub-threshold tier is now the tier the
ladder actually takes (`largest_move_minutes = max(70, 45, 95) = 95`, and
`0.90 if largest_move_minutes > 0`), so the conflict is not merely latent — it decides the scored
number. Reading the base sentence as written gives `disruption_share = 1.00` and a penalty of
**228.38**; the extended ladder gives **205.54**. The difference then cascades through the whole tree.
Worked against this world in `0.md` § `policy_self_consistency (revision 2)`.

*Affected artifact.* `air.extended.yaml`, `air_ext_cancellation_penalty.overwrite` (missing entry) and
`air_ext_airline_tax_return.overwrite` (missing entry); the factor
`air_ext_cancellation_penalty.factors[airline_disruption_share]`; the scored parameter
`penalty_amount_usd` and, through it, `voucher_value_usd` and `released_credit_usd`.

*Relation to previous revisions.* Revision 1 recorded CG-1 on the **first** sentence of the same base
rule (a ≥threshold move confers a full refund to the card), demonstrated on a 155-minute notice. The
reworker's claim that CG-1 was "closed by moving the world" is half true: the 155→95 edit does close
the revision-1 demonstration, and that demonstration would no longer reproduce. It does not close the
finding, because the base policy legislates for sub-threshold moves too and the extended ladder has a
sub-threshold tier. A world move can only ever retire one tier of a ladder at a time; the conflict is
between two texts, and both texts are unchanged.

**CG-16 — SOURCE-FACTOR RED. NEW. The brand's reissue fee is recovered twice for every voucher beyond
the first.**

*Symptom.* A traveller with two lapsed vouchers is charged the reissue fee for the second voucher on
the fee line, and then has the same fee deducted again from the value carried forward.

*Root cause.* The rework fixed CG-10 by making `lapsed_set_selection` carry every lapsed voucher
forward, and paid for the extra vouchers with a new per-voucher deduction inside `value_standing` —
without noticing that `air_ext_credit_reissue_fee.voucher_count_basis` already charges the fee once
per voucher, and that the policy's own baseline already subtracts the whole charged fee at the end.

*Evidence.* `air_ext_credit_reissue_fee.rule`: *"Where two or more vouchers stand lapsed on the
booking, the fee is taken once for each voucher standing lapsed on it"*, implemented as
`fee_multiple: voucher_count if voucher_count >= 2 …`.
`air_ext_lapsed_credit_carry_forward.rule`: *"Where two or more vouchers stand lapsed on the booking
and the voucher most recently issued on it lapsed longer ago than the long-lapse term, the value
standing is the total of every lapsed voucher on the booking **less the credit reissue fee of the fare
brand that produced them for each voucher beyond the first**"*, implemented as
`value_standing: lapsed_total - P('credit_reissue_fee_usd') * (voucher_count - 1) …`; and the same
policy's baseline sentence, *"The value carried onto the fresh voucher is the largest lapsed travel
credit standing on the booking, **less the reissue fee charged on the booking**"*, implemented as the
final `- reissue_fee_charged`. The quantity deducted inside `value_standing` and the quantity charged
by policy 5 are the same named fee, `credit_reissue_fee_usd`, for the same vouchers.

*Demonstrated consequence.* Demonstrated against task 1's world in `1.md` § `factor_weight
(revision 2)`: the second voucher costs the traveller 84.00 on the fee line and a further 34.65 of
carried value, and removing the double-counted term alone moves the scored `carried_value_usd` from
1150.94 to 1185.59. No business recovers one published fee twice for one service.

*Affected artifact.* `air.extended.yaml`,
`air_ext_lapsed_credit_carry_forward.factors[lapsed_set_selection]` tier 1 and the `value_standing`
binding; the scored parameter `carried_value_usd`.

*Relation to previous revisions.* New in revision 2, introduced by the fix for CG-10. CG-10 itself is
genuinely closed; this is a fresh defect in its remedy.

**CG-15 — Observation. NEW. Two parameters are registered and referenced by nothing.**
`air_ext_airline_tax_return.params.half_extras_share` (0.5) and
`air_ext_lapsed_credit_carry_forward.params.recent_set_share` (0.5) appear in no `K(...)` of their
policies' `compute` or `factors`. Both are leftovers of tiers the rework replaced — the half-extras
share superseded by the first-checked-bag-rate method, and the recent-set share superseded by the
carry-everything tier. The convention is that a number appears once, in `params`, and `compute`
references it through `K`; a registered number that nothing references is a loose end a reader may
mistake for a live term. Bears on no relationship of either task.

**Round-1 findings: disposition.** Each was re-tested against the reworked artifacts, not against the
reworker's account.

| round-1 finding | claimed | verified state |
| --- | --- | --- |
| CG-1 / F0-2 | closed by moving the world | **NOT CLOSED** — conflict persists on the base rule's sub-threshold sentence, and is now the tier that decides the score |
| CG-2 / F0-3 | closed by removing a binding | **CLOSED** — `air_baggage_fee` dropped from refs; no extras sentence, binding or factor remains in policy 3 |
| CG-3 / F0-4 | closed by an edit | **CLOSED** — `air_club_benefit_interaction` now declared in policy 3's `overwrite` with the verbatim base sentence |
| F1-3 | closed by an edit | **CLOSED** — same declaration added to policy 5's `overwrite` |
| CG-4 | closed by an edit | **CLOSED** — prerequisite sentence now says "against a fare line of the cancelled booking", a discriminator the two writers' `source_event_id` contracts make record-visible |
| CG-7 / F0-5 | closed, two factors replaced | **CLOSED** — every policy now has ≥ 1 genuine `method`; three relabelled, one rewritten, one replaced, one added |
| CG-10 / F1-1 | closed by an edit | **CLOSED** — all lapsed vouchers now carried forward (but see CG-16) |
| CG-11 / F1-2 | closed by an edit | **CLOSED** — closed indirectly, by CG-10's change to the quantity the factor acts on |
| F0-1 | closed by an edit | verified in `0.md` § `source_gt_comparison (revision 2)` |
| CG-5 / F1-4 | closed by an edit | **CLOSED** — `set_lapsed` now tests `credit_expires_on` against `NOW` in both credit policies |
| CG-6 | closed by an edit | **CLOSED** — both caps now sum four named event types and exclude the credit account |
| CG-9 / F0-7 | closed by an edit | **CLOSED** — recast as a per-itinerary release limit, with the balance explicitly left on the voucher |
| CG-12 | closed by an edit | **CLOSED** — both `replaced_by` texts now name the governing sentence, covering every tier |
| CG-13 | closed by an edit | **CLOSED** — tool docstrings no longer state a rounding mode that contradicts `RND` |
| F1-5 | closed by an edit | **CLOSED** — the quantity is renamed "how long the credit has stood unclaimed", which is what the anchor measures |
| CG-8 | answered without a change | **ACCEPTED** — it was recorded as an observation in revision 1 and nothing about it regressed |
| CG-14 | outside the write domain | **ACCEPTED** — it is a finding against `skills/erl-task-instantiate/scripts/replay_tasks.py`, not against this difficulty |

**Nothing else regressed.** The three prerequisite sentences that passed in revision 1 are unchanged
and still pass; the uuid8s, owners and tool-body discipline are unchanged; the base section is still
verbatim; the two trees, their kinds and their orders are unchanged; and no factor that bore weight
in revision 1 has been left without weight in revision 2 (per-task evidence in each task file).

## closing_checklist (revision 2)

Written after both tasks had a frozen `source_derivation_frozen (revision 2)` and a
`source_gt_comparison (revision 2)`. Everything above this heading in the revision_2 block was
written before any GT of either task was read this round, apart from three arithmetic corrections
made while verifying this audit's own recomputations and before the reveal (two counterfactual
figures and one skip figure in `0.md`).

**The difficulty still does NOT close out.** Two of the four relationships fail — one carried forward
in changed form, one newly introduced by a remedy.

| item | state |
| --- | --- |
| per-task audit files correspond one-to-one; `_difficulty.md` alongside | ✔ |
| old revisions traceable and not rewritten | ✔ revision 1 stands untouched in all three files; revision 2 appended below it |
| every comparison section carries a PASS | ✘ task 0 carries SOURCE-POLICY (F0-8); task 1 carries SOURCE-FACTOR (F1-6) |
| extended policies fully covered; the M scopes pairwise disjoint | ✔ task 0 claims policies 1–4, task 1 claims 5–6 |
| task tools and GT closed | ✔ six tools, four and two |
| each task tool uses an independently generated, frozen uuid8 | ✔ unchanged and re-checked |
| every tree: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥ 1 `owner=user` write, no cycle | ✔ task 0: n=3, 3 edges; task 1: n=1, 1 edge; user write at each root |
| difficulty-wide `prerequisite` graph still a DAG | ✔ two disjoint trees, four edges |
| every computation declares a self-sufficient baseline giving a definite number different from gold | ✔ 119.00/205.54, 637.20/674.31, 2350.30/2363.55, 2363.55/1129.78, 75.00/224.00, 1676.00/1150.94 |
| 4–6 factors per computation, ≥ 2 `parameter`, ≥ 1 **genuine** `method` | ✔ **closed this round** — every policy now has at least one factor whose tiers change the algorithm |
| ≥ 1 multi-source and ≥ 1 cross-difficulty factor per task | ✔ task 0 reads `club` and `care`; task 1 reads `club` and `stay`; all cross-read rows seeded |
| every ladder ≥ 3 tiers, stated in full in its rule, tiers distinct in outcome | ✔ structurally; CG-8 stands as an observation |
| every tier's condition and outcome one that line of business actually holds | ✘ CG-16 |
| every factor proved to bear weight against an honest baseline | ✔ all 31 factors, both tasks |
| instantiation-stage gates re-run on the final form | ✔ all seven green: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK |

**Summary of the four relationships, revision 2**

| relationship | task 0 | task 1 |
| --- | --- | --- |
| policy self-consistency | **SOURCE-POLICY RED** (F0-8 / CG-1, carried forward in changed form) | PASS |
| the problem tree holds | **PASS** (was SOURCE-CHAIN in r1; F0-1 closed) | PASS |
| factors bear weight | **PASS** (was SOURCE-FACTOR in r1; CG-7 closed) | **SOURCE-FACTOR RED** (F1-6 / CG-16, new) |
| policy ↔ task unique solution | **PASS** | **PASS** |

**Movement between rounds.** Seventeen round-1 items were re-tested. Fifteen were claimed closed by
an edit: **fourteen of those are verified closed and one is not**. Of the remaining two, CG-8 was
correctly answered without a change and CG-14 is correctly outside this skill's write domain. The one
that is not closed is CG-1, where the rework moved the world instead of declaring the
override, which retired the demonstrated tier and activated the neighbouring one. **One is new** —
CG-16, introduced by the remedy for CG-10. Both tasks' scored solutions were again reproduced blind,
value for value (205.54 / 674.31 / 2363.55 / 1129.78 and 224.00 / 1150.94), together with every
argument, owner, order and terminal state, and all 31 factor baselines and 6 whole-baseline
fall-backs. The unique-solution relationship holds on both tasks in both rounds.

**Write-domain disclosure, revision 2.** As in revision 1, the only artifacts written by this audit
are the three files in this directory. `replay_tasks.py` again rewrote `tasks/0.json` and
`tasks/1.json` when Step 4's mandated gate re-run invoked it; the rewrite is again confined to
`db_closure` key ordering, with `clos 25/25` and `26/26` and `match True` unchanged. See CG-14 in
revision 1 and the `write-domain disclosure` section above it.

---

# revision_3

Re-audit round 3. Revisions 1 and 2 above are left exactly as written.

## charter_global_frozen (revision 3)

- freeze time: 2026-09-17 (session clock), written **before any GT of either task was read this
  round**.
- auditor: the same independent source-layer auditor.
- frozen inputs, all **re-derived in full**:
  - `air.extended.yaml` — `671ea0fdcc5b7516` (221926 bytes); round 2 was `07d3d5dd37f16e65` — **CHANGED**
  - `task_tools.py` — `02f3522169a00614` (21757 bytes); round 2 was `38f157f2f3e9b84f` — **CHANGED**
  - `0.masked.json` — `014336befb1db19c`, **unchanged from round 2**
  - `1.masked.json` — `3f4f489240f7e22d`, **unchanged since round 1**
- Because the charter and the tool module both moved, every charter-global section below is
  re-derived in full. Both worlds are byte-identical to round 2, but both task files moved, so each
  task's per-task sections are likewise re-derived in full.
- masked and unread while this section was written: the nine GT keys, on both tasks.
- entry conditions complete: rebuilt views with hashes (re-computed here and matched) and the
  seven-gate snapshot on the round-3 form, all green. The coordinator also reports `git diff` over
  `blueprint/` and `erlbench/` is empty; this audit independently re-confirmed that the base section
  of `air.extended.yaml` is still verbatim identical to `blueprint/products/air.yaml`.
- The reworker's figures and reasoning were withheld and not sought. Its claims were treated as
  claims to test.

### policy_conflict_scan (revision 3)

Base section verbatim identical to the blueprint product (all ten keys). Ids, subjects, `computes`
and `target_tool`s unchanged; `(target_tool, computes)` still unique per policy. The four base
eligibility gates still inherited unweakened and uncontradicted. Cross-category declarations
unchanged and all genuinely exercised.

**The round-2 conflict is resolved.** `air_evt_schedule_change_rights` is now named in
`base_policy_refs` **and** in `overwrite` on all three policies that read an airline notice —
`air_ext_cancellation_penalty`, `air_ext_airline_tax_return` and `air_ext_cancelled_ticket_credit` —
and in each the **two operative base sentences are both quoted as `superseded_clause`**. Details in
`override_declarations (revision 3)`. **No conflict survives this scan.** The M tasks' scopes remain
mutually exclusive and jointly complete.

### rule_compute_equivalence (revision 3)

Forward: every `compute` binding of all six policies carries a `compute_basis` quotation located
verbatim in that policy's own `rule`, including the round-3 additions —
`lapsed_recent_total` in `air_ext_lapsed_credit_carry_forward` and the rewritten `value_standing`
that consumes it.

Backward: the round-1 gaps (CG-5, CG-6) remain closed and were re-verified — `set_lapsed` still tests
`DAYS(latest_expiry, NOW) > 0` in both credit policies, and both `money_collected` bindings still sum
exactly four named event types and exclude the credit account. The new retention window is stated in
prose and implemented to match: *"The retention window is counted in whole calendar months back from
the handling date to the day each voucher was issued"* against
`SUM('air_booking_events','amount_usd', within_months=K('retention_window_months'), date_field='posted_date', event_type='air_credit_issue')`,
where the engine's window test is `0 ≤ MONTHS(posted_date, NOW) < 24`. Equivalent.

All 31 declared factors: every tier named in `factors[].ladder` is a sentence of the `rule` and a
branch of the `decides` binding, and every branch is a tier the rule states. No tier in only one face.

**CG-15 closed.** Every parameter of every policy is now referenced by a `K(...)` in its own
`compute` or `factors`; the two orphans of round 2 (`half_extras_share`, `recent_set_share`) are
gone, and the one parameter added this round (`retention_window_months`) is referenced.

### action_binding_and_uuids (revision 3)

The six uuid8s are unchanged and were re-checked individually — `77ca3b84`, `4767edfd`, `dd7ecc26`,
`2b680572`, `efe635ea`, `f544c035`: eight lowercase hex each, all distinct, no shared prefix or tail,
no sequence, no batch derivation. **PASS.**

Function bodies re-read in full: six functions, each one `ctx.make_id`, one `ctx.find`, one
unconditional `ctx.create`, one confirmation string. The module's only conditionals are the six
`owner[0]["customer_id"] if owner else ""` fallbacks; there is no `raise`, no `except`, no `assert`.
**No tool judges a prerequisite.** Owners unchanged: four agent, two user, one user tool in each
component.

Docstrings carry no other tool's name and no cross-tool ordering instruction. **CG-13 remains
closed**: all six amount arguments read *"given to the cent exactly as the published terms produce
it"*, and the phrase *"half away from zero"* appears nowhere in the module.

**CG-4 remains closed**, and the discriminator it rests on is intact: `issue_travel_credit_voucher_dd7ecc26`
still takes *"the original fare line on the same booking whose value the voucher replaces"* while
`reissue_lapsed_travel_credit_f544c035` still takes *"the lapsed travel credit line on the same
booking"*, so the prerequisite sentence's "against a fare line of the cancelled booking" still picks
out exactly one of the two `air_credit_issue` writers.

### prerequisite_graph and prerequisite_sentences (revision 3)

The same four edges, kinds, gates, forms and `resolved_by` as revisions 1 and 2. Every `problem`
points at another extended policy id in this file; the graph is the same two acyclic trees; **all
four `policy_source` sentences were re-tested and are verbatim substrings of the blocked policy's own
`rule`**; `form` is `state` on all four and `fallback_reason` is absent from all four, which is
correct; each `gate` names a live binding; each `resolved_by` creates exactly the row that makes
`effect` hold; no authoring-viewpoint phrasing. The four-point test passes on each sentence, and each
waited-on state is brought about by exactly one write of this difficulty. **PASS.**

### override_declarations (revision 3)

Ten declared overrides now, up from eight. Every `superseded_clause` was checked as a verbatim
substring of the named base policy's `rule`, and **every `replaced_by` was checked as a verbatim
substring of the declaring policy's own `rule`** — all ten pass both tests.

The six carried over from round 2 (`air_cancel_refund` on policy 1; `air_refund_settlement` ×2,
`air_baggage_fee`, `air_service_fee` on policy 2; `air_credit_validity` and
`air_club_benefit_interaction` on policy 3; `air_agg_credit_pooling` on policy 4;
`air_credit_validity` and `air_club_benefit_interaction` on policy 5; `air_credit_validity` on
policy 6) are unchanged and still pass.

**The four added this round are the CG-1 remedy**, two on each of the three notice-reading policies:

| policy | superseded_clause (verbatim in base) | replaced_by (verbatim in the policy's rule) |
| --- | --- | --- |
| air_ext_cancellation_penalty | *"An airline schedule move at or beyond the threshold … or to be refunded in full to the original form of payment whatever the brand's ordinary refund form."* | *"What an airline move recorded on the booking does to the penalty owed follows how large that move was against the schedule-change threshold of the fare brand held, whether or not the move was large enough to give the traveller a right of its own."* |
| air_ext_cancellation_penalty | *"A move smaller than the brand's threshold gives no right: a traveller who still wants to move pays the brand's disruption rebooking fee, and a traveller who still wants to cancel is treated as a voluntary cancellation."* | (the same governing sentence) |
| air_ext_airline_tax_return | both of the above | *"What the airline's notices standing on the booking add to the amount returned follows how many of them the booking received in the recent window, whether or not any one of them was large enough to give the traveller a right of its own."* |
| air_ext_cancelled_ticket_credit | both of the above | *"What an airline notice standing on the booking does to the penalty taken off the value placed on the voucher follows whether the airline cancelled a segment or only moved one, whether or not the move was large enough to give the traveller a right of its own."* |

This is the right shape and it is complete in the respect round 2 found wanting. Round 2's defect was
that the base rule has **two** operative sentences — one for a move at or beyond the threshold and one
for a move below it — and that a world move can only ever retire one of them; the remedy now
supersedes **both**, on **every** policy that reads a notice. Each `replaced_by` is a governing
sentence covering a whole ladder rather than one tier, and each carries the clause *"whether or not
the move was large enough to give the traveller a right of its own"*, which is precisely the
proposition the base sentences asserted and the extended ladders deny. The merged semantics are
unique: once both base sentences are superseded on a policy, that policy's own ladder is the only rule
in force for what an airline move does to its quantity. **CG-1 closed.**

The remaining sentences of `air_evt_schedule_change_rights` are inherited and were each tested for a
residual conflict:

- *"Several notices on the same booking are not added together; the largest single move on any one
  segment decides the right…"* — `air_ext_cancellation_penalty` uses
  `MAX('air_booking_events','schedule_change_minutes', …)`, the largest single move, consistent.
  `air_ext_airline_tax_return` counts notices, but for a goodwill addition rather than for "the
  right" this sentence scopes itself to, and its declared `replaced_by` states outright that what the
  notices add "follows how many of them the booking received". No conflict.
- *"Where the rebooking obliges the traveller to stay overnight…"* — not engaged; no rebooking.
- *"A booking that has received more than the threshold count of notices in the last ninety days is
  passed to the disruption desk rather than rebooked again…"* — not engaged on either world (task 0's
  latest notice is 2026-05-14, outside 90 days of 2026-09-17), and it governs rebooking, not
  cancellation.
- *"An airline cancellation of the segment is always treated as a move beyond the threshold, whatever
  its recorded minutes."* — inherited and **not** superseded. See observation CG-17.

### factor_ladders (revision 3)

| policy | factors | parameter | method | genuine method after test | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| air_ext_cancellation_penalty | 5 | 4 | 1 | 1 (party_charging_basis) | club |
| air_ext_airline_tax_return | 5 | 4 | 1 | 1 (optional_extras_treatment) | club |
| air_ext_cancelled_ticket_credit | 5 | 4 | 1 | 1 (service_fee_basis) | club, care |
| air_ext_pooled_credit_release | 4 | 3 | 1 | 1 (traveller_pool_basis) | club |
| air_ext_credit_reissue_fee | 6 | 4 | 2 | 2 (lapse_clock_anchor, voucher_count_basis) | club |
| air_ext_lapsed_credit_carry_forward | 6 | 5 | 1 | 1 (lapsed_set_selection) | club, stay |

**CG-7 remains closed.** Each of the six surviving `method` factors was re-tested against the
relabel/rewrite test and each still changes how the quantity is computed rather than only its
coefficient. Every ladder still has at least three tiers stated in full in its rule, pairwise
disjoint as stated, with `decides` an input rather than `result` and disjoint `bindings` within each
policy.

**CG-16 closed, and closed by removal.** `air_ext_lapsed_credit_carry_forward.value_standing` tier 1
no longer subtracts `P('credit_reissue_fee_usd') × (voucher_count − 1)`. It now reads
`lapsed_recent_total` — *"the total of the lapsed vouchers issued on the booking within the retention
window"* — so the brand's reissue fee is charged once by `air_ext_credit_reissue_fee` and deducted
once by the baseline's `− reissue_fee_charged`, and nowhere else. The policy's baseline rule now says
so in terms, as a general proposition rather than a patch: *"The reissue fee is met once, out of the
value being carried forward, and is never taken a second time out of the vouchers it was charged
for."* That sentence is the right kind of remedy — it states the principle the defect violated, so a
later ladder cannot reintroduce it silently.

**CG-10 and CG-11 remain closed.** `lapsed_set_selection` tiers 1 and 2 still carry more than the
largest voucher where two or more stand lapsed (tier 3, the fall-through, is the single-voucher
case), so the traveller is not charged for vouchers she does not get back; and `lead_traveller_share`
still acts on a party-wide `value_standing`, so its stated ground remains true of the quantity it
reaches.

Business realism of conditions and outcomes re-checked tier by tier; CG-9's per-itinerary release
limit, CG-10's carry-everything tiers and CG-11's party share all still read as treatments this line
of business publishes. **One new observation, CG-18**, on the discriminating power the CG-16 remedy
costs `lapsed_set_selection` on task 1's world. CG-8 stands unchanged as an observation.

### findings (revision 3)

**CG-17 — Observation. NEW. One inherited sentence of `air_evt_schedule_change_rights` is not
implemented by the policy that would need it.**
Base, inherited and not superseded by any of the ten declared overrides: *"An airline cancellation of
the segment is always treated as a move beyond the threshold, whatever its recorded minutes."*
`air_ext_cancellation_penalty` decides its disruption tier from
`largest_move_minutes: MAX('air_booking_events','schedule_change_minutes', event_type='air_schedule_change_notice')`
alone, and never reads `reason_code`. On a booking carrying a notice with
`reason_code='airline_cancellation'` and small recorded minutes, base directs the at-or-beyond-threshold
treatment while the compute would select the sub-threshold tier. Its two sibling policies do read
`reason_code='airline_cancellation'`, so the gap is confined to policy 1. **Not a red light**: neither
seeded world carries an `airline_cancellation` notice — task 0's three notices are all
`involuntary_schedule_change` and task 1's booking carries no notice at all — so no consequence is
demonstrable on either world. Recorded because it is the one sentence of that base rule the CG-1
remedy leaves unreconciled. Bears on: neither task's score.

**CG-18 — Observation. NEW. The CG-16 remedy leaves `lapsed_set_selection`'s first two tiers
numerically indistinguishable on the only world where the policy acts.**
Tier 1 now selects `lapsed_recent_total` (vouchers issued inside the 24-month retention window) and
tier 2 `lapsed_total` (every lapsed voucher). On task 1 the two vouchers were issued 21 and 20 months
before the handling date, so both fall inside the window and the two tiers select the **same value**,
3116.00. The `months_since_lapse > long_lapse_months` test that separates them therefore decides
nothing on this task: a reader who took tier 2 instead of tier 1 would score identically. In round 2
the same two tiers differed by 75.00 on this world. **Not a red light**: the tiers select different
*methods* as written (a windowed sum against an unwindowed one), the ladder still has three tiers, and
the factor as a whole still bears weight against its `largest_voucher` baseline. Recorded because the
remedy for CG-16 bought correctness at the cost of this ladder's discriminating power on the only
world that exercises it. Bears on: task 1, as a loss of test power rather than a wrong answer.

**Round-2 findings: disposition.** Each re-tested against the artifacts, not the reworker's account.

| round-2 finding | claimed | verified state |
| --- | --- | --- |
| CG-1 / F0-8 | closed by declaration on all three notice-reading policies | **CLOSED** — both operative base sentences quoted verbatim as `superseded_clause` on each of the three, each `replaced_by` a governing sentence present verbatim in that policy's rule and covering a whole ladder |
| CG-16 / F1-6 | closed by removing the per-voucher deduction | **CLOSED** — the deduction is gone from `value_standing`; fee accounted once by the fee policy and once by the baseline, with a general anti-double-recovery sentence added to the baseline rule |
| CG-15 | closed | **CLOSED** — no policy now carries an unreferenced parameter |

**Regression sweep.** The fourteen items verified closed in revision 2 were each re-tested on the
round-3 artifacts and **all fourteen remain closed**: CG-2 (policy 3 still cites no `air_baggage_fee`
and carries no extras sentence, binding or factor), CG-3 and F1-3 (both `air_club_benefit_interaction`
overrides intact), CG-4 (sentence and tool discriminator intact), CG-5 / F1-4 (`set_lapsed` in both
credit policies), CG-6 (both caps still filtered to four event types), CG-7 / F0-5 (every policy still
carries a genuine `method`), CG-9 / F0-7 (per-itinerary release limit intact), CG-10 / F1-1 and
CG-11 / F1-2 (carry-everything tiers and party-wide `value_standing` intact), CG-12 (governing
`replaced_by` sentences intact), CG-13 (rounding wording intact), F1-5 (the renamed "stood unclaimed"
quantity intact), and F0-1 (verified at the reveal, in each task file). The base section is still
verbatim, the uuid8s, owners and tool-body discipline are unchanged, both trees and their orders are
unchanged, and no factor that bore weight in revision 2 is without weight in revision 3.

## closing_checklist (revision 3)

Written after both tasks had a frozen `source_derivation_frozen (revision 3)` and a
`source_gt_comparison (revision 3)`. Everything above this heading in the revision_3 block was written
before any GT of either task was read this round, apart from one arithmetic correction to an
alternative-candidate figure in `1.md`, made while verifying this audit's own recomputations.

**The difficulty CLOSES OUT.** All four relationships PASS on both tasks.

| item | state |
| --- | --- |
| per-task audit files correspond one-to-one; `_difficulty.md` alongside | ✔ |
| old revisions traceable and not rewritten | ✔ revisions 1 and 2 stand untouched in all three files; revision 3 appended below them |
| every comparison section carries a PASS | ✔ **both tasks, all four relationships** |
| extended policies fully covered; the M scopes pairwise disjoint | ✔ task 0 claims policies 1–4, task 1 claims 5–6; each scope spans a whole problem tree |
| task tools and GT closed | ✔ six tools, four and two, each `(target_tool, computes)` unique |
| each task tool uses an independently generated, frozen uuid8 | ✔ `77ca3b84`, `4767edfd`, `dd7ecc26`, `2b680572`, `efe635ea`, `f544c035` |
| every tree: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥ 1 `owner=user` write, no cycle | ✔ task 0: n=3, 3 edges; task 1: n=1, 1 edge; a user write at each root |
| difficulty-wide `prerequisite` graph still a DAG, no cross-task cycle | ✔ two disjoint trees, four edges |
| every computation declares a self-sufficient baseline giving a definite number different from gold | ✔ 119.00/205.54, 637.20/674.31, 2350.30/2363.55, 2363.55/1129.78, 75.00/224.00, 1676.00/1185.59 |
| 4–6 factors per computation, ≥ 2 `parameter`, ≥ 1 genuine `method` | ✔ 5/5/5/4 and 6/6, every computation with a genuine `method` |
| ≥ 1 multi-source and ≥ 1 cross-difficulty factor per task | ✔ task 0 reads `club` and `care`; task 1 reads `club` and `stay`; all cross-read rows seeded and charter-consistent |
| every ladder ≥ 3 tiers, stated in full in its rule, tiers distinct in outcome | ✔ structurally; observations CG-8 and CG-18 stand |
| every tier's condition and outcome one that line of business actually holds | ✔ |
| every factor proved to bear weight against an honest baseline | ✔ all 31 factors across both tasks |
| instantiation-stage gates re-run on the final form | ✔ EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK |

**Summary of the four relationships, revision 3**

| relationship | task 0 | task 1 |
| --- | --- | --- |
| policy self-consistency | **PASS** (was SOURCE-POLICY in r1 and r2) | **PASS** |
| the problem tree holds | **PASS** | **PASS** |
| factors bear weight | **PASS** | **PASS** (was SOURCE-FACTOR in r1 and r2) |
| policy ↔ task unique solution | **PASS** | **PASS** |

**Movement across the three rounds.** Round 1 raised eight findings and nine observations; round 2
verified fourteen closed, found CG-1 not closed and CG-16 newly introduced by a remedy; round 3
verifies all three outstanding items closed — CG-1 by declaring the override on every policy that
reads an airline notice, with **both** operative base sentences superseded rather than one tier of the
world moved; CG-16 by removing the per-voucher fee deduction and stating the anti-double-recovery
principle in the baseline rule; CG-15 by removing the two orphan parameters — and confirms by direct
re-test that the fourteen previously closed items are all still closed.

Two observations are new this round and neither is a red light: **CG-17**, one inherited sentence of
`air_evt_schedule_change_rights` (*"An airline cancellation of the segment is always treated as a move
beyond the threshold, whatever its recorded minutes"*) that `air_ext_cancellation_penalty` does not
implement, undemonstrable because neither world carries an `airline_cancellation` notice; and
**CG-18**, the discriminating power the CG-16 remedy costs `lapsed_set_selection` on task 1's world,
where the 24-month retention window excludes nothing and its first two tiers select the same value.

**Blind derivation across all three rounds.** Every scored value of both tasks was re-derived
independently in each round before any GT was read, and matched GT exactly every time: revision 1
(114.19 / 661.81 / 2433.49 / 1161.29 and 224.00 / 623.80), revision 2 (205.54 / 674.31 / 2363.55 /
1129.78 and 224.00 / 1150.94) and revision 3 (205.54 / 674.31 / 2363.55 / 1129.78 and 224.00 /
1185.59), together with every argument, owner, order and terminal field, and every factor baseline and
whole-baseline fall-back. The unique-solution relationship held in all three rounds; what the three
rounds moved was the policy's self-consistency and the honesty of its factor labels and ladders.

**Write-domain disclosure, revision 3.** Unchanged in kind from revisions 1 and 2: the only artifacts
written by this audit are the three files in this directory, and `replay_tasks.py` again rewrote
`tasks/0.json` and `tasks/1.json` when Step 4's mandated gate re-run invoked it, confined to
`db_closure` key ordering with `clos 25/25` and `26/26` and `match True` unchanged. See CG-14 and the
`write-domain disclosure` section in revision 1.

**This difficulty passes the source-layer audit.**

---

# revision_4

Re-audit round 4. Revisions 1–3 above are left exactly as written.

## charter_global_frozen (revision 4)

- freeze time: 2026-09-17 (session clock), written **before any GT of either task was read this
  round**.
- frozen inputs, all **re-derived in full**:
  - `air.extended.yaml` — `375d1cd4ff2273f9` (233569 bytes); round 3 was `671ea0fdcc5b7516` — **CHANGED**
  - `task_tools.py` — `02f3522169a00614`, **unchanged from round 3**
  - `0.masked.json` — `014336befb1db19c`, **unchanged since round 2**
  - `1.masked.json` — `3f4f489240f7e22d`, **unchanged since round 1**
- masked and unread: the nine GT keys, on both tasks.
- **A deliberate abstention.** This round originates in a separate agent's blind audit of the
  published KB, whose reports sit at `env/env_0000_online_travel_agency/audits/policy_kb/air_ticketing_desk/`
  and `env/env_0000_online_travel_agency/audits/runtime_context/air_ticketing_desk/`. Those reports may carry
  figures that agent derived from the documents, and a scored value reaching this audit from any side
  file before the freeze would void this round's blind derivation exactly as reading `tasks/*.json`
  would. **They were therefore not opened before the freeze.** The findings they raise reached this
  audit only as the coordinator's prose summary of the defect class, which carries no figure. They
  are another body's conclusions and this audit is not bound by them; what is re-derived below is the
  source layer on its own terms.
- entry conditions complete: rebuilt views with hashes (re-computed and matched) and the gate
  snapshot on the round-4 form, now eight gates including `check_traceability.py`, all green. The
  coordinator reports `git diff` over `blueprint/` and `erlbench/` empty; this audit independently
  re-confirmed the base section of `air.extended.yaml` is still verbatim identical to
  `blueprint/products/air.yaml`.

### the defect this round answers

The KB audit's finding, as this audit reconstructs it from the artifacts: a reader of the published
documents could establish every *tier* correctly — which share, which loading, which uplift — and
still not reach the scored number, because nothing said **in what order the tiers' outcomes enter the
result**. Whether a share acts on the flat fee before or after a dollar loading is added, whether two
shares compose successively or combine into one rate, whether a dollar amount is added before or
after a share, whether two uplifts are applied in turn or summed — each of these changes the answer,
and none of it was stated anywhere a reader could reach.

That is a source-layer defect, not a rendering one: a document cannot publish an order the charter
never fixed. The round-4 rework accordingly writes the order into the charter. **This audit's job is
to decide whether the order is now stated, in business words, strongly enough that a reader applying
every tier correctly reaches the compute's number — and whether the R0-1 compute move has left rule,
baseline, ladder and proof fields all saying the same thing.**

### composition_and_assembly_order (revision 4)

This section is new this round and is the heart of it.

**1. A shared composition convention, present in all twelve places.** One sentence now appears
verbatim in the `baseline.rule` **and** the `rule` of **all six** policies:

> *"Where more than one share is taken on the same figure, the shares act one after another, each on
> the figure the one before it gives, and are never combined into a single rate; where more than one
> uplift is added to the same figure, the uplifts are combined into a single uplift and the figure is
> increased once by that total."*

Checked as a verbatim substring of all six `baseline.rule` values and all six `rule` values — twelve
of twelve. This is R1-2(b), and it replaces what were two divergent local conventions with one.

**2. Per-computation stage sentences.** Each policy's `baseline.rule` now names its own stages and
the order they assemble in, in business words:

| policy | stage sentence (abridged) | `result` it determines |
| --- | --- | --- |
| air_ext_cancellation_penalty | *"The penalty owed for one traveller is settled in full before it is taken for the party, and the figure that party charge gives is the penalty withheld. Anything owed in dollars for one traveller enters the penalty owed for one traveller, and within that figure a share is taken on the flat cancellation penalty before anything is added to it in dollars; anything taken as a share of the penalty as a whole acts on the penalty withheld."* | `(flat × notice_share + dollars) × travellers × share × share` |
| air_ext_airline_tax_return | *"The amount the tax lines are returned at is settled first, and the amount returned is that figure with anything held back taken off it and anything else that comes back added to it."* | `tax_returned_at − holdback + additions` |
| air_ext_cancelled_ticket_credit | *"The value the booking's lines leave is settled first, and the value placed on the voucher is that figure once every share and every uplift that bears on it has been taken."* | `residual × (1+uplift) × (1−share)` |
| air_ext_pooled_credit_release | *"The pool available to the traveller is settled first, and the value released is that pool once every share and every uplift that bears on it has been taken, with anything added in dollars added last of all."* | `pool × share × (1+bonus) + dollars` |
| air_ext_credit_reissue_fee | *"The fee is settled in two stages. The tariff component is settled first … taken at whatever loading … and then taken as many times as the fee falls due on the booking. The fee charged is that tariff component with anything added to it in dollars, added once for the booking and never once for each voucher, and with any relief then taken as a share of the whole."* | `(fee × loading × multiple + dollars) × (1−relief)` |
| air_ext_lapsed_credit_carry_forward | *"The value carried onto the fresh voucher is that value standing once every share and every uplift that bears on it has been taken, with anything taken off in dollars — the reissue fee charged on the booking above all — taken off last of all, after every share and every uplift."* | `(standing × share × share × (1+uplifts) − dollars)` |

**3. Every factor sentence names the stage its outcome enters, by the baseline's own name for it.**
Checked tier by tier over all 31 factors, in the `rule` prose as well as the `ladder`. Examples where
round 3 was silent: *"the flat cancellation penalty is taken at the early-notice share **in settling
the penalty owed for one traveller**"*; *"the once-reworked loading is added **to the penalty owed for
one traveller**"*; *"**the penalty withheld** is halved"*; *"the senior-member relief is taken **as a
share off the penalty withheld**"*; *"the conversion markup … is held back **from the amount the tax
lines are returned at**"*; *"no uplift is added **to the value the booking's lines leave**"*; *"**the
tariff component** is taken once for each voucher standing lapsed on it"*; *"nothing is added **to the
fee charged** for the value standing"*; *"nothing is taken off **in dollars** for the agency service
fee"*. The stage names in the factor sentences are the stage names the baselines define — the two
faces share a vocabulary, which is what lets a reader assemble them.

**4. The decisive test: is the order load-bearing, and does the stated order give the compute's
number?** A convention that changes no number is decoration. Each statement was tested by computing
the alternative reading it forbids, on the seeded worlds:

| statement | as stated | the reading it forbids | Δ |
| --- | --- | --- | --- |
| P1 share on the flat penalty **before** dollars are added | **205.54** | dollars first: 196.99 | 8.55 |
| P1 shares act one after another, **never combined into a single rate** | **205.54** | combined `1−0.10−0.05`: 204.34 | 1.20 |
| P2 markup held back **from the amount the tax lines are returned at** | **676.23** | on the lines as posted: 674.31 | 1.92 |
| P4 dollars **added last of all** | **1129.03** | added before the share: 1122.59 | 6.44 |
| P5 dollars **added once for the booking**, never per voucher | **224.00** | per voucher: 280.00 | 56.00 |
| P5 relief **taken as a share of the whole** | **224.00** | relief on the tariff only: 248.00 | 24.00 |
| P6 dollars **taken off last**, after every share and uplift | **1185.59** | taken off first: 1322.24 | 136.65 |
| P6 uplifts **combined into a single uplift** | **1185.59** | applied successively `×1.06×1.04`: 1188.73 | 3.14 |

Every one of the eight is load-bearing: read the other way, each gives a different scored number. And
in every case the reading the charter now states is the reading the `compute` implements. **The
assembly order is stated, it is stated in business words, and it is sufficient.**

**5. Was the class closed, or three instances?** The reworker claims the class. Tested by taking all
six computations, not the three the KB audit demonstrated: all six carry the shared convention in
both faces; all six have a stage sentence in their baseline; all 31 factors name their stage. The two
computations the KB audit did not demonstrate against — `penalty_amount_usd` and `reissue_fee_usd` —
are covered as fully as the three that were, and `reissue_fee_usd`'s stage sentence is the strongest
of the six, since it pre-empts two distinct misreadings by name (per-voucher dollar loadings, and
relief on the tariff rather than the whole). **The class is closed, not the instances.**

### rule_compute_equivalence (revision 4)

Forward and backward over all six policies, binding by binding. Every `compute` binding carries a
`compute_basis` quotation located verbatim in that policy's own `rule`, including the two bindings
new this round: `tax_returned_at` and `conversion_holdback`.

**R0-1 closed, and closed in the direction that makes rule and compute agree.** Round 3's
`air_ext_airline_tax_return` said in prose that the markup is *"held back from the tax lines
returned"* while its compute took the markup on `tax_base` — the lines **as posted**, before the
holding share. The two faces disagreed, and the rule was the one stating the business intent. The
rework moved the **compute**: it now names the intermediate the rule always implied,
`tax_returned_at: tax_base * holding_share`, and takes the holdback on it,
`conversion_holdback: tax_returned_at * conversion_holdback_rate`. The rule's own wording was
tightened in step, from *"held back from the tax lines returned"* to *"held back from the amount the
tax lines are returned at"*, which is the baseline's name for that stage. Rule, baseline, ladder and
compute now use one name for one figure. This moves the scored value, and the movement is worked out
in `0.md`.

R1-1 and R1-2(a) were closed the other way — by moving the **rule** to match the compute, which is
the right direction where the compute was already doing what the business does and only the prose was
silent or loose: `air_ext_credit_reissue_fee`'s baseline now states the two-stage settlement and the
once-for-the-booking rule for dollar loadings, and
`air_ext_lapsed_credit_carry_forward`'s baseline now states that dollars come off last. Neither moves
a number; both make an existing number derivable.

The round-1 and round-3 conclusions all still hold on re-test: `set_lapsed` still tests
`credit_expires_on` against `NOW` in both credit policies (CG-5); both `money_collected` bindings
still sum four named event types and exclude the credit account (CG-6); every ladder's tiers are
stated in full in the rule and implemented in `compute`, with no tier living in only one face; and no
policy carries an unreferenced parameter (CG-15).

### action_binding_and_uuids (revision 4)

`task_tools.py` is **unchanged from round 3** (`02f3522169a00614`) and was re-read in full to confirm
it: six functions, the same six uuid8s — `77ca3b84`, `4767edfd`, `dd7ecc26`, `2b680572`, `efe635ea`,
`f544c035`, all distinct, no shared prefix or tail, no sequence; each body one `ctx.make_id`, one
`ctx.find`, one unconditional `ctx.create`, one confirmation string; the module's only conditionals
the six owner-reference fallbacks; no `raise`, no `except`, no `assert`; **no tool judges a
prerequisite**; four agent tools and two user tools, one user tool in each component; CG-13's
rounding wording intact on all six amount arguments; and CG-4's discriminator intact — the issue tool
still takes *"the original fare line"* and the reissue tool *"the lapsed travel credit line"*.

### prerequisite_graph and prerequisite_sentences (revision 4)

The same four edges, kinds, gates, forms and `resolved_by`. All four `policy_source` sentences
re-tested as verbatim substrings of the blocked policy's own `rule`; `form` is `state` on all four
with `fallback_reason` absent from all four; the four-point test passes on each; each waited-on state
is brought about by exactly one write of this difficulty. Two acyclic trees. **PASS.**

### override_declarations (revision 4)

Eleven declared overrides now, up from ten. Every `superseded_clause` re-checked as a verbatim
substring of the named base policy's rule, and every `replaced_by` as a verbatim substring of the
declaring policy's own rule — **eleven of eleven pass both tests**.

The ten from round 3 are unchanged and still pass, including the four that closed CG-1 (both
operative sentences of `air_evt_schedule_change_rights` superseded on each of the three
notice-reading policies).

**The one added this round closes a policy-side note round 3 had left open.** Base
`air_cancel_refund` carries a second sentence about the agency service fee, parallel to the one in
`air_service_fee`: *"Taxes and carrier fees that the airline itself refunds are returned even on a
non-refundable brand, and the agency service fee is not."* Round 3's
`air_ext_airline_tax_return` returned the service fee to club members while overriding only
`air_service_fee`, leaving this sentence inherited and contradicted. It is now quoted verbatim as a
`superseded_clause` and replaced by the governing sentence already in the rule, *"What comes back of
the agency service fee follows the traveller club card the traveller holds."* Both halves of the base
charter's statement about the service fee are now superseded wherever the extended policy departs
from them.

### factor_ladders (revision 4)

| policy | factors | parameter | method | genuine method | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| air_ext_cancellation_penalty | 5 | 4 | 1 | 1 | club |
| air_ext_airline_tax_return | 5 | 4 | 1 | 1 | club |
| air_ext_cancelled_ticket_credit | 5 | 4 | 1 | 1 | club, care |
| air_ext_pooled_credit_release | 4 | 3 | 1 | 1 | club |
| air_ext_credit_reissue_fee | 6 | 4 | 2 | 2 | club |
| air_ext_lapsed_credit_carry_forward | 6 | 5 | 1 | 1 | club, stay |

Counts, labels and ladders unchanged from round 3 and re-tested: every `method` still changes how the
quantity is computed rather than only its coefficient; every ladder still has at least three tiers
stated in full in its rule, pairwise disjoint as stated; every `decides` is an input rather than
`result`; `bindings` disjoint within each policy. What changed is the **wording** of the tier
outcomes, each now naming the stage it enters — which is the class fix, and which strengthens rather
than weakens the ladders. CG-7, CG-9, CG-10, CG-11 and CG-16 all re-tested and all still closed.

CG-8, CG-17 and CG-18 stand as observations, unchanged and not required to change by this round's
brief. CG-17 in particular is worth restating as still open in the same shape: base
`air_evt_schedule_change_rights` still says *"An airline cancellation of the segment is always treated
as a move beyond the threshold, whatever its recorded minutes"*, and
`air_ext_cancellation_penalty.largest_move_minutes` still reads only `schedule_change_minutes`. Not
demonstrable on either world.

### findings (revision 4)

**No new red light.** Two new observations.

**CG-19 — Observation. NEW. The composition convention is stated twice per policy, and the two copies
are load-bearing in different places.** The shared sentence appears in each policy's `baseline.rule`
and again in its `rule`. That is correct for the render — the baseline document and the hub each need
it — but it means the sentence is duplicated twelve times across the charter with no single point of
truth, so a future edit that touches one copy and not its twin would put a policy's two faces into
disagreement about how its own shares compose, in a way no current gate would catch (the gates check
that a tier is in both faces, not that a convention is). Recorded as a maintenance hazard, not a
defect of the present artifact: all twelve copies were compared character for character this round
and all twelve are identical.

**CG-20 — Observation. NEW. The interleaving of an uplift and a share is not stated, and does not
need to be.** The convention fixes how several shares compose and how several uplifts compose, but
not the order between an uplift and a share acting on one figure —
`air_ext_cancelled_ticket_credit` applies `× (1 + member_uplift) × (1 − protection_offset_share)` and
`air_ext_pooled_credit_release` applies `× release_limit_share × (1 + release_bonus)`. Multiplication
being commutative, both orders give the same number on any world, so a reader cannot go wrong and no
consequence is demonstrable. Recorded only so that the completeness claim of
`composition_and_assembly_order` is honest about its one gap.

**Round-3 items: disposition.** Each re-tested against the artifacts, not the reworker's account.

| item | claimed | verified state |
| --- | --- | --- |
| R0-1 | closed by moving the compute to match the rule | **CLOSED** — `tax_returned_at` and `conversion_holdback` added; the markup now acts on the amount returned at, as the rule always said; scored values move accordingly and rule, baseline, ladder and compute agree |
| R1-1, R1-2(a) | closed by moving the rule to match the compute | **CLOSED** — policy 5's two-stage settlement and policy 6's dollars-last are now stated in their baselines; neither moves a number, both make one derivable |
| R1-2(b) | closed by one shared composition sentence across all six | **CLOSED** — verbatim in all six `baseline.rule` and all six `rule`, twelve of twelve |
| `air_cancel_refund` service-fee note | closed by declaring an override | **CLOSED** — verbatim `superseded_clause`, `replaced_by` present in the rule |
| the class, not the instances | claimed | **VERIFIED** — all six computations carry a stage sentence and the convention; all 31 factors name their stage; the two computations the KB audit never demonstrated against are covered as fully as the three that were |
| a mis-attributed sentence in task 1's proof | reported found and re-pointed | verified at the reveal, in `1.md` |

**Regression sweep.** Every item closed in revisions 1–3 was re-tested on the round-4 artifacts and
**all remain closed**: CG-1 (four overrides intact), CG-2, CG-3, CG-4, CG-5, CG-6, CG-7, CG-9, CG-10,
CG-11, CG-12, CG-13, CG-15, CG-16, F0-1, F1-3, F1-5. The base section is still verbatim; the uuid8s,
owners and tool-body discipline are unchanged (the module did not move at all); both trees, their
kinds and their orders are unchanged; and no factor that bore weight in revision 3 is without weight
in revision 4.

## closing_checklist (revision 4)

Written after both tasks had a frozen `source_derivation_frozen (revision 4)` and a
`source_gt_comparison (revision 4)`. Everything above this heading in the revision_4 block was written
before any GT of either task was read this round, apart from one wording repair to a garbled line in
`0.md` made while verifying this audit's own arithmetic.

**The difficulty CLOSES OUT.** All four relationships PASS on both tasks.

| item | state |
| --- | --- |
| per-task audit files correspond one-to-one; `_difficulty.md` alongside | ✔ |
| old revisions traceable and not rewritten | ✔ revisions 1–3 stand untouched in all three files |
| every comparison section carries a PASS | ✔ both tasks, all four relationships |
| extended policies fully covered; the M scopes pairwise disjoint | ✔ policies 1–4 and 5–6 |
| task tools and GT closed; uuid8s independently generated and frozen | ✔ tool module unchanged from round 3 |
| every tree: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥ 1 `owner=user` write, no cycle | ✔ task 0: n=3, 3 edges; task 1: n=1, 1 edge |
| difficulty-wide `prerequisite` graph still a DAG | ✔ two disjoint trees |
| every computation declares a self-sufficient baseline giving a definite number different from gold | ✔ 119.00/205.54, 637.20/676.23, 2348.38/2361.88, 2361.88/1129.03, 75.00/224.00, 1676.00/1185.59 |
| **every computation states the order its factors' outcomes enter the result, in business words** | ✔ **new this round** — a stage sentence in all six baselines, the shared composition convention in all twelve faces, all 31 factor sentences naming their stage |
| 4–6 factors per computation, ≥ 2 `parameter`, ≥ 1 genuine `method` | ✔ 5/5/5/4 and 6/6 |
| ≥ 1 multi-source and ≥ 1 cross-difficulty factor per task | ✔ `club` and `care` on task 0; `club` and `stay` on task 1 |
| every ladder ≥ 3 tiers, stated in full in its rule, tiers distinct in outcome | ✔; observations CG-8, CG-18, CG-20 stand |
| every tier's condition and outcome one that line of business actually holds | ✔ |
| every factor proved to bear weight against an honest baseline | ✔ all 31 across both tasks |
| instantiation-stage gates re-run on the final form | ✔ **eight** green: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE and — newly runnable — TRACEABILITY |

**Summary of the four relationships, revision 4**

| relationship | task 0 | task 1 |
| --- | --- | --- |
| policy self-consistency | **PASS** | **PASS** |
| the problem tree holds | **PASS** | **PASS** |
| factors bear weight | **PASS** | **PASS** |
| policy ↔ task unique solution | **PASS** | **PASS** |

**What this round was, and what it changed.** Rounds 1–3 were this audit's own findings. Round 4 came
from a different direction: a separate agent read the published documents blind, could establish every
tier correctly and still could not reach five of the six scored numbers, because nothing anywhere said
in what order the tiers' outcomes assemble. This audit had passed the difficulty at revision 3 without
catching it — a fact worth recording plainly, since a per-binding check that each rule sentence is
quoted in `compute_basis` can pass while the prose and the expression disagree about which
intermediate a rate acts on, which is exactly how R0-1 survived three rounds here. **F0-12** records
that limitation against this audit, not against the reworker.

The remedy is now in the charter and was tested rather than accepted: a stage sentence in every
baseline, one shared composition convention in all twelve faces, and every factor sentence naming the
stage its outcome enters by the baseline's own name for it. Eight distinct misreadings the charter now
forbids were each computed, and each gives a different number from gold — the order is not decoration.
R0-1 was closed by moving the **compute** to the rule, which moved three of task 0's four scored
values; R1-1 and R1-2(a) by moving the **rule** to the compute, which moved none. Both directions are
right for their case: the first kept the charter saying what the business does, the second made an
already-correct number derivable.

**Blind derivation across all four rounds.** Every scored value of both tasks was re-derived
independently in each round before any GT was read, and matched GT exactly every time: revision 1
(114.19 / 661.81 / 2433.49 / 1161.29 and 224.00 / 623.80), revision 2 (205.54 / 674.31 / 2363.55 /
1129.78 and 224.00 / 1150.94), revision 3 (same as 2, and 224.00 / 1185.59), revision 4 (205.54 /
676.23 / 2361.88 / 1129.03 and 224.00 / 1185.59) — together with every argument, owner, order and
terminal field, and all 31 factor baselines and 6 whole-baseline fall-backs in each round.

**Standing observations, none of them a red light:** CG-8 (vacuous fall-throughs), CG-14 (the replay
gate rewrites the artifacts it checks), CG-17 (one inherited sentence of
`air_evt_schedule_change_rights` that `air_ext_cancellation_penalty` does not implement, undemonstrable
on either world), CG-18 (the retention window excludes nothing on task 1, so two tiers coincide there),
CG-19 (the composition convention is duplicated twelve times with no single point of truth) and CG-20
(the interleaving of an uplift and a share is unstated but commutative).

**Write-domain disclosure, revision 4.** Unchanged in kind: the only artifacts written by this audit
are the three files in this directory. `replay_tasks.py` again rewrote `tasks/0.json` and
`tasks/1.json` when the mandated gate re-run invoked it, confined to `db_closure` key ordering with
`clos 25/25` and `26/26` and `match True` unchanged. The KB and runtime-context audit reports were not
opened before the freeze and were not needed after it. See CG-14 and the `write-domain disclosure`
section in revision 1.

**This difficulty passes the source-layer audit.**
