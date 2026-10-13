# Policy-task audit — bank_deposit_transfers / charter-global

## charter_global_frozen

- Frozen: 2026-10-04 ~16:37Z (UTC), before any task's GT was revealed (first reveal: 16:39:50Z). Timestamp corrected after the fact: an earlier draft of this line carried an estimated time; the write order was _difficulty.md, 0.md, 1.md, then the reveal. Auditor: erl-task-policy-audit (independent Claude agent; not the author of the artifacts).
- Inputs read (sha256 checked against the source files and `/tmp/erl0030_views/policy_task/bank_deposit_transfers/VIEW_MANIFEST.txt`, all identical):
  - `bank.extended.yaml` d91d5af1071afe935657a2cb0aadf82751db733b5ace68edd7a1ba171b80c807
  - `task_tools.py` cd563e18f1e9c3989282295d916260dbc69097a77c7e51a627c2d8135c9401e9
  - masked `tasks/0.json` a0e5725d…8712, masked `tasks/1.json` 618d35ec…1062 (kept: frozen_time, user_scenario, initial_state only)
  - blueprint: `blueprint/blueprint.yaml`, `blueprint/db_schema.json` (table list), `blueprint/share_tools.py`, `blueprint/products/bank.yaml`; for level numbers / business-day definition / cross-difficulty event names only: `products/account.yaml`, `products/cash.yaml`, `products/wallet.yaml` (variant and event headers).
- Masked and not read when this file was written: `evaluation_criteria`, `computations`, `charter_scope`, `required_documents`, `design_rationale`, `solvability_contract`, `prerequisite_closure`, `db_closure*`, every `worklog.md`, every existing audit. No recursive grep was run over `env/` or `tasks/`.
- Base copy: lines 1–1506 of `bank.extended.yaml` are byte-identical to `blueprint/products/bank.yaml` (`diff` shows only the 4 added comment/blank lines 1507–1510 that open `extended_policies`).

### entry_conditions (Step 0)

- Gate snapshot supplied (`/tmp/erl0030_gates/bank_deposit_transfers.txt`): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK; traceability not run (no KB yet) — as stated in the brief.
- Masked views supplied with hashes — present and verified.
- Observation O-0: the `replay_tasks.py` section of the snapshot prints a row only for `1.json` (`1.json 13 True True 0 32 32 True`) followed by `REPLAY OK`; no `0.json` row appears. Whether the script prints only some rows cannot be told from the snapshot; per the skill the gates were not re-run by the auditor. Recorded as an input observation, not a red light.

### policy_conflict_scan

Extended policies (4) and the subjects they write:

| policy | trigger | target_tool (owner) | subject | computes |
| --- | --- | --- | --- | --- |
| bank_ext_late_delivery_refund | state_due | refund_late_delivery_fee_f06ff624 (agent) | bank_fee_refunded | refund_amount_usd |
| bank_ext_recall_fee | on_request | request_transfer_recall_f96dc6b4 (user) | bank_recall_requested, bank_fee_charged | recall_fee_usd |
| bank_ext_shortfall_credit | state_due | book_shortfall_credit_979e59e7 (agent) | bank_paloma_credit | credit_amount_usd |
| bank_ext_shortfall_delivery | on_request | choose_shortfall_delivery_49c1959f (user) | bank_remedy_chosen, bank_payout_sent | receive_amount |

Overlaps checked:
- `bank_fee_refunded`: base on_time_promise (late_delivery), cancellation (cancellation_in_window / post_window), refunds (compliance_cancellation), returns (return_paloma_attributable), error_resolution (paloma_error); extended late_delivery_refund. Distinct `fee_refund_reason`; the shared dedup "Each fee charge is refunded at most once." (bank_evt_cancellation) and "The transfer fee is refunded at most once on a transfer, so the on-time refund and an error-resolution fee refund never stack." (bank_evt_on_time_promise) give one reading: once the late-delivery refund (now partial) is booked against the transfer-fee charge, no paloma_error refund of that charge follows. No conflict; see observation O-6.
- `bank_paloma_credit`: base returns (fx_shortfall), error_resolution (error_refund / error_redelivery / incorrect_amount_shortfall); extended shortfall_credit takes over the incorrect_amount_shortfall amount by a declared overwrite. No conflict.
- `bank_fee_charged` (recall_fee): base recall + pricing; extended recall_fee by declared overwrite. bank_evt_pricing "Fees and limits are never recalculated after booking except by a re-quote, a resend or a refund rule." governs booking fees and does not bear on a fee first charged at the recall request. No conflict.
- `bank_remedy_chosen` / `bank_payout_sent`: base error_resolution (remedy) and release_and_holds (payout attempt 1); extended shortfall_delivery writes a remedy + new payout attempt by declared overwrite. Inherited base gates still apply: error_found_first, resend cap "One transfer may be sent again at most max_resends times in total (bank_msr_resends)" (a shortfall delivery is a payout_attempt >= 2).
- Eligibility / time anchors: late refund — "deposited after its date of availability" (date_available as last disclosed) ; recall — deposited status, recall_window_days from deposited_date, one recall; shortfall — error_found on the incorrect_amount notice. No two policies anchor the same scored quantity on different clocks.
- Cross-category read boundaries: late_delivery reads cash ledger (count, sum of cash_payout_made, 12 months); recall reads account level + opened_date; shortfall_credit reads account level; shortfall_delivery reads account level + opened_date and wallet ledger (count of wallet_credit_sent, 12 months). Each is declared in the policy's `cross_category` with the fields read.
- Scope exclusivity: from the prerequisite graph the charter has exactly two trees, {bank_ext_recall_fee <- bank_ext_late_delivery_refund} and {bank_ext_shortfall_delivery <- bank_ext_shortfall_credit}; with M=2 the only exclusive and complete assignment is one tree per task. The tasks' `charter_scope` fields are masked at this stage; the comparison is made in each task file after reveal.

### rule_compute_equivalence

Mechanical check (script, deleted): every `compute_basis` value is a verbatim substring of its policy's `rule`; every `baseline.rule` sentence is a verbatim sentence of the `rule`; every `overwrite.superseded_clause` is verbatim in the named base rule and every `replaced_by` verbatim in the extended rule — all True for all four policies.

Sentence-by-sentence sweep:
- late_delivery_refund: transfer-fee base (`fee_collected`, filter fee_type transfer_fee) <- "the transfer fee collected"; three-branch `days_late` <- the "lateness clock" sentence (booking-anchored less delivery_business_days; answer-anchored less hold_review_business_days and delivery_business_days; else from date_available); `delay_share` thresholds >= long, >= mid <- "reach"; pickup ladder: high = count AND sum, mid = count OR sum, window `within_months=12` <- "fewer than twelve whole calendar months"; principal ladder at/above; `MN(full_share, ...)` <- "never more than the full share"; one `RND(...,2)` at the end <- "rounded half up to the cent once at the end". Eligibility sentences (on-time tier, deposited late, customer-lateness exclusions) are gates, not compute. No invented basis, no empty promise.
- recall_fee: `LATEST payout_sent amount` <- "the latest payout sent"; basis ladder (rate in place of fee / fee + add-on / fee); standing share with `level >= 5 & tenure >= 24`, `3 <= level < 5 & tenure >= 36`, else 100 <- rule; `MONTHS(opened_date, NOW)` <- "never from the date its current level took effect"; prompt reduction `<= 3`, `<= 10` days after deposited_date; recovery `count(late_delivery refunds) >= 1` and `DAYS(date_available, deposited_date) >= 3 / >= 1`; order basis -> share -> minus prompt -> minus recovery, `MX(0, …)`, one rounding <- "worked out in this order". Equivalent.
- shortfall_credit: `shortfall_local`, `partner_rate_gap_pct`, three-way valuation, goodwill (>=14 / >=7 days notice -> decision), notice credit (<=7 / <=30 days date_available -> notice), size credit (funds_received + fee_charged >= 1000 / >= 500), result formula. Observation O-4: `finding_date` filters `bank_error_decided` by `case_outcome='error_found'` only, while the rule speaks of "the decision finding the error" on "the incorrect-amount notice"; on a transfer carrying an error_found decision on another notice type the compute would read that row. No task world of this difficulty carries such a row, so no consequence is demonstrable here.
- shortfall_delivery: make-good held = received + credits − payouts − refunds; booking reference `fx_rate / (1 − fx_margin_pct/100)`; margin ladder by level; delay uplift (batch: `MN(cap, weekly × whole weeks)`, real-time: flat, else 0; long wait >= 21 days from the latest payout's date); wallet bonus by 12-month wallet_credit_sent count; tenure bonus by months from opened_date; `RND(...,4)` rate, `RND(...,2)` amount. Equivalent. The "date of availability is the choice date plus the tier's redelivery business days, counted in Paloma business days" sentence is a tool argument not in `compute`; "Paloma business day" is defined in the account charter (Monday to Friday, excluding US Federal Reserve holidays).

Every factor ladder's tiers are each a sentence of the `rule` and a branch of the `decides` binding, and vice versa (checked per factor; see factor_ladders).

### action_binding_and_uuids

- Each `(target_tool, computes)` is claimed by exactly one policy (table above); four distinct tools, no shared target.
- uuid8s: f06ff624, f96dc6b4, 979e59e7, 49c1959f — pairwise distinct, no common prefix beyond a single hex digit, no sequence pattern; not batch-derived on their face.
- Function bodies (`task_tools.py`): each performs only `ctx.find` of the transfer, `ctx.create` of the ledger/case row(s) and `ctx.update` of held amounts / status; none checks a prerequisite, an eligibility gate or an amount, none refuses or hints. No docstring names another tool.
- Observation O-5: two docstrings carry the word "after" — `book_shortfall_credit_979e59e7` ("after Paloma's error-resolution team found an incorrect amount on that transfer") and `choose_shortfall_delivery_49c1959f` ("after Paloma found an incorrect amount on a Bank Deposit transfer"). Both refer to the base error decision (a seeded system event), not to the position of either task write relative to the other; neither docstring states the credit-before-delivery order. `refund_late_delivery_fee_f06ff624`'s "after its promised date of availability" is a lateness description. No consequence on any tree; observation only.

### prerequisite_graph

| blocked policy | problem | kind | gate (binding) | form | resolved_by |
| --- | --- | --- | --- | --- | --- |
| bank_ext_recall_fee | bank_ext_late_delivery_refund | value_input | late_refunds_booked (exists in recall compute) | state | refund_late_delivery_fee_f06ff624 = late_delivery target_tool |
| bank_ext_shortfall_delivery | bank_ext_shortfall_credit | value_input | make_good_held_usd (exists in delivery compute) | state | book_shortfall_credit_979e59e7 = shortfall_credit target_tool |

- `prerequisite` filled on all four (`[]` on late_delivery_refund and shortfall_credit). Every `problem` is an extended policy id of this file, never a base policy, never self. Graph acyclic (two disjoint edges).
- `policy_source` verbatim in the blocked policy's own rule (checked mechanically) and in no other extended rule.
- No `fallback_reason` (both state form) — correct.
- `condition` vs sentence strength: edge A "any late-delivery refund owed" <-> condition "Whenever the transfer is owed a late-delivery refund … a fee refund with the reason late delivery … stands on the ledger" (same conditional scope). Edge B "Paloma's make-good credit for the incorrect amount" <-> condition "A credit from Paloma for an incorrect-amount shortfall … stands on the transfer's ledger" (same).
- `effect`: edge A — the late-delivery count enters `recovery_reduction`; edge B — the credit enters `make_good_held_usd`. Both genuinely change the binding. Observation O-7: edge B's `effect` says the held principal "rises from zero"; that is true of a deposited transfer whose principal has all been paid out, but is a world assertion inside general text; no consequence.
- No authoring-viewpoint wording ("in this task", "at the opening") in any `prerequisite` field.

### prerequisite_sentences

Edge A — "The recall fee is fixed only after the transfer's ledger carries any late-delivery refund owed on its transfer fee."
1. Ordering connective: "only after", joining the recall fee (this policy's own result) to the waited-on state. Pass.
2. State form: "the transfer's ledger carries any late-delivery refund owed on its transfer fee" — a ledger state in the finders' words (money movements, fee refund, late delivery); no action, performer or tool. Pass.
3. No tool name, no policy id, no snake_case, no row id. Pass.
4. Strength/scope: "any … owed" is an open conditional matching the edge condition. Pass.
- Exactly one write of the difficulty brings the state about: `refund_late_delivery_fee_f06ff624` (the only tool writing `fee_refund_reason=late_delivery`; no share tool writes the ledger). Pass.
- Derivation (single reading): sentence -> reader checks the ledger for a late-delivery fee refund -> if none, asks whether one is owed -> the late_delivery_refund rule ("On a tier that carries the on-time promise, a transfer deposited after its date of availability is owed a late-delivery refund on its transfer fee, booked as one refund against the transfer-fee charge with the reason late delivery …") names the owed state and how it is booked -> resolving write = the late-delivery fee refund. No second reading.
- The late_delivery_refund rule does not restate the sentence and mentions no recall. Pass.

Edge B — "The shortfall delivery is not made until the transfer's ledger carries Paloma's make-good credit for the incorrect amount."
1. "not … until". Pass. 2. State form (ledger carries a credit). Pass. 3. No tool/id/snake_case. Pass. 4. Scope matches. Pass.
- One write brings it about: `book_shortfall_credit_979e59e7` (only writer of `credit_reason=incorrect_amount_shortfall`). Pass.
- Derivation: sentence -> ledger shows no incorrect-amount credit -> shortfall_credit rule ("When an incorrect amount is found, Paloma puts its make-good credit into the transfer, booked as a credit for an incorrect-amount shortfall against the payout that came up short …") -> resolving write = that credit. Single reading.
- The shortfall_credit rule does not restate the sentence. Pass.

Undeclared cross-problem orders: none found in the four extended rules. Base rules: bank_evt_error_resolution "A remedy can be chosen only after a decision of error_found on that notice." orders a remedy after a system decision (not an extended problem; seeded); "Paloma credits the shortfall … and the customer chooses to have the shortfall delivered" uses "and", not an ordering connective; no tree rests on a base sentence, since edge B is carried by the extended rule's own sentence. Observation only.

### override_declarations

Sentence-by-sentence against `base_policy_refs` (finding half only):

bank_ext_late_delivery_refund (refs: cancellation, error_resolution, on_time_promise)
- on_time_promise S1 "Paloma refunds the transfer fee in full, with fee_refund_reason late_delivery …" — handled differently (partial share) — declared (overwrite 1).
- S2 "The promise does not apply when the lateness came from the customer: wrong beneficiary details the customer supplied, or a request for information the customer answered after rfi_response_days." — handled differently (customer-supplied details count as customer lateness only when a payout came back) — declared (overwrite 2).
- S3 "covers the transfer fee only" — followed (`fee_type='transfer_fee'`). S4 "may claim it … without giving an error notice" — followed. S5 "refunded at most once … never stack" — inherited. S6 "on_time_promise false gives no automatic fee refund" — followed ("On a tier that carries the on-time promise").
- cancellation: "Each fee charge is refunded at most once." — inherited (one refund against the charge). Other cancellation sentences govern cancellation refunds, untouched.
- error_resolution: "On error_found every fee collected … refunded with fee_refund_reason paloma_error, unless it was already refunded under the on-time promise." — untouched; interacts with the partial refund (O-6). "no_error when … beneficiary details the customer supplied were wrong" decides error notices, not the on-time refund; the on-time exclusion that mirrored it is the declared overwrite 2.
- No undeclared override.

bank_ext_recall_fee (refs: recall, pricing, amend_resend)
- recall "recall_fee_usd is collected when the recall is requested, as fee_type recall_fee with the deposited payout's payout_attempt, and is not refunded whatever the outcome." — amount replaced — declared. "The customer requests the recall and accepts its fee." — followed. deposited-only, window, one-recall, outcome handling, recall vs wrong_account notice — inherited.
- pricing "Fees … never recalculated after booking except by a re-quote, a resend or a refund rule." — not about recall fees; no conflict. amend_resend — nothing in it governs the recall fee.
- No undeclared override.

bank_ext_shortfall_credit (refs: returns, error_resolution)
- error_resolution "For incorrect_amount, Paloma credits the shortfall (bank_paloma_credit, credit_reason incorrect_amount_shortfall)" — amount replaced — declared. The fee-refund-on-error_found sentence and the notice/decision gates — inherited.
- returns: fx_shortfall credit on Paloma-side returns — different reason, untouched.
- No undeclared override. (Anonymous-intermediate / 0-1 multiplier / dropped branch: none found — the bare shortfall at the locked rate survives as the fall-through valuation tier.)

bank_ext_shortfall_delivery (refs: error_resolution, release_and_holds)
- error_resolution "the customer chooses to have the shortfall delivered (resend_shortfall) or refunded (refund_shortfall, booked with refund_basis error_shortfall)" — the delivered amount replaced; refund choice retained — declared. "The choice is the customer's own"; "a delivery within redelivery_business_days Paloma business days of the choice" — followed (date_available sentence).
- release_and_holds: payout attempt numbering — followed (new attempt). Base amend_resend resend cap (not in refs) — inherited, not weakened.
- No undeclared override.

### factor_ladders

| policy | factor | effect | decides | bindings | tiers (fall-through last) | cross_difficulty | multi-source tiers |
| --- | --- | --- | --- | --- | --- | --- | --- |
| late_delivery_refund | lateness_clock | method | days_late | hold_on_record, rfi_answers_logged, latest_rfi_answer_date, days_late | booking-anchored / answer-anchored / availability-anchored | — | yes (transfer.held_at AND case-file RFI answers) |
| | delay_share | parameter | delay_share | days_from_availability, delay_share | 70 / 45 / 30 | — | no |
| | pickup_points | parameter | pickup_points | pickup_payout_count, pickup_paid_usd, pickup_points | 15 / 8 / 0 | cash | count AND/OR sum (same ledger rows) |
| | principal_points | parameter | principal_points | principal_collected, principal_points | 10 / 5 / 0 | — | no |
| recall_fee | recall_fee_basis | method | recall_fee_basis | payout_recalled_usd, recall_fee_basis | % of payout / fee + add-on % / listed fee | — | no |
| | recall_standing_share | parameter | standing_share | account_level_number, account_tenure_months, standing_share | 50 / 70 / 100 | account | level AND tenure |
| | prompt_request_reduction | parameter | prompt_reduction | days_since_deposit, prompt_reduction | 4.00 / 2.00 / 0 | — | no |
| | service_recovery_reduction | parameter | recovery_reduction | late_refunds_booked, deposit_gap_days, recovery_reduction | 2.75 / 1.25 / 0 | — | yes (ledger late refund AND transfer dates) |
| shortfall_credit | shortfall_valuation | **method (label contested, F-1)** | shortfall_value_usd | payout_rate_applied, partner_rate_gap_pct, valuation_level_number, shortfall_value_usd | ÷ payout rate / ÷ mean(locked, payout) / ÷ locked | account | yes (ledger payout rate, transfer fx_rate, account level) |
| | decision_goodwill | parameter | goodwill_pct | notice_date, finding_date, goodwill_pct | 8 / 4 / 0 | — | yes (notice row AND decision row) |
| | notice_credit | parameter | notice_credit_usd | notice_lag_days, notice_credit_usd | 1.50 / 0.75 / 0 | — | no |
| | transfer_size_credit | parameter | transfer_size_credit_usd | customer_paid_usd, transfer_size_credit_usd | 2.00 / 1.00 / 0 | — | no |
| shortfall_delivery | delivery_margin | parameter | delivery_margin_pct | delivery_level_number, delivery_margin_pct | 0 / 0.45 / tier fx_margin_pct | account | no |
| | delay_uplift | method | delay_uplift_pct | short_payout_date, wait_days, delay_uplift_pct | weekly accrual capped / flat / none | — | yes (payout ledger date AND tier rail) |
| | wallet_rate_bonus | parameter | wallet_rate_bonus | wallet_credits_12m, wallet_rate_bonus | 0.02 / 0.01 / 0 | wallet | no |
| | tenure_rate_bonus | parameter | tenure_rate_bonus | tenure_months, tenure_rate_bonus | 0.03 / 0.015 / 0 | account | no |

Structure checks:
- Counts as declared: each policy 4 factors (3 parameter + 1 method). Per tree: {late_delivery, recall} has multi-source (lateness_clock, service_recovery, standing share) and cross-difficulty (cash, account); {credit, delivery} has multi-source (shortfall_valuation, goodwill, delay_uplift) and cross-difficulty (account, wallet).
- Bindings disjoint within each policy; every `decides` is an input, never `result`.
- Every ladder has three pairwise-disjoint tiers; no two tiers share a value or method (delivery margin fall-through is the tier margin, which is 0.95/1.10/1.65/1.25/0.55/0.85 by tier — never 0 or 0.45; the batch accrual tier needs >= 21 days, i.e. >= 3 whole weeks = >= 0.75, never equal to the flat 0.50).
- Every tier (condition and value/method) is stated in the `rule` prose and implemented in `compute`; no tier lives only in compute.
- Every factor's fall-through equals its `baseline`, and each `baseline` equals what the policy's `baseline.rule` states (standard share; listed fee charged in full; locked-rate valuation and zero goodwill/credits; tier margin and zero bonuses/uplift).
- Method-label honesty: lateness_clock (three different anchoring algorithms), recall_fee_basis (percentage-of-payout vs flat-plus-percentage vs flat) and delay_uplift (accruing weekly schedule with cap vs flat vs none) change how the quantity is computed. **shortfall_valuation does not** — see F-1.
- Observation O-1 (structure): the `delay_share` factor lists `days_from_availability` among its bindings although its ladder reads `days_late` (lateness_clock's binding); `days_from_availability` is lateness_clock's baseline input. Bindings remain disjoint and the ladder is stated correctly; no consequence.
- Observation O-2 (realism): recall_fee_basis's large-payout tier replaces the listed fee by 0.10 % of the payout, so at the floor (25,000.00 -> 25.00) the fee falls below the mid tier just under it (24,999.99 -> 15.00 + 0.06 % = 30.00). A non-monotone fee across a band edge; not reached by any task world of this difficulty.
- Observation O-3 (realism): shortfall_delivery's wallet and tenure bonuses are absolute rate points (0.01–0.03 payout-currency units per USD) applied identically across corridors whose rates range from about 1 (SV-USD) to tens of thousands (VN-VND), and shortfall_valuation / delivery_margin vary a Regulation E error remedy by verification level. These are judged against what the industry publishes; the evidence available here does not demonstrate that no such business would publish them, so they are observations.

### findings

**F-1 — SOURCE-FACTOR RED (mislabelled effect) — bank_ext_shortfall_credit / factor `shortfall_valuation`. Bears on the task whose tree contains bank_ext_shortfall_credit (expected: task 1, by the scope argument above).**
- Symptom: the factor is labelled `effect: method`, but all three tiers compute the same formula with a different number substituted.
- Root cause: the tiers differ only in the divisor rate: `shortfall_value_usd = shortfall_local / R`, with `R = payout_rate_applied` (tier 1), `R = (F('fx_rate') + payout_rate_applied) / 2` (tier 2), `R = F('fx_rate')` (tier 3).
- Evidence: `bank.extended.yaml` bank_ext_shortfall_credit `compute.shortfall_value_usd`: "(shortfall_local / payout_rate_applied) if (…) else ((shortfall_local / ((F('fx_rate') + payout_rate_applied) / 2)) if (…) else (shortfall_local / F('fx_rate')))"; `factors[shortfall_valuation].ladder` methods "divided by the rate the latest payout applied" / "divided by the average of the locked rate and the rate the latest payout applied" / "divided by the locked exchange rate". The skill names "a rate" as the canonical case of a number substitution that a `method` label may not carry; within this same charter the analogous rate choice `delivery_margin` is labelled `parameter`.
- Demonstrated consequence: counting only honestly labelled factors, bank_ext_shortfall_credit has 0 `method` factors (decision_goodwill, notice_credit, transfer_size_credit are all number substitutions; shortfall_valuation is a number substitution too), against the floor of 1 `method` per computation. Relabelled as `parameter` it still counts as a factor (4 in total, 4 parameter, 0 method) — the computation fails the method floor either way.
- Affected artifact: `tasks/bank_deposit_transfers/bank.extended.yaml`, `extended_policies[bank_ext_shortfall_credit].factors[0]` (effect label) and the policy's factor set as a whole; the task file whose `computations` include this policy.

Observations O-0 … O-7 above (gate snapshot row, delay_share bindings, recall basis band edge, absolute rate bonuses / level-varied Reg E remedy, error_decided filter, docstring "after", partial late refund vs error-resolution fee refund, edge-B effect wording) — none demonstrates a consequence on a task world of this difficulty.

O-6 (detail): after a partial late-delivery refund (e.g. 88 % of the transfer fee), base error_resolution "On error_found every fee collected on the transfer is refunded with fee_refund_reason paloma_error, unless it was already refunded under the on-time promise" together with "Each fee charge is refunded at most once" leaves the unrefunded remainder of the transfer fee permanently unrefundable. The reading is unique (the charge was already refunded once); it is recorded because the extended partial refund changes what the base sentence delivers to the customer without the base sentence being named in the late_delivery overwrite. No task world in this difficulty carries an error_found on a late-refunded transfer.

## closing_checklist

Written after both reveals (everything above this heading was written before any reveal and is unchanged).

The difficulty does **not** close: task 1 is SOURCE-FACTOR RED. Checklist status:

- Audit files: `0.md`, `1.md` one-to-one with tasks 0 and 1, `_difficulty.md` alongside; no previous revision existed (first round). Comparison verdicts: task 0 PASS, task 1 SOURCE-FACTOR RED.
- Coverage and scopes: `charter_scope` task 0 = {bank_ext_late_delivery_refund, bank_ext_recall_fee}, task 1 = {bank_ext_shortfall_credit, bank_ext_shortfall_delivery}; pairwise disjoint, union = all four extended policies; each scope spans its whole tree. Task tools disjoint and each used by exactly one task; uuid8s independent (§ action_binding_and_uuids). — holds.
- Trees: each has 1 prerequisite problem, 1 value_input edge, 1 owner=user root write, no cycle; the difficulty's graph is two disjoint edges, acyclic. — holds.
- Computations: every computation has a self-sufficient baseline (3.00, 15.00, 32.74, 293.76 — all definite, all ≠ gold) and four factors that each bear weight on their task's world. Fails on one point: bank_ext_shortfall_credit has no honestly labelled `method` factor (F-1; demonstrated in `1.md` T1-F1).
- Instantiation-stage gates: not re-run by the auditor (the skill assigns the gate run to the coordinator); the supplied snapshot is green with observation O-0 (no `0.json` replay row printed).

Per-task verdicts: task 0 — PASS on all four relationships; task 1 — SOURCE-FACTOR RED (T1-F1 mislabelled method factor, T1-F2 proof arithmetic misstatement); policy self-consistency, problem tree and unique solution PASS.

---

## revision_2

### charter_global_frozen (revision 2)

- Frozen 2026-10-04 (UTC, after 17:10Z), before any round-2 GT was revealed. Auditor: same independent erl-task-policy-audit agent as round 1. Round-1 text above is left untouched.
- Inputs (sha256, checked against sources and `/tmp/erl0030_views/policy_task/bank_deposit_transfers/VIEW_MANIFEST.txt`; round-1 manifest `/tmp/erl0030_views/manifests/bank_deposit_transfers.r1.txt`):
  - `bank.extended.yaml` 99836ed274bb227d6dc998ec22b07fd6d9308fad7e9acd0e30c6bc2688ffa34f (round 1: d91d5af1…c807) — **changed**
  - `task_tools.py` cba3c2a7def924f5afab6f3a2baaa6f67ec381a6834d5837cffb8f28f86fc6f7 (round 1: cd563e18…01e9) — **changed**
  - masked `tasks/0.json` bb4a50c2…fc45 (changed), masked `tasks/1.json` 618d35ec…1062 (unchanged view; masked fields changed per brief)
- Because both shared inputs changed, every charter-global section is re-derived in full below (not carried forward).
- Base copy: lines 1–1506 still byte-identical to `blueprint/products/bank.yaml`.
- Masked and unread at this freeze: round-2 evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, db_closure*; worklogs; other scenarios and sibling difficulties.
- contamination_disclosure: this auditor revealed and read the round-1 GT of both tasks in round 1 (recorded in `0.md` / `1.md` round-1 comparison sections). The round-2 derivations are recomputed from the round-2 charter and views; where a round-2 figure equals a round-1 GT figure, that equality is the auditor's recomputation, but independence from the round-1 GT cannot be claimed in the strict sense. No round-2 GT field was seen before the freezes.

### entry_conditions (revision 2)

Gate snapshot `/tmp/erl0030_gates/bank_deposit_transfers.r2.txt`: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK with rows for both `0.json` (13 acts, det True, 0 errs, 33/33 match) and `1.json` (32/32 match), SOLVABILITY OK, COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK, all exit 0. Traceability deferred to the KB stage. Round-1 O-0 (no `0.json` replay row) is closed by this snapshot.

### What changed in the charter and tools (auditor's own reading; not the reworker's list)

- bank_ext_late_delivery_refund: text, params, compute, factors and baseline read identical to round 1 (all parameter values re-read: 30/45/70, 3/6, 5/1800, 3/1000, 15/8, 5000/2000, 10/5, 100).
- bank_ext_recall_fee: `large_payout_rate_pct` 0.10 -> **0.12**; everything else as in round 1.
- bank_ext_shortfall_credit: valuation factor rebuilt as `valuation_rate` (effect **parameter**, decides `valuation_rate`; `shortfall_value_usd = shortfall_local / valuation_rate`); new rule sentences "The shortfall value is the payout-currency shortfall divided by the valuation rate." and "The standard valuation rate is the transfer's locked exchange rate."; `decision_goodwill` relabelled **method** with a new slow tier ("accrues the weekly goodwill percentage for every whole week between the notice and the decision, never more than the goodwill cap"; params `weekly_goodwill_pct: 3`, `goodwill_cap_pct: 12`, `slow_goodwill_pct` removed); `finding_date` now filters `case_type='incorrect_amount'` and the rule reads "the decision finding the error on that notice"; new binding `decision_days`.
- bank_ext_shortfall_delivery: wallet and tenure bonuses are now percentages of the booking-day reference (`high/mid_wallet_bonus_pct` 0.20/0.10, `long/mid_tenure_bonus_pct` 0.30/0.15); delivery rate `RND(ref × (100 − margin + wallet + tenure)/100 × (100 + uplift)/100, 4)` with matching rule/baseline prose; edge-B `effect` now "rises by the credited amount".
- task_tools.py: docstrings of `refund_late_delivery_fee_f06ff624` ("later than its promised date of availability"), `book_shortfall_credit_979e59e7` ("on a transfer where Paloma's error-resolution team found an incorrect amount") and `choose_shortfall_delivery_49c1959f` ("on a Bank Deposit transfer where Paloma found an incorrect amount") no longer carry "after"; remaining "after" occurrences are "recorded … after rounding" / "afterwards" (no sequence). Function bodies (AST) are unchanged in shape: assignments, `ctx.create`/`ctx.update`, return — no condition, no raise, no refusal.

### policy_conflict_scan (revision 2)

Same four policies, tools, owners, subjects and `computes` as round 1; overlaps on `bank_fee_refunded`, `bank_paloma_credit`, `bank_fee_charged`, `bank_remedy_chosen`/`bank_payout_sent` resolve exactly as in round 1 (distinct reason codes, declared overwrites, inherited dedup and resend cap). No new overlap. Cross-category reads declared: cash (late refund), account (recall, credit, delivery), wallet (delivery). Two trees, one per task, is still the only exclusive complete split.

### rule_compute_equivalence (revision 2)

Mechanical (script, deleted): all `compute_basis` values verbatim in their rules; `compute` keys = `compute_basis` keys for all four; every `baseline.rule` sentence verbatim in its rule; overwrite clauses verbatim on both sides; factor bindings disjoint and all existing compute bindings.
Sentence sweep of the changed parts:
- credit: `valuation_rate` three branches <-> "The valuation rate depends on that gap: …" (rate applied / average / locked); `shortfall_value_usd` <-> "divided by the valuation rate"; `decision_days = DAYS(notice_date, finding_date)` <-> "counted in calendar days from the incorrect-amount notice to the decision finding the error on that notice"; `goodwill_pct = MN(cap, weekly × int(days/7))` if >= 14, flat 4 if >= 7, else 0 <-> the goodwill sentence. `finding_date` filters case_type incorrect_amount + error_found: closes round-1 O-4 (the compute reads the latest error_found decision of the incorrect-amount type; the rule's "on that notice" and the compute coincide whenever one incorrect-amount notice is open at a time, which bank_evt_error_resolution's "Only one notice of each case_type may be open" secures).
- delivery: rate formula prose <-> compute (percentage points added to 100 − margin, then × (100 + uplift)/100, 4 dp). Equivalent.
No invented basis, no empty promise.

### action_binding_and_uuids (revision 2)

Unchanged bindings: one `(target_tool, computes)` per policy; uuid8s f06ff624, f96dc6b4, 979e59e7, 49c1959f unchanged and independent. No docstring names another tool or carries a sequence word (round-1 O-5 closed). Bodies validate nothing.

### prerequisite_graph and prerequisite_sentences (revision 2)

Unchanged edges: recall_fee <- late_delivery_refund (value_input, gate `late_refunds_booked`, state), shortfall_delivery <- shortfall_credit (value_input, gate `make_good_held_usd`, state). `policy_source` verbatim in the blocked rule only; gates exist in compute; no fallback (state form); acyclic; `prerequisite: []` on the other two. Edge B `effect` now reads "rises by the credited amount" (round-1 O-7 closed). The four-point test, single resolving write and single-reading derivation of round 1 hold unchanged for both sentences (texts identical). No undeclared cross-problem order in any extended rule.

### override_declarations (revision 2)

Same overwrites, verbatim on both sides. Sentence sweep of the changed policies: shortfall_credit still replaces only the base "For incorrect_amount, Paloma credits the shortfall …" amount; shortfall_delivery still replaces only the delivered amount; recall_fee only the fee amount. No undeclared override. Round-1 O-6 (partial late refund vs paloma_error fee refund) unchanged — still an observation, no task world exercises it.

### factor_ladders (revision 2)

| policy | factors (effect) | parameter / method | multi-source | cross_difficulty |
| --- | --- | --- | --- | --- |
| late_delivery_refund | lateness_clock (method), delay_share, pickup_points, principal_points | 3 / 1 | lateness_clock | pickup_points -> cash |
| recall_fee | recall_fee_basis (method), recall_standing_share, prompt_request_reduction, service_recovery_reduction | 3 / 1 | service_recovery, standing share | standing share -> account |
| shortfall_credit | valuation_rate (parameter), decision_goodwill (method), notice_credit, transfer_size_credit | 3 / 1 | valuation_rate (ledger rate, transfer rate, account level); decision_goodwill (notice row, decision row) | valuation_rate -> account |
| shortfall_delivery | delivery_margin, delay_uplift (method), wallet_rate_bonus, tenure_rate_bonus | 3 / 1 | delay_uplift | margin, tenure -> account; wallet -> wallet |

- Label honesty: `valuation_rate` now honestly `parameter` (selects a rate number). `decision_goodwill` as `method`: tier 1 is an accruing schedule, `min(12, 3 × whole weeks)`, a function of the decision delay; tier 2 is a flat 4; tier 3 none — the same accrual-vs-flat-vs-none structure accepted for `delay_uplift`. Honest. **Round-1 F-1 is closed**: every computation now has one honest method factor.
- Tier distinctness: goodwill slow tier needs >= 14 days -> >= 2 whole weeks -> >= 6 %, never the flat 4; wallet 0.20/0.10/0; tenure 0.30/0.15/0; margin 0/0.45/tier margin (never 0 or 0.45 on any tier). All ladders three tiers, disjoint, stated in the rule, implemented in compute, fall-through = baseline = what `baseline.rule` states.
- Round-1 O-1 (delay_share bindings list days_from_availability) unchanged — observation.
- Round-1 O-2 (recall basis band edge): with 0.12 % the Large Amount tier is now continuous at 25,000 (15.00 + 0.06 % × 24,999.99 = 30.00; 0.12 % × 25,000 = 30.00). The International Wire tier (listed recall fee 35.00, payouts to 50,000) still drops from 50.00 just below the floor to 30.00 at it. Partially addressed; observation (no task world reaches it).
- Round-1 O-3: the absolute rate-point bonuses are now percentages of the booking-day reference, corridor-proportional — that part is closed. The level-varied valuation/margin of a Regulation E remedy remains as before; observation.

### findings (revision 2)

- No charter-global red light in revision 2. F-1 closed (see factor_ladders). O-0, O-4, O-5, O-7 closed; O-2, O-3 partially addressed (residuals above, observations); O-1, O-6 unchanged, observations.
- New-defect sweep over the changed text: none found. Bears on: nothing; each task file re-demonstrates its own world below.

### closing_checklist (revision 2)

Written after the round-2 reveals (everything above in revision_2 was written before them).

- Audit files `0.md`, `1.md` with `_difficulty.md` alongside; round-1 text preserved, round 2 appended under `## revision_2`; every revision-2 comparison carries PASS (task 0 PASS, task 1 PASS).
- Coverage/scopes: task 0 {late_delivery_refund, recall_fee}, task 1 {shortfall_credit, shortfall_delivery} — disjoint, union = all four extended policies; tools disjoint; uuid8s independent and unchanged.
- Trees: each 1 prerequisite, 1 value_input edge, 1 owner=user write, acyclic; difficulty graph acyclic.
- Computations: all four have a self-sufficient baseline (3.00, 15.00, 32.74, 293.76 — definite, ≠ gold) and 4 factors (3 parameter + 1 honest method); every factor bears weight on its task's world; each task has multi-source and cross-difficulty factors with the other products' rows seeded.
- Gates: the coordinator's round-2 re-run on the final form is green with exit 0 for every gate (`/tmp/erl0030_gates/bank_deposit_transfers.r2.txt`); traceability deferred to the KB stage.
- Round-1 item ledger (verified on the artifacts, not taken from the reworker's claims): F-1/T1-F1 closed; T1-F2 closed; O-0 closed (the snapshot now shows both replay rows); O-4/T1-O3, O-5, O-7, T0-O2, T0-O3, T1-O1, T1-O2 closed; O-2 partially (Large Amount continuous, International Wire still drops 50.00 -> 30.00 at 25,000; and task 0's rework note overstates this, T0-O4); O-3 partially (bonuses now proportional; level-varied remedy remains); O-1, O-6, T0-O1 unchanged (observations).
- Regression: task 0's scored values are unchanged from round 1; only task 1's delivery figures moved, and they were re-derived blind.

**Difficulty bank_deposit_transfers passes the source-layer audit in revision 2: task 0 PASS, task 1 PASS.**

---

## revision_3

### charter_global_frozen (revision 3)

- Frozen 2026-10-04 (UTC), before any round-3 GT was revealed. Auditor: same independent erl-task-policy-audit agent. Rounds 1–2 text untouched.
- `bank.extended.yaml` 99836ed274bb227d6dc998ec22b07fd6d9308fad7e9acd0e30c6bc2688ffa34f and `task_tools.py` cba3c2a7def924f5afab6f3a2baaa6f67ec381a6834d5837cffb8f28f86fc6f7 — both **identical** to revision 2 (checked on the sources and on the view, and against the archived round-2 view `/tmp/erl0030_views/archive/bank_deposit_transfers.r1/`). Per the re-audit rule, every charter-global section of revision 2 (conflict scan, rule/compute equivalence, action binding and uuids, prerequisite graph and sentences, override declarations, factor ladders, findings) is **carried forward by reference** on the grounds of these two unchanged hashes; it is not re-derived.
- Masked views: `tasks/0.json` 7fd17bc7…8075 (source dfff2653…685d), `tasks/1.json` 83d2577f…e11e (source 0b997ea5…de5a). Masked GT fields unread at this freeze.
- contamination_disclosure: as in revision 2 — the auditor read both tasks' round-1 and round-2 GT in earlier rounds; no round-3 GT seen before the freezes.

### entry_conditions (revision 3)

Gate snapshot `/tmp/erl0030_gates/bank_deposit_transfers.r3.txt` (coordinator re-run): EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, TRACEABILITY (KB now published), SCOPE OK; CACHE-DIFF INFO; all exit 0; whole-scenario `validate_scenario` VALID. Not re-run by the auditor.

### clock_form (revision 3, shared — tools and runtime)

What changed (structural diff of the round-3 views against the archived round-2 views, every key and value): **only the top-level `frozen_time` of each task** — task 0 `'2026-09-18T11:20:00'` -> `'2026-09-18 11:20:00 CDT'`, task 1 `'2026-09-18T15:40:00'` -> `'2026-09-18 15:40:00 CDT'`. `user_scenario` and every `initial_state` row are byte-for-byte the same values. The reworker's "only frozen_time changed" claim holds for the visible fields.

Why it was needed: `erlbench/validate.py` requires `re.match(r"^\d{4}-\d{2}-\d{2}\b", frozen_time)`; in `2026-09-18T11:20:00` the "8" and the "T" are both word characters, so `\b` fails; `2026-09-18 11:20:00 CDT` passes.

Is it the same instant: the old stamp carried no zone. The runtime's operations clock is US Central (`db_schema.json` identity_verifications.verified_at / human_handoffs.created_at: "on Paloma's operations clock (US Central Time)"), and the charter's clocks are Central (`booking_cutoff_ct`). On 2026-09-18 Central is on daylight time, so `CDT` names the same wall-clock instant. Calendar date (2026-09-18), weekday (Friday) and time of day are unchanged.

How the clock is read (each reader checked):
- `erlbench/determinism.py` `Clock.now()` returns the stamp verbatim; `erlbench/loader.py` `engine_for` builds the clock from it unchanged. The docstring's example `"2025-11-14 03:40:00 EST"` is exactly the new form.
- Task tools (`task_tools.py` lines 42, 91, 141, 204): each reads only `today = ctx.now()[:10]` -> `"2026-09-18"` under both forms, so every written `entry_date` / `case_date` is unchanged. No tool reads the time of day.
- Shared tools (`blueprint/share_tools.py`): `verify_customer_identity` writes `verified_at=ctx.now()` and `transfer_to_human_agent` writes `created_at=ctx.now()` (raw stamp). These written values change form (`2026-09-18 11:20:00 CDT`). The gold replay and a rollout read the same clock, so they write the same string. No scored value of this difficulty is moved. Every lookup tool ignores the clock.
- Policy clocks used by this difficulty's computations and gates: late refund (DAYS between seeded dates; the 12-month window is counted to the *handling date*), recall (MONTHS opened_date->handling date, DAYS deposited_date->handling date, recall window in calendar days), credit (dates of seeded rows only), delivery (DAYS latest payout->handling date, MONTHS opened_date->handling date, date_available = handling date + 1 Paloma business day). Every one of them reads only the date part of NOW, which is 2026-09-18 under both forms. No elapsed-hour gate (rate lock, cancellation window, funding deadline) compares a seeded `…T…` timestamp with NOW in either task's gold path. The coordinator's COMPUTE and REPLAY gates confirm that the compute engine parses the new stamp, with match True on both tasks.

### findings (revision 3)

- No red light. The charter-global conclusions of revision 2 stand by reference.
- R3-O1 (observation; blueprint, outside this difficulty's artifacts): `db_schema.json` declares `identity_verifications.verified_at` and `human_handoffs.created_at` as "ISO 8601 timestamp YYYY-MM-DDTHH:MM:SS … exactly as returned by ctx.now()". With the required `YYYY-MM-DD HH:MM:SS TZ` frozen_time form, `ctx.now()` returns `2026-09-18 11:20:00 CDT`, so the two halves of that format sentence now disagree: the written value matches "as returned by ctx.now()" and not "YYYY-MM-DDTHH:MM:SS". Gold and rollout write the same string, so no scored state diverges. Recorded, not a red light.
- R3-O2 (observation): the seed timestamps (`booked_at`, `held_at`) remain in `YYYY-MM-DDTHH:MM:SS` form while NOW is now `YYYY-MM-DD HH:MM:SS CDT`. No computation of this difficulty mixes the two at hour resolution (see clock_form), so nothing changes.

### closing_checklist (revision 3)

This was written after the round-3 reveals. Everything above it in revision_3 was written before them.

- There was no round-2 red to close. The round-3 rework is what it claims to be. The only visible change in either task is the top-level `frozen_time`, which now uses the `YYYY-MM-DD HH:MM:SS CDT` form for the same Central-time instant. The stamp occurs once per task file. The charter and the tools are byte-identical to revision 2.
- Clock readers: task tools read `ctx.now()[:10]`, and every policy clock and gate in these two trees reads only the date part of NOW. All of them still give 2026-09-18 (Friday), so every written date, window, month count, day count and the next-business-day `date_available` is unchanged. Shared `verify_customer_identity` / `transfer_to_human_agent` now write the raw stamp in its new form. Gold and rollout write the same value, so no score diverges (R3-O1 records the db_schema format sentence that no longer matches its own "exactly as returned by ctx.now()" clause).
- Regression check: every scored argument, every computation figure, both prerequisite closures and both factor-sensitivity sets equal revision 2.
- Coverage, scopes, trees and factor structure are unchanged (revision-2 checklist stands by reference).
- Gates: the coordinator's round-3 re-run is green with exit 0 for every gate, including TRACEABILITY now that the KB is published, and validate_scenario is VALID (`/tmp/erl0030_gates/bank_deposit_transfers.r3.txt`). The gates were not re-run by the auditor.

**Revision 3: task 0 PASS, task 1 PASS. The difficulty bank_deposit_transfers still passes the source-layer audit. No new defect; observations R3-O1 and R3-O2 recorded.**
