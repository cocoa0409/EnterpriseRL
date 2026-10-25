# Policy-task audit — business_allocation_changes_and_trueups / charter-global

## revision_1

## charter_global_frozen
- Auditor: erl-task-policy-audit (independent of the instantiator). Frozen 2026-10-25T09:24Z, before any task's GT was revealed; nothing in this section is derived from a revealed GT.
- Hashes (match the coordinator snapshot /tmp/erl0082_coord/snaps/business_allocation_changes_and_trueups.r1.txt):
  - biz.extended.yaml 782fa43c05be244af75a3d2aa2f479371347608c3682f85b091a321c0a0f6990
  - task_tools.py bb7f188768466a8fad69225cb6714b9cda24106e783933055518d527f4bf4a42
  - task0.view.json 5bac0969…8e46, task1.view.json 80c19064…cf4a
- Entry conditions (Step 0): gate snapshot supplied with all seven instantiate gates OK (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE); masked views supplied with hashes. Input complete.
- Read: blueprint.yaml, products/biz.yaml (base section of the extended file is byte-identical to it — `diff` of lines 1–1906 empty), products/garden.yaml (for cross-category seed checks), db_schema.json, share_tools.py, biz.extended.yaml, task_tools.py, the two masked views, erlbench DSL semantics (skills/erl-task-instantiate/scripts/check_compute.py: MONTHS, _within, LATEST, CFIELD, XCOUNT), coordinator files audit_common.md, XF_recipe.md, realism_bar.md, owner_ruling.md.
- Masked / not read: tasks/*.json, worklog.md, plan.md (never), other difficulties, other scenarios.
- Scratch: /tmp/audit_business_allocation_changes_and_trueups_0082/ (derive.py, t0.py, t1.py, hist.py, probes.py, sweep.py).

### policy_conflict_scan
Extended policies (4): biz_ext_guarantee_trueup (subject biz_trueup_completed, tool complete_guarantee_trueup_bd5f1ac2, agent), biz_ext_decrease_amendment_fee (biz_change_fee_assessed, accept_share_decrease_75e61509, user), biz_ext_late_statement_estimate (biz_charge_billed, bill_statement_estimate_b08e308f, agent), biz_ext_increase_deposit (biz_deposit_held, pay_increase_deposit_a318506d, user).
- Overlapping subjects: each extended policy overlaps exactly one base policy (biz_evt_annual_trueup, biz_allocation_change, biz_evt_subscription_charge, biz_evt_security_deposit); overlaps are handled by self-naming overwrites (see override_declarations for the residue). No two extended policies share a subject, trigger or write.
- Cross-policy reads: decrease reads the latest true-up written by the guarantee policy (declared value_input edge); deposit reads charges written by the estimate policy (declared value_input edge). No other extended policy reads another's output. Graph: decrease→guarantee, deposit→estimate; acyclic.
- Cross-category reads: decrease reads garden holding (CFIELD status/utility_account_id/allocation_kw); deposit reads garden_billing late fees (XCOUNT). Reads only; no write lands outside biz.
- Claimed event families vs writes: the blueprint claim lists [biz_allocation_filed, biz_allocation_reduced, biz_change_fee_assessed, biz_trueup_completed, biz_billing_credited]. Tools write biz_trueup_completed + biz_billing_credited (guarantee), biz_change_fee_assessed (decrease) — in the claim — and biz_charge_billed (estimate) and biz_deposit_held (deposit) — NOT in the claim. The write fence is per category (blueprint SKILL: "only writes are fenced", primary category axis), so no sibling collision results; recorded as observation O-1. No tool writes biz_allocation_filed/biz_allocation_reduced although they are claimed (no filing tool exists in this difficulty).
- Task scopes (inferred from tools, personas and seeds, to be confirmed against charter_scope after reveal): task0 = {guarantee, decrease}, task1 = {estimate, deposit}: pairwise disjoint, jointly covering all four extended policies.

### rule_compute_equivalence
- Scratch sweep (sweep.py): every compute_basis quote is verbatim in its rule (E5 clean); every baseline.rule sentence is in the rule; every replaced_by and every prerequisite policy_source is verbatim in the rule; no compute binding lacks a basis.
- DSL window semantics: `_within` keeps rows with 0 <= MONTHS(row_date, NOW) < n, i.e. date after the same calendar day n months before today and on or before today — matches the rule wording "after the same calendar day … and on or before" in guarantee/estimate/deposit.
- Edge inequivalences found (each is a finding below): F-GT-BASEEXCL (inherited base "not active for all twelve months" exclusion not in compute), F-C3 (month-end convention: guarantee's convention differs from base's; decrease/estimate/deposit state none), F-C2 (no same-day tie rule for LATEST over requests/charges/credits), F-B4-DEP (deposit tier-2 grouping), F-G3/F2 (0.00 and "positive" edges between rule floors and tool contracts).
- Other edges checked and consistent: guarantee measured lines count postings less reversals (rule and compute); banked share 0 when posted value 0; rate-step fall-through "including when no posting falls in those year-earlier months" = `year_kwh <= 0 → 100`; usage-decline "including for a subscription without a true-up" = `peak_usage_kwh > 0` guard; decrease/deposit share on file = SUM(filed) − SUM(reduced) (F('allocation_kw') used for share_kw in the decrease — equal on any consistent holding).

### action_binding_and_uuids
- (target_tool, computes) pairs are unique: (complete_guarantee_trueup_bd5f1ac2, guarantee_credit), (accept_share_decrease_75e61509, excess_decrease_fee), (bill_statement_estimate_b08e308f, estimated_charge), (pay_increase_deposit_a318506d, deposit_amount).
- uuid8s bd5f1ac2 / 75e61509 / b08e308f / a318506d: distinct, no common prefix, no sequence pattern. No factor id is a substring of a tool name (G5 clean). No datetime/random/uuid imports; half-up helper is a class static method (G1 clean). Every write tool calls ctx.create/update in its own body (G2). No composite args (G4). No concrete example values in docstrings (H5).
- No tool refuses, errors or hints on a prerequisite; no tool aggregates history or judges eligibility (bodies read only the subscription/request row for customer_id and billing_type; the deposit tool updates the running-sum field deposit_held_usd).
- Docstring ordering words (observation O-2): accept_share_decrease "The request itself stays open until Meadowlark files the decrease"; bill_statement_estimate "When the utility later reports that month's credit, the actual charge and the offset … are booked separately". Neither names another tool or a gold write (no filing tool exists), so no consequence is demonstrable.
- Docstring claims not enforced by the body: see F-G3.

### prerequisite_graph
- Every policy fills `prerequisite` (guarantee [], estimate [], decrease 1 edge, deposit 1 edge). Problems point at policy ids of this file; acyclic; no base policy, no self-reference.
- Decrease edge: problem biz_ext_guarantee_trueup, kind value_input, gate latest_usage_kwh (a real binding), form state, policy_source verbatim in the decrease rule, resolved_by complete_guarantee_trueup_bd5f1ac2 (the guarantee target_tool), effect (latest usage and guaranteed kWh become the new true-up's) genuinely changes allowance_pct and released_kw. condition matches the sentence.
- Deposit edge: problem biz_ext_late_statement_estimate, value_input, gate monthly_estimate (real binding), state form, policy_source verbatim, resolved_by bill_statement_estimate_b08e308f, effect real. BUT its `condition` reads "…ended more than estimate_wait_days calendar days before the frozen date" — authoring/harness phrasing in general text → F-PREQ-FROZEN.

### prerequisite_sentences
- Decrease: "The excess-decrease fee of a decrease amendment is fixed only after the records carry a completed true-up for every contract year of the subscription that has ended." Ordering connective "only after"; waits on a record-visible state (true-up records per ended contract year); no tool/policy id/snake_case; strength equals condition. Exactly one write of this difficulty produces a biz_reviews row (complete_guarantee_trueup_bd5f1ac2) — single resolver. Derivation: sentence → biz_reviews shows years 1..k−1 but the anniversary of year k has passed → the policy whose rule records a contract year's true-up (biz_ext_guarantee_trueup, base biz_evt_annual_trueup) → its tool. The guarantee rule does not restate the sentence. Single reading.
- Deposit: "The increase deposit is not fixed until the billing ledger carries a subscription charge, actual or estimated, for every statement month whose estimate waiting period has passed." Connective "not … until"; state form; clean. The only tool writing biz_charge_billed is bill_statement_estimate_b08e308f (no actual-charge tool) — single resolver in any world where the missing month has no posted credit. The estimate rule does not restate it. Single reading. Satisfiability gap in some engaged worlds → F-F1.
- No rule carries a second wording of either dependency. Cross-problem order stated without an edge: deposit rule "…for an allocation-increase request … before the increase is filed" orders the deposit before a base filing that no tool of this difficulty performs — no second order is producible, observation O-3.

### override_declarations
Sentence-by-sentence against base_policy_refs:
- biz_ext_guarantee_trueup vs biz_evt_annual_trueup: (1) annual_review_enabled — follows. (2) completed no earlier than the anniversary — follows. (3) "Contract year n ends on the activation_date plus n times review_interval_months calendar months; when that month has no such day, the last day of the month is used." — handled differently, undeclared: the extended "contract year reviewed … a month counting as whole once the review date's day of the month reaches the activation_date's day of the month" counts activation 2024-02-29 → review 2026-02-28 as MONTHS 23 → year 1, while base says year 2 ended on 2026-02-28 (probe P4) → F-C3. (4) reviewed exactly once — overwritten. (5) review period — overwritten. (6) credited/value/avg rate/"usage_kwh_12m … for the same months" — avg rate and credited follow via measured lines; "the same months" and the period months the tool records lose their defining clause → F-E1-GT. (7) guaranteed/shortfall — overwritten. (8) "The guarantee is not assessed (guaranteed_kwh 0) for a year in which the subscription was not active for all twelve months, the utility account changed, or the allocation changed." — account/allocation parts are excluded by the scope sentence (no filing line took effect); "not active for all twelve months" is inherited but neither implemented nor overwritten: probe P3 (subscription notice_given at the review, otherwise task0's world) → compute 167.93 where the inherited base sentence gives 0 → F-GT-BASEEXCL. (9) guarantee credit — overwritten. (10) posted as billing credit on review_date — follows (tool). (11) right-sizing, (12) outcome — follow (agent-supplied args).
- guarantee vs biz_benefit_basis: guarantee credit is a separate ledger line — follows.
- biz_ext_decrease_amendment_fee vs biz_allocation_change: filing calendar, first-change wait, reduction status, yearly change limit, increment sizing, min_allocation floor, company lines excluded — all follow; allowance/fee/assessment-date sentence — overwritten (self-naming tail restates it verbatim for other decreases). No residue.
- biz_ext_late_statement_estimate vs biz_evt_subscription_charge: pricing, banked, billable status, invoicing of actual charges, activation, late-statement offset — follow; "Estimates: …" — overwritten; "Each posted credit statement line is priced by exactly one actual subscription charge." — overwritten although it does not conflict with estimates (an estimate prices no line) and is restated for its whole domain → F-E2-EST (XF E2 member; no semantic change).
- biz_ext_increase_deposit vs biz_evt_security_deposit: review outcomes, deposit_required gate, release rule, no interest, never applied while open — follow; amount sentence — overwritten; "The deposit is paid by the business through the secure payment portal (ach) or by check before approval and never by a representative taking account numbers." — timing "before approval" not overwritten while the extended policy holds a deposit on an approved, active subscription → F-DEP-TIMING (undeclared override).

### factor_ladders
Per policy (effect as declared → as audited). "Pairwise" = distinguishing input per tier pair (XF B1).

biz_ext_guarantee_trueup (5 declared; cross_difficulty none):
| factor | declared | tiers | audit |
| degradation_schedule | parameter | ≥6: 0.7; 2..5: 0.5; otherwise 0 | FAIL: scope sentence admits only "a contract year after the first", so "the contract year reviewed is 2 or later" holds of every customer reaching this write and the fall-through 0 is unreachable in scope — two live tiers (F-LAD-DEG). Realism R5 (degradation-adjusted guarantees are standard). |
| excused_statement_months | method | <9 credited months: 0; 9–11: months/12; ≥12: 1 | PASS. Pairs: (0,prorate) prorate>0 on its domain; (0,1) nothing vs full; (prorate,1) prorate adds input credited_months. R3. |
| surplus_carryover | method | excess>cap: cap; 0<excess≤cap: excess; none: 0 | PASS. Pairs: (cap,excess) cap reads only prior guaranteed, excess reads prior credited too; nothing tier distinct. Clamp = one family factor (A7); T1 cap binds on task0, T2 excess binds when 0<excess≤5 %. R5. |
| banked_credit_valuation | parameter | banked share >25 %: applied rate; 0–25 %: mean; 0: average | FAIL label: tiers compute the rate by different formulas (applied rate adds input banked_value; mean adds an operation) — a method labelled parameter (F-LBL-BANK). Realism: R6 at best (company valuation keyed on recorded banked_value), not minimal (four R1–R5 factors exist) and in tension with base "The whole credit_value is priced whether the utility applied it … or banked part of it" (F-R6-MIN). |
| share_size_guarantee_schedule | parameter | ≥150 kW: +3.0; 50–150: +1.5; <50: plan | PASS (R1 credit schedule keyed on share-size band). |
Honest survivors: parameter 1 (share-size), method 2 → below the floor of 2 parameter and 4 factors (F-FLOOR-GT).

biz_ext_decrease_amendment_fee (6 declared; cross_difficulty garden):
| usage_decline_allowance | parameter | declined AND garden: 50; declined AND no garden: 40; otherwise plan | PASS, multi-source (reviews + garden holding), cross-difficulty garden. R6-WAIVED-grade (ties to account-wide sizing of biz_agg_account_sizing); observation O-4 on benefit-basis spirit. |
| usage_matched_release | method | oversized >10 %: all; 0<oversized≤10 %: half; none: 0 | FAIL B1/label: released = c × oversized with c ∈ {1, 0.5, 0}; pair (all, half) is the same input under a constant multiplier; the "none" tier's domain (oversized 0) gives 0 under every tier (F-B1-REL). |
| term_position_rate | parameter | after term: 0; <12 months to term end: min(fee, etf/kW); otherwise fee | PASS (R5). Note: etf/kW < excess fee on every plan (40<60, 35<50, 45<70, 50<80, 50<80) so the min's other bound never binds (O-5). |
| change_depth_multiplier | parameter | >50 %: 1.5; 30–50 %: 1.25; else 1 | Realism R6, not minimal: term (R5), timing (R2), size (R1), release (R4 content) and the cross factor already exceed the floor (F-R6-MIN). |
| contract_year_timing_multiplier | parameter | month 0: 0.75; 1–2: 0.9; ≥3: 1 | PASS (R2). |
| share_size_multiplier | parameter | ≥150: 0.8; 50–150: 0.9; <50: 1 | PASS (R1). |
Honest methods: 0 → floor fails (F-FLOOR-DEC).

biz_ext_late_statement_estimate (6 declared; cross none):
| thin_basis_widening | method | <2 in 3-month window & ≥1 in 6 months: 6-month average; none in 6 months: latest actual; ≥2 in window: 3-month average | FAIL B1: pair (6-month average, 3-month average) differs only in window length — XF B1 "never just … a window length"; aggregates of the same field are one input (F-B1-THIN). |
| outstanding_estimate_level | parameter | ≥2: 75; 1: 85; 0: 100 | R6-WAIVED-grade. |
| reversal_history_level | parameter | ≥2: 90; 1: 95; 0: 100 | R6-WAIVED-grade. |
| history_length_level | parameter | <12 months since activation: 90; 12–24: 95; else 100 | FAIL realism X1: a tenure/new-customer level on the computation (F-X1-HIST). |
| share_size_estimate_level | parameter | ≥40 kW: 97; 20–40: 98.5; else 100 | R6 (not a fee/rate/credit schedule — an estimate haircut by share size, which the basis already reflects). |
| credit_rate_step_level | parameter | latest rate >1.5 % above year-earlier: 102; >1.5 % below: 98; else 100 | PASS (R4 tariff-rate change). |
R1–R5 survivors: thin_basis content (R3) and rate step (R4) → two R6 factors would be minimal; four candidates (outstanding, reversal, history, share) are present → F-R6-MIN. Honest methods: 0 → F-FLOOR-EST.

biz_ext_increase_deposit (6 declared; cross_difficulty garden):
| payment_record_months | parameter | dual AND (≥2 own late fees OR ≥1 garden late fee): plan+1; dual AND none on either: 1; otherwise plan | PASS, multi-source, cross-difficulty garden (garden_billing). Observation O-6: one garden late fee raises the tier while one own late fee does not. |
| returned_payment_months | parameter | ≥2: 1; 1: 0.5; 0: 0 | PASS (real). |
| enlarged_share_band | parameter | ≥40: 0.95; 20–40: 0.98; <20: 1 | PASS (R1). |
| increase_depth_level | parameter | >40 %: 1.2; 20–40 %: 1.1; else 1 | R6, not minimal (F-R6-MIN); also scales a quantity already proportional to the added kW. |
| remaining_term_level | parameter | <12: 0.5; 12–24: 0.75; ≥24 or no term: 1 | PASS (R2). Edge: after term_end the count is negative → 0.5 (O-7). |
| held_deposit_adjustment | method | held<current: +(current−held); held>current: −0.5×(held−current); equal: 0 | FAIL B1: adjustment = c × (current − held) with c ∈ {1, 0.5}; the "equal" tier's domain yields 0 under every tier (F-B1-HELD). Its tier-2 text is also ambiguous (F-B4-DEP). |
Honest methods: 0 → F-FLOOR-DEP.

Counts: multi-source factors usage_decline_allowance (task0 side) and payment_record_months (task1 side); cross_difficulty factors read garden in both trees. Per-task floors are judged in the task files.

### findings
All are SOURCE-POLICY or SOURCE-FACTOR RED at charter level unless marked observation. XF classes are listed exhaustively.
- F-LAD-DEG (SOURCE-FACTOR, task0): degradation ladder — tier condition "2 or later" restates scope; fall-through unreachable; rule sentences quoted above.
- F-LBL-BANK (SOURCE-FACTOR, task0): banked_credit_valuation is method-shaped, labelled parameter.
- F-B1-REL (SOURCE-FACTOR, task0), F-B1-THIN (task1), F-B1-HELD (task1): method ladders whose tier pairs differ only by a constant multiplier or a window length. Exhaustive B1 sweep: the only passing method factors are excused_statement_months and surplus_carryover.
- F-FLOOR-GT / F-FLOOR-DEC (task0), F-FLOOR-EST / F-FLOOR-DEP (task1): after the strikes, guarantee has 3 honest factors with 1 parameter; decrease, estimate and deposit have no honest method factor.
- F-X1-HIST (SOURCE-FACTOR, task1): history_length_level is a tenure/new-customer level (realism bar X1).
- F-R6-MIN (SOURCE-FACTOR): R6-grade factors beyond the minimal count — members: banked_credit_valuation (task0), change_depth_multiplier (task0), two of {outstanding_estimate_level, reversal_history_level, share_size_estimate_level} plus history (task1), increase_depth_level (task1). R6-WAIVED-grade (observation) only where minimal: usage_decline_allowance, and two of the estimate levels.
- F-GT-BASEEXCL (SOURCE-POLICY, no task consequence): inherited base exclusion "not active for all twelve months" not implemented; probe P3.
- F-C3 (SOURCE-POLICY, no task consequence): month-end conventions. Members: guarantee contract_year_reviewed (conflicts with base contract-year-end convention, probe P4); decrease months_into_year and term_rate "twelve whole months"; estimate months_active, widened/reversal/year-earlier windows; deposit months_left and the late-fee/returned windows — none states which month-end convention applies while the base charter states a different one ("when the target month has no such day, the last day of that month is used"): activation 2025-01-31 → 2026-02-28 is MONTHS 12 in compute (P4b) but 13 under the base convention.
- F-C2 (SOURCE-POLICY, no task consequence): no same-day tie rule for LATEST reads — decrease requested_kw / request_received (probe P1: two decrease requests received the same day → 30 or 50 kW by row order), deposit requested_kw, estimate latest_actual and latest_rate. (Guarantee states its tie rule.)
- F-B4-DEP (SOURCE-POLICY, no task consequence in task1 since held < requirement): "minus excess_credit_share of the held deposit less the current requirement" reads −0.5×(held−current) or current−0.5×held (probe P5 with held 900: −82.88 vs +284.25). Observation: the decrease's "divided by 100 times that true-up's guaranteed_kwh" has only a dimensionally void second reading.
- F-E1-GT (SOURCE-POLICY): the guarantee overwrite retires the review-period sentence without restating, for in-scope years, the period months the true-up records (period_start_month / period_end_month) and the months over which usage_kwh_12m is taken ("for the same months"). Task0 consequence assessed in task0.md.
- F-E2-EST (SOURCE-POLICY, XF E2): non-conflicting base sentence retired; no semantic change.
- F-DEP-TIMING (SOURCE-POLICY, task1): undeclared override of base "before approval" deposit timing.
- F-PREQ-FROZEN (SOURCE-POLICY, task1): deposit prerequisite `condition` uses "the frozen date".
- F-F1 (SOURCE-POLICY, no task consequence): the deposit's state is unsatisfiable without waiting in engaged worlds — a statement month past its waiting period whose credit posted less than invoice_issue_days ago (estimate barred because a credit posted; no actual-charge tool; the charge waits for its invoice day), or more consecutive late months than max_consecutive_estimates.
- F-G3 (SOURCE-POLICY, no task consequence): docstring claims not enforced by bodies — bill_statement_estimate estimated_charge "greater than 0.00"; pay_increase_deposit deposit_amount "greater than 0.00"; complete_guarantee_trueup contract_year "1 or more", credited_kwh_12m/guaranteed_kwh/shortfall_kwh "0 or more", resize_kw/guarantee_credit "0.00 or more". Linked F2 edge: the deposit rule floors at "zero when that is negative" and the estimate can be 0 (`latest_actual or 0`), yet neither rule states a 0.00 path while both tools declare amounts > 0.00.
- H-seed findings are per task (task0: garden share with no ledger; task1: garden share with no filing line).
- Observations: O-1 claimed-event families vs writes; O-2 docstring ordering words; O-3 deposit "before the increase is filed"; O-4 garden holding raising a fee-free allowance vs biz_benefit_basis "no … second subscription … changes that price" (the fee is not a priced charge); O-5 dead bound in term_position_rate; O-6 payment-record asymmetry; O-7 post-term deposit term level; O-8 baseline.params lists omit params named only in the out-of-scope tails (production_guarantee_pct, savings_rate_pct, expected_yield…); O-9 garden "active" read as status=active excludes a still-filed notice_given garden share (probe P2).

## closing_checklist
Written after both reveals (2026-10-25T09:27Z); the charter-global section above was frozen before them and is unchanged.
- Files: _difficulty.md, 0.md, 1.md — one per task; first revision.
- Coverage/scope: charter_scope task0 = {biz_ext_guarantee_trueup, biz_ext_decrease_amendment_fee}, task1 = {biz_ext_late_statement_estimate, biz_ext_increase_deposit} — disjoint, jointly complete; tools and GT closed; uuid8s independent.
- Trees: each task has one prerequisite problem, one value_input edge, one owner=user write, no cycle; the difficulty graph is a DAG. Gold values reproduce my blind derivations exactly (167.93, 301.89, 315.33, 579.75, all dates/args) and every factor_sensitivity / baseline_result figure.
- Not closed: factor floors and realism (all four computations), plus the SOURCE-POLICY items listed below. The difficulty does NOT pass the source-layer audit.
- Gate re-run on the final form: not applicable — nothing changed this round (hashes as in the r1 snapshot).
- Charter RED ids: F-LAD-DEG, F-LBL-BANK, F-FLOOR-GT, F-B1-REL, F-FLOOR-DEC, F-B1-THIN, F-FLOOR-EST, F-B1-HELD, F-FLOOR-DEP, F-X1-HIST, F-R6-MIN, F-GT-BASEEXCL, F-C3, F-C2, F-B4-DEP, F-E1-GT, F-E2-EST, F-DEP-TIMING, F-PREQ-FROZEN, F-F1, F-G3; seed reds per task (task0 garden share without any ledger, task1 garden share without its filing line).
VERDICT revision_1: task0=RED task1=RED charter=F-LAD-DEG,F-LBL-BANK,F-FLOOR-GT,F-B1-REL,F-FLOOR-DEC,F-B1-THIN,F-FLOOR-EST,F-B1-HELD,F-FLOOR-DEP,F-X1-HIST,F-R6-MIN,F-GT-BASEEXCL,F-C3,F-C2,F-B4-DEP,F-E1-GT,F-E2-EST,F-DEP-TIMING,F-PREQ-FROZEN,F-F1,F-G3
