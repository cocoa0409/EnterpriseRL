# Policy-task audit — hotel_reservations_desk / charter-global

## charter_global_frozen

- freeze time: 2026-09-16 (session clock), written **before any task's GT fields were read**.
- auditor: independent policy-task auditor (not the instantiating agent).
- frozen inputs and hashes (verified by `sha256sum` at the repository root):
  - `env/online_travel_agency/tasks/hotel_reservations_desk/stay.extended.yaml` — `1914f3287fa6690cd00482754eb5ba247a2b17c5bd070a05788f8a8977ab6916`
  - `env/online_travel_agency/tasks/hotel_reservations_desk/task_tools.py` — `a73416711dfc0b8b60f3c77e74f53ea6d2eb62e158eb57cd44d2045c586b33c9`
- fields permitted for this section: the scenario constitution (`blueprint/blueprint.yaml`,
  `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/stay.yaml`, and
  `blueprint/products/club.yaml` for the cross-category reads the charter declares), the extended
  charter in full, and the tool module in full.
- fields explicitly masked and not read while this section was written: every task file's
  `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`,
  `solvability_contract`, `prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state`.
  The task files were reached only through the coordinator's masked views
  (`frozen_time`, `user_scenario`, `initial_state`), whose hashes the brief records.
- entry condition: the seven instantiation gates were supplied green in the brief with their
  verbatim output (EXTENDED / TASK-TOOL-CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING /
  SCOPE), together with the two masked-view hashes and the two charter-global hashes. Nothing is
  missing from the input; the gates are cited, not re-run, at this stage. A green gate is the
  qualification to enter this audit, not a proof of correctness.

### policy_conflict_scan

The difficulty's structured policy is the base section of `stay.extended.yaml` (14 base policies,
byte-identical to `blueprint/products/stay.yaml` — verified by loading both YAMLs and comparing
every top-level key: `category`, `display_name`, `binding`, `lifecycle`, `accounts`,
`parameter_schema`, `variants`, `events`, `measures`, `policies` all compare EQUAL, and
`extended_policies` is the only added key) plus 6 extended policies.

Overlapping-subject scan, base × extended:

| subject event | base policies | extended policy | compatible? |
| --- | --- | --- | --- |
| `stay_cancellation_charge` | `stay_cancellation` | `stay_ext_late_cancellation_penalty` | one declared override; one **undeclared** conflict (F-1 below) |
| `stay_refund_payout` | `stay_refund_settlement`, `stay_best_rate_guarantee` | `stay_ext_cancellation_refund_payout` | one declared override; two **undeclared** conflicts (F-2, F-3) |
| `stay_room_charge` | `stay_room_and_occupancy`, `stay_agg_portfolio_occupancy`, `stay_club_and_corporate_interaction` | `stay_ext_occupancy_supplement` | declared |
| `stay_tax_and_fee_charge` | `stay_taxes_and_fees` | `stay_ext_statutory_tax_charge` | declared |
| `stay_resort_credit_use` | `stay_resort_credit`, `stay_incidentals` | `stay_ext_resort_credit_application` | declared |
| `stay_check_out` | `stay_incidentals` | `stay_ext_departure_balance_settlement` | declared |

Triggers, eligibility, time anchors, terminal states and cross-category read boundaries:

- Triggers: `on_request` on the two cancellation-family policies, `state_due` on the four
  in-stay/departure policies. No extended policy claims a trigger a base event's `triggers:` block
  already fires (`stay_confirm` → `stay_deposit_charge`, `stay_cancel` → `stay_cancellation_charge`,
  `stay_check_in` → `stay_room_charge`/`stay_resort_credit_grant`), so no double write is implied.
- Eligibility gates the extended policies inherit unchanged and do not restate: `stay_cancellation`
  (`rooms_given_up_stated` caller_fact, `inside_free_cancellation` time),
  `stay_refund_settlement.reservation_settled` (payout only while cancelled / no show / checked out),
  `stay_incidentals.stay_in_progress` (extras only while checked in or checked out),
  `stay_resort_credit.guest_in_house` (credit spent only while checked in),
  `stay_evt_property_notice.relocation_approved`, `stay_best_rate_guarantee.one_settlement_per_reservation`.
  None of the six extended rules weakens any of these, and the tool bodies enforce none of them.
- Time anchors: `stay_cancellation.temporal_basis` anchors the free-cancellation term on
  `stay_reservations.confirmed_at` in elapsed hours, boundary inclusive. The extended penalty policy
  anchors its band ladder on `DAYS(NOW, F('check_in_date'))` — a different anchor for a different
  quantity (which band, not whether free). These do not conflict on the same quantity, but the base
  "inside the term nothing is withheld" sentence does — see F-1.
- Cross-category read boundaries: two policies declare `cross_category: [club]`
  (`stay_ext_late_cancellation_penalty` reads `status`, `variant_name`,
  `club_points_entries.points_delta`; `stay_ext_statutory_tax_charge` reads `status`,
  `variant_name`). The compute of each reads exactly those and nothing further
  (`CFIELD('club','status')`, `CPARAM('club','hotel_rate_discount_pct')`,
  `XSUM('club','club_points_entries','points_delta', within_months=12, …)`). No other extended
  policy touches another category. No cross-category *write* is attempted anywhere.

Task scope exclusivity and completeness (derived from the policies each task's world and persona
put in play, not from any masked field): task 0 exercises
{`stay_ext_late_cancellation_penalty`, `stay_ext_cancellation_refund_payout`}; task 1 exercises
{`stay_ext_occupancy_supplement`, `stay_ext_statutory_tax_charge`,
`stay_ext_resort_credit_application`, `stay_ext_departure_balance_settlement`}. The two sets are
disjoint and together cover all six extended policies.

### rule_compute_equivalence

Check 2 was run binding by binding over all six policies: every binding in `compute` was matched to
a `compute_basis` entry, every `compute_basis` entry was matched to a verbatim sentence of the
policy's own `rule`, and the rule was then swept back sentence by sentence to find promises with no
expression behind them. Every factor's `ladder` tier was checked against both faces: each tier
condition is a sentence of the `rule`, and each is a branch of the `decides` binding's ternary
chain; no tier appears in one face only.

Result: the quantities, windows (`within_months=12` on the club points read), filters
(`charge_category=` on every folio aggregate), tiers, branches, cross-category reads, acting bases,
caps (`MX(0.0, …)`, `MN(…, prepayment_held)`, `MN(gross_refund, payout_ceiling)`,
`MN(credit_available, eligible_spend)`) and the rounding convention ("rounded to two decimal
places as it is worked out", `RND(x, 2)`, Python half-to-even, matching the tool docstrings'
"rounded half to even at the second decimal") all correspond in both directions — **with two
exceptions**, F-4 and F-5 below.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: `confirm_reservation_cancellation_70c0f3f0`/`penalty_amount_usd`,
  `raise_cancellation_refund_payout_a740a404`/`refund_amount_usd`,
  `post_occupancy_supplement_f6d09258`/`extra_occupant_charge_usd`,
  `post_statutory_tax_charge_0b7e8f18`/`statutory_tax_amount_usd`,
  `spend_resort_credit_ff384f87`/`credit_applied_usd`,
  `settle_departure_balance_f8243430`/`closing_balance_usd`. Six distinct tools, six distinct
  computed quantities; no tool and no quantity is claimed twice. Each policy's subject, base refs,
  tool docstring and terminal state admit one business reading.
- uuid8 tails: `70c0f3f0`, `a740a404`, `f6d09258`, `0b7e8f18`, `ff384f87`, `f8243430`. All six are
  distinct, share no common prefix, form no arithmetic or lexical sequence, and none is another with
  a changed tail. Each is frozen into the function name, the `target_tool` field and the id prefix
  the body emits (`stpen_`, `strfd_`, `stocc_`, `sttax_`, `stcru_`).
- Docstring sequence-silence: five of six are silent about ordering. One is not — F-6 below.
- Tool bodies: each body performs exactly one atomic write set (`ctx.update` and/or `ctx.create`)
  and returns confirmation text. **No body reads the folio to test a prerequisite, refuses a call,
  raises, or emits a hint**; the only `ctx.find` calls fetch `customer_id` off the reservation (and
  `resort_credit_balance_usd` in `spend_resort_credit_ff384f87`) to stamp the new row. The tool
  layer therefore judges no prerequisite.

### prerequisite_graph

Check 7 over the whole graph. Four edges are declared, across four of the six policies; the other
two carry `prerequisite: []` (present and empty, not absent).

| blocked policy | problem | kind | gate | form | resolved_by | acyclic |
| --- | --- | --- | --- | --- | --- | --- |
| `stay_ext_cancellation_refund_payout` | `stay_ext_late_cancellation_penalty` | value_input | `penalty_withheld` | state | `confirm_reservation_cancellation_70c0f3f0` | yes |
| `stay_ext_statutory_tax_charge` | `stay_ext_occupancy_supplement` | value_input | `supplement_total` | state | `post_occupancy_supplement_f6d09258` | yes |
| `stay_ext_departure_balance_settlement` | `stay_ext_statutory_tax_charge` | value_input | `tax_posted` | state | `post_statutory_tax_charge_0b7e8f18` | yes |
| `stay_ext_departure_balance_settlement` | `stay_ext_resort_credit_application` | value_input | `credit_drawn` | state | `spend_resort_credit_ff384f87` | yes |

- Every `problem` names an extended policy id in this file; none names a base policy and none names
  itself. The whole graph is a DAG (`penalty → refund`; `supplement → tax → balance`;
  `credit → balance`), with no cycle created across the two tasks.
- Every `gate` is a real binding of the blocked policy's `compute` (`penalty_withheld`,
  `supplement_total`, `tax_posted`, `credit_drawn` all appear as binding names), and `kind:
  value_input` is honest in all four: each gate feeds an arithmetic binding, not only a status test.
- Every `resolved_by` is the depended-on policy's own `target_tool`, and each of those tools
  genuinely creates the row named in `effect` (`charge_category='cancellation_penalty'`,
  `'extra_occupant'`, `'occupancy_tax'`, `'resort_credit_use'` respectively).
- `form: state` on all four; `fallback_reason` is absent on all four, which is correct for the state
  form. No `condition` is strengthened or weakened relative to the sentence it comes from; each
  restates the same record-visible state and adds only "so that … can be read off the folio".
- No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears in
  any `prerequisite` block.

### prerequisite_sentences

Check 6, edge by edge. Each `policy_source` was located verbatim in the **blocked** policy's own
`rule` (string-matched), then put through the four-point test.

1. `refund ← penalty` — "The amount returned to the card is settled only after the folio carries the
   cancellation penalty withheld on every room given up."
   Ordering connective: "only after". Waited-on thing: "the folio carries the cancellation penalty
   withheld on every room given up" — a record-visible state in the words the folio uses
   (`stay_folio_entries`, `charge_category='cancellation_penalty'`), with no performer and no tool.
   No tool name, policy id, snake_case token or row id. Scope matches `condition`.
   **One write of this difficulty brings it about**: `confirm_reservation_cancellation_70c0f3f0` is
   the only tool in the module that creates a `cancellation_penalty` row. Derivation in one reading:
   folio shows no penalty line → the state is false → the only policy whose own rule describes
   withholding a cancellation penalty is `stay_ext_late_cancellation_penalty`, whose subject is
   `stay_cancellation_charge` → its write is the guest's own cancellation → run it first.
   The depended-on rule does not restate the sentence. **Defect: the blocked rule states the same
   dependency a second time** — F-7.
2. `tax ← supplement` — "The statutory tax due is settled only once the folio's room lines carry
   every occupant beyond the rate plan's standard occupancy for the nights of the stay already
   posted." Connective "only once"; state form; no tool/id token; scope matches `condition`. Only
   `post_occupancy_supplement_f6d09258` creates an `extra_occupant` row. Single reading. The
   depended-on rule (`stay_ext_occupancy_supplement`) does not restate it.
3. `balance ← tax` — "The balance settled at departure is struck only once the folio carries the
   statutory tax due on the room money for the stay." Connective "only once"; state form; only
   `post_statutory_tax_charge_0b7e8f18` creates an `occupancy_tax` row in this difficulty. Single
   reading; not restated in the depended-on rule.
4. `balance ← credit` — "The balance settled at departure is struck only after the property credit
   standing on the reservation has been drawn down against the charges it may be spent against."
   Connective "only after"; only `spend_resort_credit_ff384f87` creates a `resort_credit_use` row.
   Single reading; not restated in the depended-on rule. **Borderline form** — F-8.

Cross-problem orders stated in a rule that ground no declared edge: a regex sweep for ordering
connectives over all six extended rules returned, beyond the four sentences above, only sentences
about the *internal* order of one computation ("taken once on the whole prepayment still held",
"that comparison is made on the final figure alone and after every step below", "money has already
been returned against a prepayment line", "the folio carries no rollaway charge already posted",
"the arrival date has already been reached") and the two duplicate wordings in F-7. None of these
orders one problem against another, so no undeclared dependency is stated in a rule. Base rules that
state a domain order (`stay_deposit_and_prepayment`: "A deposit already taken is applied against the
first night's room charge at check-in"; `stay_incidentals`: "At departure the folio is closed off")
ground no task's tree — every tree edge here rests on an extended prerequisite sentence of its own —
so they are not red under check 6's base-sentence clause.

Docstrings: `post_occupancy_supplement_f6d09258`, `post_statutory_tax_charge_0b7e8f18`,
`spend_resort_credit_ff384f87`, `settle_departure_balance_f8243430` and
`confirm_reservation_cancellation_70c0f3f0` state no position in a sequence and name no other tool.
`raise_cancellation_refund_payout_a740a404` does — F-6.

### override_declarations

Check 1's finding half, run sentence by sentence against every entry of each policy's
`base_policy_refs`. Each extended policy declares exactly one `overwrite` entry:

| extended policy | base sentence named as superseded | verdict |
| --- | --- | --- |
| `stay_ext_late_cancellation_penalty` | `stay_cancellation`: "Outside it the penalty is read off the rate plan's cancellation ladder by how many whole days lie between the cancellation and the arrival date" | correctly named; the replacement band ladder is unique after replacement |
| `stay_ext_cancellation_refund_payout` | `stay_refund_settlement`: "Each payout is raised against the original folio line it reverses, so a folio with several lines settles as several payouts and never as one lump sum." | correctly named |
| `stay_ext_occupancy_supplement` | `stay_room_and_occupancy`: "An occupant beyond the rate plan's standard occupancy is charged the plan's extra-adult or extra-child amount for every night they stay, counted per room." | correctly named |
| `stay_ext_statutory_tax_charge` | `stay_taxes_and_fees`: "Occupancy tax and city tax are applied to the room total alone, night by night, and never to optional extras or to the agency service fee." | correctly named |
| `stay_ext_resort_credit_application` | `stay_resort_credit`: "Property credit included in the rate plan is placed on the reservation at check-in, for the plan's amount per stay and not per night." | correctly named |
| `stay_ext_departure_balance_settlement` | `stay_incidentals`: "At departure the folio is closed off: every posted line is settled against the deposit already held and the balance is taken from or returned to the card on file." | correctly named |

Sentences of the cited base policies that the extended side nevertheless handles differently, and
that **no** `overwrite` entry names — three findings, F-1, F-2, F-3 below. All three were reached by
taking each `base_policy_refs` entry sentence by sentence and asking which clause finally decides
the scored quantity, not by looking for new parameter names. The three disguised forms were looked
for specifically: no anonymous intermediate factor was found (every intermediate has a
`compute_basis` sentence); the 0/1 multiplier form **is** present as the ordinary shape of these
policies (`supplement_taxable_pct`, `tax_return_pct`, `facility_return_pct`, `service_return_pct`,
`tax_included_pct`, `onproperty_pct`, `credit_offset_pct`, `deposit_offset_pct`, `availability_pct`,
`minibar_counted_pct` are all 0/100 selectors), and each of those is declared as a factor with its
ladder in the rule — but two of them (F-2, F-3) zero out or restore a quantity base already fixed in
a way base forbids; no dropped branch was found (every ladder branch is reachable given some plan in
`variants`).

### factor_ladders

Structure only; weight is per task. Every factor's `decides` is an input binding, never `result`.
Every factor's binding set is disjoint from its siblings' within its policy (checked set by set for
all six policies). Every ladder has at least three tiers, stated in full in the `rule` — condition
and value/method — and implemented as a ternary chain in the `decides` binding; no tier lives only
in `compute`, and no branch of a `decides` binding lacks a tier in the rule.

| policy | factors | parameter | method | ≥3 tiers each | multi-source tiers | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| `stay_ext_late_cancellation_penalty` | 4 (`lead_time_share` 4-tier, `measure_selection`, `conversion_markup`, `loyalty_goodwill_release`) | 3 | 1 | yes | `measure_selection`, `conversion_markup`, `loyalty_goodwill_release` | `loyalty_goodwill_release` → club |
| `stay_ext_cancellation_refund_payout` | 6 (`prepayment_measure`, `withheld_deduction`, `statutory_return`, `facility_return`, `service_fee_return`, `settlement_ceiling`) | 4 | 2 | yes | all six | none |
| `stay_ext_occupancy_supplement` | 4 (`standard_occupancy`, `party_spread`, `nights_convention`, `rollaway_component`) | 3 | 1 | yes | all four | none |
| `stay_ext_statutory_tax_charge` | 4 (`supplement_taxability`, `room_money_discount`, `tax_night_convention`, `statutory_rate`) | 3 | 1 | yes | all four | `room_money_discount` → club |
| `stay_ext_resort_credit_application` | 4 (`credit_grant_measure`, `credit_availability`, `minibar_countability`, `eligible_charge_scope`) | 3 | 1 | yes | all four | none |
| `stay_ext_departure_balance_settlement` | 6 (`room_money_measure`, `statutory_inclusion`, `onproperty_settlement`, `credit_offset_scope`, `deposit_offset_scope`, `settlement_markup`) | 5 | 1 | yes | all six | none |

Every policy sits inside 4–6 factors with ≥2 `parameter` and ≥1 `method`. Per task (policy sets as
derived in the conflict scan above): task 0 carries 10 factors with multi-source tiers present and
one `cross_difficulty: club`; task 1 carries 18 factors with multi-source tiers present and one
`cross_difficulty: club`. Tier disjointness was checked ladder by ladder as stated — every ladder's
non-fall-through tiers differ in at least one conjunct (e.g. `active … and no corporate programme
reference` vs `active … and a corporate programme reference`), so no two tiers can both fire.

Each `method` tier names a computation rule the charter states (aggregate swaps, gross-ups, cap
selections), and each `parameter` tier substitutes a number. Two labels are questionable — F-9 —
though neither pushes its policy outside the 2-parameter/1-method bounds under either reading.

Every policy declares a `baseline` with a `rule` and a `params` list; each baseline rule's sentences
were located in the policy's own `rule` (all present), and each names default keys that are in the
policy's `params` or the variant parameter schema. Whether each baseline yields a definite number
different from gold is a fact about one world and is demonstrated in the task files.

### findings

Each finding names the tasks it bears on; the demonstration of what it costs a task lives in that
task's file.

**F-1 — `SOURCE-POLICY` (undeclared override): the free-cancellation term is inherited from base but
the extended penalty rule never consults it.**
*Symptom.* Base `stay_cancellation` says "Inside the free-cancellation term nothing is withheld on
any rate plan, and the deposit or prepayment is returned in full." No `overwrite` entry names that
sentence, so it is inherited in full. `stay_ext_late_cancellation_penalty`'s rule computes the
amount withheld from a lead-day band ladder and a set of factors with no mention of the
free-cancellation term, and `compute` carries no binding for `confirmed_at` or
`free_cancellation_hours_before_checkin`.
*Root cause.* The override declaration names only the ladder-reading clause ("Outside it the penalty
is read off the rate plan's cancellation ladder…"); the "inside it" clause governs the same scored
quantity and was not named.
*Evidence.* `blueprint/products/stay.yaml`, `stay_cancellation.rule`, and its
`eligibility[inside_free_cancellation].temporal_basis` (anchor `stay_reservations.confirmed_at`,
`duration_source: variants.free_cancellation_hours_before_checkin`, `unit: elapsed_hours`,
`boundary: inclusive`) versus `stay.extended.yaml` lines 1769–1830 (`overwrite`, `rule`, `compute`).
*Demonstrated consequence.* On any world where the cancellation falls inside the term on a plan with
a non-zero term (Semi-Flexible 72 h, Standard Flexible 24 h, Member Flex 24 h, Suite Flexible 48 h,
All-Inclusive Flex 168 h) and 2–29 whole days before arrival, base yields 0.00 withheld and the
extended ladder yields 25 % or 50 % of the prepayment still held.
*Bears on.* Neither task's world reaches the contradiction (task 0's plan carries a 0-hour term;
task 1 raises no cancellation), so no task file demonstrates a numeric consequence. Recorded here as
a charter defect with its consequence demonstrated on the charter's own parameter table rather than
on a task world.

**F-2 — `SOURCE-POLICY` (undeclared override): the extended settlement exceeds the per-line cap base
imposes on a payout.** *Bears on task 0.*
*Symptom.* Base `stay_refund_settlement` says "A payout may never exceed the amount that original
line actually collected". `stay_ext_cancellation_refund_payout`'s `overwrite` names only the
"several payouts and never as one lump sum" sentence; the per-line cap sentence is inherited. The
extended rule then raises one payout against one prepayment line whose ceiling is
`prepayment_held` or `folio_balance`, both of which can exceed what that single line collected.
*Root cause.* Lumping several lines into one payout necessarily breaches the per-line cap, and only
the lumping was declared.
*Evidence.* `blueprint/products/stay.yaml` `stay_refund_settlement.rule`;
`stay.extended.yaml` `stay_ext_cancellation_refund_payout.overwrite` and the `payout_ceiling`
binding `(folio_balance if (deposit_line_count > 1 and folio_balance < prepayment_held) else
(prepayment_held if (deposit_line_count > 1 and folio_balance >= prepayment_held) else
deposit_line_max))`.
*Demonstrated consequence.* Two defensible answers on task 0's world — see
`env/online_travel_agency/audits/policy_task/hotel_reservations_desk/0.md`, `## findings`, F-2/T0.

**F-3 — `SOURCE-POLICY` (undeclared override): the extended settlement returns the agency service
fee that base says is never returned.** *Bears on task 0.*
*Symptom.* Base `stay_cancellation` says "The agency service fee is not returned on cancellation,
because the booking service it pays for has already been performed." `stay_cancellation` is one of
`stay_ext_cancellation_refund_payout.base_policy_refs`, and no `overwrite` entry names that
sentence. The extended policy's own `baseline.rule` says the opposite outright — "The service
element is the agency service fee posted on the reservation, and all of it is returned." — and its
`service_fee_return` ladder returns 100 % of it on both its second tier and its fall-through
(`K('service_full_return_pct') = 100`).
*Root cause.* The extended baseline was written as a "return everything" default without checking
that base forbids returning this particular element at all.
*Evidence.* `blueprint/products/stay.yaml` `stay_cancellation.rule`, last sentence;
`stay.extended.yaml` `stay_ext_cancellation_refund_payout.baseline.rule` and the
`service_return_pct` binding and `service_fee_return` ladder.
*Demonstrated consequence.* On any world where the plan booked charges no agency service fee
(Member Flex Rate `agency_service_fee_usd: 0.0`, All-Inclusive Flex Rate `0.0`) yet a service-fee
line stands on the folio, base withholds it and extended returns 100 % of it. Task 0's plan charges
17.95, so its tier-1 answer happens to agree with base; the defect is live in the charter and in the
baseline a KB reader is handed. Recorded as a charter defect; task 0's file records that its own
scored number is not moved by it.

**F-4 — `SOURCE-POLICY` (rule/compute equivalence): "the nights the folio carries room lines for" is
implemented as the highest night sequence on the folio's room lines, which is a different
quantity.** *Bears on task 1.*
*Symptom.* Three policies use the phrase "the nights the folio carries room lines for"
(`stay_ext_occupancy_supplement`, `stay_ext_statutory_tax_charge`,
`stay_ext_departure_balance_settlement`), and all three implement it as
`folio_nights: MAX('stay_folio_entries','night_sequence', charge_category='room_night')`. A count of
nights and a high-water sequence number coincide only when the folio's room lines begin at night 1.
*Root cause.* The prose names a count; the expression returns an ordinal. The same charter proves it
knows the difference: where it means a high-water sequence it says so — "the highest room sequence
the prepayment lines were posted for" (`deposit_rooms`) and "taken as the highest occupant sequence
the folio shows" (`folio_occupants`). And "room lines" is a term of art in these same rules that
excludes prepayment lines: "the room lines and the prepayment lines posted on the reservation taken
together" (`stay_ext_departure_balance_settlement`, `stay_ext_statutory_tax_charge`).
*Evidence.* `stay.extended.yaml`: `stay_ext_occupancy_supplement.rule` ("…the supplement is charged
for the nights the folio carries room lines for"), `compute_basis.folio_nights`, and the
`folio_nights` binding; the same three artefacts in `stay_ext_statutory_tax_charge` and
`stay_ext_departure_balance_settlement` (where `booked_nightly_rate` divides a total that *includes*
prepayment lines by "the nights the folio carries room lines for").
*Demonstrated consequence.* Two numbers for every scored quantity of task 1 — see
`env/online_travel_agency/audits/policy_task/hotel_reservations_desk/1.md`, `## findings`, F-4/T1.

**F-5 — observation (rule/compute equivalence): `credit_standing`'s fall-through drops the drawdown
the rule and the factor baseline both promise.** *Bears on task 1.*
`stay_ext_resort_credit_application.rule` says, for its second tier and its fall-through, "the
credit standing is the largest single grant posted together with whatever has already been drawn
against it", and the factor's own `baseline` encodes exactly that —
`credit_standing: RND(lead_grant + credit_drawn_already, 2)`. But `compute` implements both of those
branches as bare `lead_grant`, with `credit_drawn_already` added only on the first tier. The rule
therefore makes a promise the expression does not keep, and the factor's declared baseline is not
the compute's fall-through. On task 1's world `credit_drawn_already = 0.0` and the first tier is the
one taken, so no number moves; recorded as an observation for want of a demonstrable consequence.

**F-6 — observation (check 3): a task-tool docstring states its position in the sequence.**
*Bears on task 0.*
`raise_cancellation_refund_payout_a740a404`'s docstring opens "Return money to the card a guest
originally paid a hotel reservation with, **once that reservation has been given up and whatever is
being withheld already stands on its folio**." Check 3 requires that no docstring state an action's
position in a sequence or carry an ordering word; "once … already stands" does both, and it restates
the very dependency the prerequisite sentence carries. It creates no second answer, so it is an
observation rather than a red. (`task_tools.py`, lines 52–59.)

**F-7 — observation (check 6): the blocked rule states one dependency twice.** *Bears on task 0.*
`stay_ext_cancellation_refund_payout.rule` opens "This rule settles the money returned to a guest's
card **once a reservation has been given up and the amount withheld already stands on the folio**."
and then carries the declared prerequisite sentence "The amount returned to the card is settled only
after the folio carries the cancellation penalty withheld on every room given up." Check 6 requires
the rule to carry nothing else about that dependency — "no second wording". The duplicate is also
copied into `baseline.rule`, so it reaches the computation document as well as the hub. No second
answer follows, so it is an observation.

**F-8 — observation (check 6): one prerequisite sentence is declared `state` but is phrased as a
perfect passive of the depended-on action.** *Bears on task 1.*
"The balance settled at departure is struck only after the property credit standing on the
reservation has been drawn down against the charges it may be spent against." "has been drawn down"
names the depended-on action in the passive rather than a record-visible state; the three sibling
edges use the state construction ("the folio carries …"). Because a record-visible state *does*
single out the write (a `resort_credit_use` line on the folio, which the sibling edges would have
phrased as "the folio carries a property credit drawdown"), and because `form: state` is declared
with no `fallback_reason`, the wording sits on the boundary. A reader still reaches exactly one
write, so no consequence is demonstrable; recorded as an observation naming the state that would
have been used.

**F-9 — observation (factor labels): two factors labelled `parameter` swap an aggregate rather than
a number.** *Bears on tasks 0 and 1.*
`stay_ext_resort_credit_application.credit_grant_measure` (`parameter`) moves `credit_standing`
between "the grants posted taken together" (`SUM`) and "the largest single grant posted" (`MAX`);
`stay_ext_occupancy_supplement.party_spread` (`parameter`) moves `counted_adults` between
`F('adults_count')` and `MAX(guest_sequence)`. Both change how the quantity is computed rather than
which number goes into a fixed formula, which is the `method` description. Relabelling either leaves
its policy at 2 `parameter` / 2 `method`, still inside the bounds, so nothing follows from it;
recorded as an observation.

**F-10 — observation (rule/compute equivalence, boundary): "the arrival date has not passed" is
implemented strictly.** *Bears on task 0.*
`stay_ext_cancellation_refund_payout`'s `statutory_return` tier 1 reads "the arrival date has not
passed", implemented as `DAYS(NOW, F('check_in_date')) > 0`; on the arrival date itself
`DAYS(...) = 0`, so the tier that fires is the one for an arrival that *has* passed. The sibling
policies implement "has already been reached" as `>= 0` (`stay_ext_statutory_tax_charge`) and "no
later than" as `<=` (`stay_ext_resort_credit_application`), so the strict comparison is the outlier.
Neither task's world sits on the boundary (task 0's arrival is 24 days out), so no consequence is
demonstrable.

## closing_checklist

**The difficulty is NOT closed out.** Step 4's close-out is reached only when all M tasks carry a
frozen derivation, a comparison, and PASS on all four relationships. Both tasks carry a frozen
derivation and a comparison, but both fail policy self-consistency, and each fails unique solution
derivatively on the same evidence. The checklist is recorded below with what holds and what does
not, so that the state of the difficulty is on file rather than implied.

Per-task verdicts (written after both reveals):

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | **`SOURCE-POLICY RED`** (F-2/T0) | PASS | PASS | **FAIL** — same evidence as F-2/T0 |
| 1 | **`SOURCE-POLICY RED`** (F-4/T1) | PASS | PASS | **FAIL** — same evidence as F-4/T1 |

What holds:

- The per-task audit files correspond one-to-one with the tasks (`0.md`, `1.md`) and `_difficulty.md`
  sits alongside them. This is revision 1, so there is no earlier revision to preserve; any re-audit
  must append under `## revision_2` and leave this text untouched.
- Every comparison section carries an item-by-item, figure-by-figure table. In both tasks the
  independent derivation reproduced GT exactly: task 0's 835.78 / 2044.10 with
  `source_entry_id 30cb5616-…`, task 1's 150.00 / 307.10 / 78.50 / 2344.28, together with all 10 and
  all 18 `factor_sensitivity` figures, both `baseline_result` pairs (1236.00 / 1236.00 and
  0.00 / 305.00 / 0.00 / 1980.00), and all four `edge_load_bearing` figures (2472.00; 283.83,
  2029.50, 2424.74). No item differs.
- The difficulty's six extended policies are fully covered by the two tasks, and the two
  `charter_scope` blocks are pairwise disjoint in policies, tools and subjects — task 0 claims
  {`stay_ext_late_cancellation_penalty`, `stay_ext_cancellation_refund_payout`} with
  `confirm_reservation_cancellation_70c0f3f0` and `raise_cancellation_refund_payout_a740a404`;
  task 1 claims the other four policies with the other four tools. Each scope spans its whole
  problem tree, root and prerequisites together. Each task tool's uuid8 is independently generated
  and frozen (see `### action_binding_and_uuids`).
- Task 0's tree has 1 prerequisite problem and 1 `value_input` edge (floor max(0,1) = 1); task 1's
  has 3 prerequisite problems and 3 `value_input` edges (floor 2). Each tree has at least one
  problem resolved by an `owner=user` tool — `confirm_reservation_cancellation_70c0f3f0` and
  `spend_resort_credit_ff384f87` respectively — and neither has a cycle. The four
  `prerequisite` edges of the difficulty together form a DAG, and no cycle is created across tasks.
- Every computation declares a self-sufficient baseline and 4–6 factors with ≥2 `parameter` and ≥1
  `method`; every ladder has ≥3 tiers stated in full in its rule; every factor was proved on its
  task's world to move the scored value against a baseline that matches `baseline.rule`; and each
  whole-computation baseline gives a definite number different from gold (1236.00 vs 835.78;
  1236.00 vs 2044.10; 0.00 vs 150.00; 305.00 vs 307.10; 0.00 vs 78.50; 1980.00 vs 2344.28).
  Each task carries at least one multi-source factor and at least one `cross_difficulty: club`
  factor whose club rows are seeded.
- The instantiation-stage gates were re-run once on the final form at the close of this audit, from
  the repository root with `DIFF=env/online_travel_agency/tasks/hotel_reservations_desk`, and all
  seven are green and unchanged from the brief's snapshot: EXTENDED OK; TASK TOOL CONTRACT OK;
  REPLAY OK (0.json 10 acts, 1.json 13 acts, both `match=True`); SOLVABILITY OK; COMPUTE OK
  (branches 33 / 46, steps 10 / 13, both `match=True`); GROUNDING OK; SCOPE OK. The artefacts were
  not edited by this audit, so this is a confirmation that the green snapshot still describes the
  form audited, not evidence that the two reds are absent — the gates prove structure, not
  self-consistency across a policy's real domain.

What does not hold, and blocks the close-out:

- **F-2** (charter) / **F-2/T0** (consequence): the extended cancellation settlement breaches an
  inherited, undeclared base cap, and on task 0's world the two clauses give 2044.10 and 1236.00.
- **F-4** (charter) / **F-4/T1** (consequence): "the nights the folio carries room lines for" and
  `MAX(night_sequence, charge_category='room_night')` denote different quantities, and on task 1's
  world the two readings give 150.00/307.10/2344.28 against 100.00/299.34/3535.57.
- **F-1** and **F-3** are charter defects of the same kind whose consequence no task world reaches;
  they block nothing here but remain undeclared overrides in the charter.
- Observations F-5 through F-11 are recorded in this file and in the task files and are not grounds
  for rework.

---

## revision_2

Round 2 of this audit. Revision 1 above is left exactly as written, including the charter-global
sections that the reworked artefacts have now moved; nothing in it has been rewritten to
accommodate the new form.

### revision_2 / re_derivation_basis

- audit time: 2026-09-16 (session clock), auditor unchanged.
- **This round is not blind and does not pretend to be.** Round 1's GT was revealed to me before
  this round began, so the round-2 figures below are a *verification* recomputation from the
  reworked charter and seed, not an independent blind derivation. Every figure was nevertheless
  computed from the charter's own `compute` bindings on the masked `initial_state` before the
  reworked GT fields were opened, and the reworked GT was then compared against it.
- Shared inputs, and therefore which charter-global sections were re-derived in full:

  | artefact | round 1 sha256 | round 2 sha256 | moved? | consequence |
  | --- | --- | --- | --- | --- |
  | `stay.extended.yaml` | `1914f328…` | `28abf44b…` | **yes** | every charter-global section re-derived in full |
  | `task_tools.py` | `a7341671…` | `de04b3c4…` | **yes** | `### action_binding_and_uuids` re-derived in full |
  | masked view `0.json` | `453de809…` | `453de809…` | no | task 0's world is byte-identical |
  | masked view `1.json` | `73dff8bd…` | `c0d1a234…` | **yes** | task 1 re-derived from the new seed, not carried forward |

  Because both charter-global inputs moved, no section is carried forward by reference; all of
  `policy_conflict_scan`, `rule_compute_equivalence`, `action_binding_and_uuids`,
  `prerequisite_graph`, `prerequisite_sentences`, `override_declarations` and `factor_ladders` were
  re-run against the reworked charter.
- Entry condition: the coordinator supplied the seven gates re-run on the reworked form, all green,
  with `1.json` now at 29 closure rows / 27 seed rows / 36 history rows (round 1: 23 / 21 / 30) —
  movement consistent with six rows added to task 1's seed. Cited, not re-run at this stage.

### revision_2 / what moved in the charter

- The base section is still byte-identical to `blueprint/products/stay.yaml` (all ten top-level keys
  compare EQUAL; `extended_policies` remains the only added key).
- `overwrite` entries: `stay_ext_late_cancellation_penalty` 1 → 2, `stay_ext_cancellation_refund_payout`
  1 → 3; the other four unchanged at 1.
- Two factor labels changed: `party_spread` and `credit_grant_measure`, both `parameter` → `method`.
- Three compute bindings changed: `tax_return_pct` (`> 0` / `<= 0` → `>= 0` / `< 0`),
  `credit_standing` (tiers 2 and 3, bare `lead_grant` → `RND(lead_grant + credit_drawn_already, 2)`),
  and `stay_ext_departure_balance_settlement` gained `facility_posted: SUM('stay_folio_entries',
  'amount_usd', charge_category='resort_fee')`, which enters `gross_balance`.
- Rule prose: a definition sentence was introduced, and every use of the round-1 phrase was
  rewritten to it.
- One tool docstring changed (`raise_cancellation_refund_payout_a740a404`); the six function bodies,
  owners and uuid8s are unchanged.

### revision_2 / closure verification, item by item

Each round-1 item is judged against the artefacts, not against the reworker's claim.

**F-1 — CLOSED.** A second `overwrite` entry on `stay_ext_late_cancellation_penalty` now names the
base sentence verbatim: `superseded_clause` = "Inside the free-cancellation term nothing is withheld
on any rate plan, and the deposit or prepayment is returned in full", string-matched inside
`stay_cancellation.rule`. Its `replaced_by` — "The withheld share is settled from the whole days
between the handling date and the arrival date in every case, whatever term ran from the moment the
property confirmed the reservation, and no term measured from that moment sets the amount withheld
to nothing." — is present verbatim in the extended `rule`.
*Merged semantics tested for uniqueness.* The base sentence that survives, "A cancellation is
handled free of penalty only when frozen time is not after the moment the guest's reservation was
confirmed by the property plus the free-cancellation term of the rate plan booked" (also the
condition of `stay_cancellation.eligibility[inside_free_cancellation]`), states a necessary
condition, not a sufficient one: it forbids a free cancellation outside the term and does not
require one inside it. With the sufficient half superseded and the replacement saying outright that
no such term zeroes the amount, a reader inside the term on a 72-hour plan now reaches one figure —
the band ladder's — where round 1 gave 0.00 and the ladder's share. No residue.

**F-2 — CLOSED.** `stay_ext_cancellation_refund_payout` now declares the cap:
`superseded_clause` = "A payout may never exceed the amount that original line actually collected,
and the sum of a reservation's payouts may never exceed its folio balance", matched verbatim in
`stay_refund_settlement.rule`; `replaced_by` present verbatim in the extended `rule`. On task 0's
unchanged world the second figure the base clause produced (1236.00) is no longer defensible: the
ceiling is now stated to be the one the ladder below gives. The task's own proof was corrected too —
`tasks/0.json` `design_rationale` no longer asserts "Inherited and not overridden: … that a payout
may never exceed what the original line collected", and instead states the three declared overrides
and names the 1236.00 / 2044.10 gap as the reason the declaration was needed.
*One residual tested and cleared:* the rule still carries "The settlement is finally capped at what
the single prepayment line standing on the reservation actually collected" (the baseline sentence,
which is also the `settlement_ceiling` ladder's fall-through) alongside the new "the ceiling on it is
the ceiling set out below rather than what the prepayment line it is raised against collected on its
own". Read together in the baseline-plus-factor idiom these are consistent — the second says the
ceiling is whatever the ladder below yields, and the ladder's fall-through happens to be the per-line
amount. In every world the ladder returns exactly one ceiling, so no second figure follows.

**F-3 — CLOSED.** A third `overwrite` entry names base `stay_cancellation`'s "The agency service fee
is not returned on cancellation, because the booking service it pays for has already been
performed." verbatim, replaced by "The agency service fee posted on the reservation is returned only
where the rate plan booked charges no such fee, the desk keeping a fee the plan levies and returning
one the plan does not." — present verbatim in the rule. The worlds that made the charter defect live
(Member Flex Rate and All-Inclusive Flex Rate, both `agency_service_fee_usd: 0.0`) are now governed
by a declared rule rather than by two clauses in conflict.

**F-4 — CLOSED, and the fix was checked against the specific hazard it creates.** The disputed
phrase "the nights the folio carries room lines for" occurs **0 times** in the reworked charter
(`grep -c`). In its place a definition sentence appears **4 times**: "The nights of the stay already
covered on the folio are taken as the highest night sequence the folio's room lines carry."
- *Stated everywhere the quantity is used.* The three policies whose `compute` binds `folio_nights`
  are `stay_ext_occupancy_supplement`, `stay_ext_statutory_tax_charge` and
  `stay_ext_departure_balance_settlement`. The definition is present in all three `rule`s **and** in
  all three `baseline.rule`s, so a reader who reaches only the computation document still gets it.
  The three policies that do not use the quantity do not carry the sentence. Every downstream use
  was rewritten to the defined term — the three ladders now read "the nights of the stay already
  covered on the folio", and `stay_ext_departure_balance_settlement.booked_nightly_rate` now reads
  "divided by the nights of the stay already covered on the folio multiplied by the rooms held",
  which was the sentence whose two halves used "room lines" in two senses in round 1.
- *Is the definition the quantity the expression computes?* "the highest night sequence the folio's
  room lines carry" ≡ `MAX('stay_folio_entries','night_sequence', charge_category='room_night')`,
  term for term: highest ↔ `MAX`, night sequence ↔ `night_sequence`, the folio's room lines ↔ the
  `charge_category='room_night'` filter. On task 1's world it yields 3, and 3 is the only number the
  sentence admits. The round-1 rival reading (a count of nights, 2) is no longer available, because
  the sentence no longer names a count.
- *`compute_basis` agrees.* `stay_ext_occupancy_supplement.compute_basis.folio_nights` quotes the
  definition sentence; the other two quote their ladder sentence, which is also in the rule.

**F-5 — CLOSED.** `credit_standing`'s second and third branches are now
`RND(lead_grant + credit_drawn_already, 2)`, matching both the rule's "the largest single grant
posted together with whatever has already been drawn against it" and the factor's declared
`baseline`. The fall-through and the baseline are now the same expression.

**F-6 — CLOSED.** `raise_cancellation_refund_payout_a740a404`'s docstring no longer contains "once
that reservation has been given up and whatever is being withheld already stands on its folio"; its
first sentence is now "Return money to the card a guest originally paid a hotel reservation with."
and the sequence claim is replaced by an intra-call statement, "the folio's other lines are left
exactly as they stand." An ordering-word sweep over all six docstrings now returns only intra-call
statements ("Afterwards the guest sees…", "read from the reservation record returned by the
reservation lookup before this call") — none names another tool or another problem's write.

**F-7 — CLOSED.** `stay_ext_cancellation_refund_payout.rule` now opens "This rule settles the money
returned to a guest's card on a cancellation settlement." The duplicate dependency wording is gone
from the rule and from `baseline.rule`. An ordering-connective sweep over all six reworked rules now
returns exactly four sentences beyond internal-calculation ordering, and each of the four is a
declared `policy_source` — no second wording anywhere, and no cross-problem order grounding no edge.

**F-8 — CLOSED.** The credit edge's sentence is now "The balance settled at departure is struck only
once the folio carries the property credit drawn down against the charges it may be spent against."
— the state construction the three sibling edges use, naming a record-visible state on the folio
rather than the action in the passive. `form: state` with no `fallback_reason` is now correct on its
face. Verbatim-locatable in the blocked policy's own rule.

**F-9 — CLOSED.** `party_spread` and `credit_grant_measure` are relabelled `method`, which is what
their tiers do (swap `F('adults_count')` for `MAX(guest_sequence)`, and `SUM` of grants for `MAX` of
grants). Counts after relabelling: `stay_ext_occupancy_supplement` 2 `parameter` / 2 `method`,
`stay_ext_resort_credit_application` 2 `parameter` / 2 `method` — both still inside 4–6 factors with
≥2 `parameter` and ≥1 `method`. No other policy's counts moved.

**F-10 — CLOSED.** `tax_return_pct` now tests `DAYS(NOW, F('check_in_date')) >= 0` for "the arrival
date has not passed" and `< 0` for "has passed", which is the convention the sibling policies use.
Verified not to move task 0: its `DAYS(...)` is 24, tier 1 under either comparison.

**F-11 — CLOSED, with two proof-text regressions it introduced (below).** Six `resort_fee` lines of
29.00 (nights 1–3 × rooms 1–2, total 174.00) now stand on the Seattle folio, matching Member Flex
Rate's `resort_fee_per_night_usd: 29.0` with `resort_fee_waived: false`, and the reservation's
`folio_balance_usd` moved 1908.50 → 2082.50, which equals the sum of its money lines
(610.00 + 1220.00 + 174.00 + 78.50). The settlement now charges them: the `overwrite` replacement
sentence, the `rule` and the `baseline.rule` all carry "The property facility fee posted on the
reservation is charged in full, being owed per room per night on every plan that does not waive it",
`compute_basis.facility_posted` quotes it, `inputs.history` declares the `resort_fee` aggregate, and
`gross_balance` adds `facility_posted`. It is a baseline element rather than a factor, so the
policy stays at 6 factors.

### revision_2 / charter-global re-derivation, results

All seven charter-global checks were re-run against the reworked charter. Results, stated as
deltas from `## charter_global_frozen` above:

- **policy_conflict_scan** — the three undeclared conflicts of round 1 (F-1, F-2, F-3) are now
  declared. A fresh sentence-by-sentence pass over every `base_policy_refs` entry of all six
  policies found no new undeclared override. The overlapping-subject table is otherwise unchanged;
  the new facility element of `stay_ext_departure_balance_settlement` agrees with base
  `stay_taxes_and_fees` ("The property facility fee is charged per room per night on every plan that
  does not waive it") rather than deviating from it, so it needs no declaration. Scope exclusivity
  and completeness unchanged: the same 2 + 4 split, disjoint and jointly complete.
- **rule_compute_equivalence** — mechanically re-checked: every `compute` binding except the direct
  record reads (`F('rooms_count')`, `F('adults_count')`, `F('nights_count')`) has a `compute_basis`
  entry; every `compute_basis` entry is a verbatim substring of its policy's `rule`; no
  `compute_basis` key lacks a binding; every sentence of every `baseline.rule` is a substring of its
  policy's `rule`. Round 1's two exceptions (F-4, F-5) are both gone and no new one appeared.
- **action_binding_and_uuids** — the six `(target_tool, computes)` pairs are unchanged and still
  claimed once each. The uuid8 tails are the same six, still distinct, prefix-free and unsequenced.
  The six function bodies are unchanged line for line: each is `make_id` → optional
  `find('stay_reservations', …)` → `create`/`update` → return text. **No body reads the folio to test
  a prerequisite, refuses, raises or hints** — re-read in full after the docstring edit.
- **prerequisite_graph** — the same four edges, the same `kind`/`gate`/`resolved_by`, all
  `form: state` with no `fallback_reason`, all four `policy_source` strings verbatim-locatable in
  the blocked policy's own rule (string-matched). Still a DAG; still `[]` filled in on the two
  policies with no prerequisite. No authoring-viewpoint phrasing.
- **prerequisite_sentences** — the four-point test re-run on all four sentences; all pass, and the
  credit edge (F-8) now passes on the state-form point as well as the rest. Each waited-on state is
  still brought about by exactly one write of this difficulty
  (`cancellation_penalty` / `extra_occupant` / `occupancy_tax` / `resort_credit_use`, one creating
  tool each). No rule restates another's sentence; no rule carries a second wording of its own
  dependency; no docstring carries a sequence claim.
- **override_declarations** — now nine declared overrides across the six policies (2 + 3 + 1 + 1 + 1
  + 1), each `superseded_clause` verbatim in the named base policy's rule and each `replaced_by`
  verbatim in the extended rule. No undeclared override remains.
- **factor_ladders** — 4 / 6 / 4 / 4 / 4 / 6 factors, unchanged in number; ≥2 `parameter` and ≥1
  `method` in every policy after the two relabels; every ladder still ≥3 tiers, pairwise disjoint as
  stated, stated in full in its rule and implemented in its `decides` binding; every `decides` is an
  input, never `result`; sibling binding sets still disjoint within each policy. Per task: 10 and 18
  factors, multi-source tiers throughout, one `cross_difficulty: club` each.

### revision_2 / findings

**F-12 — observation (new, introduced by the F-11 rework). `tasks/1.json` `design_rationale` states
a `folio_balance_usd` the row no longer carries.**
The WORLD card asserts: "No stale statistic cache is designed here:
stay_reservations.folio_balance_usd agrees with the sum of the money lines on each reservation
(**1908.50** and 653.81)". The Seattle reservation's row now reads `folio_balance_usd: 2082.5`, and
the sum of its money lines is 610.00 + 1220.00 + 174.00 + 78.50 = 2082.50. Recomputed, the *claim*
holds — the cached field and the ledger do agree — but the figure quoted for it is the pre-rework
one. No scored value reads that field on task 1 (no computation of this task binds it), so no
relationship fails and this is an observation, not a red. Affected artifact:
`env/online_travel_agency/tasks/hotel_reservations_desk/tasks/1.json`, `design_rationale`, WORLD card.
Bears on task 1.

**F-13 — observation (new, introduced by the F-11 rework). Two proof passages that enumerate task
1's folio rows omit the six `resort_fee` rows the new binding reads.**
(a) `design_rationale` BUSINESS-OBJECT CARD: "Rows entering the aggregates, on that reservation only:
two deposit lines of 305.00 …, four room-night lines of 305.00 …, two property credit grants of 50.00
…, and two minibar lines of 46.00 and 32.50 …" — an enumeration presented as complete, which now
omits the six `resort_fee` lines that `facility_posted: SUM('stay_folio_entries','amount_usd',
charge_category='resort_fee')` reads and that contribute 174.00 (178.35 after the markup) to the
scored 2522.63. (b) `prerequisite_closure.edges[stay_ext_occupancy_supplement]
.unresolved_at_frozen_time.why_false`: "the folio holds two deposit lines, four room-night lines, two
property credit grants and two minibar lines **and nothing else**" — "nothing else" is now false.
In both cases the conclusion each passage supports still holds on recomputation (the rows that enter
the aggregates do enter them, and no `extra_occupant` line stands on the folio, so the edge is
genuinely unresolved), so no relationship fails and neither is a red. Recorded because a proof that
enumerates the rows and misses the ones carrying 174.00 of the answer is an incomplete proof.
Affected artifact: `tasks/1.json`, `design_rationale` BUSINESS-OBJECT CARD and
`prerequisite_closure.edges[0].unresolved_at_frozen_time.why_false`. Bears on task 1.

**F-14 — observation (new). The facility sentence imports a per-night justification into a rule that
charges only what is posted.**
`stay_ext_departure_balance_settlement`'s new sentence reads "The property facility fee posted on
the reservation is charged in full, being owed per room per night on every plan that does not waive
it." The quantity is fixed by the restrictive "posted on the reservation" and the expression is
`SUM(resort_fee)` = 174.00, so the sentence admits one number and this is **not** a second reading of
the F-4 kind. But the participial clause invites the arithmetic 29.00 × 2 rooms × 4 nights = 232.00,
which on task 1's world would give a balance of 2582.08; and the same rule *does* add the unposted
fourth night's room money ("each night of the stay not yet covered is added at the booked nightly
rate for every room held") while leaving the unposted fourth night's facility fee uncharged. The
asymmetry is stated explicitly in both directions, so a careful reader reaches 174.00; it is
recorded as an observation with the rival figure named so the judgement is re-checkable. Bears on
task 1.

Round-1 observations F-5 through F-11 are all closed (see the item-by-item section above). Round-1
observations that were charter-global and are now moot are not re-listed.

## closing_checklist — revision_2

**The difficulty CLOSES OUT at revision 2.** Both round-1 REDs are genuinely closed — not reworded —
and all four relationships now PASS on both tasks.

Per-task verdicts (revision 2):

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | **PASS** | **PASS** | **PASS** | **PASS** |
| 1 | **PASS** | **PASS** | **PASS** | **PASS** |

Step 4's checklist, re-run on the reworked form:

- The per-task audit files correspond one-to-one with the tasks and `_difficulty.md` sits alongside
  them. Revision 1 is preserved intact in all three files; revision 2 is appended below it, and no
  round-1 derivation was rewritten.
- Every comparison section carries a PASS. Task 0's scored solution is unchanged from revision 1
  (835.78, 2044.10, `source_entry_id 30cb5616-…`) and my recomputation on the reworked charter
  reproduced it. Task 1's scored solution moved on exactly one parameter — the closing balance,
  2344.28 → **2522.63** — and my recomputation from the new seed and the new rule reached 2522.63
  before the reworked GT was opened; the other three (150.00, 307.10, 78.50) are unchanged and were
  re-derived, not carried forward.
- The six extended policies are fully covered; the two `charter_scope` blocks are pairwise disjoint
  in policies, tools and subjects, and each spans its whole problem tree. Task tools and GT are
  closed (`db_closure_matches_initial_state: true` on both). Each tool's uuid8 is independently
  generated and frozen, and the six are unchanged from revision 1.
- Task 0's tree: 1 prerequisite problem, 1 `value_input` edge (floor 1), one `owner=user` write, no
  cycle. Task 1's tree: 3 prerequisite problems, 3 `value_input` edges (floor 2), one `owner=user`
  write, no cycle. The four edges of the difficulty together remain a DAG.
- Every computation declares a self-sufficient baseline and 4–6 factors (≥2 `parameter`, ≥1
  `method`; per task ≥1 multi-source and ≥1 cross-difficulty), every ladder ≥3 tiers stated in full
  in its rule, and **every factor was re-shown to bear weight on its own task's world** — all 10 on
  task 0's unchanged world and all 18 on task 1's **new** world. Each whole-computation baseline
  gives a definite number different from gold: 1236.00 vs 835.78; 1236.00 vs 2044.10; 0.00 vs
  150.00; 305.00 vs 307.10; 0.00 vs 78.50; **2154.00 vs 2522.63**.
- The instantiation-stage gates were re-run once on the final form at the close of this round, from
  the repository root with `DIFF=env/online_travel_agency/tasks/hotel_reservations_desk`, and all
  seven are green: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK;
  GROUNDING OK; SCOPE OK. The artefacts were not edited by this audit.

Three observations remain on the record and are not grounds for rework: **F-12** and **F-13** (stale
figure and incomplete row enumerations in task 1's proof text, both introduced by the F-11 change,
neither moving a scored value or a relationship) and **F-14** (the facility sentence's per-night
justification clause).
