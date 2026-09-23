# Policy-task audit — equipment_rental_desk / charter-global

## charter_global_frozen

- Freeze time: 2026-09-17 18:30 UTC. Auditor: independent policy-task auditor (not the instantiating agent).
- Frozen inputs, by sha256:
  - `env/env_0004_ski_resort_operator/tasks/equipment_rental_desk/rentals.extended.yaml` — `037babba56a5da1e1ff046935d00ab792ee32b06bd395a90d4f2f85143c1e716`
  - `env/env_0004_ski_resort_operator/tasks/equipment_rental_desk/task_tools.py` — `6c771267c9cd8dd18e81e29a8c6e4d6dd9042098557b92e5133ea1d0c86417af`
  - masked `tasks/0.json` — `137e3244c2c2ef97…`, masked `tasks/1.json` — `13e8bfa7aad6a57b…`
- Fields permitted at freeze: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/rentals.yaml` (and other products read only as cross-category charters); the whole of `rentals.extended.yaml` and `task_tools.py`; each task's `frozen_time`, `user_scenario`, `initial_state`.
- Fields explicitly masked at freeze: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state`.
- Entry conditions supplied by the coordinator and cited, not re-run here: EXTENDED / TASK-TOOL-CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all PASS; TRACEABILITY is the single gate that cannot pass before the KB render step. Masked views were built by whitelist and their hashes match the files on disk. Entry conditions are **complete**.

### policy_conflict_scan

The base section of `rentals.extended.yaml` (lines 1–1210) is **byte-for-byte identical** to `blueprint/products/rentals.yaml`; the only addition is a comment banner at lines 1211–1215 introducing `extended_policies`. Verified by `diff`.

Seven extended policies, all `category: rentals`, all writing to `rentals_holdings` / `rentals_ledger`:

| policy | trigger | subject | computes | target_tool |
| --- | --- | --- | --- | --- |
| `rentals_ext_damage_assessment` | state_due | rentals_damage_charge | damage_charge_usd | `assess_returned_kit_damage_f0dbd642` |
| `rentals_ext_late_handin_fee` | state_due | rentals_fee_charge | late_fee_amount_usd | `raise_late_handin_fee_417b2597` |
| `rentals_ext_counter_settlement` | state_due | rentals_payment | payment_amount_usd | `settle_rental_balance_at_counter_64bcc7e2` |
| `rentals_ext_security_hold_settlement` | state_due | rentals_deposit_release | release_amount_usd | `release_rental_security_hold_9f65c28a` |
| `rentals_ext_model_change_fee` | state_due | rentals_swap, rentals_fee_charge | change_fee_amount_usd | `raise_model_change_fee_b751c3b4` |
| `rentals_ext_party_rate_charge` | state_due | rentals_rate_charge | rate_charge_amount_usd | `raise_rental_rate_charge_fcd244c0` |
| `rentals_ext_extension_charge` | on_request | rentals_extend, rentals_fee_charge | extension_charge_usd | `confirm_rental_extension_b56bb368` |

Overlapping subjects: three policies share `rentals_fee_charge` (`late_handin_fee`, `model_change_fee`, `extension_charge`). They are separated by `charge_category` in the tool bodies (`late_return_fee`, `swap_fee`, `extension_fee`) and by distinct `computes` names, so no two of them decide the same quantity. No two policies claim the same `(target_tool, computes)` pair.

Time anchors are all drawn from record fields (`due_date`, `returned_date`, `reserved_date`, `pickup_date`, `created_at`, lodging `departure_date`) against `NOW = frozen_time`. Cross-category reads are declared per policy in `cross_category` and match the categories actually reached by `EXISTS` / `CFIELD` / `XCOUNT` / `XSUM` in each `compute`.

Task scopes (derived from which policies each task's problem tree covers, not from the masked `charter_scope`):
- task 0: `damage_assessment`, `late_handin_fee`, `counter_settlement`, `security_hold_settlement`
- task 1: `party_rate_charge`, `model_change_fee`, `extension_charge`

Pairwise disjoint and jointly complete over the seven extended policies. **PASS.**

Conflicts found between base and extended are recorded under `### override_declarations`; conflicts internal to the extended charter are recorded under `### findings`.

### rule_compute_equivalence

Swept every policy sentence by sentence against its `compute_basis` and `compute`. Every quantity, window, filter, tier, branch, cross-category read, acting base, grouping, cap/floor and rounding point named in a `rule` has a verbatim `compute_basis` quotation and a restricted-expression implementation, **with the exceptions below**.

Sweeping back from `compute` to `rule`: no binding invents a basis the rule does not state. Every `factors[].ladder` tier condition is a sentence of its policy's `rule` and a branch of the `decides` binding, and every branch of each `decides` binding corresponds to a stated tier — **with the exception of `assessment_left_to_hold` (finding F-6)**.

Empty promises found in the `rule` — sentences with no `compute_basis` entry and no implementation anywhere in `compute` or the tool layer:

1. `rentals_ext_late_handin_fee.rule`, final sentence:
   > "Kit still out beyond the package's replacement threshold is treated as not coming back and is charged at the package's replacement value instead of under this rule."
   There is no `replacement` binding in that policy's `compute`, no `compute_basis` key mentioning it, and no `max_late_days_before_replacement` or `replacement_value_usd` anywhere in the compute chain (the two appear only in `baseline.params`). `result` is unconditionally `RND(billable_days * daily_figure * standing_share * exposure_uplift, 2)`. → finding **F-1**.

2. `rentals_ext_counter_settlement.rule`:
   > "Where the household holds a collective lodging reservation for the season, only the shop fees and the assessments raised on the agreement are taken at the counter, and what is left of the hire rate is moved to that reservation's folio."
   The first half is implemented (`collectable_now`); "what is left of the hire rate is moved to that reservation's folio" is implemented by nothing — no binding, no task tool of this difficulty writes to `lodging_folio` or `lodging_holdings.folio_balance_usd`, and the difficulty claims no lodging event type. → finding **F-2**.

3. `rentals_ext_damage_assessment.rule`, final sentence:
   > "Fair wear on edges and bases is not charged, and kit that never comes back is charged at the package's replacement value rather than assessed under this rule."
   Inherited verbatim in substance from base `rentals_deposit_and_damage`; no `compute` branch tests either condition. Recorded as observation **O-1** (it is a scope exclusion rather than a computed quantity, but on task 0 the only seeded finding carries `damage_code: base_gouge`, which makes the first half live).

Rounding convention: every `rule` says "rounded half up", and `RND` is evaluated as Python's `round()`, which is round-half-to-even. Neither task's gold chain lands on an exact half-cent, so the divergence does not bite on this difficulty; recorded as observation **O-2**.

### action_binding_and_uuids

Each `(target_tool, computes)` pair is claimed by exactly one policy (table above). Each policy's subject, `base_policy_refs`, target tool, docstring and terminal state admit one business reading. No docstring adds a confirmation, review, wait or procedure outside its policy; no docstring names another tool, and none states an action's position in a sequence — the only ordering words are `assess_returned_kit_damage_f0dbd642`'s "stands on the agreement's rental account at nil **until** it is assessed", which describes that same tool's own effect, and the Args convention "read from the rental agreement lookup **before** the call", which is about obtaining that call's own argument.

uuid8s, checked individually: `f0dbd642`, `417b2597`, `64bcc7e2`, `9f65c28a`, `b751c3b4`, `fcd244c0`, `b56bb368`. Seven distinct values, no shared prefix, no shared tail, no arithmetic or lexical sequence, no reuse. **PASS.**

Owners: `settle_rental_balance_at_counter_64bcc7e2` and `confirm_rental_extension_b56bb368` are `owner="user"`; the other five are `owner="agent"`. Both user tools are the target tool of a policy that sits in a task's problem tree, so both tasks have a customer's own write available.

Tool bodies judge no prerequisite: read every function body. Each is a single atomic write — `ctx.find` / `ctx.create` / `ctx.update` — with no branch on status, no aggregation, no raise, no error return and no hint. `assess_returned_kit_damage_f0dbd642` updates an existing nil finding row; the other six create a row and adjust one running quantity. **PASS.**

### prerequisite_graph

All seven policies fill `prerequisite` (four with `[]`). Five edges, all `kind: value_input`, all `form: state`, none carrying `fallback_reason` (correct, since none is action-form):

| blocked policy | problem | gate | resolved_by |
| --- | --- | --- | --- |
| `rentals_ext_counter_settlement` | `rentals_ext_damage_assessment` | `assessments_raised` | `assess_returned_kit_damage_f0dbd642` |
| `rentals_ext_counter_settlement` | `rentals_ext_late_handin_fee` | `shop_fees_raised` | `raise_late_handin_fee_417b2597` |
| `rentals_ext_security_hold_settlement` | `rentals_ext_counter_settlement` | `money_collected` | `settle_rental_balance_at_counter_64bcc7e2` |
| `rentals_ext_extension_charge` | `rentals_ext_party_rate_charge` | `rate_charged` | `raise_rental_rate_charge_fcd244c0` |
| `rentals_ext_extension_charge` | `rentals_ext_model_change_fee` | `change_fee_entries` | `raise_model_change_fee_b751c3b4` |

Every `problem` points at another extended policy id in this file; none points at a base policy or at itself. The whole graph is a DAG — two disjoint trees, `hold ← counter ← {damage, late}` and `extension ← {party_rate, model_change}` — with no cross-task edge and no cycle.

`kind` matches `gate` in every case: each gate name is a binding that genuinely exists in the blocked policy's own `compute` and is an *input*, never `result` — `assessments_raised` and `shop_fees_raised` in `rentals_ext_counter_settlement.compute`, `money_collected` in `rentals_ext_security_hold_settlement.compute`, `rate_charged` and `change_fee_entries` in `rentals_ext_extension_charge.compute`. Each `resolved_by` is exactly the depended-on policy's `target_tool`, and each named tool's body genuinely writes the row the gate's `effect` describes (`rentals_damage_charge` amount written onto the nil finding; a `rentals_fee_charge` row with `charge_category="late_return_fee"`; a `rentals_payment` row; a `rentals_rate_charge` row with `charge_category="rental_rate"`; a `rentals_fee_charge` row with `charge_category="swap_fee"`).

No `condition` is strengthened or weakened relative to the sentence it restates. No authoring-viewpoint phrasing ("in this task", "at the opening", "the current world") appears anywhere in a `prerequisite` block. **PASS.**

### prerequisite_sentences

Four-point test on each of the five `policy_source` sentences. Every one is verbatim locatable in the blocked policy's **own** `rule` (confirmed by exact-substring search over each `rule` block).

1. `counter_settlement ← damage_assessment`
   > "The amount the guest is asked to hand over is fixed only after every finding a technician has entered against an item on the agreement carries the amount the guest bears for it."
   Ordering connective: "only after". What it waits on: "every finding … carries the amount the guest bears for it" — a record-visible state in the words the rental account uses, no performer, no action, no tool. No tool name, no policy id, no snake_case, no row id. Scope matches the edge `condition` exactly (both quantify over *every* finding on the agreement).
   State form, one write: the only write of this difficulty that puts an amount onto a finding entry is `assess_returned_kit_damage_f0dbd642` (it is the only tool that touches an existing `rentals_damage_charge` row). Derivation: the sentence says the counter figure waits on findings carrying an amount → the records show a `rentals_damage_charge` row standing at nil → `rentals_ext_damage_assessment`'s own rule is the only rule in the charter that says what amount a technician's finding carries → its write is the resolving action. One reading.

2. `counter_settlement ← late_handin_fee`
   > "The amount the guest is asked to hand over is fixed only after the account carries the shop fee owed for the days the kit stayed out beyond the date written on the agreement."
   Ordering connective: "only after". State form, no tool/performer/id. Three tools of this difficulty write `rentals_fee_charge` rows, but the sentence's qualifier "owed for the days the kit stayed out beyond the date written on the agreement" matches exactly one of them — `rentals_ext_late_handin_fee`, whose own rule opens "The fee for kit handed in after the date written on the agreement rests on the stretch of days the kit stayed out beyond that date." The model-change fee is "for a change of model or size" and the extension fee is "for keeping hire kit longer", neither of which the sentence describes. One reading.

3. `security_hold_settlement ← counter_settlement`
   > "What goes back to the guest is worked out only after the money collected against the agreement stands against the charges raised on it."
   Ordering connective: "only after". State form. Only `settle_rental_balance_at_counter_64bcc7e2` writes a `rentals_payment` row in this difficulty. One reading.

4. `extension_charge ← party_rate_charge`
   > "The charge for the extra days is fixed only after the hire rate for the days the agreement was written for stands on its rental account."
   Ordering connective: "only after". State form. Only `raise_rental_rate_charge_fcd244c0` writes `charge_category="rental_rate"`, and it is the only policy whose own rule says how "the hire rate for an agreement" is arrived at. One reading.

5. `extension_charge ← model_change_fee`
   > "The charge for the extra days is fixed only after every change of model recorded on the agreement carries the shop's fee owed for it."
   Ordering connective: "only after". State form, quantified over every change, matching the edge `condition`. Only `raise_model_change_fee_b751c3b4` writes `charge_category="swap_fee"`. One reading.

No blocked rule carries a second wording of the same dependency, another problem's tool name, another problem's id, a route or an aggregated chain. No depended-on rule restates the blocked rule's prerequisite sentence — checked `rentals_ext_damage_assessment.rule`, `rentals_ext_late_handin_fee.rule`, `rentals_ext_counter_settlement.rule`, `rentals_ext_party_rate_charge.rule` and `rentals_ext_model_change_fee.rule` for any "only after" / "before" / "until" clause pointing outward: none has one.

No base rule sentence is relied on to ground any edge; every edge rests on an extended rule sentence of its own. No cross-problem order is stated in any rule without a declared edge behind it — the only other ordering language in the charter is internal to one computation ("in the order set out here", "after the step before it", "taken off last of the three", "worked out once at the end"). **PASS.**

Note on a value dependency that carries no edge and needs none: `rentals_ext_security_hold_settlement.compute.charges_raised` sums `rentals_damage_charge` and `rentals_fee_charge`, so the damage assessment and the late fee do move its figure. The declared edges already force those two writes before the counter settlement and the counter settlement before the hold release, so the topological order an agent derives from the declared edges is the one the values require; no undeclared edge is needed and none is missing. Recorded for completeness only.

### override_declarations

Findings only; each affected task's file demonstrates or disclaims the consequence against its own world.

**Declared and sound.** Checked sentence by sentence against each `base_policy_refs` entry:

- `rentals_ext_damage_assessment` → `rentals_deposit_and_damage`: the waiver-share sentence is named in `overwrite` and replaced by the three-tier cover ladder. The remaining base sentences (assessment per item against the serial; fair wear not charged; kit that never comes back charged at replacement value; hold released once the assessment is settled; release-period counting) are inherited and not contradicted by this policy. `rentals_fitting_and_pickup` (day counting) and `rentals_pricing` (add-ons) are followed, not overridden.
- `rentals_ext_late_handin_fee` → `rentals_late_return`: the per-calendar-day accrual sentence is named in `overwrite` and replaced by the stretch × daily-figure formula, which carries the change of daily basis with it. The grace-period sentence governs `rentals_mark_overdue` only and is untouched.
- `rentals_ext_model_change_fee` → `rentals_swap_and_extension`: the change-fee sentence is named in `overwrite` and replaced by the window ladder.
- `rentals_ext_party_rate_charge` → `rentals_agg_party_pricing` (passholder sentence) and `rentals_pricing` (advance-booking sentence): both named and replaced.
- `rentals_ext_extension_charge` → `rentals_swap_and_extension` (extension sentence) and `rentals_pricing` (add-on sentence): both named and replaced.

**Undeclared overrides.**

**F-3 — dropped branch: the lesson bundle reduction, standing alone, is never produced.**
Base `rentals_agg_party_pricing.rule` states:
> "The lesson bundle reduction is taken where the same rider also holds a snowsports school booking over the same dates, and the lodging bundle reduction where the household holds collective lodging over the same dates. Where more than one bundle reduction would apply to the same agreement, only the largest is taken; they are never added together."
`rentals_ext_party_rate_charge.rule` states:
> "No bundle share is taken off. Where the rider holds a school booking for the season and the household holds a collective lodging reservation for the season, the larger of the package's lesson bundle share and its lodging bundle share is taken off, and the two are never added together; where the household holds a collective lodging reservation for the season and the rider holds no school booking for it, the package's lodging bundle share is taken off."
and `compute.bundle_share` is `MX(lesson, lodging) if (school and lodging) else (lodging if (lodging and not school) else 0)`.
For a rider who holds a school booking and whose household holds no lodging, base awards `lesson_bundle_discount_pct` (15.00 on the Basic, Junior and Sport packages) and extended awards 0. The `overwrite` block of `rentals_ext_party_rate_charge` names the base *passholder* sentence and the base *advance-booking* sentence; it does not name the base bundle sentence. This is the "dropped branch" form: base declares a branch extended's selector never produces, and the override is undeclared. Verdict **SOURCE-POLICY RED**. Bears on task 1 (the only task whose tree contains this policy); see `1.md` for whether it bites that world.

**F-4 — undeclared override: forfeiting the whole hold for a settlement made inside the package's own release period.**
`rentals_ext_security_hold_settlement` carries `overwrite: []` while listing `rentals_deposit_and_damage` in `base_policy_refs`. Base states:
> "The hold is released once the assessment is settled, in whole where nothing is owed and in part where something is."
> "The hold is released no later than the package's release period counted in business days from the day the kit was handed in."
The extended rule states:
> "Where the kit reached the counter at least that many days before the hold is settled and the account carries one payment or none against the agreement, the whole of the security hold standing is instead kept back."
with `prompt_settlement_days: 2`, implemented as `retained_amount: … else (hold_standing if settle_gap_days >= K('prompt_settlement_days') else …)` and therefore `result = RND(MX(0.0, hold_standing - hold_standing), 2) = 0.0`.
In the same situation — an assessment settled, the hold standing, the release made two or more days after hand-in and at most one payment on the account — base says the hold is released (in whole where nothing is owed, in part where something is) and extended says none of it goes back. On every package the trigger date, day 2, falls **inside** the package's own `deposit_release_days` window (3 for Junior/Basic, 5 for Sport/Performance, 7 for Demo, 10 for the lease), so the tier fires on a release the base charter treats as timely. The conflict is named in no `overwrite`. Verdict **SOURCE-POLICY RED**. Bears on task 0; see `0.md`.

**Observations on base sentences extended widens without naming them:**

- **O-3** — `rentals_pricing`: "a full seven-day block is charged at the package's weekly rate where that is the lower of the two" vs `rentals_ext_party_rate_charge`: "Where the agreement runs for **seven days or more** … every day is charged at a seventh of the package's weekly rate instead." For agreements of eight days or more the extended reading charges more than a weekly block, which base does not state; the two agree at exactly seven days. Not named in `overwrite`. Neither task runs seven days or more, so no consequence is demonstrable and it is not a red light.
- **O-4** — `rentals_pricing`: "The package's payment point decides when the money is taken: at booking, at collection, or at hand-in." `rentals_ext_counter_settlement` takes money at the counter irrespective of `payment_due_point`. Base governs when the *agreement value* falls due; fees and assessments arising after hand-in have no payment point in base, so this is a gap rather than a contradiction.

### factor_ladders

Per policy: declared factors, effect labels, `decides` bindings, disjointness of binding sets, tier counts, multi-source tiers, distinctness of outcomes, and whether the whole ladder is stated in the `rule` and implemented in `compute`.

| policy | factors | parameter | method | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| `rentals_ext_damage_assessment` | 6 | 5 | 1 | `delivered_kit_setaside`, `model_change_inspection_setaside`, `school_delivery_share` | lodging, lessons |
| `rentals_ext_late_handin_fee` | 5 | 3 | 2 | `overdue_stretch_anchor`, `household_standing_share` | passes, lodging |
| `rentals_ext_counter_settlement` | 4 | 3 | 1 | `counter_settlement_order`, `service_goodwill_allowance`, `resort_credit_offset` | lodging, passes |
| `rentals_ext_security_hold_settlement` | 5 | 4 | 1 | `folio_transfer_scope`, `household_standing_allowance`, `retained_amount_method` | lodging, passes, insure |
| `rentals_ext_model_change_fee` | 4 | 3 | 1 | `instruction_referral_share`, `kit_value_uplift_level` | lessons |
| `rentals_ext_party_rate_charge` | 5 | 3 | 2 | `passholder_share_level`, `bundle_share_level` | passes, lessons |
| `rentals_ext_extension_charge` | 6 | 5 | 1 | `free_extension_days` | passes, lodging |

Every policy declares four to six factors with at least two `parameter` and at least one `method`. Per task: task 0's four computations carry cross-difficulty factors reading `lodging`, `lessons`, `passes` and `insure`, and several multi-source factors; task 1's three computations carry cross-difficulty factors reading `passes`, `lessons` and `lodging`, and multi-source factors in each. Both floors met.

Within each policy the factors' `bindings` sets are pairwise disjoint, and every `decides` names an input binding, never `result`. Every ladder has three tiers, the fall-through counted, and the tier conditions as stated are pairwise disjoint. Every tier's condition is a sentence of its policy's `rule`, and every tier's value or method is drawn from that policy's `params` or from the package parameters of `blueprint/products/rentals.yaml`.

Labels checked for honesty. The eight `method` factors — `assessment_ageing_method`, `overdue_stretch_anchor`, `daily_figure_basis`, `counter_settlement_order`, `retained_amount_method`, `change_window_basis`, `day_rate_basis`, `chargeable_day_basis`, `extra_day_rate_basis` — each change how the quantity is arrived at (rounding direction, which date anchors the stretch, which day-count convention, which set of charges enters the figure, which divisor produces the daily rate), and each names a computation rule its own `rule` states. The `parameter` factors each substitute a number into an unchanged formula. `open_assessment_margin` is correctly `parameter`: its tiers select 125 / 150 / 100 per cent applied by the same multiplication.

**Defects found in the ladders:**

**F-5 — `daily_figure_basis` (`rentals_ext_late_handin_fee`) is a borderline `method` label.** Its first two tiers differ only in which package rate is uplifted (`multi_day_daily_rate_usd` vs `daily_rate_usd`, both × 1.35); only the fall-through, the flat `late_return_fee_per_day_usd`, changes the shape of the calculation. Recorded as observation **O-5**: the ladder does change the basis the daily figure is computed from, which is a scaling/basis family, so the label is defensible and no consequence is demonstrable.

**F-6 — `assessment_left_to_hold` (`rentals_ext_counter_settlement`) has a vacuous third tier.**
Ladder as declared:
- tier 1: "the security hold standing against the agreement is at or above the assessments raised on it" → `K('deferral_cap_usd')`
- tier 2: "the security hold standing against the agreement is below the assessments raised on it" → "the whole of the hold standing"
- tier 3: "otherwise" → `0`
Tiers 1 and 2 are jointly exhaustive over the reals ("at or above" ∪ "below"), so **no world reaches tier 3**. The `rule` states only the two sentences plus the baseline sentence "Nothing is left standing against the security hold."; `compute` reads `MN(assessments_raised, K('deferral_cap_usd')) if hold_standing >= assessments_raised else (hold_standing if hold_standing > 0 else 0.0)`, whose own third branch (`hold_standing < assessments_raised` **and** `hold_standing <= 0`) is a condition the ladder nowhere states. So the ladder divides customers into two groups, not three, and the branch structure of `compute` and of the ladder do not correspond. Outcomes also collide: where `assessments_raised` is 0, tier 1 yields `MN(0, 50) = 0`, the same value as tiers 2 and 3.
Verdict **SOURCE-FACTOR RED** (unreal ladder: a tier that no world selects, and tiers that coincide in outcome). Bears on task 0.

**F-7 — `retained_amount_method` (`rentals_ext_security_hold_settlement`) tier 2 is an outcome no rental business publishes.**
> "Where the kit reached the counter at least that many days before the hold is settled and the account carries one payment or none against the agreement, the whole of the security hold standing is instead kept back."
With `prompt_settlement_days: 2`, this forfeits the guest's entire security hold — up to 650.00 USD on the Demo package — on the strength of (a) the shop's own settlement falling two or more days after hand-in, a delay the guest does not control and which base expressly allows up to the package's release period, and (b) the account carrying at most one payment. Neither limb is a fault of the guest's, and no ski-hire business forfeits a whole deposit for them. This is the same defect as F-4 seen from the factor side rather than the base side.
Verdict **SOURCE-FACTOR RED** (a tier whose outcome that line of business would not publish as its treatment of customers in that situation). Bears on task 0.

**Observations on ladder wording and realism:**

- **O-6** — three tiers state a cap as their `value` where the `rule` and `compute` apply a minimum: `assessment_left_to_hold` tier 1 (`K('deferral_cap_usd')` vs `MN(assessments_raised, cap)`), `resort_credit_offset` tier 2 (`K('inactive_credit_cap_usd')` vs `MN(credit_standing, cap)`), `folio_transfer_scope` tier 2 (`K('folio_transfer_cap_usd')` vs `MN(uncollected_balance, cap)`). The `rule` in each case says "up to the … cap", so rule↔compute equivalence holds; it is the ladder's summary `value` string that overstates. No consequence where the capped quantity exceeds the cap.
- **O-7** — `resident_relief_days` (`rentals_ext_late_handin_fee`) tiers 1 and 2 coincide in outcome when the lodging departure date falls exactly one day after the due date: tier 1 then yields 1 day and tier 2's `travel_day_relief_days` is 1. The tiers are not "the same value" as stated (one is a span, one a constant), so this is not counted as a red light.
- **O-8** — `overdue_stretch_anchor` (`rentals_ext_late_handin_fee`) tier 1, "the shop holds a request on the agreement to keep the kit to a later date", takes no account of whether the request was granted, and `compute.notice_date` reads `LATEST('rentals_requests','requested_due_date', request_type='extension')` with no `outcome` filter. A declined request therefore moves the fee anchor in the guest's favour exactly as an accepted one would. Live on task 0.
- **O-9** — `rentals_ext_counter_settlement` tier 2 of `counter_settlement_order` leaves "the shop fees and the assessments … to the security hold" while the separate `assessment_left_to_hold` factor deducts the assessments against the hold a second time, and the `rule` directs that all three offsets "are each taken off the figure the counter step arrived at". On a world that selects tier 2 with assessments standing, the assessments come off twice. Neither task selects tier 2, so no consequence is demonstrable.
- **O-10** — `change_window_basis` (`rentals_ext_model_change_fee`) tier 1 redefines "the window between the agreement being taken and the change being asked for" as "the count of the dates the account shows the kit out, less one", a quantity that measures something else entirely. It is a day-count convention the ladder selects and the rule states, so it is not a red light, but the tier's name and the quantity it produces do not describe the same thing.
- **O-11** — `rentals_ext_model_change_fee`'s final rule sentence, "A rider who has used the package's allowance of changes is offered a new agreement at the day rate rather than a further change, and no fee under this rule arises for them", admits a second reading where the rider is already at the allowance. Live on task 1 (`swap_count == max_swaps_per_rental == 1`); see `1.md`.

Whether each factor bears weight is a fact about one world and is decided in each task's `factor_weight` section.

### findings

| id | verdict | subject | tasks it bears on |
| --- | --- | --- | --- |
| F-1 | SOURCE-POLICY RED | `rentals_ext_late_handin_fee.rule`'s replacement-threshold sentence is implemented nowhere | task 0 |
| F-2 | SOURCE-POLICY RED | `rentals_ext_counter_settlement.rule` promises a transfer to a lodging folio that no binding and no tool performs | task 0 |
| F-3 | SOURCE-POLICY RED | undeclared override: the lesson-bundle-alone branch of base `rentals_agg_party_pricing` is dropped by `rentals_ext_party_rate_charge` | task 1 |
| F-4 | SOURCE-POLICY RED | undeclared override: `rentals_ext_security_hold_settlement` forfeits the whole hold inside the base release period, with `overwrite: []` | task 0 |
| F-6 | SOURCE-FACTOR RED | `assessment_left_to_hold`'s third tier is unreachable and its outcomes collide | task 0 |
| F-7 | SOURCE-FACTOR RED | `retained_amount_method` tier 2 forfeits a whole security hold for the shop's own delay | task 0 |
| O-1 … O-11 | observation | see the sections above | as noted |

Each affected task's file demonstrates the consequence against its own world, or records that the defect does not bite there.

## closing_checklist

Written after both tasks' reveals. **The difficulty does not close out.** Step 4's checklist is completed honestly below, and the two conditions it fails are named.

| item | status |
| --- | --- |
| per-task audit files correspond one-to-one with the tasks, `_difficulty.md` alongside them | ✔ `0.md`, `1.md`, `_difficulty.md` |
| old revisions traceable | ✔ first revision; nothing overwritten |
| every comparison section carries a PASS | ✘ `1.md` PASSes on all four relationships; `0.md` carries SOURCE-POLICY RED, SOURCE-FACTOR RED and SOURCE-TASK RED |
| this difficulty's extended policies fully covered | ✔ all seven, four in task 0 and three in task 1 |
| the M tasks' scopes pairwise disjoint, each spanning its whole problem tree | ✔ `{damage, late, counter, hold}` and `{party_rate, model_change, extension}` |
| task tools and GT closed | ✔ every scored call names a tool of `task_tools.py`, and every tool is the target of a policy in a task's tree |
| each task tool uses an independently generated, frozen uuid8 | ✔ see `### action_binding_and_uuids` |
| every tree has one to three prerequisite problems | ✔ three in task 0, two in task 1 |
| at least max(n−1,1) `value_input` edges | ✔ 3 of 3 in task 0 (floor 2), 2 of 2 in task 1 (floor 1) |
| at least one problem resolved by an `owner=user` tool | ✔ `settle_rental_balance_at_counter_64bcc7e2` in task 0, `confirm_rental_extension_b56bb368` in task 1 |
| no cycle, including across tasks | ✔ five edges, two disjoint DAGs, no cross-task reference |
| every computation declares a self-sufficient baseline | ✘ `rentals_ext_damage_assessment.baseline.rule` states the waiver ladder in full, so the factor `waiver_cover_share`'s declared baseline is not what it states (F-5 / T0-5); the other six baselines are self-sufficient and none gives the gold number |
| four to six factors, 2 `parameter` + 1 `method`, per task ≥ 1 multi-source and ≥ 1 cross-difficulty | ✔ as declared — but `assessment_left_to_hold` does not survive the ladder tests (F-6), which leaves `rentals_ext_counter_settlement` at three surviving factors against a floor of four |
| every ladder ≥ 3 tiers stated in full in its rule, tiers distinct in outcome, conditions and outcomes ones the business holds | ✘ F-6 (a vacuous third tier with colliding outcomes) and F-7 (a tier no ski-hire business publishes) |
| every factor bears weight against an honest baseline, the baseline alone giving a definite number different from gold | mostly ✔ — 34 of the 35 declared factors across the two tasks bear weight and every whole-baseline fall-back is definite and different from gold; `waiver_cover_share`'s baseline is dishonest (T0-5) |
| instantiation-stage gates re-run on the final form | ✔ re-run 2026-09-17 18:40 UTC against the same hashes: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. TRACEABILITY still depends on the unpublished KB and is out of scope here. |

**Conclusion.** `task 1` passes the source-layer audit on all four relationships. `task 0` fails three of the four:

- policy self-consistency — T0-1 (the replacement threshold is triggered on its world and is implemented nowhere while the base sentences that carry it are inherited undeclared), T0-2 (a transfer to a lodging folio that nothing performs), T0-3 (`overwrite: []` against a base sentence the extended rule contradicts);
- factors bear weight — T0-4 (`retained_amount_method`'s forfeiture tier), T0-5 (`waiver_cover_share`'s dishonest baseline);
- unique solution — T0-1, which leaves a second defensible terminal state for the root problem.

The problem tree holds on both tasks, and every scored value of both tasks matched the auditor's independent derivation exactly. The difficulty therefore does **not** pass the source-layer audit, and the defects are reported here rather than fixed: this audit edits no artifact under `blueprint/`, `tasks/` or `erlbench/`, and arranges no fix.

**Read-isolation incident.** A shared-scratchpad collision caused this auditor's helper module to be replaced mid-run by another agent's file, whose execution printed computed results for the `snowsports_school_desk` difficulty. Disclosed in full in `0.md` → `### contamination_disclosure`. Nothing of `equipment_rental_desk` was revealed before both tasks' derivations were frozen, so neither blind derivation is void.

**Write-domain incident, disclosed.** Step 4's instruction to re-run the instantiation-stage gates was carried out at 2026-09-17 18:40 UTC. `skills/erl-task-instantiate/scripts/replay_tasks.py` writes back by default (`write_back = "--check" not in sys.argv`, line 134; the write at line 303), so that run rewrote `db_closure` and `db_closure_matches_initial_state` into `tasks/equipment_rental_desk/tasks/0.json` and `1.json` — a write inside `tasks/`, which this audit's write domain excludes. The effect was verified to be a no-op in substance: the gate reported the same closure figures as the coordinator's entry snapshot (38/38 `match True` and 27/27 `match True`), `frozen_time`, `user_scenario` and `initial_state` remain byte-identical to the masked views the derivations were frozen against, and a subsequent `--check` run left both files byte-identical. No audit conclusion rests on the rewritten fields. Recorded rather than concealed; the gate should be invoked with `--check` from an audit.

---

## revision_2

Re-audit round 2, 2026-09-17. Round 1 above is preserved untouched; nothing in it has been rewritten to accommodate what was learned after its reveal. This round is **not blind** — the round-1 GT was already seen — and its question is narrower: is each round-1 RED genuinely closed rather than reworded, has the rework introduced a new defect, has anything that passed in round 1 regressed.

### re_derivation_grounds

| input | round 1 | round 2 | disposition |
| --- | --- | --- | --- |
| `rentals.extended.yaml` | `037babba56a5da1e` | `45afb458a6df3fe4` | **CHANGED** → every charter-global section re-derived in full |
| `task_tools.py` | `6c771267c9cd8dd1` | `6c771267c9cd8dd1` | unchanged → `### action_binding_and_uuids`'s uuid8 and tool-body conclusions carried forward by reference on the strength of this hash; the `(target_tool, computes)` half was re-derived anyway because the charter moved, and still gives 7 unique pairs over 7 policies |
| `tasks/0.json` | `137e3244c2c2ef97` | `046fa0c431a2372b` | **CHANGED** → task 0 re-derived in full |
| `tasks/1.json` | `13e8bfa7aad6a57b` | `13e8bfa7aad6a57b` | unchanged **file**, but its three policies all live in the changed charter, so task 1's per-task sections were re-derived in full rather than carried forward |

Coordinator's gate snapshot on the reworked form cited, not re-run by this auditor: EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK; TRACEABILITY unchanged pre-render. `replay_tasks.py` was **not** re-run this round in either mode, so round 1's write-domain incident is not repeated.

The base section of `rentals.extended.yaml` (lines 1–1210) is still byte-for-byte identical to `blueprint/products/rentals.yaml`; verified by `diff`. No base policy was touched.

### charter_global_rederived

**Policy conflict scan.** Seven extended policies, same ids, same triggers, same subjects, same `computes`, same target tools as round 1. `(target_tool, computes)` pairs: 7 unique over 7 policies. Task scopes still pairwise disjoint and jointly complete.

**Overwrite declarations, re-swept.** Every `superseded_clause` in the charter is a verbatim substring of the named base policy's `rule` — checked mechanically across all ten entries, all pass. Counts moved: `late_handin_fee` 1 → **3**, `security_hold_settlement` 0 → **1**; the other five unchanged (`damage_assessment` 1, `counter_settlement` 0, `model_change_fee` 1, `party_rate_charge` 2, `extension_charge` 2).

**Prerequisite graph and sentences, re-derived.** Five edges, unchanged in every field. All `value_input`, all `form: state`, none carrying a `fallback_reason`. For each: the `policy_source` is a verbatim substring of the blocked policy's own `rule`; it carries an explicit ordering connective ("only after"); it names no tool, no policy id and no snake_case token; `resolved_by` is the depended-on policy's `target_tool`; the `gate` is a real binding name in the blocked policy's own `compute`; and the depended-on policy's rule does not restate the sentence. The graph is still a DAG with no cross-task edge.

**Factor ladders, re-derived.** Factor counts unchanged at 6 / 5 / 4 / 5 / 4 / 6 per policy in charter order, with `parameter`/`method` splits 5+1, 3+2, 3+1, 4+1, 3+1, 3+2, 5+1 — every policy still within four to six factors and above the 2-`parameter`, 1-`method` floor. Checked mechanically: every ladder has at least three tiers, no ladder has two tiers stating the same value or method, no factor `decides: result`, and within each policy the factors' `bindings` sets are pairwise disjoint. One ladder gained a tier — `bundle_share_level` is now four tiers (see **R2-F3**).

**Rule/compute equivalence, re-swept mechanically.** For every policy: every `compute_basis` quotation is a verbatim substring of its own `rule`, and every `compute_basis` key names a real binding. The two round-1 empty promises are **gone from the charter** — `grep` finds zero occurrences of "Kit still out beyond the package" and no occurrence anywhere of the hire rate being "moved to that reservation's folio" in `rentals_ext_counter_settlement`. One new gap was introduced: see **R2-N1**.

### verification_of_round_1_reds

Each item is judged against the artifact, not against the reworker's account of it.

**T0-1 — CLOSED.** Three things had to happen and all three did.
1. The unimplemented sentence is deleted: `grep -c "Kit still out beyond the package"` over the whole charter returns **0**.
2. The two base sentences that carried the replacement route are now each named in `rentals_ext_late_handin_fee.overwrite`, verbatim:
   - "Once the kit has been out beyond the package's replacement threshold it is treated as not coming back: late fees stop accruing, the package's replacement value is charged instead, and the security hold is applied against it." → replaced by "Kit that has reached a shop counter is charged under this rule for the whole stretch it stayed out, the package's replacement threshold neither stopping the accrual nor diverting the agreement to a replacement charge, and the security hold is not applied against it."
   - "Kit handed in after being charged as a replacement is refunded the replacement value less the late fees that had accrued to the threshold, and the shop, not the desk, decides whether the item is fit to go back into stock." → replaced by "The fee is never more than the package's replacement value."
   Both replacement sentences are carried in the policy's own `rule` and in its `baseline.rule`.
3. The surviving normative content is implemented: `result` is now `RND(MN(billable_days * daily_figure * standing_share * exposure_uplift, P('replacement_value_usd')), 2)`, and `compute_basis.result` quotes the cap sentence verbatim. `baseline.params` moved from `[late_return_fee_per_day_usd, max_late_days_before_replacement, replacement_value_usd]` to `[late_return_fee_per_day_usd, replacement_value_usd]`, matching what the baseline paragraph now needs.
   This is a substantive change of law, not a rewording: the threshold is now expressly declared to do nothing on returned kit, so the second reading round 1 demonstrated — late fees stopping at the threshold, a replacement value charged, the hold applied against it — is excluded by a sentence of the charter rather than left open. The merged semantics are unique.

**T0-2 — CLOSED.** `rentals_ext_counter_settlement.rule` no longer says "what is left of the hire rate is moved to that reservation's folio"; it now says "what is left of the hire rate **stands on the agreement to be collected another day**". This is the sharpest kind of close: the old sentence promised a transfer no binding computed and no tool could perform, and the new sentence describes the state the records are actually left in. Nothing else in the tier moved, so the figure the tier selects is untouched.

**T0-3 — CLOSED.** `rentals_ext_security_hold_settlement.overwrite` is no longer `[]`. It now names, verbatim, base `rentals_deposit_and_damage`'s "The hold is released once the assessment is settled, in whole where nothing is owed and in part where something is.", replaced by "The amount kept back is what is then left taken once over." — which is the real deviation, since the extended policy applies a retention multiple base does not. The second limb of the round-1 finding, the clash with base's release-period sentence, is closed not by declaration but by the tier rewrite under T0-4: a release made two or more days after hand-in no longer forfeits anything, so timing inside the package's own `deposit_release_days` window costs the guest nothing.

**T0-4 — CLOSED.** The offending tier read "the whole of the security hold standing is instead kept back". It now reads:
> "Where the kit reached the counter at least that many days before the hold is settled and the account carries one payment or none against the agreement, the greater of the amount kept back and the assessments raised on the agreement is instead kept back, taken to the cent and never more than what the agreement still owes."
implemented as `RND(MN(MX(retained_raw, assessments_standing), uncollected_balance), 2)`. The outcome is now one a hire shop does publish: where the guest has not settled at the counter, keep back at least what was assessed against the kit, and never more than the agreement actually owes. Total forfeiture is gone, and the cap at `uncollected_balance` also restores agreement with base's "in whole where nothing is owed" — where nothing is owed the tier keeps back nothing.

**T0-5 — CLOSED.** `rentals_ext_damage_assessment.baseline.rule` no longer carries the three-branch waiver ladder. The whole passage is replaced by one sentence: "The guest bears the full cover share of the amount left." `baseline.params` narrowed from `[replacement_value_usd, heavy_use_share_pct, full_cover_share_pct, partial_cover_share_pct, bare_cover_share_pct]` to `[replacement_value_usd, heavy_use_share_pct, full_cover_share_pct]`. A reader of the computation document alone now computes `guest_cover_share = full_cover_share_pct / 100 = 0.25`, which is exactly the factor's declared `baseline`. The baseline is honest, and the factor's document is now the only place the partial and bare shares can be found.

**T0-6 / F-6 — CLOSED.** Both live tiers of `assessment_left_to_hold` now carry the existence conjunct:
- "the account carries an assessment raised against the agreement **and** the security hold standing against it is at or above that assessment" → "the assessment raised, up to `K('deferral_cap_usd')`"
- "the account carries an assessment raised against the agreement **and** the security hold standing against it is below that assessment" → "the whole of the hold standing"
- "otherwise" → 0
The two are no longer jointly exhaustive, so the fall-through is reached by every agreement carrying no assessment — a common world, not an empty one. `compute.deferred_against_hold` matches branch for branch: `MN(assessments_raised, K('deferral_cap_usd')) if (assessments_raised > 0 and hold_standing >= assessments_raised) else (hold_standing if assessments_raised > 0 else 0.0)`. The round-1 collision at `assessments_raised = 0` is gone, because that world is now tier 3 by construction.

**F-3 — CLOSED, and closed the better of the two available ways.** Rather than declaring a deviation from base, the charter was brought back into line with it. `rentals_ext_party_rate_charge.rule` now ends its bundle passage "…; and where the rider holds a school booking for the season and the household holds no collective lodging reservation for it, the package's lesson bundle share is taken off." `compute.bundle_share` gained the matching branch, `compute_basis.bundle_share` quotes the full three-clause passage, and `bundle_share_level`'s ladder gained a third live tier valued `P('lesson_bundle_discount_pct')`. `overwrite` is unchanged at two entries, which is now correct: there is no longer anything to declare, because extended and base agree. A rider with a school booking and no lodging is awarded the lesson bundle share by both.

**O-6 — CLOSED.** All three ladder `value` strings that stated a cap where the rule and compute applied a minimum now state the minimum: "the credit standing, up to `K('inactive_credit_cap_usd')`", "the assessment raised, up to `K('deferral_cap_usd')`", "what the agreement still owes, up to `K('folio_transfer_cap_usd')`".

**O-T0-a — CLOSED.** `uncollected_balance` is now `MX(0.0, RND(charges_raised - money_collected, 2))`, and `baseline.rule` gained the matching words "…less the money collected against it, **rounded half up to two decimal places**, and it is never below zero." The binary residue that made the round-1 sensitivity figure 644.00 instead of the exact-decimal 645.00 is eliminated at source.

**O-T0-b — CLOSED at the seed.** See `0.md` → `## revision_2`.

### new_defects_and_regressions

**R2-N1 — new, observation: a binding introduced by the T0-4 rework has no `compute_basis` key.**
`rentals_ext_security_hold_settlement.compute` gained `assessments_standing: "SUM('rentals_ledger','amount_usd', event_type='rentals_damage_charge')"`. It is the only binding in all seven policies with no key of its own in `compute_basis` — every other one of the charter's bindings has one, verified mechanically. The quantity is not ungrounded: the rule says "the greater of the amount kept back and **the assessments raised on the agreement**", and `compute_basis.retained_amount` quotes that sentence verbatim. So this is a completeness gap in the binding-to-basis mapping rather than a drifting formula or an empty promise, no second reading arises from it, and no value moves. Recorded as an observation introduced by the rework, not a red light.

**R2-N2 — new, observation: the replacement text of one override is narrower than the base sentence it supersedes.**
`rentals_ext_late_handin_fee.overwrite` supersedes base's "Once the kit has been out beyond the package's replacement threshold it is treated as not coming back: late fees stop accruing, …" with a sentence that speaks only of "Kit that has reached a shop counter". Kit that is still out beyond the threshold is therefore covered by the base sentence in its supersession but by nothing in its replacement. This policy only ever fires on returned kit, and `overwrite` is scoped to the policy that declares it, so the reading that the override applies where the policy applies is available and sound. Neither task has kit still out beyond its threshold — task 0's kit is back, task 1's is not yet due — so no consequence is demonstrable. Observation only.

**R2-N3 — new, observation, and not a regression: `bundle_share_level`'s restored tier coincides in value with its first tier on most packages.**
Tier 1 is "the larger of `P('lesson_bundle_discount_pct')` and `P('lodging_bundle_discount_pct')`" and tier 3 is "`P('lesson_bundle_discount_pct')`"; wherever the lesson share is the larger of the two — Junior, Basic, Sport, Performance — the two tiers select the same number. The coincidence is entailed by base `rentals_agg_party_pricing`'s own "Where more than one bundle reduction would apply to the same agreement, only the largest is taken", so it is what the business does rather than one tier written as two; the four conditions genuinely divide customers into four groups (both holdings, lodging only, school only, neither) and all four are reachable. It is also **not a regression**: the same coincidence held between tiers 1 and 2 on the Sport and Lease packages in round 1, and round 1 did not flag it. Recorded for completeness.

**No regressions found.** Every conclusion round 1 reached and every check round 1 passed was re-run against the reworked charter: the base section is still verbatim, all ten `superseded_clause` strings are still verbatim base text, all five prerequisite edges still pass the four-point test, the graph is still a DAG, `(target_tool, computes)` is still one-to-one, the tool module is byte-identical, every ladder still has at least three tiers with no two stating the same outcome, every policy is still within the factor bounds and above the `parameter`/`method` floors, and no factor's bindings overlap. Per-task regression results are in each task file.

**Round-1 items the reworker recorded as not reworked — this auditor's judgement on that disposition.**

| item | disposition | judged |
| --- | --- | --- |
| O-1 (damage rule's fair-wear / never-comes-back sentence has no implementation) | not reworked | **right**, and now safer than it was: it is a scope exclusion introducing no quantity, and the seed change under O-T0-b removed the one world where a reader might have applied it |
| O-2 (`RND` is half-to-even while every rule says "half up") | not reworked | **right in scope, though the defect is real.** `RND` is the evaluator's, in `erlbench`, which the rework may no more edit than this audit may. It still bites one printed counterfactual (T1-2). It belongs on the runtime's account, not the charter's |
| O-5 (`daily_figure_basis` borderline `method` label) | not reworked | **right** — round 1 judged the label defensible and nothing has changed |
| O-T0-c (the fee anchor and the goodwill allowance both move on a *declined* extension request, on a package the charter forbids extending) | not reworked | **acceptable but the weakest of the dispositions.** `grep -c outcome` over the charter returns 0, so no tier anywhere filters on whether a request was granted. Round 1 recorded it as an observation because it creates no second reading, and that remains true, so it is not a red light either round; it is nonetheless the one realism point in this charter this auditor would have preferred addressed, and it is live on task 0 |
| O-T0-d (persona and record differ on whether she was told) | not reworked | **right** — not a conflict about an authoritative fact, and no computation reads `outcome` |
| T1-2 (the 100.66 sensitivity figure rounds against the rule's stated convention) | not reworked | **right**, same ground as O-2 |
| T1-3 (notice tier decided by date subtraction over a timestamp) | not reworked | **right** — the extended rule says "days … before the date", a date-to-date phrasing, and entails one value |
| T1-4 (the change-allowance sentence admits a literal reading on a world sitting exactly on the allowance) | not reworked | **acceptable.** Round 1 showed the literal reading is self-defeating — it would empty the policy on every package whose allowance is one — so the policy still entails 5.85 uniquely. The sentence survives verbatim in both the rule and the baseline rule |
| T1-5 (a package that takes its money at collection with no hire rate raised three days on) | not reworked | **right** — it is the premise the unmet prerequisite rests on, and base fixes when money is taken rather than when a charge is raised |

Round-1 observations **O-3, O-4, O-7, O-8, O-9, O-10, O-11** were not on the reworker's disposition list. Re-checked against the new charter: all persist unchanged, none acquired a demonstrable consequence, and none is a red light. O-8 is the charter-global half of O-T0-c and is judged with it above; O-11 is the charter-global half of T1-4; O-9 (the counter settlement's second tier leaves the assessments to the hold while `assessment_left_to_hold` deducts them again) still stands — `grep` still finds "the shop fees and the assessments are left to the security hold" — and still selects on neither task's world.

### closing_checklist_r2

Written after both tasks' round-2 reveals. **The difficulty closes out.**

| item | status |
| --- | --- |
| per-task audit files correspond one-to-one with the tasks, `_difficulty.md` alongside them | ✔ |
| old revisions traceable | ✔ round 1 preserved verbatim in all three files; round 2 appended under `## revision_2` / `### …_r2` headings, nothing overwritten |
| every comparison section carries a PASS | ✔ `0.md` → `### source_gt_comparison_r2` and `1.md` → `### source_gt_comparison_r2` both PASS on all four relationships |
| this difficulty's extended policies fully covered, scopes pairwise disjoint, each spanning its whole tree | ✔ four in task 0, three in task 1, unchanged |
| task tools and GT closed; each tool an independently generated, frozen uuid8 | ✔ `task_tools.py` byte-identical to round 1 (`6c771267c9cd8dd1`); `(target_tool, computes)` still 7 unique pairs over 7 policies |
| every tree has one to three prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥ one `owner=user` write, no cycle | ✔ 3 edges / floor 2 in task 0, 2 edges / floor 1 in task 1; user writes at `settle_rental_balance_at_counter_64bcc7e2` and `confirm_rental_extension_b56bb368`; graph re-derived and still a DAG |
| every computation declares a self-sufficient baseline | ✔ **now including `rentals_ext_damage_assessment`** — its `baseline.rule` no longer carries the waiver ladder and its `baseline.params` narrowed to match (T0-5 closed) |
| 4–6 factors, 2 `parameter` + 1 `method`; per task ≥1 multi-source and ≥1 cross-difficulty | ✔ 6/5/4/5/4/5/6 with splits 5+1, 3+2, 3+1, 4+1, 3+1, 3+2, 5+1; all surviving the ladder tests, `assessment_left_to_hold` included now that its fall-through is reachable |
| every ladder ≥3 tiers stated in full in its rule, tiers distinct in outcome, conditions and outcomes ones the business holds | ✔ re-derived mechanically; **T0-6 and T0-4 closed**, so no vacuous tier and no total-forfeiture outcome remains |
| every factor bears weight against an honest baseline, the baseline alone giving a definite number different from gold | ✔ 35 of 35 across the two tasks re-run and still moving their result; whole baselines 41.25 / 408.00 / 345.19 / 425.00 and 15.00 / 138.00 / 205.00, all definite and all different from gold |
| instantiation-stage gates re-run on the final form | ✔ cited from the coordinator's snapshot on the reworked form — EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK; TRACEABILITY unchanged pre-render. Not re-run by this auditor, so `replay_tasks.py`'s write-back is not triggered a second time |

**Conclusion.** All seven round-1 red lights — T0-1, T0-2, T0-3, T0-4, T0-5, T0-6/F-6 and F-3 — are closed, each verified against the artifact rather than against the reworker's account, and each closed by a change of substance rather than of wording: a deleted unimplemented sentence plus two new verbatim overrides and an implemented cap; a promise replaced by a description of the state actually reached; an empty `overwrite` filled; a total-forfeiture tier replaced by a capped, assessment-floored one; a baseline paragraph stripped of the ladder it was meant to be silent about; an existence conjunct that makes a fall-through reachable; and a dropped branch restored into agreement with base. Three round-1 observations were closed in passing (O-6, O-T0-a, O-T0-b), the last of them in the seed.

No round-1 conclusion regressed. Both tasks' gold values, owners, orders and terminal states are identical to round 1, every edge still bears weight — the `hold ← counter` edge now moving the root 628.00 → 478.51 instead of 628.00 → 0.00, a smaller but still decisive swing — and all 35 factors still move their results.

Three new items were found, all observations, none a red light: **R2-N1** (`assessments_standing`, a binding added by the T0-4 rework, is the only binding in the charter with no `compute_basis` key of its own, though the sentence behind it is quoted under `retained_amount`), **R2-N2** (one of the new override's replacement sentences is narrower than the base sentence it supersedes, reaching only kit that has come back), **R2-T0-a** (task 0's `design_rationale` says "six overwrite entries" where its scope carries five and its own enumeration lists five). **R2-N3** is recorded but is neither new in substance nor a defect.

With `policy self-consistency PASS + problem tree holds PASS + factors bear weight PASS + unique solution PASS` on both tasks, **equipment_rental_desk passes the source-layer audit at revision 2.**

No artifact under `blueprint/`, `tasks/` or `erlbench/` was edited in this round, and no fix was arranged. `replay_tasks.py` was not run in either mode, so round 1's write-domain incident was not repeated; no shared-scratchpad module was imported, so round 1's read-isolation incident was not repeated either.

---

## revision_3

Re-audit round 3, 2026-09-17. Rounds 1 and 2 above are preserved untouched. This is a **step-2 fallback from the render layer**, not a continuation of round 2's verdict: the KB rendered from the charter I passed was audited independently and returned `KB-RUNTIME RED` on both tasks, with the root cause in my own domain.

### method_limit_admitted

**The render-layer auditor found a defect my method could not have surfaced, and I should say exactly why rather than defend the rounds that missed it.**

The defect (P1) was that three `baseline.rule` paragraphs said several multiplicative adjustments "act on the [base] itself **rather than on one another's results**", while each `compute` formed a straight product in which the second adjustment *is* worked out on what the first left. On the late-hand-in policy, at daily figure 100, share 0.85 and uplift 1.20, the product gives 102.00 and the sentence entails 105.00.

In rounds 1 and 2 I recorded that relationship as PASS. Looking at what I actually did:

- My round-1 `task_independent_derivation` for that write ends with the row "`result` | 3 × 110.70 × 0.55 × 1.20 = 219.186 | **219.19**". I wrote the product form down directly. I never asked what "act on the daily figure itself rather than on one another's results" entails arithmetically — had I asked, I would have found that it forbids the product and then fails to say what to put in its place.
- My `rule_compute_equivalence` sweep checked that every `compute_basis` quotation is a **verbatim substring of the rule** and that every binding has a key. That establishes *locatability*, not *agreement*. I nonetheless listed "cap/floor, rounding mode, rounding point and interval counting convention" among the things swept, which overstated what the sweep did — the same overstatement a sibling auditor disclosed.
- My evaluator read the charter's `compute` and `eval`'d it. It was independent of the task file, which is what let it catch world-level defects, but it is structurally incapable of testing the compute against its own prose: it takes the compute as the definition of the arithmetic and so cannot notice when the prose defines a different one, or none.

So the honest answer to the question put to me is: **no, my method could not have surfaced a composition ambiguity in a baseline sentence, and the way I reported the sweep made it look as though it had been tested.** The gap is specific — I verified that prose was quotable and that compute was evaluable, and never that a reader of the prose and a runner of the compute land on the same number.

**What I did differently this round.** For every one of the seven computations, on both tasks, I wrote the arithmetic out from the rule and baseline prose alone — naming at each step what each share or amount acts on — and fixed those figures before evaluating any `compute` expression. Only then did I run the evaluator and compare. Both derivations are recorded in the task files, and they agree on all seven; where they agree it is now evidence, because they were produced independently. This does not repair rounds 1 and 2, which stand as written with their limit now stated.

### re_derivation_grounds_r3

| input | round 2 | round 3 | disposition |
| --- | --- | --- | --- |
| `rentals.extended.yaml` | `45afb458a6df3fe4` | **`8489ea9625250c62`** | CHANGED → all charter-global sections re-derived |
| `task_tools.py` | `6c771267c9cd8dd1` | `6c771267c9cd8dd1` | unchanged → tool bodies and uuid8s carried forward on this hash |
| `tasks/0.json` | `046fa0c431a2372b` | `046fa0c431a2372b` | unchanged **file**, changed charter → task 0 re-derived in full |
| `tasks/1.json` | `13e8bfa7aad6a57b` | **`0869f35765de3a7e`** | CHANGED → task 1 re-derived in full |

Coordinator's gate snapshot on the reworked form cited, not re-run: all gates OK, and **TRACEABILITY now OK** (0.json 24 copied / 0 missing; 1.json 19 / 0). `replay_tasks.py` not run in either mode. Work confined to the private scratchpad subdirectory. Base section still byte-for-byte identical to `blueprint/products/rentals.yaml`, verified by `diff` — no frozen artifact was edited to achieve any of this.

The 68 published documents are older than the charter and were not judged; per the brief, the charter is the object this round.

### composition_determinacy_r3

**The old idiom is gone.** `grep` over the whole charter returns **0** occurrences of "rather than on one another's results", of the bare "on one another's results", of `counter_settlement`'s variant "acts on another's result", and of the three policy-specific phrasings "act on the daily figure itself", "act on the package's change fee itself". The author's claim is confirmed at the artifact.

**Every composition statement in the charter, and whether it determines one arithmetic.** I enumerated every "act(s) on / taken off / added to / added once to" phrase in the file and classified all seven computations:

| computation | composition sentence(s) | form | determinate? |
| --- | --- | --- | --- |
| `damage_assessment` | "**Every set-aside and every share** in the steps set out here acts on the amount left after the step before it, and the amount left is rounded half up to two decimal places at each of those steps" | sequential | ✔ one arithmetic |
| `late_handin_fee` | "The daily figure is **first** taken at the standing share, and the figure that step leaves is **then** raised by the exposure uplift, so the uplift acts on what the share left and not on the daily figure the step before it started from; neither step is rounded before the fee is worked out" | sequential | ✔ |
| `counter_settlement` | "The credit …, the allowance … and the amount left standing against the hold are **three amounts in money rather than shares of anything**, and each is taken off the figure the counter step arrived at rather than off what another of the three has already left" | absolute, non-compounding | ✔ |
| `security_hold_settlement` | "What is moved to a folio and what is met by a protection plan are **both taken off what the agreement still owes** before the multiple is applied"; "The allowance is taken off the amount kept back **after** the multiple has been applied" | absolute + explicit ordering | ✔ |
| `model_change_fee` | "The package's change fee is **first** taken at the window share, the figure that step leaves is **then** taken at the instruction share, and the figure that step leaves is **then** raised by the uplift, so each of the three acts on what the step before it left and not on the package's change fee itself" | sequential | ✔ |
| `party_rate_charge` | "the passholder share acts on the days charged for at the day rate, the bundle share acts on **the amount the passholder step left**, and the advance booking share acts on **the amount the bundle step left**" | sequential | ✔ (was already so) |
| `extension_charge` | "The daily figure is **first** taken at the resident share, and the figure that step leaves is **then** taken at the notice share …; the helmet addition is added to the figure the two shares leave, and the extension fee is added once to the whole rather than to each day" | sequential + explicit join points | ✔ |

**The two settled forms are each used only where they hold.** The sequential form appears in the five computations whose adjustments are multiplicative shares, where compounding is what the compute does and what the sentence now says. The absolute form appears only in `counter_settlement`, whose three deductions are USD amounts — the sentence now says so outright ("three amounts in money rather than shares of anything"), which is the calibration the render auditor found missing when the same words governed shares elsewhere. `security_hold_settlement`'s two pre-multiple deductions are also absolutes and name their common base explicitly ("both taken off what the agreement still owes"); since both are amounts derived from that base and subtracted from it, the parallel and sequential readings coincide, so no third idiom is needed and none is used. **No computation is left in an unsettled form.**

**Reader and runner now land together.** For all seven computations, on both tasks, the prose-derived figure and the compute-evaluated figure agree — not only for the three rewritten policies. The derivations are in `0.md` → `### prose_first_derivation_r3` and `1.md` → `### prose_first_derivation_r3`; the agreement table is in each task's comparison section. The two computations the author says were already determinate (`party_rate_charge`, `damage_assessment`) I re-derived from prose independently, and they match to the cent, which is consistent with the author's account of why it moved the prose rather than the compute: where a sentence determines an arithmetic the compute must follow it, and where it determines none — as "rather than on one another's results" did not — moving the compute would have picked one of two readings arbitrarily. On the evidence of the artifact that reasoning holds: the discarded sentence forbade the product without saying what to substitute, so there was no determinate prose for the compute to be conformed to.

### p_series_and_param_changes_r3

**P4 — closed by declaration, and it loses nothing the tasks need.** `rentals_ext_party_rate_charge.overwrite` gained a third entry naming base `rentals_pricing`'s "A charge is raised against an agreement only while the agreement stands in the reserved, confirmed, picked_up or overdue state." verbatim, replaced by "The standing requirement on raising a charge reaches the hire rate alone: the hire rate is raised against an agreement only while that agreement stands in the reserved, confirmed, picked_up or overdue state, and the shop fees and the assessments raised on an agreement stand or fall by the standing their own rules fix."

Checked directly, because a retired gate is exactly the kind of change that can quietly remove a constraint:
- **For the hire rate, nothing is lost.** The replacement re-states the same four allowed states for `rentals_rate_charge`, which is precisely the width of base's own `chargeable_agreement_state` (`applies_to: [rentals_rate_charge]`). The constraint is unchanged; only the sentence's over-wide *reading* is retired.
- **For shop fees, a real rule takes over.** Base `rentals_late_return.fee_bearing_agreement_state` applies to `rentals_fee_charge` and allows `confirmed, picked_up, overdue, returned, cancelled, no_show`. Task 0's agreement stands `returned` and task 1's `picked_up`; both inside it. This is what the replacement points at, and it exists.
- **What was removed was a false constraint, not a real one.** At face width the retired sentence forbade both the damage assessment and the late-hand-in fee on a `returned` agreement — which task 0 requires, and which would make every damage assessment impossible, since an assessment is by construction made on handed-in kit. Removing it restores the behaviour both rounds' gold already had.
- **The gate count drop is accounted for.** Task 1 shows 5 base gates where round 2 showed 6; task 0 is unchanged at 5. Task 1 raises two `rentals_fee_charge` writes (the change fee and the extension entry) alongside one `rentals_rate_charge`; the over-wide sentence had been realised against a fee write that `fee_bearing_agreement_state` already governs, and that duplicate realisation is what fell away. No write lost its only gate.

One residue, recorded as **R3-N1** below: the replacement says assessments "stand or fall by the standing their own rules fix", and no rule fixes a standing for `rentals_damage_charge`. Enumerating every base eligibility entry, the gates are `rentals_reserve`, `rentals_reserve_load`, `rentals_rate_charge`, `rentals_pickup`, `rentals_deposit_hold`, `rentals_deposit_release` ×2, `rentals_mark_overdue`, `rentals_fee_charge`, `rentals_cancel`, `rentals_close` — there is none for `rentals_damage_charge`, and the extended damage policy states no standing of its own.

**P2, P3, P5, P6, P7 — treated as classes.** Confirmed at the artifact where they touch the charter's determinacy: `extension_allowed` now has a reader, which closes P7 — `rentals_ext_extension_charge`'s `result` is `RND(…, 2) if P('extension_allowed') else 0.0`, backed by a new rule sentence, "Where the package is one the collective does not extend, no charge for extra days arises under this rule and the agreement runs to the date written on it", quoted in `compute_basis.result`. The remaining P-items are render-layer notes about wording and windows that bear on no scored value in either task; I did not re-litigate them.

**Parameter changes — exactly the two claimed, and no others.** Diffing every policy's `params` block against round 2: `rentals_ext_damage_assessment.full_cover_share_pct` 25 → **20**, and `rentals_ext_extension_charge.early_notice_pct` 90 → **92**. Nothing else moved in any of the seven blocks.

### half_cent_sweep_r3

I ran my own sweep rather than accepting the author's count, instrumenting `RND` to record every argument it receives.

**Within the scope that matters — the figures the task files actually assert — zero ties remain.** Over gold, every single-factor baseline substitution and every whole-baseline substitution on both tasks (the exact set that becomes `expected`, `baseline_result` and each `factor_sensitivity[].baseline_result`), **no argument reaches `RND` on an exact half cent at all**. The three diverging arguments of round 2's world — 31.415, 166.175 and 100.665, the last being my own round-1 observation T1-2 — are gone, and no new one replaced them. The fix is therefore complete on the declared surface, and slightly better than the author's own report of "one reachable tie remaining".

**Outside that scope the divergence is still live, and is worth stating precisely.** Extending the sweep to all 256 combinations of factor-baseline substitutions (every subset, both tasks) surfaces seven half-cent arguments, five of which differ between half-up and half-even:

| task | argument | half up | half even | reached by |
| --- | --- | --- | --- | --- |
| 0 | 304.425 | 304.43 | 304.42 | `late_handin_fee` with `resident_relief_days` + `kit_exposure_uplift` both at baseline |
| 0 | 98.175 | 98.18 | 98.18 | `damage_assessment`, two factors at baseline — agrees |
| 1 | 24.925 | 24.93 | 24.92 | `party_rate_charge`, three factors at baseline |
| 1 | 29.325 | 29.33 | 29.32 | `party_rate_charge`, four factors at baseline |
| 1 | 33.235 | 33.24 | 33.24 | `party_rate_charge`, two factors at baseline — agrees |
| 1 | 84.745 | 84.75 | 84.74 | `party_rate_charge`, two factors at baseline |
| 1 | 99.705 | 99.71 | 99.70 | `party_rate_charge`, two factors at baseline |

Every one of these lives in a counterfactual world formed by substituting **two or more** factors' baselines at once. No such figure is declared anywhere in either task file, so nothing the artifact asserts depends on the rounding convention, and no relationship fails. It is recorded as **R3-N2**: the underlying divergence between the charters' "rounded half up" and the evaluator's half-to-even `RND` (my round-1 observation O-2) is unrepaired and unrepairable from the charter, and the tie-free world the author searched for is tie-free only over the figures the task declares. That is the right scope to have searched; the residual matters only if a later revision ever declares a multi-factor sensitivity figure.

### structural_regression_r3

Every check rounds 1 and 2 passed, re-run mechanically against the new charter:

| check | result |
| --- | --- |
| base section verbatim vs `blueprint/products/rentals.yaml` | ✔ identical, lines 1–1210 |
| every `superseded_clause` a verbatim substring of its base policy's rule | ✔ all **11** entries (was 10; `party_rate_charge` 2 → 3 for P4) |
| every `compute_basis` quotation a verbatim substring of its own rule | ✔ |
| every binding has a `compute_basis` key | ✘ one exception, `assessments_standing` — **R2-N1 persists**, see below |
| no orphan `compute_basis` key | ✔ |
| `(target_tool, computes)` one-to-one | ✔ 7 / 7 |
| factor counts within 4–6, ≥2 `parameter`, ≥1 `method`, per policy | ✔ 6 / 5 / 4 / 5 / 4 / 5 / 6 |
| every ladder ≥3 tiers, no two tiers stating the same outcome, no `decides: result` | ✔ |
| factor `bindings` pairwise disjoint within each policy | ✔ |
| 5 prerequisite edges: `policy_source` verbatim in own rule, `resolved_by` = depended-on `target_tool`, `gate` a real binding | ✔ |
| prerequisite graph acyclic, no cross-task edge | ✔ |
| all 35 factors bear weight on their task's world | ✔ |
| all 5 prerequisite edges bear weight | ✔ |

**R2-N1 persists, unchanged.** `rentals_ext_security_hold_settlement.compute.assessments_standing` is still the only binding in the charter with no `compute_basis` key of its own. It was raised in round 2 and was not in the render layer's P-series, so it appears simply not to have been carried forward. The sentence behind it — "the greater of the amount kept back and **the assessments raised on the agreement**" — is still quoted verbatim under `retained_amount`, so the quantity is grounded and no second reading arises. Observation, not a red light, and now a **second-round-standing** one.

**R2-N2 persists**, unchanged and still with no demonstrable consequence: the late-return override's replacement text reaches only "Kit that has reached a shop counter", while the base sentence it supersedes also covered kit still out. Neither task has kit still out beyond its threshold.

**R2-N3** is unaffected; `bundle_share_level` is unchanged at four tiers.

### new_findings_r3

**R3-N1 — new, observation: P4's replacement names a rule that does not exist, for assessments.**
The replacement sentence ends "…and the shop fees and the assessments raised on an agreement stand or fall by the standing their own rules fix." For shop fees that is true — base `rentals_late_return.fee_bearing_agreement_state` fixes it. For assessments it is not: enumerating all eleven base eligibility entries, none applies to `rentals_damage_charge`, and the extended damage policy states no standing of its own. A reader following the pointer for an assessment finds nothing at the other end.

Consequence: **none demonstrable, and the direction is safe.** With no standing rule an assessment is ungated, which is what both tasks need and what gold does — task 0 assesses on a `returned` agreement. The narrowing removed a constraint that P4 showed should never have applied and added none in its place, so nothing the tasks need is lost. What remains is an over-promise in the replacement sentence. Recorded rather than red-lighted because it creates no second reading, no missing solution and no conflict: it names an authority that is absent, where absence is the correct outcome.

**R3-N2 — new, observation: the rounding divergence survives outside the declared surface.** Set out in full in `### half_cent_sweep_r3`.

**R2-T0-a (round 2) — superseded by the rework.** Task 0's `design_rationale` was rewritten this round; the "six overwrite entries" miscount is re-checked in `0.md` → `## revision_3`.

**No regression found.** Every conclusion rounds 1 and 2 reached and every check they passed was re-run against the new charter and the new worlds, and all hold. The seven round-1 red lights remain closed; the two round-2 observations that persist are named above; task 0's gold is untouched and task 1's two moved values are accounted for by the world change.

### closing_checklist_r3

Written after both tasks' round-3 reveals. **The difficulty closes out at revision 3.**

| item | status |
| --- | --- |
| per-task files one-to-one with the tasks, `_difficulty.md` alongside; old revisions traceable | ✔ rounds 1 and 2 preserved verbatim; round 3 appended |
| every comparison section carries a PASS | ✔ both tasks PASS all four relationships at `### source_gt_comparison_r3` |
| extended policies fully covered, scopes pairwise disjoint | ✔ four in task 0, three in task 1 |
| task tools and GT closed; uuid8s independently generated and frozen | ✔ `task_tools.py` byte-identical since round 1 |
| trees: 1–3 prerequisite problems, ≥ max(n−1,1) `value_input` edges, ≥1 `owner=user` write, acyclic | ✔ unchanged; all 5 edges re-run and load-bearing |
| every computation rests on a self-sufficient baseline | ✔ and every baseline now also **determines one arithmetic** — the gap that produced the render-layer RED |
| 4–6 factors, 2 `parameter` + 1 `method`, ≥1 multi-source and ≥1 cross-difficulty per task | ✔ 6/5/4/5/4/5/6 |
| every ladder ≥3 tiers, tiers distinct in outcome, conditions and outcomes ones the business holds | ✔ |
| every factor bears weight against an honest baseline; baseline alone gives a definite wrong number | ✔ all 35 |
| instantiation-stage gates re-run on the final form | ✔ cited from the coordinator's snapshot; **TRACEABILITY now OK** on both tasks |

**Conclusion.** The render layer's `KB-RUNTIME RED` had its root cause in my domain, and the source change closes it. The indeterminate idiom is gone from the charter — zero occurrences of "rather than on one another's results" or any of its variants — and each of the two settled forms of words is used only where it holds: the sequential form on the five computations whose adjustments compound, the absolute form only on `counter_settlement`, whose three deductions the sentence now says outright are "amounts in money rather than shares of anything". No computation is left in an unsettled idiom, and `security_hold_settlement`'s two pre-multiple deductions name their common base explicitly rather than reaching for a third form.

The decisive test is the one my earlier rounds did not run: for all seven computations on both tasks, a figure derived from the prose alone, fixed before any formula was evaluated, agrees with the compute and with the GT — not only on the three rewritten policies but on `damage_assessment` and `party_rate_charge`, which were already determinate, and on the two absolute-amount computations. Reader and runner now land together everywhere.

P4's narrowing was checked against the risk the coordinator named and loses nothing the tasks need: the hire rate keeps exactly its base standing, shop fees fall to a real rule that exists, and what was removed was a false constraint that would have made every damage assessment impossible. Task 1's gate count fell by one because a duplicate realisation against a fee write dropped away, not because a write lost its only gate. The task-1 world change is coherent field by field, and its single persona edit — "the Sunday, the fourteenth" → "the Monday, the fifteenth" — is correct on the calendar and consistent with every other date the persona states.

The half-cent sweep is complete on the surface that matters: over gold, every single-factor baseline and every whole-baseline substitution on both tasks, **no argument reaches `RND` on an exact half cent at all**. Five diverging ties survive in multi-factor counterfactual worlds that no task file declares (**R3-N2**).

Four observations stand, none a red light and none grounds for rework: **R3-N1** (P4's replacement promises assessments a standing rule that does not exist — safe, because ungated is the outcome the tasks need), **R3-N2**, **R2-N1** (`assessments_standing` still the only binding without its own `compute_basis` key), **R2-N2**, plus **R2-T0-a / R3-N3**, the override tallies in both tasks' `design_rationale`, wrong in two consecutive revisions on task 0 and newly wrong on task 1 — with task 1's omitting the very override this round added.

With `policy self-consistency PASS + problem tree holds PASS + factors bear weight PASS + unique solution PASS` on both tasks, **equipment_rental_desk passes the source-layer audit at revision 3** — and this time the unique-solution relationship has been tested against the prose rather than assumed from the formula.

No artifact under `blueprint/`, `tasks/`, `docs/` or `erlbench/` was edited, and no fix was arranged. `replay_tasks.py` was not run in either mode.
