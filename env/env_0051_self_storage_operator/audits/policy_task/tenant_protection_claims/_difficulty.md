# Policy-task audit — tenant_protection_claims / charter-global

## charter_global_frozen

- auditor: erl-task-policy-audit (independent auditor agent; did not author the artifacts)
- freeze time: first written 2026-10-10T19:37Z, last pre-reveal edit 19:46:43Z (F1 demonstration note, from the masked view, not GT); GT first opened 19:46:46Z
- freeze hashes (re-computed by the auditor, equal to the coordinator's brief):
  - `tasks/tenant_protection_claims/protect.extended.yaml` sha256=512ebd4f529d97c71fa1aaf7db2214b3ed13f63088d6fda0ac917437d04d7bbc
  - `tasks/tenant_protection_claims/task_tools.py` sha256=c7a7ccbb6506cc5484bca2cfd8536888ebee38813c59669ee4ca1ec34692ca2f
- read for this section: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/protect.yaml`
  (+ the `unit` and `autopay` variant tables for the cross-category parameters the computes read), the extended charter, `task_tools.py`,
  and the DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py::build_env` (SUM/COUNT/LATEST are scoped to the target
  plan; `within_months=k` keeps rows with `0 <= MONTHS(date, NOW) < k`; `F()` reads the target plan row; `P()` reads the variant
  parameters of the plan's *current* `variant_name`).
- masked and not read: every field of tasks/*.json other than `frozen_time`, `user_scenario`, `initial_state` (evaluation_criteria,
  computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure*).
- Entry conditions (Step 0): gate snapshot supplied by the coordinator — check_extended EXTENDED OK, check_task_tools TASK TOOL CONTRACT OK,
  replay_tasks REPLAY OK, check_solvability SOLVABILITY OK, check_compute COMPUTE OK, check_grounding GROUNDING OK, check_cross_fire
  SCOPE OK; check_traceability deferred (needs the rendered KB); validate_scenario only `required document ... not found`. Masked views
  supplied with hashes, re-verified: 0.view.json fd278eca…, 1.view.json f69ca2bf…. Entry conditions met.

The base section of the extended charter was compared key by key with `blueprint/products/protect.yaml` (category, display_name,
binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies): all identical; the only added key is
`extended_policies`. The base copy is verbatim.

Extended policies (7), target tools and owners:

| policy | target_tool | owner | prerequisite edges |
| --- | --- | --- | --- |
| protect_ext_fee_error_credit | credit_protection_fee_error_2320aa46 | agent | [] |
| protect_ext_first_claim_decision | record_claim_decision_61f94ad8 | agent | [] |
| protect_ext_recovery_repayment | repay_recovered_claim_money_180976c0 | **user** | first_claim_decision (state_gate), fee_error_credit (value_input `credit_offset`) |
| protect_ext_reconsideration_decision | record_reconsideration_decision_ea5df16d | agent | duplicate_payment_repayment (value_input `room`), late_claim_payment (value_input `history_factor`), credit_balance_refund (state_gate) |
| protect_ext_duplicate_payment_repayment | repay_duplicate_claim_payment_968ba4e6 | **user** | [] |
| protect_ext_late_claim_payment | issue_late_claim_payment_da72d11f | agent | duplicate_payment_repayment (state_gate) |
| protect_ext_credit_balance_refund | refund_plan_credit_balance_dd5eed31 | agent | [] |

### policy_conflict_scan

The prerequisite graph splits the seven policies into two connected components:

- component A (root `protect_ext_recovery_repayment`): {recovery_repayment, first_claim_decision, fee_error_credit} — 2 prerequisite
  problems, 1 value_input edge (floor max(2-1,1)=1 met), one `owner=user` write (the root).
- component B (root `protect_ext_reconsideration_decision`): {reconsideration_decision, duplicate_payment_repayment, late_claim_payment,
  credit_balance_refund} — 3 prerequisite problems, 2 value_input edges (floor max(3-1,1)=2 met), one `owner=user` write
  (duplicate_payment_repayment); late_claim_payment additionally waits on duplicate_payment_repayment.

The two components are disjoint and together cover all seven extended policies, so two task scopes built on them (one per task, M=2) are
mutually exclusive and jointly complete. Which task holds which component is established per task from its own `user_scenario` in the
task files (charter_scope is masked).

Overlapping subjects across policies:

- `protect_claim_decision` is the subject of first_claim_decision and reconsideration_decision (and of base claim_eligibility /
  claim_settlement / reconsideration / annual_aggregate). The two extended policies are separated by the decision history of the claim:
  first decision = "a claim that carries no claim decision yet"; reconsideration = "replaces the latest decision on a claim when the
  tenant supplies, within the reconsideration window, a document that was not on file at that decision". Disjoint by state.
- `protect_claim_payment_voided` is the subject of recovery_repayment (void reason stolen_property_recovered, earliest payment) and
  duplicate_payment_repayment (void reason issued_in_error, the most recent mailed-check payment). Disjoint by trigger (stolen property
  recovered vs a second payment issued in error); both are bounded by the inherited base dedup "Each payment is voided at most once."
- `protect_premium_credit` (fee_error_credit) and `protect_premium_refund` (credit_balance_refund) both act on `premium_balance_due`
  but on distinct event families; the refund policy reads the credit's `credit_type` and date (cross-policy read, no conflict).
- Cross-category read boundaries: every compute reads `unit` (move-in date, rent reversals, class features) and fee_error_credit /
  late_claim_payment read `autopay`; no policy writes another category.

Charter-level conflicts found by this scan are listed under `override_declarations` and `findings` (F1–F3).

### rule_compute_equivalence

Per policy, every compute binding has a `compute_basis` quotation that is a sentence fragment of the policy's own `rule`; swept back
sentence by sentence:

- **fee_error_credit**: charge_amount/charge_period (latest charge by entry_date), period_charges/error_amount ("second charge for a
  billing period already charged"), period_collections/service_base (twice / once / otherwise), tenure_months+rent_reversals+tenure_share,
  earlier_corrections+repeat_share, autopay_drafts+autopay_share, service_credit, result (rounded once) — all quoted and implemented.
  Two equivalence edges noted, judged per world: (a) the rule says "collected twice" and the compute takes `>= 2`; (b) "AutoPay drafts
  were submitted" is implemented as every `autopay_draft` row (retries and `skipped_over_cap` rows included) — a world with such rows
  gives "submitted" a second reading. Neither is a defect in a world without such rows.
- **first_claim_decision**: claim/loss_date/peril (LATEST by filed_date on the plan), the six assessed values (latest assessment),
  plan_months+jewelry_cap, alarm_e+drive_up_e+electronics_cap, humidity_c+temperature_c+collectibles_cap, settled_total,
  drive_up_d+deductible_base, rental_months+rent_reversals+tenure_share, paid_claims+history_factor, deductible, payable,
  paid_12m/voided_12m/own_paid_12m/own_voided_12m+room, result — all quoted and implemented. Edges noted: `paid_claims` counts rows
  whose `claim_status` is `paid` (the rule says "paid claims"; the base measure `protect_msr_claims_paid_count_365d` counts claims with a
  payment not fully voided — a world where the two differ gives a second reading); the voids netted in `room` are voids *dated* in the
  window.
- **recovery_repayment**: as above plus net_paid (all payments minus all voids on the claim), `*_was` = MAX over assessments,
  before_total, recovery_days+deductible_kept, entitlement_after, credit_offset (= max(0, −premium_balance_due) of the target plan),
  result. Edge noted: `other_paid_claims = COUNT(paid claims in 36 months) - 1` hard-codes that the repaid claim is itself a paid claim
  with a loss date in the window; the rule says "other paid claims", which is exact only when that holds (checked per world).
- **reconsideration_decision**: identical structure to first_claim_decision with "reconsideration" wording; same edges.
- **duplicate_payment_repayment**: claim = claim of the most recent mailed-check payment (LATEST by event_date), entitlement, result;
  `other_paid_claims` carries the same "-1" hard-coding as recovery_repayment.
- **late_claim_payment**: claim = most recently filed claim with claim_status approved; outstanding, days_late (= days_late_r, a
  duplicate binding kept only to give two factors disjoint binding sets), late_rate, work_order+peril+failure_uplift, tenure uplift,
  autopay_method+autopay_uplift, interest_rate, late_period, result — all quoted and implemented.
- **credit_balance_refund**: collected/credited/charged/refunded/credit_balance, credit_date/days_late (= days_late_r), late_rate,
  credit_kind+source_uplift, ended_on+rental_months+tenure_uplift, interest_period, result — all quoted and implemented.

Every declared factor's ladder tiers appear as rule sentences and as branches of the `decides` binding, and every branch of each
`decides` binding is a tier the rule states. No rule sentence about a computed quantity is left without a binding (the collectibles cap
of first_claim_decision / recovery_repayment / duplicate_payment_repayment is in rule and compute but is not declared as a factor —
a compute binding, not a factor; no defect). No compute invents a basis absent from the rule.

One inherited-basis divergence that is not a rule/compute mismatch inside the extended policy but a merged-semantics one: every
`P(...)` reads the plan's **current** level, while the inherited base sentence of protect_evt_claim_settlement (not superseded) says
"Every limit, sublimit and deductible is taken from the coverage level in force on the loss date, which can differ from the plan's
current level when a coverage change took effect after the loss." A world with a coverage change between loss date and handling date
would split the two readings — checked per task (F2).

### action_binding_and_uuids

- Each `(target_tool, computes=amount)` is claimed by exactly one policy (7 tools, 7 policies, no reuse).
- No task tool checks eligibility, ordering, amounts or prerequisites: every body only finds the anchor row, creates one event row and
  updates `premium_balance_due` / `claims_paid_total` / `claim_status` (task_tools.py lines 36-52, 90-103, 130-143, 176-188, 213-227,
  248-264, 286-297). No tool refuses, errors or hints on an unresolved prerequisite.
- Docstrings name no other tool, state no sequence position. The only ordering words are "rounded half up to the cent before it is
  entered" (argument formatting, not a sequence) and "replacing its earlier decision" (describes the object). Observation only.
- uuid8 tails: 2320aa46, 61f94ad8, 180976c0, ea5df16d, 968ba4e6, da72d11f, dd5eed31 — pairwise distinct, no shared prefix, no sequence
  or adjacency pattern. PASS.
- Tool effect note: `record_claim_decision_61f94ad8` and `record_reconsideration_decision_ea5df16d` both create a
  `protect_claim_decision` row; the business separation is by the claim's decision history (see policy_conflict_scan), so a state
  "carries a claim decision" on a claim with no decision is brought about only by the first-decision write.

### prerequisite_graph

- `prerequisite` filled in on all 7 policies (`[]` on four).
- Every `problem` is an extended policy id of this file; none points at a base policy or at itself.
- Graph: recovery→{first_decision, fee_error}; reconsideration→{duplicate, late, credit_refund}; late→duplicate. Acyclic.
- Every `policy_source` is verbatim locatable in the blocked policy's own `rule` (recovery rule lines 1639-1642; reconsideration rule
  lines 1942-1946; late rule lines 2439-2440).
- All six edges declare `form: state`, none carries `fallback_reason` — consistent.
- `resolved_by` equals the depended-on policy's `target_tool` on all six edges.
- `kind`/`gate`: value_input gates `credit_offset` (recovery compute), `room` and `history_factor` (reconsideration compute) exist;
  state_gate gates `protect_claim_events.decision`, `protect_premiums.event_type`, `protect_claim_events.void_reason` are real fields.
- No authoring-viewpoint wording ("in this task", "at the opening") in any `prerequisite` text.
- `condition` vs sentence scope: see prerequisite_sentences — three conditions are scoped "on the plan" while their sentences are not
  (F4); the strengthening/weakening is judged on each world.

### prerequisite_sentences

Four-point test per edge:

| edge | sentence (own rule) | connective | waited-on state | tool/id/snake_case | strength vs condition |
| --- | --- | --- | --- | --- | --- |
| recovery ← first_decision | "The recovery repayment on a claim is fixed only after every claim filed under the same police report number on the tenant's other protected units carries a claim decision." | only after | claim carries a claim decision (decision row) | none | matches condition (other plans, same police report number) |
| recovery ← fee_error | "The recovery repayment is not fixed until every protection fee charged a second time for the same billing period carries a billing-error credit on the fee ledger." | not until | second charge carries a billing-error credit | none ("billing-error credit" is business wording) | sentence unscoped (every such fee of the tenant); condition "on the plan" — broader (F4) |
| recon ← duplicate | "The reconsidered amount is fixed only after every claim payment issued a second time for an approval already paid carries a repayment void on the claim's handling history." | only after | second payment carries a repayment void | none | sentence unscoped; condition "on the plan" (F4) |
| recon ← late | "The reconsidered amount is not fixed until every approval standing on the plan's other claims carries a claim payment." | not until | approval carries a claim payment | none | matches |
| recon ← credit_refund | "The reconsidered amount is fixed only after every credit balance left on the tenant's ended protection plans carries a fee refund." | only after | credit balance carries a fee refund | none | matches |
| late ← duplicate | "A late claim payment is issued only once every second payment that a mailed check made on an already paid approval carries a repayment void." | only once | mailed-check second payment carries a repayment void | none | sentence unscoped; condition "on the plan" (F4) |

Single-write test (state form): "claim decision" on an undecided claim → only record_claim_decision (the reconsideration policy needs an
existing decision); "billing-error credit" → only credit_protection_fee_error; "repayment void" on a second payment issued in error →
repay_duplicate (repay_recovered also writes a void but its rule is for stolen property recovered, and the two rules separate the
trigger); "claim payment" on an approval → only issue_late_claim_payment (no other payment tool in this difficulty); "fee refund" → only
refund_plan_credit_balance. Each state has exactly one resolving write in this difficulty. PASS.

Derivation sentence + records + depended-on rule → action, one reading each:
- "claim … on the tenant's other protected units carries a claim decision": records = other plan's claim with same
  `police_report_number` and no decision row; first_claim_decision rule "A first decision answers a claim that carries no claim decision
  yet" → record_claim_decision on that claim.
- "fee charged a second time … carries a billing-error credit": records = two `protect_premium_charge` rows with one `period_start`, no
  credit referencing the second; fee_error_credit rule → credit_protection_fee_error on that plan.
- "claim payment issued a second time … carries a repayment void": records = second (mailed-check) payment after a first payment on the
  same approval; duplicate rule → the tenant's repayment (owner=user hand-over).
- "approval … carries a claim payment": records = other claim with approved status and no payment; late rule → issue_late_claim_payment.
- "credit balance left on … ended protection plans carries a fee refund": records = cancelled/terminated plan with negative
  `premium_balance_due`; credit refund rule → refund_plan_credit_balance.

No second wording of any dependency, no tool name, no other policy id appears in any extended rule; no depended-on rule restates the
sentence. Docstrings are silent about sequence.

Undeclared cross-problem orders in rules: the reconsideration rule's "replaces the latest decision on a claim" presupposes an earlier
decision (eligibility on the seeded history, not a cross-problem order of this tree); the base claim_eligibility sentence "A claimed
amount above inventory_list_required_over_usd needs an itemized inventory with proof of ownership, and above adjuster_inspection_over_usd
an adjuster inspection, before a decision" is a base order between document handling and a decision — it grounds no edge; whether it
bites is judged on each world (task tool set holds no document-request tool).

### override_declarations

Sentence by sentence against each `base_policy_refs` entry (finding half only):

**protect_ext_fee_error_credit vs protect_evt_fee_billing**
- "fee of the level in force … billed in full and never prorated" / "billed only while active or lapsed" / "Each billing period is billed
  once" / "collected with the rent" — followed (not governed by the credit).
- "A fee billed for a period that starts after the plan's cancellation or termination date, or a second fee for the same period, is a
  billing error and is credited in full as billing_error_correction." — declared superseded; replacement adds the service credit.
  The extended rule defines billing error only as "a second charge for a billing period already charged" and examines only the latest
  charge: the base branch "a fee billed for a period that starts after the plan's cancellation or termination date" is no longer produced
  (dropped branch, declared by the superseding of the whole sentence). Bites only in a world with such a charge — per task.
- free-look sentence — declared superseded by "A billing-error correction is credited whatever the plan's enrollment date"; the base
  sentence never governed billing-error corrections, so no conflict existed; the declaration is harmless for billing-error credits
  (observation O1).
- "A credit balance left on a cancelled or terminated plan is refunded … within 21 calendar days" — governed by credit_balance_refund,
  declared there.

**protect_ext_first_claim_decision vs annual_aggregate, claim_eligibility, claim_settlement, reconsideration**
- annual_aggregate, "Within one plan, the total paid on claims whose loss dates fall in any rolling 365-day window, measured by
  protect_msr_paid_365d, may not exceed coverage_limit_usd times aggregate_limit_multiple of the level in force on the loss date being
  decided; an approval is reduced to the room left under that aggregate" — **handled differently and NOT declared**: the extended rule
  measures "the claim payments, net of voids, issued under the plan in the 12 whole months before the handling date on claims other than
  the claim decided" (window keyed on payment dates ending at the handling date) where the base measure `protect_msr_paid_365d` keys on
  claims' *loss dates* in the 365 days ending on the *loss date being decided*. Neither `overwrite` entry names this sentence (F1).
- annual_aggregate, "The plan pays at most max_claims_per_12_months claims … a further claim is denied with reason
  claim_count_limit_reached" — not superseded, inherited; the extended rule is silent. Bites only where the count is reached — per task.
- claim_eligibility (in force, perils, filing deadline, police report / forced entry, documents before decision, exclusions, notice,
  photos) — not superseded; inherited in full; judged per world.
- claim_settlement, "The payable amount is … minus deductible_usd once per occurrence, and never below zero." — declared superseded.
- claim_settlement, "Every limit, sublimit and deductible is taken from the coverage level in force on the loss date …" — not superseded,
  inherited, but every `P()` reads the plan's current level (F2; bites only with a level change after the loss date).
- claim_settlement, "approved_full / approved_partial / zero is a denial" — followed. "paid within claim_payment_issue_days … each approval
  paid once" — not this write.
- reconsideration, window sentence — declared superseded; no conflict existed for a first decision (observation O1).

**protect_ext_recovery_repayment vs protect_evt_claim_payment_void**
- "When stolen property is recovered after payment, the tenant repays …" — declared superseded.
- "A claim payment is voided in full when it was issued in error or returned undeliverable…" — not this trigger.
- "Each payment is voided at most once." — inherited; the extended rule records the void "of the earliest claim payment issued on the
  claim" — a world in which that payment already carries a void would make the two clash (per task).

**protect_ext_reconsideration_decision vs annual_aggregate, claim_eligibility, claim_settlement, reconsideration**
- Same undeclared aggregate-window override as first_claim_decision (F1).
- claim_settlement payable sentence — declared superseded.
- reconsideration: "may ask once … by supplying a document that was not on file at the first decision", the window sentence, "The new
  decision replaces the earlier one; any increase over the amount already paid is paid as a new claim payment, and the earlier payment
  stands", "A disagreement about the assessed actual cash value itself, without a new document, is not reconsidered" — not superseded,
  inherited; the extended rule restates the first two. The "increase … is paid as a new claim payment" sentence is inherited; whether the
  scored solution must also carry that payment is judged per task.
- Same F2 level-in-force issue.

**protect_ext_duplicate_payment_repayment vs protect_evt_claim_payment_void**
- "A claim payment is voided in full when it was issued in error or returned undeliverable; an undeliverable payment is reissued …" —
  declared superseded. "Each payment is voided at most once" — inherited.

**protect_ext_late_claim_payment vs annual_aggregate, claim_settlement**
- "The approved amount is paid within claim_payment_issue_days … each approval is paid once." — declared superseded.
- annual_aggregate cap — not superseded, inherited; the late payment (approved amount + interest) is not bounded by the room in the
  extended rule; bites only where the plan's aggregate room is below the payment (per task).
- "Every limit … from the level in force on the loss date" — `claim_payment_issue_days` is read from the current level (F2).

**protect_ext_credit_balance_refund vs protect_evt_fee_billing**
- 21-day refund sentence — declared superseded. Other sentences not governed.

### factor_ladders

| policy | factor | effect | decides | tiers (incl. fall-through) | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| fee_error_credit | service_credit_base | method | service_base | 3 (both collections / charge alone / none) | no (one table) | – |
| | tenure_service_share | parameter | tenure_share | 3 (0.5 / 0.25 / 0) | yes (unit_rentals.move_in_date ∧ unit_ledger reversals) | unit |
| | repeat_error_share | parameter | repeat_share | 3 (0.5 / 0.25 / 0) | no | – |
| | autopay_service_share | parameter | autopay_share | 3 (0.25 / 0.1 / 0) | no | autopay |
| first_claim_decision | decision_jewelry_cap | parameter | jewelry_cap | 3 (×1.5 / ×1.2 / ×1) | no | – |
| | decision_electronics_cap | parameter | electronics_cap | 3 (×1.5 / ×1.25 / ×1) | tier 2 is a conjunction of two fields of one class row | unit |
| | decision_burglary_deductible_base | method | deductible_base | 3 (10% floor / 5% floor / flat) | yes (claim peril ∧ unit class drive-up) | unit |
| | decision_tenure_share | parameter | tenure_share | 3 (0.5 / 0.75 / 1) | yes | unit |
| | decision_claim_history | parameter | history_factor | 4 (1.75 / 1.5 / 1.25 / 1) | no | – |
| recovery_repayment | resettlement_jewelry_cap / _electronics_cap / _burglary_deductible_base / _tenure_share / _claim_history | as above | | as above | as above | as above |
| | recovery_deductible_restoration | method | deductible_kept | 3 (none / proportional / full) | no | – |
| reconsideration_decision | reconsideration_jewelry / electronics / burglary base / tenure / claim_history | as first decision | | | | |
| | reconsideration_collectibles_cap | parameter | collectibles_cap | 3 (×1.5 / ×1.25 / ×1) | no | unit |
| duplicate_payment_repayment | duplicate_jewelry / electronics / burglary base / tenure / claim_history | as first decision | | | | |
| late_claim_payment | late_payment_rate | parameter | late_rate | 4 (0.18 / 0.12 / 0.06 / 0) | no | – |
| | late_interest_period | method | late_period | 3 (/360 / /365 / 30-day months÷12) | no | – |
| | building_failure_uplift | parameter | failure_uplift | 3 (0.03 / 0.01 / 0) | two fields of the claim row | – |
| | late_payment_tenure_uplift | parameter | tenure_uplift | 3 (0.02 / 0.01 / 0) | yes | unit |
| | late_payment_autopay_uplift | parameter | autopay_uplift | 3 (0.01 / 0.005 / 0) | no | autopay |
| credit_balance_refund | late_refund_rate | parameter | late_rate | 3 (0.12 / 0.06 / 0) | no | – |
| | refund_credit_source_uplift | parameter | source_uplift | 3 (0.03 / 0.01 / 0) | no | – |
| | refund_tenure_uplift | parameter | tenure_uplift | 3 (0.02 / 0.01 / 0) | no (one date pair) | unit |
| | refund_interest_period | method | interest_period | 3 (/365 / months÷12 / none) | no | – |

Counts per policy (declared): fee_error 4 (3 parameter, 1 method); first_decision 5 (4/1); recovery 6 (4/2); reconsideration 6 (5/1);
duplicate 5 (4/1); late 5 (4/1); credit_refund 4 (3/1). All within 4–6, ≥2 parameter, ≥1 method as declared.

Structure checks:
- `decides` is an input binding (never `result`) for every factor; binding sets within each policy are disjoint (late and credit_refund
  achieve this only through duplicate `days_late_r` bindings — observation).
- Every tier is stated in the `rule` with its condition and value/method, and implemented in the `decides` binding. Every fall-through
  tier equals the factor's `baseline` and the policy `baseline.rule` (fee_error: "adds no service credit" ⇒ every share 0 and base 0;
  claim policies: sublimits ×1, flat deductible_usd, tenure share 1, history 1; recovery restoration: full deductible, which equals
  deductible_usd when every other factor is at baseline; late: no interest; refund: no interest).
- No two tiers of one ladder select the same value or method.
- Labels: `method` factors change the algorithm (base quantity of the service credit; percentage-of-total vs flat deductible;
  proportional vs none vs full kept deductible; day-count convention; interest-period convention); `parameter` factors change a number.
  Honest.
- Reachability / realism of tiers (the "unreal ladder" test):
  - **late_interest_period**: tiers are keyed on the plan level's `claim_payment_issue_days` (≤7 → /360; 8–10 → /365; otherwise 30-day
    months ÷ 12). The charter's six levels carry `claim_payment_issue_days` 10, 10, 10, 10, 7, 7 (protect.extended.yaml lines 108, 162,
    216, 270, 324, 378) — no level has more than 10, so the fall-through (= the baseline method) is
    selected for no customer of any level. The ladder has two reachable tiers (F5).
  - **refund_interest_period**: tiers are "ended by termination" / "ended by cancellation" / otherwise. The policy's own scope is "A credit
    balance left on a cancelled or terminated plan", so every customer who reaches this write is on tier 1 or tier 2 and the fall-through
    "no interest period is counted" holds of no customer who reaches the write; the ladder has two reachable tiers (F5).
  - **late_payment_autopay_uplift**: the late-payment interest on a claim payment is raised by 0.01 a year when the covered rental's rent
    AutoPay draws on a bank account and by 0.005 when it draws on a card. How a tenant pays rent has no bearing on the time value of claim
    money paid late to them by direct deposit; no contents-protection or insurance business varies late-claim interest by the customer's
    rent payment method (F6).
  - Other ladders (tenure / loyalty shares, repeat-error goodwill, security-feature sublimits, percentage burglary deductibles by
    exposure, claim-history deductible loading, prompt-recovery deductible restoration, late-payment rate by days late, building-failure
    uplift, credit-source uplift) are treatments a storage/contents-protection business can plausibly publish; no finding.
- Multi-source / cross-difficulty per component (judged per task on the factors that survive): component A has multi-source factors
  (tenure shares; burglary deductible base) and cross-difficulty factors reading `unit` and `autopay`; component B has the same through
  reconsideration / duplicate (unit) and late (unit, autopay).

### findings

- **F1 — SOURCE-POLICY (finding; consequence per task): undeclared override of the annual-aggregate window.** Base
  protect_agg_annual_aggregate: "Within one plan, the total paid on claims whose loss dates fall in any rolling 365-day window, measured
  by protect_msr_paid_365d, may not exceed coverage_limit_usd times aggregate_limit_multiple of the level in force on the loss date being
  decided; an approval is reduced to the room left under that aggregate", with `protect_msr_paid_365d` = "Rolling 365 calendar days of
  loss dates ending on the loss date of the claim being decided … Sum of protect_claim_payment amounts minus protect_claim_payment_voided
  amounts on claims of this plan whose loss_date falls in the window." Extended first_claim_decision and reconsideration_decision:
  "The room under the annual aggregate is coverage_limit_usd times aggregate_limit_multiple minus the claim payments, net of voids, issued
  under the plan in the 12 whole months before the handling date on claims other than the claim decided". Neither policy's `overwrite`
  names the base sentence. Bears on whichever task decides a claim (both components: first_claim_decision in A, reconsideration_decision in
  B). Whether it produces a second scored value is demonstrated (or not) in each task file. Demonstrated as a SOURCE-POLICY RED on
  task 1's world (from its masked initial_state, not from GT): the seeded 2026-09-01 decision on claim 33eb605d gets room 1018.44 under
  the extended clause and 5000 under the base clause, and with the duplicate repayment skipped the reconsideration gets 561.12 vs 4398.75
  (`1.md` § policy_self_consistency). Task 0's world gives the same room under both clauses (`0.md`).
- **F2 — observation (consequence per task): level in force on the loss date vs current level.** Every `P()` in the claim computes and
  the late payment's `claim_payment_issue_days` read the plan's current level; the inherited base sentence requires the level in force on
  the loss date. Bites only in a world where `protect_plan_changes` shows a change effective after the loss date.
- **F3 — observation: inherited base gates the extended rules are silent on** — claim count limit (annual_aggregate), documents /
  adjuster inspection before a decision (claim_eligibility), "Each payment is voided at most once", "any increase over the amount already
  paid is paid as a new claim payment" (reconsideration), the dropped post-cancellation branch of billing error. Each is checked on each
  world; a RED arises only where the world triggers it.
- **F4 — observation (consequence per task): three prerequisite sentences broader than their conditions.** recovery←fee_error,
  recon←duplicate and late←duplicate sentences name every such fee/payment of the tenant while their `condition` says "on the plan". A
  world where another plan of the customer carries an uncredited second fee charge or an unvoided second mailed-check payment would give
  the sentence a second resolving action; checked per world.
- **F5 — SOURCE-FACTOR (finding; consequence in the task holding component B): two `method` ladders with an unreachable fall-through.**
  late_claim_payment.late_interest_period (no level has claim_payment_issue_days > 10) and credit_balance_refund.refund_interest_period
  (every plan reaching the refund write ended by termination or cancellation). Each ladder has only two tiers any customer can be on, so
  neither passes "a ladder of at least three pairwise-disjoint tiers"; and in both policies it is the only `method` factor.
- **F6 — SOURCE-FACTOR (finding; consequence in the task holding component B): unreal condition** — late_claim_payment.
  late_payment_autopay_uplift ties late-claim interest to the rent AutoPay method (see factor_ladders).
- **O1 — observation**: two declared "overwrites" replace base sentences that never conflicted (fee_error_credit's free-look sentence;
  first_claim_decision's reconsideration-window sentence). Harmless as declarations; noted because the merged text now reads as if those
  base limits were withdrawn.
- **O2 — observation**: tool docstrings carry the ordering word "before" only in argument formatting ("rounded half up to the cent before
  it is entered").

## closing_checklist

Written 2026-10-10 after both tasks' frozen derivations and comparisons were on disk (post-reveal section; nothing above this heading was
derived from a revealed GT).

- Per-task audit files correspond one-to-one with tasks/0.json and tasks/1.json (`0.md`, `1.md`); first revision, no older revisions.
- Comparison verdicts: task 0 **PASS** (per-task; cites F1); task 1 **SOURCE-POLICY RED, SOURCE-FACTOR RED, SOURCE-TASK RED**. Not every
  comparison carries a PASS → **the difficulty does not close** at the source layer.
- Coverage and scopes: charter_scope task 0 = {first_claim_decision, fee_error_credit, recovery_repayment}, task 1 =
  {credit_balance_refund, duplicate_payment_repayment, late_claim_payment, reconsideration_decision} — equal to the two components
  derived blind in policy_conflict_scan; pairwise disjoint, jointly cover all 7 extended policies and all 7 task tools; uuid8s
  independent (action_binding_and_uuids).
- Trees: task 0 n=2 / 1 value_input / owner=user root; task 1 n=3 / 2 value_input / owner=user duplicate repayment; the whole graph is
  a DAG with no cross-task edge.
- Factors: every declared factor of both tasks moves its scored value on its world against an honest baseline, and every all-baseline
  fall-back is definite and differs from gold; but F5 (two method ladders with an unreachable fall-through) and F6 (unreal AutoPay
  condition) strike factors in component B, leaving late_claim_payment and credit_balance_refund without a surviving `method` factor, and
  T1-1 shows a tier read off a status stamp → not closed.
- Policy self-consistency: F1 (undeclared aggregate-window override in first_claim_decision and reconsideration_decision) is a
  demonstrated SOURCE-POLICY RED of the charter.
- Gate re-run on the final form: not performed — the difficulty is not at its final form (REDs outstanding); the coordinator's
  instantiation-stage gate snapshot (all green) is cited in charter_global_frozen.

Post-reveal note on the charter-global sections: the GT revealed nothing that changes a charter-global conclusion; the GT's own
[Revisions] r5 note in tasks/1.json confirms the O1 concern (the first-decision overwrite of the reconsideration-window sentence is read by
the gate as retiring that base gate for every decision).

## revision_2

### charter_global_frozen (revision_2)

- auditor: erl-task-policy-audit (same independent auditor as revision 1); written 2026-10-10 from 21:02Z, before any round-2 masked field
  of tasks/0.json or tasks/1.json was opened.
- hashes re-computed: protect.extended.yaml 89bc698f69502e3aba8b86ff55cc34db856a4cf287b4c16c98ea7ef50eeac664 (changed from 512ebd4f…);
  task_tools.py e1d2f4b402d62644cf61187f0af8ce97c9767c9f4f271e3dfb8c3419131563b2 (changed from c7a7ccbb…). Both shared inputs moved, so
  every charter-global section is **re-derived in full**, not carried forward. Views: 0.view.json fd278eca… (unchanged), 1.view.json
  e6f12634… (changed).
- Entry conditions: the coordinator's round-2 gate snapshot (all seven gates green; traceability deferred; validate_scenario only
  pre-render `required document … not found`) and the rebuilt masked views with hashes are supplied → met.
- contamination_disclosure (revision 2): the auditor read both tasks' round-1 GT during revision 1 (after freezing). Round-2 GT is unread
  at the time of this section. Nothing here is taken from either round's GT.
- Base section: compared key by key with `blueprint/products/protect.yaml` again — identical; only `extended_policies` added.

### what changed in the charter and tool module (auditor's own diff against the revision-1 reading)

- protect_ext_first_claim_decision and protect_ext_reconsideration_decision: each `overwrite` gains an entry naming the base
  protect_agg_annual_aggregate sentence ("Within one plan, the total paid on claims whose loss dates fall in any rolling 365-day window …
  a claim with no room left is denied with reason aggregate_limit_reached.") replaced by the room sentence. Rule and compute unchanged.
- protect_ext_recovery_repayment: prerequisite sentence becomes "… every protection fee charged a second time for the same billing
  period **on the plan** carries a billing-error credit on the fee ledger." (rule and `policy_source` both). Compute unchanged.
- protect_ext_reconsideration_decision: duplicate sentence becomes "… every claim payment issued a second time **on the plan** for an
  approval already paid …".
- protect_ext_late_claim_payment: AutoPay uplift and the day-count `late_interest_period` factor removed (autopay cross_category gone);
  new `method` factor `late_clock_start` (late days run from the assessment date less issue days / from the assessment date less decision
  target and issue days / from the decision date less issue days, keyed on how long after the latest assessment the decision came);
  `late_payment_rate` now keyed on days since the decision (≥71 / 41-70 / 11-40 / otherwise); fixed ÷365 period; prerequisite sentence
  gains "on the plan". 4 factors (3 parameter, 1 method).
- protect_ext_credit_balance_refund: `refund_interest_period` removed; new `method` factor `refund_clock_start` (from the latest fee
  credit / from the latest cancellation request / from the plan's end date); `late_refund_rate` now keyed on days since the plan ended
  (≥61 / 31-60 / otherwise); new parameter factor `refund_repeat_error_uplift` (≥2 / 1 / 0 billing-error corrections); fixed ÷365 period.
  5 factors (4 parameter, 1 method).
- protect_ext_fee_error_credit and protect_ext_duplicate_payment_repayment: unchanged.
- task_tools.py: same seven tools, same bodies and uuid8s; the argument wording "rounded half up to the cent before it is entered" is now
  "rounded half up to the cent" in the two repay tools.

### policy_conflict_scan (revision_2)

Components unchanged: A = {recovery_repayment, first_claim_decision, fee_error_credit} (n=2, 1 value_input, owner=user root); B =
{reconsideration_decision, duplicate_payment_repayment, late_claim_payment, credit_balance_refund} (n=3, 2 value_input, owner=user
duplicate). Disjoint, jointly complete over the 7 policies and 7 tools. Overlapping subjects separated as in revision 1. No new
cross-category write; component B now reads only `unit`; fee_error_credit still reads `unit` and `autopay`.

### rule_compute_equivalence (revision_2)

Unchanged policies: conclusions of revision 1 stand (same rule, compute and basis text). Re-checked the two rebuilt policies sentence by
sentence:
- late_claim_payment: claim / approved / decided_on / decisions / paid / voided / outstanding ("a claim with no decision event on file
  has nothing outstanding"), assessed_on + decision_gap + late_days (three-way clock, "in every case never below zero"), days_waited +
  late_rate (71 / 41-70 / 11-40 / ≤10), work_order + peril + failure_uplift, tenure_months + rent_reversals + tenure_uplift,
  interest_rate ("when there are late days"), result (÷365, rounded once) — every binding quoted, every rule sentence implemented.
- credit_balance_refund: collected / credited / charged / refunded / credit_balance, ended_on, credit_count + credit_date + request_date
  + late_days (three-way clock), days_since_end + late_rate, credit_kind + source_uplift, error_credits + repeat_uplift (no window — the
  rule says "the plan carries", no window either), rental_months + tenure_uplift, result — every binding quoted, every sentence implemented.
- Every ladder tier of every factor is a rule sentence and a branch of its `decides` binding; no orphan branch. PASS.
- Edge from revision 1 still present and still judged per world: `claim_status='paid'` counting of paid claims (first decision,
  reconsideration, recovery, duplicate) and the `- 1` "other" convention.

### action_binding_and_uuids (revision_2)

Seven `(target_tool, amount)` pairs, one policy each; tool bodies unchanged and still validate nothing (task_tools.py lines 36-52, 90-103,
130-143, 176-188, 213-227, 248-264, 286-297); uuid8s unchanged and independent; docstrings name no other tool and carry no sequence word
(the only "after" occurrences describe the state after the call). O2 closed.

### prerequisite_graph (revision_2)

Same six edges, same kinds/gates/forms/resolved_by; acyclic; every `policy_source` verbatim in its own rule (recovery, reconsideration and
late rules re-checked against the new wording); `condition` texts all say "on the plan" for the three re-scoped edges and now match the
sentences. PASS.

### prerequisite_sentences (revision_2)

| edge | sentence (own rule, revision 2) | strength vs condition |
| --- | --- | --- |
| recovery ← fee_error | "The recovery repayment is not fixed until every protection fee charged a second time for the same billing period on the plan carries a billing-error credit on the fee ledger." | matches ("on the plan") |
| recon ← duplicate | "The reconsidered amount is fixed only after every claim payment issued a second time on the plan for an approval already paid carries a repayment void on the claim's handling history." | matches |
| late ← duplicate | "A late claim payment is issued only once every second payment that a mailed check made on the plan for an already paid approval carries a repayment void." | matches |
| recovery ← first_decision, recon ← late, recon ← credit_refund | unchanged | match (revision 1) |

Four-point test, single-write test and the single-reading derivations of revision 1 hold for all six. No new cross-problem order: the new
sentences "The late clock starts where the claims desk's own delay began …" and "The refund clock starts at the event that left the
balance …" order nothing across problems. F4 closed.

### override_declarations (revision_2)

- F1 (annual-aggregate window): now declared in both decision policies' `overwrite`, naming the whole base sentence. Merged semantics:
  the base measure `protect_msr_paid_365d` is referenced only by the superseded sentence; the room is defined once by the extended
  sentence; the base claim-count sentence ("The plan pays at most max_claims_per_12_months claims …") is not superseded and stays
  inherited (judged per world). Unique. **F1 closed.**
- late_claim_payment still inherits the base aggregate sentence (not in its `overwrite`); judged per world (F3).
- All other sentence-by-sentence conclusions of revision 1 stand (dropped post-cancellation branch declared; F2 level-in-force reading;
  O1 non-conflicting declarations unchanged).

### factor_ladders (revision_2)

| policy | factor | effect | tiers | reachable fall-through | real condition / outcome |
| --- | --- | --- | --- | --- | --- |
| late_claim_payment | late_payment_rate | parameter | 4 (0.18 / 0.12 / 0.06 / 0 by days since decision) | yes (≤10 days) | yes |
| | late_clock_start | method | 3 (assessment − issue days / assessment − target − issue days / decision − issue days) | yes (decision within the target) | yes — interest running from when the claims desk's own delay began is a recognised prompt-payment treatment |
| | building_failure_uplift | parameter | 3 | yes | as revision 1 |
| | late_payment_tenure_uplift | parameter (unit) | 3 | yes | as revision 1 |
| credit_balance_refund | refund_clock_start | method | 3 (latest credit / latest cancellation request / plan end) | yes (no credit, no request — e.g. overpayment on a terminated plan) | yes |
| | late_refund_rate | parameter | 3 (0.12 / 0.06 / 0 by days since end) | yes | yes |
| | refund_credit_source_uplift | parameter | 3 | yes | as revision 1 |
| | refund_repeat_error_uplift | parameter | 3 (0.02 / 0.01 / 0) | yes | plausible goodwill for repeat errors |
| | refund_tenure_uplift | parameter (unit) | 3 | yes | as revision 1 |

- Method labels honest: both clock factors change the anchor date and the subtracted allowances (the algorithm of the late-day count),
  not a rate. Fall-through tiers equal the factor baselines and the `baseline.rule` "standard late clock" / "standard refund clock"
  sentences.
- Counts: late 4 (3 parameter, 1 method); refund 5 (4 parameter, 1 method); the other five policies unchanged (fee_error 4/3/1,
  first_decision 5/4/1, recovery 6/4/2, reconsideration 6/5/1, duplicate 5/4/1). All within bounds. **F5 closed; F6 closed** (the AutoPay
  uplift no longer exists).
- No two tiers of any new ladder select the same value or method.

### findings (revision_2)

- F1 closed (declared overwrite in both decision policies).
- F4 closed (three sentences now scoped "on the plan").
- F5 closed (both unreachable-fall-through method ladders replaced by reachable clock-start ladders).
- F6 closed (AutoPay uplift removed from late_claim_payment).
- O2 closed (no ordering word left in tool argument text).
- F2, F3, O1 unchanged and still observations (no world of this difficulty triggers them; see task files).
- No new charter-global defect found.

### closing_checklist (revision_2)

Written after both revision_2 comparisons (post-reveal; nothing in the revision_2 charter-global sections above was taken from GT).

- Files: `0.md`, `1.md` and this file each carry `## revision_2`; revision-1 text untouched.
- Verdicts: task 0 **PASS** (no regression). Task 1: every round-1 RED is closed (F1, F4, F5, F6, T1-1). Two new REDs are confined to
  the proof text: R2-1 (SOURCE-TASK, a stale reconsideration-window date) and R2-2 (SOURCE-CHAIN, a stale deletion-sensitivity figure
  561.12 vs 559.01) in tasks/1.json design_rationale. Not every comparison carries a PASS, so **the difficulty does not close in
  revision_2**. What remains is confined to two sentences of proof text; the charter, tools, worlds and scored solutions pass.
- Scopes: charter_scope equal to the blind components; pairwise disjoint, jointly complete; uuid8s independent.
- Trees: task 0 n=2 / 1 value_input / owner=user root; task 1 n=3 / 2 value_input / owner=user duplicate; DAG, no cross-task edge.
- Factors: 7 computations, 35 declared factors. Each has 4-6 factors with ≥2 parameter and ≥1 method, every ladder reachable and
  distinct, and every factor bears weight against an honest baseline. Each task has multi-source and cross-difficulty factors with seeded
  rows.
- Gate re-run on the final form: not performed by the auditor (coordinator's round-2 snapshot is all green).
- Charter-global observations still open: F2, F3, O1 (no world of this difficulty triggers them).

## revision_3

### charter_global_frozen (revision_3)

- written 2026-10-10T21:39Z, before any round-3 task file was opened.
- hashes re-computed: protect.extended.yaml 89bc698f69502e3aba8b86ff55cc34db856a4cf287b4c16c98ea7ef50eeac664 and task_tools.py
  e1d2f4b402d62644cf61187f0af8ce97c9767c9f4f271e3dfb8c3419131563b2 — both **identical to revision_2**. Under the re-audit rule, every
  charter-global section of revision_2 (policy_conflict_scan, rule_compute_equivalence, action_binding_and_uuids, prerequisite_graph,
  prerequisite_sentences, override_declarations, factor_ladders, findings) is **carried forward by reference** to `## revision_2`; nothing
  is re-derived because no shared input moved.
- Entry conditions: the coordinator's round-3 gate snapshot (all green; traceability deferred; validate_scenario only pre-render
  required-document errors) and the unchanged view hashes are supplied → met.
- contamination_disclosure: the auditor has read round-1 and round-2 GT of both tasks (each after freezing). Round-3 task files unread at
  this point.

### closing_checklist (revision_3)

Written after both revision_3 comparisons (post-reveal; the revision_3 charter-global section carries revision_2 forward by unchanged
hashes and takes nothing from GT).

- Per-task files `0.md` and `1.md` match the two tasks one to one, and each carries revisions 1-3. Older text is untouched. Every
  revision_3 comparison is **PASS**.
- Coverage and scopes: task 0 = {first_claim_decision, fee_error_credit, recovery_repayment}; task 1 = {credit_balance_refund,
  duplicate_payment_repayment, late_claim_payment, reconsideration_decision}. The scopes are pairwise disjoint and together cover all
  7 extended policies and all 7 task tools. Each task tool has its own frozen uuid8; tools and GT are closed.
- Trees:
  - task 0: 2 prerequisite problems, 1 value_input edge (floor 1), customer's own write = the root;
  - task 1: 3 prerequisite problems, 2 value_input edges (floor 2), customer's own write = the duplicate repayment;
  - the whole graph is a DAG with no cross-task edge.
- Factors: 7 computations with 35 declared factors. Every computation has 4-6 factors, at least 2 parameter and 1 method, and a
  self-sufficient baseline whose fall-back differs from gold. Every ladder has at least 3 distinct, reachable tiers stated in its rule.
  Every factor bears weight on its world. Each task has multi-source and cross-difficulty factors with seeded unit rows; task 0 also has
  seeded autopay rows.
- Policy self-consistency: undeclared overrides none (F1 closed in revision_2); prerequisite sentences verbatim and correctly scoped
  (F4 closed).
- Instantiation-stage gates on the final form: the coordinator's round-3 snapshot was run on exactly these hashes (charter 89bc698f…,
  tools e1d2f4b4…, views fd278eca… / e6f12634…). Results: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE
  OK. Traceability is deferred to the KB render. validate_scenario shows only the pre-render required-document errors.
- Remaining charter-global observations (not grounds for rework): F2 (current-level `P()` vs level in force on the loss date — no plan
  changes in either world), F3 (inherited base gates — none triggered), O1 (two declared overwrites of non-conflicting base sentences).

**The difficulty passes the source-layer audit (revision_3): policy self-consistency, problem tree, factor weight and unique solution all
PASS for both tasks.**

## revision_4

### charter_global_frozen (revision_4)

- written 2026-10-10 from 22:49Z, before the round-4 task files and before the KB-doc audit notes (`audits/policy_kb/…`, an existing
  audit conclusion and therefore masked until this freeze) were opened.
- hashes: protect.extended.yaml aceb608e6034a44c41d868f467fa5b34c4c8c38bad3054729d1e62ce65f61712 (**changed** from 89bc698f…);
  task_tools.py e1d2f4b4… (unchanged); 0.view.json fd278eca… (unchanged); 1.view.json d9d21cdac07f5e66e084c4ed5e92252546ae16a1817e61ad7c3eeacc79fb0bd4
  (**changed**). The charter moved, so every charter-global section is re-checked below. Where the text is unchanged, the revision_2
  conclusion is re-confirmed. The auditor now keeps a scratch copy of the charter
  (`/tmp/run_0051/audit_tenant_protection_claims/protect.extended.r4.yaml`) for mechanical diffs in later rounds.
- Entry conditions: the coordinator's round-4 snapshot is all green, including TRACEABILITY OK and validate_scenario VALID → met.
- contamination_disclosure: GT of rounds 1-3 was read after each freeze; the round-4 GT and the KB-audit notes are unread here.

### what changed in the charter (auditor's diff against revision_2/3)

- base section: identical to `blueprint/products/protect.yaml` (re-compared key by key).
- first_claim_decision, recovery_repayment, duplicate_payment_repayment: the collectibles cap is removed from rule, compute,
  compute_basis, params and cross_category. The settled total, missing-property total and duplicate total now cap "the collectibles,
  firearms and business-inventory values each … at its sublimit" (`MN(collectibles, P('collectibles_art_sublimit_usd'))`). Their factor
  sets are unchanged, because the collectibles cap was never a declared factor there.
- reconsideration_decision:
  - New sentence: "The reconsideration window closes claim_reconsideration_window_days after the date of the latest decision on the
    claim, counted in calendar days starting the day after that decision date with the last counted day included, and a reconsideration
    requested after it closes is not taken."
  - New sentence: "A new document can bring a fresh adjuster assessment, and the claim is re-assessed when its latest adjuster assessment
    is dated after the latest decision on the claim."
  - The collectibles-cap ladder now requires "the claim is re-assessed" in both uplift tiers (bindings decided_last, assessed_last,
    reassessed, humidity_c, temperature_c, collectibles_cap).
- fee_error_credit, late_claim_payment, credit_balance_refund: rule, params, ladders, prerequisite sentences and compute counts are
  identical to revision_2.

### re-checks on the changed text

- **rule_compute_equivalence:**
  - The three trimmed policies: every sentence about the totals has its binding, and no orphan collectibles binding remains (the
    `collectibles_value` / `_left` / `_was` reads feed the sublimit cap).
  - Reconsideration: `decided_last` / `assessed_last` / `reassessed = assessed_last > decided_last` implement "dated after the latest
    decision on the claim". A same-day assessment is not "after", and a claim with no decision is never re-assessed; the policy only
    applies to decided claims. The collectibles ladder's three tiers equal the rule sentence and the `collectibles_cap` branches.
  - The window sentence is eligibility text with no compute binding, so there is no empty promise.

  PASS.
- **override_declarations:**
  - The new window sentence restates the base protect_evt_reconsideration window ("requested not later than the decision date plus
    claim_reconsideration_window_days … starting the day after the decision date, and the last counted day is included"), with "the
    latest decision" for "the decision". Same quantity, same count, no conflict, so no declaration is needed.
  - It also resolves the merged-text concern O1 for this policy: the reconsideration now carries its own window clause, whatever
    first_claim_decision's declared overwrite of the base window sentence is read to retire. O1 remains an observation only for
    fee_error_credit's free-look declaration.
  - Removing the collectibles uplift from the three policies brings their collectibles treatment back to the base settlement ("each
    special class capped at its sublimit"), so there is one fewer deviation.
- **factor_ladders (reconsideration_collectibles_cap):**
  - Effect: parameter. Tiers: ×1.5 (re-assessed ∧ humidity control), ×1.25 (re-assessed ∧ temperature band, no humidity), ×1
    otherwise. All are reachable and the values are distinct.
  - Both uplift tiers are conjunctions over distinct records (claim events and unit class), so the factor is multi-source.
  - The conditions are real: a sublimit raised for collectibles that were appraised and re-assessed after the decision and are stored
    under humidity or temperature control is a recognisable treatment for documented, well-kept valuables.
  - The fall-through equals the baseline `P('collectibles_art_sublimit_usd')`, and the cap sits in the `baseline.rule` "each
    special-class value capped at its sublimit". Honest.

  Counts are unchanged: fee_error 4/3/1, first_decision 5/4/1, recovery 6/4/2, reconsideration 6/5/1, duplicate 5/4/1, late 4/3/1,
  refund 5/4/1 (35 factors).
- **prerequisite_graph / prerequisite_sentences:** all six `policy_source` sentences are verbatim in their own rules, identical to
  revision_2. No new cross-problem order: the window and re-assessment sentences order nothing across problems. PASS.
- **action_binding_and_uuids:** tool module unchanged → revision_2 conclusion carried forward.

### findings (revision_4, pre-reveal)
- No new charter-global defect. O1 is narrowed (reconsideration now self-contained); F2 and F3 are unchanged observations.

### KB-audit policy-side notes N1–N4 (assessed after the revision_4 freeze)

Source: `audits/policy_kb/tenant_protection_claims/0.md` and `1.md`, sections "Policy-side notes". Read at 22:50Z, after this revision's
charter-global and per-task freezes.

- **N2 (collectibles climate cap carried in rule but neither baseline nor factor in first_claim_decision, recovery_repayment and
  duplicate_payment_repayment): closed.** The cap is removed from the three policies and is now only a declared multi-source factor of
  the reconsideration (factor_ladders above). In revision 1 I called the undeclared rule ladder "a compute binding, not a factor; no
  defect". The KB audit's point is that a computation document must state the standard method silent about variation, and that ladder
  had no declared home. The rework removes the question; I record that my revision-1 reading did not raise it.
- **N3 (reconsideration window resting on a base clause retired by another policy's overwrite): closed.** The reconsideration rule now
  carries the window itself. This is my O1 for that policy.
- **N4 (new-document evidence only from the customer): closed** at the source by the seeded re-assessment 55c930f5. This is my O-1.1.
- **N1 (aggregate window residue in the frozen base): observation O5.** The base `parameter_schema` describes `aggregate_limit_multiple`
  as "Total paid on claims with loss dates in any rolling 365-day window, as a multiple of the coverage limit". The base measure
  `protect_msr_paid_365d` (and `max_claims_per_12_months`' description) keep the loss-date window. The policy sentence was overwritten
  and declared in revision 2, but these descriptions are not policy sentences and are not named by the overwrite.
  - When I closed F1 in revision 2 I checked the policy sentence and did not examine these base descriptions. I record that.
  - Judged now: the extended room sentence uses `aggregate_limit_multiple` as a multiplier with an explicit, declared window. Read as a
    definition, the parameter description adds at most a cumulative loss-date cap.
  - That cap binds in neither world, at any scored handling time or on any skip path:
    - task 0: 71289234 and 81634657 have loss dates 490 days apart;
    - task 1: 533fb2d9 (2025-07-01) and 33eb605d (2026-08-15) share no 365-day window, and the only other claim with a loss date in
      the window, 6d977fc6, is paid at most 459.43.
  - All scored values and edge weights are the same under the declared-only and cumulative readings. Only a reading that lets the
    parameter description replace the declared room sentence would move anything: it would strip the duplicate → reconsideration edge
    of weight. That reading contradicts the explicit declared overwrite, so I do not count it as defensible.
  - There is no demonstrable consequence, so this is an observation, not a RED. It remains a source-level residue in the frozen base
    that the KB renders as in force.

### closing_checklist (revision_4)

- Files: `0.md`, `1.md` and this file carry revisions 1-4; older text is untouched.
- Verdicts: task 0 **PASS** (no regression). Task 1 **SOURCE-TASK RED** on R4-1 (a stale payable figure, 4427.50 vs 3946.25, in the
  design_rationale [Seed] card). Its scored solution, tree and factors pass.
- Charter level: **PASS**. No undeclared override with a demonstrable consequence. Rule and compute are equivalent on the changed text.
  The prerequisite graph and sentences are verbatim. The factor set is 35 factors within bounds, every ladder reachable and real. N2, N3
  and N4 are closed. Open observations (not grounds for rework): O5/N1 (base parameter-schema residue of the loss-date window,
  outcome-neutral), F2 (current level vs level in force on the loss date, no plan changes in either world), F3 (inherited base gates
  not triggered), and O1 only for fee_error_credit's free-look declaration.
- Coverage and scopes, trees, uuids: unchanged from revision_3 (pass).
- Gates: the coordinator's round-4 snapshot is on exactly these hashes (charter aceb608e…, tools e1d2f4b4…, views fd278eca… /
  d9d21cda…), all green including TRACEABILITY OK and validate_scenario VALID.

**The difficulty does not close in revision_4: one proof-text RED (R4-1) remains in tasks/1.json. Everything else passes.**

## revision_5

### charter_global_frozen (revision_5)

- written 2026-10-10T23:10Z, before any round-5 task file was opened.
- protect.extended.yaml aceb608e… is **byte-identical** to the auditor's round-4 scratch copy (`cmp` against
  `/tmp/run_0051/audit_tenant_protection_claims/protect.extended.r4.yaml`). task_tools.py e1d2f4b4… and both views (fd278eca…,
  d9d21cda…) are unchanged. Every charter-global section of `## revision_4` is carried forward by reference: charter level PASS, with
  observations O5/N1, F2, F3 and O1 (fee_error_credit only) still open.
- Entry conditions: the coordinator's round-5 snapshot is all green (incl. TRACEABILITY OK, validate_scenario VALID) → met.
- contamination_disclosure: GT of rounds 1-4 was read after each freeze; round-5 task files unread here.

### closing_checklist (revision_5)

Written after both revision_5 comparisons (post-reveal; the revision_5 charter-global section carries revision_4 forward by a
byte-identical charter and unchanged tool/view hashes, and takes nothing from GT).

- Files: `0.md`, `1.md` and this file each carry revisions 1-5; older text is untouched. Every revision_5 comparison is **PASS**.
- Coverage and scopes: task 0 = {first_claim_decision, fee_error_credit, recovery_repayment}; task 1 = {credit_balance_refund,
  duplicate_payment_repayment, late_claim_payment, reconsideration_decision}. The scopes are pairwise disjoint and together cover all
  7 extended policies and 7 task tools. Each tool has its own frozen uuid8; tools never judge prerequisites.
- Trees:
  - task 0: 2 prerequisite problems, 1 value_input edge, customer's own write = the root;
  - task 1: 3 prerequisite problems, 2 value_input edges, customer's own write = the duplicate repayment;
  - every edge is false at the opening and bears weight (state gates gate a false state); the whole graph is a DAG with no cross-task
    edge.
- Factors: 35 declared over 7 computations. Each has 4-6 factors with ≥2 parameter and ≥1 method, a self-sufficient baseline whose
  fall-back differs from gold, reachable and distinct ladders stated in the rule, and every factor bearing weight on its world. Each task
  has multi-source and cross-difficulty factors with seeded unit rows; task 0 also has autopay rows.
- Policy self-consistency: no undeclared override with a demonstrable consequence. Prerequisite sentences are verbatim, correctly scoped
  and in state form.
- Proof text: both task files swept number by number with no contradiction left (R2-1, R2-2 and R4-1 all closed).
- Gates on the final form: the coordinator's round-5 snapshot is on exactly these hashes (charter aceb608e…, tools e1d2f4b4…, views
  fd278eca… / d9d21cda…). Results: EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE and TRACEABILITY OK;
  validate_scenario VALID.
- Open observations, not grounds for rework:
  - O5/N1: the frozen base `parameter_schema` still describes the loss-date aggregate window; outcome-neutral in both worlds.
  - F2: current level vs level in force on the loss date; no plan changes in either world.
  - F3: inherited base gates the extended rules are silent on; none triggered.
  - O1: fee_error_credit's harmless free-look declaration.
  - O-0.5: task 0's historical DE1 partial approval withheld a class pending proof of ownership, and the card does not say which.

**The difficulty passes the source-layer audit (revision_5): policy self-consistency, problem tree, factor weight and unique solution all
PASS for both tasks.**
