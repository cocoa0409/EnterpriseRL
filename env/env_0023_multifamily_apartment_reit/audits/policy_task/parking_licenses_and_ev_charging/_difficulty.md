# Policy-task audit — parking_licenses_and_ev_charging / charter-global

## charter_global_frozen

- Freeze time: 2026-09-24T17:15:48Z (revision 1). Auditor: independent policy-task auditor (a Claude agent). It did not author any artifact in this difficulty.
- Frozen inputs (sha256):
  - `tasks/parking_licenses_and_ev_charging/parking.extended.yaml` = `9011405315323c98e61fbd440027450d996bb5dcd385e9d25cb2d57269f2adf1` (same as the brief)
  - `tasks/parking_licenses_and_ev_charging/task_tools.py` = `dfaf3570773ee11c38fecf786a1aa264ebda1553d85406ac5a99c4e4d24973ab` (same as the brief)
  - `blueprint/products/parking.yaml` = `bc48c01ab81c36fa33f2ff68c3ae00d3a85ae34e15481f9b4e8047965d166ef7`
- Fields read: blueprint.yaml, db_schema.json, share_tools.py, products/parking.yaml (plus the lease/term/storage product files, which were loaded only as the compute sandbox's cross-category binding), the full extended charter, the full task_tools.py, and `skills/erl-task-instantiate/scripts/check_compute.py` (for the DSL semantics: `within_months`, `MONTHS`, `LATEST`, `RND`).
- Fields masked and not read: every task JSON under `tasks/parking_licenses_and_ev_charging/tasks/`, including evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure and the closure fields. The worklog, other audits and the scratchpad (apart from this auditor's two masked view files) were not read.
- This whole section was built from the charter, schema and tool contracts **before any reveal**. It contains nothing derived from GT.

Entry conditions (Step 0): the brief supplies the gate snapshot. check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding and check_cross_fire all return rc=0. check_traceability is deferred to render, as stated. The brief also supplies the masked views and their hashes, and I re-verified all four hashes. The entry conditions are met.

DSL semantics this audit relies on (check_compute.py `build_env`):
- A row is "within N months before the handling date" when `0 <= MONTHS(row_date, NOW) < N`. `MONTHS` counts calendar months and takes one away when the day of the month has not been reached. The window is therefore (NOW − N months, NOW] and includes today.
- `LATEST` takes the row with the greatest date string.
- `RND` is Python `round`.

### policy_conflict_scan

There are six extended policies over ten base policies. Subjects, target tools and computed quantities are pairwise distinct:

| extended policy | subject | computes | target_tool (owner) | trigger |
|---|---|---|---|---|
| parking_ext_idle_fee_schedule | parking_ev_session | credit_amount | credit_idle_fee_rerate_1959dfce (agent) | state_due |
| parking_ext_early_cancellation_fee | parking_cancellation_notice | early_cancellation_fee | sign_parking_cancellation_notice_d2378b15 (user) | on_request |
| parking_ext_violation_fine_schedule | parking_fine | credit_amount | credit_violation_fine_rerate_f29c2916 (agent) | state_due |
| parking_ext_storage_bundle_discount | parking_credit | discount_amount | credit_bundle_discount_a8c94fb6 (agent) | state_due |
| parking_ext_suspension_cure_payment | parking_payment | payment_amount | pay_parking_balance_59b25ecc (user) | on_request |
| parking_ext_privilege_restoration | parking_reinstatement | reinstatement_fee | restore_parking_privileges_f55d0d0b (agent) | on_request |

- Overlapping base clauses: `parking_suspension_rule`'s sentence "Privileges are restored only after the whole parking balance and the reinstatement_fee are paid." is superseded by **two** extended policies, suspension_cure_payment and privilege_restoration.
  - cure_payment replaces it with "The cure amount is what a resident pays toward a suspended license so that its privileges can be restored."
  - privilege_restoration replaces it with "Privileges are not restored until a payment covering the cure amount stands received on the license."
  - Merged, the two read: restoration waits on a payment ≥ cure amount, and the reinstatement fee "is not part of the cure amount" (restoration rule). They are compatible, with no conflicting conclusion.
- The charge_reversal code is posted both by credit_idle_fee_rerate (idle lines) and by credit_violation_fine_rerate (fines). The two tools are separated by the line they point at: an idle line versus a fine carrying `source_activity_id`. Neither policy reads the other's credits as its own object. early_cancellation_fee's fee base subtracts *all* charge_reversal credits in its window, which is consistent with its rule ("less the charge reversal and bundle discount credits posted on the license in the window").
- Time anchors are uniformly "the handling date" (cancellation: "the notice date", which equals the handling date because the notice is signed at the call).
- Cross-category reads are all declared in `cross_category`: lease (autopay_enrolled, move_in_date, rent_discount_program, certified_funds_only, insurance_on_file), term (term_months, status), storage (status, start_date, monthly_rent).
- **Scopes.** The `prerequisite` graph has exactly two connected components:
  - {idle_fee_schedule → early_cancellation_fee}
  - {violation_fine_schedule, storage_bundle_discount → suspension_cure_payment → privilege_restoration}

  Because M=2, a scope spans the whole tree, and scopes must be disjoint, the only admissible partition is one scope per component. Together they cover all six policies. Scopes are mutually exclusive and jointly complete, provided each task claims one component (verified per task after the reveal).

### rule_compute_equivalence

A sentence-by-sentence sweep of every `compute_basis` quotation against its own `rule` found the following. Whitespace was normalised; the check was reproduced with an inline script that has since been discarded.

- **idle_fee_schedule.** All 25 compute_basis quotations are verbatim.
  - Every quantity is implemented: review window, grace ladder, billable minutes, three hour-counting methods, standing rate, volume reduction, escalation split at `escalation_after_hours`, session multiplier, and a single final rounding.
  - The `reviewed_in_window >= 1` guard implements "idle fee lines posted earlier stand as billed". `LATEST` runs unwindowed, but the guard zeroes the result when the latest line is out of window. Equivalent.
- **early_cancellation_fee.** All quotations are verbatim, but **the rule makes a promise the compute never implements** (finding C-1). The rule and baseline both say: "When the end date falls before the commitment end, an early cancellation fee is billed with the notice; when it does not, no early cancellation fee is billed. The commitment end is the license's start date plus the commitment months".
  - No compute_basis entry quotes this sentence.
  - No binding reads `end_date`.
  - `result` is a positive fee whenever `held_months < commitment_months`, whatever end date the resident chooses.
  - Every other branch (fee base methods, fee months, commitment months, proration with floor, program share, activation credit, final rounding) is quoted and implemented.
- **violation_fine_schedule.** The `scheduled_fine` basis "…less the **fine** standing reduction, and never below zero." is **not verbatim**: the rule says "…less the standing reduction, and never below zero." The quantity is the same, so no number changes (observation O-1). Every other quotation is verbatim and implemented.
- **storage_bundle_discount.** All quotations are verbatim.
  - The coverage gate, the program rate, the three additive uplifts and the clawback, the floor at zero, the welcome multiplier and the single rounding are implemented.
- **suspension_cure_payment.** All quotations are verbatim.
  - Scope (three methods), prepayment months with reduction and floor, and the three prepayment-fee sources are implemented.
  - "the credits and payments already posted on the license always count in full" is honoured: `left_out` sums only the event types parking_fee_charge, parking_ev_session and parking_fine.
- **privilege_restoration.** The basis for `lease_certified_only`, `lease_insurance` and `standing_reduction` quotes "…the **reinstatement** standing reduction is standing_reduction_full", which is **not verbatim**. The rule's first tier says "the standing reduction is standing_reduction_full", while its second tier and final sum say "the reinstatement standing reduction". The rule therefore names one quantity two ways (observation O-1). All other quotations are verbatim and implemented.
- **Ladders in both faces.** For every factor of every policy, each `ladder` tier is a sentence of the rule and a branch of its `decides` binding, and vice versa. No tier lives in only one face.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (table above).
- Every docstring was scanned for ordering words (before, after, first, then, once, until, prior, next). The only hits are "next" used spatially ("next to that line"). No docstring names another task tool; the only `credit_` hits are the receipt field `credit_id`. No docstring adds a confirmation, review or wait.
- uuid8s: 1959dfce, d2378b15, f29c2916, a8c94fb6, 59b25ecc, f55d0d0b. They share no prefix or suffix, show no sequence or adjacency, and none is reused.
- Tool bodies judge no eligibility and validate no prerequisite. Each one finds the license, writes one line (or updates status), adjusts `balance_due`, and returns. None refuses, errors or hints when a prerequisite is unresolved.
  - `sign_parking_cancellation_notice_d2378b15` bills nothing for 0.00.
  - `restore_parking_privileges_f55d0d0b` sets `status="active"` unconditionally.

### prerequisite_graph

| blocked policy | problem | kind | gate (binding exists?) | form | resolved_by = target of problem? |
|---|---|---|---|---|---|
| early_cancellation_fee | idle_fee_schedule | value_input | fee_base_amount (yes) | state | credit_idle_fee_rerate_1959dfce (yes) |
| suspension_cure_payment | violation_fine_schedule | value_input | whole_balance (yes) | state | credit_violation_fine_rerate_f29c2916 (yes) |
| suspension_cure_payment | storage_bundle_discount | value_input | prepay_fee (yes) | state | credit_bundle_discount_a8c94fb6 (yes) |
| privilege_restoration | suspension_cure_payment | value_input | latest_payment (yes) | state | pay_parking_balance_59b25ecc (yes) |

- `prerequisite` is filled everywhere: `[]` on idle, fine and bundle. Every `problem` is an extended id in this file, none is a base policy or the policy itself, and the graph is acyclic.
- Each `policy_source` is verbatim in its own policy's `rule` (checked by script).
- All edges are state form, and none carries `fallback_reason`, which is correct.
- Each resolving tool genuinely changes the gated binding:
  - A charge_reversal credit enters `reversal_window_total` and moves `fee_base_amount`.
  - The fine credit lowers `balance_due`, which is `whole_balance`.
  - A bundle credit enters `recent_bundle_credits` / `latest_bundle_credit`, which switches `prepay_fee`.
  - The payment becomes `LATEST(... payment_received)`.
- Two `condition` fields are marginally narrower than their sentences (observation O-5):
  - early←idle: "carries the charge reversal credit that brings it down…" versus "stands at the amount the idle fee schedule sets". A line already at its scheduled amount needs no credit.
  - restoration←cure: "A payment received on the license **today**…" versus "stands received on the license".

  Neither narrowing changes any resolving action.

### prerequisite_sentences

1. **early←idle.** "The early cancellation fee is fixed only after every idle fee line posted on the license in the three months before the notice date stands at the amount the idle fee schedule sets."
   - Connective: "only after". The waited-on state is a record-visible amount (idle line net of the credits pointing at it). It names no tool, id or snake_case token. "the idle fee schedule" is the business name the depended-on rule uses for itself ("The idle fee schedule re-rates the idle fee lines…").
   - Exactly one write of this difficulty re-rates an idle fee line: the idle schedule's credit.
   - Derivation: the sentence plus the charges (idle lines in the window) plus the idle rule ("The idle fee line under review is the most recent idle fee line posted on the license within review_window_months months…; idle fee lines posted earlier stand as billed") leads to one credit on the latest in-window idle line.
   - Scope: "every idle fee line in the three months" is compatible with the idle rule, because in-window lines other than the latest "stand as billed", which is the amount the schedule sets for them. It is neither broader nor narrower in effect.
2. **cure←fine.** "The cure amount is worked out only after every fine billed on the license in the three months before the handling date stands at the amount the violation fine schedule sets."
   - Same analysis, with a single resolving write (the fine credit). The fine rule's review window is also three months with "fines billed earlier stand as billed".
3. **cure←bundle.** "The cure amount is not worked out until every monthly fee line posted on the license since the start of the lease's active storage rental carries the storage bundle discount credit owed on it."
   - Connective: "not … until". State form, with one resolving write (the bundle credit).
   - **Scope mismatch (observation O-4).** The bundle rule's object is only "the most recent monthly fee line of the license". Where two or more fee lines were posted since the storage start, the sentence demands credits on lines that the depended-on rule never computes. This bites only in a world with ≥2 such lines; per-task files check it.
4. **restoration←cure.** "Privileges are not restored until a payment covering the cure amount stands received on the license."
   - Connective: "not … until". The state is record-visible (a payment_received line ≥ cure amount).
   - The single resolving write is pay_parking_balance, the only payment tool.
   - The cure rule does not restate the sentence.

Other checks:
- No rule states any other cross-problem order. The restoration rule's "the reinstatement fee falls due with the next monthly fee and is not part of the cure amount" fixes a quantity boundary, not an order.
- No base rule sentence grounds an edge. Base orders ("a warning precedes a fine", in blueprint prose) sit within single policies.
- Docstrings are silent about sequence (see above).

### override_declarations

Each `base_policy_refs` entry, taken sentence by sentence:

- **idle ← parking_evt_ev_charging.**
  - Status gate: follows.
  - Dedicated on/off-peak rates: follows.
  - Shared chargers: follows.
  - Idle-fee sentence: handled differently, **declared** (superseded_clause verbatim in base; replaced_by verbatim in rule).
  - Per-line energy rounding: follows.
- **early_cancellation ← parking_cancellation_rule.**
  - Notice period / Surface Unreserved "any date": follows.
  - Fee sentence (commitment end and amount): **declared**.
  - Coterminous, withdrawal, move-out, transfer, carried balance: follow.
- **fine ← parking_evt_enforcement.**
  - Escalation/amount sentence: **declared**.
  - Tow-immediate, abandoned, wrong_space storage, tow charges off-ledger, one fine per violation: follow.
  - Observation O-2: the extended rule adds "Warnings and fines on record are counted over the default_window_months months before the handling date". This re-anchors the "on record" count from the base "trailing 365 days" of the violation being decided, per plate, to 12 months before the handling date on the license, without naming the base sentence "Enforcement escalates per plate over the trailing 365 days (parking_msr_enforcement_12m)". It does not govern the scored credit, because the escalation level is already recorded on the violation. Its consequence is checked per task.
- **bundle ← parking_agg_household_pricing.**
  - Earliest-permit-free: follows.
  - Bundle sentence (rate and base): **declared**.
  - "does not stack … not posted for a month in which the storage rental was not active on the fee charge day": follows. The extended coverage gate "start date falls on or before the fee line's posting date" is consistent with it.
- **cure ← parking_evt_payments_and_changes, parking_suspension_rule.**
  - Payment status gate and oldest-first allocation: follow, and the allocation is restated.
  - Suspension trigger / effects / lease-independence: follow.
  - Restoration condition: **declared**.
- **restoration ← parking_suspension_rule, parking_evt_fees.**
  - Restoration condition: **declared**.
  - Reinstatement fee amount (fees sentence): **declared**.
  - Fee status gate, proration, fee lock, fee-keeps-posting-while-suspended: follow.

No undeclared override reaches a scored quantity. No anonymous intermediate, 0/1 multiplier or dropped branch was found. early_cancellation's `program_share = 0` for active_military is a declared tier of the replaced fee sentence.

### factor_ladders

Counts are of factors as labelled. The label test comes after the table.

| policy | factors | parameter | method (as labelled) | multi-source factor(s) | cross_difficulty |
|---|---|---|---|---|---|
| idle_fee_schedule | 6 | grace, standing_rate, volume, escalation | hour_counting, session_multiplier | grace (product + idle-line history), hour_counting (product + license start), session_multiplier (product + session energy lines) | standing_rate → lease |
| early_cancellation_fee | 6 | fee_months, commitment_by_lease_term, program_share, activation_credit | fee_base_method, commitment_proration | fee_base_method (product + window lines), fee_months (activity + license start) | commitment → term; program_share → lease |
| violation_fine_schedule | 5 | class_amount, repeat_step_up, warning_surcharge, standing_reduction | counting_window | class_amount (violation row + license plate), counting_window tier 2 (charges + license start) | standing_reduction → lease |
| storage_bundle_discount | 5 | program_rate, lease_loyalty, parking_tenure, enforcement_clawback | welcome_multiplier | welcome_multiplier (bundle history + storage start) | lease_loyalty → lease (program_rate reads storage, which no difficulty claims; `null` is correct) |
| suspension_cure_payment | 4 | prepay_months, prepay_reduction | cure_scope, prepay_fee | cure_scope (license start + lease autopay), prepay_fee tier 1 (bundle history + storage) | cure_scope → lease; prepay_reduction → lease |
| privilege_restoration | 6 | graduated_fee, gate_reactivation, enforcement_surcharge, standing_reduction, household_relief | handling_share | gate_reactivation (product + remote-fee lines) | standing_reduction → lease |

Structural checks:
- Bindings are disjoint within each policy. Every `decides` is an input, never `result`. Every ladder has three tiers, stated disjointly, each in the rule and in compute. Every fall-through equals the `baseline` value for its input.
- Each `baseline.rule` is a subset of the rule's sentences (checked by script) and is self-sufficient: a reader gets a definite number from it and the records. The one exception is early_cancellation's missing end-date branch (C-1), which the baseline shares.

**Label test ("a `method` tier changes the algorithm, a `parameter` tier a number").**

Honest methods:
- idle `hour_counting`: floor of completed hours / ceiling of half hours ÷ 2 / ceiling of hours.
- early_cancellation `fee_base_method`: three different formulas.
- early_cancellation `commitment_proration`: ratio / ratio with floor / none.
- cure `cure_scope`: three different line sets excluded.
- cure `prepay_fee`: a computed net of two lines versus two different field reads. This one is borderline but accepted.

**Mislabelled** (each tier puts a different constant into one fixed formula):
- **C-2a** idle `idle_session_multiplier`: `scheduled = m × hourly_charges`, m ∈ {offpeak_multiplier 0.5, mixed_multiplier 0.75, 1}.
- **C-2b** fine `fine_counting_window`: `COUNT(violation_fine, within_months=w) − 1`, w ∈ {24, 6, 12}. A window length is a threshold number.
- **C-2c** bundle `bundle_welcome_multiplier`: `credit = m × rate × fee`, m ∈ {2.0, 1.5, 1}.
- **C-2d** restoration `restoration_handling_share`: `share = s × latest_payment`, s ∈ {0.05, 0.025, 0}.

Once the mislabelled factors are removed:
- idle keeps 1 honest method (hour_counting) and 5 factors in all, within bounds apart from the mislabel itself.
- **violation_fine_schedule, storage_bundle_discount and privilege_restoration have 0 honest `method` factors, below the floor of 1.**

Tier-outcome distinctness across the charter's six products (charter-global only; world checks are per task):
- Observation O-3: bundle `program_rate` collapses for Private Detached Garage. bundle_discount_with_storage_pct 0.15 equals bundle_rate_high 0.15, so tier 1 and the fall-through select the same value on that product. On Covered Carport, Structured Garage and EV Charging Reserved (0.10) the three tiers are distinct.
- early_cancellation `commitment_by_lease_term` collapses to 0/0/0 on the two surface products (min_commitment_months 0). Those products carry early_cancellation_fee_months 0 and no commitment, so the policy is moot there.
- cure `prepay_fee` tiers 2 and 3 (product list fee versus the license's fee in force) coincide whenever the license's fee equals the list price. They are distinct sources that usually agree.

Realness (conditions and outcomes that a line of business actually weighs):
- These are plausible for an apartment operator: grace, escalation and off-peak leniency on idle fees; loyalty and autopay reductions; clean-record and long-term-lease relief on early cancellation; military waiver; paperwork-violation classes; bundle rates by storage size; security prepayment after repeat suspensions; graduated reinstatement fees.
- Observation O-6: fine `warning_surcharge`. Under the inherited base escalation, with warnings_before_fine = 1 on every product, a fine exists only after at least one warning in the trailing 365 days. The "exactly one warning" tier therefore holds for almost every fined resident. The fall-through is reachable only when that warning has aged out of the 12-month lookback measured from the handling date. That is reachable, so this is not a RED.
- Observation O-7: restoration `handling_share` charges a reinstatement component proportional to the resident's own cure payment (5% / 2.5%), independent of instrument. It is recorded as doubtful practice. It is not asserted as RED because percentage convenience fees on payments do exist.

### findings

- **C-1 — SOURCE-POLICY RED (rule↔compute, check 2). Bears on task 0.**
  - Symptom: early_cancellation_fee's rule gates the fee on the end date. Its compute never reads the end date.
  - Evidence: rule and baseline.rule say "When the end date falls before the commitment end, an early cancellation fee is billed with the notice; when it does not, no early cancellation fee is billed." `compute` has no binding on `end_date`, and `result: RND(MX(0, fee_before_credit - activation_credit), 2)` is ungated.
  - Consequence in one situation: take any license with `held_months < commitment_months` whose resident chooses an end date on or after start + commitment months. The rule says 0.00 and the compute gives a positive fee. Task 0's license (start 2026-06-10, tier commitment 5 months, so commitment end 2026-11-10) with end date 2026-11-15: the rule gives 0.00, the compute gives 9.78 (the auditor's recomputation on the post-idle-credit world). Whether this changes task 0's scored value is judged in `0.md`.
  - Affected: `parking.extended.yaml` extended_policies[parking_ext_early_cancellation_fee].compute / compute_basis.
- **C-2 — SOURCE-FACTOR RED (mislabelled effect).**
  - C-2a (idle_session_multiplier) bears on task 0.
  - C-2b, C-2c and C-2d (fine_counting_window, bundle_welcome_multiplier, restoration_handling_share) bear on task 1. They leave three of its four policies with **no honest method factor**.
  - Evidence: the `ladder` method strings and compute expressions quoted above. Each tier differs only in a constant multiplied into, or passed to, the same expression.
  - Affected: `factors[].effect` of those four factors, and the policies' method count.
- **O-1 (observation).** compute_basis not verbatim: fine `scheduled_fine`; restoration `lease_certified_only` / `lease_insurance` / `standing_reduction`. The restoration rule names the standing reduction two ways. No number changes. check_grounding did not catch it.
- **O-2 (observation).** The extended fine rule re-anchors the "on record" count without naming the base escalation window. Tested per task.
- **O-3 (observation).** Bundle `program_rate` tier 1 equals the fall-through on Private Detached Garage. There is no task world on that product.
- **O-4 (observation).** The cure←bundle sentence covers "every monthly fee line … since the start" of storage, while the bundle rule credits only the most recent line. Tested per task.
- **O-5 (observation).** Two `condition` fields are slightly narrower than their sentences.
- **O-6, O-7 (observations).** Realness notes on warning_surcharge and handling_share.
- **O-8 (observation).** `RND` is Python `round`, not half-up. On an exact binary tie it rounds half to even. For example, 68.625 gives 68.62 where the rules' "rounded half up" gives 68.63. This matters only where a scored value lands on such a tie; checked per task.

## closing_checklist

Written after both reveals (2026-09-24T17:19:08Z). The charter-global section above was frozen before any reveal (sha256 at freeze `445182ae3a9d1152e333a698dea44312a1fc66f2d24682d4753efb41cdc243d7`) and is left untouched.

**The difficulty does NOT close.** Not every task passes all four relationships.

| item | status |
|---|---|
| per-task files 0.md, 1.md alongside `_difficulty.md`; this is revision 1, with no older revisions | yes |
| every comparison section carries a PASS | **no**: 0 = SOURCE-FACTOR RED; 1 = SOURCE-FACTOR RED + SOURCE-CHAIN RED |
| extended policies fully covered; scopes pairwise disjoint and spanning whole trees | yes: task 0 {idle, early_cancellation}; task 1 {fine, bundle, cure, restoration}, matching charter_scope |
| task tools and GT closed; independently generated uuid8s | yes |
| every tree has 1–3 prerequisite problems, ≥ max(n−1, 1) value_input edges, a user-owned write, no cycle; the whole-difficulty graph is a DAG | yes (task 0: n=1, 1 value_input, root is user-owned; task 1: n=3, 3 value_input, cure payment is user-owned). Task 1's tree nonetheless fails on the persona hint (1.md finding 2) |
| every computation has a self-sufficient baseline, 4–6 factors with 2 parameter and 1 method, honest labels, and every factor bearing weight with the baseline ≠ gold | **no**: C-2a (task 0, label only), C-2b/c/d (task 1: three computations with 0 honest method factors). Every factor bears weight, and every all-baseline number is definite and ≠ gold |
| charter-global findings | **C-1 SOURCE-POLICY RED** (early cancellation compute ignores the end-date gate; no consequence on task 0's world); observations O-1 to O-8 |
| instantiation-stage gates re-run on the final form | not re-run by this auditor (the audit edits nothing). The coordinator's pre-audit snapshot is all green; the artifacts' hashes are unchanged since that snapshot |

Per-task verdicts:
- task 0: **SOURCE-FACTOR RED**
- task 1: **SOURCE-FACTOR RED + SOURCE-CHAIN RED**

---

## revision_2

### charter_global_frozen (revision 2)

- Freeze time: 2026-09-24T18:06Z. Same auditor as revision 1. Nothing in this section derives from round-2 GT; the round-2 task files were still unopened when it was written.
- Hashes:
  - `parking.extended.yaml` = `e797adf3443ec4f3aaf97579a8ba49e1271d3c3d76211bc73ca4f32eec222b9c`. **This changed** from `9011405315…`, so every charter-global section is re-derived below.
  - `task_tools.py` = `dfaf3570773ee11c38fecf786a1aa264ebda1553d85406ac5a99c4e4d24973ab`. Unchanged.
  - `products/parking.yaml` = `bc48c01a…`. Unchanged.
- The base section is still verbatim identical to the blueprint (diff shows only the trailing blank line).
- Disclosure: this auditor has read the round-1 GT (at 17:19:08Z, during the round-1 reveal). It did not use that GT in the re-derivation. Every figure below was recomputed from the round-2 charter.

### policy_conflict_scan (r2)

- Subjects, target tools and computed quantities are unchanged: the six-row table of revision 1 still holds.
- Two extended policies still supersede the same base restoration sentence. Their replacements are unchanged and compatible.
- storage_bundle_discount now has a **second, declared** overwrite of household_pricing. The base sentence "The bundle discount does not stack … not posted for a month in which the storage rental was not active on the fee charge day." is superseded verbatim. It is replaced by the same two limits plus "the welcome catch-up for the storage-active days before the first covered fee line is carried on that first covered line".
  - That replacement sentence is verbatim in the rule and consistent with the catch-up factor.
  - No other policy claims the pre-storage month.
- The prerequisite graph is unchanged in shape: {idle → early_cancellation} and {fine, bundle → cure → restoration}. The only admissible M=2 partition is still one scope per component.

### rule_compute_equivalence (r2)

- A script check shows every `compute_basis` quotation of all six policies is verbatim in its rule, and every `baseline.rule` sentence is in its rule.
- **C-1 check.** The early-cancellation gate now reads: "When, at the notice date, the whole months from the license's start date are fewer than the commitment months, an early cancellation fee is billed with the notice; when they are not, no early cancellation fee is billed."
  - It is implemented as `fee_applies: held_months < commitment_months` and `result: … if fee_applies else 0`, and quoted in compute_basis.
  - The same sentence replaces the base clause in `overwrite` and opens `baseline.rule`.
  - Rule and compute now reach the same conclusion in every situation. For example, the round-1 counter-case (end date 2026-11-15) gives a fee under both, because 3 held months < 5.
- **O-1 check.**
  - The fine rule now says "less the fine standing reduction".
  - The restoration rule now says "the reinstatement standing reduction" in all three tiers and in the sum.
  - Both names are consistent across rule and basis.
- The new ladders appear in both the rule and the compute:
  - fine `repeat_step_up`: per fine / flat / none.
  - bundle `program_rate`: pct + premium high / mid / pct.
  - bundle `catchup_factor`: prorated / flat month / none.
  - restoration `gate_reactivation`: per remote / flat / none.
- **O-2 check.** The fine rule's generic sentence "Warnings and fines on record are counted over the default_window_months months…" is gone. The only counting sentence left is "Other fines of the license are counted over the default_window_months months before the handling date.", which covers only the schedule's own repeat count. The base escalation window is no longer restated.

### action_binding_and_uuids (r2)

- Carried forward from revision 1 by reference, because `task_tools.py` is unchanged (hash above).
- The `(target_tool, computes)` pairs in the charter are unchanged and each is claimed once.

### prerequisite_graph (r2)

- Same four edges, same kinds, gates, forms and resolving tools. Acyclic. Each `policy_source` is verbatim in its own rule.
- **O-5 check.**
  - restoration←cure condition: "A payment covering the cure amount stands received on the license, and it is the most recent payment…". The "today" narrowing is gone.
  - early←idle condition: now "stands at its scheduled idle fee, net of any charge reversal credit pointing at it". This matches the sentence.
  - cure←fine condition: still "carries the charge reversal credit that brings it down…". This slight narrowing remains (observation, carried).

### prerequisite_sentences (r2)

- early←idle and cure←fine are unchanged and pass as in revision 1.
- restoration←cure is unchanged and passes.
- **O-4 check.** cure←bundle now reads: "The cure amount is not worked out until the most recent monthly fee line of the license, when it was posted on or after the start date of the lease's active storage rental, carries the storage bundle discount credit owed on it."
  - Its object is now exactly the bundle rule's object ("The fee line credited is the most recent monthly fee line of the license").
  - Connective: "not … until". State form. Exactly one resolving write (the bundle credit).
  - The breadth mismatch is closed.
- No docstring changed.

### override_declarations (r2)

Only the sentences whose disposition changed are listed. Everything else is as in revision 1.

- **early_cancellation ← cancellation_rule.** The fee sentence is now replaced by a notice-date tenure gate rather than an end-date gate. It is declared.
  - Observation O-9 (new): a resident who gives notice inside the commitment but picks an end date past the commitment end still pays a prorated fee. This is declared, consistent, and prorated by unexpired months at the notice date. There is no demonstrable second answer.
- **bundle ← household_pricing.** Both the rate sentence and the no-stack / fee-charge-day sentence are now declared.
- **fine ← enforcement.** The only fine-schedule sentence that re-anchored the base escalation count has been removed (O-2). No undeclared override remains.

### factor_ladders (r2)

| policy | parameter | method (label test) | multi-source | cross_difficulty |
|---|---|---|---|---|
| idle | grace, standing_rate, volume, escalation, session_multiplier (relabelled `parameter`: honest) | hour_counting (honest) | grace, hour_counting, session | standing_rate → lease |
| early_cancellation | fee_months, commitment, program_share, activation | fee_base_method, commitment_proration (honest) | fee_base, fee_months | term, lease |
| fine | class_amount, counting_window (relabelled `parameter`: honest), warning_surcharge, standing_reduction | **repeat_step_up**: per-fine accrual `repeat_step_per_fine × n` vs a flat `repeat_step_single` vs none. One tier's result scales with the count and the other does not, so the algorithm differs: **honest** | class_amount, counting_window | standing_reduction → lease |
| bundle | program_rate, lease_loyalty, parking_tenure, clawback | **welcome_catchup**: `1 + min(1, active days before posting ÷ 30)` (a proration over a day span) vs a flat `1 + 1` vs none: **honest** | welcome_catchup (bundle history + storage start) | lease_loyalty → lease |
| cure | prepay_months, prepay_reduction | cure_scope, prepay_fee (as in revision 1) | cure_scope, prepay_fee | lease |
| restoration | graduated, enforcement, standing, household_relief, handling_share (relabelled `parameter`: honest) | **gate_reactivation**: per remote `7.50 × remotes` vs a flat `10.00` vs none: **honest** | gate_reactivation (product + remote-fee lines) | standing_reduction → lease |

- Every policy now has 4–6 factors, ≥2 `parameter`, ≥1 honest `method`. Labels are honest throughout. **C-2a, C-2b, C-2c and C-2d are closed.**
- **O-3 check.** `program_rate` is now "the product's pct + bundle_premium_high / + bundle_premium_mid / the product's pct", with premiums 0.05 and 0.02. It can no longer collapse on any product (for example, Private Detached Garage gives 0.20 / 0.17 / 0.15). Closed.
- Tier outcomes are distinct on every product for the new ladders:
  - repeat step: 10n with n ≥ 2 gives ≥ 20, versus 15 and 0.
  - gate: 7.5n with n ≥ 2 gives ≥ 15, versus 10 and 0.
  - catch-up: a factor in [1, 2] prorated, versus exactly 2 flat, versus 1. The prorated tier reaches 2 only when the storage started ≥ 30 days before the fee line's posting date inside a < 60-day window. The two tiers then meet at one value on a boundary case, not by construction. Observation O-10.
- Realness:
  - Per-fine repeat step-ups, per-remote reactivation charges and a prorated catch-up for missed bundle days are ordinary operator practice.
  - O-6 (warning surcharge) and O-7 (handling share realness) are unchanged, as the reworker states. They remain observations.
- `cure_prepay_months_one` changed 0.5 → 0.75 and `cure_share_mid` changed 0.025 → 0.03. These are value changes only, with no structural effect.

### findings (r2)

| id | revision-1 finding | revision-2 status |
|---|---|---|
| C-1 | SOURCE-POLICY RED (end-date gate not computed) | **closed**: the gate is now in rule, baseline, overwrite and compute alike. The new gate carries observation O-9 |
| C-2a | idle_session_multiplier mislabelled | **closed** (relabelled `parameter`; idle keeps an honest method) |
| C-2b | fine_counting_window mislabelled | **closed** (relabelled; repeat_step_up is now an honest method) |
| C-2c | bundle_welcome_multiplier mislabelled | **closed** (replaced by the welcome_catchup method) |
| C-2d | restoration_handling_share mislabelled | **closed** (relabelled; gate_reactivation is now an honest method) |
| O-1 | basis not verbatim | **closed** |
| O-2 | fine counting re-anchored | **closed** |
| O-3 | program_rate collapse on Private Detached Garage | **closed** |
| O-4 | cure←bundle sentence broader than the bundle rule | **closed** |
| O-5 | conditions narrower than sentences | **mostly closed**: cure←fine's condition is still narrower (observation) |
| O-6, O-7 | realness notes | unchanged, as the reworker claims; observations |
| O-8 | engine rounds half-to-even on ties | engine unchanged (outside this audit's write domain). Scored values are checked per task: neither task's round-2 values sit on a tie |
| O-9 (new) | fee gate uses notice-date tenure, not the end date | observation |
| O-10 (new) | catch-up tiers can meet at 2.0 on a boundary | observation |

**No charter-global RED remains in revision 2.**

## closing_checklist (revision 2)

Written after the round-2 reveals (2026-09-24T18:07:12Z). The revision_2 charter-global section above was on disk before the reveal, with sha256 at that point `8128f9e2…`.

| item | status |
|---|---|
| per-task files alongside `_difficulty.md`; revision-1 text preserved; revision_2 appended to all three | yes |
| every comparison section carries a PASS | **yes**: task 0 PASS, task 1 PASS |
| extended policies fully covered; scopes pairwise disjoint and spanning whole trees | yes: {idle, early_cancellation} and {fine, bundle, cure, restoration}, matching charter_scope |
| task tools and GT closed; uuid8s independent (tools unchanged) | yes |
| trees: 1–3 prerequisites, value_input floor, user-owned write, acyclic; graph a DAG | yes (task 0: n=1, 1 value_input; task 1: n=3, 3 value_input); the persona hints are clean in both |
| computations: self-sufficient baseline, 4–6 factors, ≥2 parameter / ≥1 honest method, multi-source and cross-difficulty per task, every factor bearing weight, all-baseline ≠ gold | yes: all six computations |
| charter-global REDs | none: C-1 and C-2a–d are closed. Observations O-5 (residual), O-6, O-7, O-8 (engine), O-9 and O-10 remain; none demonstrates a consequence on either task |
| gates re-run on the final form | the coordinator's post-rework snapshot is all rc=0 (check_traceability deferred to render). This auditor edits nothing and did not re-run them |

**The difficulty passes the source-layer audit in revision 2.**

Per-task verdicts:
- task 0: **PASS**
- task 1: **PASS**
