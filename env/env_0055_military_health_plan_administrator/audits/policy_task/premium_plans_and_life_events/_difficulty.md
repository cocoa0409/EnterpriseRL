# Policy-task audit — premium_plans_and_life_events / charter-global

## charter_global_frozen

- Revision: revision_1 (first audit of this difficulty; no earlier audit files existed in this directory).
- Freeze time: 2026-10-11T13:15Z. Auditor: erl-task-policy-audit agent (independent of the instantiating agent).
- Hashes (re-computed by the auditor, equal to the coordinator's brief):
  - `tasks/premium_plans_and_life_events/premium.extended.yaml` sha256 `88d177bcbb69508f907bee50b9bd61d0e493e71947a72ea03a079728037d6ea2`
  - `tasks/premium_plans_and_life_events/task_tools.py` sha256 `2acde4611cdef783b428b97d7327e4935f21a421a2fe2923509f5cbe72c5a408`
  - masked views `0.view.json` `4d020d66…ac428`, `1.view.json` `ad9135f1…89ff` (match the brief)
- Read for this section: `blueprint/blueprint.yaml`, `blueprint/products/premium.yaml` (and the `binding`/`lifecycle` of `prime.yaml`, `select.yaml` for the cross-category reads), `blueprint/db_schema.json`, `blueprint/share_tools.py`, the extended charter, `task_tools.py`. The DSL primitive semantics (`SUM/COUNT/LATEST/within_months/MONTHS/DAYS/EXISTS/CFIELD`) were read from the gate's interpreter `skills/erl-task-instantiate/scripts/check_compute.py` (function bodies only, lines 224-430; no task data). That file is outside the brief's listed read domain; disclosed here, it carries no GT.
- Masked and not read when this section was written: `tasks/0.json`, `tasks/1.json` (all fields), the difficulty's and the scenario's `worklog.md`. Nothing in this section derives from any revealed GT.
- Entry conditions (Step 0): gate snapshot provided with the commands and result lines (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; traceability deferred); masked views provided with hashes. Input complete.

Policy short names used below: **ec** `premium_ext_orders_start_month_credit` (→ `post_orders_start_credit_1b4c6b63`), **lm** `premium_ext_orders_later_month_cancellation` (→ `cancel_remaining_month_premium_6cf5d114`), **pd** `premium_ext_amount_due_after_orders` (→ `pay_premium_balance_d66b5446`, owner=user), **rf** `premium_ext_refund_after_plan_end` (→ `refund_premium_credit_5d7ed849`), **al** `premium_ext_age_limit_month_credit` (→ `post_age_limit_credit_46c7df0c`), **pa** `premium_ext_age_limit_later_month_cancellation` (→ `cancel_post_age_limit_premium_583248a8`), **cp** `premium_ext_amount_due_at_age_limit` (→ `pay_final_premium_40bd3f0d`, owner=user), **rp** `premium_ext_refund_at_age_limit` (→ `refund_age_limit_credit_bb33162c`).

### policy_conflict_scan

- Base copy: lines 1-949 of the extended charter are byte-identical to `blueprint/products/premium.yaml` (diff shows only one trailing blank line). PASS.
- The eight extended policies form two mirror families: TRS-on-orders {ec, lm, pd, rf} and TRR-at-age-limit {al, pa, cp, rp}. Subjects: ec/lm/al/pa → `premium_proration_credit`; pd/cp → `premium_payment`; rf/rp → `premium_refund`. Plan-type scoping separates the families at the rule level (TRS vs TRR), so pd/cp, rf/rp and ec/al never both apply to one plan.
- **Overlap al ↔ pa on one bill (conflict, see finding G7).** al: "the plan owes an age-limit credit against the bill of that most recently paid month for the days of the month after coverage ended, posted as a loss-of-eligibility credit". pa: "the bill of the latest-billed coverage month still standing on the plan owes a post-age-limit cancellation for the days of that month after coverage ended, posted as a loss-of-eligibility credit against that bill. A credit ... is posted against such a bill whether or not the bill has been paid". When the latest-billed month is also the most recently paid month, both policies owe a loss-of-eligibility credit for the same days of the same bill, and pa (unlike lm, which has `remaining_month_days_already_credited`) has no clause leaving out days al already credited. The TRS pair ec/lm does interlock (lm leaves out activation-on-orders days). Neither task world reaches this case (in both, the latest-billed month is unpaid at the opening and is not the most recently paid month).
- Time anchors: ec/al anchor on the bill of the latest *payment* by posted date; lm/pa/pd/cp/rf/rp on the latest monthly bill by due date; the claim-day factors anchor on the frozen clock (finding G2).
- Cross-category read boundaries: ec/lm read `prime_enrollments` (variant ADSM: status, effective date, application date); al/pa read `select_enrollments` (status, effective date, application date). Both are other difficulties' holdings (prime_enrollment_fees_and_pcm, select_claims_and_cost_shares). No write crosses category.
- Scope exclusivity (pre-reveal, inferred from the two worlds since `charter_scope` is masked): task 0's world (TRS plan ended on orders, Prime ADSM enrollment, unpaid October bill) can only engage {rf, pd, lm, ec}; task 1's world (TRR plan, 60th birthday, Select retiree enrollment, unpaid November bill) can only engage {rp, cp, pa, al}. Disjoint, and together they cover all eight extended policies. To be confirmed against `charter_scope` after the reveal.

### rule_compute_equivalence

Each compute binding carries a `compute_basis` quotation that is verbatim in its rule (spot-checked for every binding of every policy). The sweep back, rule sentence by rule sentence, finds these gaps:

1. **Claim-day window (G2, SOURCE-POLICY RED).** Rule (ec): "where the purchaser's own claim lines show care in that month [the most recently paid month], each of those claim lines takes one day off". Compute: `ec_own_claims: COUNT(..., within_months=2, date_field='service_date', ...) - COUNT(..., within_months=1, ...)`, and the interpreter's `_within` is `0 <= MONTHS(service_date, NOW) < within_months`. So compute counts lines whose service date is one month before the frozen clock, not lines in the most recently paid month. Same for al (`al_own_claims`, `al_all_claims`) and, with `within_months=1` (the month before NOW), for lm (`lm_own_claims`) and pa (`pa_own_claims`) against "the latest-billed month". Same situation, two conclusions: for ec with frozen clock 2026-10-30 and most recently paid month 2026-09, a claim on 2026-08-31 has MONTHS(2026-08-31, 2026-10-30) = 1. Compute counts it and the rule does not. If the frozen clock were 2026-11-05 with September still the most recently paid month, compute would count October claims and drop September ones. Neither task world has a line in a divergence band (see each task file), so no task value moves.
2. **al claim qualifier not implemented (G3, SOURCE-POLICY RED; consequence in task 1).** al rule: "Days of the most recently paid month on which the plan paid a claim *after its coverage ended* are treated as covered". `al_own_claims` / `al_all_claims` carry no comparison with the termination date. ec, lm and pa have no such qualifier.
3. **"the plan paid a claim" vs "claim lines show care" (G4, SOURCE-POLICY RED; consequence in both tasks).** The governing sentence of all four claim-day rules is "Days ... on which the plan paid a claim are treated as covered". Its ladder and compute count every `premium_claim_line_post` line, including a line on which TRICARE paid nothing (`deductible_applied = cost_share_amount = allowed_amount`). The rule's governing sentence and its ladder disagree on whether such a line counts.
4. **First-credited-day ladder vs compute (G5, SOURCE-POLICY RED).** Rule (ec; al mirrors it): "where the enrollment was applied for on or before its effective date, that effective date is the first credited day; where it was applied for after its effective date, the first credited day is the day after the application date; otherwise the first credited day is the day after the date the credit is counted from." The rule makes the first two tiers depend only on the application date. Compute `ec_first_day` applies them only when `ec_ad_open and ec_ad_day >= 1`. Situation: an ADSM enrollment applied/active with effective date before the paid month began and applied for after that date. The rule says the first credited day is the day after the application date. Compute says day 1 of the month (`ec_anchor_day + 1` with anchor 0). A second situation: an ADSM enrollment that is neither applied nor active but was applied for on or before its effective date. The rule's tier 1 names its effective date, while compute counts from the termination date. Both task worlds sit on tier 1 with the effective date inside the paid month, so no task value moves.
5. **"in force" vs `status in (active, applied)` (G6, SOURCE-POLICY RED).** rf/rp/pd/cp rules distinguish "the plan has ended" / "the plan is in force ..." / "otherwise". Compute uses `*_ended: F('status') != 'active' and F('status') != 'applied'`, so an `applied` plan, which the base lifecycle says has not started coverage, falls into the in-force branch in compute and into "otherwise" in the rule. Example: an applied plan with a credit balance. rf rule tier 3 gives "only the month whose bill the latest payment settled", while compute gives `'paid'` (every month but the latest-billed). Both task plans are `terminated_ineligible`, so no task value moves.
6. **Zero clause (observation O1).** ec: "A most recently paid month with no day after the plan's termination date carries no orders-start credit." (al: the same for the age-limit credit). This sentence is unconditional in the rule. In compute it holds only on the fall-through path (`ec_anchor_day = ec_term_day`). On tiers 1-2 of the count-from ladder, compute credits days before the termination date. The ladder sentence is the more specific one, so in ec I record this as an observation. In task 1 it combines with a seed defect into a demonstrated second reading (see `1.md`).
7. **rf/rp "every month except the latest-billed month" (observation O2).** Compute removes only entries *related to the latest bill's entry id* (`related_premium_entry_id=rf_latest_bill`), while the rule removes the latest-billed *month*. A change credit for that month booked against another entry is excluded by the rule and included by compute. This case is not reached in either world.
8. **al/pa "TRICARE Select enrollment as a retiree" (observation O3).** `EXISTS('select', status=...)` / `CFIELD('select', ...)` carry no variant filter. This is harmless in task 1, whose only Select row is `TRICARE Select Retiree Group A`.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (eight tools, eight policies, `computes: amount` each). PASS.
- uuid8s: 1b4c6b63, 6cf5d114, d66b5446, 5d7ed849, 46c7df0c, 583248a8, 40bd3f0d, bb33162c. They are pairwise unrelated, with no shared prefix or tail and no sequence. PASS.
- Tool bodies validate nothing (each does `ctx.create` on `premium_ledger` plus `_PlanLedger.shift_balance`), so there is no prerequisite check, error or hint at runtime. PASS.
- **Docstring overlap (G1, SOURCE-POLICY RED).** Three generic tools describe, word for word, the action of three TRR-specific tools:
  - `cancel_remaining_month_premium_6cf5d114`: "Cancel, by a loss-of-eligibility credit, the part of a monthly premium bill on a TRICARE Reserve Select, **TRICARE Retired Reserve** or TRICARE Young Adult plan that is still standing for a coverage month falling after the purchaser stopped being eligible for the plan". Compare `cancel_post_age_limit_premium_583248a8`: "Cancel, by a loss-of-eligibility credit, the part of a TRICARE Retired Reserve monthly premium bill that charges days of a coverage month falling after the plan's coverage ended at the age limit". Both write the same row: `event_type premium_proration_credit`, `adjustment_reason loss_of_eligibility`, same arguments. The only difference is the id prefix (`pcx_` vs `pac_`).
  - `pay_premium_balance_d66b5446` ("The purchaser of a TRICARE Reserve Select, **TRICARE Retired Reserve** or TRICARE Young Adult plan pays premiums owed on that plan ... in one payment ... applied to the named bill") vs `pay_final_premium_40bd3f0d` ("The purchaser of a TRICARE Retired Reserve plan whose coverage has ended pays ... what the plan's last monthly premium bill still owes"). The rows are identical except for the prefix (`ppy_` vs `pfp_`).
  - `refund_premium_credit_5d7ed849` ("Issue a refund to the purchaser of a TRICARE Reserve Select, **TRICARE Retired Reserve** or TRICARE Young Adult plan out of the credit balance standing on that plan") vs `refund_age_limit_credit_bb33162c`. The rows are identical except for the prefix (`prf_` vs `pra_`).
  The agent never sees `target_tool`. For a TRR plan ended at the age limit, the docstrings admit both tools for each of pa, cp and rp. Task 0 (TRS) is unaffected because every TRR-specific docstring excludes TRS. The consequence is demonstrated in `1.md`.
- Ordering words: none of "before/after/first" is used in the sequence sense. One cross-call reference exists: `refund_age_limit_credit_bb33162c`, `related_premium_entry_id`: "as returned by the premium-ledger lookup **or by the call that posted the credit**". This states that a credit-posting call can precede the refund in the same session. Recorded as observation O4: it hints the al node of the TRR tree, but I cannot demonstrate a changed score.

### prerequisite_graph

| blocked | edge → problem | kind | gate | form | resolved_by = target_tool of problem | quotable in blocked rule |
|---|---|---|---|---|---|---|
| pd | lm | value_input | `pd_elig_off` (binding exists) | state | `cancel_remaining_month_premium_6cf5d114` ✓ | ✓ |
| pd | ec | state_gate | `premium_ledger.adjustment_reason` | state | `post_orders_start_credit_1b4c6b63` ✓ | ✓ |
| rf | pd | state_gate | `premium_ledger.related_premium_entry_id` | state | `pay_premium_balance_d66b5446` ✓ | ✓ |
| rf | ec | value_input | `rf_ord_sum` (binding exists) | state | `post_orders_start_credit_1b4c6b63` ✓ | ✓ |
| cp | pa | value_input | `cp_elig_off` (exists) | state | `cancel_post_age_limit_premium_583248a8` ✓ | ✓ |
| cp | al | state_gate | `premium_ledger.adjustment_reason` | state | `post_age_limit_credit_46c7df0c` ✓ | ✓ |
| rp | cp | state_gate | `premium_ledger.related_premium_entry_id` | state | `pay_final_premium_40bd3f0d` ✓ | ✓ |
| rp | al | value_input | `rp_elig_paid` (exists) | state | `post_age_limit_credit_46c7df0c` ✓ | ✓ |

ec, lm, al and pa have `prerequisite: []`. Every `problem` names an extended policy in this file, none names itself, and the graph is acyclic (two disjoint DAGs: rf→{pd,ec}, pd→{lm,ec}; rp→{cp,al}, cp→{pa,al}). No `fallback_reason` is needed because all edges are state form. The conditions match the sentences in strength. The rf/rp "every paid month in which ..." sentences are written open and their conditions name the one month they single out in a world, which is a faithful narrowing. Observation O5: the four `state_gate` edges put a ledger column in `gate` rather than an eligibility-gate id, because the extended policies declare no `eligibility` blocks. The gate exists only as the rule sentence. No consequence.

### prerequisite_sentences

Four-point test, per edge:

- pd←lm: "The amount paid toward a bill after orders is fixed only after that bill carries the loss-of-eligibility credit owed for its days of active duty coverage." Connective "only after"; record-visible state (`adjustment_reason = loss_of_eligibility` on the bill); no tool, id or snake_case. Writes of this difficulty that create a loss-of-eligibility credit: lm, al, pa. Only lm's rule concerns a TRS bill and "days of active duty coverage", so the hop is unique. PASS.
- pd←ec: "The amount paid toward a bill after orders is not fixed before every coverage month the purchaser has already paid carries the activation-on-orders credit owed for its days of active duty coverage." Connective "not ... before"; only ec writes `activation_on_orders`. PASS.
- rf←pd: "A refund is not issued until every monthly bill on the plan has a payment posted against it." Connective "not ... until"; writes creating a payment: pd (TRS by rule) and cp (TRR by rule), so the hop is unique per plan type. PASS at the rule level (tool-level overlap is G1).
- rf←ec: "The refund owed on a plan is fixed only after every paid month in which the purchaser's active duty coverage began carries the activation-on-orders credit owed for its days of active duty coverage." PASS.
- cp←pa: "The amount paid toward the closing bill is fixed only after that bill carries the loss-of-eligibility credit owed for its days after the age limit." pa (latest-billed bill) and al (most recently paid month's bill) both write this state. They are disjoint whenever the latest-billed bill is unpaid, which is the TRR tree's shape. In the al/pa overlap of the conflict scan (G7) two writes could bring it about. PASS for unpaid latest bills.
- cp←al: "The amount paid toward the closing bill is not fixed until every coverage month the purchaser has already paid carries the loss-of-eligibility credit owed for its days after coverage ended." PASS, conditional on what "coverage ended" means in the world (see task 1, seed defect).
- rp←cp: "The refund owed at the age limit is issued only after every monthly bill on the plan carries a payment posted against it." PASS at the rule level.
- rp←al: "The refund owed at the age limit is not fixed until every month the purchaser paid before coverage ended carries the loss-of-eligibility credit owed for its days after coverage ended." PASS, with the same caveat.

No rule restates a dependency in a second wording, names another tool or policy id, or states a cross-problem order that grounds no declared edge. The depended-on rules (ec, lm, al, pa, pd, cp) do not restate the blocked side's sentence. Derivation for each family, from sentence + records + depended-on rule to the resolving action:
- TRS: rf sentence 1 → a bill without a payment → pd ("settles the bill of the latest-billed coverage month by one payment of their own") → pd sentence 1 → that bill lacks a loss-of-eligibility credit → lm ("the bill of the latest-billed coverage month ... owes a remaining-month cancellation ... posted as a loss-of-eligibility credit"). rf sentence 2 and pd sentence 2 → the paid month in which active duty coverage began lacks an activation-on-orders credit → ec ("owes an orders-start credit against the bill of that most recently paid month ... posted as an activation-on-orders credit"). One reading.
- TRR: the same shape with cp, pa and al.

### override_declarations

Sentence by sentence against each `base_policy_refs` entry:

- **premium_termination_and_refund** (refs of ec, lm, rf, al, pa, rp):
  - "A purchaser may end the plan at any time … starts no lockout." Not engaged.
  - "Premium paid for days after the termination date is credited back: … every later paid month in full." Handled differently by ec, lm, al and pa, and **declared** in each one's `overwrite` (the count-from / first-day replacement). The rate, claim-day and change-credit deviations also contradict this sentence. They are covered because the whole sentence is named as superseded, but `replaced_by` restates only the anchor (observation O6).
  - "A credit is posted only against a bill that has a payment posted against it." Followed by ec and al (paid bills); departed from by lm and pa and **declared**.
  - "A credit balance is refunded through the original payment method within premium_refund_issue_days." Replaced in rf and rp, **declared**. The extended baseline "Credits on the plan are carried forward to future bills and are not paid out" lives under that declaration.
  - "A termination for loss of eligibility or the purchaser's death is credited the same way." Superseded through the termination-credit declaration above.
- **premium_survivor_and_activation** (ec, lm): "the plan ends under activation_effect on the day before the orders start, unpaid future bills are cancelled by a credit". lm cancels the latest bill by credit, consistent with this. Its claim-day and already-credited deductions leave part of a bill uncancelled. The base does not say whether the month that contains the orders start is a "future bill", so I record no conflict.
- **premium_coverage_type_rules** (ec, lm, al, pa): followed. The seeded change credits obey the base proration in both worlds (task files).
- **premium_billing_schedule** (all): "Bills are posted only on a plan whose status is applied or active" is not engaged because no bill is written. The formula is followed.
- **premium_plan_eligibility** (al, pa): "Coverage ends under coverage_end_rule at the age limit". For TRR, `coverage_end_rule: ends_on_the_day_before_the_60th_birthday`. The extended policies follow it, and only the task 1 seed departs from it (see `1.md`).
- **premium_payment_and_nonpayment** (pd, cp, rf, rp):
  - "every later monthly premium must be paid through a recurring method": followed ("through a recurring payment method").
  - **"A payment settles the oldest unpaid bill first."** pd and cp both say "settles the bill of the latest-billed coverage month by one payment ... applied to that bill", and both have `overwrite: []`. **Undeclared override (G8, SOURCE-POLICY RED).** With two unpaid monthly bills, the base applies the payment to the older bill and pd/cp to the latest one. In both task worlds the only unpaid monthly bill is the latest-billed one, so the two coincide there.
  - Delinquency/grace/termination/reinstatement sentences: not engaged.

### factor_ladders

Declared factors per policy, effect label (P = parameter, M = method), decides, cross-difficulty, and the auditor's structural tests. The tests: are the tiers distinct in outcome, does each condition or outcome match what the business holds, is the label honest, and does any tier restate the scope or gate. All tiers of all ladders are stated in the rule prose and implemented in compute (checked).

| policy | factor | P/M | decides | xdiff | structural verdict |
|---|---|---|---|---|---|
| ec | orders_start_count_from | M | ec_anchor_day | prime | survives; tiers 1-2 multi-source (prime status + prime effective date vs premium-ledger month) |
| ec | orders_start_first_day | M | ec_first_day | prime | survives the ladder test (rule/compute gap G5 noted) |
| ec | orders_start_claim_days | M | ec_claim_days | – | **struck (G10)** |
| ec | orders_start_monthly_amount | P | ec_rate | – | **struck (G9)** |
| ec | orders_start_change_taken_off | P | ec_chg_share | – | **struck (G10)** |
| ec | orders_start_change_spread | M | ec_chg_spread | – | survives |
| lm | remaining_month_amount | P | lm_rate | – | **struck (G9)** |
| lm | remaining_month_change_taken_off | P | lm_chg_share | – | **struck (G10)** |
| lm | remaining_month_days_already_credited | P | lm_done_days | – | **struck (G10)** |
| lm | remaining_month_first_day | M | lm_first_day | prime | survives |
| lm | remaining_month_claim_days | M | lm_claim_days | – | **struck (G10)** |
| pd | payment_monthly_amount | P | pd_amount | – | **struck (G9)** |
| pd | payment_change_credits / payment_orders_credits / payment_eligibility_credits | P | pd_chg_off / pd_ord_off / pd_elig_off | – | **struck (G10)** |
| pd | payment_other_month_change_credits / payment_other_month_orders_credits | M | pd_chg_used / pd_ord_used | – | **struck (G11)** |
| rf | refund_months_covered | M | rf_scope | – | survives |
| rf | refund_change_credits / refund_orders_credits / refund_eligibility_credits | P | rf_*_out | – | survive (observation O7) |
| rf | refund_earlier_refunds | P | rf_refunded_off | – | **struck (G12)** |
| al | (mirror of ec) | | | select | count_from, first_day, change_spread survive; claim_days, monthly_amount, change_taken_off struck |
| pa | post_age_limit_amount (P), post_age_limit_change_taken_off (P), post_age_limit_first_day (M, select), post_age_limit_claim_days (M) | | | | only first_day survives |
| cp | closing_monthly_amount (P), closing_change_credits (P), closing_eligibility_credits (P), closing_other_month_change_credits (M), closing_other_month_eligibility_credits (M) | | | | none survives (G9, G10, G11, G13) |
| rp | age_limit_refund_months (M), earlier_change_credits (P), latest_change_credits (P), earlier_eligibility_credits (P), latest_eligibility_credits (P), earlier_refunds (P) | | | | **none survives (G13)** |

Declared counts: ec 6 (2P/4M), lm 5 (3P/2M), pd 6 (4P/2M), rf 5 (4P/1M), al 6 (2P/4M), pa 4 (2P/2M), cp 5 (3P/2M), rp 6 (5P/1M). As declared, every policy meets 4-6, ≥2 P and ≥1 M. Cross-difficulty factors: ec ×2 and lm ×1 (prime); al ×2 and pa ×1 (select). Multi-source factors: ec/al count_from (tiers 1-2: enrollment status ∧ enrollment effective date against the ledger month). No factor of pd, cp, rf or rp is multi-source.

Surviving counts after the structural tests: ec 3 (0P/3M), lm 1, pd 0, rf 4 (3P/1M), al 3 (0P/3M), pa 1, cp 0, rp 0. **Only rf meets the 4-6 / ≥2P / ≥1M bounds.** The per-task consequence is in each task file under `factor_weight`.

### findings

Charter-global findings. A task file picks up the demonstration of each against its own world.

- **G1: SOURCE-POLICY RED (check 3, unique action binding).** Three generic tools' docstrings admit the TRR age-limit actions of pa, cp and rp (quotations under action_binding_and_uuids). Root cause: the generic tools' docstrings name TRICARE Retired Reserve while three TRR-specific tools exist. Consequence: for a TRR plan ended at the age limit, each of the three writes has two tools whose docstring fits and whose rows are identical except for the id prefix. Affected: `task_tools.py` docstrings of `cancel_remaining_month_premium_6cf5d114`, `pay_premium_balance_d66b5446` and `refund_premium_credit_5d7ed849`. Bears on task 1, not on task 0.
- **G2: SOURCE-POLICY RED (check 2).** The claim-day window is computed relative to the frozen clock, not the named month (ec, lm, al, pa compute; quotations under rule_compute_equivalence §1). Consequence: on a line dated 2026-08-31 with clock 2026-10-30 and paid month 2026-09, compute counts it and the rule excludes it. Bears on neither task's values (checked in each file).
- **G3: SOURCE-POLICY RED (check 2).** al's qualifier "after its coverage ended" has no compute counterpart. Bears on task 1.
- **G4: SOURCE-POLICY RED (check 2 / unique solution).** In ec, lm, al and pa the governing sentence "Days ... on which the plan paid a claim" conflicts with the ladder and compute, which count any posted claim line, including lines on which TRICARE paid $0. Bears on task 0 and task 1, whose paid-month claim lines are fully deductible.
- **G5: SOURCE-POLICY RED (check 2).** The ec/al first-credited-day tiers are unconditional in the rule and gated in compute. Bears on neither task's values.
- **G6: SOURCE-POLICY RED (check 2).** "In force" vs compute `applied or active` in rf, rp, pd and cp. Bears on neither task's values.
- **G7: SOURCE-POLICY RED (conflict scan).** al and pa both owe a loss-of-eligibility credit for the same days of one bill when the latest-billed month has been paid, and pa has no already-credited deduction. Bears on neither task's values.
- **G8: SOURCE-POLICY RED (check 1, undeclared override).** pd and cp apply the payment to the latest-billed bill against base "A payment settles the oldest unpaid bill first", with `overwrite: []`. Bears on neither task's values (one unpaid bill each).
- **G9: SOURCE-FACTOR RED (unreal ladder: two tiers select the same value).** The monthly-amount factors are ec `orders_start_monthly_amount`, lm `remaining_month_amount`, pd `payment_monthly_amount`, al `age_limit_monthly_amount`, pa `post_age_limit_amount` and cp `closing_monthly_amount`. Tier 2: "where the month was billed at an amount other than the monthly premium of the tier the plan now carries, it is the amount billed". Fall-through: "otherwise it is the monthly premium of the tier the plan carries". The fall-through's condition (no adjustment and billed == tier premium) makes its value equal to the amount billed, which is tier 2's value. Compute shows it: `(ec_billed + ec_adj) if ec_adj > 0 else (ec_billed if ec_billed != ec_tier else ec_tier)` ≡ `ec_billed + ec_adj` in every world. The ladder is one formula, "the amount billed plus any adjustment", written as three tiers. Bears on both tasks.
- **G10: SOURCE-FACTOR RED (unreal ladder: one tier written as two, over a condition the business does not weigh).** Two ladder shapes:
  - "credits standing against that bill → their total; none against the bill but posted for that coverage month against another entry → that total; otherwise nothing". This covers ec/lm/al/pa `*_change_taken_off`, pd `payment_change/orders/eligibility_credits`, cp `closing_change/eligibility_credits` and lm `remaining_month_days_already_credited` (activation-on-orders days, else loss-of-eligibility days, else none).
  - "the purchaser's own claim lines → each takes one day off; only family members' lines → each takes one day off; otherwise none". This covers ec/lm/al/pa `*_claim_days`.

  In both shapes tiers 1 and 2 select the same value or method ("the month's credits" / "one day per claim line") over two subsets. The fall-through gives that same value at zero. The two tiers part only in the mixed case, where tier 1 discards the other subset: same-month credits booked elsewhere, loss-of-eligibility days already credited, or family members' claim lines. A premium administrator nets every credit already posted for a coverage month and counts every covered claim day, whoever the patient is and whichever entry the credit hangs on. The ledger entry a credit is booked against, and whether the purchaser also had care, are not conditions that line of business weighs for these quantities. Bears on both tasks. The per-task factor verdicts do not depend on G10 (G9/G11/G13 already defeat the bounds); it is listed because it is a defect.
- **G11: SOURCE-FACTOR RED (two tiers with the same effect).** These are pd `payment_other_month_change_credits` / `payment_other_month_orders_credits` and cp `closing_other_month_change_credits` / `closing_other_month_eligibility_credits`. Tier 2 ("used up to what the bill still owes") and the fall-through ("used in full") always give the same scored result, because `result = MX(0, RND(still_owed - chg_used - ord_used, 2))`. If the credits are at least what is owed, both tiers floor the result at 0; otherwise `MN(x, still_owed) = x`. Each ladder therefore has two outcome-distinct tiers, not three. Bears on both tasks.
- **G12: SOURCE-FACTOR RED (unreal tier).** rf `refund_earlier_refunds` / rp `age_limit_refund_earlier_refunds` tier 2: "where the plan is in force, refunds already issued are taken off only up to the change credits being paid out". Example: an in-force plan with an earlier refund R of an orders credit and no change credits being paid out. Compute `MN(rf_refunded_sum, rf_chg_out)` = 0, so R is paid out a second time. No premium administrator publishes that treatment. Tier 3 ("otherwise nothing") is reachable in the rule only through an `applied` plan, and compute never reaches it (G6). Bears on both tasks.
- **G13: SOURCE-FACTOR RED (tier condition holds of every customer who reaches the write).**
  - cp's scope sentence is "A purchaser whose TRICARE Retired Reserve plan has ended at the age limit settles the bill …", so cp's `closing_other_month_*` tier 1 "the plan has ended" holds of every cp customer.
  - rp's scope sentence is "A purchaser who asks for the money left on a TRICARE Retired Reserve plan that ended at the age limit …", so rp's `age_limit_refund_months`, `earlier_change_credits`, `earlier_eligibility_credits` and `earlier_refunds` tier 1 "the plan has ended" holds of every rp customer.
  - rp's `latest_change_credits` and `latest_eligibility_credits` tier 1 "the latest-billed month's bill has a payment posted against it" holds of every customer who reaches the refund write, because of rp's own gate "issued only after every monthly bill on the plan carries a payment posted against it".

  Each of these ladders restates the scope or the gate, and its other tiers are unreachable at the write. (rf's scope, "A purchaser who asks for the money left on a TRICARE Reserve Select plan", does not require an ended plan, so rf escapes this.) Bears on task 1.
- Observations (no demonstrated consequence on a task value):
  - O1: unconditional zero clause in ec/al.
  - O2: rf/rp month-vs-entry scoping.
  - O3: al/pa Select variant filter.
  - O4: `refund_age_limit_credit` docstring's cross-call reference.
  - O5: `state_gate` gates name ledger columns.
  - O6: `replaced_by` restates only the anchor while the superseded sentence also governs rate, claim and change deductions.
  - O7: rf/rp split one "credit balance" quantity into three per-credit-type factors with identical ladders. In the in-force-with-balance tier, each credit type separately retains "one monthly premium", so up to three monthly premiums are withheld. This is a factor-count inflation, not a demonstrated wrong value.
  - O8: the claimed event types premium_purchase/activate/reject/bill/coverage_type_change/payment_method_update/terminate_request have no extended policy. Allowed, noted.

## post_reveal_addendum

Written after the reveal at 2026-10-11T13:19:54Z. This file's frozen section above has mtime 13:17:32Z and was not edited after the reveal.

- `charter_scope` confirms the inferred scopes: task 0 = {ec, lm, pd, rf} with their four tools; task 1 = {al, pa, cp, rp} with theirs. Pairwise disjoint and jointly complete over the eight extended policies.
- **G1 is revised from SOURCE-POLICY RED to observation.** This does not rest on GT. `erlbench/engine.py`, read after the freeze, shows that task tools are hidden and unlocked by "the exact tool name found in the knowledge base". The policy surface therefore binds each tool to the documents of its own policy, so I cannot show that a TRR case reaches a TRS-scoped tool. The over-broad generic docstrings remain a check-3 wording defect (observation).
- The other charter-global findings are unchanged. The GT figures of every factor substitution agree with the auditor's recomputation in both tasks, so the factor findings are about ladder structure (G9–G13), not arithmetic.

## closing_checklist

- Per-task files correspond one-to-one to `tasks/0.json` and `tasks/1.json`, with `_difficulty.md` alongside. revision_1 is the only revision.
- Comparison sections do **not** all carry PASS:
  - task 0: SOURCE-POLICY RED, problem tree PASS, SOURCE-FACTOR RED, SOURCE-TASK RED.
  - task 1: SOURCE-POLICY RED, SOURCE-CHAIN RED, SOURCE-FACTOR RED, SOURCE-TASK RED.
- Coverage and scope: all eight extended policies are covered; scopes are disjoint across whole trees; task tools and GT are closed; the uuid8s are independent.
- Trees: each has 3 prerequisite problems, 2 value_input edges (≥ max(n−1, 1)), an owner=user write (pd / cp) and no cycle. The difficulty-wide graph is two disjoint DAGs.
- Factors: only rf meets 4–6 / ≥2 parameter / ≥1 method after the structural tests. ec, lm, pd, al, pa, cp and rp fall below (G9–G13). rf and rp lack a tier near-miss. Every declared factor bears weight on its world, and every whole-baseline fall-back differs from gold. In task 1 those fall-backs depend on the seed's contradictory termination date.
- Gates: not re-run by the auditor (Step 0: cite, do not run). The coordinator's snapshot (all green; traceability deferred) applies to the audited form, whose hashes (`88d177bc…`, `2acde461…`) are unchanged.
- **The difficulty does not pass the source-layer audit.**

---

## revision_2

### charter_global_frozen (revision_2)

- Re-audit round 2. Auditor: erl-task-policy-audit agent. Written before any round-2 task file was opened.
- Hashes, re-computed: `premium.extended.yaml` `b03907455774411c275bbc507dadd85dcae36ba0499ac55a12aee555dbb14db8` (changed from `88d177bc…`); `task_tools.py` `6d99b516c571e3767ba543ecfe9385a92217598b6755e37a06ea1adcbf0fbc80` (changed from `2acde461…`). Both shared inputs moved, so every charter-global section is re-derived in full below. Nothing is carried forward by reference.
- Read: the new charter (base section re-diffed against `blueprint/products/premium.yaml`: identical except for one trailing blank line), the new tool module, `blueprint/blueprint.yaml`, `erlbench/engine.py`, and the gate interpreter's DSL functions, as in revision_1. Masked and unread at this point: round-2 `tasks/*.json` and all worklogs. `/tmp/erl55_premium/` was not read.
- contamination_disclosure: I read the **round-1** task files after the revision_1 freeze, so I know round-1 GT conventions and values (rendered into the revision_1 comparison sections above). The round-2 charter, tools and worlds differ, and no round-2 GT has been seen. That prior exposure is disclosed, not hidden.
- Gate snapshot cited from the coordinator (not re-run): EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK; CACHE-DIFF info; traceability deferred. The coordinator also reports that the round-2b tools fix was implementation-only.

New policy set (short names):
- **ec** `premium_ext_orders_start_month_credit` → `post_orders_start_credit_1b4c6b63`
- **lm** `premium_ext_orders_month_relief` → `post_orders_month_relief_6cf5d114`
- **cc** `premium_ext_member_only_change_credit_after_orders` → `post_member_only_change_credit_d66b5446`
- **rf** `premium_ext_refund_after_plan_end` → `request_premium_refund_5d7ed849` (owner=**user**)
- **al** `premium_ext_age_limit_month_credit` → `post_age_limit_credit_46c7df0c`
- **cn** `premium_ext_retiree_member_only_credit` → `post_retiree_member_only_credit_40bd3f0d`
- **an** `premium_ext_post_age_limit_cancellation` → `cancel_post_age_limit_premium_583248a8`
- **rp** `premium_ext_refund_at_age_limit` → `request_age_limit_refund_bb33162c` (owner=**user**)

All other tools are owner=agent. Every body does `ctx.create` + `ctx.update` and validates nothing.

### policy_conflict_scan (revision_2)

- Families. TRS: rf→{ec, cc, lm}, lm→cc. TRR: rp→{al, an}, an→cn. The families are disjoint by plan type.
- ec vs lm both write `activation_on_orders`. ec writes it only on a month "the purchaser has already paid" and lm only on a latest-billed bill that "has no payment posted against it", so the two are disjoint. The round-1 interlock problem is gone.
- **al vs an (round-1 G7): closed.** al posts against the most recently paid month (or, where that month ended before coverage did, the latest-billed month) and returns only what was *paid* ("where they cover only part of it, it is the amount paid divided by those days; otherwise nothing is returned, the days ... being cancelled on that unpaid bill instead"). an withdraws only what is *unpaid* ("where a payment covers only part of it, it is the part still unpaid"). On one bill the two are complementary, not overlapping.
- cc vs cn both write `coverage_type_change` credits, one for TRS and one for TRR. Disjoint.
- **Ownership conflict with the scenario constitution (N3, below).** `blueprint.yaml` (this difficulty's summary) says: "Recording purchases, bills, payments, credits, refunds, coverage-type changes and payment-method updates are agent service actions on a verified caller, while confirming a termination of the plan is the purchaser's own act". rf/rp now say "A purchaser who asks for the money left on a ... plan requests its refund in person". The tools `request_premium_refund_5d7ed849` and `request_age_limit_refund_bb33162c` are `owner="user"`, and each "books one refund entry ... status 'issued'". The same refund write is an agent service action under the constitution and the purchaser's own act under the charter and tools.

### rule_compute_equivalence (revision_2)

Verbatim `compute_basis` is present for every binding (spot-checked per policy). The sweep back finds:

- **ec/lm first-credited/relieved day (round-1 G5): closed.** The rule tiers now name their own precondition ("where the credit is counted from the enrollment's effective date or from the first day of the month and the enrollment was applied for on or before that day …"). Compute `ec_first` gates the same way (`ec_from <= MX(ec_ad_day, 1)`). The orders-length interplay is resolved by `MX(anchor, ee_day)`, which reads as "count only as the length of the orders allows".
- **Claim-day windows and qualifiers (G2, G3, G4): closed.** No claim-day rule or binding remains.
- **"in force" vs status (G6): closed.** rf/rp say "active" and compute uses `F('status') == 'active'`. cc/cn/an "in force and the bill's due date has passed" is computed as `F('status') == 'active' and DAYS(eve, NOW) > 0`, consistent with the rule.
- **N8 (SOURCE-POLICY RED, new, check 2).** rp rule: "where the enrollment is active, only the installments whose period has already begun and that are unpaid are withheld". Compute: `rp_fee_due: XSUM('select', 'select_fee_ledger', 'amount', within_months=12, date_field='coverage_period_start', event_type='select_fee_charge')`. The 12-month cap has no rule basis. Example: an active Select enrollment with an unpaid installment whose period began 13 months ago is withheld by the rule and not by compute. A second gap is observation-level: in the applied tier the rule withholds "the installment charged with its application" while compute withholds `charged − paid` over all charges. Neither task world reaches either case (task 1's enrollment is applied, with one charge).
- O2 (still open as the reworker states): rf/rp "credits standing against bills that have a payment" vs compute, which removes only the latest bill's credits. A change credit on an older unpaid bill would be counted by compute. Not reached in either world.
- O9 (observation, new): al rule "where that month ended before coverage did" vs compute `DAYS(al_pay_eve, termination) < al_pay_days`. These disagree only when the termination date is the paid month's last day. Not reached.

### action_binding_and_uuids (revision_2)

- Each `(target_tool, computes)` is claimed once. PASS.
- **G1 docstring overlap: closed.** Every docstring is now plan-specific (TRS-only or TRR-only). **O4: closed.** `request_age_limit_refund_bb33162c` no longer refers to "the call that posted the credit". No sequence words.
- **N1 (check-3 defect, new).** Five uuid8s were carried from round-1 tools onto *different* tools:

  | uuid8 | round 1 | round 2 |
  |---|---|---|
  | 6cf5d114 | `cancel_remaining_month_premium` (loss-of-eligibility cancellation) | `post_orders_month_relief` (activation-on-orders relief) |
  | d66b5446 | `pay_premium_balance` (user payment) | `post_member_only_change_credit` (agent credit) |
  | 5d7ed849 | `refund_premium_credit` (agent) | `request_premium_refund` (user) |
  | 40bd3f0d | `pay_final_premium` (user payment) | `post_retiree_member_only_credit` (agent credit) |
  | bb33162c | `refund_age_limit_credit` (agent) | `request_age_limit_refund` (user) |

  Check 3 requires each uuid8 to be "independently newly generated for that tool and frozen with it, never reused across tools". I can show no score consequence, so by the demonstration threshold this is not a red light. It does fail the closing-checklist item "each task tool uses an independently generated, frozen uuid8", and it is recorded as a defect.

### prerequisite_graph (revision_2)

| blocked | → problem | kind | gate (exists) | form | resolved_by ✓ |
|---|---|---|---|---|---|
| rf | ec | state_gate | `premium_ledger.adjustment_reason` | state | `post_orders_start_credit_1b4c6b63` |
| rf | cc | value_input | `rf_unpaid_cr` ✓ | state | `post_member_only_change_credit_d66b5446` |
| rf | lm | value_input | `rf_unpaid_cr` ✓ | state | `post_orders_month_relief_6cf5d114` |
| lm | cc | value_input | `lm_off` ✓ | state | `post_member_only_change_credit_d66b5446` |
| rp | al | value_input | `rp_elig_sum` ✓ | state | `post_age_limit_credit_46c7df0c` |
| rp | an | value_input | `rp_elig_open` ✓ | state | `cancel_post_age_limit_premium_583248a8` |
| an | cn | value_input | `an_off` ✓ | state | `post_retiree_member_only_credit_40bd3f0d` |

ec, cc, al and cn have `[]`. The graph is acyclic and every `policy_source` is verbatim in its blocked rule. O5 is still open (the state_gate's gate names a column).

### prerequisite_sentences (revision_2)

- rf←ec: "A refund is not issued until every paid month the purchaser's active duty coverage overlapped carries the orders-start credit owed for those days." Connective "not … until". The waited-on state is `activation_on_orders` on a *paid* month's bill, and only ec writes that on a paid bill. PASS.
- rf←cc: "The refund owed is fixed only after the latest-billed month's bill carries the member-only change credit owed for the days its orders cancellation left standing." The state is a `coverage_type_change` credit on the latest TRS bill, and only cc writes it for TRS. PASS.
- rf←lm: "The refund owed is not fixed before the latest-billed month's bill carries the orders-month relief owed for its days of active duty coverage." The state is `activation_on_orders` on the unpaid latest bill for the overlap days; only lm writes it. Near-miss: a seeded orders cancellation on the same bill can carry the same reason for other days. PASS.
- lm←cc: "The orders-month relief on a bill is figured only after that bill carries the coverage-type change credit owed for the days its orders cancellation left standing." PASS.
- rp←al: "The refund owed on a Retired Reserve plan is fixed only after the bill of the month in which coverage ended carries the age-limit credit owed for its days after coverage ended." Loss-of-eligibility on that month's bill can be written only by al (an targets the latest-billed bill's unpaid part). PASS.
- rp←an: "… not fixed before the latest-billed month's bill carries the post-age-limit cancellation owed for its days after coverage ended." PASS.
- an←cn: "The post-age-limit cancellation of a bill is figured only after that bill carries the retiree member-only credit owed for its days before the retiree coverage began." PASS.
- No second wording, tool name or policy id appears in a rule. No undeclared cross-problem order. Depended-on rules do not restate the sentences.

### override_declarations (revision_2)

- Every extended departure from a base sentence is declared:
  - ec, lm, al and an supersede the termination-credit sentence, and `replaced_by` now restates the full formula (**O6 closed**).
  - lm, cc, cn and an supersede "A credit is posted only against a bill that has a payment posted against it."
  - cc and cn supersede the coverage-type proration sentence of `premium_coverage_type_rules`.
  - rf and rp supersede the refund sentence.
- **G8 closed**: no payment policy remains.
- Other base sentences (90-day change window, survivor/activation "unpaid future bills are cancelled by a credit", billing formula) are followed or not engaged.
- The ownership conflict N3 is with the scenario constitution's ownership statement, not with a base policy sentence, so it is recorded under the conflict scan.

### factor_ladders (revision_2)

| policy | declared (P/M) | structural verdict |
|---|---|---|
| ec | counted_from M (prime), orders_length P (prime), first_credited_day M (prime), change_settled P, change_spread M | all 5 survive; counted_from tiers 1-2 are multi-source (prime status ∧ prime date vs ledger month). Baseline (days after termination × billed/bill days) is honest: it is the base standard. |
| lm | counted_from M, orders_length P, first_relieved_day M, days_left_out P, change_settled P, change_spread M | all 6 survive. Baseline honest. |
| cc | first_day M, days_kept_out P, monthly_difference P, proration M, posted_now P | **monthly_difference struck (N4), proration struck (N5)**; 3 survive, below the 4 minimum. **Baseline is a straw man (N6).** |
| rf | months_figured M, change_paid_out P, orders_paid_out P, open_bill_credits P, held_for_orders P (prime), earlier_refunds P | all 6 survive; O7 (identical credit-type ladders) remains. held_for_orders tier 2 encodes a wait ("the whole refund waits until the orders are confirmed"): observation N9, not reached. |
| al | days_counted M, daily_amount P, change_settled P, change_spread M | ladders distinct, but **the baseline is a straw man, and the honest standard equals gold in task 1 (N6)**. |
| cn | first_day M, last_day M (select), difference P, proration M, posted_now P | **difference struck (N4), proration struck (N5), last_day struck (N7)**; 2 survive. **Baseline is a straw man (N6).** |
| an | days_counted M, daily_amount P, change_settled P, change_spread M, change_days M (select), posted_now P | 6 survive. change_days mirrors cn's split (see N7); kept, because its tiers are distinct arithmetic given the credit cn posts. Baseline "nothing" matches the base (no credit on an unpaid bill), so it is honest. |
| rp | refund_months M, change_paid P, eligibility_paid P, change_open P, eligibility_open P, select_fee P (select, multi-source tier 1: Select status ∧ Select fee ledger) | 6 survive. **G13 closed**: the scope no longer requires an ended plan, and no tier restates a gate. |

Round-1 factor findings: **G9** (monthly-amount collapse) is closed in its original six factors, but the same shape reappears as N4. **G10, G11 and G12** are closed: change_settled now selects three different treatments, claim-day ladders are gone, the other-month and payment ladders are gone, and the earlier-refund tier is a 12-month window. **G13** is closed.

### findings (revision_2)

Closure status of the round-1 findings:

| item | status | evidence |
|---|---|---|
| G1 | closed | plan-specific docstrings |
| G2–G4 | closed | claim factors removed |
| G5 | closed | §rule_compute_equivalence |
| G6 | closed | rf/rp "active"; posted_now consistent |
| G7 | closed | paid/unpaid split |
| G8 | closed | payment policies removed |
| G9 | closed as written; **regressed** as N4 | |
| G10–G13 | closed | |
| O1 | closed (zero clause removed) | |
| O3 | closed (explicit Retiree Group A/B) | |
| O4 | closed | |
| O6 | closed | |
| O2, O5, O7, O8 | open (as the reworker states) | |

New findings:

- **N1 (check-3 defect).** uuid8 reuse across tools (table above). Affects all tasks' tool identities.
- **N3: SOURCE-POLICY RED.** Refund ownership: the constitution says agent ("Recording ... refunds ... are agent service actions"), while the rf/rp rules and tools make it the purchaser's own act and let the purchaser book an issued refund entry. Same write, two owners. A premium administrator does not let a customer post their own refund. Bears on both tasks (their only owner=user write).
- **N4: SOURCE-FACTOR RED (two tiers select the same value).** cc `member_only_change_monthly_difference` and cn `retiree_member_only_difference`. Tier 1 is "the amount billed less that premium" when no credit stands, so the credit is 0. Tier 2 is "the amount billed less that premium and less the credit already standing". Tier 1 is therefore tier 2 with the credit at 0. Compute `(billed − tier) if (billed > tier and have == 0) else ((billed − tier − have) if billed > tier else 0)` ≡ `(billed − tier − have) if billed > tier else 0` in every world. Bears on both tasks.
- **N5: SOURCE-FACTOR RED (all tiers one formula).** cc `member_only_change_proration` and cn `retiree_member_only_proration`. Compute: `figured = (diff * days / bill_days) if mode != 'whole' else diff`. 'bill' and 'month' compute the same expression. 'whole' is selected only when `days ≥ bill_days`, and since days ≤ bill_days that means days = bill_days, where diff = diff·days/bill_days. The scored value is diff·days/bill_days whichever tier holds. The factor's only "weight" comes from substituting `'whole'` outside its own condition. Bears on both tasks.
- **N6: SOURCE-FACTOR RED (straw-man baseline).** cc, cn and al baselines read "Absent the rules below, the member-only change credit [retiree member-only credit] for such a month is nothing: no day of the month is counted, no monthly difference is taken, the whole monthly difference would be credited, nothing is posted now …" and "The age-limit credit is figured as nothing until the rules below place days …". The base standard methods give figures:
  - cc/cn: `premium_coverage_type_rules` credits the old/new difference for every month billed at the old rate.
  - al: `premium_termination_and_refund` credits "the days after the termination date at monthly_premium times those days over the days in the month".

  The cc/cn text is also self-contradictory: "no monthly difference is taken" and "the whole monthly difference would be credited" in one baseline. For al the honest standard method reproduces the gold-shaped value in task 1 (demonstrated in `1.md`). Bears on both tasks.
- **N7: SOURCE-FACTOR RED (unreal tier).** cn `retiree_member_only_last_day` tier 1: "where that enrollment is applied or active and took effect inside the latest-billed month, the credit counts up to the day before it took effect". The days of a member-only change credit on a Retired Reserve bill are bounded by Retired Reserve coverage, i.e. the plan's termination date. That bound is what the fall-through itself applies. Tier 1 instead bounds them by the start of a *different* plan, so it credits a member-only difference for days after the Retired Reserve plan had already ended. In task 1 these are November 1-4, after the 2026-10-08 termination. an's cancellation absorbs the rest of the bill, so the split is an accounting fiction: no administrator publishes a coverage-type change credit for days the plan did not cover. Bears on task 1.
- **N8: SOURCE-POLICY RED (check 2).** As above. No task consequence.
- N9 (observation): rf held_for_orders tier 2 is a wait encoded as a ladder outcome (`result: 0 if rf_hold == 'all'`). Not reached.
- N10 (observation): rp withholds the Select fee "before the refund is paid", but no write applies it to the Select fee ledger. The terminal state keeps the withheld amount as a TRR credit balance while the Select installment stays unpaid.

Task-level demonstrations (the decorative edge N2, factor bounds, near-miss) live in `0.md` and `1.md` under revision_2.

### closing_checklist (revision_2)

- Reveal at 2026-10-11T22:25:48Z, after both revision_2 task freezes and this file's revision_2 charter-global section. GT equals the blind derivation in both tasks (every write, owner, value and factor figure).
- Comparison verdicts are **not** all PASS:
  - task 0: SOURCE-POLICY RED (N3), SOURCE-CHAIN RED (N2), SOURCE-FACTOR RED (cc), unique solution PASS.
  - task 1: SOURCE-POLICY RED (N3), problem tree PASS, SOURCE-FACTOR RED (cn, al baseline, rp near-miss), unique solution PASS.
- Scopes: disjoint and complete over the eight extended policies.
- Trees: 3 prerequisite problems and 3 value_input edges each; the user write is the root; acyclic. Task 0's rf←ec edge is decorative.
- uuid8s: reused from round-1 tools onto different tools (N1). Fails the "independently generated" checklist item.
- Factors: cc and cn are below bounds. The cc, cn and al baselines are straw men; al's honest baseline equals gold. rp has no near-miss.
- Gates: the coordinator's round-2 snapshot is cited; the audited hashes are `b0390745…`/`6d99b516…`.
- **The difficulty does not pass the source-layer audit in round 2.**

---

## revision_3

### charter_global_frozen (revision_3)

- Re-audit round 3. Written before any round-3 task file was opened; `/tmp/erl55_premium/` was not read.
- Hashes, re-computed:
  - `premium.extended.yaml` `568e604b5a9acfe1a7213d0c2bb2b022f3de1b98c454c7a6a35d925b38dbd9af` (changed)
  - `task_tools.py` `3a583bdacab00eac2d979a558aeec2698dfb748d4a4e1518fd99f39afe317eb6` (changed)
  - views `a4193e7c…9c45` / `ee9b964f…813f` (changed)

  Every charter-global section is re-derived in full. The base section is unchanged against `blueprint/products/premium.yaml`.
- contamination_disclosure: round-1 and round-2 GT were read after their freezes (recorded above). No round-3 GT has been seen.
- Gate snapshot cited from the coordinator (all OK; traceability deferred).

Policy set (short names → tool, owner):
- TRS family:
  - **e** `premium_ext_early_duty_month_credit` → `post_early_duty_month_credit_9948ac5b` (agent)
  - **l** `premium_ext_family_adjustment_relief` → `relieve_family_adjustment_280360d9` (agent)
  - **t** `premium_ext_reserve_select_closing_adjustment` → `confirm_reserve_select_termination_4c6cc695` (**user**)
  - **r** `premium_ext_reserve_select_closing_refund` → `issue_reserve_select_refund_d64e8906` (agent)
- TRR family:
  - **k** `premium_ext_recall_termination_credit` → `confirm_retired_reserve_termination_c98977a4` (**user**)
  - **j** `premium_ext_recall_adjustment_relief` → `relieve_recall_adjustment_165573c8` (agent)
  - **d** `premium_ext_recall_month_relief` → `relieve_recall_month_993030c1` (agent)
  - **q** `premium_ext_retired_reserve_closing_refund` → `issue_retired_reserve_refund_cfa0a7d4` (agent)

### policy_conflict_scan (revision_3)

- Trees: r→{e, l, t} and q→{k, j, d}, all value_input, with no inner edges. Plan type separates the two families.
- Within each family, the writes target distinct bills:
  - e: paid monthly bill; l: that month's adjustment bill; t: latest monthly bill.
  - k: paid monthly bill; j: adjustment bill; d: later monthly bill.

  The user tools also set `status = terminated_by_request` and `termination_date`. Those are read by l/j (`*_ended`, posted-now tier), by e/k (fall-through anchors only) and by r/q. Whether the parallel writes interact is checked per world in each task file.
- **N3 (round 2), refund ownership: closed.** Refunds are agent-owned again, and confirming a termination is the purchaser's act, as `blueprint.yaml` states.
- **N3-R (SOURCE-POLICY RED, residual of N3).** The constitution says "Recording purchases, bills, payments, credits, refunds … are agent service actions on a verified caller, while confirming a termination of the plan is the purchaser's own act". The base event `premium_terminate_request` carries only `status` and `termination_date`. t and k instead say "…owes a closing-month adjustment [recall termination credit] …, posted against it as a termination-by-request credit **with the confirmation**". The user tools `confirm_*_termination` book that proration credit (an amount computed by the agent and read out) in the purchaser's own call (`_PlanLedger.credit_row(... "termination_by_request")`). Under the constitution, recording that credit is the agent's write. Under the charter and tools, it is the purchaser's. Same write, two owners.

### rule_compute_equivalence (revision_3)

- Spot-checked: every compute binding carries a verbatim `compute_basis`.
- e/k/t/d count-from, coverage-length and first-day tiers: the rule's conditions match compute gating. "Running more than 30 days from its effective date" is `DAYS(start, end) > 30`.
- e "and a later coverage month has already been billed" is computed as `e_later`.
- t "where a coverage-type adjustment bill stands for that month" is computed as `t_adj > 0`. The "paid" condition belongs only to e/k, consistent with each rule.
- The r/q scopes now remove the latest month by coverage month, so **O2 is closed**.
- O10 (observation, new): l/j rule "the plan is in force and the adjustment bill's due date has passed", while compute uses `l_eve`/`j_eve`, the due date of the *paid monthly* bill. They diverge only if the adjustment bill had a different due date. Not reached (both are 2026-09-30 in both worlds).
- O11 (observation, new): the `confirm_*_termination` docstrings restate the base termination-date rule ("the later of the date asked for in the pending request and the date that request was taken"). This is not a sequence hint and has no consequence.

### action_binding_and_uuids (revision_3)

- One `(target_tool, computes)` per policy. Docstrings are plan-specific (TRS-only or TRR-only). No sequence words. Bodies validate nothing.
- uuid8s: 9948ac5b, 280360d9, 4c6cc695, d64e8906, c98977a4, 165573c8, 993030c1, cfa0a7d4. None appears in the round-1 or round-2 modules; all are pairwise unrelated. **N1 closed.**

### prerequisite_graph / prerequisite_sentences (revision_3)

| blocked | → problem | kind | gate | sentence (verbatim in blocked rule) |
|---|---|---|---|---|
| r | e | value_input | `r_ord_sum` ✓ | "The closing refund on a Reserve Select plan is fixed only after the bill of the most recently paid month carries the early-duty month credit owed for its days of active duty coverage." |
| r | l | value_input | `r_rel_sum` ✓ | "… is not fixed before the coverage-type adjustment billed for the most recently paid month carries the family-adjustment relief owed for its days of active duty coverage." |
| r | t | value_input | `r_close_sum` ✓ | "… is fixed only after the latest-billed month's bill carries the closing-month adjustment owed with the purchaser's confirmed ending of the plan." |
| q | k | value_input | `q_term_sum` ✓ | "… the bill of the most recently paid month carries the recall termination credit owed with the purchaser's confirmed ending of the plan." |
| q | j | value_input | `q_rel_sum` ✓ | "… the coverage-type adjustment billed for the most recently paid month carries the recall adjustment relief …" |
| q | d | value_input | `q_wd_sum` ✓ | "… the latest-billed month's monthly bill, where that month is later than the most recently paid month, carries the recall month relief owed for it." |

- All edges are state form with ordering connectives. Each state is written by exactly one policy of the difficulty, distinguished by bill (paid monthly bill vs adjustment bill vs latest/later monthly bill) and reason (activation_on_orders vs termination_by_request).
- No tool name or policy id appears in a rule, and no undeclared cross-problem order exists. The graph is acyclic. No state_gate remains, so **O5 is closed**.

### override_declarations (revision_3)

Declared:
- e, t and k supersede the termination-credit sentence.
- l, t, j and d supersede the paid-bill sentence.
- r and q supersede the refund sentence.

Followed:
- t and k follow `termination_effective_rule` ("later of the requested date and the request date").
- e and k post only on paid bills.

Engaged without conflict:
- `premium_plan_eligibility` / `premium_survivor_and_activation` (plan ends the day before an activation of more than 30 days). In both worlds the activation is still in the future, and the requested termination falls on or before it.

### factor_ladders (revision_3)

| policy | declared (P/M) | structural verdict |
|---|---|---|
| e | counted_from M (prime, multi-source), coverage_length P (prime), first_day M (prime), change_settled P, change_spread M, change_days M | 6 survive. Baseline (days after termination × billed/days) is the base standard, so it is honest. |
| l | counted_from M, coverage_length P, first_day M, daily_amount P, posted_now P | 5 survive. Baseline "nothing" is honest: the base credits no day before the termination date and nothing on an unpaid bill. |
| t | counted_from M, coverage_length P, first_day M, daily_amount P, change P | 5 survive. Baseline (days after termination × tier premium/days) is the base standard. |
| r | months M, change_credits P, early_duty_credits P, adjustment_relief P, closing_adjustment P, earlier_refunds P | 6 survive the ladder tests. **Baseline is dishonest: N11.** O7 is open. |
| k | mirror of e | 6 survive; baseline honest. |
| j | mirror of l | 5 survive; baseline honest. |
| d | counted_from M, coverage_length P, first_day M, change P | **coverage_length struck (N12)**; 3 survive, below 4. Baseline "nothing" is honest (no credit on an unpaid bill). |
| q | mirror of r (months, change_credits, termination_credit, adjustment_relief, recall_month_relief, earlier_refunds) | 6 survive the ladder tests. **Baseline is dishonest: N11.** |

Round-2 factor findings:
- **N4, N5, N7 closed**: the member-only difference, proration and Select last-day factors are gone.
- **N6 closed for e/t/k/l/j/d**: their baselines are now the base standard, or "nothing" where the base indeed gives nothing.
- **N8 closed**: no Select fee factor remains.

### findings (revision_3)

Closure status of round-2 findings:

| item | status |
|---|---|
| N1 | closed |
| N2 | closed (no state_gate; every edge is value_input; demonstrated per task) |
| N3 | closed as stated (refund owner); residual **N3-R** |
| N4, N5, N7, N8, N9, N10 | closed |
| N6 | closed for the credit policies; **reappears for the refund baselines as N11** |
| O2, O5 | closed |
| O7, O8 | open |

New findings:

- **N3-R: SOURCE-POLICY RED.** As stated under §policy_conflict_scan. Bears on both tasks: t is task 0's only user write and k is task 1's.
- **N11: SOURCE-FACTOR RED (dishonest baseline; honest standard reproduces gold).**
  - Base `premium_termination_and_refund`: "A credit balance is refunded through the original payment method within premium_refund_issue_days."
  - The r/q baselines instead read "Absent the rules below, the closing refund … is what the latest-billed month is overpaid … credits of every kind are carried forward to future bills and none is paid out, and no refund already issued is taken off". On an ended plan there is no future bill, so this is a zero where the standard method gives a figure.
  - Wherever the plan has ended, every r/q ladder takes its "in full" / "every refund" tier, and the scored refund equals the plan's credit balance, which is the standard method's figure. The factors bear weight only against the straw man.
  - Demonstrated in both tasks: task 0 refund 53.28 = −balance; task 1 refund 305.31 = −balance.
  - Relation to earlier revisions: the identity also held in revision_1 (rf 15.99 = −balance, rp 1049.86 = −balance) and **I did not report it then**, which was an auditor miss. In revision_2 the hold and fee factors broke the identity (48.68 vs 56.84; 1252.59 vs 1285.59). Round 3 removed those factors, so it holds again.
- **N12: SOURCE-FACTOR RED (two tiers select the same value).** d `recall_month_relief_coverage_length`: tier 2 "it shows its coverage running 30 days or fewer → no day of the recall month relief counts", tier 3 "otherwise → no day of the recall month relief counts". The rule prose says the same: "where it shows its coverage running 30 days or fewer, no day counts; otherwise no day counts". Bears on task 1.
- Near-miss records, as before, are per task (`0.md` / `1.md`).

### closing_checklist (revision_3)

- The charter-global section of this revision was appended at 01:41:59Z, the task freezes at 01:42:47Z, and the reveal happened at 01:42:52Z. GT equals the blind derivation in both tasks (every write, owner, value, edge and factor figure).
- Verdicts:
  - task 0: SOURCE-POLICY RED (N3-R); problem tree PASS; SOURCE-FACTOR RED (N11, no near-miss in r); unique solution PASS.
  - task 1: SOURCE-POLICY RED (N3-R); problem tree PASS; SOURCE-FACTOR RED (N12, N11, no near-miss in q); unique solution PASS.
- Scopes: disjoint and complete.
- Trees: 3 prerequisite problems and 3 weight-bearing value_input edges each, with a user write. Acyclic, and order-free among the parallel prerequisites (all 6 orders checked in each task).
- uuid8s: fresh (N1 closed).
- Open observations: O7, O8, O10, O11.
- Gates: the coordinator's round-3 snapshot is cited; audited hashes `568e604b…` / `3a583bda…`.
- **The difficulty does not pass the source-layer audit in round 3.** What remains:
  - N3-R: credit booked in the purchaser's write.
  - N11: refund baselines are straw men, and the base standard equals gold.
  - N12: d's ladder has a duplicate tier.
  - No near-miss in either refund computation.

---

## revision_4

### charter_global_frozen (revision_4)

- Re-audit round 4. Written before any round-4 task file was opened; `/tmp/erl55_premium/` was not read.
- Hashes, re-computed:
  - `premium.extended.yaml` `5d6c5eae8a7dddaa939dd99792b7e30fda8b388cac5f3c388a926a00e65d7d71` (changed)
  - `task_tools.py` `79e67859a7f47f6147c00e9fefc4e868c8a148ea6ff23ebb2c60b755681c07c8` (changed)
  - views `4ca4a19a…5520` / `76388dc4…f67e` (changed)

  Every charter-global section is re-derived. The base section is unchanged.
- I diffed each policy against round 3:
  - e is byte-identical.
  - l and j changed only their posted-now tier (the due-date condition was dropped), which closes O10.
  - d was rewritten.
  - n, c, p and g are new.
- contamination_disclosure: GT from rounds 1–3 was seen after their freezes. Nothing from round 4 has been seen.
- Gate snapshot cited from the coordinator (all OK; traceability deferred).

Policy set (short names → tool, owner):
- TRS family:
  - **e** `premium_ext_early_duty_month_credit` → `post_early_duty_month_credit_9948ac5b` (agent)
  - **l** `premium_ext_family_adjustment_relief` → `relieve_family_adjustment_280360d9` (agent)
  - **n** `premium_ext_later_month_family_relief` → `relieve_later_month_family_adjustment_600a6ce9` (agent)
  - **c** `premium_ext_reserve_select_closing_reconciliation` → `confirm_reserve_select_ending_f251f30d` (**user, root**)
- TRR family:
  - **p** `premium_ext_recall_paid_month_credit` → `post_recall_paid_month_credit_948d1b7a` (agent)
  - **j** `premium_ext_recall_adjustment_relief` → `relieve_recall_adjustment_165573c8` (agent)
  - **d** `premium_ext_recall_month_relief` → `relieve_recall_later_month_3979698d` (agent)
  - **g** `premium_ext_retired_reserve_closing_reconciliation` → `confirm_retired_reserve_ending_efdb5596` (**user, root**)

### policy_conflict_scan (revision_4)

- Trees: c→{e, l, n} and g→{p, j, d}, all value_input; the leaves have no prerequisites.
- Each leaf writes an activation-on-orders credit on a distinct bill:
  - e: the paid month's monthly bill. l: that month's adjustment bill. n: the later month's adjustment bill.
  - p: the paid month's monthly bill. j: that month's adjustment bill. d: the later month's monthly bill.
- The root takes in every bill of the closing period and subtracts the activation credits already standing on each. The root and the leaves therefore never credit the same day twice.
- **N3-R, ruled now: observation (O16), downgraded from SOURCE-POLICY RED.**
  - Charter side. c/g say: "The Reserve Select closing reconciliation is the consequence of the purchaser's own confirmation and is booked by it, not recorded afterwards as a separate agent service action." The base policy `premium_termination_and_refund` groups `premium_terminate_request` with `premium_proration_credit` in one subject. The lifecycle says "the purchaser's confirmation ends coverage".
  - Contrary side. The only text saying otherwise is the descriptive difficulty summary in `blueprint.yaml` ("Recording … credits … are agent service actions"). It is neither a policy nor on the rollout surface.
  - Since the rule now states the departure outright, no reader of the policy surface reaches a second owner. My revision_3 red light was against a charter that was silent on the point.
  - The constitution sentence still literally reads otherwise; I record that as an observation.
- **O12 (observation, new).** c/g's first `overwrite` names, as superseded, base "A purchaser may end the plan at any time, but only by their own confirmation: the agent records the request as an intake and the purchaser confirms it." Booking a credit with the confirmation does not contradict that sentence. Declaring it superseded removes "may end the plan at any time" from the merged semantics of these policies, and the `replaced_by` does not restore it. The rest of each rule still conditions everything on "the purchaser … confirms in person", so the merged semantics stays unique and no consequence follows.

### rule_compute_equivalence (revision_4)

- Spot-checked: every binding carries a verbatim `compute_basis`.
- d: "where it shows its coverage running 30 days or fewer, the relief counts only through the last day that coverage runs" is `d_last = MN(d_mdays, DAYS(d_eve, d_ad_end))`; ">30 days → through the last day of the month" is `d_mdays`; "otherwise no day counts" is 0. These match.
- c/g each bill: monthly bills at amount/days, adjustments at the unpaid part per day, change settled with spread and days, and activation credits taken off with spread and days. Each matches its rule sentence.
- O13 (observation): c/g's rule ends "…rounded to the cent and never less than zero" for the sum. Compute floors and rounds each bill (`c_m1_val = MX(0, RND(…))`) and then the sum. The two differ only if one bill's contribution were negative or rounding accumulated across bills. Neither happens on the gold path of either world (checked in the task files).
- O14 (observation, the reworker's flagged point): c's baseline rule ("days of the month containing the termination date after the termination date × the monthly premium of the tier the plan carries ÷ days, rounded once") gives 261.58 in task 0. Compute's all-baseline substitution, rounded per bill, gives 261.57. Both are definite and both differ from gold, so this is a cent-level inconsistency between a baseline rule and its compute, with no score consequence.
- O15 (observation): the root tool's `coverage_days` ("the number of days of that month the closing reconciliation counts") is not defined by any rule sentence, and compute does not produce it. In both worlds every bill of the latest month counts all 30 of its days, so the reading is unique there (`0.md`/`1.md`). A world where the later month's bills counted different day ranges would leave this argument undetermined.
- O10: closed. O11: closed (the confirm-tool docstrings no longer restate the date rule).

### action_binding_and_uuids (revision_4)

- One `(target_tool, computes)` per policy.
- uuid8s: 9948ac5b, 280360d9 and 165573c8 are kept on the same tools as round 3. 600a6ce9, f251f30d, 948d1b7a, 3979698d and efdb5596 are new. No cross-tool reuse. Entry-id prefixes are distinct (pde_/pfa_/pfl_/pcr_/prp_/pra_/prl_/pcq_).
- Docstrings are plan- and bill-specific with no sequence words. Bodies validate nothing.

### prerequisite_graph / prerequisite_sentences (revision_4)

| blocked | → problem | kind | gate ✓ | sentence (verbatim in the root rule) |
|---|---|---|---|---|
| c | e | value_input | `c_m1_act` | "The Reserve Select closing reconciliation is figured only after the monthly bill of the most recently paid month carries the early-duty month credit owed for its days of active duty coverage." |
| c | l | value_input | `c_a1_act` | "… is not figured before the coverage-type adjustment billed for the most recently paid month carries the family-adjustment relief owed …" |
| c | n | value_input | `c_a2_act` | "… is figured only after the coverage-type adjustment billed for a later latest-billed month carries the later-month family relief owed …" |
| g | p | value_input | `g_m1_act` | mirror (recall paid-month credit) |
| g | j | value_input | `g_a1_act` | mirror (recall adjustment relief) |
| g | d | value_input | `g_a2…`/monthly | "… only after the monthly bill of a later latest-billed month carries the recall month relief owed …" |

All edges are state form. Each waited-on state (an activation_on_orders credit on a named bill) is written by exactly one leaf. The graph is acyclic, with no undeclared order and no tool name or policy id in any rule.

### override_declarations (revision_4)

- Termination-credit sentence: superseded by e, p, c and g (declared).
- Paid-bill sentence: superseded by l, n, j, d, c and g (declared).
- O12 as above.
- Refund sentence: no longer engaged, since there is no refund policy.
- Base "A credit balance is refunded through the original payment method within premium_refund_issue_days" stays in force. After the roots, both plans hold a credit balance (task files). No tool exists for it and no persona asks for it, so it is a within-30-days follow-up outside the scored solution (O17, observation).

### factor_ladders (revision_4)

| policy | declared (P/M) | verdict |
|---|---|---|
| e, p | counted_from M (prime, multi-source), coverage_length P, first_day M, change_settled P, change_spread M, change_days M | 6 survive; baseline = base standard |
| l, j, n | counted_from M, coverage_length P, first_day M, daily_amount P, posted_now P | 5 survive; baseline "nothing" = base (no credit on an unpaid bill) |
| d | counted_from M, coverage_length P, first_day M, daily_amount P | 4 survive (2P/2M). **N12 closed**: the tiers are now distinct (to month end / to the end of coverage / none). Baseline "nothing" = base. |
| c, g | counted_from M, coverage_length P, first_day M, change_settled P, change_days M, activation_credits P | 6 survive. Baseline = base termination credit (honest). **N11 closed**: no refund root remains. |

### findings (revision_4)

| round-3 item | status |
|---|---|
| N3-R | ruled observation (O16), with reasons above |
| N11 | closed |
| N12 | closed |
| O10, O11 | closed |
| refund near-miss | moot (no refund root); the roots' near-misses are checked per task |
| O7, O8 | open (the reworker says so; O7's refund factors are now gone, so O7 is moot) |

New observations: O12–O17, as above. No new SOURCE red light at charter level.

### closing_checklist (revision_4)

- Order on disk: this revision's charter-global section at 04:55:04Z, the task freezes at 04:55:45Z, the reveal at 04:55:50Z. GT equals the blind derivation in both tasks: every write, owner, value, argument (including the root's coverage_days 30 and termination dates), edge, skip figure and factor figure.
- Per-task verdicts: task 0 and task 1 are each PASS on all four relationships (policy self-consistency, problem tree, factors, unique solution).
- Coverage and scope: the eight extended policies are covered, and the two scopes are disjoint across whole trees.
- Tools: one per policy; uuid8s fresh or kept on the same tool; no reuse across tools.
- Trees: each has 3 prerequisite problems, 3 weight-bearing value_input edges and a user-owned root. Acyclic. Order-free among the leaves (all 6 orders checked per task).
- Factors: every computation has 4–6 factors with ≥2 parameter and ≥1 method. Each task has a multi-source factor and a cross-difficulty (prime) factor, the latter reading seeded rows. Every baseline is honest (the base method or the base's "nothing") and differs from gold. Every declared factor bears weight. Every computation has a near-miss.
- Gates: the coordinator's round-4 snapshot is cited, on hashes `5d6c5eae…` / `79e67859…`.
- Open observations, none bearing on a score: O8, O12–O18.
- **The difficulty passes the source-layer audit in round 4.**

---

## revision_5

### charter_global_frozen (revision_5)

- Re-audit round 5, after the KB render surfaced four source items. Written before any round-5 task file was opened; `/tmp/erl55_premium/` was not read.
- Hashes, re-computed:
  - `premium.extended.yaml` `c5ff4c192c7dba2b3c5a640bf8cf0ce57d4fb33b86f92c8feb5cceda758f44c9` (changed)
  - `task_tools.py` `79e67859…07c8` (unchanged; its revision_4 conclusions are carried forward on that hash)
  - views `4ca4a19a…5520` / `76388dc4…f67e` (unchanged)
- The charter changed, so its sections are re-derived below. Method: a policy-by-policy diff against the revision_4 charter (`/tmp/erl55_audit_premium/r4` vs `r5`), plus a programmatic re-check that every `compute_basis` entry, `baseline.rule`, `overwrite.replaced_by` and `prerequisite.policy_source` is verbatim in its rule. **All eight policies pass.**
- The diff shows **no change to any `compute` binding, factor `decides`/`bindings`/`baseline` substitution or prerequisite edge**. The only changes are:
  - rule prose;
  - `baseline.rule` text, and the reconciliation baselines' `params` (`[monthly_premium]` → `[]`);
  - the `overwrite.replaced_by` sentences;
  - one ladder rung (`coverage_length` tier 2 of c and g: "no active duty day counts" → "no day counts").
- contamination_disclosure: GT from rounds 1–4 was seen after their freezes. No round-5 task file has been seen.
- Gate snapshot cited (all OK including TRACEABILITY; `validate_scenario` VALID).

### verification of the four render-surfaced items

1. **Reconciliation baseline (c, g).** New `baseline.rule`: "…standard figure is the termination credit taken bill by bill: for each bill taken in, the days of its period after the termination date, multiplied by the bill's daily amount, with nothing taken off for credits already standing; each bill's figure is rounded to the cent and the figures are added."
   - Check against compute: the factor baselines put every bill's anchor/coverage-length at the termination day (`c_t1`/`c_t2`), set the first day to the day after, keep each bill's own daily amount (`c_m*_rate` amount/days; `c_a*_rate` unpaid part/days), set change and activation take-offs to 0, and round per bill (`c_*_val`). The text matches compute exactly.
   - Values: task 0 gives 26×61.17/30 + 26×240.65/30 = 53.01 + 208.56 = **261.57**, which equals the compute all-baseline. Task 1 gives 21×614.07/30 + 21×857.66/30 = 429.85 + 600.36 = **1030.21**, also equal.
   - The clash with "amount billed divided by the days the bill covers" is gone: the rule's daily-amount sentence and the baseline now use the same quantity.
   - **O14 closed.**
   - Honest-baseline judgement: this is no longer the base sentence verbatim (tier premium, paid bills only). It is a complete standard method (credit back each bill's days after the termination date at that bill's own rate, nothing netted) that a premium administrator would apply. It is neither a straw-man zero nor gold under another name, and it is stated in the rule in full.
   - Every c/g factor's fall-through equals it (termination date, day after, nothing taken off, applies to no day).
   - A stricter reading of the base (credit only paid bills at the tier premium) gives 0 in both worlds, because the November bills are unpaid. That also differs from gold (61.17 / 857.66), so no reading of an honest baseline reproduces gold.
2. **Relief baselines (l, n, j, d).**
   - "Absent the rules below" is gone from every rule (checked).
   - New text, for example l: "The family-adjustment relief's standard figure is nothing: the base posts no credit against an unpaid bill, so only days after the plan's termination date are counted, nothing is relieved for them per day, nothing is posted now, and the result is rounded to the cent."
   - This matches the compute baselines: anchor/ee at the termination day, first day = from+1, rate 0, post 0. With no termination date on the plan at handling time, compute counts no day, consistent with "only days after the plan's termination date".
   - d: "…so no day of the latest-billed month is counted, nothing is withdrawn per day" matches `d_anchor = d_mdays`, `d_last = 0`, rate 0.
   - Honest per base: the base posts no credit against an unpaid bill.
3. **Rung wording.** c/g `coverage_length` tier 2 now reads "no day counts", matching the rule ("where it shows its coverage running 30 days or fewer, no day counts") and compute (`ee_day = days+1`).
4. **Scoped overwrites.** Every `replaced_by` now names its own scope and is a verbatim rule sentence:
   - e/p: "For the most recently paid month of a TRICARE Reserve Select [Retired Reserve] plan whose purchaser came under active duty TRICARE coverage in it, the … credit takes the place of the termination credit for that month's bill; every other paid month, and every plan of another kind, keeps the termination credit."
   - c/g: "…takes the place of the termination credit for the bills of the closing period; an ending for loss of eligibility or the purchaser's death, and every plan of another kind, keeps the termination credit."
   - Paid-bill overwrites: "The paid-bill condition for credits is set aside only for a …; every other credit on the plan still needs a payment posted against its bill."

   TRICARE Young Adult termination credits and base "A termination for loss of eligibility or the purchaser's death is credited the same way" therefore keep their basis, so the render item is closed.
   - **O12 also closed.** c/g's first overwrite now reads "For a TRICARE Reserve Select [Retired Reserve] plan, the purchaser ends the plan only by confirming in person a request the agent recorded as an intake, and the … closing reconciliation is the consequence of that confirmation …". This restores the intake-and-confirmation semantics. Residual nit, observation only: the words "at any time" are not restated. The base's next sentence (termination date "never retroactively") is not superseded, so no consequence follows.

### further rule-vs-compute sweep (revision_5)

- Sentence by sentence over the changed prose:
  - the scoped-replacement sentences (descriptive scope, no quantity);
  - the "standard figure" sentences (checked above);
  - the reconciliation's "has as its daily amount" rewording (same quantities as `c_m*_rate`/`c_a*_rate`).

  Nothing new diverges.
- Still standing from revision_4: **O13** (the final "rounded … never less than zero" on the sum vs compute's per-bill floor and round; no consequence on either world, since the October residue is 0.001 in task 0 and every per-bill figure is ≥ 0). **O15** (the root's `coverage_days` is defined by no rule sentence; 30 under every reading in both worlds).
- Carried forward on the unchanged tool hash: `action_binding_and_uuids` (revision_4).
- Carried forward, since edges, gates, sentences and compute are unchanged: `prerequisite_graph` / `prerequisite_sentences` (revision_4); every sentence re-verified verbatim above.
- `factor_ladders`: counts, labels and tiers unchanged (e/p 6, l/j/n 5, d 4, c/g 6), with the c/g tier-2 rung text fixed. Baselines are honest (above).

### findings (revision_5)

- Render items 1–4: closed (verified above). O12 and O14 closed.
- Open observations: O8, O13, O15, O16, O17, O18.
- **No new defect, and no SOURCE red light at charter level.**

### closing_checklist (revision_5)

- Order on disk: this revision's charter-global section at 05:57:44Z; the task freezes, then the reveal after 05:57:56Z. GT equals the blind derivation in both tasks: every write, owner, argument, edge and factor figure.
- Per-task verdicts: task 0 and task 1 are each PASS on all four relationships.
- The four render-surfaced items are verified closed:
  1. The reconciliation baseline is now the bill-by-bill standard; it equals compute and is honest.
  2. The relief baselines are reworded and match compute.
  3. The coverage-length rung is aligned with rule and compute.
  4. The overwrites are scoped, with TYA and loss-of-eligibility/death keeping the base termination credit.
- No scored value changed, no new defect, nothing regressed.
- Gates: the coordinator's round-5 snapshot (all OK including TRACEABILITY; scenario VALID) on hashes `c5ff4c19…` / `79e67859…`.
- Open observations, none bearing on a score: O8, O13, O15, O16, O17, O18.
- **The difficulty passes the source-layer audit in round 5.**
