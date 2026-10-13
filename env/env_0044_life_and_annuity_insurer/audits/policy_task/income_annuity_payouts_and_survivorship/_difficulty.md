# Policy-task audit — income_annuity_payouts_and_survivorship / charter-global

## charter_global_frozen

- Auditor: independent erl-task-policy-audit run (Claude agent), not the instantiating agent. Revision 1 (first audit of this difficulty; no previous revision exists).
- Freeze time: 2026-10-08T07:40Z. Written before any task's GT was revealed. Nothing in this section comes from a revealed GT.
- Frozen inputs (sha256, re-checked against the brief before reading):
  - `tasks/income_annuity_payouts_and_survivorship/income.extended.yaml` = `c9a5902845659ec0713822476b3179dd510693b1e841a918ce690b4ee64485b5`
  - `tasks/income_annuity_payouts_and_survivorship/task_tools.py` = `b824583ea7936047269d120747e670071958ce441231ef38a4e6e8c02c5f9b1e`
  - masked views `task_0.masked.json` = `3eea1fcd…cd16d5`, `task_1.masked.json` = `02b9152a…5169f` (frozen_time, user_scenario, initial_state only)
- Fields I was allowed to read: blueprint.yaml, db_schema.json, share_tools.py, products/{income,indexed,fixed}.yaml, the extended charter, task_tools.py, the two masked views, and the erlbench / check_compute DSL primitives (`skills/erl-task-instantiate/scripts/check_compute.py`: MONTHS/DAYS/SUM/COUNT/LATEST/CFIELD semantics, `RND` = Python `round`).
- Masked and not read before both task freezes: tasks/0.json, tasks/1.json (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), the difficulty worklog.md, and every other audit.
- Entry conditions (Step 0): the brief supplies the gate snapshot (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; check_traceability deferred because the KB is not published yet) and the masked-view hashes. Both hashes matched on disk. I accept the entry conditions. check_traceability not having run is noted, not counted as a defect.
- Base copy: the part of the extended yaml before the `# ====` banner is byte-identical to `blueprint/products/income.yaml`, apart from one trailing newline (checked with difflib: no line differs).

### policy_conflict_scan

Six extended policies, two candidate trees (a tree is the root plus its prerequisite problems):

| policy | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- |
| income_ext_beneficiary_arrears | pay_beneficiary_arrears_076c3375 (agent) | net_paid_amount | [] |
| income_ext_commutation_election | elect_commuted_value_be644418 (user) | commuted_value | arrears (value_input, gate `unpaid_past`) |
| income_ext_commuted_value_payout | pay_commuted_value_cb4f45b9 (agent) | net_paid_amount | election (value_input, gate `commuted`) |
| income_ext_held_survivor_forfeiture | forfeit_held_installment_e717f459 (agent) | forfeited_amount | [] |
| income_ext_post_death_excess_repayment | settle_post_death_deposit_f655a739 (user) | repayment_amount | [] |
| income_ext_survivor_held_release | release_survivor_share_80ea435e (agent) | net_paid_amount | forfeiture (value_input, gate `release_gross`); repayment (state_gate, gate `income_transactions.recovery_method`) |

- Overlapping subjects: `income_payment_issued` is the subject of both arrears and release. They do not overlap in practice. Arrears covers a certain installment that was never issued on a **period-certain** tier. Release covers the survivor share of a **held** installment on a **joint-and-survivor** tier. `income_held_payment_released` is the subject of both forfeiture and release, but forfeiture books `release_outcome=forfeited` and release books `paid`. `income_commuted_value_paid` is the subject of both election and payout. The election tool actually writes an `income_service_requests` row (`commutation_election`), not that event, so the subject label is loose (observation O-9). No two policies give different results for the same quantity in the same situation.
- Triggers, eligibility and time anchors: every extended rule inherits the base death-claim gate ("A death benefit, continuation or completion is processed only on a death claim whose certified death certificate has been received and whose request status is approved"). Arrears and release use different interest anchors (proof or death date for arrears, held due date or certificate date for release). Each sits in its own policy, so they never compete for one quantity.
- Cross-category reads: arrears, payout and release each read `cost_basis` from indexed_holdings or fixed_holdings through CFIELD, keyed by the contract's own `source_*_contract_id`. Each read is bounded to the contract annuitized.
- Scope: the six policies split into {arrears, election, payout} and {forfeiture, repayment, release}. These two sets are disjoint and together cover all six. Pre-reveal, this is the partition the prerequisite graph implies. I check it against charter_scope after the reveal (closing checklist).
- Undeclared overrides of base: see `override_declarations`. Three are found (F1, F2, F3).

### rule_compute_equivalence

Swept every binding of all six policies against `compute_basis` and back against the rule.

- arrears: every binding is quoted. Mismatches found:
  - (a) `held_installment = LATEST(... event_type='income_payment_held')` takes the latest held row on the contract **whatever its payment date and whether or not it was already released**. The rule says "where the arrears installment is held in suspense". So compute is broader than the rule: a contract with an older, already released held row would be put on tier 2 at that old amount (O-1).
  - (b) `proof_date` does not filter `death_certificate_received=True`, but the rule's anchor is "the date due proof of death was received" (O-1).
  - Neither mismatch moves a value on task 0's world, because the world has no held row and a single death_claim with the certificate received.
- election: every tier of each factor is a rule sentence and a branch of its binding, and the reverse also holds.
  - `first_discount` puts lead_days == 0 on the "within the cutoff days" branch, where it evaluates to exactly 1 period. So the stated fall-through ("otherwise … one payment period") is reached only by a next_payment_date in the past (O-6).
  - The `face_count` clause ("any certain installment that fell due after the date of death and still stands unissued is added undiscounted…") can never be non-zero while the rule's own prerequisite sentence is obeyed. It is dead text under the policy's own order (O-7).
- payout: all bindings are quoted. `taxable` implements the three-tier ladder. Its "otherwise" branch (IRA) applies the exclusion ratio, matching the rule.
- forfeiture: all bindings are quoted. `forfeit_pct` implements its ladder exactly; see F4 for why that ladder is not real.
- repayment: all bindings are quoted. `same_year` derives the calendar year from MONTHS('0001-01-01', d)/12, which is equivalent to comparing years.
- release: all bindings are quoted. `certificate_date` filters `death_certificate_received=True`, matching the rule.
- No factor tier lives only in compute, and no rule tier is missing from compute.

### action_binding_and_uuids

- `(target_tool, computes)` pairs are all distinct, and each tool is claimed by exactly one policy.
- Tool bodies (task_tools.py): none checks status, eligibility, order or existence of a prerequisite. Each one writes the rows it describes.
  - pay_beneficiary_arrears books an `income_payment_issued` row and lowers unreturned_premium by gross. It does **not** write `taxable_amount` or `federal_withholding_amount` on that row (O-8).
  - elect_commuted_value books an approved `commutation_election` request.
  - pay_commuted_value books `income_commuted_value_paid` and lowers unreturned_premium.
  - forfeit_held_installment books a forfeited release and lowers suspense_held_balance.
  - settle_post_death_deposit books identified and recovered rows (direct_repayment) for the amount.
  - release_survivor_share books paid release and issued rows, and lowers suspense and unreturned_premium.
- Docstrings: none uses before/after/first. elect_commuted_value's Returns section says the election reference number is "(needed to pay the commuted value)", and pay_commuted_value's arg says "returned on the election receipt". Both point at another tool's action. This states the payout ← election dependency at the tool layer, which check 3 forbids. The payout rule states the same dependency, so no solution moves → observation O-5.
- uuid8s: 076c3375, be644418, cb4f45b9, e717f459, f655a739, 80ea435e. These share no prefix, are not sequential and are not off by one in a tail. They look independently generated. PASS.

### prerequisite_graph

- `prerequisite` is filled on all six (three are `[]`). Every `problem` is an extended id of this file. There are no base targets and no self-loops. Graph: arrears → election → payout; forfeiture → release; repayment → release. Acyclic.
- Every `policy_source` is found verbatim in the blocked policy's own rule (checked by string search after collapsing YAML folding).
- Every edge has `form: state` and none carries `fallback_reason`. Correct.
- `resolved_by` is the depended-on policy's target_tool on all four edges.
- `kind`/`gate`: `unpaid_past`, `commuted` and `release_gross` are real compute bindings of the blocked policy. The state_gate gate `income_transactions.recovery_method` is a `<table>.<field>` path, which the instantiate contract allows.
- `condition` against sentence:
  - (i) election edge: the condition says "has an issued payment", but the sentence says "stands issued **to the beneficiary**". The condition is slightly weaker (O-4).
  - (ii) payout edge: the condition adds "carrying the commuted value and the withholding rate chosen", but the sentence only requires an approved signed election. The condition is slightly stronger, though harmless because the election tool always writes both (O-4).
  - The remaining two edges match their sentences.
- No authoring-viewpoint wording ("in this task", "at the opening") appears in any `prerequisite` text.

### prerequisite_sentences

| edge | sentence (own rule) | connective | waits on (state) | single write that brings it about |
| --- | --- | --- | --- | --- |
| election ← arrears | "The commuted value is fixed only after every certain installment that fell due between the date of death and the election stands issued to the beneficiary on the contract's activity history." | only after | an issued certain installment for every post-death payment date | The arrears policy's write. It is the only policy whose rule issues "a certain installment that fell due after the date of death … to the beneficiary". release_survivor_share also books `income_payment_issued` mechanically, but its rule is restricted to joint-and-survivor held installments, so a reader cannot pick it for a "certain installment" (O-3) |
| payout ← election | "The commuted value is not paid until a commutation election signed by the beneficiary stands approved on the contract." | not … until | approved signed commutation election | elect_commuted_value (the only write that creates a commutation_election request) |
| release ← forfeiture | "The survivor share released from a held installment is fixed only after the part of that installment above the survivor share stands forfeited on the contract's activity history." | only after | forfeited release for the held date | forfeit_held_installment (the only write booking `release_outcome=forfeited`) |
| release ← repayment | "A held installment is not released to the survivor until every installment deposited at the joint amount after the first death carries a repayment entry for its excess." | not … until | repayment entry on each joint-amount post-death deposit | settle_post_death_deposit (the only write booking a direct_repayment recovery) |

- All four pass the four-point test: they have an ordering connective, name a record-visible state with no performer or tool, contain no tool name, policy id or snake_case token, and match the edge's scope.
- No blocked rule restates the dependency in a second wording. No depended-on rule restates the sentence.
- No extended rule states a cross-problem order that grounds no edge. The release rule's "Once the death … is confirmed and the contract is continuing to the survivor" and the arrears rule's "before the beneficiary's payments began" wait on base-event states, not on another problem of this difficulty.
- No base rule sentence grounds an edge.

Derivations (sentence + records + depended-on rule → resolving action):

- election ← arrears: The agent lists the post-death payment dates on the activity history and finds one with no issued row. The rule that issues "a certain installment that fell due after the date of death and before the beneficiary's payments began, and that was never issued" is the arrears rule, so that installment is paid first. There is one reading.
- payout ← election: No approved commutation_election exists. The election rule describes the beneficiary signing one, which is an owner=user write handed to the beneficiary. There is one reading.
- release ← forfeiture: No forfeited release exists for the held date. The forfeiture rule forfeits "the part of it that no living payee is owed … in one forfeited release for that payment date". There is one reading.
- release ← repayment: A deposit issued after the first death at more than the survivor installment has no repayment entry. The repayment rule lets the payee "repay what is owed back on it directly" and records it against the deposit. There is one reading of the hop. For a conflict with an inherited base sentence about **who recovers first**, see F2.

### override_declarations

Sentence-by-sentence sweep of every `base_policy_refs` entry:

- **arrears** (refs income_payment_schedule, income_death_of_annuitant)
  - Declared: the exclusion-ratio sentence and the withholding sentence. Both are correctly replaced.
  - Followed: the payable-status sentence, the death-claim proof/approval gate, the "remaining certain installments continue to the beneficiaries on the original schedule" sentence and the designation/shares sentence.
  - Base is silent on interest and state tax for an installment, so those are extensions, not conflicts (O-2).
  - **Not declared: the COLA sentence** "Where a cost-of-living rate was chosen, the installment increases by that rate, compounded, on each contract anniversary from cola_first_increase_anniversary onward, rounded to the cent." Arrears tier 1 pays "at the amount of the last installment issued to the annuitant" whenever a COLA anniversary fell after the death. That includes an arrears installment falling due **after** that anniversary, which base prices at the increased amount → **F3**.
- **election** (ref income_death_of_annuitant): the entire base commutation clause is named as superseded, so the extended ladder replaces it with unique merged semantics. `replaced_by` reproduces only the baseline, not the tiers (O-10). Everything else in the base policy is followed.
- **payout** (refs income_death_of_annuitant, income_payment_schedule)
  - Declared: the withholding sentence.
  - Followed: the lump-sum status gate and the designation sentence.
  - **Not declared: the exclusion-ratio sentence** "On a non-qualified contract where exclusion_ratio_applies is true, each installment is split into a tax-free part equal to the installment times the exclusion ratio and a taxable remainder, until the total tax-free amount equals the purchase amount …". The payout rule replaces the purchase amount as the recovery cap with "the investment in the contract … the cost basis of the annuity annuitized". That is the same contract-level quantity, the arrears and release policies both declared exactly this override for their own payments, and the payout leaves it undeclared → **F1**.
- **forfeiture** (refs income_proof_of_life_and_suspension, income_evt_overpayment_recovery)
  - Declared: the suspension sentence on held installments after a confirmed death.
  - The overpayment-recovery sentence "Held installments falling due after the death are forfeited rather than paid, and are never counted as overpayments" is not named. It is qualified within its own policy by "the date of death that ended it", and on a joint tier the first death does not end the installment, so I read it as not reaching the survivor share (O-11).
- **repayment** (refs income_evt_overpayment_recovery, income_death_of_annuitant)
  - Declared: the death-of-annuitant sentence "Every installment paid for a payment date after the date of death that ended it is an overpayment …".
  - **Not declared: the overpayment-recovery sentence** "Ashgrove first asks the bank to return a post-death direct deposit within overpayment_reclamation_window_days of the deposit; what the bank does not return is requested from the estate or the person who received it." The extended rule lets the payee "repay what is owed back on it directly" at once, with no bank reclamation first and no regard to the 90-day window → **F2**.
  - The identical "An installment paid … after the date of death that ended it is an overpayment, recorded once per installment" in income_evt_overpayment_recovery is also not named. The extended rule records the overpayment for the amount repaid, not per installment (folded into O-11).
- **release** (refs income_proof_of_life_and_suspension, income_evt_overpayment_recovery, income_payment_schedule)
  - Declared: the no-interest sentence, the held-after-death sentence, the exclusion sentence and the withholding sentence.
  - Followed: the base release-in-one-sum sentence and the reissue sentence.

### factor_ladders

Counts are per computation: P = parameter, M = method, MS = multi-source factor (every non-fall-through tier is a conjunction over distinct records), XD = cross_difficulty label.

| policy | factors (label) | P/M | MS | XD |
| --- | --- | --- | --- | --- |
| arrears | arrears_installment_amount (M), arrears_investment_in_contract (M), arrears_withholding_rate (P), arrears_interest_rate (P), arrears_interest_period (M), arrears_state_tax (P) | 3/3 | interest_rate (issue_state × proof history), state_tax (issue_state × computed federal × 12-month ledger), installment_amount (cola_pct × dates × held rows) | investment: indexed (fixed branch too) |
| election | commuted_installment_count (M), commutation_cutoff_installment (M), commutation_spread_by_term_left (P), commutation_rate_floor_and_cap (P), commutation_first_discount_period (M), commutation_cost_of_living_growth (M) | 2/4 | count tier 1 (status × ledger) | none |
| payout | commuted_value_taxable_part (M), commuted_value_investment_in_contract (M), commuted_value_withholding_rate (P), commuted_value_state_tax (P) | 2/2 | taxable (tax_qualification × cross cost basis × unreturned), state_tax | investment: indexed (fixed branch too) |
| forfeiture | forfeiture_part_of_held_installment (M), forfeiture_survivor_amount (M), forfeiture_survivor_percentage (P), forfeiture_joint_installment (P) | 2/2 | part (tier × status × dates), joint_installment (cola × dates × ledger) | none |
| repayment | repayment_excess_of_deposit (M), repayment_survivor_entitlement (M), repayment_survivor_percentage (P), repayment_share_of_excess (P) | 2/2 | excess, share (ledger × dates) | none |
| release | survivor_release_amount (M), survivor_release_investment (M), survivor_release_withholding_rate (P), survivor_release_interest_rate (P), survivor_release_interest_period (M), survivor_release_state_tax (P) | 3/3 | interest_rate, state_tax | investment: fixed (indexed branch too) |

Shape checks:
- Every ladder has exactly three tiers, all stated in the rule as prose and implemented in compute.
- Every fall-through equals the policy's baseline, and every `decides` is an input, not `result`.
- Bindings are disjoint within each policy.
- Every `baseline.rule` sentence is a rule sentence.

Defects found:

- **F4: the forfeiture_survivor_percentage and repayment_survivor_percentage ladders are not real.**
  - Tier 2 ("a joint-and-survivor tier whose joint annuitant died while the tier reduces only on the annuitant's death") can never be selected under this charter, because all six variants carry `survivor_reduction_trigger: either_death`. Tier 1's "reduces on either death" therefore holds for every joint contract.
  - Tier 3 ("otherwise zero") applies only to single-life tiers, where `survivor_continuation_pct` is already 0.00. Its value is also never consumed, because `survivor_amount`/`entitlement` read the percentage only on a joint tier.
  - So on every contract the charter can hold, the ladder evaluates to `P('survivor_continuation_pct')`. That is the base charter's own survivor percentage, which the base sentence "on the first death … payments continue to the survivor at survivor_continuation_pct of the installment" already applies to the survivor installment.
  - Its `baseline: 0.0` is a zero where the standard method gives a figure (0.50 on Joint 50%), i.e. a straw man.
  - The task-level demonstration is in 1.md.
- **F5: the state-tax factors carry a dishonest `parameter` label.** In arrears_state_tax, commuted_value_state_tax and survivor_release_state_tax, tier 1 is "the state flat rate **on the taxable part**" and tier 2 is "the state share **of the federal tax**". The two tiers compute the quantity from different bases (flat-percentage-of-distribution against percentage-of-federal, the two state withholding *methods* the industry distinguishes). They do not just substitute a number into one formula, so the honest label is `method`.
  - Effect on counts: arrears drops to P=2, which still passes. Release drops to P=2, which still passes. Payout drops to **P=1 < 2**, which fails the floor. The demonstration is in 0.md.
- **F6: arrears_interest_period tier 2 is not a treatment any insurer publishes.** "For a contract issued in any other state whose death claim was approved more than the group late days after due proof was received, it runs from the date the claim was approved". This runs interest from the later approval date exactly when the insurer was late. The claimant's interest period gets *shorter* because of the insurer's own delay, the opposite of every late-claim interest rule (statutes run interest from date of death or from receipt of proof). The factor sits in task 0's tree.
- Labels of the analogous ladders arrears_installment_amount (M) and forfeiture_joint_installment (P) are inconsistent. Both pick which record supplies an installment amount, and one tier of the latter applies a COLA growth. This has no count consequence beyond F4/F5 (O-12).
- Unreachable fall-throughs (observations, not RED):
  - commuted_installment_count's "otherwise" (status neither beneficiary_continuing nor death_claim_pending) can never be reached by a commutation, because the base lump-sum status gate allows only those two statuses.
  - survivor_release_interest_period's "with no such date … no days" can never be reached by a release, because the release rule requires the death confirmed, i.e. a certificate received.
  - The survivor_amount and entitlement fall-throughs are never consumed, because only the joint branch reads them (O-6).
- Cross-difficulty: the blueprint declares five difficulties (term, whole, ul, fixed, income). **Indexed is a product with no difficulty.**
  - The task-0 tree's only cross-category reads (arrears and payout investment) take the indexed branch on its world. Read strictly, "reads another difficulty's records" is not met by task 0. Read as "another product line's records", it is met. I record this as observation O-13 and do not upgrade it.
  - Task 1's release investment factor reads `fixed` (the deferred_annuity_withdrawals_and_death_benefits difficulty), so task 1 meets it on any reading.

### findings

| id | verdict | summary | bears on |
| --- | --- | --- | --- |
| F1 | SOURCE-POLICY RED | payout: undeclared override of the base exclusion-ratio sentence (purchase-amount recovery cap replaced by the annuitized cost basis) | task 0 (demonstrated in 0.md) |
| F2 | SOURCE-POLICY RED | repayment: undeclared override of the base "Ashgrove first asks the bank to return a post-death direct deposit within overpayment_reclamation_window_days …" | task 1 (demonstrated in 1.md) |
| F3 | SOURCE-POLICY RED (charter level) | arrears tier 1 versus the base COLA sentence, undeclared. Demonstration: death 2026-07-27, anniversary 2026-09-01, beneficiary payments begin 2026-10-12, so the arrears installment is due 2026-09-12. Base gives 538.88 × 1.01 = 544.27, arrears tier 1 gives 538.88 | task 0's policy. On task 0's world the arrears installment is due 2026-08-12, before the anniversary, and both readings give 538.88, so there is no second answer in task 0 |
| F4 | SOURCE-FACTOR RED | survivor-percentage ladders reduce to the base parameter; straw-man 0.0 baseline | task 1 (forfeiture, repayment) |
| F5 | SOURCE-FACTOR RED | state-tax factors mislabelled `parameter`; payout falls to 1 honest parameter factor | task 0 (payout). Arrears and release: label defect only, counts still pass |
| F6 | SOURCE-FACTOR RED | arrears_interest_period tier 2 unreal | task 0 (arrears ladder) |
| O-1 | observation | arrears compute filters broader than the rule (held_installment, proof_date) | none on either world |
| O-2 | observation | arrears adds interest and state tax to an installment, where base is silent (an extension, not a conflict) | task 0 |
| O-3 | observation | the release tool can also book `income_payment_issued`; only the arrears rule issues a *certain* installment | task 0 |
| O-4 | observation | election and payout edge `condition` wording slightly weaker or stronger than the sentence | tasks 0 |
| O-5 | observation | the elect / pay_commuted_value docstrings reference the other tool's action | task 0 |
| O-6 | observation | unreachable or unconsumed fall-throughs (first_discount at lead 0, commutation count, release interest period, survivor_amount, entitlement) | both |
| O-7 | observation | election count tier 1's "added undiscounted" clause is dead under the policy's own prerequisite | task 0 |
| O-8 | observation | the arrears tool writes no taxable_amount or federal_withholding_amount on the issued row | task 0 (no scored effect: the 12-month sum is already > 0) |
| O-9 | observation | election subject `income_commuted_value_paid` although it writes a request | task 0 |
| O-10 | observation | election overwrite `replaced_by` carries only the baseline | task 0 |
| O-11 | observation | overpayment-recovery sentences ("held … after the death are forfeited", "recorded once per installment") not named, limited by "the death that ended it" | task 1 |
| O-12 | observation | inconsistent effect labels across analogous ladders | both |
| O-13 | observation | indexed has no difficulty; task 0's cross read is cross-product, not cross-difficulty on a strict reading | task 0 |
| O-14 | observation | every extended rule carries both its baseline sentences and its factor sentences for the same quantity, e.g. "no state tax is withheld" and "State tax is withheld … only when …". This structure is what the instantiate contract requires; the more specific sentence governs, so it is not counted as a conflict | all |

## closing_checklist

Written after both reveals (2026-10-08, after the 07:41:28Z hash record). Nothing above this heading was changed after the reveal.

- Per-task audit files: 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json, with this file alongside. This is revision 1, so there are no older revisions. Comparison sections: **neither carries a PASS** (task 0: SOURCE-POLICY RED + SOURCE-FACTOR RED; task 1: SOURCE-POLICY RED + SOURCE-FACTOR RED). **The difficulty does not close.**
- Coverage and scope: charter_scope of task 0 = {arrears, election, payout}; of task 1 = {forfeiture, repayment, release}. The two are pairwise disjoint and together cover all six extended policies. Task tools match the scopes. The uuid8s are independent (§ action_binding_and_uuids). PASS.
- Trees:
  - Task 0: 2 prerequisite problems, 2 value_input edges, user write elect_commuted_value, acyclic.
  - Task 1: 2 prerequisite problems, 1 value_input + 1 state_gate, user write settle_post_death_deposit, acyclic.
  - Difficulty-wide graph: acyclic (two components).
  - PASS.
- Factors: **fail**.
  - F4: forfeiture and repayment each have 3 genuine factors with 1 parameter.
  - F5: payout has 1 honest parameter factor.
  - F6: the arrears interest-period ladder carries an unreal tier.
  - F7 (in 0.md): task 0's only cross reads go to indexed, which is a product no difficulty claims. GT's "another difficulty" assertion is false against blueprint.yaml.
  - Every factor otherwise bears weight on its world against its declared baseline, and every all-baseline fallback is a definite number different from gold (534.57, 13282.65, 11653.63, 1012.48, 1032.73, 962.67).
- Policy self-consistency: **fail**. F1 (payout, undeclared exclusion-ratio override) is demonstrated in task 0. F2 (repayment, undeclared "Ashgrove first asks the bank …" override) is demonstrated in task 1. F3 (arrears tier 1 against the base COLA sentence) is charter-level, with no consequence on task 0's world.
- Gate re-run on the final form: not performed. The difficulty does not close, and the artifacts are byte-identical to the gate snapshot in the brief: extended yaml, task_tools.py, 0.json and 1.json hashes all re-checked equal.

## revision_2

### charter_global_frozen (revision 2)

- Auditor: the same independent erl-task-policy-audit run as revision 1, re-auditing at the coordinator's request.
- Section written at 2026-10-08T10:2xZ, before either round-2 task JSON was opened. Nothing in this section comes from a round-2 GT.
- Inputs, all re-hashed on disk and equal to the brief:
  - extended yaml `86e7c53b935c4de1fcc6e8e20869a90cfa2c6c34c47a48f0013aa689fd6a2fba` (changed from revision 1's `c9a59028…`)
  - task_tools.py `56c3d6f32e746f77c74cf1e9898eefd36ba807aaf29d419079a2ab3cb590187d` (changed from `b824583e…`)
  - masked views `4942510369bd…0fbc4` (task 0) and `0f7cadcb69bd…ee20b` (task 1)
- Both shared inputs changed, so every charter-global section below is **re-derived in full**. Nothing is carried forward.
- Base copy: still byte-identical to blueprint/products/income.yaml.
- Entry conditions: the gate snapshot after rework was supplied (all OK; traceability deferred) and the view hashes matched.
- Revision 1 text above is left untouched.

### policy_conflict_scan (revision 2)

| policy | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- |
| income_ext_beneficiary_arrears | pay_beneficiary_arrears_076c3375 (agent) | net_paid_amount | [] |
| income_ext_commutation_election | elect_commuted_value_be644418 (user) | commuted_value | arrears (value_input `unpaid_past`) |
| income_ext_commuted_value_payout | pay_commuted_value_cb4f45b9 (agent) | net_paid_amount | election (value_input `commuted`) |
| **income_ext_returned_installment_reissue** (new; replaces the retired income_ext_held_survivor_forfeiture) | **reissue_returned_installment_7c2be31a** (agent) | net_paid_amount | [] |
| income_ext_post_death_excess_repayment | settle_post_death_deposit_f655a739 (user; new arg `overpaid_amount`) | repayment_amount | [] |
| income_ext_survivor_held_release | release_survivor_share_80ea435e (agent; now also books the forfeited part and any offset) | net_paid_amount | repayment (**value_input** `overpayment_outstanding`); reissue (state_gate `income_transactions.release_outcome`) |

- Overlaps checked:
  - `income_held_payment_released` + `income_payment_issued` are now the subjects of both reissue and release. Reissue takes "an installment that came back returned and is held in suspense". Release takes "an installment still held in suspense for a payment date after the death". On both worlds the objects are disjoint (08-01 returned-held against 09-01 death-report-held).
  - A returned installment falling due after a death whose payee is deceased fits no reissue payee clause and is left to the release. So the two are not in competition.
  - The arrears/release overlap on `income_payment_issued` is unchanged from revision 1 (disjoint by tier).
- Scope partition implied by the graph: {arrears, election, payout} and {reissue, repayment, release}. Disjoint and jointly complete over the six policies.

### rule_compute_equivalence (revision 2)

- arrears:
  - `proof_date` now filters `death_certificate_received=True` (revision-1 O-1(b) closed).
  - New bindings `report_date`, `arrears_ppy`, `arrears_mpp` and `anniversaries_to_arrears_date` are quoted and implement the new tier-1 and interest-period sentences.
  - `held_installment` is still the latest held row on the contract, whatever its date or release status (O-1(a) remains).
- election: unchanged from revision 1 (O-6 lead-0 boundary and O-7 dead face clause remain).
- payout: unchanged apart from `state_tax` (now `state_alt_rate` × taxable). It is quoted.
- reissue (new): every binding is quoted. `returned_due`/`returned_gross` filter `hold_reason='returned_payment'`. `instructions_date` reads the latest completed bank_change, matching "the date the confirmed payment instructions were received". `federal_tax` uses the contract election, matching the rule.
- repayment:
  - `entitlement` now uses `P('survivor_continuation_pct')` directly. The survivor-percentage ladder is gone.
  - New `overpayment_owed`, `held_due`, `held_amount`, `held_days_after_death` and `offset_to_come` implement the new offset sentence.
  - All are quoted.
- release:
  - The survivor share, `forfeited`, `overpayment_outstanding` ("the overpayments recorded on the contract less the recoveries recorded against them") and `offset` are each quoted and implemented.
  - The interest bindings are gone, matching "the held installment earning no interest".
- No tier is missing from either face.

### action_binding_and_uuids (revision 2)

- `(target_tool, computes)` are all distinct.
- New uuid8 `7c2be31a` shares no prefix or sequence with 076c3375, be644418, cb4f45b9, f655a739 or 80ea435e. PASS.
- No tool body checks status, order or the presence of a prerequisite:
  - reissue: unconditional creates/updates.
  - settle: books identified (overpaid_amount) and recovered (repayment_amount); receivable += owed − repaid.
  - release: books forfeited, released, paid and, when offset > 0, a payment_offset recovery.
- Docstrings:
  - elect_commuted_value no longer says "(needed to pay the commuted value)" (revision-1 O-5 closed).
  - pay_commuted_value's arg now reads "as shown on the election's receipt or in the income annuity service requests", which is neutral provenance.
  - No before/after/first ordering words are used about other actions.
- The arrears tool still books no `taxable_amount`/`federal_withholding_amount` (O-8 remains, no scored effect).

### prerequisite_graph (revision 2)

- Filled everywhere. Every `problem` is an extended id. Acyclic: arrears → election → payout; repayment → release; reissue → release.
- Every `policy_source` is verbatim in the blocked rule (checked mechanically).
- All edges have `form: state` and none has `fallback_reason`.
- `resolved_by` is the depended-on target_tool on every edge.
- `gate`: `unpaid_past`, `commuted` and `overpayment_outstanding` are real bindings. `income_transactions.release_outcome` is a table.field.
- `condition` against sentence:
  - election: now "has an issued payment **to the beneficiary**". Matches.
  - payout: now "an approved commutation election signed by the beneficiary". Matches (revision-1 O-4 closed).
  - release ← repayment: matches.
  - release ← reissue: "Every held entry for a payment date on or before the first death has a paid release entry". Matches "stands released".

### prerequisite_sentences (revision 2)

| edge | sentence | single write that brings it about |
| --- | --- | --- |
| election ← arrears | "The commuted value is fixed only after every certain installment that fell due between the date of death and the election stands issued to the beneficiary on the contract's activity history." | arrears (O-3 unchanged) |
| payout ← election | "The commuted value is not paid until a commutation election signed by the beneficiary stands approved on the contract." | elect_commuted_value |
| release ← repayment | "The survivor share of a held installment is fixed only after every installment deposited at the joint amount after the first death carries a repayment entry for its excess." | settle_post_death_deposit (the only direct_repayment writer) |
| release ← reissue | "A held installment that fell due after the first death is not released until every installment held for a payment date on or before that death stands released." | Reissue is the only policy that releases a pre-death held installment; the release rule's scope is post-death installments. On a world whose pre-death held installment is not a returned one, no policy of this difficulty would release it, but neither world has one (observation O-18) |

- All four pass the four-point test. No second wording, no tool name and no restatement in the depended-on rule.
- The release ← repayment sentence names "the survivor share" as what waits, but the repayment moves only the overpayment applied, i.e. the amount sent, not the share (506.24 either way). The resolving action is still read uniquely → observation O-15.

### override_declarations (revision 2)

- **arrears**
  - Declared: exclusion and withholding (unchanged).
  - The base COLA sentence ("…the installment increases by that rate, compounded, on each contract anniversary from cola_first_increase_anniversary onward, rounded to the cent") is **still not named**. The new tier 1 raises the last annuitant installment once for each anniversary "falling after the date of death and on or before **the first payment date after the death**", whatever the arrears installment's own payment date.
  - Demonstration (same situation as revision-1 F3): death 2026-07-27, anniversary 2026-09-01, beneficiary payments begin 2026-10-12, so 2026-08-12 and 2026-09-12 are both arrears. For the 2026-09-12 arrears the extended rule gives 538.88 × 1.01⁰ = **538.88** (no anniversary falls between 07-27 and 08-12). Base gives **544.27** (538.88 × 1.01 after the 09-01 anniversary).
  - **F3 is narrowed (the single-arrears-before-anniversary case now agrees) but not closed.**
- **election**: unchanged; whole clause superseded.
- **payout**: **now declares the exclusion-ratio sentence** (replaced_by = the three-tier taxable ladder, cap at the investment in the contract). F1 closed.
- **reissue** (refs suspension, overpayment recovery, payment schedule, returned payment)
  - Declared: the no-interest sentence and the exclusion sentence.
  - Followed:
    - "A returned payment is reissued by returned_payment_reissue_method once instructions are confirmed" (method check, confirmed bank_change).
    - "A suspension is cleared only by … confirmed new payment instructions".
    - The withholding sentence (contract/owner election, so no override needed).
    - The returned-payment sentences (return 2026-08-04, account_closed, before the death).
  - The payee clause ("to the payee named on it while that payee is living, and otherwise … to the surviving joint annuitant or to the beneficiary now receiving the payments") narrows the base "released to the estate or survivor" within the disjunction base already offers. Not a conflict.
  - Observation O-16: reissue withholds at the owner's election on a payment now made to the survivor. The arrears and release rules justify their own payee-default rates with "an election made by the owner does not govern another person's payments". That reasoning is scoped to their own quantities, and the reissue rule states its rate explicitly, so there is one reading.
- **repayment**
  - Declared: the death sentence, plus **now** the "Ashgrove first asks the bank …" sentence (replaced: a deposit paid to the surviving payee after survivor continuation is not asked back from the bank) and the offset sentence. **F2 closed.**
  - The overpayment-recovery copy of "An installment paid … after the date of death that ended it is an overpayment, recorded once per installment" is still unnamed. It is limited by "the death that ended it" (O-11 partly remains).
- **release**
  - Declared: the held-after-death sentence, exclusion, withholding and **the offset sentence**.
  - The no-interest sentence is now followed (no interest).
  - "Held installments falling due after the death are forfeited rather than paid" in income_evt_overpayment_recovery is still not named. Same "death that ended it" reading as revision 1 (O-11 remains).

### factor_ladders (revision 2)

| policy | factors (label) | P/M | MS | XD |
| --- | --- | --- | --- | --- |
| arrears | installment_amount (M), investment (M), withholding (P), interest_rate (P), interest_period (M), state_tax (P) | 3/3 | yes | investment: label fixed |
| election | unchanged | 2/4 | yes | none |
| payout | taxable (M), investment (M), withholding (P), state_tax (P) | 2/2 | yes | investment: label fixed |
| reissue | investment (M), interest_rate (P), interest_period (M), state_tax (P) | 2/2 | interest_rate (state × dates), state_tax | investment: fixed |
| repayment | excess (M), entitlement (M), share_of_excess (P), **part_left_to_offset (P, new)** | 2/2 | excess, part_left_to_offset (held rows × dates × status) | none |
| release | **survivor_release_share (M)**, joint_installment (P), investment (M), withholding (P), **overpayment_offset (P, new)**, state_tax (P) | 4/2 | yes | investment: fixed |

Shape:
- Every ladder has three tiers, all stated in the rule and implemented.
- Every fall-through equals the baseline, and every `decides` is an input.

Closure checks:
- **F4 closed.** Both survivor-percentage factors are removed, and the forfeiture policy is retired. The survivor percentage now enters only as the tier parameter `P('survivor_continuation_pct')`, which is not counted as a factor. The new factors are real:
  - repayment_part_left_to_offset: what will be recovered from the held survivor share, else from the next installment due within 10 days, else nothing.
  - survivor_release_overpayment_offset: 25% of the released share when payments continue, the whole share when none continue, else nothing. That is the base offset cap made specific.
- **F5 closed.** Every state-tax ladder is now "state flat rate (0.05) of the taxable part" against "alternative state rate (0.04) of the taxable part" against 0: one formula, different numbers. The `parameter` label is honest.
- **F6 closed.** arrears_interest_period tier 2 now runs "from the date the death was first reported" when the death was reported before due proof. That runs interest from the earlier notice, which is a real treatment.
- **F7 closed (charter side).** The investment factors' `cross_difficulty` labels now read `fixed`, a product claimed by the deferred_annuity_withdrawals_and_death_benefits difficulty. Whether each world reads fixed is checked per task.
- Observations carried:
  - O-12: effect labels for analogous "which record supplies the installment" ladders still differ (arrears M, release joint_installment P).
  - O-6: unreachable fall-throughs. Commutation count; and reissue_interest_period's "no confirmed instructions → no days", which no reissue can reach because the rule requires confirmed instructions.

### findings (revision 2)

| id | round-1 status | round-2 status | bears on |
| --- | --- | --- | --- |
| F1 | SOURCE-POLICY RED | **closed** (payout overwrite names the exclusion sentence) | task 0 |
| F2 | SOURCE-POLICY RED | **closed** (repayment overwrite names the bank-first sentence; this world's deposit falls under the replacement) | task 1 |
| F3 | SOURCE-POLICY RED (charter level) | **NOT closed: narrowed.** Arrears tier 1 against the base COLA sentence is still undeclared. A second arrears installment after a post-death anniversary still gets two answers (538.88 against 544.27). | task 0's policy. No second answer on task 0's world (single arrears 2026-08-12, before the anniversary) |
| F4 | SOURCE-FACTOR RED | **closed** (ladders removed, policy retired) | task 1 |
| F5 | SOURCE-FACTOR RED | **closed** | task 0 (and arrears, reissue, release) |
| F6 | SOURCE-FACTOR RED | **closed** | task 0 |
| F7 | SOURCE-FACTOR RED (task 0) | charter labels fixed; world checked in 0.md | task 0 |
| O-1 | obs | part (b) closed, part (a) remains | — |
| O-4 | obs | closed | — |
| O-5 | obs | closed | — |
| O-11 | obs | partly closed (bank and offset sentences now named); the "held … forfeited" / "once per installment" copies remain under the "death that ended it" reading | task 1 |
| O-2, O-3, O-6, O-7, O-8, O-9, O-10, O-12, O-14 | obs | unchanged | — |
| O-15 (new) | — | obs: the release ← repayment sentence names the survivor share as waiting, although only the amount sent moves | task 1 |
| O-16 (new) | — | obs: reissue withholds at the owner's election on a payment to the survivor, against the stated rationale of the arrears and release rules | task 1 |
| O-18 (new) | — | obs: the release ← reissue gate can be resolved by this difficulty's writes only when the pre-death held installment is a returned one | task 1 |

### closing_checklist (revision 2)

Written after both round-2 reveals. Revision-1 checklist text above is unchanged.

- Audit files: 0.md and 1.md correspond to tasks/0.json and tasks/1.json, each carrying `## revision_2` appended below its revision-1 text. Comparison verdicts:
  - Task 1: **PASS**.
  - Task 0: **SOURCE-POLICY RED**, from the charter-level F3 residual in its claimed arrears policy; every other relationship passes, and the scored solution is unique on its world.
  - **The difficulty does not close.**
- Scope: charter_scope task 0 = {arrears, election, payout}; task 1 = {reissue, repayment, release}. Disjoint and jointly complete over the six extended policies; task tools match. New uuid8 7c2be31a is independent. PASS.
- Trees:
  - Task 0: n = 2, value_input 2, user write elect, acyclic.
  - Task 1: n = 2, value_input 1 (+1 state_gate), user write settle, acyclic.
  - Difficulty graph acyclic. PASS.
- Factors: every computation has 4 to 6 factors with ≥ 2 parameter and ≥ 1 method, and honest labels (F5 closed). Real ladders (F4 and F6 closed). Every factor bears weight against its baseline. All-baseline fallbacks are definite and differ from gold: 534.57, 13,282.65, 11,653.63, 962.67, 1,032.73, 962.67. Each task has a multi-source factor and a cross-difficulty factor reading **fixed** (F7 closed). PASS.
- Policy self-consistency: F1 and F2 closed. **F3 open (narrowed).** The arrears tier 1 still prices any arrears installment at the first-post-death-date amount, and the base COLA sentence still goes undeclared in the arrears `overwrite`.
- Gates: the orchestrator's round-2 snapshot (all OK, traceability deferred) is on the same hashes I audited. Not re-run, since the difficulty does not close.

## revision_3

### charter_global_frozen (revision 3)

- Same auditor. Written at about 2026-10-08T12:40Z, before either round-3 task JSON was opened.
- Inputs, re-hashed and equal to the brief:
  - extended yaml `c7454c8d98e2f4052def2a71945f5b5439ce93e48cf91c4b90968d310e1e6e54` (changed from revision 2's `86e7c53b…`)
  - task_tools.py `56c3d6f3…187d` (unchanged)
  - masked views `4942510369bd…0fbc4` and `0f7cadcb69bd…ee20b` (both byte-identical to round 2)
- Base copy still byte-identical to blueprint/products/income.yaml.
- Because the charter changed, every charter-global section is re-derived.
  - What I re-ran: all six policies, mechanically (prerequisite sentences verbatim in their rules; baseline sentences in the rules; factor lists and labels; compute evaluated on both worlds, including every factor substitution).
  - Rule text read in full for the parts that changed (arrears rule and compute; repayment and release `overwrite` and rule).
  - Unchanged from revision 2: the tool-module checks (task_tools.py hash unchanged). **Carried forward by reference** to § revision_2 / action_binding_and_uuids, on the grounds of hash `56c3d6f3…187d`.

### changes found in the charter (against revision 2)

1. **arrears rule and compute.**
   - Scope is now "every certain installment that fell due after the date of death and was never issued … paid one at a time, earliest payment date first … the earliest certain installment that fell due after the date of death with no issued payment".
   - Tier 1 now counts anniversaries "after the date of death and on or before **the arrears installment's own payment date**".
   - Tier 2 now reads "an amount is still held in suspense **for the arrears installment's payment date**".
   - New bindings `arrears_first_index`, `arrears_months_now`, `paid_first`/`paid_second`/`paid_third`, `arrears_position` and `arrears_months_back`. `held_installment` is now the held amount for that payment date, net of releases.
   - The arrears `overwrite` is unchanged: exclusion and withholding only. **The base COLA sentence is still not named.**
2. **repayment `overwrite`** now also names "An installment paid for a payment date after the date of death that ended it is an overpayment, recorded once per installment." It is replaced by "On a joint-and-survivor tier the overpayment on a deposit paid after the first death is the part of it the surviving payee was not entitled to, recorded once against that deposit." The same sentence was added to the rule.
3. **release `overwrite`** now also names "Held installments falling due after the death are forfeited rather than paid, and are never counted as overpayments." Its replaced_by is the survivor-share ladder.
4. Election, payout and reissue are unchanged in substance. All factor figures and results on both worlds are identical to revision 2 (see the per-task files).

### re-check of the round-2 open items

**F3 (arrears tier 1 against the base COLA sentence): narrowed again, still not closed.**
- The revision-2 case now agrees: for a second arrears installment after a post-death anniversary, the count runs to its own payment date.
- What remains: tier 1 anchors on "the last installment issued to the annuitant" and raises it only for anniversaries **after the date of death**. Any anniversary between that last issued installment and the death is dropped whenever tier 1 fires, i.e. whenever some anniversary has passed between the death and now.
- Demonstration, replayed with the policy's own compute on a variant of the task-0 contract:
  - Issue 2008-09-01, COLA 1%. The last installment to the annuitant is 2026-08-12 at 538.88. Anniversary 2026-09-01; death 2026-09-05.
  - Arrears 2026-09-12 (never issued). Beneficiary installments from 2026-11-12. NOW 2027-09-20, after the 2027-09-01 anniversary.
  - Compute gives anniversaries_since_death 1, position 1, held 0, anniversaries_to_arrears_date 0, so arrears_installment = **538.88**.
  - The base COLA sentence ("the installment increases by that rate, compounded, on each contract anniversary … rounded to the cent") makes the 2026-09-12 installment 538.88 × 1.01 = **544.27**.
  - Different conclusions in the same situation, and the base sentence is still not declared in the arrears `overwrite`. **SOURCE-POLICY RED, charter level.**
  - Task 0's world is unaffected: the only arrears installment is 2026-08-12, the anniversary falls after the death, and both readings give 538.88.

**O-1(a): closed.** `held_installment` now reads the held amount for the arrears installment's own payment date, net of releases, matching the rule.

New observation **O-20**: the position search checks only the first three post-death payment dates (position 4 is assumed otherwise). It also does not test that the date has already fallen due: after the 2026-08-12 arrears is paid, task 0's world returns position 3, i.e. 2026-10-12, not yet due. The rule's "fell due … never issued" has neither limit. There is no consequence for the gold write, because it is evaluated before any arrears is paid, at position 1.

**O-11: closed, with one dropped branch to note (the "check this" item).**
1. The base dedup eligibility `income_evt_overpayment_recovery.one_overpayment_per_installment` uses exactly the now-superseded sentence as its condition.
   - The replacement restores the record-once rule only "On a joint-and-survivor tier … recorded once against that deposit".
   - For every other tier (life only, cash refund, period certain), no published sentence now says an overpayment is recorded once per installment. The base dedup branch is dropped for those tiers and survives only for joint tiers.
   - This is declared, so it is legal. Its consequence for uniqueness can only arise on a non-joint contract that already carries an overpayment entry for the same deposit. Neither task world is such a contract, and no tool of this difficulty records a non-joint overpayment. → **Observation O-19 (dropped dedup branch for non-joint tiers), not RED.**
   - On task 1's joint world the replacement's "recorded once against that deposit" governs, and the settle tool books one overpayment entry against e6a9dbe1. That is consistent.
2. The release's replacement of "Held installments falling due after the death are forfeited rather than paid, and are never counted as overpayments" restates the survivor-share ladder. It does not restate "never counted as overpayments". No extended rule counts a forfeited held part as an overpayment (the release's `overpayment_outstanding` reads only identified and recovered rows), so the omission changes no quantity. Folded into O-19.

### prerequisite_graph / prerequisite_sentences / factor_ladders (revision 3)

- Unchanged from revision 2, re-verified mechanically:
  - The four edges, kinds and gates are the same; every `policy_source` is verbatim in its blocked rule.
  - Factor sets and labels are the same: arrears 3P/3M, election 2P/4M, payout 2P/2M, reissue 2P/2M, repayment 2P/2M, release 4P/2M. Every baseline sentence is in its rule.
- The new arrears tier-1 and tier-2 wording is stated in the rule, in the ladder and in compute alike.
- Observations O-15, O-16 and O-18 are unchanged.

### findings (revision 3)

| id | round-2 status | round-3 status | bears on |
| --- | --- | --- | --- |
| F3 | SOURCE-POLICY RED (charter, residual) | **still open (narrowed)**: anniversary between the last annuitant installment and the death is dropped by tier 1; base COLA sentence still undeclared | task 0's policy; no consequence on task 0's world |
| O-1(a) | obs | closed | — |
| O-11 | obs (partial) | closed; dropped non-joint dedup branch recorded as O-19 | — |
| O-19 (new) | — | obs | none on either world |
| O-20 (new) | — | obs | none on gold |
| all other F-items | closed in revision 2 | still closed (all factor figures identical to revision 2) | — |

### closing_checklist (revision 3)

Written after both round-3 reveals.

- Audit files: 0.md and 1.md each carry `## revision_3`; earlier revisions are untouched.
- Verdicts:
  - Task 1: **PASS**.
  - Task 0: **SOURCE-POLICY RED**, from the charter-level F3 residual in the claimed arrears policy. Problem tree, factors and unique solution pass on its world.
  - **The difficulty does not close.**
- Unchanged from revision 2 and re-verified:
  - Scope disjoint and complete; uuid8s independent (tools unchanged).
  - Trees: n = 2 each; value_input 2 and 1; user write in each; acyclic.
  - Factors within bounds, honest, real and weight-bearing, with definite fallbacks different from gold. Cross-difficulty factors read fixed.
- Policy self-consistency: **F3 open.**
  - The arrears tier 1 anchors on the last annuitant installment and raises it only for post-death anniversaries, so an anniversary between that installment and the death is dropped. Demonstration: 538.88 against base 544.27.
  - The base COLA sentence is still undeclared in the arrears `overwrite`.
- O-1(a) and O-11 closed. New observations O-19 (dropped non-joint dedup branch) and O-20 (arrears position search limited to three dates, with no due-date check). Neither has a consequence on either world or on gold.
- Gates: the orchestrator's round-3 snapshot (all OK, traceability deferred) is on the same hashes. Not re-run, since the difficulty does not close.

## revision_4

### charter_global_frozen (revision 4)

- Same auditor. Written before either round-4 task JSON was opened (the hash record follows in 0.md).
- Inputs, re-hashed and equal to the brief:
  - extended yaml `3d5aec7ce963bc68b6ceeaaca5f2b503495182f3f4de0ba8e34641e8edea400f` (changed from revision 3's `c7454c8d…`)
  - task_tools.py `56c3d6f3…187d` (unchanged, so § revision_2 / action_binding_and_uuids is carried forward by reference)
  - masked views `4942510369bd…0fbc4` and `0f7cadcb69bd…ee20b` (byte-identical to rounds 2 and 3)
- Base copy still verbatim.
- Charter-global checks re-run in full:
  - All six policies, mechanically: prerequisite sentences verbatim in their rules, baseline sentences in their rules, factor lists and labels, and compute on both worlds with every factor substitution.
  - Rule text read sentence by sentence for the changed policies (arrears, repayment, release).

### changes found (against revision 3)

1. **arrears**
   - **New overwrite** of the base COLA sentence ("Where a cost-of-living rate was chosen, the installment increases by that rate, compounded, on each contract anniversary from cola_first_increase_anniversary onward, rounded to the cent.").
   - Tier 1 is now anchored on "the payment date of the last installment issued to the annuitant". It raises that installment once per anniversary after that date and on or before the arrears installment's own payment date. It rounds after each of the first twelve increases and compounds any further increases in one step.
   - The selection clause now reads "the earliest certain installment that fell due after the date of death, on or before today, with no issued payment …, **taken from the first six payment dates after the death**".
   - Compute: `last_annuitant_due`, `anniversaries_since_last_installment`, six `paid_*` probes (each treating a not-yet-due date as paid), and `cola_step_1…12` plus `cola_raised_installment`.
2. **repayment**
   - Overwrite and rule now read "An overpayment on a deposit paid after a death is recorded once against that deposit; on a joint-and-survivor tier … the part of it the surviving payee was not entitled to". The record-once rule now covers every tier.
3. **release**
   - Rule sentence 1 adds "and no part of a held installment is ever counted as an overpayment".
4. Election, payout and reissue are unchanged. Every result and factor figure on both worlds is identical to revisions 2 and 3.

### re-check of the round-3 open items

**F3: closed.**
- The base COLA sentence is now named in the arrears `overwrite`, so the override is declared. The merged semantics also agree with the base COLA schedule on every case I demonstrated, replayed with the policy's own compute:
  - Revision-3 case (death 2026-09-05 after the 2026-09-01 anniversary; arrears 2026-09-12; NOW 2027-09-20): **544.27**, equal to base. Also 544.27 with NOW 2026-10-07.
  - Revision-2 case (death 2026-07-27; arrears 2026-09-12 after the 2026-09-01 anniversary, with 08-12 paid): position 2, **544.27**, equal to base.
  - Task-0 world: 08-12, no anniversary after 2026-07-12 on or before 08-12, so **538.88**, equal to base.
- The scope of the supersession is the arrears quantity, the same scoping every other overwrite in this charter uses. The commutation and release COLA wording still rests on the base sentence elsewhere (observation O-22, no consequence).
- The round-4 rounding convention ("rounded … after each of the first twelve such increases and any further increases being compounded in one step") is declared. It differs from per-anniversary rounding only after more than twelve anniversaries between the last annuitant installment and the arrears date, which no world reaches (O-23).

**O-19: closed.** The record-once rule now applies on every tier. The release's dropped "never counted as overpayments" is restored in its rule.

**O-20: closed as stated.** The position probes now treat a date not yet due as paid ("on or before today"). After the task-0 arrears is paid, compute returns the fallback position 1 rather than the not-yet-due 2026-10-12.

**New: F8, SOURCE-POLICY RED (charter level, arrears policy; regression introduced by the O-20 rework).**
- Two passages of the same arrears rule reach different conclusions in one situation:
  - Sentence A: "every certain installment that fell due after the date of death and was never issued is owed to the beneficiary now receiving the payments as an arrears installment; the arrears installments are paid one at a time, earliest payment date first, each in one payment for its payment date …"
  - Sentence B (same sentence, continued): "so the arrears installment being paid is the earliest certain installment that fell due after the date of death, on or before today, with no issued payment on the contract's activity history, **taken from the first six payment dates after the death**."
- Situation: a monthly period-certain contract whose first six post-death installments all stand issued, while the seventh fell due and was never issued (a payment skipped after the beneficiary's payments began).
  - Under A it is owed now as an arrears installment and is the earliest unissued one.
  - Under B no arrears installment can be selected, so the rule pays nothing.
  - Compute falls back to `arrears_position = 1`, i.e. the first post-death date, which already stands issued. Neither reading matches that.
- So the merged policy is not unique: pay the seventh now under A, or treat it as outside the policy and hand it off under B.
- The six-date cap is a limit of the bounded probe in compute. No income-annuity business publishes "arrears are owed only within the first six payment dates after the death". The rule states it without declaring a basis.
- Task 0's world is unaffected: its arrears installment is the first post-death date (2026-08-12), so both readings select it.

### prerequisite_graph / prerequisite_sentences / factor_ladders (revision 4)

- Unchanged from revision 2 and re-verified:
  - Four edges with the same kinds and gates; every `policy_source` verbatim.
  - Factor sets and labels: arrears 3P/3M, election 2P/4M, payout 2P/2M, reissue 2P/2M, repayment 2P/2M, release 4P/2M. Every baseline sentence is in its rule.
- The arrears_installment_amount ladder (tier 1 now "after the payment date of the last installment issued to the annuitant") is stated in the rule, in the ladder and in compute alike.
- The tier-1 condition no longer requires a post-death anniversary, but it still divides customers (none of its parts holds of every customer reaching the write).

### findings (revision 4)

| id | round-3 status | round-4 status | bears on |
| --- | --- | --- | --- |
| F3 | SOURCE-POLICY RED (charter) | **closed** | task 0 |
| O-19 | obs | closed | — |
| O-20 | obs | closed | — |
| **F8 (new)** | — | **SOURCE-POLICY RED (charter level)**: arrears rule says every unissued post-death certain installment is owed, but selects only from the first six payment dates after the death | task 0's policy; no consequence on task 0's world |
| O-22 (new) | — | obs: COLA supersession scoped to the arrears quantity | — |
| O-23 (new) | — | obs: the "first twelve increases then one-step compounding" rounding is a compute-shaped convention, reachable only after 12+ anniversaries | — |
| all other F-items | closed | still closed (all figures identical) | — |

### closing_checklist (revision 4)

Written after both round-4 reveals.

- Verdicts:
  - Task 1: **PASS**.
  - Task 0: **SOURCE-POLICY RED (F8)**. Problem tree, factors and unique solution pass on its world.
  - **The difficulty does not close.**
- F3, O-19 and O-20 are closed.
- F8 is new and was introduced by this round's O-20 rework. The arrears rule states that every unissued post-death certain installment is owed, yet selects only from the first six payment dates after the death, and compute falls back to the already-issued first date when those six are all issued.
- Scope, trees, factors, uuids and cross-difficulty are unchanged from revision 2, re-verified, and pass.
- Gates: the orchestrator's round-4 snapshot is on the same hashes. Not re-run, since the difficulty does not close.

## revision_5

### charter_global_frozen (revision 5)

- Same auditor. Written before either round-5 task JSON was opened (the hash record follows in 0.md).
- Inputs, re-hashed and equal to the brief:
  - extended yaml `c0e046c6e9ace00aa0a2b533d40ba2c6332068af01ca1a5e9cb377f19f9172bb` (changed from revision 4's `3d5aec7c…`)
  - task_tools.py `56c3d6f3…187d` (unchanged, so § revision_2 / action_binding_and_uuids is carried forward by reference)
  - masked views unchanged (`4942510369bd…`, `0f7cadcb69bd…`)
- Base copy verbatim.
- Re-run in full:
  - All six policies, mechanically: prerequisite sentences verbatim, baseline sentences in rules, factor labels (arrears MMPPMP, election MMPPMM, payout MMPP, reissue MPMP, repayment MMPP, release MPMPPP), and compute plus every factor substitution on both worlds.
  - Sentence-level read of the changed arrears and election rules.
  - Payout, reissue, repayment and release are unchanged (same rule and compute lengths and texts; all figures identical).

### changes found (against revision 4)

1. **arrears scope**, rule sentence 1: "every certain installment that fell due after the date of death and on or before the date the death claim was approved, while payments were stopped pending the claim, and was never issued is owed … as an arrears installment; installments falling due after the claim was approved are paid on the regular schedule, and when every installment of that span stands issued no arrears installment is owed."
   - Selection: "the installment whose payment date follows those already issued, counted from the first payment date after the death".
   - The six-date cap is removed. Compute gains `claim_approved_date`, `arrears_last_index`, `issued_in_span` and `arrears_index` in place of the six probes.
2. **election.**
   - The prerequisite sentence is now "The commuted value is fixed only after every certain installment that fell due between the date of death and the approval of the death claim stands issued to the beneficiary on the contract's activity history."
   - The condition reads "… on or before the date the death claim was approved …".
   - Count-ladder tier 1 now adds unissued installments "that fell due between the death and the approval of the death claim".
   - Compute `issued_since_death` and `unpaid_past` now span the first post-death date through the last payment date on or before approval.

### re-check of the round-4 open item

**F8: closed.**
- The rule no longer says that every unissued post-death installment is owed while selecting from a capped window.
- The owed set is now the span from the death to the approval of the claim, unbounded within it, and the selection reads from the same span.
- Installments after approval are expressly left to the regular schedule, so a skipped post-approval installment is outside this policy rather than owed under it. That is a stated scope limit, not a contradiction.
- Replayed with the policy's own compute:
  - **Revision-4 F8 case** (approval 2026-08-24; post-approval installments to 2027-01-12 issued; 2027-02-12 skipped): the span {2026-08-12} stands issued, so the rule says no arrears is owed. Compute index 215 lies outside the span; the policy does not apply and the rule says so, so there is no second answer.
  - **F3 cases re-verified on the new compute (no regression):**
    - Death 2026-09-05 after the 2026-09-01 anniversary, claim approved 2026-10-20, span {09-12, 10-12}: arrears 09-12 = **544.27** = base.
    - Death 2026-07-27, approval 2026-09-30, 08-12 issued: arrears 09-12, position 2 = **544.27** = base.
    - Task-0 world: span {2026-08-12} (approval 2026-08-24) gives **538.88**.

New observations (no consequence on either world or on gold):
- **O-24:** the election sentence's "between the date of death and the approval of the death claim" does not say whether an installment due on the approval date itself is included, while the arrears rule and the edge condition say "on or before". A reader resolves it through the arrears rule's explicit span. Neither world has an installment on its approval date (2026-08-24).
- **O-25:** the arrears rule asserts "the installments of the span already issued are its earliest ones". That holds when every span installment is issued only as an arrears payment in date order. An installment issued to the deceased between the death and the notice falls outside the rule's span ("while payments were stopped pending the claim") but inside compute's span (from the first post-death date). In the cases I tried, rule and compute still select the same date. Neither world has such a deposit.
- **O-26:** when the span stands fully issued, compute still evaluates to a figure for the next date, while the rule says no arrears is owed. The gold write is evaluated before that state, so nothing scored changes. This is the same pattern as revision 3's O-20.

Carried unchanged, as the reworker declared: O-15, O-16, O-18, O-22, O-23, and the other open observations listed in earlier revisions.

### findings (revision 5)

| id | round-4 status | round-5 status | bears on |
| --- | --- | --- | --- |
| F8 | SOURCE-POLICY RED (charter) | **closed** | task 0's policy |
| F1–F7 | closed | still closed (all figures identical; F3 cases re-verified) | — |
| O-24, O-25, O-26 (new) | — | obs | none |

### correction (post-reveal, revision 5)

- O-26 is withdrawn. Arrears `result` is gated `0 if arrears_index > arrears_last_index`, so a fully issued span yields 0, which matches the rule's "no arrears installment is owed". Verified by replay.
- The frozen O-26 text above is left as written.

### closing_checklist (revision 5)

Written after both round-5 reveals.

- **Audit files:** 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json, with this file alongside. Revisions 1–5 are each preserved, in order. Every revision-5 comparison section carries a **PASS**: task 0 PASS, task 1 PASS.
- **Coverage and scope:** task 0 claims {arrears, election, payout} and task 1 claims {reissue, repayment, release}. They are pairwise disjoint and jointly cover all six extended policies. The task tools match the scopes and are closed against GT. Each uuid8 (076c3375, be644418, cb4f45b9, 7c2be31a, f655a739, 80ea435e) is independently generated and frozen.
- **Trees:**
  - Task 0: 2 prerequisite problems, 2 value_input edges, owner=user write elect_commuted_value, acyclic.
  - Task 1: 2 prerequisite problems, 1 value_input + 1 state_gate edge, owner=user write settle_post_death_deposit, acyclic.
  - The difficulty-wide graph (arrears → election → payout; repayment → release; reissue → release) is a DAG.
- **Factors:** every computation declares a self-sufficient baseline with every sentence in its rule.
  - Factor counts: arrears 6 (3P/3M), election 6 (2P/4M), payout 4 (2P/2M), reissue 4 (2P/2M), repayment 4 (2P/2M), release 6 (4P/2M).
  - Every ladder has three tiers stated in full, distinct outcomes, real conditions and honest labels.
  - Every factor bears weight on its task's world. All-baseline fallbacks are definite and differ from gold: 534.57, 13,282.65, 11,653.63, 962.67, 1,032.73, 962.67.
  - Each task has a multi-source factor and a cross-difficulty factor reading the fixed annuity's cost basis (deferred_annuity_withdrawals_and_death_benefits).
- **Policy self-consistency:** F1, F2, F3 and F8 are closed. No open SOURCE-POLICY finding remains. The open observations (O-2, O-3, O-6, O-7, O-8, O-9, O-10, O-12, O-14, O-15, O-16, O-18, O-22, O-23, O-24, O-25) carry no demonstrated consequence.
- **Gates on the final form:** the orchestrator's round-5 snapshot was taken on exactly the hashes audited here (extended yaml `c0e046c6…72bb`, task_tools `56c3d6f3…187d`, tasks/0.json `d24ee85f…`, tasks/1.json `09a8d221…`, all re-checked on disk). It reads EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / CACHE-DIFF INFO / SCOPE OK. check_traceability is deferred until the income KB is published; it is outside this skill and is to be run at the render stage.
- **Result:** this difficulty passes the source-layer policy-task audit: policy self-consistency, problem tree, factors and unique solution all PASS for both tasks.
