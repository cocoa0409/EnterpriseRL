# Policy-task audit — renters_billing_and_cancellation / charter-global

## charter_global_frozen

- Scenario: `env/env_0024_homeowners_insurance_carrier`, difficulty `renters_billing_and_cancellation`, M=2, round 1 (revision_0).
- Freeze hashes (re-checked against the brief before reading):
  - `tasks/renters_billing_and_cancellation/renters.extended.yaml` sha256 `97c7e0911a98905bb359d890f8abfcc9257e913fd2f25e0e5439c0428a64cdb6`
  - `tasks/renters_billing_and_cancellation/task_tools.py` sha256 `bd6e72d72aa5b250a5b450fb8cb8bb30414736d192c9ea471b6a61460ad99ac9`
- Freeze time: 2026-09-24T23:45Z. Auditor: independent audit agent (erl-task-policy-audit); not the instantiating agent.
- Read for this section: `blueprint/blueprint.yaml`, `blueprint/products/renters.yaml`, `blueprint/share_tools.py` (tool list and signatures), the extended charter, `task_tools.py`. No task JSON, no worklog, no GT-bearing file was read; this section contains nothing derived from any revealed GT.
- Masked until every task's derivation was frozen: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`.
- Entry conditions (Step 0): the brief supplied the gate snapshot (check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire — all exit 0; check_traceability deferred until KB publication), and masked views with hashes (`0.view.json` 6b53d2…b8a, `1.view.json` 6ff755…ac9), both re-verified by sha256sum. Entry conditions complete.

Base-section verbatim check: `diff <(sed -n '1,1419p' renters.extended.yaml) blueprint/products/renters.yaml` differs only by the four appended separator/comment lines before `extended_policies:` — the base copy is verbatim.

### policy_conflict_scan

Six extended policies, one tree per task:

| policy | trigger | target_tool (owner) | computes | subject | prerequisite |
|---|---|---|---|---|---|
| renters_ext_discount_stop_charge | state_due | post_discount_stop_charge_d8b9b7f1 (agent) | amount | renters_additional_premium | [] |
| renters_ext_discount_restart_credit | state_due | post_discount_restart_credit_e779526e (agent) | amount | renters_return_premium | stop (value_input) |
| renters_ext_late_charge | state_due | assess_late_charge_664a192e (agent) | amount | renters_fee_assessed | [] |
| renters_ext_catch_up_amount | on_request | pay_catch_up_by_card_50a8e701 (user) | amount | renters_payment_received | restart (value_input), late (value_input) |
| renters_ext_reinstatement_cure | on_request | pay_reinstatement_cure_5468a22a (user) | amount | renters_payment_received | [] |
| renters_ext_reinstatement_fee | on_request | reinstate_lapsed_policy_e7e59896 (agent) | reinstatement_fee | renters_policy_reinstated | cure (value_input) |

Overlaps examined:

- **Both halves of one base sentence.** `renters_agg_bundle_discount` sentence 3 ("When a qualifying policy is bound … starts on that policy's effective date, and when the last qualifying policy ends … stops on that policy's closed date; each is re-rated … under renters_midterm_changes.") is superseded twice — by the stop policy (stop half) and by the restart policy (start half). The two `replaced_by` sentences govern disjoint events (an ending vs a taking-effect of a qualifying policy) and different entry types (additional vs return premium), so the merged semantics stay unique. PASS.
- **Two user payment writes on one event type.** `pay_catch_up_by_card` and `pay_reinstatement_cure` both create `renters_payment_received` (card). Disjoint by their own rules' eligibility: catch-up is for "a named insured of a policy in force"; cure is for "a policy cancelled for nonpayment". A policy cannot be both at one handling time. PASS.
- **Premium restatement.** Stop and restart both restate `term_premium`; restart's value_input edge reads the stop's restated figure, so their order is fixed by the declared edge. PASS.
- **Late charge vs cure/fee.** The late-charge policy posts `late_fee` entries that the cure (current-term late count), the fee (late charges in 12 months) and the catch-up (acceleration tier) read. The late charge only applies to "a renters installment still unpaid"; on a cancelled policy whose balance is a credit none is unpaid (checked per task). No conflict.
- **Cross-category read boundaries.** Declared reads: umbrella/valuables (branch), flood (history/branch), dwelling (history/branch). Every compute CFIELD/XCOUNT category is declared in `cross_category` and `inputs.cross_category`. PASS.
- **Scope exclusivity / completeness.** Task scopes (derived from each task's tree, not from masked `charter_scope`): task 0 = {stop, restart, late, catch-up}; task 1 = {cure, fee}. Disjoint, and together cover all six extended policies. (To be re-confirmed against `charter_scope` after the reveal, in the closing checklist.)

### rule_compute_equivalence

Swept every compute binding against its `compute_basis` quote and back from every rule sentence. All windows (12/24/36/60 months), tier thresholds, cross-category reads, rounding points ("rounded half-up to the cent once, on the final figure only") and floors ("never below 0.00", "never less than minimum_annual_premium") have a verbatim basis, and every factor ladder tier is both a rule sentence and a branch of its `decides` binding. Findings are imprecisions whose consequence is world-dependent and does not arise in either task world (see per-task files), recorded as observations:

- O-RC1 (stop): `stop_ended_date` / `stop_ended_reason` / `stop_ended_held_months` take the first non-empty of umbrella-cancelled, umbrella-expired, valuables-cancelled, valuables-expired. The rule speaks of "the last live … ends" and "the ending qualifying policy". With two ended qualifying policies in one term the compute imposes an umbrella-first precedence the rule does not state. Neither task world has two.
- O-RC2 (late): `late_service_charge` = LATEST installment_fee by posted_date across the policy; the rule reads "its installment service charge" (the overdue installment's). Coincide whenever the overdue installment is the latest billed (which the rule itself defines it to be). No divergence possible under the rule's own definition; observation only.
- O-RC3 (late): the rule's first sentence ("A renters installment still unpaid after its late-fee grace period …") and its second ("The overdue installment is the installment of the term with the latest due date among those billed") can disagree when the latest billed installment is billed but not yet due (installments post bill_lead_days = 15 days before due). The compute follows the second sentence only. Task 0 world: the latest billed installment is overdue, so no divergence there.
- O-RC4 (catch-up/cure): the "account balance"/"unpaid charges" sums in compute are `SUM` over the policy's `renters_billing` with no term filter, as the rule says ("every installment billed … posted on the premium account"). Consistent.
- O-RC5 (restart): `restart_gross_premium` divides the current annual premium by (1 − autopay) — correct only when the current premium was not floored at `minimum_annual_premium`; the rule states the same division, so rule and compute agree (a base-vs-extended issue, see override_declarations O-OV2).

No compute binding invents a basis; no rule sentence is left unimplemented. PASS (with observations).

### action_binding_and_uuids

- `(target_tool, computes)` pairs: six distinct tools, each claimed by exactly one policy. PASS.
- Tool bodies (`task_tools.py`): every function performs its posting unconditionally — no eligibility test, no prerequisite test, no amount validation, no error/hint path. Confirms the tool layer judges no prerequisite (module docstring: "none of them checks eligibility, prerequisites or amounts").
- Docstrings and ordering language: no docstring names another tool. All contain "The caller can afterwards see …" — describing the observable result of the same call, not a position in a sequence. **Observation O-AB1:** `pay_reinstatement_cure_5468a22a` says "Pay the cure amount … so it can be considered for reinstatement … it does not by itself put the policy back in force." This states the purpose of the payment relative to another problem (reinstatement) and so conveys, in the tool surface, the same cure→reinstatement relationship the fee policy's prerequisite sentence carries. It creates no second reading (it is consistent with the sentence), so it is not red; it does weaken the discovery burden of task 1's single edge. Bears on task 1.
- `reinstate_lapsed_policy_e7e59896` requires `renters_request_id` of "the signed statement of no loss" and marks it completed; no tool lets the customer sign one, so the statement must already be seeded (checked per task).
- UUID8s: d8b9b7f1, e779526e, 664a192e, 50a8e701, 5468a22a, e7e59896 — all distinct, no common stem, no arithmetic sequence, no shared tail. (e779526e and e7e59896 share only the leading "e7"; the remaining six hex digits are unrelated.) PASS.

### prerequisite_graph

Check 7 over the four declared edges:

| blocked policy | problem | kind / gate | form | policy_source verbatim in own rule | gate exists in compute | resolved_by = depended target_tool |
|---|---|---|---|---|---|---|
| restart | stop | value_input / `restart_old_premium` | state | yes | yes (`F('term_premium')`) | yes (d8b9b7f1) |
| catch-up | restart | value_input / `catch_balance` | state | yes | yes | yes (e779526e) |
| catch-up | late | value_input / `catch_balance` | state | yes | yes | yes (664a192e) |
| fee | cure | value_input / `fee_cure_payment` | state | yes | yes | yes (5468a22a) |

- `prerequisite` filled on every policy (`[]` on stop, late, cure). Every `problem` is an extended policy id of this file, none self-referencing, none base. Graph: restart→stop, catch-up→restart, catch-up→late, fee→cure — acyclic (two components). No `fallback_reason` needed (all state form) and none present. No authoring-viewpoint phrasing ("this task", "at the opening", "current world") in any condition/effect.
- Effects: stop restates `term_premium`, which is exactly `restart_old_premium`; restart and late post entries that `catch_balance` sums (and the late charge feeds `catch_late_charges_12m`); the cure payment becomes the `LATEST` payment on or after `closed_date` read by `fee_cure_payment`. Each `resolved_by` genuinely changes its binding. PASS.
- Observation O-PG1 (condition strength, restart←stop): the `condition` adds "and renters_policies.term_premium has been restated to the annual premium after that stop", which the prerequisite sentence does not say. The only write that posts the charge (d8b9b7f1) also restates the premium in the same call, so the extra clause cannot be false when the sentence is true; no second reading.
- Observation O-PG2 (condition strength, fee←cure): the sentence says a payment "that covers the cure amount" (≥); the `condition` says "whose amount equals the cure amount". The condition is narrower than the sentence. Where a customer pays more than the cure amount the sentence is satisfied and the condition is not. The persona of task 1 pays "exactly the amount they give you", so no consequence is demonstrable there.

### prerequisite_sentences

Four-point test on each sentence, then the single-reading derivation.

1. restart ← stop: "The restart credit is not posted until the premium account carries a multi-policy discount change charge dated the closed date of every qualifying policy that ended earlier in the same renters term."
   - connective: "not … until" ✓; state form: a charge entry on the premium account, reason multi-policy discount change, dated a closed date ✓; no tool, no policy id, no snake_case ✓; strength: "every qualifying policy that ended earlier in the same renters term" = condition's "every umbrella or valuables policy … that closed inside the current renters term" ✓.
   - Exactly one write brings it about: only the stop policy's rule posts "one additional premium entry with change_reason multi_policy_discount_change dated the closed date of the ending qualifying policy" (the restart posts a credit, not a charge; no other tool posts an additional premium). Derivation: sentence → records (qualifying policy with a closed date inside the term, no such charge) → the stop rule ("When the last live … ends during the renters term … owes a discount-stop charge …") → post_discount_stop_charge. Single reading ✓.
2. catch-up ← restart: "The catch-up amount is fixed only after the premium account carries a multi-policy discount change credit dated the effective date of every qualifying policy that took effect during the renters term."
   - "only after" ✓; state form (a credit entry, reason, date) ✓; no tool/id ✓; strength equals the condition ✓.
   - One write: the restart rule's "one return premium entry with change_reason multi_policy_discount_change and credit_basis pro_rata dated the effective date of the new qualifying policy". Single reading ✓.
   - Observation O-PS1: the sentence (and condition) demand such a credit for **every** qualifying policy that took effect during the term, whereas the restart rule only produces one "while the renters premium carries no multi-policy discount". In a world where a second qualifying policy takes effect while the discount is still carried, no write can satisfy the sentence and the catch-up would be blocked forever. Neither task world has this shape (task 0: the only qualifying policy taking effect in term is the floater, after the umbrella ended).
3. catch-up ← late: "The catch-up amount is fixed only after each installment of the term left unpaid past its late-fee grace period carries a late charge on the premium account."
   - "only after" ✓; state form ✓; no tool/id ✓; strength equals the condition ✓. One write: the late-charge rule ("… carries one late charge, posted as one fee entry with fee_code late_fee referencing the term and the installment number"). Single reading ✓ (subject to what "left unpaid" means under a returned payment — task-level, see 0.md).
4. fee ← cure: "The reinstatement is not recorded until the premium account shows a payment received on or after the cancellation date that covers the cure amount."
   - "not … until" ✓; state form ✓; no tool/id ✓. Strength: see O-PG2.
   - Two tools can create a `renters_payment_received`: pay_reinstatement_cure and pay_catch_up_by_card. The catch-up rule is restricted to "a named insured of a policy in force", so on a cancelled policy only the cure rule ("A named insured asking to reinstate a policy cancelled for nonpayment pays the cure amount by card in one payment") applies, and "the cure amount" names that policy's quantity. Single reading ✓.
- The depended-on rules do not restate any of the four sentences (checked by substring). No rule names a tool or another policy id. No docstring states an order (see O-AB1 for the purpose clause).
- Undeclared cross-problem order: the only base rule sentence stating an order across problems in this charter's scope ("Before reinstatement, payments received since the cancellation date must cover renters_msr_amount_due as of the request date plus the reinstatement fee.") is superseded by the cure policy's `overwrite`; the fee edge rests on the extended sentence, not on it. The cure rule's clause "the reinstatement fee is not part of it because it is charged at reinstatement" is a rationale, not an ordering connective, and matches the declared edge's direction. PASS.

### override_declarations

Sentence by sentence against each `base_policy_refs` entry (finding half only).

- **stop** — refs: bundle_discount, insured_cancellation, reinstatement, midterm_changes, premium_rating.
  - bundle_discount s1 ("applies to every live renters policy … who also holds a live …"), s2 ("applied once … never stacks"), s4 (HomeGuard/CondoGuard do not qualify): followed. s3: superseded, declared ✓.
  - midterm_changes s6 (prorated change = annual change × days/term days): replaced by the year-share method — declared ✓. s7 ("An increase is posted as renters_additional_premium … dated the change effective date; when the prorated amount is below min_premium_change nothing is posted, but term_premium is still restated"): followed ("A discount-stop charge below min_premium_change is not posted"; premium restated). s1 (only while bound/in force/pending nonrenewal): inherited.
  - premium_rating s3 (discount %), s4 (subtotal reduced, rounded, floored): the stop re-derives the pre-discount subtotal by reverse division of the current premium instead of rebuilding it from contents/territory/deductible/liability charges. That is an anonymous intermediate: it equals the base subtotal only when the current premium was neither floored nor rounded away from subtotal × (1 − d). **Observation O-OV2** (world-dependent; checked per task: task 0 reverse-division gives 263.60 = base subtotal 40×5.94×1.00×1.00 + 26.00).
  - insured_cancellation, reinstatement: no sentence governs the scored quantity; followed.
- **restart** — refs: bundle_discount, insured_cancellation, midterm_changes, premium_rating. Declared: midterm s6, bundle s3, premium_rating s3 (discount %). The restart then adds schedule/household/tenure/dishonour points to the discount — this modifies the very sentence whose override is declared, so it is covered. Reverse division: O-OV2 applies identically.
- **late** — refs: fees_and_waivers; `overwrite: []`.
  - s1–s3 (grace period, counting, unpaid definition, at most once per installment): followed. s4 ("… a fee whose tier amount is 0.00 is not charged at all"): followed ("A tier whose late_fee is 0.00 charges no late charge at all").
  - **The amount of the late fee is handled differently and nothing is declared.** The base charges "a late fee" whose amount is the tier's `late_fee` ("late_fee: Late fee per late installment (USD; 0 = none)" in the base `parameter_schema`; s4 speaks of a fee's "tier amount"). The extended rule replaces that amount by a tenure-dependent base (3.00 / 4.00 / late_fee) plus dishonour and size additions, times a lateness multiplier. The extended policy's own `baseline.rule` concedes the base amount ("The late charge is the tier's late_fee"). The sibling policy `renters_ext_reinstatement_fee`, facing the identical construction for the reinstatement fee, *did* declare the override of the base "the reinstatement fee is charged" clause — the late policy leaves its analogue undeclared. **Finding F-1 (SOURCE-POLICY RED, undeclared override)**; consequence demonstrated in task 0's file.
- **catch-up** — refs: payment_application; `overwrite: []`. s1 (applied oldest charge first, reference as issued): followed. s2–s6 (returns, EFT suspension, plan changes): not touched. No base sentence fixes the amount of a customer's catch-up payment. PASS. (Observation O-OV3: the "card service charge on the catch-up" is added to the payment amount without any fee entry, so it lands as an over-payment credit; the base fee list — installment, late, returned-payment, reinstatement — has no such fee. No base sentence is contradicted because the base never forbids a payment of a given size.)
- **cure** — refs: payment_application, reinstatement. Declared: reinstatement s6 ("Before reinstatement … must cover renters_msr_amount_due … plus the reinstatement fee") ✓. Other reinstatement sentences (nonpayment only, window, frequency, statement of no loss, no-lapse reversal) inherited and not weakened.
- **fee** — refs: reinstatement, fees_and_waivers. Declared: reinstatement s7 (no-lapse reversal/fee charge) replaced with "the reinstatement fee worked out below is charged …" ✓. fees_and_waivers s4 ("the reinstatement fee once per reinstatement; a fee whose tier amount is 0.00 is not charged") followed ("A tier whose reinstatement_fee is 0.00 charges no reinstatement fee at all"). PASS.

### factor_ladders

Per policy: declared factors, labels, ladders; structure only.

**stop** (6 factors; declared 2 method / 4 parameter; cross_difficulty: flood)
- stop_courtesy_period — method, decides stop_charged_days; tiers: insured-request & held ≥12 whole months (closed→expiry − 30) / nonpayment (whole renters term) / otherwise (closed→expiry = baseline). Distinct methods (different anchor/deduction). Multi-source (status_reason + bound_date + closed_date). Stated in rule ✓. Honest label ✓.
- stop_plan_proration — method; monthly: ⌊days/30⌋/12 / two_pay: days/360 / otherwise: days/term days (= baseline). Genuinely different algorithms ✓.
- stop_flood_relief — parameter 25/10/0; multi-source (flood policy status+address × flood_billing payments in 24 months); cross_difficulty flood ✓.
- stop_tenure_relief — parameter 15/5/0 ✓. stop_claim_record_relief — parameter 10/5/0, multi-source (claims reported 60m × payments 36m) ✓. stop_dishonour_points — parameter 20/10/0 subtracted ✓.
- Counts: 6 factors, 2 honest method, 4 parameter, multi-source ≥1, cross_difficulty 1 ✓. Fall-through tiers equal `baseline` bindings, which equal `baseline.rule` ✓. `baseline.rule` self-sufficient (every sentence in the rule) ✓.

**restart** (6 factors; 2 method / 4 parameter; cross_difficulty: flood)
- restart_start_date — method; bound ≥14 days early & annual plan: bound date→expiry / bound ≥14 early & other plan: effective→expiry + 7 / bound <14 early: effective→expiry (= baseline). Multi-source (bound date, effective date, plan of the new policy). Honest ✓. Observation O-FL1: tier 2 credits 7 days beyond the renters expiration date, i.e. premium for days that are not in the term; an unusual loyalty-type bonus, recorded as an observation (no task takes this tier). Tier 1's "from its bound date" is consistent with the base definition of a live policy ("bound, in force, …").
- restart_plan_proration — method; monthly: ⌈days/30⌉/12 / two_pay: days/360 / otherwise: days/term days ✓.
- restart_schedule_points (2/1/0), restart_household_points (2/1/0; cross_difficulty flood; multi-source flood status × original_effective_date), restart_tenure_points (2/1/0), restart_dishonour_points (2/1/0 subtracted) — parameters ✓.
- Counts ✓.

**late** (4 factors; declared 1 method / 3 parameter; no cross_difficulty)
- late_tenure_base — parameter 3.00 / 4.00 / tier late_fee (= baseline); multi-source (tenure × late charges 12m) ✓.
- late_dishonour_addition — parameter 2.00/1.00/0 ✓. late_installment_size_addition — parameter 1.00/0.50/0 ✓.
- **late_lateness_scaling — labelled `method`, but its tiers select the multiplier 2 / 1.5 / 1 in the one expression `(late_base_charge + late_dishonour_add + late_size_add) * late_lateness_multiplier`.** The tiers only substitute a number into the same formula. **Finding F-2 (SOURCE-FACTOR RED, mislabelled effect).** With the label corrected the late-charge computation has 0 `method` factors (needs ≥1).

**catch-up** (5 factors; declared 1 method / 4 parameter; cross_difficulty: flood)
- **catch_acceleration — labelled `method`; its tiers select the count 2 / 1 / 0 in the single expression `catch_accelerated_count * (catch_next_installment + catch_accel_charge_each)`.** Same formula, different number. **Finding F-3 (SOURCE-FACTOR RED, mislabelled effect)**; with the label corrected the catch-up computation has 0 `method` factors.
- catch_accelerated_service_charge — parameter (0 / half / full plan service charge). Observation O-FL2: this factor only acts when catch_acceleration selects ≥1 installment; `baseline.rule` is silent about accelerated installments, so its `baseline` binding (the full plan service charge) is not a value `baseline.rule` states — it is the fall-through tier. Tiers collapse to one value on tiers whose plan service charge is 0.00 (Premier on monthly_eft, Premier Plus, Signature); checked per task.
- catch_prompt_credit — parameter 5.00/2.50/0 ✓. catch_card_service_charge — parameter installment_fee_card / installment_fee_eft / 0; tiers coincide where the tier's two fees are equal (Premier Plus, Signature: 0.00/0.00), checked per task. catch_flood_household_credit — parameter 3.00/1.00/0, cross_difficulty flood, multi-source (flood plan × flood payments 12m) ✓.

**cure** (5 factors; declared 1 method / 4 parameter; cross_difficulty: dwelling)
- **cure_late_charge_treatment — labelled `method`; its tiers select the share 0 / 0.5 / 1 in the single expression `cure_unpaid - cure_term_late_charges * (1 - cure_late_share)`.** Same formula, different number. **Finding F-4 (SOURCE-FACTOR RED, mislabelled effect)**; with the label corrected the cure computation has 0 `method` factors.
- cure_dishonour_deposit (1 / 0.5 / 0 installments), cure_landlord_credit (4.00/2.00/0; cross_difficulty dwelling; multi-source dwelling status × dwelling payments 12m), cure_lapse_length_charge (5.00/2.50/0), cure_tenure_credit (3.00/1.50/0) — parameters ✓.

**fee** (5 factors; declared 2 method / 3 parameter; cross_difficulty: dwelling)
- fee_cure_size_basis — method: 20% of cure / 25% of cure / flat tier fee (= baseline). Percentage-of-payment vs flat amount is a genuine change of algorithm ✓; multi-source (cure payment × tenure) ✓.
- **fee_lapse_age_scaling — labelled `method`; tiers select multiplier 0.5 / 1.5 / 1 in `fee_basis * fee_lapse_multiplier + …`.** **Finding F-5 (SOURCE-FACTOR RED, mislabelled effect).** Counts after relabel: 5 factors, 1 method, 4 parameter — bounds still met, but the mislabel itself stands.
- fee_late_charge_addition (4.00/2.00/0), fee_claim_record_addition (5.00/2.00/0; multi-source paid × reported), fee_landlord_relief (3.00/1.50/0; cross_difficulty dwelling) ✓.

Ladder realism (all policies): every ladder has ≥3 pairwise-disjoint tiers stated in the rule, distinct outcomes on the tiers of the two task worlds (see per-task), and conditions a personal-lines carrier plausibly weighs (tenure, returned payments, claims, companion policies, lapse length). The concept of "relief points" and "restart points" layered on a filed premium adjustment is unusual for an admitted insurer; recorded as observation O-FL3, not red — no specific tier outcome was found that no carrier would publish, beyond O-FL1.

Charter-level counts summary: stop ✓, restart ✓, late ✗ (0 honest method, F-2), catch-up ✗ (0 honest method, F-3), cure ✗ (0 honest method, F-4), fee ✓ counts but F-5 mislabel.

### findings

- **F-1 SOURCE-POLICY RED — undeclared override of the late-fee amount.** Symptom: `renters_ext_late_charge` computes a late charge other than the tier's `late_fee` with `overwrite: []`. Root cause: the base section fixes a late fee's amount at the tier parameter (`parameter_schema.late_fee` "Late fee per late installment"; fees_and_waivers "a fee whose tier amount is 0.00 is not charged at all"), and the extension handles that quantity differently without naming the base clause, unlike `renters_ext_reinstatement_fee`, which declared its analogous clause. Evidence: extended.yaml lines 1889–2023 (`overwrite: []`, rule, `baseline.rule` "The late charge is the tier's late_fee"); renters.yaml parameter_schema and renters_fees_and_waivers rule. Bears on **task 0** (demonstration there).
- **F-2 SOURCE-FACTOR RED — late_lateness_scaling mislabelled `method`** (multiplier 2/1.5/1). Late computation left with no honest method factor. Bears on **task 0**.
- **F-3 SOURCE-FACTOR RED — catch_acceleration mislabelled `method`** (count 2/1/0). Catch-up computation left with no honest method factor. Bears on **task 0**.
- **F-4 SOURCE-FACTOR RED — cure_late_charge_treatment mislabelled `method`** (share 0/0.5/1). Cure computation left with no honest method factor. Bears on **task 1**.
- **F-5 SOURCE-FACTOR RED — fee_lapse_age_scaling mislabelled `method`** (multiplier 0.5/1.5/1). Bears on **task 1** (counts still met via fee_cure_size_basis).
- Observations: O-RC1..O-RC5, O-AB1 (task 1), O-PG1, O-PG2 (task 1), O-PS1, O-OV2, O-OV3, O-FL1, O-FL2 (task 0), O-FL3 — as described above; none demonstrated as a consequence in either task world at this stage.

## closing_checklist

Written after both reveals (2026-09-24T23:52Z); everything above this heading was on disk before any reveal (sha256 of this file at that point: `61114038…4426`).

**Status: NOT CLOSED — the difficulty does not pass the source-layer audit.** Task 0: SOURCE-POLICY RED + SOURCE-FACTOR RED; task 1: SOURCE-FACTOR RED. In both tasks the independent blind derivation matched GT on every scored value, write, owner and order, and the problem tree held.

- Per-task files `0.md`, `1.md` correspond one-to-one with `tasks/0.json`, `tasks/1.json`; this is revision 0 (no earlier revision). Comparison sections: task 0 RED, task 1 RED — not all PASS.
- Coverage and scope: `charter_scope` of task 0 = {stop, restart, late, catch-up}, task 1 = {cure, fee}; pairwise disjoint and jointly covering all six extended policies — matches the pre-reveal scan. Task tools and GT closed (every GT write targets a tool of its own scope). UUID8s independent (§action_binding_and_uuids). ✓
- Trees: task 0 has 3 prerequisite problems with 3 value_input edges; task 1 has 1 with 1 value_input edge; each has an owner=user write (catch-up; cure); the difficulty's edge set is a DAG with no cross-task reference. ✓
- Computations: every computation declares a self-sufficient baseline, and every factor bears weight on its task's world against an honest baseline (all substitutions recomputed and matched to GT except the stop courtesy counterfactual, 9.23 recomputed vs 9.22 stated — F-T0-3). ✗ — late (F-2), catch-up (F-3) and cure (F-4) have no honest `method` factor; `fee_lapse_age_scaling` is mislabelled (F-5); F-1 undeclared late-fee override.
- Instantiation-stage gates on the final form: not re-run, because the difficulty does not close in this round; the brief's snapshot (all 7 gates green, check_traceability deferred) is the one on record.

---

## revision_2

Re-audit, round 2. Everything above this line is revision_1 (round 1) and is left as written. This revision was built from the reworked charter and tool module alone, before any round-2 task GT was revealed; nothing in it is derived from a revealed round-2 GT.

### charter_global_frozen (revision_2)

- Hashes (re-verified with sha256sum): `renters.extended.yaml` `f5981746b36301110e6be87188909df7ad151ea98e956b8500d1c689d42c0f39` (was `97c7e091…cdb6`); `task_tools.py` `0f175425792a7de1f6c3be5f750e9a9cc71af24acc5c9c936de45328df8eed48` (was `bd6e72d7…9ac9`). **Both shared inputs changed, so every charter-global section is re-derived in full below, not carried forward.**
- Views: `0.view.json` `6b53d21e…0b8a` (unchanged), `1.view.json` `bc6b76e7…de8c` (changed). Gate snapshot supplied by the orchestrator: all 7 gates green, check_traceability still deferred. Entry conditions complete.
- Freeze time 2026-09-25T00:03Z (clock-checked). Auditor: the same independent audit agent as round 1 (not the reworker). Reworker's closure claims were taken as pointers only; each is checked against the artifacts below.
- Read domain this round: blueprint (unchanged), the extended charter, `task_tools.py`, the two views. No task JSON, worklog, scratchpad file other than the views, or `skills/` file was read before the freeze.
- Base section: lines 1–1419 of the extended charter are still byte-identical to `blueprint/products/renters.yaml`.

### policy_conflict_scan (revision_2)

Same six policies, targets, owners, subjects and prerequisite graph as revision_1 (restart ← stop, catch-up ← restart, catch-up ← late, fee ← cure). Overlap conclusions re-checked and unchanged: the two halves of bundle_discount s3 are superseded by the stop and restart policies for disjoint events; the catch-up applies only to a policy in force and the cure only to a cancelled one; the restart reads the stop's restated premium through the declared edge. Cross-category reads declared = the reads compute actually makes (umbrella/valuables/flood for stop, valuables/umbrella/flood for restart, flood for catch-up, dwelling for cure and fee). Scopes derived from the trees: task 0 {stop, restart, late, catch-up}, task 1 {cure, fee}. These are disjoint and together cover all six policies. PASS.

### rule_compute_equivalence (revision_2)

Swept again from compute to basis and from rule to compute. Changes and where the revision_1 observations stand now:

- O-RC1 → **closed.** The rule now says "When more than one qualifying policy ended during the renters term, the ending qualifying policy is the one with the latest closed date." Compute `stop_ended_date = max(stop_umb_closed, stop_val_closed)`, and reason/bound date follow the chosen policy. Still an imprecision (observation O2-RC1): within one category, the compute prefers a cancelled row over an expired one without comparing their dates, and it does not filter to "during the renters term". Neither shape exists in either task world.
- O-RC2 → **closed.** Rule: "the installment service charge billed with that same installment". Compute filters the installment fee by `term_effective_date` and `installment_number=late_overdue_number`.
- O-RC3 → **closed.** Rule: "the installment of the current term with the latest due date already past among the installments billed". Compute takes the latest number, stepping back one when its due date is not yet past, within the current term.
- O-RC4 → unchanged, consistent (unfiltered sums, as the rule says).
- O-RC5 → the rule now states the reverse division explicitly ("is not rebuilt from the contents, liability and co-insured charges; a current annual premium held at minimum_annual_premium is divided the same way"). Rule and compute agree. The base-vs-extended aspect moves to override_declarations O2-OV2.
- New sentences all have a verbatim basis and are implemented: the late charge's "An installment whose payment was returned unpaid is unpaid from its due date, the returned payment counting as never received"; the late lateness method (`late_method_charge`); the catch-up's collection ahead of billing (`catch_unbilled_premium`, `catch_next_collected`, `catch_ahead_amount`) and service-charge relief (`catch_early_relief`); the cure's none / latest / all selection (`cure_latest_late_charge`, `cure_late_collected`, `result`); restart start-date tier 2 (`MN(DAYS(eff, exp) + 7, term_days)` = "from early_start_days calendar days before its effective date … never from a day before the renters effective date").

No compute binding invents a basis, and no rule sentence is left unimplemented. PASS (with observations).

### action_binding_and_uuids (revision_2)

- Six tools, one per policy; `(target_tool, computes)` still unique. UUID8s unchanged (d8b9b7f1, e779526e, 664a192e, 50a8e701, 5468a22a, e7e59896): independent. PASS.
- Tool bodies: the only conditional is still `if fee > 0` in `reinstate_lapsed_policy_e7e59896`, which records no fee entry for 0.00. There is no validation, no raise and no hint path, so the tools still judge no prerequisite.
- O-AB1 → **closed.** The cure tool's docstring now reads "Pay an amount on your own cancelled RentGuard renters policy … nothing else on the policy changes". The purpose clause relating the payment to reinstatement is gone. A grep over all six docstrings finds no sequence word other than "The caller can afterwards see …", which describes the call's own result.

### prerequisite_graph (revision_2)

| blocked | problem | kind / gate | form | verbatim in own rule | absent from depended rule | resolved_by = target |
|---|---|---|---|---|---|---|
| restart | stop | value_input / restart_old_premium | state | ✓ | ✓ | ✓ |
| catch-up | restart | value_input / catch_balance | state | ✓ | ✓ | ✓ |
| catch-up | late | value_input / catch_balance | state | ✓ | ✓ | ✓ |
| fee | cure | value_input / fee_cure_payment | state | ✓ | ✓ | ✓ |

The graph has no cycles, no fallback_reason (all edges are state form), no authoring-viewpoint phrasing, and every gate binding exists in compute.
- O-PG1 → **closed.** The restart ← stop condition no longer carries the extra term_premium clause and now matches the sentence.
- O-PG2 → **closed.** The fee ← cure condition now reads "whose amount is at least the cure amount", matching "covers".
- The catch-up ← restart condition was rewritten; see prerequisite_sentences.

### prerequisite_sentences (revision_2)

1. restart ← stop: sentence unchanged. It passes the four-point test, and exactly one write (the stop charge) brings its state about. Single reading ✓.
2. catch-up ← restart: now "The catch-up amount is fixed only after the premium account carries a multi-policy discount change credit dated the effective date of every qualifying policy that took effect during the renters term while the renters premium carried no multi-policy discount." It passes: the connective is "only after", it is state form, it names no tool or id, and exactly one write (the restart credit) brings the state about.
   - **O-PS1 → closed** as a blocking defect: a qualifying policy that takes effect while the discount is still carried no longer demands a credit that no write can produce.
   - New observation O2-PS1: the sentence qualifies by "while the renters premium carried no multi-policy discount", but the condition says "at a time when no umbrella or valuables policy of the customer was live". Read against the recorded premium, a floater that took effect after the umbrella ended but before any stop charge was posted took effect while the record still carried the discount. On that reading no credit would be required, and the restart rule (same wording, present tense) would never fire. That reading leaves a customer who holds a live floater without the bundle discount. The base bundle rule's first sentence, which is not superseded ("multi_policy_discount_pct applies to every live renters policy of a customer who also holds a live … Floater"), forbids that outcome. So the entitlement reading, which is the condition's reading, is the only one consistent with the charter. The same wording was accepted in revision_1 for the restart trigger.
3. catch-up ← late: sentence unchanged. It passes, and now rests on the late rule's explicit "unpaid" sentence for returned payments. Single reading ✓.
4. fee ← cure: sentence unchanged. It passes, and the catch-up rule is still excluded on a cancelled policy. Single reading ✓.

No rule names a tool or policy id (programmatic check). No depended-on rule restates a sentence. The cure rule's "charged at reinstatement" is still a rationale, not an ordering connective. No undeclared cross-problem order found. PASS.

### override_declarations (revision_2)

- **late — F-1 closed.** `overwrite` now names fees_and_waivers s4 ("The returned-payment fee is charged once per returned payment, referencing that return, and the reinstatement fee once per reinstatement; a fee whose tier amount is 0.00 is not charged at all.") and replaces it with the same sentence plus "a late fee is charged at the late charge worked out below instead of at the tier's late_fee alone". The replacement is a sentence of the rule. The late-fee amount now has one governing clause. The new "unpaid from its due date" sentence restates what base payment_application s2 already entails ("A returned payment reverses the one payment entry it references in full"); it is not a further override. Other fees_and_waivers sentences are followed.
- stop, restart: declarations as in revision_1 (midterm s6 and bundle s3 for both; premium_rating's discount sentence for restart). Observation **O2-OV2** (was O-OV2): the stop and restart rules now state outright that the pre-discount premium "is not rebuilt from the contents, liability and co-insured charges; a current annual premium held at minimum_annual_premium is divided the same way". That is a stated departure from base premium_rating s2–s4 (subtotal rebuilt from components, reduced, floored). It is named in neither policy's `overwrite`; restart's premium_rating entry covers only the discount-percentage sentence. It is a latent undeclared override: the two methods diverge only when the current premium sits on the minimum floor or rounding moves it away from subtotal × (1 − d). It cannot be demonstrated on either task world (task 0: both give 263.60), so under the core-constraints threshold it stays an observation.
- catch-up: `overwrite: []`. No base sentence fixes a catch-up amount. Observation O2-OV3 (was O-OV3): the rule now says whatever the payment carries beyond the balance "stays on the account as a credit". The "card service charge on the catch-up" is therefore collected and then carried as a credit rather than posted as a fee. It is internally consistent now, but it is a charge in name only.
- cure, fee: declarations unchanged and sufficient. PASS.

### factor_ladders (revision_2)

Factor counts from the charter: stop 6 (2 method / 4 parameter; flood), restart 6 (2 / 4; flood), late 4 (1 / 3), catch-up 5 (1 / 4; flood), cure 5 (1 / 4; dwelling), fee 5 (1 / 4; dwelling). Every ladder has 3 tiers, each stated in the rule and implemented in compute.

- **F-2 → closed.** `late_lateness_method` (was `late_lateness_scaling`). Its tiers now select how the charge is built: more than 30 days, 25 % of the overdue installment's unpaid part *in place of* the flat base; 12–30 days, flat base with additions *plus* 10 % of the unpaid part; fewer than 12 days, the flat base with additions (= baseline `late_flat_charge`). Percentage-of-balance, combined and flat are different algorithms, so the `method` label is honest. Late now has 1 honest method and 3 parameters. Observation O2-FL4: a 25 % late charge is high for a personal-lines installment, though percentage late charges are an industry form.
- **F-3 → closed.** `catch_ahead_of_billing` (was `catch_acceleration`). Its tiers now compute different quantities: two or more returns, the term's whole unbilled premium (annual premium less every installment billed, floored at 0); one return plus a late charge, the next installment at the latest billed amount plus the plan service charge; otherwise nothing (= baseline). This is an honest `method`, and collecting the unbilled balance after repeated NSF is a real carrier practice.
- **O-FL2 → closed.** `catch_early_service_charge_relief` now takes a relief *off* (whole / half / nothing waived), and its fall-through and baseline are "nothing waived" = 0. This is what `baseline.rule` gives, since nothing is collected early under the baseline.
- **F-4 → closed.** `cure_late_charge_treatment` tiers now select which charges are collected with the cure: none (`0`); only the latest late charge of the term (`LATEST(... late_fee ...)`); every late charge of the term (`SUM(...)` = baseline). Choosing none, the most recent single entry, or the full sum is a different selection/aggregation rule per tier, not one number substituted into a fixed expression, so the `method` label is accepted. With only one late charge, "latest" and "all" coincide, but the ladder routes that case to tier 1, so the tiers stay distinct in outcome.
- **F-5 → closed.** `fee_lapse_age_scaling` is relabelled `parameter` (multiplier 0.5 / 1.5 / 1). The fee keeps `fee_cure_size_basis` as its method: 5 factors, 1 method, 4 parameter.
- **O-FL1 → closed.** Restart start-date tier 2 now credits "from early_start_days calendar days before its effective date … never from a day before the renters effective date". There is no longer any credit for days beyond the renters expiration.
- Stop parameter change: `flood_relief_full_pct` 25 → 20. The ladder is still 20 / 10 / 0, distinct.
- Unchanged from revision_1: O-FL3 (relief/points layered on filed premium adjustments; observation). Card-service-charge tiers still collapse on Premier Plus and Signature (0.00 / 0.00); no task sits on those tiers.

Charter-level counts summary: every computation now has 4–6 factors with at least 2 parameter and at least 1 honest method. Cross-difficulty factors: flood in stop, restart and catch-up; dwelling in cure and fee.

### findings (revision_2)

- Round-1 charter findings: **F-1 closed, F-2 closed, F-3 closed, F-4 closed, F-5 closed** (evidence above).
- Round-1 observations: O-RC1, O-RC2, O-RC3, O-AB1, O-PG1, O-PG2, O-PS1, O-FL1 and O-FL2 closed. O-RC5/O-OV2 moved into the rule text and remain a latent undeclared override (O2-OV2, observation). O-OV3 is reworded (O2-OV3, observation). O-RC4 and O-FL3 are unchanged, as claimed.
- New this round (all observations; none demonstrable on either task world): O2-RC1, O2-PS1, O2-OV2, O2-OV3, O2-FL4.
- No new SOURCE-* red at the charter level.

## closing_checklist (revision_2)

Written after the round-2 reveals (2026-09-25T00:04Z). Everything in §revision_2 above this heading was on disk before the reveal (sha256 `3f825b26…c09f`).

**Status: CLOSED. The difficulty passes the source-layer audit in revision_2.**

- **Per-task files.** `0.md` and `1.md` correspond one to one with the tasks, and `_difficulty.md` sits alongside them. Each file keeps revision_1 untouched and appends revision_2. Both revision_2 comparison sections carry PASS.
- **Coverage.** Task 0 covers {stop, restart, late, catch-up} and task 1 covers {cure, fee}. The scopes are disjoint and together cover all six extended policies. The task tools and GT are closed. All uuid8s are independent and frozen.
- **Problem trees.** Task 0 has 3 prerequisite problems with 3 value_input edges; task 1 has 1 with 1. Each tree includes an owner=user write (the catch-up in task 0, the cure in task 1). The whole difficulty's edges form a graph with no cycles.
- **Factors.** Every computation declares a baseline that works on its own and 4–6 factors with at least 2 parameter and at least 1 honest method. Each task has at least one multi-source factor and at least one cross-difficulty factor (flood in task 0, dwelling in task 1), and the rows those factors read are seeded. Every ladder has 3 tiers stated in the rule, with distinct outcomes. Every factor bears weight against an honest baseline, and the baseline alone gives a definite number different from gold. All figures were recomputed exactly and match GT.
- **Round-1 reds.** F-1/F-T0-1, F-2, F-3 (with O-FL2), F-4/F-T1-1, F-5/F-T1-2 and F-T0-3 are all closed.
- **Remaining observations (not grounds for rework).**
  - O2-OV2: latent undeclared departure from premium_rating via reverse division; it has no consequence on either world.
  - O2-RC1: within-category precedence when several qualifying policies ended.
  - O2-PS1: "carried no discount" read by entitlement, not by the recorded premium.
  - O2-OV3: the card service charge is carried as a credit.
  - O2-FL4: the 25 % late-charge tier is high.
  - O2-T0-1: the evaluator's tie rounding was worked around, not fixed.
  - O-RC4 and O-FL3: unchanged, as the reworker claimed.
- **Instantiation-stage gates on the final form.** I did not re-run the gates; that is outside this auditor's command domain this round. The orchestrator's post-rework snapshot (all 7 green, check_traceability deferred until the KB is published) is the gate record for the final form.
- **Correction note on revision_1 timestamps.** The "Freeze time" labels written in revision_1 (23:45Z, 23:50Z, 23:55Z) were estimates, not clock readings. The clock-checked record of that round is:
  - sha256 of all three files taken at 2026-09-24T23:48:22Z;
  - the round-1 GT first opened after that, at the reveal step (23:48:50Z clock check).
  
  So the freeze preceded the reveal, as required. The revision_1 text itself is left unchanged.
