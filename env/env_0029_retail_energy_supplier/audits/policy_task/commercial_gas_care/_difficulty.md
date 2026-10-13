# Policy-task audit — commercial_gas_care / charter-global

## charter_global_frozen

- Round: 1 (no earlier revision exists; the `audits/policy_task/commercial_gas_care/` directory was empty before this run).
- Freeze time: 2026-10-04T16:19:10Z (file mtime of the charter-global write). Auditor: independent policy-task auditor (erl-task-policy-audit), not the author of the artifacts.
- Freeze hashes (sha256):
  - `tasks/commercial_gas_care/bizgas.extended.yaml` 11e1d2c605baf2b799004b9c6b66a2d49904c9c01c13c8d9a355d7b024a5b94c (matches HASHES.txt)
  - `tasks/commercial_gas_care/task_tools.py` 190979d7c78dd5330a82edae5d7f285f118e8bf2a2d56be6bf5338e1bf1175cb (matches HASHES.txt)
  - `blueprint/products/bizgas.yaml` 35b6287ccff4d79d8963ee0913f49c945df3c4786702f0d4f887bc7e25a5dd31
- Read for this section: `blueprint/products/bizgas.yaml`, `blueprint/blueprint.yaml` (difficulty claims only), `blueprint/share_tools.py` (signatures), `bizgas.extended.yaml` in full, `task_tools.py` in full, `skills/erl-task-instantiate/scripts/check_compute.py` (DSL semantics of `within_months`, `MONTHS`, `DAYS`, `LATEST`, `CFIELD`, `XSUM`, `XCOUNT`, `RND`).
- Masked and not read: `tasks/commercial_gas_care/tasks/*.json` (every field), every worklog, `.audit_views` of other difficulties. Nothing in this section is derived from a revealed GT; it was written before any task's GT was opened.

### Entry conditions (Step 0)
The brief supplied: the gate snapshot (check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cache_diff INFO; check_cross_fire SCOPE OK; check_traceability deferred until the KB is rendered), the masked views with hashes (`.audit_views/policy_task/commercial_gas_care/HASHES.txt`; recomputed sha256 of task_0.view.json 96cbe09f… and task_1.view.json 3d39772f… match). Entry conditions complete. check_traceability is deferred by design; recorded, not a defect of this audit.

### policy_conflict_scan

Base section: a mechanical comparison of every top-level key of `bizgas.extended.yaml` other than `extended_policies` against `blueprint/products/bizgas.yaml` gives equality on category, display_name, binding, lifecycle, accounts, parameter_schema, variants, events, measures, policies — the base copy is verbatim.

Extended policies (4): `bizgas_ext_swing_excess_rebill` (bizgas_adjustment, target `post_bizgas_swing_rebill_d99acf60`, owner agent), `bizgas_ext_renewal_loyalty_credit` (bizgas_renew + bizgas_credit, target `accept_bizgas_renewal_offer_c0a82e44`, owner user), `bizgas_ext_swing_shortfall_rebill` (bizgas_adjustment, target `post_bizgas_shortfall_rebill_b4d87cc1`, owner agent), `bizgas_ext_lapsed_renewal_price` (bizgas_renew, target `accept_bizgas_lapsed_renewal_f259b0f9`, owner user).

Overlapping subjects and how they separate:
- Two rebill policies share subject `bizgas_adjustment` and `computes: rebill_amount_usd`; they separate by object (the most recently posted `swing_excess_charge` line vs the most recently posted `swing_shortfall_charge` line) and by target tool. Compatible.
- Two renewal policies share `bizgas_renew`; they separate by time anchor: loyalty credit "accepts the renewal offer ... on or before its contract_end_date"; lapsed price "after its commercial gas agreement has rolled over to the monthly index plan and within the post-expiry grace period". Disjoint (an agreement that has rolled over has an empty contract_end_date). Compatible.
- Base sentence `bizgas_renewal` "Each renewal earns one renewal_loyalty_credit equal to the renewal_loyalty_credit_usd of the plan renewed into." is superseded twice (loyalty: "The base credit is the renewal_loyalty_credit_usd of the plan in force on the acceptance date."; lapsed: "A renewal accepted after the agreement has rolled over earns no renewal loyalty credit."). The two replacements govern the two disjoint time anchors above, so the merged semantics are unique (observation O-G6).
- Base `bizgas_swing` band sentence is superseded by both rebill policies (excess: upper end by tolerance tier; shortfall: lower end lowered for seasoned sites). Each replacement speaks of a different end; no common quantity. Compatible (observation O-G7 on the merged billing text).
- Base `bizgas_billing_correction` amount clause "equal to the billed amount_usd minus the correctly computed amount and posted as a negative amount" is superseded by both rebill policies (plus interest / plus service recovery credit); separated by line type. Compatible.
- Cross-category read boundary: all four read `bizpower` (status/term of the agreement on the same premise; bizpower_billing energy lines). `bizpower` belongs to difficulty `small_business_electricity_care` (blueprint.yaml), so these reads are cross-difficulty; read-only, no write outside bizgas.

Scope: the four extended policies pair into two problem trees by their declared edges — {renewal_loyalty_credit ← swing_excess_rebill} and {lapsed_renewal_price ← swing_shortfall_rebill}. With M=2 the two trees are pairwise disjoint and jointly cover all four extended policies. (Which task claims which tree is verified per task after the reveal.)

### rule_compute_equivalence

DSL semantics used (check_compute.py): `within_months=N` keeps a row when `0 <= MONTHS(row_date, NOW) < N` — equivalent to "later than the same calendar day N months before" today; `MONTHS(a,b)` counts whole months, minus one when b's day < a's day — equivalent to "a month counting only once the day of month has been reached"; `DAYS(a,b)` = b − a in days; `LATEST` picks the max `date_field`; `CFIELD` reads the customer's other-category holding filtered by premise_id; `XSUM`/`XCOUNT` read the customer's other-category ledger; `RND` is Python `round` (not decimal half-up) — no value derived in this audit lands on a binary half-cent edge that flips (checked per task).

`bizgas_ext_swing_excess_rebill` — every binding has a verbatim `compute_basis`; sweep back:
- object: "most recently posted swing_excess_charge line, read together with the energy_charge line of the same billing_period_start" ↔ `LATEST(...posted_date, line_type='swing_excess_charge')`, `SUM(usage_therms, energy_charge, billing_period_start=excess_cycle_start)`. ✓
- monthly volume half-up ↔ `int(x/12+0.5)`. ✓ Upper end half-up ↔ `int(v*(100+tol)/100+0.5)`. ✓ measured excess never below zero ↔ `MX(0, …)`. ✓
- tolerance ladder (36 / 24 energy lines on file, "at most one swing_excess_charge line whose billing_period_start is later than the same calendar day twelve months before the correction date") ↔ `swing_tolerance` with `within_months=12, date_field='billing_period_start'`; tier 2 carries the "fewer than established_cycles" bound explicitly. ✓
- relief ladder (≤ 10 % half rounded down; ≤ 20 % ×0.75 rounded up; else as measured) ↔ `int(m/2)`, `-int(-m*0.75)`, `m`. ✓
- adder ladder ↔ `CFIELD('bizpower','status'/'term_months', premise_id=F('premise_id'))`. ✓
- price "index_price_usd_therm of the monthly_index_price notice whose effective_date equals the cycle's billing_period_start" ↔ `LATEST(... effective_date=excess_cycle_start)`. ✓ (but see O-G2 against base index pricing.)
- amount half-up to cent; over-billed never below zero ↔ `RND`, `MX(0, RND(...))`. ✓
- interest rate ladder (≥2 / 1 / 0 rebill_credit lines "posted ... later than the same calendar day twenty-four months before") ↔ `COUNT(within_months=24, date_field='posted_date', line_type='rebill_credit')`. ✓
- anchor ladder (notice dated after billing_period_start and mail → start; email → end; else posted_date) ↔ `interest_months`. ✓ Interest rounded, added once ↔ `overcharge_interest`, `result`. ✓
No compute binding without a rule sentence; no rule sentence without a binding (the "dated on the correction date" and "tied through source_billing_id" sentences are tool arguments, not computed values). PASS.

`bizgas_ext_renewal_loyalty_credit`:
- base credit "plan in force on the acceptance date" ↔ `P('renewal_loyalty_credit_usd')` (the holding's current variant). ✓
- carry ladder ↔ `carried_base_credit` (else-branch = phone/web; `enrollment_channels` enum is phone|web|broker). ✓
- spend window ladder (≥24 energy lines: half 24-month sum, half-up; <12: 12-month sum ×12 / lines, half-up; else 12-month sum), "every bill line of the agreement, credits and rebill credits included, posted later than the same calendar day … months before the acceptance date" ↔ `SUM('bizgas_billing','amount_usd', within_months=…, date_field='posted_date')` with no line filter. ✓
- spend multiplier, tenure (MONTHS from service_start_date), bundle bonus (CFIELD status + XCOUNT bizpower energy lines by billing_period_start, 12 months), early bonus (DAYS(NOW, contract_end_date) ≥21 / ≥1 / 0), bonuses added after the multiplier, single rounding at the end ↔ the corresponding bindings and `result`. ✓ PASS.

`bizgas_ext_swing_shortfall_rebill`:
- object, cycle usage, billed lower end = usage + shortfall therms ↔ bindings. ✓
- seasoned lowering (≥24 lines and a loyalty line → 10 % of monthly volume; ≥24 and none → 5 %; else none; reduction half-up) ↔ `lowered_lower_end`. ✓
- cycle-length fit (days inclusive; <28 → ×days/30; >32 → ×days×12/365; else unchanged; half-up) ↔ `shortfall_cycle_days`, `fitted_lower_end`. ✓
- deadband (≥36 → 100; ≥24 → 50; else 0) taken off, never below zero ↔ `shortfall_deadband`, `correct_shortfall_therms`. ✓
- rate ladder (bizpower agreement active and the business's bizpower energy lines with billing_period_start in the last 12 months sum ≥ 15000 → 0.0300; active and less → 0.0450; else the line's rate) ↔ `XSUM(... within_months=12, date_field='billing_period_start', line_type='energy_charge')`. ✓
- service recovery credit (≥2 → 25.00; 1 → 10.00; 0 → none) ↔ `service_recovery_credit`; result ↔ `RND(over + credit, 2)`. ✓ PASS.

`bizgas_ext_lapsed_renewal_price`:
- offer selection ladder ↔ `offer_price` (`DAYS(final_date, final_end) < 30`; `60 <= DAYS(initial_date, initial_end) <= 90`; MN of both). ✓ "of the expired term" ↔ `LATEST` by notice_date of each notice type. ✓
- uplift (DAYS(plan_change_date, NOW) ≥11 / ≥6 / else) ✓; bundle discount (status active and term ≥24 / active and shorter / none) ✓; recovery discount (≥2 / 1 / 0 rebill_credit lines posted later than 24 months before) ✓; volume discount (energy therms with billing_period_start in the last 12 months ≥30000 / ≥15000 / else) ✓; result rounded to 4 places once ✓. PASS.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: (post_bizgas_swing_rebill_d99acf60, rebill_amount_usd), (accept_bizgas_renewal_offer_c0a82e44, loyalty_credit_usd), (post_bizgas_shortfall_rebill_b4d87cc1, rebill_amount_usd), (accept_bizgas_lapsed_renewal_f259b0f9, contract_rate_usd_therm) — each claimed by exactly one policy. ✓
- Docstrings: each describes one atomic write on one object; none names another tool, none places itself in a sequence, none carries before/after/first relative to another action ("Afterwards the agreement shows …" in both accept tools describes the tool's own effect, not a sequence). No confirmation, review or wait is added. ✓
- Function bodies: every tool performs `ctx.update`/`ctx.create` unconditionally — no status check, no prerequisite check, no amount computed (amounts booked as given). The tool layer judges no prerequisite. ✓
- uuid8 tails: d99acf60, c0a82e44, b4d87cc1, f259b0f9 — no shared prefix, no sequence, no adjacent values, no reuse across tools. ✓ PASS.

### prerequisite_graph

- `prerequisite` filled on all four: excess `[]`, shortfall `[]`, loyalty one edge → `bizgas_ext_swing_excess_rebill`, lapsed one edge → `bizgas_ext_swing_shortfall_rebill`. Both point at extended ids in this file, neither at itself nor at a base policy; graph has two disjoint two-node chains — acyclic. ✓
- `policy_source` verbatim in the blocked policy's own rule: checked mechanically (substring test) — both True. ✓
- `form: state` on both, no `fallback_reason` on either (none required). ✓
- `kind: value_input`; `gate: spend_24m` exists in the loyalty compute; `gate: rebills_last_24m` exists in the lapsed compute. ✓ The loyalty edge's effect names both spend sums; `spend_24m` and `spend_12m` both carry the credit (via `credit_spend_measure`). ✓
- `resolved_by` = the depended-on policy's `target_tool` on both edges. ✓ Whether resolved_by makes `condition` hold: see finding F-G1 (both edges' `condition` quantify over "Every swing_excess_charge / swing_shortfall_charge line of the agreement …", while the depended-on rule only ever corrects the most recently posted line).
- No authoring-viewpoint phrasing ("in this task", "at the opening") in either edge. ✓

### prerequisite_sentences

Edge E1 (loyalty ← excess). Sentence: "The renewal loyalty credit is fixed only after every swing excess line on the agreement that was billed above what the swing rules allow carries its own rebill credit."
- Ordering connective: "only after". ✓ Waited-on state: a swing excess line "carries its own rebill credit" — record-visible (a `rebill_credit` row whose `source_billing_id` is the swing excess line). ✓ No tool name, no policy id, no snake_case, no row id. ✓
- Exactly one write of this difficulty brings about "a swing excess line carries its own rebill credit": `post_bizgas_swing_rebill_d99acf60` (the shortfall tool's docstring and its policy address swing shortfall lines only). ✓
- Derivation a reader performs: sentence → "rebill credit on a swing excess line billed above what the swing rules allow" → the only policy whose rule works a rebill_credit on a swing excess line and states what the swing rules allow is `bizgas_ext_swing_excess_rebill` → its rule computes the over-billed amount on "the agreement's most recently posted swing_excess_charge line" → post that credit. Single resolving action.
- Strength/scope: the sentence (and the `condition`) quantify over **every** swing excess line "billed above what the swing rules allow"; the resolving rule only works the most recently posted line, and base `bizgas_billing_correction` bars correcting a line more than 12 months after posting. See F-G1.
- The rule carries no second wording of the dependency; the excess rule does not restate it. ✓

Edge E2 (lapsed ← shortfall). Sentence: "The renewed price is not fixed until every swing shortfall line on the agreement that was billed above what the shortfall rules allow carries its own rebill credit."
- "not … until" ✓; state form, record-visible ✓; no tool/id/snake_case ✓; exactly one write (`post_bizgas_shortfall_rebill_b4d87cc1`) ✓; derivation analogous to E1 via `bizgas_ext_swing_shortfall_rebill` ("most recently posted swing_shortfall_charge line"). Same scope issue: F-G1.

Undeclared cross-problem orders: no other sentence of the four extended rules orders one problem against another. Base rules state orders only inside one problem's lifecycle (e.g. `bizgas_cancellation` "re-enrolls the site after the drop"); none grounds an edge of either tree. ✓

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry (finding half only).

`bizgas_ext_swing_excess_rebill` vs
- `bizgas_billing_correction`: S1 amount clause — superseded, declared. S1 tail "a corrected energy, swing or fee line also corrects the cycle's sales_tax line with its own rebill credit" — not superseded, inherited (no extended policy computes the tax companion). S2/S3 lookback, S4 once per line, S5 agent limit 250.00, S6 no back-billing — inherited, followed. S2 is worded "only when the business disputes it" (O-G4).
- `bizgas_swing`: S1 monthly volume — followed. S2 band — superseded, declared. S3 inside-band billed at fixed price — not contradicted (the rule corrects only the excess line; the energy-line under-billing the wider band implies is barred by inherited `bizgas_billing_correction` S6). S4 excess pricing — superseded, declared (with relief). S5/S6 — not touched.
- `bizgas_index_pricing`: S2 "A billing cycle is priced with the notice for the calendar month containing its billing_period_start" vs extended "the monthly_index_price notice whose effective_date equals the cycle's billing_period_start" — differs for cycles not starting on the 1st; not named in `overwrite` (O-G2, an anonymous-intermediate deviation; whether it bites is a per-task question).
- `bizgas_agg_portfolio_bandwidth` is not among the refs although it governs whether any swing is billed on a portfolio plan (Fixed 24/36, Carbon Neutral 24) (O-G3; bites only where the business has more than one portfolio-plan site).
- Disguised forms: no 0/1 multiplier; no dropped branch (every base branch of S2/S4 reappears as a ladder tier or the fall-through).

`bizgas_ext_renewal_loyalty_credit` vs `bizgas_renewal`: S1 (plan, term, price, annual therms reset) followed; S2 active-only followed; S3 start the day after contract_end_date followed; S4/S5 grace not engaged (on-time scope); S6 credit — superseded, declared. The credit-size ladders replace S6 in full; no undeclared conflict.

`bizgas_ext_swing_shortfall_rebill` vs `bizgas_billing_correction`: as above (amount clause declared; tax companion inherited). vs `bizgas_swing`: S2 band — declared (replaced_by covers only the seasoned lowering; the cycle-length fit and deadband, which also move the shortfall therms, appear only in the rule, not in any `replaced_by` — O-G5); S5 shortfall rate — declared.

`bizgas_ext_lapsed_renewal_price` vs `bizgas_renewal`: S1 price — declared; S3 "after a rollover it starts on the acceptance date" followed; S4/S5 grace followed; S6 credit — declared (none). vs `bizgas_expiry_notices`: "when the two notices differ, the final_options_notice governs" — declared; the replacement is worded about "the renewed price" of a lapsed renewal, so after the merge no sentence states which notice governs an on-time renewal when the two differ (O-G1; per-task consequence checked in task 0). vs `bizgas_rollover_terms`: not contradicted.

No undeclared override found whose consequence is demonstrable charter-wide; per-task consequences of O-G1..O-G4 are checked in each task file.

### factor_ladders

`bizgas_ext_swing_excess_rebill` (baseline: tolerance = swing_tolerance_pct, correct excess = measured excess, adder = swing_excess_adder_usd_therm, no interest named → "any overcharge interest due" read as none):
| factor | label | decides | tiers | distinct outcomes | multi-source | cross-difficulty |
|---|---|---|---|---|---|---|
| swing_band_tolerance | parameter | swing_tolerance | 3 | +10 / +5 / +0 | yes — energy-line count AND excess-line count (two row sets) on both non-fall-through tiers | no |
| excess_bundle_adder | parameter | excess_adder | 3 | 0.0200 / 0.0300 / 0.0400 | no — status and term of one bizpower row | bizpower |
| excursion_relief | method | correct_excess_therms | 3 | halve+floor / ×0.75+ceil / identity | no | no |
| repeat_overcharge_interest_rate | parameter | monthly_interest_rate | 3 | 0.0100 / 0.0050 / 0 | no | no |
| interest_anchor | method | interest_months | 3 | start / end / posted_date anchor | no — date and channel of one notice row | no |
Counts: 5 factors; 3 parameter, 2 method; 1 multi-source; 1 cross-difficulty. Every tier stated in the rule and implemented in compute. Labels: excursion_relief changes the rounding direction and operation (honest method); interest_anchor selects which date the month count runs from (accepted as method).

`bizgas_ext_renewal_loyalty_credit` (baseline: credit = renewal_loyalty_credit_usd of the plan in force, rounded once):
| factor | label | decides | tiers | distinct | multi-source | cross |
|---|---|---|---|---|---|---|
| renewal_history_carry | **method** | carried_base_credit | 3 | ×2 / ×0.5 / ×1 | no (tier 1 single condition) | no |
| credit_spend_window | method | credit_spend_measure | 3 | half-24m / annualised-12m / 12m | no | no |
| credit_spend_multiplier | parameter | spend_multiplier | 3 | 1.5 / 1.25 / 1 | no | no |
| supply_tenure_bonus | parameter | tenure_bonus | 3 | 40 / 20 / 0 | no | no |
| electricity_bundle_bonus | parameter | bundle_bonus | 3 | 50 / 25 / 0 | yes — bizpower agreement status AND bizpower_billing count | bizpower |
| early_acceptance_bonus | parameter | early_bonus | 3 | 25 / 10 / 0 | no | no |
Counts as declared: 6; 4 parameter, 2 method. `renewal_history_carry` is labelled `method` but its three tiers multiply the same base credit by three different numbers (2, 0.5, 1) — a parameter (F-G2). After relabelling: 5 parameter, 1 method (credit_spend_window) — bounds still met. Bindings oddity: `credit_spend_multiplier` binds `spend_12m`, but its tier is read off `credit_spend_measure` (O-G8).

`bizgas_ext_swing_shortfall_rebill` (baseline: billed lower end − usage at the line's rate, plus "the service recovery credit"):
| factor | label | decides | tiers | distinct | multi-source | cross |
|---|---|---|---|---|---|---|
| seasoned_site_lower_end | parameter | lowered_lower_end | 3 | −10 % / −5 % / 0 | yes — energy-line count AND loyalty-line count | no |
| cycle_length_fit | method | fitted_lower_end | 3 | ×d/30 / ×d×12/365 / unchanged | no | no |
| shortfall_deadband_therms | parameter | shortfall_deadband | 3 | 100 / 50 / 0 | no | no |
| bundled_shortfall_rate | parameter | shortfall_rate | 3 | 0.0300 / 0.0450 / line rate | yes — bizpower status AND bizpower_billing sum | bizpower |
| service_recovery_credit_tier | parameter | service_recovery_credit | 3 | 25.00 / 10.00 / 0 | no | no |
Counts: 5; 4 parameter, 1 method; 2 multi-source; 1 cross-difficulty. Baseline coherence: F-G3.

`bizgas_ext_lapsed_renewal_price` (baseline: final_options_notice new_rate_usd_therm, rounded to 4 places):
| factor | label | decides | tiers | distinct | multi-source | cross |
|---|---|---|---|---|---|---|
| expired_term_offer_selection | method | offer_price | 3 | initial / min(both) / final | yes — final notice date AND initial notice date (two rows) | no |
| lapse_requote_uplift | parameter | lapse_uplift | 3 | 0.0150 / 0.0080 / 0 | no | no |
| electricity_term_bundle_discount | parameter | bundle_discount | 3 | 0.0120 / 0.0060 / 0 | no (one bizpower row) | bizpower |
| service_recovery_discount | parameter | recovery_discount | 3 | 0.0100 / 0.0050 / 0 | no | no |
| billed_volume_discount | parameter | volume_discount | 3 | 0.0100 / 0.0050 / 0 | no | no |
Counts: 5; 4 parameter, 1 method; 1 multi-source; 1 cross-difficulty.

Realism (every condition and every outcome is one a commercial gas supplier plausibly weighs/publishes): tenure, renewal history, broker channel, dual-fuel bundle, spend, early acceptance, volume, prior service failures, lapse re-quote, cycle length and deadbands are all ordinary commercial-energy pricing levers; every fall-through is the plan's published default (the plan's swing tolerance, adder, shortfall rate, loyalty credit, final notice price) rather than a straw man. The delivery-channel split of `interest_anchor` (mail → cycle start, email → cycle end) is the least natural lever but is a stated, non-degenerate rule (O-G9). No condition holds of every customer reaching its write; no two tiers of one ladder share an outcome.

### findings

**F-G1 — SOURCE-POLICY RED (both edges; bears on task 0 via E1, on task 1 via E2).**
- Symptom: each prerequisite sentence, and each edge's `condition`, requires that **every** swing excess (resp. shortfall) line "billed above what the swing (shortfall) rules allow" carry its own rebill credit; the resolving policy only ever corrects "the agreement's most recently posted swing_excess_charge (swing_shortfall_charge) line", and inherited `bizgas_billing_correction` bars correcting any line disputed more than `billing_dispute_lookback_months` (12) after posting.
- Root cause: the sentence's scope ("every … line") is broader than what `resolved_by` can bring about; the merged swing rules (the `bizgas_swing` clauses as replaced by the two rebill policies, whose tiers are evaluated "before the correction date") classify older lines as over-billed too.
- Evidence: loyalty rule "The renewal loyalty credit is fixed only after every swing excess line on the agreement that was billed above what the swing rules allow carries its own rebill credit."; E1 `condition` "Every swing_excess_charge line of the agreement whose billed amount_usd exceeds the swing excess amount the swing rules give has a rebill_credit line …"; excess rule "A swing excess correction is worked on the agreement's most recently posted swing_excess_charge line"; lapsed rule "The renewed price is not fixed until every swing shortfall line …"; shortfall rule "A swing shortfall correction is worked on the agreement's most recently posted swing_shortfall_charge line"; base `bizgas_billing_correction` "A commercial gas line may be corrected only when the business disputes it no later than billing_dispute_lookback_months calendar months after the line was posted."
- Consequence: in a world where an older line is over-billed under the merged rules and time-barred, a second reading exists — the gate can never be satisfied, so the root write may not be fixed (refuse / hand off) — next to the reading "correct the most recent line, then proceed". Demonstrated per task in `0.md` and `1.md` (problem_chain / findings).
- Affected: `bizgas.extended.yaml` → `extended_policies[bizgas_ext_renewal_loyalty_credit].rule` + `.prerequisite[0]`; `extended_policies[bizgas_ext_lapsed_renewal_price].rule` + `.prerequisite[0]`.

**F-G2 — SOURCE-FACTOR RED (mislabelled effect; bears on task 0).** `bizgas_ext_renewal_loyalty_credit.factors[renewal_history_carry]` is labelled `effect: method`, but its tiers "the base credit is multiplied by repeat_renewal_multiplier" / "… by broker_first_renewal_multiplier" / "carried as it is" substitute different numbers (2, 0.5, 1) into one formula `base_credit × m`. Consequence: the declared method count of the policy is overstated by one; after relabelling the policy keeps 1 honest method (`credit_spend_window`) and 5 parameters, so the count bounds survive. Affected: `extended_policies[1].factors[0].effect`.

**F-G3 — SOURCE-FACTOR RED (baseline not self-sufficient; bears on task 1).** `bizgas_ext_swing_shortfall_rebill.baseline.rule` ends "The shortfall rebill credit equals the over-billed amount plus the service recovery credit, rounded half up to the cent", but no sentence of `baseline.rule` states what the service recovery credit is; its value is stated only in the factor sentence ("when two or more rebill_credit lines … recovery_credit_repeat_usd; when exactly one … recovery_credit_first_usd; when none … no service recovery credit"), and `baseline.params` is `[months_per_year]` only. A reader holding only the baseline cannot compute a definite number. Demonstration on task 1's world in `1.md`. Affected: `extended_policies[2].baseline.rule`.

Observations (no demonstrable consequence at charter level; checked per task where noted):
- O-G1: the expiry-notice overwrite removes "when the two notices differ, the final_options_notice governs" for every renewal, but its replacement speaks only of the lapsed renewed price; an on-time renewal with differing notices has no explicit governing-notice sentence left (task 0 checks the consequence).
- O-G2: excess rule's notice lookup by `effective_date = billing_period_start` vs base `bizgas_index_pricing` "calendar month containing its billing_period_start" — undeclared; bites only for a cycle not starting on the 1st (task 0 checks).
- O-G3: `bizgas_agg_portfolio_bandwidth` not among the excess policy's refs nor addressed; bites only with ≥2 portfolio-plan sites (task 0 checks).
- O-G4: base correction eligibility is phrased "only when the business disputes it"; both rebill policies are `trigger: state_due` (agent-initiated). Whether the customer's consent counts as the dispute is a per-task persona question.
- O-G5: the shortfall overwrite's `replaced_by` texts do not mention the cycle-length fit or the deadband, though both change the shortfall therms; the superseded clauses are named, so this is a completeness blemish of `replaced_by`, not an undeclared override.
- O-G6: one base sentence superseded by two extended policies with different replacements; unique only by the disjoint time anchors.
- O-G7: after both rebill overwrites, the merged `bizgas_swing` billing text no longer states the band ends in one sentence; no task bills a new swing line.
- O-G8: factor binding sets: `excursion_relief` binds `cycle_energy_therms` (an input of the measured excess, not of the relief); `credit_spend_multiplier` binds `spend_12m` instead of `credit_spend_measure`. Binding sets remain disjoint.
- O-G9: within each rule, the baseline sentences ("where the swing tolerance is swing_tolerance_pct", "the correct excess therms are the measured excess therms", "plus an adder of swing_excess_adder_usd_therm", "each is charged at the rate_usd_therm on the shortfall line", "the offer price, which is the new_rate_usd_therm of the final_options_notice") and the factor sentences that re-decide the same quantity coexist in one rule; each ladder's fall-through equals the baseline sentence, and the ladder sentence is the more specific, so a reader resolves them one way. Recorded as an observation (it is the construction the factor relationship requires).

## post_reveal_findings

Written after both tasks' derivations were frozen (`0.md` 16:20:37Z, `1.md` 16:21:43Z) and GT was revealed (16:21:46Z). The charter-global section above is unchanged except for the clerical correction of its freeze-time line to the file mtime.

**F-G4 — SOURCE-POLICY RED (rule/compute equivalence, check 2; missed by the pre-reveal sweep, surfaced by the figure comparison in task 0).**
- Symptom: `bizgas_ext_swing_excess_rebill` rule: "when they are above minor_excursion_share and no more than moderate_excursion_share of the monthly contract volume, they are the measured excess times moderate_excursion_factor rounded up to a whole therm"; compute: `correct_excess_therms: "... (-int(-measured_excess * K('moderate_excursion_factor')) if ... "`. In the DSL `int` truncates toward zero, so `-int(-x)` equals `int(x)` for positive x — a round-down, not a round-up.
- Demonstrated consequence (same situation, two conclusions): task 0's world with the tolerance at its baseline 20 → measured excess 370 → 370 × 0.75 = 277.5 → rule 278 therms, compute 277 therms → rebill 68.78 (rule) vs 69.44 (compute, as recorded in `tasks/0.json` `computations[0].factor_sensitivity[swing_band_tolerance]`). Any world whose gold takes the moderate tier with a non-integer product would score the compute's figure against the rule's.
- Affected: `bizgas.extended.yaml` `extended_policies[bizgas_ext_swing_excess_rebill].compute` (`correct_excess_therms`); bears on task 0 (counterfactual figure only; gold 243.30 takes the minor tier and is unaffected). Task 1 does not claim this policy.
- Also confirmed at reveal: no other compute binding in the charter uses `-int(-…)`; every other "rounded half up to a whole therm" is `int(x + 0.5)` on non-negative operands.

## difficulty_verdict

| task | policy self-consistency | problem tree | factors | unique solution | GT match of frozen derivation |
|---|---|---|---|---|---|
| 0 | SOURCE-POLICY RED (F-G1, F-G4) | holds (reading A) | SOURCE-FACTOR RED (F-G2) | unique only under reading A of F-G1 | every scored value equal; one factor_sensitivity figure differs (F-G4) |
| 1 | SOURCE-POLICY RED (F-G1) | holds (reading A) | SOURCE-FACTOR RED (F-G3) | unique only under reading A of F-G1 | every scored value and every sensitivity figure equal |

The difficulty does **not** pass the source-layer audit. The independent blind derivations landed on GT for every scored write and argument in both tasks; the reds are charter defects (prerequisite scope, one rule/compute rounding mismatch, one mislabelled factor, one non-self-sufficient baseline), not derivation disagreements.

## closing_checklist

Not written: Step 4 closes a difficulty only once every task passes all four relationships, and neither task does. Status of the items for the record: per-task files 0.md and 1.md correspond one-to-one with tasks/0.json and tasks/1.json, with `_difficulty.md` alongside (round 1; no older revision); the four extended policies are fully covered by the two tasks with pairwise-disjoint scopes (`charter_scope` confirmed at reveal); each task tool has an independent uuid8; each tree has 1 prerequisite problem, 1 value_input edge, 1 owner=user write, no cycle, and the difficulty's graph is acyclic; factor counts are within bounds after relabelling F-G2. The instantiation-stage gates were not re-run by this audit (the brief's snapshot is cited in `charter_global_frozen`; re-running is the orchestrator's step after rework).

## revision_2

### charter_global_frozen (revision_2)
- Re-audit start 2026-10-04T17:52Z; this section written before any round-2 `tasks/*.json` was opened. Auditor: same independent auditor as round 1.
- Hash comparison against round 1: `bizgas.extended.yaml` **changed** (round 1 11e1d2c6…94c → round 2 987b433eea8e88bd356560fecb5ed21d92731c3f96527e79abaad3c2feca7cfa); `task_tools.py` **unchanged** (190979d7…5cf); `blueprint/products/bizgas.yaml` unchanged (35b6287c…d31). Masked views rebuilt (task_0.view.json fd42895d…2f2a, task_1.view.json 42b9754d…fd48; recomputed hashes match HASHES.txt).
- Consequence for re-derivation: every charter-global section that reads the charter (policy_conflict_scan, rule_compute_equivalence, prerequisite_graph, prerequisite_sentences, override_declarations, factor_ladders) is re-derived in full below. `action_binding_and_uuids` reads the tool module (unchanged) and the `(target_tool, computes)` pairs (re-checked: unchanged — same four pairs, one policy each), so it is carried forward by reference to round 1 on the grounds of the two hashes.
- Gate snapshot (round 2, supplied by the orchestrator): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; CACHE-DIFF INFO; SCOPE OK; check_traceability deferred. Entry conditions complete.
- contamination_disclosure (charter-global): none for this section — it reads only the charter, schema, tools and DSL semantics.

### what changed in the charter (located by re-reading every extended policy; no diff file was available, the comparison is against the round-1 text quoted in this report)
- `bizgas_ext_swing_excess_rebill`: `base_policy_refs` + `bizgas_agg_portfolio_bandwidth`; new rule sentences "A business that asks for the line to be put right once it has been pointed out to it is disputing that line." and "This correction covers an agreement whose plan has portfolio_bandwidth false, or an agreement that is the business's only commercial gas agreement on a plan with portfolio_bandwidth true; where the business has two or more agreements on plans with portfolio_bandwidth true, the portfolio measure decides the swing and the line is outside this correction."; compute `correct_excess_therms` moderate tier now `int(m*0.75) + (1 if m*0.75 > int(m*0.75) else 0)`; `cycle_energy_therms`/`cycle_usage` folded into `measured_excess`; `excursion_relief.bindings` = [measured_excess, correct_excess_therms].
- `bizgas_ext_renewal_loyalty_credit`: new rule sentence "An acceptance on or before contract_end_date takes the plan, term and price of the final_options_notice where the two expiration notices of the expiring term differ."; prerequisite sentence and `condition` narrowed to "the agreement's most recently posted swing excess line, when its billed amount is above the correct swing excess amount and its correction lookback has not ended"; `renewal_history_carry.effect` → parameter (tier values "base credit x …"); bindings `credit_spend_window` = [energy_cycles_on_file, credit_spend_measure], `credit_spend_multiplier` = [spend_12m, spend_24m, spend_multiplier].
- `bizgas_ext_swing_shortfall_rebill`: refs + portfolio; dispute and portfolio sentences (shortfall wording); band `replaced_by` now carries the lowering, the cycle-length fit and the deadband; amount clause and baseline last sentence now "The shortfall rebill credit equals the over-billed amount, together with a service recovery credit only where one is due, rounded half up to the cent, and it is posted as a negative amount."
- `bizgas_ext_lapsed_renewal_price`: prerequisite sentence and `condition` narrowed to "the agreement's most recently posted swing shortfall line, when its billed amount is above the correct shortfall amount and its correction lookback has not ended".
- Base section: still verbatim equal to `blueprint/products/bizgas.yaml` on every key (mechanical comparison).

### policy_conflict_scan (revision_2)
Same separations as round 1 (rebill policies by line type; renewal policies by on/before end vs after rollover; double supersession of the base credit sentence resolved by the disjoint time anchors). New sentences checked for overlap: the portfolio scope sentence in both rebill rules agrees with base `bizgas_agg_portfolio_bandwidth` (combined measure decides for ≥2 portfolio-plan sites; a single portfolio-plan site is measured on itself either way) — compatible. The on-time renewal sentence ("takes the plan, term and price of the final_options_notice where the two … differ") restates for the on-time anchor what base `bizgas_expiry_notices` said before the lapsed overwrite; the lapsed replacement governs only the lapsed anchor — compatible, and O-G1 is closed. The dispute sentences define what counts as a dispute for base `bizgas_dispute_lookback` without changing its window — compatible (no base sentence defines "disputes"; no overwrite needed). Scope: two disjoint trees covering the four policies, unchanged.

### rule_compute_equivalence (revision_2)
Mechanical: every compute binding has a `compute_basis` entry and no basis entry lacks a binding (all four policies); every `baseline.rule` sentence is a sentence of its `rule`; every `replaced_by` sentence is a sentence of its rule; every `superseded_clause` is verbatim in the named base rule. Manual sweep of the changed bindings: excess moderate tier now implements "rounded up to a whole therm" (checked: 370→278, 360→270, 341→256, 400→300, 680→510 equal `ceil(m×0.75)`) — **F-G4 closed**; `measured_excess` quotes both the cycle-usage and measured-excess sentences. Unchanged bindings: as round 1. The new dispute/portfolio/on-time-notice sentences are eligibility/action statements with no computed quantity — no empty promise. PASS.

### action_binding_and_uuids (revision_2)
Carried forward from round 1 (`task_tools.py` hash unchanged; the four `(target_tool, computes)` pairs unchanged). PASS.

### prerequisite_graph (revision_2)
Two edges, unchanged endpoints/kinds/gates/forms; `policy_source` verbatim in each blocked rule (mechanical True); gates `spend_24m`, `rebills_last_24m` exist; acyclic. `condition` now names exactly the handling-time state the narrowed sentence describes (most recent line; billed above the correct amount; posted_date within billing_dispute_lookback_months of the handling date) — neither strengthened nor weakened relative to the sentence; `resolved_by` (the depended-on target tool) now can always make it hold, because the depended-on rule works exactly that line. PASS.

### prerequisite_sentences (revision_2)
E1: "The renewal loyalty credit is fixed only after the agreement's most recently posted swing excess line, when its billed amount is above the correct swing excess amount and its correction lookback has not ended, carries its own rebill credit." — connective "only after"; waited-on state record-visible (rebill_credit pointing at that line); no tool, id or snake_case; "correct swing excess amount" is the excess rule's own term, so the reader lands on `bizgas_ext_swing_excess_rebill` and its single object, the most recently posted swing_excess_charge line. One write brings it about. Scope equals what `resolved_by` can do. E2: the same with "not fixed until" and the shortfall terms → `bizgas_ext_swing_shortfall_rebill`. The second and third readings of round 1 (every line incl. time-barred ones; base-rule judgement) are excluded by the text: older lines are not "the most recently posted" line and a time-barred line is excluded by "its correction lookback has not ended"; "the correct swing excess/shortfall amount" names the extended rule's computation, not base billing. **F-G1 closed.** No other cross-problem order added by the new sentences (the on-time-notice and dispute sentences order nothing). PASS.

### override_declarations (revision_2)
As round 1, plus: `bizgas_agg_portfolio_bandwidth` now in both rebill refs and handled by an explicit scope sentence (O-G3 closed); shortfall band `replaced_by` now names the fit and the deadband (O-G5 closed); `bizgas_index_pricing` S2 vs the excess rule's `effective_date = billing_period_start` lookup still undeclared (O-G2 unchanged — still bites only for cycles not starting on the 1st). No new undeclared override.

### factor_ladders (revision_2)
- Excess: 5 factors (3 parameter, 2 method), unchanged ladders; binding fix O-G8 (excursion_relief) closed.
- Loyalty: `renewal_history_carry` now `parameter` with ladder values "base credit x K(…)" — honest (**F-G2 closed**); counts 6 = 5 parameter + 1 method (`credit_spend_window`), within bounds. `credit_spend_multiplier` now binds [spend_12m, spend_24m, spend_multiplier] while its tier is read off `credit_spend_measure` (bound by `credit_spend_window`): binding sets disjoint, no effect on any substitution — O-G8 only partly addressed, kept as an observation.
- Shortfall: 5 factors unchanged; `baseline.rule` now ends "together with a service recovery credit only where one is due" — a baseline-only reader is told no credit unless one is due and the baseline states none, so the baseline yields a definite number (over-billed + 0), on the same footing as the excess baseline's "any overcharge interest due" accepted in round 1. **F-G3 closed.**
- Lapsed: unchanged.
Distinctness, realism and multi-source/cross-difficulty counts as round 1.

### findings (revision_2, pre-reveal)
- F-G1 closed; F-G2 closed; F-G3 closed; F-G4 closed (each argued above).
- O-G1 closed (on-time governing-notice sentence); O-G3 closed; O-G4 closed at charter level (dispute definition; per-task persona check in task files); O-G5 closed; O-G8 partly (observation kept).
- O-G2, O-G6, O-G7, O-G9 unchanged (reworker left them; still observations without a demonstrable consequence).
- New observation O-G10: the narrowed prerequisite sentences require a rebill on the most recent line "when its billed amount is above the correct … amount", while the new portfolio sentence places a line outside the correction for a business with ≥2 portfolio-plan agreements; for such a business the sentence would wait on a state no write can bring about. Neither task's business has a second gas agreement, so no consequence is demonstrable.
- No new SOURCE-POLICY / SOURCE-FACTOR defect found at charter level.

### post_reveal (revision_2)
Round-2 GT revealed 2026-10-04T17:55:20Z, after the charter-global section and both tasks' revision_2 derivations were on disk. Every scored write, owner, order and argument, every `prerequisite_closure` value and every `computations` figure of both tasks equals the frozen derivation; the round-1 discrepancy (task 0 swing_band_tolerance sensitivity) is resolved by the F-G4 fix. No new finding from the reveal; residual stale paraphrase in each task's `[Why a good test]` paragraph recorded as an observation in `0.md` / `1.md`.

### difficulty_verdict (revision_2)
| task | policy self-consistency | problem tree | factors | unique solution |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS | PASS |
Round-1 REDs F-G1, F-G2, F-G3, F-G4 closed; no regression; no new SOURCE-* defect. The difficulty passes the source-layer audit.

### closing_checklist (revision_2)
- Per-task files `0.md`, `1.md` correspond one-to-one with `tasks/0.json`, `tasks/1.json`; `_difficulty.md` alongside; round-1 text preserved, revision_2 appended; both comparison sections carry PASS.
- The four extended policies are covered by two pairwise-disjoint scopes ([excess, loyalty], [shortfall, lapsed]); task tools and GT closed; four independently generated uuid8 tails (d99acf60, c0a82e44, b4d87cc1, f259b0f9).
- Each tree: 1 prerequisite problem, 1 value_input edge (≥ max(n−1,1)), one owner=user write, acyclic; the difficulty's edge set (two disjoint chains) is acyclic.
- Computations: excess 5 factors (3p/2m), loyalty 6 (5p/1m), shortfall 5 (4p/1m), lapsed 5 (4p/1m); each task has ≥1 multi-source and ≥1 cross-difficulty (bizpower) factor with seeded rows; every ladder 3 tiers, distinct outcomes, stated in the rule; every factor bears weight against an honest baseline; each whole baseline gives a definite number ≠ gold.
- Instantiation-stage gates on the final form: re-run by the orchestrator after rework (EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; CACHE-DIFF INFO; SCOPE OK; check_traceability deferred until the KB is published) — cited, not re-run by this auditor.
- Open observations (no rework required): O-G2, O-G6, O-G7, O-G9 (unchanged), O-G8 residual binding of `credit_spend_multiplier`, O-G10 (portfolio-excluded line vs prerequisite sentence for a ≥2-portfolio-site business), stale `[Why a good test]` paraphrases.
