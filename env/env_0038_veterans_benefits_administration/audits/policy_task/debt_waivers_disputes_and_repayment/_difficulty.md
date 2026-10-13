# Policy-task audit — debt_waivers_disputes_and_repayment / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (Claude agent, erl-task-policy-audit), not the instantiating agent.
- Freeze time: 2026-10-06T03:34:01Z, the file birth time (written before any task's GT was revealed; nothing in this section derives from a revealed GT).
- Freeze hashes (sha256, recomputed by the auditor, equal to MANIFEST.sha256.txt):
  - `tasks/debt_waivers_disputes_and_repayment/debt.extended.yaml` = `51c719a13586bf0197ece16722cc341da3fac5fba2f104f129862b0d5ac0dd61`
  - `tasks/debt_waivers_disputes_and_repayment/task_tools.py` = `da2978bbf75a8d87efb79ae73b7b018d976325a09e422b1f6338f0a5c94b404b`
- Fields read for this section: `blueprint/blueprint.yaml` (difficulty claim), `blueprint/products/debt.yaml`, `blueprint/products/comp.yaml` and `pension.yaml` (variant parameters only), `blueprint/share_tools.py`, the extended charter, `task_tools.py`, and the DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (MONTHS / DAYS / within_months / LATEST / CPARAM / CFIELD / X-history).
- Masked and unread at freeze: every `tasks/*.json` field other than `frozen_time`, `user_scenario`, `initial_state` (read only through the orchestrator's masked views, hashes in MANIFEST); no earlier audit exists for this difficulty.
- Entry conditions (Step 0): the gate snapshot came with the brief (`/tmp/erl0038/views/policy_task/debt_waivers_disputes_and_repayment/GATES.txt`): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO (optional), SCOPE OK; check_traceability deferred to the KB stage. Masked views and their hashes were supplied. Entry conditions met.

### policy_conflict_scan

Base section: `diff` of lines 1-1194 of the extended charter against `blueprint/products/debt.yaml` shows them identical; the only difference is one trailing blank line before `extended_policies:`. The base copy is verbatim.

Extended policies (7), their write and the event they emit:

| policy | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- |
| debt_ext_plan_reinstatement_deposit | pay_plan_reinstatement_66656e17 (user) | amount | [] |
| debt_ext_waiver_request_amount | submit_waiver_request_4f8614a0 (user) | requested_amount | deposit (value_input, balance) |
| debt_ext_plan_request_term | record_repayment_plan_request_018c5870 (agent) | requested_term_months | waiver (value_input, waiver_fsr_requests) |
| debt_ext_plan_installment | start_repayment_plan_5152504c (agent) | monthly_amount | plan_request_term (value_input, months_requested) |
| debt_ext_reduced_withholding_proposal | record_reduced_withholding_request_043db99b (agent) | requested_amount | [] |
| debt_ext_reduced_withholding_amount | start_reduced_withholding_20dc00ef (agent) | monthly_amount | proposal (value_input, proposal) |
| debt_ext_compromise_offer_amount | submit_compromise_offer_8c2d0269 (user) | requested_amount | reduced_withholding_amount (value_input, monthly_withholding) |

Overlapping subjects:
- `debt_repayment_plan_requested` is the subject of both plan_request_term (request_kind repayment_plan) and reduced_withholding_proposal (request_kind reduced_withholding). They write different `request_kind`s and different quantities (`requested_term_months` vs `requested_amount`); the tools hard-code the kind. No collision.
- `debt_plan_started` is the subject of both plan_installment (method direct_payment) and reduced_withholding_amount (method benefit_withholding). Different tools, different method; base `debt_evt_repayment_plan` covers both ("repay in monthly installments paid directly, or to have the monthly withholding ... reduced"). No collision.
- Every base provision the extended rules don't override is inherited. That covers the waiver window and fraud bar, single-pending-request exclusivity (plan requests are exempt), "a repayment plan request is taken only on a debt whose status is active", FSR for reduced withholding, compromise authority max, and the Treasury-referral bar on plans and compromise offers. None of the task tools weakens any of these: the tools carry no logic.

Time anchors: notice date (`DAYS(notice_date, NOW)`) against waiver window (180 d for every type except Home Loan 365 d) and hold window (30 d); plan approval date (`MONTHS(approval, NOW)`); rolling "calendar months counted back from today" windows implemented by `within_months` (MONTHS(d, NOW) in [0, N)). Used the same way in every policy.

Cross-category read boundaries: comp (deposit, waiver, term, installment) and pension (proposal, reduced-withholding amount, compromise), read only through CPARAM/CFIELD/X-history on the customer's own holdings. No policy reads another difficulty's write.

Claimed scopes: the two chains {deposit, waiver, plan_request_term, plan_installment} and {proposal, reduced_withholding_amount, compromise} are disjoint and together cover all 7 extended policies. Tasks 0 and 1 confirm these scopes by their persona and seed. Observation: the difficulty claim in `blueprint.yaml` lists `debt_dispute_filed`, `debt_collection_held` and `debt_overcollection_refunded`. No extended policy or task tool covers them, so these three event types are claimed but untested. This is a coverage note, not a conflict.

Conflicts found: see findings G1 and G2 (the base-vs-extended undeclared overrides).

### rule_compute_equivalence

I swept each policy's `compute` against `compute_basis` and the `rule` in both directions:

- **plan_reinstatement_deposit**: every binding is quoted. `months_due` = "counted in whole calendar months from the approval date to the day of the payment" (MONTHS). `installments_counted`, `installment_value`, `deposit_floor`, `deposit_pct` and `excess_credit` are all three-tier, and each tier is a rule sentence. Order: product, then floor, then percent, then credit, then max(0), with one rounding at the end. Exact.
- **waiver_request_amount**: capacity 10%/5% of the veteran-alone rate (or the plan minimum), horizon 24/18/12, horizon_counted (minus elapsed months / minus 1 / all), credit (whole / 50% / none), result max(0, balance − (capacity × months − credit)) rounded once. Exact. One extra conjunct: compute adds `comp_monthly_rate > 0` to the capacity tier. The rule implies it ("of that award's monthly veteran-alone rate"), and every comp variant carries a rate, so nothing diverges. Observation O1: the rule caps the result at zero but not at the balance (see the task files).
- **plan_request_term**: longest_term 60/36/12, months_run (elapsed / missed count / 0), rating cut 6/3/0, pending cut 4/2/0, result max(1, …). Exact.
- **plan_installment**: spread_balance (balance − asked / balance − 50% asked, rounded / balance), spread_months (−1 / −2 / as stated), four rates acting on one quotient, ceil to the cent once, then the plan minimum floor. Exact.
- **reduced_withholding_proposal**: one divergence, see **G3**. The rule's first two starting-figure tiers require "the debtor holds a running Veterans Pension award paid monthly", but compute tests `pension_payment > 0`, where `pension_payment` = XLATEST over all of the customer's pension monthly payments with no status filter. care/offset/denial rates and the final ceil/floor are exact.
- **reduced_withholding_amount**: approved_figure (75% ceil / proposal − minimum / proposal), assets 90/95/100, income 92/96/100, history 95/98/100, ceil once, then the floor. Exact.
- **compromise_offer_amount**: recovery_months 36/48/60, recovery_value (PV at 0.5% a month / simple −6% / undiscounted, with "outstanding balance" defined in the rule as original − offsets − direct payments), cost 2/10/0, hardship 90/95/100, rate-cut 85/95/100, notice 97/94/100. The order is cost, then the multipliers, then the cap at the balance, rounded once. Exact.

Every factor's ladder tier is a rule sentence and a branch of its `decides` binding, and vice versa. No tier lives only in compute. Apart from G3, compute invents no basis and the rule makes no empty promise.

### action_binding_and_uuids

- `(target_tool, computes)`: 7 distinct pairs, each claimed by exactly one policy. Each docstring admits one business reading of its write. Owners: deposit, waiver and compromise are the debtor's signed or authorized acts (`owner=user`), matching base "Submitting the waiver request and the Financial Status Report is the debtor's own act" and the extended rules' "signed by the debtor".
- Tool bodies: each makes one `ctx.create`/`ctx.update` with no `if`, no status or eligibility check and no error path. The tools judge nothing (see each task's problem_chain).
- Docstring sequence words (observation O2):
  - `record_repayment_plan_request_018c5870` says "proposes no installment (the installment is set when a plan starts)". This describes another action, plan start, as following it, a weak ordering hint consistent with the declared edge plan_installment ← plan_request_term.
  - `pay_plan_reinstatement_66656e17` uses "after the payment" only for its own receipt.
  - `pay_plan_reinstatement_66656e17` says the payment "reinstates a repayment plan cancelled for missed installments", but its effect leaves the debt `active` with no plan terms. The label promises an effect the write does not have.
  - Neither hint names a tool or another problem's id.
- uuid8s: 66656e17, 4f8614a0, 018c5870, 5152504c, 043db99b, 20dc00ef, 8c2d0269. None is reused, no two share a prefix, and they are not sequential. Observation O3: `5152504c` decodes byte-wise to ASCII "QRPL" and `66656e17` to "fen"+0x17. Four uppercase-letter bytes from a random generator has probability ≈1e-4, which suggests hand-chosen values. This does not show batch derivation, so it is not a red.

### prerequisite_graph

- Every policy has a `prerequisite` field: `[]` on deposit and proposal, one edge each on the other five.
- Every `problem` points at an extended policy id in this file, never at a base policy or at itself. The graph is two chains, deposit → waiver → plan_request_term → plan_installment and proposal → reduced_withholding_amount → compromise. It is acyclic.
- Each `policy_source` is located verbatim in its own policy's `rule`. I checked all five by string search; every one is the second or fourth sentence of its rule.
- `form: state` on all five, and no `fallback_reason`, as required.
- `resolved_by` equals the depended-on policy's `target_tool` on all five.
- `kind: value_input` on all five, and each `gate` is a real compute binding: `balance`, `waiver_fsr_requests`, `months_requested`, `proposal`, `monthly_withholding`.
- `condition` vs sentence: waiver ← deposit adds "the outstanding balance and the direct payments of the last six months reflect it", which elaborates the effect without strengthening the state. reduced_withholding_amount ← proposal adds "states the monthly withholding proposed", which every such request does because the tool's argument is required. The others match.
- No authoring-viewpoint phrasing ("in this task", "at the opening") appears in any `prerequisite` text.

### prerequisite_sentences

Four-point test, per edge:

1. **waiver ← deposit**: "The amount a waiver request asks VA to waive is fixed only after the debt's ledger carries the reinstatement deposit owed on any repayment plan of the debt that was cancelled for missed installments."
   - Connective: "only after". The sentence is conditional ("any … cancelled") and names no tool, id or snake_case token.
   - The state is named with the depended-on rule's business term ("reinstatement deposit") rather than a ledger word ("direct payment"). Observation O4. Exactly one write of the difficulty posts a direct payment: `pay_plan_reinstatement_66656e17`. Single reading.
   - Derivation: the debt shows a granted repayment_plan decision and is `active` with plan fields reset, so the plan was cancelled. The waited-on deposit is the deposit policy's own subject ("may pay a reinstatement deposit by direct payment"), so the reader goes to the deposit policy.
2. **plan_request_term ← waiver**: "The number of months on a repayment plan request is fixed only after the debt carries a waiver request, received in the last six months, with the debtor's signed Financial Status Report attached."
   - Connective: "only after". The state uses table words: waiver request, received, Financial Status Report.
   - Exactly one writer, `submit_waiver_request_4f8614a0`. Compromise offers carry an FSR but are not waiver requests. Single reading.
   - **Unconditional**: it binds every plan request. See G1 and G4.
3. **plan_installment ← plan_request_term**: "A repayment plan's monthly installment is not fixed until the debt carries a repayment plan request received on the day the plan starts, stating the number of months the plan is to run."
   - Connective: "not … until". Table words.
   - One writer, `record_repayment_plan_request_018c5870`. The reduced-withholding request shares event_type `debt_repayment_plan_requested` but states no months, so "stating the number of months" excludes it. Single reading.
4. **reduced_withholding_amount ← proposal**: "Reduced withholding does not start on a debt until the debt carries a reduced-withholding request received on the day it starts."
   - Connective: "does not … until". One writer, `record_reduced_withholding_request_043db99b`. Single reading.
5. **compromise ← reduced_withholding_amount**: "The lump sum a compromise offer puts forward is worked out only after the debt carries an approved reduced monthly withholding from the debtor's benefit payments."
   - Connective: "only after". One writer, `start_reduced_withholding_20dc00ef`; `start_repayment_plan` sets method direct_payment, not withholding. Single reading.
   - **Unconditional**: it binds every compromise offer. See G2.

Further checks:
- No rule restates another problem's prerequisite sentence, and no depended-on rule restates the sentence that waits on it.
- No rule names another task tool or another policy id.
- No base rule sentence grounds an edge.
- No rule states a cross-problem order outside these five edges. plan_installment's spread_balance reads the waiver request, but as a tier, and the order is already implied transitively through plan_request_term.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry:

- **deposit** (refs debt_agg_collection_order, debt_evt_repayment_plan; overwrite []):
  - Its "applied to that debt" follows "A direct payment the debtor designates for a specific debt is applied to that debt".
  - Re-figuring at "current balance divided by the cancelled plan's number of months, rounded up to the cent" follows the base installment formula.
  - Cancellation, "full offset resumes" and "pay off early without penalty" are untouched.
  - The deposit is a new payment kind that base neither grants nor forbids. No conflict.
- **waiver_request_amount** (refs debt_evt_waiver, debt_excl_single_pending_request; overwrite []):
  - Base governs timeliness, completeness (FSR), the fraud bar, the hold, grant and refund, but never the amount asked. Extended fixes the amount and follows "complete only with a FSR" ("goes in with the debtor's Financial Status Report attached").
  - Its deposit gate adds a precondition to *when* the amount is fixed. Base states only necessary conditions for a waiver (timely, FSR), never "any timely debtor may file", so no affirmative base sentence is contradicted.
  - Realism observation O5: real VA practice never conditions a waiver request on first paying plan arrears.
- **plan_request_term** (ref debt_evt_repayment_plan; overwrite []): **undeclared override, G1.** Base: "a plan of up to plan_max_months_without_fsr months is approved on request". Extended: the months on any plan request are "fixed only after the debt carries a waiver request … with the debtor's signed Financial Status Report attached". Other sentences ("taken only on a debt whose status is active", "a longer plan is not available") are followed: the max(1, …) result never exceeds 60.
- **plan_installment** (ref debt_evt_repayment_plan; overwrite declares the installment clause):
  - The declared `superseded_clause` / `replaced_by` cover the installment formula, including the sub-balance spreading and the rates.
  - The first-month convention ("the calendar month after the month in which it starts") sits beside base "The first installment is due plan_first_installment_due_days calendar days after approval". In worlds where approval + 30 days crosses two month boundaries (approval Jan 31 → due Mar 2) the two can disagree. They govern arguably different quantities (plan month vs due date), and no task world reaches that edge. Observation O6.
- **reduced_withholding_proposal / reduced_withholding_amount** (ref debt_evt_repayment_plan; overwrite []):
  - Both follow "Reduced withholding is approved only with a Financial Status Report and never below reduced_withholding_min_monthly". Both floors are at the minimum, and the FSR requirement is inherited.
  - The extended "A Financial Status Report reaches a debt only with a request the debtor signs" is consistent with this.
- **compromise_offer_amount** (refs debt_evt_compromise, debt_excl_single_pending_request; overwrite []): **undeclared override, G2.** Base: "A debtor may offer a lump sum smaller than the balance to settle a debt. An offer is considered only with a Financial Status Report …". Extended: the lump sum "is worked out only after the debt carries an approved reduced monthly withholding from the debtor's benefit payments". The authority max, FSR and hold sentences are followed.

### factor_ladders

Per policy: factors and effect label; how many tiers are reachable among the customers who can reach that policy's write; and whether every tier is stated in the rule. Every ladder declares three tiers, each stated in the rule with its condition and value or method, and each implemented in compute. No two tiers of any ladder share a value or method.

| policy | factor | label | multi-source tiers | cross_difficulty | structural verdict |
| --- | --- | --- | --- | --- | --- |
| deposit | installments_counted | method (1 / all due / due − paid: distinct algorithms) | yes (payments × date span) | — | ok |
| deposit | installment_value | method (re-figure / plan minimum / approved) | yes (plan request FSR × balance; balance × payments) | — | ok |
| deposit | deposit_floor | parameter 450/200/25 | yes (approval date × comp award) | comp | ok |
| deposit | deposit_pct | parameter 55/80/100 | yes (comp rating × notice) | comp | ok (realism O7) |
| deposit | excess_credit | parameter whole / 50% / 0 | yes (payments × notice) | — | ok |
| waiver | monthly_capacity | parameter 10% rate / 5% rate / 25 | no: "AND a monthly veteran-alone rate" is always true of a rated award (O8) | comp | ok as single-source |
| waiver | horizon_months | parameter 24/18/12 | yes (notice × balance) | — | ok |
| waiver | horizon_counted | method (− elapsed months / − 1 / none) | yes (plan decision × status) | — | ok |
| waiver | repaid_credit | parameter whole / 50% / 0 | no | — | ok |
| plan_request_term | longest_term | parameter 60/36/12 | nominal | — | **RED, G4**: the waiver conjunct holds of every customer who reaches this write; the fall-through is unreachable |
| plan_request_term | months_run | method (elapsed / missed count / 0) | yes | — | ok |
| plan_request_term | rating_cut | parameter 6/3/0 | no | comp | ok |
| plan_request_term | pending_cut | parameter 4/2/0 | no | — | ok |
| plan_installment | spread_balance | method (− asked / − 50% asked, rounded / none) | yes (waiver × notice) | — | label borderline (O9) |
| plan_installment | spread_months | method (− 1 / − 2 / none) | yes (plan decision × comp award) | comp | **RED, G5**: mislabelled, the tiers only substitute k into months − k |
| plan_installment | uplift_pct | parameter 110/105/100 | no | comp | ok |
| plan_installment | relief_pct | parameter 95/90/100 | yes (comp payments × rating) | comp | ok |
| plan_installment | restart_pct | parameter 105/115/100 | yes (plan decision × direct payment) | — | ok (realism O7) |
| plan_installment | notice_pct | parameter 98/99/100 | yes (notice × fraud finding) | — | ok (realism O7) |
| proposal | starting_figure | method (10% pension / 25% pension / balance ÷ 60) | yes (pension payment × FSR request) | pension | ok; rule/compute drift G3 |
| proposal | care_pct | parameter 70/80/100 | no | pension | ok |
| proposal | offset_pct | parameter 90/95/100 | no | — | ok |
| proposal | denial_pct | parameter 85/95/100 | yes (decision × FSR request) | — | ok |
| rw_amount | approved_figure | method (75% ceil / proposal − 25 / proposal) | yes (pension payments × FSR request) | pension | ok |
| rw_amount | assets_pct | parameter 90/95/100 | no (pension award) | pension | ok |
| rw_amount | income_pct | parameter 92/96/100 | no (pension award) | pension | ok |
| rw_amount | history_pct | parameter 95/98/100 | yes (decision × offsets/original) | — | ok |
| compromise | recovery_months | parameter 36/48/60 | no: category and net worth sit on one pension award row | pension | ok |
| compromise | recovery_value | method (PV / simple −6% / undiscounted) | nominal | — | **RED, G6**: "months of recovery at least the discounting minimum" holds of every customer; the fall-through is unreachable |
| compromise | cost_pct | parameter 2/10/0 | nominal | — | **RED, G7**: "not referred to Treasury" holds of every customer who reaches this write; the reachable fall-through (1–2 offsets → 0%) is an unreal treatment |
| compromise | hardship_pct | parameter 90/95/100 | yes | — | ok |
| compromise | rate_cut_pct | parameter 85/95/100 | no | pension | ok |
| compromise | notice_pct | parameter 97/94/100 | yes (notice × fraud) | — | ok |

Surviving counts per computation, after striking the RED factors:

| computation | surviving factors | parameter | method | meets 4–6 / ≥2 parameter / ≥1 method? |
| --- | --- | --- | --- | --- |
| deposit | 5 | 3 | 2 | yes |
| waiver | 4 | 3 | 1 | yes |
| plan_request_term | 3 (longest_term struck) | 2 | 1 | **no: fewer than 4** |
| plan_installment | 5 (spread_months struck as mislabelled) | 4 | 1 (spread_balance, accepted as borderline) | yes |
| proposal | 4 | 3 | 1 | yes |
| rw_amount | 4 | 3 | 1 | yes |
| compromise | 4 (recovery_value and cost_pct struck) | 4 | 0 | **no: no method** |

Cross-difficulty factors:
- Chain {deposit, waiver, term, installment} reads comp through deposit_floor, deposit_pct, monthly_capacity, rating_cut, spread_months, uplift_pct and relief_pct.
- Chain {proposal, rw_amount, compromise} reads pension through starting_figure, care_pct, approved_figure, assets_pct, income_pct, recovery_months and rate_cut_pct.

Multi-source factors exist in both chains: deposit_floor and deposit_pct; approved_figure, denial_pct and hardship_pct.

Realism (judged against VA Debt Management Center practice):
- Plausible: tiers that weigh compensation rating or pension income, net worth, care level, prior offsets and prior waiver denial for ability-to-pay or hardship quantities. They mirror what an FSR captures (38 CFR 1.911(c)/1.917, 31 CFR 902.2: ability to pay, present value of future collections, cost of collection).
- Unreal: tiers whose condition restates the write's scope (G4, G6, G7) and gates no VA office applies (G1, G2).

### findings

**G1 — SOURCE-POLICY RED (undeclared override and internal contradiction; bears on task 0)**
- Symptom: the plan_request_term rule makes a waiver request with an FSR a precondition of every repayment plan request, contradicting base, while its own ladder and baseline still compute a term for a debtor without one.
- Root cause: the prerequisite sentence is written unconditionally. `overwrite: []`.
- Evidence:
  - Base `debt_evt_repayment_plan`: "a plan of up to plan_max_months_without_fsr months is approved on request, and a plan of up to plan_max_months_with_fsr months only with a Financial Status Report".
  - Extended `debt_ext_plan_request_term.rule`: "The number of months on a repayment plan request is fixed only after the debt carries a waiver request, received in the last six months, with the debtor's signed Financial Status Report attached."
  - Same rule, fall-through: "…otherwise it is the longest plan approved without a Financial Status Report"; `baseline.rule`: "The number of months on a repayment plan request is the longest plan approved without a Financial Status Report, and nothing is taken off it".
- Demonstrated consequence, situation: an active debt with no waiver request, whose debtor asks for a 12-month plan.
  - Base: approved on request.
  - Extended gate: the months cannot be fixed, so no plan request can be recorded, and plan_installment's own gate then blocks the plan.
  - Extended ladder and baseline: 12 months.
  - Three conclusions for one situation.
  - Realism: VA DMC grants repayment plans on request and never requires the debtor to ask for forgiveness first.
- Affected: `debt.extended.yaml` → `debt_ext_plan_request_term` (`rule`, `prerequisite[0].policy_source`, `overwrite`, `factors[longest_term]`, `baseline`).

**G2 — SOURCE-POLICY RED (undeclared override; bears on task 1)**
- Symptom: every compromise offer is made to wait on an approved reduced withholding from benefit payments.
- Root cause: the prerequisite sentence is unconditional. `overwrite: []`.
- Evidence:
  - Base `debt_evt_compromise`: "A debtor may offer a lump sum smaller than the balance to settle a debt. An offer is considered only with a Financial Status Report showing the debtor cannot pay the full amount within a reasonable time."
  - Base `debt_interact_benefit_lines`: "a debtor with no running award is billed for direct payment".
  - Extended `debt_ext_compromise_offer_amount.rule`: "The lump sum a compromise offer puts forward is worked out only after the debt carries an approved reduced monthly withholding from the debtor's benefit payments."
- Demonstrated consequence, situation: a Home Loan Guaranty debtor with no running VA benefit who offers a lump sum with an FSR.
  - Base: the offer may be made and is considered.
  - Extended: the lump sum can never be worked out, because there are no benefit payments to withhold from. Its compute gives `monthly_withholding = 0`, so the lump sum is 0.00.
  - Realism: compromise under 38 CFR 1.918/FCCS has no reduced-withholding precondition.
- Affected: `debt_ext_compromise_offer_amount` (`rule`, `prerequisite[0].policy_source`, `overwrite`).

**G3 — SOURCE-POLICY RED (rule/compute drift; charter-global, no consequence on task 1's world)**
- Evidence:
  - Rule: "when the debtor holds a running Veterans Pension award paid monthly and a request carrying a Financial Status Report was received … the proposal starts from the report share … of the latest monthly pension payment's gross amount".
  - Compute: `pension_payment: XLATEST('pension','pension_payments','gross_amount', …) or 0` and `starting_figure: … if (pension_payment > 0 and report_requests >= 1) …`. There is no status filter.
- Consequence, situation: a debtor whose pension was terminated but who has historic monthly payments. The rule gives tier 3 (balance ÷ 60); compute gives tier 1 or 2 (10% or 25% of the last payment).
- Task 1's pension is `running`, so no second answer on its world.
- Affected: `debt_ext_reduced_withholding_proposal.compute.pension_payment` / `starting_figure`.

**G4 — SOURCE-FACTOR RED (unreal ladder: a universal conjunct and an unreachable fall-through; bears on task 0)**
- Evidence: `longest_term` ladder.
  - Tier 1: "waiver request with a Financial Status Report received in the last six months AND balance at least the report-balance threshold".
  - Tier 2: "waiver request with a Financial Status Report received in the last six months AND balance below the report-balance threshold".
  - Fall-through: "otherwise", which is P('plan_max_months_without_fsr').
  - By the same policy's prerequisite sentence (G1), every customer who reaches `record_repayment_plan_request` carries such a waiver request.
- Consequence:
  - The waiver conjunct restates the write's scope. The ladder divides customers only by balance (60 vs 36), so it has two reachable tiers.
  - The fall-through, which is also the factor's `baseline`, describes a customer the rule forbids from reaching the write.
  - Struck, plan_request_term keeps 3 factors, below the floor of 4.
- Affected: `debt_ext_plan_request_term.factors[longest_term]`.

**G5 — SOURCE-FACTOR RED (mislabelled effect; bears on task 0)**
- Evidence: `spread_months` is labelled `method`. Its tiers are "the months on the latest request less K('restart_months_off_comp')" (1), "… less K('restart_months_off_other')" (2), and "the months on the latest request as stated" (0). That is one formula, months − k, with k ∈ {1, 2, 0}: a number substituted into the same formula is a `parameter` effect.
- Consequence: plan_installment's only other method factor is `spread_balance`, also a share substitution (balance − s·asked, s ∈ {1, 0.5, 0}, with a rounding step on the share). I accept it as a method on the strength of that rounding step and the extra record it reads (O9). The computation still meets the counts, but the label is dishonest.
- Affected: `debt_ext_plan_installment.factors[spread_months].effect`.

**G6 — SOURCE-FACTOR RED (unreal ladder: a universal conjunct, an unreachable fall-through and the only method factor; bears on task 1)**
- Evidence:
  - `recovery_value` tiers: "balance at least the discounting threshold AND months of recovery at least the discounting minimum" / "balance below … AND months of recovery at least the discounting minimum" / "otherwise", which is undiscounted.
  - `recovery_months` takes only K('care_level_months')=36, K('basic_pension_months')=48 or P('plan_max_months_with_fsr')=60. The last is 60 for all six debt variants (`variants[*].parameters.plan_max_months_with_fsr`).
  - `discount_months_min` = 24.
- Consequence:
  - "months ≥ 24" is true for every customer, so the undiscounted fall-through, which is also the factor's `baseline`, is unreachable, and the ladder divides only by balance: two reachable tiers.
  - This is the compromise computation's only `method` factor. Struck, the computation has 0 method factors.
- Affected: `debt_ext_compromise_offer_amount.factors[recovery_value]`, `params.discount_months_min`.

**G7 — SOURCE-FACTOR RED (unreal ladder: a universal conjunct and an unreal reachable fall-through; bears on task 1)**
- Evidence:
  - `cost_pct` tiers: "not referred to Treasury AND three or more offsets in the last three months" → 2 / "not referred to Treasury AND no offset in the last three months" → 10 / "otherwise" → 0.
  - Base `debt_evt_treasury_referral`: "Once referred, VA no longer sets up plans or takes compromise offers on the debt".
  - The G2 gate also forces `status = repayment_plan`.
- Consequence:
  - "not referred to Treasury" holds of every customer who reaches the compromise write.
  - The fall-through's intended population, referred debts on which VA bears no collection cost, never reaches the write. What reaches it is debts with 1–2 offsets in three months, which are assigned zero cost of collection while steadily offset debts bear 2% and billed debts 10%. No collector prices collection cost that way.
- Affected: `debt_ext_compromise_offer_amount.factors[cost_pct]`.

Observations (no demonstrated consequence; not grounds for rework):
- O1: the waiver amount has no cap at the balance (it can exceed the balance when credit > capacity × months).
- O2: docstring hints, as listed under action_binding_and_uuids.
- O3: the uuid8 ASCII pattern.
- O4: edge 1's state is named by business term.
- O5: the deposit-before-waiver gate is unrealistic.
- O6: the first-month and first-due-date edge case.
- O7: realism of the rating-based deposit discount, the restart surcharge and the debt-age installment discount. They have loose analogues (VA copay exemption at 50%+ ratings; risk-based restart terms) and are not demonstrably unpublishable.
- O8: a decorative conjunct in monthly_capacity tier 1.
- O9: the spread_balance method label is borderline.
- O10: the "last N calendar months counted back from today" phrasing is rolling by "counted back from today". A calendar-month reading is possible (demonstrated per task where it changes a number).

## closing_checklist

Written after both reveals (2026-10-06T03:35:54Z onward). Nothing above this heading was derived from a revealed GT.

**The difficulty does NOT close.** Not every relationship passes for every task. Status of each Step 4 item:

- **Audit files**: one file per task (`0.md`, `1.md`), with `_difficulty.md` alongside. This is the first revision, so there are no older revisions. Each file carries a source_gt_comparison.
  - Neither task is PASS on all four relationships:
    - task 0: SOURCE-POLICY RED (G1), SOURCE-FACTOR RED (G4, G5);
    - task 1: SOURCE-POLICY RED (G2, G3), SOURCE-FACTOR RED (G6, G7), SOURCE-TASK RED (proof-text intermediate only).
  - Disclosure: after the reveal, the freeze-time stamps in the three frozen sections were corrected from estimated values to the files' birth times (03:34:01Z, 03:35:05Z, 03:35:50Z). No derivation text was changed.
- **Coverage, scopes, tools**: all 7 extended policies are covered. The scopes are disjoint and span each whole tree:
  - task 0: deposit, waiver, term, installment;
  - task 1: proposal, rw_amount, compromise.
  - Task tools and GT are closed: each task's GT calls exactly its 4 or 3 scoped tools.
  - The uuid8s are distinct (O3 is an observation only).
  - Three claimed event types have no extended policy (policy_conflict_scan): debt_dispute_filed, debt_collection_held, debt_overcollection_refunded.
- **Trees**: task 0 has 3 prerequisites, 3 value_input edges and 2 user writes. Task 1 has 2 prerequisites, 2 value_input edges and 1 user write (the root). Both are acyclic, and the whole difficulty's graph is two disjoint chains, so it is a DAG.
- **Factors**: FAIL.
  - plan_request_term keeps 3 surviving factors (G4).
  - compromise has no surviving method factor (G6, G7).
  - spread_months is mislabelled (G5).
  - Every factor bears weight on its task's world against an honest baseline, and each whole-baseline fall-back differs from gold. All are confirmed figure for figure against `factor_sensitivity` / `baseline_result`.
- **Policy self-consistency**: FAIL. Undeclared overrides G1 and G2, and rule/compute drift G3.
- **Gates**: no re-run on a final form. The audited artifacts are unchanged: `debt.extended.yaml` and `task_tools.py` hashes re-verified equal to the freeze hashes at close; `tasks/0.json` sha256 `6363c8a3…f5f7`, `tasks/1.json` `ecce17d6…3108`. The instantiation gates in the brief's snapshot stand for this form.

Grounds for rework: G1–G7, and task 1 finding 4. Observations O1–O10, T0-O1 and T1-O1 are not grounds.

## revision_2

### charter_global_frozen (revision 2)

- Auditor: the same independent policy-task auditor as round 1. Written before any round-2 reveal of `tasks/*.json`.
- Hashes, round 1 → round 2 (recomputed by the auditor, equal to the new MANIFEST):
  - `debt.extended.yaml`: `51c719a1…dd61` → `4b31e9c84963610d85a8b7d1d00b92ab03495d2f92ed183b4703cc8a5f57a212`. **Changed.**
  - `task_tools.py`: `da2978bb…404b` → `fdf5d76140393b6a86ed2616f77d9c6d4227b84249b31a0260fc9de578be2b52`. **Changed.**
  - Both shared inputs moved, so every charter-global section below is re-derived in full, not carried forward.
- Masked views `task_0.view.json` (`cc093751…`) and `task_1.view.json` (`9563c76b…`) are byte-identical to round 1: `frozen_time`, `user_scenario` and `initial_state` did not change.
- Entry conditions: a fresh GATES.txt with all 8 lines green (check_traceability deferred). Met.
- Base section: still verbatim against `blueprint/products/debt.yaml` (the only difference is the trailing blank line).
- Where the extended section changed: `debt_ext_plan_request_term` (`overwrite`, rule, prerequisite), `debt_ext_plan_installment` (`factors[spread_months]` label and wording), `debt_ext_reduced_withholding_proposal` (`compute.pension_payment`), and `debt_ext_compromise_offer_amount` (`overwrite`, rule, prerequisite, params, compute, factors, baseline). I read deposit, waiver and reduced_withholding_amount again in full: same line counts, rules, compute and factors as round 1.

### policy_conflict_scan (rev 2)

- Overlapping subjects, time anchors and cross-category boundaries: as in round 1.
- Scopes: unchanged and disjoint; the 7 policies are fully covered.
- The three claimed event types without an extended policy (debt_dispute_filed, debt_collection_held, debt_overcollection_refunded) are still untested. I accept the reworker's "no change needed": this is a coverage note, not a conflict.
- **New conflict, R2-G8:** see findings (rev 2).

### rule_compute_equivalence (rev 2)

- **proposal**: compute now gates on running status. `pension_payment: "(XLATEST(...) or 0) if CFIELD('pension','status') == 'running' else 0"` matches "when the debtor holds a running Veterans Pension award paid monthly". **G3 closed.**
- **plan_request_term**: the compute is unchanged and the rule only added the conditional gate and restated base's "approved on request". Every binding is still quoted. Exact.
- **compromise**: re-swept in both directions:
  - `monthly_withholding` = "the approved reduced withholding or plan installment recorded on the debt, or, where none is recorded, the smallest plan installment of the debt type". Compute: method ≠ none and amount > 0, else P(min). Exact.
  - `recovery_value` tiers (benefit_withholding with ledger ≥ 5000 → present value; direct_payment with ledger ≥ 5000 → × (100 − 15)%; otherwise undiscounted) are all rule sentences and compute branches. Exact.
  - `cost_pct`: ≥3 offsets → 2, 0 → 10, otherwise (1–2) → 5. Exact.
  - The baseline rule ("… less the standard cost of collection … as a percentage") equals all fall-throughs, with cost 5 and recovery undiscounted.
  - `params` no longer carries `discount_months_min` or `cost_pct_none`, and nothing references them.
- **Others**: unchanged and exact, as in round 1.

### action_binding_and_uuids (rev 2)

- `(target_tool, computes)`: the 7 pairs are unchanged and unique. The uuid8s are unchanged, so O3 stands as an observation.
- Bodies: still unconditional, with no `if` or `raise`.
- Docstrings:
  - `pay_plan_reinstatement_66656e17` now says it posts "a reinstatement deposit" and "sets up no plan". The false "reinstates a repayment plan" claim is gone.
  - `record_repayment_plan_request_018c5870` no longer says "(the installment is set when a plan starts)".
  - "after the payment" and "after that window has closed" remain, but they describe the call's own effect and timing, not a cross-action order.
  - **O2 closed.**

### prerequisite_graph (rev 2)

- Same two chains, acyclic.
- All five `policy_source` strings are verbatim in their own rules. I confirmed this with a whitespace-normalised substring check.
- All edges: `form: state`, `kind: value_input`, `resolved_by` = the depended-on target_tool.
- The edges on plan_request_term and compromise are now conditional. Their `condition` texts carry the same condition as the sentence:
  - "Where the debtor asks for a plan longer than the no-report limit … a debtor asking for a plan within the no-report limit needs none";
  - "Where benefit offsets are being taken on the debt … a debt not collected by benefit offset needs none".
- Compromise `effect` was updated to the new fall-back: minimum installment, undiscounted. It is consistent with compute.

### prerequisite_sentences (rev 2)

- **Edge 2 (term ← waiver)**: "For a debtor who asks for a plan longer than the longest plan approved without a Financial Status Report, the number of months on the repayment plan request is fixed only after the debt carries a waiver request, received in the last six months, with the debtor's signed Financial Status Report attached."
  - Connective "only after"; state in table words; one writer.
  - The scope is now a closed condition (the debtor's ask beyond the no-report limit). A debtor asking within the limit is not gated.
- **Edge 5 (compromise ← rw_amount)**: "For a debtor whose VA benefit payments are being withheld for the debt, the lump sum … is worked out only after the debt carries an approved reduced monthly withholding …"
  - Connective "only after"; one writer, `start_reduced_withholding_20dc00ef`.
  - The scope (benefit offsets on the debt) is record-visible as `debt_offset_collected` rows.
- **Edges 1, 3, 4**: unchanged; round-1 conclusions stand, and O4 stands as an observation.
- No rule names a tool, policy id or another problem's sentence.

### override_declarations (rev 2)

- **plan_request_term**:
  - `overwrite` now names the base clause "a plan of up to plan_max_months_with_fsr months only with a Financial Status Report" (verbatim in `debt_evt_repayment_plan`). Its replacement is the conditional waiver gate.
  - Base "a plan of up to plan_max_months_without_fsr months is approved on request" is no longer contradicted; the rule now restates it.
  - The ladder's fall-through (no waiver → 12 − cuts) is now the treatment of a debtor asking within the limit, not a forbidden state.
  - Merged semantics are unique. **G1 closed.**
- **compromise**:
  - `overwrite` names base "A debtor may offer a lump sum smaller than the balance to settle a debt." (verbatim), replaced by the conditional gate.
  - The original G2 situation, a debtor with no running award, is no longer gated, because that debt is not collected by withholding. **G2 closed.**
  - The rework added a new sentence that is not part of the declared replacement: "A debtor whose debt is not being collected by withholding from VA benefit payments may offer such a lump sum at any time." See **R2-G8**.
- **The rest**: as in round 1. O5 and O6 stand as observations.

### factor_ladders (rev 2)

Changed rows only; every other row is as in round 1:

| policy | factor | label | reachable tiers | verdict |
| --- | --- | --- | --- | --- |
| plan_request_term | longest_term | parameter 60/36/12 | 3: a debtor asking within the limit reaches the write without a waiver, so the fall-through is reachable; the waiver conjunct is no longer universal | ok, **G4 closed** |
| plan_installment | spread_months | parameter (−1 / −2 / 0 months) | 3 | label honest, **G5 closed** |
| plan_installment | spread_balance | method (balance − whole asked / − 50% asked, rounded / balance) | 3 | **R2-F1 RED**, the round-1 O9 acceptance reversed (see findings) |
| compromise | recovery_value | method (present value / × 85% / undiscounted) | 3: withholding plus ledger ≥ 5000; direct plan plus ledger ≥ 5000; otherwise | ok, **G6 closed**. The months conjunct is gone; the tiers are multi-source (plan method on the debt row × the ledger) |
| compromise | cost_pct | parameter 2/10/5 | 3 by offset count, with no universal conjunct; the fall-through (1–2 offsets → standard 5%) is a realistic middle cost | ok, **G7 closed** |

Surviving counts:
- plan_request_term: 4 (3 parameter, 1 method). OK.
- compromise: 6 (5 parameter, 1 method). OK.
- plan_installment: 6 declared (5 parameter, 1 method). Its only method, spread_balance, fails R2-F1, so 0 honest method factors remain. **FAIL.**

Other observations, re-judged:
- O7: stands.
- O8: the decorative conjunct on monthly_capacity stands; it is only cosmetic.
- O1: the waiver amount is still uncapped at the balance, and the rule is unchanged. I accept "no change needed": it shows no consequence on any scored value.
- O10: the rolling window stands; the rule text resolves it.

### findings (rev 2)

Round-1 items:

| item | status | grounds |
| --- | --- | --- |
| G1 | **closed** | conditional gate, declared overwrite, base "approved on request" restated |
| G2 | **closed** | conditional gate, declared overwrite |
| G3 | **closed** | compute gates on running status |
| G4 | **closed** | fall-through reachable |
| G5 | **closed** | relabelled parameter |
| G6 | **closed** | months conjunct removed; three reachable tiers |
| G7 | **closed** | referral conjunct removed; fall-through is a standard 5% |
| O2 | **closed** | docstrings |
| O1, O3, O4, O5, O6, O7, O8, O10, untested event types | accepted, no change needed | observations only |
| O9 | **not accepted** | becomes R2-F1 |

**R2-F1 — SOURCE-FACTOR RED (mislabelled effect; bears on task 0). Escalates round-1 O9 and is disclosed as an auditor reversal, not a regression introduced by the rework.**
- Symptom: `debt_ext_plan_installment.factors[spread_balance]` is labelled `method`, but its three tiers are one formula. Balance − s × (amount asked), with s = 1, 0.5 (product rounded), or 0. That is a share substituted into the same formula.
- Evidence that the charter itself classes this exact shape as a `parameter`:
  - `debt_ext_plan_reinstatement_deposit.factors[excess_credit]` ("the whole excess" / "K('excess_credit_late_pct') percent of the excess" / "nothing"), effect: parameter;
  - `debt_ext_waiver_request_amount.factors[repaid_credit]` ("their whole total" / "K('partial_credit_pct') percent of it" / "nothing"), effect: parameter.
- Root cause: in round 1 I accepted spread_balance as borderline while spread_months was struck. With G5 fixed by relabelling spread_months as `parameter`, spread_balance is the computation's only `method` factor, and on inspection it does not change the algorithm.
- Demonstrated consequence: plan_installment has 0 honest `method` factors, below the floor of 1.
- Affected: `debt.extended.yaml` → `debt_ext_plan_installment.factors[spread_balance].effect`. Task 0, `computations` for the installment.

**R2-G8 — SOURCE-POLICY RED (undeclared override introduced in the rework; charter-global, bears on task 1's policy).**
- Symptom: the new compromise sentence "A debtor whose debt is not being collected by withholding from VA benefit payments may offer such a lump sum at any time." grants an unconditional, timeless permission that base sentences outside the declared overwrite forbid.
- Evidence:
  - (a) Base `debt_evt_offset`: "A debt that is on hold, referred to Treasury, or whose debtor has died is not offset from VA benefits."
  - (b) Base `debt_evt_treasury_referral`: "Once referred, VA no longer sets up plans or takes compromise offers on the debt; the debtor deals with Treasury."
  - (c) Base `debt_excl_single_pending_request` (a declared base ref of this policy): "a new request of any of these kinds is taken only when no earlier one on the same debt is still undecided".
  - The compromise `overwrite` supersedes only "A debtor may offer a lump sum smaller than the balance to settle a debt."
- Demonstrated consequences:
  - Situation 1: a debt `referred_to_treasury`. It is not offset from VA benefits, by (a). Extended: the debtor "may offer such a lump sum at any time". Base (b): VA takes no compromise offers; the debtor deals with Treasury.
  - Situation 2: a debt on hold because a timely waiver request is pending. It is not offset, by (a). Extended: may offer at any time. Base (c): the offer is not taken while the waiver is undecided; the debtor must withdraw it first.
- Affected: `debt_ext_compromise_offer_amount.rule`, sentence 2; `overwrite`.
- No consequence on task 1's world: the debtor is withheld, not referred, and has no pending request.

### closing_checklist (rev 2)

Written after the round-2 reveals (2026-10-06T06:08:29Z). Nothing above this sub-heading in revision_2 derives from a round-2 GT.

**The difficulty does NOT close in round 2.**

- **Round-1 REDs**:
  - Genuinely closed: G1, G2, G3, G4, G5, G6, G7, task-1 finding 4.
  - Observations closed: O2, T0-O1, T1-O1.
  - Accepted as observations needing no change: O1, O3, O4, O5, O6, O7, O8, O10, and the three untested event types.
  - O9 is not accepted; it becomes R2-F1.
- **Open**:
  - **R2-F1**, SOURCE-FACTOR RED, task 0: spread_balance mislabelled, leaving plan_installment with no method factor.
  - **R2-G8**, SOURCE-POLICY RED, charter, in task 1's policy: the new "may offer … at any time" sentence overrides the base Treasury-referral and single-pending-request sentences without declaring it.
  - **R2-T1**, SOURCE-TASK RED (proof text only), task 1: stale 2223.00 fall-back in `design_rationale`.
- **Regression check**: every scored argument of both tasks is unchanged from round 1 and equal to my independent recomputation. Trees, edges and skip effects hold, apart from the compromise skip, which moved from 0.00 to 654.49, as intended by the G2 rework. The tools remain logic-free. The base copy is still verbatim. Scopes are disjoint. No regression apart from R2-G8, which was introduced by the G2 rework.
- **Trees**: both still hold (task 0: 3 prerequisites, 3 value_input edges, 2 user writes; task 1: 2, 2, and a user-owned root). The graph is a DAG.
- **Gates**: the round-2 snapshot (all 8 green) was supplied, not re-run by the auditor.
- **Hashes at close**: `debt.extended.yaml` `4b31e9c8…a212`, `task_tools.py` `fdf5d761…2b52`, `tasks/0.json` `30cba47c…43e4`, `tasks/1.json` `7a69125f…a173`.

## revision_3

### charter_global_frozen (revision 3)

- Written 2026-10-06T07:03:53Z, before any round-3 reveal.
- Hashes, round 2 → round 3:
  - `debt.extended.yaml`: `4b31e9c8…a212` → `92eadea37def79170a84cdd65cecee7c5e5fa3026f5f2ee5321cf93c34babb18`. **Changed.**
  - `task_tools.py`: `fdf5d761…2b52`. **Unchanged.**
  - Masked views: `cc093751…` and `9563c76b…`, byte-identical to rounds 1–2.
  - Gate snapshot: the fresh GATES.txt shows all 8 green (traceability deferred).
- Because the charter moved, the charter-global sections are re-derived:
  - The tool-module half (action_binding_and_uuids, tool bodies, docstrings) is carried forward from revision_2 on the unchanged `task_tools.py` hash.
  - Base section: still verbatim.
  - Changed extended text:
    - `debt_ext_plan_installment`: param `plain_waiver_share_pct` replaced by `plain_request_reduction_pct: 20`; the spread_balance rule sentence, compute, compute_basis and ladder tier 2 changed.
    - `debt_ext_compromise_offer_amount`: rule sentence 2.
  - Every other policy matches revision_2 (same line spans; key compute lines and factor labels re-checked).
- Machine re-checks, by whitespace-normalised substring:
  - all five `policy_source` sentences are verbatim in their own rules;
  - all three `overwrite.superseded_clause`s are verbatim in `blueprint/products/debt.yaml`.

### Re-derivation of changed sections (rev 3)

**R2-F1 (`spread_balance` label).** The tiers are now:
1. balance − the amount the FSR-backed waiver asks (subtractive; reads the waiver request record);
2. round(balance × (100 − 20)/100, 2) (proportional scaling; "the amount asked is not relied on because the request is incomplete");
3. balance.

- The three are no longer one formula with a substituted share: tier 1 subtracts another record's value, and tier 2 scales the balance itself.
- That is the same standard applied to the other accepted `method` ladders (horizon_counted, months_run, starting_figure), where at least one tier computes the quantity by a different algorithm from a different input. The label is honest.
- Rule, compute_basis, compute and ladder agree on all three tiers, with rounding at the cent on tier 2. No code still references the removed `plain_waiver_share_pct`.
- Realism: discounting the spread balance for an incomplete pending waiver is a judgement call, but no less real than the prior 50% share. Observation O11.
- plan_installment counts: 6 factors (5 parameter, 1 honest method). **R2-F1 closed.**

**R2-G8 (compromise "at any time").** Sentence 2 now reads: "A debtor whose debt is not being collected by withholding from VA benefit payments is not held to the reduced-withholding step below; every other condition on taking an offer still applies to that debtor."
- Situation 1, a referred debt: base `debt_evt_treasury_referral` ("Once referred, VA no longer … takes compromise offers") still applies, as "every other condition on taking an offer". One conclusion.
- Situation 2, an on-hold debt with a pending waiver: `debt_excl_single_pending_request` still applies. One conclusion.
- The sentence now only exempts non-withheld debtors from the gate, consistent with the conditional prerequisite sentence and the declared overwrite. **R2-G8 closed.**
- Scan for new conflicts in this text: none. "the reduced-withholding step below" refers unambiguously to the next sentence, which is the gate.

**Unchanged sections** (policy_conflict_scan, prerequisite_graph, prerequisite_sentences, override_declarations, factor_ladders): the revision_2 conclusions stand on re-check. No new defect was found in round 3.

### closing_checklist (rev 3)

Written after the round-3 reveal (2026-10-06T07:04:00Z). **The difficulty closes: both tasks PASS all four relationships.**

- **Audit files**:
  - `0.md` and `1.md` correspond one-to-one with the tasks, with `_difficulty.md` alongside.
  - Revisions 1–3 are appended in place, and older text is untouched apart from the round-1 freeze-timestamp correction disclosed in round 1.
  - Every revision carries a source_gt_comparison. Revision 3 is PASS for both tasks.
- **Round-2 REDs**: R2-F1, R2-G8 and R2-T1 are genuinely closed (evidence under revision_3). All round-1 REDs remain closed.
- **Regression check**: every scored argument, tree, skip effect and sensitivity figure equals revision 2 and my recomputation. The tools are unchanged (same hash), the base copy is still verbatim, and the overwrites and prerequisite sentences are verbatim-locatable.
- **Coverage**:
  - All 7 extended policies are covered, and the two scopes (whole trees) are disjoint.
  - Task tools and GT are closed; the uuid8s are distinct and frozen (O3 observation only).
  - The claimed-but-untested event types debt_dispute_filed, debt_collection_held and debt_overcollection_refunded remain a coverage note.
- **Trees**:
  - task 0: 3 prerequisites, 3 value_input edges, 2 user writes;
  - task 1: 2 prerequisites, 2 value_input edges, a user-owned root.
  - The whole graph is a DAG of two disjoint chains.
- **Factors**: every computation has 4–6 factors with at least 2 `parameter` and 1 honest `method`:

  | computation | factors | parameter | method |
  | --- | --- | --- | --- |
  | deposit | 5 | 3 | 2 |
  | waiver | 4 | 3 | 1 |
  | term | 4 | 3 | 1 |
  | installment | 6 | 5 | 1 |
  | proposal | 4 | 3 | 1 |
  | reduced withholding | 4 | 3 | 1 |
  | compromise | 6 | 5 | 1 |

  - Each task has multi-source factors, and a cross-difficulty factor reading seeded comp (task 0) or pension (task 1) rows.
  - Every ladder has 3 reachable tiers with distinct outcomes.
  - Every factor bears weight against an honest baseline, and each whole-baseline fall-back differs from gold.
- **Gates**: the round-3 snapshot supplied by the orchestrator shows all 8 green on the final form (traceability deferred to the KB stage). The auditor did not re-run them.
- **Final hashes**: `debt.extended.yaml` `92eadea3…bb18`, `task_tools.py` `fdf5d761…2b52`, `tasks/0.json` `6f6b8aff…b58e`, `tasks/1.json` `aef97c46…d7a3`.
- **Open observations** (not grounds for rework): O1, O3, O4, O5, O6, O7, O8, O10, O11.
