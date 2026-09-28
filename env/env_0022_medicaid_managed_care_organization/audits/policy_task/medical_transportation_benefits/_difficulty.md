# Policy-task audit — medical_transportation_benefits / charter-global

## charter_global_frozen

- Scenario: `env/env_0022_medicaid_managed_care_organization`; difficulty `medical_transportation_benefits` (category `ride`), M=2.
- Freeze time: 2026-09-24T17:19Z (written before any task's GT was revealed; sha256 of this pre-reveal text recorded at 17:22:35Z). Auditor: independent erl-task-policy-audit agent (round 1). This agent did not write the audited artifacts.
- Frozen inputs (sha256 re-computed by the auditor, equal to the brief):
  - `tasks/medical_transportation_benefits/ride.extended.yaml` = `bcd8e8ad1b5fb8aae2ac5a3bc12a007ee6921d294a747fac184710af47f14b14`
  - `tasks/medical_transportation_benefits/task_tools.py` = `fecb1ed2d83a8228fc61bd9a1189ec543cd1852d75331811366752b96b44a718`
  - masked view `0.json` = `886bec06…4f1c1`, masked view `1.json` = `81d4c992…a7b81` (coordinator-built, keep `frozen_time`, `user_scenario`, `initial_state`).
- Fields permitted: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/ride.yaml` (plus the cross-category product yamls `plan/auth/pcp/rx/care/appeal.yaml`, loaded only as engine inputs for cross reads), the extended charter, `task_tools.py`, the two masked views, and `erlbench/` / `skills/erl-task-instantiate/scripts/check_compute.py` (engine semantics of `LATEST/SUM/MAX/XCOUNT/XLATEST/CFIELD/MONTHS/DAYS`).
- Fields explicitly masked until every task's derivation is frozen: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`, the author worklog `tasks/medical_transportation_benefits/worklog.md`, `__pycache__`, and every other scratchpad file.
- Nothing in this section is derived from a revealed GT.

### Entry conditions (Step 0)

- Gate snapshot supplied with the brief: `check_extended` (EXTENDED OK), `check_task_tools` (OK), `replay_tasks` (0.json/1.json det=True, match=True), `check_solvability` (OK), `check_compute` (COMPUTE OK), `check_grounding` (OK), `check_cross_fire` (SCOPE OK); `check_traceability` deferred to the KB stage (stated in the brief).
- Input observation O-IN-1: the `check_compute` snapshot is truncated — it carries only the `1.json` row and the suite lines; the header and the `0.json` row are missing (rc=0 and "COMPUTE OK" are present). Not re-run by the auditor (the skill forbids it); recorded as partial input.
- Input observation O-IN-2: the brief says the masked views keep `task_index`; neither view carries it (keys are `frozen_time`, `user_scenario`, `initial_state`). No effect on the audit.
- Masked views and hashes: present and matching.

### policy_conflict_scan

Complete structured policy = 10 base policies (verbatim, see `override_declarations`) + 6 extended policies:

| id | subject | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- | --- |
| `ride_ext_stay_lodging_meals` | ride_mileage_approved (lodging_meals) | `approve_stay_lodging_meals_3bb3a021` (agent) | amount | [] |
| `ride_ext_trip_mileage` | ride_mileage_approved (mileage) | `approve_trip_mileage_f67ba186` (agent) | amount | stay_lodging_meals, value_input, state |
| `ride_ext_trip_settlement` | ride_mileage_paid | `collect_trip_settlement_816cec94` (user) | amount | trip_mileage, value_input, state |
| `ride_ext_year_end_expiry` | ride_allotment_expire | `expire_year_trips_0d38b23b` (agent) | trips | [] |
| `ride_ext_year_allotment_load` | ride_trip_allotment | `load_year_allotment_a6239ac8` (agent) | trips | year_end_expiry, state_gate, state |
| `ride_ext_alt_ride_allowance` | ride_mileage_approved (late_pickup_alternative) | `file_alternative_ride_claim_fa98ae6a` (user) | amount | year_allotment_load, value_input, state |

- Overlapping subjects: three extended policies write `ride_mileage_approved`; they are separated by `reimbursement_type` (lodging_meals / mileage / late_pickup_alternative), each tool's docstring names the one type it records and says the other types are "never recorded", and the base dedup `one_claim_per_leg` keys on (trip_number, leg, reimbursement_type). No two policies reach different conclusions on the same (event, type). PASS.
- Triggers: stay/mileage/expiry/load are `state_due`; settlement/alt are `on_request`. Compatible.
- Eligibility inherited by every reimbursement policy from base `ride_mileage_reimbursement` (filing window 90 days from trip date; one claim per leg per type) and from `ride_late_pickup_policy` (a `ride_late_pickup` row for the same trip number and leg; the member did not leave before the late threshold). No extended rule weakens them.
- Time anchors: all anchors are the single clock `frozen_time` (`NOW`) and seeded dates; no extended rule introduces a second clock.
- Cross-category read boundaries: every `CFIELD/XCOUNT/XLATEST` in compute names a category declared in that policy's `cross_category` (plan, auth for stay; auth, plan for mileage; plan for settlement; plan, pcp for expiry; plan, rx, care for load; auth, plan for alt). PASS.
- Scope exclusivity / completeness (derived from the charter's prerequisite graph alone, before any reveal): the graph has exactly two connected trees — {settlement ← mileage ← stay} and {alt ← load ← expiry}; together they cover all 6 extended policies and share none. With M=2, one tree per task is the only disjoint complete partition. The task-to-tree assignment is confirmed per task in its own file (from `user_scenario` + world), and against `charter_scope` only after reveal.
- Observation O-SC-1 (blueprint claim vs charter subjects): the difficulty claim in `blueprint.yaml` lists event_types `[ride_trip_booked, ride_trip_cancelled, ride_standing_order_set, ride_transit_pass_issue, ride_mileage_approved, ride_mileage_denied]`; three extended policies write events outside that list (`ride_mileage_paid`, `ride_allotment_expire`, `ride_trip_allotment`). No other difficulty claims the `ride` category, so no collision is demonstrable; recorded as an observation only.

### rule_compute_equivalence

Sweep done both ways for all 6 policies. Mechanical part: every `compute_basis` value is a verbatim substring of its policy's whitespace-normalised `rule` (0 misses), every `baseline.rule` sentence is in the `rule` (all True), and no snake_case token appears in any rule. Sentence-level findings:

- `ride_ext_stay_lodging_meals`: `out_date/ret_date/trip_no` ← "latest registered legs of each kind"; `base_nights = DAYS(out,ret)` ← "nights between"; `stay_nights` three-way ← appointment-time sentence; `nightly_rate` ← stay-length sentence (tests `base_nights`, as the rule says "standard lodging nights"); `one_way = MAX` ← "longest registered one-way miles among the trip's legs"; `edge_day_share`, `meal_days = travel_days − 2(1−share)` ← edge-day sentence; `meals_rate` ← treatment-course sentence (`XCOUNT` plan_claims outpatient_hospital paid, `within_months=3`); `meal_supplement` ← income sentence; `attendant_share` ← attendant sentence; `lodging_part/meals_part/result` ← final sentence ("rounded ... once, on the final amount only"). Every tier of every declared factor is both a rule sentence and a branch of its binding. PASS.
  - Observation O-RC-1 (terminology): the rule uses three nouns for nights — "standard lodging nights", "the nights counted", and, in "The travel days are the lodging nights plus one", an unqualified "lodging nights". Compute binds `travel_days = stay_nights + 1` (nights counted). The other reading (standard nights + 1) is weaker because the entry "records ... the nights counted" as its lodging nights and the first travel day is the day the member travels to the first counted night; the demonstration of what each reading yields on a world is in the task file that claims this policy.
- `ride_ext_trip_mileage`: `mile_rate` ← equipment/purpose sentence; `stay_entry_date/stay_entry_nights/local_trips` ← local-round-trip sentence; `local_rt_miles` ← outbound one-way miles sentence; `route_miles = SUM(one_way_miles)` over the trip's booked legs ← "outbound and return legs added together"; `approved_miles`, `tapered_miles` (three-band piecewise), `result` ← their sentences. PASS.
  - Observation O-RC-2 (latent): the rule's local-trip tier is existential ("when the ledger carries a lodging and meals entry whose trip date is the outbound leg's appointment date"), but compute tests only the latest-posted lodging entry (`LATEST(..., date_field='posted_date', reimbursement_type='lodging_meals')`). On a world where a later-posted lodging entry of another trip exists, rule and compute diverge. Not instantiated in either task world (see task files).
- `ride_ext_trip_settlement`: `mileage_trip_date` ← "the latest approved mileage entry"; `entries = SUM(amount, claim_trip_date = that date)` ← "every approved reimbursement entry the ledger carries for the trip, found by the trip date"; clock-start three-way, credit rate three-way against `P('mileage_payment_days')`, credit scale (lodging nights on the trip's lodging entry, 0 when the latest lodging entry is for another trip), allowance tier and "a settlement that is not late carries no allowance" (`allowance_tier if late_days > P('mileage_payment_days') else 0`), result. PASS.
- `ride_ext_year_end_expiry`: `current_year/prior_year`, `loaded/used` by `benefit_year`, `load_posted`, `months_with_trips = 13 − load month`, `measured_use` three-way, `carry_share`, `carry_cap`, `cap_bonus`, `carried = MN(cap+bonus, int(unused·share))`, `result = unused − carried`. PASS with one finding:
  - Observation O-RC-3 (compute floor with no rule sentence): `unused: MX(0, loaded - used)` floors at zero; the rule says only "the trips its allotment load entries carried less the trips its debit entries used". Consequence appears only where debits exceed loads for the year; not instantiated in either world, so not a red light.
- `ride_ext_year_allotment_load`: WIC, food, pharmacy, class bonuses, covered months, `int((trips+bonuses)·months/12)`. PASS with one latent note:
  - Observation O-RC-4 (latent): "paid pharmacy fills" is implemented as `XCOUNT(rx_fills, event_type='rx_fill')`; an `rx_fill` later reversed keeps its `rx_fill` row, so a reversed fill would still count. Not instantiated in task 1's world (no `rx_fill_reversal` rows; the one rejected fill is excluded by event type).
- `ride_ext_alt_ride_allowance`: late trip/leg/date = latest `ride_late_pickup` by `event_date`; `miles = MAX` over the trip's legs; fare base; mile fare by the late leg's scheduled `pickup_time`; `escorts = MAX(escort_count)` over the trip's legs ("Escorts who rode on the trip's registered legs"); wait factor against `P('late_threshold_minutes')`; leg share (value-added purpose × loaded > used for the leg's year); cap; `RND(MN(cap, fare), 2)`. PASS.
  - Observation O-RC-5 (latent): `escorts = MAX` reads "escorts who rode on the trip's registered legs" as distinct persons, not escort-legs; a summing reading would count one escort on two legs as two. Assessed against the persona in the task file.
- Observation O-RC-6 (latent, all policies reading K0001): `CFIELD('auth','status', variant_name=DME, service_code='K0001')` returns the first matching row, while the rules read "holds an approved or expired ... authorization" existentially. A member with two K0001 rows of different status could diverge. Neither world has more than one K0001 row.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: (3bb3a021, amount), (f67ba186, amount), (816cec94, amount), (0d38b23b, trips), (a6239ac8, trips), (fa98ae6a, amount) — each claimed by exactly one policy. PASS.
- Each tool performs one `ctx.create` of one ledger row with the event type its policy's subject names; none reads, checks or refuses anything (no `if`, no error return, no eligibility/prerequisite test in any body — `task_tools.py` lines 54–68, 111–125, 157–166, 191–200, 225–234, 273–285). PASS for "tool layer judges no prerequisite".
- Docstrings name no other tool and no position in a sequence. The words "then … until it is paid" (approve tools, alt claim) and "after a late pickup" describe business states/events, not call order.
  - Observation O-AB-1: `collect_trip_settlement_816cec94` Arg `reimbursement_claim_number` says it is "copied ... from the approval receipt the agent reads out", which presumes an approval issued in the same call; it names no tool and no ordering connective, so it is not an ordering statement, but it is a light hint that an approval precedes the payout.
- uuid8s: `3bb3a021`, `f67ba186`, `816cec94`, `0d38b23b`, `a6239ac8`, `fa98ae6a` — no shared prefix/suffix, no sequence, no adjacency; consistent with independent generation. PASS.
- Observation O-AB-2 (terminal state): none of the six tools updates the holding integrals (`ride_benefits.trips_remaining`, `ride_benefits.reimbursement_owed`) although the charter's `accounts` define them as the integrals of these ledgers ("Nothing else on the benefit changes"). In addition, the settlement pays approved amounts plus credit and allowance as a `ride_mileage_paid` (account `mileage_reimbursement`, direction out), so the account's integral goes below zero by the credit + allowance. No scored value depends on the integrals; recorded as an observation.

### prerequisite_graph

- `prerequisite` filled on all 6 policies (`[]` on stay and expiry). Every `problem` is another extended policy id of this file, never base, never self. Graph: mileage→stay, settlement→mileage, load→expiry, alt→load. Acyclic (two chains of length 3). PASS.
- Every `policy_source` is verbatim in its own policy's `rule` (whitespace-normalised substring: True ×4). `form: state` on all four edges; no `fallback_reason` (none needed). PASS.
- `resolved_by` is the depended-on policy's `target_tool` on all four edges. PASS.
- `kind` vs `gate`: three `value_input` edges name bindings that exist in the blocked policy's compute (`local_trips`, `entries`, `leg_share`); the one `state_gate` edge (load→expiry) names `gate: ride_ledger.benefit_year`, a column rather than an eligibility gate — the extended load policy has no `eligibility` entry; the gate is the prerequisite sentence itself.
  - Observation O-PG-1: `state_gate` edge points at a field, not an eligibility gate id. No consequence demonstrable.
- `condition` strength:
  - mileage→stay: sentence "…the mileage entry is fixed only after the ledger carries the approved lodging and meals entry for that trip"; condition "…an approved lodging and meals entry whose trip date is the trip's outbound appointment date". Equivalent (the stay rule records the outbound appointment date as the entry's trip date). PASS.
  - settlement→mileage: sentence "…not released until the ledger carries the approved mileage entry for that trip"; condition adds "and it is the latest approved mileage entry". Observation O-PG-2: the extra clause restates the settlement rule's own definition of "the trip's mileage entry", so it is a restatement, not a strengthening with a different outcome.
  - load→expiry and alt→load: equivalent. PASS.
- `effect` statements: checked against compute — local_trips moves 0 → course-day count; entries moves to the trip's amounts; leg_share moves uncovered → covered; the load's trips do not read the expiry (true: `result` has no ledger read of expiry rows). PASS.
- No authoring-viewpoint phrasing ("in this task", "at the opening") in any `prerequisite` text. PASS.

### prerequisite_sentences

Four-point test per edge:

| edge | ordering connective | waited-on state (record-visible, no action/performer/tool) | no tool / id / snake token | strength = condition |
| --- | --- | --- | --- | --- |
| mileage→stay | "only after" | "the ledger carries the approved lodging and meals entry for that trip" | yes | yes |
| settlement→mileage | "not … until" | "the ledger carries the approved mileage entry for that trip" | yes | yes (O-PG-2) |
| load→expiry | "not … until" | "the ledger carries the expiry entry for the previous benefit year's unused trips" | yes | yes |
| alt→load | "only after" | "the ledger carries the allotment load for the benefit year of that leg's trip date" | yes | yes |

- One write per waited-on state: lodging_meals approved row ← only `approve_stay_lodging_meals_3bb3a021` (the two other `ride_mileage_approved` writers say lodging_meals is a type they "never record"); mileage approved row ← only `approve_trip_mileage_f67ba186`; `ride_allotment_expire` row ← only `expire_year_trips_0d38b23b`; `ride_trip_allotment` row ← only `load_year_allotment_a6239ac8`. PASS.
- Derivations (sentence + records + depended-on rule → resolving action, single reading):
  - mileage→stay: the stay rule opens "A lodging and meals entry is booked for a registered long-distance trip whose one-way miles are at least the level's lodging threshold and whose stay includes at least one lodging night" and says what it records → it is the policy that brings about the waited-on entry. Single reading.
  - settlement→mileage: the mileage rule says "A trip's mileage entry is worked out from its registered outbound leg … and it records the trip's reservation number …" → single reading.
  - load→expiry: the expiry rule "The year-end expiry entry is booked once for the benefit year before the current one … and records that year and the trips that expire" → single reading.
  - alt→load: the load rule "The allotment load entry of a benefit year is booked once, for the current benefit year" → single reading (the leg's year equals the current year only when the late leg falls in the current year; a late value-added leg of an earlier year would wait on a load the load rule never books — latent, O-PS-2).
- No second wording of any dependency in the blocked rules; no depended-on rule restates the sentence; no rule states a cross-problem order that grounds no edge (the ordering words elsewhere — "the night before the first appointment", "booked once for the benefit year before the current one", "After a late pickup" — are within-problem). No base rule sentence grounds any edge. PASS.
- Observation O-PS-1 (latent dead end, mileage→stay): the sentence covers every trip "whose return leg falls on a later date than its outbound leg", but the stay rule books a lodging entry only when one-way miles ≥ the level's lodging threshold (120 on RideLink Mileage Reimbursement). A multi-day trip under 120 miles one way can never satisfy the waited-on state, so its mileage entry could never be fixed. Not instantiated in either world.
- Observation O-PS-2 (latent dead end, load→expiry and alt→load): the expiry tool accepts only a positive trip count ("trips: … positive"), so a previous year whose unused trips are all carried (expiry of 0) or that had no load cannot produce the waited-on expiry entry, and the load would never be released; likewise a late value-added leg dated in an earlier year waits on a load the load rule books only for the current year. Neither is instantiated in task 1's world (expiry there is positive; the late leg is in the current year — shown in `1.md`).

### override_declarations

Base copy: `yaml.safe_load` of every base key of `ride.extended.yaml` equals `blueprint/products/ride.yaml` (category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies — all True); the textual diff is only the header comment line. PASS.

Sentence-by-sentence against each `base_policy_refs` entry:

- `ride_ext_stay_lodging_meals` (refs late_pickup, mileage_reimbursement, long_distance):
  - long_distance "For an approved long-distance trip … lodging up to lodging_per_night_usd per night and meals up to meals_per_day_usd per travel day are reimbursed as a lodging_meals reimbursement." — handled differently (allowances, weekly/monthly rates, supplements, attendant share); **declared** in `overwrite`. Other long_distance sentences (long-distance booking conditions, out-of-state approval) followed.
  - mileage_reimbursement: attendance, filing window, one-per-leg-per-type, late → filed_late — followed (inherited). Payment sentence — handled by settlement's declared overwrite.
  - late_pickup: not governing lodging — no conflict.
  - Observation O-OV-1 (base `formula`): base `ride_mileage_reimbursement.formula` (`amount: mileage_amount + lodging_nights * lodging_per_night_usd + meal_days * meals_per_day_usd`) is a structured field, not a rule sentence, and no `overwrite` names it. Its content is exactly the two prose clauses both declared superseded (long_distance lodging clause; mileage_reimbursement per-mile clause), so the merged semantics stay unique; recorded because a reader who takes the formula at face value computes a different figure (the figure on task 0's world is given in `0.md`).
- `ride_ext_trip_mileage` (same refs): mileage_reimbursement first sentence (rate, basis, round trip) — handled differently; **declared**. "measured by mileage_distance_basis" is kept in substance ("each measured by the shortest driving route", the value of that parameter on RideLink Mileage Reimbursement). Remaining sentences followed.
- `ride_ext_trip_settlement` (ref mileage_reimbursement): "an approved amount is paid within mileage_payment_days by the member's chosen payment method" — handled differently (credit + allowance; `mileage_payment_days` becomes the lateness threshold); **declared**.
- `ride_ext_year_end_expiry` (ref value_added): "unused trips expire on December 31 or when the benefit closes" — **declared**. Other sentences (load, debit, booking only while trips remain, no displacement) followed.
- `ride_ext_year_allotment_load` (ref value_added): the January-1 load clause — **declared**. Activation-year proration sentence ("or on activation for a benefit activated during the year, prorated …") is not superseded and remains in force for activation loads; the extended rule books the January load only.
  - Observation O-OV-2: the superseded clause also carries "to value_added_purposes destinations within value_added_trip_max_miles", a use restriction; its `replaced_by` drops it, so after the merge the purpose and 15-mile limits survive only in parameters, the completion trigger and measures, not in a rule sentence. No scored value in this difficulty depends on it.
- `ride_ext_alt_ride_allowance` (refs late_pickup, mileage_reimbursement, long_distance): late_pickup "the member may then take an alternative ride and be reimbursed its receipted cost up to late_pickup_alt_reimbursement_max_usd" — **declared**. "reimbursed only where a ride_late_pickup row exists for the same trip number and leg; a member who left before the late threshold was reached is not reimbursed" — followed. mileage_reimbursement filing window and one-per-leg-per-type — followed.
  - Observation O-OV-3 (scope of the base attendance sentence): base `ride_mileage_reimbursement` says "Attendance is proven by a paid claim on plan_claims for the member with the trip's appointment date and destination provider; without one the claim is denied with denial_reason no_attended_appointment." It sits between the mileage sentence and the general reimbursement sentences. If it were read to govern every reimbursement type, every late value-added leg (no destination provider, no plan claim) would be denied — which would leave the extended rule's own value-added tiers (covered / uncovered share) with no possible application, and would already make base `ride_late_pickup_policy` self-contradictory for value-added legs. The consistent reading confines it to mileage (and to trips to a provider). Its bearing on task 1 is assessed in `1.md`.
  - Observation O-OV-4: the fall-through cap is the level's `late_pickup_alt_reimbursement_max_usd`, which is 0.00 on four levels ("0.00 where not offered"), while the two higher cap tiers pay up to 60/75 on any level. On a not-offered level, a late return leg or a Pregnancy Care member would be paid; other claims capped at 0.00 (a non-positive amount the user tool rejects by contract). The superseded clause is declared, so this is the declared new semantics; not instantiated (task 1 is on RideLink Door-to-Door Assist, max 50.00).
- Disguised forms: no anonymous intermediate overriding a base quantity outside the declared clauses; no 0/1 multiplier zeroing a base-fixed amount; no dropped base branch that a task world needs. No rule/compute_basis text calls base output a "wrong value".
- Undeclared override: none found. PASS.

### factor_ladders

Per policy (label / decides / tiers / honest? / multi-source? / cross_difficulty):

`ride_ext_stay_lodging_meals` — 6 declared:
1. `stay_nights_counted` — **method** — decides `stay_nights` — tiers "+2 / +1 / +0 nights" (`base_nights + 2 | base_nights + 1 | base_nights`). **Label dishonest**: every tier is the same expression `base_nights + k` with a different constant k ∈ {2,1,0}; it substitutes a number, it does not change how nights are computed. Counts as `parameter`.
2. `stay_length_nightly_rate` — parameter — 58 / 72 / level (85 on Mileage Reimbursement). Honest. Single-source.
3. `drive_length_edge_day_share` — parameter — 0.5 / 0.75 / 1. Honest.
4. `treatment_course_meals_rate` — parameter — 31 / 28 / level 25; tiers = conjunction / exactly-one of (outbound purpose radiation|chemo, ≥8 paid outpatient claims in 3 months) → **multi-source** (ride_trips + plan_claims); cross_difficulty plan.
5. `income_meal_supplement` — parameter — 6.5 / 3.25 / 0; single-source (plan membership income); cross_difficulty plan.
6. `attendant_meals_share` — parameter — 1.0 / 0.5 / 0; conjunction / exactly-one of (K0001 auth approved|expired, plan category ABD|Dual) → **multi-source** (auth + plan); cross_difficulty auth.
- Counts after the honesty test: parameter 6, **method 0** (bound ≥1 **fails**), multi-source 2, cross-difficulty 3 (plan, plan, auth). Every tier stated in the rule and implemented in compute; ladders pairwise disjoint; no two tiers share a value; fall-through = baseline on every factor.

`ride_ext_trip_mileage` — 4 declared:
1. `chair_treatment_mile_rate` — parameter — 0.32 / 0.26 / level 0.21; multi-source (auth + ride_trips); cross_difficulty auth.
2. `stay_local_round_trips` — method — local trips = paid outpatient claims count / lodging nights on the entry / none; tiers derive the quantity from different records → honest method; multi-source (ride_ledger + plan_claims); cross_difficulty plan.
3. `destination_local_miles` — parameter — 14.0 / 8.0 / 0. Honest.
4. `approved_miles_taper` — method — three piecewise formulas → honest method.
- Counts: parameter 2, method 2, multi-source 2, cross-difficulty 2. PASS structurally.

`ride_ext_trip_settlement` — 4 declared:
1. `late_settlement_credit_rate` — parameter — 0.02 / 0.01 / 0. Honest.
2. `settlement_clock_start` — method — clock starts on a plan claim's booked date / the registration date / the return date: each tier derives the anchor from a different record → honest method; multi-source (plan_claims vs ride_trips); cross_difficulty plan.
3. `stay_length_credit_scale` — parameter — 2.0 / 1.5 / 1. Honest.
4. `late_settlement_allowance` — parameter — 15 / 10 / 0; conjunction / exactly-one of (category ABD|Dual, income ≤100% FPL) — both conditions are fields of the same `plan_memberships` row, so not multi-source under "over distinct records"; cross_difficulty plan.
- Counts: parameter 3, method 1, multi-source 1, cross-difficulty 2. PASS structurally.

`ride_ext_year_end_expiry` — 4 declared:
1. `partial_year_use_measure` — method — annualise / add one per month without trips / as debited → honest method (three formulas).
2. `use_carry_share` — parameter — 1 / 0.5 / 0. Honest. (Its `bindings` list `used`, but its tiers read `measured_use`; structure-only note.)
3. `category_carry_cap` — parameter — 6 / 3 / 0; cross_difficulty plan.
4. `primary_care_carry_bonus` — parameter — 2 / 1 / 0; cross_difficulty pcp.
- Counts: parameter 3, method 1, multi-source 0, cross-difficulty 2. PASS structurally (the multi-source requirement is per task).

`ride_ext_year_allotment_load` — 5 declared:
1. `maternity_wic_bonus` — parameter — 8 / 4 / 0; conjunction / exactly-one of (Pregnancy Care category, ≥1 paid preventive claim in 3 months) → multi-source (plan_memberships + plan_claims); cross_difficulty plan.
2. `income_food_bonus` — parameter — 6 / 3 / 0; plan.
3. `pharmacy_fill_bonus` — parameter — 4 / 2 / 0; rx.
4. `care_management_class_bonus` — parameter — 4 / 2 / 0; care.
5. `coverage_months_counted` — method — months through the renewal month / through the termination month / twelve: tiers derive the quantity from different records → honest method; plan.
- Counts: parameter 4, method 1, multi-source 1, cross-difficulty 5. PASS structurally.

`ride_ext_alt_ride_allowance` — 6 declared:
1. `assistance_fare_base` — parameter — 12.0 / 6.5 / 3.5; auth + level parameter; cross_difficulty auth.
2. `pickup_hour_mile_fare` — parameter — 3.2 / 2.75 / 2.4.
3. `escort_fare_add` — parameter — 5.5 / 2.75 / 0.
4. `stranded_wait_factor` — **method** — decides `wait_factor` — tiers "multiply by 1.5 / by 1.25 / leave as is (×1)". **Label dishonest**: the binding is a constant multiplier `1.5 | 1.25 | 1` inserted into the same expression `fare = (…) * wait_factor * leg_share`; it substitutes a number. Counts as `parameter`.
5. `leg_kind_share` — parameter — 0.9 / 0.5 / 1.
6. `return_leg_cap` — parameter — 75 / 60 / level max; conjunction / exactly-one of (late leg is return, Pregnancy Care category) → multi-source (ride_trips + plan_memberships); cross_difficulty plan.
- Counts after the honesty test: parameter 6, **method 0** (bound ≥1 **fails**), multi-source 1, cross-difficulty 2.

Ladder realism (every condition and outcome is one the NEMT line of business weighs): tiers read as plausible NEMT/travel-reimbursement practice for night-before/night-after lodging, extended-stay rates, first/last-day meal share (the federal 75% convention), treatment-course meals, attendant meals, wheelchair/treatment mileage rates, local shuttle miles, mileage tapers, prompt-payment credit by lateness, carry-over by use, maternity/food/pharmacy/class value-added bonuses, coverage months, taxi-style fare base/night fare/escort/strand/cap. Observations (argued, not raised to red light because the artifacts give no evidence beyond the auditor's judgment):
- O-FL-1: `stay_length_credit_scale` scales a late-payment credit rate by the lodging nights on the trip; a prompt-payment credit is normally proportional to the amount and the delay only, and the amount already reflects the stay length.
- O-FL-2: `late_settlement_allowance` keys a flat lateness allowance on eligibility category; `attendant_meals_share`'s half tier pays an attendant share to an ABD/Dual member with no documented wheelchair need.
- O-FL-3: `destination_local_miles` uses the outbound one-way distance as the proxy for how far the lodging is from the facility.

### findings

- **F-C1 — SOURCE-FACTOR RED (charter half) — `ride_ext_stay_lodging_meals` has no honest `method` factor.** Symptom: the only factor labelled `method`, `stay_nights_counted`, selects a constant. Root cause: its binding `stay_nights: base_nights + 2 if (…) else (base_nights + 1 if (…) else base_nights)` is one expression with a tier-selected addend, the "different number into the same formula" shape. Evidence: `ride.extended.yaml` compute item `stay_nights` and `factors[0]` (`effect: method`, ladder "plus two / plus one / only the nights between"). Consequence: after relabelling, the policy has 0 method factors against the bound of ≥1. Bears on the task that claims this policy (task 0) — the demonstration is in `0.md`.
- **F-C2 — SOURCE-FACTOR RED (charter half) — `ride_ext_alt_ride_allowance` has no honest `method` factor.** Symptom: the only factor labelled `method`, `stranded_wait_factor`, selects a multiplier 1.5 / 1.25 / 1. Root cause: `wait_factor: K('long_strand_factor') if … else (K('strand_factor') if … else 1)` feeds `fare = (fare_base + mile_fare * miles + escort_fare) * wait_factor * leg_share` unchanged in every tier. Evidence: compute items `wait_factor`, `fare`; `factors[3]`. Consequence: 0 method factors against ≥1. Bears on the task that claims this policy (task 1) — demonstrated in `1.md`.
- Observations O-IN-1, O-IN-2, O-SC-1, O-RC-1…6, O-AB-1, O-AB-2, O-PG-1, O-PG-2, O-PS-1, O-PS-2, O-OV-1…4, O-FL-1…3 as above; none demonstrated to change a scored value on the charter alone. O-RC-1, O-OV-1 and O-OV-3 are checked against a world in the task files.
- Policy self-consistency (charter half): no undeclared override, no rule/compute divergence on either task world's inputs (the per-task files confirm), no undeclared cross-problem order, every prerequisite quotable and state-form. **PASS** at charter level.

## closing_checklist

Written after both tasks' `source_gt_comparison` (reveal 2026-09-24T17:22:35Z). Nothing above this heading was changed after the reveal except the freeze-time metadata line (see the note below).

- Per-task files `0.md`, `1.md` correspond one-to-one with `tasks/0.json`, `tasks/1.json`; `_difficulty.md` alongside; first revision (no older revisions). Blind = GT on every argument, owner, order and terminal row of both tasks.
- Coverage and exclusivity: task 0 claims {stay, mileage, settlement}, task 1 claims {expiry, load, alt} — all 6 extended policies covered once, trees disjoint; task tools closed (each used by exactly one task); uuid8s independent (see `action_binding_and_uuids`).
- Problem trees: each has 2 prerequisite problems, ≥1 value_input edge (task 0: 2; task 1: 1), an owner=user root, no cycle; the difficulty graph is acyclic.
- Factors: every factor of every computation bears weight against an honest baseline, and every all-baseline number differs from gold. **Not met:** the ≥1 `method` bound fails for `ride_ext_stay_lodging_meals` (task 0) and `ride_ext_alt_ride_allowance` (task 1) because their only `method` factors (`stay_nights_counted`, `stranded_wait_factor`) select constants (F-C1, F-C2).
- Gates re-run on the final form: not applicable — the difficulty does not close.

**Difficulty status: NOT PASSED at the source layer** — task 0 SOURCE-FACTOR RED (F-C1 / T0-F1), task 1 SOURCE-FACTOR RED (F-C2 / T1-F1). Policy self-consistency, problem tree and unique solution PASS on both tasks.

> Post-reveal edit note: after the reveal, only the "Freeze time" / "Reveal time" metadata lines were corrected. They had carried estimated clock times later than the real reveal (17:22:35Z, taken from `date -u`). No derivation, figure or verdict in any frozen section changed. The sha256 values quoted in the files are of the pre-reveal text, before this metadata correction.

## revision_2

- Re-audit time: 2026-09-24T17:32Z. Auditor: the same independent audit agent as round 1. From this round on the derivation is not blind: GT was revealed in round 1, and the round-2 GT was read after the charter-global checks below were re-derived.
- Inputs: brief `scratchpad/brief_ride_r2.md`. The gate snapshot has all 7 gates green; this time the `check_compute` table is complete, so O-IN-1 is closed.
  - `ride.extended.yaml`: `e4cbd2461aefd15bbfe4feaa76f4459b9092b3bd00266fff7c9200d8828a337b` (changed from `bcd8e8ad…`).
  - `task_tools.py`: `07483c6138ebcf759112a6fed303afe79fc2c55e838968ca845abaca56b7ae84` (changed from `fecb1ed2…`).
  - Masked views: round2 `0.json` = `886bec06…4f1c1` (unchanged); round2 `1.json` = `e5e0736f…0ffdc` (only the persona weekday changed; `initial_state` and `frozen_time` are identical to round 1).
- Because both shared inputs changed, every charter-global check was re-derived in full. The round-1 text above is kept unchanged.
- Base section: `yaml` equality with `blueprint/products/ride.yaml` is still True for every base key.

### Item-by-item closure

| item | round-1 claim | round-2 evidence | status |
| --- | --- | --- | --- |
| F-C1 (stay has no honest method) | `stay_nights_counted` selects a constant | `stay_nights_counted` is now labelled `parameter`. A new `stay_length_lodging_taper` (method) decides `lodging_part` with three different formulas: three-band `7×std + 21×weekly + (n−28)×monthly`, two-band `7×std + (n−7)×weekly`, and flat `n×std`. All three tiers are reachable, the baseline is `stay_nights × P('lodging_per_night_usd')`, which is what `baseline.rule` says ("Each lodging night is paid at the level's standard nightly lodging allowance"), and the fall-through is flat, which equals the baseline. Count: 5 parameter + 1 method. | **closed** |
| F-C2 (alt has no honest method) | `stranded_wait_factor` was a constant multiplier | Replaced by `stranded_waiting_charge` (method): per-minute `(m − threshold) × 0.45` / flat 8.00 / none. The label is now honest (the tiers differ in algorithm), but its ladder has only two live tiers. See **F-C3**. | label closed; **replaced by F-C3** |
| O-RC-1 (three nouns for nights) | — | The rule now uses a single term, "lodging nights": "The lodging nights also take in the nights the appointment times need …"; travel days = lodging nights + 1. | closed |
| O-RC-2 (existential rule vs latest-posted compute) | — | The mileage rule now counts local trips "from the latest lodging and meals entry on the ledger … when the latest lodging and meals entry carries another trip date, or there is none, no local round trips". The settlement credit-scale sentence is aligned the same way. | closed |
| O-RC-3 (MX(0,…) floor with no rule sentence) | — | The rule now says "…less the trips its debit entries used, and never fewer than none" (and so does `baseline.rule`). | closed |
| O-RC-4 (reversed fills counted as paid) | — | The rule now says "pharmacy fill entries …, where a fill later reversed still counts because the pharmacy visit was made and a rejected fill is not a fill". This matches `event_type='rx_fill'`. | closed |
| O-RC-5 (escort persons vs escort-legs) | — | The rule now says "the escorts being counted as persons, the most recorded on any one of the trip's registered legs", which matches `MAX(escort_count)`. | closed |
| O-AB-1 (settlement docstring hints at an approval) | — | The claim-number Arg now reads "copied … as it appears on the member's reimbursement history or as the agent reads it out". Every tool body is otherwise unchanged: six unconditional `ctx.create` calls, no `Error` return, the same `make_id` prefixes and the same uuid8s. | closed |
| O-PS-1 (mileage dead end under the lodging threshold) | — | The sentence is now scoped: "For a trip whose return leg falls on a later date than its outbound leg **and whose one-way miles reach the level's lodging threshold** …". The condition was updated to match. | closed |
| O-PS-2 (load/alt dead ends) | — | The load sentence now ends "…, whenever that year leaves trips to expire"; the alt sentence now reads "For a late value-added leg **in the current benefit year** …". Conditions were updated. | closed |
| O-OV-2 (dropped purpose / distance limit) | — | `replaced_by` and the rule now carry "of one-way trips to the level's value-added destinations, within the level's value-added trip distance". | closed |
| O-OV-3 (attendance sentence scope) | — | This is now a declared `overwrite` on `ride_ext_alt_ride_allowance` against `ride_mileage_reimbursement`'s attendance sentence, with `replaced_by` "An alternative-ride claim rests on the late pickup record of its leg and needs no paid claim to prove attendance." That sentence is verbatim in the rule. | closed |
| O-OV-4 (a level that does not offer the reimbursement) | — | New sentence: "A level whose alternative-ride maximum is zero offers no alternative-ride reimbursement, and every claim on it is capped at zero". It is implemented by `offered_cap = cap if P(max) > 0 else 0`. | closed |
| persona weekday slip (task 1) | — | Now "Tuesday January 5"; 2027-01-05 is a Tuesday. | closed |
| O-IN-1 (truncated gate) | left open | The snapshot is now complete. | closed |
| O-IN-2, O-SC-1, O-RC-6, O-AB-2, O-PG-1, O-PG-2, O-OV-1, O-FL-1…3 | left open | Re-checked; unchanged. They remain observations. | open (observations) |

### Re-derived charter-global checks (on `e4cbd246…` / `07483c61…`)

- **policy_conflict_scan**: the same 6 policies, subjects, target tools, owners and two disjoint trees as in round 1; no new overlap. PASS.
- **rule_compute_equivalence**: mechanical re-sweep. Every `compute_basis` value is verbatim in its rule (0 misses), every compute binding has a basis, every `baseline.rule` sentence is in its rule, and no rule contains a snake_case token. Sentence-level re-read of the changed passages:
  - stay: taper and nights.
  - mileage: scope of the prerequisite sentence and the latest-entry wording.
  - settlement: credit-scale wording.
  - expiry: floor.
  - load: fills, destinations and the conditional prerequisite.
  - alt: attendance, escorts, waiting charge, offered cap.
  All of them are equivalent to compute. PASS.
- **action_binding_and_uuids**: unchanged pairs, unchanged uuid8s, bodies unconditional; the only docstring change is the O-AB-1 closure. PASS.
- **prerequisite_graph**: the same four edges, acyclic; every `policy_source` is verbatim in its own rule; all four are state form. The load→expiry condition now carries the same "when the previous benefit year leaves trips to expire" scope as its sentence. New observation **O-PG-3**: the mileage→stay condition reads "the ledger's latest approved lodging and meals entry carries the trip's outbound appointment date", while the sentence says "carries the approved lodging and meals entry for that trip". This is the same kind of note as O-PG-2: the extra word "latest" restates the rule's own local-trip wording, and no different outcome can be demonstrated. PASS.
- **prerequisite_sentences**: the four-point test passes on all four edges. The added scope clauses ("whose one-way miles reach the level's lodging threshold", "whenever that year leaves trips to expire", "in the current benefit year") are record-visible and name no tool. Each waited-on state still has exactly one writer. PASS.
- **override_declarations**: one new declared overwrite, the attendance sentence (alt). No undeclared override was found in the changed text. The new zero-maximum sentence restates base "0.00 where not offered" rather than departing from it. PASS.

### factor_ladders (re-derived)

Tier reachability was checked this round against every tier of every ladder, using the charter's own conditions for who can reach each write. Round 1 did not test reachability systematically; that is how F-C4 below was missed.

| policy | factors (label) | parameter / method after tests | notes |
| --- | --- | --- | --- |
| stay | stay_nights_counted (P), stay_length_lodging_taper (M), drive_length_edge_day_share (P), treatment_course_meals_rate (P), income_meal_supplement (P), attendant_meals_share (P) | 5 / 1 | O-FL-4 |
| mileage | chair_treatment_mile_rate (P), stay_local_round_trips (M), destination_local_miles (P), approved_miles_taper (M) | 2 / 2 | O-FL-5 |
| settlement | late_settlement_credit_rate (P), settlement_clock_start (M), stay_length_credit_scale (P), late_settlement_allowance (P) | **3 factors / 0 method** after F-C4 strikes `settlement_clock_start` | **F-C4** |
| expiry | partial_year_use_measure (M), use_carry_share (P), category_carry_cap (P), primary_care_carry_bonus (P) | 3 / 1 | — |
| load | maternity_wic_bonus, income_food_bonus, pharmacy_fill_bonus, care_management_class_bonus (P), coverage_months_counted (M) | 4 / 1 | — |
| alt | assistance_fare_base, pickup_hour_mile_fare, escort_fare_add (P), stranded_waiting_charge (M), leg_kind_share, return_leg_cap (P) | **5 factors / 0 method** after F-C3 strikes `stranded_waiting_charge` | **F-C3** |

### findings (revision_2)

- **F-C3 — SOURCE-FACTOR RED (charter half; introduced by the round-2 rework) — the alt policy's only `method` factor, `stranded_waiting_charge`, has a fall-through tier no claimant can reach.**
  - Symptom: the ladder reads "at least twice the late threshold → per-minute charge; at least the late threshold and under twice it → flat 8.00; otherwise (under the late threshold) → no waiting charge".
  - Root cause: every claim that reaches this write rests on a late pickup. Base `ride_late_pickup_policy` says: "A pickup more than late_threshold_minutes after the end of the pickup window is a late pickup … The alternative ride is reimbursed only where a ride_late_pickup row exists for the same trip number and leg". The alt rule says it is worked out "for the member's latest recorded late pickup" and "rests on the late pickup record of its leg". So minutes late is always more than the threshold.
  - Consequence:
    - The "under the late threshold" tier selects nobody.
    - The part "at least the late threshold" of tier 2 holds for every claimant, so it restates the policy's scope instead of dividing its customers.
    - The ladder has two live tiers, against the bound of three.
  - Under the rule "a rule the tests strike out is not a factor", the alt computation is left with 5 factors, **0 `method`**.
  - Evidence: `ride.extended.yaml` → `ride_ext_alt_ride_allowance.compute.waiting_charge` and `factors[3].ladder[2]`; base `ride_late_pickup_policy.rule`.
  - Bears on task 1, demonstrated in `1.md` revision_2.
  - Relation to round 1: the round-1 multiplier ladder (≥3×, ≥2×, otherwise) did have a live fall-through (between the threshold and twice it). The rework moved the lower boundary down to the threshold itself.
- **F-C4 — SOURCE-FACTOR RED (charter half; pre-existing in round 1 and missed by this auditor then) — the settlement policy's only `method` factor, `settlement_clock_start`, has a middle tier no settled trip can reach.**
  - Symptom: tier 2 reads "no such claim was booked after the return leg's appointment date **and the trip was registered after its outbound appointment date** → start the clock on the registration date".
  - Root cause: the settlement "is not released until the ledger carries the approved mileage entry for that trip". The mileage rule says "Mileage is reimbursed only on RideLink Mileage Reimbursement, for a trip registered with a trip number before the appointment" (and base `ride_mileage_reimbursement` has the same condition, with denial reason `trip_not_registered`). So every trip that reaches the settlement write was registered before its outbound appointment, and the condition in tier 2 is false for all of them.
  - Consequence: two live tiers against the bound of three. With `settlement_clock_start` struck, the settlement computation has 3 factors (bound 4 to 6) and **0 `method`** (bound ≥1).
  - Evidence: `ride_ext_trip_settlement.rule` (clock sentence and prerequisite sentence); `ride_ext_trip_mileage.rule` (second sentence); compute `clock_start: course_booked if … else (registered_on if registered_on > out_date else ret_date)`.
  - Bears on task 0, demonstrated in `0.md` revision_2.
  - Relation to round 1: the text is unchanged since round 1, where `_difficulty.md` → `factor_ladders` passed it. That PASS is superseded by this finding.
- New observations (no red light):
  - **O-FL-4**: on every level with a 120-mile lodging threshold, a stay entry needs one-way miles ≥ 120, so the edge-day ladder's "under the mid-drive miles (100)" tier can only be reached on RideLink Transit Pass. That level's lodging threshold is 0 and its standard lodging and meals allowances are 0.00. The tier is not strictly empty, so this is not raised to a red light. Round 1 missed it.
  - **O-FL-5**: `destination_local_miles`'s fall-through ("under the regional trip miles (50)", adds none) is only selected when there are no local round trips. Local trips need a lodging entry, which needs ≥ 120 miles, so the tier never changes a result. It is formally reachable, so this is an observation. Round 1 missed it.
  - **O-PG-3**: described under `prerequisite_graph` above.
- Everything else in the round-1 `findings` is closed or remains an observation, as listed in the closure table.

### closing_checklist (revision_2)

- Coverage, disjoint scopes, closed task tools, independent uuid8s, and acyclic trees (2 prerequisite problems each, value_input edges 2 and 1, owner=user roots): all still met.
- Every factor bears weight on its task's world against an honest baseline, and every all-baseline number differs from gold (figures in the task files).
- **Not met:**
  - The ladder-reality bound fails for `settlement_clock_start` (F-C4, task 0) and `stranded_waiting_charge` (F-C3, task 1).
  - As a result, the settlement computation (task 0) and the alternative-ride computation (task 1) carry no surviving `method` factor, and the settlement falls to 3 factors.
- **Difficulty status after revision_2: NOT PASSED at the source layer.**
  - task 0: SOURCE-FACTOR RED (F-C4).
  - task 1: SOURCE-FACTOR RED (F-C3).
  - Policy self-consistency, problem tree and unique solution PASS on both tasks.
  - No regression in any of those three relationships.

## revision_3

- Re-audit time: 2026-09-24 (round 3). Auditor: the same independent audit agent. Not blind.
- My revision_2 is complete on disk: its closing checklist and both task verdict lines were written before the run was cut off.
- Inputs:
  - brief `scratchpad/brief_ride_r3.md`, with all 7 gates green (full snapshot);
  - `ride.extended.yaml` `a65a3a86b9cec749069f9604539e5506b369153ab641035403bc1871f99fbbfa` (changed from `e4cbd246…`);
  - `task_tools.py` `07483c61…ae84` (unchanged);
  - masked views round3 `0.json` `886bec06…` and `1.json` `e5e0736f…` (both unchanged).
- Carry-forward rule: `task_tools.py` is unchanged, so `action_binding_and_uuids` from revision_2 is carried forward by reference, on the ground of that hash. The charter changed, so every other charter-global check was re-derived.
- The base section is still equal to `blueprint/products/ride.yaml`.

### What changed in the charter (found by reading, not taken from the reworker)

1. `ride_ext_trip_settlement`:
   - clock tier 2 now reads "…but the return leg was registered after the outbound leg's appointment date, because the stay was extended while the member was away, the clock starts on the return leg's registration date";
   - compute `return_registered_on: LATEST(ride_trips.event_date, leg='return')`;
   - `clock_start: course_booked if … else (return_registered_on if return_registered_on > out_date else ret_date)`;
   - ladder and bindings updated.
2. `ride_ext_alt_ride_allowance`:
   - The waiting-charge ladder is now: ≥ 3× threshold → `minutes_late × 0.45` ("every minute past the pickup window"); ≥ 2× and < 3× → `(minutes_late − threshold) × 0.45`; otherwise (late, but under 2×) → flat 8.00.
   - The rule states "every late pickup being more than the level's late threshold past the pickup window".
   - The baseline is now `waiting_charge: K('flat_strand_charge')`, and `baseline.rule` adds "plus the flat stranding charge for the wait".
3. `ride_ext_stay_lodging_meals`: `mid_drive_miles` 100 → 150.
4. `ride_ext_trip_mileage`: `metro_trip_miles` 150 → 200, `regional_trip_miles` 50 → 150.

### Item-by-item closure

| item | round-3 evidence | status |
| --- | --- | --- |
| **F-C4** (settlement clock tier 2 unreachable) | Tier 2 now keys on the **return** leg's registration date. A trip whose outbound leg was registered before its appointment (which is what the mileage entry requires) can still have its return leg registered after the outbound appointment date, so the tier is reachable by a settled trip. All three tiers are live: (1) a claim booked after the return date; (2) no such claim, and the return leg registered after the outbound date; (3) otherwise. The tiers derive the anchor from different records, so the method label stays honest. The baseline `ret_date` is the fall-through. | **closed** (latent reading: O-PS-3) |
| **F-C3** (waiting-charge fall-through unreachable) | Every tier is now reachable by a late pickup (threshold < m < 2×, 2× ≤ m < 3×, m ≥ 3×). The rule itself says every late pickup is past the threshold, so no tier condition restates scope. Flat vs metered are different algorithms. Tiers 1 and 2 meter different spans (from the window vs from the threshold); see O-FL-6. The baseline is the flat charge, which is what `baseline.rule` says, and the fall-through equals the baseline. | **closed** |
| O-FL-4 (edge-day short tier reachable only on Transit Pass) | The mid-drive boundary is now 150 miles. On a 120-mile-threshold level, one-way miles of 120 to under 150 select the short-drive share, so the tier is reachable wherever a stay entry exists. | closed |
| O-FL-5 (local-miles fall-through never bears weight) | The regional boundary is now 150 miles. A stay with lodging on the Mileage Reimbursement level (threshold 120) and one-way miles of 120 to under 150 selects the fall-through (0 local miles) while local trips > 0, so the tier now changes the result. | closed |
| round-2 closures (F-C1, O-RC-1…5, O-AB-1, O-PS-1, O-PS-2, O-OV-2…4, weekday) | Re-read; the texts are unchanged from revision_2 except the four edits above. | still closed |
| O-PG-3, O-IN-2, O-SC-1, O-RC-6, O-AB-2, O-PG-1, O-PG-2, O-OV-1, O-FL-1…3 | Unchanged. | open (observations) |

### Re-derived charter-global checks

- **policy_conflict_scan**: unchanged structure (6 policies, 2 disjoint trees). PASS.
- **rule_compute_equivalence**:
  - Mechanical sweep: 0 non-verbatim `compute_basis` values, 0 compute bindings without a basis, every `baseline.rule` sentence in its rule, and bindings disjoint in every policy.
  - Sentence read of the four edits: settlement tier 2 ↔ `return_registered_on > out_date`; waiting-charge three branches ↔ the three sentences; new `baseline.rule` ↔ `waiting_charge: K('flat_strand_charge')`; parameter changes are values only.
  - PASS.
  - New observation **O-RC-7**: the settlement clause "because the stay was extended while the member was away" is explanatory; no record or compute branch tests for an "extension". Read as a condition, it would need evidence that no table carries. It is phrased as a reason ("because"), so no second reading can be demonstrated.
- **prerequisite_graph** / **prerequisite_sentences**: all four sentences are unchanged and verbatim in their rules; state form, one writer each, acyclic. PASS.
- **override_declarations**: no new overwrite. The edits touch only extended-only quantities (settlement clock, waiting charge, two distance boundaries), so there is no undeclared override. PASS.
- **action_binding_and_uuids**: carried forward from revision_2 (`task_tools.py` hash unchanged). PASS.

### factor_ladders (re-derived; tier reachability swept for every ladder)

| policy | factors (P/M) after the tests | live tiers |
| --- | --- | --- |
| stay | 6 (5 P / 1 M) | all 3 on every ladder (edge-day short tier: 120–<150 mi) |
| mileage | 4 (2 P / 2 M) | all 3 (local miles fall-through bears weight at 120–<150 mi with local trips) |
| settlement | 4 (3 P / 1 M) | all 3 (clock tier 2 via a late-registered return leg) |
| expiry | 4 (3 P / 1 M) | all 3 |
| load | 5 (4 P / 1 M) | all 3 |
| alt | 6 (5 P / 1 M) | all 3 (waiting charge: 30 < m < 60 / 60–89 / ≥ 90 on a 30-minute level) |

- Each task still has at least 1 multi-source factor and at least 1 cross-difficulty factor.
- Fall-through = baseline on every factor.
- No two tiers select the same value or method.

New observations (no red light):

- **O-FL-6**: waiting-charge tiers 1 and 2 are both metered at the same 0.45 per minute and differ in where metering starts (the pickup window vs the late threshold). They are accepted as distinct methods by the same standard applied to `settlement_clock_start` and `coverage_months_counted` (the tier selects a different anchor). Tier 3 (flat) differs in kind in any case, so the factor's `method` label stands either way. There is a jump in the charge at 3× the threshold (at 89 minutes: 26.55; at 90 minutes: 40.50).
- **O-PS-3** (latent): clock tier 2 relies on reading the mileage condition "for a trip registered with a trip number before the appointment" as satisfied by the trip's first registration (its outbound leg). A reader who required every leg, including a late-added return leg, to be registered before its own appointment would still reach tier 2, because the return leg is registered before the return appointment. Only a reader who required every leg to be registered before the **outbound** appointment would find tier 2 unreachable again. That third reading is not supported by the rule's words. Neither task's world instantiates tier 2.

### closing_checklist (revision_3)

- Per-task files carry revision_3 sections; older revisions are untouched.
- Coverage: 6 policies over 2 disjoint tasks. Tools closed; uuid8s independent (unchanged).
- Trees: 2 prerequisite problems each; value_input edges 2 and 1; owner=user roots; acyclic.
- Factors: every computation has 4 to 6 factors after the tests, with ≥2 parameter and ≥1 method; every ladder has three live, disjoint tiers stated in its rule; every factor bears weight on its task's world against an honest baseline; every all-baseline number differs from gold (figures in the task files); each task has multi-source and cross-difficulty factors, with the other product's rows seeded.
- Gates re-run on the final form: the coordinator's round-3 snapshot (all 7 green, full output) is the re-run on this final form (`ride.extended.yaml` `a65a3a86…`, `task_tools.py` `07483c61…`). The auditor did not re-run them; the skill has the coordinator supply them.
- **Difficulty status after revision_3: PASSED at the source layer.** Task 0 PASS, task 1 PASS. Every red light from rounds 1 and 2 is closed; the remaining items are observations.
