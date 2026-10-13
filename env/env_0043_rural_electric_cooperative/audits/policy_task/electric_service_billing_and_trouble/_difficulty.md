# Policy-task audit — electric_service_billing_and_trouble / charter-global

## charter_global_frozen

- Freeze time: 2026-10-06T18:34Z (written before any task's GT was revealed; nothing in this section is derived from `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure` or the worklog).
- Auditor: independent policy-task auditor (erl-task-policy-audit), not the author of the artifacts.
- Frozen inputs (sha256, recomputed by the auditor, identical to `/tmp/orch43/views/electric_service_billing_and_trouble/HASHES.txt`):
  - `tasks/electric_service_billing_and_trouble/service.extended.yaml` = `b5acc07371693753414bf986728ce85aa4b41827825bff7c16c3d987ee8c4325`
  - `tasks/electric_service_billing_and_trouble/task_tools.py` = `ff5877cf4e82a693451f0c8ebc1bc4e9930161de8e013c88eb401766d2d20e5e`
- Fields read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/*.yaml` (service base charter plus the deposit, light, capital, line and arrange charters for the cross-category reads), the extended charter, `task_tools.py`, and the runtime evaluator used by the gates (`skills/erl-task-instantiate/scripts/check_compute.py`: `within_months=k` keeps rows with `0 <= MONTHS(date, NOW) < k`; `MONTHS` counts whole months, dropping one when the day number has not been reached; `CFIELD` returns the first holding of the customer in that category matching the filters). The masked views (`0.view.json`, `1.view.json`; only `frozen_time`, `user_scenario`, `initial_state`) were used for the per-task halves.
- Masked and unread before freeze: the whole of `tasks/*/tasks/*.json` beyond the views, and `tasks/electric_service_billing_and_trouble/worklog.md`. No recursive grep was run over `tasks/`.
- Entry conditions (Step 0): the gate snapshot `/tmp/orch43/snap_electric_service_billing_and_trouble.txt` was supplied with the commands and their output lines: check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all OK, check_cache_diff INFO, check_traceability deferred until the KB is published. The masked views and their hashes were supplied too. The base section of the extended charter (lines 1-1430) is byte-identical to `blueprint/products/service.yaml`; the only difference is one trailing blank line (`diff <(head -1430 service.extended.yaml) products/service.yaml` → `1430d1429 <`).

### policy_conflict_scan

Seven extended policies, two trees, as the auditor derived them from the charter and the two worlds (the masked `charter_scope` is compared after the reveal):

| Policy | target_tool / computes | owner | prerequisite |
| --- | --- | --- | --- |
| service_ext_late_charge_assessment | assess_late_charge_b4948c69 / late_charge_amount | agent | [] |
| service_ext_meter_error_refund | post_meter_error_credit_d380ee62 / refund_amount | agent | [] |
| service_ext_reconnection_payment | pay_reconnection_amount_66e1876e / payment_amount | user | late charge (value_input, gate month_charges); meter refund (value_input, gate month_credits) |
| service_ext_reconnect_fee | reconnect_service_ea86e786 / reconnect_fee_amount | agent | reconnection payment (state_gate) |
| service_ext_seasonal_minimum_settlement | bill_seasonal_minimum_25412e46 / adjustment_amount | agent | [] |
| service_ext_restore_payment | pay_restore_balance_91f3e2ab / payment_amount | user | seasonal minimum (value_input, gate minimum_line) |
| service_ext_seasonal_restore_fee | restore_seasonal_service_78495a78 / restore_fee_amount | agent | restore payment (state_gate) |

- Overlapping subjects. `service_payment` is the subject of both the reconnection payment and the restore payment. Their triggers do not overlap, because each is keyed to the account's lifecycle state: the reconnection payment applies to "service account is disconnected for nonpayment", the restore payment to "an idle seasonal or irrigation account". The two policies never reach different conclusions about one account. Each policy computes into a different tool, and the deposit ladders of the two give the same outcome for the same deposit state.
- Shared inputs. Several rules read the same records: the security deposit status (reconnection payment, reconnect fee, restore payment, restore fee), the area light status, LIHEAP rows, returned payments and late charges. Within a tree, the earlier write can change what a later rule reads. Tree A: the late charge and the meter error credit are parallel inputs to the reconnection payment. Tree B is a chain. Shared-balance parallel edges are taken up per task (task 0 shows that the late charge and the meter credit are order-independent).
- Cross-policy coherence (observation G15). The deposit amount that the reconnection payment and the restore payment add is paid as a service card payment onto `account_balance`. No write in the difficulty moves it to the deposit record. The next policy in the same tree (deposit security surcharge / deposit security addition) still reads the deposit record as `partially_paid` / `assessed with nothing held`.
- Time anchors. The late charge, the meter refund, the reconnection payment, the restore payment and the seasonal minimum all count windows in whole months from `NOW` (the current date). The inspection and pledge tests use calendar days. No two policies anchor the same quantity differently.
- Terminal states. The reconnect write sets `active` and clears the disconnect fields. The restore write sets `active`, clears `idle_date` and completes the order. No other extended write changes status.
- Cross-category read boundaries. Each policy's `cross_category` declaration matches the CFIELD calls of its compute: late charge→arrange; reconnection payment→deposit; reconnect fee→deposit, light; seasonal minimum→capital, line; restore payment→deposit, light; restore fee→deposit, light, capital.
- Scope exclusivity and completeness (derived from the worlds, pre-reveal). Task 0's tree spans {late charge, meter refund, reconnection payment, reconnect fee}. Task 1's tree spans {seasonal minimum, restore payment, restore fee}. The two sets are disjoint and together cover all seven extended policies.

### rule_compute_equivalence

Every compute binding of all seven policies was swept against its `compute_basis` quotation and back against the rule, sentence by sentence. Every quoted basis is a verbatim fragment of that policy's `rule`. Every ladder named in `factors[].ladder` appears as a rule sentence and as a branch of the `decides` binding. Every rule tier has a compute branch. The channel split of the cash-only tier is exhaustive over the `payment_channel` enum: the 5 accepted channels and the 5 subtracted channels together make up all 10 values. Two compute branches carry a condition the rule does not state:

1. service_ext_reconnection_payment, `pledge_selected`. Rule: "when that agency has posted payments in that month, the latest pledge less those payments, never below zero, is taken". Compute: `... if (pledging_agency_paid > 0 and same_agency_pledges >= 1) else pledges_month`. The extra conjunct `same_agency_pledges >= 1` has no basis in the rule. Situation: the latest pledge, 100.00 from agency X, is dated more than one whole month before NOW; X posted 60.00 in the month; no pledge is dated in the month. The rule gives 40.00; the compute gives `pledges_month` = 0.00 → finding G5.
2. service_ext_seasonal_restore_fee, `idle_late_count`. Rule: "when a late payment charge is dated after the idle date". Compute: `COUNT(... within_months=idle_months ...)`, which counts only charges dated less than `MONTHS(idle_date, NOW)` whole months before NOW. Situation: idle_date 2025-11-24, NOW 2026-04-07, a late charge dated 2025-12-01 (after the idle date). Then `MONTHS(2025-12-01, 2026-04-07)` = 4, which is not < 4. The rule adds the collection review; the compute adds nothing → finding G6. The restore payment's own idle late-charge sentence is written in whole-month form ("dated less than the whole months elapsed since the idle date before the current date") and is equivalent to its compute. The restore-fee sentence is not.

Approximations that do not reach a different conclusion in any situation the auditor could construct without leaving the declared scope (recorded, not red):
- service_ext_late_charge_assessment, `agency_of_payment`: the rule speaks of "the agency payments of that month" and the agency behind them. The compute keys on the agency of the latest agency payment only. The two diverge only in a month with payments from two agencies (observation G16).
- service_ext_meter_error_refund, `window_late_before_test`: the compute additionally requires the latest late charge to fall inside the window before leaving it out. A late charge outside the window is not in `window_late` anyway, so the result is the same.

### action_binding_and_uuids

- `(target_tool, computes)` pairs are all distinct. `payment_amount` is computed by two policies but into two different tools (`pay_reconnection_amount_66e1876e`, `pay_restore_balance_91f3e2ab`).
- Function bodies (task_tools.py). Each tool lands its rows and returns a receipt. No tool reads another record's state, refuses, raises or hints on an unresolved prerequisite. The only read is `_account`, used for customer_id and balance.
- Docstrings. No docstring names another tool, states a position in a sequence, or carries before/after/first/then/until/prior. The only hits for ordering words are "at once" (post_meter_error_credit, bill_seasonal_minimum), which means "immediately", not an order between tools.
- uuid8s: b4948c69, d380ee62, 66e1876e, ea86e786, 25412e46, 91f3e2ab, 78495a78. They are pairwise distinct, share no common prefix, carry no sequence, and none is a tail-variant of another. No sign of batch derivation.
- Two business readings? The two user payment tools have identical effects: one `service_payment` row, `phone_ivr_card`, dated today, balance lowered. They differ only in the id prefix (`pay_` vs `rpay_`, which changes the row id and so the final hash) and in the docstring scope. `pay_restore_balance_91f3e2ab`: "Pay toward your idle seasonal or irrigation service account". `pay_reconnection_amount_66e1876e`: "Make your own card payment on your electric service account", with no account-state restriction. See prerequisite_sentences / G8.

### prerequisite_graph

- `prerequisite` is filled on all seven policies (`[]` on late charge, meter refund, seasonal minimum). Every `problem` names another extended policy id in this file, never a base policy and never itself. Graph: reconnect_fee → reconnection_payment → {late_charge_assessment, meter_error_refund}; seasonal_restore_fee → restore_payment → seasonal_minimum_settlement. It is acyclic, and no edge crosses between the two trees.
- `policy_source` of all five edges is verbatim in the blocked policy's own `rule` (located by string match).
- `form: state` on all five edges; no `fallback_reason` (correct for the state form).
- `kind`/`gate`:
  - value_input `month_charges`, `month_credits` (reconnection payment) and `minimum_line` (restore payment) are real compute bindings of the blocked policy.
  - state_gate `service_evt_reconnect.past_due_covered` (reconnect fee) is a real base eligibility gate. Its condition ("payments posted since the notice date ... reach the disconnect_past_due_amount ...") is not the edge's condition ("a service_payment row dated the current date, for at least the reconnection payment").
  - state_gate `service_payments.amount` (restore fee) is a column, not an eligibility gate (`service_evt_seasonal_idle` has `eligibility: []`).
  - Neither gate label changes what an agent does → observation G9.
- `condition` vs sentence: all five conditions carry the sentence at its own strength. Neither is strengthened or weakened.
- `resolved_by` equals the depended-on policy's `target_tool` on every edge, and that tool's body creates exactly the row the condition names (service_late_charge row / service_bill_credit with credit_reason meter_error_refund sourced on the test / service_payment dated today / service_usage_charge annual_minimum_adjustment dated today).
- No authoring-viewpoint phrasing ("in this task", "at the opening") appears in any `prerequisite` field.

### prerequisite_sentences

Four-point test, single-write test and derivation per edge:

1. reconnection_payment ← late charge. Sentence: "The reconnection payment is fixed only after every bill left unpaid past its due date carries its late payment charge line on the account."
   - Four points: connective "only after". The state names the record (a late payment charge line per unpaid bill), with no action, performer or tool. No tool, id or snake_case token. Scope "every bill" equals the condition "Every billing period whose bill remained unpaid after its due date".
   - Single write: only `assess_late_charge_b4948c69` creates `service_late_charge` rows.
   - Derivation: the reader looks for the policy whose rule produces "late payment charge lines". That is service_ext_late_charge_assessment ("The late payment charge is figured on the most recent bill ..."). Its rule defines which bill is charged and when ("once the current date is later than that bill's due date"), and that a bill whose late-charged amount is zero carries no line. So the state is reached by charging the most recent bill past its due date. Older bills whose extended late-charged amount comes to zero need no line (checked on both worlds, see the task files).
   - The depended-on rule does not restate the sentence. PASS.
2. reconnection_payment ← meter refund. Sentence: "The reconnection payment is not worked out until every meter test on the account that found the meter fast carries its meter error refund credit."
   - Four points: connective "not ... until". State: a credit per fast test. Scope "every" equals the condition.
   - Single write: only `post_meter_error_credit_d380ee62` creates bill credits.
   - Derivation: the policy whose rule "settles" a fast test by a "meter error refund ... posted as one bill credit ... whose source is the meter test" is service_ext_meter_error_refund. PASS.
3. reconnect_fee ← reconnection payment. Sentence: "The reconnection, and the reconnect fee billed with it, is made only after a payment at least equal to the reconnection payment the account requires stands on the account, posted on the day of reconnection."
   - Four points pass. "the reconnection payment" is a business term defined by service_ext_reconnection_payment's rule ("is told the reconnection payment, the amount the member pays on the spot toward reconnection"), not an id.
   - Single-write test fails at DB level. Two writes of this difficulty bring the waited-on state about. `pay_reconnection_amount_66e1876e` and `pay_restore_balance_91f3e2ab` both post a `service_payment` dated today for an arbitrary amount on any `service_account_id`, with no state check. The policy hop is unique (only one rule defines "the reconnection payment"). The tool hop is fixed only by docstring scope → finding G8.
4. restore_payment ← seasonal minimum. Sentence: "The restore payment is fixed only after the account carries the annual minimum adjustment line its closed season owes, dated after the account went idle."
   - Four points pass.
   - Single write: only `bill_seasonal_minimum_25412e46` writes `annual_minimum_adjustment`.
   - Derivation: the policy that "settles its seasonal minimum once its season has closed and the account stands idle ... an annual_minimum_adjustment line is billed for any shortfall" is service_ext_seasonal_minimum_settlement. PASS.
5. restore_fee ← restore payment. Sentence: "No idle account is re-energized, and no restore fee is billed, until the account shows a payment posted on the restore day that covers the restore payment it requires."
   - Four points pass ("until").
   - Single-write test fails at DB level, with the same two candidate payment writes as edge 3 → G8.

Other checks:
- No rule carries a second wording of any dependency, a tool name or another problem's id.
- No depended-on rule restates the sentence.
- No extended rule states a cross-problem order that grounds no declared edge. Sentences checked: seasonal minimum "once its season has closed and the account stands idle" (a lifecycle state, not another problem); restore fee "on the member's confirmed seasonal restore order" (a seeded order state).
- No tree rests on a base sentence.

### override_declarations

Checked sentence by sentence against every `base_policy_refs` entry. Below, "follows" means extended keeps the base sentence.

**service_ext_late_charge_assessment** (refs service_evt_late_charge, service_evt_program_charges)

- Follows: the due-date sentence, the "may be assessed only when ... later than" gate, the day-counting sentence, the waiver sentences (not its subject) and "never partly waived".
- Superseded and declared: the past-due-amount sentence ("payments posted on or before the due date") and the "late_charge_pct percent ... once per bill" sentence.
- **Undeclared conflict.** Base: "No late charge is assessed on a bill whose past-due amount is fully covered by an energy assistance pledge recorded on or before the due date". Extended deducts a pledge only when it is "the latest energy assistance pledge", "recorded no more than assistance_pledge_hold_days calendar days before the current date", and (for a full deduction) not met by agency payments in the month. Same situation, different conclusions: bill dated 09-07 for 200.00, due 09-27; a LIHEAP pledge of 250.00 recorded 09-02; nothing paid; NOW 10-05. Base: fully covered by a pledge recorded before the due date, so no late charge. Extended: the pledge is 33 days old, more than the 30-day hold, so nothing is deducted and a late charge of 1.5% of 200.00 = 3.00 is assessed. The base sentence is not named in `overwrite` → G7.
- service_evt_program_charges: "Program charges count toward the past-due amount and the late charge like any other charge" is named as superseded. Its `replaced_by` carries only the area-light exclusion. The rule also excludes arrangement installment and rebill lines (program charges) → observation G13. The sentence is named, so the departure is declared.
- The arrangement-installment exclusion "when the account's payment arrangement is active" is compatible with base "nor on the portion of a balance moved into an active payment arrangement".

**service_ext_meter_error_refund** (refs service_evt_late_charge, service_evt_meter_test, service_evt_bill_credits)

- The fast-meter refund sentence (and with it `service_msr_rebill_window_energy`, which it names) is superseded and declared.
- Follows: "No more than meter_error_rebill_max_months billing periods are ever corrected". The window is at most 6 whole months. But the meter-test-fee refund reaches fees up to twelve whole months old (observation G11).
- service_evt_late_charge "A late charge is never partly waived": the late-charge refund "at the overbilled share" refunds part of a late charge. It is not declared. It is posted as a meter_error_refund, not a late_charge_waiver, so the auditor records it as observation G10 (refund vs waiver).
- Follows service_evt_bill_credits: one credit per source per reason, amount from the source record.

**service_ext_reconnection_payment** (`overwrite: []`; refs service_evt_payments, service_evt_reconnect)

- service_evt_reconnect's "reconnected, only when payments posted since the notice date ... reach the disconnect_past_due_amount ..." is a necessary condition, so the extra amounts the extended policy requires do not conflict with it.
- The deposit-record sentence is followed.
- "never collected as a condition of reconnection": the reconnection payment carries no reconnect fee. Followed.
- service_evt_payments: oldest-first application, credit-balance carry-forward and the cash-only channel rule are followed (the tool pays by `phone_ivr_card`, an accepted channel).
- "An energy assistance pledge ... moves no money, it only holds disconnection ...": the extended pledge credit lowers the member's payment without moving money. The base itself already gives pledges a further effect in service_evt_late_charge, so the "only" is not absolute → observation G12.

**service_ext_reconnect_fee** (refs service_agg_member_balance, service_evt_reconnect)

- The crew-charge sentence and "never waived at the service desk" are superseded and declared.
- Follows: "billed on the next bill, never collected as a condition of reconnection, and is charged once per reconnection", the deposit-record gate, and the past_due_covered gate (necessary condition).
- service_agg_member_balance: "any other service account ... disconnected_nonpay is reconnected only on its own payment" is followed (single-account worlds).

**service_ext_seasonal_minimum_settlement** (refs service_evt_usage_billing, service_evt_minimum_bill)

- Superseded and declared: the December annual-minimum sentence and the "Power cost adjustment, sales tax and fees never count" sentence.
- Follows: the monthly-minimum sentences (not this quantity), "Minimum lines carry no kWh" (the tool writes kwh 0), and the billable-status gate (idle is billable).

**service_ext_restore_payment** (`overwrite: []`; refs service_evt_payments, service_evt_seasonal_idle)

- No base sentence governs a restore payment amount.
- The back-billing sentence of service_evt_seasonal_idle ("When the restore is ordered before seasonal_idle_min_months ...") is a separate quantity. It is not contradicted, and in task 1 it does not fire.

**service_ext_seasonal_restore_fee** (ref service_evt_seasonal_idle)

- "A restore is billed seasonal_restore_fee" is superseded and declared.
- Follows: "only on the member's confirmed service order" and the back-billing sentence.

Disguised forms:
- No anonymous intermediate factor overrides a base quantity outside the sentences above.
- 0/1 multiplier: the reconnect multiplier of zero is a full waiver, declared through the superseded "never waived" sentence.
- Dropped branch: base reconnect after-hours by order time is dropped by the declared crew-charge replacement.

### factor_ladders

Per policy: factors, effect labels, honest-label verdict, tier distinctness and business reality. Bindings were checked disjoint across the factors of each policy, and every `decides` is an input, not `result`. Every tier is stated in the rule and implemented in compute (see rule_compute_equivalence).

**service_ext_late_charge_assessment** — 6 factors

| factor | label | ladder outcomes | honest? | notes |
| --- | --- | --- | --- | --- |
| late_charge_rate_tier | parameter | 2.00 / 1.75 / late_charge_pct | yes | multi-source (late charges × returns) |
| pledge_deduction_from_late_charged_amount | parameter | full / pledge − agency paid / 0 | yes | |
| assisted_household_multiplier | method | ×0.75 / ×0.50 / ×1 | **no** | same formula `amount × rate × m`, only the number m differs → G1 |
| payments_applied_to_bill | method | three different payment sets | yes | |
| area_light_line_exclusion | parameter | rental / charge lines / 0 | yes | |
| arrangement_line_exclusion | parameter | rebill / installment / 0 | yes | cross_difficulty arrange |

Counts: parameter 4, honest method 1, cross-difficulty 1.

**service_ext_meter_error_refund** — 6 factors

| factor | label | ladder outcomes | honest? | notes |
| --- | --- | --- | --- | --- |
| rebill_window_length | method | N = months since accurate test / since connect / 6 | doubtful | only the number of months fed into one window sum changes (G1, PLAUSIBLE) |
| refund_base_lines | parameter | E+PCA+D / E+PCA / E | — | the PCA conjunct is met by every billed window, because `pca_applies: true` on all seven schedules and base usage billing bills the PCA line every period; the fall-through (= baseline) is unreachable for any refund that has an energy line → G3 |
| overbilled_share_method | method | e/100 ; (e−t)/(100+e−t) ; e/(100+e) | yes | |
| late_charge_refund_on_overbilling | parameter | full / × share / 0 | yes | |
| overbilling_interest | method | ×1.0184 / ×1.0092 / ×1 | **no** | number substitution → G1 |
| meter_test_fee_refund | parameter | in-window fee / 0.50 × earlier fees / 0 | yes | |

Counts: parameter 3, honest method 1, cross-difficulty 0.

**service_ext_reconnection_payment** — 5 factors

| factor | label | ladder outcomes | honest? | notes |
| --- | --- | --- | --- | --- |
| amount_owed_for_reconnection | method | four different formulas | yes | multi-source (reconnect fees × returns) |
| payments_counted_toward_reconnection | method | different payment sets | yes | |
| pledge_selection_for_reconnection | method | different pledge sets | yes | but see G5 |
| pledge_credit_toward_reconnection | parameter | full / capped at 100.00 / 0 | yes | |
| deposit_installment_with_reconnection | parameter | min(unpaid, required/count) / required / 0 | — | cross_difficulty deposit; the partially_paid outcome is not this business's own installment as its deposit charter publishes it → G4 |

Counts: parameter 2, method 3, cross-difficulty 1.

**service_ext_reconnect_fee** — 6 factors

- Parameter: crew_charge_for_reconnection, repeat_reconnection_surcharge, deposit_security_surcharge (cross deposit), site_inspection_charge, area_light_restoration_charge (cross light).
- Method: assisted_household_reconnect_multiplier (×0 / ×0.50 / ×1), which is a number substitution and **not honest** → G1.
- Counts: parameter 5, **honest method 0** (floor is 1), cross-difficulty 2.

**service_ext_seasonal_minimum_settlement** — 4 factors

- seasonal_minimum_rate_per_kva: parameter, cross line/capital. Tier 1's capital conjunct is entailed by its 120-month conjunct for any member holding an IR account (`capital_accounts.inactive_date` = "final date of the member's last service account in the class; empty while active") → observation G14.
- seasonal_minimum_capacity_measure: method (which quantity is measured: peak kW / twice peak kW / transformer kVA); honest. Mixes kW and kVA (observation G17).
- seasonal_minimum_credited_lines: parameter. Tier 1 (demand lines → F+E) and the fall-through (F+E+D, reached only when there are no demand lines, so D = 0 and the value is F+E) **select the same value in every world**. Tier 2's PCA conjunct is met by every billed IR account. Effectively a two-outcome ladder → G2.
- seasonal_minimum_proration: labelled method. The outcomes are months/12 or 1 fed into the same product, so it is doubtful (G1, PLAUSIBLE).
- Counts: parameter 2 (1 once credited_lines is struck, below the floor of 2), honest method 1, cross-difficulty 1.

**service_ext_restore_payment** — 5 factors

- Parameter: minimum_adjustment_hold_back, deposit_due_with_restore (cross deposit; its partially_paid outcome carries the same formula as G4), idle_season_late_charge_hold_back, area_light_lines_while_out (cross light).
- Method: uncleared_payments_added_back (different payment sets); honest.
- Counts: parameter 4, method 1, cross-difficulty 2.

**service_ext_seasonal_restore_fee** — 6 factors

- Parameter: restore_charge_by_meter, idle_period_inspection, deposit_security_addition (cross deposit), area_light_visit_on_restore (cross light), collection_review_on_restore (multi-source late × returns).
- Method: restore_fee_multiplier (×0.50 / ×0.80 / ×1), which is a number substitution and **not honest** → G1. Tier 2's capital conjunct is the same as in G14.
- Counts: parameter 5, **honest method 0**, cross-difficulty 2 (+ capital read, declared `cross_difficulty: null`).

Other structural checks, all policies:
- Every ladder has three or more tiers.
- No tier rests on a field that names the outcome.
- Every baseline rule is a sentence block of the rule, and its `params` keys are the ones it uses.
- Every factor's fall-through equals its baseline (by expression).

### findings

Charter-global findings. Each names the tasks whose file demonstrates its consequence.

- **G1 — SOURCE-FACTOR RED (mislabelled effect).** Symptom: factors labelled `method` whose tiers only change a number fed into one unchanged formula. Clear cases (CONFIRMED):
  - late charge `assisted_household_multiplier` (0.75 / 0.50 / 1)
  - meter refund `overbilling_interest` (1.0184 / 1.0092 / 1)
  - reconnect fee `assisted_household_reconnect_multiplier` (0 / 0.50 / 1)
  - restore fee `restore_fee_multiplier` (0.50 / 0.80 / 1)

  Doubtful cases (PLAUSIBLE): `rebill_window_length` (a month count) and `seasonal_minimum_proration` (n/12 vs 1).

  Root cause: the multiplier ladders are labelled by their prose ("the charge is ... times the multiplier") rather than by their effect. The `result` expressions `RND(... * assisted_multiplier, 2)`, `RND((...) * interest_factor, 2)`, `RND((...) * reconnect_multiplier, 2)` and `RND((...) * restore_multiplier, 2)` are one formula whatever the tier.

  Consequence: service_ext_reconnect_fee and service_ext_seasonal_restore_fee are left with **zero honest `method` factors** (the floor is 1).

  Bears on task 0 (late charge, meter refund, reconnect fee) and task 1 (restore fee, seasonal minimum proration).
- **G2 — SOURCE-FACTOR RED (unreal ladder, two tiers one value).** service_ext_seasonal_minimum_settlement `credited_lines`. Compute: `(year_facility + year_energy) if year_demand > 0 else ((... + year_pca) if (year_pca > 0 and year_demand == 0) else (year_facility + year_energy + year_demand))`. The fall-through is reached only with `year_demand == 0`, so it equals `year_facility + year_energy`, the value of tier 1. In addition, the PCA conjunct of tier 2 holds of every billed IR account (`pca_applies: true` on Schedule IR, as on every schedule). Striking the factor leaves the policy one `parameter` factor (floor 2). Bears on task 1.
- **G3 — SOURCE-FACTOR RED (condition holding of every customer reaching the write).** service_ext_meter_error_refund `refund_base_lines`. "power cost adjustment lines" in the window is met by every customer whose window carries an energy line. Base usage billing: "Where pca_applies the power_cost_adjustment line is calculated by the billing system ...", and `pca_applies: true` on all seven schedules. So the fall-through "energy charge lines of the window" (= the baseline) is never reached by a customer who has anything to refund, and tier 2 reduces to "no demand charge line". Bears on task 0.
- **G4 — SOURCE-FACTOR RED (tier outcome not what this business gives).** reconnection payment `deposit_installment_with_reconnection` tier 1, with the same formula in restore payment `deposit_due_with_restore` tier 2: "the smaller of its unpaid part and its required amount divided by its installment count". The cooperative's own deposit charter (`blueprint/products/deposit.yaml`, deposit_evt_payments) publishes the installment differently: "a first installment of first_installment_pct percent of the required amount ..., with the rest split evenly over the remaining installments due with the next monthly bills". It adds "Where installment_default_accelerates is true, an installment unpaid on its due date makes the whole unpaid remainder due at once". Every tier with installments has `first_installment_pct: 50` and `installment_default_accelerates: true`. "required / count" is neither the first installment, nor a later one, nor the accelerated remainder. Demonstrated on task 0 (see `0.md`).
- **G5 — SOURCE-POLICY RED (rule/compute, compute-only condition).** reconnection payment `pledge_selected`. The compute's `same_agency_pledges >= 1` is not in the rule. Situation and the two values are given in rule_compute_equivalence item 1 (rule 40.00, compute 0.00). Bears on task 0's policy; task 0's world takes tier 1, so no consequence there.
- **G6 — SOURCE-POLICY RED (rule/compute, window vs "after the idle date").** restore fee `idle_late_count`. Situation in rule_compute_equivalence item 2 (rule +collection review, compute +0). Bears on task 1's policy; task 1's only post-idle late charge (2025-12-13) is counted either way, so no consequence there.
- **G7 — SOURCE-POLICY RED (undeclared override).** Base service_evt_late_charge "No late charge is assessed on a bill whose past-due amount is fully covered by an energy assistance pledge recorded on or before the due date" vs the extended pledge-deduction ladder. Situation and values in override_declarations (base no charge, extended 3.00). Bears on task 0's policy. In task 0 the pledge does not fully cover the bill, so there is no consequence.
- **G8 — SOURCE-POLICY RED, PLAUSIBLE (state-form edge with two candidate writes).** The waited-on states of reconnect_fee ← reconnection_payment and restore_fee ← restore_payment ("a payment ... stands on the account, posted on the day ...") are each brought about by both `pay_reconnection_amount_66e1876e` and `pay_restore_balance_91f3e2ab`, whose bodies write identical rows apart from the id prefix. The sentence's business term ("the reconnection payment" / "the restore payment") singles out the policy. Only the docstrings' scope singles out the tool, and the generic docstring of `pay_reconnection_amount_66e1876e` does not exclude idle accounts. Consequence per task in `0.md` / `1.md`.
- Observations (no consequence demonstrable; not grounds for rework on their own):
  - **G9:** state_gate labels (`service_payments.amount` is a column; `service_evt_reconnect.past_due_covered` carries a different condition).
  - **G10:** late-charge refund at the overbilled share vs base "never partly waived".
  - **G11:** test-fee refund reaching fees up to 12 months old vs "No more than meter_error_rebill_max_months billing periods are ever corrected".
  - **G12:** pledge credit vs "it moves no money, it only holds disconnection".
  - **G13:** program-charge `replaced_by` omits the arrangement-line exclusion.
  - **G14:** capital patron-class conjunct entailed by the 120-month conjunct.
  - **G15:** a deposit amount paid as a service payment while the next rule surcharges the unpaid deposit.
  - **G16:** single-agency simplification in `agency_of_payment`.
  - **G17:** capacity measure mixes kW and kVA.
  - **G18:** the restore of an `ami_demand_ct` meter is priced as a crew visit ("a crew having to re-energize the current-transformer cabinet"), yet the restore write completes the order at once. The base lifecycle assigns the idle→active transition to the agent, so this is not treated as a fabricated wait.
  - **G19:** many claimed event types (outage report, trouble resolution, meter test, medical certificate, certificate update, cash-only flag, notice cleared, seasonal idle, returned payment) have no extended policy. This audit does not require them.

## closing_checklist

Written after both reveals (2026-10-06T18:39:43Z). Everything above this heading was frozen before them. **The difficulty does not close: neither task passes all four relationships.**

- Audit files: `0.md` and `1.md` correspond one-to-one with tasks 0 and 1, with `_difficulty.md` alongside. This is the first revision, so there are no older revisions. Each comparison section carries a verdict, and neither is PASS:
  - task 0: SOURCE-POLICY RED + SOURCE-FACTOR RED; problem tree PASS; unique solution PASS.
  - task 1: SOURCE-POLICY RED + SOURCE-FACTOR RED; problem tree PASS; unique solution PASS.
- Coverage and scope:
  - The revealed `charter_scope` matches the auditor's pre-reveal derivation. Task 0 has {late_charge_assessment, meter_error_refund, reconnection_payment, reconnect_fee}; task 1 has {seasonal_minimum_settlement, restore_payment, seasonal_restore_fee}. The two are pairwise disjoint and cover all 7 extended policies; each tree is contained in its own scope.
  - Task tools and GT are closed: each GT write calls its policy's `target_tool`.
  - uuid8s are independent (§ action_binding_and_uuids).
- Problem trees: task 0 has 3 prerequisite problems with 2 value_input edges; task 1 has 2 with 1 value_input edge. Each has one owner=user write. Both are acyclic, and the difficulty-wide graph is acyclic with no cross-task edge. **Holds.**
- Factors **do not hold**:
  - Every computation declares a baseline that alone gives a definite non-gold number, and every factor bears weight against an honest baseline on its world. Task 0: 23/23 factors, baselines 8.67 / 45.25 / 221.65 / 75.00. Task 1: 15/15, baselines 1644.56 / 1585.06 / 45.00.
  - But honest `method` counts fall below the floor of 1 for service_ext_reconnect_fee and service_ext_seasonal_restore_fee (G1).
  - service_ext_seasonal_minimum_settlement's credited-lines ladder has two tiers with one value, which leaves it 1 `parameter` (G2).
  - The refund-base PCA condition holds of every customer (G3).
  - The deposit installment outcome contradicts the deposit charter (G4).
  - The cross-difficulty deposit rows contradict their own charter in both tasks (T0-1, T1-1).
- Policy self-consistency **does not hold**: G5, G6, G7 (rule/compute and undeclared-override conflicts, shown on constructed situations; no consequence on either task's world) and G8 (two candidate writes per payment state; the author's single-write assertions are false).
- Gates: the instantiation-stage gates were not re-run by the auditor (Step 0 cites the supplied snapshot). The audited artifacts are unchanged since the snapshot: `service.extended.yaml` `b5acc07371693753…`, `task_tools.py` `ff5877cf4e82a693…`, both re-hashed at close. The final-form re-run belongs to the round that fixes the findings above.

## revision_2

### charter_global_frozen (revision 2)

- Freeze time: 2026-10-06T19:35Z, before either round-2 task file was revealed. Auditor: the same independent auditor as round 1.
- Shared inputs re-hashed:
  - `service.extended.yaml` = `8412b1ea98d66830ecbd0cc37aa793d2f2562e8fe8afb9a9146affd87d4ea1d5` (round 1: `b5acc073…`)
  - `task_tools.py` = `8f242f3262b4fba1321c42a95d40117ec581d2bd017465c4db5d449be7405793` (round 1: `ff5877cf…`)
  - Both match `/tmp/orch43/views/electric_service_billing_and_trouble_r2/HASHES.txt`.
  - Both changed, so every charter-global section below is **re-derived in full**, not carried forward.
- Blueprint: unchanged since round 1 (mtimes 11:15–11:20Z, before round 1; sizes identical). The base section of the extended charter is again byte-identical to `products/service.yaml` (only the trailing blank line differs).
- Gate snapshot `/tmp/orch43/snap_electric_service_billing_and_trouble_r2.txt` was supplied. All instantiation gates are OK (EXTENDED, TASK TOOL CONTRACT, REPLAY 90/90 and 56/56, SOLVABILITY, COMPUTE, GROUNDING, SCOPE); cache-diff INFO; traceability deferred.
- Masked for this revision: the round-2 `tasks/*.json` beyond the r2 views, and `worklog.md` (not read in either round). Searches were scoped to the extended yaml, task_tools.py and the views only.
- Disclosure: the auditor saw the round-1 GT of both tasks during round 1. Every round-2 figure below was recomputed from the round-2 rules and views. Where a figure equals round 1 (late charge 3.77, seasonal minimum 1512.57), that is because the inputs it reads did not change, and this is checked line by line.
- Method of change detection: the auditor kept no copy of the round-1 charter. The round-1 text it compares against is the round-1 report itself, which quotes the round-1 sentences and compute expressions.

### policy_conflict_scan (revision 2)

- The seven policies, their target tools, owners and the prerequisite graph are unchanged in shape. Tree A (task 0) is the late charge and meter refund → reconnection payment → reconnect fee. Tree B (task 1) is seasonal minimum → restore payment → restore fee.
- The subject overlap on `service_payment` is still partitioned by account state, and now also by the two tools' docstrings (see action_binding).
- Cross-policy deposit coherence (round-1 G15) is resolved:
  - The restore payment and the restore fee no longer read the deposit.
  - The reconnection payment adds the deposit remainder that the deposit charter itself makes "due at once and counts as past due on the service account". That wording comes from deposit_evt_payments and is now carried in the rule.
  - The reconnect fee's deposit factor reads `assessment_basis`, which a payment cannot change. So the round-1 situation of a surcharge for an unsecured deposit just after the member paid it can no longer occur.
- Cross-category reads now declared:
  - late charge → arrange
  - reconnection payment → deposit (record fields plus CPARAM tier parameters)
  - reconnect fee → arrange, deposit, light
  - seasonal minimum → line
  - restore payment → light
  - restore fee → light, line

  Each matches its CFIELD/CPARAM calls.
- No two policies reach different conclusions on the same subject.

### rule_compute_equivalence (revision 2)

Programmatic sweep:
- every compute binding has a `compute_basis` entry;
- every basis quotation is in its policy's rule (the meter refund's `result` basis is two rule sentences joined, as in round 1);
- every `baseline.rule` sentence and every `prerequisite.policy_source` is in its rule;
- every `overwrite.replaced_by` is in its rule.

Then a manual sentence-by-sentence sweep of the changed ladders:

- reconnection payment `pledge_selected`: the compute is now `... else (MX(0, latest_pledge_amount - pledging_agency_paid) if pledging_agency_paid > 0 else pledges_month)`, which matches the rule ("when that agency has posted payments in that month ..."). The round-1 extra conjunct is gone. **G5 closed.**
- restore fee review window: the rule now reads "otherwise it is the late payment charges dated less than the whole months elapsed since the idle date before the current date", which equals `within_months=idle_months`. **G6 closed.**
- New ladders, each with rule ↔ compute in both directions:
  - meter refund `energy_refund`: block-rate re-pricing;
  - reconnection payment `deposit_past_due` / `deposit_installment_due`;
  - reconnect fee `lookback_months` / `prior_reconnects` / `deposit_surcharge`;
  - seasonal minimum `minimum_rate` (late-charge conjunct) and `credited_lines` (demand-period count);
  - restore payment `facility_prepaid`;
  - restore fee `review_months` / `warranty_credit`.

  No compute-only condition or empty rule promise was found. In `deposit_installment_due` tier 2, the extra `deposit_installments > 1` is implied by a `partially_paid` record, so it is not a divergence.

### action_binding_and_uuids (revision 2)

- `(target_tool, computes)` pairs are unchanged and distinct. The uuid8s are unchanged (b4948c69, d380ee62, 66e1876e, ea86e786, 25412e46, 91f3e2ab, 78495a78) and remain independent.
- Function bodies are unchanged in behaviour. No tool reads another record's state, refuses or hints. There are no ordering words in any docstring (only "at once" = immediately).
- The two user payment docstrings now partition the account states:
  - `pay_reconnection_amount_66e1876e`: "toward getting power restored on your electric service account that stands disconnected for nonpayment ... it is not the line for an idle seasonal or irrigation account or for an account in service".
  - `pay_restore_balance_91f3e2ab`: "your idle seasonal or irrigation service account ... it is not the line for an account disconnected for nonpayment or for an account in service".
  - The bodies still write identical rows (prefix aside), which is correct: tools must not judge state. But each payment state edge is now reached by exactly one write whose contract covers that account state. **G8 closed** at the business-reading level.

### prerequisite_graph and prerequisite_sentences (revision 2)

- All five edges carry the same `policy_source`, `condition`, `form: state`, `kind`, `gate` and `resolved_by` as in round 1. All are verbatim in their own rules. The graph is acyclic, with no cross-tree edge.
- The four-point test passes for all five, as in round 1.
- Single-write test:
  - The late-charge and meter-credit edges pass, as in round 1.
  - The two payment edges now pass too: the other user payment tool's contract excludes the account state of that edge.
- G9 is unchanged: the restore edge's gate label `service_payments.amount` is a column, and the reconnect edge's gate is the base past_due_covered gate. It has no consequence for what an agent does, so it remains an observation, answered by the reworker with no change.

### override_declarations (revision 2)

- **late charge** declares four overwrites. Base "No late charge is assessed on a bill whose past-due amount is fully covered by an energy assistance pledge recorded on or before the due date, nor on the portion of a balance moved into an active payment arrangement" is now named. Its replacement is the pledge-deduction ladder, plus the arrangement-line ladder carried in the program-charge entry. **G7 closed.** The program-charge `replaced_by` now carries both the area-light and the arrangement-line text. **G13 closed.**
- **meter refund** declares base "A late charge is never partly waived" superseded by the overbilled-share late-charge refund. **G10 closed.** The test-fee refund now reaches only fees "dated less than meter_error_rebill_max_months whole months before the current date". **G11 closed.** The fast-meter refund sentence remains declared.
- **reconnect fee**: the crew-charge override is still declared. The multiplier is gone, and so is the "never waived at the service desk" overwrite. Base "The reconnect fee is never waived at the service desk" is now followed (no tier reduces the fee). Consistent.
- **seasonal minimum**: the December annual-minimum override is still declared. The PCA overwrite was dropped, and the credited lines never include PCA (facility, energy and demand only). So base "Power cost adjustment, sales tax and fees never count toward either minimum" is followed. Consistent.
- **restore payment** (`overwrite: []`): the new facility-prepayment addition is a payment amount, not a facility_charge line, so it does not touch service_evt_usage_billing. Base service_evt_payments "A payment over the balance leaves a credit balance that is applied to future bills" accommodates it.
- **restore fee**: "A restore is billed seasonal_restore_fee" superseded, still declared. Its `replaced_by` now names restore credits.
- **reconnection payment** (`overwrite: []`): unchanged reading. G12 (pledge credit vs "moves no money") stays an observation, answered with no change.

### factor_ladders (revision 2)

Label standard applied this round: a `method` tier must change the algorithm. Substituting a constant into one formula is a `parameter`; this covers a rate, a multiplier, and also a look-back length given as a constant number of months. A window whose *anchor event* changes (since an accurate test / since connect / since idle) changes which history is read, and is accepted as `method`. This sharpens round 1's "doubtful" note on rebill_window_length: under this standard that factor is honest.

**late charge** (6)
- Factors: rate tier P; pledge deduction P; assisted multiplier **now P** (relabelled, ×0.75/×0.50/×1); payments applied M; light exclusion P; arrangement exclusion P (cross arrange).
- Parameter 5, honest method 1.

**meter refund** (6)
- rebill_window_length: M (anchor), honest.
- **over_registered_energy_pricing: M, new, replaces refund_base_lines.**
  - Tier 1: over-registered kWh × block-2 rate. Tier 2: × block-1 rate. Tier 3: share of the energy dollars.
  - Tier 3 is a different algorithm, so the label is honest. Tiers 1 and 2 differ only in the rate (observation).
  - The condition "energy_rate_block2_per_kwh below energy_rate_block1_per_kwh" holds on R, FH, GS-1, GS-3 and LP but not on RS or IR (flat 0.1261 / 0.08915), so it divides customers. **G3 closed.**
  - Business reality: refunding over-registered kWh at the marginal block rate they were billed at is a real rebilling practice.
- overbilled share: M, honest.
- late-charge refund: P.
- overbilling interest **now P** (×1.0184 / ×1.0092 / ×1).
- test-fee refund: P.
- Parameter 3, honest method 3.

**reconnection payment** (5)
- Factors: amount owed M; payments counted M; pledge selection M; pledge credit P; deposit installment P (cross deposit).
- The deposit ladder (accelerated remainder / next installment / 0) is now the deposit charter's own schedule: `first_installment_pct`, "the rest split evenly over the remaining installments", and `installment_default_accelerates` "makes the whole unpaid remainder due at once", read through CPARAM. **G4 closed.**
- Parameter 2, method 3.

**reconnect fee** (6)
- Factors: crew charge P; **reconnection_lookback_window labelled M**; repeat surcharge P; deposit basis surcharge P (new; cross deposit); site inspection P; area light P (cross light). The multiplier was removed.
- The new method factor's three tiers are, verbatim, "earlier reconnections are counted over the default_lookback_months / return_lookback_months / standard_lookback_months whole months before today". In compute: `COUNT(... within_months=lookback_months ...)` with `lookback_months` ∈ {K 24, K 18, K 12}.
  - One formula, three constants, same anchor (today). By the standard above this is a `parameter` factor mislabelled `method`.
- **Honest method count stays 0 (floor 1): G1 is not closed for this policy** (finding R2-G1 below).
- The ladder itself is real: three disjoint tiers with distinct outcomes, cross-difficulty on arrange, multi-source tier 2. Only its label and the policy's method floor fail.

**seasonal minimum** (4)
- Minimum rate P (cross line). Tier 1 is now "connected 120 whole months or more ... with no late payment charge dated in the twelve whole months": a real, dividing condition. The capital conjunct is gone. **G14 closed.**
- Capacity M.
- Credited lines P, now by demand-period count: 1–3 periods → F+E; 4–6 → F+E+½D; else → F+E+D.
  - The fall-through covers both 0 periods (D = 0) and 7 or more periods, so its formula F+E+D takes values other than tier 1's.
  - No two tiers select one outcome as stated. **G2 closed.**
- Proration **now P**.
- Parameter 3, honest method 1.

**restore payment** (5)
- Factors: minimum hold-back P; **facility charge prepaid P (new; replaces the deposit factor)**; uncleared payments M; idle late charges P; light lines P (cross light).
- Prepaying one facility charge on the first restore of a new service, or two after a returned payment, is a plausible advance-payment practice.
- Parameter 4, method 1.

**restore fee** (6)
- Factors: restore charge P; idle inspection P; area light P (cross light); **collection_review_period M (new)**; collection review P; **line extension warranty credit P (new; cross line)**. The multiplier and the deposit addition were removed.
- The period ladder changes the anchor of the history read: since connect counting the month in progress / a fixed 12 months back / since the idle date. Accepted as method.
- **G1 closed for this policy.** Parameter 5, method 1.

All ladders have three disjoint tiers with distinct outcomes, every tier stated in the rule, and every fall-through equal to the baseline. No tier rests on an outcome stamp.

### findings (revision 2, charter-global)

| Round-1 item | Revision-2 status | Evidence |
| --- | --- | --- |
| G1 mislabelled methods | **partly closed** | Late-charge multiplier, interest, proration relabelled P. Restore fee now has an anchor-changing method. **Reconnect fee: still no honest method** (R2-G1). |
| G2 credited lines two-tier | closed | demand-period ladder |
| G3 PCA universal | closed | factor replaced; declining-block condition divides schedules |
| G4 deposit installment | closed | ladder is the deposit charter's schedule plus acceleration |
| G5 pledge selection compute | closed | conjunct removed |
| G6 review window | closed | rule restated in whole months |
| G7 fully covered pledge | closed | sentence named in overwrite |
| G8 two payment writes | closed | docstrings partition account states |
| G9 gate labels | unchanged, observation | answered no change |
| G10 late charge partly waived | closed | declared overwrite |
| G11 test fee beyond 6 months | closed | window limited to rebill max |
| G12 pledge "moves no money" | unchanged, observation | answered no change |
| G13 program-charge replaced_by | closed | arrangement text added |
| G14 capital conjunct | closed | replaced by the late-charge condition; capital read gone |
| G15 deposit paid then surcharged | closed | surcharge reads assessment_basis; restore no longer collects a deposit |
| G16–G19 | unchanged, observations | answered no change |

- **R2-G1 — SOURCE-FACTOR RED (mislabelled effect; CONFIRMED). This is not a new defect; it is the round-1 G1 left open in another form.**
  - Symptom: service_ext_reconnect_fee's only `method` factor, `reconnection_lookback_window`, substitutes one of three constants (24 / 18 / 12 whole months) into the same count of reconnect fees dated before today. Its three method strings differ only in the parameter named.
  - Root cause: the round-1 multiplier was replaced by another constant-selecting factor that is labelled `method`.
  - Consequence: the policy has 0 honest `method` factors (floor 1).
  - Bears on task 0 (demonstrated in `0.md` revision_2).
- **R2-O1 — observation.** In over_registered_energy_pricing, tiers 1 and 2 differ only in the rate applied. The factor stays honest through tier 3.

### closing_checklist (revision 2)

Written after the revision-2 reveals (2026-10-06T19:36:26Z). **The difficulty does not close: task 0 is RED (SOURCE-FACTOR, R2-1 / R2-G1). Task 1 is PASS.**

- **Files.** `0.md` and `1.md` each carry an untouched round-1 text and an appended `## revision_2`, with frozen derivation, comparison and findings. `_difficulty.md` carries round 1 plus this revision.
- **Coverage and scope.** The revealed r2 `charter_scope` equals the auditor's derivation: task 0 has the 4 tree-A policies, task 1 the 3 tree-B policies. The two are disjoint and cover all 7. GT writes call each policy's `target_tool`. The uuid8s are unchanged and independent.
- **Trees.** Task 0 has 3 prerequisite problems with 2 value_input edges; task 1 has 2 with 1 value_input edge. Each has one owner=user write. Both are acyclic, with no cross-task edge. All edges bear weight on the r2 worlds. **Holds.**
- **Factors.**
  - Every computation has a self-sufficient baseline giving a non-gold number: 8.67, 45.25, 221.65, 75.00; 1644.56, 1585.06, 45.00.
  - Every factor bears weight, has a ladder of 3 distinct tiers stated in its rule, and has seeded cross-difficulty evidence consistent with its charter.
  - Every task has multi-source and cross-difficulty factors.
  - **Fails only on service_ext_reconnect_fee: 0 honest `method` factors (R2-G1).**
- **Policy self-consistency.** G5, G6, G7, G8, G10, G11 and G13 are closed. No new conflict. **Holds.**
- **Gates.** The orchestrator's r2 snapshot is all green on the reworked artifacts, and the hashes match. The auditor did not re-run the gates.

## revision_3

### charter_global_frozen (revision 3)

- Freeze time: 2026-10-06T20:29Z, before either round-3 task file was revealed. Auditor: the same independent auditor.
- Shared inputs:
  - `service.extended.yaml` = `fc3560a6313c4505d97883e868117cbd0b361789e30163c4c0c9ac90d7ddeba7` (changed from round 2's `8412b1ea…`).
  - `task_tools.py` = `8f242f32…`, unchanged from round 2, so § action_binding_and_uuids (revision 2) is **carried forward by reference** on that hash.
  - The r3 views are byte-identical to the r2 views (`0f0733de…`, `d85b4948…`).
  - The blueprint is unchanged (mtimes before round 1). The base section is still verbatim.
- Gate snapshot `/tmp/orch43/snap_electric_service_billing_and_trouble_r3.txt`: all OK.
- Masked: the round-3 `tasks/*.json` beyond the views, and `worklog.md` (never read).
- Disclosure: round-1 and round-2 GT of both tasks were seen in earlier rounds.
- Change localisation: no round-2 charter copy was kept. Evidence that only service_ext_reconnect_fee changed:
  - the policy offsets are identical up to that policy (1432 / 1715 / 1938 / 2205) and shifted by +3 after it (2441 / 2610 / 2813);
  - re-evaluating all seven computes on the unchanged views reproduces every round-2 result and every per-factor baseline figure for the six other policies;
  - the label of every factor in those six is unchanged.
  - Because the charter hash changed, the sweeps below were re-run over the whole charter anyway.

### re-derived sections (revision 3)

- **rule_compute_equivalence.** The programmatic sweep (every binding has a basis; every basis, baseline sentence, prerequisite sentence and replaced_by is in its rule) passes for all seven policies. In the redesigned `lookback_months`, the rule and compute agree in both directions:
  - "every reconnect fee since the account's connect date ..., the month in progress counted" = `MONTHS(F('connect_date'), NOW) + 1`;
  - "the reconnect fees since the latest returned payment ..., the whole months elapsed since that return's posting date, the month in progress counted" = `MONTHS(latest_return_date, NOW) + 1`;
  - "otherwise ... standard_lookback_months whole months" = `K('standard_lookback_months')`.

  The unused round-2 params (default/return look-back months) were removed, and `inputs` was updated.
- **policy_conflict_scan / override_declarations / prerequisite_graph / prerequisite_sentences.** Re-run; the conclusions are unchanged from revision 2:
  - the reconnect fee still declares only the crew-charge override, and "never waived" is followed;
  - the prerequisite edge is unchanged (same sentence, condition and gate);
  - cross-category reads are unchanged (arrange, deposit, light).
- **factor_ladders, reconnect fee.** `reconnection_lookback_window` is still labelled `method`. Its tiers now change the **starting event** of the history read:
  - connect date (whole life);
  - latest returned payment;
  - a rolling 12-month window.

  That is the same anchor-changing pattern accepted in revision 2 for rebill_window_length and collection_review_period, so it is an honest `method`. The policy now has parameter 5 and honest method 1. The three tiers are disjoint with distinct outcomes, the fall-through equals the baseline, and the factor is cross-difficulty (arrange) and multi-source (tier 2 conjunction). **R2-G1 closed.**
- **New observation R3-O1 (PLAUSIBLE business-reality note, not RED).** Tier 2 counts reconnections only since a returned payment that is by definition less than 12 months old. So its look-back is never longer than the clean-account standard of 12 months. An account with a returned payment can therefore be surcharged less than a clean account with the same history: for example, with reconnect fees 10 and 3 months ago and a return 5 months ago, tier 2 counts 1 fee (+25.00) where the standard would count 2 (+50.00). The direction is odd but publishable (a fresh count from the return). It does not bite in task 0 (tier 1). Also, the "since the latest returned payment" phrasing and its stated whole-month window can admit a fee dated earlier in the return's own month. The rule states the window explicitly, so there is one reading.
- Other observations carried: R2-O1, G9, G12, G16–G19 (answered with no change).

### closing_checklist (revision 3)

Written after the revision-3 reveal (2026-10-06T20:29:31Z). **The difficulty closes: both tasks PASS all four relationships.**

- **Files.** `0.md` and `1.md` (one-to-one with tasks 0 and 1) plus `_difficulty.md`. Rounds 1 and 2 are preserved untouched, and revisions 2 and 3 are appended. Each latest comparison section carries PASS.
- **Coverage and scope.** The revealed `charter_scope` partitions all 7 extended policies: 4 in task 0, 3 in task 1, pairwise disjoint. Each tree lies inside its own scope. GT writes use each policy's `target_tool`. uuid8s are independent and frozen.
- **Trees.** Task 0 has 3 prerequisite problems with 2 value_input edges; task 1 has 2 with 1. Each has one owner=user write. The difficulty graph is acyclic, with no cross-task edge.
- **Factors.**
  - Every computation has a self-sufficient baseline with a definite non-gold number (8.67 / 45.25 / 221.65 / 75.00; 1644.56 / 1585.06 / 45.00).
  - Each has 4–6 factors with at least 2 `parameter` and at least 1 honest `method`.
  - Every ladder has ≥ 3 distinct tiers stated in its rule, and every factor bears weight on its world.
  - Each task has a multi-source factor and a cross-difficulty factor with seeded, charter-consistent evidence (task 0: arrange, deposit, light; task 1: line, light).
- **Policy self-consistency.** No open conflict. The remaining items are observations only:
  - R2-O1, R2-O2, R2-O3, R3-O1;
  - G9, G12, G16–G19.
- **Gates.** The orchestrator's r3 snapshot is all green on the final form (charter `fc3560a6…`, tools `8f242f32…`). The auditor did not re-run the gates.
