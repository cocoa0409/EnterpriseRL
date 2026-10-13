# Policy-task audit — collection_appointments / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (erl-task-policy-audit), not the instantiating agent.
- Freeze time: 2026-10-04T16:47Z (UTC), before any task file was opened.
- Frozen inputs (sha256, re-computed by the auditor and equal to `audits/_views/policy_task/collection_appointments/HASHES.txt`):
  - `tasks/collection_appointments/visits.extended.yaml` = `2405d15e3ed69884aa2e83493a6cb4b63cd079540c9e8ed5ec51696b3c460e65`
  - `tasks/collection_appointments/task_tools.py` = `dda57fd993a943e800131870bdb40014a199114e7c6a1d1364d992cc465f1ffe`
- Fields permitted: `blueprint/` (blueprint.yaml, db_schema.json, share_tools.py, products/*.yaml), `visits.extended.yaml`, `task_tools.py`, the masked views `task0.view.json` / `task1.view.json` (frozen_time, user_scenario, initial_state only), `erlbench/` and the gate scripts' DSL evaluator (`skills/erl-task-instantiate/scripts/check_compute.py`, read for the semantics of SUM/XCOUNT/EXISTS/CFIELD/MONTHS/DAYS only).
- Fields masked (never opened while this section was written): every `tasks/collection_appointments/tasks/*.json`, hence `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`; the instantiate worklog; any earlier audit (none exists — this is revision 0).
- Entry conditions (Step 0): the brief carries the gate snapshot — check_extended EXTENDED OK, check_task_tools TASK TOOL CONTRACT OK, replay_tasks REPLAY OK, check_solvability SOLVABILITY OK, check_compute COMPUTE OK, check_grounding GROUNDING OK, check_cross_fire SCOPE OK; check_traceability deferred (KB not rendered). Masked views and their hashes are supplied. Entry conditions met; the gates were not re-run by the auditor.
- Base copy: lines 1-927 of `visits.extended.yaml` are byte-identical to `blueprint/products/visits.yaml` (`diff` shows only the two appended separator lines 928-929). Base copy verbatim: PASS.

### policy_conflict_scan

Seven extended policies, seven distinct target tools:

| policy | subject | target_tool (owner) | fee line written |
| --- | --- | --- | --- |
| visits_ext_trip_charge | visits_fee_assessed | assess_trip_fee_73c5b19a (agent) | trip_fee |
| visits_ext_household_charge | visits_fee_assessed | assess_household_fee_59046739 (agent) | additional_patient_fee |
| visits_ext_weekend_charge | visits_fee_assessed | assess_weekend_surcharge_242d901c (agent) | weekend_surcharge |
| visits_ext_home_visit_settlement | visits_fee_paid | pay_home_visit_fees_e8e0d8a4 (user) | payment against the trip_fee line |
| visits_ext_missed_visit_charge | visits_fee_assessed | assess_no_show_fee_12606755 (agent) | no_show_fee |
| visits_ext_missed_visit_settlement | visits_fee_paid | pay_missed_visit_fee_baa116ed (user) | payment against the no_show_fee line |
| visits_ext_late_change_charge | visits_appointment_rescheduled | reschedule_home_visit_6b0b2488 (agent) | move + late_cancellation_fee |

- Overlapping subjects: the four `visits_fee_assessed` policies are separated by fee type (one line per fee type, base "A fee type is assessed at most once per visit"); the two `visits_fee_paid` policies are separated by object (a collected home visit's service charges vs. a missed visit's no-show charge) — a no-show visit carries no trip fee (base: "a no-show assesses only the no-show fee, never a trip fee"), so no visit falls under both. No two policies reach different values for one quantity.
- Triggers / time anchors: every computation is evaluated "today" (frozen date) on the records as they stand at the write; all windows are counted back from today (DSL MONTHS/DAYS against NOW). The trip charge's weekend-dispatch band and the weekend charge both price a Sunday; this is a declared double source (the weekend charge's dispatch-overlap step reads the assessed trip fee), not a conflict.
- Eligibility / terminal states: all base eligibility (fee_states, homebound_no_trip_fee, reschedule_booked_only, booking eligibility, waiver/refund dedup) is inherited unweakened; no tool checks any of it (see action_binding_and_uuids).
- Cross-category read boundaries: orders (standing flag, class, charges, rejections, status/hold, billing method), invoices (status, payments), coverage (status), plans (status, missed installments) — all read-only, all reachable through share finders `find_orders`, `find_order_events`, `find_invoices`, `find_invoice_transactions`, `find_coverages`, `find_payment_plans`, `find_plan_transactions`.
- Scope partition (derived blind, from the prerequisite graph and the two masked views): the graph has two components — {trip, household, weekend, home_visit_settlement} and {missed_visit_charge, missed_visit_settlement, late_change_charge}. Task 0's world (a collected Sunday home visit with two household members, no fee yet assessed) instantiates the first; task 1's world (a booked home visit due tomorrow plus an unpaid no-show) the second. The two scopes are disjoint and jointly cover all seven extended policies. (The task files compare this against the revealed `charter_scope`.)

### rule_compute_equivalence

Swept every binding's `compute_basis` quotation against its rule and back. Every quantity, window, tier, branch, cap/floor and rounding point in the seven computes is quoted verbatim from its own rule, and every factor tier in `factors[].ladder` is a rule sentence and a branch of its `decides` binding. Windows: "last six months" -> `within_months=6`; "last three months" -> `within_months=3`; "last 12 months" -> `within_months=12` (MONTHS counts whole months back from today); "calendar days from X to Y" -> `DAYS(X, Y)`. Day-of-week: `DAYS('2026-01-03', d) % 7` (0 = Saturday, 1 = Sunday; 2026-01-03 is a Saturday) and `DAYS('2026-01-05', d) % 7 >= 5` (Saturday/Sunday; 2026-01-05 is a Monday) — both correct. Rounding: every policy says "rounded to the cent only once, at the end" = single `RND(...,2)` in `result`. Floors: "never goes below 0.00" in trip and late-change = `MX(0.0, ...)`.

Rule sentences that compute does not implement (rule -> compute direction). Each is an eligibility statement rather than a tier, and none is exercised by either task world, so none is demonstrable as a second answer; recorded as observations:

- O-1 `visits_ext_trip_charge`: "No trip charge is assessed at all when the patient's Medicare homebound certification is on file for the visit" — no branch in compute (left to base gate `homebound_no_trip_fee`).
- O-2 `visits_ext_household_charge`: standard method "a visit that drew no additional household member carries no household charge" — compute with `hh_members = 0` returns `hh_early_add` (10.00 / 6.00 for an early visit), i.e. a non-zero household charge the rule says does not exist.
- O-3 `visits_ext_weekend_charge`: "a weekday visit carries none" — compute has no weekday branch (wk_day_rate falls to 35.00 on a weekday).
- O-4 `visits_ext_late_change_charge`: "a change made 24 hours or more before the current start carries no charge" — compute has no notice branch and returns a positive charge for any change.
- O-5 `visits_ext_home_visit_settlement`: "the patient has no live health coverage on file" is implemented as `EXISTS('coverage', status='active')`; the coverage charter's states are pending_verification / active / inactive / terminated and its own text uses "live" for any not-terminated record ("A fourth live coverage is refused until one is terminated"). A patient with only a pending_verification or inactive coverage gets two readings (5% vs 10%). Not exercised (task 0's only coverage is terminated).

### action_binding_and_uuids

- `(target_tool, computes)` pairs: seven pairs, each claimed by exactly one policy. PASS.
- Tool bodies (`task_tools.py`): every write tool finds the visit, writes one `visit_events` row (or updates the visit) and returns a receipt; none refuses, errors or hints on a missing prerequisite, none computes a fee. PASS (the tool layer judges no prerequisite).
- Docstrings: none names another tool or states a position in a sequence with before/after/first. Observation O-6: `pay_home_visit_fees_e8e0d8a4.assessed_event_id` says "as returned when the trip charge was posted or read from the visit's fee history" and `pay_missed_visit_fee_baa116ed.assessed_event_id` says "as returned when the no-show charge was posted ..." — they presuppose the depended-on line exists, but the settlement rules themselves already say the payment is "recorded against the visit's assessed trip fee" / "the assessed no-show fee", so the docstrings add nothing the rule does not state.
- uuid8s: 73c5b19a, 59046739, 242d901c, e8e0d8a4, 12606755, baa116ed, 6b0b2488 — no shared prefix or suffix, no sequence, none reused. PASS.

### prerequisite_graph

Edges (blocked <- depended-on, kind, gate):

1. household <- trip, value_input, `hh_trip_entry`
2. weekend <- trip, value_input, `wk_trip_entry`
3. weekend <- household, value_input, `wk_household_entry`
4. home_visit_settlement <- trip, value_input, `st_open_trip`
5. home_visit_settlement <- household, value_input, `st_open_household`
6. home_visit_settlement <- weekend, value_input, `st_open_weekend`
7. missed_visit_settlement <- missed_visit_charge, value_input, `pm_open_no_show`
8. late_change_charge <- missed_visit_settlement, state_gate, `visit_events.assessed_event_id`

- `prerequisite` filled on every policy (trip and missed_visit_charge `[]`). Every `problem` is an extended policy id of this file, none self, none base. Acyclic (two DAG components; topological orders trip -> household -> weekend -> settlement and missed charge -> missed settlement -> late change). PASS.
- Every `policy_source` is verbatim in its own policy's rule (checked string-for-string). All `form: state`, no `fallback_reason` anywhere. Every value_input `gate` is a compute binding of the blocked policy; the state_gate `gate` is a `<table>.<field>`. Every `resolved_by` is the depended-on policy's target_tool and its effect makes the gate's input change (verified numerically in task 0's file for edges 1-6, in task 1's file for edges 7-8). No authoring-viewpoint words in any `prerequisite` field.
- Observation O-7 (edge 8): `condition` reads "For every visit of the patient with status no_show ..." while the sentence reads "every home visit of the patient recorded as a no-show" — the condition drops "home" and is broader than the sentence (a PSC no-show, which carries no no-show fee, would block it forever). Task 1's patient has a single no-show, which is a home visit, so no consequence there.

### prerequisite_sentences

Four-point test per edge (ordering connective / record-visible state in the finders' words / no tool, id or code token / strength equal to the condition):

| edge | sentence (verbatim) | connective | state | single resolving write |
| --- | --- | --- | --- | --- |
| 1 | "The household charge on a home visit is fixed only after the visit carries an assessed trip fee." | only after | assessed trip fee on the visit's fee history | only `assess_trip_fee` writes a `visits_fee_assessed` / `trip_fee` line |
| 2 | "The weekend charge on a Saturday or Sunday home visit is not worked out until the visit's fee record shows its assessed trip fee." | not ... until | same | same |
| 3 | "Before the weekend charge is worked out for a visit that drew additional household members, the visit must carry its assessed additional-patient fee." | before | assessed additional-patient fee | only `assess_household_fee` |
| 4 | "The home-visit settlement charge is taken only after the trip fee assessed on the visit stands on its fee record." | only after | assessed trip fee | only `assess_trip_fee` |
| 5 | "No home-visit settlement charge is taken until the visit carries the assessed additional-patient fee owed for the household members drawn at it." | no ... until | assessed additional-patient fee | only `assess_household_fee` |
| 6 | "For a visit dated on a Saturday or Sunday, the home-visit settlement charge is worked out only after its assessed weekend surcharge is on the fee record." | only after | assessed weekend surcharge | only `assess_weekend_surcharge` |
| 7 | "The missed-visit settlement charge is fixed only after the missed visit carries its assessed no-show fee." | only after | assessed no-show fee | only `assess_no_show_fee` |
| 8 | "A home visit is not moved to a new date until every home visit of the patient recorded as a no-show carries a paid no-show fee." | not ... until | a paid no-show fee (a `visits_fee_paid` line against the no-show line) | `pay_missed_visit_fee` (the home-visit settlement's scope is a collected visit, so it cannot be read as the resolver) |

Derivation (sentence + records + depended-on rule -> resolving action, one reading each): the fee lines named ("assessed trip fee", "assessed additional-patient fee", "assessed weekend surcharge", "assessed no-show fee", "paid no-show fee") are exactly the fee types `find_visit_events` lists; the only policy whose own rule posts that line is, respectively, the trip charge ("posted as one assessed trip fee"), the household charge ("posted as one assessed additional-patient fee"), the weekend charge ("posted as one assessed weekend surcharge"), the missed-visit charge ("posted as one assessed no-show fee") and the missed-visit settlement ("one card payment ... recorded against the assessed no-show fee"). No sentence is broader or narrower than its condition except O-7. No rule restates another's sentence, names a tool, a policy id or a snake_case token. No rule states a cross-problem order that grounds no edge; no base sentence grounds an edge. PASS.

Observation O-8 (edge 8, policy-level): the sentence demands a *paid* no-show fee. A no-show whose fee was waived (base `visits_evt_fee_waiver`: first_occurrence_courtesy / severe_weather_closure / laboratory_initiated_cancellation) or that was never assessed because the visit was a recollection (base: "No fee of any kind is assessed on a recollection visit") can never carry a paid no-show fee, so such a patient could never move any home visit. Not exercised by task 1 (its single no-show is an initial collection with no waiver).

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry:

- `visits_evt_fee_assessment` (refs of trip, household, weekend, missed charge): "may be assessed only on a visit whose status is collected, cancelled or no_show" — followed. "the trip fee for the visit's service zone from trip_fee_by_zone" — replaced, declared (trip). "plus additional_patient_fee for each additional household member collected" — replaced, declared (household); base `formula.fee_amount_additional_patients` is the same quantity and falls with that clause. "plus weekend_surcharge when the appointment date is a Saturday or Sunday" — replaced, declared (weekend). "each fee type is one line" — followed. Homebound sentence — followed (restated by trip). "late-cancellation and no-show fees follow the cancellation rule; a no-show assesses only the no-show fee, never a trip fee" — followed. Incomplete / recollection exemptions — inherited, untouched. "A fee type is assessed at most once per visit" — followed. "Fees are charged to the card on file when fee_due_timing is at_completion; PSC, pediatric, timed and facility visit types carry no patient fees." — **not named by any overwrite** (see O-9).
- `visits_evt_cancellation_and_no_show` (missed charge): "assesses no_show_fee when above 0.00" — replaced, declared. All other sentences inherited.
- `visits_evt_fee_payment_and_refund` (both settlements): "A fee is paid in full in one payment with a method listed in fee_payment_methods" — replaced, declared by both policies on disjoint objects. Empty-method-list, refund, refund-once and "not reduced by financial assistance" sentences — inherited; the settlement allowances are not financial assistance.
- `visits_evt_reschedule` (late change): the "with less notice ... assesses that fee once, exactly as a late cancellation would" clause — replaced, declared. Booked-only, max reschedules, booking-rule-as-of-change, timely-at-exactly-24h, recollection exemption — inherited.

Anonymous intermediates / 0-1 multipliers / dropped branches: none found — each extended deviation acts on the quantity its declared clause governs.

Observation O-9: base "Fees are charged to the card on file when fee_due_timing is at_completion" (Mobile In-Home `fee_due_timing: at_completion`) is not named by `visits_ext_home_visit_settlement`, whose rule has the patient settle on request by one card payment of a reduced amount. The base sentence fixes a mechanism and timing, not an amount (the amount clause "paid in full" is declared replaced), and no write in the charter executes a card-on-file charge, so no second scored value can be produced from it; whether it bears on a task is examined in task 0's file.

### factor_ladders

Per policy (labels as declared; "honest" = the auditor's reading of whether the tiers change the algorithm or only substitute a number into one formula):

| policy | factor | label | tiers (fall-through last) | multi-source? | cross_difficulty | label honest? |
| --- | --- | --- | --- | --- | --- | --- |
| trip | weekend_dispatch_band | method | Sun +2 bands / Sat +1 / weekday booked band (cap zone 3) | no (date) | — | no: one formula `fee(MN(band+k,3))`, k ∈ {2,1,0} |
| trip | series_route_band | method | standing ∧ ≥6 charges: nearer band fee / standing ∧ 3-5: average of two band fees / dispatch band fee | yes (orders row ∧ order_events) | orders | yes (pricing basis changes; averaging) |
| trip | handling_kit | parameter | 20 / 12 / 0 by class | no | orders | yes |
| trip | early_route_premium | parameter | <07:30 ∧ weekend 15 / <07:30 ∧ weekday 8 / 0 | no (visit row) | — | yes |
| trip | dispatch_notice_rate | parameter | ≤3 d 1.15 / ≥21 d 0.95 / 1.00 | no | — | yes |
| trip | redraw_credit | parameter | lab-fault rejection 25 / other rejection 10 / 0 | no (order_events) | orders | yes |
| household | series_member_rate | parameter | 25 / 30 / 35 | yes | orders | yes |
| household | short_notice_member_addition | parameter | +5 / −3 / 0 | no | — | yes |
| household | member_specimen_kit | parameter | 4 / 2 / 0 | no | orders | yes |
| household | shared_extended_dispatch | method | ≥2 members ∧ trip ≥1.25×published: 1+(n−1)·0.5 / ≥2 ∧ between: 1+(n−1)·0.75 / n | yes (visit ∧ visit_events) | — | **no**: one formula `1+(n−1)·s`, s ∈ {0.5, 0.75, 1} (n = 1+(n−1)·1) |
| household | early_household_addition | parameter | 10 / 6 / 0 | no | — | yes |
| weekend | weekend_day_rate | parameter | 50 / 45 / 35 | no | — | yes |
| weekend | weekend_courier | parameter | 25 / 15 / 0 | no | orders | yes |
| weekend | weekend_staffing_notice | parameter | +10 / −5 / 0 | no | — | yes |
| weekend | weekend_dispatch_overlap | method | ×0.50 / ×0.75 / ×1 | no (visit_events vs visit zone) | — | **no**: a multiplier substituted into one formula |
| weekend | weekend_per_person_staffing | method | ×(1+n)·0.5 / ×1.25 / ×1 | yes (visit_events ∧ visit) | — | yes (per-person vs once-per-visit) |
| weekend | series_weekend_rotation | method | ×0.65 / ×0.80 / ×1 | yes | orders | **no**: a multiplier |
| home_visit_settlement | settlement_day_count | method | from posting date / from collection less (lag−3) / from collection | no | — | yes (anchor changes) |
| home_visit_settlement | prompt_settlement_allowance | parameter | 5% / 2% / 0 | yes (days ∧ invoices) | invoices | yes |
| home_visit_settlement | multi_charge_allowance | parameter | 3% / 1% / 0 | no | — | yes |
| home_visit_settlement | self_pay_allowance | parameter | 10% / 5% / 0 | yes (orders ∧ coverage) | orders (+coverage) | yes |
| home_visit_settlement | paying_history_allowance | parameter | 3% / 1% / 0 | no | invoices | yes |
| missed_visit_charge | missed_weekend_dispatch_rate | parameter | 80 / 75 / 60 | no | — | yes |
| missed_visit_charge | wasted_long_dispatch | parameter | z3 ∧ ≤3 d 20 / z2 ∧ ≤3 d 10 / 0 | no (both on the visit row) | — | yes |
| missed_visit_charge | missed_early_route | parameter | 10 / 5 / 0 | no | — | yes |
| missed_visit_charge | order_held_at_missed_visit | method | ×0.50 / ×0.75 / ×1 | yes (order ∧ visit date) | orders | **no**: a multiplier |
| missed_visit_settlement | missed_visit_day_count | method | from posting date / from appointment less (lag−3) / from appointment | no | — | yes |
| missed_visit_settlement | early_settlement_relief | parameter | 10% / 4% / 0 | yes | invoices | yes |
| missed_visit_settlement | payment_plan_standing | parameter | 6% / 2% / 0 | yes (plans ∧ plan_transactions) | plans | yes |
| missed_visit_settlement | invoice_payment_record | parameter | 5% / 2% / 0 | no | invoices | yes |
| late_change_charge | change_day_rate | parameter | 55 / 45 / 40 | no | — | yes |
| late_change_charge | repeat_change | method | ×1.25 / ×1.50 / ×1 | no (visit row) | — | **no**: a multiplier |
| late_change_charge | prepared_collection_kit | parameter | 15 / 8 / 0 | no | orders | yes |
| late_change_charge | route_rebuild | parameter | z3 ∧ day-of/day-before 10 / z2 ∧ same 5 / 0 | no | — | yes (but see F-3) |
| late_change_charge | household_rescheduling | parameter | 8·n / 5·n / 0 | no | — | yes |
| late_change_charge | order_on_hold_deduction | parameter | 15 / 8 / 0 | no (order row) | orders | yes |

Structure checks:
- Counts per policy as declared: trip 6 (2 method), household 5 (1 method), weekend 6 (3 method), home_visit_settlement 5 (1), missed_visit_charge 4 (1), missed_visit_settlement 4 (1), late_change_charge 6 (1). All within 4-6, all ≥2 parameter, all ≥1 method **as labelled**.
- After honest relabelling: trip 1 method, weekend 1 method, both settlements 1 method each; **household, missed_visit_charge and late_change_charge have 0 honest `method` factors** (F-1, F-2).
- Every ladder has three pairwise-disjoint tiers, each stated in the rule with its condition and value/method, each a branch of its `decides` binding; bindings are disjoint within each policy; no `decides` is `result`. No two tiers of a ladder select the same value or method. Every fall-through equals what `baseline.rule` states for that input (the published zone fee, 35.00 per member, 35.00 weekend, 60.00 no-show, 40.00 late change, no allowance / no relief, the plain day count).
- `baseline.rule` of every policy is a sentence of its `rule` and is self-sufficient (a reader computes a definite number from it and the records).
- Business realism: no tier value is a straw man (each fall-through is the published fee or "no allowance"). One vacuous conjunct found (F-3).
- Multi-source per component: the trip/household/weekend/settlement component carries several (series_route_band, series_member_rate, prompt_settlement_allowance, self_pay_allowance, ...); the missed/late component carries order_held_at_missed_visit, early_settlement_relief, payment_plan_standing. Cross-difficulty categories read: orders, invoices, coverage, plans.

### findings

- **F-1 SOURCE-FACTOR RED (mislabelled effect).** Symptom: five factors labelled `method` have tiers that only put a different number into one formula. Evidence: `weekend_dispatch_band` (trip) — `tr_pricing_band = MN(tr_booked_band + k, 3)`, k ∈ {2, 1, 0}; `shared_extended_dispatch` (household) — `1 + (hh_members − 1) * s`, s ∈ {0.50, 0.75, 1} (the fall-through "every member counts in full" is the same expression with s = 1, since n = 1 + (n−1)·1); `weekend_dispatch_overlap` (weekend) — `× {0.50, 0.75, 1.0}`; `series_weekend_rotation` (weekend) — `× {0.65, 0.80, 1.0}`; `order_held_at_missed_visit` (missed charge) — `× {0.50, 0.75, 1.0}`; `repeat_change` (late change) — `× {1.25, 1.50, 1.0}`. The rule's own wording for each is "is multiplied by x" / "counts as half / three quarters of a member" / "priced N bands farther out", i.e. a rate or offset. Root cause: multiplier and offset tiers labelled as methods. Affects tasks 0 (trip, household, weekend) and 1 (missed charge, late change).
- **F-2 SOURCE-FACTOR RED (method floor).** Consequence of F-1 for three policies: once the dishonest labels are struck, `visits_ext_household_charge`, `visits_ext_missed_visit_charge` and `visits_ext_late_change_charge` each declare 0 honest `method` factors against a floor of 1. Affected: household in task 0; missed charge and late change in task 1. Demonstrated per task in each task file.
- **F-3 SOURCE-FACTOR RED (vacuous conjunct, unreal ladder).** `visits_ext_late_change_charge.route_rebuild`: tiers "service zone 3 AND the change is recorded on the appointment date or the day before" / "service zone 2 AND ...". The policy charges only a change "with less than 24 hours' notice before its current start"; a change recorded two or more calendar days before the appointment date is at least 24 hours before any start time, so every change that reaches this write is recorded on the appointment date or the day before. The second conjunct holds of every customer who reaches the write and divides no one; the ladder is a zone-only ladder written as a compound. Affects task 1.
- Observations (no demonstrable consequence on either task): O-1 to O-5 (rule sentences without a compute branch / the "live coverage" reading), O-6 (payment docstrings presuppose the depended-on line), O-7 (edge-8 condition broader than its sentence), O-8 (a waived or never-assessed no-show blocks every later home-visit move forever), O-9 (base card-on-file-at-completion sentence not named by any overwrite).

## closing_checklist

Not closed: tasks 0 and 1 carry SOURCE-FACTOR RED findings (see `0.md`, `1.md`), so Step 4's checklist does not apply. The instantiation gates were not re-run by the auditor.

## post_reveal_note (appended after both reveals; the sections above are unchanged)

- Both revealed `charter_scope` lists match the blind partition: task 0 = {trip, household, weekend, home_visit_settlement} + their four tools; task 1 = {missed_visit_charge, missed_visit_settlement, late_change_charge} + their three tools. Pairwise disjoint, jointly complete over the seven extended policies and seven tools.
- Both tasks' gold values, trees and factor sensitivities equal the blind derivations figure for figure (see `0.md`, `1.md` § source_gt_comparison). The REDs are factor-structure findings (F-1, F-2, F-3) plus one false proof assertion in task 1; no SOURCE-POLICY, SOURCE-CHAIN or SOURCE-TASK RED.
- The difficulty does not close (see § closing_checklist).

## revision_2

### charter_global_frozen (revision 2)

- Re-audit requested by the coordinator (round 2). Freeze time 2026-10-04T17:50Z (UTC), written before either revised task file was opened. Revision-0 text above is untouched.
- Shared inputs moved, so every charter-global section is re-derived in full, not carried forward: `visits.extended.yaml` `2405d15e…0e65` -> `5f7d06eb2d2c1d2b9c92b9fed7ca1b2245295734528e4b34d497aa76b998f0d8`; `task_tools.py` `dda57fd9…1ffe` -> `74e17bc7053017d8435343a4a70c1af333329f37a343ca7a879b92412ffedac5` (both re-computed by the auditor, equal to the round-2 HASHES.txt). Views: task0 unchanged (`82fb83b7…`), task1 `2071c4b6…` -> `9abe0bf0c5b3a80ad033e7bd62268872260ded95e4bf2f583a4a395495cdbea2`.
- Masked as in revision 0. Gate snapshot supplied by the coordinator (all OK; traceability deferred). Base copy lines 1-927 still byte-identical to `blueprint/products/visits.yaml`.
- contamination_disclosure: the coordinator's brief lists the item ids the reworker claims closed (no values). No task JSON, worklog or GT field was read before this section and both tasks' revision-2 frozen sections were on disk.

### What changed in the charter (read in full, policy by policy)

- trip: `weekend_dispatch_band` relabelled `parameter` (value "band offset +2/+1/0"); compute gains `tr_billed_to_medicare` and `result = 0.0 if tr_billed_to_medicare else …` quoting the homebound sentence.
- household: new early-household sentence — weekend start before 07:30 "per member drawn, 10.00 for each additional household member", weekday "once per visit, 6.00", else none; `early_household_addition` is now the `method`; `shared_extended_dispatch` relabelled `parameter`; `result = 0.0 if hh_members == 0 else …` with the rule sentence "a visit that drew no additional household member is charged nothing at all".
- weekend: `weekend_dispatch_overlap`, `series_weekend_rotation` relabelled `parameter`; `wk_is_weekend` branch makes a weekday charge 0.00 (quoting "a weekday visit carries none").
- home_visit_settlement: second overwrite declared against `visits_evt_fee_assessment` ("Fees are charged to the card on file when fee_due_timing is at_completion" -> charges not charged at completion "stay open on the visit and are settled when the patient asks to pay them"), with `base_policy_refs` extended; "a coverage on file counts as live until it is terminated, whatever its verification status" and `st_live_coverage` = active ∨ pending_verification ∨ inactive.
- missed_visit_charge: early-route sentence becomes weekend "per person booked, 10.00 for the patient and 10.00 for each additional household member", weekday "once per visit, 5.00"; `missed_early_route` is now the `method`; `order_held_at_missed_visit` relabelled `parameter` and its provider-side tier gains the conjunct "the patient has a live coverage on file (a coverage counts as live until it is terminated) to which the diagnosis codes must go" (coverage added to cross_category).
- missed_visit_settlement: unchanged.
- late_change_charge: new sentence "A change recorded two or more calendar days before the appointment date always has at least 24 hours' notice and carries no charge." with `lc_charged_window = lc_days_to_visit <= 1`; the prerequisite sentence becomes "A home visit is not moved to a new date until every home visit of the patient recorded as a no-show carries a no-show fee that is paid or waived, a no-show on a recollection visit excepted because it carries no fee." (condition: Mobile In-Home, not recollection, paid or waived line); route rebuild becomes four tiers (zone 3 same day 15.00 / zone 3 day before 10.00 / zone 2 same day 5.00 / otherwise 0.00); household rescheduling becomes day-before "per person booked, 5.00 for the patient and 5.00 for each member", same-day "once per visit, 12.00", and is now the `method`; `repeat_change` relabelled `parameter`.
- task_tools.py: only the two payment docstrings' `assessed_event_id` lines changed ("as listed in the visit's fee history"); every function body is unchanged and still writes unconditionally.

### policy_conflict_scan (revision 2)

Subjects, target tools, fee types and the two DAG components are unchanged; no two policies reach different values for one quantity. The new settlement overwrite and the base "charged to the card on file" clause no longer coexist. Blind scope partition unchanged: {trip, household, weekend, home_visit_settlement} / {missed_visit_charge, missed_visit_settlement, late_change_charge}. PASS.

### rule_compute_equivalence (revision 2)

Every new or changed binding quotes its own rule verbatim (`tr_billed_to_medicare`, `hh_early_add`, `result` of household, `wk_is_weekend`, `st_live_coverage`, `ms_early`, `ms_live_coverage`, `ms_hold_factor`, `lc_route`, `lc_household`, `lc_charged_window`), and every ladder tier is a rule sentence and a branch of its binding. Status of revision-0 observations: O-1 closed (homebound branch); O-2 closed (zero-member guard); O-3 closed (weekday branch); O-5 closed ("live" defined as not terminated, compute matches). **O-4 only partly closed**: the compute now zeroes a change recorded two or more calendar days ahead, but the rule's "a change made 24 hours or more before the current start carries no charge" also covers a change recorded the day before at a clock time earlier than the start (e.g. 07:00 the day before an 08:00 start = 25 h), which `lc_charged_window` (days ≤ 1) still charges. Not exercised by task 1 (16:20 for an 08:00 start = 15 h 40 min); remains an observation.

### action_binding_and_uuids (revision 2)

Seven pairs, one policy each; uuid8s unchanged and independent; bodies unchanged (no refusal or hint). O-6 closed: the payment docstrings now say "as listed in the visit's fee history" and no longer presuppose a prior posting. PASS.

### prerequisite_graph (revision 2)

Edges 1-7 unchanged. Edge 8 (late change <- missed settlement, state_gate, `visit_events.assessed_event_id`, form state) has a new sentence, verbatim in the late-change rule; its condition ("every Mobile In-Home visit of the patient with status no_show whose collection purpose is not recollection … a visits_fee_paid or visits_fee_waived line") now matches the sentence's scope ("every home visit … a no-show on a recollection visit excepted") and strength ("paid or waived"). O-7 closed. Acyclic, all `problem` ids valid, no authoring-viewpoint words. PASS.

### prerequisite_sentences (revision 2)

Edge 8 four-point test: "not … until" ✓; waited-on state "a no-show fee that is paid or waived" — a record-visible payment or waiver line against the no-show line ✓; no tool, id or code token ✓; scope/strength equal to the condition ✓. Single resolving write in this difficulty: "paid" is written only by `pay_missed_visit_fee_baa116ed`; no task or share tool writes a waiver, and a courtesy waiver under base `visits_evt_fee_waiver` applies "only when the patient asks" — so sentence + records + the missed-visit settlement rule ("one card payment … recorded against the assessed no-show fee") still lead to one action. O-8 closed (a waived or recollection no-show no longer blocks moves forever). Edges 1-7 unchanged and still pass. PASS.

### override_declarations (revision 2)

Same sentence-by-sentence result as revision 0, plus: base "Fees are charged to the card on file when fee_due_timing is at_completion" is now named by `visits_ext_home_visit_settlement.overwrite[0]` (O-9 closed); the remainder of that base sentence ("PSC, pediatric, timed and facility visit types carry no patient fees") is inherited. No undeclared override found. PASS.

### factor_ladders (revision 2)

| policy | factors (label) | honest method | multi-source present | notes |
| --- | --- | --- | --- | --- |
| trip | weekend_dispatch_band (P), series_route_band (M), handling_kit (P), early_route_premium (P), dispatch_notice_rate (P), redraw_credit (P) | series_route_band | yes | labels now honest |
| household | series_member_rate (P), short_notice_member_addition (P), member_specimen_kit (P), shared_extended_dispatch (P), early_household_addition (M) | early_household_addition: per member drawn (10.00 × n) vs once per visit (6.00) vs none — the count the amount scales with changes, the same kind of per-person/per-visit change accepted for weekend_per_person_staffing in revision 0 | yes | |
| weekend | day_rate (P), courier (P), staffing (P), dispatch_overlap (P), per_person_staffing (M), rotation (P) | per_person_staffing | yes | labels now honest |
| home_visit_settlement | unchanged (settlement_day_count M + 4 P) | yes | yes | |
| missed_visit_charge | weekend_dispatch_rate (P), wasted_long_dispatch (P), missed_early_route (M), order_held_at_missed_visit (P) | missed_early_route: per person booked (10.00 × (1 + n)) vs once per visit (5.00) vs none | yes (order ∧ visit date ∧ coverage) | |
| missed_visit_settlement | unchanged | yes | yes | |
| late_change_charge | change_day_rate (P), repeat_change (P), prepared_collection_kit (P), route_rebuild (P, 4 tiers), household_rescheduling (M), order_on_hold_deduction (P) | household_rescheduling: per person booked (5.00 × (1 + n)) vs once per visit (12.00) vs none | no single factor with conditions over distinct records (task-level multi-source comes from the missed-visit policies) | |

- Every policy: 4-6 factors, ≥2 parameter, exactly one honest method; every ladder ≥3 pairwise-disjoint tiers stated in the rule and implemented in compute; no two tiers of a ladder share a value or method; fall-throughs equal what `baseline.rule` states; `baseline.rule` self-sufficient.
- F-1 closed (every factor's label now matches its tiers). F-2 closed (household, missed charge and late change each have one honest method). F-3 closed: route_rebuild now separates a same-day from a day-before change, and both occur among charged changes, so the date conjunct divides customers.
- New-ladder realism checks: (i) `order_held_at_missed_visit` tier 1's new coverage conjunct is nearly implied by its other conjunct — the orders charter places a missing_diagnosis hold only "when the order is billed to insurance" (`orders_evt_order_holds`) — but a coverage can be terminated while the hold stands, so the conjunct does divide customers; observation O-10. (ii) `household_rescheduling`: for a household of two or more members the day-before amount (5.00 × (1 + n) ≥ 15.00) exceeds the same-day amount (12.00), the reverse of the change-day rate's own gradient (55.00 same day > 45.00/40.00 day before); not exercised by task 1 (one member: 10.00 vs 12.00); observation O-11.

### findings (revision 2)

- F-1, F-2, F-3: closed (see factor_ladders).
- O-1, O-2, O-3, O-5, O-6, O-7, O-8, O-9: closed. O-4: partly closed, still open for a day-before change made at a clock time earlier than the start (observation; no task world exercises it).
- New observations: O-10 (near-implied coverage conjunct), O-11 (household-rescheduling gradient inverted for households of two or more).
- No new charter-global RED.

### closing_checklist (revision 2)

Pending the two per-task comparisons; see `post_reveal_note_r2` below.

### post_reveal_note_r2 (appended after both revision-2 reveals)

- Revealed charter_scope lists unchanged and equal to the blind partition; all gold values, trees and factor sensitivities equal the blind revision-2 derivations figure for figure.
- Task 0: SOURCE-TASK RED (design_rationale [1] still states the old settlement value 186.55; gold and recomputation 194.45). Task 1: PASS on all four relationships.
- Charter level: F-1, F-2, F-3 closed; no charter-global RED; open observations O-4 (partial), O-10, O-11.
- The difficulty does not close while task 0 carries a RED.

## revision_3

### charter_global_frozen (revision 3)

- Re-audit round 3. Freeze time 2026-10-04T18:16Z (UTC), before either task file was reopened. Earlier revisions untouched. (This block was first written at 18:16Z with shell-stripped code words and rewritten at 18:18Z, still before any reveal; content unchanged in substance. Both hashes are in `FREEZE_HASHES.txt`.)
- Hashes (re-computed, equal to round-3 HASHES.txt): `visits.extended.yaml` `5f7d06eb…f0d8` -> `cc4ed9e03c12b42274b5f2eaaf3c8ae2df7ea87f453a1e14c33f5700975030c6` (moved: charter-global sections re-derived); `task_tools.py` `74e17bc7…dac5` unchanged (action_binding_and_uuids carried forward from revision 2 on that hash); views unchanged (task0 `82fb83b7…`, task1 `9abe0bf0…`). Base copy lines 1-927 still identical to the blueprint.
- contamination_disclosure: only the coordinator's list of claimed item ids; nothing else read before this freeze.

### Changes found (revision 2 -> 3)

- late_change_charge: the first rule sentence now reads "A home visit moved on its appointment date or on the calendar day before it carries one late-change charge …"; `baseline.rule` ends "a move recorded two or more calendar days before the appointment date carries no charge"; the round-2 two-calendar-day sentence is replaced by "For a home visit the notice of a move is counted in calendar days from the date the move is recorded to the appointment date, not in hours, so a move recorded two or more calendar days before the appointment date is free whatever the clock time." Two new overwrites against `visits_evt_reschedule` name "A reschedule made at or beyond free_change_notice_hours before the current appointment start is free" and "Notice is measured in elapsed hours from the moment the change is recorded to the current appointment date and time, and a change at exactly free_change_notice_hours counts as timely." Household rescheduling same-day amount 12.00 -> 24.00 ("never less than the day-before amount for a household of up to three members"; `household_visit_day` = 24.0). No other compute change.
- missed_visit_charge: the 0.75 tier now also covers "a missing diagnosis while the patient has no live coverage on file, so that the patient had to put a coverage on file or switch the order to self-pay"; `ms_hold_factor` and the ladder carry the same branch.
- No other policy changed in substance (all bindings re-evaluated; see task files).

### Re-derived checks (revision 3)

- policy_conflict_scan: subjects, tools, fee types, components and scope partition unchanged. PASS.
- rule_compute_equivalence: every `compute_basis` string, every `policy_source`, every `baseline.rule` and every overwrite's `replaced_by` re-checked verbatim inside its own rule (scripted): all present. Late change: rule (charged iff moved on the appointment date or the calendar day before; notice in calendar days) and `lc_charged_window = lc_days_to_visit <= 1` now agree exactly — **O-4 closed**. Missed charge: the new 0.75 branch is present in rule, ladder and `ms_hold_factor`. PASS.
- override_declarations: the three superseded clauses of `visits_evt_reschedule` are verbatim base text; after replacement a home-visit move is charged iff recorded on the appointment date or the day before, counted in calendar days; every other reschedule sentence (booked-only, max reschedules, booking rule as of the change, recollection exemption) is inherited. Merged semantics unique. Observation O-12: base `visits_evt_cancellation_and_no_show` still measures a home-visit *cancellation*'s notice in elapsed hours, so a cancellation and a move recorded at the same moment are judged on different clocks; different subjects and tools, and neither task contains a cancellation, so no second scored value arises. PASS.
- prerequisite_graph / prerequisite_sentences: edges and sentences unchanged from revision 2; all `policy_source` verbatim. PASS.
- factor_ladders: counts unchanged (trip 5P/1M, household 4P/1M, weekend 5P/1M, settlement 4P/1M, missed charge 3P/1M, missed settlement 3P/1M, late change 5P/1M). `order_held_at_missed_visit`: the coverage conjunct now separates the 0.50 tier (live coverage) from the 0.75 tier (no live coverage), so it divides customers on a condition the business weighs — **O-10 closed**. `household_rescheduling`: same-day 24.00 ≥ day-before 5.00 × (1 + n) for every n ≤ `max_additional_patients` 3 (at most 20.00) — **O-11 closed**; tiers still distinct, method still per-person vs per-visit. PASS.
- findings (revision 3): no charter-global RED; O-4, O-10, O-11 closed; new observation O-12.

### post_reveal_note_r3

- Both round-3 task files match their blind revision-3 derivations figure for figure; charter_scope lists unchanged and equal to the blind partition. Task 0's revision-2 SOURCE-TASK RED is closed; task 1 stays PASS.

## closing_checklist (revision 3)

- Audit files: `0.md`, `1.md` correspond one-to-one with `tasks/0.json`, `tasks/1.json`; `_difficulty.md` alongside; revisions 0, 2, 3 appended in order, earlier text untouched; freeze hashes per revision in `FREEZE_HASHES.txt`; every revision-3 comparison carries PASS on all four relationships.
- Coverage and scope: the seven extended policies are covered exactly once (task 0: trip, household, weekend, home_visit_settlement; task 1: missed_visit_charge, missed_visit_settlement, late_change_charge), scopes pairwise disjoint across whole trees; seven task tools, each with an independent frozen uuid8 (73c5b19a, 59046739, 242d901c, e8e0d8a4, 12606755, baa116ed, 6b0b2488); tools and GT closed.
- Problem trees: task 0 — 3 prerequisite problems, 6 value_input edges (≥ 2), customer's own write `pay_home_visit_fees_e8e0d8a4`, acyclic; task 1 — 2 prerequisite problems, 1 value_input edge (≥ 1), customer's own write `pay_missed_visit_fee_baa116ed`, acyclic; the difficulty's eight edges form a DAG with no cross-task cycle.
- Factors: every computation declares a self-sufficient baseline and 4-6 factors with ≥2 honest `parameter` and exactly 1 honest `method`; each task has multi-source and cross-difficulty factors (orders, invoices, coverage, plans); every ladder ≥3 distinct tiers stated in its rule; every factor bears weight on its task's world and every fall-back number differs from gold.
- Gates re-run by the auditor on the final form (2026-10-04, read-only; `replay_tasks` with `--check`; artifact hashes verified unchanged before/after): EXTENDED OK · TASK TOOL CONTRACT OK · REPLAY OK · SOLVABILITY OK · COMPUTE OK · GROUNDING OK · SCOPE OK (traceability deferred to KB publication).
- Open observations carried (not grounds for rework): O-12 (cancellation notice still in elapsed hours vs calendar-day move notice), task 1 O-c (near-misses partly boundary/reading-level), O-d (persona conditional line).
- The collection_appointments difficulty passes the source-layer audit.
