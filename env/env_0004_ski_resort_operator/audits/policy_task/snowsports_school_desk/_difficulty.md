# Policy-task audit — snowsports_school_desk / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (not the instantiating agent).
- Freeze time (charter-global section, written before any task GT was revealed): 2026-09-17T18:30Z.
- Frozen inputs, both read in full (permitted unmasked):
  - `env/env_0004_ski_resort_operator/tasks/snowsports_school_desk/lessons.extended.yaml` — sha256:16 = `ccaa40cd9520ae99`
  - `env/env_0004_ski_resort_operator/tasks/snowsports_school_desk/task_tools.py` — sha256:16 = `7abc9779ff7c3bdf`
- Also read: `env/env_0004_ski_resort_operator/blueprint/blueprint.yaml`, `blueprint/products/lessons.yaml`,
  `blueprint/products/lodging.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`,
  `erlbench/`, and `skills/erl-task-instantiate/scripts/check_compute.py` (for the exact semantics of
  the compute primitives `DAYS`, `MONTHS`, `within_months`, `XCOUNT`, `CFIELD`, `MAX`, `LATEST`).
- Task files were read only through the coordinator's masked view
  (`.../masked_views_coordinator/snowsports_school_desk/tasks/{0,1}.json`, keys kept =
  `frozen_time`, `user_scenario`, `initial_state`; sha256:16 `3b5aa50ba28bd840` / `c91118905e02a626`).
- Fields explicitly masked and not consulted while this section was written: `evaluation_criteria`,
  `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`,
  `prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state`.
- **Nothing in this section is derived from any revealed GT field.**

### entry_conditions
The coordinator supplied the instantiation-stage gate snapshot (commands and output lines) with the
brief: EXTENDED, TASK-TOOL-CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all green;
CACHE-DIFF informational; TRACEABILITY not runnable before the KB render step, by construction. The
masked views and their hashes were supplied and re-verified above. Entry conditions are complete; the
gates were not re-run by this auditor at this stage. A machine green light qualifies the bundle for
manual audit and proves nothing about self-consistency or unique entailment.

### base_section_verbatim
`head -1357 lessons.extended.yaml` is byte-identical to `blueprint/products/lessons.yaml`
(`diff` empty). The extended file adds only the comment banner at lines 1359-1362 and
`extended_policies:` from line 1364. **PASS** — the base copy has not been rewritten.

### policy_conflict_scan

Five extended policies, each with a distinct subject, trigger, computed quantity and target tool:

| policy | trigger | subject | computes | target_tool | prerequisite |
| --- | --- | --- | --- | --- | --- |
| `lessons_ext_weather_session_credit` | state_due | lessons_credit_issue | credit_amount_usd | `issue_weather_session_credit_1ce20aea` (agent) | [] |
| `lessons_ext_balance_settlement` | on_request | lessons_payment | payment_amount_usd | `settle_school_balance_78bdef11` (**user**) | 1 edge |
| `lessons_ext_session_tuition_charge` | state_due | lessons_tuition_charge | tuition_amount_usd | `raise_session_tuition_charge_38aef0d5` (agent) | [] |
| `lessons_ext_lift_access_addon` | state_due | lessons_equipment_addon | addon_charge_usd | `raise_lift_access_addon_aea17349` (agent) | [] |
| `lessons_ext_date_change_fee` | on_request | lessons_reschedule | change_fee_usd | `confirm_lesson_date_change_58e66cab` (**user**) | 2 edges |

No two policies claim the same subject event, the same computed binding name or the same tool. The
eligibility, time anchors, objects and terminal states of the five do not overlap: each acts on one
booking's own school account and writes one ledger row (plus, for the date change, the booking's
`first_session_date` and `reschedule_count`).

Cross-category read boundaries: `passes` (read by `lessons_ext_weather_session_credit` only, as
`history`: `passes_holdings.status` via `EXISTS`, `passes_ledger.event_type` via `XCOUNT`) and
`lodging` (read by the other three of the tuition/addon/change group, as `branch`:
`lodging_holdings.status` / `rate_plan` / `nights_booked` via `CFIELD`, `lodging_folio.amount_usd` via
`XSUM`). All reads are read-only and declared in each policy's `cross_category` block. No policy
writes outside `lessons`.

Task scope exclusivity: the `prerequisite` graph partitions the five policies into exactly two closed
problem trees —
`{lessons_ext_balance_settlement -> lessons_ext_weather_session_credit}` and
`{lessons_ext_date_change_fee -> lessons_ext_session_tuition_charge, lessons_ext_lift_access_addon}`.
The two sets are pairwise disjoint and jointly cover all five policies, so the suite's scopes are
mutually exclusive and jointly complete. (Derived from the charter's own `prerequisite` edges; the
tasks' `charter_scope` fields were masked.)

**PASS** — no conflict between policies of this difficulty on an overlapping subject.

### rule_compute_equivalence

Machine-checked over all five policies (script over `compute` / `compute_basis` / `rule`):

- every `compute_basis` value is a **verbatim** substring of its policy's own `rule` (5/5 policies, 0 misses);
- every `compute_basis` key names a real `compute` binding (0 orphans);
- every declared factor's ladder tier is a sentence of the `rule` and a branch of the `decides`
  binding, and every branch of each `decides` binding is a tier the rule states (checked by hand,
  policy by policy; no tier lives only in `compute`, none only in prose);
- every `baseline.rule` is a verbatim run of sentences of its policy's own `rule` (5/5).

Two bindings of `lessons_ext_balance_settlement` carry **no** `compute_basis` entry: `figure_owed`
and `instalment_due`. Both are pure arithmetic over quantities that are themselves based, and both
are in fact covered by rule sentences quoted under neighbouring keys ("The figure owed is the tuition
raised against the booking, plus the add-ons raised against it, plus the school fees raised against
it, less the payments already collected on it." / "…the first instalment share of what remains is
collected."). Recorded as observation OBS-1 — a completeness gap in `compute_basis`, not an invented
basis.

Three `compute_basis` quotations of `lessons_ext_weather_session_credit` are attached to the wrong
binding of the pass-offset ladder (`active_pass` carries the *skied-on* sentence, `pass_scans_recent`
the *idle-pass* sentence, `pass_offset` the *no-pass* sentence). Each quotation is a genuine rule
sentence and the three together state the whole ladder, so the two-way correspondence holds; the
per-binding attribution is off. Observation OBS-2.

`settled_ratio` in `lessons_ext_balance_settlement` is implemented as
`SUM(payments) / MX(SUM(tuition), 1)`. The rule says only "judged as the payments collected on the
booking measured against the tuition raised on it"; the `MX(…, 1)` division guard is not stated.
Observation OBS-3 (guard only; on any world with tuition raised the two readings agree).

Otherwise **PASS** — no quantity, window, filter, tier, branch, cross-category read, acting base,
grouping, cap/floor or rounding convention is implemented without a verbatim rule sentence behind it,
and no rule sentence makes a promise `compute` does not keep.

### action_binding_and_uuids

`(target_tool, computes)` pairs — 5 distinct tools, 5 distinct computed bindings, each claimed by
exactly one policy (table above). **PASS.**

uuid8 tails: `1ce20aea`, `78bdef11`, `38aef0d5`, `aea17349`, `58e66cab`. Pairwise distinct; no shared
prefix; no arithmetic or lexical sequence; no tail is another's with a changed character; none looks
batch-derived. **PASS.**

Docstrings: grep for `before | after | first | prior | once | until | then` over `task_tools.py`
returns hits only at lines 175, 184, 192-193 and 211, and every one is the noun phrase "first session"
(the booking's own first session) or "once this move is counted" (internal to the same call). No
docstring states an action's position in a sequence, names another tool, or carries an ordering word
about another problem. Each function body performs one atomic write and returns a confirmation; none
refuses, errors or hints on any prerequisite state. **PASS.**

### prerequisite_graph

Three edges in total, all `kind: value_input`, all `form: state`, no `fallback_reason` anywhere
(correct: none is action-form).

| blocked policy | problem | gate | resolved_by | acyclic |
| --- | --- | --- | --- | --- |
| `lessons_ext_balance_settlement` | `lessons_ext_weather_session_credit` | `credit_standing` | `issue_weather_session_credit_1ce20aea` | yes |
| `lessons_ext_date_change_fee` | `lessons_ext_session_tuition_charge` | `tuition_standing` | `raise_session_tuition_charge_38aef0d5` | yes |
| `lessons_ext_date_change_fee` | `lessons_ext_lift_access_addon` | `addon_entries` | `raise_lift_access_addon_aea17349` | yes |

- Every policy has `prerequisite` filled in (`[]` for the three leaves).
- Every `problem` names another extended policy id in this file; none names a base policy or itself.
- The graph is a DAG (two disjoint trees, depth 1).
- Each `gate` is a real binding name in the blocked policy's own `compute`: `credit_standing`
  (`credit_issued - credit_applied`), `tuition_standing`
  (`SUM('lessons_ledger','amount_usd', event_type='lessons_tuition_charge')`), `addon_entries`
  (`COUNT('lessons_ledger', event_type='lessons_equipment_addon')`). `kind: value_input` therefore
  matches `gate` in all three cases — each gate is a binding feeding the calculation, not an
  eligibility flag.
- Each `resolved_by` is the depended-on policy's own `target_tool`, and each tool genuinely writes the
  row the gate aggregates: `issue_weather_session_credit_1ce20aea` creates a `lessons_credit_issue`
  row; `raise_session_tuition_charge_38aef0d5` a `lessons_tuition_charge` row;
  `raise_lift_access_addon_aea17349` a `lessons_equipment_addon` row.
- No `prerequisite` field contains authoring-viewpoint phrasing ("in this task", "at the opening",
  "the current world"); each `condition` is written as a general record state.

**PASS.**

### prerequisite_sentences

Each edge's `policy_source`, verified verbatim-locatable in the **blocked** policy's own `rule`
(script check: 3/3 True):

1. `lessons_ext_balance_settlement` — "The amount collected is settled only after the school account
   carries the credit entry owed for every session the collective could not run."
   Ordering connective: *only after*. What it waits on: *the school account carries the credit entry
   owed for every session the collective could not run* — a record-visible state, in the words the
   ledger and `find_lesson_account_entries` use, with no action, performer or tool. No tool name, no
   policy id, no snake_case token, no row id. Scope matches the edge `condition` exactly (a credit
   entry per lost session). **State form honoured; no fallback claimed or needed.**
   Exactly one write of this difficulty brings that state about: `issue_weather_session_credit_1ce20aea`
   is the only tool in `task_tools.py` that creates a `lessons_credit_issue` row, so the hop resolves
   uniquely. Derivation a reader performs: the sentence names a credit entry answering for a session
   the collective could not run -> the only policy whose own rule describes writing that entry is
   `lessons_ext_weather_session_credit` ("the school makes good the value of that session as school
   credit on the booking it was lost from … One credit entry is issued for each session the collective
   could not run") -> that policy's own rule then gives the amount. One reading.
2. `lessons_ext_date_change_fee` — "The ceiling the fee is held to is fixed only after the school
   account carries the tuition entry due for the booking."
   Connective *only after*; waited-on state = *the school account carries the tuition entry due for the
   booking*; state form; no tool/id/token. Unique bringer: `raise_session_tuition_charge_38aef0d5` is
   the only tool writing `lessons_tuition_charge`. Reader's hop: a tuition entry on the school account
   -> `lessons_ext_session_tuition_charge` is the only policy whose rule describes raising tuition
   ("The tuition raised for a booking is the product's block price…"). One reading.
3. `lessons_ext_date_change_fee` — "The handling amount for re-arranging what the school laid on is
   worked out only once the school account carries the add-on entry due for the lift access the session
   date requires."
   Connective *only once*; waited-on state = *the school account carries the add-on entry due for the
   lift access the session date requires*; state form; no tool/id/token. Unique bringer:
   `raise_lift_access_addon_aea17349` is the only tool writing `lessons_equipment_addon`. Reader's hop:
   a lift-access add-on entry -> `lessons_ext_lift_access_addon` is the only policy whose rule describes
   raising it ("the school puts the lift access the lesson day needs on the booking as an add-on of its
   own"). One reading. Note the sentence is narrower than a bare "an add-on entry": it names *the lift
   access the session date requires*, which is what distinguishes the write to be done from the
   rental add-on that may already stand on the account — correct strength for the edge's `condition`.

No rule carries a second wording of any dependency, no other problem's tool name, policy id or route,
and no depended-on policy's rule restates the blocked policy's sentence (checked: the rules of
`lessons_ext_weather_session_credit`, `lessons_ext_session_tuition_charge` and
`lessons_ext_lift_access_addon` never mention settlement or a date change).

Sweep for undeclared cross-problem orders: every other occurrence of an ordering connective in the
five rules is within-computation sequencing ("the reduction in money is **then** taken off that
result", "the ceiling is applied last of all", "the three reductions are **first** combined into one
total", "…and **then** halved"). No rule states an order between two problems that grounds no declared
edge. No **base** rule sentence is used to ground any of the three edges.

**PASS.**

### override_declarations

Findings only; each affected task's file demonstrates (or fails to demonstrate) the consequence
against its own world.

`lessons_ext_weather_session_credit` — `base_policy_refs: [lessons_cancellation, lessons_session_delivery]`
- `lessons_cancellation`, sentence "Where the collective cancels the session for weather, mountain
  conditions or an instructor being unavailable, the product's weather basis decides what the
  household receives and no fee is retained." — **named in `overwrite`, verbatim**, replaced by "The
  amount made good is the value of one session taken at the standard weather share, and the figure is
  rounded to the nearest cent." Declared. Merged semantics unique.
- `lessons_cancellation`, remaining sentences (free-cancellation deadline, elapsed-hour counting, late
  cancellation share, pro-rating for delivered sessions, "What comes back is issued as school credit")
  — none governs the quantity this policy scores; the last is followed (the write is a credit issue).
  Inherited intact.
- `lessons_session_delivery`, sentence **"Where a session is lost to weather or mountain conditions
  the collective makes good on the product's weather basis, and that session is not drawn from the
  block."** — **NOT named in any `overwrite` entry.** This is the same promise as the
  `lessons_cancellation` sentence that *was* superseded, restated in a second base policy that the
  extended policy itself cites. Finding **F-1** below.
- `lessons_session_delivery`, other sentences (block loading, delivery, grace period, makeup
  allowance/period) — followed; the extended `makeup_answer_method` ladder reads
  `makeup_sessions_allowed` and `makeup_booking_days` exactly as base defines them; the credit tool
  does not draw a session from the block (`issue_weather_session_credit_1ce20aea` touches only
  `lessons_ledger` and `lessons_holdings.lesson_credit_usd`), which honours "that session is not drawn
  from the block". Inherited intact.

`lessons_ext_balance_settlement` — `base_policy_refs: [lessons_payment_terms, lessons_credit_use]`, `overwrite: []`
- `lessons_payment_terms` sentence by sentence: deposit share at booking (untouched, historical);
  "The balance is collected no later than the product's balance period counted in calendar days from
  the day the booking was recorded" plus its counting rule (**followed exactly** — `days_since_booked
  = DAYS(F('booked_date'), NOW)` against `P('balance_due_days')`, anchor day zero, every day alike);
  "A product whose deposit is the whole price has no balance to collect" (not engaged);
  "Where the product offers scheduled instalments, the balance may be divided instead of collected at
  once" (**refined**, not contradicted, by `instalment_split`); "A balance that is not collected by
  its due date puts the place at risk…" (not engaged). No conflict -> `overwrite: []` is correct here.
- `lessons_credit_use` sentence by sentence: "not paid out" (followed — the write is a payment against
  the account, never a payout); validity period and its calendar-day counting (**not re-checked by the
  extended policy**; see OBS-4); "A single application must be at least the product's minimum"
  (**followed** — `credit_set_against` is gated on `P('credit_minimum_redemption_usd')`); "credit may
  be applied to part of a charge" (followed); "applied only while the booking … has not reached the
  cancelled, no_show or closed state" (a state gate the extended policy does not restate; see OBS-4);
  "Credit issued on one booking may be applied to any school booking on the same household account"
  (the extended policy narrows to the booking's own credit — narrower, not contradictory); "Where
  several credit entries sit on one household account, the entry closest to running out is applied
  first" (the extended policy sums them instead; engaged only where two or more entries stand — see
  OBS-4).
- **Structural point, not an override:** the rule says the credit standing "is set against the figure
  owed and money is taken only for what is left", but the only write the policy owns is a
  `lessons_payment` row; nothing in this difficulty writes a `lessons_credit_redeem` row, and
  `settle_school_balance_78bdef11` does not lower `lesson_credit_usd`. Finding **F-2**.

`lessons_ext_session_tuition_charge` — `base_policy_refs: [lessons_agg_household_group_pricing, lessons_pricing]`
- `lessons_pricing`, sentence "The tuition raised for a booking is the product's block price where the
  product is sold as a block, and its session price multiplied by the number of sessions booked where
  it is sold session by session." — **named in `overwrite`, verbatim.** Declared.
- `lessons_pricing`, sentence **"The season passholder reduction is taken first where the product
  carries one and the participant is shown on the collective's records as holding a pass in the active
  state, then the group reduction, and the result is rounded to the cent."** — **NOT named in any
  `overwrite` entry**, and neither reduction appears anywhere in the extended rule or `compute`.
  Finding **F-3**.
- `lessons_pricing.formula.amount_usd`
  (`round(tuition_before_discount_usd * (1 - multi_booking_discount_pct / 100), 2)`) applies the
  multi-booking reduction unconditionally; the extended `compute` never does. Same finding F-3.
- `lessons_pricing`, "Add-ons … are raised as their own entries … and an add-on already included in
  the product is never raised as a charge" — governs the *add-on* policy, superseded there (below).
  "Tuition is raised only while the booking record stands in the requested, waitlisted, confirmed or
  in_progress state" — inherited, not weakened. "A product sold with a deposit raises the whole
  tuition at once and collects the deposit share of it at booking, with the balance falling due later"
  — the extended policy raises the whole tuition at once (consistent); the accompanying deposit
  collection is not part of this policy's subject. Observation OBS-5.
- `lessons_agg_household_group_pricing` — "Where the household books the same product for two or more
  participants starting on the same date, the multi-booking reduction … is taken off"; "the sibling
  reduction … whichever of the two is the larger"; "The season passholder reduction … is taken first
  and the group reduction is worked out on the figure it leaves"; "Bookings made on different days are
  not grouped after the fact". `group_minimum_participants: 2`. The extended policy takes neither
  reduction. Same finding F-3; whether it bites depends on the world and is settled per task.

`lessons_ext_lift_access_addon` — `base_policy_refs: [lessons_pricing]`
- `lessons_pricing`, sentence "Add-ons the household asks for are raised as their own entries at the
  product's add-on prices, one entry for each kind of add-on and each session date, and an add-on
  already included in the product is never raised as a charge." — **named in `overwrite`, verbatim.**
  Declared; the replacement keeps both riders ("A product that includes a lift ticket in its price
  never carries this add-on at all, and one entry is raised for each session date the access covers").
- Remaining `lessons_pricing` sentences: the tuition basis and the reductions govern tuition, not
  add-ons, and this policy computes no tuition. No further conflict.

`lessons_ext_date_change_fee` — `base_policy_refs: [lessons_change_terms, lessons_pricing]`
- `lessons_change_terms`, sentence "A booking may be moved to another date where the product allows
  it, up to the number of moves the product allows, and each move carries the product's move fee." —
  **named in `overwrite`, verbatim**, replaced by "The fee for a change of date is the product's move
  fee, and the figure is rounded to the nearest cent." Declared. Note the replacement drops the two
  eligibility riders (product allows it; within the move allowance), but base's own
  `move_notice_deadline` eligibility block and the `reschedule_allowed` / `max_reschedules`
  parameters survive untouched in the base section, so they are inherited rather than weakened.
- `lessons_change_terms`, "A move to another date is accepted only when it is recorded on or before
  the move deadline …" plus the elapsed-hour counting rule — inherited in full; the extended policy's
  own `days_of_notice` is a *calendar-day* quantity used only to pick a fee band and never used as an
  eligibility test, so the two do not collide (different quantities, different jobs).
- `lessons_change_terms`, "A move does not reprice the booking: the tuition already raised stands …"
  — restated by the extended rule ("A move does not reprice the booking, so the tuition already
  standing on it is untouched by the change") and honoured by the tool. Consistent.
- Re-registration and instructor-assignment sentences — different subjects, not engaged.
- `lessons_pricing` — the extended policy raises a fee, not tuition; no sentence engaged.

### factor_ladders

Structure only. Counts per policy (all ladders have exactly 3 tiers, fall-through counted; every
ladder is stated in full in its policy's own `rule`, condition and outcome, and implemented as one
ternary chain in `compute`; every `decides` is an intermediate binding, never `result`; every factor's
`bindings` set is disjoint from its siblings' within its policy):

| policy | factors | parameter | method | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| `lessons_ext_weather_session_credit` | 4 | 3 | 1 (`makeup_answer_method`) | `pass_day_offset` | `pass_day_offset` -> passes |
| `lessons_ext_balance_settlement` | 4 | 3 | 1 (`credit_offset_method`) | `credit_offset_method` | none |
| `lessons_ext_session_tuition_charge` | 5 | 4 + `advance_rate_method` labelled method | **0 genuine** (see F-4) | `resort_stay_reduction` | `resort_stay_reduction`, `rate_window_supplement` -> lodging |
| `lessons_ext_lift_access_addon` | 4 | 3 | 1 (`session_length_method`) | `resort_guest_ticket_points` | `resort_guest_ticket_points` -> lodging |
| `lessons_ext_date_change_fee` | 6 | 5 | 1 (`block_move_method`) | `instructor_rebooking_amount` | `resort_guest_relief` -> lodging |

All five are inside the 4-to-6 bound and meet the >= 2 `parameter` floor. The `>= 1 method` floor is
met by four of the five; `lessons_ext_session_tuition_charge` fails it once
`advance_rate_method` is judged honestly — finding **F-4**.

Label honesty, factor by factor:
- Genuine `method` (the tiers change how the quantity is computed, not which number goes into one
  formula): `makeup_answer_method` (halve the shared figure / drop the share entirely and take the
  whole session value / apply the share), `credit_offset_method` (offset the whole credit standing /
  offset only as much as the figure owed / offset nothing), `session_length_method` (price per session
  *loaded* / price at the half-day share per session *loaded* / price per session the *booking holds*
  — the multiplicand itself changes source), `block_move_method` (multiply by the record-derived
  count of sessions loaded / leave as worked out / take a fixed share).
- **Not a genuine `method`:** `advance_rate_method`. Its three tiers are
  `base_price * K('early_booking_multiplier')`, `base_price * K('ahead_booking_multiplier')` and
  `base_price` — one formula with a substituted rate (0.90 / 0.95 / 1.00), which the ladder's own
  wording calls a *multiplier*. Finding **F-4**.
- All 18 factors labelled `parameter` do select a number, and none changes an algorithm. Honest.

Method tiers naming a rule the charter states: every method tier's wording is a verbatim sentence of
its own policy's `rule` (checked in `rule_compute_equivalence`). **PASS.**

Tier distinctness *as written*: no ladder has two tiers whose declared `value`/`method` string is the
same (script check, 23/23 ladders). But three ladders take an outcome from a **product
parameter**, so the outcome collapses onto the fall-through for some products of the charter:
- `named_instructor_charge` (tier 1 = `P('instructor_request_fee_usd')`, fall-through = `0.00`):
  collapses for All-Mountain Adult (0.00), Mountain Explorers (0.00), Mountain Cubs (0.00), Six-Week
  Development Programme (0.00) and Elite Performance Camp (0.00). For the Elite Performance Camp the
  collapse is also an unreal outcome: `instructor_request_allowed` is true and a *pending* request
  costs `K('provisional_instructor_charge')` = 35.00 while a *confirmed* one costs 0.00, so the
  household pays less for a request the school has agreed to than for one it has not.
- `laid_on_extras_makegood` (tier 1 = `P('rental_addon_usd')`, fall-through = `K('no_addon_makegood')`
  = 0.00): collapses for Mountain Explorers (0.00) and Mountain Cubs (0.00).
- `notice_band_fee` (fall-through = `P('reschedule_fee_usd')` = 25/25/25/95/45/75/250) never collapses
  onto 20.00 or 35.00 for any product.
Finding **F-5** (charter-global; whether either collapse is instantiated is a per-task question).

Conditions and outcomes that the line of business actually holds — reviewed tier by tier. The
conditions are all things a snowsports school genuinely weighs (how much of a block was taught before
a storm day; whether a makeup date is still open; how many extras were laid on; whether the
participant skied anyway on their own pass; how much credit stands and how it compares to the minimum
redemption and to the bill; how many sessions are still to come on an instalment product; how much of
the tuition is already paid; how far ahead of the due date the household is paying; how far ahead the
booking was made; whether the household is staying on the mountain and on what rate window and with
what deposit; whether a named instructor was asked for and agreed; how big a block is held; how long
the session runs; how much notice a move gives; how many nights the stay holds; how many sessions a
move disturbs). None of them holds of every customer who reaches the write. Two exceptions are
recorded:
- **F-6** — `lessons_ext_date_change_fee.tuition_share_cap` fall-through: "Where no tuition stands on
  the booking, the ceiling is nothing", i.e. the move fee is **zero** whenever the school has not yet
  invoiced the booking. Taken with `block_move_method`'s fall-through this makes the policy's declared
  baseline self-contradictory; see F-6 in full below.
- `makeup_answer_method` tier 2 ("outside the makeup period -> the whole session value, the weather
  share not applied") coincides numerically with tier 3 whenever the weather share stands at
  `K('late_block_share')` = 100. The two tiers remain distinct *as methods* and the coincidence is
  confined to one value of another ladder, so this is recorded as observation OBS-6, not a collapse.

Baseline coherence (each policy's `baseline.rule` read on its own, against the number the factors'
fall-through bindings actually produce):
- `lessons_ext_weather_session_credit`: baseline.rule -> session value x standard weather share, no
  extras, no offset. Fall-through bindings: `weather_share = K('standard_weather_share')`,
  `made_good = session_value * weather_share / 100`, `addon_makegood = K('no_addon_makegood')`,
  `pass_offset = K('no_pass_offset')`. **Agree.** `baseline.params` names exactly the keys used.
- `lessons_ext_balance_settlement`: baseline.rule -> the figure owed, rounded. Fall-throughs give
  `credit_set_against = 0`, `instalment_share = 100`, `standing_points = 0`, `prompt_reduction = 0`
  -> `RND(figure_owed, 2)`. **Agree.**
- `lessons_ext_session_tuition_charge`: baseline.rule -> the block price, rounded. Fall-throughs give
  `priced_figure = base_price` and all four additions/reductions at zero -> `RND(base_price, 2)`.
  **Agree.**
- `lessons_ext_lift_access_addon`: baseline.rule -> lift ticket add-on price x sessions the booking
  holds, rounded. Fall-throughs give `access_basis = P('lift_ticket_addon_usd') * F('sessions_booked')`
  and all three point reductions at zero. **Agree.**
- `lessons_ext_date_change_fee`: baseline.rule -> **the product's move fee**, rounded. Fall-throughs
  give `notice_fee = P('reschedule_fee_usd')` (agreeing), but then
  `moved_fee = raw_fee * K('unallocated_share') / 100` (half the move fee) and
  `cap_share = K('no_cap_share')` -> `fee_ceiling = tuition_standing * 0 = 0` ->
  `result = MN(moved_fee, 0) = 0`. **Do not agree**, and `baseline.params`
  (`[reschedule_fee_usd, no_addon_handling, no_instructor_rebooking, no_relief, no_cap_share]`) does
  not even name `unallocated_share`, the key its own fall-through binding uses. Finding **F-6**.

### findings

---

**F-1 — observation (undeclared override; consequence not demonstrable on either task of this difficulty)**

- *Symptom*: `lessons_ext_weather_session_credit` cites `lessons_session_delivery` in
  `base_policy_refs` but names no sentence of it in `overwrite`, while replacing the quantity that
  policy's weather sentence governs.
- *Root cause*: the same promise is written in two base policies. The author superseded the
  `lessons_cancellation` copy and left the `lessons_session_delivery` copy standing.
- *Evidence*: base, `env/env_0004_ski_resort_operator/blueprint/products/lessons.yaml` (`lessons_session_delivery.rule`):
  "Where a session is lost to weather or mountain conditions the collective makes good on the
  product's weather basis, and that session is not drawn from the block."
  Extended, `lessons.extended.yaml` (`lessons_ext_weather_session_credit.overwrite`): the only entry
  names `lessons_cancellation`. Extended rule: "The amount made good is the value of one session taken
  at the standard weather share" with `standard_weather_share: 50`.
- *Consequence*: base and extended reach different conclusions for any product whose
  `weather_cancellation_basis` is `full_credit` (All-Mountain Adult, Mountain Explorers,
  Semi-Private Coaching Session) or `full_refund` (Mountain Cubs, Private Instruction Full Day): base
  says the whole session value comes back, extended says 50% at the standard share. Neither task of
  this difficulty instantiates this policy on such a product — the only booking this policy is scored
  on is an Elite Performance Camp, whose basis is `partial_credit`
  (`blueprint/products/lessons.yaml`, Elite Performance Camp `weather_cancellation_basis`), a
  qualitative value the extended policy refines rather than contradicts. So the consequence table's
  "two passages, same situation, different conclusion" cannot be demonstrated on the worlds actually
  scored here. Recorded as an observation; the undeclared override is real.
- *Artifact and location*: `env/env_0004_ski_resort_operator/tasks/snowsports_school_desk/lessons.extended.yaml`,
  `lessons_ext_weather_session_credit.overwrite`.
- *Bears on*: task 0 (demonstration of non-consequence in `0.md`).

---

**F-2 — observation (terminal-state omission)**

- *Symptom*: `lessons_ext_balance_settlement`'s rule consumes school credit arithmetically ("the whole
  of the credit standing is set against the figure owed and money is taken only for what is left")
  but nothing records the consumption, so the credit still stands in full afterwards.
- *Root cause*: this difficulty owns no tool that writes a `lessons_credit_redeem` row, although
  `lessons_credit_redeem` is in the difficulty's claimed `event_types`
  (`blueprint/blueprint.yaml`, `snowsports_school_desk.claim.event_types`), and
  `settle_school_balance_78bdef11` touches only `lessons_ledger` (a `lessons_payment` row) and
  `lessons_holdings.tuition_balance_usd`.
- *Evidence*: `task_tools.py` lines 47-95 (`settle_school_balance_78bdef11` body — `ctx.create(...
  event_type="lessons_payment" ...)`, `ctx.update("lessons_holdings", lesson_id,
  tuition_balance_usd=outstanding)`; `lesson_credit_usd` untouched). Base
  `lessons_credit_use.subject: [lessons_credit_redeem]`; `lessons.yaml` `accounts.lesson_credit`:
  "…and spent when it is applied against a school charge."
- *Consequence*: the scored parameter is unaffected (the offset is an input to the payment amount),
  but the terminal state after the gold run shows the full credit still standing on the booking while
  the household has already had the benefit of it, so the same credit could be offset again on a
  second settlement. A terminal-state defect, not a second answer; recorded as an observation because
  the demonstration table asks for a second reading producing a different scored value, and there is
  none.
- *Artifact and location*: `lessons.extended.yaml`, `lessons_ext_balance_settlement.rule` /
  `compute.credit_set_against`; `task_tools.py`, `settle_school_balance_78bdef11`.
- *Bears on*: task 0.

---

**F-3 — observation (undeclared override; consequence not demonstrable on either task of this difficulty)**

- *Symptom*: `lessons_ext_session_tuition_charge` replaces the tuition basis of `lessons_pricing` but
  silently drops the reduction sentence that follows it, naming only the basis sentence in `overwrite`.
- *Root cause*: `overwrite` was written against the sentence that defines the *base figure* and not
  against the sentence that defines what is *taken off* it.
- *Evidence*: base `lessons_pricing.rule`: "The season passholder reduction is taken first where the
  product carries one and the participant is shown on the collective's records as holding a pass in
  the active state, then the group reduction, and the result is rounded to the cent."; base
  `lessons_pricing.formula.amount_usd`:
  `round(tuition_before_discount_usd * (1 - multi_booking_discount_pct / 100), 2)`; base
  `lessons_agg_household_group_pricing.rule` (same ordering restated).
  Extended `lessons_ext_session_tuition_charge.overwrite` names only "The tuition raised for a booking
  is the product's block price where the product is sold as a block, …"; the extended `rule` and
  `compute` mention neither reduction.
- *Consequence*: an agent reading base would take the passholder reduction and then the group
  reduction off the figure the extended policy prices, giving a different tuition. On the only world
  this policy is scored on, neither reduction is applicable: `group_minimum_participants: 2` and the
  account carries exactly one `lessons_holdings` row, so the multi-booking/sibling reduction does not
  arise; and the participant holds no season pass, so the passholder reduction does not arise (row
  evidence in `1.md`). The base charter also fixes no percentage for the passholder reduction
  anywhere in `parameter_schema` (`passholder_discount_applies` is a boolean and there is no
  `passholder_discount_pct`), so that half of the base sentence is unquantified in the source itself.
  Consequence therefore not demonstrable here; the undeclared override is real.
- *Artifact and location*: `lessons.extended.yaml`, `lessons_ext_session_tuition_charge.overwrite`.
- *Bears on*: task 1.

---

**F-4 — SOURCE-FACTOR RED (mislabelled effect; per-policy `method` floor not met)**

- *Symptom*: `lessons_ext_session_tuition_charge.factors[advance_rate_method]` is declared
  `effect: method`, but its three tiers substitute a rate into one unchanged formula.
- *Root cause*: a per-tier multiplier has been booked as an algorithm change.
- *Evidence*: `lessons.extended.yaml`, `lessons_ext_session_tuition_charge`:
  `compute.priced_figure: "base_price * K('early_booking_multiplier') if (advance_days >= 21 and
  P('advance_booking_days_max') >= 120) else (base_price * K('ahead_booking_multiplier') if
  (advance_days >= 21 and P('advance_booking_days_max') < 120) else base_price)"`, with
  `params.early_booking_multiplier: 0.90`, `params.ahead_booking_multiplier: 0.95`. The ladder's own
  wording calls each outcome a *multiplier*: "the block price is taken at the early booking
  multiplier" / "…at the ahead booking multiplier" / "the block price stands as it is" (i.e. x 1.00).
  Contrast a genuine method factor in the same charter, `session_length_method`, whose tiers change
  which count the price is taken on (`sessions_loaded` vs `F('sessions_booked')`).
- *Consequence*: counting only factors that pass the honesty test, this policy declares **5
  `parameter` factors and 0 `method` factors**, below the floor of at least one `method` per
  computation. The policy's ladder set therefore tests only which numbers are substituted and never
  which algorithm is chosen, which is precisely what the `method` floor exists to prevent.
- *Artifact and location*: `lessons.extended.yaml`,
  `lessons_ext_session_tuition_charge.factors[0]` (`advance_rate_method`), `effect` key and ladder.
- *Bears on*: task 1 (`factor_weight` in `1.md` records the tier taken and the recomputation).

---

**F-5 — observation (product-dependent tier collapse; not instantiated in this difficulty)**

- *Symptom*: two ladders take their top tier from a product parameter that is `0.00` for several
  products, making that tier select the same value as the fall-through.
- *Root cause*: `P(...)` in a tier outcome is not constrained to differ from the policy's `K(...)`
  fall-through across the charter's variants.
- *Evidence*: `lessons_ext_session_tuition_charge.factors[named_instructor_charge]` tier 1 =
  `P('instructor_request_fee_usd')`, fall-through = `K('no_instructor_charge')` = `0.00`;
  `instructor_request_fee_usd` is `0.00` for All-Mountain Adult Group Lesson, Mountain Explorers Group
  Lesson, Mountain Cubs Group Lesson, Six-Week Development Programme and Elite Performance Camp
  (`blueprint/products/lessons.yaml`, `variants[].parameters`).
  `lessons_ext_weather_session_credit.factors[laid_on_extras_makegood]` tier 1 =
  `P('rental_addon_usd')`, fall-through = `K('no_addon_makegood')` = `0.00`; `rental_addon_usd` is
  `0.00` for Mountain Explorers Group Lesson and Mountain Cubs Group Lesson.
  Additionally, for the Elite Performance Camp `instructor_request_allowed` is `true` while
  `instructor_request_fee_usd` is `0.00` and `K('provisional_instructor_charge')` is `35.00`, so a
  *confirmed* named-instructor request costs the household less than a *pending* one.
- *Consequence*: on a booking of any of those products the ladder has two distinct outcomes rather
  than three. Neither task of this difficulty instantiates such a booking for the affected policy —
  task 0's weather credit is on an Elite Performance Camp (`rental_addon_usd` = 89.00, distinct from
  0.00) and task 1's tuition charge is on a Semi-Private Coaching Session
  (`instructor_request_fee_usd` = 75.00, distinct from `provisional_instructor_charge` 35.00 and from
  0.00) — so the consequence is not demonstrable on the scored worlds. Observation.
- *Artifact and location*: `lessons.extended.yaml`, the two factors named.
- *Bears on*: neither task's scored value; recorded here for the charter.

---

**F-6 — SOURCE-FACTOR RED (dishonest / incoherent baseline)**

- *Symptom*: `lessons_ext_date_change_fee` declares a `baseline` whose prose and whose factor
  fall-throughs give two different numbers. A reader who computes from `baseline.rule` alone gets the
  product's move fee; substituting every factor's `baseline` binding gives **0.00** on every world.
- *Root cause*: two of the six factors put something other than the standard method into their
  fall-through tier — `block_move_method` halves the figure, and `tuition_share_cap` sets a ceiling of
  nothing, which multiplies the whole fee by zero. `baseline.rule` states neither a halving nor a
  ceiling.
- *Evidence*: `lessons.extended.yaml`, `lessons_ext_date_change_fee`:
  - `baseline.rule`: "The fee for a change of date is the product's move fee, and the figure is
    rounded to the nearest cent. A move does not reprice the booking, so the tuition already standing
    on it is untouched by the change." — no halving, no ceiling.
  - `baseline.params`: `[reschedule_fee_usd, no_addon_handling, no_instructor_rebooking, no_relief,
    no_cap_share]` — does **not** name `unallocated_share`, although
    `factors[block_move_method].baseline.moved_fee` is `"raw_fee * K('unallocated_share') / 100"`
    (`params.unallocated_share: 50`).
  - `factors[tuition_share_cap].baseline.cap_share`: `"K('no_cap_share')"` with
    `params.no_cap_share: 0`, feeding `fee_ceiling: "tuition_standing * cap_share / 100"` and
    `result: "RND(MN(moved_fee, fee_ceiling), 2)"` — a 0-multiplier on the whole fee.
- *Consequence (recomputed by this auditor on the one world the policy is scored on, task 1's, using
  the policy's own `compute` under `skills/erl-task-instantiate/scripts/check_compute.py`)*:
  - from `baseline.rule` alone, for a Semi-Private Coaching Session (`reschedule_fee_usd` = 45.00):
    **45.00**;
  - substituting every factor's `baseline` binding at once: **0.00**.
  Two different "definite fall-back numbers" for the same declared baseline. This is the straw-man
  form the audit names explicitly ("a zero where the standard method gives a figure") plus the
  0/1-multiplier form ("an existence condition multiplied onto an amount the base has already fixed,
  zeroing it out"). It also makes the policy's declared baseline not self-sufficient in the sense
  required: the reader who follows `baseline.rule` and the reader who follows the factors' fall-through
  tiers do not arrive at the same number.
- *Artifact and location*: `lessons.extended.yaml`, `lessons_ext_date_change_fee.baseline` (rule and
  params), `factors[block_move_method].baseline`, `factors[tuition_share_cap].baseline`,
  `compute.fee_ceiling`, `compute.result`.
- *Bears on*: task 1 (`factor_weight` and `source_gt_comparison` in `1.md` carry the figures).

---

**OBS-1** — `lessons_ext_balance_settlement.compute_basis` has no entry for the bindings `figure_owed`
and `instalment_due`. Both are arithmetic over based quantities and both are covered by rule sentences
quoted under neighbouring keys, so no basis is invented; the coverage table is incomplete.
(`lessons.extended.yaml`, `lessons_ext_balance_settlement.compute_basis`.)

**OBS-2** — `lessons_ext_weather_session_credit.compute_basis` attaches the pass-offset ladder's three
rule sentences to the wrong bindings (`active_pass` <- the skied-on sentence, `pass_scans_recent` <-
the idle-pass sentence, `pass_offset` <- the no-pass sentence). Each is a genuine rule sentence and
together they state the whole ladder.

**OBS-3** — `lessons_ext_balance_settlement.compute.settled_ratio` divides by `MX(SUM(tuition), 1)`;
the rule states only "measured against the tuition raised on it" and declares no floor of 1 on the
denominator.

**OBS-4** — `lessons_ext_balance_settlement` reads credit through
`SUM('lessons_ledger','amount_usd', event_type='lessons_credit_issue')` with no window and no ordering,
while base `lessons_credit_use` (inherited in full, `overwrite: []`) makes credit conditional on its
validity period (`P('credit_validity_days')`) and on the booking's state, and orders multiple entries
"closest to running out … first". The extended policy restates none of these; on a world with an
out-of-date credit entry or two entries of different ages the two would part company.

**OBS-5** — base `lessons_pricing`: "A product sold with a deposit raises the whole tuition at once and
collects the deposit share of it at booking, with the balance falling due later." Where a booking
stands confirmed with no tuition entry at all, the tuition raise and the deposit collection have both
been missed; `lessons_ext_session_tuition_charge` raises the tuition and this difficulty owns no write
for the accompanying deposit. Recorded for world realism, not as a conflict.

**OBS-6** — `lessons_ext_weather_session_credit.factors[makeup_answer_method]`: tier 2 ("the whole
session value, the weather share not being applied to it at all") and tier 3 ("the session value taken
at the weather share") coincide numerically whenever `block_progress_share` has selected
`K('late_block_share')` = 100. They remain distinct as methods and the coincidence depends on another
ladder's tier, so this is not a same-outcome collapse.

**OBS-7** — `lessons_ext_weather_session_credit.compute.days_since_loss` is
`DAYS(storm_notice_date, NOW)` where `storm_notice_date` is a `LATEST` over `lessons_requests` with
`stated_reason='mountain_conditions'`. Bindings are evaluated eagerly, so on any world where this
policy fires with no such request row the calculation is undefined rather than falling through to the
"product allows no makeup session" tier (reproduced: evaluating this policy against task 1's world
raises `ValueError: invalid literal for int() with base 10: 'None'`). The rule assumes a request
exists but never says so.

**OBS-8** — `lessons_ext_weather_session_credit.rule` says "Where the participant holds a season pass
standing in the active state…", while `compute` reads `EXISTS('passes', status='active')` and
`XCOUNT('passes','passes_ledger', …)`, both of which `check_compute.build_env` scopes to the
**customer**, not to the participant. On a household holding a pass for a different member, rule and
compute would part company. On task 0's world the account holds exactly one pass and its
`passholder_name` is the booking's `participant_name`, so the two readings coincide.

**OBS-9** — `lessons_ext_session_tuition_charge.factors[rate_window_supplement]` declares
`bindings: [stay_rate_plan, window_supplement]`, but its ladder conditions ("the household holds a
lodging reservation standing in the confirmed state priced on the holiday window") and its compute
branch both also test `stay_status`, which is declared under a sibling factor. The binding *sets* stay
disjoint, so the structural rule holds; the declaration under-states what the tier rests on.


---

## closing_checklist

Written after both tasks' `source_derivation_frozen` and `source_gt_comparison` sections landed
(reveal time 2026-09-17T19:10Z). This section is post-reveal and sits below the pre-reveal
charter-global section by construction.

**The difficulty does not close.** Two of the four relationships fail on task 1.

| relationship | task 0 | task 1 |
| --- | --- | --- |
| policy self-consistency | PASS | PASS |
| the problem tree holds | PASS | PASS (with T1-F-A) |
| factors bear weight | PASS | **SOURCE-FACTOR RED** (F-6, F-4, T1-F-C) |
| unique solution | PASS | **SOURCE-TASK RED** (T1-F-B) |

Step 4's list, item by item:

- **Audit files correspond one-to-one with the tasks.** `0.md` and `1.md` sit beside this file in
  `env/env_0004_ski_resort_operator/audits/policy_task/snowsports_school_desk/`. This is revision 1; there are
  no older revisions to preserve. Every comparison section carries a verdict; **`1.md`'s does not
  carry a PASS.**
- **Extended policies fully covered; task scopes pairwise disjoint.** Confirmed pre-reveal from the
  `prerequisite` graph and confirmed again against the revealed `charter_scope`:
  task 0 = `{lessons_ext_weather_session_credit, lessons_ext_balance_settlement}`,
  task 1 = `{lessons_ext_session_tuition_charge, lessons_ext_lift_access_addon,
  lessons_ext_date_change_fee}`. Disjoint, and together all five. Each scope spans a whole problem
  tree — root plus every prerequisite problem. Tool sets likewise disjoint (2 + 3 = the 5 in
  `task_tools.py`), and each tool's uuid8 is independently generated, frozen, unreused and not
  batch-derived (§ `action_binding_and_uuids`).
- **Problem trees.** Task 0: 1 prerequisite problem, 1 `value_input` edge (floor `max(0,1)` = 1), one
  `owner=user` write (the root), no cycle. Task 1: 2 prerequisite problems, 2 `value_input` edges
  (floor 1), one `owner=user` write (the root), no cycle. Across the difficulty the three edges form
  a DAG in two disjoint components; no cross-task reference creates a cycle. One qualification:
  task 1's tuition edge is declared `value_input` but operates as a `state_gate` (`1.md`, T1-F-A); the
  floor is met independently by the add-on edge.
- **Baselines and factors.** 23 factors over 5 computations; every ladder has 3 tiers stated in full
  in its own `rule`; no ladder has two tiers whose declared value or method is the same; every factor
  was proved to bear weight on its task's world by an explicit baseline substitution (`0.md`
  § `factor_weight`, `1.md` § `factor_weight`), with every figure matching the artifacts'
  `factor_sensitivity` figure for figure. **Three failures**:
  - `lessons_ext_date_change_fee` has no self-sufficient baseline — its `baseline.rule` reads to 45.00
    on task 1's world while its factors' fall-through bindings give 0.00 (F-6; `computations[2]
    .baseline_result` records the 0.00);
  - `lessons_ext_session_tuition_charge` has no honest `method` factor (F-4);
  - the lodging rows four of task 1's factors read contradict the lodging charter's own deposit rule
    (1290.00 seeded against 1877.04 the charter fixes) and two further lodging fields
    (`deposit_due_date`, `nights_remaining`) contradict it as well (`1.md`, T1-F-C).
  Two computations of the difficulty (task 0's settlement, task 1's add-on and change fee) carry no
  near-miss record; recorded as observations T0-OBS-C and T1-OBS-B.
- **Instantiation-stage gates re-run on the final form** (2026-09-17T19:15Z, from the repository
  root, `.venv/bin/python skills/erl-task-instantiate/scripts/<gate>.py
  env/env_0004_ski_resort_operator/tasks/snowsports_school_desk`):
  `EXTENDED OK`, `TASK TOOL CONTRACT OK`, `REPLAY OK` (0.json 11 acts / 16 closure rows matched,
  1.json 13 acts / 8 matched), `SOLVABILITY OK`, `COMPUTE OK` (suite means branches 30.50, steps
  12.00; depth history_rows_max 12, branches_max 39), `GROUNDING OK`, `SCOPE OK`.
  `TRACEABILITY NOT OK` — its five misses are exactly the five hidden task-tool names
  (`issue_weather_session_credit_1ce20aea`, `settle_school_balance_78bdef11`,
  `raise_session_tuition_charge_38aef0d5`, `raise_lift_access_addon_aea17349`,
  `confirm_lesson_date_change_58e66cab`), which the later KB render step publishes through each
  policy's `target_tool`; unchanged from the entry snapshot and not a defect of this stage.
  **Every gate that can run is green, and the difficulty still fails this audit** — which is the
  point of running it.

### findings index

| id | verdict | where the consequence is demonstrated |
| --- | --- | --- |
| F-1 | observation (undeclared override) | `0.md` § policy_self_consistency |
| F-2 | observation (terminal-state omission) | `0.md` § policy_self_consistency |
| F-3 | observation (undeclared override) | `1.md` § policy_self_consistency |
| **F-4** | **SOURCE-FACTOR RED** (mislabelled `method`; policy left with none) | `1.md` § policy_self_consistency, § factor_weight |
| F-5 | observation (product-dependent tier collapse, not instantiated) | `_difficulty.md` only |
| **F-6** | **SOURCE-FACTOR RED** (dishonest / incoherent baseline) | `1.md` § policy_self_consistency, § factor_weight, § source_gt_comparison |
| OBS-1 … OBS-9 | observations | `_difficulty.md` |
| T0-OBS-A … T0-OBS-D | observations | `0.md` § findings |
| T1-F-A | SOURCE-CHAIN observation (`value_input` acting as `state_gate`) | `1.md` § findings |
| **T1-F-B** | **SOURCE-TASK RED** (two readings of `session_date`) | `1.md` § findings |
| **T1-F-C** | **SOURCE-FACTOR RED** (cross-difficulty rows contradict the lodging charter) | `1.md` § findings |
| T1-OBS-A … T1-OBS-D | observations | `1.md` § findings |

---

# revision_2 — re-audit of the reworked form (charter-global)

## charter_global_frozen (revision 2)

- Auditor: same independent policy-task auditor. Revision 1 above is left untouched.
- Freeze time (charter-global section): 2026-09-17T20:05Z. **Written before any revision-2 GT field was
  read.** Revision 1's GT is known to this auditor, so revision 2 is not a blind audit; its question is
  narrower — is each revision-1 RED genuinely closed, has the rework introduced anything new, has
  anything that passed regressed.
- Hashes, compared against the round that produced each section (revision 1):

| artifact | revision 1 | revision 2 | re-derivation |
| --- | --- | --- | --- |
| `lessons.extended.yaml` | `ccaa40cd9520ae99` | **`1018928d2a2d2824`** | **changed -> every charter-global section re-derived in full** |
| `task_tools.py` | `7abc9779ff7c3bdf` | `7abc9779ff7c3bdf` | unchanged |
| `tasks/0.json` (masked) | `3b5aa50ba28bd840` | **`00946864c6733295`** | changed -> task 0 re-derived |
| `tasks/1.json` (masked) | `c91118905e02a626` | **`e92c476084c884e7`** | changed -> task 1 re-derived |

  The charter changed, so **no section is carried forward by reference**; all of
  `policy_conflict_scan`, `rule_compute_equivalence`, `action_binding_and_uuids`, `prerequisite_graph`,
  `prerequisite_sentences`, `override_declarations` and `factor_ladders` were re-derived below against
  the new file. `task_tools.py` being byte-identical is recorded as a finding in its own right, not
  only as grounds (see R2-F-2).
- Masked-out keys, unchanged from round 1: `charter_scope`, `computations`, `db_closure`,
  `db_closure_matches_initial_state`, `design_rationale`, `evaluation_criteria`,
  `prerequisite_closure`, `required_documents`, `solvability_contract`.
- Entry conditions: the coordinator supplied the re-run gate snapshot (EXTENDED / TASK TOOL CONTRACT /
  REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK; TRACEABILITY unchanged pre-render). Not
  re-run by this auditor at the freeze stage; re-run once on the final form under
  `closing_checklist (revision 2)`.

### base_section_verbatim (revision 2)
`head -1357` of the new `lessons.extended.yaml` is still byte-identical to
`blueprint/products/lessons.yaml` (`diff` empty). **No regression.**

### policy_conflict_scan (revision 2)

Still five extended policies, the same five subjects, the same five `computes` names, the same five
target tools and the same two-tree partition of the charter:

```
task-0 tree : lessons_ext_balance_settlement  -> lessons_ext_weather_session_credit
task-1 tree : lessons_ext_date_change_fee     -> lessons_ext_session_tuition_charge
                                              -> lessons_ext_lift_access_addon
```

Pairwise disjoint, jointly complete, unchanged from revision 1. Triggers, eligibility, time anchors,
objects and terminal states remain non-overlapping.

Cross-category read boundaries have **moved**, and the declarations moved with them:
- `lessons_ext_weather_session_credit` still reads `passes` as `history` (`status`,
  `passes_ledger.event_type`) — unchanged.
- `lessons_ext_session_tuition_charge` reads `lodging` as `branch`, now declaring
  `[status, rate_plan, lodging_folio.amount_usd]` — unchanged set, one more consumer
  (`reduction_selection_method` also reads `status`), and the `note` was rewritten to name all three
  consuming factors. Declared exactly.
- `lessons_ext_lift_access_addon` reads `lodging` `[status, rate_plan]` — unchanged.
- `lessons_ext_date_change_fee` now reads `lodging` **`[status, departure_date]`** where revision 1
  read `[status, nights_booked]`. `CFIELD('lodging','departure_date')` is the only new read and it is
  declared. No undeclared read anywhere.

**PASS.**

### rule_compute_equivalence (revision 2)

Machine-checked over all five policies against the new file:

- every `compute` binding now carries a `compute_basis` entry — **0 misses in all five policies**
  (revision 1 had two, `figure_owed` and `instalment_due`: **OBS-1 closed**);
- no `compute_basis` key is an orphan;
- every `baseline.rule` is a verbatim run of sentences of its own policy's `rule` (5/5);
- every declared factor ladder tier is a sentence of the `rule` and a branch of its `decides` binding,
  and every branch of each `decides` binding is a tier the rule states (checked policy by policy; no
  tier lives only in `compute`, none only in prose).

**Two `compute_basis` values are no longer verbatim substrings of their own rule** — a regression
against revision 1, which was clean on this test for all five policies:

1. `lessons_ext_weather_session_credit.compute_basis.storm_notice_date` ends
   "…every day of the week counting alike." The rule now reads
   "…every day of the week counting alike**;** where no request raised over a lost session stands
   against the booking, the handling date is taken to fall outside that makeup period." The quote
   substitutes a full stop for the semicolon and drops the clause, so it is not verbatim.
2. `lessons_ext_balance_settlement.compute_basis.settled_ratio` reads
   "judged as the payments collected on the booking measured against the tuition raised on it. Where
   no tuition has been raised on the booking there is nothing for the payments to be measured against
   and no points are allowed on that count." The first clause is mid-sentence in the rule (it is
   followed there by a colon and the three-tier ladder); the second is a **separate later sentence**.
   The quote fabricates a sentence boundary and elides the ladder between them.

Both were created by the very edits that closed OBS-3 and OBS-7 — clauses were added to the rules and
the quotations were not re-cut. Every fragment quoted is genuinely in the rule and the semantics agree,
so nothing is invented and no second reading follows. Recorded as observation **R2-OBS-1**.

`settled_ratio`'s undeclared `MX(..., 1)` guard of revision 1 is gone: the compute is now
`SUM(payments) / SUM(tuition) if SUM(tuition) > 0 else 0`, and the rule states the zero branch outright
("Where no tuition has been raised on the booking there is nothing for the payments to be measured
against and no points are allowed on that count"). **OBS-3 closed.**

`days_since_loss` is now `DAYS(storm_notice_date, NOW) if storm_notice_date else
P('makeup_booking_days') + 1`, and the rule states the branch ("where no request raised over a lost
session stands against the booking, the handling date is taken to fall outside that makeup period").
The eager-evaluation crash of revision 1 is gone. **OBS-7 closed.**

`lessons_ext_weather_session_credit`'s pass-offset bases are now attached to the right bindings
(`active_pass` and `pass_scans_recent` <- the lead sentence about the lift records, `pass_offset` <-
the ladder sentence). **OBS-2 closed.**

Otherwise **PASS**.

### action_binding_and_uuids (revision 2)

Re-derived because the charter changed. `(target_tool, computes)`: five policies, five distinct tools,
five distinct computed bindings (`credit_amount_usd`, `payment_amount_usd`, `tuition_amount_usd`,
`addon_charge_usd`, `change_fee_usd`), each claimed by exactly one policy. Unchanged from revision 1.
uuid8 tails `1ce20aea`, `78bdef11`, `38aef0d5`, `aea17349`, `58e66cab` — the module is byte-identical,
so the revision-1 conclusion (pairwise distinct, no shared prefix, no sequence, not batch-derived)
stands on the recorded hash `7abc9779ff7c3bdf`. Docstring silence about sequence likewise unchanged.
**PASS.**

### prerequisite_graph (revision 2)

Same three edges, all `kind: value_input`, all `form: state`, no `fallback_reason` anywhere.

| blocked policy | problem | gate | binding in the blocked compute? | resolved_by |
| --- | --- | --- | --- | --- |
| `lessons_ext_balance_settlement` | `lessons_ext_weather_session_credit` | `credit_standing` | yes | `issue_weather_session_credit_1ce20aea` |
| `lessons_ext_date_change_fee` | `lessons_ext_session_tuition_charge` | `tuition_standing` | yes | `raise_session_tuition_charge_38aef0d5` |
| `lessons_ext_date_change_fee` | `lessons_ext_lift_access_addon` | `addon_entries` | yes | `raise_lift_access_addon_aea17349` |

DAG, two components, depth 1; no policy points at itself or at a base policy; every `prerequisite` is
filled in (`[]` on the three leaves); every `resolved_by` is the depended-on policy's own
`target_tool`; no authoring-viewpoint phrasing. `kind: value_input` on the **tuition** edge is now
honest — the gate `tuition_standing` feeds `value_component = tuition_standing * value_share / 100`,
an additive term, where revision 1 fed a `MN(...)` ceiling that never bound (see R2-CLOSED-4 below).
**PASS.**

### prerequisite_sentences (revision 2)

All three `policy_source` strings are verbatim in the blocked policy's own `rule` (script check 3/3).
Two are unchanged from revision 1 and their revision-1 four-point derivations stand; one is **new**:

- `lessons_ext_date_change_fee` -> `lessons_ext_session_tuition_charge`, new sentence:
  > "The share of the tuition standing that is added to the fee is fixed only after the school account
  > carries the tuition entry due for the booking."
  Ordering connective *only after*; what it waits on is *the school account carries the tuition entry
  due for the booking*, a record-visible state in the words the ledger and `find_lesson_account_entries`
  use, with no action, performer or tool; it names no tool, policy id, snake_case token or row id; it
  is written at exactly the strength the edge's `condition` carries. Exactly one write of this
  difficulty brings that state about — `raise_session_tuition_charge_38aef0d5` is the only tool in
  `task_tools.py` creating a `lessons_tuition_charge` row — so the hop resolves uniquely, and the
  reader's route is: a tuition entry on the school account -> the only policy whose own rule describes
  raising tuition is `lessons_ext_session_tuition_charge` -> its rule gives the amount. One reading.
  The replaced revision-1 wording ("The ceiling the fee is held to is fixed only after…") named a
  ceiling the policy no longer has, so the change was forced by the F-6 rework rather than cosmetic.

No rule carries a second wording of any dependency, no other problem's tool name, policy id or route,
and no depended-on policy's rule restates a blocked policy's sentence. The ordering-connective sweep
over all five rules returns only within-computation sequencing ("…and **then** halved", "the share of
the tuition standing is added **last of all**", "The three reductions are **first** combined…").

**One new cross-problem statement appears and is not an ordering**, so it grounds no edge and needs
none, but it is a promise the charter does not keep — `lessons_ext_lift_access_addon.rule`:
> "…access for a date the lesson is later moved to is answered by the terms that price a change of
> date rather than by re-dating this entry."
`lessons_ext_date_change_fee`'s rule says nothing whatever about lift access, and
`confirm_lesson_date_change_58e66cab` writes only a `lessons_fee_charge` row and rewrites
`first_session_date` / `reschedule_count`. Recorded as **R2-F-3**.

Otherwise **PASS.**

### override_declarations (revision 2)

Re-swept sentence by sentence against each `base_policy_refs` entry. Every `superseded_clause` in the
file is verbatim locatable in the base policy it names (script check, 7/7 entries across five
policies — revision 1 had 5).

- `lessons_ext_weather_session_credit` now carries **two** entries: the `lessons_cancellation` weather
  sentence (as in revision 1) **and** `lessons_session_delivery`'s "Where a session is lost to weather
  or mountain conditions the collective makes good on the product's weather basis, and that session is
  not drawn from the block." **F-1 closed** — the duplicate promise is now declared, so the conflict
  with `full_credit` / `full_refund` products no longer sits undeclared.
- `lessons_ext_session_tuition_charge` now carries **two** entries: the block-price sentence (as in
  revision 1) **and** `lessons_pricing`'s "The season passholder reduction is taken first where the
  product carries one and the participant is shown on the collective's records as holding a pass in
  the active state, then the group reduction, and the result is rounded to the cent.", replaced by
  "The reductions this policy names are the only ones taken off the block price", which is a verbatim
  sentence of the new extended rule. **F-3 closed.** `lessons_agg_household_group_pricing`'s ordering
  sentence restates the same rule and is governed by the same declaration; its remaining sentences
  (group judged at the moment tuition is raised; bookings on different days not grouped) are inherited
  and not contradicted.
- `lessons_ext_balance_settlement` now carries **one** entry where revision 1 had `overwrite: []`:
  `lessons_credit_use`'s "School credit is applied only when it is applied no later than its validity
  period counted in calendar days from the day the credit was issued.", replaced by "Credit issued
  more than twelve months before the handling date has run out and no longer counts toward the credit
  standing". The compute implements it
  (`SUM('lessons_ledger','amount_usd', within_months=K('credit_validity_months'),
  event_type='lessons_credit_issue')`, `credit_validity_months: 12`) and the rule now also carries the
  ordering sentence ("…and where several credit entries stand they are counted together, the entry
  closest to running out being the first spent"). **OBS-4 closed.** One consequence of the
  declaration is recorded as **R2-OBS-2**: the override replaces a per-product period
  (`credit_validity_days` = 365 / 270 / 180 across the charter's variants) with a flat twelve months
  for every product, so `P('credit_validity_days')` is now dead for this policy.
- `lessons_ext_lift_access_addon` and `lessons_ext_date_change_fee` keep their single revision-1
  entries, both still verbatim. Re-swept: no other base sentence is handled differently.
  `lessons_change_terms`'s `move_notice_deadline` eligibility, its elapsed-hour counting rule and its
  "A move does not reprice the booking" sentence are all still inherited intact — the last is now
  restated in the extended rule and echoed in `baseline.rule`.

**PASS** — no undeclared override remains anywhere in the charter. This is the clean result revision 1
did not have.

### factor_ladders (revision 2)

| policy | factors | parameter | method | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| `lessons_ext_weather_session_credit` | 4 | 3 | 1 `makeup_answer_method` | `pass_day_offset` | `pass_day_offset` -> passes |
| `lessons_ext_balance_settlement` | 4 | 3 | 1 `credit_offset_method` | `credit_offset_method` | none |
| `lessons_ext_session_tuition_charge` | 6 | 5 | 1 `reduction_selection_method` | `resort_stay_points`, `reduction_selection_method` | `resort_stay_points`, `reduction_selection_method`, `rate_window_supplement` -> lodging |
| `lessons_ext_lift_access_addon` | 4 | 3 | 1 `session_length_method` | none | `resort_guest_ticket_points` -> lodging |
| `lessons_ext_date_change_fee` | 5 | 4 | **1 `guest_on_mountain_method` (contested)** | `instructor_rebooking_amount` | `guest_on_mountain_method` -> lodging |

All five are inside the 4-to-6 bound and meet the >= 2 `parameter` floor. Every ladder has exactly
three tiers, stated in full in its own `rule` with its condition and its value or method, implemented
as one ternary chain; every `decides` is an intermediate binding, never `result`; no ladder has two
tiers whose declared value or method string is the same (23 ladders checked); and every factor's
`bindings` set is disjoint from its siblings' within its policy — the three separate
`CFIELD('lodging','status')` bindings (`stay_status`, `selection_status`, `window_status`) in
`lessons_ext_session_tuition_charge` exist precisely to keep that disjointness while three factors
read the same field, which also closes revision 1's OBS-9 (`rate_window_supplement` now declares
`window_status`). **OBS-9 closed.**

**Label honesty, factor by factor.**

Genuine `method` — the tiers change how the quantity is computed, not which constant goes into one
formula:
- `makeup_answer_method` (halve the share-adjusted figure / drop the share and take the whole session
  value / apply the share) — unchanged from revision 1;
- `credit_offset_method` (offset the whole credit standing / offset only as much as the figure owed /
  offset nothing) — unchanged;
- `session_length_method` (price per session *loaded* / at the half-day share per session *loaded* /
  per session the *booking holds* — the multiplicand's source changes) — unchanged;
- `reduction_selection_method` — **new, and genuine**. Its tiers select
  `advance_points + stay_points`, `stay_points` alone, and `advance_points` alone: three different
  expressions over two record-derived quantities, not three constants. Its `baseline`
  (`taken_points: advance_points`) is its own fall-through tier. This is the honest `method` factor
  `lessons_ext_session_tuition_charge` lacked. **F-4 closed in that policy.**

**Not a genuine `method`: `guest_on_mountain_method`** in `lessons_ext_date_change_fee`. Its three
tiers are `raw_fee * K('resident_share') / 100`, `raw_fee * K('departed_share') / 100` and `raw_fee` —
one formula with a substituted policy constant (50 / 150 / 100), which is precisely the shape this
audit red-lighted as `advance_rate_method` in revision 1 (`_difficulty.md` § revision 1, F-4). The
mislabel has been removed from `lessons_ext_session_tuition_charge` and reintroduced, unchanged in
kind, in `lessons_ext_date_change_fee`. Counted honestly that policy declares **4 `parameter` factors
and 0 `method` factors**, below the floor of one `method` per computation. Recorded as **R2-F-1**.

**Conditions and outcomes the line of business actually holds.** Re-reviewed tier by tier over the
whole charter. The conditions are all things a snowsports school genuinely weighs, and none holds of
every customer who reaches its write. One new ladder draws an adverse note:
`guest_on_mountain_method` orders its outcomes **50% / 150% / 100%**, so the fall-through sits between
the two tiers: a household whose stay runs through the lesson date pays half the move fee, a household
with **no** lodging at all pays the whole fee, and a household whose stay with the same collective
ended before the lesson date pays **half as much again**. The distinguishing fact is not "on the
mountain or not" — a local with no reservation is equally not lodged and pays less than the departed
guest. Recorded as observation **R2-OBS-3** rather than a red light, because a rationale can be
constructed (a slot must be re-fitted for a party no longer housed on the hill) and the tier is not
the one taken on the only world the policy is scored on.

**Baseline coherence** — each policy's `baseline.rule` read on its own against the number the factors'
fall-through bindings produce:

| policy | `baseline.rule` reads to | factor fall-throughs give | agree? |
| --- | --- | --- | --- |
| `lessons_ext_weather_session_credit` | session value x standard weather share | same | yes |
| `lessons_ext_balance_settlement` | the figure owed, rounded | same | yes |
| `lessons_ext_session_tuition_charge` | the block price, rounded ("Where the booking earns no reduction the block price stands as it is, and nothing is added to it") | `taken_points` = `advance_points` = 0, all supplements 0 -> `RND(base_price, 2)` | yes |
| `lessons_ext_lift_access_addon` | add-on price x sessions the booking holds | same | yes |
| `lessons_ext_date_change_fee` | the product's move fee ("The fee stands as worked out for the booking, and nothing is added for the value of the tuition standing on it") | `notice_fee` = `P('reschedule_fee_usd')`, handling 0, rebooking 0, `moved_fee` = `raw_fee`, `value_share` = `K('no_booking_share')` = 0 -> `RND(reschedule_fee_usd, 2)` | **yes** |

`lessons_ext_date_change_fee`'s `baseline.params`
(`[reschedule_fee_usd, no_addon_handling, no_instructor_rebooking, no_booking_share]`) now names every
key its own fall-through bindings use — `guest_on_mountain_method`'s baseline is the bare `raw_fee`
and needs no constant, and the `unallocated_share` of revision 1 no longer exists. The two halves of
revision 1's F-6 — the halving fall-through and the zeroing ceiling — are both gone, and the
`MN(moved_fee, fee_ceiling)` cap has been replaced by an additive `+ value_component`.
**F-6 closed at the charter level**; the per-world figures are in `1.md` § revision 2.

### findings (revision 2)

Derived from the charter, the schema and the tool module alone, before any revision-2 GT was read.

---

**R2-F-1 — SOURCE-FACTOR RED (mislabelled `method`; the revision-1 F-4 pattern relocated)**

- *Symptom*: `lessons_ext_date_change_fee.factors[guest_on_mountain_method]` is declared
  `effect: method`, but its three tiers substitute a policy constant into one unchanged formula.
- *Root cause*: the rework removed the multiplier ladder from `lessons_ext_session_tuition_charge`
  (closing F-4 there, correctly, by replacing multipliers with percentage points and adding a genuine
  method in `reduction_selection_method`) and introduced a multiplier ladder of exactly the same shape
  in the other policy of the same task.
- *Evidence*: `lessons.extended.yaml`, `lessons_ext_date_change_fee`:
  `compute.moved_fee: "raw_fee * K('resident_share') / 100 if (stay_status == 'confirmed' and
  stay_departure >= F('first_session_date')) else (raw_fee * K('departed_share') / 100 if
  (stay_status == 'confirmed' and stay_departure < F('first_session_date')) else raw_fee)"`, with
  `params.resident_share: 50` and `params.departed_share: 150`. The three outcomes are
  `raw_fee x 0.50`, `raw_fee x 1.50` and `raw_fee x 1.00` — one formula, three constants, and the
  ladder's own wording calls each one a *share*. Compare the revision-1 finding F-4 against
  `advance_rate_method` (`base_price x 0.90 / 0.95 / 1.00`): the same shape, red-lighted then.
  Compare also the genuine method factors of this charter, whose tiers change **which quantities** are
  combined or **which record** supplies a multiplicand — `reduction_selection_method`
  (`advance_points + stay_points` / `stay_points` / `advance_points`), `credit_offset_method`
  (`credit_standing` / `figure_owed` / 0), `session_length_method` (`sessions_loaded` vs
  `F('sessions_booked')`), `makeup_answer_method` (halve / drop the share / apply the share).
- *Demonstrated consequence*: counting only factors that pass the honesty test,
  `lessons_ext_date_change_fee` declares **4 `parameter` factors and 0 `method` factors**, below the
  floor of at least one `method` per computation. The ladder set of the root computation of task 1
  then tests only which numbers are substituted and never which algorithm is chosen. The task-level
  `method` count also falls from 3 to 2 across its three computations.
- *Affected artifact and location*: `lessons.extended.yaml`,
  `lessons_ext_date_change_fee.factors[3]` (`guest_on_mountain_method`), `effect` key and ladder;
  `compute.moved_fee`; `params.resident_share` / `params.departed_share`.
- *Relation to previous revisions*: **new in revision 2**, and a relocation of revision 1's F-4 rather
  than a fresh kind of defect. F-4 itself is closed where it was raised.
- *Bears on*: task 1 (`1.md` § revision 2 `factor_weight`).

---

**R2-F-2 — observation (the tool module was not reopened)**

- *Symptom*: `task_tools.py` is byte-identical between the two rounds (`7abc9779ff7c3bdf`), although
  two revision-1 findings named the tool layer as the place the defect lives.
- *Evidence*: the two hashes; revision 1's F-2 ("`settle_school_balance_78bdef11` touches only
  `lessons_ledger` and `lessons_holdings.tuition_balance_usd`; `lesson_credit_usd` untouched") and
  T1-F-B (whose `session_date` Arg text, "the lesson date the lift access covers", is unchanged and
  still does not say which date it names — the disambiguation was put in the policy rule instead).
- *Assessment*: putting the `session_date` disambiguation in the **rule** is the better placement, not
  a worse one: a docstring that said "as the booking currently stands" would be a tool contract
  carrying policy, which this audit would have to raise separately. So the unchanged module is not
  itself a defect. It is recorded because it is the reason F-2 could not be closed from the tool side
  and because it makes revision 1's `action_binding_and_uuids` conclusion carry forward on the hash.
- *Relation to previous revisions*: new framing of revision 1's F-2 and T1-F-B.

---

**R2-F-3 — observation (a rule promise the charter does not keep)**

- *Symptom*: `lessons_ext_lift_access_addon.rule` now points at another policy's terms to answer for
  something those terms do not touch.
- *Root cause*: closing T1-F-B required the rule to say which date the add-on entry names; the
  sentence added also disposes of the date it does **not** name, by referring it elsewhere.
- *Evidence*: `lessons.extended.yaml`, `lessons_ext_lift_access_addon.rule`:
  > "The entry names the date the booking's first session is due to run at the moment the access is put
  > on the booking, and a date the household has asked the school to move the lesson to, which the
  > booking does not yet stand on, is never named; **access for a date the lesson is later moved to is
  > answered by the terms that price a change of date rather than by re-dating this entry.**"
  Against `lessons_ext_date_change_fee.rule`, read end to end: it prices a notice fee, a handling
  amount, a rebooking amount, a settling share and a share of the tuition standing, and says nothing
  whatever about lift access for any date. Against `task_tools.py`,
  `confirm_lesson_date_change_58e66cab`: it writes one `lessons_fee_charge` row and rewrites
  `first_session_date` and `reschedule_count`; it raises no add-on and re-dates none.
- *Demonstrated consequence*: the sentence is the sweep-back failure of check 2 — the rule makes a
  promise `compute` and the tools do not keep. On task 1's world the gold run leaves the household
  charged for lift access covering 2027-02-14 and holding none for 2027-02-15, the date the same
  transaction moves the lesson to, with the charter's only statement about that gap pointing at terms
  that do not fill it. No scored parameter admits a second reading as a result — the ambiguity
  revision 1 raised is genuinely gone — so this is recorded as an observation rather than a red light.
- *Affected artifact and location*: `lessons.extended.yaml`,
  `lessons_ext_lift_access_addon.rule`, third sentence of the opening paragraph.
- *Relation to previous revisions*: **new in revision 2**; it is the residue of closing T1-F-B, and it
  is the business half of that finding written into the charter rather than removed from it.
- *Bears on*: task 1.

---

**R2-OBS-1 — observation (two `compute_basis` quotations are no longer verbatim; a regression)**

Set out under § `rule_compute_equivalence (revision 2)`. `storm_notice_date` in
`lessons_ext_weather_session_credit` truncates its rule sentence at a semicolon and closes it with a
full stop; `settled_ratio` in `lessons_ext_balance_settlement` joins a mid-sentence clause to a later
separate sentence across a fabricated boundary, eliding the three-tier ladder between them. Both were
caused by the edits that closed OBS-7 and OBS-3. Every fragment is genuine rule text and the semantics
agree, so nothing is invented. Revision 1 was clean on this test for all five policies.

**R2-OBS-2 — observation (a per-product period replaced by a flat one)**

`lessons_ext_balance_settlement`'s new `overwrite` against `lessons_credit_use` replaces "no later than
its validity period counted in calendar days from the day the credit was issued" with a flat twelve
months (`params.credit_validity_months: 12`, `within_months=K('credit_validity_months')`). The
declaration makes the override legal and OBS-4 is closed by it, but the base parameter
`credit_validity_days` — 365 for the Elite Performance Camp, 270 for the Semi-Private Coaching
Session, 180 for the All-Mountain Adult Group Lesson — is now dead for this policy, and for products
whose period is not twelve months the extended figure is the one in force. Not engaged on either
task's world.

**R2-OBS-3 — observation (non-monotone ladder outcomes in `guest_on_mountain_method`)**

Set out under § `factor_ladders (revision 2)`: 50 / 150 / 100, so the fall-through sits between the two
tiers and a household with **no** lodging pays the standard fee while a household whose stay with the
same collective ended before the lesson date pays half as much again. The distinguishing fact does not
separate "on the mountain" from "not on the mountain", since the local with no reservation is equally
unlodged. Not the tier taken on the only world the policy is scored on.

**R2-OBS-4 — observation (residual wording in a `cross_category` note)**

`lessons_ext_weather_session_credit.cross_category[0].note` still reads "The pass offset factor decides
its tier from the **participant's own** season pass record…", while the rule, both tier conditions and
the `compute_basis` quotations were all changed to "the **household** holds a season pass standing in
the active state" to match the customer-scoped `EXISTS` / `XCOUNT`. OBS-8 is closed in the rule; the
note was not propagated. `cross_category` is part of the charter's general text.

## closing_checklist (revision 2)

Written after both tasks' revision-2 `source_derivation_frozen` and `source_gt_comparison` sections
landed (reveal 2026-09-17T20:40Z). Revision 1's closing checklist above is left untouched.

**The difficulty still does not close.** One of the four relationships fails on task 1 — one ground,
down from four.

| relationship | task 0 rev 1 | task 0 rev 2 | task 1 rev 1 | task 1 rev 2 |
| --- | --- | --- | --- | --- |
| policy self-consistency | PASS | **PASS** | PASS | **PASS** |
| the problem tree holds | PASS | **PASS** | PASS (with T1-F-A) | **PASS** (T1-F-A closed) |
| factors bear weight | PASS | **PASS** | SOURCE-FACTOR RED (F-6, F-4, T1-F-C) | **SOURCE-FACTOR RED** (R2-F-1 only) |
| unique solution | PASS | **PASS** | SOURCE-TASK RED (T1-F-B) | **PASS** (T1-F-B closed) |

### is each revision-1 RED genuinely closed, or merely reworded

| id | closed? | what was actually verified, against the artifact |
| --- | --- | --- |
| **F-6** (dishonest / incoherent baseline) | **genuinely closed** | not a rewording: the `MN(moved_fee, fee_ceiling)` cap was **removed** and replaced by an additive `value_component`; the `unallocated_share` constant no longer exists in the policy; `baseline.rule` gained a sentence that states the zero case outright; `baseline.params` now names every key its fall-throughs use. Recomputed on task 1's world: prose **45.00**, all-factor substitution **45.00** (revision 1: 45.00 against 0.00). |
| **F-4** (mislabelled `method`) | **closed where raised, reopened elsewhere** | `lessons_ext_session_tuition_charge`'s multiplier ladder was genuinely replaced by percentage points plus a real `method` (`reduction_selection_method`, three expressions over record-derived quantities). But the identical shape reappears as `guest_on_mountain_method` in `lessons_ext_date_change_fee` (`raw_fee x 50/100 / x 150/100 / x 1`). Recorded as **R2-F-1**. |
| **T1-F-C** (cross-difficulty rows contradict the lodging charter) | **genuinely closed** | the lodging rows were re-seeded and every figure re-derived here from `blueprint/products/lodging.yaml`: deposit **1877.04** = 30% x (8 x 869.00 x 0.90), `deposit_due_date` **2026-12-24**, `nights_remaining` **8** with a matching `lodging_nights_load` row, and a new `lodging_payment` of **4379.76** = 6256.80 − 1877.04, dated inside the 21-day pre-arrival deadline. **The holding-field-equals-sum-of-deltas property was checked on all three bound accounts and holds on every one** (`1.md` § revision 2). The expected failure mode — headline figure fixed, second field left inconsistent — did not occur. |
| **T1-F-B** (two readings of `session_date`) | **genuinely closed** | the disambiguation is a sentence of the **published** `lessons_ext_lift_access_addon.rule`, readable by a rollout agent, not a GT-only `argument_uniqueness_tracing` note. The second reading is excluded by policy text. Its business half is now written into the charter and is carried as **R2-F-3**. |
| **T1-F-A** (`value_input` edge acting as a `state_gate`) | **genuinely closed** | `tuition_standing` now feeds `value_component = tuition_standing * value_share / 100`. Verified by varying the tuition entry alone and recomputing the root: 500.00 -> 62.50, 549.00 -> 74.46, 553.22 -> 74.63, 700.00 -> 80.50. The amount reaches the answer, not only its existence. |

Observations claimed closed and verified closed: **F-1, F-3, OBS-1, OBS-2, OBS-3, OBS-4, OBS-7, OBS-9,
T1-OBS-C, T1-OBS-D/OBS-5**. Verified **partly** closed: **OBS-8** (rule and ladder corrected, the
`cross_category` note not propagated — R2-OBS-4); **T0-OBS-A / T1-OBS-A** (the clause naming the
prerequisite's subject removed; the blanket authorisation line correctly kept); **T1-OBS-B** (a real
excluded record now exists — the `withdrawn` instructor request — serving two of task 1's three
computations, but not the lift-access computation).

### have the answered-not-changed items been answered with reasons or with difficulty

- **F-2** — answered with **reasons**. Both structural routes it names were re-verified here against
  the base charter (`lessons_credit_use.eligibility[0].evidence_contract.action_bindings` does bind
  `lessons_ledger.lesson_event_id` to `related_event_id`), and each would trade the observation for a
  defect this audit would raise in its place; a wording-only route would leave the behaviour under a
  new name. One leg of its argument — "a third problem is not available, the tree is fixed by the
  draw" — is true but carries nothing, since the defect turns on a missing recording write and not on
  tree size. Disposition accepted; the observation stays open (`0.md`, R2-T0-F-1).
- **F-5, OBS-6, T0-OBS-B, T0-OBS-D** — answered with reasons. T0-OBS-B's reason is stronger than the
  one revision 1 recorded (the duplicated fields are account fields the schema *defines* as the sum of
  their deltas) and the observation is withdrawn as a criticism.
- **T0-OBS-C** — the reason given ("a near-miss would need a second school booking") **has been
  overtaken by the reworker's own OBS-4 fix in the same pass**: `credit_issued` is now a *filtered*
  binding (`within_months=12`) on this booking's own ledger, so an excluded record no longer requires a
  second booking. The observation stays open and its stated ground no longer holds (`0.md`,
  R2-T0-F-2).

### has anything regressed

- **Task 0's scored values are unchanged** — 227.60 and 737.88, plus baselines 229.50 / 1784.50 and all
  eight factor substitutions, every one re-derived from the new charter rather than read back. Its
  world is byte-identical and reconciles on all three lessons accounts.
- **Task 1's scored values moved** — 569.69 -> 553.22, 59.60 unchanged, 80.00 -> 74.63, terminal
  balance 768.29 -> 746.45 — and all five were reproduced independently before the reveal.
- One genuine regression: **R2-OBS-1**, two `compute_basis` values that are no longer verbatim
  substrings of their own rule (`storm_notice_date`, `settled_ratio`), both caused by the edits that
  closed OBS-7 and OBS-3. Revision 1 was clean on this test for all five policies.
- Nothing else that passed in revision 1 has weakened: the base section is still verbatim, the tool
  module is byte-identical, the uuid8s are untouched, the two task scopes are still disjoint and
  jointly complete, all three prerequisite edges still resolve to exactly one write each, and every one
  of the 23 factors still bears weight against an honest baseline.

### Step 4's list, on the reworked form

- Per-task files correspond one-to-one with the tasks; `_difficulty.md` sits alongside them; revision 1
  is preserved verbatim and revision 2 appended below it in all three files. `1.md`'s revision-2
  comparison does **not** carry a PASS on the factors relationship.
- Extended policies fully covered; the two task scopes pairwise disjoint and each spanning a whole
  problem tree; task tools and GT closed; each tool's uuid8 independently generated and frozen
  (carried on the unchanged hash `7abc9779ff7c3bdf`).
- Task 0: 1 prerequisite problem, 1 `value_input` edge, one `owner=user` write, no cycle.
  Task 1: 2 prerequisite problems, 2 `value_input` edges — **both now genuinely value-carrying** —
  one `owner=user` write, no cycle. The difficulty's three edges remain a DAG in two components.
- Every computation declares a self-sufficient baseline whose prose and whose factor fall-throughs now
  agree on all five policies, four to six factors each, every ladder three tiers stated in full, tiers
  distinct in outcome; every factor proved to bear weight on its task's world; the all-baseline numbers
  (229.50, 1784.50, 549.00, 149.00, 45.00) are all definite and all different from gold. **The one
  failure is the honesty of a single `effect` label (R2-F-1), which leaves one computation with no
  `method` factor.**
- Instantiation-stage gates re-run on the final form (2026-09-17T20:50Z, from the repository root):
  `EXTENDED OK`, `TASK TOOL CONTRACT OK`, `REPLAY OK` (0.json 11 acts / 16 of 16 closure rows matched;
  1.json 15 acts / 10 of 10 — run with `--check`, so no `db_closure` was written back),
  `SOLVABILITY OK`, `COMPUTE OK` (suite means branches 31.00, steps 13.00; depth history_rows_max 12,
  branches_max 39), `GROUNDING OK`, `SCOPE OK`. `TRACEABILITY NOT OK`, unchanged pre-render state, its
  misses solely the five hidden task-tool names.

### findings index (revision 2)

| id | verdict | where demonstrated |
| --- | --- | --- |
| **R2-F-1** | **SOURCE-FACTOR RED** — `guest_on_mountain_method` labelled `method`; policy left with none | `1.md` § revision 2 findings (R2-T1-F-1) |
| R2-F-2 | observation — the tool module was not reopened | `_difficulty.md` § revision 2 findings |
| R2-F-3 | observation — a rule promise the charter does not keep | `1.md` (R2-T1-OBS-2) |
| R2-OBS-1 | observation — two non-verbatim `compute_basis` quotations (regression) | `_difficulty.md` |
| R2-OBS-2 | observation — a per-product validity period replaced by a flat one | `_difficulty.md` |
| R2-OBS-3 | observation — non-monotone ladder outcomes 50 / 150 / 100 | `1.md` (R2-T1-OBS-4) |
| R2-OBS-4 | observation — stale `cross_category` note after OBS-8 | `0.md` (R2-T0-OBS-1) |
| R2-T0-F-1 | observation — F-2 carried; disposition accepted, one leg non-load-bearing | `0.md` |
| R2-T0-F-2 | observation — T0-OBS-C carried; its stated reason overtaken by the rework | `0.md` |
| R2-T0-OBS-2 | observation — the new 12-month credit window is unexercised | `0.md` |
| R2-T1-OBS-1 | examined, not a defect — the folio stands in credit before arrival | `1.md` |
| R2-T1-OBS-3 | observation — near-miss now in two computations of three | `1.md` |

---

# revision_3 — re-audit of the reworked form (charter-global)

## charter_global_frozen (revision 3)

- Auditor: same independent auditor. Revisions 1 and 2 above are left untouched.
- Freeze time: 2026-09-17T21:20Z. **Written before any revision-3 GT field was read.**
- Hashes, compared against the round that produced each section:

| artifact | r1 | r2 | r3 | re-derivation |
| --- | --- | --- | --- | --- |
| `lessons.extended.yaml` | `ccaa40cd9520ae99` | `1018928d2a2d2824` | **`8a41f7038a8d7403`** | **changed -> all charter-global sections re-derived in full** |
| `task_tools.py` | `7abc9779ff7c3bdf` | same | **same** | unchanged across all three rounds |
| `tasks/0.json` (masked) | `3b5aa50ba28bd840` | `00946864c6733295` | **`00946864c6733295`** | unchanged from r2 |
| `tasks/1.json` (masked) | `c91118905e02a626` | `e92c476084c884e7` | **`e92c476084c884e7`** | unchanged from r2 |

  Re-verified independently: the two masked task files hash to their round-2 values, and hashing
  `initial_state` and `user_scenario` separately confirms **both worlds and both personas are
  byte-identical to round 2**. Only the charter and the masked-out regions moved.
- `head -1357` of the new charter is still byte-identical to `blueprint/products/lessons.yaml`.
  **Base section verbatim: no regression across three rounds.**
- Masked-out keys unchanged. Entry conditions: the coordinator supplied the re-run gate snapshot
  (all green except the expected pre-render `TRACEABILITY`), re-run once by this auditor on the final
  form under `closing_checklist (revision 3)`.

### policy_conflict_scan (revision 3)

Five policies, same five subjects, same five `computes` names, same five target tools, same two-tree
partition and the same disjoint-and-complete task scopes. Unchanged.

**Cross-category boundaries contracted, and the declarations contracted with them.** The gate's
`cross-cat` count falls 4 -> 3 because `lessons_ext_date_change_fee` no longer reads another category
at all. Verified directly rather than inferred:

| policy | `cross_category` | `inputs.cross_category` | reads in `compute` |
| --- | --- | --- | --- |
| `lessons_ext_weather_session_credit` | `passes` (`status`, `passes_ledger.event_type`) | `[passes]` | `EXISTS('passes', …)`, `XCOUNT('passes','passes_ledger', …)` |
| `lessons_ext_balance_settlement` | `[]` | `[]` | none |
| `lessons_ext_session_tuition_charge` | `lodging` (`status`, `rate_plan`, `lodging_folio.amount_usd`) | `[lodging]` | 3 x `CFIELD('lodging', …)`, `XSUM('lodging','lodging_folio', …)` |
| `lessons_ext_lift_access_addon` | `lodging` (`status`, `rate_plan`) | `[lodging]` | 2 x `CFIELD('lodging', …)` |
| `lessons_ext_date_change_fee` | **`[]`** | **`[]`** | **none** |

Declared exactly in both directions: every declared read is performed and every performed read is
declared. Grep over the whole extended section for the removed names —
`resident_share`, `departed_share`, `guest_on_mountain`, `stay_departure`, `departure_date`,
`nights_booked`, and revision 1's `unallocated_share`, `fee_ceiling`, `moved_fee`, `tuition_share_cap`
— returns **no hit anywhere**. Nothing was left stranded by the deletion. **PASS.**

### rule_compute_equivalence (revision 3)

**R2-OBS-1 checked independently, not accepted from the author's checker.** This auditor re-ran its own
three tests, the same ones that produced the revision-2 finding, over all five policies of the new
file:

| test | result |
| --- | --- |
| every `compute` binding carries a `compute_basis` entry | **0 misses**, 5/5 policies |
| no `compute_basis` key is an orphan | **0 orphans**, 5/5 |
| every `compute_basis` value is a **verbatim** substring of its own policy's `rule` | **0 non-verbatim**, 5/5 |
| every `baseline.rule` is a verbatim run of its own `rule` | 5/5 |
| every `overwrite.superseded_clause` verbatim in the base policy it names | **7/7 entries** |
| every `overwrite.replaced_by` a sentence of the superseding rule | 7/7 |

Revision 2's two failures are gone: `storm_notice_date` now quotes the whole semicolon-joined sentence
(no rule change needed — the quotation was re-cut), and `settled_ratio` quotes a single sentence that
now exists.

**The `settled_ratio` fix changed published text, so the change was inspected rather than assumed.**
Revision 2's rule read:
> "…judged as the payments collected on the booking measured against the tuition raised on it: where
> the payments cover half or more … and where they cover less than a quarter no points are allowed."
> *(separate sentence)* "Where no tuition has been raised on the booking there is nothing for the
> payments to be measured against and no points are allowed on that count."

Revision 3 reads:
> "…judged as the payments collected on the booking measured against the tuition raised on it, **and
> where no tuition has been raised on the booking there is nothing for the payments to be measured
> against and no points are allowed on that count.** Where the payments cover half or more of the
> tuition raised the settled account points are allowed; where they cover at least a quarter of it but
> less than half the part settled points are allowed; and where they cover less than a quarter no
> points are allowed."

The zero-tuition clause moved into the lead sentence and the three-tier ladder became a sentence of its
own. **All three tiers survive word for word, the zero branch survives word for word, and no condition,
threshold or outcome changed.** `settled_ratio`'s basis is now the lead sentence and
`standing_points`' basis is the ladder sentence — each quotation now matches the binding it labels.
The compute is unchanged. **No normative content was lost to make the quotation verbatim.**

Ladder-in-rule coverage was re-checked by hand, tier by tier, across all 23 ladders (a substring test
fails on the `when` strings because they are noun-phrase paraphrases of "Where X, Y" rule sentences —
the same was true in rounds 1 and 2 and is not a change): every tier's condition and its value or
method is stated in its policy's own `rule`, and every branch of each `decides` binding is a tier the
rule states.

One new convention needs recording — **R3-OBS-1**, below.

**PASS**, and cleaner than either previous round.

### action_binding_and_uuids (revision 3)

Re-derived because the charter changed. Five policies, five distinct tools, five distinct `computes`
names, each claimed by exactly one policy — unchanged. `task_tools.py` is byte-identical for the third
round running (`7abc9779ff7c3bdf`), so the uuid8 conclusion (`1ce20aea`, `78bdef11`, `38aef0d5`,
`aea17349`, `58e66cab` — pairwise distinct, no shared prefix, no sequence, not batch-derived) and the
docstring-silence conclusion both carry forward on that hash. **PASS.**

### prerequisite_graph (revision 3)

Same three edges, all `kind: value_input`, all `form: state`, no `fallback_reason`. DAG, two
components, depth 1. Every `gate` is a real binding of the blocked policy's own `compute`
(`credit_standing`, `tuition_standing`, `addon_entries`), every `resolved_by` is the depended-on
policy's `target_tool`, every `prerequisite` filled in, no authoring-viewpoint phrasing.

Both `effect` texts on the task-1 edges were **rewritten** this round and both were checked against the
new compute rather than taken on trust:
- tuition edge: "The tuition standing binding rises from nothing to the tuition raised, **the figure the
  booking's value is reckoned on rises with it**, and the share added to the fee rises with the
  amount" — correct: `tuition_standing` now feeds both `value_share` (the tier) and `value_base` (the
  figure the share is taken on), in all three tiers of `moved_value_method`.
- add-on edge: "The add-on entries binding rises by one, so the handling amount moves up a tier, **and
  the add-ons standing on the booking rise with it, so the fee charged changes twice over**" —
  correct, and it is the honest description of a real second channel the rework created:
  `moved_value_method`'s single-session tier is `tuition_standing + addon_total`, so the add-on write
  now moves the fee through `addon_handling` **and** through `value_base`. The declared `gate` names
  one binding (`addon_entries`), which the rules require to be a real value input and it is; the
  `effect` names both channels. **Not under-declared.**

**PASS.**

### prerequisite_sentences (revision 3)

All three `policy_source` strings verbatim in the blocked policy's own `rule` (3/3). Two unchanged from
revision 2. One **re-cut**, because the quantity it named no longer exists:

- revision 2: "The share of the **tuition standing** that is added to the fee is fixed only after the
  school account carries the tuition entry due for the booking."
- revision 3: "The share of the **booking's value** that is added to the fee is fixed only after the
  school account carries the tuition entry due for the booking."

Re-tested on the four points: *only after* is an explicit ordering connective joining this policy's own
result (the share added to the fee, and so the fee) to what it waits on; the waited-on side is
"the school account carries the tuition entry due for the booking", a record-visible state in the words
the ledger and `find_lesson_account_entries` use, with no action, performer or tool; it names no tool,
policy id, snake_case token or row id; and it is written at exactly the strength and scope the edge's
`condition` carries. Exactly one write of this difficulty brings that state about
(`raise_session_tuition_charge_38aef0d5` is the only tool creating a `lessons_tuition_charge` row), and
the reader's route is unchanged: a tuition entry on the school account -> the only policy whose own rule
describes raising tuition -> its rule gives the amount. **One reading.** The re-cut was required by the
rework and was performed; it did not drift in strength.

No rule carries a second wording of any dependency, no other problem's tool name, policy id or route,
and no depended-on rule restates a blocked rule's sentence. The ordering-connective sweep over all five
rules returns only within-computation sequencing.

**Revision 2's R2-F-3 is closed by deletion, not by rewording.** The clause
"…access for a date the lesson is later moved to is answered by the terms that price a change of date
rather than by re-dating this entry" has been **removed** from
`lessons_ext_lift_access_addon.rule`; the sentence now ends at "…is never named." The promise the
charter could not keep is gone rather than restated, and the sentence that closed T1-F-B — which date
the entry names — survives intact, so that closure is not undone. See R3-OBS-3 for what the deletion
leaves.

**PASS.**

### override_declarations (revision 3)

Seven `overwrite` entries across five policies, all seven verbatim against the base sentence they name
and all seven replaced by a sentence of the superseding rule. Re-swept sentence by sentence against
each `base_policy_refs` entry: **no undeclared override anywhere**, the clean result revisions 2 and 3
share and revision 1 did not have. The entries are unchanged from revision 2 except one:

`lessons_ext_balance_settlement` against `lessons_credit_use` — revision 2 replaced the per-product
validity sentence with a flat "twelve months"; revision 3 replaces it with "Credit issued longer ago
than **the product's credit validity period**, counted in whole months of thirty days from the day of
issue, has run out and no longer counts toward the credit standing", and the compute follows with
`within_months=P('credit_validity_days') / 30`. The flat constant `credit_validity_months` is gone from
`params`. **R2-OBS-2 closed**: the per-product parameter (`credit_validity_days` — 365 / 270 / 180
across the charter's variants) is live again rather than dead. The new counting convention is recorded
as R3-OBS-1.

### factor_ladders (revision 3)

| policy | factors | parameter | method | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| `lessons_ext_weather_session_credit` | 4 | 3 | 1 `makeup_answer_method` | `pass_day_offset` | `pass_day_offset` -> passes |
| `lessons_ext_balance_settlement` | 4 | 3 | 1 `credit_offset_method` | `credit_offset_method` | none |
| `lessons_ext_session_tuition_charge` | 6 | 5 | 1 `reduction_selection_method` | `resort_stay_points`, `reduction_selection_method` | 3 -> lodging |
| `lessons_ext_lift_access_addon` | 4 | 3 | 1 `session_length_method` | none | `resort_guest_ticket_points` -> lodging |
| `lessons_ext_date_change_fee` | 5 | 4 | **1 `moved_value_method`** | `instructor_rebooking_amount` | **none** |

All five inside 4-6, all meeting >= 2 `parameter` and **>= 1 `method`**. Every ladder three tiers, stated
in full in its own rule, one ternary chain, `decides` an intermediate binding, binding sets disjoint
within each policy, no two tiers of any ladder selecting the same value or method.

**The `method`-honesty sweep, run independently across the whole charter.** Enumerating every factor
carrying `effect: method` returns **exactly five**, and this auditor's enumeration matches the five the
author names — the list is complete, there is no sixth:

| # | policy / factor | the three expressions its tiers select | genuine? |
| --- | --- | --- | --- |
| 1 | `lessons_ext_weather_session_credit` / `makeup_answer_method` | `(session_value * weather_share / 100) / 2` ; `session_value` ; `session_value * weather_share / 100` | **yes** — halve, drop the share entirely, apply the share |
| 2 | `lessons_ext_balance_settlement` / `credit_offset_method` | `credit_standing` ; `figure_owed` ; `K('no_credit_set_against')` | **yes** — different quantities, not one quantity at different rates |
| 3 | `lessons_ext_session_tuition_charge` / `reduction_selection_method` | `advance_points + stay_points` ; `stay_points` ; `advance_points` | **yes** — which record-derived quantities are combined |
| 4 | `lessons_ext_lift_access_addon` / `session_length_method` | `P(addon) * sessions_loaded` ; `P(addon) * K('half_day_share')/100 * sessions_loaded` ; `P(addon) * F('sessions_booked')` | **yes** — the multiplicand's *source* changes between tiers 1 and 3 (loaded block vs booked sessions); tier 2 also introduces a share, but the ladder is not one base at three rates. Same judgement as rounds 1 and 2 |
| 5 | `lessons_ext_date_change_fee` / `moved_value_method` | `tuition_standing / sessions_loaded` ; `tuition_standing + addon_total` ; `tuition_standing` | **yes** — a division by a record-derived count, a sum with a second record-derived aggregate, and the bare quantity. **No policy constant is substituted anywhere in the ladder** |

The shape this audit red-lighted twice — `base x K1` / `base x K2` / `base` (revision 1's
`advance_rate_method`, revision 2's `guest_on_mountain_method`) — occurs **nowhere** in the charter.
**R2-F-1 closed, and the sweep confirms it was not merely relocated a second time.**

**How R2-F-1 was closed** (checked against the artifact, not the account): `guest_on_mountain_method`
was **deleted**, together with `params.resident_share`, `params.departed_share`, the `stay_status` and
`stay_departure` bindings, the `moved_fee` binding it decided and the policy's whole `cross_category`
block; `raw_fee` now flows straight into `result`. The replacement `moved_value_method` decides a new
binding `value_base`, which feeds the pre-existing `value_component`. This is structural surgery, not a
relabel — the constants that made the old ladder a rate ladder no longer exist in the file.

**What the deletion took with it, and whether the floors still hold.** The date-change policy lost its
only cross-difficulty factor, so the charter's `cross-cat` count is 3 and task 1's cross-difficulty
factor count is 4 (`resort_stay_points`, `reduction_selection_method`, `rate_window_supplement` in the
tuition computation, `resort_guest_ticket_points` in the add-on computation). The floors are stated
**per task, over its computations**, not per computation:
- task 1 cross-difficulty: **4 >= 1** ✔, all reading `lodging`, all with rows seeded;
- task 1 multi-source: `resort_stay_points`, `reduction_selection_method` and
  `instructor_rebooking_amount` — **3 >= 1** ✔;
- task 0 unchanged: 1 cross-difficulty (`pass_day_offset` -> passes), 2 multi-source.
Both floors hold. What did change and is worth recording is that the **root** computation of task 1 —
the one the customer's own write scores — now reads no other difficulty's records at all, where in
revisions 1 and 2 it did. Recorded as **R3-OBS-2**.

**Conditions and outcomes the line of business actually holds.** Re-reviewed tier by tier. The new
ladder's three tiers are all things a school weighs when pricing a move: a multi-session block where
only one date shifts is valued per session; a single-session engagement moves whole, extras and all;
with no block loaded there is only the tuition to reckon on. Revision 2's non-monotone 50 / 150 / 100
ladder (R2-OBS-3) is gone with the factor that carried it. No tier of any ladder in the charter now
publishes an outcome this auditor can name as one the line of business would not.

**Baseline coherence** — each `baseline.rule` read on its own against what the factors' fall-throughs
produce:

| policy | prose reads to | fall-throughs give | agree? |
| --- | --- | --- | --- |
| `lessons_ext_weather_session_credit` | session value x standard weather share | same | yes |
| `lessons_ext_balance_settlement` | the figure owed, rounded | same | yes |
| `lessons_ext_session_tuition_charge` | the block price, rounded | same | yes |
| `lessons_ext_lift_access_addon` | add-on price x sessions the booking holds | same | yes |
| `lessons_ext_date_change_fee` | **the product's move fee**, with the share "taken on the tuition standing alone" and "where the booking earns no share nothing is added on that count" | `notice_fee` = `P('reschedule_fee_usd')`, handling 0, rebooking 0, `value_base` = `tuition_standing`, `value_share` = `K('no_booking_share')` = 0 -> `RND(reschedule_fee_usd + 0, 2)` | **yes** |

`lessons_ext_date_change_fee.baseline.rule` gained a sentence — "The share of the booking's value that
is added to it is taken on the tuition standing alone, and where the booking earns no share nothing is
added on that count" — which is exactly what its two new fall-throughs do, so `baseline.params`
(`[reschedule_fee_usd, no_addon_handling, no_instructor_rebooking, no_booking_share]`) still names
every key its fall-throughs use and `moved_value_method`'s fall-through needs no constant.
**F-6 remains closed, and the author's assertion that the whole-baseline is unchanged at 45.00 is
confirmed by this auditor's own substitution** — figures in `1.md` § revision 3.

### findings (revision 3)

Derived from the charter, the schema and the tool module alone, before any revision-3 GT was read.

---

**R3-OBS-1 — observation (a counting convention the rule states and the compute does not implement)**

- *Symptom*: closing R2-OBS-2 restored the per-product credit validity period, and the sentence that
  restores it defines a counting convention the restricted expression does not follow.
- *Evidence*: `lessons.extended.yaml`, `lessons_ext_balance_settlement`:
  - rule / `overwrite[0].replaced_by`: "Credit issued longer ago than the product's credit validity
    period, **counted in whole months of thirty days from the day of issue**, has run out and no
    longer counts toward the credit standing";
  - `compute.credit_issued`: `SUM('lessons_ledger','amount_usd',
    within_months=P('credit_validity_days') / 30, event_type='lessons_credit_issue')`.
  `within_months` is evaluated by `check_compute._within` as `0 <= MONTHS(event_date, NOW) <
  within_months`, and `MONTHS` counts **calendar** months (`(y2-y1)*12 + (m2-m1)`, less one where the
  day of month has not come round), not thirty-day blocks. The rule's "months of thirty days" and the
  machine's calendar months are two different conventions, and they part company at the boundary: a
  credit issued 2026-01-31 against a handling date of 2027-01-30 is 364 days old — 12.13 thirty-day
  months — but `MONTHS` returns 11.
- *Consequence*: none demonstrable on either audited world. Task 0's only `lessons_credit_issue` row is
  the one the prerequisite write creates, dated `NOW`, so `MONTHS` = 0; task 1 has no credit row and
  this policy is not in its tree. Recorded as an observation because the interval counting convention
  is one of the items check 2 requires the compute to implement as stated, and here the prose names a
  convention the expression does not use.
- *Artifact and location*: `lessons_ext_balance_settlement.rule` (the credit sentence),
  `overwrite[0].replaced_by`, `compute.credit_issued`.
- *Relation to previous revisions*: **new in revision 3**, arising from the fix that closed R2-OBS-2.
  Revision 2's flat twelve months had no such mismatch, but it had the defect R2-OBS-2 named.

---

**R3-OBS-2 — observation (the root computation of task 1 no longer reads another difficulty)**

- *Symptom*: deleting `guest_on_mountain_method` removed `lessons_ext_date_change_fee`'s only
  cross-category read, so the policy that scores the customer's own write now reads `lessons` alone.
- *Evidence*: `lessons_ext_date_change_fee.cross_category: []`, `inputs.cross_category: []`, and no
  `CFIELD` / `XSUM` / `XCOUNT` / `EXISTS` in its `compute`. In revision 1 it read
  `lodging` (`status`, `nights_booked`) through `resort_guest_relief`; in revision 2,
  `lodging` (`status`, `departure_date`) through `guest_on_mountain_method`.
- *Assessment*: **no floor is breached.** The requirement is at least one multi-source and one
  cross-difficulty factor **per task over its computations**, and task 1 carries four cross-difficulty
  factors and three multi-source factors across its three computations; the root computation itself
  still carries a multi-source factor (`instructor_rebooking_amount`, over a `lessons_requests` row and
  a `lessons_holdings` field). Recorded because it is a real narrowing that the fix bought, and
  because it is the kind of collateral a structural deletion is most likely to cause.
- *Artifact and location*: `lessons_ext_date_change_fee.cross_category`, `factors`.
- *Relation to previous revisions*: new in revision 3; collateral of closing R2-F-1.

---

**R3-OBS-3 — observation (what the deletion of the empty promise leaves behind)**

- *Symptom*: R2-F-3 is closed by removing the clause that referred lift access for a moved-to date to
  "the terms that price a change of date". Nothing was put in its place.
- *Evidence*: `lessons_ext_lift_access_addon.rule` now reads "…The entry names the date the booking's
  first session is due to run at the moment the access is put on the booking, and a date the household
  has asked the school to move the lesson to, which the booking does not yet stand on, is never named."
  and stops there. `lessons_ext_date_change_fee.rule`, read end to end, still says nothing about lift
  access.
- *Assessment*: the finding as raised — a rule making a promise the charter does not keep — is
  **genuinely closed**, and closed the honest way: the promise was withdrawn rather than reworded. The
  charter is now silent about the gap rather than wrong about it. What remains is a fact about the
  world, not an inconsistency in the charter: on task 1 the gold run leaves the household charged for
  lift access covering 2027-02-14 and holding none for 2027-02-15. That was never itself graded a
  defect of the four relationships in any round, and it is not graded one now.
- *Relation to previous revisions*: closes R2-F-3; supersedes R2-T1-OBS-2, which is carried forward as
  a note about the world rather than about the text.

---

**R3-OBS-4 — observation (the change fee is now bounded by nothing)**

Across the three revisions the date-change fee lost, in order, its ceiling (`tuition_share_cap` /
`fee_ceiling`, revision 1 -> 2) and its only reduction (`guest_on_mountain_method`'s resident share,
revision 2 -> 3), while gaining an additive share of the booking's value. Nothing in the extended
policy or in base `lessons_change_terms` now bounds the fee relative to the booking, so the figure the
charter's own first sentence calls "the product's move fee" (45.00 for the Semi-Private Coaching
Session) is charged at **131.87** on task 1's world — 2.9 times the published figure. Each tier taken
in isolation is a modest, defensible number (35.00 notice, 30.00 handling, 40.00 rebooking, 4 per cent
of the value), so no single tier outcome is one this auditor can name as unbusinesslike, and a definite
wrong baseline of 45.00 is exactly what the design intends a factor-blind reader to reach. Recorded as
an observation on the composition rather than as a red light against any tier, and recorded because it
is the cumulative effect of three rounds of rework on one policy rather than of any one change.

## closing_checklist (revision 3)

Written after both tasks' revision-3 `source_derivation_frozen` and `source_gt_comparison` sections
landed (reveal 2026-09-17T21:50Z). The revision-1 and revision-2 checklists above are left untouched.

**The difficulty closes.** All four relationships PASS on both tasks.

| relationship | task 0 r1 / r2 / r3 | task 1 r1 / r2 / r3 |
| --- | --- | --- |
| policy self-consistency | PASS / PASS / **PASS** | PASS / PASS / **PASS** |
| the problem tree holds | PASS / PASS / **PASS** | PASS / PASS / **PASS** |
| factors bear weight | PASS / PASS / **PASS** | RED / RED / **PASS** |
| unique solution | PASS / PASS / **PASS** | RED / PASS / **PASS** |

### is each revision-2 finding genuinely closed, or merely reworded

| id | closed? | what was verified, against the artifact |
| --- | --- | --- |
| **R2-F-1 / R2-T1-F-1** (sole blocker) | **genuinely closed, structurally** | `guest_on_mountain_method` **deleted**, with `params.resident_share`, `params.departed_share`, the `stay_status` / `stay_departure` bindings, the `moved_fee` binding and the policy's whole `cross_category` block; a grep for every removed name returns **no hit** in the extended section, so nothing was stranded. The replacement `moved_value_method` selects `tuition_standing / sessions_loaded`, `tuition_standing + addon_total`, `tuition_standing` — three expressions over record-derived quantities, **no constant substituted**. The policy now has 4 `parameter` + 1 honest `method`. |
| — the method sweep | **enumeration verified complete** | Enumerating every factor with `effect: method` charter-wide returns **exactly five**, matching the five the author names: `makeup_answer_method`, `credit_offset_method`, `reduction_selection_method`, `session_length_method`, `moved_value_method`. Each was re-judged on its three expressions; **none** is `base x K1 / base x K2 / base`. There is no sixth `method` factor and no other instance of the shape. |
| — the floors after the deletion | **verified, not assumed** | charter `cross-cat` 4 -> 3 and task 1's cross-difficulty factor count 5 -> 4, because the root policy lost its only cross-category read. The floors are per task over its computations: task 1 carries **4** cross-difficulty and **3** multi-source factors, task 0 carries 1 and 2. Both hold. The root computation of task 1 still carries a multi-source factor of its own. The narrowing is recorded as **R3-OBS-2**, not as a breach. |
| **R2-OBS-1** (the regression) | **genuinely closed, and checked independently** | this auditor re-ran its **own** three tests over all five policies rather than accepting the author's checker: **0 bindings without a basis, 0 orphans, 0 non-verbatim quotations**, plus 7/7 `overwrite.superseded_clause` entries verbatim in base and 5/5 `baseline.rule` runs verbatim. The `settled_ratio` **rule** was re-cut to make the quotation work, so the published text was compared word for word against revision 2: all three tiers and the zero-tuition branch survive verbatim, no threshold or outcome changed, the compute is untouched, and each quotation now labels the binding it belongs to. **No normative content was traded for the verbatim property.** |
| **R2-F-3** | **genuinely closed by deletion** | the clause referring lift access for a moved-to date to "the terms that price a change of date" is removed; the sentence ends at "…is never named." The promise is withdrawn rather than reworded, and the sentence that closed T1-F-B survives, so that closure is not undone. What the deletion leaves is a fact about the world, recorded as R3-OBS-3. |
| **R2-OBS-2** | **genuinely closed** | `params.credit_validity_months` gone; `within_months=P('credit_validity_days') / 30`, so the charter's own 365 / 270 / 180 are live again, under a declared override. New convention recorded as R3-OBS-1. |
| **R2-OBS-4** | **genuinely closed** | the `cross_category` note now reads "the household's season pass record", matching the rule, the tier conditions and the quotations. |
| **R2-F-2, R2-T1-OBS-1, R2-T1-OBS-3** | accepted as framing / carried | R2-F-2's reason is this audit's own assessment accepted back, and it is right. R2-T1-OBS-1 (the folio in credit before arrival) was examined and found to be the lodging charter's own consequence. R2-T1-OBS-3 is unchanged: the near-miss serves two computations of three, and the lift-access computation still has none. |

### the two revisited dispositions

- **F-2 / R2-T0-F-1** — the non-load-bearing leg ("a third problem is not available; the tree is fixed
  by the draw") **has been deleted** from the worklog, which is what revision 2 asked for. The
  disposition now rests on the two structural legs this auditor verified in revision 2 and again here
  against `blueprint/products/lessons.yaml`. **Accepted.** The observation stays open: the settlement
  still consumes credit arithmetically with no recording write.
- **T0-OBS-C / R2-T0-F-2** — the overtaken reason is **withdrawn** and replaced by one this auditor
  checked arithmetically and found sound, and stronger than its predecessor: the product's 270-day
  booking window puts the earliest lawful `booked_date` for this booking at **2026-04-23**, a credit
  row cannot predate the booking it sits on, and `MONTHS(2026-04-23, 2027-01-21)` is **8** against a
  window of 365/30 = **12.17** — so the filter is structurally incapable of excluding anything on this
  booking, whatever the seed does. Correctly scoped to "this booking" rather than "any booking".
  **Accepted**; the observation stays open with a charter-checkable reason on record, and R2-T0-F-2 is
  closed.

### has anything regressed

- **Task 0 is undisturbed end to end for the third round running** — 227.60, 737.88, baselines 229.50
  and 1784.50, all eight factor substitutions and the 849.40 counterfactual, every one re-derived on
  the new charter rather than carried forward. Its world and persona are byte-identical to round 2.
- **Task 1's change fee moved again** (74.63 -> 131.87, terminal balance 746.45 -> 803.69) and all five
  scored arguments, fifteen factor substitutions, three baselines and both edge counterfactuals were
  reproduced independently before the reveal.
- **Revision 2's one regression is gone and no new one replaces it**: the `compute_basis` tests are
  clean on all five policies, the base section is still verbatim, the tool module is byte-identical
  for the third round, the uuid8s are untouched, the scopes are still disjoint and jointly complete,
  all three prerequisite edges still resolve to exactly one write each, the two re-cut sentences
  (one prerequisite sentence, one rule sentence) both survive their four-point and word-for-word
  re-tests, and every one of the 23 factors still bears weight against an honest baseline.
- Three new observations arise from this round's fixes — **R3-OBS-1** (a stated counting convention
  the expression does not implement), **R3-OBS-2** (the root computation of task 1 no longer reads
  another difficulty) and **R3-OBS-4** (nothing now bounds the change fee) — and none is a red light.

### Step 4's list, on the closed form

- Per-task files correspond one-to-one with the tasks; `_difficulty.md` sits alongside them; revisions
  1, 2 and 3 are all preserved in each file, oldest first, with no earlier text rewritten. Every
  revision-3 comparison section carries a **PASS**.
- This difficulty's five extended policies are fully covered; the two task scopes are pairwise
  disjoint and each spans a whole problem tree; task tools and GT are closed; each of the five tools
  carries an independently generated, frozen uuid8 (`7abc9779ff7c3bdf`, unchanged for three rounds).
- Task 0: 1 prerequisite problem, 1 `value_input` edge, one `owner=user` write, no cycle. Task 1:
  2 prerequisite problems, 2 `value_input` edges — both value-carrying, the add-on edge through two
  declared channels — one `owner=user` write, no cycle. The difficulty's three edges are a DAG in two
  components with no cross-task cycle.
- Every computation declares a self-sufficient baseline whose prose and factor fall-throughs agree on
  all five policies; four to six factors each; every ladder three tiers stated in full in its own rule,
  tiers distinct in outcome, conditions and outcomes ones the line of business holds; every factor
  proved to bear weight on its task's world; per task at least one multi-source and one
  cross-difficulty factor; the all-baseline numbers (229.50, 1784.50, 549.00, 149.00, 45.00) all
  definite and all different from gold (227.60, 737.88, 553.22, 59.60, 131.87).
- Instantiation-stage gates re-run on the final form (2026-09-17T21:52Z, from the repository root):
  `EXTENDED OK` (cross-cat=3), `TASK TOOL CONTRACT OK`, `REPLAY OK` (0.json 11 acts / 16 of 16;
  1.json 15 acts / 10 of 10 — run with `--check`, and the task files' mtimes confirm nothing was
  written back), `SOLVABILITY OK`, `COMPUTE OK` (suite means branches 30.00, steps 13.00; depth
  history_rows_max 12, branches_max 37), `GROUNDING OK`, `SCOPE OK`. `TRACEABILITY NOT OK`, the
  unchanged pre-render state, its misses solely the five hidden task-tool names, which the KB render
  step publishes through each policy's `target_tool`.

**Source-layer audit: PASS.** Policy self-consistency, the problem tree, the factors' weight and the
unique solution all hold on both tasks. The open items are observations, listed below; none of them
changes a scored value, and each carries a reason on the record.

### findings index (revision 3)

| id | verdict | where |
| --- | --- | --- |
| R3-OBS-1 | observation — "whole months of thirty days" against calendar `MONTHS` | `_difficulty.md`, `0.md` (R3-T0-OBS-1) |
| R3-OBS-2 | observation — task 1's root computation no longer reads another difficulty | `1.md` (R3-T1-OBS-2) |
| R3-OBS-3 | observation — what the deletion of the empty promise leaves | `1.md` (R3-T1-OBS-1) |
| R3-OBS-4 | observation — the change fee is bounded by nothing | `1.md` (R3-T1-OBS-3) |
| R3-T0-F-1 | disposition accepted — F-2 stays open on two verified legs | `0.md` |
| R3-T0-F-2 | disposition accepted — T0-OBS-C stays open on a sound new reason; R2-T0-F-2 closed | `0.md` |
| carried | F-2, F-5, OBS-6, T0-OBS-A/B/C/D, T1-OBS-A, R2-T1-OBS-3 | `0.md`, `1.md` |
