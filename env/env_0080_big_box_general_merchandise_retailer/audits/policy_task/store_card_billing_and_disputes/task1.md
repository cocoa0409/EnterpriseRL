# Policy-task audit — store_card_billing_and_disputes / task 1

## source_derivation_frozen
- freeze time 2026-10-23T20:59Z, auditor: independent policy auditor, revision_1
- inputs: task1.view.json sha256 d1b2d38debb094bb5844f79c6480345360ec2cf2d3f500a4947b13c846ed61a2 (frozen_time, user_scenario, initial_state only); card.extended.yaml 03a90980…ac3e; task_tools.py b95bcb32…e158
- masked and unread until after this section: evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, worklog.md, plan.md
- contamination_disclosure: none.
- scratch: /tmp/erl0080_audit_card/t1.py (independent Decimal arithmetic), probe.py

### policy_self_consistency (this task only)
Charter-global conclusions cited from `_difficulty.md` (same directory): all `charter_global_frozen` subsections and findings R-A1…R-E3.

Per-task checks:
- Handling time. Clock 2026-10-22 14:05 EDT (Thursday). Courtesy evaluated on the opening world; refund after the courtesy reversal.
- No real-world waits. All inputs are seeded rows or the courtesy reversal's own DB effect; the refund "is issued at once"; the holds are amounts withheld today, not waits for an event.
- Demonstration of charter-global defects against this world:
  - R-A2 (U2) bears: base card_evt_payments says the credit balance is refunded on the cardholder's request; the extended rule withholds the 12-month rewards 48.87 permanently ("statement credits … not paid out as cash") and the open-dispute amount 186.40. Reading 1 (extended): 662.58. Reading 2 (base clause in force for the rewards part): 711.45 (credit balance less the payment, dispute and order holds only); a strict base reading refunds the whole 1527.01 within 7 business days. A second defensible scored refund.
  - R-E3c bears: the courtesy share here is 81 % (25.92); under the base courtesy (still restated for every other late fee, and met by this account: no courtesy in 12 months, no other late fee in the previous six statements) the fee is reversed in full, 32.00 — the cleanest first-time late payer receives less than the charter's repeat-fee courtesy. Refund would be 668.66 with 32.00.
  - R-E1 bears: lateness_points (courtesy's only method) and payment_clearing_hold (refund's only method) fail the pairwise test → each computation has 0 surviving method factors.
  - R-E3b, R-E3e: history_points sits on its first tier here and pending_order_hold on its first tier with one pending order; the ladders are struck structurally regardless.
  - R-B1.3/4, R-C3: no merchant-resolved dispute, no same-day second payment, the placed order d535f515 has no card posting — no consequence on this world.
  - Dup policy (state_due) out of scope: World Mastercard has provisional credit and no duplicate dispute. Catch-up/line: not requested.

### problem_chain
Customer raises only the refund of the credit ("I'd like you to send that credit back to me"). The persona does not mention the late fee unless the representative raises it.
1. Refund rule's prerequisite sentence: "fixed only after every late fee that is the only late fee of the last 12 months on an account with no courtesy reversal in that time carries its courtesy reversal." Late fees after 2025-10-22: 96941f26 32.00 (2026-09-10, statement 2026-08-15) only; courtesy reversals in that time: none; no card_reverse_fee referencing it → unmet at the opening. Write that brings it about: the courtesy reversal (card_ext_first_late_fee_courtesy, reverse_late_fee_courtesy_ba087f69, agent). Edge kind value_input (`credit_bal`).
2. Courtesy rule: no prerequisite. Tree ends.
Derived tree: refund ←(value_input) courtesy; n = 1, value_input edges 1 ≥ 1; acyclic; owner=user write = the root refund (ruling (a); the persona asks to confirm it herself). Order: reverse_late_fee_courtesy → refund_credit_balance. Load-bearing: skip the courtesy → refund 636.66 instead of 662.58. Tool bodies (task_tools.py 144–205) check nothing about fees or holds. Persona closes when told the refund amount = last write.

### task_independent_derivation
Authorisation: refund is her own decision, completed by her at hand-over (owner=user); the courtesy reversal is an agent write owed "at the cardholder's next contact, whatever the contact is about". Identity: Felicia Hargrove, 3055550164, DOB 1972-02-08, ZIP 33611 = customer a5ff5961. Act now.

Step 1 — reverse_late_fee_courtesy_ba087f69 (agent), opening world:
- late_fee_event_id 96941f26-… (32.00, statement 2026-08-15, due 2026-09-09); qualifying (only late fee in 12 months, no courtesy reversal)
- tenure: opened 2019-03-04 → 91 whole months → 15
- lateness: most recent payment against 2026-08-15 = 7debcac0 1299.59 credited 2026-09-11 → 2 days late → 15
- membership: Northgate+ Monthly active (d2ffd1bb) → 6
- automatic payments in 12 months: aa20e94d (2026-10-10, autopay) → 1 → 5
- history: late fees in 24 months 1, returned payments in 24 months 0 → 12
- coverage: payments against 2026-08-15 1299.59 ≥ new balance 1299.59 → 8
- share 20 + 61 = 81 % → reversal_amount_usd = 32.00 × 0.81 = **25.92**; card_account_id fd994ef9-3169-4464-8c0c-d7dad1f189fa. Owed after −1527.01.

Step 2 — refund_credit_balance_0212c7e9 (user), after step 1:
- credit balance 1527.01
- payment hold: no returned payment in 12 months; most recent payment aa20e94d 554.18 credited 2026-10-10, 12 days ≤ 15 → 554.18
- dispute hold: dispute b8baa781 (186.40, not_received, open), provisional credit 55fbcd74 186.40 posted → 186.40
- rewards hold: reward credits 2025-11-15 … 2026-09-15 = 48.87 (< credit balance) → 48.87 (2025-10-15 1.49 is outside the window)
- order hold: d535f515 Ship to Home, placed, paid with this card, no posting → 74.98
- refund_amount_usd = 1527.01 − 554.18 − 186.40 − 48.87 − 74.98 = **662.58**; owed after −864.43
- root on the opening world (no courtesy): 636.66

Terminal state: courtesy reversal 25.92 against 96941f26 (courtesy_waiver); confirmed credit_balance_refund request and refund 662.58; current_balance −864.43.

### factor_weight
Courtesy (opening world): fee 32.00; all-baseline 20 % → 6.40 ≠ 25.92.
| factor | label | tier & rows | baseline | value under baseline |
|---|---|---|---|---|
| tenure_points | parameter | T1, opened_date 2019-03-04 | 0 | 21.12 |
| lateness_points | method (fails pairwise, R-E1) | T1, PAY 7debcac0 09-11 vs due 09-09 | 0 | 21.12 |
| membership_points | parameter, cross: membership | T2, membership d2ffd1bb Monthly active | 0 | 24.00 |
| automatic_payment_points | parameter | T2, PAY aa20e94d autopay | 0 | 24.32 |
| history_points | parameter (unreal, R-E3b) | T1, one late fee in 24 m, no returns | 0 | 22.08 |
| coverage_points | parameter | T1, 1299.59 ≥ STM 0df829d0 1299.59 | 0 | 23.36 |
Near-miss: the card holding's autopay_option 'statement_balance' (enrolment, not a count) vs the one autopay payment; the 2026-10-08 online payment is against 2026-09-15, not the fee statement. Surviving: 4 parameter, 0 method.

Refund (after step 1): all-baseline 1527.01 ≠ 662.58.
| factor | label | tier & rows | baseline | value under baseline |
|---|---|---|---|---|
| payment_clearing_hold | method (fails pairwise, R-E1) | T2, PAY aa20e94d 554.18 (12 days) | 0 | 1216.76 |
| open_dispute_hold | parameter | T1, DSP b8baa781 open + DCR 55fbcd74 provisional | 0 | 848.98 |
| rewards_cash_hold | parameter | T2, RWD rows 48.87 | 0 | 711.45 |
| pending_order_hold | parameter, cross: order (unreal, R-E3e) | T1, order d535f515 placed 74.98 | 0 | 737.56 |
Near-miss: payment 0f737170 (2026-10-08, 14 days) inside 15 days but not the most recent; reward bcc… 2025-10-15 1.49 outside 12 months; fulfilled card orders 94e92252, 8565a811 not held. Surviving: 2 (open_dispute_hold, rewards_cash_hold), 0 method.
Task-level: multi-source ✓ (open_dispute_hold, history/coverage); cross-difficulty ✓ (membership_points; pending_order_hold struck).

### task-specific findings (frozen)
None beyond the charter-global demonstrations above.

## source_gt_comparison
Reveal time 2026-10-23T20:59Z (after all frozen sections were on disk).
| item | frozen derivation | GT | same? |
|---|---|---|---|
| need / authorisation / timing | refund now; agent posts the owed courtesy; customer confirms the refund on hand-over | same (owner ruling (a)) | same |
| read set | customer, identity, card holding, card events, membership, orders | find_customers, verify_customer_identity, find_card_holdings, find_card_events, find_membership_holdings, find_order_holdings | same |
| now/wait/refuse | act now | act now | same |
| step 1 tool/owner | reverse_late_fee_courtesy_ba087f69 / agent | same | same |
| late_fee_event_id | 96941f26-… | 96941f26-982f-458a-b14a-d26472098545 | same |
| reversal_amount_usd | 25.92 | 25.92 | same |
| step 2 tool/owner | refund_credit_balance_0212c7e9 / user | same | same |
| refund_amount_usd | 662.58 | 662.58 | same |
| order | courtesy → refund | steps 7 → 9 | same |
| terminal | courtesy 25.92, confirmed request + refund 662.58 | same | same |
Closest alternative candidates excluded: (a) holding both October payments (1108.36) — excluded by the payment-hold second tier ("that most recent payment is held"; the two are on different days); (b) full courtesy 32.00 — excluded by the declared overwrite for a qualifying fee (but see R-E3c); (c) rewards included in the refund (711.45) — excluded by the extended rewards hold, but defended by the in-force base clause (R-A2).

Problem tree vs `prerequisite_closure`: root card_ext_credit_balance_refund = same; edge kind value_input = same, gate credit_bal = same, form state = same, resolved_by reverse_late_fee_courtesy_ba087f69 = same; opening: credit 1501.09 = 1501.09; flip 636.66 → 662.58 = same; resolution_order courtesy → refund = same.

factor_weight vs `computations`:
- courtesy: baseline 6.40 = 6.4; tenure 21.12 = 21.12; lateness 21.12 = 21.12; membership 24.00 = 24.0; automatic payment 24.32 = 24.32; history 22.08 = 22.08; coverage 23.36 = 23.36; tiers equal.
- refund: baseline 1527.01 = 1527.01; payment hold 1216.76 = 1216.76; dispute hold 848.98 = 848.98; rewards 711.45 = 711.45; order 737.56 = 737.56; tiers equal.
Proof-text check: design_rationale §5 "the base 'credit balance above credit_balance_refund_min_usd is refunded ... of the cardholder's written request' stays in force (the refund is issued at once, inside the 7 business days)" — false as an assertion of compatibility: the rewards hold is never released ("not paid out as cash") and the dispute hold outlasts 7 business days; this is R-A2.

Verdicts: SOURCE-POLICY RED (R-A2 demonstrated here; other charter-global REDs cited, no consequence on this world); SOURCE-CHAIN PASS; SOURCE-FACTOR RED (R-E1 lateness_points and payment_clearing_hold — 0 surviving method factors in both computations; R-E3b history_points; R-E3c courtesy baseline; R-E3e pending_order_hold — refund keeps 2 surviving factors); SOURCE-TASK RED via R-A2's second defensible refund (711.45) and R-E3c's (full courtesy 32.00 → refund 668.66).

## findings
1. SOURCE-POLICY RED — R-A2. Symptom: refund 662.58 (extended) vs 711.45 (rewards part refunded under the in-force base clause; whole credit 1527.01 under a strict base reading). Root cause: undeclared override of base card_evt_payments credit-balance refund. Evidence: base sentence and refund rule quoted in `_difficulty.md`; reward rows 2025-11-15…2026-09-15 = 48.87. Location: card_ext_credit_balance_refund (rule, overwrite []); gold step 10. New.
2. SOURCE-FACTOR RED — R-E3c. Symptom: the cleanest first-time late fee is reversed at 81 % (25.92) while the same rule keeps a full courtesy for other late fees. Evidence: baseline.rule "The courtesy reversal is 20 percent of the courtesy late fee"; replaced_by "any other late fee may still be reversed as a courtesy in full when …". Consequence: 25.92 vs 32.00 (refund 662.58 vs 668.66). Location: card_ext_first_late_fee_courtesy. New.
3. SOURCE-FACTOR RED — R-E1 (lateness_points T1/T3; payment_clearing_hold T1/T2), R-E3b (history_points non-monotone), R-E3e (pending_order_hold holds one order). All factors move their scored value on this world, but after the structural strikes courtesy has 4 parameter / 0 method and refund 2 / 0 method. Location: factors of both policies. New.
4. Observations: none task-specific beyond the charter-global list.

## revision_2

### source_derivation_frozen (revision_2)
- freeze time 2026-10-24T13:34Z; inputs task1.view.json 5ecdd8cf55027183f96178743282b2bde6125fb7c1cf06dd2c855a982c269889 (rebuilt: frozen 2026-10-30 14:05 EDT, no order rows), card.extended.yaml aafb1362…6c34. Masked until after this section: all GT fields of tasks/1.json. contamination_disclosure: none for round 2 (the world and both policies changed; every figure re-derived).

#### policy_self_consistency (revision_2, this task)
Clock Friday 2026-10-30; all inputs seeded. Charter-global defects against this world:
- R-E1r bears: fee_basis_correction T1 gives 32.00 − 3.93 (b6d7f501 regulatory_cap) = 28.07, equal to T2's value, the 2026-08-14 minimum 28.07 — the only method factor of the courtesy does not distinguish its tiers here.
- N5 bears: channel (7) and risk (7) days are both needed to hold the 408.04 payment aged 11 days; each one's baseline substitution removes the whole hold.
- N3, N4, N6, R-C1r, R-D2r, R-D3r: not triggered here (fee partly reversed for the cap only; open dispute on the first hold tier; no duplicate dispute; no line/catch-up).

#### problem_chain (revision_2)
Root: refund (customer: "I'd like you to send that credit back to me"). Wait: late fee b60b1fb0 32.00 (2026-09-09, statement 2026-08-14) is the only late fee after 2025-10-30; no courtesy_waiver reversal in that time (b6d7f501 is regulatory_cap) → unmet. Resolver: courtesy (agent). Tree refund ←(value_input) courtesy; n = 1; owner=user refund. Load-bearing: skip courtesy → 263.56 vs 285.45. Persona raises only the refund; the channel facts it gives on request ("normally … by phone, the October payment was the first time you paid online, … set the account to pay the minimum automatically") agree with the records (phone payments through 2026-09-10, autopay 2026-10-09, single online payment c022dbba 2026-10-19).

#### task_independent_derivation (revision_2)
- reverse_late_fee_courtesy_ba087f69 (agent): fee b60b1fb0-…; basis T1 28.07; points tenure 15 (91 months) + lateness 15 (a61d812e 09-10, 2 days after 09-08) + membership 6 (Monthly) + autopay 5 (23b77d74) + history 12 (one late fee, no returns in 24 months); share 25 + 53 = 78 % → **21.89**.
- refund_credit_balance_0212c7e9 (user), after the courtesy: credit 860.00 + 21.89 = 881.89; payment hold 408.04 (c022dbba online, 11 days ≤ 7 + 7 — only online payment in 12 months, no returns); dispute hold 186.40 (b8baa781 open, provisional 55fbcd74); residual interest hold max(2.00, 408.04 × 27.49 % / 365 × 4 = 1.23) = 2.00 (2026-10-14 charged 11.49, paid in full 10-19) → **285.45**; without the courtesy 263.56.

#### factor_weight (revision_2)
- courtesy (all-baseline 8.00): tenure 17.68; lateness 17.68; membership 20.21 (cross: membership d2ffd1bb); autopay 20.49; history 18.53; fee_basis_correction 24.96. All bear weight; fee_basis_correction struck structurally (R-E1r).
- refund (all-baseline 881.89): channel_clearing_days 693.49; risk_clearing_days 693.49 (N5); open_dispute_hold 471.85; residual_interest_hold 287.45 (the 2.00 floor binds). Near-misses: the 10-09 autopay payment (not the most recent); the 3.93 cap reversal (not a courtesy reversal, so the fee still qualifies); the 2025-10-14 reward outside 12 months is no longer read.

#### task-specific findings (revision_2, frozen)
None beyond the charter-global demonstrations above.

### source_gt_comparison (revision_2)
Reveal 2026-10-24T13:25Z of tasks/1.json sha256 4cac645c…fc49.
| item | frozen | GT | same? |
|---|---|---|---|
| reads | customers, identity, card holding, card events, membership | same five | same |
| courtesy args | fd994ef9-…, b60b1fb0-…, 21.89 | same | same |
| refund (user) | 285.45 | 285.45 | same |
| order / owners | courtesy (agent) → refund (user) | steps 6 → 8 | same |
Closure: value_input / credit_bal / state / reverse_late_fee_courtesy = same; opening credit 860.00 = same; flip 881.89 and 263.56 → 285.45 = same; order = same.
factor_sensitivity: courtesy 17.68 / 17.68 / 20.21 / 20.49 / 18.53 / 24.96, baseline 8.0 = same; refund 693.49 / 693.49 / 471.85 / 287.45, baseline 881.89 = same.
Closest alternatives excluded: holding the 10-09 autopay payment too (not the most recent); fee basis 32.00 (a reversal is posted against the fee, first tier); a 3-day clearing period (online + first online payment in 12 months → 7 + 7).

Verdicts (revision_2): SOURCE-POLICY PASS on this world (R-A2 closed; N3/N4/N6 not triggered here); SOURCE-CHAIN PASS; SOURCE-FACTOR RED (R-E1r: fee_basis_correction's T1 equals T2's value on this very world, 28.07 = 28.07, so the courtesy has no method factor that survives the pairwise test; N5: the two clearing-day factors are one clearing period split in two, each removing the whole 408.04 hold); SOURCE-TASK PASS.

### findings (revision_2)
1. R-A2, R-E3b, R-E3c, R-E3e, R-B1.4 (refund) — closed.
2. SOURCE-FACTOR RED — R-E1r (residual): courtesy method tiers T1/T2 coincide on the reachable domain; demonstrated here (28.07 both). Location: card_ext_first_late_fee_courtesy factor fee_basis_correction.
3. SOURCE-FACTOR RED — N5 (new): refund channel_clearing_days + risk_clearing_days split one clearing period. Location: card_ext_credit_balance_refund rule ("every clearing period this rule sets, added together"), compute `payment_hold`.
4. Charter-global, no value consequence here: N3 (zero-amount courtesy vs refund wait), N6 (dispute-hold second tier).

## revision_3

### source_derivation_frozen (revision_3)
- freeze: written before the 2026-10-24T13:56:33Z reveal; view 5ecdd8cf…9889 (unchanged), charter 24dbff27…54d4. contamination_disclosure: world unchanged since revision_2 (round-2 gold known); both policies changed and every figure below is re-derived under the new charter.
- Tree as revision_2 (refund ←value_input courtesy). Wait: late fee b60b1fb0 is the only late fee of 12 months, standing 32.00 − 3.93 = 28.07 ≥ 1.00, no courtesy reversal → unmet. Skip courtesy → 259.77.
- Courtesy: standing 28.07; share 25 + tenure 15 + lateness 15 + loyalty 2 (Northgate+ Monthly enrolled 2024-01-12 → 2 whole years) + autopay 5 + history 12 + coverage 8 (28.07 paid of 28.07) = 82 % → **23.02**.
- Refund: credit 860.00 + 23.02 = 883.02; payment hold 408.04 (online, the only online payment in 12 months → 14 days, age 11); dispute hold 186.40; residual interest 2.00; dispute interest exposure 186.40 × 27.49 % / 365 × 27 days (10-03 → 10-30) = 3.79 → **282.79**.
- factor_weight: courtesy 18.81 / 18.81 / 22.46 (loyalty, cross membership d2ffd1bb) / 21.61 / 19.65 / 20.77, all-baseline 7.02; refund clearing_period 690.83, open_dispute_hold 469.19, dispute_interest_exposure 286.58, residual_interest_hold 284.79, all-baseline 883.02. All bear weight; dispute_interest_exposure struck structurally (R3-4) → refund 3 surviving factors (< 4).
- Charter-global findings against this world: R3-4 bears (structure; the scored exposure here comes from the billing-error tier with a single open dispute). R3-1/2/3/5 not triggered.

### source_gt_comparison (revision_3)
Reveal 2026-10-24T13:56:33Z of tasks/1.json sha256 d0b0b932…3796. Writes: courtesy b60b1fb0 / 23.02 (agent), refund 282.79 (user) — same. Closure: value_input / credit_bal / state / reverse_late_fee_courtesy (same); 860.00 → 883.02 and 259.77 → 282.79 (same); order same. factor_sensitivity: courtesy 18.81 / 18.81 / 22.46 / 21.61 / 19.65 / 20.77, baseline 7.02; refund 690.83 / 469.19 / 286.58 / 284.79, baseline 883.02 — all same.

Verdicts (revision_3): SOURCE-POLICY PASS on this world; SOURCE-CHAIN PASS; SOURCE-FACTOR RED (R3-4: dispute_interest_exposure's network-only tier and its latest-dispute-only selection are treatments no issuer publishes; struck, the refund computation keeps 3 factors, below the floor of 4); SOURCE-TASK PASS.

### findings (revision_3)
1. R-E1r, N3, N5, N6 — closed.
2. SOURCE-FACTOR RED — R3-4 (new, introduced by the N5 rework): see `_difficulty.md` § revision_3. Location: card_ext_credit_balance_refund factor dispute_interest_exposure (rule sentence "The dispute interest exposure follows the most recent dispute on the account …").

## revision_4

### source_derivation_frozen (revision_4)
- written before the round-4 reveal; view a1790926…3407 (changed: Publix credit a9933333 16.47 on 2026-10-27 against purchase 2KXNGHWK3UWE of 2026-09-20; current_balance −876.47); charter f4bdc22b…5040. The round-3 gold of the previous world is known to me; the courtesy is unchanged and the refund is re-derived on the new world.
- Tree as before (refund ←value_input courtesy); wait unmet (fee b60b1fb0 standing 28.07, no courtesy reversal); skip courtesy → 263.56.
- Courtesy **23.02** (28.07 × 82 %: 25 + 15 + 15 + 2 + 5 + 12 + 8).
- Refund: credit 876.47 + 23.02 = 899.49; payment hold 408.04 (online first use → 14 days, age 11); dispute hold 186.40; residual interest 2.00; merchant credit hold 16.47 (most recent credit a9933333, outside merchant, matched to a purchase → 7 days, age 3) → **286.58**.
- factor_weight: courtesy 18.81 / 18.81 / 22.46 / 21.61 / 19.65 / 20.77 (7.02); refund clearing_period 694.62, open_dispute_hold 472.98, merchant_credit_hold 303.05, residual_interest_hold 288.58 (all-baseline 899.49). All bear weight; merchant_credit_hold struck structurally (R4-2a) → refund 3 surviving factors.
- Charter-global findings against this world: R4-2 bears structurally only (the 860.00 credit is 9 days old, outside any 7-day window, and the 10-09 autopay payment is 21 days old), so no value moves here. Persona: the Publix return is disclosed "only if asked" and agrees with the record.

### source_gt_comparison (revision_4)
Frozen section written 2026-10-24T18:41:21Z; reveal 18:41:29Z of tasks/1.json sha256 5fee7353…c562. Writes b60b1fb0 / 23.02 (agent), 286.58 (user) — same. Closure value_input / credit_bal / state / courtesy tool; 876.47 → 899.49 and 263.56 → 286.58 — same. factor_sensitivity: courtesy 18.81 / 18.81 / 22.46 / 21.61 / 19.65 / 20.77 (7.02); refund 694.62 / 472.98 / 303.05 / 288.58 (899.49) — same.
Verdicts (revision_4): SOURCE-POLICY PASS on this world; SOURCE-CHAIN PASS; SOURCE-TASK PASS; SOURCE-FACTOR RED — R4-2a: merchant_credit_hold holds only the most recent merchant credit, a treatment no issuer publishes (probe5: a 4-day-old 860.00 outside credit released while a 3-day-old 16.47 is held); struck, the refund computation keeps 3 factors, below 4. → task1 RED.

### findings (revision_4)
1. R3-4 — closed (exposure factor removed).
2. SOURCE-FACTOR RED — R4-2a (new, introduced by the R3-4 rework); and the payment-hold member R4-2b (present since revision_2, missed by me in revisions 2–3) — see `_difficulty.md` § revision_4. Location: card_ext_credit_balance_refund rule sentences "The most recent merchant credit is …", "The merchant credit hold follows where the most recent merchant credit came from …", "The most recent payment is held when its age is no more than the clearing period …".

## revision_5

### source_derivation_frozen (revision_5)
- written 2026-10-24T23:07Z before the round-5 reveal; view 472d6512…606a (changed: Bayshore Grill credit 16.47 on 2026-10-27, unreferenced, own reference 2BG7Q4MRW9KD); charter 1af18631…e7ac. Courtesy unchanged; refund re-derived.
- Courtesy **23.02** (as revision_4).
- Refund: credit 876.47 + 23.02 = 899.49; payment clearing (no returned payment in 12 months): the 408.04 online payment (online's only use in 12 months, in the last month) and the 40.00 automatic payment of 10-09 (autopay's only use, in the last month) → 448.04; phone payments not held (phone used before the month); dispute hold 186.40; residual interest 2.00; merchant credit hold: unreferenced outside credit of the month 16.47 (the 860.00 credit references purchase 2FFS8GMDRUDN) → **246.58**; without the courtesy 223.56.
- factor_weight (all-baseline 899.49): payment_clearing 694.62; open_dispute_hold 432.98; merchant_credit_hold 263.05; residual_interest_hold 248.58; courtesy as revision_4 (7.02 baseline). All bear weight; none struck.
- Persona: the Bayshore Grill refund is mentioned only if asked and agrees with the record. R5-2 bears structurally (both refund factors here own the returned-payment test; it is false on this world, so both sit on their second tiers); no value consequence.

### source_gt_comparison (revision_5)
Reveal 2026-10-24T23:07:25Z of tasks/1.json (sha256 89e9c9a1…). Writes b60b1fb0 / 23.02 (agent), 246.58 (user) — same; closure value_input / credit_bal / state / courtesy tool, 876.47 → 899.49, 223.56 → 246.58 — same; sensitivities: courtesy 18.81 / 18.81 / 22.46 / 21.61 / 19.65 / 20.77 (7.02), refund 694.62 / 432.98 / 263.05 / 248.58 (899.49) — same.
Verdicts (revision_5): SOURCE-POLICY PASS on this world (R5-2 is structural, no value consequence); SOURCE-CHAIN PASS; SOURCE-FACTOR PASS (10 factors over the two computations, all bear weight, none struck; ≥ 1 method and 2 parameters in each; multi-source open_dispute_hold; cross-difficulty loyalty_points); SOURCE-TASK PASS → task1 PASS.

### findings (revision_5)
R4-2 (a)/(b) — closed. No task-level defect; the charter-global R5-2 concerns two of this task's refund factors structurally only.

## revision_6

### source_derivation_frozen (revision_6)
- written 2026-10-24T23:31Z before the round-6 reveal; view unchanged (472d6512…606a; earlier gold known); charter 020883d2…f212. Courtesy **23.02**; refund **246.58** (payment record clean → payment hold 408.04 + 40.00; dispute 186.40; residual 2.00; unreferenced outside credit 16.47); sensitivities 694.62 / 432.98 / 263.05 / 248.58, all-baseline 899.49 — unchanged. R6-2 bears on the label of one refund factor only; counted as a parameter the refund keeps 4 factors with 1 honest method.

### source_gt_comparison (revision_6)
Reveal 2026-10-24T23:31:34Z of tasks/1.json (sha256 f3ddbdcb…). Writes b60b1fb0 / 23.02 (agent), 246.58 (user); closure (value_input credit_bal, state, courtesy tool; 223.56 → 246.58); sensitivities 18.81 / 18.81 / 22.46 / 21.61 / 19.65 / 20.77 (7.02) and 694.62 / 432.98 / 263.05 / 248.58 (899.49) — all same. Verdicts: SOURCE-POLICY PASS, SOURCE-CHAIN PASS, SOURCE-TASK PASS; SOURCE-FACTOR PASS on counts and weight (R6-2 is a charter-global label defect; counted honestly as a parameter, merchant_credit_hold still bears weight, 263.05 vs 246.58, and the refund keeps 3 parameters + 1 method) → task1 PASS.

## revision_7

### source_derivation_frozen (revision_7)
- written 2026-10-24T23:46Z before the round-7 reveal; view unchanged (earlier gold known); charter 32f4e896…3be4. Courtesy **23.02**; refund **246.58**; sensitivities 694.62 / 432.98 / 263.05 / 248.58, all-baseline 899.49; merchant_credit_hold now honestly `parameter` (refund 3 parameters + 1 method).

### source_gt_comparison (revision_7)
Reveal 2026-10-24T23:46:43Z of tasks/1.json (sha256 c8bc73b1…). Writes b60b1fb0 / 23.02 (agent), 246.58 (user); closure and skip effect (223.56); sensitivities and baselines — all same. Verdicts: all four PASS → task1 PASS.

## revision_8

### source_derivation_frozen (revision_8)
- written 2026-10-24T23:57Z before the round-8 reveal; view unchanged (earlier gold known); charter b7c2a711…cc22 (refund and courtesy untouched this round). Courtesy **23.02**; refund **246.58**; sensitivities and baselines as revision_7.

### source_gt_comparison (revision_8)
Reveal 2026-10-24T23:57:40Z of tasks/1.json (sha256 d8a17b1b…). Writes b60b1fb0 / 23.02 (agent), 246.58 (user); closure and order; sensitivities and baselines — all same. Verdicts: all four PASS → task1 PASS.

## revision_9

### source_derivation_frozen (revision_9)
- written 2026-10-25T00:17Z before the round-9 reveal; view unchanged (earlier gold known); charter 1dc5ae2b…fe0d. Courtesy **23.02**; refund **246.58** (payment record clean, so the newly worded not-clean floor is not reached); sensitivities and baselines as revision_8.

### source_gt_comparison (revision_9)
Reveal 2026-10-25T00:17:54Z of tasks/1.json (sha256 7b49f428…). Writes b60b1fb0 / 23.02 (agent), 246.58 (user); closure and order; sensitivities and baselines — all same. Verdicts: all four PASS → task1 PASS.
