# Policy-task audit — residential_electricity_care / task 1

## source_derivation_frozen

- Freeze time: 2026-10-04T16:36Z (round 1). Auditor: independent policy-task auditor (Claude agent, erl-task-policy-audit).
- Freeze hashes: `task_1.view.json` = `4aab36daee63865e6cf1e5e565436a7b3312431c6c33cfa0fb3329a3396aae72`; charter `5266e76b…bdf`; tools `8cc6224c…7cf`.
- Fields permitted: `task_index`, `frozen_time` (2026-10-14 11:40 CDT), `user_scenario`, `initial_state` from the masked view; the charter, tools, blueprint.
- Fields masked (not read before this section was written to disk): `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, worklogs, other audits. Task 0's GT was not revealed either.
- contamination_disclosure: none.
- Arithmetic cross-checked with the charter's own `compute` lines under the `check_compute.py` DSL on the masked world plus the auditor's derived writes (temporary script, deleted).

### policy_self_consistency (this task only)

- Charter-global conclusions cited: `_difficulty.md` § override_declarations (no undeclared override reaching a scored quantity; the plan-change eligibility sentence does not require a price offer — this world seeds no `price_offers` rows), § rule_compute_equivalence, § prerequisite_graph, § prerequisite_sentences (edges 4–6 pass), § action_binding_and_uuids.
- O-1 (dispute kWh MAX): the largest-amount off-peak line `29f0ca62…` (164.80) is also the largest-kWh off-peak line (1,240) and the multiplier is 0.00 → no consequence.
- O-2 (rebill LATEST without the within-limit filter): the latest off-peak line `94a54dd6…` (posted 2026-10-03, 116.95) is the within-limit one → rule and compute select the same line.
- O-3 (rounding): no scored figure of this task is a half-cent tie. One factor-substitution figure is: plan-change rate with the billing-error concession at baseline = 13.29 − 0.875 = 12.415 → `RND` 12.41, half-up 12.42 (proof field, compared after reveal).
- Handling time: all writes at `NOW` 2026-10-14; the rebill after the dispute; the plan change after the rebill and the sign-up credit.
- No real-world wait: the dispute is opened (status `open`), not settled; the rebill's input is the open dispute count, not the review outcome. All other inputs are seeded rows.

### problem_chain

Root — customer: "You want to move your home electricity from Free Nights to the plain twelve-month Price Lock, starting with the next billing cycle". Policy `power_ext_plan_change_rate` (tool `change_plan_fbee8941`, owner=user: "The customer authorizes a mid-term plan change personally").

1. Prerequisite sentence "The plan-change rate is fixed only after the agreement's bill lines carry a rebill credit for every over-billed energy line whose correction is within the care agent's adjustment limit."
   - Agreement `64a9aa9b…` Free Nights 12 (`offpeak_rate_multiplier 0.00`, contract rate 13.29). Off-peak lines: 2026-03 … 2026-07 billed 0.00 (correct); `29f0ca62…` (cycle 2026-08-01, 1,240 kWh, billed 164.80 at 13.29, posted 2026-09-03) and `94a54dd6…` (cycle 2026-09-01, 880 kWh, billed 116.95, posted 2026-10-03) billed at the full rate → over-billed 164.80 and 116.95. All on-peak lines recompute exactly (e.g. 1,021 × 13.29 / 100 = 135.69). Agent limit 150.00. `94a54dd6…` is within the limit (bare 116.95; worked-out rebill 138.24) and has no rebill line → unmet. → `power_ext_offpeak_rebill_credit` (tool `post_rebill_credit_41f05139`). kind value_input (`plan_error_items`).
2. Rebill rule sentence 3: "A rebill credit is not posted until every over-billed line of the agreement whose correction exceeds the care agent's adjustment limit stands as an open billing dispute." `29f0ca62…` over-billed 164.80 > 150; the world has no `power_billing_disputes` rows → unmet. → `power_ext_offpeak_dispute_amount` (tool `open_billing_dispute_231feff0`). kind value_input (`open_dispute_count`).
3. Prerequisite sentence "A plan change is not recorded until the sign-up credit the current plan has earned stands on the agreement's bill lines." Free Nights 12 `signup_credit_usd 50.00`, `signup_credit_after_cycles 3`; completed cycles 2026-03 … 2026-09 = 7 ≥ 3; no `signup_credit` line on `64a9aa9b…` → unmet. → `power_ext_signup_credit_amount` (tool `post_signup_credit_3f59f0ed`). kind state_gate.
4. Dispute and sign-up rules carry no prerequisite sentence.

Derived tree: plan change ← {rebill ← dispute, sign-up}; 3 prerequisite problems; 2 value_input edges (= max(3−1,1)); acyclic; owner=user write = the root. Isomorphic to the declared graph.

Load-bearing runs:
- Skip dispute: rebill 133.24 instead of 138.24 (open disputes 0 → no repeat courtesy); plan-change rate also moves (error items 1).
- Skip rebill: plan-change rate 12.10 instead of 11.79 (error items 1 → single concession).
- Skip sign-up: the plan change is not recordable (state gate); the rate is unaffected (state_gate, as declared).

Parallel-edge test: siblings rebill-branch and sign-up. The sign-up computation reads energy lines, gas status and gas sign-up lines; the rebill/dispute computations read off-peak/on-peak energy lines, fee lines, open disputes, gas status; the plan-change rate reads rebill lines and open disputes but no sign-up line. No write of one branch is read by the other → one terminal state for every compliant order.

No-wait / tool layer: `task_tools.py` lines 154–243 perform unconditional update/create; nothing checks a prerequisite.

### task_independent_derivation

User need and authorisation: the customer asks only for the plan change to "the plain twelve-month Price Lock" (= Beacon Ridge Price Lock 12) from the next billing cycle; she raises no prerequisite (bill errors and a missing credit are answered only "If the representative tells you …"); she authorises credits and billing-review referrals ("you are happy for them to post credits or send things to billing review without asking you each time"); she confirms the change personally on hand-over and accepts "the plan, rate and dates exactly as the representative states them". She ends the call after completing the change — the root's write.

Identity: `find_customers(phone_number=6305550112)` → `ccabf6f5…`; verify with phone + SSN last four 1758.

Now / wait / refuse: act now. Agreement active; Free Nights 12 → Price Lock 12: equal term (12 = 12) → allowed; Price Lock 12 is offered in IL, residential, CAP-eligible, no smart-meter requirement; `etf_waive_on_upgrade true` → no fee.

Writes (one compliant order; the sign-up credit may sit anywhere before the plan change):

1. `open_billing_dispute_231feff0` (agent) — opening world.
   - Object: `power_agreement_id 64a9aa9b-7425-4a75-8990-ec8967437eda`, `source_billing_id 29f0ca62…` (largest billed off-peak line).
   - over-billed 164.80 − RND(1,240 × 13.29 × 0.00 / 100) = 164.80; protection: `DAYS(2026-02-18, 2026-10-14)` = 238 ≤ 365 → ×1.10 = 181.28; fee return: ≥100 and fee lines → +9.95; bundle: gas `72bc055f…` Capped Variable 12 (`capped_variable`, active) → other +3.00; usage: on-peak 5,573 kWh / 7 = 796.1 → high +2.00; tenure `MONTHS(2026-03-01, 2026-10-14)` = 7 → mid +1.00; systemic: off-peak billed total 281.75 → high +5.00.
   - `disputed_amount_usd` = **202.23**.
2. `post_rebill_credit_41f05139` (agent) — after write 1.
   - Object: `source_billing_id 94a54dd6…`, `billing_period_start 2026-09-01`.
   - over-billed 116.95; late: `DAYS(2026-10-03, 2026-10-14)` = 11 → ×1.02 = 119.289; fee return ≥100 → +9.95; bundle other +3.00; open disputes 1 → single +5.00; tenure 7 → mid +1.00.
   - `rebill_amount_usd` = RND(138.239) = **138.24** (within 150 under every reading of the limit test). Contrast on the opening world: 133.24.
3. `post_signup_credit_3f59f0ed` (agent) — any time before write 4.
   - Object: `64a9aa9b…`, `referred_customer_id ""`, `billing_period_start 2026-06-01` (cycle after the third completed cycle, 2026-05).
   - plan 50.00; completed cycles 7 (on-peak lines; off-peak lines not counted), 4 beyond 3 → ×1.5 = 75.00; gas active and gas sign-up line `6fc9ac52…` present → settled +15.00; usage 10,233 kWh / 7 = 1,461.9 → high +10.00; off-peak share 4,660 / 10,233 = 0.455 → high +10.00.
   - `credit_amount_usd` = **110.00**. No online enrollment credit (Free Nights 12 `online_enrollment_credit_usd 0.00`).
4. `change_plan_fbee8941` (user, handed over) — after writes 1–3.
   - rate in force 13.29; error items = 1 rebill + 1 open dispute = 2 → multi 0.50; bundle other 0.20; tenure 7 → mid 0.15; volume 1,461.9 → high 0.20; peak max(on-peak 1,021, all-hours none) → high 0.15; combined 1.20; remaining `MONTHS(2026-10-14, 2027-02-28)` = 4 → ×1.25 = 1.50.
   - Args: `variant_name "Beacon Ridge Price Lock 12"`, `term_months 12`, `contract_rate_cents_kwh` = 13.29 − 1.50 = **11.79**, `plan_change_date 2026-11-01` (next cycle start; next read 2026-11-01), `contract_end_date 2027-10-31`. Contrast on the opening world: 12.41.

Terminal state: agreement on Price Lock 12 at 11.79, 2026-11-01 – 2027-10-31, active; one open dispute (202.23 on `29f0ca62…`); rebill −138.24 on `94a54dd6…`; sign-up −110.00 (2026-06-01).

Context closure: all inputs reachable through `find_power_agreements`, `find_power_billing`, `find_power_billing_disputes`, `find_gas_agreements`, `find_gas_billing`, `find_premises`, and the charter's plan parameters.

### factor_weight

**Dispute (202.23; whole baseline 164.80).** new_customer_protection (M) first-year → 185.75; dispute_fee_return (P) full → 192.28; dispute_bundle_courtesy (P, cross gas) other → 199.23; dispute_usage_courtesy (P) high → 200.23; dispute_tenure_courtesy (P) mid → 201.23; systemic_error_courtesy (P) high → 197.23. Each bears weight on this world. But see F-T1-1: on the customers who can reach this write, `dispute_fee_return` can only take its first tier and `systemic_error_courtesy` can never take its fall-through. Near-miss: the later, smaller over-billed line `94a54dd6…` (excluded by "largest billed amount"); off-peak lines excluded from the on-peak average.

**Rebill (138.24; whole baseline 116.95).** late_correction_scaling (M) short → 135.90; rebill_fee_return (P) full → 128.29; rebill_bundle_courtesy (P, cross gas) → 135.24; repeat_referral_courtesy (P) single → 133.24; rebill_tenure_courtesy (P) mid → 137.24. Near-miss: `29f0ca62…`, the larger over-billed line, excluded by "within the care agent's adjustment limit".

**Sign-up (110.00; whole baseline 50.00).** late_signup_scaling (M) long → 85.00; dual_commodity_welcome (P, cross gas, multi-source: `gas_agreements/72bc055f.status active` × `gas_billing/6fc9ac52… signup_credit`) settled → 95.00; signup_usage_bonus (P) high → 100.00; load_shift_bonus (P) high → 100.00. Near-miss: the 7 off-peak energy lines, excluded from the cycle count (counting them gives 14 cycles, 731 kWh/cycle → no usage bonus, and 11 beyond → same late tier).

**Plan change (11.79; whole baseline 13.29).** billing_error_concession (P) multi → 12.41 (half-up 12.42; O-3); plan_bundle_reduction (P, cross gas) other → 12.04; plan_tenure_reduction (P) mid → 11.98; plan_volume_reduction (P) high → 12.04; peak_cycle_reduction (P) high → 11.98; remaining_term_scaling (M) short → 12.09. Near-miss: off-peak lines excluded from the cycle denominator (14 lines → 731 kWh → no volume reduction) and from the peak (1,240 kWh off-peak line).

Stamps: none naming a tier. `premises.annual_kwh_usage 14630` (≈1,219/month) agrees with the sign-up usage and plan volume high tiers (observation).

Counts: dispute 6 declared (5P/1M) — 4 survive F-1 (3P/1M); rebill 5 (4P/1M) — `rebill_fee_return` survives only as a single-condition ladder; sign-up 4 (3P/1M); plan change 6 (5P/1M). Multi-source: `dual_commodity_welcome` (the two fee-return factors' multi-source claim is void, F-1). Cross-difficulty: gas, seeded (holding `72bc055f…`, 8 `gas_billing` rows including the sign-up credit). Floors hold after striking.

## findings

### F-T1-1 — SOURCE-FACTOR RED: three ladder conditions hold of every customer who reaches the dispute/rebill writes (`_difficulty.md` F-1)

- Symptom: `dispute_fee_return` always lands on its first tier; `systemic_error_courtesy` can never land on its fall-through; `rebill_fee_return`'s "bill lines carry a monthly service fee" part is constant.
- Root cause: both corrections apply only to off-peak lines of a time-of-use agreement; the only such plan is Free Nights 12 (fee 9.95 billed every cycle, multiplier 0.00); a dispute requires a correction > 150.00, so the disputed line's over-billed amount (= its billed amount) exceeds 150 (≥ 114.6 even if the limit is tested on the worked-out amount).
- Evidence on this world: fee lines `270ab1e5…`, `89081fd3…`, … `926de86f…` (9.95 each, every cycle); disputed over-billed 164.80; off-peak total 281.75. Rule text: "Dispute fee return: when the over-billed amount is 100 USD or more and the agreement's bill lines carry a monthly service fee, the plan's full monthly service fee is added; when the over-billed amount is from 50 up to but not including 100 USD and the bill lines carry a monthly service fee, half of that fee is added; otherwise nothing is added." / "Systemic error courtesy: … at 250 USD or more … from 100 up to but not including 250 USD … below 100 USD nothing is added." / "Rebill fee return: when the over-billed amount is 100 USD or more and the agreement's bill lines carry a monthly service fee …".
- Demonstrated consequence: for every customer who can reach `open_billing_dispute_231feff0`, `dispute_fee_return` = the full fee (a constant add-on, not a tier) and the `systemic_error_courtesy` ladder has two reachable tiers; the fee-line condition of `rebill_fee_return` divides no customer, so its declared multi-source character is void. The struck factors still move this world's figure, but they are not factors under the audit's ladder test. Counts still meet the floors (dispute 4, rebill 4; multi-source via `dual_commodity_welcome`).
- Affected: `power.extended.yaml` → `power_ext_offpeak_dispute_amount.factors[dispute_fee_return, systemic_error_courtesy]` and rule sentences 6 and 10; `power_ext_offpeak_rebill_credit.factors[rebill_fee_return]` and rule sentence 6; `computations[]` of this task (dispute, rebill).
- Previous revisions: none (round 1).

### Observations
- O-3: billing-error concession baseline substitution 12.415 → `RND` 12.41 vs half-up 12.42 (proof field).
- O-5, O-9, O-12 (`_difficulty.md`).
- Stamp-adjacent `annual_kwh_usage` agrees with two tiers.

## source_gt_comparison

- Reveal time: `tasks/0.json` was opened at 2026-10-04T16:24:58Z, `tasks/1.json` immediately after task 0's comparison data was read. Timestamp note: the "Freeze time" line above (16:36Z) was an estimate written into the file; the file's actual write time is 16:24:54Z (`stat`), before any reveal. The frozen text is left untouched.
- Revealed: `evaluation_criteria` (16 actions), `computations` (4), `charter_scope`, `required_documents`, `prerequisite_closure`, `design_rationale`, `solvability_contract`.

| item | frozen derivation | GT | same? |
| --- | --- | --- | --- |
| need / authorisation / timing | plan change to Price Lock 12 from next cycle; agent posts credits and referrals; customer confirms change personally; act now | same; step 15 owner=user | same |
| necessary reads | customer, premise, agreement, bill lines, disputes, gas agreement + ledger | steps 0–7 identical set | same |
| now / wait / refuse | act now | act now | same |
| scope | {plan_change, rebill, dispute, signup} | `charter_scope` identical | same |
| dispute | `64a9aa9b…`, `29f0ca62…`, 202.23 | step 9 identical | same |
| rebill | `94a54dd6…`, 2026-09-01, 138.24 | step 11 identical | same |
| sign-up | `""`, 2026-06-01, 110.00 | step 13 identical | same |
| plan change | PL12, 12, 11.79, 2026-11-01, 2027-10-31 (user) | step 15 identical | same |
| order | dispute → rebill → plan change; sign-up anywhere before plan change | 9, 11, 13, 15; `order_uniqueness` states sign-up commutes | same |
| terminal state | as derived | same | same |

Problem tree vs `prerequisite_closure`:
- plan change → rebill (value_input, state): why-false 116.95 on `94a54dd6…`, correction 138.24 within 150, no rebill line; flip: error items 2, 0.25 → 0.50 — equal (auditor: skip rebill → 12.10).
- rebill → dispute (value_input, state): 164.80 on `29f0ca62…` > 150, no dispute; flip: open disputes 1, courtesy 5.00 — equal (skip → 133.24).
- plan change → sign-up (state_gate, state): 3 qualifying cycles by 2026-05-31, no sign-up line; flip at 2026-06-01 — equal.
- `edge_load_bearing` figures 12.10 / 133.24 & 12.10 / unchanged rate + gate — equal to the frozen runs.
- `order_uniqueness` (sign-up free relative to dispute and rebill; both precede the plan change) — equal to the frozen parallel-edge test; true on recomputation.

Factors vs `computations[]`:
- Dispute: GT 185.75 / 192.28 / 199.23 / 200.23 / 201.23 / 197.23, baseline 164.8 — equal.
- Rebill: GT 135.9 / 128.29 / 135.24 / 133.24 / 137.24, baseline 116.95 — equal.
- Sign-up: GT 85.0 / 95.0 / 100.0 / 100.0, baseline 50.0 — equal.
- Plan change: GT 12.41 / 12.04 / 11.98 / 12.04 / 11.98 / 12.09, baseline 13.29 — equal to `RND`; the billing-error-concession figure is a half-cent tie (12.415) that the rule's "rounded half up" puts at 12.42 (O-3; proof field only, the scored 11.79 is unaffected).
- `design_rationale` labels `dispute_fee_return (multi)` and implies the fee-line condition is evidence; F-1 shows that condition, and the over-billed ≥ 100 condition of the dispute ladder, hold of every customer who reaches the write — the "multi" claim is not true as an assertion about which customers the ladder divides.

Closest alternative candidates and exclusion: (a) disputing the most recent over-billed line instead of the largest — excluded by "The dispute is opened on the off-peak energy line of the agreement with the largest billed amount"; (b) rebilling the August line — excluded by "whose off-peak rebill amount is within the care agent's adjustment limit" and by its over-limit correction; (c) counting off-peak lines as cycles (14) — excluded by "Completed cycles are counted as the agreement's billing cycles that carry an on-peak or an all-hours energy charge line"; (d) pricing the plan change from a price offer — excluded by the declared override ("rather than the price-sheet offer"); (e) a renewal-style term start (day after contract end) — excluded by "takes effect at the start of the next billing cycle".

Verdict per relationship:
- Policy self-consistency: PASS (charter-global observations O-1, O-2, O-3, O-5, O-9, O-12 do not change any scored value here).
- Problem tree holds: PASS.
- Factors bear weight: **SOURCE-FACTOR RED** (F-T1-1 / `_difficulty.md` F-1: `dispute_fee_return` and `systemic_error_courtesy` ladders, and the fee-line part of `rebill_fee_return`, state conditions that hold of every customer who reaches the write). All declared factors move this world's figures and the floors still hold after striking them.
- Unique solution: PASS — the frozen derivation equals GT item by item.

## revision_2

### source_derivation_frozen (revision_2)

- Written 2026-10-04 (round 2) before `tasks/1.json` of round 2 was opened. View hash `4aab36da…6aae72` = round 1; charter and tools changed → per-task sections re-derived.
- contamination_disclosure: the round-1 GT of this task was read in round 1. Figures below are recomputed from the round-2 charter on the view.

#### policy_self_consistency (round 2)
- Cites `_difficulty.md` § revision_2. O-1/O-14: correct amount of `29f0ca62…` = 164.80 × 0.00 = 0.00 under either wording. O-2 closed: the latest off-peak line `94a54dd6…` is within the limit, so sentence 2 credits it here. O-13 not exercised (latest line within limit; one over-limit line, which is the largest).
- Handling time / no wait: unchanged.

#### problem_chain (round 2)
Unchanged tree (plan change ← {rebill ← dispute, sign-up}); each edge unmet at opening for the same rows as round 1. Load-bearing: skip dispute → rebill 133.24 and plan-change rate 12.15; skip rebill → plan-change rate 12.15 (error items 1 → 0.25; 0.95 × 1.2 = 1.14); skip sign-up → rate unchanged, gate false. Sign-up branch independent of the dispute/rebill branch (re-checked against the new dispute bindings). Opening-world plan-change rate: 12.45.

#### task_independent_derivation (round 2)
1. `open_billing_dispute_231feff0`: `64a9aa9b…`, `29f0ca62…`. Over-billed 164.80 − RND(164.80 × 0.00) = 164.80; protection 238 days → ×1.10 = 181.28; fee return: reliance 4,660 / 10,233 = 0.455 → full 9.95; bundle (capped variable) 3.00; usage 796.1 → 2.00; tenure 7 months → 1.00; systemic: off-peak lines billed at 13.29 = `29f0ca62…`, `94a54dd6…` = 2 → mid 3.00 (the five 0.00-rate off-peak lines excluded). Disputed amount **200.23**.
2. `post_rebill_credit_41f05139`: `94a54dd6…`, `2026-09-01`. 116.95 × 1.02 = 119.289; fee return (over-billed 116.95 ≥ 100) 9.95; bundle 3.00; open-review (1 open dispute) 5.00; tenure 1.00 → **138.24** (within 150).
3. `post_signup_credit_3f59f0ed`: `""`, `2026-06-01`, **110.00** (unchanged).
4. `change_plan_fbee8941` (user): Price Lock 12, 12, rate = 13.29 − (0.50 + 0.20 + 0.15 + 0.20 + 0.15) × 1.2 = 13.29 − 1.44 = **11.85**, `2026-11-01`, `2027-10-31`.
Persona, identity, authorisation, closure: unchanged and passing.

#### factor_weight (round 2)
- Dispute: protection 183.75; fee return 190.28; bundle 197.23; usage 198.23; tenure 199.23; systemic 197.23; baseline 164.80. Every ladder's conditions vary across the customers who reach the write (`_difficulty.md` revision_2 § factor_ladders). Near-miss: the five off-peak lines billed at 0.00 (excluded from the full-rate count) and the smaller over-billed line `94a54dd6…` (excluded by "largest billed amount").
- Rebill: late 135.90; fee return 128.29; bundle 135.24; open-review 133.24; tenure 137.24; baseline 116.95.
- Sign-up: 85.00 / 95.00 / 100.00 / 100.00; baseline 50.00.
- Plan change: concession 12.45; bundle 12.09; tenure 12.03; volume 12.09; peak 12.03; remaining-term 12.09; baseline 13.29. No half-cent ties.
- Multi-source: `dual_commodity_welcome`; cross-difficulty gas, seeded.
- Pre-reveal verdict: PASS on all four relationships.

### source_gt_comparison (revision_2)

- Reveal time: 2026-10-04T17:42:38Z (after the revision_2 freeze, 17:42:31Z).

| item | frozen (round 2) | GT (round 2) | same? |
| --- | --- | --- | --- |
| scope | {dispute, rebill, signup, plan_change} | identical | same |
| dispute | `29f0ca62…`, 200.23 | step 9 identical | same |
| rebill | `94a54dd6…`, 2026-09-01, 138.24 | step 11 identical | same |
| sign-up | `""`, 2026-06-01, 110.00 | step 13 identical | same |
| plan change (user) | PL12, 12, 11.85, 2026-11-01, 2027-10-31 | step 15 identical, owner user | same |
| order | dispute → rebill → plan change; sign-up free before plan change | 9, 11, 13, 15; `order_uniqueness` reports replay 13/9/11/15 identical | same |

- `prerequisite_closure`: edges, kinds, forms equal; flip and `edge_load_bearing` figures (12.15 / 133.24 & 12.15 / gate) equal to the frozen runs.
- `factor_sensitivity` / `baseline_result`: all 21 figures and 4 baselines equal; the round-1 half-cent tie (12.415) no longer occurs (concession substitution now 12.45 exactly).
- `design_rationale` assertions re-checked: "two of them billed at the full contract rate" (`29f0ca62…`, `94a54dd6…` at 13.29) true; reliance 0.455 true. Its sign-up near-miss ("the 2026-10 cycle is still running and is not a completed cycle") names a cycle with no record in the world — not false, but not a record-level near-miss; the computation's genuine near-miss is the seven off-peak lines excluded from the cycle count (observation).
- Closest alternatives excluded as in round 1 (largest vs latest line, off-peak lines as cycles, price-sheet rate, renewal-style start date).
- Verdicts: policy self-consistency PASS; problem tree PASS; factors PASS; unique solution PASS.

### findings (revision_2)
- F-T1-1 / F-1 (round 1 SOURCE-FACTOR RED): **closed**. Evidence: dispute fee return now "the night-usage reliance is the agreement's off-peak kWh taken as a share of all the kWh on its energy charge lines; at a reliance of 0.40 or more … from 0.20 … below 0.20 nothing"; systemic error courtesy now "the agreement's off-peak energy lines billed at the full contract rate are counted; with three or more … exactly two … only one nothing"; rebill fee return now "the over-billed amount of the corrected line decides …" with no fee-line condition. Each ladder's tiers are reachable by customers who reach the write (`_difficulty.md` revision_2 § factor_ladders); on this world each bears weight (190.28 / 197.23 / 128.29 vs 200.23 / 138.24).
- O-1, O-2, O-3, O-12 closed for this world; O-13, O-14 (new, latent) not exercised; O-5, O-9 unchanged observations.
- No regression: sign-up and rebill figures unchanged; plan-change rate moves only through the declared factor change.
