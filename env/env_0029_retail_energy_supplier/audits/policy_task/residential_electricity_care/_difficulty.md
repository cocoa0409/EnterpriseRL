# Policy-task audit — residential_electricity_care / charter-global

## charter_global_frozen

- Freeze time: 2026-10-04T16:21:15Z (round 1). Auditor: independent policy-task auditor (Claude agent, erl-task-policy-audit), not the author of the artifacts.
- Freeze hashes (sha256, recomputed by the auditor and equal to `.audit_views/policy_task/residential_electricity_care/HASHES.txt`):
  - `tasks/residential_electricity_care/power.extended.yaml` = `5266e76b034f9a61117e86f4daef809fa4ff9d7bdc514e7d9d1bcc720b8af20d`
  - `tasks/residential_electricity_care/task_tools.py` = `8cc6224cb27c8c68f7d8619cff875ae6a4fd70cc2641cf7efd9672f769be87cf`
  - `task_0.view.json` = `7857bd0f…12bdf`, `task_1.view.json` = `4aab36da…6aae72`
- Fields permitted: the whole extended charter (base section + `extended_policies`), `task_tools.py`, `blueprint/{blueprint.yaml, db_schema.json, share_tools.py, products/power.yaml, products/gas.yaml}`, the DSL semantics in `skills/erl-task-instantiate/scripts/check_compute.py` (`MONTHS`, `DAYS`, `COUNT`/`SUM`/`MAX`/`LATEST` holding scope, `CPARAM`/`CFIELD`/`X*` customer scope), and the two masked views (`task_index`, `frozen_time`, `user_scenario`, `initial_state`).
- Fields masked and not read while writing this section: everything in `tasks/residential_electricity_care/tasks/*.json` beyond the views (`evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`), every worklog, every other audit.
- Nothing in this section is derived from a revealed GT; it was written before either task's GT was opened.
- Entry conditions (Step 0): the orchestrator supplied the gate snapshot (EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; CACHE-DIFF INFO; SCOPE OK; traceability deferred until the KB is published), the masked views and their hashes. Input is complete; the auditor did not re-run the gates.
- Base copy: `diff <(sed -n 1,1242p power.extended.yaml) blueprint/products/power.yaml` differs only by one trailing blank line — the base section is verbatim.

### policy_conflict_scan

Eight extended policies, two problem trees (read from the `prerequisite` graph and the two personas; the claimed `charter_scope` is masked and is compared after the reveal):

| tree | root (customer's ask) | prerequisite problems |
| --- | --- | --- |
| A (task 0 persona: "you want that loyalty credit put on your electricity account") | `power_ext_renewal_loyalty_credit` | `power_ext_renewal_rate` (owner=user tool `accept_renewal_offer_e5d86473`), `power_ext_dual_fuel_restoration` (via the renewal rate), `power_ext_referral_credit_amount` |
| B (task 1 persona: "move your home electricity from Free Nights to the plain twelve-month Price Lock") | `power_ext_plan_change_rate` (owner=user tool `change_plan_fbee8941`) | `power_ext_offpeak_rebill_credit`, `power_ext_offpeak_dispute_amount` (via the rebill), `power_ext_signup_credit_amount` |

- Scopes: {loyalty, renewal_rate, dual_fuel_restoration, referral} and {plan_change, rebill, dispute, signup} are disjoint and together cover all eight extended policies. No `prerequisite` edge crosses between the two trees.
- Overlapping subjects: four policies write `power_credit` (dual-fuel, referral, loyalty, sign-up) through four distinct tools, each fixing its own `line_type`; two write `power_adjustment` (dispute → `power_billing_disputes`, rebill → `power_billing`); `power_renew` and `power_plan_change` are written by two distinct owner=user tools. No two policies compute the same quantity on the same tool.
- Triggers / eligibility / time anchors: every extended policy inherits the base eligibility of its base refs (renewal: active only, on/before `contract_end_date` → new term starts the next day; plan change: active, equal-or-longer term; credits: active or drop_pending; corrections: 12-month lookback, one correction per line). Handling time of every computation is `NOW` (frozen date) — "restoration date", "election date", "posting date", "referral date", "correction date", "change request" all bind to `NOW`.
- Cross-category read boundary: every extended policy reads only the gas holding/ledger of the same customer (CPARAM/CFIELD filtered by `premise_id`; XCOUNT/XSUM customer-scoped, matching the rule's "the customer's gas bill lines").
- Interaction across problems inside one tree (the input to the parallel-edge test of each task file):
  - Tree A: the renewal acceptance overwrites `power_agreements.contract_end_date`, and the referral computation's renewal-season scaling reads exactly that field ("when the referring agreement's contract end date is 1 to 60 calendar days after the posting date…"). The referral and the renewal acceptance are sibling prerequisites of the loyalty credit and no sentence of any rule orders them. Whether this produces two terminal states is a fact about one world — demonstrated in `task_0.md`.
  - Tree B: the sign-up computation reads energy lines, gas status and gas sign-up lines; the dispute/rebill/plan-change computations read off-peak/on-peak energy lines, fee lines, disputes and rebill lines. None of the sign-up branch's writes is read by the dispute/rebill branch or vice versa; only the root reads both rebill lines and open disputes, and both are ordered before it.

### rule_compute_equivalence

Each binding's `compute_basis` quotation was checked verbatim against the policy's `rule`, then each rule sentence was swept back against `compute`.

- `power_ext_dual_fuel_restoration`: per-cycle credit `P('dual_fuel_credit_usd_per_cycle')` ("plan in force"); bundle uplift from gas `rate_type`/`term_months` (three tiers, rule = compute); compensation count `COUNT(dual_fuel_credit, within_months=12, billing_period_start)` = "billing cycle started less than twelve whole months before the restoration date" (`0 ≤ MONTHS(bps, NOW) < 12`); tenure `MONTHS(service_start_date, NOW)`; usage average = SUM/COUNT of energy lines in the same window; paperless web/email; combination order and single final rounding — equivalent.
- `power_ext_renewal_rate`: offered rate = `LATEST(power_notices.new_rate_cents_kwh, event_type=power_renewal_notice)` ("latest renewal notice"); expiring term `MONTHS(plan_change_date or service_start_date, contract_end_date)+1` ("from the later of … through the contract end date, the end month included" — `plan_change_date`, when set, is always the later); early election `DAYS(NOW, contract_end_date)`; volume scaling on the combined reduction; final rounding — equivalent.
- `power_ext_referral_credit_amount`: season `DAYS(NOW, contract_end_date)` 1–60 / 61–180 / else; gas status+rate type; referral-line count; energy-line count (no window, as the rule says "carries"); paperless; combination — equivalent.
- `power_ext_renewal_loyalty_credit`: renewed term `MONTHS(plan_change_date, contract_end_date)+1`; tenure factor applied to the term-scaled amount (order stated); gas status + `XCOUNT(gas_billing energy_charge)` (customer scope = "the customer's gas bill lines"); net billed `SUM(amount_usd, within_months=12, posted_date)`; referral count; therms `XSUM(..., within_months=12, billing_period_start)` — equivalent.
- `power_ext_offpeak_dispute_amount`: equivalent except one binding: the rule states "that line's correctly billed amount at its kWh" for the line with the largest billed amount, while `disputed_line_kwh = MAX('power_billing','usage_kwh', off_peak)` takes the largest kWh of any off-peak line. Charter-wide the only time-of-use variant is Beacon Ridge Free Nights 12 with `offpeak_rate_multiplier: 0.00`, so the correct amount is 0.00 whichever kWh is used; the divergence cannot change a number in any charter-consistent world → observation O-1.
- `power_ext_offpeak_rebill_credit`: the rule restricts the correction to "the most recently posted off-peak energy line … whose off-peak rebill amount is within the care agent's adjustment limit"; compute's `LATEST(... off_peak)` selects the latest off-peak line without that filter. Where the latest line is itself over the limit, rule and compute pick different lines → observation O-2 (latent; the per-task file checks whether it bites).
- `power_ext_signup_credit_amount`: completed cycles = `COUNT(on_peak)+COUNT(all_hours)` = "billing cycles that carry an on-peak or an all-hours energy charge line"; late scaling on cycles beyond `signup_credit_after_cycles`; welcome from gas status + `XCOUNT(gas_billing signup_credit)`; usage per completed cycle; off-peak share — equivalent.
- `power_ext_plan_change_rate`: rate in force `F('contract_rate_cents_kwh')`; error items = rebill lines + open disputes; volume per on-peak/all-hours cycle; peak = max single on-peak/all-hours kWh; remaining whole months `MONTHS(NOW, contract_end_date)` scaling the combined reduction — equivalent.
- Every factor ladder's tiers appear as sentences of the rule and as branches of the `decides` binding, and vice versa (checked for all 44 factors).
- Rounding (charter-wide): every rule says "rounded half up"; `RND` is Python `round` on a float. No scored value of either task lands on a half-cent tie (checked in the task files); one factor-sensitivity figure does (see `task_1.md`) → observation O-3.

### action_binding_and_uuids

- `(target_tool, computes)` pairs: `post_dual_fuel_credit_18175409/credit_amount_usd`, `accept_renewal_offer_e5d86473/contract_rate_cents_kwh`, `post_referral_credit_79c21554/credit_amount_usd`, `post_renewal_loyalty_credit_25af361b/credit_amount_usd`, `open_billing_dispute_231feff0/disputed_amount_usd`, `post_rebill_credit_41f05139/rebill_amount_usd`, `post_signup_credit_3f59f0ed/credit_amount_usd`, `change_plan_fbee8941/contract_rate_cents_kwh` — each claimed by exactly one policy.
- uuid8s `e5d86473, 25af361b, 79c21554, 18175409, fbee8941, 41f05139, 231feff0, 3f59f0ed`: pairwise distinct, no shared prefix, no sequence or adjacent-value pattern.
- Owners: `accept_renewal_offer` and `change_plan` are `owner="user"` ("The account holder personally accepts / authorizes"); the six others are `owner="agent"`.
- Tool bodies (lines 33–243 of `task_tools.py`): each performs one `ctx.update` or `ctx.create` with the arguments given; none reads a status, date, amount or another table to accept/refuse, none errors or hints — the tool layer judges no prerequisite and no eligibility (module docstring says so, and the bodies confirm it).
- Docstrings name no other tool and state no position in a sequence. The two owner=user docstrings say "Afterwards the agreement record shows …" — this describes the call's own post-state, not an order between problems (observation O-4).

### prerequisite_graph

| blocked policy | problem | kind | gate (binding/field) | form | resolved_by = depended-on `target_tool` |
| --- | --- | --- | --- | --- | --- |
| `power_ext_renewal_rate` | `power_ext_dual_fuel_restoration` | value_input | `credited_bundle_cycles` (exists) | state | `post_dual_fuel_credit_18175409` ✓ |
| `power_ext_renewal_loyalty_credit` | `power_ext_renewal_rate` | value_input | `renewed_term_months` (exists) | action (fallback_reason present) | `accept_renewal_offer_e5d86473` ✓ |
| `power_ext_renewal_loyalty_credit` | `power_ext_referral_credit_amount` | value_input | `loyalty_referral_lines` (exists) | state | `post_referral_credit_79c21554` ✓ |
| `power_ext_offpeak_rebill_credit` | `power_ext_offpeak_dispute_amount` | value_input | `open_dispute_count` (exists) | state | `open_billing_dispute_231feff0` ✓ |
| `power_ext_plan_change_rate` | `power_ext_offpeak_rebill_credit` | value_input | `plan_error_items` (exists) | state | `post_rebill_credit_41f05139` ✓ |
| `power_ext_plan_change_rate` | `power_ext_signup_credit_amount` | state_gate | `power_billing.line_type` | state | `post_signup_credit_3f59f0ed` ✓ |

- Every policy fills `prerequisite` (`[]` on dual-fuel, referral, dispute, sign-up). Every `problem` is another extended policy id; none is a base policy or the policy itself. The graph is two disjoint DAGs (depth 2 each); acyclic.
- Every `policy_source` is a verbatim sentence of the blocked policy's own `rule` (checked by substring): renewal-rate rule sentence 2; loyalty rule sentences 2 and 3; rebill rule sentence 3; plan-change rule sentences 3 and 4.
- `form`/`fallback_reason`: present exactly on the one action-form edge.
- `condition` vs sentence: each condition restates the sentence at the same scope (every lookback cycle with active gas; every qualifying referred customer; every over-limit line; every within-limit over-billed energy line; earned sign-up credit) — neither strengthened nor weakened.
- `state_gate` `gate: power_billing.line_type` names the record field the gate reads, not an eligibility id; the gate itself is real and stated in the rule (observation O-5).
- `effect` texts are descriptive; two of them narrate one world's counts in general text ("raises the count the repeat-referral courtesy is tiered on from none to one"; "(one open dispute plus one rebill credit makes two, the multi-error tier)"). Not agent-facing (the KB carries `policy_source`, not `effect`) → observation O-6.

### prerequisite_sentences

Four-point test per edge:

1. Renewal rate ← dual-fuel restoration — "The renewal rate is fixed only after the agreement's bill lines carry a dual-fuel credit for every billing cycle within the billing dispute lookback on whose start date a Beacon Ridge gas agreement on the same premise was active." Connective "only after"; waits on a record-visible state in table words (bill lines carrying dual-fuel credit lines per cycle); no tool, id or snake_case token; scope = condition. Exactly one write of this difficulty creates a `dual_fuel_credit` line (`post_dual_fuel_credit`). Derivation: sentence + `power_billing` (per-cycle lines) + `gas_agreements` (active period) → a lookback cycle with active gas and no dual-fuel line → the dual-fuel restoration rule ("A dual-fuel credit that was missed on a past billing cycle … is restored as one dual-fuel credit line for that cycle") is the only rule whose write produces that line. Single reading.
2. Loyalty ← renewal acceptance — "The renewal loyalty credit is not posted until the customer's acceptance of the renewal offer is recorded on the agreement." Connective "not … until"; action form in business words; no tool/id. The depended-on rule ("A customer renews by accepting the offer stated in the governing renewal notice …") is the only rule performing that action. Fallback test: the fallback reason says no record-visible state singles out a renewal acceptance because a plan change writes the same fields; but the edge's own `condition` names one ("a term start date on the day after the expiring contract end date and the renewed term's contract end date") and the renewal notice's `effective_date` stays on `power_notices`, so a state of the form "the agreement's current term starts the day after the renewal notice's effective date, on the offered plan" would single the write out → fallback not fully justified, observation O-7.
3. Loyalty ← referral credit — "The renewal loyalty credit is fixed only after the agreement's bill lines carry the referral credit owed for every referred customer whose agreement has reached the qualifying number of completed cycles." State form; unique write (`post_referral_credit` is the only creator of `referral_credit` lines); derivation through `find_power_agreements(referred_by_customer_id=…)` + base `power_referral_credit` qualification + the referral-amount rule. Single reading.
4. Rebill ← dispute — "A rebill credit is not posted until every over-billed line of the agreement whose correction exceeds the care agent's adjustment limit stands as an open billing dispute." State form; unique write (`open_billing_dispute` is the only creator of open disputes); derivation via the dispute rule ("A correction larger than the care agent's adjustment limit is not posted as a rebill credit but referred to billing review as one open billing dispute on the line"). Single reading.
5. Plan change ← rebill — "The plan-change rate is fixed only after the agreement's bill lines carry a rebill credit for every over-billed energy line whose correction is within the care agent's adjustment limit." State form; unique write (`post_rebill_credit`). Single reading.
6. Plan change ← sign-up — "A plan change is not recorded until the sign-up credit the current plan has earned stands on the agreement's bill lines." State form; unique write (`post_signup_credit`). Single reading.

- No rule carries a second wording of any of these dependencies, no tool name, no other policy id; no depended-on rule restates the blocked side's sentence.
- Undeclared cross-problem order: no extended rule states an order between two problems that grounds no declared edge. The base `power_renewal` sentence placing the loyalty credit "on the first bill of the new term" is overwritten by the loyalty policy and grounds no edge. The absence of any sentence ordering the referral credit against the renewal acceptance is the subject of the parallel-edge test in `task_0.md`.

### override_declarations

Sentence-by-sentence against each `base_policy_refs` entry:

- `power_ext_dual_fuel_restoration` vs `power_agg_dual_fuel`: the per-cycle amount sentence is declared superseded; "At most one dual-fuel credit … per premise per cycle", "a gas agreement that is enrollment_pending, drop_pending or closed … does not qualify the cycle", "Missed dual-fuel credits are restored for cycles within the billing dispute lookback" are followed. "A plan with dual_fuel_credit_usd_per_cycle 0.00 earns none" is not superseded and therefore inherited (a 0.00 plan has nothing "missed" to restore). Against that inherited sentence, the renewal-rate prerequisite sentence ("carry a dual-fuel credit for every billing cycle … on whose start date a … gas agreement … was active") is unconditional: on a 0.00 plan with active gas (Price Lock 6, Free Nights 12, Monthly Variable) the renewal rate would wait on lines the plan never earns. Latent — the one renewal of this difficulty is on Price Lock 24 (5.00/cycle) → observation O-8. vs `power_signup_credit`, `power_referral_credit`, `power_renewal`: nothing in the restoration handles their quantities.
- `power_ext_renewal_rate` vs `power_renewal`: the rate sentence is declared superseded ("at the renewal rate worked out below rather than the bare offered rate"); active-only, start-date, end-date counting, grace period, late-election and different-plan sentences followed; the loyalty sentence is handled (and declared) by the loyalty policy. "When the two notices state different offers, the final_options_notice governs" (`power_expiry_notices`) vs "the latest renewal notice": coincide whenever the final notice is compliant (issued after the initial).
- `power_ext_referral_credit_amount` vs `power_referral_credit`: the posting/amount sentence is declared superseded (adds the bill cycle in progress on the posting date and the worked-out amount); qualification at `referral_qualifying_cycles` completed cycles, active-referrer, one-per-referred-customer, yearly cap and "referred customer receives none" followed.
- `power_ext_renewal_loyalty_credit` vs `power_renewal`: the loyalty sentence is declared superseded (bill of the cycle that starts with the new term; worked-out amount; 0.00 earns none kept). vs `power_signup_credit` ("All bill credits are additive …") followed.
- `power_ext_offpeak_dispute_amount` vs `power_billing_correction`: the limit sentence is declared superseded (over-limit → one open billing dispute at the worked-out disputed amount); lookback, one-correction-per-line, no back-billing, usage disputes excluded followed. The schema meaning of `power_billing_disputes.disputed_amount_usd` ("Over-billed amount computed for the line …") is not policy text; the declared override governs (observation O-9).
- `power_ext_offpeak_rebill_credit` vs `power_billing_correction`: the rebill-amount sentence is declared superseded; the under-limit half of the limit sentence is restated in rule sentence 2. vs `power_supply_billing`: the off-peak correct-amount definition follows "off-peak kWh at the contract rate times offpeak_rate_multiplier".
- `power_ext_signup_credit_amount` vs `power_signup_credit`: sentence 1 is declared superseded; "Completed cycles are counted as the agreement's billing cycles that carry an on-peak or an all-hours energy charge line" redefines the count the superseded clause referred to through `power_msr_completed_cycles`. The measure also requires `billing_period_end` on or before the handling date; the extended count does not. They differ only for a billed cycle not yet ended — none exists in either world (every posted energy line's cycle ended before `frozen_time`) → no consequence. Online-credit, once-per-agreement, active/drop_pending, forfeit, "never by plan change/renewal/rollover", additivity followed.
- `power_ext_plan_change_rate` vs `power_plan_change_terms`: the rate sentence is declared superseded; active-only, equal-or-longer term, enrollment eligibility, next-cycle effective date, new term from `plan_change_date`, no ETF on an allowed change, no credits followed. "The new plan must satisfy the enrollment eligibility rules for the premise and the customer" points at `power_enrollment_eligibility`, whose structured eligibility is premise class, CAP and smart meter; the price-offer sentence there is a pricing rule replaced for plan changes by the extended rate → no second reading that refuses for lack of a price offer.
- No anonymous intermediate factor, 0/1 multiplier or dropped branch found against base: the extended quantities either replace a declared base amount or are new.

Finding: no undeclared override reaching a scored quantity of either task.

### factor_ladders

| policy | factors (effect) | P / M | multi-source (distinct records) | cross_difficulty |
| --- | --- | --- | --- | --- |
| dual_fuel_restoration | bundle_uplift (P), restoration_compensation (M), tenure_addition (P), usage_addition (P), paperless_addition (P) | 4/1 | paperless (agreement channel × notices) | bundle_uplift → gas (CPARAM rate_type, term_months) |
| renewal_rate | tenure (P), bundle (P), commitment (P), paperless (P), early_election (P), volume_scaling (M) | 5/1 | paperless | — |
| referral_credit_amount | renewal_season_scaling (M), referrer_bundle_bonus (P), referral_count (P), seasoned_referrer (P), referral_paperless (P) | 4/1 | paperless; bundle (gas status × gas plan) | referrer_bundle_bonus → gas (CFIELD status, CPARAM rate_type) |
| renewal_loyalty_credit | renewed_term_scaling (M), loyalty_tenure_scaling (M), bundle_loyalty (P), spend (P), referral_loyalty (P), whole_home (P) | 4/2 | bundle_loyalty (gas_agreements.status × gas_billing count) | bundle_loyalty, whole_home → gas (CFIELD, XCOUNT, XSUM) |
| offpeak_dispute_amount | new_customer_protection (M), dispute_fee_return (P), dispute_bundle_courtesy (P), dispute_usage_courtesy (P), dispute_tenure_courtesy (P), systemic_error_courtesy (P) | 5/1 | fee_return (declared; see F-1), bundle | bundle → gas |
| offpeak_rebill_credit | late_correction_scaling (M), rebill_fee_return (P), rebill_bundle_courtesy (P), repeat_referral_courtesy (P), rebill_tenure_courtesy (P) | 4/1 | fee_return (declared; see F-1), bundle | bundle → gas |
| signup_credit_amount | late_signup_scaling (M), dual_commodity_welcome (P), signup_usage_bonus (P), load_shift_bonus (P) | 3/1 | dual_commodity_welcome (gas_agreements.status × gas_billing sign-up line) | dual_commodity_welcome → gas (CFIELD, XCOUNT) |
| plan_change_rate | billing_error_concession (P), plan_bundle_reduction (P), plan_tenure_reduction (P), plan_volume_reduction (P), peak_cycle_reduction (P), remaining_term_scaling (M) | 5/1 | bundle | bundle → gas |

- Counts: every policy has 4–6 factors, ≥2 `parameter`, ≥1 `method`. Bindings per policy are disjoint; every `decides` is an input of `result`, never `result`.
- Every ladder has three tiers, pairwise disjoint as stated, the fall-through equal to the factor's `baseline` (0.0 or "taken as it stands"); no two tiers of any ladder select the same value or method (all `K` pairs differ; multipliers ≠ 1).
- Every tier (condition and value/method) is stated in the rule and implemented in compute (see rule_compute_equivalence).
- `method` labels: all ten method factors are multipliers on an intermediate (×K_long / ×K_mid / ×1). The audit text classes "a rate" substituted into the same formula as a parameter, but the instantiation charter lists "a transform or multiplier on an intermediate or on the result" as a method family; the auditor applies the framework's own definition and does not red-light the labels (observation O-10).
- Baselines: each `baseline.rule` is one sentence of the rule and is self-sufficient (dual-fuel: the plan's per-cycle credit; renewal: the latest notice's offered rate; referral: the plan referral credit; loyalty: the plan loyalty credit; dispute: largest off-peak line billed − correct; rebill: latest off-peak line billed − correct; sign-up: the plan sign-up credit; plan change: the contract rate in force). Every `baseline.params` key is a tier parameter or empty.
- Business reality of tier conditions (charter-global, structural):
  - **F-1 (SOURCE-FACTOR, bears on task 1).** The off-peak dispute and the off-peak rebill apply only to off-peak energy lines of a time-of-use agreement. The only time-of-use variant is Beacon Ridge Free Nights 12 (`rate_type: fixed_tou`, `monthly_service_fee_usd: 9.95`, `offpeak_rate_multiplier: 0.00`), and base `power_supply_billing` bills "one monthly_service_fee line" in every cycle, "billed in full for partial first and final cycles". Hence:
    - `dispute_fee_return` ("when the over-billed amount is 100 USD or more and the agreement's bill lines carry a monthly service fee …; from 50 up to but not including 100 USD and the bill lines carry a monthly service fee, half …; otherwise nothing"): a dispute is opened only for a correction larger than `agent_adjustment_limit_usd` 150.00; with multiplier 0.00 the over-billed amount equals the billed amount, so every customer who reaches this write has over-billed > 150 ≥ 100 and carries fee lines — the first tier's condition holds of every such customer; the half tier and the fall-through are unreachable. (Even if the limit were tested on the worked-out disputed amount, that amount ≤ 1.10·x + 9.95 + 5 + 2 + 2 + 5, so it exceeds 150 only when x > 114.6 ≥ 100.)
    - `systemic_error_courtesy` ("the billed amounts of all of the agreement's off-peak energy lines are added up; at 250 USD or more … from 100 up to but not including 250 … below 100 USD nothing"): the sum includes the disputed line, already > 114.6 → the fall-through "below 100" is unreachable for every customer who reaches this write.
    - `rebill_fee_return`: the part "the agreement's bill lines carry a monthly service fee" of both non-fall-through tiers holds of every customer who reaches the rebill write; the over-billed-amount part does divide customers.
    - Consequence: the declared multi-source character of both fee-return factors is fictitious (one part constant), and two of the dispute computation's ladders do not divide the customers who reach the write. Per-task demonstration in `task_1.md`.
  - Other factors: every condition of every remaining ladder varies across the customers who reach its write (e.g. a renewal of Price Lock 6 sits on the commitment and renewed-term fall-throughs; Monthly Variable has no end date for season/early/remaining-term; a customer without gas sits on every bundle fall-through).
  - Paperless ladders (dual-fuel, renewal, referral): base `power_expiry_notices` delivers notices "by email only to customers who enrolled through the web channel", so "email but not web" never occurs; the partial tier reduces to "web, no email notice yet". The three tiers remain distinct and reachable → observation O-11.
  - Naming: the rebill's "Repeat-referral courtesy" is tiered on open billing disputes, not on referrals; the condition itself (number of open billing errors) is one a utility weighs for goodwill → naming only, observation O-12.
- Per-task floors (multi-source ≥1, cross-difficulty ≥1): tree A carries paperless (multi-source) and gas factors in three computations; tree B carries `dual_commodity_welcome` (gas_agreements.status × gas_billing sign-up line, genuinely multi-source) and gas factors in four computations — both floors hold even after F-1 strikes the fee-return factors.
- Stamp-adjacent fields (charter/schema-wide): `premises.annual_kwh_usage` and `premises.annual_therm_usage` ("The utility's most recent 12-month historical … usage") are schema fields present on every premise; where they agree with a 12-month-usage tier, a solver reading them lands on the same tier. They do not name a tier outcome and no ladder rests on them; whether they agree is noted per task (observation).

### findings

| id | class | summary | bears on |
| --- | --- | --- | --- |
| F-1 | SOURCE-FACTOR RED (structure) | dispute fee return and systemic-error courtesy: conditions that hold of every customer who reaches the dispute write (first tier always, lower tiers unreachable); rebill fee return: fee-line part constant | task 1 (demonstrated in `task_1.md`) |
| O-1 | observation | dispute compute takes MAX off-peak kWh instead of the selected line's kWh; cannot change a number while the only TOU multiplier is 0.00 | task 1 (no consequence) |
| O-2 | observation | rebill compute's LATEST off-peak line omits the rule's "within the care agent's adjustment limit" filter | task 1 (checked: no consequence) |
| O-3 | observation | `RND` is Python float `round`, rule says half up | checked per task |
| O-4 | observation | "Afterwards" in two owner=user docstrings describes the call's own post-state | — |
| O-5 | observation | `state_gate` edge's `gate` names a field (`power_billing.line_type`), not an eligibility id | task 1 |
| O-6 | observation | two `effect` texts narrate one world's counts | — |
| O-7 | observation | action-form fallback on loyalty ← renewal acceptance not fully justified (a record-visible state exists) | task 0 |
| O-8 | observation | renewal-rate prerequisite sentence demands dual-fuel lines even on 0.00-credit plans, against inherited "0.00 earns none" (latent) | none (task 0 plan is 5.00/cycle) |
| O-9 | observation | schema meaning of `disputed_amount_usd` ("over-billed amount") vs the declared worked-out disputed amount | task 1 |
| O-10 | observation | all method factors are multipliers (accepted under the framework's method families) | both |
| O-11 | observation | paperless "exactly one" tier can only be "web without email" under base delivery rules | task 0 |
| O-12 | observation | "Repeat-referral courtesy" is tiered on open disputes | task 1 |

## closing_checklist

(Written after both tasks' freezes and reveals — see below.)

Written 2026-10-04 after both tasks' derivations were frozen (`task_0.md` 16:24:03Z, `task_1.md` 16:24:54Z, `_difficulty.md` charter-global section 16:22:58Z) and then revealed (from 16:24:58Z). Nothing above this heading was edited after the reveal.

- Per-task files correspond one-to-one with the tasks (`task_0.md` ↔ `tasks/0.json`, `task_1.md` ↔ `tasks/1.json`), with `_difficulty.md` alongside; round 1, no older revision. Comparison sections: task 0 does **not** carry PASS (SOURCE-CHAIN RED + SOURCE-TASK RED); task 1 does **not** carry PASS (SOURCE-FACTOR RED).
- Coverage and scopes: both `charter_scope`s revealed equal to the pre-reveal partition — {renewal_loyalty_credit, renewal_rate, dual_fuel_restoration, referral_credit_amount} and {plan_change_rate, offpeak_rebill_credit, offpeak_dispute_amount, signup_credit_amount}; pairwise disjoint, jointly covering all eight extended policies; every task tool used by exactly one task's GT; uuid8s independent (§ action_binding_and_uuids). ✓
- Trees: 3 prerequisite problems each; value_input edges 3 (task 0) and 2 (task 1) ≥ 2; owner=user write in each (`accept_renewal_offer_e5d86473`, `change_plan_fbee8941`); difficulty-wide graph acyclic, no cross-task edge. ✓ — but task 0's tree admits two compliant orders with different terminal states (F-T0-1). ✗
- Factors: every computation declares 4–6 factors with ≥2 parameter / ≥1 method, ≥3-tier ladders stated in the rule, distinct tier outcomes, honest self-sufficient baselines whose figures differ from gold, and every factor bears weight on its world (both tasks; GT `factor_sensitivity` equals the auditor's recomputation). ✗ for task 1: F-1 — three ladder conditions of the dispute/rebill computations hold of every customer who reaches the write.
- Gate re-run on the final form: not performed by this audit — the artifacts are unchanged since the orchestrator's snapshot (charter and tool hashes equal to `HASHES.txt`), and a re-run belongs to the rework round.

**Difficulty verdict (round 1): NOT PASSED.**
- task 0: SOURCE-CHAIN RED + SOURCE-TASK RED (sibling prerequisites referral credit / renewal acceptance unordered; the acceptance rewrites the contract end date the referral's season scaling reads → referral credit 92.50 vs 80.00; `prerequisite_closure.order_uniqueness` asserts the pair is pinned).
- task 1: SOURCE-FACTOR RED (F-1). Independent derivation equals GT on every scored value, object, date, owner and order.
- Charter-global observations O-1 … O-12 carry no demonstrated consequence on either task.

## revision_2

### charter_global_frozen (revision_2)

- Written 2026-10-04 (round 2), before either task's round-2 GT was opened. Auditor: same independent auditor as round 1.
- Hashes (recomputed, equal to the round-2 `HASHES.txt`): `power.extended.yaml` = `0e643c9e9551d6aacc7bfb79f2fe0e889d8807408fbb1e27e81da50a88a24ad5` (round 1: `5266e76b…`), `task_tools.py` = `b09d2f32f61d294d2804661e8212168eaeceac470cd9b3c30bdaba4847d94d13` (round 1: `8cc6224c…`), `task_0.view.json` `7857bd0f…` and `task_1.view.json` `4aab36da…` — both views identical to round 1 (same worlds, same personas).
- Both shared inputs changed → every charter-global section is re-derived below (not carried forward). Base section still verbatim (`diff` against `blueprint/products/power.yaml`: trailing blank line only).
- contamination_disclosure (round 2): the auditor read the round-1 GT of both tasks during round 1 (`task_0.md` / `task_1.md` § source_gt_comparison). That knowledge predates this re-derivation and cannot be removed; the round-2 derivation was recomputed from the round-2 charter and the views, and every figure below comes from that recomputation (charter `compute` lines evaluated under the `check_compute.py` DSL on the masked worlds plus the auditor's derived writes; temporary script outside the repo, deleted). No round-2 task JSON was opened before the task freezes below were on disk.

### changes found (round 1 → round 2), by policy

| policy | change | round-1 item |
| --- | --- | --- |
| `task_tools.py` | docstrings of `accept_renewal_offer` / `change_plan`: "Afterwards …" → "On success …"; all function bodies unchanged (each still one unconditional `ctx.update` / `ctx.create`) | O-4 |
| `power_ext_renewal_rate` | prerequisite sentence now "…carry **the dual-fuel credit owed** for every billing cycle…"; `condition` adds "on which the plan in force carried a per-cycle dual-fuel credit above 0.00" | O-8 |
| `power_ext_referral_credit_amount` | renewal-season scaling now reads "the latest renewal notice on the referring agreement, whose stated contract end date stays as printed whatever renewal or plan change the agreement records"; compute `season_notice_end_date = LATEST(power_notices.effective_date, event_type=power_renewal_notice)`; fall-through adds "or the referring agreement has no renewal notice" | F-T0-1 |
| `power_ext_renewal_loyalty_credit` | acceptance edge now state form: "The renewal loyalty credit is not posted until the agreement's current term starts on the day after the contract end date stated on its latest renewal notice, on the plan that notice offers."; `fallback_reason` removed; `effect` reworded | F-T0-1 / O-7 |
| `power_ext_offpeak_dispute_amount` | correct amount now "billed amount times the off-peak rate multiplier" ("because such a line was billed at the full contract rate"); `disputed_line_kwh` binding removed; fee return re-tiered on night-usage reliance (off-peak kWh / all energy kWh: ≥0.40 full fee, 0.20–0.40 half, <0.20 none); systemic error courtesy re-tiered on the count of off-peak lines billed at the full contract rate (≥3 / exactly 2 / only one) | O-1, F-1 |
| `power_ext_offpeak_rebill_credit` | sentence 2 now "applies to the most recently posted off-peak energy line …; when that line's off-peak rebill amount would exceed the care agent's adjustment limit, it is not credited here but referred to billing review as a billing dispute"; fee return tiered on the corrected line's over-billed amount alone (fee-line condition removed); "repeat-referral courtesy" renamed "open-review courtesy"; `effect` reworded | O-2, F-1, O-12, O-6 |
| `power_ext_plan_change_rate` | `remaining_term_factor_short` 1.25 → 1.2; `effect` reworded | O-3, O-6 |
| dual-fuel restoration, sign-up | no change found | — |

### policy_conflict_scan (revision_2)

- Partition unchanged (tree A: loyalty ← {renewal acceptance ← dual-fuel restoration, referral}; tree B: plan change ← {rebill ← dispute, sign-up}); disjoint, jointly complete; no cross-tree edge.
- Tree A sibling interaction (round-1 F-T0-1): the referral computation no longer reads `power_agreements.contract_end_date`; it reads `power_notices.effective_date` of the latest renewal notice, which `accept_renewal_offer_e5d86473` does not write (body: `ctx.update("power_agreements", …)` only). Remaining reads of the referral computation — plan referral credit `P('referral_credit_usd')` of the current variant (the acceptance can only put the offered plan, whose referral credit is 50.00 in every variant), referral lines, energy lines, email notices, enrollment channel, gas — are not written by the acceptance. → the two sibling orders cannot diverge on any charter-consistent world. The loyalty computation reads the referral line (count and amount) — both ordered before it.
- Tree B: unchanged independence of the sign-up branch from the dispute/rebill branch (the new dispute bindings read energy-line kWh and rates, not sign-up lines).
- New cross-policy sentence: rebill sentence 2 routes an over-limit latest off-peak line to billing review "as a billing dispute", while the dispute rule opens "the" dispute "on the off-peak energy line … with the largest billed amount". In a world where the latest line exceeds the limit but is not the largest billed line, the two sentences name different lines → latent; does not arise in task 1 (the latest line is within the limit) → observation O-13.

### rule_compute_equivalence (revision_2)

- Dispute: `disputed_line_correct_amount = RND(disputed_line_amount * P('offpeak_rate_multiplier'), 2)` = "its billed amount times the off-peak rate multiplier, rounded half up"; reliance = `SUM(off_peak kWh)/SUM(all energy kWh)` = "off-peak kWh taken as a share of all the kWh on its energy charge lines"; systemic = `COUNT(off_peak, rate_cents_kwh = F('contract_rate_cents_kwh'))` = "off-peak energy lines billed at the full contract rate are counted" — equivalent. The rule's own first sentence still defines the correct amount as "kWh times the contract rate times the plan's off-peak rate multiplier"; the "because such a line was billed at the full contract rate" sentence makes the two equal only when the line was billed at the contract rate; with the only TOU multiplier 0.00 both give 0.00 → no consequence (O-1 closed in substance; residual wording note O-14).
- Rebill: compute's `LATEST(... off_peak)` now matches the rule's object ("the most recently posted off-peak energy line"); the within-limit condition is now a routing gate, not a filter → O-2 closed. Fee return reads `fee_return_line_amount − rebill_line_correct_amount` = "the over-billed amount of the corrected line" — equivalent.
- Referral: `season_notice_end_date` and the `DAYS(NOW, …)` tiers equal the rule; no-notice fall-through implemented (`if season_notice_end_date else 0` → factor 1).
- Plan change: unchanged except the factor value.
- All other policies: unchanged and equivalent (round-1 section stands for them).
- Rounding: `RND` is still Python float `round`. Re-checked every scored value and every factor-substitution figure of both worlds under the round-2 charter: no half-cent tie remains (the round-1 tie 12.415 is gone with the 1.2 factor) → O-3 closed for this difficulty's worlds; the generic `RND` semantics are unchanged (charter-wide note only).

### action_binding_and_uuids (revision_2)

Same eight `(target_tool, computes)` pairs, same uuid8s, same owners; docstrings no longer carry "Afterwards"; no docstring names another tool or a sequence position; no tool body judges a prerequisite. → O-4 closed.

### prerequisite_graph (revision_2)

| blocked | problem | kind | gate | form | resolved_by |
| --- | --- | --- | --- | --- | --- |
| renewal_rate | dual_fuel_restoration | value_input | `credited_bundle_cycles` | state | `post_dual_fuel_credit_18175409` |
| renewal_loyalty_credit | renewal_rate | value_input | `renewed_term_months` | **state** (no `fallback_reason`) | `accept_renewal_offer_e5d86473` |
| renewal_loyalty_credit | referral_credit_amount | value_input | `loyalty_referral_lines` | state | `post_referral_credit_79c21554` |
| offpeak_rebill_credit | offpeak_dispute_amount | value_input | `open_dispute_count` | state | `open_billing_dispute_231feff0` |
| plan_change_rate | offpeak_rebill_credit | value_input | `plan_error_items` | state | `post_rebill_credit_41f05139` |
| plan_change_rate | signup_credit_amount | state_gate | `power_billing.line_type` | state | `post_signup_credit_3f59f0ed` |

- Every `policy_source` is a verbatim sentence of the blocked rule (renewal rule s2; loyalty s2, s3; rebill s3; plan change s3, s4). Acyclic; every `problem` an extended id; `form` state on all six, no `fallback_reason` anywhere (consistent).
- `condition` vs sentence: renewal-rate condition now restricts to cycles "on which the plan in force carried a per-cycle dual-fuel credit above 0.00" — the sentence's "the dual-fuel credit owed" carries exactly that restriction (owed ⇔ plan pays > 0.00 and gas active, base `power_agg_dual_fuel`) → same strength. Loyalty acceptance condition ("latest plan change date is the day after the contract end date stated on its latest renewal notice, its plan is the plan offered on that notice, and its contract end date is the end of the renewed term") matches the sentence; the trailing clause "only the acceptance of the renewal offer writes this state (accepting any other plan is a plan change, not a renewal)" restates base `power_renewal` and does not strengthen the gate.
- `effect` texts: no longer narrate one world's counts ("raises the count of open billing disputes the open-review courtesy is tiered on"; "raises the combined count of rebill credit lines and open billing disputes …") → O-6 closed.
- O-5 (state_gate `gate` names a field) unchanged → observation stands.

### prerequisite_sentences (revision_2)

- Edge 1 (renewal ← dual-fuel): "The renewal rate is fixed only after the agreement's bill lines carry the dual-fuel credit owed for every billing cycle within the billing dispute lookback on whose start date a Beacon Ridge gas agreement on the same premise was active." Connective "only after"; record-visible state; no tool/id; scope now matches inherited "A plan with dual_fuel_credit_usd_per_cycle 0.00 earns none" (nothing is owed on a 0.00 plan) → O-8 closed. Unique write unchanged.
- Edge 2 (loyalty ← acceptance), now state form: "The renewal loyalty credit is not posted until the agreement's current term starts on the day after the contract end date stated on its latest renewal notice, on the plan that notice offers." Connective "not … until"; waits on a record-visible state named in table words (term start = `plan_change_date`, notice `effective_date`, `offered_variant_name`); no tool, id or snake_case. Which write brings it about: base `power_renewal` "When the election is made on or before contract_end_date, the new term starts the day after contract_end_date" + "the agreement takes the offered plan" → the acceptance. Could the plan change write the same state? Base `power_plan_change_terms`: a change moves the agreement "to another … plan" and "takes effect at the start of the next billing cycle". It would coincide only if (i) the notice offers a plan different from the current one and (ii) the next billing cycle starts exactly on the day after the notice's end date (a change requested during the final cycle); base `power_renewal` "Accepting a different plan than the one offered is a plan change, not a renewal" leaves the offered-plan case to renewal. In task 0's world the offered plan equals the current plan (Price Lock 24 → "another plan" excludes it) and the next cycle starts 2026-10-01, so only the acceptance can produce the state. Narrow latent coincidence → observation O-15. Fallback removed → O-7 closed.
- Edges 3–6 unchanged; pass as in round 1.
- No rule carries a second wording, tool name or policy id of any dependency; no depended-on rule restates the blocked sentence. Undeclared cross-problem order: the new rebill sentence 2 sends an over-limit line to billing review but states no order between problems (the order dispute → rebill is the declared edge 4) → no undeclared order; the latent line-selection tension is O-13.

### override_declarations (revision_2)

- Referral: the superseded clause is unchanged; the season-scaling sentence is new extended text with no base counterpart (base referral has no season scaling) → no new override.
- Dispute: the new correct-amount wording ("billed amount times the off-peak rate multiplier") departs from base `power_supply_billing` ("off-peak kWh at the contract rate times offpeak_rate_multiplier") only for a line billed at a rate other than the contract rate; with multiplier 0.00 both are 0.00 → no consequence on any charter-consistent world (O-14).
- Rebill sentence 2 restates the base limit sentence's split (≤ limit credited, > limit referred) that the dispute policy's overwrite declared superseded → consistent with the declared replacement.
- Plan change: factor value only.
- Others unchanged. Finding: no undeclared override reaching a scored quantity.

### factor_ladders (revision_2)

- Counts unchanged per policy (dual-fuel 5: 4P/1M; renewal 6: 5P/1M; referral 5: 4P/1M; loyalty 6: 4P/2M; dispute 6: 5P/1M; rebill 5: 4P/1M; sign-up 4: 3P/1M; plan change 6: 5P/1M). Bindings disjoint; three-tier ladders stated in full in the rule; distinct outcomes; fall-through = baseline.
- **F-1 re-check (dispute / rebill ladders over the customers who reach the write)** — every customer reaching the dispute write is on Free Nights 12 with at least one off-peak line billed > 150.00 (≥ 1,129 kWh at 13.29¢ is not required by the rule; any over-limit line suffices):
  - `dispute_fee_return` (night-usage reliance = off-peak kWh / all energy kWh, ≥0.40 / 0.20–0.40 / <0.20): the share depends on the whole history of on- and off-peak kWh; nothing about reaching the write fixes it (a long-tenure customer with one over-billed night cycle and heavy day use sits below 0.20). All three tiers reachable; no condition holds of every such customer. A utility returning the time-of-use plan's monthly fee in proportion to how much the customer relied on the free-night window it paid for is a treatment the business would publish. ✓
  - `systemic_error_courtesy` (count of off-peak lines billed at the full contract rate, ≥3 / 2 / only one): every such customer has ≥1 (the disputed line), so the fall-through "only the disputed line" is exactly the minimum and reachable; 2 and ≥3 reachable. ✓
  - `rebill_fee_return` (corrected line's over-billed amount ≥100 / 50–100 / <50): the rebill applies only when the rebill amount is within 150.00, so all three tiers are reachable; the constant fee-line condition is gone; the factor no longer claims a compound condition. ✓
  - → F-1 closed.
- Multi-source per task: tree A — paperless (×3), bundle loyalty; tree B — `dual_commodity_welcome` (gas_agreements.status × gas_billing sign-up line). Cross-difficulty: gas in both trees, seeded.
- Referral `renewal_season_scaling`: reads the latest renewal notice's stated end date; condition varies (no notice / near / approaching / far) ✓. A referral bonus scaled by the referrer's renewal season as announced to them is a promotion a retailer would publish ✓.
- Rebill "open-review courtesy" tiered on open billing disputes — name now matches its condition → O-12 closed.
- Unchanged observations: O-10 (method factors are multipliers, accepted under the framework's method families), O-11 (paperless "exactly one" tier reduces to web-without-email).

### findings (revision_2, pre-reveal)

| id | round-1 class | round-2 status |
| --- | --- | --- |
| F-T0-1 | SOURCE-CHAIN RED + SOURCE-TASK RED | closed in the charter (season read from the notice; acceptance writes no notice) — per-task demonstration in `task_0.md` revision_2 |
| F-1 / F-T1-1 | SOURCE-FACTOR RED | closed (all three ladders divide the customers who reach the write) — per-task check in `task_1.md` revision_2 |
| O-1 | obs | closed (kWh MAX binding removed); residual wording O-14 |
| O-2 | obs | closed |
| O-3 | obs | closed for these worlds (no half-cent tie remains); `RND` semantics unchanged |
| O-4, O-6, O-7, O-8, O-12 | obs | closed |
| O-5, O-9, O-10, O-11 | obs | unchanged, stand as observations |
| O-13 (new) | obs | rebill sentence 2 routes an over-limit latest line to "a billing dispute" vs the dispute rule's single dispute on the largest line — latent, not exercised |
| O-14 (new) | obs | dispute correct amount = billed × multiplier "because such a line was billed at the full contract rate" — asserts a fact about the line; differs from base only for a line billed at another rate; moot at multiplier 0.00 |
| O-15 (new) | obs | loyalty ← acceptance state could coincide with a plan change taking effect on the day after the notice's end date onto a different offered plan — narrow; not reachable in task 0 |

### closing_checklist (revision_2)

Written after both revision_2 freezes (17:42:31Z) and the round-2 reveal (17:42:38Z); nothing above this heading in revision_2 was edited after the reveal.

- Files: `task_0.md`, `task_1.md`, `_difficulty.md`, each with round 1 untouched and `## revision_2` appended; both revision_2 comparison sections carry PASS. ✓
- Scopes: both `charter_scope`s equal the pre-reveal partition; disjoint; all eight extended policies covered; each task tool used by one task; uuid8s unchanged and independent. ✓
- Trees: 3 prerequisite problems each; value_input 3 and 2; owner=user write in each; acyclic; every compliant order of each tree recomputes to one terminal state (task 0's sibling pair now commutes). ✓
- Factors: 4–6 per computation with ≥2 parameter / ≥1 method; ≥3-tier ladders stated in full; distinct outcomes; no tier condition that holds of every customer reaching its write (F-1 re-checked); honest baselines whose figures differ from gold; every factor bears weight on its world; multi-source and seeded gas cross-difficulty in both tasks. ✓
- Round-1 items: F-T0-1, F-1/F-T1-1 closed; O-1, O-2, O-3 (for these worlds), O-4, O-6, O-7, O-8, O-12 closed; O-5, O-9, O-10, O-11 stand as observations; new observations O-13, O-14, O-15 (latent, no consequence on either task).
- Gate re-run on the final form: taken from the orchestrator's round-2 snapshot (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK; traceability deferred until the KB is published); the auditor did not re-run them.

**Difficulty verdict (revision_2): PASSED** — task 0 PASS, task 1 PASS on all four relationships; no new RED, no regression.
