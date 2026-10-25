# Policy-task audit — meal_account_and_benefits / charter-global

## charter_global_frozen
- Frozen 2026-10-24T18:44Z, revision_1, auditor: independent policy-task auditor (not the instantiator).
- Hashes (sha256, first 16): `meals.extended.yaml` = e6b9691f697ad7bb, `task_tools.py` = 2b44be40b0fc568e; masked views 0.view.json = a92acd4c1ba36f60, 1.view.json = dd92f3b49aeb4c38 (all recomputed by the auditor, all equal to the coordinator snapshot).
- Read: blueprint.yaml, db_schema.json, share_tools.py (signatures), products/meals.yaml, products/enroll.yaml (cross-category owner charter), meals.extended.yaml, task_tools.py, the two masked views, audits/render_source/XF_recipe.md and owner_ruling.md.
- Masked / unread at the time of writing this section: tasks/0.json and tasks/1.json (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure), plan.md, worklog.md. Searches were scoped to named files; no recursive grep.
- Entry conditions (Step 0): gate snapshot /tmp/erl0078_coord/snap_meal_account_and_benefits_r1.txt shows EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; masked views and their hashes are supplied. Inputs are complete.
- Base copy: lines 1-946 of meals.extended.yaml are byte-identical to blueprint/products/meals.yaml (diff shows only the blank separator line 947).
- B5 sweep (scratch /tmp/audit_meal_account_and_benefits_0078/b5.py): every `compute_basis` quote, every `baseline.rule` sentence, every prerequisite `policy_source` and both `replaced_by` texts are verbatim in their policy's rule.

### policy_conflict_scan
Eight extended policies, all on School Nutrition meal accounts, all `computes: amount`:

| policy | tool (owner) | subject | object | base refs |
|---|---|---|---|---|
| meals_ext_prepayment_quote | deposit_meal_prepayment_ffe018a7 (user) | meals_deposit | the student's active account | deposits_and_returns, meal_pricing, unpaid_meal_charges |
| meals_ext_departed_charge_cover | transfer_departed_charge_cover_80639818 (agent) | transfer_out/in | inactive account of "a departed sibling" -> the student's active account | refunds_and_transfers, meal_pricing, unpaid_meal_charges |
| meals_ext_sibling_idle_netting | transfer_idle_sibling_balance_b810dc58 (agent) | transfer_out/in | another active account -> the active account with the largest unpaid charges | same |
| meals_ext_inactive_repayment | pay_inactive_meal_installment_c0dba3e7 (user) | meals_deposit | inactive account with unpaid charges | deposits_and_returns, unpaid_meal_charges |
| meals_ext_cep_balance_refund | refund_cep_meal_balance_19cb6a0f (agent) | meals_refund | active account at a CEP campus | refunds_and_transfers (2 overwrites), meal_pricing, unpaid_meal_charges |
| meals_ext_collection_repayment | pay_collection_meal_installment_be0f7285 (user) | meals_deposit | active account carrying a prior-year collection balance | deposits_and_returns, unpaid_meal_charges |
| meals_ext_departure_rollover | transfer_departure_rollover_b6d76228 (agent) | transfer_out/in | inactive account of a student who left for another state/country -> youngest active student | refunds_and_transfers, meal_pricing, unpaid_meal_charges |
| meals_ext_graduate_rollover | transfer_graduate_rollover_43099774 (agent) | transfer_out/in | graduate's inactive account -> active account with the largest unpaid charges | same |

Overlaps found:
- **Same inactive balance claimed by three policies (finding P-02).** The cover rule takes "the positive balance on the inactive account of a departed sibling" to "the student's active account" whenever "a prepayment is quoted for a student". "Departed" is never defined, and base lifecycle makes an account inactive "when the student withdraws from the district or graduates". The departure rollover takes the inactive balance of a student whose leaver reason is moved_out_of_state / returned_to_home_country "to the household's youngest active student". The graduate rollover takes a graduate's inactive balance "to the household's active account that carries unpaid meal charges (... the one with the largest ...)". The same inactive balance can fall under two of them at once, with a different recipient and a different amount (see findings).
- **Netting trigger vs prepayment edges (finding P-03).** The netting rule opens "When a sibling's departed-balance cover or prepayment is being worked out, the idle balance of each other active account of the household is netted first". That states a netting-before-prepayment order which the prepayment rule never states and no `prerequisite` edge declares.
- **Collection balance vs base allocation (finding P-01).** The collection policy's scope sentence ("still carries unpaid meal charges from an earlier school year") disagrees with its defining sentence (latest notice amount capped by today's unpaid charges) whenever the balance has gone back to zero or above since the notice. Base meals_unpaid_meal_charges says "Any deposit is applied to unpaid meal charges first". The same notice-amount carve-out is used by the cover and graduate rollover (`c_charges_taken`, `g_charges_taken`), and the CEP refund's prerequisite sentence relies on it ("whose year-end collection balance is not yet repaid").
- The trigger and time anchors otherwise agree: every policy evaluates on frozen_time with the same whole-calendar-month window sentence, which matches the DSL `MONTHS` (month-end rolls to the 1st of the next month). Cross-category reads are declared for `enroll` only (campus / status / grade_level / leaver_reason / withdrawal_date).
- Scope coverage: from the trees the charter states, task 0's world engages prepayment ← {cover ← netting, inactive_repayment}, and task 1's world engages cep_refund ← {departure_rollover, collection_repayment, graduate_rollover ← collection_repayment}. Together they cover all 8 policies with disjoint scopes. This is derived from the charter and the worlds; each task file checks it against its own world.

### rule_compute_equivalence
- All eight computes implement their rule sentence by sentence (B5 sweep clean). Equivalences checked: `LATEST(year_end_collection)` without a window vs "the latest such notice", where "such" means inside 12 months, is equivalent because the latest overall lies inside the window whenever any does. `r_limit_ever` has no window and its rule has none. `n_charged_lunches` counts paid/reduced/free lunch lines against "every reimbursable lunch ... served at no charge under the CEP".
- **Mismatch (P-06): meals_ext_collection_repayment `k_size_collection`.** Compute sizes the installments on the uncapped notice amount. The rule sizes them on "the year-end collection balance". The standard sentence admits two groupings: "the year-end collection balance in full, that is the unpaid amount stated on the latest year-end collection notice on the account, never more than the account's unpaid meal charges". In one, the cap belongs to the balance (k_basis). In the other, the cap belongs only to the payment. Compute follows the second grouping for the size (`k_size_collection`) and the first for the up-front part and the share (`k_basis`). In a world where unpaid charges are below the notice amount, the two readings give different installment counts.
- Rounding: every policy rounds half up once at the end with `RND(x+1e-9)`, which is the coordinator ruling. The milk tiers also round "two fifths of the milk-only price". 0.75 × 0.4 = 0.30 exactly in every variant, so the extra rounding point never changes a number (observation O-4).
- Base meals_meal_pricing prices a meal "by ... the pricing level of the account's campus". The lunch-charge readers (q_/c_/n_/g_) use the campus of the enrolled record, and `w_lunch_charge` uses the withdrawn record. The breakfast readers use `F('campus')`. Base meals_account_status makes the account campus follow the enrollment campus "from the same date", so a world consistent with base never splits them. Observation O-6.

### action_binding_and_uuids
- Each `(target_tool, computes)` is claimed by exactly one policy. The 8 tools are distinct and have random-looking, independent uuid8s (ffe018a7, c0dba3e7, 80639818, b810dc58, 19cb6a0f, be0f7285, 43099774, b6d76228). None shares a prefix or sequence.
- No tool body checks an eligibility, a status or a prerequisite. Bodies only validate a positive cent amount and the existence of the account ids, then `ctx.create`. Every write tool writes in its own body, and rounding uses the static `_MealMoney.cents` Decimal ROUND_HALF_UP helper (B4/B6 met).
- No docstring names another tool, a policy or a position in a sequence. The only ordering word is in deposit_meal_prepayment: "any unpaid meal charges are cleared first because the deposit simply raises the balance". It describes the balance effect and repeats base wording (observation O-2).
- The four transfer tools write identical row shapes (transfer_out + transfer_in, same-category trigger honoured, D4 met). The three portal tools write identical online_card meals_deposit rows. The record-level indistinguishability is the stated reason for the action-form fallbacks below.

### prerequisite_graph
Edges (`problem` → resolved_by, kind, form):
1. prepayment → departed_charge_cover (transfer_departed_charge_cover_80639818), value_input on q_balance, action
2. prepayment → inactive_repayment (pay_inactive_meal_installment_c0dba3e7), state_gate, state
3. departed_charge_cover → sibling_idle_netting (transfer_idle_sibling_balance_b810dc58), value_input on c_balance, action
4. cep_balance_refund → departure_rollover (transfer_departure_rollover_b6d76228), value_input on e_balance, action
5. cep_balance_refund → collection_repayment (pay_collection_meal_installment_be0f7285), state_gate, action
6. cep_balance_refund → graduate_rollover (transfer_graduate_rollover_43099774), state_gate, action
7. graduate_rollover → collection_repayment (pay_collection_meal_installment_be0f7285), value_input on g_balance, action

- Every policy has `prerequisite` filled in (`[]` for netting, inactive, collection, departure). Every `problem` is an extended policy id of this file. The graph is acyclic (two components; collection_repayment is reached twice inside the second, which is not a cycle). Every `policy_source` is verbatim in its own rule. `fallback_reason` is present exactly on the action edges. Value_input gates name real bindings (q_balance, c_balance, e_balance, g_balance), and each resolver's write moves that binding. State_gate edges 5 and 6 put the field `meal_transactions.event_type` in `gate`; the CEP refund policy has no eligibility block for them to point at (observation O-8, gates passed).
- `condition` texts match the sentences. Edge 2's condition ("a meals_deposit row dated the quote date") states the sentence's "repayment payment posted on the day of the quote" in record words.

### prerequisite_sentences
Four-point test, per edge:
- Every sentence joins the policy's own result to what it waits on with "only after" / "not ... until", names no tool, no policy id and no snake_case token, and has the condition's scope. Edge 2 names its closed set by kind ("each inactive account of the household whose unpaid meal charges are at least the online deposit minimum"), with the D2 de minimis carve-out stated in the sentence.
- State-form edge 2: the only write of this difficulty that posts a deposit on an **inactive** account is pay_inactive_meal_installment_c0dba3e7. deposit_meal_prepayment and pay_collection_meal_installment are both documented onto an **active** account, so one write brings the state about. "repayment payment" is a business word, not the finder word "deposit" (observation).
- Action-form fallbacks tested. Edges 1, 3, 4 and 6 are justified, because a sibling transfer in is indistinguishable from a household-requested one and the transfer may be zero. **Edges 5 and 7 are not justified**: the record-visible state "the account carries a repayment payment posted on the day of the refund/rollover" singles the write out exactly as edge 2 does in this same charter. pay_collection is the only write onto an active account dated today that is a repayment-plan payment, and the prepayment deposit belongs to a different tree. Recorded as observation O-1 naming that state.
- Depended-on rules restating the dependency: the netting rule's opening "is netted first" restates edge 3 from the depended-on side and adds an undeclared order against the prepayment (P-03). The cover rule's "When a prepayment is quoted for a student" is a trigger, not an ordering sentence.
- Derivations, one reading each, given the charter apart from P-01/P-03:
  - Prepayment sentence + the household's inactive accounts with unpaid charges ≥ 10.00 → the inactive repayment rule ("each repayment payment is the parent's own act ... through the district's online payment portal") → pay_inactive_meal_installment.
  - Prepayment sentence "every cover owed ... from the inactive account of a departed sibling" → the cover rule → transfer_departed_charge_cover. Its sentence "after the idle balance of each other active account ... has been netted" → the netting rule → transfer_idle_sibling_balance.
  - CEP sentence "every rollover owed to the account from the balance of a sibling who left for another state or country" → the departure rule → transfer_departure_rollover.
  - CEP sentence "repayment-plan payment due today on every other account ... whose year-end collection balance is not yet repaid" → the collection rule → pay_collection_meal_installment. This hop's scope is contested by P-01.
  - CEP sentence "every rollover owed from a graduate's inactive account" → the graduate rule → transfer_graduate_rollover. Its sentence "after the household has made the repayment-plan payment due today on the receiving account's year-end collection balance" → collection rule.

### override_declarations
Sentence by sentence against each `base_policy_refs` entry:
- **meals_deposits_and_returns** (prepayment, inactive, collection): s1 min/max per online deposit is followed (every result is clamped to 10.00–300.00 and the processor fee is never posted). s2 cafeteria methods: not touched. s3 "an inactive account takes deposits only to clear unpaid meal charges" is followed. s4 returned checks: not touched. s5 no checks after a return is followed (all three writes are online card).
- **meals_meal_pricing** (prepayment, cover, netting, cep, departure, graduate): s1 account-campus pricing differs only through the enrolled/withdrawn-record campus, which a base-consistent world never splits (O-6). s2 CEP override, s3 second meal and milk prices and s4 0.00 lines are followed. s5 not touched.
- **meals_unpaid_meal_charges** (all eight): s1–s5 are followed (no fee, interest or penalty in the repayment policies; notices are read as the base defines them). **s6 "Any deposit is applied to unpaid meal charges first, because it simply raises the balance."** meals_ext_collection_repayment handles this quantity differently. It keeps "the unpaid amount stated on the latest year-end collection notice" alive as a prior-year balance after later deposits have raised the balance to zero or above, and it splits today's unpaid charges into a "year-end collection balance" and a "current-year part" by that stale notice amount. `overwrite: []`, so this is an **undeclared override (P-01)**. The cover and graduate rollover carve-outs ("less the unpaid amount stated on the latest such notice ... because those charges are repaid under the collection plan") carry the same anonymous intermediate.
- **meals_refunds_and_transfers** (cover, netting, cep, departure, graduate): s1 and s5 are overwritten by the CEP policy and declared. Both `replaced_by` restate the in-force inactive-account content with refund_minimum and refund_processing_days, name their own scope, and appear verbatim in the rule (C1 met; no sibling overwrites, C2 n/a). s2–s4 are followed: transfers only to an active account of the household, never above the giving balance, unpaid charges never transferred, and "owed only from a balance at least the amount" in cover and graduate. s6 (close at zero, unclaimed fund) is not touched.
- **meals_account_status** (not in any ref list): s1 "Meals and items are rung up only on an account in status active." The departure rollover's premise "Meals from a student's last days of attendance can still reach the account from the point of sale after the student has left" contradicts it without a declared overwrite (C3; part of P-04).

### factor_ladders
Per policy (label; multi-source = every non-fall-through tier is an and/or over distinct records; X = cross_difficulty):

| policy | factors (label) | count P/M | multi-source | X |
|---|---|---|---|---|
| prepayment | quote_lunch_charge (P, X enroll), quote_added_meal (M), quote_serving_days (P, multi), quote_milk (P), quote_low_balance_buffer (P, multi) | 4/1 | 2 | 1 |
| cover | cover_charges_taken (M), cover_restore_days (P, multi), cover_restore_lunch (P, X), cover_restore_breakfast (M), cover_restore_milk (P) | 3/2 | 1 | 1 |
| netting | netting_keep_lunch (P, X), netting_keep_days (P), netting_keep_milk (P), netting_extra_keep (M), netting_check_hold (P, multi) | 4/1 | 1 | 1 |
| inactive | plan_size_installments (P), plan_relocation (P, X), plan_up_front (M), plan_payment_history (P, multi), plan_recency (P) | 4/1 | 1 | 1 |
| cep_refund | cep_refund_card_reversal (M), cep_refund_check_hold (P, multi), cep_refund_keep_days (P, X), cep_refund_keep_milk (P), cep_refund_keep_extras (M) | 3/2 | 1 | 1 |
| collection | coll_size_installments (P), coll_age (P), coll_payment_history (P, multi), coll_up_front (M, X), coll_current_charges (P) | 4/1 | 1 | 1 |
| departure | departure_check_hold (P, multi), departure_card_stays (M), departure_reserve_days (P, X), departure_reserve_lunch (P, X), departure_reserve_meal (M), departure_reserve_milk (P) | 4/2 | 1 | 2 |
| graduate | rollover_charges_taken (M), rollover_restore_days (P, multi), rollover_restore_lunch (P, X), rollover_restore_meal (M), rollover_restore_milk (P), rollover_buffer (P, multi) | 4/2 | 2 | 1 |

Structural checks:
- Every ladder has 3 tiers stated in the rule and implemented in its `decides` binding, with disjoint conditions as stated. No two tiers share a symbolic value. Binding sets are disjoint, and no factor `decides: result`.
- No factor reads another factor's binding (A1). Assembly lives in plain bindings with one generic order sentence per policy (A2/A5).
- Lunch-charge tiers coincide numerically on part of the domain: for reduced status the secondary and elementary lunch are both 0.40, and for every free status all three tiers are 0.00. Both worlds are Paid Meal Status (observation O-3).
- **A7 (rate × count with a zero baseline), finding F-01.** In each case below the per-day factors multiply a day count whose baseline is 0, so T2 fails: with every other factor at baseline, they never move the result.
  - cover: `result = c_restore_days * (c_lunch_charge + c_added_meal + c_milk_charge) + c_charges_taken` with c_restore_days baseline restore_days_none = 0. cover_restore_lunch, cover_restore_breakfast and cover_restore_milk fail.
  - graduate: same shape, g_restore_days baseline 0. rollover_restore_lunch, rollover_restore_meal and rollover_restore_milk fail.
  - departure: w_reserve_days baseline 0. departure_reserve_lunch, departure_reserve_meal and departure_reserve_milk fail.
  - cep_refund: `e_keep = e_keep_days * e_milk_keep + ...` with both baselines 0. cep_refund_keep_days and cep_refund_keep_milk each fail.
- **A3, finding F-02.** cover and graduate `baseline.rule` carry "When meals are restored, a restored day's standard charge is one reimbursable lunch at the elementary lunch charge of the student's meal status, with nothing added." Their baseline restores no day, so only the factors use the sentence.
- **Effect labels, finding F-03.**
  - Labelled `method` but only adding a different number per day (breakfast charge / second-meal price / 0 into "daily += x"): quote_added_meal, cover_restore_breakfast, departure_reserve_meal, rollover_restore_meal. With quote_added_meal struck, meals_ext_prepayment_quote has **no** honest `method` factor.
  - Labelled `parameter` but tier 2 changing the algorithm (`MX(0, k_current_part - k_current_limit)`, a subtraction and a floor, against tier 1's whole part): coll_current_charges.
  - Honest methods: cover_charges_taken, rollover_charges_taken (different record source plus a floor); plan_up_front, coll_up_front; cep_refund_card_reversal, departure_card_stays (sum of a window vs a single latest row); netting_extra_keep, cep_refund_keep_extras (a data sum vs a published constant).
- **Realism (F1/F2), finding F-04.** Each factor is judged on whether a Texas district publishes that dimension with those outcomes.

| factor(s) | verdict | why |
|---|---|---|
| quote_lunch_charge, cover_restore_lunch, netting_keep_lunch, departure_reserve_lunch, rollover_restore_lunch | real dimension | NSLP prices by level and CEP no charge, the base's own figures (two are struck under A7 regardless) |
| quote_added_meal, cover_restore_breakfast, departure_reserve_meal, rollover_restore_meal | plausible dimension | adding breakfast when the child eats breakfast; struck under F-03 or A7 |
| netting_check_hold, cep_refund_check_hold, departure_check_hold | plausible | hold on check deposits still inside the bank return period, longer after a returned check |
| plan_size_installments, coll_size_installments | plausible | repayment plans sized by debt |
| quote_milk, cover_restore_milk, netting_keep_milk, cep_refund_keep_milk, departure_reserve_milk, rollover_restore_milk | **invented share** | "one to three milk-only purchases add two fifths of the milk-only price to each day" is a fractional allowance no district publishes |
| quote_serving_days (15/10/5), cover_restore_days (5/3/0), rollover_restore_days (4/2/0), netting_keep_days (15/5/10), cep_refund_keep_days (by grade 03–05 / PK3–02 / other) | **invented allowance** | day counts keyed on notice counts or grade bands for a quote, a sibling transfer or a refund hold-back are not a published district schedule. "Restoring serving days" by moving extra money is not a district mechanism (a sibling transfer moves what the household asks or what is owed). A refund that keeps ten days of milk for grades 3–5 and nothing for grade 6 has no business basis |
| quote_low_balance_buffer, rollover_buffer | **invented** | "twice the low-balance threshold when no online card deposit posted" is padding; the threshold is a notice trigger, not a buffer the district adds |
| cover_charges_taken, rollover_charges_taken | **invented condition/outcome** | refusing to let the household's own departed-sibling balance pay charges equal to a returned check ("a returned check is repaid by the household itself") or a prior-year collection amount is not a district rule. The money is the household's either way, and the collection tier rests on P-01 |
| plan_relocation (+2 out of state/country, +1 other Texas district), plan_payment_history (±1), plan_recency (±1), coll_age (±1), coll_payment_history (±1) | **invented tapers** | installment counts adjusted by leaver reason, deposit/notice counts, months since inactivation or letter age are padding no district publishes |
| plan_up_front, coll_up_front | **one invented tier** | returned-check amounts due up front is real practice. "The part above the charge limit of the account campus's level (coll: of the campus on the current enrollment record) is paid up front" is not, and for coll it keys a prior-year debt on the student's current campus |
| coll_current_charges | **invented** | a prior-year collection plan that adds all current-year charges after a charge-limit notice, part of them after a negative notice, and none otherwise has no business basis |
| cep_refund_card_reversal, departure_card_stays | **condition not weighed** | reversibility of a card payment depends on its age, not on whether two or more were made in two months. The count-keyed split (all of two months vs only the latest) is not what a processor or district weighs |
| cep_refund_keep_extras, netting_extra_keep | **invented allowance** | keeping last month's à la carte total, or two second-meal prices, back from a refund or a transfer the household asked for |
| departure_reserve_days | **invented, contradicts base** | the "late-posting reserve" rests on meals reaching an inactive account, which base meals_account_status forbids (P-04) |

- Counts after striking A7, F-03 and F-04 members (survivors):
  - prepayment: quote_lunch_charge → 1 (needs 4; 0 method).
  - cover: 0.
  - netting: netting_keep_lunch, netting_check_hold → 2.
  - inactive: plan_size_installments → 1.
  - cep_refund: cep_refund_check_hold → 1.
  - collection: coll_size_installments → 1.
  - departure: departure_check_hold → 1.
  - graduate: 0.
  - Every computation is below 4 factors, 2 parameter and 1 method (finding F-05).
  - Surviving cross-difficulty factors: quote_lunch_charge and netting_keep_lunch (task-0 policies). Every cross-difficulty factor of task-1 policies is struck: cep_refund_keep_days (F-04 + F-01), coll_up_front (F-04), departure_reserve_days (F-04), departure_reserve_lunch (F-01), rollover_restore_lunch (F-01).

### findings
Each finding below is a charter-global defect. The affected task files carry the per-world demonstration.

- **P-01 SOURCE-POLICY RED: undeclared override of base allocation; collection balance defined against its own scope sentence.**
  - Symptom: meals_ext_collection_repayment applies "When an active meal account still carries unpaid meal charges from an earlier school year for which a year-end collection notice was sent". Yet its standard figure is "the unpaid amount stated on the latest year-end collection notice on the account, never more than the account's unpaid meal charges", and "the part of the account's unpaid meal charges beyond the year-end collection balance" is called current-year.
  - Root cause: the notice amount is treated as still outstanding however much has been deposited since. Base meals_unpaid_meal_charges s6 says "Any deposit is applied to unpaid meal charges first, because it simply raises the balance", and `overwrite: []`.
  - Demonstrated consequence: when the balance went to zero or above after the notice, the scope sentence says no prior-year charges remain, while the formula re-labels new current-year charges as the collection balance. The two sentences give two answers on one world: a payment owed vs none owed.
  - The same stale-notice intermediate sits in `c_charges_taken` / `g_charges_taken` and in the CEP prerequisite sentence ("whose year-end collection balance is not yet repaid").
  - Bears on task 1 (demonstrated there on Samuel's account).
- **P-02 SOURCE-POLICY RED: one inactive balance, three competing policies.**
  - Evidence (quotes in policy_conflict_scan): the cover rule says "the positive balance on the inactive account of a departed sibling ... covers the student's unpaid meal charges". The departure rule says the balance "is moved ... to the household's youngest active student, less what the schedules keep back". The graduate rule says the balance "is rolled ... to the household's active account that carries unpaid meal charges".
  - Demonstrated consequence on the charter: take a household where a prepayment is quoted for an older child with unpaid charges and a sibling withdrew with leaver_reason moved_out_of_state holding a positive balance. The cover sends the cover amount (unpaid charges as the schedules take them + restored days) to the older child. The departure rollover sends that balance less holds and reserve to the youngest child. These are two different writes on the same balance, and neither rule excludes the other. A graduate's inactive balance is in the same position against the cover, because "departed" is undefined and base inactivates on graduation too.
  - Neither task world engages the overlap: task 0's departed sibling with a balance left for private_school, and task 1 quotes no prepayment and asks no cover. Each task file records this as an observation.
- **P-03 SOURCE-POLICY RED: undeclared cross-problem order in the netting rule.**
  - Evidence: "When a sibling's departed-balance cover or prepayment is being worked out, the idle balance of each other active account of the household is netted first". meals_ext_prepayment_quote's rule states no netting wait and its `prerequisite` has no netting edge; the only declared netting edge is cover → netting.
  - Demonstrated consequence: take a household with a student owing unpaid charges, an active sibling with an idle balance, and no departed sibling holding a balance. The prepayment rule quotes at once on the student's own balance, while the netting rule says net first and so raises the balance and lowers the quote. Two orders give two terminal states.
  - The netting rule also restates the dependency of edge 3 from the depended-on side.
  - Task 0 is not moved numerically, because its cover chain forces the netting first anyway.
- **P-04 SOURCE-POLICY RED (B8 framing clauses / C3).**
  - (a) The CEP refund says "Online card deposits the payment processor can still reverse are refunded to the card through the processor rather than by district check". The departure rollover says they "go back to the card through the processor rather than to a sibling". No tool, no record and no gold-capable write performs a processor refund, and refund_cep_meal_balance's docstring says "the rest of the balance stays on the account". The rule promises an outcome no write produces.
  - (b) The departure rollover's "Meals from a student's last days of attendance can still reach the account from the point of sale after the student has left" contradicts the in-force base sentence "Meals and items are rung up only on an account in status active." with no overwrite declared.
  - Bears on task 1, which is demonstrated there.
- **P-05 SOURCE-POLICY RED (B2 tie rule).** "only the most recent online card deposit is left out / stays" (`e_online_latest`, `w_online_latest`) and "the latest year-end collection notice" state no same-date tie rule. DSL `LATEST` keeps the first row met on a tied date.
  - Demonstrated consequence: two online card deposits of different amounts on the same latest date give two readings of the left-out amount.
  - Neither world has a same-date tie on a tier that is taken, so this is an observation in each task file.
- **P-06 SOURCE-POLICY RED (A9 grouping / rule–compute edge).** As shown in rule_compute_equivalence, when the account's unpaid charges are below the notice amount, compute sizes the installments on the uncapped notice amount while a reader of "the year-end collection balance ... never more than the account's unpaid meal charges" caps it first. Example: notice 28.70 with unpaid 20.00 gives 3 installments by compute and 2 by the capped reading. Task 1's world has unpaid above the notice amount, so this is an observation there.
- **F-01 SOURCE-FACTOR RED (A7):** listed in factor_ladders; 11 factor slots across cover, graduate, departure and cep_refund fail T2. Task files give T1.
- **F-02 SOURCE-FACTOR RED (A3):** cover and graduate baseline.rule carry a defining sentence used only by factors.
- **F-03 SOURCE-FACTOR RED (mislabelled effect):** quote_added_meal, cover_restore_breakfast, departure_reserve_meal and rollover_restore_meal (method label, value substitution); coll_current_charges (parameter label, algorithm change). meals_ext_prepayment_quote is left with no method factor.
- **F-04 SOURCE-FACTOR RED (unreal ladders, user's top-priority realism bar):** the invented members in the realism table above.
- **F-05 SOURCE-FACTOR RED (counts):** after F-01 to F-04, no computation keeps 4–6 factors with 2 parameter and 1 method. Task 1's policies keep no cross-difficulty factor.

Observations (no demonstrable consequence on any task; not grounds for rework on their own):
- O-1: the action-form fallbacks of edges 5 and 7 are unjustified. The state "the account carries a repayment payment posted on the day of the refund / rollover" singles out pay_collection_meal_installment, as edge 2 does in the same charter.
- O-2: the ordering word "first" appears in deposit_meal_prepayment's docstring, as an effect description.
- O-3: lunch-charge tiers coincide numerically for the reduced and free statuses.
- O-4: the milk tier's own rounding sits beside "rounded half up to the cent once, at the end". It is numerically exact in every variant.
- O-6: lunch prices come from the enrollment-record campus while breakfast prices come from the account campus. They never differ in a base-consistent world.
- O-7: some seeded balance notices are thinner than base's notice sentence: no low_balance notice after a purchase left 0.65 on Rafael's account (2026-08-25, task 0). No computation reads that account's low-balance notices.
- O-8: the `gate` of state_gate edges 5 and 6 is a field, not an eligibility id.

<!-- closing_checklist is appended below only after both task files carry their source_gt_comparison -->

## closing_checklist
Written after both task files carry their source_gt_comparison (reveal 2026-10-24T18:47:49Z). Nothing above this heading was edited after the reveal.

| check | result |
|---|---|
| per-task files 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json; this file sits alongside | yes (revision_1, no older revision) |
| every comparison section carries a PASS | **no**: task 0 is RED (SOURCE-FACTOR); task 1 is RED (SOURCE-POLICY, SOURCE-CHAIN, SOURCE-FACTOR, SOURCE-TASK) |
| all 8 extended policies covered, scopes pairwise disjoint | yes (charter_scope task 0 = netting, cover, inactive_repayment, prepayment; task 1 = departure, collection, graduate, cep_refund) |
| task tools closed, uuid8s independent | yes |
| GT writes match the independent derivations | yes, every argument; task 1 under reading A only |
| problem trees: 1–3 prerequisite problems, ≥ max(n−1,1) value_input, an owner=user write, acyclic | task 0 yes. Task 1 yes under reading A; under reading B (P-01) the collection node is already satisfied and the tree has no owner=user write |
| whole-difficulty prerequisite graph acyclic | yes |
| factor structure: 4–6 per computation (2 P, 1 M), multi-source and cross-difficulty per task, ladders real, every factor bearing weight against an honest baseline | **no** (F-01 to F-05) |
| instantiation gates re-run on the final form | not re-run by this auditor; the snapshot of the audited form is all green. A rework must re-run them |

The difficulty does **not** pass the source-layer audit. RED ids:
- P-01: undeclared override of base allocation; stale year-end collection balance. Demonstrated in task 1 as a second solution and a pre-met prerequisite.
- P-02: one inactive balance claimed by cover / departure / graduate rollover; "departed" undefined.
- P-03: netting rule states an undeclared netting-before-prepayment order and restates edge 3 from the depended-on side.
- P-04: processor card-refund framing clauses no write honours (CEP refund, departure rollover); late-posting reserve contradicts base "Meals and items are rung up only on an account in status active" with no overwrite.
- P-05: no same-date tie rule for "the most recent online card deposit" or "the latest year-end collection notice".
- P-06: collection "year-end collection balance ... never more than the account's unpaid meal charges" has two groupings; compute sizes installments on the uncapped amount.
- F-01: A7 rate × count splits with a zero-day baseline (cover, graduate, departure, CEP keep).
- F-02: A3: cover and graduate baseline.rule carry the restored-day sentence only factors use.
- F-03: mislabelled effects (four method→value substitutions, coll_current_charges); prepayment has no method.
- F-04: unreal ladders: milk two-fifths share ×6, notice-count day ladders, buffers, installment tapers, above-limit up-front tiers, count-keyed card reversal, grade-keyed CEP keep, extras keeps, late-posting reserve, charges-taken carve-outs, current-year add.
- F-05: no computation keeps 4–6 / 2P / 1M after the strikes; task 1 keeps no cross-difficulty factor.

VERDICT revision_1: task0=RED task1=RED charter=P-01,P-02,P-03,P-04,P-05,P-06,F-01,F-02,F-03,F-04,F-05

---

## revision_2

### charter_global_frozen (revision_2)
- Frozen 2026-10-24T20:36Z, independent auditor, written before reading any revision-2 task JSON.
- Entry checks:
  - The last non-blank line of worklog.md is `REWORK round 2: gates 7/7 green`.
  - Gate snapshot /tmp/erl0078_coord/snap_meal_account_and_benefits_r2.txt was run by the auditor (execute-only). EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE are all OK.
- Hashes, recomputed by the auditor and equal to the snapshot:
  - meals.extended.yaml: 9a85e8bc4a4737eb (r1: e6b9691f697ad7bb).
  - task_tools.py: 4978e6f7d61c0e66 (r1: 2b44be40b0fc568e).
  - r2/0.view.json: a92acd4c1ba36f60, unchanged from r1.
  - r2/1.view.json: bd4f60a9231da3e8. Only user_scenario differs from r1; initial_state and frozen_time are identical, checked by script.
- Both shared inputs changed, so every charter-global section below is **re-derived in full**. The revision_1 text above is left untouched.
- Read in this revision:
  - the reworker's "REWORK round 2 claims", by item id, with every figure masked by sed on read;
  - audits/render_source/realism_bar.md, read in full; it supersedes the original realism line;
  - owner_ruling.md;
  - XF_recipe.md.
- Base copy: lines 1–946 are byte-identical to blueprint/products/meals.yaml.
- B5 sweep, re-run: every compute_basis quote, baseline sentence, policy_source and replaced_by text is verbatim in its rule.
- Tools: the 8 uuid8s are unchanged and independent. Bodies still only validate amount and ids and then `ctx.create`. pay_collection_meal_installment's docstring now reads "toward the unpaid meal charges on a student's active cafeteria meal account under the district's repayment plan for active accounts". No docstring names another tool or a sequence. Action binding: each (tool, amount) is claimed once.

### policy_conflict_scan (revision_2)
- Givers of sibling transfers are now disjoint by stated scope tails:
  - cover: "a student whose enrollment record in status withdrawn carries a leaver reason other than moved_out_of_state or returned_to_home_country ... never this cover";
  - departure rollover: only those two reasons;
  - graduate rollover: "the leaver reason graduated on the student's completed enrollment record ... A student who withdrew is never a graduate here";
  - netting: "made only as part of working out a departed-balance cover".
- **New overlap, meals_deposit on an active account (P-07).** meals_ext_collection_repayment was rebuilt as "the district's repayment plan for active accounts". It triggers "When the household asks to repay the unpaid meal charges on an active meal account, or when a refund on another account of the household waits on that repayment". meals_ext_prepayment_quote triggers when a parent asks "how much to put on a student's active meal account so that the account is brought current and funded ahead", and its quote "adds its unpaid meal charges to the quote".
  - A request to bring an account current is a request to repay its unpaid meal charges, so both policies claim it.
  - One answer is a single quote; the other is an installment of a plan.
  - Neither rule names the other in an exclusion tail. The collection rule excludes only inactive accounts.
- Inactive vs active repayment plans are disjoint ("Unpaid meal charges on an inactive account are repaid under the repayment plan for inactive accounts, never this one").
- The CEP refund is the only refund.
- Cross-category reads: enroll only (campus, status, grade_level, leaver_reason, withdrawal_date).
- Scopes of the two tasks are re-checked in the task files.

### rule_compute_equivalence (revision_2)
- All eight computes follow their rule, sentence by sentence (B5 clean). The changed bindings were checked one by one:
  - `q_serving_days` ← `MONTHS('2026-08-01', NOW)` equal to 2 or 3. That is a quote dated October or November 2026, matching "a quote dated in October / November" read inside "the district's 2026-27 calendar" (O-10 below).
  - `c_/g_today_deposits` = COUNT(meals_deposit, transaction_date = NOW), matching "a deposit posted on the cover/rollover date".
  - `e_/w_online_latest` = SUM over transaction_date = LATEST card-deposit date, matching "the online card deposits of the most recent card-deposit date stay (all of them when several post that date)".
  - `k_size_charges` = unpaid, matching "by the size of the unpaid meal charges", so P-06 has no second grouping left.
  - `k_up_front` = MN(unpaid, returned) or MN(unpaid, letter amount), matching "up to the unpaid meal charges".
  - `k_grade_change` and `k_age` (the latter guarded by `k_letter_date`) match their ladders.
- The rounding and month conventions are unchanged from revision_1. The whole-month sentence matches DSL `MONTHS`.
- Lunch-vs-breakfast campus split: unchanged (O-6).

### prerequisite_graph and prerequisite_sentences (revision_2)
- Edges are unchanged in shape: 1–7 as in revision_1, the same kinds, gates, forms and resolvers. Every policy_source is verbatim; the graph is acyclic; fallback_reason appears exactly on the action edges.
- Changed sentences:
  - CEP refund ← collection: "A CEP refund is not paid until the household has made the repayment-plan payment due today on every other active account of the household whose unpaid meal charges are at least the online deposit minimum." It is no longer tied to a year-end balance and carries the D2 carve-out.
  - Graduate ← collection: "The rollover amount is fixed only after the household has made the repayment-plan payment due today on the receiving account."
- Fallback re-test for edges 5 and 7: the new reason holds. deposit_meal_prepayment and pay_collection_meal_installment both post an online_card meals_deposit dated today on an active account, so no state singles out the payment. **O-1 is closed.**
- Edge 2 (state form) still has one writer (pay_inactive, the only deposit tool documented onto an inactive account).
- **Depended-on rules restating a dependency (check 6), class swept across all eight rules:**
  - The netting rule now reads "A netting is made only as part of working out a departed-balance cover for a student's active account". That is a scope restriction with no order word. The revision-1 "netted first ... or prepayment" is gone, so **P-03 as raised is closed**.
  - **The collection rule's trigger "or when a refund on another account of the household waits on that repayment" restates edge 5 from the depended-on side** with an ordering verb ("waits on"). This is a new member of the P-03 class (P-03b).
  - The cover's "When a prepayment is quoted for a student" is a trigger without an order word, as in revision_1 (observation).
- D1 (resolver settles every engaged world): the graduate rollover waits on "the repayment-plan payment due today on the receiving account". The collection rule's trigger list (household request, or a waiting refund) does not include a waiting rollover. In a world where only a graduate rollover is in play, the resolver's own rule does not say it applies. Neither task is such a world (task 1 has the waiting refund), so this is observation O-11.

### override_declarations (revision_2)
- meals_deposits_and_returns, meals_meal_pricing and meals_refunds_and_transfers: conclusions as in revision_1. The CEP overwrites are unchanged and hygienic.
- meals_unpaid_meal_charges s6, "Any deposit is applied to unpaid meal charges first": the collection plan now works on "the account's unpaid meal charges ... the amount by which the account's balance is below zero". The year-end letter no longer classifies the balance. The cover and graduate charges-taken tiers no longer read notices. **The P-01 contradiction (scope sentence against formula) is closed.** One residue: the up-front tier "the amount stated on the latest such notice, up to the unpaid meal charges, is paid up front" still prices from a letter whose debt later deposits may have repaid. As a plan term it contradicts no sentence, so it is judged under realism (F-04).
- meals_account_status s1: the departure reserve now rests on "School Nutrition reconciles the account's final weeks of point-of-sale batches". No meal reaches an inactive account any more, so **the P-04(b) contradiction is closed**.
- P-04(a): card deposits now "stay on the account" / "stay on the departed account", which matches the refund tool docstring, so **it is closed**.
- P-05: a tie rule is stated for the card-deposit date, and "Notices of one kind are one per account per date", which matches the base grain "One row per notice per account per date", so **it is closed**.

### factor_ladders (revision_2)
Counts: prepayment 5 (4P/1M), cover 5 (3P/2M), netting 5 (4P/1M), inactive 5 (4P/1M), cep 5 (3P/2M), collection 5 (4P/1M; coll_current_charges removed, coll_grade_change added), departure 6 (4P/2M), graduate 6 (4P/2M). Ladders have 3 disjoint tiers each, are stated in the rule and implemented, with no factor-reads-factor.

**A7 / T2 (class swept over every rate × count pair):**
- Pairs with a nonzero baseline count now pass T2 for the per-day factors:
  - prepayment: days 20;
  - cover: restore_days_standard 2;
  - netting: keep 10;
  - departure: reserve_days_standard 1;
  - graduate: rollover_days_standard 2.
- **cep_refund_keep_days still fails T2.** `e_keep = e_keep_days * e_milk_keep + e_extras_keep`, and cep_refund_keep_milk's baseline is 0. With every other factor at baseline, the kept days multiply 0, so no producible world exists in which keep_days alone moves the refund. The reworker's own residue note says the same. cep_refund_keep_milk passes T2 (days baseline 3). **F-01 is not closed (one member).**

**A3:** the restored/reserved-day sentences are now used by the baselines. **F-02 is closed.**

**Effect labels:**
- I accept the reworker's counter-argument for quote_added_meal, cover_restore_breakfast, departure_reserve_meal and rollover_restore_meal under the run's XF A6 text: "PASSES if one tier adds an input or an operation (floor, max/conditional pick, data-selected window, published parameter)". Tier 1 adds the account-campus input and a conditional pick that tier 2 lacks. My revision-1 reading was stricter than the run ruling; this item is withdrawn, not "fixed".
- coll_current_charges is removed. **F-03 is closed.**

**Realism, judged against realism_bar.md** (each factor tagged; R = accepted shape, X = rejected):

| factor | tag | reason |
|---|---|---|
| quote_lunch_charge, cover_restore_lunch, netting_keep_lunch, departure_reserve_lunch, rollover_restore_lunch | R1 | meal price by campus level / CEP / status |
| quote_added_meal, cover_restore_breakfast, departure_reserve_meal, rollover_restore_meal | R1 | breakfast price by campus level and status |
| quote_serving_days | R3 | serving-day count from the district calendar; see O-10 |
| netting_check_hold, cep_refund_check_hold, departure_check_hold | R2 | hold on check deposits inside the bank return period, keyed on a date window and on a returned check |
| plan_size_installments, coll_size_installments | R5 | installment threshold |
| quote_milk, cover_restore_milk, netting_keep_milk, cep_refund_keep_milk, departure_reserve_milk, rollover_restore_milk | **X1** | "Fractions of other prices ('two fifths of the milk price')", named verbatim in X1 |
| quote_low_balance_buffer, rollover_buffer | **X1** | a buffer added to a quote or a transfer is a "reserve or keep no policy publishes" |
| netting_keep_days, netting_extra_keep, cep_refund_keep_days, cep_refund_keep_extras | **X1** | keeps no policy publishes (days kept by notice history or grade band; last month's à la carte total) |
| departure_reserve_days | **X1** | a "reconciliation reserve" of serving days by months since withdrawal is a reserve no policy publishes |
| cover_restore_days, rollover_restore_days | **X1** | "restoring serving days" by moving more than is owed is an uplift no policy publishes; days keyed on notice counts |
| cover_charges_taken, rollover_charges_taken | **X1** | refusing to let the household's own sibling balance pay charges because a deposit posted today ("that day's repayment payment and its plan settle them") or because a check was returned is an invented penalty or relief |
| plan_relocation, plan_payment_history, plan_recency, coll_age, coll_payment_history, coll_grade_change | **X1, also X2** | installment add-ons and cut-backs by leaver reason, deposit/notice history, months inactive, letter age and grade band. Four (inactive) or four (collection) adjustments are stacked on one installment count |
| plan_up_front, coll_up_front | **X1** (one tier each) | returned check paid up front is acceptable (R5-like). "The part above the charge limit" (inactive) and "the amount stated on the latest year-end letter, even after later deposits cleared the balance" (collection) are not |
| cep_refund_card_reversal, departure_card_stays | **X1/X4** | the stated reason is "still inside the card dispute period", but the tiers key on how many card deposits were made (≥ 2 in two months → all of two months; otherwise the latest date). A dispute window runs on a deposit's age, not on a count |

**Mechanism realism in the baselines (new member of the F-04 class).** To clear A7, the reworker moved the X1 mechanisms into the baselines themselves:
- cover: "plus two restored serving days";
- graduate: "plus two restored serving days";
- departure: "less a reconciliation reserve of one serving day";
- netting: "the keep being ten serving days", already present in revision_1 and missed there, now swept.

Each standard method itself carries a keep, reserve or uplift no district publishes. **F-04 is not closed.**

**Survivors and counts:**
- Survivors (R-tagged): prepayment 3, cover 2, netting 2, inactive 1, cep 1, collection 1, departure 3, graduate 2.
- Every computation is below the 4–6 floor. **F-05 is not closed.** The reworker states the floor and the realism bar cannot both be met in this charter without a waiver; that is a coordinator decision, not an audit outcome.
- Cross-difficulty survivors exist only as R1 lunch prices that sit inside X1 mechanisms: task 0 (quote_lunch_charge, netting_keep_lunch, cover_restore_lunch) and task 1 (departure_reserve_lunch, rollover_restore_lunch).

### findings (revision_2)
Status of every revision-1 id:

| id | revision_2 status |
|---|---|
| P-01 | closed (contradiction removed; letter-amount residue judged under F-04) |
| P-02 | closed (scope tails disjoint) |
| P-03 | closed as raised; new class member P-03b below |
| P-04 | closed (a) and (b) |
| P-05 | closed |
| P-06 | closed |
| F-01 | **open**, one member: cep_refund_keep_days fails T2 |
| F-02 | closed |
| F-03 | closed (four items withdrawn under the XF A6 ruling; coll_current_charges removed) |
| F-04 | **open**: the X1/X2/X4 members in the table above, plus the baseline mechanisms of cover, graduate, departure and netting |
| F-05 | **open**: counts after F-04 |

New in revision_2:
- **P-07 SOURCE-POLICY RED: the prepayment and the active-account repayment plan both claim a request to bring an active account current.** Quotes are in policy_conflict_scan.
  - Demonstrated consequence on a charter world: a parent asks to clear a student's negative balance of 52.75, on an account with a returned 15.00 check and two deposits plus a negative notice in two months, grade 06.
  - The collection rule quotes one installment: 3 by size, +1 history, +1 grade, so 5 installments, with 15.00 up front, giving 22.55.
  - The prepayment rule quotes the whole balance plus serving days in one deposit.
  - These are two different scored writes for one request, and no exclusion tail decides between them.
- **P-03b SOURCE-POLICY RED: the depended-on rule restates the dependency.** The collection rule's trigger says "or when a refund on another account of the household waits on that repayment". Edge 5's prerequisite sentence must live only in the CEP refund's rule; the depended-on rule may not restate it.
- O-10 (observation): quote_serving_days's fall-through "twenty ... for a quote dated in any other month" claims 20 serving days for every month other than November and December, including a January after winter break and a March with spring break week. Only the October tier is engaged by any task. The figures are the district's own calendar (R3), so this is not struck; it is noted for the renderer.
- O-11 (observation): the collection rule's trigger list does not cover the graduate rollover's wait.
- O-2, O-3, O-4, O-6, O-7, O-8: carried forward unchanged (the reworker's reasons accepted).

### closing_checklist (revision_2)
Written after both revision-2 comparisons; nothing above it in revision_2 was edited after the reveal.
- Per-task files match tasks one-to-one, and revision_1 text is preserved. Comparisons: task 0 is RED (SOURCE-FACTOR), task 1 is RED (SOURCE-FACTOR). Every other relationship is PASS in both.
- Coverage and disjoint scopes: yes. Tools and uuid8s: yes. GT equals the independent derivation in both tasks, every argument and every sensitivity figure.
- Trees: task 0 has 3 prerequisite problems, 2 VI edges and 2 owner=user writes. Task 1 has 3 prerequisite problems, 2 VI edges and 1 owner=user write. Both are acyclic, and the whole-difficulty graph is acyclic.
- Factor structure: **no**. F-01 has one member left, F-04 has the X1/X2/X4 members and the baseline mechanisms, and F-05 has the counts.
- Gates: the coordinator snapshot r2 is 7/7 green on this form.
- Final sweep: every class raised in either revision was re-run across all eight policies.
  - Undeclared or base override (P-01 class): none left.
  - Overlapping subjects (P-02 class): one new member, P-07.
  - Order statements outside the blocked rule (P-03 class): one new member, P-03b.
  - Framing and promise clauses (P-04 class): none left as contradictions; the departure "reconciliation" premise is judged under F-04.
  - Tie rules (P-05): closed.
  - Groupings (P-06): closed.
  - A7 (F-01): cep_refund_keep_days only.
  - A3 (F-02): closed.
  - Labels (F-03): closed under XF A6.
  - Realism (F-04): every member listed in factor_ladders (revision_2), with the netting baseline keep newly swept.
  - Counts (F-05).
- The difficulty does not pass the source-layer audit. Closing F-04 and F-05 together requires either a redesign onto R1–R5 levers or a coordinator waiver; the reworker's claim says the same.

VERDICT revision_2: task0=RED task1=RED charter=P-03b,P-07,F-01,F-04,F-05

---

## revision_3

### charter_global_frozen (revision_3)
- Frozen 2026-10-24T22:45Z, independent auditor, written before reading any revision-3 task JSON.
- Entry checks:
  - The last non-blank line of worklog.md is `REWORK round 3: gates 7/7 green`.
  - The snapshot /tmp/erl0078_coord/snap_meal_account_and_benefits_r3.txt was run by the auditor (execute-only). All seven gates are OK.
- Hashes, recomputed and equal to the snapshot:
  - meals.extended.yaml: fac21a708b2787f9.
  - task_tools.py: 3be73c39ed425255.
  - r3/0.view.json: 2f1e34885162365a. The persona is unchanged; initial_state was rebuilt: Rafael has a returned check, Mateo a card deposit dated 2026-10-05, Tomas a second card deposit, and Lucia's notices were re-seeded.
  - r3/1.view.json: 9d7418cb721d72f3. The persona is unchanged from r2; initial_state was rebuilt (Samuel has a returned check dated 2026-10-12, Daniel's and Grace's deposits changed).
- Both shared inputs changed, so every charter-global section below is **re-derived in full**. Older revisions are untouched.
- Read in this revision:
  - the "REWORK round 3 claims", by id, with figures masked on read;
  - realism_bar.md including AMENDMENT 1 (R6), read in full;
  - owner_ruling.md;
  - XF_recipe.md.
- Base copy: byte-identical. B5 sweep: clean (every compute_basis, baseline sentence, policy_source and replaced_by is verbatim in its rule).
- Tools: 8 uuid8s unchanged. Bodies validate amount and ids only, then `ctx.create`. No docstring names another tool or a sequence.
- cep_meal_charge is 0.00 in all seven variants (blueprint/products/meals.yaml), which matters for the A6 findings below.

### policy_conflict_scan (revision_3)
- **P-07 closed.** The prepayment says: "A request to repay unpaid meal charges in installments, or for the repayment-plan payment due today, follows the repayment plan for active accounts, never this quote." The plan says: "a request for one deposit that brings an active account current and funds it ahead follows the prepayment quote, never this plan." Each tail names the other.
- **P-02 stays closed.** The givers are disjoint by leaver-reason tails. The departure receiver is now "the household's youngest active student whose account's campus is not listed in cep_campuses", with a stated fall-back ("when every active student's account is at a campus listed in cep_campuses, the departed balance stays on the account").
- Inactive and active plans are disjoint by tail. The CEP refund is the only refund. Cross-category reads are enroll only: campus, status, and a count of the household's enrolled records via `XCOUNT('enroll','enrollments', status='enrolled')`.

### rule_compute_equivalence (revision_3)
- **Calendar**, checked weekday by weekday against the rule's stated closures:
  - next month after July = 14, August = 21 (September less Labor Day), September = 21 (October less Oct 12), October = 16, November = 14, December = 19, January = 19, February = 17, March = 22, April = 19 (May to the 27th), May/June = 0;
  - the days-left counts use (start, end], with start = NOW (or Aug 11) and the weekday computed from Monday 2026-08-03;
  - every figure equals the compute.
- Balance-basis, holds, R6 factors and the up-front term match their rules sentence by sentence. Rounding happens once at the end everywhere (**O-4 closed**).
- One B3 edge: plan/coll_last_payment say "within thirty days" and "more than sixty days" without saying whether the day count includes the end date. Compute uses DAYS(last, NOW) ≤ 30 and > 60. Neither world sits on a boundary: task 0 is 61 days and task 1 is 22. Observation O-13.

### prerequisite_graph and prerequisite_sentences (revision_3)
Edges:

| # | edge | kind | form | change |
|---|---|---|---|---|
| 1 | prepay→cover | VI | action | |
| 2 | prepay→inactive | SG | state | |
| 3 | cover→netting | VI | action | |
| 4 | cep→departure | SG | action | was VI; the departure now lands on a non-CEP sibling |
| 5 | cep→collection | SG | action | |
| 6 | cep→graduate | SG | action | |
| 7 | graduate→collection | VI | action | |
| 8 | departure→graduate | VI | action | **new**: "The departure rollover amount is fixed only after every graduate rollover owed to the receiving account has been made." |

- The graph is acyclic. Every policy_source is verbatim. Fallbacks are present exactly on the action edges and are justified (a sibling transfer in or out is indistinguishable, and the transfer may be not owed).
- **P-03b closed.** The plan's trigger now reads "or when School Nutrition quotes the repayment payment due today on an active meal account that carries unpaid meal charges of at least the online deposit minimum". It restates no other rule's wait.
  - Sweep of every rule for ordering sentences ("until", "only after", "waits"): each hit is a prerequisite sentence in the blocked policy's own rule.
  - The cover's "When a prepayment is quoted for a student" remains a trigger (observation, as before).
- **O-11 closed:** the plan's trigger covers any quote of the payment due today, including the graduate rollover's wait.

### override_declarations (revision_3)
- No notice amount is priced anywhere: no compute reads meal_notices. Base s6 is followed (**P-01 stays closed**).
- P-04 stays closed: holds "stay on the account", and there is no late-posting or processor premise.
- P-05 stays closed: the only LATEST is a date read, so same-date ties give one value.
- P-06 stays closed.
- CEP overwrites are unchanged and hygienic.
- Other base sentences: as in revision_2.

### factor_ladders (revision_3)
Counts (P/M): prepayment 5 (4/1), cover 5 (3/2), netting 5 (4/1), inactive 5 (4/1), cep 6 (5/1), collection 5 (4/1), departure 6 (4/2), graduate 5 (3/2). No factor reads another factor's binding.

**A7/T2:** every rate × count pair now has nonzero standards: 20 days or 5 days, times a one-lunch day charge of 3.10 Paid. The keep_days × milk pair is gone. **F-01 closed.**

**A3:** baseline sentences are used by the baselines. **F-02 stays closed.**

**A6 and effect labels: F-03 reopens.** All members:

| member | label | why it fails |
|---|---|---|
| quote_breakfast, cover_breakfast, departure_breakfast, rollover_breakfast | method | Tier 1 ("a breakfast rung up ... at a campus listed in cep_campuses → each serving day adds the CEP meal charge") selects 0.00 across its whole domain, because cep_meal_charge is 0.00 in every variant. Tier 4 ("no breakfast rung up → no breakfast is added") also selects 0. XF A6: "A 'nothing' tier fails where another tier is also 0 across its whole domain". The skill: no two tiers may select the same value or method. |
| cover_balance_basis, departure_balance_basis, rollover_balance_basis | method | Tier 1 "unpaid meal charges are added" = −balance; tier 2 "positive balance is subtracted" = −balance; tier 3 "nothing" = 0 = −balance. All three tiers are the single formula −balance (A6: any aggregate of the same field counts as ONE input; the tiers are the same combination of it). There is no second method. |
| netting_keep_extras, cep_refund_keep_extras | method | Their ladder (milk-only price per day / second-meal price per day / nothing) is word-for-word the ladder that quote_extras, cover_extras, departure_extras and rollover_extras carry with the label `parameter`. The tiers substitute a published price into "day charge += x", which is a parameter. |

Consequence: prepayment, cover, netting, cep_refund, departure and graduate have **no honest method factor**. Only the two repayment plans keep one (plan_up_front / coll_up_front). Their tiers "all unpaid / the returned amount / nothing" read different inputs and pass A6's letter, as accepted in revision_1.

**Straw-man baselines (new, SOURCE-FACTOR; class "dishonest baseline").**
- cover, graduate: the baseline "leaves the receiving account's balance out of account". Yet each rule's first sentence says the transfer "clears the account's unpaid meal charges" / "clears those charges". A reader computing the standard method ignores the very charges the policy exists to clear, and the balance term is carved out into the identity factor above.
- departure: the same carve-out, against "funds that student's meals", where a positive balance "already pays for meals" by the rule's own sentence.
- cep_refund: the baseline keeps "twenty serving days ... of one reimbursable lunch at the elementary lunch charge". The policy applies only to "an active account at a campus listed in cep_campuses", where "Reimbursable breakfasts and lunches are served at no charge". No in-scope reader charges a lunch. cep_refund_keep_lunch's tiers 2 and 3 (secondary / elementary) are unreachable for any in-scope account in a base-consistent world, because base meals_account_status makes the account campus follow the enrolled campus. Its condition "the enrolled campus is a CEP campus" holds of every customer reaching this write.
- departure_lunch: the same dead tier in reverse. The receiver is by scope a student "whose account's campus is not listed in cep_campuses", so the CEP tier is unreachable, leaving two reachable tiers.

**X2 / R2 "ONE factor per timing dimension per computation" (new).** The serving days "from the day after the [quote] date through the end of the calendar month after it" are one calendar count keyed on one date, but are split into two factors:

| computation | factor pair |
|---|---|
| prepayment | quote_serving_days + quote_days_left |
| netting | netting_keep_days + netting_keep_days_left |
| cep_refund | cep_refund_keep_days + cep_refund_keep_days_left |
| departure | departure_serving_days + departure_days_left |

Both factors of each pair read only NOW against the same stated calendar, and their sum is the single quantity the rule defines. Cover and graduate carry only the days-left factor and are not members.

**Realism** (realism_bar R1–R6 / X1–X4):

| factors | tag |
|---|---|
| the lunch factors (where reachable) | R1 |
| the extras factors | R1 (published milk-only and second-meal prices for what the student buys) |
| the serving-day factors | R3 (district calendar per school day; the full 2026-27 calendar is stated, **O-10 closed**) |
| check holds and card holds | R2 (bank return period / dispute window keyed on deposit dates, longer after a returned deposit; the count-keyed card tier of revision_2 is gone) |
| plan/coll_size_installments, plan/coll_up_front | R5 |

Every revision-2 X1 member has been removed, not reworded: the milk two-fifths share, the buffers, the notice- and grade-keyed days, the à la carte keeps, the reserve, the charges-taken carve-outs, the installment tapers and the letter tier.

R6 grading (AMENDMENT 1, conditions 1–6), for plan_household_students, coll_household_students, plan_school_calendar, coll_school_calendar, plan_last_payment and coll_last_payment:
1. Recorded keys: the enrolled-record count, the quote month, and the lead days since the latest online card deposit.
2. Round figures: ±1 or ±2 installments.
3. No federal or base conflict: SP 46-2016 allows plans and nothing adds a fee.
4. None is a named X1 mechanism. The rule wording "a household that still has students in the district" reads like "continuing family", but the key is the count of the household's children enrolled, which condition 1 names as admissible. Noted, not failed.
5. A1–A10 and B1–B8 pass (O-13 aside). No two R6 factors share a dimension.
6. Count = 5 drawn − 2 honest = 3, listed with tag, key and reason in the claims.

All six are **R6-WAIVED (BLUEPRINT-KNOWN)** observations.

**Mechanism, flagged by the reworker for a ruling.** The netting keep, the CEP keep and the cover/graduate/departure funding price a student's coming serving days with calendar × published prices. This is an R1+R3 composite, not a named X1 keep: the revision-2 keeps were arbitrary day counts keyed on notices or grade. I do not raise it as RED. It is recorded as **O-12** for the coordinator: whether a district would set a sibling-transfer or refund amount by this forecast instead of the household's stated amount is a coordinator ruling.

**Survivors after A6, mislabel, straw-man and X2 strikes** (one factor of each X2 pair kept):

| computation | survivors | below floor? | method left? |
|---|---|---|---|
| prepayment | days, lunch, extras = 3 | yes | none |
| cover | days_left, lunch, extras = 3 | yes | none |
| netting | card_hold, days, lunch = 3 | yes | none |
| inactive | 2 honest + 3 R6-waived = 5 | no | yes |
| cep | check_hold, card_hold, days = 3 | yes | none |
| collection | 5 | no | yes |
| departure | days, extras = 2 | yes | none |
| graduate | days_left, lunch, extras = 3 | yes | none |

**F-05 stays open** for six computations.

### findings (revision_3)

| id | revision_3 status |
|---|---|
| P-01, P-02, P-03, P-04, P-05, P-06 | stay closed (re-checked) |
| P-03b | closed |
| P-07 | closed |
| F-01 | closed |
| F-02 | closed |
| F-03 | **reopened, regression**: breakfast ×4 (CEP tier ≡ nothing), balance_basis ×3 (identity), extras mislabelled ×2; six computations have no method |
| F-04 | **closed** for every revision-2 X1/X2/X4 member. The new X2 day-count splits are raised as F-06 |
| F-05 | **open** (six computations below the floor) |

New in revision_3:
- **F-06 SOURCE-FACTOR RED (X2/R2):** the day-count splits listed above (4 pairs).
- **F-07 SOURCE-FACTOR RED (dishonest baseline / unreachable tiers):**
  - the cover, graduate and departure baselines "leave the receiving account's balance out of account";
  - the cep_refund baseline charges an elementary lunch at a CEP campus;
  - cep_refund_keep_lunch has one reachable tier for in-scope accounts;
  - departure_lunch's CEP tier is unreachable.

Observations:
- O-12: forward-meal funding mechanism, for the coordinator.
- O-13: day-count inclusivity on the last-payment factors.
- R6-WAIVED ×6.
- Carried forward: O-2, O-3, O-6, O-7, O-8. O-10 and O-11 are closed, O-4 closed.

### closing_checklist (revision_3)
Written after both revision-3 comparisons; nothing above in revision_3 was edited after the reveal.
- Files match tasks one-to-one, and earlier revisions are preserved. Both comparisons are RED on SOURCE-FACTOR only; policy, chain and task are PASS in both.
- Coverage and disjoint scopes: yes. Tools: yes. GT equals the blind derivation in every argument and every figure.
- Trees: task 0 has n = 3, 2 VI edges and 2 user writes. Task 1 has n = 3, 2 VI edges and 1 user write. Both are acyclic, and the difficulty graph is acyclic.
- Gates: the r3 snapshot is 7/7 green.
- Final sweep of every class raised in revisions 1–3, across all eight policies, one pass each:

| class | result |
|---|---|
| undeclared override / stale notice (P-01) | none |
| overlapping subjects (P-02, P-07) | none |
| depended-on or undeclared order (P-03, P-03b) | none |
| framing/promise (P-04) | none |
| tie rules (P-05) | none |
| grouping (P-06) | none |
| A7 (F-01) | none |
| A3 (F-02) | none |
| A6/labels (F-03) | the 9 members listed |
| realism X1/X4 (F-04) | none; the R6 ×6 are waived |
| X2 (F-06) | 4 pairs |
| dishonest baselines / dead tiers (F-07) | 4 baselines + 2 factors |
| counts (F-05) | 6 computations |

- The difficulty does not pass.

VERDICT revision_3: task0=RED task1=RED charter=F-03,F-05,F-06,F-07

---

## revision_4

### charter_global_frozen (revision_4)
- Frozen 2026-10-24T23:07Z, before any revision-4 task JSON was read, independent auditor.
- Entry checks:
  - The last non-blank line of worklog.md is `REWORK round 4: gates 7/7 green`.
  - The snapshot /tmp/erl0078_coord/snap_meal_account_and_benefits_r4.txt was run by the auditor (execute-only). All seven gates are OK.
- Hashes, recomputed and equal to the snapshot:
  - meals.extended.yaml: 74d4cb4a5af03e5e (changed).
  - task_tools.py: 3be73c39ed425255 (unchanged since revision_3, so the tool conclusions carry forward on that hash).
  - r4/0.view.json: bf231a888dd03c9a. Persona changed; world rebuilt.
  - r4/1.view.json: bee62f3f7927d681. Persona changed; world rebuilt.
- The charter changed, so its sections are **re-derived in full**.
- Read in this revision:
  - the "REWORK round 4 claims", by id, with figures masked;
  - realism_bar.md, including AMENDMENT 1 (unchanged since revision_3, md5 bf22bd25…);
  - owner_ruling.md;
  - XF_recipe.md.
- The reworker cites a coordinator ruling on O-12 ("each persona states that purpose explicitly"). **No such ruling file is among the auditor's inputs**: audits/render_source holds only XF_recipe.md, owner_ruling.md and realism_bar.md. Where it matters it is flagged below, not assumed.
- Base copy: byte-identical. B5 sweep: clean. The prerequisite graph is unchanged from revision_3 (8 edges, acyclic, the same kinds, forms and resolvers). Every ordering sentence is a prerequisite sentence of its own blocked rule.

### policy_conflict_scan (revision_4)
- P-02, P-07: the scope tails and two-way tails are unchanged, so they stay closed.
- **New, P-09: the CEP keep has two definitions in one rule.**
  - "The CEP refund leaves on the account what the household asks it to keep for the student's milk, extra meals and snacks for the serving days left in the current month."
  - Against that: "The standard CEP refund amount is the account's balance less a keep of five serving days (days_week), a school week, of one carton of milk bought on its own at the milk-only price". The milk, second-meal and snack schedules then derive the keep from the purchase history.
  - For a household that asks to keep nothing ("refund all of it"), the first sentence gives keep 0 while the schedules give a positive keep. That is two refunds for one request.
  - The transfers' "for the purpose the household states when it agrees: to …" names the purpose in the rule itself, so it is recorded as an observation (O-14): the rule offers no amount for any other stated purpose.

### rule_compute_equivalence (revision_4)
- **New, P-08 (B1/A9): "days" in the rule vs purchase lines in the compute.**
  - Every milk and second-meal schedule, across all 8 policies, says "by how often the student bought it ...: on four (regular_days) or more days ... on one to three days".
  - Compute counts purchase lines: `COUNT('meal_transactions', ..., meal_type='milk_only')`, not distinct dates.
  - Two milk cartons rung up on one date count 2 in compute and 1 day in the rule. Base permits this: "milk bought alone is charged milk_only_price" per line.
  - Example: an account with milk on three dates, one of them with two cartons. The rule says "one to three days", so the month's spend is added once. Compute counts 4 and adds the milk price on every serving day.
  - Neither world contains a same-date duplicate (checked by script), so neither task is moved. The charter mismatch stands.
- Other bindings checked against their rules:
  - the single serving-days binding per computation (days left + next month, or days left only);
  - breakfast with the CEP campus folded into the nothing tier;
  - the balance terms in the standards;
  - holds; R6 terms; the last-payment day convention, now stated ("counting the days from the deposit date to the quote date"; **O-13 closed**).
  - Rounding happens once at the end.

### override_declarations (revision_4)
- **P-01 class reopens (regression) through coll_year_end_notice.**
  - The rule says: "The repayment plan sets more installments for unpaid meal charges carried across the summer break, as a year-end collection notice on the account in the twelve months before the quote date shows: two more ... thirty dollars ... or more below zero, one more ... when it stated less".
  - Base meals_unpaid_meal_charges s6 says: "Any deposit is applied to unpaid meal charges first". A later deposit that took the balance to zero or above repaid every carried charge.
  - The factor still reads the notice as proof that charges are carried. Its tier rests on a stamp (the notice and its stated balance), not on the history the sentence describes.
  - This fails R6 condition 3 ("contradicts no ... in-force base clause") and is the revision-1 P-01 shape in a new place. The task-1 demonstration is in 1.md.
- **B8 / unreal tier in departure_lunch.**
  - The rule says: "no lunch when the student holds no enrollment record in status enrolled, because the student is not attending".
  - The base charters contradict that premise. meals_account_status keeps an account active, or reactivates it, for a student whose enrollment is "in status provisional or enrolled". enroll lets a student "attend provisionally".
  - A provisional receiving student attends and is charged lunch, yet the tier counts none. The other seven policies price the same case at the elementary lunch charge.
- Base sentences otherwise: as in revision_3. CEP overwrites are unchanged.

### factor_ladders (revision_4)
Counts (P/M): prepayment 5 (3/2), cover 5 (3/2), netting 5 (3/2), inactive 5 (4/1), cep 6 (4/2), collection 6 (5/1), departure 5 (3/2), graduate 5 (3/2). No factor reads another factor.

- **F-03 closed.**
  - Breakfast is now a parameter with three distinct values (secondary / elementary at a non-CEP campus / nothing). The CEP case is folded into nothing, so no two tiers share a value.
  - balance_basis is removed.
  - Milk and second-meal are methods whose tiers differ in input and operation (price × counted days / the month's recorded spend once / nothing), which passes A6.
  - Every computation has at least one honest method.
- **F-06 closed:** one serving-days factor per computation.
- **F-07:** mostly closed; two members remain.
  - The cover, graduate and departure standards subtract the balance. The CEP lunch factor is removed.
  - Remaining member 1: **cep_refund_keep_milk's baseline is `e_milk_rate: P('milk_only_price')`, while its fall-through tier is "not bought in that month → nothing is added"**. The skill requires "every factor's fall-through tier is that baseline". A student who bought no milk sits on the fall-through and gets 0, while the baseline keeps the milk price on every day.
  - Remaining member 2: departure_lunch's "no lunch ... not attending" tier is unreal for a provisional student (see above).
- **F-01/A7:** T2 holds for every pair. The CEP keep days × (milk 0.75 baseline + second) is nonzero at baseline.
- **Realism (R1–R6 / X1–X4):**
  - lunch, breakfast, milk and second-meal factors: R1 (published prices for what the student buys, or the month's recorded spend);
  - serving days: R3;
  - holds: R2;
  - size and up-front: R5;
  - cep_refund_keep_snacks: the household's own stated keep (the parent asks for it), recorded à la carte spend. Accepted, with the P-09 caveat;
  - no X1/X2/X4 member is reintroduced.
- **R6:**
  - plan_household_students, coll_household_students, plan_school_calendar, coll_school_calendar, plan_last_payment and coll_last_payment meet conditions 1–6: **R6-WAIVED (BLUEPRINT-KNOWN)**.
  - **coll_year_end_notice fails condition 3** (above) and is RED.
- **F-05 closed on counts.** After the strikes above (cep_refund_keep_milk, departure_lunch, coll_year_end_notice), every computation keeps ≥ 4 factors with ≥ 2 parameter and ≥ 1 method. The R6-waived factors count as waived observations. Each task keeps a multi-source factor (the holds) and a cross-difficulty factor (lunch / household count).

### findings (revision_4)

| id | revision_4 status |
|---|---|
| P-02, P-03, P-03b, P-04, P-05, P-06, P-07 | stay closed |
| F-01, F-02 | stay closed |
| F-03 | closed |
| F-05 | closed |
| F-06 | closed |
| F-07 | **open**, 2 members: cep_refund_keep_milk baseline ≠ fall-through; departure_lunch unreal "not attending" tier |
| P-01 | **reopened** as P-01r through coll_year_end_notice (stale notice read as carried charges against base s6; R6 condition 3) |

New in revision_4:
- **P-08** (rule "days" vs compute purchase lines in all 16 milk/second-meal schedules).
- **P-09** (CEP keep defined as "what the household asks" and by the schedules).

Observations:
- O-12: the coordinator ruling cited by the reworker is not in the auditor's inputs.
- O-14: the transfers' fixed "purpose the household states".
- R6-WAIVED ×6.
- Carried forward: O-2, O-3, O-6, O-7, O-8.

### closing_checklist (revision_4)
Written after both revision-4 comparisons; nothing above in revision_4 was edited after the reveal.

| check | result |
|---|---|
| files and revisions | preserved |
| task 0 comparison | **PASS** on all four relationships |
| task 1 comparison | **RED** (SOURCE-POLICY P-01r, SOURCE-TASK, SOURCE-FACTOR) |
| coverage, disjoint scopes, tools | yes |
| GT equals the blind derivation | yes in both tasks; task 1 equals reading A only |
| trees | n = 3 with 2 VI edges and a user write in each; acyclic |
| gates | the r4 snapshot is 7/7 green |

Final sweep of every class raised in revisions 1–4, across all eight policies:

| class | result |
|---|---|
| stale notice / base s6 (P-01) | **coll_year_end_notice** (only member; no other compute reads meal_notices) |
| overlap (P-02, P-07) | none |
| order (P-03, P-03b) | none |
| framing (P-04, B8) | **departure_lunch "not attending"** (only member) |
| ties (P-05) | none |
| grouping (P-06) | none |
| rule vs compute edges (P-08) | **16 milk/second-meal schedules** (days vs lines) |
| two definitions of one quantity (P-09) | **CEP keep** (only member; the transfers' fixed purpose is O-14) |
| A7 (F-01) | none |
| A3 (F-02) | none |
| A6/labels (F-03) | none |
| realism X1/X4 (F-04) | none; R6 ×6 waived, coll_year_end_notice failed |
| counts (F-05) | none |
| X2 (F-06) | none |
| baselines/tiers (F-07) | **cep_refund_keep_milk, departure_lunch** |
| persona steering | **task 1 only** |

The difficulty does not pass.

VERDICT revision_4: task0=PASS task1=RED charter=P-01r,P-08,P-09,F-07

---

## revision_5

### charter_global_frozen (revision_5)
- Frozen 2026-10-24T23:32Z, before any revision-5 task JSON was read, independent auditor.
- Entry checks:
  - The last non-blank line of worklog.md is `REWORK round 5: gates 7/7 green`.
  - The snapshot /tmp/erl0078_coord/snap_meal_account_and_benefits_r5.txt was run by the auditor (execute-only). All seven gates are OK.
- Hashes:
  - meals.extended.yaml: ac7e1932eac0b7fa (changed; a copy is kept in scratch r5/r5.yaml).
  - task_tools.py: 3be73c39ed425255 (unchanged, so the tool conclusions carry forward on that hash).
  - r5/0.view.json: bf231a888dd03c9a (equal to r4: persona, world and frozen_time unchanged).
  - r5/1.view.json: b9a3fdb4ac26bbbe. Persona changed; the world changed on Samuel (à la carte lines on 09-30 and 10-01, re-identified lines, notices re-seeded) and Grace (deposit raised).
- Read in this revision:
  - the "REWORK round 5 claims", by id, figures masked;
  - realism_bar.md, read in full, including AMENDMENT 2 (split prorations; meal-forecast shape accepted for transfers and keeps only where the persona states the purpose and nothing the rules decide; X3 component exclusions);
  - owner_ruling.md;
  - XF_recipe.md.
- AMENDMENT 2 now records the O-12 ruling, so the revision-4 note that it was missing is resolved.
- Base copy: identical. B5: clean. Prerequisite graph: unchanged (8 edges, acyclic). No ordering sentence lies outside its blocked rule. P-07 two-way tails and P-02 scope tails are present.

### re-derived checks (revision_5)
- **P-01r closed.** No compute reads meal_notices; checked by script over all 8 policies. coll_year_end_notice is gone, so base s6 governs every balance.
- **P-08 closed.** All 16 milk and second-meal schedules now read "rung up four (regular_buys) or more times" / "one to three purchases", which matches `COUNT` of purchase lines. No remaining "days" in any rule is anything but a serving-day, calendar-day or lead-day count; checked by script.
- **P-09 closed.** "The CEP refund leaves on the account a keep ... as the schedules below count it ...; the keep is defined only by those schedules", and the standard is "the account's whole balance, with nothing kept and no deposit held back". There is one definition.
- **F-07 closed.**
  - Every factor's fall-through tier equals its baseline: 42 factors checked by script, including cover/rollover_serving_days, whose fall-through is now "outside July 2026 through June 2027 → K('days_week')".
  - cep_refund_keep_milk's baseline is nothing.
  - departure_lunch is removed. The departure's lunch is a plain amount at "the account's campus" under base pricing, which follows base meals_meal_pricing more closely; the receiver is non-CEP by scope. No "not attending" premise is left.
- **Persona (task 1) closed under AMENDMENT 2.** The persona states the purposes ("Grace's leftover to go first toward anything one of the kids still owes and then toward that child's meals and extras for the rest of this month, and Daniel's toward meals and extras through the end of November"; Esther's keep "for her milk, the second helpings she buys and her snacks for the rest of this month"). It names no receiving account and no amount. The June-letter line is gone. O-15 (task 0) is closed under the same amendment.
- **Factor sweep.** Counts (P/M): prepayment 5 (3/2), cover 5 (3/2), netting 5 (3/2), inactive 5 (4/1), cep 5 (3/2), collection 6 (5/1), departure 5 (3/2), graduate 6 (4/2).
  - One serving-day factor or plain count per computation; no X2 split (AMENDMENT 2).
  - The milk and second-meal methods pass A6 (price × counted days vs the month's recorded spend once vs nothing).
  - Breakfast parameters have three distinct values. Snack factors read the month's or the earlier month's recorded spend.
  - T1/T2 hold: every multiplying count has a nonzero baseline, either the plain CEP days left or 20/5.
  - Realism: lunch, breakfast, milk, second-meal and snack factors are R1; serving days R3; holds R2; size and up-front R5. The forecast shape on transfers and keeps is accepted under AMENDMENT 2, with every task persona stating the purpose.
  - R6 grading, conditions 1–6, all hold for plan_household_students, plan_school_calendar, plan_last_payment, coll_household_students, coll_school_calendar, coll_last_payment and coll_campus_level. coll_campus_level is keyed on the enrolled campus level, a published key; it is round (+1/+2), conflicts with nothing, and is no named X1. Its dimension is not used by another factor, and the count is 6 drawn − 2 honest = 4. All 7 are **R6-WAIVED (BLUEPRINT-KNOWN)**.
- **Final sweep, every class raised in revisions 1–5, across all eight policies:**

| class | result |
|---|---|
| stale notice / undeclared override (P-01) | none |
| overlapping subjects (P-02, P-07) | none |
| order statements (P-03, P-03b) | none |
| framing / promise / B8 (P-04, the departure-lunch premise) | none |
| tie rules (P-05) | none |
| grouping (P-06) | none |
| rule-vs-compute edges (P-08) | none |
| double definitions (P-09) | none |
| A7 (F-01) | none |
| A3 (F-02) | none |
| A6 / labels (F-03) | none |
| realism X1/X2/X4 (F-04, F-06) | none |
| counts (F-05) | none |
| dishonest baselines / dead tiers (F-07) | none |
| persona carrying rule-decided facts | none |

### observations (revision_5)
- O-14: each transfer rule states its purpose as "the purpose the household states when it agrees: to …". The rule applies that purpose whatever the household says, and AMENDMENT 2 accepts it only where the persona states it. Both task personas do.
- O-16: the CEP keep applies even if a household asks to keep nothing. Accepted here because the task-1 persona asks for exactly that keep (AMENDMENT 2).
- O-17 (seed): Samuel's charge_limit_reached notice is dated 2026-10-13, while the middle-school limit was crossed on 2026-10-12 by the returned check. No compute reads notices.
- Carried forward: O-2, O-3, O-6, O-7, O-8.
- R6-WAIVED ×7.

### closing_checklist (revision_5)
Written after both revision-5 comparisons; nothing above in revision_5 was edited after the reveal.

| check | result |
|---|---|
| per-task files | match tasks one-to-one; revisions 1–5 preserved; every revision-5 comparison carries PASS on all four relationships |
| coverage | all 8 extended policies covered; scopes pairwise disjoint (task 0: netting, cover, inactive repayment, prepayment; task 1: departure, collection, graduate, CEP refund) |
| tools | 8 task tools with independent, frozen uuid8s; tool contracts unchanged (3be73c39ed425255); bodies judge no prerequisite |
| trees | each has 3 prerequisite problems with 2 value_input edges and at least one owner=user write (task 0: 2; task 1: 1), owner ruling (b) met; whole-difficulty graph acyclic |
| computations | each declares a self-sufficient baseline and 5–6 factors with ≥ 2 parameter and ≥ 1 honest method; every ladder ≥ 3 distinct tiers stated in its rule, fall-through = baseline, T1/T2 hold |
| task-level factor floors | each task keeps a multi-source factor (holds) and a cross-difficulty factor (enrolled-campus lunch) |
| realism | every factor is R1/R2/R3/R5, or R6-WAIVED (7, BLUEPRINT-KNOWN, AMENDMENT 1); forecast shape accepted under AMENDMENT 2 |
| GT | equals the independent derivation in both tasks, every argument and every sensitivity figure |
| gates | the r5 snapshot (/tmp/erl0078_coord/snap_meal_account_and_benefits_r5.txt) is 7/7 green on this final form |

The final sweep of every class raised in revisions 1–5 finds no member (table in revision_5 re-derived checks). Observations O-2, O-3, O-6, O-7, O-8, O-14, O-16 and O-17 and R6-WAIVED ×7 are recorded; none is grounds for rework.

The difficulty passes the source-layer audit at revision_5.

VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

---

## revision_6

### charter_global_frozen (revision_6)
- Frozen 2026-10-24T23:46Z, before any revision-6 task JSON was read, independent auditor.
- Entry checks:
  - The last non-blank line of worklog.md is `REWORK round 6: gates 7/7 green`.
  - The snapshot /tmp/erl0078_coord/snap_meal_account_and_benefits_r6.txt was run by the auditor (execute-only). All seven gates are OK.
- Hashes:
  - meals.extended.yaml: d1df998776a54820 (changed; scratch copy r6/r6.yaml).
  - task_tools.py: e0d10ca5800524d3 (changed: docstrings only).
  - r6/0.view.json: bf231a888dd03c9a and r6/1.view.json: b9a3fdb4ac26bbbe, both equal to r5 (worlds, personas and frozen_times unchanged).
- Items this round: the renderer's scan-first findings in audits/render_source/meal_account_and_benefits/render_r1.md (F1–F4), read in full, plus the "REWORK round 6 claims" by id with figures masked.
- Rulings applied: realism_bar.md (AMENDMENT 1 and 2), owner_ruling.md, XF_recipe.md.
- Method: a structured diff of r5 → r6 over every policy (rule sentences, compute, compute_basis, factors, baseline). The base copy is unchanged. B5 is clean.

### auditor's own miss (disclosed)
**Renderer F1 should have been caught in my revision_5.** There, `w_lunch_charge` was a plain campus-priced binding while baseline.rule said "the elementary lunch charge". I recorded the plain lunch as following base pricing more closely, but never checked it against baseline.rule. My all-baseline departure figure in revision_5 (computed with the secondary lunch) therefore did not equal what baseline.rule states. This is an audit miss, recorded rather than rewritten; the revision_5 text is left untouched.

### renderer items (revision_6)
- **F1: closed.**
  - baseline.rule now reads "of one reimbursable lunch at the lunch charge the departure rollover counts" and carries the plain sentence: "The lunch charge the departure rollover counts is the student's charge under the district's meal pricing at the account's campus: the secondary lunch charge ... at Ridgecrest ..., Calloway Creek ... or Mesquite Ridge ..., and the elementary lunch charge of the status at any other campus not listed in cep_campuses". baseline.params now list both lunch charges.
  - The computation document and compute now agree. On the task-1 world, the all-baseline departure is 20 × 3.45 − 46.15 = 22.85, which equals the DSL figure.
  - Class sweep, every plain binding of all 8 policies against its baseline.rule: no other plain binding reads a price, a parameter or a record beyond the balance and the result clamp. No other member.
- **F2: closed.**
  - The CEP sentence "The CEP refund leaves on the account a keep for the student's milk, second meals and snacks ... together with every deposit not yet cleared; the keep is defined only by those schedules." is removed.
  - The CEP assembly sentence is generic: "first every amount the schedules keep is added together, which gives the keep; then the keep and every deposit the schedules hold back are subtracted from the account's balance".
  - The netting opening, which listed the keep and hold quantities, now reads "with the household's agreement and for the purpose it states for the giving account's own student: part of another active account's balance is moved by sibling transfer to that student's account".
  - Class sweep: the remaining openings of the cover, graduate and departure rollovers, and the prepayment's first baseline sentence, state the household's purpose as a generic phrase ("meals and the items the student buys on their own", with "snacks included" in the two rollovers). The renderer's scan passed them. AMENDMENT 2 requires the purpose to be stated and none is an assembly inventory, so they are recorded as observation O-18, not RED.
- **F3: closed.**
  - The CEP refund has no plain serving-day count any more. Each per-day factor owns its count: cep_refund_keep_milk's bindings include em_left_* … em_days_left, and cep_refund_keep_second_meal's include es_left_* … es_days_left.
  - Baseline: the whole balance, nothing kept, nothing held. The computation document is a plain whole-balance calculation with no orphan multiplication.
  - The one calendar sentence ("The serving days the keep counts left in the month of the refund date are ...") is quoted by both factors' compute_basis. It belongs to two factor documents and to no baseline; A3 is satisfied, A1 is satisfied (no factor reads another's binding). Observation O-20.
  - Method shapes still pass A6 (price × the factor's own days / spend once / nothing). T1/T2 hold.
- **F4: closed.** The transfer_idle_sibling_balance_b810dc58 docstring now reads "to a sibling's active meal account in the same household", with no "that carries unpaid meal charges". Class sweep of all 8 docstrings against their rules (B6): the deposit (active account), inactive plan, cover (purpose matches the rule), CEP (CEP campus, household request), active plan, graduate and departure. None adds a condition its rule lacks. The departure docstring's "a sibling's active meal account" is broader than "youngest active student whose account's campus is not listed in cep_campuses" but adds no condition.

### regression sweep (revision_6)
- Every class raised in revisions 1–5 was re-run across all 8 policies on the r6 charter. Findings:

| class | result |
|---|---|
| P-01 stale notice | no compute reads meal_notices |
| P-02 / P-07 tails | present (5 tail sentences) |
| P-03 / P-03b order sentences | only in blocked rules; graph unchanged, 8 edges, acyclic |
| P-04 framing | none |
| P-05 ties | none |
| P-06 grouping | none |
| P-08 "purchases" vs counted lines | matches in all 16 schedules |
| P-09 single CEP keep definition | holds (the double sentence is removed) |
| A7 / T2 | holds; the CEP per-day factors carry nonzero own counts |
| A3 | holds |
| A6 / labels | hold |
| X1/X2/X4 | none; one serving-day factor per computation, CEP counts owned by their factors |
| F-05 counts | unchanged: 5/5/5/5 and 5/6/6/5, each ≥ 2 P, ≥ 1 M |
| F-07 fall-through = baseline | holds for all 42 factors |
| B6 docstrings | hold |

- R6-WAIVED ×7: unchanged.
- No figure of either task changes: DSL replay on both unchanged views reproduces every revision-5 value and sensitivity.

### observations (revision_6)
- O-18: generic household-purpose phrases name item categories, required by AMENDMENT 2.
- O-19: the baselines do not restate the result clamp or rounding sentence ("raised to the online deposit minimum ...", "never below nothing, rounded half up ..."). Those live in each rule's result sentence, which the computation document covers through `result`. They are unchanged since revision_3, the renderer passed them, and there is no contradiction.
- O-20: the shared CEP calendar sentence is carried by two factor documents.
- Carried forward: O-2, O-3, O-6, O-7, O-8, O-14, O-16, O-17.

### closing_checklist (revision_6)
- Renderer F1–F4: each is closed. All four were genuine; none was disproved.
- No new defect. No regression of any class closed in revision_5 (sweep above).
- Disclosed:
  - the auditor's revision-5 miss of F1;
  - the revision-6 per-task ordering lapse (replay output not on disk before the reveal; worlds unchanged).
- Both tasks are PASS on all four relationships.
- Gates: the r6 snapshot is 7/7 green on the final form.

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN
