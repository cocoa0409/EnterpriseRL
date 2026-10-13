# Policy-task audit — residential_electricity_care / task 0

## source_derivation_frozen

- Freeze time: 2026-10-04T16:30Z (round 1). Auditor: independent policy-task auditor (Claude agent, erl-task-policy-audit).
- Freeze hashes: `task_0.view.json` = `7857bd0fa994ac65dec408a36b161ff0c310f79016577a93f7382699b9212bdf`; charter `5266e76b…bdf`; tools `8cc6224c…7cf` (see `_difficulty.md` § charter_global_frozen).
- Fields permitted: `task_index`, `frozen_time` (2026-09-24 10:15 EDT), `user_scenario`, `initial_state` from the masked view; the charter, tools, blueprint.
- Fields masked (not read before this section was written to disk): `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, every worklog and other audit.
- contamination_disclosure: none. No task JSON, worklog or recursive search over the tasks directory was opened; all reads were by explicit path.
- Arithmetic was cross-checked with a temporary script that evaluated the charter's own `compute` lines with the DSL of `check_compute.py` on the masked `initial_state` plus the auditor's own derived writes (script deleted after use).

### policy_self_consistency (this task only)

- Charter-global conclusions cited, not restated: `_difficulty.md` § override_declarations (no undeclared override reaching a scored quantity), § rule_compute_equivalence (dual-fuel, renewal, referral, loyalty equivalent), § prerequisite_graph and § prerequisite_sentences (edges 1–3 pass; O-7 fallback observation), § action_binding_and_uuids.
- O-8 (renewal-rate sentence vs "0.00 earns none") does not bear here: the agreement is on Beacon Ridge Price Lock 24, `dual_fuel_credit_usd_per_cycle: 5.00`.
- Handling time: every write is evaluated at `NOW` = 2026-09-24 on the world "initial_state + the preceding writes of this tree"; the renewal rate is computed after the dual-fuel restoration, the loyalty credit after the acceptance and the referral credit.
- No real-world wait: every input is a seeded record (`power_billing`, `power_notices`, `power_agreements`, `gas_agreements`, `gas_billing`) or a preceding write; the acceptance is the customer's own immediate action at hand-over ("when they hand the acceptance over to you, you complete it yourself right then"). The referred customer's qualification (two completed cycles, July and August 2026, both ended before `frozen_time`) is already in the records.

### problem_chain

Walked from the root:

1. Root — customer: "you want that loyalty credit put on your electricity account". Policy `power_ext_renewal_loyalty_credit`. Its rule carries two prerequisite sentences:
   - (a) "The renewal loyalty credit is not posted until the customer's acceptance of the renewal offer is recorded on the agreement." At opening `power_agreements/ef419fc4…` has `plan_change_date: ""`, `contract_end_date: 2026-10-31`, `term_months: 24` (the original term from `service_start_date 2024-11-01`) — no acceptance recorded. → `power_ext_renewal_rate` (tool `accept_renewal_offer_e5d86473`, owner=user). kind value_input (`renewed_term_months` cannot be counted without the new term's dates).
   - (b) "The renewal loyalty credit is fixed only after the agreement's bill lines carry the referral credit owed for every referred customer whose agreement has reached the qualifying number of completed cycles." `power_agreements/b1a11f95…` (Owen Castillo) has `referred_by_customer_id: 62b11348…` (Diane), `service_start_date 2026-07-01`, energy lines for cycles 2026-07-01 and 2026-08-01 (both `billing_period_end` before 2026-09-24) → 2 completed cycles = `referral_qualifying_cycles` 2 → qualified; no `power_billing` row with `line_type: referral_credit` exists → unmet. → `power_ext_referral_credit_amount` (tool `post_referral_credit_79c21554`). kind value_input (`loyalty_referral_lines`, and the line also enters the spend sum).
2. `power_ext_renewal_rate` rule sentence 2: "The renewal rate is fixed only after the agreement's bill lines carry a dual-fuel credit for every billing cycle within the billing dispute lookback on whose start date a Beacon Ridge gas agreement on the same premise was active." Gas `59376ab3…` on premise `8d51d1ec…` is `active`, `service_start_date 2025-02-01`. `power_billing` of `ef419fc4…` carries `dual_fuel_credit` lines for every cycle 2025-02-01 … 2026-06-01 and 2026-08-01, but none for 2026-07-01 (energy line `be1cbea6…`, posted 2026-08-03, inside the 12-month lookback) → unmet. → `power_ext_dual_fuel_restoration` (tool `post_dual_fuel_credit_18175409`). kind value_input (`credited_bundle_cycles`). The in-progress cycle 2026-09-01 has no bill yet and nothing has been "missed" on it; not part of the condition.
3. `power_ext_dual_fuel_restoration` and `power_ext_referral_credit_amount` carry no prerequisite sentence.

Derived tree: loyalty ← {renewal acceptance ← dual-fuel restoration, referral credit}; 3 prerequisite problems, 3 value_input edges (≥ max(3−1,1)=2), acyclic, one owner=user write (acceptance). Isomorphic to the declared `prerequisite` edges in the charter.

Topological constraints: dual-fuel → acceptance → loyalty; referral → loyalty. The order of the referral relative to the dual-fuel restoration and to the acceptance is not fixed by any sentence.

Load-bearing runs (recomputed):
- Skip dual-fuel restoration: renewal rate 10.63 instead of 10.42 (bundle count 10 → partial tier).
- Skip acceptance: no new term — `renewed_term_months` has no start date; the loyalty credit is not postable (sentence (a)).
- Skip referral: loyalty 106.00 instead of 116.00 (referral loyalty bonus 0; spend 1243.01 stays in the mid tier).

Parallel-edge test (sibling prerequisites of the root: acceptance and referral):
- The acceptance overwrites `contract_end_date` 2026-10-31 → 2028-10-31. The referral computation's renewal-season scaling reads that field ("when the referring agreement's contract end date is 1 to 60 calendar days after the posting date …").
- Order referral → acceptance: `DAYS(2026-09-24, 2026-10-31)` = 37 → near-renewal factor 1.25 → referral credit **92.50**.
- Order acceptance → referral: `DAYS(2026-09-24, 2028-10-31)` = 768 → "further away" → factor 1 → referral credit **80.00**.
- Loyalty under either order: 116.00 (spend 1150.51 vs 1163.01, both 1,000–1,250 → mid). Terminal states differ in the referral line's amount (and its line id, which hashes the amount).
- No rule orders these two: the loyalty rule's two prerequisite sentences each order one sibling before the root only; the referral rule and the renewal rule say nothing about each other. Both orders are compliant → two defensible terminal states. **SOURCE-CHAIN RED (two solutions on parallel edges)**, see findings.

No-wait argument: all three prerequisites are writes the agent/customer performs now on seeded facts. Tool bodies (`task_tools.py` lines 33–129) perform an unconditional update/create — no tool judges a prerequisite.

Customer-owned write: `accept_renewal_offer_e5d86473` (owner=user); persona hands it over passively ("when they hand the acceptance over to you, you complete it yourself right then and read back what it confirms").

### task_independent_derivation

User need and authorisation: the customer asks only for the loyalty credit ("you are not calling about anything else"); she authorises the agent to post credits ("You are fine with the representative posting any credits that belong on your account without asking you each time"); she will accept the renewal personally once told it is required and accepts "the plan, rate and dates exactly as the representative states them"; she raises no prerequisite herself (Owen, the summer credit and the gas are mentioned only "if the representative brings up / mentions / asks"). "You have already made up your mind to keep your electricity with Beacon Ridge" states her intent, not a step. Closing: she ends the call once told the loyalty credit has been posted — the root's write.

Identity: `find_customers(phone_number=2155550104)` → `62b11348…`; `verify_customer_identity(customer_id, phone_number=2155550104, tax_id_last4=1427)` → 2 matches.

Now / wait / refuse: act now. Agreement active; election on 2026-09-24, before `contract_end_date` 2026-10-31 (base `power_renewal`: new term starts the day after); renewal notice `22a63554…` (initial, 2026-09-01 = 60 days before end, compliant, email) offers Beacon Ridge Price Lock 24 at 11.89.

Writes in topological order (one of the two compliant orders; see problem_chain):

1. `post_dual_fuel_credit_18175409` (agent) — handling time: opening world.
   - Object: agreement `ef419fc4-5fe7-4983-83af-af7ef0abd8fd`, cycle `billing_period_start 2026-07-01`, `referred_customer_id ""`.
   - per-cycle 5.00 (Price Lock 24); bundle uplift: gas Price Lock 24 `rate_type fixed`, `term_months 24` → long 2.00; compensation: dual-fuel lines with cycle start < 12 whole months before 2026-09-24 = 2025-10-01 … 2026-06-01 (9) + 2026-08-01 = 10 → ≥10 established ×1.5 → 10.50 (near-miss: 2025-09-01 line, 12 whole months, excluded); tenure `MONTHS(2024-11-01, 2026-09-24)` = 22 → mid +0.50; usage: 11 energy lines 2025-10 … 2026-08, 11,076 kWh, avg 1,006.9 → high +1.00 (2025-09 line 958 kWh excluded); paperless: web + 1 email notice → full +0.50.
   - `credit_amount_usd` = RND(10.50 + 0.50 + 1.00 + 0.50) = **12.50**.
2. `accept_renewal_offer_e5d86473` (user, handed over) — handling time: after write 1.
   - offered rate 11.89; tenure 22 → mid 0.25; credited bundle cycles now 11 → full 0.30; expiring term `MONTHS(2024-11-01, 2026-10-31)+1` = 24 → long 0.20; paperless full 0.10; early election 37 days → long 0.20; combined 1.05; volume avg 1,006.9 → ×1.4 → 1.47.
   - Args: `power_agreement_id ef419fc4…`, `variant_name "Beacon Ridge Price Lock 24"`, `term_months 24`, `contract_rate_cents_kwh` = 11.89 − 1.47 = **10.42**, `plan_change_date 2026-11-01`, `contract_end_date 2028-10-31` (day before 2028-11-01).
   - Contrast on the opening world (without write 1): 10.63.
3. `post_referral_credit_79c21554` (agent) — handling time: depends on the order (see problem_chain).
   - Object: referring agreement `ef419fc4…` (Diane's earliest-enrolled, only active agreement), `referred_customer_id 7e95608f-7677-4524-b1a6-342404cae2f5`, `billing_period_start 2026-09-01` (cycle in progress on 2026-09-24; cycles run calendar months, next read 2026-10-01).
   - plan referral credit 50.00; season: before acceptance 37 days → ×1.25 = 62.50, after acceptance 768 days → 50.00; gas active + fixed → +10.00; no referral line yet → first +10.00; 22 energy lines → seasoned +5.00; web + email → +5.00.
   - `credit_amount_usd` = **92.50** (posted before the acceptance) or **80.00** (posted after it). The auditor cannot select one from the policy.
4. `post_renewal_loyalty_credit_25af361b` (agent) — handling time: after writes 1–3.
   - Object: `ef419fc4…`, `referred_customer_id ""`, `billing_period_start 2026-11-01` ("the billing cycle that starts with the new term").
   - plan loyalty 50.00 (Price Lock 24); renewed term `MONTHS(2026-11-01, 2028-10-31)+1` = 24 → ×1.2 = 60.00; tenure 22 → ×1.10 = 66.00; gas active, 19 gas energy lines → established +20.00; net billed (posted < 12 whole months before 2026-09-24): energy 1,310.51 − 11 dual-fuel lines 55.00 − restored 12.50 − referral (92.50 | 80.00) = 1,150.51 | 1,163.01 → mid +10.00 (near-miss: lines posted 2025-09-03, 12 whole months, excluded; including them would give ≥1,250 → high); one referral line → +10.00; gas therms of cycles 2025-10 … 2026-08 = 810 → high +10.00.
   - `credit_amount_usd` = **116.00** under either order.

Terminal state: agreement on Price Lock 24 at 10.42, term 2026-11-01 – 2028-10-31, active; new bill lines: dual-fuel −12.50 (2026-07-01), referral −92.50 or −80.00 (2026-09-01, Owen), renewal loyalty −116.00 (2026-11-01).

Context closure: every input is reachable — `find_power_agreements(customer_id)` / `(referred_by_customer_id=62b11348…)`, `find_power_billing(power_agreement_id)`, `find_power_notices(power_agreement_id)`, `find_gas_agreements(premise_id|customer_id)`, `find_gas_billing(gas_agreement_id)`, `find_premises`; plan parameters from the charter.

### factor_weight

Per computation; each figure is the result with that factor's `baseline` substituted and everything else unchanged (auditor's recomputation).

**Dual-fuel restoration (gold-candidate 12.50; whole baseline 5.00 = baseline.rule "the per-cycle dual-fuel credit of the electricity plan in force").**
- bundle_uplift (P, cross-difficulty gas): tier long — gas `59376ab3…` Price Lock 24 (`fixed`, 24); baseline 0.0 → 9.50.
- restoration_compensation (M): tier established — 10 dual-fuel lines in window; baseline ×1 → 9.00.
- tenure_addition (P): tier mid — 22 whole months; → 12.00.
- usage_addition (P): tier high — avg 1,006.9 kWh; → 11.50.
- paperless_addition (P, multi-source): tier full — `enrollment_channel web` × notice `22a63554…` `delivery_channel email`; → 12.00.
- Near-miss: dual-fuel line 2025-09-01 and energy line 2025-09-01 (12 whole months; excluded by "less than twelve whole months").

**Renewal rate (10.42; whole baseline 11.89 = offered rate of the latest notice).**
- tenure (P) mid → 10.77; bundle (P) full (11 lines after restoration) → 10.84; commitment (P) long (24) → 10.70; paperless (P, multi-source) full → 10.56; early_election (P) long (37 days) → 10.70; volume_scaling (M) high → 10.84.
- Near-miss: the 2025-09-01 dual-fuel and energy lines (excluded).

**Referral credit (92.50 or 80.00; whole baseline 50.00).** Under the referral-first order:
- renewal_season_scaling (M): near (37 days) → 80.00; referrer_bundle_bonus (P, cross gas): fixed → 82.50; referral_count (P): first → 82.50; seasoned (P): 22 lines → 87.50; paperless (P, multi-source) full → 87.50.
- Under the acceptance-first order the season factor sits on its fall-through (768 days) and does not bear weight (80.00 = its own baseline substitution).
- Near-miss: the referred customer's own agreement `b1a11f95…` (phone enrollment, no notices, 2 energy lines, end 2027-06-30, no gas at its premise) — a reader who evaluates the bonuses on the referred side lands on different tiers; the rule's "the referring agreement" excludes it.

**Renewal loyalty credit (116.00; whole baseline 50.00).**
- renewed_term_scaling (M) long (24) → 105.00; loyalty_tenure_scaling (M) mid → 110.00; bundle_loyalty (P, cross gas, multi-source: `gas_agreements.status` × `gas_billing` count 19) → 96.00; spend (P) mid → 106.00; referral_loyalty (P) single → 106.00; whole_home (P, cross gas XSUM 810 therms) → 106.00.
- Near-miss: lines posted 2025-09-03 (energy 134.06, dual-fuel −5.00) excluded from the 12-month spend window — including them moves spend to the high tier; gas line 2025-09-01 (24 therms) excluded from the therm window.

Stamps: no field names a tier outcome. `premises.annual_therm_usage 742` (≥700) and `annual_kwh_usage 12302` (≈1,025/month ≥1,000) agree with the whole-home, usage and volume tiers taken (observation; the ladders rest on the ledgers).

Counts surviving the tests: dual-fuel 5 (4P/1M), renewal 6 (5P/1M), referral 5 (4P/1M), loyalty 6 (4P/2M); multi-source present (paperless ×3, bundle_loyalty); cross-difficulty present (gas, seeded: holding `59376ab3…` and 20 `gas_billing` rows).

Factor verdict (pre-reveal): every factor bears weight on this world (except the referral season factor under the acceptance-first order, which is part of the order defect, not a separate one).

## findings

### F-T0-1 — SOURCE-CHAIN RED + SOURCE-TASK RED: two compliant orders of the sibling prerequisites give two referral credits

- Symptom: the referral credit and the renewal acceptance are both prerequisites of the loyalty credit; the policy orders each before the root but not against each other, and the acceptance changes an input the referral computation reads.
- Root cause: `power_ext_referral_credit_amount` rule "Renewal-season scaling: when the referring agreement's contract end date is 1 to 60 calendar days after the posting date, the plan referral credit is multiplied by the near-renewal season factor; … when it is further away … taken as it stands." reads `power_agreements.contract_end_date`, which `accept_renewal_offer_e5d86473` overwrites (`ctx.update(... contract_end_date=...)`, `task_tools.py` line 33). No sentence of the loyalty, renewal or referral rule orders the referral credit relative to the acceptance (`_difficulty.md` § prerequisite_sentences).
- Evidence: `power_agreements/ef419fc4…contract_end_date = 2026-10-31`; `frozen_time 2026-09-24`; renewal to Price Lock 24 sets it to 2028-10-31.
- Demonstrated consequence: referral first → 37 days → ×1.25 → `credit_amount_usd` 92.50; acceptance first → 768 days → ×1 → 80.00. Loyalty 116.00 in both. Two defensible terminal states for the referral line.
- Affected: `power.extended.yaml` → `power_ext_renewal_loyalty_credit.prerequisite` / rule (sibling edges unordered) and `power_ext_referral_credit_amount` rule (season scaling); scored argument `post_referral_credit_79c21554.credit_amount_usd` and the write order in `evaluation_criteria`.
- Previous revisions: none (round 1).

### Observations
- O-7 (`_difficulty.md`): the acceptance edge's action-form fallback is not fully justified.
- Stamp-adjacent `premises.annual_*_usage` agree with three tiers.
- The referral computation's only near-miss is the referred customer's own agreement.

## source_gt_comparison

- Reveal time: 2026-10-04T16:24:58Z (first command that opened `tasks/0.json`). Timestamp note: the "Freeze time" line above (16:30Z) was an estimate written into the file; the file's actual write time is 16:24:03Z (`stat`), i.e. the frozen section was on disk before the reveal. The frozen text is left untouched.
- Revealed: `evaluation_criteria` (19 actions), `computations` (4), `charter_scope`, `required_documents`, `prerequisite_closure`, `design_rationale`, `solvability_contract`.

| item | frozen derivation | GT | same? |
| --- | --- | --- | --- |
| need / authorisation / timing | loyalty credit only; agent posts credits; customer accepts renewal personally on hand-over; act now | same (`solvability_contract.request_alignment`, step 16 owner=user) | same |
| necessary reads | customer, premise, agreement, bill lines, notices, gas agreement + ledger, referred-by lookup, Owen's lines | same set (steps 0–10; GT also reads Owen's premise) | same |
| now / wait / refuse | act now | act now | same |
| scope | {loyalty, renewal_rate, dual_fuel_restoration, referral} | `charter_scope.extended_policies` identical | same |
| dual-fuel restoration | `ef419fc4…`, `""`, 2026-07-01, 12.50 | step 12: same, 12.5 | same |
| referral credit | `ef419fc4…`, Owen `7e95608f…`, 2026-09-01, **92.50 or 80.00 (order-dependent)** | step 14: 92.5, posted before the acceptance | GT took one of the two compliant orders |
| renewal acceptance | PL24, 24, 10.42, 2026-11-01, 2028-10-31 (user) | step 16: identical, owner user | same |
| loyalty credit | `ef419fc4…`, `""`, 2026-11-01, 116.00 | step 18: identical | same |
| write order | dual-fuel → acceptance → loyalty; referral anywhere before loyalty | 12 dual-fuel, 14 referral, 16 acceptance, 18 loyalty | consistent with one of the compliant orders |
| terminal state | as derived (referral amount order-dependent) | referral −92.50 | differs from the acceptance-first order |

Problem tree vs `prerequisite_closure` (value against value):
- Edge renewal_rate → dual_fuel: GT `value_input`, gate `credited_bundle_cycles`, state; why-false rows `be1cbea6…` (2026-07-01, no dual-fuel twin), `2a84bfe9…`/`f21b0a2a…` neighbours, gas `59376ab3…` from 2025-02-01; flip 10 → 11, 0.15 → 0.30 — equal to the frozen derivation (10 → 11; rate 10.63 → 10.42).
- Edge loyalty → renewal_rate: action form, `plan_change_date ''`, `contract_end_date 2026-10-31`, flip to 2026-11-01 / 2028-10-31 / 10.42 — equal.
- Edge loyalty → referral: Owen `b1a11f95…` referred_by Diane, cycles ending 2026-07-31 and 2026-08-31, no referral line; flip: count 1, net −92.50 — equal.
- `edge_load_bearing`: 10.63, "loyalty compute raises / no renewed term", 106.00 — equal to the frozen runs.
- `resolution_order` [restoration, referral, renewal_rate, loyalty] — one of the compliant orders.
- **`order_uniqueness` is false as asserted.** It states: "The only free pair is the restoration (step 12) and the referral credit (step 14) … Every other order is pinned by the prerequisite sentences: the renewal rate waits on the dual-fuel credits, and the loyalty credit waits on the acceptance and on the referral credit." The pair (referral, acceptance) is not pinned by any sentence — the acceptance waits only on the dual-fuel credits and the referral waits on nothing — and swapping it changes the referral credit from 92.50 to 80.00 (recomputed on the world after steps 12 and 16: `DAYS(2026-09-24, 2028-10-31)` = 768 → season factor 1). This is the proof field of the parallel-edge relationship, and it asserts a world fact that recomputation contradicts.

Factors vs `computations[].factor_sensitivity` and `baseline_result` (figure against figure):
- Dual-fuel: GT 9.5 / 9.0 / 12.0 / 11.5 / 12.0, baseline 5.0 — auditor 9.50 / 9.00 / 12.00 / 11.50 / 12.00, 5.00. Equal.
- Referral: GT 80.0 / 82.5 / 82.5 / 87.5 / 87.5, baseline 50.0 — auditor (referral-first world) equal.
- Renewal rate: GT 10.77 / 10.84 / 10.7 / 10.56 / 10.7 / 10.84, baseline 11.89 — equal.
- Loyalty: GT 105.0 / 110.0 / 96.0 / 106.0 / 106.0 / 106.0, baseline 50.0 — equal.
- Tiers taken: identical to the frozen tiers. GT's near-miss statement (2025-09-01 dual-fuel line) equals the frozen one.

Closest alternative candidate and its exclusion: for the referral amount, the closest candidate is 80.00 (acceptance before referral). **No policy or world evidence excludes it** — "GT chose this one" is the only ground, which the audit does not accept. Every other scored value has no defensible alternative (dual-fuel cycle forced by the only gap; renewal plan/term/dates forced by the notice and base date rules; loyalty value equal under both orders).

Verdict per relationship:
- Policy self-consistency: PASS (charter-global observations only; `_difficulty.md`).
- Problem tree holds: **SOURCE-CHAIN RED** — two solutions on parallel edges (F-T0-1); the closure's `order_uniqueness` asserts the contrary.
- Factors bear weight: PASS (every factor off its fall-through and load-bearing on the GT world; baselines honest; multi-source and cross-difficulty present and seeded).
- Unique solution: **SOURCE-TASK RED** — the second reading (acceptance first) yields `credit_amount_usd` 80.00 for `post_referral_credit_79c21554`, as defensible under the published policy as GT's 92.50.

### F-T0-1 (confirmed after reveal)
- Relation to GT: GT encodes the referral-first order (step 14 before step 16) and 92.50; `prerequisite_closure.order_uniqueness` and the `design_rationale` "[Problem-tree card] … Free pair restoration/referral commutes" both omit the referral/acceptance pair. Affected artifact and location: `power.extended.yaml` (`power_ext_renewal_loyalty_credit` prerequisite sentences leave the siblings unordered; `power_ext_referral_credit_amount` renewal-season scaling reads the field the acceptance rewrites); `tasks/0.json` → `evaluation_criteria[14].arguments.arguments.credit_amount_usd`, `computations[policy_id=power_ext_referral_credit_amount]`, `prerequisite_closure.order_uniqueness`.

## revision_2

### source_derivation_frozen (revision_2)

- Written 2026-10-04 (round 2) before `tasks/0.json` of round 2 was opened. View hash `7857bd0f…12bdf` = round 1 (world and persona unchanged); charter `0e643c9e…a24ad5` and tools `b09d2f32…94d13` changed → every per-task section re-derived.
- contamination_disclosure: the round-1 GT of this task was read in round 1 (§ source_gt_comparison above). The figures below are recomputed from the round-2 charter on the view; they are not copied from round 1.

#### policy_self_consistency (round 2)
- Cites `_difficulty.md` § revision_2 (override_declarations, rule_compute_equivalence, prerequisite_sentences: edges 1–3 pass; O-15 not reachable here).
- O-8 closed; does not bear here anyway (Price Lock 24 pays 5.00/cycle).
- Handling time / no wait: unchanged from round 1.

#### problem_chain (round 2)
- Root loyalty rule, sentence (a) now: "The renewal loyalty credit is not posted until the agreement's current term starts on the day after the contract end date stated on its latest renewal notice, on the plan that notice offers." Latest renewal notice `22a63554…`: `effective_date 2026-10-31`, `offered_variant_name Beacon Ridge Price Lock 24`. Agreement `ef419fc4…`: `plan_change_date ""` → current term starts at `service_start_date 2024-11-01` ≠ 2026-11-01 → unmet. Writer: the acceptance (base renewal: new term the day after contract end, offered plan); a plan change cannot produce it (offered plan = current plan, and a change requested on 2026-09-24 takes effect 2026-10-01). → `power_ext_renewal_rate`, value_input.
- Sentence (b) (referral), renewal-rate sentence (dual-fuel, now "the dual-fuel credit owed" — Price Lock 24 pays 5.00 and gas `59376ab3…` is active, so the 2026-07-01 cycle is owed): unmet exactly as in round 1.
- Tree: unchanged (3 prerequisite problems, 3 value_input, owner=user acceptance, acyclic).
- Load-bearing: skip dual-fuel → renewal 10.63; skip acceptance → no renewed term, loyalty not postable; skip referral → loyalty 106.00.
- **Parallel-edge test (round-1 F-T0-1):** referral computation now reads `LATEST(power_notices.effective_date)` = 2026-10-31 → `DAYS(2026-09-24, 2026-10-31)` = 37 → near ×1.25 under both orders. Recomputed: referral before acceptance = 92.50; after acceptance (agreement end date rewritten to 2028-10-31, notice untouched) = 92.50. Loyalty 116.00 under both. Dual-fuel / referral pair independent as before. → one terminal state for every compliant order.
- Tools: bodies unchanged; none judges a prerequisite.

#### task_independent_derivation (round 2)
Writes (any topological order; referral may sit anywhere before the loyalty credit):
1. `post_dual_fuel_credit_18175409`: `ef419fc4…`, `""`, `2026-07-01`, credit **12.50** (unchanged formula and inputs).
2. `accept_renewal_offer_e5d86473` (user, handed over): Price Lock 24, 24, rate **10.42**, `2026-11-01`, `2028-10-31`.
3. `post_referral_credit_79c21554`: `ef419fc4…`, Owen `7e95608f…`, `2026-09-01`, credit **92.50** (50.00 × 1.25 + 10 gas fixed + 10 first + 5 seasoned + 5 paperless), order-independent.
4. `post_renewal_loyalty_credit_25af361b`: `ef419fc4…`, `""`, `2026-11-01`, credit **116.00**.
Persona, identity, authorisation, closure: unchanged and passing (round-1 analysis stands; the view is byte-identical).

#### factor_weight (round 2)
- Dual-fuel: 9.50 / 9.00 / 12.00 / 11.50 / 12.00; baseline 5.00.
- Renewal: 10.77 / 10.84 / 10.70 / 10.56 / 10.70 / 10.84; baseline 11.89.
- Referral: season (near, from the notice's 2026-10-31) 80.00; bundle 82.50; count 82.50; seasoned 87.50; paperless 87.50; baseline 50.00. Season factor now bears weight under every order.
- Loyalty: 105.00 / 110.00 / 96.00 / 106.00 / 106.00 / 106.00; baseline 50.00.
- Near-misses as in round 1; referral's renewal-season evidence now also has a near-miss: the agreement's own `contract_end_date` (rewritten to 2028-10-31 by the acceptance) — the rule excludes it ("whose stated contract end date stays as printed whatever renewal … the agreement records").
- Multi-source and cross-difficulty floors hold (unchanged).
- Pre-reveal verdict: PASS on all four relationships.

### source_gt_comparison (revision_2)

- Reveal time: 2026-10-04T17:42:38Z (after the revision_2 freeze above, written 17:42:31Z).
- Item by item:

| item | frozen (round 2) | GT (round 2) | same? |
| --- | --- | --- | --- |
| scope | {dual_fuel, referral, renewal_rate, loyalty} | `charter_scope` identical | same |
| dual-fuel | `ef419fc4…`, `""`, 2026-07-01, 12.50 | step 12 identical | same |
| referral | `ef419fc4…`, Owen, 2026-09-01, 92.50, any order | step 14 identical | same |
| acceptance (user) | PL24, 24, 10.42, 2026-11-01, 2028-10-31 | step 16 identical, owner user | same |
| loyalty | `ef419fc4…`, `""`, 2026-11-01, 116.00 | step 18 identical | same |
| order | dual-fuel → acceptance → loyalty; referral free before loyalty | 12, 14, 16, 18; `order_uniqueness` names both free pairs and reports a replay of 12/16/14/18 with identical values and terminal hash | same (auditor's own recomputation of the swapped order also gives 92.50) |

- `prerequisite_closure` vs frozen tree: three edges, kinds and forms equal (acceptance edge now `state`); flip figures 10 → 11 / 0.15 → 0.30, the renewed term 2026-11-01 – 2028-10-31, referral count 1 and net −92.50 equal; `edge_load_bearing` 10.63 / no renewed term / 106.00 equal.
- `factor_sensitivity` and `baseline_result`: all 22 figures and 4 baselines equal to the frozen recomputation.
- `order_uniqueness` (round 1 false assertion) is now true on recomputation.
- Closest alternative: the acceptance-first order — now yields the same referral credit (the renewal season is read from the notice the acceptance does not write); excluded as a distinct answer.
- Verdicts: policy self-consistency PASS; problem tree PASS; factors PASS; unique solution PASS.

### findings (revision_2)
- F-T0-1 (round 1 SOURCE-CHAIN RED + SOURCE-TASK RED): **closed**. Evidence: referral rule "Renewal-season scaling: the renewal season is read from the latest renewal notice on the referring agreement, whose stated contract end date stays as printed whatever renewal or plan change the agreement records"; compute `season_notice_end_date = LATEST('power_notices','effective_date', …)`; `accept_renewal_offer_e5d86473` writes only `power_agreements`; both orders recompute to the same referral credit and terminal state.
- O-7 closed (acceptance edge in state form). O-15 (new, `_difficulty.md`) not reachable in this world.
- No regression: dual-fuel, renewal rate and loyalty figures, persona, identity and closure unchanged.
