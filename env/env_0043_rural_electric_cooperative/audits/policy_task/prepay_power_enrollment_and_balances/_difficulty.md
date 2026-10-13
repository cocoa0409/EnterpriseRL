# Policy-task audit — prepay_power_enrollment_and_balances / charter-global

## charter_global_frozen

- Freeze time: 2026-10-06 18:28 UTC (written before any task's GT was revealed). Auditor: erl-task-policy-audit subagent (Claude Opus 5.5), independent of the instantiating agent.
- Freeze hashes (recomputed by the auditor; they match `/tmp/orch43/views/prepay_power_enrollment_and_balances/HASHES.txt`):
  - `tasks/prepay_power_enrollment_and_balances/prepay.extended.yaml` sha256 `eb1a9214c172ad6a4b4685f8e778f04d0ea0a0cf136ef113504fb0af1ca96f33`
  - `tasks/prepay_power_enrollment_and_balances/task_tools.py` sha256 `6d3ee4906ce8cd497cebfe9188613b6ea6f41f7bf805c45efb1a4d393f0c8798`
  - masked views `0.view.json` `4b5f77a1…dbb89e8f`, `1.view.json` `4ae7939c…ee0e1` (match).
- Permitted inputs used: `blueprint/blueprint.yaml` (difficulty claim only), `blueprint/products/{prepay,deposit,service}.yaml` (base charters, for the conflict scan), `blueprint/share_tools.py` (finder signatures), the extended charter, `task_tools.py`, the two masked views, `skills/erl-task-instantiate/scripts/check_compute.py` (only to read the runtime semantics of `within_months`, `SUM/COUNT` scoping, `XCOUNT/XSUM` customer scoping, `MONTHS`, `DAYS`).
- Masked and unread at freeze: `tasks/*.json` (all of `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`), any worklog under `tasks/`, the scenario `worklog.md`, any earlier audit. No recursive grep was run over `tasks/`.

### Entry conditions (Step 0)
Gate snapshot `/tmp/orch43/snap_prepay_power_enrollment_and_balances.txt` supplied with actual output lines: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (0.json 18 acts / 1.json 20 acts, match True), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; CACHE-DIFF informational. `check_traceability` deferred by the orchestrator until the KB is published (noted, not a defect of this audit's input). Masked views and hashes supplied. Entry conditions complete.

Runtime semantics relied on (from `check_compute.py::build_env`): a window of N months keeps a row when `0 <= MONTHS(row_date, NOW) < N`, i.e. "dated after the same day N months before the current date, through the current date" — exactly the sentence each extended rule carries; `SUM/COUNT/LATEST` are scoped to the target prepay account; `XSUM/XCOUNT/XLATEST` are scoped to the customer (rows carrying the customer_id or pointing at one of the customer's holdings), so the un-filtered `arrange_ledger` and `capital_ledger` reads are member-wide as the rules say ("a payment arrangement of the member", "the member's capital credit records").

### policy_conflict_scan

Base copy: the base section of `prepay.extended.yaml` (lines 1-1052) is key-for-key identical to `blueprint/products/prepay.yaml` (all ten top-level keys equal after YAML load; the only textual diff is one trailing blank line). PASS.

Extended policies and the subjects / tools they claim:

| policy | subject | target_tool (owner) | computes | trigger | prerequisite |
|---|---|---|---|---|---|
| prepay_ext_deposit_release_credit | prepay_deposit_credit | post_deposit_release_credit_69d45e15 (agent) | credit_amount | state_due | [] |
| prepay_ext_activation_payment | prepay_payment | make_activation_payment_0416a855 (user) | gross_payment_amount | on_request | deposit_release_credit (value_input, state) |
| prepay_ext_meter_error_refund | prepay_credit_adjustment | post_meter_error_refund_29b7beca (agent) | refund_amount | state_due | [] |
| prepay_ext_disconnect_alert_reset | prepay_alert_settings | reset_low_balance_alert_c29238fa (agent) | low_balance_alert_amount | state_due | [] |
| prepay_ext_restore_payment | prepay_payment | make_restore_payment_2eb3ad28 (user) | gross_payment_amount | on_request | meter_error_refund (value_input, state); disconnect_alert_reset (value_input, action) |

Overlap scan:
- Two policies compute `gross_payment_amount` on `prepay_payment`; their subjects are disjoint by status (activation: "an enrollment awaiting activation"; restore: "a PrePay Power meter disconnected for low balance ... on an enrollment that carries no arrears balance") and they use different tools. Both carry "no recovery portion", consistent with base `prepay_evt_payment_split` (activation payment exempt; split applies only "While the arrears_balance is above zero"). Both clamp to base payment limits (activation_payment_min / min_payment_amount, max_payment_amount). No conflict.
- Alert reset vs base `prepay_evt_alerts`: base lets "The member ... change the low_balance_alert_amount to any amount from low_balance_alert_min through low_balance_alert_max"; the extended reset is a cooperative-initiated write clamped to the same range. No base sentence reserves the change to the member alone, so `overwrite: []` stands (observation O-4).
- Restore vs base `prepay_evt_disconnect_reconnect`: reconnection still happens when the balance reaches reconnect_threshold_balance; the restore quote can exceed the threshold. No conflict.
- Meter error refund vs service charter `service_evt_meter_test`: the service rule refunds the standard-bill energy charges of the rebill window on the service account; the extended rule refunds the prepay daily charges and states "standard-billing periods before the activation are refunded on the service account, not here". Disjoint quantities. No conflict.
- **Deposit release vs deposit charter `deposit_evt_application` (cross-category read boundary): CONFLICT** — see finding F-1.
- Deposit release vs base `prepay_agg_member_arrears`: see override_declarations and finding F-2.

Scope: the five extended policies split into two trees — {activation_payment <- deposit_release_credit} and {restore_payment <- meter_error_refund, disconnect_alert_reset} — which are disjoint and together cover all five extended policies (derived from the prerequisite graph; each task's own scope is confirmed per task after reveal). The difficulty claim in `blueprint.yaml` also lists prepay_enroll, prepay_arrears_transfer, prepay_arrears_recovery, prepay_tier_change, prepay_convert, prepay_refund and prepay_arrears_return, which no extended policy targets (observation O-1).

### rule_compute_equivalence

Every `compute_basis` quotation is verbatim in its policy's `rule` (scripted check, all 5 policies, no miss). Sweep back, policy by policy:

- deposit_release_credit: held amount (CFIELD deposit held_amount, status held), covered balance (MX(0, account_balance) less set-aside, floor 0), cut-over reserve RND(reserve_days * reserve_daily_cost, 2), reserve days DAYS(last bill date, enrolled_date) + notice + returned − patronage, floor 0 ("applied together ... never fewer than zero"), result MX(0, RND(held − covered − reserve, 2)). Three-tier reserve daily cost: "at least full_year_bills standard bills ... and ... fewer kWh than the average energy line" ↔ `bills_12m >= 12 and kwh_last_bill * bills_12m < kwh_12m` (algebraically identical); 6-11 bills ↔ usage_6m/182; else last bill/30. Bills are counted as `energy_charge` lines (one per standard bill). "patronage years" is implemented as a count of distribution-margin `capital_allocation` rows, not distinct `allocation_year` values (observation O-2; equal in both seeds — one DM row per year). Pledge set-aside: government whole / else charity 50% RND / else 0 ↔ compute. No invented basis, no empty promise.
- activation_payment: result MN(max, MX(min, RND(target − balance, 2))) ↔ "raised to ... activation_payment_min ... lowered to ... max_payment_amount"; target RND(cover_days * daily_cost, 2); cover days = channel days + medical + arrangement + late ("added together before they multiply"). Opening daily cost: ≥12 bills → MX(last bill, 13-month-minus-12-month usage)/30; 6-11 → 6m/182; else last/30. Channel ladder reads the latest `service_payment` (pledges and returns are other event types, so excluded) and 3-month counts of mail_check/office_check/money_order and office_cash/payment_kiosk. Medical 12m/24m by received_date; arrangement default rebill / missed installment in 24m member-wide; late charges 12m. Equivalent.
- meter_error_refund: window ladder (earlier within-tolerance test on/after activation → MX(1, MONTHS(test, NOW)); else activated < max months → months+1; else max months); refunded lines (tax>0 and PCA → energy+PCA+tax; PCA, no tax → energy+PCA; else energy); share ladder (earlier within-tolerance fast-side test → average; else error < 2×tolerance → (error−tol)/(100+error−tol); else error/(100+error)); test-request courtesy (≥3 → 15, ==2 → 7.5, else 0) by report_date in 12m; disconnection courtesy (≥ max_disconnects_per_30_days → 10, ≥2 → 5, else 0) in the refund window. Implementation reads only the latest within-tolerance test and does not check that it precedes the fast test ("an earlier meter test") — observation O-3, not exercised by any seed.
- disconnect_alert_reset: alert daily cost = daily-charge total / count of energy_charge lines (one per service day) in the window; window ladder (<2 whole months → since activation; ≥6 → 3m; else 1m); warning days ladder (≥ max_disconnects → 7; >2 → 5; else disconnect_warning_days); lag (latest prepay payment office_check & ≥2 → 2; latest cash/kiosk & ≥2 → 1; else 0); medical 3/1/0; returned 2/1/0; arrangement 2/1/0; result MN(max, MX(min, MX(current, ceil-dollar(total_days * cost)))). Equivalent.
- restore_payment: target ladder (≥2 disconnects in 1m and alert > threshold → alert; ≥2 and alert ≤ threshold → threshold+10; else threshold); cushion daily cost 1m charges / service days; frequency days (≤1 → 6, 2-3 → 4, else 0); reconnect fees on the service account 24m (≥2 → 2, 1 → 1, else 0); patronage (≥25 → −2, ≥10 → −1); cushion days floor 0; pledge scale (government 25%, else charity 50%, else 100%); result MN(max, MX(min, RND(target − balance + cushion, 2))). Equivalent.

Every factor's ladder tiers are stated in the rule (the `when` texts are verbatim or word-order paraphrases of the rule sentences) and each `decides` binding implements exactly those tiers. PASS (with observations O-2, O-3).

### action_binding_and_uuids

- Five `(target_tool, computes)` pairs, each claimed by exactly one policy. Docstrings: each describes one atomic write; none names another tool, states a position in a sequence, or carries before/after/first ("the next low-balance alert follows the new amount" refers to alert delivery, not to a tool order). Each function body only creates/updates rows; none validates eligibility, a prerequisite, or a computed amount (module docstring: "No tool judges eligibility, checks a prerequisite or computes a policy amount" — confirmed by reading all five bodies).
- uuid8s: 69d45e15, 0416a855, 29b7beca, c29238fa, 2eb3ad28 — five distinct, no shared prefix or tail, no sequential pattern. PASS.

### prerequisite_graph

- `prerequisite` present on all 5 policies (`[]` on three). Edges: activation → deposit_release_credit; restore → meter_error_refund; restore → disconnect_alert_reset. All targets are extended ids in this file, none self, graph acyclic (depth 1).
- `policy_source` verbatim in the blocked policy's own rule: all three True (scripted).
- `form`: two `state`, one `action` with `fallback_reason` present; the two state-form edges carry none. PASS.
- `kind: value_input` on all three; `gate` names `balance_on_enrollment`, `balance_now`, `alert_amount` exist as bindings in the blocked compute (F('prepaid_balance') / F('low_balance_alert_amount')). `resolved_by` equals the depended-on policy's `target_tool` in all three, and each tool's effect (raise prepaid_balance by the credited amount; replace low_balance_alert_amount) changes exactly that binding.
- `condition` vs sentence: deposit edge "a deposit credit for every security deposit that was held on the enrolled service account when the enrollment was taken" ↔ "deposit-credit entry whose source is the deposit record in held status on the enrolled service account" — same closed set; meter edge "for every meter test ... that found the meter fast" ↔ "each meter test ... with result fast" — same; reset edge ↔ "alert amount equals the reset figure ... for the latest low-balance disconnection" — same. No authoring-viewpoint phrasing. PASS.

### prerequisite_sentences

1. activation ← deposit credit (state): "The activation payment is quoted only after the prepaid balance of the enrollment carries a deposit credit for every security deposit that was held on the enrolled service account when the enrollment was taken." Ordering connective "only after"; waited-on state is record-visible (a `prepay_deposit_credit` row on the enrollment's ledger with the deposit as source, and the prepaid balance) in finder words; no tool, id or snake_case token; closed set by kind. Exactly one write of the difficulty creates a deposit-credit entry (post_deposit_release_credit_69d45e15; the other four tools write a payment, a credit adjustment or an alert amount). Derivation: sentence → find_deposit_accounts(service_account_id) shows a held deposit → find_prepay_ledger shows no deposit credit → the only rule describing a deposit credit is prepay_ext_deposit_release_credit ("the security deposit held on that service account ... is released into the enrollment as one deposit credit on the prepaid balance") → one reading.
2. restore ← meter error refund (state): "The restore payment is not quoted until the prepaid balance carries the meter error refund for every meter test of the underlying service account that found the meter fast." Connective "not ... until"; state record-visible (credit adjustment with reason meter_error_refund sourced on the test); one write creates it (post_meter_error_refund_29b7beca). Derivation: sentence → find_service_trouble_reports shows a fast test → ledger has no meter_error_refund adjustment → prepay_ext_meter_error_refund rule describes that credit → one reading.
3. restore ← alert reset (action): "The restore payment is not quoted before the low-balance alert amount owed a reset after the latest low-balance disconnection has been reset." Connective "not ... before"; names the action in business words. Fallback tested: the reset tool writes only `low_balance_alert_amount` on the account (no ledger or notification row), so no record-visible state singles the reset out from a member-chosen or earlier-reset amount; fallback justified. Derivation: sentence → "owed a reset" is defined only by prepay_ext_disconnect_alert_reset's first sentence ("An enrollment disconnected for low balance that has been disconnected for low balance at least twice in the one-month window is owed a reset of its low-balance alert amount") → one reading.
- No rule restates another problem's prerequisite sentence; no rule names another problem's tool or id; the depended-on rules (deposit release, meter refund, alert reset) carry no sentence about the payments.
- Base rule sentences stating cross-problem orders (prepay_enrollment_eligibility "an active Budget Billing plan ... must be ended and settled first, and an active payment arrangement ... must be ended first"; prepay_agg_member_arrears "the member must first pay the total down into a band") ground no edge of this difficulty; neither condition holds in either seed (see task files). Observation O-5.
PASS.

### override_declarations

- prepay_ext_deposit_release_credit — refs prepay_evt_enrollment_transfers, prepay_agg_member_arrears.
  - prepay_evt_enrollment_transfers: sentence "it is applied first against the arrears that would otherwise be transferred, and only the remainder is credited to the prepaid balance as a prepay_deposit_credit whose source_reference_id is the deposit record" — handled differently; declared in `overwrite` (superseded clause verbatim in base: True; replaced_by verbatim in rule: True). "Deposit interest accrued to that day is paid out by the deposit charter, not here" — followed (no interest in the extended credit). "Arrears transfers follow prepay_agg_member_arrears" — followed. Credit-adjustment sentence — not this policy's quantity.
  - prepay_agg_member_arrears: "The arrears to be transferred ... the positive account_balance of the service account being enrolled plus the positive account_balance of every final-billed service account of the same member, after any security deposit held on the enrolled service account has been applied to them." The extended covered balance is "the positive account balance of the enrolled service account" only (less agency pledges), and the extended rule states "The part of the deposit kept back by the covered balance and the cut-over reserve stays with the deposit record". Where a final-billed account with a positive balance exists, base applies the deposit against it too (smaller remainder), the extended rule does not. Not named in `overwrite` → undeclared partial override (finding F-2). Band, tier and per-source transfer sentences — not this policy's quantity, followed.
- prepay_ext_activation_payment — refs prepay_evt_activation, prepay_evt_payment_split; `overwrite: []`. "activation payment of at least activation_payment_min" — followed (floor); "credited in full ... debt_recovery_applies false" — followed; activation window / agreement on file — inherited, not touched; payment_split min/max/channels — followed (cap at max_payment_amount; tool channel phone_ivr_card is in payment_channels_allowed). No undeclared deviation.
- prepay_ext_meter_error_refund — ref prepay_evt_enrollment_transfers; the "for the difference only and once per source record" sentence is replaced (courtesies added) and declared; "once per source record" kept ("booked once for the meter test"). No other deviation.
- prepay_ext_disconnect_alert_reset — refs prepay_evt_alerts, prepay_evt_disconnect_reconnect; `overwrite: []`. Range min/max followed (clamp, instead of "not accepted" for an out-of-range member request — the reset never produces an out-of-range amount, so no conflict on the scored quantity). No undeclared deviation.
- prepay_ext_restore_payment — refs prepay_evt_activation, prepay_evt_payment_split, prepay_evt_disconnect_reconnect; `overwrite: []`. Payment limits followed; no recovery portion only on an enrollment with zero arrears (consistent with the split rule); reconnect at threshold unaffected. No undeclared deviation.
- No anonymous intermediate factor, 0/1 multiplier or dropped branch found against the prepay base. No rule calls a base output "wrong".

### factor_ladders

| policy | factor | label | decides | tiers | multi-source (every non-fall-through tier ≥2 conditions over distinct records) | cross_difficulty | label honest? |
|---|---|---|---|---|---|---|---|
| deposit_release | reserve_daily_cost_basis | method | reserve_daily_cost | 3 (12m/365 if ≥12 bills & last kWh < avg; 6m/182 if 6-11; last/30) | no (tier 2 single) | service | yes (averaging basis changes) |
| | notice_reserve_days | parameter | notice_days | 3 (8/4/0) | tier1 status+amount on one row | service | yes |
| | returned_payment_reserve_days | parameter | returned_days | 3 (8/4/0) | no | service | yes |
| | patronage_reserve_days | parameter | patronage_days | 3 (6/3/0) | no | capital | yes |
| | assistance_pledge_set_aside | parameter | assistance_set_aside | 3 (whole gov / 50% charity / 0) | no (tier1 single) | service | yes |
| activation | payment_habit_cover_days | parameter | channel_cover_days | 3 (14/10/7) | **yes** (latest payment channel AND count of payments in 3m) | service | yes |
| | opening_daily_cost_basis | method | opening_daily_cost | 3 (max(last, year-ago)/30; 6m/182; last/30) | no | service | yes (max-of comparison) |
| | medical_certificate_cover_days | parameter | medical_days | 3 (4/2/0) | no | service | yes |
| | arrangement_history_cover_days | parameter | arrangement_days | 3 (5/2/0) | no | arrange | yes |
| | late_charge_cover_days | parameter | late_days | 3 (3/1/0) | no | service | yes |
| meter_refund | refund_window_anchor | method | refund_window_months | 3 | no | service | yes (different anchoring computation) |
| | refunded_line_scope | parameter | refunded_lines | 3 | tier1 tax AND PCA (one variant row) | service | acceptable |
| | overbilled_share_method | method | error_share | 3 | no | service | yes (different formulas) |
| | test_request_courtesy | parameter | test_request_courtesy | 3 (15/7.5/0) | no | service | yes |
| | disconnection_courtesy | parameter | disconnection_courtesy | 3 (10/5/0) | no | null | yes |
| alert_reset | alert_daily_cost_window | method | alert_daily_cost | 3 (since activation / 3m / 1m) | no | null | borderline (window choice only; observation O-6) |
| | repeat_disconnection_warning_days | parameter | warning_days | 3 (7/5/3) | no | null | yes |
| | payment_lag_warning_days | parameter | lag_days | 3 (2/1/0) | **yes** (latest payment AND count in 1m) | null | yes |
| | medical_certificate_warning_days | parameter | medical_days | 3 (3/1/0) | no | service | yes |
| | returned_payment_warning_days | parameter | returned_days | 3 (2/1/0) | no | service | yes |
| | arrangement_warning_days | parameter | arrangement_days | 3 (2/1/0) | no | arrange | yes |
| restore | repeat_disconnection_restore_target | parameter | restore_target | 3 (alert / threshold+10 / threshold) | **yes** (notification count AND account alert amount) | null | yes |
| | payment_frequency_cushion_days | parameter | frequency_days | 3 (6/4/0) | no | null | yes |
| | reconnect_history_cushion_days | parameter | reconnect_days | 3 (2/1/0) | no | service | yes |
| | patronage_cushion_days | parameter | patronage_days | 3 (2/1/0) | no | capital | yes |
| | assistance_pledge_cushion_scale | **method** | restore_cushion | 3 (×25% / ×50% / ×100%) | no | service | **NO** — finding F-3 |

- Counts per policy (declared): deposit 5 (4 P, 1 M); activation 5 (4 P, 1 M); meter refund 5 (3 P, 2 M); alert reset 6 (5 P, 1 M); restore 5 (4 P, 1 M). All within 4-6, ≥2 P. After the label test, restore has **0 honest method factors** (F-3).
- Bindings: each factor's binding set is disjoint from every other factor's in the same policy (scripted); each `decides` is an input, never `result`.
- Tiers: every ladder has three pairwise-disjoint tiers, the fall-through counted; no two tiers of one ladder select the same value or method; every fall-through equals the policy's baseline for that input.
- Baselines (`baseline.rule` sentences all verbatim in the rule): deposit, activation, alert reset and restore baselines are self-sufficient. **meter_error_refund's baseline is not**: it states "The meter error refund is the overbilled amount plus the test-request courtesy and the disconnection courtesy" but gives no default for either courtesy (`baseline.params: []`) — finding F-4.
- Conditions/outcomes realism: tenure (patronage years), notices, returned payments, arrangement defaults, late charges and medical certificates as risk adjustments to a hold-back, a cover or a warning horizon; agency pledges reducing the amount kept or the cushion; courtesy credits after repeated tests or disconnections — each is a consideration a cooperative's credit/collections desk weighs for that quantity, and none holds of every customer reaching the write. Fall-throughs (last bill/30 over days since bill; 7 cover days; 6-month energy refund at error/(100+error), mirroring the service charter; disconnect_warning_days; reconnect threshold with no cushion) are ordinary published treatments. Observation O-7 on the cut-over reserve days being raised by risk signals that do not change unbilled usage.

### findings

- **F-1 — SOURCE-POLICY RED (cross-charter conflict on the deposit credit amount). Bears on task 0.**
  Symptom: two published rules fix the amount of the same `prepay_deposit_credit`. Root cause: the extended `overwrite` replaces only the prepay base copy of the "remainder" clause; the deposit charter's own statement of the release amount stands, and its `deposit_apply_prepay` event triggers `prepay:prepay_deposit_credit` with `amount: amount`. Evidence: `blueprint/products/deposit.yaml` `deposit_evt_application`: "When the service account enrolls in PrePay Power and apply_on_prepay_enrollment is true, the held_amount and accrued interest are applied first against the service account's balance (deposit_apply_balance) up to that balance, and only the remainder is released into the prepaid balance (deposit_apply_prepay)." and "Each application ends the deposit record in applied status."; `prepay.extended.yaml` prepay_ext_deposit_release_credit: "The deposit credit is the held amount of the deposit less the covered balance and less the cut-over reserve, rounded to the cent, and never less than zero." and "The part of the deposit kept back by the covered balance and the cut-over reserve stays with the deposit record for the standard bills of the enrolled service account." In any world with a positive cut-over reserve or a pledge the two give different credits, and they disagree on the deposit's terminal status (applied vs still held). Also the base prepay sentence "Deposit interest accrued to that day is paid out by the deposit charter, not here" contradicts the deposit charter's inclusion of accrued interest in the release (pre-existing base/base conflict; consequence only where accrued_interest > 0). Demonstration against task 0's world: see `0.md`. Affected: prepay_ext_deposit_release_credit rule/overwrite vs blueprint deposit charter `deposit_evt_application`.
- **F-2 — undeclared partial override of prepay_agg_member_arrears (observation at charter level; no task demonstrates it).** The base sentence applies the held deposit against the enrolled account's and every final-billed account's positive balance; the extended covered balance omits final-billed accounts and is not named in `overwrite` for that base policy. Neither seed carries a final-billed service account (task 0 and task 1 each seed one service account), so no scored value moves; recorded as an observation.
- **F-3 — SOURCE-FACTOR RED (mislabelled method). Bears on task 1.** `assistance_pledge_cushion_scale` is labelled `method`, but its three tiers are "the cushion days times the cushion daily cost scaled to pledge_cushion_government_pct percent", "... scaled to pledge_cushion_charity_pct percent", "... in full" — one formula `RND(cushion_days * cushion_daily_cost * pct / 100, 2)` with pct ∈ {25, 50, 100}: a rate substituted into the same formula, i.e. a `parameter`. Struck as a method, prepay_ext_restore_payment has zero `method` factors (its other four are `parameter`), below the floor of one per computation. Affected: `prepay.extended.yaml` prepay_ext_restore_payment `factors[assistance_pledge_cushion_scale]`.
- **F-4 — SOURCE-FACTOR RED (incoherent baseline). Bears on task 1.** prepay_ext_meter_error_refund `baseline.rule` names "the test-request courtesy and the disconnection courtesy" as addends of the refund but states no default for either (`baseline.params: []`); their zero values exist only as the fall-through tiers of the factor ladders ("with one request it is zero", "with fewer disconnections it is zero"), which the baseline document must be silent about. A reader of the computation document alone cannot compute a definite refund. Demonstration on task 1's world in `1.md`.
- Observations: O-1 claimed event types with no extended policy (prepay_enroll, prepay_arrears_transfer, prepay_arrears_recovery, prepay_tier_change, prepay_convert, prepay_refund, prepay_arrears_return); O-2 patronage years counted as allocation rows, not distinct years; O-3 "earlier meter test" not ordered against the fast test in compute; O-4 cooperative-initiated alert reset of a member-chosen setting with `overwrite: []`; O-5 base cross-problem order sentences (budget/arrangement "first", "pay the total down into a band" first) ground no edge; O-6 `alert_daily_cost_window` (and `reserve_daily_cost_basis`) change only the averaging window — accepted as method, borderline, while the analogous `refunded_line_scope` is labelled parameter; O-7 the cut-over reserve, described as keeping back unbilled usage, is lengthened/shortened by risk and tenure signals that do not change usage.

## closing_checklist

Written 2026-10-06 18:34 UTC, after both task reveals. The charter-global section above was frozen before any reveal, at sha256 `aefba3ce514923585b63ce1cd12284b6fcba498431c04dcecf49fc2862bd6936`, and is left untouched.

**The difficulty does NOT pass the source-layer audit.** Not every task has all four relationships at PASS:

| task | SOURCE-POLICY | problem tree | factors | unique solution | verdict |
|---|---|---|---|---|---|
| 0 | RED (F-1) | PASS | PASS | two answers via F-1 | **RED: SOURCE-POLICY** |
| 1 | PASS | PASS | RED (F-3, F-4) | PASS | **RED: SOURCE-FACTOR** |

Step 4 items:
- Files: `0.md` and `1.md` match tasks 0 and 1 one-to-one, with `_difficulty.md` alongside. This is the first revision, so there is no older one to trace. Neither comparison section carries an overall PASS.
- Coverage and disjointness: `charter_scope` is {deposit_release_credit, activation_payment} for task 0 and {meter_error_refund, disconnect_alert_reset, restore_payment} for task 1. The two are pairwise disjoint and together cover all five extended policies. The five task tools are closed by GT, and each has an independently generated uuid8. PASS.
- Problem trees:
  - task 0 has 1 prerequisite problem and 1 value_input edge;
  - task 1 has 2 prerequisite problems and 2 value_input edges;
  - each tree has an owner=user root;
  - the difficulty-wide graph is acyclic and has no cross-task edge.
  PASS.
- Factors: task 0 passes. Task 1 does not: the restore payment has no honest method factor (F-3), and the meter refund baseline is not self-sufficient (F-4).
- Gates: the auditor did not re-run the instantiation-stage gates, because the difficulty cannot close. The orchestrator's snapshot `/tmp/orch43/snap_prepay_power_enrollment_and_balances.txt` (all green; check_traceability deferred) is cited as the state of the audited form.

## revision_2

### charter_global_frozen (revision 2)

- Freeze time 2026-10-06 19:42 UTC, written before either round-2 task's GT was revealed. Auditor: erl-task-policy-audit subagent (Claude Opus 5.5). The round-1 text above is left untouched.
- Inputs moved since round 1, so every charter-global section below is re-derived in full rather than carried forward:
  - `prepay.extended.yaml` round 1 `eb1a9214…ca96f33` → round 2 `eb673b175795f6f3b381725d878efe24956a2584a2adf12e5003620a40cf2552`;
  - `task_tools.py` round 1 `6d3ee490…c8798` → round 2 `e4aab85d302dfdd56cd48f46ace8e9855f3f6a1eb812cb8c785e87a6fa6cb3ca`.
  Both match `/tmp/orch43/views/prepay_power_enrollment_and_balances_r2/HASHES.txt`. The blueprint is unchanged (file mtimes 11:15-11:20, before round 1).
- Entry conditions: gate snapshot `/tmp/orch43/snap_prepay_power_enrollment_and_balances_r2.txt` shows every gate OK:
  - EXTENDED, TASK TOOL CONTRACT, SOLVABILITY, COMPUTE, GROUNDING and SCOPE all OK;
  - REPLAY: 0.json 17 acts, 1.json 20 acts, closures match;
  - CACHE-DIFF informational only.
  Masked views `0.view.json` `3934d91b…2603d` and `1.view.json` `fd8135bf…04266` verified. Complete.
- Masked and unread at freeze: round-2 `tasks/0.json` and `tasks/1.json` beyond the views, and all worklogs.
- Prior exposure (inherent to a re-audit, disclosed): the round-1 GT of both tasks was read in round 1.

### policy_conflict_scan (r2)

Base copy: identical to `blueprint/products/prepay.yaml` (all ten keys equal). PASS.

Extended set:

| policy | target_tool | owner |
|---|---|---|
| prepay_ext_postpaid_credit_carry_in (new; replaces prepay_ext_deposit_release_credit) | post_carried_credit_69e6c97d | agent |
| prepay_ext_activation_payment (prerequisite now points at the carry-in) | make_activation_payment_0416a855 | user |
| prepay_ext_meter_error_refund | post_meter_error_refund_29b7beca | agent |
| prepay_ext_disconnect_alert_reset | reset_low_balance_alert_c29238fa | agent |
| prepay_ext_restore_payment | make_restore_payment_2eb3ad28 | user |

- Carry-in vs meter refund: both write `prepay_credit_adjustment`, with distinct reasons (postpaid_credit_transfer and meter_error_refund), distinct sources (the service account and the meter test) and distinct tools. No overlap.
- Both carry-in and meter refund supersede the same base sentence of prepay_evt_enrollment_transfers ("A credit adjustment is posted only for … once per source record."), each with a replacement covering only its own reason. The two replacements are compatible. The base's billing_error_correction and estimated_read_correction reasons are left with no governing sentence (observation R2-O2; no policy or task produces them).
- Cross-charter scan for the carried-in amount: no other charter fixes it.
  - Service charter `service_evt_payments` says "A payment over the balance leaves a credit balance that is applied to future bills". This states no transfer amount, and the carry-in rule keeps the held-back part "on the enrolled service account for its final standard bill".
  - `service_agg_member_balance` bars only cross-account offsets, and the carry-in keeps "never netted against another account's debt".
  - The deposit charter is no longer touched by any extended policy.
  - The round-1 deposit conflict (F-1) has no extended counterpart left.
- Other overlaps as in round 1 (activation vs restore disjoint by status; alert reset inside the base range). PASS.
- Scope: the two trees are {activation ← carry-in} and {restore ← meter refund, alert reset}. They are disjoint and cover all five policies.

### rule_compute_equivalence (r2)

Scripted check: every `compute_basis` quotation and every `baseline.rule` sentence of all five policies is verbatim in its rule, and every K() key exists in params.

- **carry-in** — every sentence has a matching compute binding:
  - "credit balance … stands below zero" ↔ MX(0, −account_balance);
  - cut-over reserve ↔ RND(days × cost, 2);
  - reserve days ↔ DAYS(last bill date, enrolled_date) + late days + reconnect days − patronage days, floored at 0;
  - reserve daily cost ladder ↔ the same three tiers as round 1;
  - uncleared hold ↔ latest `service_payment` channel in {mail_check, office_check, online_echeck}, MONTHS(latest_date, NOW) < 1, and returns in 12 months ≥ 1 → whole payment; = 0 → 50 %; else 0;
  - late charges 3+/1-2/0 → 6/3/0 days;
  - reconnect fees 2+/1/0 in 24 months → 6/3/0;
  - patronage ≥25/≥10 → −6/−3;
  - result MX(0, RND(credit − reserve − hold, 2)).
  The compute reads the current account_balance, while the rule says "when the enrollment is taken". The two coincide wherever nothing has posted to the account since the enrollment date (checked per task).
- **activation**: unchanged except the prerequisite sentence. Equivalent.
- **meter refund**:
  - "and before the fast test" is now in the rule and in compute (`accurate_date < fast_date` on the window and share tiers), so O-3 is closed;
  - "The test-request courtesy and the disconnection courtesy are each zero (courtesy_tests_default and courtesy_disconnects_default)" is in the rule and the baseline, and both fall-through tiers read those keys.
  Equivalent.
- **alert reset**: unchanged. Equivalent.
- **restore**: the pledge ladder is now government pledge → cushion 0 ("waived"); charity pledge → RND(cushion_days × P('daily_facility_charge'), 2); else → RND(cushion_days × cushion_daily_cost, 2). This is identical to the rule sentences. Equivalent.
- "patronage years" in the carry-in and restore rules now carry "(one is booked for each patronage year)", which makes the row count equal the year count by the rule's own statement. O-2 is addressed.

PASS.

### action_binding_and_uuids (r2)

- Five `(target_tool, computes)` pairs, each claimed once.
- The new docstring (`post_carried_credit_69e6c97d`) describes one atomic write, names no other tool and has no ordering word.
- All five function bodies only create a row and/or update one field; none validates anything.
- uuid8s: 69e6c97d, 0416a855, 29b7beca, c29238fa, 2eb3ad28 are distinct. The new 69e6c97d shares its first two hex characters with the retired 69d45e15 (observation R2-O1). No tail copying and no sequential pattern beyond that.

PASS.

### prerequisite_graph (r2)

- Edges:
  - activation → postpaid_credit_carry_in (value_input, gate balance_on_enrollment, state, resolved_by post_carried_credit_69e6c97d);
  - restore → meter_error_refund (value_input, state);
  - restore → disconnect_alert_reset (value_input, action, fallback_reason present).
- Every `policy_source` is verbatim in its blocked rule (scripted). Every target is an extended id, none points at itself, and the graph is acyclic.
- Each `condition` matches its sentence: "the carried-in credit for a credit balance that stood on the enrolled service account" ↔ "a credit-adjustment entry with the reason carried-in standard-billing credit whose source is the enrolled service account".
- Each `effect` is real: the tool raises prepaid_balance.

PASS.

### prerequisite_sentences (r2)

- **New edge**: "The activation payment is quoted only after the prepaid balance of the enrollment carries the carried-in credit for a credit balance that stood on the enrolled service account when the enrollment was taken."
  - Ordering connective "only after".
  - The waited-on state is record-visible: a credit adjustment with reason postpaid_credit_transfer and the service account as its source. No tool, id or token is named, and the scope is a closed set.
  - Exactly one write creates such an entry: post_carried_credit_69e6c97d. The meter refund tool writes reason meter_error_refund, so it cannot satisfy the sentence.
  - Derivation: sentence → find_service_accounts shows account_balance < 0 → find_prepay_ledger shows no carried-in credit → the only rule describing a carried-in credit is prepay_ext_postpaid_credit_carry_in → one reading.
- **Restore edges**: unchanged from round 1, PASS.
- No rule restates another problem's prerequisite sentence or names another problem's tool.
- Base order sentences: as round 1 (O-5).

PASS.

### override_declarations (r2)

- **prepay_ext_postpaid_credit_carry_in**, refs prepay_agg_member_arrears and prepay_evt_enrollment_transfers:
  - "A credit balance on the enrolled service account is carried in as a prepay_credit_adjustment … never netted …" is handled differently (credit less reserve less hold) and is declared (superseded clause verbatim in base: True; replaced_by verbatim in rule: True).
  - The credit-adjustment sentence of prepay_evt_enrollment_transfers is declared (True/True). "Once per source record" is kept ("booked once").
  - The other agg_member_arrears sentences (arrears measure over enrolled and final-billed positive balances, bands, per-source transfers) concern positive balances only and are followed.
  - The deposit sentence of prepay_evt_enrollment_transfers is not this policy's quantity.
  - No undeclared deviation.
- Activation, alert reset and restore: `overwrite: []`, no undeclared deviation (the new restore pledge ladder changes only the extended cushion, which base does not define).
- Meter refund: declared overwrite as in round 1.
- F-2 is moot: no extended policy now applies a deposit.

PASS.

### factor_ladders (r2)

Counts per policy:

| policy | factors | parameter | method | method factors | multi-source factors |
|---|---|---|---|---|---|
| carry-in | 5 | 4 | 1 | reserve_daily_cost_basis | uncleared_payment_hold (latest payment channel AND its date in the 1-month window AND a returned payment in 12 months; both non-fall-through tiers) |
| activation | 5 | 4 | 1 | opening_daily_cost_basis | payment_habit_cover_days |
| meter refund | 5 | 3 | 2 | refund_window_anchor, overbilled_share_method | |
| alert reset | 6 | 5 | 1 | alert_daily_cost_window (borderline, O-6) | payment_lag_warning_days |
| restore | 5 | 4 | 1 | assistance_pledge_cushion_method | repeat_disconnection_restore_target |

Carry-in cross-difficulty factors: service (reserve basis, hold, late, reconnect) and capital (patronage).

- **Restore's `assistance_pledge_cushion_method` (relabel of F-3's factor)** — the tiers are:
  - "the restore cushion is waived";
  - "the restore cushion covers only the fixed charges: the cushion days multiplied by the tier's daily_facility_charge";
  - "the restore cushion is the cushion days multiplied by the cushion daily cost".
  The second and third tiers draw the per-day cost from different sources: a tariff constant versus the one-month ledger average of all daily lines. The first removes the cushion term. This is no longer one formula with a scaled rate, so the `method` label is accepted. Borderline in the same sense as O-6, because tier 2 vs 3 is still "days × a daily figure". **F-3 closed.** The restore computation now has one honest method factor.
- **Meter-refund baseline**: it now states "The test-request courtesy and the disconnection courtesy are each zero (courtesy_tests_default and courtesy_disconnects_default)", and `baseline.params` names both keys. A reader of the computation document alone computes a definite number. **F-4 closed.**
- Carry-in ladders: three tiers each, pairwise distinct outcomes:
  - reserve basis 12m/365, 6m/182, last bill/30;
  - hold whole, 50 %, 0;
  - late 6/3/0; reconnect 6/3/0; patronage 6/3/0.
  Every fall-through equals the baseline. Every tier is stated in the rule. Bindings are disjoint.
- Realism of the new conditions and outcomes:
  - Holding back a recent check or e-check payment that may still bounce (in full when the account has a recent return) is a standard credit-balance refund control.
  - Late-charge and reconnect history lengthening a hold-back is a risk adjustment of the same kind as O-7.
  - The fall-through (credit less unbilled usage, no hold) is the ordinary treatment.
  - Restore pledge tiers: waiving the cushion when a government agency has committed funds, and covering only fixed charges when a charity grant will meet usage, are plausible published treatments.

PASS.

### findings (r2, charter-global)

- F-1 **closed**: no extended policy computes a deposit credit any more, and the deposit charter sentence no longer competes with any scored quantity of this difficulty. The base prepay/deposit interest wording conflict remains as a pre-existing base/base observation and touches no task (neither world seeds a deposit).
- F-2 **closed** (moot): the policy that omitted final-billed accounts no longer exists.
- F-3 **closed**: see factor_ladders (r2).
- F-4 **closed**: see factor_ladders (r2).
- O-2 addressed (rule states one DM allocation per year). O-3 closed (before-the-fast-test condition in rule and compute). O-1 and O-4 to O-7 unchanged, as claimed.
- New observations:
  - **R2-O1**: the new uuid8 69e6c97d shares its "69" prefix with the uuid8 of the tool it replaced (69d45e15). Independent generation cannot be proved or disproved from two characters, so no consequence is shown.
  - **R2-O2**: two extended policies supersede the same base credit-adjustment sentence, leaving billing_error_correction and estimated_read_correction without a governing sentence. No policy or task produces those reasons.
  - **R2-O3**: the carry-in compute reads the current account_balance for "the credit balance … when the enrollment is taken". This is checked per task.

### closing_checklist (r2)

Written 2026-10-06 19:45 UTC, after both round-2 reveals. It sits below the frozen r2 charter-global sections, and the round-1 closing checklist above is left as it was.

| task | SOURCE-POLICY | problem tree | factors | unique solution | verdict r2 |
|---|---|---|---|---|---|
| 0 | PASS | PASS | PASS | PASS (30.59, then 102.19) | **PASS** |
| 1 | PASS | PASS | PASS | PASS (14.77, 61, then 56.80) | **PASS** |

- **Files:** `0.md` and `1.md` match the tasks one-to-one. Each carries a round-1 section and an appended `## revision_2`; the round-1 text is untouched.
- **Round-1 findings:**

  | item | status |
  |---|---|
  | F-1 | closed |
  | F-2 | closed (moot) |
  | F-3 | closed |
  | F-4 | closed |
  | O-2, O-3 | addressed |
  | alert-history observation | addressed |
  | false design-rationale claims | corrected |
  | O-1, O-4 to O-7 | unchanged, still observations |

  New observations R2-O1 to R2-O3 have no demonstrated consequence.
- **Coverage:** `charter_scope` is {postpaid_credit_carry_in, activation_payment} for task 0 and {meter_error_refund, disconnect_alert_reset, restore_payment} for task 1. The scopes are pairwise disjoint and cover all five extended policies. Five tools, each with a distinct uuid8.
- **Trees:** task 0 has 1 prerequisite problem and 1 value_input edge; task 1 has 2 prerequisite problems and 2 value_input edges. Each tree has an owner=user root, and the difficulty graph is acyclic with no cross-task edges.
- **Factors:** every computation has 4 to 6 factors, with ≥2 parameter and ≥1 honest method. Each task has a multi-source factor (uncleared_payment_hold and payment_habit_cover_days in task 0; repeat_disconnection_restore_target and payment_lag_warning_days in task 1) and seeded cross-difficulty factors. Every factor bears weight against an honest baseline, and each baseline alone gives a definite number different from gold.
- **Gates:** the orchestrator's final-form run `/tmp/orch43/snap_prepay_power_enrollment_and_balances_r2.txt` is all green (check_traceability still deferred until the KB is published). The auditor did not re-run the gates.

**The difficulty passes the source-layer audit in revision 2.**
