# Policy-task audit — ticket_changes_refunds_and_disruptions / charter-global

## charter_global_frozen

- Scenario: `env/env_0020_national_network_airline`; difficulty `ticket_changes_refunds_and_disruptions`; M = 2 (tasks 0 and 1).
- Auditor: independent audit subagent (Claude Opus 5.5), not the authoring agent; no answer supplied by the author or coordinator was accepted.
- Freeze time of this section: 2026-09-24T18:24Z (before any task GT was revealed).
- Freeze hashes (re-computed by the auditor, equal to the coordinator's brief):
  - `tasks/ticket_changes_refunds_and_disruptions/ticket.extended.yaml` sha256 `4a3e530dd49b6f5d7c021737b5722d93d2ec655c847908699c8d44bffbaa4650`
  - `tasks/ticket_changes_refunds_and_disruptions/task_tools.py` sha256 `9255fa2be82db05e4d669c1f8ec5eaf561327ac9bf6c8409dba915cadd8d0783`
  - masked view task 0 sha256 `a9e1ff8b639f555ee9e5eaa432d93c80f46131dc576543e5bd399f8471e913ef`; masked view task 1 sha256 `6d30d2bfafc1cfdf407ad44fb4e2aa8e8cd7f7d36779ec94be4adc3f7cd82abd`
- Fields permitted for this section: the whole extended charter (base copy + `extended_policies`), `task_tools.py`, `blueprint/` (blueprint.yaml, db_schema.json, share_tools.py, products/*.yaml), `erlbench/` and the expression evaluator of `skills/erl-task-instantiate/scripts/check_compute.py` (read for DAYS/MONTHS/LATEST/XCOUNT semantics only).
- Fields masked and not read: `tasks/*/tasks/0.json` and `1.json` in full, the difficulty `worklog.md`, the scenario `worklog.md`, sibling audits under `audits/policy_task/*`, the shared scratchpad of the authoring session. Nothing in this section is derived from a revealed GT.
- Entry conditions (Step 0): the brief carried the gate snapshot (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire — all rc=0 with their OK lines) and the masked views with hashes; check_traceability is deferred to the render stage by design. Entry conditions are met; the green gates are only the qualification to enter this audit.

Policy short names used below: P1 `ticket_ext_same_day_change_fee`, P2 `ticket_ext_seat_charge_correction`, P3 `ticket_ext_first_upgrade_charge`, P4 `ticket_ext_change_fee_posting`, P5 `ticket_ext_bag_sequence_charge`, P6 `ticket_ext_bag_weight_charge`, P7 `ticket_ext_premium_economy_upgrade_charge`.

### policy_conflict_scan

Subjects and targets (one policy per `(target_tool, computes)`):

| Policy | subject | trigger | target_tool / computes | scope sentence |
| --- | --- | --- | --- | --- |
| P1 | ticket_change_fee | state_due | post_same_day_change_fee_61b8e8ae / fee_amount | same-day confirmed exchange without a linked same-day fee, on a ticket naming no corporate agreement |
| P2 | ticket_fee_refund | state_due | refund_seat_charge_excess_9145fc3e / refund_amount | advance seat charge standing on the first unflown segment, charged above the seat price |
| P3 | ticket_upgrade_purchase | on_request | purchase_first_upgrade_fa17fda8 (owner=user) / upgrade_fee | paid First upgrade on the first unflown segment, bought by the ticket holder |
| P4 | ticket_change_fee | state_due | post_change_fee_ac050962 / fee_amount | latest standard exchange without a linked change fee |
| P5 | ticket_bag_charge | state_due | post_bag_sequence_charge_b2992c63 / charge_amount | bag of the first unflown segment with a weight/size entry but no first/second/third charge, ticket crediting no Summit membership |
| P6 | ticket_bag_charge | state_due | post_bag_weight_charge_02a99017 / charge_amount | heaviest bag with a first/second/third charge on the first unflown segment and no weight/size entry |
| P7 | ticket_upgrade_purchase | on_request | purchase_premium_economy_upgrade_2477ee45 (owner=user) / upgrade_fee | paid Premium Economy upgrade on the first unflown segment |

Overlaps examined:
- P1 vs P4 (both `ticket_change_fee`): disjoint by exchange type (P1 `same_day_confirmed`, P4 "voluntary, standard exchange"); distinct tools; no conflict.
- P5 vs P6 (both `ticket_bag_charge`): P5's bag carries a weight/size entry and lacks a sequence charge; P6's bag carries a sequence charge and lacks a weight/size entry — disjoint objects; distinct tools and distinct `service_type` written.
- P3 vs P7 (both `ticket_upgrade_purchase`): disjoint by cabin; distinct tools.
- Triggers/eligibility/time anchors: every state_due policy inherits the base status gates (seat and bag charges only on `ticketed`/`partially_flown` tickets; paid upgrade only on those statuses and unflown segments); no extended policy weakens them.
- Cross-category read boundaries: P1/P2/P3 read `loyalty` (holding status/variant/tier_basis/enrolled_date and `loyalty_activity`), P4/P5/P6/P7 read `business` (holding status/variant/spend/approved_date/point_balance and `business_activity`); each is declared in the policy's `cross_category`, scoped by the evaluator to the ticket's own customer.
- Cross-policy value couplings not carried by any prerequisite edge (observation O9 in `findings`): P3's trip spend reads every change, seat, bag and upgrade fee and every fee refund on the ticket, so P4, P5, P6 writes on the same ticket would move P3's spend band; P7's trip charges read seat charges and fee refunds, so P2's refund on a seat of the upgraded segment would move P7's credit. No declared edge or rule sentence fixes an order for those pairs. Neither task world instantiates such a pair (task 0 has no bags and no standard exchange; task 1 has no seat charge), so no scored value is moved.
- Gap (observation O7 in `findings`; P1 corporate gap also under F1): P1 sends a same-day change on a ticket naming an agreement to "the corporate-agreement rule", but no extended policy prices such a fee and the base `ticket_corporate_agreement_benefits` carries no fee formula.

Scopes of the M tasks (derived from each task's world and root request, before reveal): task 0 = {P3 root, P1, P2}; task 1 = {P7 root, P4, P5, P6}. The two scopes are pairwise disjoint and jointly cover all seven extended policies. The seven extended policies cover 5 of the 18 claimed event types (`ticket_change_fee`, `ticket_fee_refund`, `ticket_upgrade_purchase`, `ticket_bag_charge`, and exchanges only as read inputs); the rest of the claim is carried by base policies only — recorded as a fact, not a defect.

### rule_compute_equivalence

Mechanical facts (auditor script over the frozen yaml): every `compute_basis` value is a verbatim substring of its own policy's `rule` (0 misses across P1–P7); every `baseline.rule` sentence is a verbatim sentence of its `rule`; bindings without a `compute_basis` entry are pure bookkeeping (`next_segment`, `seat_kind_included`, `up_segment`, `trip_spend`, `seq_segment`, `seq_direction`, `w_segment`, `pe_segment`) — each is `flown + 1`, a sum of quoted terms or a restatement of a quoted clause, so none invents a basis.

Sentence-by-sentence sweep back (rule -> compute), per policy:
- P1: scope/linking/zero-not-recorded (tool contract), list fee `P('same_day_confirmed_change_fee')`, member tier ladder (3 tiers incl. `member_flights >= member_min_flights` over `XCOUNT(... within_months=12 ...)`), delay ladder over `MAX(arrival_delay_minutes, segment_number=next_segment, flight_date=NOW)`, direction-fare method (3 tiers), fare-band ladder, product rounded once at the end — every sentence implemented, every branch stated. Equivalent.
- P2: first-unflown-segment seat entry (`LATEST ... segment_number=next_seat_segment`), short/long list price by kind, correction floor at zero, member seat ladder, advance-days method (issue-date anchor / zero / purchase-date anchor), advance-rate ladder, channel ladder, product rounded to the cent, then correction rounded. Equivalent.
- P3: price by seat-entry distance, seat credit ladder, trip spend, spend ladder, window method, member ladder, departure-day ladder, product minus credit floored and rounded once. Latent divergence O3 below (`up_seat_paid` sums every seat charge on the segment; the rule says "the seat charged on the segment").
- P4: base fee by `origin_region`/`route_type`, agreement relief ladder, notice-days method, notice ladder, fare band, brand ladder, product rounded once. Latent divergence O2 below (`chg_exchange_date`/`chg_new_departure` read the latest standard exchange, the rule says the latest one "that has no change fee entry linked to it").
- P5: direction, channel, allowance (max, never added), list charge by place/route/channel, place-in-count method, posting/fare/channel ladders, product rounded once. Latent divergence O1 below (`seq_channel` reads the latest overweight/oversize entry on the segment, the rule says "its check-in channel is the channel of its weight or size entry").
- P6: heaviest first/second/third bag on the segment, recorded weight/size/channel "of its bag charge" (`w_tag` then per-tag LATEST), weight bands on the weight counted, size charge, higher-of-two, weight-counted method, points/fare/repeat/place ladders, product rounded once. Equivalent on the stated inputs.
- P7: PE price, corporate/travel-day/fare/lead ladders, trip-charges method, credit-share ladder, product minus credit floored and rounded once. Latent divergence O4 below (tier 1 of the trip-charges method: the rule counts "the change, seat, bag and upgrade charges ... of the whole itinerary"; compute adds only change fees without a segment filter).

Every tier named in `factors[].ladder` is a sentence of its rule and a branch of its `decides` binding, and every branch of each `decides` binding is a tier the rule states (checked for all 32 factors). No tier lives in one face only.

Latent rule/compute divergences (each demonstrated on a constructed world; each verified NOT to move any value on task 0's or task 1's world — see F3):
- O1 (P5 `seq_channel`): world — segment 2 carries bag A (overweight entry, `sales_channel` airport, dated D1, no sequence charge) and bag B (first_bag + overweight entry, `sales_channel` online, dated D2 > D1). Rule: A's channel is airport -> check-in rate 1.1. Compute: `LATEST('ticket_services','sales_channel', ..., service_type='overweight_bag', segment_number=seq_segment)` returns B's online -> 0.9. On task 1's world the only other overweight entry that can appear on segment 2 is P6's own write (call_center, same date as the airport entry); `LATEST` keeps the first row on a date tie (strict `>` in `check_compute.py` LATEST), so the airport row wins in all six orders of the three writes (auditor replay).
- O2 (P4 exchange selection): world — standard exchange E1 (no fee) and a later standard exchange E2 already carrying a linked change fee. Rule: fee owed for E1, notice days from E1's date to E1's new first departure. Compute: `LATEST(... exchange_type='standard_change')` = E2. Task 1 has a single standard exchange.
- O3 (P3 `up_seat_paid`): world — a released preferred seat ($24) and a standing extra-legroom seat ($49) on the upgraded segment. Rule: "the seat charged on the segment" = 49 -> credit 49. Compute: SUM of both = 73, refunds filtered to the latest kind -> credit 73. Task 0 has one seat charge on segment 2.
- O4 (P7 tier 1): an itinerary-level (segment 0) seat, bag or upgrade row is counted by the rule's "of the whole itinerary" but not by compute. The tool module only writes segment 0 for change fees, so no such row arises in this difficulty; recorded for completeness.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (table above); the seven task tools are the seven targets, one each.
- Owners: P1, P2, P4, P5, P6 targets are `owner="agent"`; P3 and P7 targets are `owner="user"` (the ticket holder, or for a company-held ticket the travel manager, per P7's rule and the tool docstring).
- Docstrings: none names another tool, none states a position in a sequence, none carries before/after/first as an ordering word ("first" appears only as an ordinal of bags/flights; "already recorded" and "not yet charged" describe the object's state). Each function body only builds and writes one row; no body reads a prerequisite, validates eligibility, status, dedup or computes a value (`task_tools.py` module docstring and all seven bodies read in full). Each tool writes the row its docstring promises: P1/P4 tools `segment_number=0`, `sales_channel="call_center"`, `related_transaction_id` set; P2 tool copies the refunded charge's `service_type` and `segment_number`, `fee_refund_reason="charged_in_error"`; P5/P6 tools copy segment/direction/weight/size from the first row carrying the tag, `sales_channel="call_center"`; P3/P7 tools write `ticket_upgrade_purchase` at the given segment.
- uuid8s: `61b8e8ae`, `9145fc3e`, `fa17fda8`, `ac050962`, `b2992c63`, `02a99017`, `2477ee45` — seven distinct values, no shared prefix or suffix, no sequential or adjacent pattern, none reused across tools. Consistent with independent generation.
- Business reading of each target: unique (one row of one kind per call, value passed in = value booked). No confirmation, review or wait outside the policy is added.

Result: PASS.

### prerequisite_graph

| Edge | kind | gate (binding exists?) | form | policy_source verbatim in own rule | resolved_by == depended-on target_tool | sentence absent from depended-on rule |
| --- | --- | --- | --- | --- | --- | --- |
| P3 -> P1 | value_input | `fees_charged` (yes) | state | yes | yes | yes |
| P3 -> P2 | value_input | `up_seat_standing` (yes) | state | yes | yes | yes |
| P7 -> P4 | value_input | `pe_trip_charges` (yes) | state | yes | yes | yes |
| P7 -> P5 | value_input | `pe_trip_charges` (yes) | state | yes | yes | yes |
| P7 -> P6 | value_input | `pe_trip_charges` (yes) | state | yes | yes | yes |

- P1, P2, P4, P5, P6 declare `prerequisite: []`; P3 and P7 declare the edges above. Every `problem` names an extended policy of this file (none base, none self). The graph is two disjoint stars rooted at P3 and P7 — acyclic.
- No edge carries `fallback_reason`, consistent with `form: state` on all five.
- `effect` statements: P3->P1 "adds its amount to the change ... fees ... which raises the trip spend and can move the spend rate to a lower band" — the same-day fee row is `event_type=ticket_change_fee`, summed by `fees_charged`: holds. P3->P2 "lowers the seat standing ... and the fees net of refunds": the refund row carries the seat's `service_type` and `segment_number` (tool body), so it enters `up_seat_standing` and `fees_refunded`: holds. P7->P4/P5/P6 "enters the trip charges of that segment": change fee rows are summed without a segment filter, bag rows by `segment_number=pe_segment` copied from the tag's first row (segment 2 in task 1): holds.
- `condition` vs sentence: P3->P1, P7->P4, P7->P5, P7->P6 — the condition restates the sentence at the same strength. P3->P2 — NOT the same scope: the sentence says "a refund entry stands against every seat charge on that segment for the part of it charged in error above the seat price"; the condition says "For the seat_purchase entry on the first unflown segment whose amount exceeds the seat price of the seat charge correction rule, a ticket_fee_refund entry ... names it". The sentence quantifies over every seat charge on the segment, the condition over the one entry P2 corrects. See F2.
- No authoring-viewpoint wording ("in this task", "at the opening") appears in any `prerequisite` field.

Result: structurally PASS except the P3->P2 scope mismatch (F2).

### prerequisite_sentences

Four-point test per edge (ordering connective / state named in record words with no actor or tool / no tool, policy id, snake_case or row id / strength equals condition):

1. P3->P1: "The First upgrade charge is not fixed until a same-day change fee entry stands on the ticket for every same-day confirmed exchange recorded on it." — connective "not ... until"; state "a same-day change fee entry stands ... for every same-day confirmed exchange" in ledger words; no tool/id; strength = condition. Writes that bring the state about: only P1's tool writes a `same_day_change_fee` row linked to an exchange (P4's tool writes `change_fee`). One write. Derivation a reader performs: P3's rule -> the ticket's fare history shows a same-day confirmed exchange with no same-day change fee entry on the service ledger -> the only rule whose result is "one same-day change fee entry linked to that exchange entry" is P1 -> post it, then price the upgrade. Single reading — except in the zero-fee situations of F1.
2. P3->P2: "The First upgrade charge on a segment is fixed only after a refund entry stands against every seat charge on that segment for the part of it charged in error above the seat price." — connective "only after"; state in ledger words; "the seat price" is P2's term; no tool/id. One write: P2's tool is the only writer of `charged_in_error` seat refunds. Derivation: P3's rule -> the upgraded segment's seat charge is above the seat price P2's rule gives -> P2's rule refunds "the excess ... as one fee refund entry against that seat charge" -> refund, then price. Single reading when the segment has one seat charge; scope defect F2 when it has more.
3. P7->P4: "The Premium Economy upgrade charge is fixed only after a change fee entry stands on the ticket for every standard exchange recorded on it." — passes the four points. One write (P4's tool). Derivation: fare history shows a standard exchange with no linked change fee -> P4 posts "one itinerary-level change fee entry linked to that exchange entry". Zero-fee defect F1.
4. P7->P5: "The Premium Economy upgrade charge is not fixed until every bag carrying a weight or size entry on the ticket also carries its first, second or third bag charge." — passes the four points. One write (P5's tool is the only writer of first/second/third rows). Scope defect F1 (P5 resolves only bags of the first unflown segment on tickets crediting no membership; the sentence covers every bag on the ticket).
5. P7->P6: "Before the Premium Economy upgrade charge is fixed, every bag whose bag charge records a weight or size above the limits must carry its weight or size entry." — connective "Before"; passes the four points. One write (P6's tool is the only writer of overweight/oversize rows). Scope and zero-charge defect F1.

No rule carries a second wording of any of these dependencies, no tool name, no other policy id; the depended-on rules (P1, P2, P4, P5, P6) do not restate the sentences (auditor substring check). No extended rule states a cross-problem order that grounds no edge. Base rules state orders that ground no task edge (e.g. `ticket_evt_seat_fees` "A seat already confirmed on the segment must be released before another is purchased"; `ticket_voluntary_change` change-fee linkage) — no task tree rests on a base sentence, so these are observations only.
Every edge is state form; no fallback to test.

### override_declarations

Base copy: the non-`extended_policies` part of `ticket.extended.yaml` is identical (parsed-YAML equality) to `blueprint/products/ticket.yaml`. Every `overwrite.superseded_clause` is a verbatim substring of the named base rule, the named base policy is in `base_policy_refs`, and every `replaced_by` is a verbatim substring of the extended rule (auditor script).

Sentence-by-sentence conclusions against each cited base policy (F = followed, D = handled differently and declared, U = handled differently and undeclared):
- P1 vs `ticket_same_day_change`: same-route/same-date/same-cabin definition F; brand permission F; window F (exchange already recorded); "The fee is same_day_confirmed_change_fee per passenger per direction, recorded as a same_day_change_fee entry linked to the exchange entry" D; tier/corporate waiver and "a waived fee is not recorded" F (P1 tier 1 = 0, "a fee worked out at zero is not recorded", corporate tickets sent elsewhere); no add-collect/residual F. vs `ticket_voluntary_change`: routing of same-day changes to the same-day rule F. vs `ticket_corporate_agreement_benefits`: waiver F (scope excludes agreement tickets); no-stacking F.
- P2 vs `ticket_evt_fee_refunds`: "reverses exactly one earlier fee entry ... refunds its full amount" D (partial refund); grounds list F (charged_in_error); "Each fee entry can be refunded at most once" F; "A service the passenger actually used is never refunded on request" F (unflown segment only). vs `ticket_evt_seat_fees`: advance_seat_selection semantics F (standard seat price 0 on Main Cabin); per-segment price sentence D; elite inclusion -> no charge F (P2 tier 1 = 0); "lowest applicable price" F.
- P3 vs `ticket_evt_paid_upgrade`: "for a fixed fee" (first sentence) — not named in the overwrite (observation O5 below); fee sentence D; brand permission F; status/unflown segment F; brand/refund/accrual unchanged F; complimentary-cabin exclusion F; not-provided refund F (n/a).
- P4 vs `ticket_voluntary_change`: fee sentence D; "A change fee is charged as a separate fee entry linked to the exchange entry, and a fee of zero is not recorded" F; "never deducted from a residual" F. vs `ticket_corporate_agreement_benefits`: waiver -> 0 F (tier 1); active-only F (every agreement tier requires active); vs `ticket_same_day_change` F (standard exchanges only).
- P5 vs `ticket_evt_bag_fees`: "Every checked bag is recorded ... amount of zero when ... inside the free allowance" F; sequence = measure + 1 D; free allowance most-generous, never added F (members excluded by scope); domestic first/second bag prices F (P5's list charge reproduces them); "on international itineraries the first and second bag fees for the route_type apply in every channel" D; third-bag clause — the multiplier also acts on it but the clause is not named (observation O6); status gate F. vs `ticket_corporate_agreement_benefits`: allowance competition F.
- P6 vs `ticket_evt_bag_fees`: separate entries on top of the sequence charge F; overweight bands D; oversize clause — the multiplier also acts on it but it is not named (observation O6); higher-of-two F; max-weight acceptance F. vs corporate F.
- P7 vs `ticket_evt_paid_upgrade`: as P3 (fee sentence D; "for a fixed fee" observation O5).

Disguised forms: no anonymous intermediate factor outside a declared overwrite; no 0/1 multiplier onto a base-fixed quantity (the zero tiers of P1/P4 restate base waivers); no dropped base branch. No rule or `compute_basis` calls a base output a "wrong value".

Result: no undeclared override whose merged semantics is not unique (O5, O6 are observations: in each the extended rule's own sentence names "the list charge"/"the price" as the multiplicand, so the merged reading is unique).

### factor_ladders

Structure per policy (label as declared; "multi" = every non-fall-through tier is a conjunction/disjunction over distinct records; "xd" = cross_difficulty):

| Policy | factor | label | tiers (values/methods) | multi | xd | stated in rule / in compute |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | same_day_member_rate | parameter | 0 / 0.65 / 1 | yes (holding status + tier param; tier 2 adds loyalty_activity count) | loyalty | yes / yes |
| P1 | same_day_delay_relief | parameter | 0 / 0.45 / 1 | no | – | yes / yes |
| P1 | same_day_fare_band | parameter | 0.5 / 0.8 / 1 | no | – | yes / yes |
| P1 | same_day_direction_fare | method | fare − flown / fare ÷ 2 / whole fare | no | – | yes / yes |
| P2 | member_seat_rate | parameter | 0 / 0.7 / 1 | yes | loyalty | yes / yes |
| P2 | seat_advance_purchase_rate | parameter | 0.85 / 0.9 / 1 | no | – | yes / yes |
| P2 | seat_channel_rate | parameter | 0.95 / 1.15 / 1 | no | – | yes / yes |
| P2 | seat_advance_days_convention | method | issue-date anchor / zero / purchase-date anchor | yes (seat channel + loyalty status + issue date) | – | yes / yes |
| P3 | upgrade_seat_credit | parameter | whole / 0.5 share / 0 | no | – | yes / yes |
| P3 | upgrade_spend_rate | parameter | 0.85 / 0.92 / 1 | no | – | yes / yes |
| P3 | upgrade_member_rate | parameter | 0.8 / 0.9 / 1 | yes | loyalty | yes / yes |
| P3 | upgrade_member_flight_window | method (declared) | 24 / 18 / 12 months | yes (tier_basis + enrolled_date) | loyalty | yes / yes |
| P3 | upgrade_departure_day_rate | parameter | 0.85 / 0.95 / 1 | no | – | yes / yes |
| P4 | change_agreement_relief | parameter | 0 / 0.6 / 1 | yes | business | yes / yes |
| P4 | change_notice_days_convention | method (declared) | days × 2 / floor(days × 1.5) / days × 1 | yes (status + approved_date + exchange row) | business | yes / yes |
| P4 | change_notice_rate | parameter | 0.8 / 0.9 / 1 | no | – | yes / yes |
| P4 | change_fare_band | parameter | 0.92 / 0.96 / 1 | no | – | yes / yes |
| P4 | change_brand_rate | parameter | 0.9 / 0.97 / 1 | yes | business | yes / yes |
| P5 | bag_posting_rate | parameter | 0.8 / 0.9 / 1 | yes | business | yes / yes |
| P5 | bag_fare_band | parameter | 0.9 / 0.95 / 1 | no | – | yes / yes |
| P5 | bag_check_in_channel_rate | parameter | 1.1 / 0.9 / 1 | no | – | yes / yes |
| P5 | bag_count_convention | method | whole-ticket count / charged-only count in direction / count in direction | yes | – | yes / yes |
| P6 | weight_counted_convention | method | recorded − 3 lb / round up to 5 lb / recorded | no | – | yes / yes |
| P6 | weight_points_rate | parameter | 0.8 / 0.9 / 1 | yes (status + balance, one holding row) | business | yes / yes |
| P6 | weight_fare_band | parameter | 0.95 / 0.97 / 1 | no | – | yes / yes |
| P6 | weight_repeat_rate | parameter | 1.2 / 1.1 / 1 | no | – | yes / yes |
| P6 | weight_count_place_rate | parameter | 0.9 / 0.95 / 1 | no | – | yes / yes |
| P7 | pe_corporate_upgrade_rate | parameter | 0.8 / 0.9 / 1 | yes | business | yes / yes |
| P7 | pe_travel_day_rate | parameter | 0.85 / 0.95 / 1 | no | – | yes / yes |
| P7 | pe_fare_band | parameter | 0.93 / 0.97 / 1 | no | – | yes / yes |
| P7 | pe_booking_lead_rate | parameter | 0.95 / 0.98 / 1 | no | – | yes / yes |
| P7 | pe_trip_charge_credit | parameter | 0.1 / 0.05 / 0 | yes | business | yes / yes |
| P7 | pe_trip_charges_measure | method | segment + itinerary-level / half of all / all | no | – | yes / yes |

Shape facts that hold everywhere: 4–6 declared factors per policy (P1 4, P2 4, P3 5, P4 5, P5 4, P6 5, P7 6); each ladder has three pairwise-disjoint tiers with the fall-through counted; no two tiers of one ladder share a value or method; every `decides` is an input binding, never `result`; binding sets are disjoint within each policy; every fall-through equals the factor's `baseline`, and every factor `baseline` is what the policy's `baseline.rule` gives for that input (the baseline rules are silent about every factor input, i.e. the list price with no rate, no credit, the plain day count and the per-direction count); every tier is stated in the rule with its condition and its value/method, and implemented in compute. Every `baseline.rule` is self-sufficient: it yields a definite list price or list charge from the records (P1 75 on Main Cabin; P2 charged − list seat price; P3 the First price by seat-entry distance; P4 the origin/route change fee; P5 the per-direction list charge; P6 the weight/size list charge on recorded weight; P7 the PE fee).

Declared counts: parameter 26, method 7 (one per policy), cross_difficulty 11 (loyalty 4: P1, P2, P3×2; business 7: P4×3, P5, P6, P7×2).

Structural defects (the tests of Step 2 that a charter-level reading already decides; whether a task is hurt is demonstrated in its own file):
- **Mislabelled `method` — P3 `upgrade_member_flight_window`.** Its three tiers compute the same quantity by the same formula, "Summit flight accruals are counted over the last N months", substituting N = 24, 18 or 12 (compute: the same `XCOUNT('loyalty','loyalty_activity', within_months=N, date_field='activity_date', event_type='loyalty_flight_accrual')` with only `within_months` changing). That is a number substituted into one formula — the skill's definition of a `parameter`. Struck as a method, P3 has no `method` factor. See F4.
- **Mislabelled `method` — P4 `change_notice_days_convention`.** Tiers: "twice the whole days from the exchange date to the first departure", "one and a half times those days, rounded down to a whole day", "those days as counted" — the one formula floor(k × days) with k = 2, 1.5, 1. Struck as a method, P4 has no `method` factor. See F4.
- **Unreal ladder — P5 `bag_count_convention`.** Tier 1 ("on a partially flown round trip whose next departure falls within the short-trip days of the first flown flight, it is the number of first, second and third bag charges on the whole ticket plus one") counts bags checked on the outbound toward the return bag's place. Checked-bag allowances and bag fees are set per passenger per direction — this charter says so itself (`parameter_schema`: "Checked bags included per passenger per direction"; base measure `ticket_msr_bags_checked_in_direction`: "on the same ticket and travel_direction") — and no carrier prices a return bag as a third bag because a bag was checked on the outbound. Tier 2 ("on a ticket naming an active agreement whose tier includes a corporate checked-bag allowance ... the number of those charges above zero in the bag's direction plus one") yields unlimited free bags: with a corporate allowance of 1 (e.g. Crestline Corporate Select, `corporate_free_checked_bags: 1`), the first bag is recorded at $0, so the second bag's charged count is 0, its place is 1 <= allowance 1 and its list charge is 0; the third bag is again place 1 and free, and so on. That contradicts the base "the single most generous allowance applies and allowances never add together" and is not a treatment any carrier publishes. See F5.
- **Unreal ladder — P6 `weight_count_place_rate`.** The overweight/oversize charge is scaled by the bag's place in the bag count (0.9 first bag, 0.95 second, 1 third or later). The place in the count is what the separate sequence charge prices; it has no bearing on what a carrier charges for the excess weight or size of that bag, and no carrier discounts an overweight fee because the bag was the first one checked. See F5.
- Doubtful but not red-lit (observations): P6 `weight_repeat_rate` (overweight fee surcharged when other weight/size entries already stand on the ticket — escalation of excess-baggage charges is at least a recognisable commercial rationale); P6 `weight_points_rate` and all fare-band ladders on fees (P1, P4, P5, P6, P7) — value-based relief for higher-paying or higher-volume customers is a recognisable practice even where the specific fee is unusual; P1 tier 2 uses "complimentary preferred seating" as a proxy for the Silver tier; P7 `pe_corporate_upgrade_rate` reads the agreement's long-haul discount on a short-haul ticket; P7 `pe_trip_charge_credit` tier 2 ("an active agreement that does not list that channel") can hold only on a ticket the business charter says is not booked under the agreement ("A ticket counts as booked under the agreement only when it was booked through one of the booking_channels_eligible"); P4 notice-days doubling is an odd vehicle for a tenure benefit (label defect recorded above).

### findings

**F1 — SOURCE-POLICY RED (charter-global): state-form prerequisite sentences wait on states that no write of this difficulty brings about in whole classes of situations.**
- Symptom: the blocked rule waits on "an entry stands for every X", while the depended-on rule writes that entry only for some X, or writes nothing when its value works out at zero.
- Root cause and evidence, edge by edge:
  - P7->P4. P7: "The Premium Economy upgrade charge is fixed only after a change fee entry stands on the ticket for every standard exchange recorded on it." P4: "a fee worked out at zero is not recorded" (and base `ticket_voluntary_change`: "a fee of zero is not recorded"). Crestline Main Cabin `change_fee_us_origin: 0`, so on every US-origin Main Cabin ticket with a standard exchange P4's result is 0 × rates = 0 and no entry is ever written; the same holds on any ticket naming an agreement whose tier has `change_fee_waiver: true` (Corporate Select and above; P4 tier 1 = 0).
  - P3->P1. P3: "The First upgrade charge is not fixed until a same-day change fee entry stands on the ticket for every same-day confirmed exchange recorded on it." P1: "a fee worked out at zero is not recorded" — P1 is 0 for Summit Gold and above (`same_day_change_fee_waived: true`) and for a delay of at least 120 minutes; and P1 does not price same-day changes on a ticket naming an agreement ("a ticket booked under an agreement is charged under the corporate-agreement rule"), which no policy of this difficulty prices.
  - P7->P6. P7: "Before the Premium Economy upgrade charge is fixed, every bag whose bag charge records a weight or size above the limits must carry its weight or size entry." P6 writes only for "the heaviest bag carrying a first, second or third bag charge on a ticket's first unflown segment", and "a charge worked out at zero is not recorded" — an airport-checked bag recorded at 51–53 lb is counted at 48–50 lb (scale tolerance) and prices at zero. A second overweight bag on the segment, an overweight bag on a flown segment, or a 51–53 lb airport bag is never given the entry the sentence waits on.
  - P7->P5. P7: "The Premium Economy upgrade charge is not fixed until every bag carrying a weight or size entry on the ticket also carries its first, second or third bag charge." P5 covers only "a bag of a ticket's first unflown segment ... on a ticket that credits no Summit membership".
- Demonstrated consequence (two passages, one situation): a US-origin Main Cabin ticket with one standard exchange whose holder asks for a Premium Economy upgrade. P7's own rule "prices a paid upgrade into Premium Economy that the ticket holder buys, on request"; read with P4's zero-fee sentence, P7's prerequisite sentence can never hold, so the charge is never fixed and the upgrade can never be sold. A second reader takes the zero fee as settled and prices the upgrade. Two conclusions (never sellable / sellable at the computed price) from the same records. The same construction works for each edge above.
- Affected artifacts: `ticket.extended.yaml` P3 and P7 `rule` prerequisite sentences and `prerequisite[].condition`; P1, P4, P5, P6 scope and zero-value sentences.
- Bears on: task 0 (P3->P1), task 1 (P7->P4, P7->P5, P7->P6). Whether it moves either task's scored solution is demonstrated in each task file.

**F2 — SOURCE-POLICY RED (charter-global): the P3->P2 prerequisite sentence is broader than its condition.**
- Evidence: sentence "a refund entry stands against every seat charge on that segment for the part of it charged in error above the seat price"; condition "For the seat_purchase entry on the first unflown segment whose amount exceeds the seat price of the seat charge correction rule, a ticket_fee_refund entry ... names it through refunded_service_id". P2 corrects only "the advance seat charge standing on a ticket's first unflown segment" (compute: `LATEST(... segment_number=next_seat_segment)`).
- Demonstrated consequence: segment with a released extra-legroom seat charge of $89 and a standing one of $89 (base `ticket_evt_seat_fees`: "A seat already confirmed on the segment must be released before another is purchased; the released seat's fee is not refunded"). The sentence requires a refund entry against both charges; P2 and the condition produce one; the First upgrade charge is fixed under the condition and never fixed under the sentence.
- Bears on: task 0.

**F3 — SOURCE-POLICY RED (charter-global, latent): three compute bindings do not implement the rule sentence they quote** — O1 (P5 `seq_channel`), O2 (P4 `chg_exchange_date`/`chg_new_departure`), O3 (P3 `up_seat_paid`), each demonstrated on a constructed world in `rule_compute_equivalence`. Bears on: task 1 (O1, O2), task 0 (O3). The auditor's replay shows none moves a value on either task world; the task files record this.

**F4 — SOURCE-FACTOR (charter-global structure): the only `method` factor of P3 and of P4 is a parameter by the skill's own test.** Evidence in `factor_ladders` (P3 window N = 24/18/12 months in one `XCOUNT`; P4 notice multiplier k = 2/1.5/1 in one floor(k × days)). With those struck, P3 and P4 each declare 0 honest `method` factors against the floor of 1. Bears on: task 0 (P3), task 1 (P4); red-lit per task in its own file.

**F5 — SOURCE-FACTOR (charter-global structure): unreal ladders — P5 `bag_count_convention` (tiers 1 and 2) and P6 `weight_count_place_rate`.** Evidence and demonstration in `factor_ladders`. Bears on: task 1 only.

Observations (no consequence demonstrable on either task world; not grounds for rework on their own):
- O5 — `ticket_evt_paid_upgrade` first sentence "A paid upgrade moves the passenger on one unflown segment into a higher cabin for a fixed fee" is not named in P3's or P7's `overwrite`; the named fee sentence is the one that gives the amount, so the merged reading is unique, and a reader who takes "fixed fee" literally lands on each policy's declared baseline, not on a third number.
- O6 — P5's multiplier also acts on base's third-bag and domestic clauses, P6's on base's oversize clause, which the overwrites do not name; each extended rule itself calls those amounts "the list charge" and applies the rates to "the bag's list charge", so the merged reading is unique.
- O7 — P3 prices by "the segment distance recorded on the segment's seat entry"; for a segment with no seat entry (e.g. a Main Cabin passenger in an included standard seat, if no zero entry is written) the rule gives no distance and the compute raises; P3 also names only "the ticket holder" as buyer, with no clause for a company-held ticket (P7 has one).
- O8 — Each extended rule states its baseline sentence and then the refining ladder for the same quantity (e.g. P5: "The bag's place in the count is the number of first, second and third bag charges in the bag's direction plus one ..." then "The bag's place in the count is set by one of three conventions ..."); this is the mandated baseline-plus-factor layout, and the ladder's specificity decides; the render stage must keep the ladder visibly governing.
- O9 — Cross-policy value couplings with no edge (P4/P5/P6 -> P3 trip spend; P2 -> P7 trip charges), see `policy_conflict_scan`.
- O10 — Doubtful-realism ladders listed at the end of `factor_ladders`.

## closing_checklist

Written after both reveals. Everything above this heading was on disk before any GT was read (sha256 of this file at the first reveal, 2026-09-24T18:29:26Z: `571fdc6cf7ec523504aed3ca8c9e75c46cf211759bd9309999c20c672c1bd4ff`); nothing above was edited afterwards except this appended section.

The difficulty does **not** close: not every task passes all four relationships.

| item | status |
| --- | --- |
| per-task files one-to-one with tasks, `_difficulty.md` alongside | yes: `task_0.md`, `task_1.md`; first revision, no older revision to preserve |
| every comparison section carries a PASS | no — task 0 SOURCE-FACTOR RED, task 1 SOURCE-FACTOR RED |
| extended policies fully covered; scopes pairwise disjoint; tools and GT closed | yes — task 0 {P1, P2, P3}, task 1 {P4, P5, P6, P7} (`charter_scope` of each task equals the auditor's derived scope); seven tools, seven independent uuid8s |
| each tree: 1–3 prerequisite problems, >= max(n−1, 1) value_input edges, an owner=user write, no cycle; difficulty graph acyclic | yes (task 0: n = 2, 2 value_input, root user; task 1: n = 3, 3 value_input, root user; two disjoint stars) |
| every computation: self-sufficient baseline, 4–6 honest factors (>= 2 parameter, >= 1 method), real ladders, each factor bearing weight, baseline ≠ gold | no — P3 and P4 have no honest method factor (F4); P5 `bag_count_convention` and P6 `weight_count_place_rate` are unreal (F5), leaving P5 with 3 factors and no method. Weight-bearing and baseline ≠ gold hold for all 32 factors on their worlds |
| policy self-consistency of the charter | no — SOURCE-POLICY RED F1 (prerequisite states unreachable in named situations), F2 (P3->P2 sentence broader than condition), F3 (latent rule/compute divergences O1–O3); none moves a scored value on task 0 or task 1 |
| unique solution | yes for both tasks (independent derivation equals GT on every item) |
| instantiation-stage gates re-run on the final form | not applicable — the artifacts were not changed by this audit and the difficulty does not close; the gate snapshot supplied with the brief (all rc=0) is the one on record |

Per-task verdicts: task 0 **SOURCE-FACTOR RED**; task 1 **SOURCE-FACTOR RED**. Charter-global: **SOURCE-POLICY RED** (F1, F2, F3) open at the difficulty level.

---

## revision_2

### charter_global_frozen (revision 2)

- Re-audit round 2 of the same difficulty, same auditor (independent audit subagent, Claude Opus 5.5). Revision 1 above is left untouched.
- Input hashes (re-computed by the auditor, equal to the coordinator's brief): `ticket.extended.yaml` sha256 `0d4f8d91c702a89830d19fd70fdc309d95effcea81dd0cb0adb66a8938053b21` (round 1 `4a3e530d…` — **changed**, so every charter-global section below is re-derived in full); `task_tools.py` sha256 `9255fa2be82db05e4d669c1f8ec5eaf561327ac9bf6c8409dba915cadd8d0783` (unchanged, so the tool-body and uuid8 conclusions are carried forward on that hash); masked views r2: task 0 `1a22a3ea…2594`, task 1 `74927bc0…df4f`.
- Section written 2026-09-24 ~18:55Z, before either round-2 task JSON was opened. Scratch work only under `/tmp/claude-1000/erl_coord_env0020/work/d1_auditor/`.
- Masked and not read before the round-2 freeze: both task JSONs (their round-2 form), both worklogs, sibling audits. Contamination carried from round 1 is disclosed in each task file.
- Gate snapshot (coordinator, round 2): EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK, all rc=0; traceability deferred. Entry conditions met.
- What moved in the charter (auditor's reading of the new yaml, not the rework list): P1 now also covers agreement tickets (waiver tier includes "an active agreement whose tier waives change fees") and targets "the latest same-day confirmed exchange", with "an exchange whose fee works out at zero owes no same-day change fee"; P2 names "the latest seat charge recorded for that segment"; P3 dropped `upgrade_member_flight_window` (member flights now a fixed 12-month count), added the method `upgrade_fare_part_convention`, rebuilt the trip spend (fare part + seat charges + same-day change fees − refunds against seat charges, 4-tier spend ladder), reads the seat standing by `refunded_service_id` of the latest seat charge, and names the travel manager as buyer on company-held tickets; P4 dropped `change_notice_days_convention` (plain day count), added the method `change_banding_fare_convention`, targets "the latest standard exchange" and "owes no change fee" at zero; P5 dropped `bag_count_convention` (base per-direction count restored, member tickets and elite allowance included, "each bag" of the first unflown segment), added the method `bag_banding_fare_convention`, and defines a segment-level check-in channel; P6 dropped `weight_count_place_rate`, added the parameter `weight_excess_rate`, "a bag whose charge works out at zero owes no weight or size charge"; P7 reads the itinerary-class discount, restricts trip charges to change, bag and upgrade charges of the first unflown segment plus segment-0 charges, and replaces the credit-share tier 2 with "an agreement under review that lists the ticket's booking channel"; all five prerequisite sentences rewritten (below). Base copy still parsed-identical to `blueprint/products/ticket.yaml`.

### policy_conflict_scan (revision 2)

- `(target_tool, computes)` pairs, subjects, triggers and owners unchanged from revision 1 (table there). Disjointness P1/P4 (exchange type), P5/P6 (object), P3/P7 (cabin) still holds.
- Closed gap: P1 now prices same-day fees on agreement tickets (tier 1 zero for waiving agreements; otherwise member/one), so no same-day fee is left without a pricing policy.
- Cross-policy couplings without an edge (revision-1 O9): P4/P5/P6 -> P3 closed (P3's trip spend no longer reads change, bag or upgrade fees other than same-day fees); P2 -> P7 closed (P7's trip charges no longer read seats or refunds). **Remaining**: P1 -> P7 — P7's trip charges sum `ticket_change_fee` rows at segment 0, which includes P1's same-day fee rows, and no P7 sentence waits on a same-day fee; on a ticket with an unfeed same-day exchange and a PE request, P7's credit depends on whether P1 posted first. Latent (task 1 has no same-day exchange). Observation R2-O1.
- New latent coupling (present in revision 1 too, missed there — recorded now): **P5 -> P6 object selection.** P6 charges "the heaviest bag carrying a first, second or third bag charge ... when that bag carries no weight or size entry"; P5's write gives a bag with a weight entry its first/second/third charge. World: segment bag X (first_bag, 60 lb, airport, no weight entry) and bag Y (overweight entry, 75 lb, no sequence charge). P6 first: heaviest charged bag is X -> X is charged; then P5 charges Y. P5 first: heaviest charged bag is Y, which already carries its entry -> P6 owes nothing and X is never charged; P7's sentence ("the heaviest bag charged by count on that segment must carry its weight or size entry") is then satisfied. Two terminal states and two PE prices, no sentence fixes the order. Not instantiated on task 1 (CR1047736 is 56 lb < CR1047735's 72 lb; auditor's six-order replay gives one terminal state). Observation R2-O2 (same class as revision-1 O9: coupling without an edge, hypothetical world).
- New latent: P5 now charges "each bag" of the segment lacking a sequence charge, and a bag's place is "the number ... already recorded in the bag's direction plus one", so with two such bags the order of the two writes decides which gets place 2 and which place 3 (per-bag arguments differ; totals equal). Task 1 has one such bag. Observation R2-O3.
- Scopes: task 0 = {P1, P2, P3}, task 1 = {P4, P5, P6, P7} (derived from worlds and root requests before reveal); disjoint, jointly complete.

### rule_compute_equivalence (revision 2)

Mechanical (auditor script): every `compute_basis` value is verbatim in its rule; every `baseline.rule` sentence is in its rule; no-basis bindings are bookkeeping only (`next_segment`, `seat_kind_included`, `up_segment`, `trip_spend`, `seq_segment`, `seq_direction`, `w_segment`, `pe_segment`). Every ladder tier is a rule sentence and a branch of its `decides` binding and vice versa (33 factors).

Revision-1 latent divergences:
- O1 (P5 channel) — **closed**: the rule now defines "the segment's check-in channel" (airport when any bag charge of that segment was paid at the airport, online when one was paid online and none at the airport, call center otherwise) and `seq_channel` counts exactly those rows; P6's call-center row cannot change it.
- O2 (P4 exchange) — **closed**: the rule now targets "the latest voluntary, standard exchange" and owes the fee "while no change fee entry is linked to that exchange"; `LATEST(... exchange_type='standard_change')` implements it.
- O3 (P3 seat standing) — **closed**: rule "the latest seat charge recorded for the segment less every refund entry against that charge"; compute `up_seat_id` = latest seat charge, refunds summed by `refunded_service_id=up_seat_id`.
- O4 (P7 itinerary-level charges) — **closed**: rule "the charges recorded against the first unflown segment plus the itinerary-level charges recorded against no segment"; compute sums change, bag and upgrade rows at `segment_number=pe_segment` and at `segment_number=0`.
New sweep of rewritten bindings: P1 `sd_exchange_date`/`delay_minutes` (flight date of that exchange), `agreement_waives`; P3 `up_fare_part`, `up_seat_fees`, `up_same_day_fees`, `up_seat_refunds`, 4-tier `spend_rate`, 12-month `up_member_flights`; P4 `chg_banding_fare` (taxes-out / unflown / collected), plain `chg_notice_days`; P5 `seq_elite_bags`, per-direction `seq_position`, `seq_banding_fare`; P6 `w_excess`, `w_excess_rate` (only when the weight component is recorded); P7 `pe_discount` by itinerary class, `pe_segment_charges`, `pe_under_review`, `pe_credit_share` — each implements its quoted sentence; no divergence found.

Remaining latent omission (revision-1 O7, first half): P3 still prices by "the segment distance recorded on the segment's seat entry"; a segment with no seat entry has no distance (`up_miles` None). The travel-manager half of O7 is closed. Observation, unchanged class.

### action_binding_and_uuids (revision 2)

`task_tools.py` unchanged (hash equal to round 1): revision-1 conclusions carried forward on that hash — one policy per `(target_tool, computes)`, silent docstrings, bodies that judge nothing, seven independent uuid8s. PASS.

### prerequisite_graph (revision 2)

| Edge | kind | gate (exists) | form | verbatim in own rule | resolved_by = target | absent from depended-on rule |
| --- | --- | --- | --- | --- | --- | --- |
| P3 -> P1 | value_input | `up_same_day_fees` (yes) | state | yes | yes | yes |
| P3 -> P2 | value_input | `up_seat_standing` (yes) | state | yes | yes | yes |
| P7 -> P4 | value_input | `pe_trip_charges` (yes) | state | yes | yes | yes |
| P7 -> P5 | value_input | `pe_trip_charges` (yes) | state | yes | yes | yes |
| P7 -> P6 | value_input | `pe_trip_charges` (yes) | state | yes | yes | yes |

Acyclic (two stars), no `fallback_reason`, no authoring-viewpoint wording. `effect` statements hold against the compute (P1's row is `service_type=same_day_change_fee` summed by `up_same_day_fees`; P2's refund names the seat charge through `refunded_service_id`, lowering `up_seat_standing` and `up_seat_refunds`; P4/P5/P6 rows land at segment 0 or the first unflown segment and enter `pe_segment_charges`). Condition vs sentence — all five now at the same scope (the revision-1 F2 mismatch is gone: both say "the latest seat charge"/"the latest seat_purchase entry"). PASS.

### prerequisite_sentences (revision 2)

Full four-point test on each rewritten sentence, plus the resolving write and its single reading:
1. P3->P1 "The First upgrade charge is not fixed until the latest same-day confirmed exchange recorded on the ticket carries its same-day change fee entry, whenever that exchange owes a same-day change fee." Connective "not ... until"; waited-on state in ledger words (an exchange carrying its fee entry); the "whenever ... owes" clause is decided by P1's own rule ("an exchange whose fee works out at zero owes no same-day change fee"), matching the condition's "owes a same-day change fee above zero under the same-day change fee rule"; no tool/id/snake_case. One write (P1's tool). Zero-fee and agreement-ticket situations of revision-1 F1 now resolve: nothing is owed, the clause is vacuous, the charge can be fixed.
2. P3->P2 "The First upgrade charge on a segment is fixed only after the latest seat charge on that segment carries a refund entry for any part of it charged in error above the seat price." "only after"; state in ledger words; scope "the latest seat charge" = P2's object "the latest seat charge recorded for that segment" = condition's "the latest seat_purchase entry". "for any part of it charged in error" reads as "for whatever part is in error" — when none is, no entry is awaited (condition: "When ... is charged above the seat price"). One write (P2's tool). Revision-1 F2 closed.
3. P7->P4 "The Premium Economy upgrade charge is fixed only after the latest standard exchange recorded on the ticket carries its change fee entry, whenever that exchange owes a change fee." Passes; scope equals P4's "latest" and its zero clause; one write. Revision-1 F1(a) closed (US-origin Main Cabin zero fee, waiving agreements: nothing owed).
4. P7->P5 "The Premium Economy upgrade charge on a segment is not fixed until every bag of that segment carrying a weight or size entry also carries its first, second or third bag charge." Passes; scope (bags of the upgraded segment = first unflown) equals P5's ("each bag of a ticket's first unflown segment"), member tickets now included in P5; one writer kind (P5's tool, one call per bag). Revision-1 F1(d) closed.
5. P7->P6 "Before the Premium Economy upgrade charge on a segment is fixed, the heaviest bag charged by count on that segment must carry its weight or size entry whenever it owes a weight or size charge." "Before"; state in ledger words; scope equals P6's ("the heaviest bag carrying a first, second or third bag charge on a ticket's first unflown segment") and its zero clause ("a bag whose charge works out at zero owes no weight or size charge"); one write. Revision-1 F1(c) closed. Latent object coupling with P5 noted as R2-O2.
No second wording, no tool name, no policy id in any rule; the depended-on rules do not restate the sentences; no extended rule states a cross-problem order grounding no edge. PASS.

### override_declarations (revision 2)

Base copy identical; every superseded clause verbatim in its base rule; every replacement verbatim in the extended rule. Changes against revision 1: P3 and P7 now also name base "A paid upgrade moves the passenger on one unflown segment into a higher cabin for a fixed fee." (revision-1 O5 **closed**); P5 no longer overrides the base sequence sentence (it follows it) and now names the third-bag clause; P6 now names the oversize clause (revision-1 O6 **closed for P6**, **partly** for P5: the multiplier still acts on base's domestic first/second-bag clause "on domestic itineraries a first bag costs first_bag_fee_domestic_online ... and a second bag costs second_bag_fee_domestic", which is not named — merged reading still unique because P5's rule calls that amount "the bag's list charge"; observation). P1's waiver tier now restates base `ticket_same_day_change` "or when the ticket's corporate agreement waives change fees" and base `ticket_corporate_agreement_benefits` waiver — followed. P5's allowance now includes the Summit elite allowance — follows base `ticket_evt_bag_fees`. No undeclared override with a non-unique merged reading. PASS.

### factor_ladders (revision 2)

| Policy | factor | label (honest?) | tiers | multi | xd |
| --- | --- | --- | --- | --- | --- |
| P1 | same_day_member_rate | parameter (yes) | 0 / 0.65 / 1 | yes | loyalty (+ business read) |
| P1 | same_day_delay_relief | parameter (yes) | 0 / 0.45 / 1 | no | – |
| P1 | same_day_fare_band | parameter (yes) | 0.5 / 0.8 / 1 | no | – |
| P1 | same_day_direction_fare | method (yes: minus flown / half / whole) | 3 | no | – |
| P2 | member_seat_rate | parameter (yes) | 0 / 0.7 / 1 | yes | loyalty |
| P2 | seat_advance_purchase_rate | parameter (yes) | 0.85 / 0.9 / 1 | no | – |
| P2 | seat_channel_rate | parameter (yes) | 0.95 / 1.15 / 1 | no | – |
| P2 | seat_advance_days_convention | method (yes: issue anchor / zero / purchase anchor) | 3 | yes | – |
| P3 | upgrade_seat_credit | parameter (yes) | whole / 0.5 / 0 | no | – |
| P3 | upgrade_spend_rate | parameter (yes) | 0.8 / 0.85 / 0.92 / 1 | no | – |
| P3 | **upgrade_fare_part_convention** (new) | method (yes: fare minus flown / half / whole — different operations on different inputs) | 3 | no | – |
| P3 | upgrade_member_rate | parameter (yes) | 0.8 / 0.9 / 1 | yes | loyalty |
| P3 | upgrade_departure_day_rate | parameter (yes) | 0.85 / 0.95 / 1 | no | – |
| P4 | change_agreement_relief | parameter (yes) | 0 / 0.6 / 1 | yes | business |
| P4 | change_notice_rate | parameter (yes) | 0.8 / 0.9 / 1 | no | – |
| P4 | **change_banding_fare_convention** (new) | method (yes: collected minus taxes / collected minus flown / collected) | 3 | no | – |
| P4 | change_fare_band | parameter (yes) | 0.92 / 0.96 / 1 | no | – |
| P4 | change_brand_rate | parameter (yes) | 0.9 / 0.97 / 1 | yes | business |
| P5 | bag_posting_rate | parameter (yes) | 0.8 / 0.9 / 1 | yes | business |
| P5 | bag_fare_band | parameter (yes) | 0.9 / 0.95 / 1 | no | – |
| P5 | bag_check_in_channel_rate | parameter (yes) | 1.1 / 0.9 / 1 | no | – |
| P5 | **bag_banding_fare_convention** (new) | method (yes: collected minus flown / base-fare field / collected) | 3 | yes (tier 2: no flown coupon + active agreement) | – |
| P6 | weight_counted_convention | method (yes) | 3 | no | – |
| P6 | weight_points_rate | parameter (yes) | 0.8 / 0.9 / 1 | yes | business |
| P6 | weight_fare_band | parameter (yes) | 0.95 / 0.97 / 1 | no | – |
| P6 | weight_repeat_rate | parameter (yes) | 1.2 / 1.1 / 1 | no | – |
| P6 | **weight_excess_rate** (new) | parameter (yes) | 0.5 / 0.8 / 1 | yes (component recorded + excess) | – |
| P7 | pe_corporate_upgrade_rate | parameter (yes) | 0.8 / 0.9 / 1 | yes | business |
| P7 | pe_travel_day_rate | parameter (yes) | 0.85 / 0.95 / 1 | no | – |
| P7 | pe_fare_band | parameter (yes) | 0.93 / 0.97 / 1 | no | – |
| P7 | pe_booking_lead_rate | parameter (yes) | 0.95 / 0.98 / 1 | no | – |
| P7 | pe_trip_charge_credit | parameter (yes) | 0.1 / 0.05 / 0 | yes | business |
| P7 | pe_trip_charges_measure | method (yes) | 3 | no | – |

Counts: P1 4 (3p/1m), P2 4 (3/1), P3 5 (4/1), P4 5 (4/1), P5 4 (3/1), P6 5 (4/1), P7 6 (5/1) — all within 4–6 with >= 2 parameter and exactly 1 honest method. Every ladder has >= 3 pairwise-disjoint tiers with distinct outcomes; every fall-through equals the factor `baseline`; every `baseline.rule` is self-sufficient.

Realism and label check of the new or changed ladders:
- `upgrade_fare_part_convention`: counting only the unflown fare of a partly flown ticket (half of a round trip with none flown) as the fare part of a spend measure is a coherent value measure for pricing an upgrade on the remaining trip. Real; honest method.
- `change_banding_fare_convention`: a corporate ticket banded on its negotiated pre-tax fare (the business charter's discounts apply to the base fare, `discount_applies_to_taxes: false`), a flown non-corporate ticket on its unflown fare, otherwise the fare collected — each condition is one the business weighs for the value a change fee is scaled by. Real; honest method.
- `bag_banding_fare_convention`: same logic for the bag fee band (unflown fare once flown; base fare for a corporate ticket not yet flown). Real within the charter's (doubtful, observation R1-O10) premise that bag fees are banded by fare; honest method.
- `weight_excess_rate`: a reduced charge for a small excess over the allowance and a graduated one up to 20 lb is a recognisable graduated excess-weight tariff; the tier applies only when the weight component is recorded. Real; honest parameter.
- `pe_trip_charge_credit` tier 2 (agreement under review listing the channel): `under_review` is a real agreement status (`db_schema.business_holdings.status`), and a reduced credit for an agreement under review is a coherent commercial treatment; the revision-1 concern (tier holding only on a ticket not booked under the agreement) is gone. Real.
- `pe_corporate_upgrade_rate` now reads the discount for the itinerary class (revision-1 O10 item closed).
- `bag_check_in_channel_rate` now keyed to the segment's check-in channel: bags of one segment are checked together at one place, so the segment-level channel is a real attribute.
Revision-1 F4 (P3 and P4 without an honest method) — **closed**: both mislabelled factors removed, each policy now has a genuine method. Revision-1 F5 (unreal `bag_count_convention`, `weight_count_place_rate`) — **closed**: both removed; P5 counts per direction as the charter's allowance and measure do. Still-doubtful ladders carried as observations (no change claimed): `weight_repeat_rate`, `weight_points_rate`, the fare-band rates on fees.

### findings (revision 2)

Revision-1 charter findings: F1 **closed** (all four sub-cases), F2 **closed**, F3 **closed** (O1, O2, O3), F4 **closed**, F5 **closed**. Observations: O4 closed, O5 closed, O6 closed for P6 and partly for P5 (domestic clause unnamed, merged reading unique), O7 half closed (buyer clause) / half open (no-seat-entry distance), O8 unchanged, O9 mostly closed (P1 -> P7 remains, R2-O1), O10 partly closed (itinerary-class discount, under-review tier) / rest unchanged.

New in revision 2 (no RED): R2-O1 (P1 -> P7 coupling), R2-O2 (P5 -> P6 object selection by order — a pre-existing coupling missed in revision 1), R2-O3 (order of two P5 bags on one segment). All latent; none instantiated on task 0 or task 1 (verified per task).

No charter-global RED remains in revision 2.

### closing_checklist (revision 2)

Written after the round-2 reveals; everything in `revision_2` above this heading was on disk before either round-2 task JSON was opened (sha256 of this file at that moment: `fe745b11f55d82bbc13bfa34a549f7077b1e7789e4e106690606d1dff93d4609`, 2026-09-24T18:54:48Z).

| item | status |
| --- | --- |
| per-task files one-to-one with tasks; revision 1 kept intact; each carries `revision_2` with a comparison | yes |
| every revision-2 comparison carries a PASS | yes — task 0 PASS, task 1 PASS |
| extended policies fully covered; scopes pairwise disjoint; tools and GT closed; independent uuid8s | yes (task 0 {P1, P2, P3}, task 1 {P4, P5, P6, P7}; tool module unchanged) |
| each tree: 1–3 prerequisite problems, >= max(n−1, 1) value_input, an owner=user write, acyclic; difficulty graph acyclic | yes (n = 2 / 2 value_input; n = 3 / 3 value_input; both roots owner=user) |
| every computation: self-sufficient baseline, 4–6 honest factors (>= 2 parameter, 1 method), real ladders, each factor bears weight, baseline ≠ gold | yes on both worlds (auditor recomputation: every one of the 33 substitutions moves its value; every all-baseline fall-back differs from gold) |
| charter self-consistency | no charter RED remains; revision-1 F1–F5 closed |
| instantiation-stage gates on the final form | re-run by the coordinator for round 2, all rc=0 (snapshot in the brief); this audit changed no artifact |

Open observations (not grounds for rework on their own): R2-O1 (P1 -> P7 coupling), R2-O2 (P5 -> P6 object chosen by write order, pre-existing, missed in revision 1), R2-O3 (order of two P5 bags on one segment), the O6 domestic-clause remnant, the O7 no-seat-entry distance gap, O8, the O10 remnants, task 0's stale `prerequisite_closure.edges[0].gate` (`fees_charged`, a rework regression in a proof field), task 0 observations 3 and 5.

Difficulty result (revision 2): all four relationships PASS for both tasks; the difficulty passes the source-layer audit, subject to the render-stage traceability gate that was deferred by design.

Post-reveal edit disclosure: after the reveal, the factor count in § rule_compute_equivalence (revision 2) was corrected from "31" to "33" (4+4+5+5+4+5+6), an arithmetic slip in the frozen text; nothing was derived from GT and no conclusion changed.
