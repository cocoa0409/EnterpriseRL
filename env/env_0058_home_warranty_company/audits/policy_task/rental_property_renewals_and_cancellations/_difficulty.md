# Policy-task audit — rental_property_renewals_and_cancellations / charter-global

## charter_global_frozen

- Frozen: written 2026-10-12 between 13:42:07 UTC (`date` before first write) and the GT reveal at 13:45:37 UTC; the freeze minute first typed here (13:45) was an estimate and is corrected in place, with no content change. Auditor: independent erl-task-policy-audit agent (did not author the artifacts).
- `tasks/rental_property_renewals_and_cancellations/landlord.extended.yaml` sha256 `888b481198d1c35b3e9b30270f8cc5c90503c7e474ad1a968f976442b6f9bcd0`
- `tasks/rental_property_renewals_and_cancellations/task_tools.py` sha256 `f0327668d3df3ad7c766d9e5032ab1931ae9fc5b211564bd4d6ebe3b71005913`
- Masked views: `0.view.json` sha256 `77d55051…bdc7c8`, `1.view.json` sha256 `8b04b44a…b9f7` (both re-hashed on entry; match the brief).
- Read: blueprint (`blueprint.yaml`, `db_schema.json`, `share_tools.py`, `products/landlord.yaml`; `products/{homeplan,lineplan,addon}.yaml` only for the cross-category prices/rider rule), the extended charter, the tool module, the two masked views, and the DSL interpreter `skills/erl-task-instantiate/scripts/check_compute.py` (for the semantics of `within_months`, `MONTHS`, `LATEST`, `CFIELD`, `XCOUNT`).
- Masked/unread: every task JSON field other than `frozen_time`, `user_scenario`, `initial_state`; `worklog.md`; any other scenario; sibling difficulties.
- Entry conditions (Step 0): gate snapshot supplied (EXTENDED / TASK TOOL CONTRACT / REPLAY --check / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; TRACEABILITY NOT OK only on pre-docs `tool_name` unlock; validate_scenario only "required document not found"). Masked views and hashes supplied. Entry conditions met.
- Base section: `diff <(sed -n 1,1536p landlord.extended.yaml) blueprint/products/landlord.yaml` differs only by a trailing blank line — base copy is verbatim.

### policy_conflict_scan

Eight extended policies, each with one `(target_tool, computes)`:

| id | target_tool (owner) | computes | prerequisite edges (kind) |
|---|---|---|---|
| landlord_ext_late_renewal_premium | record_late_renewal_5b858282 (agent) | renewal_premium | ← upgrade_catchup (value_input) |
| landlord_ext_upgrade_catchup_charge | bill_upgrade_catchup_f812c6ed (agent) | catchup_amount | — |
| landlord_ext_returned_payment_fee | bill_returned_payment_fee_d229d74e (agent) | fee_amount | ← late_renewal (state_gate) |
| landlord_ext_plus_upgrade_charge | accept_plus_upgrade_7955ec7e (user) | upgrade_charge | ← late_renewal (value_input), ← upgrade_catchup (value_input), ← returned_payment_fee (state_gate) |
| landlord_ext_rerating_correction_credit | post_rerating_correction_12887c54 (agent) | correction_amount | — |
| landlord_ext_notice_period_installment | bill_period_installment_43ec6687 (agent) | installment_amount | ← rerating (value_input) |
| landlord_ext_upgrade_difference_charge | bill_upgrade_difference_aa78d3be (agent) | difference_amount | ← notice_period_installment (value_input) |
| landlord_ext_sale_cancellation_credit | confirm_sale_cancellation_d8f9046f (user) | cancellation_credit | ← notice_period_installment (value_input), ← upgrade_difference (state_gate) |

- Overlapping subjects: `landlord_premium_charge` is a subject of five policies (catch-up, returned fee, installment, upgrade difference, Plus upgrade). Their triggers are disjoint by scope sentence: an unbilled past upgrade (catch-up), a returned payment without fee, an unbilled due installment of a monthly contract, a monthly contract upgraded part-way through a period, and a new move to a Plus tier on an annual contract.
- Scope overlap catch-up vs upgrade difference (observation O-1): both write an `upgrade_proration` charge for an upgrade "never billed". The catch-up scope sentence ("a tier upgrade whose upgrade charge was never billed") is not restricted to annual billing, while the upgrade-difference scope is "a monthly-billed … contract moved to a higher tier part-way through a billing period". On a monthly contract the catch-up method has no input — it needs "the portfolio discount rate recorded on the term's annual premium charge", which a monthly contract does not carry — and its overwrite replaces only the annual-billed base sentence. So a reader can resolve the overlap only through that inapplicability, not through the scope sentence. No second computable answer was found.
- Time anchors: every computation is anchored at its own write ("before the late renewal", "before the catch-up is billed", "before the upgrade", "before the confirmation"). No conflicts.
- Terminal states: late renewal → active, new term; sale confirmation → contract cancelled, request confirmed, credit posted. The base event `landlord_cancellation` also triggers `addon:addon_rider_base_termination` (addon rule: "When the base contract is cancelled … the rider ends the same day with status ended_with_base"). `confirm_sale_cancellation_d8f9046f` does not cascade it, and no tool of this difficulty can (observation O-2; this matters to task 1, whose contract carries an active rider).
- Cross-category reads: lineplan (status, billing_channel, billing entries), homeplan (status, billing_frequency, billing entries), addon (rider on this contract, billing entries). All are declared in `cross_category`, and all are read-only.
- Scope of the M=2 tasks (from the masked worlds, before reveal): task 0's world (annual contract, expired, unbilled May upgrade, returned payment without fee) instantiates {late renewal, catch-up, returned fee, Plus upgrade}. Task 1's world (monthly contract, zero-rate installments, unbilled due installment, mid-period upgrade, sale cancellation pending) instantiates {rerating, installment, upgrade difference, sale cancellation}. The two sets are disjoint and together cover all eight extended policies. They are confirmed against `charter_scope` in each task's comparison.

### rule_compute_equivalence

I swept every binding of all eight `compute` blocks against its `compute_basis` quotation and the `rule`, and every rule sentence back to a binding. Every ladder tier named in `factors[].ladder` is a rule sentence and a branch of its `decides` binding, and vice versa. No tier lives in only one face. No compute basis is invented. Residual gaps, none of which bears on either task's world:

- O-3 `landlord_ext_late_renewal_premium.line_status` uses `CFIELD('lineplan','status')`, which reads the customer's first line plan, while `line_payments_12` uses `XCOUNT`, which counts payments on all of the customer's line plans. The rule says "an active … plan with at least twelve premium payments posted on it". This diverges only for a customer holding two or more line plans; task 0 has one.
- O-4 `landlord_ext_notice_period_installment.rider_payments_12` is `XCOUNT('addon', …)` across all of the customer's riders, while the rule ties the payments to "an active Bridgewell rider … attached to the contract". `after_hours_12` counts every billing row with `fee_type='after_hours_surcharge'` without filtering `event_type`, so a `landlord_service_fee_refund` row would also be counted. `base_monthly_a` reads `P()` of the tier held now, while the rule says "the tier the contract holds on the period start". Task 1 has none of these divergent shapes: one rider, no fee refunds, and the upgrade (2026-08-25) precedes the period start (2026-09-17).
- O-5 `landlord_ext_returned_payment_fee.returned_amount` / `return_date` read the latest `returned_payment` row, while the rule speaks of "the returned payment" the fee names. They diverge only when an older return is the one without a fee. Its `compute_basis.result` quotes the standard-fee sentence although `result = RND(aged_fee, 2)`.
- `landlord_ext_rerating_correction_credit` / `landlord_ext_notice_period_installment` take the term's correct rate as `MAX` over all monthly installments of the contract, not just the current term's. This is what their rules say; the conflict with the base is G2 below.

### action_binding_and_uuids

- Each `(target_tool, computes)` pair is claimed by exactly one policy (table above). Owners: two `user` tools (accept_plus_upgrade, confirm_sale_cancellation) and six `agent` tools.
- uuid8 tails: f812c6ed, 5b858282, d229d74e, 7955ec7e, 12887c54, 43ec6687, aa78d3be, d8f9046f. They are pairwise distinct, share no prefix or sequence, and none is a copied tail. They read as independently generated.
- Docstrings: `grep -n "before\|after\|first"` over `task_tools.py` returns nothing. No docstring names another tool or a position in a sequence.
- No tool body checks a prerequisite: every function does `find` → `create`/`update` with the passed values, and none returns an error or hint for status, balance or missing rows.
- O-6 The `bill_upgrade_catchup_f812c6ed` docstring and body date the charge today (`entry_date=ctx.now()`, `billing_period_start=last_plan_change_date`). The catch-up rule says the charge is "billed … as one upgrade charge dated to the upgrade". Every consumer of that charge (late renewal: "every upgrade charge billed on the contract in those twelve months"; Plus upgrade: "upgrade charges already billed … in the twelve months before the upgrade") gets the same count under either dating on task 0's world (2026-05-12 and 2026-10-14 are both within twelve months of 2026-10-14). No consequence.

### prerequisite_graph

- Every extended policy fills in `prerequisite` (`[]` for catch-up and rerating). Every `problem` is an extended policy id of this file, never the policy itself and never a base policy.
- The graph is acyclic: catch-up → late renewal → returned fee → Plus upgrade; catch-up → Plus; late renewal → Plus; rerating → installment → upgrade difference → sale cancellation; installment → sale cancellation.
- Every `policy_source` is found verbatim in its own policy's `rule` (checked by string match):
  - "The late-renewal premium is fixed only after every tier upgrade made during the expired term carries its upgrade charge on the contract."
  - "A returned-payment fee is not billed until the contract stands in force again, in a status under which premium is billed."
  - "An upgrade charge is worked out only once the contract stands active in a current term whose annual premium is billed on the contract."
  - "An upgrade charge is fixed only after every earlier tier upgrade on the contract carries its own upgrade charge."
  - "No upgrade charge is fixed until every returned payment on the contract carries its returned-payment fee."
  - "The installment for a billing period is fixed only after every earlier installment of the term that was billed at a portfolio discount rate of zero carries its billing correction."
  - "No upgrade difference charge is fixed until the installment for the first billing period at the new tier stands billed on the contract."
  - "A sale cancellation credit is not fixed until the installment for the billing period in which notice was given stands billed on the contract."
  - "The cancellation is confirmed and its credit posted only after every tier upgrade made during the term carries its upgrade charge on the contract."
- All edges are `form: state`, and none carries a `fallback_reason` (correct for state form).
- `resolved_by` equals the depended-on policy's `target_tool` on all nine edges.
- `value_input` gates name real bindings: `expired_term_premium`, `remaining_days`, `upgrade_charges_12u`, `correction_goodwill`, `monthly_difference`, `notice_installment`. `state_gate` gates name real fields: `landlord_contracts.status`, `landlord_billing_entries.charge_type`.
- Conditions neither strengthen nor weaken their sentences.
- O-7 Authoring-viewpoint residue in the `prerequisite` text (the field is not rendered to the solver, so no consequence can be demonstrated; recorded as an observation): Plus edge 2 condition "…including the upgrade recorded in the expired term"; Plus edge 1 and returned-fee edge effects "Once the lapsed contract is renewed…"; sale edge 2 condition "for the mid-period tier upgrade recorded on the last plan change date". These describe one world rather than the general policy.

### prerequisite_sentences

Four-point test on all nine sentences:
1. Each has an ordering connective: "only after", "not … until", "only once", "No … until".
2. Each waits on a record-visible state in table words: "carries its upgrade charge on the contract", "stands in force again, in a status under which premium is billed", "stands active in a current term whose annual premium is billed", "carries its returned-payment fee", "carries its billing correction", "stands billed on the contract".
3. None names a tool, policy id, snake_case token or row id.
4. Each matches its `condition`, and closed sets are named by kind ("every tier upgrade", "every returned payment", "every earlier installment … billed at … zero").

No rule restates another problem's sentence. No depended-on rule restates the sentence that waits on it. No rule carries an undeclared cross-problem order.

Which single write brings each waited-on state about:
- "carries its upgrade charge" on an annual contract → only the catch-up (the upgrade-difference scope is monthly-billed). On a monthly contract upgraded mid-period → the upgrade difference; the catch-up is excluded only because its method cannot be computed there (see O-1).
- "stands in force again / stands active in a current term whose annual premium is billed" → only the late renewal sets `expired → active` and bills an annual premium. No other write of this difficulty or of `share_tools.py` changes a landlord contract's status to active.
- "carries its returned-payment fee" → only the returned-payment fee.
- "carries its billing correction" → only the rerating credit (`credit_reason='billing_correction'`).
- "installment … stands billed" → only `bill_period_installment_43ec6687`.

Each derivation of sentence + records + depended-on rule → resolving action is written out on the task's own world in that task's `problem_chain`.

### override_declarations

Sentence-by-sentence over every `base_policy_refs` entry. Base portfolio sentences:
- S2 = "The number of contracts counted is landlord_msr_portfolio_property_count, a snapshot taken on the first day of the term being priced…"
- S5 = "The rate is fixed for the whole term … and the rate is taken again at each renewal and late renewal."
- S6 = "The rate applies to monthly_installment, annual_premium and upgrade_proration charges and never to returned_payment, returned_payment_fee or transfer_fee charges."

| extended | base sentence | handled | declared? |
|---|---|---|---|
| late renewal | portfolio S5 (rate taken again at late renewal) | carries the recorded rate | yes (overwrite 1) |
| late renewal | pricing annual sentence | PIF ladder, loadings, credits, lapse credit | yes (overwrite 2). Observation O-8: `replaced_by` speaks only of loadings/credits "on top of the standard late-renewal premium", but the PIF ladder alters the standard premium itself. The base sentence is superseded as a whole, so no second answer. |
| late renewal | renewal_terms late-renewal sentences; pricing P1/P5/P8 | followed | n/a |
| catch-up | pricing P8 (billed only while open) | billed on an expired contract | yes |
| catch-up | upgrade_rules annual proration sentence | catch-up method | yes |
| catch-up | portfolio S5/S6 | rate recorded on the term's annual premium; upgrade_proration discounted | followed |
| returned fee | pricing returned-payment sentence | fee ladder | yes |
| returned fee | **portfolio S6** "…never to returned_payment, returned_payment_fee or transfer_fee charges" | the portfolio rate band reduces the fee ("portfolio courtesy") | **no — G1** |
| Plus upgrade | upgrade_rules annual proration sentence | Plus method | yes |
| Plus upgrade | upgrade_rules U1 "…status is waiting_period or active" | prerequisite sentence requires "stands active" | not declared. Narrower than base only for a waiting-period contract; neither world has one. Observation O-9. |
| rerating | cancellation sentences (confirmation, sale window, one-credit) | exempts billing corrections | yes (defensive) |
| rerating, installment | **portfolio S2/S5** (rate = snapshot count on the term's first day, fixed for the term) | "the term's correct portfolio rate … is the highest portfolio discount rate recorded on the contract's monthly installments" (any term) | **no — G2** |
| installment | pricing monthly-installment sentence | late-billed installment method | yes |
| upgrade difference | upgrade_rules monthly sentence | adds the difference charge | yes |
| sale cancellation | cancellation monthly sentence | unused-share credit | yes |
| sale cancellation | cancellation "The cancellation is effective on notice_date and never backdated." | the closing-anchor tier counts unused days "from the day after the closing date", i.e. before the effective date | not declared. The sentence governs the effective date, which the tool keeps at `notice_date`, and the extended sentence governs only the credit's day count, so I read no contradiction on one quantity. Observation O-10. |

### factor_ladders

Counts as declared (P = parameter, M = method, MS = multi-source, X = cross-difficulty):

| policy | factors | P | M | MS | X |
|---|---|---|---|---|---|
| late renewal | returned_history_pif_rate, claims_experience_loading (MS), request_frequency_loading, tenure_credit, line_plan_bundle_credit (MS, X lineplan), lapse_day_credit (M) | 5 | 1 | 2 | 1 |
| catch-up | covered_share_convention (M), billing_delay_concession, coverage_use_loading, homeowner_plan_concession (X homeplan; status and billing_frequency are one record, so not MS), payment_method_concession | 4 | 1 | 0 | 1 |
| returned fee | repeat_return_level, returned_amount_addition, portfolio_courtesy, fee_ageing (M) | 3 | 1 | 0 | 0 |
| Plus upgrade | repeat_change_share (M, MS: billing rows × claim rows), tenant_request_loading, emergency_request_loading, term_timing_adjustment, unpaid_premium_loading | 4 | 1 | 1 | 0 |
| rerating | rerated_count_goodwill, overcharge_interest (M), line_plan_goodwill (X lineplan; one record), portfolio_band_goodwill, overcharge_size_goodwill | 4 | 1 | 0 | 1 |
| installment | correction_goodwill (MS: credit row × payment row), rider_attachment_credit (MS, X addon), tenant_request_share, request_volume_loading, after_hours_surcharge (M) | 4 | 1 | 2 | 1 |
| upgrade difference | difference_day_count (M), difference_delay_concession, emergency_use_loading, upgrade_term_timing, contract_tenure_credit | 4 | 1 | 0 | 0 |
| sale cancellation | closing_anchor_share (M), recent_claim_holdback, homeowner_plan_bonus (MS, X homeplan), remaining_term_bonus, returned_payment_offset, payment_record_bonus | 5 | 1 | 1 | 1 |

Structural checks:
- All ladders have three tiers, are disjoint as stated and are stated in full in the rule.
- Every fall-through equals its factor's `baseline`.
- Every `decides` is an input, never `result`.
- Bindings are disjoint (but see O-11).
- No two tiers of a ladder share a value as written, except where G3/G4 below show that the tiers are one formula.

Findings on structure and realism (each demonstrated on the task it bears on):

- **G3 (SOURCE-FACTOR, mislabelled effect)**: `landlord_ext_late_renewal_premium.lapse_day_credit` is labelled `method`. Its three tiers are "every lapse day is credited", "half of the lapse days, rounded down to a whole day" and "no lapse day is credited". These are one formula, credited = floor(c × lapse_days) with c ∈ {1, ½, 0}, and the premium step "(365 − credited)/365" is the same in every tier. Only a number changes. The late-renewal computation is therefore left with 0 honest `method` factors (requirement ≥1). Bears on task 0.
- **G4 (SOURCE-FACTOR, tiers select the same method)**: `landlord_ext_rerating_correction_credit.overcharge_interest` has the tiers "≥2 months: × 1.01^m", "exactly 1 month: × (1 + 0.01)" and "<1 month: × 1". These are the single formula 1.01^m at m ≥ 2, m = 1 and m = 0 (1.01^1 = 1.01, 1.01^0 = 1). Three tiers state one method. The rerating computation has no `method` factor. Bears on task 1.
- **G5 (SOURCE-FACTOR, ladder with only two live tiers)**: in `landlord_ext_rerating_correction_credit`, two fall-through tiers can never decide a credit the policy can post.
  - portfolio_band_goodwill: its fall-through ("correct rate under 0.05") means correct rate = 0.00 (the charter's only bands are 0, 0.05 and 0.10). Then overcharge = total × 0 = 0 and the credit is 0 whatever the goodwill.
  - overcharge_size_goodwill: its fall-through (< 2.00 per installment) is unreachable because the smallest installment in the charter is 42.99 (Rental Appliance), and 42.99 × 0.05 = 2.15 ≥ 2.00.
  - Within the policy's scope, each ladder has two tiers. Bears on task 1.
- **G6 (SOURCE-FACTOR, unreal ladder — realism)**: the conditions below are ones no US home-warranty or landlord service-contract program weighs for the quantity named. Those programs work as follows:
  - The price of a tier for a term is the published rate.
  - The charter's own base fixes installments for the term ("never changes the installments already set").
  - Claims or usage experience enters only at renewal pricing, which the charter's late-renewal policy does — that part is realistic.
  - A mid-term charge (an installment billed late, the pro-rata difference of an upgrade, a catch-up of an unbilled upgrade, the price of a mid-term upgrade, whose anti-selection the base already handles with `upgrade_waiting_period_days`) is the rate-table figure, prorated.
  - A refund or correction is restitution of premium.

  The unreal ladders:
  - (a) installment.after_hours_surcharge: adds 1.50 per after-hours surcharge (or a flat 2.00) to a premium installment, for surcharges already billed per request as service fees (base: "A routine request for an after-hours visit is also charged tenant_after_hours_surcharge"). This re-bills fee history into premium, which is a double charge. It is also that computation's only `method` factor.
  - (b) installment.tenant_request_share and request_volume_loading: usage loadings on one installment of an in-force term.
  - (c) upgrade_difference.emergency_use_loading: a usage loading on a sub-month pro-rata tier difference.
  - (d) upgrade_catchup.coverage_use_loading: a usage loading on the back-billed price of an upgrade already in force.
  - (e) plus_upgrade.tenant_request_loading and emergency_request_loading: usage loadings on a mid-term upgrade price.
  - (f) plus_upgrade.unpaid_premium_loading: loads the upgrade price by any balance "owed" (`F('premium_balance')`), including charges billed the same day and not yet due. The base charter's treatment of unpaid premium is the grace/suspension/cure procedure, not a surcharge on other transactions.
  - (g) rerating.line_plan_goodwill: inflates restitution of Bridgewell's own overcharge according to how an unrelated utility line plan (any property) is billed (partner utility bill vs other).
  - (h) sale_cancellation.returned_payment_offset: cuts a cancellation refund 5–10 % for returned payments already billed back with their fee, a second penalty for one event.
  - (i) sale_cancellation.remaining_term_bonus: raises the refund by the number of whole term months left after notice. On a monthly contract those months are never billed (base: "billed no further installments"), so no premium is attached to them.

  Surviving honest factors once G3–G6 are struck:
  - rerating: 1 (rerated_count_goodwill); no method.
  - installment: 2 (correction_goodwill, rider_attachment_credit); no method.
  - Plus upgrade: 2 (repeat_change_share M, term_timing_adjustment P); fewer than 4, 1 P.
  - late renewal: 5 P, 0 M.
  - catch-up: 4 (M + 3 P).
  - upgrade difference: 4 (M + 3 P).
  - sale cancellation: 4 (M + 3 P).
  - returned fee: 4, but its portfolio_courtesy rests on G1.
- Realism observations (O-12, not grounds for RED):
  - The card tier (0.01) of payment_method_concession: card payments are not usually discounted.
  - homeowner_plan_concession on a catch-up, and homeowner_plan_bonus / payment_record_bonus on a cancellation refund: retention-style gestures that are unusual but conceivable.
  - The ACH split of the installment's correction_goodwill.
  - rider_attachment_credit applied only to a late-billed installment, where a bundle discount would apply to every installment.
  - The upgrade difference's day-count convention changes with Bridgewell's own billing lag; the "+1 day when billed 15–30 days late" tier works against the customer.
  - The upgrade difference's monthly difference is taken from the late-billed installment including that installment's loadings, credits and the +2.00 after-hours amount.
- O-11 (duplicate evidence): pairs of factors share one condition under two binding names.
  - upgrade difference: `billing_lag_days` and `delay_lag_days` are both `DAYS(last_plan_change_date, NOW)`, and both ladders split at >30 and ≥15.
  - catch-up: `change_age_days` and `posting_delay_days` are the same expression.
  - rerating: `band_rate_seen` = `correct_rate`.

  Bindings are disjoint by name only.

### findings

- **G1 — SOURCE-POLICY RED (undeclared override, anonymous intermediate)**.
  - Symptom: the portfolio discount band reduces a returned-payment fee charge.
  - Root cause: `landlord_ext_returned_payment_fee.overwrite` names only the base pricing sentence on returned payments. It does not name base S6 of `landlord_agg_portfolio_discount` (in `base_policy_refs`): "The rate applies to monthly_installment, annual_premium and upgrade_proration charges and never to returned_payment, returned_payment_fee or transfer_fee charges."
  - Evidence: the extended rule says "The portfolio courtesy is 10.00 when the portfolio discount rate recorded on the contract's most recent annual premium charge is 0.10 or more, 5.00 when it is at least 0.05 but under 0.10…" and "The fee before ageing is the repeat-return fee level plus the returned-amount addition less the portfolio courtesy."
  - Bears on task 0 (consequence demonstrated in `0.md`).
- **G2 — SOURCE-POLICY finding (undeclared redefinition of the term's portfolio rate)**.
  - Base S2/S5: the rate is the band of the snapshot count "on the first day of the term being priced" and "is fixed for the whole term".
  - Rerating rule: "The term's correct portfolio rate for this correction is the highest portfolio discount rate recorded on the contract's monthly installments". The installment rule likewise: "the term's portfolio discount rate, which is the highest rate recorded on the contract's monthly installments". Neither is limited to the current term, and neither is declared.
  - Constructed divergence: a contract whose prior term's installments carry 0.10, whose current-term snapshot gives 0.05, and two current installments billed at 0. The base gives a correct rate of 0.05; the extended rule gives 0.10.
  - Bears on task 1, but on task 1's world both readings give 0.05 (count on 2026-03-17 = 3 open contracts; the highest recorded rate = 0.05). No consequence there, so it is an observation at task level.
- **G3, G4, G5, G6** — SOURCE-FACTOR, as stated under factor_ladders. G3, G6(d) and G6(e)(f) bear on task 0; G4, G5 and G6(a)(b)(c)(g)(h)(i) bear on task 1.
- Observations O-1 … O-12 as stated above. None changes a scored value on either world.

## closing_checklist

Written 2026-10-12 after both reveals; post-reveal content is confined to this section. **The difficulty is not closed.** Not every task passes all four relationships:

| task | policy self-consistency | problem tree | factors | unique solution |
|---|---|---|---|---|
| 0 | SOURCE-POLICY RED (G1) | PASS | SOURCE-FACTOR RED (G3, G6 d/e/f) | not determinate while G1 stands (fee 17.00 vs 20.00); otherwise unique and equal to GT |
| 1 | PASS (G2 no consequence) | PASS | SOURCE-FACTOR RED (G4, G5, G6 a/b/c/g/h/i) | PASS, equal to GT |

Checklist items that do hold:
- Per-task files `0.md` and `1.md` sit alongside this one. This is the first revision.
- `charter_scope` of the two tasks is disjoint and covers all 8 extended policies and all 8 task tools. The uuid8s are independent.
- Each tree has 3 prerequisite problems, 3 value_input edges and a user-owned root, and is acyclic. The difficulty-wide graph is acyclic.
- Every factor on both worlds bears weight against its baseline, and every all-baseline number differs from gold. These match GT's `factor_sensitivity` and `baseline_result` figure for figure.

Items that do not hold: G1 (undeclared override); the factor-structure and realism bounds G3–G6. The instantiation-stage gates were not re-run by this audit; the coordinator's snapshot is cited in `charter_global_frozen`.

## revision_2

### charter_global_frozen (revision_2)

- Re-audit round 2. Written 2026-10-12 after 19:11:30 UTC and before any round-2 task JSON was opened. The round-1 text above is untouched.
- Hashes, re-checked on entry and matching the brief:
  - `landlord.extended.yaml` `3b2b998c03e5129e630a5704d635560cdb2600962702b4f6bb01a0387fa34d8d` — changed, so every charter-global section is re-derived in full below.
  - `task_tools.py` `f0327668…05913` — unchanged, so `#action_binding_and_uuids` is carried forward by reference (same uuid8s; no docstring ordering words; no prerequisite checks in any body).
  - Views: `0.view.json` `787fde36…a536`, `1.view.json` `77c92cd8…4a61`.
- The base copy is still verbatim: diff against `blueprint/products/landlord.yaml` shows only the trailing blank line.
- Entry conditions: the round-2 gate snapshot was supplied (all OK except TRACEABILITY pre-docs unlock misses) and the masked views were rebuilt. Met.

### policy_conflict_scan (revision_2)

- Eight extended policies with the same ids, target tools and `computes` as in round 1. The policy order in the file has changed (catch-up first); the graph has not.
- Catch-up scope is now "a tier upgrade of an annual-billed rental property service contract". The overlap with the monthly-only upgrade difference is gone (O-1 closed).
- Scopes of the two masked worlds are unchanged: task 0 = {catch-up, late renewal, returned fee, Plus}; task 1 = {rerating, installment, difference, sale credit}. Disjoint and complete.
- O-2 closed on task 1's world (no rider seeded). The charter-level cascade gap remains for any world with a rider: `confirm_sale_cancellation_d8f9046f` does not end riders. Observation.

### rule_compute_equivalence (revision_2)

Every `compute_basis` quotation was string-checked against its `rule`: all present. Every `baseline.rule` sentence is in its `rule`. Every binding was swept back to the rule. Round-1 residuals:
- O-3 closed (`CFIELD('lineplan','status', status='active')`; rule now "payments … on the landlord's line plans").
- O-4 closed (rider and after-hours bindings removed; tier read "when the installment is billed", matching `P()` of the current tier — but see N-3).
- O-5 closed (fee rule now "the most recent returned premium payment").

New residuals:
- N-2 (upgrade difference): `days_left` / `period_position_days` read the period start from the latest billed `monthly_installment` row. The rule's quantity, "before the start of the first billing period at the new tier", is a calendar date (periods start on the term-start day of the month). The two agree once that installment is billed, which is the policy's handling time, so the scored value is unaffected. On a world without the row, the compute gives a different number from the rule. This matters for the edge kind (see `#prerequisite_graph`).
- `period_position_days` is the same expression as `days_left` under a second name (O-11 residue, harmless).

### prerequisite_graph (revision_2)

- Same nine edges, same kinds, same resolvers. Acyclic.
- Every `policy_source` is verbatim in its own rule (string-checked). `resolved_by` equals the depended-on `target_tool`. Every `value_input` gate names a real binding (`expired_term_premium`, `remaining_days`, `upgrade_charges_12u`, `correction_goodwill`, `days_left`, `notice_installment`).
- O-7 closed: the conditions and effects are now worded generally ("every tier upgrade the contract records", "Once the contract stands in force again", "every mid-period tier upgrade made during the current term").
- **N-2 — observation (edge kind overstated)**: upgrade_difference ← notice_period_installment is declared `value_input` with gate `days_left`.
  - Under the rule, the days left are counted to "the start of the first billing period at the new tier", a calendar date that does not depend on whether that installment has been billed. Skipping the installment write therefore leaves the rule's difference unchanged; only the compute's row-read changes.
  - The edge is still a genuine state gate: the sentence "No upgrade difference charge is fixed until the installment for the first billing period at the new tier stands billed on the contract" is false at the opening.
  - It is not a RED because task 1's tree keeps 2 genuine `value_input` edges (credit ← installment and installment ← rerating), which equals max(n − 1, 1) = 2.

### prerequisite_sentences (revision_2)

- Four-point test on the nine sentences: passes.
- Plus sentence 1 now reads "…stands in a current term, in its waiting period or active, whose annual premium is billed on the contract", consistent with base U1 (O-9 closed).
- Single resolving write per state-form edge:
  - catch-up for an annual contract (the upgrade difference is monthly-only, and the catch-up is now annual-only, so there is no overlap);
  - late renewal (the only write that turns an expired contract active);
  - returned fee, rerating credit, installment and upgrade difference — as in round 1.
- New edge case (observation): the Plus sentence requires "every returned payment on the contract carries its returned-payment fee", while the fee policy now covers only "the most recent returned premium payment". If an older return lacked its fee while the newest had one, no write of this difficulty could satisfy the gate. Neither world has that shape.

### override_declarations (revision_2)

Sentence sweep against every `base_policy_refs` entry:
- G1 closed: `landlord_ext_returned_payment_fee.overwrite` now names base S6 ("The rate applies to monthly_installment … never to returned_payment, returned_payment_fee or transfer_fee charges.") and replaces it with a fixed-dollar courtesy, stating the rate is "still never applied as a percentage". The merged semantics are unique.
- G2 closed: rerating, installment and upgrade difference each now name base S2 and take "the rate recorded on the installment for the term's first billing period". The merged semantics are unique.
- O-8 closed (late renewal `replaced_by` names the pay-in-full rate). O-9 closed. O-10 closed (sale cancellation now declares the "never backdated" sentence and keeps the effective date at notice).
- **N-3 — SOURCE-POLICY finding (regression, undeclared override)**.
  - Round 1 priced the late-billed installment at "the tier the contract holds on the period start"; revision 2 changed it to "the base monthly amount of the tier the contract holds when the installment is billed".
  - Base `landlord_plan_upgrade_rules`: "A monthly-billed contract is billed the new tier's installment from the next billing period". This policy is not in the installment's `base_policy_refs` and is not named in its overwrite. The installment's overwrite names only the pricing sentence.
  - Constructed divergence: the 2026-09-17 period is unbilled and the contract is upgraded on 2026-09-20; the installment is billed late on 2026-09-29. Base: the period that started 09-17 carries the old tier, the new tier applies from 10-17, and the upgrade difference covers 09-21..10-16. Extended: the 09-17 installment is billed at the new tier, and the upgrade difference again bills 09-21..10-16 — two answers, one of them a double charge.
  - Task 1's upgrade (2026-08-22) precedes its unbilled period (2026-09-17), so both readings coincide there. Charter-level finding; observation at task level.

### factor_ladders (revision_2)

| policy | factors (label) | P | M | MS | X |
|---|---|---|---|---|---|
| catch-up | covered_share_convention (M), billing_delay_concession, homeowner_plan_concession (X homeplan), catchup_autopay_concession (MS: payment row × returned rows), term_count_goodwill | 4 | 1 | 1 | 1 |
| late renewal | returned_history_pif_rate, claims_experience_loading (MS), request_frequency_loading, tenure_credit, line_plan_bundle_credit (MS, X lineplan), lapse_day_credit (M) | 5 | 1 | 2 | 1 |
| returned fee | repeat_return_level, returned_size_basis (M), returned_channel_addition, portfolio_courtesy, fee_ageing_reduction | 4 | 1 | 0 | 0 |
| Plus upgrade | repeat_change_share (M, MS), term_timing_adjustment, plus_line_bundle_credit (MS, X lineplan), plus_autopay_credit (MS) | 3 | 1 | 3 | 1 |
| rerating | rerated_count_goodwill, overcharge_interest (M), correction_tenure_goodwill, correction_autopay_goodwill (MS), line_plan_customer_goodwill (MS, X lineplan) | 4 | 1 | 2 | 1 |
| installment | correction_goodwill (MS), late_billing_goodwill, installment_homeowner_credit (X homeplan), installment_line_credit (MS, X lineplan), installment_autopay_discount (M) | 4 | 1 | 2 | 2 |
| upgrade difference | difference_period_share (M), difference_delay_concession, upgrade_term_timing, contract_tenure_credit, difference_homeowner_credit (X homeplan), difference_autopay_credit (MS) | 5 | 1 | 1 | 1 |
| sale cancellation | closing_anchor_share (M), recent_claim_holdback, homeowner_plan_bonus (MS, X homeplan), payment_record_bonus, departing_tenure_bonus | 4 | 1 | 1 | 1 |

Round-1 structural findings:
- **G3 closed**: lapse_day_credit now selects an actual-day convention, (365 − lapse days)/365, against a whole-week convention, (52 − ⌊lapse/7⌋)/52, against none. The unit and the rounding differ, so this is an honest method.
- **G4 closed**: overcharge_interest is daily simple interest (1 + 0.12·d/365) against monthly simple interest (1 + 0.01·m) against none. These are distinct formulas.
- **G5 closed**: portfolio_band_goodwill and overcharge_size_goodwill are removed. The ladders of the new rerating factors are live in all tiers: one zero-rate installment; no ACH; no line plan or fewer payments; under 730 days of tenure.
- **G6 (a)–(i) closed**: every flagged ladder is removed. after_hours_surcharge, tenant/volume/emergency/coverage-use/unpaid loadings, the line-channel goodwill, the returned-payment offset and the remaining-term bonus no longer appear in any policy.

New factors, judged for realism:
- Normal practice in the line: autopay (ACH) discounts, the late-billing goodwill on an installment Bridgewell failed to bill, the chargeback/check channel addition on an NSF fee, the 2.5 % basis for a large returned payment, and the full/none/prorated period-share convention.
- Retention or relationship gestures that are unusual but publishable — observation O-12 (revision 2):
  - the term-count goodwill on a catch-up;
  - the tenure/line-plan goodwill on a correction;
  - homeowner/line-plan credits on late-billed installments and upgrade differences;
  - the departing-customer tenure bonus on a refund.

New structural finding:
- **N-1 — SOURCE-FACTOR RED (ladder with only two live tiers; class sweep incomplete)**: `landlord_ext_notice_period_installment.late_billing_goodwill`.
  - Its fall-through is "0 when it is billed on its due date".
  - The same policy's scope and overwrite say: "For an installment that fell due and was never billed this policy fixes the installment as set out here, and only for such an installment; every installment billed on its due date remains under the base pricing rule."
  - An installment billed on its due date is therefore never priced by this policy. Every customer who reaches this write is on the "1 to 10 days" or the "more than 10 days" tier, and the condition "billed at least one day late" restates the policy's scope.
  - Within scope the ladder has two tiers. Bears on task 1.

  The remaining four factors of that computation still meet the bounds (1 M, 3 P).

### findings (revision_2)

- Closed since round 1: G1, G2, G3, G4, G5, G6(a)–(i); O-1, O-2 (on task 1's world), O-3, O-4, O-5, O-6, O-7, O-8, O-9, O-10, O-11 (residual duplicate expression `period_position_days` = `days_left`, harmless).
- O-12: the card concession is gone; relationship credits remain as observations (above).
- New:
  - **N-1 SOURCE-FACTOR RED** (installment late-billing ladder; bears on task 1).
  - **N-3 SOURCE-POLICY finding** (regression: tier "when the installment is billed" vs base "new tier's installment from the next billing period"; no consequence on task 1's world).
  - N-2 observation (difference ← installment edge is in substance a state gate).
  - Fee-coverage edge case (observation).

### closing_checklist (revision_2)

Written after both round-2 reveals. **The difficulty is not closed.**

| task | policy | tree | factors | unique solution |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | PASS (all values equal GT) |
| 1 | PASS (N-3 no consequence) | PASS (N-2 obs.) | **SOURCE-FACTOR RED (N-1)** | PASS (all values equal GT) |

What holds:
- Every round-1 RED (G1–G6) is verified closed.
- Scopes are disjoint and cover all 8 policies. Tools are unchanged and their uuid8s are independent.
- Both trees have n = 3, ≥ 2 genuine value_input edges and a user root, and are acyclic.
- Every factor bears weight, and all-baseline results differ from gold. The figures match GT exactly.

Outstanding:
- N-1 (RED, task 1).
- N-3, a regression introduced by the rework: a charter-level undeclared override with no consequence on either current world.
- N-2 (observation).

Gates were not re-run by this audit; the coordinator's round-2 snapshot is cited.

## revision_3

### charter_global_frozen (revision_3)

- Re-audit round 3. Written starting 2026-10-12 21:01:24 UTC (system clock), before any round-3 task JSON was opened. Text of earlier revisions is untouched.
- Hashes, re-checked and matching the brief:
  - `landlord.extended.yaml` `f5791a109e8f1280445df5ea15d5c8103740579f244407ad59ddae7d2d4fce2f` — changed, so the charter-global sections are re-derived below.
  - `task_tools.py` `f0327668…05913` — unchanged; `#action_binding_and_uuids` is carried forward by reference.
  - Views `787fde36…a536` and `77c92cd8…4a61` — unchanged since round 2, so the worlds are the same.
- Base copy still verbatim (diff shows only the trailing blank line). Gate snapshot supplied. Entry met.

### delta and closure check (revision_3)

I read every extended rule and prerequisite in full and diffed them against revision 2. Changes:
1. **landlord_ext_notice_period_installment**:
   - New sentence: "The tier in force for the period billed is the tier the contract held before its most recent tier change when that change was made on or after the period's start date, because a new tier's installment is billed only from the next billing period, and is otherwise the tier the contract holds." The standard installment now uses "the tier in force for the period billed".
   - Compute: `base_monthly_a = prior_base_a if (last_plan_change_date != '' and DAYS(period_end_before, last_plan_change_date) >= 1) else current_base_a`. This is equivalent to "change on or after the start of the period billed" (that period starts the day after `period_end_before`).
   - The late-billing ladder is now "more than 20 days → 0.05; 11 to 20 days → 0.03; otherwise (1 to 10 days) → 0".
2. **landlord_ext_upgrade_difference_charge**: the edge to the installment is now `kind: state_gate`, `gate: landlord_billing_entries.billing_period_start`. Its condition and effect are reworded generally.
3. **landlord_ext_plus_upgrade_charge**:
   - Prerequisite sentence 3 now reads "No upgrade charge is fixed until the most recent returned payment on the contract carries its returned-payment fee." Its edge condition was aligned to match.
   - Repeat-change share, tier 2: "the whole calendar months from the upgrade date to the term end date, counted down to whole months, divided by twelve" (the "+1" is dropped). Compute: `remaining_months_u / 12`.
4. Catch-up, late renewal, returned fee, rerating and sale cancellation are unchanged.

Closure of the round-2 items:
- **N-1 closed.** All three late-billing tiers lie inside the policy's scope (billed 1+ days late), and their values (0.05 / 0.03 / 0) are distinct.

  I repeated the class sweep for every ladder of all eight policies against each policy's own scope. No other fall-through is out of scope:
  - catch-up term-count "one" is reachable on a first-term upgrade;
  - the late-renewal lapse fall-through is reachable with auto-renew off;
  - the fee repeat-level fall-through (exactly one return) is reachable;
  - the remaining fall-throughs are reachable by inspection.
- **N-3 closed.** The installment now follows base `landlord_plan_upgrade_rules` ("A monthly-billed contract is billed the new tier's installment from the next billing period"); none of its sentences contradicts that rule, so no overwrite is needed. In the constructed world of revision 2 (period 09-17 unbilled, upgrade 09-20), the 09-17 installment now takes the old tier, the difference covers the rest of that period, and there is no double charge.
- **N-2 closed.** The edge is declared a state gate. The gate field is real, and the sentence's state is false at the opening on task 1. Task 1's tree keeps 2 `value_input` edges = max(3 − 1, 1).
- **Fee-coverage gap closed.** The Plus quantifier ("the most recent returned payment") now matches the fee policy's scope ("the most recent returned premium payment"), so every possible gate state has a resolving write.
- **T0-O1 closed.** On a day-0 upgrade tier 1 gives share 1, tier 2 gives 11/12 and the fall-through gives 364/365. The three tiers are distinct, and the 2026-07-03 authorization near-miss (exactly 3 months) now changes the value.

Re-checks:
- Verbatim `policy_source`, compute_basis ⊂ rule, baseline.rule ⊂ rule, `resolved_by` = depended-on `target_tool`, real gates, acyclic graph — all pass (string-checked).
- No overwrite was removed or added except as described; G1/G2 declarations are intact.
- Factor counts are unchanged: per policy 4–6 factors, ≥ 2 P and 1 honest M. MS/X per task as in revision 2.

No new defect. Two pre-existing shapes that I had not written up before are recorded now as observations. Neither touches either world, and neither is a regression:
- **O-13**: `landlord_ext_returned_payment_fee`'s portfolio courtesy reads "the portfolio discount rate recorded on the contract's most recent annual premium charge", but the policy's scope includes monthly-billed contracts, which carry no annual premium charge. The rule's "0 otherwise" gives a reading; the compute (`None >= 0.10`) has none. Task 0's contract is annual.
- **O-14**: `landlord_ext_upgrade_difference_charge`'s "7 or fewer days left → no difference is charged" tier makes a zero charge. The tool contract expects a positive amount, and the sale-cancellation gate asks that the upgrade "carries its upgrade charge", so whether a 0.00 charge must be billed is not stated. Task 1 has 25 days left.

### closing_checklist (revision_3)

Filled after both round-3 reveals.

| task | policy | tree | factors | unique solution |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | PASS (all values = GT) |
| 1 | PASS | PASS | PASS | PASS (all values = GT) |

**All four relationships PASS for both tasks. The difficulty passes the source-layer audit at revision 3.**

Checklist:
- The per-task files `0.md` and `1.md` correspond to the tasks. Revisions 1–3 are preserved in order. Every comparison section of revision 3 carries PASS.
- All 8 extended policies are covered. The two scopes (from `charter_scope`) are disjoint. The 8 task tools are unchanged with independent uuid8s. Tools and GT are closed.
- Each tree has 3 prerequisite problems, ≥ max(n − 1, 1) = 2 value_input edges (task 0: 3; task 1: 2) and a user-owned root, and is acyclic. The difficulty-wide graph is acyclic.
- Every computation has a self-sufficient baseline that differs from gold, and 4–6 factors (≥ 2 P, 1 honest M). Each task has at least 1 multi-source and 1 cross-difficulty factor. Every ladder has 3 distinct, in-scope tiers stated in the rule. Every factor bears weight on its world, and the figures equal GT's.
- Gates: the coordinator's round-3 snapshot is cited (all OK except TRACEABILITY pre-docs unlock misses). This audit did not re-run them.

Open observations (not grounds for rework):
- O-13: fee courtesy on a monthly contract.
- O-14: zero-share upgrade difference.
- O-12: relationship credits.
- The O-2 cascade at charter level: a sale cancellation does not end an attached rider; no current world has one.


## revision_4

### charter_global_frozen (revision_4)

- Re-audit round 4. Written starting 2026-10-13 04:32:45 UTC (system clock), before any round-4 task JSON was opened. Earlier revisions are untouched.
- Hashes, re-checked and matching the brief:
  - `landlord.extended.yaml` `62e60988da596ecf3f31be44ff84faf47db6bca71f25483d17ea61ecf71425c1` — changed.
  - `task_tools.py` `f0327668…05913` — unchanged; `#action_binding_and_uuids` carried forward.
  - Views `787fde36…a536` / `77c92cd8…4a61` — unchanged.
- Base copy still verbatim.
- Also read: `audits/render_notes/landlord.md` (three renderer items).
- Gate snapshot supplied, all OK including TRACEABILITY.

### delta (revision_4)

I diffed every extended rule and prerequisite sentence-by-sentence against revision 3 (the round-3 dump). Only three policies changed. Catch-up, late renewal, Plus upgrade, installment and sale cancellation are identical in rule and prerequisites.
1. **landlord_ext_upgrade_difference_charge**:
   - The overwrite of base `landlord_plan_upgrade_rules` ("A monthly-billed contract is billed the new tier's installment from the next billing period;") is removed. The rule now says: "A monthly-billed contract upgraded part-way through a billing period is also billed the difference for the rest of that period as set out here, while the new tier's installment is billed from the next billing period."
   - Period share, short-remainder tier: "when 7 or fewer days were left, a one-week minimum of 7 days divided by 30 is charged for that period". Compute: `minimum_charge_days / month_days_convention` when `period_position_days <= minimum_charge_days` (7).
2. **landlord_ext_rerating_correction_credit**: the three cancellation-credit overwrites remain, with new `replaced_by` sentences, each carried verbatim in the rule:
   - "The condition that a premium credit waits on a confirmed cancellation request binds cancellation credits only, so this policy posts a billing-correction credit without one, and only such a credit; every cancellation credit remains under the base rule."
   - "The sale-waiver window conditions only the admin fee of a cancellation credit, so it is not applied to a billing-correction credit, and only to such a credit; …"
   - "The count of one credit and one refund per cancellation request covers cancellation credits only, so a billing-correction credit, which names no cancellation request, is not counted against it, and only such a credit is exempt; …"
3. **landlord_ext_returned_payment_fee**:
   - The card tier now reads "10.00 when it had been made by card", which equals the compute `returned_method == 'card'`.
   - New sentence: "The contract's recorded portfolio discount rate is the rate recorded on its most recent annual premium charge for an annual-billed contract, and the rate recorded on the installment for the current term's first billing period for a monthly-billed contract." The courtesy and the S6 `replaced_by` now read "the contract's recorded portfolio discount rate". The compute branches on `F('billing_frequency')`.

### closure check (revision_4)

- **Render item 1 — closed.** No overwrite now retires the next-billing-period sentence. The difference rule restates it as still in force and adds a charge for a quantity the base never governs: the base names an annual proration and a next-period installment, and says nothing about a mid-period difference on a monthly contract. No base sentence reaches a different conclusion on any quantity this policy scores, so no override is needed and none is undeclared.
- **Render item 2 — kept by route-around; the narrowing is stated exactly.** Each of the three base sentences binds `landlord_premium_credit` through its eligibility block:
  - `credit_after_confirmation` applies_to [landlord_premium_credit];
  - `sale_waiver_window` applies_to [landlord_premium_credit];
  - `one_credit_one_refund` applies_to [landlord_premium_credit, landlord_premium_refund].

  So the overwrites are real narrowings. Each `replaced_by` names the scope it narrows to (cancellation credits) and the one class exempted (billing-correction credits). The first clause ("binds cancellation credits only") and the second ("only such a credit") coincide exactly, because the base event `landlord_premium_credit` has only two kinds ("A premium credit is posted for a cancellation or a billing correction."). The second sentence rests on the base formula, where the sale window enters only `admin_fee_applied`. The third rests on the dedup key `landlord_cancellation_request_id`, which a correction credit does not carry. None of the three says more than it narrows, and the merged semantics are unique.
- **Render item 3 — closed.** Wording equals compute. Realism: a card payment that comes back is a chargeback, and a higher fee for it than for a check is ordinary practice.
- **O-13 — closed.** The recorded rate is now defined for both billing frequencies. The monthly branch uses the same first-period-installment rate as the declared G2 overrides. On task 0's annual contract the value read is unchanged.
- **O-14 — closed.** A zero charge is no longer possible, so the tool's positive-amount contract and the sale-cancellation gate are always satisfiable.
  - Distinct method: the tier is a constant share (7/30 regardless of the days left), against a proportional share (days left/30) and the full share. It equals the proportional share only at exactly 7 days left; below that the two differ. It is a floor, a different algorithm, not a substituted number.
  - Realism: a minimum billing increment (one week) on a partial-period upgrade is an ordinary billing convention.
  - Observation O-15: the boundary day 7 sits in the minimum tier, where its value equals the prorated value. This is harmless and no ladder value is duplicated across a tier.

### structural re-check (revision_4)

String checks on all eight policies pass:
- every `compute_basis` is in its rule;
- every `baseline.rule` sentence is in its rule;
- every overwrite `replaced_by` is carried verbatim in its rule;
- every `policy_source` is verbatim;
- every `resolved_by` equals the depended-on `target_tool`.

The graph is unchanged and acyclic. Factor counts per policy: catch-up 5, late renewal 6, fee 5, Plus 4, rerating 5, installment 5, difference 6, sale 5; each has exactly 1 method factor and ≥ 3 parameters. In-scope sweep repeated for the changed ladders (difference period share; fee channel; fee courtesy): every tier is reachable inside its policy's scope.

No new defect and no regression found. Open observations: O-12 (relationship credits), O-15 (above), and the charter-level O-2 rider cascade (no world has a rider).

### closing_checklist (revision_4)

Written after both round-4 reveals (2026-10-13 04:32:49 UTC).

| task | policy | tree | factors | unique solution |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | PASS (all values = GT) |
| 1 | PASS | PASS | PASS | PASS (all values = GT) |

**All four relationships PASS for both tasks. The difficulty passes the source-layer audit at revision 4.**

Checklist:
- Revisions 1–4 are preserved in order.
- Scopes are disjoint and cover all 8 policies.
- Tools are unchanged with independent uuid8s.
- Each tree has 3 prerequisite problems, ≥ 2 value_input edges and a user root, and is acyclic.
- Every computation has a self-sufficient baseline that differs from gold, 4–6 factors (≥ 2 P, 1 honest M), MS and X factors per task, in-scope distinct tiers, and every factor bearing weight with figures equal to GT.
- Gates: the coordinator's round-4 snapshot is cited, all OK including TRACEABILITY. This audit did not re-run them.

Open observations: O-12, O-15, and the O-2 charter-level rider cascade.


## revision_5

### charter_global_frozen (revision_5)

- Re-audit round 5. Written starting 2026-10-13 05:10:17 UTC (system clock), before any round-5 task JSON was opened. Earlier revisions are untouched.

Gates, run by this auditor from the repository root starting 2026-10-13 05:08:54 UTC (run only, nothing edited):
- check_extended → `EXTENDED OK`
- check_task_tools → `TASK TOOL CONTRACT OK`
- check_solvability → `SOLVABILITY OK`
- check_compute → `COMPUTE OK` (history_rows_max=107, branches_max=62)
- check_grounding → `GROUNDING OK`
- check_cross_fire → `SCOPE OK`
- check_traceability → `TRACEABILITY OK`
- replay_tasks.py … --check → `REPLAY OK` (0.json 17 acts, closure 61/61 match; 1.json 19 acts, 115/115 match)

`/tmp/erl0058_coord/mkviews.py rental_property_renewals_and_cancellations` was run only, not edited. Hashes it reported (and re-hashed by me):
- 0.view.json `787fde3612a57ebe81772d18952f3cae7d89e72d21656600e2f99671eae4a536`
- 1.view.json `77c92cd8d6ac549bebbdace6251d015f5e6bff3e3d4e8e4be5cbeda9d7674a61`
- task_tools.py `f0327668d3df3ad7c766d9e5032ab1931ae9fc5b211564bd4d6ebe3b71005913` (unchanged)
- landlord.extended.yaml `f6f41a4e5ef12967bb910d5c3fba11f7723d20ffb8b8d95426829695ebade885` — changed from revision 4's `62e60988…25c1`.

All gates are green and the charter changed, so the entry conditions are met and the input is not incomplete.

Also read: `audits/policy_kb/rental_property_renewals_and_cancellations/0.md` "Policy-side notes". This is the landlord KB audit of this same difficulty; I read only the routed note and its section.

### delta (revision_5)

- Every extended `rule` is identical to revision 4 (sentence diff against the revision-3 dump plus the revision-4 dump of the three policies changed in round 4: 8/8 RULE SAME).
- Prerequisites are identical: kinds, gates and sentences.
- The rework is confined to the rounding surface of `landlord_ext_returned_payment_fee`:
  - compute `fee_basis` is now `K('large_returned_share') * returned_amount if …`, no longer `RND(…, 2)`;
  - the `returned_size_basis` ladder's percentage tier now reads "2.5 percent of the returned payment replaces the fee level, carried unrounded until the fee is rounded once at the end".

### rounding item — closure check (revision_5)

- **Rule, ladder and compute now agree.**
  - Rule: "the returned-payment fee is the fee before ageing times one less the ageing reduction, rounded to the cent once at the end".
  - Ladder: the percentage basis is "carried unrounded until the fee is rounded once at the end".
  - Compute: one `RND(…, 2)`, at `result` only.
- Probe on the KB note's example (task 0's world with the returned amount set to 1000.20, check channel +5.00, courtesy −5.00, ageing 0.50): `fee_basis` = 25.005 unrounded, and the fee = RND(25.005 × 0.5) = **12.50**. That is the once-at-the-end reading. The old compute gave 12.51.
- Class sweep: I checked every rounding sentence of all eight rules against its compute.
  - Each policy's final "rounded to the cent once at the end" maps to a single `RND` at `result`, and no compute holds another `RND`.
  - The only other truncations are ones the rules state themselves: the lapse "whole weeks of lapse" (`int(lapse_days/7)`), the sale "counted down to whole weeks", and `MONTHS` "whole calendar months".
  - The "standard … rounded to the cent once at the end" sentences describe the baselines. Where a rule then scales the standard amount, it says so: "before rounding" (late renewal); "after the autopay discount is rounded … once at the end" (installment).
  - No rule-vs-compute rounding gap remains.
- Structural re-check passes on all eight policies:
  - every `compute_basis` and `baseline.rule` sentence is in its rule;
  - every `replaced_by` is carried in its rule;
  - every `policy_source` is verbatim;
  - every `resolved_by` is correct;
  - factor counts (5/6/5/4/5/5/6/5) and 1 method each are unchanged; the graph is unchanged and acyclic.
- Note for the coordinator (outside this skill's four relationships): the KB note says the rendered `returned_payment_size_basis` document carries "2.5 percent of the returned payment, rounded to the cent". The source ladder now says the opposite, so that document is stale relative to the revised source until the landlord docs are re-rendered.

No new defect, no regression.

### closing_checklist (revision_5)

Written after both round-5 reveals (2026-10-13 05:10:22 UTC).

| task | policy | tree | factors | unique solution |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | PASS (all values = GT, unchanged) |
| 1 | PASS | PASS | PASS | PASS (all values = GT, unchanged) |

**All four relationships PASS for both tasks. The difficulty passes the source-layer audit at revision 5.**

- The instantiation-stage gates were re-run by this auditor on the final form. All are green: EXTENDED, TASK TOOL CONTRACT, SOLVABILITY, COMPUTE, GROUNDING, SCOPE, TRACEABILITY and REPLAY --check (`#charter_global_frozen (revision_5)`).
- Scopes are disjoint and cover all 8 policies. Tools are unchanged.
- Trees: n = 3, ≥ 2 value_input edges, a user root, acyclic.
- Factor bounds hold, every factor bears weight, and the figures equal GT.
- Revisions 1–5 are preserved in order.

Open observations: O-12, O-15, the O-2 charter-level rider cascade, and the stale rendered `returned_payment_size_basis` wording, which is a KB-side item for re-render.
