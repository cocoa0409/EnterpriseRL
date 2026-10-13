# Policy-task audit — free_night_award_redemptions / charter-global

## charter_global_frozen

- Auditor: claude-opus-5-5 running erl-task-policy-audit, independent of the authoring agent; accepted no answers on its behalf.
- Freeze time: 2026-10-05T13:36Z UTC (before any task GT was revealed).
- Frozen inputs (sha256 recomputed by the auditor and matching `/tmp/env0036_views/free_night_award_redemptions/HASHES.txt`):
  - `env/env_0036_hotel_and_resort_brand/tasks/free_night_award_redemptions/certificate.extended.yaml`: `99b15860d4266dcb96980dd6b0254bc660345dbe641c8ee5ed54b75c44d92e9c`
  - `env/env_0036_hotel_and_resort_brand/tasks/free_night_award_redemptions/task_tools.py`: `da3b626327535b9084435bdeda4e3783520959c6623baf2914be3b115a174c92`
- Permitted and read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/certificate.yaml`, plus targeted excerpts of `blueprint/products/booking.yaml` (Reward Night Rate variant and `booking_cancellation_deadline`) and `blueprint/products/loyalty.yaml` (`award_chart`, `loyalty_award_redemption`). Also read: the extended charter, task_tools.py, the DSL evaluator semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (lines 20-420, primitives only, no task data), and the two masked views.
- Masked and not read before the freeze: every `tasks/*.json` field other than frozen_time / user_scenario / initial_state (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure), `tasks/free_night_award_redemptions/worklog.md`, the scenario worklog, and any other audit directory. No recursive search touched `tasks/` or `env/`.
- Entry conditions (Step 0): the gate snapshot `/tmp/env0036_views/free_night_award_redemptions/GATES.txt` shows EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. The masked views and their hashes are present. Traceability is deferred to render (per brief). Entry conditions are met.

DSL semantics this audit relies on (from check_compute.py `build_env`): `F(field)` reads the target award's own row; `SUM/COUNT/MAX/LATEST` are scoped to `certificate_id = HID`; `CFIELD(cat, field, **eq)` returns the first of the customer's holdings in that category that matches `eq`; `XCOUNT/XSUM` read another category's ledger scoped to the customer; `within_months=w` keeps rows with `0 <= MONTHS(date, NOW) < w`; `MONTHS` counts whole months and subtracts one when the end day number is smaller than the start day number; `DAYS` is a plain day difference on the date part.

### policy_conflict_scan

The extended charter has six policies, which form two chains:

| id | subject / computes | target_tool (owner) | trigger | prerequisite |
|---|---|---|---|---|
| P1 `certificate_ext_late_cancel_loss_value` | forfeit + forfeit_record / award_points_price | `forfeit_late_cancel_award_5a86721d` (agent) | state_due | [] |
| P2 `certificate_ext_late_cancel_return_protection` | release + release_record / award_points_price | `release_later_night_award_2a59ee43` (agent) | state_due | P1, state_gate |
| P3 `certificate_ext_returned_award_rebook_price` | apply + hold_record / award_points_price | `apply_returned_award_7b7c21ba` (user) | on_request | P2, value_input |
| P4 `certificate_ext_relocation_return_protection` | release + release_record / award_points_price | `release_relocated_award_8143384d` (agent) | state_due | [] |
| P5 `certificate_ext_relocation_replacement_validity` | issue / expiry_date | `reissue_replacement_award_0d99e6ce` (agent) | state_due | P4, value_input |
| P6 `certificate_ext_replacement_hold_price` | apply + hold_record / award_points_price | `apply_replacement_award_003026b1` (user) | on_request | P5, state_gate |

- Overlapping subjects. P2 and P4 both own `certificate_release`. Their triggers do not overlap: P2 covers a later-night award on a reservation cancelled after its deadline, and P4 covers any award on a reservation the hotel relocated. A reservation is either cancelled or relocated, never both (booking `status` enum). P3 and P6 both own `certificate_apply`. P3 covers "an award that came back from a cancelled stay" and P6 covers "a replacement award". These overlap in one case that neither task seeds: a replacement that was later applied, cancelled and returned would fall under both P3 and P6 for its next hold. The charter does not resolve that case. This is recorded as observation O-1, with no consequence on either task world.
- Base vs extended on the same quantity. P1, P2, P3, P4 and P6 each replace the base "repeat the points price recorded on the hold" or "chart price on the hold" clause, and each declares the replacement. Section `override_declarations` covers this, and also one undeclared override (finding G-4).
- Time anchors. P1, P2 and P3 anchor on `cancelled_at`/`arrival_date`/`booked_date` and on NOW (the return or hold date). P4 and P5 anchor on `relocated_date` and the return date. Every write happens at NOW, so no anchor conflicts with another.
- Cross-category reads. All six declare `cross_category` for booking and loyalty, and every read is a `CFIELD`/`XCOUNT`/`XSUM` over the customer's own rows. No write touches another category. Note that the base `certificate_apply` triggers `loyalty_points_redeem` when top-off is not 0, and `certificate_release` triggers `loyalty_points_redeposit`. Both apply tools hard-code `top_off_points=0`, and `release_later_night_award` hard-codes 0 on the return record. See O-2.
- Scope exclusivity and completeness. charter_scope is masked. Structurally the two chains {P1, P2, P3} and {P4, P5, P6} are disjoint, and together they cover all six policies. Each task view matches exactly one chain: task 0 is a late cancellation with a re-application, and task 1 is a relocation with a replacement. This is confirmed against charter_scope after the reveal, in each task file.

### rule_compute_equivalence

I swept every compute binding against its `compute_basis` quote and the rule, in both directions.

- P1. The chart, step and season bindings are stated in the rule. `lv_hold_topoff` (deducted minus returned for that award) is stated. The three share methods are stated. Both reliefs are stated, with their compound conditions. "Both taken off once, in whole points and never below zero" is implemented as `int(MX(0, ...))`. Nothing is invented and nothing is promised without being implemented.
- P2. Every tier, window ("twelve calendar months before the return", `within_months=12`) and counting convention ("whole calendar days from the date the cancellation was recorded to the arrival date", `DAYS(cancelled_at, arrival_date)`) is quoted. "Whole calendar months from the enrolment date to the date of the return" is `MONTHS(enrolled_date, NOW)`. Equivalent.
- P3. Equivalent except for two points:
  - (a) `ap_cat`, `ap_season`, `ap_lead_days` and `ap_points_nights` read `CFIELD('booking', ..., status='confirmed', variant_name='Reward Night Rate')`, which is the first confirmed Reward Night Rate reservation of the customer. The rule names "the new reservation", meaning the reservation the award is being applied to. These differ whenever a member holds two confirmed reward reservations. Neither task world has a second one (task 0 has only df81d5b8, task 1 has only b855decd), so this is observation O-3 with no demonstrated consequence.
  - (b) "The stays reduction counts the stay night credits posted to the membership in the twelve calendar months before the hold" is implemented as `XCOUNT(... loyalty_night_credit, stay_nights)`, which counts postings. Throughout this charter, "night credits" is a count of nights: "elite night credits this year are at least the lower loss night threshold" is compared against `elite_night_credits`, which the schema calls "integer nights … the sum of night credits". So the sentence also reads as the number of nights credited, which is SUM(nights). The rule admits two readings and compute implements one of them. **Finding G-2.**
- P4. Equivalent. The ladder says "more than the short-delay days … ; fewer protect it at the price on the standing hold", which leaves a delay of exactly 30 days unnamed in prose. Compute's `else` covers it. That is observation O-4; neither world sits on the boundary (task 1 delay = 94 days).
- P5. Equivalent. The month arithmetic (`rq_anchor_index`, `rq_target_index`, `rq_target_days`, `rq_day`) implements "the calendar month that lies the total months after the month of the reissue date" and the three day conventions. The stays sentence has the same wording as P3, "The stays extra counts the stay night credits posted to the membership in the twelve calendar months before the reissue", and is implemented as a count of postings. **Finding G-2.**
- P6. Equivalent as prose. Two caveats:
  - "Walk protection reads the history of the award the replacement replaces" is implemented with `LATEST/COUNT` scoped to HID, plus `F('reservation_id')`. This matches the rule only when the computation's target holding is the replaced award. On the replacement itself, `F('reservation_id')` is empty (the reissue tool sets no reservation) and its own history holds no relocated return. That would silently send walk protection to the fall-through. The target holding is masked, so this is checked after the reveal in the task 1 file.
  - The same `CFIELD(status='confirmed', variant_name='Reward Night Rate')` keying as P3 applies (O-3).

### action_binding_and_uuids

- `(target_tool, computes)` pairs are all distinct: (5a86721d, award_points_price), (2a59ee43, award_points_price), (7b7c21ba, award_points_price), (8143384d, award_points_price), (0d99e6ce, expiry_date), (003026b1, award_points_price). No pair is claimed by two policies.
- The uuid8s are 5a86721d, 2a59ee43, 7b7c21ba, 8143384d, 0d99e6ce and 003026b1. They share no common prefix or suffix, show no sequence, and no tail is a copy of another. I found no sign that they were derived in a batch.
- Function bodies (task_tools.py) find the award, update status/fields and create the history row, and nothing else. No tool refuses a call, checks a status or a prerequisite, or computes a value. The tool layer judges no prerequisite.
- Docstrings name no other tool and state no sequence position. Two observations:
  - Every Id-class argument says "read from … records before the call". That is a generic read instruction, not an ordering between writes.
  - `apply_replacement_award_003026b1.certificate_id` says "as returned when the replacement was issued or read from the member's award records". This alludes to the reissue action, but adds nothing beyond P6's own prerequisite sentence (O-5).
- Terminal states. The base lifecycle says "issued→expired by: system". `release_relocated_award_8143384d` always sets `status="issued"` ("Afterwards the award shows back in the member's account"), including for an award whose expiry date has passed. See finding G-4.

### prerequisite_graph

- `prerequisite` is filled in on all six (P1 `[]`, P4 `[]`).
- Edges are P2→P1, P3→P2, P5→P4 and P6→P5. Every `problem` is an extended policy id in this file, none is a base policy, and none points at itself. The graph is acyclic: two chains of length 3.
- `policy_source` is verbatim in the blocked policy's own rule, for each edge:
  - P2: "A later-night award of a reservation cancelled after its deadline is not returned until the award paying that reservation's first night stands forfeited with its loss record in its history." Present in P2.rule.
  - P3: "The rebooked night's price of a returned award is fixed only after the award stands back in the member's account with its return from the cancelled stay entered in its history." Present in P3.rule.
  - P5: "A replacement's expiry date is set only after the award it replaces stands back in the member's account with its return from the relocated stay entered in its history." Present in P5.rule.
  - P6: "A replacement award's hold is not placed until the replacement stands issued in the member's account carrying the number of the award it replaces." Present in P6.rule.
- `form: state` on all four, and none carries a `fallback_reason`, which is correct.
- `resolved_by` is the depended-on policy's `target_tool` in all four cases: 5a86721d, 2a59ee43, 8143384d, 0d99e6ce.
- `kind`/`gate`:
  - P2 `state_gate` on `free_night_certificates.status` is a real state, the first-night award's status.
  - P3 `value_input` on `ap_protected` exists in P3.compute, and the depended-on write creates the latest return record that `ap_ret_recent`, `ap_ret_price` and `ap_same_hotel` read.
  - P5 `value_input` on `rq_return_date` exists, and is the LATEST relocated return that P4 writes.
  - P6 `state_gate` on `free_night_certificates.replaced_certificate_id` is a real field, set by the reissue.
- `condition` against the sentence:
  - P2, P3 and P6 conditions restate their sentences.
  - P5's condition adds "dated on or after its expiry date has passed". That clause comes from P5's own trigger ("after the award's expiry date had passed"), not from the prerequisite sentence. It is a mild strengthening that changes no reading on either world (O-6).
  - P5's condition also requires "The replaced award's status is issued", which collides with a base sentence. See G-4.
- None of the four `prerequisite` texts uses authoring-viewpoint phrasing ("in this task / at the opening").

### prerequisite_sentences

The four-point test on each edge:

| edge | ordering connective | waited-on state (state form) | no tool / id / snake_case | strength = condition |
|---|---|---|---|---|
| P2→P1 | "not … until" | first-night award "stands forfeited with its loss record in its history" (status + certificate_activity) | yes | yes |
| P3→P2 | "only after" | award "stands back in the member's account with its return from the cancelled stay entered in its history" (status issued + release record) | yes | yes |
| P5→P4 | "only after" | replaced award "stands back … with its return from the relocated stay entered in its history" | yes | yes, but see O-6 and G-4 |
| P6→P5 | "not … until" | replacement "stands issued … carrying the number of the award it replaces" | yes ("number" loosely names `replaced_certificate_id`, which is a reference rather than `certificate_number`; O-7) | yes |

The single write that brings about each state, derived as a reader would derive it:

- P2→P1. The waited-on state is a first-night award forfeited with a loss record. Of this difficulty's writes, only P1's rule produces a forfeiture: "the award that pays its first night is forfeited, and its loss record states …". Base no-show and closure forfeitures have no tool here, and their reasons differ. The resolving action is unique: P1's write.
- P3→P2. The waited-on state is the award back in the account with a return from the cancelled stay. The writes that return an award are P2 (cancelled after its deadline) and P4 (relocated stay, not a cancelled stay). A base timely-cancel release would also be "a return from a cancelled stay", but no task tool performs it. For a stay cancelled after its deadline, only P2 applies. Unique.
- P5→P4. The waited-on state is a return from the relocated stay. Only P4 writes a return with reason relocated. Unique.
- P6→P5. The waited-on state is a replacement issued carrying the replaced award's reference. Only P5 issues awards in this difficulty. Unique.

Other checks:

- No rule carries a second wording of its dependency, another problem's tool name or another problem's id.
- The depended-on rules do not restate the blocked sentence. P2.rule does describe its quantity as "the points price at which that returned night stays protected if the member rebooks it", which refers to the rebooking without stating an order.
- No undeclared cross-problem order appears in any extended rule.
- Base rules state no cross-problem order that a tree rests on. Base `certificate_release_and_expiry` says "on a late cancellation or no-show, awards on nights after the first night are released too", which states no order.

### override_declarations

Sentence by sentence against each `base_policy_refs` entry (finding half only):

- **P1** (refs forfeiture, evt_activity_records, redemption_eligibility).
  - forfeiture: the "forfeited only when it pays the first night … after_deadline …" sentence is followed. "Top-off points added to a forfeited award are lost with it" is followed: the tool copies the award's `top_off_points` onto the loss record and posts no redeposit. The closure sentences are not touched.
  - evt_activity_records: "loss records repeat the points price recorded on the hold" is replaced, and the replacement is declared. The reason `cancelled_after_deadline` is followed.
  - redemption_eligibility: the chart-price sentence is used only to define the chart, not overridden.
  - No undeclared override.
- **P2** (refs release_and_expiry, evt_activity_records, forfeiture).
  - Release of later nights on a late cancellation is followed.
  - Both changes to evt_activity_records are declared: the price, and the reason `cancelled_after_deadline` on a release record.
  - "Top-off points come back with the award when top_off_refund_on_release is true" is not overwritten. However, the tool hard-codes `top_off_points=0` on the return record and posts no redeposit. If a later-night award carried a top-off, the tool could not return it. Task 0's later-night award carries 0 top-off, so nothing is demonstrable on either world (O-2).
  - "A released award keeps its original expiry date" is followed (the tool does not touch expiry_date).
- **P3** (refs redemption_eligibility, agg_awards_per_reservation, evt_activity_records).
  - The chart-price-on-hold sentence is replaced, and declared.
  - "when it does [exceed the cap] … the difference is added as top-off points" is inherited. The tool hard-codes top-off 0, so it can only carry a price at or below the cap (O-2). Whether this matters is checked per task.
  - The earliest-night rule is inherited.
- **P4** (refs release_and_expiry, evt_activity_records, reissue).
  - The price clause is declared.
  - Base `certificate_release_and_expiry` reads: "A released award whose expiry date has already passed therefore expires on the day it is released when reinstate_requires_unexpired is true; it is never reinstated for a new stay." P4 handles this quantity, the released award's terminal status, differently. Its tool sets `status="issued"` whatever the expiry date ("Afterwards the award shows back in the member's account"), and P5's prerequisite condition requires "The replaced award's status is issued". P4's `overwrite` does not name this base sentence. **Undeclared override, finding G-4.** Its consequence is demonstrated in the task 1 file.
- **P5** (refs reissue, issuance, agg_multi_holding, release_and_expiry).
  - Both validity clauses are declared.
  - "An award is reissued at most max_reissues_per_award times" and "only when … released because the hotel relocated … and the award's expiry date had passed by the release date" are inherited.
  - "Expiry dates are never extended when extension_allowed is false" is about extending an existing award, not setting a replacement's date, so there is no conflict.
- **P6** (refs redemption_eligibility, agg_awards_per_reservation, evt_activity_records, reissue). The chart-price-on-hold sentence is replaced, and declared. The other sentences are inherited.

I found none of the three disguised forms (anonymous intermediate, 0/1 multiplier, dropped branch). No rule calls base output a "wrong value".

### factor_ladders

| policy | factor | effect | decides | tiers | multi-source | xdiff | rule states every tier |
|---|---|---|---|---|---|---|---|
| P1 | loss_night_season | parameter | lv_season_adj | 3 (+step / −step / 0) | no | booking | yes |
| P1 | loss_award_share | method | lv_share | 3 | no | loyalty | yes |
| P1 | loss_elite_relief | parameter | lv_elite_relief | 3 (2500 / 1000 / 0) | yes (tier AND nights) | loyalty | yes |
| P1 | loss_card_relief | parameter | lv_card_relief | 3 (1500 / 500 / 0) | no | loyalty | yes |
| P2 | return_cancellation_timing | method | rp_basis | 3 (peak+step / peak / hold) | no | booking | yes |
| P2 | return_member_tenure | parameter | rp_tenure_red | 3 (2000 / 1000 / 0) | no | loyalty | yes |
| P2 | return_repeat_returns | parameter | rp_repeat_add | 3 (2500 / 1000 / 0) | no | — | yes |
| P2 | return_card_reduction | parameter | rp_card_red | 3 (1500 / 500 / 0) | no | loyalty | yes |
| P2 | return_elite_nights | parameter | rp_nights_red | 3 (1500 / 500 / 0) | no | loyalty | yes |
| P3 | rebook_night_season | parameter | ap_season_adj | 3 | no | booking | yes |
| P3 | rebook_protection | method | ap_protected | 3 | yes (window AND same/other hotel) | booking | yes |
| P3 | rebook_booking_lead | parameter | ap_lead_red | 3 (1000 / 500 / 0) | no | booking | yes |
| P3 | rebook_member_tier | parameter | ap_tier_red | 3 (3000 / 1500 / 0) | no | loyalty | yes |
| P3 | rebook_recent_stays | parameter | ap_stays_red | 3 (1000 / 500 / 0) | no | loyalty | yes (but see G-2) |
| P3 | rebook_points_nights | parameter | ap_mix_red | 3 (500 / 250 / 0) | no | booking | yes |
| P4 | walk_return_delay | method | rr_basis | 3 (off-peak / standard / hold) | no | booking | yes (boundary O-4) |
| P4 | walk_award_placements | parameter | rr_moves_red | 3 (2500 / 1000 / 0) | no | — | yes |
| P4 | walk_member_tier | parameter | rr_tier_red | 3 (5000 / 2500 / 0) | no | loyalty | yes |
| P4 | walk_earlier_walks | parameter | rr_walks_red | 3 (5000 / 2000 / 0) | no | loyalty | yes |
| P4 | walk_stay_length | parameter | rr_nights_red | 3 (5000 / 2500 / 0) | no | booking | yes |
| P5 | replacement_tier_extra | parameter | rq_tier_months | 3 (3 / 1 / 0) | yes | loyalty | yes |
| P5 | replacement_delay_extra | parameter | rq_delay_months | 3 (2 / 1 / 0) | no | booking | yes |
| P5 | replacement_tenure_extra | parameter | rq_tenure_months | 3 (2 / 1 / 0) | no | loyalty | yes |
| P5 | replacement_stays_extra | parameter | rq_stays_months | 3 (2 / 1 / 0) | no | loyalty | yes (but see G-2) |
| P5 | replacement_moves_extra | parameter | rq_moves_months | 3 (2 / 1 / 0) | no | — | yes |
| P5 | replacement_expiry_day | method | rq_convention | 3 | yes (card AND nights) | loyalty | yes |
| P6 | replacement_night_season | parameter | aq_season_adj | 3 | no | booking | yes |
| P6 | replacement_walk_protection | method | aq_protected | 3 (whole / half / none) | yes (relocated AND same/other brand) | booking | yes |
| P6 | replacement_elite_nights | parameter | aq_nights_red | 3 (3000 / 1500 / 0) | no | loyalty | yes |
| P6 | replacement_points_nights | parameter | aq_points_red | 3 (2000 / 1000 / 0) | no | booking | yes |
| P6 | replacement_booking_lead | parameter | aq_lead_red | 3 (1000 / 500 / 0) | no | booking | yes |

Structural checks:

- Declared counts per policy:
  - P1: 4 (3 parameter, 1 method)
  - P2: 5 (4, 1)
  - P3: 6 (5, 1)
  - P4: 5 (4, 1)
  - P5: 6 (5, 1)
  - P6: 5 (4, 1)
- Every `decides` is an input, never `result`. Binding sets are pairwise disjoint within each policy.
- No two tiers of any ladder select the same value or method as stated.
- Every tier appears in the rule and in compute.
- Every factor's fall-through equals its declared `baseline`. Each `baseline.rule` is a sentence of the rule and gives a definite number: the chart standard price for P1/P3/P6, the standing hold price for P2/P4, and the base validity months on the same day number for P5.
- Labels are honest:
  - Each method factor changes how the input is formed: a basis anchor, a share algorithm, a min with a protected price, a whole/half discount, or a day convention.
  - Each parameter factor substitutes a number.
- Per-chain counts:
  - Multi-source: chain {P1, P2, P3} has loss_elite_relief and rebook_protection. Chain {P4, P5, P6} has replacement_tier_extra, replacement_expiry_day and replacement_walk_protection.
  - Cross-difficulty: both chains read loyalty and booking.

Reality of the ladders, judged by what hotel loyalty programmes actually do:

- Comparable to real practice:
  - Season steps on a category chart. The Ashbury award_chart in loyalty.yaml has exactly these steps: 2500 for categories 1-3, 5000 for 4-6, 10000 for 7 and 15000 for 8.
  - Top-off points lost with a forfeited award.
  - Walk compensation scaled by elite tier and by the length of the walked stay.
  - Goodwill months on a replacement by tier, tenure and the length of the delay.
  - Card-holder and elite-night benefits generally.
  - A points-night count on the same reservation, which is analogous to the charter's own fifth_night_free_on_points.
- Not real. The following are findings, demonstrated below:
  - **G-1 (SOURCE-FACTOR RED, P2 `return_cancellation_timing`): the fall-through is empty and tier 2's condition restates the policy's scope.**
    - P2 applies only to a Reward Night Rate reservation cancelled after its deadline. booking.yaml sets Reward Night Rate `cancellation_deadline_days: 2`, `resort_cancellation_deadline_days: 3` and `cancellation_deadline_time: "23:59"`.
    - booking_cancellation_deadline says "The cancellation is timely only if the moment … is not later than the effective cancellation deadline … cancellation_deadline_time hotel local time on the calendar date obtained by subtracting the effective deadline days … from the arrival date".
    - So a late cancellation is recorded no earlier than arrival−1 at non-resort brands and no earlier than arrival−2 at resort brands. `rp_cancel_days` is therefore always ≤ 2 = `close_cancel_days`.
    - As a result, the tier "a cancellation recorded no more than the close-cancellation days before the arrival date" holds of every customer who reaches this write and did not cancel on the arrival date. The fall-through, "an earlier cancellation protects it at the price on the standing hold", which is also the policy's `baseline.rule`, can be reached by no customer in scope.
    - The ladder really divides customers into two groups, so it has fewer than three real tiers. P2's baseline for this input is a method that the policy's own scope excludes.
    - Bears on task 0.
  - **G-3 (SOURCE-FACTOR RED): conditions or outcomes that no hotel loyalty business weighs or would publish for that quantity.**
    - (a) P1 `loss_elite_relief` and `loss_card_relief`. The "late-cancellation loss value" is a figure written on the loss record only. The award is lost either way, no points are charged or returned, and no other policy reads it. A "relief" for Titanium/Ambassador/Gold/Platinum members or card holders reduces a statement number and changes nothing the member owes or receives. No programme publishes such a treatment.
    - (b) P2 `return_repeat_returns`. This raises a returned night's protected price because the award had earlier come back from cancellations. Every one of those earlier returns was, by base `certificate_release_and_expiry` and `reinstate_on_timely_cancel: true`, a consequence-free timely cancellation ("A released award keeps its original expiry date"). Penalising previous free cancellations contradicts the programme's own existing logic, and no hotel weighs it.
    - (c) P4 `walk_award_placements`. The compensation for a hotel's own failure to honour a reservation grows with how many times the member had placed this award on other reservations in the past year. That is a member-side reshuffling count unrelated to the walk, and no business weighs it for walk protection.
    - (d) P5 `replacement_moves_extra`. A replacement's validity grows with how many times the member cancelled timely and got the award back. Again this rewards the member's own reshuffling, which is unrelated to the relocation that justifies the replacement. Not a real treatment.
    - (e) P3 `rebook_booking_lead`, P6 `replacement_booking_lead` and P3 `rebook_recent_stays`. These are discounts on an award night's points price for booking far in advance, or for the number of paid stays in the past year. A category/season chart programme does not price award nights by booking lead or recent stays. Within this very world, loyalty_award_redemption prices the same Reward Night Rate night paid with points at "the standard-room price of award_chart for the hotel's award_category and the award_season", with no lead or stays term.
    - Bears on task 0 for (a), (b) and (e: P3), and on task 1 for (c), (d) and (e: P6).
  - Observations (fabricated quantities, but directionally coherent loyalty benefits), not grounds for rework:
    - The "protected rebooking price" and "walked-night protected price" as recorded quantities.
    - Tier reductions on award night price (P3, P6), loosely comparable to tier-gated fifth-night benefits.
    - P4's return-delay basis, which compensates for a slow return.
    - P5's convention method, a card-holder month-end benefit (O-8).
- Effect of striking the G-1 and G-3 factors on the declared counts:
  - P1 keeps 2 (season, share), which is below 4 in total and below 2 `parameter`.
  - P2 keeps 3 (tenure, card, nights) with no `method` left.
  - P3 keeps 4 (season, protection, tier, points-nights), which passes.
  - P4 keeps 4, which passes.
  - P5 keeps 5, which passes.
  - P6 keeps 4, which passes.

### findings

- **G-1 — SOURCE-FACTOR RED (unreal ladder: fall-through empty, tier condition restates scope).**
  - Symptom: P2 `return_cancellation_timing` tier 2 and its fall-through/baseline.
  - Root cause: `close_cancel_days: 2` is at or beyond the latest late-cancellation lead time that the Reward Night Rate deadline allows: 2 days at resort brands, 1 day elsewhere.
  - Evidence: P2.rule "a cancellation recorded no more than the close-cancellation days before the arrival date protects it at that category's peak-season price; an earlier cancellation protects it at the price on the standing hold". booking.yaml Reward Night Rate `cancellation_deadline_days: 2`, `resort_cancellation_deadline_days: 3`, `cancellation_deadline_time: "23:59"`. The booking_cancellation_deadline rule, quoted above.
  - Consequence: no reservation in P2's scope can fall through to the baseline method. The factor has two real tiers, and P2's baseline is a straw man for this input.
  - Affected: certificate.extended.yaml P2 params/rule/factors. Task 0.
- **G-2 — SOURCE-POLICY RED (rule admits two readings that compute resolves silently).**
  - Symptom: "counts the stay night credits posted to the membership in the twelve calendar months before the hold/reissue" in P3 and P5.
  - Root cause: "night credits" is this charter's unit of nights (the schema says elite_night_credits = "integer nights … the sum of night credits", and P1, P2, P5 and P6 compare "elite night credits" in nights). Compute counts postings (`XCOUNT`).
  - Evidence: the P3.rule sentence, P3.compute `ap_stays`, the P5.rule sentence, P5.compute `rq_stays`, and db_schema `loyalty_transactions.nights`.
  - Consequence: two values, demonstrated per task. Task 0 P3 and task 1 P5.
- **G-3 — SOURCE-FACTOR RED (conditions or outcomes not held by the line of business).** Factors (a) to (e) above.
  - Affected: certificate.extended.yaml P1, P2, P3, P4, P5 and P6 factor and rule sentences. Task 0 (P1, P2, P3) and task 1 (P4, P5, P6).
- **G-4 — SOURCE-POLICY RED (undeclared override of a base sentence).**
  - Base sentence: base `certificate_release_and_expiry` "A released award whose expiry date has already passed therefore expires on the day it is released when reinstate_requires_unexpired is true; it is never reinstated for a new stay."
  - What the extended side does instead: `release_relocated_award_8143384d` sets status issued ("the award's status becomes issued again … Afterwards the award shows back in the member's account"). P5's prerequisite condition requires "The replaced award's status is issued", and P5's sentence waits on the award "stands back in the member's account".
  - P4.overwrite names only the evt_activity_records price clause.
  - Consequence: demonstrated in task 1, where cf42b0e1's expiry date of 2026-07-09 had passed by the return.
- Observations:
  - O-1: the P3/P6 overlap on a returned replacement.
  - O-2: tools hard-code top-off 0 against the inherited base top-off and redeposit clauses.
  - O-3: CFIELD keys "the new reservation" by status/plan rather than by reservation_id.
  - O-4: P4 leaves exactly 30 days unnamed.
  - O-5: the apply_replacement docstring alludes to issuance.
  - O-6: P5's condition is slightly strengthened.
  - O-7: "number" names a reference.
  - O-8: realism observations listed above.

## closing_checklist

This section was written after both reveals: task 0 at 2026-10-05T13:36:51Z and task 1 at 13:37:09Z. Nothing above this heading was changed after either reveal.

The difficulty is **not closed**. Neither task passes all four relationships.

| item | status |
|---|---|
| Per-task files correspond one-to-one with the tasks (`0.md`, `1.md`), sitting next to this file, with no earlier revision | yes |
| Every comparison section carries a PASS | **no**. Task 0 is SOURCE-POLICY + SOURCE-FACTOR + SOURCE-TASK RED, and so is task 1 |
| Extended policies fully covered and scopes pairwise disjoint | yes. Task 0's charter_scope is {P1, P2, P3} with tools 5a86721d, 2a59ee43 and 7b7c21ba. Task 1's is {P4, P5, P6} with tools 8143384d, 0d99e6ce and 003026b1. They are disjoint and together cover all six policies |
| Task tools and GT closed; uuid8s independently generated | yes (§ action_binding_and_uuids) |
| Each tree has 1–3 prerequisite problems, at least max(n−1, 1) value_input edges, a customer write, and no cycle; the difficulty-wide graph is a DAG | yes. Both tasks have n = 2, 1 value_input edge, and a user apply. The graph is two disjoint chains |
| Every computation has a self-sufficient baseline and 4–6 real factors (2 parameter, 1 method), with ladders that the line of business holds and that bear weight | **no**. G-1 and G-3 strike factors. P1 is left with 2 and P2 with 3 and no method. Every declared factor does move its scored value, and every full-baseline result differs from gold |
| Rule uniquely entails gold | **no**. Under G-2, P3 in task 0 and P5 in task 1 each admit a second value |
| Base sentences that are not overwritten are inherited | **no**. G-4: P4's tool and P5's condition keep a past-expiry relocated award `issued` |
| Instantiation gates re-run on the final form | Not re-run by the auditor, per Step 0. The artifacts are unchanged since the gate snapshot: the charter, tool and task hashes I recomputed at the reveal equal those in HASHES.txt, and the task files were not modified. The orchestrator's snapshot (all seven OK) therefore applies to the audited form |

Per-task verdicts:

- Task 0:
  - SOURCE-POLICY RED (G-2)
  - problem tree PASS
  - SOURCE-FACTOR RED (G-1, G-3 a/b/e)
  - SOURCE-TASK RED (34750 vs 34250)
- Task 1:
  - SOURCE-POLICY RED (G-4, G-2)
  - problem tree PASS
  - SOURCE-FACTOR RED (G-3 c/d/e)
  - SOURCE-TASK RED (2028-03-31 vs 2028-04-30)

---

## revision_2

### charter_global_frozen (revision 2)

- Auditor: claude-opus-5-5, running erl-task-policy-audit. This round re-audits the same difficulty.
- Freeze time: 2026-10-05T16:37Z UTC. This was before any revision-2 task GT was revealed.
- Inputs are new. `certificate.extended.yaml` is sha256 `369eac8fff496d4911a42c36dc7b49581cc84cf9e9f84fe9a30bfa5382411bc8` and `task_tools.py` is `5453ba4ac9185ee3e208317ccf6217754c488eeced793cc4caeb0bc6426f86c3`. Both changed since round 1, so every charter-global section below is re-derived in full rather than carried forward. My recomputed hashes equal those in `/tmp/env0036_views/free_night_award_redemptions/HASHES.txt`.
- Gate snapshot: `/tmp/env0036_views/free_night_award_redemptions/GATES.txt` reports all seven gates OK.
- Masked and not read before the freeze: every field of the revision-2 `tasks/*.json` other than frozen_time, user_scenario and initial_state, plus `tasks/free_night_award_redemptions/worklog.md`, which was updated at 16:10 and is unread.
- contamination_disclosure. This is a re-audit by the round-1 auditor, so I still know the round-1 GT of both tasks: the round-1 values, the target holdings, and the conventions the round-1 compute adopted. No revision-2 GT field was read before this freeze. The reworker's claim list contained item ids only and no values.
- Base copy: the base section of the extended file is byte-identical to `blueprint/products/certificate.yaml`, apart from one trailing blank line.

### policy_conflict_scan (revision 2)

- The chains and targets are unchanged: P1 → forfeit_late_cancel 5a86721d, P2 → release_later_night 2a59ee43, P3 → apply_returned 7b7c21ba (user), P4 → release_relocated 8143384d, P5 → reissue 0d99e6ce, P6 → apply_replacement 003026b1 (user). The edges are still P2→P1, P3→P2, P5→P4 and P6→P5.
- O-1 (the overlap between P3 and P6) is **closed**. P3.rule now says "This rule prices the hold of every award returned from a cancelled stay, a replacement award included once it has come back from a cancelled stay". P6.rule now says "These terms price the first hold of a replacement award; a replacement that later comes back from a cancelled stay is rebooked as any returned award is". The two subjects are now disjoint.
- The P2/P4 release triggers are unchanged and disjoint.
- New observation O-9. The base sentence "A released award whose expiry date has already passed therefore expires on the day it is released …" is overwritten only in P4. P2's release of a later-night award whose expiry passed between its night and the return still falls under the base sentence, yet the P2 tool writes `issued`. No task seeds that case, so the consequence cannot be demonstrated.

### rule_compute_equivalence (revision 2)

- **P1.** Every binding is quoted in the rule.
  - The step bands are stated: cat 8, cat 7, cat 1–3 and cat 4–6. The middle-band default is stated.
  - The three top-off sentences correspond to `lv_topoff`. The three share methods correspond to `lv_share`, keyed on `lv_topped_here`. The result is "the award's share … never below zero".
  - The two sentences "One season step of the award chart is the middle-band step" and "The size of a season step follows the award chart's category bands …" are framed by "change that value as follows", so they read as a baseline followed by its factor. This is O-10, an observation. A reader who takes the first sentence literally hits the rule's own correction two sentences later.
- **P2.** The tiers are now "on the arrival date or later" (`<= 0`), "on the calendar day before" (`== 1`), and "two or more days before" (else). Tenure, tier, card and nights are as stated. The unprompted side change is that `rp_hold` is now the chart price of the returned night, "the award-chart price of the returned night for the category and season recorded on the cancelled reservation", rather than the hold record. That change is equivalent between rule and compute. The binding name `rp_hold` is a leftover and has no effect.
- **P3.** Lead and stays are gone. The card and elite-night reductions are stated and implemented.
  - O-3 is **unchanged**. The CFIELD lookup still keys "the new reservation" by `status='confirmed', variant_name='Reward Night Rate'`.
  - G-2 has **no remaining instance in P3**, because the stays sentence is gone.
- **P4.**
  - The side change: `rr_night` is now the chart price of the walked night, which matches its basis sentence.
  - O-4 is **closed**: the rule now reads "the short-delay days or fewer".
  - T1-O1 is **closed**: the rule now reads "the posting for this relocation included".
  - The elite-night reduction is stated and implemented.
- **P5.**
  - G-2 is **closed**. The rule reads "The stays extra adds up the nights of the stay night credits posted …, card anniversary night credits not counted", and compute uses `XSUM(nights)` filtered to `stay_nights`. One reading now.
  - The walked-stay extra is stated and implemented.
  - The delay extra's new clause "for an award whose history holds that return" is implemented as `rq_reloc_returns >= 1`. See finding R2-F3.
- **P6.**
  - The walk-hold sentence now reads "the price on that award's latest hold, the one for its walked night, less the walked-night protected price on its latest return, the one from the relocated stay". It is implemented as unfiltered `LATEST` on hold and release records, scoped to the computation's holding. The equivalence holds only when the computation's holding is the replaced award, the same caveat as in round 1, and is checked at the reveal.
  - The tier reduction is stated and implemented.

### action_binding_and_uuids (revision 2)

- The `(target_tool, computes)` pairs and the uuid8s are unchanged and distinct. The function bodies still perform no checks.
- O-5 is **closed**. `apply_replacement_award_003026b1.certificate_id` now reads "read from the member's award records before the call".
- `release_relocated_award_8143384d` now says "Afterwards the award stands returned in the member's account, keeping its original expiry date". This matches P4's new overwrite.
- O-2 is **unchanged** (the tools hard-code top-off 0), as the reworker declared.

### prerequisite_graph (revision 2)

- The graph is unchanged and acyclic. Each `policy_source` is still verbatim in its own rule.
  - P6's sentence now reads "carrying the reference of the award it replaces", so O-7 is **closed**.
  - P5's condition now reads "The replaced award stands returned in the member's account and its history carries a return record with the reason that its reservation was relocated", so O-6 is **closed**. It no longer adds the expiry clause or the "status is issued" wording that collided with base.
- `form`, `kind`, `gate` and `resolved_by` are unchanged and valid.

### prerequisite_sentences (revision 2)

- All four edges pass the four-point test, as in round 1, and each still names a state brought about by exactly one write of this difficulty.
- P2→P1: only the P1 forfeit.
- P3→P2: the return from a cancelled stay. Only P2 writes one in this difficulty.
- P5→P4: only P4.
- P6→P5: only P5.

### override_declarations (revision 2)

- **G-4 is closed.** P4.overwrite now names the base sentence "A released award whose expiry date has already passed therefore expires on the day it is released when reinstate_requires_unexpired is true; it is never reinstated for a new stay." It replaces that sentence with "An award that comes back from a relocated stay after its expiry date has passed stands returned in the member's account, usable for no stay, so that its replacement can be deposited against it; the system's own expiry run then closes it as expired, and it is never reinstated for a new stay." The same sentence appears in P4.rule.
  - The merged semantics are unique: the award is `issued` but usable for no stay (base night-within-validity still bars it), and the system later closes it. The tool, the P5 condition and the world's 2024 precedent (closed by the system on the release date) are all compatible with this.
- P1: the reliefs are removed, and the declared override of the price clause stands.
- P2, P3, P5 and P6: their declarations are unchanged. P3 and P6 add scope sentences only.
- P2 does not declare the base past-expiry sentence (O-9). This is not demonstrable on either world.

### factor_ladders (revision 2)

| policy | factor | effect | tiers | multi-source | xdiff |
|---|---|---|---|---|---|
| P1 | loss_night_season | parameter | 3 | no | booking |
| P1 | loss_season_step_band | parameter | 4 (15000 / 10000 / 2500 / 5000) | no | booking |
| P1 | loss_award_share | method | 3 | no | loyalty |
| P1 | loss_topoff_reconciliation | method | 3 | tier 2 is a conjunction | loyalty |
| P2 | return_cancellation_timing | method | 3 (≤0 / =1 / ≥2 days) | no | booking |
| P2 | return_member_tenure | parameter | 3 | no | loyalty |
| P2 | return_member_tier | parameter | 3 (5000 / 2500 / 0) | no | loyalty |
| P2 | return_card_reduction | parameter | 3 | no | loyalty |
| P2 | return_elite_nights | parameter | 3 | no | loyalty |
| P3 | rebook_night_season | parameter | 3 | no | booking |
| P3 | rebook_protection | method | 3 | yes | booking |
| P3 | rebook_member_tier | parameter | 3 | no | loyalty |
| P3 | rebook_card_reduction | parameter | 3 | no | loyalty |
| P3 | rebook_elite_nights | parameter | 3 | no | loyalty |
| P3 | rebook_points_nights | parameter | 3 | no | booking |
| P4 | walk_return_delay | method | 3 | no | booking |
| P4 | walk_member_tier | parameter | 3 | no | loyalty |
| P4 | walk_relocations_compensated | parameter | 3 | no | loyalty |
| P4 | walk_stay_length | parameter | 3 | no | booking |
| P4 | walk_elite_nights | parameter | 3 | no | loyalty |
| P5 | replacement_tier_extra | parameter | 3 | yes | loyalty |
| P5 | replacement_delay_extra | parameter | 3 | yes as declared (see R2-F3) | booking |
| P5 | replacement_tenure_extra | parameter | 3 | no | loyalty |
| P5 | replacement_stays_extra | parameter | 3 | no | loyalty |
| P5 | replacement_walked_stay_extra | parameter | 3 | no | booking |
| P5 | replacement_expiry_day | method | 3 | yes | loyalty |
| P6 | replacement_night_season | parameter | 3 | no | booking |
| P6 | replacement_walk_protection | method | 3 | yes as declared (see R2-F2) | booking |
| P6 | replacement_elite_nights | parameter | 3 | no | loyalty |
| P6 | replacement_points_nights | parameter | 3 | no | booking |
| P6 | replacement_member_tier | parameter | 3 | no | loyalty |

Declared counts:

- P1: 4 (2 parameter, 2 method)
- P2: 5 (4 parameter, 1 method)
- P3: 6 (5 parameter, 1 method)
- P4: 5 (4 parameter, 1 method)
- P5: 6 (5 parameter, 1 method)
- P6: 5 (4 parameter, 1 method)

Every fall-through equals its declared baseline. Every tier is in both the rule and compute.

Status of the round-1 ladder findings:

- **G-1 is closed.** P2's timing tiers are now arrival day or later, the day before, and two or more days before.
  - The second tier, "on the calendar day before the arrival date", no longer holds of every late canceller.
  - The fall-through is reachable at Ashbury Resort & Spa and Ashbury Reserve. Their deadline is arrival − 3 days at 23:59, so a late cancellation can be recorded at arrival − 2.
  - The first tier is reachable: booking_cancellation_deadline says "may be cancelled … at any time before arrival", which includes the arrival date.
- **G-3 (a) is closed.** The P1 elite and card reliefs are removed.
- **G-3 (b) is closed.** P2 return_repeat_returns is removed.
- **G-3 (c) is closed.** P4 walk_award_placements is removed.
- **G-3 (d) is closed.** P5 replacement_moves_extra is removed.
- **G-3 (e) is closed.** P3 lead and stays are removed, and P6 lead is removed.
- The replacement factors are realistic loyalty benefits, and I record them as O-8-class observations only. They are:
  - tier, card and elite-night reductions in P2, P3, P4 and P6;
  - walked-stay months in P5;
  - P1's step band, which follows the real award_chart of loyalty.yaml.

New ladder findings:

- **R2-F1 — SOURCE-FACTOR RED: P1 `loss_topoff_reconciliation` is one method written as three tiers.**
  - Tier 1 counts "the top-off deducted for the cancelled reservation, less any returned for it". Tier 2, which applies only when the award was topped off for that reservation alone, counts "deducted less returned". The fall-through counts "all the top-off deducted".
  - Under each tier's own condition, all three equal top-off deducted for the cancelled reservation less top-off returned for it.
    - In tier 2, "topped off only for that reservation" makes total deducted equal deducted-for-it.
    - In the fall-through, wherever the value is used (`lv_topped_here ≥ 1`), deducted-for-it equals total deducted and nothing was returned.
  - I checked this exhaustively over a 0–40000 grid of (deducted in total, deducted for the reservation, returned for it). In every case where the binding is used, the compute equals `lv_ded_res − lv_ret_res`. There were 0 exceptions.
  - The ladder therefore selects one method, and its tiers are a case split rather than distinct treatments. Its only effect is its baseline, `lv_ded_all`, which counts top-off already refunded on another reservation. It is a near-miss presented as a factor.
  - Striking it leaves P1 with 3 factors, below 4.
  - This defect was introduced by the rework, as the replacement for G-3 (a).
- **R2-F2 — SOURCE-FACTOR RED: P6 `replacement_walk_protection` has an empty fall-through, and its shared condition restates scope.**
  - Base certificate_reissue says: "A replacement award is reissued only when an award was released because the hotel relocated its reservation … and guest services issues no award outside this rule."
  - So every replacement that reaches P6's write replaces an award that "came back from a relocated stay". The conjunct shared by tiers 1 and 2 holds for every customer in scope, and "otherwise: the night keeps its price", which is also the baseline, cannot be reached.
  - The ladder has two real tiers, same brand and other brand.
  - This is pre-existing: it was present in round 1 unchanged and I missed it then. It is reported now.
- **R2-F3 — SOURCE-FACTOR RED: P5 `replacement_delay_extra` has a filler conjunct.**
  - The new conjunct "the award's history holds its return from the relocated stay" holds for every customer who reaches P5's write. P5's own prerequisite sentence requires that return before the expiry is set, and base reissue requires the release.
  - Taken on its own, that part of the compound condition restates scope. The factor's multi-source label is decorative.
  - Without the conjunct the factor is a valid three-tier ladder, so the counts are unaffected.
  - This defect was introduced by the rework.
- **R2-F4 — SOURCE-FACTOR RED, to be demonstrated per task: P2's computation has no near-miss.**
  - After the rework, P2 reads only single fields by inspection: the cancelled reservation's category, season, cancelled_at and arrival, plus the membership's enrolment date, tier, card and elite_night_credits.
  - No aggregate or history row remains through which a record could be counted by a careless reader and excluded by the rule.
  - The near-miss P2 had in round 1 (earlier returns in the award's history) went with return_repeat_returns.
  - This is a regression introduced by the rework, and it is confirmed on task 0's world in `0.md` revision 2.

Counts after striking R2-F1:

- P1: 3, which fails the minimum of 4.
- P2: 5, which passes the count but fails the near-miss test.
- P3: 6, which passes.
- P4: 5, which passes.
- P5: 6, which passes (R2-F3 voids only the multi-source label).
- P6: 5, which passes, but R2-F2 leaves the method factor with two real tiers. That falls below the three-tier minimum, so P6 has 0 valid `method` factors.

### findings (revision 2)

Status of the round-1 items:

- G-1: closed.
- G-2: closed (P3's sentence is removed; P5 is now unambiguous).
- G-3 (a) to (e): closed.
- G-4: closed.
- O-1, O-4, O-5, O-6, O-7, T1-O1: closed.
- O-2, O-3: unchanged, with no demonstrated consequence.
- O-8: unchanged, as realism observations.

New items:

- R2-F1: new, P1, bears on task 0.
- R2-F2: pre-existing, missed in round 1, P6, bears on task 1.
- R2-F3: new, P5, bears on task 1.
- R2-F4: regression, P2, bears on task 0.
- O-9: observation, P2 past-expiry release.
- O-10: observation, P1 step sentences.

## closing_checklist (revision 2)

This checklist was written after the revision-2 reveals at 2026-10-05T16:38:05Z. The revision-2 charter-global section above was frozen before those reveals and has not been edited since.

**The difficulty is not closed.**

| item | status |
|---|---|
| Per-task files are one-to-one with the tasks; revision 1 is preserved untouched; revision 2 is appended | yes |
| Every comparison carries a PASS | **no**. Both tasks are SOURCE-FACTOR RED. Policy self-consistency, problem tree and unique solution PASS in both. |
| Extended policies fully covered; scopes disjoint | yes. Task 0 covers {P1, P2, P3} and task 1 covers {P4, P5, P6}. The tools are disjoint. |
| uuid8s independent; task tools and GT closed | yes |
| Trees: 1–3 prerequisites, enough value_input edges, a customer write, acyclic; the difficulty graph is a DAG | yes |
| Factors: 4–6 real factors per computation (≥2 parameter, ≥1 method), each bearing weight, each ladder real, with a near-miss per computation | **no**. See the factor findings below. |
| Round-1 REDs closed | yes. G-1, G-2, G-3 (a)–(e) and G-4 are closed. O-1, O-4, O-5, O-6, O-7 and T1-O1 are closed. O-2, O-3 and O-8 are unchanged, as declared. |
| Regressions | R2-F4 (P2 lost its only near-miss source) |
| Gates re-run on the final form | Not re-run by the auditor. The revealed task hashes and the charter/tool hashes are the ones the orchestrator's revision-2 gate snapshot (all seven OK) ran on, with no edits since. |

Factor findings blocking closure:

- R2-F1: P1 is down to 3 factors.
- R2-F2: P6 has no valid method factor.
- R2-F3: P5's delay extra has a filler conjunct.
- R2-F4: P2 has no near-miss.

---

## revision_3

### charter_global_frozen (revision 3)

- Auditor: claude-opus-5-5 (erl-task-policy-audit), third round. Freeze time: 2026-10-05T23:36Z UTC, before any revision-3 task GT was revealed.
- Inputs:
  - `certificate.extended.yaml` sha256 `4b26e02878ab8aa2b82684b3f175fd3b32632a5400765a26bda8d511f9a96457` (changed since revision 2, so the charter-global sections are re-derived).
  - `task_tools.py` `5453ba4ac9185ee3e208317ccf6217754c488eeced793cc4caeb0bc6426f86c3` (unchanged, so action_binding_and_uuids is carried forward from revision 2 on the strength of that hash).
  - Both hashes equal HASHES.txt.
  - GATES.txt: all seven OK.
  - The base copy is still verbatim.
- Masked fields were not read before the freeze.
- contamination_disclosure:
  - As the auditor of rounds 1 and 2, I know the revision-1 and revision-2 GT of both tasks.
  - Task 0's world is unchanged since revision 2. Several revision-3 values on it coincide with revision-2 gold I have already seen, so the independence of my task-0 derivation is limited.
  - No revision-3 GT field was read before this freeze.
  - The worklog was not read.

### changes verified (revision 3)

- **R2-F1 closed.** P1's top-off reconciliation factor is removed. The top-off counted is now a single sentence: "it is the top-off deducted for the cancelled reservation less any top-off returned for that reservation; top-off deducted for or returned on any other reservation of the award never counts". It is implemented as the binding `lv_topoff = lv_ded_res − lv_ret_res`, not as a factor. Its replacement factor is `loss_cancellation_timing` (method; see R3-F1 and R3-F2).
- **R2-F2 closed.** P6 walk protection is now three tiers: "at the very hotel that relocated the stay" (protected price itself), "another hotel of the same brand" (whole discount), and "otherwise, at a hotel of another brand" (the standard half discount).
  - The baseline is now that half-discount standard, and the sentence "As the standard, half the walked-night discount … is taken off" appears in both the rule and baseline.rule.
  - All three tiers are reachable, and none holds for every replacement.
  - The vacuous "came back from a relocated stay" conjunct is gone. `aq_walk_protected` is guarded to None when there is no relocated return, which the prerequisite makes unreachable at handling time.
- **R2-F3 closed.** P5's delay extra no longer carries the history conjunct. Its ladder is ≥3 months / ≥1 month / otherwise. The guard on `rq_return_date` is computational only.
- **R2-F4 closed.** P2's night reduction now reads "the elite night credits posted to the member's Ashbury Rewards account in the last twelve months … stay credits and card anniversary credits alike; a year-end reset of the night count is not a credit and takes nothing away, and the membership's count for the current calendar year is not the measure". Compute is `XSUM(loyalty_night_credit nights, within_months=12)`. That puts the reset row and credits older than 12 months into the computation as near-miss candidates, demonstrated per task.
- **O-9 closed.** P2.rule now says: "This rule returns only a later-night award whose expiry date has not passed on the day of the return; one whose expiry date has passed expires as the release rule sets and is not returned here." This is consistent with the inherited base sentence.
- **O-10 closed.** "Unless the category band sets another size, one season step of the award chart is the middle-band step" now frames the default.
- **Unchanged and re-checked:**
  - P3 and P4 compute are identical to revision 2. Their rules still match.
  - The prerequisite graph and sentences are unchanged and pass. The four state-form edges each have exactly one resolving write.
  - O-2 and O-3 are unchanged.
- Factor counts as declared (all ladders ≥3 tiers, all fall-throughs equal their baselines):
  - P1: 4 (2 parameter, 2 method)
  - P2: 5 (4, 1)
  - P3: 6 (5, 1)
  - P4: 5 (4, 1)
  - P5: 6 (5, 1)
  - P6: 5 (4, 1)

### new findings (revision 3)

- **R3-F1 — SOURCE-POLICY RED (P1 contradicts itself). New, introduced with the R2-F1 rework.**
  - P1.rule defines the quantity as "the late-cancellation loss value: the points value of the forfeited night that the award itself is counted as having lost, apart from any top-off points the member had added".
  - The new timing tier says "a cancellation recorded on the arrival date or later is handled as a no-show of the first night and loses the whole night price, the top-off included".
  - Take one situation: a capped award topped off for the cancelled reservation, cancelled on the arrival date.
    - The definition gives the night price less the top-off.
    - The tier gives the whole night price including the top-off.
  - In addition, `forfeit_late_cancel_award_5a86721d` copies the award's `top_off_points` onto the same loss entry ("the top-off points the award carried"). Under the tier, that top-off is recorded twice.
  - The two passages reach different values in that one situation.
  - Task 0's cancellation falls the day before arrival, so it sits on tier 1 and its scored value is unaffected (see `0.md` revision 3).
- **R3-F2 — SOURCE-FACTOR RED (P1 `loss_cancellation_timing` middle tier is not real). New. The reworker flagged it for judgement.**
  - The tier reads: "a cancellation recorded two or more days before the arrival date, which only a deadline further out than one day makes late, loses the award's share less one season step, the night being released early enough to be resold".
  - The award is forfeited whole in every late cancellation (base certificate_forfeiture). This world's own late-cancellation rule says the opposite of a resale credit. booking_late_cancellation_penalty: "Under first_night_points no cash penalty is charged: the points or the Free Night Award paying the first night are retained". The group charter sets `resell_credit_applies: false`. The blueprint lists "crediting resold rooms" among requests outside policy.
  - Hotel loyalty programmes do not restate a forfeited award's value because the hotel may resell the room. The member loses the same award whatever the hotel does with the room.
  - The tier's treatment, a season step off the recorded loss for resale, has no counterpart in real practice and contradicts the world's own logic.
  - With this factor struck, P1 has 3 factors, below 4. This fails the count, so the P1 computation remains SOURCE-FACTOR RED.
- Observation **O-11**: the tier "handled as a no-show of the first night" says nothing about the loss record's reason. The tool hard-codes `cancelled_after_deadline`, so there is no agent choice and no consequence.

### status table (revision 3)

| item | status |
|---|---|
| R2-F1 | closed (but its replacement introduced R3-F1 and R3-F2) |
| R2-F2 | closed (task 1 world rebooked to Ashbury Resort & Spa PSRSP so the tier taken is not the fall-through) |
| R2-F3 | closed |
| R2-F4 | closed (per-task near-miss shown in `0.md` revision 3) |
| O-9, O-10 | closed |
| O-2, O-3, O-8 | unchanged; no consequence |
| R3-F1 | new, SOURCE-POLICY RED (P1) |
| R3-F2 | new, SOURCE-FACTOR RED (P1) |
| O-11 | new observation |

## closing_checklist (revision 3)

Written after the revision-3 reveals at 2026-10-05T23:36:49Z. The revision-3 charter-global section above was frozen before those reveals and has not been edited.

**The difficulty is not closed.**

| item | status |
|---|---|
| Per-task files one-to-one with the tasks; revisions 1 and 2 untouched; revision 3 appended | yes |
| Every comparison carries a PASS | **no**. Task 0 is SOURCE-POLICY RED + SOURCE-FACTOR RED. Task 1 PASSES on all four relationships. |
| Scopes disjoint and complete; tools closed; uuid8s independent | yes. Task 0 covers {P1, P2, P3}, task 1 covers {P4, P5, P6}. The tool module is unchanged. |
| Trees: 1–3 prerequisites, enough value_input edges, a customer write, acyclic; the difficulty graph is a DAG | yes |
| Factors: 4–6 real factors per computation, bearing weight, with real ladders and a near-miss each | **no**. P1 falls to 3 once R3-F2 is struck. P2–P6 pass. |
| Round-2 REDs closed | yes: R2-F1, R2-F2, R2-F3, R2-F4. O-9 and O-10 are also closed. |
| New defects | R3-F1 (SOURCE-POLICY, P1) and R3-F2 (SOURCE-FACTOR, P1). Both came in with the R2-F1 rework. |
| Regressions | none found in P2–P6 or the tool module |
| Gates on the final form | Not re-run by the auditor. The orchestrator's revision-3 snapshot (all seven OK) covers the charter, tool and view hashes audited here. |

---

## revision_4

### charter_global_frozen (revision 4)

- Auditor: claude-opus-5-5 (erl-task-policy-audit), round 4. Freeze time: 2026-10-05T23:58Z UTC, before any revision-4 task GT was revealed.
- Inputs and carry-forward:
  - `certificate.extended.yaml` sha256 is `fd73a514d5f3e1f004874fba8e2ba4237fd2fbba90c15a71b96f21d09fe14e2a`. It changed, so P1 is re-derived in full.
  - `task_tools.py` `5453ba4a…6c3` is unchanged, so action_binding_and_uuids carries forward on that hash.
  - Both views are unchanged since revision 3.
  - GATES.txt shows all seven gates OK.
  - The base copy is still verbatim.
- Per-policy fingerprints for later rounds (sha256[:10] of rule / compute / factors / prerequisite):

  | policy | rule | compute | factors | prerequisite |
  |---|---|---|---|---|
  | P1 | da7fc93335 | cbea69ca9f | 9c4a0e5b66 | 4f53cda18c |
  | P2 | 608223e43d | 08d009b555 | 152478ffe0 | bcf674fa3b |
  | P3 | f8289c00b8 | 33892bc60d | bb29eb05e3 | a82f2f770a |
  | P4 | 74fa4b0ad8 | 6d2793fa95 | 41a5bda525 | 4f53cda18c |
  | P5 | b5857bf6a1 | b31f082f1b | 9c106118e1 | 1498079cb3 |
  | P6 | 888055694b | ce6e72b74c | 2b26ecc99e | 49d040a99f |

- "P2–P6 untouched" is the reworker's claim. I kept no round-3 per-policy hashes, so I checked it by re-reading P2–P6 and re-evaluating them on both worlds. Every result and every factor substitution equals revision 3, figure for figure. I found no textual change in their factor lists or prerequisites.
- contamination_disclosure: as auditor of rounds 1–3, I know the earlier GT. Both worlds are unchanged. Every revision-4 value except P1's factor substitutions equals revision-3 gold I have already seen. No revision-4 GT was read before this freeze.

### changes verified (revision 4)

- **R3-F2 closed.** `loss_cancellation_timing`, including its resale tier, is removed. P1 no longer reads cancelled_at.
- **R3-F1 closed.**
  - The definition now reads "apart from any top-off points the member had added, which are lost with the award and recorded on the loss entry as its top-off".
  - The arrival-date "top-off included" tier is gone.
  - The tool's copying of `top_off_points` onto the loss entry now matches the rule.
  - No sentence of P1 contradicts another.
- **O-11 closed**, because its tier no longer exists.
- P1's rule and compute are equivalent:
  - `lv_std` comes from the eight-category sentence.
  - `lv_step` comes from the band sentence, through the duplicate binding `lv_band_cat`, which reads the same field.
  - Share and top-off are as before.

### new findings (revision 4)

**R4-F1 — SOURCE-FACTOR RED: the new P1 `loss_night_category` has a baseline that its own baseline.rule does not state, and the factor is decoration.**

- The factor's baseline binding is `lv_std: K('chart_std_cat4')`, the category-4 price for every hotel.
- baseline.rule reads: "The award chart's standard-season prices by category are those of the Ashbury Rewards award chart. … Unless the award category recorded on the cancelled reservation sets another price, the late-cancellation loss value is the category-4 standard-season price of the award chart."
- Every reservation records an award category, since `booking_reservations.award_category` is an enum 1–8, and baseline.rule itself names the chart that prices each one. So a reader of baseline.rule alone already arrives at the recorded category's own price. For the hotel in question that is the chart's standard price, which is exactly the factor's tier value. The category-4 binding is never reached.
- The inherited base rule `certificate_redemption_eligibility` reads: "The night's price is the standard-room points price of the Ashbury Rewards award chart for the reservation's award_category and award_season". The visible `loyalty_award_redemption` rule says the same.
- So the baseline binding is a straw man that no reader would choose. The "factor" restates the base chart lookup. Where baseline.rule alone is applied, it gives the scored input, so the factor bears no weight against an honest baseline.
- This is new in revision 4.

**R4-F2 — SOURCE-FACTOR RED: P1 `loss_season_step_band`, by the same mechanism. It entered in revision 3 with the O-10 rewording, and I missed it in round 3.**

- Since revision 3, baseline.rule reads: "Unless the category band sets another size, one season step of the award chart is the middle-band step."
- The chart that baseline.rule names gives every category its own step: 2500 / 5000 / 10000 / 15000 in loyalty `award_chart`. Every other extended policy also states "A category's season step is the gap between its neighbouring seasons on that chart".
- So baseline.rule alone either yields the recorded category's true step, which is the factor's tier value, or it is not self-sufficient, because "unless … sets another size" points at a band the baseline does not define. Either way the factor's binding baseline of `K('season_step_cat4_6')` for every category is not what baseline.rule states.
- In revision 2 the sentence was unconditional, "One season step of the award chart is the middle-band step". That made a coherent default, and I had accepted the factor on that basis. The revision-3 change, which I recorded as closing O-10, removed that coherence, and I did not catch it then.

**Count after striking R4-F1 and R4-F2:** P1 is left with `loss_night_season` (parameter) and `loss_award_share` (method), so 2 factors. That is below 4, and it has only 1 `parameter`. **The P1 computation is SOURCE-FACTOR RED.**

**P2–P6:** no new defects. Their revision-3 PASS conclusions carry forward, unchanged per the check above.

### status table (revision 4)

| item | status |
|---|---|
| R3-F1 | closed |
| R3-F2 | closed |
| O-11 | closed |
| R4-F1 | new, SOURCE-FACTOR RED, P1 (task 0) |
| R4-F2 | SOURCE-FACTOR RED, P1 (task 0); introduced in revision 3, missed in my round-3 audit |
| O-2, O-3, O-8 | unchanged; no consequence |

## closing_checklist (revision 4)

This checklist was written after the revision-4 reveal at 2026-10-05T23:58:18Z. The revision-4 charter-global section above is unedited since its freeze.

**The difficulty is not closed.**

| item | status |
|---|---|
| Per-task files one-to-one with the tasks; revisions 1–3 untouched; revision 4 appended | yes |
| Every comparison carries a PASS | **no**. Task 0 is SOURCE-FACTOR RED (R4-F1, R4-F2). Task 1 PASSES. |
| Scope, tools, uuid8s, trees, DAG | yes (unchanged) |
| Factors: 4–6 real factors per computation with honest baselines | **no**. P1 has 2 real factors. P2–P6 pass. |
| Round-3 REDs | R3-F1, R3-F2 and O-11 are closed. |
| New or missed defects | R4-F1 is new. R4-F2 was introduced in revision 3 and missed by this auditor in round 3. |
| Regressions in P2–P6 | none (behavioural re-evaluation on both worlds is identical; fingerprints are recorded for future rounds) |
| Gates on the final form | The orchestrator's revision-4 snapshot shows all seven OK. Not re-run by the auditor. |

---

## revision_5

### charter_global_frozen (revision 5)

- Auditor: claude-opus-5-5 (erl-task-policy-audit), round 5. Freeze time: 2026-10-06T00:36Z UTC, before any revision-5 GT was revealed.
- Input hashes, all equal to HASHES.txt:
  - `certificate.extended.yaml`: `0b506d9a5ba65547cb5327f20faa038c3214e4f4de676e834064d9ab068a1a16`
  - `task_tools.py`: `27a6526d529be10fd03a29b7a6bde5ad5a6270ad9b73a027e9b86a2b844aaeaf`
  - task_0 view: `d72d191b…8ee3d`
  - task_1 view: `91c64dae…f0b` (unchanged)
- GATES.txt: all seven OK. The base copy is still verbatim.
- Per-policy fingerprints compared with revision 4:
  - P3, P4, P5 and P6 are **identical** in rule, compute, factors and prerequisite (f8289c00b8/33892bc60d/…, 74fa4b0ad8/…, b5857bf6a1/…, 888055694b/…). Their revision-3/4 conclusions carry forward on those fingerprints.
  - P1 changed: rule 9df53accfd, compute 67f6596937, factors a74baacb63; prerequisite unchanged.
  - P2 changed: rule c56604ec01, compute 519adf057e, factors d3514e2bd5; prerequisite unchanged (bcf674fa3b).
- Tools: only the docstring of `forfeit_late_cancel_award_5a86721d` changed. It now says "the stay's protected value given here", which matches P1. The body, uuid8s and other tools are unchanged, and no ordering language or tool names were added.
- contamination_disclosure: I know all earlier GT. Task 1's world and its policies are unchanged, so its values equal revision-4 gold. For task 0, the P2 and P3 values equal revision-4 gold; only P1's value is new to me. No revision-5 GT was read before this freeze.

### changes verified (revision 5)

**R4-F1 closed.** The `loss_night_category` factor is removed.
- The category price is plain compute that every tier shares: "The stay's protected value is the standard-season price of the award chart for the award category recorded on the cancelled reservation".
- The baseline.rule now states exactly this and is self-sufficient.

**R4-F2 closed.** The `loss_season_step_band` factor is removed.
- The step is now plain compute: "a category's season step is the gap between its neighbouring seasons on the award chart".
- The "unless … sets another size" sentence is gone.

**What P1 scores now.** The quantity is "the stay's protected value: the points value at which the late-cancelled stay stays protected for the member, set from what the forfeited award itself carried for that night, apart from any top-off points … recorded on the loss entry as its top-off". P1 has four factors:

| factor | effect | ladder |
|---|---|---|
| season | parameter | ±step / 0 |
| award share | method | 3 tiers, unchanged |
| stay length | parameter | ≥3 / ≥2 / one-night |
| stay-credit nights | parameter | ≥40 / ≥20 / fewer; stay_nights only, 12 months, card credits excluded |

- That is 3 parameter + 1 method, with every tier stated in the rule and in compute.
- Each fall-through equals its declared baseline (0, lv_night, 0, 0), and the baselines are honest.
- No sentence contradicts another; the R3-F1 wording is kept.

**P2 now consumes P1.** The fall-through of `return_cancellation_timing` (two or more days before arrival) and the P2 baseline.rule are both "the stay's protected value recorded on the loss record of the stay's first-night award". Night thresholds changed to 60 and 30.
- Rule and compute are equivalent only if the computation's holding is the first-night award. The binding `LATEST(certificate_activity …, event_type='certificate_forfeit_record', reservation_id=F('reservation_id'))` is scoped by the DSL to `certificate_id = HID`.
- With the later-night award as the holding (the award P2 actually writes), the lookup finds nothing. The fall-through and the baseline substitution then fail to evaluate (TypeError, recomputed).
- This is the same kind of caveat as P6's in revision 1, and it is checked at the reveal against `target_holding_id`.
- If the holding there is the first-night award, P2 is equivalent to its rule.

**Realism.** The stay-length and stay-credit reductions are frequent-guest benefits of the O-8 class. A lower protected value favours the member: P3 prices a rebook at "the lower of its price and the protected rebooking price". These are observations, not RED.

### new observations (revision 5)

- **O-12.** On any world where a late cancellation is recorded two or more days out, P2's scored value reads P1's written value. The P2→P1 edge then carries a value while being declared `state_gate`. The declared gate (first-night award status) is real and unmet at the opening, so this is not a mismatch. It is recorded only because the edge kind understates the dependency on such worlds.
- **O-13 (base issuance seed gap, task 1; the reworker self-reported it). I missed this in rounds 1–4.**
  - Task 1's membership 288398a0 reaches 50 elite night credits in 2026 on 2026-07-06 (8+7+9+6+25). Base certificate_issuance says "An elite_milestone award is deposited once per calendar year on the day the member's elite night credits for the year first reach the type's milestone_nights … within issue_within_days", which is 10 days for the 40K award.
  - The seed holds no 2026 40K milestone award.
  - No computation reads award holdings, the persona raises no issuance question, and the agent "need only act within the scope of the user's need". So no gold value, write or second answer is affected. The skill makes an undemonstrable defect an observation, not RED.
  - Task 0 had the same gap through revision 4 (52 credits by 2026-07-10, no 2026 milestone award). Revision 5 fills it with 43be35a5, a 40K, elite_milestone, issued 2026-07-13, expiring 2027-07-13. That is consistent with base (deposited 3 days after the qualifying date, 12-month validity). I missed that gap too in rounds 2–4.

### status table (revision 5)

| item | status |
|---|---|
| R4-F1 | closed |
| R4-F2 | closed |
| P1 rewrite | 4 real factors; no new RED found |
| P2 change | caveat on the target holding, checked at the reveal |
| O-12, O-13 | new observations (O-13 is pre-existing in task 1) |
| P3–P6, tool bodies | unchanged (fingerprints) |

## closing_checklist (revision 5)

Written after the revision-5 reveal (2026-10-06T00:37:02Z). The revision-5 charter-global section above has not been edited since its freeze.

**The difficulty passes the source-layer audit at revision 5.**

| item | status |
|---|---|
| Per-task files one-to-one with the tasks; revisions 1–4 untouched; revision 5 appended | yes |
| Every comparison carries a PASS | yes. Task 0 PASS; task 1 PASS. |
| Extended policies fully covered; scopes pairwise disjoint (task 0 {P1, P2, P3}, task 1 {P4, P5, P6}) | yes |
| Task tools and GT closed; uuid8s independent and frozen | yes (bodies unchanged since revision 1; one docstring aligned with P1) |
| Each tree has 2 prerequisite problems, 1 value_input edge (≥ max(n−1, 1)), a customer write, and no cycle; the difficulty graph is a DAG | yes |
| Every computation has a self-sufficient baseline and 4–6 real factors (≥2 parameter, ≥1 method), with real ladders, weight on its world, a near-miss, and a baseline result differing from gold. Per task: ≥1 multi-source factor (task 0 rebook_protection; task 1 tier_extra, expiry_day, walk protection) and ≥1 cross-difficulty factor | yes. Factor counts per policy (parameter + method): P1 4 (3+1), P2 5 (4+1), P3 6 (5+1), P4 5 (4+1), P5 6 (5+1), P6 5 (4+1). |
| Round-4 REDs (R4-F1, R4-F2) | closed |
| Regressions | none. P3–P6 are fingerprint-identical; the P1/P2 changes are verified above. |
| Open observations (not grounds for rework) | O-2 (tools hard-code top-off 0; no gold consequence), O-3 (CFIELD keys "the new reservation" by status), O-8 (fabricated protected-price quantities, directionally coherent), O-12 (P2→P1 carries a value on ≥2-day worlds), O-13 (task 1 seed lacks the owed 2026 milestone award; no gold consequence) |
| Instantiation gates on the final form | The orchestrator's revision-5 snapshot (all seven OK) covers exactly the hashes audited here. I did not re-run them, per Step 0. |
