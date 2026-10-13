# Policy-task audit — security_deposit_lifecycle / charter-global

## charter_global_frozen

- Scenario: `env/env_0043_rural_electric_cooperative`; difficulty `security_deposit_lifecycle`; category `deposit`; M = 2 (tasks 0, 1).
- Freeze hashes (sha256, re-computed by the auditor and equal to `/tmp/orch43/views/security_deposit_lifecycle/HASHES.txt`):
  - `tasks/security_deposit_lifecycle/deposit.extended.yaml` = `86967ee60b6aebe5f7af34d5ca16cb5d90ee06346f9384bd965f4fafddc1f7a7`
  - `tasks/security_deposit_lifecycle/task_tools.py` = `74d36bffbda04674b66cc921b3f88652a55ad27a65fe8753a5ecdf3573e8411b`
- Freeze time: 2026-10-06T18:30Z (pre-reveal; no task JSON, worklog or GT field read before this section was written).
- Auditor: erl-task-policy-audit agent (independent of the instantiating agent; no answers supplied by the brief).
- Fields read: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/deposit.yaml` (plus `arrange.yaml` default/harvest parameters, for the cross-difficulty seed sanity check), `deposit.extended.yaml`, `task_tools.py`, the masked views `0.view.json` / `1.view.json` (frozen_time, user_scenario, initial_state only), and the DSL evaluator semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (read-only: `MONTHS`, `DAYS`, `_within`, `XSUM`/`XCOUNT`/`CFIELD`/`RND`).
- Fields masked and not read: all of `tasks/security_deposit_lifecycle/tasks/*.json` beyond the views (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), `tasks/security_deposit_lifecycle/worklog.md`, the scenario-level `env/env_0043_rural_electric_cooperative/worklog.md`, any earlier audit.
- Step 0 entry conditions: the gate snapshot `/tmp/orch43/snap_security_deposit_lifecycle.txt` was supplied with the commands and output lines (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; check_traceability deferred until the KB is published). The masked views and their hashes were supplied; the view hashes match (`202b6f17…` for 0, `8314c320…` for 1). Entry conditions are complete.
- Base copy: `deposit.extended.yaml` keys `category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies` are each equal (parsed YAML equality) to `blueprint/products/deposit.yaml`. The base section is a verbatim copy.

### policy_conflict_scan

Six extended policies, six distinct target tools:

| policy | subject | computes | target_tool | owner | trigger |
| --- | --- | --- | --- | --- | --- |
| deposit_ext_reinstated_first_installment | deposit_payment, deposit_partial | amount | pay_reinstated_deposit_installment_114bda0d | user | on_request |
| deposit_ext_waiver_reinstatement | deposit_assess | required_amount | assess_reinstated_deposit_c3ac4854 | agent | state_due |
| deposit_ext_reconnection_deposit | deposit_assess | required_amount | assess_reconnection_deposit_9009d8a2 | agent | on_request |
| deposit_ext_year_end_interest | deposit_interest_accrual | amount | post_year_end_deposit_interest_3b717487 | agent | state_due |
| deposit_ext_refund_date_interest | deposit_interest_accrual | amount | post_refund_date_deposit_interest_50449ec1 | agent | on_request |
| deposit_ext_recalculation_refund | deposit_refund | refund_amount | refund_deposit_by_check_ead765c2 | user | on_request |

Overlapping subjects and how they are separated:
- `deposit_assess` (waiver_reinstatement vs reconnection): separated by assessment basis (waiver_reinstatement vs reconnect_after_nonpay), by tier (the waived record's tier vs always Residential Credit Reestablishment Deposit) and by tool. The base dedup `deposit_agg_multi_holding` (one open assessment per basis) does not collide because the bases differ. The base ceiling `deposit_agg_service_total` is followed by the reconnection in substance (nets the reinstated deposit, room under 900 = the Credit Reestablishment maximum) and asserted away by the reinstatement ("A reinstated deposit is the only deposit its account carries"). See observation O1.
- `deposit_interest_accrual` (year-end vs refund-date): separated by period (a full calendar year ending December 31 held in full vs the part of the current year ending on the refund date) and by tool. Tranche years ("a year in which installments posted") are left to the base interest rules by the year-end rule's first sentence; no extended policy claims them.
- `deposit_refund`: only the recalculation policy claims it; the base good-payment refund (`deposit_evt_refund`) and the cancellation refund (`deposit_evt_cancellation`) are inherited without a task tool.
- Time anchors: reconnection, reinstatement and first installment all read "today" (frozen_time); year-end reads "the twelve whole months before the accrual is posted" (posting date = today), refund-date reads "since the last accrual period ended" through today; recalc reads today. No two policies anchor the same quantity differently.
- Terminal states: first installment moves the reinstated record to partially_paid (or held); the two assessments create assessed records; the accrual tools add accrued_interest; the refund tool leaves the record held (or refunded when no cash is left). No two policies drive one record to incompatible states.
- Cross-category read boundaries: every `cross_category.reads` entry names a field of `service`, `arrange` or `capital` tables present in `db_schema.json`; the gate snapshot reports "cross-category reads declared exactly".
- Scope exclusivity (from the charter alone, before reveal): the three assessment/payment policies form one connected component of the `prerequisite` graph (reconnection -> first installment, reconnection -> waiver reinstatement) and the three interest/refund policies form the other (recalc -> refund-date -> year-end). Two components, two tasks, six policies: the scopes can be pairwise disjoint and jointly complete only if each task claims exactly one component. Confirmed against `charter_scope` only at reveal, in the task files.

### rule_compute_equivalence

Check 2, per policy. "OK" means a verbatim `compute_basis` quotation exists and the expression implements it; deviations are listed.

**deposit_ext_reinstated_first_installment**
- `required`, `result`: "multiplied by the first-installment share in percent and divided by one hundred, then multiplied by the meter allowance on the first installment, and rounded half up to the cent once" -> `RND(required * share / 100 * meter_allowance, 2)`. OK.
- `paid_since_notice` / `notice_amount` / `start_share`: "service payments posted on the account less than one whole month before today reach the past-due amount the outstanding notice demands" -> `XSUM(... within_months=1, event_type='service_payment')` vs `CFIELD('service','disconnect_past_due_amount')`, `notice_amount > 0` as "outstanding". OK.
- `months_connected`, `tenure_points`: whole months connect_date -> today, >=36 / >=12 / else. OK.
- `pledges_recent`, `pledges_older`, `pledge_points`: `service_assistance_pledge` rows within 1 / within 3 months. OK.
- `meter_type`, `returns_12m`, `meter_allowance`: `ami_remote_disconnect` and returned payments within 12. OK.
- `share`: start_share - tenure_points - pledge_points. OK.
- Rounding: `RND` is Python `round` on a binary float, not half-up (observation O6; no audited value lands on a half cent).

**deposit_ext_waiver_reinstatement**
- Window ladder (`months_connected`, `sum_since`/`periods_since` with `within_months=months_connected + 1`, `sum_24`/`periods_24`, `sum_12`/`periods_12`, `window_average`): the three tiers quoted verbatim in `compute_basis.window_average`. OK.
- "the number of billing periods is the number of facility charge lines" -> `charge_component='facility_charge'` counts. OK.
- Growth (`sum_3`, `periods_3`, `recent_average`, `basis_bill`): ">1.35x -> recent; >1.15x -> midpoint; else window". OK.
- Record (`late_12`, `returns_12`, `record_multiple`): 0/0 -> 1.75; exactly 1 late and 0 returns -> 1.9; else deposit_multiple. OK.
- Waiver-loss (`own_status`, `qualifying_status` via `account_number=F('waiver_reference')`, `waiver_loss_adjustment`). OK.
- Autopay (`payments_12`, `drafts_12`, `autopay_relief`). OK.
- Remote meter (`shop_meter`, `remote_meter_relief` with `months_connected >= 12`). OK.
- `reinstatement_multiple` = MX(floor, record + adj - autopay - remote). OK.
- `estimate`, `raw_amount` (periods_12 >= min_history_months), `rounded_amount` (ceiling to rounding_increment), `result` (min, then max). OK.

**deposit_ext_reconnection_deposit**
- Bills `bill_1..bill_12` as differences of cumulative `XSUM(... within_months=k)`: "each month's bill read by itself". OK.
- `highest_bill`, `average_bill` (sum_12m / facility-line count), `basis_bill` tempering (>2.0x midpoint; >1.5x two-thirds/one-third; else highest). OK.
- Lateness (>=5 -> 2.5; >=3 -> 2.25; else tier multiple), returns surcharge (>=2 / 1 / 0), arrangement (member-wide `arrange_balance_rebill` with `rebill_reason='default'` within 24; else completed arrangement on the account), hardship (LIHEAP `service_payment` within 12 and certificate within 12). OK, with observation O5 (`certificates_12` counts every `service_certificates` row, the rule says "a medical certificate").
- `paid_on_reinstated` = `SUM('deposit_ledger','amount',event_type='deposit_payment')` on the holding (the reinstated record); `installment_relief` >= half / > 0 / none. OK.
- `reconnection_multiple` = MX(tier multiple 2.0, ...). OK. `rounded_amount` = MX(minimum, ceiling to 5). OK. `result` = MX(0, MN(rounded - reinstated_required, 900 - reinstated_required)). OK.

**deposit_ext_year_end_interest**
- `cash_held` = payments - refunds - applications on the ledger. OK.
- `last_end`, `accrual_year` = year of last_end + 1. OK.
- `commission_rate` from `commission_rate_20xx` keys equal to the tier's `interest_rate_by_year` values (0.48 / 1.65 / 2.28 / 2.07 / 1.84). OK.
- `year_days`, `days_counted` (returned -> minus 30 per return; else >=3 lates -> minus 15 per late beyond the second; else all days). OK.
- `seasoning_months` = MONTHS(paid_in_full_date, last_end) ("to the last day of the year before the accrued year"); `patron_months` = MONTHS(active capital opened_date, last_end); `other_connects_12m/24m` member-wide minus own account. OK.
- `member_rate`, `result`. OK.

**deposit_ext_refund_date_interest**
- `base_days` = DAYS(last_end, NOW) = "from the day after the last accrual period ended through the refund date, both ends included". OK.
- `now_year`, `current_rate`, `previous_rate`, `held_months`, `selected_rate` (>=36 -> max; >=18 -> average; else current). OK.
- `part_months` = MONTHS(last_end, NOW) used as `within_months`: matches the rule's own convention "counting charges and payments posted fewer whole months before today than the whole months from that period's end to today". OK.
- `days_counted` (returns -> minus 30 each; else lates -> minus 10 each; else base days). OK.
- `draft_supplement`, `prompt_supplement` (<= prompt_late_limit 3), `accrual_rate`, `result`. OK.

**deposit_ext_recalculation_refund**
- Bills `bill_1..bill_12`: "read month by month back from today". OK.
- `window_months`: "MONTHS(latest_connect_fee, NOW) if another account's connect fee within 12 months; own_connect_months + 1 if own connected < 12 months; else 12". The rule says "fewer whole months before today than have passed since that connect fee" (the other account's); `latest_connect_fee` is an `XLATEST` over all the member's connect fees, own account included (observation O4; not reached in task 1, where the own account has no connect fee row).
- `window_sum`, `window_periods`, `window_average`, `window_highest` (bills restricted to the window), `trimmed_average`, `basis_bill` (>1.6x trimmed; >1.3x midpoint; else window average). OK.
- Record (24 months: no return and no reconnect fee -> 1.75; no return but a reconnect fee -> 1.9; else deposit_multiple), harvest (`ended_date` of a completed Agricultural Harvest agreement < 24 months; else any completed arrangement < 24 months), moved-load (other accounts' payments, lates and drafts within 12), remote relief. OK.
- `recalculation_multiple`, `recalculated_requirement` (ceiling to rounding_increment, min, max), `excess_cash` = F('held_amount') - requirement, `unpaid_interest` = ledger accruals - payouts, `result` (threshold 10). OK.

Sweep back (rule -> compute): rule sentences without a compute counterpart are non-scored statements only (the remaining installments "fall due with the next monthly bills", disbursement method, "the deposit stays held for the recalculated requirement", "the waived record itself is not reopened"); each is carried by a tool argument or tool effect rather than by an invented basis. Every factor ladder tier named in `factors[].ladder` is a sentence of the rule and a branch of its `decides` binding, and vice versa. No equivalence RED.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: six, each claimed by exactly one policy (table above). No two policies share a target tool.
- uuid8 tails: `114bda0d`, `9009d8a2`, `c3ac4854`, `3b717487`, `50449ec1`, `ead765c2` — six distinct tails, no shared prefix or suffix, no sequence or adjacency pattern, none reused. Nothing indicates batch derivation (independent generation itself cannot be proven from the artifact; no counter-evidence).
- Docstrings: none names another tool, none states a position in a sequence. Ordering-looking words appear only as business descriptions: "the first installment" (ordinal of the installment, `pay_reinstated_deposit_installment_114bda0d` Args), "reconnected after a nonpayment disconnection" (the meaning of the enum value `reconnect_after_nonpay`, in both assessment tools), "the part of a year that ends on the day a cash security deposit is refunded" (`post_refund_date_deposit_interest_50449ec1`). Observation O11; no RED.
- Function bodies: every tool performs its write unconditionally (`ctx.create` / `ctx.update`), with no status check, no prerequisite check, no amount check and no hint. The tool layer judges no prerequisite.
- Business reading of each tool is unique: `assess_reconnection_deposit_9009d8a2` always records the Residential Credit Reestablishment tier ("a Schedule R or Schedule FH electric service account"); `assess_reinstated_deposit_c3ac4854` takes the tier as an argument ("replaces a deposit waiver which no longer stands"); the two accrual tools are separated by "the December 31 interest accrual of one calendar year" vs "the part of a year that ends on the day a cash security deposit is refunded"; `refund_deposit_by_check_ead765c2` is the member's check request. No added confirmation, review or wait.

### prerequisite_graph

Check 7.

| blocked policy | problem | kind | gate | form | policy_source locatable in own rule |
| --- | --- | --- | --- | --- | --- |
| deposit_ext_reinstated_first_installment | — (`[]`) | | | | |
| deposit_ext_waiver_reinstatement | — (`[]`) | | | | |
| deposit_ext_reconnection_deposit | deposit_ext_reinstated_first_installment | value_input | installment_relief (a compute binding: yes) | state | yes, verbatim |
| deposit_ext_reconnection_deposit | deposit_ext_waiver_reinstatement | state_gate | deposit_accounts.assessment_basis | state | yes, verbatim |
| deposit_ext_year_end_interest | — (`[]`) | | | | |
| deposit_ext_refund_date_interest | deposit_ext_year_end_interest | value_input | base_days (a compute binding: yes) | state | yes, verbatim |
| deposit_ext_recalculation_refund | deposit_ext_refund_date_interest | value_input | unpaid_interest (a compute binding: yes) | state | yes, verbatim |

- Every policy fills `prerequisite`; every `problem` is an extended policy id of this file, never a base policy and never itself. The graph is acyclic (two chains: reconnection -> {first installment, reinstatement}; recalc -> refund-date -> year-end).
- `form` is `state` on all four edges and no `fallback_reason` is present; consistent.
- `resolved_by` equals the depended-on policy's `target_tool` on all four edges, and each tool's effect makes the stated condition hold (deposit_payment ledger row; waiver_reinstatement record; deposit_interest_accrual rows with the stated period ends).
- `condition` vs sentence: three edges match in strength. The refund-date -> year-end edge's `condition` ("The latest deposit_interest_accrual entry on the deposit ledger has an accrual_period_end of December 31 of the year before the refund year") is stricter than its sentence ("a December 31 accrual for every earlier calendar year in which cash was held") for a deposit first paid in the refund year, where the sentence holds vacuously and the condition never can. Observation O2: the case occurs in neither task world and the `condition` field is not rendered for the agent.
- The `state_gate` edge's `gate` names a DB field (`deposit_accounts.assessment_basis`), not an eligibility gate id. The extended policies declare no `eligibility` blocks, and the gate is carried by the rule sentence. Observation O3.
- No authoring-viewpoint phrasing ("in this task", "at the opening") in any `prerequisite` text.

### prerequisite_sentences

Check 6, per edge.

1. reconnection <- first installment. Sentence: "The reconnection deposit is fixed only after the first installment of the reinstated deposit on the account stands posted as a deposit payment on the deposit ledger."
   - Connective "only after" joins the policy's own result ("the reconnection deposit is fixed") to a waited-on state. State form: "stands posted as a deposit payment on the deposit ledger" names a record-visible state in ledger words (event type deposit payment) with no performer or tool. No tool name, policy id, snake_case token or row id. Strength: "the first installment ... stands posted" = at least one deposit payment on the reinstated record, the same as `condition`.
   - One write brings it about: only `pay_reinstated_deposit_installment_114bda0d` creates a `deposit_payment` ledger row (no share tool writes the deposit ledger).
   - Derivation: the reader of the reconnection rule finds the reinstated record (assessment_basis waiver_reinstatement) on the account with no deposit payment. The only policy whose own rule sets "the first installment a member pays on a deposit reinstated ... while the service account it secures stands disconnected for nonpayment and waits to be reconnected" is `deposit_ext_reinstated_first_installment`, so that policy's tool is the resolving action (owner user). Single reading.
   - The depended-on rule does not restate the sentence. The reconnection rule carries no second wording of this dependency (the installment-relief sentence is the value the edge feeds, not a second ordering).
2. reconnection <- waiver reinstatement. Sentence: "The reconnection deposit is not fixed until every deposit waiver resting on this account's payment history stands replaced by a reinstated deposit on the account that waiver covered."
   - Connective "not ... until". State form: "stands replaced by a reinstated deposit on the account that waiver covered", where "resting on this account's payment history" uses the reinstatement rule's own definition ("A waiver rests on another account when its waiver basis is coop_payment_history and its waiver reference is that account's account number"). No tool, id or snake_case. Strength "every" = `condition` "For every deposit record waived on coop_payment_history whose waiver reference is this account's account number ...". Match.
   - One write: `assess_reinstated_deposit_c3ac4854`. `assess_reconnection_deposit_9009d8a2` accepts `waiver_reinstatement` in its basis enum, but its docstring restricts it to "a Schedule R or Schedule FH electric service account" and it always records the Credit Reestablishment tier, while the reinstatement rule requires "the tier of the waived record". It cannot produce the waited-on state on a covered account of another tier, and for an R/FH covered account it would produce a record on the wrong tier. Single write.
   - Derivation: reconnection rule -> find waived records with waiver basis coop_payment_history and waiver reference = this account's number -> the policy whose rule reinstates such a waiver "when the waiver rested on the payment history of another Cedar Fork service account and that other account is disconnected for nonpayment" is `deposit_ext_waiver_reinstatement`. Single reading.
3. refund-date <- year-end. Sentence: "The refund-date accrual is worked out only after the deposit ledger carries a December 31 accrual for every earlier calendar year in which cash was held."
   - "only after"; state form (ledger carries a December 31 accrual); no tool or id. Strength: see O2 (condition stricter in a corner case only).
   - One write for a year held in full: `post_year_end_deposit_interest_3b717487` ("Post the December 31 interest accrual of one calendar year"). The refund-date tool's docstring restricts it to "the part of a year that ends on the day a cash security deposit is refunded", so it is not a second candidate.
   - Derivation: refund-date rule -> last accrual period end on the ledger vs the earlier years cash was held -> the policy that "posts the December 31 accrual of a calendar year on a cash deposit that was held in full for the whole of that year" is `deposit_ext_year_end_interest`. Single reading for a year held in full. For a tranche year the year-end rule sends the reader to the base interest rules, which have no task tool (relevant to neither task).
4. recalc <- refund-date. Sentence: "The recalculation refund is not made until the deposit ledger carries an interest accrual whose period ends on the refund date."
   - "not ... until"; state form; no tool or id; strength = `condition`.
   - One write: `post_refund_date_deposit_interest_50449ec1`. The year-end tool posts only a December 31 accrual, so it is a candidate only on a December 31 refund date (relevant to neither task).
   - Derivation: recalc rule -> no accrual ending today on the ledger -> the policy that "posts the accrual for the part of the current calendar year that ends on the day a cash deposit is refunded" is `deposit_ext_refund_date_interest`. Single reading.

Undeclared cross-problem orders: no extended rule states an order between two problems that grounds no declared edge. The year-end rule's "a year in which installments posted is accrued tranche by tranche under the interest rules" is a scope sentence, not an order. One base sentence states a cross-problem order, `deposit_evt_payments`: "Where deposit_due_before_connect is true the full deposit or first installment must be paid before the meter is energized". It grounds no edge of this difficulty, and the tiers on the audited trees (Residential Standard, Credit Reestablishment, Farm, General Service) all have `deposit_due_before_connect: false`, except General Service, whose shop account in task 0 is already energized (active). Observation O12.

### override_declarations

Check 1 (finding half), sentence by sentence against `base_policy_refs`.

**deposit_ext_reinstated_first_installment** (refs: deposit_evt_payments; overwrite: sentence 1)
- S1 "A deposit is due deposit_due_days ... first installment of first_installment_pct percent ... rest split evenly ... last one absorbing any cent difference." Replaced (declared). The replacement covers only the first installment, while the extended rule keeps "the rest of the reinstated deposit falls due with the next monthly bills as the payments rules provide", which points back at the sentence just superseded (observation O10; the remainder is not scored).
- S2 "Deposit payments may be posted only while the deposit record is in assessed or partially_paid status ..." Followed.
- S3 "Where deposit_due_before_connect is true ..." Followed (n/a on the tiers of this policy's trees).
- S4 "Where installment_default_accelerates is true ..." Followed (not engaged).
- S5 "The record moves to partially_paid with the first installment and to held when the payments reach the required amount; an overpayment ..." Followed (the tool effect implements it).
- S6 "Deposit payments are accepted only through deposit_payment_channels." Followed ("by card over the phone"; phone_ivr_card is a listed channel).

**deposit_ext_waiver_reinstatement** (refs: multi_holding, service_total, assessment, waiver, reassessment; overwrite: waiver S "Where waiver_reinstatement_on_nonpay ..." and assessment amount S)
- deposit_agg_multi_holding: followed (no second open waiver_reinstatement record is created).
- deposit_agg_service_total, "A new assessment on a service account that already carries deposits is the computed amount less the required_amount of the deposits already in assessed, partially_paid or held status ... reduced to the room left under the maximum_deposit": the extended rule replaces netting with the assertion "A reinstated deposit is the only deposit its account carries ... and it never exceeds the tier's maximum_deposit". This is not named in `overwrite`. For an account that also carries an open usage_reassessment or reconnection deposit, the base nets and the extended does not. Undeclared narrowing; no scored consequence in either task world (task 0's shop carries no open deposit). Observation O1.
- deposit_evt_assessment: trigger S (followed: waived account disconnected); status S (followed); tier S ("the deposit_tier named by the service account's rate schedule") vs extended "on the tier of the waived record" (identical whenever the rate schedule has not changed since the waiver; no world difference); amount S (replaced, declared); rounding/floor S (followed, ceiling see O1); installments S (followed); PrePay S (followed); eligible schedules S (followed).
- deposit_evt_waiver: reinstatement S replaced (declared, broadened to the qualifying-account cut); the other sentences (grounds, the before-payment rule, reconnection never waived, own statement never waives, bond follow-up and lapse) inherited.
- deposit_evt_reassessment: not engaged.

**deposit_ext_reconnection_deposit** (same refs; overwrite: assessment amount S)
- Amount S replaced (declared), including the dropped history/estimate branch (the superseded clause contains it, so the drop is declared).
- deposit_agg_service_total: the extended nets "the required amount of the reinstated deposit on the account" only, while the base nets every deposit in assessed, partially_paid or held status on the account. They differ only where the account carries another open deposit besides the reinstated one. Not declared; no difference on task 0's world (house open deposits: the reinstated record only; the reconnect_after_nonpay record is cancelled). Observation O1.
- Tier S: followed (the Credit Reestablishment exception for R/FH reconnections). Multi-holding: followed. Waiver "A reconnection after a nonpayment disconnection is never waived": followed.

**deposit_ext_year_end_interest** (refs: deposit_evt_interest; overwrite: rate S only)
- S1 "Where interest_applies is true, cash held earns simple interest at the rate interest_rate_by_year gives for each calendar year." Replaced (declared).
- S2 "Interest accrues on the held_amount for each day it was held, the accrual_days of a period counting the posting date of each deposit payment and the last day of the period, divided by interest_day_count." **Handled differently, not declared.** The extended rule makes the year "lose the returned-payment days for each returned payment" or "the late-charge days for each late payment charge beyond the second", so days on which the cash was held earn no interest. The rule itself names the base reading as the "standard" ("The standard year-end accrual counts every day of the accrued year"), which shows the author knew this was a deviation. The quantity is the scored `amount` (and the `accrual_days` argument). Finding F1.
- S3 "Interest is accrued for each calendar year on December 31 and ... part year ..." Followed.
- S4 "Interest may be accrued only while ... partially_paid or held." Followed.
- S5 "The prior year's interest is paid out by interest_payout_method on the bill of interest_payout_month; part-year interest is paid out with the refund ..." Not engaged by the accrual itself (see O7 for the recalc interaction).
- S6 "Interest is rounded to the cent per accrual period and never compounds." Followed.

**deposit_ext_refund_date_interest** (refs: deposit_evt_interest; overwrite: rate S only)
- S1 replaced (declared; the selected commission rate plus supplements).
- S2 (each day held accrues; accrual_days count). **Handled differently, not declared.** The refund-date accrual "takes away the part-year returned days for each returned payment" or "the part-year late days for each late payment charge". The rule again names the base reading as the "standard" ("counts the calendar days from the day after the last accrual period ended through the refund date, both ends included"). Finding F2.
- S3 "where interest_on_partial_year is true, for the part year up to the date of a refund" followed; S4, S6 followed.

**deposit_ext_recalculation_refund** (refs: refund, cancellation, reassessment; overwrite: refund "review that is not good" S and reassessment "falling bill basis" S)
- deposit_evt_refund: good-refund S, "Refunds are paid only from ... partially_paid or held" (followed), held-long-enough (followed), counting (followed), good-record definition (followed: decides that the base path is closed), "A good review refunds the whole held_amount together with interest accrued to the refund date ... by check when the member asks ... at least refund_check_on_request_min" (the recalculation follows the same disbursement rule), "A review that is not good leaves the deposit held ..." (replaced, declared), "never refunded on disconnected_nonpay or final_billed" (followed).
- deposit_evt_cancellation: not engaged.
- deposit_evt_reassessment: falling-basis S replaced (declared).
- Not in refs: deposit_evt_interest S5 ("The prior year's interest is paid out ... on the bill of interest_payout_month"). Where a prior-year accrual is posted late (after the January bill), the recalc's "together with all interest accrued on the deposit and not yet paid out" pays it by check. The base sentence can no longer be executed (that bill is past), no tool posts an interest payout, and the refund tool's contract ("the interest accrued and not yet paid out on the record is paid with it") forces the extended reading. Observation O7; no second executable answer.

Disguised forms checked: anonymous intermediate factors (the day-count deduction is the one found, F1/F2); 0/1 multipliers (none: no existence condition zeroes an amount); dropped branches (the reconnection drops the base history/estimate branch, which its superseded clause declares).

### factor_ladders

Structure only. Weight is per task.

| policy | factor | label | tiers (incl. fall-through) | distinct outcomes | multi-source | cross_difficulty | in rule | structural finding |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| first_installment | notice_clearance_share | parameter | 3 (30 / 40 / tier pct 50) | yes | yes (notice field AND payments) | service | yes | — |
| first_installment | connection_tenure_points | parameter | 3 (5 / 2 / 0) | yes | no (date only) | service | yes | — |
| first_installment | assistance_pledge_points | parameter | 3 (5 / 3 / 0) | yes | no (pledge rows only) | service | yes | — |
| first_installment | remote_meter_allowance | **method** | 3 (x0.9 / x0.95 / x1) | yes | yes (meter AND returns) | service | yes | **F4: number-selector labelled method** |
| reinstatement | reinstatement_averaging_window | method | 3 | yes | no (date span) | service | yes | — |
| reinstatement | reinstatement_recent_growth | method | 3 | yes | no | service | yes | — |
| reinstatement | reinstated_account_record | parameter | 3 (1.75 / 1.9 / 2.0) | yes | yes (lates AND returns) | service | yes | — |
| reinstatement | waiver_loss_adjustment | parameter | 3 (-0.1 / +0.25 / 0) | yes | yes (own status AND qualifying account status) | service | yes | O9 (fall-through reachable only off the two triggers) |
| reinstatement | reinstatement_autopay_relief | parameter | 3 (0.15 / 0.05 / 0) | yes | no | service | yes | — |
| reinstatement | reinstatement_remote_meter_relief | parameter | 3 (0.05 / 0.02 / 0) | yes | yes (meter AND connect date) | service | yes | — |
| reconnection | seasonal_peak_tempering | method | 3 | yes | no | service | yes | — |
| reconnection | reconnection_lateness_multiple | parameter | 3 (2.5 / 2.25 / 2.0) | yes | no | service | yes | — |
| reconnection | reconnection_returned_payment_surcharge | parameter | 3 (0.5 / 0.25 / 0) | yes | no | service | yes | — |
| reconnection | reconnection_arrangement_adjustment | parameter | 3 (+0.25 / -0.1 / 0) | yes | yes (no default AND completed arrangement) | arrange | yes | — |
| reconnection | reconnection_hardship_relief | parameter | 3 (0.5 / 0.25 / 0) | yes | yes (LIHEAP AND certificate) | service | yes | — |
| reconnection | reinstated_installment_relief | parameter | 3 (0.5 / 0.25 / 0) | yes | no | null (own ledger) | yes | **F3: "above zero" holds of every customer reaching the write; fall-through dead** |
| year_end | year_end_delinquency_days | method | 3 | yes | yes (no return AND >=3 lates) | service | yes | — |
| year_end | year_end_seasoning_supplement | parameter | 3 (0.25 / 0.1 / 0) | yes | no | null | yes | — |
| year_end | year_end_patron_supplement | parameter | 3 (0.15 / 0.05 / 0) | yes | no | capital | yes | — |
| year_end | year_end_new_meter_supplement | parameter | 3 (0.05 / 0.02 / 0) | yes | no | service | yes | O9 (business realism doubtful) |
| refund_date | refund_date_rate_selection | method | 3 (max / average / current) | yes | no | null | yes | — |
| refund_date | refund_date_delinquency_days | method | 3 | yes | yes (no return AND lates) | service | yes | — |
| refund_date | refund_date_draft_supplement | parameter | 3 (0.1 / 0.05 / 0) | yes | yes (drafts AND no return) | service | yes | — |
| refund_date | refund_date_prompt_supplement | parameter | 3 (0.25 / 0.05 / 0) | yes | yes (lates AND no return) | service | yes | — |
| recalc | recalculation_window | method | 3 | yes | yes (no other connect fee AND own connect date) | service | yes | — |
| recalc | recalculation_peak_trim | method | 3 | yes | no | service | yes | — |
| recalc | recalculation_record_multiple | parameter | 3 (1.75 / 1.9 / 2.0) | yes | yes (returns AND reconnect fees) | service | yes | — |
| recalc | recalculation_harvest_relief | parameter | 3 (0.15 / 0.05 / 0) | yes | yes (completed AND variant AND end date) | arrange | yes | — |
| recalc | recalculation_moved_load_relief | parameter | 3 (0.1 / 0.05 / 0) | yes | yes (payments AND no lates AND drafts) | service | yes | — |
| recalc | recalculation_remote_meter_relief | parameter | 3 (0.05 / 0.02 / 0) | yes | yes (meter AND returns) | service | yes | — |

- Counts per policy (declared): first installment 4 (3 parameter, 1 method); reinstatement 6 (4 P, 2 M); reconnection 6 (5 P, 1 M); year-end 4 (3 P, 1 M); refund-date 4 (2 P, 2 M); recalc 6 (4 P, 2 M). All within 4 to 6. Every `decides` is an input binding, never `result`. Binding sets within each policy are pairwise disjoint.
- Every factor's fall-through equals its `baseline` expression, and each `baseline` agrees with the policy's `baseline.rule` (first installment: tier pct, no points, allowance one; reinstatement: 12-period average, deposit_multiple; reconnection: highest bill, tier multiple, no surcharge or relief; year-end: every day, commission rate, no supplement; refund-date: base days, current-year rate; recalc: 12-period average, deposit_multiple).
- Every `baseline.rule` sentence is verbatim in the rule, and each is self-sufficient (a definite number can be computed from it plus the records).
- Every tier, including its condition and its value or method, is stated in the rule prose. No tier lives only in `compute`.
- Method labels: the eight `method` factors other than `remote_meter_allowance` change how a quantity is computed (window convention, basis choice among recent / midpoint / window, tempering formula, day-count deduction formula, max / average / current selection, trim formula). `remote_meter_allowance` selects one of three numbers (0.9, 0.95, 1.0) that enter the fixed expression `RND(required * share / 100 * meter_allowance, 2)`, the same shape as the policy's two `parameter` point factors (F4). The authoring reference (`skills/erl-task-instantiate/references/product_extended.yaml`) gives "multiplied by 0.75" as a method example. In that example the tiers also differ in rounding convention ("halved and rounded down", "multiplied by 0.75 and rounded up"); here every tier shares one rounding. Recorded so the conflict between the two references stays visible.
- F3 detail. `reinstated_installment_relief` tier 2 is "payments above zero but below half", and the fall-through is "no payment takes no relief". The same policy's rule says "The reconnection deposit is fixed only after the first installment of the reinstated deposit on the account stands posted as a deposit payment on the deposit ledger". So every customer who reaches the reconnection write has deposit payments above zero. The "above zero" part of tier 2 restates the scope, and the fall-through (= the factor's baseline, 0) is a tier no correctly handled customer can be on. The ladder has two live tiers.
- Per-task multi-source / cross-difficulty availability: the first chain's computations carry multi-source factors (notice, meter, record, waiver-loss, remote, arrangement, hardship) and cross-difficulty factors (service, arrange). The second chain's carry multi-source factors (delinquency days, draft, prompt, window, record, harvest, moved-load, remote) and cross-difficulty factors (service, capital, arrange).

### findings

- **F1 — SOURCE-POLICY RED (charter-global; bears on the task that claims deposit_ext_year_end_interest).** Symptom: two in-force clauses govern the year-end accrual's day count. Root cause: `deposit_ext_year_end_interest.overwrite` names only the base rate sentence; the base day-count sentence of `deposit_evt_interest` stays in force. Evidence: base `policies[deposit_evt_interest].rule`: "Interest accrues on the held_amount for each day it was held, the accrual_days of a period counting the posting date of each deposit payment and the last day of the period, divided by interest_day_count." Extended rule: "when that record shows a returned payment, the year loses the returned-payment days for each returned payment; when it shows no returned payment but at least three late payment charges, the year loses the late-charge days for each late payment charge beyond the second". Consequence: in any world where the account has a returned payment or three or more late charges in the twelve months before posting, the base sentence gives the year's full days held and the extended gives fewer, so `accrual_days` and `amount` have two readings (demonstrated with figures in the task file). Affected: `deposit.extended.yaml` `extended_policies[deposit_ext_year_end_interest].overwrite` / rule; the scored `amount` and `accrual_days` of `post_year_end_deposit_interest_3b717487`, and downstream every value that reads the ledger's interest.
- **F2 — SOURCE-POLICY RED (charter-global; bears on the task that claims deposit_ext_refund_date_interest).** Same shape as F1. Base sentence as quoted in F1. Extended rule: "a returned payment in that time takes away the part-year returned days for each returned payment; no returned payment but one or more late payment charges takes away the part-year late days for each late payment charge". `overwrite` names only the rate sentence. Affected: `extended_policies[deposit_ext_refund_date_interest].overwrite` / rule; scored `amount` and `accrual_days` of `post_refund_date_deposit_interest_50449ec1`, and the recalc refund that carries it.
- **F3 — SOURCE-FACTOR RED (structural; bears on the task that claims deposit_ext_reconnection_deposit).** Factor `reinstated_installment_relief`: tier 2's condition part "above zero" holds of every customer who reaches the reconnection write, because of the policy's own sentence "The reconnection deposit is fixed only after the first installment of the reinstated deposit on the account stands posted as a deposit payment on the deposit ledger". The fall-through/baseline "no payment takes no relief" is unreachable, so the ladder has two live tiers. Affected: `extended_policies[deposit_ext_reconnection_deposit].factors[reinstated_installment_relief]` and the rule sentence "payments above zero but below half take the part-paid installment relief; no payment takes no relief".
- **F4 — SOURCE-FACTOR RED (structural; bears on the task that claims deposit_ext_reinstated_first_installment).** Factor `remote_meter_allowance` is labelled `method`, but its tiers only substitute 0.9 / 0.95 / 1.0 into the fixed expression `result: "RND(required * share / 100 * meter_allowance, 2)"`, and the binding is `meter_allowance: "K('remote_clean_allowance') if (...) else (K('remote_return_allowance') if (...) else 1.0)"`. With the label struck, the policy has 0 honest `method` factors against the floor of 1. Affected: `extended_policies[deposit_ext_reinstated_first_installment].factors[remote_meter_allowance].effect`.
- Observations (no demonstrated scored consequence):
  - O1: the reinstatement ("A reinstated deposit is the only deposit its account carries") and the reconnection (nets only "the required amount of the reinstated deposit on the account") narrow the base `deposit_agg_service_total` netting without an `overwrite` entry.
  - O2: the refund-date -> year-end `condition` is stricter than its sentence for a deposit first paid in the refund year.
  - O3: the `state_gate` edge's `gate` is a DB field, not an eligibility gate id.
  - O4: the recalc `latest_connect_fee` is not restricted to other accounts.
  - O5: the reconnection `certificates_12` counts every `service_certificates` row.
  - O6: `RND` is Python `round`, not half-up.
  - O7: base S5 "prior year's interest paid out ... on the bill of interest_payout_month" vs the recalc "all interest accrued and not yet paid out"; resolved by the tool contract.
  - O8: the year-end delinquency window is anchored on the posting date, not on the accrued year, so a late-posted accrual of the same year reads a different record.
  - O9: the new-meter supplement (a connect fee on another account raising the deposit interest rate) is of doubtful business realism. The `waiver_loss_adjustment` fall-through is reachable only off the policy's two triggers (a lapsed bond or letter of credit, or a qualifying account reconnected before the reinstatement is assessed).
  - O10: the first-installment rule's "as the payments rules provide" points at the superseded clause.
  - O11: ordinal and enum words in the docstrings are business descriptions.
  - O12: the base `deposit_evt_payments` "must be paid before the meter is energized" grounds no edge.

## closing_checklist

Written after both reveals. The charter-global section above was written before any reveal and was not edited afterwards (pre-reveal sha256 `e71b97c6…`).

- Per-task files: `0.md` and `1.md` correspond one-to-one with `tasks/0.json` and `tasks/1.json`; `_difficulty.md` sits alongside. There is no earlier revision; this is revision 0. Each file carries a frozen derivation and a `source_gt_comparison`. Neither comparison is PASS:
  - task 0: **SOURCE-FACTOR RED** (F3, F4);
  - task 1: **SOURCE-POLICY RED** (F1, F2).
- Coverage and scope:
  - `charter_scope` of task 0 = {deposit_ext_waiver_reinstatement, deposit_ext_reinstated_first_installment, deposit_ext_reconnection_deposit};
  - `charter_scope` of task 1 = {deposit_ext_year_end_interest, deposit_ext_refund_date_interest, deposit_ext_recalculation_refund}.
  - The two scopes are pairwise disjoint and jointly cover all six extended policies, matching the two components of the `prerequisite` graph. Task tools: the same split, each tool used by exactly one task. uuid8 tails are distinct and show no pattern.
- Problem trees:
  - task 0: 2 prerequisite problems, 1 value_input edge, owner=user write (first installment), acyclic;
  - task 1: 2 prerequisite problems, 2 value_input edges, owner=user write (the root refund), acyclic.
  - The difficulty-wide graph is a DAG with no cross-task edge.
- Factors: every declared factor bears weight on its task's world against a baseline that agrees with `baseline.rule`, and each computation's all-baseline figure differs from gold:
  - task 0: 220.00 / 560.00 / 410.00 vs 83.60 / 450.00 / 365.00;
  - task 1: 13.25 / 9.00 / 189.39 vs 14.54 / 9.85 / 399.39.
  - Not closed: F4 (the first-installment computation has no honest `method` factor) and F3 (`reinstated_installment_relief` has two live tiers).
- Policy self-consistency: not closed. F1 and F2 are undeclared day-count overrides of `deposit_evt_interest` in both accrual policies.
- Instantiation-stage gates on the final form: the orchestrator's snapshot `/tmp/orch43/snap_security_deposit_lifecycle.txt` was taken on artifacts whose hashes equal this audit's freeze hashes (`86967ee6…`, `74d36bff…`, views `202b6f17…` / `8314c320…`). The auditor did not re-run the gates (Step 0: they are cited, not run). `check_traceability` is deferred until the KB is published.
- Difficulty source-layer verdict: **NOT PASSED** (task 0 SOURCE-FACTOR RED; task 1 SOURCE-POLICY RED).

## revision_2

### charter_global_frozen (revision_2)

- Re-audit round 2, requested by the orchestrator: verify that every round-1 RED is closed, that there is no new defect and that nothing regressed. Revision 0 above is left untouched.
- Freeze hashes (sha256, recomputed by the auditor; equal to `/tmp/orch43/views/security_deposit_lifecycle_r2/HASHES.txt`):

  | artifact | round 1 | round 2 |
  | --- | --- | --- |
  | `deposit.extended.yaml` | `86967ee6…` | `8d0e4e58d477f583e8ef027c4b54a9c5433ed66805710ab38a38c5c0419534d6` |
  | `task_tools.py` | `74d36bff…` | `f4d8bfd853fe5b91ec1e6ce427e35c887996f8a6832775ccc37c41caff435e16` |
  | view 0 | `202b6f17…` | `847a379fd7040df36cfb387264ffbf6d78723067c7d03b627008f727ceb835ac` |
  | view 1 | `8314c320…` | `8314c320…` (identical) |

  Both shared inputs changed, so every charter-global section below is re-derived in full; none is carried forward by reference.
- Freeze time: 2026-10-06T19:55Z, before any round-2 task JSON was opened. Auditor: the same erl-task-policy-audit agent as round 1.
- Read in this round: the reworked `deposit.extended.yaml` (all six extended policies, read in full), `task_tools.py` (bodies and docstrings), `blueprint/products/deposit.yaml` (the base copy still equals it key by key), the round-2 views, and the gate snapshot `/tmp/orch43/snap_security_deposit_lifecycle_r2.txt` (all gates OK; check_traceability still deferred).
- Masked until the reveal below: the round-2 `tasks/*.json` GT fields and both worklogs (not read at any point).
- contamination_disclosure: this auditor revealed the round-1 GT of both tasks in round 1 (scored values, factor_sensitivity, closures, design_rationale). Round-2 derivations are therefore not blind with respect to round 1. Two things limit how far that knowledge could steer them:
  - view 1 is byte-identical to round 1, so task 1's round-2 derivation is a recomputation under the reworked charter;
  - task 0's seed changed, so its round-2 figures are new and were derived before any round-2 GT was read.
  The reworker's claim list (item ids only, no values) was also seen before the freeze.
- View diff (auditor's own diff of the round-1 vs round-2 views): task 0 changes exactly one field, `deposit_accounts.a18738d6….required_amount` 440.0 -> 480.0; frozen_time and user_scenario are identical. Task 1: no change.

### policy_conflict_scan (revision_2)

- Same six policies, same six target tools, owners and triggers as revision 0; `(target_tool, computes)` pairs are unchanged and each is claimed once.
- Overlap by subject is separated as before (assessment basis and tier; full-year vs part-year accrual; one refund policy).
- The reconnection rule now states its own scope against the base ceiling: "Because the account's own deposit had been waived, the reinstated deposit is the only other deposit such an account carries in assessed, partially_paid or held status; a reconnection on an account that carries any further open deposit is outside this policy." Both assessment policies now declare their deviation from `deposit_agg_service_total` in `overwrite`. No two policies reach incompatible conclusions on one record.
- Scope components are unchanged (reconnection <- {first installment, reinstatement}; recalc <- refund-date <- year-end), so a one-component-per-task split is still the only disjoint covering.

### rule_compute_equivalence (revision_2)

Unchanged bindings are as in revision 0. Changed bindings:
- **First installment.**
  - `meter_allowance` is removed from rule, compute and factors.
  - New `returns_12m` and `relief_points`: "with exactly one returned payment, the larger of the two point counts is taken in full and the smaller is taken at the single-return weight; with two or more returned payments, only the larger of the two point counts is taken; with none, the two point counts are added together" -> `MX(t,p) + 0.5*MN(t,p) if returns_12m == 1 else (MX(t,p) if returns_12m >= 2 else t + p)`. OK.
  - `share` = start_share - relief_points. OK.
  - `result: RND(required * share / 100, 2)` matches "rounded to the nearest cent once". OK.
  - The remainder and due-date sentence is now stated in the rule (non-scored).
- **Reconnection.**
  - `installment_payments`, `installment_date` (LATEST deposit_payment entry_date), `days_to_installment` = DAYS(assessed_date, installment_date) (9999 when none), `installment_relief` (<= 10 days prompt 0.5; <= tier `deposit_due_days` on-time 0.25; else 0) match "counted in calendar days from the reinstated deposit's assessed date to the posting date of the deposit payment on it (the latest one, where more than one has posted) …". OK.
  - `certificates_12` now matches "a medical certificate, accepted or not". OK; closes O5.
- **Year-end.** `kept_arrangement_end` = CFIELD(arrange ended_date, status completed, the account), `kept_arrangement_months` = MONTHS(end, NOW), tier < 12 / < 24 / else, match "an arrangement completed less than twelve whole months before the accrual is posted … at least twelve but fewer than twenty-four … otherwise none". OK, with observation N3: CFIELD reads the first matching completed arrangement, while the rule's "an arrangement" is existential.
- **Recalc.** `own_latest_connect_fee` is added, and `window_months` tier 1 = other-account fee within 12 months AND latest fee date != own latest fee date. This matches the reworded rule "the most recent connect fee billed on the member's service accounts falls in the twelve whole months before today and was billed on another account than this one". The only gap is a same-date tie between own and other fees (residual of O4; reached by neither world).
- Rounding: every "rounded half up" now reads "rounded to the nearest cent"; `RND` = Python `round`, which is round-to-nearest; the tie rule is unspecified (residual of O6, no value at a half cent).
- No RED.

### action_binding_and_uuids (revision_2)

- uuid8 tails unchanged (`114bda0d`, `9009d8a2`, `c3ac4854`, `3b717487`, `50449ec1`, `ead765c2`): distinct, no pattern.
- Function bodies are structurally identical to revision 0 (same `ctx.create` / `ctx.update` writes, no status, prerequisite or amount check). Docstring edits are limited to rounding wording ("rounded to the nearest cent before posting / before it is recorded"), which describes how the tool rounds its own argument, not a sequence.
- No docstring names another tool. No RED.

### prerequisite_graph (revision_2)

- Edges are unchanged in problem, kind, gate, form, policy_source and resolved_by; the graph is acyclic.
- The refund-date -> year-end `condition` now reads "For every calendar year before the refund year in which cash was held on the deposit, the deposit ledger carries a deposit_interest_accrual entry whose accrual_period_end is December 31 of that year". That is the same strength as its sentence, which closes O2.
- O3 is unchanged (the state_gate's `gate` is a DB field).
- New observation **N1**: the reconnection -> first-installment edge's `effect` still says "the installment relief moves from nothing to the part-paid installment relief". The part-paid tier no longer exists; the ladder is now prompt / on-time / later. The text is not a rule sentence and drives no value.

### prerequisite_sentences (revision_2)

- The four sentences are verbatim as in revision 0 and pass the same four-point test, single resolving write and single-reading derivation.
- The new rule sentences add no cross-problem order:
  - the reconnection scope sentence above;
  - the recalc's "Interest accrued and not yet paid out, including a prior year's interest whose payout bill has already been issued, is paid with the recalculation refund.";
  - the first installment's restated remainder sentence.
- No RED.

### override_declarations (revision_2)

- **F1 closure:** `deposit_ext_year_end_interest.overwrite` now names the base sentence "Interest accrues on the held_amount for each day it was held, the accrual_days of a period counting the posting date of each deposit payment and the last day of the period, divided by interest_day_count." Its replaced_by is the delinquency-days sentence. That sentence is in the rule, so the merged semantics for a year-end accrual is unique. **Closed.**
- **F2 closure:** `deposit_ext_refund_date_interest.overwrite` names the same base sentence, replaced by the refund-date delinquency-days sentence (in the rule). **Closed.** Each policy supersedes the base sentence only within its own accrual; tranche-year accruals stay under the base, and no task tool claims them.
- **O1 closure:** both assessment policies now declare `deposit_agg_service_total`'s netting sentence as superseded (reinstatement: "A reinstated deposit is the only deposit its account carries …"; reconnection: "… less the required amount of the reinstated deposit on the account …"), and the reconnection rule scopes out accounts with any further open deposit. **Closed.**
- **O7 closure:** `deposit_ext_recalculation_refund` adds `deposit_evt_interest` to `base_policy_refs` and supersedes S5 ("The prior year's interest is paid out by interest_payout_method on the bill of interest_payout_month; part-year interest is paid out with the refund or applied with the deposit.") with "Interest accrued and not yet paid out, including a prior year's interest whose payout bill has already been issued, is paid with the recalculation refund." **Closed.**
- **O10 closure:** the first-installment rule now states the remainder split and the first-installment due date itself, instead of pointing at the superseded clause. **Closed.**
- The other base sentences are followed as in revision 0, re-checked against the reworked rule text. No undeclared override remains. No RED.

### factor_ladders (revision_2)

Only changed factors are listed; every other row of the revision-0 table is unchanged.

| policy | factor | label | tiers | distinct | multi-source | cross_difficulty | in rule | finding |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| first_installment | relief_points_combination (replaces remote_meter_allowance) | method | 3 (weighted max + 0.5 x min / max only / sum) | yes (distinct whenever both point counts > 0) | no | service | yes | honest method: the tiers change how two quantities are combined, not a number in a fixed formula. **F4 closed.** |
| reconnection | reinstated_installment_relief (re-based on payment timing) | parameter | 3 (0.5 prompt <= 10 days / 0.25 on time <= tier deposit_due_days / 0 later) | yes | no | null | yes | all three tiers are reachable by a customer who reaches the write (the first installment must have posted, but it may have posted promptly, on time or late), so no tier part holds of every such customer. **F3 closed.** |
| year_end | year_end_kept_arrangement_supplement (replaces new_meter) | parameter | 3 (0.05 / 0.02 / 0) | yes | no | arrange | yes | business reading plausible (reward for an arrangement kept on the secured account); closes the realism half of O9. |

- Counts: first installment 4 (3 P, 1 M); reconnection 6 (5 P, 1 M); year-end 4 (3 P, 1 M); the other three policies as in revision 0. All within 4-6, >= 2 P, >= 1 M.
- Fall-through and baseline:
  - `relief_points_combination` baseline `tenure_points + pledge_points` = its fall-through. The policy's `baseline.rule` ("the tier's first_installment_pct with no relief points") is silent on how the points combine. With all baselines substituted at once it gives relief 0 = "no relief points", so it is consistent. Observation **N2**: `baseline.rule` does not state the additive convention the factor's baseline uses when substituted alone.
  - `reinstated_installment_relief` baseline 0 = "no surcharge or relief" = its fall-through.
  - `year_end_kept_arrangement_supplement` baseline 0 = "no supplement".
- Residual O9 half: the `waiver_loss_adjustment` fall-through reachability is unchanged.
- Multi-source per component: the first component keeps notice_clearance_share, reinstated_account_record, waiver_loss_adjustment, reinstatement_remote_meter_relief, reconnection_arrangement_adjustment and reconnection_hardship_relief (remote_meter_allowance, a multi-source factor, was removed). The second component is unchanged. Cross-difficulty: both components unchanged (service and arrange; service, capital and arrange).

### findings (revision_2)

| item | round-1 class | round-2 status | grounds |
| --- | --- | --- | --- |
| F1 | SOURCE-POLICY RED | **closed** | day-count base sentence declared in the year-end `overwrite` |
| F2 | SOURCE-POLICY RED | **closed** | same, in the refund-date `overwrite` |
| F3 | SOURCE-FACTOR RED | **closed** | installment relief re-based on payment timing; three live tiers |
| F4 | SOURCE-FACTOR RED | **closed** | meter allowance replaced by a genuine method factor (point combination) |
| O1 | observation | closed | netting deviation declared in both assessment policies; reconnection scope sentence |
| O2 | observation | closed | `condition` matches sentence strength |
| O3 | observation | unchanged | state_gate `gate` is a field |
| O4 | observation | changed, residual | rule and compute aligned; same-date own/other fee tie unhandled |
| O5 | observation | closed | "accepted or not" in rule |
| O6 | observation | changed, residual | "nearest cent", tie rule unspecified |
| O7 | observation | closed | S5 superseded in recalc |
| O8 | observation | unchanged | year-end window anchored on posting date |
| O9 | observation | changed, partly closed | new-meter supplement removed; waiver_loss fall-through reachability unchanged |
| O10 | observation | closed | remainder and due date stated in rule |
| O11 | observation | unchanged | docstring business words |
| O12 | observation | unchanged | base before-energizing sentence |
| N1 | new observation | — | stale "part-paid" wording in the prerequisite `effect` |
| N2 | new observation | — | `baseline.rule` silent on the additive point combination |
| N3 | new observation | — | year-end CFIELD reads the first completed arrangement, not any |

No new charter-global RED, and no regression of a revision-0 PASS conclusion.

### closing_checklist (revision_2)

Written after the round-2 reveals. Pre-reveal hashes and clock: `_difficulty.md` `47c19857…`, `0.md` `002b2569…`, `1.md` `5697cf10…` at 2026-10-06T19:49:08Z. The "19:55Z" in `charter_global_frozen (revision_2)` was an estimate; the hash clock is authoritative.

- Per-task files correspond one-to-one with the tasks, each with a `## revision_2` holding a frozen derivation and a comparison. Revision-0 text is untouched. Both comparisons PASS:
  - task 0 **PASS** (round-1 SOURCE-FACTOR RED: F3 and F4 closed);
  - task 1 **PASS** (round-1 SOURCE-POLICY RED: F1 and F2 closed).
- Coverage and scope: round-2 `charter_scope` = task 0 {waiver_reinstatement, reinstated_first_installment, reconnection_deposit}, task 1 {year_end_interest, refund_date_interest, recalculation_refund}. The scopes are pairwise disjoint and cover all six extended policies; each task tool is used by exactly one task. uuid8 tails are unchanged, distinct and patternless.
- Problem trees:
  - task 0: 2 prerequisite problems, 1 value_input, owner=user write, acyclic;
  - task 1: 2 prerequisite problems, 2 value_input, owner=user root, acyclic.
  - The difficulty graph is a DAG with no cross-task edge. Each edge is false at the opening and bears weight (task 0: 325.00 vs 410.00, plus the gate; task 1: 389.54 vs 399.39, and 22.60 vs 9.85).
- Factors: 4-6 per computation, >= 2 parameter and >= 1 honest method each. Per task there is >= 1 multi-source and >= 1 cross-difficulty factor with seeded rows. Every ladder has three live, distinct tiers stated in the rule. Every factor bears weight against an honest baseline, and each all-baseline figure differs from gold:
  - task 0: 240.00 / 560.00 / 370.00 vs 108.00 / 450.00 / 325.00;
  - task 1: 13.25 / 9.00 / 189.39 vs 14.54 / 9.85 / 399.39.
- Policy self-consistency: no undeclared override remains (F1 and F2 closed; O1 and O7 declared).
- Instantiation-stage gates on the final form: the orchestrator's round-2 snapshot `/tmp/orch43/snap_security_deposit_lifecycle_r2.txt` (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK) was taken on the hashes this audit froze (`8d0e4e58…`, `f4d8bfd8…`). It is cited, not re-run. `check_traceability` remains deferred until the KB is published.
- Remaining observations, none a red light: O3, O4 residual (same-date tie), O6 residual (tie rule), O8, O9 residual (waiver-loss fall-through), O11, O12, T1-O1, N1 (stale "part-paid" in the prerequisite `effect`), N2 (`baseline.rule` silent on the additive point combination), N3 (CFIELD first completed arrangement), and the remote-meter multi-source classification (same `service_accounts` row; revision 0's table and task 0's rationale both list it).
- Difficulty source-layer verdict (revision_2): **PASS** — all four relationships PASS for both tasks.
