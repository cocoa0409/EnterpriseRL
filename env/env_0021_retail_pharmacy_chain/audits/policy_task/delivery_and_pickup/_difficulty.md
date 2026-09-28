# Policy-task audit — delivery_and_pickup / charter-global

## charter_global_frozen

- Scenario: `env/env_0021_retail_pharmacy_chain`, difficulty `delivery_and_pickup`, M = 2.
- Freeze hashes (re-verified by the auditor against the brief):
  - `tasks/delivery_and_pickup/delivery.extended.yaml` sha256 `6ff45850e908362c0d680b8f07b3c3a8a7d7b50c222b33596b96bdc084e6d7b0`
  - `tasks/delivery_and_pickup/task_tools.py` sha256 `ea4b53ce3c26ddef6c3f01b9b9ce71c61302f28281bf58acebdd5faa16c0bfe7`
  - masked view `r1/task0.view.json` sha256 `46266186566a08345f1b34ac3f660fbb55c34f9b154825fd35c3cce48e32f7a1`; `r1/task1.view.json` sha256 `6cfc0af483aab77e510a84c6ca635e338a6884888b3ddbf18be426e8f08e02ef`
- Freeze time: 2026-09-24T17:18Z (revision 1). Auditor: independent policy-task auditor (Claude agent), not the instantiation agent.
- Fields read for this section: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/delivery.yaml` (and, for cross-category parameter lookups only, `products/rewards.yaml` and `products/rx.yaml` by targeted grep), the whole `delivery.extended.yaml`, the whole `task_tools.py`, and the DSL semantics of `skills/erl-task-instantiate/scripts/check_compute.py` (`build_env`, `MONTHS`, `DAYS`, `_within`, `LATEST`, `CFIELD`, `XCOUNT`) — the gate script, read for its primitive definitions only.
- Masked and not read when this section was written: every `tasks/*.json`, including `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`; no earlier audit exists for this difficulty. No search was ever run with `tasks/` in its match domain.
- Entry conditions (Step 0): the brief carries the gate snapshot (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all rc=0 with their last lines; check_traceability deferred until the KB is published) and the masked views with hashes. Input complete.
- Base copy: lines 1–1023 of `delivery.extended.yaml` diff against `blueprint/products/delivery.yaml` differs only by one trailing blank line — the base section is a verbatim copy.

### policy_conflict_scan

Structured policy surface: 8 base policies (`delivery_agg_multi_holding`, `delivery_plan_enrollment`, `delivery_evt_subscription_billing`, `delivery_evt_order_eligibility`, `delivery_evt_order_fees`, `delivery_evt_handover`, `delivery_evt_failed_attempts`, `delivery_evt_refunds`, `delivery_plan_cancellation`) and 5 extended policies:

| extended policy | subject | computes / target_tool | owner | prerequisite |
| --- | --- | --- | --- | --- |
| `delivery_ext_overdue_cycle_settlement` | delivery_subscription_charged, delivery_plan_recovered | amount_usd / `settle_overdue_pass_fee_c99b5804` | user | [] |
| `delivery_ext_express_order_fee` | delivery_order_fee_charged | amount_usd / `charge_order_fee_01b49350` | agent | settlement (value_input, state) |
| `delivery_ext_late_delivery_refund` | delivery_fee_refunded | amount_usd / `refund_late_delivery_fee_e6f66314` | agent | express fee (value_input, state) |
| `delivery_ext_dispatch_cancellation_refund` | delivery_fee_refunded | amount_usd / `refund_cancelled_order_fee_665693af` | agent | [] |
| `delivery_ext_annual_pass_switch_charge` | delivery_plan_details_updated, delivery_subscription_charged | amount_usd / `switch_delivery_pass_b46d5026` | user | cancellation refund (value_input, state) |

Overlap scan, subject by subject:

- **delivery_subscription_charged** is written by two extended policies (settlement, switch). Triggers are disjoint: settlement fires on a plan in `past_due` for the cycle that began on the plan's current cycle start date; the switch fires on an `active` Monthly/Senior pass being replaced by the Annual pass, for a cycle starting on the switch date. No world satisfies both triggers at once (status `past_due` vs `active`). Base inheritance: `one_charge_per_cycle` dedup (per `delivery_plan_id` + `cycle_start_date`) applies to both and is not weakened. Both extended policies supersede **the same** base clause of `delivery_evt_subscription_billing` — see finding D-O1.
- **delivery_fee_refunded** is written by two extended policies (late refund, cancellation refund). Triggers are disjoint: a late order is a completed delivery; a cancelled order has a `delivery_order_cancelled` row and by base `deliver_once` dedup can never be completed. Both inherit the base `refund_once` dedup (each fee refunded at most once, never more than was charged); the late refund's `MN(fee_booked, …)` and the cancellation refund's `MX(0, …)` keep within it.
- **delivery_order_fee_charged**: one extended policy (express fee). Base `delivery_evt_order_fees` still governs the same-day, mail, extended-radius and redelivery fees and has no target tool in this difficulty. Two base sentences that price the same express fee are not named in the express policy's `overwrite` — findings D-P1 and D-P2.
- **Time anchors**: settlement — failure date `past_due_since` as day 0, settlement date counted; express fee — "the day the fee is booked" (6-month rx window, plan age); late refund — "3 months up to today"; cancellation — "6 months up to today"; switch — "switch date" (1-month, 3-month, 6-month windows, plan age, unused days). All read `frozen_time` via `NOW`; the DSL's `within_months=n` keeps a row when `MONTHS(row_date, NOW)` is in `[0, n)`, which matches "the n months up to …".
- **Cross-category read boundaries**: coverage (`coverage_plans.variant_name/status`), rewards (`rewards_memberships.variant_name/status`), rx (`rx_fills.event_type/pickup_channel/event_date`). All three are read-only and are reachable through `find_coverage_plans`, `find_rewards_memberships`, `find_rx_fills`. No extended policy writes outside `delivery_plans` / `delivery_charges`.
- **Terminal states**: settlement leaves the plan `active` with `past_due_since` cleared (tool body) — consistent with base `delivery_plan_recovered`; the switch leaves the plan `active` on the new variant with a new cycle (tool body) — consistent with base `delivery_plan_details_updated` (a switch is an update of the same plan). No conflict.
- **Scope exclusivity and completeness** (derived from the charter's prerequisite graph alone, `charter_scope` still masked): the graph has exactly two connected components, {settlement → express fee → late refund} and {cancellation refund → switch}. With M = 2 and each task's scope spanning a whole tree, the only partition that is complete and pairwise disjoint is one component per task. Whether the two tasks actually claim them that way is compared per task after the reveal.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (and against every other base sentence that governs the same scored quantity).

**`delivery_ext_overdue_cycle_settlement`** (refs: `delivery_evt_subscription_billing`)
- "A plan activates on its trial_end_date…" — not touched.
- "a plan with a subscription_fee_usd above 0.00 is charged that fee for its first cycle on activation and for every later cycle on the cycle's first day" — **handled differently** (overdue cycle collects fee − credit + reinstatement); named in `overwrite` verbatim. Declared.
- "each cycle lasting billing_cycle_months calendar months…" — followed (cycle_days reads the plan's own cycle dates).
- "Each cycle is charged once." — followed (inherited dedup).
- "A charge that cannot be collected puts the plan past due; while past due, where benefits_suspended_when_past_due is true, orders are priced as Kestrel Pay-Per-Delivery orders." — second half is superseded by the express policy (declared there); the settlement does not touch it.
- "A past-due plan whose fee is collected no later than the date the charge failed plus the past-due grace days … returns to active; otherwise it lapses on the next day." — followed (the settlement is the collection; grace inherited).
- "Plans without a subscription never go past due." — followed.
- Base `formula: amount_usd: subscription_fee_usd` is the structured twin of the superseded sentence; covered by the same declaration.

**`delivery_ext_express_order_fee`** (refs: `delivery_evt_order_fees`, `delivery_evt_subscription_billing`)
- order_fees "Order fees are set by the plan in force on the day the order is placed." — followed.
- "A same_day order is charged same_day_fee_usd…" — not the express quantity; untouched.
- "An express_1hr order is charged express_1hr_fee_usd, waived while delivery_msr_free_express_month is below free_express_per_month." — handled differently (speed charge less discount plus supplements); named. Declared. The allowance itself is kept by the extended rule ("counted as the Delivery & Pickup Services charter counts it").
- "A mail_standard … A courier order whose distance_miles is above delivery_radius_miles is also charged extended_radius_fee_usd. A redelivery is charged redelivery_fee_usd." — other fee types; untouched.
- "Each fee type is charged at most once per order, and a waived fee is not charged at all rather than charged and refunded." — followed.
- "Where the plan is past due and benefits_suspended_when_past_due is true, the Kestrel Pay-Per-Delivery fees apply instead." — handled differently; named. Declared.
- "A patient who holds a Kestrel Care Rewards membership in active status whose level has free_rx_delivery true is charged no same_day or express fee on an order that carries prescriptions, whatever the delivery plan; distance and redelivery fees still apply." — **handled differently and not named** → finding D-P2.
- subscription_billing "while past due, where benefits_suspended_when_past_due is true, orders are priced as Kestrel Pay-Per-Delivery orders" — handled differently; named. Declared.
- Outside the refs, `delivery_evt_order_eligibility`: "An order is placed only on a plan in enrolled, active or past_due status; a past-due plan's orders are priced as Kestrel Pay-Per-Delivery orders under delivery_evt_subscription_billing and a cancelled plan takes no orders." — the pricing clause governs the same express fee and is **handled differently and not named** → finding D-P1. (The clause is also the text of the base eligibility `order_on_open_plan.condition`.)

**`delivery_ext_late_delivery_refund`** (refs: `delivery_evt_refunds`)
- "Each fee is refunded at most once and never for more than was charged." — followed (MN with fee_booked; inherited dedup).
- "A late order has its order fees refunded at late_delivery_refund_pct percent, as refund_reason late_delivery, where late_credit_applies is true and delivery_msr_late_refunds_cycle is below late_credit_max_per_cycle; a late order on a plan that charged it no fee earns nothing." — handled differently (shares, rewards adjustment; the per-cycle cap is dropped and the plan's late_credit_max_per_cycle reappears only as a tier boundary of the 3-month frequency share); the whole sentence is named. Declared. The dropped per-cycle cap is inside the named sentence, so it is a declared drop, not a dropped branch.
- The remaining sentences (cancellation, missing orders, subscription refunds) are other quantities; untouched.
- `delivery_evt_handover` definition of lateness ("more than late_threshold_minutes after promised_window_end on the scheduled date, or when it arrives on a later date") — restated identically in the extended rule. Followed.

**`delivery_ext_dispatch_cancellation_refund`** (refs: `delivery_evt_refunds`)
- "An order cancelled before dispatch has its order fees refunded in full where order_cancel_refund_before_dispatch is true" — handled differently (fee less retained charges); named. Declared.
- "an order already dispatched cannot be cancelled" — followed.
- "Each fee is refunded at most once and never for more than was charged." — followed (MX(0,…) ≤ fee).

**`delivery_ext_annual_pass_switch_charge`** (refs: `delivery_plan_enrollment`, `delivery_evt_subscription_billing`)
- enrollment "A plan switch is an update of the same plan, allowed only where the current plan's plan_switch_allowed is true and the plan is in enrolled or active status" — followed (extended narrows its computation to `active` Monthly/Senior passes; Monthly/Senior have plan_switch_allowed true).
- "a switch to a subscription plan starts that plan's billing on the switch date with no new trial when the patient has had a trial before" — followed ("pays the switch charge for the annual pass's opening cycle, which starts on the switch date"; the no-trial-before case "falls outside this computation").
- "a switch from the annual pass refunds under delivery_evt_refunds as a cancellation would" — not this direction; untouched.
- subscription_billing "a plan with a subscription_fee_usd above 0.00 is charged that fee for its first cycle on activation and for every later cycle on the cycle's first day" — handled differently (switch price less six credits); named. Declared. Same clause as the settlement's — finding D-O1.
- base `delivery_plan_cancellation` / `delivery_evt_refunds` subscription-refund sentences: the switch is not a cancellation and the Monthly pass has `full_refund_window_days` 0 and `prorated_refund_after_window` false; the extended unused-cycle credit therefore overlaps no base refund of the Monthly fee. No conflict.

Disguised forms: no anonymous intermediate factor, no 0/1 multiplier on a base-fixed amount, and no author text calling a base output a "wrong value" were found. One dropped-branch shape exists (D-O1).

### rule_compute_equivalence

Machine sweep (normalised whitespace): every `compute_basis` quotation of all five extended policies is a verbatim substring of its own `rule`; every compute binding has a `compute_basis` entry; every `baseline.rule` is a verbatim sentence of its `rule`. The manual two-way sweep:

**Settlement** — cycle_fee `P('subscription_fee_usd')` ↔ "collecting the plan's subscription fee for that cycle"; days_past_due `DAYS(past_due_since, NOW)` ↔ "failure date not counted and the settlement date counted" (DAYS counts exactly that); cycle_days `DAYS(start,end)+1` ↔ "its start date and end date both counted"; prior_cycle_charges `COUNT(subscription charges)` ↔ "how many subscription fees the plan has already had collected"; the three credit tiers, the whole-week tier `int(days/7)` ↔ "the number of whole weeks in the days past due"; reinstatement 4.00/2.00/0 ↔ rule; cap by active coverage class ↔ rule; relief by active rewards level AND `COUNT(delivery_completed, within_months=12)` ↔ "the deliveries completed on the plan in the 12 months up to the settlement date"; `MN` ↔ "first reduced to its cap where the cap is lower"; `RND(capped*(100−pct)/100)` ↔ "relief percentage then acts on that capped fee … rounded to the cent"; `RND(MX(0, …))` ↔ "never below zero and rounded to the cent". Equivalent. One reading note: `CFIELD('coverage','variant_name',status='active')` returns the first active coverage row; the rule speaks of "the patient's prescription insurance record in active status" in the singular — a patient with a primary and a secondary active plan has no unique reading (observation D-X3; neither task world has two).

**Express fee** — speed charge, discount tiers (both counts over `rx_fills` in the 6 months to NOW), `standing_ok`, four supplement ladders, the plan-age share with floor/ceil, final `RND` — each has its quotation and no compute branch lacks a rule sentence. Two non-equivalences:
- the order the fee is for: the rule says "worked out when it is booked, from that express order's own record", compute reads `LATEST('delivery_orders', …, event_type='delivery_order_placed', speed='express_1hr')` — the plan's latest-placed express order, whatever order the fee is booked on. Equal only when the charged order is the latest express order (finding D-P3).
- the cycle whose fee must stand collected: the rule says "the billing cycle in which the order was placed", compute counts subscription charges with `cycle_start_date=F('cycle_start_date')` (the plan's current cycle). Because a past-due plan lapses after its grace (7 or 14 days, shorter than any cycle) and the charge fails on the cycle's first day, an order placed while past due is always in the current cycle — no situation separates the two; observation D-X1.
- `free_express_per_month` allowance and `late_credit`-style gates are treated as preconditions of whether to write at all, not as compute branches; the rule says so ("an order it covers is not charged at all"). Consistent.

**Late refund** — late_order `LATEST(delivery_completed).source_order_id` ↔ "the one whose delivery was most recently completed on the plan"; fault tiers map one-to-one onto the `failure_reason` enum (no_one_available_for_signature / id_not_presented → 50; building_access / address_not_found → 75; weather_or_road_closure → 90; none → late_delivery_refund_pct); frequency `COUNT(refund_reason='late_delivery', within_months=3)` with boundaries 6 and `P('late_credit_max_per_cycle')`; handover by speed AND includes_controlled of the late order's placed row; `refund_worked` sequential without intermediate rounding ↔ "applied one after another to the result of the previous step"; rewards boost with ceiling ↔ "rounded up to the cent"; `RND(MN(fee, adj))` ↔ "then limited to the fee booked on the order". Non-equivalences:
- `fee_booked = SUM(all order fees on the late order)` while the rule says "a fee charged on a late order is refunded as a late-delivery refund, one refund for each fee" and "the fee refunded is the amount booked on that order" — for an order carrying two fees (express + extended-radius) the rule gives two refunds each on its own fee, compute one refund on their sum; the cap `MN(fee_booked, …)` also then caps against the sum (finding D-P3).
- `attempt_reason = LATEST(failed attempt).failure_reason`: the rule reads "the reason recorded for a failed delivery attempt on that order" and says nothing about an order with two failed attempts of different reasons (observation D-X2).

**Cancellation refund** — cancelled_order `LATEST(delivery_order_cancelled)` ↔ "the one most recently cancelled on the plan"; packing by cancel_reason AND `DAYS(placed, cancelled)`; repeat `COUNT(patient_request cancellations, within_months=6)` "the cancelled order included"; the rule's "repeat_cancel_low_count keeps repeat_cancel_low_usd" is an equality while compute uses `>=`, equivalent because the higher tier (≥3) is tested first and low_count = 2; restock by value; rewards keep 50 % floor / 75 % ceil / whole; `RND(MX(0, fee − kept))`. Non-equivalence: `fee_charged = SUM(all order fees on the cancelled order)` vs "one refund for each fee … the fee refunded is the amount charged on that order" — same shape as the late refund (finding D-P3).

**Switch** — price, current fee, plan age, unused days `DAYS(NOW, cycle_end)` ↔ "switch date not counted and the end date counted", cycle_days, three credit tiers, recent-fees credit, share ladder, Medicare, maintenance, missed, spend (cancelled orders included via `delivery_order_placed` rows) — all quoted. Non-equivalence: `net_recent_fees = MX(0, fees_1m − refunds_1m)` — the floor at zero is stated nowhere in the rule; the rule says "a share of the order fees charged on the plan in the month up to the switch date less the refunds booked on the plan in that month, rounded to the cent", and the `compute_basis` quotation offered for `net_recent_fees` is the prerequisite sentence, which describes an ordering and no arithmetic. Compute invents a floor (finding D-P4).

### action_binding_and_uuids

- `(target_tool, computes)`: (`settle_overdue_pass_fee_c99b5804`, amount_usd), (`charge_order_fee_01b49350`, amount_usd), (`refund_late_delivery_fee_e6f66314`, amount_usd), (`refund_cancelled_order_fee_665693af`, amount_usd), (`switch_delivery_pass_b46d5026`, amount_usd) — each claimed by exactly one policy.
- Owners: settle and switch are `owner="user"` ("The patient pays, in person with their own card"); charge and both refunds are `owner="agent"`. The persona-facing wording matches the policies ("the patient settles the overdue cycle", "may switch … and pays the switch charge").
- Tool bodies: every body is `find` plan → `create` one `delivery_charges` row → `update` the plan; none reads a charge ledger, an order ledger, a status or an amount to accept or refuse; none returns an error or a hint. The tool layer judges no eligibility, prerequisite or amount.
- Docstrings: no docstring names another tool, states its position in a sequence, or carries "before / first / prior to". Each says "Afterwards the … appears / sees …", describing the tool's own effect, not an order among actions (observation D-X4). `refund_late_delivery_fee_e6f66314.source_charge_id` reads "as shown by the delivery fee lookup or returned when that fee was booked" — it tells the reader that the fee being refunded may have been booked in the same conversation, a weak pointer at the prerequisite chain; it names no tool and states no order (observation D-X5).
- uuid8s: `c99b5804`, `01b49350`, `e6f66314`, `665693af`, `b46d5026` — pairwise distinct, no shared prefix or suffix, no arithmetic progression, no adjacent values; consistent with independent generation.

### prerequisite_graph

- `prerequisite` filled on all five extended policies (`[]` on settlement and cancellation refund).
- Edges: express fee → settlement; late refund → express fee; switch → cancellation refund. Every `problem` is an extended policy id of this file, none a base policy, none self. Acyclic (two chains, depths 2 and 1).
- `policy_source` verbatim in the blocked policy's own `rule`: all three (machine check, whitespace-normalised).
- `form: state` on all three; no `fallback_reason` present — consistent.
- `gate` bindings exist in the blocked compute: `cycle_fee_collected` (express), `fee_booked` (late refund), `net_recent_fees` (switch). `kind: value_input` on all three: `cycle_fee_collected` → `standing_ok` → `discount_applied` → `speed_charge`; `fee_booked` is the base every share acts on; `net_recent_fees` is the base of the recent-fees credit. All genuine value inputs.
- `resolved_by` equals the depended-on policy's `target_tool` in all three cases; each tool's body writes exactly the row that makes the gate change (a `delivery_subscription_charged` row with the named `cycle_start_date`; a `delivery_order_fee_charged` row with the named `source_order_id`; a `delivery_fee_refunded` row dated today, which enters `refunds_1m`).
- `condition` vs sentence: express — "a collected subscription fee entry whose cycle start date is the plan's current cycle start date, the cycle in which the express order was placed" equates the placement cycle with the current cycle (see D-X1; not a strengthening in any reachable world); late refund — "an order fee entry whose order reference is the late order, with the amount the fee rules set for it" (the sentence says "the late order's fees stand booked"; the added "with the amount the fee rules set" is not checkable by a state and restates the depended-on policy's job, not a strengthening of the gate); switch — "For every order of the plan with a cancellation entry, each order fee entry on that order has a refund entry on the plan's fee ledger naming it" — same strength and scope as the sentence (open set "every order … cancelled", stated open).
- No authoring-viewpoint phrasing ("in this task", "at the opening") in any prerequisite field.

### prerequisite_sentences

Four-point test per edge:

1. **express fee ← settlement.** "The express fee of an order placed while its plan is past due is not fixed until the subscription fee of the billing cycle in which the order was placed stands collected on the plan's ledger." Connective "not … until" ✓. Waited-on state is record-visible in ledger words (a subscription fee for a billing cycle standing collected — `find_delivery_charges` returns "subscription fees per billing cycle") with no actor, tool or action ✓. No tool, policy id, snake_case token or row id ✓. Scope matches the condition ✓. Writes of this difficulty that can bring the state about: only a `delivery_subscription_charged` row for that cycle. `switch_delivery_pass_b46d5026` also books a subscription row, but for a cycle starting on the switch date of an `active` Monthly/Senior pass, never the cycle of an order placed while past due; `settle_overdue_pass_fee_c99b5804` is the only one. Derivation: sentence → the state is a collected subscription fee for the placement cycle → the policy whose own rule books "the payment … as that cycle's subscription fee" is the overdue-cycle settlement → its write resolves the edge. Single reading. The rule also carries "the discount applies only where the plan has no subscription or the subscription fee of the billing cycle in which the order was placed stands collected" and "Once it stands collected, the order is priced at the plan's own express fee like any order of a plan in good standing" — these state how the value depends on the state (the value_input mechanism), not a second ordering of the same dependency; recorded as observation D-X6, not a red light.
2. **late refund ← express fee.** "A late-delivery refund is worked out only after the late order's fees stand booked on the plan's charge ledger; the fee refunded is the amount booked on that order." Connective "only after" ✓; state "the late order's fees stand booked on the plan's charge ledger" ✓; no tool/id ✓; scope ✓. Writers of an order fee row in this difficulty: only `charge_order_fee_01b49350` (base `delivery_evt_order_fees` has no target tool here). Derivation: sentence → a fee row on the late order → the policy whose rule books an express order's fee → `delivery_ext_express_order_fee` (the late order being an express order). Single reading.
3. **switch ← cancellation refund.** "The switch charge for the Kestrel Delivery Pass Annual is fixed only after every order of the plan cancelled before dispatch carries a refund entry for each fee charged on it." Connective "only after" ✓; state in ledger words ✓; no tool/id ✓; scope open and stated open ✓. Writers of a refund row: `refund_cancelled_order_fee_665693af` and `refund_late_delivery_fee_e6f66314` (both create `delivery_fee_refunded`); by policy, a late-delivery refund is only for a completed (hence never cancelled) order, so only the cancellation-refund policy's write refunds a fee on a cancelled order. Single reading.

- The depended-on rules do not restate any of the three sentences (settlement rule never mentions express orders; express rule never mentions late refunds; cancellation-refund rule never mentions switching) ✓.
- Undeclared cross-problem orders: none found. Base rules carry no cross-problem ordering sentence that any task's tree could rest on (the base `delivery_plan_enrollment` "a switch from the annual pass refunds under delivery_evt_refunds as a cancellation would" states a treatment, not an order).

### factor_ladders

Structure only; whether each factor bears weight is judged per task under `factor_weight`. "Multi-source" is read as the skill words it: every tier beyond the fall-through combines two or more conditions over **distinct records**. Every ladder below has three or more tiers, pairwise disjoint as stated, every tier (condition and value or method) stated in its policy's `rule` and implemented as a branch of the `decides` binding; no tier lives only in `compute`; every `decides` is an input, never `result`; binding sets within each policy are pairwise disjoint.

| policy | factor | effect | tiers (fall-through last) | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- |
| settlement | suspended_day_credit | method | ≥3 collected fees: pro-rata days / 1–2: whole weeks only / none: no credit | no | — |
| settlement | reinstatement_fee | parameter | ≥8 days: 4.00 / 4–7: 2.00 / <4: 0 | no | — |
| settlement | reinstatement_cap | parameter | Medicaid MC: 0.50 / Medicare D Std, D Enh, MA-PD: 1.50 / other or none: uncapped | no (one coverage record) | coverage |
| settlement | reinstatement_relief | parameter | Platinum ∧ ≥8 deliveries 12m: 100 % / Gold ∧ ≥8: 50 % / else 0 | **yes** (rewards membership + delivery ledger) | — (rewards is claimed by no difficulty) |
| express fee | maintenance_delivery_discount | parameter | ≥6 HD pickups ∧ ≥6 refills: 20 % / ≥3 ∧ ≥3: 10 % / else 0 | **yes** (pickup rows + refill rows) | rx |
| express fee | high_value_supplement | parameter | ≥250: 2.00 / 100–<250: 1.00 / else 0 | no | — |
| express fee | long_distance_express_supplement | parameter | >12 mi: 2.50 / >radius–12: 1.25 / else 0 | no | — |
| express fee | id_check_handling_supplement | parameter | controlled ∧ store items: 2.00 / controlled only: 1.00 / else 0 | two fields of one order row — multi-source under the gate's `_bool_sources` reading, not under "distinct records" | — |
| express fee | evening_express_supplement | parameter | window end ≥20:00: 1.75 / ≥18:00: 0.90 / else 0 | no | — |
| express fee | plan_age_supplement_adjustment | method | ≥36 months: keep 50 % rounded down / 12–35: keep 75 % rounded up / else whole | no | — |
| late refund | fault_share | parameter | signature/ID: 50 / access/address: 75 / weather: 90 / none: late_delivery_refund_pct | no | — |
| late refund | late_refund_frequency_share | parameter | ≥6 in 3m: 50 / ≥late_credit_max_per_cycle: 80 / else 100 | no | — |
| late refund | controlled_handover_share | parameter | express ∧ controlled: 90 / same-day ∧ controlled: 95 / else 100 | one order row (as above) | — |
| late refund | rewards_refund_adjustment | method | Platinum: ×200 % round up / Gold: ×150 % round up / else as worked | no | — |
| cancellation | packing_charge | parameter | patient ∧ later day: 2.00 / patient ∧ same day: 1.00 / else 0 | **yes** (cancellation row reason + placed/cancelled dates) | — |
| cancellation | repeat_cancellation_charge | parameter | ≥3 in 6m: 1.50 / exactly 2: 0.75 / else 0 | no | — |
| cancellation | restocking_charge | parameter | ≥150: 1.00 / 75–<150: 0.50 / else 0 | no | — |
| cancellation | rewards_retained_adjustment | method | Platinum: keep 50 % rounded down / Gold: keep 75 % rounded up / else whole | no | — |
| switch | unused_cycle_credit | method | ≥18 months: pro-rata unused days / 6–17: whole unused weeks / else none | no | — |
| switch | recent_fees_credit_share | parameter | Gold/Platinum ∧ ≥6 deliveries 3m: 100 % / Member/Silver ∧ ≥6: 75 % / else 50 % | **yes** (rewards membership + delivery ledger) | — |
| switch | medicare_member_credit | parameter | MA-PD: 3.00 / Part D Std/Enh: 1.50 / else 0 | no | coverage |
| switch | maintenance_delivery_credit | parameter | ≥6 refills ∧ ≥3 HD pickups: 4.00 / ≥3 ∧ ≥1: 2.00 / else 0 | **yes** | rx |
| switch | missed_delivery_credit | parameter | ≥2 failed attempts 3m: 2.00 / 1: 1.00 / none: 0 | no | — |
| switch | delivery_spend_credit | parameter | ≥600: 1.50 / 300–<600: 0.75 / else 0 | no | — |

Counts per policy (parameter / method; bounds 4–6 total, ≥2 parameter, ≥1 method): settlement 4 (3/1) ✓; express fee 6 (5/1) ✓; late refund 4 (3/1) ✓; cancellation refund 4 (3/1) ✓; switch 6 (5/1) ✓. Per connected component (the only possible task scopes, see policy_conflict_scan): {settlement, express, late} has multi-source (relief, maintenance discount) and cross-difficulty (coverage via cap, rx via discount) ✓; {cancellation, switch} has multi-source (packing, recent share, maintenance credit) and cross-difficulty (coverage via Medicare credit, rx via maintenance credit) ✓.

Distinct outcomes: no two tiers of any ladder select the same value; for the method ladders the tiers differ in algorithm (pro-rata days vs whole weeks vs none; share with floor vs share with ceiling vs whole) except `rewards_refund_adjustment`, whose Platinum and Gold tiers are the same algorithm (multiply, round up) with a different percentage — see observation D-X7.

Business reality of conditions and outcomes: every condition divides the customers who reach its write (none restates the policy's own scope); all outcomes are fees, credits, shares or roundings a pharmacy delivery service could publish. Nothing found that no such business would publish.

Baseline coherence (the policy's `baseline.rule` against the fall-through of every factor):
- settlement: `baseline.rule` "An overdue cycle is settled by collecting the plan's subscription fee for that cycle, rounded to the cent." — all factor fall-throughs (no credit, no reinstatement fee, uncapped, no relief) reduce the compute to exactly that ✓.
- express fee: "charged the plan's express fee, rounded to the cent" — all fall-throughs (no discount, no supplements, whole sum of zero) reduce to `express_1hr_fee_usd` ✓.
- late refund: "refunded at late_delivery_refund_pct percent of the fee booked on the order" — fall-throughs (fault = late_delivery_refund_pct, 100, 100, as worked) reduce to exactly that ✓.
- cancellation refund: "refunded in full" — fall-throughs (0, 0, 0, whole of 0) reduce to the fee ✓.
- **switch: ✗.** `baseline.rule` "The switch into the Kestrel Delivery Pass Annual is charged the annual switch price, annual_switch_price_usd, rounded to the cent." states no recent-fees credit at all, so a reader of the baseline alone gives no credit for that input; but the fall-through tier of `recent_fees_credit_share` is `standard_credit_pct` = 50 %, so substituting every factor's baseline leaves a recent-fees credit of 50 % of the net recent fees. The fall-through of that factor is not the baseline, and the policy has two fall-back numbers (finding D-F1; demonstrated on task 1's world in `1.md`).

### findings

Each finding names the tasks whose files carry the demonstration. Task membership below is by the charter's graph components (settlement/express/late ↔ one tree, cancellation/switch ↔ the other); which task holds which tree is confirmed only after the reveal.

- **D-P1 — SOURCE-POLICY RED (undeclared override).** Symptom: a base sentence that prices the express fee of a past-due plan's order is not named in any `overwrite`, while the extended express-fee rule prices that same order differently. Evidence: base `delivery_evt_order_eligibility.rule` (and `eligibility.order_on_open_plan.condition`): "An order is placed only on a plan in enrolled, active or past_due status; a past-due plan's orders are priced as Kestrel Pay-Per-Delivery orders under delivery_evt_subscription_billing and a cancelled plan takes no orders." Extended `delivery_ext_express_order_fee.rule`: "The express fee of an order placed while its plan is past due is not fixed until the subscription fee of the billing cycle in which the order was placed stands collected on the plan's ledger. Once it stands collected, the order is priced at the plan's own express fee like any order of a plan in good standing; an order of a plan that has lapsed is priced as a Kestrel Pay-Per-Delivery order and falls outside this computation." `delivery_ext_express_order_fee.overwrite` names two sentences of `delivery_evt_order_fees` and one of `delivery_evt_subscription_billing`, none of `delivery_evt_order_eligibility`. Same situation (an express order placed while the plan was past due, fee booked after the overdue cycle is settled): base → Pay-Per-Delivery express price (`express_1hr_fee_usd` 12.99 of Kestrel Pay-Per-Delivery, and Pay-Per-Delivery's distance fee regime); extended → the plan's own `express_1hr_fee_usd`. Root cause: the override was declared against the two sentences that state the PPD pricing rule but not against its third statement in the order-eligibility policy, whose "under delivery_evt_subscription_billing" pointer now points at a superseded clause. Affected: `delivery.extended.yaml` → `delivery_ext_express_order_fee.overwrite`; base `delivery_evt_order_eligibility.rule`. Bears on the settlement→express→late tree (task holding it demonstrates the value).
- **D-P2 — SOURCE-POLICY RED, latent (undeclared override).** Base `delivery_evt_order_fees.rule`: "A patient who holds a Kestrel Care Rewards membership in active status whose level has free_rx_delivery true is charged no same_day or express fee on an order that carries prescriptions, whatever the delivery plan; distance and redelivery fees still apply." Extended: "An express order that the free express allowance does not cover is charged the plan's express fee" with a compute that has no rewards branch. `products/rewards.yaml` sets `free_rx_delivery: true` for Kestrel Care Rewards Plus Monthly and Plus Annual. For an active Plus member's prescription express order outside the allowance: base → no express fee; extended → speed charge plus supplements. Not named in `overwrite`. Consequence on a task only where the patient is an active Plus member; checked per task.
- **D-P3 — SOURCE-POLICY RED, latent (rule ↔ compute object non-equivalence).** (a) Express fee: rule "from that express order's own record" vs compute `LATEST(... delivery_order_placed, speed='express_1hr')` — the latest-placed express order on the plan, not the order being charged. (b) Late refund and cancellation refund: rule "one refund for each fee … the fee refunded is the amount booked/charged on that order" vs compute `SUM('delivery_charges','amount_usd', event_type='delivery_order_fee_charged', source_order_id=…)` — one amount over all fees of the order. Two readings differ on any order that is not the latest express order (a) or that carries more than one fee (b). Consequence checked per task.
- **D-P4 — SOURCE-POLICY RED, latent (compute invents a floor).** Switch: `net_recent_fees: "MX(0, fees_1m - refunds_1m)"`; no sentence of the rule floors "the order fees charged on the plan in the month up to the switch date less the refunds booked on the plan in that month" at zero, and the `compute_basis` quotation given for this binding is the prerequisite sentence, not an arithmetic sentence. Where refunds booked in the month exceed the order fees charged in it (a refund of a fee charged the month before), rule → a negative recent-fees credit that raises the charge; compute → 0. Consequence checked on the task holding the switch.
- **D-F1 — SOURCE-FACTOR RED structure (incoherent baseline).** Switch: `recent_fees_credit_share.baseline` is `K('standard_credit_pct')` (50 %), the ladder's fall-through; the policy's `baseline.rule` states no recent-fees credit at all. The factor's fall-through is not the baseline, and "the fall-back number" is two numbers (baseline.rule alone vs all factor baselines substituted). Demonstrated on the task holding the switch.
- **D-O1 — observation (dropped branch shape).** The base clause "a plan with a subscription_fee_usd above 0.00 is charged that fee for its first cycle on activation and for every later cycle on the cycle's first day" is superseded by two extended policies, each with a replacement scoped to its own situation (overdue-cycle settlement; switch charge). Read literally, the ordinary activation and renewal charge is left without a statement after the merge. No task writes an ordinary activation or renewal, so no consequence can be demonstrated.
- **D-X1 — observation.** Express-fee gate: rule "billing cycle in which the order was placed" vs compute/condition "the plan's current cycle"; inseparable in every reachable world (grace shorter than any cycle, charge fails on the cycle's first day).
- **D-X2 — observation.** Late refund: an order with two failed attempts of different reasons has no rule reading; compute takes the latest.
- **D-X3 — observation.** `CFIELD('coverage', 'variant_name', status='active')` returns the first active coverage row; a patient with primary and secondary active plans has no unique reading under "the patient's prescription insurance record in active status" (settlement cap, switch Medicare credit).
- **D-X4 — observation.** Every task-tool docstring says "Afterwards …" of its own effect; not a position in a sequence of actions.
- **D-X5 — observation.** `refund_late_delivery_fee_e6f66314` docstring, `source_charge_id`: "as shown by the delivery fee lookup or returned when that fee was booked" — hints that the fee may be booked in the same conversation.
- **D-X6 — observation.** The express-fee rule carries, besides its prerequisite sentence, two sentences that restate the same state ("the discount applies only where … stands collected"; "Once it stands collected, the order is priced at the plan's own express fee"). They carry the value mechanism of the value_input edge, not a second ordering; not a red light.
- **D-X7 — observation (method label).** `rewards_refund_adjustment` (late refund): Platinum and Gold tiers select the same algorithm (multiply, round up) with a different percentage; only the fall-through differs in algorithm. The framework's own factor reference counts "a multiplier on an intermediate or on the result" as a method, so the label is held honest here; the same holds, more clearly, for the floor/ceiling share adjustments of `plan_age_supplement_adjustment` and `rewards_retained_adjustment`.
- **D-X8 — observation.** Rounding: `RND` is Python `round` on binary floats; the extended rules say "rounded to the cent" without a mode. No computed value in either task world sits on a half-cent boundary before rounding (checked per task), so no consequence.

## closing_checklist

Written after both reveals (2026-09-24T17:23Z); everything above this heading was written before any GT was opened and is left as frozen.

**The difficulty does not close.** Not every task passes all four relationships:

| task | policy self-consistency | problem tree | factors bear weight | unique solution | file |
| --- | --- | --- | --- | --- | --- |
| 0 | SOURCE-POLICY RED (T0-1 ← D-P1) | PASS | SOURCE-FACTOR RED (T0-2, T0-3: no near-miss in settlement and late refund) | no independent defect (second write set recorded under T0-1) | `0.md` |
| 1 | PASS | PASS | SOURCE-FACTOR RED (T1-1 ← D-F1) | PASS | `1.md` |

Checklist items, as they stand:
- Per-task files `0.md`, `1.md` correspond one-to-one with `tasks/0.json`, `tasks/1.json`; `_difficulty.md` sits alongside; revision 1, no earlier revision exists. Comparison sections carry the verdicts above, not all PASS.
- Coverage and scope: `charter_scope` of task 0 = {overdue_cycle_settlement, express_order_fee, late_delivery_refund}, of task 1 = {dispatch_cancellation_refund, annual_pass_switch_charge} — pairwise disjoint and jointly complete over the five extended policies, each scope a whole tree, as the graph predicted. Task tools and GT are closed (every write in GT uses a tool of its own scope). uuid8s independent (see action_binding_and_uuids).
- Trees: task 0 has 2 prerequisite problems with 2 value_input edges; task 1 has 1 with 1; each has one `owner=user` write (settlement; switch); the difficulty-wide graph is acyclic and no cross-task edge exists.
- Factors: counts within bounds on every computation; every factor bears weight on its task's world; baselines honest except the switch (D-F1); the settlement and late-refund computations of task 0 have no near-miss record.
- Charter-level SOURCE-POLICY findings: D-P1 (demonstrated on task 0), D-P2, D-P3, D-P4 (latent — no consequence on either task world).
- Gate re-run on the final form: not performed — the difficulty does not close, and the brief's gate snapshot (all rc=0) is the latest on record. The machine gates being green does not contradict these findings: none of them tests base sentences outside `base_policy_refs`, near-miss presence, or the coherence of `baseline.rule` with the factors' fall-through tiers.

## revision_2

### charter_global_frozen (revision 2)

- Inputs re-verified by the auditor: `delivery.extended.yaml` sha256 `6922750332ae55931303931eaa04ea284670a420c2c5eade323818ecdd6007d4` (round 1: `6ff45850…d6b0` — **changed**); `task_tools.py` sha256 `fe49c300fc26fe08d51fe2e29b6adbf29c2036b85859122b2ef7aaf1eef5a19b` (round 1: `ea4b53ce…fbe7` — **changed**); views `r2/task0.view.json` `a428e764…8faa` (changed), `r2/task1.view.json` `6cfc0af4…02ef` (byte-identical to `r1/task1.view.json`). Both shared inputs moved, so every charter-global section is re-derived below in full rather than carried forward.
- Gate snapshot after rework (from the brief): check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all rc=0. Input complete.
- Freeze time 2026-09-24T18:05Z; written before either task's round-2 GT was opened. Same read set as round 1 (charter, tool module, blueprint, share tools, gate DSL primitives); `tasks/*.json` masked.
- contamination_disclosure (revision-level): the auditor opened the **round-1** `tasks/0.json` and `tasks/1.json` after the round-1 freeze. Round-2 derivations are therefore not blind to the round-1 GT values; they are re-derived from the round-2 charter and views by recomputation, and every place where a round-2 figure coincides with a round-1 GT figure is stated as such. The round-1 text above is left untouched.
- Base copy: lines 1–1023 still differ from `blueprint/products/delivery.yaml` only by one trailing blank line.

### re-derived charter-global checks (revision 2)

Machine sweep on the new charter: every `compute_basis` quotation is a verbatim substring of its rule; no compute binding lacks a basis; every `baseline.rule` is a verbatim rule sentence; every prerequisite `policy_source` is verbatim in its blocked rule; every `overwrite.superseded_clause` is verbatim in the named base rule (including the new `delivery_evt_order_eligibility` entry).

What changed and what it does, policy by policy:

- **Settlement.** New first rule sentence: "A cycle that is not overdue is charged the plan's subscription fee, on activation for the plan's first cycle and on the cycle's first day for every later cycle, exactly as the Delivery & Pickup Services charter provides." Cap now read from the **primary** active coverage record (`CFIELD(..., status='active', coverage_order='primary')`, rule and ladder say "primary prescription insurance record in active status"; the fall-through adds "a terminated or removed record does not count"). Compute otherwise unchanged.
- **Express fee.** `base_policy_refs` now include `delivery_evt_order_eligibility`, and `overwrite` names its clause "a past-due plan's orders are priced as Kestrel Pay-Per-Delivery orders under delivery_evt_subscription_billing", replaced by "Once it stands collected, the order is priced at the plan's own express fee …". The rule now carries the rewards waiver as an inherited no-charge case: "a patient who holds a Kestrel Care Rewards membership in active status whose level carries free prescription delivery is charged no express fee on an order that carries prescriptions, as that charter provides, and such an order is not charged at all." The order is now fixed by the rule: "The express order concerned is the one most recently placed on the plan", which is what compute's `LATEST(... speed='express_1hr')` reads.
- **Late refund.** Refunds the late order's **speed fee** only ("its same-day fee or its express fee"; "a late order's distance or redelivery fee earns no late-delivery refund"); compute adds `speed_fee_type` and sums only that fee type on the order (base dedup `one_fee_type_per_order` makes it a single fee). Fault share: "the most recent attempt on that order deciding where it has more than one". Prerequisite sentence now "A late-delivery refund is worked out only after the late order's speed fee stands booked on the plan's charge ledger; the fee refunded is that speed fee." Whole superseded base sentence unchanged, so the narrowing to speed fees is inside the declared override.
- **Cancellation refund.** "each fee charged on an order that was cancelled before dispatch is refunded by its own cancellation refund. The order's speed fee … is refunded under this computation; a distance or redelivery fee on such an order is refunded in full and falls outside this computation." Compute sums only the speed-fee type.
- **Switch.** Rule and `baseline.rule` now read "The switch into the Kestrel Delivery Pass Annual is charged the annual switch price, annual_switch_price_usd, less a recent-fees credit of standard_credit_pct percent of the order fees charged on the plan in the month up to the switch date net of the refunds booked on the plan in that month, that net amount never below zero, rounded to the cent." (`baseline.params` adds `standard_credit_pct`). The recent-fees sentence now states "that net amount never below zero". Medicare credit read from the primary active record.
- **Tools.** Bodies unchanged in behaviour (find → create one row → update; no refusal, error or hint); uuid8s unchanged. `refund_late_delivery_fee_e6f66314.source_charge_id` now reads "as shown by the delivery fee lookup for the late order" (the "returned when that fee was booked" phrase is gone). Docstrings still say "Afterwards …" of their own effect only.

Prerequisite graph and sentences: same three edges, all state form, gates `cycle_fee_collected`, `fee_booked`, `net_recent_fees` exist, `resolved_by` = the depended-on target tool; acyclic. The changed late-refund sentence passes the four-point test ("only after"; "the late order's speed fee stands booked on the plan's charge ledger" is a ledger state; no tool/id; scope = the late order's speed fee). Its single writer in this difficulty is `charge_order_fee_01b49350` (no other tool books order fees). The condition now names the fee types in enum words (`express_fee`, `same_day_fee`) — in the `condition` field, not in the policy_source sentence; no red light.

Factor ladders: same 24 factors, same labels, same tiers and counts (settlement 4 = 3/1, express 6 = 5/1, late 4 = 3/1, cancellation 4 = 3/1, switch 6 = 5/1); per-tree multi-source and cross-difficulty unchanged. Baseline coherence now holds for all five: switch — `baseline.rule` states the 50 % recent-fees credit, which is exactly the fall-through of `recent_fees_credit_share`, and every other factor's fall-through (no credit) reduces the compute to that sentence.

### round-1 items, verified against the artifacts

| item | round-1 verdict | revision-2 evidence | status |
| --- | --- | --- | --- |
| D-P1 | SOURCE-POLICY RED | `overwrite` of `delivery_ext_express_order_fee` now names the `delivery_evt_order_eligibility` clause verbatim; the replacement is the extended rule's own pricing sentence; the merged reading is unique (plan's own fee once collected; Pay-Per-Delivery only for a lapsed plan, outside this computation). The base `order_on_open_plan.condition` text repeats the same clause as eligibility evidence text; it gates order placement, not pricing, and is covered by the declared supersession of its rule sentence. | **closed** |
| D-P2 | SOURCE-POLICY RED (latent) | Extended rule now keeps the base waiver ("charged no express fee … such an order is not charged at all"), consistent with base; no-charge is a precondition of the write, as with the allowance. | **closed** |
| D-P3 (a) | latent | Rule now fixes "the express order concerned is the one most recently placed on the plan" = compute. Equivalent. (Observation R2-X1 below on what this does to scope.) | **closed** |
| D-P3 (b) | latent | Late and cancellation refunds now refund the speed fee only, compute sums only that fee type (single by base dedup); distance/redelivery fees are either not refunded (late) or refunded in full outside the computation (cancellation). Rule = compute. | **closed** |
| D-P4 | latent | Rule now says "that net amount never below zero"; compute `MX(0, …)` and `compute_basis` quote it. | **closed** |
| D-F1 | SOURCE-FACTOR RED (structure) | `baseline.rule` now includes the 50 % recent-fees credit = the factor's fall-through. Demonstration in `1.md` revision_2. | **closed (structure)** |
| D-O1 | observation | Addressed by the new first sentence of the settlement rule — which creates finding **R2-P1** below. | superseded by R2-P1 |
| D-X1 | observation | unchanged | held |
| D-X2 | observation | "the most recent attempt on that order deciding" = compute `LATEST` | closed |
| D-X3 | observation | primary + active in rule, ladder and compute (settlement, switch) | closed |
| D-X4 | observation | unchanged | held |
| D-X5 | observation | phrase removed | closed |
| D-X6, D-X7, D-X8 | observation | unchanged | held |

### new findings (revision 2)

- **R2-P1 — SOURCE-POLICY RED (new; conflict between two extended rules over the same charge).** Symptom: the settlement rule now states a price for every cycle that is not overdue, and the switch policy prices one such cycle differently. Evidence: `delivery_ext_overdue_cycle_settlement.rule`: "A cycle that is not overdue is charged the plan's subscription fee, on activation for the plan's first cycle and on the cycle's first day for every later cycle, exactly as the Delivery & Pickup Services charter provides." `delivery_ext_annual_pass_switch_charge.rule`: "may switch to the Kestrel Delivery Pass Annual and pays the switch charge for the annual pass's opening cycle, which starts on the switch date; the payment is booked as the subscription fee of that cycle … The switch charge is the annual switch price less the unused-cycle credit, the recent-fees credit, …". Both policies write `delivery_subscription_charged` (`subject`), and both supersede the very base clause the settlement sentence restates. Same situation — the annual pass's opening cycle on a switch, a cycle of the same plan record that is not overdue, charged on its first day: settlement sentence → the plan's subscription fee (Annual 48.00); switch rule → the switch charge. Root cause: the D-O1 dropped branch was repaired by restating the superseded base clause as a general sentence inside one extended rule, without excepting the cycle the other extended policy prices; the trailing "exactly as the … charter provides" defers to a charter whose clause for that cycle is superseded, so it does not resolve the collision. Affected: `delivery.extended.yaml` → `delivery_ext_overdue_cycle_settlement.rule` (first sentence). Bears on the switch tree (task 1; demonstrated in `1.md` revision_2).
- **R2-X1 — observation.** The express-fee rule now confines the computation to "the one most recently placed on the plan"; an express fee still to be booked on any earlier express order has no computation in the charter. No task world has such an order (task 0's charged order is the latest express order).
- **R2-X2 — observation.** The switch policy's `cross_category` note for coverage still reads "the class of the patient's active prescription insurance record" while rule and compute now read the primary active record. Structural note only; the rule is the policy text.

### closing_checklist (revision 2)

Written after the round-2 reveals (2026-09-24T18:07Z); everything in revision_2 above this heading was written before them.

**The difficulty still does not close.**

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS |
| 1 | **SOURCE-POLICY RED** (R2-P1, new in revision 2) | PASS | PASS | no independent defect (second reading under R2-P1) |

- Round-1 REDs: D-P1/T0-1, T0-2, T0-3, D-F1/T1-1 closed; latent D-P2, D-P3 (a), D-P3 (b), D-P4 closed. Observations D-X2, D-X3, D-X5, T0-4/T1-2 closed; D-O1 was addressed by the sentence that now forms R2-P1; D-X1, D-X4, D-X6, D-X7, D-X8 held unchanged (none is a red light).
- New: R2-P1 (SOURCE-POLICY RED, bears on task 1); observations R2-X1, R2-X2.
- Scope, trees and factors: `charter_scope` of tasks 0 and 1 unchanged, disjoint, jointly complete; trees 2 and 1 prerequisite problems, all edges value_input, one owner=user write each, graph acyclic; every factor bears weight against a coherent baseline with a definite fall-back different from gold; every computation now has a genuine near-miss (express fee's still flips only in combination — observation).
- GT re-verification: every scored value, closure figure and factor figure of both tasks recomputes from the round-2 charter and worlds exactly as declared.
- Gate re-run on the final form: not performed by the auditor (the difficulty does not close); the coordinator's round-2 snapshot is 7/7 rc=0. No gate compares the prose of two extended rules for the same event, which is why R2-P1 passes them.

## revision_3

### charter_global_frozen (revision 3)

- Inputs re-verified: `delivery.extended.yaml` sha256 `d9f9156aa3658fc5f8536be8fbe2d873fa08a46de202b4718073b0c4277b039f` (round 2: `69227503…07d4` — **changed**); `task_tools.py` `fe49c300…a19b` (**unchanged** since round 2); views `r3/task0.view.json` `a428e764…8faa` and `r3/task1.view.json` `6cfc0af4…02ef` — byte-identical to the round-2 views. Gate snapshot (brief): 7/7 rc=0. Input complete.
- Because the charter moved, the charter-global checks are re-derived below; the tool-module section (bodies, owners, docstrings, uuid8s) is carried forward from revision 2 on the grounds of the unchanged `task_tools.py` hash.
- Freeze time 2026-09-24T18:10Z, before the round-3 task files were opened. contamination_disclosure: the auditor has seen the round-1 and round-2 GT of both tasks; revision-3 figures are recomputed, not recalled.

### re-derived charter-global checks (revision 3)

- Base copy still verbatim (trailing blank line only).
- Machine sweep: every `compute_basis` quotation verbatim in its rule; every compute binding has a basis; every `baseline.rule` verbatim in its rule; every prerequisite `policy_source` verbatim in its blocked rule; every `overwrite.superseded_clause` verbatim in its base rule. Compute bindings, factors (ids, labels, ladders, baselines), params, prerequisite edges (problem, gate, form, resolved_by, condition, effect) and `overwrite` lists are the same as in revision 2.
- Text changes found:
  1. **Settlement rule, first sentence** now reads: "A cycle that is neither overdue nor the opening cycle of a switch into the Kestrel Delivery Pass Annual is charged the plan's subscription fee, on activation for the plan's first cycle and on the cycle's first day for every later cycle; the opening cycle of a switch into the Kestrel Delivery Pass Annual is charged the switch charge that the switch rules set for it, and an overdue cycle is settled as follows."
  2. **Express-fee rule**, new sentence after "The express order concerned …": "An express fee is booked while its order is still the most recently placed express order on the plan; a fee left unbooked once a later express order has been placed falls outside this computation."
  3. **Switch `cross_category` note** for coverage now reads "the class of the patient's primary prescription insurance record in active status."
- Re-checks affected by the changes:
  - Overlap on `delivery_subscription_charged`: the settlement rule now partitions every cycle into three disjoint cases (ordinary → subscription fee; opening cycle of a switch into the Annual pass → switch charge; overdue → settlement), and the switch rule prices exactly the second case. The two extended rules now reach one conclusion for every cycle. The base clause they both supersede is fully covered by the three cases, so the D-O1 dropped branch stays closed.
  - Check 6: the new settlement sentence names another problem's subject in business words ("the switch charge that the switch rules set for it") but states no order between the two writes and grounds no edge; no tool name, no policy id. No undeclared cross-problem order. Recorded as observation R3-X1 only because it is a cross-reference between two hubs.
  - The new express sentence is a scope/timing statement on the policy's own write (while its order is still the latest express order); it names no other problem and no ordering against another write. With it, R2-X1's gap is a declared boundary of the computation rather than a silent one.
  - Factor ladders and baseline coherence: unchanged from revision 2; all five baselines coherent.

### round-2 items, verified against the artifacts

| item | revision-3 evidence | status |
| --- | --- | --- |
| R2-P1 (SOURCE-POLICY RED) | settlement sentence now excepts "the opening cycle of a switch into the Kestrel Delivery Pass Annual" and prices it at "the switch charge that the switch rules set for it" — the same conclusion as the switch rule (27.92 on task 1's world). No second reading remains. | **closed** |
| R2-X1 (observation) | express rule declares the scope boundary ("a fee left unbooked once a later express order has been placed falls outside this computation") | closed (as a declared boundary) |
| R2-X2 (observation) | switch coverage note now says "primary … in active status" = rule and compute | closed |
| D-P1, D-P2, D-P3 (a)/(b), D-P4, D-F1, D-X2, D-X3, D-X5 | the texts that closed them in revision 2 are unchanged (overwrite list, waiver sentence, "most recently placed" sentence, speed-fee-only refunds, "never below zero", switch `baseline.rule`, attempt tie-break, primary coverage, docstring) | still closed |
| D-X1, D-X4, D-X6, D-X7, D-X8 | unchanged | held (observations) |

### new findings (revision 3)

- **R3-X1 — observation.** The settlement hub now points at the switch hub's price in words ("the switch charge that the switch rules set for it"). It states no ordering and grounds no dependency, so it is not a red light; it is recorded because the rendered settlement document will carry a reference to another problem's rule.
- No new red light found.

### closing_checklist (revision 3)

Written after the round-3 reveals (2026-09-24T18:11Z).

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

- Per-task files `0.md`, `1.md` correspond one-to-one with the tasks; `_difficulty.md` alongside; revisions 1–3 kept intact and appended in order; every revision-3 comparison carries PASS.
- Extended policies fully covered: task 0 = {overdue_cycle_settlement, express_order_fee, late_delivery_refund}, task 1 = {dispatch_cancellation_refund, annual_pass_switch_charge}; pairwise disjoint, jointly complete; each scope is a whole tree. Task tools and GT closed; five task tools with independent, unchanged uuid8s (`c99b5804`, `01b49350`, `e6f66314`, `665693af`, `b46d5026`).
- Trees: task 0 — 2 prerequisite problems, 2 value_input edges, owner=user settlement; task 1 — 1 prerequisite problem, 1 value_input edge, owner=user switch; the difficulty-wide graph is acyclic with no cross-task edge.
- Factors: every computation has 4–6 factors (≥2 parameter, ≥1 method), a self-sufficient baseline stated in its rule and equal to its factors' fall-throughs, every ladder ≥3 tiers stated in full in its rule with distinct outcomes; every factor bears weight on its task's world; each baseline gives a definite number ≠ gold (48.00 ≠ 47.96; 6.99 ≠ 8.36; 8.36 ≠ 6.78; 6.29 ≠ 4.60; 44.01 ≠ 27.92); each task has a multi-source and a cross-difficulty factor with seeded rows; each computation has a near-miss (the express fee's flips its tier only in combination — observation).
- All round-1 and round-2 red lights closed: D-P1/T0-1, T0-2, T0-3, D-F1/T1-1, D-P2, D-P3 (a)/(b), D-P4, R2-P1. Open observations only: D-X1, D-X4, D-X6, D-X7, D-X8, R3-X1.
- Instantiation-stage gates on the final form: the coordinator's round-3 re-run (7/7 rc=0 on charter `d9f9156a…039f`, tools `fe49c300…a19b`) is cited; the auditor did not re-run them (Step 0: gates are supplied, not run by the auditor).

**The difficulty passes the source-layer audit (revision 3).**

## revision_4

### charter_global_frozen (revision 4)

- Inputs re-verified: `delivery.extended.yaml` `d9f9156a…039f` — **unchanged** since revision 3; `task_tools.py` sha256 `54a79a2d3def53a7e9cc9842ea149556ec4bdb63ea64bebd5381a9e8b45d2cda` (revision 3: `fe49c300…a19b` — **changed**); views `r4/task0.view.json` `a428e764…8faa`, `r4/task1.view.json` `6cfc0af4…02ef` — unchanged. Gate snapshot (brief): 7/7 rc=0. Trigger (brief): the whole-scenario validator rejected `import datetime` in `task_tools.py`.
- Carried forward by hash (charter unchanged): policy_conflict_scan, rule_compute_equivalence, prerequisite_graph, prerequisite_sentences, override_declarations and factor_ladders as re-derived in revision 3. Re-derived because the tool module moved: action_binding_and_uuids.
- Freeze time 2026-09-24T20:03Z, before the round-4 task files were opened. contamination_disclosure: earlier rounds' GT seen; no GT value is used below.

### action_binding_and_uuids (revision 4)

- Module: one import (`from erlbench import ToolContext, tool`); no `datetime`, `time`, `random` or file access; five `@tool` functions, the same names, owners (`settle` user, `charge` agent, `refund_late` agent, `refund_cancelled` agent, `switch` user) and uuid8s (`c99b5804`, `01b49350`, `e6f66314`, `665693af`, `b46d5026`).
- The four other tools, compared line by line with the text read in round 1 (plus the one round-2 docstring change): module docstring, `settle_overdue_pass_fee_c99b5804`, `charge_order_fee_01b49350`, `refund_cancelled_order_fee_665693af` identical; `refund_late_delivery_fee_e6f66314` identical to its revision-2 form (the `source_charge_id` line "as shown by the delivery fee lookup for the late order"). Signatures, docstrings, `make_id` arguments, created fields, updates and return dictionaries unchanged. The reworker's "untouched" claim holds.
- `switch_delivery_pass_b46d5026`: signature and docstring unchanged (same cycle description "its last day being one day short of the same date a period later: one calendar month for the monthly passes, twelve calendar months for the annual pass"); `make_id`, `create`, `update` and the return dictionary unchanged. Only the date handling changed: `_dt.date.fromisoformat(...)` and `date(...) - timedelta(days=1)` are replaced by a pure-integer re-implementation (ISO calendar and ISO week forms, validation errors, month-length table, previous-day roll-back, year-10000 overflow).
- **Behaviour equivalence, demonstrated rather than taken on the claim:** the round-1 body (`fromisoformat` + month arithmetic + `timedelta`, reconstructed verbatim from the round-1 read) and the new body were run side by side (Python 3.14.4, a stub `ctx`) on **every calendar date 0001-01-01 … 9999-12-31 for both the annual and the monthly period — 7,304,118 calls, 0 differences** in `cycle_end_date` or in the raised exception type (including the year-9999 overflow of the annual period); on 28 malformed or alternative-form strings (basic format, ISO week forms incl. W53 edge years, out-of-range fields, padding, non-ASCII digits, trailing text, empty) — 0 differences in outcome; on non-string inputs — both raise `TypeError`. For the scored input (`2026-09-23`, annual) the new body books the subscription row dated `ctx.now()` and sets `cycle_end_date` **2027-09-22**, the value the round-1 body gives.
- Tool layer still judges no prerequisite: the only new failure paths are malformed-date errors that the round-1 body raised identically before any write.
- Observation R4-X1: the re-implementation is ~90 lines of calendar code in a task tool to reproduce `fromisoformat`'s full input grammar (ISO week dates included) that no task uses; it changes no contract and no result.

### round-3 items

No round-3 red light existed. All round-1/round-2 closures rest on charter text that is byte-identical (hash-unchanged) since revision 3 — still closed. Observations D-X1, D-X4, D-X6, D-X7, D-X8, R3-X1 held unchanged. New: R4-X1 (observation). No new red light.

### closing_checklist (revision 4)

Written after the round-4 reveals (2026-09-24T20:04Z).

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

- The revision-3 closing checklist holds item for item (charter and worlds hash-identical); the only moved artifact, `task_tools.py`, keeps every contract, owner and uuid8, and its one changed body is behaviour-identical to the round-1 body over all 7,304,118 date/period combinations and the malformed-input set tested; it no longer imports `datetime`.
- GT of both tasks unchanged in every scored value, closure figure and factor figure.
- Observations open: D-X1, D-X4, D-X6, D-X7, D-X8, R3-X1, R4-X1, R4-X2 (none a red light).
- Gates on the final form: the coordinator's round-4 re-run (7/7 rc=0 on charter `d9f9156a…039f`, tools `54a79a2d…2cda`) is cited; not re-run by the auditor.

**The difficulty passes the source-layer audit (revision 4).**
