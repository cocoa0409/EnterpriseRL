# Policy-task audit — transfers_and_enrollment_changes / charter-global

## charter_global_frozen
- Freeze: 2026-10-24T18:44:06 (file mtime; revision_1), auditor: independent policy-task auditor (erl-task-policy-audit), coordinator brief /tmp/erl0078_coord/audit_common.txt.
- Hashes checked against the gate snapshot /tmp/erl0078_coord/snap_transfers_and_enrollment_changes_r1.txt: `enroll.extended.yaml` sha256 19a56d19f365c70e (match), `task_tools.py` 0ec8c84ea220751e (match), views 0.view.json 7de15f7ddac0531e / 1.view.json 460258898f5d2747 (match).
- Read for this section: blueprint.yaml, db_schema.json, share_tools.py, products/enroll.yaml (and, for cross-product pricing, products/care.yaml and products/meals.yaml), the extended charter, task_tools.py, audits/render_source/XF_recipe.md and owner_ruling.md, the DSL evaluator in skills/erl-task-instantiate/scripts/check_compute.py (MONTHS/DAYS/LATEST/within_months semantics).
- Masked and not read before both task derivations were frozen: tasks/0.json, tasks/1.json (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure), plan.md, worklog.md. This section contains nothing derived from GT.
- Entry conditions: the snapshot shows the 7 instantiation gates OK (EXTENDED, TASK TOOL CONTRACT, REPLAY --check, SOLVABILITY, COMPUTE, GROUNDING, SCOPE); check_traceability deferred by the coordinator. Entry conditions complete.

### policy_conflict_scan
Seven extended policies, all on the Pre-K (Tuition-Based) tuition ledger:

| id | subject | target_tool (owner) | trigger | prerequisite |
|---|---|---|---|---|
| P1 enroll_ext_combined_program_credit | enroll_tuition_credit (billing_correction, vs a tuition charge) | credit_prek_combined_program_abf513c1 (agent) | state_due | [] |
| P2 enroll_ext_late_fee_assessment | enroll_tuition_late_fee | post_prek_late_fee_f766f23b (agent) | state_due | [] |
| P3 enroll_ext_advance_payment | enroll_tuition_payment | pay_prek_tuition_in_advance_058a705f (user) | on_request | P2 (value_input, action), P1 (value_input, action) |
| P4 enroll_ext_eligibility_month_credit | enroll_tuition_credit (eligibility_established, vs a tuition charge) | credit_prek_eligibility_month_43743e06 (agent) | state_due | [] |
| P5 enroll_ext_late_fee_share_reversal | enroll_tuition_credit (eligibility_established, vs a late fee) | credit_prek_late_fee_reversal_2a81de73 (agent) | state_due | P4 (value_input, action) |
| P6 enroll_ext_late_fee_hardship_waiver | enroll_tuition_credit (billing_correction, vs a late fee) | credit_prek_late_fee_waiver_decba573 (agent) | state_due | P5 (value_input, action) |
| P7 enroll_ext_payment_plan_installment | enroll_tuition_payment | pay_prek_plan_installment_1e1e8562 (user) | on_request | P6 (value_input, action) |

- Overlapping subjects: four policies post `enroll_tuition_credit`; they are separated by source row (tuition charge vs late fee) and credit_reason (P1/P6 billing_correction, P4/P5 eligibility_established), so each credit row is attributable to one policy. Two payment policies are separated by the customer's request (pay the year in advance vs a payment plan). No two policies settle the same quantity.
- Triggers/terminal states: P1/P2/P4/P5/P6 are state_due credits/fees; P3/P7 are customer payments through the portal. P2's credits-not-counted unpaid portion and P1's charge-and-care-only inputs make P1 and P2 commute (no shared balance read).
- Cross-category read boundaries: P1/P2 read care (care_enrollments variant/status/subsidy_payer/start_date, care plan monthly_tuition, care_ledger ACH payments); P4/P5/P6/P7 read meals (meal_accounts variant/benefit_effective_date, meal_notices approval letters). All reads are declared in `cross_category`; no tool of this difficulty writes another category's rows (D4 trigger rule holds: the tools write only enrollment_ledger rows whose base events carry `triggers: []`).
- Scope exclusivity / completeness (from the views' worlds only, before reveal): task 0's world (tuition-based enrollment, active CCS-funded Pre-K Wraparound, unassessed December late fee, advance-payment request) engages P3 <- {P2, P1}; task 1's world (enrollment moved to State-Eligible on 2027-01-01, Reduced-Price status effective 2026-12-15, two late fees, payment-plan request) engages P7 <- P6 <- P5 <- P4. The two trees are disjoint and together cover all 7 policies. Confirmed against charter_scope only after the reveal (see task files).

### rule_compute_equivalence
- Scratch sweep /tmp/audit_transfers_and_enrollment_changes_0078/sweep.py (B5): every `compute_basis` quote of all 7 policies is verbatim in its rule; every baseline.rule sentence is in the rule; every prerequisite `policy_source` and every overwrite `replaced_by` is in the rule; every compute binding has a basis and vice versa.
- Ladder face vs compute face: for every declared factor each tier the ladder names is a branch of its `decides` binding and vice versa (checked by hand for all 33 factors). Rounding: every result is `RND(x + 0.000000001, 2)` on a non-negative value, matching "only that final amount is rounded to the nearest cent, half a cent rounding up"; tool bodies use `_Fmt.money` (Decimal ROUND_HALF_UP, class static method) — B4 holds.
- Window conventions: `within_months=K` counts rows with 0 <= MONTHS(posted, NOW) < K (MONTHS = whole months, day-of-month compared), which matches "within the last K months" / "within the last whole month" on the tasks' dates; `MONTHS(F('entry_date'), NOW)` matches "fewer than N whole months before ..." (B3 holds).
- Defects of this class are listed under findings: C-P2, C-P3 (rule words no compute tests), C-P4/C-P5 (rule sentences with two readings), C-P10/C-P11 (A3/A4), C-P12 (B2 tie rule).

### action_binding_and_uuids
- Each `(target_tool, computes)` is claimed by exactly one policy (7 tools, 7 policies, all `computes: amount`).
- uuid8s abf513c1, f766f23b, 058a705f, 43743e06, 2a81de73, decba573, 1e1e8562: no shared prefix, no sequence, no common tail; independent.
- Docstrings: no docstring names another tool or states a position in a sequence among actions. The only ordering words are intra-call ("the tool rounds half up to the cent before booking"; "the first installment" as an ordinal of the plan) — observation O-3, not a sequence statement.
- Tool bodies check only format (YYYY-MM, positive amount, payment_method in {online_card, ach_bank_draft}, source-row existence); no tool judges a prerequisite, an eligibility or an amount. Every write tool calls `ctx.create` (B6 holds). Docstrings carry no concrete figures or task codes (E2 holds); no composite string args (E3 holds).
- Owner ruling (audits/render_source/owner_ruling.md, (b)): both owner=user tools are portal payments the parent makes personally after the agent quotes the amount, and P3/P7's rules state it ("which the parent or guardian makes personally through the district's online payment portal ... (district staff never take card or bank details)"); no base sentence assigns tuition-payment posting to staff, so no scoped overwrite was owed. Accepted.

### prerequisite_graph
- `prerequisite` present on all 7 policies ([] on P1, P2, P4). Edges: P3->P2, P3->P1, P5->P4, P6->P5, P7->P6. Every `problem` is an extended policy id of this file, none self-referential, none a base policy. Acyclic (two components: a fan-in of 2 and a chain of 3).
- All five edges are `form: action` with a `fallback_reason`; `kind: value_input`; `gate` names a real compute binding (open_balance / advance_month_rate / reversal_share / waiver_base / plan_balance); `resolved_by` is the depended-on policy's target_tool and its effect genuinely changes that binding (open balance, the most recent charge's credits, rs_credits, hw_credited, the plan balance).
- `condition` vs sentence: P3->P2's condition ("For the most recent billing month whose tuition was left unpaid after its due day ...") is narrower than its sentence ("the late fee owed for every billing month whose tuition was left unpaid after its due day") — finding C-P7. The other four conditions match their sentences. No authoring-viewpoint wording in any prerequisite field.

### prerequisite_sentences
| edge | sentence (verbatim, in the blocked rule) | connective | waited-on action in business words | names a tool/id? |
|---|---|---|---|---|
| P3->P2 | "The advance payment is not fixed until the late fee owed for every billing month whose tuition was left unpaid after its due day has been assessed." | not ... until | assessing the late fee | no |
| P3->P1 | "The advance payment is fixed only after the combined-program credit owed on the most recent billing month has been worked out and posted for a child who attends Creek Kids Club Pre-K Wraparound Care (5 Days)." | only after | working out and posting the combined-program credit | no |
| P5->P4 | "The late-fee reversal is not fixed until the eligibility credit owed on the month's tuition has been worked out and posted." | not ... until | the eligibility (basis-month) credit | no |
| P6->P5 | "The hardship waiver of a late fee is fixed only after the late-fee reversal owed for the month's eligibility credit has been worked out and posted." | only after | the late-fee reversal | no |
| P7->P6 | "The first installment of a payment plan is not fixed until the hardship waiver owed on the enrollment's most recent late fee has been worked out and posted." | not ... until | the hardship waiver | no |

- Fallback test (state form has priority): every depended-on schedule can owe exactly 0.00 (P2 de minimis/full hardship; P1 late start with no addition; P4 status effective > 25 days after the charge; P5 no eligibility credit; P6 no free/reduced status), the tools refuse a 0.00 amount and the ledger schema says amounts are "always positive" (D2), so no record-visible state singles out "worked out at nothing". The fallbacks are justified.
- Single reading of each hop: the depended-on rule is found by its business noun (late fee schedule; combined-program credit; basis-month eligibility credit; late-fee reversal; meal-benefit hardship waiver), each noun is the subject of exactly one extended rule, and no rule restates another's sentence, names a tool or another problem's id. No rule states a cross-problem order outside these five sentences. No base sentence grounds an edge.
- Defect: C-P7 (P3->P2 sentence broader than its condition and than what the resolver can do).

### override_declarations
Sentence-by-sentence against each `base_policy_refs` entry:
- P1 (refs enroll_tuition_payments_and_refunds, enroll_prek_admission, enroll_prek_tuition; overwrite []): payments-method/oldest-first, withdrawal-notice, refund sentences — not touched. prek_admission sentences — not touched (P1 uses billing_correction, not eligibility_established). prek_tuition charge/proration/rounding/late-fee sentences — not touched (P1 credits after the charge; the charge is unchanged). Follows. (Observation O-1: a recurring discount is booked under credit_reason billing_correction.)
- P2 (ref enroll_prek_tuition; overwrite of the late-fee sentence, declared): the replaced_by restates due day, oldest-first application and one fee per billing month, and states the amount comes from the schedule. Remaining prek_tuition sentences (posting dates, open-status gate, charge, rounding, 0.00 types) are inherited. Defect C-P5: the same rule then states a second due-day definition.
- P3 (ref enroll_tuition_payments_and_refunds; overwrite []): "Tuition is paid by the methods in accepted_payment_methods" (base list: online_card, ach_bank_draft, personal_check, money_order) vs P3 "makes personally through the district's online payment portal by online_card or ach_bank_draft" — undeclared narrowing, finding C-P6. Oldest-first: followed. Notice/refund sentences: not touched.
- P4 (refs enroll_prek_admission, enroll_tuition_payments_and_refunds; overwrite of the move/credit sentence, declared): replaced_by restates the effective date, the full credit of later months and the owed earlier months, and carves out the basis month. Rest inherited. No undeclared deviation found.
- P5 (refs enroll_tuition_payments_and_refunds, enroll_prek_admission; overwrite []): base is silent on late-fee reversals; the base credit event allows a credit against a late fee. Follows.
- P6 (same refs; overwrite []): base is silent on late-fee waivers. Follows (O-1 applies: a hardship waiver booked as billing_correction).
- P7 (ref enroll_tuition_payments_and_refunds; overwrite []): same undeclared method narrowing as P3 (C-P6); additionally the plan fee is a new charge the base charter has no event for (C-P8).

### factor_ladders
Counts as declared (sweep): P1 4 factors (3 parameter, 1 method; all 4 cross_difficulty care); P2 6 (5 p, 1 m; 1 care); P3 5 (3 p, 2 m; 0 cross); P4 4 (3 p, 1 m; 2 meals); P5 4 (3 p, 1 m; 2 meals); P6 4 (3 p, 1 m; 1 meals); P7 6 (5 p, 1 m; 1 meals). Every ladder has three disjoint tiers stated in the rule and implemented in compute; every fall-through equals the factor's baseline; every `decides` is an input, not `result`; binding sets are disjoint.

Realism verdict per factor (F1/F2, the coordinator's realism bar: a dimension a real Texas district publishes, plausible figures, no invented tapers/shares/allowances, a flat fee stays flat):

| policy | factor | label | verdict | reason |
|---|---|---|---|---|
| P1 | wraparound_payer_tier | parameter | keep (O-4) | bundle credit for Pre-K + district wraparound care is publishable; a reduced credit for a CCS-funded seat mirrors care's own "district rates do not combine with CCS funding" rule — weak but tolerable |
| P1 | wraparound_start_share | method | STRIKE | 5/20-day thresholds on a 30-day month are an invented taper; care's own charter bills that same month as a full month (start before half_month_start_day 16), so the credit is prorated for a month the family is billed in full |
| P1 | dual_program_autopay | parameter | STRIKE | a cash "AutoPay bonus" added to a tuition credit, graded by the count of ACH payments on another program's account (a one-off registration-fee payment counts) — no district publishes this |
| P1 | household_tuition_cap | parameter | STRIKE (CCS tier) | a household cap is publishable, but the CCS tier adds 50 % of an excess computed on the care plan's standard tuition, which a CCS-funded family does not pay; an invented share on a mis-measured sum |
| P2 | repeat_lateness_schedule | parameter | keep | escalating late fee for repeat lateness is a published pattern; 25/30/40 plausible |
| P2 | unpaid_portion_share | method | STRIKE (pro-rata tier) | de minimis "no fee" is real; prorating a flat late fee by the unpaid share is exactly "a flat fee stays flat" (F2); and the unpaid portion ignores credits the district itself posted ("credits not being counted"), assessing lateness on money not owed |
| P2 | subsidy_hardship_waiver | parameter | keep (O-5) | first late fee waived for a CCS-subsidized household is a plausible courtesy; the 50 % tier is a percentage stacked on a flat fee (borderline) |
| P2 | autopay_household_reduction | parameter | STRIKE | $3/$1.50 off a late fee by count of ACH payments — invented |
| P2 | entry_cohort_reduction | parameter | STRIKE | $2/$1 off a late fee for families new to the district / re-entering within 5 months — invented |
| P2 | payment_window_reduction | parameter | STRIKE | $2 off for a check at the cashier 1–3 days late, $1 off for ACH 1–2 days late — a real district publishes a grace period (no fee), not graded discounts on the fee |
| P3 | advance_rate_basis | method | STRIKE | prices every future month at the most recent charge less the credits against it, projecting one month's month-specific credit (start-month proration, one-off bonus) onto all later months; fall-through unreachable (C-F4); residue demonstrated in task 0 |
| P3 | advance_offer_terms | method | keep | pay-in-full discount (one month free / 3 %) is a published pattern |
| P3 | advance_autopay_terms | parameter | STRIKE | $4/$2 per month off a single advance payment by count of past ACH drafts — invented |
| P3 | continuing_family_tenure | parameter | STRIKE | 1 %/0.5 % "tenure" discount counting this year's posted charges — invented loyalty taper (and see C-P2) |
| P3 | good_standing_terms | parameter | STRIKE | 1 %/0.5 % discount by count of late fees — invented |
| P4 | basis_month_share | method | keep (O-6) | crediting the part of the basis month after eligibility is a plausible board choice; its 9/25-day, 30-day convention differs from the charter's half-month convention |
| P4 | awaiting_determination_allowance | parameter | STRIKE | $10/$5 added to a tuition credit for having made no/one payment in the last month — invented and rewards non-payment |
| P4 | household_approval_reach | parameter | STRIKE | $7.50/$5 added by the number of approval letters School Nutrition sent — invented |
| P4 | continuing_billing_tenure | parameter | STRIKE | $5/$2.50 by count of tuition charges — invented |
| P5 | credited_share_reversal | method | keep | reversing the late fee in proportion to the tuition credited is a natural correction |
| P5 | determination_window_addition | parameter | STRIKE | $3/$1.50 added by days between the late fee and the approval letter — invented (and C-P3) |
| P5 | meal_status_level_addition | parameter | STRIKE | $2/$1 added by meal status to a reversal already computed — invented |
| P5 | repeat_fee_addition | parameter | STRIKE | more late fees -> larger reversal — invented and perverse |
| P6 | standing_part_rule | method | keep | waiver acting on the part of the fee still standing is sound mechanics |
| P6 | meal_hardship_scale | parameter | keep | fee waivers for free (100 %) / reduced (50 %) households are published district practice |
| P6 | arrears_depth_addition | parameter | STRIKE | deeper arrears -> larger waiver add-on — invented |
| P6 | waiver_cohort_addition | parameter | STRIKE | $0.75/$0.50 by entry cohort — invented |
| P7 | plan_length_schedule | parameter | keep | installment count by balance is published practice |
| P7 | down_payment_terms | method | keep (O-7) | down payment for repeat-late payers is plausible |
| P7 | plan_fee_terms | parameter | STRIKE (ACH part) | plan fee waived/reduced by free/reduced status is publishable; the ACH-count half of both compound conditions is invented |
| P7 | eligibility_move_reduction | parameter | STRIKE | $10/$5 off the installment for having moved to State-Eligible — invented |
| P7 | plan_entry_cohort | parameter | STRIKE | invented cohort discount |
| P7 | plan_billing_tenure | parameter | STRIKE | invented tenure discount |

Surviving factors per policy: P1 1 (0 method), P2 2 (0 method once the pro-rata tier is struck), P3 1, P4 1, P5 1, P6 2, P7 2. Every policy is below the 4-factor floor (C-F2).

Method-shape all-pairs (A6), on the declared ladders: P1 start share (x0 / x(30-d)/30 / x1) pass; P2 unpaid share (x0 / x unpaid/charge / x1) pass; P3 advance_rate_basis tier "charge less credits" vs "charge" pass, "charge" vs "monthly_tuition" is a number substitution and the latter tier is unreachable (C-F4); P3 offer (P / P*m*pct / 0) pass; P4 share pass; P5 share pass; P6 standing part pass; P7 down payment pass.

Lesser-of / gating (A7, T2): P1 MN(charge, ...) never binds on producible values (max credit ~ 40 + 5 + 32 << charge). P4 `scoped_credit` zeroes the result whenever `credited_share` (factor basis_month_share) is 0, so with that factor at baseline no other P4 factor can ever move the result; P6 `scoped_waiver` does the same through `waive_pct` (meal_hardship_scale) — T2 fails for 3 factors of P4 and 3 of P6 (C-F3). P5 `scoped_reversal` gates the three additions on `rs_credits`, a binding of credited_share_reversal (A1/A10, C-F3).

### findings
Charter-global findings (each names the tasks whose file demonstrates its cost):

- **C-F1 SOURCE-FACTOR RED (realism, F2)** — 23 of 33 declared factors, or tiers of them, are invented padding (table above: P1 start_share, autopay, cap CCS tier; P2 pro-rata tier, autopay, cohort, payment window; P3 rate basis, autopay, tenure, standing; P4 awaiting, letters, tenure; P5 window, level, repeat; P6 arrears, cohort; P7 plan-fee ACH half, move reduction, cohort, tenure). Root cause: the ladders were built to satisfy factor counts with small cash adders and percentage tapers no Texas district publishes. Evidence: the rule sentences quoted in the table (enroll.extended.yaml lines 993–995, 1140, 1142–1144, 1325, 1327–1329, 1512–1514, 1646–1648, 1796–1797, 1953–1956). Consequence: each struck factor is a treatment "no such business would publish". Bears on tasks 0 and 1.
- **C-F2 SOURCE-FACTOR RED (factor count)** — counting only factors that pass the realism test, every policy has 1–2 factors (P1 and P2 also lose their only method factor), below the 4–6 / 2 parameter / 1 method floor. Tasks 0 and 1.
- **C-F3 SOURCE-FACTOR RED (A1/A7/A10 gating)** — P4 `scoped_credit: "credit_total if credited_share > 0 else 0.0"` (rule: "A month with no tuition credited under the share rule has no basis-month credit at all, allowances included."), P6 `scoped_waiver: "waiver_total if waive_pct > 0 else 0.0"` ("... has no hardship waiver at all, additions included."), P5 `scoped_reversal: "reversal_total if rs_credits > 0 else 0.0"`. With basis_month_share / meal_hardship_scale at their baselines (0.0 / 0) the result is 0.00 in every world, so awaiting_determination_allowance, household_approval_reach, continuing_billing_tenure (P4) and standing_part_rule, arrears_depth_addition, waiver_cohort_addition (P6) fail T2; P5's three additions read a binding of credited_share_reversal, so their documents cannot name what they modify without naming that factor. Task 1.
- **C-F4 SOURCE-FACTOR RED (A6 unreachable tier)** — P3 advance_rate_basis fall-through "otherwise (no tuition charge has posted yet) -> the type's monthly_tuition": base enroll_registration triggers enroll_tuition_charge for the tuition-based type and "the first month's tuition posts on the registration date", so an enrollment that can receive an advance payment always has a charge; the third tier is empty and the other two differ from it only by a substituted number. Task 0.
- **C-P1 SOURCE-POLICY RED (A2 assembly sentences)** — all 7 order sentences name factor quantities instead of stating the order generically: P1 "first the wraparound credit is taken at its share for the month, then the schedule's additions"; P2 "first the schedule fee is taken at its unpaid-portion share, then the reductions are subtracted ..., then the waived percentage is taken off"; P3 "priced at the advance month rate less the per-month reduction ..., then the offer and the percentage reductions"; P4 "first the month's tuition is taken at its credited share, then the allowances"; P5 "first the late fee is taken at its credited share, then the additions"; P6 "first the waived percentage is taken of the part the waiver acts on"; P7 "first the down payment is set aside, the rest ... divided by the number of installments ..., then the plan fee is added and the reductions". Consequence: no factor document can be rendered without naming another factor's quantity (A10). Tasks 0 and 1.
- **C-P2 SOURCE-POLICY RED (B8/A9, "continuing family")** — P3 "A continuing family whose enrollment already shows tenure_full_months or more posted tuition charges ...", P4 "A continuing family whose enrollment already shows five or more tuition charges ...", P7 "A continuing family whose enrollment shows five or more tuition charges ...". The base charter defines the term: enroll_agg_multi_holding "a continuing student is registered for each new school year with entry_type returning_student; a student never attending the district before is new_to_district". Compute (`tn_posted`, `tn_charges`, `pt_charges`) counts this year's posted charges and never reads entry_type. Two readings for a new_to_district enrollment with five charges: the tier applies (compute) or nothing applies (not a continuing family). Demonstrated in task 0 (P3) and task 1 (P4, P7).
- **C-P3 SOURCE-POLICY RED (B8/A9, framing clauses no record test checks)** — P5 "A late fee posted while the household's meal benefit application was being determined has an addition: window_near when the late fee posted no more than window_near_days calendar days before the household's most recent approval letter ..." (compute `dw_days` never reads meal_benefit_applications.submitted_date); P4 "A family that waited on its determination with the month unpaid is given an awaiting-determination allowance" (compute counts payments only); P2/P3 "An AutoPay household, whose enrollment shows ..." (no AutoPay enrollment record exists). Demonstrated for P5 in task 1 (late fee posted 2026-12-06, application submitted 2026-12-08).
- **C-P4 SOURCE-POLICY RED (handling time of the late fee)** — P2: "one late fee for that billing month posts tuition_late_fee_offset_days after the due day", yet the unpaid portion, "the enrollment's most recent payment" and "before the assessment" carry no as-of date, and the payment-window reduction rewards a payment made "no more than cashier_days calendar days after the due day", i.e. after the stated posting day. Evaluated on the stated posting day vs on the day the agent posts, the same fee has two values whenever a payment falls in between. Demonstrated in task 0.
- **C-P5 SOURCE-POLICY RED (two due-day sentences in P2)** — replaced_by "Tuition is due by tuition_due_day of the month" vs the next sentence "its due day is the day that charge posted plus tuition_due_day less one calendar days". For the first month's charge, which posts on the registration date (base: "the first month's tuition posts on the registration date"), e.g. posted 07-13 for billing month 08: the first gives the 5th of the month (08-05), the second 07-17 — different due days, so different lateness, payment-window days and fees. Not reached in tasks 0/1 (most recent charges post on the 1st); recorded charter-level.
- **C-P6 SOURCE-POLICY RED (C3 undeclared narrowing)** — base enroll_tuition_payments_and_refunds "Tuition is paid by the methods in accepted_payment_methods" (variant: online_card, ach_bank_draft, personal_check, money_order) vs P3/P7 "by online_card or ach_bank_draft", with `overwrite: []`; a family offering a check at the cashier for an advance payment or a first installment gets "accepted" from base and "refused" from the extended rule. No scored consequence in either task (personas choose ach_bank_draft / online_card).
- **C-P7 SOURCE-POLICY RED (check 6/7, D1)** — P3->P2 sentence "the late fee owed for every billing month whose tuition was left unpaid after its due day" is broader than its condition ("For the most recent billing month ...") and than its resolver: P2 "The late fee is assessed on the enrollment's most recent tuition charge". In a world where an earlier month was paid after its due day and carries no late fee row, the sentence keeps the advance payment unfixed and no write of this difficulty can satisfy it. Not engaged in task 0 (October, the only earlier late month, carries its row).
- **C-P8 SOURCE-POLICY RED (B7/E1 ledger closure of P7)** — "the first installment is one of them plus the plan fee" and "... has moved_reduction / plan_new_family / plan_tenure_five taken off the first installment": the enroll charter has no plan-fee event and P7 books no credit for the reductions, so the single payment row both pays a fee that was never charged and is reduced by amounts that are never credited; the ledger's open balance after the installment no longer equals the installments still due. Demonstrated in task 1.
- **C-P9 SOURCE-POLICY RED (P3 vs P1, advance does not settle the months)** — P1 owes "a combined-program credit against each billing month's Pre-K tuition charge", while P3 prices every unposted month at "that charge less the credits against it" (the most recent month's net) and says the months "post on their usual dates and are paid from it". The months then post at monthly_tuition and receive their own P1 credits, so the advance payment cannot equal what those months net to whenever the most recent month's credit is month-specific. Demonstrated in task 0.
- **C-P10 SOURCE-POLICY RED (A3 defining sentence in the baseline used by one factor)** — P2 baseline "its due day is the day that charge posted plus tuition_due_day less one calendar days" is used only by `cw_days` (payment_window_reduction); P5 baseline "... and on the tuition charged for the enrollment's most recent billing month" is used only by `rs_charge` (credited_share_reversal). Tasks 0 (P2) and 1 (P5).
- **C-P11 SOURCE-POLICY RED (A4 shared selections stated twice)** — P2 states the count of the enrollment's late fees in the school year twice, for repeat_lateness_schedule ("already carries two or more late fees in the school year") and subsidy_hardship_waiver ("carries no earlier late fee in the school year"), with two bindings (`lateness_count`, `hs_earlier`); P7 recomputes the open balance three times (`plan_balance`, `pl_balance`, `dp_balance`); P3 `months_ahead`/`of_months`. No value consequence on the tasks.
- **C-P12 SOURCE-POLICY RED (B2 no tie rule)** — "the enrollment's most recent payment" (P2), "most recent late fee" (P5/P6/P7), "most recent tuition charge" (P1–P5) state no same-day tie rule; `LATEST` keeps the first row met on equal dates. Not reached in either task (no same-day rows).

Observations (no RED): O-1 recurring discounts/waivers booked under credit_reason billing_correction (enum has no better value); O-2 meal_notices.balance_at_notice is null on task 1's benefit notices where db_schema says "0.00 on benefit notices" (row residue not read by any formula); O-3 intra-call ordering words in docstrings ("before booking"); O-4/O-5/O-6/O-7 borderline-realism keeps noted in the table.

## closing_checklist
Written after both reveals (2026-10-24T18:46:15); the charter-global section above was frozen before any reveal and is unchanged.
- Per-task files 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json; this is revision_1 (no older revision). Neither comparison section carries a PASS: task 0 RED (SOURCE-POLICY, SOURCE-CHAIN, SOURCE-FACTOR, SOURCE-TASK), task 1 RED (SOURCE-POLICY, SOURCE-FACTOR, SOURCE-TASK).
- Coverage and scopes: the 7 extended policies are fully covered; task 0 = {P1, P2, P3}, task 1 = {P4, P5, P6, P7}, pairwise disjoint over whole trees; each task tool is used by exactly one task; uuid8s independent — holds.
- Problem trees: task 0 has 2 prerequisite problems / 2 value_input edges, task 1 has 3 / 3; each has one owner=user write accepted under owner_ruling (b); the difficulty-wide graph is acyclic — holds (task 0 proof field T0-6 aside).
- Factors: fails — 23 struck factors or tiers (C-F1), every policy below 4 surviving factors (C-F2), gated factors (C-F3), unreachable tier (C-F4); task 0's seeded October late fee off-schedule (T0-3).
- Unique solution: fails in both tasks (T0-1, T0-2, T1-1, T1-2).
- Instantiation gates: not re-run by this auditor (Step 0: cited from the coordinator snapshot, all 7 OK on hashes 19a56d19f365c70e / 0ec8c84ea220751e). The difficulty does not close in revision_1.

VERDICT revision_1: task0=RED task1=RED charter=C-F1,C-F2,C-F3,C-F4,C-P1,C-P2,C-P3,C-P4,C-P5,C-P6,C-P7,C-P8,C-P9,C-P10,C-P11,C-P12

## revision_2

### charter_global_frozen (revision_2)
- Re-audit requested by the coordinator (round 2). Entry: `worklog.md` last non-empty line is `REWORK round 2: gates 7/7 green`; snapshot /tmp/erl0078_coord/snap_transfers_and_enrollment_changes_r2.txt (run by this auditor, execute-only) shows all 7 gates OK; hashes enroll.extended.yaml e97271d66410b4cd (changed from 19a56d19f365c70e), task_tools.py 0ec8c84ea220751e (unchanged), views r2/0.view.json 6a96b06a3248fe30, r2/1.view.json daf925190f5e7cdf.
- Because the extended charter changed, every charter-global section is re-derived below from the charter, the schema and the tool contracts alone (tools unchanged: action_binding_and_uuids carried forward by hash). New coordinator ruling audits/render_source/realism_bar.md read in full and applied (R1–R5 / X1–X4); XF_recipe.md and owner_ruling.md unchanged (same size and date).
- Masked and unread while this section and both r2 task derivations were written: tasks/0.json, tasks/1.json (all GT fields), plan.md, and the "REWORK round 2 claims" section of worklog.md (only its last line was read, by the coordinator's command). The revision_1 text above is untouched.

### policy_conflict_scan (r2)
Same seven policies, same tools and owners, same subjects; base section still verbatim (diff against products/enroll.yaml: identical). Prerequisite graph unchanged in shape: P3 <- {P2, P1}; P7 <- P6 <- P5 <- P4, all value_input/action. Cross-category reads: P1/P3 care (seat, plan half_month_start_day, care_ledger tuition/remittance rows), P4/P5/P6/P7 meals. No tool writes another category (D4 holds). P1 and P2 still commute (P2's only credit-sensitive read is the scope threshold, the open balance; P1 reads no late fee).

### rule_compute_equivalence (r2)
Sweep (sweep.py): every compute_basis quote, baseline sentence, prerequisite sentence and replaced_by is verbatim in its rule; compute and basis keys correspond. Hand check of ladders vs compute: consistent except the A9 members listed in C-P14 below. LATEST reads now select by billing_month (unique per enrollment per month), so the r1 tie-rule gap is gone. P2 now states one due day ("day tuition_due_day of that billing month") and its handling time ("on the records as they stand on the day the fee is assessed").

### action_binding_and_uuids (r2)
task_tools.py unchanged (0ec8c84ea220751e): revision_1's section carried forward by hash.

### prerequisite_graph / prerequisite_sentences (r2)
- P3->P2 sentence now "The advance payment is not fixed until the late fee owed for the enrollment's most recent billing month, when that month's tuition was left unpaid after its due day, has been assessed." — matches its condition and its resolver's scope (P2 assesses the most recent billing month). C-P7 closed.
- Other four sentences unchanged; connectives, business wording, no tool/id tokens, fallbacks valid (each resolver can owe exactly 0.00 and the tools refuse 0.00). gates ap_open / ap_open / share_part / waiver_base / pl_open are real bindings. Acyclic.

### override_declarations (r2)
- P2 overwrite of the base late-fee sentence: declared; replaced_by restates due day, oldest-first, one fee per billing month, assessment day and amount source.
- P3 and P7 now both declare the overwrite of base "Tuition is paid by the methods in accepted_payment_methods ...": identical replaced_by naming both cases (advance payment, first installment) and restating the in-force content for every other payment ("every other tuition payment may still be made by personal_check or money_order at the campus cashier") — C1/C2 satisfied. C-P6 closed.
- P4 overwrite: declared, restates the move, the full credit of later months, the owed earlier months and the basis-month carve-out.
- P1, P5, P6: overwrite [] — sentence-by-sentence, no base sentence is contradicted (base silent on bundle credits, late-fee reversals and late-fee waivers).
- P7 R2 "the plan neither charges a fee nor changes the balance, so the installments together equal the open balance" — the r1 ledger-closure defect is gone (C-P8 closed). P3 R2 "any credit one of those months later receives stays on the account as a credit balance, refunded under the refund rule" — the r1 settlement conflict with P1 is now resolved by rule (C-P9 closed).

### factor_ladders (r2) — realism_bar.md applied
| policy | factor | label | verdict | realism_bar ground |
|---|---|---|---|---|
| P2 | repeat_lateness_schedule | parameter | keep | R1 (published late-fee amount keyed on prior late fees this year: 25/30/35) |
| P2 | days_past_due_schedule | parameter | keep | R2 (fee amount keyed on days past the due date) |
| P2 | paper_payment_schedule | parameter | STRIKE | X1 — a late-fee add-on for having paid earlier months by check/money order; R1's payment-method key prices the payment itself, not a later penalty |
| P2 | months_in_arrears_schedule | parameter | STRIKE | X2 — arrears depth is already priced by one late fee per unpaid month and by the repeat schedule; a third delinquency add-on stacks the same dimension |
| P2 | late_fee_scope_rule | method | keep | R5 (minimum threshold) |
| P2 | yearly_late_fee_cap | parameter | keep on realism | R5 (annual cap) — but see C-F5 (fall-through is not the baseline; two tiers select one method) |
| P1 | wraparound_funding_tier | parameter | keep | R1 (bundle credit keyed on plan/funding) |
| P1 | care_month_proration | parameter | keep | R3 (half-month convention of the care plan itself) |
| P1 | combined_tuition_cap | method | keep on realism | R5 (household cap) — but see C-F5 |
| P1 | creek_kids_children_tier | parameter | STRIKE | X1/X2 — R1 admits "number of children of the household enrolled in THIS program"; this keys a Pre-K credit on another program's child count, which that program already prices by sibling position |
| P1 | wraparound_registration_lead | parameter | STRIKE | X1 — a recurring monthly add-on to a Pre-K credit for having registered early for another program |
| P3 | pay_in_full_offer | method | keep | R1 (pay-in-full discount keyed on months prepaid) |
| P3 | offer_timing_window | parameter | keep on realism | R2 — but fails A7/T2 (C-F3) |
| P3 | arrears_offer_reduction | parameter | STRIKE | X1 — graded cash cut of a prepay offer by months of arrears |
| P3 | creek_kids_household_reduction | parameter | STRIKE | X1 — cash cut of a tuition prepayment by the number of children another program bills |
| P4 | basis_month_convention | method | keep | R3 (half-month vs daily proration selected by a recorded attribute; O-r2-1: keying the convention on the status source is unusual) |
| P4 | basis_arrears_tier | parameter | STRIKE | X1 — uplift of a tuition credit for being further in arrears |
| P4 | basis_paper_tier | parameter | STRIKE | X1 — uplift for having paid by check |
| P4 | basis_move_lead | parameter | STRIKE | X1 — uplift for an earlier basis date; the date already sets the proration (also X2) |
| P5 | credited_share_reversal | method | keep | R3-type proportional correction of a fee on credited tuition |
| P5 | fee_status_timing | parameter | STRIKE | X2 — second timing on the status effective date, which already sets the credited share through P4's proration |
| P5 | reversal_paper_tier | parameter | STRIKE | X1 |
| P5 | reversal_arrears_tier | parameter | STRIKE | X1 |
| P6 | standing_part_rule | method | keep | mechanics of the part still standing |
| P6 | meal_status_sliding_scale | parameter | STRIKE | X1 names it: "Hardship shares or percentage cuts on penalty fees" (50 %/100 % of a late fee by meal status) |
| P6 | waiver_paper_tier | parameter | STRIKE | X1 |
| P6 | waiver_arrears_tier | parameter | STRIKE | X1 |
| P7 | plan_length_schedule | parameter | keep | R5 (installment thresholds) |
| P7 | down_payment_terms | method | keep | R5 (published plan terms) |
| P7 | meal_status_extra_installment | parameter | keep on realism | R1 (plan terms keyed on meal status) — but see C-P15 ("may") |
| P7 | arrears_down_addition | parameter | STRIKE | X2 — delinquency already sets the down payment through down_payment_terms |
| P7 | paper_down_addition | parameter | STRIKE | X1 |
| P7 | payment_gap_down_addition | parameter | STRIKE | X2 — a third delinquency add-on to the same down payment |

18 of 33 struck. Surviving on realism: P2 4, P1 3, P3 2, P4 1, P5 1, P6 1, P7 3; after XF A1–A10 (C-F3, C-F5): P2 1 (scope rule), P1 2, P3 1, P4 1, P5 1, P6 1, P7 3. Every policy is below the 4-factor floor.

### findings (r2, charter-global)
Status of revision_1 charter REDs (verified against the r2 charter):
- C-F1 realism — **still RED** in a new form (18 struck, table above).
- C-F2 floor — **still RED** (every policy below 4 passing factors).
- C-F3 gating (A1/A7/A10) — **still RED**, new members: P2 `selected_fee: "0.0 if scope_choice == 0 else (combined_fee if scope_choice == 1 else P('tuition_late_fee'))"` — with late_fee_scope_rule at its baseline ('2') repeat_lateness_schedule, days_past_due_schedule, paper_payment_schedule and months_in_arrears_schedule can never move the result (T2 fails for 4); P3 `net_offer: "MX(0.0, offer_amount * offer_share - arrears_cut)"` — with pay_in_full_offer at baseline (0.0) offer_timing_window and arrears_offer_reduction are inert (T2 fails for 2); P6 `waiver_base * waive_pct / 100` — a base x rate split whose rate is 0 at baseline (A7 "never split one charge into two multiplying factors"). The r1 members in P4/P5 are gone (their gates are now plain meal-status/credit scope sentences).
- C-F4 unreachable advance-rate tier — **closed** (factor removed).
- C-P1 A2 assembly — **still RED, one member**: P3 "then multipliers and reductions act on the offer, never taking it below zero, then the offer and the remaining reductions are taken off" names the pay_in_full_offer quantity. The other six order sentences are now generic. 
- C-P2 "continuing family" — **closed** (no tenure/continuing wording remains).
- C-P3 framing clauses — **closed** (no AutoPay, "waited", "while being determined" wording remains).
- C-P4 late-fee handling time — **closed** (assessment day stated).
- C-P5 two due-day sentences — **closed** as a contradiction, replaced by C-P13 below.
- C-P6 method narrowing — **closed** (declared overwrites, C1/C2 satisfied).
- C-P7 prerequisite sentence scope — **closed**.
- C-P8 plan ledger closure — **closed** (P7 R2).
- C-P9 advance vs P1 credits — **closed** (P3 R2).
- C-P10 A3 baseline sentences — **closed** (baselines now "The late fee is the type's tuition_late_fee." / "The reversal is 0.00.").
- C-P11 A4 duplicate selections — **closed** (each rule states each selection once).
- C-P12 B2 tie rule — **closed** (selections by billing_month).

New in revision_2:
- **C-F5 SOURCE-FACTOR RED (fall-through is not the baseline / two tiers one method)** — P1 combined_tuition_cap: ladder fall-through "the excess over household_cap of the Pre-K charge plus the seat's Creek Kids Club tuition for the month" vs `baseline: cap_addition: '0.0'`; P2 yearly_late_fee_cap: fall-through `K('yearly_cap')` vs `baseline: cap_room: K('no_cap')` (99999), and its second tier "yearly_cap less those fees" applied to zero earlier fees is its third tier, so two tiers select one method. Tasks 0 (both computations).
- **C-P13 SOURCE-POLICY RED (B1, first-month due day)** — P2 "whose due day is day tuition_due_day of that billing month" with base "the first month's tuition posts on the registration date": a first month registered after the 5th (task 1's August charge posted 2026-08-20, due day 2026-08-05) is "unpaid after the due day" on the day it posts, so P2 owes a late fee for every such month however promptly the family pays. Task 1 (seed consequence).
- **C-P14 SOURCE-POLICY RED (A9 ladder/rule text vs compute)** — P1/P3 "billed by Creek Kids Club for three or more children" vs `XCOUNT('care','care_ledger', event_type='care_tuition_charge', billing_month=...)`, which counts tuition rows, not children (a mid-month plan change books two rows for one child); P4 "three or more whole months of arrears when the basis comes on file" vs `ba_months` computed on the ledger at NOW. No value consequence on either task world (one tuition row per child; no ledger rows between 2026-12-17 and 2027-01-04).
- **C-P15 SOURCE-POLICY RED (permissive "may" with no record)** — P7 R6 "A family whose child's meal account holds any Free Meal Status tier may spread the plan over free_extra more installments ..., one whose child holds any Reduced-Price Meal Status tier over reduced_extra more" while compute always adds them; whether the family takes the extra installments is a choice no record holds and the rule fixes no default. Demonstrated in task 1.
- **C-P16 SOURCE-POLICY RED (P5 R0 vs R1)** — R0 "the late fee posted for that billing month" (the most recent billing month) vs R1 "the late fee of the enrollment's most recent billing month that carries a late fee" (`rv_fee` by the latest late-fee billing month): when the most recent billing month carries no late fee but an earlier month does, R0 reverses nothing and R1 reverses the earlier fee. Not engaged in task 1 (December carries both).

Observations (r2): O-r2-1 P4 keys its proration convention on the status source; O-r2-2 P1's "household combined-tuition cap" counts only the Pre-K child's seat although the rule names the household (the defining clause makes the reading unique); O-1, O-3 carried.

### closing_checklist (r2)
Written after the r2 reveals (2026-10-24T20:47:31); the r2 charter-global section above was frozen before them.
- Files: 0.md and 1.md each carry revision_1 and revision_2; revision_1 text untouched.
- Coverage/scopes: 7 policies covered, task scopes {P1,P2,P3} / {P4,P5,P6,P7} disjoint; tools and uuid8s unchanged — holds.
- Trees: both hold (task 0 n=2, task 1 n=3, all value_input, owner=user roots, acyclic); T0-6 closed — holds.
- Factors: fails (C-F1, C-F2, C-F3, C-F5; task 1 B4 half-cent baseline and the missing August late fee).
- Unique solution: task 0 holds; task 1 fails (C-P15 "may").
- Final sweep of every class raised in either revision across all 7 policies: realism X1/X2 (18 members, table), floor (all 7), A1/A7 gating (P2, P3, P6), A2 (P3), fall-through vs baseline (P1 cap, P2 cap), A9 (P1/P3 child count, P4 arrears date), B1 first-month due day (P2), B2/B4 (no charter member; task 1 baseline figure), B8 framing (none left), C1–C3 overwrites (clean), A3/A4 (clean), check 6/7 sentences (clean), D1–D4 (clean), E1 (task 1 August fee), permissive rule wording (P7), P5 R0/R1 month selection. No further members found.
- Gates not re-run by this auditor beyond the coordinator's snapshot script (all 7 OK). The difficulty does not close in revision_2.

VERDICT revision_2: task0=RED task1=RED charter=C-F1,C-F2,C-F3,C-F5,C-P1,C-P13,C-P14,C-P15,C-P16

## revision_3

### charter_global_frozen (revision_3)
- Round-3 re-audit. Entry: worklog last non-empty line `REWORK round 3: gates 7/7 green`; snapshot /tmp/erl0078_coord/snap_transfers_and_enrollment_changes_r3.txt (run by this auditor, execute-only): 7/7 OK; hashes enroll.extended.yaml 4aadc757d14261a9 (changed), task_tools.py 6887dd1cea40bba8 (changed: the waiver tool's docstring/receipt now name the eligibility-transition waiver; signatures, owners, format checks and effects unchanged), views r3/0 8a8f4bad5c49fa9b, r3/1 fde8af67ffa6dc03.
- Read before this section: realism_bar.md in full incl. AMENDMENT 1 (R6); worklog "REWORK round 3 — working notes" (R-tag table, record keys, why-no-R1–R5) and "REWORK round 3 claims" (item ids; no scored figure in either). Masked until both r3 task derivations are frozen: tasks/0.json, tasks/1.json.
- All charter-global sections re-derived (charter and tools changed). Base section verbatim (diff clean). Sweep: every compute_basis quote, baseline sentence, prerequisite sentence and replaced_by verbatim in its rule; no tenure/AutoPay/continuing/hardship wording left.

### structure (r3)
- P6 is renamed enroll_ext_late_fee_transition_waiver (target tool unchanged); P7's prerequisite points at the new id; graph P3 <- {P2, P1}, P7 <- P6 <- P5 <- P4, acyclic, all value_input/action with valid zero-amount fallbacks; sentences pass the four-point test; conditions match sentences (P7's sentence and condition now both name "the late fee of the enrollment's most recent billing month").
- Overwrites: P2 (late-fee sentence; due day now "day tuition_due_day of the billing month or, for a month whose tuition charge posts after that day, tuition_due_day days after the charge posts"), P3/P7 (shared payment-method overwrite, C1/C2 hold), P4 (move/credit sentence). P1, P5, P6 contradict no base sentence.
- Tools: uuid8s unchanged; bodies check formats only; waiver receipt text matches its docstring (B6).

### factor_ladders (r3) — realism_bar R1–R6 / X1–X4
| policy | factor | tag (reworker) | audit verdict |
|---|---|---|---|
| P2 | repeat_lateness_schedule | R1 | pass |
| P2 | days_past_due_schedule | R2 | **RED — X1 "desk-posting-delay add-on" (AMENDMENT 1 cond. 4)**: the add-on is keyed on "when the fee is assessed more than days_far calendar days after the due day", and R0/R8 set only an earliest assessment day; one unpaid month yields 25 + 0 / +10 / +20 depending on the day the desk posts the single fee |
| P2 | paper_payment_schedule | R6 [payment_method] | R6-WAIVED (BLUEPRINT-KNOWN) |
| P2 | unpaid_month_method | R6 [unpaid part of the month] | **RED — R6 cond. 2 ("no odd fractions of other prices") and cond. 5 / X2 ("a percentage stack on a flat service fee")**: adds unpaid_pct percent of the month's tuition charge to the flat tuition_late_fee, giving late fees in odd cents (seeded 39.94, 54.94, 49.94) |
| P2 | yearly_late_fee_cap | R5 | pass (fall-through "no earlier late fee -> not limited" = baseline no_cap; middle tier restricted to earlier fees above zero) |
| P1 | wraparound_funding_tier | R1 | pass |
| P1 | care_month_proration | R3 | pass |
| P1 | combined_tuition_cap | R5 | pass (fall-through "nothing is added" = baseline) |
| P1 | creek_kids_children_tier | R6 [active care_enrollments count] | R6-WAIVED |
| P1 | wraparound_registration_lead | R6 [registration_date -> start_date] | R6-WAIVED |
| P1 | account_standing_reduction | R6 [whole months of arrears] | R6-WAIVED |
| P3 | pay_in_full_offer | R1 | pass (baseline = standard discount = fall-through) |
| P3 | offer_timing_window | R2 | pass (keyed on the day the family pays; acts on the non-zero standard discount) |
| P3 | arrears_offer_reduction | R6 [arrears months] | R6-WAIVED |
| P3 | creek_kids_household_reduction | R6 [active care_enrollments count] | R6-WAIVED |
| P4 | basis_month_convention | R3 | pass (O-r2-1) |
| P4 | basis_arrears_tier / basis_paper_tier / household_size_tier | R6 | R6-WAIVED (credit limited to the charge; keys recorded; one factor per key) |
| P5 | credited_share_reversal | R3-type | pass |
| P5 | reversal_paper_tier / reversal_arrears_tier / reversal_household_tier | R6 | R6-WAIVED (no status or income test; limited to the fee) |
| P6 | standing_part_rule | mechanics | pass (fall-through = baseline whole fee; binds as the limit) |
| P6 | courtesy_waiver_schedule / waiver_paper_tier / waiver_household_tier | R6 | R6-WAIVED (no meal-status share; flat amounts; limited to the standing part) |
| P7 | plan_length_schedule / down_payment_terms | R5 | pass |
| P7 | meal_status_extra_installment | R1 | pass ("has the plan spread over", no family choice) |
| P7 | closing_account_down / paper_down_addition / household_size_installments | R6 | R6-WAIVED |
R6 minimality (cond. 6) holds per computation as listed in the working notes (P1 3 of 6, P2 2 of 5, P3 2 of 4, P4–P6 3 of 4, P7 3 of 6). After the two P2 REDs, P2 carries repeat, cap and one R6 factor: below the drawn count, and with no method factor left.
XF on the remaining factors: A1 no factor reads another's binding; A2 order sentences generic (P3 names only the baseline's "discount"); A6 all method pairs differ by an input or operation; A7 no base x rate split, no gate on a factor output, P2/P6 limits bind with every other factor still moving on the task worlds; A9 child counts read active enrollments/accounts (one per student by the base charters), P4/P5 arrears "on the day the credit/reversal is posted"; B1 first-month due day fixed; B2 selections by billing_month and status filters; fall-through = baseline for every factor.

### findings (r3, charter-global)
Round-2 REDs: C-F1 — partly closed (all X1/X2 members raised in r2 removed; new members below); C-F2 — still RED for P2 only (see C-F7); C-F3 closed; C-F5 closed; C-P1 closed; C-P13 closed (task 1's August charge is due 08-25, paid 08-21); C-P14 closed; C-P15 closed; C-P16 closed (P5 R0/R1 and P6 read the late fee of the most recent billing month). Revision_1 items stay closed.
- **C-F6 SOURCE-FACTOR RED** — P2 unpaid_month_method: R6 conditions 2 and 5 fail (rule R6 "a month whose whole tuition charge is still unpaid adds unpaid_pct percent of that tuition charge"); a percentage of another price stacked on the flat tuition_late_fee. Bears on task 0 (scored late fee) and on both seeds (odd-cent late fees).
- **C-F7 SOURCE-FACTOR RED** — P2 days_past_due_schedule: X1 desk-posting-delay add-on (AMENDMENT 1 cond. 4) as tabled; with C-F6, P2 is left with fewer factors than its drawn count and no method factor (C-F2 member). Relation to earlier revisions: revision_2 passed this factor as R2; it is raised now because AMENDMENT 1 names the desk-posting-delay add-on as an X1 mechanism. It is not a regression by the reworker. Bears on task 0.

Observations (r3): R6-WAIVED (BLUEPRINT-KNOWN) — the 18 R6 factors tabled above that meet all six conditions; O-r2-1 kept; O-1, O-3 carried; O-2 closed (balance_at_notice 0.00); the R6 list (tag, key, why) sits in the working-notes section the claims cite rather than in the claims section itself.

### closing_checklist (r3)
Written after the r3 reveals (2026-10-24T22:05:42); the r3 charter-global section was frozen before them.
- Files: 0.md and 1.md carry revisions 1–3; earlier text untouched.
- Coverage/scopes: 7 policies, scopes {P1,P2,P3} / {P4,P5,P6,P7}, disjoint; tools' uuid8s unchanged — holds.
- Trees: both hold (n = 2 / 3, all value_input, owner=user roots under owner_ruling (b), acyclic); closure figures true — holds.
- Factors: task 1 holds; task 0 fails on P2 only (C-F6, C-F7).
- Unique solution: holds in both tasks.
- Final sweep of every class raised in any revision across all 7 policies: X1 named mechanisms (tenure, continuing family, AutoPay, cohort, awaiting-determination, hardship share, desk-posting-delay) — one member: P2 days_past_due_schedule. X2 percentage stack and R6 cond. 2 — one member: P2 unpaid_month_method. Floor/method count — P2. The following classes are clean:
  - A1/A7 gating and base × rate splits.
  - A2, A3, A4, A6, A9.
  - Fall-through vs baseline.
  - B1 (first-month due day), B2, B4 (no half-cent figure), B5, B6, B8.
  - C1–C3 overwrites.
  - Check 6/7 sentences and conditions; D1–D4.
  - E1 seeds (consistent with the r3 charter).
  - Permissive "may"; P5/P6 month selection; plan ledger closure; advance/credit settlement.
- Gates: the coordinator's snapshot script, run once by this auditor, shows 7/7 OK. The difficulty closes only when C-F6 and C-F7 are resolved (and task 1's late-fee seed is recomputed with them, O-T1-r3).

VERDICT revision_3: task0=RED task1=PASS charter=C-F6,C-F7

## revision_4

### charter_global_frozen (revision_4)
- Round-4 re-audit. Entry: worklog last non-empty line `REWORK round 4: gates 7/7 green`; snapshot /tmp/erl0078_coord/snap_transfers_and_enrollment_changes_r4.txt (run by this auditor, execute-only): 7/7 OK; enroll.extended.yaml 5ae577e1e967f562 (changed), task_tools.py 6887dd1cea40bba8 (unchanged since r3: tool sections carried by hash), views r4/0 cac4bff38199a375, r4/1 77632c3362340f09. realism_bar.md (incl. AMENDMENT 1), XF_recipe.md and owner_ruling.md unchanged since r3 (same size and date).
- Read before this section: worklog "REWORK round 4 — working notes" and "claims" (item ids, R6 list; no scored figure). Masked until both r4 task derivations are frozen: tasks/0.json, tasks/1.json.
- Scope of the change, checked: base section verbatim; P1 and P3–P7 carry the same params, factor ids, ladders and compute bindings as in r3 (extracted and compared), and the reworker states their rules are unchanged; only P2 changed. Sweep: all compute_basis quotes, baseline sentences, prerequisite sentences and replaced_by verbatim. P2 is re-derived in full below; the r3 conclusions for the other six policies are re-confirmed on the unchanged text.

### P2 enroll_ext_late_fee_assessment (r4)
- Rule: the overwrite and due-day sentences are the same as r3. Factors:
  - repeat_lateness_schedule (R1);
  - paper_payment_schedule (R6, payment_method);
  - unpaid_month_schedule (R6: flat unpaid_whole_add / unpaid_half_add by the unpaid part of the month);
  - yearly_late_fee_cap (R5, now labelled method: limit nothing / yearly_cap less earlier fees / not limited);
  - multi_program_household_cut (R6: flat cut by the count of the household's active care enrollments, after the limit).
- days_past_due_schedule and the percentage tier are gone. The order sentence is generic: "first replacements and additions, then the limit, then reductions, never taking the fee below zero".
- Compute matches every sentence; the R8 guard is a plain record test; the fall-through equals the baseline for all five factors. A6: the cap's tiers differ by an input and an operation, and its method label is honest (it chooses whether and how the limit applies). A7: one cap. The reduction after the limit moves the result whether or not the cap binds, and no base × rate split remains. A1: no factor reads another factor's binding. The cross_category declaration now includes care (care_enrollments.status).
- R6 grading:
  - paper_payment_schedule: conditions 1–6 hold → R6-WAIVED.
  - unpaid_month_schedule: recorded key; round 15/5; no percentage of another price; no other P2 factor on the unpaid dimension; not a named X1 → R6-WAIVED.
  - multi_program_household_cut: key listed in condition 1; round 5/10; flat; not a hardship or status test; one factor on the key in P2 → R6-WAIVED.
  - Minimality (condition 6): 5 drawn − 2 honest (repeat, cap) = 3 R6 slots; the "why no R1–R5" note is in the working notes.
- Class re-sweep, all 7 policies:
  - Desk-posting-delay add-ons: none left. P3's window is keyed on the family's payment day, P7's closing schedule on the plan day, P1's lead on care's registration and start dates.
  - Percentage of another price stacked on a flat fee: none. P3's discount acts on tuition months and P7's down payment on the balance.
  - All earlier classes (A1–A10, B1–B8, C1–C4, D1–D4, E1/E2, permissive wording, month selection, ledger closure) are clean on the unchanged policies, as concluded in r3.

### findings (r4, charter-global)
- C-F6 — **closed** (no percentage tier; flat amounts; seeded fees are in whole dollars).
- C-F7 — **closed** (days_past_due_schedule removed; no other member in the charter).
- C-F2 (P2 member) — **closed** (P2 at its drawn five, with a method factor; R6 equals drawn minus honest).
- No new charter-level defect found. Observations: R6-WAIVED (BLUEPRINT-KNOWN) — the 18 r3 R6 factors (unchanged) plus P2's three (paper_payment_schedule carried, unpaid_month_schedule, multi_program_household_cut); O-1, O-3, O-r2-1 carried.

### closing_checklist (r4)
Written after the r4 reveals (2026-10-24T22:56:51); the r4 charter-global section was frozen before them.
- Files: 0.md and 1.md carry revisions 1–4; earlier text is untouched; every r4 comparison section carries PASS.
- Coverage and scopes: 7 policies; scopes {P1, P2, P3} and {P4, P5, P6, P7}, disjoint; task tools closed; uuid8s independent and unchanged.
- Trees: task 0 has n = 2 and task 1 n = 3, all edges value_input; owner=user roots accepted under owner_ruling (b); the difficulty-wide graph is acyclic.
- Factors: every computation carries its drawn 4–6 factors, at least 2 parameter and 1 method. Each task has a multi-source factor (P1 cap; P4 convention) and a cross-difficulty factor (care; meals), with the other product's rows seeded and priced as their charters produce. Every factor bears weight against an honest baseline whose fall-back figure differs from gold. Every factor is honest R1–R5 or R6-WAIVED (BLUEPRINT-KNOWN), 21 R6 observations in all.
- Unique solution: holds in both tasks.
- Final sweep of every class raised in revisions 1–4 across all 7 policies:
  - Realism X1–X4, including desk-posting-delay add-ons and percentage stacks on flat fees: no member.
  - Floor and method counts: no member.
  - A1–A10 (gating, base × rate splits, assembly sentences, fall-through vs baseline, method shapes, ladder text vs compute): no member.
  - B1–B8 (first-month due day, tie rule, half cents, verbatim quotes, tool bodies, framing clauses): no member.
  - C1–C4 overwrites: no member.
  - Prerequisite sentences and conditions (check 6/7), D1–D4: no member.
  - E1/E2 seeds: no member.
  - Permissive wording, month selection, plan ledger closure, advance/credit settlement: no member.
- Gates: the coordinator's r4 snapshot (run once by this auditor) shows 7/7 OK on the final form (5ae577e1e967f562 / 6887dd1cea40bba8). check_traceability stays deferred to the KB stage, per the coordinator.
- The difficulty passes the source-layer audit in revision_4.

VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN

## revision_5

### charter_global (revision_5)
- Round-5 re-audit; items are the renderer's scan-first findings in audits/render_source/transfers_and_enrollment_changes/render_r1.md (F1–F7; it lists no O items), read in full.
- Entry: worklog last non-empty line `REWORK round 5: gates 7/7 green`. Snapshot /tmp/erl0078_coord/snap_transfers_and_enrollment_changes_r5.txt (run by this auditor, execute-only): 7/7 OK.
- Hashes: enroll.extended.yaml ad1a99cf5409c6f2 (changed); task_tools.py f452cff1522de765 (changed); views r5/0 cac4bff38199a375 and r5/1 77632c3362340f09 are byte-identical to r4 (task worlds unchanged).
- Rulings: realism_bar.md read in full, including AMENDMENT 2 (split prorations; meal forecast shape; component exclusions vs X3). None of the three bears on this charter: it has no split proration, no meal forecast and no component exclusion. XF_recipe.md and owner_ruling.md are unchanged.
- What changed, checked:
  - Base section verbatim.
  - Params, factor ids, ladders' tiers and tags are unchanged in all 7 policies.
  - Rule text changed in P2, P4, P5, P6 and P7.
  - Compute changed in two places: P2's guard now reads a plain `lf_unpaid`; P4 adds the `bc_later` / `scope_eff` month tests.
  - task_tools.py: only the reversal tool's docstring changed ("Post the reversal of all or part of ..."). Bodies, signatures, owners and uuid8s are unchanged, and every receipt still matches its docstring (B6).
- Sweep: all compute_basis quotes, baseline sentences, prerequisite sentences and replaced_by are verbatim in their rules.

### render findings F1–F7 (verified on the r5 charter)
| id | verdict | evidence |
|---|---|---|
| F1 (A10, P7 meal-status sentence named plan_length_schedule) | **closed** | R6 now reads "has the plan spread over free_extra more installments ..." and names no factor. R11 "then the number of installments is fixed as the sum of the installment counts" matches `installments: plan_count + extra_installments + hh_extra`. |
| F2 (A2/A10, P6 plain sentence named standing_part_rule) | **closed** | R0 ends "the waiver is never more than that late fee"; the part-still-standing limit is stated only in R2, the standing-part sentence. With that factor at baseline (`sp_fee`), R0's limit is the whole fee, so the computation document is consistent with R0. |
| F3 (A9/B1, P7 "pays that late fee") | **closed** | R5 and the ladder read "pays the amount of that late fee as posted, whatever credits stand against it", matching compute (gross late-fee SUM). |
| F4 (B7/A9, P4 status "source") | **closed** | R3 names the tiers per branch (Household Application, Reduced-Price and both Prior-Year Carryover → whole/half; Direct Certification and Categorical Eligibility → calendar days; any other → nothing), matching `credited_tuition`. R7 scope names Free/Reduced tiers, matching `added`. The carryover tiers now have one placement. |
| F5 (P5 "partly reversed") | **closed** | R0 now reads "reversed in whole or in part"; the tool docstring reads "Post the reversal of all or part of ..."; P6 R0 reads "all or part of the late fee". |
| F6 (A3/A4, P2 unpaid part defined only in a factor sentence) | **closed** | Plain R2 defines the open balance and "the part of the month's tuition still unpaid ... never less than zero". The guard `lf_unpaid` and the factor's `um_part` both implement it, and R6 (the factor sentence) now only states its tiers. |
| F7 (B1 month-end, P4 31-day offset) | **closed** | `bc_later` = MONTHS(first of the basis month, effective date) >= 1 → nothing credited, matching R3 "a tier that took effect in a month after the basis month ... has nothing credited". `added` applies the same month test, matching R7. Probes on the compute: basis month November, effective Dec 1 → 0.00; February, effective Mar 1 → 0.00; a carryover tier effective before the month → whole month; Direct Certification before the month → capped at month_days_convention (whole month). |

### regression and class sweep (r5)
- Every revision_4 conclusion is re-checked on the r5 text:
  - The factor tags, R6 grading (21 R6-WAIVED, BLUEPRINT-KNOWN) and counts are unchanged; every fall-through still equals its baseline.
  - A1: no factor reads another factor's binding.
  - A7: no gate on a factor output; P2 and P6 each have one limit.
  - The prerequisite sentences, conditions, fallbacks and overwrites (C1–C3) are unchanged.
- The render classes swept over all 7 policies:
  - A sentence naming another factor (F1/F2 class): no other member. The order sentences name only baseline quantities (tuition_late_fee, the standard credit, the standard discount, the standard waiver) or generic steps.
  - "Part" wording on an amount that can be whole (F5 class): P5 and P6 now say "in whole or in part" / "all or part"; no other member.
  - A defining sentence living only in a factor sentence (F6 class): no other member. The arrears count is defined inside each factor sentence that uses it, and no plain binding reads it.
  - A month-end offset test (F7 class): P1's care_month_proration already uses MONTHS for "a month after the billing month"; no other DAYS-offset month test remains.
  - "As posted" vs net of credits a prerequisite posts (F3 class): P5 compares the credits with "that charge" and reverses "the late fee posted for that billing month", which is unambiguous. P6 states its net explicitly. P3 R4/R5 price the unposted months "at the most recent billing month's tuition charge" while its prerequisite P1 posts a credit against that charge. R2 ("The months the advance covers post on their usual dates ... any credit one of those months later receives stays on the account as a credit balance"), together with the charter's usage of "credits standing against" a charge for the net, excludes the net reading. This is observation O-r5-1, not a RED.
- No new defect found.

### findings (r5)
- F1–F7: all closed (table above).
- Observations: O-r5-1 (P3 rate reading, excluded by R2), plus 21 R6-WAIVED (BLUEPRINT-KNOWN). O-1, O-3 and O-r2-1 are carried.

### closing_checklist (r5)
- Files 0.md and 1.md carry revisions 1–5; earlier text is untouched.
- Coverage, scopes, trees, factor floors and the unique solution hold as in revision_4. The r5 edits change no figure, count, tag or edge.
- Final sweep of every class raised in revisions 1–5 across all 7 policies found no member. That covers:
  - realism X1–X4 and R6 conditions 1–6;
  - A1–A10, B1–B8, C1–C4, D1–D4, E1/E2;
  - check 6/7 sentences and conditions;
  - permissive wording, month selection, ledger closure and advance settlement;
  - the render classes F1–F7.
- Gates: the r5 snapshot shows 7/7 OK on ad1a99cf5409c6f2 / f452cff1522de765. check_traceability stays deferred, per the coordinator.

VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

## revision_6

### charter_global (revision_6)
- Round-6 re-audit. This round's item is the renderer's render_r2.md (R2-F1; the file also confirms F1–F7 closed). I read it in full, together with RENDER.log.
- Entry: worklog last non-empty line `REWORK round 6: gates 7/7 green`. Snapshot /tmp/erl0078_coord/snap_transfers_and_enrollment_changes_r6.txt (run by this auditor, execute-only): 7/7 OK.
- Hashes: enroll.extended.yaml 12ecffa0d8cf2dc9 (changed); task_tools.py f452cff1522de765 (unchanged since r5); views r6/0 cac4bff38199a375 and r6/1 77632c3362340f09, byte-identical to r5. realism_bar.md, XF_recipe.md and owner_ruling.md are unchanged.
- Change checked:
  - Base section verbatim.
  - The sweep (verbatim quotes, baselines, prerequisite sentences, overwrites) is clean on all 7 policies.
  - Params, factors and ladders are the same as r5.
  - enroll_ext_eligibility_month_credit.baseline.params is now [].

### R2-F1 and its class (baseline.params vs the baseline paragraph)
- R2-F1 — **closed**. P4's baseline.params no longer lists month_days_convention, a key only basis_month_convention's calendar-day tier reads. The baseline paragraph "The basis-month credit is 0.00, the basis month remaining owed." names no key.
- Class sweep over all 7 policies. The instantiation contract (erl-task-instantiate, `baseline`) says params are "the quantitative keys ... whose home is that paragraph". The policy-audit skill's incoherent-baseline test says "its default keys are not the ones baseline.params names".

| policy | baseline.params | keys the baseline paragraph names | verdict |
|---|---|---|---|
| P1 | credit_standard | credit_standard | match |
| P2 | tuition_late_fee, tuition_due_day | tuition_late_fee | tuition_due_day is a type parameter whose home is the plain due-day sentence and guard (R1, R9), not a factor. Observation O-r6-1 |
| P3 | school_year_billing_months | offer_pct | **RED**: offer_pct (the standard discount, "less the standard discount of offer_pct percent of those months at that charge") is a default key of the baseline paragraph and is not listed. school_year_billing_months lives in plain R3, used by the plain `ap_months` (O-r6-1) |
| P4 | [] | none | match (R2-F1 closed) |
| P5 | [] | none | match |
| P6 | [] | waiver_standard | **RED**: the baseline paragraph "The waiver is waiver_standard." states its default key, and baseline.params is empty |
| P7 | plan_installments_standard | plan_installments_standard | match |

- Relation to earlier revisions: R2-F1 (P4) and the P3/P6 members existed in revisions 3–5 (P6's baseline since r3; P3's standard discount since r3). The earlier revisions of this audit did not check baseline.params against the paragraph. They are missed members, not regressions by the reworker.

### findings (r6)
- R2-F1 — closed.
- **C-F8 SOURCE-FACTOR RED (incoherent baseline: default keys ≠ baseline.params)**. Members:
  - P3 enroll_ext_advance_payment: baseline paragraph names offer_pct; baseline.params = [school_year_billing_months].
  - P6 enroll_ext_late_fee_transition_waiver: baseline paragraph names waiver_standard; baseline.params = [].
  - Consequence: the render gate checks the computation document against baseline.params only. A computation document that omits the standard discount's 3 % or the standard waiver's figure passes, and the reader then has no definite fall-back number. The baseline would not be self-sufficient in the KB.
  - Bears on task 0 (P3) and task 1 (P6).
- No other new defect. Every revision_5 conclusion is re-confirmed on the unchanged rule and compute text: render F1–F7, realism tags (21 R6-WAIVED), A1–A10, B1–B8, C1–C4, D1–D4, E1/E2, check 6/7. O-r5-1 is carried.
- GT equality check (read after the sections above): every task's expected and baseline_result figures are unchanged from r4/r5.

### closing_checklist (r6)
- Not closed: C-F8 (P3 and P6 baseline.params). Every other item holds as in revision_5.
- Gates: the r6 snapshot shows 7/7 OK. check_traceability is not run.

VERDICT revision_6: task0=RED task1=RED charter=C-F8

## revision_7

### charter_global (revision_7)
- Round-7 re-audit.
- Entry: worklog last non-empty line `REWORK round 7: gates 7/7 green`. Snapshot /tmp/erl0078_coord/snap_transfers_and_enrollment_changes_r7.txt (run by this auditor, execute-only): 7/7 OK.
- Hashes: enroll.extended.yaml 0c3feb33baacf692 (changed); task_tools.py f452cff1522de765 (unchanged); views r7/0 cac4bff38199a375 and r7/1 77632c3362340f09, byte-identical to r4–r6. Rulings unchanged.
- Claims read: worklog "REWORK round 7 — working notes" and "claims" (item ids; no scored figure).
- Change checked:
  - Base section verbatim.
  - Sweep clean on all 7 policies: compute_basis quotes, baseline sentences, prerequisite sentences and replaced_by are verbatim.
  - Factor ids and compute bindings are the same as r6. Every expected, baseline_result and factor_sensitivity figure in the task files equals the r4–r6 figures.
  - Only baseline.params lines changed.

### baseline.params two-way sweep (all 7 policies)
| policy | baseline.params | keys the baseline paragraph names | result |
|---|---|---|---|
| P1 | credit_standard | credit_standard | match |
| P2 | tuition_late_fee | tuition_late_fee | match (tuition_due_day dropped; it lives in the plain due-day sentence and guard) |
| P3 | offer_pct | offer_pct | match (school_year_billing_months dropped; it lives in plain R3) |
| P4 | [] | none | match |
| P5 | [] | none | match |
| P6 | waiver_standard | waiver_standard | match |
| P7 | plan_installments_standard | plan_installments_standard | match |
No factor-only key is listed (R2-F1 class), and no key the paragraph names is missing (C-F8 class).

### findings (r7)
- C-F8 — **closed** (P3 [offer_pct]; P6 [waiver_standard]).
- O-r6-1 — closed.
- R2-F1 — remains closed.
- Regression and class sweep: every class raised in revisions 1–7 is re-checked on the r7 text, and no member was found:
  - realism X1–X4 and R6 conditions 1–6 (21 R6-WAIVED, BLUEPRINT-KNOWN);
  - floors and method counts;
  - A1–A10;
  - B1–B8;
  - C1–C4;
  - D1–D4;
  - E1/E2;
  - check 6/7 sentences and conditions;
  - render F1–F7, R2-F1 and C-F8.
- Observation O-r7-1: the P3 and P7 baseline paragraphs use "the open balance" and "every month not yet posted". Those terms are defined in plain non-factor sentences (P3 R3, P7 R2), not in the paragraph itself, and the render contract places such plain sentences in the computation document (as render_r1 F2/F6 apply). So the computation document is self-sufficient. This is not a RED. O-r5-1 is carried.

### closing_checklist (r7)
- Every item of the revision_4/5 checklist holds on the r7 form, and C-F8 is closed.
- Gates: the r7 snapshot shows 7/7 OK on 0c3feb33baacf692 / f452cff1522de765. check_traceability is deferred, per the coordinator.
- The difficulty passes the source-layer audit.

VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN

## revision_8 (seed-only round: KB audit S1/S2)
- Entry: worklog last non-empty line `REWORK round 8: gates 7/7 green`. Snapshot /tmp/erl0078_coord/snap_transfers_and_enrollment_changes_r8.txt (run by this auditor): 7/7 OK.
- Charter and tools are byte-identical: enroll.extended.yaml 0c3feb33baacf692 and task_tools.py f452cff1522de765, the same as r7. Every charter-global section is therefore carried forward from revision_7 by hash.
- Views: r8/1 is 77632c3362340f09, unchanged. r8/0 is 5b1a55d87c61395e, changed. Against r7 its only differences are two new rows (frozen_time and persona unchanged):
  - **S1:** care_ledger d10e6156, a care_payment of 192.00 by ACH on 2026-12-10 against Lucia's Pre-K Wraparound seat.
  - **S2:** enrollments eb988618, Mateo's 2026-27 Attendance Zone Enrollment at Alder Springs Elementary, grade 03, enrolled.
- Check against the published docs:
  - docs/care due_dates_late_fees_and_suspension says tuition is "due by the tuition due day of that month", and the figures table gives day 10. Lucia's December charge posted 2026-12-09 (on seat confirmation, per monthly_tuition_posting_and_rate_basis "The first month's tuition ... posts on the day the seat is confirmed") and is now paid in full on its due day, so no care late payment fee is owed at the opening (S1 closed).
  - docs/care registration_admission_and_waitlist says registration "is open to a student whose current district enrollment record is in status enrolled at a campus in the plan's offered campuses". Mateo's new record matches the docs/enroll registration/residency rules: zoned campus Alder Springs, grade 03 for a 2018-06-11 date of birth, residency verified 2026-07-20 within 30 days of the 2026-07-13 registration. It is enrolled before his 2026-07-20 Creek Kids Club registration and agrees with the persona ("a third grader at Alder Springs") (S2 closed).
  - Accepted residue, not read by any gold step: Mateo's meal account and the registration-document rows.
- Scored reads: no compute of this difficulty reads care_payment rows or a second enrollment record. P1 reads the seat's tuition charges and remittances and its rate basis; P2 and P3 count active care_enrollments, which are unchanged; every enroll aggregate is scoped to the target holding. Gold's find_enrollments(customer_id) now returns two records, and the persona names Lucia's Pre-K tuition, so the object stays unique.
- GT check: every expected, baseline_result and factor_sensitivity figure of both tasks equals the r4–r7 figures, and so my revision_4 derivation. No scored figure moved.
- No regression: every revision_7 conclusion holds on the unchanged charter, and the class sweep is not reopened by a seed-only change.

VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN
