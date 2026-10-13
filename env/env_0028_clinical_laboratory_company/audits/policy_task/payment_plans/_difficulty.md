# Policy-task audit — payment_plans / charter-global

## charter_global_frozen

- Auditor: independent policy-task auditor (Claude agent, erl-task-policy-audit), not the instantiating agent.
- Freeze time: 2026-10-04 (UTC wall clock of the audit host), written before any task GT was revealed.
- Freeze hashes (sha256, re-computed by the auditor and equal to `audits/_views/policy_task/payment_plans/HASHES.txt`):
  - `tasks/payment_plans/plans.extended.yaml` 0e34b8dc49cd89ba64928c13c69a5e4c9b87b7524ac1cea9ae786069fbe1cf11
  - `tasks/payment_plans/task_tools.py` dd910fe148e596148cebef7d56be0c27bd53b8a5f034f80d1c449dd3ee96f864
  - `task0.view.json` 2c36a2e434f807a2c4906f9ac3c68adc67f186ab7dee2114cd8a94302bff4aeb; `task1.view.json` f58facbab35e42ff6759c38ac18b507a3a8f6a4753722017efcea000b7b3c9e7
- Fields read for this section: `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, `blueprint/products/plans.yaml` (and `assistance.yaml` variant parameters for `discount_pct`), the whole `plans.extended.yaml`, the whole `task_tools.py`, `erlbench/scoring.py` (exact-hash scoring and order check), and the DSL evaluator in `skills/erl-task-instantiate/scripts/check_compute.py` (semantics of SUM/COUNT/MONTHS/CFIELD/XSUM; read, not run on tasks).
- Masked and not read for this section: every field of `tasks/payment_plans/tasks/*.json` other than the masked views (evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure), the instantiation worklog, and any prior audit. Nothing in this section is derived from a revealed GT.

Entry conditions (Step 0): the gate snapshot came with the brief (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire all OK; check_traceability deferred because the KB is not rendered). Masked views and hashes were supplied. Entry conditions met; the deferred traceability gate is recorded, not run.

Base copy: every top-level key of `plans.extended.yaml` other than `extended_policies` is byte-for-byte equal (parsed) to `blueprint/products/plans.yaml` (category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies all equal). The base section is verbatim.

### policy_conflict_scan

Extended policies (6) and their subjects:

| policy | subject | target_tool (owner) | computes | prerequisite |
| --- | --- | --- | --- | --- |
| plans_ext_catch_up_payment | plans_installment_paid | pay_catch_up_2a071954 (user) | amount | [] |
| plans_ext_add_on_down_payment | plans_installment_paid | pay_add_on_down_payment_958d6e13 (user) | amount | [] |
| plans_ext_relief_installment | plans_schedule_changed | reset_relief_installment_53948494 (agent) | installment_amount | catch_up (value_input, state) |
| plans_ext_added_invoice_installment | plans_invoice_enrolled | add_invoice_to_plan_14a3a600 (agent) | installment_amount | relief (value_input, action); add_on (value_input, state) |
| plans_ext_reinstatement_payment | plans_installment_paid | pay_reinstatement_amount_fe9b74b8 (user) | amount | [] |
| plans_ext_reinstated_installment | plans_reinstated, plans_invoice_enrolled | reinstate_plan_60f00772 (agent) | installment_amount | reinstatement_payment (value_input, state) |

Overlaps scanned:

- Three policies share subject `plans_installment_paid` (catch-up, add-on down payment, reinstatement payment). They are separated by the plan status and situation stated in their own rules: catch-up "to bring a past-due plan back to current standing"; reinstatement payment "on a defaulted plan inside its reinstatement window"; add-on "when an invoice is added to a plan already accepted whose term carries a down payment". Catch-up and reinstatement payment post the same ledger row type (`payment_type=arrears_cure`), but on disjoint plan statuses (past_due vs defaulted). No overlap in conclusion.
- Two policies write `plans_invoice_enrolled` (added-invoice on an accepted plan, reinstated-installment on a defaulted plan); disjoint by plan status (base `plan_open_for_enrollment` amended by the reinstated policy's declared overwrite for the defaulted re-enrollment).
- Base eligibility inherited and not weakened: schedule change only while active (base plans_evt_schedule_changes, line 885) — relief is reached only after the catch-up tool sets status active; add-invoice only while active (line 730) — likewise; payments on a defaulted plan only "as the arrears payment that precedes a reinstatement" (line 776) — matches the reinstatement payment; reinstatement count and window (plans_evt_reinstatement) — not touched by extended.
- Cross-category reads: assistance (approved case, `discount_pct`, `household_size`, document events), coverage (`status='active'`), invoices (open invoice `balance_due`, `variant_name`, invoice payments). All are reads; no extended policy writes another category.
- Claimed scope: two tasks. From the policy graph alone the charter decomposes into two trees: {added_invoice ← relief ← catch_up; added_invoice ← add_on} and {reinstated ← reinstatement_payment}. These are disjoint and jointly cover all six extended policies. (Per-task scopes are checked against each task's world in the task files; the GT `charter_scope` is masked here.)

Conflict findings from the scan are listed under `override_declarations` and `findings` (F1, F2).

### rule_compute_equivalence

Mechanical sweep: every `compute_basis` value was checked sentence by sentence to be a verbatim substring of the policy's own `rule` (whitespace-normalised). All pass (two bases — add_on `result`, added_invoice `n_respread` — quote two non-adjacent rule sentences; each sentence is present). Every baseline.rule sentence is a sentence of its rule. Every ladder tier corresponds to a branch of the `decides` binding and vice versa (checked by reading each factor against its binding; all six policies).

Divergences found by reading the rule against the compute (not caught by the substring sweep):

1. **added_invoice: held installments in the layered method (F2, RED).** Rule line 1574: "The held installments are taken out of the amount spread at the standing installment and out of the installments counted." This sentence is unconditional and follows the three folding methods. Compute implements it only in the re-spread branch: `n_respread: (n_carried + n_added_net - n_lead * n_inst) / (n_respread_count - n_lead)`; the layered branch takes the held installments out of the count only: `n_layered: n_inst + n_added_net / (n_layer_count - n_lead)`. compute_basis confirms the split (n_respread quotes the held sentence, n_layered does not). The rule promises a subtraction from "the amount spread" that the layered branch does not perform. Consequence demonstrated in task 0.
2. **added_invoice: cap on the extended re-spread (observation).** Rule: "the re-spread runs over the installments still to fall due under the term plus the term's add-on extension months" and "The installments an added invoice may be spread over are capped by the patient's standing". Compute: `MN(n_term_remaining, n_limit) + extension` — the cap is applied before the extension months are added, so the total can exceed the cap; a reader can as well apply the cap to the total. Neither task's world takes the `respread_extended` branch (task 0 is layered), so no consequence is demonstrable.
3. **"approved award" vs `discount_pct > 0` (observation).** Rules say "a patient with an approved award" (relief document and coverage months, reinstated award months, add-on 7.5% tier "an approved award below 50 percent"); compute tests `c_award_pct > 0`, `r_award_pct > 0`, `s_apct > 0`. An approved Catastrophic Medical Hardship Adjustment has `discount_pct: 0` (assistance.yaml) and is an approved award by the rule but not by the compute. `n_award`/`r_award_on_file`/`b_award` use `EXISTS(status='approved')` instead, so the charter is internally inconsistent on this input. Neither task holds a hardship award; no consequence demonstrable.
4. **"payments posted ... since the default" (observation).** reinstated `r_direct: XSUM(..., within_months=MONTHS(F('defaulted_date'), NOW) + 1, ...)` is a whole-month window, which also admits invoice payments posted before the default date inside the same month bucket. Task 1's only invoice payment (2026-10-02) is after the default, so no consequence.
5. **Rounding ties (finding F4, consequence in task 1).** Every rule says "rounded to the nearest cent" / "taken to the cent"; no sentence of the charter (base `installment_rounding: cent_final_absorbs` included) fixes the tie rule, and the compute's `RND` is Python `round`, which rounds an exact half-cent to even. Wherever an intermediate lands exactly on a half cent, half-up and half-even readers differ by one cent, and scoring is an exact DB-hash match (`erlbench/scoring.py`, `match = predicted == target`).

No compute binding was found that invents a basis absent from the rule other than items 1–4.

### action_binding_and_uuids

- `(target_tool, computes)` pairs are six distinct pairs, each claimed by exactly one policy.
- uuid8s: 2a071954, 958d6e13, 53948494, 14a3a600, fe9b74b8, 60f00772 — no shared prefix or tail, no sequence, no adjacency; each appears once in the module. Pass.
- Function bodies (task_tools.py): every tool does `ctx.find` on the plan and a `create`/`update`; none branches on status, amount, date or ledger content, none refuses or hints. The tool layer judges no prerequisite. Effects: catch-up posts `arrears_cure` and sets `status='active'`; add-on posts `down_payment` dated today, status unchanged; relief updates `installment_amount` only (no ledger line); add-invoice posts `plans_invoice_enrolled` and sets `installment_amount`; reinstatement payment posts `arrears_cure`, status unchanged; reinstate posts `plans_invoice_enrolled`, sets active, increments `reinstatement_count`, sets `installment_amount`.
- Docstrings: none names another tool or states a position in a sequence. Observation: `reset_relief_installment_53948494` says "Sets a new regular monthly installment ... once a financial-assistance release has lowered the plan's balance" — an ordering word, but anchored to a release that no tool of this difficulty writes (it is seeded history), so it orders no task write.

### prerequisite_graph

- Every extended policy carries `prerequisite` (`[]` for catch-up, add-on, reinstatement payment). Every `problem` names another extended policy in this file; none names a base policy or itself.
- Graph: catch_up → relief → added_invoice ← add_on; reinstatement_payment → reinstated. Acyclic.
- Each `policy_source` is verbatim in its own policy's `rule` (checked mechanically); none is restated in the depended-on policy's rule (checked).
- `form`/`fallback_reason`: relief→added is `action` and carries a fallback_reason; the other three are `state` with no fallback_reason. Consistent.
- `resolved_by` equals the depended-on policy's `target_tool` on all four edges.
- `gate`/`kind`: all four are `value_input`; each `gate` is a binding of the blocked policy's compute (`c_carried`, `n_inst`, `n_addon_down`, `r_ledger`), and each depended-on write changes that binding's value (arrears line enters `c_carried` and `r_ledger`; the relief write sets `F('installment_amount')` read as `n_inst`; the add-on line enters `n_addon_down`).
- `condition` wording vs the sentence: relief←catch_up "On a plan whose status is past_due, plan_transactions holds ... arrears_cure whose event_date is on or after the event_date of the plan's latest plans_installment_missed line" — same strength as the sentence. added←add_on "... payment_type down_payment whose event_date is after payment_plans.accepted_date and whose amount is the add-on down payment owed" — the clause "whose amount is the add-on down payment owed" is narrower than the sentence ("carries the down payment owed on that invoice"), but it restates "owed"; not a strengthening of substance. reinstated←reinstatement_payment matches. added←relief "payment_plans.installment_amount equals the relief installment worked out for the financial-assistance release standing on the plan ledger" — matches the action sentence.
- No authoring-viewpoint phrasing ("in this task", "at the opening") in any `prerequisite` field.

### prerequisite_sentences

Four-point test, per edge:

1. relief ← catch_up (state). "A relief installment is not set on a past-due plan until the plan ledger carries an arrears payment dated on or after the date of the plan's latest missed-installment line." Ordering connective "not ... until"; waits on a record-visible ledger state (an arrears payment dated on/after the latest missed line); no tool, id or snake_case token; scope "a past-due plan" equals the condition's. Which write brings the state about: two tools post `arrears_cure` lines (catch-up and reinstatement payment), but the reinstatement payment's own rule confines it to "a defaulted plan", while the sentence is scoped to "a past-due plan", whose payment is the catch-up ("the payment a patient makes to bring a past-due plan back to current standing; it is posted on the plan ledger as an arrears payment against the plan's latest missed installment"). One reading. Pass.
2. added ← add_on (state). "The installment of a plan taking on another invoice is fixed only after the plan ledger carries the down payment owed on that invoice, posted as a down payment dated after the plan's acceptance date." Connective "only after"; record-visible state; no tool/id. Only the add-on tool posts a `down_payment` line after acceptance; the add-on rule names this payment ("it belongs to the invoice being added, and it is posted on the plan ledger as a down payment dated the day it is paid"). One reading. Pass.
3. added ← relief (action, fallback). "Before the installment of a plan taking on another invoice is fixed, the relief installment owed for a financial-assistance release already standing on the plan ledger is set." Connective "Before"; names the depended-on action in business words; no tool/id. Derivation: the relief policy's rule opens "the relief installment is the regular monthly installment set on the plan once a financial-assistance release has been booked on its ledger" — the only policy whose rule sets that figure. One reading. Fallback test: the relief write leaves no ledger line (tool body updates `installment_amount` only). A record-visible candidate state exists — "the installment standing on the plan differs from the installment set at acceptance", which the added-invoice rule itself uses in its count-reading factor — but it would not single out the relief write (add-invoice and reinstate also set the installment), so the fallback is defensible. Observation O3 names that state.
4. reinstated ← reinstatement_payment (state). "A reinstated installment is fixed only after the plan ledger carries an arrears payment dated after the plan's default date." Connective "only after"; record-visible; on a defaulted plan the only arrears payment is the reinstatement payment (catch-up is confined to past-due plans). One reading. Pass.

Undeclared cross-problem orders in extended rules: none found. Base sentences stating an order: plans_evt_installments "on a defaulted plan only as the arrears payment that precedes a reinstatement" (line 776) — it restates the reinstated policy's own declared edge; the extended rule carries its own sentence, so it is an observation (O4), not a red. Base state gates "The schedule of a plan can be changed only while the plan status is active" and "After acceptance an invoice may be added ... only while the plan is active" also make the catch-up a gate of the relief and of the add-invoice write; the catch-up is already in that tree, so the order they imply equals the declared one (O4).

### override_declarations

Swept sentence by sentence against each `base_policy_refs` entry.

- **catch_up** (refs plans_evt_installments, plans_evt_delinquency). Declared: the partial-payment sentence of plans_evt_installments ("A payment below the installment due counts toward it only when partial_installment_accepted is true; otherwise it is applied as extra principal and the installment is still owed.") replaced by "Extra-principal payments posted on a past-due plan count toward the catch-up payment as this rule sets out, even where each of them is smaller than an installment." Not declared, and handled differently: plans_evt_installments "Extra principal reduces the balance without moving the schedule when extra_principal_allowed is true" and plans_evt_delinquency "It becomes current again only when every past-due installment is paid in full (cure_requires_full_past_due)". The catch-up rule counts extra-principal payments by a look-back window of 1, 2 or 3 whole months regardless of the plan's status when they were posted, so an extra-principal payment posted while the plan was current (which under the surviving base sentence did not move the schedule and left the next installment owed in full) is credited toward the missed installment, and the catch-up tool returns the plan to active. The declared replacement covers only payments "posted on a past-due plan". → **F1 (SOURCE-POLICY RED)**, consequence demonstrated in task 0. Also the missed-installment span (3/6 months) drops older missed installments from the amount that "brings a past-due plan back to current standing", which conflicts with "every past-due installment is paid in full" whenever an older missed installment is still unpaid; in task 0 the older missed installment is shown settled on the ledger, so that branch has no demonstrable consequence there (observation).
- **add_on** (refs plans_evt_installments, plans_term_selection_and_terms), `overwrite: []`. Base sets the acceptance down payment ("down_payment_pct percent of the enrolled balance ... due at acceptance") and the add-invoice conditions; neither base sentence governs a down payment on an invoice added after acceptance. The add-on charge is a new requirement layered on necessary conditions ("only where/only while"), not a contradiction of a base sentence. No undeclared override found (observation O5: the charge itself has no base counterpart).
- **relief** (refs plans_evt_schedule_changes, plans_evt_release_and_assistance). Declared: "the installment is recomputed over the remaining installments when assistance_adjustment_reamortizes is true" replaced. Base "The schedule of a plan can be changed only while the plan status is active" is inherited, and the extended sentence "A relief installment is not set on a past-due plan until ..." is compatible with it only because the catch-up write returns the plan to active (tool effect). "A skip does not change the installment amount" — not touched. Pass.
- **added_invoice** (refs plans_agg_invoice_consolidation, plans_evt_invoice_eligibility, plans_evt_release_and_assistance). Declared: the re-amortize/extension clause replaced. Inherited and not weakened: invoice open, billing class, active plan, max_invoices_per_plan, max_enrolled_balance. Pass.
- **reinstatement_payment** (refs plans_evt_installments, plans_evt_reinstatement). Declared: "The patient must first pay every missed installment in full;" replaced by "The reinstatement payment of a defaulted plan is the amount this rule sets out, in place of every missed installment paid in full." The replacement is broad enough to cover the extra-principal credit and the span. Pass.
- **reinstated_installment** (refs plans_evt_reinstatement, plans_evt_invoice_eligibility, plans_agg_invoice_consolidation). Declared: re-enrollment "with the original schedule" replaced; enrollment-state sentence extended to the defaulted re-enrollment. Inherited: window, count, "An invoice placed in collections since the default is not re-enrolled". Pass.

### factor_ladders

Per policy (label as declared → auditor's reading of the label):

| policy | factor | declared | decides | tiers | auditor |
| --- | --- | --- | --- | --- | --- |
| catch_up | catch_up_credit_share | parameter | b_share | 3 (½ / ¼ / whole) | parameter; multi-source (missed count on ledger + plan autopay method) |
| catch_up | catch_up_credit_span | method | b_credit_span | 3 (3 / 2 / 1 months) | **a look-back length (number) fed to the same `SUM(..., within_months=b_credit_span)`** — parameter, mislabelled |
| catch_up | catch_up_missed_span | method | b_missed_span | 3 (3 / 6 months / none) | **a look-back length fed to the same `SUM(..., within_months=b_missed_span)`** — parameter, mislabelled; fall-through see F5 |
| catch_up | catch_up_minimum | parameter | b_min_share | 3 (¼ / ½ / 1) | parameter |
| add_on | add_on_down_payment_rate | parameter | s_rate | 3 (5 / 7.5 / term %) | parameter; cross_difficulty assistance; multi-source |
| add_on | add_on_class_scale | parameter | s_class_scale | 3 (½ / ¾ / 1) | parameter (cross-category invoices) |
| add_on | add_on_missed_span | method | s_span | 3 (3 / 6 / 12 months) | **look-back length fed to the same `COUNT(..., within_months=s_span)`** — parameter, mislabelled |
| add_on | add_on_invoice_count_scale | parameter | s_invoice_scale | 3 (1.5 / 1.25 / 1) | parameter |
| add_on | add_on_minimum | parameter | s_minimum | 3 (5 / 10 / 25) | parameter |
| relief | relief_award_months | parameter | c_award_months | 3 (2/1/0) | parameter; cross_difficulty assistance; both tier conditions read one assistance row (not multi-source) |
| relief | relief_document_months | parameter | c_document_months | 3 (1/2/0) | parameter; cross_difficulty assistance (assistance_events) |
| relief | relief_standing_months | parameter | c_standing_months | 3 (2/1/0) | parameter; multi-source (plan accepted_date + ledger count) |
| relief | relief_coverage_months | parameter | c_coverage_months | 3 (2/1/0) | parameter; reads coverage (declared cross_difficulty null) |
| relief | relief_invoice_months | parameter | c_invoice_months | 3 (1/2/0) | parameter |
| relief | relief_floor | method | c_floor | 3 (15% of standing / 30.00 fixed / term minimum) | accepted as method: the first tier computes the floor as a proportion of the standing installment, the others take fixed amounts (O6: borderline) |
| added_invoice | added_invoice_folding | method | n_method | 3 (layered / extended re-spread / re-spread) | genuine method |
| added_invoice | added_invoice_count_reading | method | n_counted | 3 (quotient nearest / quotient up / remaining term) | genuine method |
| added_invoice | added_invoice_spread_cap | parameter | n_limit | 3 (18/12/9) | parameter |
| added_invoice | added_invoice_down_payment_netting | parameter | n_net_share | 3 (1/½/0) | parameter |
| added_invoice | added_invoice_held_installments | parameter | n_lead | 3 (1/2/0) | parameter |
| added_invoice | added_invoice_rise_cap | parameter | n_rise | 3 (100/75/25) | parameter |
| reinstatement_payment | reinstatement_missed_span | method | q_span | 3 (3 / 2 months / none) | **look-back length fed to the same `SUM(..., within_months=q_span)`** — parameter, mislabelled; fall-through see F5 |
| reinstatement_payment | reinstatement_fallen_due_share | parameter | q_fallen_share | 3 (1 / ½ / 0) | parameter |
| reinstatement_payment | reinstatement_deposit | parameter | q_deposit_share | 3 (0 / ¼ / 1) | parameter; cross_difficulty assistance |
| reinstatement_payment | reinstatement_principal_credit | parameter | q_credit_share | 3 (1 / ½ / 0) | parameter |
| reinstated | reinstatement_reenrolled_basis | method | r_basis | 3 (invoice balance now / release less payments / release) | genuine method; multi-source (invoice payments + plan autopay) |
| reinstated | reinstatement_installment_count | method | r_counted | 3 (quotient down / quotient up / remaining term) | genuine method |
| reinstated | reinstatement_award_months | parameter | r_award_months | 3 (3/2/0) | parameter; cross_difficulty assistance |
| reinstated | reinstatement_household_months | parameter | r_household_months | 3 (2/1/0) | parameter; cross_difficulty assistance |
| reinstated | reinstatement_held_installments | parameter | r_held | 3 (2/1/0) | parameter |
| reinstated | reinstatement_floor | parameter | r_floor_share | 3 (0.3/0.75/1) | parameter |

Structural checks:

- Factor counts 4–6 per policy: catch_up 4, add_on 5, relief 6, added 6, reinstatement_payment 4, reinstated 6. Pass.
- Tiers: every ladder has three pairwise-disjoint tiers as stated (checked each `when` against its compute branch); no two tiers of one ladder select the same value or method. Pass.
- Every tier (condition and value/method) is stated in the rule prose and implemented in compute. Pass.
- Bindings disjoint across factors of one policy; no `decides: result`. Pass.
- Baselines: each `baseline.rule` sentence is in the rule; each factor's baseline equals its fall-through tier. Pass structurally (per-world honesty is in the task files).
- **Method count after striking mislabels (F3, SOURCE-FACTOR RED).** The only `method` factors of catch_up (credit_span, missed_span), add_on (missed_span) and reinstatement_payment (missed_span) choose a look-back length in months for one unchanged aggregate; the tiers substitute a number (3, 2, 1, 6, 12 or "no window") into `within_months` of the same `SUM`/`COUNT`. By the skill's definition that is a `parameter` (a number substituted into the same formula, like a threshold), so those three computations carry 0 genuine `method` factors against a floor of 1. relief keeps 1 (relief_floor, borderline), added_invoice 2, reinstated 2.
- **Fall-through of the missed-installment spans (F5, SOURCE-FACTOR RED where it carries the weight).** catch_up_missed_span and reinstatement_missed_span fall through to "every missed installment and every arrears payment on the plan ledger is counted"; the amount owed is then missed lines less `arrears_cure` lines only. A missed installment later settled by a payment line booked as `scheduled_installment` (with that `installment_number`) is still charged. No laboratory collects, to bring a plan current or to reinstate it, an installment its ledger shows as paid. Whether this bites is per world (both tasks seed exactly such a line — see task files).
- Realism notes (observations): relief tiers conditioned on "an approved award" are reached only by plans that already carry a financial-assistance release, so "approved award" largely restates the policy's scope (it can still fail when an award expired or was rescinded, so not struck) (O7); relief_invoice_months (more invoices on a plan → more relief months) and add_on_minimum (minimum set by the last installment's payment method) are weakly motivated but not shown to be outside what a lab billing office weighs (O7).
- Counts: parameter ≥2 in every policy (pass). Genuine method ≥1: fails in catch_up, add_on, reinstatement_payment (F3). Multi-source factors exist in each tree (catch_up_credit_share / add_on rate / relief_standing / added folding in tree A; reinstatement_reenrolled_basis in tree B). Cross_difficulty factors: assistance in both trees (add_on rate, relief award/document months, relief_floor; reinstatement_deposit, reinstated award/household months).

### findings

- **F1 — SOURCE-POLICY RED (catch_up; bears on task 0).** Symptom: the catch-up counts extra-principal payments posted while the plan was current toward the missed installment and the tool returns the plan to active. Root cause: undeclared override of plans_evt_installments "Extra principal reduces the balance without moving the schedule when extra_principal_allowed is true" together with plans_evt_delinquency "It becomes current again only when every past-due installment is paid in full"; the declared replacement covers only "Extra-principal payments posted on a past-due plan". Evidence: `plans.extended.yaml` lines 776–781, 813–815 (base), 986–991 (overwrite), 1014/1019 (window sentences), compute `b_credit_base: SUM(..., within_months=b_credit_span, payment_type='additional_principal')` (no status filter). Consequence: demonstrated in `0.md` (two readings of the catch-up amount).
- **F2 — SOURCE-POLICY RED (added_invoice; bears on task 0).** Rule line 1574 vs `n_layered` (see rule_compute_equivalence item 1). Consequence: demonstrated in `0.md`.
- **F3 — SOURCE-FACTOR RED (catch_up, add_on → task 0; reinstatement_payment → task 1).** Look-back-length factors labelled `method`; after relabelling, those computations have no `method` factor. Demonstration: in each, the tiers only change the `within_months` argument of one unchanged aggregate (compute lines 1036–1040, 1200–1201, 1841–1843).
- **F4 — rounding tie unresolved by the charter (bears on task 1).** No sentence fixes how an exact half cent rounds; consequence demonstrated in `1.md`.
- **F5 — fall-through of missed-installment spans charges settled installments (catch_up → task 0; reinstatement_payment → task 1).** Weight demonstration per task file.
- Observations: O1 extended re-spread cap order (item 2); O2 approved award vs `discount_pct > 0` (item 3); O3 action-form fallback (candidate state named); O4 base sentences that restate/imply the same orders; O5 add-on charge has no base counterpart; O6 relief_floor method label borderline; O7 ladder realism notes; O8 `r_direct` month-bucket window (item 4); O9 relief_coverage_months reads another difficulty (coverage) but is declared `cross_difficulty: null` (metadata only).

## closing_checklist

Written after both reveals. The difficulty is **not closed**: the four relationships do not all PASS.

- Audit files: `0.md` and `1.md` correspond one-to-one with `tasks/0.json` and `tasks/1.json`; this file sits alongside them. First revision, so there are no older revisions. Comparison sections: task 0 — SOURCE-POLICY RED + SOURCE-FACTOR RED; task 1 — SOURCE-TASK RED + SOURCE-FACTOR RED.
- Coverage and scope:
  - Revealed `charter_scope`: task 0 = {catch_up, relief, add_on, added_invoice}; task 1 = {reinstatement_payment, reinstated}.
  - The two scopes are pairwise disjoint and jointly cover all six extended policies and all six task tools. This matches the decomposition derived blind.
  - The uuid8s are independent (§ action_binding_and_uuids).
- Problem trees:
  - Task 0 has 3 prerequisite problems, 3 value_input edges and 2 user writes.
  - Task 1 has 1 prerequisite problem, 1 value_input edge and 1 user write.
  - The difficulty-wide graph is acyclic. PASS.
- Factors: FAIL.
  - F3: the catch-up, add-on and reinstatement-payment computations have no genuine `method` factor.
  - F5: catch_up_missed_span and reinstatement_missed_span carry their weight only by charging settled installments.
  - Every factor's substitution moves the scored value, and every whole-baseline fall-back differs from gold.
- Policy self-consistency: FAIL. F1 (undeclared override in the catch-up) and F2 (held-installment sentence vs the layered compute) each give task 0 a second defensible value. F4 (no rounding-tie rule) gives task 1 a second defensible value.
- Instantiation gates on the final form: not re-run. The artifacts are unchanged since the coordinator's snapshot (hashes in § charter_global_frozen), and the difficulty does not close in this round.

## revision_2

### charter_global_frozen (revision 2)

- Re-audit round 2 by the same independent auditor. Written 2026-10-04 ~18:05 UTC, before any round-2 task GT was revealed.
- Hashes (re-computed; equal to the round-2 `HASHES.txt`): `plans.extended.yaml` 59042d40254be187bc4a777135740c7514c924ca7be2ef61e1dc6ba568e42e4e; `task_tools.py` 5dd8bfb4f95cd5d7d6e75c4e1e45044db155d73a1b355fe08542191b984f2215; `task0.view.json` a999a5d2…a9e5; `task1.view.json` 2b88fd68…db35.
- Both shared inputs changed since round 1 (round-1 hashes 0e34b8dc… / dd910fe1…). Every charter-global section is therefore re-derived in full below, and nothing is carried forward by reference.
- Entry conditions: the coordinator's round-2 gate snapshot (all seven gates OK, traceability deferred) and the rebuilt masked views were supplied. Met.
- Fields read and masked: as in round 1. The round-1 sections above are left untouched.
- contamination_disclosure: the auditor read the round-1 GT of both tasks during round 1 (see `0.md`/`1.md` source_gt_comparison). The coordinator states that the worlds and scored values changed, and no round-2 task JSON was opened before the freezes below. The round-1 knowledge covers conventions (for example layering, and that GT values follow the DSL `RND`), not round-2 values. It is disclosed here rather than hidden.
- Base copy: every key other than `extended_policies` still parses equal to `blueprint/products/plans.yaml`.

### policy_conflict_scan (r2)

- Six extended policies with the same ids, targets, subjects and prerequisite graph as round 1 (catch_up → relief → added_invoice ← add_on; reinstatement_payment → reinstated).
- Subject overlaps resolve as in round 1, by plan status (past_due / accepted plan with an add / defaulted).
- Base eligibilities are inherited unweakened.
- From the policy graph alone, the charter still decomposes into two disjoint trees that together cover all six policies.

### rule_compute_equivalence (r2)

Mechanical sweep: every sentence of every `compute_basis` value and of every `baseline.rule` is a verbatim sentence of its own rule. Pass. Read-through, item by item:

- **Catch-up (rewritten).**
  - Missed amounts are now taken over the whole ledger, less arrears.
  - The credit is taken from extra-principal payments that carry the latest missed installment's number: `SUM`/`MAX`/`LATEST` with `installment_number=b_latest_missed_no`.
  - The selection is all / largest / most recent; the share is ½ / ¾ / whole by award and household; the cap is ¼ / ½ / 1 installment by scheduled count; the minimum is as before.
  - The order of operations stated in the rule (credit, then cap, then subtraction, then minimum) matches `b_credit` and `result`. Equivalent.
- **Add-on.**
  - The missed raise is now a three-way method: flat ¼ for the latest missed only / compounding `1.25 ** n` / the step ½ / ¼.
  - The award test is now `EXISTS(approved)` with the hardship case named in the rule. Equivalent.
- **Relief.** `c_award = EXISTS(approved)` now drives the document and coverage tiers, matching "an approved award". Equivalent.
- **Added invoice.**
  - The held-installment sentence now distinguishes the two methods: "In a re-spread the held installments are taken out of the amount spread at the standing installment and out of the installments counted; in a layering the balance of the added invoice is spread over the installments counted less the held installments, and the held installments keep the standing amount without anything being taken out of the added balance". This matches `n_respread` and `n_layered`.
  - The cap's position is stated ("the cap applies to the installments counted or still to fall due before any add-on extension months are added"), matching `n_respread_count`. Equivalent.
- **Reinstatement payment (rewritten).**
  - Missed amounts are taken over the whole ledger, less arrears.
  - The credit selection is check-paid only / most recent / all, within 6 months; `q_extra_latest` has no window, but it is guarded by `q_extra_all > 0`, so the latest row is inside the window whenever any row is. The share is ½ / ¾ / whole; the deposit is keyed on `EXISTS(approved)`. Equivalent.
- **Reinstated.** The `r_direct` window is now described in the rule ("the calendar-month window that runs back from today over the whole months elapsed since the default date plus one"), and the award months are keyed on `EXISTS(approved)`. Equivalent.
- **Rounding (R2-F1, new form of round-1 F4).**
  - Every extended rule now says "rounded to the nearest cent, an exact half cent being rounded up" (catch-up, add-on, relief, added invoice, reinstatement payment, reinstated).
  - The DSL primitive the compute uses for every one of those roundings is unchanged: `"RND": lambda x, n=2: round(float(x), n)` (`check_compute.py` line 388). That is Python's binary-float round-half-to-even, which rounds an exact half cent down whenever the cent digit is even.
  - So the rule and the compute disagree on every exact half cent. Whether a world hits one is per task; task 1 does (see `1.md` revision_2).
  - Observation: the added-invoice count reading ("to the nearest whole installment", `RND(x, 0)`) and the acceptance installment ("rounded to the cent") state no tie rule. Task 0's quotient is an exact integer, so there is no consequence.

### action_binding_and_uuids (r2)

- Six distinct `(target_tool, computes)` pairs; the uuid8s are unchanged and independent.
- Owners: catch-up, add-on and reinstatement payment are user tools; relief, add-invoice and reinstate are agent tools.
- Function bodies are unchanged in effect: plain `find` + `create`/`update`, no refusals or branches.
- The relief docstring now reads "to reflect a financial-assistance release booked on the plan", with no ordering word. The round-1 docstring observation is closed.
- No docstring names another tool or a sequence position.

### prerequisite_graph and prerequisite_sentences (r2)

- The four edges are unchanged in `problem`, `kind`, `gate`, `form`, `policy_source`, `condition`, `resolved_by` and `fallback_reason`.
- Each `policy_source` is still verbatim in its own rule and absent from the depended-on rule; the graph is acyclic.
- The four-point test and the single-reading derivations of round 1 still hold: arrears lines on a past-due plan come from the catch-up, on a defaulted plan from the reinstatement payment; only the add-on posts a post-acceptance `down_payment`; the relief rule alone sets the relief installment.
- O3 (action-form fallback) and O4 (base sentences that imply the same orders) are unchanged.

### override_declarations (r2)

- **Catch-up.**
  - The declared overwrite now replaces the partial-payment sentence with "An extra-principal payment posted on the plan ledger against the latest missed installment, carrying that installment's number, counts toward the catch-up payment as this rule sets out, even where it is smaller than an installment; an extra-principal payment carrying no installment number reduces the balance without moving the schedule and never counts toward the catch-up payment."
  - Payments that carry no number now follow the surviving base sentence ("Extra principal reduces the balance without moving the schedule"). Numbered payments against a missed installment are partial payments of that installment, which is exactly the superseded clause's subject.
  - plans_evt_delinquency "paid in full": the catch-up equals the missed amounts less arrears less a credit that never exceeds what was actually posted against the installment. The arrears plus all numbered payments therefore always cover the past-due installments, because the share and the cap only make the patient pay more.
  - No undeclared override remains. **Round-1 F1 closed.**
- **Add-on, relief, added invoice, reinstatement payment, reinstated.** Declarations are as in round 1 (unchanged wording). The rewritten reinstatement-payment credit is covered by the broad declared replacement ("the amount this rule sets out, in place of every missed installment paid in full"). Pass.

### factor_ladders (r2)

| policy | factor | label | tiers | auditor |
| --- | --- | --- | --- | --- |
| catch_up | catch_up_credit_selection | method | all / largest single (`MAX`) / most recent (`LATEST`) | genuine method (different aggregate); multi-source (missed count + autopay method) |
| catch_up | catch_up_credit_share | parameter | 1 / ¾ / ½ | parameter; cross_difficulty assistance (approved + household on one row) |
| catch_up | catch_up_credit_cap | parameter | 1 / ½ / ¼ installment | parameter |
| catch_up | catch_up_minimum | parameter | ¼ / ½ / 1 | parameter |
| add_on | add_on_down_payment_rate | parameter | 5 / 7.5 / term % | parameter; assistance; multi-source |
| add_on | add_on_class_scale | parameter | ½ / ¾ / 1 | parameter |
| add_on | add_on_missed_raise | method | flat ¼ for the latest only / compounding per missed / step | genuine method (three different formulas) |
| add_on | add_on_invoice_count_scale | parameter | 1.5 / 1.25 / 1 | parameter |
| add_on | add_on_minimum | parameter | 5 / 10 / 25 | parameter |
| relief | 5 month factors + relief_floor | as round 1 | — | unchanged; relief_coverage_months now `cross_difficulty: coverage` (O9 closed) |
| added_invoice | 6 factors | as round 1 | — | unchanged |
| reinstatement_payment | reinstatement_fallen_due_share | parameter | 1 / ½ / 0 | parameter |
| reinstatement_payment | reinstatement_deposit | parameter | 0 / ¼ / 1 | parameter; assistance |
| reinstatement_payment | reinstatement_credit_selection | method | check-paid only / most recent / all | genuine selection method; multi-source (autopay + payment method on ledger) |
| reinstatement_payment | reinstatement_credit_share | parameter | 1 / ¾ / ½ | parameter; assistance |
| reinstated | 6 factors | as round 1 (floor_award now 25%) | — | unchanged structure |

- Counts:
  - Factors: 4–6 per policy.
  - `parameter` ≥ 2 everywhere.
  - Genuine `method` ≥ 1 everywhere: catch_up 1, add_on 1, relief 1 (borderline as before, O6), added 2, reinstatement_payment 1, reinstated 2. **Round-1 F3 closed.**
- Ladder structure: every ladder still has three pairwise-disjoint tiers, each tier stated in the rule and implemented in compute, and no duplicate values.
- The window-length factors are gone. The missed amounts in the catch-up and the reinstatement payment are now whole-ledger missed lines less arrears, which is correct only if every settled missed installment is booked as an arrears payment; both round-2 seeds do so (see task files). **Round-1 F5 closed at the charter level.**
- Realism observations (O7, extended):
  - The new credit selections ("only the largest single one" of the payments posted against the missed installment, for frequent bank-autopay missers; "only the payments made by check" for manual payers) and the ½ fall-through share credit less than what the patient actually posted against an installment.
  - These are penalties a billing office could choose, but they are weakly motivated. They are recorded as observations, not demonstrated as unreal.

### findings (r2)

- Round-1 F1, F2, F3 and F5: closed (see the sections above). O1, O2, O8 and O9 closed; the relief-docstring observation closed. O3–O7 unchanged.
- **R2-F1 — SOURCE-POLICY (rule/compute non-equivalence on half cents; supersedes round-1 F4).**
  - The rules now fix half-up, while every compute rounding uses Python `round` (half to even).
  - On an exact half cent, a rule-follower and the compute differ by one cent.
  - Consequence to be demonstrated per task (task 1's world contains such a value).
- Observation: no tie rule for "nearest whole installment" (`RND(x, 0)`) or for the acceptance installment ("rounded to the cent").

### findings (r2) — post-reveal correction

- **R2-F1 is downgraded to an observation and round-1 F4 is withdrawn.**
  - The only world value the auditor had cited as an exact half cent, the 25% deposit 36.5625 in task 1, is 3656.25 cents and not a tie; the auditor's arithmetic was wrong in round 1 and in the revision-2 freeze (details in `1.md` § source_gt_comparison (revision 2)).
  - The rule/compute divergence on true half cents (rules say half up; `RND` is Python half-to-even on binary floats) is real as a latent property of the charter. No gold value of either round-2 world lands on a true half cent (verified for task 0, as its rationale also asserts; task 1 has none).
  - So no consequence is demonstrable, and it stays an observation.

### closing_checklist (revision 2)

- Audit files: `0.md` and `1.md` correspond one-to-one with `tasks/0.json` and `tasks/1.json`; each carries the untouched round-1 text and an appended `## revision_2`. Both revision-2 comparisons are PASS.
- Coverage and scope: GT `charter_scope` task 0 = {catch_up, relief, add_on, added_invoice}; task 1 = {reinstatement_payment, reinstated}. The scopes are disjoint and cover all six extended policies and six task tools; the uuid8s are independent.
- Problem trees:
  - Task 0: 3 prerequisite problems, 3 value_input edges, 2 user writes.
  - Task 1: 1 prerequisite problem, 1 value_input edge, 1 user write.
  - The difficulty-wide graph is acyclic.
- Factors:
  - Each computation has 4–6 factors with ≥ 2 parameter and ≥ 1 genuine method.
  - Each task has multi-source and assistance cross-difficulty factors on seeded rows.
  - Every factor moves its scored value against an honest baseline, and every whole-baseline fall-back is definite and differs from gold.
- Policy self-consistency: round-1 F1, F2, F3 and F5 closed; F4 withdrawn; no new RED. Remaining observations: O3–O7 (O7 extended to the new credit selections), latent half-cent rounding divergence, no tie rule for "nearest whole installment".
- Instantiation gates re-run by the auditor on the final form (2026-10-04, after the reveal): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. Traceability is deferred to KB publication.
- Charter and tools hashes are unchanged after the gate run (59042d40… / 5dd8bfb4…).
- **The difficulty passes the source-layer audit in revision 2.**
