# Policy-task audit — bus_eligibility_and_stops / charter-global

## revision_1

## charter_global_frozen
- Freeze: 2026-10-24 18:18 UTC, auditor = independent erl-task-policy-audit agent (not the instantiator).
- Hashes (match the coordinator snapshot): `transport.extended.yaml` sha256 adf7a40f4c0bbf0f…, `task_tools.py` sha256 feb45cbfb4453f4c…; views 0.view.json 472d4b53b1bfcde7…, 1.view.json 49dbfb7136ea478f….
- Entry conditions (step 0): snapshot `/tmp/erl0078_coord/snap_bus_eligibility_and_stops_r1.txt` shows EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (--check), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; check_traceability deferred (coordinator). Masked views were supplied with hashes. Input complete.
- Read for this section: `blueprint/blueprint.yaml` (claim), `blueprint/products/transport.yaml`, `meals.yaml`, `care.yaml` (multi-holding), `enroll.yaml` (multi-holding), `share_tools.py` (finder list), `db_schema.json` (via DSL), `transport.extended.yaml`, `task_tools.py`, `audits/render_source/XF_recipe.md`, `owner_ruling.md`, the DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py`.
- Masked / unread at freeze: `tasks/*.json` (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure*), `plan.md`, `worklog.md`. Nothing in this section derives from a revealed GT.
- Scratch: `/tmp/audit_bus_eligibility_and_stops_0078/` (recompute.py, t0.py, t1.py, edges.py, sweep.py).

### policy_conflict_scan
- Base copy: every top-level key of `transport.extended.yaml` other than `extended_policies` is `==` to `blueprint/products/transport.yaml` (scratch dict comparison: category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies all True).
- Extended policies (4): P1 `transport_ext_meal_status_fee_adjustment` (record_fee_correction_81e67279, agent, state_due, billing_correction credit); P2 `transport_ext_family_cancellation_credit` (confirm_permit_cancellation_9706a650, user, on_request); P3 `transport_ext_offered_seat_permit_fee` (sign_seat_agreement_96917571, user, on_request, permit fee); P4 `transport_ext_seat_fee_meal_waiver` (post_waiver_credit_eb03a46e, agent, state_due, free/reduced waiver credit).
- Overlapping subjects: P1 and P4 both post meal-status-driven credits on a permit fee. Rule-level they are disjoint: P4 is scoped to "a permit fee posted later than its assignment's application date" and counts a status that took effect after posting at zero, "a later rise being left to the fee-waiver adjustment"; P1 is framed on "A meal status determined after a courtesy rider permit fee posted". Compute-level they are NOT disjoint (finding P-01). P2 and base `transport_cancellation_and_refunds`: the base cancellation-window sentence is retired by P2's overwrite; capacity revocation/conduct/refund sentences untouched and compatible. P3 and base `transport_evt_permit_fee` s1: scoped overwrite with in-force restatement (C1 met).
- Triggers / time anchors: P1 "on the day the transportation office finds it owed"; P4 owed once the seat fee stands; P2 last day of service = day of confirmation; P3 posting day = signing day. No two policies write the same `(table, event, credit_reason)`.
- Cross-category read boundaries: P1 meals (variant, benefit_effective_date, application submitted_date); P2 meals (variant); P3 enroll (grade_level), care (variant, status, campus); P4 meals (variant, carryover param, notices), care (subsidy_payer, status). All declared in `cross_category`.
- Scope partition (pre-reveal, from tool ownership and prerequisite edges only): tree A = {P2 root, P1 prerequisite}; tree B = {P4 root, P3 prerequisite}. Two disjoint trees covering all four policies, consistent with M=2.

### rule_compute_equivalence
- B5 sweep (scratch `sweep.py`): every `compute_basis` string of P1–P4 is a verbatim substring of its rule; every baseline.rule sentence is in its rule; each `overwrite.replaced_by` is in the rule and each `superseded_clause` is in the cited base rule.
- Month arithmetic: `MONTHS(x, K('day_marker_31'))` is a month-index offset (day 31 never triggers the day correction), so `MONTHS(a,M31) − MONTHS(b,M31)` = index(b) − index(a); `MONTHS(x,M10)==MONTHS(x,M31)` iff day(x) ≤ 10, likewise for 15/20. Every "whole calendar months … that month included / after the month" sentence matches its expression, except where noted in P-02.
- Rounding: every compute ends `RND(… + 0.000000001, 2)` on a non-negative value, matching "rounded half-up to the cent once on the result" (P1–P4). Exception: P4 can go negative (P-03). Tools: `_Money.cents` is a Decimal ROUND_HALF_UP class static method (B4 met).
- Edge mismatches found: P-01 (P1 scope gate absent from compute), P-02 (P1 months not limited to the permit period), P-03 (P4 adverse-action tier unfloored), P-04 (P4 status read at handling time vs "for the posting date of the fee"), P-05 (care first-match), P-06 (P2 request selection unstated).
- Factor ladders vs rule (A9): every tier of every `factors[].ladder` is a rule sentence and a branch of its `decides` binding, and every branch is a stated tier. Wording slack without a consequence: P1 effective_month_part says "the higher status took effect", compute reads the meal account's benefit_effective_date whatever the status; where it is not higher, share_difference = 0 and the result is 0 (observation O-02).
- Factor independence (A1, transitive read table in `sweep.py`): no factor binding reads another factor's binding in any policy. Assembly lives in plain bindings / `result` (A2). A5 order sentences are present in all four ("added … before the share difference is applied"; "added to the credited months … subtracted … replaces"; "added to the standard monthly seat rate … replaces"; "added to the covered months, never exceed the seat months").

### action_binding_and_uuids
- `(target_tool, computes)`: (record_fee_correction_81e67279, adjustment_amount), (confirm_permit_cancellation_9706a650, credit_amount), (sign_seat_agreement_96917571, permit_fee_amount), (post_waiver_credit_eb03a46e, waiver_amount). Each claimed by exactly one policy.
- uuid8s 81e67279 / 9706a650 / 96917571 / eb03a46e: pairwise different, no shared prefix, no sequence. Accepted as independent.
- Docstrings: none names another tool, none states a position in a sequence ("then" in "The correction then shows…" / "The family then sees…" describes the tool's own effect). No docstring example values (E2), no composite args (E3).
- Tool bodies (B6): every write tool calls ctx.create/update itself; formats enforced (positive / non-negative 2-dp amounts, enums, fee entry of the same assignment). Observation O-03: confirm_permit_cancellation's docstring calls the request "the family's pending permit cancellation request" but the body checks only type and assignment, not `request_status`.
- No tool judges a prerequisite: none reads billing_correction rows, meal status, or whether a seat fee exists beyond the id reference of the argument.

### prerequisite_graph
- P1 `prerequisite: []`; P3 `[]`; P2 → P1 (value_input, gate fee_net, form state); P4 → P3 (value_input, gate seat_fee_posted, form state). Both `problem` ids are extended policies of this file, neither is self; graph is acyclic (two disjoint edges).
- `policy_source` verbatim in the blocked rule: P2 "The cancellation credit is fixed only after the permit fee carries the billing correction owed for a higher meal status that took effect after the fee posted." (rule sentence 3); P4 "The seat waiver is not figured until the permit fee for the accepted seat stands on the assignment's billing record." (rule sentence 3). Both found by the sweep.
- `form: state` on both; no `fallback_reason` (correct). `resolved_by` = the depended-on `target_tool` in both. `gate` bindings exist (fee_net in P2 compute, seat_fee_posted in P4 compute) and genuinely move the result (task files demonstrate).
- `condition` strength: P2's condition adds "carries a larger waiver share than the share already credited", which is what "a higher meal status" means against the fee's credited share; not strengthened. P4's condition "a transport_permit_fee entry posted later than the assignment's application date" = "the permit fee for the accepted seat" under P3/P4's shared scope test. No authoring-viewpoint phrasing.

### prerequisite_sentences
- P2 edge: connective "only after"; waited-on state "the permit fee carries the billing correction owed …" is record-visible (a transport_fee_credit with credit_reason billing_correction against the fee) and named in table words; no tool, policy id, snake_case or row id. Exactly one write of the difficulty creates a billing_correction credit (record_fee_correction_81e67279; the other credit tools post cancellation_window and free/reduced_meal_waiver). Derivation: sentence → reader looks for the policy whose rule posts "a transport_fee_credit with credit_reason billing_correction against the permit fee" for a higher meal status after posting → P1 → its write. One reading.
- P4 edge: connective "not … until"; state "the permit fee for the accepted seat stands on the assignment's billing record"; exactly one write creates permit fee rows in this difficulty (sign_seat_agreement_96917571). Derivation: sentence → P3 ("the permit fee posts on the day the parent or guardian signs the courtesy rider permit agreement accepting the seat") → the parent's signing. One reading.
- Depended-on rules do not restate the sentences. Cross-references to other problems that ground no edge and state no order (observations O-08): P1 "so that months after it are left to the credit that closes the permit"; P4 "a later rise being left to the fee-waiver adjustment".
- Base sentences stating cross-problem orders ("A courtesy permit becomes active only once its permit fee is settled") ground no edge of this difficulty; observation only.

### override_declarations
Sentence by sentence over each `base_policy_refs` entry:
- P1 vs `transport_evt_permit_fee`: s1 (fee posts on application date) followed; s2 (fee-free types) followed; s3 (posting-date waiver) followed — the original waiver credit is left standing ("never lowers or removes"); s4 ("A meal status determined after the fee posted does not change that fee…") — handled differently, DECLARED; s5 (cap after waiver, due in 14 days) — followed in wording, but see O-07 (the correction ignores cap credits already on the fee). vs `transport_agg_household_permit_cap`: s1–s3 followed (the billing correction is not a cap credit; the base measure excludes billing_correction). vs `transport_bus_pass`: untouched. vs `transport_cancellation_and_refunds`: s2 retired by P2, others untouched.
- P2 vs `transport_cancellation_and_refunds`: s1 (only the family cancels; desk records the request, family confirms) followed and sharpened to a portal confirmation — consistent with lifecycle `active → cancelled by: user`; s2 (cancellation window credit) DECLARED and replaced; s3 capacity revocation, s4 conduct/withdrawal no credit, s5 refund timing/state — followed. vs evt_permit_fee / cap / bus_pass: P2's fee_net uses permit fee rows and meal/cap/billing credits only; replacement fees are excluded as the base requires.
- P3 vs `transport_evt_permit_fee`: s1 DECLARED, scoped, with the in-force content restated for every other courtesy application (C1 met); s3 waiver retired for seat fees by P4 (sibling, different clause); s5 due-date followed. vs `transport_eligibility_basis`: space-available / waitlist and fee-settled-before-active followed. vs cap: seat fee is a courtesy fee and is capped by base (followed). vs `transport_stop_assignment_rules`: followed.
- P4 vs `transport_evt_permit_fee` s3: DECLARED, scoped by a record test, in-force content (with its rounding sentence) restated (C1 met). s4: retired by P1; P4 is consistent with P1's replacement ("left to the fee-waiver adjustment"). cap / bus_pass / cancellation: followed.
- No undeclared override found in the anonymous-intermediate, 0/1-multiplier or dropped-branch forms.

### factor_ladders
| policy | factor | label | decides | tiers | distinct outcomes | multi-source | cross_difficulty | judgment |
|---|---|---|---|---|---|---|---|---|
| P1 | held_status_share | parameter | held_share | 3 | 100 / 0 / 50 | no | meals | real dimension; Paid tier lies wholly outside the write (O-02) |
| P1 | credited_share_level | parameter | credited_share | 3 | 100 / 50 / 0 | no | — | real; free-credited tier lies wholly outside the write (O-02) |
| P1 | effective_month_part | parameter | effective_part | 3 | 1 / 0.5 / 0 | no | meals | proration convention, plausible (O-09) |
| P1 | application_backdate | method | backdated_months | 3 | app-month window / start-month window / none | yes (meal account source AND application date) | meals | RED F-08 (USDA attribution misstated) |
| P1 | window_end_month | method | window_last_day | 3 | request month / report month / period end | no (tier 2 same table) | — | coherent; address-report tier weak (O-10) |
| P2 | credited_months_method | method | credited_months | 3 | all months / month-count incl. / month-count excl. | no | — | RED F-01 (tiers 2 and 3 one method) |
| P2 | notice_lead_months | parameter | notice_months | 3 | 1 / 0.5 / 0 | tiers AND request+date | — | real (refund by notice date) |
| P2 | riding_retention_months | parameter | retained_months | 3 | 1 / 0.5 / 0 | no | — | marginal (O-09) |
| P2 | conduct_withheld_months | parameter | conduct_months | 3 | 2 / 1 / 0 | no | — | dimension real (no refund for suspension), magnitude generous (O-09) |
| P2 | release_withheld_months | parameter | release_months | 3 | 1 / 0.5 / 0 | no | — | RED F-06 (invented penalty) |
| P2 | processing_charge_level | parameter | processing | 3 | 0 / 5 / 10 | no | meals | real (fee-waiver eligibility) |
| P3 | billed_months_method | method | billed_months | 3 | all / incl. / excl. | no | — | RED F-02 (tiers 2 and 3 one method) |
| P3 | held_seat_months | parameter | held_months | 3 | month-window / 0.5 / 0 | no | — | RED F-03 (tier 1 is a computed window: mislabelled); non-monotone (O-06) |
| P3 | application_timing_charge | parameter | application_charge | 3 | 25 / 15 / 0 | no | — | plausible; fixed 07-15 deadline applied to spring permits (O-05) |
| P3 | school_level_rate | parameter | level_adjust | 3 | −2 / +2 / 0 | no | enroll | RED F-05 (padding on a flat fee) |
| P3 | waiting_list_rate | parameter | wait_adjust | 3 | −2 / −1 / 0 | no | — | RED F-04 (invented allowance) |
| P3 | one_way_riding_share | parameter | riding_share | 3 | 0.60 / 0.80 / 1 | yes (care status AND campus vs assignment campus AND plan) | care | real (AM-only rider) |
| P4 | seat_status_share | parameter | status_share | 3 | 100 / 0 / 50 | yes (variant AND effective date vs fee date) | meals | real; 0 tier lies outside the write (O-02) |
| P4 | coverage_by_source | method | covered_months | 3 | to carryover month / through notice month / all seat months | yes (seat-fee scope AND meal source / notice) | meals | concept real; tier 2 defective (P-03) |
| P4 | carryover_end_month | parameter | carryover_end_part | 3 | 1 / 0.5 / 0 | yes | meals | proration convention (O-09) |
| P4 | childcare_subsidy_supplement | parameter | supplement_share | 3 | 50 / 25 / 0 | yes | care | RED F-07 |

- Counts as declared: P1 5 (3 parameter, 2 method); P2 6 (5 parameter, 1 method); P3 6 (5 parameter, 1 method); P4 4 (3 parameter, 1 method). Every `bindings` set disjoint; no `decides: result`; every fall-through = the baseline value/method (checked tier by tier against each `baseline` block and `baseline.rule`).
- After the tests: P2 and P3 have no `method` factor that survives (F-01, F-02; held_seat_months is labelled parameter).
- Baselines are self-sufficient: each `baseline.rule` yields a definite number from the records alone (P1 standard share reduced_meal_fee_waiver_pct, nothing credited, months after the effective month to period end; P2 months after the last-day month, nothing withheld, processing_charge; P3 permit_fee/months × months after the signing month, share one, no charge; P4 reduced share over all seat months, no supplement). Observation O-01: P4's baseline sentence names "the supplement months", a quantity defined only in the childcare factor's sentence (zeroed in the standard figure by "the supplement share is zero").

### findings
Charter-global RED findings (consequences are demonstrated on constructed producible worlds in `/tmp/audit_bus_eligibility_and_stops_0078/edges.py` and `t1.py`; per-task costs are in each task file).

**P-01 SOURCE-POLICY RED — P1's compute drops the rule's scope "a meal status determined after a courtesy rider permit fee posted".**
- Symptom: P1's compute has no comparison between benefit_effective_date and the fee's posted_date; it prices any fee whose credited share is below the held share.
- Evidence: rule sentence 2 frames the correction on "A meal status determined after a courtesy rider permit fee posted … and only in that case"; P4 says a status that took effect on/before posting is P4's ("a later rise being left to the fee-waiver adjustment"). compute `status_effective`/`months_after_effective`/`effective_part` contain no such gate, and `result` has no ceiling at the fee or at the period's months.
- Consequence: on task 1's world just after the seat fee posts (135.00 on 2026-09-09, no waiver yet; Free carryover effective 2026-07-01), P1 compute = 148.50 (adjustment_months 11 of a 10-month period, greater than the fee itself); the rule says nothing is owed. The tool record_fee_correction_81e67279 accepts the figure. A second (out-of-scope) write is priced where the rule prices none.
- Bears on: task 1 (mid-state); charter.

**P-02 SOURCE-POLICY RED — P1's months are not limited to the permit period, as the rule says.**
- Evidence: rule "The adjustment months are the whole calendar months of the permit period after the month the higher status took effect, through the last month of the adjustment window"; compute `months_after_effective = MX(0, MONTHS(status_effective,M31) − MONTHS(window_last_day,M31))` counts from the effective month whatever the period's start, and `effective_part` adds the effective month even when it is outside the permit period.
- Consequence (probe A): a Courtesy Rider Permit (Semester) spring_semester fee 135.00 posted 2026-11-02 with a 67.50 reduced waiver; Free (Household Application) effective 2026-11-04; figured 2026-11-20. Compute = 94.50 (7 months / 5). The rule gives 5 permit-period months (Jan–May) → 67.50, or 81.00 if November's part is counted. 94.50 also exceeds the 67.50 left on the fee.
- Bears on: charter (no task world is a semester permit).

**P-03 SOURCE-POLICY RED — P4 coverage_by_source tier 2 has no zero floor, and its record test also catches a reduction already in force.**
- Evidence: rule "for a status on a meal account whose latest benefit notice is an adverse_action notice, the covered months are the whole calendar months from the month the fee posted through the month of that adverse_action notice"; compute `(MONTHS(fee_day,M31) − MONTHS(adverse_notice_day,M31) + 1)` with no MX(0, …); `covered_total = MN(seat_months, …)` has no floor either.
- Consequence (probe B): Reduced-Price Meal Status (lowered after verification) whose latest notice is an adverse_action of 2026-09-20; seat fee 120.00 posted 2026-11-16. Compute = −8.57; the rule's range "November through September" is empty → 0 (no entry). The student keeps a Reduced status for the rest of the year, yet the record test zeroes or negates the waiver.
- Bears on: charter.

**P-04 SOURCE-POLICY RED — P4 reads the meal status at handling time; the rule reads it "for the posting date of the fee".**
- Evidence: rule "The status share is read from the student's School Nutrition meal account for the posting date of the fee"; compute `meal_level = CPARAM('meals','benefit_level', …)` is the status on file now; only the effective date is compared with the fee date.
- Consequence: a seat signed 2026-09-20 by a family on Free (Prior-Year Carryover), waiver figured on 2026-09-28 after the 2026-09-24 reversion to Paid Meal Status: compute status_share = 0 → nothing posted; rule (status for 2026-09-20) = free_meal_fee_waiver_pct → a positive waiver. (Task 1's frozen date 2026-09-09 sits two weeks before this carryover reversion.)
- Bears on: charter.

**P-05 SOURCE-POLICY RED (XF B2) — the care-enrollment read is a first-match with no stated selection.**
- Evidence: P3 `care_plan`/`care_open_here` and P4 `supplement_share` use `CFIELD('care', …, student_id, school_year)` (first row in table order). The rules say "the rider's Creek Kids Club enrollment for the school year". `care_agg_multi_holding`: "a withdrawn student may register again for the same school year", so two rows for one student and year can be produced.
- Consequence (probe C, task 1's world plus a withdrawn row listed first): P3 compute = 215.00 (share one); the rule, reading the active enrollment, gives 135.00. P4's supplement has the same exposure.
- Bears on: charter (task 1 seeds one care row).

**P-06 SOURCE-POLICY RED (XF B2) — P2 states no selection when several received permit_cancellation requests stand.**
- Evidence: P2 rule "when the family's permit_cancellation request on the assignment that stands with request_status received was received notice_days_full or more…"; compute takes `LATEST(… created_at …)`. P1 states "(the latest such request when there are several)", P2 does not, and no dedup rule exists for transport_requests.
- Consequence: requests received 2026-10-30 and 2026-11-05, last day 2026-11-09: latest → 4 days → 0 months; first → 10 days → 0.5 month. Two readings.
- Bears on: charter (task 0 has one request).

**F-01 SOURCE-FACTOR RED (XF A6) — P2 credited_months_method tiers 2 and 3 select one method.**
- Evidence: tier 2 = index(period end) − index(last-day month) + 1; tier 3 = the same count without the +1. Under A6, same calendar-month count with a different window, no added input or operation, means the pair FAILS. This leaves P2 with no `method` factor that passes (the other five are parameters).
- Bears on: task 0.

**F-02 SOURCE-FACTOR RED (XF A6) — P3 billed_months_method tiers 2 and 3 select one method.** Same shape as F-01, and P3 is left with no passing `method` factor.
- Bears on: task 1.

**F-03 SOURCE-FACTOR RED — P3 held_seat_months is labelled `parameter`, but tier 1's value is a computed window.**
- Evidence: tier 1 value "the whole calendar months from the month of the offer up to, but not including, the month of signing" (`MONTHS(stop_assignment_date) − MONTHS(NOW)`); tiers 2/3 are constants. The tier changes how the quantity is computed, so the label is dishonest.
- Bears on: task 1.

**F-04 SOURCE-FACTOR RED (realism F2) — P3 waiting_list_rate.**
- "Families kept waiting for a seat receive a waiting-list rate" (−2.00 / −1.00 a month by days waited). No district publishes a discount for time spent on a courtesy-seat waitlist; it is an invented allowance stacked on a flat permit fee.
- Bears on: task 1.

**F-05 SOURCE-FACTOR RED (realism F2) — P3 school_level_rate.**
- ±2.00 a month by KG–05 / 09–12 grade band on the courtesy permit, whose charter fee (`permit_fee` 240.00 / 135.00) is flat per transportation type with no grade dimension. This is padding on a flat fee.
- Bears on: task 1.

**F-06 SOURCE-FACTOR RED (realism F2) — P2 release_withheld_months.**
- Withholding refund credit (1 / 0.5 month) for no-adult PM returns. The base charter treats a return as a safety procedure that "does not count as a conduct offense and never revokes a courtesy permit". A refund penalty for it is not something a district publishes.
- Bears on: task 0.

**F-07 SOURCE-FACTOR RED (realism F1/F2) — P4 childcare_subsidy_supplement.**
- A transport fee-waiver "supplement" for households whose Creek Kids Club care is Workforce Solutions CCS-funded. Its second tier is an invented 25 % `ccs_pending_share` for a registered/waitlisted CCS enrollment: a share no district schedule would publish, and a CCS-pending supplement with no published basis.
- Bears on: task 1.

**F-08 SOURCE-FACTOR RED (realism F4) — P1 application_backdate misstates the USDA rule it cites.**
- Rule: "the district dates a household application's benefit from the month the application was received, as USDA permits a local educational agency to do". USDA (Eligibility Manual for School Meals) lets an LEA use the date the application was submitted as the effective date, not the start of that calendar month. The tier credits the whole month of receipt (an application received on the 28th earns that whole month), which is more than the cited federal allowance.
- Bears on: task 0.

Observations (no RED):
- O-01 P4 baseline names "the supplement months", which are defined only in the childcare factor's sentence (A3-adjacent; zeroed in the standard figure).
- O-02 P1 held_status_share Paid tier, P1 credited_share_level free-credited tier and P4 seat_status_share 0 tier always give a result of 0 ("owed as nothing"). Among customers who reach the write, each of these ladders has two live tiers.
- O-03 confirm_permit_cancellation does not enforce "pending" on the request id.
- O-04 P3 scope "first assigned after the first school day" depends on a future event at the application date, and the records keep only the latest stop_assignment_date.
- O-05 P3 application_timing_charge applies the fixed 2026-07-15 deadline to spring_semester permits.
- O-06 P3 held_seat_months is non-monotone (signed 11+ days after an offer in the same month → 0; 6–10 days → 0.5).
- O-07 P1's correction ignores household_cap credits already on the fee, and the base cap measure excludes billing_correction. With a capped fee, total credits can exceed the fee.
- O-08 P1 and P4 rules refer to the other problems' quantities; no order is stated.
- O-09 Realism marginal, not struck: effective_month_part and carryover_end_month (10th/20th-day proration), riding_retention_months (retention after 30 riding days on top of the processing charge), conduct_withheld_months (dimension real, a month per suspension generous).
- O-10 P1 window_end_month tier 2: a pending address_change_report does not by itself end service.
- O-12 Neither P1 nor P4 nets corrections or waivers already posted. Repeats are closed only by the base fee_credit grain ("One row per credited fee per credit reason").

## closing_checklist
Written after both reveals (2026-10-24 18:21:22 UTC). Not every relationship passes, so the difficulty does not close.
- Audit files 0.md and 1.md correspond to tasks 0 and 1, alongside this file. revision_1 only.
- Coverage: the charter_scope of task 0 = {P1, P2} and of task 1 = {P3, P4}. They are disjoint and cover all four extended policies; each task tool is called by exactly one task; the uuid8s are independent.
- Trees: each has 1 prerequisite problem, 1 value_input edge and 1 owner=user write; the difficulty graph is acyclic. Task 1's tree fails SOURCE-CHAIN (T1-1).
- Factors: see findings F-01..F-08 and the per-task T0-1, T1-2, T1-3. The method floor fails in P2 and P3.
- Gates: not re-run by this audit (the coordinator owns the re-run on the final form).
- Instantiator realism flags judged:
  - RED: school-level rate F-05, waiting-list rate F-04, CCS supplement F-07, PM-release withholding F-06.
  - Not struck (O-09): half-month tiers.
  - Plausible: held-seat billing (but mislabelled, F-03) and carryover coverage (but its adverse tier is defective, P-03).
  - The USDA backdate attribution is RED (F-08).

VERDICT revision_1: task0=RED task1=RED charter=P-01,P-02,P-03,P-04,P-05,P-06,F-01,F-02,F-03,F-04,F-05,F-06,F-07,F-08

## revision_2

## charter_global_frozen (revision_2)
- Freeze: 2026-10-24, before any revision-2 task JSON or worklog claim was read; auditor = same independent auditor as revision_1. The revision_1 text above is untouched.
- Entry: the worklog's last non-empty line is `REWORK round 2: gates 7/7 green`. Snapshot `/tmp/erl0078_coord/snap_bus_eligibility_and_stops_r2.txt` (run by me, execute-only) shows all 7 gates OK.
- Hashes: extended.yaml 8190ad623ac1df32…, task_tools.py 4b689506ac3be450…. Views r2/0 71b60996b492a14a…, r2/1 333ac1767571dc15….
- Both shared inputs changed, so every charter-global section is re-derived below. New rulings read in full: `audits/render_source/realism_bar.md` (R1–R5 / X1–X4). XF_recipe.md and owner_ruling.md are unchanged since revision_1 (mtime Oct 23).
- Base copy is still verbatim (all ten base keys `==` the blueprint). Scratch: `/tmp/audit_bus_eligibility_and_stops_0078/{recompute2,t0r2,t1r2,edges2,probes2,sweep}.py`.

### policy_conflict_scan (r2)
- Same four policies, tools and owners.
- P3's overwrite now retires base `transport_evt_permit_fee` s1 for every courtesy fee ("Every courtesy rider permit fee is the courtesy permit fee of this schedule"). It still posts on the application date, except for waiting-list seats, which post at signing.
- P4's replaced_by now restates the posting-date waiver for other fees as "the fee, less the application charge it carries". This modification of out-of-scope content is declared inside the overwrite.
- P1 is now gated on `rise_after_posting` and capped at the fee net of credits. P1 and P4 are disjoint in compute as well as in rule: P1 on task 1's mid-state = 0.00.
- Scope partition: {P1, P2} and {P4, P3}, as before.

### rule_compute_equivalence (r2)
- B5 sweep: every compute_basis quote, baseline sentence, replaced_by and superseded clause is verbatim. A1: no factor reads another factor's binding (`sweep.py` table).
- Round-1 edge probes re-run (`edges2.py`):
  - P1 spring-semester probe = 67.50, the rule's 5 permit-period months (P-02 closed).
  - P4 adverse probe = 0.00, and tier 2 now requires a notice dated after the status on file took effect (P-03 closed).
  - Swapping the order of care rows leaves P3 unchanged (P-05 closed: status 'active' filter, care charter's one-open-enrollment sentence quoted).
  - P2 request selection is now stated ("latest by its received time"; P-06 closed).
  - P4 status share is now read "on the day the seat waiver is figured, by this record test", which matches compute (P-04 closed by rule wording).
  - P1 compute now carries the rule's scope gate and a fee-net cap (P-01 closed).
- New edge mismatch N-05 (below): P3 compute fails on an application with no stop assigned, a case the rule now prices because it governs every courtesy fee.

### action_binding_and_uuids (r2)
- Unchanged bindings and uuid8s.
- confirm_permit_cancellation now refuses a request that is not `received`, matching its docstring ("pending (received)"). O-03 is closed.
- No ordering words and no other tool names in the docstrings. No tool judges a prerequisite.

### prerequisite_graph / prerequisite_sentences (r2)
- Edges and policy_source sentences are unchanged and verbatim. Form state; acyclic.
- P2's condition now states the vacuous case ("when no such status exists nothing is owed and the condition holds"), which closes D1.
- One write per waited-on state, as in revision_1.

### override_declarations (r2)
- P3: s1 retired for every courtesy fee and the in-force posting-date content restated; the base `permit_fee` survives only as the "any other rider" rate (grades 06–08). Declared.
- P4: s3 retired with a restated rule for other fees (net of application charge). Declared.
- P1: s4 retired; the base cap ordering is now respected by the cap at the fee net of every credit (O-07 closed).
- P2: cancellation-window sentence retired. Declared.
- No undeclared override found.

### factor_ladders (r2) — realism judged against realism_bar.md
| policy | factor | label | shape cited | verdict |
|---|---|---|---|---|
| P1 | held_status_share | parameter | R1 meal status | passes; but its baseline is the straw man of N-01 |
| P1 | credited_share_level | parameter | R1 meal status | passes |
| P1 | effective_month_part | parameter | R3 half-month proration by effective date | passes |
| P1 | application_receipt_part | parameter | R4 Eligibility Manual date-of-application option + R3 | passes (F-08 closed) |
| P1 | window_end_month | method | none of R1–R5; tier 2 is X1 | RED N-02 |
| P2 | credited_share_method | method | R3 (whole / half-month for Annual / daily for Semester) | passes A6 (month count vs day count), so F-01 is closed |
| P2 | application_charge_withheld | parameter | R1/R2 school-calendar window: late application charge non-refundable | passes (X3 adjacency: O-r2-2) |
| P2 | notice_lead_months | parameter | R2 notice N days before | passes |
| P2 | riding_retention_months | parameter | X2: the same start→last-day relation as credited_share_method tier 1, stacked on the proration | RED N-03 |
| P2 | conduct_withheld_months | parameter | X1: invented penalty (months forfeited per suspension count) | RED N-04 |
| P2 | processing_charge_level | parameter | R1 meal status | passes |
| P3 | billed_share_method | method | R3 | passes A6, so F-02 is closed |
| P3 | held_seat_months | parameter (constants now) | R2 days after the offer | passes, so F-03 is closed |
| P3 | application_timing_charge | parameter | R1 school-calendar date window | passes |
| P3 | school_level_rate | parameter | R1 grade band (216 / 240 / 264 annual; 121.50 / 135 / 148.50 semester) | passes, so F-05 is closed |
| P3 | walk_zone_distance | parameter | R1 distance band | passes |
| P3 | one_way_riding_share | parameter | R1 plan / days per week | passes |
| P4 | seat_status_share | parameter | R1 meal status | passes |
| P4 | coverage_by_source | method | R4 (7 CFR 245 carryover; 245.6a adverse-action period) | passes |
| P4 | carryover_end_month | parameter | R3 half-month by the carryover end date | passes (complementary month, not stacked: O-r2-3) |
| P4 | application_charge_excluded | parameter | R1 date window: waivers do not reach a late charge | passes (X3 adjacency: O-r2-2) |
- Removed since revision_1: application_backdate, release_withheld_months (F-06 closed), waiting_list_rate (F-04 closed), childcare_subsidy_supplement (F-07 closed).
- Counts after strikes:
  - P1: 4 surviving, 0 method. Method floor fails (N-02).
  - P2: 4 surviving (1 method, 3 parameter). Within bounds, but below its drawn 6.
  - P3: 6 (1 method).
  - P4: 4 (1 method).

### findings (r2, charter-global)
**N-01 SOURCE-FACTOR RED — P1's baseline is a straw man: the standard figure is zero on every world.**
- Evidence: baseline.rule "In the standard figure the waiver share of the meal status on file and the waiver share already credited are both zero". The share difference is then 0, and the result is 0 for every customer ("owed as nothing").
- A meal-status fee adjustment whose standard method can never produce a figure is "a zero where the standard method gives a figure". In revision_1 the standard held share was reduced_meal_fee_waiver_pct.
- Consequence: the computation document never yields a correction, so a baseline reader posts nothing in every world. held_status_share's baseline/fall-through is the Paid tier, which lies outside the write.
- Bears on: task 0.

**N-02 SOURCE-FACTOR RED (realism X1) — P1 window_end_month tier 2.**
- "for an open assignment on which a permit_cancellation request stands with request_status received, the adjustment window ends with the month that request was received".
- The correction is forfeited for months the student still rides on a higher status, merely because a cancellation request is pending. No district publishes such a curtailment. Tier 1 (end_date of a closed assignment) would be R3.
- Consequence: P1 is left with no method factor.
- Bears on: task 0.

**N-03 SOURCE-FACTOR RED (realism X2) — P2 riding_retention_months is stacked on the proration.**
- It is keyed on the same start→last-day relation as credited_share_method tier 1 (≤ 10 days → whole fee). It withholds a further month once 30 days are ridden, on top of a proration that already refunds only the remaining period.
- Bears on: task 0.

**N-04 SOURCE-FACTOR RED (realism X1) — P2 conduct_withheld_months.**
- One or two months of refund forfeited by suspension count (a 3-day suspension costs a month). Real handbooks at most decline to refund suspended days; this table shape is an invented penalty.
- In revision_1 this was observation O-09; it is struck now under realism_bar X1.
- Bears on: task 0.

**N-05 SOURCE-POLICY RED (XF B1/B2 absent record) — P3 compute fails when no stop is assigned.**
- Evidence: P3's rule now governs "Every courtesy rider permit fee", including application-date postings made before any stop is assigned. `held_months` evaluates `MONTHS(F('stop_assignment_date'), …)` on an empty field.
- Consequence (`probes2.py`): a fresh application with empty stop_assignment_date raises ValueError. The rule gives "otherwise nothing is added".
- Bears on: charter (both task worlds have stop dates).

Round-1 charter REDs: P-01 … P-06 closed; F-01, F-02, F-03 closed; F-04, F-05, F-06, F-07 closed (removed or rebuilt as R1); F-08 closed.

Observations (r2):
- O-r2-1 P1's baseline.rule names "the application charge it carries", but the sentence defining it (plain binding fee_application_charge) is outside baseline.rule. This is moot while N-01 stands.
- O-r2-2 P2 and P4 re-derive the late charge already carried inside the posted fee (X3-adjacent). It is load-bearing because the ledger shows no breakdown, and it is realistic (late fees are non-refundable and not waivable).
- O-r2-3 P4 coverage_by_source tier 1 and carryover_end_month split one carryover proration across two factors, covering complementary months; no double effect.
- O-r2-4 Same-date benefit-notice ties remain unstated (DSL residue).
- O-02 persists for P1's Paid tier, now as its baseline (see N-01).

### class sweep (revision_2, after the reveals; every class raised in revision_1 or revision_2, over all four policies)
- Scope gate in compute (P-01 class): P1 rise gate; P3 one schedule for both postings; P4 seat_fee_scope; P2 family cancellation only. Clean.
- Period / share limits (P-02 class): P1 window and period caps; P2 share in [0, 1]; P3 billed + held ≤ 1 (one held month at most, and only when the offer was in an earlier month); P4 MN(seat_months). Clean.
- Floors (P-03 class): P1, P2, P3 (MX(0, period_rate)), P4. Clean.
- Status read time (P-04 class): P1 "on the day the adjustment is figured"; P2 "on the last day of service"; P4 "on the day the seat waiver is figured"; P3 latest-registered enrollment. Clean.
- Selection / decoy (P-05, P-06 class): requests latest received (P1, P2); care status active (P3); enrollment latest-registered (P3); meal account by student. Residue: same-date notice ties (O-r2-4). Absent-record probe: N-05 (empty stop_assignment_date).
- A6 method pairs: P1 window (end_date / request / period end), P2 credited share (one / months / days), P3 billed share (one / months / days), P4 coverage (carryover / notice / seat months). All pass.
- Label honesty (F-03 class): every parameter tier is a constant or a P/K read. Clean.
- A8 cancelling pairs (T0-1 class): none in any computation on either world.
- Realism: N-02, N-03, N-04 RED; all other factors cited to R1–R4 in factor_ladders (r2).
- Baseline honesty: N-01 (P1). P2, P3 and P4 baselines are self-sufficient and nonzero (62.78 / 216.99 / 62.22).
- Persona raises a prerequisite (T1-1 class): closed in both tasks.
- Persona/DB conflict: R2-T0-1.
- Seed E1: task 0 fee/waiver/payment re-priced consistently; task 1 care rows R2-T1-1.

## closing_checklist (revision_2)
- Not closable. RED remain in charter (N-01..N-05) and in both tasks (R2-T0-1, R2-T0-2, R2-T1-1).
- Coverage and disjointness, uuid8s, trees (1 prerequisite, 1 value_input edge, 1 owner=user write each, acyclic) and gates 7/7 (snapshot r2) are as stated above.
- Every round-1 RED is closed: P-01..P-06, F-01..F-08, T0-1..T0-3, T1-1..T1-4.
- New or reclassified REDs:
  - N-01, N-05 are new.
  - N-02 was O-10 and N-04 was O-09 in revision_1; both are struck now under realism_bar X1.
  - N-03 is new, under realism_bar X2.
- Rework claim O-10 ("window tier 2 replaced") does not match the charter.

VERDICT revision_2: task0=RED task1=RED charter=N-01,N-02,N-03,N-04,N-05

## revision_3

## charter_global_frozen (revision_3)
- Frozen before reading any revision-3 task JSON or the round-3 claims. Revisions 1–2 are untouched.
- Entry: the worklog's last non-empty line is `REWORK round 3: gates 7/7 green`. Snapshot `/tmp/erl0078_coord/snap_bus_eligibility_and_stops_r3.txt` (run by me, execute-only) shows all 7 gates OK.
- Hashes: extended.yaml e7b7ca1d481992a4… (changed), task_tools.py 4b689506ac3be450… (unchanged since revision_2). Views r3/0 5a7db6e0f01a3ead…, r3/1 a939fffa2bb70e6b….
- Rulings: realism_bar.md read in full, including AMENDMENT 1 (R6, six conditions). XF_recipe.md and owner_ruling.md are unchanged.
- The base copy is still verbatim. The B5 verbatim sweep and the A1 factor-reads table (`sweep.py`) are clean for all four policies.
- What changed: P1 and P2 are rebuilt. P3 adds an empty-field guard to the held months, and P4 adds a notice tie rule and a guard on the application date. Tool bodies and docstrings are unchanged, so the revision_2 `action_binding_and_uuids` section carries forward on the unchanged task_tools hash.
- The prerequisite edges, their policy_source sentences and conditions are textually unchanged from revision_2, so `prerequisite_graph` / `prerequisite_sentences` carry forward. One write per waited-on state, acyclic.

### rule_compute_equivalence (r3)
Round-2 items re-checked (`edges3.py`, `probes3.py`, `t0r3.py`, `t1r3.py`):
- N-05 is closed. A fresh application with no stop assigned prices 115.20, with held months 0, as the rule gives.
- N-01 is closed. P1's standard share is reduced_meal_fee_waiver_pct, with day-count months; the all-baseline figure on task 0 is nonzero and differs from gold.
- N-02 is closed. The window is now the end_date of an ended or cancelled assignment, otherwise the period end; the pending-request tier is gone from rule and compute.
- Round-1 probes still hold: P1 spring permit = 67.50; P4 adverse-action probe = 0.00; P1 on task 1's mid-state = 0.00; care row order makes no difference.
- P4 now states the tie rule for same-date notices (O-r2-4 closed).

New edges checked, all consistent:
- P1 tier "status took effect before the first school day → all months" ignores the window by its own wording.
- P2 credited share = 1 when there is no start_date.
- P2 payment processing kept, as in the rule: 3 % of online_card payments plus 1.00 per ACH draft, rounded once on the result.

### override_declarations (r3)
- As in revision_2, plus P2's new payment-processing-kept sentence.
- Base `transport_payments` and `transport_cancellation_and_refunds` carry no clause on processing costs, so nothing is contradicted and nothing new needs declaring.

### factor_ladders (r3) — realism against R1–R6 / X1–X4
| policy | factor | label | shape | verdict |
|---|---|---|---|---|
| P1 | held_status_share | parameter | R1 meal status | passes |
| P1 | unadjusted_application_charge | parameter | R1 school-calendar date window (late charge not waivable) | passes; X3-adjacent as O-r2-2 |
| P1 | month_count_method | method | R3 (all months / whole months on Annual / daily) | passes A6 |
| P1 | effective_month_part | parameter | half-month taper on the effective date, already the month_count_method date | RED R3-01 (X2/R2) |
| P1 | application_receipt_part | parameter | R4 Eligibility Manual date-of-application + R3 | passes |
| P2 | credited_share_method | method | R3 (one / whole months after the last-day month on Annual / daily) | passes A6 |
| P2 | application_charge_withheld | parameter | R1/R2 (late charge non-refundable) | passes |
| P2 | notice_lead_months | parameter | R2 notice lead | passes |
| P2 | last_month_part | parameter | half-month taper on the last day of service, already the credited_share_method date | RED R3-01 (X2/R2) |
| P2 | payment_processing_kept | parameter | R1 payment method; card/ACH processing costs non-refundable is a commonly published refund clause; 3 % / 1.00 plausible | passes (see R6 note at reveal) |
| P2 | processing_charge_level | parameter | R1 meal status | passes |
| P3 | billed_share_method | method | R3 | passes |
| P3 | held_seat_months | parameter | R2 days after the offer | passes |
| P3 | application_timing_charge | parameter | R1 date window | passes |
| P3 | school_level_rate | parameter | R1 grade band | passes |
| P3 | walk_zone_distance | parameter | R1 distance band | passes |
| P3 | one_way_riding_share | parameter | R1 plan | passes |
| P4 | seat_status_share | parameter | R1 meal status | passes |
| P4 | coverage_by_source | method | R4 carryover / 245.6a | passes |
| P4 | carryover_end_month | parameter | half-month taper on carryover_last_operating_day, already coverage_by_source tier 1's date | RED R3-01 (X2/R2) |
| P4 | application_charge_excluded | parameter | R1 date window | passes |

Counts after strikes:
- P1: 4 (1 method).
- P2: 5 (1 method).
- P3: 6.
- P4: 3 — below the 4-factor floor (R3-02).

### findings (r3, charter-global)
**R3-01 SOURCE-FACTOR RED (XF A6 / realism_bar X2 and R2 "ONE factor per timing dimension per computation, never stacked with a second proration of the same dates").**
- Three computations split one half-month proration convention into two factors keyed on the same recorded date. All three members:
  - P1: effective_month_part, stacked on month_count_method's tier "whole calendar months after the month the status took effect" (benefit_effective_date).
  - P2: last_month_part, stacked on credited_share_method's tier "whole calendar months of the permit period after the month of the last day" (last day of service).
  - P4: carryover_end_month, stacked on coverage_by_source's tier "whole calendar months … up to, but not including, the month of carryover_last_operating_day" (carryover_last_operating_day).
- In each, the whole-month count and the part-month taper are one R3 convention, which R3 itself describes ("whole-month or half-month proration … selected by a recorded attribute"). Two factors on one timing dimension is a taper stacked on a proration of the same date.
- The round-2 claims themselves give this reading for P2: "the separate last-day-month part was folded into credited_share_method's monthly tier (one proration per last-day date, X2)". Round 3 splits it out again.
- Auditor disclosure: in revision_2 I recorded P4's pair as observation O-r2-3 ("complementary months, not stacked"). That was a misjudgment by me, not a change in the artifact. The pair has been present since revision_1. The required class sweep now lists all three members together.
- Bears on: task 0 (P1, P2) and task 1 (P4).

**R3-02 SOURCE-FACTOR RED (floor) — once R3-01 strikes carryover_end_month, P4 carries 3 surviving factors.**
- That is below the 4-factor floor (realism_bar: the floor is not waivable). P1 (4) and P2 (5) stay within bounds.
- Bears on: task 1.

Closed round-2 items:
- N-01 (P1 baseline): closed.
- N-02 (window tier): closed.
- N-03 (riding retention): removed.
- N-04 (conduct withholding): removed.
- N-05 (empty stop guard): closed.

Observations (r3):
- O-r3-1: After the correction posts, P1's rule ("less the meal-status waiver credits already on the fee") does not net the billing correction. A re-evaluation would price a further 31.20 (task 0). Only the base fee_credit grain (one row per fee per credit reason) closes this (O-12 persists).
- O-r3-2: P1's "all months" tier for a status effective before the first school day ignores an early end_date window, by its own wording.
- O-r2-2 persists (late charge re-derived inside P1, P2 and P4).

### R6 grading (revision_3, after reveal; the round-3 claims tag one factor)
- P2 payment_processing_kept, tagged R6 — **R6-WAIVED (BLUEPRINT-KNOWN)**, observation:
  1. Recorded key: transport_ledger.payment_method and amount. Holds.
  2. Figures 3 % and 1.00 per draft. Holds.
  3. No federal/state or in-force base conflict; refunds still go by district check. Holds.
  4. Not a named X1 mechanism; card-cost non-refundability is a commonly published clause. Holds.
  5. A1 and B5 clean; it reads only payment rows (no X2); no posted amount carries it (no X3); edge probes with check-only and ACH-only payments hold. Holds.
  6. Minimal: 1 R6 factor. Even with last_month_part struck (R3-01), P2's honest count is 4, so the allowance would be 2. Holds.
- (The factor would also pass as R1 by its payment-method key.) No other factor is tagged R6, and no untagged factor fails an R6 condition.

### class sweep (revision_3; every class raised in revisions 1–3, over all four policies)
- Scope gate, period/share limits, floors, status read time: clean. Revision_2 sweep holds; P1 rebuilt and re-probed.
- Selection / decoy / absent record: requests (P2), care status and school_year (P3), enrollment latest-registered (P3), notice ties (P4 now stated); empty stop / application / start / distance guards present. Clean.
- A6 method pairs: P1 month_count, P2 credited_share, P3 billed_share, P4 coverage. All pass.
- One timing dimension, one factor (X2/R2): R3-01 lists all members (P1 effective_month_part, P2 last_month_part, P4 carryover_end_month). Not members:
  - P3 held_seat_months (offer → signing lead).
  - P2 notice_lead_months (request → last day).
  - P1 application_receipt_part (receipt date).
  - The application-charge factors (application date).
- Label honesty: clean. A8 cancelling pairs: none on either world.
- Baseline honesty: P1 (6.22), P2 (11.26), P3 (216.99) and P4 (62.22) are all nonzero and differ from gold.
- Realism X1/X3/X4: no member. X3-adjacent: O-r2-2.
- Persona/prerequisite and persona/DB: clean in both tasks.
- Seed E1: clean in both tasks.
- Floor: R3-02.

## closing_checklist (revision_3)
- Not closable. Open: R3-01 (charter, three members), R3-02 (P4 floor), R3-T0-1, R3-T1-1.
- All revision_2 REDs are closed: N-01..N-05, R2-T0-1, R2-T0-2, R2-T1-1. No regression of any revision_1 item.
- Gates 7/7 green (snapshot r3).
- Note for the coordinator: R3-01 reverses my own revision_2 observation O-r2-3, which the round-3 rework relied on to split P1 and P2. If you rule that a whole-month count plus a separate partial-month factor on the same date is one acceptable R3 convention split in two, R3-01 and R3-02 fall away and the difficulty is otherwise clean.

VERDICT revision_3: task0=RED task1=RED charter=R3-01,R3-02

## revision_4

## charter_global_frozen (revision_4)
- Frozen before reading any revision-4 task JSON or the round-4 claims. Revisions 1–3 untouched.
- Entry: worklog last line `REWORK round 4: gates 7/7 green`. Snapshot `/tmp/erl0078_coord/snap_bus_eligibility_and_stops_r4.txt` (run by me) shows all 7 gates OK.
- Hashes:
  - extended.yaml 1d561d4677993cb6… (changed)
  - task_tools.py 4b689506ac3be450… (unchanged, so action_binding_and_uuids carries forward)
  - views r4/0 12358ef50db4ecb5… (redesigned world) and r4/1 a939fffa2bb70e6b… (unchanged from r3)
- realism_bar.md, XF_recipe.md and owner_ruling.md are unchanged since revision_3.
- Base copy verbatim. B5 verbatim sweep clean; A1 factor-reads table clean (`sweep.py`).
- Prerequisite edges and their sentences are unchanged, so those sections carry forward.

### what changed
- R3-01 fold-back:
  - P1's effective-month part is now inside month_count_method's Annual tier.
  - P2's last-day-month part is now inside credited_share_method's Annual tier.
  - P4's carryover end-month part is now inside coverage_by_source's carryover tier.
  - Each is one proration convention per timing dimension, stated in one ladder tier.
- New factor class "held-seat charge": the months P3 bills for a seat held between the offer (stop_assignment_date) and posting. It is re-derived from the posted fee as (fee − application charge) × held / (months covered + held) and then:
  - P1 `unadjusted_held_seat`: excluded from the waivable fee.
  - P2 `unrefunded_held_seat`: withheld from the refund base.
  - P4 `unwaived_held_seat`: excluded from the seat waiver base.
- P1 now spreads over "the months the fee covers" (fee_months) and subtracts billing corrections already posted. O-r3-1 is closed; re-evaluation after the correction = 0.00.
- P2 spreads over fee_months, and its day share is over the fee's span.

### rule_compute_equivalence (r4)
Probes re-run:
- P1 spring-semester probe (`probeA4.py`) = 67.50.
- P1 on task 1's mid-state = 0.00.
- P3 with no stop assigned = 115.20.
- P3 is independent of the order of care rows.
- P1 re-evaluated after its own correction = 0.00.

The held-seat fraction is consistent with P3's composition: for an Annual seat, (held/10)/(billed/10 + held/10) = held/(months covered + held). Task 1: 0.5/9.5. Task 0: 1/10. The rule text in P1, P2 and P4 states the same formula.

### factor_ladders (r4) — realism R1–R6 / X1–X4 (R6 grading of tagged factors is appended at reveal)
| policy | factor | shape | verdict |
|---|---|---|---|
| P1 | held_status_share | R1 | passes |
| P1 | unadjusted_application_charge | R1 date window | passes (O-r2-2) |
| P1 | unadjusted_held_seat | carve-out of a service charge from a TEC 11.158 fee waiver | see R4-01 |
| P1 | month_count_method | R3 (now carries the effective-month part: one factor per date) | passes A6 / X2 |
| P1 | application_receipt_part | R4 date-of-application | passes |
| P2 | credited_share_method | R3 (now carries the last-day-month part) | passes |
| P2 | application_charge_withheld | R1/R2 | passes |
| P2 | notice_lead_months | R2 | passes |
| P2 | unrefunded_held_seat | R2 (a billed period already consumed before service began is not refunded) | passes |
| P2 | payment_processing_kept | R6-WAIVED in r3; unchanged | observation |
| P2 | processing_charge_level | R1 | passes |
| P3 | all six | as revision_3 | pass |
| P4 | seat_status_share | R1 | passes |
| P4 | coverage_by_source | R4 + R3 carryover part in one tier | passes |
| P4 | unwaived_held_seat | carve-out of a service charge from the meal-status waiver | see R4-01 |
| P4 | application_charge_excluded | R1 | passes |

### findings (r4, charter-global)
**R4-01 SOURCE-FACTOR RED (realism X1 invented carve-out; and X3 "nothing already in a recorded amount" with no real basis).** Members:
- P1 `unadjusted_held_seat` ("Nor does it reach a held-seat charge").
- P4 `unwaived_held_seat` ("Meal-status fee waivers never reach a held-seat charge either").

The held-seat charge is P3's own service billing for months the seat is held: the same period rate times months, billed in P3's schedule as ordinary seat months. Unlike the late application charge, which is a penalty and not a fee for service (accepted in revisions 2–3, observation O-r2-2), no district fee-waiver schedule carves a held seat out of a meal-status waiver. Both factors re-derive a component the posted fee already carries, only to exclude it from the waiver.

Consequence:
- In P4 the carve-out holds even when the status was in force during the hold. Task 1's Free carryover (effective 2026-07-01) covered the 2026-08-31 offer, yet the factor removes that half month from the waiver base (12.16 without vs 11.52 with).
- In P1 the carve-out applies whatever the status's effective date. Its tier 1 counts all months of the period for a status in force before the first school day, and still excludes the held month.

P2's `unrefunded_held_seat` is NOT a member. A refund of unused service months not reaching a billed hold period already consumed is the R2 refund-schedule shape.

Bears on: task 0 (P1) and task 1 (P4).

**R4-02 SOURCE-FACTOR RED (floor, conditional on R4-01).** Struck, P1 keeps 4 factors (within bounds) and P4 keeps 3 (below the 4-factor floor).
- Bears on: task 1.

Closed revision-3 items:
- R3-01 closed (all three parts folded into one tier per date).
- R3-02 closed (P4 has 4 declared factors; but see R4-02).
- O-r3-1 closed.

Observations:
- O-r2-2 now extends to the held-seat component in P2 (late and held components re-derived from the posted fee).
- payment_processing_kept stays R6-WAIVED unless the round-4 tagging changes it (checked at reveal).

### R6 grading (revision_4, after reading the round-4 claims; supersedes the provisional R4-01 / R4-02 above)
The claims tag all three held-seat factors R6. AMENDMENT 1 says an R6-tagged factor is RED only if one of the six conditions fails. My frozen R4-01 applied the general "would a parent find this" test, which AMENDMENT 1 replaces for R6-tagged factors. The tags come from the claims, not from GT, so this grading is not a GT-driven change.

Grading of unadjusted_held_seat (P1), unrefunded_held_seat (P2) and unwaived_held_seat (P4):
1. Recorded key: stop_assignment_date and the fee's posted_date (lead days between two recorded dates). Holds.
2. Figures: P3's own held_days thresholds and month counts, nothing new; the held component is the seat's own billed months, not a fraction of another price. Holds.
3. No federal/state rule or in-force base clause contradicted:
   - The base posting-date waiver for other fees is restated in P4's scoped overwrite.
   - Seat fees and their corrections are declared overrides.
   - TEC 11.158(b) requires reasonable waiver procedures and does not fix their scope.
   - Holds.
4. Not a named X1 mechanism. Holds.
5. A1 and B5 clean; within each computation no other factor reads the offer→posting relation (no X2). X3 is read exactly as for the late-charge factors since revision_2 (O-r2-2): removing a component the posted fee carries is not re-pricing it. Holds under the reading applied in revisions 2–4.
6. Minimal: P1 has 4 honest factors (drawn 5) → 1 R6. P2 has 5 honest factors (payment_processing_kept passing as R1) → 1 R6, within the allowance of 2 even if it counted as R6. P4 has 3 honest factors (drawn 4) → 1 R6. Holds.

Result: all three are **R6-WAIVED (BLUEPRINT-KNOWN)** observations. R4-01 is withdrawn. R4-02 falls with it (an R6-waived factor counts toward the floor; it is "not a FLOOR item").

Coordinator point: if the coordinator reads X3 / condition 5 literally ("nothing already in a recorded amount"), then all six component-exclusion factors are members:
- the three late-charge factors (O-r2-2)
- the three held-seat factors

I have not applied that reading in any revision.

### class sweep (revision_4; every class from revisions 1–4, whole charter)
- Scope gate, period limits, floors, read time, selection / decoy / absent record: clean. Probes re-run (spring 67.50, mid-state 0.00, no-stop 115.20, care order, notice tie, self-netting 0.00).
- A6 method pairs: clean.
- One factor per timing dimension (R3-01 class): clean after the fold-back. P3 held vs billed are different relations; P1 receipt month vs effective month are different months.
- Label honesty, A8 pairs, baselines (P1 103.91 / P2 25.07 / P3 216.99 / P4 62.22): clean.
- Realism: R1–R5 as tabled; R6-WAIVED: payment_processing_kept and the three held-seat factors. X1/X4: no member.
- Persona: clean in both tasks.
- Seed E1: task 1 clean; task 0 has R4-T0-1 (approval before settlement).

## closing_checklist (revision_4)
- Closed revision-3 items:
  - R3-01, R3-02, R3-T0-1, R3-T1-1
  - O-r3-1, O-r3-2
- Open: R4-T0-1 (task 0 seed). The charter is clean.
- No regression of any revision 1–3 item. Gates 7/7 (snapshot r4).
- GT matches my frozen derivations figure for figure in both tasks.

VERDICT revision_4: task0=RED task1=PASS charter=CLEAN

## revision_5

## charter_global_frozen (revision_5)
- Frozen before reading any revision-5 task JSON or the round-5 claims.
- Entry: worklog last line `REWORK round 5: gates 7/7 green`. Snapshot `/tmp/erl0078_coord/snap_bus_eligibility_and_stops_r5.txt` (run by me) shows all 7 gates OK.
- Hashes: extended.yaml 1d561d4677993cb6… and task_tools.py 4b689506ac3be450…, both unchanged from revision_4, so every charter-global section of revision_4 carries forward by reference on these two hashes.
- Views: r5/0 02d7ab8001c121d6… (task 0 seed changed); r5/1 a939fffa2bb70e6b… (unchanged).
- New ruling read in full: realism_bar.md AMENDMENT 2.
  - "Split prorations" confirms the R3-01 reading; the revision_4 fold-back satisfies it.
  - "X3 / R6 condition 5 vs component exclusions" confirms the reading applied since revision_2. The late-charge and held-seat exclusions are read from recorded dates (application_date; stop_assignment_date and posted_date), so they are not X3. The coordinator point raised in revision_4 is resolved.
  - "Meal forecast shape" does not apply to this difficulty (no meal forecast computation).
- R6 grading of revision_4 stands under AMENDMENT 2: payment_processing_kept and the three held-seat factors are R6-WAIVED (BLUEPRINT-KNOWN).
- Class sweep (all classes raised in revisions 1–5) re-run over the unchanged charter. Probes give the same results (no-stop 115.20; mid-state 0.00; self-netting 0.00; care-order independence). Clean.

## closing_checklist (revision_5)
Written after both reveals (2026-10-24 23:24:08 UTC).
- Per-task audit files 0.md / 1.md correspond to tasks 0 / 1. Revisions 1–5 are kept in order; every revision-5 comparison carries a PASS.
- Coverage: task 0 = {P1 fee-waiver adjustment, P2 family cancellation credit}; task 1 = {P3 seat fee, P4 seat waiver}. Pairwise disjoint and jointly complete. Four task tools, each called by exactly one task. uuid8s independent (revision_1, unchanged since).
- Trees: each has 1 prerequisite problem, 1 value_input edge and 1 owner=user write (the cancellation confirmation under ruling (a); the seat agreement under ruling (d)). The difficulty graph is acyclic. Each prerequisite is unmet at the opening and bears weight (skip runs 146.27 and 0.00).
- Factors (per computation):
  - P1: 5 factors (1 method, 4 parameters).
  - P2: 6 (1 method, 5 parameters).
  - P3: 6 (1 method, 5 parameters).
  - P4: 4 (1 method, 3 parameters).
  - Each task has ≥1 multi-source and ≥1 cross-difficulty factor.
  - Ladders: every one has ≥3 tiers, distinct outcomes, and is stated in its rule.
  - Weight: every factor bears weight on its task's world, against an honest baseline; each all-baseline result is nonzero and differs from gold.
  - No cancelling pair.
  - Realism: every factor is R1–R5. Four R6-WAIVED (BLUEPRINT-KNOWN) observations: payment_processing_kept, unadjusted_held_seat, unrefunded_held_seat, unwaived_held_seat.
- Gates: all 7 green on the final form (snapshot r5).
- Closed revision-4 items: R4-T0-1 (seed), plus R4-01, R4-02, R4-T0-2 and R4-T1-1, all withdrawn in the revision-4 R6 grading and confirmed by AMENDMENT 2. No regression of any revision 1–4 item.
- Observations kept for the record:
  - O-r2-2: component exclusions are read from recorded dates (not X3 per AMENDMENT 2).
  - O-12: the base fee_credit grain blocks a repeat write; P1 also nets its own correction now.

VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

## revision_6

## charter_global_frozen (revision_6)
- Frozen before reading the round-6 claims or any revision-6 task JSON.
- Entry: worklog last line `REWORK round 6: gates 7/7 green`. Snapshot `/tmp/erl0078_coord/snap_bus_eligibility_and_stops_r6.txt` (run by me) shows all 7 gates OK.
- Hashes:
  - extended.yaml 41fa27e89d6fdc38… (changed).
  - task_tools.py 4b689506ac3be450… (unchanged, so action_binding_and_uuids carries forward).
  - Views r6/0 02d7ab8001c121d6… and r6/1 a939fffa2bb70e6b… are identical to r5, so the task worlds are unchanged.
- Round items: renderer scan-first findings S1–S8 in `audits/render_source/bus_eligibility_and_stops/render_r1.md` (read in full).
- Rulings: realism_bar.md (AMENDMENT 1 and 2), owner_ruling.md and XF_recipe.md, all unchanged since revision_5.
- Re-derived over the changed charter (text diff against the revision-4/5 charter):
  - B5 verbatim sweep: clean.
  - A1 factor-reads table: clean. P1 `application_received` is now a plain binding, read by month_count_method and application_receipt_part, with no factor reading another factor's binding.
  - Base copy: verbatim.
  - Prerequisite edges and sentences: unchanged, carried forward.

### S1–S8 verification (probes in `witness6.py`, `probes6.py`, `t0r6.py`, `t1r6.py`)
| item | fix in the charter | verification | status |
|---|---|---|---|
| S1 P1 cap omits cancellation/proration credits | `credits_against_fee` = every fee_credit whose source is the fee entry | renderer witness (fee 240, reduced 120, Free effective Aug 1, cancellation credit 120): compute 0.00 = rule | closed |
| S2 P1 "inside the permit period" vs first school day | rule and ladder now say "on or after the permit period's first school day" | rule = compute = ladder | closed |
| S3 P1/P2 MX(1, months covered) | divisors are the months covered themselves; P2 notice "nothing for a fee that covers no months" with a > 0 guard; P1 adjustment capped by months covered | fall seat offered Nov 20, signed Dec 8: months covered 0.8156, held fraction 0.5508 = rule's 1/1.8156; no crash | closed |
| S4 P3 walk-zone boundary | rule now "less than that walk zone" / "outer_band_miles or more and not less than that walk zone" = compute `<` / `>=` | equality defined | closed |
| S5 P1 status effective after the window end | counted months "none" and receipt part gated on the effective date ≤ window end (rule, ladder, compute) | witness (end 2026-08-20, Free effective 2026-09-01): 0.00 | closed |
| S6 shared selections | P1: application_received is a plain binding with a stated selection sentence. P3: the rule now states the grade selection once as its own sentence ("The rider's grade is the grade_level on the student's latest-registered … record"); the walk-zone sentence no longer leans on the school-level sentence | P3 compute still re-reads the same XLATEST inline in `level_rate` and `rider_walk_zone` (identical expressions, no plain binding); equivalent, no reachable divergence | closed at rule level; observation O-r6-1 |
| S7 P4 cap counts non-fee credits | `credits_against_fee` filtered to source = the fee entry | free_replacement credits (source = the pass fee) excluded | closed |
| S8 P4 out-of-scope fallback | rule: "This rule figures no seat waiver for a permit fee that is not the fee of a seat …"; result `… if seat_fee_scope else 0` | non-seat fees are priced nothing by P4 and keep the restated base posting-date waiver | closed |

### regression check
- Task worlds are unchanged and the recomputed figures are identical to revision_5 for every scored value, baseline and sensitivity in both tasks.
- No exactly cancelling pair. Prerequisite skip runs 146.27 / 0.00.
- Earlier probes unchanged: mid-state 0.00, self-netting 0.00, no-stop 115.20, care order.

### class sweep (all classes raised in revisions 1–6, whole charter)
- Clean:
  - scope gates; period/share limits (now including fractional months covered); floors
  - status read time; selection, decoy and absent record
  - A6 method pairs; one factor per timing dimension (AMENDMENT 2); label honesty
  - A8 pairs; baselines (103.91 / 25.07 / 216.99 / 62.22, unchanged)
  - realism (R1–R5; R6-WAIVED: payment_processing_kept and the three held-seat factors, unchanged)
  - X3 per AMENDMENT 2; persona; seed E1
- New observation O-r6-1: P3 compute does not hoist the stated grade selection into a plain binding. The rule-level requirement of A4 is met and the two inline reads are identical.

### claims check (revision_6, after reveal)
- S1–S8 claims match the charter changes and witnesses recorded above.
- S6 P3: the claim gives the reason the compute keeps the inline XLATEST (the gates require a cross-difficulty factor's binding to read its category directly). That accounts for O-r6-1, which stays an observation (rule-level A4 met, identical expressions).
- S8: the carve-out is a record test (seat_fee_scope) with in-force base text restated, which is C4-compliant.

## closing_checklist (revision_6)
- All eight renderer items (S1–S8) are closed. No new defect.
- No regression of any item closed in revisions 1–5. GT matches the frozen derivations in both tasks.
- Gates 7/7 green (snapshot r6).
- Coverage, trees, factor counts and bounds, realism grading and R6-WAIVED observations are as in closing_checklist (revision_5).

VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN
