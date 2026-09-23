# Policy-task audit — trip_booking_and_settlement_desk / charter-global

## charter_global_frozen

- auditor: independent source-layer auditor (erl-task-policy-audit), revision 1
- freeze time (charter-global section): 2026-09-22, written before any task's GT fields were read
- frozen inputs and their hashes:
  - `env/env_0015_car_sharing_marketplace/tasks/trip_booking_and_settlement_desk/trips.extended.yaml`
    sha256 `6e48ab25930485361555f7d29139fc869c4ba37001c9dd66ef7c81002b1cd333` (16-prefix `6e48ab2593048536`, matches the brief)
  - `env/env_0015_car_sharing_marketplace/tasks/trip_booking_and_settlement_desk/task_tools.py`
    sha256 `d15df91eaeb2deac6ec10a4c00aa9a9b0ab75bebf2bf402ec6f51c9c25b69e32` (16-prefix `d15df91eaeb2deac`, matches the brief)
  - `env/env_0015_car_sharing_marketplace/blueprint/blueprint.yaml`, `blueprint/products/trips.yaml`,
    `blueprint/products/guestplan.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`
- fields permitted in this section: the whole extended charter (base copy + `extended_policies`), the
  task tool module, the blueprint products, the DB schema, the shared tool schemas.
- fields explicitly masked while this section was written: **every** field of
  `tasks/0.json` and `tasks/1.json` other than `frozen_time`, `user_scenario`, `initial_state` —
  i.e. `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`,
  `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure`,
  `db_closure_matches_initial_state`. Nothing derived from a revealed GT appears in this section.
- entry conditions: the brief supplied the instantiation-stage gate snapshot (check_extended,
  check_task_tools, replay_tasks --check, check_solvability, check_compute, check_grounding,
  check_cross_fire — all green) together with the two masked-view sha256 prefixes
  (`922f7f5e9518f8ce`, `bd41eb84345dc944`, both re-verified against the files on disk). The masked
  views were re-hashed by this auditor and match. Input is complete; no gate was re-run at this
  stage, and a green gate is taken as the qualification to audit, not as proof of correctness.
- previous revisions: none. `env/env_0015_car_sharing_marketplace/audits/policy_task/trip_booking_and_settlement_desk/`
  did not exist before this round.

### policy_conflict_scan

The charter in force for category `trips` at this difficulty is: the base section of
`trips.extended.yaml` lines 1–1058, which `diff` shows is **byte-identical** to
`blueprint/products/trips.yaml` lines 1–1058 (the only added lines are 1059–1062, a blank line and
a three-line comment banner introducing `extended_policies`); plus four extended policies.

Base copy verbatim: **PASS**. The base section has not been rewritten.

Four extended policies, their claimed surfaces:

| id | subject | computes | target_tool | base_policy_refs | overwrite |
| --- | --- | --- | --- | --- | --- |
| `trips_ext_mileage_topup_grant` | `trips_mileage_allowance_granted` | `granted_miles` | `grant_mileage_topup_0373887d` (owner=agent) | `trips_evt_mileage_allowance` | 1 declared |
| `trips_ext_mileage_topup_pricing` | `trips_reservation_charge_posted` | `purchase_amount` | `pay_for_mileage_topup_d571ad94` (owner=user) | `trips_evt_reservation_pricing`, `trips_evt_payment_recovery` | `[]` |
| `trips_ext_young_driver_surcharge` | `trips_reservation_charge_posted` | `surcharge_amount` | `post_young_driver_surcharge_8e3312c3` (owner=agent) | `trips_evt_reservation_pricing`, `trips_evt_payment_recovery` | `[]` |
| `trips_ext_extension_quote` | `trips_extension_charge_posted` | `quoted_amount` | `submit_extension_request_8f69bfd6` (owner=user) | `trips_evt_extension` | `[]` |

Overlapping subjects, triggers, eligibility, time anchors, action parameters, terminal states:

- **Subject overlap `trips_reservation_charge_posted`** is claimed by two extended policies
  (`..._topup_pricing`, `..._young_driver_surcharge`) and by base `trips_evt_reservation_pricing`.
  They are separated by `charge_basis` on the row each tool writes
  (`extra_miles_package` vs `young_driver_surcharge`, task_tools.py:76, :113) and by `computes`
  (`purchase_amount` vs `surcharge_amount`). No collision on the scored quantity. **PASS.**
- **Eligibility inherited and not weakened.** Base `booking_open_for_pricing`
  (trips.yaml:710–722, `trips_bookings.status ∈ {requested, booked, in_progress}`) binds both
  `trips_reservation_charge_posted` writers; base `allowance_window_open` (trips.yaml:746–758,
  `status ∈ {booked, in_progress, completed}`) binds the grant. No extended policy, tool body or
  persona weakens either. **PASS.**
- **Time anchors.** No extended policy declares a temporal_basis of its own; the base anchors
  (`host_acceptance_window`, `free_window_elapsed`, `extension_decision_window`) are untouched.
  See finding F-06 for the one place where a base time anchor and an extended rule sentence speak
  about the same act.
- **Cross-category read boundary.** Three of the four policies declare `cross_category: [{category:
  guestplan, as: branch, ...}]` and read only through `CFIELD`/`XSUM` on `guestplan_elections` /
  `guestplan_charges`; `inputs.cross_category: [guestplan]` agrees in each. `trips_ext_mileage_topup_grant`
  declares `cross_category: []` and its compute uses no cross primitive. **PASS** — declared exactly.
- **Terminal states.** Each target tool writes exactly one row into exactly one table and mutates
  nothing else (task_tools.py:38–42, 72–78, 109–114, 153–157). No two policies claim the same
  terminal row. **PASS.**
- **Scope exclusivity of the M tasks.** Task 0's problem tree is
  `{trips_ext_mileage_topup_pricing (root) ← trips_ext_mileage_topup_grant}`; task 1's is
  `{trips_ext_extension_quote (root) ← trips_ext_young_driver_surcharge}`. The two sets are
  pairwise disjoint and jointly exhaust the four extended policies. **PASS.**
  (The tree membership here is the auditor's own pre-reveal derivation from the `prerequisite`
  field and the two personas; it is compared against the declared closures in each task file.)

### rule_compute_equivalence

Check 2 run over all four extended policies, sentence of `rule` ↔ `compute_basis` quotation ↔
restricted expression in `compute`, and swept back binding by binding.

`trips_ext_mileage_topup_grant` (lines 1098–1157): 22 compute bindings, every one carrying a
`compute_basis` quotation that is a verbatim substring of the `rule`. Quantities checked and found
equivalent in both directions: the block quantum and its ladder; the shortfall formula
(`MX(0, days_covered * daily_allowance - miles_unused + reserve_miles)` ↔ "the daily included-mile
measure multiplied by the days … still to run, less the included miles … still has unused, with the
top-up reserve added; where that figure comes out at nothing or less, the top-up must cover
nothing"); the ceiling of blocks (`MX(1, -(-shortfall // block_size))` ↔ "the smallest whole number
of blocks that cover … and never fewer than one block"); the headroom cap and the whole-mile floor
(`int(MN(granted_raw, headroom))` ↔ "held down to the room left … miles are granted as whole miles
with no part mile granted"); the three day-counting conventions of `days_covered` (return day
counted / counted / left out); the three `miles_unused` bases. **PASS.**

`trips_ext_mileage_topup_pricing` (lines 1295–1355): 17 bindings, all quoted. The rounding point
("rounded to the nearest cent once at the end") is implemented once at `result`, with an inner
`RND` only inside `line_price`, which the rule licenses by naming the line price as its own
quantity. The floor ("taken as nothing where that comes out below nothing") is `MX(0, ...)`.
**PASS.**

`trips_ext_young_driver_surcharge` (lines 1470–1524): 17 bindings, all quoted. The percentage-point
arithmetic ("each of them in percentage points and all of them added together to the rate before
the rate is taken on anything") is implemented as
`effective_rate = MX(0, surcharge_rate + protection_adjustment + conduct_adjustment + driver_adjustment)`
and `result = RND(effective_rate/100 * charged_base, 2)`; the "where that leaves a rate below
nothing, no surcharge is owed" floor is the `MX(0, …)`. The acting base ("the base-rate line
standing on the reservation spread evenly over the days of the reserved period and taken for each
day charged") is `daily_base` × `days_charged`, with the intermediate rounded to the cent — the rule
does not name that intermediate rounding, but it names the quantity ("spread evenly … and taken for
each day charged"), and on both a two-step and a one-step reading of this world the figure is the
same. **PASS.**

`trips_ext_extension_quote` (lines 1639–1707): 20 bindings, all carrying a quotation — but one of
them, `modification_fee`, implements a condition the `rule` nowhere states. See **finding F-05**.
Everything else is equivalent in both directions. **FAIL on one binding.**

Sweep back (does `compute` invent a basis, does the `rule` make an empty promise): the only
invented basis is F-05. The only sentence of a `rule` that promises something the compute never
delivers is the opening sentence of `trips_ext_mileage_topup_grant` — "A guest who asks for more
included miles part way through a reservation **is granted** a top-up of included miles" — which the
same rule's own ceiling clause can reduce to zero miles; see **observation O-01**.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: `(grant_mileage_topup_0373887d, granted_miles)`,
  `(pay_for_mileage_topup_d571ad94, purchase_amount)`,
  `(post_young_driver_surcharge_8e3312c3, surcharge_amount)`,
  `(submit_extension_request_8f69bfd6, quoted_amount)`. Each pair is claimed by exactly one policy,
  and no tool appears in two policies. **PASS.**
- uuid8 tails: `0373887d`, `d571ad94`, `8e3312c3`, `8f69bfd6`. Four distinct 8-hex tails, no shared
  prefix, no shared suffix, no arithmetic or lexical sequence, no tail that is another with a changed
  last character, none derivable from a counter. Each is frozen with its tool name in the module.
  **PASS.**
- Docstrings: none names another tool, none states this action's position relative to another
  problem's write, none carries a confirmation/review/wait step outside the policy. The words
  "before"/"After" do occur, but only in two places, both of which are about the call itself and not
  about a sequence of business actions — the argument-provenance phrase "read from the trip booking
  lookup before the call" (task_tools.py:25, :59, :96, :134) and the effect phrase "After the call
  the reservation's mileage record carries the added miles" (task_tools.py:18, :53, :90, :127).
  Neither locates the write among the other problems of a tree. Recorded as **observation O-02**
  rather than a red light, because no consequence follows from either.
- No tool body judges eligibility, aggregates history or prices anything: each body is one
  `ctx.make_id` plus one `ctx.create` plus a confirmation string (task_tools.py:38–44, 72–80,
  109–116, 151–159). **PASS.**

### prerequisite_graph

Check 7 over the whole `prerequisite` graph.

| blocked policy | `problem` | `kind` | `gate` | `form` | `fallback_reason` | `resolved_by` |
| --- | --- | --- | --- | --- | --- | --- |
| `trips_ext_mileage_topup_grant` | — (`prerequisite: []`, line 1111) | | | | | |
| `trips_ext_mileage_topup_pricing` | `trips_ext_mileage_topup_grant` | `value_input` | `granted_miles` | `state` | absent (correct for state form) | `grant_mileage_topup_0373887d` |
| `trips_ext_young_driver_surcharge` | — (`prerequisite: []`, line 1481) | | | | | |
| `trips_ext_extension_quote` | `trips_ext_young_driver_surcharge` | `value_input` | `yd_share` | `state` | absent (correct) | `post_young_driver_surcharge_8e3312c3` |

- `prerequisite` is filled in on all four policies (`[]` where there is none). **PASS.**
- Every `problem` points at another policy id present in this file, never at a base policy, never at
  itself. **PASS.**
- The graph is two disjoint single edges, `grant → pricing` and `young_driver → extension_quote`.
  Acyclic, and no cross-task reference creates a cycle. **PASS.**
- `form: state` on both edges, `fallback_reason` absent on both — correct, since `fallback_reason` is
  required exactly on action-form edges. **PASS.**
- `kind: value_input` on both; the named `gate` is in each case a real binding of the blocked
  policy's own `compute` (`granted_miles` at line 1323; `yd_share` at line 1679), not an eligibility
  flag. **PASS.**
- `resolved_by` is the depended-on policy's `target_tool` in both cases, and the tool genuinely
  changes the binding: `grant_mileage_topup_0373887d` writes a `trips_usage` row with
  `event_type='trips_mileage_allowance_granted', grant_reason='purchased_package'`
  (task_tools.py:39–42), which is exactly the filter `granted_miles` sums;
  `post_young_driver_surcharge_8e3312c3` writes a `trips_charges` row with
  `charge_basis='young_driver_surcharge'` (task_tools.py:110–114), which is exactly the filter
  `surcharge_line` sums and `yd_share` is built from. **PASS.**
- `condition` neither strengthened nor weakened relative to the sentence: see next section.

### prerequisite_sentences

Check 6, both edges, four-point test.

**Edge 1 — `trips_ext_mileage_topup_pricing` → `trips_ext_mileage_topup_grant`.**
`policy_source` (line 1310–1311): *"The price of a mileage top-up is fixed only after the miles it
adds stand on the reservation's included-mile record."*

1. Verbatim in the blocked policy's **own** `rule`: yes, line 1296, second sentence.
2. Ordering connective joining this policy's own result to what it waits on: "**only after**". The
   result is "the price of a mileage top-up"; the thing waited on is "the miles it adds stand on the
   reservation's included-mile record". **PASS.**
3. Declared `form: state`, and the sentence is in the state form: what it waits on is a
   record-visible state ("the miles … stand on the reservation's included-mile record"), named in
   the words the tables and the finder use — `find_trips_usage` is documented as returning "the
   included miles granted at booking, at extension or **by a purchased package**"
   (share_tools.py:107–112). No action, no performer, no tool, no policy id, no snake_case token, no
   row id. **PASS.**
4. Strength and scope: the edge's `condition` is "the reservation's mileage record carries a
   purchased top-up grant whose miles are the miles this purchase is being priced for" — exactly the
   state the sentence names, neither broader nor narrower. **PASS.**

State-form single-write test: exactly one write of this difficulty brings that state about —
`grant_mileage_topup_0373887d` is the only tool in the module that creates a
`trips_mileage_allowance_granted` row, and the only one that sets
`grant_reason='purchased_package'`. No second candidate. **PASS.**

Single-reading derivation (prerequisite sentence + records + the depended-on rule → the resolving
action): the sentence says the price is fixed only after the added miles stand on the mileage
record. A reader queries `find_trips_usage(booking_id=…)`; if no row with a purchased top-up grant
is there, the state does not hold. The reader then asks which policy's own rule describes the write
that puts one there, and finds `trips_ext_mileage_topup_grant`, whose rule opens "A guest who asks
for more included miles part way through a reservation is granted a top-up of included miles"
(line 1099) and whose `target_tool` is the grant tool. One reading, no second candidate.

**Edge 2 — `trips_ext_extension_quote` → `trips_ext_young_driver_surcharge`.**
`policy_source` (line 1654–1655): *"A quote for extra time is not fixed before the reservation
carries the young-driver surcharge owed on the driver named on it."*

1. Verbatim in the blocked policy's own `rule`: yes, line 1640, second sentence.
2. Ordering connective: "**not … before**". Result: "a quote for extra time". Waited on: "the
   reservation carries the young-driver surcharge owed on the driver named on it". **PASS.**
3. `form: state`, state form honoured: "the reservation carries the young-driver surcharge" is a
   record-visible state over `trips_charges`, whose finder is documented to return the trip's priced
   lines and "what it was priced on" (share_tools.py:84–105). No action word, no tool, no snake_case,
   no id. **PASS.**
4. Strength/scope: `condition` is "a young-driver surcharge line stands among the priced lines of the
   reservation the extra time is quoted on" — the same state, same scope. **PASS.**

State-form single-write test: `post_young_driver_surcharge_8e3312c3` is the only tool in the module
that writes `charge_basis='young_driver_surcharge'`. **PASS.**

Single-reading derivation: the sentence says the quote is not fixed before the surcharge line
stands. A reader queries `find_trips_charges(booking_id=…)`; with no such line the state fails. The
reader looks for the policy whose own rule describes raising it, and finds
`trips_ext_young_driver_surcharge`, rule line 1471: "A driver under the young-driver threshold on
the first day of the reserved period **owes the young-driver surcharge on the reservation, raised as
its own priced line**". One reading.

**Nothing else about either dependency is written anywhere it should not be.** Neither blocked rule
carries a second wording of its edge, a tool name, a route or another policy's id; neither
depended-on rule (`trips_ext_mileage_topup_grant` line 1098–1110,
`trips_ext_young_driver_surcharge` line 1470–1480) restates the sentence or mentions the blocked
policy. **PASS.**

**Cross-problem orders in a rule that ground no declared edge.** Swept all four extended rules and
all thirteen base rules. In the extended set there is none beyond the two above. In the base set,
`trips_settlement` (trips.yaml:1006) states "Settlement is performed once every end-of-trip line
that can arise has been posted or ruled out" and `trips_evt_mileage_overage` (trips.yaml:774) states
"Mileage is settled once, at the end of the trip, against the allowance standing on the reservation
at that moment, including any miles granted by an extension or bought mid-trip" — both are
base-rule cross-problem orders. Neither task's tree rests on either (neither `trips_settlement` nor
`trips_evt_mileage_overage` is a node of either tree, and neither is a base policy an edge may point
at), so per check 6 these are recorded as **observation O-03** rather than as a red light.

### override_declarations

Check 1's finding half, run once, sentence by sentence against each `base_policy_refs` entry of each
extended policy. The criterion applied throughout is "the quantity that ultimately gets scored".

**`trips_ext_mileage_topup_grant` vs `trips_evt_mileage_allowance` (trips.yaml:736–770).**
Sentence by sentence:

| base sentence (trips.yaml) | extended treatment |
| --- | --- |
| :739 "Included miles are granted to the reservation rather than to the guest: the plan's daily allowance multiplied by the reserved days, **capped at the plan's per-booking ceiling however long the reservation runs**." | **handled differently, not declared** — see **F-01** |
| :740 "An approved extension grants further miles at the plan's extension allowance for each extended day…" | untouched; the extended policy prices no extension grant |
| :741 "A guest may buy further miles in whole packages only; part packages are not sold…" | **declared** in `overwrite` (lines 1066–1071), replaced by "A top-up of included miles is granted in whole blocks, the standard block being five hundred miles." Correctly declared. |
| :742 unlimited-mileage clause | inherited; neither task's plan offers it at its value class |
| :743 "A telematics reading is authoritative where one exists…" | inherited; the extended policy reads `usage_source` but never overrides authority |
| :744 "Allowance records are written only while the reservation is in the booked, in_progress or completed state" | inherited in full |

**`trips_ext_mileage_topup_pricing` vs `trips_evt_reservation_pricing` (trips.yaml:699–735)** —
every base sentence there governs a different line (base rate, trip fee, young-driver surcharge,
delivery, deposit); the one that binds is :708 "a line is posted only while the reservation is in the
requested, booked or in_progress state", inherited in full. **No conflict on this ref.**
**vs `trips_evt_payment_recovery` (trips.yaml:1042–1058)** — retries, late-payment fee, unpaid-balance
bar; none governs the price of a mileage purchase. **No conflict on this ref.**
But the quantity this policy scores *is* governed by base parameters that no `overwrite` names —
`extra_miles_package_price` / `extra_miles_package_size_miles`, carried on
`trips_evt_mileage_allowance`'s `per_tier` block, whose sentence-level clause was superseded by the
grant policy while the price was not. See **F-02**.

**`trips_ext_young_driver_surcharge` vs `trips_evt_reservation_pricing`.** Sentence :705 —
"A driver under the young-driver threshold on the first day of the reserved period pays the
young-driver surcharge **on the discounted base rate**, posted as its own line so that it can be
reversed on its own if the driver's age is later corrected." The extended policy computes the same
scored quantity by a different rate and a different acting base, with `overwrite: []`. See **F-03**.
Base :708 (posting state) is inherited in full.
**vs `trips_evt_payment_recovery`** — no sentence governs the surcharge amount. No conflict.

**`trips_ext_extension_quote` vs `trips_evt_extension` (trips.yaml:926–966).**

| base sentence | extended treatment |
| --- | --- |
| :929 request goes on the register, reservation moves only on host approval | followed |
| :930 lead time; **"The extension is priced only where the host's decision is recorded no later than the decision window…"** | see **O-04** |
| :931 "One extension may not add more than the plan's maximum additional hours…" | followed for the tasks' plans |
| :932 "**Extended time is priced at the locked daily rate lifted by the plan's uplift percentage**, applied to the extended days only" | **handled differently, not declared** — see **F-04** |
| :933 extension mileage allowance; no second trip fee | followed (no trip fee is added) |
| :934 declined/expired request leaves the reservation untouched | followed |

The extended quote also adds a "date-change fee" of its own, a quantity base carries as
`modification_fee_amount` / `modification_free_changes_count` on `trips_evt_payment_recovery`, which
this policy does not list in `base_policy_refs` at all. See **F-05b**.

### factor_ladders

Structure only. Whether a factor bears weight is a fact about one world and lives in that task's
`factor_weight`.

| policy | factors | `parameter` | `method` | multi-source tiers | `cross_difficulty` |
| --- | --- | --- | --- | --- | --- |
| `..._topup_grant` | 6 | 4 | 2 | all 6 ladders: every non-fall-through tier is a conjunction over ≥2 distinct records | none |
| `..._topup_pricing` | 5 | 4 | 1 | 3 of 5 (`volume_concession_tier`, `line_price_basis`, `reading_handling_charge`); `protection_block_price` t1 is a conjunction over the election row and the guestplan ledger; `early_purchase_credit` t1/t2 conjoin booking dates and the usage ledger | `protection_block_price` → `guestplan` |
| `..._young_driver_surcharge` | 5 | 4 | 1 | `secured_period_rate`, `protection_level_adjustment`, `allowance_conduct_adjustment`, `declared_driver_adjustment` | `protection_level_adjustment` → `guestplan`; `declared_driver_adjustment` → `guestplan` |
| `..._extension_quote` | 5 | 3 | 2 | `lapsed_request_uplift`, `quoted_time_selection`, `young_driver_share_basis`, `extended_day_protection_charge` | `extended_day_protection_charge` → `guestplan` |

- **Counts.** Every policy declares 4–6 factors with ≥2 `parameter` and ≥1 `method`. **PASS.**
- **Per task.** Task 0's computations carry ≥1 multi-source factor (six of them, in the grant alone)
  and ≥1 `cross_difficulty` (`protection_block_price`). Task 1's carry ≥1 multi-source
  (`secured_period_rate` among others) and ≥1 `cross_difficulty` (`protection_level_adjustment`,
  `declared_driver_adjustment`, `extended_day_protection_charge`). **PASS.**
- **`decides` is an input, never `result`.** All 21 `decides` values are intermediate bindings
  (`miles_unused`, `days_covered`, `daily_allowance`, `block_size`, `mile_ceiling`, `reserve_miles`,
  `block_price`, `concession`, `line_price`, `handling_charge`, `early_credit`, `surcharge_rate`,
  `protection_adjustment`, `conduct_adjustment`, `driver_adjustment`, `days_charged`, `uplift`,
  `extra_hours`, `yd_share`, `modification_fee`, `protection_day`). **PASS.**
- **Binding sets disjoint within each policy.** Checked element by element for all four policies; no
  binding name appears in two factors' `bindings` of the same policy. **PASS.**
- **Three tiers each, fall-through counted.** All 21 ladders have exactly three tiers. **PASS.**
- **No two tiers of one ladder select the same value or method.** Checked all 21:
  175/150/125 · 900/750/500 · 8000/4500/3750 · 800/400/0 · 125/165/145 · 15/8/0 · 0/12/6 · 40/20/0 ·
  9/18/15 · −4/+5/0 · 3/1/0 · 4/2/0 · 4/12/8 · 35/18/0 · 14/9/0, and the six `method` ladders each
  name three textually and operationally distinct algorithms. **PASS.**
- **Every tier stated in the `rule` and implemented in `compute`.** True for 20 of 21 ladders. The
  exception is `date_change_fee_tier`, whose `compute` branch carries a conjunct absent from both the
  `rule` sentence and the ladder — **F-05**.
- **Labels honest.** Every `method` factor's tiers change the algorithm, not a number
  (`unused_miles_basis` swaps the holding field for a ledger reconstruction and then for a
  decayed reconstruction; `covered_period_anchor` and `charged_days_anchor` swap the day-count
  anchor and the inclusive/exclusive convention; `line_price_basis` swaps per-mile apportionment for
  whole-blocks-only for ceiling-of-blocks; `quoted_time_selection` swaps which register row supplies
  the hours; `young_driver_share_basis` swaps per-extended-day for one-day for nothing). Every
  `parameter` factor's tiers substitute a number into an unchanged formula. No `method` tier names a
  computation rule the charter does not state. **PASS.**
- **Conditions and outcomes ones that line of business actually holds.** Reviewed tier by tier. The
  conditions are all things a car-sharing marketplace weighs when settling these quantities (how far
  through the trip the guest is, how many odometer readings have been booked and how recent, how
  long the reservation is, whether a deposit was taken, what protection the guest elected and what
  it has cost, how many extra drivers are on the trip, whether a prior extension request expired or
  was refused), and none of them holds of every customer who reaches the write. The outcomes — block
  sizes of 500/750/900 miles, per-block prices of $125/$145/$165, handling of $0/$6/$12, credits of
  $0/$20/$40, surcharge rates of 9/15/18 per cent, adjustments of ±1 to ±5 points, date-change fees
  of $0/$18/$35, protection of $0/$9/$14 a day — are all treatments such a marketplace would
  publish. **PASS**, with the single reservation recorded as **O-01** (the topup-grant baseline's
  published outcome on a Monthly reservation is "no miles at all", which reads as a refusal rather
  than a default).
- **Tiers pairwise disjoint as stated.** 19 of 21 are. Two are not — `protection_block_price` and
  `protection_level_adjustment` — recorded as **observation O-05**, because neither task's world
  realises the overlap and no consequence can therefore be demonstrated.

### findings

---

**F-01 — SOURCE-POLICY RED — undeclared override of the per-booking included-mile ceiling.**

*Symptom.* Base and extended give different answers to "how many included miles may this reservation
accumulate", and the extended answer is not declared as an override.

*Root cause.* `trips_ext_mileage_topup_grant` lists `trips_evt_mileage_allowance` in
`base_policy_refs` (line 1065) and declares exactly one `overwrite` entry (lines 1066–1071), naming
the *package-purchase* sentence. The *ceiling* sentence of the same base policy is left standing and
is then contradicted by the factor `included_mile_ceiling_tier`.

*Evidence.* Base, `blueprint/products/trips.yaml:739`:

> "Included miles are granted to the reservation rather than to the guest: the plan's daily
> allowance multiplied by the reserved days, **capped at the plan's per-booking ceiling however long
> the reservation runs**."

with `parameter_schema` (trips.yaml:47) "`included_miles_cap_per_booking`: Ceiling on the included
miles one booking **can accumulate**, in miles" and, for the Keyturn Monthly Rate Plan,
`included_miles_cap_per_booking: 3750` (trips.yaml:214).

Extended, `trips.extended.yaml:1109`:

> "Where the reserved period runs for sixty days or more and no mileage overage has been charged on
> the reservation, the included-mile ceiling is **eight thousand** miles; where the reserved period
> runs for sixty days or more and a mileage overage has been charged on the reservation, the
> included-mile ceiling is **four thousand five hundred** miles; in every other case the
> included-mile ceiling is the standard one."

The base sentence's clause "however long the reservation runs" is the explicit refusal of exactly
the exception the extended tier introduces, so the two cannot both be in force. `overwrite` does not
name this sentence.

*Demonstrated consequence.* Demonstrated on task 0's own world in
`env/env_0015_car_sharing_marketplace/audits/policy_task/trip_booking_and_settlement_desk/0.md`,
§`policy_self_consistency`: the two readings give **3600 miles and $814.40** against **0 miles and
$0.00**. Task 1 does not touch either policy, so this finding does not bear on it.

*Affected artifact and location.* `tasks/trip_booking_and_settlement_desk/trips.extended.yaml`,
policy `trips_ext_mileage_topup_grant`, `overwrite` (lines 1066–1071), `params.ceiling_long_clean` /
`ceiling_long_charged` (lines 1084–1085), `rule` line 1109, factor `included_mile_ceiling_tier`
(lines 1219–1233). Bears on task 0 only.

*Relation to previous revisions.* New; revision 1.

---

**F-02 — SOURCE-POLICY RED — undeclared override of the published price of a block of extra miles.**

*Symptom.* Base and extended price the same purchase — a block of extra included miles on a Keyturn
Monthly reservation — differently, and the deviation is declared nowhere.

*Root cause.* `trips_ext_mileage_topup_pricing` has `overwrite: []` (line 1267) and does not list
`trips_evt_mileage_allowance` in `base_policy_refs` (line 1266), although that base policy is where
the marketplace publishes the price of a block of extra miles. The grant policy's declared
`overwrite` supersedes only the base *grant* sentence and says nothing about price, so the base
price provision is inherited in full and may not be weakened.

*Evidence.* Base, `blueprint/products/trips.yaml:52`: "`extra_miles_package_price`: Price of one
block of extra miles, in USD", with the Keyturn Monthly Rate Plan value
`extra_miles_package_price: 145.00` and `extra_miles_package_size_miles: 500` (trips.yaml:215), both
carried into the policy through `trips_evt_mileage_allowance.params.per_tier` (trips.yaml:765).
Extended, `trips.extended.yaml:1300`: "…the block price is **one hundred and twenty-five dollars**;
…the block price is **one hundred and sixty-five dollars**; in every other case the block price is
the standard one", with `block_price_standard: 145.00` (line 1273) matching base and
`block_price_corporate: 125.00` / `block_price_unprotected: 165.00` (lines 1274–1275) departing from
it.

*Demonstrated consequence.* Demonstrated on task 0's world in `0.md` §`policy_self_consistency`:
holding everything else at the extended reading and substituting only the base's published price,
the scored `purchase_amount` moves from **$814.40** to **$958.40**.

*Affected artifact and location.* `trips.extended.yaml`, policy `trips_ext_mileage_topup_pricing`,
`base_policy_refs` line 1266, `overwrite` line 1267, `params` lines 1273–1275, `rule` line 1300,
factor `protection_block_price` (lines 1357–1371). Bears on task 0 only.

*Relation to previous revisions.* New; revision 1.

---

**F-03 — SOURCE-POLICY RED — undeclared override of the young-driver surcharge rate and its acting base.**

*Symptom.* Base and extended compute the scored `surcharge_amount` by a different rate and on a
different base, with `overwrite: []`.

*Root cause.* `trips_ext_young_driver_surcharge` names `trips_evt_reservation_pricing` in
`base_policy_refs` (line 1447) — the base policy that states how the young-driver surcharge is
arrived at — and declares no override of it (line 1448).

*Evidence.* Base, `blueprint/products/trips.yaml:705`:

> "A driver under the young-driver threshold on the first day of the reserved period pays the
> young-driver surcharge **on the discounted base rate**, posted as its own line so that it can be
> reversed on its own if the driver's age is later corrected."

with `parameter_schema` (trips.yaml:84) "`young_driver_surcharge_percent`: Surcharge **on the base
rate** for drivers under the young-driver threshold, as a percentage" and, for the Keyturn Weekly
Rate Plan, `young_driver_surcharge_percent: 15` (trips.yaml:201).

Extended, `trips.extended.yaml:1472–1479`: the surcharge is "the effective surcharge rate taken on
the amount charged over", the amount charged over is "the base-rate line … **spread evenly over the
days of the reserved period and taken for each day charged**", and the rate is 9 or 18 per cent by
tier (line 1476) moved by protection, conduct and additional-driver adjustments of −4 to +5
percentage points (lines 1477–1479).

*Demonstrated consequence.* Demonstrated on task 1's world in
`env/env_0015_car_sharing_marketplace/audits/policy_task/trip_booking_and_settlement_desk/1.md`,
§`policy_self_consistency`: base gives **$162.62**, extended gives **$86.73**, and because the root
problem consumes the surcharge line the root's scored value moves from **$241.43** to **$252.27**.
Task 0 does not touch this policy.

*Affected artifact and location.* `trips.extended.yaml`, policy `trips_ext_young_driver_surcharge`,
`overwrite` line 1448, `rule` lines 1471–1480, `params.rate_long_secured` / `rate_long_unsecured`
(lines 1455–1456) and the adjustment params (lines 1457–1465). Bears on task 1 only.

*Relation to previous revisions.* New; revision 1.

---

**F-04 — SOURCE-POLICY RED — undeclared override of the extension uplift.**

*Symptom.* Base and extended lift the locked daily rate by different percentages for the same
extended time, with `overwrite: []`.

*Root cause.* `trips_ext_extension_quote` names `trips_evt_extension` in `base_policy_refs`
(line 1618) and declares no override (line 1619), while its `lapsed_request_uplift` factor replaces
the plan's published uplift with a two-tier ladder.

*Evidence.* Base, `blueprint/products/trips.yaml:932`: "Extended time is priced at the locked daily
rate lifted by **the plan's uplift percentage**, applied to the extended days only", with
`parameter_schema` (trips.yaml:71) "`extension_rate_uplift_percent`: Uplift applied to the daily
rate for extended time, as a percentage" and, for the Keyturn Weekly Rate Plan,
`extension_rate_uplift_percent: 8` (trips.yaml:197). Extended, `trips.extended.yaml:1644`: "…the
extension uplift is **four per cent**; … the extension uplift is **twelve per cent**; in every other
case the extension uplift is the standard one", with `uplift_standard: 8` (line 1625) matching base
and `uplift_repeat: 4` / `uplift_declined: 12` (lines 1626–1627) departing from it.

*Demonstrated consequence.* Demonstrated on task 1's world in `1.md` §`policy_self_consistency`:
the scored `quoted_amount` moves from **$241.43** (extended, uplift 4 %) to **$248.47** (base,
uplift 8 %). Task 0 does not touch this policy.

*Affected artifact and location.* `trips.extended.yaml`, policy `trips_ext_extension_quote`,
`overwrite` line 1619, `params` lines 1625–1627, `rule` line 1644, factor `lapsed_request_uplift`
(lines 1709–1723). Bears on task 1 only.

*Relation to previous revisions.* New; revision 1.

---

**F-05 — SOURCE-POLICY RED — `compute` carries a condition on the date-change fee that no `rule`
sentence and no ladder tier states.**

*Symptom.* For the same reservation, the prose of the policy and the executable binding that
implements it select different date-change fees.

*Root cause.* The `modification_fee` branch in `compute` conjoins a "seven days" test onto each tier;
the `rule` sentence that `compute_basis` quotes for that binding, and the factor ladder
`date_change_fee_tier` that declares it, both state the tiers without it.

*Evidence.* `trips.extended.yaml:1681` (`compute`):

> `modification_fee: "K('modification_fee_repeat') if (change_count >= 2 and days_run_b >= K('week_days')) else (K('modification_fee_first') if (change_count == 1 and days_run_b >= K('week_days')) else K('modification_fee_none'))"`

`trips.extended.yaml:1647` (`rule`) and `:1702` (`compute_basis`, verbatim the same sentence):

> "Where two or more extension requests already stand on the reservation, the date-change fee is
> thirty-five dollars; where one extension request already stands on the reservation, the
> date-change fee is eighteen dollars; in every other case no date-change fee is charged."

`trips.extended.yaml:1758–1764` (`date_change_fee_tier.ladder`): the three `when` strings are
"two or more extension requests already stand on the reservation", "one extension request already
stands on the reservation", "otherwise" — no seven-day conjunct.

*Demonstrated consequence.* The two faces reach different conclusions in the same situation: on a
reservation carrying one standing extension request where the trip has run five days, the `rule` and
the ladder award the guest a date-change fee of **$18.00** while `compute` awards **$0.00**. Every
tier the ladder names is therefore not a branch of the `decides` binding, which is check 2's own
failure condition. On task 1's world the conjunct happens to be satisfied
(`days_run_b = 11 ≥ 7`), so the defect does not move that task's scored number — recorded honestly
in `1.md` §`policy_self_consistency`, which cites this finding rather than restating it.

*Affected artifact and location.* `trips.extended.yaml`, policy `trips_ext_extension_quote`,
`compute` line 1681 against `rule` line 1647 / `compute_basis` line 1702 / factor
`date_change_fee_tier` lines 1754–1768. Bears on task 1.

*Relation to previous revisions.* New; revision 1.

---

**F-05b — SOURCE-POLICY RED — the date-change fee is charged against a base provision the policy
neither cites nor overrides.**

*Symptom.* The marketplace's published terms for changing the dates of a confirmed booking and the
extended quote's date-change fee give different money for the same act, with nothing declared.

*Root cause.* `trips_ext_extension_quote` charges a quantity base already governs, while listing
only `trips_evt_extension` in `base_policy_refs` (line 1618) and declaring `overwrite: []`
(line 1619). The base provision is therefore inherited in full and is then contradicted.

*Evidence.* Base `parameter_schema` (trips.yaml:93–94): "`modification_fee_amount`: Fee for changing
the dates of a confirmed booking **once the free changes are used**, in USD" and
"`modification_free_changes_count`: Date changes allowed on one booking before the modification fee
applies", carried into `trips_evt_payment_recovery.params.per_tier` (trips.yaml:1056). For the
Keyturn Weekly Rate Plan: `modification_fee_amount: 35.00`, `modification_free_changes_count: 1`
(trips.yaml:204–205). Extended, `trips.extended.yaml:1647`: the **first** standing request attracts
a date-change fee of **eighteen dollars**.

*Demonstrated consequence.* Demonstrated on task 1's world in `1.md` §`policy_self_consistency`:
under base the guest's first date change is free, giving **$223.43**; under base's fee schedule if
the change were chargeable it would be $35.00, giving **$258.43**; the extended reading gives
**$241.43**. Three defensible numbers on one quantity.

*Affected artifact and location.* `trips.extended.yaml`, policy `trips_ext_extension_quote`,
`base_policy_refs` line 1618, `overwrite` line 1619, `params.modification_fee_repeat` /
`modification_fee_first` (lines 1630–1631), `rule` line 1647. Bears on task 1.

*Relation to previous revisions.* New; revision 1.

---

**F-06 — SOURCE-FACTOR RED — the seeded cross-difficulty rows contradict the guestplan charter.**

*Symptom.* Every `cross_difficulty` factor of this difficulty reads `guestplan_elections` and
`guestplan_charges` rows that could not have been produced under `blueprint/products/guestplan.yaml`.

*Root cause.* The guestplan rows seeded into both tasks' `initial_state` carry protection fees, and
in task 1 a secondary-driver fee, that do not follow from the elected level's own parameters.

*Evidence.* Charter, `blueprint/products/guestplan.yaml` variants:
Keyturn Business Traveler Protection — `daily_protection_fee_amount: 64.0`,
`protection_fee_charging_basis: daily_flat`, `protection_fee_minimum_amount: 64.0`;
Keyturn Premier Protection — `daily_protection_fee_amount: 52.0`,
`protection_fee_minimum_amount: 52.0`, **`secondary_driver_fee_amount: 0.0`**.
Seed, task 0 `initial_state.guestplan_charges`: two rows against election
`4ef510a7-0d9a-4244-b220-138d89affb13` (level *Business Traveler*), each
`charge_basis: daily_protection_fee`, `charge_amount: 168.0`, `days_covered: 22` — i.e. **$7.64 a
day** where the charter's daily flat is **$64.00** (22 × 64 = $1,408.00 a row).
Seed, task 1 `initial_state.guestplan_charges`: two rows against election
`e91f33ed-fc40-4328-94c6-bbff72a065df` (level *Premier*), each `charge_basis:
daily_protection_fee`, `charge_amount: 63.0`, `days_covered: 7` — **$9.00 a day** where the
charter's daily flat and minimum are both **$52.00** (7 × 52 = $364.00 a row); plus row
`fb70580c-0d1d-44df-a601-552c85fd778a`, `charge_basis: secondary_driver_fee`,
`charge_amount: 45.0`, on a level whose `secondary_driver_fee_amount` is **0.0**.
A further internal inconsistency in the same task 1 election: `coverage_days: 11` while the two
protection-fee rows it carries cover 7 + 7 = 14 days and the trip itself runs 14 days.

*Demonstrated consequence.* The factors that read these rows — `protection_block_price`
(`elec_fees`), `protection_level_adjustment` and `extended_day_protection_charge` (`elec_fees_c`,
`elec_fees_b`) — decide their tier from a figure the other product could not have produced, so they
test nothing about that product. Recomputed on the charter-correct figures the thresholds
($200.00 and $100.00) are still cleared, so **no scored number moves**; what fails is the evidence,
not the arithmetic. In task 1 the failure is sharper: the row the rule excludes as the computation's
near-miss (`secondary_driver_fee`, $45.00) is a row Keyturn Premier Protection never raises, so that
computation has no near-miss a reader could have got wrong — see `1.md` §`factor_weight`.

*Affected artifact and location.* `tasks/trip_booking_and_settlement_desk/tasks/0.json`
`initial_state.guestplan_charges` (2 rows) and `initial_state.guestplan_elections`
`4ef510a7-…`; `tasks/1.json` `initial_state.guestplan_charges` (3 rows) and
`initial_state.guestplan_elections` `e91f33ed-…`. Bears on both tasks.

*Relation to previous revisions.* New; revision 1.

---

**O-01 — observation — the `trips_ext_mileage_topup_grant` baseline publishes a refusal.**

The policy's `rule` opens (line 1099) "A guest who asks for more included miles part way through a
reservation **is granted** a top-up of included miles", and its `baseline.rule` (lines 1250–1255)
fixes the standard ceiling at 3,750 miles — which is exactly the Keyturn Monthly Rate Plan's
`included_miles_cap_per_booking`, i.e. exactly the miles the plan has already granted at booking. A
reader who applies the baseline alone to an ordinary Monthly reservation therefore computes **zero
miles granted**, not a standard grant. The number is definite and differs from gold, so the baseline
passes the self-sufficiency and surprise tests, but the default the policy publishes for its
ordinary customer reads as a refusal rather than as a standard treatment. No consequence is
demonstrable against either task's scored solution beyond what F-01 already demonstrates, so this is
recorded as an observation.

---

**O-02 — observation — ordering words in the tool docstrings.**

`task_tools.py` uses "before the call" in argument descriptions (lines 25, 59, 96, 134) and "After
the call" in effect descriptions (lines 18, 53, 90, 127). Neither locates the write relative to
another problem's write, and no docstring names another tool, so the check-3 purpose is met; the
wording is recorded only so a later revision can see it was looked at.

---

**O-03 — observation — cross-problem orders stated in base rules.**

`trips_settlement` (trips.yaml:1006) — "Settlement is performed once every end-of-trip line that can
arise has been posted or ruled out" — and `trips_evt_mileage_overage` (trips.yaml:774) — "Mileage is
settled once, at the end of the trip, against the allowance standing on the reservation at that
moment, including any miles granted by an extension or bought mid-trip" — are base rule sentences
stating an order between problems. Neither grounds a declared edge, and neither task's tree rests on
either, which is why this is an observation and not a red light. Both are however visible to a
reader of the rendered KB and could invite an agent to wait for a settlement that is not part of
either task.

---

**O-04 — observation — "priced" vs "quoted", and a `subject` the target tool never writes.**

`trips_ext_extension_quote` declares `subject: [trips_extension_charge_posted]` (line 1621), but
`submit_extension_request_8f69bfd6` writes a row into `trips_extension_requests`
(task_tools.py:153–157) and never a `trips_charges` row, so no `trips_extension_charge_posted` event
occurs. Base `trips_evt_extension`'s eligibility `extension_decision_window`
(trips.yaml:936–954) `applies_to: [trips_extension_charge_posted]` and states "The extension is
**priced** only where the host's decision is recorded no later than the decision window counted
forward from the scheduled return", while the extended rule (line 1640) has the guest "**quoted** a
price for the extra time **before** the request goes onto the extension request register". On a
reading that treats a quote as a pricing, the two sentences disagree about whether the desk may act
now or must wait for the host — but since the write is a register row and not a priced line, the
base gate does not in fact bind it, so no consequence is demonstrable and this is an observation.
The `subject` declaration nonetheless names an event family this policy never emits.

---

**O-05 — observation — two ladders whose tiers overlap as stated.**

`protection_block_price` (lines 1361–1367): tier 1 is "the trip's protection election is written as
Keyturn Business Traveler Protection **and** the protection fees … come to at least two hundred
dollars"; tier 2 is "the trip's protection election is written as Keyturn Declined Protection **or**
that election **stands voided**". A Business Traveler election carrying $250 of fees that stands
voided satisfies both, and the ladder as written does not say which wins (the `compute` resolves it
by evaluation order). `protection_level_adjustment` (lines 1545–1551) has the same shape with
Premier/Business Traveler against "Declined … or … voided". Neither task's world contains a voided
election, so no consequence can be demonstrated against a scored solution, and per the demonstration
standard this is recorded as an observation rather than a `SOURCE-FACTOR` red light.

---

## closing_checklist

Written after both tasks' `source_derivation_frozen` and `source_gt_comparison` were complete. This
section is post-reveal by construction and sits below the charter-global section, which stays
pre-reveal.

**The difficulty does not close.** Step 4's checklist requires all four relationships PASS on every
task; two relationships fail on both tasks.

| item | state |
| --- | --- |
| per-task audit files correspond one-to-one with the tasks, `_difficulty.md` alongside | **yes** — `0.md`, `1.md`, `_difficulty.md`; revision 1, no older revision to preserve |
| every comparison section carries a PASS | **no** — `0.md` §`source_gt_comparison` verdict is SOURCE-POLICY RED + SOURCE-FACTOR RED; `1.md` the same |
| this difficulty's extended policies fully covered by the M tasks | **yes** — task 0 claims `trips_ext_mileage_topup_grant` + `trips_ext_mileage_topup_pricing`, task 1 claims `trips_ext_young_driver_surcharge` + `trips_ext_extension_quote`; all four, no gap |
| the M tasks' scopes pairwise disjoint, each spanning its whole tree | **yes** — the two `charter_scope.extended_policies` sets are disjoint and each is exactly its task's root plus its one prerequisite problem |
| task tools and GT closed | **yes** — the four tools of `task_tools.py` are exactly the four `charter_scope.task_tools` across the two tasks, two per task, and each task's gold write set uses both of its own and neither of the other's |
| each task tool uses an independently generated, frozen uuid8 | **yes** — `0373887d`, `d571ad94`, `8e3312c3`, `8f69bfd6`; see §`action_binding_and_uuids` |
| every tree: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥ 1 `owner=user` problem, no cycle | **yes** — each tree has n = 1 prerequisite problem, 1 `value_input` edge (floor 1), and its root is the customer's own write (`pay_for_mileage_topup_d571ad94`, `submit_extension_request_8f69bfd6`); both trees acyclic |
| the difficulty's `prerequisite` edges together still a DAG, no cycle from cross-task references | **yes** — two disjoint single edges, no cross-task reference |
| every computation declares a self-sufficient baseline giving a definite number ≠ gold | **yes** — 0 vs 3600, 1166.00 vs 814.40, 139.39 vs 86.73, 285.12 vs 241.43, each recomputed independently and each matching the artifact's own `baseline_result`; with the reservation at **O-01** on the first |
| 4–6 factors per computation, ≥ 2 `parameter` and ≥ 1 `method`; ≥ 1 multi-source and ≥ 1 cross-difficulty per task | **yes** — 6/5/5/5 factors; see §`factor_ladders` |
| every ladder ≥ 3 tiers stated in full in its own `rule`, tiers distinct in outcome | **no** — 20 of 21 ladders are stated in full and implemented as stated; `date_change_fee_tier` is not (**F-05**). All 21 have three tiers distinct in outcome. Two ladders' tiers overlap as stated (**O-05**, observation) |
| every ladder's conditions and outcomes ones that line of business actually holds | **yes**, with **O-01** noted |
| every factor proved to bear weight on its task's world against an honest baseline | **yes** — all 21 move the scored value when their baseline is substituted, and every `baseline` is what the policy's `baseline.rule` states for that input; the auditor's 21 recomputed figures match the artifacts' `factor_sensitivity` figure for figure |
| **policy self-consistency** | **FAIL** on both tasks — F-01, F-02 (task 0); F-03, F-04, F-05, F-05b (task 1) |
| **the problem tree holds** | **PASS** on both tasks |
| **factors bear weight** | bearing-weight **PASS** on all 21; evidence **FAIL** on both tasks — F-06, and on task 1 the near-miss claim contradicted by recomputation (`1.md` Finding 1-D) |
| **policy → task unique solution** | the auditor's blind derivations reproduced GT exactly on all six scored parameters, both tool sequences, both owner assignments, both orders and both terminal states; GT is derivable but **not uniquely entailed**, the multiplicity being the SOURCE-POLICY defects above rather than a defect of its own |
| instantiation-stage gates re-run on the final form | **not re-run.** The artifacts were not touched by this audit (write domain is this directory only), so the gate snapshot supplied with the brief still describes the form audited. Re-running is for the round that reworks these artifacts. |

### verdict roll-up

| task | policy self-consistency | problem tree | factors bear weight | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | SOURCE-POLICY RED | PASS | weight PASS / evidence SOURCE-FACTOR RED | derivation identical to GT; not uniquely entailed | **SOURCE-POLICY RED + SOURCE-FACTOR RED** |
| 1 | SOURCE-POLICY RED | PASS | weight PASS / evidence SOURCE-FACTOR RED | derivation identical to GT; not uniquely entailed | **SOURCE-POLICY RED + SOURCE-FACTOR RED** |

**This difficulty does not pass the source-layer audit.** Findings and their evidence are above and
in the two task files; no artifact was edited and no fix was designed.

---

# revision_2

Round 2 re-audit. Revision 1 above is preserved unaltered; nothing in it has been rewritten to
accommodate what round 2 revealed.

## charter_global_frozen (revision 2)

- auditor: same independent source-layer auditor, revision 2
- freeze time (charter-global section): 2026-09-22, written **before** any GT field of either task
  was read in this round
- re-derivation grounds, hash against hash with the round producing the section:

| input | revision 1 | revision 2 | action |
| --- | --- | --- | --- |
| `trips.extended.yaml` | `6e48ab2593048536…` | `68e1725cd39e643c61c3a85d50d506c848791dc7a8abb916715702409b77fbdf` | **changed → charter-global section re-derived in full** |
| `task_tools.py` | `d15df91eaeb2deac…` | `d15df91eaeb2deac6ec10a4c00aa9a9b0ab75bebf2bf402ec6f51c9c25b69e32` | **unchanged** → §`action_binding_and_uuids`'s uuid and docstring findings carry forward by reference; the `(target_tool, computes)` half is re-derived because the charter moved |
| masked view `0.json` | `922f7f5e9518f8ce…` | `4d25e61d100375b9bb251a25bf8aa15dce166fd450ab34283c3d3da9608233dc` | changed → task 0 re-derived in full |
| masked view `1.json` | `bd41eb84345dc944…` | `ddf2961858970285dbbb4ecabc73f8978e654b52de3b0b844e41417723081580` | changed → task 1 re-derived in full |

  All four were re-hashed by this auditor and match the values the brief states.
- fields permitted / masked: exactly as revision 1. Nothing derived from a revealed GT appears in
  this section.
- entry conditions: the brief supplied the re-run gate snapshot (all seven green). Re-checked and
  cited, not re-run.
- **base section re-verified independently**: `diff` of `trips.extended.yaml` lines 1–1058 against
  `blueprint/products/trips.yaml` is empty — byte-identical, all 1058 lines. `git diff --stat` over
  `env/env_0015_car_sharing_marketplace/blueprint/` is empty: the blueprint was not edited, including
  for the item claimed as re-scoped rather than overridden.

### policy_conflict_scan (revision 2)

Four extended policies, unchanged in identity, subject, `computes` and `target_tool`; the scope
split between the two tasks is unchanged and still pairwise disjoint and jointly complete. What
moved:

| policy | `base_policy_refs` | `overwrite` r1 → r2 | other structural change |
| --- | --- | --- | --- |
| `trips_ext_mileage_topup_grant` | unchanged `[trips_evt_mileage_allowance]` | 1 → **3** | `ceiling_standard` 3750 → **5000**, `ceiling_long_charged` 4500 → **6000** |
| `trips_ext_mileage_topup_pricing` | **+ `trips_evt_mileage_allowance`** | 0 → **1** | `corporate_fee_threshold` 200.00 → **2000.00**; `protection_block_price` tier 1 gains "that election stands active", tier 2 becomes "does not stand active" |
| `trips_ext_young_driver_surcharge` | unchanged | 0 → **1** | `protection_fee_floor` 100.00 → **800.00**; `adjust_unprotected: 5` removed, `adjust_protected_light: -2` added; `protection_level_adjustment` re-laddered on a fee band |
| `trips_ext_extension_quote` | unchanged `[trips_evt_extension]` | 0 → **1** | `date_change_fee_tier` → **`register_lodgement_charge`** (35/18/0 → 24/12/0); `extended_day_protection_charge` → **`protection_cover_credit`**, now subtracted; `protection_fee_floor` 100.00 → **800.00**; the stray conjunct removed from `compute` |

Overlapping subjects, eligibility, time anchors, terminal states and cross-category boundaries:
re-swept and **PASS** on the same grounds as revision 1 §`policy_conflict_scan`, which the moves
above do not disturb — the two `trips_reservation_charge_posted` writers are still separated by
`charge_basis` and by `computes`, the base eligibility gates are still inherited unweakened, and
each `cross_category` block still declares exactly what its `compute` reads (note
`trips_ext_extension_quote` now declares `reads: [status, guestplan_charges.charge_amount]`, having
correctly dropped `protection_level_name`, which its compute no longer reads).

### rule_compute_equivalence (revision 2)

Re-run over all four policies, binding by binding, in both directions.

- `trips_ext_mileage_topup_grant`: 22 bindings, all quoted, all equivalent. **PASS.**
- `trips_ext_mileage_topup_pricing`: 17 bindings, all quoted, all equivalent; the floor "taken as
  nothing where that comes out below nothing" is in the `rule` (line 1312) and is `MX(0, …)` in
  `compute`. **PASS.**
- `trips_ext_young_driver_surcharge`: 17 bindings, all quoted; the rate floor "where that leaves a
  rate below nothing, no surcharge is owed" (line 1495) is `MX(0, …)` on `effective_rate`.
  **PASS.**
- `trips_ext_extension_quote`: 20 bindings. The revision-1 defect **F-05 is fixed** — `compute`
  line 1706 now reads
  `lodgement_charge: "K('lodgement_repeat') if (change_count >= 2) else (K('lodgement_first') if (change_count == 1) else K('lodgement_none'))"`,
  with the `days_run_b >= K('week_days')` conjunct gone, so rule (line 1672), ladder (lines
  1783–1789) and compute now state the same three tiers on every world. **One new miss**, recorded
  as observation **O-08**: `result` (line 1711) carries `MX(0, …)` while the rule sentence it quotes
  (line 1666) states no floor.

Mechanically re-checked across all four policies and found clean: every `K('…')` resolves to a
declared param; no param is declared and unused; every ladder `when` and every ladder `method` is a
verbatim substring of its own `rule`; every `baseline.rule` sentence is in the `rule`; every
`baseline.params` key is declared.

### action_binding_and_uuids (revision 2)

`task_tools.py` is byte-identical to revision 1, so the uuid8 sweep (`0373887d`, `d571ad94`,
`8e3312c3`, `8f69bfd6` — distinct, unsequenced, unshared) and the docstring findings carry forward
by reference to revision 1 §`action_binding_and_uuids`; the two hashes recorded above are the
grounds. Re-derived because the charter moved: the four `(target_tool, computes)` pairs are
unchanged and each is still claimed by exactly one policy. **PASS.**

### prerequisite_graph and prerequisite_sentences (revision 2)

Both `prerequisite` blocks are unchanged in every field — same `problem`, `kind: value_input`,
`gate` (`granted_miles`, `yd_share`), `form: state`, absent `fallback_reason`, same `condition`,
same `resolved_by`, and the same two `policy_source` sentences. Re-verified mechanically on the new
file: each `policy_source` is still verbatim in the blocked policy's **own** rule (lines 1311 and
1665), each `gate` is still a real binding of that policy's own compute, each `resolved_by` is still
the depended-on policy's `target_tool`, and neither sentence is restated in the depended-on rule.
The graph is still two disjoint single edges and acyclic. The four-point test and the
single-write / single-reading derivations of revision 1 §`prerequisite_sentences` are unchanged by
the rework and carry forward. **PASS.**

### override_declarations (revision 2) — the sweep, and its exemptions

The reworker claims a sweep across all 21 tiered factors, six overrides declared and the rest left
alone. This auditor re-derived the sweep from the charter rather than accepting the dispositions.

**The six declarations, mechanically verified.** For each, the `superseded_clause` is a verbatim
substring of the cited base policy's `rule`, and the `replaced_by` text is a verbatim sentence of
the extended policy's own `rule`:

| extended policy | base policy | superseded clause (verbatim in base) | verified |
| --- | --- | --- | --- |
| `..._topup_grant` | `trips_evt_mileage_allowance` | "A guest may buy further miles in whole packages only" | ✓ ✓ |
| `..._topup_grant` | `trips_evt_mileage_allowance` | "a package bought mid-trip is granted in full and charged in full even where fewer miles are eventually driven" | ✓ ✓ |
| `..._topup_grant` | `trips_evt_mileage_allowance` | "capped at the plan's per-booking ceiling however long the reservation runs" | ✓ ✓ |
| `..._topup_pricing` | `trips_evt_mileage_allowance` | "A guest may buy further miles in whole packages only; part packages are not sold, and a package bought mid-trip is granted in full and charged in full even where fewer miles are eventually driven." | ✓ ✓ |
| `..._young_driver_surcharge` | `trips_evt_reservation_pricing` | "pays the young-driver surcharge on the discounted base rate" | ✓ ✓ |
| `..._extension_quote` | `trips_evt_extension` | "Extended time is priced at the locked daily rate lifted by the plan's uplift percentage, applied to the extended days only" | ✓ ✓ |

**The exemptions, audited rather than accepted.** The round-1 signature of this pattern was: a
factor's fall-through equals the base figure *for the plan of the task that uses it*, and the tiers
then depart. This auditor re-enumerated every base figure that could be mirrored, against the two
plans in play (Keyturn Monthly for task 0, Keyturn Weekly for task 1):

| base figure | plan value | extended fall-through | mirrored? | disposition | sound? |
| --- | --- | --- | --- | --- | --- |
| `included_miles_cap_per_booking` | Monthly 3750 | `ceiling_standard` **5000** | no longer | **declared** (overwrite 3) | ✓ and the mirror is now broken as well |
| `extra_miles_package_size_miles` | Monthly 500 | `block_standard` 500 | yes | **declared** (overwrite 1) | ✓ the replacement makes 500 "the standard block", which is what licenses the 750/900 tiers |
| `extra_miles_package_price` | Monthly 145.00 | `block_price_standard` 145.00 | yes | **declared** (pricing overwrite) | ✓ — see the note below |
| `young_driver_surcharge_percent` | Weekly 15 | `rate_standard` 15 | yes | **declared** | ✓ the quoted clause names the surcharge and its acting base, and the param's own schema line binds it to that clause |
| `extension_rate_uplift_percent` | Weekly 8 | `uplift_standard` 8 | yes | **declared** | ✓ |
| `extension_max_additional_hours` | Weekly 72 | `max_extra_hours` 72 | yes | **exempt** | ✓ **sound**: base states a *cap* ("One extension may not add more than the plan's maximum additional hours"); extended uses 72 as the quoted time and as a ceiling on a declined request's hours ("held to the longest further time the reservation can still take"), and no tier ever exceeds it. Base and extended agree, so there is nothing to override |
| `included_miles_per_day` | Monthly 125 | `allowance_standard` 125 | yes | **exempt** | ✓ **sound**: base's "the plan's daily allowance multiplied by the reserved days" fixes the allowance *granted with the reservation at confirmation*; the extended measure projects *how many miles the top-up must cover for the rest of the trip*. Different questions, and the fall-through agreeing with the plan's own daily allowance is the coherent choice, not a contradiction of it |
| `modification_fee_amount` / `modification_free_changes_count` | Weekly 35.00 / 1 | `lodgement_*` 24/12/0 | no | **re-scoped** | ✓ **sound** — see below |
| the other 13 tiered quantities (top-up reserve, volume concession, handling charge, early-purchase credit, protection/conduct/additional-driver adjustments, cover credit, and the six `method` ladders' algorithms) | — | — | no base figure exists | **exempt** | ✓ base states no figure and no sentence governing any of them; each is structure the extended policy adds, not a base provision weakened |

*Note on the pricing declaration.* It is the weakest of the six in mechanism: the clause it
supersedes never stated a price, and the base price lives in a `params` block that no `overwrite`
can quote. It nevertheless works, because superseding "A guest may buy further miles in whole
packages only; part packages are not sold…" removes the only clause `extra_miles_package_price`
("Price of one block of extra miles") attached to, and the replacement sentence takes over the same
question in the extended policy's own words. And the residual is benign rather than adversarial:
the surviving base figure (145.00) is **equal to the extended fall-through**, so a reader who
reached for the plan's parameter table would land on the documented standard tier, not on a rival
answer. The same holds for `young_driver_surcharge_percent` (15 = `rate_standard`) and
`extension_rate_uplift_percent` (8 = `uplift_standard`).

*Verification of the F-05b re-scoping.* The coordinator asked whether re-scoping relocates the
contradiction rather than removing it. It does not, and the ground is a **base** sentence, not the
reworker's assertion. Base `trips_evt_extension` (trips.yaml:929) says: "A guest who wants the
vehicle for longer asks for an extension, which is taken onto the extension request register rather
than applied to the reservation straight away; **the reservation's scheduled return moves only once
the host has approved the request**." So on base's own account lodging a request is not a date
change. Base's `modification_fee_amount` is, by its schema line, the "Fee for **changing the dates**
of a confirmed booking once the free changes are used" — it triggers on a date change occurring.
The two therefore answer different questions, and the extended rule now says so in terms
(line 1672): "Lodging a request neither moves the reservation's scheduled return nor changes its
dates, so the register lodgement charge is not the fee the marketplace charges for a date change
once a reservation's free date changes are used; it is charged for putting a fresh request on the
extension request register while earlier requests already stand there." The tool contract agrees —
`submit_extension_request_8f69bfd6` "leaves it standing as submitted and waiting on the host. The
reservation itself is untouched by the call: its dates, its allowance and its balance stay as they
were" (task_tools.py:126–129). The quantity is genuinely a different charge, base is silent about
it, and the values (24/12/0) no longer shadow base's 35.00/1. **Re-scoping sound; F-05b closed.**

*Verification of the volunteered guestplan-pricing change.* In revision 1 the extension quote added
"the protection charge for the extended days" of $14/$9 a day — this desk pricing cover that belongs
to the guestplan product and to another difficulty. It is now `protection_cover_credit`: the same
guestplan reads decide a **credit of this desk's own money**, subtracted from the trips quote
(`result: RND(MX(0, extension_price + yd_share + lodgement_charge - cover_credit), 2)`), and the
`cross_category` entry is `as: branch` with a note that matches. The change is **sound**: the policy
now prices nothing of the other product and only discounts its own quote, which is exactly what a
`branch`-mode cross-category read licenses; the factor still bears weight on task 1 and still reads
that product's seeded rows. It introduced one thing, recorded as **O-08**: the credit is the first
subtrahend in this quote, so the compute needed a floor at nothing, and that floor was put in
`compute` without a sentence in the `rule`.

### factor_ladders (revision 2)

| policy | factors | `parameter` | `method` | `cross_difficulty` |
| --- | --- | --- | --- | --- |
| `..._topup_grant` | 6 | 4 | 2 | none |
| `..._topup_pricing` | 5 | 4 | 1 | `protection_block_price` → guestplan |
| `..._young_driver_surcharge` | 5 | 4 | 1 | `protection_level_adjustment`, `declared_driver_adjustment` → guestplan |
| `..._extension_quote` | 5 | 3 | 2 | `protection_cover_credit` → guestplan |

Mechanically re-verified across all 21 factors: 4–6 per policy with ≥ 2 `parameter` and ≥ 1
`method`; every `decides` an intermediate binding and never `result`; binding sets disjoint within
each policy; every ladder exactly three tiers; **no two tiers of any ladder select the same value or
method**; every tier's `when` and every `method` text a verbatim sentence of its own `rule`; every
tier implemented as a branch of the `decides` binding (the revision-1 exception, F-05, is fixed).
Per task: task 0 carries ≥ 1 multi-source and 1 cross-difficulty factor; task 1 carries ≥ 1
multi-source and 3 cross-difficulty. **PASS.**

**Tier disjointness — revision 1's O-05 is fixed.** Both offending ladders were re-laddered and both
are now pairwise disjoint as stated:

- `protection_block_price`: tier 1 now requires "that election **stands active**"; tier 2 is
  "written as Keyturn Declined Protection or that election **does not stand active**". A Business
  Traveler election that is active cannot satisfy tier 2, so the revision-1 overlap (an active-level
  election that also stood voided) is gone.
- `protection_level_adjustment`: the "Declined or voided" tier is replaced by a fee band — tier 1
  "stands active, is written as Premier or Business Traveler, and the fees … come to at least eight
  hundred dollars", tier 2 the same with "less than eight hundred dollars". Disjoint on the fee
  test.
- `protection_cover_credit` was already disjoint on the same shape and remains so.

**Tier reachability after the threshold moves** (the coordinator's fourth item). Both raised
thresholds leave all three tiers of every affected ladder reachable in worlds this charter permits:
`corporate_fee_threshold: 2000.00` against Business Traveler's charter fee of $64.00 a day needs
about 32 covered days, which a 60-day-plus reservation reaches easily (task 0's own election has
$2,688.00 over 42 days); `protection_fee_floor: 800.00` against Premier's $52.00 a day needs about
16 covered days, which task 1's 14-day trip just misses ($728.00) and a three-week trip clears. The
fall-through of each remains reachable for any guest without an active qualifying election.
**PASS.**

**Conditions and outcomes ones that line of business actually holds.** Re-reviewed tier by tier,
including the three new or changed ladders. `register_lodgement_charge` at $0/$12/$24 for putting a
further request on the register while earlier ones stand is an ordinary administrative charge;
`protection_cover_credit` at $0/$9/$14 a day off the quote for guests carrying active cover is an
ordinary retention discount; `protection_level_adjustment` at 0/−2/−4 points banded on what the
guest has actually paid for cover is an ordinary risk adjustment. Revision 1's **O-01 is fixed**:
with `ceiling_standard` lifted from 3750 to 5000, the topup-grant baseline no longer computes a
refusal for an ordinary Monthly guest — it grants miles (demonstrated on task 0's world in `0.md`
revision_2 §`factor_weight`). **PASS.**

### findings (revision 2)

**Round-1 findings, disposition verified.** Each was re-tested against the reworked charter and, for
the per-task consequences, against the reworked worlds (in the two task files).

| id | round-1 verdict | round-2 disposition | verified how |
| --- | --- | --- | --- |
| **F-01** | SOURCE-POLICY RED | **CLOSED** | overwrite 3 of `..._topup_grant` quotes the base clause verbatim and replaces it; `ceiling_standard` also moved off the base figure. The base reading is no longer available to a reader |
| **F-02** | SOURCE-POLICY RED | **CLOSED** | `..._topup_pricing` now cites `trips_evt_mileage_allowance` in `base_policy_refs` and declares an overwrite of the package clause; residual base figure equals the extended fall-through, so it leads to the documented default, not a rival answer |
| **F-03** | SOURCE-POLICY RED | **CLOSED** | overwrite of "pays the young-driver surcharge on the discounted base rate"; `rate_standard` still equals the Weekly figure, which is the fall-through |
| **F-04** | SOURCE-POLICY RED | **CLOSED** | overwrite of the base uplift sentence |
| **F-05** | SOURCE-POLICY RED | **CLOSED** | the stray `days_run_b >= K('week_days')` conjunct is gone from `compute` line 1706; rule, ladder and compute now agree on every world, not only on task 1's |
| **F-05b** | SOURCE-POLICY RED | **CLOSED by re-scoping**, and the re-scoping is sound — grounded in base trips.yaml:929, stated in the extended rule, and matched by the tool contract |
| **F-06** | SOURCE-FACTOR RED | **CLOSED** | verified against `blueprint/products/guestplan.yaml` in both task files |
| **the pattern** | (the common root of F-01…F-04) | **SWEPT, and the exemptions hold** | re-derived above, figure by figure, against both plans in play |
| **O-01** | observation | **FIXED** | `ceiling_standard` 3750 → 5000 |
| **O-05** | observation | **FIXED** | both ladders re-laddered disjoint |
| **O-02** | observation | **NO CHANGE**, correctly — `task_tools.py` is byte-identical and the observation never asked for one |
| **O-03** | observation | **NO CHANGE**, correctly — the two base rules that state a cross-problem order are in the blueprint, which an audit of this difficulty may not edit, and neither grounds an edge |
| **O-04** | observation | **NO CHANGE** — `subject: [trips_extension_charge_posted]` still names an event family the target tool never emits. Still an observation; see **O-09** |

---

**O-06 — observation — three overwrite entries claim overlapping text of one base sentence.**

`trips_ext_mileage_topup_grant` supersedes two fragments of base `trips_evt_mileage_allowance`'s
package sentence ("A guest may buy further miles in whole packages only" and "a package bought
mid-trip is granted in full and charged in full even where fewer miles are eventually driven"),
while `trips_ext_mileage_topup_pricing` supersedes **the whole of that same sentence**. One base
sentence therefore carries three different `replaced_by` texts from two policies.

Recorded as an observation, not a red light: the three replacements govern different quantities —
two the granting of miles, one the pricing of them — so no situation produces two conclusions about
one quantity, and the merged semantics is unique. It is the bookkeeping that is redundant, not the
policy. Bears on task 0.

---

**O-07 — observation — the base telematics-authority clause is not mirrored in the mileage ledger sum.**

Base `trips_evt_mileage_allowance` (trips.yaml:743) says "A telematics reading is authoritative where
one exists; a host or guest reading stands only where no telematics reading covers the same
handover". `ledger_unused` (line 1126) and `driven_miles` (line 1139) sum every reading regardless of
source. No `overwrite` names that clause.

Checked against both worlds and **no consequence arises**: task 0's three odometer readings are
dated 2026-08-19, 2026-09-04 and 2026-09-16 and task 1's two are dated 2026-09-10 and 2026-09-15 —
in neither world do two readings cover the same handover, so base's tie-break never fires and the
sum is what base would give. Recorded so a later reseed does not reintroduce the question.
Bears on both tasks.

---

**O-08 — observation — the extension quote's compute carries a floor the rule does not state.**

`trips_ext_extension_quote.compute` line 1711:
`result: "RND(MX(0, extension_price + yd_share + lodgement_charge - cover_credit), 2)"`.
The rule sentence it quotes, line 1666, states no floor: "The quote is the price of the extended
time, with the young-driver share and the register lodgement charge added to it and the cover credit
taken off it, rounded to the nearest cent once at the end." Its sibling
`trips_ext_mileage_topup_pricing` does state its floor ("taken as nothing where that comes out below
nothing", line 1312), so the omission is local.

This arrived with the volunteered change: the cover credit is the first quantity ever subtracted in
this quote, and the floor came with it into `compute` alone. Recorded as an observation and not a
red light because the consequence cannot be demonstrated on a world this business has. Both the
price and the credit scale with the extended days, so the quote goes negative only when the uplifted
daily rate falls below the credit — below about **$13.46** a day at the 4 % uplift and **$12.50** at
the 12 % uplift. No plan in `variants` states a minimum daily rate, so the charter permits such a
world, but no car-sharing daily rate in this scenario approaches it (task 1's is $88.00, giving
$91.52 uplifted against a credit of at most $14.00). Bears on task 1.

---

**O-09 — observation — `subject` still names an event family the target tool never emits.**

Carried forward from revision 1 §`findings` O-04, re-checked and unchanged:
`trips_ext_extension_quote` declares `subject: [trips_extension_charge_posted]` (line 1646) while
`submit_extension_request_8f69bfd6` writes only a `trips_extension_requests` row
(task_tools.py:153–157). Base `trips_evt_extension`'s eligibility `extension_decision_window`
`applies_to: [trips_extension_charge_posted]` therefore still does not bind the write this policy
performs, which is why this remains an observation rather than a wait/act-now conflict. The rework
sharpened rather than worsened it: the new lodgement sentence (line 1672) spells out that lodging a
request moves nothing on the reservation, which makes the register-row reading the plain one.
Bears on task 1.

## closing_checklist (revision 2)

Written after both tasks' revision_2 `source_derivation_frozen` and `source_gt_comparison` were
complete. Post-reveal by construction, so it sits below the charter-global section, which stays
pre-reveal.

**The difficulty does not close**, on one narrow finding. Fifteen of the sixteen round-1 and
round-2 items are closed; a single false figure in a proof field of task 1 keeps that task's factors
relationship from passing.

| item | state |
| --- | --- |
| per-task audit files correspond one-to-one with the tasks, `_difficulty.md` alongside | **yes** — `0.md`, `1.md`, `_difficulty.md`, each carrying revision 1 intact and revision_2 appended below it; old revisions traceable |
| every comparison section carries a PASS | **no** — `0.md` revision_2 PASSES on all four relationships; `1.md` revision_2 carries **SOURCE-FACTOR RED** (Finding 1-F) |
| this difficulty's extended policies fully covered, the M tasks' scopes pairwise disjoint, each spanning its whole tree | **yes** — unchanged from revision 1 and re-verified against the revealed `charter_scope`: task 0 `{topup_grant, topup_pricing}`, task 1 `{young_driver_surcharge, extension_quote}` |
| task tools and GT closed; each tool an independently generated, frozen uuid8 | **yes** — `task_tools.py` is byte-identical to revision 1; the four `(target_tool, computes)` pairs are each claimed by one policy |
| every tree: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥ 1 `owner=user` problem, no cycle; the difficulty's edges together a DAG | **yes** — both trees n = 1 with one `value_input` edge and an `owner=user` root; two disjoint single edges, acyclic, no cross-task reference |
| every computation a self-sufficient baseline giving a definite number ≠ gold | **yes** — 1250 vs 3600, 1166.00 vs 814.40, 139.39 vs 108.42, 285.12 vs 192.53; all four independently recomputed and matching the artifacts' own `baseline_result`. Revision 1's O-01 (a baseline that published a refusal) is fixed |
| 4–6 factors per computation, ≥ 2 `parameter` and ≥ 1 `method`; ≥ 1 multi-source and ≥ 1 cross-difficulty per task | **yes** — 6/5/5/5; task 0 one cross-difficulty factor, task 1 three |
| every ladder ≥ 3 tiers stated in full in its own rule, tiers distinct in outcome **and pairwise disjoint as stated** | **yes** — all 21 verified mechanically; revision 1's F-05 (a tier implemented with a condition the rule never stated) and O-05 (two overlapping ladders) are both fixed |
| every ladder's conditions and outcomes ones that line of business actually holds | **yes**, including the three new or changed ladders |
| every factor proved to bear weight against an honest baseline | **yes** — all 21, recomputed, every figure matching the artifacts' `factor_sensitivity` |
| every computation has a near-miss that a careless reader would fold in **and that flips a tier** | **yes, now** — task 0: the other booking's mileage overage (3600 → 2250) and the plan-allowance grant row (814.40 → 1589.00); task 1: the young-driver protection surcharge on the election (108.42 → 86.73 and 192.53 → 182.53), plus the goodwill credit. Revision 1's finding 1-D(b) is closed |
| cross-difficulty rows follow the other product's charter | **yes** — every seeded guestplan figure now derives from `blueprint/products/guestplan.yaml`; F-06 closed on both worlds |
| proof fields free of figures from the previous revision | **all but one** — the full sweep over `argument_uniqueness_tracing`, `factor_trace`, `why_false`, `flips_to_true_by`, `edge_load_bearing` and `seed_consistency` in both files found every current-world assertion true except one in task 1 (**Finding 1-F**, `106.62` where the world gives `105.91`). Revision-1 figures elsewhere occur only in dated change-log narrative, each true of the moment it names |
| **policy self-consistency** | **PASS** on both tasks — the override pattern is swept, six declarations verified verbatim against base, and the fifteen exemptions independently audited and found sound |
| **the problem tree holds** | **PASS** on both tasks |
| **factors bear weight** | task 0 **PASS**; task 1 weight and evidence PASS but **RED** on one false proof figure |
| **policy → task unique solution** | **PASS** on both tasks — both blind derivations reproduced GT exactly on all six scored parameters, every tool, owner, order and terminal state, and GT is now uniquely entailed rather than merely derivable |
| instantiation-stage gates re-run on the final form | **not re-run by this auditor** — the write domain is this directory only and the artifacts were not touched. The brief's re-run snapshot (all seven green) describes the form audited |

### round-1 item disposition, one by one

| item | round-1 verdict | round-2 |
| --- | --- | --- |
| the override **pattern** across all 21 tiered factors | root of F-01…F-04 | **SWEPT — verified, exemptions sound** |
| F-01 / 0-A | SOURCE-POLICY RED | **CLOSED** |
| F-02 / 0-B | SOURCE-POLICY RED | **CLOSED** |
| F-03 / 1-A | SOURCE-POLICY RED | **CLOSED** |
| F-04 / 1-B | SOURCE-POLICY RED | **CLOSED** |
| F-05 | SOURCE-POLICY RED | **CLOSED** (for every world, not only task 1's) |
| F-05b / 1-C | SOURCE-POLICY RED | **CLOSED by re-scoping — reasoning verified against base trips.yaml:929** |
| F-06 / 0-C / 1-D(a) | SOURCE-FACTOR RED | **CLOSED** on both worlds |
| 1-D(b) — inert near-misses | SOURCE-FACTOR RED | **CLOSED** — both computations now have a tier-flipping near-miss |
| O-01 | observation | **FIXED** |
| O-05 | observation | **FIXED** |
| O-02, O-03 | observations | **NO CHANGE, correctly** |
| O-04 | observation | **NO CHANGE** — carried forward as O-09 |
| 0-D, 1-E | observations | **ACTED ON** — both personas softened, and both softenings verified to remove the pre-emption without removing the caller fact |

### new in round 2

| id | class | where |
| --- | --- | --- |
| **1-F** | **SOURCE-FACTOR RED** | `tasks/1.json` `computations[0].factor_trace`: "a reader who nets it in reaches 106.62 instead" — the world gives 105.91 (or 105.92 on the other reading); no reading reaches 106.62 |
| O-06 | observation | three overwrite entries claim overlapping text of one base sentence |
| O-07 | observation | the base telematics-authority clause is not mirrored in the mileage ledger sums — inert on both worlds |
| O-08 | observation | the extension quote's `compute` carries a floor at nothing that its `rule` does not state — arrived with the volunteered cover-credit change; unreachable above a daily rate of about $13.46 |
| O-09 | observation | `subject: [trips_extension_charge_posted]` still names an event family the target tool never emits (carried from O-04) |
| 1-G | observation | task 1's persona says protection was "charged weekly" against a single charge at trip start |
| 1-H | observation | two change-log entries in task 1's `design_rationale` carry no round marker |

### verdict roll-up (revision 2)

| task | policy self-consistency | problem tree | factors bear weight | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | **PASS** |
| 1 | PASS | PASS | RED (Finding 1-F) | PASS | **SOURCE-FACTOR RED** |

**Task 0 passes the source-layer audit. Task 1 does not, on Finding 1-F alone** — every other
relationship it must satisfy now holds, and every round-1 defect against it is genuinely closed
rather than relocated. No artifact was edited by this audit and no fix was designed.

---

# revision_3

Round 3 re-audit, narrow scope: confirm round 2's single RED (Finding 1-F) is closed, confirm
nothing that passed has regressed, and judge the four observations. Revisions 1 and 2 above are
preserved unaltered.

## charter_global_frozen (revision 3)

- auditor: same independent source-layer auditor, revision 3
- freeze time: 2026-09-22, written **before** any GT field of either task was read in this round

| input | revision 2 | revision 3 | action |
| --- | --- | --- | --- |
| `trips.extended.yaml` | `68e1725cd39e643c…` | `ce70b0729c53fefff23255ce2e2b637dae4d64895dcfd6034c348d28dc093076` | **changed → charter-global section re-derived in full** |
| `task_tools.py` | `d15df91eaeb2deac…` | `d15df91eaeb2deac6ec10a4c00aa9a9b0ab75bebf2bf402ec6f51c9c25b69e32` | **unchanged** (third round running) → the uuid8 and docstring findings carry forward by reference to revision 1 §`action_binding_and_uuids` |
| masked `0.json` | `4d25e61d100375b9…` | `4d25e61d100375b9bb251a25bf8aa15dce166fd450ab34283c3d3da9608233dc` | **unchanged** — but the charter moved, so task 0's figures are re-derived against the new charter rather than carried forward |
| masked `1.json` | `ddf2961858970285…` | `697052275ed16f445aecd7ad10add1a2d181224bbd76064107efc731feced697` | **changed → task 1 re-derived in full** |

All four re-hashed by this auditor and matching the brief. Fields permitted / masked exactly as
revisions 1 and 2; nothing derived from a revealed GT appears in this section.

**Base section re-verified independently**: `diff` of lines 1–1058 against
`blueprint/products/trips.yaml` is empty; `git diff --stat` over `blueprint/` is empty. The
blueprint was not edited.

### policy_conflict_scan / rule_compute_equivalence / prerequisite_graph (revision 3)

Re-run mechanically over the new file. Unchanged and **PASS**: the four policies keep their
identity, `subject`, `computes` and `target_tool`; the four `(target_tool, computes)` pairs are each
claimed by one policy; every `K('…')` resolves and no param is orphaned; every ladder has three
tiers with distinct outcomes, each `when` and each `method` a verbatim sentence of its own `rule`;
binding sets are disjoint within each policy; every `baseline.rule` sentence is in the `rule` and
every `baseline.params` key is declared; factor counts are 6/5/5/5 with ≥ 2 `parameter` and ≥ 1
`method` each, and cross-difficulty coverage is unchanged. Both `prerequisite` edges are unchanged
in every field, each `policy_source` still verbatim in the blocked policy's own rule, each `gate` a
real binding, each `resolved_by` the depended-on `target_tool`, neither sentence restated in the
depended-on rule, graph still two disjoint edges and acyclic.

**Nothing in `compute` moved.** Re-derived independently from the new charter: all six scored
values, all four `baseline` figures and all 21 factor-sensitivity figures are **identical to
revision 2** (3600 / 814.40 / 108.42 / 192.53; baselines 1250 / 1166.00 / 139.39 / 285.12). The
reworker's assertion that no value moved as a side effect **holds**.

### the four observations — judged

**O-06 — CLOSED.** The base sentence

> "A guest may buy further miles in whole packages only; part packages are not sold, and a package
> bought mid-trip is granted in full and charged in full even where fewer miles are eventually
> driven."

is now claimed by four disjoint fragments, one `replaced_by` per quantity, verified mechanically:

| fragment | claimed by | replaced by (quantity) |
| --- | --- | --- |
| "A guest may buy further miles in whole packages only" | `..._topup_grant` | the whole-blocks sentence (the unit of sale) |
| "a package bought mid-trip is granted in full" | `..._topup_grant` | the shortfall sentence (how many miles) |
| "charged in full even where fewer miles are eventually driven" | `..._topup_pricing` | the standard line-price sentence (what it costs) |
| "part packages are not sold" | **nobody** | — |

The fragments are **pairwise disjoint** (checked by span arithmetic against the base sentence), each
is verbatim in the base rule, and each `replaced_by` is verbatim in the claiming policy's own rule.
The revision-2 defect — one sentence carrying three replacements from two policies — is gone.

**Judging the clause left claimed by nobody**, as asked. "part packages are not sold" is the
negative restatement of the fragment immediately before it, "A guest may buy further miles in whole
packages only" — and that fragment *is* superseded, by "A top-up of included miles is granted in
whole blocks, the standard block being five hundred miles." The replacement preserves the force the
surviving fragment asserts (whole units only) while renaming the unit, so on the gold path nothing
opposes it: `granted_raw = blocks × block_size` is always a whole number of blocks, and on task 0
the ceiling does not bind (`headroom` 4250 > `granted_raw` 3600), so the grant is 4 whole blocks of
900. **The decision is sound for both scored solutions.**

One residual reading survives and is recorded as **observation O-10** rather than suppressed: the
in-force extended ceiling clause ends "miles are granted as **whole miles** with no part mile
granted", not *whole blocks*, so where the ceiling does bind the grant can be a part block. On task
0 that never happens on the gold path, but it happens on two paths the artifact itself publishes —
the documented baseline (1250 miles, which is 2.5 blocks of 500) and the near-miss (2250 miles,
2.5 blocks of 900). A reader who applies the unclaimed fragment to blocks would round those to
1000 and 1800. No **scored** value has two readings, which is why this is an observation; but the
clause is not quite unopposed, and the reworker's own criterion ("right only if nothing contradicts
it") is met only once "package" is read as retired along with the fragment that defined it.

**O-07 — the reasoning is SOUND; disposition accepted.** The claim is that base
`trips_evt_mileage_allowance` (trips.yaml:743) — "A telematics reading is authoritative where one
exists; a host or guest reading stands only where no telematics reading covers **the same
handover**" — cannot honestly be coded, so it was recorded as a standing reseed constraint instead
of being written into the `rule`. Both halves check out:

- *Not codable.* The evaluator's whole primitive set is
  `F P SUM COUNT MAX LATEST EXISTS CPARAM CFIELD XSUM XCOUNT XMAX XLATEST MONTHS DAYS MX MN RND ABS`
  plus `int/float/round/abs/min/max`. Every aggregate is flat over a filtered row set: there is no
  grouping, no per-row iteration and no set difference. Expressing "host readings **except those
  whose handover already carries** a telematics reading" needs a correlated anti-join over
  `(usage_date, reading_point)`, which no primitive provides. `SUM(..., usage_source='telematics')`
  would silently drop genuine host-only readings instead, which is a different rule.
- *Prosing it alone would be worse.* Adding a tie-break sentence to the `rule` with no matching
  branch in `compute` is exactly the check-2 divergence that revision 1 red-lighted as **F-05** and
  revision 2 closed. Recording a constraint is the only disposition that neither mis-codes the base
  clause nor reintroduces F-05.

And on any world satisfying the constraint there is **no conflict to declare**: base's tie-break
never fires, so the flat sum is precisely what base gives. Verified on both worlds — task 0's three
odometer readings are `(2026-08-19, mid_trip)`, `(2026-09-04, mid_trip)`, `(2026-09-16, mid_trip)`
and task 1's two are `(2026-09-10, mid_trip)`, `(2026-09-15, mid_trip)`; **no handover in either
world carries more than one reading**. One caveat, recorded as **observation O-11**: the constraint
is prose, and no gate enforces it, so a future reseed can reintroduce the question silently.

**O-08 — CLOSED.** The floor is now stated in all three faces and `compute` is untouched:

- `rule` line 1666: "The quote is the price of the extended time, with the young-driver share and the
  register lodgement charge added to it and the cover credit taken off it, **taken as nothing where
  that comes out below nothing**, and rounded to the nearest cent once at the end."
- `compute_basis.result` line 1732: the same sentence verbatim.
- `baseline.rule` line 1811: the same sentence verbatim.
- `compute` line 1711: `RND(MX(0, extension_price + yd_share + lodgement_charge - cover_credit), 2)`
  — byte-identical to revision 2, which is why no value moved.

The wording now matches its sibling `trips_ext_mileage_topup_pricing`, which carried the same floor
sentence all along. Check 2 passes on this binding.

**O-09 — NO CHANGE, correctly.** `trips_ext_extension_quote` still declares
`subject: [trips_extension_charge_posted]` while its tool writes a `trips_extension_requests` row.
Unchanged, still an observation, still no consequence: base's
`extension_decision_window` `applies_to: [trips_extension_charge_posted]`, so it does not bind a
register-row write.

### findings (revision 3)

**O-10 — observation — the unclaimed base fragment is unopposed only once "package" is read as
retired.** Set out in full under O-06 above. Figures: on the documented baseline the ceiling caps
the grant at 1250 miles, which is 2.5 blocks of 500; on the ceiling near-miss it caps at 2250, which
is 2.5 blocks of 900; under a reading that applies "part packages are not sold" to blocks those
become 1000 and 1800. No scored value is affected on either task. Bears on task 0.

**O-11 — observation — the O-07 reseed constraint is prose and ungated.** The disposition is right,
but nothing mechanical prevents a later reseed from placing a telematics and a host reading on one
handover, at which point base's tie-break and the extended flat sum would diverge with no
declaration covering them. Bears on both tasks.

**Carried forward unchanged:** O-02, O-03 (revision 1); O-09 (was O-04). **Closed this round:**
O-06, O-08. **Judged and accepted:** O-07.

**O-12 — observation — superseded figures survive as dated, negated citations; judged acceptable.**

Two superseded figures remain on disk, twice each: `770.00` in task 0 and `106.62` in task 1. This
auditor read every occurrence and judges that the sibling difficulty's stricter convention — reword
so the change is named rather than the number — **does not compel rewording here**, because these
are not bare citations: each sits in a reporting clause ("reported … as", "asserted that"), each is
negated in the same sentence ("no reading reaches 106.62"; "770.00 was computed with the
fifteen-dollar bulk concession that applied before …"), each stands beside the corrected figure and
its derivation, and every change-log entry now carries a round marker. `design_rationale` is also
not in the rollout's visible context, so a superseded figure there cannot mislead a solving agent.
Adopting the sibling's convention scenario-wide would be a defensible editorial choice; it is not a
defect of this artifact. Full reasoning in `1.md` revision_3 §`the residual superseded figures —
judged`. Bears on both tasks.

## closing_checklist (revision 3)

Written after both tasks' revision_3 frozen sections and comparisons were complete.

**The difficulty closes.** Both tasks pass all four relationships; every round-1, round-2 and
round-3 item is closed, fixed or judged and accepted.

| item | state |
| --- | --- |
| per-task files one-to-one with the tasks, `_difficulty.md` alongside; old revisions traceable | **yes** — three files, each carrying revisions 1, 2 and 3 in order, nothing overwritten |
| every comparison section carries a PASS | **yes** — `0.md` and `1.md` revision_3 both PASS on all four relationships |
| extended policies fully covered; the M tasks' scopes pairwise disjoint, each spanning its whole tree | **yes**, unchanged and re-verified against the revealed `charter_scope` |
| task tools and GT closed; each tool an independently generated, frozen uuid8 | **yes** — `task_tools.py` byte-identical for the third round |
| every tree: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥ 1 `owner=user` problem, no cycle; the difficulty's edges a DAG | **yes** — both trees n = 1 with one `value_input` edge and an `owner=user` root; two disjoint edges, acyclic |
| every computation a self-sufficient baseline giving a definite number ≠ gold | **yes** — 1250 / 1166.00 / 139.39 / 285.12, all four independently recomputed |
| 4–6 factors per computation, ≥ 2 `parameter` and ≥ 1 `method`; ≥ 1 multi-source and ≥ 1 cross-difficulty per task | **yes** — 6/5/5/5 |
| every ladder ≥ 3 tiers stated in full in its own rule, tiers distinct in outcome and pairwise disjoint as stated | **yes**, re-verified mechanically |
| every factor bears weight against an honest baseline | **yes** — all 21, every figure matching the artifacts' `factor_sensitivity` |
| every computation has a tier-flipping near-miss | **yes** — 3600 → 2250 and 814.40 → 1589.00; 108.42 → 86.73 and 192.53 → 182.53 (plus 108.42 → 105.91) |
| cross-difficulty rows follow the other product's charter | **yes**, and the round-3 sweep surfaced a further confirmation this auditor had not made itself: 728.00 is right on Premier's `greater_of_daily_and_percent` basis (14 × 52.00 = 728.00 against 45 % of 1084.16 = 487.87) |
| every base/extended conflict declared, every declaration verbatim, every exemption sound | **yes** — six declarations across four disjoint fragments and two other base sentences, all verified verbatim; the fifteen exemptions audited in revision 2 and the one unclaimed fragment judged in revision 3 (**O-10**) |
| proof fields free of figures from the previous revision | **yes** — swept with the auditor's own oracle over both files; every current-world assertion true, and the only superseded figures are dated, negated citations (**O-12**) |
| **policy self-consistency** | **PASS** on both tasks |
| **the problem tree holds** | **PASS** on both tasks |
| **factors bear weight** | **PASS** on both tasks |
| **policy → task unique solution** | **PASS** on both tasks |
| instantiation-stage gates re-run on the final form | **not re-run by this auditor** (write domain is this directory only; artifacts untouched). The brief's read-only re-run reports all seven green on the final artifacts |

### item disposition across all three rounds

| id | first raised | final state |
| --- | --- | --- |
| the override **pattern** (21 tiered factors) | r1 | **SWEPT**; six declarations verified, fifteen exemptions audited sound |
| F-01 / 0-A, F-02 / 0-B, F-03 / 1-A, F-04 / 1-B, F-05, F-05b / 1-C | r1 | **CLOSED** (r2) |
| F-06 / 0-C / 1-D(a), 1-D(b) | r1 | **CLOSED** (r2) |
| **1-F** | r2 | **CLOSED** (r3) — figure now checkable, independently recomputed as 75.65 → 1059.10 → 105.91 |
| O-01, O-05 | r1 | **FIXED** (r2) |
| 0-D, 1-E | r1 | **ACTED ON** (r2) |
| **O-06**, **O-08**, **1-G**, **1-H** | r2 | **CLOSED** (r3) |
| **O-07** | r2 | **ACCEPTED** (r3) — not codable in the DSL, prosing alone would reinstate F-05, constraint recorded with its evidence |
| O-02, O-03, O-09 (was O-04) | r1/r2 | **NO CHANGE, correctly** |
| **O-10**, **O-11**, **O-12** | r3 | observations, no consequence on either scored solution |

### verdict roll-up (revision 3)

| task | policy self-consistency | problem tree | factors bear weight | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | **PASS** |
| 1 | PASS | PASS | PASS | PASS | **PASS** |

**Both tasks pass the source-layer audit; this difficulty passes.** Three round-3 observations are
recorded for whoever carries the scenario forward, none of them grounds for rework. No artifact was
edited by this audit and no fix was arranged.

---

# revision_4

Round 4 re-audit. Revisions 1–3 above are preserved unaltered. This round applies a test none of
the earlier rounds and no gate applies: **for every rule sentence and every ladder tier, if a reader
had only that sentence and not the expression beneath it, would they compute the same number?**

## charter_global_frozen (revision 4)

- freeze time: 2026-09-22, **before** any GT field of either task was read in this round

| input | revision 3 | revision 4 | action |
| --- | --- | --- | --- |
| `trips.extended.yaml` | `ce70b0729c53feff…` | `dd7d913eb8ee7a1c1549014d4d9c70913b4dbf88305e98bd88fd3b2f155a08d5` | **changed → re-derived in full** |
| `task_tools.py` | `d15df91eaeb2deac…` | `d15df91eaeb2deac…` | unchanged (fourth round) |
| masked `0.json` | `4d25e61d100375b9…` | `4d25e61d100375b9…` | **unchanged** |
| masked `1.json` | `697052275ed16f44…` | `697052275ed16f44…` | **unchanged** |

Both worlds and the tool module are byte-identical; only the charter's prose moved. Base section
re-verified: `diff` against `blueprint/products/trips.yaml` empty, `git diff --stat` over
`blueprint/` empty. Fields permitted / masked as before; nothing from a revealed GT is in this
section.

**Nothing in `compute` moved.** Re-derived independently: all six scored values, all four baselines
and all 21 sensitivities are identical to revision 3 (3600 / 814.40 / 108.42 / 192.53; baselines
1250 / 1166.00 / 139.39 / 285.12). The reworker's assertion holds.

### method — the prose-alone test, applied mechanically

This auditor has already seen earlier rounds' `compute`, so simulating a naive reader is not
available to it. It used the stronger and un-foolable converse: **extract every number-fixing
machine feature from every compute binding mechanically, then ask of each whether a sentence of the
prose determines it uniquely.** Features extracted: every `RND` and its nesting depth, `int()`
truncation, `-(-x//y)` ceilings and bare `//` floors, `MX(0,·)` floors, `MN(·)` caps, `MX(1,·)`
guards, `ABS`, every `field='value'` filter, every `DAYS(·)` with and without `+1`, every `LATEST`
tie-break field, and every division. 68 features across the four policies. Each was then adjudicated
by hand against the rule, the ladder `when`/`method` texts and the `compute_basis` quotation.

### rule_compute_equivalence (revision 4) — feature by feature

**Counting conventions — now pinned by a general clause in every policy.** Policies 1 and 2 carry a
four-limb sentence; policies 3 and 4 carry its first limb plus local sentences. Each limb was
checked against the expression on task 0's dates:

| limb | expression | check |
| --- | --- | --- |
| "how long the trip has run … the day it started not counted and the day of handling counted" | `DAYS(actual_start, NOW)` | 2026-08-05 → 2026-09-18 gives **44**; inclusive-both would be 45, exclusive-both 43. **Exact** |
| "how many days of the reserved period are still to run … the day of handling not counted and the day of return counted" | `DAYS(NOW, trip_end)` | 2026-09-18 → 2026-10-09 gives **21**. **Exact** |
| "how many days have passed since a reading … the day of the reading not counted and the day of handling counted" | `DAYS(latest, NOW)` | 2026-09-16 → 2026-09-18 gives **2**. **Exact** |
| "the days of the reserved period are counted from the first day of that period to the last, both days counted" | `DAYS(start, end) + 1` | **66**. **Exact** |

The three `days_covered` tiers are separately pinned — "both that day and the day of return counted"
(= `DAYS(latest, end)+1` = 24 and `days_to_return+1` = 22) against the fall-through's "with the day
of return left out" (= `days_to_return` = 21). `days_charged`'s three tiers likewise. **PASS.**

**Roundings — now pinned, including position.** `trips_ext_mileage_topup_grant` needs none (integer
miles throughout). The other three carry 2, 3 and 6 "brought to the nearest cent" clauses
respectively, and each was matched to its `RND`: the per-cent spreading and its re-multiplication in
the young-driver limb ("the daily figure the spreading gives is brought to the nearest cent, and the
amount charged over is brought to the nearest cent in its turn"); the lifted daily rate and the
extension price ("brought to the nearest cent, and the price of the extended time is brought to the
nearest cent in its turn"); the young-driver share ("once the spreading and the taking have both
been done **and at no earlier step**", which is exactly the single outer `RND`); the cover credit;
and each assembly ("brought to the nearest cent **again once those have been put together**", which
resolves the revision-3 "rounded once at the end" that in fact rounded an intermediate). **PASS.**

**Floors, caps, ceilings and truncation.** `MX(0,·)` on `shortfall` ("comes out at nothing or less
… must cover nothing"), on `headroom` ("where no room is left, no miles are granted"), on
`net_block_price` ("where the concession would come to more than the block price the block price
less the concession is taken as nothing"), on `effective_rate` ("where that leaves a rate below
nothing, no surcharge is owed"), and on both assemblies ("taken as nothing where that comes out
below nothing"). `-(-x//y)` ceilings on `blocks` ("the smallest whole number of blocks that cover")
and `extended_days` ("rounded up to the next whole day"). `MX(1,·)` on both of those ("never fewer
than one block", "never fewer than one day"). `int()` truncation on `result` ("whole miles with no
part mile granted") and inside `line_price` ("each whole priced block … and nothing for the miles
left over"). `MN(·)` caps on `result` (the ceiling clause) and `extra_hours` ("held to the longest
further time the reservation can still take"). **All pinned. PASS.**

**Filters — the class the render audit exposed.** Every `field='value'` restriction in every
aggregate was checked against the prose:

| binding | filter | prose | verdict |
| --- | --- | --- | --- |
| `granted_miles` (pricing) | `event_type` + `grant_reason='purchased_package'` | "which are the miles granted to it as a purchased top-up **and not the allowance granted to it when the reservation was confirmed**" | **pinned** (B-1/P-1) |
| `elec_fees`, `elec_fees_c`, `elec_fees_b` | `charge_basis='daily_protection_fee'` | "the **daily** protection fees…" plus, in all three policies, "The fees counted are the daily protection fee lines raised on that election **and those alone**; a line raised on it for anything else — a young-driver protection surcharge, a level-change difference, an additional-driver fee, a deductible or a credit — is not a daily protection fee and is not counted." | **pinned** (B-1/P-1) |
| `granted_to_date` (grant) | `event_type` only, **no** `grant_reason` | "the included miles already granted to the reservation" — unrestricted, and now explicitly contrasted with the pricing policy's restricted reading | **pinned** |
| `daily_base` | `charge_basis='base_rate'` | "the **base-rate line** standing on the reservation" | **pinned** |
| `deposit_count` | `charge_basis='deposit'` | "a deposit line stands on the reservation" | **pinned** |
| `overage_count` | `charge_basis='mileage_overage'` | "no mileage overage has been charged on the reservation" | **pinned** |
| `surcharge_line` | `charge_basis='young_driver_surcharge'` | "the reservation carries the young-driver surcharge owed on the driver named on it" | **pinned** |
| `expired_count`, `expired_hours` | `request_status='expired'` | "an extension request that **expired without a decision**" | **pinned** |
| `declined_count`, `declined_hours` | `request_status='declined'` | "one that **was declined**" | **pinned** |
| `reading_count`, `avg_miles_per_day`, `driven_miles`, `used_miles_c` | `event_type='trips_mileage_usage_recorded'` | "odometer readings … booked against the reservation" | **see O-13** |
| **`change_count`** | **none — counts every request whatever its status** | "where one extension request **already stands on the reservation**" | **NOT pinned — see F-07** |

**LATEST tie-breaks.** `expired_hours` / `declined_hours` are now pinned: "where more than one such
request stands the one read is the latest of them **by the time it was put on the register**".
`latest_reading_date` is the deliberate refusal judged below. **PASS** apart from that.

### the two deliberate refusals — judged

**Refusal 1 — the unobservable guard. SOUND.** The feature is `MX(1, days_run)` in
`avg_miles_per_day = ABS(SUM(...)) / MX(1, days_run)`. Verified: `avg_miles_per_day` is read only by
`daily_mile_measure`, whose two non-fall-through tiers are each conjoined with "the trip has run for
at least four weeks", and whose fall-through does not read it at all. So the guard can bind only
where `days_run < 1`, which those conjunctions exclude. Writing it into the prose would describe a
branch that can never execute — an empty promise of the kind check 2 exists to catch, and the
mirror-image of the defect this round is about. **Refusing to prose it is right.**

**Refusal 2 — the same-day tie-break, converted to a seed invariant. SOUND, with a caveat.** The
feature is `LATEST('trips_usage','usage_date', date_field='usage_date', …)`. The evaluator keeps a
candidate only on a strictly greater key, so two readings sharing a `usage_date` are resolved by the
order the rows happen to sit in the table — which is not a business fact and cannot honestly be put
into business words. The three available moves are: state a business tie-break and code it
(impossible — the DSL has no grouping and no correlated anti-join, exactly as established for O-07
in revision 3); state it in prose and leave `compute` alone (which reinstates F-05, the very defect
of this round); or constrain the world so the tie never arises. The third is the only one that
neither mis-codes nor diverges. **Accepted.**

The caveat the coordinator anticipated is real and sharper than O-07's: `latest_reading_date` feeds
`days_since_reading` and `days_covered`, both of which reach the scored number, so a violated
invariant would move a scored value rather than merely an inert sum. Verified satisfied on both
worlds — task 0's readings sit at `(2026-08-19, mid_trip)`, `(2026-09-04, mid_trip)`,
`(2026-09-16, mid_trip)` and task 1's at `(2026-09-10, mid_trip)`, `(2026-09-15, mid_trip)`; no
handover in either world carries two. Recorded as **O-14**, which supersedes and widens revision 3's
O-11.

### findings (revision 4)

---

**F-07 — SOURCE-POLICY RED (new in round 4) — the register lodgement charge counts requests whose
prose does not say which requests count.**

*Verdict.* Red light, and it is a surviving instance of the exact class this round was convened to
sweep: `compute` pins a restriction — here, the *absence* of a status restriction — that no sentence
of the prose states, and the prose-alone reading yields a different scored value.

*Symptom.* A reader with the rule and the records, but not the expression, can defensibly compute
either $180.53 or $192.53 for task 1's `quoted_amount`.

*Root cause.* `change_count` is the only one of the charter's five `COUNT` bindings with **no**
filter, and the prose that is meant to carry it uses a standing verb whose scope it never fixes. Its
two immediate neighbours in the same policy, `expired_count` and `declined_count`, both carry a
`request_status` filter that the prose names in terms — so a reader has every reason to think the
third count is also about a particular kind of request.

*Evidence.* `trips.extended.yaml`, `trips_ext_extension_quote`:

- `compute`: `change_count: "COUNT('trips_extension_requests')"` — no `request_status`, so a request
  counts whatever has become of it.
- `rule`: "Where two or more extension requests already **stand on the reservation**, the register
  lodgement charge is twenty-four dollars; where one extension request already **stands on the
  reservation**, the register lodgement charge is twelve dollars; in every other case no register
  lodgement charge is made." The ladder's `when` texts are the same two phrases.
- The only gloss is "it is charged for putting a fresh request on the extension request register
  **while earlier requests already stand there**" — which repeats the verb without fixing it.
- No sentence anywhere in the policy says that a request counts whatever its status. Swept for
  "whatever", "whether", "status", "regardless", "no matter", "still", "every request", "all
  requests": **no hit** bearing on this count, against the explicit "and those alone" exclusion the
  same rework wrote for the fee limb.
- Base `trips_evt_extension` (trips.yaml:934), inherited and unopposed, cuts the other way: "A
  declined or expired request **leaves the reservation untouched**." A reader who takes that clause
  at its word does not count an expired request among those standing *on the reservation*.

*Demonstrated consequence.* Task 1's only register row,
`trips_extension_requests["93eac519-…"]`, carries `request_status: "expired"`. Recomputed on that
world, holding every other binding at its gold value:

| reading | `change_count` | `lodgement_charge` | `quoted_amount` |
| --- | --- | --- | --- |
| compute's (a request counts whatever its status) | 1 | $12.00 | **$192.53** (gold) |
| prose's, with base's "leaves the reservation untouched" | 0 | $0.00 | **$180.53** |

$180.53 is exactly the figure the task's own
`computations[1].factor_sensitivity` publishes as `register_lodgement_charge`'s baseline — i.e. the
number an agent is *supposed* to reach only by failing to find the factor's document. A reader who
finds the document and reads it carefully can reach it too. This is the same signature the
render-layer audit reported: the documents alone entail a value the artifact itself names as the
careless-reader error.

*Affected artifact and location.* `tasks/trip_booking_and_settlement_desk/trips.extended.yaml`,
`trips_ext_extension_quote`: `compute` binding `change_count`; the `rule` sentence beginning "Where
two or more extension requests already stand on the reservation"; the `compute_basis` quotation for
`change_count`; and both non-fall-through `when` texts of factor `register_lodgement_charge`. Bears
on task 1; task 0 does not touch this policy.

*Relation to previous revisions.* New in revision 4. It is the same class as B-1/P-1 — which this
round closed for the `grant_reason` and `charge_basis` filters — surviving on the one aggregate
whose restriction is a negative.

---

**O-13 — observation — "odometer readings" against the `event_type` filter.** Four bindings
(`reading_count`, `avg_miles_per_day`, `driven_miles`, `used_miles_c`) restrict to
`event_type='trips_mileage_usage_recorded'`, while the prose says "odometer readings … booked
against the reservation". Task 0's world also holds
`trips_usage["b3ad3cb6-…"]`, a `trips_fuel_level_recorded` row which carries a populated
`odometer_reading` of 40080 — so a reader counting "odometer readings" could count four rather than
three. Recomputed: `reading_count = 4` still clears the three-reading test and leaves
`granted_miles` at **3600**, and the row's `miles_delta` is 0 so the sums are untouched. **No
consequence on either world**, which is why this is an observation; but the prose does not exclude
it, and a world with two mileage readings plus a fuel row would flip the `unused_miles_basis` tier.

**O-14 — observation — two load-bearing world constraints are prose and ungated.** Revision 3's
O-11 (no two mileage readings on one handover, for base's telematics tie-break) and this round's
refusal 2 (no two mileage readings sharing a `usage_date`, for the `LATEST` tie-break) are the same
constraint stated for two reasons, and the second is load-bearing on the scored number through
`latest_reading_date` → `days_covered`. Both are recorded in prose and neither is checked by any
gate. Supersedes O-11. Bears on both tasks.

**Carried forward:** O-02, O-03, O-09, O-10, O-12 unchanged. **Closed this round:** B-1/P-1,
B-4/P-5 (verified below in each task file). **Judged and accepted:** both refusals.

### tie_scan (revision 4) — added on the coordinator's addendum

A sibling difficulty established that *stating* a rounding mode is not sufficient where the quantity
lands on an exact half-cent: the evaluator's `RND` rounds the binary double, so on a tie it falls
either side by representation, and a hand-rolled half-up inside `compute` fails the same way. The
addendum asked this auditor to determine, for every published figure of both tasks, whether the
arithmetic reaching it crosses a tie, and whether the prose's stated mode and the evaluator's `RND`
agree there.

**Method.** This auditor wrote an independent exact-rational re-implementation of the whole
evaluator — `SUM`, `COUNT`, `LATEST`, `CFIELD`, `XSUM`, `F`, `K` and `DAYS` all returning
`fractions.Fraction`, so every intermediate is exact and no binary double appears anywhere. `RND`
was instrumented to record, for each call, the **exact rational input**, whether `input × 10ⁿ` has
fractional part exactly ½, the half-up result computed by exact floor arithmetic, and the
evaluator's own `round(float(x), n)`. (An initial `Decimal` version was discarded: Decimal `//`
truncates toward zero where the evaluator's float `//` floors, which silently changed `blocks` from
4 to 3. `Fraction` floors correctly and reproduces the evaluator.)

**Coverage.** All **29 published figures** — 4 scored values, 4 `baseline_result`s and 21
`factor_sensitivity` figures — each re-derived end to end in exact rationals, plus the **6 published
near-miss figures** the `factor_trace` entries assert. 35 runs, **83 `RND` calls** in total.

**Result.**

| scan | figures | RND calls | exact half-cent ties | half-up vs `RND` disagreements |
| --- | --- | --- | --- | --- |
| 29 published figures | 29 | 68 | **0** | **0** |
| 6 published near-miss figures | 6 | 15 | **0** | **0** |

All 35 exact-rational results reproduce the artifacts' figures **exactly**: 3600 · 814.40 · 108.42 ·
192.53; baselines 1250 · 1166.00 · 139.39 · 285.12; and the 21 sensitivities
2700·2700·2700·3500·1250·2700 / 958.40·872.00·908.00·808.40·854.40 /
173.47·130.10·97.57·86.73·92.93 / 199.57·282.79·177.04·180.53·210.53. **Tie-freedom is confirmed,
and no divergence exists to report.** The nine instances pinned in prose this round are all
tie-free, so stating the mode is sufficient for each of them here.

**One corroboration worth recording.** The only exact half-cent anywhere in reach of this charter is
`86.73 / 14 = 1239/200 = 6.195`, which arises **solely on the superseded path B-4/P-5 removed** —
the reading in which the young-driver share is rounded at the spreading step before being taken for
each extended day. On the current compute the share is rounded once at the end, on
`108.42/14 × 2 = 15.48857…`, which is not a tie. So the B-4 fix did not merely name a mode: it moved
the computation off the one tie within reach. That tie was also latent-but-benign — half-up and the
evaluator's `round()` happen to agree at 6.195, both giving 6.20 — which is exactly the sibling's
"the pass was luck" situation, and the reason a pass on a scored value cannot establish tie-freedom.
Here it is established by full-domain scanning instead.

**Consequence for refusal 2.** The addendum asked that the second refusal be judged in this light,
and the light is favourable. The sibling's conclusion was that *no nameable convention is reliably
implementable on a tie, so the only sound design is that no scored quantity be one* — remove the tie
from the world rather than name a convention for it. That is precisely what refusal 2 does for the
same-day reading tie-break: the resolution is row order, which is not a business fact and cannot be
implemented from any primitive the DSL has, so the tie is removed from the world by invariant rather
than papered over by a sentence. Refusal 2 is not the weaker disposition the caveat feared; it is
the same disposition the sibling arrived at independently, applied to a different kind of tie. The
caveat that survives is only **O-14**: the invariant is prose and no gate enforces it.

## closing_checklist (revision 4)

**The difficulty does not close.** Task 0 passes all four relationships; task 1 carries one
SOURCE-POLICY RED, **F-07**, which is a surviving instance of the class this round was convened to
sweep.

| item | state |
| --- | --- |
| per-task files one-to-one, revisions 1–4 in order, nothing overwritten | **yes** |
| every comparison section carries a PASS | **no** — `1.md` revision_4 carries F-07 |
| scopes, tools, uuid8s, trees, owners, DAG | **yes**, unchanged and re-verified |
| every computation a self-sufficient baseline ≠ gold | **yes** — 1250 / 1166.00 / 139.39 / 285.12 |
| factor counts, ladders, disjointness, distinct outcomes | **yes**, re-verified mechanically |
| every factor bears weight; every near-miss flips a tier | **yes** — all 21; 3600→2250, 814.40→1589.00, 108.42→86.73, 192.53→182.53, 108.42→105.91 |
| every base/extended conflict declared; exemptions sound | **yes**, unchanged from revision 3 |
| proof fields free of stale figures | **yes** — swept with the auditor's own oracle; `179.44` flagged and then verified reachable, so no stale figure remains |
| **every number-fixing feature of `compute` pinned by prose** | **no** — 67 of 68 features pinned; `change_count`'s absent status filter is not (**F-07**), and one is an accepted refusal each (guard, tie-break) |
| **tie-freedom of every published figure** | **yes — established, not assumed.** 35 exact-rational re-derivations, 83 `RND` calls, **0 ties and 0 half-up/`RND` disagreements**; all 35 reproduce the artifacts' figures exactly |
| **policy self-consistency** | task 0 **PASS**; task 1 **RED** (F-07) |
| **problem tree** / **factors** / **unique solution** | **PASS** on both tasks |
| gates re-run on the final form | not by this auditor; the brief's read-only re-run reports all eight green, `check_traceability` now included |

### verdict roll-up (revision 4)

| task | policy self-consistency | problem tree | factors | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | **PASS** |
| 1 | **RED (F-07)** | PASS | PASS | PASS | **SOURCE-POLICY RED** |

### what this round answers

- **B-1/P-1: genuinely closed.** The two filters the render audit traced to the source are now
  stated with explicit exclusions naming the very rows each world holds.
- **B-4/P-5: genuinely closed**, and more substantively than claimed — the share-rounding clause
  keeps the computation off the only exact half-cent in reach of this charter.
- **Both refusals: sound.** The guard is unreachable, so prosing it would be an empty promise; the
  tie-break is unimplementable, and removing the tie from the world is the same disposition the
  sibling difficulty reached independently for rounding ties.
- **The sweep missed one instance.** `change_count` counts every extension request whatever its
  status, while the prose says only "already stands on the reservation" and inherited base says a
  declined or expired request "leaves the reservation untouched". On task 1 that is $180.53 against
  the gold $192.53 — and $180.53 is the figure the task's own `factor_sensitivity` publishes as the
  baseline. The sweep pinned every *positive* restriction and missed the one that is a **negative**:
  the absence of a filter is itself a fact the prose must state.
- **Tie-freedom: confirmed explicitly**, by independent exact-rational re-derivation of all 35
  published figures, with zero ties and zero divergences.

No artifact was edited by this audit and no fix was arranged.

---

# revision_5

Round 5 re-audit, narrow: confirm F-07 closed, judge the no-`overwrite` claim, verify the
negative-restriction sweep with this auditor's own oracle, judge the ungated invariant, and check
that the newly pinned sentences do not restate, weaken or strengthen a base clause. Revisions 1–4
above are preserved unaltered.

## charter_global_frozen (revision 5)

- freeze time: 2026-09-22, **before** any GT field was read in this round

| input | revision 4 | revision 5 | action |
| --- | --- | --- | --- |
| `trips.extended.yaml` | `dd7d913eb8ee7a1c…` | `944183b0733f6f229e94108bf2c2f067730adec48335fdfafa71341476e1ef60` | **changed → re-derived in full** |
| `task_tools.py` | `d15df91eaeb2deac…` | `d15df91eaeb2deac…` | unchanged (fifth round) |
| masked `0.json` / `1.json` | `4d25e61d100375b9…` / `697052275ed16f44…` | identical | **unchanged** |

Base section re-verified byte-identical; `git diff --stat` over `blueprint/` empty. `overwrite`
block counts unchanged at 3 / 1 / 1 / 1, consistent with the claim that none was added.

**Nothing in `compute` moved.** All six scored values, four baselines and 21 sensitivities
re-derived identical to revision 4.

### F-07 — verified CLOSED

The rule now carries, as its own sentence: "**A request stands on the register whatever has become
of it — submitted, under the host's review, approved, declined, expired or withdrawn alike — and
each is counted**, because what this charge answers to is the request already lodged on the register
and not anything the reservation has since done; that a declined or an expired request leaves the
reservation itself untouched is why it is the register, and not the reservation, that this count is
taken over." Both non-fall-through ladder `when` texts moved from "on the reservation" to "on the
extension request register against the reservation", and the `compute_basis` quotation for
`change_count` is the status enumeration itself.

The prose-alone reading that produced $180.53 is foreclosed: `expired` is named in the enumeration,
so a reader cannot drop task 1's only register row. **Closed by moving the prose, not the compute —
the divergence is gone from the reading, and the scored value is unchanged at $192.53.**

### the no-`overwrite` claim — judged SOUND

The claim is that taking the count over the register rather than the reservation *agrees* with base,
so no supersession is owed. Tested against this auditor's own check-1 criterion — does any base
sentence reach a different conclusion about the scored quantity on any world?

- **Base fixes no value for this quantity.** `trips_evt_extension` has no lodgement charge at all.
  The only base figure in the neighbourhood is `modification_fee_amount` on
  `trips_evt_payment_recovery`, and revision 2's F-05b analysis — which this audit judged sound and
  has not disturbed — established that it triggers on a date change, which lodging a request is not.
  There is therefore no base quantity for extended to contradict.
- **Base:929** ("taken onto the extension request register **rather than applied to the reservation**
  straight away") positively *establishes* the register as a locus distinct from the reservation.
  The extended reading follows it rather than departing from it.
- **Base:934** ("A declined or expired request leaves the reservation untouched") is **cited as the
  reason** for the choice of locus, not restated as a rule of this policy and not retired. Its own
  content is untouched and remains true under the extended reading: the $12 charge is a component of
  a *quote* on a register row, and the tool leaves "its dates, its allowance and its balance … as
  they were" (task_tools.py:126–129).

**An `overwrite` here would in fact be wrong.** `overwrite` declares a base clause retired and
replaced. Base:934 is not retired — it is relied upon. Declaring it superseded would remove from
force the very sentence the extended rule offers as its ground, leaving the reader with the
inference and not the premise. The claim that none is owed is correct, and it is the same
distinction that closed F-05b/1-C, applied to the *locus of a count* rather than the *trigger of a
fee*. **Sound.**

One minor note, recorded as **O-15**: the extended sentence paraphrases base:934 near-verbatim ("a
declined or an expired request leaves the reservation itself untouched"). Citing a base clause as a
ground is legitimate, but a near-verbatim paraphrase inside an extended rule will drift if base is
ever reworded. No consequence today.

### the base-clause check the coordinator asked for — no override by a new door

The sentence to scrutinise appears in all four policies: "The readings counted wherever this rule
speaks of the reservation's odometer readings are the records its mileage record holds as readings
of miles driven, which are the records that book miles against the allowance, and those alone; a
reading of the fuel tank or the traction battery is not one of them whatever else it notes, and
**every reading of miles driven counts whoever took it — the marketplace's telematics, the host or
the guest alike — since a reading that another supersedes books no miles against the allowance and
so adds nothing to what the readings have booked.**"

Against base `trips_evt_mileage_allowance` (trips.yaml:743): "A telematics reading is authoritative
where one exists; a host or guest reading stands only where no telematics reading covers the same
handover, and a reading taken during a post-trip audit supersedes the reading taken at the return."

- **Restate?** No. The extended sentence says nothing about which reading is authoritative. It says
  what a *superseded* reading contributes to a sum — nothing — and therefore that summing all
  mile-booking rows is safe.
- **Strengthen?** No. It adds no condition to base's test and narrows no one's rights.
- **Weaken?** This is the live question, because "every reading counts whoever took it" read alone
  would count a host reading base excludes. The sentence supplies its own reconciliation in the same
  breath: it counts them all *because* a superseded reading books no miles. On that reading the
  extended sum equals the base sum exactly, and base's authority rule is left entirely in force —
  the extended policy simply observes that the ledger has already applied it.

**Verdict: no undeclared override.** The reconciliation is explicit, correct, and stated rather than
assumed, which is the opposite of the class. It does carry one conditional dependency, recorded as
**O-16**: the reconciliation holds because superseded readings book no miles. Were a seed ever to
carry a superseded host reading with a non-zero `miles_delta`, the extended flat sum would count it
and base would not. No world of this difficulty does — and the invariant of O-14 excludes the
configuration that would produce one — so no consequence is demonstrable; but the sentence's
agreement with base is conditional on a property of the records rather than unconditional.

### the negative-restriction sweep — verified with this auditor's own oracle

The sweep that missed F-07 was also reported clean, so this auditor built its own rather than
checking the reworker's. Method, independent of the reworker's: for every aggregate call in every
`compute`, take the filter keys it imposes; take the union of (a) every filter key any sibling call
imposes on that same table anywhere in the charter and (b) every column of that table in
`db_schema.json` whose name ends in `_type`, `_basis`, `_status`, `_reason`, `_source`, `_point`,
`_segment` or `_code`; subtract the imposed keys and the holding/correlation keys. What remains is
the set of dimensions a reader could assume are restricted and which the expression leaves open.

**Result: 19 of 23 aggregate calls carry at least one such dimension — the same count the reworker
reports, reached independently.** Adjudicated dimension by dimension against the prose:

| table | open dimension | pinned by | verdict |
| --- | --- | --- | --- |
| `trips_usage` | `usage_source` | "every reading of miles driven counts **whoever took it** — the marketplace's telematics, the host or the guest alike" | **pinned** |
| `trips_usage` | `fuel_type`, `event_type` | "the records that book miles against the allowance, **and those alone**; a reading of the fuel tank or the traction battery is **not** one of them" | **pinned** (also closes O-13) |
| `trips_usage` | `grant_reason` (on the grant totals) | "the included miles already granted to the reservation, **whatever those miles were granted for**" — and, in the pricing policy, the converse "the miles granted to it **as a purchased top-up and not** the allowance granted when the reservation was confirmed" | **pinned, in both directions** |
| `trips_usage` | `reading_point` | no explicit clause, but the definitional sentence closes the set by what the records *do* ("book miles against the allowance, and those alone"), not by where they were taken | **closed by definition** |
| `trips_charges` | `waiver_code`, `event_type` (overage, deposit) | "a line once raised for one counting as charged **however it was afterwards treated**"; "a deposit line stands on the reservation, **whatever was afterwards done about it**" | **pinned** |
| `trips_charges` | `waiver_code`, `event_type` (base rate) | "every line raised for the base rate, taken together and as each was raised, **a credit or a reversal raised against one of them being a line of its own and not taken off it**" | **pinned** — and this is the goodwill-credit near-miss made explicit |
| `trips_charges` | `waiver_code` (young-driver surcharge) | "every young-driver surcharge line standing on the reservation taken together, as each was raised **and whatever was afterwards done about it**" | **pinned** |
| `guestplan_charges` | `coverage_segment`, `event_type`, `adjustment_reason` | "the daily protection fees charged on it … **however many lines they stand as and whenever they were raised**", with "and those alone" plus the naming exclusion list | **pinned** |
| `trips_extension_requests` | `request_status` | the F-07 status enumeration | **pinned** |

**Zero open dimensions remain with any consequence.** This auditor's oracle found nothing the
reworker's sweep missed. The one dimension with no explicit clause, `reading_point`, is foreclosed
by a closed definition rather than by an enumeration, which is a sound way to close it — and it is
worth noting that this is the strictest of the residuals: applying it wrongly (counting only
handover readings) would take task 0's `reading_count` from 3 to 0, so the definitional sentence is
load-bearing and it does close the set.

### O-13, O-14 — judged

**O-13 — CLOSED.** "a reading of the fuel tank or the traction battery is not one of them whatever
else it notes" excludes task 0's `trips_fuel_level_recorded` row by kind, whatever
`odometer_reading` it carries.

**O-14 — half closed, half accepted with the risk recorded.** The first half (a superseded reading
books no miles) is now a rule sentence rather than an invariant, which is the right direction: it
converts a world constraint into prose that is true of the records. The second half — two readings
sharing a `usage_date`, where `LATEST` ties and the evaluator resolves by row order — remains an
invariant, now checked by the authoring sweeper on every run rather than only asserted.

**Judgement.** Mechanised checking is materially better than prose alone: it makes the invariant
falsifiable and it runs. It is not equivalent to a gate, because it runs when *this* author runs
*this* sweeper, and the failure mode is a future reseed by another hand or another tool. That matters
here more than the reworker's account allows, and for a reason worth stating: the invariant is
load-bearing on a **scored** input, not merely on an inert one. `latest_source` — which decides
`reading_handling_charge` at $0 / $12 / $6 — is a `LATEST` over the same rows. On task 0 the latest
reading is `host_report` and the handling charge is $12.00; two readings sharing 2026-09-16 with
different sources would have the tie decide $0.00 against $12.00, moving `purchase_amount` between
$802.40 and $814.40. So the resolution is **accepted for this revision** — the invariant is stated,
reasoned, mechanically checked, and verified satisfied on both worlds by this auditor's own check —
and the residual risk is recorded as **O-17** rather than closed.

### findings (revision 5)

**O-15 — observation** — the extension-quote rule paraphrases base:934 near-verbatim while citing it
as a ground. Legitimate as a citation; it will drift if base is reworded. No consequence.

**O-16 — observation** — the reading-authority reconciliation is conditional on superseded readings
booking no miles. True of both worlds and of the data model the rule describes; not enforced.

**O-17 — observation, supersedes O-14** — the same-day `LATEST` invariant is now mechanically
checked by the authoring sweeper but by no gate, and it is load-bearing on a scored input
(`latest_source` → the handling charge, $0/$12/$6 on task 0), not only on `latest_reading_date`. A
reseed performed without that sweeper could reintroduce the tie silently.

**O-18 — observation** — `line_price_basis`'s fall-through `method` text is the only ladder string in
the charter that is not a character-exact substring of its rule: the rule reads "**The standard**
line price is …" and the ladder "the line price is …". The method *is* stated in the rule; the
difference is the tier-neutral article. Unchanged since revision 2 and adjudicated benign in each
round; recorded once so it is not re-found.

**Carried forward:** O-02, O-03, O-09, O-10, O-12 unchanged. **Closed this round:** F-07, O-13, and
the first half of O-14.

### tie_scan (revision 5)

Re-run because the charter moved, although only its prose did. All 29 published figures re-derived
end to end in exact rationals: **68 `RND` calls, 0 exact half-cent ties, 0 half-up/`RND`
disagreements**, all 29 reproducing the artifacts' figures exactly. Tie-freedom holds.

## closing_checklist (revision 5)

**The difficulty closes.** Both tasks pass all four relationships. Every finding raised across five
rounds is closed, fixed, or judged and accepted with its residual risk recorded.

| item | state |
| --- | --- |
| per-task files one-to-one, revisions 1–5 in order, nothing overwritten | **yes** |
| every comparison section carries a PASS | **yes** — `0.md` and `1.md` revision_5 both PASS on all four |
| scopes, tools, uuid8s, trees, owners, DAG | **yes**, unchanged and re-verified |
| every computation a self-sufficient baseline ≠ gold | **yes** — 1250 / 1166.00 / 139.39 / 285.12 |
| factor counts, ladders, tier disjointness, distinct outcomes | **yes**, re-verified mechanically |
| every factor bears weight; every computation has a tier-flipping near-miss | **yes** — all 21; 3600→2250, 814.40→1589.00, 108.42→86.73, 192.53→182.53, 108.42→105.91 |
| every base/extended conflict declared; exemptions sound; no override by a new door | **yes** — six declarations verbatim, fifteen exemptions audited, the register-locus claim judged sound, and the reading-authority sentences verified not to restate, weaken or strengthen base |
| every verbatim relation holds after the prose edits | **yes** — every `compute_basis`, `baseline.rule` sentence, `overwrite.replaced_by`, `policy_source` and ladder `when`/`method` re-checked; one cosmetic article difference recorded as O-18 |
| proof fields free of stale figures | **yes** — swept with this auditor's own oracle; only dated, negated citations remain |
| **every number-fixing feature pinned by prose** | **yes** — the 68 positive features (revision 4) and, now, every negative restriction: 19 bindings carrying an open dimension, all pinned or closed by definition |
| **tie-freedom of every published figure** | **yes** — 29 figures, 68 `RND` calls, 0 ties, 0 half-up/`RND` disagreements, all reproducing exactly under independent exact-rational re-derivation |
| **policy self-consistency / problem tree / factors / unique solution** | **PASS** on both tasks |
| gates re-run on the final form | not by this auditor; the brief's read-only re-run reports all eight green |

### verdict roll-up (revision 5)

| task | policy self-consistency | problem tree | factors | unique solution | verdict |
| --- | --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS | **PASS** |
| 1 | PASS | PASS | PASS | PASS | **PASS** |

### the five-round arc

| round | raised | outcome |
| --- | --- | --- |
| 1 | the undeclared-override pattern (F-01…F-05b), cross-difficulty evidence contradicting the guestplan charter (F-06), inert near-misses (1-D) | all closed by round 2 |
| 2 | a false proof figure (1-F) | closed round 3 |
| 3 | O-06 fragment overlap, O-07 uncodable tie-break, O-08 unstated floor, 1-G/1-H | all closed or accepted round 3–4 |
| 4 | the prose-alone class the render audit exposed: B-1/P-1 and B-4/P-5 closed, **F-07** found — the one aggregate whose restriction is a *negative* | closed round 5 |
| 5 | the negative-restriction sweep verified independently; the no-`overwrite` claim and the ungated invariant judged | closes |

### residual observations, for whoever carries the scenario forward

None is grounds for rework; all are recorded so they are not re-found.

- **O-17** (was O-14) — the same-day `LATEST` invariant is mechanically checked by the authoring
  sweeper but by **no gate**, and it is load-bearing on a scored input: `latest_source` decides
  task 0's handling charge at $0 / $12 / $6. A reseed performed without that sweeper could
  reintroduce the tie silently. This is the largest residual.
- **O-16** — the reading-authority reconciliation with base is conditional on superseded readings
  booking no miles; true of both worlds and of the data model, but not enforced.
- **O-10, O-12, O-15, O-18** — a base fragment unopposed only once "package" is read as retired; the
  dated superseded figures kept as citations; a near-verbatim paraphrase of base:934 that would
  drift if base were reworded; one cosmetic ladder-wording difference.
- **O-02, O-03, O-09** — docstring ordering words, base rules stating cross-problem orders that
  ground no edge, and a `subject` naming an event family its tool never emits.

**Both tasks pass the source-layer audit; this difficulty passes.** No artifact was edited by this
audit and no fix was arranged.
