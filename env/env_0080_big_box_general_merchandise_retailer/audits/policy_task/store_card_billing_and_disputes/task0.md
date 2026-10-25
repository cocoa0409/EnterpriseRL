# Policy-task audit — store_card_billing_and_disputes / task 0

## source_derivation_frozen
- freeze time 2026-10-23T20:58Z, auditor: independent policy auditor, revision_1
- inputs: task0.view.json sha256 ce76fbe58c40f4534fbf6e7b7be1b45f4e5fbdc9ad39fad48bf7d70e9623aa74 (frozen_time, user_scenario, initial_state only); card.extended.yaml 03a90980…ac3e; task_tools.py b95bcb32…e158
- masked and unread until after this section: evaluation_criteria, computations, charter_scope, required_documents, design_rationale, solvability_contract, prerequisite_closure, worklog.md, plan.md
- contamination_disclosure: none. No search touched tasks/*.json; the two views were the only task sources read.
- scratch: /tmp/erl0080_audit_card/t0.py, t0b.py (independent Decimal arithmetic), probe.py (gate DSL on scratch copies)

### policy_self_consistency (this task only)
Charter-global conclusions cited from `_difficulty.md` (same directory): `policy_conflict_scan`, `rule_compute_equivalence`, `action_binding_and_uuids`, `prerequisite_graph`, `prerequisite_sentences`, `override_declarations`, `factor_ladders`, findings R-A1…R-E3.

Per-task checks:
- Handling time. Clock 2026-10-14 10:30 EDT (Wednesday, before the 17:00 ET cutoff → a phone payment is credited today). Each write evaluated after its own prerequisites and before itself: dup on the opening world; catch-up after the dup settlement; line after the catch-up payment.
- No real-world waits. Every input is a seeded record (card_events, card_holdings, order_holdings 269b5650, membership ae727ffd) or the DB effect of an earlier write of this task. The dup rule confirms "at once" from records; the payment is completed by the cardholder on the call; no approval, clearing or date has to pass.
- Demonstration of charter-global defects against this world:
  - R-A1 (U1) bears: the 07-05 late fee 32.00 (row 99a3a603, statement 2026-06-09) was charged although the payments recorded against that statement (113.00) reach the dispute-adjusted minimum 102.01 — "a fee charged in error" under the base clause. Reading 1 (extended): final credit 1421.69 incl. 32.00. Reading 2 (base sentence in force): final credit 1389.69 and the fee reversed as billing_error (no tool carries that reason) → catch-up over-limit restoration 265.14, catch-up payment 551.03 instead of 519.03 (t0b.py run "base fee-reversal reading"). Two defensible scored values for the dup credit and the catch-up payment.
  - R-A3 (U3): base days past due here is also 10 (the 2026-06-09 statement is met once the disputed amount is excluded, consistent with the account being active rather than suspended at 60 days); no consequence on this world.
  - R-B1, R-B2, R-C1–R-C3, R-D1–R-D3: none of their decoy/edge records is present (one duplicate dispute, Northgate-order source, notice 2026-06-17 before the latest close 2026-10-09; no cash advances; no credits against the disputed posting; autopay none; the returned-payment shortfall tier, not the disputed-statement tier, applies) — no consequence on this world.

### problem_chain
Customer raises only: "My Northgate card got declined … I'd like my credit limit raised" (root = card_ext_line_increase, on_request). The persona mentions no prerequisite; the TV double charge and the bounced payment are disclosed only if the representative brings them up.

Walk from the root:
1. Line rule's prerequisite sentence: "granted only after the statement for which the most recent late fee was recorded has payments recorded against it, net of the payments returned unpaid, that reach its minimum payment due." Most recent late fee: facfff5e 43.00 on 2026-10-08, statement_date 2026-09-09; that statement (e1252da9) minimum 143.01, due 2026-10-04. Payments carrying 2026-09-09: a9b41d68 143.01 (2026-10-02); returned: f347e200 143.01 (2026-10-07, insufficient_funds). Net 0.00 < 143.01 → unmet at the opening. The write that records a payment against a statement: the catch-up payment (card_ext_catch_up_payment, make_card_payment_5ec32b69, owner=user). Edge kind: value_input (the gate `cure_unmet` and the post-payment balance feed `line_use`).
2. Catch-up rule's prerequisite sentence: "not fixed until every duplicate-posting dispute that the Northgate order record confirms has its final credit posted on the account." Dispute fbef94b5 (duplicate, billing_error, 1412.84, notice 2026-06-17, source order 269b5650). Postings carrying 269b5650: 325c6bf0 1329.05 (05-30) + 820740ff 1412.84 (05-31) = 2741.89 > order amount paid 1412.84 → confirmed; no card_dispute_credit final row → unmet. Resolver: the dup settlement (card_ext_duplicate_final_credit, in scope: duplicate reason, Northgate Store Card provisional_credit_on_open false, Northgate order source). Edge kind: value_input (`owed_net`).
3. Dup rule: no prerequisite sentence. Tree ends.
Derived tree: line ←(value_input) catch-up ←(value_input) dup; n = 2 prerequisite problems, 2 value_input edges ≥ max(1,1); acyclic; one owner=user write (the payment, ruling (b): "Northgate keeps no payment method on file", persona "your checking account isn't saved on the card account" and autopay_option none).
Topological order: settle_duplicate_dispute → make_card_payment → raise_credit_limit.
Load-bearing runs: skip the settlement → catch-up 527.88 instead of 519.03 (owed net of disputes 4241.99 vs 4233.14); skip the payment → line gate unmet (143.01) → limit stays 4000.00 instead of 5100.00. No parallel edges. Tool bodies (task_tools.py 29–141) check nothing about disputes, payments or late fees. Persona closes at the new limit, which is the last write.

### task_independent_derivation
Authorisation: customer asks for the limit increase (agent write); is "happy for the representative … to take care of whatever the card rules say has to be handled on their side" (covers the agent-side dispute settlement); agrees to pay today only if told a payment is required, completes it herself with the amount and statement date given (owner=user). Act now, no refusal, no wait. Identity: name/phone + DOB (1969-07-23) / ZIP 31406 match customers e14e1738.

Step 1 — settle_duplicate_dispute_b93aba52 (agent), handling time = opening world:
- card_account_id 32e88020-b07e-4ab3-a8ee-3fc8f95d8131; dispute_event_id fbef94b5-… (the card_open_dispute row)
- released_amount_usd = 1412.84 ("its whole disputed amount leaves dispute status")
- duplicate excess = 2741.89 − 1412.84 = 1329.05; no credit against posting 2TB2AHY8CV4F; 0 < 1329.05 < 1412.84 → settled principal 1329.05
- first statement 2026-06-09: purchase interest 62.35 > 0, payments 113.00 < new balance 5379.43 → carried days = 2026-05-31 → 2026-06-17 = 17 → finance charge 1329.05 × 29.99/100/365 × 17 = 18.56
- correct part 1412.84 − 1329.05 = 83.79; latest close 2026-10-09 < today, 3 whole months after notice ≥ 2 (also 119 days > 90) → past limit; 83.79 ≥ 50 → allowance 50.00
- dispute-adjusted minimum max(40, 116.14 − 14.13) = 102.01; late fee 32.00 recorded for 2026-06-09; notice 06-17 ≤ due 07-04; paid 113.00 ≥ 102.01 → carried fee 32.00
- latest statement purchase interest 99.88 > 0 → reinstated 83.79 × 29.99/100/365 × 115 (06-17…10-09 both counted) = 7.92
- final_credit_usd = 1329.05 + 18.56 + 50.00 + 32.00 − 7.92 = **1421.69** (gate DSL on the view gives 1421.69). Account after: owed 4233.14, disputed 0.00.

Step 2 — make_card_payment_5ec32b69 (user), handling time = after step 1:
- missed statement 2026-09-09; days past due 2026-10-04 → 10-14 = 10
- shortfall (returned tier) 143.01 − (143.01 − 143.01) = 143.01
- owed net of disputes 4233.14 > limit 4000.00 → over-limit restoration 233.14
- restoration fee (1–29 days, late fee 43.00 recorded for the missed statement) = 43.00
- cycle-since-miss (1–29 days, latest close 2026-10-09 after due 2026-10-04) = purchase interest 99.88
- amount_usd = **519.03**, statement_closing_date **2026-09-09**, card_account_id 32e88020-…; owed after 3714.11
- opening-world contrast (no settlement): 527.88

Step 3 — raise_credit_limit_a1e4ca90 (agent), handling time = after step 2:
- gate: net payments against 2026-09-09 = 143.01 + 519.03 − 143.01 = 519.03 ≥ 143.01 → granted; account open since 2024-11-18 (≥ 6 months), active
- conduct: late fees in 12 months 2 (2026-07-05, 2026-10-08), returned payments 1 → 5 %
- use 3714.11 / 4000 = 0.9285 ≥ 0.70 → amount = highest statement new balance 5654.83 (2026-10-09)
- membership Northgate+ Annual active → +500; tenure 22 whole months → +200; net purchases 12 m = 6865.56 − 0 − 1421.69 = 5443.87 → +150
- raw 4000 + 282.7415 + 500 + 200 + 150 = 5132.74 → floor to 5100 → ≤ 10,000 → new_credit_limit_usd **5100.00**
- root on the opening world: gate unmet → 4000.00 (unchanged); on the world without the settlement but with a payment: 5200.00

Terminal state: dispute fbef94b5 resolved_for_cardholder, final credit 1421.69, disputed_balance 0.00; payment 519.03 recorded against 2026-09-09; credit limit 5100.00; current_balance 3714.11.

### factor_weight
Dup (task0 world, opening):
| factor | label/kind ok | tier taken & rows | baseline input (from baseline.rule) | scored value under that baseline |
|---|---|---|---|---|
| settled_principal | method ✓ | T2: no credit on 2TB2AHY8CV4F; excess 1329.05 from postings 325c6bf0+820740ff vs order 269b5650 amount_paid 1412.84 (order difficulty's record) | disputed amount 1412.84 | 1505.48 |
| carried_error_days | parameter | T1: INT 3f38dc89 62.35, PAY e7c37e02 113.00 < STM 25d2765c 5379.43 | 0 | 1403.13 |
| noncompliance_allowance | parameter | T1: latest close 2026-10-09, 119 days, correct part 83.79 | 0 | 1371.69 |
| error_late_fee | parameter | T1: FEE 99a3a603 32.00, due 07-04, paid 113.00 ≥ 102.01 | 0 | 1389.69 |
| correct_part_reinstatement | parameter | T1: INT 41505ab0 99.88 | 0 | 1429.61 |
Whole baseline: 1412.84 ≠ 1421.69. Near-miss: posting 325c6bf0 (1329.05) carries the order reference but is not the disputed posting and has no credit against it; the 2026-10-08 late fee is not the fee for the first statement. Stamps: none names a tier. 5 factors pass.

Catch-up (after step 1):
| factor | tier & rows | baseline | value under baseline |
|---|---|---|---|
| shortfall_measure (method) | T1 returned: RET f347e200 143.01 against 2026-09-09 | 143.01 − 143.01 = 0.00 | 376.02 |
| over_limit_restoration | T1: owed 4233.14 net of disputes vs limit 4000 | 0 | 285.89 |
| restoration_fee | T2: 10 days, FEE facfff5e 43.00 | 0 | 476.03 |
| cycle_since_miss (method) | T2: latest STM 2026-10-09 after due 10-04, INT 41505ab0 99.88 | 0 | 419.15 |
Whole baseline: 0.00 (a definite number; the tool would refuse a zero payment) ≠ 519.03. Near-miss: late fee 99a3a603 (2026-07-05) is outside the two-month window and is not on the missed statement. All four bear weight; restoration_fee is struck structurally (R-E3d) → 3 surviving factors (< 4).

Line (after step 2):
| factor | tier & rows | baseline | value under baseline |
|---|---|---|---|
| conduct_percentage | T2: FEE 99a3a603, facfff5e; RET f347e200 → 5 % | 10 % | 5400.00 |
| line_use_sizing (method) | T1: 3714.11/4000 ≥ 0.70 → STM c4ca2f6b 5654.83 | current limit 4000 | 5000.00 |
| membership_line_addition (cross: membership) | T1: membership ae727ffd Northgate+ Annual active | 0 | 4600.00 |
| tenure_line_addition | T2: opened 2024-11-18 → 22 months | 0 | 4900.00 |
| purchase_volume_addition | T2: purchases 6865.56 less dispute credit 1421.69 = 5443.87 | 0 | 4900.00 |
Whole baseline: 4000 + 10 % × 4000 = 4400.00 ≠ 5100.00. Near-miss: the dispute credit posted today pulls net purchases below 6,000 (6865.56 gross → careless tier 300); purchase 3a8cb612 (2025-08-30) is outside the 12-month window. All bear weight on this world; structurally conduct_percentage (R-E3a) and line_use_sizing (R-E1) are struck and the pair is a multiplicative split (R-E2) → 3 surviving factors, 0 method.
Task-level: multi-source ✓ (carried_error_days, settled_principal T2); cross-difficulty ✓ (membership_line_addition reads membership ae727ffd; settled_principal reads order 269b5650, labelled null — O-3).

### task-specific finding (frozen)
**T0-1 SOURCE-TASK RED — seeded purchases the charter declines.** Base card_product_and_limit: "transactions above the limit are declined." Running balance (t0.py): after 820740ff (2026-05-31) 5262.90 on a 4000.00 limit; purchases 01f1c249 54.18 (06-05, balance 5317.08, before any dispute), bb62fd15 71.90 (06-24, 5451.33; 4038.49 even net of the 1412.84 under dispute), 4d188ac0 39.60 (07-25, 4103.23 net), 32aeedc4 63.47 (08-22, 4090.62 net), f69119d9 48.95 (09-26, 4099.11 net) were all posted as approved. Consequence: these 278.10 of purchases (plus the interest they carried) are what put the account over its limit; without them the owed amount net of disputes after the settlement is at most 4233.14 − 278.10 = 3955.04, room ≥ 44.96 ≥ the 40.00 floor → over-limit restoration third tier 0.00 instead of 233.14, catch-up payment ≤ 285.89 instead of 519.03. The over-limit tier the scored payment takes rests on rows the charter cannot produce. Location: initial_state.card_events rows above.

## source_gt_comparison
Reveal time 2026-10-23T20:59Z (after task0.md, task1.md and _difficulty.md charter-global sections were on disk).
| item | frozen derivation | GT | same? |
|---|---|---|---|
| need / authorisation / timing | limit increase now; agent settles the dispute; customer pays herself on hand-over | same (persona + owner ruling (b)) | same |
| read set | customer, identity, card holding, card events, order holdings, membership | find_customers, verify_customer_identity, find_card_holdings, find_card_events, find_order_holdings, find_membership_holdings | same |
| now/wait/refuse | act now, no wait | act now | same |
| step 1 tool/owner | settle_duplicate_dispute_b93aba52 / agent | same | same |
| card_account_id | 32e88020-b07e-4ab3-a8ee-3fc8f95d8131 | same | same |
| dispute_event_id | fbef94b5-… (the only open duplicate dispute) | fbef94b5-78a1-4e9c-8069-86afdb127aae | same |
| released_amount_usd | 1412.84 | 1412.84 | same |
| final_credit_usd | 1421.69 | 1421.69 | same |
| step 2 tool/owner | make_card_payment_5ec32b69 / user | same | same |
| statement_closing_date | 2026-09-09 | 2026-09-09 | same |
| amount_usd | 519.03 | 519.03 | same |
| step 3 tool/owner | raise_credit_limit_a1e4ca90 / agent | same | same |
| new_credit_limit_usd | 5100.00 | 5100.0 | same |
| order | settle → pay → raise | steps 7 → 9 → 11 | same |
| terminal | dispute resolved, credit 1421.69, payment 519.03 vs 2026-09-09, limit 5100.00 | same | same |
Closest alternative candidates excluded: (a) final credit = disputed amount 1412.84 — excluded by the settled-principal sentence's second tier (excess 1329.05 strictly between 0 and 1412.84, no credit against 2TB2AHY8CV4F); (b) payment recorded against 2026-10-09 — excluded because the line gate measures payments carrying the missed statement's date 2026-09-09 (O-7 notes the catch-up rule never names it); (c) limit 5200.00 (volume tier 300) — excluded because the 1421.69 dispute credit is posted inside the 12-month window before the review.

Problem tree vs `prerequisite_closure`: root card_ext_line_increase = same; edge line→catch-up: kind value_input = value_input, gate cure_unmet = cure_unmet, form state = state, resolved_by make_card_payment_5ec32b69 = same, opening value net 0.00 vs 143.01 = "0.00 against a 143.01 minimum", flip 4000.00 → 5100.00 = same; edge catch-up→dup: value_input/owed_net/state/settle_duplicate_dispute_b93aba52 = same, owed_net 4241.99 → 4233.14 = same, skipped-effect 527.88 = 527.88 and 5200.00 = 5200.00; resolution_order dup → catch-up → line = same.

factor_weight vs `computations[].factor_sensitivity` / `baseline_result` (figure against figure):
- final credit: baseline 1412.84 = 1412.84; settled_principal 1505.48 = 1505.48; carried_error_days 1403.13 = 1403.13; noncompliance_allowance 1371.69 = 1371.69; error_late_fee 1389.69 = 1389.69; correct_part_reinstatement 1429.61 = 1429.61; tiers taken equal.
- catch-up: baseline 0.00 = 0.0; shortfall 376.02 = 376.02; over-limit 285.89 = 285.89; restoration fee 476.03 = 476.03; cycle-since-miss 419.15 = 419.15; tiers equal.
- line: baseline 4400.00 = 4400.0; conduct 5400 = 5400.0; line use 5000 = 5000.0; membership 4600 = 4600.0; tenure 4900 = 4900.0; volume 4900 = 4900.0; tiers equal.
Proof-text check: design_rationale §7 "21 in-store orders paid on the card" — the seed has 20 in-store purchases and one Ship to Home order (269b5650) (observation O-T0-a; no relationship rests on it). §7 asserts every interest row, minimum and late fee follows the base formulas but is silent on the purchases approved while over the limit (T0-1).

Verdicts: SOURCE-POLICY RED (R-A1 demonstrated here; charter-global R-A3, R-B1, R-B2, R-C1–R-C3, R-D1–R-D3 cited, no consequence on this world); SOURCE-CHAIN PASS; SOURCE-FACTOR RED (R-E1 line_use_sizing, R-E2, R-E3a conduct_percentage, R-E3d restoration_fee — surviving factors line 3 / 0 method, catch-up 3); SOURCE-TASK RED (T0-1; and R-A1's second defensible final credit 1389.69 / payment 551.03).

## findings
1. SOURCE-POLICY RED — R-A1 (see `_difficulty.md` findings). Symptom: two defensible values for final_credit_usd (1421.69 vs 1389.69 + a billing_error reversal) and amount_usd (519.03 vs 551.03). Root cause: undeclared override of the base fee-reversal sentence. Evidence: base card_evt_late_and_returned_fees sentence quoted there; row 99a3a603 32.00; payments 113.00 ≥ 102.01. Location: card_ext_duplicate_final_credit (rule, overwrite, compute carried_fee); gold steps 8, 10. New in revision_1.
2. SOURCE-FACTOR RED — R-E1 / R-E2 / R-E3a / R-E3d (see `_difficulty.md`). On this world every declared factor moves its scored value (factor_weight above), but line_use_sizing's T2/T3 pair has no distinguishing input, conduct_percentage is non-monotone, the line increase is pct × base split across two factors, and restoration_fee's late-fee condition holds for every customer reaching the catch-up write. Location: card_ext_line_increase.factors, card_ext_catch_up_payment.factors. New.
3. SOURCE-TASK RED — T0-1 (frozen above). Purchases 01f1c249, bb62fd15, 4d188ac0, 32aeedc4, f69119d9 were approved while the account was over its 4000.00 limit, which base card_product_and_limit declines; the over-limit tier of the scored catch-up payment (233.14 of 519.03) rests on them. Location: initial_state.card_events. New.
4. Observations: O-7 (statement of the catch-up payment inferred, not stated); O-T0-a (rationale count of in-store orders); O-3 (settled_principal cross_difficulty null though it reads order 269b5650).

## revision_2

### source_derivation_frozen (revision_2)
- freeze time 2026-10-24T13:33Z; inputs task0.view.json 726079d9f9a1c9983679f2cde85cf5f2cc7b71316a53fa8d1b84cb687b9378ed (rebuilt), card.extended.yaml aafb1362…6c34, task_tools.py unchanged. Masked until after this section: all GT fields of the rebuilt tasks/0.json. contamination_disclosure: none for round 2 (round-1 GT of the previous world is known from revision_1; the world, limit and every computed figure below changed and were re-derived from the view and the new charter; the rework claims file names no figures).
- charter-global conclusions: cite `_difficulty.md` § revision_2.

#### policy_self_consistency (revision_2, this task)
Handling time and no-wait arguments as in revision_1 (clock 2026-10-14 10:30 EDT, Wednesday; all inputs seeded or own-write effects). Charter-global defects against this world:
- R-D2r bears: after the gold settlement the dup policy re-evaluates `confirmed=True`, 1421.69 on this world (probe2) — a second settlement of the same dispute is what the rule text calls for at that point; terminal state with one vs two final credits.
- R-D3r bears: on this world a 1.00 payment against 2026-09-09 already opens the gate (5300.00 with 134.50 still short); the edge does not test that the catch-up is paid.
- N1 bears: shortfall_measure's baseline gives the whole catch-up 0.00 instead of 183.99.
- R-C1r, N2, N3, N4, N5, N6, R-E1r: no record of this world triggers them (one duplicate dispute with two postings and no return; no dispute on the missed statement; usage on T1; courtesy and refund out of scope).

#### problem_chain (revision_2)
Root: line increase (customer: "I'd like my credit limit raised"). Line wait: latest late fee facfff5e 43.00 posted 2026-10-08 for statement 2026-09-09; latest payment against 2026-09-09 is a9b41d68 credited 2026-10-02 (< 10-08; returned 10-07) → unmet. Resolver: catch-up payment (owner=user). Catch-up wait: most recent duplicate dispute fbef94b5 (Northgate order 269b5650, Store Card, postings 325c6bf0 1329.05 + 820740ff 1412.84 = 2741.89 > 1412.84, two postings) has no final credit → unmet. Resolver: dup settlement (agent). Tree = revision_1's: line ←(value_input) catch-up ←(value_input) dup; n = 2, 2 value_input; owner=user payment; order settle → pay → raise. Load-bearing: skip settlement → catch-up 328.34 (vs 319.49) and line 5300.00 (vs 5200.00); skip payment → line 3900.00. Tools unchanged and judge nothing.

#### task_independent_derivation (revision_2)
- settle_duplicate_dispute_b93aba52 (agent): card 32e88020-…, dispute fbef94b5-…, released 1412.84, final credit = 1329.05 (excess) + 18.56 (17 days; 2026-06-09 interest 62.12, paid 112.00 < 5325.02) + 50.00 (past limit; correct part 83.79) + 32.00 (standing fee 99a3a603, no reversals; paid 112.00 ≥ adjusted minimum 115.37 − 14.13 = 101.24) − 7.92 (83.79 × 29.99 % / 365 × 115) = **1421.69**.
- make_card_payment_5ec32b69 (user), against **2026-09-09**: shortfall 135.50 (returned tier) + over-limit 47.33 (owed 3947.33 > 3900.00) + standing fee 43.00 (10 days) + latest purchase interest 93.66 (statement 2026-10-09 after due 10-04) = **319.49**; opening-world contrast 328.34.
- raise_credit_limit_a1e4ca90 (agent): gate met (payment 10-14 ≥ fee 10-08); 5 % × 3900 = 195.00 (one return, two late fees); use 3627.84 / 3900 = 0.930 → 5 % × 5369.02 = 268.45; +500 (Annual); +200 (22 months); net purchases 6587.46 − 1421.69 = 5165.77 → +150; raw 5213.45 → **5200.00**; opening world 3900.00.
Independent Decimal arithmetic and the gate DSL agree on all three.

#### factor_weight (revision_2)
- dup: settled_principal 1505.48; carried_error_days 1403.13; noncompliance_allowance 1371.69; error_late_fee 1389.69; correct_part_reinstatement 1429.61; all-baseline 1412.84.
- catch-up: shortfall_measure 0.00 (N1); over_limit_restoration 272.16; restoration_fee 276.49; cycle_since_miss 225.83; all-baseline 0.00.
- line: conduct_percentage 5400.00; usage_line_addition 4900.00; membership_line_addition 4700.00 (cross: membership ae727ffd); tenure_line_addition 5000.00; purchase_volume_addition 5000.00; all-baseline 4200.00.
All bear weight; whole baselines ≠ gold. Near-misses: posting 325c6bf0 vs the disputed posting; late fee 99a3a603 outside the two-month window; the bounced 10-02 payment that precedes the fee date (line gate); the 1421.69 dispute credit that pulls net purchases from 6587.46 to 5165.77. Stamps: none.

#### task-specific findings (revision_2, frozen)
T0-1 closed (rebuilt seed). No new task-specific defect.

### source_gt_comparison (revision_2)
Reveal 2026-10-24T13:25Z of tasks/0.json sha256 42a8ad55…7a96 (after the revision_2 frozen sections of all three files were on disk).
| item | frozen | GT | same? |
|---|---|---|---|
| reads | customers, identity, card holding, card events, orders, membership | same six | same |
| settle args | 32e88020-…, fbef94b5-…, 1412.84, 1421.69 | same | same |
| payment (user) | 2026-09-09, 319.49 | same | same |
| new limit | 5200.00 | 5200.0 | same |
| order / owners | settle (agent) → pay (user) → raise (agent) | steps 7 → 9 → 11, same owners | same |
Closure, value against value: line edge value_input / cure_open / state / make_card_payment = same; opening "latest payment 10-02 before the 10-08 fee" = same; flip 3900.00 → 5200.00 = same; dup edge value_input / owed_net / state / settle = same; owed_net 3956.18 → 3947.33 = mine (4… opening 5369.02 − 1412.84 = 3956.18; after 3947.33); skip-settlement 328.34 and 5300.00 = same; skip-payment 3900.00 = same; resolution order = same.
factor_sensitivity figure against figure: dup 1505.48 / 1403.13 / 1371.69 / 1389.69 / 1429.61, baseline 1412.84 = same; catch-up 0.0 / 272.16 / 276.49 / 225.83, baseline 0.0 = same; line 5400 / 4900 / 4700 / 5000 / 5000, baseline 4200 = same.
Proof text: rationale §7 order count (15 in-store + the TV order) now correct (O-T0-a closed); "re-presented without re-authorization" matches the seed.

Verdicts (revision_2): SOURCE-POLICY RED (R-D2r demonstrated here: after the gold settlement the dup policy is still owed, 1421.69, a second final credit; R-D3r: the line wait is met on this world by a 1.00 payment); SOURCE-CHAIN PASS (tree holds on this world: both edges engaged, unmet, load-bearing, one owner=user write); SOURCE-FACTOR RED (N1: shortfall_measure's output gates the other three catch-up factors — its baseline gives 0.00 instead of 183.99; N2 structural on the line); SOURCE-TASK PASS on the unique-solution comparison except for R-D2r's second terminal state.

### findings (revision_2)
1. T0-1 — closed (seed rebuilt; no purchase approved over the limit).
2. R-A1 — closed (declared overwrite).
3. SOURCE-POLICY RED — R-D2r (residual): dup scope has no open-status test; on this world the rule is still due after its own write. Location: card_ext_duplicate_final_credit rule scope sentence / compute `confirmed`.
4. SOURCE-POLICY RED — R-D3r (residual): line wait satisfied by any payment credited on or after the fee date (1.00 on this world → 5300.00 with 134.50 unpaid). Location: card_ext_line_increase prerequisite sentence, compute `cure_open`.
5. SOURCE-FACTOR RED — N1 (new, introduced by the R-A3 rework): catch-up result gated by shortfall_measure. Location: card_ext_catch_up_payment rule last sentence, compute `result`.
6. Structural, charter-global, no value consequence here: N2 (usage T2 definition), N4 (dispute-adjusted minimum).

## revision_3

### source_derivation_frozen (revision_3)
- freeze: written before the 2026-10-24T13:56:33Z reveal; view 726079d9…78ed (unchanged), charter 24dbff27…54d4. contamination_disclosure: the world is unchanged since revision_2, so the round-2 gold of this world is known to me; this revision therefore re-derives under the new charter with the gate DSL and my own arithmetic and states where it differs from round 2 (it does not), rather than claiming a blind answer.
- Problem tree as revision_2 (line ←value_input catch-up ←value_input dup; owner=user payment). Line wait now: net payments against 2026-09-09 = 135.50 − 135.50 = 0.00 < 135.50 → unmet; catch-up wait: dispute fbef94b5 open (no resolution entry), Northgate order, Store Card, two postings 2741.89 > charged 1412.84 + 0.00 refunds → unmet. Load-bearing: skip settlement → catch-up 328.34, line 5300.00; skip payment → 3900.00.
- Derivation: settle 1412.84 released / **1421.69** (only billing-error dispute on 2026-06-09, notice 06-17 after the close → fee tier 1, 32.00); payment **319.49** against 2026-09-09 (135.50 + 47.33 + 43.00 + 93.66; not met → owed); limit **5200.00** (unmet −183.99 after the payment; 195.00 + 268.45 + 500 + 200 + 150 → 5213.45).
- factor_weight: dup 1505.48 / 1403.13 / 1371.69 / 1389.69 / 1429.61 (all-baseline 1412.84); catch-up 183.99 / 272.16 / 276.49 / 225.83 (0.00); line 5400 / 4900 / 4700 / 5000 / 5000 (4200). All bear weight.
- Charter-global findings against this world: R3-1 (one dispute on the first statement), R3-2 (one payment), R3-3 (no dispute on the missed statement), R3-5 (no refunds on the order) — no consequence here. O-11 applies (empty order history).

### source_gt_comparison (revision_3)
Reveal 2026-10-24T13:56:33Z of tasks/0.json sha256 9e2c26cf…a2a2d. Reads: GT adds find_order_events(order 269b5650) — matches the dup's new order-history read (returns no rows, O-11). Writes: settle 1412.84 / 1421.69, payment 2026-09-09 / 319.49 (user), limit 5200.00 — all same. Closure: line edge value_input / cure_unmet / state / make_card_payment (same), opening unmet 135.50 (same), flip to 5200.00 (same); dup edge owed_net 3956.18 → 3947.33 (same); skip effects 328.34 / 5300.00 / 3900.00 (same); order same. factor_sensitivity: dup 1505.48 / 1403.13 / 1371.69 / 1389.69 / 1429.61, baseline 1412.84; catch-up 183.99 / 272.16 / 276.49 / 225.83, baseline 0.0; line 5400 / 4900 / 4700 / 5000 / 5000, baseline 4200 — all same.

Verdicts (revision_3): SOURCE-POLICY PASS on this world (R3-1/R3-2/R3-3/R3-5 are charter-global with no consequence here); SOURCE-CHAIN PASS; SOURCE-FACTOR PASS (14 factors, all bear weight, none struck); SOURCE-TASK PASS. Task0 = PASS; the difficulty still fails on the charter-global REDs in `_difficulty.md` § revision_3.

### findings (revision_3)
R-D2r, R-D3r, N1, N2 (the round-2 REDs that bore on this task) — closed. No task-level defect. Observations O-11 (empty order history read by gold).

## revision_4

### source_derivation_frozen (revision_4)
- written before the round-4 reveal; view 726079d9…78ed (unchanged since revision_2 — the earlier gold of this world is known to me, so this is a re-derivation under the new charter, not a blind answer); charter f4bdc22b…5040.
- The missed statement 2026-09-09 carries no billing-error dispute → its minimum is the printed 135.50; tree, waits and load-bearing runs as revision_3. Derivation (gate DSL + own arithmetic): settle 1412.84 / **1421.69**; payment **319.49** against 2026-09-09; limit **5200.00**. factor_weight: dup 1505.48 / 1403.13 / 1371.69 / 1389.69 / 1429.61 (1412.84); catch-up 183.99 / 272.16 / 276.49 / 225.83 (0.00); line 5400 / 4900 / 4700 / 5000 / 5000 (4200). All bear weight; none struck.
- Charter-global findings against this world: R4-1 needs two disputes on 2026-09-09 (none here); R4-2 is a refund defect (out of scope). No consequence.

### source_gt_comparison (revision_4)
Frozen section written 2026-10-24T18:41:21Z; reveal 18:41:29Z of tasks/0.json sha256 6843ee0a…6720. Writes 1412.84 / 1421.69, 2026-09-09 / 319.49 (user), 5200.00 — same; reads same as revision_3 (incl. find_order_events). Closure: both edges value_input / state with gates cure_unmet, owed_net and resolvers as derived; 135.50 unmet → 5200.00; 3956.18 → 3947.33; skip effects 328.34 / 5300.00 / 3900.00 — same. factor_sensitivity and baselines figure for figure same (1505.48 / 1403.13 / 1371.69 / 1389.69 / 1429.61, 1412.84; 183.99 / 272.16 / 276.49 / 225.83, 0.0; 5400 / 4900 / 4700 / 5000 / 5000, 4200).
Verdicts (revision_4): SOURCE-POLICY PASS on this world; SOURCE-CHAIN PASS; SOURCE-FACTOR PASS; SOURCE-TASK PASS → task0 PASS (charter-global REDs R4-1, R4-2 have no consequence here).

## revision_5

### source_derivation_frozen (revision_5)
- written 2026-10-24T23:07Z before the round-5 reveal (resumed after an account cut); view 726079d9…78ed (unchanged since revision_2 — earlier gold of this world known, re-derived under charter 1af18631…e7ac).
- 2026-09-09 carries no billing-error dispute → no referral, printed minimum 135.50; tree, waits and load-bearing runs as revision_4. Derivation: settle 1412.84 / **1421.69**; payment **319.49** against 2026-09-09; limit **5200.00**; sensitivities and baselines unchanged (dup 1505.48 / 1403.13 / 1371.69 / 1389.69 / 1429.61, 1412.84; catch-up 183.99 / 272.16 / 276.49 / 225.83, 0.00; line 5400 / 4900 / 4700 / 5000 / 5000, 4200).
- R5-1 needs two disputes on the missed statement (none here); R5-2 is a refund defect. No consequence on this world.

### source_gt_comparison (revision_5)
Reveal 2026-10-24T23:07:25Z of tasks/0.json (sha256 4b13eca0…). Writes 1412.84 / 1421.69, 2026-09-09 / 319.49 (user), 5200.00 and reads — same; closure edges, gates, flips (135.50 → 5200.00; 3956.18 → 3947.33) and skip effects (328.34 / 5300.00 / 3900.00) — same; sensitivities and baselines figure for figure same.
Verdicts (revision_5): SOURCE-POLICY PASS on this world; SOURCE-CHAIN PASS; SOURCE-FACTOR PASS; SOURCE-TASK PASS → task0 PASS.

## revision_6

### source_derivation_frozen (revision_6)
- written 2026-10-24T23:31Z before the round-6 reveal; view unchanged (726079d9…78ed; earlier gold known); charter 020883d2…f212. 2026-09-09 carries no billing-error dispute → no referral; derivation unchanged: settle 1412.84 / **1421.69**, payment **319.49** against 2026-09-09, limit **5200.00**; sensitivities and baselines as revision_5. R6-1 needs disputes on the missed statement (none here); R6-2 is a refund defect. No consequence.

### source_gt_comparison (revision_6)
Reveal 2026-10-24T23:31:34Z of tasks/0.json (sha256 ba4b2901…). Writes 1412.84 / 1421.69, 2026-09-09 / 319.49 (user), 5200.00; closure (value_input cure_unmet / owed_net, state, resolvers, order) and skip effects (3900.00; 328.34 / 5300.00); sensitivities and baselines — all same. Verdicts: SOURCE-POLICY, SOURCE-CHAIN, SOURCE-FACTOR, SOURCE-TASK PASS → task0 PASS.

## revision_7

### source_derivation_frozen (revision_7)
- written 2026-10-24T23:46Z before the round-7 reveal; view unchanged (earlier gold known); charter 32f4e896…3be4. 2026-09-09 carries no billing-error dispute → no referral; derivation unchanged: settle 1412.84 / **1421.69**, payment **319.49** against 2026-09-09, limit **5200.00**; sensitivities and baselines as revision_6. R7-1 touches the catch-up rule text of this task's chain but no value.

### source_gt_comparison (revision_7)
Reveal 2026-10-24T23:46:43Z of tasks/0.json (sha256 d5d6953b…). Writes 1412.84 / 1421.69, 2026-09-09 / 319.49 (user), 5200.00; closure (value_input cure_unmet / owed_net, state, resolvers, order) and skip effects; sensitivities and baselines — all same. Verdicts: SOURCE-POLICY PASS on this world (R7-1 is a rule-placement defect with no value here), SOURCE-CHAIN PASS, SOURCE-FACTOR PASS, SOURCE-TASK PASS → task0 PASS.

## revision_8

### source_derivation_frozen (revision_8)
- written 2026-10-24T23:57Z before the round-8 reveal; view unchanged (earlier gold known); charter b7c2a711…cc22 (rule text only; compute unchanged). No referral on 2026-09-09; derivation unchanged: settle 1412.84 / **1421.69**, payment **319.49** against 2026-09-09, limit **5200.00**; sensitivities and baselines as revision_7.

### source_gt_comparison (revision_8)
Reveal 2026-10-24T23:57:40Z of tasks/0.json (sha256 60462617…). Writes 1412.84 / 1421.69, 2026-09-09 / 319.49 (user), 5200.00; closure edges, gates, resolvers and order; sensitivities and baselines — all same. Verdicts: SOURCE-POLICY, SOURCE-CHAIN, SOURCE-FACTOR, SOURCE-TASK PASS → task0 PASS.

## revision_9

### source_derivation_frozen (revision_9)
- written 2026-10-25T00:17Z before the round-9 reveal; view unchanged (earlier gold known); charter 1dc5ae2b…fe0d (rule words and binding lists only; compute unchanged). Derivation unchanged: settle 1412.84 / **1421.69**, payment **319.49** against 2026-09-09, limit **5200.00** (usage 5 % of 5369.02 = 268.451 → 268.45 by the now-stated cent rounding; the hundred-dollar floor is unaffected); sensitivities and baselines as revision_8.

### source_gt_comparison (revision_9)
Reveal 2026-10-25T00:17:54Z of tasks/0.json (sha256 1bde9ce7…). Writes 1412.84 / 1421.69, 2026-09-09 / 319.49 (user), 5200.00; closure edges, gates, resolvers and order; sensitivities and baselines — all same. Verdicts: all four PASS → task0 PASS.
