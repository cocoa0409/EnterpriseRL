# Policy-task audit — purchase_deposits_and_closing / charter-global

## charter_global_frozen

- Frozen: 2026-10-04T23:33Z, before any task's GT was revealed. Auditor: erl-task-policy-audit subagent (independent of the instantiator).
- Freeze hashes (re-computed by the auditor, equal to the brief's MANIFEST):
  - `tasks/purchase_deposits_and_closing/purchase.extended.yaml` sha256 `eef9d073183a3fea2d686ef0c93267ef3744868d57446a1319a1dd390829a9ac`
  - `tasks/purchase_deposits_and_closing/task_tools.py` sha256 `1207266b10e35d53da538defec468881325b922bb48ea3f0be0a5136790a94f0`
- Permitted and read: `blueprint/blueprint.yaml`, `blueprint/share_tools.py`, `blueprint/products/purchase.yaml` (plus the `homesite`, `design`, `lock` charters only for the cross-category parameters / seed plausibility), the extended charter, `task_tools.py`, the masked views `audits/_views/policy_task/purchase_deposits_and_closing/{0,1}.view.json`.
- Masked and not read for this section: every task field outside task_id / frozen_time / user_scenario / initial_state (evaluation_criteria, computations, db_closure*, design_rationale, prerequisite_closure, solvability_contract, charter_scope, required_documents), both worklogs, other difficulties' audits. No recursive search was run over `tasks/` or the scenario directory.
- Entry conditions (Step 0): the brief supplied the gate snapshot (check_extended / check_task_tools / replay_tasks / check_solvability / check_compute / check_grounding OK, check_cache_diff INFO, check_cross_fire SCOPE OK, check_traceability NOT OK with the stated reason: hidden task-tool names waiting for the published KB) and the masked-view manifest with hashes. The view hashes and the two artifact hashes were re-computed and match. The TRACEABILITY line is accepted as the declared pre-render state; it is not re-run here.
- Base copy: `purchase.extended.yaml` lines 1-978 are byte-identical to `blueprint/products/purchase.yaml` (diff shows only the added `extended_policies`), and every top-level key compares equal after YAML parse.

The charter has four extended policies:

| id | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- |
| P1 `purchase_ext_closing_delay_per_diem` | `assess_closing_delay_per_diem_8d15ee11` (agent) | amount | [] |
| P2 `purchase_ext_buyer_closing_extension` | `sign_closing_extension_addendum_c0ddd0a3` (user) | extension_days | P1, value_input, gate `last_charged_offset`, state form |
| P3 `purchase_ext_returned_payment_fee` | `assess_returned_payment_fee_3b45ee8d` (agent) | amount | [] |
| P4 `purchase_ext_returned_deposit_replacement` | `wire_replacement_deposit_5b0eb18e` (user) | amount | P3, value_input, gate `fee_count`, state form |

### policy_conflict_scan

- Subjects / tools: P1 and P3 both write `purchase_charge_assessed` but different `charge_type` (closing_delay_per_diem vs returned_payment_fee), different tools; P2 writes `purchase_closing_extended`; P4 writes `purchase_deposit_posted`. No two policies claim the same `(target_tool, computes)`.
- Triggers / eligibility: P1 "agreement in status closing_scheduled ... reason on the buyer's side" inherits base `purchase_closing_schedule`; P2 "agreement in status closing_scheduled" inherits base `extension_state` and `closing_extension_max`; P3/P4 inherit base `purchase_returned_payment` (`return_cure_window`, "Replacement funds must come by wire"). No two policies give opposite eligibility on the same object.
- Shared inputs read by more than one policy: (a) the studio options file — P1 counts `finalized or delivered` with thresholds 40,000 / 75,000; P4 counts `structural_closed, finalized or delivered` with thresholds 30,000 / 60,000. Different quantities (per diem multiplier vs deposit rate uplift), each fully stated in its own rule; not a conflict, but a cross-policy near-miss (a 68,450 option total is "mid" for P1 and "high" for P4). (b) closing extension fee charges — P1 reads them (end tier, grace tier), P2 says the fee "is charged when the request is received"; the charter has no policy that writes the fee, so both read a seeded record. Compatible.
- Terminal states: P1/P3 raise `buyer_charges_due`; P2 moves `scheduled_closing_date` and `closing_extensions_used`; P4 raises `earnest_money_held`. No overlap.
- Cross-category reads: P1 design (branch); P2 lock (existence); P3 homesite + design (history); P4 homesite (class param, occupancy, ledger) + design (branch). All inside the base `cross_category` boundaries; none writes another category.
- Scope partition (derived from the charter alone, to be confirmed against `charter_scope` after the reveal): the prerequisite graph has exactly two connected components, {P1 -> P2} and {P3 -> P4}. With M=2 and every tree spanning its root and its prerequisite, the only partition that is pairwise disjoint and jointly complete is one task per component. The worlds confirm the expected assignment (task 0: closing_scheduled agreement past its closing date with an extension fee; task 1: under_construction agreement with a returned deposit that has no fee charge yet).

### rule_compute_equivalence

P1 `purchase_ext_closing_delay_per_diem`
- `now_offset`, `period_days`, `billed_days`, `daily_rate`, `result`: quoted verbatim; RND once on the daily rate and once on the product, both "rounded half up to the cent" — equivalent.
- `first_day_offset`: three branches match the three rule clauses (completion > scheduled and stage complete; completion <= scheduled and notice lead < closing_notice_days; otherwise) — equivalent; offset arithmetic `closing_notice_days - notice_lead + 1` = "the day after the date that falls closing_notice_days calendar days after that notice".
- `last_day_offset`: rule "a closing extension fee charge dated after the scheduled closing date ... the latest such charge date"; compute takes the latest charge overall and requires `request_offset > 0`. If the latest charge is after the scheduled date it is also the latest of those after it, and if it is not, none is after — equivalent. Same argument for the default notice branch.
- `grace_days`: rule counts all closing extension fee charges (no date filter), compute counts all — equivalent.
- `deposits_in/out`, `deposit_cover_pct`, `cover_multiplier`, `options_multiplier`: equivalent.
- No invented basis; no empty promise found.

P2 `purchase_ext_buyer_closing_extension`
- `base_length`, `contract_slip`/`courtesy_days`, `reached_offset`, `reached_weekday` (2026-01-05 is a Monday, so residue 5 = Saturday, 6 = Sunday), `rolled_offset`, `result`: equivalent.
- `start_offset`: **not equivalent** — see finding F4. Rule tier 2 is "where no per diem has been charged, the scheduled closing date has passed and the home's estimated completion date falls after the scheduled closing date"; compute is `last_charged_offset if perdiem_count > 0 and last_charged_offset >= 0 else (completion_lag if now_offset > 0 and completion_lag > 0 else 0)`, which enters tier 2 also when per diem HAS been charged but its latest period ends before the current scheduled closing date. The condition "no per diem has been charged" lives in the rule only.

P3 `purchase_ext_returned_payment_fee`
- `agreement_returns` (12 months, the one being charged included), `stepped_fee`, `homesite_returns`/`design_returns`/`account_surcharge`, `returned_item`/`item_charge` ("above" = strict >, half of the wire threshold), `latest_payment_method`/`processing_charge`, `result`: equivalent.

P4 `purchase_ext_returned_deposit_replacement`
- `held_additional`, `premium_class_pct`/`premium_add`, `options_add`, `occupancy_add`, `rate_pct`, `additional_due`, `fee_count`/`security`, `lp_credit`, `lp_held`, `result`: equivalent.
- `financing_add`: rule "an outside-lender deposit stands on the ledger"; compute sums outside_lender_deposit posted without subtracting a returned one. Divergent only for a returned, unreplaced outside-lender deposit (observation O2).
- `lp_owed`: compute `... if lp_class_pct != None else 0` — the rule is silent for a buyer with no converted reservation (observation O1).
- `lp_adjust`: compute adds `lp_owed >= 0` to the excess branch and `lp_owed > 0` to the shortfall branch; neither guard is in the rule. With the current homesite class parameters `lp_owed` cannot be negative (Interior/Corner: pct 0, holding fee 0, extension fee 0; every other class's pct x floor premium exceeds holding fee + creditable extension fee), so the guards change no reachable value (observation O1).

### action_binding_and_uuids

- `(target_tool, computes)`: four distinct pairs, each claimed by exactly one policy.
- Docstrings: none states a position in a sequence, names another tool, or carries before/after/first/until; each describes one atomic effect. `sign_closing_extension_addendum_c0ddd0a3.extension_days` says "counted from the current scheduled closing date", which matches P2's `result` definition.
- Function bodies (task_tools.py lines 37-53, 95-106, 134-149, 186-202): each checks only that the agreement exists (P2 also that a scheduled closing date exists to move) and writes the passed values. None validates a prerequisite, amount, order, status or window.
- uuid8s: `8d15ee11`, `c0ddd0a3`, `3b45ee8d`, `5b0eb18e` — pairwise distinct, no common prefix, no sequential or adjacent pattern, no shared tail. No reuse or batch derivation is visible.

### prerequisite_graph

- `prerequisite` filled on all four (`[]` on P1 and P3).
- Edges: P2 -> P1, P4 -> P3. Both `problem` ids are extended policies in this file, neither is self or base. Graph acyclic (two disjoint chains of length 1).
- `policy_source` verbatim in the blocked policy's own rule: P2 rule contains "Where the buyer asks for the extension after the scheduled closing date has passed, the new closing date is set only after the ledger carries closing delay per diem for every day of buyer delay before the extension request was received." (exact); P4 rule contains "Replacement funds for a returned deposit payment are not figured until the ledger carries the returned-payment fee for every returned payment notified on the agreement." (exact).
- `form: state` on both, no `fallback_reason` on either — consistent.
- `kind: value_input`: gate `last_charged_offset` is a P2 compute binding feeding `start_offset`; gate `fee_count` is a P4 compute binding feeding `security`. Both exist.
- `resolved_by`: P1's and P3's `target_tool` respectively; their effects write exactly the rows the gates read (`charge_type=closing_delay_per_diem` with `period_end`; `charge_type=returned_payment_fee` dated today).
- `condition` vs sentence: P2's condition ("period_end is the day before the latest closing_extension_fee charge date") is what P1's own end tier produces when the ledger carries an extension-fee charge dated after the scheduled date, i.e. "per diem for every day of buyer delay before the extension request was received" given P2's "its closing extension fee is charged when the request is received". Neither strengthened nor weakened. P4's condition ("for every purchase_payment_returned row ... a purchase_charge_assessed row with charge_type returned_payment_fee naming that return's receipt number") equals the sentence.
- No authoring-viewpoint wording ("in this task", "at the opening") in either `prerequisite` block.

### prerequisite_sentences

Edge P2 -> P1:
1. Ordering connective "only after" joining P2's result ("the new closing date is set") to the waited-on state. Pass.
2. State form: "the ledger carries closing delay per diem for every day of buyer delay before the extension request was received" — a record-visible ledger state in finder words (ledger, closing delay per diem), no actor, no tool. Pass.
3. No tool name, policy id, snake_case token or row id. Pass.
4. Scope: conditional on "the buyer asks for the extension after the scheduled closing date has passed" — the same scope as the gate's use (tier 1 of the counting day only applies once a per diem period ending on/after the scheduled date exists). Pass.
- Exactly one write of this difficulty brings the state about: only P1 / `assess_closing_delay_per_diem_8d15ee11` writes `closing_delay_per_diem`. Pass.
- Derivation (one reading): sentence -> the reader looks for the rule that books closing delay per diem -> P1's rule ("A closing delay per diem is owed when the buyer has not closed on the scheduled closing date ...") -> P1's end tier "where the ledger carries a closing extension fee charge dated after the scheduled closing date, the period ends on the day before the latest such charge date" makes the booked period end the day before the request, exactly the span the sentence names.
- P2's rule carries no second wording of the dependency (its counting-day tier reads the booked per diem as an input, which is the value use, not a restatement); P1's rule does not restate the sentence. Pass.

Edge P4 -> P3:
1. Connective "not ... until". Pass. 2. State form: "the ledger carries the returned-payment fee for every returned payment notified on the agreement". Pass. 3. No tool/id tokens. Pass. 4. Scope "every returned payment notified on the agreement" = the condition. Pass.
- One write: only P3's tool writes `returned_payment_fee` charges in this difficulty. Pass.
- Derivation: sentence -> rule that charges the returned-payment fee -> P3 ("Each returned deposit payment carries one returned-payment fee charge ... The charge names the receipt number of the returned payment"). Single reading. P3's rule does not restate the sentence.

Base-rule cross-problem order sentences: base `purchase_closing_schedule` and `purchase_returned_payment` contain no "before/after" ordering between these problems ("Replacement funds and the fee must post within ..." is a joint deadline, not an order). No extended rule states an order that grounds no declared edge.

### override_declarations

P1 (refs: purchase_closing_schedule, purchase_plan_lot_changes, purchase_returned_payment, purchase_cancellation_refund)
- purchase_closing_schedule: "a closing_delay_per_diem of per_diem_usd per calendar day accrues from the day after per_diem_grace_days have elapsed, booked as one charge per delay period with its first and last day" — handled differently (start tiers, end tiers, grace tiers, rate multipliers); **declared** in `overwrite` with `replaced_by` naming first day, last day, grace days and daily rate. The base `formula.per_diem_days = max(purchase_msr_buyer_delay_days - per_diem_grace_days, 0)` and the measure window "through the frozen date" govern the same quantity; the replaced clause names "its first and last day", so the end day is inside the declared replacement (observation O4). "for a reason on the buyer's side", "booked as one charge per delay period", the default-notice sentence and the builder-delay "accrues no per diem" sentence are followed.
- purchase_returned_payment: "A returned deposit payment comes off the deposits held" — followed (deposits held subtracts "returned unpaid").
- purchase_plan_lot_changes, purchase_cancellation_refund: govern no quantity P1 scores; nothing followed or contradicted.

P2 (refs: purchase_closing_schedule, purchase_builder_delay)
- "each extension adds closing_extension_days calendar days to the current scheduled closing date" — handled differently; **declared**.
- "up to closing_extension_max times", "carries closing_extension_fee_usd as a closing_extension_fee charge", "written only on an agreement whose status is closing_scheduled", "must be at least closing_notice_days calendar days after the date of the closing_date_notice" — followed / not contradicted.
- purchase_builder_delay "the contract completion date stated at signing never changes; each stage update refreshes the estimated completion date" — followed by the courtesy tier.

P3 (refs: purchase_closing_schedule, purchase_plan_lot_changes, purchase_returned_payment, purchase_cancellation_refund)
- purchase_returned_payment "a returned_payment_fee of returned_payment_fee_usd is charged" — handled differently; **declared**. "Replacement funds and the fee must post within returned_payment_cure_business_days business days" — followed. Base event trigger `purchase_payment_returned -> purchase_charge_assessed {charge_type: returned_payment_fee, event_date: event_date}` is not a rule sentence; see observation O3.
- Other refs govern no P3 quantity.

P4 (refs: purchase_agg_concurrent_agreements, purchase_earnest_money, purchase_ratification, purchase_returned_payment)
- purchase_earnest_money "An additional deposit of additional_deposit_pct percent of the contract price is due after construction starts." — handled differently (rate plus uplifts); **declared**. "must post within additional_deposit_due_days", "Any single payment above wire_required_above_usd must be a wire" — followed.
- purchase_returned_payment "Replacement funds must come by wire" — followed (tool posts `payment_method="wire"`). The base does not fix the amount of replacement funds, so P4's security deposit and lot-premium squaring add to, and do not replace, a base sentence.
- purchase_agg_concurrent_agreements, purchase_ratification: no P4 quantity.
- Disguised forms: no anonymous intermediate (every intermediate is named in compute_basis); no 0/1 multiplier on a base-fixed amount; no dropped base branch. No "wrong value / algorithm to avoid" language in rule or compute_basis.

Result: no undeclared override.

### factor_ladders

| policy | factor | effect | decides | tiers (incl. fall-through) | distinct outcomes | multi-source tiers | cross_difficulty | stated in rule / in compute |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | delay_start | method | first_day_offset | 3 | yes (3 anchors) | tier 2 (agreement date + ledger notice); tier 1 two fields of one agreement row | — | yes / yes |
| P1 | delay_end | method | last_day_offset | 3 | yes | tier 2 (charge rows absent + notice row) | — | yes / yes |
| P1 | request_grace | parameter | grace_days | 3 | **collection-dependent** (F3) | no | — | yes / yes |
| P1 | studio_options_rate | parameter | options_multiplier | 3 | yes (1.25/1.10/1) | no (status and total on one design row) | design | yes / yes |
| P1 | deposit_cover_rate | parameter | cover_multiplier | 3 | yes (0.80/0.90/1) | ledger vs agreement price | — | yes / yes |
| P2 | extension_counting_day | method | start_offset | 3 | yes | tier 2 (ledger absence + agreement dates) | — | yes / compute drops a tier-2 condition (F4) |
| P2 | financing_base_length | parameter | base_length | 3 | yes (21/18/14 for Summit; 21/18/10 or 7 elsewhere) | **yes**: agreement financing_type AND lock row | lock | yes / yes |
| P2 | construction_slip_courtesy | parameter | courtesy_days | 3 | yes (14/7/0) | no (two dates of one agreement row) | — | yes / yes |
| P2 | weekend_closing_roll | method | rolled_offset | 3 declared | **no — Saturday and Sunday tiers select the same method** (F1) | no | — | yes / yes |
| P3 | repeat_return_step | method | stepped_fee | 3 | yes (fee x n / fee + 25 / fee) | no | — | yes / yes |
| P3 | other_account_returns | parameter | account_surcharge | 3 | yes (30/15/0) | **yes**: homesite ledger AND design ledger; tier 2 disjunction | homesite (+design) | yes / yes |
| P3 | large_item_pass_through | parameter | item_charge | 3 | yes (40/15/0) | no | — | yes / yes |
| P3 | return_processing_charge | parameter | processing_charge | 3 | yes (15/5/0) | no | — | yes / yes |
| P4 | financing_uplift | parameter | financing_add | 3 | yes (0.5/0.25/0) | tier 1 agreement + ledger; tier 2 single | — | yes / "stands" not netted (O2) |
| P4 | premium_class_uplift | parameter | premium_add | 3 | yes | no | homesite | yes / yes |
| P4 | studio_options_uplift | parameter | options_add | 3 | yes | no | design | yes / yes |
| P4 | occupancy_uplift | parameter | occupancy_add | 3 | yes (1.0/0.5/0) | no | homesite | yes / yes |
| P4 | repeat_return_security | parameter | security | 3 | yes (1%/0.5%/0) | no | — | yes / yes |
| P4 | lot_premium_squaring | method | lp_adjust | 3 declared | **no — all three tiers are the same signed true-up** (F2) | held (purchase ledger) vs owed (homesite class + homesite ledger) | homesite | yes / guards not in rule (O1) |

Counts as declared: P1 5 (2 method, 3 parameter); P2 4 (2 method, 2 parameter); P3 4 (1 method, 3 parameter); P4 6 (1 method, 5 parameter). Every `decides` is an intermediate (none is `result`); binding sets are pairwise disjoint within each policy. Every `baseline` block is the fall-through tier's value.

Counts after striking factors that fail the ladder tests (F1, F2; F3 strikes request_grace only on the collections it affects, not Summit):
- P1: 5 on Summit worlds (4 if request_grace is struck) — >= 4, >= 2 parameter, >= 1 method either way.
- P2: **3** factors (extension_counting_day method; financing_base_length, construction_slip_courtesy parameter) — below the floor of 4.
- P3: 4 (1 method, 3 parameter) — passes.
- P4: 5 factors, **0 method** — below the floor of 1 method.

Per-task multi-source / cross-difficulty availability: {P1,P2} has financing_base_length (multi-source, lock) and studio_options_rate (design); {P3,P4} has other_account_returns (multi-source, homesite+design) and four homesite/design factors.

Industry realness (conditions and outcomes): per-diem on buyer delay with a grace period, a later start when the builder's own notice was short or the home completed late, rate scaled by options held and eased by deposit cover; extension length by financing; courtesy days for construction slip; repeat-return step-ups, other-account surcharge, bank item pass-through, check vs ACH processing; additional deposit uplifts by financing, lot class, options, occupancy; security after repeated returns — each is a quantity a production builder plausibly prices this way, and each fall-through is the ordinary customer's published treatment. Exceptions recorded in F1-F3 and O2.

### findings

**F1 — SOURCE-FACTOR RED (charter-global; bears on task 0).** P2 `weekend_closing_roll` (effect `method`): its Saturday tier ("the new closing date is the following Monday, two days later") and Sunday tier ("the new closing date is the following Monday, one day later") select one and the same method — move the date to the following Monday; the "two days / one day" text is the distance that method yields from each weekday, not a different algorithm. The ladder is therefore two methods (roll to Monday / no roll) written as three tiers. Root cause: one weekend rule split by weekday. Evidence: extended.yaml P2 rule "A closing is never set on a weekend: where the day reached falls on a Saturday, the new closing date is the following Monday, two days later; where it falls on a Sunday, the new closing date is the following Monday, one day later; otherwise the new closing date is the day reached." and `factors[weekend_closing_roll].ladder`. Consequence: struck, P2 keeps 3 factors (< 4). Task 0's file demonstrates on its world.

**F2 — SOURCE-FACTOR RED (charter-global; bears on task 1).** P4 `lot_premium_squaring` (effect `method`): tier 1 "the excess held is taken off the replacement" adds owed - held (negative); tier 2 "the shortfall is added to the replacement" adds owed - held (positive); tier 3 "not adjusted" adds 0, which is owed - held when they are equal. All three tiers are the one signed true-up `lp_adjust = lp_owed - lp_held`, and compute writes the identical expression in both non-fall-through branches: `lp_adjust: "lp_owed - lp_held if lp_held > lp_owed and lp_owed >= 0 else (lp_owed - lp_held if lp_held < lp_owed and lp_owed > 0 else 0)"`. Root cause: a sign split presented as a method ladder. Consequence: struck, P4 has 5 factors and 0 `method` factors (< 1). Task 1's file demonstrates on its world.

**F3 — SOURCE-POLICY RED + SOURCE-FACTOR (charter-global; no consequence on either task's world).** P1's rule: "The grace days shrink once the buyer has asked to extend the closing: where the ledger carries two or more closing extension fee charges, the period has no grace days; where it carries exactly one, the period's grace days are its first grace_days_after_one_extension_request days; otherwise the grace days are the first per_diem_grace_days days." with `grace_days_after_one_extension_request: 1`. For a Pathway or Meadow agreement (`per_diem_grace_days: 0`) with exactly one extension fee charge, the "shrink" sentence gives grace <= 0 while the tier sentence gives 1 day — two passages, same situation, different conclusions; and a buyer who asked for an extension gets more grace than one who did not, a treatment no builder publishes. For a Heritage or Crestview agreement (`per_diem_grace_days: 1`) the one-request tier and the fall-through select the same value (1). Task 0 is a Summit agreement (`per_diem_grace_days: 2`), where the passages agree and the tiers are distinct; task 1 does not use P1. Recorded for the charter; not a task-level RED for either task.

**F4 — SOURCE-POLICY RED (charter-global, check 2; no consequence on task 0's world).** P2 `start_offset` drops the rule's tier-2 condition "no per diem has been charged" (quoted above). Situation: an agreement whose ledger carries a per diem whose latest period ends before the current scheduled closing date (booked before an earlier extension), whose scheduled date has passed again and whose estimated completion date is after it — the rule's ladder reaches "otherwise" (count from the current scheduled closing date, offset 0), compute reaches tier 2 (count from the estimated completion date, offset `completion_lag` > 0); the extension length differs by `completion_lag`. On task 0's world the per diem's period ends after the scheduled date, so both faces select tier 1.

Observations (no demonstrable consequence on any task world):
- **O1** P4 compute `lp_owed ... else 0` and the `lp_owed >= 0` / `lp_owed > 0` guards in `lp_adjust` have no rule sentence; unreachable with current homesite parameters (see rule_compute_equivalence).
- **O2** P4 `financing_uplift` tier 1's second condition ("an outside-lender deposit stands on the ledger") holds for nearly every outside_lender agreement that reaches a replacement (ratification requires the signing outside-lender deposit), so it adds little division; compute does not net out a returned outside-lender deposit although the rule says "stands". The task's multi-source requirement does not rest on this factor.
- **O3** Base event `purchase_payment_returned` declares a trigger writing `purchase_charge_assessed {charge_type: returned_payment_fee, event_date: event_date}`; a world in which a return has no fee row departs from that trigger, and P3's tool dates the fee "today", not the notification date. For the twelve-month counts used in this charter the two dates fall in the same window; no score changes.
- **O4** Base `formula.per_diem_days` / `purchase_msr_buyer_delay_days` ("through the frozen date") vs P1's baseline "through the day before the date the per diem is booked": the replaced clause names the period's "first and last day", so the end day is inside the declared override; recorded because the base formula block is rendered alongside.

## closing_checklist

Written after both reveals (first GT read 2026-10-04T23:36:03Z; the charter-global section above was on disk at 23:34:26Z, sha256 `56e6196cd968445500fd92d83b71da98fcd75f61b4c8f9db267e236efc286ab6`, and is unchanged). The difficulty is **not closed**: not every task passes all four relationships.

| item | status |
| --- | --- |
| per-task files 0.md, 1.md one-to-one with tasks; `_difficulty.md` alongside; first revision, no older revisions | yes |
| every comparison section carries a PASS | **no** — task 0: SOURCE-CHAIN RED, SOURCE-FACTOR RED; task 1: SOURCE-CHAIN RED, SOURCE-FACTOR RED |
| extended policies fully covered; scopes pairwise disjoint | yes — `charter_scope` task 0 = {P1, P2} + their two tools, task 1 = {P3, P4} + their two tools, matching the partition derived pre-reveal in §policy_conflict_scan |
| task tools and GT closed; uuid8s independent and frozen | yes (§action_binding_and_uuids; every GT write uses one of the four tools) |
| each tree: 1-3 prerequisite problems, >= max(n-1,1) value_input edges, an owner=user problem, no cycle; whole-difficulty graph acyclic | yes for structure (each tree n=1 with 1 value_input edge; roots P2 and P4 are user writes; two disjoint chains); both trees' discovery is undercut by persona pre-authorisations (T0-F2, T1-F2) |
| every computation: self-sufficient baseline, 4-6 factors (>= 2 parameter, >= 1 method), real ladders, every factor bears weight against an honest baseline, baseline alone != gold | **no** — P2 has 3 surviving factors (F1 / T0-F1); P4 has no surviving method factor (F2 / T1-F1); P1 and P3 pass; every declared factor bears weight on its world and every all-baseline number is definite and differs from gold (3,825.00 / 14 / 35.00 / 12,829.80); P4's factor proof misstates two figures by 0.01 (T1-F3) |
| per task >= 1 multi-source and >= 1 cross-difficulty factor, rows seeded | yes — task 0: financing_base_length (agreement + lock, cross lock), studio_options_rate (cross design); task 1: other_account_returns (homesite + design), plus premium_class / occupancy / lot-premium (homesite) and studio (design); all rows present and consistent with their charters. Both design_rationales call a single-row studio factor "multi-source" (observations T0-O2, T1-O1) |
| charter-level defects with no consequence on either world | F3 (P1 grace ladder vs "shrink" for Pathway/Meadow/Heritage/Crestview), F4 (P2 compute drops "no per diem has been charged"), O1-O4 |
| instantiation-stage gates re-run on the final form | not performed by this audit (Step 0: the auditor cites the supplied snapshot and does not run gates); the supplied snapshot shows TRACEABILITY NOT OK pending KB render |

Unresolved REDs for this difficulty, in order of severity: T0-F1 / T1-F1 (factor floors breached by unreal ladders F1, F2), T0-F2 / T1-F2 (persona pre-authorisations hinting at the prerequisite), T1-F3 (0.01 proof figure), charter F3 / F4 (no task consequence).

## revision_2

### charter_global_frozen (revision 2)

- Re-audit round 2, written before either task's round-2 GT was opened. Auditor: same erl-task-policy-audit subagent as round 1 (independent of the instantiator and the reworker).
- Shared inputs: `purchase.extended.yaml` sha256 `c831739f38161d8528832487bcad7f64b32b86408a3c4753671d6d2f4a329a89` (**changed** from round 1 `eef9d073...`), `task_tools.py` sha256 `1207266b10e35d53da538defec468881325b922bb48ea3f0be0a5136790a94f0` (unchanged). Because the charter changed, every charter-global section is re-derived in full below; the round-1 text above is preserved unchanged.
- Base copy: lines 1-978 still byte-identical to `blueprint/products/purchase.yaml` (re-diffed).
- Masked as in round 1; the worklogs and task JSONs were not read before this section and both task sections were frozen.
- Entry conditions: the brief supplied the round-2 gate snapshot (EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING OK, CACHE-DIFF INFO, SCOPE OK, TRACEABILITY NOT OK deferred to KB publication) and the rebuilt manifest; the four hashes were re-computed and match.

What moved in the charter (read off the new text; no round-1 copy of the file was kept, so this lists what the round-1 findings quoted and what now stands):
- P1: `grace_days_after_one_extension_request` removed; one-request tier now "the period's grace days are one day fewer than per_diem_grace_days, never fewer than zero" (rule, compute `MX(0, P('per_diem_grace_days') - 1)`, compute_basis and ladder agree).
- P2: weekend sentence now "A closing is never set on a weekend and moves to the nearest weekday: where the day reached falls on a Saturday, the new closing date is the Friday before it; where it falls on a Sunday, the new closing date is the Monday after it; otherwise the new closing date is the day reached."; compute `rolled_offset: reached_offset - 1 if Saturday else (+1 if Sunday else 0)`; `start_offset` tier 2 now carries `perdiem_count == 0`.
- P3: rule adds "and the charge is dated the day it is booked; a return whose fee has not yet been booked carries it from the day the return is next handled."
- P4: params `cash_rate_add_pct` 0.3, `premium_rate_add_high_pct` 0.6, `premium_rate_add_low_pct` 0.3, `options_rate_add_high_pct` 0.6, `options_rate_add_mid_pct` 0.3; financing tier now "that is outside-lender deposits posted exceed those returned unpaid" with compute netting returns; lot premium owed "is zero where the agreement has no converted Homesite Reservation"; squaring rewritten: excess "credited against the replacement but never by more than those applied reservation credits"; shortfall "the whole shortfall is added"; compute `lp_adjust: 0 - MN(lp_held - lp_owed, lp_credit) if lp_held > lp_owed and lp_credit > 0 else (lp_owed - lp_held if lp_held < lp_owed else 0)`.

### policy_conflict_scan (revision 2)

Unchanged in substance from round 1: four policies, four distinct `(target_tool, computes)`, no opposite eligibility on a shared object, disjoint terminal fields, cross-category reads inside base boundaries. The P1/P4 studio thresholds still differ (40,000/75,000 vs 30,000/60,000) as distinct quantities. The P3 dating sentence is compatible with P4's "twelve months up to the replacement" count and with the tool, which dates the charge `ctx.now()`. Scope partition derivable from the graph is still {P1 -> P2}, {P3 -> P4}.

### rule_compute_equivalence (revision 2)

- P1: unchanged bindings equivalent as in round 1; `grace_days` new tier equivalent to "one day fewer than per_diem_grace_days, never fewer than zero".
- P2: `start_offset` now equivalent to the three-clause rule (tier 2 requires `perdiem_count == 0`) — round-1 F4 divergence gone. `rolled_offset` equivalent to the Saturday/Sunday/otherwise sentence (2026-01-05 Monday reference: residue 5 Saturday, 6 Sunday).
- P3: unchanged compute; the new dating sentence is realised by the tool (`event_date=ctx.now()[:10]`) and by `within_months=12` anchored on the booking date — no empty promise.
- P4: `outside_deposit_held` now nets returns, equivalent to "posted exceed those returned unpaid"; `lp_owed ... else 0` now has its rule sentence ("is zero where the agreement has no converted Homesite Reservation"); `lp_adjust`: rule tier 1 (excess credited, capped at applied reservation credits) = `-MN(held-owed, credit)`; the compute's extra `lp_credit > 0` guard gives 0, which is what the rule's cap at zero credits gives — equivalent; tier 2 `owed - held` uncapped = "the whole shortfall"; else 0. No invented basis found.

### action_binding_and_uuids (revision 2)

`task_tools.py` unchanged (hash equal); round-1 conclusions carried forward by hash: four distinct pairs, no ordering words in docstrings, no prerequisite checks in bodies, uuid8s `8d15ee11`, `c0ddd0a3`, `3b45ee8d`, `5b0eb18e` independent. One cross-check against the changed charter: P2's Saturday tier can shorten the reached length by one day; the result is still >= base length + courtesy - 1 >= 6, a positive integer as the tool's `extension_days` contract requires.

### prerequisite_graph and prerequisite_sentences (revision 2)

Both `prerequisite` blocks are textually unchanged (P2 -> P1 `last_charged_offset`, P4 -> P3 `fee_count`, both state form); each `policy_source` is still verbatim in its blocked rule; gates exist in compute; graph acyclic. Four-point test, single resolving write and single-reading derivation as in round 1. No new cross-problem order sentence: P3's added sentence orders the fee's date, not another problem.

### override_declarations (revision 2)

Same four declared overwrites, unchanged text. Sentence sweep repeated on the changed rules: P2's weekend move ("Friday before") still falls inside the declared `replaced_by` "moved off a weekend"; P4's capped squaring and new uplift values change no base sentence (base does not fix replacement funds). P3's dating sentence does not contradict a base rule sentence (the base trigger on `purchase_payment_returned` is an event mapping, round-1 O3). No undeclared override.

### factor_ladders (revision 2)

Changed rows only (all others as in round 1's table):

| policy | factor | effect | tiers | distinct outcomes | verdict |
| --- | --- | --- | --- | --- | --- |
| P1 | request_grace | parameter | 0 / per_diem_grace_days - 1 (floor 0) / per_diem_grace_days | distinct as rules; numerically equal where the floor bites: Pathway/Meadow (grace 0) all three = 0; Heritage/Crestview (grace 1) tiers 1-2 = 0 | real (a "less one day, never below zero" rule); "shrink" sentence now true in every collection |
| P2 | weekend_closing_roll | method | Saturday -> Friday before / Sunday -> Monday after / no move | three distinct moves (back one, forward one, none) | real nearest-weekday observance; label `method` accepted (the tiers change which neighbouring weekday anchors the date, as delay_start/delay_end change anchors) |
| P4 | lot_premium_squaring | method | excess credited, capped at applied reservation credits / whole shortfall added, uncapped / none | tier 1 and tier 2 now differ in algorithm (capped credit vs uncapped charge) | real; distinct |
| P4 | financing_uplift | parameter | 0.5 / 0.3 / 0 | yes | real; tier 1's deposit condition still near-universal for ratified outside_lender agreements (residual of O2) |
| P4 | premium / studio | parameter | 0.6 / 0.3 / 0 | yes | real |

Counts after the ladder tests: P1 5 (2 method, 3 parameter); P2 4 (2 method, 2 parameter); P3 4 (1 method, 3 parameter); P4 6 (1 method, 5 parameter). Multi-source and cross-difficulty availability per task as in round 1 (task 0: financing_base_length agreement + lock; task 1: other_account_returns homesite + design).

### findings (revision 2) — status of round-1 charter findings

- **F1 — closed.** Weekend tiers now select three different moves; P2 keeps 4 factors.
- **F2 — closed.** Squaring tiers now differ in algorithm (capped vs uncapped); P4 keeps a method factor.
- **F3 — closed** as a SOURCE-POLICY contradiction (the one-request tier can no longer exceed the fall-through). Residual observation **R2-O1**: in Pathway/Meadow all three grace tiers evaluate to 0 and in Heritage/Crestview the first two do; the factor divides no customer in those collections. Neither task is in those collections; no task consequence.
- **F4 — closed.** Compute tier 2 now requires no per diem charged.
- **O1 — closed** (rule sentence for the no-reservation case; guards now match the rule). **O2 — compute half closed**, near-universality of the outside-lender-deposit condition remains (observation). **O3 — addressed** by P3's dating sentence. **O4 — unchanged** (kept by the reworker; still an observation).

No new charter-global RED found.

### closing_checklist (revision 2)

Written after both round-2 reveals (first GT read 2026-10-05T00:16:47Z; the revision_2 charter-global section above was on disk at 00:16:08Z, the task sections at 00:16:42Z).

| item | status |
| --- | --- |
| per-task files one-to-one with tasks, `_difficulty.md` alongside, round-1 text preserved, revision_2 appended | yes |
| every comparison section carries a PASS | **yes** — task 0 and task 1 PASS on all four relationships in revision 2 |
| extended policies fully covered; scopes pairwise disjoint | yes — `charter_scope` {P1,P2} / {P3,P4} |
| task tools and GT closed; uuid8s independent and frozen | yes (tool module unchanged by hash) |
| trees: 1 prerequisite each, 1 value_input edge, user-owned root, acyclic; whole graph acyclic | yes |
| computations: self-sufficient baseline, 4-6 real factors (>= 2 parameter, >= 1 method), each bears weight, baseline != gold | yes — P1 5, P2 4, P3 4, P4 6; all-baselines 3,825.00 / 14 / 35.00 / 12,829.80 differ from gold |
| per task >= 1 multi-source and >= 1 cross-difficulty factor, rows seeded | yes |
| round-1 REDs | F1, F2, F3, F4, T0-F1, T0-F2, T1-F1, T1-F2, T1-F3 all closed |
| residual observations | R2-O1 (grace tiers coincide where per_diem_grace_days <= 1; no task in those collections), O2 near-universal deposit condition, O4 base per-diem formula rendered alongside, R2-T1-O1 evaluator half-cent rounding untested |
| instantiation-stage gates on the final form | not run by the auditor (Step 0); the round-2 snapshot supplied shows all correctness gates OK and TRACEABILITY NOT OK deferred until the KB is published — must be re-run after rendering |

The difficulty passes the source-layer policy-task audit in revision 2, subject to the deferred TRACEABILITY gate.
