# Policy-task audit — store_card_billing_and_disputes / charter-global

## charter_global_frozen
- freeze time: 2026-10-23T20:56Z (written before any task's GT was revealed; nothing below is derived from `evaluation_criteria`, `computations` or any other masked field)
- auditor: independent policy auditor (erl-task-policy-audit), revision_1
- hashes (re-computed, equal to the coordinator snapshot /tmp/erl0080_coord/snaps/store_card_billing_and_disputes.r1.txt):
  - `card.extended.yaml` 03a909807e07fe8ea4de9a79b3cbdf23f1ff1ae77080c3bd8b40a3016f1bac3e
  - `task_tools.py` b95bcb32eaaabdd2103a3c3267b50ce2e81a23f3adaa2c00534e7bf7fc82e158
  - task0.view.json ce76fbe5…aa74, task1.view.json d1b2d38d…61a2
- entry conditions (Step 0): gate snapshot present with commands and output lines — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; masked views present with hashes. Complete.
- read: blueprint (blueprint.yaml, db_schema.json, share_tools.py, products/card.yaml, and order/market/membership charters for cross-category facts), this difficulty's `card.extended.yaml`, `task_tools.py`, the two masked views. Masked / unread: `tasks/*.json`, `worklog.md`, `plan.md`, every other difficulty's tasks and audits.
- base copy: `card.extended.yaml` lines 1–1332 are byte-identical to `blueprint/products/card.yaml` (diff shows only one trailing blank line).
- binding checklists applied: audits/render_source/XF_recipe.md (all 30 points on all 5 extended policies), audits/render_source/owner_ruling.md.
- scratch: /tmp/erl0080_audit_card/ (dump.py, t0.py, t0b.py, t1.py, probe.py — the probes run the gate's own DSL evaluator `check_compute.build_env` on scratch copies of the masked views).

### policy_conflict_scan
Extended policies (5): `card_ext_duplicate_final_credit` (state_due, settle_duplicate_dispute_b93aba52, agent), `card_ext_line_increase` (on_request, raise_credit_limit_a1e4ca90, agent), `card_ext_catch_up_payment` (on_request, make_card_payment_5ec32b69, user), `card_ext_first_late_fee_courtesy` (state_due, reverse_late_fee_courtesy_ba087f69, agent), `card_ext_credit_balance_refund` (on_request, refund_credit_balance_0212c7e9, user).
- Overlapping subjects: `card_dispute_credit`/`card_resolve_dispute` (dup only), `card_change_limit` (line only), `card_post_payment` (catch-up only), `card_reverse_fee` (courtesy only), `card_refund_credit_balance` (refund only). No two extended policies write the same event type.
- Triggers: the two state_due policies fire "whatever the contact is about" (courtesy) / "at once" (dup). Their scopes are record tests (dup: duplicate reason + no-provisional tier + Northgate order source; courtesy: only late fee of 12 months + no courtesy in 12 months). Cross-fire on the two worlds: task0 has two late fees in 12 months → courtesy out of scope; task1 is a World Mastercard (provisional credit) with no duplicate dispute → dup out of scope. No cross-fire.
- Time anchors: all "last N months" windows are stated as "entries dated after the same calendar day N months before today/the review date", matching `within_months` (MONTHS(d, NOW) < N).
- Cross-category read boundaries: dup reads `order.amount_paid_usd`; line and courtesy read `membership.variant_name/status`; refund reads `order.amount_paid_usd/status/payment_method_type`. All read-only.
- Conflicts found with in-force base clauses: see `override_declarations` (U1–U3) and findings.
- Scopes of the M=2 tasks (derived from the persona + world, blind): task0 = {line_increase ← catch_up_payment ← duplicate_final_credit}; task1 = {credit_balance_refund ← first_late_fee_courtesy}. Pairwise disjoint and jointly cover all 5 extended policies.

### rule_compute_equivalence
Mechanical sweep (scratch script): every `compute_basis` quotation, every `policy_source`, every `baseline.rule` and every `replaced_by` is verbatim in its policy's `rule`; every compute binding has a basis and vice versa. The semantic two-way sweep, with probes (decoy / absent / second record) through the gate's own DSL, found these rule ≠ compute cases (each listed as a member of finding R-B1):
1. dup selector: rule settles "a billing-error dispute recorded with the reason duplicate, … whose source record is a Northgate order; where an account carries more than one such dispute, it settles the one with the latest notice date"; compute `d_ref/d_amt/d_date/d_src/d_stmt = LATEST(card_open_dispute, dispute_reason='duplicate')` has no source test. Probe P1 (later Northgate Marketplace duplicate dispute on the same Store Card): compute picks d_src='mkt_x', `order_paid`=0, result 60.54; the rule picks the Northgate-order dispute (1421.69 on that world).
2. dup reinstatement: rule "times the days from the notice date through that statement's closing date, both counted"; compute `DAYS(d_date, latest_close) + 1` goes negative when the notice postdates the latest close. Probe P2 (notice moved to 2026-10-12, latest close 2026-10-09): `reinstated` = −0.14, i.e. the "reinstated" interest is added to the credit; the rule's day range is empty (0).
3. refund dispute hold, second tier: rule "where no dispute stands open and the disputes resolved for the merchant carry provisional credits not yet re-billed, those unbilled credits are held"; compute `merchant_resolved - rebilled` uses the resolved amounts, not provisional credits. Probe P3 (merchant-resolved dispute, no provisional credit ever posted): `provisional_posted`=0.0 yet `dispute_hold`=186.40; the rule holds 0.
4. refund payment hold: rule "the most recent payment … that most recent payment is held" states no same-day tie rule; `LATEST` keeps the first row. Probe P6 (second payment the same day): compute holds 554.18 only; a reader of the rule has two "most recent" payments (hold one, or both = 579.18).
5. catch-up shortfall second tier: rule "a billing-error dispute received after its closing date and on or before its payment due date concerns a transaction the statement shows … less the tier's minimum payment percentage of the disputed amount"; compute `cure_disputed = SUM(all billing_error disputes with statement_date=cure_stmt)` and `cure_notice = LATEST(...)` — (a) a second dispute on the same statement received before the close is added into the disputed amount; (b) a later dispute received after the due date makes `cure_notice > cure_due` and drops the qualifying one to the third tier.
6. "purchases": the catch-up rule lists "purchases, interest, fees, returned payments, re-billed dispute credits and credit balance refunds raise it" and the line rule speaks of "the purchase postings"; both computes `SUM(card_post_purchase)` include `transaction_kind='cash_advance'` rows (base event: "A purchase or cash advance posts"). Probe P5 (600.00 cash advance on the task0 world): line `net_purchases` 7465.56 → volume tier 300; catch-up `owed_in` +600.
7. courtesy lateness ladder gap: rule "a payment credited 1 to 3 days after the due date grants a flat 15 points; … 4 to 10 days … ; a later payment, or none, grants none" — a most-recent payment credited on or before the due date (days late ≤ 0) is in no stated case; compute gives 0 (probe P7: days_late 0 → 0). The ladder in `factors` says "otherwise", the rule does not.

### action_binding_and_uuids
- Each `(target_tool, computes)` is claimed once: (settle_duplicate_dispute_b93aba52, final_credit_usd), (raise_credit_limit_a1e4ca90, new_credit_limit_usd), (make_card_payment_5ec32b69, amount_usd), (reverse_late_fee_courtesy_ba087f69, reversal_amount_usd), (refund_credit_balance_0212c7e9, refund_amount_usd).
- uuid8s b93aba52, a1e4ca90, 5ec32b69, ba087f69, 0212c7e9: no shared prefix, no sequence, no shared tail — independently generated as far as can be judged.
- Function bodies (task_tools.py 29–205): none reads eligibility, a prerequisite state or another tool's effect; each validates only positivity/whole cents (and a YYYY-MM-DD date for the payment); each calls ctx.create/ctx.update in its own body; no forbidden substrings (grep clean); exact half-up helper is a class static method.
- Docstrings: no other tool named, no concrete example values. Every docstring carries "Afterwards the cardholder sees …" and raise_credit_limit's summary says "after a requested credit line review" — both describe the call's own post-state, not a position relative to another problem (observation O-1).
- Bodies accept any `card_account_id` / `dispute_event_id` / `late_fee_event_id` without checking that the row exists or is of the declared kind (e.g. settle accepts a non-dispute id) (observation O-2; no scored consequence shown).
- Owner ruling: make_card_payment (user) — ruling (b), holder-completed secure payment; refund_credit_balance (user) — ruling (a), the cardholder's own credit-balance refund request. But see R-C2 (the catch-up rule's "no payment method on file" premise is false wherever autopay is enrolled).

### prerequisite_graph
| blocked policy | problem | kind | gate (binding) | form | resolved_by = depended-on target_tool | verdict |
|---|---|---|---|---|---|---|
| card_ext_line_increase | card_ext_catch_up_payment | value_input | cure_unmet (exists) | state | make_card_payment_5ec32b69 ✓ | structurally OK |
| card_ext_catch_up_payment | card_ext_duplicate_final_credit | value_input | owed_net (exists) | state | settle_duplicate_dispute_b93aba52 ✓ | structurally OK |
| card_ext_credit_balance_refund | card_ext_first_late_fee_courtesy | value_input | credit_bal (exists) | state | reverse_late_fee_courtesy_ba087f69 ✓ | structurally OK |
`prerequisite: []` on dup and courtesy. Graph: refund → courtesy; line → catch-up → dup. Acyclic; no edge points at a base policy or at itself; every `policy_source` verbatim in its own rule (sweep); no `fallback_reason` needed (all state form); no authoring-viewpoint phrasing. `condition` texts match the sentences' strength. Satisfiability of each edge by its resolver in every engaged world is NOT given — see R-D1, R-D2, R-D3.

### prerequisite_sentences
- line: "A requested credit line increase is granted only after the statement for which the most recent late fee was recorded has payments recorded against it, net of the payments returned unpaid, that reach its minimum payment due." Connective "only after"; waits on a record-visible state (payments carrying that statement's closing date, net of returned ones, vs its minimum_due_usd); no tool/id/snake_case. The only write of this difficulty that records a payment against a statement is the catch-up payment (make_card_payment … statement_closing_date). Derivation: sentence → missed statement (latest late fee's statement_date) → shortfall → the catch-up rule ("the payment a cardholder makes to bring a past-due … account back to good standing … measured on the missed statement") → payment recorded against that statement. Single reading.
- catch-up: "The catch-up payment is not fixed until every duplicate-posting dispute that the Northgate order record confirms has its final credit posted on the account." Connective "not … until"; state = a final dispute credit posted for each confirmed duplicate dispute; the only write posting a final dispute credit is the dup settlement. Single reading — but broader than the resolver's scope (R-D1, R-D2).
- refund: "The credit balance refund is fixed only after every late fee that is the only late fee of the last 12 months on an account with no courtesy reversal in that time carries its courtesy reversal." Connective "only after"; state = a courtesy reversal against that fee; the only write is the courtesy reversal; its set equals the courtesy rule's "qualifying" set exactly; the courtesy share is ≥ 20 % so the reversal is always > 0. Single reading; satisfiable.
- No depended-on rule restates the sentence; no rule carries a second wording, a tool name or another problem's id; no rule states a cross-problem order that grounds no edge.

### override_declarations
Sentence-by-sentence against each `base_policy_refs` entry (and against base sentences that govern the same scored quantity even where the ref is missing):
- dup vs card_dispute_credits: "When a dispute is resolved for the cardholder … a final credit of the disputed amount posts" — declared, replaced_by self-scoped and restates the out-of-scope case ✓. "Where provisional_credit_on_open is true …", "A dispute credit can be posted only on an account in active, suspended or closed status", "When it is resolved for the merchant …", "A withdrawn dispute …", "Unauthorized charges …" — followed or not touched.
- dup vs card_billing_dispute: notice window, tracks, dispute-once, return-on-record, resolution limits, "keeps up to dispute_noncompliance_forfeit_usd" (extended K noncompliance_keep_usd = 50.00 = base 50.00) — followed.
- **U1 (undeclared)** dup vs card_evt_late_and_returned_fees (not in base_policy_refs): base "A fee charged in error, or above the minimum-payment ceiling, is reversed in full as billing_error or for the excess as regulatory_cap." The dup rule settles exactly those two cases ("it is that whole late fee" when the dispute-adjusted minimum was met = a fee charged in error; "the late fee less the dispute-adjusted minimum" = the excess above the ceiling) as part of the dispute final credit (card_dispute_credit), not as a card_reverse_fee. No overwrite names the base sentence.
- line vs card_product_and_limit: line-review age, active status, "further request … after the last limit change" (not restated; "considered only when the base rule's account-age and active-status conditions hold" is a necessary condition, does not retire it), over-limit/decline sentence — followed. `overwrite: []` correct.
- **U3 (undeclared)** catch-up vs base measure card_msr_days_past_due ("From the payment due date of the oldest statement whose minimum payment remains unmet …; 0 when every minimum payment due has been met"): the catch-up rule redefines "The days past due are the calendar days from the missed statement's payment due date to today" — no unmet test, and anchored on the latest-late-fee statement rather than the oldest unmet one. card_evt_payments sentences (channels, cutoff, statuses, allocation, autopay, credit balance) — followed.
- courtesy vs card_evt_late_and_returned_fees: courtesy sentence declared; replaced_by self-scoped and restates the in-force base content for every other late fee ✓. Other sentences (late fee, repeat fee, cap, returned fee, single-event) followed.
- **U2 (undeclared)** refund vs card_evt_payments: base "a credit balance above credit_balance_refund_min_usd is refunded within credit_balance_refund_business_days business days of the cardholder's written request, and any credit balance above that amount remaining after credit_balance_auto_refund_months months is refunded without a request." The refund rule withholds parts of the credit balance with no release: "The rewards hold … which are statement credits and are not paid out as cash", the dispute hold (open disputes may run up to 90 days, far beyond 7 business days). `overwrite: []`.

### factor_ladders
| policy | factor | label | tiers | multi-source (non-fall-through tiers) | cross_difficulty | ladder in rule | structural verdict |
|---|---|---|---|---|---|---|---|
| dup | settled_principal | method | 3 | T1 single (credits), T2 multi (credits+postings+order) | null (reads order — mislabel O-3) | yes | pairs T1/T2 (credit rows vs order rows), T1/T3 (credit rows), T2/T3 (order rows) distinct ✓ |
| dup | carried_error_days | parameter | 3 | multi (interest+payments+statement) | null | yes | ✓ |
| dup | noncompliance_allowance | parameter | 3 | multi (dates+correct part) | null | yes | ✓ |
| dup | error_late_fee | parameter | 3 | multi (fee+due+payments) | null | yes | ✓ (but see U1) |
| dup | correct_part_reinstatement | parameter | 3 | multi | null | yes | ✓ (edge R-B1.2) |
| line | conduct_percentage | parameter | 3 | multi | null | yes | **unreal ladder (F-3a)** |
| line | line_use_sizing | method | 3 | single | null | yes | **T2/T3 no distinguishing input (F-1)** |
| line | membership_line_addition | parameter | 3 | single | membership | yes | ✓ |
| line | tenure_line_addition | parameter | 3 | single | null | yes | ✓ |
| line | purchase_volume_addition | parameter | 3 | multi (purchases, credits, dispute credits) | null | yes | ✓ (edge R-B1.6) |
| catch-up | shortfall_measure | method | 3 | multi | null | yes | pairs distinct (returned input / disputed+floor max / plain) ✓ |
| catch-up | over_limit_restoration | parameter | 3 | multi | null | yes | ✓ |
| catch-up | restoration_fee | parameter | 3 | nominally multi | null | yes | **condition holds of every customer reaching the write (F-3d)** |
| catch-up | cycle_since_miss | method | 3 | multi | null | yes | T1 min-due field / T2 interest field / T3 nothing ✓ |
| courtesy | tenure_points | parameter | 3 | single | null | yes | ✓ |
| courtesy | lateness_points | method | 3 | single | null | yes (gap R-B1.7) | **T1/T3 both constants, no distinguishing input (F-1)** |
| courtesy | membership_points | parameter | 3 | single | membership | yes | ✓ |
| courtesy | automatic_payment_points | parameter | 3 | single | null | yes | ✓ |
| courtesy | history_points | parameter | 3 | multi | null | yes | **non-monotone ladder (F-3b)** |
| courtesy | coverage_points | parameter | 3 | multi | null | yes | ✓ |
| courtesy | (baseline / fall-through share 20 %) | — | — | — | — | — | **unreal baseline vs the charter's own full courtesy (F-3c)** |
| refund | payment_clearing_hold | method | 3 | T1 single | null | yes | **T1/T2 same field (payment amount_usd) — one input per XF-7 (F-1)** |
| refund | open_dispute_hold | parameter | 3 | multi | null | yes | ✓ (edge R-B1.3) |
| refund | rewards_cash_hold | parameter | 3 | multi | null | yes | ✓ (but see U2) |
| refund | pending_order_hold | parameter | 3 | single | order | yes | **holds only one of several pending orders (F-3e)**; framing R-C3 |
Declared counts: dup 5 (1 method, 4 parameter); line 5 (1/4); catch-up 4 (2/2); courtesy 6 (1/5); refund 4 (1/3). Counts after striking the factors failed below: line 3 (0 method), catch-up 3, courtesy 4 (0 method), refund 2 (0 method); dup 5 ✓. Cross-difficulty: line (membership), courtesy (membership), refund (order). Assembly sentences are generic (XF-2 ✓). No factor binding reads another factor's binding (XF-1 mechanical read-set ✓), except the multiplicative split F-2. No factor id is a substring of a tool name (XF-9 ✓).

### findings
Each finding: symptom → root cause → evidence → demonstrated consequence → artifact/location → tasks it bears on. All are new (revision_1).

**R-A1 SOURCE-POLICY RED — U1 undeclared override: erroneous / over-ceiling late fee folded into the dispute final credit.** Symptom: two in-force clauses settle the same late fee. Root cause: dup rule "The late fee carried by the error is set by the late fee recorded for the statement that first showed the disputed posting: … it is that whole late fee; … it is the late fee less the dispute-adjusted minimum" credits it inside `final_credit_usd`, while base card_evt_late_and_returned_fees "A fee charged in error, or above the minimum-payment ceiling, is reversed in full as billing_error or for the excess as regulatory_cap" remains in force (no overwrite; card_evt_late_and_returned_fees not in base_policy_refs). Consequence: a base-following reader posts the final credit without the fee and reverses the fee as billing_error (no tool exists for that reason; the only fee tool hard-codes courtesy_waiver), or does both (double credit). Demonstrated on task0 (see task0.md). Location: card_ext_duplicate_final_credit.rule/overwrite, compute `carried_fee`. Bears on task0.

**R-A2 SOURCE-POLICY RED — U2 undeclared override: refund holds vs base credit-balance refund.** Root cause: base card_evt_payments "a credit balance above credit_balance_refund_min_usd is refunded within credit_balance_refund_business_days business days of the cardholder's written request, and any credit balance above that amount remaining after credit_balance_auto_refund_months months is refunded without a request" vs refund rule "The rewards hold follows the outside-purchase rewards credited in the last 12 months, which are statement credits and are not paid out as cash" (withheld permanently) and the dispute hold (withheld for the life of an open dispute, up to 90 days). `overwrite: []`. Consequence: a reader of the base clause refunds the rewards part (and anything beyond 7 business days); demonstrated on task1. Location: card_ext_credit_balance_refund. Bears on task1.

**R-A3 SOURCE-POLICY RED — U3 undeclared redefinition of days past due.** Base measure card_msr_days_past_due: "From the payment due date of the oldest statement whose minimum payment remains unmet, to the date being evaluated. … 0 when every minimum payment due has been met." Catch-up: "The days past due are the calendar days from the missed statement's payment due date to today." Two readings in world W3: statements S1 (due D1) and S2 (due D1+31) both unpaid, late fees on both, today = D1+40 → base 40 days (30+ band: restoration fee = every late fee in 2 months, cycle-since-miss = latest minimum), catch-up definition 9 days (1–29 band: that late fee, latest interest or nothing). World W3′: missed statement later paid in full (cured), today 45 days after its due date → base 0 (third tiers, nothing), catch-up 45 (30+ band: adds the latest statement's minimum and all late fees). Location: card_ext_catch_up_payment.rule. Bears on no task's scored value (task0: both definitions give 10 — see task0.md).

**R-B1 SOURCE-POLICY RED — rule ≠ compute on decoy / edge records (XF-10, XF-8).** Members 1–7 as listed under `rule_compute_equivalence` (dup source test, dup negative reinstatement, refund dispute-hold second tier, refund same-day tie, catch-up disputed-amount aggregate, cash advances counted as purchases, courtesy lateness gap ≤ 0 days). Each is demonstrated by its probe value there. Bears on no task's scored value (neither world contains the decoys; checked in the task files).

**R-B2 SOURCE-POLICY RED — "the greater of A and B less C" has two readings (XF-12).** dup: "The dispute-adjusted minimum is the greater of the tier's minimum payment floor and the minimum payment due printed on the statement … less the tier's minimum payment percentage of the disputed amount"; catch-up: "the shortfall is the greater of the tier's minimum payment floor and that minimum payment due less the tier's minimum payment percentage of the disputed amount, … less the payments recorded against it". Reading A max(floor, min − pct) (compute); reading B max(floor, min) − pct. World: Store Card, printed minimum 50.00, disputed 1,500.00 (1 % = 15.00): A = 40.00, B = 35.00 (catch-up shortfall with 0 paid: 40.00 vs 35.00). Neither task world separates the readings (task0: 116.14 − 14.13 = 102.01 > 40 under both).

**R-C1 SOURCE-POLICY RED — dup investigation test confirms non-duplicates and re-credits credits already given.** Rule "when those postings total more than the order's amount paid, the investigation confirms the error at once"; the order charter defines amount paid as "Net amount paid on the order before tax; merchandise lines and fees book in, and returns, price adjustments and other refunds book out." World: Store Card, one 500.00 posting for a Northgate order, a 100.00 return credited against that posting (amount paid 400.00), cardholder files a duplicate dispute on the 500.00 posting: postings 500.00 > 400.00 → "confirmed", settled principal (first tier) = 500.00 − 100.00 = 400.00 → the whole legitimate charge is credited although nothing was posted twice. Second member: `first_late_fee` = SUM of late fees for the first statement with no netting of an earlier reversal — a late fee already courtesy-reversed in full (base allows this) is credited a second time inside the dispute credit. No issuer would publish either outcome.

**R-C2 SOURCE-POLICY RED — false framing clause in the catch-up rule (XF-14).** "Northgate keeps no payment method on file for card payments and representatives never take bank or card numbers, so the cardholder makes this payment in person through the secure payment line." Base card_evt_payments: "Automatic payments may be set to one of the tier's autopay_options and are drawn on the payment due date"; card_holdings.autopay_option records enrollment (task1's account is on statement_balance autopay). Where autopay is enrolled a bank account is on file, so the rule's stated reason for the owner=user hand-over is false in those worlds (owner ruling (b) requires the method not to be on file). Bears on no task's scored value (task0 autopay_option = none).

**R-C3 SOURCE-POLICY RED — false framing clause in the refund order hold (XF-14).** "the cardholder's Northgate orders paid with this card that have not yet been charged: where such an order is in placed status, its amount paid is held". The tier test is status only, but placed orders can already be charged: this charter's own seeded world task0 shows order 269b5650 (Ship to Home, placed 2026-05-29, fulfilled 2026-06-02) posted to the card on 2026-05-30 and 2026-05-31 while placed. Two readings in such a world: hold it (status test) or not (it has been charged); the refund differs by the order's amount paid. Bears on no task's scored value (task1's placed order has no posting).

**R-D1 SOURCE-POLICY RED — catch-up wait unsatisfiable on provisional-credit tiers (XF-20).** Catch-up: "not fixed until every duplicate-posting dispute that the Northgate order record confirms has its final credit posted". Dup rule scope: "on an account of a tier without provisional credit". Base (in force for every other dispute): "a provisional credit becomes final with no further posting". World: Northgate Mastercard / World Mastercard / Business Mastercard with an open duplicate dispute on a Northgate order whose postings exceed the amount paid → no write of this difficulty (and no base rule) ever posts a final dispute credit → the catch-up payment is never fixed.

**R-D2 SOURCE-POLICY RED — catch-up wait unsatisfiable with two confirmed duplicate disputes (XF-20, XF-10 second record).** The dup rule "settles the one with the latest notice date" and its selector does not exclude disputes already resolved; after the latest one is settled it is still the latest, so the earlier confirmed duplicate dispute is never settled and the catch-up's "every duplicate-posting dispute … has its final credit posted" never holds.

**R-D3 SOURCE-POLICY RED — the catch-up resolver does not satisfy the line-increase wait in the disputed-statement tier (XF-20).** Line wait: net payments against the missed statement "reach its minimum payment due" (printed minimum). Catch-up second shortfall tier uses the dispute-adjusted minimum. World W: Store Card, missed statement minimum 200.00, billing-error dispute 5,000.00 received after its close and before its due date, no payment, late fee 32.00, today 3 days after the due date (no statement closed since), amount owed net of disputes well inside the limit: shortfall = max(40, 200.00 − 50.00) − 0 = 150.00; restoration fee 32.00; cycle-since-miss 0; over-limit 0 → catch-up 182.00; line gate 200.00 − 182.00 = 18.00 > 0 → no increase after the resolver has run.

**R-E1 SOURCE-FACTOR RED — method tier pairs with no distinguishing input (XF-7).** line_use_sizing T2 "half the current credit limit" vs T3 "the current credit limit": same input, a constant multiplier. lateness_points T1 "a flat 15 points" vs T3 "no points": two constants. payment_clearing_hold T1 "every payment credited in the last two months" (SUM amount_usd of card_post_payment, 2-month window) vs T2 "that most recent payment" (LATEST amount_usd of card_post_payment): the same field, which XF-7 counts as one input whatever the window. Each of these is its policy's only `method` factor, so line, courtesy and refund have no surviving method factor. Bears on task0 (line) and task1 (courtesy, refund).

**R-E2 SOURCE-FACTOR RED — one charge split into two multiplying factors (XF-6).** Line: "The line increase is taken at … percent of …" with conduct_percentage deciding the percent and line_use_sizing deciding the amount it is taken on; `raw_limit = limit + inc_pct/100 * inc_base + …`. Each factor's effect is scaled by the other's tier (on task0: conduct's effect is 5 % of 5,654.83 under line_use T1 but 5 % of 4,000 under its baseline). Bears on task0.

**R-E3 SOURCE-FACTOR RED — unreal ladders (realism, XF-28).**
- (a) conduct_percentage is non-monotone: 1 returned payment + 2 late fees → 5 %; 1 returned payment + 3 late fees → "every other case" 10 %. A worse record earns a larger line increase. Bears on task0.
- (b) history_points is non-monotone: only late fee in 24 months + a payment returned 13–24 months ago → none (0); a second late fee in 24 months + the same old returned payment → 6 points. An extra late fee earns more points. Bears on task1.
- (c) courtesy baseline / fall-through: "The courtesy reversal is 20 percent of the courtesy late fee" applies to the cleanest case (the only late fee in 12 months, no courtesy used), while the same rule keeps "any other late fee may still be reversed as a courtesy in full when … it has no other late fee in the previous six statements". A cardholder with two late fees in 12 months (the earlier one 7–11 statements back) can receive 100 %, a first-time late payer receives 20 %–100 % by points. No issuer publishes a smaller first-late-fee courtesy than its repeat-late-fee courtesy. Bears on task1.
- (d) restoration_fee: "where the account is 30 or more days past due and a late fee was recorded for the missed statement" / "1 to 29 days … and a late fee was recorded for the missed statement" — the missed statement is defined as "the statement for which the most recent late fee on the account was recorded", so the late-fee part holds of every customer who has a missed statement, and with days past due counted from that statement's due date regardless of cure (R-A3) every such customer is ≥ 1 day past due: the fall-through "in every other case there is none" is unreachable for anyone the catch-up rule serves. Bears on task0.
- (e) pending_order_hold: "where several orders share a status, the first on the order list is the one held", and a ready order is ignored whenever a placed order exists. With a placed order 50.00 and a ready order 80.00 (or two placed orders) only one is held; a business holding pending card authorizations holds all of them. Bears on task1 (structure only; task1 has one pending order).

**Observations (no RED):** O-1 docstring "Afterwards" / "after a requested credit line review" wording; O-2 tool bodies do not check referenced ids; O-3 settled_principal reads order records (`evidence: [history, cross_category]`) but declares `cross_difficulty: null`; O-4 several `parameter` factors select a record-derived quantity per tier (noncompliance 50.00 vs the correct part; error_late_fee whole fee vs fee less adjusted minimum; carried_error_days end date notice vs close; open_dispute_hold, rewards_cash_hold) — the labels read as method-like but XF-7 only binds `method` labels; O-5 the base "further request … after the last limit change" rests on a change no card_events row records (card_change_limit is a holding update) — base clause; O-6 cycle_since_miss second tier (1–29 days past due: add the latest statement's purchase interest, not its minimum) and the catch-up's adding interest and fees that are already inside the over-limit excess are unusual treatments but no demonstrable second reading; O-7 the catch-up rule never names the statement the catch-up payment is recorded against (the reader infers the missed statement from "It is measured on the missed statement"); O-8 persona names unique across difficulties not checkable under read isolation.

## closing_checklist
Written after both reveals (2026-10-23T21:01Z). Not closed: the four relationships do not all PASS.
- Audit files: task0.md, task1.md, _difficulty.md present, one per task; no previous revision exists (revision_1).
- Coverage and scopes: the 5 extended policies are covered; task0 {dup, catch-up, line} and task1 {courtesy, refund} are disjoint (GT charter_scope agrees); task tools and GT closed; uuid8s independent.
- Problem trees: task0 2 prerequisites / 2 value_input / owner=user payment; task1 1 / 1 / owner=user refund; difficulty graph acyclic. SOURCE-CHAIN PASS on both worlds; charter-level satisfiability defects R-D1–R-D3 stand.
- Factors: every declared factor bears weight on its task world against an honest baseline and every whole-baseline differs from gold (task files), but the structural strikes (R-E1, R-E2, R-E3) leave line 3/0-method, catch-up 3, courtesy 0 method, refund 2/0-method.
- Gates were not re-run by this auditor (no artifact changed; the coordinator snapshot is the current form).
Charter RED ids: R-A1, R-A2, R-A3, R-B1, R-B2, R-C1, R-C2, R-C3, R-D1, R-D2, R-D3, R-E1, R-E2, R-E3. Task-level additions: T0-1 (task0 seed).

VERDICT revision_1: task0=RED task1=RED charter=R-A1,R-A2,R-A3,R-B1,R-B2,R-C1,R-C2,R-C3,R-D1,R-D2,R-D3,R-E1,R-E2,R-E3

## revision_2

### charter_global_frozen (revision_2)
- freeze time 2026-10-24T13:30Z, before any round-2 GT was read; nothing below is derived from `evaluation_criteria` / `computations` / closures of the rebuilt tasks.
- coordinator snapshot executed (`/tmp/erl0080_coord/snapshot.sh store_card_billing_and_disputes 2`, 2026-10-24T13:17:21Z): task0.view.json 726079d9…78ed, task1.view.json 5ecdd8cf…9889; card.extended.yaml aafb1362…6c34 (changed), task_tools.py b95bcb32…e158 (unchanged); gates EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- inputs read: rework_claims_r2.md (item ids and locations only), the full new extended section (base copy still byte-identical), the two rebuilt views, `tail -1 worklog.md` ("REWORK round 2: gates 7/7 green"). Not read: plan.md, tasks/*.json (until the reveal below).
- re-derivation scope: `card.extended.yaml` changed → every charter-global subsection is re-derived; `task_tools.py` unchanged → `action_binding_and_uuids` carried forward from revision_1 by reference (hash b95bcb32…e158 both rounds).
- scratch: /tmp/erl0080_audit_card/probe2.py (task chains + every factor's baseline substitution through the gate DSL), probe3.py (closed-item re-probes and new decoy / absent / second / same-day-tie probes).

### policy_conflict_scan (revision_2)
Same five policies, targets, owners and triggers as revision_1. No two write the same event type. Base/extended overlaps are now declared for: dup (card_dispute_credits final credit; card_evt_late_and_returned_fees fee-in-error sentence), courtesy (courtesy sentence, now retired for every late fee), refund (card_evt_payments credit-balance refund sentence). Cross-fire on the rebuilt worlds: task0 has two late fees in 12 months (courtesy out of scope) and no credit balance; task1 is a World Mastercard with no duplicate dispute. After each world's own writes: courtesy re-evaluates to `qualifies=False` (not due again); the dup policy re-evaluates to `confirmed=True`, 1421.69 (still due again — R-D2r below). Scopes: task0 {line ← catch-up ← dup}, task1 {refund ← courtesy}; disjoint, jointly complete.

### rule_compute_equivalence (revision_2)
Mechanical sweep: every compute_basis quote, policy_source, baseline.rule and replaced_by is verbatim in its rule; every binding has a basis. Re-probes of the revision_1 members (probe3.py):
- R-B1.1 later Northgate Marketplace duplicate dispute → `confirmed=False`, 0 — rule and compute agree (closed).
- R-B1.2 notice after the latest close → `reinstated=0.0` (closed).
- R-B1.3 merchant-resolved dispute with no provisional credit → second tier now min(provisional − re-billed, merchant-resolved − re-billed) = 0 (closed for that decoy; see N6 for a new decoy).
- R-B1.4 refund same-day second payment entered later → the first-entered payment is held, as the rule now states (closed for the refund). The catch-up's "most recent billing-error dispute" read still has no tie rule (N4c).
- R-B1.5 the catch-up disputed tier now reads one row for amount and notice (rule = compute; but see N4b).
- R-B1.6 cash advance 600.00 → line purchases 6587.46 (excluded), catch-up owed includes it, both as the rules now say (closed).
- R-B1.7 payment credited on the due date → 0 points, stated in the rule (closed).
New rule/compute or edge findings are listed under `findings (revision_2)`.

### action_binding_and_uuids (revision_2)
Carried forward unchanged from revision_1 (task_tools.py b95bcb32…e158 in both rounds). O-1/O-2 remain observations (reworker disputes them; no consequence demonstrated).

### prerequisite_graph (revision_2)
| blocked | problem | kind | gate | form | resolved_by | structural |
|---|---|---|---|---|---|---|
| line | catch-up | value_input | cure_open (exists) | state | make_card_payment_5ec32b69 ✓ | OK |
| catch-up | dup | value_input | owed_net (exists) | state | settle_duplicate_dispute_b93aba52 ✓ | OK |
| refund | courtesy | value_input | credit_bal (exists) | state | reverse_late_fee_courtesy_ba087f69 ✓ | OK |
Acyclic; all policy_source verbatim; conditions match the sentences. Satisfiability: R-D1 closed (catch-up wait narrowed to exactly the dup scope); R-D2 partly closed (R-D2r); R-D3 not closed (R-D3r); new zero-amount wait N3.

### prerequisite_sentences (revision_2)
- line: "A requested credit line increase is granted only after a payment has been recorded against the statement for which the most recent late fee was recorded, credited on or after the day that late fee posted." "only after"; record-visible state; only the payment write produces it. But the state no longer measures a cure (R-D3r).
- catch-up: "The catch-up payment is not fixed until the most recent duplicate-posting dispute on the account, when its source is a Northgate order on a tier without provisional dispute credits and two or more postings carrying that order's reference exceed the order's amount paid, has its final credit posted." "not … until"; state = final credit on that one dispute; only the dup settlement produces it; its object now equals the dup scope.
- refund: unchanged sentence; only the courtesy reversal produces the state; but a zero-amount qualifying case exists (N3).
- No rule restates another's sentence; no tool names / ids; no ungrounded cross-problem order.

### override_declarations (revision_2)
- dup: card_dispute_credits sentence (unchanged, OK); card_evt_late_and_returned_fees "A fee charged in error, or above the minimum-payment ceiling, is reversed in full as billing_error or for the excess as regulatory_cap." now declared, self-scoped to the settled dispute's first-statement late fee, restates the base for every other fee → **R-A1 closed**.
- refund: card_evt_payments credit-balance sentence declared, self-scoped, held parts stay as credit balance and follow the base on a later request / after six months → **R-A2 closed**.
- catch-up: no longer defines "days past due" ("the days since the missed due date") and the result is nothing when the shortfall is nothing → **R-A3 closed**.
- courtesy: the base courtesy sentence is retired for every late fee and the restated tail ("returned payment fees and cash advance fees are never waived as a courtesy") kept → consistent; no sibling retires the same clause.
- line: `overwrite: []`; base line-review sentences followed.

### factor_ladders (revision_2)
| policy | factor | label | pairwise / ladder verdict |
|---|---|---|---|
| dup | settled_principal | method | pairs distinct ✓ |
| dup | carried_error_days, noncompliance_allowance, error_late_fee, correct_part_reinstatement | parameter | ✓ (error_late_fee now on the standing fee) |
| line | conduct_percentage | parameter | 4 tiers, disjoint, monotone in late fees and in returns ✓ (R-E3a closed) |
| line | usage_line_addition | method | T1 top statement balance / T2 12-month net purchases / T3 nothing — distinct inputs ✓ (R-E1 closed for line); **T2's quantity is defined only in purchase_volume_addition's sentence (N2)** |
| line | membership / tenure / purchase_volume | parameter | ✓ |
| line | pct × limit | — | percentage now acts on the current limit only, usage is additive → **R-E2 closed** |
| catch-up | shortfall_measure | method | pairs distinct ✓; **its output gates the whole result (N1)** |
| catch-up | over_limit_restoration, restoration_fee | parameter | restoration_fee fall-through reachable via a reversed fee → **R-E3d closed** |
| catch-up | cycle_since_miss | method | ✓ |
| courtesy | tenure, lateness (now parameter 15/8/0), membership, automatic payment | parameter | ✓ |
| courtesy | history_points | parameter | monotone ✓ (R-E3b closed) |
| courtesy | fee_basis_correction | method | **T1 "fee less reversals" and T2 "fee statement's minimum" coincide on the reachable domain (R-E1r)** |
| courtesy | single courtesy schedule | — | **R-E3c closed** |
| refund | channel_clearing_days, risk_clearing_days | parameter | **one clearing period split into two summed factors (N5)** |
| refund | open_dispute_hold | parameter | see N6 |
| refund | residual_interest_hold | method | T1 new balance × days to completing payment / T2 unpaid part × days to today / nothing — distinct ✓ (R-E1 closed for refund) |
| refund | pending_order_hold, rewards_cash_hold | — | removed → **R-E3e, R-C3 closed** |
Counts: dup 5 (1 m / 4 p); line 5 (1 m / 4 p); catch-up 4 (2 m / 2 p); courtesy 6 (1 m / 5 p); refund 4 (1 m / 3 p). Cross-difficulty: line and courtesy (membership); refund none (task1 still has membership_points). Surviving after strikes: courtesy 5 / 0 method (R-E1r); refund 2 (N5 strikes both clearing factors), 1 method; catch-up 4 but N1; line 5 but N2.

### status of revision_1 findings
| id | status | evidence |
|---|---|---|
| R-A1 | closed | declared overwrite (above) |
| R-A2 | closed | declared overwrite (above) |
| R-A3 | closed | term and result changed (above) |
| R-B1 (1,2,3,4-refund,5,6,7) | closed | probes above; residual tie on the catch-up dispute read → N4c |
| R-B2 | closed | both sentences now two ordered steps (single reading) |
| R-C1 | **partly closed** — member 2 (re-credit of a reversed fee) closed by the standing fee; member 1 remains (R-C1r) | probe3: two legitimate postings 600 + 400 for one order, a 100.00 return credited against the 600 posting (amount paid 900), duplicate dispute on the 400 posting → `order_post_count=2`, 1000 > 900 → `confirmed=True`, principal 100.00, credit 155.05 although nothing posted twice; the 100.00 was already refunded by the return credit. Root cause unchanged: gross postings compared with an amount paid that the order charter books net of returns. |
| R-C2 | closed | framing replaced |
| R-C3 | closed | order hold removed |
| R-D1 | closed | wait object = dup scope |
| R-D2 | **partly closed** (R-D2r) | the older-dispute case is gone, but neither the dup scope nor the catch-up wait tests that the most recent duplicate dispute is still open: probe2 re-evaluates the dup policy on task0 after its own settlement → `confirmed=True`, 1421.69 (the state_due policy is owed again; a second final credit would post). Where the most recent duplicate dispute was withdrawn after a full merchant credit (base: no final credit posts), the catch-up waits on a final credit that only an erroneous settlement of a withdrawn dispute can post. |
| R-D3 | **not closed** (R-D3r) | (a) the new line wait is met by any payment credited on or after the fee date, whatever its amount and even if it is returned: probe3 — a 1.00 payment against 2026-09-09 on task0's world → `cure_open=False`, 5300.00 while the catch-up shortfall is still 134.50; the bounced 135.50 payment moved to the fee date (10-08) and returned 10-12 → `cure_open=False`, 5300.00 with nothing paid. A card issuer does not grant a line increase on a token or bounced payment. (b) unsatisfiable world W: the missed minimum paid in full after the due date but before the fee posted (paid 10-06, due 10-04, fee 10-08 — the posting lag of this charter's own seeds): catch-up shortfall 0 → catch-up "nothing" (the tool rejects 0.00) → line gate `cure_open=True` → the increase can never be granted by any write. |
| R-E1 | line closed, refund closed, **courtesy not closed** (R-E1r) | fee_basis_correction: the only reversals a qualifying late fee can carry are billing_error ("reversed in full") and regulatory_cap ("for the excess" over the minimum); so T1 "fee less those reversals" is either 0.00 or exactly the fee statement's minimum — T2's value. On task1 itself T1 gives 32.00 − 3.93 = 28.07 = the 2026-08-14 minimum 28.07. The tiers coincide wherever T1 is positive (XF-7) → courtesy has no surviving method factor. |
| R-E2 | closed | — |
| R-E3a–e | closed | — |
| T0-1 | closed | rebuilt seed: balance 3850.06 < 3900.00 before the duplicate re-presentment; no purchase after 2026-05-31 |

### findings (revision_2)
Residual REDs: **R-C1r, R-D2r, R-D3r, R-E1r** (table above). New REDs:

**N1 SOURCE-FACTOR RED — catch-up factors gated through another factor's output (XF-1).** Rule "where the shortfall is nothing, the account is current and the catch-up payment is nothing"; compute `result = … if shortfall > 0 else 0`. over_limit_restoration, restoration_fee and cycle_since_miss contribute only through shortfall_measure's output. On task0 (after the settlement) substituting shortfall_measure's baseline gives 0.00 for the whole payment, not 319.49 − 135.50 = 183.99: the other three factors are switched off by it. Bears on task0.

**N2 SOURCE-POLICY RED — a definition shared by two factors lives inside one factor's sentence (XF-3/XF-4).** usage_line_addition T2 "5 percent of the account's net purchases over the last 12 months"; the only definition of net purchases is in purchase_volume_addition's sentence ("the account's net purchases over the last 12 months, being the purchases less the merchant credits and the dispute credits posted in that time"), and compute duplicates it in a second binding (`use_purchases_12`, unrounded, floored at 0) instead of one shared plain binding. The usage factor's document cannot state its own T2 quantity without reproducing another factor's ladder sentence. Bears on task0 structurally (task0 sits on T1).

**N3 SOURCE-POLICY RED — zero-amount courtesy leaves the refund wait unsatisfiable (XF-20).** fee_basis_correction T1: a qualifying late fee already reversed in full as billing_error → basis 0.00 → courtesy 0.00 (probe3: `qualifies=True`, `fee_basis=0.0`, result 0.0); the reversal tool rejects 0.00; the refund rule's wait ("every late fee that is the only late fee of the last 12 months on an account with no courtesy reversal in that time carries its courtesy reversal") still names that fee → the refund is never fixed. No de minimis carve-out in either sentence.

**N4 SOURCE-POLICY RED — the dispute-adjusted minimum departs from the base minimum formula.** Base card_evt_interest: the minimum is the percentage "of the new balance excluding disputed amounts". (a) A dispute received before the statement closed is already excluded from that statement's printed minimum; dup ("the minimum payment due printed on the statement that first showed the disputed posting", notice test only "on or before that statement's payment due date") and catch-up (round-1 test "received after its closing date" dropped — regression) take the percentage off a second time. (b) catch-up takes only "the most recent billing-error dispute" on the missed statement: probe3, disputes 900.00 (09-20) and 100.00 (09-25) → 1 % of 100.00 only, shortfall 114.50, where the base exclusion of both gives 105.50. (c) no same-day tie rule for that read: two disputes received 09-20 → shortfall 106.50 or 114.50 depending on entry order (probe3).

**N5 SOURCE-FACTOR RED — one clearing period split into two summed factors (XF-6).** Refund: "The most recent payment is held when its age is no more than every clearing period this rule sets, added together"; channel_clearing_days + risk_clearing_days feed one comparison. On task1 each factor's baseline substitution removes the whole 408.04 hold (693.49 both) and neither has an effect independent of the other's tier (7 + 0 = 7 < 11 and 3 + 7 = 10 < 11 days). Bears on task1.

**N6 SOURCE-FACTOR RED — refund dispute-hold second tier miscounts re-billed credits (realism).** "the hold is the smaller of two figures, each counted after taking off the provisional credits already re-billed, the provisional dispute credits posted and the amounts resolved for the merchant": a withdrawn dispute's re-bill (base: on withdrawal after a merchant credit "the provisional credit is reversed against the merchant credit") is subtracted from the merchant-resolved figure. probe3: merchant-resolved 186.40 not yet re-billed + withdrawn 50.00 re-billed → hold 136.40, while 186.40 of provisional credit is outstanding. No issuer holds less than the credit it may still re-bill. Bears on no task's scored value (task1 has an open dispute, first tier).

Observations carried: O-1, O-2, O-3 (reworker disputes; no consequence), O-8. New: O-9 line conduct "nothing" tier still lets membership/tenure/volume/usage additions raise the limit of an account with more than two late fees; O-10 residual interest hold applies the minimum interest charge (2.00) where the computed trailing interest is 1.23 (task1) — consistent with the base minimum-charge sentence, noted only.

### closing_checklist (revision_2)
Written after the round-2 reveals (2026-10-24T13:27Z). Both rebuilt tasks' gold equals the independent derivations figure for figure (task files). Not closed: residual R-C1r, R-D2r, R-D3r, R-E1r and new N1–N6 stand. Trees: task0 2 prerequisites / 2 value_input / owner=user payment; task1 1 / 1 / owner=user refund; acyclic. Every declared factor bears weight on its world and every whole baseline differs from gold, but N1, N5 and R-E1r strike factors structurally. Gates not re-run by this auditor (coordinator snapshot round 2 is the current form). No regression of a closed item found other than the catch-up's dropped "after its closing date" test, recorded as N4a.
Charter RED ids (revision_2): R-C1r, R-D2r, R-D3r, R-E1r, N1, N2, N3, N4, N5, N6.

VERDICT revision_2: task0=RED task1=RED charter=R-C1r,R-D2r,R-D3r,R-E1r,N1,N2,N3,N4,N5,N6

## revision_3

### charter_global_frozen (revision_3)
- freeze time: written between 2026-10-24T13:52:22Z (snapshot) and 13:56:33Z (reveal), before any round-3 GT was read.
- coordinator snapshot executed (`/tmp/erl0080_coord/snapshot.sh store_card_billing_and_disputes 3`, 2026-10-24T13:52:22Z): task0.view.json 726079d9…78ed and task1.view.json 5ecdd8cf…9889 (both unchanged from round 2 — the rework did not touch initial_state); card.extended.yaml 24dbff27…54d4 (changed); task_tools.py b95bcb32…e158 (unchanged); gates EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK.
- read: rework_claims_r3.md (ids/locations), the full extended section (base copy still byte-identical), `tail -1 worklog.md` ("REWORK round 3: gates 7/7 green"). Not read: plan.md; tasks/*.json until the reveal.
- re-derived in full (charter changed); action_binding_and_uuids carried forward (tool hash unchanged since revision_1).
- scratch: probe2r3.py (chains and every factor's baseline substitution), probe4.py (decoy / absent / second / same-day-tie probes on every changed read). Mechanical sweep: every compute_basis quote, policy_source, baseline.rule and replaced_by verbatim in its rule; every binding has a basis.

### status of revision_2 findings
| id | status | evidence (probe4 / probe2r3) |
|---|---|---|
| R-C1r | closed | "what the order record charged" = amount paid + refunds booked in the order history; split shipment 600 + 400 with a 100.00 return → charged 1000.00, `confirmed=False` |
| R-D2r | closed | scope requires no resolution entry: after task0's own settlement `confirmed=False`; withdrawn most recent duplicate → `confirmed=False`; catch-up sentence and condition carry the same open test |
| R-D3r | closed | line wait back to "minimum … met in full by the payments … that were not returned unpaid": 1.00 token payment → unmet 134.50; world W (paid in full 10-06, fee 10-08) → met, catch-up nothing, line granted; every catch-up shortfall tier ≥ the unmet part |
| R-E1r | closed | fee_basis_correction removed; loyalty_points (membership years capped at 10 / whole tens of 12-month rewards capped at 10 / none) has distinct inputs per tier; decoys (trial Annual, active Rewards, cancel_pending Monthly) fall to the rewards tier as the rule states |
| N1 | closed | gate is the plain record test cure_unmet; shortfall_measure's baseline now gives 183.99 on task0 |
| N2 | closed | usage low-use tier reads its own input (12-month payments net of returns) |
| N3 | closed | qualification and the refund wait both require ≥ 1.00 standing; standing 0.50 → not qualifying, refund wait excludes it |
| N4 | **partly closed** — (a) double exclusion in the dup fee tiers closed (notice must postdate the close); (b)/(c) closed for the dup by the single-dispute test; but see R3-1, R3-2, R3-3 |
| N5 | closed | one family factor clearing_period (30 / 14 / 10 / 3 days), ladder disjoint |
| N6 | closed | round-2 world (merchant-resolved 186.40 unbilled + withdrawn 50.00 re-billed) → hold 186.40 |

### findings (revision_3)
**R3-1 SOURCE-POLICY RED — the dup's fee overwrite leaves an erroneous fee uncorrected (XF-16/XF-17).** replaced_by: "For the late fee recorded for the statement that first showed the disputed posting of a dispute this rule settles, and only for that fee, the part charged in error or above the dispute-adjusted minimum is credited inside the duplicate-posting final credit … instead of being reversed as a fee". The new fee tiers credit it only when "the dispute being settled is the only billing-error dispute on a transaction that statement first showed, its notice was received after that statement's closing date"; otherwise "it is nothing". probe4: a second billing-error dispute (50.00) on the 2026-06-09 statement → `stmt_disputes=2`, carried fee 0, final credit 1389.69, although the 32.00 fee is still in error (payments 112.00 ≥ 115.37 − 14.13 − 0.50 = 100.74). The base reversal is retired for that very fee, so no rule corrects it; a reader applying the base reversal instead gets a second reading (1389.69 + a 32.00 billing_error reversal, for which no tool exists). Same gap for a notice received before the close.

**R3-2 SOURCE-POLICY RED — no same-day tie rule on the catch-up's most recent payment (XF-10).** "where none was returned and the most recent of them was mailed and credited no more than 10 days before today" — two payments against the missed statement credited the same day (60.00 mail, 50.00 online): entered mail-first → shortfall 85.50, catch-up 222.16; entered online-first → 25.50, 162.16 (probe4). The claim "tie rules stated for every most-recent read" misses this read.

**R3-3 SOURCE-POLICY RED — catch-up and line wait ignore a billing-error dispute received after the missed statement closed (base conflict; N4 residual).** Base card_billing_dispute: "while it is open the disputed amount is excluded from the minimum payment … no late fee arises from leaving it unpaid". Both rules now measure the printed minimum only ("The missed statement is met when its minimum payment due is met in full …"; line "the minimum payment due on the statement … is met in full"). probe4: dispute 2468.41 received 2026-09-15 on the 2026-09-09 statement (printed minimum 135.50, paid 110.00): rule → unmet 25.50, catch-up 162.16, line refused; base exclusion → minimum max(40, 135.50 − 24.68) = 110.82, short 0.82. Two readings.

**R3-4 SOURCE-FACTOR RED — unreal tiers in dispute_interest_exposure (realism).** (a) network-only tier: "on the network-only track it is that amount times the same daily rate, times the days from the posting date of the disputed transaction to today" — the network-only track runs "without those protections" (base card_billing_dispute), so the disputed amount was never excluded from interest; no interest is reinstated on it, and the pre-notice days were billed normally (probe4: 8.84 held on task1's dispute moved to network_only). (b) "follows the most recent dispute on the account": with a second, later open dispute (10.00 on 10-20) the exposure falls from 3.79 to 0.08 while the first dispute is still open and held in full by the dispute hold. No issuer holds the interest exposure of one open dispute and not another. Struck → refund keeps 3 factors (< 4).

**R3-5 SOURCE-POLICY RED — stale ladder text (XF-8).** settled_principal ladder T2: "the duplicate excess (the purchase postings carrying the order's reference less the amount paid on the order record)"; the rule now: "exceed what the order record charged, that is the order's amount paid plus the refunds its order history books". The factor face and the rule face state different tiers wherever an order carries a return or adjustment.

Observations: O-1, O-2, O-3, O-8 kept (reworker disputes). O-11 task0's order history (order_events) has no rows at all although the dup now reads it; refunds 0.00 is consistent with a fulfilled order with no returns, so no value consequence. O-12 the catch-up mailed-payment tier asks the cardholder to pay again an amount already credited by mail. O-13 open_dispute_hold second tier subtracts cardholder-resolved amounts that had no provisional credit (only after a product change from a no-provisional tier).

### factor_ladders (revision_3)
dup 5 (1 method); line 5 (1 method, usage distinct inputs ✓, conduct monotone ✓); catch-up 4 (2 methods; mailed tier distinct ✓); courtesy 6 (loyalty method, cross membership ✓; lateness/autopay/history/coverage/tenure parameters ✓); refund 4 (clearing_period family parameter ✓, open_dispute_hold ✓, residual_interest_hold method ✓, dispute_interest_exposure method — struck R3-4). XF-1 read-set check: no factor reads another factor's binding; the catch-up gate is the plain cure_unmet ✓. No factor id is a substring of a tool name ✓.

### erratum (revision_3)
The freeze-time stamps written in revision_2 (13:30Z, 13:33Z, 13:34Z) were mis-stated: those sections were written between 2026-10-24T13:23:51Z (the `date` taken just before writing) and 13:25:36Z (the round-2 reveal), i.e. before the reveal as required; the revision_2 text is otherwise left untouched. The revision_3 stamps were corrected in place to "before the 13:56:33Z reveal" before this erratum.

### closing_checklist (revision_3)
Written after the round-3 reveals. Both tasks' gold equals the derivations figure for figure. Trees: task0 2 prerequisites / 2 value_input / owner=user payment; task1 1 / 1 / owner=user refund; acyclic. Closed this round: R-C1r, R-D2r, R-D3r, R-E1r, N1, N2, N3, N5, N6 (N4 partly). Remaining charter REDs: R3-1, R3-2, R3-3, R3-4, R3-5 (R3-1 and R3-4 introduced by this round's rework of N4 and N5; R3-3 is the N4 residual). Gates not re-run by this auditor (coordinator snapshot round 3 is the current form).

VERDICT revision_3: task0=PASS task1=RED charter=R3-1,R3-2,R3-3,R3-4,R3-5

## revision_4

### charter_global_frozen (revision_4)
- written after the snapshot (2026-10-24T18:38:24Z) and before the round-4 reveal (time recorded in the task files); nothing below is derived from round-4 GT.
- snapshot executed (`/tmp/erl0080_coord/snapshot.sh store_card_billing_and_disputes 4`): task0.view.json 726079d9…78ed (unchanged), task1.view.json a1790926…3407 (changed: one Publix merchant credit added); card.extended.yaml f4bdc22b…5040 (changed); task_tools.py b95bcb32…e158 (unchanged); gates EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK.
- read: rework_claims_r4.md, the full extended section (diffed against my revision_3 extraction; base copy still byte-identical), `tail -1 worklog.md` ("REWORK round 4: gates 7/7 green"). Not read: plan.md, the worklog body the claims point to, tasks/*.json before the reveal.
- sweep: every compute_basis quote, policy_source, baseline.rule, replaced_by verbatim in its rule; every binding has a basis; every ladder `when`/value/method is a verbatim span of its rule except settled_principal T2's method ("the duplicate excess, the amount by which … exceed what the order record charged"), a faithful paraphrase of the rule's definition (O-17, no consequence).
- scratch: probe2r4.py (chains, every factor's baseline substitution), probe5.py (decoy / absent / second / same-day-tie probes on every changed read).

### status of revision_3 findings
| id | status | evidence |
|---|---|---|
| R3-1 | closed | replaced_by now retires the base fee reversal only "where the late fee carried by the error worked out below is above zero" and restates it in force otherwise; two-dispute world → carried fee 0, credit 1389.69, base reversal in force for the 32.00 fee. (No tool of this difficulty posts a billing_error reversal — O-16, no task world reaches it.) |
| R3-2 | closed | same-day tie stated for the catch-up's most recent payment; compute LATEST keeps the first-entered row |
| R3-3 | closed for one dispute | "The minimum payment due on the missed statement is the minimum printed on it, less the amount the base rule excludes …": one open dispute received after the close → 135.50 − 24.68 = 110.82 in both catch-up and line (probe5); resolved → printed 135.50; notice before the close → printed 135.50. The two-or-more case is R4-1. |
| R3-4 | closed | dispute_interest_exposure removed; replaced by merchant_credit_hold (see R4-2) |
| R3-5 | closed | ladders now verbatim spans (except O-17) |

### findings (revision_4)
**R4-1 SOURCE-POLICY RED — two or more disputes on the missed statement switch the catch-up off and lift the line wait (realism; base conflict).** Catch-up: "where two or more billing-error disputes are recorded on transactions the missed statement first showed, the statement is left to those disputes' investigation, this rule does not measure it and the catch-up payment is nothing"; line: "… the statement is left to those disputes' investigation and the increase does not wait on it". Base: "while it is open the disputed amount is excluded from the minimum payment" — only the disputed amounts are excluded; the rest of the minimum stays due and a late fee for missing it stands. probe5 on task0's world with two disputes of 10.00 and 12.00 on 2026-09-09 and the payment bounced: catch-up 0 (`cure_unmet=0`), line granted 5300.00, while 135.50 − 0.10 − 0.12 = 135.28 of the minimum is unpaid. No issuer cures a past-due statement, and grants a line increase on it, because two small disputes are open on it. (Introduced by the R3-3 rework.)

**R4-2 SOURCE-POLICY RED — holds that look only at the most recent item of their kind (realism; second record). Class listed exhaustively:**
- (a) merchant_credit_hold: "The merchant credit hold follows where the most recent merchant credit came from … it is held when its age is no more than 7 days". probe5: the 860.00 outside credit moved to 10-26 (4 days old, inside its 7-day window) with the 16.47 Publix credit on 10-27 → only 16.47 held; the 860.00 is refunded at once (263.56 instead of 0.00 after holds).
- (b) payment hold: "The most recent payment is held when its age is no more than the clearing period". With a payment returned in the last 12 months (30-day clearing), two payments credited 10-17 and 10-19 are both uncleared, but only the 10-19 one is held. Further, probe5: a second online payment (300.00 on 10-17, then 408.04 on 10-19) turns the 14-day first-use period into 3 days for the most recent payment, so neither is held (671.60), whereas one online payment alone is held for 14 days. This member has been in the charter since revision_2; I missed it in revisions 2 and 3 (it is the same class as R3-4(b), which I did flag).
No other hold or factor reads a single most-recent row where several rows of the kind can be inside the same window (dispute hold sums all disputes; residual interest reads the most recent statement, which is a single object by definition; courtesy reads the single courtesy fee).
merchant_credit_hold is struck structurally → refund keeps 3 factors (< 4).

Observations: O-1, O-2, O-3, O-8, O-11, O-12, O-13 as before (reworker disputes/keeps). New: O-14 the line rule restates the catch-up's missed-statement-minimum definition word for word (the wait needs a record-visible definition; no consequence). O-15 the Publix credit a9933333 reuses transaction_reference 27X28BLK6AWU of the 2019-05-23 Suncoast Pharmacy purchase (its original_transaction_reference 2KXNGHWK3UWE is correct; no value consequence). O-16 the base billing_error / regulatory_cap fee reversal that R3-1 restores has no tool in this difficulty. O-17 settled_principal T2 paraphrase.

### factor_ladders (revision_4)
dup 5 (1 m), line 5 (1 m), catch-up 4 (2 m), courtesy 6 (1 m, cross membership), refund 4 (clearing_period p, open_dispute_hold p, merchant_credit_hold p — struck R4-2a, residual_interest_hold m). Read-set check: no factor reads another factor's binding; the catch-up gate is the plain cure_unmet built on the plain m_min. merchant_credit_hold is a `parameter` (30 / 7 / no hold window) ✓. No factor id is a substring of a tool name.

### closing_checklist (revision_4)
Frozen sections written 2026-10-24T18:41:21Z, reveal 18:41:29Z. Both tasks' gold equals the derivations figure for figure. Trees unchanged (task0 2 prerequisites / 2 value_input / owner=user payment; task1 1 / 1 / owner=user refund); acyclic. Closed this round: R3-1, R3-2, R3-3 (one-dispute case), R3-4, R3-5. Remaining charter REDs: R4-1 (introduced by the R3-3 rework), R4-2 (a introduced by the R3-4 rework; b pre-existing since revision_2 and missed by me before). Gates not re-run by this auditor (coordinator snapshot round 4 is the current form).

VERDICT revision_4: task0=PASS task1=RED charter=R4-1,R4-2

## revision_5

### charter_global_frozen (revision_5)
- the round-5 request reached me at ~19:04Z and the run was cut by an account limit right after the snapshot; resumed from that breakpoint (files still ended at revision_4; nothing re-done that was already right). Written 2026-10-24T23:07Z, before the round-5 reveal; nothing below is derived from round-5 GT.
- snapshot executed (`/tmp/erl0080_coord/snapshot.sh store_card_billing_and_disputes 5`, 2026-10-24T19:04:30Z): task0.view.json 726079d9…78ed (unchanged), task1.view.json 472d6512…606a (changed: the Bayshore Grill credit replaces the Publix one, unreferenced, own reference); card.extended.yaml 1af18631…e7ac (re-hashed at resume: same); task_tools.py b95bcb32…e158 (unchanged); gates EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK.
- read: rework_claims_r5.md, the full extended section (diffed against my revision_4 extraction; base copy still byte-identical), `tail -1 worklog.md` ("REWORK round 5: gates 7/7 green"). Not read: plan.md, worklog body, tasks/*.json before the reveal.
- sweep: every compute_basis quote, policy_source, baseline.rule, replaced_by and every ladder text verbatim in its rule; every binding has a basis.
- scratch: probe2r5.py (chains + every factor's baseline substitution), probe6.py (decoy / absent / second / same-day probes on every changed read).

### status of revision_4 findings
| id | status | evidence |
|---|---|---|
| R4-1 | closed | the two-or-more case no longer lifts the line wait: line "… the increase is not granted: nothing is booked and the request awaits those disputes' investigation"; catch-up "the missed statement is referred to those disputes' investigation: no catch-up payment is booked". probe6, two open 10.00/12.00 disputes on 2026-09-09: catch-up 0, line 3900.00 (not granted). See R5-1 for the referral's record test. |
| R4-2 (a) | closed | merchant_credit_hold now sums every qualifying credit of the last month (returned payment in 12 months → every outside credit; otherwise every unreferenced outside credit); second unreferenced credit → 25.47 held. |
| R4-2 (b) | closed | payment_clearing sums every held payment of the last month: two first-use online payments → both held (748.04); two mailed → 110.00 + 408.04 + 40.00; a phone payment with prior phone use → not held; returned payment → every payment of the month less the returned one. |
| class sweep | closed | catch-up mailed tier sums the month's mailed payments (two mailed 50 + 40 → both left out, shortfall 135.50). No other single-most-recent hold remains (courtesy fee, latest statement and dup's most recent duplicate dispute are single objects by definition). |
| O-15, O-17 | closed | unique credit reference; settled_principal T2 verbatim |

### findings (revision_5)
**R5-1 SOURCE-POLICY RED — the referral's record test reaches past its own object.** Line and catch-up: "while that statement carries two or more billing-error disputes on transactions it first showed and a dispute still stands open on the account, the disputed amounts opened exceeding the amounts that have left dispute status …" / "… the catch-up payment is nothing until the investigation ends". The test is "a dispute still stands open on the account", not that one of the statement's disputes is still open. probe6 on task0's world: the two disputes on 2026-09-09 resolved on 10-01, the unrelated duplicate dispute fbef94b5 (first shown on 2026-06-09) still open → `referral=True`: catch-up 0 and the line refused, although "those disputes' investigation" has ended; the rule's own purpose clause ("until the investigation ends") reads the other way, and the base rule then measures the printed minimum (unmet 135.50 after the bounce). Two readings in a reachable world (open duplicate disputes are exactly this charter's subject).

**R5-2 SOURCE-POLICY RED — one record selection owned by two factors (XF-4).** "a payment was returned unpaid in the last 12 months" is stated as the first tier of both payment_clearing ("The payment clearing hold follows the account's payment record over the last 12 months …: where a payment was returned unpaid in the last 12 months …") and merchant_credit_hold ("… where a payment was returned unpaid in the last 12 months, every merchant credit …"), and computed twice (`pay_returns_12`, `mc_returns_12`) instead of once as a plain binding both read. No other selection is duplicated across factors of one policy (checked: conduct_percentage, history_points, usage_line_addition each read their own selections; dup's shared first_paid / correct_part and catch-up's days_since_due are plain bindings).

Observations: O-1, O-2, O-3, O-8, O-11, O-12, O-13, O-14, O-16 as before. New: O-18 the referral sentence is folded into the line's prerequisite sentence and edge condition, so part of that wait (the open disputes) is ended by dispute resolutions, one of which is the dup settlement — ordering still unique through catch-up → dup, no second terminal state shown. O-19 payment_clearing and merchant_credit_hold are labelled `parameter` though their tiers sum different record sets (the O-4 class). O-20 the unreferenced-credit test matches an empty reference string; a credit row lacking the field altogether would not count (seed convention stores '').

### factor_ladders (revision_5)
dup 5 (1 m), line 5 (1 m), catch-up 4 (2 m), courtesy 6 (1 m, cross membership), refund 4 (payment_clearing p, open_dispute_hold p, merchant_credit_hold p, residual_interest_hold m). All ladders ≥ 3 tiers, disjoint, verbatim in their rules; no factor reads another factor's binding; no factor id is a substring of a tool name. No factor is struck this round.

### closing_checklist (revision_5)
Frozen sections written 2026-10-24T23:07Z, reveal 23:07:25Z. Both tasks' gold equals the derivations figure for figure; both tasks PASS on all four relationships. Trees: task0 2 prerequisites / 2 value_input / owner=user payment; task1 1 / 1 / owner=user refund; acyclic; scopes disjoint and covering the five extended policies; uuid8s independent (tools unchanged since revision_1). Every computation declares a self-sufficient baseline and 4–6 factors, every factor bears weight on its world and every whole baseline differs from gold. The difficulty does not pass the source-layer audit yet: charter-global R5-1 (introduced by the R4-1 rework) and R5-2 (introduced by the R4-2 rework) stand. Gates not re-run by this auditor (coordinator snapshot round 5 is the current form).

VERDICT revision_5: task0=PASS task1=PASS charter=R5-1,R5-2

## revision_6

### charter_global_frozen (revision_6)
- written 2026-10-24T23:31Z, before the round-6 reveal; nothing below is derived from round-6 GT.
- snapshot executed (`/tmp/erl0080_coord/snapshot.sh store_card_billing_and_disputes 6`, 2026-10-24T23:30:17Z): task0.view.json 726079d9…78ed and task1.view.json 472d6512…606a (both unchanged from revision_5); card.extended.yaml 020883d2…f212 (changed); task_tools.py b95bcb32…e158 (unchanged); gates EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK.
- read: rework_claims_r6.md, the extended section (diffed against my revision_5 extraction: changes confined to the referral sentences/bindings of line and catch-up, and the refund's payment-record sentence, hold sentences, bindings and one effect label); `tail -1 worklog.md` ("REWORK round 6: gates 7/7 green"). Not read: plan.md, worklog body, tasks/*.json before the reveal.
- sweep: all quotes, policy_sources, baselines, replaced_by texts and ladder texts verbatim; every binding has a basis; no binding is owned by two factors.
- scratch: probe2r6.py (chains + sensitivities), probe7.py (referral decoy / second / same-day probes; refund shared-record probe).

### status of revision_5 findings
| id | status | evidence |
|---|---|---|
| R5-1 | closed for its world | referral now tests the missed statement's own most recent billing-error dispute ("the most recent of them … still stands open with no resolution entry referring back to it"); probe7, both statement disputes resolved and the unrelated duplicate dispute fbef94b5 still open → `referral=False` (catch-up 328.34, line measured normally). Second-record residual → R6-1. |
| R5-2 | closed | one plain sentence ("The account's payment record is clean when no payment was returned unpaid in the last 12 months") and one plain binding `returns_12`, read by both holds; no factor owns it. Returned-payment probe: payment hold 448.04 and merchant-credit hold 876.47 both on their first tiers. |
| O-20 | closed | "an unreferenced merchant credit is one whose purchase reference is empty" |
| O-19 | retracted (see R6-2) | |

### findings (revision_6)
**R6-1 SOURCE-POLICY RED — the referral ends while an older dispute on the statement is still open, and the minimum then ignores it (second record; base conflict; residual of R5-1 / R3-3).** The referral keys on "the most recent of them" only; the minimum sentence excludes a disputed amount only "where exactly one billing-error dispute is recorded on a transaction that statement first showed … in every other case the minimum payment due is the printed minimum". probe7: two disputes on 2026-09-09 — 1,000.00 (09-15, still open) and 12.00 (09-20, resolved 10-01): `referral=False`, minimum 135.50, catch-up shortfall 135.50 (272.16 in all), line wait unmet 135.50; base card_billing_dispute ("while it is open the disputed amount is excluded from the minimum payment") gives max(40, 135.50 − 10.00) = 125.50 for the still-open 1,000.00 dispute, and the referral's own clause ("until the investigation ends") says the investigation has not ended. Two readings. Mirror case (older resolved, latest open) → referral holds, consistent.

**R6-2 SOURCE-FACTOR RED — merchant_credit_hold relabelled `method` with a tier pair that XF-7 counts as one input.** T1 "every merchant credit posted in the last month by a merchant other than Northgate" (SUM amount_usd of card_post_credit, external, last month) and T2 "those unreferenced credits" (SUM of the same field over the same window, filtered to an empty reference): "Aggregates of the same field count as one input whatever their window/filter" — no distinguishing input for T1/T2, so the `method` label is dishonest. This follows my own O-19 (revision_5), which I retract: under XF-7 as I applied it to payment_clearing_hold in revision_1, the `parameter` label was the honest one. The refund still has an honest method (residual_interest_hold) and, with merchant_credit_hold counted as a parameter, 4 factors (3 parameter, 1 method) — no task's counts fall below the floors.

Observations: O-1, O-2, O-3, O-8, O-11, O-12, O-13, O-14, O-16, O-18 as before.

### closing_checklist (revision_6)
Frozen sections written 2026-10-24T23:31Z, reveal 23:31:34Z. Both tasks' gold equals the derivations figure for figure; both tasks PASS on all four relationships (trees, factor counts and weights as in revision_5). Closed this round: R5-1 (its world), R5-2, O-20. Remaining charter REDs: R6-1 (second-record residual of the referral / dispute-adjusted minimum), R6-2 (merchant_credit_hold `method` label, prompted by my retracted O-19). Gates not re-run by this auditor (coordinator snapshot round 6 is the current form).

VERDICT revision_6: task0=PASS task1=PASS charter=R6-1,R6-2

## revision_7

### charter_global_frozen (revision_7)
- written 2026-10-24T23:46Z, before the round-7 reveal; nothing below is derived from round-7 GT.
- snapshot executed (`/tmp/erl0080_coord/snapshot.sh store_card_billing_and_disputes 7`, 2026-10-24T23:45:44Z): both views unchanged (726079d9…78ed, 472d6512…606a); card.extended.yaml 32f4e896…3be4 (changed); task_tools.py b95bcb32…e158 (unchanged); gates EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK.
- read: rework_claims_r7.md, the extended section (diffed against my revision_6 extraction: changes confined to the referral sentences / `referral` bindings of line and catch-up, the line's policy_source and condition, and merchant_credit_hold's label and last tier text); `tail -1 worklog.md` ("REWORK round 7: gates 7/7 green"). Not read: plan.md, worklog body, tasks/*.json before the reveal.
- coordinator route for R6-1 accepted as given (coarse exact count: two or more billing-error disputes on the missed statement's own transactions, resolved or not → referred, nothing booked; exactly one keeps the base exclusion). This revision verifies compliance and does not re-open the route.
- sweep: all quotes, policy_sources, baselines, replaced_by and ladder texts verbatim; every binding has a basis.
- scratch: probe2r6.py (chains, unchanged figures), probe8.py (referral count probes).

### status of revision_6 findings
| id | status | evidence (probe8) |
|---|---|---|
| R6-1 | closed — complies with the coordinator's route | `referral = s_disp_n >= 2` in both line and catch-up, rule "whether resolved or not"; both disputes resolved → referral (catch-up 0, limit 3900.00 not raised); the round-6 world (older open, latest resolved) → referral; exactly one open dispute after the close → minimum 125.50 (base exclusion); exactly one resolved → 135.50; exactly one received before the close → 135.50; a network-only dispute is not counted (one billing-error + one network-only → no referral, 125.50). |
| R6-2 | closed | merchant_credit_hold labelled `parameter` again; last tier "0". |

### findings (revision_7)
**R7-1 SOURCE-POLICY RED — the depended-on rule restates the blocked rule's prerequisite sentence and names the other problem (check 6).** The line's policy_source is now two sentences, the second being "While the missed statement carries two or more billing-error disputes on transactions it first showed, whether resolved or not, the catch-up payment and a requested credit line increase are referred to the disputes team: nothing is booked and the customer is handed over to a human representative because no published policy resolves the request in this conversation." The same sentence, verbatim, is in the catch-up's rule (the depended-on policy). Check 6: "the depended-on policy's rule does not restate the sentence", and a rule names no other problem's route — the catch-up rule now states the outcome of "a requested credit line increase". The route itself (coarse count → referral) is not in question; only its placement: each rule can state its own referral without the other's. Bears on no task's values (no world has two disputes on its missed statement); it is a rendering-surface defect for task0's chain (the catch-up hub would carry the line increase's referral).

Observations: O-1, O-2, O-3, O-8, O-11, O-12, O-13, O-14, O-16, O-18 as before. New: O-21 the referral is a hand-over to a human representative (a scored write in the runtime); the line's edge condition now carries a route clause ("the request is referred and nothing is booked") that no write of this difficulty resolves — consistent with the coordinator's route, no task world reaches it.

### closing_checklist (revision_7)
Frozen sections written 2026-10-24T23:46Z, reveal 23:46:43Z. Both tasks' gold equals the derivations figure for figure; both tasks PASS on all four relationships. Closed this round: R6-1 (per the coordinator's route), R6-2. Remaining charter RED: R7-1 (the referral sentence of the line's prerequisite is restated verbatim in the depended-on catch-up rule, naming the line increase). Gates not re-run by this auditor (coordinator snapshot round 7 is the current form).

VERDICT revision_7: task0=PASS task1=PASS charter=R7-1

## revision_8

### charter_global_frozen (revision_8)
- written 2026-10-24T23:57Z, before the round-8 reveal; nothing below is derived from round-8 GT.
- snapshot executed (`/tmp/erl0080_coord/snapshot.sh store_card_billing_and_disputes 8`, 2026-10-24T23:57:04Z): both views unchanged (726079d9…78ed, 472d6512…606a); card.extended.yaml b7c2a711…cc22 (changed); task_tools.py b95bcb32…e158 (unchanged); gates EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK.
- read: rework_claims_r8.md, the extended section (diffed against my revision_7 extraction: changes confined to the two referral sentences and the line's policy_source / condition; compute unchanged); `tail -1 worklog.md` ("REWORK round 8: gates 7/7 green"). Not read: plan.md, worklog body, tasks/*.json before the reveal.
- sweep: all quotes, policy_sources, baselines, replaced_by and ladder texts verbatim; every binding has a basis; the line's policy_source is no longer in the catch-up rule; the catch-up rule names no other problem's outcome (its only cross-problem mention is its own waiting sentence on the duplicate dispute's final credit; "credit balance refunds" there is the base ledger term in the amount-owed sentence); the refund rule names the courtesy reversal only in its own waiting sentence.
- probes (probe8, compute unchanged): referral on two or more billing-error disputes on the missed statement, resolved or not (both resolved; older open / latest resolved) → catch-up 0, limit not raised; exactly one open after the close → 125.50; one resolved or received before the close → 135.50; network-only not counted. Chains (probe2r6) unchanged.

### status of revision_7 findings
| id | status | evidence |
|---|---|---|
| R7-1 | closed | line: waiting sentence alone as policy_source; its own referral sentence ("A requested credit line increase is not granted, and is referred to the disputes team, while the statement for which the most recent late fee was recorded carries two or more billing-error disputes …: no limit change is booked …"); catch-up: its own referral sentence for the catch-up payment only. Neither rule restates the other's sentence. |
| O-21 | closed | route clause removed from the line's edge condition |

### findings (revision_8)
None. Observations carried (no RED): O-1, O-2, O-3, O-8 (reworker disputes), O-11, O-12, O-13, O-14, O-16, O-18.

### closing_checklist (revision_8)
Frozen sections written 2026-10-24T23:57Z, reveal 23:57:40Z.
- Audit files task0.md / task1.md / _difficulty.md correspond one-to-one with the tasks; revisions 1–8 are appended in order, older text untouched (errata recorded in revision_3); every comparison section of this revision carries a PASS.
- The five extended policies are covered; scopes task0 {dup, catch-up, line} and task1 {courtesy, refund} are disjoint; task tools and GT closed; uuid8s independent and unchanged since revision_1.
- Trees: task0 2 prerequisite problems / 2 value_input edges / owner=user payment; task1 1 / 1 / owner=user refund; the difficulty's prerequisite graph is acyclic.
- Every computation declares a self-sufficient baseline and 4–6 factors (dup 5, line 5, catch-up 4, courtesy 6, refund 4; ≥ 2 parameter and ≥ 1 method each; multi-source and cross-difficulty factors present in both tasks); ladders ≥ 3 tiers, verbatim in their rules, distinct in outcome; every factor bears weight on its task world against an honest baseline and every whole baseline differs from gold.
- Gates: this auditor did not re-run them; the coordinator's round-8 snapshot (all 7 OK on the final form) is cited above.
All four relationships PASS for both tasks and no charter-global RED remains.

VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN

## revision_9

### charter_global_frozen (revision_9)
- written 2026-10-25T00:17Z, before the round-9 reveal; nothing below is derived from round-9 GT.
- snapshot executed (`/tmp/erl0080_coord/snapshot.sh store_card_billing_and_disputes 9`, 2026-10-25T00:16:27Z): both views unchanged (726079d9…78ed, 472d6512…606a); card.extended.yaml 1dc5ae2b…fe0d (changed); task_tools.py b95bcb32…e158 (unchanged); gates EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK.
- read: rework_claims_r9.md, the renderer's STOP audits/render_source/store_card_billing_and_disputes/render_r1.md (M1–M4, P1–P3), the extended section (diffed against my revision_8 extraction: changes confined to floor / rounding words in seven rule sentences and to factor binding lists; compute unchanged), `tail -1 worklog.md` ("REWORK round 9: gates 7/7 green"). Not read: plan.md, worklog body, tasks/*.json before the reveal.
- **Own miss recorded:** M1–M4 (rule words lacking a floor or a rounding that compute applies) and P1–P3 (plain bindings used by one factor only, XF-3) were present when I wrote `charter=CLEAN` in revision_8 and had been through several of my rounds; my revision_8 sweep checked quotation, ladder and binding coverage but did not test each floor / cap / rounding operation in compute against the words of its basis sentence, and my placement check did not run mechanically. Both checks are now run exhaustively below.

### exhaustive sweeps (revision_9)
**Floor / cap / rounding vs rule words (the M class).** Every compute binding containing MX(0,…), MX(floor,…), MN(cap,…), RND(…) or int(…) was listed with its basis sentence:
- now stated in words: dup dup_excess, correct_part, standing_fee ("never less than zero"), carried_interest, adj_min, reinstated (rounding, floor, "no days when the notice came after that closing date"), result; line m_min ("never more than the printed minimum", floor), use_add (both tiers "rounded half up to the cent", low-use tier "that difference never less than zero"), result ("rounded down to a whole hundred dollars and never above the tier's highest credit limit"); catch-up m_min, shortfall, standing_fee, window_fees ("never less than zero"), result; courtesy standing ("never less than zero"), loyalty_pts ("whole years … at most 10", "whole tens … at most 10"), share ("never above 100 percent"), result; refund credit_bal ("nothing when the account owes money"), payment_hold not-clean tier ("never less than zero"), dispute_hold, residual_hold ("never below the tier's minimum interest charge"; the empty day range from "the day after its closing date to the day before the most recent payment" is none), result.
- RND only as cent clean-up of sums and differences of cent amounts (no reading changes): dup order_charged, principal, carried_fee; line cure_unmet, net_purchases; catch-up cure_unmet, owed_net, over_add.
No member remains. M1 (window_fees), M2 (payment_hold), M3 (use_add low-use floor), M4 (use_add cent rounding) and the reworker's class sweep (three standing-fee sentences) are closed.

**Single-factor plain bindings and cross-factor reads (the P class, XF-1/XF-3).** Mechanical read-set check over every policy: no plain binding is consumed by exactly one factor and nothing else, and no factor binding is read by another factor. P1 (post_date, carried_interest → carried_error_days), P2 (fee_due → lateness_points, fee_paid → coverage_points), P3 (latest_stmt, latest_paid → residual_interest_hold) are closed. carried_interest inside carried_error_days still multiplies the plain shared dup_excess; the factor's baseline (carried_days 0) gives 0.00, so the sensitivity is unchanged (1403.13).

**Other sweeps.** All compute_basis quotes, policy_sources, replaced_by, baselines and ladder texts verbatim; every binding has a basis; base copy byte-identical. Chains and every factor's baseline substitution (probe2r6) unchanged on both worlds.

### status of revision_8 state and renderer items
| id | status |
|---|---|
| R7-1, O-21 (revision_8) | still closed (referral sentences unchanged) |
| M1, M2, M3, M4 | closed (words now match compute) |
| P1, P2, P3 | closed (bindings moved into their factors) |

### findings (revision_9)
None. Observations carried (no RED): O-1, O-2, O-3, O-8, O-11, O-12, O-13, O-14, O-16, O-18.

### closing_checklist (revision_9)
Frozen sections written 2026-10-25T00:17Z, reveal 00:17:54Z. Both tasks' gold equals the derivations figure for figure; both PASS on all four relationships. Coverage, scopes, uuid8s, trees and factor structure as in the revision_8 checklist, now with the floor/rounding words and the single-factor placements swept exhaustively (above). Gates: the coordinator's round-9 snapshot (all 7 OK on the final form) is cited; not re-run by this auditor. No charter-global RED remains.

VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN
