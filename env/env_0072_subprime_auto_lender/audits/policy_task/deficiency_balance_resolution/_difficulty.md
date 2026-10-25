# Policy-task audit — deficiency_balance_resolution / charter-global

## revision_1

## charter_global_frozen
- Frozen 2026-10-19T23:54Z, before any task GT was revealed. Auditor: independent policy-task auditor (not the instantiator).
- Hashes: `deficiency.extended.yaml` 177415da51d3d8b60c8fc056443fc1618347e9c91a393acfc6790b82fd6655c5; `task_tools.py` da468bc401b602144ae484eef713d03a9688373b414a43a0c9a6a6ad4e520dd1 (they match the brief); base `products/deficiency.yaml` b2093040…5fb62; `db_schema.json` f5fecc1f…941755; `share_tools.py` 169d05b6…c4c4.
- Read: blueprint.yaml, db_schema.json, share_tools.py (signatures), products/deficiency.yaml (through the verbatim base copy), products/recovery.yaml and contract.yaml (only the expense, late-charge and interest parameters, to re-price seeded cross-category rows), the extended charter, task_tools.py, audits/render_source/XF_recipe.md, the DSL in skills/erl-task-instantiate/scripts/check_compute.py (MONTHS/DAYS/LATEST/within_months semantics), and the masked views r1/0.json and r1/1.json (hashes match the brief).
- Masked / never opened before the freeze: tasks/*.json, plan.md, both worklog.md files, any audit conclusions. No recursive grep touched the difficulty directory.
- Entry conditions: gate snapshot supplied (EXTENDED / TASK TOOL CONTRACT / REPLAY --check / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK); masked views and their hashes supplied. Complete.
- Scratch: /tmp/audit_deficiency_0072/ (mech.py, xf.py, evalp.py, t0.py, t1.py, contract_check.py). They re-evaluate the charter's compute on scratch copies of the masked worlds, using the gate's own DSL.

### policy_conflict_scan
- Base copy: the part of the extended file before `extended_policies:` is byte-identical to products/deficiency.yaml (checked by diff).
- Five extended policies, five task tools, one `(target_tool, computes)` each:
  P1 `deficiency_ext_restart_down_payment` -> pay_restart_down_payment_04892a83.amount_usd (owner user);
  P2 `deficiency_ext_plan_installment` -> record_payment_plan_offer_3f4fb3a9.installment_amount_usd (agent);
  P3 `deficiency_ext_lump_sum_settlement` -> record_lump_sum_settlement_offer_7c3d7537.offer_amount_usd (agent; it also takes hardship_document);
  P4 `deficiency_ext_installment_settlement` -> accept_installment_settlement_d1722676.settlement_amount_usd (owner user);
  P5 `deficiency_ext_settlement_installment` -> start_installment_settlement_185f50ba.installment_amount_usd (agent).
- Overlapping subjects: P1 and P2 both list `deficiency_payment_posted`; P3 and P4 both list `deficiency_settlement_waiver`. Their computed quantities are disjoint, so the overlap has no consequence. The subjects of P2/P3/P4 do not match the event their write produces (offer writes are intake rows). Observation O1.
- Trigger rule (XF 26): the only ledger event any tool writes is `deficiency_payment_posted` (P1), which triggers only `deficiency:deficiency_account_update`. `start_installment_settlement` produces `deficiency_settlement_started`, which triggers nothing. No tool writes into another category.
- Eligibility, time anchors and terminal states agree across policies: P1/P2 cover a new payment plan, P3/P4/P5 a settlement. The base restart requirement applies to plans only (base deficiency_payment_plan), so no settlement policy needs a restart. Base eligibility still in force for every task: explanation before demand, no offer while a dispute is open, time-barred handling, referral after 120 days without a payment, the settlement min-days / re-offer wait / broken-count bar, and the plan broken-count bar.
- Scope partition read off the prerequisite graph: two components, {P1, P2} (one tree: root P2, prerequisite P1) and {P3, P4, P5} (one tree: root P5, prerequisites P4 and P3). Together they cover all five policies and are disjoint. Which task claims which component is confirmed after the reveal (closing_checklist).

### rule_compute_equivalence
- Sweep (mech.py): every `compute_basis` quotation is a verbatim substring of its own rule; every compute binding has a basis; every `baseline.rule` sentence and every `replaced_by` is verbatim in its rule; every prerequisite `policy_source` is verbatim in the blocked rule (XF 16).
- Ladders: every tier of every factor is stated in its rule (condition plus value or method) and is a branch of its `decides` binding. No compute branch lacks a rule tier, and no rule tier lacks a branch.
- DSL semantics checked against the rule words:
  - `within_months=N` means `0 <= MONTHS(d, today) < N`, i.e. "fewer than N whole months before today".
  - MONTHS subtracts one when the end day-of-month is smaller than the start day.
  - DAYS counts calendar days ("no more than 90 calendar days" is `<= 90`).
  - LATEST keeps the first row on a key tie (strict `>`).
- Assembly and order (XF 3, 4): each policy states one generic combination sentence that fixes the order.
  - P1: points subtracted, percent applied, rounded, additions on top.
  - P2: replacement first, then one multiplicative total, then the raises to min$ and the term floor, then the ceiling to the cent.
  - P3: points added, percent applied once, rounded, rounded reduction subtracted, then floor and cap.
  - P4: replacement first, then surcharge points applied once and rounded, then floor and cap.
  - P5: replacement first, then cuts and additions, then the clamp to [1, max], then divide and ceiling.
- Rounding (XF 14): RND/ceiling placement matches the rule in all five policies, including P3's "itself rounded half up" reduction and P4's "each premium is rounded half up to the cent before any comparison".
- Edges (XF 11):
  - P2 and P5 recent counts can be negative (a return dated in the window for a payment posted before it). Compute falls through to the "none" tier. The rule's tiers are ">= k / exactly one / none". No second value is defensible. Observation O2.
  - P3 `ls_sale_ratio` returns 0 when book value is absent. The rule is silent, and every contract carries a book value. Observation.
  - The absent-prerequisite edges of P4 and P5 are RED: R-ABSENT below.
- Ties and decoys (XF 12): LATEST over `broken_date` is tie-free by the rule's own stated fact ("an account has only one arrangement in force at a time, so no two of its arrangements break on the same day"). LATEST over `created_at` is not tie-free: R-TIE below.
- Month-end (XF 13): R-MONTHEND below.

### action_binding_and_uuids
- Each `(target_tool, computes)` is claimed by exactly one policy (list above).
- uuid8s 04892a83, 3f4fb3a9, 7c3d7537, d1722676, 185f50ba share no prefix or suffix, are not sequential, and are not derived from one another.
- No factor id is a substring of any tool name (XF 7).
- Tool bodies validate no eligibility, prerequisite or amount. They write exactly what their docstrings claim (XF 28), and no docstring carries a concrete example value.
- Docstring sequence wording:
  - accept_installment_settlement says the installment fields "stay unset … until the settlement is started".
  - record_* offers say "no due date yet, since the due date is set when the borrower accepts".
  - start_installment_settlement is described as "Start an accepted installment settlement".
  - These place the accept action before the start action. The same order is already stated by the base eligibility `settlement_offer_accepted` (applies_to deficiency_settlement_started) and by P5's own prerequisite sentence. Nothing new is revealed, so no consequence can be shown. Observation O3.

### prerequisite_graph
- Edges: P2 -> P1 (value_input, gate pi_balance); P4 -> P3 (value_input, gate si_lump_read); P5 -> P4 (value_input, gate ss_amount_read). P1 and P3 have `[]`.
- Every `problem` is another extended id, never a base id and never itself. The graph is acyclic.
- Every edge has `form: state` with no `fallback_reason`. Every `resolved_by` is the depended-on policy's target_tool, and its body produces the state named in `condition`:
  - pay_restart creates deficiency_payment_posted with arrangement_offer_id None and reduces the balance.
  - record_lump_sum creates a lump_sum_settlement row with offer_date today.
  - accept creates an installment_settlement row with offer_status accepted.
- Every gate binding exists in the blocked compute. `effect` texts are accurate. `condition` is neither stronger nor weaker than its sentence. No authoring-viewpoint phrasing.

### prerequisite_sentences
- E1 (P2): "When the account had a broken arrangement in the rolling 12 months, the monthly installment of a new plan is fixed only after the account's ledger carries the restart down payment, posted after the latest broken date as a payment that carries no arrangement."
  - Four-point test: connective "only after"; record-visible state (a posted payment with no arrangement, dated after the latest broken date); no tool, id or snake_case token; conditional scope equal to the condition's.
  - Exactly one write of the difficulty brings the state about: pay_restart_down_payment is the only payment-posting tool.
  - Single-reading derivation: sentence -> the reader finds the policy whose rule figures "the restart down payment … collected as a payment on the account that carries no arrangement" (P1) -> P1's target write.
  - P1's own rule (its replaced_by) also says "a new plan also requires a restart down payment". This states the same order from the depended-on side, in substance rather than verbatim. It is the declared base replacement, so no conflicting order exists. Observation O4.
- E2 (P4): "An installment settlement amount is not worked out until the account carries a lump-sum settlement offer dated today." Connective "not … until"; record-visible state; one write (record_lump_sum_settlement_offer) brings it about; no tool or id. Single reading -> P3. P3's rule says nothing about installment settlements.
- E3 (P5): "The installment of an installment settlement is fixed only after the account carries an installment settlement offer that the borrower has accepted." Connective "only after"; state; one write (accept_installment_settlement) brings it about. Single reading -> P4. A base sentence (eligibility settlement_offer_accepted) states the same order, but P5 carries its own sentence, so this is an observation only (O5).
- No undeclared cross-problem order found in any extended rule.

### override_declarations
- P1 retires base deficiency_payment_plan "Where the account had a broken arrangement … a new plan also requires a down payment of plan_restart_down_payment_pct of the balance".
  - replaced_by names its scope and restates the out-of-scope case ("an account without a broken arrangement … needs no restart down payment").
  - The other sentences of the five base refs are followed: max-broken bar, offer validity, status gates, no-fee payments, separate resolution, explanation-before-demand, referral.
- P2 retires "The monthly installment is the greater of … on the acceptance date, rounded up to the cent". The retired clause's scope is the plans of balance >= min_balance_for_plan_usd (base: "A plan is offered only on an open account with a balance of at least min_balance_for_plan_usd"). replaced_by covers that whole scope and keeps the small-balance terms.
  - The small-balance installment count is under-determined in base itself; the overwrite neither creates nor resolves this. Observation O6.
  - The base parameter_schema gloss of plan_min_payment_pct_of_balance ("on the acceptance date (the installment is the greater of this and plan_min_monthly_payment_usd, rounded up to the cent)") will be rendered verbatim. It restates the retired clause, which replaced_by explicitly names ("in place of the greater of the two minimums on the balance on the acceptance date"). Observation O7, flagged for the KB audit.
- P3 `overwrite: []`, checked sentence by sentence against deficiency_settlement.
  - Base states only a minimum authority ("may be no lower than the greater of … and settlement_floor_usd, … the minimum percent is lowered by hardship_extra_discount_pct points").
  - P3's figure equals or exceeds that minimum on every input: surcharges are >= 0; the jobless reduction is <= h%; the floor and the balance cap are re-applied.
  - Offer validity, the settlement eligibility bars, the 1099-C rule and letters stay inherited. No undeclared departure.
- P4 `overwrite: []`. On the gated path its figure is >= the base installment minimum, because the lump figure is >= (lump% - h)% of the balance or the floor, plus spread% of the balance or more. Its absent-offer clause departs from the base minimum without a declaration: R-ABSENT.
- P5 `overwrite: []`.
  - Base "equal monthly installments … no more than max_settlement_installments": P5 rounds up to the cent (the last installment is smaller) and keeps the count <= max. Observation O8.
  - Its absent-acceptance clause contradicts the base eligibility gate: R-ABSENT.
- Sibling overwrites (XF 20): P1 and P2 retire different clauses of deficiency_payment_plan. No shared clause.

### factor_ladders
All 27 factors have three pairwise-disjoint tiers (fall-through included) with distinct values or methods. Bindings are disjoint, `decides` is never `result`, and labels are honest (`parameter` tiers change a number; `method` tiers change the formula). Each fall-through is its policy's baseline. Mechanical independence check (xf.py): no factor binding reads another factor's binding; only the assembly bindings (dp_pct/result, pi_adjust_pct/pi_adjusted, ls_pct/result, si_extra_pts/si_figure, ss_count) read factor outputs (XF 1-3). Quantities used by two or more parts are plain bindings stated once (dp_broken_date, pi_term_floor, si_floor). Single-use quantities are factor-owned (XF 5).

| policy | factors (effect) | counts | multi-source (gate sense: every fork A and/or B over distinct reads) | cross_difficulty |
|---|---|---|---|---|
| P1 | hardship_relief (p), surrender_relief (p), broken_run_relief (p), contract_history_relief (p), make_good_addition (m) | 5: 4p/1m | surrender_relief (recovery_method AND keys_obtained) | surrender_relief→recovery; contract_history_relief→contract |
| P2 | installment_basis_method (m), rebreak_surcharge, returned_surcharge, paydown_reduction, credit_tier_surcharge, recent_payer_reduction (p) | 6: 5p/1m | none in the gate sense | credit_tier_surcharge→contract |
| P3 | hardship_reduction_method (m), debt_age_points, sale_recovery_points, paydown_points, recovery_route_points, lapsed_offer_points (p) | 6: 5p/1m | none in the gate sense | sale_recovery_points→recovery+contract; recovery_route_points→recovery |
| P4 | premium_method (m), returned_points, idle_points, contract_paid_points, credit_tier_points (p) | 5: 4p/1m | none | contract_paid_points, credit_tier_points→contract |
| P5 | count_method (m), returned_cut, tier_history_cut, paydown_extension, recent_extension (p) | 5: 4p/1m | tier_history_cut (credit tier AND contract payment count, two distinct records) | tier_history_cut→contract |

Observation O9: surrender_relief's two conditions are two fields of the single recovery_cases row. It qualifies under the instantiate definition ("distinct evidence"), not under a strict "distinct records" reading. Other {P1,P2} factors are compound over distinct offer rows in prose (hardship_relief tier 2: no ssa/medical offer AND an unemployment offer; installment_basis_method tier 2: no hardship offer AND a broken plan within 12 months that ran 6+ months), but their first tiers are single conditions.

Method factors, all-pairs shape tables (XF 8). The distinguishing input is taken from the audited worlds where possible.

| factor | pair | shape difference | distinguishing input → values |
|---|---|---|---|
| make_good_addition (P1) | T1 vs T2 | sum of the 12-month returned rows' amount vs the latest broken offer's installment_amount_usd (different input) | returned total 140.96, broken installment 200.00 → +140.96 vs +200.00 |
| | T1 vs T3 | adds an input vs adds nothing; a return's amount is always > 0 | any return → +140.96 vs 0 |
| | T2 vs T3 | adds an input vs nothing; a broken arrangement always carries a set installment | break 68 days ago, installment 140.96 → +140.96 vs 0 |
| installment_basis_method (P2) | T1 vs T3 | balance/max_term vs greatest of (min$, pct×bal, bal/term): the standard adds two inputs and a max | Band 3, balance 5245.87 → 109.29 vs 131.15 |
| | T2 vs T3 | max(standard, prior plan installment) adds an input | prior installment 140.96 → 140.96 vs 131.15 |
| | T1 vs T2 | different inputs | 109.29 vs 140.96 |
| hardship_reduction_method (P3) | T1 vs T2 | T2 adds input jobless_cap×plan_min and a min | Band 4, balance 9525.46 → 952.55 vs 900.00 |
| | T1/T2 vs T3 | reduction vs none (balance > 0 on an open account) | 816.71 vs 0 |
| premium_method (P4) | T1 vs T3 | spread × original_deficiency vs spread × balance (different field) | 9925.46 vs 8167.06 → 992.55 vs 816.71 |
| | T2 vs T3 | adds floor input and a max | floor 1000 → 1000.00 vs 816.71 |
| | T1 vs T2 | different inputs and operation | 992.55 vs 1000.00 |
| count_method (P5) | T1 vs T3 | data-selected count (months a broken plan ran, min with max) vs constant max | ran 5 → 5 vs 6 |
| | T2 vs T3 | floor(amount/plan_min) vs constant | Band 4, amount 600 → 4 vs 6 |
| | T1 vs T2 | different inputs | 5 vs 35 → clamped 6 |

Every pair passes. No "nothing" tier coincides with another tier over its whole domain.

Gaps and overlaps against each policy's own scope (XF 9): none. Every ladder is "A / not A and B / otherwise", or numeric bands that close at both ends.

Realism (XF 10). Each condition below is one a deficiency-recovery desk weighs, and each outcome is a company schedule a subprime auto lender could publish:
- Hardship documents lower the restart percent, stretch the plan to the maximum term, and reduce the settlement.
- A surrender (voluntary, and with keys) is treated as cooperation.
- The run of the broken plan, and the contract installment history, count as demonstrated capacity.
- A make-good of bounced amounts or the missed installment is added.
- Surcharges apply for a recent re-break, returns, the credit tier, and an involuntary or impound recovery.
- Reductions apply for paydown and recent payments.
- Young debt carries a higher settlement percent.
- A higher sale recovery means a less disputable deficiency.
- Lapsed settlement offers carry a surcharge.
- An installment premium is charged over lump-sum; the installment count is capped at the months a broken plan lasted; the count is cut for weak tier/history and returns; the count is extended for paydown and recent payers.
- No loyalty or tenure inventions. Statutory items are inherited from base and real: UCC 9-616 explanation before demand, Form 1099-C at $600.

Two outcome choices are unusual but not shown to be unpublishable: O10 (P4 premium_method tier 2 reuses settlement_floor_usd, "smallest settlement accepted", as a minimum installment premium) and O11 (P1 surrender_relief differentiates by keys_obtained).

### findings
Charter-wide REDs. Every member of each class is listed.

**R-ABSENT — SOURCE-POLICY RED (XF 25 / 11 / 21): blocked rules state a figure for the case where their prerequisite record is absent, and the figure contradicts an in-force base clause with no overwrite.**
- Member P4. Symptom: the rule (and baseline.rule) says "an account without such an offer has a lump-sum figure of zero", next to "An installment settlement amount is the lump-sum figure plus an installment premium of min_installment_settlement_pct less min_lump_sum_settlement_pct percentage points of the balance".
  - Base deficiency_settlement, in force since overwrite is []: "The settlement amount may be no lower than the greater of the band's minimum percent of the balance on the offer date (min_lump_sum_settlement_pct for a lump sum, min_installment_settlement_pct for installments) and settlement_floor_usd".
  - Root cause: compute `si_lump: si_lump_read or 0` gives the absent edge a 0.00 value instead of carving it out.
  - Demonstration (task 1 opening world, account a72b872c…, Band 4, balance 8167.06, scratch run t1.py): P4 gives 0 + 992.55 + 571.69 = 1564.24, while base forbids any installment settlement below 55% × 8167.06 = 4491.88 (3675.18 even with the hardship 10-point allowance).
  - P4 is also internally inconsistent: it says the amount "is not worked out until" the offer exists, yet states a figure for that case.
  - Bears on: task 1 (the edge P4 ← P3).
- Member P5. "The settlement amount is the offer_amount_usd of the account's installment_settlement offer with offer_status accepted that was recorded most recently; an account without one is figured on its whole balance."
  - Base eligibility settlement_offer_accepted (applies_to deficiency_settlement_started): "A settlement is carried out only under an arrangement offer of offer_type lump_sum_settlement or installment_settlement that the borrower has accepted."
  - Demonstration (task 1 opening world): P5 figures 8167.06 / 4 = 2041.77 for a settlement start that base refuses outright. Two conclusions for the same situation: refuse vs. start at 2041.77.
  - Bears on: task 1 (the edge P5 ← P4).
- Non-members: P2 states no figure for the absent restart payment. P1 and P3 have no prerequisite.

**R-TIE — SOURCE-POLICY RED (XF 12 / 17): "most recently recorded" is resolved by LATEST over `created_at`, which ties for every row recorded in one consultation (the tools stamp created_at = ctx.now() = frozen_time), and LATEST then keeps the first row.**
- Member P4: "the offer_amount_usd of the account's lump_sum_settlement offer whose offer_date is today, the most recently recorded one where there are several" vs `si_lump_read: LATEST(..., date_field='created_at', offer_type='lump_sum_settlement', offer_date=NOW)`.
  - The "several" case is reachable only in-session, and in-session rows always tie. Seeds cannot hold a lump offer dated today: that would satisfy E2 at the opening.
  - Probe (t1.py, scratch copy of task 1): offers 3797.68 then 4000.00 recorded on the same clock. Rule → 4000.00; compute → 3797.68.
  - The rule's "recorded most recently" also names no field the records can order.
- Member P5: "…with offer_status accepted that was recorded most recently" vs `ss_amount_read: LATEST(..., date_field='created_at', …)`.
  - Probe: acceptances 5361.92 then 5000.00. Rule → 5000.00 / 4 = 1250.00; compute → 1340.48.
- Non-members: LATEST over broken_date in P1/P2/P4/P5 (tie-free by the stated one-arrangement fact).
- Bears on: task 1 only off the gold path. No gold value moves.

**R-MONTHEND — SOURCE-POLICY RED (XF 13): every extended "whole month" count is defined as "a whole month running from a date to the same day of a later month", which is undefined when the start day does not exist in the end month. MONTHS() silently applies day-overflow. The base charter's own convention is a month-end fallback (deficiency_msr_broken_arrangements_12m: "same calendar day 12 months earlier … month-end fallback to the last day of the month").**
- Demonstration: a payment dated 2026-03-31 seen on 2026-09-30. MONTHS = 5 → "fewer than 6 whole months" → counted. Under the charter's fallback convention, 6 whole months have run on 2026-09-30 → not counted. Likewise 2026-01-31 → 2026-02-28: MONTHS = 0, fallback = 1.
- Members (every sentence):
  - P1: restart hardship look-back; restart run (accepted_at → broken_date); restart make-good returned look-back.
  - P2: basis hardship look-back, carry window and carry run; rebreak surcharge (both bands); returned look-back; recent-payer window.
  - P3: hardship look-back; lump-sum debt age; lapsed-offer look-back.
  - P4: premium broken window; young-account months; returned look-back.
  - P5: count-method broken window; plan-ran months; returned look-back; recent-payment window.
- Bears on: neither audited world. Every window ends on the 19th of October, every start day is <= 28, and the run endpoints are 12-03→08-12 and 01-22→06-30.

Observations O1–O11 are as listed in the sections above. None is grounds for rework.

## closing_checklist
(written after the reveal — see below)

## closing_checklist
Written after the reveal of both tasks. It contains no GT-derived content in the charter-global sections above.
- Per-task files 0.md and 1.md correspond to tasks 0 and 1. Each carries source_derivation_frozen before source_gt_comparison. revision_1 is the first revision.
- Scope: charter_scope task 0 = {P1, P2} with tools {pay_restart_down_payment_04892a83, record_payment_plan_offer_3f4fb3a9}; task 1 = {P3, P4, P5} with tools {record_lump_sum…, accept_installment…, start_installment…}. The scopes are pairwise disjoint and jointly cover all five extended policies and five tools. Each uuid8 is independent.
- Trees:
  - Task 0: one prerequisite, one value_input edge, a user write (pay_restart).
  - Task 1: two prerequisites, two value_input edges, a user write (accept).
  - The whole-difficulty graph {P2→P1, P4→P3, P5→P4} is acyclic.
- Factors: 5/6 (task 0) and 6/5/5 (task 1) factors, each >= 2 parameter and 1 method. Multi-source: surrender_relief (task 0, see O9) and tier_history_cut (task 1). Cross-difficulty factors are seeded in both tasks. Every factor bears weight and every whole baseline differs from gold (all figures re-derived blind and equal to GT).
- **Not closed.** Task 1 is RED, and the charter carries the open REDs R-ABSENT (P4, P5), R-TIE (P4, P5) and R-MONTHEND (every whole-month sentence of P1–P5, listed in findings). The instantiation-stage gate re-run on a final form is therefore not applicable. The gates listed in the brief were green on the audited form (an entry condition, not proof).
VERDICT revision_1: task0=PASS task1=RED charter=R-ABSENT,R-TIE,R-MONTHEND

## revision_2

## charter_global_frozen (revision_2)
- Frozen 2026-10-20 (before any round-2 task file was read). Auditor: same independent auditor.
- Entry gate: `worklog.md` last line = "REWORK round 2: gates 7/7 green".
- Round-2 gate snapshot (coordinator `snapshot.sh deficiency_balance_resolution 2`, 2026-10-20T04:48:31): all seven gates OK (EXTENDED, TASK TOOL CONTRACT, REPLAY --check, SOLVABILITY, COMPUTE, GROUNDING, SCOPE).
- Masked views r2/0.json 0158a870…a9af and r2/1.json 3f4a51a7…415a: byte-identical to r1, so the worlds and personas are unchanged.
- Source hashes:
  - `deficiency.extended.yaml` 4e171b6a0ea019a0567d649ba15053e5df88c7249552e959040addf27ab798a5 — CHANGED from 177415da…, so every charter-global section is re-derived below.
  - `task_tools.py` da468bc4…0dd1 — unchanged, so action_binding_and_uuids (tool part) carries forward from revision_1 by these hashes.
- Read in addition: `rework_claims_r2.md`, used only as a list of item ids to check.

### policy_conflict_scan (r2)
- Base copy still byte-identical to products/deficiency.yaml.
- Policies, targets, subjects, triggers and the scope partition are unchanged ({P1,P2} | {P3,P4,P5}).
- P5's edge is re-declared `state_gate`. No new cross-category read or tool.

### rule_compute_equivalence (r2)
- mech.py: every compute_basis quote is verbatim in its rule; every binding has a basis; baseline.rule / replaced_by / policy_source are verbatim.
- New and changed reads:
  - P4: si_lump_count, si_lump_read = MAX, si_band_min, and `result = … if si_lump_count >= 1 else si_band_min`.
  - P5: ss_amount_read = MAX, ss_amount with no fallback (MAX of no rows = 0.0, so result = 0.00).
  - Both match their new rule sentences.
- Month counts: every "whole month" sentence of P1–P5 now carries "the difference in calendar months, less one when the later date's day of the month is below the earlier date's" (sweep: no whole-month sentence lacks it), which is exactly MONTHS(). The earlier probes (03-31→09-30 = 5; 01-31→02-28 = 0) now follow from the rule words. No conflict with the base rolling-12 measure on the probed month-end cases (10-31→10-30, 03-31→02-28, leap 02-28→02-29).
- O2 closed: P2 "any smaller count (none, or fewer once returns are taken off)", P5 "any smaller count adds none".
- P3 missing-figure sentence matches compute.
- New sentence in P2, P4 and P5 rules: "No two arrangements of an account break on the same day, since an account has only one arrangement in force at a time."
  - P2: no compute_basis quotes it (a framing fact supported by the one-arrangement lifecycle; observation O12).
  - P4 and P5: it sits in baseline.rule (see R-BASELINE).

### action_binding_and_uuids (r2)
Carried forward from revision_1 (task_tools.py hash unchanged; targets unchanged). No factor id is a substring of a tool name.

### prerequisite_graph (r2)
- Edges:
  - P2→P1 value_input pi_balance (unchanged).
  - P4→P3 value_input si_lump_read (unchanged).
  - P5→P4 now `kind: state_gate`, `gate: deficiency_settlement.settlement_offer_accepted`. That is a real base eligibility (applies_to deficiency_settlement_started), and the condition (installment_settlement accepted) is narrower than the base gate but equal to P5's own sentence.
- Acyclic; resolved_by bodies produce the states.
- P4 `effect` still says "without it the lump-sum figure is zero". True of the binding (MAX of no rows = 0.0), but no longer of the rule, which now sends that state to the band minimum. Stale general text: observation O13.

### prerequisite_sentences (r2)
- E1, E2 and E3 are unchanged verbatim and pass the four-point test as in revision_1.
- E2 now coexists in P4's rule with a carve-out sentence that prices the very state E2 waits on: R-ABSENT (P4, re-opened form) below.

### override_declarations (r2)
- P1 and P2 overwrites are unchanged in substance. P3, P4 and P5 have `[]`.
- P4's carve-out figure ("the band minimum the settlement rule sets: the greater of min_installment_settlement_pct percent of the balance … and settlement_floor_usd") is at or above the base minimum, so there is no base conflict.
- But the carve-out calls it the minimum "the settlement rule sets", while base lowers that minimum by hardship_extra_discount_pct with a documented hardship. This feeds the second reading below.
- P5's nil clause agrees with base settlement_offer_accepted (no start).

### factor_ladders (r2)
- Factor sets, effects, ladders, bindings and baselines are unchanged except for the O2 tier wording. Mechanical independence re-run (xf.py): only assembly bindings read factor outputs; si_band_min reads no factor binding.
- The all-pairs method tables of revision_1 still hold (formulas unchanged).
- Realism judgments unchanged (O10, O11 stand).
- New: R-BASELINE below.

### findings (r2)
Round-1 RED status:
- **R-TIE: CLOSED.**
  - P4 si_lump_read and P5 ss_amount_read are now MAX, and the rule reads "the largest such amount where the account carries more than one".
  - Same-clock probes: rule and compute both give 4000.00 for lump offers 3797.68/4000.00, and both give 5361.92 for acceptances 5361.92/5000.00.
  - No LATEST over created_at remains in the charter. LATEST over broken_date stays tie-free by the stated fact.
- **R-MONTHEND: CLOSED** for every member listed in revision_1 (sweep above).
- **R-ABSENT member P5: CLOSED.** "an account carrying none has no settlement the settlement rule allows to start, and its settlement installment is nil (0.00)" agrees with the base gate. There is a record test plus a refusal, and no second figure a write could use.
- **R-ABSENT member P4: NOT CLOSED (changed form) — SOURCE-POLICY RED.**
  - Two sentences of P4's own rule address the same state with different conclusions:
    - E2: "An installment settlement amount is not worked out until the account carries a lump-sum settlement offer dated today."
    - The new carve-out: "An account carrying no lump_sum_settlement offer dated today is outside the schedules of this policy, and its installment settlement amount is the band minimum the settlement rule sets: the greater of min_installment_settlement_pct percent of the balance on the offer date, rounded half up to the cent, and settlement_floor_usd, never more than the balance."
  - Compute agrees with the carve-out (`result … else si_band_min`).
  - In the no-offer state, E2 says wait and resolve P3 first, while the carve-out gives a definite, base-legal figure now. The prerequisite stops being a prerequisite: the policy itself prices the unresolved state.
  - Demonstration on task 1's world (alt-path probe t1_alt.py): P4 on the opening world = 4491.88 (55% × 8167.06). Accept 4491.88, then P5 on that acceptance = 1122.97. That is a complete, rule-grounded alternative to the three-write gold path.
  - A third figure exists for this state: the base hardship minimum, 45% → 3675.18 → P5 918.80, because the carve-out claims to be "the band minimum the settlement rule sets" and the account carries an unemployment_determination offer within the look-back.
  - Bears on: task 1.
- **New R-BASELINE — SOURCE-POLICY RED (XF 5).**
  - The baseline must be the standard method with default values, silent about every variation. The P4 and P5 `baseline.rule` now begin with "No two arrangements of an account break on the same day, since an account has only one arrangement in force at a time."
  - That sentence is not part of either standard method. No compute_basis of P4 or P5 quotes it. It concerns broken-arrangement records that only a factor reads: P4 premium_method (si_broken_date) and P5 count_method (ss_plan_broken).
  - So the computation document rendered from baseline.rule is not silent about the variation; it points the reader at broken arrangements.
  - Members: P4 baseline.rule, P5 baseline.rule. Non-members: P1, P2 and P3 baseline.rule (each is only the standard-method sentence).
  - Bears on: task 1's rendered computation documents; no scored value.
- Observations: O12 (P2 framing sentence quoted by no binding), O13 (stale P4 effect text). O1, O3–O11 are carried forward. O2 and the P3 missing-figure observation are closed.

## closing_checklist (revision_2)
- Files: 0.md, 1.md and _difficulty.md each carry revision_2 appended below an untouched revision_1.
- Scopes, tools and uuid8s: unchanged, disjoint, complete.
- Trees:
  - Task 0: one prerequisite, value_input, user write.
  - Task 1: two prerequisites, P5←P4 state_gate and P4←P3 value_input (>= 1 value_input), user write.
  - The graph is acyclic.
- Factors: counts, labels, weights and baselines are unchanged and re-verified (all equal to GT).
- Round-1 REDs: R-TIE closed, R-MONTHEND closed, R-ABSENT P5 closed; **R-ABSENT P4 not closed (changed form)**.
- New: **R-BASELINE** (P4 and P5 baseline.rule carry the broken-arrangement tie sentence).
- **Not closed.** Task 1 is RED, and the charter has open REDs R-ABSENT (member P4) and R-BASELINE (members P4, P5).
VERDICT revision_2: task0=PASS task1=RED charter=R-ABSENT,R-BASELINE

## revision_3

## charter_global_frozen (revision_3)
- Frozen 2026-10-20, before any round-3 task file was read.
- Entry gate: worklog last line "REWORK round 3: gates 7/7 green".
- Round-3 gate snapshot (`snapshot.sh deficiency_balance_resolution 3`, 2026-10-20T06:40:12): all seven gates OK.
- Masked views r3/0.json 0158a870…a9af and r3/1.json 3f4a51a7…415a: identical to r1/r2, so the worlds are unchanged and no fresh blind freeze is needed.
- Source hashes:
  - `deficiency.extended.yaml` 17b268cb406b930c49244527d89698ed98d26d01d1bac8437d166f9747749c78 — CHANGED, so all charter-global sections are re-derived.
  - `task_tools.py` da468bc4…0dd1 — unchanged; tool and uuid conclusions carry forward.
- Claims file `rework_claims_r3.md` was read by item id only.

### re-derived sections (r3)
- **policy_conflict_scan:** base copy byte-identical. Policies, targets, scopes and graph unchanged (P2→P1 value_input; P4→P3 value_input; P5→P4 state_gate on settlement_offer_accepted).
- **rule_compute_equivalence:**
  - mech.py: every compute_basis quote is verbatim.
  - Every baseline.rule sentence is a sentence of its rule (per-sentence check; P5's baseline is two non-adjacent rule sentences, each verbatim).
  - P4: `si_band_min` removed; `result = … if si_lump_count >= 1 else 0`. That matches the new sentence "While the account carries no lump_sum_settlement offer dated today, no installment settlement is offered on it: its installment settlement amount is not yet worked out and stands at nil (0.00)", which is quoted by result's basis.
  - P5 nil sentence quoted by ss_amount, and MAX of no rows = 0 gives 0.00.
  - Every whole-month sentence still carries the MONTHS() definition.
  - Exception: P2's standalone sentence "No two arrangements of an account break on the same day, since an account has only one arrangement in force at a time." is quoted by no binding (see R-SHAREDCONV).
- **prerequisite_sentences / graph:**
  - E1–E3 unchanged and pass the four-point test.
  - P4 now has a single answer for E2's waited-on state (defer: nil, no offer). E2 forces P3 again: no rule sentence prices the no-offer state.
  - P4 `effect` now reads "without it no installment settlement is offered and the amount stands at nil", which matches the rule. O13 closed.
- **override_declarations:** unchanged (P1/P2 declared; P3–P5 `[]`). No P4 or P5 figure lies below the base minimum or starts without acceptance.
- **factor_ladders:** unchanged.
  - xf.py: no factor reads another factor's binding.
  - The tie clause now sits inside P4 premium_method's sentence and P5 count_method's sentence. Each is the only factor of its policy reading broken arrangements. The P4 and P5 baseline.rule are now silent about broken arrangements.
  - All-pairs method tables from revision_1 still hold; realism unchanged.
- **XF sweep (points 1–31):** pass except point 6 (R-SHAREDCONV).
  - Point 12 re-probed: same-clock second offer and acceptance → MAX, rule = compute. No-offer and yesterday-only offer → nil. No acceptance → nil.
  - Point 25: the nil cases are carved out by a record test plus "no installment settlement is offered" / "no settlement … allows to start".

### findings (r3)
- **R-ABSENT P4: CLOSED.**
  - The carve-out and si_band_min are gone. On task 1's opening world, P4 = 0 (nil, not offered) and P5 = 0 (nil, no start).
  - The alternative path (accept without a lump-sum offer) now has no rule basis: the accept-then-start probe yields only nil figures.
  - Class sweep: P2 has no absent-state figure; P1 and P3 have no prerequisite. No other member.
- **R-BASELINE: CLOSED.** The P4 and P5 baseline.rule carry only the read and standard-method sentences. P1–P3 are unchanged and clean.
- **New R-SHAREDCONV — SOURCE-POLICY RED (XF 6, "no single convention sentence serves several factors"; also the XF 16 reverse sweep, a rule sentence with no compute counterpart).**
  - Member P2: the standalone tie-fact sentence underwrites the "latest … with offer_status broken" reads of two factors, installment_basis_method (pi_plan_broken / pi_plan_accepted / pi_plan_installment) and rebreak_surcharge (pi_broken_date). No binding quotes it.
  - This was recorded as observation O12 in revision_2. The round-3 point-6 re-check reclassifies it, because round 3 moved the same sentence into the single factor that needs it in P4 and P5, while P2's copy still serves two factors from one place.
  - Non-members:
    - P1: its sentence defines the shared plain selection "the latest broken arrangement" (dp_broken_date), which XF 2 permits.
    - P3: none.
    - P4 and P5: the clause sits in one factor sentence.
  - Consequence: the sentence cannot be placed in either of P2's factor documents without leaving the other factor's document without it. No scored value is affected.
- Observations carried forward: O1, O3–O11.

## closing_checklist (revision_3)
- All three files carry revision_3 below untouched earlier revisions.
- Scopes, tools and uuid8s: unchanged, disjoint, complete.
- Trees:
  - Task 0: one prerequisite, value_input, user write.
  - Task 1: two prerequisites, one value_input and one state_gate, user write.
  - Acyclic.
- Factors: unchanged; every factor bears weight; baselines differ from gold. All equal to GT.
- Round-2 REDs: R-ABSENT (P4) CLOSED; R-BASELINE CLOSED.
- New: **R-SHAREDCONV** (XF 6 / 16, member P2 only).
- **Not closed** while R-SHAREDCONV is open. Both tasks pass on their worlds.
VERDICT revision_3: task0=PASS task1=PASS charter=R-SHAREDCONV

## revision_4

## charter_global_frozen (revision_4)
- Frozen 2026-10-20, before any round-4 task file was read.
- Entry gate: worklog last line "REWORK round 4: gates 7/7 green".
- Round-4 snapshot (`snapshot.sh deficiency_balance_resolution 4`, 2026-10-20T08:06:47): all seven gates OK.
- Masked views r4/0.json 0158a870…a9af and r4/1.json 3f4a51a7…415a: identical to r1–r3, so the worlds are unchanged.
- Source hashes:
  - `deficiency.extended.yaml` 1965b769eb59fa4a509bbe969f69202b4e26210cd3e2ba9fc9a6f6374bc4b33b — CHANGED, so all charter-global sections are re-derived.
  - `task_tools.py` da468bc4…0dd1 — unchanged.
- Claims file `rework_claims_r4.md` was read by item id.

### re-derived sections (r4)
- **Base copy:** byte-identical to products/deficiency.yaml.
- **Policies, targets, scopes, prerequisite graph, E1–E3 sentences and overwrites:** unchanged.
- **rule_compute_equivalence:**
  - mech.py: all compute_basis quotes are verbatim; every baseline.rule sentence is a rule sentence (per-sentence check).
  - Every whole-month sentence carries the MONTHS() definition.
  - No baseline.rule mentions broken arrangements.
- **Factor independence (xf.py):** only assembly bindings read factor outputs.
- **Re-evaluation on r4:** every figure is identical to revision_3.
  - Task 0: 336.34 / 122.41, with the same substitutions and baselines.
  - Task 1: 3797.68 / 5361.92 / 1340.48, with the same substitutions and baselines.
  - Absent-prerequisite probes: P4 nil without today's lump-sum offer; P5 nil without an acceptance.
- **XF sweep, points 1–31:** no member found.
  - Point 6 / 16 class sweep, sentence by sentence over all five rules:
    - Sentences quoted by no binding are only scope sentences (P1–P5 first sentences), the overwrite replaced_by (P1, P2), prerequisite sentences (E1, E2, E3), P2 "A plan offer states no down payment of its own…", and P3's hardship-document recording sentence. P3's sentence governs the tool's hardship_document argument, not a computed quantity.
    - No rule sentence is quoted by bindings of two or more factors.
    - The tie statement now occurs once inside each factor sentence that reads broken arrangements: P2 basis, P2 rebreak, P4 premium, P5 count. P1 keeps it in its plain shared-selection definition (XF 2).

### findings (r4)
- **R-SHAREDCONV (P2): CLOSED.** The standalone sentence is removed. The statement now closes the plan installment basis sentence (quoted by pi_hardship_docs … pi_basis) and the plan rebreak surcharge sentence (quoted by pi_broken_date, pi_since_break, pi_rebreak_pct). Compute is unchanged.
- No new defect. No regression of R-ABSENT, R-TIE, R-MONTHEND or R-BASELINE: re-probed and sentence-swept above.
- Observations carried forward: O1, O3–O11.

## closing_checklist (revision_4)
- Files: per-task files 0.md and 1.md plus _difficulty.md, each with revisions 1–4 appended in order and earlier text untouched.
- Scope: extended policies {P1,P2} | {P3,P4,P5} and their five tools, disjoint and complete. Each uuid8 is independent.
- Trees, both acyclic:
  - Task 0: one prerequisite (value_input) and a user write.
  - Task 1: two prerequisites (one value_input, one state_gate) and a user write.
- Factors: every computation has 4–6 factors (>= 2 parameter, >= 1 method). Each task has a multi-source and a cross-difficulty factor, seeded. Every factor bears weight. Every whole baseline differs from gold. All equal to GT.
- Gates: the instantiation-stage gates are re-run on this final form (round-4 snapshot, 7/7 OK).
- All four relationships PASS for both tasks. The charter has no open RED.
VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN

## revision_5

## charter_global_frozen (revision_5)
- Entry gate: worklog last line "REWORK round 5: gates 7/7 green".
- Round-5 snapshot (`snapshot.sh deficiency_balance_resolution 5`, 2026-10-20T10:11:58): all seven gates OK.
- Masked views r5/0.json 0158a870…a9af and r5/1.json 3f4a51a7…415a: unchanged worlds.
- Source hashes: `deficiency.extended.yaml` 9b65506c94b87f8c2288c8aca3a7d419ae36317625ec57b37342f0c6fbe04f9e (CHANGED → re-derived); `task_tools.py` da468bc4…0dd1 (unchanged).
- Read: `rework_claims_r5.md` (item ids) and `audits/render_source/deficiency_balance_resolution/render_r1.md`.
- Auditor disclosure: render_r1 RED-1 (the unordered hardship document when both ssa_award_letter and medical_disability_statement are present) is a defect my revisions 1–4 should have found under rule_compute_equivalence / XF 11–12. I noticed the two-document case while deriving revision_1, but never recorded it, so it was not routed. revision_4's CLEAN was wrong on that item.

### re-derived sections (r5)
- Base copy byte-identical. Policies, targets, scopes, graph, E1–E3, overwrites and factors unchanged.
- mech.py: compute_basis verbatim; baseline sentences are rule sentences; E1–E3 in their rules.
- xf.py: no factor reads another factor.
- Whole-month definition present in every whole-month sentence.
- Re-evaluation on r5: every figure is identical to revision_4 (task 0: 336.34 / 122.41; task 1: 3797.68 / 5361.92 / 1340.48; all substitutions and baselines; nil probes).

### render items
- **RED-1 CLOSED.** P3 now reads: "…records as its hardship document the document that reduction rests on, the ssa_award_letter where an offer within the hardship look-back carries one, otherwise the medical_disability_statement where an offer within the hardship look-back carries one, and otherwise the unemployment_determination; an offer without a hardship reduction records none."
  - The order is total over the reduction's own domain. Tier 1 (ssa or medical) gives the same reduction for either document, so only the recorded value needed the order.
  - Worlds: task 1 carries only unemployment_determination (gold argument unchanged). Task 0's historical lump offer recorded the medical statement, the only document then on file (consistent).
  - The sentence governs a tool argument and is quoted by no binding, as before.
- **Low note CLOSED.** P4 idle sentence: "…from the later of opened_date and last_payment_date to today, counted from opened_date when last_payment_date is empty". This matches `DAYS(MX(F('opened_date'), F('last_payment_date') or F('opened_date')), NOW)` and is quoted by si_idle_days and si_idle_pts.
- **Reworker's extra member CLOSED.** P5: "…the largest such amount where the account carries more than one, and the settlement is started under the offer that amount comes from". This fixes the start's arrangement_offer_id; it is quoted by ss_amount_read.

### class sweep, exhaustive

**(a) Rule sentences that select one of several record values:**

| policy | selection | how it is settled |
|---|---|---|
| P1 | the latest broken arrangement and its accepted_at / broken_date / installment_amount_usd | tie fact stated |
| P1, P3 | the recovery case and contract of the account | one row by recovery_case_id / contract_id |
| P2 | the latest broken payment_plan (basis) and the latest broken offer (rebreak) | tie fact in each sentence |
| P2, P4, P5 | the contract tier | single row |
| P3 | hardship document | now ordered |
| P4 | lump-sum figure | largest |
| P4 | latest broken (premium) | tie fact |
| P5 | settlement amount and the offer it is started under | largest, now bound |
| P5 | latest broken payment_plan (count) | tie fact |

Tool arguments: pay_restart / record_payment_plan_offer / accept take only the named account and one amount. record_lump_sum's hardship_document is now ordered. start's arrangement_offer_id is now bound.

- Residual, observation O14: two accepted installment_settlement rows with identical amounts would leave "the offer that amount comes from" unresolved.
  - It cannot arise in a consultation: the accept tool's id is make_id(account, type, amount, today), so a same-day repeat is the same row.
  - It needs a stale, never-started acceptance from an earlier day with an identical-to-the-cent amount.
  - The scored installment is identical under either row.

**(b) Empty-field and absent-record edges, every read:**
- last_payment_date: P4 idle, now stated. No other policy reads it.
- Absent broken arrangement: P1 run/make-good and P2 basis/rebreak "otherwise" tiers; P4 premium "no such broken arrangement"; P5 count "no such broken plan". All stated.
- Absent lump-sum offer today / accepted settlement: nil, stated.
- Contract absent: P2/P4 "every other credit tier"; P5 "every other contract". P1/P4 counts of 0 fall to the stated lowest bands.
- Book value / gross proceeds missing: P3, stated.
- Unproducible edges, observation O15. Compute falls to the fall-through, and no rule sentence prices them:
  - Empty accepted_at or installment_amount_usd on a broken arrangement (P1 run/make-good, P2 carry, P5 count): a broken arrangement was necessarily accepted and started under base deficiency_payment_plan / deficiency_settlement.
  - Absent recovery_method (P1 surrender, P3 route): every deficiency account opens from a sold recovery case with an enum recovery_method under base deficiency_opening.
- No other member.

### findings (r5)
- render_r1 RED-1: closed. Low note: closed. Extra P5 offer binding: closed.
- No remaining member of either class at RED.
- No regression: all figures, factor weights, trees, nil probes and the XF 1–31 sweep are re-checked.
- New observations: O14, O15. O1 and O3–O11 are carried.

## closing_checklist (revision_5)
- Files: revisions 1–5 appended in order in all three files.
- Scopes, tools, uuid8s, trees (acyclic; user write in each), factor floors and weights: unchanged and equal to GT.
- Gates: 7/7 on the final form (round-5 snapshot).
- All four relationships PASS for both tasks. No open charter RED.
VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

## revision_6

## charter_global_frozen (revision_6)
- Frozen before any round-6 task file was read.
- Entry gate: worklog last line "REWORK round 6: gates 7/7 green".
- Round-6 snapshot (`snapshot.sh deficiency_balance_resolution 6`, 2026-10-20T19:10:52): all seven gates OK.
- Masked views r6/0.json 96dad9f7…0408 and r6/1.json 387d6c33…44a4 (both worlds changed; fresh derivations frozen in 0.md and 1.md).
- Source hashes, both changed, so every section is re-derived:
  - `deficiency.extended.yaml` dee25036f312c21dd75db946cd4358e8db4a652184815c876078a32e9f77a52c;
  - `task_tools.py` efdae9f34fd8cf640add14f9e2eeda01e6f99f230956c90f1d9bb7f801a2ba27.
- Read: rework_claims_r6.md, audits/policy_kb/deficiency_balance_resolution/_difficulty.md (S1–S5), and docs/contract and docs/recovery:
  - late_charge_amount_computation, autopay_late_charge_relief, first_delinquency_late_charge_relief, late_charge_booking, late_charge_eligibility_and_limits, late_charge_base_amount_by_installment, state_late_charge_schedule;
  - surrender_fee_charge_basis, state_limits_on_surrender_fees, surrender_fee_vehicle_value_reduction, prompt_surrender_timing_credit, company_dropoff_lot_credit, agency_recovery_fee_* , low_value_vehicle_agency_fee_reduction, keyless_handling_charge_agency_recoveries, weekend_recovery_charge_agency_fee, storage_lot_rate_card, recovery_expense_charging_rules.

### re-derived sections (r6)
- Base copy byte-identical.
- Policies, targets, scopes, graph and E1–E3 unchanged.
- mech.py: verbatim quotes; baseline sentences are rule sentences; whole-month definition in every sentence.
- xf.py: no factor reads another factor.
- Charter change: P3 only.
  - (i) The hardship-document sentence now reads "A lump-sum offer records as its hardship document the hardship document the borrower hands in with the request for that offer; where the borrower hands in none, an offer whose amount carries a hardship reduction records the document that reduction rests on, the ssa_award_letter …, otherwise the medical_disability_statement …, and otherwise the unemployment_determination; an offer with neither records none."
  - (ii) The hardship-reduction sentence adds "the offers read are those already recorded on the account when the amount is figured, so a document handed in with the offer being made goes on file with that offer and counts only toward later figures". This matches compute, which reads the state before the write.
- Tool change: record_lump_sum's hardship_document description now reads "the hardship document recorded on the offer". No example values, and the body is unchanged.
- S5 closed: a first hardship document can now be recorded, and both worlds' first hardship-bearing offers reproduce under (i)+(ii) (see the task files).
- S2/S3 cross-product seeds: every re-priced row reproduces under the published contract/recovery rules (task files). The rows unchanged since revision_1 were re-checked against the same docs and still hold (agency fee 425.00 on task 1; storage by the lot rate card; transport, key, reconditioning, auction; interest splits; proceeds order). No member left.

### class sweep (r6)
**(a) Rule sentences selecting one of several values without a stated order.** All revision_5 members stay closed, plus one new member:
- **R-HANDIN — SOURCE-POLICY RED (render_r1 RED-1 class; XF 11–12).**
  - P3's new first clause, "records as its hardship document the hardship document the borrower hands in with the request for that offer", names a single document with no order when the borrower hands in more than one. The tool records exactly one enum value.
  - Demonstration: a borrower hands in an ssa_award_letter and an unemployment_determination with the request. The recorded document is either ssa_award_letter or unemployment_determination, with no rule basis to choose between them.
  - The choice moves later figures: a later lump-sum offer's hardship tier (10% of the balance vs. the jobless cap), P1's restart relief (3.0 vs 1.5 points) and the recorded argument itself.
  - A borrower handing in an SSA award letter together with a physician's disability statement is ordinary. Those two give the same later tiers, but still two values of the write argument.
  - Member: P3 hardship-document sentence, first clause. No other member: the reduction-based branch is ordered, and no other rule reads a customer-supplied document.
- Not affected: the scored arguments of either task (task 1's borrower hands in none; task 0 records no lump-sum offer).

**(b) Empty-field and absent-record edges:** unchanged from revision_5. O15 is unproducible.

### realism (P3 change)
- "A document handed in with the offer … counts only toward later figures" reads as a document-on-file-before-pricing practice. That is publishable.
- But a second lump-sum offer recorded the same day after the first already counts the document. Observation O16: a same-day re-quote earns the reduction the first quote was denied. This is not demonstrated unpublishable.
- db_schema's meaning of hardship_document ("supporting a hardship settlement") now also covers a document recorded without a reduction. Observation O17; the blueprint is frozen.

### findings (r6)
- S2, S3, S5: closed (S1 and S4: no action, as routed; S1 = O7, S4 = the CPI-seed observation).
- R-HANDIN: open (new).
- No regression of R-ABSENT, R-TIE, R-MONTHEND, R-BASELINE, R-SHAREDCONV, RED-1 or the idle-day note: re-swept.

## closing_checklist (revision_6)
- Files: revisions 1–6 in all three files.
- Scopes, tools, uuid8s and trees unchanged.
- Factor floors met; every factor bears weight on the re-priced worlds; baselines differ from gold; all equal to GT.
- Gates 7/7 (round-6 snapshot).
- Both tasks PASS on their worlds.
- **Not closed:** charter RED R-HANDIN (member: P3 hardship-document sentence, first clause).
VERDICT revision_6: task0=PASS task1=PASS charter=R-HANDIN

## revision_7

## charter_global_frozen (revision_7)
- Entry gate: worklog last line "REWORK round 7: gates 7/7 green".
- Round-7 snapshot (`snapshot.sh deficiency_balance_resolution 7`, 2026-10-20T19:57:41): all seven gates OK.
- Masked views r7/0.json 96dad9f7…0408 and r7/1.json 387d6c33…44a4: identical to r6, so the worlds are unchanged.
- Source hashes: `deficiency.extended.yaml` cb8adfadaaae06e0eac6fbfb43f9ccf408ad99619dc3c8db72651cf61397c1ea (CHANGED → re-derived); `task_tools.py` efdae9f3…ba27 (unchanged).
- Read: rework_claims_r7.md (item ids).

### re-derived sections (r7)
- Base copy byte-identical.
- mech.py: verbatim quotes; baseline sentences are rule sentences; E1–E3 in their rules; whole-month definition in every sentence.
- xf.py: no factor reads another factor.
- Only P3's hardship-document sentence changed.
- Re-evaluation on r7: every figure identical to revision_6:
  - task 0: 333.96 / 121.54; opening 132.80; sensitivities and baselines 554.27 / 130.22;
  - task 1: 3779.65 / 5337.02 / 1334.26; baselines 3657.73 / 4592.48 / 889.51;
  - nil probes unchanged.

### findings (r7)
- **R-HANDIN: CLOSED.** P3 now reads: "A lump-sum offer records one hardship document: where the borrower hands in one or more hardship documents with the request for that offer, it records the first of them in the order ssa_award_letter, medical_disability_statement, unemployment_determination; where the borrower hands in none, an offer whose amount carries a hardship reduction records the document that reduction rests on in the same order, …; an offer with neither records none."
  - The order is total for any set of handed-in documents. The demonstration case (ssa + unemployment) now records ssa_award_letter.
  - The handed-in branch takes precedence over the reduction branch, and that is stated.
  - "Hardship documents" are the three kinds of base hardship_documents_accepted, matching the tool enum.
- **Class sweep (a), exhaustive.** Every rule sentence or tool argument that picks one of several values:

| policy | selection | how it is settled |
|---|---|---|
| P1 | the latest broken arrangement (accepted_at / broken_date / installment) | tie fact |
| P1, P3 | recovery case and contract | one row by id |
| P2 | latest broken plan and latest broken offer | tie fact in each sentence |
| P2, P4, P5 | contract tier | single row |
| P3 | hardship document, handed-in branch | ordered |
| P3 | hardship document, reduction branch | ordered |
| P4 | lump-sum figure | largest |
| P4 | latest broken | tie fact |
| P5 | settlement amount and the offer it is started under | largest, bound; O14 residual unproducible in a consultation |
| P5 | latest broken plan | tie fact |

  - Customer-supplied values: the payment amount, the accepted amount and the channel are each single. No other member.
- **Class (b), empty-field edges:** unchanged; O15 unproducible.
- **Regression:** none. R-ABSENT, R-TIE, R-MONTHEND, R-BASELINE, R-SHAREDCONV, RED-1, the idle-day note and S2/S3/S5 were re-checked (worlds unchanged, figures identical).
- O16 and O17 stay observations.

## closing_checklist (revision_7)
- Files: revisions 1–7 in all three files.
- Scopes, tools, uuid8s, trees and factor floors unchanged; every factor bears weight; baselines differ from gold; all equal to GT.
- Gates 7/7 (round-7 snapshot).
- Both tasks PASS. No open charter RED.
VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN
