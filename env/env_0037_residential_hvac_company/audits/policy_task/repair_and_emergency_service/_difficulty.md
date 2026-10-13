# Policy-task audit — repair_and_emergency_service / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (erl-task-policy-audit), not the author of the artifacts.
- Freeze time: 2026-10-05T15:46Z (written before any task's GT was revealed; contains nothing derived from a revealed GT).
- Frozen inputs (sha256, re-checked against `/tmp/erl37/views/repair_and_emergency_service/charter.sha256`, all match):
  - `tasks/repair_and_emergency_service/service.extended.yaml` 4357430a29f21f6332aed156c9a9849d8189ddbf51133ee9aa7a6c0dfdf4c23a
  - `tasks/repair_and_emergency_service/task_tools.py` b2417a588c24cb6a70d355d6e7beeabf517e216d7e62e21368c3e3761886be53
  - masked views `task_0.masked.json` 04797b9e…f2b8d0, `task_1.masked.json` fd43bd73…ae07e (frozen_time, user_scenario, initial_state only)
- Fields permitted: blueprint (`blueprint.yaml`, `db_schema.json`, `share_tools.py`, `products/*.yaml` tier parameters), the extended charter, the tool module, the masked views.
- Fields masked (unread at freeze): `evaluation_criteria`, `computations`, `db_closure`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`; tasks/*.json were not opened; no recursive search was run over `env/` or `tasks/`.
- Entry conditions (Step 0): gate snapshot supplied (`/tmp/erl37/gates/repair_and_emergency_service.snapshot.txt`: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK); masked views and their hashes supplied. check_traceability deferred by the coordinator (KB not yet published) — noted, not an input defect of this audit.
- Base copy check: lines 1–1246 of the extended charter are byte-identical to `blueprint/products/service.yaml` (`diff` empty).

### policy_conflict_scan

Seven extended policies, all of category service, each with its own target tool:

| policy | trigger | computes | target_tool (owner) | prerequisite edges |
| --- | --- | --- | --- | --- |
| service_ext_refrigerant_allowance | state_due | amount | post_refrigerant_allowance_39aa6c52 (agent) | [] |
| service_ext_on_time_credit | state_due | amount | post_on_time_credit_a011cbd0 (agent) | [] |
| service_ext_late_payment_charge | state_due | amount | post_late_payment_charge_b790dc9b (agent) | -> on_time_credit, -> refrigerant_allowance (value_input, l_bal) |
| service_ext_past_due_installment | on_request | amount | pay_past_due_installment_4c600ae8 (user) | -> late_payment_charge (value_input, p_bal) |
| service_ext_member_premium_discount | state_due | amount | post_member_premium_discount_f1d91bca (agent) | [] |
| service_ext_courtesy_discount | state_due | amount | post_courtesy_discount_1179d4e9 (agent) | [] |
| service_ext_special_order_release | on_request | amount | pay_special_order_deposit_ccffba41 (user) | -> member_premium_discount, -> courtesy_discount (value_input, d_open) |

Overlapping subjects: four policies write `service_discount` lines, each on a distinct line_type (member_refrigerant_allowance, late_arrival_credit, member_premium_discount, discount_program); two write `service_payment` (past-due installment, special-order release) on distinct situations (past-due balance > 30 days vs. a call whose approved repair waits for a special-order part); one writes `service_charge` (late_payment_charge). No two policies govern the same quantity on the same line.

Shared balance: on_time_credit's result is capped by "the balance owing on the invoice when it posts" (t_open = ticket_balance), so its value depends on whether refrigerant_allowance has already posted — the two are parallel parents of late_payment_charge. The order between them matters only when the cap binds (ticket_balance after the other credit < on-time amount); a per-task check is required (task files, problem_chain).

Time anchors: late-payment days anchored on completed_date (day 0); past-due >30 days on completed_date; tenure / install / window counts on "the date of handling"; on-time lateness on scheduled_date + arrival_window vs arrived_at. No conflicting anchors.

Cross-category read boundaries: every cross-category read is declared in `cross_category` (plan, install, warranty, filter); none writes another category.

Scopes: the prerequisite graph has two connected components — {past_due_installment, late_payment_charge, on_time_credit, refrigerant_allowance} and {special_order_release, member_premium_discount, courtesy_discount}. With M=2 these are the only two trees that cover all seven policies with disjoint scopes; task 0's persona raises a past-due payment arrangement (component 1) and task 1's persona raises a special-order release payment (component 2), so the claimed scopes are mutually exclusive and jointly complete (confirmed against charter_scope only after reveal, in the task files).

### rule_compute_equivalence

Swept every compute binding against its `compute_basis` quotation (all quotations are verbatim substrings of the rule; every baseline.rule sentence is a sentence of the rule — checked mechanically with whitespace normalisation) and every rule sentence back against compute.

- refrigerant_allowance: tier pounds, five additions, min with billed pounds, 1-dp rounding of pounds, single 2-dp rounding of value — all implemented. Bindings r_freq, r_renew, r_install_status, r_unit_contract, r_filter_status, r_filter_merv carry no compute_basis entry (lookup intermediates; the sentences that use them are quoted under r_upkeep_count / r_install_lbs / r_contract_lbs / r_filter_lbs). Observation only.
- on_time_credit: grace ladder, 0/60/120-minute cut-offs, later-day test, level ladder, comfort addition, cap at ticket_balance, rounding before the addition — implemented. Evening-window 120-minute cut-off is the string 'T24:xx' (lexically later than any same-day time; arrival after it is on a later day and caught by t_day_after) — no divergence.
- late_payment_charge: **divergence.** Rule: "the charge for every period counted **and not yet charged** is posted together as one late-payment charge line". Compute: `l_periods: (int((l_days - l_grace - 1) / l_period_len) + 1) if l_days > l_grace else 0` and `l_raw: RND(l_bal * l_rate / 100 * l_periods * l_relief, 2)` — no binding subtracts periods already charged (no read of existing late_payment_charge lines). Same situation, two conclusions: a call that already carries a late_payment_charge for period 1, handled on a day when period 2 has started — rule charges 1 period, compute charges 2. (finding F-G1)
- past_due_installment: front amount, installment count, extras, minimum, single rounding of the share — implemented; "a smaller balance is paid in one installment" implemented as p_n = 1.
- member_premium_discount: standard pct (holiday vs after-hours), five additions, 100-pct ceiling, single rounding — implemented.
- courtesy_discount: implemented; the enrolment-in-a-courtesy-program condition is not in compute (it is the base eligibility `courtesy_program_on_file`, inherited) — no divergence.
- special_order_release: **divergence.** Rule: "For a member whose call concerns a unit with a **completed** Comfort Club tune-up on record, the deposit … is multiplied by 0.75; for a member whose call concerns a unit with no Comfort Club tune-up on record, it is multiplied by 0.9". Compute: `d_unit_visits: XCOUNT('plan','plan_service_entries', event_type='plan_tuneup_visit', equipment_id=F('equipment_id'))` — no `entry_reason='completed_visit'` filter, while `db_schema.json` plan_service_entries.entry_reason admits `no_show_forfeit` and `late_cancel_forfeit` on plan_tuneup_visit rows (plan.yaml line 608). Same situation, two conclusions: a member's unit whose only plan_tuneup_visit row is a no_show_forfeit — rule ×0.9, compute ×0.75. (finding F-G2)
- special_order_release, minor: the rule's second-tier wording "a unit with no Comfort Club tune-up on record" (not "no completed tune-up") leaves a unit with only forfeited visits in neither tier as stated; same root as F-G2.

### action_binding_and_uuids

- Seven `(target_tool, computes)` pairs, each claimed by exactly one policy; every target_tool exists in task_tools.py with the owner the charter implies (5 agent writes, 2 user payments).
- uuid8 tails 39aa6c52, a011cbd0, b790dc9b, 4c600ae8, f1d91bca, 1179d4e9, ccffba41: pairwise distinct, no shared prefix, no sequence or adjacency pattern — consistent with independent generation.
- Function bodies: each tool creates exactly one service_lines row and adjusts ticket_balance by the amount passed; none reads eligibility, existing lines, prerequisites or amounts (module docstring: "No tool checks eligibility, prerequisites or amounts"). Confirmed by reading every body.
- Docstrings name no other tool, no policy id and no sequence position among writes. Each Args entry says an id is "read from the service call lookup before the call" — the word "before" orders a read against this tool's own invocation, not two problems' writes. Observation O-G1 (no consequence).

### prerequisite_graph

- Every extended policy carries `prerequisite` (four are `[]`).
- Edges: late_payment_charge -> on_time_credit; late_payment_charge -> refrigerant_allowance; past_due_installment -> late_payment_charge; special_order_release -> member_premium_discount; special_order_release -> courtesy_discount. Every `problem` is an extended policy id of this file, none a base policy, none self; graph acyclic (two trees, depth 2 and 1).
- Every `policy_source` is a verbatim sentence of the blocked policy's own rule (normalised-whitespace substring check: 5/5).
- `form: state` on all five edges; no `fallback_reason` key on any (correct for state form).
- `resolved_by` equals the depended-on policy's target_tool on all five edges; each tool's effect lowers/raises ticket_balance and writes the line the sentence names.
- `kind: value_input`, `gate` names exist in the blocked compute (l_bal ×2, p_bal, d_open ×2). l_bal and p_bal are `F('ticket_balance')` (moved by the tool's balance update); d_open sums service_lines by event_type (moved by the new service_discount row). Effects hold.
- `condition` texts restate the sentence at the same scope (late-arrival credit owed; every refrigerant line of an active member's call; every charging period past the grace; member's premium line; courtesy customer's tune-up line). No strengthening/weakening found. No authoring-viewpoint wording.

### prerequisite_sentences

| blocked policy | sentence (verbatim) | connective | waited-on state (record-visible) | sole write producing it |
| --- | --- | --- | --- | --- |
| late_payment_charge | "No late-payment charge is figured until the invoice of a call whose technician arrived after the end of the booked window and the arrival grace carries the late-arrival credit owed on it." | until | a late-arrival credit line on the invoice | post_on_time_credit (only tool writing late_arrival_credit) |
| late_payment_charge | "The late-payment charge is fixed only after every refrigerant line on an active member's call carries the member refrigerant allowance line owed on it." | only after | a member refrigerant allowance line naming each refrigerant line | post_refrigerant_allowance (only tool writing member_refrigerant_allowance) |
| past_due_installment | "The first installment of a payment arrangement is not taken until the invoice carries a late-payment charge for every charging period that has run past the customer's late-payment grace." | not … until | late-payment charge line(s) covering the periods | post_late_payment_charge (only tool writing late_payment_charge) |
| special_order_release | "The special-order deposit payment is taken only after the after-hours premium line on a member's call carries the member premium discount line owed on it." | only after | member premium discount line naming the premium line | post_member_premium_discount (only tool writing member_premium_discount) |
| special_order_release | "No special-order deposit payment is taken until the paid tune-up line of a courtesy-program customer's call carries the courtesy discount line owed on it." | until | courtesy discount line naming the tune-up line | post_courtesy_discount (only tool writing discount_program) |

Four-point test: each joins the blocked policy's own result to a state with an ordering connective; each state is named in table/finder words (invoice, line, credit, discount, charge) with no actor and no tool; none names a tool, policy id, snake_case token or row id (mechanical snake_case scan of all seven rules: none); scope matches the edge condition. The depended-on rules do not restate the sentences (checked: no extended rule mentions another policy's id/tool, and none of the depended-on rules mentions late payment, installments or special orders).

Derivations (sentence + records + depended-on rule -> resolving action, single reading):
- "late-arrival credit owed on it" -> on_time_credit's rule is the only rule that defines an amount for a late-arrival credit line naming the diagnostic fee line -> post it. "the arrival grace" in the sentence is the grace defined in that same rule.
- "member refrigerant allowance line owed" -> refrigerant_allowance's rule defines "one member refrigerant allowance line naming the refrigerant line and the agreement" -> post it.
- "late-payment charge for every charging period … past the customer's late-payment grace" -> late_payment_charge's rule defines grace, charging period and the single line -> post it.
- "member premium discount line owed" -> member_premium_discount's rule -> post it.
- "courtesy discount line owed" on "the paid tune-up line" -> courtesy_discount's rule (tune-up line) -> post it.

Cross-problem orders in rules that ground no declared edge: none in the extended rules. Base rules carry two order statements — service_evt_coverage_credit ("discounts first, protection contract coverage next, Comfort Club covered repairs last") and service_evt_discount_stacking ("coverage credits are applied only after every discount on that line") — neither touches a policy of this charter's trees (no coverage-credit write exists in this difficulty) and no tree rests on them. service_payment_and_collections' "a call closes … once every discount and coverage credit … has been posted" governs a system transition, not a write of this charter. Observation O-G2.

### override_declarations

Sentence-by-sentence against each policy's `base_policy_refs` (finding half only):

- refrigerant_allowance: member_benefits' allowance sentence ("counted across all of the member's calls in the current term") handled differently (per call, plus additions) — declared. member_benefits "active … on the date the charge line posts" followed; "never applied retroactively" followed; discount_stacking "a line's discounts and coverage together never exceed its charged amount" followed (allowance ≤ refrigerant line by construction: covered pounds ≤ billed pounds at billed price). dispatch_fees, diagnostic_credit, repair_guarantee, late_arrival_credit: no sentence governs the allowance quantity — followed.
- on_time_credit: late_arrival_credit's earning condition (grace) — declared; amount sentence ("late_arrival_credit_usd … never below zero") — declared; discount_stacking's per-line cap — declared (the credit now measured against the whole invoice). "Only one on-time credit per call", "rescheduled after dispatch … earns no credit", "separate from … response-guarantee credit" — followed (not overridden, inherited).
- late_payment_charge: payment_and_collections' grace sentence and per-charge sentence — declared. "rounded to the cent half up and never less than late_payment_charge_min_usd" restated in the replacement rule. "A balance that is owing only because a protection contract claim or a Comfort Club covered repair is still being decided accrues no late-payment charge" — not overridden, inherited (per-task check). Other refs (one_open_call, dispatch_fees, flat_rate, tuneup, repair_guarantee, cancellation) govern no late-charge quantity — followed.
- past_due_installment: "The invoice is due payment_due_days after completion" — declared. "Payments are applied to the invoice as a whole" — followed.
- member_premium_discount: dispatch_fees' premium-discount clause — declared. "The courtesy discount program never applies to … the premium" — followed.
- courtesy_discount: discount_stacking's courtesy clause — declared (replacement limited to tune-up lines; "courtesy discounts on repair lines are settled as before" points back to the superseded base text for repair lines — observation O-G3, merged semantics still unique: repair lines keep the base treatment). "applies only in classes where discount_program_applies is true" followed (c_std_rate).
- special_order_release: flat_rate's special-order deposit sentence and payment_and_collections' due sentence — declared.

Disguised forms: no anonymous intermediate, 0/1 multiplier or dropped branch found against base. No undeclared override.

### factor_ladders

| policy | factor | label | decides | tiers | multi-source tier(s) | x-difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| refrigerant_allowance | consecutive_term_pounds | parameter | r_loyalty_lbs | 3 | no (one plan row) | plan |
| | maintenance_count_window | method | r_upkeep_count | 3 | no (one plan row: billing_frequency + auto_renew) | plan |
| | maintenance_count_pounds | parameter | r_upkeep_lbs | 3 | no | (null; reads plan entries) |
| | harbison_installation_pounds | parameter | r_install_lbs | 3 | no | install |
| | protection_contract_pounds | parameter | r_contract_lbs | 3 | tier 2 (call's unit lacks + another unit holds) | warranty |
| | filter_subscription_pounds | parameter | r_filter_lbs | 3 | no | filter |
| on_time_credit | arrival_grace | parameter | t_grace | 3 | no | plan |
| | lateness_multiplier | method | t_mult | 3 | no | — |
| | credit_level | parameter | t_level | 3 | yes, both tiers (plan agreement + warranty contract on call's unit) | warranty |
| | comfort_call_addition | parameter | t_bonus | 3 | tier 1 yes (ticket symptom + plan tier); tier 2 single | plan |
| late_payment_charge | late_payment_grace | parameter | l_grace | 3 | yes, both tiers (agreement + billing entries) | plan |
| | charging_period_length | parameter | l_period_len | 3 | no | plan |
| | late_payment_rate | parameter | l_rate | 3 | yes, both tiers (agreement + billing entries) | plan |
| | tenure_relief | method | l_relief | 3 | no | plan |
| past_due_installment | installment_count | parameter | p_count | 3 | no | plan |
| | filter_subscriber_installments | parameter | p_extra | 3 | no | filter |
| | arrangement_minimum | parameter | p_min | 3 | tier 2 only | warranty |
| | up_front_amount | method | p_front | 3 | yes, both tiers (agreement + billing entries) | plan |
| member_premium_discount | enrollment_tenure_points | parameter | m_tenure_pts | 3 | no | plan |
| | prepaid_renewal_points | parameter | m_prepay_pts | 3 | no | plan |
| | tune_up_count_window | method | m_visits | 3 | no | plan |
| | tune_up_points | parameter | m_visit_pts | 3 | no | plan |
| | installation_points | parameter | m_install_pts | 3 | no | install |
| | filter_points | parameter | m_filter_pts | 3 | no | filter |
| courtesy_discount | consecutive_term_points | parameter | c_term_pts | 3 | no | plan |
| | installed_system_points | parameter | c_install_pts | 3 | no | install |
| | shipment_count_window | method | c_ship_count | 3 | no | filter |
| | shipment_points | parameter | c_ship_pts | 3 | no | filter |
| | protection_scope_points | parameter | c_contract_pts | 3 | no | warranty |
| | dues_payment_points | parameter | c_pay_pts | 3 | yes, both tiers (agreement + billing entries) | plan |
| special_order_release | deposit_rate_by_scheduling | parameter | d_rate | 3 | no | plan |
| | installation_price_points | parameter | d_install_off | 3 | no | install |
| | protection_runway_points | parameter | d_contract_off | 3 | no | warranty |
| | dues_payment_history_points | parameter | d_dues_off | 3 | yes, both tiers | plan |
| | unit_enrollment_multiplier | method | d_mult | 3 | yes (agreement + service entries on the ticket's unit) | plan |

Structure checks passed: every factor's bindings are disjoint within its policy; every `decides` is an input binding, never `result`; every ladder has three pairwise-disjoint tiers whose conditions and values are stated in the rule and implemented in compute (both directions); no two tiers of any ladder select the same value or method; every fall-through equals the factor's baseline and the baseline equals what `baseline.rule` states (standard values: class grace 15 min / class credit / class late-payment terms 30 d, 30 d, 1.5 % / single payment / tier premium pct / class courtesy pct / class deposit pct; additions/points/off/extra default to nothing; multipliers default to "as figured"); every `baseline.rule` sentence is a rule sentence; counts per policy are 4–6 factors with ≥2 `parameter`.

Structure checks failed:

1. **Mislabelled `method` factors (tiers substitute a number into one formula).**
   - on_time_credit.lateness_multiplier: "The on-time credit is the credit level multiplied by the lateness multiplier" — tiers 2 / 1.5 / 1 are numbers in the same product (`t_amount: RND(t_level * t_mult, 2) + t_bonus`).
   - late_payment_charge.tenure_relief: "The product of balance, rate and periods is multiplied by the relief factor" — tiers 0.5 / 0.75 / 1 in one product (`l_raw`).
   - special_order_release.unit_enrollment_multiplier: "the deposit figured at that rate is multiplied by 0.75 … 0.9 … taken as figured" — numbers in one product (`d_deposit`).
   - courtesy_discount.shipment_count_window: tiers "shipments of the last 24 / 12 / 6 months" differ only in the window length passed to one count (`XCOUNT(..., within_months=N)`).
   Struck as `method`, each of these four computations has **zero** honest `method` factors, below the floor of 1. (finding F-G3)
   Accepted as honest `method`: refrigerant.maintenance_count_window and member_premium.tune_up_count_window (fall-through switches from a rolling window to the current term's visits — a different counting basis; observation O-G4 that two of the three tiers still differ only by window length); past_due_installment.up_front_amount (tiers change which lines make up the up-front amount and therefore the algorithm).
2. **Unreal ladder conditions (conditions the line of business does not weigh for that quantity).**
   - late_payment_charge.charging_period_length: the length of the late-payment accrual period on a repair invoice is set by how the customer's Comfort Club dues are billed (annual 45 d / monthly 35 d / 30 d). The cadence of a different contract's dues has no bearing on how a repair invoice's monthly late charge accrues; no service contractor publishes a "1.5 % per month" late charge that accrues per 45 days because the customer pays a maintenance plan annually.
   - refrigerant_allowance.maintenance_count_window and member_premium_discount.tune_up_count_window: the look-back window used to count completed maintenance visits is chosen by the agreement's dues billing cadence (and, for the refrigerant allowance, by its auto-renew flag). How dues are billed is not a basis on which a business decides how far back to look at a member's maintenance history.
   - past_due_installment.filter_subscriber_installments: the number of installments in a repair-bill payment arrangement is raised by the depth of the customer's FilterDirect filter (4-inch media cabinet +2, thinner +1). Filter cabinet depth is not something a contractor weighs when deciding how many installments to allow on a past-due repair balance.
   - Scope-restating conjuncts: refrigerant_allowance.consecutive_term_pounds ("agreement active and held …"), member_premium_discount.enrollment_tenure_points and prepaid_renewal_points ("active agreement …") carry an "agreement active" conjunct that holds of every customer who reaches those writes (both policies apply only to active members: "a customer without an active agreement has no refrigerant allowance"; "a customer without an active agreement receives no member premium discount"). The conjunct divides no customers.
   (finding F-G4)
   Recorded as observations, not red (bundle/loyalty perks a business could plausibly publish): filter grade adding refrigerant pounds or premium points, protection-contract or installation holding adding pounds/points/levels, installation staging/contract price, dues paid by card on file, contract runway (O-G5).
3. Counts per task (multi-source ≥1, cross-difficulty ≥1): component 1 has multi-source factors (credit_level, late_payment_grace, late_payment_rate, up_front_amount) and cross-difficulty factors (plan/install/warranty/filter); component 2 likewise (dues_payment_points, dues_payment_history_points, unit_enrollment_multiplier; plan/install/warranty/filter). Met at the structural level; whether they bear weight is per task.

### findings

- **F-G1 — SOURCE-POLICY RED (charter-global, rule/compute).** Symptom: late_payment_charge charges every counted period. Root cause: compute omits "and not yet charged". Evidence: rule sentence 4 of service_ext_late_payment_charge vs `l_periods` / `l_raw` (quoted above). Demonstrated consequence: in a situation where the call already carries a late_payment_charge for period 1 and period 2 has begun, rule -> 1 period charged, compute -> 2. Affected: service.extended.yaml, service_ext_late_payment_charge.compute (`l_periods`). Bears on: task 0 (its tree contains this policy) — consequence on task 0's world demonstrated (or not) in task_0.md.
- **F-G2 — SOURCE-POLICY RED (charter-global, rule/compute).** Symptom: special-order unit multiplier counts any plan_tuneup_visit row. Root cause: compute omits the "completed" filter the rule states. Evidence quoted above. Consequence: forfeited-only unit -> rule 0.9, compute 0.75. Affected: service_ext_special_order_release.compute (`d_unit_visits`). Bears on: task 1.
- **F-G3 — SOURCE-FACTOR RED (charter-global structure).** Four `method` labels on numeric multipliers / window lengths (on_time_credit, late_payment_charge, special_order_release, courtesy_discount); each computation is left with no honest `method` factor. Affected: `factors[].effect` of those policies and the rule sentences that define them. Bears on: task 0 (on_time_credit, late_payment_charge), task 1 (courtesy_discount, special_order_release).
- **F-G4 — SOURCE-FACTOR RED (charter-global ladder realism).** charging_period_length, maintenance_count_window, tune_up_count_window, filter_subscriber_installments carry conditions the business does not weigh for that quantity; consecutive_term_pounds, enrollment_tenure_points and prepaid_renewal_points carry scope-restating "agreement active" conjuncts. Bears on: task 0 (late_payment_charge, refrigerant_allowance, past_due_installment), task 1 (member_premium_discount).
- O-G1 docstring "before the call" (read ordering only). O-G2 base order sentences touching no tree. O-G3 courtesy "settled as before" points to superseded base text. O-G4 window factors whose two tiers differ only by length. O-G5 plausible bundle perks. O-G6 refrigerant_allowance compute bindings without their own compute_basis key (lookups only).

## closing_checklist

Written after both tasks' derivations were frozen (hashes recorded 2026-10-05T15:49:36Z) and their GT revealed. Nothing above this heading was changed after the reveal.

Status: **the difficulty does not close.** Step 4 requires all four relationships to PASS for every task, and the factors relationship is RED in both tasks.

| item | status |
| --- | --- |
| Per-task audit files match the tasks one-to-one (task_0.md, task_1.md) and sit next to this file. First revision, so there is no earlier revision. | done |
| Every comparison section carries a PASS | **no**: both tasks are SOURCE-FACTOR RED |
| All 7 extended policies are covered. Task scopes are disjoint (task 0: refrigerant_allowance, on_time_credit, late_payment_charge, past_due_installment; task 1: member_premium_discount, courtesy_discount, special_order_release; confirmed against charter_scope). Task tools and GT are closed. uuid8s are independent. | met |
| Each tree has 1–3 prerequisite problems (3 and 2), at least max(n−1,1) value_input edges (3/3 and 2/2), a user-owned root, and no cycle. The difficulty-wide graph is a DAG. | met |
| Each computation has a self-sufficient baseline with a definite fall-back number different from gold (0.00, 25.00, 18.42, 617.22 / 59.50, 14.90, 323.70). Every factor bears weight on its task's world. | met |
| Each computation has 4–6 factors with at least 2 parameter and at least 1 **honest** method | **no**: on_time_credit, late_payment_charge, courtesy_discount and special_order_release have none (F-G3) |
| Ladder conditions and outcomes are ones the line of business actually holds | **no**: F-G4 |
| At least one genuine near-miss per computation | **no**: past_due_installment in task 0 (T0-F3) |
| The proof's world assertions are verified | **no**: one installment sensitivity figure is 310.14, while the rule's half-up gives 310.15 (T0-F4) |
| Instantiation gates re-run on the final form | not run. The difficulty does not close, and this audit runs no gates (snapshot supplied by the coordinator). |

Post-reveal charter-level observation O-G7: every rule says "rounded … to the cent half up", but the compute primitive RND is `round(float(x), n)` (skills/erl-task-instantiate/scripts/check_compute.py:388). That is float rounding, not half-up. It moved one recorded sensitivity figure in task 0 and no gold value in either task. Any future world whose figure lands on a binary .xx5 tie will score a value the rule does not give.

Policy self-consistency at charter level: F-G1 and F-G2 are SOURCE-POLICY RED, each shown on a constructed situation. Neither has a consequence on the world of task 0 or task 1.

## revision_2

### charter_global_frozen (revision 2)

- Re-audit round 2. Auditor is the same independent auditor as round 1. Written 2026-10-05 ~17:04Z (shell clock), before any round-2 GT was read.
- Hash comparison against round 1:
  - service.extended.yaml changed: 4357430a…4c23a → **d4b4f03e91c18b14099fa289e9c460462a1a63263441062b91c667bbdcfc745b**. Every charter-global section is therefore re-derived in full below.
  - task_tools.py unchanged (b2417a58…6be53). The tool contracts, owners and uuid8 conclusions of round 1 (action_binding_and_uuids) carry forward, with this hash as the grounds.
  - Base copy still byte-identical to blueprint/products/service.yaml.
- Inputs: `/tmp/erl37/views_r2/repair_and_emergency_service/charter.sha256` (all hashes re-checked and matching) and the r2 gate snapshot `/tmp/erl37/gates/repair_and_emergency_service.r2.snapshot.txt` (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK; CACHE-DIFF INFO).
- Masked at freeze: round-2 GT fields of tasks/0.json and tasks/1.json.
- contamination_disclosure: round-1 GT of both tasks was read in round 1 (after the round-1 freeze) and remains in this auditor's memory, including round-1 scored values, factor_sensitivity figures and design_rationale. No round-2 GT field has been read. The reworker's claim list (item ids only) is known.

### policy_conflict_scan (r2)

- Same seven policies, same triggers, target tools and owners, same two prerequisite components.
- Line-type ownership is unchanged; no two policies govern one quantity.
- The shared-balance cap of on_time_credit still makes it order-sensitive against refrigerant_allowance only when the cap binds. Per-task check required.
- Cross-category reads are declared:
  - plan everywhere;
  - install for refrigerant, member premium, courtesy and special order;
  - warranty for refrigerant, on-time, installment, courtesy and special order;
  - filter for refrigerant, member premium, courtesy and special order.
- Past-due installment no longer reads filter; late payment no longer reads billing_frequency.
- Scopes remain mutually exclusive and jointly complete (two trees, M=2).

### rule_compute_equivalence (r2)

Mechanical checks:
- Every compute_basis value is a verbatim substring of its rule, **except** member_premium_discount `m_visits_term`. Its quotation "otherwise, the completed tune-up visits of the agreement's current term only" no longer occurs in the rule, which now says "for a member in the first term, the completed tune-up visits of the agreement's current term only".
- Every baseline.rule sentence is a rule sentence.
- Compute bindings without their own compute_basis key: on_time `plan_active`, `t_comfort`; past_due `plan_active`; member_premium `m_install_status`, `m_filter_status`, `m_filter_merv`. All are lookups whose sentences are quoted under the dependent binding.

Round-1 divergences:
- **F-G1 closed.** The rule now says: "Periods already charged are the periods counted, in the same way, as of the posting date of the call's latest late-payment charge line, and only the periods counted beyond them are charged now." Compute implements this with `l_last_charge` (LATEST late_payment_charge posted_date), `l_elapsed_last`, `l_periods_charged` (the same convention) and `l_periods = MX(0, now − charged)`. The rule and compute now agree on the round-1 counter-example.
- **F-G2 closed.** `d_unit_visits` now filters `entry_reason='completed_visit'`, and the rule's second tier now reads "no completed Comfort Club tune-up on record".

New logic:
- on_time `t_base` (10 % / 5 % of repair labor charges, half-up, floored at the class credit, else class credit) is implemented as stated.
- late_payment `l_convention` / `l_periods_now` implement the three counting conventions:
  - completed: `int(e/30)`;
  - prorated: `int(e/30)` + 0.5 if a remainder exists;
  - started: `int((e−1)/30)+1`.
  The convention is chosen by payments over charges on the call.
- past_due `p_ledger` and `p_extra` are implemented as stated.
- courtesy `c_products` and `c_bonus`: every award / the two largest / the single largest, chosen by the count of products held. Implemented as stated.
- special_order `d_products` and `d_off`: both / the larger / none. Implemented as stated.

Rounding:
- Every cent rounding now adds `K('half_up_nudge') = 1e-9` before RND (round-1 O-G7). The constant exists only in params and compute; it carries no rule sentence. It implements "half up" and adds no business basis (observation O-R2-1).
- The refrigerant pounds rounding (`RND(MN(...),1)`) has no nudge. The rule says only "rounded to one decimal place", without "half up". No divergence.

New wording observation O-R2-2 (late_payment_charge):
- Rule sentence 4, "Once the grace has passed, one charging period is counted for the first day past the grace and one more for each further full charging period …", states the started-period count with no condition.
- Rule sentence 10, "How the charging periods are counted depends on what the customer has paid toward the call: …", makes the count conditional. Its nothing-paid tier restates sentence 4.
- Read with "depends on" as the specific provision, the merged reading is unique: sentence 4 describes the standard (fall-through) count, and it is also the baseline.rule sentence.
- A reader who applies sentence 4 to everyone gets the started count for part-payers too. Per-task files quantify this second reading.
- The same general-then-combining pattern appears in courtesy_discount (each "adds N points" sentence vs the bonus-combination sentence) and special_order_release (each "takes N points off" vs the reduction-combination sentence). There too the combining sentence is explicitly about how the awards combine, and is read as governing.
- Recorded as an observation, not red: the specific sentence names the very quantity, and the general sentence is reproduced verbatim as its own fall-through tier.

### action_binding_and_uuids (r2)

- Carried forward from round 1 (task_tools.py unchanged).
- The `(target_tool, computes)` pairs in the charter are unchanged: seven distinct pairs, one per policy.

### prerequisite_graph (r2)

- The five edges are unchanged in endpoints, kind, gate, form and resolved_by.
- `policy_source` is still verbatim in each blocked rule (5/5). No fallback_reason; the graph is acyclic.
- Gates still exist (l_bal, p_bal, d_open). Effects still hold.
- New interaction: past_due's `p_ledger` is also moved by the late-payment charge line (a service_charge row). The edge's effect text names only p_bal and the up-front amount, but the late charge also raises p_ledger. That is an additional channel of the same edge, not a contradiction.

### prerequisite_sentences (r2)

- The same five sentences, unchanged, pass the same four-point test as in round 1.
- No extended rule mentions another policy's id or tool. No snake_case tokens appear in any rule (mechanical scan).
- The depended-on rules do not restate the sentences.
- The new late-payment sentence on periods already charged concerns the policy's own prior writes. It states no cross-problem order.
- The courtesy and special-order combination sentences state no order.

### override_declarations (r2)

- The overwrite blocks are unchanged in base targets. Every superseded_clause is still verbatim in the base, and every replaced_by is still verbatim in the extended rule.
- on_time's replaced_by now says "credit base" instead of "credit level". It is still verbatim in the rule.
- courtesy: the rule now restates the base treatment of repair lines itself ("on repair lines the courtesy program percentage still applies only to a line that receives no member repair discount, or in place of the member repair discount when the courtesy percentage is higher"). It no longer points back to superseded text. **O-G3 closed.**
- Sentence-by-sentence sweep: no new undeclared override.
  - The on-time credit base no longer equals base's late_arrival_credit_usd for members. That is within the declared amount override ("The on-time credit is the credit base multiplied by …").
  - Late-payment period counting is within the declared replacement of the per-charge clause.

### factor_ladders (r2)

| policy | factors (label) | honest method | notes |
| --- | --- | --- | --- |
| refrigerant_allowance | consecutive_term_pounds (p), maintenance_count_window (m), maintenance_count_pounds (p), harbison_installation_pounds (p), protection_contract_pounds (p), filter_subscription_pounds (p) | maintenance_count_window: the fall-through switches to the current term's visits | Window now chosen by enrollment length ("looks back as far as the membership reaches"), which the business plausibly weighs. "agreement active" conjunct removed. |
| on_time_credit | arrival_grace (p), lateness_multiplier (**p**, relabelled), credit_basis (m), comfort_call_addition (p) | credit_basis: percentage of repair labor charges vs a flat class credit, which is a different algorithm | credit_basis tiers are multi-source (agreement + contract on the call's unit). |
| late_payment_charge | late_payment_grace (p), period_counting_convention (m), late_payment_rate (p), tenure_relief (**p**, relabelled) | period_counting_convention: floor / floor+half / ceiling counts are different counting rules | charging_period_length removed (fixed 30 days). Convention chosen by the share of charges paid, which is a plausible good-faith condition. |
| past_due_installment | installment_count (p), balance_size_installments (p), arrangement_minimum (p), up_front_amount (m) | up_front_amount (unchanged) | filter_subscriber_installments replaced by balance size (≥1000 +2, ≥500 +1), which the business plausibly weighs. |
| member_premium_discount | enrollment_tenure_points (p), prepaid_renewal_points (p), tune_up_count_window (m), tune_up_points (p), installation_points (p), filter_points (p) | tune_up_count_window: the fall-through is term-only | Window now chosen by consecutive terms. Scope conjuncts removed from the tenure and prepay ladders. |
| courtesy_discount | consecutive_term_points, installed_system_points, shipment_points, protection_scope_points, dues_payment_points (p); bonus_combination (m) | bonus_combination: sum all / sum of the two largest / the single largest are different aggregations | shipment_count_window removed (fixed 24 months). Combination tiers are multi-source (four product records). |
| special_order_release | deposit_rate_by_scheduling, installation_price_points, dues_payment_history_points, unit_enrollment_multiplier (**p**, relabelled) (p); reduction_combination (m) | reduction_combination: both / the larger / none | protection_runway_points removed. Combination tiers are multi-source. |

Structure:
- Every policy has 4–6 factors with at least 2 parameter and exactly 1 method, and every method is honest. **F-G3 closed.**
- Bindings are disjoint within each policy. No `decides` is `result`.
- Every ladder has three tiers, stated in the rule and implemented in compute. No two tiers of a ladder share a value or method.
- Fall-through = baseline for every factor:
  - courtesy bonus_combination's fall-through and baseline are both "single largest award";
  - special_order reduction_combination's fall-through and baseline are both "no reduction".

Realism:
- **F-G4 closed.**
  - The dues-billing-cadence conditions are gone: charging period removed, windows now set by enrollment length or terms.
  - Filter depth no longer sets the number of installments.
  - No tier condition restates a policy's scope: refrigerant and member-premium ladders now condition on terms or tenure only.
- Remaining bundle and loyalty perks are kept as observations, as in round-1 O-G5.
- New observation O-R2-3: courtesy bonus_combination's baseline, "single largest award", is not literally what baseline.rule states for the bonus (no points at all). With every other factor at baseline it gives 0 = baseline.rule, and its fall-through equals its baseline, so it is not a straw man. Noted because, on its own, its substitution leaves one award in place.

Per-task structural requirements:
- Each component has multi-source factors:
  - tree 1: credit_basis, late_payment_grace, late_payment_rate, up_front_amount;
  - tree 2: dues_payment_points, dues_payment_history_points, bonus_combination, reduction_combination.
- Each component has cross-difficulty factors (plan, install, warranty, filter).

### findings (r2, charter-global)

- F-G1 closed; F-G2 closed; F-G3 closed; F-G4 closed; O-G3 closed; O-G6 closed for refrigerant_allowance (all of its lookups now carry a basis quotation).
- O-G7 addressed in compute through the nudge constant; observation O-R2-1.
- New observation O-R2-4: member_premium_discount compute_basis for `m_visits_term` quotes text no longer in the rule. The binding's semantics are covered by the `m_visits` quotation, so no consequence is demonstrable.
- New observation O-R2-2: late-payment general vs conditional period-count sentences (and the analogous combining sentences). Per-task quantification follows.
- No new SOURCE-POLICY or SOURCE-FACTOR red at charter level.

### closing_checklist (r2)

Written after both revision_2 derivations were frozen (17:04:55Z) and the round-2 GT was revealed (17:05:01Z). Nothing in revision_2 above this heading was changed after the reveal.

Status: **the difficulty does not close.** Task 0 remains SOURCE-FACTOR RED on T0-F3. Task 1 passes all four relationships.

| item | status |
| --- | --- |
| Per-task files match the tasks one-to-one. Round-1 text is preserved, and revision_2 is appended in each file. | done |
| Every comparison carries a PASS | **no**: task 0 is SOURCE-FACTOR RED (T0-F3) |
| Coverage: 7/7 policies; scopes disjoint (confirmed against charter_scope); tools closed; uuid8s independent (tools unchanged) | met |
| Trees: 3 and 2 prerequisite problems; all edges value_input; user-owned roots; acyclic; the difficulty graph is a DAG | met |
| 4–6 factors per computation with at least 2 parameter and 1 honest method; multi-source and cross-difficulty factors per task | met (F-G3 closed) |
| Ladder conditions and outcomes realistic; no scope-restating conjunct | met (F-G4 closed; plausible bundle perks kept as observations) |
| A genuine near-miss in every computation | **no**: past_due_installment in task 0 (T0-F3) |
| Every factor bears weight against an honest baseline, and the baseline alone gives a definite number different from gold | met in both tasks |
| Proof figures verified | met (T0-F4 closed; all round-2 figures recomputed and identical) |
| Instantiation gates on the final form | coordinator's r2 snapshot shows all OK; this audit runs no gates |

Round-1 items the reworker claimed as changed:
- Closed: F-G1, F-G2, F-G3, F-G4, T0-F4, O-G3, O-G6 (refrigerant), O0-2, O1-1; O-G7 addressed by the nudge constant.
- Not closed: **T0-F3**.

New in this round (observations only):
- O-R2-1: the nudge constant has no rule sentence.
- O-R2-2: general vs conditional period-count and combining sentences. Quantified in task_0.md; no second answer on task 1's world.
- O-R2-3: courtesy combination baseline.
- O-R2-4: stale `m_visits_term` compute_basis quotation.

No regression found.

## revision_3

### charter_global_frozen (revision 3)

- Re-audit round 3, same independent auditor. Written ~18:31Z (shell clock), before any round-3 GT was read.
- Hashes:
  - service.extended.yaml **changed** again: d4b4f03e… → cb8487adcefdfd5840a843730aa4c731a3499c4543defe3c0a6948c3e472a5ba. The charter checks are re-run in full below.
  - task_tools.py unchanged (b2417a58…). action_binding_and_uuids carries forward.
  - Base copy still byte-identical to the blueprint.
  - Views and hashes from `/tmp/erl37/views_r3/repair_and_emergency_service/charter.sha256`, all re-checked.
  - r3 gate snapshot: all 7 OK + CACHE-DIFF INFO.
- contamination_disclosure: GT from rounds 1 and 2 of both tasks is known to this auditor. Round-3 GT has not been read.

### re-run of the charter checks (r3)

- **Mechanical re-check of all seven policies.** Every compute_basis value is verbatim in its rule, and every compute binding now has a compute_basis key (O-G6 and O-R2-4 closed: member_premium `m_visits_term` now quotes "for a member in the first term, the completed tune-up visits of the agreement's current term only"). Every baseline.rule sentence is a rule sentence. Every prerequisite `policy_source` is verbatim (5/5) and every gate exists. Factor bindings are disjoint. Every superseded_clause is in its base, and every replaced_by is in the extended rule. No snake_case tokens appear in any rule. No rule names another policy's id or tool.
- **O-R2-1 closed.** Each of the seven rules now carries "An amount that falls exactly halfway between two cents is rounded up to the higher cent." The compute constant `half_up_nudge` now implements a stated rule sentence.
- **O-R2-2 closed.**
  - Late payment: sentence 4 now reads "Under the standard count, once the grace has passed, one charging period is counted …". The convention sentence now reads "Which count applies depends on what the customer has paid toward the call: … instead of the standard count; … instead of the standard count; when nothing has been paid toward the call, the standard count applies." The general sentence is now explicitly the standard, so the unconditional second reading is gone. The declared overwrite replaced_by was updated to the same wording, and it is verbatim in the rule.
  - Courtesy: each ladder sentence now says the customer "earns a courtesy bonus award of N points". Only the combination sentence ("How the courtesy bonus awards are added to the courtesy rate depends on …") adds anything to the rate.
  - Special order: likewise, "earns a deposit reduction of N points", and only the combination sentence takes reductions off.
  - None of these rules now has a general sentence that conflicts with a conditional one.
- **O-R2-3 closed.** Courtesy bonus_combination now has fall-through "with one or none, no bonus award is added" (compute `else 0`) and baseline `c_bonus: 0`, which is what baseline.rule states (the standard courtesy rate, with no points).
- **Other checks.**
  - The prerequisite graph, sentences, owners, tools and override targets are unchanged from revision_2, and those conclusions hold.
  - Factor structure is unchanged from revision_2 except the courtesy fall-through: 4–6 factors per policy, at least 2 parameter, exactly 1 honest method, multi-source and cross-difficulty factors in each component.
  - No two tiers of any ladder share a value or method. The courtesy ladder's "no award" fall-through differs from both the "two largest" and "all" tiers.
- **New findings.** No new SOURCE-POLICY or SOURCE-FACTOR red at charter level, and no regression.

### closing_checklist (r3)

Written after the revision_3 freeze (hashes recorded 18:31:13Z, with a timestamp correction re-hashed at 18:31:19Z, before the reveal) and the round-3 reveal (18:31:19Z).

Status: **the difficulty closes.** Both tasks PASS all four relationships.

| item | status |
| --- | --- |
| Per-task files match the tasks one-to-one. Revisions 1–3 are preserved in order, and each comparison section carries PASS. | met |
| 7/7 extended policies covered; task scopes disjoint (confirmed against charter_scope); task tools and GT closed; uuid8s independent and frozen (tools unchanged since round 1) | met |
| Trees have 3 and 2 prerequisite problems, all edges value_input (≥ max(n−1,1)); each root is owner=user and handed to the customer; acyclic; the difficulty graph is a DAG | met |
| Every computation has a self-sufficient baseline giving a definite number different from gold; 4–6 factors with ≥2 parameter and exactly 1 honest method; ladders of 3 distinct, realistic tiers stated in the rule; every factor bears weight; a record-level near-miss in every computation; multi-source and cross-difficulty factors seeded in each task | met |
| Proof figures (factor_sensitivity, baseline_result, load-bearing effects) recomputed and identical | met |
| Instantiation gates re-run on the final form | coordinator r3 snapshot: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK (CACHE-DIFF INFO). This audit runs no gates. check_traceability is still deferred to after KB publication, per the coordinator. |

Round-2 items the reworker claimed as changed: T0-F3, O-R2-1, O-R2-2, O-R2-3 and O-R2-4 are all verified closed.

Remaining observations, none of which bears on a red:
- bundle and loyalty perks (O-G5);
- docstrings saying "before the call" (O-G1);
- base rules stating order only on non-tree policies (O-G2).
