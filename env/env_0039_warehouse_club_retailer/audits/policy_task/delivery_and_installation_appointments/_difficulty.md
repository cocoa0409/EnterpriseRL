# Policy-task audit — delivery_and_installation_appointments / charter-global

## charter_global_frozen

- Scenario: env/env_0039_warehouse_club_retailer; difficulty: delivery_and_installation_appointments; product: delivery; M=2.
- Freeze hashes (sha256, re-verified at audit start, equal to the brief):
  - tasks/delivery_and_installation_appointments/delivery.extended.yaml `d3d19e64c4bdb7c68b41613a6a805b73a8c3e5a64af3ac439c81b9ef1c8ec9c4`
  - tasks/delivery_and_installation_appointments/task_tools.py `784d7903257750cc67ac2906df5c94c4f7b79c3c6e858373f9c1e9540b1e1c90`
  - audits/views/policy_task/delivery_and_installation_appointments/0.view.json `6d13322124b655abdf7b6a45e11af3f6bf233d0d99def6f17f0f3965a5c23643`
  - audits/views/policy_task/delivery_and_installation_appointments/1.view.json `7ce4aa677994596466783dbdb3b347bdc7d22c65b8ba19e40ea8586d2109bfea`
- Freeze time: 2026-10-05T21:31Z (written before any task's GT was revealed). Auditor: independent policy-task auditor (Claude agent, erl-task-policy-audit), not the instantiating agent.
- Fields read: blueprint/blueprint.yaml (difficulty entry), blueprint/products/delivery.yaml, blueprint/db_schema.json (field meanings), blueprint/share_tools.py (finder signatures), the extended charter, task_tools.py, the two masked views (frozen_time, user_scenario, initial_state only), and the compute-DSL semantics in skills/erl-task-instantiate/scripts/check_compute.py (MONTHS/DAYS/_within/RND).
- Fields masked / unread at freeze: tasks/*.json (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), worklog.md (never opened), any earlier audit (none exist).
- Entry conditions (Step 0): the brief supplies the gate snapshot (EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; TRACEABILITY NOT OK, deferred as KB-dependent), the masked views and their hashes. Input complete. Gates were not re-run by the auditor.

### policy_conflict_scan

Base section: `head -958` of the extended charter is byte-identical to blueprint/products/delivery.yaml (diff shows only the trailing blank line). Base copy is verbatim.

Extended policies (5), each with its own `(target_tool, computes)`:

| policy | trigger | target_tool (owner) | prerequisite edges |
| --- | --- | --- | --- |
| delivery_ext_distance_settlement | state_due | post_extended_distance_charge_120a0e6d (agent) | [] |
| delivery_ext_reschedule_settlement | state_due | post_reschedule_fee_c618067c (agent) | -> distance (value_input, route_miles) |
| delivery_ext_wall_mount_addition | on_request | authorize_wall_mounting_3e376943 (user) | -> distance (value_input, n_distance); -> reschedule (state_gate) |
| delivery_ext_install_kit_settlement | state_due | post_installation_kit_charge_19cc3b17 (agent) | [] |
| delivery_ext_replacement_haul_away | on_request | authorize_haul_away_734a64e4 (user) | -> kit (value_input, old_appliances) |

Overlap scan on subjects (all five write `delivery_service_charged` rows, each of a distinct `charge_type`: extended_distance / reschedule_fee / wall_mount_labor / installation_parts_kit / haul_away), so no two extended policies post the same charge component. Cross-reads between extended policies:
- distance reads haul_away units (trip_mult); haul_away never reads distance. On an appliance appointment both beyond the radius and asking for haul-away, the distance amount would depend on whether the haul-away entry stands first, and no rule orders them. Neither task's world reaches this (task 0's haul-away rows are seeded base charges; task 1's appointment is within the radius, distance_miles 37 <= 50). Observation O-6.
- wall-mount reads haul_away / stair_carry / extended_distance / installation_parts_kit counts; the extended_distance read is ordered by a declared edge; the others are seeded base charges in the relevant world.
- reschedule reads extended_distance units (declared edge).
- haul_away reads installation_parts_kit units (declared edge).

Eligibility / time anchors / terminal states: no extended policy carries an `eligibility` list; the base eligibilities (booking lead times, service area, one open appointment, reschedule only while scheduled, credit status) are untouched by every extended rule and are inherited. Time anchors used: booked_date -> scheduled_date (reschedule hold span, haul-away planning span), today -> scheduled_date (wall-mount late multiplier, haul-away late multiplier), twelve whole months before today (distance spend, kit volume), whole months since membership opened (reschedule courtesy, kit tenure, wall-mount tier). All are record-visible and evaluated at frozen_time; none waits on a future event.

Scope: from the worlds alone (derived in the task files) task 0 is the tree {wall_mount <- distance, wall_mount <- reschedule, reschedule <- distance} and task 1 is {haul_away <- kit}. The two scopes are pairwise disjoint and jointly cover all five extended policies.

Charter-level conflicts found: F-1 (reschedule notice clause) and F-2 (zero-amount extended-distance entry) under `findings`.

### rule_compute_equivalence

Checked binding by binding for all five policies; every binding's `compute_basis` quotation is a verbatim substring of that policy's `rule`, and every rule sentence that fixes a quantity is implemented.

- distance: miles_beyond `MX(0, distance - radius)` <- "The entry carries as its units the appointment's road miles beyond the included radius, counted before any free miles"; free_miles 15/10/0 on the presented membership; miles_charged floored at 0 <- "never fall below zero"; mile_rate on the delivered purchase's sold-less-returned line amounts 3000/2000 thresholds; spend_mult on the member's sold-less-returned within twelve whole months (DSL `_within`: `0 <= MONTHS(event_date, NOW) < 12`, MONTHS counts whole months with day-of-month borrow, matching "fewer than twelve whole months"); trip_mult on the SUM of haul_away units (rule: "remove three or more old items in all"); result rounded once at the end. The "no extended-distance charge when not beyond the radius" sentence is implemented by miles_beyond = 0 -> result 0 (see F-2 for the zero-amount case).
- reschedule: moves_owed `MX(0, reschedule_count - free_reschedules - COUNT(reschedule_fee rows))` <- "reschedule count less the service level's free reschedules less the reschedule fee entries already standing ..., never fewer than none"; hold_days DAYS(booked_date, scheduled_date); route_miles SUM of extended_distance units; card_mult both/one/neither on order tender and membership auto_renew_tender; courtesy_pct Plus x months>=120; result `(fee + hold + route) * moves * card * (1 - pct/100)` <- "The reschedule fee with both surcharges, times the moves that owe one, is then multiplied ... A change-fee courtesy discount is then taken off the multiplied amount".
- wall mount: televisions = TV units sold less returned on the delivered purchase; mount_units 1+0.5(n-1) / 1.75 / n; spend and tender allowances subtract from the labor fee per TV; late_mult on DAYS(NOW, scheduled_date) <=2 / <=6; tier_pct + bundle_pct added then applied once ("the two discounts do not act successively"); bundle counts distinct component types with at least one entry.
- kit: appliances = major_appliance units sold less returned on the delivered purchase; kits_owed = MX(0, appliances - kit units standing); kit_price Business x volume(12 whole months) >= 4; stock_reduction on kit units standing (2+/1/0); tenure_reduction 180/96 months; pair_scale on appliances; tender pct; rounded once.
- haul-away: old_appliances = SUM of kit units; included_items Business 0 / Club Plus 2 / other P; removed_beyond floored at 0; removal_fee on delivered purchase sold-less-returned 2500/1500; planning_reduction 14/7 days booked->scheduled; late_removal_mult <=1 / <=5 days; renewal_pct on auto_renew and auto_renew_tender.

Every factor ladder tier appears as a rule sentence and as a branch of its `decides` binding, and vice versa. No compute-only tier; no rule-only tier.

One divergence between the rule text and the DSL implementation (not between rule and compute expression): every rule says "rounded to the cent once, at the end, half up", while `RND` is Python `round(float(x), 2)` (check_compute.py line 388), i.e. round-half-even on binary floats. At an exact half-cent the two differ (e.g. 13.125 -> 13.12 under RND, 13.13 half up; 261.625 -> 261.62 vs 261.63). The rule is the agent-facing text and governs. Observation O-1; per-task files check whether any gold value or proof figure falls on such a tie.

### action_binding_and_uuids

- `(target_tool, computes)` pairs are five distinct tools x `amount`; each claimed by exactly one policy.
- Tool bodies (task_tools.py) only `ctx.create` one `delivery_charges` row with a fixed `charge_type`, `event_date = ctx.now()[:10]`, `credit_reason="not_applicable"`; none reads the DB, checks eligibility, checks any prerequisite, refuses or hints. post_reschedule_fee always writes `units=1`.
- Docstrings: an ordering-word sweep (`before|after|first|then|until|prior|once`, whole word) over task_tools.py returns nothing; no docstring names another tool or states a position in a sequence.
- uuid8 tails: 120a0e6d, c618067c, 3e376943, 19cc3b17, 734a64e4 — five distinct values with no shared prefix, no sequence, no adjacent-value pattern. PASS.
- Owners: the two on_request policies (wall mount, haul-away) are `owner="user"`, matching their rules ("booked on the member's own authorization"; "authorizes the removal personally"); the three state_due settlements are `owner="agent"`.

### prerequisite_graph

- `prerequisite` filled on all five ([] on distance and kit).
- Edges: reschedule -> distance; wall_mount -> distance; wall_mount -> reschedule; haul_away -> kit. Every `problem` is an extended policy id of this file, none a base policy, none self. Acyclic (distance and kit are sources; topological orders distance < reschedule < wall_mount and kit < haul_away).
- Each `policy_source` is a verbatim sentence of the blocked policy's own rule (reschedule rule last sentence; wall-mount rule last two sentences; haul-away rule last sentence).
- All four edges `form: state`; no `fallback_reason` key anywhere in the file (grep), as required for state form.
- `resolved_by` equals the depended-on policy's `target_tool` on all four.
- `kind`/`gate`: the three value_input gates (route_miles, n_distance, old_appliances) are binding names in the blocked policy's compute. The state_gate edge wall_mount -> reschedule names `gate: delivery_charges.charge_type`, a field rather than an eligibility id (extended policies carry no eligibility list); the gate itself is the rule sentence. Observation O-3, no consequence.
- `condition` vs sentence: reschedule -> distance condition adds "whose units are the road miles beyond the included radius", which the sentence does not say; the units are fixed by the distance policy's own rule, so the hop resolves identically. Observation O-4. haul_away -> kit condition says the kit units "add up to" the appliances; the sentence says "cover"; kits_owed is floored so over-coverage cannot arise. No strengthening that changes a hop.
- No authoring-viewpoint phrasing ("in this task", "at the opening", "current world") in any prerequisite (grep: none).

### prerequisite_sentences

For each edge, the four-point test and the single-reading derivation:

1. reschedule -> distance: "The reschedule fee owed on an appointment whose road miles exceed the included radius is not fixed until the appointment's extended-distance entry stands on it." Connective "not ... until"; waited-on state "the appointment's extended-distance entry stands on it" = a delivery_charges row of charge_type extended_distance (finder: find_delivery_charges); names no tool, policy id, snake_case token or row id; scope "whose road miles exceed the included radius" equals the condition. Unique writer of an extended_distance row in this difficulty: post_extended_distance_charge_120a0e6d (distance policy). Derivation: sentence -> records show no extended_distance row -> the distance policy's rule ("owes an extended-distance charge, posted as one extended-distance entry") is the only rule that produces one -> resolve distance first. One reading. PASS.
2. wall_mount -> distance: "Where the appointment's road miles exceed the included radius, the wall-mounting charge is fixed only after the appointment carries its extended-distance entry." Same state, same unique writer. PASS.
3. wall_mount -> reschedule: "On an appointment moved more times than its free reschedules, wall mounting is booked only after the appointment carries a reschedule fee entry for every move beyond them." Connective "only after"; state = reschedule_fee rows on the appointment; unique writer post_reschedule_fee_c618067c (reschedule settlement). Scope "moved more times than its free reschedules" equals the condition (count >= reschedule_count - free_reschedules). PASS. (Phrasing "for every move beyond them" vs the settlement's "one reschedule fee entry" for all owed moves: see O-5.)
4. haul_away -> kit: "The haul-away charge for the old appliances an installation replaces is fixed only once the appointment's installation parts kit entries cover every appliance it installs." Connective "only once"; state = installation_parts_kit units vs appliances installed; unique writer post_installation_kit_charge_19cc3b17. PASS.

No rule restates another problem's sentence; the depended-on rules (distance, reschedule, kit) carry no ordering sentence about their dependants. No rule states any other cross-problem order (the distance rule's read of haul-away entries is a value read with no ordering connective; see O-6). No base sentence grounds an edge.

### override_declarations

Swept sentence by sentence against each `base_policy_refs` entry:

- distance vs delivery_booking_and_fees: "road miles beyond included_radius_miles at extended_distance_fee_per_mile_usd each" — declared (overwrite 1). "At booking the following are charged, each as its own entry dated the booking date with the appointment date as service_date" — declared (overwrite 2). "A component whose amount comes to zero is not entered." — NOT declared, and the extended rule handles that quantity differently when free miles absorb all miles beyond the radius -> F-2. Plus-discount, haul-away, stairs, kit, wall-mount sentences govern other components: followed/not touched. "Delivery and installation fees never earn Annual Reward": followed. vs delivery_reschedule / delivery_failed_attempts: no sentence governs the distance amount; followed.
- reschedule vs delivery_reschedule: "otherwise reschedule_fee_usd is charged as a reschedule_fee entry whose service_date is the new date" — declared. The head of the same sentence, "A reschedule is free only when at least reschedule_notice_days calendar days separate the request date from the booked delivery date and the appointment has made fewer than free_reschedules free reschedules (...)", stays in force and conflicts with the extended exhaustive definition of the moves that owe a fee -> F-1. "Changing only the window on the same date counts as a reschedule": followed (reschedule_count). Status/lead-time/max_reschedules sentences: followed. vs delivery_booking_and_fees: "At booking ..." — the settlement posts later, dated the posting date, undeclared; event_date is stamped by the tool and service_date is the same date under both -> no scored difference, O-2.
- wall mount vs delivery_booking_and_fees: "and wall_mount_labor_usd per television mounted" — declared. "At booking ..." — undeclared; mounting added after booking is dated the posting date; no scored difference, O-2. vs delivery_crew_scope: screen-size and wall-construction limits restated as "still apply at the door"; followed.
- kit vs delivery_booking_and_fees: "one installation_parts_kit per appliance installed at installation_parts_kit_fee_usd" — declared. "At booking ..." — undeclared; O-2.
- haul-away vs delivery_booking_and_fees: "haul-away of old items beyond haul_away_included_items at haul_away_fee_per_item_usd each, only where haul_away_available" — declared (the replacement drops "only where haul_away_available"; the rule is confined to installation appointments, where the Appliance level has haul_away_available true, so no service level is newly opened in practice). "At booking ..." — undeclared; O-2. vs delivery_crew_scope: "the appliance being replaced is disconnected only where old_appliance_disconnect_included" — followed.

Disguised forms: no anonymous intermediate factor found beyond the declared ones; no 0/1 multiplier zeroing a base-fixed amount (route_surcharge 0 when no entry is a declared tier); no dropped base branch except the one in F-1 (the notice branch of "free only when").

### factor_ladders

| policy | factor | label | decides | tiers | multi-source tiers | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| distance | plus_free_miles | parameter | free_miles | 3 (15 / 10 / 0) | no (one membership row) | membership |
| distance | purchase_size_mile_rate | parameter | mile_rate | 3 ($1.00 / $1.25 / P per-mile) | no | order |
| distance | twelve_month_spend_scaling | method | spend_mult | 3 (x0.5 / x0.75 / x1) | no | order |
| distance | return_leg_trip_count | method | trip_mult | 3 (x2 / x1.5 / x1) | no | null |
| reschedule | hold_span_surcharge | parameter | hold_surcharge | 3 ($20 / $10 / 0) | no | null |
| reschedule | long_route_surcharge | parameter | route_surcharge | 3 ($20 / $8 / 0) | no | null |
| reschedule | northgate_visa_multiplier | method | card_mult | 3 (x0.5 / x0.75 / x1) | yes (order tender AND/OR membership renewal tender) | order |
| reschedule | plus_change_fee_courtesy | parameter | courtesy_pct | 3 (50 / 25 / 0) | no (tier and opened_date on one membership row) | membership |
| wall mount | multi_television_pricing | method | mount_units | 3 (1+0.5(n-1) / 1.75 / n) | no | order |
| wall mount | television_spend_allowance | parameter | spend_allowance | 3 ($25 / $10 / 0) | no | order |
| wall mount | mounting_tender_allowance | parameter | tender_allowance | 3 ($15 / $5 / 0) | no | order |
| wall mount | late_mounting_multiplier | method | late_mult | 3 (x1.5 / x1.25 / x1) | no | null |
| wall mount | mounting_member_tier_discount | parameter | tier_pct | 3 (20 / 10 / 0) | no | membership |
| wall mount | multi_service_discount | parameter | bundle_pct | 3 (15 / 10 / 0) | yes-ish (four charge types, one table) | null |
| kit | contractor_kit_price | parameter | kit_price | 3 ($27.99 / $33.99 / P kit fee) | yes (membership tier AND order_lines volume) | membership |
| kit | fittings_stock_reduction | parameter | stock_reduction | 3 ($5 / $2.50 / 0) | no | null |
| kit | kit_tenure_reduction | parameter | tenure_reduction | 3 ($4 / $2 / 0) | no | membership |
| kit | installed_appliance_scaling | method | pair_scale | 3 (x0.5 / x0.75 / x1) | no | order |
| kit | kit_tender_discount | parameter | kit_tender_pct | 3 (10 / 5 / 0) | no | order |
| haul-away | removal_included_items | parameter | included_items | 3 (0 / 2 / P included) | no | membership |
| haul-away | removal_fee_by_purchase | parameter | removal_fee | 3 ($15 / $20 / P per-item) | no | order |
| haul-away | removal_planning_reduction | parameter | planning_reduction | 3 ($3 / $1 / 0) | no | null |
| haul-away | late_removal_multiplier | method | late_removal_mult | 3 (x2 / x1.5 / x1) | no | null |
| haul-away | renewal_billing_discount | parameter | renewal_pct | 3 (20 / 10 / 0) | no (auto_renew and tender on one membership row) | membership |

Structure checks:
- Counts as declared: distance 4 (2 param, 2 method), reschedule 4 (3 param, 1 method), wall mount 6 (4 param, 2 method), kit 5 (4 param, 1 method), haul-away 5 (4 param, 1 method). All within 4-6, all with >= 2 parameter and >= 1 method as labelled.
- `decides` is an input binding, never `result`; binding sets are pairwise disjoint within each policy.
- Every ladder has three pairwise-disjoint tiers as stated (thresholds are closed/open consistently: ">= X", ">= Y but under X", "under Y"; "N or more / M to N-1 / fewer than M"; day-count tiers "<= 2 / 3-6 / >= 7" etc.).
- Every tier is stated in prose in the rule (condition and value/method) and implemented in compute (rule_compute_equivalence above).
- Baselines: each `baseline.rule` is two sentences, both verbatim in the rule, with `params` naming the variant keys it reads; each factor's fall-through equals its baseline binding (free_miles 0; mile_rate P; spend_mult 1; trip_mult 1; hold 0; route 0; card 1; courtesy 0; mount_units = televisions; allowances 0; late_mult 1; tier/bundle 0; kit_price P; reductions 0; pair_scale 1; tender pct 0; included_items P; removal_fee P; planning 0; late 1; renewal 0). Honest by construction; per-task files check the numbers.
- Distinct tier outcomes: one failure — purchase_size_mile_rate on two service levels -> F-3.
- Label honesty: seven of the eight `method` factors select only a scalar multiplier entering the same product -> F-4. multi_television_pricing changes the per-unit pricing schedule (first television full, each other at a share, vs every television at the full fee) and is accepted as an honest method.
- Realism: the conditions are ones a warehouse-club delivery business can plausibly weigh (membership tier and tenure, co-brand card, purchase size, booking lead, late-change surcharges, contractor pricing for business accounts). Two are weak but not demonstrably unreal: the return-leg multiplier's x1.5 for one or two hauled items, and the renewal-billing discount on a haul-away fee. Observation O-7.
- Multi-source factors (every non-fall-through tier a conjunction/disjunction over distinct records): northgate_visa_multiplier (order_holdings.tender with membership_holdings.auto_renew_tender) and contractor_kit_price (membership_holdings.variant_name with order_lines volume). Per task: task 0's tree contains the reschedule settlement (visa multiplier); task 1's tree contains the kit settlement (contractor price). Each task has at least one.
- Cross-difficulty factors (order / membership) exist in every policy; per-task seeding is checked in the task files.

### findings

F-1 — SOURCE-POLICY RED (charter-global). Bears on task 0 (reschedule settlement is in its tree); task 1 not affected.
- Symptom: the merged reschedule semantics give two answers to "does this move owe a fee".
- Root cause: the overwrite on delivery_ext_reschedule_settlement supersedes only the tail "otherwise reschedule_fee_usd is charged as a reschedule_fee entry whose service_date is the new date." The head of the same base sentence stays in force: "A reschedule is free only when at least reschedule_notice_days calendar days separate the request date from the booked delivery date and the appointment has made fewer than free_reschedules free reschedules (reschedule_count minus delivery_msr_paid_reschedules)". The extended rule defines the moves owing a fee exhaustively by count: "The moves that owe a fee are the appointment's reschedule count less the service level's free reschedules less the reschedule fee entries already standing on the appointment, never fewer than none".
- Evidence: delivery.extended.yaml, base policy delivery_reschedule rule (lines 655-658) vs delivery_ext_reschedule_settlement rule (lines 1167-1170) and compute `moves_owed`.
- Demonstrated consequence (same situation): a TV Delivery & Wall-Mount appointment (free_reschedules 1, reschedule_notice_days 2, reschedule_fee_usd 50) moved once with one day's notice and no reschedule fee entry. Base: notice 1 < 2, so the move is not free and $50.00 is owed. Extended: moves_owed = MX(0, 1 - 1 - 0) = 0, so nothing is owed. Two conclusions.
- Affected: delivery.extended.yaml delivery_ext_reschedule_settlement.overwrite / rule; inherited base delivery_reschedule rule.

F-2 — SOURCE-POLICY RED (charter-global). Bears on task 0's distance and its two dependants only in a world where free miles absorb all miles beyond the radius; not in task 0's world (see 0.md). Task 1 not affected.
- Symptom: an appointment beyond the radius whose free miles cover every mile beyond it is told both to post and not to post an extended-distance entry, and the downstream state-form gates hinge on that entry.
- Root cause: the base sentence "A component whose amount comes to zero is not entered." (delivery_booking_and_fees) is not named in the distance overwrite, while the extended rule says "An appointment whose road miles from the delivering club exceed the service level's included radius owes an extended-distance charge, posted as one extended-distance entry ... The entry carries as its units the appointment's road miles beyond the included radius, counted before any free miles", and free miles can take the charge to zero ("the miles charged never fall below zero").
- Demonstrated consequence: TV appointment, distance_miles 50 (10 beyond the 40-mile radius), purchase presented Business Plus (15 free miles): miles_charged = 0, amount 0.00. Base: the zero component is not entered, so no extended-distance entry ever stands, and the reschedule ("not fixed until the appointment's extended-distance entry stands on it") and wall-mount ("fixed only after the appointment carries its extended-distance entry") gates can never be met. Extended: one entry with units 10 and amount 0.00 is posted, but the tool contract says amount is "always positive". Reschedule route_surcharge is $0 under the first reading and $8 under the second; the wall-mount bundle count differs by one.
- Affected: delivery_ext_distance_settlement.overwrite / rule; post_extended_distance_charge_120a0e6d docstring (amount "always positive").

F-3 — SOURCE-FACTOR RED (charter-global; consequence on no task of this difficulty).
- Symptom: two tiers of purchase_size_mile_rate select the same value on two service levels.
- Evidence: tier 2 "K('rate_mid_purchase') = $1.25 a mile"; fall-through "P('extended_distance_fee_per_mile_usd')", which is 1.25 for Northgate Curbside Delivery (line 102) and Northgate Threshold Delivery (line 154).
- Demonstrated consequence: on a Curbside or Threshold appointment, a purchase of $2,000.00-$2,999.99 and a purchase under $2,000.00 both get $1.25/mile; the tier is one tier written as two, and the factor cannot bear weight for a mid-size purchase at those levels. Task 0 uses the TV level (1.50), and task 1's appointment owes no distance charge, so neither task's score is affected.
- Affected: delivery_ext_distance_settlement.factors[purchase_size_mile_rate].ladder; params rate_mid_purchase vs variants Curbside/Threshold extended_distance_fee_per_mile_usd.

F-4 — SOURCE-FACTOR RED (charter-global finding; the per-task count shortfall is demonstrated in 0.md and 1.md).
- Symptom: factors labelled `method` whose tiers substitute only a different scalar into one unchanged product formula.
- Evidence (compute `result` lines): distance `RND(miles_charged * mile_rate * spend_mult * trip_mult, 2)` with spend_mult in {0.5, 0.75, 1} and trip_mult in {2, 1.5, 1}. reschedule `... * card_mult * (1 - courtesy_pct / 100)` with card_mult in {0.5, 0.75, 1}. wall mount `... * late_mult * ...` with late_mult in {1.5, 1.25, 1}. kit `... * pair_scale * (1 - kit_tender_pct / 100)` with pair_scale in {0.5, 0.75, 1}. haul-away `... * late_removal_mult * (1 - renewal_pct / 100)` with late_removal_mult in {2, 1.5, 1}. In the same formulas the `parameter` factors kit_tender_pct / renewal_pct / courtesy_pct also act as multiplicative scalars ((1 - pct/100)) — a `method` x0.75 and a `parameter` 25-percent-off are the same operation under two labels. This is the skill's "mislabelled effect": "a factor labelled method whose tiers only substitute a different number into the same formula (a rate, a fee, a threshold)".
- Counter-reading considered: "halve / three quarters / whole" could be read as a change of procedure, and "counted out and back" (trip x2) as a different trip-leg counting rule. Rejected: every tier of each ladder, the fall-through included, is the same product with a different constant, and the x1.5 tier of the trip ladder is not a leg count at all.
- Consequence, counting only honest labels: distance 0 method (both scalars), reschedule 0, kit 0, haul-away 0, wall mount 1 (multi_television_pricing). Four of five computations fall below ">= 1 method". Task 0: distance and reschedule fail; task 1: kit and haul-away fail.
- Affected: factors[].effect of twelve_month_spend_scaling, return_leg_trip_count, northgate_visa_multiplier, late_mounting_multiplier, installed_appliance_scaling, late_removal_multiplier; the method count of each of those policies.

Observations (not grounds for rework):
- O-1: RND is Python round-half-even on floats, while the rules say half up. They differ only at exact half-cent results; per-task files check gold and proof figures.
- O-2: "At booking the following are charged, each as its own entry dated the booking date ..." is declared superseded only on the distance policy; reschedule / wall mount / kit / haul-away also post after booking, dated the posting date. event_date is stamped by the tool, not passed as an argument, and service_date is the currently booked date under both readings, so no scored difference.
- O-3: the state_gate edge wall_mount -> reschedule names `gate: delivery_charges.charge_type` (a field) rather than an eligibility gate; the gate lives in the rule sentence. No consequence.
- O-4: the reschedule -> distance `condition` adds the units clause that its sentence does not carry; it is fixed by the distance rule itself, so the hop resolves identically.
- O-5: the reschedule settlement posts "one reschedule fee entry" for all owed moves, and its moves_owed subtracts the count of entries. The wall-mount gate asks for "a reschedule fee entry for every move beyond them". The two diverge only when two or more moves are owed at once, but max_reschedules - free_reschedules = 1 on every service level (3-2 or 2-1), so that never happens within the charter's parameters.
- O-6: distance trip_mult reads haul-away entries with no stated order against a haul-away write on the same appointment (an appliance appointment beyond 50 miles asking for haul-away). This is not reached by either task's world.
- O-7: realism of the return-leg x1.5 tier and of the renewal-billing discount on haul-away is weak but not demonstrably unreal.

## closing_checklist

Written after both reveals (2026-10-05T21:35Z). Nothing above this heading was changed after the reveal.

Status: NOT CLOSED. The difficulty does not pass the source-layer audit, because both tasks carry SOURCE-FACTOR RED and the charter carries SOURCE-POLICY RED (F-1, F-2) and SOURCE-FACTOR RED (F-3, F-4).

| checklist item | state |
| --- | --- |
| per-task files 1:1 with tasks, _difficulty.md alongside | yes: 0.md, 1.md, _difficulty.md. First revision, no older revisions |
| every comparison section carries a PASS | no: 0.md and 1.md are SOURCE-FACTOR RED |
| extended policies fully covered; scopes pairwise disjoint | yes: GT charter_scope task 0 = {distance, reschedule, wall_mount}, task 1 = {kit, haul_away}, the same as the pre-reveal derivation |
| task tools and GT closed; uuid8s independent and frozen | yes (§ action_binding_and_uuids) |
| each tree has 1-3 prerequisite problems, >= max(n-1,1) value_input edges, an owner=user write, no cycle; difficulty graph acyclic | yes: task 0 n=2 with 2 value_input edges and a user root; task 1 n=1 with 1 value_input edge and a user root; whole graph acyclic |
| every computation: self-sufficient baseline, 4-6 factors (2 parameter, 1 method), >= 1 multi-source and >= 1 cross-difficulty per task, ladders of >= 3 distinct, realistic tiers stated in the rule, each factor bearing weight, baseline != gold | partly. Baselines self-sufficient and != gold everywhere (36.00 / 50.00 / 398.00 / 39.99 / 25.00 vs gold). Every factor bears weight on its world. Multi-source and cross-difficulty present per task. FAILS: honest method count is 0 in distance, reschedule, kit and haul-away (F-4); one ladder has duplicate tiers on Curbside/Threshold (F-3) |
| instantiation-stage gates re-run on the final form | not re-run by the auditor (brief: coordinator snapshot 2026-10-05, all green except traceability, which is deferred to the KB step). No artifact changed during this audit, since the audit edits nothing |

Per-task verdicts: task 0 SOURCE-FACTOR RED (F-4 via T0-1; false proof figures T0-2, T0-3); task 1 SOURCE-FACTOR RED (F-4 via T1-1). Charter-global: SOURCE-POLICY RED F-1 and F-2; SOURCE-FACTOR RED F-3 and F-4.

## revision_2

### charter_global_frozen (revision_2)

- Re-audit round 2, requested by the coordinator after rework. Revision 1 above is left untouched.
- Inputs re-hashed at 2026-10-05T22:21:58Z:
  - delivery.extended.yaml `acd3e80e12de9f1480646385a64313088c00176162f26bbbe8d350ecd9ecc514`. Changed from rev 1 (`d3d19e64…`), so every charter-global section is re-derived in full below.
  - task_tools.py `784d7903…1c90`. Unchanged.
  - 0.view.json `6d133221…3c23643`. Unchanged; the world of task 0 is identical.
  - 1.view.json `e3c0b982d1d2b8fff273cbf60da8b5da08f50817c05465f21370a07deda28668`. Changed; the only difference is the seeded kit row 130426b2 amount, 26.99 (was 20.24).
- Base section: `head -958` of the extended charter still equals blueprint/products/delivery.yaml (only the trailing blank line differs).
- Fields read before freezing this section: the extended charter, task_tools.py, the two masked views, the blueprint. Not read: tasks/{0,1}.json in their revision-2 form, and worklog.md (never).
- contamination_disclosure: the auditor saw the revision-1 GT of both tasks in round 1: values, the read sequence, the trees and the factor traces. Task 0's world is unchanged and task 1's changed only in one seeded amount. The round-2 derivations below are therefore not blind with respect to round-1 conventions (tree shape, read set, step layout). Every scored value of round 2 comes from the reworked charter, which the auditor had not seen solved. The round-2 per-task derivations were frozen before the round-2 task files were opened. Treat their independence accordingly.
- Gate snapshot: supplied by the coordinator, all green except traceability, which is deferred. Not re-run by the auditor.

### policy_conflict_scan (revision_2)

Same five extended policies, tools, owners, triggers and prerequisite graph as rev 1. Changed content:
- distance: free miles and the return-leg multiplier are removed. It now applies a purchase-size rate ($0.90 / $1.10 / P), a Plus reduction per mile ($0.30 / $0.20 / 0), a twelve-month mileage schedule (capped at 10 / graduated / flat) and a tenure discount (10 / 5 / 0). It no longer reads haul-away entries.
- reschedule: the full base sentence is now superseded (see override_declarations). The hold surcharge becomes a storage charge (daily / flat / none). The card multiplier becomes a Visa discount percentage. The courtesy factor is removed. A crew re-slot surcharge on stair-carry units is added.
- wall mount: the late multiplier becomes a late-addition surcharge percentage (50 / 25 / 0). The Plus tier discount is 15 (was 20).
- kit: the scalar appliance scaling becomes a positional kit-place schedule.
- haul-away: the planning reduction and late multiplier are replaced by a recycler-trip schedule (consolidated / graduated / itemized) and a late-request surcharge percentage.

Cross-reads between extended policies: reschedule reads extended_distance units (declared edge) and stair_carry units (written by no extended policy). Wall mount reads haul_away / stair_carry / extended_distance (declared edge) / installation_parts_kit counts. Haul-away reads kit units (declared edge). Distance reads no delivery_charges row. No undeclared cross-problem value read remains (rev-1 O-6 is gone).
Scopes: the worlds still yield task 0 = {distance, reschedule, wall_mount} and task 1 = {kit, haul_away}, disjoint and jointly complete.

### rule_compute_equivalence (revision_2)

Programmatic sweep (whitespace-normalised substring test) over all five policies:
- every `compute_basis` quotation is in its rule;
- every `baseline.rule` sentence is in its rule;
- every `policy_source` is in its rule;
- every overwrite `replaced_by` is in its rule.

Bindings without their own basis are pure differences of quoted bindings (purchase_merchandise, year_spend, televisions, tv_spend, appliances, volume_units, removal_merchandise), the same pattern as rev 1.

Manual binding-by-binding review of the new bindings:
- distance: `miles_charged` = inner (MN(miles, 10)) / inner + 0.5 x outer / miles <- the three schedule sentences. `mile_rate - plus_reduction` <- "A Plus reduction then comes off that per-mile fee". The tenure pct is applied once to the mileage amount. Rounded once.
- reschedule: `storage_charge` = 1.20 x (hold_days - 14) for >= 21 days / 10.00 for 15-20 days / 0 <- the storage sentence. `stair_flights` = SUM of stair_carry units <- "carry as their units in all". `result` = (fee + storage + route + reslot) x moves x (1 - visa_pct/100) <- "taken off once, from the reschedule fee with its storage charge and both surcharges, times the moves that owe one".
- wall mount: `(1 + late_pct/100)` <- "a percentage of the priced labor added to it".
- kit: `first_place_owed` / `later_share` / `kit_places` <- the place sentences ("the kits already standing first and the kits owed after them").
- haul-away: `removal_amount` three-way <- the recycler sentences. `late_removal_pct` <- "a percentage of it added to it".

No compute-only tier and no rule-only tier. PASS. O-1 (RND = Python round-half-even vs the rule's "half up") is unchanged, because check_compute.py line 388 is untouched. It stays a charter observation; per-task files check for ties.

### action_binding_and_uuids (revision_2)

task_tools.py hash unchanged; every target_tool and every computes unchanged. Rev-1 conclusion carried forward on the unchanged hash `784d7903…1c90` together with the unchanged binding set. PASS.

### prerequisite_graph (revision_2)

The four edges, their kinds, gates, forms, resolved_by and policy_source are unchanged and acyclic. Change: the reschedule -> distance `condition` drops the units clause and now says only that an extended_distance row exists, which matches its sentence (rev-1 O-4 closed). The O-3 field-name gate on the state_gate edge is unchanged and remains an observation. PASS.

### prerequisite_sentences (revision_2)

All four sentences are verbatim unchanged; the four-point test and the single-writer derivations of rev 1 hold. Swept for new cross-problem order statements: the new reschedule replacement text ("a short-notice move owes its fee at that moment") is an intra-policy timing statement about the reschedule's own fee and names no other problem. The crew re-slot sentence reads stair_carry entries, which no extended policy writes. No new undeclared order. PASS.

### override_declarations (revision_2)

- distance: declares "road miles beyond … each" and "At booking …". The base "A component whose amount comes to zero is not entered" is still undeclared, but the extended charge can no longer be zero. The reduced per-mile fee is >= 0.60 (minimum rate 0.90 - 0.30; the service-level fees are 1.25 or 1.50). Miles charged >= min(miles beyond, 10) > 0 whenever an appointment is beyond the radius. The tenure discount is <= 10 %. So the two clauses never meet: rev-1 F-2 is closed. The rule now states this itself ("an appointment beyond the included radius always owes a charge of more than zero").
- reschedule: the superseded clause is now the whole base sentence, "A reschedule is free only when at least reschedule_notice_days … whose service_date is the new date." The replacement keeps the notice test for moves at the moment they are made and gives recorded moves a record-only test. A short-notice move owes at the moment it is made; a recorded move within the free reschedules that has no fee entry "stands as a free move". In rev 1's F-1 situation (one recorded move with one day's notice and no fee entry), base is now superseded and the extended text says it stands free: one conclusion. F-1 closed. The base eligibility entry `free_reschedule_notice` repeats the same sentence as its `condition`; it is the structured face of the superseded sentence and not a second rule. "At booking …" is now declared (rev-1 O-2).
- wall mount, kit, haul-away: each now declares "At booking …" alongside its rev-1 declaration (O-2 closed). Haul-away's replacement still drops "only where haul_away_available"; Appliance level has it available. Unchanged, no consequence.

### factor_ladders (revision_2)

| policy | factor | label | tiers | honest? |
| --- | --- | --- | --- | --- |
| distance | purchase_size_mile_rate | parameter | $0.90 / $1.10 / P (1.25 or 1.50) | yes; tiers distinct on every service level (rev-1 F-3 closed) |
| distance | plus_mile_reduction | parameter | $0.30 / $0.20 / 0 | yes |
| distance | twelve_month_mileage_schedule | method | capped at 10 / first 10 full then half / flat | yes: each tier is a different function of miles beyond |
| distance | distance_tenure_discount | parameter | 10 / 5 / 0 % | yes |
| reschedule | storage_by_hold_span | method | $1.20 x (days-14) / flat $10 / none | yes: per-day accrual vs flat vs none |
| reschedule | long_route_surcharge | parameter | $20 / $8 / 0 | yes |
| reschedule | northgate_visa_discount | parameter | 50 / 25 / 0 % | yes; multi-source (order tender with membership renewal tender) |
| reschedule | crew_reslot_surcharge | parameter | $15 / $5 / 0 | yes |
| wall mount | multi_television_pricing | method | positional shares | yes (as rev 1) |
| wall mount | television_spend_allowance / mounting_tender_allowance / late_mounting_surcharge / mounting_member_tier_discount / multi_service_discount | parameter x5 | $25/$10/0; $15/$5/0; 50/25/0 %; 15/10/0 %; 15/10/0 % | yes |
| kit | contractor_kit_price | parameter | $27.99 / $33.99 / P | yes; multi-source |
| kit | fittings_stock_reduction / kit_tenure_reduction / kit_tender_discount | parameter x3 | as rev 1 | yes |
| kit | kit_place_schedule | method | positional: first full, later x0.5 / x0.75 / all full | yes: price depends on the kit's place, standing kits counted first |
| haul-away | removal_included_items / removal_fee_by_purchase / late_removal_surcharge / renewal_billing_discount | parameter x4 | 0/2/P; $15/$20/P; 100/50/0 %; 20/10/0 % | yes |
| haul-away | recycler_trip_schedule | method | fee once / first full then half / every item full | yes |

Counts: distance 4 (3 parameter, 1 method), reschedule 4 (3, 1), wall mount 6 (5, 1), kit 5 (4, 1), haul-away 5 (4, 1). Every computation now has >= 2 parameter and exactly 1 honest method. The rev-1 F-4 count shortfall is closed: every remaining scalar (percent off / added) is labelled `parameter`.

Other ladder checks:
- Every ladder has three disjoint tiers.
- Every tier is stated in the rule.
- Every fall-through equals its factor baseline (mile_rate P; plus 0; miles_charged = miles_beyond; tenure 0; storage 0; route 0; visa 0; reslot 0; mount_units = televisions; allowances / pcts 0; kit_price P; reductions 0; kit_places = kits_owed; included P; removal_fee P; removal_amount = removed_beyond x removal_fee; late 0; renewal 0).
- Each `baseline.rule` ("… with no reduction, schedule or discount", "… with no storage charge, surcharge or discount", etc.) states exactly those defaults.

Realism:
- Observation R2-O1: storage_by_hold_span is not monotone at its tier boundary. A 20-day hold pays the flat $10.00 while a 21-day hold pays 1.20 x 7 = $8.40, and a 22-day hold pays $9.60. Each tier alone is a treatment a business could publish, but the published schedule charges less storage for a longer hold on days 21-22. It is not RED: no two tiers select the same value, and each tier's condition and outcome is individually real. It bears on a task only if that task's hold span is 21-22 days.
- The renewal-billing discount on a haul-away fee (rev-1 O-7, second half) is unchanged; it remains an observation. The return-leg multiplier (first half of O-7) is gone.

### findings (revision_2)

Status of revision-1 charter findings:
- F-1 SOURCE-POLICY RED: CLOSED. The full base sentence is superseded, and the merged semantics are unique in the rev-1 demonstration situation.
- F-2 SOURCE-POLICY RED: CLOSED. A zero extended-distance charge is now impossible, so the inherited zero-component clause never meets the extended rule.
- F-3 SOURCE-FACTOR RED: CLOSED. The tier values are $0.90 / $1.10 and the service-level fees are $1.25 / $1.50; no two coincide.
- F-4 SOURCE-FACTOR RED: CLOSED at charter level. Each computation carries exactly one honest method; the scalars are relabelled `parameter`. Per-task weight is checked in the task files.
- O-1: OPEN, still an observation. RND is unchanged; the per-task files check for ties.
- O-2: CLOSED.
- O-3: OPEN, observation.
- O-4: CLOSED.
- O-5: OPEN, observation (max_reschedules - free_reschedules is still 1 on every level).
- O-6: CLOSED.
- O-7: half closed. The return-leg multiplier is gone; the renewal-billing discount remains an observation.

New charter findings: none RED. New observation R2-O1 (storage tier discontinuity).

### closing_checklist (revision_2)

Written after the round-2 reveals (2026-10-05T22:25:23Z); nothing in the revision_2 charter-global sections above was changed after them.

Status: CLOSED. Both tasks PASS all four relationships in revision 2.

| checklist item | state |
| --- | --- |
| per-task files 1:1 with tasks, _difficulty.md alongside; old revisions traceable | yes. Revision 1 is preserved verbatim above each `## revision_2` heading |
| every comparison section carries a PASS | yes. 0.md rev 2 PASS; 1.md rev 2 PASS |
| extended policies fully covered; scopes pairwise disjoint | yes. GT charter_scope task 0 {distance, reschedule, wall_mount}, task 1 {kit, haul_away} |
| task tools and GT closed; uuid8s independent and frozen | yes. task_tools.py unchanged (`784d7903…`) |
| trees: 1-3 prerequisite problems, >= max(n-1,1) value_input, an owner=user write, acyclic; difficulty graph acyclic | yes. Task 0: n=2, 2 value_input. Task 1: n=1, 1 value_input. Both roots user-owned |
| computations: self-sufficient baseline != gold; 4-6 factors with >= 2 parameter and >= 1 honest method; per task >= 1 multi-source and >= 1 cross-difficulty; ladders >= 3 distinct, real tiers in the rule; every factor bears weight | yes. Counts 4/4/6 (task 0) and 5/5 (task 1), each with exactly 1 honest method. Multi-source: Visa discount (task 0) and contractor kit price (task 1). Every factor moves gold on its world; every baseline differs from gold |
| instantiation-stage gates on the final form | coordinator snapshot after rework: all OK except check_traceability, which is deferred to the KB step. Not re-run by the auditor |

Open observations carried (not grounds for rework): O-1 (RND half-even vs the half-up rule; no tie in any task figure), O-3, O-5, O-7 (renewal-billing discount realism), R2-O1 (storage tier discontinuity at 20/21 days; not reached by either task), O-T0-c / O-T1-c (net_paid_amount), O-T1-b.
