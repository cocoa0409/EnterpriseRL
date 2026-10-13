# Policy-task audit — reservation_cancellations_and_no_shows / charter-global

## charter_global_frozen

- Freeze time: 2026-10-05T16:20Z (written before any task's GT was revealed; nothing in this section is derived from a revealed GT field).
- Auditor: erl-task-policy-audit subagent (independent of the instantiating author; no answer supplied by the brief).
- Frozen inputs (sha256, re-computed by the auditor and equal to /tmp/env0036_views/reservation_cancellations_and_no_shows/HASHES.txt):
  - `tasks/reservation_cancellations_and_no_shows/booking.extended.yaml` a8e39ee2ec5498ca4b9ba6078cbf49829f566ffcc27b51098c1458bf5a97d0fe
  - `tasks/reservation_cancellations_and_no_shows/task_tools.py` a3ea0abfb0e01af60eb106be7d8f6ae86e5d5014e273f7354e7a9c1f57a86b2b
- Read for this section: blueprint.yaml, db_schema.json, share_tools.py, blueprint/products/booking.yaml (base), the extended charter, task_tools.py, erlbench DSL semantics (skills/erl-task-instantiate/scripts/check_compute.py: `DAYS`, `MONTHS`, `_within`, `CFIELD`, `XCOUNT`, `LATEST`).
- Masked / not read: every task's `evaluation_criteria`, `computations`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `charter_scope`, `required_documents`, `db_closure*`; the difficulty `worklog.md`; any earlier audit; every other scenario and every sibling difficulty directory.
- Entry conditions (Step 0): gate snapshot supplied at /tmp/env0036_views/reservation_cancellations_and_no_shows/GATES.txt with commands and output lines; all seven gates print OK (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE). Masked views and hashes supplied. Input complete. `check_traceability` deferred to render stage (not an input of this audit).

### policy_conflict_scan

Base copy: lines 1-1609 of the extended charter are byte-identical to `blueprint/products/booking.yaml` (diff shows only the trailing blank line). Six extended policies:

| policy | subject | computes | target_tool | owner | prerequisite |
| --- | --- | --- | --- | --- | --- |
| booking_ext_capacity_room_move | booking_reservation_modify | nightly_rate | move_reservation_room_563d533b | agent | [] |
| booking_ext_extra_person_reprice | booking_reservation_modify | nightly_rate | reprice_extra_persons_22837316 | agent | capacity_room_move (value_input, state) |
| booking_ext_deposit_topup | booking_deposit_collect | amount | pay_deposit_topup_8cd35ccc | user | extra_person_reprice (value_input, action); penalty_excess_reversal (state_gate, action) |
| booking_ext_penalty_excess_reversal | booking_penalty_reversal | amount | reverse_penalty_excess_975f0de4 | agent | [] |
| booking_ext_no_show_charge | booking_no_show_charge | amount | post_no_show_charge_68d6e4c0 | agent | [] |
| booking_ext_deposit_refund | booking_deposit_refund | amount | request_deposit_refund_05a65982 | user | no_show_charge (value_input, state) |

Overlaps found:
- capacity_room_move and extra_person_reprice both write `nightly_rate` under `booking_reservation_modify`; their triggers differ (adults above room capacity vs. adults above included_adults) and the second is gated on the first, so they compose rather than compete. Each tool is distinct.
- deposit_topup and base booking_evt_advance_payment both govern `booking_deposit_collect`; the conflict (single collection) is declared (see override_declarations).
- penalty_excess_reversal and base booking_evt_penalty_reversal both govern `booking_penalty_reversal` amount under `penalty_basis_misapplied`; the base clause is NOT named in `overwrite` (finding F1).
- no_show_charge and base booking_no_show both govern the no-show charge amount; declared.
- deposit_refund and base booking_evt_deposit_settlement both govern the refund after a no-show; declared (two clauses).
- Cross-category reads: loyalty (`variant_name`, `elite_night_credits`, `cobrand_card`, `loyalty_transactions` night credits) and club (`variant_name`, `status`, `family_members`) — all read-only, all declared in each policy's `cross_category`.
- Scope exclusivity (from the worlds' shape only; verified against `charter_scope` after the reveal in each task file): task 0's world exercises a resort reservation with raised adults + a late-cancelled sibling reservation (move, reprice, reversal, top-up); task 1's world a no-show resort reservation with several deposits (no-show charge, refund). Together the six policies are covered with no overlap.

### rule_compute_equivalence

Swept every compute binding against `compute_basis` and back against every rule sentence.

- capacity_room_move: all bindings have a verbatim basis, except two invented conventions:
  - `gross_diff: MX(new_diff - old_diff, 0)` — the rule says "The move supplement is the published differential of the new room type less that of the room type it leaves" with no floor; the only "never below zero" in the rule applies after the card credit. Finding F3.
  - `new_diff` falls to `move_diff_one_bedroom_suite` for any adults above 4, including adults above 6, where the rule ("the lowest-priced room type that sleeps them") yields no room type. Observation (no task has more than 6 adults).
- extra_person_reprice: equivalent, except `stay_credits` (finding F2).
- deposit_topup: equivalent. `inputs.history` lists only collect/refund sums though `held` also subtracts forfeit and transfer (metadata observation).
- penalty_excess_reversal: equivalent; "package plan" is implemented as `P('breakfast_included')`, which in this charter selects exactly the Bed & Breakfast Package Rate (the only plan with a package supplement), so equivalent.
- no_show_charge: equivalent, except `stay_credits` (finding F2). `change_lead` falls back to booked_date when no deposit exists; the rule is silent but that tier also requires more than one payment, so the fallback never decides a tier.
- deposit_refund: equivalent. `inputs.history` omits the refund/forfeit/transfer sums `held` reads (metadata observation).
- Every factor ladder: each `factors[].ladder` tier is a rule sentence and a branch of its `decides` binding; no binding branch is missing from the rule. Checked for all 25 factors.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy: (move_reservation_room_563d533b, nightly_rate), (reprice_extra_persons_22837316, nightly_rate), (pay_deposit_topup_8cd35ccc, amount), (reverse_penalty_excess_975f0de4, amount), (post_no_show_charge_68d6e4c0, amount), (request_deposit_refund_05a65982, amount).
- share_tools.py holds only finders, `verify_customer_identity` and `transfer_to_human_agent`; no shared write can change `room_type`, `nightly_rate` or post a booking_charges row, so each task write has exactly one tool.
- Tool bodies: every tool performs one `ctx.update`/`ctx.create` with caller values; none reads a status, a prerequisite or a policy quantity, none refuses or errs (task_tools.py lines 37-40, 62-64, 88-98, 125-137, 174-185, 212-223). `reverse_penalty_excess` copies `settlement_source` from the original row and hard-codes `reversal_reason="penalty_basis_misapplied"`; this is recording, not judging.
- Docstrings: none names another tool or a sequence position. `reprice_extra_persons` opens "Record the nightly room rate ... once the extra-person charge for its registered adults has been priced in" — "once" refers to its own value, not to another write (observation only).
- uuid8s 563d533b, 22837316, 8cd35ccc, 975f0de4, 68d6e4c0, 05a65982: no shared prefix, no shared tail, no sequence or adjacency pattern; no reuse.

### prerequisite_graph

- `prerequisite` present on all six policies (`[]` on move, reversal, no_show).
- Edges: extra_person -> capacity_move; topup -> extra_person; topup -> penalty_excess_reversal; refund -> no_show_charge. Every `problem` is an extended id in this file, none a base policy, none self. Acyclic (two disjoint trees: {move -> reprice -> topup <- reversal}, {no_show -> refund}).
- `policy_source` verbatim in the blocked policy's own rule: all four located (extra_person rule sentence 3; topup rule sentences 6 and 7; refund rule sentence 3).
- `form`/`fallback_reason`: two state edges without fallback, two action edges with fallback — consistent.
- `kind`/`gate`: value_input gates `room_rate`, `rate_now`, `kept` are real bindings of the blocked compute; the state_gate `booking_charges.event_type` names a field, not one of the policy's eligibility gates (the extended policies declare none) — observation.
- `resolved_by` equals the depended-on policy's `target_tool` on all four edges, and each write does change the gated value or state (move writes `nightly_rate`/`room_type`; reprice writes `nightly_rate`; reversal creates the booking_penalty_reversal row; no-show charge creates the row `kept` sums).
- `condition` strength:
  - extra_person <- move: condition adds "and its nightly_rate is the double-occupancy rate of that room type", which the sentence ("only after the room type on the reservation sleeps every adult registered on it") does not say. Strengthened; observation (no task world separates the two).
  - refund <- no_show: condition adds "settled from money held, at the amount the no-show charge rules give"; the sentence only requires that "a no-show charge stands among the reservation's charges". Strengthened; observation.
  - the two topup edges match their sentences.
- No authoring-viewpoint phrasing ("this task", "at the opening") in any `prerequisite` text.

### prerequisite_sentences

| edge | sentence (own rule) | connective | form test | names tool/id/snake_case? | strength |
| --- | --- | --- | --- | --- | --- |
| reprice <- move | "The extra-person charge is added to the nightly rate only after the room type on the reservation sleeps every adult registered on it." | only after | state: room_type vs adults, capacity schedule in the rule | no | as condition minus the strengthening above |
| topup <- reprice | "No further advance deposit is collected until the extra-person charge for every adult beyond those the nightly rate covers has been added to the reservation's nightly rate." | until | action, fallback: the reprice tool writes only `nightly_rate`; no field marks the charge as added — justified | no | matches |
| topup <- reversal | "An additional deposit is collected only after the excess of any late cancellation penalty kept from money held on another reservation of the same guest at the same hotel for overlapping nights has been reversed." | only after | action, fallback: "before the reversal no entry marks it" | no | matches |
| refund <- no_show | "The refund of money held after a no-show is not made until a no-show charge stands among the reservation's charges." | not until | state: a booking_no_show_charge row | no | sentence weaker than condition (see above) |

- State-form single writer: room_type sleeping the adults is produced only by move_reservation_room (reprice does not write room_type; no shared write exists). A no-show charge row is produced only by post_no_show_charge. Unique.
- Fallback test on topup <- reversal: the reversal write leaves a record-visible state — a booking_penalty_reversal entry whose related_charge_id names that penalty (reversal_reason penalty_basis_misapplied). A state sentence "...only once each such penalty kept beyond what it owes carries a reversal" would single out that write. Observation: fallback not justified; the state is "a penalty reversal entry naming the kept penalty".
- Derivations (sentence + records + depended-on rule -> resolving action):
  - reprice <- move: room_type and adults are on the reservation; the capacity schedule (sleeps_*) is in the move policy; the only policy whose rule moves a reservation to a room type that sleeps its adults is capacity_room_move -> move_reservation_room. One reading.
  - topup <- reprice: the action is named in business words; the only policy that adds an extra-person charge to the nightly rate is extra_person_reprice. One reading.
  - topup <- reversal: the action is named; the only policy that reverses the excess of a late cancellation penalty is penalty_excess_reversal; the object is found via booking_reservations (same customer_id, property_code, overlapping nights) and booking_charges (booking_cancellation_penalty with settlement_source advance_deposit). One reading.
  - refund <- no_show: the only policy that posts a no-show charge is no_show_charge. One reading.
- No second wording of any dependency in any rule; no depended-on rule restates its sentence; docstrings silent on order. No extended rule states a cross-problem order that grounds no declared edge. Base rule sentences carry no cross-problem order on which a tree of this difficulty rests.

### override_declarations

Sentence-by-sentence against every `base_policy_refs` entry (findings only; demonstrations are in the task files).

- capacity_room_move vs booking_modification: superseded "Re-pricing follows booking_rate_plan_pricing." (declared). Every other sentence is followed (confirmed status, room_type_change_allowed, OTA exclusion, length-of-stay limits untouched by a room-type move). vs booking_rate_plan_pricing: the base prices a room type at booking from "the hotel's Flexible Rate quote for the room type and night"; no record carries such a quote, so the base gives no competing number for a move — observation, no conflict on the scored quantity.
- extra_person_reprice vs booking_rate_plan_pricing: superseded "The rate covers included_adults adults; each further adult adds extra_adult_charge_per_night_usd per night, and children up to children_stay_free_max_age years sharing existing bedding are not counted as adults." (declared). The replacement drops the children clause; schema records only adults, so no consequence (observation). vs booking_modification: followed.
- deposit_topup vs booking_evt_advance_payment: superseded single-collection sentence and resort-deposit sentence (both declared). The second replacement keeps only the size of the deposit and drops "charged at booking and the reservation is guaranteed by advance_deposit instead of the plan's default_guarantee_type" — a dropped provision; no task depends on it because guarantee_type is seeded (observation). "Money is collected only for a reservation whose status is confirmed" is followed.
- penalty_excess_reversal vs booking_late_cancellation_penalty: superseded the penalty-amount sentence (declared); its replacement is the baseline (one night / full stay with tax). vs booking_evt_penalty_reversal: NOT named in `overwrite`. Base sentences: "A cancellation penalty or no-show charge is reversed only for one of three recorded reasons" and "penalty_basis_misapplied applies when the amount charged exceeds the amount the plan's penalty basis yields for the reservation; only the excess is reversed." The extended rule reverses, under the same reason, the excess over "the penalty a late cancellation owes", which it builds from "the penalty night the plan's late-cancellation basis gives" multiplied by a lateness share and reduced by elite and card relief. By the extended rule's own vocabulary "what the basis gives" (the penalty night) and "what is owed" are different quantities, and the base clause bounds the reversal at the excess over the former. Undeclared override of the scored quantity and of the reversal's eligibility. Finding F1.
- no_show_charge vs booking_no_show: superseded the charge-amount sentence (declared). Others followed (no_show status, one charge, settlement from money held, hotel marks).
- deposit_refund vs booking_evt_deposit_settlement: superseded the refund-status sentence and the late-cancellation/no-show forfeit sentence (declared). The second replacement addresses only the no-show and drops the late-cancellation branch ("On a late cancellation ... retained as a forfeit and any amount held beyond the penalty is refunded") — dropped branch, declared as superseded; no task in this difficulty exercises a late-cancellation deposit settlement (observation). The first replacement adds "on the guest's own instruction", which also covers relocation refunds that the base `booking_relocate` trigger issues automatically (observation).
- Three disguised forms: no anonymous intermediate, no 0/1 multiplier found; the dropped branches above are the only instances.

### factor_ladders

Per policy (structure only; weight is per task):

| policy | factor | label | decides | tiers | multi-source | cross_difficulty | label honest |
| --- | --- | --- | --- | --- | --- | --- | --- |
| capacity_room_move | season_lead_multiplier | parameter | season_mult | 3 | yes (season + date) | — | yes |
| | elite_upgrade_discount | parameter | elite_disc | 3 | yes (tier + nights) | loyalty | yes |
| | club_upgrade_rate | parameter | club_rate | 3 | yes (level + status) | club | yes |
| | card_upgrade_credit | parameter | card_credit | 3 | no | loyalty | yes |
| | supplement_night_share | method | night_share | 3 | yes (stay + lead) | — | yes (three counting rules) |
| extra_person_reprice | extra_person_season_charge | parameter | adult_charge | 3 | yes | — | yes |
| | club_dependant_cover | parameter | uncharged | 3 | yes | club | yes |
| | frequent_guest_share | parameter | stay_share | 3 | no | loyalty | yes |
| | extra_person_night_share | method | night_share | 3 | yes | — | yes |
| deposit_topup | season_deposit_nights | parameter | deposit_nights | 3 | yes | — | yes |
| | stay_share_cap | method | deposit_base | 3 | yes | — | yes |
| | elite_deposit_relief | parameter | elite_relief | 3 | yes | loyalty | yes |
| | club_deposit_relief | parameter | club_relief | 3 | yes | club | yes |
| penalty_excess_reversal | lateness_share | parameter | late_share | 3 | no | — | yes |
| | penalty_night_basis | method | night_base | 3 | yes (stay + plan) | — | yes |
| | elite_penalty_relief | parameter | elite_relief | 3 | yes | loyalty | yes |
| | card_penalty_relief | parameter | card_relief | 3 | no | loyalty | yes |
| no_show_charge | late_change_saver_pricing | method | priced_night | 3 | yes | — | yes |
| | tier_no_show_relief | parameter | tier_relief | 4 | yes | loyalty | yes |
| | stay_history_relief | parameter | stay_relief | 3 | no | loyalty | yes |
| | card_no_show_relief | parameter | card_relief | 3 | no | loyalty | yes |
| deposit_refund | long_hold_handling_fee | parameter | handling_fee | 3 | yes (brand + date) | — | yes |
| | refund_size_fee_cap | method | fee_charged | 3 | no | — | yes |
| | tier_fee_waiver | parameter | tier_waiver | 4 | yes | loyalty | yes |
| | card_fee_waiver | parameter | card_waiver | 3 | no | loyalty | yes |

Shape: 4-6 factors each (5,4,4,4,4,4), at least 2 parameter and 1 method each; bindings disjoint within each policy; no `decides` is `result`; every tier stated in the rule with its value/method; no two tiers of a ladder share a value or method in the parameter tables as configured (one exception below). Fall-through of every ladder equals its `baseline` binding, and every `baseline.rule` sentence is a rule sentence; `baseline.params` keys exist.

Realism (conditions and outcomes judged against hotel and loyalty practice and the charter's own logic):
- Real or recognisable practice: seasonal/close-in upgrade pricing, elite and resort-club discounts on a paid upgrade, a free night per full week, seasonal extra-person charges, family-club dependants not charged as extra persons, peak/off-peak resort deposit nights, a deposit capped at a share of the stay, elite/club deposit relief, a graduated late-cancellation scale by days before arrival, a long-stay penalty share, a package penalty excluding the package supplement, tier-based fee waivers, a refund-size fee cap.
- Not a practice a hotel publishes (finding F4): a percentage reduction of the hotel's own late-cancellation penalty (`card_penalty_relief`), no-show charge (`card_no_show_relief`) or deposit refund handling fee (`card_fee_waiver`) because a co-brand card is linked. Co-brand card benefits are points, certificates, status and property credits; cancellation relief linked to a card comes from the card issuer's trip-cancellation insurance for covered reasons, never as a hotel tariff.
- Not a practice a hotel publishes (finding F5): `late_change_saver_pricing` prices a no-show night above the reservation's own booked nightly rate (up to the undiscounted Flexible Rate), selected by how many deposit payments the reservation carries and how many days before arrival the latest one posted. No hotel charges a no-show more than the rate the guest was booked at, and neither condition (count of deposit payments, date of the latest top-up) is something a hotel weighs for a no-show charge; it also contradicts the charter's own guarantee logic ("one night at the reservation's nightly rate", base booking_no_show / booking_late_cancellation_penalty).
- Borderline, recorded as observations: elite penalty/no-show relief as fixed percentages (elite leniency is a real courtesy but is not published as a percentage tariff); frequent-stay relief on the no-show charge and on the extra-person charge; a "long-hold" handling fee on deposit refunds keyed on days since booking; the per-night co-brand credit against a paid upgrade (close to real co-brand property credits).
- Charter-global ladder defect without a task bearing it: `extra_person_season_charge` on the Bed & Breakfast Package Rate — the plan's own extra-adult charge (35.00, the fall-through) is above the "mid-season" charge (32.00), so a peak short stay pays less per extra adult than an off-peak stay. Observation (both tasks are on other plans).

Counts per task (structural): task 0's policies carry cross_difficulty factors reading loyalty and club and several multi-source factors; task 1's carry cross_difficulty factors reading loyalty and multi-source factors. Whether they survive the realism tests and bear weight is in each task's `factor_weight`.

### findings

- **F1 — SOURCE-POLICY RED (undeclared override).** Symptom: penalty_excess_reversal reverses an amount the base reversal clause does not allow. Root cause: booking_evt_penalty_reversal is in `base_policy_refs` but absent from `overwrite`; its sentences "A cancellation penalty or no-show charge is reversed only for one of three recorded reasons" and "penalty_basis_misapplied applies when the amount charged exceeds the amount the plan's penalty basis yields for the reservation; only the excess is reversed" stay in force, while the extended rule reverses the excess over a penalty "owed" that is reduced by lateness share, elite relief and card relief. Evidence: extended charter lines 1484-1501 (base) vs 2245-2275 (extended rule), overwrite at 2219-2224 names only booking_late_cancellation_penalty. Bears on: task 0 (demonstrated in 0.md). Artifact: booking.extended.yaml `booking_ext_penalty_excess_reversal.overwrite`.
- **F2 — SOURCE-POLICY RED (rule/compute equivalence).** Symptom: the stay-history tier in two policies is counted differently by rule and compute. Root cause: the rules say "at least the frequent number of stay night credits posted in the last twelve months" (extra_person_reprice) and "at least the steady number of stay night credits posted in the last twelve months" (no_show_charge); compute is `XCOUNT('loyalty', 'loyalty_transactions', within_months=12, ...)`, a count of postings, and `_within` admits a row only when `0 <= MONTHS(posted, NOW) < 12`. (a) "Night credits" is the charter's unit of nights (`loyalty_transactions.nights`: "number of elite night credits moved"; `loyalty_memberships.elite_night_credits` is a sum of nights), so the rule counts nights while compute counts postings; the param names `frequent_stays`/`steady_stays` appear nowhere in the rule text. (b) The rule states no boundary for "the last twelve months"; compute excludes a posting dated exactly twelve months before the handling date — a counting convention with no basis quotation. Evidence: charter lines 1868-1871, 1910, 1927-1928, 2437-2440, 2465, 2482-2483; check_compute.py `_within`. Bears on: task 0 (reading a) and task 1 (readings a and b), demonstrated in each file.
- **F3 — SOURCE-POLICY RED (compute invents a floor), no task bears it.** `gross_diff: "MX(new_diff - old_diff, 0)"` vs rule "The move supplement is the published differential of the new room type less that of the room type it leaves". Same situation, different conclusions: a deluxe_king reservation (55.00) raised to 3 adults moves to standard_two_queens (40.00); the rule gives a differential of -15.00 (a lower nightly rate), compute gives 0 (rate unchanged). Neither task's world enters this branch (task 0 moves standard_king -> standard_two_queens, +40.00). Artifact: capacity_room_move compute `gross_diff`.
- **F4 — SOURCE-FACTOR RED (unreal ladder), co-brand card reliefs** `card_penalty_relief`, `card_no_show_relief`, `card_fee_waiver`: every non-fall-through tier is a treatment no hotel publishes (see factor_ladders). Bears on: task 0 (card_penalty_relief), task 1 (card_no_show_relief, card_fee_waiver); consequences on factor counts are in the task files.
- **F5 — SOURCE-FACTOR RED (unreal ladder), `late_change_saver_pricing`**: tiers charge a no-show above the booked rate on conditions no hotel weighs (see factor_ladders). Bears on: task 1.
- Observations (no demonstrated consequence): adults above 6 in `new_diff`; strengthened `condition` on reprice <- move and refund <- no_show; topup <- reversal fallback unjustified (state: a penalty reversal entry naming the kept penalty); state_gate `gate` names a field; dropped provisions in the deposit_topup and deposit_refund overwrites; `inputs.history` metadata incomplete; B&B extra-person ladder inversion; reprice docstring "once".

## post_reveal_addendum

Written after both task files were frozen and their GT revealed (2026-10-05T16:23Z onward). The charter-global section above is left as frozen.

- Missed in the pre-reveal scan, prompted by task 0's `design_rationale` ("Known risk recorded: the further deposit uses booking_deposit_collect, an event the blueprint lists for no difficulty's claim") and re-checked against blueprint.yaml alone: the claim of this difficulty is `event_types [booking_reservation_cancel, booking_reservation_modify, booking_cancellation_penalty, booking_no_show_charge, booking_penalty_reversal, booking_deposit_refund, booking_deposit_forfeit]`; `booking_ext_deposit_topup.subject` is `booking_deposit_collect`, outside it, and the summary's agent duties ("posts the penalty, refund, forfeit or reversal the rules produce") do not include collecting deposits. No policy-task relationship is contradicted by this (the merged policy is self-consistent on it and task 0's tree uses it consistently); recorded as an observation on the blueprint-claim boundary, outside the four relationships.

## closing_checklist

Not closed. Step 4 requires every task to PASS all four relationships; neither does.

| task | policy self-consistency | problem tree | factors | unique solution |
| --- | --- | --- | --- | --- |
| 0 | SOURCE-POLICY RED (F1, F2a) | PASS | SOURCE-FACTOR RED (F4: card_penalty_relief; reversal below 4 real factors) | SOURCE-TASK RED |
| 1 | SOURCE-POLICY RED (F2a, F2b) | PASS | SOURCE-FACTOR RED (F4, F5: no-show 2 real factors and no method; refund 3) | SOURCE-TASK RED |

Items that do hold: one audit file per task plus this file; the six extended policies covered by the two tasks' `charter_scope` with no overlap (task 0: topup, reprice, move, reversal; task 1: no_show_charge, deposit_refund); task tools closed with GT and six independent uuid8s; each tree has 1-3 prerequisite problems, enough value_input edges, a customer-owned write and no cycle, and the difficulty-wide graph is acyclic; every factor bears weight on its world against an honest baseline and every all-baseline number is definite and differs from gold. F3 (compute floor in capacity_room_move) is a charter defect no task exercises.

Gate re-run on the final form: not performed by this audit (no artifact changed; the brief's gate snapshot in /tmp/env0036_views/reservation_cancellations_and_no_shows/GATES.txt stands). The gates passing does not offset the REDs above.

## revision_2

Re-audit round 2. The text above (revision 1, including its post_reveal_addendum and closing_checklist) is left untouched.

### charter_global_frozen (revision 2)

- Freeze: written 2026-10-05 17:29Z, before any revision-2 task GT was read. Auditor: erl-task-policy-audit subagent.
- Hashes (re-computed, equal to the rebuilt HASHES.txt): booking.extended.yaml 9c36fcd978c8deaef8bb946da57d1a3df9df2655089121688210bb2682a7d51a (CHANGED from a8e39ee2… -> every charter-global section re-derived below); task_tools.py a3ea0abfb0e01af60eb106be7d8f6ae86e5d5014e273f7354e7a9c1f57a86b2b (UNCHANGED -> § action_binding_and_uuids of revision 1 carried forward by reference on that hash).
- Entry conditions: rebuilt views + HASHES.txt and a fresh GATES.txt (seven gates OK) supplied. Input complete.
- Base copy: lines 1-1609 still byte-identical to blueprint/products/booking.yaml.
- contamination_disclosure: the auditor read the revision-1 GT of both tasks in round 1 (recorded there). That knowledge predates this revision; no revision-2 GT field, worklog or reworker note was read before the freezes below. The reworker's claim list (item ids only) was read from the brief.

### policy_conflict_scan (revision 2)

Same six policies, subjects, computes and tools as revision 1. Changes found: capacity_room_move rule gains the no-lowering sentence; extra_person_reprice per-adult tiers are now the plan's charge plus a supplement, and the stay-history sentence is rewritten; deposit_topup's second overwrite (resort-deposit sentence) is removed and its reversal edge is now state form; penalty_excess_reversal declares a second overwrite (the base penalty_basis_misapplied clause), drops `card_penalty_relief` and adds `holiday_penalty_floor`; no_show_charge drops `late_change_saver_pricing` and `card_no_show_relief`, adds `no_show_night_basis` (method), `direct_booking_courtesy` and a money-held cap; deposit_refund drops `card_fee_waiver`, adds `direct_booking_fee_waiver`, and narrows its first overwrite to the status sentence. Overlapping subjects compose as in revision 1, with one new conflict (finding F6). Cross-category reads now: loyalty (variant_name, elite_night_credits, cobrand_card [move only], status, night-credit postings) and club. The blueprint-claim observation on `booking_deposit_collect` stands.

### rule_compute_equivalence (revision 2)

- capacity_room_move: `gross_diff: MX(new_diff - old_diff, 0)` now has its basis, "A move never lowers the nightly rate: where the new room type's differential is below that of the room type it leaves, no differential is charged." (also in baseline.rule). F3 closed. Adults above 6 still fall to one_bedroom_suite (observation).
- extra_person_reprice / no_show_charge stay-history: the rules now read "the frequent [steady] number of stays credited in the twelve months before the day of handling, each stay night-credit posting counting as one stay whatever its nights and a posting dated on or before the same calendar date twelve months earlier being outside them". Compute `XCOUNT(... within_months=12 ...)` with `_within: 0 <= MONTHS(posted, NOW) < 12`: a posting on the same calendar date twelve months earlier gives MONTHS = 12 (excluded), any later posting gives at most 11 (included); the unit is postings. Rule and compute agree. F2a and F2b closed. Residual: a posting dated on the handling day itself is counted by compute (MONTHS = 0) while "before the day of handling" can be read to exclude it; no world has such a posting (observation).
- extra_person_reprice `adult_charge`: P + supplement tiers match the rule; the round-1 B&B inversion is gone (35.00 / 42.00 / 50.00).
- penalty_excess_reversal: `floor_share`, `share_charged = MX(late_share, floor_share)` have bases ("Holiday terms set a floor under that share ...", "The share charged is the larger of the lateness share and the holiday floor"). Equivalent.
- no_show_charge: `room_portion`, `no_show_night`, `direct_channel`, `direct_relief`, `charge`, `result = MN(charge, held)` for advance_deposit/full_prepayment — each has a basis ("A no-show charge settled from money held is never more than the money held ...", "the limit of the money held is applied last, to the rounded charge"). Equivalent.
- deposit_refund: `direct_waiver` has its basis. Equivalent. `inputs.history` now complete on topup, no-show and refund.
- All factor ladders: every tier is a rule sentence and a binding branch, both directions.

### action_binding_and_uuids (revision 2)

Carried forward from revision 1 by reference (task_tools.py hash unchanged; no policy changed its `target_tool` or `computes`).

### prerequisite_graph (revision 2)

Same four edges, acyclic. Changes: reprice <- move `condition` now "booking_reservations.room_type of the reservation is a room type whose capacity in the room-type capacity schedule is at least booking_reservations.adults." (matches its sentence; round-1 strengthening closed); refund <- no_show `condition` now "booking_charges carries a booking_no_show_charge entry for the reservation." (matches; closed); topup <- reversal now `form: state`, no `fallback_reason`, condition "Every booking_cancellation_penalty settled from money held on another reservation of the same customer_id and property_code whose nights overlap, where it exceeds the penalty its cancellation owes, has a booking_penalty_reversal entry whose related_charge_id names it." (matches its sentence). The state_gate `gate: booking_charges.event_type` still names a field rather than an eligibility gate (observation, unchanged).

### prerequisite_sentences (revision 2)

- topup <- reversal: "An additional deposit is collected only after each late cancellation penalty kept from money held on another reservation of the same guest at the same hotel for overlapping nights, where it exceeds the penalty that cancellation owes, carries a penalty reversal entry naming it." Connective "only after"; state "carries a penalty reversal entry naming it" in record words; no tool, id or snake_case; strength equals the condition. The only write creating a booking_penalty_reversal row is reverse_penalty_excess_975f0de4. One reading. Round-1 fallback observation closed.
- The other three sentences are unchanged and pass as in revision 1 (topup <- reprice action form with a justified fallback).
- No new cross-problem order in any rule; docstrings unchanged.

### override_declarations (revision 2)

- capacity_room_move, extra_person_reprice: as revision 1.
- deposit_topup: only the single-collection sentence is superseded now; the base resort-deposit sentence ("... a resort advance deposit of resort_deposit_nights nights of room and tax is charged at booking ...") stays in force and governs the collection at booking, while the extended rule governs further deposits after a change; no shared scored quantity. Round-1 dropped-provision observation closed.
- penalty_excess_reversal vs booking_evt_penalty_reversal: the clause "penalty_basis_misapplied applies when the amount charged exceeds the amount the plan's penalty basis yields for the reservation; only the excess is reversed." is now superseded by "A late cancellation penalty that was kept at more than the penalty a late cancellation owes is reversed for the excess, under the reason that the plan's penalty basis was misapplied, naming the original penalty it reverses." The base closed-reason sentence ("reversed only for one of three recorded reasons") stays and is satisfied (the reason is penalty_basis_misapplied as redefined). F1 closed.
- no_show_charge vs booking_no_show: only the computing sentence is superseded. The base sentence "When no_show_releases_remaining_nights is true the nights after the first are released and not charged; when it is false the whole stay is retained." is NOT named. The new `no_show_night_basis` extended-stay tier ("For a stay of at least the extended-stay nights, the no-show night is the extended-stay share of the whole stay at the nightly rate less any package supplement") charges 0.30 × nights of room portion — for any stay of 7 or more nights that is more than one night, i.e. it charges nights after the first on every plan whose `no_show_releases_remaining_nights` is true (all plans but Advance Purchase). Undeclared override. Finding F6.
- deposit_refund: first overwrite now replaces only the status sentence ("... cancelled, relocated or no-show"); the guest-instruction clause moved into the rule and limited to refunds after a no-show — round-1 relocation observation closed. The second overwrite still replaces the late-cancellation-and-no-show forfeit sentence with a no-show-only sentence (dropped late-cancellation branch; observation unchanged, no task exercises it).

### factor_ladders (revision 2)

| policy | factors (label) | count | parameter / method | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| capacity_room_move | unchanged (5) | 5 | 4 / 1 | yes | loyalty, club |
| extra_person_reprice | extra_person_season_charge (P + supplement), club_dependant_cover, frequent_guest_share, extra_person_night_share (method) | 4 | 3 / 1 | yes | club, loyalty |
| deposit_topup | unchanged (4) | 4 | 3 / 1 | yes | loyalty, club |
| penalty_excess_reversal | lateness_share, holiday_penalty_floor, penalty_night_basis (method), elite_penalty_relief | 4 | 3 / 1 | yes (floor: season + stay; elite) | loyalty |
| no_show_charge | no_show_night_basis (method), tier_no_show_courtesy, stay_history_courtesy, direct_booking_courtesy | 4 | 3 / 1 | yes (tier; direct: channel + membership status) | loyalty |
| deposit_refund | long_hold_handling_fee, refund_size_fee_cap (method), tier_fee_waiver, direct_booking_fee_waiver | 4 | 3 / 1 | yes | loyalty |

Every ladder has 3-4 disjoint tiers with distinct values/methods, fall-through = baseline, every tier stated in the rule; labels honest (`no_show_night_basis` changes the computation: share of the whole stay vs room portion vs plan basis).

Realism:
- F4 closed for the three card reliefs (removed). `card_upgrade_credit` on the paid room move remains (observation, as agreed: close to co-brand property credits).
- F5 closed (`late_change_saver_pricing` removed; nothing now charges a no-show above the booked rate per night).
- New `holiday_penalty_floor`: holiday/peak minimum cancellation charges are a published resort practice — passes. Its middle tier is also applied to standard-season stays of 7+ nights under the name "holiday short-stay floor" (naming oddity, observation).
- New `direct_booking_courtesy` / `direct_booking_fee_waiver`: hotels do differentiate direct bookings and members; a small percentage courtesy is borderline, recorded with the elite courtesies as an observation.
- New `no_show_night_basis` extended-stay tier: contradicts the charter's own release rule (F6); as a hotel practice a holiday long-stay no-show term is recognisable, so the realism point is subsumed in F6.

### findings (revision 2)

- F1 closed; F2 (a, b) closed; F3 closed; F4 closed; F5 closed (evidence above).
- **F6 — SOURCE-POLICY RED (undeclared override, new in revision 2).** Symptom: the no-show charge on a stay of 7+ nights exceeds one night on plans that release the nights after the first. Root cause: booking_no_show's release sentence is not named in `booking_ext_no_show_charge.overwrite`, while the new extended-stay tier charges the extended-stay share of the whole stay. Evidence: base rule (charter line 1229-1230) "When no_show_releases_remaining_nights is true the nights after the first are released and not charged"; extended rule lines 2427-2431; compute `no_show_night` line 2461; overwrite lines 2388-2393. Bears on: task 1 (demonstrated in 1.md revision_2). Affected: booking.extended.yaml `booking_ext_no_show_charge`.
- Observations carried: adults above 6 in `new_diff`; handling-day posting edge of the twelve-month window; state_gate `gate` field; dropped late-cancellation branch in the deposit_refund overwrite; `booking_deposit_collect` outside the blueprint claim; elite/direct/stay courtesies and the card upgrade credit as borderline realism; seeded no_show without the event-triggered charge (task 1, see 1.md).

### closing_checklist (revision 2)

Written after both revision-2 reveals (2026-10-05T17:31Z). Not closed: task 1 fails two relationships.

| task | policy self-consistency | problem tree | factors | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS |
| 1 | SOURCE-POLICY RED (F6) | PASS | PASS | SOURCE-TASK RED (F6) |

- Round-1 REDs: F1, F2a, F2b, F3, F4, F5, T0-1, T0-2, T0-3, T0-5, T1-1, T1-2, T1-3 all verified closed on the revision-2 artifacts. Round-1 observations closed: reprice <- move and refund <- no_show conditions, topup <- reversal form, topup dropped provision, refund relocation clause, inputs.history, B&B extra-person inversion. Kept as observations: `booking_deposit_collect` outside the blueprint claim, elite courtesies, card upgrade credit, dropped late-cancellation branch in the refund overwrite, state_gate field, adults above 6.
- New defect: F6 (task 1).
- Holds: one audit file per task plus this file, revisions appended; six policies covered by disjoint task scopes; task tools and uuid8s unchanged and closed with GT; each tree has 1-3 prerequisites, value_input floor met, a customer-owned write, no cycle, and the difficulty graph is acyclic; every computation has 4-6 factors (>= 2 parameter, >= 1 method), multi-source and cross_difficulty per task, every factor bears weight against an honest baseline, and every all-baseline number is definite and differs from gold.
- Gates: the fresh GATES.txt (seven OK) is the re-run on the final form; it does not offset F6.

## revision_3

Re-audit round 3. Revisions 1 and 2 above are left untouched.

### charter_global_frozen (revision 3)

- Freeze: written 2026-10-05T23:55Z, before any revision-3 task GT was read. Auditor: erl-task-policy-audit subagent.
- Hashes (re-computed, equal to the rebuilt HASHES.txt): booking.extended.yaml 64874eaed7189e0a861fa42aa3833ea8a554bbb25d104d379ab1df8f0b939e0e (CHANGED from 9c36fcd9… -> charter re-checked below); task_tools.py a3ea0abf… (UNCHANGED -> § action_binding_and_uuids carried forward by reference).
- Fresh GATES.txt: seven gates OK. Base copy lines 1-1609 still byte-identical to blueprint/products/booking.yaml.
- What changed (located by reading the file, no prior copy kept): the first five policies start at the same lines as revision 2 (1615, 1827, 2002, 2207, 2386) and their hallmark sentences/params are present; re-evaluating their compute on task 0's unchanged world reproduces every revision-2 figure, including all baseline substitutions. Changed: `booking_ext_no_show_charge` (extended-stay tier and its two params removed; new tier for extra adults; release sentence added to the rule) and `booking_ext_deposit_refund` (`long_hold_days` 120 -> 100). The file is 4 lines shorter.
- contamination_disclosure: the auditor knows the revision-1 and revision-2 GT of both tasks (read in earlier rounds, recorded there). No revision-3 GT, worklog or reworker note read before the freezes below.

### charter-global re-check (revision 3)

- no_show_charge rule now says "The nights after the first are released or retained as the plan's no-show release rule provides, and what the no-show night contains follows the services that were never provided: on a package plan the no-show night is one night at the nightly rate less the package supplement, the package's inclusions not being served; on any other plan that releases the nights after the first, where the reservation registers adults beyond those the plan's rate covers, it is one night at the nightly rate less the extra-adult charge for those adults; any other reservation keeps the no-show night the plan's basis gives." Every tier charges at most one night on a releasing plan; the only multi-night outcome is the fall-through full_stay basis, which belongs to the Advance Purchase plan whose `no_show_releases_remaining_nights` is false ("the whole stay is retained"). The base release sentence is now honoured, so no override needs declaring. **F6 closed.**
- rule/compute: `room_portion`, `extra_adult_part = MX(adults − included_adults, 0) × extra_adult_charge_per_night_usd`, `no_show_night` match the three tiers both ways; the package tier is implemented as `P('breakfast_included')` (B&B only, as before). Equivalent.
- Ladder `no_show_night_basis` (method): 3 disjoint tiers, distinct methods, fall-through = baseline, stated in the rule. Realism: a no-show charge that leaves out undelivered package inclusions and per-person charges for guests who never arrived is consistent with hotel practice and with the charter's own first-night logic — passes. Factor counts unchanged (4 per computation; 3 parameter / 1 method), multi-source and cross_difficulty unchanged.
- Observation (new, no task exercises it): the extra-adult tier subtracts the plan's extra-adult charge × extra adults (the charter's "extra-adult charge" vocabulary), not the extra-person charge the reprice policy actually added; for a reservation repriced under `booking_ext_extra_person_reprice` the two differ (e.g. task 0's R1 after its reprice, were it a no-show: 435.42 − 50.00 = 385.42 vs 408.75 had the added 26.67 been removed). The vocabulary distinguishes "extra-adult charge" (plan) from "extra-person charge" (reprice), so one reading prevails; recorded as a realism/consistency observation.
- deposit_refund: only `long_hold_days` changed; rule wording ("at least the long-hold days") unchanged and parametric. No other change.
- prerequisite graph, prerequisite sentences, override declarations, factor ladders of the other five policies: as revision 2 (unchanged policies). Observations carried as listed in revision 2.

### findings (revision 3)

- F6 closed. No new RED at charter level. New observation: the extra-adult no-show tier's charge vocabulary (above).

### closing_checklist (revision 3)

Written after both revision-3 reveals (2026-10-05T23:55Z).

| task | policy self-consistency | problem tree | factors | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

- Per-task files 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json, with this file alongside; revisions 1-3 appended, older text untouched; every revision-3 comparison carries a PASS.
- Round-2 RED F6 / T1-5 verified closed; all round-1 REDs remain closed; no regression on task 0 (all figures reproduced).
- Coverage and exclusivity: the six extended policies are covered by task 0 {deposit_topup, extra_person_reprice, capacity_room_move, penalty_excess_reversal} and task 1 {no_show_charge, deposit_refund}, pairwise disjoint across each whole tree; task tools closed with GT; six independently generated, frozen uuid8s (563d533b, 22837316, 8cd35ccc, 975f0de4, 68d6e4c0, 05a65982).
- Trees: task 0 has 3 prerequisite problems with 2 value_input edges, task 1 has 1 with 1; each has an owner=user write (pay_deposit_topup, request_deposit_refund); no cycle; the difficulty-wide graph is acyclic.
- Factors: every computation declares a self-sufficient baseline and 4-6 factors (>= 2 parameter, >= 1 method); per task at least one multi-source and one cross_difficulty factor (task 0: loyalty, club; task 1: loyalty) on seeded rows; every ladder has >= 3 tiers stated in its rule with distinct outcomes; every factor bears weight against an honest baseline, and every all-baseline number is definite and differs from gold.
- Gates: the orchestrator's fresh GATES.txt for this final form shows all seven gates OK (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE); traceability deferred to render.
- Standing observations (no RED): `booking_deposit_collect` outside the blueprint claim; elite/stay/direct-booking courtesies and the card upgrade credit as borderline realism; dropped late-cancellation branch in the refund overwrite; state_gate `gate` names a field; adults above 6 in the move compute; handling-day posting edge of the twelve-month window; extra-adult no-show tier vocabulary; seeded no_show without its event-triggered charge.

The difficulty passes the source-layer audit at revision 3.
