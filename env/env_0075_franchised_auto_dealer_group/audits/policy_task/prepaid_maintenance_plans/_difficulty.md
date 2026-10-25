# Policy-task audit — prepaid_maintenance_plans / charter-global

## revision_1

## charter_global_frozen
- Frozen: 2026-10-22, auditor = independent erl-task-policy-audit agent (not the instantiator). Written before any task GT was revealed; nothing below is derived from a revealed GT field.
- Hashes (sha256, 12-char): `maintenance.extended.yaml` ad56e0ee801b, `task_tools.py` 430512172c3e (match the coordinator's gate snapshot). Masked views: 0.view.json a3abc54f37f2545e, 1.view.json 67a3d3465cd0f80a (match).
- Read: blueprint.yaml, db_schema.json, share_tools.py, products/maintenance.yaml (and the purchase / service / warranty charters only for the cross-category realism and seed checks), the extended charter, task_tools.py, `audits/render_source/XF_recipe.md`, the two masked views, the DSL evaluator `skills/erl-task-instantiate/scripts/check_compute.py` (build_env / eval_compute, used read-only to run the charter's own compute on the views and on probe copies in /tmp/audit_prepaid_maintenance_plans_0075/).
- Masked / not read: tasks/*.json, every masked key (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure*), plan.md, both worklog.md files, any other scenario.
- Entry conditions (step 0): gate snapshot supplied (EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK); masked views supplied with hashes. Complete.

DSL facts used throughout (check_compute.py build_env): `SUM/COUNT/MAX/LATEST` are scoped to the computation's single target holding (`eq[holding_pk] = HID`); `F()/P()` read that holding's row and its variant's parameters; `CFIELD` returns the first matching row of the other category in insertion order; `XMAX` returns 0.0 on no rows; `LATEST` keeps the first row on a same-day tie; `NOW` is the frozen date; `_within(m)` is `0 <= MONTHS(d, NOW) < m`; `MONTHS` counts whole months with a day-of-month adjustment.

### policy_conflict_scan
- Six extended policies, six distinct target tools. Subjects overlap only where scopes are partitioned by name:
  - `maintenance_plan_sold`: P1 `maintenance_ext_fleet_addendum_price` (Fleet 12-Visit bought on its own) / P5 `maintenance_ext_retail_plan_price` (Essentials/Plus/Premium bought on its own). Each replaced_by excludes the other by name. Plans sold on a purchase deal stay under base pricing (no tool in this difficulty).
  - cancellation trio: P2 `maintenance_ext_fleet_cancel_refund` (fleet, reason not total loss), P3 `maintenance_ext_total_loss_refund` (any plan, total loss), P6 `maintenance_ext_retail_cancel_refund` (retail, reason not total loss). Pairwise disjoint, jointly complete over (fleet/retail) x (total loss / other); each restates free look, unwound-deal precedence, effective date and the 0.00 floor.
  - `maintenance_vehicle_substituted`: P4 `maintenance_ext_fleet_transfer_odometer` only.
- Cross-category reads: purchase (deal status, delivery date/odometer, trade fields, delivery method), service (tier, opened date, open balance, credit limit, late fees, check-in odometers, line counts), warranty (FCM existence). No task tool writes another category; share tools carry no write other than verification and hand-off, so no other product's "owed at once" write is reachable by a solver in this difficulty (XF16 cross-product: clear). Within maintenance, the only writes are the six task tools.
- Scope partition (from the masked views + charter, pre-reveal): task 0 (fleet addendum root) spans {P1, P2, P3, P4}; task 1 (retail price root) spans {P5, P6}. Disjoint and jointly complete over the six policies (to be value-compared against charter_scope after reveal).

### rule_compute_equivalence
Mechanical sweep: every `compute_basis` quote of all six policies is verbatim in its rule (whitespace-normalised); every baseline.rule sentence is in its rule; no factor binding reads another factor's binding (transitive closure over the compute DAG); no factor id is a substring of a tool name (XF7). Sentence-by-sentence two-way sweep findings (each is a finding below; demonstrations on probe copies of the task worlds, file `/tmp/audit_prepaid_maintenance_plans_0075/probes.txt`):
- F-EFF (P2, P3, P6): every rule says the refund "is still computed as of the effective date (the request date)", but every date-sensitive binding is evaluated at `NOW` — P2 `share_recent_visits`, `share_day`, `fee_days`, `recent_days`, `recapture_months`, `standing_opened_months`, `free_look`; P3 `loss_unit_age`, `loss_day_share`, `loss_plan_age`, `courtesy_late_fees` (window), `bonus_days`, `tl_free_look`; P6 `fee_deal_days`, `bundle_months`, `rv_free_look`. Also negative lag: `DAYS(delivery, date) <= 30` is true for a delivery after the date (P1 enrollment, P2 fee, P3 bonus, P5 window, P6 fee), so a deal delivered after the effective date lands on the most generous tier.
- F-REIN (P2, P4): "the plan's latest redeemed visit" / "visit number N has been redeemed" / "no redeemed visit in the last 12 whole months" are computed with `LATEST`/`COUNT` over all `maintenance_visit_redeemed` rows, including redemptions later reversed by `maintenance_visit_reinstated` (base: "A redemption recorded in error ... is reversed and its visit returned"; base measure maintenance_msr_last_visit excludes reinstated redemptions). Members: P2 `latest_visit_odometer`, `share_recent_visits`, `filter_last_used`, `filter_first_used`, `recent_visit_date`; P4 `latest_visit_odometer`.
- F-FALLBACK (P2): P2's rule gives no reading for "the odometer of the plan's latest redeemed visit" when no visit was redeemed; compute invents `or F('odometer_at_sale')` (P4's rule states that fallback, P2's does not).
- F-ANCHOR (P1, P5): the two sale policies price a plan that does not yet exist, but compute is anchored on an existing holding: P1 `replacement_total_loss`/`replacement_sold` and P5 `trade_cancellations` are `COUNT` over that one holding's ledger while the rules read "the cancellation entries of the customer's ... plan" (customer-wide); P5 `P('plan_price_usd')`, `P('retail_value_per_visit_usd')`, `P('visits_included')`, `P('bundled_with_purchase_discount_pct')` read the anchor plan's variant while the rule prices "the chosen plan".
- F-FIRST (P1, P2, P3, P4, P5, P6): definite-article reads of "the customer's ... deal/agreement that stands in delivered (closed) status" are `CFIELD` first matches with no tie rule; P3 `loss_unit_delivery` has no status filter at all.
- Rounding / order: assembly sentences fix the order (rate once, then credits/deductions, round at end; P2/P6 round the share/pro-rata amount first, floor at end; P3 cap after credits); RND placement matches. P4 `int()` truncation matches "in whole miles" for the integer inputs the charter produces.

### action_binding_and_uuids
- (target_tool, computes): P1 (sign_fleet_care_addendum_ac106112, purchase_price), P2 (process_fleet_plan_cancellation_44bd9d69, refund_amount), P3 (process_total_loss_cancellation_8f67308a, refund_amount), P4 (move_fleet_plan_badb11fe, expiration_odometer), P5 (sign_care_plan_contract_c0d53aa0, purchase_price), P6 (process_care_plan_cancellation_e800fe25, refund_amount) — each claimed once.
- Docstrings: format-only arg descriptions, no example values, no other tool named, no sequencing words (only "the new plan then appears", a consequence of the tool's own effect). One enumerated arg per field. Every claimed effect exists in the body. Bodies check nothing and refuse nothing (tool layer judges no prerequisite).
- uuid8s ac106112, c0d53aa0, 44bd9d69, 8f67308a, e800fe25, badb11fe: no shared prefix/suffix, no sequence; independent.
- Trigger rule (XF18): sign tools write plan_sold + visits_loaded (entry_date = sale_date); process tools write plan_cancelled + visits_cancelled + refund_calculated dated the request date (closed_date); move writes vehicle_substituted (no triggers). Nothing lands in another category.

### prerequisite_graph
- Every policy fills `prerequisite` (P2, P4, P6: `[]`). Edges: P1 -> P3 (value_input, gate `replacement_credit`, state), P1 -> P2 (state_gate, gate `maintenance_plans.status`, state), P3 -> P4 (value_input, gate `loss_refund`, state), P5 -> P6 (value_input, gate `trade_credit`, state). All `problem` ids are extended policies of this file, none self, none base. Acyclic (two components: P1->{P2,P3}, P3->P4; P5->P6).
- Each `policy_source` is verbatim in the blocked policy's own rule (mechanical check). All four are `form: state`, none carries `fallback_reason` (correct). `value_input` gates are real compute bindings; the state_gate names the status field.
- `resolved_by` = depended-on policy's target_tool in all four; each effect is real on the task worlds (task files demonstrate the numbers).
- Condition strength: P1->P3 and P5->P6 conditions add "with a maintenance_visits_cancelled entry carrying cancel_reason ..." to the sentence's "stands cancelled"; the only write that cancels such a plan always books that entry, so this is not a semantic strengthening (observation O-1). No authoring-viewpoint phrasing in any `prerequisite` text.

### prerequisite_sentences
- P1 (a) "The fleet addendum price is fixed only after every Kessler Care plan of the customer that carries a signed total-loss cancellation request stands cancelled." — ordering connective "only after"; waited state = plan status cancelled (record-visible: maintenance_plans.status + maintenance_cancellation_requests.cancel_reason); no tool/id/snake_case; scope "every ... plan of the customer" matches the condition. Unique resolving write: process_total_loss_cancellation_8f67308a (the fleet and retail process tools are documented for reasons other than a total loss). Derivation: request row with reason total_loss on an active plan -> P3's own rule ("For any Kessler Care plan cancelled because its vehicle is a total loss") -> that tool. Single reading.
- P1 (b) "A fleet plan addendum is not written until every Kessler Care Fleet 12-Visit plan of the customer that carries a signed cancellation request for a reason other than a total loss stands cancelled." — "not ... until"; state form; unique write process_fleet_plan_cancellation_44bd9d69 (P2 scope). Single reading.
- P3 "Where the unit of a Kessler Care Fleet 12-Visit plan was taken in trade on a Kessler Fleet Vehicle Purchase Agreement, the total-loss refund on that plan is worked out only after the plan stands on the unit delivered on that agreement." — "only after"; waited state (plan.vehicle_id = agreement.vehicle_id) is record-visible and brought about only by move_fleet_plan_badb11fe. BUT the sentence's trigger "the unit ... was taken in trade on [an agreement]" names a fact no record holds: purchase_deals carries trade_in_allowance / trade_appraisal_date / trade_appraisal_odometer and no trade-in vehicle reference; vehicles carries no disposition. Which plan's unit was traded on which agreement can only be guessed from odometer/date consistency -> finding F-TRADEID.
- P5 "The retail plan price is fixed only after every Kessler Care Essentials, Plus or Premium plan of the customer that carries a signed cancellation request for a vehicle sold or traded stands cancelled." — "only after"; state form; unique write process_care_plan_cancellation_e800fe25. Single reading.
- No depended-on rule restates a sentence; no rule names another problem's tool or id; no rule states a cross-problem order that grounds no declared edge; no docstring states sequence.

### override_declarations
Sentence-by-sentence against each `base_policy_refs` entry:
- P1 vs maintenance_agg_fleet_volume: threshold/discount sentence retired by a scoped, self-naming overwrite (restates "not repriced", "no bundle discount"); the "0 means no discount" and "not combined" sentences follow. vs maintenance_evt_sale: "a plan bought on its own is priced at plan_price_usd" retired for the addendum (sibling P5 excludes it by name); eligibility (condition, age, odometer, diesel, one active plan per vehicle), term construction and visit loading are restated or followed. UNDECLARED: "The unit being enrolled is the unit on the customer's Kessler Fleet Vehicle Purchase Agreement that stands in delivered status" narrows base standalone sale (any eligible vehicle) to the delivered-agreement unit, with no overwrite naming the base sale scope -> part of F-FIRST/absent-record. vs maintenance_agg_multi_holding: followed.
- P2 vs maintenance_evt_cancellation_refund: pro-rata clause retired for fleet non-total-loss (scoped, restates free look / unwound / effective date / floor). Free look, unwound, signed request, active-status, shortfall-not-billed followed. Fee: part of the retired clause; fee factor legal.
- P3 vs maintenance_evt_cancellation_refund: "Otherwise the refund follows the plan's refund_method" retired for total-loss cancellations; fee waiver restated; new cap stated in the replacement. Followed elsewhere.
- P4 vs maintenance_evt_fleet_substitution: "its expiration odometer is not reset" retired (scoped). Followed: active-only, replacement eligible and plan-free, keeps sale/expiry date, visits, price, max once. UNDECLARED: "The replacement unit is the unit delivered on the customer's Kessler Fleet Vehicle Purchase Agreement that stands in closed status" narrows base ("the replacement vehicle", any eligible) -> F-FIRST/absent-record.
- P5 vs maintenance_evt_sale: standalone price retired for retail (scoped, sibling exclusion). UNDECLARED: "The vehicle being covered is the vehicle on the customer's Kessler vehicle purchase deal that stands in delivered status" narrows base standalone retail sale to the delivered-deal vehicle -> F-FIRST/absent-record.
- P6 vs maintenance_evt_cancellation_refund: retail-value clause retired for retail non-total-loss (scoped); free look / unwound / floor / effective date restated.
- Disguised forms: no anonymous intermediate, no 0/1 multiplier, no dropped base branch found (the deal_unwound reason routes to P2/P6, whose unwound precedence is kept).

### factor_ladders
Counts as declared -> after the tests below (struck factors in brackets). Every ladder has 3 tiers (owner_rewards, rewards_refund: 4), every tier stated in the rule and implemented in compute, every fall-through equal to the baseline, no factor reads another factor (XF1), no factor id inside a tool name (XF7).

| policy | declared (param/method) | multi-source factors | cross_difficulty | surviving after tests |
|---|---|---|---|---|
| P1 fleet_addendum_price | 6 (5 / 1) | account_standing (tier AND late-fee history) | warranty, service, purchase | 4 params, **0 method** [unit_basis mislabelled F-MLABEL; credit_utilisation unreal F-REAL] |
| P2 fleet_cancel_refund | 6 (5 / 1) | none strictly (usage_share tier 1 is a single comparison) | service, purchase | 5 (4 / 1) [recent_visit unreal F-REAL] |
| P3 total_loss_refund | 4 (3 / 1) | loss_courtesy (tier AND late fees; tier-2 disjunction) | purchase, service | 4 (3 / 1) |
| P4 fleet_transfer_odometer | 5 (3 / 2) | none strictly | purchase, service | 4 (2 / 2) [account_transfer_allowance: observation O-4, kept] |
| P5 retail_plan_price | 4 (3 / 1) | trade_cycle (cancellation entry AND delivered deal) | warranty, purchase, service | **2 (2 / 0)** [retail_basis mislabelled F-MLABEL; delivery_window unreal F-WINDOW] |
| P6 retail_cancel_refund | 4 (3 / 1) | retail_refund_basis (deal field AND ledger) | purchase, service | **3 (3 / 0)** [retail_refund_basis tiers 1 and 2 coincide F-DUPTIER] |

All-pairs method-tier table (XF5; a distinguishing input per pair, or the reason the pair fails):
- P1 unit_basis: T1 = plan_price_usd - retail_value_per_visit_usd = 1029.00 - 94.95 = **934.05**; T2 = 12 x 94.95 = **1139.40**; T3 = **1029.00**. Fleet 12-Visit is the only variant in scope, so every tier is a constant drawn from the variant table; no record value enters any tier; the downstream formula `RND(basis_price*(1-standing_rate)-credit_total,2)` is identical. A parameter ladder labelled method -> FAIL (F-MLABEL).
- P2 usage_share: T1 min(visit share, unused-mile share from max check-in) / T2 min(visit share, unused-day share) / T3 visit share. T1-T3: check-in odometer; T2-T3: days to expiry; T1-T2: check-in vs days. PASS.
- P3 loss_share: T1 price x avg(visit share, mile share) / T2 price x avg(visit share, day share) / T3 standard refund (pro rata or retail value). Distinct inputs pairwise (check-in odometer, days, used-visit retail value). PASS.
- P4 closing_reading_source: T1 trade_appraisal_odometer / T2 max retired-unit check-in / T3 latest redeemed-visit odometer — three different record fields. PASS. starting_reading_source: T1 max replacement check-in / T2 delivery odometer minus delivery distance (added input + operation) / T3 delivery odometer. PASS.
- P5 retail_basis: for the chosen variant T1 = pp - rv, T2 = n x rv, T3 = pp (Plus 8: 574.05 / 999.60 / 699.00); constants per variant, no record value, same downstream formula -> FAIL (F-MLABEL).
- P6 retail_refund_basis: T1 pro rata / T2 max(retail value, pro rata) / T3 retail value. T2 vs T1: retail value amount > pro rata iff purchase_price / visits_included > retail_value_per_visit_usd. For every retail variant plan_price_usd/visits_included (99.50, 97.25, 91.50, 87.375, 89.90) < retail_value_per_visit_usd (99.95, 104.95, 119.95, 124.95, 139.95), and P5's own standalone price never exceeds visits_included x retail_value_per_visit_usd, so on every plan the charter can produce T2 returns the pro-rata amount = T1 -> one tier written as two -> FAIL (F-DUPTIER).

T1/T2 per factor (XF6): T1 is demonstrated per task (task files, factor_weight). T2: every surviving factor is additive or multiplicative into an unconstrained sum; P2/P6 floors and P3's purchase_price cap bind only at extremes, so a producible world exists where each factor alone moves the result (e.g. P3 credits with one visit used: standard refund < purchase_price - 65). PASS for all surviving factors.

Realism (XF22-25), condition by condition: tenure, account standing (net-terms tier + no late fee), new-unit enrollment window, total-loss / sold replacement credit, FCM-adjusted basis, demo-miles per-visit pricing, discount recapture (fleet volume / bundle), filter-visit deduction (visits 6/12 carry cabin + engine filters in the Fleet variant table), delivered-replacement fee waiver, check-in/time-based lesser-of shares, Owner Rewards rates, trade-cycle credit, remaining-visit and booking-delay mileage allowances: real dealer / F&I administrator practice or a plain company schedule. Struck: see F-REAL, F-WINDOW. Goodwill credits keyed on account tier (P2 fleet_standing, P3 loss_courtesy / plan_relationship, P6 rewards_refund) are company-schedule goodwill — observation O-3.
Seeded cross-category rows checked against owning charters: service lines (Net 30: labor -15 %, parts -18 %, shop supplies 5 % of labor, hazardous 4.95, late fee min 25.00 after Net 30 + 5 grace days, payments equal RO totals, open_balance = unpaid RO 363114 = 676.77), warranty (Chevrolet FCM 12 months / 1 visit; Toyota FCM 24 months / 25,000; Ford none; Basic voided by salvage title), plan prices (bundle 5 %, fleet volume 8 % at the 10th active plan) all consistent. Purchase balance_due figures cannot be re-derived without purchase_transactions (unread, accepted residue; observation O-5).

### findings
Probe numbers come from running the charter's own compute (check_compute.build_env/eval_compute) on copies of the masked task worlds with one row added or changed; "reader" values are worked by hand from the rule text. Raw output: /tmp/audit_prepaid_maintenance_plans_0075/probes.txt.

**F-MLABEL — SOURCE-FACTOR RED (P1 unit_basis, P5 retail_basis). Bears on task 0 (P1) and task 1 (P5).**
Symptom: both factors are labelled `method` but every tier only picks a constant from the variant table. Root cause: "takes plan_price_usd less one retail_value_per_visit_usd" / "visits_included times retail_value_per_visit_usd" / "plan_price_usd" are numbers fixed by the variant, not computing methods. No record value enters any tier, and the computation that follows (`RND(basis*(1-rate)-credits,2)`) is the same for all three. Evidence: compute `basis_price` / `retail_basis_price` (maintenance.extended.yaml line 817 `basis_price`, line 1594 `retail_basis_price`). Consequence: P1 is left with 0 method factors (Fleet only: 934.05 / 1139.40 / 1029.00), and P5 is left with 0 method factors (Plus 8: 574.05 / 999.60 / 699.00). Both computations fall below the "at least 1 method" floor. XF5 says "Parameter factors select values, not methods".

**F-DUPTIER — SOURCE-FACTOR RED (P6 retail_refund_basis). Bears on task 1.**
Tier 2 ("the greater of the retail-value amount and that pro-rata amount") equals tier 1 (pro rata) on every plan the charter can produce. Algebra: retail value > pro rata exactly when purchase_price/visits_included > retail_value_per_visit_usd. That never holds: each base retail plan_price is below visits_included x retail_value_per_visit_usd, P5 standalone prices are at most that product, and bundled prices are lower still. So the "sold on a deal / bought on its own" split changes no outcome, and the ladder is really two tiers. P6 is left with 0 method factors and 3 factors in all.

**F-WINDOW — SOURCE-FACTOR RED (P5 delivery_window). Bears on task 1 (charter-global ladder; the task's Plus 8 world sits on a monotone branch).**
Tier 1 takes `bundled_with_purchase_discount_pct`, which is 0.0 for Essentials 2-Visit and Essentials 4-Visit. For those plans tier 1 gives the same value as the fall-through (0), and it is smaller than tier 2 (window_rate_far 0.025). Demonstrated (probe H, Essentials 4-Visit, task 1 world): bought 14 days after delivery the price is 272.69; bought 45 days after it is 265.59. The plan costs less the longer the customer waits, which no dealer publishes as a point-of-sale window.

**F-REAL — SOURCE-FACTOR RED (P1 credit_utilisation, P2 recent_visit). Bears on task 0.**
P1 credit_utilisation discounts a prepaid maintenance addendum by 20.00 / 10.00 according to the service account's current open balance as a share of its credit limit. That ratio is a credit-risk snapshot of the repair-order receivable. No dealer weighs it when it prices a maintenance plan; payment standing is already the account_standing factor. P2 recent_visit deducts 35.00 / 15.00 from a fleet refund when the latest visit was 30 / 90 days or fewer before the effective date. The used visit is already charged through the refund share (and the filter-visit deduction), and no administrator charges extra for how recently it happened. Both conditions are ones the business does not weigh for that quantity.

**F-EFF — SOURCE-POLICY RED (P2, P3, P6; all members listed in rule_compute_equivalence). No consequence in either task world (both requests are dated 2026-10-21 = frozen date).**
Rule: "the refund is still computed as of the effective date (the request date)". Compute: NOW. Demonstration (task 0 world, plan 066912d5 request dated 2026-09-30, processed 2026-10-21): the reader computes the fee as of 09-30. The only delivered Fleet agreement (Silverado) was delivered 10-09, which is not "before the effective date", so the fee is 25.00 and the refund 286.89. Compute counts DAYS(2026-10-09, NOW) = 12 and waives the fee, giving 311.89. Negative lag: evaluated as of 09-30, compute still waives (DAYS = -9 <= 30).

**F-REIN — SOURCE-POLICY RED (P2 five bindings, P4 one; listed above). No consequence in either task world (no reinstatement seeded).**
Probe B (task 0 world, visit 6 of 066912d5 reinstated 2026-08-20). The reader treats visit 6 as reversed, so there is no filter deduction, and takes 2026-06-29 as the latest redemption (114 days, no recent deduction): refund 371.89. Compute: 311.89.

**F-FALLBACK — SOURCE-POLICY RED (P2 latest_visit_odometer). No consequence in the task worlds.**
Probe D2 (066912d5 with no redemption). Compute substitutes odometer_at_sale 21300, so tier 1 applies (check-in 61900 > 26300) and the refund is 371.89. The rule has no latest visit, so tier 1 cannot be tested; the reader drops to tier 2 (no visit in 12 months): min(1, 772/1096) gives 604.50.

**F-ANCHOR — SOURCE-POLICY RED (P1 replacement COUNTs; P5 trade COUNT and every P()). Bears on task 0 (value depends on which holding the computation is anchored to) and task 1 (anchor variant).**
Task 0 world after every prerequisite: compute anchored on the total-loss plan 3f4887c1 gives 756.03, anchored on 066912d5 gives 791.03, and anchored on any other fleet plan gives 816.03. The rule ("the cancellation entries of the customer's Kessler Care Fleet 12-Visit plan") reads all of them and gives 756.03. World with only the sold/traded cancellation booked: rule 791.03 (sold tier) vs compute anchored on 3f4887c1 816.03. P5 probe E5: the customer chooses Plus 8 but the anchor plan is Essentials 4. Compute prices the Essentials 4 tables (222.69); the rule prices the chosen Plus 8 (472.39).

**F-FIRST — SOURCE-POLICY RED (first-match / absent-record reads). Bears on tasks 0 and 1 as charter defects; in both task worlds exactly one deal of each status is seeded, so no in-world consequence.**
Members:
- P1 `basis_unit`, `basis_delivery_odometer`, `enrollment_delivery_date` (FVPA delivered).
- P2 `fee_delivery_date` (FVPA delivered).
- P3 `bonus_delivery_date` (any deal, delivered), and `loss_unit_delivery` (by vehicle, with no status filter: a cancelled deal listed first returns '' and hides the delivered one).
- P4 `rep_vehicle`, `rep_delivery_odometer`, `closing_trade_allowance`, `closing_trade_odometer`, `starting_method`, `starting_distance`, `delay_delivery_date` (FVPA closed: every past fleet purchase ends closed, so a realistic fleet holds many).
- P5 `retail_vehicle`, `retail_cpo`, `window_delivery_date` (any deal, delivered).
- P6 `fee_deal_date` (any deal, delivered).

Demonstrations:
- Probe C, a second delivered agreement listed first: fleet refund 286.89 vs 311.89; addendum 888.13 vs 756.03.
- Probe C4, a second closed agreement listed first: re-based odometer 40009 vs 42650.

Absent record: with no delivered (P1/P5/P6) or closed (P4) deal, the rules' "the unit being enrolled / the vehicle being covered / the replacement unit is the unit on ..." names no vehicle, and compute falls to None. These sentences also narrow the base sale and substitution scope without an overwrite (see override_declarations).

**F-TRADEID — SOURCE-POLICY RED (P3 prerequisite trigger; P4 closing tier 1). Bears on task 0.**
"the unit ... was taken in trade on a Kessler Fleet Vehicle Purchase Agreement" (P3) and "where the replacement's agreement records a trade-in allowance above 0.00, the closing reading is that agreement's trade appraisal odometer" (P4) both assume that the agreement's trade-in is the plan's unit. purchase_deals holds no trade-in vehicle reference (db_schema: trade_in_allowance, trade_payoff_amount, trade_appraisal_date, trade_appraisal_odometer only). XF11 says no rule word may name a fact the records lack. The task-0 consequence is in 0.md.

**F-MOVED-READING — SOURCE-FACTOR RED (P3 loss_reading fallback, unreal value in a world the charter itself produces). No consequence in task 0 (the replacement has a check-in).**
After a P4 move, "odometer_at_sale where the unit has none" is still the retired unit's sale reading. Probe D3 (task 0 world with the Transit's repair order removed): compute uses 12400 against a unit delivered at 14. Mile share 0.3386 instead of 0.5037; refund 400.70 instead of 485.67.

Observations (not grounds for rework):
- O-1: P1->P3 and P5->P6 `condition` adds the cancellation ledger entry; it is implied by the only resolving write.
- O-2: base fleet substitution "at most fleet_substitution_max_per_plan times per plan" cannot be checked, because `maintenance_vehicle_substituted` books no ledger row (base residue).
- O-3: goodwill credits keyed on account tier (P2 fleet_standing, P3 loss_courtesy / plan_relationship, P6 rewards_refund) are company-schedule goodwill, not contract refund terms.
- O-4: P4 account_transfer_allowance (+1000 / +500 term miles by net-terms tier) is loyalty goodwill in miles. It is weak but kept.
- O-5: purchase balance_due figures (49,053.00; 33,260.42) are not re-derivable without the unseeded purchase_transactions. They are unread.
- O-6: the rules call the deal type "Kessler Fleet Vehicle Purchase Agreement" while the record value is "Fleet Vehicle Purchase Agreement". A reader resolves this.

## closing_checklist
Not closed. Step 4 runs only after all M tasks PASS, and both tasks are RED.

Post-reveal facts, for whoever re-audits:
- One audit file per task (0.md, 1.md) sits alongside this file. This is the first revision.
- Scopes match charter_scope exactly: task 0 = {P1, P2, P3, P4} with the four fleet tools; task 1 = {P5, P6} with the two retail tools. The scopes are disjoint and together cover all six policies.
- Trees: task 0 has n = 3 with 2 value_input edges; task 1 has n = 1 with 1 value_input edge. Each has an owner=user root, and the difficulty graph is acyclic.
- Every gold value equals the independent derivation: 42650, 495.67, 311.89, 756.03, 421.05, 472.39.
- The gates were not re-run; that is not this skill's job on a RED round.

Summary of verdicts:
- **Task 0 RED.**
  - SOURCE-POLICY F-TRADEID: two readings of the TL refund, 495.67 vs 398.00.
  - SOURCE-POLICY F-ANCHOR: the proof figure 816.03 vs the rule's 791.03.
  - SOURCE-FACTOR: P1 has 0 method factors (F-MLABEL, F-REAL credit_utilisation); P2's recent_visit is struck (F-REAL).
- **Task 1 RED.** SOURCE-FACTOR: P5 has 0 method factors and 2 surviving factors (F-MLABEL, F-WINDOW); P6 has 0 method factors and 3 factors (F-DUPTIER).
- **Charter RED ids:** F-MLABEL, F-DUPTIER, F-WINDOW, F-REAL, F-EFF, F-REIN, F-FALLBACK, F-ANCHOR, F-FIRST, F-TRADEID, F-MOVED-READING.

VERDICT revision_1: task0=RED task1=RED charter=F-MLABEL,F-DUPTIER,F-WINDOW,F-REAL,F-EFF,F-REIN,F-FALLBACK,F-ANCHOR,F-FIRST,F-TRADEID,F-MOVED-READING

---

## revision_2

### charter_global_frozen (revision_2)
- Frozen 2026-10-22, before any round-2 GT reveal and before reading the reworker's worklog claims. The only thing read from the worklog was its last line, "REWORK round 2: gates 7/7 green" (the entry gate).
- Coordinator snapshot, re-run by me (`/tmp/erl0075_coord/snapshot.sh prepaid_maintenance_plans 2`, 2026-10-22T03:41:17):
  - Gate results: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
  - File hashes: maintenance.extended.yaml 22da08c3d6f2 (changed from ad56e0ee801b); task_tools.py 430512172c3e (unchanged); tasks/0.json f8117ddc9f9b; tasks/1.json 64ac5fc9493e.
  - Views: r2/0.view.json 5cbaeb91c0048187; r2/1.view.json 42e56091547341f4. Masked keys are as in round 1.
- Because the extended charter changed, every charter-global section is re-derived in full below. The tool module did not change, so § action_binding_and_uuids is carried forward by reference: same uuid8s, bodies and docstrings, hash 430512172c3e. The base copy is still verbatim (first 723 lines identical to products/maintenance.yaml, 925140f020c2). The DSL evaluator (check_compute.py, dated 2026-09-16) is unchanged.
- Probe harness and output: /tmp/audit_prepaid_maintenance_plans_0075/derive.py, derive_r2.txt, probes_r2.txt.

### policy_conflict_scan (revision_2)
- The scope partition is unchanged. Sales are split between P1 (fleet addendum) and P5 (retail replacement purchase). Cancellations are split between P2 (fleet, other reasons), P3 (total loss) and P6 (retail, other reasons). Substitution is P4 only.
- New scope tests:
  - P1: a single delivered Fleet Vehicle Purchase Agreement (FVPA), and the unit on it.
  - P2, P3 and P6: the request is processed on its own request date.
  - P4: the plan's unit is no longer registered to the customer, the holder names the replacement, and the customer has a single closed FVPA.
  - P5: a single delivered deal, the same plan name as the replaced plan, and the replaced plan carries a sold/traded cancellation or request.
- Every scoped overwrite names its own scope ("within this policy's scope … and only for such") and restates the base outcome for out-of-scope cases: base price / fleet volume threshold, base refund, unchanged expiration odometer. Sibling exclusions are kept.
- Cross-product "owed at once" writes (XF16): still unreachable, because the share tools have no other-category writes. New seeds:
  - Tacoma FVPA: balance 42,603.00, due 30 days after delivery 2026-10-09, so not late.
  - Fleet incentive: fleet_volume_min_units is 5 and 2026 shows 2 fleet units, so nothing is owed.
  - No maintenance write is owed at the opening beyond the tree.

### rule_compute_equivalence (revision_2)
- Mechanical: every compute_basis quote is verbatim in its rule. Every baseline sentence is in its rule. Every replaced_by and policy_source is in its rule. No factor reads another factor's binding. No factor id is a substring of a tool name. `visits_unused` (P2) and `tl_unused` (P3) carry no compute_basis entry; both are covered by the quoted "unused visits (visits loaded, less visits redeemed, plus visits reinstated)" (observation O2-6).
- Round-1 classes re-checked:
  - **F-EFF: closed.** Each scope is the same-day request, and each rule states "every span this policy counts ends on the effective date, which is the day the refund is worked out". Negative lag is closed everywhere: P1, P4 and P5 use `MX(0, DAYS(..))`, and P2, P3 and P6 no longer count deal days.
  - **F-REIN: closed.** P2 and P4 now say "(reinstated or not)" for the last recorded visit reading and the 12-month redemption test, which matches the MAX/COUNT. The filter deduction now reads net visits used (redeemed − reinstated), which matches the compute. The recent-visit factor is gone.
  - **F-FALLBACK: closed.** P2's rule now states "or odometer_at_sale where that is higher or there is no such entry", and the compute uses MX(MAX(..), odometer_at_sale).
  - **F-ANCHOR:**
    - P5 is closed. The trade count reads "the replaced plan", and the scope requires the bought plan to carry the replaced plan's name, so the anchor variant equals the chosen variant.
    - **P1 is still open.** The rule says "the customer's most recent cancellation of a Kessler Care Fleet 12-Visit plan for a total loss", which is customer-wide. The compute is `COUNT(...)` over the single anchor holding. Probe: a world with a total loss today on 3f4887c1 and an older total loss (2026-08-30) on 0f2e346b. The rule gives 60 and a price of 515.57. Compute anchored on 0f2e346b gives 30 and 545.57.
  - **F-FIRST:**
    - Closed: P1 and P4 (single-agreement scope tests, with stated out-of-scope outcomes); P2 (fee now keyed on net-terms tier); P3 (bonus via XCOUNT of vehicle_price charges; unit deal by vehicle and status delivered/closed); P6 (fee via XCOUNT).
    - **P5 still has one member.** "the replaced plan, which is the customer's retail Kessler Care plan that carries a cancellation, or a signed cancellation request, for a vehicle sold or traded" has no uniqueness test. Probe: task 1 world plus a second same-name plan cancelled sold/traded on 2026-06-10. The trade-cycle credit is 50 if the reader takes today's plan and 0 if it takes the June plan; the price is 269.50 or 319.50.
  - **F-TRADEID: closed.** The P3 prerequisite now reads the title brand, which is record-visible (vehicles.title_brand). The P4 trade-appraisal tier is removed. The replacement unit is now the one the holder names, which the persona supplies only when asked.
  - **F-MOVED-READING: closed.** P3's loss_reading is the greater of the unit's highest check-in and its odometer at delivery on its own deal.
- **New defect, F-PAYTYPE (SOURCE-POLICY):**
  - P1's rule adds up "the customer-pay labor and parts amounts". The compute `spend_total` XSUMs every labor/parts row.
  - P2's rule counts "the customer-pay labor lines … on the plan's unit". The compute `unit_labor_lines` XCOUNTs every labor row.
  - db_schema `service_ro_lines.pay_type` separates customer_pay from service_contract_deductible and warranty_deductible, so the rule's "customer-pay" filter has no counterpart in the compute.
  - Probes: two service-contract-deductible labor lines on 1726aeef give a P2 compute of 346.89 against a rule value of 331.89. One 4,000.00 deductible labor line gives a P1 compute of 495.57 against a rule value of 515.57.

### prerequisite_graph and prerequisite_sentences (revision_2)
- The edges are unchanged in shape: P1→P3 (value_input), P1→P2 (state_gate), P3→P4 (value_input), P5→P6 (value_input). All are state form and acyclic, and each policy_source is verbatim in its blocked rule.
- P3's sentence is now: "The total-loss refund on a plan is worked out only after the plan stands on a unit whose title the records show branded salvage, rebuilt or flood."
  - It uses an ordering connective ("only after").
  - The state it waits on is record-visible (plan.vehicle_id → vehicles.title_brand).
  - It names no tool or id.
  - The condition carries the same scope.
  - Only one write changes a plan's unit: move_fleet_plan_badb11fe. The P4 rule then gives the target: the unit the holder names, on the single closed FVPA. One reading.
- Observation O2-1: the sentence applies to every total-loss refund, retail included. For a retail plan, or any plan whose totalled unit's title is not yet branded in the records, no write of this difficulty brings the state about, so the refund waits on the state's title branding. That is a real proof-of-loss practice. It does not touch either task's tree.
- The P1 and P5 sentences are unchanged, and their single resolving writes are unchanged. The P1→P3 effect text now cites replacement_credit_recent.

### override_declarations (revision_2)
- P1: retires the fleet-volume threshold and the standalone price, but only for an addendum within its scope. The replaced_by says that "every other fleet plan sale keeps the fleet volume threshold" and that out-of-scope addenda keep the base price. The round-1 undeclared narrowing is closed.
- P2, P3, P6: retire the same clauses as in round 1, now with the same-day scope and an explicit out-of-scope exit.
- P4: retires "its expiration odometer is not reset" within its scope only; "every other move keeps its expiration odometer". The undeclared narrowing is closed.
- P5: retires the standalone price for a replacement purchase within its scope; "every other retail plan bought on its own is still priced at plan_price_usd". The undeclared narrowing is closed.
- Observation O2-2 (XF12 route): none of these scope tests appears in compute. The DSL cannot count a category's holdings, cannot read the request date and cannot see the requested vehicle. The compute is therefore exact only on in-scope worlds. Out-of-scope cases follow base text the rule restates. This is the accepted XF12 "coarse exact scope test stated as a plain record test" route.
- Realism: P4 applies only to a customer with a single closed FVPA, and P2/P3/P6 apply only to requests processed on their own date. Both are coarse, artificial boundaries, but the out-of-scope outcome is the published base rule (observation O2-3).

### factor_ladders (revision_2)

| policy | declared (param/method) | method tiers: distinguishing input per pair | multi-source | surviving |
|---|---|---|---|---|
| P1 | 6 (5/1) | unit_basis: T1 pp·max(months share, miles share) vs T2 pp·months share (FCM expiration_odometer > 0 and miles share > months share); T2 vs T3 pp (FCM expiration_date); T1 vs T3 (both). Record inputs: FCM expiration date and odometer, delivery odometer. Genuine. | account_standing | 6 (5/1) |
| P2 | 6 (5/1) | usage_share as in round 1. Genuine. | none strictly | 6 (5/1) |
| P3 | 4 (3/1) | loss_share: T1 avg(visit, mile share from max(check-in, delivery odometer)) / T2 avg(visit, day share) / T3 standard. Genuine. | loss_courtesy | 4 (3/1) |
| P4 | 5 (3/2) | closing: retired-unit max check-in / max Factory Basic claim odometer / last recorded visit reading (three fields). starting: as in round 1. Genuine. | none strictly | 5 (3/2) |
| P5 | 4 (3/1) | retail_basis, same shape as P1. Genuine. | trade_cycle (struck) | **3 (2/1)** — trade_cycle struck, F-UNREACH |
| P6 | 4 (3/1) | retail_refund_basis: T1 pro rata (financed) / T2 min(retail value, day share), not financed and > half the term run / T3 retail value. T2≠T3 when the day share < retail value (e.g. Plus 8 standalone 699.00, 1 visit used, 75 % run: 174.75 vs 574.05). T1≠T3 always unless 0 used. Genuine. F-DUPTIER closed. | none strictly | 4 (3/1) |

- F-MLABEL: closed for P1 and P5 (the FCM-overlap shares read warranty and delivery records).
- F-WINDOW: closed. delivery_window is removed; new_owner_enrollment (30.00 / 15.00 / 0) is monotone.
- F-REAL: closed. credit_utilisation and recent_visit are removed.
- Realism of the new factors:
  - P1 service_spend (12-month customer-pay spend) is a real loyalty measure.
  - P2 net_terms_fee is a company fee schedule.
  - P2 fleet_tenure_refund and unit_service_history are goodwill (observation O-3 class).
  - P4's warranty-claim closing reading is real odometer evidence.
  - P5 new_owner_enrollment is real.
  - P6's financed→pro-rata tier is real (pro-rata refunds of products financed on the installment contract).
  - P6 trade_up_fee is real.
  - P4 account_transfer_allowance is unchanged (observation O-4).
- T1/T2: each surviving factor is additive or multiplicative, so a producible world moves it alone.
- **New defect, F-UNREACH (SOURCE-FACTOR):**
  - P5's scope requires "the customer's single Kessler vehicle purchase deal that stands in delivered status". Every customer who reaches this write therefore has a delivered deal.
  - The trade_cycle conjunct "with a Kessler vehicle purchase deal of the customer in delivered status" holds for every such customer.
  - The tier "such an entry with no deal in delivered status earns trade_credit_without_deal" can never be selected (`trade_deal = EXISTS('purchase', status='delivered')` is always True in scope).
  - The ladder therefore has two reachable tiers (50 / 0) and a vacuous condition. trade_cycle is struck, leaving P5 with 3 surviving factors (below 4). It was also P5's only multi-source factor.
- Cross-category seeds re-checked:
  - Tacoma FVPA ledger: vehicle_price 41,860.00 on the contract date; sales tax 7.5 % = 3,139.50; fleet electronic filing 18.00; doc fee waived (fleet); title 85.50; ACH deposit 2,500.00 (fleet minimum) applied with its payment row; balance 42,603.00 equals the ledger.
  - Highlander ledger: vehicle_price 46,880.00; doc 299.00 (KTD); tax 3,516.00 = 7.5 %; electronic filing 24.00; title 52.00; card deposit 1,000.00 (≤ card max 5,000) applied; check 8,000.00; balance 41,771.00 equals amount financed.
  - New cfe44607 RO 364520 (2026-07-28, 53,640 miles): Net 30 labor −15 %, parts −18 %, supplies 5 %, paid 08-20 within terms.
  - Toyota FCM 24 months / 25,000 on the Tacoma: consistent with the warranty charter.

### findings (revision_2)
These are the open charter findings after round 2. The round-1 ids not listed below were verified against the artifacts and are closed; § rule_compute_equivalence and § factor_ladders (revision_2) give the evidence per id.

**F-PAYTYPE — SOURCE-POLICY RED (new).** All members, in one pass:
- P1 `spend_total`. The rule counts "customer-pay labor and parts amounts". The compute sums every labor and parts row, with no pay_type filter.
- P2 `unit_labor_lines`. The rule counts "customer-pay labor lines". The compute counts every labor row.

The schema defines pay_type with three values: customer_pay, service_contract_deductible and warranty_deductible. The two deductible values are distinct from customer_pay, so the rule's filter excludes them.

Probes:
- P2: rule 331.89, compute 346.89.
- P1: rule 515.57, compute 495.57.

Neither task world seeds a deductible row, so this has no consequence in the tasks.

**F-UNREACH — SOURCE-FACTOR RED (new).** P5 trade_cycle. The "no deal in delivered status" tier cannot be reached inside P5's single-delivered-deal scope, and the delivered-deal conjunct is vacuous there. This bears on task 1: P5 is left with 3 surviving factors and the task has no multi-source factor.

Other members of the class, from a sweep of every scoped policy for tiers that contradict their own scope:
- P1: none. Its enrollment, standing and spend tiers are all reachable inside the scope.
- P4: none. Its booking-delay and starting tiers read the single closed agreement and every tier is reachable.
- P2, P3, P6: none. A same-day scope does not collide with any tier.

**F-FIRST — SOURCE-POLICY RED (one member left).** P5 "the replaced plan, which is the customer's retail Kessler Care plan that carries a cancellation, or a signed cancellation request, for a vehicle sold or traded" has no uniqueness or recency test. A second same-name plan cancelled sold/traded on 2026-06-10 gives two readings: price 269.50 or 319.50.

Other first-match reads, swept:
- P3 `loss_unit_delivery` (closed, then delivered, deal on the unit). A second closed deal on the same vehicle (bought, sold back, rebought) is barely producible. Observation O2-5.
- Every other CFIELD is either inside a single-record scope or is the one-per-customer service account.

**F-ANCHOR — closed (re-assessment of my own frozen revision_2 note; this does not rest on GT).** The pre-reveal note above recorded P1 as still open. That note's probe anchored the computation on a plan carrying an older total loss. P1's rule singles out "the customer's most recent cancellation … for a total loss", so the holding the computation must read is the plan that carries that entry. On that plan, `COUNT(within 1)` / `COUNT(within 3)` reproduces the rule exactly, including the cases of no total loss at all and a same-day tie. The probe used an anchor the rule excludes, so it is not a second reading.

Observation O2-4: an in-scope fleet customer with no existing plan has no holding to anchor the oracle on. The rule is unaffected.

Observations O2-1 to O2-6 are recorded in the sections above. O-3 (goodwill credits) and O-4 (transfer allowance) carry over from revision_1.

## closing_checklist (revision_2)
Not closed: task 1 is RED.

What does hold:
- **Files:** one file per task plus this one, with revision_1 preserved and revision_2 appended.
- **Scopes:** match charter_scope exactly — task 0 = {P1, P2, P3, P4}, task 1 = {P5, P6}. They are disjoint and together complete.
- **Graph:** acyclic.
- **Trees:**
  - Task 0: n = 3, 2 value_input edges, owner = user.
  - Task 1: n = 1, 1 value_input edge, owner = user.
- **Gold values:** all six equal the independent derivation — 43130, 498.96, 331.89, 515.57, 421.05, 269.50.
- **Gates:** green per the snapshot I re-ran myself (cited in charter_global_frozen revision_2).

Round-1 → round-2 status:

| Round-1 finding | Status |
|---|---|
| F-MLABEL | closed |
| F-DUPTIER | closed |
| F-WINDOW | closed |
| F-REAL | closed |
| F-EFF | closed |
| F-REIN | closed |
| F-FALLBACK | closed |
| F-ANCHOR | closed |
| F-TRADEID | closed |
| F-MOVED-READING | closed |
| F-FIRST | open, P5 "replaced plan" member only |

New in round 2: F-PAYTYPE and F-UNREACH. Nothing that passed in round 1 regressed, other than these two new classes, both introduced by the round-2 edits.

VERDICT revision_2: task0=PASS task1=RED charter=F-PAYTYPE,F-UNREACH,F-FIRST

---

## revision_3

### charter_global_frozen (revision_3)
- Frozen 2026-10-22, before the round-3 GT reveal and before reading the reworker's round-3 claims. The only worklog line read was the gate line "REWORK round 3: gates 7/7 green".
- I ran `/tmp/erl0075_coord/snapshot.sh prepaid_maintenance_plans 3` myself at 2026-10-22T05:08:24:
  - Gates: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
  - Hashes: maintenance.extended.yaml 1612343de78c (changed); task_tools.py 8d7ce9149aa2 (changed); tasks/0.json a031c106604b; tasks/1.json 9c01254502d2.
  - Views: r3/0.view.json 5cbaeb91c0048187, r3/1.view.json 42e56091547341f4. Both are identical to r2, so the task worlds and personas are unchanged.
- Re-derivation scope:
  - The charter and the tool module both changed, so every charter-global section was re-derived.
  - The base copy is still verbatim. The DSL evaluator is unchanged.
  - Scratch files: /tmp/audit_prepaid_maintenance_plans_0075/ext_r3.yaml, derive_r3.txt.
- What changed in the charter:
  - P1 `spend_total` and P2 `unit_labor_lines` now filter `pay_type='customer_pay'`.
  - P5 has a new replaced-plan definition and trade-cycle tiers.
  - All six rules now say "rounded half up to the cent".
  - All other compute bindings are unchanged from revision_2.

### action_binding_and_uuids (revision_3)
- Unchanged: the uuid8s, signatures, owners and docstrings. Docstrings carry format only, with no example values and no sequencing words; the only "then" is "the new plan then appears".
- New `_Fmt` helpers. Every docstring format claim is now enforced in the tool body:
  - money args: half-up to the cent on the decimal string, so 332.025 is stored as 332.03;
  - odometer args: half-up to whole miles;
  - dates: truncated to YYYY-MM-DD;
  - refund_due_balance: re-rounded half up.
- Bodies still check no business condition and refuse no call. Every effect a docstring claims is present in its body.

### rule_compute_equivalence (revision_3)
- Mechanical sweep: clean. All quotes and baseline sentences are verbatim, no factor reads another factor, and no factor id is a substring of a tool name.
- **F-PAYTYPE: closed.** P1 `spend_total` and P2 `unit_labor_lines` now filter `pay_type='customer_pay'`. Re-run probes with two 2,000.00 service-contract-deductible labor lines give P2 = 331.89 and P1 = 515.57, equal to the rule.
- **F-FIRST (P5 member): closed.** The replaced plan is now "the Essentials, Plus or Premium plan named on the customer's most recent signed cancellation request for a vehicle sold or traded (by request date)". A same-date tie, or no such request, is outside scope.
  - Probe (second same-name plan with an older request): there is one reading — the replaced plan is the one with today's request, priced at 269.50.
  - The computation anchor is the plan the rule singles out.
  - Remaining first-match reads: P3 `loss_unit_delivery` stays observation O2-5. Nothing else.
- **New, F-HALFUP (SOURCE-POLICY RED).** Every rule now states "rounded half up to the cent", but `RND` is Python `round(float(x), 2)`. On a decimal half-cent tie the float sits just below the tie, so it rounds down.
  - Producible example: a Plus 8 plan bought on a deal at 664.05 (5 % bundle), financed, with 4 visits used. P6 pro rata = 664.05 × 4/8 = 332.025. The rule gives 332.03; compute gives 332.02. With task 1's other terms (fee 0, recapture 13.98, Gold +20) the refund is 338.05 under the rule and 338.04 under compute.
  - Another tie: Plus 6 bundled at 521.55 with 3 or 5 unused visits (260.775, 434.625).
  - Members, every RND that can see a tie:
    - P1 `result`;
    - P2 `share_amount`, `recapture_amount`, `result`;
    - P3 `standard_refund`, `loss_refund`, `result`;
    - P5 `result`;
    - P6 `basis_day_amount`, `method_amount` (pro rata), `bundle_recapture`, `result`.
  - P4 `int()` matches "in whole miles" for the integer inputs the charter produces.
  - The tool bodies now round half up, so an agent passing a tie value is stored on the rule's side while gold sits on the other.
  - This mismatch was already latent in rounds 1–2 (the tool docstrings said half up, the rules said "rounded to the cent"). Round 3 states the mode in the rules, which makes it an explicit rule/compute conflict.
  - Neither task world hits a tie: 415.03125, 664.05 × 5/8 and all other gold intermediates are off-tie.

### prerequisite_graph / prerequisite_sentences / override_declarations (revision_3)
- Unchanged from revision_2: the edges, the sentences and every replaced_by. P5's scope sentence changed, but its overwrite exit ("every other retail plan bought on its own is still priced at plan_price_usd") is unchanged and still covers the new out-of-scope cases (tie, no request).

### factor_ladders (revision_3)
- **F-UNREACH: closed.** P5 trade_cycle now reads two records:
  - the replaced plan's sold/traded cancellation entry in the last 3 months, combined with whether the replaced plan was sold on a Kessler deal (50.00) or bought on its own (25.00);
  - no such entry gives 0.
  - All three tiers are reachable within scope. Probe: replaced plan bought on its own gives 294.50; task world gives 269.50; opening world gives 319.50. Neither conjunct holds for every in-scope customer.
  - The factor is multi-source: maintenance ledger entry plus the plan's own Kessler deal row.
  - Realism: a larger trade credit for a customer whose replaced plan was bundled on a Kessler deal is a plausible company loyalty schedule.
- Counts:

| Policy | Factors | Methods |
|---|---|---|
| P1 | 6 | 1 |
| P2 | 6 | 1 |
| P3 | 4 | 1 |
| P4 | 5 | 2 |
| P5 | 4 | 1 |
| P6 | 4 | 1 |

- Multi-source factors: account_standing (P1), loss_courtesy (P3), trade_cycle (P5).
- Method tiers are as in revision_2 and all pairwise distinct.
- T1/T2 hold.

### findings (revision_3)
- **F-HALFUP — SOURCE-POLICY RED (new).** All members are listed above. No in-task consequence.
- Closed: F-PAYTYPE, F-UNREACH, F-FIRST.
- Observations O2-1 to O2-6, O-3 and O-4 carry over.

## closing_checklist (revision_3)
- Both tasks PASS on all four relationships (0.md, 1.md revision_3). The checklist is not closed: the charter-global F-HALFUP remains RED. It has no consequence in either task.
- **Files:** one file per task plus this one; revisions 1–3 preserved.
- **Scopes:** equal to charter_scope; disjoint and complete.
- **Graph:** acyclic. Trees: task 0 n = 3 / 2 value_input; task 1 n = 1 / 1 value_input; both roots are owner = user.
- **Factor floors:** every computation has a baseline and meets the floors (table above); each task has a multi-source factor and a cross-difficulty factor.
- **Gold:** equal to the independent derivation (43130, 498.96, 331.89, 515.57, 421.05, 269.50).
- **Gates:** green per the round-3 snapshot I ran.
- **Tool bodies:** they enforce their docstrings.
- **Round-2 REDs:** F-PAYTYPE, F-UNREACH and F-FIRST are closed.
- **New RED:** F-HALFUP — rules say half up, but `RND` rounds the binary float; tie demonstrated at 332.025, giving 338.05 vs 338.04.
- **Reworker's claim:** the worklog says "rule rounding sentences, docstrings and tool bodies all say/enforce half up". That is true of the rules, docstrings and tool bodies, but not of the compute that produces gold.

VERDICT revision_3: task0=PASS task1=PASS charter=F-HALFUP

---

## revision_4

### charter_global_frozen (revision_4)
- Frozen 2026-10-22, before the round-4 GT reveal and before reading the round-4 worklog body. I read only the gate line, which is the last non-blank line: "REWORK round 4: gates 7/7 green".
- I ran `/tmp/erl0075_coord/snapshot.sh prepaid_maintenance_plans 4` myself at 2026-10-22T05:53:56:
  - Gates: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
  - Hashes: maintenance.extended.yaml 50d3a690ea23 (changed); task_tools.py 8d7ce9149aa2 (unchanged); tasks/0.json e21b8f568013; tasks/1.json e017edde2c98.
  - Views: r4/0.view.json 5cbaeb91c0048187 and r4/1.view.json 42e56091547341f4, both identical to r2/r3.
- The charter diff against my saved round-3 copy (/tmp/audit_prepaid_maintenance_plans_0075/ext_r3.yaml) touches only compute. `+ 0.000001` is added inside 13 RND bindings, every member listed under F-HALFUP: P1 result; P2 recapture_amount, share_amount, result; P3 standard_refund (both branches), loss_refund (both branches), result; P5 result; P6 basis_day_amount, method_amount, bundle_recapture, result.
- No rule, compute_basis, factor, prerequisite or overwrite changed, and task_tools is unchanged. The round-3 sections on prerequisites, overrides, factor ladders, action binding, tool bodies and seeds therefore carry forward by reference: their inputs are unchanged apart from the RND arguments examined below. The mechanical sweep re-ran clean.

### rule_compute_equivalence (revision_4)
- **F-HALFUP: closed at exact ties.**
  - Probe from round 3 (Plus 8 bundled at 664.05, 4 visits used, pro rata 332.025): compute now gives 338.05, which equals the rule.
  - Brute force over every price/share/rate grid the charter can produce found 1,192 exact ties; at every one, `round(x + 1e-6, 2)` equals the exact half-up result.
- **New, F-EPS — SOURCE-POLICY RED.** The epsilon also rounds up values that are not ties but sit within 1e-6 below a half cent. The rules ("rounded half up to the cent") round those down.
  - Where the risk comes from: arguments whose exact denominator is fine enough to land in (h − 1e-6, h), with h a half cent. That happens with mile shares over 75,000 or term_miles, combined with a rate.
  - Demonstrated on the task-0 world, changing only the Tacoma's delivery odometer from 11 to 869 (a realistic dealer-transport reading):
    - P1 basis = 1029 × 50869/75000; × 0.97 = 676.9849996.
    - Price = 676.9849996 − 150 = 526.9849996.
    - Rule (half up): 526.98. Compute: 526.99.
  - All members, from an exact-fraction brute force (/tmp/audit_prepaid_maintenance_plans_0075/tiecheck.py, tiecheck2.py):
    - P1 `result`: Net 30 at m ∈ {869, 14238, 25869, 39238, 50869, 64238}; Net 15 at 9 m values.
    - P5 `result`: e.g. Essentials 4 + Silver, m = 10209, gives 155.6749992 (compute .68, rule .67). 31 grid hits across E4/P6/PR at the Silver, Platinum and other rates.
    - P2 `share_amount`: mile share on an addendum-priced plan, e.g. price 515.57 at m = 26421; price 756.03 at m = 22699.
    - P3 `loss_refund`: e.g. a 946.68 fleet plan, mile tier, m = 20241, gives 48.8549992 (compute .86, rule .85).
  - Bindings swept and cleared (their exact denominators keep them at least 5.5e-6 from a half cent):
    - P6 basis_day_amount (/days ≤ 1827);
    - P6 method_amount pro rata (/visits);
    - P6 bundle_recapture and P2 recapture_amount (rate × cents);
    - P3 standard_refund (/12, or retail value);
    - P2, P3 and P6 `result` (sums of already-rounded cents plus whole-dollar credits).
  - In-task consequence: none. Gold intermediates are 686.1508×0.97, 433.9638, 434.2105, 415.03125 and 349.50, none within 1e-6 of a half cent.

### findings (revision_4)
- **F-EPS — SOURCE-POLICY RED (new).** All members are listed above.
- **Closed:** F-HALFUP.
- **Observations carried:** O2-1 to O2-6, O-3, O-4.

## closing_checklist (revision_4)
- Both tasks PASS all four relationships (0.md and 1.md, revision_4). Gold values (43130, 498.96, 331.89, 515.57, 421.05, 269.50) match my independent derivation.
- Gates are green per the round-4 snapshot I ran. Tool bodies enforce their docstrings (unchanged since revision_3).
- Not closed. The charter-global F-EPS is RED: the 1e-6 offset added for F-HALFUP fixes exact ties but rounds up non-tie values within 1e-6 below a half cent.
- Reworker's claim: "RND(x + 0.000001, 2), so they round half up as the rules state". This holds at exact ties only. It is contradicted at 526.9849996, where the rule gives 526.98 and the compute 526.99.

VERDICT revision_4: task0=PASS task1=PASS charter=F-EPS

---

## revision_5

### charter_global_frozen (revision_5)
- Frozen on 2026-10-22, before the round-5 GT reveal and before I read the round-5 worklog body. The only worklog line I read was the gate line: "REWORK round 5: gates 7/7 green".
- I ran `/tmp/erl0075_coord/snapshot.sh prepaid_maintenance_plans 5` myself at 2026-10-22T07:06:23:
  - Gates: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
  - File hashes: maintenance.extended.yaml 86c5c1247c76 (changed); task_tools.py 8d7ce9149aa2 (unchanged); tasks/0.json 2ed1f7d2f8b1; tasks/1.json 1cd9966268cb.
  - View hashes: r5/0.view.json 5cbaeb91c0048187 and r5/1.view.json 42e56091547341f4, both unchanged since r2.
- What changed: diffed against my saved round-4 copy (ext_r4.yaml), the only change is the offset inside the same 13 RND bindings, `+ 0.000001` → `+ 0.000000001`.
  - No rule, quote, factor, prerequisite, overwrite or tool changed.
  - Every other charter-global section therefore carries forward by reference from revision_3/revision_4.
  - The XF_recipe re-check on the changed bindings: B8 (rounding sentence vs RND placement and mode) is examined below. The rest of the recipe is unaffected, since only an additive constant inside RND moved.
- Coordinator ruling applied: a value within 1e-9 below a half cent is DSL-known residue, not a RED. Any rule/compute rounding mismatch larger than 1e-9 is RED. A floor that creates an amount where the rule owes nothing is RED.

### rule_compute_equivalence (revision_5)
- **F-EPS: closed.** I ran an exact-fraction brute force (/tmp/audit_prepaid_maintenance_plans_0075/tiecheck5.py) comparing `round(x + 1e-9, 2)` against exact half-up, over:
  - P1 and P5 price grids (every retail variant and every fleet/retail rate, mile and month shares);
  - P2 share mile, P3 loss mile, day shares and pro rata, at prices 1029, 946.68, 515.57, 756.03, 664.05, 521.55, 363.85, 199 and 389.

  Results:
  - Mismatches larger than 1e-9: **0**.
  - Residue at or below 1e-9: 0 hits found.
  - Exact ties: all 6,208 round up correctly.
  - The round-4 probe (Tacoma delivered at 869) now gives 526.98, equal to the rule (was 526.99).
- **F-HALFUP stays closed.** The tie probe (pro rata 332.025) gives 338.05, equal to the rule.
- **Floor check.** The offset cannot create an amount where the rule owes nothing:
  - Every `MX(0, RND(x + 1e-9, 2))` with x ≤ 0 returns 0.00 (or −0.00, which the floor lifts to 0.00).
  - A 0.01 could appear only for x within 1e-9 below 0.005, which is ruled residue.
  - No pass-through `result` adds a non-cent amount, so the floor creates nothing.

### findings (revision_5)
- No open RED. F-EPS is closed; F-HALFUP, F-PAYTYPE, F-UNREACH and F-FIRST remain closed.
- Observations carried forward: O2-1 to O2-6, O-3 and O-4.

## closing_checklist (revision_5)
Every item of the step-4 checklist is met:

- **Files:** one audit file per task (0.md, 1.md) sits alongside this file. Revisions 1–5 are kept in place, and every comparison section of revision_5 carries a PASS.
- **Coverage and scope:**
  - All six extended policies are covered. charter_scope assigns {P1, P2, P3, P4} to task 0 and {P5, P6} to task 1; the scopes are disjoint and together complete.
  - Task tools and GT close against each other.
  - The six uuid8s were generated independently and are frozen (ac106112, c0d53aa0, 44bd9d69, 8f67308a, e800fe25, badb11fe).
- **Problem trees:**
  - Task 0 has 3 prerequisite problems with 2 value_input edges.
  - Task 1 has 1 prerequisite problem with 1 value_input edge.
  - Both roots are owner=user signing tools.
  - The difficulty-wide prerequisite graph is acyclic.
- **Factors:**
  - Every computation has a self-sufficient baseline, 4–6 factors, at least 2 of type parameter and at least 1 of type method, and three or more tiers per ladder, all stated in the rule.
  - Tiers are distinct, conditions and outcomes are realistic, and every factor bears weight on its task's world.
  - The baseline fall-back differs from gold in every computation.
  - Task 0 has multi-source factors (account_standing, loss_courtesy) and cross-difficulty factors (service, purchase, warranty). Task 1 has a multi-source factor (trade_cycle) and cross-difficulty factors (warranty, service, purchase).
- **Gates:** the instantiation gates were re-run on the final form (round-5 snapshot I ran at 2026-10-22T07:06:23): 7/7 OK.
- **Tool bodies:** they enforce their docstrings — money half-up to the cent, odometers in whole miles, dates as YYYY-MM-DD.
- **Rounding:** compute rounding agrees with the "half up" rules at every exact tie, with no mismatch above 1e-9.
- **Gold:** all six values equal my independent derivation (43130, 498.96, 331.89, 515.57, 421.05, 269.50).
- **Round-4 RED F-EPS:** closed. Every earlier RED id (rounds 1–4) stays closed. Nothing that passed has regressed.
- **Observations (not grounds for rework):** O2-1 to O2-6, O-3 and O-4.

VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

---

## revision_6

### charter_global_frozen (revision_6)
- **Freeze.** Frozen 2026-10-22, before the round-6 GT reveal and before I read the round-6 worklog body. The only worklog line I read was the last non-blank one: "REWORK round 6: gates 7/7 green".
- **Input read in full.** `audits/render_source/prepaid_maintenance_plans/render_r1.md`: the renderer's scan-first findings F1–F5, against charter 86c5c1247c76 — the one I graded CLEAN in revision_5.
- **Snapshot.** I ran `/tmp/erl0075_coord/snapshot.sh prepaid_maintenance_plans 6` myself, at 2026-10-22T07:31:24:
  - Gates: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
  - maintenance.extended.yaml 19abc6277d2f — changed.
  - task_tools.py 8d7ce9149aa2 — unchanged.
  - tasks/0.json c691d3388058; tasks/1.json dbddb991606c.
  - Views r6/0 5cbaeb91c0048187 and r6/1 42e56091547341f4 — unchanged.
- **Diff.** Field by field, against my saved revision_5 copy (ext_r5.yaml → ext_r6.yaml). The base section is byte-identical. Changes:
  - P1 rule, compute and compute_basis: scope sentence, replaced_by, `result` floor, replacement-credit sentence and factor tier text, prerequisite effect.
  - P2: replaced_by and scope sentence (later-day exit restated); `last_visit_reading` added to `usage_share` bindings.
  - P3: replaced_by and scope sentence (later-day exit restated); combination sentence.
  - P5: combination sentence and `result` floor.
  - P6: replaced_by and scope sentence (later-day exit restated).
  - No other compute changed. P4 is unchanged.
- **Accountability.** The renderer found five source defects after my revision_5 CLEAN. Three of them — F1 (no floor on P5), F2 (floor/credit order in P3), F5 (binding outside its factor) — are classes my rounds 1–5 did not sweep for: negative-result coverage and factor-binding completeness. F3 is the same issue as my revision_2 "F-ANCHOR closed" note. I closed it by assuming the gold anchor is the plan with the most recent total loss. The renderer is right that the rule never named which plan's entries are read, so the rule alone did not determine the read. My revision_2/5 closure of F-ANCHOR for P1 was premature. F4 is a C13 member I missed: "keeps the base price" left the price undefined.

### render_r1 items — graded against the artifacts (revision_6)
- **F1 (P5 price can go negative): closed.**
  - The rule now states the floor and where it falls: "…credits that apply are then added together and subtracted from that reduced price; a result below 0.00 is 0.00, so the credits never make the price negative; the retail plan price is rounded half up to the cent only at the end."
  - The compute matches: `RND(MX(0, retail_basis_price * (1 - rewards_rate) - credit_total) + 0.000000001, 2)`. The compute_basis quote is verbatim.
  - Probe — renderer's case (Essentials 2, new Toyota, replaced plan sold on a deal, cancelled today): 0.00 under both rule and compute. It was −71.71 before.
  - Same-class sweep for an unfloored negative final amount:
    - P1 had the same gap. The basis can approach 0 when FCM covers the plan term, and credits reach 150.00. The same floor was added in rule and compute: closed.
    - P2: floored at the end; P6: floored at the end; P3: floored and capped at the end.
    - P4: `miles_left` uses MX(0); starting reading ≥ 0; allowances ≥ 0.
    - No other member.
  - The floor yields 0.00, never an amount where nothing is owed, so the ruling is satisfied.
- **F2 (P3 floor/credit order): closed.**
  - The rule now reads: "Credits that apply are added to the rounded refund, and that sum is then floored at 0.00 and capped at purchase_price, in that order, at the end."
  - The compute matches: `MN(price, MX(0, RND(sum + 1e-9, 2)))`.
  - Probe — renderer's case (retail Plus 6, 5 net visits used, standard refund −50.75, credits 40.00): 0.00 under rule and compute. Flooring before the credits would create 40.00 where the plan owes nothing; that ordering is excluded both by the stated order and by the ruling.
  - Siblings already state "floored at 0.00 at the end" (P2 and P6). No other member.
- **F3 (P1 replacement credit is customer-wide in the rule but single-plan in compute): closed.**
  - The rule now names the record: "the total-loss cancellation entry of the Kessler Care Fleet 12-Visit plan named on the customer's most recent signed total-loss cancellation request (by request date, and on the same date by the time the request was registered)".
  - Both fields it relies on, `request_date` and `created_at`, are on the requests table and reachable through find_maintenance_cancellation_requests.
  - The compute's single-holding `COUNT` reads exactly that plan.
  - The renderer's probe (target entry 2 months old, another plan's entry under 1 month): the rule now names one plan, giving one reading.
  - Same-class sweep for customer-wide rule wording over a single-holding COUNT/SUM/LATEST/MAX:
    - P5 `trade_cancellations` is keyed on "the replaced plan", which is named by the most recent sold/traded request.
    - P2, P3, P4 and P6 read "the plan's" own ledger.
    - No other member.
- **F4 (P1 out-of-scope price undefined): closed.**
  - The rule now reads: "…is outside this policy and is priced like every other fleet plan bought on its own: at plan_price_usd, less fleet_volume_discount_pct where the customer's active Kessler Care Fleet 12-Visit plans, including it, reach fleet_volume_min_plans, rounded to the cent."
  - The maintenance_evt_sale replaced_by now restates "every other fleet plan bought on its own is still priced at plan_price_usd (less fleet_volume_discount_pct where the fleet volume threshold is reached)". Both replaced_by texts are verbatim in the rule.
  - Same-class (C13) sweep over every scoped exit:
    - P2, P3 and P6 previously said only "a request processed on a later day [is] outside this policy". They now restate the in-force base refund verbatim: pro rata less fee; refund_method with no fee; retail value less fee. A latent member, closed in the same pass.
    - P4: "every other move keeps its expiration odometer".
    - P5: "every other retail plan bought on its own is still priced at plan_price_usd".
    - No remaining member.
- **F5 (`last_visit_reading` outside `usage_share`): closed.** It is now in the `usage_share` bindings.
  - Mechanical sweep: every plain compute binding whose only consumers are one factor's bindings, and which no factor baseline references, in all six policies. One structural hit: P4 `rep_vehicle`, consumed only by `starting_checkin`.
  - It is not a member in substance, so I record it as observation O6-1:
    - `rep_vehicle` is not a quantity. It is the replacement unit itself — the policy's scope object and the move tool's `replacement_vehicle_id` argument — defined in the scope sentence of the rule ("The replacement unit is the unit delivered on…"). It is not in factor or baseline text.
    - P4's baseline.rule refers to the same unit ("its odometer at delivery on that agreement").
    - The renderer listed P4 as clean.
- **Mechanical sweep (all six policies):** every compute_basis quote, baseline sentence, replaced_by and policy_source is verbatim in its rule; every superseded_clause is verbatim in its base rule; no factor reads another factor's binding; no factor id is a substring of a tool name. Tool bodies are unchanged and still enforce their docstrings (revision_3). The RND(x + 1e-9) form is kept, with MX inside: accepted under the ruling.
- **XF_recipe re-check of every changed sentence:**
  - A3: the order of non-commuting steps is now stated (P1, P3, P5).
  - A4: F5 closed.
  - B8: rule and compute agree two-way on floors, caps and order.
  - B12: F3 now uses the "key the read on a named record" route.
  - C13: scope exits restate in-force base content.
  - D15: the prerequisite effect text on P1 is consistent with the new read.
  - F22: realism of a 0.00 sale price — observation O6-2.
    - P5 can now sell a plan at 0.00 when FCM covers almost all of the plan's term.
    - Example: Essentials 2 on a new Toyota, where the plan's useful term is about one month after factory coverage ends.
    - Base sale eligibility permits that sale. A 0.00 price after loyalty and trade credits is a plausible promotional outcome, and the base charter (not this difficulty's policies) decides whether such a sale is offered.

### findings (revision_6)
- No open RED. All five render_r1 items are closed, with their same-class members closed in the same pass. F-EPS, F-HALFUP, F-PAYTYPE, F-UNREACH and F-FIRST stay closed.
- New observations: O6-1 (P4 `rep_vehicle` is the scope object, defined in the scope sentence) and O6-2 (0.00 retail sale price). O2-1 to O2-6, O-3 and O-4 carry forward.

## closing_checklist (revision_6)
- Both tasks pass all four relationships (0.md and 1.md, revision_6). Gold values (43130, 498.96, 331.89, 515.57, 421.05, 269.50) equal my independent derivation.
- All five render_r1 items (F1–F5) are graded closed against the artifacts, and their same-class members are closed too: the P1 floor, and the later-day exits of P2, P3 and P6.
- Every earlier RED id stays closed.
- The step-4 checklist items of revision_5 still hold on the final form:
  - Scopes are disjoint and complete.
  - The graph is acyclic.
  - Tree depths and owner=user roots are as before.
  - Factor counts, labels, realism and weight are as before.
  - The uuid8s are frozen.
  - Tool bodies enforce their docstrings.
  - Rounding is within the ruling.
- Gates: re-run on the final form by the round-6 snapshot I ran at 2026-10-22T07:31:24, 7/7 OK.
- Worklog round-6 claims, checked against the artifacts: each item holds as stated, including the class sweep of scoped exits.

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN

---

## revision_7

### charter_global_frozen (revision_7)
- **Freeze.** Frozen 2026-10-22, before the round-7 GT reveal and before reading the round-7 worklog body. The only worklog line read was the gate line: "REWORK round 7: gates 7/7 green".
- **Input.** KB revision_2 source items S-0a, S-0b and S-1a, from `audits/policy_kb/prepaid_maintenance_plans/_difficulty.md` (read in full).
- **Snapshot.** I ran `/tmp/erl0075_coord/snapshot.sh prepaid_maintenance_plans 7` myself at 2026-10-22T12:37:08:
  - Gates: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
  - Hashes: maintenance.extended.yaml 19abc6277d2f; task_tools.py 8d7ce9149aa2; tasks/0.json 5e2cd8109130; tasks/1.json f6c9983b0a96.
  - Views: r7/0.view.json 96cd0b9802f6b7f9; r7/1.view.json 87d75107acafef70. Both changed: this is a seed-only round.
- **Charter and tools byte-identical.** `cmp` of maintenance.extended.yaml against my saved revision_6 copy (ext_r6.yaml) shows no difference, and task_tools.py is still 8d7ce9149aa2. Every charter-global section of revision_6 therefore carries forward by reference.
- **Seed diff, r6 → r7 views.** frozen_time and both personas are unchanged.
  - Task 0, purchase deal 4340069a (KCV-26-30418, closed):
    - The trade-in fields are cleared: trade_in_allowance 21500.00 → 0.00, appraisal date and odometer emptied.
    - 8 purchase_transactions are added.
  - Task 0, service: 1 service_ro_lines credit is added, and service_accounts.open_balance changes 676.77 → 672.60.
  - Task 1: purchase deal cf335dda hold_expires_date changes 2023-03-18 → 2023-03-16.

### S-items graded against the artifacts and the owning products' published docs (revision_7)
- **S-0a: closed.**
  - **The booked row.** An early_payment_discount credit of 4.17 on RO 362877, line A, source_line_id 9d0a3f8b (the invoice's latest customer-pay labor charge), dated 2026-09-30, pay_type customer_pay.
  - **Recomputed from docs/service:**
    - Invoice date: the latest labor line date, 2026-09-15.
    - Payment: ACH, 148.11 on 2026-09-30, which pays the invoice in full (charges 148.11 less payments 148.11 = 0).
    - Window: Net 30 by ACH is 15 days (fleet_ach_payment_discount_window), and 09-15 → 09-30 is 15 days, so it is inside.
    - Rate:
      - The unit 60f24b70 was bought on a closed Fleet VPA (4340069a) on a Net 30 account, which sets 2.5 % (fleet_vehicle_purchase_discount_rate).
      - Tenure is 101 whole months (60 or more) at Net 30, which adds 0.5 % (fleet_account_tenure_discount_addition).
      - The prompt-payer addition is 0: only 1 payment falls in the last 12 months, against the 8 required.
      - The standing share is unreduced: the 2025-07-18 late fee is outside 12 months, and there is no returned payment.
    - Discountable total: labor 80.58 + parts 58.55 = 139.13 (no comeback, overage or goodwill credit). Labor exceeds credits by at least 10.00.
    - Result: 3.0 % × 139.13 = 4.1739, which rounds half up to **4.17**. It is booked against the latest labor line, which matches the doc.
  - **Ledger.** open_balance 672.60 equals all charges less all credits and payments (recomputed from the seeded lines: 672.60).
  - **No scored read moves:**
    - spend_total sums only labor and parts charges.
    - unit_labor_lines counts labor rows only.
    - relationship_lines on 60f24b70 goes from 5 to 6 lines, which is still > 0.
    - The check-in maximum on 60f24b70 stays 4870 (the credit row carries 4870).
    - Late-fee counts are unchanged.
- **S-0b: closed.** KCV-26-30418's ledger is now seeded and re-prices against the purchase charter:

| Date | Entry | Amount |
|---|---|---|
| 2026-07-29 | Reservation deposit (ACH; meets the 2500.00 fleet minimum) | 2500.00 |
| 2026-08-06 (contract date) | vehicle_price (= cash_price) | 52480.00 |
| 2026-08-06 | sales_tax (7.5 %) | 3936.00 |
| 2026-08-06 | title_registration_fee | 85.50 |
| 2026-08-06 | electronic_filing_fee (fleet; doc fee waived) | 18.00 |
| 2026-08-12 (delivery date) | deposit_applied, with its triggered deposit_transfer payment | 2500.00 |
| 2026-09-08 | ACH payment | 54019.50 |

  - Charges 56519.50 = payments 56519.50, so the balance is 0.00, which matches status closed on 2026-09-08.
  - Removing the trade-in fields is legal: since revision_2 no rule reads any trade field.
  - The persona's only statement about this deal ("replaced by the 2026 Transit the Commercial Vehicle Center delivered in August") stays true.
  - The P3 replacement-purchase bonus is unchanged. The 2026-10-03 Tacoma vehicle_price charge keeps the 1-month tier (30.00); the new 08-06 charge falls only in the 3-month window.
  - Fleet incentive: still not owed (2 units delivered in 2026, below the minimum of 5).
- **S-1a: closed.** hold_expires_date is 2023-03-16 = reserved 2023-03-11 + vehicle_hold_days 5 (New Vehicle Retail), with 0 extensions. The contract date 2023-03-15 is inside the hold. No computation reads the field.
- **XF16 (owed at once) re-check on the new seed.** With S-0a booked, nothing is owed:
  - RO 363114 is unpaid, so no discount is owed on it.
  - Its due date is 2026-10-24, so no late fee is owed.
  - No fleet late balance is owed: the Tacoma is due 30 days after 10-09.
  - No incentive is owed.
- **XF20 (cross-category seeds).** The new rows are states the owning charters can produce, priced with their formulas, and the ledgers are complete.

### findings (revision_7)
- No open RED. S-0a, S-0b and S-1a are closed. Every earlier RED id stays closed. Observations carry forward.

## closing_checklist (revision_7)
- Both tasks pass all four relationships (0.md and 1.md, revision_7).
- The seed-only items S-0a, S-0b and S-1a are closed, checked against the artifacts and the owning products' published docs (docs/service early-payment documents; purchase charter).
- The charter and tool module are byte-identical to revision_6, so every checklist item from revision_6 still holds on the final form.
- Gates: 7/7 OK in the round-7 snapshot I ran (2026-10-22T12:37:08).
- Gold is unchanged and matches my independent derivation: 43130, 498.96, 331.89, 515.57, 421.05, 269.50.
- The persona is consistent with the seed. Nothing regressed.
- The worklog's round-7 claims hold against the artifacts.

VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN
