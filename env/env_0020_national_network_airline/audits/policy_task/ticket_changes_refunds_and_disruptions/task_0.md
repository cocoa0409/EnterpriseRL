# Policy-task audit — ticket_changes_refunds_and_disruptions / task 0

## source_derivation_frozen

- Freeze hashes: `ticket.extended.yaml` sha256 `4a3e530dd49b6f5d7c021737b5722d93d2ec655c847908699c8d44bffbaa4650`; `task_tools.py` sha256 `9255fa2be82db05e4d669c1f8ec5eaf561327ac9bf6c8409dba915cadd8d0783`; masked view `task_0.masked.json` sha256 `a9e1ff8b639f555ee9e5eaa432d93c80f46131dc576543e5bd399f8471e913ef`.
- Freeze time: 2026-09-24T18:40Z (before any task's GT was revealed). Auditor: independent audit subagent (Claude Opus 5.5).
- Fields permitted: `task_index`, `frozen_time`, `user_scenario`, `initial_state` (through the masked view), the extended charter, `task_tools.py`, `blueprint/`, `erlbench/`, the evaluator helpers of `check_compute.py`.
- Fields masked and not read before this freeze: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state`, the task JSON file itself, both worklogs, sibling audits.
- contamination_disclosure: none. The brief carried no scored value; no recursive search touched `tasks/*/tasks/*.json`; the worklogs were not opened.
- Method: the auditor derived every write, argument and order from the rules and the world, then replayed its own writes through the real tool functions and evaluated each policy's `compute` on the handling-time world with the evaluator's own DAYS/MONTHS/LATEST/XCOUNT semantics (script in the auditor's scratchpad, inputs: masked view + charter + tools only).

### policy_self_consistency (this task only)

Charter-global conclusions this task rests on (cited, not restated): `_difficulty.md` § policy_conflict_scan, § rule_compute_equivalence, § action_binding_and_uuids, § prerequisite_graph, § prerequisite_sentences, § override_declarations, § factor_ladders, § findings.

Consequence of each charter-global finding that bears on this task, demonstrated on this world:
- F1 (P3->P1 zero-fee gap): on this world P1 evaluates to a non-zero fee (see derivation: 17.55), so P1 writes the same-day change fee entry and P3's prerequisite sentence can hold. Leah's tier (Summit Silver) does not waive the fee (`loyalty.yaml` Summit Silver `same_day_change_fee_waived: false`), the delay on segment 2 is 105 minutes (< 120) and the ticket names no agreement (`corporate_account_id: null`). No consequence on this task.
- F2 (P3->P2 sentence broader than condition): segment 2 carries exactly one seat charge (`ticket_services.3ddcb4d9-c8da-41a3-b6f0-acceecad556f`); "every seat charge on that segment" and "the seat_purchase entry" name the same row. No consequence.
- F3/O3 (P3 `up_seat_paid` sums every seat charge on the segment): one seat charge on segment 2, so SUM = that charge. No consequence.
- F4 (P3's only `method` factor is a parameter): bears on this task; demonstrated under `factor_weight`.
- Override declarations: P1, P2, P3 conclusions in `_difficulty.md` § override_declarations; O5 ("for a fixed fee") would give 149, which is P3's declared baseline, not a third number. No second defensible answer on this world.

Handling time: P1 and P2 are evaluated on the opening world (neither reads the other's writes: P1 reads `ticket_transactions`, `ticket_disruptions`, the loyalty holding and `loyalty_activity`; P2 reads the seat rows of `ticket_services`, the ticket and the loyalty holding); auditor replay: P1 = 17.55 before or after P2's write, P2 = 61.30 before or after P1's write. P3 is evaluated after both writes and before its own.

Real-world waits: none. Every consumed fact is a seeded record (exchange `6fe1ec4d-...`, seat charge `3ddcb4d9-...`, delay record `8641005c-...`, loyalty holding `f11c3391-...` and its activity rows) or the synchronous effect of an earlier write of this task. The delay record is a record of the evening flight already on file at the opening (`recorded_date` 2026-09-24); no outcome of a future event is consumed.

Result for this task: PASS (the charter-global REDs F1–F3 are real but move nothing on this world).

### problem_chain

Walk from the root:
- Root P3 (First upgrade, `purchase_first_upgrade_fa17fda8`, owner=user). Its rule carries two prerequisite sentences:
  1. "The First upgrade charge is not fixed until a same-day change fee entry stands on the ticket for every same-day confirmed exchange recorded on it." At the opening `ticket_transactions.6fe1ec4d-2005-4973-891d-59807ca0ce76` is a `ticket_exchange` with `exchange_type: same_day_confirmed` dated 2026-09-24, and `ticket_services` holds only two `ticket_seat_purchase` rows — no `ticket_change_fee` row at all. False at the opening. The write that brings it about is described by P1's rule ("posted through the call center as one same-day change fee entry linked to that exchange entry"); P1 applies because the ticket names no agreement.
  2. "The First upgrade charge on a segment is fixed only after a refund entry stands against every seat charge on that segment for the part of it charged in error above the seat price." Segment 2 (first unflown: one flown coupon `6455de36-...`) carries seat charge `3ddcb4d9-...` of 89.00; P2's seat price for it is 27.70 (below); no `ticket_fee_refund` row exists. False at the opening. The write is described by P2's rule ("refunded to the original payment as one fee refund entry against that seat charge").
- P1 and P2 carry no prerequisite sentence (`prerequisite: []`); the walk stops.

Derived tree: nodes {P3 root, P1, P2}; edges P3->P1 (value_input: the fee enters `fees_charged` -> trip spend -> spend band), P3->P2 (value_input: the refund lowers `up_seat_standing` -> seat credit, and raises `fees_refunded`). n = 2 prerequisite problems, 2 value_input edges >= max(n−1, 1) = 1. Acyclic. Topological order: {P1, P2} in either order, then P3. Isomorphic to the declared `prerequisite` of P3.

Load-bearing (auditor replay on the handling-time world):
- all prerequisites resolved: P3 = 69.19;
- skip P1's write: trip spend 436.23 < 450 -> spend rate 0.92 -> P3 = 77.17 (moves);
- skip P2's write: seat standing 89.00 -> credit 89.00, spend 515.08 -> P3 = 7.89 (moves);
- opening world (both skipped): P3 = 7.89.

Parallel edges: P1's and P2's writes touch different rows and neither policy reads the other's row kind (see handling time), so both orders give the same values (17.55, 61.30) and the same terminal state; P3 reads both only after both are written.

No-wait: both resolving writes are synchronous ledger entries; nothing waits on payment clearing, approval or a date.

Tool layer: the bodies of `post_same_day_change_fee_61b8e8ae`, `refund_seat_charge_excess_9145fc3e` and `purchase_first_upgrade_fa17fda8` only create one row each; none reads another row to refuse, warn or compute (`task_tools.py`).

Customer's own write: the root P3 is `owner="user"`; the persona hands it over passively ("when the agent hands the purchase over to you, you complete it yourself with the details the agent reads out").

Persona and the tree: the customer raises only the root ("you want to know what it costs to move up to First on your flight home today and to buy it. You are not asking for anything else."). The same-day change and the seats come out only on the agent's question ("Only if the agent asks which flight you are on today or whether you changed anything ..."; "Only if the agent asks about seats ..."). "If the agent tells you that something on your ticket has to be charged or refunded before the upgrade can be priced, you say that is fine" is a passive, conditional consent, not a hint the simulator volunteers. The persona closes after the upgrade purchase and its confirmation. No ask outside the charter.

Result: PASS.

### task_independent_derivation

Need, object, authorisation, timing: Leah Castellano (customer `7d1bc826-...`), ticket CQ7XMB (`2abfe7dc-...`, Crestline Main Cabin, `partially_flown`), segment 2 = SFO->SEA today 12:40 (`next_departure_at` 2026-09-24T12:40; persona "flying home to Seattle today on the 12:40 flight"). She asks for the price and the purchase of a First upgrade and commits in advance to buy "at whatever price the agent quotes", paying herself; she consents to charges/refunds the agent says are owed. Act now: frozen 2026-09-24 09:10 PDT, before departure; ticket status allows a paid upgrade (base `upgrade_ticket_open`), Main Cabin `paid_upgrade_permitted: true` (`upgrade_brand`), no complimentary cabin confirmed (`upgrade_certificate_balance: 0`, no upgrade rows).

Identity: `verify_customer_identity(customer_id=7d1bc826-3561-4fae-9c23-9a7e1b8f6f6c, phone_number=3605551847, date_of_birth=1986-04-19)` — two details from the persona, matching `customers.7d1bc826-...`.

P1 — same-day change fee (agent, owed "whether or not the customer raises it"); handling time = opening world.
- List fee: Main Cabin `same_day_confirmed_change_fee` 75.
- Member rate: loyalty holding `f11c3391-...` Summit Silver, `status: active`; Silver `same_day_change_fee_waived: false`, `complimentary_preferred_seating: true`; flight accruals within 12 months of 2026-09-24 (evaluator MONTHS < 12): 2025-10-14, 2025-12-02, 2026-01-19, 2026-03-08, 2026-05-21, 2026-07-11, 2026-09-21 = 7 >= 6 -> 0.65. Excluded: 2025-08-30 and older (window), hotel partner accrual `57394208-...` (not a flight accrual).
- Delay rate: `ticket_disruptions.8641005c-...` segment 2, flight_date 2026-09-24, delay 105 min: >= 60, < 120 -> 0.45.
- Direction fare (method): one flown coupon -> fare collected 379.20 (`fe9a9cd8-...`) − flown 189.60 (`6455de36-...`) = 189.60 -> >= 150, < 300 -> fare rate 0.8.
- Fee = RND(75 × 0.65 × 0.45 × 0.8) = **17.55**. Write `post_same_day_change_fee_61b8e8ae(ticket_id=2abfe7dc-765a-4b51-90a6-a35047a07878, related_transaction_id=6fe1ec4d-2005-4973-891d-59807ca0ce76, corporate_account_id="", fee_amount=17.55)`.

P2 — seat charge correction (agent, owed on sight); handling time = opening world.
- Seat entry on segment 2: `3ddcb4d9-...` extra_legroom_seat, 679 miles, 89.00, online, bought 2026-08-27. List price: 679 <= 1000 -> short-segment extra-legroom 49.
- Member seat rate: Silver includes preferred but not extra-legroom seating -> 0.7.
- Advance days (method): online, active membership, bought 9 days after issue (2026-08-18 -> 2026-08-27, <= 14) -> issue date to departure date = DAYS(2026-08-18, 2026-09-24) = 37 -> >= 35 -> 0.85.
- Channel: online -> 0.95.
- Seat price = RND(49 × 0.7 × 0.85 × 0.95) = 27.70; correction = RND(max(0, 89.00 − 27.70)) = **61.30**. Write `refund_seat_charge_excess_9145fc3e(ticket_id=2abfe7dc-..., refunded_service_id=3ddcb4d9-c8da-41a3-b6f0-acceecad556f, source_disruption_id="", refund_amount=61.30)`.

P3 — First upgrade (user); handling time = after both writes.
- Price: seat entry of segment 2 records 679 miles -> short-segment First fee 149.
- Seat credit: extra-legroom seat, standing 89.00 − 61.30 = 27.70 -> credit 27.70.
- Trip spend: fare 379.20 + fees (17.55 same-day + 29.33 + 89.00 seats) − refunds 61.30 = 453.78 -> >= 450 -> 0.85.
- Member flight window (declared method): earned tier, enrolled 2014-03-02, 4589 days >= 3650 -> 24 months -> 11 flight accruals (2024-11-05 through 2026-09-21; 2024-08-10 excluded).
- Member rate: Silver `upgrade_priority_rank: 5`, 11 >= 10 -> 0.9.
- Departure-day rate: departure date = today -> 0.85.
- Charge = RND(max(0, 149 × 0.85 × 0.9 × 0.85 − 27.70)) = RND(96.887 − 27.70) = **69.19**. Opening-world contrast: 7.89 (fee absent drops spend to 497.53 but still >= 450; credit 89.00 instead of 27.70). 69.19 is right because P3's rule fixes the charge only after both prerequisite states hold.
- Hand-over: the agent quotes 69.19 and reads out ticket 2abfe7dc-..., segment 2, 679 miles; the customer runs `purchase_first_upgrade_fa17fda8(ticket_id=2abfe7dc-..., segment_number=2, segment_miles=679, upgrade_fee=69.19)`.

Write sequence and owners: verify (agent) -> {P1 post (agent), P2 refund (agent)} in either order -> P3 purchase (user). Terminal state: three new `ticket_services` rows (same_day_change_fee 17.55 linked to 6fe1ec4d; fee refund 61.30 against 3ddcb4d9, kind extra_legroom_seat, segment 2, charged_in_error; upgrade_first 69.19 on segment 2, 679 miles) and a verified identity row.

Reachability: every input above is readable through `find_ticket_holdings`, `find_ticket_transactions`, `find_ticket_services`, `find_ticket_disruptions`, `find_loyalty_holdings`, `find_loyalty_activity` (all in `share_tools.py`) or stated by the persona; the segment miles come from the seat entry. No seed-only field is needed.

Closest alternative candidates and their exclusion: (a) same-day member rate 1 (reading the Silver tier as ineligible) — excluded by 7 flight accruals >= 6 and `complimentary_preferred_seating: true`; (b) advance days from the purchase date (28 -> 0.9, correction 59.67) — excluded because the seat was paid online within 14 days of issue on a ticket crediting an active membership; (c) First price from the long-segment fee because the seat was charged at the long-segment price — excluded because the rule reads the recorded distance (679 <= 1000).

Result: act now; unique solution as above.

### factor_weight

All figures from the auditor's recomputation on the handling-time world of each computation.

P1 (result 17.55; all-baseline fall-back 75.00 ≠ 17.55):

| factor | label honest? | tier taken / records | baseline (from `baseline.rule`) | value with that factor at baseline |
| --- | --- | --- | --- | --- |
| same_day_member_rate | parameter, yes | tier 2 (0.65): holding `f11c3391` active Silver + 7 flight accruals in 12 months (loyalty = other difficulty) | 1.0 (baseline.rule charges the list fee) | 27.00 |
| same_day_delay_relief | parameter, yes | tier 2 (0.45): disruption `8641005c` 105 min | 1.0 | 39.00 |
| same_day_fare_band | parameter, yes | tier 2 (0.8): direction fare 189.60 | 1.0 | 21.94 |
| same_day_direction_fare | method, yes (subtraction vs halving vs whole) | tier 1: one flown coupon | whole fare collected 379.20 (-> fare rate 0.5) | 10.97 |

Near-miss: hotel partner accrual `57394208-...` and the 2025-08-30 flight accrual (outside 12 months) — a careless count gives 8, still the same tier, but the rule excludes both; the flown coupon 189.60, which a reader who skips the direction-fare method leaves in. No stamp naming a tier. Counts: 4 factors, 3 parameter, 1 method, 1 multi-source, 1 cross-difficulty — PASS.

P2 (result 61.30; all-baseline fall-back 89.00 − 49.00 = 40.00 ≠ 61.30):

| factor | label honest? | tier taken / records | baseline | value with that factor at baseline |
| --- | --- | --- | --- | --- |
| member_seat_rate | parameter, yes | tier 2 (0.7): Silver includes preferred, not extra-legroom (loyalty) | 1.0 | 49.43 |
| seat_advance_purchase_rate | parameter, yes | tier 1 (0.85): 37 counted days | 1.0 | 56.42 |
| seat_channel_rate | parameter, yes | tier 1 (0.95): `sales_channel: online` | 1.0 | 59.85 |
| seat_advance_days_convention | method, yes (anchor date changes / constant zero) | tier 1: online, active member, 9 days after issue | purchase date to departure = 28 days (-> 0.9) | 59.67 |

Near-miss: segment 1's extra-legroom seat `ac7a7d39-...` (29.33, flown segment) excluded by "first unflown segment"; the purchase-date day count (28) that a reader skipping the convention uses. No stamp. Counts: 4 factors, 3 parameter, 1 method, 1 multi-source (advance-days tier 1), 1 cross-difficulty — PASS.

P3 (result 69.19; all-baseline fall-back 149.00 ≠ 69.19):

| factor | label honest? | tier taken / records | baseline | value with that factor at baseline |
| --- | --- | --- | --- | --- |
| upgrade_seat_credit | parameter, yes | tier 1: extra-legroom standing 27.70 | 0 | 96.89 |
| upgrade_spend_rate | parameter, yes | tier 1 (0.85): trip spend 453.78 | 1.0 | 86.28 |
| upgrade_member_rate | parameter, yes | tier 2 (0.9): Silver rank 5, 11 flights (loyalty) | 1.0 | 79.95 |
| upgrade_member_flight_window | declared method — **not honest**: the tiers substitute 24/18/12 into one count formula (`_difficulty.md` § factor_ladders, F4) | tier 1: earned, enrolled 4589 days ago -> 24 months -> 11 | 12 months -> 7 flights -> member rate 1 | 79.95 |
| upgrade_departure_day_rate | parameter, yes | tier 1 (0.85): departs today | 1.0 | 86.28 |

Every factor bears weight on this world (each substitution moves the value). Near-miss: accrual 2024-08-10 (outside 24 months) and 2024-11-05 / 2025-02-17 (inside 24, outside 18 months); seat `ac7a7d39-...` on segment 1 (excluded from the seat credit, included in the trip spend). No stamp. Cross-difficulty rows (loyalty holding and activity) are seeded.

Counts after the tests: 5 declared; the window factor survives as a parameter at most, so P3 has 5 parameter and **0 method** factors against the floor of 1 — **SOURCE-FACTOR RED** (F4).

Task-level: multi-source (P1 member rate, P2 advance days, P3 member rate) and cross-difficulty (loyalty in P1, P2, P3) both present.

Observation (not a red light): the loyalty holding is Summit Silver with `tier_basis: earned`, but the seeded 2025 flight accruals carry 927 qualifying dollars against Silver's `qualifying_dollars_threshold: 4500`; the seed need not hold the full qualifying history, so no contradiction is demonstrable, and no ladder here reads qualifying dollars.

Result: SOURCE-FACTOR RED (P3 has no honest `method` factor); all other factor tests PASS.

## source_gt_comparison

- Reveal: `tasks/ticket_changes_refunds_and_disruptions/tasks/0.json` opened at 2026-09-24T18:29:26Z, after both task derivations were on disk (sha256 at the moment of reveal: `_difficulty.md` `571fdc6c...`, `task_0.md` `71bec31e...`, `task_1.md` `8961b5c8...`). Timestamp correction, stated rather than edited: the "Freeze time" lines written inside the frozen sections of `task_0.md` (18:40Z) and `task_1.md` (18:50Z) were estimates typed before the clock was read; the real freeze is bounded by the hashes above, taken at 18:29:26Z immediately before the reveal command. The frozen text itself is unchanged.

Item-by-item:

| item | auditor (frozen) | GT | same? |
| --- | --- | --- | --- |
| need / authorisation / timing | buy First on segment 2 today, self-paid, consent to owed charges/refunds, act now | same (`solvability_contract.request_alignment`, step 15 binding) | same |
| identity | verify with phone 3605551847 + DOB 1986-04-19 | step 1, same args | same |
| read set | ticket holdings, transactions, services, disruptions, loyalty holding, loyalty activity | same, plus `find_customers`, `find_business_roster`, `find_business_holdings` (to see the employer agreement is not named on the ticket) | same in substance; GT's two business reads are corroborative (the ticket's `corporate_account_id: null` already decides P1's scope) |
| P1 object / args | exchange 6fe1ec4d…, corporate "" , 17.55 | step 11 same | same |
| P2 object / args | seat 3ddcb4d9…, disruption "", 61.30 | step 13 same (61.3) | same |
| P3 args / owner | segment 2, 679 miles, 69.19, owner user | step 15 same, `call_user_discoverable_tool` | same |
| order | {P1, P2} either order, then P3 | P1 (11), P2 (13), P3 (15); `order_uniqueness` states the two commute | same |
| terminal state | three new service rows + verification | same | same |

Problem tree vs `prerequisite_closure` (value against value):
- root `ticket_ext_first_upgrade_charge` = auditor root P3.
- edge to `ticket_ext_same_day_change_fee`: kind value_input / gate fees_charged / form state / same sentence — equal. `why_false` evidence: exchange 6fe1ec4d… same_day_confirmed and no change-fee row — equal to the auditor's rows. `flips_to_true_by`: fee 17.55, fees charged 118.33 -> 135.88 — auditor recomputes 118.33 (29.33 + 89.00) and 135.88: equal.
- edge to `ticket_ext_seat_charge_correction`: value_input / up_seat_standing / state — equal. Evidence amount 89.0, miles 679; flips: refund 61.3, standing 89.00 -> 27.70 — equal.
- `resolution_order` [P1, P2, P3] — one of the auditor's two equivalent orders; `order_uniqueness` claim (commute, identical DB) — auditor replay: P1 17.55 and P2 61.30 in both orders, P3 69.19 in both: equal.
- `edge_load_bearing`: skip P1 -> 436.23 spend, 0.92, 77.17; skip P2 -> credit 89.00, 7.89 — auditor 77.17 and 7.89: equal.

Factors vs `computations` (figure against figure):
- P1 expected 17.55 (auditor 17.55); baseline_result 75.0 (75.00); sensitivity member 27.0 / delay 39.0 / fare 21.94 / direction 10.97 (auditor 27.00 / 39.00 / 21.94 / 10.97): all equal.
- P2 expected 61.3 (61.30); baseline 40.0 (40.00); sensitivity 49.43 / 56.42 / 59.85 / 59.67 (same): all equal.
- P3 expected 69.19 (69.19); baseline 149.0 (149.00); sensitivity credit 96.89 / spend 86.28 / member 79.95 / window 79.95 / day 86.28 (same): all equal.

Assertions of `design_rationale` checked against the world: seat 9C on segment 1 prices at exactly 29.33 (issue-date convention, 34 days -> 0.9; 49 × 0.7 × 0.9 × 0.95 = 29.33) — true; 12 flight accruals + 1 hotel accrual (13 rows) — true; 18-month window gives 9 flights — true; the 105-minute delay is below the 3-hour meal and goodwill thresholds — true; the employer agreement is active with zero balances — true. Author's claim "member-flight window method" — disputed on label, see findings.

Closest candidate exclusion (from policy/world, not from GT): see the frozen derivation (member rate 1, purchase-date advance days, long-segment First price) — each excluded by a named record and rule sentence.

Verdicts for task 0:
- Policy self-consistency: PASS on this world (charter-global SOURCE-POLICY REDs F1, F2, F3 cited from `_difficulty.md` § findings move no value here).
- Problem tree holds: PASS.
- Factors bear weight: **SOURCE-FACTOR RED** — P3 has no honest `method` factor (F4).
- Unique solution: PASS (independent derivation = GT on every item).

**Task 0 verdict: SOURCE-FACTOR RED.**

## findings

1. **SOURCE-FACTOR RED — P3 declares no genuine `method` factor.**
   - Symptom: the First upgrade computation's only `method` factor, `upgrade_member_flight_window`, selects among 24, 18 and 12 months for one and the same count.
   - Root cause: the ladder's tiers substitute a number (`within_months`) into one formula (`XCOUNT('loyalty','loyalty_activity', within_months=N, ...)`); by the skill's test that is a parameter; the charter-level fact is `_difficulty.md` § factor_ladders / F4.
   - Evidence: `ticket.extended.yaml` P3 `compute.up_member_flights` (three `XCOUNT` calls differing only in `within_months`), `factors[upgrade_member_flight_window].ladder` ("Summit flight accruals are counted over the last 24 / 18 / 12 months"); `computations[2].factor_trace[3]` labels it "(method, loyalty)".
   - Demonstrated consequence: counting only honest factors, P3 has 5 parameter factors and 0 method factors on this world, against the floor of 1 method per computation. (The factor does bear weight here: 12-month window -> 7 flights -> member rate 1 -> 79.95 vs 69.19 — the defect is its label, not its weight.)
   - Affected: `ticket.extended.yaml` → `extended_policies[ticket_ext_first_upgrade_charge].factors`; `tasks/0.json` → `computations[2]` (policy `ticket_ext_first_upgrade_charge`, step 15, arg `upgrade_fee`).
   - Relation to previous revisions: first audit of this difficulty.
2. Charter-global SOURCE-POLICY REDs F1 (P3->P1 zero-fee gap), F2 (P3->P2 sentence broader than condition), F3/O3 (P3 seat-standing sum) — cited from `_difficulty.md` § findings; demonstrated above to move nothing on this task's world. They stay open at the difficulty level.
3. Observation — `solvability_contract.gold_actions[step 13].base_preconditions` records the bag-delay gate `bag_delay_record` as `satisfied: true`, binding `ticket_disruptions.disruption_id` to the seat row's `source_disruption_id` (null) and to delay record 8641005c…; a charged-in-error seat refund rests on no disruption, so the gate is inapplicable rather than satisfied. No scored value depends on it.
4. Observation — persona says the extra-legroom seats were picked "in the app when you booked"; the records show seat purchases on 2026-08-19 and 2026-08-27 through `online`, issue on 2026-08-18. The rules read the records, the persona adds no number, so no second answer arises.
5. Observation — seeded Summit Silver history carries 927 qualifying dollars for 2025 against a 4,500 threshold (see `factor_weight`).

---

## revision_2

### source_derivation_frozen (revision 2)

- Hashes: `ticket.extended.yaml` `0d4f8d91c702a89830d19fd70fdc309d95effcea81dd0cb0adb66a8938053b21` (changed since revision 1); `task_tools.py` `9255fa2b…0783` (unchanged); masked view r2 `task_0.masked.json` `1a22a3ea1ce69eb6ab1a54f694e912716f964731654922fb4ca127d202022594`.
- Written 2026-09-24 ~18:57Z, before the round-2 task JSON was opened. Auditor as revision 1. Fields permitted/masked as revision 1.
- contamination_disclosure: this round is not blind with respect to revision 1's GT. The auditor read the round-1 `tasks/0.json` (evaluation_criteria, computations, prerequisite_closure, design_rationale) at the revision-1 reveal and its values are quoted in revision 1 of this file. The round-2 derivation below was recomputed from the round-2 charter and view with the auditor's own replay, but where a round-2 value equals a round-1 GT value the auditor's knowledge of it was prior. The round-2 task JSON and the worklogs were not read before this freeze.
- World delta vs revision 1 (auditor diff of r1/r2 masked views): only `user_scenario` changed — the seat line now reads "you picked extra-legroom seats online in the days after you booked". `initial_state` is byte-identical in content.

### policy_self_consistency (revision 2, this task)

Cites `_difficulty.md` § revision_2 (all subsections). Charter-global REDs of revision 1 that bore on this task (F1 P3->P1, F2, F3/O3, F4) are closed at the charter level. Latent observations R2-O1..O3 do not touch this task (no bags, no PE request). Handling time: P1 = 17.55 before or after P2's write; P2 = 61.30 before or after P1's write; P3 evaluated after both. No real-world waits (same seeded rows as revision 1). PASS.

### problem_chain (revision 2)

Root P3 (owner=user). Its two rewritten sentences, judged on the world:
1. "... not fixed until the latest same-day confirmed exchange recorded on the ticket carries its same-day change fee entry, whenever that exchange owes a same-day change fee." Latest (only) same-day exchange `6fe1ec4d-...`; P1 on the opening world owes 17.55 > 0; no `ticket_change_fee` row. False at the opening; resolved by P1's write.
2. "... fixed only after the latest seat charge on that segment carries a refund entry for any part of it charged in error above the seat price." Latest seat charge on segment 2 `3ddcb4d9-...` 89.00 vs P2 seat price 27.70; no refund row. False at the opening; resolved by P2's write.
Tree {P3; P1, P2}, both value_input (P1 via `up_same_day_fees`, P2 via `up_seat_standing` and `up_seat_refunds`), n = 2, acyclic, isomorphic to the declared `prerequisite`. Load-bearing (auditor replay): with both writes 69.19; skip P1 -> trip spend 246.63 < 250 -> spend rate 0.92 -> 77.17; skip P2 -> credit 89.00 -> 7.89; opening world 7.89. Parallel edges commute (P1 reads no seat row, P2 reads no change fee; P3 identical in both orders). Tools judge nothing. Persona raises only the root; the seat line is still answer-only-if-asked. PASS.

### task_independent_derivation (revision 2)

Identity, object, authorisation and timing as revision 1 (persona lines unchanged except the seat wording, which now matches `ticket_services` dates and `sales_channel: online`).
- P1: waiver rate — Silver active, does not waive, preferred seating, ticket names no agreement (`corporate_account_id: null`, so no waiving agreement), 7 flight accruals in 12 months -> 0.65; delay on segment 2 for the exchange's date 2026-09-24: 105 min -> 0.45; direction fare 189.60 -> 0.8. Fee **17.55**, `post_same_day_change_fee_61b8e8ae(2abfe7dc-..., 6fe1ec4d-..., "", 17.55)`.
- P2: latest seat charge on segment 2 `3ddcb4d9-...`; list 49; 0.7 × 0.85 (37 counted days, issue-date convention) × 0.95 -> 27.70; correction **61.30**, `refund_seat_charge_excess_9145fc3e(2abfe7dc-..., 3ddcb4d9-..., "", 61.30)`.
- P3 (after both): list 149 (679 miles); seat credit: latest seat charge 89.00 less the refund against it 61.30 = 27.70; trip spend = fare part (flown coupon -> 379.20 − 189.60 = 189.60) + every seat charge 118.33 + same-day fees 17.55 − seat refunds 61.30 = 264.18 -> >= 250, < 400 -> 0.85; member rate: Silver rank 5, 7 flight accruals in 12 months >= 6 -> 0.9; departure today -> 0.85. Charge = RND(149 × 0.85 × 0.9 × 0.85 − 27.70) = **69.19**; handed over as `purchase_first_upgrade_fa17fda8(2abfe7dc-..., 2, 679, 69.19)` (user). Opening-world contrast 7.89.
Order: verify -> {P1, P2} -> P3. Terminal state as revision 1. Closest alternatives excluded as revision 1, plus: fare part = whole fare 379.20 (spend 453.78 -> top band 0.8 -> 63.49) — excluded by the flown-coupon convention.

### factor_weight (revision 2)

- P1 (17.55; all-baseline 75.00): member 27.00, delay 39.00, fare band 21.94, direction-fare method 10.97. Multi-source member tier; loyalty cross-difficulty rows seeded; near-miss 2025-08-30 accrual and hotel accrual. 4 factors (3p/1m). PASS.
- P2 (61.30; all-baseline 40.00): member 49.43, advance 56.42, channel 59.85, advance-days method 59.67. 4 factors (3p/1m). PASS.
- P3 (69.19; all-baseline 149.00): seat credit 96.89; spend rate 86.28; **fare-part method** (baseline whole fare collected -> spend 453.78 -> 0.8) 63.49; member rate 79.95; departure day 86.28. Every factor bears weight; the fare-part method is an honest method (different operation per tier); near-miss: accruals older than 12 months (2025-08-30 and before) and the hotel accrual (a careless count gives 8, same tier), seat `ac7a7d39-...` on segment 1 (in the trip spend, not in the credit). No stamp. 5 factors (4p/1m). PASS.
Task level: multi-source and cross-difficulty present. Revision-1 finding 1 (P3 without an honest method) — closed on this world.

Result before reveal: all four relationships PASS.

### source_gt_comparison (revision 2)

- Reveal of the round-2 `tasks/0.json` after both round-2 derivations were on disk (sha256 at that moment: `_difficulty.md` `fe745b11…`, `task_0.md` `d66a405c…`, `task_1.md` `420cd510…`, taken at 2026-09-24T18:54:48Z immediately before the reveal command). As in revision 1, the "~18:57Z" written in the frozen header was an estimate; the hash bounds the freeze. Frozen text unchanged.
- Item by item: identity (step 1), reads, P1 args and 17.55 (step 11), P2 args and 61.3 (step 13), P3 segment 2 / 679 / 69.19 by the user (step 15), order and terminal state — **all same** as the frozen derivation. `charter_scope` = {P1, P2, P3} = auditor's scope.
- `computations` vs `factor_weight`, figure against figure: P1 17.55 / 75.0 / 27.0, 39.0, 21.94, 10.97; P2 61.3 / 40.0 / 49.43, 56.42, 59.85, 59.67; P3 69.19 / 149.0 / seat credit 96.89, spend 86.28, member 79.95, fare-part method 63.49, departure 86.28 — **all equal**.
- `prerequisite_closure` vs auditor tree: root, edges, kinds, form, sentences, conditions, resolved_by — equal; `resolution_order` [P1, P2, P3] is one of the two equivalent orders; `edge_load_bearing` 246.63 / 0.92 / 77.17 and 89.00 / 7.89 — equal. **One field differs**: edge P3->P1 carries `gate: "fees_charged"`, while the round-2 charter declares `gate: up_same_day_fees` and P3's round-2 compute has no binding named `fees_charged` (it was the round-1 binding). Its `flips_to_true_by` ("fees charged rise from 118.33 to 135.88") is still numerically true of the ledger (seat charges 118.33 plus the 17.55 fee), but names the retired quantity; the round-2 input is `up_same_day_fees` 0 -> 17.55. Stale proof field left by the rework — observation (no relationship's outcome depends on it; see findings).
- `design_rationale` assertions re-checked: trip spend 189.60 + 118.33 + 17.55 − 61.30 = 264.18; whole-fare baseline 453.78 -> 0.8 -> 63.49; 7 flights in 12 months; skip effects 246.63 / 77.17 and 7.89 — all true.

Verdicts (revision 2): policy self-consistency PASS; problem tree PASS; factors PASS; unique solution PASS.

**Task 0 verdict (revision 2): PASS.**

### findings (revision 2)

Closure of revision-1 items for this task:
- Finding 1 (SOURCE-FACTOR RED, P3 without an honest method) — **closed**: `upgrade_member_flight_window` removed; `upgrade_fare_part_convention` is a genuine method (subtraction of the flown coupons / halving / whole fare) and bears weight (63.49 vs 69.19).
- Finding 2 (charter F1/F2/F3 citations) — **closed** at the charter level (`_difficulty.md` § revision_2 findings).
- Observation 3 (`bag_delay_record` recorded as satisfied on a charged-in-error seat refund) — **unchanged**, as the rework states; still an observation.
- Observation 4 (persona "in the app when you booked") — **closed**: the line now reads "online in the days after you booked", matching seat purchases on 2026-08-19 and 2026-08-27 through `online`.
- Observation 5 (Silver tier vs 2025 qualifying dollars) — **unchanged**, observation.
New:
- R2-T0-O1 (observation; regression introduced by the rework) — `prerequisite_closure.edges[0].gate` = `fees_charged`, a binding that no longer exists in P3's compute; the charter's edge declares `up_same_day_fees`. Evidence: `tasks/0.json` `prerequisite_closure.edges[0]`; `ticket.extended.yaml` P3 `prerequisite[0].gate` and `compute`. Consequence: none on the scored solution or on the tree's truth (the edge is unmet at the opening and bears weight: 77.17 vs 69.19); the proof field simply names the retired binding and would mislead anyone reading the closure. Affected: `tasks/0.json` → `prerequisite_closure.edges[0].gate` and `.unresolved_at_frozen_time.flips_to_true_by`.
- No regression in the scored solution; no new RED.
