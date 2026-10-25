# Policy-task audit — garden_cancellations_and_termination_fees / charter-global

## revision_1

## charter_global_frozen
- Frozen 2026-10-25T09:20Z, before any task GT was revealed. Auditor: independent erl-task-policy-audit run (not the instantiator).
- Freeze hashes (sha256, match the coordinator snapshot `/tmp/erl0082_coord/snaps/garden_cancellations_and_termination_fees.r1.txt`):
  - `tasks/garden_cancellations_and_termination_fees/garden.extended.yaml` 0fe77a8c7b696b7d9b3e1df657d3ad48999540099fee2fb0d7862d30b66a8da4
  - `tasks/garden_cancellations_and_termination_fees/task_tools.py` fce4c09b4c0e2377b69a16ecec16ae96a05dfa18cecdaa5df85d481580440fae
  - `blueprint/products/garden.yaml` 891b8165746fc964e5faca57abac15bf221f07913c90ab094bccebddef05335e
- Read for this section: blueprint.yaml, db_schema.json, share_tools.py, products/garden.yaml (whole), products/biz.yaml and products/home.yaml (variant parameters plus the charge, late-fee, cancellation, sizing, enrollment and benefit-basis rules), the extended charter, task_tools.py, and the coordinator checklists audits/render_source/{XF_recipe.md, realism_bar.md, owner_ruling.md}. I also used the DSL evaluator `skills/erl-task-instantiate/scripts/check_compute.py` (the build_env/eval_compute semantics) to evaluate compute expressions.
- Not read (masked): every task's evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure and db_closure; tasks/*.json; worklog.md; plan.md; other difficulties' tasks or audits.
- Entry conditions (Step 0): the snapshot file records seven green instantiate gates (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE). The masked views are present and their hashes match (task0 c07d9a41…, task1 df18b504…). The base section of the extended file (lines 1–1806) is byte-identical to blueprint/products/garden.yaml (I checked with `diff`).

### policy_conflict_scan
The charter has eight extended policies, one business/residential pair for each of four write subjects:

| policy | target_tool | owner | event written | trigger |
|---|---|---|---|---|
| garden_ext_business_settlement_payment | pay_garden_settlement_c372b67a | user | garden_payment_received | on_request |
| garden_ext_business_etf | assess_closing_etf_d780691d | agent | garden_etf_assessed | state_due |
| garden_ext_business_returned_late_fee | assess_reopened_late_fee_7f086ee4 | agent | garden_late_fee_assessed | state_due |
| garden_ext_business_excess_decrease_fee | assess_decrease_fee_e48668a1 | agent | garden_change_fee_assessed | state_due |
| garden_ext_residential_settlement_payment | pay_garden_settlement_8237cc21 | user | garden_payment_received | on_request |
| garden_ext_residential_etf | assess_closing_etf_e3af903e | agent | garden_etf_assessed | state_due |
| garden_ext_residential_returned_late_fee | assess_reopened_late_fee_3e91b283 | agent | garden_late_fee_assessed | state_due |
| garden_ext_residential_excess_decrease_fee | assess_decrease_fee_99d02cc8 | agent | garden_change_fee_assessed | state_due |

- Business and residential siblings split cleanly by plan name. Each retiring overwrite names its sibling in its tail, and every tail restates the base text for the out-of-scope residue (XF E1/E3 hold).
- Trigger rule (XF F4): the base `triggers` of all four events written are `[]`, so no write lands in another category.
- **Claim breach (finding C-SCOPE).** The blueprint claims these event types for this difficulty: garden_notice_given, garden_notice_withdrawn, garden_closed, garden_preactivation_cancelled, garden_etf_assessed, garden_allocation_reduced, garden_successor_assigned, garden_transfer_lapsed, garden_charge_billed. Three of the four event types the charter writes are outside that list: garden_payment_received, garden_late_fee_assessed and garden_change_fee_assessed. Six of the eight policies therefore govern writes the difficulty does not claim. The blueprint summary describes the scope as "notice period, scheduled end date, the fee per kW … with its per-plan cap and waivers … the agent records the notice outcome, removal, closing and fee"; settlement payments, re-opened-charge late fees and excess-decrease fees fall outside it.
- Overlapping subjects with the base: settlement overlaps garden_evt_payment_application, garden_benefit_basis and garden_cancellation ("a balance left after closing remains due"). The late fee overlaps garden_evt_late_fee and garden_evt_payment_application. The ETF overlaps garden_cancellation, garden_transfer_at_move and garden_nonpayment_removal (not cited). The decrease fee overlaps garden_allocation_change. The conflicts found are listed under findings C-APPLY, C-ETFRED, C-RESERVE and C-NONPAY.
- Task scopes: tasks/0 runs on a Garden Business Fixed 15 world and tasks/1 on a Garden Fixed 10 world. On those worlds the business four and the residential four respectively are the only policies engaged, so the inferred scopes are disjoint and together cover all eight policies. charter_scope itself is masked until the reveal.

### rule_compute_equivalence
- Mechanical sweep (normalised whitespace): every `compute_basis` quote of all eight policies is verbatim in its rule. So is every `baseline.rule`, every prerequisite `policy_source` and every overwrite `replaced_by`. Each policy's compute_basis keys equal its compute binding names (XF E5 holds).
- Every ladder tier appears both as a rule sentence and as a branch of its `decides` binding, and the reverse also holds.
- Rounding (XF D1/D2): settlement, ETF, late fee and decrease fee each apply RND(x+1e-9) last, which matches each rule's "rounding … applies last". Late fee: "the rounding, the minimum and the maximum … apply last in that order" equals MN(max, MX(min, RND(·))). ETF: "rounded half up to the cent and then limited to etf_cap_usd" equals MN(cap, RND(·)). Floors: ETF basis_kw MX(0,…) is stated ("the result never falling below zero"), and decrease excess_kw MX(0,…) is stated ("nothing when the decrease is within it").
- **Edge mismatches (findings C-B5, C-C1, C-NONPAY, C-C3):**
  - (a) Both late-fee computes floor `unpaid: MX(0, …)`, but the rules define the unpaid amount with no floor. With unpaid 0 the compute then raises the fee to late_fee_min_usd, while the inherited sentence says "No fee is written … when the charge is fully paid".
  - (b) ETF `h_*/b_*` take `CFIELD/CPARAM` first-match per status. The rule says "one qualifying subscription in active status and one in allocated status each count once". Suppose the first active match was signed before the request date and a second active one after it: the compute deducts 0, while the rule deducts the qualifying one's contract_kw.
  - (c) Settlement `last_month` = LATEST(statement_month) by posted_date. The rule reads "the latest statement_month with a posted credit". A corrected re-post of an earlier month, which base garden_evt_credit_correction produces ("a new posting"), makes the compute return the older month (month_gap ≥3, so 2×avg) where the rule returns the newer (gap 2, so 1×avg).
  - (d) Late fee `charge_id/charge_amt/charge_due` = LATEST actual charge of ret_month by bill_date. The rule names "the actual subscription charge whose billing_month equals …" in the singular and gives no selection. A reversed-and-re-posted month carries two actual charges.
  - (e) ETF `request_date` falls back to '', and `lead_days: DAYS('', closing_date)` then raises an error. Base garden_nonpayment_removal applies the ETF to a nonpayment removal, a closing with neither a notice_date nor a move_transfer request, and the rule has no absent-record tier (XF B3).
  - (f) "whole calendar months" in the late fee (repeat windows), settlement (avg window) and decrease fee (term_left, overlap) states no month-end convention. The compute uses MONTHS() (day-of-month comparison). The base charter's own convention ("when the target month has no such day, the last day of that month is used") gives one more month at month-end edges, for example bill 08-31 against assessment 02-28.

  None of (a)–(f) is engaged on either task world (both worlds checked: no reversals, one actual charge per month, one other-line holding per status, closings carry a request date).

### action_binding_and_uuids
- Each (target_tool, computes) pair is claimed by exactly one policy, and the eight uuid8s (c372b67a, d780691d, 7f086ee4, e48668a1, 8237cc21, e3af903e, 3e91b283, 99d02cc8) share no prefix or sequence.
- Docstrings carry no ordering word, name no other tool and state no sequence position. The tool bodies make unconditional single `ctx.create` writes: no eligibility check, no prerequisite check and no derived value (`_Money.cents` only rounds the argument) (XF G2 holds).
- frozen_time format and banned imports are clean (G1). No composite args (G4). No factor id is a substring of a tool name (G5).
- **Finding C-G3.** All eight docstrings declare `amount` "a positive number with 2 decimal places", but no body enforces positivity. `amount=0` or a negative amount books a 0.00 or negative fee line or payment, contradicting the docstring and the rules' "when the computed fee is 0.00 no fee line is written".
- The business and residential tool bodies for the same event are byte-identical apart from their docstrings. Each docstring names its plan family, so the binding reading is unique (observation O10).

### prerequisite_graph
- All eight policies fill `prerequisite`. Only the two settlement policies carry edges, three each, all pointing at the same-family sibling policy ids in this file:
  - business: settlement → {business_etf, business_returned_late_fee, business_excess_decrease_fee}
  - residential: the residential mirror of the same three edges
- No policy points at itself or at a base policy, the graph is acyclic (depth 1) and no edge crosses tasks.
- Every edge is form=state with no fallback_reason (correct for state form) and kind=value_input with gate `lines_all`, a real binding of the settlement compute. resolved_by equals the depended-on policy's target_tool.
- Each `condition` matches its sentence's strength: "holds a garden_etf_assessed line for its closing" / "a garden_late_fee_assessed line referring to the charge the most recent payment_returned line re-opened" / "a garden_change_fee_assessed line for the most recent subscriber_decrease filing".
- **Finding C-E4.** The `effect` text of the ETF edge in both settlement policies (lines 1873 and 3547) reads "the line read by the prompt and partner deductions". No "partner" deduction exists in the charter; the deductions are prompt settlement and agreement form. This is a stale name in charter text (XF E4).

### prerequisite_sentences
For all six sentences:
- **Four-point test.** Each sentence joins the settlement result to a waited-on state with an ordering connective: "fixed only after", "not fixed until", "Before … must". The state is ledger-visible and named in table words: "the billing ledger carries the early termination fee line owed for its closing"; "… the late fee owed on the charge that the subscription's most recent returned payment re-opened"; "… the excess-decrease fee line owed for the subscription's most recent subscriber decrease". No sentence names a tool, policy id, snake_case token or row id. Each matches the edge condition.
- **No second wording.** The depended-on rules do not restate the sentences, and the docstrings are silent about order.
- **Derivation, one reading each.** The sentence names a fee line, and the reader finds the one rule in the plan family that books that fee line: the ETF rule ("prices the early termination fee of a subscription on a Garden Business plan"), the returned-payment late fee rule ("prices the late fee on the subscription charge that the most recent returned payment … re-opened") or the excess-decrease fee rule. Each of these rules names its own amount, assessment date and due date. On each family's world exactly one write brings each state about. The opposite-family tool writes the same event type, but its policy excludes this plan by name (O10).
- **Vacuous worlds (observation O7).** Where nothing is owed (no returned payment, computed fee 0.00, open subscription with no closing), the sentences presuppose a line "owed" that does not exist. They read as vacuously satisfied. Neither task world engages this.

### override_declarations
Sentence by sentence against base_policy_refs:
- **ETF (both).**
  - Retired and declared: the base ETF formula sentence (kW basis, years, rounding, cap, assessment/due) and "No other circumstance waives or reduces the early termination fee of a Garden plan".
  - Followed: term condition, at most once, the four waivers ("Apart from the waivers of the base rule"), assessment on the closing date, due invoice_due_days later, and garden_transfer_at_move's "early termination fee … applies unless waived there".
  - Not followed and not declared: garden_nonpayment_removal (not in base_policy_refs) says "the early termination fee of garden_cancellation applies as for a cancellation closing on the removal date". The extended standard method counts only cancellation_removal/move_removal lines, and the retiring tail says "no Garden subscription remains under the retired sentence". A nonpayment removal (filing_reason nonpayment_removal) inside the term therefore prices to kW 0, writes no line, or errors (see (e) above). This is a dropped branch (finding C-NONPAY).
- **Late fee (both).**
  - Retired and declared: the base fee sentence, which carried the unpaid definition (garden_msr_unpaid_on_charge: "the charge's amount less payments settled to it").
  - Followed and restated: dual only, grace, at most one per charge, no fee when fully paid/credited/disputed.
  - Conflict: the replacement defines the unpaid amount by the billing_month label of payments ("less the payments recorded for that billing_month, plus the payment_returned amounts recorded for that billing_month"). The in-force, un-retired garden_evt_payment_application, cited in this policy's own base_policy_refs, settles payments "in payment_application_order: the line with the earliest due_date first", and after a return "the lines it had settled are open again from their original due dates". When a payment labelled for month M+1 arrives after month M's payment was returned, the two clauses disagree about which charge is unpaid. The disagreement also creates a base-rule late fee owed on charge M+1 under "every other late fee remains under the base rule" (finding C-APPLY; both task worlds engage it, demonstrated in 0.md and 1.md).
- **Decrease fee (both).**
  - Retired and declared: the allowance/fee/assessment sentence (allowance basis moves from "held on the first day of that contract year" to "held before the decrease"; assessment "or … on the day it is booked").
  - Followed: company-initiated lines excluded, one change per year, the filing calendar.
- **Settlement (both), overwrite [].**
  - Followed: payment application, portal/no card numbers (narrowed to ach/card, no mailed check: observation O8), billing_month.
  - Conflict, undeclared: the prompt-settlement and agreement-form tiers deduct "percentages of the early termination fee line" from what the subscriber pays. Three in-force clauses say otherwise. (1) The ETF policies' own retiring tail: "the early termination fee of a subscription on a Garden Business plan … is adjusted only as this rule states …; no other circumstance waives or reduces the early termination fee of a Garden plan." (2) garden_cancellation: "a balance left after closing remains due." (3) garden_benefit_basis: "Billing credits are separate ledger lines". Since no credit line is written, the deducted share stays on the ledger as owed. The "settlement" therefore does not settle the balance, and the agreement form's "settlement clause credits part of the early termination fee" credits nothing (finding C-ETFRED).
  - Conflict, undeclared: the reserve tier collects "twice the average monthly charge" or "one average monthly charge" for a statement the utility has not posted. Every Garden plan sets estimated_billing_allowed false and max_consecutive_estimates 0, and base garden_evt_subscription_charge allows an estimate only "when estimated_billing_allowed is true" (finding C-RESERVE).

### factor_ladders
Labels are judged against XF B1: a pair of tiers fails when the two are the same combination of the same input up to a constant multiplier, or when they are aggregates of the same field under different filters. Each pair is listed with its distinguishing input.

**Settlement (business = residential; 4 factors).**

| factor | label | tiers | pairwise | verdict |
|---|---|---|---|---|
| closing_line_scope | method | SUM(amount) all / bill_date≤today / due_date≤today | all three pairs: same field, different filter | **fails B1 → parameter-class**; realism ok (acceleration at closing) |
| prompt_settlement_share | parameter | 2 / 1 / 0 % of ETF line | distinct values | label ok; conflicts with C-ETFRED |
| agreement_form_share | parameter | 3 / 1.5 / 0 % | distinct | label ok; C-ETFRED |
| final_statement_reserve | method | 2×avg / 1×avg / 0 | (1,2) constant multiple of avg | **fails B1**; C-RESERVE |

Genuine method factors: **0** (floor 1), so the floor fails (finding C-B1). Multi-source: none. cross_difficulty: none. All four are tagged R6.

**ETF (business and residential identical; 6 factors).**

| factor | label | tiers | pairwise | verdict |
|---|---|---|---|---|
| remaining_year_rule | method | (m+1)/12 / ⌊m/12⌋ / ⌊m/12⌋+1 | (1,2),(1,3): proration without floor vs floor; (2,3): floor with/without the +1 part-year term | passes on (1,x); (2,3) borderline (O1). R3 ok |
| share_band_rate | parameter | 85% / 92% / 100% of rate | distinct | R1 ok |
| line_switch_credit | method | contract_kw / 0.5×contract_kw / 0 | (1,2) constant multiple | **fails B1 → parameter**. Multi-source (other-line status+signed_date vs garden request date; plan term). cross_difficulty (home/biz) |
| notice_lead_rate | parameter | 80 / 90 / 100 % | distinct | R2 ok |
| market_rate_relief | parameter | 80 / 90 / 100 % | distinct | **unreal ladder (C-MARKET)** |
| prior_decrease_addback | method | dec_kw / 0.5×dec_kw / 0 | (1,2) constant multiple | **fails B1 → parameter**. R6 anti-avoidance ok |

After relabelling: 1 method (remaining_year_rule) and 5 parameter. The count holds, but two labels are dishonest (C-B1).

**C-MARKET (charter-level).** Enrollment states "The contract_rate_per_kwh written at enrollment is the plan's fixed_rate_per_kwh in force on the signed_date". Each Garden variant carries one fixed_rate_per_kwh. So escalated rate = fixed_rate × (1+esc)^n ≥ fixed_rate for every subscription. Tier 2's condition "at least the plan's fixed_rate_per_kwh" holds of every customer who reaches this write, and the fall-through "in full" (the baseline) is unreachable. The ladder reduces to "≥ n0 complete contract years → 80 %, else 90 %" (n0 = 7 at 1.5 %, 5 at 2.0 %, 10 at 1.0 %), which is a tenure discount on a termination fee (realism_bar X1).

**Late fee, business (6 factors) and residential (5 factors).**

| factor | label | tiers | pairwise | verdict |
|---|---|---|---|---|
| lateness_accrual | method | pct×⌈days/30⌉ / pct×1.5 / pct | (1,x): adds days input; (2,3): constant multiplier | **fails B1** (pair 2,3) |
| repeat_lateness_points | parameter | +1.0 / +0.5 / 0 | distinct | R6 |
| unpaid_band_share | parameter | 80 / 90 / 100 % | distinct | R6 |
| closing_status_load | parameter | 125 / 110 / 100 % | distinct | R6 |
| returned_instrument_points | parameter | check +0.5 / ach +0.25 / 0 | distinct | tagged R1; really R6 (late-fee rate keyed on the instrument of a returned payment) |
| other_line_lateness_points (business only) | parameter | +1.0 / +0.5 / 0 | distinct | R6; cross_difficulty biz (XCOUNT home/biz late fees) |

Genuine method factors: **0** (floor 1), so the floor fails (C-B1). Multi-source: none, but the task-level requirement is met through the ETF.

**Decrease fee (5 factors, both).**

| factor | label | tiers | pairwise | verdict |
|---|---|---|---|---|
| term_position_allowance | parameter | 35 / 25 / 20 % | distinct | R2 ok |
| decrease_size_rate | parameter | 85 / 95 / 100 % | distinct | R1 ok |
| advance_request_terms | parameter | 80 / 90 / 100 % | distinct | R2 ok |
| allowance_basis_rule | method | contract_kw / held_before−increase_kw / held_before | (1,2): different field; (1,3): different field; (2,3): adds an increase-lines input | **passes B1**; R6 |
| closing_overlap_share | parameter | 50 / 75 / 100 % | distinct | R6. Tiers are reachable only when the fee was not booked on its effective date (O4) |

Other structure:
- Every ladder has three disjoint tiers with stated boundaries.
- Every fall-through equals its factor baseline, except market_rate_relief, whose fall-through is unreachable.
- No decides is `result`. Binding sets are disjoint.
- No factor reads another factor's binding (XF A1 holds).
- Assembly is stated once, generically, with a fixed order (A2/A3 hold).
- baseline.params match the baseline paragraphs (A8 holds).

**C-R6COUNT.** realism_bar R6 requires "minimal in count". The non-R6 kinds available are R1–R5, plus the R6 factors needed for the cross-difficulty and multi-source floors:
- ETF: 3 non-R6 factors plus line_switch_credit (needed) reach the floor of 4. market_rate_relief and prior_decrease_addback are surplus R6 (and market fails anyway).
- Business late fee: accrual (R2) and instrument (claimed R1) plus other_line (needed) leave one more slot. repeat, band and closing_status make three R6 where one suffices, so two are surplus.
- Residential late fee: one surplus R6.
- Decrease fee: three non-R6 plus one R6 suffice, so one surplus (allowance_basis_rule is the only method, so closing_overlap_share is the surplus).
- Settlement: four R6 factors with no non-R6 alternative offered, so the count is minimal.

The surplus R6 factors cannot be graded R6-WAIVED.

### findings
| id | verdict | summary | bears on |
|---|---|---|---|
| C-SCOPE | SOURCE-POLICY RED | 3 of 4 written event types (garden_payment_received, garden_late_fee_assessed, garden_change_fee_assessed) lie outside the difficulty's claimed event_types; 6 of 8 policies govern unclaimed writes | 0, 1 |
| C-APPLY | SOURCE-POLICY RED | late-fee unpaid defined by payment billing_month labels contradicts the in-force oldest-due-first payment application; under the base reading the next month's charge is unpaid and its base late fee is owed at once (owed-write class) | 0, 1 (demonstrated per task) |
| C-ETFRED | SOURCE-POLICY RED | settlement deducts prompt/form percentages of the ETF line against the in-force "no other circumstance waives or reduces the ETF" (ETF replaced_by), "a balance left after closing remains due" and the credit-line rule; the deducted share stays owed, so the "settlement" does not settle | 0, 1 |
| C-RESERVE | SOURCE-POLICY / SOURCE-FACTOR RED | reserve collects estimated charges for an unposted statement on plans with estimated_billing_allowed false / max_consecutive_estimates 0 | 0, 1 |
| C-B1 | SOURCE-FACTOR RED | mislabelled method factors: closing_line_scope, final_statement_reserve (both settlements), line_switch_credit, prior_decrease_addback (both ETFs), lateness_accrual (both late fees); settlement and late-fee computations are left with 0 genuine method factors | 0, 1 |
| C-MARKET | SOURCE-FACTOR RED | market_rate_relief tier-2 condition holds of every customer; fall-through unreachable; tenure discount in disguise (X1) | 0, 1 |
| C-R6COUNT | SOURCE-FACTOR RED (realism bar) | R6 minimal-count condition unmet: ETF +2, business late fee +2, residential late fee +1, decrease fee +1 surplus R6 factors | 0, 1 |
| C-NONPAY | SOURCE-POLICY RED | ETF drops the base nonpayment-removal branch (kW basis 0 → no line) and has no absent-request tier (DAYS('') error) | not engaged |
| C-C1 | SOURCE-POLICY RED | rule ≠ compute on second-record/decoy probes: CFIELD first-match (line_switch), LATEST-by-posted_date statement month (reserve), singular charge of a month (late fee) | not engaged |
| C-B5 | SOURCE-POLICY RED | late-fee MX(0) floor on unpaid not in rule words; unpaid 0 yields the minimum fee where the rule writes none | not engaged |
| C-C3 | SOURCE-POLICY RED (minor) | "whole calendar months" without a month-end convention in late fee, settlement and decrease fee; MONTHS() differs from the base charter's last-day-of-month convention | not engaged |
| C-G3 | SOURCE-POLICY RED | eight tool docstrings promise a "positive number" the bodies never enforce | 0, 1 (tool layer) |
| C-E4 | SOURCE-POLICY RED (minor) | stale "partner deductions" in both settlement ETF-edge effects | 0, 1 |

Observations:
- **O1.** remaining_year_rule pair (2,3) differs only by the +1 part-year term (floor vs floor+1). I accept it as a counting-convention change, but it sits at the edge of B1.
- **O2.** garden/biz/home benefit_basis "no … second subscription … changes that price, and benefits never stack" is worded for charges. Up to six ETF reductions stack (band, lead, market, switch, then prompt and form at settlement). line_switch_credit lowers a fee because of a second subscription. Not graded RED, since the rule words govern subscription charges.
- **O4 (H3).** Every tree rests on fees left unbooked for 26 days to 7 months, although the rules assess them on the closing date, effective date or grace end. closing_overlap_share's discounting tiers are reachable only through that booking lag: a fee booked on its effective date sees an open subscription and a 100 % tier.
- **O5.** The decrease-fee "request with the latest received_date" has no outcome filter. A later declined allocation_decrease request makes the rule and compute price 0, while the settlement sentence still waits on "the excess-decrease fee line owed for the subscription's most recent subscriber decrease". Rule equals compute; the risk is a desync.
- **O6.** held_before ("filed lines less reduced lines other than that decrease and the closing removal") also subtracts company lines or increases dated after the decrease, so it is not the allocation "held before" in such worlds.
- **O7.** The prerequisite sentences are vacuous where nothing is owed (see prerequisite_sentences).
- **O8.** Settlement is narrowed to portal ach/card, while base payment application also accepts mailed check.
- **O9.** The R6 factors not counted surplus are graded R6-WAIVED: closing_line_scope, prompt_settlement_share, agreement_form_share, line_switch_credit, the R6 late-fee factors within the minimum, and allowance_basis_rule.
- **O10.** Two tools per event type with identical bodies; the plan-family docstrings and policies make the reading unique.

## closing_checklist
Written after both reveals (2026-10-25T09:27Z). Nothing above this heading was changed after the reveals.

- **Per-task files.** 0.md and 1.md correspond one-to-one to tasks/0.json and tasks/1.json. Each has a frozen section written before any reveal, then a comparison section. Neither comparison is PASS.
- **Coverage.** The 8 extended policies are covered. Scopes (charter_scope) are task 0 = business four and task 1 = residential four: disjoint and complete.
- **UUIDs.** Each tool's uuid8 is independent.
- **Event types.** 3 of 4 written event types lie outside the claimed event_types (C-SCOPE). The author's DECISION D1 acknowledges this; it needs a coordinator ruling.
- **Problem trees.** Each has 3 prerequisites, 3 value_input edges and an owner=user root. Both are acyclic and hold on their worlds. Task 0's closure cites wrong step numbers (T0-4).
- **Factors: FAIL.**
  - Settlement and late-fee computations have 0 genuine method factors (C-B1).
  - market_rate_relief ladder is unreal (C-MARKET).
  - final_statement_reserve conflicts with the base (C-RESERVE).
  - R6 minimal count is exceeded (C-R6COUNT).
  - Weight (T1) itself is proven for every factor on both worlds. Baseline results are definite and differ from gold.
- **Unique solution: FAIL.** Both tasks admit a second settlement through C-APPLY (6145.83/6148.77 and 918.24) and through C-ETFRED (6387.41 and 935.73).
- **Gate re-run.** Not re-run by this auditor, because the artifacts were not changed. The round-1 snapshot gates are green, as cited.

Difficulty does NOT pass the source-layer audit.

VERDICT revision_1: task0=RED task1=RED charter=C-SCOPE,C-APPLY,C-ETFRED,C-RESERVE,C-B1,C-MARKET,C-R6COUNT,C-NONPAY,C-C1,C-B5,C-C3,C-G3,C-E4

## revision_2

## charter_global_frozen (revision_2)
- **Freeze.** Frozen 2026-10-25T10:1xZ, before any revision-2 GT was revealed. Auditor: the same independent auditor. Revision 1 text above is untouched.
- **Entry conditions.**
  - The worklog tail reads `REWORK round 2: gates 7/7 green`; I read only that line (`tail -1`).
  - I executed `/tmp/erl0082_coord/snapshot.sh garden_cancellations_and_termination_fees 2` (output 2026-10-25T09:55:42Z). It printed EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK and SCOPE OK.
- **Hashes.** Both shared inputs moved, so every charter-global section is re-derived in full.

  | file | sha256 |
  |---|---|
  | garden.extended.yaml | 25182277777162dda96819d8798439eba1d2517bde53c9231bc1a2915599b8f2 |
  | task_tools.py | 3961ebbd4ef551ffe85386c29622234da7e2a0cdda178b8aeb87cb974c9d7330 |
  | task0.view | a3a39a54b859dd59efe3379c27a0cdca83814bd4e4098dbae33d0304ef30d185 |
  | task1.view | 25a8441572d9121deddc826245cc164e7e99951e98bc4108d018d2be233461fa |

- **Read.**
  - rework_r2_claims.md, which carries item ids only.
  - realism_bar.md AMENDMENT 1 (points 1–8). XF_recipe.md and owner_ruling.md are unchanged.
  - The new charter and tools. The base section is still byte-identical to blueprint/products/garden.yaml.
- **Not read.**
  - worklog.md (beyond the tail line), plan.md, and every masked task field.
  - This means **I could not inspect the reworker's LEVER CATALOGUE**: AMENDMENT 1.2 places it in the worklog, and the same addendum forbids reading the worklog. I checked R6 against the charter myself instead; see factor_ladders.

### policy_conflict_scan (r2)
- There are still eight policies in two plan families.
- New elements:
  - **Settlement:**
    - dispute_holdback and moved_share_deferral replace the prompt and agreement-form deductions.
    - reported_statement_prepay replaces the reserve.
    - The rule now cites garden_evt_credit_correction and garden_evt_subscription_charge.
  - **ETF:** counts nonpayment_removal lines and cites garden_nonpayment_removal. agreement_form_terms replaces market_rate_relief. Moved kW are now read from other-line initial filings in the removal filing_month.
  - **Late fee:** unpaid is defined through payment application. lateness_accrual is re-anchored. A zero floor and no-fee clause are added.
  - **Decrease fee:** the request read is filtered to outcome completed.
- Event types: under AMENDMENT 1.1, writing own-category events outside the event_types list is legitimate. The base books all four events written, the triggers are `[]`, and the task scopes stay disjoint. **C-SCOPE is closed by the ruling.**
- New conflict, settlement against garden_evt_payment_application (finding **C-HOLDAPPLY**):
  - The settlement rule says the settlement "holds back" the disputed line and (with moved kW) the not-yet-due ETF. It says the posted-but-uninvoiced statement's charge is added and that "the payment then settles that charge when it is invoiced". It also says that "a part of it that covers no open line stays on the subscription for the line it was taken for".
  - The same rule says "what the payment covers is settled under payment application". The in-force base rule settles "open charge and fee lines … the line with the earliest due_date first", with no exception for disputed lines and no earmarking.
  - In the same situation the two passages give different terminal states. Applied oldest-due-first, the settlement payment settles the disputed line in full. It then puts the rest on the ETF line it was supposed to hold back. The later-invoiced statement charge is left open. Demonstrated per task in 0.md and 1.md.

### rule_compute_equivalence (r2)
- **Sweep.** Every compute_basis quote, baseline.rule, policy_source and replaced_by is verbatim in its rule. Compute_basis keys equal the binding names in all eight policies.
- **Closed items:**
  - C-B5: `result = 0 if unpaid <= 0`, and the rule states "never below zero; when it is 0.00 no fee is written".
  - C-NONPAY: nonpayment_removal is counted. `lead_days -1` when there is no request date, matching "otherwise, or when the closing has no request date, in full". This was probed with the absent record.
  - C-C3: every policy states "the difference in calendar months, less one when the later date's day of the month is smaller …; no last-day-of-month substitution", which equals MONTHS().
  - C-C1 (c): the reserve is gone.
  - C-C1 (d): "with the latest bill_date among those" equals LATEST.
  - C-C1 (b) is re-designed (see C-C2).
- **New, finding C-C2 (XF C2, same-day ties not stated).**
  - (i) Settlement and ETF: "the moved subscription is the one whose such line takes effect latest". All initial lines filed in one MN_CSG filing_month take effect on the same first-of-month date, so whenever two qualifying lines exist (home and biz, or two of one line) the latest is a tie. The compute resolves it silently: `moved_home_term if moved_home_eff > moved_biz_eff else moved_biz_term` picks biz on a tie, and XLATEST picks the first row met within a category. The rule states no tie rule, and the term_months of the two plans can differ, which changes the deduction or deferral by 50 points.
  - (ii) Late fee: "the most recent payment_returned line (the line with the latest bill_date)" has no tie rule for two returns on one day.
  - (iii) Settlement prepay: "the posted line with the latest posted_date" has no tie rule for two statements posted together.
  - None of these is engaged on either world.
- **New, finding C-LABEL (XF C6 and AMENDMENT 1.7).** The late-fee rule asserts that "each payment is recorded under the billing_month of the line it settles", and computes the unpaid amount from labels on that premise.
  - The base payment event carries one billing_month, but under oldest-due-first one payment can settle lines of two months. The premise is therefore not producible in general.
  - The seeds contradict it. Re-applying every payment oldest-due-first (scratch apply.py):
    - task0 garden: 7a801728 (5.00, labelled 2026-01) settles 74ecbe1f (2026-02); a5f83454 (400.72, labelled 2026-02) settles 395.72 of 2026-02 plus 5.00 of late fee ee6166c9 (2026-01).
    - task0 biz: 4af78d08 and 8892425a split across 2025-11 and 2025-12 the same way.
    - task1 garden: 66767fe9, 67e3b5f7, f786e250 and 8267afb2 likewise split.
  - Counterfactual on the task0 seed: had a5f83454 been the returned payment, the rule's label arithmetic gives unpaid 400.72 on 74ecbe1f, while application gives 395.72 (5.00 was paid by 7a801728).
  - No world engages this for the returned charge itself (both re-opened charges were paid by a single same-month payment). It is a seed-producibility defect and a false premise in rule text.

### action_binding_and_uuids (r2)
- The uuid8s are unchanged and unique. Each (target_tool, computes) pair has a single claimant.
- All eight bodies now return "Nothing booked …" when `amt <= 0`, and the docstrings say so. **C-G3 is closed.**
- A non-positive guard is a value-format check, not a prerequisite judgement.
- No ordering words; G1/G2/G4/G5 are clean.

### prerequisite_graph / prerequisite_sentences (r2)
- The edges, forms, kinds, gates, conditions and resolved_by are unchanged.
- The six policy_source sentences are verbatim and unchanged; the four-point test and single-reading derivation still hold, as in revision 1.
- The effect texts now read "the moved-share deferral reads the same line" and contain no stale names. **C-E4 is closed.**

### override_declarations (r2)
- **ETF:**
  - Both overwrites now name the nonpayment-removal closing, and garden_nonpayment_removal is cited. The dropped branch is closed.
  - agreement_form_terms reduces the ETF inside the ETF rule ("adjusted only as this rule states"), so it is consistent with the in-force restatement.
- **Settlement:**
  - It no longer deducts any part of the ETF. moved_share_deferral holds the line back "to its due date" (timing only), so "no other circumstance … reduces" is not engaged. **C-ETFRED is closed.**
  - reported_statement_prepay prices an already-posted statement by the base charge formula for closed subscriptions, so this is not an estimate. **C-RESERVE is closed.**
  - The notice_given tier ("the per-kWh rate of the latest actual charge") differs from the charge rule across an anniversary. That tier is an approximation the charge rule will not bill (observation O12; not engaged).
  - New: C-HOLDAPPLY (see policy_conflict_scan).
- **Late fee:** the unpaid definition is now worded as payment application, but rests on the false premise C-LABEL.
- **Decrease fee:** unchanged except for the outcome filter. **O5 is closed.**

### factor_ladders (r2)
**Settlement (4 factors, both families).**

| factor | label | pairwise check | realism |
|---|---|---|---|
| closing_line_scope | P | — | acceleration at closing; R6-WAIVED |
| reported_statement_prepay | M | (1,2): escalated contract rate vs latest charge's rate per kWh; (1,3),(2,3): an added statement input. **Passes B1** | R6-WAIVED (O12) |
| dispute_holdback | P | — | real: base dispute rules. Tier 2 is reachable only after Meadowlark misses its own dispute deadline (O4-class) |
| moved_share_deferral | P | — | cross-difficulty home/biz; multi-source (not-yet-due AND moved kW AND term); R6-WAIVED |

Counts: 1 method and 3 parameters. The reworker's "dispute" over the method count is moot, since the floor is 1.

**ETF (6 factors).**

| factor | label | realism |
|---|---|---|
| remaining_year_rule | M | O1 unchanged |
| share_band_rate | P | R1 |
| line_switch_credit | P | relabel accepted; multi-source; cross-difficulty |
| notice_lead_rate | P | R2 |
| agreement_form_terms | P | R6: contract-version ETF schedule; plausible |
| prior_decrease_addback | P | relabel accepted; R6 anti-avoidance |

C-MARKET is closed (factor removed). The ETF has 1 method and 5 parameters.

**Late fee.** lateness_accrual (M) is re-anchored:
- tier 1 counts started 30-day periods from the return date (payment came back after the due date);
- tier 2 counts from the due date (payment came back on or before the due date);
- tier 3 is flat.

Pair (1,2) uses a data-selected anchor; pairs (1,3) and (2,3) add the period-count operation. **It passes B1, and it is realistic** (lateness runs from when the customer actually became late). The C-B1 residue is closed.

**Decrease fee.** Unchanged. allowance_basis_rule (M) passes.

**R6 under AMENDMENT 1.2.** I could not inspect the catalogue (see freeze). My own charter scan follows.
- **ETF, candidate unused lever (observation O13).** closure_reason is recorded and publishable. The base already keys waivers on it, and it takes distinct values on the two worlds (subscriber_cancellation, transfer_not_completed). Whether the catalogue marks it unusable, and why, I cannot verify. agreement_form_terms and prior_decrease_addback are graded R6-WAIVED, conditional on that.
- **Late fee, finding C-INVENT.** AMENDMENT 1.2 excludes from R6 "an invented mechanism no community solar provider uses". Two factors in each late-fee policy are such mechanisms:
  - returned_instrument_points (business and residential) adds late-fee *rate* points according to the instrument of a returned payment (check +0.5, ACH +0.25). The base already charges the return through the returned-payment fee. Late-payment charges in utility and community-solar billing are a percentage of the past-due amount, bounded by a minimum and maximum, and are not keyed on the payment instrument.
  - closing_status_load (business and residential) loads the late fee by 125 % on closed accounts and 110 % on pending ones. No published late-payment schedule I know of raises the late-charge rate because the account closed.

  This re-grades my revision-1 O9, which had graded both R6-WAIVED; the AMENDMENT's exclusion clause is new binding text. Removing these two leaves the business late fee with 4 factors (accrual, repeat, band, other_line) and the residential late fee with 3, below the floor.
- repeat_lateness_points, unpaid_band_share and other_line_lateness_points are graded R6-WAIVED (plausible repeat-delinquency and balance-tier schedules). closing_overlap_share and allowance_basis_rule are R6-WAIVED.

### findings (r2)
| id | r1 → r2 | evidence |
|---|---|---|
| C-SCOPE | CLOSED (AMENDMENT 1.1) | own-category events, base-booked, triggers [] |
| C-APPLY | CLOSED on both worlds (re-seeded; no second fee owed: task0 10bbbda9 grace through 11-20, task1 62d8407f through 11-10); charter residue moved to C-LABEL | apply.py open-line list |
| C-ETFRED | CLOSED | deductions removed; deferral is timing-only |
| C-RESERVE | CLOSED | posted statement priced by the charge formula |
| C-B1 | CLOSED | relabels plus redesigned accrual and prepay pass B1 |
| C-MARKET | CLOSED | removed |
| C-R6COUNT | SUPERSEDED by AMENDMENT 1.2 → C-INVENT RED; O13 observation | — |
| C-NONPAY | CLOSED | absent-request probe gives full lead tier; kW basis counts nonpayment lines |
| C-C1 | CLOSED except the tie residue → C-C2 | — |
| C-B5, C-C3, C-G3, C-E4 | CLOSED | — |
| **C-HOLDAPPLY** | NEW SOURCE-POLICY RED | settlement holdback, prepay and earmark sentences against in-force oldest-due-first application |
| **C-LABEL** | NEW SOURCE-POLICY RED | false "each payment is recorded under the billing_month of the line it settles" premise; 8 mislabelled seeded payments |
| **C-C2** | NEW SOURCE-POLICY RED | three unstated same-day/same-effective-date tie rules |
| **C-INVENT** | NEW SOURCE-FACTOR RED | returned_instrument_points and closing_status_load (×2) are invented mechanisms |
| **C-USAGE** | NEW SOURCE-POLICY RED (seed, task0) | see 0.md |

Observations:
- O4: unchanged.
- O11: task0 frozen 2026-11-20 is past the 7th anniversary 2026-11-06, so a contract-year-7 true-up (a no-change row: allocation changed in the year, closed share) is owed. No tool writes it, and it has no ledger effect.
- O12 and O13: as above.

## closing_checklist (revision_2)
Written after both revision-2 reveals at 2026-10-25T10:04Z. The revision_2 charter-global section above it was written before the reveals.

- **Scored values and proofs.**
  - Both tasks' scored writes, order, closures (step numbers now correct), factor_sensitivity and baseline_result match my blind derivation.
  - Scopes are disjoint and complete. The tools keep their uuid8s, and the non-positive guard has been added.
  - Trees: 3 value_input edges each, an owner=user root, acyclic, load-bearing. The trees hold.
- **Unique solution.** It holds for the scored amounts in both tasks.
- **Remaining RED: policy (charter or seed).**
  - C-HOLDAPPLY: the settlement's holdback, prepay and earmark sentences contradict in-force payment application.
  - C-LABEL: a false single-label premise in the late-fee rule; 8 seeded payments are mislabelled; the GT proof asserts they are labelled correctly.
  - C-C2: three unstated tie rules.
  - C-USAGE: the task0 garden and biz true-up usage for the same account disagree.
- **Remaining RED: factor.**
  - C-INVENT: returned_instrument_points and closing_status_load in both late fees are invented mechanisms.
  - The residential late fee then falls below the 4-factor floor.
- **Not fully checkable.** The R6 waivers of agreement_form_terms and prior_decrease_addback are conditional on the LEVER CATALOGUE (O13). It sits in the worklog, which this addendum forbids me to read; candidate unused lever: closure_reason.
- **Gate re-run.** I re-ran the gates once through snapshot.sh round 2: 7/7 OK.

The difficulty does NOT pass the source-layer audit.

VERDICT revision_2: task0=RED task1=RED charter=C-HOLDAPPLY,C-LABEL,C-C2,C-INVENT,C-USAGE
