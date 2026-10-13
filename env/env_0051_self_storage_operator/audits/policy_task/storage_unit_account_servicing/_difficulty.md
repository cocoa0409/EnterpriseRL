# Policy-task audit — storage_unit_account_servicing / charter-global

## charter_global_frozen

- Freeze time: 2026-10-10T19:44:43Z UTC (file mtime). Auditor: erl-task-policy-audit subagent. It is independent of the instantiating agent and has no access to the instantiation worklog.
- Frozen inputs (sha256, recomputed by the auditor; they match the coordinator's brief):
  - `tasks/storage_unit_account_servicing/unit.extended.yaml` = `8e2f60bfad61490bbe35ebee379a6ccc151079c34fe9cd335d53dd69ad69e382`
  - `tasks/storage_unit_account_servicing/task_tools.py` = `9c6399f73db983c081de4afa591e0c580e66e2c61d8175ad0f12df677f0b39ae`
  - masked views `0.view.json` = `680b5900…4d24a` and `1.view.json` = `496ad79f…4e36e`. Both match the brief.
- Read for this section: `blueprint/products/unit.yaml`, the autopay, protect, prepay and parking product charters (variant parameters only), `blueprint/db_schema.json` and `blueprint/share_tools.py` (finder signatures), the extended charter, `task_tools.py`, and `skills/erl-task-instantiate/scripts/check_compute.py` (the DSL semantics of MONTHS, DAYS, within_months, LATEST, CFIELD, CPARAM and XLATEST).
- Masked and not read: every field of `tasks/0.json` and `tasks/1.json` other than what the masked views carry (`evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, the closure fields). This section contains nothing derived from any revealed GT.
- Entry conditions (Step 0): the brief carries the gate snapshot. EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING and SCOPE are all OK. check_traceability is deferred to the render stage, and validate_scenario reports only missing KB documents. The masked views come with their hashes. The entry conditions are met. The traceability deferral is recorded as given and is not a finding.
- Base copy: lines 1–1693 of `unit.extended.yaml` are byte-identical to `blueprint/products/unit.yaml`. `diff` shows only the appended `# extended_policies` banner comment.

### policy_conflict_scan

The charter has six extended policies:

| id | trigger | subject | target_tool (owner) | computes |
|---|---|---|---|---|
| unit_ext_late_fee_schedule | state_due | unit_fee_charge | assess_unit_late_fee_4b513073 (agent) | amount |
| unit_ext_returned_payment_fee | state_due | unit_fee_charge | post_unit_returned_payment_fee_fb0d77c5 (agent) | amount |
| unit_ext_returned_payment_replacement | on_request | unit_payment | pay_unit_returned_balance_f137f581 (user) | amount |
| unit_ext_good_standing_payment | on_request | unit_payment, unit_redemption | restore_unit_good_standing_afa2c723 (user) | amount |
| unit_ext_increase_limit_correction | state_due | unit_rate_change_notice | reduce_unit_rate_increase_85726890 (agent) | new_rent |
| unit_ext_retention_concession | on_request | unit_rate_change_notice | grant_unit_retention_concession_f9ae06a9 (agent) | new_rent |

- **Late fee vs returned-payment fee.** Both are `unit_fee_charge`, separated by `fee_type` (late_fee / returned_payment_fee), and their `reference_entry_id` objects differ (the rent charge vs the returned payment). Neither reads the other's output, so there is no overlap.
- **Reduction vs concession.** Both are `unit_rate_change_notice`, separated by `change_reason` (increase_rescinded / retention_concession). The concession reads the reduction through `rent_as_stands`, and that ordering is a declared edge.
- **Replacement vs good-standing (observation O-1).** Both are on_request phone payments by the tenant. Replacement: "A tenant whose payment the bank returned replaces it with one payment …". Good-standing: "A tenant brings a delinquent storage agreement back to good standing with one payment …". Their triggers overlap whenever a tenant has a bank-returned payment and the agreement is delinquent. Neither rule states which one governs, and they price the payment differently (balance + security advance vs balance + next-period coverage). Base `unit_evt_late_fee` says "The first late fee of a cycle moves an active rental to delinquent", and base `unit_evt_payment_acceptance` says "A reversal that leaves rent from a period past its grace period unpaid makes the rental delinquent again". So by the charter's own text, a tenant reaching the replacement policy after the late fee is posted is also "delinquent". The overlap is real at the charter level. Whether it costs a task depends on that task's records; see `0.md` → policy_self_consistency.
- **Cross-category reads.** All are reads: protect (late fee), autopay (returned fee, good-standing, concession), prepay (increase limit), parking (concession). No extended policy writes another category.
- **Inherited base provisions.** None is weakened (details under override_declarations).
- **Scope partition, derived blindly from the prerequisite graph.** There are two connected components:
  - {replacement ← late fee, replacement ← returned fee}
  - {concession ← increase limit ← good-standing}

  Two tasks with one tree each would cover all six policies exactly once. Whether the M=2 claimed scopes are exactly these is checked per task after the reveal; the claimed blueprint scope is category `unit` only.

### rule_compute_equivalence

Check 2 was swept over every binding of all six policies. Every binding has a `compute_basis` quotation that is a verbatim fragment of its own `rule`, and every rule sentence that names a quantity, window, tier, rounding or order has a binding. Points checked in detail:

- **Late fee.**
  - The order sentence is implemented exactly by `shared_fee` and `result`: percentage × (rent basis + protection) × tenancy share × returned share, one half-up rounding, then max with the floor, then capped.
  - `rent_basis` implements the three-way sentence.
  - `late_fees_12m` uses `within_months=12`, which under the DSL means 0 ≤ MONTHS(entry_date, NOW) < 12.
  - The floor is keyed to the rent charged (`charged_rent_level` = latest rent charge).
  - Observation O-2: `paid_in_grace_then_returned` reads the agreement's latest payment and latest reversal. It does not restrict them to "the period's" payment, and it does not check that the reversal points at that payment. The rule's wording is narrower than compute. The two coincide whenever the latest payment is the one for the latest period and the latest reversal returns it, which holds in task 0's world. No task here is affected.
- **Returned-payment fee.**
  - `fee_level` follows the returns count "with the return being charged included".
  - `limited_fee` rounds each percentage amount to the cent.
  - `reasoned_fee` follows Python precedence `(limited_fee + 5) if closed else (0 if chargeback else limited_fee)`, which matches the rule.
  - `autopay_share` reads `status='suspended'` with suspension_date for "Bluegate suspended", and `status='cancelled', end_reason='tenant_revoked'` for "the tenant cancelled". Both are in the schema enums.
  - The single final rounding matches "rounded … once".
- **Replacement.**
  - balance = F('balance_due').
  - The advance-month count, the next-due-rent ladder (concession → increase → contracted, both "effective date after the handling date"), the advance-month billing ladder (vacate on or before the latest period end → 0; military → rent × (1 − pct) half-up; else rent) and the tenancy share all match the rule sentence for sentence.
  - The result is balance + security advance.
- **Good-standing.**
  - The ledger-derived balance lists exactly the families the rule lists: rent, fee, reversal and refund less payment, credit and sale-proceeds. The enum names exist in the schema.
  - Coverage months, covered-month price, timing share (next due = latest period_end + 1 day, with ">28", "15 to 28" and nearer), AutoPay-history share (active authorization only, "shorter or missing" → 1) and delinquency share all match the rule.
  - Rounding is applied once to coverage and once to the total.
- **Increase limit.**
  - The tenure, recent-increase, prepaid, lien and lateness reductions match the rule.
  - "Took effect … in the 24 months" is read by effective_date with within_months, so future-effective notices are excluded (MONTHS < 0).
  - The cap base matches the rule. Rounding down uses `int(x*100+1e-9)/100`. The limit rent is the contracted rent plus the allowed increase. The result is min(noticed, limit).
- **Concession.**
  - rent_as_stands (reduction notice if on file, otherwise the increase's own new rent) matches the rule. increase = rent_as_stands − previous_rent.
  - The start share and the four additions match the rule. The bands are measured against the rent before the increase. The give-back is rounded down. The result is rent_as_stands − give-back.
- **Ladders against rules.** Every `factors[].ladder` tier is a sentence of its rule and a branch of the `decides` binding, and every branch is a stated tier. No tier lives only in compute.

**Result: no rule/compute gap that changes a scored value.**

### action_binding_and_uuids

- **Target-tool claims.** Each `(target_tool, computes)` pair is claimed by exactly one policy (see the table above). The six tools map one-to-one to the six policies.
- **Docstrings.** None names another tool or states a position in a sequence. The words "first" and "before" appear only as data descriptions ("the due date (first day) of the billing period", "rent-before-change"), not as action order. No docstring adds a confirmation, review or wait.
- **Tool bodies.** Each body writes only what its docstring says. No tool checks a status, balance, date or prior row; the only lookups are `ctx.find(...)[0]` on the rental and on the source rate change. So **no tool judges a prerequisite.**
- **uuid8s.** 4b513073, fb0d77c5, f137f581, afa2c723, 85726890 and f9ae06a9 are all distinct. There is no shared prefix or suffix, no sequence and no adjacent values. They are consistent with independent generation.
- **Observation O-3 (tool omits a base state transition).** `assess_unit_late_fee_4b513073` does not move an active rental to delinquent or set delinquent_since, although base `unit_evt_late_fee` says "The first late fee of a cycle moves an active rental to delinquent, with delinquent_since set to that period's due date". `pay_unit_returned_balance_f137f581` does not redeem (active, delinquent_since cleared) a rental it brings to zero or below, although base `unit_evt_payment_acceptance` says it does. For a late fee followed by a full replacement payment the two omissions cancel in the terminal status. The terminal-state consequence is judged per task.

### prerequisite_graph

Check 7:

| blocked policy | problem | kind | gate | form | policy_source verbatim in blocked rule | resolved_by = depended target_tool |
|---|---|---|---|---|---|---|
| replacement | late_fee_schedule | value_input | `balance` (binding exists) | state | yes | yes |
| replacement | returned_payment_fee | value_input | `balance` (binding exists) | state | yes | yes |
| increase_limit | good_standing | state_gate | unit_rentals.status | state | yes | yes |
| concession | increase_limit | value_input | `rent_as_stands` (binding exists) | state | yes | yes |

- Every policy has `prerequisite` filled in; late fee, returned fee and good-standing have `[]`.
- Every `problem` is an extended id in this file, never a base id and never itself.
- The graph is acyclic: two disjoint trees of depth 1 and depth 2.
- There is no action-form edge and no `fallback_reason`.
- No authoring-viewpoint phrasing ("in this task", "at the opening") appears in any prerequisite field.
- **Finding F-1 (SOURCE-POLICY RED, charter-global, bears on task 0).** The `condition` of edge replacement ← returned_payment_fee is stated over the wrong object, and the resolving write can never make it hold.
  - condition: "Every unit_payment_reversal entry with reversal reason ach_return_insufficient_funds or ach_return_account_closed on the agreement is referenced by a returned_payment_fee entry, so the balance due includes each of those fees."
  - policy_source: "The replacement amount is not fixed until every payment the bank has returned on the agreement carries its returned-payment fee."
  - Tool contract: `post_unit_returned_payment_fee_fb0d77c5.reference_entry_id` is "the ledger entry number of the payment the bank returned (the payment entry the reversal points at)".
  - Schema: `unit_ledger.reference_entry_id` is the "payment behind a reversal or returned-payment fee".

  A returned-payment fee therefore references the **payment**, never the reversal entry. Read against the records, the condition is false for every reversal that has ever been fee'd, and it stays false after `resolved_by` runs. The condition is thus stricter than the sentence (it covers a different object), and `resolved_by` cannot make it hold. The demonstration against task 0's world is in `0.md`.
- All other conditions match their sentences:
  - The late-fee condition is "late_fee entry … referencing its rent charge", which is what the tool's reference_entry_id carries.
  - The good-standing condition is "status is active and delinquent_since is empty", which is exactly what `restore_unit_good_standing_afa2c723` writes.
  - The concession condition is "new rent at or below the limit, or a reduction notice … carries the limit rent".

### prerequisite_sentences

Check 6, edge by edge:

1. **replacement ← late fee.** Sentence: "The replacement amount is fixed only after the ledger carries a late fee for every billing period whose rent remains unpaid past its grace days."
   - Connective: "only after".
   - Waited-on state: record-visible (a late-fee entry on the ledger for each unpaid-past-grace period).
   - No tool, id or snake_case token.
   - Exactly one write of this difficulty produces a `late_fee` ledger entry: `assess_unit_late_fee_4b513073`. The returned-fee tool writes fee_type returned_payment_fee.
   - Derivation: the reader finds the unpaid-past-grace period on the ledger. The only policy whose rule posts "a late fee … for a billing period whose rent is still unpaid after its grace days" is unit_ext_late_fee_schedule, which yields one reading.
2. **replacement ← returned fee.** Sentence: "The replacement amount is not fixed until every payment the bank has returned on the agreement carries its returned-payment fee."
   - Connective: "not until".
   - Waited-on state: record-visible (a returned-payment fee against each bank-returned payment).
   - Exactly one write produces it: `post_unit_returned_payment_fee_fb0d77c5`.
   - The depended-on rule ("one returned-payment fee is posted against that returned payment") names the same object, which yields one reading. (The `condition` defect is F-1 above. The sentence itself is sound.)
3. **increase_limit ← good-standing.** Sentence: "A reduction of a noticed increase is noticed only once the agreement stands in active status with no delinquency date on it."
   - Connective: "only once".
   - Waited-on state: record-visible (status, delinquent_since).
   - Writes of this difficulty that set status=active and clear delinquent_since: only `restore_unit_good_standing_afa2c723`. `pay_unit_returned_balance_f137f581` changes balance_due only.
   - Observation O-4: under the base charter text, a replacement payment that brings a delinquent rental to zero or below would also redeem it. A reader of the rules alone could then see two writes reaching "active, no delinquency date" in a world that has both a returned payment and a delinquency. The hop is unique only where the replacement policy's subject (a bank-returned payment) is absent; this is judged per task.
4. **concession ← increase_limit.** Sentence: "The retention concession is not figured until the agreement's rent changes show its noticed increase at or within the increase limit."
   - Connective: "not until".
   - Waited-on state: the rent-change records.
   - Exactly one write puts a rent-change row at the limit: `reduce_unit_rate_increase_85726890`. The concession's own write is the blocked one.
   - One reading.

Further checks:
- No depended-on rule restates its blocked sentence (checked programmatically: the normalised sentence is not a substring of the depended-on rule).
- No other rule states a cross-problem order: no sentence of the six rules orders one of these writes against another, apart from the four edges.
- Base sentences: base `unit_evt_rate_increase` "Rate increase notices are issued only to rentals in active status" applies to `unit_rate_change_notice`, so it also covers the reduction and the concession. The extended rule carries its own state-form sentence for the reduction, so no tree rests on a base sentence. Recorded as an observation only.
- Docstrings are silent about sequence.

### override_declarations

Check 1 (findings half), sentence by sentence against each `base_policy_refs` entry:

- **unit_ext_late_fee_schedule vs unit_evt_late_fee.**
  - "assessed once … any part … unpaid after grace": followed.
  - "posted only when handling date later than due + grace_period_days": inherited, not contradicted.
  - Grace counting: inherited.
  - **Amount sentence** ("greater of late_fee_flat_usd and late_fee_pct_of_rent times the monthly rent … never more than late_fee_max_usd"): **handled differently**. The basis, percentage, floor, shares and order all change. It is named in `overwrite` as superseded_clause, and replaced_by is the rule's own order sentence. The merged reading is unique: the ladders define every input.
  - Second late fee at second_late_fee_days_after_due: inherited, untouched.
  - Status set: inherited.
  - "at most one late fee and one second late fee": compatible.
  - "fully paid on or before the last grace day → never charged": followed.
  - "first late fee … moves an active rental to delinquent": inherited (tool omission is O-3).
  - No undeclared override. No anonymous intermediate factor: the floor change sits inside the declared clause. No 0/1 multiplier: the shares are 0.5–0.9 and never zero. No dropped branch.
- **unit_ext_returned_payment_fee vs unit_evt_payment_acceptance.**
  - The "reversed in full and returned_payment_fee_usd is posted … a card chargeback is reversed without that fee" sentence is replaced. The declaration is present.
  - Every other acceptance sentence is untouched.
  - vs unit_evt_late_fee: no sentence of the late-fee policy governs the returned fee. Nothing to declare.
- **unit_ext_returned_payment_replacement vs unit_agg_payment_allocation and unit_evt_payment_acceptance**, `overwrite: []`.
  - Named-unit payment applied only to that agreement, excess kept as a credit balance: followed.
  - payment_application_order and one row per agreement: compatible.
  - Accepted phone methods: compatible.
  - Any amount while delinquent and full balance after a lien notice: compatible, because the replacement amount is at least the balance.
  - Redemption when the balance reaches ≤ 0: not contradicted by the rule (tool omission O-3).
  - No base sentence fixes the payment amount, so `[]` is correct.
- **unit_ext_good_standing_payment, same refs**, `overwrite: []`. "Returns the agreement to active status and clears its delinquency date" agrees with base redemption ("balance due to zero or below … returns to active, delinquent_since is cleared"), because the amount is at least the balance. All other sentences are as above. `[]` is correct.
- **unit_ext_increase_limit_correction vs unit_evt_rate_increase.**
  - "The new rent is at most the current monthly rent times one plus rate_increase_max_pct, rounded down" is replaced. The declaration is present.
  - Eligibility windows, notice days and active-only notices are inherited; the extended sentence is stricter and compatible.
  - Prepaid lock is inherited. The concession sentences are not touched by this policy.
- **unit_ext_retention_concession vs unit_evt_rate_increase.**
  - "gives back retention_concession_pct_of_increase of the increase, rounded down" is replaced. The declaration is present and covers the change of base, which is now "the increase's rent as it stands".
  - Request window, 365-day count, "already taken effect", "move-out notice → no concession" and "agreement rent on the effective date is the concession's new_rent" are inherited and compatible.

**Result: no undeclared override found.**

### factor_ladders

Each policy has 4–6 factors, every ladder has 3 tiers with "otherwise" as the fall-through, every fall-through equals the factor's `baseline`, every factor's `decides` is an input rather than `result`, and binding sets are disjoint within each policy (all checked programmatically).

| policy | factors (label) | parameter / method | cross_difficulty | multi-source factor(s) |
|---|---|---|---|---|
| late fee | rent_basis (method), lateness_percentage (param), protection_fee_basis (method, protect), tenancy_share (param), returned_payment_share (param), floor_by_rent_charged (param) | 4 / 2 | protect | returned_payment_share (each non-fall-through tier: payment row in grace AND later reversal AND a 12-month return count) |
| returned fee | level_by_returns (param), amount_limit (method), return_reason (param), autopay_share (param, autopay) | 3 / 1 | autopay | none (each tier is one record or one count) |
| replacement | advance_months (param), next_due_rent (param), advance_month_billing (method), advance_tenancy_share (param) | 3 / 1 | none | next_due_rent tier 2 ("no such concession … and an increase noticed …"), advance_month_billing tier 2 (no vacate date AND military flag) |
| good-standing | coverage_months (param, autopay), covered_month_price (method), timing_share (param), autopay_history_share (param, autopay), delinquency_share (param) | 4 / 1 | autopay | coverage_months (autopay status AND latest draft result; autopay status AND ledger late-fee count) |
| increase limit | tenure_maximum, recent_increases, prepaid_plan (prepay), lien_record, lateness (all param), cap_base (method) | 5 / 1 | prepay | lien_record tier 2 (steps AND no notice), cap_base tier 2 (last change a concession AND no lower rent billed) |
| concession | history_start, autopay_rail (autopay), parking_standing (parking), rent_stability, notice_lead_time (all param), banded_give_back (method) | 5 / 1 | autopay, parking | parking_standing (active AND balance) |

**Labels.**
- The `method` factors that change an algorithm are: amount_limit (min-cap vs no cap), advance_month_billing (zero / discount / as-is), covered_month_price, and banded_give_back (banded vs flat).
- rent_basis, protection_fee_basis and cap_base choose which base the percentage acts on, or what is added to it. That is a change of acting base rather than a substituted rate, fee or threshold, so the `method` label is accepted.
- Observation O-5: these three are borderline, since each tier still feeds one number into the same product.
- No `parameter` factor changes an algorithm.

**Baselines.**
- Each `baseline.rule` sentence is a verbatim sentence of its rule, and `baseline.params` names the class parameters it uses.
- Late fee, returned fee, replacement, good-standing and increase limit give a definite number from the baseline alone.
- **Finding F-4 (SOURCE-FACTOR RED, charter-global, bears on task 1):** the concession baseline does not. It is "The give-back is the class's retention share of the increase." It defines only the give-back, not the scored quantity `new_rent` ("the increase's rent as it stands less the give-back" is in a non-baseline sentence). It does not say what "the increase" is measured from (the noticed new rent or the reduced rent). It does not state the rounding: the "rounded down to the cent" sits in the rule's first sentence, not in baseline.rule. A reader of baseline.rule alone gets a give-back of 50% of an unspecified increase, with no new rent and no rounding. Per-world consequences are in `1.md`.

**Reality of the ladders.**

- **Finding F-2 (SOURCE-FACTOR RED, charter-global, bears on task 0): `returned_fee_return_reason` has a tier no customer reaching this write can occupy.**
  - Ladder: closed account → limited fee + 5; card chargeback → 0; otherwise → limited fee.
  - The policy's scope sentence is "When the bank returns a payment on the agreement for insufficient funds or because the account is closed, one returned-payment fee is posted …", and base `unit_evt_payment_acceptance` already says "a card chargeback is reversed without that fee".
  - The tool requires the amount to be "always positive".
  - So the chargeback tier restates the policy's scope exclusion and divides no customer who reaches the write. The ladder has only two live tiers (closed / insufficient funds), below the three-tier floor. Struck as a factor, the returned-fee computation is left with 3 factors (< 4).
- **Finding F-3 (SOURCE-FACTOR RED, charter-global, bears on task 1): the band rates of `concession_banded_give_back` exceed 100% under the share the same rule builds.**
  - The share starts at 0.60 or 0.55 (or the class share of 0.5) and adds up to 10 + 5 + 5 + 3 points, a maximum of 0.83.
  - The moderate tier gives back the part above 5% "at one and a half times the share", which exceeds 100% of that band once the share exceeds 0.667.
  - The steep tier gives back the part above 5% "at twice the share", which exceeds 100% once the share exceeds 0.5. With a share above 0.5 the steep tier alone can return more than the whole increase, so the "retention concession" sets the rent below the rent before the increase.
  - No storage operator publishes a give-back that refunds more than the slice of increase it is applied to, or more than the increase. The per-world demonstration is in `1.md`.
- **Finding F-5 (SOURCE-FACTOR RED, charter-global, latent; bears on no task in this bundle): `late_fee_lateness_percentage` gives the same value in two tiers for two classes.** The tiers are "one or two late fees → 20 percent" and fall-through "none → the class's late-fee percentage". For Bluegate Drive-Up Standard and Bluegate Interior Standard, `late_fee_pct_of_rent` = 0.2, so both tiers select 20%. Both bundle tasks are on other classes (Climate Plus and Climate Controlled), so no scored value here is affected.
- Observation O-6: `increase_limit_tenure_maximum` is non-monotone for Premier Climate Suite (younger 9%, 48–83 months 10%, 84+ months 8%) and Wine & Collectibles Vault (younger 7%, 48–83 months 10%). The tiers are distinct and the direction is a business choice; not a red.
- Observation O-7: tier 2 of `good_standing_covered_month_price` (military discount but latest charge not below the contracted rent) is reachable only in edge cases. One example is a transfer to a cheaper unit while the old period's charge stands. For the Vault class (military_discount_pct 0.0) it would select the same value as the fall-through. Task 1 sits on tier 1, so this is recorded as an observation.
- Every other tier condition is one a self-storage operator weighs: tenure, lateness history, bank-return history, AutoPay standing, rent actually billed, protection plan, prepaid history, lien history, notice lead time, a parking holding. No other tier holds for every customer reaching its write. Every tier value is drawn from `params` or the class parameters.

**Per-task counts, using the derived trees.**
- Task 0 = late fee + returned fee + replacement.
  - Multi-source: yes (late-fee returned_payment_share and others).
  - Cross-difficulty: yes (protect, autopay).
  - Factor counts: the returned fee falls below 4 once F-2 strikes return_reason.
- Task 1 = good-standing + increase limit + concession.
  - Multi-source: yes (coverage_months and others).
  - Cross-difficulty: yes (autopay, prepay, parking).
  - Method count: the concession loses its only `method` factor if F-3 strikes banded_give_back.

### findings

| id | class | summary | bears on |
|---|---|---|---|
| F-1 | SOURCE-POLICY RED | condition of edge replacement ← returned_payment_fee is stated over reversal entries, which the fee never references; `resolved_by` can never make it hold | task 0 |
| F-2 | SOURCE-FACTOR RED | returned_fee_return_reason: the chargeback tier restates the policy scope, leaving 2 live tiers | task 0 |
| F-3 | SOURCE-FACTOR RED | concession_banded_give_back: band rates above 100%; the steep tier can cut rent below the pre-increase rent | task 1 |
| F-4 | SOURCE-FACTOR RED | concession baseline.rule is not self-sufficient (no new_rent, undefined "increase", no rounding) | task 1 |
| F-5 | SOURCE-FACTOR RED (latent) | late_fee_lateness_percentage tiers 2 and 3 coincide for Drive-Up and Interior Standard | none in bundle |
| O-1 | observation | replacement / good-standing triggers overlap with no precedence | task 0 (demonstrated there) |
| O-2 | observation | late fee paid_in_grace_then_returned is not restricted to the period's own payment | none |
| O-3 | observation | late-fee and replacement tools omit base status transitions | task 0 (terminal state) |
| O-4 | observation | the good-standing state hop could also be reached by a redeeming replacement payment under the base text | task 1 (checked there) |
| O-5 | observation | the "acting base" method labels are borderline | — |
| O-6 | observation | tenure maximum is non-monotone for Premier and Vault | none |
| O-7 | observation | covered-month tier 2 is near-empty | none |

## closing_checklist

Written after both reveals: 2026-10-10 ~19:50Z UTC. **The difficulty is NOT closed, because not all four relationships PASS.**

| item | status |
|---|---|
| per-task files 1:1 with tasks; `_difficulty.md` alongside; first revision | done (`0.md`, `1.md`) |
| every comparison section PASS | **no**: task 0 is SOURCE-POLICY RED + SOURCE-FACTOR RED; task 1 is SOURCE-FACTOR RED |
| extended policies fully covered; scopes disjoint | yes. Task 0 charter_scope = {late_fee_schedule, returned_payment_fee, returned_payment_replacement}; task 1 = {good_standing_payment, increase_limit_correction, retention_concession}. Disjoint, and together all 6. Tool sets are disjoint and the 6 uuid8s are independent. |
| trees: 1–3 prerequisite problems, enough value_input edges, a user-owned problem, acyclic | yes, both tasks (task 0: 2 problems / 2 value_input / user root; task 1: 2 problems / 1 value_input / user good-standing). The difficulty-wide graph is a DAG. |
| factors: self-sufficient baselines, 4–6 real factors (2 param, 1 method), ladders real, all bearing weight | **no**: F-2 (returned fee: 3 real factors; no near-miss), F-3 (concession method ladder unreal), F-4 (concession baseline not self-sufficient). F-5 is latent on other classes. Every declared factor does bear weight on its task's world (all substitutions differ from gold; figures equal GT). |
| prerequisite conditions consistent with sentences and resolvable | **no**: F-1 (condition of the returned-fee edge) |
| instantiation gates re-run on the final form | not re-run by this auditor. The coordinator's snapshot (all OK) applies to the frozen hashes above. |

## revision_2

### charter_global_frozen (revision_2)

- Re-audit round 2. Frozen 2026-10-10, before either round-2 task JSON was opened.
- Hashes (recomputed; they match the coordinator's brief):

| input | round 1 | round 2 | status |
|---|---|---|---|
| `unit.extended.yaml` | `8e2f60bf…69e382` | `19b2b9c5c071a57abe7776e43f760f57c205ea1908a7241509c1c95ee1c085cb` | **changed** |
| `task_tools.py` | `9c6399f7…0b39ae` | same | unchanged |
| `0.view.json` | | `1189b7b4…cac9f55` | changed |
| `1.view.json` | | `496ad79f…4e36e` | unchanged |

- Because the extended charter changed, every charter-global section is **re-derived in full** below. The tool-contract half of `action_binding_and_uuids` is carried forward on the unchanged `task_tools.py` hash.
- The base copy (lines 1–1693) is still byte-identical to `blueprint/products/unit.yaml`.
- **contamination_disclosure:** the auditor read the round-1 GT of both tasks during round 1. Round-1 expected values are therefore known to the auditor: 20.73, 19.51, 302.59, 340.42, 225.55 and 216.81. The round-2 derivations below are recomputations of the changed charter on the masked views. Any figure that coincides with a round-1 value is coincident because the relevant charter text and world did not change, which is shown per figure. No round-2 GT has been read.
- Masked as in round 1. No recursive search over `tasks/`.

### Changes found in the extended charter (auditor's own reading, not the reworker's list)

- **late_fee_schedule.** The lateness percentage ladder is now: three or more late fees → the class percentage + 10 points; one or two → + 5 points; none → the class percentage. Params `pct_add_*` replace the absolute 25% and 20%. Rule, basis, compute and ladder were updated consistently.
- **returned_payment_fee.**
  - The return-reason factor (closed-account +5 / chargeback 0) is removed.
  - "A card chargeback carries no returned-payment fee at all." remains as a plain scope sentence.
  - A new `returned_fee_tenancy_share` factor is added: 48+ months → 0.8; 24–47 → 0.9; younger → 1, "counted … from the agreement's move-in date …, whatever unit the agreement has since been moved to".
  - The order sentence and `overwrite.replaced_by` were rewritten to match: limit → × tenancy share × AutoPay share → one rounding.
- **returned_payment_replacement.** The edge condition now reads: "Every unit_payment entry on the agreement that a unit_payment_reversal with reversal reason … points at is itself pointed at by a returned_payment_fee entry". Nothing else changed.
- **good_standing_payment.** The rule adds: "A payment that replaces a payment the bank returned is not a good-standing payment, even where the return has left the agreement delinquent: it is priced as the replacement of that returned payment." Compute is unchanged.
- **increase_limit_correction.** The tenure maximum is now relative: 84+ months → the class's largest single increase − 4 points; 48–83 months → − 2 points; younger → the class maximum. Params `tenure_cut_*` replace the absolute 8% and 10%.
- **retention_concession.**
  - The band rates are now "the share plus 20 percentage points" for the steep tier and "plus 10" for the moderate tier, each "never more than the whole of that part". Compute uses `MN(1, share + extra)`, with params `steep_extra` and `moderate_extra`.
  - The baseline is now two sentences: the rent as it stands and the increase, then "The new rent is the increase's rent as it stands less a give-back of the class's retention share of the increase, rounded down to the cent." Both are verbatim in the rule.
  - The rule's old sentence "The give-back is the class's retention share of the increase." was replaced by the new baseline sentence.

### policy_conflict_scan (revision_2)

- The six policies, their subjects, target tools and trees are as in round 1.
- **O-1 (replacement vs good-standing overlap) is closed.** The good-standing rule now carries an explicit precedence: a payment replacing a bank-returned payment "is not a good-standing payment, even where the return has left the agreement delinquent". For a tenant with a returned payment and a delinquent agreement, only one payment policy now prices the payment. The sentence states no cross-problem order and names no tool or id.
- No other overlap was introduced.

### rule_compute_equivalence (revision_2)

The full sweep was re-run. For every policy, compute keys equal compute_basis keys, and every basis quotation is a verbatim fragment of its own rule (checked programmatically). Spot checks on the changed bindings:

- **late_fee_pct:** `P(pct) + K(add_3)` / `P(pct) + K(add_1)` / `P(pct)` matches "plus 10 percentage points … plus 5 points … the class's late-fee percentage".
- **fee_months_in_force:** `MONTHS(F('move_in_date'), NOW)` matches "counted … from the agreement's move-in date". It ignores `unit_transfers`, as the rule demands.
- **Returned fee result:** `RND(limited_fee × fee_tenancy_share × autopay_share, 2)` matches the order sentence.
- **tenure_maximum:** `P(max) − K(cut_long)` / `P(max) − K(cut_mid)` / `P(max)` matches the rule.
- **give_back_raw:** `share × first_band + MN(1, share + extra) × (increase − first_band)` matches "the share plus 20 [10] percentage points, never more than the whole of that part".

No gap was found.

### action_binding_and_uuids (revision_2)

- Carried forward from round 1 on the unchanged `task_tools.py` hash `9c6399f7…0b39ae`: tool bodies, docstrings, uuid8s, no prerequisite judged by tools, and O-3.
- The `(target_tool, computes)` claims are unchanged (one policy per tool).

### prerequisite_graph (revision_2)

- The same four edges, all state form, all `policy_source` verbatim in the blocked rule (rechecked programmatically), acyclic, `resolved_by` = the depended-on target_tool.
- **F-1 is closed.** The returned-fee edge's condition is now stated over the returned **payment** entries ("Every unit_payment entry … that a unit_payment_reversal … points at is itself pointed at by a returned_payment_fee entry"). That is the object the policy_source names, the object the tool's `reference_entry_id` carries, and the object the schema's `reference_entry_id` meaning describes. `resolved_by` (a fee with reference_entry_id = the returned payment) now makes it hold.
- The other three conditions are unchanged and consistent.

### prerequisite_sentences (revision_2)

- The four sentences are unchanged. The four-point test, single resolving write and single reading hold as in round 1.
- The new good-standing sentence is not a prerequisite sentence. It is a scope precedence with no ordering connective that joins this policy's result to another write. It grounds no edge and states no undeclared order.
- O-4 is unchanged. Task 1's world has no returned payment.

### override_declarations (revision_2)

- **late_fee_schedule:** the amount sentence remains declared, and the new percentage ladder sits inside the declared clause.
- **returned_payment_fee:** the overwrite's `replaced_by` was rewritten to the new order sentence. The superseded base sentence is unchanged.
  - The base clause "a card chargeback is reversed without that fee" is now restated in the rule as a scope sentence, which is compatible.
  - Base "returned_payment_fee_usd is posted" is replaced as declared.
- **increase_limit, concession:** declared clauses as in round 1. The concession's changed band rates sit inside the declared give-back clause.
- **good_standing:** `overwrite: []`. The new precedence sentence contradicts no base sentence. Base redemption ("When a payment brings the balance due to zero or below on a delinquent … rental, the rental is redeemed") governs status, not which policy prices the payment.

**No undeclared override.**

### factor_ladders (revision_2)

| policy | factors (param / method) | cross_difficulty | change vs round 1 |
|---|---|---|---|
| late fee | 6 (4 / 2) | protect | lateness ladder now relative |
| returned fee | 4 (3 / 1): level, amount_limit (method), tenancy_share, autopay_share | autopay | return_reason removed, tenancy added |
| replacement | 4 (3 / 1) | — | none |
| good-standing | 5 (4 / 1) | autopay | none |
| increase limit | 6 (5 / 1) | prepay | tenure ladder now relative |
| concession | 6 (5 / 1) | autopay, parking | band rates now additive, capped at 1 |

Every ladder has 3 tiers. Every fall-through equals the factor's baseline. All binding sets are disjoint.

- **F-2 is closed.** The chargeback tier is gone from the factor set (it remains only as a scope sentence). The new tenancy ladder has three tiers (0.8 / 0.9 / 1), and each is occupied by real tenants reaching the write. The returned-fee computation has 4 factors, with 3 parameter and 1 method.
- **F-3 is closed.**
  - The moderate band rate is min(1, share + 0.10) and the steep band rate is min(1, share + 0.20). Neither can exceed 100% of its band.
  - The first band is at the share (≤ 0.83 < 1), so the give-back is at most the increase and the concession can never set the rent below the pre-increase rent.
  - The ladder's tiers are distinct (band at share + 20 / + 10 / no band), they are a progressive give-back an operator could publish, and the method label is honest.
- **F-4 is closed.**
  - baseline.rule is now: "The increase's rent as it stands is the new rent of the reduction notice pointing at the increase where one is on file, and otherwise the increase's own new rent; the increase is that rent less the rent before the increase. The new rent is the increase's rent as it stands less a give-back of the class's retention share of the increase, rounded down to the cent."
  - It names the scored quantity, defines the increase and gives the rounding, so it is self-sufficient. Both sentences are verbatim in the rule, and `params: [retention_concession_pct_of_increase]`.
- **F-5 is closed.** The lateness tiers are now class percentage + 10 points, + 5 points, and the class percentage. They are distinct for every class.
- **O-6 is closed.** The tenure maximum is now monotone (class max − 4 < class max − 2 < class max) for every class.
- **New finding N-1 (SOURCE-FACTOR RED, latent; bears on no task in this bundle; introduced by the O-6 rework).** With the tenure maximum now relative, the increase-limit percentage can go **negative**.
  - The percentage is the tenure maximum less up to 2 + 1 + 1 + 2.5 = 6.5 points of reductions, and the rule sets no floor.
  - Premier Climate Suite (class max 9%): 84+ months gives 5 − 6.5 = **−1.5%**.
  - Wine & Collectibles Vault (7%): 84+ months gives 3 − 6.5 = **−3.5%**, and 48–83 months gives 5 − 6.5 = **−1.5%**.
  - The tenant who reaches these values is the model tenant: two increases taken in 24 months, a prepaid plan completed within 36 months, no lien step, no late fee.
  - Then `allowed_increase` < 0, the limit rent is below the contracted rent, and the "reduction notice" (change reason increase_rescinded) sets a new rent **below the rent before the increase**. The rule's "cut back to the limit" becomes a rent cut.
  - No operator publishes an increase cap that mandates cutting an existing tenant's rent. In round 1 the minimum was +0.5% (Vault, younger), so this is a regression of the rework.
  - Both bundle tasks are on other classes (task 1 is Climate Controlled, with a minimum of +1.5%), so no scored value here is affected.
- Observation O-5 stands (the "acting base" method labels), and O-7 stands.

### findings (revision_2)

| id | round-1 class | round-2 status |
|---|---|---|
| F-1 | SOURCE-POLICY RED | **closed** (condition now over returned payments) |
| F-2 | SOURCE-FACTOR RED | **closed** (chargeback tier removed; tenancy factor added; near-miss judged per task in `0.md`) |
| F-3 | SOURCE-FACTOR RED | **closed** (band rates capped at 100%; give-back ≤ increase) |
| F-4 | SOURCE-FACTOR RED | **closed** (self-sufficient baseline) |
| F-5 | SOURCE-FACTOR RED (latent) | **closed** |
| O-1 | observation | **closed** (precedence sentence) |
| O-6 | observation | **closed** (monotone), but see N-1 |
| O-2, O-3, O-4, O-5, O-7 | observation | unchanged, as the reworker stated |
| **N-1** | — | **new SOURCE-FACTOR RED (latent, no task in bundle)**: increase-limit percentage can go negative for Premier and Vault after the relative-tenure rework |

## closing_checklist (revision_2)

Written after both round-2 reveals (2026-10-10 ~21:00Z UTC).

| item | status |
|---|---|
| per-task files 1:1, revision_2 appended, round-1 text untouched | done |
| every comparison PASS | **yes**: task 0 PASS, task 1 PASS (revision_2) |
| policies fully covered, scopes disjoint, tool uuid8s independent | yes (unchanged) |
| trees: 2 prerequisite problems each, value_input floor met, user-owned problem, DAG | yes |
| factors: 4–6 per computation, ≥ 2 param / ≥ 1 method, multi-source and cross-difficulty per task, real ladders, self-sufficient baselines, all bearing weight, near-miss per computation | yes for both tasks' worlds |
| charter-global REDs | F-1 to F-5 closed. **N-1 open (new, latent): the increase-limit percentage can go negative for Premier Climate Suite (84+ months) and Wine & Collectibles Vault (48+ months) after the relative-tenure rework.** No task in this bundle can reach it. |
| instantiation gates on the final form | the coordinator's round-2 snapshot (all OK) covers hashes `19b2b9c5…` and `9c6399f7…`. Not re-run by the auditor. |

**Difficulty status:** both tasks PASS the source-layer audit on their worlds. The charter carries one latent SOURCE-FACTOR RED (N-1) that no task here exercises. It is a defect of the shared extended charter and is reported for the coordinator's disposition.

## revision_3

### charter_global_frozen (revision_3)

- Re-audit round 3. Frozen 2026-10-10 ~21:36Z UTC, before either round-3 task JSON was opened.
- Hashes (recomputed; they match the brief):

| input | round 3 hash | status |
|---|---|---|
| `unit.extended.yaml` | `7b5319b45aa84c742670c7d6d9607f677eb185b60629a2e4fdc4288af2ddf4a0` | **changed** |
| `task_tools.py` | `9c6399f7…0b39ae` | unchanged |
| `0.view.json` | `4393eead…333ebf7` | changed |
| `1.view.json` | `496ad79f…4e36e` | unchanged |

- The base copy is still byte-identical to `blueprint/products/unit.yaml`.
- **contamination_disclosure:** round-1 and round-2 GT of both tasks were read in earlier rounds. Round-3 figures are recomputations; no round-3 GT has been read.
- **How the change was located.** Policies 3–6 were dumped structurally and diffed against the round-2 dump (`/tmp/run_0051/audit_storage_unit_account_servicing/r3_p36.txt` vs the round-2 output). Policies 1–2 were compared field by field with the round-2 printout.
- **The only charter change** is in `unit_ext_increase_limit_correction`:
  - The order sentence, which appears both in `rule` and in `overwrite.replaced_by`, now reads "… less the recent-increase, prepaid-plan, lien-record and lateness reductions, **never less than zero, so that a reduction never sets the rent below the rent before the increase**, then …".
  - New param `limit_pct_floor: 0.0`.
  - `limit_pct` is now `MX(K('limit_pct_floor'), tenure_maximum − …)`.
  - The `compute_basis` for `limit_pct` quotes the new clause verbatim from the rule.
- Everything else in the six policies is identical to round 2, including every prerequisite, factor, ladder and baseline. `rule_compute_equivalence`, `prerequisite_graph` and `prerequisite_sentences` were re-run programmatically and are unchanged: compute keys equal basis keys, every basis quotation is in its rule, and every policy_source is verbatim. The round-2 conclusions on `policy_conflict_scan`, `action_binding_and_uuids`, `prerequisite_graph`, `prerequisite_sentences`, `override_declarations` and `factor_ladders` are therefore carried forward, apart from the item below.

### N-1 re-checked

- **Closed.** The minimum limit percentage per class, by tenure tier (84+ / 48–83 / younger), with every reduction maximal and then floored:

| class | 84+ months | 48–83 months | younger |
|---|---|---|---|
| Drive-Up Standard | 4.5% | 6.5% | 8.5% |
| Interior Standard | 4.5% | 6.5% | 8.5% |
| Climate Controlled | 1.5% | 3.5% | 5.5% |
| Climate Plus | 1.5% | 3.5% | 5.5% |
| Premier Climate Suite | **0** | 0.5% | 2.5% |
| Wine & Collectibles Vault | **0** | **0** | 0.5% |

- At a 0% limit, the limit rent equals the contracted rent, which is the rent before the increase. The reduction notice then rescinds the increase in full and never sets a rent below the pre-increase rent. That is a treatment an operator can publish.
- The floor is declared in the overwrite's `replaced_by` and stated in the rule. Compute and basis agree.
- **No new defect.** The clamp is a floor on a composed quantity, not a new factor tier. On worlds where it binds, the reduction factors stop moving the value, but whether a factor bears weight is judged per task world, and neither task here is near the floor (task 1's limit is 6%).

### Status after round 3

| item | status |
|---|---|
| F-1 to F-5 | closed in round 2, still closed (text unchanged) |
| N-1 | **closed** |
| O-1, O-6 | closed in round 2, still closed |
| O-8, O-9 | per task: see `0.md` revision_3 |
| O-2, O-3, O-4, O-5, O-7 | unchanged observations |
| New defects | none found |

## closing_checklist (revision_3)

Written after both round-3 reveals (2026-10-10 ~21:38Z UTC).

| item | status |
|---|---|
| per-task files 1:1, revisions 1–3 appended, earlier text untouched apart from the disclosed timestamp corrections | done |
| every comparison PASS | **yes**: task 0 PASS, task 1 PASS |
| policies fully covered, scopes disjoint, uuid8s independent | yes |
| trees: 1–3 prerequisite problems, enough value_input edges, user-owned problem, DAG difficulty-wide | yes |
| factors: 4–6 per computation (≥ 2 param, ≥ 1 method), multi-source and cross-difficulty per task, real ladders, self-sufficient baselines, all bearing weight, near-miss per computation | yes |
| charter-global REDs | none open. F-1 to F-5 and N-1 are closed. O-2, O-3, O-4, O-5 and O-7 remain as observations. |
| instantiation gates on the final form | the coordinator's round-3 snapshot (all OK) covers `7b5319b4…` and `9c6399f7…`. Not re-run by the auditor. |

**The difficulty passes the source-layer audit.**
