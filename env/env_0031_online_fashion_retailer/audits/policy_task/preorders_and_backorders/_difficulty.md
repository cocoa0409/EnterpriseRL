# Policy-task audit — preorders_and_backorders / charter-global

## charter_global_frozen

- Freeze time: 2026-10-05T00:57Z (UTC). Auditor: independent erl-task-policy-audit agent (did not author the artifacts).
- Freeze hashes (sha256, checked with `sha256sum -c` against the coordinator's HASHES.txt, all OK):
  - `tasks/preorders_and_backorders/preorders.extended.yaml` 86e385d6e50279cdcf37c2d4d0f47042d4d42a9ee524e92e99007e19710347ca
  - `tasks/preorders_and_backorders/task_tools.py` b7294ab797f1dd26cdf46821fc87dc6cbd274873fa2f6d8eeacf79deb926affa
  - `audits/_views/policy_task/preorders_and_backorders/0.view.json` f58134ae…ae5, `1.view.json` b566ed9f…29a
- Entry conditions (Step 0): the gate snapshot `audits/_views/policy_task/preorders_and_backorders/GATES.txt` reports EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK, CACHE-DIFF INFO; traceability deferred to the KB stage. Masked views and hashes were supplied. Input complete.
- Fields read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json` (enum lookups), `blueprint/share_tools.py`, `blueprint/products/preorders.yaml`, `blueprint/products/loyalty.yaml` (per-tier `restocking_fee_waiver` only), the full extended charter, `task_tools.py`, and the two masked views (`frozen_time`, `user_scenario`, `initial_state`).
- Fields masked and not read at freeze time: every `tasks/preorders_and_backorders/tasks/*.json` (and so `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, closures), `tasks/preorders_and_backorders/worklog.md`, `tasks/preorders_and_backorders/_views/`, the scenario-level `worklog.md`, all other scenarios and sibling difficulties.
- Read-domain note: to fix the semantics of the restricted compute expressions (`MONTHS`, `DAYS`, `within_months`, `RND`, `LATEST`, `CFIELD`/`CPARAM`/`X*`), I read the evaluator definitions in `skills/erl-task-instantiate/scripts/check_compute.py` lines 215–390. That file carries no task data and no GT. I record it here because it lies outside the read domain listed in the skill.
- Base copy: lines 1–1077 of the extended charter differ from `blueprint/products/preorders.yaml` only by one trailing blank line (`diff` shows `1077d1076 <` empty). The base copy is verbatim.

### policy_conflict_scan

Extended policies (P1–P6) and their write surfaces:

| id | policy | target_tool (owner) | computes | object |
|---|---|---|---|---|
| P1 | preorders_ext_made_to_order_work_charge | confirm_made_to_order_cancellation_940e1e7b (user) | work_charge_usd | MTO reservation in production, pending cancellation request |
| P2 | preorders_ext_made_to_order_remake_deposit | take_made_to_order_remake_13bceb2b (agent) | deposit_required_usd | new MTO remaking a cancelled MTO |
| P3 | preorders_ext_price_protection | lower_reserved_price_a108b215 (agent) | new_unit_price_usd | open Deposit / Seasonal / back-order reservation |
| P4 | preorders_ext_preorder_cancellation_charge | confirm_preorder_cancellation_aa3f8734 (user) | cancellation_charge_usd | unallocated Deposit Pre-Order cancelled at will |
| P5 | preorders_ext_made_to_order_deposit | pay_reservation_deposit_93996964 (user) | deposit_usd | MTO (non-remake) whose card deposit was declined, within grace |
| P6 | preorders_ext_replacement_deposit | take_replacement_reservation_e3795f43 (agent) | deposit_required_usd | new Deposit Pre-Order replacing one whose size change is used |

- Overlapping subjects. P1/P4 share `preorders_deposit_forfeited`/`preorders_deposit_refunded`, but their objects are disjoint (MTO after production start vs Deposit Pre-Order before allocation). P2/P5/P6 share `preorders_deposit_captured`, and P2/P6 share `preorders_reserved`. Their objects are disjoint too: P5 explicitly excludes "a remake of a cancelled pair", P2 is MTO only and P6 is Deposit Pre-Order only. P3 excludes MTO and Launch by its own rule, which matches the base. No two extended policies compute the same quantity on the same object.
- Triggers. P3 is `state_due`; the rest are `on_request`. P3 fires only on a Deposit / Seasonal / back-order reservation in an open status that has a qualifying lower booking on or after its reservation date. That restriction keeps it from firing on any MTO and on any reservation newly created by P6 when the qualifying booking predates it.
- Eligibility, time anchors and terminal states. The P1/P4 confirmation writes all end in `cancelled / customer_request`; P2/P6 create `reserved`; P5 leaves the reservation `reserved` with its deposit charged. No conflicting terminal states.
- Cross-category reads (loyalty membership, Unlimited pass, order_lines, order_payments, loyalty_ledger, return_cases) are declared in each policy's `cross_category` and are read-only.
- Scope partition (inferred from the views alone; re-checked after reveal): task 0's world holds one in-production MTO with a pending cancellation request and a remake ask, so P1+P2. Task 1's world holds a Deposit Pre-Order with its one size change used plus a declined-deposit MTO, so P3+P4+P5+P6. The two sets are pairwise disjoint and together cover all six extended policies.
- Observation (coverage of the claim): the difficulty claims event types `preorders_delay_consented`, `preorders_size_changed` and `preorders_specs_confirmed`. No extended policy has them as subject and no task exercises them. This is not a relationship failure.

### rule_compute_equivalence

Check 2, policy by policy. Every compute binding has a verbatim `compute_basis` quotation, and the check below covers whether the quotation actually carries what the expression does.

- **P1.** price, held, notices, stage_end, stage_start (three tiers), stage_days (start excluded, end included = `DAYS`), work_share (<14 / 14–<28 / ≥28), personal_mult (personalised and ≥7 production days counted to today / personalised <7 / none), tenure (Icon|Atelier and ≥36 months / Gold|Platinum and ≥24 / else), footwear count (24 months, `orders_line_booked`, `product_class=footwear`), returns count (12 months, any outcome), one product, cap at held, round once. All equivalent. `LATEST(reservation_requests…)` has no `request_type` filter, but the schema enum for `request_type` has the single value `cancellation_with_forfeiture`, so "most recent cancellation request" is equivalent.
- **P2.** paid_pct `RND(deposit_paid*100/price,2)` against "taken to two decimal places" (truncation vs rounding is undetermined; observation O-3). carried_pct (≤14 / ≤45 / else), pass_cut, points (12 months, `loyalty_points_earned`, `posting_date`), setoff_share, setoff_mult (`DAYS(production_start, cancelled_date)`), net pct, then subtract the set-off, then floor, then round. Equivalent.
- **P3. Not equivalent on the Icon/Atelier branch (finding CG-4).** The rule says "protected by the most recent booking of the reserved style in any colour or size at regular or clearance price". The compute is `style_any_*` = `XLATEST` over *all* bookings of the style, and then accepts the result only if its `price_type` is regular or clearance, falling back to `reserved_price` otherwise. These diverge whenever the latest style booking is `flash_sale` (a value in the `order_lines.price_type` enum) and an earlier qualifying regular or clearance booking exists. The Gold/Platinum and other-customer branches are equivalent. The limit, wait, pass and floor bindings are equivalent.
- **P4.** price, held, notices, days_to_ship `DAYS(NOW,current_ship_by_date)` with <15 / >60 / else, waiver (tier's `restocking_fee_waiver` and ≥60 months), look-back months by tier (6 / 9 / 12), returns count over that look-back (≥3 / ≥1 / 0), points (12 months), one product, cap, round. Equivalent.
- **P5.** mto_pct, spend window (≥60 months gives 24 months ÷ 2; <12 months gives since the enrolment month, implemented as `within_months=tenure+1`; else 12 months), spend_cut, footwear_cut, pct_net, floor, round. Equivalent within the evaluator's whole-month convention.
- **P6.** rep_pct, wait_factor (`held_days` = reservation date to cancellation date), pass_cut, apparel count (12 months), pct_net = `rep_pct*wait_factor - pass - apparel`, set-off subtracted before the floor, round. The `setoff_share` compute requires `left_standing == 0`, but the set-off sentence it quotes says only "within … days of that cancellation … and `setoff_none` later or when that reservation is not cancelled". The "settled" conjunct comes from the prerequisite sentence, not the set-off sentence. At any legitimate replacement write the gate makes it true, so no consequence follows (observation O-4).
- Rounding: every policy says "rounded half up to the cent", and the evaluator's `RND` is Python `round` on binary floats. No tie arises in either task world (checked in each task file), so this is observation O-3.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (table above).
- uuid8 tails: 940e1e7b, 13bceb2b, a108b215, aa3f8734, 93996964, e3795f43. They are pairwise distinct, share no prefix and show no sequence or batch pattern. PASS.
- No tool body refuses, errors or branches on a prerequisite. Every body does `find`/`update`/`create`, computes no amount and checks no status (`task_tools.py` lines 11–276). PASS.
- Docstrings naming another tool: none.
- Ordering words in docstrings (observation O-5):
  - `lower_reserved_price_a108b215`: "the lower price is what the customer pays (or what a deposit or charge is worked out on) from then on". This tells the agent that a later deposit or charge computation reads the lowered price, which is exactly the hop that P4 and P6 encode as prerequisites.
  - `take_made_to_order_remake_13bceb2b`: "remakes a made-to-order pair the customer has cancelled" names the waited-on state of P2's edge.
  - Every docstring's "Afterwards the reservation shows …" describes the result of the same call, not a sequence position.
  - I can demonstrate no change to a scored outcome, so this stays an observation.

### prerequisite_graph

Check 7:

| blocked | depends on | kind | gate binding | form | `policy_source` verbatim in own rule | in depended rule | resolved_by == depended target_tool |
|---|---|---|---|---|---|---|---|
| P2 | P1 | value_input | setoff_share (exists) | state | yes | no | yes |
| P4 | P3 | value_input | price (exists) | state | yes | no | yes |
| P6 | P4 | value_input | setoff_share (exists) | state | yes | no | yes |
| P6 | P3 | value_input | price (exists) | state | yes | no | yes |
| P6 | P5 | state_gate | `reservation_events.amount_usd` | state | yes | no | yes |

- `prerequisite` is filled everywhere (P1, P3 and P5 are `[]`). Every `problem` is an extended policy id of this file and none is self-referential. The graph is acyclic: P3→P4→P6, P3→P6, P5→P6, P1→P2. No `fallback_reason` appears, which is correct because all edges are state form.
- Observation O-6: the P6←P5 `state_gate` names a DB field as its `gate`, not an eligibility gate id (extended policies carry no `eligibility` list). Its `effect` reads "The held made-to-order reservation whose card charge was declined shows its deposit charged", which describes one situation rather than the general state. That is mild authoring-viewpoint phrasing.

### prerequisite_sentences

Check 6, edge by edge:

- **P2←P1**: "A remake is taken only after the pair it remakes shows status cancelled, its cancellation request confirmed and no deposit left standing on it."
  - Connective: "only after". Form: state (reservations.status, reservation_requests.request_status, the reservation_events sum). No tool, id or snake_case.
  - Single resolving write: only `confirm_made_to_order_cancellation_940e1e7b` sets an MTO to cancelled, confirms its request and books entries summing the deposit to zero. `confirm_preorder_cancellation_aa3f8734` confirms no request and is P4's Deposit Pre-Order write.
  - Derivation: sentence, then the records (status, request, events), then P1's rule ("the cancellation is made on the customer's own in-person confirmation of the pending cancellation request … keeps a work charge … refunds the rest"). That leads to P1's write, in one reading.
  - Observation O-7: the same waited-on state is worded again inside P2's rule, in the set-off sentence ("when the pair stands cancelled with its latest cancellation request confirmed and no deposit left standing on it") and in "a Made-to-Order pair the customer has cancelled". See CG-2 for the consequence on the factor.
- **P4←P3**: "The cancellation charge is fixed only after the reserved unit price reflects every lower regular price of the reserved style recorded on the customer's orders since the reservation date."
  - Connective and form pass. **Scope fails; see CG-5.**
- **P6←P4**: "A replacement is taken only after the reservation it replaces shows status cancelled with its deposit settled to nothing."
  - Connective and form pass. Single resolving write: P4's `confirm_preorder_cancellation_aa3f8734`, the only policy that cancels a Deposit Pre-Order at the customer's request.
  - Observation O-7: P6's set-off fall-through "… or when that reservation is not cancelled" restates the gated state.
- **P6←P3**: "The deposit on a replacement is not worked out until the reserved unit price of the reservation it replaces reflects every lower regular price of its style recorded on the customer's orders."
  - Connective and form pass. **Scope fails; see CG-5.** This sentence also drops the "since the reservation date" bound.
- **P6←P5**: "A replacement is not taken until every Made-to-Order Reservation and Deposit Pre-Order the customer holds in status reserved shows its deposit charged."
  - Connective "not until". Form: state.
  - Resolving write for an MTO: `pay_reservation_deposit_93996964` under P5, a single reading.
  - Observation O-8: the sentence also covers a reserved Deposit Pre-Order without a deposit, and no extended policy resolves that case (P5 is MTO only). Neither world contains such a row.
- No rule states a cross-problem order that grounds no declared edge. The "cancellation first" clauses in P1 and P4 order steps inside one write. The superseded base clause "A refund or forfeiture is booked only once the reservation is in status cancelled" grounds no edge.

### override_declarations

Check 1, findings half:

- **P1** against `preorders_evt_cancellation_refund`. The forfeiture-after-cutoff sentence and the "booked only once … cancelled" sentence are superseded and declared. The cutoff sentence, the delay-notice full-refund sentence, the original-tender sentence and the seller-cause sentences are followed. Against `preorders_evt_made_to_order`, the confirmation, window and lead-time sentences are followed.
- **P2** against `preorders_reservation`. The deposit-formula sentence is superseded and declared. The ship-by sentence ("no later than"; P2 uses exactly +56 days), the units cap, card-only deposit and verbatim personalisation are followed. `agg_multi_holding`, `agg_launch_style_limit` (not applicable) and `evt_deposit` are followed.
- **P3** against `preorders_evt_price_protection`.
  - Sentence 1 (lowest regular *site* price of the *SKU*) and sentence 3 (clearance/flash/code-only never count) are superseded and declared. The status sentence and the "Launch / MTO keep their price" sentence are followed.
  - Observation O-9: the `replaced_by` of sentence 1 states only the cap. The rule's other departures from that sentence ("most recent" instead of "lowest", "booked order line on the customer's own orders" instead of "site price", style instead of SKU for upper tiers) are carried by the rule, not by `replaced_by`. The superseded sentence is named, so the merged semantics are unique.
  - Observation O-10: the rule defines the protection limit twice. "never lowered by more than the protection limit, which is `limit_standard` of the reserved unit price" is unhedged; the later sentence sets it per tier. Specific-over-general resolves this, and the per-task files give the number each reading yields.
- **P4** against `preorders_evt_cancellation_refund`. "Before the cutoff the deposit is refunded in full" and "booked only once … cancelled" are superseded and declared. The rest is followed.
  - Observation O-11: the superseded full-refund sentence covers every type, but the replacement speaks only of Deposit Pre-Orders. The merged rule for an MTO cancelled before production start, which the base refunded in full, is left without a stated refund. Neither world contains that case.
  - Observation O-12: P4 books a `preorders_deposit_forfeited` row on a Deposit Pre-Order, while the base event meaning says it is booked "because the customer cancelled a made-to-order item after production started". This is an event-definition drift, not a scored quantity.
- **P5** against `preorders_reservation`. The deposit-formula sentence is superseded and declared.
  - Observation O-13: P5 captures the deposit after a declined charge at reservation, within `payment_decline_grace_hours`. The base says "charged at reservation" (`preorders_reservation`) and "captured once, at reservation" (`preorders_evt_deposit`). The base itself carries a decline grace for MTO (`payment_decline_grace_hours: 48`, cancel reason `payment_declined`), and the capture timing is not scored.
- **P6** against `preorders_reservation`. The deposit-formula sentence is superseded and declared. Against `preorders_evt_size_change`, the "at most `max_size_changes`" and "cancel and reserve again" sentences are compatible: the replacement is a cancel-and-re-reserve. Ship-by stays within 90 days. No undeclared override found.
- No anonymous intermediate factor, 0/1 multiplier or dropped base branch was found.

### factor_ladders

Effect labels as declared, and as judged ("→" marks a mislabel). MS means multi-source: every tier beyond the fall-through is a conjunction or disjunction over **distinct records**.

| policy | factor | declared | judged | tiers | MS? | cross_difficulty |
|---|---|---|---|---|---|---|
| P1 | production_stage_share | parameter | parameter | 3 (0.15/0.30/0.50) | no (one threshold on a day count) | – |
| P1 | stage_clock_start | method | method (anchor date changes how stage_days is computed) | 3 | no (all conditions on one reservation row) | – |
| P1 | personalisation_multiplier | method | **→ parameter**: all tiers compute `work_share × m`, m ∈ {1.5, 1.2, 1.0} | 3 | no (one row) | – |
| P1 | rewards_tenure_relief | parameter | parameter | 3 (0.6/0.8/1.0) | no (tier, status and enrolled_date are one membership row) | loyalty |
| P1 | footwear_client_relief | parameter | parameter | 3 | no | orders |
| P1 | return_record_relief | parameter | parameter | 3 | no | returns |
| P2 | paid_percentage_carry | method | method (carry paid % / average / standard %) | 3 | no (one condition: days since the request) | – |
| P2 | unlimited_plan_reduction | parameter | parameter | 3 (5/2/0) | no (plan and status are one pass row) | pass |
| P2 | rewards_points_reduction | parameter | parameter | 3 (3/1/0) | no | loyalty |
| P2 | work_charge_setoff | parameter | parameter | 3 (0.4/0.2/0) | **formally yes** (reservations.status, reservation_requests, reservation_events, request date), **but see CG-2** | – |
| P2 | setoff_personalisation_multiplier | method | **→ parameter**: set-off × {1.2, 1.1, 1.0} | 3 | no | – |
| P3 | qualifying_booking_selection | method | method (which booking set gives the price) | 3 | no (tier and months are one membership row) | orders |
| P3 | protection_limit | parameter | parameter | 3 (0.15/0.10/0.05) | no | loyalty |
| P3 | waiting_addition | parameter | parameter | 3 | no | – |
| P3 | unlimited_limit_addition | parameter | parameter | 3 | no | pass |
| P4 | ship_by_proximity_rate | parameter | parameter | 3 (0.15/0.05/0.10) | no | – |
| P4 | restocking_waiver | parameter | parameter | 3 (0.5/0.75/1.0) | no (tier param and months are one membership row) | loyalty |
| P4 | returns_look_back | method | **→ parameter**: all tiers compute the same count with `within_months` ∈ {6, 9, 12} | 3 | no | loyalty |
| P4 | returns_adjustment | parameter | parameter | 3 | no | returns |
| P4 | points_relief | parameter | parameter | 3 | no | loyalty |
| P5 | made_to_order_rate | parameter | parameter | 3 (30/40/50) | no (one row) | loyalty |
| P5 | spend_window | method | method (24-month yearly average / since enrolment / trailing 12 months) | 3 | no | loyalty |
| P5 | spend_reduction | parameter | parameter | 3 | no | orders |
| P5 | footwear_reduction | parameter | parameter | 3 | no | orders |
| P6 | replacement_rate | parameter | parameter | 3 (10/15/20) | no | loyalty |
| P6 | waiting_factor | method | **→ parameter**: pct × {0.8, 0.9, 1.0} | 3 | no | – |
| P6 | charge_setoff | parameter | parameter | 3 (0.4/0.2/0) | **formally yes** (reservations.status, reservation_events, cancelled_date), **but see CG-2** | – |
| P6 | unlimited_points_off | parameter | parameter | 3 | no | pass |
| P6 | apparel_points_off | parameter | parameter | 3 | no | orders |

- Every ladder has three pairwise-disjoint tiers. No two tiers of one ladder select the same value or method. Every tier, with its condition and value or method, is stated in the policy's `rule` and implemented as a branch of the `decides` binding (except the P3 Icon branch, CG-4). `decides` is never `result`, and binding sets within each policy are disjoint.
- Baselines:
  - P1, P2, P3, P4 and P5: `baseline.rule` sentences are all verbatim in the `rule`, its params are the named defaults, and each factor's fall-through equals its baseline.
  - P6: `baseline.rule` contains "less any charge set-off", a quantity no baseline sentence defines (CG-3).
- Counts after the judged labels:
  - P1: 6 factors (5 parameter, 1 method). P2: 5 (4P / 1M). P3: 4 (3P / 1M). P5: 4 (3P / 1M).
  - **P4: 5 (5P / 0M). P6: 5 (5P / 0M).** Both fall below the required 1 method.
  - Cross-difficulty factors read loyalty, orders, returns and pass. Both tasks have at least one.
- Realism (observation O-14): P1 stage_clock_start tier 2 counts the work stage from the *reservation date* for a pair "confirmed on the reservation date and whose production started fewer than 10 days after". No production work exists on the reservation date. Tier 1 gives a reason (leather cut at confirmation); tier 2 gives none. I judge this a doubtful condition, not a demonstrable one. All other conditions and outcomes are ones a fashion retailer could publish.

### findings

- **CG-1 — SOURCE-FACTOR RED (mislabelled effect; method count).**
  - Symptom: four factors labelled `method` select only a number substituted into one unchanged formula. These are P1 `personalisation_multiplier`, P2 `setoff_personalisation_multiplier`, P4 `returns_look_back` and P6 `waiting_factor`.
  - Root cause: multiplier and window ladders were declared as methods.
  - Evidence: P1 rule "the work share is multiplied by `pers_full` … by `pers_part` … by `pers_none`"; P2 "multiplied by `mult_long` … `mult_short` … `mult_none`"; P4 "the last `look_top_months` months … `look_mid_months` … `look_std_months`" fed into one count (`XCOUNT(..., within_months=look_months)`); P6 "multiplied by `wait_long_factor` … `wait_mid_factor` … left as it is".
  - Demonstrated consequence: P4 and P6 are left with **zero** honest `method` factors against the floor of one. P1 and P2 keep one honest method each (stage_clock_start, paid_percentage_carry), so for them only the labels are wrong.
  - Bears on: task 1 (P4, P6: count failure; P4/P6 labels) and task 0 (P1, P2: labels).
- **CG-2 — SOURCE-FACTOR RED (a conjunct that holds for every customer who reaches the write; no genuine multi-source factor).**
  - Symptom: the only factors whose tiers combine conditions over distinct records are P2 `work_charge_setoff` and P6 `charge_setoff`. Their cross-record conjunct restates the blocked policy's own prerequisite gate.
  - Evidence:
    - P2 gate "A remake is taken only after the pair it remakes shows status cancelled, its cancellation request confirmed and no deposit left standing on it" against the P2 set-off tier condition "when the pair stands cancelled with its latest cancellation request confirmed and no deposit left standing on it" (factor ladder: "pair cancelled, request confirmed and deposit settled AND …").
    - P6 gate "A replacement is taken only after the reservation it replaces shows status cancelled with its deposit settled to nothing" against the P6 ladder "replaced reservation cancelled and settled AND …" and the fall-through "… or when that reservation is not cancelled".
  - Demonstrated consequence: at every write the policy permits, that conjunct is true, so it divides no customers. Struck out, each set-off ladder is a single condition on one date gap. No other factor in either task is multi-source over distinct records (table above: every other compound condition reads one membership, pass or reservation row). Neither task carries a genuine multi-source factor.
  - Bears on: task 0 (P2) and task 1 (P6).
- **CG-3 — SOURCE-FACTOR RED (incoherent baseline, P6).**
  - Symptom: `baseline.rule` reads "The deposit on a replacement is its reserved unit price times its units times the replacement deposit percentage, divided by 100, less any charge set-off; …". No baseline sentence says what the "charge set-off" is.
  - Consequence: a reader of the computation document alone can take the set-off as nothing, or as the cancellation charge kept in full. The two give different fall-back numbers (shown on task 1's world in `1.md`).
  - Bears on: task 1.
- **CG-4 — SOURCE-POLICY RED (rule ≠ compute, P3 Icon/Atelier branch).**
  - Constructed situation: an active Icon member enrolled 36 months or more holds a Deposit Pre-Order reserved at 200.00. On their own orders since the reservation date are a clearance booking of the style at 170.00 and, later, a flash_sale booking of the style at 150.00.
  - Rule: protected by "the most recent booking … at regular or clearance price", which is 170.00, then floored by the limit.
  - Compute: `style_any_type` is `flash_sale`, so `protected_price = reserved_price` and nothing is lowered.
  - These are two different results in the same situation. Bears on no task in this difficulty: task 1's customer is Platinum. The per-task file records it as an observation.
- **CG-5 — SOURCE-POLICY RED (prerequisite sentence broader or narrower than the edge's condition, P4←P3 and P6←P3).**
  - The sentences require the reserved price to "reflect every lower regular price of the reserved style". P3's own result differs from that in four ways:
    - For every customer not on the upper tiers, P3 protects only from the reserved **SKU** itself.
    - For Icon/Atelier members of 36 months or more, P3 also counts **clearance**.
    - P3 takes the **most recent** qualifying booking, not every lower one.
    - P3 **caps** the lowering at the protection limit.
  - P6's sentence also drops "since the reservation date", which P3 requires.
  - Constructed situation: a non-member holds a Deposit Pre-Order of style X in black at 300.00, and books style X in camel at a regular 250.00 after the reservation date.
    - P4's sentence keeps the charge unfixed until the reserved price reflects 250.00.
    - P3 gives this customer the SKU-only tier, so the price stays 300.00.
    - The waited-on state is unreachable by any write of the difficulty, so there are two conclusions: the charge can never be fixed, or the agent proceeds contrary to the sentence.
  - The same holds for P6 with a style booking dated before the reservation date.
  - Bears on: task 1's edges. Whether task 1's world produces a different value is examined in `1.md`.
- Observations O-3 to O-14 are listed in the sections above. None changes a scored value in either world (verified in the task files where it applies).

## closing_checklist

Written after both reveals (2026-10-05T01:01Z–01:03Z). The sections above are pre-reveal; their freeze hash is 3e307f18… in `FREEZE_HASHES.txt`. Only this section changed after the reveals.

- Per-task files `0.md` and `1.md` correspond one-to-one with `tasks/0.json` and `tasks/1.json`, with `_difficulty.md` alongside. There are no old revisions (first audit).
  - **Not every comparison carries a full PASS.** Both tasks are SOURCE-FACTOR RED. Policy self-consistency, problem tree and unique solution PASS in both.
- Coverage and scope:
  - GT `charter_scope` confirms the blind partition: task 0 holds P1 and P2; task 1 holds P3, P4, P5 and P6. They are pairwise disjoint and jointly complete over the six extended policies.
  - Task tools and GT are closed. Every uuid8 is independent.
- Trees:
  - Task 0: 1 prerequisite problem, 1 value_input edge, a user write (P1).
  - Task 1: 3 prerequisite problems, 3 value_input edges, user writes P4 and P5.
  - The whole graph is acyclic and no edge crosses tasks.
- Factors:
  - Every factor of both tasks bears weight: 29 of 29 substitutions move the scored value.
  - **Not satisfied:**
    - P4 and P6 have no honest `method` factor (CG-1).
    - Neither task has a genuine multi-source factor (CG-2).
    - P6's baseline is indefinite (CG-3).
- Charter-level SOURCE-POLICY REDs CG-4 (P3 rule ≠ compute on the Icon branch) and CG-5 (prerequisite sentence scope on P4←P3 and P6←P3) stand, with no demonstrated cost in either task's world.
- Gate re-run on the final form: not performed. The difficulty does not reach closing, and the auditor neither edits artifacts nor re-runs gates (Step 0).

**Difficulty verdict: the source-layer audit does NOT pass** (SOURCE-FACTOR RED in both tasks, plus charter-level SOURCE-POLICY REDs CG-4 and CG-5).

## revision_2

### charter_global_frozen (round 2)

- Freeze time: 2026-10-05, round-2 freeze, before any round-2 task JSON was opened. Auditor: the same independent auditor as round 1.
- Inputs (`sha256sum -c audits/_views/policy_task/preorders_and_backorders/r2/HASHES.txt`, all OK):
  - extended charter **b543d54a47e00fc05522a4f4eeabe191ba53d4f5936a906661fac8800d1f8c31** (round 1: 86e385d6…, changed)
  - task_tools.py **87d549b483d0dcbed7e41cc0e8327a5b9f4c9872eb53b81cca28426609c22e14** (round 1: b7294ab7…, changed)
  - r2/0.view.json d9b50c01… (changed); r2/1.view.json b566ed9f… (**byte-identical** to round 1)
  - Both shared inputs changed, so every charter-global section below is **re-derived in full**, not carried forward.
- Entry conditions: `r2/GATES.txt` reports EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE OK, with CACHE-DIFF INFO and traceability deferred. Input complete.
- Masked at freeze: `tasks/*.json` (round 2), all worklogs, `tasks/preorders_and_backorders/_views/`.
- Base copy: lines 1–1076 of the charter are byte-identical to `blueprint/products/preorders.yaml` (`diff` is empty). Verbatim.
- Round-1 sections above are left untouched.
- contamination_disclosure: this auditor revealed the round-1 GT of both tasks in round 1, so it knows the round-1 scored values. Every round-2 value below was recomputed from the round-2 charter and views. For task 0, the round-2 charter leaves P1 and P2 arithmetically unchanged on that world, so its round-2 derivation cannot claim independence from the known round-1 values. The round-2 changes to P4 and P6 make task 1's values new.

### policy_conflict_scan (round 2)

- Objects, subjects, triggers, terminal states and cross-category reads are as in round 1, with these changes:
  - P6 no longer reads the pass.
  - P2 and P3 now read loyalty and pass together.
  - P4 no longer has a tier-dependent returns look-back; it now has a tier-dependent points-counting rule.
- Overlaps: P1/P4 objects disjoint (MTO in production vs unallocated Deposit Pre-Order); P2/P5/P6 objects disjoint (P5 excludes remakes). P3 never fires on an MTO, and it does not fire on a replacement whose qualifying booking predates the replacement's reservation date.
- No two extended policies compute the same quantity on the same object.
- Scope partition from the views: task 0 holds P1 and P2; task 1 holds P3, P4, P5 and P6. They are disjoint and jointly complete. The O-2 observation (claimed event types delay_consented, size_changed and specs_confirmed are not exercised) is unchanged.

### rule_compute_equivalence (round 2)

- Every compute binding of every policy has a `compute_basis` that appears verbatim in its own `rule` (scripted check, all true).
- **P1**: unchanged arithmetic. Tier 2 of the stage clock now carries its reason ("built on a stock pattern whose leather is cut on the day it is ordered"); the compute is unchanged and equivalent.
- **P2**:
  - Set-off: `setoff_share` now depends only on days since the most recent cancellation request (≤14 / ≤30 / else). This matches "`setoff_full` of it when the remake is taken within `setoff_full_days` days … and `setoff_none` later".
  - `paid_pct`: the rule now says "rounded half up to two decimal places", matching `RND`.
  - `pass_cut`: requires an active annual or monthly Unlimited plan **and** an active Gold, Platinum, Icon or Atelier membership, matching "held by an active Gold, Platinum, Icon or Atelier member … any other customer, including an Unlimited member below Gold, takes `cut_none`".
  - Equivalent. **O-22:** the binding `last_request_status` is computed but no longer used by any expression. It is harmless.
- **P3**:
  - Icon/Atelier branch: the compute now takes the latest clearance booking and the latest regular booking of the style, keeps those on or after the reservation date, and uses the later of the two. That equals "the most recent booking of the reserved style in any colour or size at regular or clearance price". A flash_sale booking no longer interferes.
  - Re-run of the round-1 constructed case (Icon ≥36 months; clearance 170.00 then a later flash_sale 150.00): the compute now gives 170.00, the same as the rule. **CG-4 is closed.**
  - **O-21:** on a same-day tie between a regular and a clearance booking, the compute prefers the regular one (`DAYS(reg, clr) > 0`); the rule does not state which wins. No task world has a tie.
  - The pass addition carries the same Gold+ conjunct as in P2. Equivalent.
- **P4**:
  - Returns are counted over a fixed `ret_months` 12 months.
  - New points counting: Platinum/Icon/Atelier count earned and bonus entries by `posting_date`; Gold/Silver count earned entries by `posting_date`; everyone else counts earned entries by `available_date`, so pending points drop out because a future available date never falls inside the window.
  - Equivalent to the rule sentences.
  - **O-23:** the binding `pts_available_earned` is listed under the `points_relief` factor, although only the counting method (`points_counted`) reads it. Binding sets stay disjoint, and nothing is scored differently.
- **P5**: unchanged and equivalent.
- **P6**:
  - Set-off depends on days since the replaced reservation's cancellation date, matching the rule. The round-1 "settled" conjunct (O-4) is gone.
  - Apparel count: members enrolled 60 months or more count the last 24 months ÷ 2; members under 12 months count since the enrolment month; everyone else counts the last 12 months. Then thresholds 6 / 3. Matches the rule.
  - `pct_net = rep_pct × wait_factor − apparel_cut` matches "first set by tier, then scaled by the waiting factor, and the apparel reduction is then subtracted".
  - Equivalent.
- Rounding: every rule still says half up, and `RND` is Python `round`. No task value lands on a tie; see the task files (O-3 residual).

### action_binding_and_uuids (round 2)

- Each `(target_tool, computes)` pair is still claimed by exactly one policy. The six uuid8 tails are unchanged (940e1e7b, 13bceb2b, a108b215, aa3f8734, 93996964, e3795f43): distinct and not batch-derived.
- No tool body contains a status check, refusal or error branch (grep for raise / error returns / status conditions finds none).
- Docstrings:
  - `lower_reserved_price_a108b215` now reads "nothing else on the reservation changes and no money moves. Afterwards the reservation shows the new reserved unit price." The round-1 "what a deposit or charge is worked out on … from then on" is removed. **O-5 is closed for this tool.**
  - **Residual O-5:** `take_made_to_order_remake_13bceb2b` still describes its object as "a made-to-order pair the customer has cancelled". This describes the object, not a sequence, and contains no ordering word.

### prerequisite_graph (round 2)

| blocked | depends on | kind | gate binding | form | `policy_source` verbatim in own rule | in depended rule | resolved_by == target |
|---|---|---|---|---|---|---|---|
| P2 | P1 | value_input | setoff_share (in compute; the work charge enters through `work_charge_kept`) | state | yes | no | yes |
| P4 | P3 | value_input | price | state | yes | no | yes |
| P6 | P4 | value_input | setoff_share | state | yes | no | yes |
| P6 | P3 | value_input | price | state | yes | no | yes |
| P6 | P5 | state_gate | `reservation_events.amount_usd` | state | yes | no | yes |

- Acyclic. Every policy fills `prerequisite`. No `fallback_reason` (correct, since all edges are state form).
- P6←P5 `effect` now reads "Once every reserved made-to-order reservation shows its deposit charged, the replacement may be taken", which is general. **O-6 is closed for the wording.** The `gate` field still names a DB field rather than an eligibility id (residual structural note, no consequence).

### prerequisite_sentences (round 2)

- **P2←P1** is unchanged: "A remake is taken only after the pair it remakes shows status cancelled, its cancellation request confirmed and no deposit left standing on it." The four-point test passes and P1's confirmation is the single resolving write.
  - P2's set-off sentence no longer restates the gated state, so O-7 is closed there.
  - **Residual O-7:** the definition "a Made-to-Order pair the customer has cancelled" remains.
- **P4←P3**: "The cancellation charge is fixed only after the reserved unit price stands at the reservation's protected reserved price."
  - Connective "only after". Form: state (`unit_price_usd` against the term "protected reserved price", which P3's rule defines: "the price this protection gives the reservation, its protected reserved price, is the higher of … never above the reserved unit price … and it is the reserved unit price itself when no qualifying booking is lower").
  - No tool, id or snake_case.
  - Scope now equals the condition ("equals its protected reserved price as price protection defines it"), including the cap, the tiered booking set, "most recent" and the reservation-date bound.
  - Single resolving write: `lower_reserved_price_a108b215` under P3.
  - The round-1 constructed case (non-member, other-colour lower booking): the sentence now waits on P3's own SKU-only result, which leaves the price as it stands, so the state holds and nothing is blocked. **CG-5 is closed for P4.**
- **P6←P3**: "The deposit on a replacement is not worked out until the reservation it replaces carries its protected reserved price as its reserved unit price." Same analysis, and the reservation-date bound is inherited through the defined term. **CG-5 is closed for P6.**
- **P6←P4** is unchanged and passes. The set-off fall-through no longer says "or when that reservation is not cancelled", so O-7 is closed there.
- **P6←P5**: "A replacement is not taken until every Made-to-Order Reservation the customer holds in status reserved shows its deposit charged." Now limited to MTO, which P5 resolves. **O-8 is closed.**
- No rule states an undeclared cross-problem order. The "cancellation first" clauses still order steps inside one write.

### override_declarations (round 2)

- **P1, P2, P5, P6**: same declared supersessions as round 1. Every `superseded_clause` is verbatim in its base rule and every `replaced_by` is verbatim in the extended rule (scripted check). No undeclared override.
- **P3**: the supersession of sentence 1 now carries a `replaced_by` that defines the limit as "a share … whose standard value is `limit_standard`" and defines the "protected reserved price". The unhedged "which is `limit_standard`" is gone. **O-10 is closed.** O-9 (the `replaced_by` not spelling out every departure) is left as is by the reworker; no consequence.
- **P4**: the `replaced_by` now ends "a cancellation at will of any other type before its cutoff is still refunded in full", so the merged rule for an MTO before production start is again a full refund. **O-11 is closed.** O-12 (forfeited event booked on a Deposit Pre-Order) is left as is.
- O-13 (P5 capture after a declined charge) is left as is; no consequence.

### factor_ladders (round 2)

| policy | factor | declared | judged | tiers / outcomes | multi-source over distinct records | cross_difficulty |
|---|---|---|---|---|---|---|
| P1 | production_stage_share | parameter | parameter | 0.15 / 0.30 / 0.50 | no | – |
| P1 | stage_clock_start | method | method | specs date / reservation date (stock pattern, now with a reason, **O-14 closed**) / production start | no | – |
| P1 | personalisation_multiplier | parameter | parameter (**relabelled**) | 1.5 / 1.2 / 1.0 | no | – |
| P1 | rewards_tenure_relief | parameter | parameter | 0.6 / 0.8 / 1.0 | no (one membership row) | loyalty |
| P1 | footwear_client_relief | parameter | parameter | 0.85 / 0.92 / 1.0 | no | orders |
| P1 | return_record_relief | parameter | parameter | 0.9 / 0.95 / 1.0 | no | returns |
| P2 | paid_percentage_carry | method | method | carry / average / standard % | no | – |
| P2 | unlimited_plan_reduction | parameter | parameter | 5 / 2 / 0 | **yes**: pass row (plan, status) AND loyalty row (tier Gold+) | pass |
| P2 | rewards_points_reduction | parameter | parameter | 3 / 1 / 0 | no | loyalty |
| P2 | work_charge_setoff | parameter | parameter | 0.4 / 0.2 / 0 (days only; the gate conjunct is removed) | no | – |
| P2 | setoff_personalisation_multiplier | parameter | parameter (**relabelled**) | 1.2 / 1.1 / 1.0 | no | – |
| P3 | qualifying_booking_selection | method | method | style regular-or-clearance / style regular / SKU regular | no | orders |
| P3 | protection_limit | parameter | parameter | 0.15 / 0.10 / 0.05 | no | loyalty |
| P3 | waiting_addition | parameter | parameter | 0.03 / 0.01 / 0 | no | – |
| P3 | unlimited_limit_addition | parameter | parameter | 0.02 / 0.01 / 0 | **yes**: pass row AND loyalty row | pass |
| P4 | ship_by_proximity_rate | parameter | parameter | 0.15 / 0.05 / 0.10 | no | – |
| P4 | restocking_waiver | parameter | parameter | 0.5 / 0.75 / 1.0 | no | loyalty |
| P4 | returns_adjustment | parameter | parameter | 1.2 / 1.1 / 1.0 (fixed 12-month window) | no | returns |
| P4 | points_count_method | method | **method** (the tiers change which entries count, earned+bonus vs earned only, and the anchoring date, posting vs available; not a number fed into one formula) | 3 distinct counting rules | no | loyalty |
| P4 | points_relief | parameter | parameter | 0.8 / 0.9 / 1.0 | no | loyalty |
| P5 | made_to_order_rate | parameter | parameter | 30 / 40 / 50 | no | loyalty |
| P5 | spend_window | method | method | 24-month ÷ 2 / since enrolment / 12 months | no | loyalty |
| P5 | spend_reduction | parameter | parameter | 5 / 2 / 0 | no | orders |
| P5 | footwear_reduction | parameter | parameter | 5 / 2 / 0 | no | orders |
| P6 | replacement_rate | parameter | parameter | 10 / 15 / 20 | no | loyalty |
| P6 | waiting_factor | parameter | parameter (**relabelled**) | 0.8 / 0.9 / 1.0 | no | – |
| P6 | charge_setoff | parameter | parameter | 0.4 / 0.2 / 0 (days since cancellation) | no | – |
| P6 | apparel_window | method | method (24-month yearly average / since enrolment / 12 months) | 3 | no | loyalty |
| P6 | apparel_points_off | parameter | parameter | 2 / 1 / 0 | no | orders |

- Counts as judged:

  | policy | factors | parameter | method |
  |---|---|---|---|
  | P1 | 6 | 5 | 1 |
  | P2 | 5 | 4 | 1 |
  | P3 | 4 | 3 | 1 |
  | P4 | 5 | 4 | 1 |
  | P5 | 4 | 3 | 1 |
  | P6 | 5 | 4 | 1 |

  Every policy has 4–6 factors, at least 2 `parameter` and at least 1 honest `method`. **CG-1 is closed.**
- Multi-source per task: task 0 has P2 `unlimited_plan_reduction`; task 1 has P3 `unlimited_limit_addition`. Each is a conjunction over two distinct records (pass_memberships and loyalty_memberships). Neither conjunct holds for every customer who reaches the write; Unlimited members below Gold, and Gold+ members without a plan, fall through. A retailer weighs both for a perk. The round-1 vacuous set-off conjuncts are removed from P2 and P6. **CG-2 is closed.**
- Baselines: every `baseline.rule` sentence is verbatim in its `rule`, and every factor's fall-through equals its baseline. P6's baseline no longer contains "less any charge set-off"; it reads price × `deposit_pct` / 100, floored and rounded, which is definite. **CG-3 is closed.**
- Every ladder has three disjoint tiers with distinct outcomes, all stated in the `rule` and implemented in the `decides` binding.

### findings (round 2)

| round-1 item | status | evidence |
|---|---|---|
| CG-1 | **closed** | relabelled P1, P2 and P6 multipliers; P4 `points_count_method` and P6 `apparel_window` are honest methods |
| CG-2 | **closed** | set-off gate conjuncts removed (P2 `setoff_share`, P6 `setoff_share` read days only); pass∧loyalty conjunctions in P2 and P3 |
| CG-3 | **closed** | P6 `baseline.rule` is definite |
| CG-4 | **closed** | P3 Icon compute re-run on the constructed case gives 170.00, the same as the rule |
| CG-5 | **closed** | P4 and P6 sentences wait on the defined "protected reserved price" |
| O-3 | partly closed | paid_pct rounding is stated; `RND` is still a float round, with no tie in either world |
| O-4, O-8, O-10, O-11, O-14 | closed | see the sections above |
| O-5 | closed for `lower_reserved_price`; residual on the remake docstring object description (no ordering word) | |
| O-6 | wording closed; `gate` field still a DB field | |
| O-7 | closed in the set-off sentences; residual in P2's definition sentence | |
| O-9, O-12, O-13 | left as is, as the reworker states; no consequence | |
| new O-21 | P3 Icon same-day regular/clearance tie unspecified in the rule | no task world |
| new O-22 | P2 `last_request_status` unused binding | |
| new O-23 | P4 `pts_available_earned` listed under `points_relief`, read by the method | |

No new charter-global RED found.

### closing_checklist (round 2)

Written after the round-2 reveals (2026-10-05T04:47Z). The round-2 sections above were frozen first (`FREEZE_HASHES.txt`, "r2" lines).

- Per-task files carry `revision_2` sections. The round-1 text is untouched.
- Charter-global: CG-1 to CG-5 are **closed**, and no new charter-global RED was found. New observations O-21, O-22 and O-23 are minor.
- Coverage and scope: GT `charter_scope` confirms task 0 holds P1 and P2 and task 1 holds P3–P6. Disjoint and complete. The uuid8s are independent and unchanged.
- Trees:
  - Task 0: 1 prerequisite problem, 1 value_input edge, a user write.
  - Task 1: 3 prerequisite problems, 3 value_input edges, 2 user writes.
  - Acyclic, with no cross-task edge.
- Factors:
  - Every computation has 4–6 factors, at least 2 parameter and exactly 1 honest method.
  - Each task has a multi-source factor (P2 and P3 pass∧loyalty) and cross-difficulty factors.
  - Every factor bears weight: 29 of 29 substitutions move the scored value.
  - Every baseline is definite and ≠ gold.
- Scored solutions: all 9 scored arguments and both terminal states equal the blind round-2 derivation.
- **Not yet closed:** one proof-text defect per task, each SOURCE-FACTOR RED (proof assertion) with no effect on any scored value:
  - task 0, design_rationale [4]: "the two request rows", while the world has three;
  - task 1, design_rationale [6]: the 2025-09-23 ledger entry is "outside every window", contradicted by its available date and by the GT's own 62.35.
- Gate re-run on the final form: not performed by the auditor (Step 0). The coordinator's `r2/GATES.txt` reports all gates green on the audited hashes.

**Difficulty verdict (round 2): does NOT yet pass.** The four relationships hold for the policy, the tree and the scored solution in both tasks. Each task still carries one false or stale world assertion in its `design_rationale`.

## revision_3

### charter_global_frozen (round 3)

- Inputs (`r3/HASHES.txt`, all OK):
  - extended charter **f30c21474a451aede83fdb39275f0f3490172540bd64ab62f5d9b853a1a04b77** (round 2: b543d54a…, changed)
  - task_tools.py 87d549b4… (**unchanged** since round 2)
  - r3/0.view.json d9b50c01… and r3/1.view.json b566ed9f…, both **byte-identical to round 2** (`cmp`)
- `r3/GATES.txt`: all 7 gates OK, cache-diff INFO, traceability deferred. Base copy (lines 1–1076) is verbatim with the blueprint.
- Because the charter hash moved, every charter-global check was re-run over the whole charter (scripted below, plus a reading of every changed sentence). The `action_binding_and_uuids` section is carried forward by reference on the unchanged task_tools.py hash 87d549b4….
- contamination_disclosure: the auditor knows the round-2 GT of both tasks, and the round-3 worlds are identical to round 2. The round-3 task derivations are recomputations under the round-3 charter, not independent blind derivations.

### What changed (round 2 → round 3), found by diffing
- **P3** (`preorders_ext_price_protection`): the Icon/Atelier booking sentence, in both the `rule` and the second `overwrite.replaced_by`, gains ", a regular-price booking winning when both fall on the same day". Nothing else in P3, P4, P5 or P6 changed. That was checked by a textual diff of the full P3–P6 extraction against the round-2 extraction.
- **P2** (`preorders_ext_made_to_order_remake_deposit`): the unused binding `last_request_status` is removed from `compute`, `compute_basis` and `work_charge_setoff.bindings`. The P2 rule, params, ladders and prerequisite are unchanged.
- **P1**: unchanged.

### Re-run checks (round 3)
- For all six policies:
  - Every `policy_source` is verbatim in its own rule and absent from the depended rule, and `resolved_by` equals the depended `target_tool`.
  - Every `baseline.rule` sentence is in the `rule`.
  - Every `superseded_clause` is verbatim in its base rule and every `replaced_by` in the extended rule.
  - Every compute binding has a verbatim `compute_basis`.
  - No compute binding is unused, and no binding is shared between factors.
  - Result: **clean on all six**.
- Factor counts are unchanged from round 2 (P1 5P/1M, P2 4P/1M, P3 3P/1M, P4 4P/1M, P5 3P/1M, P6 4P/1M). Multi-source factors (P2, P3 pass∧loyalty) and cross-difficulty factors are unchanged.
- **O-21 closed.** P3's rule now resolves the same-day tie in favour of the regular booking. The compute already did this: `style_clr` is chosen only when `DAYS(style_reg_date, style_clr_date) > 0`, so on the same day the regular booking is taken. Rule and compute are now equivalent on the tie. The factor ladder's method text ("the most recent booking … at regular or clearance price") does not repeat the tie clause; the rule carries it (observation, no consequence).
- **O-22 closed** (binding removed; the unused-binding check is clean).
- **O-23** is kept as the reworker states: `pts_available_earned` is still listed under `points_relief`. It is structural and changes no score.
- Residuals O-5, O-6, O-7, O-9, O-12, O-13, O-15, O-16, O-18, O-19 and O-20 are unchanged, as recorded in round 2.
- No new charter-global defect. Round-2 charter-global conclusions (CG-1 to CG-5 closed) hold on the round-3 charter: the only edits are the P3 tie clause and the P2 binding removal, and neither touches a ladder, a baseline, a prerequisite sentence or a label.

### closing_checklist (round 3)

Written after the round-3 reveals (2026-10-05T05:07Z). The round-3 sections were frozen first (`FREEZE_HASHES.txt`, "r3" lines).

- Per-task files `0.md` and `1.md` correspond one-to-one with `tasks/0.json` and `tasks/1.json`, each carrying `revision_2` and `revision_3`. Older text is untouched.
- **Every comparison section of round 3 carries a PASS** on all four relationships, for both tasks.
- Round-2 REDs: task 0 R2-1 and task 1 R2-1 are **closed**. CG-1 to CG-5 stay closed; O-21 and O-22 are closed.
- No regression: the only charter edits are the P3 tie clause and the P2 unused-binding removal; the views and task_tools.py are unchanged. All scored values, factor sensitivities and tree closures are identical to round 2.
- Coverage and scope:
  - The extended policies are fully covered: task 0 holds P1 and P2; task 1 holds P3–P6. Disjoint and complete; the whole tree is inside each scope.
  - Task tools and GT are closed. The six uuid8s are independently generated and unchanged.
- Trees:
  - Task 0: 1 prerequisite problem, 1 value_input edge, user write P1.
  - Task 1: 3 prerequisite problems, 3 value_input edges, user writes P4 and P5.
  - The difficulty-wide graph is acyclic, with no cross-task edge.
- Factors:
  - Every computation has a definite baseline that differs from gold.
  - Every computation has 4–6 factors with at least 2 parameter and exactly 1 honest method. Per task there is a multi-source factor (P2 and P3, pass∧loyalty) and cross-difficulty factors (loyalty, orders, returns, pass), all seeded.
  - Every ladder has ≥3 distinct tiers stated in its rule.
  - Every factor bears weight: 29 of 29 substitutions move the scored value.
- Gates on the final form: `r3/GATES.txt` (coordinator run on charter f30c2147…, task_tools 87d549b4…) shows EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE OK, with traceability deferred to the KB stage. Under Step 0 the auditor cites this snapshot rather than re-running the gates.
- Remaining observations, non-blocking: O-5, O-6 and O-7 residuals; O-9; O-12; O-13; O-15; O-16 residual (P3, P5, P6); O-18; O-19; O-20; O-23 (kept on purpose); and new O-24 (stale round-1 gate quotes in task 0 design_rationale [9]).

**Difficulty verdict (round 3): PASS.** Policy self-consistency, problem tree, factors and unique solution hold for both tasks.
