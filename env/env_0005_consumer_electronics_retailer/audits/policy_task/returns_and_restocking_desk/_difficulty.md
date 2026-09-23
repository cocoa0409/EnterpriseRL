# Policy-task audit — returns_and_restocking_desk / charter-global

## charter_global_frozen

- freeze time: 2026-09-18T09:12Z (written before any task's GT was revealed)
- auditor: independent source-layer auditor (not the instantiating agent)
- freeze hashes (sha256, first 16):
  - `env/env_0005_consumer_electronics_retailer/tasks/returns_and_restocking_desk/returns.extended.yaml` = `c0c05a50a6d836a5`
  - `env/env_0005_consumer_electronics_retailer/tasks/returns_and_restocking_desk/task_tools.py` = `7a0140a9b4173cc6`
  - masked view `0.json` = `d9511150a100d5f1`; masked view `1.json` = `02e724ca1216ca51` (both as reported in the brief)
- fields permitted while this file was written: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`,
  `blueprint/share_tools.py`, `blueprint/products/returns.yaml` (and the `orders` / `membership` product
  charters only for the tier parameters the extended policies' `cross_category` blocks declare),
  the whole of `returns.extended.yaml`, the whole of `task_tools.py`, and each task's
  `frozen_time` / `user_scenario` / `initial_state` through the masked copies only.
- fields explicitly masked and not read while this file was written: `evaluation_criteria`,
  `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`,
  `prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state`.
- entry conditions: the brief carried the instantiation-stage gate snapshot with the actual output
  lines of `check_extended`, `check_task_tools`, `replay_tasks`, `check_solvability`, `check_compute`,
  `check_grounding` and `check_cross_fire`, all green; `check_traceability` is deferred to the render
  step by design and was not run. The masked views were built mechanically by the caller with the
  allowlist `{frozen_time, user_scenario, initial_state}` and their hashes were supplied. Entry
  conditions are therefore **complete**. A machine green light is the qualification to enter this
  audit, not a proof of correctness.

### policy_conflict_scan

The structured policy in force for category `returns` on this desk is the twelve base policies of
`blueprint/products/returns.yaml` plus the five `extended_policies` of `returns.extended.yaml`.

- **Base copy is verbatim.** Every top-level section of the extended file (`category`,
  `display_name`, `binding`, `lifecycle`, `accounts`, `parameter_schema`, `variants`, `events`,
  `measures`, `policies`) hashes identically to the blueprint's product file. No base sentence has
  been rewritten.
- **Subjects.** The five extended subjects are `returns_shipping_label_issue` (twice),
  `returns_restocking_fee_charge`, `returns_restocking_fee_waive`, `returns_exchange_issue`. The two
  policies sharing `returns_shipping_label_issue` compute different quantities
  (`booking_open_days` vs `pickup_notice_days`) against different target tools and do not overlap.
- **Triggers.** `on_request` for `returns_ext_collection_booking_window`,
  `returns_ext_collection_slot_notice`, `returns_ext_exchange_difference`; `state_due` for
  `returns_ext_restocking_fee_charge`, `returns_ext_member_fee_relief`. No trigger contradicts the
  base state gate it inherits.
- **Eligibility / state gates.** Inherited unchanged: `authorizable_rma_state` (requested or
  authorized) for the two logistics policies, `feeable_rma_state` (inspected or settled) for the two
  fee policies, `settleable_rma_state` (inspected or settled) for the exchange policy. No extended
  rule weakens any of these.
- **Time anchors.** One genuine cross-policy tension, recorded as finding **O-6**: the phrase
  "the item was held longer than the long hold multiple of the schedule's return window" appears in
  both `returns_ext_restocking_fee_charge` and `returns_ext_exchange_difference` with the same
  multiple (2) and the same window, but each policy anchors the span differently.
- **Action parameters.** `(target_tool, computes)` pairs are pairwise distinct — see
  `action_binding_and_uuids`.
- **Terminal states.** One tension, recorded as **O-5**: `returns_ext_exchange_difference` keeps the
  standing restocking fee back out of the exchange difference, but no write of this difficulty
  relieves `return_authorizations.restocking_fee_outstanding` for the amount withheld, so the
  receivable survives collection.
- **Cross-category read boundaries.** `orders` and `membership` only, declared per policy with
  `as:`, the field list and a `note`; `protection`, `tradein`, `service` and `credit` are never read.
  All declared reads resolve to real columns/tier parameters (`purchase_orders.variant_name`,
  orders' `delivery_lead_days_min` / `appliance_connection_included` /
  `old_item_disconnection_included` / `two_person_crew_required`; `membership_holdings.status` /
  `dues_outstanding` / `activation_date` / `points_balance`, membership's
  `return_window_extension_days` / `restocking_fee_waiver_pct` /
  `points_value_usd_per_100_points` / `member_only_discount_pct`; `membership_events.points_delta`
  with `source_order_id` / `redemption_ref`; `order_events.credit_amount` / `charge_amount` /
  `unit_price`). Every one of these columns exists in `db_schema.json`.
- **Scope exclusivity and completeness across the M tasks.** Derived from the policy and the two
  masked worlds alone (not from `charter_scope`): task 0's tree is
  `{returns_ext_collection_slot_notice, returns_ext_collection_booking_window}` and task 1's is
  `{returns_ext_exchange_difference, returns_ext_member_fee_relief, returns_ext_restocking_fee_charge}`.
  The two sets are disjoint and their union is all five extended policies — **pairwise disjoint and
  jointly complete**.

### rule_compute_equivalence

Checked for all five policies, in both directions.

- Every `compute` binding of every policy carries a `compute_basis` entry, and every one of those
  entries is a verbatim substring of that policy's own `rule` (checked mechanically over the
  whitespace-normalised rule text). No `compute` binding rests on a basis absent from the rule.
- Sweeping back: every quantity, window, filter, tier, branch, cross-category read, acting base,
  cap/floor and rounding sentence in each `rule` is implemented by a restricted expression. Every
  tier named in every `factors[].ladder` is a sentence of the `rule` and a branch of the `decides`
  binding, and every branch of each `decides` binding is a tier the rule states. No tier lives only
  in `compute`, and no tier lives only in prose.
- Rounding and interval conventions are stated and implemented consistently: `RND(x, 2)` behind
  "rounded to the cent"; `int(...)` behind "rounded down to a whole day"; `int((n*7+4)/5)` behind
  "counted in days the depot is open, five in every seven, and rounded up to a whole day";
  `MX(0, ...)` behind "never less than nothing"; `MX(K('floor_open_days'), ...)` and
  `MX(K('same_day_floor_days'), ...)` behind the two floors; `MN(MX(...))` behind
  "held between the schedule's minimum and its cap".
- Two empty-promise candidates were checked and cleared: `returns_ext_collection_booking_window`'s
  carrier sentence and `returns_ext_exchange_difference`'s "The stock number recorded on the exchange
  is the stock number of the item the return was raised on" both govern a non-computed argument of
  the target tool (`carrier_name`, `exchange_sku`) rather than the `computes` quantity, and each
  fixes that argument to exactly one value.
- No `rule` names a tool, a policy id, or any snake_case token (checked mechanically).

**Conclusion: rule/compute equivalence holds in both directions for all five policies.**

### action_binding_and_uuids

| policy | target_tool | computes | owner |
| --- | --- | --- | --- |
| returns_ext_collection_booking_window | `issue_collection_booking_70222685` | booking_open_days | agent |
| returns_ext_collection_slot_notice | `confirm_collection_slot_e0893723` | pickup_notice_days | user |
| returns_ext_restocking_fee_charge | `charge_restocking_fee_677c7b7a` | restocking_fee_amount | agent |
| returns_ext_member_fee_relief | `waive_restocking_fee_47bbe442` | waived_fee_amount | agent |
| returns_ext_exchange_difference | `accept_exchange_item_1cf629c9` | price_difference_amount | user |

- Each pair is claimed by exactly one policy; no tool is a subject of two policies.
- uuid8s: `70222685`, `e0893723`, `677c7b7a`, `47bbe442`, `1cf629c9`. No two share a prefix, no two
  differ only in a tail, none is a sequence number or an adjacent value of another, and the set mixes
  all-digit and hex forms — consistent with five independent draws frozen with their tools.
- Docstrings: no docstring names another tool, states a position in a sequence, or carries an
  ordering word (before / after / first / once / until). Each states its own atomic effect, its own
  Args with four-way typing, and its own success return. `waive_restocking_fee_47bbe442`'s
  "the fee entry it relieves is left as it stands" presupposes a standing fee but that is the
  semantics of a waiver, not a sequence statement.
- No tool body aggregates history, judges eligibility, checks a state, or refuses because another
  entry is missing. Every body reads the one `return_authorizations` row by id, writes one row
  (plus, for the two fee tools, one `ctx.update` of the running quantity the base `accounts` block
  declares), and returns. The prerequisite is therefore never judged by the tool layer.

**Conclusion: unique action binding and uuid integrity hold.**

### prerequisite_graph

Three edges, all declared on the blocked side:

| blocked policy | problem | kind | gate | form | resolved_by |
| --- | --- | --- | --- | --- | --- |
| returns_ext_collection_slot_notice | returns_ext_collection_booking_window | value_input | `booking_recorded_day` | state | `issue_collection_booking_70222685` |
| returns_ext_member_fee_relief | returns_ext_restocking_fee_charge | value_input | `fee_charged` | state | `charge_restocking_fee_677c7b7a` |
| returns_ext_exchange_difference | returns_ext_member_fee_relief | value_input | `fee_held_back` | state | `waive_restocking_fee_47bbe442` |

- `prerequisite` is filled in on all five policies (`[]` on `returns_ext_collection_booking_window`
  and `returns_ext_restocking_fee_charge`).
- Every `problem` points at another extended policy id in this file; none points at a base policy or
  at itself. The graph is
  `slot_notice -> booking_window`, `member_fee_relief -> restocking_fee_charge`,
  `exchange_difference -> member_fee_relief` — a forest of two chains, **acyclic**, with no
  cross-task reference and therefore no cycle created across tasks either.
- Each `policy_source` is verbatim locatable in the **blocked** policy's own `rule` (checked
  mechanically on normalised text) and is **absent** from the depended-on policy's rule.
- `form: state` on all three; `fallback_reason` is absent on all three, which is correct because none
  is action-form. The state form is therefore honoured everywhere and no fallback needed testing.
- `condition` matches the handling-time state check 6 derives and is neither strengthened nor
  weakened: each names exactly the record-visible state its sentence names and adds only the
  value-input consequence.
- `resolved_by` is in each case the depended-on policy's own `target_tool`, and each genuinely moves
  the named binding: `issue_collection_booking_70222685` creates the `returns_shipping_label_issue`
  row that `LATEST('return_events','event_date', event_type='returns_shipping_label_issue')` reads;
  `charge_restocking_fee_677c7b7a` creates the `returns_restocking_fee_charge` row that
  `SUM('return_events','restocking_fee_amount', ...)` reads; `waive_restocking_fee_47bbe442` creates
  the `returns_restocking_fee_waive` row that `fee_relieved` reads and so moves `fee_held_back` from
  the whole fee to the fee less relief.
- `kind` matches `gate` in all three: each `gate` names a binding that exists in the blocked policy's
  own `compute` (`booking_recorded_day`, `fee_charged`, `fee_held_back`), so `value_input` is the
  honest label; none is a bare eligibility flip.
- No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears in
  any `prerequisite` field.

**Conclusion: the `prerequisite` declarations are self-consistent.**

### prerequisite_sentences

Four-point test on each edge.

**E1 — `returns_ext_collection_slot_notice` waits on a recorded collection booking.**
Sentence: *"The earliest day the collection may be booked for is settled only after a collection
booking naming the carrier that is to move the item stands recorded against the return with a last
usable day that has not passed."*
(1) ordering connective: "only after". (2) form: state — "a collection booking … stands recorded
against the return with a last usable day that has not passed" names a record-visible state in the
words `find_return_events` uses ("any prepaid label or collection booked with its carrier, tracking
reference and last usable day"); no performer, no action, no tool. (3) no tool, policy id,
snake_case token or row id. (4) strength: the `condition` says the same and adds only that the notice
runs from the day that entry was recorded, which is the value-input consequence, not a strengthening.
*One write brings the state about:* of the five task tools only
`issue_collection_booking_70222685` writes a `returns_shipping_label_issue` row into `return_events`
(`confirm_collection_slot_e0893723` writes `return_pickup_requests`), so the reader resolves the hop
uniquely. *Derivation:* the sentence says the notice waits on a booking whose last usable day has not
passed; `find_return_events` shows what bookings stand and their last usable day;
`returns_ext_collection_booking_window`'s own rule is the only rule in the charter that says how long
a collection booking stays usable and what carrier is recorded on it — so the reader concludes that a
fresh booking must be put on the return first, and there is no second reading.

**E2 — `returns_ext_member_fee_relief` waits on a charged restocking fee.**
Sentence: *"The relief is worked out only after the restocking fee it relieves stands charged against
the return."*
(1) "only after". (2) state form — "the restocking fee … stands charged against the return" is the
running quantity the base `accounts` block calls `restocking_fee_receivable` and
`find_return_authorizations` reads out as "any restocking fee still outstanding". (3) clean of tokens.
(4) `condition` adds only "so that the fee still standing against it is more than nothing".
*One write:* only `charge_restocking_fee_677c7b7a` creates a `returns_restocking_fee_charge` row.
*Derivation:* relief is a share of the fee still standing; the fee still standing is what has been
charged less what has been relieved; `returns_ext_restocking_fee_charge`'s own rule is the only rule
that says how a restocking fee is worked out — so the fee must be charged first. Single reading.

**E3 — `returns_ext_exchange_difference` waits on the membership relief.**
Sentence: *"The difference returned on an exchange is fixed only after the relief the membership
allows against the restocking fee owed on the return stands recorded against that return with the
membership as its ground."*
(1) "only after". (2) state form — a waiver entry recorded with the membership as its ground is
visible on the return's history (`find_return_events`: "restocking fees charged and waived with the
ground for the waiver"). (3) clean. (4) `condition` adds only the value-input consequence.
*One write:* only `waive_restocking_fee_47bbe442` creates a `returns_restocking_fee_waive` row.
*Derivation:* the difference keeps back what is left of the fee after relief; the only rule that says
what relief the membership allows is `returns_ext_member_fee_relief`'s own rule; so the relief must be
recorded first. Single reading.

- **No second wording of the dependency, no tool name, no other problem's id** in any blocked rule —
  with one exception recorded as **O-7**: `returns_ext_collection_slot_notice`'s rule refers to the
  depended-on booking twice more, in its baseline sentences, without an ordering connective.
- The depended-on rules do not restate any of the three sentences (checked mechanically).
- A **base** rule sentence states a cross-problem order in three places —
  `returns_authorization_and_logistics` ("the business authorisation the schedule requires is on file
  before the crew is booked"), `returns_exchange_handling` ("An exchange item is issued only once the
  returned item has been received and graded at a grade the schedule refunds in full") and
  `returns_condition_grading` ("Every returned item is inspected before the refund is worked out").
  No task's declared tree rests on any of them (each names a state the seed already carries, or a
  branch neither task enters), so each is recorded as an observation, **O-8**, not a red light.

**Conclusion: all three prerequisite sentences pass the four-point test in the state form.**

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry. Every `overwrite` entry's
`superseded_clause` was confirmed to be a verbatim substring of the named base rule, and every
`replaced_by` a verbatim substring of the extending rule. Findings (consequences are demonstrated in
the task files where a task's world reaches them):

| base policy | base sentence | extended treatment | declared? |
| --- | --- | --- | --- |
| returns_authorization_and_logistics | S1 state gate | inherited, unchanged | n/a |
| " | S2 allowed return methods | inherited; the carrier ladder of `returns_ext_collection_booking_window` is consistent with it | n/a |
| " | S3a "A prepaid label stays usable … reissued once without a fee" | replaced by the four-step window of `returns_ext_collection_booking_window` | **yes** |
| " | S3b "a collection needs the schedule's lead days of notice and may be moved only as often as the schedule allows" | replaced by the six-step notice of `returns_ext_collection_slot_notice` | **yes** |
| " | S4 carrier fee / S6 carriage damage | inherited, untouched | n/a |
| " | S5 business authorisation before the crew | inherited; no extended rule touches it (see O-8) | n/a |
| returns_restocking_fee | S1 percentage/min/cap | replaced by the six-step fee of `returns_ext_restocking_fee_charge` | **yes** |
| " | S2 state gate | inherited, unchanged | n/a |
| " | **S3 "No restocking fee is charged where the item is graded defective on arrival or not as described, or where the retailer shipped the wrong item"** | the extended formula zeroes only the *percentage* part and then raises the result to `restocking_fee_min_usd`, so a positive fee still stands | **NO — R-1** |
| " | **S4 "A device already activated on a network carries the schedule's flat activated device fee instead of a percentage fee"** | the extended formula never reads `activated_device_fee_usd`; on the one schedule that carries it every bound is 0, so the extended selector can never produce the flat fee | **NO — R-2** |
| " | S5a "the waiver is recorded with the membership as its reason" | inherited; `returns_ext_member_fee_relief` states "The relief is recorded with the membership as its ground" | n/a |
| " | S5b "the member's tier waiver percentage is applied to whatever fee is left where the schedule does not waive it outright" | replaced by the three-step share of `returns_ext_member_fee_relief`; but the replacement drops the "where the schedule does not waive it outright" restriction, so the outright-waiver branch of `restocking_fee_waived_for_member` is produced by no extended branch | partly — **O-1** |
| " | S6 goodwill waiver | inherited, untouched | n/a |
| returns_combo_membership_protection | S1a member window extension | inherited (no extended policy computes the return window) | n/a |
| " | S1b "the tier's restocking fee waiver percentage is applied to the fee the schedule charges" | replaced by `returns_ext_member_fee_relief`'s relief formula | **yes** |
| " | S2 "The extension is read from the membership tier standing on the day the return is asked for" | the extended policies read the membership holding as it stands at handling time | **O-2** |
| " | S3 protection plan / S5 stronger ground | inherited; neither task's world reaches them | n/a |
| " | S4 "A member who returns an item bought with reward points has the points restored rather than refunded in money" | implemented by `points_back_as_points` in `returns_ext_exchange_difference` | consistent |
| returns_exchange_handling | **S1 "An exchange is offered only on the schedules that allow it and only inside the schedule's exchange window, counted from the same anchor as the return window"** | inherited; no extended policy touches it | inherited — bears on task 1, see `1.md` **R-3** |
| " | S2a-b price difference direction | replaced by the seven-step difference of `returns_ext_exchange_difference` | **yes** |
| " | S2c "and on a like-for-like schedule no difference is settled at all" | the extended formula computes a difference on every schedule | **O-3** |
| " | S3 received-and-graded-in-full gate | inherited, unchanged | n/a |
| " | S4 haul-away / S5 plan moved | inherited; the parameters make both inert on the schedules the tasks use | n/a |
| returns_excl_refund_or_exchange | S1, S3, S5 | inherited and consistent: the exchange tool writes a `returns_exchange_issue` row carrying the difference as `refund_amount`, which base S3 expressly says is not a refund of the line | n/a |
| returns_refund_settlement | S2 state gate | inherited, unchanged | n/a |
| " | S3 "the delivery charge … refunded only where the schedule says so" | `delivery_carried_over` adds half the delivery charge into the exchange difference on a schedule whose `delivery_fee_refunded` is false | **O-4** |
| " | S4 "The restocking fee still outstanding is kept back from the refund as an offset rather than billed separately" | replaced by "The restocking fee still standing on the return is kept back last" | **yes** |
| " | S1, S5, S6 | inherited; no extended policy computes a refund component, a refund method or settlement days | n/a |

No `overwrite: []` appears in this charter.

### factor_ladders

Structure only. Per policy: declared factors, effect label, `decides`, ladder size, disjointness,
multi-source, `cross_difficulty`, and whether the ladder is stated in full in the `rule`.

**returns_ext_collection_booking_window** — 4 factors (3 `parameter`, 1 `method`).

| factor | effect | decides | tiers | outcomes distinct? | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| collection_route_window | parameter | route_open_days | 3 | yes (validity+7 / validity+3 / validity) | yes (orders variant lead × returns schedule freight fee) | orders |
| reissued_booking_window | parameter | reissue_reduction_days | 3 | yes (6 / 3 / 0) | tier 2 yes (count × expiry date); tier 1 single | — |
| aged_authorisation_window | method | aged_open_days | 3 | yes (halve / less a quarter / as counted) | no | — |
| member_booking_hold | parameter | member_extra_days | 3 | yes (4 / 2 / 0) | yes (status × tier extension × dues) | membership |

Binding sets are disjoint across the four factors; every `decides` is an input, never `result`.
Every tier's condition and value is a sentence of the `rule`; every tier is a branch of the named
binding. Labels honest: the one `method` selects a multiplier-and-floor convention on an
intermediate, which is a way the calculation itself varies.

**returns_ext_collection_slot_notice** — 5 factors (3 `parameter`, 2 `method`).

| factor | effect | decides | tiers | outcomes distinct? | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| collection_crew_notice | parameter | crew_notice_days | 3 | yes (8 / 6 / schedule's own) | tier 2 yes | orders |
| site_preparation_notice | parameter | site_extra_days | 3 | yes (2 / 1 / 0) | yes (connections × haul-away) | orders |
| member_priority_notice | parameter | priority_reduction_days | 3 | yes (2 / 1 / 0) | yes | membership |
| depot_day_count_convention | method | counted_notice_days | 3 | yes (five-in-seven / plus one day / calendar) | yes (freight fee × days standing) | — |
| waiting_return_priority | method | offered_notice_days | 3 | yes (halve / less a quarter / as counted) | yes (days standing × booking count) | — |

Disjoint bindings; every tier in the rule and in `compute`.

**returns_ext_restocking_fee_charge** — 6 factors (4 `parameter`, 2 `method`).

| factor | effect | decides | tiers | outcomes distinct? | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| shelf_loss_fee_rate | parameter | fee_rate | 4 | yes (22 / 18 / 14 / schedule's own 10) | tiers 1-2 yes (days held × grade) | — |
| holding_days_convention | method | days_held | 3 | yes | yes (label count × receipt date) | — |
| good_faith_share | method | good_faith_fee | 3 | yes (none / half / full) | tier 2 yes (reason × inspection) | — |
| route_handling_addition | parameter | handling_addition | 3 | yes (35 / 12 / 0) | yes (crew × lead) | orders |
| spent_points_addition | parameter | points_addition | 3 | yes (full value / half / 0) | yes (status × balance vs earned) | membership |
| credited_line_reduction | parameter | credited_reduction | 3 | yes (20 / 10 / 0) | tier 2 yes | orders |

**`spent_points_addition` tier 2 fails the outcome-realism test — R-4.** Everything else is
structurally sound; `credited_line_reduction`'s outcome direction is recorded as **O-9**.

**returns_ext_member_fee_relief** — 4 factors (3 `parameter`, 1 `method`).

| factor | effect | decides | tiers | outcomes distinct? | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| membership_standing_share | parameter | standing_share_pct | 3 | as stated yes (published / half / none) | yes (status × dues) | membership |
| year_earning_share | parameter | spend_share_pct | 3 | yes (10 / 5 / 0) | yes (status × points in 12m) | membership |
| returned_grade_share | parameter | grade_share_pct | 3 | yes (15 / 8 / 0) | yes (inspection exists × grade) | — |
| membership_tenure_scaling | method | scaled_relief | 3 | yes (×1.5 / ×1 / ×0.5) | tier 2 yes | membership |

`membership_standing_share`'s tiers 1 and 3 collapse to the same number on a tier whose published
waiver share is 0 (Circle Free Membership); as *stated* the three outcomes are distinct, so this is
recorded as **O-10** rather than a duplicate-tier red.

**returns_ext_exchange_difference** — 6 factors (4 `parameter`, 2 `method`).

| factor | effect | decides | tiers | outcomes distinct? | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| member_replacement_pricing | method | replacement_price | 3 | yes (less discount / less half / shelf) | yes (status × discount) | membership |
| held_item_drop_share | parameter | drop_share_pct | 3 | yes (40 / 70 / 100) | no (one date span) | — |
| delivery_carried_over | parameter | delivery_carried | 3 | yes (half / whole / nothing) | yes (charge exists × schedule flag) | orders |
| unused_carriage_deduction | parameter | carriage_deduction | 3 | yes (fee / half fee / nothing) | yes (booking count × schedule fee) | — |
| points_back_as_points | parameter | points_restored_part | 3 | yes (value / half value / nothing) | yes (status × points redeemed) | membership |
| standing_fee_holdback | method | fee_held_back | 3 | yes (charged less relief / whole charge / nothing) | yes (charge × relief) | — |

`standing_fee_holdback`'s tier is decided entirely by the two writes of this task's own chain and by
no seeded record — recorded as **O-11**.

**Counts against the bounds.** Every policy declares 4 to 6 factors with at least 2 `parameter` and
at least 1 `method`, every ladder has at least 3 pairwise-disjoint tiers stated in full in the rule,
and every tier's value or method is drawn from the charter (a schedule parameter, a declared `params`
key, or a cross-category tier parameter). Per-task multi-source and cross-difficulty coverage:
task 0 — multi-source present (e.g. `collection_route_window`, `waiting_return_priority`),
cross-difficulty present (`orders` and `membership`); task 1 — multi-source present
(e.g. `shelf_loss_fee_rate`, `membership_standing_share`), cross-difficulty present (`orders` and
`membership`). Whether each factor **bears weight** is a fact about one world and is proved in
`0.md` / `1.md` under `factor_weight`.

### findings

Charter-global findings. The task each bears on is named; that task's file demonstrates the
consequence against its own world.

---

**R-1 — SOURCE-POLICY RED: undeclared override of the "no fee where the retailer shipped the wrong
item" clause.**

- *Symptom.* Base and extended reach different conclusions about the same scored quantity
  (`restocking_fee_amount`) in the same situation.
- *Root cause.* `returns_ext_restocking_fee_charge`'s `overwrite` names only base sentence S1
  (the percentage/minimum/cap sentence). Base S3 is therefore inherited in full, but the extended
  formula contradicts it: `good_faith_fee` is zeroed for those reasons and the result is then raised
  to `restocking_fee_min_usd`.
- *Evidence.* Base `returns_restocking_fee`, S3: *"No restocking fee is charged where the item is
  graded defective on arrival or not as described, or where the retailer shipped the wrong item,
  because the fee pays for putting saleable stock back."*
  Extended rule: *"Where the reason recorded is that the wrong item was shipped or that the item
  arrived damaged in transit, no percentage fee is taken at all"* — followed by
  *"the result is held between the schedule's minimum and its cap"*, implemented as
  `result: RND(MN(MX(fee_before_bounds, P('restocking_fee_min_usd')), P('restocking_fee_cap_usd')), 2)`.
- *Demonstrated consequence.* Take a Standard Fifteen Day Return line, grade `open_box_complete`,
  `return_reason = wrong_item_shipped`, delivered on Store Pickup Hold, no credits and no
  membership. Base S3 gives **0.00**. The extended compute gives
  `good_faith_fee = 0`, `handling_addition = 0`, `points_addition = 0`, `credited_reduction = 0`,
  `fee_before_bounds = 0`, `result = RND(MN(MX(0, 9.95), 199.0), 2) = ` **9.95**. Two clauses of the
  same published policy therefore fight over one quantity, and an agent following base computes a
  different number from the scored one.
- *Affected artifact.* `env/env_0005_consumer_electronics_retailer/tasks/returns_and_restocking_desk/returns.extended.yaml`,
  `extended_policies[2].overwrite` (missing entry for base S3) and `extended_policies[2].compute.result`.
- *Bears on.* Neither task 0 nor task 1 reaches this branch (task 1's reason is
  `performance_disappointing`), so no per-task consequence is available; the contradiction is proved
  here on a situation inside the policy's own domain.
- *Relation to previous revisions.* First revision.

---

**R-2 — SOURCE-POLICY RED: the activated-device-fee branch is dropped.**

- *Symptom.* A branch base declares is one the extended selector can never produce (the "dropped
  branch" form).
- *Root cause.* The extended formula for `restocking_fee_amount` is built entirely out of
  `restocking_fee_pct`, `restocking_fee_min_usd` and `restocking_fee_cap_usd`; it never reads
  `activated_device_fee_usd`, and `overwrite` does not name base S4.
- *Evidence.* Base `returns_restocking_fee`, S4: *"A device already activated on a network carries the
  schedule's flat activated device fee instead of a percentage fee, and the two are never charged
  together."* The base `accounts` block confirms one quantity is at stake:
  `restocking_fee_receivable` = *"restocking and activated-device fees charged against a return and
  not yet settled or waived"*. The Activated Wireless Device Return schedule carries
  `restocking_fee_pct: 0`, `restocking_fee_min_usd: 0.0`, `restocking_fee_cap_usd: 0.0`,
  `activated_device_fee_usd: 45.0`.
- *Demonstrated consequence.* On the Activated Wireless Device Return schedule the extended compute
  reduces to `result = RND(MN(MX(x, 0.0), 0.0), 2) = ` **0.00** for every world, while base S4
  requires **45.00**. The base branch is unreachable through the extended policy.
- *Affected artifact.* same file, `extended_policies[2]` (`rule`, `compute`, `overwrite`).
- *Bears on.* Neither task; both tasks are on other schedules.
- *Relation to previous revisions.* First revision.

---

**R-4 — SOURCE-FACTOR RED: `spent_points_addition` tier 2 is an outcome that contradicts the ground
the rule gives for the addition.**

- *Symptom.* A tier's value is not what that line of business gives customers in that situation, and
  it is the opposite of what the rule's own stated ground entails.
- *Root cause.* The step is introduced as *"The value of reward points that cannot be clawed back is
  then added"*; tier 1 covers the case where the balance has fallen below the points the line earned
  (they cannot be clawed back) and adds their full value. Tier 2 covers the case where the balance is
  **at or above** the points the line earned — i.e. exactly the case where the points *can* be
  clawed back off the balance — and still adds half their cash value to the fee.
- *Evidence.* Extended rule: *"The value of reward points that cannot be clawed back is then added.
  Where the profile's membership stands active and its reward point balance now stands below the
  points the line earned, the value of the points the line earned at the tier's published redemption
  rate is added, because those points have been spent and cannot be taken back. Where the membership
  stands active and its balance stands at or above the points the line earned, half that value is
  added."* Compute: `points_addition: … (RND(points_earned * points_value_rate / 200, 2) if
  (member_status == 'active' and member_points_now >= points_earned) else 0)`.
- *Demonstrated consequence.* No retailer charges a returning customer cash for loyalty points it is
  simultaneously able to reverse off the balance; doing so recovers the same value twice. The tier
  therefore states a treatment no business in this line publishes, and it is inconsistent with the
  sentence that introduces the step in the same rule.
- *Affected artifact.* same file, `extended_policies[2].rule` and
  `extended_policies[2].factors[4].ladder[1]`.
- *Bears on.* Task 1 (which sits on tier 1, so its scored number is unaffected — the defect is in the
  ladder, not in the value taken).
- *Relation to previous revisions.* First revision.

---

**O-1 — Observation: the outright member waiver has no extended branch.** Base
`returns_restocking_fee` S5 restricts the tier-percentage rule to "where the schedule does not waive
it outright"; `returns_ext_member_fee_relief`'s replacement drops that restriction and governs every
case. On Member Extended Thirty Day Return (`restocking_fee_waived_for_member: true`) base implies the
whole fee goes while the extended formula gives only the tiered share. Not a red light here because
the restriction sits inside the clause the `overwrite` does name and neither task uses that schedule,
so no consequence can be demonstrated. Location: `extended_policies[3].overwrite[0]`.

**O-2 — Observation: the membership is read at handling time, not at the day the return was asked
for.** Base `returns_combo_membership_protection` S2 anchors the membership read to "the day the
return is asked for"; `returns_ext_collection_booking_window`,
`returns_ext_collection_slot_notice`, `returns_ext_member_fee_relief` and
`returns_ext_exchange_difference` all read the `membership_holdings` row as it stands now
(`CFIELD`/`CPARAM` on the live row). Neither task's seed carries a tier change between
`requested_date` and `frozen_time`, so no consequence is demonstrable.

**O-3 — Observation: the like-for-like tail of base `returns_exchange_handling` S2 is inherited but
never honoured.** Base: *"and on a like-for-like schedule no difference is settled at all."* The
Activated Wireless Device Return schedule carries
`exchange_price_difference_basis: an exchange is like for like only`, yet the extended formula
computes a difference on every schedule and reads that parameter nowhere. Not instantiated by either
task.

**O-4 — Observation: half a non-refundable delivery charge is paid out inside the exchange
difference.** `delivery_carried_over` tier 1 fires precisely when
`P('delivery_fee_refunded')` is false and adds 50% of the charge to the money returned, while base
`returns_refund_settlement` S3 says the delivery charge is refunded "only where the schedule says
so". The two readings can be reconciled — base
`returns_excl_refund_or_exchange` S3 says a price difference on an exchange is not a refund of the
line — so this is recorded as an observation rather than an undeclared override; but the stated
ground ("the customer does not pay to have the same line delivered twice") justifies not charging
again, not paying cash back.

**O-5 — Observation: the withheld restocking fee is never relieved on the record.**
`returns_ext_exchange_difference` keeps the standing fee back out of the difference, but
`accept_exchange_item_1cf629c9` does not touch `restocking_fee_outstanding`, and this difficulty
declares no offset write. After the chain runs, the receivable still shows the amount that has in
fact already been collected out of the difference. Base
`returns_refund_settlement` S4 recorded that netting as an offset event; the declared replacement
("kept back last") drops the event without providing another. No second defensible scored value
follows, so this is an observation on the terminal state.

**O-6 — Observation: "the days the item was held" is anchored two ways in one charter.**
`returns_ext_restocking_fee_charge`: *"The days the item was held are counted from the day the item was
delivered to the day it was booked in. Where a prepaid label or collection booking stands on the
return and the item was booked in on or after the day the latest of them was issued, the days are
counted instead from the day the return was authorised …"*
`returns_ext_exchange_difference`: *"Where the item was held longer than the long hold multiple of the
schedule's return window, counted from the day it was delivered to the day it was booked in …"*
Both use the same predicate and the same multiple (2) against the same window, and on task 1's world
they disagree (27 days vs 31 days, i.e. inside vs outside twice the window). Not a red light because
each rule states its own anchor inline and is therefore self-contained; the alternative figure a
reader who carries the first convention into the second would produce is demonstrated in `1.md`.

**O-7 — Observation: the same dependency is worded three times in
`returns_ext_collection_slot_notice`'s rule.** Besides the prerequisite sentence, the rule also says
*"counted in calendar days from the day the collection booking now standing on the return was
recorded"* and *"The days that have already passed since that booking was recorded are taken off the
notice"*. Both are value-input descriptions and carry no ordering connective, so the edge remains
stated once as an ordering; but a reader meets the dependency three times.

**O-8 — Observation: three base sentences state a cross-problem order that grounds no declared
edge.** `returns_authorization_and_logistics` S5, `returns_exchange_handling` S3 and
`returns_condition_grading`'s first sentence. No task's tree rests on any of them.

**O-9 — Observation: `credited_line_reduction` runs the wrong way for the reason given.** A
late-delivery goodwill credit already paid on the line *lowers* the restocking fee by 20 USD. The
rule offers no ground, and the ordinary commercial treatment of an allowance already given is to
recover it, not to discount the fee. Location: `extended_policies[2].factors[5]`.

**O-10 — Observation: `membership_standing_share` tiers 1 and 3 coincide numerically on Circle Free
Membership** (`restocking_fee_waiver_pct: 0`), where "the tier's published restocking fee waiver
share" and "no share at all" are both 0. As stated the three outcomes differ, so this is not a
duplicate-tier red.

**O-11 — Observation: `standing_fee_holdback`'s tier rests on no seeded record.** Its two
discriminating bindings (`fee_charged`, `fee_relieved`) are both produced by writes of the same
task's own chain, so the factor's `evidence: [history]` label is carried by no row of
`initial_state`. It bears weight at handling time, but it tests the chain rather than the customer's
world.

**O-12 — Observation: base `returns_exchange_handling` S1 and S3 are jointly unsatisfiable on the
shorter schedules.** S1: *"An exchange is offered only on the schedules that allow it and only inside
the schedule's exchange window, counted from the same anchor as the return window."* S3: *"An exchange
item is issued only once the returned item has been received and graded at a grade the schedule
refunds in full."* On Major Appliance Forty Eight Hour Return the exchange window is 2 days from
delivery while the collection alone needs `pickup_lead_days: 2` and the inspection may take
`inspection_days: 5`, so the two can never both hold; on Standard Fifteen Day Return the window is 15
days against `inspection_days: 3` plus the label's travel time, so the pair holds only for a return
that comes back and is graded almost at once. This tension belongs to the blueprint's base charter
rather than to this difficulty's artifacts, but it is part of the policy in force on this desk and it
is the root of task 1's `R-3` (see
`env/env_0005_consumer_electronics_retailer/audits/policy_task/returns_and_restocking_desk/1.md`).
Location: `env/env_0005_consumer_electronics_retailer/blueprint/products/returns.yaml`,
`policies[returns_exchange_handling].rule`.

## closing_checklist

Written after both tasks' reveals, so it sits below the pre-reveal charter-global section.

**This difficulty does NOT close.** Step 4's checklist item by item:

| item | status |
| --- | --- |
| per-task audit files correspond one-to-one with the tasks, `_difficulty.md` alongside them | **yes** — `0.md`, `1.md`, `_difficulty.md` in this directory |
| old revisions traceable | **yes** — first revision; nothing to carry forward |
| every comparison section carries a PASS | **NO** — `1.md` `## source_gt_comparison` records `SOURCE-TASK RED` (**R-3**, **R-5**); `0.md` records PASS on all four relationships |
| this difficulty's extended policies fully covered | **yes** — five policies, task 0 claims two, task 1 claims three |
| the M tasks' scopes pairwise disjoint over the whole problem tree | **yes** — `{booking_window, slot_notice}` vs `{restocking_fee_charge, member_fee_relief, exchange_difference}`, disjoint in policies, tools, subjects and base lineage |
| task tools and GT closed | **yes** — each of the five tools is the target of exactly one policy and is called by exactly one task, and every gold write's computed argument is the `computes` of that policy |
| each task tool uses an independently generated, frozen uuid8 | **yes** — see `### action_binding_and_uuids` |
| every problem tree has 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥ 1 `owner=user` write, no cycle | **yes** — task 0: 1 problem / 1 `value_input` / root is `owner=user`; task 1: 2 problems / 2 `value_input` / root is `owner=user` |
| the difficulty's `prerequisite` edges are together a DAG with no cross-task cycle | **yes** — two disjoint chains, no cross-task reference |
| every computation declares a self-sufficient baseline and 4–6 factors (2 `parameter`, 1 `method`; per task ≥ 1 multi-source and ≥ 1 cross-difficulty) | **yes** on the counts and on baseline self-sufficiency — five computations declaring 4, 5, 6, 4 and 6 factors, every whole baseline definite and different from gold (7, 2, 124.90, 29.12, 300.00) |
| every ladder ≥ 3 tiers stated in full in its rule, tiers distinct in outcome, conditions and outcomes ones that line of business actually holds | **NO** — `spent_points_addition` tier 2 fails the outcome test (**R-4**); the rest hold |
| every factor proved to bear weight on its task's world against an honest baseline | **yes** — all 25 declared factors across the five computations move the scored value, and every `baseline` is the value the policy's own `baseline.rule` states |
| instantiation-stage gates re-run once on the final form | **yes** — re-run 2026-09-18 on the unchanged artifacts (`returns.extended.yaml` = `c0c05a50a6d836a5`, `task_tools.py` = `7a0140a9b4173cc6`): `EXTENDED OK`, `TASK TOOL CONTRACT OK`, `REPLAY OK`, `SOLVABILITY OK`, `COMPUTE OK`, `GROUNDING OK`, `SCOPE OK`. `check_traceability` still cannot run: it needs the published KB, which the render step has not produced. |

**Per-task verdicts.**

| task | policy self-consistency | problem tree | factors bear weight | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | **PASS** |
| 1 | PASS (per-task checks; charter-global reds inert here) | PASS | PASS (weight); ladder defect **R-4** is charter-global | **FAIL** | **SOURCE-TASK RED** |

**Charter-global red lights outstanding:** **R-1** and **R-2** (`SOURCE-POLICY`, undeclared overrides
of base `returns_restocking_fee` S3 and S4), **R-4** (`SOURCE-FACTOR`,
`spent_points_addition` tier 2). None of the three bears on a scored value of either task, but all three
are defects of the charter both tasks' documents will be rendered from.

Because "policy self-consistency PASS + problem tree holds PASS + factors bear weight PASS + unique
solution PASS" does not hold together across the difficulty, **returns_and_restocking_desk does not pass
the source-layer audit.**

### auditor_write_disclosure

Disclosed against the boundary "an audit does not change `blueprint/`, `tasks/` or the runtime
`erlbench/`".

Re-running the instantiation-stage gates on the final form (the last checklist row above) **wrote to
both task files**. `skills/erl-task-instantiate/scripts/replay_tasks.py` recomputes `db_closure` and
`db_closure_matches_initial_state` and writes the task JSON back unless `--check` is passed
(`write_back = "--check" not in sys.argv`, line 134; `open(tp, "w").write(...)`, line 303). The
auditor ran it without `--check`, so `tasks/0.json` and `tasks/1.json` were rewritten at
2026-09-18 09:27:18Z.

**What changed: nothing semantic.** Verified after the fact on both files:
`db_closure`'s row set equals `initial_state`'s row set (13 rows for task 0, 25 for task 1), every
`db_closure` row is byte-equal to its `initial_state` row, `db_closure_matches_initial_state` is still
`True`, and every other top-level key is unchanged — `computations[].expected` still 12 / 6 and
116.48 / 53.29 / 56.37, `baseline_result` still 7 / 2 and 124.90 / 29.12 / 300.00, and the gold
arguments of all five writes still exactly those compared in `0.md` and `1.md`. Only the **key order**
inside `db_closure` moved, because the script builds it by iterating a Python `set` of
`(table, row_id)` tuples, whose order varies between interpreter runs.

**Both GT reveals happened before this write**, so nothing in the two comparison sections was read from
a rewritten file.

**Observation for the tooling (outside the four relationships, reported for completeness):** because
`replay_tasks.py` writes back by default and its `db_closure` key order is not stable across runs, the
task files' bytes change on every gate run even when nothing about the task has changed. That makes
"the artifacts are unchanged since the gate snapshot" unverifiable by file hash, and it is why the two
task-file hashes quoted in the brief could not be reproduced here. Location:
`skills/erl-task-instantiate/scripts/replay_tasks.py` lines 134 and 290–303.

---

# revision_2

Re-audit round 2, 2026-09-18. Same auditor as revision 1, resumed with the round-1 derivations and
evidence intact. This round is **not** a fresh blind derivation — GT for this difficulty was revealed
in round 1 and cannot be un-seen. It is an item-by-item verification that each round-1 red light is
genuinely closed, that the rework introduced no new defect, and that nothing already passed has
regressed. Everything below was re-derived or recomputed by the auditor from the artifacts; no claim of
the reworker is accepted on its own word.

## revision_2 / re-derivation basis

| input | round 1 | round 2 | treatment |
| --- | --- | --- | --- |
| `returns.extended.yaml` | `c0c05a50a6d836a5` | `dfc4f4e8f87fb919` | **changed — every section resting on it re-derived in full** |
| `task_tools.py` | `7a0140a9b4173cc6` | `7a0140a9b4173cc6` | unchanged — `### action_binding_and_uuids` **carried forward by reference**, on those two hashes as the grounds |
| `tasks/0.json` | — | masked view `e19ab1baa4f7a24f` | changed — task 0's per-task sections re-derived |
| `tasks/1.json` | — | masked view `847d095ac85d0e1f` | changed — task 1's per-task sections re-derived |
| blueprint | unchanged | unchanged | base section of the extended file re-verified byte-verbatim against `blueprint/products/returns.yaml` for all ten shared sections |

Gates re-run by the auditor with `replay_tasks --check` as instructed: `EXTENDED OK`,
`TASK TOOL CONTRACT OK`, `SOLVABILITY OK`, `COMPUTE OK`, `GROUNDING OK`, `SCOPE OK`, `REPLAY OK`, and
the two task files' hashes verified byte-identical before and after the run — **no auditor write this
round**, unlike revision 1 (see `### auditor_write_disclosure`).

**Correction to the record.** The coordinator's brief attributes to revision 1 a report that the masked
copies had been re-serialised with sorted JSON keys. That was not my finding. Revision 1's
`### auditor_write_disclosure` concerned one thing only: `replay_tasks.py` rewriting `db_closure` into
both task files because `write_back` defaults on. I made no claim about the masking tool's key order and
took no work-around on that account. Noting it so the record is accurate; the masking-tool fix is
welcome either way.

## revision_2 / charter-global re-derivation

Re-derived from `dfc4f4e8f87fb919`.

### policy_conflict_scan (revision 2)

- Base copy still byte-verbatim in all ten sections.
- Subjects, triggers, target tools and `computes` unchanged; the five `(target_tool, computes)` pairs
  remain pairwise distinct and each is claimed by exactly one policy.
- Task scopes unchanged and still pairwise disjoint and jointly complete over the five policies
  (`charter_scope` re-read after the freeze and re-derived independently from the two trees).
- Three new result-level conformance branches appear, all three stated in the rule and carried in
  `compute_basis`: `retailer_ground_no_fee` (policy 3), `outright_member_waiver` (policy 4),
  `like_for_like_only` (policy 5). Each is a 0/1 selector on `result`, and each implements an inherited
  base provision rather than concealing a deviation from one — the opposite of the disguised-override
  form revision 1 warned about. None is declared as a factor, correctly: none is a tiered variation of
  the desk's own method.
- Terminal states and cross-category read boundaries unchanged (`orders` and `membership` only).

### rule_compute_equivalence (revision 2)

Re-swept over all five policies. Every `compute` binding of every policy carries a `compute_basis`
entry — including the eight new bindings (`activated_device_fee`, `chargeable_fee_base`,
`retailer_ground_no_fee`, `bounded_fee`, `outright_member_waiver`, `off_shelf_days`,
`like_for_like_only`, and policy 2's merged counting sentence). Every tier of every ladder is stated in
the rule and implemented as a branch of its `decides` binding, and every branch of every `decides`
binding is a tier the rule states; verified semantically tier by tier (the mechanical substring test is
not decisive for `ladder.when` text, because the ladder restates the rule's condition in standalone
form where the rule uses anaphora — "Where **that service** offers no slot…" against "**the service the
item was delivered on** offers no slot…").

**One exception, and a correction to revision 1.**
`returns_ext_collection_booking_window.compute_basis.result` is not a verbatim substring of its own
rule: it concatenates the four-steps sentence and the floor sentence in the reverse of their order in
the rule. Both sentences are individually verbatim and every quantity `result` computes is supported, so
there is no consequence. **Revision 1's `### rule_compute_equivalence` asserted that every
`compute_basis` entry is a verbatim substring, "checked mechanically over the whitespace-normalised rule
text". That assertion was overstated**: the mechanical sweep I ran in round 1 covered the
`prerequisite.policy_source` and `overwrite` clauses, not `compute_basis`, which I read rather than
swept. The condition was present in round 1 as well, so it is **not a regression** — it is an error in
my own round-1 report, corrected here and recorded as **N-5**.

### action_binding_and_uuids (revision 2)

**Carried forward by reference** from revision 1's `### action_binding_and_uuids`. Grounds:
`task_tools.py` is byte-identical (`7a0140a9b4173cc6` in both rounds), and the extended charter's
`target_tool` / `computes` assignments are unchanged, so nothing that section rests on has moved. The
five uuid8s, the docstrings' silence about sequence, and the finding that no tool body judges a
prerequisite all stand unchanged and were not re-derived.

### prerequisite_graph and prerequisite_sentences (revision 2)

Re-derived. All three edges are unchanged in `problem`, `kind`, `gate`, `form`, `condition`,
`policy_source`, `resolved_by` and `effect`; `form: state` on all three with no `fallback_reason`
needed; each `policy_source` re-verified verbatim in the blocked policy's own rule and absent from the
depended-on rule; each `gate` re-verified to name a binding of the blocked policy's own `compute`; each
`resolved_by` re-verified to be the depended-on policy's `target_tool`. Graph still two disjoint chains,
acyclic, no cross-task reference. The four-point test passes on all three sentences as in revision 1.

Policy 2's rule was reworded for **O-7** and now states the dependency twice rather than three times —
once as the ordering sentence (the `policy_source`) and once as the counting sentence the value-input
needs — which is the minimum the edge can be described in. Verified that the `policy_source` text itself
is unchanged and still the only ordering statement in that rule.

### factor_ladders (revision 2)

| policy | factors | parameter | method | tiers | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| returns_ext_collection_booking_window | 4 | 3 | 1 | 3,3,3,3 | orders, membership |
| returns_ext_collection_slot_notice | 5 | 3 | 2 | 3,3,3,3,3 | orders ×2, membership |
| returns_ext_restocking_fee_charge | 6 | 4 | 2 | 4,3,3,3,3,3 | orders ×2, membership |
| returns_ext_member_fee_relief | 4 | 3 | 1 | 3,3,3,3 | membership ×3 |
| returns_ext_exchange_difference | 6 | 4 | 2 | 3,3,3,3,3,3 | membership ×2, orders |

All within the 4–6 bound with ≥ 2 `parameter` and ≥ 1 `method` each; every ladder ≥ 3 pairwise-disjoint
tiers stated in full in its rule; multi-source and cross-difficulty coverage present in both tasks.
Three ladders changed and were re-derived tier by tier:

- **`shelf_loss_fee_rate`** — thresholds reshaped from `long_hold_multiple` (2 × window, window) to
  `short_hold_divisor` (window, window ÷ 2). Partition on a 15-day window: > 15 → 22 or 18 by grade;
  (7.5, 15] → 14; ≤ 7.5 → the schedule's 10. Disjoint, exhaustive, four distinct outcomes.
- **`spent_points_addition`** — rewritten; see **R-4** below. Three distinct outcomes, each matching the
  ground the rule gives for the step.
- **`held_item_drop_share`** — same reshaping, and its quantity renamed to "how long the item was away
  from the shelf" with binding `off_shelf_days`; see **O-6**.

`good_faith_share`'s first tier now covers only damage in transit; its outcome phrase is the subject of
**N-1**.

### findings (revision 2)

**Verdict on every round-1 item, verified against the artifacts.**

| id | round-1 verdict | reworker's claim | auditor's verdict |
| --- | --- | --- | --- |
| **R-1** | SOURCE-POLICY RED | closed by conforming the formula to base | **CLOSED** |
| **R-2** | SOURCE-POLICY RED | closed by implementing the branch | **CLOSED** |
| **R-4** | SOURCE-FACTOR RED | closed by rewriting the ladder + moving the world | **CLOSED** |
| **O-1** | observation | closed | **CLOSED** |
| **O-2** | observation | answered with argument, no change | **still an observation; argument sound on consequence, one false supporting claim — N-4** |
| **O-3** | observation | closed | **CLOSED** |
| **O-4** | observation | closed by restating the ground | **CLOSED**, with **N-3** on a neighbouring ground |
| **O-5** | observation | answered with argument, no change | **CLOSED — argument sound; reclassified blueprint-level** |
| **O-6** | observation | closed | **CLOSED** |
| **O-7** | observation | closed | **CLOSED** |
| **O-8** | observation | no change available or needed | **correctly answered; remains a blueprint-level observation** |
| **O-9** | observation | closed by giving the rule a ground | **CLOSED for the direction; N-3 records the residue** |
| **O-10** | observation | answered with argument, no change | **correctly answered; remains an observation** |
| **O-11** | observation | answered with argument, no change | **CLOSED — argument sound** |
| **O-12** | observation | resolved inside this charter; blueprint untouched | **addressed for this desk; blueprint tension unchanged and still an observation** |

---

**R-1 — CLOSED.** The extended formula now conforms to base `returns_restocking_fee` S3 rather than
declaring an override. The rule carries *"No fee at all is charged where the grade recorded is that the
item was defective on arrival or not as described, or where the reason recorded is that the wrong item
was shipped, and in that case nothing is charged and the schedule's minimum does not apply"*, and
`compute` carries `retailer_ground_no_fee` with `result: 0.0 if retailer_ground_no_fee == 1 else
RND(bounded_fee, 2)` — the zero is applied **before** the minimum, which was the exact mechanism of the
round-1 defect. Recomputed on task 1's world with each ground substituted in turn: `wrong_item_shipped`
→ **0.00**, `defective_on_arrival` → **0.00**, `not_as_described` → **0.00**. Revision 1's demonstration
situation (Standard Fifteen Day, `open_box_complete`, `wrong_item_shipped`) gave base 0.00 against
extended 9.95; it now gives 0.00 against 0.00. Base and extended reach the same conclusion in that
situation.

**R-2 — CLOSED.** The dropped branch is implemented. The rule carries *"Where the schedule charges a
flat activated device fee, that fee is charged instead of the percentage fee, the two are never charged
together, and the schedule's percentage minimum and percentage cap do not bound it"*, and `compute`
carries `activated_device_fee: P('activated_device_fee_usd')`,
`chargeable_fee_base: activated_device_fee if activated_device_fee > 0 else percentage_fee`, and
`bounded_fee: MX(0, fee_before_bounds) if activated_device_fee > 0 else MN(MX(fee_before_bounds,
P('restocking_fee_min_usd')), P('restocking_fee_cap_usd'))`. Recomputed with the authorisation moved to
Activated Wireless Device Return: `chargeable_fee_base` = **45.00**, the schedule's flat fee, and the
zero percentage minimum and cap no longer bound the result. Base S4's branch is reachable through the
extended policy; revision 1's demonstration (0.00 against base's 45.00) no longer holds.

**R-4 — CLOSED.** The ladder's outcomes now match the ground the rule gives for the step. Tier 1 is *"its
reward point balance now stands at nothing"* → the whole value of the points the line earned, *"because
none of them can be taken back off a balance that is empty"*; tier 2 is *"its balance stands above
nothing but below the points the line earned"* → the value of *"the part that cannot be taken back, that
is the points the line earned less the balance now standing"*; the fall-through adds nothing, *"because
the points the line earned are taken back off the balance instead"*. The case revision 1 named — a
balance at or above the points earned, where the points **can** be clawed back — now adds nothing, which
is what clawing them back means. Each of the three outcomes is what a retailer does in that situation,
and each is derivable from the step's stated ground. Verified on the world: `points_balance` is 0 and the
ledger reconciles to it exactly (3200 + 1177 + 1873 − 500 − 5750 = 0), so the customer sits on the
rewritten tier 1 and the scored addition is still 14.05.

**O-1 — CLOSED.** The relief rule now carries *"Where the schedule waives the fee for a Circle member
outright, the whole fee still standing is relieved and no share is worked out"*, implemented as
`outright_member_waiver: 1 if P('restocking_fee_waived_for_member') else 0` with
`result: RND(fee_standing, 2) if outright_member_waiver == 1 else RND(MN(scaled_relief, fee_standing),
2)`. Recomputed with the authorisation moved to Member Extended Thirty Day Return
(`restocking_fee_waived_for_member: true`): the relief becomes the whole standing fee, which is what base
`returns_restocking_fee` S5's excluded case implies. The branch the round-1 finding said no extended
selector produced now exists. See **N-2** for a small self-sufficiency residue in the baseline block.

**O-3 — CLOSED.** The rule now carries *"Where the schedule settles an exchange like for like only, no
difference is settled at all"*, implemented as `like_for_like_only` keyed on
`P('exchange_price_difference_basis')` with `result: 0.0` on that branch. The inherited tail of base
`returns_exchange_handling` S2 is now honoured; on task 1's schedule the basis is today's shelf price and
nothing moves.

**O-4 — CLOSED.** The ground now supports what the money does: *"because the charge paid on the line
bought one delivery of goods the customer is giving back and the replacement is delivered again at no
further charge, so the share of it the first delivery did not earn goes back with the difference"*. That
is a reason for returning a share rather than merely for not charging twice, which was the round-1
objection. Tiers, share and the 14.50 unchanged.

**O-5 — CLOSED, and reclassified as a blueprint-level observation.** The reworker declined to change it
and argued; the argument is **sound on the evidence**, verified independently against the base charter:
`restocking_fee_receivable` carries exactly two delta events in the whole charter —
`returns_restocking_fee_charge` (`direction: in`) and `returns_restocking_fee_waive` (`direction: out`) —
and `returns_refund_offset` carries `account: refund_payable, direction: out`, not the receivable. So
base's own netting sentence reduces what the retailer owes and never the fee receivable, no event in the
charter can clear a charged-and-unwaived fee, and having the exchange write clear
`restocking_fee_outstanding` would break the account's declared delta set rather than mend the record.
The standing receivable is the blueprint's treatment, not this policy's invention. The observation is
correctly answered and moves to the blueprint's account.

**O-6 — CLOSED.** The exchange policy no longer uses the fee policy's phrase. It now fixes its share
*"by how long the item was away from the shelf, counted from the day it was delivered to the day it was
booked in"*, with binding `off_shelf_days`, against the plain return window; the fee policy keeps *"the
days the item was held"*, with binding `days_held` and its own travel-time convention. Two different
names for two different quantities, each with its anchor stated inline. Recomputed on task 1's world:
`days_held` = 15 and `off_shelf_days` = 16, and the phrase that formerly read identically in both rules
is gone, so the 149.21 alternative revision 1 demonstrated is no longer reachable by carrying one rule's
convention into the other.

**O-7 — CLOSED.** Policy 2's rule now carries the dependency twice, not three times: the ordering
sentence (the edge's `policy_source`, unchanged) and one merged counting sentence, *"counted in calendar
days from the day the collection booking now standing on the return was recorded, the day it was
recorded counted as day zero and the days that have already passed since then taken off"*. The
value-input must be described somewhere, so two is the floor. No binding and no value moved — verified
by recomputing both of task 0's values.

**O-8 — correctly answered; remains an observation.** The three base sentences are in the frozen
blueprint and outside the reworker's write domain. Re-verified that no declared edge of either task rests
on any of them and that the states they name are carried by the seed on both worlds.

**O-9 — CLOSED for the direction.** The rule now gives the ground it lacked: *"because a line the
retailer has already credited for its own failure does not then carry the full charge for putting the
stock back"*. That is a consistency a desk does keep. The residue — that the binding sums a credit kind
the ground does not cover — is recorded as **N-3**.

**O-10 — correctly answered; remains an observation.** The three tiers select three treatments as
stated; the numerical coincidence arises only on a tier that publishes no waiver share, where "the tier's
published share" and "no share at all" are the same nothing, which is what that tier gives either way.
No world of this difficulty sits on it. This is what revision 1 already concluded ("as stated the three
outcomes are distinct, so this is not a duplicate-tier red"), so declining to change it is right.

**O-11 — CLOSED; the argument is sound.** The decisive half is structural and I verify it: the factor's
two discriminating bindings are `fee_charged` and `fee_relieved`, and seeding rows that would put the
customer on a tier other than the fall-through at the **opening** would make edge 2 (no fee charged) or
edge 1 (no waiver recorded) already satisfied at `frozen_time` — which is exactly what the problem tree
requires to be false. The factor therefore cannot rest on seeded rows without destroying the tree it
belongs to. The skill's red-light condition for this shape is a **stamp** naming the outcome, and none
exists. Accepted; the observation is answered rather than merely deflected.

**O-12 — addressed for this desk; the blueprint tension is unchanged.** Inside this charter the
obstruction is resolved: the R-3 override states the window this desk offers an exchange inside and adds
the member extension the schedule takes, and task 1's world now satisfies base S1 and base S3 together
(received 2026-03-16 and graded 2026-03-17, both inside the window that runs to 2026-03-30). The
underlying blueprint tension on the short schedules is untouched and unchangeable from here: on Major
Appliance Forty Eight Hour Return the exchange window is still 2 days from delivery with
`member_window_extension_applies: false`, against `pickup_lead_days` 2 and `inspection_days` 5, so S1 and
S3 remain jointly unsatisfiable there. Correctly out of the reworker's write domain; the observation
stands against `blueprint/products/returns.yaml`.

---

### new findings (revision 2)

No new red light. Six observations, all verified by recomputation.

**N-1 — Observation: `good_faith_share` tier 1's outcome phrase promises more than the policy delivers.**
The tier reads *"Where the reason recorded is that the item arrived damaged in transit, no fee is taken
at all, because the damage happened in the carrier's hands and not the customer's."* The subsequent
declared steps then add the handling and the points value, take off the credits, and floor the result at
the schedule's minimum. Recomputed: on task 1's own world with `return_reason` set to
`damaged_in_transit` the fee is **29.05** (0 share + 35.00 handling + 14.05 points − 20.00 credits); on a
bare world with no membership and no credits it is **35.00**. The same rule's genuine zero case is
distinguished only by the clause attached to it — *"and in that case nothing is charged and the
schedule's minimum does not apply"* — so a reader who follows the declared order reaches 35.00 and there
is no second defensible number; that is why this is an observation and not a red light. But two sentences
of one rule use near-identical English ("No fee at all **is charged**" / "no fee **is taken** at all")
for outcomes that differ by the whole of the handling and the minimum, and a reader who stops at the tier
sentence writes 0.00. Flagged explicitly for the KB-document audit, where that reader lives.
Location: `returns.extended.yaml`, `extended_policies[2].rule` and `factors[2].ladder[0]`.

**N-2 — Observation: the relief policy's `baseline` states a branch whose figure it does not publish.**
`extended_policies[3].baseline.params` is `[]`, but the O-1 fix put *"Where the schedule waives the fee
for a Circle member outright, the whole fee still standing is relieved and no share is worked out"* into
`baseline.rule`. The condition of that sentence is the schedule parameter
`restocking_fee_waived_for_member`, which `baseline.params` does not name, so the baseline document as
declared states a branch a reader cannot resolve from it. Inert on task 1's world — the flag is false on
Standard Fifteen Day Return and the baseline still yields a definite 29.12, different from gold — so no
red light. Introduced by the O-1 fix.

**N-3 — Observation: O-9's new ground does not cover one of the rows its binding sums.** The rule now
justifies the reduction by *"a line the retailer has already credited for its own failure"*, while
`line_credits: XSUM('orders','order_events','credit_amount', order_line_reference=F('order_line_reference'))`
carries no `credit_kind` filter, and the line carries a `promotional_discount` of 3.75 beside the
`late_delivery_credit` of 25.00. A promotional discount is a price promotion, not an admission of the
retailer's failure. No consequence on the score: 25.00 alone already reaches the 25.00 threshold, so the
tier and the 20.00 are unchanged whichever reading is taken. Location:
`extended_policies[2].rule`, `extended_policies[2].compute.line_credits`;
`tasks/1.json` `initial_state.order_events` (the `promotional_discount` row).

**N-4 — Observation: a false supporting claim in task 1's dossier, contradicted by task 0's.** Task 1's
O-2 disposition states *"The one place this difficulty now uses the extension is the exchange window
sentence added for R-3"*. That is false: `member_booking_hold` (policy 1) and `member_priority_notice`
(policy 2) both decide their tier by testing the membership tier's published
`return_window_extension_days` against `top_member_extension_days` / `paid_member_extension_days`, read
via `CPARAM('membership','return_window_extension_days', status='active')` off the holding standing now.
Task 0's dossier states this correctly — *"they read the tier's published extension days as the evidence
of a tier band"* — so the two dossiers contradict each other on a fact about the charter. Consequence:
none, and this is why **O-2 remains an observation rather than becoming a red light** — on both worlds
`tier_effective_date` (2022-11-02 and 2023-05-02) precedes `requested_date` (2026-03-05 and 2026-03-01),
so the tier standing on the day the return was asked for is the tier standing at `frozen_time` and the
two readings coincide. The consequence-half of the reworker's argument is sound; the factual half is not.
Location: `tasks/1.json`, `design_rationale`, the O-2 paragraph.

**N-5 — Observation, and a correction to revision 1.**
`returns_ext_collection_booking_window.compute_basis.result` is not a verbatim substring of its rule: it
concatenates the four-steps sentence and the floor sentence in the reverse of their order there. Both are
individually verbatim and every quantity `result` computes is supported, so there is no consequence.
Revision 1's `### rule_compute_equivalence` claimed every `compute_basis` entry was a verbatim substring
and said so was "checked mechanically"; in fact the mechanical sweep covered the `policy_source` and
`overwrite` clauses only. The condition also held in round 1, so this is **not a regression** but an
error in my own earlier report, corrected here.

**N-6 — Observation: the near-miss order added for F-1 carries no `seed_consistency` entry.**
`tasks/0.json` `initial_state.purchase_orders.779d3424-ecbd-4338-87d0-d47f0867f1e9` and its two
`order_events` rows are deliberately planted and load-bearing for the near-miss claim, but
`solvability_contract.seed_consistency` still carries only the two entries of revision 1. I verified the
row independently and it contradicts nothing: Standard Parcel Delivery, placed 2025-11-08 against
`promised_date` 2025-11-12 (4 days against `delivery_lead_days_min` 2), `haul_away_requested` and
`installation_requested` both false as that service provides, `order_total` 268.91 against a 249.00
merchandise line and its matching payment capture. No red light; the gap is in the proof's coverage, not
in the world.

## revision_2 / closing_checklist

**This difficulty now closes.** Step 4's list, re-checked on the round-2 form:

| item | status |
| --- | --- |
| per-task audit files one-to-one with the tasks, `_difficulty.md` alongside, old revisions traceable | **yes** — revision 1 text left untouched; revision 2 appended below it in all three files |
| every comparison section carries a PASS | **yes** — `0.md` and `1.md` revision_2 both PASS on all four relationships |
| extended policies fully covered; task scopes pairwise disjoint over the whole tree | **yes** — 2 + 3 over five policies, re-derived |
| task tools and GT closed; each tool an independently generated, frozen uuid8 | **yes** — carried forward on the unchanged `task_tools.py` hash |
| every tree: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥ 1 `owner=user` write, no cycle; the difficulty's edges together a DAG | **yes** — task 0: 1/1/root is `owner=user`; task 1: 2/2/root is `owner=user`; two disjoint chains |
| every computation: self-sufficient baseline, 4–6 factors (2 `parameter`, 1 `method`; per task ≥ 1 multi-source, ≥ 1 cross-difficulty), every ladder ≥ 3 tiers stated in full, tiers distinct in outcome, conditions and outcomes ones the business holds, every factor load-bearing against an honest baseline, baseline alone definite and ≠ gold | **yes** — 25 factors across five computations, all recomputed load-bearing; whole baselines 7, 2, 124.90, 29.12, 300.00, all definite and all ≠ gold. **N-1** and **N-2** are wording and completeness observations, not ladder or baseline failures |
| instantiation-stage gates re-run once on the final form | **yes** — all seven green, `replay_tasks --check`, task files byte-unchanged by the run |

**Per-task verdicts, revision 2.**

| task | policy self-consistency | problem tree | factors bear weight | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | **PASS** (unchanged from revision 1; no regression) |
| 1 | PASS | PASS | PASS | **PASS** (was FAIL) | **PASS** |

No red light remains anywhere in this difficulty. "policy self-consistency PASS + problem tree holds PASS
+ factors bear weight PASS + unique solution PASS" now holds together across both tasks, so
**returns_and_restocking_desk passes the source-layer audit**, carrying the observations **N-1** to
**N-6** and the standing blueprint-level observations **O-5**, **O-8**, **O-10**, **O-12** forward to the
render step. **N-1** in particular should be put in front of the KB-document audit.

### revision_2 / hash-convention loop closed

Revision 1 could not reproduce the two task-file hashes the brief quoted and recorded that as part of the
`replay_tasks.py` disclosure. Round 2 settles it: the coordinator's hashes are plain `sha256` over the
file bytes, truncated to 16 hex digits, and this round both reproduce exactly —
`tasks/0.json` = `15d126cc6fe5c79d` and `tasks/1.json` = `a201b2cd4a0fc416`, matching the brief. Round 1
could not match them only because `replay_tasks.py` had already rewritten `db_closure`'s key order in the
interval. Running the gate with `--check` this round left both files byte-identical, verified before and
after, so the artifacts this audit ruled on are exactly the artifacts the brief named.

---

# revision_3

Narrow re-audit, 2026-09-20, same auditor. Revisions 1 and 2 above are untouched. Scope: verify that the
two rule sentences added after the render-layer audit disturb nothing, introduce no defect, and regress
nothing. Not a full re-audit and not a blind derivation.

## revision_3 / basis

| input | revision 2 | revision 3 | treatment |
| --- | --- | --- | --- |
| `returns.extended.yaml` | `dfc4f4e8f87fb919` | `fe73d1068cf136a3` | changed — the two policies touched are re-derived in full; the other three re-swept |
| `task_tools.py` | `7a0140a9b4173cc6` | `7a0140a9b4173cc6` | unchanged — `action_binding_and_uuids` still carried forward by reference |
| masked view `0.json` | `e19ab1baa4f7a24f` | `e19ab1baa4f7a24f` | **byte-identical — the world has not moved** |
| masked view `1.json` | `847d095ac85d0e1f` | `847d095ac85d0e1f` | **byte-identical — the world has not moved** |
| `tasks/0.json` / `tasks/1.json` | — | `e95ada1c754ef532` / `10cb1dd7d84b759b` | both match the brief; only the charter and the proof fields moved |

Gates re-run by the auditor: `EXTENDED OK`, `TASK TOOL CONTRACT OK`, `SOLVABILITY OK`, `COMPUTE OK`,
`GROUNDING OK`, `SCOPE OK`, `REPLAY OK` (`--check`), and **`TRACEABILITY OK`** — now runnable, 0.json
15 copied / 0 missing, 1.json 20 / 0, matching the brief. Task-file hashes verified byte-identical before
and after the run: **no auditor write this round.**

Render-layer reports read at `env/env_0005_consumer_electronics_retailer/audits/policy_kb/returns_and_restocking_desk/`
(`1.md`, the exchange-floor write-up). My reading of the defect matches theirs exactly, and the new
sentence states word for word the semantics that report says the visible materials failed to carry.

## revision_3 / calibration — why revision 2 missed this

I own the miss, and the shape of it matters. Revision 2's `rule_compute_equivalence` swept `compute_basis`
for **presence and verbatimness**: every binding had an entry, and every entry (bar one) was a verbatim
substring of its rule. `raw_difference` passed that sweep — it had an entry and the entry was verbatim.
What it did not have was an entry that carried the *operation the step performs*: it pointed at the
final-floor sentence while the step is a **mid-calculation** floor. My sweep asked "is this quoted?" and
never asked "does the quoted sentence say what this step does?". That is the gap, and a verbatim-substring
test cannot close it.

The corrected form of the check is what I ran this round and record below: enumerate every compute step
that performs a guard, a bound or a rounding, and ask of each whether its basis sentence states that
operation. I ran it over all five policies, not only the two that were edited. Its output is **N-8**.

## revision_3 / the five verification points

### 1. Are the added sentences genuinely sentences of the rules they are quoted from, and is `baseline.rule` still a subset of `rule`? — CLEAN

**`returns_ext_exchange_difference`** — one genuinely new sentence, sentence 3 of 33:

> "Where the price of the replacement going out is the same as or more than the price paid on the line, the
> drop is nothing rather than a negative figure, and the drop is held at nothing before the share of the
> drop is taken."

Verbatim in `rule` ✓ and verbatim in `baseline.rule` ✓. Its placement matches what it asserts about itself:
it sits immediately after the two sentences that define the drop and the replacement price (sentences 1–2)
and eleven sentences before the share step (sentence 14, "The share of the drop returned is then fixed by
how long the item was away from the shelf…"), so "before the share of the drop is taken" is where it
actually is.

**`returns_ext_restocking_fee_charge`** — not a new sentence but a trailing clause on the existing flat-fee
sentence (sentence 2 of 29), which now ends "…and the schedule's percentage minimum and percentage cap do
not bound it, **though the fee charged on that branch is never less than nothing**." Verbatim in `rule` ✓
and in `baseline.rule` ✓.

**`baseline.rule` ⊆ `rule`**: mechanically, every baseline sentence of both policies is verbatim in that
policy's own rule — 0 exceptions in either. The exchange baseline is sentences {1,2,3,4,5,6}; the fee
baseline is {1,2,3,4,6}.

**Nothing else moved in either rule**: sentence by sentence against the revision-2 dumps, every other
sentence is present, unaltered and in the same order. The exchange rule went 32 → 33 sentences (the one
addition) and the fee rule stayed at 29 (the one extended clause). The final-floor sentence of the
exchange rule — "The difference returned is never less than nothing and is rounded to the cent." — is
untouched, as the brief says.

### 2. Are the baselines still self-sufficient, and do they still yield the same definite fall-back numbers? — CLEAN

The risk the brief names is real in principle: a baseline that acquires a conditional can stop yielding one
number. It does not materialise here, because both added texts are **total, decidable conditions on figures
the baseline already names**, and each branch ends in a definite figure.

**Exchange baseline, derived from `baseline.rule` and `baseline.params: ['whole_drop_pct']` alone, on task
1's world:** the difference is the price paid times the units less the replacement price (1249.00 − ?); the
replacement price is the unit price on the most recent merchandise line for that stock number, **949.00**;
the new sentence asks whether the replacement is the same as or more than the price paid — 949.00 is less,
so the mid-floor does not engage and the drop is **300.00**; the whole of that drop is returned
(`whole_drop_pct` 100); the final floor and the rounding leave it; the schedule is not like-for-like.
→ **300.00**, one definite number, **identical to revision 2**, and machine substitution of every factor's
baseline into the compute agrees (300.00).

**Fee baseline, from `baseline.rule` and `baseline.params: [restocking_fee_pct, restocking_fee_min_usd,
restocking_fee_cap_usd, activated_device_fee_usd]` alone:** 10 per cent of 1249.00 × 1 = 124.90, inside the
9.95 minimum and the 199.00 cap; the flat-fee branch is not engaged because `activated_device_fee_usd` is
0.00 on this schedule, so the added clause is dormant; no no-fee ground applies.
→ **124.90**, one definite number, **identical to revision 2**, and machine substitution agrees.

**And no baseline moved on any other world either.** The only world where the added fee clause can engage
is one where a flat fee is charged, and there the baseline reads the flat fee — 45.00 on Activated Wireless
Device Return — with or without the clause, because a floor at nothing cannot bind a positive flat fee. The
only world where the added exchange sentence can engage is one where the replacement is dearer, and there
the baseline reads nothing either way (a 100-per-cent share of nothing is nothing, and the final floor
would have caught it in the baseline case).

`baseline.params` is unchanged in both policies and still sufficient: neither added text introduces a
figure — both are floors at nothing.

### 3. Does any added sentence collide with a prerequisite sentence? — CLEAN

Checked both added texts against all three of the charter's prerequisite sentences, in both directions:

| added text | vs slot-notice edge | vs relief edge | vs exchange edge |
| --- | --- | --- | --- |
| exchange mid-floor sentence | equal ✗, contains ✗, contained ✗ | ✗ ✗ ✗ | ✗ ✗ ✗ |
| fee flat-branch clause | ✗ ✗ ✗ | ✗ ✗ ✗ | ✗ ✗ ✗ |

Neither added text appears in any other policy's `rule`. The three prerequisite sentences are byte-unchanged
and each is still verbatim-locatable in its own blocked rule and absent from the depended-on rule. There is
no shared distinctive phrasing to confuse a text locator either: the prerequisite sentences turn on
"stands recorded against the return" and "stands charged against the return"; the added texts turn on the
drop against the replacement price, and on the flat-fee branch. The dependency layer is undisturbed.

### 4. Does the new sentence create a second reading, and can the mid-floor and the final floor both be read as governing the same step? — CLEAN, on four independent distinguishers

1. **Different subjects.** The new sentence governs **"the drop"**; the surviving sentence governs **"the
   difference returned"**. Sentence 1 defines them as distinct quantities — the difference returned *is* the
   price paid less the replacement price "and the whole of that drop is returned" — so the drop is the
   pre-share intermediate and the difference returned is what is paid out at the end.
2. **Each carries its own position.** The new sentence says "before the share of the drop is taken". The
   ordering sentence (sentence 9) pins the other one last: "…and the result is never less than nothing and
   is rounded to the cent". They are anchored to opposite ends of the declared order, each by its own text.
3. **The compute homes them disjointly.** `compute_basis.raw_difference` cites the new sentence and nothing
   else; `compute_basis.result` cites the final-floor sentence (with the like-for-like sentence that
   follows it, verbatim and adjacent in the rule) and nothing else. No binding cites both.
4. **Neither cross-reading survives its own text.** There is no reading on which the final-floor sentence
   governs `raw_difference`, because it names the difference *returned*, which sentences 1 and 9 tie to the
   end; and none on which the new sentence governs `result`, because its own clause excludes that.

**And the placement is load-bearing, which is the point of the fix.** On a world where the replacement is
dearer than the price paid — one unit at 300.00, the most recent merchandise line for that stock number at
340.00, the line's delivery charge at 149.00, everything else as seeded — the policy as computed yields
**55.76**, while the single-final-floor reading yields **41.12**. So the sentence documents a step that
genuinely changes the number, and the entailment the render auditor found missing is now available to a
document without inventing policy.

### 5. Did any scored value, baseline or factor sensitivity move? — NO

Recomputed all five computations from the round-3 charter on the byte-identical worlds, in topological
order, each on its own handling-time state:

| | revision 2 | revision 3 | same? |
| --- | --- | --- | --- |
| task 0 `booking_open_days` / baseline | 12 / 7 | **12 / 7** | same |
| task 0 `pickup_notice_days` / baseline | 6 / 2 | **6 / 2** | same |
| task 0 sensitivities (4 + 5) | 7,14,15,8 / 1,4,7,4,12 | **identical** | same |
| task 0 edge load-bearing | 1 | **1** | same |
| task 1 `restocking_fee_amount` / baseline | 116.48 / 124.90 | **116.48 / 124.90** | same |
| task 1 `waived_fee_amount` / baseline | 53.29 / 29.12 | **53.29 / 29.12** | same |
| task 1 `price_difference_amount` / baseline | 56.37 / 300.00 | **56.37 / 300.00** | same |
| task 1 sensitivities (6 + 4 + 6) | 91.50,141.46,199.00,81.48,102.43,136.48 / 75.13,35.82,39.31,35.53 / 52.57,242.06,41.87,71.36,60.12,119.56 | **identical** | same |
| task 1 edge load-bearing | 0.00 / 3.08 / 119.56 | **identical** | same |

**Neither new floor binds on either world**, as claimed: the exchange mid-floor is inactive because
`line_price` 1249.00 exceeds `replacement_price` 939.51, giving `raw_difference` 309.49; the fee's
flat-branch floor is not reached at all because `activated_device_fee_usd` is 0.00 on Standard Fifteen Day
Return, and on the percentage branch `fee_before_bounds` 116.48 sits above the 9.95 minimum.

**The reworker's decision not to write prose for the percentage branch is sound, and I verified it rather
than accepting it.** On that branch the floor is `MX(fee_before_bounds, restocking_fee_min_usd)`, and
`restocking_fee_min_usd` is a stated schedule figure that is ≥ 0 on every one of the six schedules
(9.95, 9.95, 45.00, 0.00, 0.00, 25.00). On the four where it is positive the stated minimum is strictly the
binding floor; on the two where it is 0.00 the stated minimum **is** the zero floor. So there is no
unstated floor on that branch on any schedule, and manufacturing prose for it would have added a sentence
with nothing behind it.

## revision_3 / structural re-sweep of the whole charter

Re-run because the charter moved: base section still byte-verbatim against the blueprint in all ten shared
sections; the three prerequisite edges unchanged and all four-point tests still passing; all eight
`overwrite` entries' superseded clauses still verbatim in their base rule and all replacements verbatim in
the extending rule; no rule names a tool, a policy id or a snake_case token; factor counts still 4/5/6/4/6
with ≥ 2 `parameter` and ≥ 1 `method` each and every ladder ≥ 3 tiers stated in full; all 25 factors still
load-bearing; scopes still pairwise disjoint and jointly complete.

**No new undeclared override.** The added exchange sentence bears on the base clause "where today's shelf
price is higher the customer pays the difference", which this policy's `overwrite` already names and
replaces; the sentence documents that already-declared deviation rather than creating a new one, so it
needs no `overwrite` entry of its own. The added fee clause sits inside the flat-fee sentence that
implements base `returns_restocking_fee` S4, which says nothing about a floor, and a floor at nothing
cannot bind a positive flat fee — no conflict.

## revision_3 / new findings

No red light. Two observations.

**N-7 — Observation (newly introduced): `compute_basis.bounded_fee` is not a verbatim substring of its
rule.** The entry concatenates a fragment of the ordering sentence — "and the result is held between the
schedule's minimum and its cap and rounded to the cent." — with the flat-fee sentence, in the **reverse**
of their order in the rule (the flat-fee sentence begins at character 199 of the normalised rule, the
fragment at character 1303). Both fragments are individually verbatim, and every quantity `bounded_fee`
computes is supported by one of them, so there is no consequence for any number on any world. It is
recorded because (a) it is a second instance of revision 2's **N-5** shape, now created rather than
inherited — the charter carries two such entries, this one and
`returns_ext_collection_booking_window.compute_basis.result` — and (b) it lands on precisely the field the
render auditor used to locate where a floor is homed, so a reader or a tool that resolves a basis by
substring match gets nothing back for the binding that carries the fee's bounds. Location:
`returns.extended.yaml`, `extended_policies[2].compute_basis.bounded_fee`.

**N-8 — Observation (pre-existing, from the corrected sweep): the residual of the class the render auditor
found.** Enumerating every compute step in all five policies that performs a guard, a bound or a rounding,
and asking of each whether its basis states that operation:

- **Every floor and cap in the charter is now carried by prose.** All eight `MX`/`MN` steps —
  `window_after_reissue`, `booking_window.result`, `notice_before_priority`, `slot_notice.result`,
  `fee_standing`, `relief.result`, `bounded_fee`, `raw_difference`, `exchange.result` — have a rule
  sentence that states the bound. Before this round, `raw_difference` did not. That part of the class is
  closed.
- **What remains uncarried is finer: five intermediate `RND(…, 2)` roundings** —
  `fee.points_addition`, `exchange.delivery_carried`, `exchange.carriage_deduction`,
  `exchange.points_restored_part`, `exchange.fee_held_back` — whose prose states the amount but states no
  rounding, the rule reserving "rounded to the cent" for the result. **None binds on either world**: I
  stripped every non-`result` `RND` and recomputed, and all five scored values are unchanged
  (12, 6, 116.48, 53.29, 56.37). `fee.points_addition` is the only one that moves its own intermediate
  (14.0475 → 14.05) and the final rounding absorbs it.
- The `or 0` / `or False` absence-defaults on the cross-category reads are likewise unstated, with the
  fall-through tiers ("In any other case nothing is added") carrying the business semantics.

Both are pre-existing and neither was introduced by this round's change. Recorded so the class stays on the
register rather than being assumed closed by the two fixes, and because a rounding that does not bind on
two worlds can bind on a third.

## revision_3 / verdict

| task | policy self-consistency | problem tree | factors bear weight | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | **PASS** |
| 1 | PASS | PASS | PASS | PASS | **PASS** |

The two added sentences are clean on all five points the brief asks about. Nothing regressed: every scored
value, every baseline and all 25 factor sensitivities are identical to revision 2, on worlds that are
byte-identical. No red light anywhere in this difficulty. **`returns_and_restocking_desk` remains closed at
the source layer**, now with `check_traceability` green as well, carrying **N-1** to **N-8** and the
standing blueprint-level observations **O-5**, **O-8**, **O-10**, **O-12** as observations. **N-7** should
go to whoever next touches the fee policy's `compute_basis`; **N-8** belongs with the render layer, since
an unstated intermediate rounding is exactly what it has to carry or omit.
