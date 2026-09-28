# Policy-task audit — dwelling_underwriting_and_renewal / charter-global

## charter_global_frozen

- auditor: independent policy-task auditor (erl-task-policy-audit), round 1
- freeze time: 2026-09-25T00:06Z (written before any task's GT was revealed; contains nothing derived from a revealed GT)
- `tasks/dwelling_underwriting_and_renewal/dwelling.extended.yaml` sha256 `5181cd0e93d9cae340a263f4ce6d4d4e18eadfb2d5bd0c5699110f898f2622b5` (re-hashed at audit start; equals the hash supplied with the brief)
- `tasks/dwelling_underwriting_and_renewal/task_tools.py` sha256 `fcf765f55eda727ad494e7d1796e1cc686b455de7a62b52abbd7aac0a8273146` (re-hashed; equals the brief)
- read for this section: `blueprint/blueprint.yaml`, `blueprint/products/dwelling.yaml`, `blueprint/db_schema.json` (umbrella tables), `blueprint/share_tools.py` (finder and verification contracts), grep-level reads of `blueprint/products/{flood,home,umbrella}.yaml` for event and field names, the extended charter, `task_tools.py`
- masked and unread when this section was written: every task's `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`; the difficulty `worklog.md`; the scenario `worklog.md`; sibling difficulties' audit folders
- entry conditions (Step 0): the brief supplied the instantiation gate snapshot (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all exit 0; check_traceability deferred until the KB is published), and masked views `0.view.json` / `1.view.json` whose sha256 I re-computed and found equal to the brief (`a0e57e5b…`, `8a221f08…`). Entry conditions are met. A green gate only qualifies the bundle for this manual audit.
- base copy: `diff <(sed -n 1,1283p dwelling.extended.yaml) blueprint/products/dwelling.yaml` differs only by one trailing blank line, so the base section is a verbatim copy.

### policy_conflict_scan

Seven extended policies, all with trigger and target tool as follows:

| policy | trigger | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- | --- |
| dwelling_ext_vacancy_permit_charge | on_request | issue_vacancy_permit_2309bb3c (agent) | charge | [] |
| dwelling_ext_renewal_indication | state_due | record_renewal_indication_d716047a (agent) | indicated_renewal_premium | vacancy_permit_charge (value_input, vac_pct) |
| dwelling_ext_renewal_premium_paid_in_full | on_request | pay_renewal_premium_4100e9a3 (user) | amount | renewal_indication (value_input, indicated) |
| dwelling_ext_installment_fee | state_due | assess_installment_fee_8325e06b (agent) | amount | [] |
| dwelling_ext_late_fee | state_due | assess_late_fee_984fd113 (agent) | amount | [] |
| dwelling_ext_returned_payment_fee | state_due | assess_returned_payment_fee_55a26ad1 (agent) | amount | [] |
| dwelling_ext_term_payoff | on_request | pay_off_term_premium_a09f99f1 (user) | amount | installment_fee, returned_payment_fee (value_input, fees), late_fee (value_input, n_late_24) |

Overlap scan:
- Two user-owned payment policies both write `dwelling_payment_received`. Their objects are disjoint: paid-in-full is "recorded against the upcoming term" and pays the renewal term premium; pay-off is "recorded against the current term" and pays the current term's balance. No situation makes both answer the same request.
- Three fee policies all write `dwelling_fee_assessed`, disjoint by fee_code (installment_fee / late_fee / returned_payment_fee) and by object (billed installment; unpaid installment; returned payment).
- The fee policies are `state_due`: whenever a world holds a billed installment >1 without its fee, an installment unpaid past grace without a late fee, or a returned payment without its fee, the agent owes those writes whether or not a pay-off is requested. This is a cross-task hazard only if a task's world carries such a gap outside its own scope. I checked this per task (see the task files).
- `dwelling_ext_renewal_indication` is `state_due` from `renewal_offer_lead_days` before expiration. Same hazard: any task world within 45/60 days of expiration with an empty `indicated_renewal_premium` owes the indication. Checked per task.
- Base `dwelling_cancellation` (nonpayment notice after `nonpayment_notice_after_due_days`) and base `dwelling_nonrenewal` are agent actions that no extended policy claims. They could fire in a task world. Checked per task.
- Cross-category read boundaries: the indication reads home (status) and umbrella (underlying schedule). Paid-in-full reads flood (policy at the same address, claim payments) and umbrella (rental_units, status). Late fee reads home and umbrella status. Returned-payment fee reads home status and home_billing returned payments. Each is declared in `cross_category` and in `inputs.cross_category`, and none is written.
- Scope: the brief's claimed scope for this difficulty is category `dwelling`. The two trees are {paid_in_full ← renewal_indication ← vacancy_permit_charge} (task 0 as the persona frames it) and {term_payoff ← installment_fee, returned_payment_fee, late_fee} (task 1). The two trees are disjoint and together cover all 7 extended policies. Whether each task's GT actually claims exactly these sets is checked only at reveal.
- Observation (claim vs charter): the blueprint claim lists event types `dwelling_inspection_*`, `dwelling_condition_*`, `dwelling_nonrenewal_*`, `dwelling_cancellation_*`, `dwelling_renewal_offered`, `dwelling_policy_renewed` and others. The extended policies cover only `dwelling_additional_premium` (permit), `dwelling_renewal_offered`, `dwelling_payment_received`, and `dwelling_fee_assessed`. `dwelling_fee_assessed` and `dwelling_payment_received` are not in the claimed event_types list. This is a claim-coverage observation for the orchestrator, not one of the four relationships.

No conflict between extended policies that demonstrates two conclusions in one situation.

### rule_compute_equivalence

For every extended policy I read each `compute` binding against its `compute_basis` quotation and swept back through the rule sentence by sentence. The verbatim quotations are in the charter at the lines cited.

- **vacancy_permit_charge** (yaml ~1285-1437): permit_days = MN(DAYS(NOW, expiration), max_days) implements "runs through the day before the policy's expiration date … both the first and the last day counted". term_days = DAYS(effective, expiration). The four point factors use 36-month windows on `posted_date` / `loss_date` and whole-month ages from Jan 1 of year_built and from original_effective_date. vacant_days_at_start = DAYS(vacancy_start, NOW)+1 ("vacancy start date as day 1"). charged_days rounds up to 30 or 7, or is exact. result is one RND on the final figure. Every sentence of the rule has a binding, and every binding has a sentence. PASS.
- **renewal_indication** (~1439-1605): every tier of claims_pct, claims_load_pct, roof_pct, vac_pct and credit_pct is a rule sentence and a branch. trended × (1 + pct/100) takes one RND. Two gaps where compute is broader than the rule, recorded as observations because they have no consequence in either world: (a) `umbrella_schedules` counts `umbrella_underlying_scheduled` rows and ignores `umbrella_underlying_removed` / `_lapsed` (schema enum), and it does not check that the umbrella is in force, while the rule says the policy is "scheduled as underlying on a Larkspur umbrella"; (b) `latest_peril` orders by `loss_date`, while "most recent claim reported" could be read as report date. The two orders coincide in every seeded world. The prerequisite sentence is in the rule, and `vac_pct` is the binding it gates. PASS with observations.
- **renewal_premium_paid_in_full** (~1607-1790): cap_pct, capped (RND), smaller_premium, late_window, late_pct, flood_credit_pct, book_credit_pct and result (RND) all quote their sentences. Observation: `n_flood_paid` is `XCOUNT('flood','flood_claims', …)` over all of the customer's flood claim payments, while the rule scopes the payments to "a FloodGuard policy in force at that address". compute is broader than the rule whenever a customer holds more than one flood policy. No seeded world has that. PASS with observation.
- **installment_fee** (~1792-1918): fee_basis has three branches (0.8 % of amount / half of installment_fee_direct / installment_fee_direct), with returned_add, eft_credit (EFT count less returned count), tenure_credit, and result = RND(MX(0, …)). One-to-one with the rule. PASS.
- **late_fee** (~1920-2081): size_add, days_add (DAYS(latest due_date, NOW)), household_credit (home and umbrella `EXISTS in_force`), tenure_credit, repeat_factor over 24 months, and result = RND(MX(0,(late_fee+adj)×factor)). One-to-one. PASS.
- **returned_payment_fee** (~2083-2239): amount_add, channel_add (latest payment_received method), household_adj (home in force × home returned count over 12 months), tenure_credit, frequency_factor ("this one included" = count of returned rows already posted, which includes the returned row being charged), and result. One-to-one. PASS.
- **term_payoff** (~2241-2428): past_due sums every billed/fee/returned/additional/refund minus paid/credits and is floored at 0. This matches the rule's own definition of "amount past due" (it sums billed amounts regardless of due date, unlike base measure `dwelling_msr_amount_due`, which the rule does not cite). unbilled, plan_count, n_unbilled, unbilled_fees (n / min(n,1) / 0), late_load, tenure_disc, claim_free_disc and result (one RND) are all present. PASS.

Charter-global result: rule ⇄ compute are equivalent for every quantity a scored parameter depends on. No `compute` invents a basis and no rule makes an empty promise. Only the three observations above remain.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (table above). No two policies share a target tool.
- uuid8 tails: `2309bb3c`, `d716047a`, `4100e9a3`, `8325e06b`, `984fd113`, `55a26ad1`, `a09f99f1`. All seven are distinct and share no prefix. None is a sequence, a copy with a changed tail, or an adjacent value. They look independently generated. PASS.
- Docstrings: none names another tool. None states a position in a sequence or carries before/after/first as an ordering word ("the permit's first and last day" and "1 is the opening installment" name days and positions, not an order among actions). No docstring adds a confirmation, review or wait. PASS.
- Function bodies: every tool performs only `ctx.update` / `ctx.create` plus a premium_balance adjustment. None reads a prerequisite state, refuses, errors or hints. `pay_off_term_premium_a09f99f1` reads `effective_date` only to stamp the term, and `pay_renewal_premium_4100e9a3` takes term_effective_date as input. PASS: the tool layer judges no prerequisite.
- Owners: two `owner="user"` tools (both payments) and five agent tools. Each of the two trees has a user-owned root.

### prerequisite_graph

- `prerequisite` is filled on all 7 policies (`[]` on vacancy_permit_charge, installment_fee, late_fee, returned_payment_fee).
- Edges: renewal_indication → vacancy_permit_charge; paid_in_full → renewal_indication; term_payoff → installment_fee, returned_payment_fee, late_fee. Every `problem` names an extended policy id in this file, none names a base policy, and none names itself. The graph is two disjoint trees with no cycle.
- `policy_source` is verbatim in the blocked policy's own `rule` for all five edges. I located each string exactly:
  - indication: "For a building on file as vacant longer than the tier's vacancy exclusion period, the indicated renewal premium is recorded only after the policy carries a vacancy permit whose dates cover the offer date."
  - paid_in_full: "The renewal term premium is fixed only once the policy record carries the indicated renewal premium for the upcoming term."
  - payoff (1): "The pay-off amount is not fixed until every billed installment of the current term other than installment 1 carries its installment fee on the premium account."
  - payoff (2): "The pay-off amount is fixed only after each returned payment posted on the policy carries its returned-payment fee entry."
  - payoff (3): "The pay-off amount is not fixed until the premium account carries a late fee for every installment still unpaid more than the grace days after its due date."
- `form: state` on all five edges and no `fallback_reason` anywhere in the file (grep: none). This is consistent.
- `condition` is neither strengthened nor weakened relative to the sentence in any edge. Check (3)'s condition names `late_fee_grace_days`, which the sentence calls "the grace days"; the scope is the same.
- `resolved_by` is the depended-on policy's `target_tool` on every edge, and each tool writes exactly the state the `effect` describes: permit dates → `vacancy_permit_start/expiration`; indication → `indicated_renewal_premium`; three fee rows with the right fee_code and keys.
- `kind: value_input` on every edge, and each `gate` binding exists in the blocked compute (`vac_pct`, `indicated`, `fees`, `fees`, `n_late_24`). No authoring-viewpoint wording ("in this task", "at the opening") appears in any `prerequisite` field.
- Result: PASS.

### prerequisite_sentences

Four-point test per edge:

| edge | ordering connective | waited-on state (words the finders use) | no tool / id / snake_case / row id | strength = condition |
| --- | --- | --- | --- | --- |
| indication ← permit | "only after" | "policy carries a vacancy permit whose dates cover the offer date" (policy record shows vacancy permit dates) | yes | yes; the sentence's own scope clause "on file as vacant longer than the tier's vacancy exclusion period" matches the condition's "whenever … vacant for more than … vacancy_exclusion_days" |
| paid_in_full ← indication | "only once" | "the policy record carries the indicated renewal premium for the upcoming term" (finder lists "any indicated renewal premium") | yes | yes |
| payoff ← installment fee | "not … until" | billed installments other than 1 of the current term carry their installment fee on the premium account | yes | yes |
| payoff ← returned fee | "only after" | each returned payment carries its returned-payment fee entry | yes | yes |
| payoff ← late fee | "not … until" | premium account carries a late fee for every installment unpaid > grace days | yes | yes |

Uniqueness of the resolving write for each state-form edge (exactly one write in this difficulty brings the state about):
- Vacancy permit dates on the policy: only `issue_vacancy_permit_2309bb3c` writes `vacancy_permit_start/expiration`. No other task tool touches them and the shared tools are read-only plus verify/transfer. A reader who reads the rules finds `dwelling_ext_vacancy_permit_charge` ("A vacancy permit requested by the landlord starts on the date of the request …"), so one reading.
- `indicated_renewal_premium` on the policy: only `record_renewal_indication_d716047a`. The rule that describes recording it is `dwelling_ext_renewal_indication` ("When the renewal is offered, the indicated renewal premium … is"), so one reading.
- installment_fee rows: only `assess_installment_fee_8325e06b`, described by the installment-fee rule. The base trigger `dwelling_premium_billed → dwelling_fee_assessed` belongs to a billing event that no tool of this bundle performs.
- returned_payment_fee rows: only `assess_returned_payment_fee_55a26ad1`. The base trigger `dwelling_payment_returned → fee` is not performable here.
- late_fee rows: only `assess_late_fee_984fd113`.

Other checks:
- No rule carries a second wording of any of these dependencies, a tool name, or another problem's id.
- No depended-on rule restates the blocked policy's sentence (the permit, indication and three fee rules are silent about renewal payment and pay-off).
- Undeclared cross-problem orders: I swept every extended and base rule for ordering connectives that link two problems. The only hits are the five declared sentences. Base `dwelling_renewal`'s "renewal installment 1 is billed on the capped premium" is superseded (see override_declarations). Base "Payments apply oldest charge first" orders charges within one payment, not problems. Nothing else was found.
- The docstrings are silent about sequence (see action_binding_and_uuids).
- Result: PASS.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (finding half only; each consequence is demonstrated in the task files):

- **vacancy_permit_charge** vs `dwelling_occupancy_and_vacancy`:
  - The permit-charge sentence is replaced and declared in `overwrite`.
  - "issued only on a tier whose vacancy_permit_available is true, for no more than vacancy_permit_max_days, starting no earlier than the date it is requested and never retroactively" is followed. The extended rule fixes a start on the request date and an end on the day before expiration (or max days). That is one value inside the base's allowed range, not a conflict.
  - The vacancy-report, renovation-is-vacant and lease-type sentences are unaffected.
  - vs `dwelling_cancellation`: the vacancy-cancellation sentences are unaffected.
  - Observation (not a rule sentence): base `formula: vacancy_permit_charge: "term_premium * vacancy_permit_rate_pct / 100"` (unprorated) is not named in `overwrite`, and neither is `parameter_schema.vacancy_permit_rate_pct` ("prorated over the permit days"). The extended charge bills charged_days, which can exceed the permit days. Both base texts are non-rule structured fields, and base's own rule already prorates, so this finding hands no second answer through a rule sentence. Whether the rendered KB carries them is for the KB audit.
- **renewal_indication** vs `dwelling_renewal`, with `overwrite: []`:
  - "When the renewal is offered, renewal_offer_lead_days before expiration, the rating system's indicated premium for the upcoming term is recorded as indicated_renewal_premium": extended defines the indicated premium by formula and, for a renewal found late, sets "the offer date is that day". The base sentence schedules the offer. It does not say which date counts when the scheduled offer did not happen, and it gives no number. I record an observation, not a RED. The alternative reading (offer date = expiration − lead days) is self-refuting in any late-found world, because a permit "never retroactively" cannot cover a past offer date, so the indication could never be recorded. The per-task demonstration is in 0.md.
  - "and renewal installment 1 is billed on the capped premium" is superseded, but by paid_in_full's overwrite, not the indication's. Merged semantics: no bill at offer; a term paid in full is never billed. No second answer arises because no tool bills.
  - The rate-cap sentence is superseded and declared by paid_in_full.
  - The inflation-guard/roof re-evaluation sentence and the "renews … when installment 1 is paid" sentence are not scored by any extended policy.
- **renewal_premium_paid_in_full** vs `dwelling_renewal`: the rate-cap sentence and the installment-1 billing clause are both declared. Observation: base `formula: renewal_term_premium` is not named (structured field; same remark as above). vs `dwelling_billing_and_payments`: "Payments apply oldest charge first …" is compatible with a payment recorded against the upcoming term, and the refund and mortgagee sentences are untouched.
- **installment_fee** vs `dwelling_billing_and_payments`: "installment_fee_direct is charged on each installment after the first" is declared. "none of these on a mortgagee-billed term, and none when the tier amount is 0.00" is restated in the extended rule and followed.
- **late_fee**: "a late fee once per installment still unpaid more than late_fee_grace_days …" is declared. The mortgagee and 0.00 exclusions are followed.
- **returned_payment_fee**: "a returned-payment fee once per returned payment" is declared, and the exclusions are followed.
- **term_payoff**: "Each term is billed on its plan's schedule" is declared, replaced by the pay-off sentence. The installment-count sentence of base (1 / 2 / 4) is restated. The base measure `dwelling_msr_amount_due` (billed amounts due on or before the date) is not cited by the extended rule, which defines its own "amount past due" over all billed amounts. Where an installment is billed but not yet due, the two differ. Observation; the per-task check is in 1.md.

Disguised forms (anonymous intermediate factor, 0/1 multiplier, dropped branch): none found. No rule or compute_basis calls base output a "wrong value". Result: no undeclared override in a rule sentence; observations only.

### factor_ladders

Structure only; whether each factor bears weight is decided in each task's `factor_weight`. For every factor I checked that bindings are disjoint within the policy, that `decides` is an input (never `result`), that the ladder has 3 tiers that are pairwise disjoint as stated, that every tier is a rule sentence and a `compute` branch, that the fall-through equals `baseline`, and that the outcomes are pairwise distinct. All of that holds for all 34 factors below except where noted.

| policy | factor | label | honest? | multi-source | cross-difficulty |
| --- | --- | --- | --- | --- | --- |
| vacancy_permit_charge | prior_permits | parameter | yes (10/5/0 pts) | no | no |
| | building_age | parameter | yes (10/5/0) | no | no |
| | vacancy_losses | parameter | yes (8/4/0) | no | no |
| | landlord_tenure | parameter | yes (5/2/0 off) | no | no |
| | charge_day_count | method | borderline, see F-3 (ceil to 30 / ceil to 7 / exact) | no | no |
| renewal_indication | claims_count | parameter | yes (20/10/0) | no | no |
| | claim_cause_weighting | method | **no, F-1**: load × 1.5 / × 0.5 / × 1 | no | no |
| | roof_age | parameter | yes (12/6/0) | no | no |
| | vacancy_at_offer | parameter | yes (4/8/0) | vacant ∧ permit: two fields of one row, so not distinct records | no |
| | household_account_credit | parameter | yes (7/4/0) | yes (home policy ∧/∨ umbrella schedule row) | reads home (a difficulty); label says `umbrella`, see F-4 |
| paid_in_full | loyalty_cap | parameter | yes (cap−5 / cap−2 / cap) | yes (policy dates ∧ claim rows) | no |
| | payment_history_window | method | **no, F-1**: COUNT(late fees, within_months = 36 / 24 / 12) | no | no |
| | late_payment_surcharge | parameter | yes (4/2/0) | no | no |
| | flood_companion | parameter | yes (3/1/0) | yes (flood policy ∧ flood claim rows) | flood (a difficulty) |
| | rental_book_credit | parameter | yes (4/2/0) | no | label `umbrella`; umbrella is not any difficulty's category (F-4) |
| installment_fee | fee_basis_by_size | method | yes (percent of amount / half flat / flat: different inputs and algorithms) | no | no |
| | returned_payment_addon | parameter | yes | no | no |
| | eft_clearing_credit | parameter | yes | no | no |
| | installment_tenure_credit | parameter | yes | no | no |
| late_fee | late_installment_size | parameter | yes | no | no |
| | days_late | parameter | yes | no | no |
| | household_credit | parameter | yes | yes (home policy ∧/∨ umbrella policy) | home (a difficulty) |
| | late_fee_tenure_credit | parameter | yes | no | no |
| | repeat_lateness | method | **no, F-1**: adjusted fee × 2 / × 1.5 / × 1 | no | no |
| returned_payment_fee | returned_amount_size | parameter | yes | no | no |
| | payment_channel | parameter | yes | no | no |
| | household_standing | parameter | yes (−5 / +5 / 0) | yes (home policy ∧ home_billing rows) | home (a difficulty) |
| | returned_fee_tenure_credit | parameter | yes | no | no |
| | return_frequency | method | **no, F-1**: adjusted fee × 2 / × 1.5 / × 1 | no | no |
| term_payoff | payoff_installment_fees | method | yes (fee on every unbilled installment / on the next one only / none: a different set counted) | no | no |
| | late_payment_load | parameter | yes | no | no |
| | payoff_tenure_discount | parameter | yes | no | no |
| | claim_free_discount | parameter | yes | no | no |

Counts as declared: every policy has 4 to 6 factors, with ≥ 2 `parameter` and exactly 1 `method`.

Counts after the honesty test (F-1), where a factor labelled `method` whose tiers substitute a number into one formula counts as a parameter:

| policy | honest method factors |
| --- | --- |
| vacancy_permit_charge | 1 (charge_day_count, kept as borderline, F-3) |
| renewal_indication | **0** |
| paid_in_full | **0** |
| installment_fee | 1 |
| late_fee | **0** |
| returned_payment_fee | **0** |
| term_payoff | 1 |

Multi-source / cross-difficulty across the two trees: the indication/paid-in-full tree has household_account_credit, loyalty_cap and flood_companion (multi-source) and flood_companion and household_account_credit's home read (cross-difficulty). The pay-off tree has household_credit and household_standing (multi-source) and both read home (cross-difficulty). Both trees meet "≥ 1 multi-source and ≥ 1 cross-difficulty" if the task claims the whole tree (checked per task).

Realism of tiers (conditions and outcomes that the landlord-insurance line would actually use): most ladders are plausible pricing or servicing credits. Two I record as observations, because neither can be shown to be a treatment no carrier would publish:
- `term_payoff.payoff_installment_fees` charges `installment_fee_direct` on installments that the same rule says will never be billed ("a term paid off in full receives no further installment bill"), as a penalty tier for recent returned payments. Paying in full normally avoids installment service charges.
- `term_payoff.late_payment_load` adds a percentage to the unbilled premium at pay-off based on late fees already charged.

No tier reads a stamp field that names its outcome (all read counts, dates, statuses or amounts).

### findings

- **F-1 SOURCE-FACTOR RED: mislabelled `method` factors; four computations have no honest method factor.**
  - Symptom: the only `method` factor of four policies selects a number inside one fixed formula:
    - renewal_indication.claim_cause_weighting: `claims_load_pct = claims_pct × w`, w ∈ {1.5, 0.5, 1}. Rule: "the load is multiplied by 1.5 … multiplied by 0.5 … taken as it stands".
    - paid_in_full.payment_history_window: `n_late_fees = COUNT(late_fee, within_months = W)`, W ∈ {36, 24, 12}. Rule: "the window is the 36 … 24 … 12 calendar months".
    - late_fee.repeat_lateness: `result = (late_fee + adj) × m`, m ∈ {2, 1.5, 1}.
    - returned_payment_fee.return_frequency: `result = (returned_payment_fee + adj) × m`, m ∈ {2, 1.5, 1}.
  - Root cause: these factors are labelled `method`, but each tier substitutes a rate, multiplier or window length into the same algorithm. The skill's test ("a factor labelled method whose tiers only substitute a different number into the same formula (a rate, a fee, a threshold)") makes each of them a parameter.
  - Evidence: `compute` lines `claims_load_pct`, `late_window`/`n_late_fees`, `repeat_factor`/`result`, `frequency_factor`/`result` in `dwelling.extended.yaml`.
  - Demonstrated consequence: each ladder is written above as one formula with one substituted constant. After relabelling, the four policies have 0 `method` factors, below the floor of 1 per computation.
  - Affected: extended charter, `factors[]` of the four policies. Bears on task 0 (indication, paid_in_full) and task 1 (late_fee, returned_payment_fee). Consequence recorded in each task file.
- **F-2 observation: rule/compute breadth.** Three compute bindings read more than their rule sentences: the umbrella schedule count ignores removals and umbrella status; `n_flood_paid` is not scoped to the same-address flood policy; `latest_peril` orders by loss date. None changes a number in either seeded world (verified in the task files).
- **F-3 observation: charge_day_count is a borderline method.** Its tiers can be written as ceil(d/b)·b with b ∈ {30, 7, 1}, but block billing against exact-day proration is a recognised difference of charging convention. I keep it as a method, so vacancy_permit_charge keeps 1.
- **F-4 observation: cross-difficulty labels name umbrella.** `household_account_credit` and `rental_book_credit` carry `cross_difficulty: umbrella`, but no difficulty of this scenario claims umbrella. household_account_credit also reads home (a difficulty), and flood_companion reads flood, so task 0's cross-difficulty requirement does not rest on the umbrella label.
- **F-5 observation: offer-date wording** (dwelling_renewal vs renewal_indication, `overwrite: []`); see override_declarations. Bears on task 0.
- **F-6 observation: non-rule base fields** (`formula` of dwelling_occupancy_and_vacancy and dwelling_renewal, parameter_schema text) are not named by the overwrites. Bears on task 0.
- **F-7 observation: claim coverage.** The blueprint's claimed event_types (inspections, letters, cures, notices, renewals) are largely not what the extended policies exercise (fees, payments, permit charge, renewal offer).

## closing_checklist

Written after both reveals (2026-09-25T00:12Z). Everything above this heading was frozen before any reveal and has not been edited since.

| item | status |
| --- | --- |
| per-task files 0.md, 1.md match tasks 0.json, 1.json one-to-one; _difficulty.md sits alongside | yes |
| every comparison section carries PASS | **no**: both tasks are SOURCE-FACTOR RED (F-1); the blind derivations equal GT on every item, and the policy, tree and unique-solution relationships PASS for both |
| extended policies fully covered; task scopes pairwise disjoint | yes: task 0 {vacancy_permit_charge, renewal_indication, paid_in_full}, task 1 {installment_fee, returned_payment_fee, late_fee, term_payoff}; union = all 7 |
| task tools / GT closed; uuid8s independent | yes (§ action_binding_and_uuids) |
| each tree has 1–3 prerequisites, ≥ max(n−1,1) value_input edges, a user-owned write, and no cycle; whole-difficulty graph acyclic | yes (task 0: n=2, 2 value_input, user root; task 1: n=3, 3 value_input, user root) |
| every computation has a self-sufficient baseline, 4–6 factors (≥ 2 parameter, ≥ 1 method), ladders ≥ 3 tiers in the rule, factors that bear weight, and a baseline number ≠ gold | **no**: all factors bear weight and all baselines are definite and ≠ gold, but renewal_indication, paid_in_full, late_fee and returned_payment_fee have 0 honest method factors (F-1) |
| per task ≥ 1 multi-source and ≥ 1 cross-difficulty factor | yes |
| instantiation gates re-run on the final form | not run: the difficulty does not close, and there is no final form to re-run on. The gate snapshot in the brief is the only gate evidence |

Difficulty verdict: **does not pass** the source-layer audit. Both tasks are SOURCE-FACTOR RED on F-1 (mislabelled `method` factors). No SOURCE-POLICY, SOURCE-CHAIN or SOURCE-TASK red was found.

---

## revision_2

### charter_global_frozen (revision_2)

- auditor: the same independent auditor, round 2 re-audit. Written before any round-2 GT reveal, and it contains nothing derived from a round-2 GT.
- freeze time: 2026-09-25T04:02Z (UTC).
- Inputs re-hashed at the start of round 2; all equal the round-2 brief:

| file | sha256 | status |
| --- | --- | --- |
| `dwelling.extended.yaml` | `8a350df1bd1331fc0c5fbd8d3ca8458849d1a84ba2aacf9e956c0f7a26eb50aa` | **changed** since round 1 |
| `task_tools.py` | `fcf765f55eda727ad494e7d1796e1cc686b455de7a62b52abbd7aac0a8273146` | unchanged |
| `0.view.json` | `a0e57e5b…` | unchanged |
| `1.view.json` | `5cc3eb5e…` | changed |

- Base copy: `diff` against `blueprint/products/dwelling.yaml` still differs only by the trailing blank line.
- Gate snapshot supplied (all 7 green, traceability deferred). Entry conditions are met.
- Because the charter hash changed, every charter-global section is re-derived below. The round-1 sections above are left untouched.
- contamination_disclosure (round 2): in round 1 I read both tasks' round-1 GT. For computations the rework left textually unchanged (vacancy_permit_charge, installment_fee), my round-2 figures are the round-1 blind figures, which equalled round-1 GT; that knowledge cannot be un-seen. The four reworked computations (renewal_indication, paid_in_full, late_fee, returned_payment_fee), and term_payoff (downstream of them), were derived fresh under the new rules. Round-1 GT gives no value for them under the new ladders. I have not opened `tasks/*.json` in round 2 before these freezes.

### what changed in the charter (my own read, verified against round-1 text)

| policy | change |
| --- | --- |
| vacancy_permit_charge | none: rule, compute and factors re-read, labels unchanged |
| renewal_indication | `overwrite` now declares two dwelling_renewal clauses (offer timing; "the rating system's indicated premium"). The latest-claim sentence now reads "the claim with the most recent loss date". New sentence: a policy counts as scheduled only while an umbrella is in force and scheduling entries outnumber removal/lapse entries; `umbrella_schedules` implements it. `claim_cause_weighting` relabelled `parameter`. `vacancy_at_offer` is now `method`: with a covering permit the 8 % load is prorated over days from vacancy start through the permit's last day ÷ days in the expiring term; without one it is a flat 8 %; occupied gives 0. The params `vacant_with/without_permit_pct` are replaced by `vacancy_annual_pct` 8, and the edge `effect` is updated. `household_account_credit.cross_difficulty` is now `home`. |
| paid_in_full | `payment_history_window` relabelled `parameter`. `rental_book_credit` is now `method`: ≥ 4 units gives a flat 25.00 USD per unit taken off after the percentage; 2–3 units give 2 % inside the percentage; otherwise none. `cross_difficulty: null`. The overwrite `replaced_by` and `baseline.rule` add "reduced by the flat account credit". `n_flood_paid` is now scoped to the same-address FloodGuard policy (`flood_policy_id=CFIELD(…property_address…)`). |
| installment_fee | none |
| late_fee | the `late_installment_size` add-on is removed. New `method` factor `late_fee_basis`: > 1000 USD gives 1.2 % of the installment; ≤ 250 gives half the tier late_fee; otherwise the tier late_fee. `repeat_lateness` relabelled `parameter`. |
| returned_payment_fee | the `returned_amount_size` add-on is removed. New `method` factor `returned_fee_basis`: > 1000 gives the tier fee + 2 % of the excess over 1000; ≤ 100 gives half the tier fee; otherwise the tier fee. `return_frequency` relabelled `parameter`. |
| term_payoff | one sentence added to the rule, stating the business reason for the pay-off installment fees and the late-payment load. compute and factors unchanged. |

### policy_conflict_scan (revision_2)

The overlap scan is unchanged in substance. It concludes as in round 1: the payment objects are disjoint (upcoming vs current term), the fee objects are disjoint by fee_code, and the state_due hazards are checked per task. Scopes are still the two disjoint trees covering all 7 policies. F-7 (claimed event_types vs exercised events) is unchanged and kept as an observation.

### rule_compute_equivalence (revision_2)

Re-checked sentence by sentence for the changed policies:

- **renewal_indication**:
  - `permit_vacancy_days = DAYS(vacancy_start, permit_expiration)+1` ⇄ "from the vacancy start date through the permit's last day, both counted".
  - `vac_pct = 8 × permit_vacancy_days / DAYS(effective, expiration)` ⇄ "divided by the calendar days in the expiring term"; there is no intermediate rounding, which is consistent with "rounded … once, on the final figure".
  - `umbrella_schedules = (scheduled − removed − lapsed) × EXISTS(umbrella in_force)`, with credit tier "≥ 1" ⇄ "outnumber … while … in force".
  - `latest_peril` by loss_date ⇄ "most recent loss date".
  - PASS. **F-2 closed** for both of its indication items.
  - Residual observation: `inputs.history` still lists only the `umbrella_underlying_scheduled` count, not the removal/lapse counts that compute now reads. This is metadata, not a rule/compute face.
- **paid_in_full**:
  - `book_credit_pct` (2 % for 2–3 units) and `book_flat` (25 × units for ≥ 4) ⇄ the new sentence.
  - `result = RND(smaller × (1+adj/100) − book_flat)` ⇄ "increased by the account adjustment percentage, reduced by the flat account credit and rounded".
  - `n_flood_paid` scoped to the same-address policy ⇄ "no flood claim payment on that FloodGuard policy".
  - PASS. **F-2 flood item closed.**
- **late_fee**: `late_basis` three branches ⇄ the "How the late-fee basis is set …" sentence. `result = (late_basis + days_add − household − tenure) × repeat` ⇄ "late-fee basis plus the late-fee adjustment … days-late add-on minus the household credit minus the late-fee tenure credit". The removed size add-on is gone from both faces. PASS.
- **returned_payment_fee**: `fee_basis` three branches ⇄ the sentence. The adjustment is now three terms (channel + household − tenure) in both faces. PASS.
- **term_payoff**: the new sentence ("A pay-off made after repeated returned payments … stay earned; the late-payment load prices the collection cost …") states reasons and no quantity. It creates no promise that compute must implement. PASS. Wording observation: "after repeated returned payments" motivates the ≥ 2 tier, while the rule's "exactly one" tier also charges the next installment's fee. The reason sentence does not cover that tier, but it does not contradict it either.
- vacancy_permit_charge and installment_fee: unchanged text; the round-1 conclusion carries forward.

### action_binding_and_uuids (revision_2)

`task_tools.py` is unchanged (same hash). No `target_tool` or `computes` changed. The round-1 section carries forward: PASS.

### prerequisite_graph and prerequisite_sentences (revision_2)

- All five `policy_source` strings are still verbatim in their own rules. Forms are all state; there is still no `fallback_reason`; kinds and gates are unchanged.
- The indication edge's `effect` now reads "moves from the flat 8 percent to 8 percent prorated …". That matches the new compute, and `vac_pct` is still the gated binding.
- The writer of each state is still unique (tools unchanged).
- No new ordering sentence appears in any rule. The new pay-off reason sentence contains "after repeated returned payments", which describes the payment history, not an order between problems. The new umbrella-scheduling sentence has no ordering connective between problems.
- PASS; the round-1 conclusions carry forward.

### override_declarations (revision_2)

- renewal_indication `overwrite` now names "When the renewal is offered, renewal_offer_lead_days before expiration", replaced by the day-found offer sentence, and "the rating system's indicated premium … recorded as indicated_renewal_premium", replaced by the formula sentence. Both are verbatim fragments of base `dwelling_renewal`. **F-5 closed.** The offer date is now declared, not merely stated.
- paid_in_full `replaced_by` is updated for the flat credit, and it still names the same two base clauses. Declared.
- late_fee and returned_payment_fee: the amount is now a basis ladder rather than the tier figure, and it is still governed by the declared replaced clause (same analysis as round 1).
- F-6 (the base `formula:` fields and the parameter_schema proration text are not named) is unchanged and kept as an observation. It remains structured, non-rule text, and whether it surfaces is for the KB audit.
- No undeclared rule-sentence override.

### factor_ladders (revision_2)

| policy | factors (label) | honest method? | counts (p/m) |
| --- | --- | --- | --- |
| vacancy_permit_charge | unchanged: 4 p + charge_day_count m (F-3 borderline, kept) | 1 (borderline) | 4/1 |
| renewal_indication | claims_count p, claim_cause_weighting **p** (now honest), roof_age p, **vacancy_at_offer m**, household_account_credit p | vacancy_at_offer: a day-prorated load vs a flat annual load vs none. Tier 1 computes a new quantity (days from vacancy start to permit end ÷ term days); tier 2 applies a constant. Honest method (pro-rata vs flat is a genuine rating convention). | 4/1 |
| paid_in_full | loyalty_cap p, payment_history_window **p**, late_payment_surcharge p, flood_companion p, **rental_book_credit m** | rental_book_credit: a flat per-unit dollar credit taken after the percentage vs a percentage credit inside it vs none. A different algorithm, input (unit count × 25) and point of application. Honest. | 4/1 |
| installment_fee | unchanged (fee_basis_by_size m) | 1 | 3/1 |
| late_fee | **late_fee_basis m**, days_late p, household_credit p, late_fee_tenure_credit p, repeat_lateness **p** | late_fee_basis: percent of the installment amount vs half the flat fee vs the flat fee. Different inputs and algorithm. Honest. | 4/1 |
| returned_payment_fee | **returned_fee_basis m**, payment_channel p, household_standing p, returned_fee_tenure_credit p, return_frequency **p** | returned_fee_basis: flat + 2 % of the excess over 1000 vs half the flat fee vs the flat fee. An excess-percentage algorithm vs flat. Honest. | 4/1 |
| term_payoff | unchanged | 1 | 3/1 |

- Every new ladder has 3 tiers, pairwise disjoint as stated, with distinct outcomes. Every tier is in the rule and in compute, and each fall-through equals `baseline`:
  - vacancy_at_offer: baseline 0 = "occupied → no vacancy load" and equals "the standard rating percentage is zero".
  - rental_book_credit: baseline 0/0 = "standard account adjustment zero, flat credit zero".
  - late_fee_basis: P('late_fee') = "standard late-fee basis is the tier's late_fee".
  - returned_fee_basis: P('returned_payment_fee') = "standard returned-fee basis".
- Realism: percentage-of-installment late fees and excess-based returned-item fees are common servicing practice. Per-unit portfolio credits and pro-rated vacancy loads are recognisable rating devices. No tier condition holds of every customer who reaches its write, and none reads a stamp field.
- Cross-difficulty labels: household_account_credit is now `home`; rental_book_credit is now `null`; flood_companion is `flood`; the late-fee household_credit and household_standing are `home`. No label names umbrella. **F-4 closed.**
- Multi-source per tree: unchanged (household_account_credit, loyalty_cap, flood_companion; household_credit, household_standing).
- F-3 is kept as is: charge_day_count is unchanged.

**F-1 closure (charter-global half): closed.** The four mislabelled factors are now `parameter`, and each of the four affected computations carries one new `method` factor that passes the honesty test. Every computation now has at least 1 honest method factor. Whether each new factor bears weight is decided per task below.

### findings (revision_2)

- F-1: **closed** at the charter level (see above; per-task weight in 0.md and 1.md revision_2).
- F-2: **closed** (umbrella netting and in-force check, same-address flood scope, loss-date wording). New minor observation: the umbrella `inputs.history` metadata omits the removal/lapse counts.
- F-3: kept (unchanged factor); observation.
- F-4: **closed**.
- F-5: **closed** (declared overwrite).
- F-6: kept; observation.
- F-7: kept; observation.
- New observation (term_payoff): the added reason sentence motivates the "two or more returned payments" tier only. The "exactly one" tier still charges one unbilled installment's fee without a stated reason. No numeric consequence.
- No new RED at the charter level.

### closing_checklist (revision_2)

Written after both round-2 reveals (2026-09-25T04:03Z). The revision_2 charter-global sections above were frozen before the reveals and have not been edited since.

| item | status |
| --- | --- |
| per-task files match tasks one-to-one; old revisions preserved | yes (round-1 text untouched; revision_2 appended in all three files) |
| every comparison section carries PASS | yes: task 0 PASS, task 1 PASS (revision_2) |
| extended policies fully covered; scopes pairwise disjoint | yes: task 0 {permit, indication, paid_in_full}, task 1 {installment, returned, late, payoff} = all 7 |
| tools / GT closed; uuid8s independent | yes (task_tools.py unchanged) |
| trees: 1–3 prerequisites, value_input floor, user-owned write, acyclic | yes (unchanged) |
| computations: self-sufficient baseline; 4–6 factors with ≥ 2 honest parameter and ≥ 1 honest method; ladders ≥ 3 tiers in the rule; every factor bears weight; baseline ≠ gold; per task ≥ 1 multi-source and ≥ 1 cross-difficulty | yes (revision_2 factor_weight in 0.md and 1.md; F-1 closed) |
| instantiation gates on the final form | the orchestrator's round-2 snapshot (all 7 green, traceability deferred) is cited. The auditor does not re-run gates. |

Round-1 RED status: **F-1 closed** (charter and both tasks).

Observation status:

| item | status |
| --- | --- |
| F-2 | closed |
| F-4 | closed |
| F-5 | closed |
| task-1 observation 2 | closed |
| task-1 observation 4 | closed |
| F-3 | kept |
| F-6 | kept |
| F-7 | kept |
| task-0 observation 2 | kept |
| task-1 observation 3 | kept |
| new: umbrella `inputs.history` metadata omits removal/lapse counts | new, minor |
| new: the pay-off reason sentence covers only the ≥ 2-return tier | new, minor |

Difficulty verdict (revision_2): **passes** the source-layer audit. There is no SOURCE-POLICY, SOURCE-CHAIN, SOURCE-FACTOR or SOURCE-TASK red.
