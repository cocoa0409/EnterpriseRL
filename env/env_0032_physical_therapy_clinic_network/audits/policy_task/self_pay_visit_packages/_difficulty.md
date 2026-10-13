# Policy-task audit — self_pay_visit_packages / charter-global

## charter_global_frozen

- Freeze time: 2026-10-05T05:22:35Z (written before any task GT was revealed). Auditor: independent policy-task auditor (Claude agent, not the instantiating agent).
- Freeze hashes (sha256, verified against the orchestrator's brief and against the live files):
  - `package.extended.yaml` 3ca77bf32932e405aa13634a94cc36c666cb593a8dd2a53569306f09ce76966d
  - `task_tools.py` a3fe05313a9dfa42eef41b1acf249e1a0998fcc6115a604272eaafc33943294a
- Fields permitted: `blueprint/blueprint.yaml` (difficulty entry), `blueprint/products/{package,series,plan,membership}.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`, the extended charter and tool module above, and the masked views `task{0,1}.visible.json` (frozen_time, user_scenario, initial_state only).
- Fields masked and unread at the time of writing: all of `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure` of both tasks; no prior audit exists.
- Entry conditions (Step 0): gate snapshot supplied in the brief — check_extended EXTENDED OK, check_task_tools TASK TOOL CONTRACT OK, replay_tasks REPLAY OK, check_solvability SOLVABILITY OK, check_compute COMPUTE OK, check_grounding GROUNDING OK, check_cross_fire SCOPE OK; check_traceability deferred (KB not rendered); blueprint gates BLUEPRINT OK, SHARE TOOLS OK, VALID. Masked views supplied with hashes, all four re-verified. Input complete.
- Recomputation aid: the DSL sandbox `build_env`/`eval_compute`/`substitute` of `skills/erl-task-instantiate/scripts/check_compute.py` was imported to evaluate the charter's `compute` on the visible `initial_state` (it reads no task GT); a temporary driver script in this directory was deleted after use.

### policy_conflict_scan

Extended policies (6), each with a distinct `(target_tool, computes)`:

| policy | target_tool | computes | subject overlap |
| --- | --- | --- | --- |
| package_ext_installment_catch_up | draft_package_installment_97c9f1d1 (agent) | amount | package_payment_received, package_visits_credited |
| package_ext_unfreeze_extension | unfreeze_visit_package_d2f7d693 (agent) | expiry_extension_days | package_unfrozen |
| package_ext_renewal_purchase | purchase_visit_package_a542d834 (agent) | purchase_price | package_purchased/activated, payment_received, visits_credited |
| package_ext_household_transfer | transfer_package_visits_0bb17a94 (user) | visits | package_visits_transferred, visits_credited |
| package_ext_reinstatement_charge | reinstate_visit_package_76109996 (agent) | reinstatement_fee | package_reinstated, payment_received, visits_credited |
| package_ext_cancellation_refund | confirm_package_cancellation_a8d08ce2 (user) | refund_amount | package_cancelled, visits_refunded |

- Overlapping subjects (`package_payment_received`, `package_visits_credited`) are shared by four policies but each writes a different `payment_kind`/`credit_kind` (installment on an existing package; installment 1 of a new package; reinstatement_fee/reinstatement; transfer_in) — no two policies write the same row kind for the same holding, so no overlap on action parameters or terminal states.
- Shared-state interaction found: the catch-up's medical-hold allowance reads `status == frozen`, and the unfreeze's paid-up limitation reads the installment count. The two writes therefore change each other's values (catch-up first: 664.48 / +66 days on task 0's world; unfreeze first: 709.48 / +10 days). The order is pinned by the declared edge unfreeze <- catch-up ("is fixed only after ..."), so this is not a two-order ambiguity; recorded here because any task carrying both writes depends on that one sentence.
- Time anchors: catch-up (due dates from opened_date), unfreeze (freeze_start_date -> NOW), renewal (exhaustion closed_date -> NOW; membership opened_date; plan discharge_date), reinstatement (expiry_date -> NOW), cancellation (opened_date vs plan opened_date). No two policies anchor the same quantity differently.
- Cross-category read boundaries: series (series_events counts, appointment_series status/pause/visits_per_week/booked), plan (status, opened_date, diagnosis_code, discharge fields), membership (status, opened_date, tier percentage). All reads are of the customer's own holdings; membership is not a difficulty of this scenario (difficulties claim plan, series, package, payplan, wc), so `cross_difficulty: null` on membership-reading factors is honest.
- Scope of the M=2 tasks, as derived blind from the trees (charter_scope itself masked): task 0 = {household_transfer (root), unfreeze_extension, renewal_purchase, installment_catch_up}; task 1 = {cancellation_refund (root), reinstatement_charge}. Pairwise disjoint and jointly cover all six extended policies.

### rule_compute_equivalence

Swept every `compute` binding against its `compute_basis` quotation and back against the `rule`; the quotations are all verbatim substrings of their policy's `rule`. Tiers named in every `factors[].ladder` are sentences of the rule and branches of the `decides` binding. Divergences found (none realised in either task world — see findings O-1..O-3):

- package_ext_reinstatement_charge, coverage credit. Rule: "coverage_credit_ended where it is discharged or closed". Compute: `plan_dx_discharged: "CFIELD('plan', 'opened_date', status='discharged', diagnosis_code=F('diagnosis_code'))"` — a plan in `closed` status is never read, so it gets 0 in compute and 7.50 by the rule.
- package_ext_unfreeze_extension, freeze-day count tier 1. Rule: "Where the appointment series the package funds was paused on or before the freeze start date ...". Compute: `series_pause_start: "CFIELD('series', 'pause_start_date', package_id=HID, status='paused')"` — requires the series to be paused now; a series paused on/before the freeze start and since resumed satisfies the rule but not the compute.
- package_ext_renewal_purchase, continuation discount. Rule: "the patient's Insured Plan of Care for the same diagnosis code as the package" (the package being bought). Compute compares `prior_plan_dx == F('diagnosis_code')`, i.e. the diagnosis of the previous (exhausted) package the compute is anchored on. Identical whenever the renewal is for the same diagnosis.
- Everything else is equivalent: windows (half of renewal_window_days, continuation_window_days, transfer_in_recent_days, reeval days), rounding (card allowance rounded on its own, one-step rounding of the remainder; reinstatement and refund rounded once at the end; purchase price RND after cap), floors (MX(0, ...) on all four that state "never below"), caps (MN(standing_days, cap_days); MN(total_discount, cap_pct); MN(price_part, cap_value)), and the ordering sentences of unfreeze, reinstatement and cancellation.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (table above). Each tool's docstring describes exactly its own write; none names another tool, a sequence position, or an ordering word (the only hit, "can be used again at once" in the unfreeze docstring, means "immediately"). No tool adds confirmation, review or wait.
- Tool bodies (`task_tools.py`) perform no status, eligibility, prerequisite or amount check — every function writes unconditionally (`ctx.find` is only used to read the current balance/customer). The tool layer judges no prerequisite.
- uuid8 tails: 97c9f1d1, d2f7d693, a542d834, 0bb17a94, 76109996, a8d08ce2 — no shared prefix, no sequence, no adjacency; consistent with independent generation. Format `<verb>_<object>_<uuid8>` holds for all six.

### prerequisite_graph

- `prerequisite` filled on all six policies: catch-up [], unfreeze [catch-up], renewal [], transfer [unfreeze, renewal, catch-up], reinstatement [], cancellation [reinstatement]. Every `problem` is an extended policy id of this file, none a base policy, none self. The graph is acyclic (transfer -> {unfreeze, renewal, catch-up}; unfreeze -> catch-up; cancellation -> reinstatement).
- Every `policy_source` is a verbatim sentence of the blocked policy's own `rule` (checked by substring). All five edges declare `form: state`, none carries `fallback_reason` — consistent.
- `resolved_by` equals the depended-on policy's `target_tool` on all five edges, and each resolving write genuinely makes `effect` hold (draft adds the installment payment+credit; unfreeze sets active/freeze_reason none; purchase creates an active paid package; reinstate adds the reinstatement credit and sets active).
- `kind`/`gate`: value_input gates `standing_days` (unfreeze), `balance` (transfer), `cap_value` (cancellation) are real compute bindings. The two transfer state_gates name `visit_packages.status`; the unfreeze edge maps to the base eligibility `transfer_from_active`; the renewal edge (recipient's package) maps to no declared eligibility entry, only to the base sentence "they are credited to an active package the recipient holds" (observation O-6).
- No authoring-viewpoint phrasing ("in this task", "at the opening", "current world") in any prerequisite field.

### prerequisite_sentences

Four-point test on each edge:

1. unfreeze <- catch-up: "The expiry extension on unfreezing is fixed only after the package's history carries an installment payment for every installment whose due date has passed;" — connective "only after"; waited-on state is record-visible (installment payments in the package history), names no tool/id; strength matches `condition`. Resolving write: the only write of this difficulty that adds a `package_payment_received` of kind installment to an existing package is the catch-up draft (purchase writes one only on a new package; reinstatement writes kind reinstatement_fee). Single reading. The same rule continues "while one does not, the freeze days are limited to the days from the freeze start date to the due date of the first unpaid installment" — this supplies a value for the unresolved state (O-4); the "only after" connective still decides the order.
2. transfer <- unfreeze: "Visits are not transferred until the giving package's freeze is lifted and it stands in active status." — "not ... until"; state (freeze lifted, active status). For a frozen giving package only the unfreeze write produces it. Single reading.
3. transfer <- renewal: "Visits are not transferred until the recipient holds an active package of their own, bought and paid for." — "not ... until"; state. Writes that can leave a recipient holding an active package: purchase, and — charter-wide — reinstatement of a recipient's expired package (or unfreezing a recipient's frozen one). "bought and paid for" leans to purchase but does not exclude a reinstated package (O-5). Single reading in task 0's world (see task 0 file).
4. transfer <- catch-up: "Before the transferable balance is worked out, every installment of the giving package whose due date has passed must stand paid in the package's history." — "Before"; state. Single resolving write (as in 1).
5. cancellation <- reinstatement: "No refund is worked out until the package stands active again with the visits removed at its expiry credited back." — "until"; state (active again + expiry visits credited back). Only the reinstatement write credits back expired visits. Single reading.

- No rule carries a second wording, tool name or other problem id about any of these dependencies; no depended-on rule restates the blocked sentence (catch-up, unfreeze, renewal and reinstatement rules are silent about transfer/cancellation).
- Undeclared cross-problem orders: none found in the extended rules. Base rules: package_evt_refunds "the request is registered first and the package is cancelled once the patient confirms" is intra-write (one user tool registers and cancels); package_expiry_and_reinstatement "needs the reinstatement_fee paid first" is overwritten and also intra-write. No task tree rests on a base ordering sentence.

### override_declarations

Sentence by sentence against each `base_policy_refs` entry (findings only; consequences in the task files):

- catch-up vs package_evt_payments_and_crediting: payment methods — followed; "split into installment_count equal installments (the last absorbing any cent of rounding)" — overwritten (declared); due-date schedule — followed (purchase date + interval per installment paid); visits per installment — followed; card-on-file drafting — not contradicted (no scored quantity); late installment stops crediting — followed; "Payments never exceed the purchase price plus any reinstatement fee" — followed (a reduced installment only lowers the total). Base formula `installment_amount: round(purchase_price / installment_count, 2)` is the quantity the declared overwrite replaces. No undeclared override.
- unfreeze vs package_freeze_rules: two clauses overwritten (declared): "A freeze lasts at most freeze_max_days calendar days;" and the expiry move-out clause. "A frozen package not unfrozen within freeze_max_days whose original expiry date has passed expires" — inherited, not contradicted. No undeclared override.
- renewal vs package_renewal_pricing: three clauses overwritten (renewal discount, member discount, "The two never stack ..."). **Not declared: "The purchase price is the list price of the new tier less one discount."** The extended rule stacks up to three discounts ("the renewal, member and continuation discounts are added together"; "it is added to the higher of the renewal and member discounts") — a quantity the base sentence fixes at one discount. Undeclared override -> finding F-1. "The price is rounded to the cent" and the base formula shape — followed. vs package_purchase_eligibility: Medicare/in-network/guardian/GFE/surgery-window/activation — inherited; "expiry date is the activation date plus validity_days" equals the extended "purchase date plus validity_days" because the sale activates the package. vs package_agg_multi_holding and package_evt_payments_and_crediting — followed.
- transfer vs package_evt_transfers: "All remaining visits move together;" overwritten (declared). Active-only, transfer_allowed, relationship, transfer_min_visits, transfers_per_package, "The transfer is the holder's own decision" — inherited. "... and keep the giving package's expiry date" — inherited but not representable through the tool (no scored quantity; O-7).
- reinstatement vs package_expiry_and_reinstatement: "Reinstatement needs the reinstatement_fee paid first;" overwritten (declared, replaced by the reinstatement charge). Expiry, window (inclusive, day zero = expiry date), restoration of expired visits, new expiry = reinstatement date + extension, window-0 tiers, at most once — inherited and followed.
- cancellation vs package_evt_refunds: the prorated-refund clause overwritten (declared). Patient confirmation — followed (user tool). Full-refund window — inherited. "where it is false nothing is refunded after the full-refund window" — inherited. "Reinstatement fees are never refunded" — followed ("reinstatement-fee payments are never part of it"). Refund timing/method — not a scored quantity of this tool.

### factor_ladders

| policy | factor | label | honest? | tiers | multi-source tier | cross_difficulty |
| --- | --- | --- | --- | --- | --- | --- |
| catch-up | medical_hold_allowance | method | yes (per-week time amount vs percent of share vs none) | 3 | yes (status+freeze reason+due date vs freeze start) | — |
| catch-up | card_history_allowance | parameter | yes | 3 | no | — |
| catch-up | clinic_disruption_credit | parameter | yes | 3 | no | series |
| catch-up | insured_transition_credit | parameter | yes | 3 | yes (plan status+opened vs package freeze start) | plan |
| unfreeze | freeze_day_count | method | yes (end anchor/inclusivity change) | 3 | yes (series pause + package history) | series |
| unfreeze | freeze_cap | parameter | yes | 3 | yes (freeze reason + plan) | plan |
| unfreeze | rebooking_allowance | parameter | yes | 3 | no | series |
| unfreeze | closure_credit | parameter | yes | 3 | no | series |
| unfreeze | noshow_deduction | parameter | yes | 3 | no | series |
| renewal | renewal_discount | parameter | yes | 3 | yes (days since exhaustion + forfeits) | — |
| renewal | member_tenure | parameter | yes | 3 | no | — (membership) |
| renewal | continuation_discount | parameter | yes | 3 | yes (dx + reason + discharge date) | plan |
| renewal | discount_combination | method | yes (sum vs max+cont vs max) | 3 | yes | — |
| renewal | discount_cap | parameter | yes | 3 | yes (attended count + tier size) | — |
| transfer | booked_appointment_keepback | method | **no** — see F-2 | 3 | no | series |
| transfer | return_assessment_keepback | parameter | yes | 3 | yes (series status + last visit) | — |
| transfer | received_transfer_keepback | parameter | yes | 3 | yes (credit + date) | — |
| transfer | noshow_reserve | parameter | yes | 3 | yes (no-show count + series status) | series |
| reinstatement | lapse_scaling | parameter | yes | 3 | no | — |
| reinstatement | member_reduction | parameter | yes | 3 | no | — (membership) |
| reinstatement | restoration_charge | method | yes (per-visit vs flat vs none) | 3 | no | — |
| reinstatement | clinic_disruption_credit | parameter | yes | 3 | no | series |
| reinstatement | coverage_credit | parameter | yes | 3 | yes (dx + opened date in span + status) | plan |
| reinstatement | use_adjustment | parameter | yes | 3 | no | — |
| cancellation | used_visit_value | method | yes (valuation basis) | 3 | yes (plan dx/opened/status vs purchase date) | plan |
| cancellation | admin_fee_waiver | parameter | yes | 3 | no | series |
| cancellation | forfeit_charge | method | **no** — see F-3 | 3 | yes | — |
| cancellation | unused_visit_cap | parameter | yes | 3 | no | — |
| cancellation | installment_service_fee | parameter | yes | 3 | no | — |
| cancellation | reinstated_handling_charge | parameter | yes | 3 | yes (reinstatement + last use) | — |

- Counts per policy (declared / surviving the label test): catch-up 4 (3 param, 1 method) / same; unfreeze 5 (4, 1) / same; renewal 5 (4, 1) / same; **transfer 4 (3, 1) / 4 (4 param, 0 method)**; reinstatement 6 (5, 1) / same; cancellation 6 (4, 2) / 6 (5 param, 1 method). All within 4-6; every ladder 3 tiers, pairwise disjoint as stated; `decides` is an input, never `result`; binding sets disjoint within each policy.
- Every ladder is stated in full in the rule (each tier's condition and value/method) and implemented in compute; every fall-through equals the policy's baseline (baseline.rule sentences are all in the rule; `baseline` bindings encode exactly that default).
- Tier distinctness is variant-dependent in two ladders (O-8): freeze_cap — bereavement_cap_days 30 equals the fall-through freeze_max_days 30 on Recovery 6 and Core 8; used_visit_value — tier 1 (package rate) equals the fall-through on the Post-Surgical 18 tier, whose refund_used_visit_valuation is package_rate. Neither variant occurs in this difficulty's task worlds.
- Realism: every condition is a fact a cash-pay PT clinic plausibly weighs for that quantity (freeze reason, insurance status/timing, clinic-caused cancellations, no-shows, standing schedule, tenure, lapse length, visits restored, utilisation), none restates the policy's own scope, and every fall-through is the standard published treatment (full scheduled share, plain day count with freeze_max_days, single higher discount, everything moves, flat reinstatement fee, standard prorated refund). No unreal tier demonstrated.

### findings

- **F-1 SOURCE-POLICY RED (undeclared override) — bears on task 0.** Symptom: the base sentence "The purchase price is the list price of the new tier less one discount." (blueprint/products/package.yaml, package_renewal_pricing.rule, verbatim in the extended file's base section) remains in force, while package_ext_renewal_purchase.rule states "Where a continuation discount applies and the purchase is a prompt renewal, the renewal, member and continuation discounts are added together; where a continuation discount applies otherwise, it is added to the higher of the renewal and member discounts." Root cause: `overwrite` of package_ext_renewal_purchase names three base clauses but not this one; the extended rule's "reduced once by the total discount percentage" redefines "one discount" without declaring it. Affected: package.extended.yaml package_ext_renewal_purchase `overwrite` / `rule`; the purchase_price and discount_percent arguments of purchase_visit_package_a542d834. Demonstration: tasks/0 file, section policy_self_consistency.
- **F-2 SOURCE-FACTOR RED (mislabelled effect; computation left without a method factor) — bears on task 0.** package_ext_household_transfer factor `booked_appointment_keepback` is labelled `method`, but its three tiers ("keep back every appointment still booked on it" / "keep back half ..., rounded up" / "keep back nothing") are one formula with a substituted share: booked_kept = ceil(series_booked x s), s in {1, 1/2, 0} reproduces every tier exactly (ceil(b x 1) = b, ceil(b x 0) = 0). It is a parameter. With it relabelled, the transfer computation carries 4 parameter and 0 method factors, below the floor of 1 `method` per computation. Affected: package.extended.yaml package_ext_household_transfer.factors[0].
- **F-3 SOURCE-FACTOR RED (mislabelled effect) — bears on task 1.** package_ext_cancellation_refund factor `forfeit_charge` is labelled `method`, but its tiers ("every forfeited visit ... at the used-visit value" / "at half the used-visit value" / "nothing") are forfeit_charge = all_forfeits x used_rate x s, s in {1, 1/2, 0} — one formula with a substituted multiplier. The computation still keeps one honest `method` factor (used_visit_value), so the count floor holds; the defect is the label itself. Affected: package_ext_cancellation_refund.factors[2].
- O-1 (observation, charter-global, no task world realises it): reinstatement coverage credit rule "discharged or closed" vs compute reading `status='discharged'` only. A closed same-diagnosis plan opened in the validity span would give 7.50 by rule and 0.00 by compute.
- O-2 (observation): unfreeze tier-1 compute requires the series to be paused now; the rule says "was paused on or before the freeze start date".
- O-3 (observation): renewal continuation compute keys on the previous package's diagnosis; the rule on the new package's.
- O-4 (observation): unfreeze rule supplies the value for the unresolved prerequisite state ("while one does not, the freeze days are limited to ..."), which a reader could take as a permitted alternative; the preceding "is fixed only after" decides the order.
- O-5 (observation): transfer <- renewal state sentence ("an active package of their own, bought and paid for") is also brought about charter-wide by reinstating (or unfreezing) a recipient's own package; resolves uniquely only where no such package is eligible.
- O-6 (observation): the transfer <- renewal `state_gate` points at `visit_packages.status` of the recipient's package, for which the base declares no eligibility entry (only the rule sentence "credited to an active package the recipient holds").
- O-7 (observation): base package_evt_transfers "keep the giving package's expiry date" is not representable by transfer_package_visits_0bb17a94 (no per-visit expiry); no scored quantity.
- O-8 (observation): variant-dependent tier coincidences in freeze_cap and used_visit_value (see factor_ladders).

## closing_checklist

Written after both reveals (2026-10-05T05:24:19Z onward); everything above this heading was frozen before any reveal (sha256 2e1a302b3a69e8a69f960848545dddade2b70363b014e5435c0f0856f010c91c at 05:24:16Z).

**The difficulty does not close**: not every task passes all four relationships.

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | SOURCE-POLICY RED (F-1) | PASS | SOURCE-FACTOR RED (F-2) | PASS (beyond F-1's second reading) |
| 1 | PASS | PASS | SOURCE-FACTOR RED (F-3) | PASS |

- Audit files `0.md`, `1.md` correspond one-to-one with tasks/0.json and tasks/1.json, with `_difficulty.md` alongside; first revision, nothing to carry.
- Coverage and scope: the six extended policies are covered (task 0: catch-up, unfreeze, renewal, transfer; task 1: reinstatement, cancellation), scopes pairwise disjoint (confirmed against `charter_scope` of both tasks), task tools closed over GT, uuid8s independent.
- Trees: task 0 three prerequisite problems / two value_input edges / owner=user transfer; task 1 one prerequisite / one value_input edge / owner=user cancellation; difficulty-wide graph acyclic, no cross-task references.
- Factors: every factor of every task bears weight against an honest baseline and every all-baseline number is definite and differs from gold (task 0: 752.00, 60, 599.40, 16; task 1: 35.00, 451.00); label defects F-2 (transfer left with 0 method factors) and F-3 remain.
- Gates: not re-run by this audit (the skill has the auditor cite, not run, them); the snapshot in the brief stands for the audited form, which is unchanged (hashes above).

## revision_2

### charter_global_frozen (round 2)

- Freeze time: 2026-10-05T06:24:37Z, before either round-2 task file was revealed. Auditor: same independent auditor as round 1. The round-1 text above is left untouched.
- Inputs (sha256, verified against the brief and the live files): package.extended.yaml **41deab5f57af880e1359f7cb0bdae0a5e17ee65c647f3090091221c9f2df37f0** (changed from 3ca77bf3...); task_tools.py a3fe05313a9dfa42eef41b1acf249e1a0998fcc6115a604272eaafc33943294a (unchanged); task0/1.visible.json unchanged (b65560fc..., c7736470...).
- Masked until all round-2 derivations are frozen: everything in tasks/0.json (77f9138a...) and tasks/1.json (b64d9e6a...) beyond frozen_time, user_scenario and initial_state. Round-2 brief carries no scored value. No contamination.
- Re-derivation basis: the charter changed, so every charter-global section is re-derived. The tool module is unchanged, so the uuid8 and docstring checks of §action_binding_and_uuids carry forward by reference to hash a3fe0531...; the `(target_tool, computes)` uniqueness was re-checked on the new charter (unchanged pairs).
- Charter diff vs round 1 (mechanical `diff`): (a) unfreeze param bereavement_cap_days 30 -> 21; (b) unfreeze `series_pause_start` drops `status='paused'`; (c) renewal `overwrite` gains the clause "The purchase price is the list price of the new tier less one discount." replaced by "The purchase price is the list price reduced once by the total discount percentage and rounded to the cent."; (d) renewal continuation sentence now reads "for the diagnosis code of the exhausted package, the condition the new package continues" (rule and two compute_basis entries); (e) transfer booked keep-back rewritten — paused series now keeps back "one week of its standing schedule ..., as many visits as the series' standing visits per week" (new binding `series_weekly`), ladder texts rewritten, label still `method`; (f) reinstatement `plan_dx_discharged` now also reads `status='closed'`; (g) cancellation forfeit charge split into `forfeit_share` (1 / 0.5 / 0) and `forfeit_charge = all_forfeits * used_rate * forfeit_share`, factor relabelled `parameter` deciding `forfeit_share`. Nothing else changed; base section still textually identical to blueprint/products/package.yaml.

### policy_conflict_scan (round 2)

Re-run on the new charter: same six policies, same distinct `(target_tool, computes)` pairs, same row kinds per write, same time anchors and cross-category reads (series, plan, membership). The catch-up/unfreeze shared-state interaction and its pinning by "is fixed only after" are unchanged. Scopes still derive as task 0 = {catch-up, unfreeze, renewal, transfer}, task 1 = {reinstatement, cancellation}. No new conflict.

### rule_compute_equivalence (round 2)

Mechanical sweep (all `compute_basis` quotations, every `policy_source`, every `replaced_by` and every `baseline.rule` sentence found verbatim in the policy's rule; every `superseded_clause` found verbatim in its base rule; every factor binding present in compute) — no failures. Manual sweep of the changed bindings:
- O-1 closed: reinstatement rule "coverage_credit_ended where it is discharged or closed" now matches compute (`status='discharged'` or `status='closed'`).
- O-2 closed: unfreeze rule "was paused on or before the freeze start date" now matches compute reading `pause_start_date` regardless of current status; series_resumed clears only pause_reason (blueprint/products/series.yaml line 237-244), so a resumed series keeps its pause_start_date and is read as the rule says.
- O-3 closed: renewal rule now keys the continuation discount on "the diagnosis code of the exhausted package", which is what `prior_plan_dx == F('diagnosis_code')` reads on the anchored exhausted package. (The ladder's `when` texts still say "the same diagnosis code" — a paraphrase of the rule, not a second tier; observation R2-O-1.)
- Transfer: rule "every appointment still booked on it is kept back; where that series is paused, ... one week of its standing schedule is kept back instead, as many visits as the series' standing visits per week; where there is no such open series, none are kept back" == compute `series_booked if active/booked else (series_weekly if paused else 0)`.
- Cancellation: `forfeit_share` + `forfeit_charge` reproduce the rule sentence exactly (no-show -> full, all late -> half, none -> nothing).

### prerequisite_graph / prerequisite_sentences (round 2)

Unchanged: all five edges, their sentences, forms, conditions, kinds, gates and resolvers are byte-identical to round 1 and the graph stays acyclic; the round-1 conclusions above stand. No changed rule introduces an ordering connective or another problem's write. O-4, O-5, O-6 remain as observations (kept by the reworker with reasons; no consequence in either world).

### override_declarations (round 2)

- **F-1 closed.** package_ext_renewal_purchase `overwrite` now names "The purchase price is the list price of the new tier less one discount." (verbatim in base package_renewal_pricing, line 472) and replaces it with a sentence that is verbatim in the extended rule. All four sentences of package_renewal_pricing that touch the scored price are now either declared or followed ("The price is rounded to the cent." — followed). Merged semantics: one reduction by a total percentage that the extended rule defines; the base "one discount" reading no longer stands in the published charter.
- Other policies: no change to their overwrites or to the base sentences they touch; round-1 conclusions stand (transfer's changed keep-back text concerns only an extended-added quantity, not a base sentence). O-7 stays an observation.

### factor_ladders (round 2)

- **F-2 closed.** booked_appointment_keepback tiers now select different quantities by different measurements: active/booked series -> the count of appointments still booked (`booked_visits_remaining`); paused series -> the series' standing weekly rate (`visits_per_week`), the bookings being treated as suspended; otherwise none. No single formula with a substituted number reproduces the three tiers (tier 1 and tier 2 read different fields), so the `method` label is honest. Transfer: 4 factors, 3 parameter / 1 method, meeting the floor. Realism: holding back one week of a paused standing schedule for its resumption is a treatment a clinic plausibly applies.
- **F-3 closed.** forfeit_charge is now a `parameter` deciding `forfeit_share` (1 / 0.5 / 0) — the honest label. Cancellation: 6 factors, 5 parameter / 1 method (used_visit_value).
- O-8 (freeze_cap) closed: bereavement_cap_days 21 differs from every freeze-allowed tier's freeze_max_days (30, 30, 45, 60, 60), so no two freeze_cap tiers coincide on any variant. O-8 (used_visit_value on the Post-Surgical 18 tier) kept by the reworker; remains an observation (no task world on that tier).
- All other ladders unchanged; counts per policy: catch-up 4 (3/1), unfreeze 5 (4/1), renewal 5 (4/1), transfer 4 (3/1), reinstatement 6 (5/1), cancellation 6 (5/1).

### findings (round 2)

- F-1, F-2, F-3: closed (evidence above). Per-task consequences re-checked in each task file's revision_2.
- R2-O-1 (observation, new, no consequence): continuation_discount ladder `when` texts still say "for the same diagnosis code" while the rule now says "for the diagnosis code of the exhausted package, the condition the new package continues".
- R2-O-2 (observation, new): the transfer rewrite changes task 0's scored transfer count (round-1 derivation 9, round-2 rule 8 — see 0.md revision_2); on task 0's world the active/booked tier and the paused tier of booked_appointment_keepback give the same number (2 booked = 2 per week), so the score does not separate those two tiers there; the factor still bears weight against its baseline.
- No new RED in the charter-global scan.

### closing_checklist (round 2)

Written after the round-2 reveals (2026-10-05T06:25:11Z); everything in revision_2 above this heading was frozen before them.

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS (F-1 closed) | PASS | PASS (F-2 closed) | PASS (transfer visits 8) |
| 1 | PASS | PASS | PASS (F-3 closed) | PASS |

- Audit files 0.md / 1.md correspond one-to-one with the tasks; round-1 text preserved, round 2 appended under `## revision_2` in each file.
- Coverage: all six extended policies covered; scopes disjoint (charter_scope of both tasks confirmed); task tools closed over GT; uuid8s independent (module unchanged).
- Trees: task 0 — 3 prerequisite problems, 2 value_input edges, owner=user transfer; task 1 — 1 prerequisite, 1 value_input edge, owner=user cancellation; difficulty graph acyclic.
- Factors: every computation 4-6 factors with >= 2 parameter and 1 honest method; each task has multi-source and cross-difficulty (series, plan) factors; every factor bears weight against an honest baseline; all-baseline numbers definite and different from gold (task 0: 752.00, 60, 599.40, 16; task 1: 35.00, 451.00).
- Regressions: none — every round-1 figure not targeted by a fix is unchanged; the only moved value (task 0 transfer 9 -> 8) follows from the F-2 rule change and matches GT.
- Remaining observations (no consequence): O-4, O-5, O-6, O-7, O-8 (used_visit_value on the Post-Surgical 18 tier), household ZIP evidence, R2-O-1 (continuation ladder wording), R2-O-2 (tier coincidence on task 0's world).
- Gates: the orchestrator's post-rework snapshot (EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; traceability deferred to post-render) covers the audited hashes; not re-run by this auditor.

**The difficulty passes the source-layer audit in round 2.**

## revision_3

### charter_global_frozen (round 3)

- Freeze time: 2026-10-05T06:58:08Z, before the round-3 task files (tasks/0.json fcabdc7f..., tasks/1.json 10a26221...) were opened. Same independent auditor; rounds 1-2 left untouched.
- Inputs (sha256, verified on the views and the live files): package.extended.yaml 41deab5f57af880e1359f7cb0bdae0a5e17ee65c647f3090091221c9f2df37f0 (**unchanged** from round 2); task_tools.py **864c582b035ae2997471410550c29ae510ba99ae70647a8dce72678e2824a213** (changed from a3fe0531...); task0/1.visible.json b65560fc... / c7736470... (byte-identical to the round-2 views, `cmp`).
- Re-derivation basis: the charter hash is unchanged, so §revision_2 policy_conflict_scan, rule_compute_equivalence, prerequisite_graph, prerequisite_sentences, override_declarations and factor_ladders carry forward by reference (grounds: package.extended.yaml 41deab5f... in both rounds). The tool module changed, so §action_binding_and_uuids and the tools-judge-no-prerequisite check are re-derived below.

### action_binding_and_uuids (round 3)

- Diff r2 -> r3 (mechanical `diff`): exactly two hunks, both in the module body — (1) `from datetime import date, timedelta` removed; (2) in `unfreeze_visit_package_d2f7d693` the line `new = (date.fromisoformat(old) + timedelta(days=int(expiry_extension_days))).isoformat()` replaced by integer proleptic-Gregorian day-number arithmetic (days-from-civil, add the extension, civil-from-days, format `YYYY-MM-DD`). No signature, owner, `rw`, docstring, uuid8 suffix, other tool body, row field or receipt key changed. The only remaining import is `from erlbench import ToolContext, tool`; no clock is read (the `old` fallback `ctx.now()[:10]` is the unchanged runtime clock of the environment, as before).
- Equivalence of the replaced arithmetic, tested by executing the new block against the removed `date + timedelta` expression: every date 1990-01-01..2110-12-31 x every extension 0..400 days — 17,721,794 cases, 0 mismatches; every 7th date of the same span x extensions -400..-1 — 2,525,600 cases, 0 mismatches; edge dates 0001-01-01, 1600-02-29, 2000-02-29, 2100-02-28, 9998-12-31 x {0, 1, 59, 365, 366, 1461} — 0 mismatches. The policy-reachable domain (an ISO expiry date on file, extension = MX(0, capped freeze days + re-booking + closure - no-show) <= 101 days on any tier) lies inside the exhaustively tested range. Only unreachable inputs differ in failure mode (a malformed date string, or a year beyond 9999, raised under the old code).
- `(target_tool, computes)` pairs, owners and uuid8s (97c9f1d1, d2f7d693, a542d834, 0bb17a94, 76109996, a8d08ce2) unchanged; docstrings unchanged, so the no-sequence/no-tool-name conclusion of round 1 stands. Every tool body still writes unconditionally — no prerequisite, status or amount check was introduced.
- Conclusion: every tool writes the same values as in round 2 for every input the policies can reach; no new defect in the contract, docstrings or suffixes.

### closing_checklist (round 3)

Written after the round-3 reveal (2026-10-05T06:58:18Z).

| task | policy self-consistency | problem tree | factors bear weight | unique solution |
| --- | --- | --- | --- | --- |
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |

- Tool module 864c582b...: only the datetime import and the unfreeze date arithmetic changed; the new arithmetic equals the old on 20.2M tested cases covering the whole policy-reachable domain; contracts, owners, docstrings and uuid8s unchanged; no tool judges a prerequisite.
- Task files: frozen_time / user_scenario / initial_state identical to the views; every scored argument, computation figure, closure edge and scope identical to round 2; db_closure equals initial_state in both tasks.
- Charter (41deab5f...) unchanged, so all round-2 charter-global conclusions and observations carry forward.
- Gates: the orchestrator's post-fix snapshot (EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; validator no longer reports the forbidden import) covers the audited hashes; not re-run by this auditor.

**The difficulty still passes the source-layer audit in round 3.**
