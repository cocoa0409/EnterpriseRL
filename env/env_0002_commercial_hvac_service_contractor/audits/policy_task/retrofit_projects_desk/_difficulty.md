# Policy-task audit — retrofit_projects_desk / charter-global

## charter_global_frozen

- Auditor: independent source-layer auditor (did not write these artifacts; edits nothing).
- Freeze time (charter-global section): 2026-09-17, written in full **before any task's GT was revealed**.
- Freeze hashes (sha256, verified by the auditor against disk, and equal to the hashes supplied with the brief):
  - `env/env_0002_commercial_hvac_service_contractor/tasks/retrofit_projects_desk/retrofit.extended.yaml`
    `1f9ff70230bb2aa99122b085ac8d543df26cb5a3954a4c4cf0c6257ac7135e31`
  - `env/env_0002_commercial_hvac_service_contractor/tasks/retrofit_projects_desk/task_tools.py`
    `101ac47c75e9a373c374d392aad60e112a9f8bae5e25ebbb6ccfa2cf9d248149`
  - masked task views `0.masked.json` `18d18c3ebdc49d6ba3c2d32ef5fb32a36519d11b26ab2091a6a993b29f9aaf61`,
    `1.masked.json` `669137a19e24c0caef9642ad4d4ca453de9585220ca4b72ba65b9fc3bba5fbf2`
- Fields permitted while this section was written: `blueprint/blueprint.yaml` (the `retrofit_projects_desk`
  difficulty entry), `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/*.yaml`
  (this scenario only — for the cross-category variant parameters the charter reads), the whole of
  `retrofit.extended.yaml`, the whole of `task_tools.py`, and the masked task views
  (`frozen_time`, `user_scenario`, `initial_state` only).
- Fields explicitly masked and not read while this section was written: `evaluation_criteria`,
  `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`,
  `prerequisite_closure`, `db_closure`, `db_closure_matches_initial_state`.
- Entry conditions (Step 0): the M=2 claim block and summary were read verbatim from
  `blueprint/blueprint.yaml` under `difficulties[name=retrofit_projects_desk]`; the gate snapshot
  (`check_extended.py`, `check_task_tools.py`, `replay_tasks.py`, `check_solvability.py`,
  `check_compute.py`, `check_grounding.py`, `check_cross_fire.py`, all green; `check_traceability.py`
  deliberately deferred to the render step) was supplied with the brief and is cited, not re-run.
  The masked views were constructed by the coordinator with the division this skill requires, and
  their hashes match. **Entry conditions complete — no "incomplete input" finding.**
  A green gate is the qualification to enter this audit, not a proof of correctness.

### policy_conflict_scan

Scope of the scan: the 10 base policies copied into `retrofit.extended.yaml` plus the 6
`extended_policies`, over overlapping subjects, triggers, eligibility, time anchors, action
parameters, terminal states and cross-category read boundaries.

- **Base copy is verbatim.** Every top-level key of `blueprint/products/retrofit.yaml`
  (`category`, `display_name`, `binding`, `lifecycle`, `accounts`, `parameter_schema`, `variants`,
  `events`, `measures`, `policies`) is byte-for-byte identical in the extended file; the only added
  key is `extended_policies`. No base sentence has been rewritten.
- **Subjects / triggers.** The six extended policies carry disjoint `computes` and disjoint
  `target_tool`s: `storage_amount_usd`/`bill_storage_charge_e8c4e90e`,
  `settlement_amount_usd`/`settle_project_cancellation_6d1f2e6f`,
  `damages_credit_usd`/`credit_liquidated_damages_732a84c1`,
  `retainage_release_usd`/`release_project_retainage_a81bb865`,
  `late_fee_amount_usd`/`bill_overdue_late_fee_5c3179f3`,
  `payment_amount_usd`/`pay_project_balance_ec87bb4f`. Three policies share the subject
  `retrofit_progress_billed` (storage, late fee, and — through `billing_class` — the cancellation
  settlement line), but each computes a different quantity onto a different `billing_class`, so no
  two policies contend for one figure.
- **Eligibility / time anchors.** The base gates that bear on these six writes
  (`retainage_release_after_completion`, `completion_past_guaranteed_date`,
  `deposit_received_before_release`) are inherited; none is contradicted by an extended `rule`.
  Every extended policy anchors its clock on `frozen_time` (`NOW`) plus record dates on the project.
- **Cross-category read boundaries.** Declared reads are `maintenance.status`,
  `maintenance.balance_due`, `maintenance.signed_date`, `energy.status`,
  `energy.savings_guarantee_included`, `service.status`, `service.critical_response_hours`,
  `service.balance_due`. Each is read through `CFIELD`/`CPARAM`/`EXISTS` only — no write, no
  aggregate over another category's ledger — and each matches the `cross_category` block of the
  policy that performs it. No extended policy reads a category it does not declare.
- **Terminal states.** Only `settle_project_cancellation_6d1f2e6f` moves `retrofit_projects.status`
  (to `cancelled`); the other five leave `status` alone and move only money fields. No two policies
  drive the same status transition.
- **Task scopes.** Task 0 claims {`retrofit_ext_storage_accrual_billing`,
  `retrofit_ext_cancellation_settlement`}; task 1 claims {`retrofit_ext_liquidated_damages_credit`,
  `retrofit_ext_retainage_release`, `retrofit_ext_overdue_invoice_late_fee`,
  `retrofit_ext_closeout_balance_payment`} — each scope spanning the whole problem tree, root and
  prerequisite problems. Pairwise disjoint and jointly exhaustive over the six extended policies.
- **Result: no cross-policy conflict found.** The one policy-level defect this audit does find is an
  undeclared override inside a single policy (see `override_declarations`, finding F1).

### rule_compute_equivalence

Check 2, run over all six extended policies in both directions.

- Forward (`compute` -> `compute_basis` -> `rule`): every binding of every `compute` list carries a
  `compute_basis` entry except four pure field/sum re-reads that introduce no basis of their own —
  `booked_start = F('scheduled_start_date')` and `mobilised_on = F('mobilization_date')`
  (storage / liquidated damages), `contract_billed` (late fee) and `billed_all` (closeout balance),
  each a restatement of bindings already carrying a basis. Every other `compute_basis` value was
  matched, case-insensitively and whitespace-normalised, against the policy's own `rule` and found
  verbatim there.
- Backward (`rule` -> `compute`): every quantity, window, filter, tier, branch, cross-category read,
  acting base, grouping, cap/floor, rounding mode and interval-counting convention stated in each
  `rule` is implemented by a restricted expression. Rounding is uniformly `RND(..., 2)` at the point
  the rule names; the whole-weeks-begun convention (`int((DAYS+6)/7)`), the part-month convention
  (`int((d+29)/30)`), the day-count conventions ("the mobilisation day excluded and the final day
  included" = `DAYS(anchor, end)`) and the caps (`MN(raw, ceiling)`, `MX(0, ...)`) all correspond.
- Every `factors[].ladder` tier is stated in its policy's `rule` (condition and outcome) and is a
  branch of the named `decides` binding; no tier lives only in `compute`, and no branch of a
  `decides` binding is missing from the rule. The ladder wordings in `factors` are paraphrases of the
  rule sentences (e.g. "the owner's changes" for "changes the owner asked for"); the semantics
  match tier for tier.
- **Three places where the rule and the compute do not fully meet (all three unexercised by either
  task world, so recorded as observations, not red lights):** see findings O1, O2, O3.

### action_binding_and_uuids

Check 3 over the whole charter and the one tool module.

- Each `(target_tool, computes)` pair is claimed by exactly one policy (table above). No policy
  names a tool another policy also targets.
- Each policy's subject, `base_policy_refs`, target tool, tool docstring and terminal state admit one
  business reading; no confirmation, review, wait or procedure outside the policy is added by a
  docstring.
- No docstring names another tool, and none states a position in a sequence. The word "Afterwards"
  appears in five docstrings, but always about the post-state of that same call ("Afterwards the
  owner sees a storage charge on the project statement"), never about an order between actions.
- uuid8s: `e8c4e90e`, `6d1f2e6f`, `732a84c1`, `a81bb865`, `5c3179f3`, `ec87bb4f`. Six distinct
  values, no shared prefix, no shared tail, no arithmetic or alphabetical progression, none derivable
  from another. Each is frozen with its tool. PASS.

### prerequisite_graph

Check 7 over the whole `prerequisite` graph of the difficulty.

- `prerequisite` is present on all six policies (`[]` on storage, liquidated damages and late fee).
- Edges (4 in total), all `kind: value_input`, all `form: state`, no `fallback_reason` present and
  none required:
  1. `retrofit_ext_cancellation_settlement` <- `retrofit_ext_storage_accrual_billing`,
     gate `billings_raised`, `resolved_by: bill_storage_charge_e8c4e90e`.
  2. `retrofit_ext_retainage_release` <- `retrofit_ext_liquidated_damages_credit`,
     gate `credits_on_project`, `resolved_by: credit_liquidated_damages_732a84c1`.
  3. `retrofit_ext_closeout_balance_payment` <- `retrofit_ext_retainage_release`,
     gate `retainage_released_total`, `resolved_by: release_project_retainage_a81bb865`.
  4. `retrofit_ext_closeout_balance_payment` <- `retrofit_ext_overdue_invoice_late_fee`,
     gate `late_fees_total`, `resolved_by: bill_overdue_late_fee_5c3179f3`.
- Every `problem` points at another extended policy id in this file; none points at a base policy or
  at itself. The graph `{storage -> cancellation}`, `{LD -> retainage -> closeout}`,
  `{late fee -> closeout}` is a DAG; no cycle, and no cycle is created across the two tasks either
  (the two components are disjoint).
- Every `gate` names a binding that genuinely exists in the blocked policy's `compute`:
  `billings_raised` (cancellation), `credits_on_project` (retainage release),
  `retainage_released_total` and `late_fees_total` (closeout balance). `kind: value_input` matches in
  all four cases — each gate is a binding feeding the arithmetic, not an eligibility flag.
- Every `resolved_by` is the depended-on policy's own `target_tool`, and each genuinely changes the
  named binding: `bill_storage_charge_e8c4e90e` writes `billing_class="storage"` which
  `billings_raised` sums; `credit_liquidated_damages_732a84c1` writes
  `event_type="retrofit_credit_issued"` which `credits_on_project` sums;
  `release_project_retainage_a81bb865` writes `event_type="retrofit_retainage_released"` which
  `retainage_released_total` sums; `bill_overdue_late_fee_5c3179f3` writes
  `billing_class="late_fee"` which `late_fees_total` sums (task_tools.py, the `ctx.create` call in
  each function body).
- No `condition` is strengthened or weakened relative to its `policy_source`; each restates the same
  record-visible state in the same scope. No authoring-viewpoint phrasing ("in this task", "at the
  opening", "the current world") appears anywhere in the four `prerequisite` blocks.
- PASS.

### prerequisite_sentences

Check 6, four-point test on each of the four edges.

| # | `policy_source` (verbatim from the blocked policy's own `rule`) | connective | waited-on | tokens | scope |
|---|---|---|---|---|---|
| 1 | "The settlement figure on a stopped project is worked out only once every week the delivered equipment has stood in storage is carried as a storage charge on the project's billing record." | "only once" | state: a storage charge standing on the project's billing record | none | exact |
| 2 | "The retainage released on a project is worked out only after every day of delay past the day substantial completion was guaranteed by stands credited on the project's account." | "only after" | state: a credit standing on the project's account | none | exact |
| 3 | "The amount an owner settles a project at is fixed only after the retainage held on the project stands released on its account." | "only after" | state: retainage standing released on the account | none | exact |
| 4 | "Before the amount to settle is worked out, every month the project's billings have stood past their due day must be carried as a late fee on the project's billing record." | "Before" | state: a late fee standing on the project's billing record | none | exact |

- All four are **state form**; none names a performer, an action, a tool, a policy id, a snake_case
  token or a row id. The state form has priority and is honoured throughout — there is no action-form
  edge in this charter, hence no `fallback_reason` to test.
- **One write per waited-on state.** Across the whole tool module exactly one function produces each
  state: a `billing_class="storage"` line only `bill_storage_charge_e8c4e90e`; a
  `retrofit_credit_issued` row only `credit_liquidated_damages_732a84c1`; a
  `retrofit_retainage_released` row only `release_project_retainage_a81bb865`; a
  `billing_class="late_fee"` line only `bill_overdue_late_fee_5c3179f3`. No second candidate exists,
  so each hop resolves in one reading.
- **Written derivation, edge 1.** The cancellation rule says the settlement is worked out *only once*
  every week in storage is carried as a storage charge on the billing record. The records show weeks
  in storage and no storage line on the billing record. Reading the other policies' own rules, the
  only one whose result is a storage charge raised on equipment the building cannot yet receive is
  `retrofit_ext_storage_accrual_billing`; its rule computes exactly that charge. Hence: raise the
  storage charge, then settle. One reading. Edges 2, 3 and 4 derive the same way — the waited-on
  state is a credit for days of delay (only the liquidated-damages rule produces one), retainage
  standing released (only the retainage-release rule), and a late fee for months past due (only the
  overdue-late-fee rule).
- **Nothing else about the dependency is written.** No rule carries a second wording of its own edge,
  a tool name, or another policy's id; a regex sweep of all six `rule` texts for the tool names, the
  policy ids and snake_case tokens returns nothing. The depended-on policy's rule never restates the
  sentence (the storage rule is silent about settlement; the damages rule about retainage; the
  retainage and late-fee rules about the settled amount).
- **No undeclared cross-problem order in an extended rule.** A sweep of every sentence of all six
  `rule` texts for ordering connectives returns, besides the four sentences above, only
  within-computation ordering ("the equipment arrived before the day installation was booked to
  begin", "cleared on or before the day it fell due", "signed before the project was awarded", …) —
  each a tier condition of a declared factor, grounding no cross-problem hop.
- **Base rules that state a cross-problem order**: `retrofit_progress_billing_and_retainage`
  ("Retainage is released within the tier's release period … provided the punch list is cleared and
  the closeout documents are delivered.") and `retrofit_completion_and_closeout` ("The project closes
  when the punch list is clear, the documents are delivered and the retainage is released."). No
  task's tree rests on either — every edge above is grounded in an *extended* rule sentence — so per
  check 6 these are recorded as an observation (O4), not a red light.
- PASS.

### override_declarations

Check 1's finding half, run once over all six extended policies, sentence by sentence against each
`base_policy_refs` entry. Criterion: the quantity that ultimately gets scored.

| extended policy | base sentences that govern the scored quantity | declared in `overwrite`? |
|---|---|---|
| `retrofit_ext_storage_accrual_billing` | `retrofit_scheduling_and_delivery`: "Equipment delivered before the site can receive it is stored, and storage beyond the week of delivery carries the tier's weekly storage charge, counted per whole week begun." — the single base sentence fixing the storage rate *and* the week count; the yard/rack premium, the lot scaling, the clock anchor and the free period all deviate from within it. `retrofit_progress_billing_and_retainage`: nothing about storage (its retainage clause expressly excludes stored equipment, which extended honours). | **Yes** — named and replaced. |
| `retrofit_ext_cancellation_settlement` | `retrofit_cancellation_and_settlement` s1 (awarded-stage fee), s2 (scheduled-stage fee + restocking pass-through), s3 (in-progress fee + retainage released against the settlement) — all three deviated from by `stopped_stage_basis`, `notice_lead_relief`, `equipment_share_of_value`, `restocking_return_window` and `late_fee_settlement_treatment`. | **Yes** — all three named and replaced. |
| `retrofit_ext_cancellation_settlement` | `retrofit_cancellation_and_settlement` s5: "Deposits are applied to the settlement and refunded only where the settlement is smaller than the deposit." Extended's `result = RND(MX(0, …), 2)` can never produce a refund. | **No** — a dropped branch; see observation O5 (no task world exercises it). |
| `retrofit_ext_liquidated_damages_credit` | `retrofit_schedule_guarantee` s0 (the guaranteed period and its extension by change-order impact days). | **Yes** — named and replaced. |
| `retrofit_ext_liquidated_damages_credit` | `retrofit_schedule_guarantee` s1: "Liquidated damages are credited at **the tier's daily amount** for **each calendar day of delay past that date**, capped at the tier's portion of the contract value, and they are the owner's whole remedy for lateness." Extended deviates on both halves — `performance_daily_amount` and `critical_response_addition` credit the class's daily amount *plus* additions, and `closeout_grace_allowance` and `arrears_guarantee_suspension` withhold days from "each calendar day of delay past that date". | **No** — finding **F1**, `SOURCE-POLICY RED`. |
| `retrofit_ext_retainage_release` | `retrofit_progress_billing_and_retainage`: "The tier's retainage is withheld from every progress and change order billing, not from the deposit or from stored equipment, and it is held until closeout." — the sentence `withholding_rate_check` and `unpaid_work_retention` deviate from. | **Yes** — named and replaced. The base release clause ("Retainage is released within the tier's release period … provided the punch list is cleared and the closeout documents are delivered") fixes a timing and a proviso, not an amount, and the extended `baseline` ("The whole of the retainage held is releasable. The share released is the whole of the releasable retainage.") is exactly what it implies, so the inspection-share and credit-offset factors refine a quantity base leaves open rather than contradicting it. No finding. |
| `retrofit_ext_overdue_invoice_late_fee` | `retrofit_progress_billing_and_retainage`: "Each invoice falls due the tier's payment term after the invoice date … and an invoice unpaid past its due day carries the tier's late fee for each month or part month it stays unpaid." — the one base sentence fixing the late fee's rate, its base and its month count; the fee base scope, the clock anchor, the month count, the rate share, the surcharge and the ceiling all deviate from within it. | **Yes** — named and replaced. |
| `retrofit_ext_closeout_balance_payment` | `retrofit_progress_billing_and_retainage`: "Payments are applied to the oldest unpaid project invoice unless the owner names one." | **Yes** — named and replaced. Its other clauses (retainage withheld and held to closeout; the late fee on an overdue invoice) are honoured rather than contradicted: the extended rule takes the withheld retainage off the settled billings and decides only *how much of an already-raised late fee* is settled with the balance, not what the fee is. |

Every base provision not hit by an `overwrite` was walked sentence by sentence and found inherited
intact — eligibility (`signed_proposal_on_file`, `award_inside_estimate_validity`,
`owner_authorization_for_large_change`, `inspections_passed_before_completion`,
`retainage_release_after_completion`, `completion_past_guaranteed_date`), authoritative evidence
(`evidence_contract.authority: system_record`, `timing: pre_action` throughout), time anchors,
status/liability/dedup/channel boundaries. Neither an extended rule, nor a tool body, nor a persona
weakens any of them. No 0/1 multiplier and no anonymous intermediate was found other than the one in
F1; no author note calls a base output a "wrong value".

### factor_ladders

Charter-global structure only. Whether a factor bears weight is a fact about one world and lives in
that task's `factor_weight`.

| policy | factors | `parameter` | `method` | ladder tiers | multi-source tiers | `cross_difficulty` |
|---|---|---|---|---|---|---|
| storage accrual | `storage_clock_anchor`(m), `free_period_allowance`(p), `storage_rate_premium`(p), `lot_bay_scaling`(m) | 2 | 2 | 3 each | `free_period_allowance` (agreement standing × project late-fee history), `storage_clock_anchor` (arrival date × booked day × schedule request) | `maintenance` |
| cancellation settlement | `stopped_stage_basis`(m), `notice_lead_relief`(m), `equipment_share_of_value`(p), `restocking_return_window`(p), `late_fee_settlement_treatment`(m) | 2 | 3 | 3 each | `notice_lead_relief` (confirmed notice row × booked start date), `restocking_return_window` (stored delivery × arrival date) | none |
| liquidated damages | `guarantee_clock_anchor`(m), `change_impact_allocation`(m), `closeout_grace_allowance`(p), `arrears_guarantee_suspension`(p), `performance_daily_amount`(p), `critical_response_addition`(p) | 4 | 2 | 3 each | `guarantee_clock_anchor`, `closeout_grace_allowance` (walkthrough inspection × punch due date × closeout acceptance), `critical_response_addition` (program standing × guaranteed response) | `energy`, `service` |
| retainage release | `withholding_rate_check`(m), `unpaid_work_retention`(m), `inspection_release_share`(p), `credit_offset_on_release`(p) | 2 | 2 | 3 each | `withholding_rate_check` (withholding rows × progress billings), `credit_offset_on_release` (credit rows × unpaid contract billings × contract value), `inspection_release_share` (two inspection classes) | none |
| overdue late fee | `overdue_base_scope`(m), `overdue_clock_anchor`(m), `overdue_month_count`(m), `account_standing_rate`(p), `portfolio_arrears_surcharge`(p), `payment_silence_ceiling`(p) | 3 | 3 | 3 each | `overdue_clock_anchor` (payment rows × progress due dates), `account_standing_rate` (program standing × program balance × fee base vs contract value), `portfolio_arrears_surcharge` (agreement standing × agreement balance) | `service`, `maintenance` |
| closeout balance | `due_now_scope`(m), `released_retainage_settlement`(p), `credit_settlement_share`(p), `arrears_late_fee_settlement`(p), `portfolio_settlement_allowance`(p) | 4 | 1 | 3 each | `released_retainage_settlement` (release rows × class release period), `credit_settlement_share` (credit rows × release rows), `portfolio_settlement_allowance` (agreement standing × signing date vs award date) | `maintenance` |

- Counts: every policy declares 4–6 factors with at least 2 `parameter` and at least 1 `method`.
  Per task: task 0's policies carry a multi-source factor and one `cross_difficulty` factor
  (`free_period_allowance`, reading `maintenance`); task 1's carry several multi-source factors and
  four `cross_difficulty` factors reading `energy`, `service` and `maintenance`. Bounds met.
- `decides` is an input binding in every case, never `result`; every factor's `bindings` set is
  disjoint from every other factor's within its policy.
- Tier conditions are pairwise disjoint as stated, and every tier's outcome is drawn from the charter
  (a `P(...)` tier parameter, a `K(...)` policy constant, or a named record aggregate).
- **Labels.** Every `method` tier changes an algorithm (which date anchors a clock, which rows are
  summed, which aggregate is the base, whether a count is scaled) except one: see finding **F3**.
- **Distinct outcomes.** Every ladder was checked for two tiers selecting the same value or method
  over their own stated domains. Two fail: findings **F2** (`change_impact_allocation`) and
  **F4** (`overdue_month_count`).
- **Conditions and outcomes a contractor actually holds.** Every tier condition was read against what
  a commercial HVAC contractor genuinely weighs for that quantity — the standing of a maintenance
  agreement at the building, a written cancellation notice and how far ahead of the booked start it
  arrived, which equipment class is in storage and how many units, whether authority and commissioning
  inspections have been passed, how long the account has been silent, whether a remobilisation fee
  stands billed. None holds of every customer who reaches the write, and none restates the policy's
  scope. Every tier outcome, the fall-through's above all, is a treatment such a contractor would
  publish (a 1-week free storage period, the class's own restocking fee, the class's own daily
  liquidated-damages amount, the whole of the retainage held, no portfolio allowance). No straw-man
  default found.
- One authoring pattern worth recording but not a defect: in four ladders
  (`restocking_return_window`, `withholding_rate_check`, `unpaid_work_retention`,
  `credit_settlement_share`) the tier whose outcome equals the policy `baseline` is the **middle**
  tier, the last tier being the "nothing of that kind exists on the record" case which correctly
  yields nothing. The `baseline` in each is still exactly what `baseline.rule` states for that input,
  so the honest-baseline test passes.

### findings

---

**F1 — `SOURCE-POLICY RED` — undeclared override of the base liquidated-damages clause**
*(bears on task 1; the consequence is demonstrated in `1.md` against task 1's world and scored solution)*

- **Symptom.** `retrofit_ext_liquidated_damages_credit` computes the credited damages from a daily
  figure that is *not* the tier's daily amount and from a day count that is *not* every calendar day
  of delay past the guaranteed date, while the base sentence that fixes both is left standing,
  unnamed in `overwrite` and therefore inherited in full.
- **Root cause.** `overwrite` declares one superseded clause only — base sentence s0, the
  guaranteed-period sentence. Base sentence s1 of `retrofit_schedule_guarantee`, which fixes the
  *amount* formula, is not named, yet four of the policy's six factors deviate from it.
- **Evidence.**
  - Base, `policies[id=retrofit_schedule_guarantee].rule`, sentence 1 (verbatim):
    "Liquidated damages are credited at the tier's daily amount for each calendar day of delay past
    that date, capped at the tier's portion of the contract value, and they are the owner's whole
    remedy for lateness."
  - `extended_policies[id=retrofit_ext_liquidated_damages_credit].overwrite` — one entry only, whose
    `superseded_clause` is base sentence s0 ("Where the tier carries a schedule guarantee,
    substantial completion is guaranteed inside the tier's guaranteed period …"). s1 is nowhere named.
  - Extended `rule`, the daily amount: "Where an energy subscription covers the building and its
    class carries a guaranteed savings commitment, the daily amount is the daily amount the project's
    class carries together with the measured performance addition"; and "Where the owner carries an
    active demand service rate program whose guaranteed response at a critical facility is 4 hours or
    less, a further critical facility addition is made to the daily amount".
  - Extended `rule`, the days counted: "Where the punch list was cleared on or before the day it fell
    due and a confirmed closeout acceptance stands on the project record, 5 days of grace are allowed
    past the end of the guaranteed period before damages begin"; and "Where a remobilisation fee
    stands billed on the project … the guarantee is suspended for the number of days past due at
    which the project's class stops work".
  - `compute`: `raw_damages: RND(delay_days * (daily_amount + daily_addition), 2)` and
    `delay_days: MX(0, elapsed_days - P('schedule_guarantee_days') - extension_days - grace_days - suspension_days)`.
- **Demonstrated consequence.** Two passages of the merged policy reach different conclusions in the
  same situation. Worked on task 1's world in `1.md` (`policy_self_consistency`): following base s1
  as inherited gives a definite second answer of **37100.00** against the extended computation's
  **33750.00**. The task therefore carries a second defensible answer. Declaring an override makes an
  override legal; leaving s1 undeclared makes two answers legal.
- **Affected artifact and location.**
  `env/env_0002_commercial_hvac_service_contractor/tasks/retrofit_projects_desk/retrofit.extended.yaml`,
  `extended_policies[id=retrofit_ext_liquidated_damages_credit].overwrite` (the missing declaration),
  read against `policies[id=retrofit_schedule_guarantee].rule` sentence 1. It bears on task 1's
  scored `damages_credit_usd` and, through the prerequisite chain, on `retainage_release_usd` and
  `payment_amount_usd`.
- **Relation to previous revisions.** First revision; no prior audit of this difficulty exists.

---

**F2 — `SOURCE-FACTOR RED` — `change_impact_allocation`'s three tiers collapse to one outcome**
*(bears on task 1)*

- **Symptom.** The `change_impact_allocation` ladder is written as three tiers, but on every world
  all three select the same quantity: the sum of the impact days stated on owner-requested,
  concealed-condition and code-requirement change orders. No record can tell the tiers apart.
- **Root cause.** Tier 1's outcome is `owner_impact_days + supplier_impact_days` *under a condition
  that forces `supplier_impact_days == 0`*, so it equals tier 2's outcome `owner_impact_days`; and
  tier 3 fires only when `owner_impact_days == 0`, where `K('no_extension_days') = 0` equals
  `owner_impact_days` too. The ladder is the identity function `extension_days = owner_impact_days`.
- **Evidence.**
  - `compute`: `extension_days: (owner_impact_days + supplier_impact_days) if (owner_impact_days > 0 and supplier_impact_days == 0) else (owner_impact_days if (owner_impact_days > 0 and supplier_impact_days > 0) else K('no_extension_days'))`, with `params.no_extension_days: 0`.
  - Replacing that whole expression with the single expression `owner_impact_days` and replaying the
    computation over six seeded variations of the change-order impact days
    `(owner, supplier) ∈ {(12,9),(12,0),(0,9),(0,0),(5,5),(30,1)}` gives an identical
    `extension_days` and an identical scored result in every one.
- **Demonstrated consequence.** Two tiers of one ladder — in fact all three — select the same value.
  A three-tier ladder is claimed where the world can exhibit only one, so the factor's ladder tests
  nothing about the distinction it states (the supplier's days "not being the owner's to have" never
  changes an answer, because tier 1 can only fire when there are no supplier days to exclude).
- **Affected artifact and location.** `retrofit.extended.yaml`,
  `extended_policies[id=retrofit_ext_liquidated_damages_credit].factors[id=change_impact_allocation]`
  and the `extension_days` binding of that policy's `compute`; the corresponding three sentences of
  its `rule`.
- **Relation to previous revisions.** First revision.

---

**F3 — `SOURCE-FACTOR RED` — `stopped_stage_basis` is labelled `method` but only substitutes a rate**
*(bears on task 0)*

- **Symptom.** `stopped_stage_basis` carries `effect: method`, but its three tiers leave the formula
  untouched and select a different percentage to put into it.
- **Root cause.** The factor `decides: stage_pct`, a percentage; a factor that decides a percentage
  can only select a number, and its tiers do exactly that.
- **Evidence.**
  - `compute`: `stage_pct: P('cancellation_fee_pct_in_progress') if days_since_mobilization >= 0 else (P('cancellation_fee_pct_scheduled') if days_since_release >= 0 else P('cancellation_fee_pct_awarded'))` — three tier parameters, one binding.
  - The formula that consumes it is the same in all three tiers:
    `stage_fee: RND(F('contract_value_usd') * stage_pct / 100 * K(...), 2)`. Nothing about how the
    stage fee is computed changes between tiers; only the rate does (55 / 25 / 8 per cent on task 0's
    Energy Retrofit Project tier).
  - Contrast the policy's genuine `method` factors: `notice_lead_relief` scales the computed fee by a
    share, and `late_fee_settlement_treatment` changes which rows are aggregated into the settlement.
- **Demonstrated consequence.** A mislabelled effect: the label asserts the tier changes the
  algorithm, and the artifact shows it changes a number. The policy still satisfies the count bounds
  once relabelled (3 `parameter`, 2 `method`), so the consequence is confined to the false claim in
  `factors[].effect` rather than to the counts.
- **Affected artifact and location.** `retrofit.extended.yaml`,
  `extended_policies[id=retrofit_ext_cancellation_settlement].factors[id=stopped_stage_basis].effect`.
- **Relation to previous revisions.** First revision.

---

**F4 — `SOURCE-FACTOR RED` — `overdue_month_count` tiers 2 and 3 are indistinguishable**
*(bears on task 1)*

- **Symptom.** The middle tier of `overdue_month_count` ("more than 30 days but fewer than 60 … only
  the whole months completed count and a part month does not") returns exactly **1** at every point
  of its own stated domain, which is precisely what the third tier ("30 days or fewer … counted as
  one month") returns. The three-tier ladder has two distinguishable outcomes.
- **Root cause.** `int(overdue_days / 30)` equals 1 for every `overdue_days` in `(30, 60)`, so the
  "whole months completed" method and the "counted as one month" value coincide across the whole
  band the tier is written for.
- **Evidence.**
  - `compute`: `months_overdue: int((overdue_days + K('days_in_month') - 1) / K('days_in_month')) if overdue_days >= K('long_overdue_days') else (int(overdue_days / K('days_in_month')) if overdue_days > K('short_overdue_days') else K('one_month'))`, with `days_in_month: 30`, `long_overdue_days: 60`, `short_overdue_days: 30`, `one_month: 1`.
  - Enumerating the tiers' domains: tier 2 over `overdue_days ∈ [31, 59]` yields the value set `{1}`;
    tier 3 over `[0, 30]` yields `{1}`; tier 1 over `[60, 200]` yields `{2,…,7}`. There is no
    `overdue_days` for which tier 2 and tier 3 differ.
- **Demonstrated consequence.** Two tiers of one ladder select the same value, so one tier has been
  written as two and the ladder falls below the three-distinct-tier floor. An agent that never
  distinguishes "whole months completed" from "one month" is never wrong below 60 days.
- **Affected artifact and location.** `retrofit.extended.yaml`,
  `extended_policies[id=retrofit_ext_overdue_invoice_late_fee].factors[id=overdue_month_count]`, the
  `months_overdue` binding of its `compute`, and the corresponding sentence of its `rule`.
- **Relation to previous revisions.** First revision.

---

**O1 — observation — `overdue_clock_anchor` tier 3 promises no clock and the compute raises a fee anyway**

The rule says "where no progress billing has fallen due on the project, no overdue clock runs", but
`overdue_anchor: … else NOW` with `months_overdue` falling through to `K('one_month') = 1` yields
`raw_fee = fee_base * monthly_rate / 100 * 1`, a positive fee. The rule makes a promise the compute
does not keep. Neither task world reaches the tier (task 1's project carries three progress
billings; task 0 does not compute a late fee), so no consequence can be demonstrated and this is not
a red light. Location: `retrofit_ext_overdue_invoice_late_fee`, `compute.overdue_anchor` /
`compute.months_overdue` against the rule sentence quoted above.

**O2 — observation — two ladders are not exhaustive, and the compute fills the gap silently**

(a) `payment_silence_ceiling`: where no payment has *ever* been received,
`days_since_last_payment … if last_payment_on else 0` puts the customer on the 2 per cent ceiling,
although the rule's third tier is conditioned on "a payment has been received on the project within
the last 30 days", which is false. (b) `credit_offset_on_release`: where credits stand and nothing at
all is unpaid, no tier of the rule applies, and the compute falls through to
`K('no_credit_share')`. In both cases a reader cannot derive the tier from the rule. Task 1 sits
outside both gaps (payments exist; `unpaid_contract = 151950.00 > 0`), so no consequence is
demonstrable. Location: `retrofit_ext_overdue_invoice_late_fee.factors[payment_silence_ceiling]`,
`retrofit_ext_retainage_release.factors[credit_offset_on_release]`.

**O3 — observation — an undocumented 60-month window implements "whose due day has passed"**

`retrofit_ext_closeout_balance_payment` reads its due-now billings through
`within_months=K('due_window_months')` with `due_window_months: 60` on `due_date`. The rule says only
"whose due day has passed"; the 60-month bound has no quotation in `compute_basis`. It behaves
correctly here (`_within` rejects a future due date, which is exactly the intended filter, and no
billing on either world is older than five years), but the window is a convention the rule does not
state. Location: `retrofit_ext_closeout_balance_payment.compute.progress_due` / `.billed_due`.

**O4 — observation — base rules state cross-problem orders that ground no declared edge**

`retrofit_progress_billing_and_retainage` ("Retainage is released within the tier's release period …
provided the punch list is cleared and the closeout documents are delivered.") and
`retrofit_completion_and_closeout` ("The project closes when the punch list is clear, the documents
are delivered and the retainage is released.") each state an order between problems. No task's tree
rests on either — all four edges are grounded in extended rule sentences — so per check 6 this is an
observation. Location: the base copies inside `retrofit.extended.yaml`.

**O5 — observation — a base branch extended's selector can never produce**

`retrofit_cancellation_and_settlement`: "Deposits are applied to the settlement and refunded only
where the settlement is smaller than the deposit." `retrofit_ext_cancellation_settlement` floors the
figure at zero (`result: RND(MX(0, …), 2)`), so the refund branch can never be produced, and the
sentence is not named in `overwrite`. Task 0's settlement far exceeds its deposit
(103446.25 against a 67000.00 deposit billing), so no second answer arises on the only world that
exercises this policy, and this is recorded as an observation rather than a red light. Location:
`extended_policies[id=retrofit_ext_cancellation_settlement].overwrite` against
`policies[id=retrofit_cancellation_and_settlement].rule`, last sentence.

**O6 — observation — four `compute` bindings carry no `compute_basis` entry**

`booked_start` and `mobilised_on` (bare `F(...)` reads), `contract_billed` (late fee) and
`billed_all` (closeout balance) are restatements of bindings that already carry a basis. No new
basis is invented, so the two-way equivalence holds; the omission is recorded for completeness.
Location: the four `compute_basis` maps named.

**O7 — observation — one dead binding**

`retrofit_ext_closeout_balance_payment.compute.retainage_now_held` is computed
(`MX(0, retainage_withheld_total - retainage_released_total)`) and never read by any later binding.
It changes no scored value.


## closing_checklist

Written after both tasks were revealed and compared. This section is post-reveal by construction and
sits below the charter-global section, which was written and frozen before any reveal.

- **Audit files correspond one-to-one with the tasks.** `0.md` and `1.md` sit alongside this file in
  `env/env_0002_commercial_hvac_service_contractor/audits/policy_task/retrofit_projects_desk/`. This is
  revision 1 of the difficulty; there is no earlier revision to preserve. Both task files carry a
  `## source_gt_comparison`, and **neither carries an unqualified PASS**: task 0 closes
  `SOURCE-CHAIN RED (R1)`, task 1 closes `SOURCE-POLICY RED (F1) · SOURCE-FACTOR RED (F2, F4) ·
  SOURCE-CHAIN RED (R1)`.
- **Coverage and scope.** The six extended policies are fully covered by the two tasks; the scopes
  are pairwise disjoint and each spans the whole problem tree, root and prerequisites
  (`charter_scope` on both tasks confirms the split the auditor derived). Task tools and GT are
  closed: every write in `evaluation_criteria` is a `charter_scope` task tool, and each task tool's
  uuid8 is independently generated, frozen and unreused (`### action_binding_and_uuids`).
- **Problem trees.** Task 0: 1 prerequisite problem, 1 `value_input` edge (floor 1), the root
  resolved by the `owner="user"` tool `settle_project_cancellation_6d1f2e6f`, acyclic. Task 1:
  3 prerequisite problems, 3 `value_input` edges (floor 2), the root resolved by the `owner="user"`
  tool `pay_project_balance_ec87bb4f`, acyclic. The difficulty's four edges together form a DAG over
  two disjoint components; no cross-task reference creates a cycle. Every edge was shown to bear
  weight by replaying the skip on that task's own world.
- **Computations, baselines and factors.** All six computations declare a self-sufficient `baseline`
  whose sentences are all in the `rule`, and 4–6 factors each (2 `parameter`, 1 `method` minimum),
  with at least one multi-source and at least one cross-difficulty factor per task, the latter's
  other-product rows seeded and consistent with their own charters. Every factor was proved to bear
  weight against an honest baseline on its own handling-time world, and the whole-baseline fall-back
  of every computation is a definite number different from gold (1800.00, 49595.00; 37100.00,
  2669.20, 61586.00, 144575.00). **Two ladders, however, do not carry three distinguishable tiers**
  — findings F2 and F4 — and **one label is dishonest** — finding F3.
- **Instantiation-stage gates, re-run on the final form** (2026-09-17, from the repository root with
  `DIFF=env/env_0002_commercial_hvac_service_contractor/tasks/retrofit_projects_desk`), all green and
  unchanged from the snapshot supplied with the brief: `check_extended.py` EXTENDED OK;
  `check_task_tools.py` TASK TOOL CONTRACT OK; `replay_tasks.py` REPLAY OK (0.json 11 acts / 23 clos
  / match True, 1.json 17 acts / 30 clos / match True); `check_solvability.py` SOLVABILITY OK;
  `check_compute.py` COMPUTE OK (comps 2/4, factors 9/21, cross-difficulty factors 1/5);
  `check_grounding.py` GROUNDING OK; `check_cross_fire.py` SCOPE OK. `check_traceability.py` is not
  run at this stage — it reads the published KB, which the render step has yet to produce.
- **Difficulty verdict.** The four relationships do **not** hold together. Policy self-consistency
  fails on F1; the factors relationship fails on F2, F3 and F4; the problem tree holds in substance
  but its closure carries false world-assertions on both tasks (R1 in each task file); the unique
  solution is derivable and the auditor's independent derivation equals GT figure for figure on all
  six scored parameters, but F1 leaves a second defensible reading of task 1's `damages_credit_usd`
  standing. **This difficulty does not pass the source-layer audit at revision 1.**

## revision_2

Re-audit round 2, 2026-09-17. Revision 1 above is left untouched. This section was written and
frozen **before either task's round-2 GT was revealed**; it rests on the reworked charter, the
unchanged tool module and the rebuilt masked views only.

### charter_global_frozen_r2

- Hashes verified on disk against the round-2 brief:
  `retrofit.extended.yaml` `968366e517f695ffda2870935ec34ef2e9b35bf8f89487a9bac70dedfa3c17d5`
  (**changed** from `1f9ff702…`); `task_tools.py`
  `101ac47c75e9a373c374d392aad60e112a9f8bae5e25ebbb6ccfa2cf9d248149` (**unchanged**);
  `0.masked.json` `18d18c3e…` and `1.masked.json` `669137a1…` (**both identical to round 1** — the
  worlds and the customers' openings have not moved).
- Same permitted / masked field division as revision 1. Entry conditions: the coordinator's re-run of
  the full gate block (all OK, same lines as the original brief) is cited, not re-run;
  `check_traceability.py` stays deferred. Contamination: none.
- Re-derivation rule applied: the charter moved, so every charter-global section whose input is the
  charter is re-derived below; `action_binding_and_uuids` is carried forward by reference on the
  grounds that `task_tools.py` is byte-identical and the six `(target_tool, computes)` pairs in the
  reworked charter are the same six as in revision 1 (verified by listing them).
- **What moved in the charter** (a policy-by-policy diff of the round-1 dump against the reworked
  file; the base section is still byte-for-byte the constitution's copy):
  - `retrofit_ext_liquidated_damages_credit`: a second `overwrite` entry naming base
    `retrofit_schedule_guarantee` sentence 1 (the damages-amount clause) with the extended's own
    damages sentence as `replaced_by`; the `change_impact_allocation` ladder rebuilt on three new
    bindings `owner_asked_days` (owner-requested + schedule-acceleration impact),
    `concealed_code_days` (concealed-condition + code-requirement impact) and `supplier_days`
    (supplier-substitution impact), with tiers "owner asked → every impact day", "concealed/code and
    no owner-asked → those days alone", "otherwise → half the supplier days, rounded down" and a new
    param `shared_impact_share: 0.5`; `compute_basis` entries added for `mobilised_on`,
    `booked_start`.
  - `retrofit_ext_cancellation_settlement`: `stopped_stage_basis` relabelled `effect: parameter`
    with `value:` tiers; a third `overwrite` entry naming the base deposit-refund sentence.
  - `retrofit_ext_overdue_invoice_late_fee`: `months_overdue` middle tier now pro rata
    (`RND(overdue_days/30, 2)`); a `clock_runs` binding multiplying the result to zero when no
    progress billing has fallen due, with the rule sentence extended "… no overdue clock runs and no
    late fee is raised"; `payment_silence_ceiling` third tier extended to "or no payment has yet been
    received on it"; `contract_billed` basis added; the `overwrite.replaced_by` now quotes the
    ceiling sentence.
  - `retrofit_ext_retainage_release`: `credit_offset_share` middle tier now
    `unpaid_contract <= tenth` with the rule reading "a tenth of the contract value or less, nothing
    standing unpaid included".
  - `retrofit_ext_closeout_balance_payment`: new rule sentence "A billing whose due day has passed
    is one whose due day falls no later than the day of settlement and no earlier than five years
    before it, five years being as far back as a project account runs", quoted as the basis of
    `progress_due` / `billed_due`; `billed_all` basis added; dead binding `retainage_now_held`
    removed.
  - `retrofit_ext_storage_accrual_billing`: `booked_start` basis added. No other change.

### policy_conflict_scan_r2
Re-run over the reworked charter. Subjects, triggers, eligibility, time anchors, terminal states and
cross-category read boundaries are unchanged from revision 1 (same six `computes` / `target_tool`
pairs, same `cross_category` blocks, same status transition confined to the cancellation tool). The
task scopes are unchanged and remain pairwise disjoint and jointly exhaustive. No cross-policy
conflict. The intra-policy defect F1 is now declared (see `override_declarations_r2`).

### rule_compute_equivalence_r2
Re-run in both directions over all six policies. Every `compute` binding now carries a
`compute_basis` entry (the four gaps of O6 are filled), every `compute_basis` value is verbatim in
its `rule`, every `baseline.rule` sentence and every `overwrite.replaced_by` sentence is in the
`rule`, and every ladder tier's condition is in the `rule` and a branch of its `decides` binding.
The three round-1 promise/implementation gaps are closed by the charter itself: O1 (a late fee raised
when "no overdue clock runs") — the rule now says "and no late fee is raised" and `result` is
multiplied by `clock_runs`; O2(a) (no payment ever) — the ceiling ladder's third tier now names that
case; O2(b) (credits with nothing unpaid) — the credit-offset middle tier now reads "a tenth … or
less, nothing standing unpaid included" and the compute's `<= tenth` covers zero; O3 (an undocumented
60-month window) — the rule now states the five-year bound in words and the basis quotes it.
O7 (dead binding) is gone. PASS.

### action_binding_and_uuids_r2
Carried forward from revision 1 by reference: `task_tools.py` hash unchanged
(`101ac47c…`), and the reworked charter's six `(target_tool, computes)` pairs are the same six
(`bill_storage_charge_e8c4e90e`/`storage_amount_usd`,
`settle_project_cancellation_6d1f2e6f`/`settlement_amount_usd`,
`credit_liquidated_damages_732a84c1`/`damages_credit_usd`,
`release_project_retainage_a81bb865`/`retainage_release_usd`,
`bill_overdue_late_fee_5c3179f3`/`late_fee_amount_usd`,
`pay_project_balance_ec87bb4f`/`payment_amount_usd`). PASS.

### prerequisite_graph_r2 and prerequisite_sentences_r2
Re-run. The four edges, their `kind`/`form`/`gate`/`resolved_by`/`condition`/`policy_source`, and
the four prerequisite sentences are byte-identical to revision 1 (each `policy_source` re-located
verbatim in its own reworked `rule`); the graph is the same DAG; no tool name, policy id or
snake_case token appears in any rule; the sweep for cross-problem ordering sentences returns exactly
the four declared ones. The four-point test, the one-write-per-state argument and the written hop
derivations of revision 1 therefore stand unchanged. PASS. O4 (base rules stating cross-problem
orders that ground no edge) stands as an observation; no action was needed and none was taken.

### override_declarations_r2
Re-run sentence by sentence. **F1 closed**: base `retrofit_schedule_guarantee` sentence 1 is now
named in `overwrite` with a `replaced_by` that is a sentence of the extended rule, so the daily-amount
additions and the grace/suspension deductions are declared overrides and base's "at the tier's daily
amount for each calendar day of delay past that date" is no longer inherited in full. **O5 closed**:
the base deposit-refund sentence is now named, with the zero-floor sentence as `replaced_by`. All
other rows of the revision-1 table are unchanged and still declared. No undeclared override remains.

### factor_ladders_r2
Re-run over all six policies. Counts unchanged (4/5/6/4/6/5 factors; `parameter`/`method` now
2/2, 3/2, 4/2, 2/2, 3/3, 4/1; multi-source and cross-difficulty floors met per task as in
revision 1). **F3 closed**: `stopped_stage_basis` is labelled `parameter` and its tiers are `value:`
tier parameters; the policy keeps 2 `method` factors. **F4 closed**: the middle tier of
`overdue_month_count` now yields `RND(d/30, 2)` — 1.03 … 1.97 over its stated domain, never 1 — so
its three tiers select three distinct outcomes. **F2 closed**: the rebuilt
`change_impact_allocation` is no longer the identity on any one binding; replayed over seven
seeded variations of the change orders' reasons and impact days it returns distinct outcomes by
tier (every impact day when the owner asked for work; the concealed/code days alone otherwise
when they exist; half the supplier days, rounded down, in every other case), and its three
conditions are pairwise disjoint and exhaustive. The moved condition — schedule acceleration now
counted as owner-asked rather than supplier-side — is what a contractor actually holds, an
acceleration being work the owner asked for. Every other ladder is unchanged. One new observation,
**O8** below.

### findings_r2
- **F1, F2, F3, F4 — closed** (grounds above). **O1, O2, O3, O5, O6, O7 — closed.** **O4 — stands
  as an observation**, correctly left alone.
- **O8 — observation — `change_impact_allocation`'s fall-through tier is not the policy baseline.**
  `baseline.rule` says "The guaranteed period is not extended" and the factor's `baseline` is
  `K('no_extension_days') = 0`, which is honest; but the rebuilt ladder's `otherwise` tier extends
  the period by half the supplier-substitution days, rounded down, which equals the baseline only
  when fewer than two such days are stated. The same shape (the baseline-valued tier sitting away
  from the fall-through) was recorded for four ladders in revision 1 and is not a red light: the
  baseline is what `baseline.rule` states, substituting it changes the scored value, and the whole
  baseline gives a definite number different from gold on the only world that exercises the policy.
  Location: `extended_policies[id=retrofit_ext_liquidated_damages_credit].factors[id=change_impact_allocation]`.
- No new defect found in the charter.

### closing_checklist_r2
Written after both round-2 reveals.
- `0.md` and `1.md` each carry `## revision_2` with a frozen re-derivation, a comparison and
  findings; revision 1 text in all three files is untouched. **Both comparisons carry PASS.**
- Coverage and scope unchanged and complete; task tools and GT closed; uuid8s unchanged and
  independent (`task_tools.py` byte-identical).
- Problem trees unchanged: 1 and 3 prerequisite problems, 1 and 3 `value_input` edges, an
  `owner="user"` root in each, the whole difficulty a DAG; every edge re-proved load-bearing on the
  reworked charter with figures identical to revision 1, and every counterfactual terminal balance in
  both closures now equals the replayed figure.
- Every computation keeps a self-sufficient baseline and 4–6 factors within the label floors; every
  factor re-proved to bear weight; whole-baseline fall-backs unchanged and different from gold; the
  two ladders red-lighted in revision 1 now carry three distinguishable tiers; the one mislabel is
  corrected; the one undeclared override and the one dropped branch are declared.
- Gates: the coordinator's post-rework run of the full block (all OK, same lines as the original
  brief) is cited; `check_traceability.py` stays deferred to the render step.
- Round-1 items: F1, F2, F3, F4, R1 (×2), O1, O2, O3, O5, O6, O7 verified closed; O4 correctly left
  standing. New observations O8 (fall-through tier away from the baseline in the rebuilt
  `change_impact_allocation`, no consequence) and O9 (a stale sentence in task 1's
  `design_rationale`, no consequence). No new defect; nothing regressed.
- **Difficulty verdict at revision 2: all four relationships hold on both tasks — PASS.**
