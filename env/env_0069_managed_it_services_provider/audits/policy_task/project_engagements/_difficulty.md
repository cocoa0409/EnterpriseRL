# Policy-task audit — project_engagements / charter-global

## revision_1

## charter_global_frozen
- Freeze time: 2026-10-18T03:35:07Z (file mtime; written before any reveal). Auditor: erl-task-policy-audit (independent of the instantiator).
- Frozen inputs: `tasks/project_engagements/project.extended.yaml` sha256=570c30eb7290434560335d923e0192bdac82aefbc3bf3c2037c3537727064f06; `tasks/project_engagements/task_tools.py` sha256=7ebbb5aff4f0309789206142f7e0454cebc7e48310cb2714452818363c9a7802 (both re-hashed on disk, match the brief).
- Read for this section: `blueprint/products/project.yaml` (and managed/hardware/timebank charters for cross-product pricing), `blueprint/db_schema.json`, `blueprint/share_tools.py`, the extended charter, `task_tools.py`, `audits/render_source/XF_recipe.md`, the DSL semantics in `erl-task-instantiate/scripts/check_compute.py` (MONTHS / `_within` / LATEST / CFIELD / RND).
- Masked and not read when this section was written: every task's `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, db_closure fields; `tasks/project_engagements/plan.md`, `worklog.md`; sibling audits. Nothing in this section is derived from a revealed GT.
- Entry conditions (Step 0): the brief carries the gate snapshot (2026-10-18T03:19:24; check_extended, check_task_tools, replay_tasks --check, check_solvability, check_compute, check_grounding, check_cross_fire all rc=0; check_traceability deferred until the KB is published) and the two view hashes (0.view.json 7e59ae4f…, 1.view.json 6916237…, both re-hashed and matching). Entry conditions complete; check_traceability deferral recorded as given.
- Isolation note: one early repo-wide grep for DSL definitions (`grep -rn within_months|CFIELD|XSUM|def .*months --include=*.py .`) printed ~20 one-line hits from other scenarios' `task_tools.py` files (function signature lines only; no task JSON, no GT of this scenario). Nothing from them was used. Recorded for transparency; it does not touch this difficulty's GT.

Base copy: `diff` of extended lines 1–1078 against `blueprint/products/project.yaml` differs only by one trailing blank line — verbatim.

### policy_conflict_scan
Extended policies (6): `project_ext_sow_signature_rate_lock` (sign SOW, user), `project_ext_signature_deposit` (deposit, agent), `project_ext_milestone_billing` (milestone invoice, agent), `project_ext_restart_repricing` (sign restart CO, user), `project_ext_restart_change_order_fee` (CO fee, agent), `project_ext_restart_remobilization` (remob fee, agent).
- Overlapping subjects: each extended policy has a distinct subject event and target tool. Two policies overwrite clauses of the same base policy `project_schedule_and_holds` (restart_repricing: the max_client_hold_days termination/re-price clause; remobilization: the remobilization-fee clause) — different clauses, so XF#17 does not apply.
- Triggers/eligibility/time anchors: inherited base eligibilities hold unchanged (SOW validity, milestone billable status, change order signed, verified contact). The "restart" scope is defined consistently in restart_repricing, CO fee and remobilization ("fixed-fee engagement resumed after a client-caused hold longer than max_client_hold_days").
- Cross-category reads: managed (all six policies except milestone reads only tier), hardware (deposit), timebank (rate lock). All read the client's own records; `managed` max_per_customer=1 for open statuses, so `CFIELD(..., status='active')` is single-valued.
- Terminal states: see finding C15 — the restart CO signature leaves `project_engagements.contract_value_usd` / `change_order_count` untouched although an inherited base sentence moves them.
- Scope coverage: the prerequisite graph splits into two components {rate_lock ← deposit} and {milestone ← restart ← CO fee ← remob}. With M=2, one component per task covers all six policies exactly once; disjointness/completeness is confirmed against `charter_scope` only after reveal (task files).

### rule_compute_equivalence
Mechanical sweep (scratch `sweep.py`): every `compute_basis` quote normalised and searched in its own rule.
- rate_lock, deposit, milestone, restart, remobilization: every quote verbatim; every compute branch has a rule sentence and every rule tier a compute branch. DSL conventions match the rules: `MONTHS()` counts a whole month only on the same day number of a later month (= the rules' "a whole month being complete only on the same day number of a later month"); `_within` keeps rows with 0 ≤ MONTHS(posted, today) < N (= "fewer than N whole months separate"); prepaid "rounded down to one decimal place" = `int(x*10)/10` on a non-negative value; milestone same-day tie stated and implemented through MAX(milestone_number).
- CO fee: **three quotes are not in the rule** — `signed_at`, `since_resume`, `window_factor` quote "a restart change order **signed** window_short_days or fewer calendar days after the engagement's resumed_date …", while the rule reads "a restart change order **registered** window_short_days or fewer …". Finding C2.
- CO fee `delta_abs`/`signed_at`: rule "the change order most recently **signed** on the engagement" vs compute `LATEST(..., date_field='created_at', request_status='signed')` (most recently *registered*; `project_change_orders` has no signature timestamp). Finding C3.
- Remobilization `co_fee_net`: `LATEST(project_billing, posted_date, event_type=project_change_order_fee)` on a date-only field; the rule states no same-day tie. Finding C4.
- Rounding: every rule's "rounded half up … only at the end" sits at the final `RND`; RND is Python `round` (not strictly half-up on binary floats) — DSL-wide, observation O4.

### action_binding_and_uuids
- `(target_tool, computes)` pairs are pairwise distinct: (sign_statement_of_work_96bc6bf1, rate_discount_pct), (post_deposit_invoice_06d795b1, amount_usd), (post_milestone_invoice_79b8c922, amount_usd), (sign_restart_change_order_602c3012, value_delta_usd), (post_change_order_fee_93724a4c, amount_usd), (post_remobilization_fee_508d4151, amount_usd).
- uuid8s 96bc6bf1, 06d795b1, 79b8c922, 602c3012, 93724a4c, 508d4151: distinct, no shared prefix, no sequence; no evidence of batch derivation.
- No factor id is a substring of any tool name (mechanical check, XF#7 clean).
- Tool bodies validate nothing (no status, signature or prerequisite check) — they write and confirm.
- Docstrings: no tool named, no sequence position. "after a pause" in `sign_restart_change_order` / `post_remobilization_fee` describes the business event, not write order (observation O1). `sign_statement_of_work` carries a concrete value "(0.0 when no discount is locked)" and claims "the value is stored rounded half up to 1 decimal place" while the body uses Python `round` — finding C9 (XF#19).
- `sign_restart_change_order_602c3012` updates only `project_change_orders` (status, value_delta_usd) — finding C15.

### prerequisite_graph
| blocked policy | problem | kind/gate | form | resolved_by | sentence verbatim in own rule |
|---|---|---|---|---|---|
| signature_deposit | sow_signature_rate_lock | value_input / est_fees (exists) | state | sign_statement_of_work_96bc6bf1 (= that policy's target_tool) | yes |
| restart_repricing | milestone_billing | value_input / remaining_value (exists) | state | post_milestone_invoice_79b8c922 | yes |
| restart_change_order_fee | restart_repricing | value_input / delta_abs (exists) | state | sign_restart_change_order_602c3012 | yes |
| restart_remobilization | restart_change_order_fee | value_input / co_fee_net (exists) | state | post_change_order_fee_93724a4c | yes |
- `prerequisite` filled everywhere (`[]` on rate_lock and milestone); every `problem` is an extended id, none self, none base; graph acyclic (two chains). No `fallback_reason` needed (all state form). No authoring-viewpoint wording.
- `condition` vs sentence: deposit edge adds "status is signed" (implied by the signature date — no change of strength). **CO-fee edge adds "registered on or after the engagement's resumed_date"; remobilization edge adds "posted on or after resumed_date"** — neither is in the sentence. Finding C14.

### prerequisite_sentences
1. Deposit: "The deposit of a time-and-materials statement of work is fixed only after the engagement record carries the client's signature date and the rate discount locked at signature." — ordering connective "only after"; record-visible state (signed_date, rate_discount_pct per the schema's own meaning "labor rate discount locked at signature"); no tool/id/snake_case. One write brings it about: the only tool writing `signed_date`/`rate_discount_pct` is sign_statement_of_work, whose own rule (rate_lock) figures the locked discount. Single reading.
2. Restart: "The value of a restart re-pricing is fixed only after the engagement's billing carries a milestone invoice for every milestone recorded complete." — state; only `post_milestone_invoice` writes milestone invoices; milestone_billing's rule names the milestone invoiced. Single reading.
3. CO fee: "The administration fee of a restart change order is fixed only after the engagement's change orders carry that change order signed by the client." — state; only `sign_restart_change_order` sets a CO to signed; restart_repricing's rule figures its value. Single reading.
4. Remobilization: "The remobilization fee of such a resumption is not invoiced until the engagement's billing carries the administration fee owed on the change order that re-priced the restart." — "not … until"; state; only `post_change_order_fee` writes CO fees. **Second reading when the restart CO's fee is zero**: the CO fee rule says "a fee of zero is not posted", so the billing can never carry it — reading A: the remobilization fee is never invoiced; reading B: nothing is owed so the wait is vacuous (which the remobilization rule's "and nothing otherwise" presupposes). Finding C5 (member of XF#13 class).
- No depended-on rule restates a sentence; no rule carries a second wording or another problem's tool/id. No undeclared cross-problem order found in any extended rule. Base sentences with an order ("On signature the deposit is invoiced") ground no edge — the extended rules carry their own sentences.

### override_declarations
Sentence-by-sentence against each `base_policy_refs` entry:
- rate_lock ← classification_and_pricing: the issue-date rate_discount sentence is overwritten, scoped (T&M signed under this policy; fixed fee keeps issue-date figure) — XF#16 satisfied. Other sentences followed. ← signature_deposit_and_kickoff: validity window followed; deposit sentence overwritten by deposit policy. ← client_signed_changes: client e-signs (owner=user) and verification inherited; "the service desk registers each as a change request … pending the authorized contact's e-signature" has no SOW-signature change type in the schema enum and no registration tool (observation O2).
- deposit ← signature_deposit_and_kickoff: deposit sentence overwritten, scoped (T&M only; fixed fee restated). Kickoff sentences untouched. ← classification: NTE-as-contract-value followed.
- milestone ← fixed_fee_billing: milestone sentence overwritten for every milestone invoice (no out-of-scope remainder). "On acceptance the final invoice bills contract_value_usd minus everything already billed … so that a fixed fee is billed exactly once in total; the holdback is final_holdback_pct percent" is not overwritten; combined with this policy's "credit … taken off" schedules and its cumulative true-up "less everything already billed", every credit granted is billed back later — finding C13. ← change_orders: followed.
- restart_repricing ← schedule_and_holds: termination/re-price clause overwritten; replaced_by keeps termination for every engagement but **drops the base's re-pricing-by-change-order option for every engagement outside scope (time-and-materials engagements held longer than max_client_hold_days)** — finding C6. ← change_orders: inherited "A signed change order changes contract_value_usd by its value delta" is not applied by the target tool — finding C15. Cap (max_cumulative_change_pct) and lapse window inherited.
- CO fee ← change_orders: fee clause overwritten; replaced_by restates the out-of-scope fee and names its scope — XF#16 satisfied.
- remobilization ← schedule_and_holds: fee clause overwritten; replaced_by restates holds threshold < h ≤ max, but **not the base fee for a resumption outside scope after a hold longer than max_client_hold_days (a time-and-materials engagement)** — finding C6.

### factor_ladders
| policy | factors (effect) | P/M | multi-source | cross_difficulty |
|---|---|---|---|---|
| rate_lock | managed_component (P), commitment_component (P), seat_scale_component (P), tenure_component (P), prepaid_hours_component (M) | 4/1 | none (Premier-or-Enterprise is one field) | managed ×4, timebank |
| deposit | client_standing (P), hardware_exposure (P), start_lead (P), clearpath_autopay (P), open_balance (P), planned_duration (M) | 5/1 | client_standing (agreement tier AND billing late-fee count) | managed ×3, hardware |
| milestone | change_order_schedule (M), billing_lag (P), managed_client_credit (P), prompt_payment (P) | 3/1 | change_order_schedule (signed COs AND milestone invoices); prompt_payment (late-fee rows AND payment rows) | managed |
| restart | hold_length (M), managed_rate (P), scope_growth (P), repeat_pause (P), phases_remaining (P), clearpath_standing (P) | 5/1 | none (managed_rate tier+seats on one record) | managed ×2 |
| CO fee | fee_basis (M), sequence_factor (P), managed_client_factor (P), restart_window (P), contract_growth (P) | 4/1 | none | managed |
| remob | hold_span (M), continuity (P), remaining_work (P), repeat_restart (P), architect_ramp (P), after_hours_windows (P) | 5/1 | none | managed |
- Counts 4–6 everywhere; ≥2 parameter and 1 method everywhere; per-task multi-source available in both chains (deposit; milestone). Ladders ≥3 tiers, pairwise disjoint as stated, every tier stated in its rule and implemented in compute; `decides` are inputs, never `result`; bindings disjoint; mechanical XF#1 walk: no factor binding reaches another factor's binding.
- Method labels: prepaid (flat / proportional / none), long planned-duration tier (time-proration), change-order schedule (true-up / original-value share / in-force share), hold_length (escalation pro-rata / uplift+block / uplift), fee_basis (affine / percentage / flat-waived), hold_span (quarterly pro-rata / flat+weekly / flat) change formula shape. **The deposit planned_duration short tier ("deposit basis is original_value_usd … with no reduction for the locked rate discount") only drops the (100 − rate_discount_pct)/100 multiplier and coincides with the fall-through whenever rate_discount_pct = 0** — finding C8.
- Realism of tiers (XF#21): findings C10 (client_standing on Major/Strategic classes), C11 (hold-length ladders non-monotone), C12 (fee_basis non-monotone on Major/Strategic), C13 (credits recaptured). Billing-lag credit (a credit for the firm's own late invoicing) recorded as observation O3.
- XF#3 assembly sentences: rate_lock is generic ("the sum of the discount components that apply"). Five rules name factors in their combination sentence — finding C1. XF#5: restart defines "The hold length … the full months on hold …" as a free-standing rule sentence although only hold_length uses it — finding C7.

### findings
All are charter-global; the task(s) each bears on are named so their files carry the demonstration.

**C1 — SOURCE-FACTOR RED (XF#3, charter-level).** Symptom: combination sentences name factor schedules instead of stating the assembly generically. Members (every one in the charter): deposit "the deposit percentage is deposit_pct or the percentage the client-standing schedule sets in its place, … the deposit basis, which is the estimated fees or the amount the planned-duration schedule sets in their place"; milestone "first the amount to be billed for the milestone is figured by the change-order schedule"; restart "the hold-length schedule gives the base re-pricing amount"; CO fee "the fee-basis schedule gives the base fee"; remobilization "the hold-length schedule gives the remobilization amount, the factors of the continuity and remaining-work schedules are multiplied together". Consequence: the assembly sentence names the factor quantities, so the hub/computation documents carry factor names. No scored-number effect. Bears on: task 0 (deposit), task 1 (milestone, restart, CO fee, remob).

**C2 — SOURCE-POLICY RED (XF#9).** CO fee `compute_basis` keys `signed_at`, `since_resume`, `window_factor` quote "signed …" — not in the rule, which says "registered …". The rule and its basis state two different anchors. Bears on task 1 (no number effect there: CO-044310-03 is registered 10-12 and signed 10-14, both ≤ 7 days).

**C3 — SOURCE-POLICY RED (XF#8/#14).** Rule: "The restart change order whose fee is figured is the change order most recently signed on the engagement." Compute: LATEST by `created_at` (registration moment); the table has no signature date. Decoy: a scope CO registered after the restart CO but signed before it — the rule picks the restart CO, compute picks the other. Bears on task 1 (no effect in its world: CO-03 is both latest registered and latest signed).

**C4 — SOURCE-POLICY RED (XF#11).** Remobilization "the change order fee most recently posted on the engagement" on a date-only `posted_date`; two CO fees on one day have no tie rule (compute keeps the first row encountered). Bears on task 1 (no tie in its world).

**C5 — SOURCE-POLICY RED (XF#13 class; list complete).** Unstated negative-lag/absent branches: (a) deposit start-lead: a scheduled_start_date before the signature date gives `lead_days` < 0 → compute adds rush_14_pts, the rule ("rush_14_days or fewer calendar days after the signature date") does not say; (b) CO fee restart-window: a restart CO registered before resumed_date gives `since_resume` < 0 → window_short_factor, the rule ("… or fewer calendar days after the engagement's resumed_date") does not say — exercised in task 1's skip-the-signature run (CO-02 registered 2026-05-15 → −150 days → 0.75); (c) remobilization prerequisite sentence when the restart CO fee is zero and never posted (two readings, see prerequisite_sentences 4). Bears on task 0 (a), task 1 (b, c) — neither gold path hits them.

**C6 — SOURCE-POLICY RED (XF#16 class; list complete).** Retired base content not restated for out-of-scope cases: restart_repricing's replaced_by drops "re-price the remaining work by change order" for engagements other than resumed fixed-fee ones; remobilization's replaced_by states no fee for a resumption after a client-caused hold longer than max_client_hold_days outside its scope (time-and-materials). The KB marks the base clause dead for those engagements. Charter-level; bears on task 1's policies, no effect on its fixed-fee world.

**C7 — SOURCE-FACTOR RED (XF#5).** Restart: "The hold length is the calendar days from on_hold_date to resumed_date, or to the re-pricing date for an engagement not yet resumed; the full months on hold are counted the same way …" is a free-standing sentence although only the hold_length factor uses it (the baseline does not). Charter-level; task 1.

**C8 — SOURCE-FACTOR RED (XF#6).** Deposit planned_duration short tier vs fall-through: original_value_usd vs original_value_usd × (100 − rate_discount_pct)/100 — a multiplier swap, identical on every client with a 0.0 locked discount (the rate-lock baseline). Charter-level; task 0 sits on the long tier.

**C9 — SOURCE-POLICY RED (XF#19).** `sign_statement_of_work_96bc6bf1` docstring: concrete value "(0.0 when no discount is locked)" and the claimed effect "stored rounded half up to 1 decimal place" which the body (`round(float(x), 1)`) does not implement. Task 0 (gold not 0.0 and no tie on its path — no number effect).

**C10 — SOURCE-FACTOR RED (realism, unreal ladder).** Deposit client_standing: clean_deposit_pct 15, one_late_deposit_pct 20, fall-through deposit_pct by class. Major Project deposit_pct 20 = one_late 20 (tier 2 ≡ fall-through); Strategic Program deposit_pct 15 = clean 15 (tier 1 ≡ fall-through) and one-late 20 > 15, i.e. a managed client with one late fee pays a higher deposit than a client with no ClearPath agreement at all. Charter-level; task 0 is an Advanced Project (25) — no effect there.

**C11 — SOURCE-FACTOR RED (realism, non-monotone hold ladders; class complete).** restart hold_length and remobilization hold_span: the longest-hold tier is cheaper than the middle tier over most of its range. Probe on task 1's engagement (Major, max hold 90, on hold 2026-05-29, opening billing): hold 179 days → re-pricing block 9,868.16 / remob span 5,500.00; hold 180 days → 9,471.40 / 4,166.67. Standard/Advanced classes invert even more (2 full months at 9 %/yr = 1.5 % < 4 %). No IT services firm charges a client less for a longer pause. Task 1 sits in the middle tier (136 days); demonstration in 1.md.

**C12 — SOURCE-FACTOR RED (realism, non-monotone fee schedule).** CO fee fee_basis on Major (waiver 5,000, admin 350): |delta| 19,999.99 → 500.00; |delta| 20,000.00 → 350.00; Strategic likewise (39,999.99 → 1,000; 40,000 → 500). Task 1 (Major, delta in the middle tier).

**C13 — SOURCE-POLICY RED (credits billed back).** Milestone: "that total credit is taken once off that amount" vs the same rule's change-order tier "less everything already billed by the deposit and milestone invoices" and the inherited base "the final invoice bills contract_value_usd minus everything already billed … so that a fixed fee is billed exactly once in total". Under the latter two every credit granted on an earlier milestone is re-billed at the next true-up or at the final invoice; under the credit sentence the client's total is reduced. Demonstration in 1.md.

**C14 — SOURCE-POLICY RED (check 7).** CO fee edge `condition` adds "registered on or after the engagement's resumed_date"; remobilization edge `condition` adds "posted on or after resumed_date"; neither is in its `policy_source`. A restart CO registered during the hold satisfies the sentence and fails the declared condition. Charter-level (both hold in task 1's world).

**C15 — SOURCE-POLICY RED (inherited base effect not applied by the tool).** Base `project_change_orders`: "A signed change order changes contract_value_usd by its value delta"; event `project_change_order_applied` fields "contract_value_usd: New contract value., change_order_count: Incremented." The restart policy's subject is `project_change_order_applied`, but `sign_restart_change_order_602c3012` writes only the change-order row. Terminal state after gold: engagement contract_value_usd and change_order_count stale. Demonstration in 1.md.

Observations: O1 "after a pause" wording in two docstrings; O2 base "registers each as a change request" for a SOW signature has no change type/tool; O3 billing-lag credit realism (credit for the firm's own late invoicing) is unusual but plausible as a published concession; O4 RND/round is not strict half-up (no tie on either gold path); O5 rate-lock `baseline.params` names the list rates while the baseline default is a literal 0.0; O6 base remobilization event "posted_date: Resume date" vs extended posting after the CO fee; O7 prompt-payment "exactly one payment" is the floor for every kicked-off engagement (deposit paid), still dividing customers.

## closing_checklist
Written after both reveals (2026-10-18T03:36:56Z); nothing above this heading was edited after a reveal except freeze-timestamp corrections to the file mtimes.
- Audit files: `0.md`, `1.md` one-to-one with tasks 0 and 1; `_difficulty.md` alongside; first revision.
- Coverage/disjointness: task 0 scope {sow_signature_rate_lock, signature_deposit} + tools {sign_statement_of_work_96bc6bf1, post_deposit_invoice_06d795b1}; task 1 scope {milestone_billing, restart_repricing, restart_change_order_fee, restart_remobilization} + their four tools. Pairwise disjoint, jointly all six extended policies and all six task tools; uuid8s independent (§ action_binding_and_uuids).
- Trees: task 0 — 1 prerequisite, 1 value_input, user write (signature); task 1 — 3 prerequisites, 3 value_input, user write (restart CO). Whole-difficulty graph acyclic. Every edge unmet at the opening and load-bearing (recomputed; matches GT figures).
- Factors: counts within 4–6 with ≥2 parameter / 1 method per computation; multi-source per task (deposit client_standing; milestone change_order_schedule, prompt_payment); cross-difficulty seeded per task; every factor bears weight against its baseline and every fall-back differs from gold (all figures equal to GT).
- **Not closed**: task 0 RED (T0-1), task 1 RED (T1-1 … T1-6), charter findings C1–C15 open. Gate re-run on a final form not performed (no final form; the brief's gate snapshot stands for this round).

VERDICT revision_1: task0=RED T0-1 task1=RED T1-1,T1-2,T1-3,T1-4,T1-5,T1-6 charter=C1,C2,C3,C4,C5,C6,C7,C8,C9,C10,C11,C12,C13,C14,C15

## revision_2

### charter_global_frozen (revision_2)
- Gate: `tasks/project_engagements/worklog.md` last line = `REWORK round 2: gates 7/7 green` (checked with `tail -n 1` only).
- Snapshot (executed `/tmp/erl0069_coord/snapshot.sh project_engagements 2`, 2026-10-18T07:15:44): check_extended EXTENDED OK, check_task_tools TASK TOOL CONTRACT OK, replay_tasks REPLAY OK, check_solvability SOLVABILITY OK, check_compute COMPUTE OK, check_grounding GROUNDING OK, check_cross_fire SCOPE OK (all rc=0). Views r2/0.view.json sha256=1132bda9bb68b66de7ba2c98308088c14bfca53e231add627d19b402e27627eb, r2/1.view.json sha256=14897423ddf26b29c3118141a56b3ab5e4dfb0a71a77e01dba109ce38f742b6e; project.extended.yaml sha256=32c7ce1b3691a12876acde2d8548a6d809476cf2d520f4316e9b0a18fd5ba60f; task_tools.py sha256=543e7e166bba6ccee087e379ace103f888cbc136b718e51bd33e42e57619c513.
- Both shared inputs changed since revision_1 → every charter-global section re-derived in full below. Base copy re-diffed: verbatim (trailing blank line only). XF_recipe.md now carries points 23–26; all 26 points checked on all six policies.
- Written before reading the round-2 claims list, any task JSON, plan.md or the worklog body. Not blind in the strict sense: the auditor knows the revision_1 GT; derivations below are fresh recomputations on the r2 views with the gate's DSL evaluator.

### re-derived charter checks (revision_2)
- rule_compute_equivalence: mechanical sweep — every `compute_basis` quote verbatim in its own rule, every `policy_source` verbatim, every baseline sentence in its rule (remobilization's baseline is two rule sentences with the prerequisite sentence between them — each present). XF#1 walk: no factor binding reaches another factor's binding. XF#26 mechanical: no plain binding reads a factor-owned binding. XF#7: no factor id inside a tool name.
- action_binding_and_uuids: same six `(target_tool, computes)` pairs and uuid8s; tools validate nothing. `sign_restart_change_order_602c3012` now also moves `contract_value_usd` by the delta and increments `change_order_count`; docstring describes exactly that. `sign_statement_of_work_96bc6bf1` docstring has no concrete value and no rounding claim.
- XF#24 (trigger rule): events written — project_sow_signed (base trigger project:project_deposit_invoice), project_deposit_invoice ([]), project_milestone_invoice ([]), project_change_order_applied (project:project_change_order_fee), project_change_order_fee ([]), project_remobilization_fee ([]). None crosses into another category. PASS.
- prerequisite_graph: unchanged shape (two chains, four state-form value_input edges); every `condition` now restates its sentence without additions (deposit: "carries a signature date and a rate_discount_pct holding the labor rate discount locked at signature …"; CO fee: "carry the restart change order in signed status"; remob: "carries an administration fee posted for the restart change order"). The "registered on or after resumed_date" requirement now lives in the rules' own definition of the restart change order.
- prerequisite_sentences: four sentences unchanged in form; each resolved by exactly one write; zero-fee reading removed (CO-fee rule: "a restart change order is never waived, so it always carries a fee").
- override_declarations: restart and remobilization `replaced_by` now restate the out-of-scope remainder ("any other such engagement that resumes may still have its remaining work re-priced by change order"; "every other resumption after a client-caused hold longer than remobilization_threshold_days … remobilization_fee_usd"); milestone `replaced_by` restates the final invoice; CO fee scoped. Base "registers each as a change request" for a SOW signature (O2) unchanged — observation.
- XF#23 all-pairs (method factors):
  | factor | pair | verdict |
  |---|---|---|
  | rate_lock prepaid_hours | flat vs proportional (adds hours, floor); proportional vs none (none is not 0 across proportional's domain); flat vs none | PASS |
  | deposit planned_duration | long (adds duration, division) vs standard; short (adds max with tariff min_contract_value_usd) vs standard; long vs short | PASS |
  | milestone change_order_schedule | true-up (adds billed amounts) vs standard — PASS; **reduction tier "schedule share of original_value_usd" vs standard "schedule share of contract_value_usd" — same combination (share × one amount), one input swapped for another, nothing added → FAIL**; true-up vs reduction PASS | FAIL |
  | restart hold_length | uplift+block (adds tariff) vs uplift; +escalation (adds months) vs uplift+block; vs uplift | PASS |
  | CO fee fee_basis | flat vs admin+2.5 % excess (adds delta); +review block (adds tariff) | PASS |
  | remob hold_span | flat vs +weekly (adds weeks); +quarterly (adds months) | PASS |
- Monotonicity probes (task-1 engagement, Major, on hold 2026-05-29, opening billing): re-pricing amount for the hold 134 d 6,522.88 / 135 d 10,042.88 / 179 d 10,042.88 / 180 d 16,158.08 / 200 d 17,381.12; remob 2,500.00 / 4,000.00 / 5,500.00 / 9,666.67 / 11,250.00 — monotone. CO fee base, Major: 4,999.99 → 350.00, 5,000 → 350.00, 19,999.99 → 725.00, 20,000 → 1,165.00; Strategic and Quick Start likewise monotone.
- factor_ladders: counts rate_lock 5 (4P/1M), deposit 6 (5P/1M), milestone 4 (3P/1M), restart 6 (5P/1M), CO fee 5 (4P/1M), remob 6 (5P/1M); multi-source per chain: deposit client_standing; milestone change_order_schedule (signed COs AND milestone invoices). Deposit client_standing is now "points taken off deposit_pct" (10 / 5 / 0) — distinct on every class.

### findings (revision_2, charter-global)
Round-1 items: C2, C3, C4, C5, C6, C7, C8, C9, C10, C11, C12, C13, C14, C15 — closed on the re-derived text (evidence above and in the probes). C1 — partly closed (deposit is now generic), residual members below.

**C1-r — SOURCE-FACTOR RED (XF#3 / XF#1 prose; class complete).** Combination sentences still name the quantity a single method factor sets: milestone "the amount billable for the milestone is figured first … withheld once from that amount"; restart "the amount for the hold is figured first … added to the amount for the hold"; CO fee "the fee amount for the size of the change is figured first"; remob "the amount for the hold is figured first, the factors of the adjustments that scale it …". The parameter factors of two policies are stated against that factor-owned quantity rather than the result or the standard amount: milestone retentions "… percent of the amount billable" (×3), CO fee "… times the fee amount" (sequence, managed-client, restart-window, contract-growth). Deposit shows the generic form is available ("the estimated fees unless an adjustment sets another basis"). No scored-number effect.

**N1 — SOURCE-FACTOR RED (XF#23).** Milestone change_order_schedule reduction tier vs fall-through: share × original_value_usd vs share × contract_value_usd — an input swap with no added input or operation.

**N2 — SOURCE-FACTOR RED (realism, XF#21).** Milestone retentions defer billing for the riskier client: a client with ClearPath late fees (10 % / 5 %) or engagement late fees (5 % / 2.5 %) is billed less on the milestone now and the balance later — the opposite of how an IT services firm treats a late payer (it tightens terms, it does not extend credit on earned milestones). The open-change-order retention (10 % / 5 % while change orders await signature) withholds an earned milestone for a contract change that does not touch it. Bears on task 1.

**N3 — SOURCE-POLICY RED (XF#13 zero branch).** Deposit: for a Strategic Program (deposit_pct 15) a clean ClearPath client (−10) with six ACH payments in six months (−5) and no added points has a deposit percentage of 0 → deposit 0.00; the rule says neither "no deposit is posted" nor a floor, and the tool takes "a positive decimal number". Two readings (post 0.00 / post nothing). Charter-level; task 0 not affected (30 %).

Observations: O8 CO-fee `rco_ok` tests hold length and registration date but not the fixed-fee / client-caused parts of the rule's restart-CO definition (scope-level; no effect in task 1); O9 Quick Start CO-fee step 132.50 → 622.50 at |delta| 2,000 (monotone, steep); O1, O2, O4, O5, O6 carried.

### closing_checklist (revision_2)
- Files: 0.md, 1.md, _difficulty.md carry revision_2 sections appended; revision_1 text untouched.
- Scopes unchanged and disjoint; all six policies and tools covered; uuid8s unchanged and independent; graph acyclic; trees 1/3 prerequisites with all edges value_input and one user write each; every factor bears weight on its task world (all GT figures equal to the re-derivation).
- Not closed: task 0 T0-1 (residual FEFO draws); task 1 T1-7, T1-8; charter C1-r, N1, N2, N3. Gates: snapshot of round 2 (all 7 green) is the final-form run for this round.

VERDICT revision_2: task0=RED T0-1 task1=RED T1-7,T1-8 charter=C1-r,N1,N2,N3

## revision_3

### charter_global_frozen (revision_3)
- Gate: worklog last line = `REWORK round 3: gates 7/7 green` (`tail -n 1` only).
- Snapshot (executed `/tmp/erl0069_coord/snapshot.sh project_engagements 3`, 2026-10-18T08:05:23): check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire — all rc=0 / OK. Views r3/0.view.json sha256=63b4d13ba192882a8d22b9e0f572bad81ff3ace8cdf45b57a2bd662ce478f107, r3/1.view.json sha256=a84caef780754884e24e35948b2558efc4ab7cccca2bc632c56c85064252df6c; project.extended.yaml sha256=3f7a065f6f22b3f1d6c3f7ae3940c95f3ae6b0f809e1ac51e3320e4c6f59ff96 (changed); task_tools.py sha256=543e7e166bba6ccee087e379ace103f888cbc136b718e51bd33e42e57619c513 (unchanged since revision_2 → action_binding_and_uuids and XF#19/#24 carried by reference to revision_2).
- Charter re-derived in full; written before the round-3 claims list and before any task JSON; not blind (earlier GT known).
- This round is the single exhaustive pass requested: every XF point 1–26 on all six policies, and every seeded row of both tasks (project, managed, security, TimeBank, hardware) against its owning charter. Items listed below are the complete set found.

### exhaustive pass — policies (XF 1–26)
Mechanical: every compute_basis quote, policy_source and baseline sentence verbatim in its rule; every compute binding has a basis; XF#1 walk and XF#26 plain-binding check clean; no factor id inside a tool name. Base copy verbatim.
| XF | rate_lock | deposit | milestone | restart | CO fee | remob |
|---|---|---|---|---|---|---|
| 1–2 independence / shared selections | ok | ok | ok | ok | ok | ok |
| 3 generic assembly | ok ("components that apply") | ok ("unless an adjustment sets another basis") | ok ("unless an adjustment figures it another way") | **"unless an adjustment for the hold figures it another way"** | **"unless an adjustment for the size of the change figures it another way"** | **"unless an adjustment for the hold figures it another way"** |
| 4 order | sum (commutes) | points, floor, basis — stated | before-retainage, then retainage — stated | stated | stated | scale, add, deduct, floor — stated |
| 5 single-use quantities in own sentences | ok | ok | ok | ok | ok | ok |
| 6/23 method shape (all pairs) | PASS | PASS | PASS (scope tiers: +delta outright / −delta / plain share — each adds an input or operation) | PASS | PASS | PASS |
| 7 factor id ⊄ tool | ok | ok | ok | ok | ok | ok |
| 8–9 rule == compute, quotes | ok | ok | ok | ok | ok (scope tests partly in `rco_ok`, O8) | ok |
| 10 rounding | ok | ok | ok | ok | ok | ok |
| 11 ties | single active agreement | — | highest CO number; same-day milestones stated | — | highest CO number | highest CO number; fees summed |
| 12 month-end | ok (MONTHS) | ok | ok | ok | — | ok |
| 13 absent / zero / negative | ok | ok (floor min_deposit_pct; start on/before signature stated) | **ClearPath good-standing tier for a client with no ClearPath billing unstated** | ok | ok (no restart CO → nothing; never zero) | ok |
| 14 decoys | closed agreements excluded | ok | pending/earlier COs excluded by rule | ok | pre-resume CO excluded | ok |
| 15 DSL limits | ok | ok | ok | ok | ok | ok |
| 16–18 overwrite hygiene | **base "registers each as a change request" not applied to a SOW signature, no overwrite** | ok | ok (final invoice restated) | ok | ok | ok |
| 19 docstrings | ok (r2) | ok | ok | ok | ok | ok |
| 21 realism | ok | ok | **scope-addition billing re-bills earlier additions** | ok | ok ("multiplied by nothing", O10) | ok |
| 24 trigger rule | ok (r2 list) | ok | ok | ok | ok | ok |
| 26 result named / fields exist | ok | ok | ok | ok | ok | ok |

### findings (revision_3, charter-global)
Round-2 items: N1 closed (reduction tier removed; scope tiers pass XF#23); N2 closed (retainage now extended to clients in good standing and to large programs, released by the final invoice); N3 closed (min_deposit_pct floor, stated and implemented); C1-r closed for milestone (generic) — residual below.

**C1-r2 — SOURCE-FACTOR RED (XF#3; class complete: restart, CO fee, remob).** The combination sentences still identify the replacing factor ("an adjustment for the hold", "an adjustment for the size of the change"); deposit and milestone show the anonymous form. No number effect.

**N4 — SOURCE-POLICY RED (realism / billing exceeds contract value).** Milestone: "A signed scope addition is billed in full with the milestone that delivers it. Only the signed scope addition with the highest change order number is tested, earlier ones having been billed with earlier milestones" — yet every later milestone bills its schedule share of contract_value_usd, which still contains every earlier addition. Earlier additions are therefore billed again at each later milestone. Charter-level demonstration (Major, original 240,000, one +96,000 addition delivered with milestone 1, within the 40 % cap): deposit 48,000 + M1 (20 % × 240,000 + 96,000) 144,000 + M2 67,200 + M3 67,200 + M4 33,600 = 360,000 > contract value 336,000 — the base final invoice ("contract_value_usd minus everything already billed") would be −24,000. Second reading of the same sentences (an addition already billed in full is out of every later share): M2 of task 1 = 20 % × (256,000 − 9,600 − 6,400) + 6,400 = 54,400 before retainage. Demonstration in 1.md.

**N5 — SOURCE-FACTOR RED (XF#13 absent record).** Milestone clearpath_good_standing: "a client whose ClearPath billing shows no late fee posted in the twelve months … has a further cp_clean_pct percent … withheld"; a client with no ClearPath agreement (whom relationship_retainage names explicitly: "whose client holds no such agreement") has no ClearPath billing — compute (`XCOUNT == 0`) grants the clean-standing retainage, the rule states no tier for it. Not reached in task 1 (Professional, one late fee).

**C16 — SOURCE-POLICY RED (XF#18, pre-existing, was O2).** Base `project_client_signed_changes` (subject includes project_sow_signed): "the service desk registers each as a change request carrying the change order number, type, value delta and new target date, pending the authorized contact's e-signature". Rate lock cites this base policy, the client signs the SOW through `sign_statement_of_work_96bc6bf1` with no registered change request, the schema's change_type has no SOW-signature value, and no overwrite retires the sentence. A reader of the base text looks for a registration step the toolset cannot perform. Bears on task 0.

Observations: O8 carried (scope tests partly in `rco_ok`); O10 CO-fee factor sentences say "multiplied by nothing" for the neutral tier (compute 1.0; "always carries a fee" excludes the ×0 reading); O1, O4, O5, O6 carried.

### closing_checklist (revision_3)
- Revision_3 sections appended to all three files; earlier text untouched. Scopes, tools, uuid8s, graph and trees unchanged; every factor bears weight; every GT figure equals the re-derivation.
- Complete list after the exhaustive pass — task 0: T0-2, T0-3; task 1: T1-9, T1-10; charter: C1-r2, N4, N5, C16. Observations O1, O4, O5, O6, O8, O10 and the winter EDT labels (task 0) carry no consequence. Nothing else was found in any policy or seeded row.
- Gates: round-3 snapshot (7/7 green) is this round's final-form run.

VERDICT revision_3: task0=RED T0-2,T0-3 task1=RED T1-9,T1-10 charter=C1-r2,N4,N5,C16

## revision_4

### charter_global_frozen (revision_4)
- Gate: worklog last line = `REWORK round 4: gates 7/7 green`. Snapshot executed (`/tmp/erl0069_coord/snapshot.sh project_engagements 4`, 2026-10-18T09:22:14): all seven gates rc=0 / OK. Views r4/0.view.json sha256=6d7eb65a969fd28a2de9a9eacb4026121f646542d147bc64bc5b839fc26239a5, r4/1.view.json sha256=87f3e7053990edb22dc049bdf073b09b8f9530b8662b59a5e02d2e5efef2df6f; project.extended.yaml sha256=b035bbbbb505ece5524723dc6b3443be8617fb1c1f9a3f25acb9e2f8311bdc87 (changed); task_tools.py sha256=543e7e16… (unchanged since revision_2 — tool sections carried).
- Scope of this round (per brief): what changed since revision_3 plus a regression run. Changed: rate-lock overwrite list (new scoped overwrite of `project_client_signed_changes`); milestone scope-addition billing and good-standing tier; combination sentences of restart / CO fee / remob. Seeds: task 0 seat-baseline ticket blanked, winter timestamps relabelled EST; task 1 seat-baseline ticket blanked. Written before the round-4 claims list and any task JSON; not blind.
- Regression run: mechanical sweep (quotes, replaced_by text, policy_source, baseline sentences, bases for every binding, XF#1, XF#26, XF#7) clean on all six policies; base copy verbatim; tool module unchanged.

### findings (revision_4, charter-global)
- **C1-r2 — closed.** Restart, CO fee and remob now read "unless an adjustment figures it another way" (anonymous, as deposit and milestone).
- **N4 — closed.** Milestone: "A signed scope addition is billed exactly once, in full, with the milestone that delivers it, and never through a schedule share"; compute bills share × (contract_value_usd − every signed addition) + the delivered addition, capped at contract_value_usd less deposit and milestone billing (`MN(pre_retainage, billing_cap)`, stated). Re-run of the revision_3 counter-example (Major, +96,000 with M1): 48,000 + 144,000 + 48,000 + 48,000 + 24,000 = 312,000 ≤ 336,000; final invoice positive. XF#23: tiers add an input (sum of additions) / add the delivered delta — PASS.
- **N5 — closed.** "… and any other client none, including a client with no ClearPath billing at all"; compute requires ClearPath monthly-fee billing.
- **C16 route (BLUEPRINT-KNOWN, base frozen).** New overwrite of `project_client_signed_changes`, scoped "For the signature of a time-and-materials statement of work under this policy, and only for that signature, no change request is registered: the authorized contact e-signs the issued statement of work itself …", and it restates registration for change orders, termination notices, acceptance sign-offs and rejections. Signing path judged: for a T&M SOW signed under this policy the published text now says one thing — no registration, the client e-signs the issued SOW, the desk never signs — matching `sign_statement_of_work_96bc6bf1`; the identity-verification sentence ("A contract change may be registered only … after identity verification has passed") is not retired and the shared `verify_customer_identity` contract requires verification before any change, so verification stays unambiguous. C16 closed for the task-0 path.
- **N7 — SOURCE-POLICY RED (XF#16, consequence of the C16 route).** The retired clause covered "Signing a statement of work, change orders, termination notices, acceptance sign-off and acceptance rejections"; the replaced_by restates registration for every item except **the signature of a fixed-fee statement of work** (out of this policy's scope). For a fixed-fee SOW the KB carries neither "no change request is registered" nor the registration sentence, so the published text is silent on how a fixed-fee SOW is signed. Charter-level; no task signs a fixed-fee SOW. (Restating it would carry the BLUEPRINT-KNOWN base defect into that case — noted, not a fix.)
- **N6 — SOURCE-POLICY RED (XF#14/#15, second-record case of the new scope-addition rule).** "A milestone delivers at most one scope addition, the signed scope addition with the highest change order number … earlier additions were delivered and billed with earlier milestones." Probe: on task 1's engagement add a signed scope addition CO-044310-02A (+3,000, registered 2026-05-18) beside CO-044310-02 (+6,400, 2026-05-15) in M2's window — compute bills 20 % × (259,000 − 19,000) + 3,000 = 51,000.00 before retainage; CO-02's 6,400 is billed by no milestone (excluded from every share, never "delivered") and reaches the client only in the final invoice, contradicting "billed exactly once, in full, with the milestone that delivers it" and the rule's assertion that earlier additions were billed with earlier milestones. Reading that bills both additions delivered with M2: 57,400.00. Two scope additions inside one milestone's window are ordinary. Charter-level; task 1 has one addition per window (CO-01 before M1, CO-02 before M2).

Observations: O8, O10, O1, O4, O5, O6 carried; winter EDT labels fixed (EST).

### closing_checklist (revision_4)
- Revision_4 appended to all three files; earlier text untouched. Scopes, tools, uuid8s, prerequisite graph and trees unchanged; every factor bears weight; every GT figure equals the re-derivation; both tasks PASS.
- Charter still open: N6 (two scope additions in one milestone window), N7 (fixed-fee SOW signature left without a stated signing rule by the C16 route). Neither moves a scored value in task 0 or task 1.
- Gates: round-4 snapshot (7/7 green) is this round's final-form run.

VERDICT revision_4: task0=PASS task1=PASS charter=N6,N7

## revision_5

### charter_global_frozen (revision_5)
- Gate: worklog last line = `REWORK round 5: gates 7/7 green`. Snapshot executed (`/tmp/erl0069_coord/snapshot.sh project_engagements 5`, 2026-10-18T09:55:17): all seven gates rc=0 / OK. Views r5/0.view.json sha256=6d7eb65a…39a5 and r5/1.view.json sha256=87f3e705…df6f — byte-identical to r4 (worlds, personas, frozen_time unchanged); project.extended.yaml sha256=e00536b5f230995a36568edb23d06f5cb4d4637c2c9926b6823a6321d16bc2bd (changed); task_tools.py 543e7e16… (unchanged).
- Changed text (confined to the rate-lock overwrite list and the milestone scope-addition sentences; other policies' offsets and lengths unchanged). Regression: mechanical sweep (quotes, replaced_by, policy_source, baseline sentences, binding bases, XF#1, XF#26, XF#7) clean on all six policies; base copy verbatim; both chains recomputed on the r5 views with the gate's evaluator — every result, factor substitution and baseline identical to revision_4 (13.1; 14,077.80; 50,592.00; 8,205.76; 354.87; 3,935.13).

### findings (revision_5)
- **N7 — closed.** The overwrite of `project_client_signed_changes` now reads "For the signature of every statement of work, fixed-fee or time-and-materials, and only for such a signature, no change request is registered: the authorized contact e-signs the issued statement of work itself, the service desk never signs on the client's behalf, and a fixed-fee statement of work signed this way keeps the rate discount figured on its issue date; change orders, termination notices, acceptance sign-offs and acceptance rejections are still registered …". Every item of the retired clause is now covered either by the scoped replacement or by the restated remainder; the fixed-fee clause agrees with the first overwrite (issue-date discount kept). Signing path unambiguous for every SOW; verification sentence untouched.
- **N6 — closed.** The rule now states the treatment compute applies to every signed scope addition: "one that shared a milestone's window with a higher-numbered addition is not delivered by any milestone and is billed in full by the final invoice on acceptance, because no schedule share includes it". The revision_4 probe (CO-02 +6,400 and CO-02A +3,000 in one window) now has one reading — M2 51,000.00 before retainage, CO-02 on the final invoice — and every addition is billed exactly once. Observation O11: deferring a delivered addition to acceptance only because a later addition shares its window is an unusual (firm-unfavourable, client-neutral) billing convention; it is stated, priced once and not reached in task 1.
- No new defect found in the changed text; no regression.

### closing_checklist (revision_5)
- Revision_5 appended to all three files; earlier text untouched. Scopes, tools, uuid8s, prerequisite graph, trees, factor weights and GT unchanged from revision_4 (re-verified). Both tasks PASS; charter findings all closed; observations O1, O4, O5, O6, O8, O10, O11 carry no consequence.
- Gates: round-5 snapshot (7/7 green) is the final-form run.

VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN

## revision_6

### charter_global_frozen (revision_6)
- Gate: worklog last line = `REWORK round 6: gates 7/7 green`. Snapshot executed (`/tmp/erl0069_coord/snapshot.sh project_engagements 6`, 2026-10-18T10:33:39): all seven gates rc=0 / OK. Views r6/0 sha256=6d7eb65a…39a5 and r6/1 sha256=87f3e705…df6f (identical to r4/r5); project.extended.yaml sha256=2132a049b0fc82a1675070b4f5c5548f71cbe130bdf19cda2f14e26470d930b1 (changed); task_tools.py 543e7e16… (unchanged).
- RED input read in full: `audits/render_source/project_engagements/render_r1.md` (renderer scan-first STOP after revision_5, three findings). Then the round-6 claims list. Disclosure: all three renderer findings existed in revision_5 text and were missed by this audit (findings 1 and 2 since revision_2/3, finding 3 since revision_4).
- Regression: mechanical sweep (quotes, replaced_by, policy_source, baseline sentences, binding bases, XF#1, XF#26, XF#7) clean on all six policies; base copy verbatim; both chains recomputed on the r6 views — every result, substitution and baseline identical to revision_5 (13.1; 14,077.80; 50,592.00; 8,205.76; 354.87; 3,935.13). Probe: task-1 engagement re-classed Quick Start Project (empty schedule, no milestones) — restart compute runs (no error), phases points 0.

### renderer findings (revision_6)
- **R1 (XF#13, empty milestone schedule) — closed.** Restart rule: "a class schedule with no milestones has none, so that no milestone remains open and no points are added"; compute `ms_total … if P('milestone_pcts') else 0`. Class members swept: the only other reader of `milestone_pcts` is the milestone policy — now guarded in rule ("a class schedule with no milestones has no milestone invoice"; "An engagement with no milestone recorded complete has no milestone invoice") and compute (`ms_last`/`ms_pct` guards, `result … if ms_pos >= 1 else 0.0`). Other class-parameter edge values in scope, swept: Assessment Engagement change_order_admin_fee_usd 0.0 and waiver 0.0 (restart CO fee = 2.5 % of the delta + review block, positive — "always carries a fee" holds); Assessment remobilization_fee_usd 0.0 (floor at zero stated); no division by a zero class parameter in any policy. No further member.
- **R2 (XF#16, "client-caused" definition) — closed.** Restart replaced_by: "a client-caused hold is a hold for client_request, client_dependency or nonpayment"; remobilization replaced_by restates "(client_request, client_dependency or nonpayment)". The term is now defined in force for restart, CO-fee and remobilization scopes.
- **R3 (XF#16, "never signs" ban) — closed.** Signature replaced_by now ends "… and the service desk never signs any of them on the client's behalf."

### XF#16 class sweep — every overwrite (revision_6)
| policy | retired clause | out-of-scope content restated |
|---|---|---|
| rate_lock → classification_and_pricing | "Its rate_discount_pct is clearpath_rate_discount_pct when, on the issue date, … and 0 otherwise." | fixed-fee: yes. **Time-and-materials SOW on its issue date (the provisional figure; also every T&M SOW that is never signed and lapses): no** |
| rate_lock → client_signed_changes | registration / never signs | yes (all items) |
| deposit → signature_deposit_and_kickoff | deposit sentence | yes (fixed fee) |
| milestone → fixed_fee_billing | milestone sentence | nothing out of scope |
| restart → schedule_and_holds | max-hold clause | yes (termination, other re-pricing, definition) |
| CO fee → change_orders | fee sentence | yes |
| remob → schedule_and_holds | remobilization-fee tail | yes (other resumptions, definition) |

**N8 — SOURCE-POLICY RED (XF#16; pre-existing since revision_1, missed until now).** The rate-lock replaced_by keeps the issue-date formula only in the fixed-fee clause ("a fixed-fee statement of work keeps the rate discount figured on its issue date, which is clearpath_rate_discount_pct when, on the issue date, … and 0 otherwise"). For a time-and-materials SOW it only says "the rate discount figured on the issue date is provisional" — the figure is referenced but its formula is retired, and a T&M SOW that is issued but never signed (lapses, or is still proposed) has no in-force rule for its rate_discount_pct at all. Task 0's record shows the provisional 7.5 (= Advanced clearpath_rate_discount_pct for an active rank-5 client), which no in-force sentence now produces. No scored value moves (gold reads the locked discount, not the provisional one). Charter-level.

Observations carried: O1, O4, O5, O6, O8, O10, O11.

### closing_checklist (revision_6)
- Revision_6 appended to all three files. Scopes, tools, uuid8s, graph, trees, factor weights and GT unchanged (GT re-checked at 2026-10-18T10:34:55Z: 13.1 / 14,077.80; 50,592.00 / 8,205.76 / 354.87 / 3,935.13 with unchanged baselines). Both tasks PASS. Charter open: N8.

VERDICT revision_6: task0=PASS task1=PASS charter=N8

## revision_7

### charter_global_frozen (revision_7)
- Gate: worklog last line = `REWORK round 7: gates 7/7 green`. Snapshot executed (`/tmp/erl0069_coord/snapshot.sh project_engagements 7`, 2026-10-18T11:35:03): all seven gates rc=0 / OK. Views r7/0 sha256=6d7eb65a…39a5 and r7/1 sha256=87f3e705…df6f (identical to r6); project.extended.yaml sha256=ecaae80c46aeb5d31cdc22f7361d072d20fc1e56babf19b5ed5e6d452b4c4776 (changed); task_tools.py 543e7e16… (unchanged). Round-7 claims read (N8; milestone overwrite re-sweep; no value moved).
- Regression: mechanical sweep (quotes, replaced_by, policy_source, baseline sentences, binding bases, XF#1, XF#26, XF#7) clean on all six policies; base copy verbatim; every earlier closure sentence re-located verbatim in its rule (restart client-caused definition, empty-schedule branch, anonymous combination sentences of restart / CO fee / remob / deposit, deposit floor, CO-fee never-waived, milestone scope-addition and good-standing sentences, empty-schedule and no-milestone branches, billing cap). Both chains recomputed on the r7 views: every result, substitution and baseline identical to revision_6 and to GT (checked 2026-10-18T11:35:35Z): 13.1 / 14,077.80; 50,592.00 / 8,205.76 / 354.87 / 3,935.13.

### findings (revision_7)
- **N8 — closed.** Classification replaced_by now opens: "Every statement of work carries from its issue date the rate discount figured on that date, which is clearpath_rate_discount_pct when, on the issue date, the client holds an active ClearPath agreement at or above clearpath_discount_min_rank and 0 otherwise; for a time-and-materials statement of work signed under this policy … that issue-date figure is provisional and the labor rate discount is locked on the signature date …, while a fixed-fee statement of work, and a time-and-materials statement of work that is not signed, keep the issue-date figure." Every SOW (fixed fee, signed T&M, unsigned or lapsed T&M) now has an in-force rule; task 0's provisional 7.5 = Advanced clearpath_rate_discount_pct for an active rank-5 (≥ 4) client follows from it.
- XF#16 class re-sweep over all seven overwrites: classification — all cases restated; client_signed_changes — all items; deposit — fixed fee; milestone — now also restates "A milestone of a fixed-fee engagement is still invoiced when it is recorded complete"; restart — termination, other re-pricing, client-caused definition; CO fee — other changes; remob — other resumptions with definition. No member left.
- No new defect; no regression. Observations O1, O4, O5, O6, O8, O10, O11 carried (no consequence).

### closing_checklist (revision_7)
- Revision_7 appended to all three files. Scopes, tools, uuid8s, prerequisite graph, trees, factor weights and GT unchanged and re-verified. Both tasks PASS; no charter finding open.

VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN

## revision_8

### charter_global_frozen (revision_8)
- Gate: worklog last line = `REWORK round 8: gates 7/7 green`. Snapshot executed (`/tmp/erl0069_coord/snapshot.sh project_engagements 8`, 2026-10-18T12:26:43): all seven gates rc=0 / OK. Views r8/0 sha256=6d7eb65a…39a5, r8/1 sha256=87f3e705…df6f (identical to r7); project.extended.yaml sha256=43eec9bdb4f65e545f7965bf12aaf587469d03204cdc6d82887da18692c91a3d (changed); task_tools.py 543e7e16… (unchanged).
- RED input read in full: `audits/render_source/project_engagements/render_r2.md` (renderer scan-first STOP after revision_7; finding 1 blocking, finding 2 low). Then the round-8 claims. Disclosure: both findings were present in the revision_7 text and missed by this audit.
- Regression: mechanical sweep clean on all six policies; base copy verbatim; both chains recomputed on r8 views — all results, substitutions, baselines and skip figures identical to revision_7 and to GT (checked 2026-10-18T12:27:56Z): 13.1 / 14,077.80 (skip-signature 14,985.00); 50,592.00 / 8,205.76 / 354.87 / 3,935.13.

### renderer findings (revision_8)
- **R2-1 (XF#8/#14, "ClearPath billing" narrower in compute) — closed.** Milestone `cp_billing` is now `XCOUNT('managed','managed_billing')` — any ClearPath billing entry — matching "a client with ClearPath billing … including a client with no ClearPath billing at all". An applied/onboarding agreement whose billing holds only an onboarding fee now gets cp_clean_pct, as the rule says.
- **R2-2 (deposit anchored on today vs the signature date) — closed.** `lead_days` reads `F('signed_date')` (NOW only when no signature date is recorded — the skip-signature run); the window sentence now reads "… from the signature date, which is the day the deposit is invoiced …", which is also the base event's definition of the deposit's posted_date ("posted_date: Signature date"), so the window counts from NOW and the start lead from signed_date coincide on every world the charter can produce. Observation O12: the two anchors would split only if a deposit were posted on a later day than the signature, which the base event excludes.

### class sweeps (revision_8)
- Class of R2-1 (a rule qualifier on a record set broader or narrower than the compute filter), every read of every policy: rate lock (active agreement; grants across all blocks), deposit (ClearPath late fees, hardware late fees, ACH payments, active balance), milestone (signed scope additions, latest milestone/deposit invoice dates, engagement late fees, active Professional+ tier, ClearPath billing), restart (signed scope additions, remobilization fees, recorded milestones, ClearPath late fees), CO fee (signed additions/reductions/schedule changes; all signed deltas for growth; highest-numbered signed CO), remob (architect / after-hours minutes, remobilization fees, fees posted for the restart CO). Each rule qualifier equals its compute filter. No further member.
- Class of R2-2 (window or lead anchored on a named date while compute reads today): rate lock — "signature date" = the day of the signing write itself (the tool records signed_date = today); milestone and remob — "invoice date" = the posting day of the write; restart — "re-pricing date" now defined as "the day the client signs the restart change order" (= today for the re-pricing write); CO fee — window between two recorded dates (resumed_date, registration). No further member. Observation O13: that definition sits in the repeat-pause sentence only, while the ClearPath-standing sentence uses the same term; both equal today, no consequence.
- No new defect; no regression. Observations O1, O4, O5, O6, O8, O10, O11, O12, O13 carry no consequence.

### closing_checklist (revision_8)
- Revision_8 appended to all three files. Scopes, tools, uuid8s, prerequisite graph, trees, factor weights and GT unchanged and re-verified. Both tasks PASS; no charter finding open.

VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN

## revision_9

### charter_global_frozen (revision_9)
- Gate: worklog last line = `REWORK round 9: gates 7/7 green`. Snapshot executed (`/tmp/erl0069_coord/snapshot.sh project_engagements 9`, 2026-10-18T14:17:56): all seven gates rc=0 / OK. Views r9/0 sha256=2d781193199ad18d0b51cb4f5ab9f7e65a06a99ef21ccad96212c2c28e95eaa6, r9/1 sha256=3c5f252aabad038ab5b0128854305ca4d84104fd8d681c07d67c3524d29013c8 (changed); project.extended.yaml sha256=43eec9bd… and task_tools.py sha256=543e7e16… — both **unchanged** (seed-only round confirmed); revision_8 charter sections carried by reference.
- Input: `audits/policy_kb/project_engagements/_difficulty.md` revision_1 source items S1–S4 (ClearPath monthly fees and late fees priced at the base rule instead of the published extended ClearPath schedules; stale factor_trace text).
- World diff r8 → r9 (seed only): task 0 — 30 ClearPath monthly fees 8,977.50 → 8,908.67 and their payments; May 2024 combined payment 17,886.17; late fees 134.66 → 19.50 (2025-08-01) and 134.66 → 29.25 (2026-07-01) with their payments; the September 2026 payment changed to an 8,800.00 check (CHK 32104), leaving 108.67 open; balance_due 9,017.34. Task 1 — 15 monthly fees 17,343.60 → 16,976.49 and payments; August 2025 combined payment 34,320.09; late fees 520.31 → 35.00 and 260.15 → 35.00 with payments; balance_due 16,976.49. Nothing else.

### exhaustive cross-product pass against the published docs (revision_9)
Every non-project row of both tasks was checked against the document set published under `docs/` (managed and hardware render their extended charters; security renders base; TimeBank has no published set — checked against `blueprint/products/timebank.yaml`). Scripted recomputation for every ClearPath fee, late fee, payment and balance.
- **ClearPath monthly fee** (`managed_ext_current_month_fee`: hub "Monthly Fee Invoice for the Current Service Month", baseline "Seat Amount and Billed Seats", factors Sentinel bundle, volume break, server management, frontline F3, Continuum, CSP). In scope for every fee row (current month at its posting, no seat change in that month, no F3/Business Premium subscription, term in force). Task 0: Sentinel MDR Standard active, 36 months, 52 enrolled ≥ 50 seats → 3.0 %; volume (50 billed seats: 11 × 2.0 / 50) 0.44 %; 4 servers × 60.00 = 240.00 → RND(8,977.50 × 0.9656) + 240.00 = **8,908.67** = every seeded fee. Task 1: no Sentinel, no servers; volume (35 × 2.0 + 46 × 4.0) / 120 = 2.1167 % → **16,976.49** = every seeded fee. Baseline prorations (8,977.50; 17,343.60) are outside that scope and follow "Seat Ledger Changes and Proration" (rate × seats × days / days), carried on the next monthly invoice — correct.
- **ClearPath late fees** (`managed_ext_first_late_fee`): each of the four is in scope (the invoice is the agreement's only one with an amount unpaid at the end of the previous day). Task 0 2025-08-01: no late fee and 11 payments in 12 months → 1.0 %; bands 10.00 + 20.00 = 30.00; recent payment 25 % + Sentinel relationship 10 % → 19.50; minimum 10.00 (16 months) → **19.50**. Task 0 2026-07-01: late fee in window → 1.5 %; 45.00; 35 % off → 29.25; minimum 5.00 (27 months) → **29.25**. Task 1 2025-10-01: 1.25 % (2 payments); 37.50; 25 % off → 28.13; tier minimum 35.00 (3 months) → **35.00**. Task 1 2026-03-01: 1.5 %; 45.00; 25 % → 33.75; minimum 35.00 → **35.00**. All equal the seed; late-fee timing complete (no further assessment due by either frozen time; the 108.67 left on task 0's September invoice is not past grace before 2026-11-01).
- **Payments and balances**: every invoice except task 0's September (108.67 open) and the two October fees is paid in full; balances 9,017.34 and 16,976.49 reconcile; payment application by named remittance.
- **ClearPath agreements, seats, tickets**: signing rates 179.55 / 144.53; onboarding waived (36 months) / 9,000.00 paid 2025-05-16 before onboarding 2025-05-19; seat baselines 50 / 120 with no ticket; task 0's draw tickets P4, first response 29 minutes against the Premier P4 guarantee of 480 coverage minutes — no breach, no credit; billable minutes route to TimeBank.
- **TimeBank** (charter): prices, orders, invoices, payments, activation on payment, expiry, earliest-expiry-first draws, conversion minutes / 60 at the technician business-hours band — correct.
- **Sentinel** (base docs): rates 10.72 / 22.56 (36-month 6 % off list, no bundle discount at the 2024-01-08 order), 604.80 monthly from 2024-02, onboarding 750.00, IR hours 0 — correct.
- **Hardware** (published extended set): both orders are Accessory & Peripheral Orders (deposit 0 %, outside the endpoint and infrastructure deposit schedules); within the 50,000.00 credit limit; unit prices cost × 1.19 (ClearPath rank ≥ 3 on each quote date), handling 15.00, no staging or rush; final invoices on delivery; late fees 1.5 % above the 25.00 minimum after the 5-day grace; closed when paid after the 30-day return window (later than the 15-day DOA window). Observation O14: the published closing sentence ("closes on the day after the later of … provided nothing is owed") does not say on which day an order that was still owing then closes; the seed closes on the payment day, as the base lifecycle reads. No scored effect.
- No remaining member found.

### findings (revision_9)
- **S1 — closed, gold unchanged.** The ClearPath rows now follow the published schedule. Task 0's deposit re-derived from the r9 view: client standing −5 (one ClearPath late fee in 12 months: 2026-07-01), hardware +5, start lead +2.5, ACH −2.5 (three ACH payments in six months: 2026-06-24, 07-24, 08-25 — the 2026-09-24 payment is now a check; boundary ach_mid_count 3), open balance +5.0 (balance due 9,017.34 ≥ the rule's monthly seat charge 50 × 179.55 = 8,977.50) → 30 % × 46,926.00 = **14,077.80** (substitutions 16,424.10 / 11,731.50 / 12,904.65 / 15,250.95 / 11,731.50 / 22,524.48; baseline 18,770.40). The KB audit's 12,904.65 assumed a balance of 8,908.67; the short-paid September invoice keeps the full open-balance tier. Observation O15: the deposit rule's "monthly seat charge" is defined as seat_count × seat_rate_usd (8,977.50), which is no longer the fee the published ClearPath schedule bills (8,908.67); the rule defines its own term, so one reading.
- **S2 — closed** (16,976.49 on every task-1 fee; no task-1 factor reads ClearPath amounts).
- **S3 — closed** (all four late fees per the published schedule, above).
- **S4 — closed.** No "one_late_deposit_pct" or "step 8" left in 0.json; proof-text sweep of both task files (design_rationale, prerequisite_closure, solvability_contract, evaluation_criteria, computations) finds every ClearPath figure current (8,908.67; 9,017.34; 17,886.17; 19.50; 29.25; 16,976.49; 34,320.09; 35.00) and the base 8,977.50 / 17,343.60 used only for prorations and the rule's seat charge.
- Rate lock, milestone, re-pricing, CO fee and remobilization re-run on r9: 13.1; 50,592.00 / 8,205.76 / 354.87 / 3,935.13 (unchanged — task-1 factors read ClearPath tier, seats and late-fee counts only).

### closing_checklist (revision_9)
- Revision_9 appended to all three files. Charter and tools unchanged; trees, factor weights and GT (re-checked 2026-10-18T14:21:34Z) unchanged and equal to the re-derivation. Both tasks PASS; no charter finding; observations O1, O4, O5, O6, O8, O10–O15 carry no consequence.

VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN
