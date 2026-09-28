# Policy-task audit — ticket_changes_refunds_and_disruptions / task 1

## source_derivation_frozen

- Freeze hashes: `ticket.extended.yaml` sha256 `4a3e530dd49b6f5d7c021737b5722d93d2ec655c847908699c8d44bffbaa4650`; `task_tools.py` sha256 `9255fa2be82db05e4d669c1f8ec5eaf561327ac9bf6c8409dba915cadd8d0783`; masked view `task_1.masked.json` sha256 `6d30d2bfafc1cfdf407ad44fb4e2aa8e8cd7f7d36779ec94be4adc3f7cd82abd`.
- Freeze time: 2026-09-24T18:50Z (before any task's GT was revealed; task 0's derivation was frozen first and no GT of either task had been read). Auditor: independent audit subagent (Claude Opus 5.5).
- Fields permitted: `task_index`, `frozen_time`, `user_scenario`, `initial_state` (through the masked view), the extended charter, `task_tools.py`, `blueprint/`, `erlbench/`, the evaluator helpers of `check_compute.py`.
- Fields masked and not read before this freeze: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state`, the task JSON file itself, both worklogs, sibling audits.
- contamination_disclosure: none. The brief carried no scored value; no recursive search touched `tasks/*/tasks/*.json`; the worklogs were not opened.
- Method: as in task 0 — the auditor's own writes replayed through the real tool functions, each policy's `compute` evaluated on the handling-time world with the evaluator's semantics.

### policy_self_consistency (this task only)

Charter-global conclusions this task rests on (cited, not restated): `_difficulty.md` § policy_conflict_scan, § rule_compute_equivalence, § action_binding_and_uuids, § prerequisite_graph, § prerequisite_sentences, § override_declarations, § factor_ladders, § findings.

Consequence of each charter-global finding that bears on this task, demonstrated on this world:
- F1 / P7->P4 (zero change fee): the ticket's `origin_region` is `outside_united_states` (the journey began in Toronto; base `ticket_voluntary_change` updates `origin`/`destination` on exchange but not `origin_region`), so the base fee is the non-US short-haul fee 125 and P4 evaluates to 49.68 ≠ 0; Business Connect Plus has `change_fee_waiver: false`. The entry is written; no consequence.
- F1 / P7->P5 (sequence charge only on the first unflown segment, non-member tickets): the only bag with a weight/size entry and no sequence charge is CR1047736 on segment 2 (first unflown), and the ticket credits no membership (`membership_id: null`). No consequence.
- F1 / P7->P6 (heaviest bag only; zero charge for 51–53 lb airport bags): the only bag whose sequence charge records a weight above 50 lb without a weight entry is CR1047735 (72 lb, segment 2) — the heaviest; counted 69 lb, first band, non-zero. After P5's write CR1047736 (56 lb) carries its sequence charge and already has its weight entry. Segment 1's bag CR1039921 is 44 lb / 58 in. No consequence.
- F3 / O1 (P5 `seq_channel` not tag-scoped): auditor replay of all six orders of the three prerequisite writes gives P5 = 133.65 every time (P6's call-center overweight row ties on date with CR1047736's airport row; LATEST keeps the earlier row). No consequence.
- F3 / O2 (P4 latest standard exchange): one standard exchange (`e8b3cd9b-...`). No consequence.
- F4 (P4's only `method` factor is a parameter) and F5 (P5 `bag_count_convention`, P6 `weight_count_place_rate` unreal): bear on this task; demonstrated under `factor_weight`.
- Override declarations: P4–P7 conclusions in `_difficulty.md` § override_declarations. O6: base's third-bag clause, read alone, would say the third bag "costs" 150; P5's own rule calls that amount "the bag's list charge" and applies the rates to it, so the merged reading gives one number. No second defensible answer.

Handling time: P4, P5, P6 are evaluated on the opening world; none reads a row another of them writes in a way that moves its value (auditor replay: P4 = 49.68, P5 = 133.65, P6 = 75.24 in every one of the six orders). P7 is evaluated after all three and before its own write.

Real-world waits: none. Every consumed fact is seeded (exchange `e8b3cd9b-...`, flown coupon `b8421c9c-...`, bag rows `850f233c-...`, `dbd8394c-...`, `6de602dd-...`, business holding `8ce9157a-...` and its activity) or a synchronous effect of an earlier write of this task.

Result for this task: PASS on this relationship (charter-global REDs F1, F3 move nothing on this world).

### problem_chain

Walk from the root:
- Root P7 (Premium Economy upgrade, `purchase_premium_economy_upgrade_2477ee45`, owner=user). Its rule carries three prerequisite sentences:
  1. "The Premium Economy upgrade charge is fixed only after a change fee entry stands on the ticket for every standard exchange recorded on it." `ticket_transactions.e8b3cd9b-1692-46e2-bc4f-beb666f92a36` is a `standard_change` exchange (2026-09-15); `ticket_services` holds no `ticket_change_fee` row. False at the opening; P4's rule describes the write.
  2. "The Premium Economy upgrade charge is not fixed until every bag carrying a weight or size entry on the ticket also carries its first, second or third bag charge." Tag CR1047736 carries `overweight_bag` row `6de602dd-...` and no first/second/third row. False at the opening; P5's rule describes the write.
  3. "Before the Premium Economy upgrade charge is fixed, every bag whose bag charge records a weight or size above the limits must carry its weight or size entry." Tag CR1047735's `first_bag` row `dbd8394c-...` records 72 lb (> 50) and the tag has no overweight/oversize row. False at the opening; P6's rule describes the write.
- P4, P5, P6 carry no prerequisite sentence; the walk stops.

Derived tree: nodes {P7 root, P4, P5, P6}; edges P7->P4, P7->P5, P7->P6, all value_input (each write's amount enters `pe_trip_charges` and so the trip-charge credit). n = 3, value_input edges 3 >= max(n−1, 1) = 2. Acyclic. Topological order: {P4, P5, P6} in any order, then P7. Isomorphic to P7's declared `prerequisite`.

Load-bearing (auditor replay): all resolved P7 = 29.67; skip P4 -> 34.64; skip P5 -> 43.03; skip P6 -> 37.19; opening world -> 55.52. Every edge moves the root.

Parallel edges: P4, P5, P6 write different rows; the only cross-read is P5's `seq_channel` over overweight rows on the segment (F3/O1), shown above not to move P5 in any order. Six orders -> one terminal state.

No-wait: all three resolving writes are synchronous ledger entries.

Tool layer: the four tool bodies create one row each and judge nothing (`task_tools.py`).

Customer's own write: the root P7 is `owner="user"`; the persona completes the purchase when handed over ("When the agent hands the purchase over to you, you complete it yourself with the details the agent reads out").

Persona and the tree: Denise raises only the root ("you would like to upgrade Mara to Premium Economy on her flight home tonight ... That is the only thing you are calling for."). Bags and the change come out only on the agent's question. "If the agent explains that some charges on the ticket have to be posted before the upgrade can be priced, you accept that as the company's to pay" is passive, conditional consent. The persona closes after the upgrade. No ask outside the charter.

Result: PASS.

### task_independent_derivation

Need, object, authorisation, timing: Denise Ashford, travel manager (`business_holdings.8ce9157a-...travel_manager_name`), speaks for Bramlett Hydraulics Co. (`customers.9ea68524-...`), the holder of ticket DK4TRW (`050efc00-...`, Main Cabin, `partially_flown`, `corporate_account_id` = the Business Connect Plus agreement). Object: segment 2, DEN->YYZ tonight 17:10. She wants the upgrade and will pay; she accepts charges the agent says must be posted. P7's rule: "for a company-held ticket the company's travel manager, confirms and pays it in person". Act now: frozen 2026-09-24 14:20 MDT, before departure; status and brand permit a paid upgrade.

Identity: `verify_customer_identity(customer_id=9ea68524-af3a-4ab4-be09-81fd8239ab59, phone_number=7165551934, postal_code=14203)`.

P4 — change fee (agent, owed on sight); opening world.
- Base fee: journey originates outside the US, short-haul international -> Main Cabin `change_fee_non_us_origin_short_haul` 125.
- Agreement relief: active Connect Plus, no waiver, spend this agreement year 31,480 >= threshold 25,000 -> 0.6.
- Notice days (declared method): agreement approved 2025-02-10, 582 days before the 2026-09-15 exchange (>= 365) -> 2 × DAYS(2026-09-15, 2026-09-24) = 18 -> >= 14 -> 0.8.
- Fare band: fare collected 658.36 -> >= 600 -> 0.92.
- Brand rate: Main Cabin in the agreement's discount-eligible brands -> 0.9.
- Fee = RND(125 × 0.6 × 0.8 × 0.92 × 0.9) = **49.68**. Write `post_change_fee_ac050962(ticket_id=050efc00-98b5-4fa8-8413-06c136c9568d, related_transaction_id=e8b3cd9b-1692-46e2-bc4f-beb666f92a36, corporate_account_id=8ce9157a-acea-487f-8890-187199e8bb46, fee_amount=49.68)`.

P5 — sequence charge for CR1047736 (agent); opening world.
- Direction return (partially flown round trip); channel airport (its overweight entry).
- Allowance: short-haul international 0; corporate bags 0 -> 0.
- Place in count (method): partially flown round trip, first flown flight 2026-09-21, next departure 2026-09-24 (3 <= 7 days) -> first/second/third charges on the whole ticket (CR1039921, CR1047735) + 1 = 3.
- List charge: third bag on a short-haul itinerary -> 150.
- Posting rate: spend postings within 6 months — 2026-05-06, 2026-07-22, 2026-09-21 = 3 (2026-03-12 outside; points accruals are not spend postings) -> 0.9. Fare band 658.36 -> 0.9. Channel airport -> 1.1.
- Charge = RND(150 × 0.9 × 0.9 × 1.1) = **133.65**, position 3. Write `post_bag_sequence_charge_b2992c63(ticket_id=050efc00-..., bag_tag_number=CR1047736, corporate_account_id=8ce9157a-..., bag_sequence_position=3, charge_amount=133.65)`.

P6 — weight charge for CR1047735 (agent); opening world.
- Heaviest first/second/third bag on segment 2: CR1047735, 72 lb, 59 in, airport, first_bag.
- Weight counted (method): airport -> 72 − 3 = 69 -> > 50, <= 70 -> first band 100. Size 59 <= 62 -> 0. Component overweight_bag, list 100.
- Points: active agreement, balance 18,420 >= 15,000 -> 0.8. Fare band -> 0.95. Repeat: one weight/size entry already on the ticket (`6de602dd-...`) -> 1.1. Place: first bag -> 0.9.
- Charge = RND(100 × 0.8 × 0.95 × 1.1 × 0.9) = **75.24**. Write `post_bag_weight_charge_02a99017(ticket_id=050efc00-..., bag_tag_number=CR1047735, corporate_account_id=8ce9157a-..., charge_component=overweight_bag, charge_amount=75.24)`.

P7 — Premium Economy upgrade (user); after the three writes.
- Price: Main Cabin PE fee 99. Corporate rate: long-haul discount 5% (>= 1, < 10) -> 0.9. Travel today -> 0.85. Fare band 658.36 -> 0.93. Booking lead: issued 2026-09-02, first flight 2026-09-21 = 19 days -> >= 7, < 21 -> 0.98.
- Trip charges (method): one flown coupon -> segment-2 charges 35.00 + 100.00 + 133.65 + 75.24 plus itinerary-level change fee 49.68, less segment-2 refunds 0 = 393.57.
- Credit share: corporate_booking_tool listed by Connect Plus -> 0.1 -> credit 39.357.
- Charge = RND(max(0, 99 × 0.9 × 0.85 × 0.93 × 0.98 − 39.357)) = RND(69.0249 − 39.357) = **29.67**. Opening-world contrast: 55.52 (trip charges 135.00 only). 29.67 is right because P7 is fixed only after the three states hold.
- Hand-over: the customer runs `purchase_premium_economy_upgrade_2477ee45(ticket_id=050efc00-..., segment_number=2, upgrade_fee=29.67)`.

Write sequence and owners: verify (agent) -> {P4, P5, P6} (agent) in any order -> P7 (user). Terminal state: change fee 49.68 (segment 0, linked to e8b3cd9b); third_bag 133.65 for CR1047736 (segment 2, return); overweight_bag 75.24 for CR1047735 (segment 2); upgrade_premium_economy 29.67 on segment 2; verified identity row.

Reachability: all inputs are readable via `find_ticket_holdings`, `find_ticket_transactions`, `find_ticket_services`, `find_business_holdings`, `find_business_activity` or stated by the persona (travel manager name, company verification details).

Closest alternative candidates and their exclusion: (a) US-origin fee 0 read off `origin: DEN` — excluded by `origin_region: outside_united_states` ("whether the journey originates in the United States") and the persona's "flight back to Toronto"; (b) place 2 (per-direction count, second bag 65 -> 57.92) — excluded by the short-trip convention; (c) weight counted at 72 lb (second band 200 -> 150.48) — excluded by the airport tolerance convention; (d) trip charges including segment 1's 35.00 bag (428.57 -> 26.17) — excluded by the segment convention (observation: the phrase "charges of the first unflown segment and of the whole itinerary" could be read as "all charges"; that reading makes tier 1 coincide with tier 3's "every ... charge on the ticket", and P4's rule names its entry "itinerary-level", so the reader is steered to segment 2 + itinerary-level charges).

Result: act now; unique solution as above.

### factor_weight

P4 (result 49.68; all-baseline fall-back 125.00 ≠ 49.68):

| factor | label honest? | tier / records | baseline | value at baseline |
| --- | --- | --- | --- | --- |
| change_agreement_relief | parameter, yes | tier 2 (0.6): holding `8ce9157a` active, spend 31,480 >= 25,000 (business) | 1.0 | 82.80 |
| change_notice_days_convention | declared method — **not honest** (k = 2 / 1.5 / 1 in one floor(k × days); F4) | tier 1: approved 582 days before exchange -> 18 | 9 days | 55.89 |
| change_notice_rate | parameter, yes | tier 1 (0.8) | 1.0 | 62.10 |
| change_fare_band | parameter, yes | tier 1 (0.92): 658.36 | 1.0 | 54.00 |
| change_brand_rate | parameter, yes | tier 1 (0.9): Main Cabin eligible (business) | 1.0 | 55.20 |

Near-miss: the flown coupon 329.18 (a reader netting it drops the fare below 400); `base_fare` 540 vs fare collected 658.36; `origin: DEN` vs `origin_region`. No stamp. Counts after tests: 5 declared, **0 honest method** -> **SOURCE-FACTOR RED** (F4).

P5 (result 133.65; all-baseline fall-back 65.00 ≠ 133.65):

| factor | label honest? | tier / records | baseline | value at baseline |
| --- | --- | --- | --- | --- |
| bag_posting_rate | parameter, yes | tier 2 (0.9): 3 spend postings in 6 months (business) | 1.0 | 148.50 |
| bag_fare_band | parameter, yes | tier 1 (0.9) | 1.0 | 148.50 |
| bag_check_in_channel_rate | parameter, yes | tier 1 (1.1): airport | 1.0 | 121.50 |
| bag_count_convention | method, label honest — **ladder unreal** (F5) | tier 1: short round trip -> whole-ticket count -> place 3 | per-direction count -> place 2 | 57.92 |

The taken tier is exactly the unreal one: it prices Mara's second return bag as a third bag (150 list) because a bag was checked on the outbound three days earlier, where every carrier — and this charter's own per-direction allowance and measure — would count it as the second bag in the return direction (65 list). Near-miss: 2026-03-12 spend posting (outside 6 months), the two points accruals (not spend postings), CR1047736's own overweight row (not a sequence charge). No stamp. Counts after tests: the method factor is struck -> 3 factors (< 4) and 0 method -> **SOURCE-FACTOR RED** (F5).

P6 (result 75.24; all-baseline fall-back 200.00 ≠ 75.24):

| factor | label honest? | tier / records | baseline | value at baseline |
| --- | --- | --- | --- | --- |
| weight_counted_convention | method, yes (subtract / round up / identity) | tier 1: airport -> 69 lb | recorded 72 lb -> second band 200 | 150.48 |
| weight_points_rate | parameter, yes | tier 1 (0.8): balance 18,420 (business) | 1.0 | 94.05 |
| weight_fare_band | parameter, yes | tier 1 (0.95) | 1.0 | 79.20 |
| weight_repeat_rate | parameter, yes (realism doubtful, observation) | tier 2 (1.1): one weight entry on the ticket | 1.0 | 68.40 |
| weight_count_place_rate | parameter — **ladder unreal** (F5) | tier 1 (0.9): the bag's charge is a first bag | 1.0 | 83.60 |

Near-miss: CR1039921 (flown segment, 44 lb) and CR1047736 (already carries its weight entry). No stamp. Counts after tests: 4 surviving factors (1 method, 3 parameter) — within bounds, but the unreal `weight_count_place_rate` is itself **SOURCE-FACTOR RED** (F5).

P7 (result 29.67; all-baseline fall-back 99.00 ≠ 29.67):

| factor | label honest? | tier / records | baseline | value at baseline |
| --- | --- | --- | --- | --- |
| pe_corporate_upgrade_rate | parameter, yes | tier 2 (0.9): Connect Plus long-haul discount 5 (business) | 1.0 | 37.34 |
| pe_travel_day_rate | parameter, yes | tier 1 (0.85) | 1.0 | 41.85 |
| pe_fare_band | parameter, yes | tier 1 (0.93) | 1.0 | 34.86 |
| pe_booking_lead_rate | parameter, yes | tier 2 (0.98): 19 days | 1.0 | 31.08 |
| pe_trip_charge_credit | parameter, yes | tier 1 (0.1): channel listed (business) | 0 | 69.02 |
| pe_trip_charges_measure | method, yes | tier 1: flown coupon -> segment + itinerary-level | all charges 428.57 | 26.17 |

Near-miss: segment 1's bag charge 35.00 (excluded by the segment convention). No stamp. Counts: 6 factors, 5 parameter, 1 method, multi-source (corporate rate, credit share), cross-difficulty — PASS.

Cross-difficulty rows read (business holding `8ce9157a-...` and `business_activity` rows) are seeded. Observations: the ticket's `payment_form: corporate_invoice` sits under a tier with `invoice_billing_permitted: false` (no ladder reads it); the two points accruals (9,210 each) do not match `points_per_dollar: 1` against the seeded spend postings, but any consistent balance would still exceed 15,000, so the points tier is unchanged.

Result: SOURCE-FACTOR RED (P4 without an honest method factor; P5 `bag_count_convention` unreal and, once struck, P5 below 4 factors and without a method; P6 `weight_count_place_rate` unreal).

## source_gt_comparison

- Reveal: `tasks/ticket_changes_refunds_and_disruptions/tasks/1.json` opened after task 0's comparison was written and after both task derivations were frozen (hash of this file at the moment of the first reveal, 2026-09-24T18:29:26Z: `8961b5c8...`). Timestamp correction, stated rather than edited: the "Freeze time" line inside the frozen section (18:50Z) was an estimate typed before the clock was read; the freeze is bounded by that hash. The frozen text is unchanged.

Item-by-item:

| item | auditor (frozen) | GT | same? |
| --- | --- | --- | --- |
| need / authorisation / timing | travel manager buys PE on segment 2 tonight, company pays, consents to owed charges, act now | same (step 14 by `user`) | same |
| identity | verify company with phone 7165551934 + ZIP 14203 | step 1 same | same |
| read set | ticket holdings, transactions, services, business holding, business activity | same (+ `find_customers`) | same |
| P4 | exchange e8b3cd9b…, agreement 8ce9157a…, 49.68 | step 8 same | same |
| P5 | CR1047736, position 3, 133.65 | step 10 same | same |
| P6 | CR1047735, overweight_bag, 75.24 | step 12 same | same |
| P7 | segment 2, 29.67, owner user | step 14 same | same |
| order | {P4, P5, P6} any order, then P7 | P4, P5, P6, P7; `order_uniqueness` says the three commute | same |
| terminal state | four new service rows + verification | same | same |

Problem tree vs `prerequisite_closure` (value against value):
- root `ticket_ext_premium_economy_upgrade_charge` = P7.
- edge to P4: value_input / pe_trip_charges / state / same sentence; why_false rows e8b3cd9b… (standard_change) and "only bag rows" — equal; flips: 49.68 — equal.
- edge to P5: same fields; why_false CR1047736 overweight row 6de602dd… with no sequence charge — equal; flips: third_bag 133.65 — equal.
- edge to P6: same fields; why_false dbd8394c… 72 lb, CR1047735 — equal; flips: overweight 75.24 — equal.
- `edge_load_bearing`: trip charges 343.89 / 259.92 / 318.33, upgrade 34.64 / 43.03 / 37.19 — auditor 393.57 − 49.68 = 343.89, − 133.65 = 259.92, − 75.24 = 318.33; 34.64 / 43.03 / 37.19: equal.
- `order_uniqueness` "none reads what another writes. An actual replay of all 6 orders gave one terminal DB hash and the same upgrade charge 29.67" — the conclusion matches the auditor's six-order replay (P4 49.68, P5 133.65, P6 75.24, P7 29.67 in every order). The stated reason is not literally true: P5's `seq_channel` reads overweight rows on the segment, which is the row kind P6 writes; the value is unchanged only because P6's call-center row ties on date with CR1047736's airport row and `LATEST` keeps the earlier row (charter-global O1 in `_difficulty.md` § rule_compute_equivalence). Observation, not a red light: the claimed values hold.

Factors vs `computations` (figure against figure):
- P4 expected 49.68 (auditor 49.68); baseline 125.0 (125.00); sensitivity 82.8 / 55.89 / 62.1 / 54.0 / 55.2 (same).
- P5 expected 133.65 (133.65); baseline 65.0 (65.00); sensitivity 148.5 / 148.5 / 121.5 / 57.92 (same).
- P6 expected 75.24 (75.24); baseline 200.0 (200.00); sensitivity 150.48 / 94.05 / 79.2 / 68.4 / 83.6 (same).
- P7 expected 29.67 (29.67); baseline 99.0 (99.00); sensitivity 37.34 / 41.85 / 34.86 / 31.08 / 69.02 / 26.17 (same).

Assertions of `design_rationale` checked against the world: spend 31,480 = sum of the four spend postings — true; points 18,420 = sum of the two points accruals — true; the 2026-03-12 posting is outside 6 months — true (MONTHS = 6); the outbound bag was charged 35.00 and the 56-lb bag's overweight entry 100.00 under the base baggage rule — true; "the ticket credits no Summit membership ... the corporate allowance of Business Connect Plus is 0" — true. The rationale describes the count convention and the count-place rate as factors without addressing their realism; see findings.

Closest candidate exclusion: see the frozen derivation (US-origin fee read off `origin: DEN`; per-direction place 2; recorded 72 lb; trip charges including segment 1).

Verdicts for task 1:
- Policy self-consistency: PASS on this world (charter-global F1, F3 move no value here).
- Problem tree holds: PASS.
- Factors bear weight: **SOURCE-FACTOR RED** (three defects, below).
- Unique solution: PASS (independent derivation = GT on every item).

**Task 1 verdict: SOURCE-FACTOR RED.**

## findings

1. **SOURCE-FACTOR RED — P5 `bag_count_convention` is an unreal ladder, and the tier this task takes is the unreal one.**
   - Symptom: Mara's second bag on the return is charged as a third bag (list 150) because a bag was checked on the outbound three days earlier.
   - Root cause: tier 1 counts first/second/third bag charges "on the whole ticket" on a short round trip; tier 2 counts only charged bags when the agreement has a corporate allowance (`_difficulty.md` § factor_ladders, F5).
   - Evidence: P5 rule sentence "on a partially flown round trip whose next departure falls within the short-trip days of the first flown flight, it is the number of first, second and third bag charges on the whole ticket plus one"; `parameter_schema.free_checked_bags_*` "Checked bags included per passenger per direction"; base measure `ticket_msr_bags_checked_in_direction` "on the same ticket and travel_direction"; seed rows `850f233c-...` (outbound CR1039921) and `dbd8394c-...` (return CR1047735).
   - Demonstrated consequence: the taken tier prices the bag at 150 × 0.891 = 133.65, where the per-direction count every carrier (and this charter's own allowance unit) uses gives place 2, list 65 -> 57.92; tier 2, on a Corporate Select ticket, makes every bag after a free first bag free again (place 1 <= allowance 1), which no carrier publishes and which contradicts base "allowances never add together". Struck, P5 keeps 3 factors (< 4) and 0 method.
   - Affected: `ticket.extended.yaml` P5 `rule`, `compute.seq_position`, `factors[bag_count_convention]`; `tasks/1.json` `computations[1]` (step 10, `charge_amount`, and `bag_sequence_position`).
2. **SOURCE-FACTOR RED — P6 `weight_count_place_rate` is an unreal ladder.**
   - Symptom: the overweight charge on CR1047735 is discounted 10% because its sequence charge is a first bag.
   - Root cause: the ladder's condition (the bag's place in the count) is priced by the separate sequence charge and is not something a carrier weighs when charging for a bag's excess weight or size (F5).
   - Evidence: P6 rule "The count-place rate follows the bag's own bag charge: a first bag gives the first-place rate, a second bag gives the second-place rate, and a third or later bag gives a rate of one"; `compute.w_place_rate`; seed `dbd8394c-...` `service_type: first_bag`.
   - Demonstrated consequence: the scored 75.24 carries a 0.9 factor that no carrier's overweight tariff contains; at the factor's baseline the charge is 83.60. After striking it P6 keeps 4 factors (1 method) — the count bound holds, the ladder itself is the defect.
   - Affected: `ticket.extended.yaml` P6 `factors[weight_count_place_rate]`; `tasks/1.json` `computations[2]` (step 12).
3. **SOURCE-FACTOR RED — P4 declares no genuine `method` factor.**
   - Symptom/root cause: `change_notice_days_convention` selects k = 2, 1.5 or 1 in floor(k × days) — a number in one formula, i.e. a parameter (F4).
   - Evidence: P4 `compute.chg_notice_days`; ladder methods "twice the whole days ...", "one and a half times those days, rounded down ...", "those days as counted"; `computations[0].factor_trace` labels it a method.
   - Demonstrated consequence: counting honest labels, P4 has 5 parameter factors and 0 method factors on this world (the factor bears weight: baseline 9 days -> 55.89 vs 49.68 — the defect is the label).
   - Affected: `ticket.extended.yaml` P4 `factors[change_notice_days_convention]`; `tasks/1.json` `computations[0]` (step 8).
4. Charter-global SOURCE-POLICY REDs F1 (P7 prerequisite sentences vs zero-fee/scope of P4, P5, P6) and F3 (O1, O2) — cited from `_difficulty.md` § findings; demonstrated above to move nothing on this world.
5. Observation — `prerequisite_closure.order_uniqueness` gives a reason ("none reads what another writes") that is not literally true for P5's channel read; the claimed invariance holds on this world by a date-tie in `LATEST`.
6. Observation — ticket `payment_form: corporate_invoice` under Business Connect Plus (`invoice_billing_permitted: false`); no ladder or write reads it.
7. Observation — P7 tier 1 of the trip-charges method, "the change, seat, bag and upgrade charges of the first unflown segment and of the whole itinerary", admits the reading "all charges" (428.57 -> 26.17); the contrast with tier 3's "every change, seat, bag and upgrade charge on the ticket" and P4's "itinerary-level change fee entry" steer a careful reader to 393.57, so no second defensible answer is established.
8. Observation — doubtful-realism ladders on this task that were not red-lit: P6 `weight_repeat_rate`, P6 `weight_points_rate`, fare-band rates on P4/P5/P6/P7, P7 corporate rate read from the long-haul discount on a short-haul ticket.

Relation to previous revisions: first audit of this difficulty.

---

## revision_2

### source_derivation_frozen (revision 2)

- Hashes: `ticket.extended.yaml` `0d4f8d91c702a89830d19fd70fdc309d95effcea81dd0cb0adb66a8938053b21` (changed); `task_tools.py` `9255fa2b…0783` (unchanged); masked view r2 `task_1.masked.json` `74927bc0b30b4551e048c5bee0ea4b94f913ef5a01d88f50294f98dde3d4df4f`.
- Written 2026-09-24 ~18:58Z, before the round-2 task JSON was opened (task 0's revision-2 derivation was frozen first; no round-2 GT of either task had been read).
- contamination_disclosure: not blind with respect to revision 1's GT — the auditor read the round-1 `tasks/1.json` at the revision-1 reveal (its values are quoted in revision 1 of this file). The round-2 values below that differ from round 1 come from the auditor's own recomputation on the round-2 charter; the round-2 task JSON and the worklogs were not read before this freeze.
- World delta vs revision 1 (auditor diff of r1/r2 views): `ticket_holdings.050efc00-….payment_form` and `ticket_transactions.1f5c4503-….payment_form` changed `corporate_invoice` -> `credit_card`; nothing else. No computation reads `payment_form`.

### policy_self_consistency (revision 2, this task)

Cites `_difficulty.md` § revision_2. Revision-1 charter REDs bearing on this task (F1 P7 edges, F3 O1/O2, F4 P4, F5 P5/P6) are closed at the charter level. Latent observations: R2-O1 (P1 -> P7) — the ticket has no same-day exchange; R2-O2 (P5 -> P6 object) — CR1047736 (56 lb) is lighter than CR1047735 (72 lb), so P6's object is CR1047735 in every order (auditor six-order replay: one terminal state); R2-O3 — only one bag lacks a sequence charge. Handling time: P4, P5, P6 evaluate identically in all six orders; P7 after all three. No real-world waits. PASS.

### problem_chain (revision 2)

Root P7 (owner=user). Rewritten sentences on the world:
1. "... fixed only after the latest standard exchange recorded on the ticket carries its change fee entry, whenever that exchange owes a change fee." Latest (only) standard exchange `e8b3cd9b-...`; P4 owes a positive fee (journey originates outside the US; agreement does not waive); no change-fee row. False; P4's write.
2. "... on a segment is not fixed until every bag of that segment carrying a weight or size entry also carries its first, second or third bag charge." Segment 2: CR1047736 has overweight row `6de602dd-...` and no sequence charge. False; P5's write.
3. "Before ... fixed, the heaviest bag charged by count on that segment must carry its weight or size entry whenever it owes a weight or size charge." Heaviest bag with a sequence charge on segment 2 is CR1047735 (72 lb, `dbd8394c-...`), counted 69 lb > 50 -> owes a positive charge; no weight row for its tag. False; P6's write.
Tree {P7; P4, P5, P6}, all value_input via `pe_trip_charges`, n = 3 (>= 2 value_input), acyclic, isomorphic to the declared `prerequisite`. Load-bearing: all resolved 36.89; skip P4 -> 42.72; skip P5 -> 43.00; skip P6 -> 43.58; opening 55.52. Parallel edges: six orders, one terminal state. Tools judge nothing. Persona raises only the root; bags and the change only on request; consent is passive. PASS.

### task_independent_derivation (revision 2)

Identity and authorisation as revision 1 (company verified with phone 7165551934 + ZIP 14203; Denise is the agreement's travel manager; P7 names the travel manager as buyer on a company-held ticket; she pays on the company card — now consistent with `payment_form: credit_card`).
- P4 (opening world): base fee 125 (journey originates outside the US, short-haul); agreement relief 0.6 (active Connect Plus, no waiver, spend 31,480 >= 25,000); notice 9 days (2026-09-15 -> 2026-09-24) -> >= 7, < 14 -> 0.9; banding fare (method): ticket names an active agreement -> fare collected 658.36 less taxes and fees 118.36 = 540.00 -> >= 400, < 600 -> 0.96; brand 0.9. Fee = RND(125 × 0.6 × 0.9 × 0.96 × 0.9) = **58.32**. `post_change_fee_ac050962(050efc00-..., e8b3cd9b-..., 8ce9157a-..., 58.32)`.
- P5 (opening world): CR1047736, return direction; allowance max(0 brand, 0 corporate, 0 elite — no membership) = 0; place = return-direction first/second/third charges (CR1047735) + 1 = 2 -> short-haul second bag 65; posting rate 0.9 (3 spend postings in 6 months); banding fare (method): flown coupon -> 658.36 − 329.18 = 329.18 -> >= 300, < 500 -> 0.95; segment check-in channel airport (bag charges of segment 2 paid at the airport) -> 1.1. Charge = RND(65 × 0.9 × 0.95 × 1.1) = **61.13**, position 2. `post_bag_sequence_charge_b2992c63(050efc00-..., CR1047736, 8ce9157a-..., 2, 61.13)`.
- P6 (opening world): CR1047735, 72 lb airport -> counted 69 -> first band 100 (size 59 <= 62); points 0.8 (18,420); fare band 0.95 (658.36); repeat 1.1 (one weight entry on the ticket); excess 69 − 50 = 19 lb -> > 5, <= 20 -> 0.8. Charge = RND(100 × 0.8 × 0.95 × 1.1 × 0.8) = **66.88**, component overweight_bag. `post_bag_weight_charge_02a99017(050efc00-..., CR1047735, 8ce9157a-..., overweight_bag, 66.88)`.
- P7 (after the three): price 99; corporate rate: domestic/short-haul discount 3% -> >= 1, < 10 -> 0.9; travel today 0.85; fare band 0.93; lead 19 days 0.98; trip charges (flown coupon): segment-2 change/bag/upgrade rows 35.00 + 100.00 + 61.13 + 66.88 plus segment-0 rows 58.32 = 321.33; credit share 0.1 (active agreement listing `corporate_booking_tool`) -> credit 32.133. Charge = RND(99 × 0.9 × 0.85 × 0.93 × 0.98 − 32.133) = **36.89**; `purchase_premium_economy_upgrade_2477ee45(050efc00-..., 2, 36.89)` (user). Opening contrast 55.52.
Order: verify -> {P4, P5, P6} any order -> P7. Terminal state: change fee 58.32 (segment 0), second_bag 61.13 for CR1047736, overweight 66.88 for CR1047735, PE upgrade 36.89 on segment 2, verified identity row.
Closest alternatives: banding fare 658.36 for the change fee (-> 55.89) — excluded by the corporate convention; place 3 (whole-ticket count, revision-1 rule) — no longer in the charter, excluded by "in the bag's direction"; unflown fare for the change fee (329.18 -> 60.75) — excluded because the corporate tier comes first; weight at 72 lb (second band) — excluded by the airport tolerance.

### factor_weight (revision 2)

- P4 (58.32; all-baseline 125.00): agreement 97.20; notice 64.80; **banding-fare method** 55.89; fare band 60.75; brand 64.80. Near-miss: flown coupon 329.18 (a reader taking tier 2 gets band 1); `base_fare`/taxes vs fare collected. 5 factors (4p/1m), multi-source (agreement relief), cross-difficulty (business). PASS.
- P5 (61.13; all-baseline 65.00): posting 67.93; fare band 64.35; channel 55.57; **banding-fare method** 57.92. Near-miss: 2026-03-12 spend posting (outside 6 months), points accruals (not postings), outbound bag CR1039921 (other direction). 4 factors (3p/1m), multi-source (posting), cross-difficulty (business). PASS.
- P6 (66.88; all-baseline 200.00): counted method 167.20; points 83.60; fare band 70.40; repeat 60.80; **excess rate** 83.60. Near-miss: CR1039921 (flown segment), CR1047736 (already carries its entry). 5 factors (4p/1m). PASS.
- P7 (36.89; all-baseline 99.00): corporate 44.56; travel day 49.07; fare band 42.09; lead 38.30; credit share 69.02; trip-charges method 33.39. Near-miss: segment-1 bag 35.00. 6 factors (5p/1m). PASS.
No stamp names a tier; business cross-difficulty rows seeded. Revision-1 findings 1 (unreal `bag_count_convention`), 2 (unreal `weight_count_place_rate`), 3 (P4 without an honest method) — closed on this world.

Result before reveal: all four relationships PASS.

### source_gt_comparison (revision 2)

- Reveal of the round-2 `tasks/1.json` after both round-2 derivations were on disk (hashes at 2026-09-24T18:54:48Z: `_difficulty.md` `fe745b11…`, `task_0.md` `d66a405c…`, `task_1.md` `420cd510…`). The "~18:58Z" in the frozen header was an estimate; the hash bounds the freeze. Frozen text unchanged.
- Item by item: identity (step 1), reads, P4 args and 58.32 (step 8), P5 CR1047736 position 2 and 61.13 (step 10), P6 CR1047735 overweight_bag 66.88 (step 12), P7 segment 2 and 36.89 by the user (step 14), order and terminal state — **all same**. `charter_scope` = {P4, P5, P6, P7} = auditor's scope.
- `computations` vs `factor_weight`: P4 58.32 / 125.0 / 97.2, 64.8, 55.89, 60.75, 64.8; P5 61.13 / 65.0 / 67.93, 64.35, 55.57, 57.92; P6 66.88 / 200.0 / 167.2, 83.6, 70.4, 60.8, 83.6; P7 36.89 / 99.0 / 44.56, 49.07, 42.09, 38.3, 69.02, 33.39 — **all equal**.
- `prerequisite_closure` vs auditor tree: root, three edges (value_input, `pe_trip_charges`, state, round-2 sentences and conditions, resolved_by) — equal; flips 58.32 / second_bag 61.13 / overweight 66.88 — equal; `edge_load_bearing` trip charges 263.01 / 260.20 / 254.45 and upgrade 42.72 / 43.0 / 43.58 — auditor 321.33 − 58.32 = 263.01, − 61.13 = 260.20, − 66.88 = 254.45 and 42.72 / 43.00 / 43.58 — equal. `order_uniqueness` now gives a true reason (P5 takes the segment channel from airport/online rows; P6's row is call-center; P6's object is the 72-lb bag, not the 56-lb bag P5 charges) — revision-1 observation 5 closed; the auditor's six-order replay agrees (one terminal state).
- `design_rationale` assertions re-checked: 658.36 − 118.36 = 540.00 (band 0.96; baseline 0.92 -> 55.89); unflown 329.18 for the bag band; 69 lb counted, 19 lb excess -> 0.8; 3 spend postings; trip charges 321.33 — all true.

Verdicts (revision 2): policy self-consistency PASS; problem tree PASS; factors PASS; unique solution PASS.

**Task 1 verdict (revision 2): PASS.**

### findings (revision 2)

Closure of revision-1 items for this task:
- Finding 1 (SOURCE-FACTOR RED, unreal `bag_count_convention`) — **closed**: removed; the place in the count is the base per-direction count (CR1047736 is the second return bag, second-bag fee), and the method is `bag_banding_fare_convention`, which is real and honest and bears weight (57.92 vs 61.13).
- Finding 2 (SOURCE-FACTOR RED, unreal `weight_count_place_rate`) — **closed**: removed; replaced by `weight_excess_rate`, a graduated excess-weight parameter (real, honest, bears weight: 83.60 vs 66.88).
- Finding 3 (SOURCE-FACTOR RED, P4 without an honest method) — **closed**: `change_notice_days_convention` removed; `change_banding_fare_convention` (taxes-out fare for an active-agreement ticket / unflown fare / fare collected) is a genuine method and bears weight (55.89 vs 58.32).
- Finding 4 (charter F1, F3 citations) — **closed** at the charter level.
- Observation 5 (`order_uniqueness` reason) — **closed** (see comparison).
- Observation 6 (`payment_form: corporate_invoice` under a tier without invoice billing) — **closed**: both rows now `credit_card`, consistent with "you will pay for it on the company card".
- Observation 7 (P7 tier 1 "of the whole itinerary" ambiguity) — **closed**: the rule now says "the charges recorded against the first unflown segment plus the itinerary-level charges recorded against no segment".
- Observation 8 (doubtful-realism ladders) — **partly closed**: the long-haul-discount reading is replaced by the itinerary-class discount (Connect Plus domestic/short-haul 3% -> 0.9 on this world); `weight_repeat_rate`, `weight_points_rate` and the fare-band rates remain as observations.
New: none on this task. Latent charter observations R2-O1..O3 do not instantiate on this world (verified in `policy_self_consistency`). No regression.
