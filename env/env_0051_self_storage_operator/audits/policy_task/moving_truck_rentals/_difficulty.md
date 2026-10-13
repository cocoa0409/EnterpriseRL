# Policy-task audit — moving_truck_rentals / charter-global

## charter_global_frozen

- Freeze time: 2026-10-10T19:45Z (written before any task's GT was revealed; nothing below is derived from a revealed GT).
- Auditor: erl-task-policy-audit subagent (independent of the instantiating agent).
- Freeze hashes (match the coordinator brief):
  - `tasks/moving_truck_rentals/truck.extended.yaml` sha256 `134bb967791ac0c74599f4cc3fb01378ca9009151a8bd612555fa044735d2e40`
  - `tasks/moving_truck_rentals/task_tools.py` sha256 `b179847a5dfac8739723b06f41c5137e31e2a5c87ed543a098e4bdc38e031c98`
  - masked views `0.view.json` sha256 `afc655a0…c8f7`, `1.view.json` sha256 `d5f8b1a0…95bb` (match)
- Read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/truck.yaml`, `blueprint/products/unit.yaml` (variant parameters only, for `military_discount_pct`), the extended charter, `task_tools.py`, the two masked views, `skills/erl-task-instantiate/scripts/check_compute.py` (expression semantics of DAYS/MONTHS/X*/CFIELD only).
- Masked and not read before the per-task freezes: every `tasks/<i>.json` field other than frozen_time / user_scenario / initial_state (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure*). No recursive search was run over the scenario or tasks directory.
- Entry conditions (Step 0): gate snapshot supplied by the coordinator — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; traceability deferred (needs the rendered KB); validate_scenario only `required document … not found`. Masked views and hashes supplied. Entry conditions met (traceability deferral noted, not a defect of this audit).
- Base copy: lines 1-1006 of the extended charter are byte-identical to `blueprint/products/truck.yaml` (diff shows only the trailing blank line). Scratch: `/tmp/run_0051/audit_moving_truck_rentals/charter_scan.py`.

### policy_conflict_scan

Extended policies (6) and their single target tools:

| policy | target_tool (owner) | computes | trigger | prerequisite edges |
| --- | --- | --- | --- | --- |
| truck_ext_late_cancellation_fee | cancel_truck_reservation_ee0618b8 (user) | late_cancellation_fee | on_request | [] |
| truck_ext_additional_day_charge | post_additional_rental_day_charge_add5e32c (agent) | amount | state_due | [] |
| truck_ext_move_in_mileage_allowance | apply_move_in_claim_miles_credit_24951572 (agent) | amount | state_due | -> late_cancellation_fee (state_gate, state); -> additional_day_charge (value_input, state) |
| truck_ext_move_in_rental_waiver | credit_move_in_rental_waiver_7c9a948d (agent) | amount | state_due | -> move_in_mileage_allowance (value_input, state) |
| truck_ext_first_day_rate | post_first_day_rental_fee_f35b099c (agent) | amount | state_due | [] |
| truck_ext_signing_authorization_hold | sign_truck_rental_contract_074f2414 (user) | deposit_hold_amount | on_request | -> first_day_rate (value_input, state) |

Overlap scan:
- **Base pricing sentence 1** ("A contract is charged base_rate_usd for each rental period started …; the first period is posted at pickup.") is superseded twice — by `truck_ext_first_day_rate` (first period) and by `truck_ext_additional_day_charge` (every later day). The two replacements partition the periods (first day / days after the first; the additional-day rule itself says "the first of them is the first-day rental fee posted when the contract opened"), so the merged semantics are unique. Compatible.
- **Base free-move-in sentence** ("On a free move-in contract the charges in free_move_in_waived_charges … are credited in full …, and the first free_move_in_included_miles miles are not charged.") is superseded twice — by the mileage allowance (the miles half) and by the rental waiver (the fee half, adding "the environmental fee of a free move-in contract stays chargeable"). Complementary halves; compatible.
- **Two `free_move_in_waiver` credits on one contract** (mileage credit against the mileage line, rental waiver against the first-day line) are distinct objects: `truck_evt_breakdown_and_corrections` dedup is per `reference_id`, and the two credits reference different charge lines. Compatible.
- **Additional-day charge vs base late return** (`truck_evt_late_return`, in `base_policy_refs` but not overwritten): on a return more than `extra_period_after_hours` late, base posts `extra_period_fee_usd` for the late period, and the additional-day rule posts a base-rate additional day for every rental day started, the late one included. Two clauses price the same late day. No task world returns late (task 0 returned before its scheduled return; task 1 is a pickup), so no consequence is demonstrable — observation O-1.
- **Free-move-in once-per-unit**: base `truck_agg_free_move_in_once` rule ("A cancelled or no-show reservation does not use the benefit") and its `dedup_contract` (duplicates = linked contracts in reserved/picked_up/returned/closed) treat a still-reserved linked booking as occupying the benefit, while the base measure `truck_msr_free_move_in_used` only counts linked rentals that already carry a `free_move_in_waiver` credit. Base-internal tension; the extended mileage sentence follows the rule/dedup reading. Not an extended override; observation O-2.
- Time anchors: late-cancellation notice is anchored at the cancellation moment (= handling time, the user tool stamps `now`); additional-day, mileage and waiver anchor on the contract's actual pickup/return; first-day and hold anchor on the reservation's scheduled dates and the handling date. No conflicting anchors.
- Cross-category read boundaries: unit (holdings + ledger), protect (plan on the claimed unit), autopay (authorization on the claimed unit / any active one). All reads only; no extended policy writes another category.
- **Claimed scope vs subjects**: the blueprint difficulty claim lists event_types `[truck_reservation, truck_reservation_change, truck_reservation_cancelled, truck_charge, truck_credit, truck_payment, truck_refund, truck_deposit_release, truck_damage_report]`; extended subjects also name `truck_return` (additional-day), `truck_pickup` (first-day, signing) and `truck_deposit_hold` (signing), which are not in the claim list. The blueprint summary does assign "signing the contract at pickup" to this difficulty, the categories are exclusive (truck only) and check_cross_fire is green, so no cross-difficulty collision results — observation O-3.
- Task scope partition (blind expectation from the masked views, to be checked against `charter_scope` after reveal): task 0 = {late_cancellation_fee, additional_day_charge, move_in_mileage_allowance, move_in_rental_waiver}; task 1 = {first_day_rate, signing_authorization_hold}. Disjoint and jointly covering all six.

### rule_compute_equivalence

Mechanical sweep (`charter_scan.py`): every compute binding of every extended policy has a `compute_basis` entry, and every `compute_basis` quotation, every `baseline.rule`, every `overwrite.replaced_by` and every `prerequisite.policy_source` is a verbatim substring of that policy's own `rule` (whitespace-normalised). Every factor's `bindings` exist in `compute`; factor binding sets are pairwise disjoint in every policy; every `decides` is an input binding, never `result`.

Manual sweep, rule -> compute and compute -> rule:
- late_cancellation_fee: notice days `DAYS(NOW, scheduled_pickup_date)` = "calendar days from the cancellation date to the scheduled pickup date" (cancellation happens at handling time); ladders 2+/1/same-day; peak by weekday of scheduled pickup; basis 3+/2/other booked days counted pickup-date->return-date; courtesy `XCOUNT(... within_months=1 ...admin_fee)` / `XCOUNT(... within_months=12 ... unit_rent_charge)`; product order and single final rounding all match. The free-cancellation branch is carried by the inherited base eligibility `free_cancellation_cutoff`, not by compute — acceptable (a gate, not a value). Wording risk on "within the last calendar month": see finding F-6.
- additional_day_charge: days started = calendar days + 1 if return time > pickup time (equivalent to base "periods of rental_period_hours elapsed hours started" for MST, no DST); last-day share noon/15:00/whole; booked share 3+/2/"a one-day booking"; second-day weekday = day after actual pickup; move-in share (pickup-or-return-date move-in / pickup-facility tenant / other). Gap: the rule's booked-length ladder names "three or more", "two" and "a one-day booking"; a same-day booking (0 calendar days by the rule's own count) is named by no sentence and falls to compute's `else 1.0` — compute decides a case the rule does not (observation O-4; no task world has a same-day booking on this policy).
- move_in_mileage_allowance: claimed unit = latest storage admin fee; size ladder covers the whole `unit_size` enum (large 10x15/10x20/10x25/10x30, medium 5x10/5x15/10x10, smaller 4x5/5x5); rental-day miles by count of base rental fee lines; trip miles by DAYS(pickup, move-in) 0 / 1..3; class miles; cross-facility on-or-before / after; protection multiple on an active plan of the claimed unit; floor after summing and multiplying; credited miles min(miles charged, allowance) × per_mile_usd. Equivalent.
- move_in_rental_waiver: first-day fee = base rental fee lines dated the actual pickup date; basis ÷ friday/weekend share by scheduled-pickup weekday; size, promotion, tenancy, facility (strictly-before / on-or-after), AutoPay (none / not active / active) shares; min with the contract balance (charges + refunds − credits − payments). Equivalent.
- first_day_rate: weekday rate, same-day duration rate (light vs truck classes), tenant discount on an active agreement at the pickup facility by MONTHS(move-in, handling date), advance discount by DAYS(reservation, scheduled pickup), military discount = class `military_discount_pct` / former / none, AutoPay discount ACH / card / none, discounts summed and taken once. Equivalent.
- signing_authorization_hold: card deposit by `deposit_method`; risk multiple debit/credit × reversal in 12 months; tenant share (24+ months and no late fee in 12 months / other tenant at pickup facility / none); military share; lead share (<2 / ≥14 / other); mileage estimate (light 40 mi / truck 80 mi / none, same-day bookings only); posted first-day fee added. Equivalent.

Result: rule/compute equivalence PASS charter-wide, with observation O-4.

### action_binding_and_uuids

- Each `(target_tool, computes)` is claimed by exactly one extended policy (six distinct tools, six policies).
- uuid8 tails: `ee0618b8`, `add5e32c`, `24951572`, `7c9a948d`, `f35b099c`, `074f2414` — all distinct, no shared prefix, no sequence, no near-copies. PASS.
- Tool bodies (task_tools.py lines 34-49, 77-90, 119-131, 158-170, 194-205, 246-262): each writes exactly the values given and checks no status, eligibility, prior write or amount; none refuses, errors or hints. The tool layer judges no prerequisite.
- Docstrings: none names another tool or uses before/after/first as an ordering word. `post_first_day_rental_fee_f35b099c` says "on a truck rental contract that is opening for pickup" and "The renter sees the first-day fee on the contract shown for signature" — a positional hint toward the signing write (see finding F-4, observation).

### prerequisite_graph

- `prerequisite` filled on all six (`[]` on late_cancellation_fee, additional_day_charge, first_day_rate).
- Every `problem` is an extended policy id of this file, never base, never self. Graph: mileage -> {late_cancellation, additional_day}; waiver -> mileage; signing -> first_day. Acyclic (two components).
- Every `policy_source` is verbatim in the blocked policy's own rule (sweep above). All edges `form: state`, no `fallback_reason` key on any edge (correct for state form).
- `resolved_by` equals the depended-on policy's `target_tool` on all four edges.
- `kind`/`gate`: value_input gates `rental_day_lines`, `claimed_size`, `first_day_fee_posted` are real bindings of the blocked compute; the state_gate `truck_rentals.status` points at a real eligibility gate (base `truck_agg_free_move_in_once.once_per_unit`, evidence `truck_rentals.linked_rental_id`, `truck_rentals.status`).
- `effect` texts are true of the tools (`apply_move_in_claim_miles_credit` sets `linked_rental_id`; `post_additional_rental_day_charge` / `post_first_day_rental_fee` add a `base_rental_fee` line; `cancel_truck_reservation` sets status `cancelled`).
- **Condition strength, edge mileage -> late_cancellation (F-1)**: the sentence waits on "no other reserved, picked-up or returned truck contract of the renter carries a claim on the same storage unit"; the declared `condition` requires "Every other truck contract … whose linked storage unit is the unit being claimed stands in cancelled or no_show status". The status enum is {reserved, picked_up, returned, closed, cancelled, no_show}: a `closed` contract linked to the same unit satisfies the sentence and fails the condition. The condition is strengthened relative to the sentence.
- No authoring-viewpoint phrasing ("in this task", "at the opening") in any `prerequisite` field.

### prerequisite_sentences

Four-point test per edge:

1. mileage <- late_cancellation (state_gate). Sentence: "The included-miles credit is not posted until no other reserved, picked-up or returned truck contract of the renter carries a claim on the same storage unit." Own result + "not … until" ✓; waited-on thing is a record-visible state in table words (status values; "claim" = `linked_rental_id`, schema meaning "Storage unit rental the free move-in truck is claimed for") ✓; no tool, id or snake_case ✓; strength vs condition: narrower than the condition on `closed` (F-1). Single write that brings the state about: among this difficulty's writes only `cancel_truck_reservation` moves a reserved contract out of {reserved, picked_up, returned} (no reservation-change tool exists in task_tools.py or share_tools.py; `no_show` is a system transition). Reader derivation: sentence -> find_truck_rentals(customer) shows another contract `reserved` with the same `linked_rental_id` -> the only rule that takes a reservation out of `reserved` is the late-cancellation policy ("A reservation in reserved status is cancelled by the renter …") -> cancellation, the renter's own act. One reading.
2. mileage <- additional_day (value_input). Sentence: "The included-miles credit is fixed only after every rental day the contract started stands charged on the contract." "only after" ✓; state = charge lines on the contract versus rental days started (actual pickup/return) ✓; no tool/id ✓; strength matches the condition. Single write: the additional-day rule ("At check-in every rental day the contract started after its first is charged as an additional rental day") — the first-day rule applies only to a contract opening at pickup. One reading.
3. waiver <- mileage (value_input). Sentence: "The rental waiver is not credited before the truck contract carries the storage-unit claim it is credited for." "not … before" ✓; state = contract's linked storage unit ✓; single write: the mileage allowance rule ("A free move-in claim is recorded on a truck contract for the renter's storage unit with the most recent move-in … and when the claim is recorded the claimed miles are credited …"); `apply_move_in_claim_miles_credit` is the only tool that sets `linked_rental_id`. One reading.
4. signing <- first_day (value_input). Sentence: "The authorization hold is fixed only after the contract's first-day rental fee stands posted on the contract." "only after" ✓; state = a base rental fee line for the first day on the contract ✓; single write: first-day rule. One reading.

- No blocked rule carries a second wording, tool name or other problem id about its dependency.
- **Depended-on rule restates the dependency (F-4)**: the first-day rule (the depended-on side of edge 4) says "The first-day rental fee of a truck contract is posted when the contract opens at its pickup, as one base rental fee line dated that day with a quantity of one, ahead of the renter's signature, so that the contract the renter signs shows it." (also in its `overwrite.replaced_by`), and its tool docstring says "shown for signature". The order fee-before-signature is thus stated on the depended-on side too. It reaches the same conclusion as the blocked sentence (no conflicting outcome), so it is recorded as an observation-level form defect, not a RED.
- Cross-problem orders stated in rules that ground no declared edge: none found. Base rules carrying order ("the first period is posted at pickup") are superseded and ground no edge.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry:

- **late_cancellation_fee / truck_evt_cancellation_no_show**: free-cancellation sentences (1-3) followed and restated; "A later cancellation posts late_cancellation_fee_usd." — superseded, declared; no-show and facility-cannot-fill sentences untouched and inherited. Unique.
- **additional_day_charge / truck_evt_pricing**: sentence 1 superseded, declared; mileage, environmental, waiver-fee, fuel, driver, ancillary and rounding sentences untouched. **/ truck_evt_late_return**: no sentence declared, but the extended rule prices late days that the base late-return clause also prices (O-1, no task consequence).
- **move_in_mileage_allowance / truck_evt_free_move_in**: the waived-charges/included-miles sentence superseded, declared; eligibility (class, unit status, window, counting, delinquency) and "Extra periods, extra miles, … stay chargeable" followed. **/ truck_agg_free_move_in_once**: "Each unit rental agreement supports one free move-in truck rental …" and "A cancelled or no-show reservation does not use the benefit" followed (the new sentence implements them, see O-2); "never combined with another discount" not touched by this policy. **/ truck_evt_breakdown_and_corrections**: "A charge already credited is not credited again" followed. **/ truck_evt_pricing**: "less any included miles" — the included miles are now the extended allowance; consistent with the declared free-move-in override.
- **move_in_rental_waiver / truck_evt_free_move_in**: same sentence superseded, declared (environmental fee stays chargeable, declared). **/ truck_agg_free_move_in_once**: "never combined with another discount" superseded, declared. Others followed.
- **first_day_rate / truck_evt_pricing**: sentence 1 superseded, declared. **/ truck_evt_driver_requirements**: nothing changed.
- **signing_authorization_hold / truck_evt_deposit_and_settlement**: hold sentence superseded, declared (hold = card deposit + posted first-day fee + factors). "A hold is placed once per contract" and settlement sentences inherited. **/ truck_evt_pricing, truck_evt_driver_requirements**: followed.
- Disguised forms: no anonymous intermediate factor that deviates from base without a declaration; no 0/1 multiplier on a base quantity; no dropped base branch. No author note calls a base output a "wrong value".

Result: no undeclared override charter-wide. PASS (observations O-1, O-2).

### factor_ladders

Per policy (effect labels as declared; "honest" = per the skill's test that a `method` tier changes the algorithm, a `parameter` tier substitutes a number):

| policy | factor | label | tiers | cross_difficulty | multi-source (every non-fall-through tier ≥2 conditions over distinct records) | label honest? |
| --- | --- | --- | --- | --- | --- | --- |
| late_cancellation_fee | cancellation_fee_basis | method | 3 (2×base_rate / 1×base_rate / flat late_cancellation_fee_usd) | – | no | yes — the fall-through switches the source quantity from a rate multiple to a flat fee |
| | cancellation_notice_share | parameter | 3 (0.5 / 0.75 / 1) | – | no | yes |
| | cancellation_peak_day | parameter | 3 (1.5 / 1.25 / 1) | – | no | yes |
| | cancellation_tenant_courtesy | parameter | 3 (0.5 / 0.75 / 1) | unit | no (tier 1 single condition) | yes |
| additional_day_charge | last_day_return_count | method | 3 (last day 0.5 / 0.75 / 1 of a day) | – | no | **no** — counted_days = (additional_days − 1) + s with s ∈ {0.5, 0.75, 1.0}; one formula, a number substituted |
| | booked_length_share | parameter | 3 (0.7 / 0.8 / 1) | – | no | yes |
| | second_day_weekday | parameter | 3 (1.2 / 1.1 / 1) | – | no | yes |
| | move_in_day_share | parameter | 3 (0.5 / 0.9 / 1) | unit | yes (unit move-in date × truck pickup/return date; unit facility × truck facility) | yes |
| move_in_mileage_allowance | claimed_unit_size_miles | parameter | 3 (100 / 60 / 50) | unit | no | yes |
| | rental_day_miles | parameter | 3 (40 / 20 / 0) | – | no | yes — but see F-3 (top tier unreachable) |
| | move_in_trip_miles | parameter | 3 (15 / 10 / 0) | unit | yes (truck pickup × unit move-in) | yes |
| | claimed_unit_class_miles | parameter | 3 (25 / 10 / 0) | unit | no | yes |
| | cross_facility_miles | parameter | 3 (25 / 15 / 0) | unit | yes (unit facility × truck facility × dates) | yes |
| | protection_multiple | method | 3 (×1.5 / ×1.25 / ×1) | protect | no | **no** — allowance × m, m ∈ {1.5, 1.25, 1.0}; one formula, a number substituted |
| move_in_rental_waiver | waiver_basis_weekday | method | 3 (÷1.1 / ÷1.2 / ÷1) | – | no | **no** — first_day_fee ÷ k, k ∈ {1.1, 1.2, 1.0} |
| | waiver_unit_size_share | parameter | 3 | unit | no | yes |
| | waiver_promotion_share | parameter | 3 | unit | no (same unit record) | yes |
| | waiver_tenancy_share | parameter | 3 | unit | no | yes |
| | waiver_facility_share | parameter | 3 | unit | yes | yes |
| | waiver_autopay_share | parameter | 3 | autopay | no | yes |
| first_day_rate | first_day_weekday_rate | parameter | 3 | – | no | yes |
| | first_day_duration_rate | method | 3 (×0.6 / ×0.8 / ×1) | – | no | **no** — day-rated fee × d, d ∈ {0.6, 0.8, 1.0} |
| | first_day_tenant_discount | parameter | 3 | unit | yes-ish (unit facility × truck facility) | yes |
| | first_day_advance_discount | parameter | 3 | – | no | yes |
| | first_day_military_discount | parameter | 3 (class pct / 0.05 / 0) | unit | no | yes — but see F-5 |
| | first_day_autopay_discount | parameter | 3 | autopay | no | yes |
| signing_authorization_hold | hold_payment_risk | parameter | 3 | unit | yes (truck card on file × unit ledger reversal) | yes |
| | hold_tenant_share | parameter | 3 | unit | yes (tenure × late-fee ledger; unit × truck facility) | yes |
| | hold_military_share | parameter | 3 | unit | no | yes |
| | hold_booking_lead_share | parameter | 3 | – | no | yes |
| | hold_mileage_estimate | method | 3 (40 mi / 80 mi / 0 mi × per_mile) | – | no | **no** — miles_tier × per_mile_usd, miles_tier ∈ {40, 80, 0} |

Counts (declared -> after the honesty test):
- late_cancellation_fee: 4 factors, 3 parameter + 1 method -> unchanged. PASS.
- additional_day_charge: 4, 3P+1M -> 4P+0M. **Below the 1-method floor.**
- move_in_mileage_allowance: 6, 5P+1M -> 6P+0M (and rental_day_miles is struck under F-3, leaving 5). **Below the 1-method floor.**
- move_in_rental_waiver: 6, 5P+1M -> 6P+0M. **Below the 1-method floor.**
- first_day_rate: 6, 5P+1M -> 6P+0M. **Below the 1-method floor.**
- signing_authorization_hold: 5, 4P+1M -> 5P+0M. **Below the 1-method floor.**
- Every ladder has exactly three pairwise-disjoint tiers, each stated in the `rule` with its condition and value/method and implemented in the `decides` binding; no tier lives only in compute.
- Every factor's fall-through equals that policy's `baseline` for the input (late-cancel: flat fee, ×1s; additional-day: whole days, ×1s; mileage: free_move_in_included_miles + 0s, ×1; waiver: posted fee, ×1s; first-day: ×1, discounts 0; hold: ×1s, no estimate). Every `baseline.rule` is a verbatim sentence of its rule and computes a definite number with no factor applied.
- Per task (blind partition): task 0 multi-source = move_in_day_share, move_in_trip_miles, cross_facility_miles, waiver_facility_share; cross_difficulty = unit/protect/autopay factors. Task 1 multi-source = hold_payment_risk, hold_tenant_share; cross_difficulty = unit/autopay factors.
- Ladder realness (conditions and outcomes a self-storage truck-rental line would hold): weekday surcharges, same-day half-day rates, tenant/advance/military/AutoPay discounts, payment-risk and tenant deposit shares, notice/peak cancellation shares, move-in-day and facility-tenant rates and unit-size/class mileage bonuses are all plausible published treatments. Exceptions: F-3 and F-5 below; weaker-but-accepted items are O-5.

### findings

- **F-1 SOURCE-POLICY RED (charter-global, check 7; no task-world consequence)** — symptom: edge `truck_ext_move_in_mileage_allowance -> truck_ext_late_cancellation_fee` declares a condition stronger than its prerequisite sentence. Root cause: the condition's "stands in cancelled or no_show status" omits `closed`, which the sentence ("no other reserved, picked-up or returned truck contract … carries a claim") admits. Evidence: extended charter lines 1364-1369; status enum (charter line 13; db_schema truck_rentals.status). Demonstrated consequence: in the situation "another contract of the renter, status `closed`, `linked_rental_id` = the claimed unit, no free-move-in credit", the sentence says the included-miles credit may be posted and the condition says the prerequisite is unmet. Neither task world contains a closed contract linked to a claimed unit, so no scored value moves. Bears on: task 0 (the edge is in its tree).
- **F-2 SOURCE-FACTOR RED (charter-global structure; mislabelled `method` factors)** — symptom: five of the six policies' only `method` factor substitutes a number into one formula. Root cause/evidence: `last_day_return_count` (compute line 1205-1206), `protection_multiple` (1410-1411), `waiver_basis_weekday` (1623), `first_day_duration_rate` (1836, 1848), `hold_mileage_estimate` (2052) — formulas shown in the table above. Demonstrated consequence: each of additional_day_charge, move_in_mileage_allowance, move_in_rental_waiver, first_day_rate and signing_authorization_hold has 0 honest `method` factors, below the required 1. Bears on: task 0 (additional-day, mileage, waiver computations) and task 1 (first-day, hold computations).
- **F-3 SOURCE-FACTOR RED (charter-global ladder realness)** — `rental_day_miles` ("three or more lines add three_day_bonus_miles, two lines add two_day_bonus_miles, and a single line adds no miles"): under the charter's own posting rules a contract carries one first-day line ("as one base rental fee line … with a quantity of one") and one additional-day line ("posted as one base rental fee line dated the actual return date with the additional days as its quantity"); base per-period posting is superseded, and late days post `extra_period_fee`/`late_return_fee` charge types. A contract that ran 2 days and one that ran 6 both carry 2 lines; the top tier is reachable by no contract posted under this charter, and the condition (invoice line count) is not what a rental business weighs for a mileage bonus (rental days). The factor still separates 1 line from 2 lines, so it bears weight in task 0 (see 0.md), but its ladder has two live tiers. Bears on: task 0.
- **F-4 Observation (check 6 form)** — the depended-on first-day rule and its tool docstring restate the fee-before-signature order ("ahead of the renter's signature, so that the contract the renter signs shows it"; "shown for signature"). Same conclusion as the blocked sentence; no conflicting outcome. Bears on: task 1 (the hop is also readable from the depended-on side).
- **F-5 SOURCE-FACTOR RED (charter-global ladder realness; no task-world consequence)** — `first_day_military_discount` tier 1 takes "that unit class's military_discount_pct"; `Bluegate Wine & Collectibles Vault` has `military_discount_pct: 0.0` (products/unit.yaml line 445), so for a renter whose active military agreement is a vault, tier 1 selects 0.0 — the fall-through's value — and pays more than a former-military renter (0.05). Task 1's agreement is a Drive-Up Standard (0.10), so its scored value is unaffected. Bears on: task 1 (ladder only).
- **F-6 (per-task demonstration in 0.md)** — the late-cancellation courtesy tier "billed a storage administrative fee within the last calendar month" admits a second reading (the preceding calendar month) against compute's rolling `within_months=1`. Demonstrated against task 0's world in 0.md.
- **O-1** additional-day vs base late-return double pricing of a late day (no task returns late).
- **O-2** base-internal tension between `truck_msr_free_move_in_used` (requires a credit row) and the `truck_agg_free_move_in_once` rule/dedup_contract (a linked reserved contract occupies the benefit). The extended sentence follows the rule.
- **O-3** subjects `truck_pickup`, `truck_return`, `truck_deposit_hold` outside the blueprint claim's event_types list (no cross-difficulty collision).
- **O-4** booked-length ladder of the additional-day rule silent on a same-day (0-day) booking; compute's fall-through decides it.
- **O-5** accepted but weak realness: the rental waiver shrinks with storage tenure (long tenants get 0.85 of a move-in benefit); an *inactive* AutoPay authorization reduces the waiver more (0.8) than none ever given (0.9); the hold's mileage estimate applies to same-day bookings only; for the Pickup Truck and Cargo Van the two-day cancellation basis (one base rate, 19.95/24.95) is below the one-day flat fee (25.00), so a longer booking can cost less to cancel.

## closing_checklist

Written after both reveals (2026-10-10T19:5xZ). The charter-global section above is unchanged since 19:44:43Z (pre-reveal); its header freeze time "19:45Z" was an estimate — the file's mtime before any reveal is 19:44:43Z and the first reveal ran at 19:47:05Z.

- Per-task files: `0.md`, `1.md` correspond one-to-one with `tasks/0.json`, `tasks/1.json`; this is revision 1 (no older revision exists). Each has a frozen section and a comparison. **Not every comparison carries a PASS** (see below).
- Coverage and scopes: revealed `charter_scope` — task 0 {late_cancellation_fee, additional_day_charge, move_in_mileage_allowance, move_in_rental_waiver}, task 1 {first_day_rate, signing_authorization_hold} — equals the blind partition; pairwise disjoint over the whole trees, jointly covering all six extended policies and all six task tools. uuid8s independent (`### action_binding_and_uuids`). ✓
- Problem trees: task 0 — 3 prerequisite problems, 2 value_input edges (≥ 2), owner=user cancellation; task 1 — 1 prerequisite problem, 1 value_input edge, owner=user signing; both acyclic; the difficulty graph is two disjoint DAGs. ✓ (F-1 condition strengthening on edge mileage -> late_cancellation recorded, no task-world consequence.)
- Computations and factors: every computation declares a self-sufficient baseline and 4-6 factors; every factor bears weight on its task's world; every whole baseline gives a definite number ≠ gold (25.00 / 29.95 / 49.50 / 32.95; 24.95 / 210.78); multi-source and cross-difficulty factors present in both tasks. **Fails**: five of six computations have 0 honest `method` factors (F-2); `rental_day_miles` top tier unreachable (F-3); `first_day_military_discount` tier 1 collapses onto the fall-through for the vault class (F-5); no tier-moving near-miss in task 0's cancellation and additional-day computations (T0-F4) and in task 1's first-day computation (T1-F2).
- Unique solution: task 1 PASS; task 0 SOURCE-TASK RED (plausible) on "within the last calendar month" (T0-F2: 16.85 vs 25.27).
- Gate re-run on the final form: not performed — the difficulty does not pass this audit, so the closing re-run has no final form to certify; the coordinator's gate snapshot (all green, traceability deferred) is the latest machine state.

**Difficulty verdict: does not pass the source-layer audit.**
- task 0: policy PASS (F-1 cited, no consequence) · tree PASS · **SOURCE-FACTOR RED** (F-2, F-3, T0-F4) · **SOURCE-TASK RED (plausible)** (T0-F2).
- task 1: policy PASS (F-4, F-5 cited) · tree PASS · **SOURCE-FACTOR RED** (F-2, T1-F2) · unique solution PASS.

## revision_2

### charter_global_frozen (revision 2)

- Written before any round-2 GT field was read. Auditor: erl-task-policy-audit subagent (same auditor as revision 1).
- Shared inputs moved, so every charter-global section is re-derived in full: `truck.extended.yaml` sha256 `e57ab7a17ff2f9a0b7d192ce2859472848f7ef4289c61bc08bf4e230d68f60a7` (was `134bb967…`), `task_tools.py` sha256 `392e1d565b222647b96291561e1c1f2c4c7fd446f53443e39fa1c794c7726ccc` (was `b179847a…`). New masked views: `0.view.json` `10b53cd1…b330`, `1.view.json` `ce694b7f…7d`. All hashes match the coordinator brief.
- Base copy (lines 1-1006) is byte-identical to the round-1 base copy saved at `/tmp/run_0051/audit_moving_truck_rentals/base_copy.yaml` and to `blueprint/products/truck.yaml`.
- contamination_disclosure: round-1 GT for both tasks (their scored values, factor sensitivities and design rationales) was read during revision 1. The round-2 task JSONs have not been opened. The round-2 derivation below rests on the reworked charter and the new views; where a number repeats the round-1 GT, that is because the inputs it reads are unchanged.
- Entry conditions: the coordinator re-ran the gates after the rework and supplied the output (all OK; traceability deferred; validate_scenario shows only the pre-render missing-document errors). Masked views and hashes were supplied. Met.
- Scratch: `charter_scan.py` (re-run on the new charter) and `blind_calc_r2.py`.

### policy_conflict_scan (revision 2)

- Base pricing sentence 1 is still superseded by both first-day and additional-day. The additional-day rule now caps additional days "up to the rental days booked" and sends "rental days started beyond the rental days booked … [to] the late-return rules, not additional days". The two clauses no longer price the same late day, so **O-1 is closed**.
- The two half-overrides of the base free-move-in sentence (miles / fee) are unchanged and still complementary.
- Free-move-in once-per-unit: O-2 is unchanged (left by the reworker with reasons); the extended sentence still follows the base rule and dedup reading.
- **New (R2-F1): the rental-waiver rule contradicts itself on discounted first-day fees.** The rule says "On a contract whose first-day rental fee was charged with a discount, the rental waiver is figured on the fee as posted". The reworked basis ladder says "a longer booking whose scheduled pickup date is a Friday, Saturday or Sunday takes the class base_rate_usd as its waiver basis … ; any other booking takes the first-day rental fee as posted". The part-day tier is similar ("part_day_share of the class base_rate_usd"). Take a two-day 10 ft booking picked up on a Friday whose first-day fee carried a discount, e.g. 29.95 × 1.1 × (1 − 0.15) = 28.00:
  - the first sentence figures the waiver on 28.00;
  - the basis ladder figures it on 29.95.

  With unit shares 0.9 (and the others 1.0), that gives two waivers: 25.20 and 26.96. Round 1's basis divided the posted fee by the surcharge share, so it stayed "figured on the fee as posted"; the rework introduced the conflict.
- The courtesy tier of the late-cancellation fee is now facility-scoped ("an active storage agreement at the reservation's own facility whose move-in date is less than one whole calendar month before the cancellation date"). It no longer reads admin fees, and no other policy reads that tier.
- Claimed scope vs subjects: O-3 unchanged.

### rule_compute_equivalence (revision 2)

`charter_scan.py`: every binding has a basis. Every basis quotation, baseline rule, `replaced_by` and `policy_source` is verbatim in its own rule. Factor bindings exist and are disjoint per policy, and no `decides` is `result`. The manual sweep of the reworked parts:
- **late_cancellation_fee.**
  - The two-day basis `MX(base_rate, late_cancellation_fee_usd)` matches "the larger of one class base_rate_usd and the flat late_cancellation_fee_usd".
  - Courtesy: `CFIELD(unit, move_in_date, status=active, facility_code=F('facility_code'))` with `MONTHS(·, NOW) < 1` matches "an active storage agreement at the reservation's own facility whose move-in date is less than one whole calendar month before the cancellation date".
  - Rent: `XCOUNT(… within_months=12 …)` matches "billed storage rent less than twelve whole calendar months before the cancellation date". The phrase now names a counting convention ("whole calendar months … before"), so the round-1 second reading is gone.
- **additional_day_charge.**
  - `booked_periods` uses the same started-day count on scheduled times.
  - `additional_days = MX(0, MN(days_started, MX(1, booked_periods)) − 1)` matches "after its first, up to the rental days booked".
  - The last-day share is gated on `days_started <= booked_periods` ("came back within the rental days booked").
  - `day_rate` gives MN(fee, base) for 3+ booked days / the posted fee for 2 / base otherwise, as stated.
  - The move-in share matches its rule: same facility 0.5, other facility 0.75, else 1.
  - The old booked-length ladder is gone, so **O-4 is closed**.
- **move_in_mileage_allowance.**
  - Rental days charged = `SUM(quantity)` of base rental fee lines, matching "the quantities of its base rental fee lines added together".
  - Trip miles: `early_pickup_miles * pickup_lead_days` for leads of 1-3, matching "for each of those days".
- **move_in_rental_waiver.** The new basis ladder (part-day / Fri-Sun longer booking / other) is implemented as stated. The conflict with the discount sentence is R2-F1.
- **first_day_rate.**
  - The rating day is the reservation weekday if lead ≥ 14, the next day if the pickup time is ≥ 17:00, else the pickup weekday — as stated.
  - Military = `MX(class pct, 0.05)` for an active agreement.
  - AutoPay reads `status='active'` only, matching "an authorization that is cancelled, suspended or replaced does not count".
  - The advance discount is removed from both rule and compute.
- **signing_authorization_hold.** The rental estimate is 40 mi × per_mile for a same-day booking, (booked_days − 1) × base_rate for 2 or more days, and 0 for a one-day booking — as stated.

Result: PASS (the R2-F1 conflict is between two rule sentences and is not a rule/compute gap).

### action_binding_and_uuids (revision 2)

- The six tools, owners and uuid8s are unchanged (`ee0618b8`, `add5e32c`, `24951572`, `7c9a948d`, `f35b099c`, `074f2414`). Each (tool, computes) has one policy. Bodies still write without checking anything.
- The `post_first_day_rental_fee_f35b099c` docstring now reads "Post the first-day rental fee on a truck rental contract … The renter sees the first-day fee among the charges on the contract". The "opening for pickup" / "shown for signature" wording is gone.

### prerequisite_graph (revision 2)

- Edges, kinds, forms and resolved_by are unchanged; the graph is acyclic. The value_input gate of mileage -> additional_day is renamed `rental_days_charged`, which is a real binding.
- **F-1 is closed.** The condition now reads "No truck contract of the renter other than the credited one stands in reserved, picked_up or returned status with the claimed storage unit as its linked storage unit". That is the same scope as the sentence: a `closed` contract is admitted by both.

### prerequisite_sentences (revision 2)

- All four sentences are verbatim and unchanged, and pass the four-point test. For each state-form edge there is still a single write that brings the state about.
- **F-4 is closed.** The first-day rule and its `replaced_by` now end "… as one base rental fee line dated that day with a quantity of one." No mention of signature remains in the depended-on rule or docstring.
- No rule states an undeclared cross-problem order.

### override_declarations (revision 2)

- Each declared `superseded_clause` is verbatim in its base policy. Sentence-by-sentence findings match revision 1.
- The additional-day rule now defers explicitly to `truck_evt_late_return` for days beyond the booking, which is consistent with that base policy.
- The waiver's override of "never combined with another discount" now conflicts internally with its new basis ladder (R2-F1, above).
- No undeclared override.

### factor_ladders (revision 2)

| policy | factors (label) | method honest? | count |
| --- | --- | --- | --- |
| late_cancellation_fee | fee_basis (M: 2×base / max(base, flat) / flat), notice (P), peak (P), courtesy (P, unit; multi-source: unit status + facility vs reservation facility + move-in date) | yes — the source quantity switches between a base-rate multiple and the flat fee | 4 = 3P + 1M ✓ |
| additional_day_charge | last_day_return_share (P, relabelled), additional_day_rate_source (M: min(posted fee, base) / posted fee / class base), second_day_weekday (P), move_in_day_share (P, unit, multi-source) | yes — the price source switches between the contract ledger and the tariff | 4 = 3P + 1M ✓ |
| move_in_mileage_allowance | size (P), rental_day_miles (P, now summed quantities), move_in_trip_miles (M: flat 15 / 10 × lead days / none), class (P), cross_facility (P, multi-source), protection_multiple (P, relabelled) | yes — flat amount vs per-day scaling | 6 = 5P + 1M ✓ |
| move_in_rental_waiver | basis_source (M: 0.5 × base / base / posted fee), size, promotion, tenancy, facility (multi-source), autopay (P) | yes — tariff vs posted fee | 6 = 5P + 1M ✓ |
| first_day_rate | rating_day (M: reservation-date weekday / next-day weekday / pickup weekday), weekday_rate (P), duration_rate (P, relabelled), tenant (P, unit), military (P, unit), autopay (P, autopay) | yes as a method — it selects which date sets the weekday. **Realness: see R2-F2** | 6 = 5P + 1M |
| signing_authorization_hold | payment_risk (P, multi-source), tenant (P), military (P), lead (P), rental_estimate (M: mileage-based / day-based / none) | yes | 5 = 4P + 1M ✓ |

- **F-2 is closed**: each policy now has one honest method factor.
- **F-3 is closed**: the rental-day miles read summed line quantities, so a 3-day contract (quantities 1 + 2) reaches the top tier.
- **F-5 is closed as demonstrated.** An active military agreement now takes max(class pct, 0.05), so the vault (0.0) no longer falls to the fall-through value and no longer pays more than a former-military renter. Residual observation R2-O2: for the vault class, tier 1 (0.05) equals tier 2's value. That is a coherent "at least the former-military rate" floor and no task world uses a vault.
- Every ladder has three disjoint tiers, stated in full in its rule and implemented in compute. Every fall-through equals its policy's baseline. Every baseline rule is self-sufficient.
- **O-5 is partly closed.**
  - The two-day cancellation basis is now max(base, flat), so a longer booking no longer costs less to cancel.
  - The hold estimate now covers multi-day bookings.
  - Unchanged and still observations: the waiver's tenancy share falls with tenure, and an inactive AutoPay (0.8) reduces the waiver more than no AutoPay ever given (0.9).
- **New (R2-F2): first_day_rating_day tier 1 is unreal.** "a reservation made advance_lock_days or more calendar days before its scheduled pickup date is rated on the weekday of its reservation date, the rate being locked when it was booked". A weekday surcharge prices demand on the day the vehicle is out. Locking the rate at booking would lock the rate quoted for the rental day, not apply the weekday of the day the booking happened to be made. No rental business would publish this: a Saturday rental booked on a Thursday is charged the weekday rate, and a Tuesday rental booked on a Saturday is charged the weekend rate. Tiers 2 (an evening pickup rated on the next day) and 3 are coherent. Task 1 sits on tier 1 (see 1.md).
- **New (R2-O1): additional-day compounding.** Pricing two-day bookings at the posted first-day fee and then applying the second-day weekday multiple compounds surcharges. A Friday pickup prices day 2 (Saturday) at 1.1 × 1.2 = 1.32 × base; a Saturday pickup prices day 2 (Sunday) at 1.44 × base, against the 1.2 × base the first-day rule gives a weekend day. The waiver rule itself works to keep "the pickup-day surcharge … payable", which shows the charter knows the posted fee carries the pickup-day surcharge. This is a defensible "contracted day rate × day surcharge" scheme, so it is recorded as an observation.

### findings (revision 2)

| round-1 item | status | evidence |
| --- | --- | --- |
| F-1 (condition stronger than the sentence on `closed`) | closed | condition text (charter lines 1376-1378) |
| F-2 (mislabelled methods) | closed | table above |
| F-3 (rental-day miles top tier unreachable) | closed | rule lines 1349-1352, compute line 1409 |
| F-4 (dependency restated on the depended-on side) | closed | first-day rule line 1806-1807; docstring line 175-179 |
| F-5 (vault military collapse) | closed as demonstrated; residual R2-O2 | compute line 1853 |
| F-6 / T0-F2 ("last calendar month") | closed — the tier now reads a dated facility agreement and states "whole calendar months … before" | rule lines 1046-1050 |
| O-1 (late-day double pricing) | closed | rule lines 1173-1179 |
| O-2, O-3 | unchanged; accepted as observations | — |
| O-4 (same-day booking silent) | closed (ladder removed) | — |
| O-5 | partly closed (see above) | — |

New findings:
- **R2-F1 SOURCE-POLICY RED (charter-global)** — the waiver's discount sentence vs its tariff-based basis tiers. Demonstrated above with a hypothetical discounted Friday contract. Bears on task 0's waiver policy; task 0's first-day fee 32.95 = 29.95 × 1.1 carries no discount, so no scored value moves there.
- **R2-F2 SOURCE-FACTOR RED (charter-global ladder realness)** — the first-day rating-day tier 1. Bears on task 1, whose tier it is.
- **R2-O1** (additional-day compounding) and **R2-O2** (vault military floor) are observations.

### closing_checklist (revision 2)

Written after the round-2 reveals (21:12:20Z). The charter-global revision-2 section above was written before them.

- **Files.** `0.md` and `1.md` each now carry `## revision_2` (frozen derivation, then comparison). Revision-1 text is untouched.
- **Scopes.** `charter_scope` again equals the blind partition: task 0 holds four policies and task 1 holds two. They are disjoint and cover the charter. The uuid8s are unchanged and independent.
- **Trees.**
  - Task 0: 3 prerequisites, 2 value_input edges, a user-run cancellation.
  - Task 1: 1 prerequisite, 1 value_input edge, a user-run signing.
  - Both are acyclic, and every edge bears weight.
- **Factors.**
  - Every computation has 4-6 factors with exactly 1 honest method factor.
  - Multi-source and cross-difficulty factors are present in both tasks.
  - Every factor bears weight against an honest baseline.
  - Every whole baseline differs from gold: 25.00 vs 25.27, 29.95 vs 14.83, 49.50 vs 185.13, 32.95 vs 12.37, 24.95 vs 11.53, 211.53 vs 155.13.
  - Every computation has a near-miss.
  - **Open: R2-F2**, the first-day rating-day tier 1 is unreal, and task 1 sits on it.
- **Policy.** **Open: R2-F1**, the waiver's discount sentence conflicts with its tariff-based basis tiers. It is charter-global and moves no score in task 0's world.
- **Gate re-run.** Not performed by this audit. The coordinator's post-rework gate snapshot (all OK, traceability deferred) is the latest machine state.

**Difficulty verdict, revision 2: does not yet pass.**

- Every round-1 RED is genuinely closed, and nothing regressed.
- **Task 0:** PASS on all four relationships in its world.
- **Task 1:** SOURCE-FACTOR RED (R2-F2).
- **Charter-global:** SOURCE-POLICY RED R2-F1 remains open.
- **Observations:** R2-O1, R2-O2, O-2, O-3, and the remaining part of O-5.

## revision_3

### charter_global_frozen (revision 3)

- Written before any round-3 GT field was read.
- `truck.extended.yaml` sha256 is now `71b9090760d9d5f9e445c0a4aea4731c65064821648b718f6c31f6519d305a83` (changed), so the charter-global section is re-derived. A copy is kept at `/tmp/run_0051/audit_moving_truck_rentals/ext_r3.yaml` for future diffs.
- `task_tools.py` is `392e1d56…cccc`, unchanged since revision 2. The tool conclusions are carried forward on that hash: same six tools, owners, uuid8s, bodies and docstrings.
- Views: `0.view.json` `10b53cd1…b330` (unchanged) and `1.view.json` `ec1af546…0ffc` (reseeded). Both match the brief.
- The base copy is still byte-identical.
- contamination_disclosure: round-1 and round-2 GT of both tasks were read in earlier revisions. Round-3 task JSONs are unopened.
- Method note: no revision-2 copy of the charter was kept. The unchanged status of the first three extended policies (late cancellation, additional day, mileage) therefore rests on two checks: their line spans are identical (1011-1149, 1150-1308, 1309-1543), and each reworked string from revision 2 occurs verbatim. The waiver, first-day and hold policies were re-read in full.
- Entry conditions: the coordinator's gate snapshot is all OK, traceability is deferred, and validate_scenario shows only pre-render errors. Met.

### re-derived sections (revision 3)

- **policy_conflict_scan.** No new overlapping or contradictory clause.
  - Waiver: the override replacement now reads "The rental waiver is never figured on more than the first-day rental fee as posted, so a discount already given on that fee and the rental waiver together never exceed it".
  - Every waiver basis tier is now capped by the posted fee: the part-day tier takes "the lower of the first-day rental fee as posted and part_day_share of the class base_rate_usd", and the Friday–Sunday tier takes "the lower of the first-day rental fee as posted and the class base_rate_usd". In compute these are `MN(first_day_fee, …)` (line 1633).
  - The revision-2 example (discounted Friday fee 28.00) now gives a basis of min(28.00, 29.95) = 28.00 under both sentences. **R2-F1 is closed.**
- **rule_compute_equivalence.** `charter_scan.py` is clean: every binding has a basis, every quotation is verbatim, factor bindings are disjoint, and no `decides` is `result`.
  - First-day: the rating-day ladder is implemented as stated. For a booking of 3 or more days, compute checks whether the booked days (pickup date onward, `booked_days` days) take in a Saturday/Sunday or a Friday; otherwise a pickup at 17:00 or later moves to the next day; otherwise the pickup date is used. The duration rate is removed from both rule and compute, and the advance discount is back in both.
  - The waiver's inactive AutoPay share changed to 0.95 in both the param and the ladder.
  - PASS.
- **action_binding_and_uuids.** Carried forward on the unchanged tool hash. PASS.
- **prerequisite_graph / prerequisite_sentences.** Edges, sentences, conditions and resolved_by are unchanged. The first-day rule still says nothing about signature. PASS.
- **override_declarations.** Every superseded clause is verbatim in its base policy. The waiver's second override now agrees with its basis tiers. No undeclared override. PASS.
- **factor_ladders.**

  | policy | count | method factor | honest? |
  | --- | --- | --- | --- |
  | late cancellation | 4 = 3P + 1M | — | yes |
  | additional day | 4 = 3P + 1M | — | yes |
  | mileage | 6 = 5P + 1M | — | yes |
  | waiver | 6 = 5P + 1M | basis: capped tariff / capped part-day tariff / posted fee | yes |
  | first-day | 6 = 5P + 1M | rating day (see below) | yes |
  | hold | 5 = 4P + 1M | — | yes |

  - **First-day rating day.** The tiers are: busiest booked day for bookings of 3 or more days; the next day for an evening pickup; the pickup date otherwise. This is a real pricing practice (a multi-day hire priced at its peak day, an evening hire priced on the day it is used), so **R2-F2 is closed**.
  - Every ladder has three disjoint tiers, stated in full in its rule. Fall-through equals baseline everywhere.
  - **O-5 AutoPay sub-item closed:** an inactive authorization (0.95) now reduces the waiver less than none ever given (0.9).
  - Kept, as observations with the reworker's reasons: R2-O1 (additional-day surcharge compounding), R2-O2 (vault military floor), O-5 tenure sub-item. The waiver rule now states its rationale: "The free move-in truck is an acquisition benefit for new storage customers".

### findings (revision 3)

| item | status |
| --- | --- |
| R2-F1 | closed |
| R2-F2 | closed |
| O-5 AutoPay sub-item | closed |
| R2-O1, R2-O2, O-5 tenure, O-2, O-3 | observations, unchanged |

No new charter-global defect found.

### closing_checklist (revision 3)

Written after the round-3 reveals (21:42:21Z).

- **Files.** `0.md` and `1.md` each carry `## revision_3`: frozen derivation first, then comparison, and both comparisons PASS. Earlier revisions are untouched.
- **Scopes.** `charter_scope` matches the blind partition (task 0: four policies; task 1: two). They are disjoint and cover all six policies and six tools. The uuid8s are independent and unchanged.
- **Trees.**
  - Task 0: 3 prerequisites, 2 value_input edges, a user cancellation.
  - Task 1: 1 prerequisite, 1 value_input edge, a user signing.
  - Both are acyclic, the difficulty graph is a DAG, and every edge bears weight.
- **Factors.**
  - Every computation has 4-6 factors with exactly 1 honest method factor.
  - Multi-source and cross-difficulty factors are present in each task, and their rows are seeded.
  - Every factor bears weight against an honest baseline.
  - Every whole baseline is definite and differs from gold: 25.00 / 29.95 / 49.50 / 32.95 against 25.27 / 14.83 / 185.13 / 12.37 in task 0; 24.95 / 217.96 against 17.96 / 175.86 in task 1.
  - Every computation has a genuine near-miss.
- **Policy.** No open SOURCE-POLICY finding.
- **Gate re-run.** Not run by this audit. The coordinator's round-3 snapshot (all OK, traceability deferred until the KB is rendered) is the final-form machine state.

**Difficulty verdict, revision 3: PASSES the source-layer audit.** All findings from rounds 1 and 2 are closed.

Open observations, none of them grounds for rework:
- R2-O1: additional-day surcharges compound;
- R2-O2: vault military floor;
- O-5 tenure sub-item;
- O-2: base-measure tension;
- O-3: subjects outside the claimed event types.

## revision_4

### charter_global (revision 4) — carried forward by hash

- Neither shared input has moved since revision 3:
  - `truck.extended.yaml` sha256 is `71b9090760d9d5f9e445c0a4aea4731c65064821648b718f6c31f6519d305a83`, byte-identical to the revision-3 copy `/tmp/run_0051/audit_moving_truck_rentals/ext_r3.yaml` (`cmp` clean);
  - `task_tools.py` sha256 is `392e1d565b222647b96291561e1c1f2c4c7fd446f53443e39fa1c794c7726ccc`.
- On those two hashes, every revision-3 charter-global section is carried forward by reference, unre-derived: conflict scan, rule/compute equivalence, action binding and uuids, prerequisite graph and sentences, override declarations, factor ladders. No SOURCE-POLICY or SOURCE-FACTOR finding is open at the charter level.
- Views: `0.view.json` `77ef4542…a42a` (changed; task 0 world moved) and `1.view.json` `ec1af546…0ffc` (unchanged). Both match the brief.
- contamination_disclosure: GT of rounds 1-3 was read earlier. Round-4 task JSONs were unopened when this was written.
- The coordinator's gate snapshot is all OK, including TRACEABILITY OK, and validate_scenario is VALID.
- **Rounding-tie claim (from the KB-doc audit) is closed in the scored solution; see 0.md.** The scored additional-day charge is 22.24125 exactly, which is not a half-cent tie.
- **New observation R4-O1:** the source states no tie-breaking rule for amounts that land exactly on a half cent. Two what-if figures in task 0's factor sensitivity land on one; they are not scored values.

### closing_checklist (revision 4)

Written after the round-4 reveal (22:53:46Z).

- **Files.** `0.md` and `1.md` carry `## revision_4`. Task 0 was re-derived and frozen before its reveal; task 1 was carried forward on its unchanged view hash and checked against its GT. Both PASS. Earlier revisions are untouched.
- **Scopes and tools.** Scopes are unchanged and disjoint, covering all six policies and six tools. uuid8s are unchanged.
- **Trees.** Unchanged and acyclic, every edge bears weight, and each tree has an owner=user write.
- **Factors.** Every factor bears weight, labels are honest, and every computation has a near-miss. Every whole baseline differs from gold: in task 0, 25.00 / 29.95 / 49.50 / 32.95 against 25.27 / **22.24** / 185.13 / 12.37; in task 1, 24.95 / 217.96 against 17.96 / 175.86.
- **Rounding.** No scored value in either task sits on a half-cent tie.
- **Gate re-run.** Not run by this audit. The coordinator's round-4 snapshot is all OK, including TRACEABILITY OK, and validate_scenario is VALID.

**Difficulty verdict, revision 4: PASSES the source-layer audit.**

Open observations, none of them grounds for rework:
- R4-O1: no tie rule in the source; only non-scored what-if figures land on a tie;
- R2-O1: additional-day surcharge compounding;
- R2-O2: vault military floor;
- O-5 tenure sub-item;
- O-2: base-measure tension;
- O-3: subjects outside the claimed event types.
