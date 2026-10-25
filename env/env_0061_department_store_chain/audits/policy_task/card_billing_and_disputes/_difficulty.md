# Policy-task audit — card_billing_and_disputes / charter-global

## charter_global_frozen
- Frozen: 2026-10-13T15:58Z, auditor: erl-task-policy-audit (independent auditor agent; did not author these artifacts).
- Inputs and hashes (sha256[:16], verified on disk before reading):
  - `tasks/card_billing_and_disputes/card.extended.yaml` 5d75237e58a8c743
  - `tasks/card_billing_and_disputes/task_tools.py` 7c5d54c3038bc53a
  - `blueprint/products/card.yaml`, `blueprint/blueprint.yaml`, `blueprint/db_schema.json`, `blueprint/share_tools.py`; `blueprint/products/loyalty.yaml` and `order.yaml` only for tier names / refund trigger fields.
  - DSL semantics: `skills/erl-task-instantiate/scripts/check_compute.py` (MONTHS, DAYS, `_within`, LATEST, RND).
- Permitted: the four items above. Masked/unread at the time this section was written: every field of `tasks/card_billing_and_disputes/tasks/*.json` other than the masked views' `frozen_time`, `user_scenario`, `initial_state`; no other audit, no other scenario, no sibling difficulty directory. This section contains nothing derived from any revealed GT.
- Entry conditions (Step 0): gate snapshot supplied in the brief (all green except the expected pre-render traceability / validate_scenario KB misses); masked views supplied with hashes 0.json 20a39f6cc083f431, 1.json 7dd07605ed856bee (verified). Complete.
- Base copy: lines 1-1517 of the extended file are byte-identical to `blueprint/products/card.yaml` (diff shows only the trailing blank line + `# ---- extended policies ----` comment).

Abbreviations: CLR = `card_ext_credit_line_review`, DPN = `card_ext_double_posting_notice`, MCN = `card_ext_missing_credit_notice`, CUP = `card_ext_catch_up_payment`, CC = `card_ext_courtesy_credit`.

### policy_conflict_scan
| Policy | subject | computes | target_tool (owner) | base_policy_refs | overwrite |
|---|---|---|---|---|---|
| CLR | card_credit_limit_change | new_credit_limit | raise_credit_line_b8050b6c (agent) | card_agg_combined_credit_line, card_credit_line_increase | [] |
| DPN | card_dispute_filed | disputed_amount | file_double_posting_notice_03ed3b71 (user) | card_billing_dispute | [] |
| MCN | card_dispute_filed | disputed_amount | file_missing_credit_notice_85b33449 (user) | card_billing_dispute | [] |
| CUP | card_payment | amount | take_phone_payment_161e7e24 (agent) | card_evt_payment_crediting | [] |
| CC | card_fee_reversal | amount | grant_courtesy_credit_38b9fa68 (agent) | card_courtesy_fee_waiver, card_account_closure | 2 entries |

- Overlapping subjects: DPN and MCN both write `card_dispute_filed`, but with disjoint `dispute_reason` (duplicate_charge vs credit_not_posted, fixed in the tool bodies) and disjoint objects (outside-merchant twin posting vs a refunded M&F purchase posting). No conflict.
- Triggers / eligibility / time anchors: all five are `on_request`; base eligibility inherited (dispute notice window 60 days from the first statement on which the disputed transaction appeared; no other open dispute on the transaction; CLI tests; courtesy allowance and 6-statement streak). No extended rule weakens a base gate.
- Shared quantity "amount under open billing dispute": CLR, CUP and CC each define it identically ("disputed amounts of the account's dispute filings less those of its resolutions and withdrawals"); consistent with base `card_billing_dispute` ("A dispute is open from its card_dispute_filed row until a card_dispute_resolved or card_dispute_withdrawn row").
- Cross-category read boundaries: CLR and CC read loyalty `variant_name/status` (branch); MCN reads order `order_events` + `purchases.order_number`. Tier names used (Finch Circle Silver/Gold/Platinum/Diamond/Icon) exist in `products/loyalty.yaml`; `order_refund.refund_tender_type = mf_card` exists in `products/order.yaml` (trigger to `card:card_merchandise_credit`).
- Terminal states: each policy writes one row/field; no two policies write the same field of the same row.
- Scope exclusivity of the M=2 tasks (from the prerequisite graph + the masked views' worlds): task 0 tree {CLR, DPN}; task 1 tree {CC, CUP, MCN}. Pairwise disjoint and jointly complete over the 5 extended policies.
- Blueprint claim lists event types no extended policy targets (card_dispute_withdrawn, card_fee, card_autopay_change, card_reissue, card_closure, card_credit_balance_refund) — observation O7 only.

### rule_compute_equivalence
Swept every compute binding against `compute_basis` and back against the `rule`.

- CLR: all bindings quote the rule; measured_balance / utilization / util_share / relationship_share / late_share / recency_share / increase_pct / raised_line / result match their sentences (multiplication "all at once and before it is applied", MN cap at max_credit_line_usd, `int(raised/100)*100` = "rounded down to a whole multiple of line_increment"). Two observations: (a) the base sizing cap "within card_agg_combined_credit_line" (inherited by "meets every test of the base credit line rule") has no compute binding — O2; (b) `within_months=N` in the DSL is a rolling window `0 <= MONTHS(d, NOW) < N`, while the rule says "in the last N full calendar months" — O1.
- DPN: **F1** — `twin_merchant`/`twin_date` filter `merchant_category='other_merchant'`, a basis the rule does not state. The rule says "a purchase from a merchant other than Marlowe & Finch" and "the outside-merchant purchase posting most recently posted to the account"; in this charter "outside-merchant" covers every non-M&F category (base `card_purchase` trigger `card_outside_spend` when merchant_category in [supermarket, gas_station, other_merchant]; `card_promo_financing` "outside-merchant purchases never qualify"; `card_welcome_discount` "does not apply to outside-merchant purchases"). Every other DPN binding matches its sentence (err_amt three-way selection incl. the equal-amount case, related_fee, int_base, billed_int thresholds incl. "less that statement's promotional balance", unbilled_int span and the "no payment after the latest statement date" case).
- MCN: all bindings match (credit_owed three tiers, mc_billed incl. `0 <= refund_lead_days <= proration_days`, mc_unbilled spans). XLATEST scoping is per customer, the rule says "to the card"; equivalent while the customer holds one card (both worlds) — no finding.
- CUP: all bindings match; cu_min_basis reproduces the base statement formula on the reduced balance (base: full balance when at/below floor, else max(floor, pct + interest/fees), + past_due); cu_int_fees = interest + fees − fee reversals of the latest statement_period (same as base `card_msr_cycle_interest_and_fees`); cu_counted/cu_addback implement "most recent payment credited after the missed due date".
- CC: all bindings match; `ct_late_others` subtracts the fee being reversed unconditionally (the rule's "other than the fee being reversed"; the fee being reversed is always the most recent late fee, so it is inside a 12-month rolling window whenever the courtesy rule can apply).
- Rounding: RND is Python `round` (binary float, ties-to-even), the rule says "rounded half up". No value in either world sits on a half-cent tie (checked per task) — no finding.
- Every factor ladder tier is a sentence of its `rule` and a branch of its `decides` binding, and vice versa (checked for all 24 factors).

### action_binding_and_uuids
- Each `(target_tool, computes)` is claimed by exactly one policy; base policies claim no task tool.
- Tool bodies: none refuses, errors or hints on an unresolved prerequisite (no branch on dispute/payment state in any of the five functions). Writes: raise_credit_line updates credit_limit, last_credit_limit_change_date and **status** (O10); the two notice tools create one `card_dispute_filed` row each (reason hard-coded); take_phone_payment creates one `card_payment` (phone_agent, period = next closing) and lowers current_balance; grant_courtesy_credit creates one `card_fee_reversal` (courtesy_waiver, fee_type late_fee) and lowers current_balance.
- Docstrings: no other tool named, no sequence/ordering word about actions ("before and after" / "first statement" / "after the payment" describe values, not action order), no concrete example value (no figure besides format specs "2 decimal places", "YYYY-MM").
- uuid8s: b8050b6c, 03ed3b71, 85b33449, 161e7e24, 38b9fa68 — pairwise distinct, no common prefix/suffix, no sequential pattern. Uniqueness against other difficulties' modules not checked (read isolation) — O9.
- Share tools (`blueprint/share_tools.py`) are finders + verify_customer_identity + transfer_to_human_agent; none writes card_disputes or card_transactions, so each state-form edge below has a single writer.

### prerequisite_graph
| Edge | blocked | problem | kind / gate | form | resolved_by = depended target_tool | gate binding exists |
|---|---|---|---|---|---|---|
| E1 | CLR | DPN | value_input / open_disputed | state | file_double_posting_notice_03ed3b71 ✓ | ✓ (CLR compute) |
| E2 | CUP | MCN | value_input / cu_open_disputed | state | file_missing_credit_notice_85b33449 ✓ | ✓ |
| E3 | CC | CUP | value_input / ct_cured | state | take_phone_payment_161e7e24 ✓ | ✓ (also feeds ct_cure_days via ct_pay_date) |
| E4 | CC | MCN | value_input / ct_open_disputed | state | file_missing_credit_notice_85b33449 ✓ | ✓ |

- `prerequisite` filled on all 5 (DPN, MCN: `[]`); every `problem` is an extended id of this file, none is a base policy or self; graph acyclic (MCN → CUP → CC, MCN → CC; DPN → CLR).
- Every `policy_source` is verbatim the last sentence(s) of the blocked policy's own rule (CLR rule l.1575-1576; CUP l.2125-2126; CC l.2365-2368). No `fallback_reason` needed (all state form). No authoring-viewpoint phrasing.
- `condition` vs sentence: E1 and E3 match. **E2 and E4 do not** — see F3.

### prerequisite_sentences
- E1 "The new credit line is worked out only after every purchase that posted to the account twice carries an open duplicate-charge dispute on the posting in error." — connective "only after"; waited-on state record-visible (card_disputes filing, reason duplicate charge, on the posting in error, not resolved/withdrawn); no tool/id/snake_case. Single writer: the only tool creating a duplicate_charge filing. Derivation: state → the policy whose rule describes a notice that a purchase "posted to the account twice" and defines "the posting in error" (DPN) → its target tool. One reading.
- E2 "The catch-up amount is not set until each Marlowe & Finch refund to the card that lacks its full card credit is under an open credit-not-posted dispute." — "not … until"; state form; single writer (credit_not_posted is written only by the MCN tool). Derivation → MCN ("notice that a Marlowe & Finch refund settled to the card has not been credited").
- E3 "The courtesy credit is not granted until the most recent payment credited after the missed payment due date stands unreturned at no less than the minimum payment due that was missed." — "not … until"; state form; single writer in the difficulty (take_phone_payment). Derivation → CUP ("pays by phone to bring the account current"). The CC rule states the same test twice more (overwrite replaced_by "the payment test is met when …" and "there is no courtesy credit while the payment test is not met") — same strength, same scope, no second reading — O6.
- E4 "The courtesy credit is worked out only after every Marlowe & Finch refund settled to the card without its full card credit carries an open credit-not-posted dispute on the refunded purchase." — "only after"; state form; single writer; derivation → MCN.
- No depended-on rule restates any of these sentences (DPN/MCN/CUP rules checked). No base rule sentence states a cross-problem order that a tree rests on.
- Scope of sentence vs depended-on rule: E1/E2/E4 sentences are universal ("every purchase that posted twice", "each … refund … that lacks its full card credit"), while DPN and MCN each resolve exactly one object ("the outside-merchant purchase posting most recently posted", "the most recent Marlowe & Finch refund record settled to the card"). See F3.

### override_declarations
- CLR vs `card_credit_line_increase`: "The new credit line is at most the current credit line plus cli_max_increase_pct percent of it, at most the card's max_credit_line_usd, and within card_agg_combined_credit_line; it is rounded down to a multiple of cli_min_increment_usd." — followed (extended picks a value under the ceiling; increment 100 = 100). All eligibility sentences (active, 6 months open, 6 months since change, streak 6, decline on failure) inherited. `card_agg_combined_credit_line` — inherited, not implemented in compute (O2). No undeclared override.
- DPN / MCN vs `card_billing_dispute`: window, no-open-dispute dedup, ack/resolution timing, provisional credit, rebill, return/delivery tests — followed. Base fixes no formula for `disputed_amount`; extended's "amount in dispute … together with the finance and other charges related to it" is compatible. No override.
- CUP vs `card_evt_payment_crediting`: crediting date, cut-off, channels, application order, "a payment never needs to be applied to an amount under open billing dispute" (quoted and used) — followed. No override.
- CC vs `card_courtesy_fee_waiver`: two declared overrides — (1) "A reversal always equals the full amount … partial reversals are not made." → partial courtesy credit, scoped to courtesy reversals of this policy; (2) "and payments credited since the missed due date add up to at least the missed minimum payment due." → most recent unreturned payment ≥ missed minimum. Remaining sentences (allowance below courtesy_late_fee_waivers_per_12_months, streak from the statement before the missed one, only late fees, assessed_in_error in full, not reversed before) inherited. Merged semantics unique. The event-field line `card_fee_reversal.amount: "… equal to the fee reversed."` (events section, not a sentence of a cited base policy) is left undeclared — O5.
- CC vs `card_account_closure`: annual-fee refund in full — preserved verbatim in the replaced_by. No conflict.
- Disguised forms (anonymous intermediate, 0/1 multiplier, dropped branch): none found; CC's `result = … if ct_cured else 0` is the base payment-test gate as overridden, declared.

### factor_ladders
| Policy | factor | label | decides | tiers | multi-source tier | cross_difficulty |
|---|---|---|---|---|---|---|
| CLR | balance_measure | method | measured_balance | 3 | t1 promo + statement count; t2 statements + payments | – |
| CLR | utilization_share | parameter | util_share | 3 | t1/t2 statements(or balance) + disputes + credit line | – |
| CLR | relationship_share | parameter | relationship_share | 3 | loyalty tier AND card M&F spend | loyalty |
| CLR | late_history_share | parameter | late_share | 3 | fees − reversals | – |
| CLR | recency_share | parameter | recency_share | 3 | date only | – |
| DPN | twin_selection | method | err_amt | 3 | – | – |
| DPN | conversion_fee_tie | parameter | related_fee | 3 | t2 fee rows on both twins | – |
| DPN | interest_base_pick | parameter | int_base | 3 | – | – |
| DPN | billed_interest_part | method | billed_int | 3 | payments + statements | – |
| DPN | unbilled_accrual_span | method | unbilled_int | 3 | payment + statement | – |
| MCN | owed_comparison | parameter | credit_owed | 3 | order refund + card credits / card purchases | order |
| MCN | missing_credit_interest_base | parameter | mc_int_base | 3 | – | – |
| MCN | missing_credit_proration | method | mc_billed | 3 | order refund date + statement | order |
| MCN | missing_credit_accrual | method | mc_unbilled | 3 | interest row + order refund date | – |
| CUP | coverage_follow | method | cu_coverage | 3 | statements + date | – |
| CUP | dispute_relief_basis | method | cu_min_basis | 3 | disputes + statement + interest/fees | – |
| CUP | promo_paydown_addon | parameter | cu_promo_add | 3 | statement promo + promo purchase date | – |
| CUP | returned_payment_addback | parameter | cu_addback | 3 | payment-returned + fee rows | – |
| CC | tenure_share | parameter | ct_tenure_share | 3 | – | – |
| CC | courtesy_relationship_bonus | parameter | ct_rel_bonus | 3 | loyalty tier AND card M&F spend | loyalty |
| CC | dispute_allowance | parameter | ct_err_bonus | 3 | disputes vs missed statement | – |
| CC | cure_speed | method | ct_cure_adj | 3 | payment + statement due date | – |
| CC | lateness_record | parameter | ct_hist_adj | 3 | fees − reversals | – |
| CC | prior_courtesy | parameter | ct_waiver_adj | 3 | – | – |

- Counts as declared: CLR 5 (4p/1m), DPN 5 (2p/3m), MCN 4 (2p/2m), CUP 4 (2p/2m), CC 6 (5p/1m). Bindings disjoint within each policy; no `decides` is `result`.
- Each ladder has three tiers, pairwise disjoint as stated, every tier stated in the rule (condition + value/method) and implemented in compute; no two tiers of one ladder select the same value or method (CLR shares 0.4/0.75/1.0, 0.5/0.75/1.0 [rel_top_share 1.0 = full_share but distinct from the other two tiers of its own ladder], 0.5/0.8/1.0, 0.6/0.8/1.0; CC 0.6/0.5/0.4, 0.15/0.08/0, 0.3/0.15/0, sliding/−0.1/0, −0.3/−0.15/0, −0.25/−0.1/0).
- Every fall-through equals the policy baseline for that input (CLR standard_share and full_share multipliers; DPN later-posted / 0; MCN refund amount / 0; CUP missed minimum / 0; CC standard_share / 0). Nested fall-throughs (DPN billed_interest_part, MCN missing_credit_proration, CUP dispute_relief_basis) are formulas that evaluate to the baseline value when their parent factor is at its own baseline (int_base = 0, coverage = missed minimum) — consistent.
- Each policy `baseline.rule` is verbatim rule text and self-sufficient: CLR (standard_share × cli_max, cap, round down), DPN (later-posted twin amount), MCN (refund amount), CUP (missed minimum less most recent payment after the missed due date, floored at 0), CC (fee × standard_share, nil while the payment test is unmet).
- Realism of conditions and outcomes (department-store card program, FCBA/Reg Z): CLR ladders (utilization, late history, months since last line change, loyalty relationship) are standard CLI sizing inputs; MCN (credit owed capped at amount charged — base `card_evt_merchandise_credit`; interest prorated by days the credit was missing) and CUP (bring-current amount following the newest statement; disputed amount excluded from the minimum — base; returned payment added back; deferred-interest pay-down) are real practice; CC tenure / relationship / cure speed / lateness / prior courtesy are real goodwill inputs; DPN twin selection (FX re-presentment vs auth/capture) and interest-base / billed-interest tier 1 (lost grace because the error was left unpaid, promo balance excluded per Reg Z deferred-interest grace) are real. **F2**: DPN `conversion_fee_tie` tier 2 is not. Weak-realism observations O3 (DPN billed_interest_part tier 2/3 "at least half" threshold; DPN unbilled_accrual_span tier 3 "no payment → no accrual").
- Label honesty: method factors genuinely change the algorithm. Two parameter factors have tiers that differ by formula rather than by a number — DPN `conversion_fee_tie` (posted fee vs pct × posting vs 0) and CUP `promo_paydown_addon` (whole balance vs balance ÷ months vs 0) — O4.

### findings
**F1 — SOURCE-POLICY RED (check 2, rule/compute non-equivalence). Bears on task 0.**
- Symptom: DPN's compute selects the twin postings among `merchant_category='other_merchant'` only; the rule selects among all outside-merchant postings.
- Root cause: compute filter with no rule basis.
- Evidence: rule (extended l.1740-1743) "A cardmember who gives notice that a purchase from a merchant other than Marlowe & Finch posted to the account twice … The notice concerns the outside-merchant purchase posting most recently posted to the account and the other purchase posting from the same merchant with the same transaction date"; compute l.1778-1779 `LATEST(… event_type='card_purchase', merchant_category='other_merchant')`; charter usage of "outside-merchant" = all non-M&F (base `card_purchase.triggers` `card_outside_spend` when [supermarket, gas_station, other_merchant]; `card_promo_financing`; `card_welcome_discount`).
- Demonstrated consequence: see `0.md` — in task 0's world the rule's object is a gas-station posting with no twin (no definite amount), the compute's is the Casa Lusitana pair.
- Affected: `card.extended.yaml` DPN rule l.1742-1743 / compute `twin_merchant`, `twin_date`.

**F2 — SOURCE-FACTOR RED (unreal ladder tier → factor count). Bears on task 0.**
- Symptom: DPN `conversion_fee_tie` tier 2 adds to the amount in dispute a conversion fee that was never assessed on the posting in error.
- Evidence: rule l.1750-1753 "when none has posted against the posting in error but one has posted against the other twin posting, the related conversion fee is the card's foreign_transaction_fee_pct percent of the posting in error"; factor l.1858-1859.
- Why unreal: under FCBA / Reg Z §1026.13(e) the creditor credits the erroneous amount and the finance or other charges *imposed* as a result of it. A fee posted only against the other (valid) twin belongs to that valid purchase; no fee resulted from the error, so no issuer states as a related charge — or would credit — a fee it never charged. The tier is a treatment no card issuer would publish.
- Consequence: struck from the count, DPN keeps 4 factors with only 1 `parameter` (interest_base_pick) against the floor of 2. Task 0's world sits on tier 1 (fee 15.38 posted on the posting in error), so the scored number is unaffected; the defect is in the ladder's structure.
- Affected: `card.extended.yaml` DPN rule l.1750-1753, factor `conversion_fee_tie`.

**F3 — SOURCE-POLICY RED (checks 6/7, sentence vs condition and vs depended-on rule). Bears on task 1 (E2, E4); no consequence in task 1's world.**
- Symptom: the E2/E4 sentences require a dispute on *each/every* M&F refund lacking its full card credit; the E2/E4 `condition` fields require it only for "the most recent Marlowe & Finch refund record settled to the card whose card credits total less than the refund"; and MCN's rule can only produce a dispute for "the most recent Marlowe & Finch refund record settled to the card" (whether or not that one is under-credited).
- Demonstration (constructed situation, same charter): refund R1 (older) credited 250 of 612.40, refund R2 (newer) credited in full. Sentence: the gate is unmet until R1 carries an open credit-not-posted dispute. Condition ("most recent … whose credits total less") also points to R1, but MCN's rule names R2 (the most recent refund record) and gives credit owed = R2's full amount (tier 3) on a fully credited refund, so no MCN write ever satisfies the sentence. With two under-credited refunds the sentence requires two disputes, the condition one. The three passages reach different conclusions on the same records. Same pattern for E1 (sentence "every purchase that posted to the account twice" vs DPN rule "the … posting most recently posted"); E1's condition matches its sentence.
- Affected: `card.extended.yaml` CUP prerequisite[0].condition, CC prerequisite[1].condition, MCN rule l.1936 ("The notice concerns the most recent Marlowe & Finch refund record settled to the card"), DPN rule l.1742.

**Observations (no demonstrated consequence on either task):**
- O1 `within_months` = rolling `MONTHS(d, NOW) < N` vs prose "last N full calendar months"; recomputed both readings in both worlds — same tiers (see task files).
- O2 CLR compute has no `card_agg_combined_credit_line` cap; each task customer holds one card, no effect.
- O3 DPN billed_interest_part tier 2/3 split on "at least half of that statement balance" and unbilled_accrual_span tier 3 "no payment → no unbilled interest" are weakly grounded in issuer practice (interest on an erroneous amount accrues irrespective of later payments); task 0 sits on billed tier 1 and unbilled tier 2.
- O4 Parameter labels on formula-differing tiers (DPN conversion_fee_tie, CUP promo_paydown_addon). Read as `method`, CUP would have 1 parameter (returned_payment_addback); not asserted as RED because each tier still yields one number for the input.
- O5 `card_fee_reversal.amount` event-field meaning "equal to the fee reversed" not named in CC overwrite (outside base_policy_refs); CC's replaced_by explicitly scopes the partial credit, so the merged reading is unique.
- O6 CC states the payment test in three wordings (two of them the declared overwrite / its gate), all of identical scope.
- O7 Blueprint claim event types not targeted by any extended policy.
- O8 The seeds' billing-error states (a 250.00 card credit for a 612.40 refund record, contrary to base "The credit equals the amount that record settles to the card"; a duplicate posting) are the errors the dispute policies address, not charter-producible normal states; accepted as premises.
- O9 uuid8 uniqueness across other difficulties' modules not checked (read isolation).
- O10 `raise_credit_line_b8050b6c` takes `status` and writes it to the account; harmless when the looked-up status is passed, but a credit-line tool writing account status is outside the policy's terminal state.

## closing_checklist
Written 2026-10-13 after both tasks' reveals; nothing above this heading was changed after any reveal.

**The difficulty does not close: the four relationships are not PASS on either task.**

| task | SOURCE-POLICY | SOURCE-CHAIN | SOURCE-FACTOR | SOURCE-TASK | file |
|---|---|---|---|---|---|
| 0 | RED (F1, demonstrated on its world) | PASS | RED (F2) | RED (stale 6300.00 in the scored argument's tracing) | `0.md` |
| 1 | RED (F3 by citation; no consequence in its world) | RED (stale "card_disputes is empty" in closure why_false) | RED (stale 2665.75 tier evidence) | PASS | `1.md` |

Step 4 list:
- One audit file per task (`0.md`, `1.md`) plus this file. First revision, so no older revisions. Neither comparison section is PASS.
- Coverage and scopes: the 5 extended policies are covered by task 0 {CLR, DPN} and task 1 {CC, CUP, MCN}, pairwise disjoint. Five task tools, each with its own uuid8 (cross-module uniqueness not checked, O9). Independent derivation equals GT on every scored argument (567.22, 6400.00; 370.38, 228.47, 28.48).
- Trees: task 0 has 1 prerequisite problem / 1 value_input edge; task 1 has 2 prerequisite problems / 3 value_input edges; each has a customer-owned write (DPN, MCN); difficulty graph acyclic.
- Factors: every declared factor bears weight on its task's world against an honest baseline, and every all-baseline fall-back differs from gold (6700, 498.00; 612.40, 0.00, 12.80). Ladder realism fails for DPN `conversion_fee_tie` (F2), which leaves DPN under the 2-parameter floor.
- Gates: not re-run by the auditor. The brief's snapshot is the only gate evidence; a re-run on the final form belongs after rework.

## revision_2

### charter_global_frozen (revision 2)
- Frozen 2026-10-13T19:40Z, same auditor. Round-1 text above is untouched.
- Entry conditions: coordinator snapshot `.audit_views/policy/card_billing_and_disputes/snapshot_r2.txt` (2026-10-13T19:37Z) shows EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE (branches 38.50, steps 13.50, history_rows_max 75, branches_max 48), GROUNDING and SCOPE all OK. Traceability has 0 non-tool_name misses. validate_scenario is INVALID only because of "required document … not found": the auditor re-ran it and got 24 errors, 0 of any other kind. `tasks/card_billing_and_disputes/rework_r2_claims.md` is present.
- Shared inputs moved: `card.extended.yaml` 5d75237e58a8c743 → ab6d07308c9c2e68; `task_tools.py` 7c5d54c3038bc53a → a82cf685a25c9e9b. So every charter-global section is re-derived below. Masked views unchanged (0.json 20a39f6cc083f431, 1.json 7dd07605ed856bee): frozen_time, user_scenario and initial_state did not move.
- Base copy: lines 1-1517 are still byte-identical to `blueprint/products/card.yaml`.
- Nothing in this section is derived from round-2 GT. The revised task JSONs (0.json 175285f3debe9406, 1.json e1accc8f48907827) were not opened before this section and both task revision_2 derivations were written.

### re-derivation summary (all checks 1-3, 6, 7 and factor_ladders re-run on the revised file)
- **policy_conflict_scan**: same five policies, subjects, computes and target tools. DPN and MCN are still told apart by reason and object. CLR now opens with a scope sentence: "…for a cardmember holding no other Marlowe & Finch card account in active or restricted status… a cardmember who also holds an account on the other network is sized under the base credit line rule and the combined credit line limit alone." This carve-out leaves a dual-account holder with only the base ceilings ("at most …"), so it gives no single figure; no task world has a second account (observation O11). Scopes are still disjoint and complete: task 0 {CLR, DPN}, task 1 {CC, CUP, MCN}.
- **rule_compute_equivalence**:
  - DPN: the object is now anchored on `fx_anchor` = LATEST foreign_transaction_fee `original_card_txn_id` by post_date. The rule says "the purchase posting against which the account's most recently posted foreign transaction fee was assessed and the other purchase posting from the same merchant with the same transaction date". No merchant-category filter remains. The zero cases ("no foreign transaction fee … or … no such twin … zero") map to `pair_total > later_amt` / `or 0` guards. `related_fee` is a plain sum, and the rule says "The foreign transaction fee posted against the posting in error, when one has posted, is the related fee". `grace_excl`, `billed_int` (whole base / day-prorated when `err_period == last_period` / balance share; 0 when int_base ≤ 0, which the rule's own formulas also give) and `unbilled_int` (keyed on purchase interest charged and on the error's posting date) each match their sentences. "the sum, rounded half up to the cent" matches `result`.
  - MCN: the object is "the cardmember's most recent Marlowe & Finch refund record settled to the Marlowe & Finch card tender", which is exactly the `refund_tender_type='mf_card'` XLATEST filter. The out-of-scope / zero sentence maps to `0 if (not refund_amt or credited >= refund_amt)`. All else is unchanged and equivalent.
  - CUP: unchanged except the no-late-fee guard ("an account with no late fee has no missed statement and no catch-up amount is taken").
  - CC: the cure ladder is now ≤ cure_fast_days / > cure_slow_days / in between, and the compute matches. The result gate `ct_cured and ct_fee_amt > 0` rests on the prerequisite sentence and the overwrite's payment test, plus "an account with no late fee has no courtesy credit".
  - CLR: windows now read "fewer than N full calendar months before today", which is exactly the DSL `_within` (closes O1).
  - Every ladder tier is still a rule sentence and a compute branch.
- **action_binding_and_uuids**:
  - Five distinct `(target_tool, computes)` claims; uuid8s unchanged and distinct.
  - `raise_credit_line_b8050b6c` no longer writes status: it updates only credit_limit and last_credit_limit_change_date and echoes `status` as `status_confirmed`.
  - No tool body branches on a prerequisite state. No docstring names another tool, orders actions or carries an example value.
- **prerequisite_graph**: same four edges (CLR←DPN, CUP←MCN, CC←CUP, CC←MCN), all value_input and state form. Each `policy_source` is still verbatim the closing sentence(s) of the blocked rule, each `resolved_by` is still the depended-on target_tool, each gate binding exists, and the graph is acyclic.
- **prerequisite_sentences** — each sentence, its condition and the depended-on policy's object now name one and the same record:
  - E1: "the foreign purchase against which the account's most recently posted foreign transaction fee was assessed, when it posted to the account twice" = condition "the purchase posting named by the original_card_txn_id of the account's most recently posted foreign_transaction_fee row has a twin" = DPN's object.
  - E2: "the cardmember's most recent Marlowe & Finch refund to the card tender, if it lacks its full card credit" = condition "the card credits naming the cardmember's most recent order_refund record with refund_tender_type mf_card total less than that refund" = MCN's object.
  - E4: same as E2.
  - E3: unchanged.
  - Each edge still has a single writer, and each sentence still passes the four-point test.
- **override_declarations**: unchanged. CC carries the two declared overwrites on `card_courtesy_fee_waiver`. CLR, DPN, MCN and CUP have no undeclared override.
  - DPN's new "finance and other charges imposed as a result of it" is compatible with base `card_billing_dispute`.
  - CLR's scope carve-out narrows where the extension applies and does not override any base sentence.
- **factor_ladders**:
  - DPN now has twin_selection (method), interest_base_pick (parameter), grace_test_exclusion (parameter: promo + excluded / excluded / 0), billed_interest_part (method) and unbilled_accrual_span (method) — 2 parameter, 3 method.
  - grace_test_exclusion is real practice: a payment need not cover deferred-interest promotional balances (Reg Z §1026.54) or amounts under billing dispute (§1026.13(d)) to keep the grace period.
  - The billed tiers (whole base when the error alone cost the grace period / day-prorated when the error posted in the latest cycle / balance share) are real practice. So are the unbilled tiers (no accrual while grace holds; accrual from the statement date or from the posting date) — this closes O3.
  - CC cure_speed (bonus up to 21 days / penalty past 45 / nothing in between) is real goodwill practice, and all three tiers are reachable.
  - The other ladders are unchanged from round 1. Counts: CLR 4p/1m, DPN 2p/3m, MCN 2p/2m, CUP 2p/2m, CC 5p/1m. Cross-difficulty: CLR relationship_share (loyalty), MCN owed_comparison and proration (order), CC courtesy_relationship_bonus (loyalty).
  - No two tiers of one ladder share an outcome. Every fall-through equals its policy's baseline.
  - The DPN baseline rule now includes the plain related fee (later-posted posting + its fee).
  - O4 for DPN is gone with conversion_fee_tie. CUP promo_paydown_addon remains a borderline label (observation only).

### round-1 charter findings — status
- **F1 (SOURCE-POLICY): CLOSED.** The rule and compute select the same anchor, and no unsupported filter is left. Its effect on task 0's world is in `0.md` revision_2.
- **F2 (SOURCE-FACTOR): CLOSED.** The unreal ladder is struck, the fee is a plain imposed charge, and DPN is back to 2 parameter factors with a real-practice grace_test_exclusion.
- **F3 (SOURCE-POLICY): CLOSED.** The E1, E2 and E4 sentences, conditions and depended-on objects are of equal scope.
- **Observations**:
  - O1 closed.
  - O2: now handled by the scope carve-out, which is left as new observation O11.
  - O3 closed.
  - O4: partially closed (CUP label remains).
  - O5, O7, O8 and O9 unchanged.
  - O6 closed: the payment test is stated once in the overwrite and once in the prerequisite sentence.
  - O10 closed.
- **New charter-level findings**: none at RED. New observation O11: the CLR scope carve-out leaves dual-account holders without a definite size, and no task touches it.

### closing_checklist (revision 2)
Written after both revision_2 reveals; nothing in the charter-global revision_2 sections above was changed after the reveal.
- Task files: one per task, plus this file; the round-1 text is preserved and revision_2 is appended. Both revision_2 comparisons are PASS.

  | task | SOURCE-POLICY | SOURCE-CHAIN | SOURCE-FACTOR | SOURCE-TASK |
  |---|---|---|---|---|
  | 0 | PASS | PASS | PASS | PASS |
  | 1 | PASS | PASS | PASS | PASS |

- Coverage: the 5 extended policies are covered by disjoint scopes (task 0 {CLR, DPN}, task 1 {CC, CUP, MCN}). There are five tools, each with its own uuid8, and the task tools and GT are closed. Independent derivation equals GT on every scored argument.
- Problem trees: task 0 has n = 1 with 1 value_input edge; task 1 has n = 2 with 3 value_input edges. Each tree has a user-owned write (DPN, MCN). The difficulty graph is acyclic.
- Factors:
  - Every computation has a self-sufficient baseline and 4-6 factors with at least 2 parameter and at least 1 method: CLR 4/1, DPN 2/3, MCN 2/2, CUP 2/2, CC 5/1.
  - Each task has a multi-source factor and a cross-difficulty factor: task 0 has loyalty; task 1 has order and loyalty.
  - Every ladder is real, and every factor bears weight against an honest baseline.
  - The all-baseline fall-backs (6700, 512.94; 612.40, 0.00, 12.80) all differ from gold.
- Gates: the coordinator's round-2 snapshot (`snapshot_r2.txt`) on the final form is all OK. Traceability shows only the tool_name misses expected before the KB render, and validate_scenario shows only required-document errors.
- Open observations, none at RED level: O4 (CUP promo_paydown_addon label), O5, O7, O8, O9, O11.

**Charter: CLEAN. Difficulty passes the source-layer audit (revision 2).**

## revision_3

### charter_global_frozen (revision 3)
- Frozen 2026-10-14 (UTC, before the revised task JSONs were opened), same auditor. The round-1 and round-2 text above is untouched.
- Entry conditions: coordinator snapshot `snapshot_r3.txt` (2026-10-14T19:41Z):
  - EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE (branches 41.50, branches_max 52), GROUNDING, SCOPE and TRACEABILITY are all OK, with 0 misses.
  - validate_scenario: re-run by the auditor, 12 errors, all "required document … not found".
  - `rework_r3_claims.md` is present. Render-source report `audits/render_source/card_billing_and_disputes/render_r1_card.md` read in full.
- Moved inputs: `card.extended.yaml` → bdaf24343dc939ef (re-derived below). `task_tools.py` unchanged (a82cf685a25c9e9b), so its round-2 conclusions carry forward by these hashes.
- Masked views: task 0 changed (0.json → 38835d34258c86b4: the seed and the persona's Casa Lusitana lines); task 1 unchanged (7dd07605ed856bee). Base copy lines 1-1517 still identical to `blueprint/products/card.yaml`.

### re-derivation (checks 1-3, 6, 7 and factor_ladders on the revised charter)
- **R1, compute_basis verbatim — CLOSED.** Mechanical sweep, whitespace-normalised, over all five policies:
  - every compute binding has a `compute_basis` entry, and there are no extras;
  - every quote is a substring of its own rule;
  - every `baseline.rule` sentence is a sentence of the rule;
  - every `policy_source` is in its blocked rule.
  The three render-reported quotes (CLR `paid_3m`, CC `ct_mf_spend_12m`, CC `ct_missed_due`) now pass.
- **R2, CLR clause without compute — CLOSED.** The one-account / other-network scope clause is gone, which also closes O11. The base `card_agg_combined_credit_line` is again inherited and not computed (round-1 O2, re-opened as an observation). The task 0 customer holds one card.
- **R3, factor tiers resting on another factor's output — CLOSED as stated.** Every factor's tier conditions now read its own bindings and plain record reads:
  - CLR: utilization_share absorbs the measured-balance method.
  - DPN: interest_bearing_balance, billing_time_fraction and accrual_days read the latest statement and the *fee-bearing posting*.
  - MCN: time fraction and accrual days read the refund date.
  - CUP: coverage_follow selects among record values; dispute_relief is a separate reduction.
  The skill does not itself require factor independence; it was checked only because the renderer raised it. Its side effect in DPN is new finding N1 below.
- **R4, pinned readings — CLOSED.**
  - MCN: "issued on the latest statement date or within the proration_days … before it … after the latest statement date, the fraction is zero" = `mc_time_frac`.
  - CUP: "(a due date already passed included)" = `DAYS(NOW, cu_last_due) <= 21`.
- **rule_compute_equivalence**: every revised binding matches its sentence.
  - CLR: recency is `recent_floor + recent_step × months`; pay_share has three tiers with the "no statement in the span" fall-through.
  - DPN: `ib_bal` has three tiers, rounded; `time_frac` and `acc_days` are keyed on `anchor_post`/`anchor_period`; billed is 0 when ib_bal ≤ 0.
  - MCN: `mc_time_frac`, `mc_acc_days`; billed is 0 when the latest balance ≤ 0.
  - CUP: `cu_relief` has three tiers floored at 0, and `cu_due_part = max(missed minimum, coverage − relief)`.
  - CC: unchanged from round 2.
- **action_binding_and_uuids / prerequisite_graph / prerequisite_sentences / override_declarations**: tools unchanged. The four edges, their sentences and conditions, form, writers and overwrites are unchanged from round 2, and the sweep confirms each policy_source is verbatim.
- **factor_ladders**:
  - Counts:
    - CLR: utilization_share, relationship_share, late_history_share and payment_pattern_share are parameters; recency_scale is the method. 4p/1m.
    - DPN: interest_base_pick and interest_bearing_balance are parameters; twin_selection, billing_time_fraction and accrual_days are methods. 2p/3m.
    - MCN: owed_comparison and missing_credit_interest_base are parameters; missing_credit_time_fraction and missing_credit_accrual_days are methods. 2p/2m.
    - CUP: coverage_follow and dispute_relief are methods; promo_paydown_addon and returned_payment_addback are parameters. 2m/2p.
    - CC: 5p/1m, unchanged.
  - Every ladder has three disjoint tiers with distinct outcomes, and every fall-through equals its policy's baseline.
  - The baseline rules (DPN, MCN, CUP) now spell out the composed formula with standard values ("as standard … zero / one / the latest statement balance"), so each is self-sufficient.
  - Cross-difficulty: CLR relationship (loyalty), MCN owed/time/accrual (order), CC relationship (loyalty).
  - Realism: CLR payment pattern (revolver vs transactor) and sliding recency are real CLI inputs. DPN interest_bearing_balance (statement balance net of deferred-interest promo and disputed amounts) is real practice. MCN time fraction (days the credit was missing in the cycle) and the CUP dispute relief (reduction of the minimum by excluding the disputed amount) are real practice. **Exception: N1.**

### findings (revision 3)
**N1 — SOURCE-FACTOR RED (new; unreal method tier introduced by the R3 restructuring). Bears on task 0.**
- Symptom: DPN's `billing_time_fraction` and `accrual_days` measure the interest caused by the posting in error on the posting date of the *fee-bearing posting*, which may be the other, valid twin.
- Evidence:
  - The rule sentence that introduces the time fraction: "the billing-time fraction follows the posting date of the fee-bearing posting: when that posting belongs to the latest billing period, the fraction is the calendar days from its posting date to the latest statement date divided by proration_days".
  - The accrual-days sentence carries the same anchor.
  - Compute keys on `anchor_post` / `anchor_period` (from `fx_anchor`), not on the posting in error. The rule's own opening defines the amount as "the posting in error together with the finance and other charges imposed as a result of it".
- Why unreal: an issuer crediting the finance charges a billing error imposed (FCBA / Reg Z §1026.13(e)) prorates them from when the erroneous charge was on the balance — its own posting date. No issuer would publish that the interest caused by one posting is timed from a different posting's posting date. Here the "fee-bearing posting" is an anchor chosen to make the factor read no sibling output; it is not something the business weighs.
- Demonstrated consequence: see `0.md` revision_3. On task 0's world the fee-bearing posting 1eacd1df posted 2026-08-29, while the posting in error deaf6d98 posted 2026-08-27. The charter gives billed interest 3.80 and amount 543.39. Prorating from the erroneous posting's own date gives 4.18 and 543.77.
- Affected: `card.extended.yaml` DPN rule (billing-time fraction and accrual-days sentences), compute `anchor_post`, `anchor_period`, `time_frac`, `acc_days`, factors `billing_time_fraction` and `accrual_days`.

**Observations (revision 3):**
- O2 re-opened: no combined-cap compute in CLR; one card in the task 0 world, so no effect.
- O4: CUP promo_paydown_addon label, unchanged.
- O5, O7, O8, O9: unchanged.
- O11: closed by R2.

### closing_checklist (revision 3)
- Written after both revision_3 reveals. Nothing in the revision_3 charter sections above was changed after the reveal.

  | task | SOURCE-POLICY | SOURCE-CHAIN | SOURCE-FACTOR | SOURCE-TASK |
  |---|---|---|---|---|
  | 0 | PASS | PASS | **RED (N1)** | PASS |
  | 1 | PASS | PASS | PASS | PASS |

- Render-source items R1–R4: closed. Round-1 F1/F2/F3 and T-level findings: remain closed.
- Gates on the final form: the coordinator snapshot `snapshot_r3.txt` is all OK.
- **Difficulty does not close: N1 is open.**

## revision_4

### charter_global_frozen (revision 4)
- Frozen 2026-10-14 (UTC) before the revised task JSONs were opened. Earlier revisions are untouched.
- Entry conditions: `snapshot_r4.txt` (2026-10-14T20:24Z) shows every gate OK, including TRACEABILITY OK with 0 misses. validate_scenario, re-run by the auditor: 12 errors, all "required document … not found". `rework_r4_claims.md` is present.
- Inputs:
  - `card.extended.yaml` changed → 65a7e72c01b91c83, re-derived below.
  - `task_tools.py` unchanged (a82cf685a25c9e9b).
  - Masked views: 0.json changed → d9fa4b3e54a621e7 (seed plus a persona line); 1.json unchanged (7dd07605ed856bee).
  - Base copy lines 1-1517 still identical to `blueprint/products/card.yaml`.
- What moved: a whitespace-normalised comparison against the revision-3 dump shows MCN, CUP and CC rule, compute, ladders, prerequisites and baselines unchanged. Prerequisite forms, writers and conditions are unchanged on all four edges (condition lengths identical). CLR changed only in `paid_3m` / `pay_span_paid` and their rule sentences, which now net out returned payments. DPN was restructured.

### re-derivation
- **Render-source items stay closed** (scripted sweep):
  - every compute binding has a basis, and every basis is a verbatim substring of its rule;
  - every baseline sentence is in its rule, and every policy_source is in its blocked rule;
  - no factor's bindings read another factor's binding, directly or through plain bindings (transitive closure), in any of the five policies.
- **N1 — CLOSED.**
  - Rule: "the billing-time fraction follows the posting in error's own posting date, from which the erroneous charge was on the balance"; "the accrual days follow the latest statement and the posting in error's own posting date".
  - Compute: `err_post` / `err_period` come from `err_id`. The fee-bearing posting only locates the pair.
  - The posting in error is now a plain three-way record selection, stated once in the rule and the baseline, and no longer a factor. This is what lets the time fraction read it without breaking factor independence.
- **DPN new factor `related_other_charge`** (parameter): returned payment fee / late fee for the error's billing period / 0.
  - Rule and compute match.
  - Realism: tier 2 (a late fee for the period the error posted in) is the classic Reg Z "other charge" resulting from a billing error. Tier 1 credits a returned-payment fee on a payment of at least the statement balance that carried the error. The causal link to the error is presumed, not tested against the cardmember's funds, but a goodwill issuer can plausibly publish it — observation O12.
  - Compute reads only the *latest* returned payment fee, while the rule says "a returned payment fee was assessed after the latest statement date …". A world with an older qualifying fee and a newer non-qualifying one would split the two; neither task world has more than one such fee — observation O13.
- **DPN counts**: 3p (interest_base_pick, interest_bearing_balance, related_other_charge) / 2m (billing_time_fraction, accrual_days). Each method tier is a distinct formula. Every fall-through equals the baseline. The baseline rule (correct posting + fee; base 0; balance = statement balance; fraction 1; days 0; other 0) is self-sufficient.
- **CLR**: netting returned payments in the payment spans is consistent with base `card_evt_returned_payment` ("that payment no longer counts toward any minimum payment"). Rule and compute match. Counts are still 4p/1m.
- Other checks:
  - tools unchanged;
  - prerequisite graph, sentences and conditions unchanged and verbatim;
  - CC overwrites unchanged;
  - MCN, CUP and CC ladders and counts unchanged from revision 3.

### findings (revision 4)
- N1 closed. No new RED-level charter finding.
- Observations: O2 (no combined-cap compute in CLR; one card in task 0), O4, O5, O7, O8, O9, plus new O12 and O13 above.

### closing_checklist (revision 4)
- Written after both revision_4 reveals. Nothing in the revision_4 charter sections above was changed after the reveal.

  | task | SOURCE-POLICY | SOURCE-CHAIN | SOURCE-FACTOR | SOURCE-TASK |
  |---|---|---|---|---|
  | 0 | PASS | PASS | PASS | PASS |
  | 1 | PASS | PASS | PASS | PASS |

- Earlier findings: F1–F3, the task-level findings, the render-source items R1–R4 and N1 are all closed.
- Coverage: the five extended policies sit in disjoint task scopes. Five tools, each with its own uuid8.
- Problem trees: task 0 has n = 1 with 1 value_input edge; task 1 has n = 2 with 3 value_input edges. Each has a user-owned write. The graph is acyclic.
- Factors:
  - Counts: CLR 4p/1m, DPN 3p/2m, MCN 2p/2m, CUP 2p/2m, CC 5p/1m.
  - Each task has a multi-source factor and a cross-difficulty factor.
  - Every factor bears weight against an honest baseline.
  - The all-baseline fall-backs (6700, 528.18; 612.40, 0.00, 12.80) all differ from gold.
- Gates on the final form: `snapshot_r4.txt` all OK.
- Open observations, none at RED level: O2, O4, O5, O7, O8, O9, O12, O13.
- **Charter: CLEAN. The difficulty passes the source-layer audit (revision 4).**

## revision_5
- Entry conditions: `snapshot_r5.txt` (2026-10-14T21:51Z) shows every gate OK, including TRACEABILITY OK. validate_scenario is VALID (0 errors, 0 warnings, re-run by the auditor). `rework_r5_claims.md` is present.
- Charter and tools are unchanged against round 4 (`card.extended.yaml` 65a7e72c01b91c83, `task_tools.py` a82cf685a25c9e9b), so every charter-global section carries forward from revision_4 by these hashes.
- Masked views: 0.json → 512983ef7d9b46cd (rename); 1.json unchanged (7dd07605ed856bee).
- `tasks/1.json` bytes changed (318c61dba6301b24 → b0ddabc8fbe5062a) with no claim. Its masked view is identical, and every scored argument, computation, sensitivity, closure edge and proof path re-checks equal to revision_4. No semantic change was found — observation O14.
- **Closing (revision 5): both tasks PASS. Charter: CLEAN.** Open observations: O2, O4, O5, O7, O8, O9, O12, O13, O14, plus O15 in `0.md`.
