# Policy-task audit — guest_protection_desk / charter-global

## charter_global_frozen

| item | value |
| --- | --- |
| scenario | `env/env_0015_car_sharing_marketplace` |
| difficulty | `guest_protection_desk` (category `guestplan`, M=2) |
| `guestplan.extended.yaml` | sha256:16 = `a7e5821b0e67c075` |
| `task_tools.py` | sha256:16 = `a26d40350c5c0987` |
| freeze time (UTC) | 2026-09-22T09:07:43Z |
| auditor | erl-task-policy-audit, independent of the instantiating agent |
| revision | 1 (no prior revision on disk) |

**Fields permitted while this section was written**: `blueprint/blueprint.yaml`,
`blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/guestplan.yaml`,
the whole of `tasks/guest_protection_desk/guestplan.extended.yaml` (base copy + `extended_policies`,
including `rule`, `compute`, `compute_basis`, `overwrite`, `prerequisite`, `factors`, `baseline`,
`params`, `inputs`, `cross_category`), `tasks/guest_protection_desk/task_tools.py`, and `erlbench/`.

**Fields explicitly masked**: every task file's `evaluation_criteria`, `computations`,
`charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`,
`prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state`. This section contains
nothing derived from a revealed GT: it was written before either task's reveal, from the charter,
the schema and the tool contracts alone.

**Entry conditions (Step 0)** — supplied by the coordinator and cited, not re-run here:
`check_extended.py` PASS (category=guestplan, extended_policies=5, cross-cat=5, task_tools=5,
tasks=2, no_handoff=True); `check_task_tools.py` PASS (5 tools); `replay_tasks.py --check` PASS
(0.json 14/19/19, 1.json 11/17/17); `check_solvability.py` PASS; `check_compute.py` PASS
(branches mean 66.00, steps mean 12.50, history_rows_max 10, branches_max 78);
`check_grounding.py` PASS; `check_cross_fire.py` PASS (hard-fails 0). Masked views were built by
the coordinator with the hashes `858e4c67ec7ebf24` (0.json) and `ff4ecf45949506ec` (1.json), both
re-verified by this auditor, and both contain exactly `frozen_time`, `user_scenario`,
`initial_state`. Input is complete; `check_traceability.py` is correctly deferred to the KB stage.
A machine green light is the qualification to enter this audit, not a proof of correctness.

---

### policy_conflict_scan

The structured policy in force for `guestplan` at this difficulty is the base section of
`blueprint/products/guestplan.yaml` (8 base policies) plus 5 `extended_policies`.

**Base copy is verbatim.** `diff <(sed -n '1,718p' guestplan.extended.yaml) blueprint/products/guestplan.yaml`
returns only `718d717 <` — a single trailing blank line. No base sentence, parameter, variant,
event or eligibility contract has been rewritten. PASS.

**Overlapping subjects.** Five extended policies, five distinct `target_tool`s, five distinct
`computes`:

| policy | subject | computes | target_tool |
| --- | --- | --- | --- |
| `guestplan_ext_additional_driver_charge` | `guestplan_secondary_driver_charged` | `driver_fee_amount` | `declare_additional_driver_a214c8dd` |
| `guestplan_ext_young_driver_surcharge` | `guestplan_protection_fee_charged` | `surcharge_amount` | `post_young_driver_surcharge_f46febb9` |
| `guestplan_ext_level_change_difference` | `guestplan_level_change_charged` | `difference_amount` | `price_level_change_f4995b0a` |
| `guestplan_ext_level_election_cover` | `guestplan_election_confirmed` | `covered_days_count` | `confirm_protection_level_63b6fff8` |
| `guestplan_ext_protection_fee_assessment` | `guestplan_protection_fee_charged` | `fee_amount` | `post_protection_fee_513639f7` |

`guestplan_ext_young_driver_surcharge` and `guestplan_ext_protection_fee_assessment` share the
subject event family `guestplan_protection_fee_charged`, but they compute different quantities,
write through different tools, and the rows they create are separated by `charge_basis`
(`young_driver_protection_surcharge` vs `daily_protection_fee`) in `task_tools.py:45` and
`task_tools.py:219`. No two policies reach different conclusions on the same quantity in the same
situation on this axis. PASS.

**Triggers / eligibility / time anchors / terminal states.** Every extended policy inherits the
base eligibility contracts unchanged (`own_policy_evidenced`, `trip_confirmed_not_started`,
`election_chosen_before_charging`, `change_decision_window`, `deductible_dispute_window`,
`protection_refund_not_duplicated`, `cover_starts_with_trip`, `void_only_before_completion`); none
is weakened by an extended rule, by a tool body or by a params block. No extended rule adds a
confirmation, review, wait or back-office procedure. PASS, subject to finding F-3 below.

**Cross-category read boundaries.** All five policies declare `cross_category: [{category: trips}]`
and read only `trips_bookings` fields (`daily_rate_amount`, `trip_start_date`, `trip_end_date`,
`reserved_hours_total`, `included_miles_total`, `rate_plan_name`, `delivery_location_type`) and
`trips_charges` (`charge_amount`, `charge_basis`, `charge_date`). Every `CFIELD`/`XSUM`/`XCOUNT`
in the `compute` blocks stays inside that declared set. No policy reads `hostplan`, `payouts`,
`listings`, `roadside` or `service`. PASS.

**Scope exclusivity and joint completeness of the M tasks.** Derived from the charter and the two
masked worlds alone (no `charter_scope` read):

- task 0's world carries an `active` election with an approved change request, one declared
  additional driver and no driver-fee line and no surcharge line — the problem tree
  `level_change_difference -> young_driver_surcharge -> additional_driver_charge`;
- task 1's world carries a `quoted` election with no protection line at all — the problem tree
  `protection_fee_assessment -> level_election_cover`.

The two sets `{additional_driver_charge, young_driver_surcharge, level_change_difference}` and
`{level_election_cover, protection_fee_assessment}` are pairwise disjoint and together cover all
five extended policies. PASS.

---

### rule_compute_equivalence

Check 2 was run sentence by sentence over all five policies in both directions. Every
quantity, window, filter, tier, branch, cross-category read, acting base, grouping, cap/floor and
rounding point in each `compute` carries a `compute_basis` entry, and every `compute_basis` string
was located verbatim in that policy's own `rule`. The sweep back found no rule sentence with no
implementation — with the exceptions recorded here.

**One failure: the per-hundred scaling of `cover_load_rate` has no basis in the rule.**
See finding **F-1**. This is `SOURCE-POLICY RED`.

**Two weaker instances of the same shape** (`move_discount_rate`, `stay_discount_rate`) are
recorded as observations under finding **F-2**.

Everything else in the sweep is clean, and specifically:

- the per-level constants in all five `params` blocks are faithful copies of the base `variants`:
  `level_daily_* == daily_protection_fee_amount`, `level_share_* == protection_fee_percent_of_trip_price`,
  `level_floor_* == protection_fee_minimum_amount`, `driver_fee_* == secondary_driver_fee_amount`,
  `level_surcharge_* == young_driver_protection_surcharge_percent`,
  `level_min_days_declined: 0 / level_min_days_other: 1 == minimum_charge_days`. The hardcoded
  `level_basis` / `new_level_basis` selectors agree with every variant's
  `protection_fee_charging_basis` (Declined and Business Traveler `daily_flat`, the other four
  `greater_of_daily_and_percent`);
- the `/100` on `level_share_*` and on `surcharge_rate` is grounded in the base
  `parameter_schema`, which says in as many words
  `protection_fee_percent_of_trip_price: Protection fee expressed as a percentage of the trip price.`
  and `young_driver_protection_surcharge_percent: ... as a percentage.` — so those two are not
  instances of F-1/F-2;
- `MONTHS`, `DAYS`, `MX`, `MN`, `RND`, `SUM`, `COUNT`, `XSUM`, `XCOUNT`, `LATEST`, `CFIELD` are the
  erlbench restricted forms (`skills/erl-task-instantiate/scripts/check_compute.py:229-400`); the
  12-month window is `0 <= MONTHS(row_date, NOW) < 12`, which is the "last twelve months" the rules
  state.

---

### action_binding_and_uuids

Each `(target_tool, computes)` pair is claimed by exactly one policy — see the table under
`policy_conflict_scan`. No pair is duplicated, and no policy claims a tool another policy claims.

The five uuid8s, each frozen with its tool in `task_tools.py`:

| tool | uuid8 |
| --- | --- |
| `declare_additional_driver_` | `a214c8dd` |
| `post_young_driver_surcharge_` | `f46febb9` |
| `price_level_change_` | `f4995b0a` |
| `confirm_protection_level_` | `63b6fff8` |
| `post_protection_fee_` | `513639f7` |

All five are 8 hex characters, pairwise distinct, share no common prefix beyond the incidental
two characters of `f46febb9`/`f4995b0a`, form no sequence, and none is another with a changed tail.
Nothing suggests batch derivation. PASS.

**Docstrings.** No docstring names another tool, and none states its call's position in the task's
write sequence. Two mild usages are recorded as observations under finding **F-6**.

---

### prerequisite_graph

Check 7 over the whole graph. Every extended policy has `prerequisite` filled in
(`[]` on `guestplan_ext_additional_driver_charge` and `guestplan_ext_level_election_cover`).

| blocked policy | problem | kind | gate | form | resolved_by |
| --- | --- | --- | --- | --- | --- |
| `guestplan_ext_young_driver_surcharge` | `guestplan_ext_additional_driver_charge` | `value_input` | `driver_lines_total` | `state` | `declare_additional_driver_a214c8dd` |
| `guestplan_ext_level_change_difference` | `guestplan_ext_young_driver_surcharge` | `value_input` | `surcharge_lines_total` | `state` | `post_young_driver_surcharge_f46febb9` |
| `guestplan_ext_protection_fee_assessment` | `guestplan_ext_level_election_cover` | `value_input` | `charged_days` | `state` | `confirm_protection_level_63b6fff8` |

- every `problem` points at another policy id in this file, never at a base policy and never at
  itself; **PASS**
- the graph `additional_driver -> young_driver -> level_change` and
  `level_election_cover -> protection_fee_assessment` is two chains, acyclic, no cross-task cycle;
  **PASS**
- every `policy_source` is verbatim locatable in the **blocked** policy's own `rule` — verified by
  string match against `guestplan.extended.yaml` lines 981, 1218 and 1662; **PASS**
- `form: state` on all three edges, so no `fallback_reason` is required and none is present;
  **PASS**
- each `condition` restates the sentence's state at the same strength and scope, neither
  strengthened nor weakened, and carries no authoring-viewpoint phrasing ("in this task", "at the
  opening", "the current world"); **PASS**
- each `resolved_by` is the depended-on policy's own `target_tool`, and each genuinely moves the
  named binding: `declare_additional_driver_a214c8dd` creates a `secondary_driver_fee` row read by
  `driver_lines_total` (`task_tools.py:42-47`); `post_young_driver_surcharge_f46febb9` creates a
  `young_driver_protection_surcharge` row read by `surcharge_lines_total` (`task_tools.py:83-89`);
  `confirm_protection_level_63b6fff8` writes `status='elected'`, `protection_level_name` and
  `coverage_days` read by `charged_days` (`task_tools.py:183-185`); **PASS**
- `kind: value_input` matches `gate` in all three cases: `driver_lines_total`,
  `surcharge_lines_total` and `charged_days` are each a named binding in the blocked policy's own
  `compute`, not an eligibility gate name and not `result`. **PASS**

---

### prerequisite_sentences

Check 6 over the three edges. The four-point test, and the single-reading derivation, for each.

**Edge 1 — `guestplan_ext_young_driver_surcharge` waits on `guestplan_ext_additional_driver_charge`.**

> "The young-driver surcharge on a trip is not fixed before the election's charge lines carry the
> fee due for every additional driver declared on it."

(1) ordering connective: "not ... before". (2) declared `form: state`, and what it waits on is a
record-visible state named in the words the tables and finders use — "the election's charge lines",
"the fee ... for every additional driver declared on it" are `guestplan_charges` rows and
`guestplan_elections.declared_secondary_driver_count`, retrievable through
`find_guestplan_charges` and `find_guestplan_elections`; no action, performer or tool appears.
(3) no tool name, policy id, snake_case token or row id. (4) the `condition` — "The election's
charge lines carry a line charging the additional driver fee for every additional driver the
election declares" — is exactly the sentence's scope, closed over the drivers the election
declares. **Exactly one write of this difficulty brings the state about**:
`declare_additional_driver_a214c8dd` is the only tool in the module that creates a row with
`charge_basis="secondary_driver_fee"`. Derivation with a single reading: the sentence says the
surcharge waits on driver-fee lines; the records show how many drivers the election declares and
which lines stand; the only policy whose own rule describes charging the level's additional driver
fee is `guestplan_ext_additional_driver_charge`; so the resolving action is to take the declared
driver onto the cover and charge for them, and only then fix the surcharge. **PASS.**

**Edge 2 — `guestplan_ext_level_change_difference` waits on `guestplan_ext_young_driver_surcharge`.**

> "The difference due on a move of level is worked out only after the protection already charged on
> the election for the level first held stands complete, the young-driver surcharge included."

(1) "only after". (2) `form: state`; "the protection already charged on the election ... stands
complete, the young-driver surcharge included" names a record state, and the rule's own next
sentences define "the protection already charged on the election" as "the protection fee charged
for the trip, the fee for every additional driver and the young-driver surcharge, less any
protection fee returned against them" — all `guestplan_charges` rows. (3) no tool, id or token.
(4) the `condition` is the same scope. The only write in this difficulty that puts a
`young_driver_protection_surcharge` line on an election is `post_young_driver_surcharge_f46febb9`.
**PASS**, with one observation: see **F-4**.

**Edge 3 — `guestplan_ext_protection_fee_assessment` waits on `guestplan_ext_level_election_cover`.**

> "The protection fee for a trip is fixed only once the election has left the quoted state and
> carries the number of days of cover the level will run for."

(1) "only once". (2) `form: state`; "has left the quoted state" and "carries the number of days of
cover" are `guestplan_elections.status` and `guestplan_elections.coverage_days`, both returned by
`find_guestplan_elections`. (3) clean. (4) scope matches the `condition`. The only write that moves
an election out of `quoted` and writes `coverage_days` is `confirm_protection_level_63b6fff8`
(`task_tools.py:183-185`). Derivation with a single reading: the fee waits on a settled election
carrying its days of cover; the only policy whose own rule describes fixing how many days of cover
an election carries is `guestplan_ext_level_election_cover`; that write is the guest's own act; so
the level must be settled before the fee is worked out. **PASS.**

**No second wording, no tool name, no other problem's id** appears in any of the three blocked
rules beyond its one prerequisite sentence, and **none of the three depended-on rules restates the
sentence**: `guestplan_ext_additional_driver_charge`'s rule nowhere mentions the surcharge,
`guestplan_ext_young_driver_surcharge`'s rule nowhere mentions a move of level, and
`guestplan_ext_level_election_cover`'s rule nowhere mentions the protection fee.

**No undeclared cross-problem order.** An ordering-cue sweep over all five extended rules
(`before|after|only once|only after|until|not until|first|prior to|once`) returned 17 sentences;
14 of them speak of the trip's own timeline ("once the trip has begun", "before the trip has
begun") or of the rounding point ("rounded ... only once the whole of it has been worked out"), and
the remaining 3 are exactly the three declared prerequisite sentences above. No rule states a
cross-problem order that grounds no declared edge. No **base** rule sentence grounds any edge.
**PASS.**

---

### override_declarations

Check 1's finding half, run once, sentence by sentence against each `base_policy_refs` entry. The
base policies referenced across the charter are `guestplan_evt_fee_charging` (4 times),
`guestplan_level_change`, `guestplan_agg_claim_history` and `guestplan_election_eligibility`.

**Declared and sound:**

| extended policy | base sentence named in `overwrite` | conclusion |
| --- | --- | --- |
| `..._additional_driver_charge` | "Additional drivers are charged the level's additional driver fee once each for the whole trip, not once for each day, and a level that carries no additional driver fee charges nothing however many drivers are approved." | declared; the extended seat-rate/seat-days/uplift/load construction replaces the whole clause, including the "charges nothing" tail that would otherwise fight the band uplift on Premier and Business Traveler. Merged semantics unique. |
| `..._young_driver_surcharge` | "A driver under the young-driver threshold pays the level's protection surcharge on the fee, and the surcharge is posted as its own line so that it can be reversed on its own." | declared; the extended base-selection/rate/ceiling/step construction replaces it. Merged semantics unique. |
| `..._level_change_difference` | "Where that basis is the remaining whole days, the difference between the two levels' daily fees is charged for the days left in the trip counted from the day of the change, the day of the change itself included." | declared. |
| `..._level_change_difference` | "A change made once the trip has started carries the level's mid-trip change fee where the level has one, posted as part of the same line rather than separately." | declared. |
| `..._level_election_cover` | "Charged days are the whole days of the trip as reserved, with any part day counted as a whole day, and never fewer than the level's minimum charge days." | declared; replaced by the covered-days definition. |
| `..._protection_fee_assessment` | "The fee arrived at is then held between the level's floor and its ceiling, the floor applied first and the ceiling last, so a trip long enough to pass the ceiling pays the ceiling and no more." | declared; replaced by the loyalty/long-stay/trip-ceiling/mileage-step construction, whose closing sentence states the order floor-then-ceiling-then-step and whose `result` implements exactly that. |

**Base provisions inherited in full and not weakened anywhere**: all eight base eligibility
contracts; `guestplan_agg_multi_holding` (one live election per trip); `guestplan_agg_claim_history`
in its entirety, including the sentence "a guest whose covered days would take one trip past the
level's maximum trip length is quoted on the level that will carry the whole trip rather than on
one that would run out midway", which no `overwrite` touches and which therefore binds the level
selection at `guestplan_election_confirmed`; `guestplan_election_eligibility`'s age, score, vehicle
value, excluded class, own-policy-evidence, commercial and cross-border gates;
`guestplan_lifecycle`; `guestplan_void`; `guestplan_evt_deductible`; `guestplan_evt_refund`.

**Three deviations from base that no `overwrite` names** — findings **F-3**, **F-5** and **F-7**
below. Findings only; each affected task's file demonstrates or disclaims the consequence against
its own world.

---

### factor_ladders

Structure only. Whether a factor bears weight is a fact about one world and lives in that task's
`factor_weight`.

| policy | factor | effect | decides | tiers | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| `..._additional_driver_charge` | `seat_rate_by_guest_record` | parameter | `seat_fee_rate` | 3 | yes (12m base-rate spend ∧ 12m cancellation-fee count) | `trips` |
| | `seat_days_convention` | method | `seat_days` | 3 | yes (trip-begun ∧ covered-days threshold) | — |
| | `vehicle_band_uplift_step` | parameter | `vehicle_band_uplift` | 3 | no | — |
| | `cover_load_share` | parameter | `cover_load_rate` | 3 | no | — |
| `..._young_driver_surcharge` | `surcharge_base_selection` | method | `surcharge_base` | 3 | yes (declared drivers ∧ cover running) | — |
| | `surcharge_percent_by_driving_record` | parameter | `surcharge_rate` | 3 | yes (12m late returns ∧ 12m mileage overages) | `trips` |
| | `surcharge_ceiling_by_cover_length` | parameter | `surcharge_cap` | 3 | no | — |
| | `trip_length_step` | parameter | `trip_step` | 3 | no | — |
| `..._level_change_difference` | `new_level_cost_basis` | method | `new_level_cost` | 3 | no | — |
| | `credit_for_cover_used` | method | `credit_for_days_left` | 3 | yes (cover running ∧ covered-days threshold) | — |
| | `move_discount_by_cover_left` | parameter | `move_discount_rate` | 3 | yes (days-left share ∧ reserved months) | — |
| | `change_fee_by_move_history` | parameter | `change_fee` | 3 | yes (cover running ∧ earlier move lines) | — |
| | `young_driver_move_step` | parameter | `young_move_step` | 3 | yes (12m young-driver surcharges ∧ trip daily rate) | `trips` |
| | `party_step_by_drivers_covered` | parameter | `party_step` | 3 | no | — |
| `..._level_election_cover` | `plan_day_count_convention` | method | `plan_days` | 3 | no | — |
| | `handover_grace_by_delivery` | parameter | `handover_grace` | 3 | no | — |
| | `late_return_allowance` | parameter | `late_return_cover` | 3 | yes (12m late returns ∧ rate plan) | `trips` |
| | `cover_ceiling_by_reserved_time` | parameter | `cover_ceiling` | 3 | no | — |
| `..._protection_fee_assessment` | `fee_basis_by_level` | method | `base_fee` | 3 | no | — |
| | `loyalty_rate_by_trip_record` | parameter | `loyalty_fee_rate` | 3 | yes (12m base-rate trip count ∧ 12m mileage overages) | `trips` |
| | `long_stay_discount` | parameter | `stay_discount_rate` | 3 | no | — |
| | `trip_fee_ceiling_by_reservation` | parameter | `trip_fee_ceiling` | 3 | no | — |
| | `mileage_exposure_step` | parameter | `mileage_step` | 3 | no | — |

**Counts per computation** — all within 4..6, all with ≥2 `parameter` and ≥1 `method`:
additional_driver 4 (3P/1M); young_driver 4 (3P/1M); level_change 6 (4P/2M);
level_election_cover 4 (3P/1M); protection_fee_assessment 5 (4P/1M). **PASS.**

**Per task**: task 0's three computations carry 5 multi-source factors and 3 `cross_difficulty:
trips` factors; task 1's two computations carry 2 multi-source factors and 2 `cross_difficulty:
trips` factors. Both floors met. **PASS.**

**Disjointness and `decides`.** Every factor's `bindings` set is disjoint from every other factor's
within its policy (checked pairwise), and every `decides` names an intermediate input binding, never
`result`. **PASS.**

**Tiers pairwise disjoint as stated, and distinct in outcome.** Each of the 23 ladders has exactly
3 tiers whose conditions partition the domain (checked against the `compute` if/else chain that
implements them), and no two tiers of any one ladder select the same value or the same method:

- every numeric ladder has three distinct constants (e.g. `0.70 / 0.85 / 1.00`,
  `14.0 / 17.0 / level's own percent`, `900 / 400 / 150`, `45 / 25 / 0`, `12.0 / 6.0 / 0.0`,
  `45 / 20 / 0`, `55 / 30 / 0`, `60 / 30 / 0`, `2 / 1 / 0`, `3 / 2 / 0`, `120 / 90 / 30`,
  `0.90 / 0.95 / 1.00`, `3200 / 2400 / 1200`, `90 / 45 / 0`, `14 / 9 / 0`, `1.0 / 0.6 / 0.0`);
- every `method` ladder has three genuinely different algorithms (whole-weeks vs calendar-days vs
  covered-days; net-fee+driver-fees vs level-daily×covered-days vs net-fee alone; greater-of vs
  share-of-price vs daily×days; spread-evenly-and-prorate vs whole-of-charged vs old-daily×days).

`surcharge_percent_by_driving_record`'s third tier selects "the level's own protection surcharge
percentage", which for the six levels is 0/25/22/18/15/12 — never equal to `14.0` or `17.0` on any
level. **PASS.**

**Every tier stated in the `rule` and implemented in `compute`.** Each of the 69 tiers was matched
to a clause of its policy's `rule` prose and to a branch of its `decides` binding. No tier lives
only in `compute`, and no branch of a `decides` binding is absent from the rule. **PASS**, with one
observation: see **F-8**.

**Labels are honest.** Each `method` factor's tiers change the algorithm rather than substituting a
constant, and each `parameter` factor's tiers substitute a value into an unchanged formula. Each
`method` tier names a rule the charter states — in particular `fee_basis_by_level` and
`new_level_cost_basis` name the three charging bases the base `parameter_schema` defines
(`protection_fee_charging_basis: ... one of daily_flat, percent_of_trip_price or
greater_of_daily_and_percent`), and `plan_day_count_convention` names rate plans the blueprint's
`trips` charter writes. **PASS.**

**Conditions and outcomes are ones this line of business actually holds.** Spend- and
history-based loyalty seat rates and fee rates, a band uplift by the vehicle's locked daily rate, a
load on the cover already bought, a driving-record surcharge rate, a surcharge ceiling by cover
length, a step by reservation length, a discount for moving level with most of the trip left, a
first-move vs repeat-move fee, a young-driver step, a party step by drivers covered, day-count
conventions that follow the rate plan, an airport/delivered/self-collect handover grace, a
late-return allowance, a cover ceiling and fee ceiling by reservation size, and a mileage-exposure
step are all things a peer-to-peer car-sharing marketplace weighs when settling these quantities,
and none of them holds of every customer who reaches the write. Every fall-through outcome is a
treatment the business would publish for an ordinary customer: the standard seat rate `1.00` and
loyalty rate `1.00` (full price, no loyalty discount), the level's own published surcharge
percentage, the level's own published daily amount for the days, no uplift, no load, no step, no
discount, the standard cover ceiling and the short-trip fee ceiling. **PASS.**

**`baseline` blocks.** Every policy declares a `baseline` with a `rule` extracted verbatim from its
own `rule` and a `params` list, and in every case each factor's fall-through tier is exactly what
that baseline states for the binding:

| policy | baseline value for each factor's fall-through |
| --- | --- |
| `..._additional_driver_charge` | `seat_fee_rate = seat_rate_standard`, `seat_days = covered_days`, `vehicle_band_uplift = 0`, `cover_load_rate = 0` — "the level's additional driver fee, taken in full for the whole of the election's covered days" |
| `..._young_driver_surcharge` | `surcharge_base = fee_lines_net`, `surcharge_rate = level_surcharge_percent`, `surcharge_cap = short_trip_surcharge_ceiling`, `trip_step = 0` — all four in the baseline rule's two sentences |
| `..._level_change_difference` | `new_level_cost = new_level_daily * days_still_to_run`, `credit_for_days_left = old_level_daily * days_still_to_run`, `move_discount_rate = 0`, `change_fee = 0`, `young_move_step = 0`, `party_step = 0` |
| `..._level_election_cover` | `plan_days = ceil(reserved_hours/24) floored at minimum_cover_days`, `handover_grace = 0`, `late_return_cover = 0`, `cover_ceiling = standard_cover_ceiling_days` |
| `..._protection_fee_assessment` | `base_fee = level_daily * charged_days`, `loyalty_fee_rate = 1.00`, `stay_discount_rate = 0`, `trip_fee_ceiling = short_trip_fee_ceiling`, `mileage_step = 0` |

Every `baseline.rule` is self-sufficient — a reader computes a definite number from it and the
records with no factor applied — and every sentence of each `baseline.rule` is a verbatim sentence
of that policy's full `rule`. Every `baseline.params` key list names exactly the constants the
baseline rule uses. **PASS.**

---

### findings

#### F-1 — `SOURCE-POLICY RED`: the per-hundred scaling of the cover load is implemented in `compute` and stated nowhere in the `rule`

- **Symptom.** `guestplan_ext_additional_driver_charge` arrives at two different numbers for the
  same additional-driver fee depending on whether the reader follows the published rule or the
  `compute` binding, and the two differ by a factor of 100 on the cover-load term.
- **Root cause.** The rule states the cover load as a rate *charged on* an amount and never says it
  is a percentage, while `compute` divides it by 100. The parameter names carry no `percent` and
  the base `parameter_schema` — which does ground the `/100` on `level_share_*` and on
  `surcharge_rate` — has no entry for a cover load at all.
- **Evidence.** `guestplan.extended.yaml:778-782` (rule):

  > "A cover load is added as a share of the protection already charged on the election for the
  > trip. ... Where the protection already charged reaches the high cover threshold, the high cover
  > load rate is charged on it; where it reaches the middle cover threshold but not the high cover
  > threshold, the middle cover load rate is charged on it; where it reaches neither, no cover load
  > is charged."

  `guestplan.extended.yaml:752-754` (params): `high_cover_load_rate: 1.0`,
  `middle_cover_load_rate: 0.6`, `no_cover_load_rate: 0.0`.
  `guestplan.extended.yaml:809` (compute `result`):
  `RND(level_driver_fee * seat_fee_rate * seat_days / covered_days + vehicle_band_uplift + protection_charged_before * cover_load_rate / 100, 2)`.
  `compute_basis.cover_load_rate` and `compute_basis.result`
  (`guestplan.extended.yaml:826, 827`) quote only the two sentences above; neither contains the
  word percent, per cent, per hundred, or any other statement of the scaling.
  Contrast `guestplan_evt_fee_charging`'s base `parameter_schema` entries
  (`blueprint/products/guestplan.yaml:35, 58`), which do say "as a percentage" for the two
  bindings whose `/100` is legitimate.
- **Demonstrated consequence.** Written out in task 0's file against its own world and scored
  solution — the rule reading gives a driver fee two orders of magnitude above the compute reading,
  and the divergence then propagates through both downstream problems of that task's tree. See
  `env/env_0015_car_sharing_marketplace/audits/policy_task/guest_protection_desk/0.md`,
  §`policy_self_consistency (this task only)`.
- **Affected artifact and location.** `tasks/guest_protection_desk/guestplan.extended.yaml`,
  policy `guestplan_ext_additional_driver_charge`: `rule` (the cover-load paragraph), `params`
  (`high_cover_load_rate`, `middle_cover_load_rate`, `no_cover_load_rate`), `compute[result]`,
  `compute_basis[cover_load_rate]`, `compute_basis[result]`, factor `cover_load_share`. Bears on
  **task 0** only.
- **Relation to previous revisions.** New in revision 1.

#### F-2 — observation: two further scaling conventions carried only by the parameter name

- **Symptom.** `move_discount_rate` (`guestplan_ext_level_change_difference`) and
  `stay_discount_rate` (`guestplan_ext_protection_fee_assessment`) are each divided by 100 in
  `compute` while their rules say only that the rate "is taken off".
- **Evidence.** `guestplan.extended.yaml:1188-1193` and `:1258` ("where half or more of the
  election's covered days are still to run ... the long move discount rate is taken off";
  `result: RND(new_level_cost * (1 - move_discount_rate / 100) - ...)`);
  `guestplan.extended.yaml:1639-1643` and `:1694` ("the long stay discount rate is taken off";
  `... base_fee * loyalty_fee_rate * (1 - stay_discount_rate / 100) ...`).
- **Why this is an observation and not a red light.** Unlike F-1, "a discount rate of 12.0 taken
  off a cost" has only one commercially sensible reading, and the alternative (subtracting a factor
  of 12) produces a negative fee that no reader would accept. No second defensible number follows,
  so the consequence the "Core constraints" table demands cannot be demonstrated.
- **Affected artifact and location.** `guestplan_ext_level_change_difference.rule` / `compute`;
  `guestplan_ext_protection_fee_assessment.rule` / `compute`. Bears on **task 0** and **task 1**
  respectively.

#### F-3 — observation: the base billing-point sentence is not named in any `overwrite`

- **Symptom.** `guestplan_ext_protection_fee_assessment` opens "The protection fee for a trip is
  charged once against the election that carries the cover", which is a different disposition of
  the same quantity from the base sentence it never names.
- **Evidence.** Base `guestplan_evt_fee_charging` (`blueprint/products/guestplan.yaml:518`):

  > "The fee falls due at the level's billing point, whether at booking, at the start of the trip
  > or daily in arrears, and a level billed daily in arrears posts one line for each completed day
  > rather than one line for the trip."

  `guestplan_ext_protection_fee_assessment.overwrite` names only the floor/ceiling sentence
  (`guestplan.extended.yaml:1567-1573`).
- **Why this is an observation.** The base sentence's posting claim is expressly restricted to the
  `daily_in_arrears` levels, and the only level with that billing point is Keyturn Business
  Traveler Protection. Neither task's election stands on that level, so no second defensible
  number or sequence follows on either world. The "falls due" half governs when the guest owes the
  money, which no field of `guestplan_charges` records; the base posting gate that does bind — "A
  fee line is posted only while the election is in the elected or active state" — is inherited
  unweakened and is satisfied in both tasks.
- **Affected artifact and location.** `guestplan_ext_protection_fee_assessment.overwrite`.

#### F-4 — observation: edge 2's waited-on state is broader than the single write the edge declares

- **Symptom.** The prerequisite sentence of `guestplan_ext_level_change_difference` waits on "the
  protection already charged on the election for the level first held stands complete, the
  young-driver surcharge included", and that policy's own definition of "the protection already
  charged" is the fee lines *and* the additional-driver fees *and* the surcharge. Two writes of
  this difficulty therefore bear on "stands complete", while the edge declares one.
- **Evidence.** `guestplan.extended.yaml:1218` (the sentence) against `:1180-1181` ("The protection
  already charged on the election is the protection fee charged for the trip, the fee for every
  additional driver and the young-driver surcharge, less any protection fee returned against
  them.") and `prerequisite[0].resolved_by: post_young_driver_surcharge_f46febb9`.
- **Why this is an observation.** The trailing apposition "the young-driver surcharge included"
  singles the surcharge out, and the additional-driver leg is independently reachable through
  edge 1's own sentence on the surcharge policy, so both readings converge on the same topological
  order `additional_driver -> young_driver -> level_change`. No second order and no second terminal
  state follow.
- **Affected artifact and location.**
  `guestplan_ext_level_change_difference.prerequisite[0].policy_source`. Bears on **task 0**.

#### F-5 — observation: the base downgrade-credit sentence is not named in any `overwrite`

- **Symptom.** `guestplan_ext_level_change_difference` prices every move of level as
  `new_level_cost * (1 - discount) - credit + fees + steps`, with no downgrade branch, while base
  `guestplan_level_change` prescribes a distinct treatment for a move down.
- **Evidence.** Base (`blueprint/products/guestplan.yaml:554`):

  > "A downgrade returns the level's downgrade credit percentage of the same difference and never
  > the whole of it, because cover already run cannot be given back; a level whose downgrade credit
  > is nil returns nothing at all."

  The extended policy's `overwrite` (`guestplan.extended.yaml:1117-1127`) names two other base
  sentences and not this one; `downgrade_credit_percent` appears in no `params` block and in no
  `compute` binding of the charter.
- **Why this is an observation.** The undeclared conflict bites only on a move to a lower-ranked
  level. Task 0's approved change request is Keyturn Standard Protection -> Keyturn Advantage
  Protection, a move up, so no second defensible number follows on either world.
- **Affected artifact and location.** `guestplan_ext_level_change_difference.overwrite`.

#### F-6 — observation: two docstring phrases carry an ordering word

- **Symptom.** `declare_additional_driver_a214c8dd` says "Once the line stands, the extra driver is
  an approved driver on that trip"; `post_young_driver_surcharge_f46febb9` says "so that it can
  later be reversed on its own"; `price_level_change_f4995b0a` says "measured against the protection
  fee line **already raised** for the level first held".
- **Evidence.** `task_tools.py:20-21`, `task_tools.py:59-60` and `task_tools.py:97-99`.
- **Why this is an observation.** None names another tool, and none states its call's position in
  this task's write sequence: the first describes the effect of its own call, the second a
  hypothetical future reversal that no policy of this difficulty performs, and the third describes
  the row the `source_charge_id` argument must point at — which in both tasks that use it is a
  seeded row, not one a sibling problem writes. No prerequisite becomes discoverable from a
  docstring rather than from a rule.
- **Affected artifact and location.** `tasks/guest_protection_desk/task_tools.py`.

#### F-7 — observation: `guestplan_ext_protection_fee_assessment` redefines the charged days without naming the base sentence in its own `overwrite`

- **Symptom.** That policy says "The charged days are the election's covered days, never fewer than
  the level's minimum charge days", which is a different basis from base
  `guestplan_evt_fee_charging`'s "Charged days are the whole days of the trip as reserved, with any
  part day counted as a whole day, and never fewer than the level's minimum charge days".
- **Evidence.** `guestplan.extended.yaml:1623` against `blueprint/products/guestplan.yaml:515`; the
  `overwrite` of `guestplan_ext_protection_fee_assessment` names only the floor/ceiling sentence.
- **Why this is an observation.** The very same base sentence *is* named and retired charter-wide by
  `guestplan_ext_level_election_cover.overwrite` (`guestplan.extended.yaml:1403-1408`), and the two
  extended statements agree — charged days = covered days. Base and extended are rendered together,
  so the base clause is not left standing to fight the extended one, and the merged semantics are
  unique. What is irregular is only the placement of the declaration, and no second defensible
  value follows on either world.
- **Affected artifact and location.** `guestplan_ext_protection_fee_assessment.overwrite`.

#### F-8 — observation: one tier of two `method` ladders is unreachable on this charter's six levels

- **Symptom.** `fee_basis_by_level`'s second tier ("the level ... arrives at its fee as a share of
  the trip price") and `new_level_cost_basis`'s second tier (same) select the
  `percent_of_trip_price` branch, which no variant of `guestplan` uses: the base `variants` put
  Declined and Business Traveler on `daily_flat` and the other four on
  `greater_of_daily_and_percent`.
- **Evidence.** `blueprint/products/guestplan.yaml:97, 120, 143, 166, 189, 212`
  (`protection_fee_charging_basis` per variant) against `guestplan.extended.yaml:1725` and `:1297`; `compute`'s `level_basis` / `new_level_basis` bindings can only ever return
  `'daily_flat'` or `'greater_of_daily_and_percent'`.
- **Why this is an observation.** The basis is one the business publishes — the base
  `parameter_schema` names all three bases in as many words — and the three tiers remain pairwise
  disjoint and distinct in method, so no tier has been written as two and no condition restates the
  policy's scope. The tier is simply dead on the current variant table, which changes no
  relationship on either task's world.
- **Affected artifact and location.** `guestplan_ext_protection_fee_assessment.factors[0]`,
  `guestplan_ext_level_change_difference.factors[0]`.

#### F-9 — observation: the young-driver threshold itself is stated nowhere in this charter

- **Symptom.** `guestplan_ext_young_driver_surcharge`'s rule opens "A guest under the marketplace's
  young-driver threshold on the first day of a trip carries a loading", and neither the base
  section nor any extended policy of `guestplan` states what that threshold is. The base
  `parameter_schema` entry (`blueprint/products/guestplan.yaml:60`) describes the surcharge
  percentage but not the age.
- **Why this is an observation.** The loading's applicability never has to be decided from the age:
  the blocked policy's prerequisite sentence — "the protection already charged ... stands complete,
  the young-driver surcharge included" — entails that the surcharge is owed on any election whose
  move of level is being priced, and the guest's own `trips` ledger carries a
  `young_driver_surcharge` line on the very booking. The charter's entailment is therefore intact
  without the number.
- **Affected artifact and location.** `guestplan_ext_young_driver_surcharge.rule`. Bears on
  **task 0**.

---

## closing_checklist

Written **after** both tasks' reveals, at 2026-09-22T09:23:02Z. The section above this heading is
pre-reveal by construction and has not been touched since the reveal, except to extend finding
**F-6** with a third docstring phrase that no reveal was needed to see.

**This difficulty does not close out.** Task 1 passes on all four relationships; task 0 carries two
red lights. The checklist below is therefore recorded item by item, with the items that hold marked
as such and the items that do not naming the finding that blocks them.

| Step 4 item | status |
| --- | --- |
| the per-task audit files correspond one-to-one with the tasks, and `_difficulty.md` sits alongside them | **holds** — `0.md`, `1.md` and `_difficulty.md` in `env/env_0015_car_sharing_marketplace/audits/policy_task/guest_protection_desk/`, against `tasks/0.json` and `tasks/1.json` |
| old revisions are traceable | **holds** — revision 1; no prior revision existed on disk, and nothing was overwritten |
| every comparison section carries a PASS | **does not hold** — `1.md` §`source_gt_comparison` is PASS on all four; `0.md` is SOURCE-POLICY RED (T0-F1 / charter-global F-1) and SOURCE-FACTOR RED (T0-F2) |
| this difficulty's extended policies are fully covered and the M tasks' scopes are pairwise disjoint, each scope spanning the whole problem tree | **holds** — task 0 claims `{additional_driver_charge, young_driver_surcharge, level_change_difference}`, task 1 claims `{level_election_cover, protection_fee_assessment}`; disjoint, and together all five. Each `charter_scope` covers the root and every prerequisite problem of its own tree |
| task tools and GT are closed | **holds** — 5 tools, each claimed by exactly one policy and called by exactly one task; `replay_tasks.py --check` reproduces both terminal states with 0 errors and `match=True` |
| each task tool uses an independently generated, frozen uuid8 | **holds** — `a214c8dd`, `f46febb9`, `f4995b0a`, `63b6fff8`, `513639f7`; see §`action_binding_and_uuids` |
| every task's problem tree has one to three prerequisite problems | **holds** — task 0 has 2, task 1 has 1 |
| at least max(n−1, 1) `value_input` edges | **holds** — task 0: 2 edges, both `value_input`, floor 1; task 1: 1 edge, `value_input`, floor 1 |
| at least one problem resolved by an `owner=user` tool | **holds** — task 0 `declare_additional_driver_a214c8dd`, task 1 `confirm_protection_level_63b6fff8`; the charter's only two `owner=user` writes, one to each task |
| no cycle, and the difficulty's `prerequisite` edges together are still a DAG with no cycle created by cross-task references | **holds** — two disjoint chains, `additional_driver -> young_driver -> level_change` and `level_election_cover -> protection_fee_assessment`; no edge crosses between the two task scopes |
| every computation declares a self-sufficient baseline | **holds** — five baselines, each giving a definite number different from gold on its task's world: 20.00, 150.00, 432.00 (task 0); 30, 1200.00 (task 1) |
| four to six factors per computation, 2 `parameter` and 1 `method` | **holds** — 4 / 4 / 6 and 4 / 5, all with ≥ 2 `parameter` and ≥ 1 `method` |
| per task at least 1 multi-source and 1 cross-difficulty factor | **holds** — task 0: 7 multi-source, 3 cross-difficulty (`trips`); task 1: 2 multi-source, 2 cross-difficulty (`trips`) |
| every ladder of at least three tiers stated in full in its rule | **holds** — 23 ladders, 3 tiers each, every tier located in its policy's `rule` prose and in its `decides` binding |
| tiers distinct in outcome, conditions and outcomes ones that line of business actually holds | **holds** — see §`factor_ladders`; observation F-8 records one tier that is dead on the current variant table without collapsing its ladder |
| every factor proved to bear weight on its task's world against an honest baseline | **holds on recomputation** — all 23 factors move their scored value when their `baseline` is substituted, and every `baseline` is what its policy's `baseline.rule` states for that input. **But one submitted proof of this is false**: finding T0-F2, `tasks/0.json` `computations[0].factor_trace[0]` and `design_rationale` assert 39.00 where the world gives 38.60 |
| the baseline alone giving a definite number different from gold | **holds** — 20.00 ≠ 36.50, 150.00 ≠ 296.40, 432.00 ≠ 211.12, 30 ≠ 81, 1200.00 ≠ 3272.03 |
| this difficulty's instantiation-stage gates re-run once on the final form | **done** — see below |

### Instantiation-stage gates, re-run on the final form

Run from the repository root at 2026-09-22T09:22Z against
`DIFF=env/env_0015_car_sharing_marketplace/tasks/guest_protection_desk`:

```
check_extended.py    $DIFF          -> EXTENDED OK   (category=guestplan, extended_policies=5, cross-cat=5, task_tools=5, tasks=2, no_handoff=True)
check_task_tools.py  $DIFF          -> TASK TOOL CONTRACT OK   (5 tools)
check_solvability.py $DIFF          -> SOLVABILITY OK   (0.json True 3 3 3 True / 1.json True 2 4 1 True)
check_compute.py     $DIFF          -> COMPUTE OK   (suite means branches=66.00 steps=12.50; depth history_rows_max=10 branches_max=78)
check_grounding.py   $DIFF          -> GROUNDING OK   (0.json 2 3 3 12 True / 1.json 2 2 2 9 True)
check_cross_fire.py  $DIFF          -> SCOPE OK   (2 tasks, policies=5, hard-fails=0)
replay_tasks.py      $DIFF --check  -> REPLAY OK   (0.json 14 True True 0 19 19 True / 1.json 11 True True 0 17 17 True)
```

All seven are green on the final form, identical to the entry snapshot. **They do not overturn the
two red lights**: no script checks whether a rule's prose and its `compute` binding agree on a
scaling convention (F-1 / T0-F1), and no script recomputes the figures a `factor_trace` sentence
asserts (T0-F2). That is precisely the gap a manual audit exists to cover.

### Artifacts unchanged by this audit

Verified after the gate re-run: `guestplan.extended.yaml` sha256:16 `a7e5821b0e67c075` and
`task_tools.py` sha256:16 `a26d40350c5c0987` — both identical to the values frozen in
§`charter_global_frozen`. The masked views are likewise unchanged (`858e4c67ec7ebf24`,
`ff4ecf45949506ec`). Nothing under `blueprint/`, `tasks/` or `erlbench/` was edited; the audit's
only writes are the three files in this directory.

### Verdict for the difficulty

| task | policy self-consistency | problem tree | factors bear weight | unique solution | overall |
| --- | --- | --- | --- | --- | --- |
| 0 | **SOURCE-POLICY RED** (T0-F1) | PASS | **SOURCE-FACTOR RED** (T0-F2) | PASS | **RED** |
| 1 | PASS | PASS | PASS | PASS | **PASS** |

Since "policy self-consistency PASS + problem tree holds PASS + factors bear weight PASS + unique
solution PASS" does not hold together for task 0, **this difficulty does not pass the source-layer
audit.** Both red lights are defects of the artifacts, not of any solving agent: T0-F1 is a rule
that does not say what its `compute` does, and T0-F2 is a figure in the submitted proof that the
world does not produce. Neither is repaired here, and no fix is designed or arranged.

---

# revision_2

Round 2 re-audit. **Revision 1 above is preserved unaltered**; nothing in it has been rewritten to
accommodate the reworked artifacts.

## charter_global_frozen_r2

| item | round 1 | round 2 |
| --- | --- | --- |
| `guestplan.extended.yaml` sha256:16 | `a7e5821b0e67c075` | **`578bb1a8bbd48c29` — CHANGED** |
| `task_tools.py` sha256:16 | `a26d40350c5c0987` | **`97f057796ce850bd` — CHANGED** |
| masked view `0.json` sha256:16 | `858e4c67ec7ebf24` | `858e4c67ec7ebf24` — unchanged, re-verified |
| masked view `1.json` sha256:16 | `ff4ecf45949506ec` | `ff4ecf45949506ec` — unchanged, re-verified |
| `tasks/0.json` sha256:16 | — | `339928690b464b50` (moved) |
| `tasks/1.json` sha256:16 | — | `63aed43d8c91c322` (moved) |
| freeze time (UTC) | 2026-09-22T09:07:43Z | 2026-09-22T09:31:10Z |

**Both charter-level hashes moved, so every charter-global section below is re-derived in full
rather than carried forward by reference**, exactly as the re-derivation rule requires.

**contamination_disclosure (round 2).** This is a re-audit, and the round-1 gold values for both
tasks are already in this auditor's context from the round-1 reveal. Round 2's derivation therefore
**cannot be blind in the round-1 sense, and is not presented as such.** What it is instead, and what
makes it independent evidence: every figure below was produced by evaluating the **reworked
charter's own `compute` blocks** against the **unchanged masked worlds**, using erlbench's own
evaluator (`build_env` / `eval_compute` from
`skills/erl-task-instantiate/scripts/check_compute.py`), with the write chain simulated from the
tool bodies — not by transcribing round 1's numbers forward. Where round 2 reproduces a round-1
figure that is a finding, not an assumption: it shows the rework did not move the arithmetic. The
round-1 blind derivations stand above as written, and none was edited.

**Fields permitted**: the whole reworked `guestplan.extended.yaml` and `task_tools.py`;
`blueprint/` (blueprint.yaml, db_schema.json, share_tools.py, products/guestplan.yaml,
products/trips.yaml); the three masked fields of each task; `erlbench/` and the instantiation
scripts. **Fields masked until the freeze below was on disk**: both task files'
`evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`,
`solvability_contract`, `prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state`.

### base_copy_r2

`diff <(sed -n '1,718p' guestplan.extended.yaml) blueprint/products/guestplan.yaml` returns only
`718d717 <` — one trailing blank line, as in round 1. **The base section was not edited.** This
matches the coordinator's independent key-for-key check. Every base sentence quoted in revision 1
is still at the same line: `:515` (charged days), `:518` (billing point), `:554` (downgrade
credit), and the eight base eligibility contracts are untouched.

### what changed in the charter, enumerated

Re-derived by reading the reworked file against revision 1's record of the round-1 form. Six
edits, all in `extended_policies`, plus three docstring edits:

| # | location | edit |
| --- | --- | --- |
| 1 | `guestplan_ext_additional_driver_charge` | params `high/middle/no_cover_load_rate` renamed to `…_percent`; rule gains **"The cover load is the cover load percentage of the protection already charged, expressed as a percentage of that amount."**; the three ladder sentences now say "percentage"; new compute binding `cover_load_amount: protection_charged_before * cover_load_percent / 100` with its own `compute_basis` quoting the new sentence; `result` now reads `… + cover_load_amount`; factor `cover_load_share` re-pointed to `cover_load_percent` in `decides`, `bindings`, ladder values and `baseline` |
| 2 | `guestplan_ext_level_change_difference` | rule gains **"The move discount is the move discount rate of that cost, expressed as a percentage of it."**; new compute binding `discounted_new_level_cost: new_level_cost * (1 - move_discount_rate / 100)` with its own `compute_basis` quoting it; `result` now reads `discounted_new_level_cost - credit_for_days_left + …` |
| 3 | `guestplan_ext_level_change_difference` | opening rule sentence narrowed from "A guest who moves to a different protection level…" to **"A guest who moves **up to a protection level of higher rank than the one first held**…"**; `compute_basis[requested_level]` updated to quote the narrowed sentence |
| 4 | `guestplan_ext_protection_fee_assessment` | rule gains **"The long-stay discount is the stay discount rate of the figure it is taken off, expressed as a percentage of that figure."**; new compute binding `discounted_fee: base_fee * loyalty_fee_rate * (1 - stay_discount_rate / 100)` with its own `compute_basis`; `result` now reads `RND(MN(MX(discounted_fee, level_floor), trip_fee_ceiling) + mileage_step, 2)` |
| 5 | `guestplan_ext_protection_fee_assessment` | `overwrite` grows from 1 entry to 3: the base billing-point sentence and the base charged-days sentence are now each named with their replacement |
| 6 | `task_tools.py` | `declare_additional_driver_a214c8dd`: "Once the line stands, the extra driver is…" → "With that line on the election the extra driver stands as…", and `days_covered` re-described as "the seat days the extra driver's fee was measured across"; `post_young_driver_surcharge_f46febb9`: "so that it can later be reversed on its own" → "which keeps the loading separable from the fee itself"; `price_level_change_f4995b0a`: "the protection fee line **already raised** for the level first held" → "…**standing** for the level first held" |

No other rule sentence, parameter value, factor, ladder tier, baseline, prerequisite edge, tool
signature, tool body or uuid8 moved. Confirmed structurally: the five policies still carry
4 / 4 / 6 / 4 / 5 factors with the same ids, effects, `decides` (bar the `cover_load_percent`
rename), `cross_difficulty` assignments and 3-tier ladders; `guestplan_ext_young_driver_surcharge`
and `guestplan_ext_level_election_cover` have byte-equivalent `compute` binding lists to round 1.

### policy_conflict_scan_r2

Five extended policies, five distinct `target_tool`s, five distinct `computes` — the table in
revision 1 §`policy_conflict_scan` still holds verbatim, with no pair duplicated. Cross-category
reads are still `trips` only, and every `CFIELD`/`XSUM`/`XCOUNT` stays inside the declared field
set. Task scopes are still disjoint and jointly complete over the five policies.

**One new question the rework raises, and its answer.** The base sentence "Charged days are the
whole days of the trip as reserved…" is now named in **two** policies' `overwrite`:
`guestplan_ext_level_election_cover` (replaced by the covered-days definition) and
`guestplan_ext_protection_fee_assessment` (replaced by "The charged days are the election's covered
days, never fewer than the level's minimum charge days"). Two declarations of one supersession is
not a conflict: the two replacements are jointly determinate — covered days are fixed by the first,
and the second sets charged days equal to them under the level's minimum — so the merged semantics
remain unique, `charged_days = MX(covered_days, level_min_charge_days)`. **PASS.**

### rule_compute_equivalence_r2

Re-run in both directions over all five reworked policies, mechanically and by reading.

- **Every compute binding has a `compute_basis` entry and every `compute_basis` entry names a
  binding** — 0 mismatches across the five policies, including the three new bindings
  `cover_load_amount`, `discounted_new_level_cost` and `discounted_fee`.
- **Every `compute_basis` string is a verbatim sentence of its own policy's `rule`** — 0 gaps.
- **Every `baseline.rule` sentence is a verbatim sentence of the full `rule`**, and every
  `baseline.params` key exists in `params` — 0 gaps.
- **Every factor `baseline` key is a real compute binding, and no `decides` is `result`** — 0 gaps.
- **Every ladder tier is stated in the rule.** A strict substring test flags 11 tiers; all 11 are
  the rule writing the second or third tier with an elided subject or a pronoun ("where **it** runs
  for the medium stay days or more but fewer than the long stay days", "where **they** carry a fee
  for exactly the smaller party driver count of additional driver", "where the booking reserves
  **fewer**") while the ladder spells the subject out. The content is present and recoverable from
  the immediately preceding clause in every case. **This is the same wording as round 1** — these
  tiers were read and passed in revision 1 §`factor_ladders`; it is not new and not a regression.
- **No compute invents a basis, and no rule makes an empty promise** — with one new exception
  recorded as **R2-O1** below.

**The three per-hundred scalings that grounded revision 1's F-1 and F-2 are now all stated in
prose**, each with its own named intermediate binding carrying the new sentence as its
`compute_basis`:

| binding | new rule sentence | compute |
| --- | --- | --- |
| `cover_load_amount` | "The cover load is the cover load percentage of the protection already charged, expressed as a percentage of that amount." | `protection_charged_before * cover_load_percent / 100` |
| `discounted_new_level_cost` | "The move discount is the move discount rate of that cost, expressed as a percentage of it." | `new_level_cost * (1 - move_discount_rate / 100)` |
| `discounted_fee` | "The long-stay discount is the stay discount rate of the figure it is taken off, expressed as a percentage of that figure." | `base_fee * loyalty_fee_rate * (1 - stay_discount_rate / 100)` |

A reader who follows the rule alone now reaches the `/100` reading and no other: "expressed as a
percentage of that amount" admits one arithmetic. The alternative reading that revision 1
demonstrated — multiplying by the bare rate — is no longer available from the prose.

### action_binding_and_uuids_r2

Each `(target_tool, computes)` pair still claimed by exactly one policy. The five uuid8s are
**unchanged and still distinct**: `a214c8dd`, `f46febb9`, `f4995b0a`, `63b6fff8`, `513639f7` — no
renaming, no reuse, no sequence, no batch prefix. Tool signatures and bodies are unchanged (bodies
are still bare `ctx.create` / `ctx.update`, no branch, no read, no validation).

**Docstring ordering-word sweep, re-run on the reworked module.**
`declare_additional_driver_a214c8dd`, `confirm_protection_level_63b6fff8` and
`post_protection_fee_513639f7` are now **clean of every cue**. Two residues remain and neither is
of the flagged kind: "read from the protection lines **already** on the election" (a locative — the
lines that are on the election — in both `post_young_driver_surcharge_f46febb9` and
`price_level_change_f4995b0a`), and "the level **first** held" (the policy's own noun phrase for the
original level, used identically in the rule). Neither names another tool nor states a position in
a write sequence. **F-6's two flagged phrases are gone.**

### prerequisite_graph_r2 and prerequisite_sentences_r2

All three edges are **unchanged in every field** — `problem`, `kind`, `gate`, `form`, `condition`,
`policy_source`, `resolved_by`, `effect`. Each `policy_source` is still verbatim in the blocked
policy's own `rule`, now at lines `985`, `1224` and `1682`:

- `young_driver_surcharge` ← `additional_driver_charge`: "The young-driver surcharge on a trip is
  not fixed before the election's charge lines carry the fee due for every additional driver
  declared on it."
- `level_change_difference` ← `young_driver_surcharge`: "The difference due on a move of level is
  worked out only after the protection already charged on the election for the level first held
  stands complete, the young-driver surcharge included."
- `protection_fee_assessment` ← `level_election_cover`: "The protection fee for a trip is fixed only
  once the election has left the quoted state and carries the number of days of cover the level
  will run for."

Graph still two acyclic chains; `form: state` on all three, so no `fallback_reason` required;
`kind: value_input` still matches each `gate`, and each gate is still a real binding of the blocked
policy's compute. The four-point test passes on all three as in revision 1 §`prerequisite_sentences`.

**Ordering-cue sweep re-run on the reworked rules**: the only cross-problem orders stated anywhere
are the three prerequisite sentences above. The narrowed opening sentence of
`guestplan_ext_level_change_difference` introduces no ordering — "moves up to a protection level of
higher rank than the one first held" is a domain restriction, not a sequence. **No undeclared
cross-problem order.** **PASS.**

### override_declarations_r2

Now **eight** declarations across the charter (round 1 had six). Sentence by sentence against each
`base_policy_refs` entry:

| extended policy | base sentence named | round 1 | round 2 |
| --- | --- | --- | --- |
| `..._additional_driver_charge` | "Additional drivers are charged the level's additional driver fee once each for the whole trip…" | declared | declared, unchanged |
| `..._young_driver_surcharge` | "A driver under the young-driver threshold pays the level's protection surcharge on the fee…" | declared | declared, unchanged |
| `..._level_change_difference` | "Where that basis is the remaining whole days, the difference between the two levels' daily fees is charged…" | declared | declared, unchanged |
| `..._level_change_difference` | "A change made once the trip has started carries the level's mid-trip change fee…" | declared | declared, unchanged |
| `..._level_election_cover` | "Charged days are the whole days of the trip as reserved…" | declared | declared, unchanged |
| `..._protection_fee_assessment` | "The fee arrived at is then held between the level's floor and its ceiling…" | declared | declared, unchanged |
| `..._protection_fee_assessment` | "The fee falls due at the level's billing point, whether at booking, at the start of the trip or daily in arrears, and a level billed daily in arrears posts one line for each completed day rather than one line for the trip." | **undeclared — F-3** | **NEW: declared**, replaced by "The protection fee for a trip is charged once against the election that carries the cover, on the level the election stands on and for the days of cover the election carries." |
| `..._protection_fee_assessment` | "Charged days are the whole days of the trip as reserved…" | **undeclared in this policy — F-7** | **NEW: declared**, replaced by "The charged days are the election's covered days, never fewer than the level's minimum charge days." |

**F-5 was addressed by a different route** — not a new `overwrite` entry but a narrowing of the
extended policy's own domain. `guestplan_ext_level_change_difference` now opens "A guest who moves
**up to a protection level of higher rank than the one first held** is charged the difference…",
so the policy no longer reaches a move down, and base `guestplan_level_change`'s sentence "A
downgrade returns the level's downgrade credit percentage of the same difference and never the
whole of it…" (`blueprint/products/guestplan.yaml:554`) governs downgrades unopposed. **This is a
sound route and it closes the conflict**: a conflict removed by narrowing the extended domain needs
no supersession, because the two clauses no longer speak to the same situation. It also brings the
policy into agreement with its own tool, which hardcodes
`charge_basis="level_upgrade_difference"` (`task_tools.py:134`) and has no downgrade path — a
mismatch that stood unremarked in round 1.

**No new undeclared override.** Every remaining divergence of extended from base across the five
policies was re-checked sentence by sentence against `guestplan_evt_fee_charging`,
`guestplan_level_change`, `guestplan_agg_claim_history` and `guestplan_election_eligibility`, and
each is either named in an `overwrite` or is an unopposed elaboration. In particular
`guestplan_agg_claim_history`'s "a guest whose covered days would take one trip past the level's
maximum trip length is quoted on the level that will carry the whole trip rather than on one that
would run out midway" is still inherited in full by no policy's `overwrite`, which is what fixes
task 1's level.

### factor_ladders_r2

Structure re-derived in full. The table in revision 1 §`factor_ladders` still holds with exactly
one cell changed: `cover_load_share` now `decides: cover_load_percent` (was `cover_load_rate`), with
`bindings: [protection_fee_lines_before, protection_refunds_before, protection_charged_before,
cover_load_percent]` and ladder values `K('high_cover_load_percent')` / `K('middle_cover_load_percent')`
/ `K('no_cover_load_percent')` and `baseline: {cover_load_percent: K('no_cover_load_percent')}`. The
rename is consistent across `params`, `rule`, `compute`, `compute_basis`, ladder and baseline — no
dangling `cover_load_rate` survives anywhere in the file.

- counts per computation: **4 / 4 / 6 / 4 / 5**, each with ≥ 2 `parameter` and ≥ 1 `method` — unchanged;
- 23 ladders, 3 tiers each, tiers pairwise disjoint and **distinct in outcome** — the parameter
  values are unchanged (`1.0 / 0.6 / 0.0` now read as percentages, still three distinct outcomes),
  and the method ladders are untouched;
- per task: task 0 still 7 multi-source and 3 `cross_difficulty: trips`; task 1 still 2 and 2;
- every factor `baseline` is still what its policy's `baseline.rule` states for that input, and
  every fall-through tier is still that baseline. The three `baseline.rule` blocks that sit under
  the edited policies were re-checked and **none of the four new sentences was added to a
  `baseline.rule`** — the baselines still describe a computation with no factor applied, and still
  give a definite number.

### findings_r2 (charter-global)

#### R2-O1 — observation, **new**: retiring the billing-point sentence orphans a base parameter

- **Symptom.** `guestplan_ext_protection_fee_assessment.overwrite` now supersedes the base sentence
  "The fee falls due at the level's billing point, whether at booking, at the start of the trip or
  daily in arrears…" That was the only sentence in the whole merged charter that used the billing
  point. After the supersession, base `guestplan_evt_fee_charging.params.per_tier` still binds
  `protection_fee_billing_point: "=protection_fee_billing_point"` for all six levels, and the base
  `parameter_schema` still defines it — a parameter promised by a policy whose only prose about it
  has been retired.
- **Evidence.** `blueprint/products/guestplan.yaml:39` (schema entry: "protection_fee_billing_point: When
  the fee falls due, as one of at_booking, at_trip_start or daily_in_arrears."), `:537-542` (the
  six `per_tier` bindings), `:518` (the superseded sentence);
  `tasks/guest_protection_desk/guestplan.extended.yaml:1576-1581` (the new `overwrite` entry).
- **Why this is an observation and not a red light.** No `compute` in the charter has ever read
  `protection_fee_billing_point`, in round 1 or round 2, so no scored value depends on it and no
  second defensible answer follows on either world. The base section is verbatim and may not be
  rewritten, so the orphaning is an unavoidable side effect of declaring the override — and
  declaring it is what check 1 requires. **This is a strictly better state than round-1 F-3**, which
  left the same sentence standing in opposition to the extended rule; the residue is recorded
  because it is new, not because it is worse.
- **Affected artifact and location.** `guestplan_ext_protection_fee_assessment.overwrite[0]`;
  bears on **task 1**, whose level bills `at_trip_start`.

#### R2-O2 — observation, **carried forward**: the anaphoric tier wording

Eleven ladder tiers state their condition with the subject elided or pronominalised in the `rule`
("where **it** runs for…", "where **they** carry…", "where the booking reserves **fewer**") while
the factor's `when` spells it out. Content is present and recoverable from the preceding clause in
every case. **Unchanged from round 1**, where these tiers were read and passed; recorded here only
because revision 2 re-ran the check mechanically and the residue is worth naming.

#### Round-1 charter-global findings: disposition

| id | round-1 verdict | round-2 finding |
| --- | --- | --- |
| **F-1** | `SOURCE-POLICY RED` | **CLOSED** — the scaling is now stated in the rule and carried by its own binding; see `rule_compute_equivalence_r2`, and the task-0 demonstration in `0.md` §`revision_2` |
| **F-2** | observation (2 instances) | **CLOSED** — both instances now carry the same prose grounding |
| **F-3** | observation | **CLOSED** — declared; leaves R2-O1 |
| **F-4** | observation | **UNCHANGED, and the reasoning holds.** The sentence "…stands complete, the young-driver surcharge included" is still broader than the one write the edge declares. Re-tested on the reworked charter: the trailing apposition still singles the surcharge out, the additional-driver leg is still independently reachable through edge 1's own sentence, and both readings still converge on the one topological order. No second order, no second terminal state. Declining to change it is correct |
| **F-5** | observation | **CLOSED by narrowing** — see `override_declarations_r2`; the route is sound and additionally aligns the policy with its tool's hardcoded `charge_basis` |
| **F-6** | observation | **CLOSED** for both flagged phrases; residue is locative/noun-phrase, not ordering |
| **F-7** | observation | **CLOSED** — declared in the policy's own `overwrite`; the double declaration of one base sentence is jointly determinate, per `policy_conflict_scan_r2` |
| **F-8** | observation | **UNCHANGED, and the reasoning holds.** The `percent_of_trip_price` tier of `fee_basis_by_level` and `new_level_cost_basis` is still unreachable on the six variants. Re-tested: the basis is still named by the base `parameter_schema:36`, the three tiers are still pairwise disjoint and distinct in method, and no condition restates the policy's scope. Nothing on either task's world changes. Declining to change it is correct |
| **F-9** | observation | **UNCHANGED, and the reasoning holds.** The young-driver threshold age is still stated nowhere in this charter. Re-tested: the blocked policy's prerequisite sentence still entails the surcharge is owed, and the guest's `trips` ledger still carries a `young_driver_surcharge` line on the booking in hand, so the entailment stands without the number. Declining to change it is correct |

## closing_checklist_r2

Written **after** both tasks' round-2 reveals, at 2026-09-22T09:52Z. Everything above the
`### findings_r2` heading in this revision is pre-reveal by construction and has not been touched
since the reveal.

**This difficulty now closes out.** Both tasks pass all four relationships.

| Step 4 item | status |
| --- | --- |
| per-task audit files correspond one-to-one with the tasks, `_difficulty.md` alongside | **holds** — `0.md`, `1.md`, `_difficulty.md` |
| old revisions traceable | **holds** — revision 1 is preserved verbatim in all three files; revision 2 is appended below it, and no round-1 blind answer was rewritten to accommodate the reworked artifacts |
| every comparison section carries a PASS | **now holds** — `0.md` §`source_gt_comparison_r2` PASS on all four (was SOURCE-POLICY RED + SOURCE-FACTOR RED); `1.md` §`source_gt_comparison_r2` PASS on all four (unchanged, and re-derived rather than inherited) |
| extended policies fully covered, task scopes pairwise disjoint, each scope spanning the whole tree | **holds** — unchanged by the rework; `{additional_driver, young_driver, level_change}` and `{level_election_cover, protection_fee_assessment}` |
| task tools and GT closed | **holds** — `replay_tasks.py --check` reproduces both terminal states, 0 errors, `match=True` |
| each task tool uses an independently generated, frozen uuid8 | **holds** — `a214c8dd`, `f46febb9`, `f4995b0a`, `63b6fff8`, `513639f7`, **unchanged by the rework** |
| one to three prerequisite problems per task | **holds** — 2 and 1 |
| at least max(n−1, 1) `value_input` edges | **holds** — 2 and 1 |
| at least one problem resolved by an `owner=user` tool | **holds** — `declare_additional_driver_a214c8dd` (task 0), `confirm_protection_level_63b6fff8` (task 1) |
| no cycle; the difficulty's edges together a DAG | **holds** — two disjoint chains, all three edges unchanged in every field |
| every computation declares a self-sufficient baseline | **holds** — 20.00, 150.00, 432.00, 30, 1200.00, each definite and each different from gold; none of the four new rule sentences was added to a `baseline.rule` |
| 4–6 factors per computation, 2 `parameter` and 1 `method` | **holds** — 4 / 4 / 6 / 4 / 5 |
| per task ≥ 1 multi-source and ≥ 1 cross-difficulty | **holds** — task 0: 7 and 3; task 1: 2 and 2 |
| every ladder ≥ 3 tiers stated in full in its rule, tiers distinct in outcome, conditions and outcomes ones the business holds | **holds** — 23 ladders × 3 tiers; the `1.0 / 0.6 / 0.0` cover-load outcomes now read as percentages and remain three distinct outcomes; residue R2-O2 is anaphoric wording, pre-existing |
| every factor proved to bear weight against an honest baseline | **now holds without qualification** — all 23 factors move their scored value under their own baseline, **and every submitted proof of this now matches the recomputation**: all 23 `factor_trace` "would have given" figures were re-checked against `factor_sensitivity` and against an independent recomputation, and all 23 agree. Revision 1's single false figure (39.00 for 38.60) is corrected in both of its locations |
| the baseline alone gives a definite number different from gold | **holds** — 20.00 ≠ 36.50, 150.00 ≠ 296.40, 432.00 ≠ 211.12, 30 ≠ 81, 1200.00 ≠ 3272.03 |
| instantiation-stage gates re-run once on the final form | **done** — see below |

### Instantiation-stage gates, re-run on the reworked final form

```
DIFF=env/env_0015_car_sharing_marketplace/tasks/guest_protection_desk
check_extended.py    $DIFF          -> EXTENDED OK
check_task_tools.py  $DIFF          -> TASK TOOL CONTRACT OK
check_solvability.py $DIFF          -> SOLVABILITY OK
check_compute.py     $DIFF          -> COMPUTE OK
check_grounding.py   $DIFF          -> GROUNDING OK
check_cross_fire.py  $DIFF          -> SCOPE OK
replay_tasks.py      $DIFF --check  -> REPLAY OK
```

All seven green, matching the coordinator's entry snapshot. As in round 1 they are the
qualification, not the proof: no script checks whether a rule's prose and its `compute` agree on a
scaling convention, and none recomputes the figures a `factor_trace` asserts — which is why both
round-1 red lights were invisible to them and why closing them had to be verified by hand here.

### Artifacts unchanged by this audit

`guestplan.extended.yaml` `578bb1a8bbd48c29` and `task_tools.py` `97f057796ce850bd` after the gate
re-run — identical to the values frozen in §`charter_global_frozen_r2`; `tasks/0.json`
`339928690b464b50` and `tasks/1.json` `63aed43d8c91c322`; masked views `858e4c67ec7ebf24` and
`ff4ecf45949506ec`. Nothing under `blueprint/`, `tasks/` or `erlbench/` was edited by this audit;
its only writes are the three files in this directory. The `__pycache__` directories the gate runs
leave under `env/` were removed afterwards.

### Round-2 verdict for the difficulty

| task | policy self-consistency | problem tree | factors bear weight | unique solution | round 1 | round 2 |
| --- | --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | RED | **PASS** |
| 1 | PASS | PASS | PASS | PASS | PASS | **PASS** |

"Policy self-consistency PASS + problem tree holds PASS + factors bear weight PASS + unique
solution PASS" now holds together for both tasks. **This difficulty passes the source-layer audit
at revision 2.**

### Round-1 item register — closed or not

| id | round-1 verdict | round-2 disposition | closed? |
| --- | --- | --- | --- |
| **F-1 / T0-F1** | `SOURCE-POLICY RED` | rule sentence added, params renamed `…_percent`, scaling moved into the named binding `cover_load_amount` with that sentence as its `compute_basis`; rename complete with no `cover_load_rate` surviving; **arithmetic verified unmoved** (36.50 / 296.40 / 211.12 and all 14 sensitivities reproduce round 1) | **YES** |
| **T0-F2** | `SOURCE-FACTOR RED` | 39.00 → 38.60 in both `computations[0].factor_trace[0]` and the `design_rationale` FACTOR CARD; agrees with `factor_sensitivity` and with independent recomputation; factor itself untouched and still bearing weight | **YES** |
| **F-2** | observation ×2 | both instances grounded by a new rule sentence and a named binding (`discounted_new_level_cost`, `discounted_fee`); arithmetic unmoved | **YES** |
| **F-3** | observation | declared in `guestplan_ext_protection_fee_assessment.overwrite` | **YES** — leaves R2-O1 / R2-O4 |
| **F-4** | observation | no change; reasoning re-tested on the reworked charter and holds — both readings still converge on one order and one terminal state | **correctly left open** |
| **F-5** | observation | closed by narrowing the extended policy's domain to a move up, so base's downgrade sentence governs downgrades unopposed; additionally aligns the policy with its tool's hardcoded `charge_basis` | **YES** |
| **F-6** | observation | all three flagged phrases reworded; residue is locative/noun-phrase, not ordering | **YES** |
| **F-7** | observation | declared in the policy's own `overwrite`; double declaration of one base sentence is jointly determinate | **YES** |
| **F-8** | observation | no change; reasoning re-tested and holds — the basis is published by the base `parameter_schema`, the tiers stay disjoint and distinct, removing it would breach the three-tier floor | **correctly left open** |
| **F-9** | observation | no change; reasoning re-tested and holds — base is frozen and carries no age threshold, and the entailment stands without the number | **correctly left open** |
| **T0-O1** | observation | tool arg re-described as "the seat days the extra driver's fee was measured across", naming one binding | **YES** |
| **T0-O2** | observation | "two steps earlier" → "the first write of this task's tree" | **YES** — leaves R2-O3 |
| **T1-O1** | observation | no change; reasoning re-tested on the byte-identical world and holds | **correctly left open** |
| **T1-O2** | observation | no change; reasoning re-tested and holds, and the reworker's added point (task 0 does discriminate the rounding point) is verified | **correctly left open** |

**New in revision 2, all observations, none a red light**: **R2-O1** (the retired billing-point
sentence orphans the base `protection_fee_billing_point` parameter), **R2-O2** (anaphoric tier
wording, pre-existing and carried forward), **R2-O3** (a sibling of T0-O2's phrase left behind in
`computations[1].factor_trace[0]`), **R2-O4** (three proof-field sentences in `tasks/1.json` still
lean on the clause R2-O1 retired). **No regression was found in either task**, and in particular
task 1 — which was PASS in round 1 and which the rework touched in three places — was re-derived
from the reworked charter and matches value for value.

---

# revision_3

Round 3 re-audit. **Revisions 1 and 2 above are preserved unaltered.**

This difficulty passed at revision 2. Its KB was then rendered, and a render-layer auditor failed
it; one of that audit's findings traced to the **source**, which is why it returns here. The finding
and the reworker's response are set out and independently tested below.

## charter_global_frozen_r3

| item | round 2 | round 3 |
| --- | --- | --- |
| `guestplan.extended.yaml` sha256:16 | `578bb1a8bbd48c29` | **`9380b435776e459a` — CHANGED** |
| `task_tools.py` sha256:16 | `97f057796ce850bd` | **`2544581697fbcf78` — CHANGED** |
| masked `0.json` / `1.json` sha256:16 | `858e4c67ec7ebf24` / `ff4ecf45949506ec` | identical — **byte-identical worlds**, re-verified |
| `tasks/0.json` / `tasks/1.json` sha256:16 | `339928690b464b50` / `63aed43d8c91c322` | `f0f35c2924107809` / `bad81edee5a59f70` (both moved) |
| freeze time (UTC) | 2026-09-22T09:31:10Z | 2026-09-22T12:35:37Z |

**Both charter-level hashes moved, so every charter-global section is re-derived in full.** Nothing
was carried forward: three of five scored values moved, so revision 2's figures were treated as
void and every quantity was re-derived from the reworked charter.

**contamination_disclosure (round 3).** As in round 2, prior GT is in this auditor's context, so
round 3 is **not blind in the round-1 sense and is not offered as such**. What makes it independent
evidence is stronger than in round 2: rather than re-running the shipped evaluator, this round
**re-implemented the evaluator from scratch over exact rationals** and derived every figure from the
reworked charter's own `compute` blocks against the unchanged masked worlds. Revisions 1 and 2 stand
unedited.

### The oracle used, and why it is built this way

`Fraction`, never `Decimal` and never a binary float, on the coordinator's instruction and for a
reason this round can now confirm: `Decimal //` truncates where the evaluator floors, which would
silently change a count, and a float oracle would reproduce the very representation error under
test.

- Every numeric literal enters as `Fraction` built **from its decimal text** — YAML floats through a
  custom `SafeLoader` constructor, JSON through `parse_float=Fraction`. No binary double exists
  anywhere in the oracle, so no representation error can exist.
- `int()` is reimplemented as truncation toward zero, matching the evaluator (for the non-negative
  quantities in this charter that is floor, which is what `Decimal //` would have broken).
- `MONTHS`, `DAYS` are exact integer date arithmetic; `SUM`/`XSUM`/`COUNT`/`XCOUNT`/`LATEST`/`CFIELD`
  mirror `check_compute.build_env` including its holding-key scoping, its `0 <= MONTHS(d, NOW) <
  within_months` window and its cross-category ownership test.
- `RND` is **exact half-up at two decimal places**, and every call records its exact rational
  argument together with a flag for whether that argument is an exact half-cent. The `round(s, 2)`
  inside `SUM`/`XSUM` is instrumented the same way, so aggregation is swept as well as the final
  rounding.

### what changed in the charter, enumerated

Two parameter values, and prose in four of five policies plus the tool module:

| # | location | edit |
| --- | --- | --- |
| 1 | `guestplan_ext_young_driver_surcharge.params` | `watched_record_surcharge_percent: 17.0` → **`17.5`** |
| 2 | `guestplan_ext_protection_fee_assessment.params` | `returning_fee_rate: 0.95` → **`0.94`** |
| 3 | all five policies' prose | every rounding phrase now reads "rounded **half up to the cent**" — **except one sentence**, see **R3-F1** |
| 4 | `task_tools.py` | all four money-carrying arguments now read "in USD to 2 decimal places, **rounded half up to the cent** and never rounded anywhere but at the end"; `confirm_protection_level_63b6fff8` correctly carries no mode, taking a whole day count |
| 5 | `guestplan_ext_young_driver_surcharge` (**N1**) | `surcharge_ceiling_by_cover_length`'s ladder and `compute_basis[charged_days_total]` changed from "the election's charge lines carry protection for…" to "**the protection fee lines standing on the election** carry protection for…", matching `SUM('guestplan_charges', 'days_covered', charge_basis='daily_protection_fee')` |
| 6 | `guestplan_ext_protection_fee_assessment` (**B3**, source side) | `loyalty_fee_rate`'s sentence gains "…**taken on the fee the level's basis produces for the charged days and taken before that fee is held at the level's floor or under the trip ceiling**"; `discounted_fee`'s gains "…**and it is taken off after the loyalty rate has been applied and before the fee is held at the level's floor or under the trip ceiling**" |

Not changed: any other parameter, every factor id / effect / `decides` / `bindings` / ladder shape /
`baseline`, all three prerequisite edges in every field, all five `target_tool`s, all five uuid8s
(`a214c8dd`, `f46febb9`, `f4995b0a`, `63b6fff8`, `513639f7`), every tool signature and body, the
eight `overwrite` declarations, and the narrowed opening sentence of
`guestplan_ext_level_change_difference`. Base section verbatim (`718d717` only).

### Both ladders keep three distinct outcomes after the parameter moves

| ladder | tiers, round 2 | tiers, round 3 | distinct? | business reading |
| --- | --- | --- | --- | --- |
| `surcharge_percent_by_driving_record` | 14.0 / 17.0 / level's own (22 on Standard) | 14.0 / **17.5** / level's own | **yes** | clean record cheapest, watched record dearer, a record carrying a late return dearest — ordering preserved |
| `loyalty_rate_by_trip_record` | 0.90 / 0.95 / 1.00 | 0.90 / **0.94** / 1.00 | **yes** | established guest cheapest, returning guest next, no-record guest full price — ordering preserved |

Neither move collapses a tier onto another, and neither changes which tier either task's customer
sits on. The fall-through of each is still the baseline.

### the_tie_sweep

This is the substance of the round. The question applied across the charter, not only to the four
ties reported: **for every scored value, every whole baseline and every `factor_sensitivity` figure,
does the arithmetic producing it pass through an exact half-cent, and do the stated mode and the
evaluator agree there?**

The sweep covers all **33** published figures — 5 scored values, 5 whole baselines, 23 factor
sensitivities — under **both** parameter generations, computing each twice: once with the exact
oracle (half-up on exact rationals) and once with the shipped float evaluator
(`check_compute.build_env` / `eval_compute`). Every `RND` **and** every `SUM`/`XSUM` aggregation is
instrumented for tie-ness.

**Round-2 generation (`watched 17.0`, `returning 0.95`) — four exact half-cent quantities, and
they are exactly the four reported:**

| # | figure | rounding point | nearest double | float evaluator | exact half-up | outcome |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | task 0, `young_driver_surcharge`, **scored** | `RND(296.405)` | **below** (296.404999999999972715…) | 296.40 | **296.41** | **DIVERGED** — the reported defect |
| 2 | task 0, `young_driver_surcharge`, **sensitivity** `trip_length_step` | `RND(271.405)` | **below** (271.404999999999972715…) | 271.40 | **271.41** | **DIVERGED** — a sensitivity figure, which no runtime audit reaches |
| 3 | task 1, `protection_fee_assessment`, **scored** | `RND(3272.025)` | **above** (3272.025000000000090949…) | 3272.03 | 3272.03 | **agreed — by representation only** |
| 4 | task 1, `protection_fee_assessment`, **sensitivity** `mileage_exposure_step` | `RND(3182.025)` | **above** (3182.025000000000090949…) | 3182.03 | 3182.03 | **agreed — by representation only** |

**The reworker's tie report is confirmed in every particular**: four exact half-cents, in **both**
tasks, two diverging and two agreeing by representation alone, and one of the agreeing pair under a
**scored** value of task 1.

Two further facts this sweep establishes, neither of which was in the brief:

- **The single diverging scored tie contaminated eight of task 0's fourteen figures.** Because
  296.405 feeds `protection_charged` in the downstream problem, under exact half-up the round-2
  charter yields task 0's difference as **211.11**, not the published 211.12, and five of its six
  sensitivities likewise shift by a cent (173.09, 380.45, 191.11, 156.11, 181.11). A single tie was
  not a single wrong figure; it was a wrong figure plus a seven-figure cascade.
- **`Decimal` would have been the wrong oracle** and `Fraction` the right one, as instructed:
  the charter's `int((days_still_to_run + 6) / 7)` and `int((reserved_hours + 23) / 24)` are floors
  over non-integers, and `Decimal //` truncates — on this charter it happens to agree, but the
  agreement is accidental and the sibling auditor's caution is sound.

**Round-3 generation — zero ties and zero divergences across all 33 figures.** Every rounding point
in both tasks, scored, baseline and sensitivity, sits strictly off the half-cent, and the exact
oracle and the float evaluator return the identical value at every one. **The reworker's claim of
33/33 with 0 ties and 0 divergences is verified by an independent implementation.**

### was task 1's revision-2 pass luck rather than entailment?

**Yes, and this auditor's own revision-1 and revision-2 passes of task 1 are implicated.** Task 1's
scored fee at revision 2 was 3272.03, reached through `RND(3272.025)` — an exact tie. The published
figure matched a half-up reading only because the nearest double to 3272.025 happens to lie above
it. Had the representation fallen the other way — as it did for 296.405 at the identically-shaped
rounding point in task 0 — the evaluator would have scored 3272.02 while every stated reading of the
policy gives 3272.03, and task 1 would have failed on the same ground task 0 did.

Revision 1 §`factor_weight` and revision 2 §`factor_weight_r2` both reproduced 3272.03 and recorded
it as agreeing with GT. Both were right about the figure and **wrong about what established it**:
the agreement came from the binary representation, not from anything the policy says. Revision 1 in
fact recorded the near miss without recognising it — T1-O2 noted that "a reader who rounds early …
still lands on 3,272.03" and treated the coincidence as harmless. That was the tie, seen and not
named. **A pass that rests on a representation coincidence is not an entailment, and this audit
should have caught it in round 1.** It is recorded here against this audit's own earlier revisions,
not only against the artifacts.

The general lesson, which is why the tie sweep is now part of this audit rather than a one-off: an
agreeing tie is invisible to every comparison an auditor runs, because both sides produce the same
number. It is detectable only by asking whether the exact arithmetic lands on a half-cent at all —
which is a question about the computation, not about its output, and must be asked of every figure
including the ones that match.

### rule_compute_equivalence_r3

Re-run in both directions over all five reworked policies.

- every compute binding has a `compute_basis` entry and every entry names a binding — **0 gaps**;
- every `baseline.rule` sentence is verbatim in its own `rule`; every `baseline.params` key exists;
  every factor `baseline` key is a real binding; no `decides` is `result` — **0 gaps**;
- no ladder has two tiers selecting the same value or method — **0 collisions**, including the two
  ladders whose parameters moved;
- **every `compute_basis` entry is a verbatim sentence of its own `rule` — with three exceptions in
  one policy**, recorded as **R3-F1** below. Two are a real new break; the third is the
  pre-existing capitalisation artifact (`days_left_share`), which matches case-insensitively and was
  already noted at revision 2 as R2-O2's neighbour;
- the anaphoric tier wording (**R2-O2**) is unchanged and still present on the same eleven tiers,
  pre-existing and not a regression.

### N1 — closed

`surcharge_ceiling_by_cover_length` said "the election's charge lines carry protection for…" while
its binding is `charged_days_total = SUM('guestplan_charges', 'days_covered',
charge_basis='daily_protection_fee')` — the election's charge lines include additional-driver,
surcharge, deductible and refund lines, which the sum does not read. Both the ladder's three `when`
clauses and `compute_basis[charged_days_total]` now read "**the protection fee lines standing on the
election**", which is exactly the filtered set. Prose and compute now describe the same rows.
**Genuinely closed** — and it is the same defect class as the cover-load scaling closed at revision
2: a rule saying something the compute does not do.

### B3, source side — closed

The two factors of `guestplan_ext_protection_fee_assessment` whose position in the composition was
unstated now each carry it, and both conditions the finding imposed hold:

| factor | sentence now carrying its position | claimed by its own binding | in `baseline.rule`? |
| --- | --- | --- | --- |
| `loyalty_rate_by_trip_record` | "The loyalty rate is the share of that fee a guest with a record on the marketplace is asked for, **taken on the fee the level's basis produces for the charged days and taken before that fee is held at the level's floor or under the trip ceiling**." | `compute_basis[loyalty_fee_rate]` | **no** |
| `long_stay_discount` | "The long-stay discount is the stay discount rate of the figure it is taken off, expressed as a percentage of that figure, **and it is taken off after the loyalty rate has been applied and before the fee is held at the level's floor or under the trip ceiling**." | `compute_basis[discounted_fee]` | **no** |

Checked across the whole charter: **all 23 factors** have their deciding sentence verbatim in their
own `rule`, each claimed by its own binding in `compute_basis`, and **none** of the 23 appears in
its policy's `baseline.rule` — so no factor leaks into the standard method. The document-side
repair is the renderer's and is out of scope here.

### the rounding mode, as now stated

"Rounded half up to the cent" appears in the `rule` and the `baseline.rule` of
`guestplan_ext_additional_driver_charge`, `guestplan_ext_young_driver_surcharge` and
`guestplan_ext_protection_fee_assessment`, and in the closing `result` sentence of
`guestplan_ext_level_change_difference`. `guestplan_ext_level_election_cover` correctly carries no
mode: its `result` is `MN(plan_days + handover_grace + late_return_cover, cover_ceiling)` over
integers, with no `RND` and nothing to round. All four money-carrying tool arguments state the mode.
**The one gap is R3-F1.**

### findings_r3 (charter-global)

#### R3-F1 — observation, **new and significant**: one policy's rounding sentence was not updated, and two `compute_basis` entries now quote a sentence its `rule` does not contain

- **Symptom.** `guestplan_ext_level_change_difference` is the one policy of five whose rounding
  phrase was **not** brought to the stated mode. Its `rule` and its `baseline.rule` both still read
  "…and the whole is rounded **to two decimal places** only once it has been worked out", while
  `compute_basis[old_level_daily]` and `compute_basis[new_level_daily]` quote that same sentence
  **as if it read** "…and the whole is rounded **half up to the cent** only once it has been worked
  out". The quotation does not exist in the rule it claims to quote.
- **Root cause.** The mode was propagated into the `compute_basis` quotations of this policy but not
  into the `rule` sentence and `baseline.rule` sentence they quote — the one place in the sweep
  where the two faces were updated separately.
- **Evidence.**
  - `guestplan.extended.yaml:1176-1178` (`rule`): "The difference due on a move of level is the
    level moved to at its daily amount for the days still to run, less a credit at the daily amount
    of the level first held for those same days, and the whole is rounded **to two decimal places**
    only once it has been worked out."
  - `guestplan.extended.yaml:1396-1398` (`baseline.rule`): the same sentence, same wording.
  - `compute_basis[old_level_daily]` and `compute_basis[new_level_daily]`: "…and the whole is
    rounded **half up to the cent** only once it has been worked out." Neither string occurs in the
    policy's `rule`, case-sensitively or case-insensitively.
  - By contrast the other four policies carry the mode in `rule` and `baseline.rule` alike, and this
    policy's own closing `result` sentence does say "rounded half up to the cent at the end"
    (`:1216`).
- **Why this is an observation and not a red light.** The consequence test is whether the two
  passages reach different conclusions in the same situation. "Two decimal places" and "half up to
  the cent" differ **only on a tie**, and the round-3 sweep proves there is no tie anywhere in this
  charter; where this policy's figures do need rounding (the scored 206.322 → 206.32) every mode and
  even truncation agree, and its whole baseline (432.00) and the figures it feeds are exact. No
  second defensible number follows on either task's world, so the threshold for `SOURCE-POLICY RED`
  is not met.
- **Why it is nonetheless significant, and reported as such.** (i) It is a **verbatim break in
  `compute_basis`**, which check 2 requires absolutely and which `check_compute` passed over — the
  gates do not test it. (ii) It leaves the mode unstated in a **`baseline.rule`**, which is exactly
  the surface a computation document renders as the standard method and exactly the surface whose
  silence brought this difficulty back from the render audit. (iii) It contradicts the reworker's
  own claim that "every rounding phrase in all five policies" now reads the mode — four of five do.
  A defect that costs nothing on today's world but sits in the class the round was convened to
  eliminate should not be closed out silently.
- **Affected artifact and location.** `tasks/guest_protection_desk/guestplan.extended.yaml`,
  `guestplan_ext_level_change_difference`: `rule` (`:1176-1178`), `baseline.rule` (`:1396-1398`),
  `compute_basis[old_level_daily]`, `compute_basis[new_level_daily]`. Bears on **task 0**.
- **Relation to previous revisions.** New in revision 3, created by this round's fix.

#### R3-O1 — observation, **new**: "exact to the cent" is claimed more widely than it holds

The rework's account is that moving the two parameters makes "the arithmetic land exact to the
cent". That is true of task 1's fee — `3806.25 × 0.94 = 3577.875`, `× 0.88 = 3148.53` exactly, so
the scored 3238.53 needs no rounding at all — but it is **not** true of task 0's surcharge:
`1596.50 × 17.5% = 279.3875`, and `+ 25.00 = 304.3875` still requires a rounding decision to reach
304.39. What the fix actually achieves, and what soundness requires, is the weaker and sufficient
property that **no rounding point lands on a tie**. Recorded because the stronger claim, if carried
into a sibling difficulty as the design rule, would be unattainable in general, whereas the
no-tie rule is both attainable and sufficient. No consequence on either world: 304.3875 is not a
tie, and the mode that resolves it is stated in this policy's `rule`, `baseline.rule` and tool
contract.

#### Round-2 items: disposition

| id | round-2 verdict | round-3 finding |
| --- | --- | --- |
| **R2-O1** | observation (retired billing-point sentence orphans a base parameter) | **unchanged**; re-tested and still without consequence — no compute reads `protection_fee_billing_point` |
| **R2-O2** | observation (anaphoric tier wording, 11 tiers) | **unchanged**, pre-existing, still no consequence |
| **R2-O3** | observation (a "preceding step" phrase in `computations[1].factor_trace[0]`) | see `0.md` §`findings_r3` |
| **R2-O4** | observation (three proof sentences leaning on the retired clause) | see `1.md` §`findings_r3` |
| **F-4, F-8, F-9** | correctly left open | re-tested on the reworked charter; all three reasons still hold |

## closing_checklist_r3

Written **after** both tasks' round-3 reveals, at 2026-09-22T12:41Z. Everything above
`### findings_r3` in this revision is pre-reveal by construction and untouched since the reveal.

**This difficulty closes out at revision 3.** Both tasks pass all four relationships, and — unlike
revision 2 — both now pass for reasons that do not depend on a binary representation.

| Step 4 item | status |
| --- | --- |
| per-task files one-to-one with the tasks, `_difficulty.md` alongside | **holds** |
| old revisions traceable | **holds** — revisions 1 and 2 preserved verbatim in all three files; revision 3 appended below them; no earlier derivation rewritten to accommodate the reworked artifacts. Where an earlier revision's *conclusion* is corrected (task 1's pass, T1-O2) the correction is recorded in revision 3 and the earlier text is left standing |
| every comparison section carries a PASS | **holds** — `0.md` and `1.md` §`source_gt_comparison_r3`, all four each |
| policies fully covered, scopes pairwise disjoint, each spanning its whole tree | **holds** — unchanged |
| task tools and GT closed | **holds** — `replay_tasks.py --check` reproduces both terminal states, 0 errors, `match=True`, on the moved figures |
| independently generated, frozen uuid8 per tool | **holds** — `a214c8dd`, `f46febb9`, `f4995b0a`, `63b6fff8`, `513639f7`, unchanged across all three rounds |
| 1–3 prerequisite problems; ≥ max(n−1,1) `value_input` edges; ≥ 1 `owner=user` write; acyclic | **holds** — 2 and 1 problems, 2 and 1 `value_input` edges, `declare_additional_driver_a214c8dd` and `confirm_protection_level_63b6fff8`, two disjoint chains |
| self-sufficient baseline per computation, definite and ≠ gold | **holds** — 20.00 ≠ 36.50, 150.00 ≠ 304.39, 432.00 ≠ 206.32, 30 ≠ 81, 1200.00 ≠ 3238.53 |
| 4–6 factors, 2 `parameter` + 1 `method` each; per task ≥ 1 multi-source and ≥ 1 cross-difficulty | **holds** — 4/4/6/4/5; task 0: 7 and 3, task 1: 2 and 2 |
| ladders ≥ 3 tiers, stated in the rule, distinct in outcome, conditions and outcomes ones the business holds | **holds** — 23 ladders × 3 tiers, 0 outcome collisions; the two moved parameters keep their ladders' ordering and distinctness (14.0/17.5/22 and 0.90/0.94/1.00) |
| every factor bears weight against an honest baseline, and every submitted proof matches recomputation | **holds** — all 23 factors move their scored value; all 23 `factor_trace` figures agree with `factor_sensitivity` and with the exact oracle |
| **no scored quantity, baseline or sensitivity is a tie** *(new at this revision)* | **holds** — 0 of 33 figures reach a rounding point on an exact half-cent, in either task, and the exact oracle and the float evaluator agree at every rounding point |
| instantiation-stage gates re-run on the final form | **done** — see below |

### Gates, re-run on the reworked final form

```
check_extended.py    -> EXTENDED OK        check_grounding.py  -> GROUNDING OK
check_task_tools.py  -> TASK TOOL CONTRACT OK   check_cross_fire.py -> SCOPE OK
check_solvability.py -> SOLVABILITY OK     replay_tasks.py --check -> REPLAY OK
check_compute.py     -> COMPUTE OK
```

Seven green, matching the coordinator's entry snapshot. `check_traceability.py` — the eighth in that
snapshot — reads the published KB under `docs/`, which is outside this audit's read domain; this
auditor did not read `docs/` and cites the coordinator's green result rather than re-running it.

**What the gates still cannot see, now demonstrated three rounds running.** They cannot see a rule
whose prose and `compute` disagree on a scaling (revision 1, F-1); they cannot recompute a figure a
`factor_trace` asserts (revision 1, T0-F2); they cannot see that a `compute_basis` entry quotes a
sentence its `rule` does not contain (revision 3, R3-F1); and — the finding of this round — **they
cannot see a tie at all**, because the evaluator that produces the gold value is the same evaluator
they check it against. A tie is invisible to every comparison run in float, including an auditor's,
which is why this revision's oracle is exact-rational and why the sweep asks about the computation
rather than about its output.

### Artifacts unchanged by this audit

`guestplan.extended.yaml` `9380b435776e459a`, `task_tools.py` `2544581697fbcf78`,
`tasks/0.json` `f0f35c2924107809`, `tasks/1.json` `bad81edee5a59f70`, masked views
`858e4c67ec7ebf24` / `ff4ecf45949506ec` — all identical after the gate re-run to the values frozen
in §`charter_global_frozen_r3`. Nothing under `blueprint/`, `tasks/`, `docs/` or `erlbench/` was
read-for-modification or edited; `docs/` was not read at all. The audit's only writes are the three
files in this directory. `__pycache__` left by the gate runs was swept from this scenario only.

### Round-3 verdict for the difficulty

| task | policy self-consistency | problem tree | factors bear weight | unique solution | r1 | r2 | r3 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | RED | PASS | **PASS** |
| 1 | PASS | PASS | PASS | PASS | PASS | PASS\* | **PASS** |

\* Revision 2's pass of task 1 was correct in its figures but rested on a tie resolved by binary
representation rather than by any published sentence — see `1.md` §`findings_r3`. It is recorded
here as a qualified pass in hindsight, and the qualification is this audit's own, not the
reworker's.

**This difficulty passes the source-layer audit at revision 3**, with one new observation (**R3-F1**)
that costs neither task a defensible answer today and is reported rather than closed out.

### Round-3 item register

| id | claim | verdict |
| --- | --- | --- |
| **R1** (the tie) | CLOSED by removing the ties and then stating the mode; 33/33, 0 ties, 0 divergences | **GENUINELY CLOSED.** Independently reproduced with an exact-rational oracle: 33 of 33 agree, 0 ties, 0 divergences. Both halves present — the ties are gone *and* the mode is stated, which matters because a non-tie still needs a mode to exclude truncation |
| **the tie sweep** | four exact half-cents before this round, in both tasks; two diverged, two agreed by representation; one of the agreeing pair under task 1's scored value | **CONFIRMED in every particular**, and extended: the single diverging scored tie cascaded into eight of task 0's fourteen figures. **Complete** — the sweep here covers all 33 published figures under both generations, instrumenting every `RND` and every `SUM`/`XSUM` aggregation |
| **task 1's pass was luck** | claimed | **CONFIRMED, against this audit's own record.** Revisions 1 and 2 passed task 1 on a figure no published sentence entailed, and revision 1's T1-O2 reported the coincidence without recognising it |
| **three scored values moved** | with every dependent figure propagated | **CORRECT AND UNIQUELY ENTAILED.** 296.40 → **304.39**, 211.12 → **206.32**, 3272.03 → **3238.53**; each derived independently before the reveal, each matching GT; tiers taken, trees, owners, personas, seeds, read nodes and whole baselines unchanged, and every dependent figure — sensitivities, closures, business effects, tracings, traces — propagated correctly |
| **N1** | closed | **CLOSED** — ladder and `compute_basis` now read "the protection fee lines standing on the election", matching the `charge_basis='daily_protection_fee'` filter |
| **B3 source side** | addressed | **CLOSED** — both factors now state their position, each claimed by its own binding, neither in `baseline.rule`; verified for all 23 factors charter-wide |
| **B1, B2** | render defects, out of the reworker's write domain | **not in this audit's scope**; `docs/` was not read |
| — | — | **R3-F1 new**: one policy's `rule` and `baseline.rule` keep an unmoded rounding sentence that two of its `compute_basis` entries quote as moded. Observation: no tie exists for the modes to disagree on, so no second defensible number follows |
| — | — | **R3-O1 new**: "the arithmetic lands exact to the cent" holds for task 1's fee but not task 0's surcharge (304.3875). The property the fix actually achieves, and the one to propagate to sibling difficulties, is **no rounding point is a tie** — weaker, sufficient, and attainable in general |
