# Policy-task audit — pass_membership_billing_and_benefits / charter-global

## charter_global_frozen

- Freeze time: 2026-10-11T11:54:30Z (file mtime) (written before any task's GT was revealed; nothing in this section is derived from a revealed GT).
- Auditor: independent policy-task auditor (erl-task-policy-audit), revision 1 (no earlier revision exists for this difficulty).
- Frozen inputs (sha256 re-computed by the auditor, equal to the coordinator's HASHES.txt):
  - `tasks/pass_membership_billing_and_benefits/pass.extended.yaml` = `c5a6e9e750d285d8c24dbc41a8e45e625d4d8cc58b7d776fa24464336e6199d4`
  - `tasks/pass_membership_billing_and_benefits/task_tools.py` = `8881c405c91bae7956fdb24f21eaa17239b0c03690ccf328182333e722837767`
- Fields permitted: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/pass.yaml` (and, as the cross-category charters the extended computes read, `blueprint/products/trip.yaml` and `blueprint/products/earnings.yaml`), the extended charter, `task_tools.py`, the DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (`build_env`, `MONTHS`, `DAYS`, `RND`), and the masked views `0.view.json` / `1.view.json` (frozen_time, user_scenario, initial_state only).
- Fields explicitly masked until every task derivation was frozen: `evaluation_criteria`, `computations`, `prerequisite_closure`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `db_closure*`, the worklog, other audits.
- Entry conditions (Step 0): the coordinator's gate snapshot came with the brief (check_extended / check_task_tools / replay_tasks / check_solvability / check_compute / check_grounding / check_cross_fire all rc=0; check_traceability deferred to render). Masked views supplied with hashes; re-hashed and equal. Entry conditions met. The coordinator's rewrite of `share_tools.verify_customer_identity` (`matched = sum(...)`) was read and is behaviourally equivalent; not a finding.

### policy_conflict_scan

Extended policies (6) and their claims:

| policy | subject | target_tool (owner) | computes | task |
| --- | --- | --- | --- | --- |
| pass_ext_restoration_payment | pass_fee_charge, pass_payment_recover | restore_past_due_pass_5ad4a609 (user) | amount | 0 (prereq) |
| pass_ext_plus_monthly_upgrade_charge | pass_plan_change, pass_fee_charge | upgrade_pass_to_plus_monthly_9f7c0895 (user) | proration_charge | 0 (root) |
| pass_ext_trip_credit_posting | pass_credit_earn | post_pass_ride_credit_f79e4c68 (agent) | amount | 1 (prereq) |
| pass_ext_refunded_fare_credit_forfeit | pass_credit_forfeit | forfeit_pass_ride_credit_4b5902d4 (agent) | amount | 1 (prereq) |
| pass_ext_upgrade_window_refund | pass_fee_refund | refund_pass_period_fee_d96d0945 (agent) | amount | 1 (prereq) |
| pass_ext_all_access_upgrade_charge | pass_plan_change, pass_fee_charge | upgrade_pass_to_all_access_2d51c03c (user) | proration_charge | 1 (root) |

- Base copy: lines 1-1055 of the extended file are byte-identical to `blueprint/products/pass.yaml` (`diff` empty).
- Scopes: task 0 = {restoration_payment, plus_monthly_upgrade_charge}; task 1 = {trip_credit_posting, refunded_fare_credit_forfeit, upgrade_window_refund, all_access_upgrade_charge}. Pairwise disjoint and jointly cover all six extended policies (the scope labels in the yaml comments agree). Claimed event types pass_cancel_now / pass_auto_renew_off / pass_auto_renew_on / pass_pause_schedule are not written by any extended policy (observation only; not a relationship of this audit).
- Overlapping subjects: the two upgrade policies share subject [pass_plan_change, pass_fee_charge] and both overwrite the same two base sentences, but they bind different target plans and different tools; no shared `(target_tool, computes)`.
- **Overlap that does produce a conflict** — the window-refund trigger (`pass_ext_upgrade_window_refund` rule S1: "A period fee is refunded under the full refund window when, no later than the last day of the plan's full refund window, the member ends the membership at once or moves up to a higher plan; ...") applies to *every* move up, including a move up to Plus Monthly, while only the All Access policy declares an edge onto it and only the All Access basis has a tier for a booked window refund. See finding G2.
- **Cross-category read boundary conflict** — the card-partner tiers of both upgrade policies against base `pass_plan_change_rules` / `pass_evt_fee_billing`. See finding G1.
- Time anchors: all "last N months" windows use `MONTHS(d, NOW) < N` (check_compute `_within`), i.e. strictly after the same day-of-month N months back; "whole months held" = `MONTHS(enrolled_date, NOW)`; the full refund window = `DAYS(charge, NOW) <= refund_full_window_days`, consistent with base counting ("day 1 is the calendar day after the charge").

### rule_compute_equivalence

Every `compute_basis` quotation was machine-checked as a verbatim substring of its policy's `rule` (all pass), every `baseline.rule` sentence is a sentence of the `rule` (all pass), every `overwrite.replaced_by` is a sentence of the rule (all pass). Sweep back, binding by binding:

- pass_ext_restoration_payment: r_fee, r_attempts (all declines with `billing_period_start = current_period_start`), r_share (monthly days / annual unused months `P(12) - MONTHS(start, NOW) - 1` / full), r_tenure, r_other_declines (retry_number 0 in 12 months less the current period's), r_trips (fare charges, 3 months by charge_date), r_credit_spent (redeems, 6 months), r_recovery_fee, one combined discount, add fee, round once — equivalent.
- pass_ext_plus_monthly_upgrade_charge: equivalent **except** `um_basis` first tier: rule "where the period's renewal shows a declined attempt and a membership fee has since been collected for the period, the basis is the membership fees collected for the period less any fee refunds booked against it" vs compute `um_paid if um_declined > 0 and um_paid > 0` where `um_paid` is already net of refunds. Situation where they diverge: renewal declined, fee collected, then refunded in full (net 0): rule → tier 1, basis 0.00; compute → falls through to `P('membership_fee')`. (G3-c.)
- pass_ext_trip_credit_posting: divergences —
  - (G3-a) `e_eligible_fare` tier 1: rule "where the fare charge was recalculated above the upfront fare" vs compute `e_fare_basis == 'recalculated'`. The trip charter (`trip.yaml` fare rule: "fare_basis records upfront when the upfront fare stood, recalculated when it was recalculated above the minimum") allows a recalculated fare below the upfront fare (rider shortens the route). Same situation: upfront 30.00, recalculated fare 25.00, booking fee 2.70 → rule tier 3: eligible 22.30; compute tier 1: 30.00 − 2.70 − discount = 27.30.
  - (G3-b) `e_month`: rule "capped ... at what remains of the plan's monthly cap for the calendar month of the drop-off" vs compute `LATEST('pass_events', 'credit_month', event_type='pass_credit_earn')` — the month of the most recently booked earlier credit, not the drop-off month of the trip being posted. Same situation: trip dropped off 2026-09-30 posted late after an October credit was booked → rule reads September's cap room, compute reads October's.
  - `e_trip` (latest fare-charged trip) stands in for "a trip whose credit did not reach the membership" — object selection by recency; observation (O5).
- pass_ext_refunded_fare_credit_forfeit: divergence (G3-d) `f_refunded = 0 - XSUM(trip_refund, trip_id=f_trip)` sums refunds of *every* charge on the trip (toll, airport surcharge, reservation fee) while the rule measures "how much of the fare came back". Same situation: fare 20.00 refunded 8.00 (40%) plus a 5.00 toll refund on the same trip → rule: under half, nothing clawed back; compute: 13.00/20.00 = 65% → partial clawback. `f_trip` (latest refund of any charge) has the same defect as an object selector (O5).
- pass_ext_upgrade_window_refund: equivalent (w_waivers' `pass_membership_id=HID` filter matches the trip charter's rule that only Pass-basis waivers carry the membership id).
- pass_ext_all_access_upgrade_charge: equivalent; `ua_renewals` counts every renewal charge (the rule's "annual renewals" is defined in the same sentence as "renewal fee charges less those refunded as duplicate charges") — observation only.
- DSL rounding: `RND` is Python `round(float, 2)`, not half-up; no scored value of either task lands on a half-cent boundary (checked in the task files) — observation O6.

### action_binding_and_uuids

- `(target_tool, computes)` pairs are pairwise distinct; each task tool is the target of exactly one extended policy.
- uuid8 tails: 5ad4a609, 9f7c0895, 2d51c03c, f79e4c68, 4b5902d4, d96d0945 — six distinct values, no shared prefix, no sequence, no copied-and-retailed pattern. PASS.
- Docstrings name no other tool and state no position in a workflow. Each Id-class Args line carries "as returned by the membership lookup before the call" — an ordering word attached to a read lookup, not to another problem's write (observation O1).
- Function bodies: none of the six tools checks status, window, prior refunds, credit entries or any prerequisite; each lands its one row and one holding update unconditionally. The tool layer judges no prerequisite. PASS.

### prerequisite_graph

| blocked policy | problem | kind | gate (bound in compute?) | form | resolved_by = dep target_tool | policy_source verbatim in own rule | in dep rule |
| --- | --- | --- | --- | --- | --- | --- | --- |
| plus_monthly_upgrade_charge | restoration_payment | value_input | um_paid (yes) | state | yes | yes | no |
| upgrade_window_refund | trip_credit_posting | value_input | w_credit_period (yes) | state | yes | yes | no |
| upgrade_window_refund | refunded_fare_credit_forfeit | value_input | w_credit_period (yes) | state | yes | yes | no |
| all_access_upgrade_charge | upgrade_window_refund | value_input | ua_paid (yes) | state | yes | yes | no |

- Every policy fills `prerequisite` (`[]` on the three leaves). All `problem` ids are extended ids, none self, none base. Graph is acyclic (two disjoint trees). No `fallback_reason` (all state form). No authoring-viewpoint phrasing in any `prerequisite` block.
- `condition` vs sentence: the plus-monthly edge's condition adds "and the membership status is active", which the sentence does not carry (strengthened; the same restore write makes both true, so no consequence — observation O2). The credit-posting edge's condition limits to trips "whose credit was due" while the sentence does not — see G4.

### prerequisite_sentences

1. "The Plus Monthly upgrade charge is worked out only after the billing period in force carries a collected membership fee." — connective "only after"; waited-on state record-visible (a `pass_fee_charge` with `billing_period_start = current_period_start`); no tool / id / snake_case. Writes of this difficulty that book a fee charge for the period in force: `restore_past_due_pass` (renewal charge for that period) and the two upgrade tools, which create a *new* period (the root itself, and a move to a different plan that also needs an active membership). Single reading: restoration rule S1 "A past-due membership is restored when the member pays the declined renewal of the billing period in force ... booked as a renewal fee charge for that period" → restore. PASS.
2. "The window refund is fixed only after every eligible trip completed in that period carries its ride credit entry." — "only after"; state = credit earn entry per trip; only `post_pass_ride_credit` writes credit earn rows. Breadth: see G4.
3. "The window refund is not worked out before every fare in that period refunded in part or in full carries the forfeiture owed on its credit." — "not ... before"; only `forfeit_pass_ride_credit` writes trip_refunded forfeitures. Condition ("at least half the fare") equals the sentence read through the forfeiture rule ("less than half ... nothing is clawed back"). PASS.
4. "The All Access upgrade charge is not fixed until a period fee still inside its full refund window carries the refund owed on it." — "not ... until"; state = `pass_fee_refund` naming the in-window charge; only `refund_pass_period_fee` writes fee refunds; window-refund rule S1 says when the refund is owed ("... or moves up to a higher plan"). PASS.
- Depended-on rules do not restate any sentence; no second wording, no tool name in any rule.
- Base rule sentence carrying an order: base `pass_plan_change_rules` S1 "is allowed only on an active membership" is a second gate on task 0's tree (past_due → restore → active). Task 0's extended rule carries its own prerequisite sentence, so this is an observation (O3), not a red.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (F = followed/inherited, O = overwritten and declared, — = not applicable):

- restoration_payment: pass_evt_fee_billing S1 F (past_due billable), S2 O, S3 F, S4 —, S5 F (one renewal charge for the period); pass_evt_payment_dunning S1 F, S2 F, S3 F (grace inherited; restore keeps period dates), S4 —; pass_plan_change_rules: no sentence governs the restoration quantity.
- plus_monthly_upgrade_charge: pass_plan_change_rules S1 F, S2 O, S3 —, S4 —, **S5 "A membership taken out through a card partner offer can change plan only by ending the partner membership and enrolling again." — not followed and not declared** (G1); pass_evt_fee_billing S2 O, **S4 "A membership taken out through a card partner offer is never billed by Wayfare." — contradicted by a card-partner upgrade charge, not declared** (G1); pass_student_verification —.
- all_access_upgrade_charge: same as plus-monthly, including the same two undeclared contradictions (G1).
- trip_credit_posting: pass_evt_ride_credit S1 F, S2 O, S3 F, S4 O, S5 F; pass_trip_benefits S1-S3 F (tier-1 eligible fare is net of the member discount, consistent with "credit is earned on the discounted fare").
- refunded_fare_credit_forfeit: pass_evt_credit_redeem_forfeit S1 —, S2 —, S3 O, S4 O.
- upgrade_window_refund: pass_cancellation_and_refund S1 F, S2 F, S3 O, S4 O, S5 —, S6 F, S7 F, S8 F. The overwrite of S3 extends the window refund to "moves up to a higher plan" for every plan — see G2 for what that does to the Plus Monthly upgrade.

### factor_ladders

| policy | factor | effect | decides | tiers | multi-source tiers | cross_difficulty | rule states full ladder |
| --- | --- | --- | --- | --- | --- | --- | --- |
| restoration | restored_period_share | method | r_share | 3 | yes (plan period × decline count) | — | yes |
| restoration | loyalty_restoration_discount | parameter | r_loyal | 3 | yes (enrolled_date × declines) | — | yes |
| restoration | frequent_rider_restoration_discount | parameter | r_rider | 3 | no | trip | yes |
| restoration | credit_use_restoration_discount | parameter | r_credit_use | 3 | no | — | yes |
| restoration | payment_recovery_fee | parameter | r_recovery_fee | 3 | no | — | yes |
| plus_monthly | unused_value_basis | method | um_basis | 3 (**2 live**, G1) | yes | — | yes |
| plus_monthly | unused_period_share | method | um_share | 3 | yes (charge date × credit posts × plan) | — | yes |
| plus_monthly | loyalty_upgrade_discount | parameter | um_loyal | 3 | yes (enrolled_date × trip charges) | trip | yes |
| plus_monthly | comfort_rider_upgrade_discount | parameter | um_comfort | 3 | no | trip | yes |
| plus_monthly | reserve_rider_upgrade_credit | parameter | um_reserve | 3 | no | trip | yes |
| plus_monthly | airport_rider_upgrade_discount | parameter | um_airport | 3 | no | trip | yes |
| credit_posting | frequent_rider_points | parameter | e_freq_points | 3 | yes | — | yes |
| credit_posting | ride_option_points | parameter | e_option_points | 3 | no | trip | yes |
| credit_posting | eligible_fare_basis | method | e_eligible_fare | 3 | yes | trip | yes (compute tier 1 differs, G3-a) |
| credit_posting | late_posting_goodwill | parameter | e_goodwill | 3 | no | trip | yes |
| credit_posting | pro_driver_points | parameter | e_pro_points | 3 | no | earnings | yes |
| credit_posting | trip_type_points | parameter | e_trip_points | 3 | yes (airport_leg × booking_mode) | trip | yes |
| forfeit | refund_share_clawback | method | f_clawback | 3 | no | trip | yes |
| forfeit | loyalty_forfeiture_relief | parameter | f_loyal | 3 | yes | — | yes |
| forfeit | refund_reason_forfeiture_relief | parameter | f_reason_relief | 3 (**unreal**, G5) | no | trip | yes |
| forfeit | pro_forfeiture_relief | parameter | f_pro_relief | 3 | no | earnings | yes |
| forfeit | frequent_rider_forfeiture_relief | parameter | f_rider_relief | 3 | no | trip | yes |
| window_refund | benefit_netting_basis | method | w_netted | 3 | yes (plan × spend) | — | yes |
| window_refund | netting_share | parameter | w_share | 3 | yes | — | yes |
| window_refund | pass_waiver_charge | parameter | w_waiver_value | 3 | no | trip | yes |
| window_refund | pro_refund_relief | parameter | w_pro_relief | 3 | no | earnings | yes |
| window_refund | frequent_rider_refund_relief | parameter | w_rider_relief | 3 | no | trip | yes |
| all_access | unused_period_basis | method | ua_basis | 3 (**2 live**, G1) | yes | — | yes |
| all_access | unused_period_portion | method | ua_portion | 3 | yes | — | yes |
| all_access | loyalty_all_access_discount | parameter | ua_loyal | 3 | yes | trip | yes |
| all_access | pro_all_access_discount | parameter | ua_pro | 3 | no | earnings | yes |
| all_access | annual_commitment_discount | parameter | ua_commit | 3 | yes (plan × renewals) | — | yes |
| all_access | green_rider_all_access_discount | parameter | ua_green | 3 | no | trip | yes |

- Counts per policy (declared): restoration 5 (1 method / 4 parameter), plus_monthly 6 (2/4), credit_posting 6 (1/5), forfeit 5 (1/4), window_refund 5 (1/4), all_access 6 (2/4). All within 4-6, ≥2 parameter, ≥1 method. Per task: task 0 has multi-source (restored_period_share, loyalty_*, unused_period_share) and cross-difficulty (trip); task 1 has multi-source and cross-difficulty (trip, earnings). After striking the factors G1/G5 strike, every policy still keeps ≥4 factors with ≥1 method and ≥2 parameter.
- Bindings are disjoint within each policy; every `decides` is an input, never `result`. No two tiers of one ladder share a value or method. Every tier is stated in the rule and implemented as a branch of its `decides` binding (G3-a notes the one tier whose compute condition is wider than the rule's).
- Every factor's `baseline` equals its fall-through tier and what the policy's `baseline.rule` states for that input (refund_share_clawback's baseline is the baseline rule's "whole credit when refunded in full, nothing when only part", which is honest). Each `baseline.rule` is self-sufficient and gives a definite number from the records.
- Labels honest: method factors change how a quantity is formed (day share vs month share vs whole; which ledger quantity is the basis; refund-share algorithm; credit earned vs credit spent); parameter factors substitute numbers.
- Realness: G1 (card-partner tiers unreachable / contradicting base) and G5 (refund-reason fault tier names reasons the trip charter never books on a fare refund) fail. Other ladders: conditions are ones a membership business plausibly weighs (tenure, decline history, trip frequency, ride mix, Pro status, refund reason, timing) and no condition holds of every customer reaching its write.

### findings

**G1 — SOURCE-POLICY RED and SOURCE-FACTOR RED (card-partner tier of both upgrade bases).**
- Symptom: `unused_value_basis` (plus_monthly) and `unused_period_basis` (all_access) each have a middle tier "for a membership taken out through a card partner offer the basis is nothing".
- Root cause: base `pass_plan_change_rules` S5 "A membership taken out through a card partner offer can change plan only by ending the partner membership and enrolling again." and base `pass_evt_fee_billing` S4 "A membership taken out through a card partner offer is never billed by Wayfare." are neither followed nor named in either policy's `overwrite`; in addition `card_partner_plans` is false for Plus Monthly and All Access Annual, and plus_monthly's own prerequisite sentence ("worked out only after the billing period in force carries a collected membership fee") can never hold for a never-billed partner membership.
- Demonstrated consequence: same situation — a card-partner Monthly member asks to move up to Plus Monthly. Base S5: no plan change (end and re-enroll), no Wayfare charge (S4). Extended plus_monthly rule S1 + basis tier 2: the move takes effect today and Wayfare collects 19.99 × (1 − discount) − reserve credit − 0.00. Different terminal states. Read as base-governed instead, the tier is never reached by any customer who reaches this write, so each ladder has only two live tiers (< 3).
- Affected: `pass.extended.yaml` pass_ext_plus_monthly_upgrade_charge (rule S5, factors.unused_value_basis, compute um_basis) and pass_ext_all_access_upgrade_charge (rule S5, factors.unused_period_basis, compute ua_basis). Bears on tasks 0 and 1 (no consequence on either scored value: both members signed up through website / rider_app).

**G2 — SOURCE-POLICY RED (the window refund fires on every move up; only the All Access root is wired to it).**
- Symptom: `pass_ext_upgrade_window_refund` S1 makes a period fee refundable "when, no later than the last day of the plan's full refund window, the member ends the membership at once or moves up to a higher plan", for every plan; only `pass_ext_all_access_upgrade_charge` carries a prerequisite sentence onto it and a basis tier for it. `pass_ext_plus_monthly_upgrade_charge` already credits the *whole* period inside the window (unused-period share tier 1) and carries no sentence about a refund.
- Root cause: a cross-problem link stated in a rule (refund ↔ move up) that grounds no declared edge for the Plus Monthly root, together with two policies that each compensate the same unused in-window fee.
- Demonstrated consequence (charter level): a Monthly member charged 9.99 yesterday, no benefit used, moves up to Plus Monthly. Reading A (no refund): charge = 19.99 × (1 − d) − r − 9.99. Reading B (window refund owed under S1, refund ≈ 9.99, then the upgrade): the member gets 9.99 back *and* the upgrade still credits 9.99 (plus-monthly basis tier 3, share tier 1) — two terminal states, and the order of the two writes is not pinned. Task 0 sits exactly in this situation; the demonstration against its world is in `0.md`.
- Affected: `pass.extended.yaml` pass_ext_upgrade_window_refund rule S1 / overwrite[0]; pass_ext_plus_monthly_upgrade_charge rule (no sentence on a window refund) and um_basis/um_share. Bears on task 0.

**G3 — SOURCE-POLICY RED (rule ↔ compute non-equivalence, four places).** (a) e_eligible_fare tier 1 "recalculated above the upfront fare" vs `fare_basis == 'recalculated'`; (b) e_month "calendar month of the drop-off" vs latest booked credit_month; (c) um_basis "a membership fee has since been collected" vs net `um_paid > 0`; (d) f_refunded "how much of the fare came back" vs all refunds on the trip. Each pair is quoted in `rule_compute_equivalence` with a situation where the two give different numbers. On task 1's world (a), (b), (d) coincide (fare 44.90 > upfront 38.75; drop-off month 2026-10 = latest credit_month 2026-10; the only refund on trip 84f9b68c is against its fare); (c) bears on task 0's second reading (see `0.md`). Affected: compute bindings e_eligible_fare, e_month, um_basis, f_refunded.

**G4 — SOURCE-POLICY RED (credit-posting prerequisite sentence broader than its condition).** Sentence "The window refund is fixed only after every eligible trip completed in that period carries its ride credit entry." covers a trip completed inside the 48-hour posting delay (eligible, entry not yet due), which can only acquire its entry by the passage of time — a real-world wait; the edge's condition limits to trips "whose credit was due". Same situation (member ends at once 10 hours after an eligible trip): sentence → the refund waits two days; condition → the refund is fixed now. Bears on task 1; no consequence on its world (latest drop-off 2026-10-06 14:47 MST, all credits due by frozen_time).

**G5 — SOURCE-FACTOR RED (refund-reason ladder of the forfeiture is not a real ladder).** The trip charter books a whole-charge `trip_refund` only for "duplicate_charge, toll_not_incurred, airport_surcharge_not_applicable, cancelled_within_grace, driver_eta_exceeded, premature_no_show, reserved_driver_late and courtesy_cancellation_refund" (of which only duplicate_charge applies to a fare), route_inefficiency / fare_above_upfront are `trip_fare_adjustment` reasons, and "any wrong drop-off location claim, is sent to the fare review team ... instead of being adjusted". So of the fault tier's four reasons none is ever recorded on a fare refund, and the pricing tier's fare_above_upfront never is either; a charter-conformant fare refund always sits on the pricing tier (duplicate_charge), i.e. the condition holds of every customer who reaches the write. Affected: pass_ext_refunded_fare_credit_forfeit factors.refund_reason_forfeiture_relief, rule S7. Bears on task 1 (its demonstration against the seed is in `1.md`).

**Observations (no demonstrated consequence):**
- O1 Docstring Args carry "as returned by the ... lookup before the call" (ordering word on a read, not on a cross-problem write).
- O2 plus-monthly edge `condition` adds "and the membership status is active" beyond its sentence.
- O3 Base `pass_plan_change_rules` S1 ("allowed only on an active membership") is an additional base gate on task 0's tree; the extended rule carries its own sentence.
- O4 The window-refund trigger "when ... the member ... moves up to a higher plan" presupposes the move, while the All Access root waits on the refund; the root's sentence pins the order (refund first), so one reading survives.
- O5 `e_trip` / `f_trip` select the object by recency (latest fare charge / latest refund of any charge), not by the rule's identifying property; correct on task 1's world.
- O6 `RND` is Python float rounding, not half-up.
- O7 `restoration_payment.base_policy_refs` lists pass_plan_change_rules, which governs none of its quantities.

## closing_checklist

Written after both reveals (2026-10-11T11:56:31Z); nothing above this heading was changed by a reveal except the freeze-time line, corrected to the file mtime.

**Closure not reached — the difficulty does not pass the source-layer audit.**

| item | state |
| --- | --- |
| one audit file per task + `_difficulty.md`, every comparison section present | yes (`0.md`, `1.md`); no older revision exists |
| every comparison section carries PASS on all four relationships | **no** — task 0: SOURCE-POLICY RED, SOURCE-FACTOR RED, SOURCE-TASK RED (CHAIN PASS); task 1: SOURCE-POLICY RED (charter-global), SOURCE-CHAIN RED, SOURCE-FACTOR RED (TASK PASS) |
| extended policies fully covered, scopes pairwise disjoint, tools/GT closed, uuid8s independent | yes |
| each tree 1-3 prerequisites, ≥ max(n−1,1) value_input, ≥1 owner=user problem, acyclic; whole-difficulty graph acyclic | yes (task 0: 1 / 1; task 1: 3 / 3) |
| every computation: self-sufficient baseline, 4-6 real factors (2 parameter, 1 method), ladders real, every factor bearing weight, baseline ≠ gold | **no** — G1 (dead card-partner tier in both upgrade bases), G5 (refund-reason ladder unreal; task 1's forfeiture falls to 3 surviving factors with no method on a seeded row that contradicts the trip charter); weight and baseline ≠ gold hold everywhere |
| policy self-consistent | **no** — G1, G2 (demonstrated on task 0), G3 (a-d), G4 |
| gates re-run on the final form | not run — closure not reached; the auditor only cites the coordinator's snapshot (all green) |

Per-task verdicts: task 0 — POLICY RED / CHAIN PASS / FACTOR RED / TASK RED. Task 1 — POLICY RED (charter-global, no per-task consequence) / CHAIN RED (false skipped-posting figure 185.08 vs 185.07 by the published half-up rounding) / FACTOR RED / TASK PASS.

## revision_2

### charter_global_frozen (revision 2)

- Written 2026-10-11 (UTC) before any round-2 task GT was revealed; revision 1 above is left untouched.
- Inputs re-hashed and equal to the coordinator's HASHES.txt: `pass.extended.yaml` `29fd1be3d0e5dc88f06753c585b68eb699a2082b1adb8eb0ff02d56e21e9a055` (changed from `c5a6e9e7…`), `task_tools.py` `7795b1ed82eeabc07b3040f193901ced6f2ac4501e04de1ced30ed11e76aa2e4` (changed from `8881c405…`). Both shared inputs moved, so every charter-global section is re-derived in full below; nothing is carried forward by reference. Blueprint files unchanged; base copy (lines 1-1055) still byte-identical to `blueprint/products/pass.yaml`.
- Same permitted / masked division as revision 1. Gate snapshot (coordinator, after rework): EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK, rc=0; traceability deferred. Entry conditions met.
- Tool module: only the `forfeit_pass_ride_credit_4b5902d4` docstring changed ("reduced or refunded"); all six bodies unchanged and still judge no prerequisite; uuid8s unchanged and independent.

### policy_conflict_scan (revision 2)

- Scopes unchanged: task 0 = {restoration_payment, plus_monthly_upgrade_charge}; task 1 = {trip_credit_posting, refunded_fare_credit_forfeit, upgrade_window_refund, all_access_upgrade_charge}; disjoint and jointly complete; `(target_tool, computes)` pairs distinct.
- Window-refund trigger now reads "... the member ends the membership at once or moves up to the Wayfare Pass All Access Annual plan" — a Plus Monthly move up no longer makes a period fee refundable, so the round-1 G2 overlap with the Plus Monthly policy is gone.
- Neither upgrade policy has a card-partner tier any more; both bases are "membership fees collected for the billing period in force less any fee refunds booked against them", which is 0.00 for a never-billed partner membership and so agrees with base `pass_evt_fee_billing` S4; base `pass_plan_change_rules` S5 is inherited untouched and no extended sentence reaches a different conclusion. Round-1 G1 conflict gone.
- The forfeiture policy now governs credit corrections after **fare adjustments** only; base `pass_evt_credit_redeem_forfeit` S3 (full refund → forfeit) is no longer overwritten and is inherited. No overlap between the two.
- **New conflict (R2-N1)**: the credit-posting cap is now counted over a rolling month of posting dates ("counted over the Pass ride credit posted to the membership after the same day of the previous month less the credit forfeited in that time"), while base `pass_evt_ride_credit` still binds `credit_month_basis: "=credit_month_basis"`, whose schema meaning is "Monthly credit caps and allowances count by calendar month in the member's home market time" (variant value `calendar_month`), and `credit_month` (db_schema: "calendar month a credit entry counts toward for the monthly credit cap"; post tool Args: "the calendar month the credit counts toward") still describes the calendar-month cap. The overwrite names only S4. See findings.

### rule_compute_equivalence (revision 2)

Machine check: every `compute_basis` quotation is a substring of its rule, every key is a bound name, every baseline sentence and every `replaced_by` is a rule sentence, every factor binding exists.
- restoration: unchanged; equivalent.
- plus_monthly: um_paid = fee charges + refunds for the period (rule "membership fees collected ... less any fee refunds booked against them"); um_unused = RND(MX(0, um_paid) × um_share); new um_pickup_charges = `trip_priority_pickup_charge` rows, 3 months by charge_date ("Priority Pickup charges the member paid in the last three months"); result subtracts reserve, pickup, unused. Equivalent. Round-1 G3-c closed (no "has since been collected" tier left).
- credit_posting: eligible-fare tier 1 now "where the rider changed the route and the fare charge was recalculated to more than the upfront fare less the member discount recorded on it" ↔ `e_route_changed == True and e_fare_basis == 'recalculated' and e_fare > e_upfront - e_discount` — equivalent (G3-a closed). Tier 2 now keyed on adjustments `original_charge_id = e_fare_id` ("booked against the fare charge") — equivalent. Cap room ↔ `SUM(credit_earn, within_months=1) + SUM(credit_forfeit, within_months=1)` = posted after the same day of the previous month, less forfeitures in that time — equivalent (G3-b closed as rule↔compute; see R2-N1 for the base residue). `e_trip` still selected by recency (O5).
- forfeiture: f_taken = adjustments with `original_charge_id = f_fare_id` ("the amount taken back" by adjustments against the fare); f_eligible = fare − booking fee; tiers under-minimum / ≥ a tenth / under a tenth; loyalty counts trip-kind forfeitures in 12 months; timing = DAYS(fare charge date, latest adjustment date on the trip). Equivalent. Round-1 G3-d closed (refunds of other charges no longer summed). `f_trip` = latest `trip_fare_adjustment` of any charge, including wait-time adjustments (O5 remains).
- window_refund: w_credit_period nets earns less trip-kind forfeitures of the period ("less the credit forfeited or corrected on trips of that period") — equivalent.
- all_access: ua_paid basis as plus_monthly; new ua_black_trips = completed Black + Black SUV by dropoff, 3 months — equivalent.
- `RND` still float `round` (O6).

### action_binding_and_uuids (revision 2)

Unchanged from revision 1 in substance: six distinct `(target_tool, computes)`; uuid8s 5ad4a609 / 9f7c0895 / 2d51c03c / f79e4c68 / 4b5902d4 / d96d0945 independent; no docstring names another tool or a sequence position (Args "as returned by the ... lookup before the call" remains, O1); bodies validate nothing.

### prerequisite_graph (revision 2)

| blocked | problem | kind | gate bound | form | resolved_by = dep tool | source verbatim in own rule / absent from dep rule |
| --- | --- | --- | --- | --- | --- | --- |
| plus_monthly | restoration | value_input | um_paid yes | state | yes | yes / yes |
| window_refund | credit_posting | value_input | w_credit_period yes | state | yes | yes / yes |
| window_refund | forfeiture | value_input | w_credit_period yes | state | yes | yes / yes |
| all_access | window_refund | value_input | ua_paid yes | state | yes | yes / yes |

Acyclic, no fallback, no viewpoint phrasing. Plus-monthly condition is now exactly the sentence's state ("a membership fee charge whose billing period start equals the membership's current period start") — round-1 O2 closed.

### prerequisite_sentences (revision 2)

1. Plus Monthly sentence unchanged; resolver restoration (only write booking a fee charge for the period in force other than the new-period upgrade charges). PASS.
2. "The window refund is fixed only after every eligible trip completed in that period whose credit has fallen due carries its ride credit entry." — now at the condition's strength ("whose credit has fallen due (48 hours after drop-off)"); no wait on not-yet-due trips. Round-1 G4 closed. Only the posting tool writes credit earn rows. PASS.
3. "The window refund is not worked out before every fare of that period reduced by a fare adjustment carries the credit correction owed on it." — "not ... before"; state = trip-kind forfeiture naming the earn entry; "owed" read through the forfeiture rule gives the condition's "at least a tenth ... or under the minimum". Only the forfeiture tool writes it. PASS.
4. All Access sentence unchanged; the window-refund rule now says the refund is owed when the member "moves up to the Wayfare Pass All Access Annual plan" within the window. PASS. (O4 — the refund's trigger presupposes the move, the root's sentence orders refund first — unchanged, observation.)

### override_declarations (revision 2)

- plus_monthly / all_access vs `pass_plan_change_rules` S5 and `pass_evt_fee_billing` S4: no longer contradicted (no card-partner treatment; a never-billed membership has 0.00 collected). G1 closed.
- credit_posting vs `pass_evt_ride_credit`: S2, S4 overwritten and declared; **the S4 overwrite changes the cap's month basis, but the policy's bound parameter `credit_month_basis` ("Monthly credit caps and allowances count by calendar month ...") is not named** (R2-N1). `pass_trip_benefits` S2 ("Allowances count per calendar month") concerns allowances, not the credit cap — followed.
- forfeiture vs `pass_evt_credit_redeem_forfeit`: only S4 ("Partial fare adjustments do not change credit already earned.") overwritten and declared; S3 inherited.
- window_refund vs `pass_cancellation_and_refund`: S3, S4 overwritten and declared; the S3 replacement now extends the window only to a move up to All Access Annual.
- restoration: unchanged (O7 kept).

### factor_ladders (revision 2)

| policy | factors (effect) | cross_difficulty |
| --- | --- | --- |
| restoration | restored_period_share (m), loyalty (p), frequent_rider (p), credit_use (p), recovery_fee (p) | trip |
| plus_monthly | unused_period_share (m), loyalty (p), comfort (p), reserve (p), airport (p), priority_pickup (p) — new | trip |
| credit_posting | frequent_rider (p), ride_option (p), eligible_fare_basis (m), goodwill (p), pro (p), trip_type (p) | trip, earnings |
| forfeiture | adjustment_clawback (m) — new, loyalty_correction (p), correction_timing (p) — new, pro (p), frequent_rider (p) | trip, earnings |
| window_refund | netting_basis (m), netting_share (p), waiver_charge (p), pro (p), frequent_rider (p) | trip, earnings |
| all_access | unused_period_portion (m), loyalty (p), pro (p), commitment (p), green (p), black_rider (p) — new | trip, earnings |

- Counts: 5-6 per policy, exactly 1 method and ≥4 parameter each; multi-source factors in both tasks; cross-difficulty factors in both tasks.
- Every ladder has 3 pairwise-distinct tiers stated in its rule and implemented in its decides binding; every baseline is the fall-through and what `baseline.rule` states (adjustment_clawback baseline 0 = "A fare adjustment leaves the credit already earned on the trip in place, so the credit correction is nothing", which is also the "under a tenth" fall-through — honest now).
- Realness: the dead card-partner tiers are gone (G1 closed); the refund-reason ladder is replaced by `correction_timing_relief` (days from the fare charge to the adjustment: 7+ / 3-6 / under 3), and the forfeiture's tiers now rest on `trip_fare_adjustment` rows, which the trip charter books for route_inefficiency / fare_above_upfront with the amount rule it states — G5 closed at the charter level (seed conformity checked in `1.md`). New ladders (Priority Pickup charges paid, Black/Black SUV trips, adjustment share, adjustment timing) are conditions a membership desk plausibly weighs; none holds of every customer reaching its write.

### findings (revision 2)

| round-1 item | status in revision 2 | evidence |
| --- | --- | --- |
| G1 card-partner tiers | **closed** | no card-partner tier in either upgrade rule/compute; basis = collected less refunds |
| G2 window refund on every move up | **closed** | trigger limited to "moves up to the Wayfare Pass All Access Annual plan" (rule S1, overwrite[0]) |
| G3-a eligible-fare tier 1 | **closed** | compute adds route-changed and `e_fare > e_upfront - e_discount` |
| G3-b cap month | **closed as rule↔compute**; residue → R2-N1 | rule and compute both rolling posted month |
| G3-c um_basis | **closed** | tier removed |
| G3-d f_refunded | **closed** | f_taken limited to adjustments against the fare charge |
| G4 sentence breadth | **closed** | "whose credit has fallen due" |
| G5 refund-reason ladder | **closed (charter)** | factor replaced; forfeiture keyed on fare adjustments |
| O2 condition strengthened | **closed** | "status is active" removed |
| O7 restoration base ref | kept (observation) | |
| O1, O4, O5, O6 | unchanged observations | |

**R2-N1 — SOURCE-POLICY RED (new, introduced by the G3-b rework): cap month basis declared in one clause, still calendar-month in another.**
- Symptom: extended credit-posting rule caps credit "at what remains of the plan's monthly cap, counted over the Pass ride credit posted to the membership after the same day of the previous month less the credit forfeited in that time"; base `pass_evt_ride_credit` still binds `credit_month_basis: "=credit_month_basis"` = `calendar_month`, defined "Monthly credit caps and allowances count by calendar month in the member's home market time", and the ledger's `credit_month` is "calendar month a credit entry counts toward for the monthly credit cap".
- Root cause: the overwrite supersedes the S4 sentence but not the parameter that the base policy binds for the same quantity.
- Demonstrated consequence (same situation): Plus Annual member, credit posted 2026-09-15 … 2026-09-30 totalling 95.00, a trip dropped off 2026-10-03 posted 2026-10-05 with raw credit 6.00 → rolling reading room 5.00 → credit 5.00; calendar-month reading (October, nothing yet) room 100.00 → credit 6.00.
- Affected: `pass.extended.yaml` pass_ext_trip_credit_posting overwrite[1] / rule S4 vs base `pass_evt_ride_credit.params.credit_month_basis`. Bears on task 1 (consequence on its world examined in `1.md`).

### closing_checklist (revision 2)

Written after the round-2 reveal (2026-10-11T13:47:42Z); the revision-2 charter-global sections above were written before it.

**Closure not reached — one charter-global SOURCE-POLICY RED (R2-N1) remains.**

| item | state |
| --- | --- |
| audit files one per task, revisions preserved, comparison sections present | yes (`0.md`, `1.md` each carry revision 1 and `## revision_2`) |
| every comparison PASS on all four relationships | task 0: PASS / PASS / PASS / PASS; task 1: SOURCE-POLICY RED (R2-N1, charter-global, no consequence on its values) / PASS / PASS / PASS |
| coverage, disjoint scopes, closed tools/GT, independent uuid8s | yes |
| trees: 1-3 prerequisites, value_input floor, owner=user problem, acyclic | yes (task 0: 1/1; task 1: 3/3) |
| computations: baseline, 4-6 real factors (≥2 parameter, ≥1 method), real ladders, every factor bearing weight, baseline ≠ gold | yes — all six policies; G1 and G5 closed |
| policy self-consistency | **no** — R2-N1 (cap month basis: rolling posted month in the extended rule vs `credit_month_basis = calendar_month` bound by base `pass_evt_ride_credit`, not named in the overwrite) |
| round-1 items | G1, G2, G3-a, G3-b (rule↔compute), G3-c, G3-d, G4, G5, task-1 rounding, O2 closed; O7 kept as observation; nothing regressed apart from the R2-N1 residue of the G3-b fix |
| gates re-run on final form | not run by the auditor (closure not reached); coordinator snapshot all green |

Per-task verdicts (revision 2): task 0 — POLICY PASS / CHAIN PASS / FACTOR PASS / TASK PASS. Task 1 — POLICY RED (charter-global R2-N1, no per-task consequence) / CHAIN PASS / FACTOR PASS / TASK PASS.

## revision_3

### charter_global_frozen (revision 3)

- Written 2026-10-11T14:28:38Z, before the round-3 task files were opened; revisions 1-2 untouched.
- Inputs re-hashed, equal to HASHES.txt: `pass.extended.yaml` `90d0639c437818416289591bc0d7e027b04a76d7bd95ab177e69ebc1d50811ea` (changed from `29fd1be3…`), `task_tools.py` `198d08503d487f1b500418695184831b0ab5790943f992730716bc35a99592c5` (changed from `7795b1ed…`); views unchanged (`35772dcd…`, `fe1083bd…`); blueprint unchanged; base copy still byte-identical. Both shared inputs moved, so the charter-global checks were re-run in full rather than carried forward.
- Where the charter moved (no copy of the revision-2 file was kept, so located by structure and by re-reading every extended policy's rule, prerequisite and compute): the file grew by one line; every policy keeps its revision-2 line span except `pass_ext_trip_credit_posting`, which gained one rule sentence — "For this monthly cap the rolling month above takes the place of the calendar month of the drop-off that the plan's credit-month basis sets for monthly credit caps: a credit is never held back by the credit already counted in the calendar month of its drop-off, and the calendar month of the drop-off recorded on each credit entry only shows when the trip was taken." — repeated at the end of its `overwrite[1].replaced_by` and quoted as the `compute_basis` of `e_month_earned`. Compute expressions, params, factors, baselines and prerequisite blocks of all six policies re-read and found as recorded in revision 2; re-executing every compute on the unchanged worlds reproduces every revision-2 figure (see the task files).
- Tool module: only Args docstrings changed — the Id-class lines now end "as returned by the membership lookup." (no "before the call"); `post_pass_ride_credit` `credit_month` now reads "the calendar month of the trip's drop-off in the member's home market time, recorded on the entry as its credit month". Bodies replay to the identical rows (all revision-2 figures reproduced).

### charter-global checks (revision 3)

- policy_conflict_scan: as revision 2; the only conflict recorded there (R2-N1) is now addressed on the extended side (below). No new overlap.
- rule_compute_equivalence: machine check re-run — every compute_basis quotation is a rule substring and a bound name, every baseline sentence and every replaced_by is a rule sentence, every factor binding exists (0 problems). The new sentence matches `e_month_earned` = rolling-month posted credit less forfeitures; equivalent.
- action_binding_and_uuids: unchanged; six distinct pairs, independent uuid8s, bodies validate nothing; **O1 closed** (no ordering word left in any Args line; the only "before" left is inside the private `_PeriodCalendar.period_end` helper's description of the period-end arithmetic, not a tool docstring).
- prerequisite_graph / prerequisite_sentences: unchanged from revision 2 — four state-form value_input edges, sentences verbatim in their own rules and absent from the depended-on rules, resolvers unique, acyclic. PASS.
- override_declarations: `pass_ext_trip_credit_posting` overwrite[1] now states, in its replaced_by and in the rule, that for this cap the rolling month replaces "the calendar month of the drop-off that the plan's credit-month basis sets for monthly credit caps", and that the recorded calendar month only dates the trip. The base parameter `credit_month_basis` is therefore named and displaced for exactly this quantity on the extended side; the merged semantics for the cap are unique (rolling posted month). **R2-N1 closed.** Residual wording elsewhere — db_schema `credit_month` ("calendar month a credit entry counts toward for the monthly credit cap") and the post tool's summary line "counted toward the given calendar month and billing period" — is outranked by the declared sentence; observation O8, no reading of either task changes.
- factor_ladders: unchanged from revision 2 (5-6 factors, exactly 1 method each, real three-tier ladders, cross-difficulty trip/earnings, multi-source present).

### findings (revision 3)

| item | status |
| --- | --- |
| R2-N1 cap month basis | **closed** — declared on the extended side in overwrite[1] and the rule |
| O1 docstring "before the call" | **closed** |
| O4, O5, O6, O7, T1 | unchanged observations (as the reworker states) |
| O8 (new observation) | db_schema `credit_month` meaning and the post tool's summary line still speak of a calendar month "counted toward"; outranked by the declared extended sentence; no consequence |

No new SOURCE-* defect found at the charter level; nothing regressed.

### closing_checklist (revision 3)

Written after the round-3 reveal (2026-10-11T14:28:42Z).

**Closure reached at the source layer — all four relationships PASS for both tasks.**

| item | state |
| --- | --- |
| audit files one per task, revisions 1-3 preserved, comparison sections present and PASS | yes |
| extended policies fully covered; scopes disjoint; tools and GT closed; uuid8s independent and frozen | yes |
| trees: task 0 one prerequisite (1 value_input), task 1 three prerequisites (3 value_input); owner=user problem in each; whole-difficulty graph acyclic | yes |
| computations: self-sufficient baselines ≠ gold; 5-6 real factors each, ≥2 parameter and exactly 1 method; multi-source and cross-difficulty (trip; trip + earnings) per task; every factor bears weight | yes |
| policy self-consistency (G1-G5, R2-N1) | yes — all closed |
| open observations | O3, O4, O5, O6, O7, O8, T1 (no demonstrated consequence) |
| instantiation-stage gates on the final form | not re-run by the auditor (Step 0: the auditor cites, does not run); coordinator's round-3 snapshot: EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK, rc=0; traceability deferred to render |

Caveat: the round-3 task derivations are re-executions on worlds whose GT had already been revealed in round 2 (disclosed in each task file); the blind evidence for these worlds is the revision-2 derivation, which matched GT item for item.

Per-task verdicts (revision 3): task 0 — PASS / PASS / PASS / PASS; task 1 — PASS / PASS / PASS / PASS.

## revision_4

### charter_global_frozen (revision 4)

- Written 2026-10-11T15:27:17Z, before the round-4 task files were opened; revisions 1-3 untouched. I did not read the KB audit (`audits/policy_kb/…`) that prompted this round; the two notes are known only from the coordinator's one-line brief.
- Inputs re-hashed: `pass.extended.yaml` `8d407b8ec8b30450a630a931eeb50d182a7e23ca91040e91fa11464e00d1c896` (changed from `90d0639c…`); `task_tools.py` `198d0850…` (unchanged); views `35772dcd…` / `fe1083bd…` (unchanged); blueprint unchanged; base copy byte-identical. The charter moved, so the charter-global checks are re-run in full.
- What moved (all policies re-read; machine checks re-run: every compute_basis quote, baseline sentence and replaced_by is a rule sentence, every **superseded_clause is now also verified verbatim inside its base policy's rule**, every factor binding and prerequisite gate exists — 0 problems):
  1. `pass_ext_restoration_payment`, `pass_ext_plus_monthly_upgrade_charge`, `pass_ext_all_access_upgrade_charge`: the `pass_evt_fee_billing` overwrite now supersedes only "The fee for a period is the plan's membership_fee;" instead of the whole sentence. The rest of that base sentence — "the period ends on the day before the same day-of-month billing_period_months later, falling back to the last day of the month when that day does not exist (period_end_rule)" — is therefore inherited, which is exactly what the tools apply (`_PeriodCalendar.period_end`), what the restoration keeps ("the same period dates"), and what "a new one-month / twelve-month period ... starts that day" needs to fix its end. No extended sentence conflicts with the inherited part. (Revision 1-3 had recorded these overwrites as declared and found no consequence; the narrowing removes an over-broad retirement — no relationship verdict changes.)
  2. `pass_ext_refunded_fare_credit_forfeit`: the baseline sentence is now "When fare adjustments reduce a fare that earned Pass ride credit, the clawed-back credit is the whole credit earned on the trip, and the credit correction is that clawed-back credit." (it no longer restates the retired base sentence "Partial fare adjustments do not change credit already earned."); the `adjustment_clawback` ladder is reordered — tier 1 "less than a tenth taken back and left at or above the minimum eligible fare → nothing", tier 2 "at least a tenth and left at or above the minimum → pro rata", fall-through "left under the minimum → whole credit"; factor baseline `f_clawback: f_earned`; compute `(0 if f_taken < f_eligible * 0.10 else RND(f_earned * f_taken / f_eligible, 2)) if f_eligible - f_taken >= min else f_earned`. Trigger sentence, reliefs and params unchanged.

### charter-global checks (revision 4)

- policy_conflict_scan / scopes / action bindings / uuid8s / prerequisite graph and sentences: unchanged from revision 3; PASS.
- override_declarations: the three narrowed overwrites are verbatim fragments of base `pass_evt_fee_billing` S2 and leave the period-end rule in force; the forfeiture overwrite still supersedes exactly base S4 and its policy no longer restates S4 anywhere; base S3 (full refund → forfeit) inherited. No undeclared override.
- rule_compute_equivalence (forfeiture): rule ladder ↔ compute branches equivalent (under-minimum checked first in compute, which is the rule's fall-through; tiers are pairwise disjoint so order is immaterial). Baseline sentence ↔ `baseline.f_clawback = f_earned` with every relief at its 0 baseline → whole credit, limited to the balance.
- factor_ladders (forfeiture): `adjustment_clawback` — three disjoint tiers with distinct methods (nothing / pro rata / whole credit), stated in the rule; the fall-through equals the baseline (whole credit) — honest; the fall-through condition (an adjusted fare whose eligible remainder falls under the minimum that earned it credit) is reachable and is a treatment a credit programme plausibly applies (the trip would not have earned credit at that fare). The baseline is now a definite, non-trivial standard method (claw back the whole trip credit on any downward adjustment), not a restatement of the retired base clause. Counts unchanged: 5 factors, 1 method.
- No new SOURCE-* defect at the charter level; nothing regressed. Observations O3-O8, T1 unchanged.

### closing_checklist (revision 4)

Written after the round-4 reveal (2026-10-11T15:27:22Z).

**Closure holds — all four relationships PASS for both tasks.**

| item | state |
| --- | --- |
| audit files per task, revisions 1-4 preserved, comparison sections present and PASS | yes |
| coverage / disjoint scopes / closed tools and GT / independent uuid8s | yes |
| trees (task 0: 1 prerequisite, 1 value_input; task 1: 3 prerequisites, 3 value_input), owner=user problem in each, acyclic | yes |
| computations: baselines self-sufficient and ≠ gold (forfeiture baseline now 4.45 ≠ 0.52), 5-6 real factors with exactly 1 method, multi-source and cross-difficulty per task, every factor bearing weight | yes |
| policy self-consistency, overrides declared at the right width (superseded clauses verified verbatim in base; period-end rule inherited) | yes |
| open observations | O3, O4, O5, O6, O7, O8, T1 (no demonstrated consequence) |
| gates on the final form | cited, not run by the auditor: coordinator's round-4 snapshot EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE / TRACEABILITY OK; validate_scenario VALID |

Caveat as in revision 3: the round-3 and round-4 task derivations are re-executions on worlds whose GT had been revealed in round 2; the blind evidence for these worlds is revision 2, which matched GT item for item.

Per-task verdicts (revision 4): task 0 — PASS / PASS / PASS / PASS; task 1 — PASS / PASS / PASS / PASS.
