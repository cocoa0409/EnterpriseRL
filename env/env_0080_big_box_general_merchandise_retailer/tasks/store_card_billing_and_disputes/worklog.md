# worklog — store_card_billing_and_disputes (env_0080), M=2

## Step 0 — pre-check
- Read: references (product_extended.yaml, task_tools.py, task.json), blueprint.yaml, products/card.yaml (base copied verbatim into card.extended.yaml), db_schema.json, share_tools.py, XF_recipe.md, owner_ruling.md; other charters only for cross-category rows (membership_delivery_benefit, order policies, market_fbn_benefits).
- Claimed events: card_open_dispute, card_dispute_credit, card_reverse_dispute_credit, card_resolve_dispute, card_assess_fee, card_reverse_fee, card_assess_interest, card_post_payment, card_post_credit, card_refund_credit_balance, card_set_autopay, card_change_limit, card_close.
- Trigger rule: every card event in base has `triggers: []` -> no task-tool write of this difficulty can land in another category.
- Base automatic clauses to watch: interest at statement close; late fee at missed due date; suspension at 60 dpd; credit-balance auto refund after 6 months; dispute resolution limit (2 cycles / 90 days, $50 noncompliance); courtesy waiver 1 per 12 months.
- DSL limits found (check_compute.py): windows only `within_months` from NOW; eq filters exact; LATEST keeps first row on ties; no row-literal may enter a policy, so every computation must locate its object by a record test (latest dispute, latest late fee, latest statement).

## Draws
- task 0: prerequisite_problems=2, factor_counts=[4,5,5]
- task 1: prerequisite_problems=1, factor_counts=[6,4]

## Inventory / scope decision (Principle C)
Card writes whose amount is decided by several record-decidable rules: credit line increase (on request, agent), catch-up payment (holder's own payment, user, ruling c/b), final credit of a confirmed duplicate-posting dispute (owed, agent), credit-balance refund (holder's request, user, ruling a), first-late-fee courtesy reversal at the next contact (owed, agent).
Not claimed (single-number or not locatable without literals): fee-cap reversals, provisional-credit re-bills, dispute openings, autopay (no amount field), closure (no amount).
- Task 0 [4,5,5]: SEE plan.md revision 2 (line increase <- catch-up payment, final credit).
- Task 1 [6,4]: SEE plan.md revision 2 (credit-balance refund <- first-late-fee courtesy).
- Headroom: after task 0 claims refund/final-credit/courtesy, task 1 keeps line increase + payment (disjoint tools/events).

## Trigger list (filled per tool)
| tool | event(s) written | base triggers |
|---|---|---|

## Probe table (decoy / absent / second record per read) — filled per policy
## Defining-sentence table (sentence -> binding/factor) — filled per policy

## Revision 3 (factor allocation inside task 0)
- card_ext_duplicate_final_credit takes 5 factors (settled_principal method; carried_error_days, noncompliance_allowance, error_late_fee, correct_part_reinstatement parameter) — written to disk, check_extended structure clean.
- card_ext_catch_up_payment takes 4, card_ext_line_increase 5. Multiset {4,5,5} = draw.
- Independence (XF A1/A4): shared selections (d_ref/d_amt/d_date/d_src/d_stmt, dup_excess, correct_part, first_paid, latest_close) are plain bindings stated once in the rule; factor bindings read only plain bindings and records; carried_interest and result are assembly.
- Cross-difficulty for task 0 is carried by the line increase (membership), not by the final credit (its order read sits in a plain binding shared by three factors).

## Task 0 — closed (per-task gates 7/7 green: extended, task_tools, replay, solvability, compute, grounding, cross_fire)
Tree: card_ext_line_increase <- card_ext_catch_up_payment (user) <- card_ext_duplicate_final_credit; both edges value_input, state form (line: affirmative 'only after'; catch-up: negated 'not until').
Expected: final credit 1421.69 (baseline 1412.84), catch-up 519.03 (baseline 0.00), new limit 5100.00 (baseline 4400.00). Edge deletion: no payment -> limit 4000.00; no final credit -> catch-up 527.88, limit 5200.00.
World generator / builder: scratch only (/tmp/store_card_billing_and_disputes_0080/gen0.py, t0/*). frozen_time 2026-10-14 10:30:00 EDT.

### Trigger list
| tool | event(s) written | base triggers |
|---|---|---|
| settle_duplicate_dispute_b93aba52 | card_resolve_dispute, card_dispute_credit (+ holding balances) | [] , [] |
| make_card_payment_5ec32b69 | card_post_payment (+ holding balance) | [] |
| raise_credit_limit_a1e4ca90 | card_change_limit (holding update) | [] |

### Probe table (scratch copies, probe0.py)
| read | decoy | absent | second record |
|---|---|---|---|
| FC latest duplicate dispute | older not_received dispute ignored -> 1421.69 | no dispute -> 0.00 (nothing settled) | credit 100.00 posted against the disputed posting -> tier 1, 1405.48 |
| FC order amount paid (CFIELD order_id=source) | other 20 orders never matched (order_id filter) | missing order -> 0 paid -> excess = postings, tier 'otherwise' | n/a (one order per id) |
| catch-up missed statement (latest late fee) | 2026-07-05 fee belongs to 2026-06-09, not the latest | no late fee -> no missed statement, shortfall 0 | returned payment netted |
| line membership CFIELD status=active | canceled membership -> addition 0 (4600.00) | no membership -> 0 | n/a |
Same-day ties: LATEST keeps the first row in history order; the FC rule states 'of two received the same day the one recorded first'.

### Defining-sentence table (sentence -> binding/factor)
- FC: scope sentence -> d_* (plain); duplicate excess -> dup_excess (plain, shared by settled_principal / carried interest / correct part); settled principal ladder -> settled_principal; payments recorded against a statement -> first_paid (plain); finance charge carried by the error -> carried_interest (assembly); carried-error days ladder -> carried_error_days; correct part -> correct_part (plain); resolution limit -> past_limit (noncompliance_allowance); noncompliance allowance ladder -> noncompliance_allowance; dispute-adjusted minimum + late fee carried ladder -> error_late_fee; interest reinstated ladder -> correct_part_reinstatement; 'amount posted' -> result.
- Catch-up: missed statement -> cure_stmt (plain); days past due -> days_past_due (plain); baseline sentence -> cure_min/cure_paid; shortfall ladder -> shortfall_measure; amount owed from history -> owed_in/owed_out/under_dispute (over_limit_restoration); over-limit ladder -> over_limit_restoration; restoration fee ladder -> restoration_fee; cycle-since-miss ladder -> cycle_since_miss; total -> result.
- Line: prerequisite sentence -> cure_* (plain gate); 12-month window sentence -> window counts; baseline sentence -> result rounding/ceiling; percentage ladder -> conduct_percentage; base ladder -> line_use_sizing; membership ladder -> membership_line_addition; tenure ladder -> tenure_line_addition; purchase-volume ladder -> purchase_volume_addition; 'every line addition is added' -> raw_limit.

### Known weak points (honest notes for the audit)
- catch-up restoration_fee and cycle_since_miss both key on the days-past-due band (company 'restore to current' schedule); over_limit_restoration measures over-limit on the history-read balance net of amounts still under dispute.
- line increase grants a modest increase to an account with a recent return; its conduct ladder prices that (5% vs standard 10%).

## Task 1 — policies on disk (card_ext_first_late_fee_courtesy 6 factors, card_ext_credit_balance_refund 4 factors), tools reverse_late_fee_courtesy_ba087f69 / refund_credit_balance_0212c7e9 (user, ruling a)
- Edge: refund <- courtesy, value_input gate credit_bal, state form, affirmative 'fixed only after'.
- Overwrite: card_evt_late_and_returned_fees courtesy sentence retired only for a qualifying courtesy late fee (replaced_by restates the base courtesy treatment for every other fee).
- Known DSL residue: the order hold reads CFIELD first match; the rule states 'where several orders share a status, the first on the order list is the one held' so rule == compute.

## Task 1 — closed (per-task gates 7/7 green)
Tree: card_ext_credit_balance_refund (user) <- card_ext_first_late_fee_courtesy; value_input, state form, affirmative.
Expected: courtesy 25.92 (baseline 6.40), refund 662.58 (baseline 1527.01). Edge deletion: refund 636.66. frozen_time 2026-10-22 14:05:00 EDT.

### Trigger list
| tool | event(s) written | base triggers |
|---|---|---|
| reverse_late_fee_courtesy_ba087f69 | card_reverse_fee (+ holding balance) | [] |
| refund_credit_balance_0212c7e9 | card_requests row (credit_balance_refund, confirmed) + card_refund_credit_balance (+ holding balance) | [] |

### Probe table (probe1.py)
| read | decoy | absent | second record |
|---|---|---|---|
| refund payment hold | equal 2026-10-08 online payment not held | no payment within 15 days -> no hold | returned payment in 12 months -> all 2-month payments held (refund 0.00) |
| refund dispute hold | — | no dispute -> 0 | dispute resolved for merchant, not re-billed -> unbilled credit held (662.58) |
| refund order hold (CFIELD first match, rule states 'first on the order list') | fulfilled order -> no hold (737.56) | no order -> 0 | ready order -> held (662.58) |
| courtesy late fee | — | no late fee -> 0 | second late fee in 12 months -> does not qualify (0.00); older late fee 13-24 months -> history 6 points (24.00) |
| courtesy membership CFIELD status=active | canceled -> 0 points (24.00) | none -> 0 | — |

### Defining-sentence table
- Courtesy: 'The courtesy late fee is the most recent late fee ...' -> fee_stmt/fee_amt/late_fees_12/courtesies_12/qualifies (plain); fee statement sentence -> fee_paid (plain), fee_due (plain); tenure/lateness/membership/automatic-payment/history/coverage ladders -> the six factors; 'The courtesy share is 20 percent together with every point ...' -> share (assembly); baseline sentence -> result.
- Refund: credit balance sentence -> credit_bal (plain, gate of the edge); payment/dispute/rewards/order hold ladders -> the four factors; 'less every hold this rule sets' -> result.

### Draft recomputation from the visible context (both tasks)
Using only the policy prose, the tool schemas, the persona lines and the share-tool returns, the same objects (dispute row, missed statement 2026-09-09, late fee 2026-09-10, card accounts) and the same figures were re-derived binding by binding (the evalx traces print every binding from the visible records): 1421.69 / 519.03 / 5100.00 and 25.92 / 662.58 (identical to evalx.py and check_compute).

### Revision log
- R1-R2 allocation (plan.md): refund moved to a World Mastercard world because Store Card worlds cannot exercise provisional-credit or rewards holds.
- R3: final credit took 5 factors (correct_part_reinstatement added), catch-up 4; FC-to-line edge moved to FC-to-catch-up (catch-up reads the history-read amount owed net of disputes, which the settlement changes).
- R4: absent-record guards ('or 0', 'if cure_due else 0', past_limit gated on a dispute existing) after probe0 crashed on a world with no dispute.
- R5: assembly sentences of the final credit and catch-up made generic (no factor quantity named), compute_basis quotes re-swept verbatim (basis_sweep.py: bad = 0).
ROUND 1: gates 7/7 green

## REWORK round 2 — plan (audit revision_1: R-A1..R-E3, T0-1)
Verified every finding against the artifacts (all reproduce). Closure plan by defect class:
- R-A1 dup folds the error late fee into the final credit: declare a self-scoped overwrite of the base fee-reversal sentence (card_evt_late_and_returned_fees added to base_policy_refs); fee net of any reversal already posted against it (R-C1 second member).
- R-A2 refund holds vs base refund clause: declare a self-scoped overwrite that keeps held parts as credit balance released on a later request / six-month rule; drop the rewards hold (never released) entirely.
- R-A3 catch-up 'days past due': stop redefining the base measure — quantity renamed 'days since the missed due date'; the catch-up is nothing once the missed statement is met (plain gate).
- R-B1 rule != compute: dup selector scoped to the most recent duplicate dispute (out of scope when its source is not a Northgate order); reinstatement days floored at zero; refund dispute hold second tier rewritten on provisional credits; same-day tie stated for every LATEST read; catch-up disputed tier reads the single most recent dispute; cash advances excluded where the rule says purchases; courtesy lateness ladder states the on-time case.
- R-B2 'greater of A and B less C': rewritten as an ordered two-step sentence in dup and catch-up.
- R-C1 confirmation test: needs two or more postings carrying the order's reference.
- R-C2 false framing: removed 'no payment method on file'; the rule states the cardholder enters the paying bank account in the secure line.
- R-C3 / R-E3e: order hold dropped.
- R-D1/R-D2: catch-up wait narrowed to the same object the dup rule settles (most recent duplicate dispute, Northgate-order source, tier without provisional credit).
- R-D3: line wait restated on a state every catch-up tier produces (a payment recorded against the missed statement on or after the day its late fee posted).
- R-E1/R-E2/R-E3a: line rebuilt (conduct ladder monotone, line-use factor becomes an additive sizing method with distinct inputs per tier, no pct x base split); courtesy lateness becomes a parameter and a new method (fee basis) with distinct inputs; refund method = residual-interest hold (distinct inputs); clearing hold split into two parameters (channel days, risk days).
- R-E3b history ladder made monotone; R-E3c base courtesy retired for every late fee (one schedule); R-E3d restoration fee keyed on the fee still standing (no reversal), fall-through reachable.
- T0-1 purchases approved over the limit: removed from the task 0 seed (the account goes over limit through interest and fees only); all figures recomputed.


## REWORK round 2 — closures (the round-1 task/figure sections above are superseded by this section and by the rebuilt task files)
- Charter rebuilt policy by policy (scratch scripts /tmp/store_card_billing_and_disputes_0080/r2/src/*.py, reassembled behind the verbatim base copy).
- Task 0 seed: the five purchases posted while the balance exceeded the limit were removed; limit set to 3900.00 so the one duplicate settlement (re-presented, not re-authorized) is what crosses it; interest and fees keep it over. New gold: final credit 1421.69, catch-up 319.49, limit 5200.00 (baselines 1412.84 / 0.00 / 4200.00). Deletion runs: no payment -> 3900.00; no settlement -> catch-up 328.34, limit 5300.00.
- Task 1 seed rebuilt: closing day 14 (no weekend due dates), payments by phone, one 2-day-late payment on a 28.07 statement (fee 32.00 capped by a same-day regulatory-cap reversal 3.93), minimum autopay 2026-10-09, the 2026-10-14 statement paid in full online (credited Monday 2026-10-19), open not-received dispute with provisional credit, resort refund 860.00 on 2026-10-21; order rows and reads dropped (no factor reads orders). frozen_time 2026-10-30 14:05:00 EDT. New gold: courtesy 21.89, refund 285.45 (baselines 8.00 / 881.89); deletion run 263.56. Persona rewritten (no double payment).
- Factor counts unchanged and honest: dup 5 (1m/4p), line 5 (1m/4p), catch-up 4 (2m/2p), courtesy 6 (1m/5p), refund 4 (1m/3p). Mechanical read-set sweep (readset.py): no factor binding reads another factor's binding. compute_basis sweep: bad = 0.
- Method pairwise inputs: usage_line_addition T1 statement new balance / T2 net purchases / T3 nothing; fee_basis_correction T1 reversal rows / T2 statement minimum / T3 fee; residual_interest_hold T1 full balance + completing payment date / T2 unpaid part + today / T3 nothing; shortfall_measure and cycle_since_miss unchanged (accepted in round 1).

### Probe table round 2 (probe_r2.py, scratch copies)
| read | case | outcome |
|---|---|---|
| dup selector | later marketplace duplicate dispute | rule and compute both settle nothing (0) |
| dup reinstatement | notice after the latest close | no reinstated days (credit not increased by a negative term) |
| dup confirmation | only one posting carries the order | not confirmed (0) |
| dup carried fee | error fee already reversed in full | standing fee 0, fee term 0 |
| line purchases | 600 cash advance added | volume tier unchanged (cash advances excluded) |
| catch-up gate | missed statement re-paid before the call | account current -> 0 |
| catch-up fee | missed late fee already reversed | restoration fee third tier (none) |
| refund dispute hold | merchant-resolved, no provisional credit ever | hold 0 |
| refund latest payment | second payment the same day entered later | the first entered is the most recent (tie rule stated) |
| refund risk | returned payment in 12 months | +20 risk days |
| courtesy lateness | payment on the due date | lateness none (stated case) |
| courtesy basis | no cap reversal posted, fee above minimum | share taken of the minimum |

### Disputed / observation notes
- O-3 (settled_principal reads orders but cross_difficulty null): the order read sits in a plain binding shared by three factors (XF A4), so the factor declares history evidence only; the task's cross-difficulty factor is membership_line_addition.
- O-1 / O-2 (docstring 'Afterwards', no id checks in tool bodies): kept — tools must not validate references or eligibility (skill boundary); the wording describes each call's own post-state.
- O-7 closed: the catch-up rule now says it is recorded against the missed statement.
REWORK round 2: gates 7/7 green

## REWORK round 3 — plan (audit revision_2: R-C1r, R-D2r, R-D3r, R-E1r, N1-N6)
All ten items reproduced on scratch copies before any change. Closure plan:
- R-C1r: duplicate excess compares the postings with what the order record charged = amount paid plus the refunds the order books (returns, price adjustments, other refunds), read from the order history.
- R-D2r: settlement scope requires the most recent duplicate dispute to be still open (no resolution entry refers back to it); the catch-up wait names the same open-dispute test.
- R-D3r / N3 / N1: line wait = the missed statement's minimum met in full by payments recorded against it and not returned (plain record test, verbatim in the catch-up rule); the catch-up's own gate is the same plain test (not a factor output); shortfall_measure keeps the returned-payment tier and gets a mailed-payment clearing tier (both only raise the shortfall), the dispute-adjusted tier is removed; courtesy qualification and the refund wait both carve out fees with less than 1.00 still standing.
- R-E1r: fee_basis_correction removed (its tiers coincide); the courtesy share is taken of the standing late fee (plain); new method factor loyalty_points (membership years / outside-rewards dollars / nothing — distinct inputs) replaces membership_points; coverage_points restored as the sixth factor.
- N2: net purchases defined once in a plain sentence and one plain binding, read by the usage and volume factors.
- N4: dup late-fee tier requires the settled dispute to be the only billing-error dispute its first statement showed and its notice after that statement's closing; catch-up no longer adjusts for disputes.
- N5: one family factor clearing_period owns the clearing window; new method factor dispute_interest_exposure (interest reinstated if the open dispute goes to the merchant, base card_dispute_credits) keeps the refund at four factors.
- N6: second dispute-hold tier = provisional credits posted less those re-billed and less those made final by resolutions for the cardholder.

## REWORK round 3 — closures (supersedes the round-2 figures above for task 1; task 0 figures unchanged)
- Scratch scripts: /tmp/store_card_billing_and_disputes_0080/r2/src/{dup_r3,catchup_r3,courtesy_r3,refund_r3}.py applied on the round-2 policy files and reassembled behind the verbatim base copy; line edits inline in the same scratch dir.
- Task 0 gold unchanged (final credit 1421.69, catch-up 319.49, limit 5200.00); a read of the TV order's history (no refund booked) added before the writes (write steps now 8 / 10 / 12). shortfall_measure's baseline now gives 183.99 (the other three catch-up factors keep their effect: N1 closed).
- Task 1 gold: courtesy 23.02 (standing part 28.07 x 82%; baseline 7.02), refund 282.79 (baseline 883.02); deletion run 259.77.
- Factor counts: dup 5 (1m/4p), line 5 (1m/4p), catch-up 4 (2m/2p), courtesy 6 (1m/5p), refund 4 (2m/2p). Read-set sweep clean; basis sweep bad = 0; no factor id inside a tool name.
- Method pairwise inputs: loyalty_points T1 membership enrolled date / T2 reward credits / T3 nothing; dispute_interest_exposure T1 notice date / T2 disputed transaction's posting date / T3 nothing; shortfall_measure T1 returned rows / T2 mailed payment channel and date / T3 payments only; usage_line_addition T1 statement balance / T2 payments net of returns / T3 nothing.

### Probe table round 3 (probe_r3.py, scratch copies)
| read / case | outcome |
|---|---|
| dup re-evaluated after its own settlement | 0 (still-open test) |
| dup on a withdrawn dispute | 0; catch-up wait not engaged (prices the whole balance as owed) |
| dup when the order books a return equal to the excess | 0 (not a duplicate) |
| dup with a second billing-error dispute on the first statement | fee tier none, rest unchanged |
| line after a 1.00 payment | wait unmet, limit unchanged |
| missed minimum met after the due date, before the fee | catch-up nothing; line granted without a payment |
| mailed payment credited 4 days ago with a returned payment on record | returned tier first (stated order of tiers) |
| courtesy with the fee reversed in full | does not qualify (0); refund wait not engaged |
| courtesy without a membership | loyalty from rewards |
| refund: merchant-resolved, provisional not re-billed | that provisional credit held |
| refund: latest payment mailed, channel new | new-channel period (one family factor) |
| refund: open dispute on the network-only track | exposure counted from the posting date |

### Observations carried
- O-9 (additions still raise the limit of an account in the conduct 'nothing' tier) and O-10 (minimum interest charge in the residual hold) are consistent with the stated rules and the base minimum-charge sentence; kept.
REWORK round 3: gates 7/7 green

## REWORK round 4 (revision_3 findings R3-1..R3-5; observations O-11..O-13)
Verified every finding against the charter and probes before editing; all five reproduced, none disputed.
- R3-1 (dup fee overwrite gap) — closed. card_ext_duplicate_final_credit overwrite on card_evt_late_and_returned_fees: the late fee of the first statement is credited inside the final credit only where the late fee carried by the error is above zero; where it is nothing (second billing-error dispute on that statement, notice before the close or after the due date) and for every other fee the base reversal sentence is restated in force. Rule sentence and replaced_by carry the same text. Probe: second dispute on 2026-06-09 -> final credit 1389.69 with the fee left to the base billing_error reversal; notice before close -> 1379.25, base reversal in force.
- R3-2 (catch-up same-day tie) — closed. Mailed tier now reads "the most recent of them, and of two credited the same day the one entered first in the account history"; shortfall_measure ladder and compute_basis carry it verbatim. Probe (return removed, mail 60.00 + online 50.00 credited 2026-10-12): mail entered first -> 222.16, online entered first -> 162.16, both as the rule states.
- R3-3 (base minimum) — closed for the catch-up and the line wait with one shared definition: the minimum payment due on the missed statement is the printed minimum less the base exclusion: with exactly one billing-error dispute recorded on a transaction that statement first showed, still open with no resolution entry and received after its close, two steps (min-pay percentage of the disputed amount off the printed minimum, floored at the tier floor, never above the printed minimum); with two or more such disputes the statement is left to the investigation (catch-up nothing, the line does not wait on it); otherwise the printed minimum. Decision (DSL limit, recorded): per-dispute open status and notice-after-close cannot be summed across several disputes, so the two-or-more case is scoped out explicitly rather than read from the most recent one only. Line prerequisite condition updated. Probes (task0 world after the dup write): auditor world (2468.41 received 2026-09-15 on 2026-09-09) -> minimum 110.82, catch-up 247.48, line refused until 110.82 is paid, then 5200.00; resolved dispute -> printed (319.49); notice before close, network-only track, dispute on another statement -> printed minimum (decoys); two disputes -> catch-up 0, line 5200.00; small 10.00 dispute -> 135.40 minimum. Task0 values unchanged (no billing-error dispute on a transaction the 2026-09-09 statement first showed): 1421.69 / 319.49 / 5200.00.
- R3-4 (refund realism) — closed. dispute_interest_exposure removed (network-only tier and latest-dispute selection struck). New parameter factor merchant_credit_hold: the most recent merchant credit (same-day tie: entered first) is held 30 days when posted by a merchant other than Northgate and no purchase on the account carries the reference it credits (card networks require a merchant to credit the account that was charged, so an unmatched credit is verified first), 7 days when an outside merchant credits a purchase on the account (the company's own standing period, inside the 7 business days Reg Z 1026.11(a)(2) allows after a written request), nothing for Northgate's own or Marketplace credits, which Northgate books against its own return records. Reg Z check: the overwrite now states held amounts are refunded once released "and in every case within the base number of business days of a written request" (comment 11(a)-1.iii lets the issuer set its own practice for oral requests; written requests keep the base timing). Refund keeps 4 factors (clearing_period, open_dispute_hold, merchant_credit_hold, residual_interest_hold). Seed: task1 gains a 16.47 Publix return credit (2026-10-27) against the 2026-09-20 Publix purchase 58.12 (card category, charter-produced, ledger re-derived by gen1; statements unchanged, balance -876.47). Gold refund 286.58 = 899.49 - 408.04 - 186.40 - 16.47 - 2.00; T1 baseline substitution -> 303.05; T2 tier rests on the seeded credit and the matching purchase. Courtesy 23.02 unchanged. Persona: the Publix return is mentioned only if asked.
- R3-5 (ladder text) — closed as a class: every ladder `when` in all five policies is now a verbatim substring of its rule (mechanical check: 0 non-verbatim), and every text value/method is verbatim except the settled_principal duplicate-excess line, which joins the rule's two verbatim sentences. tier_taken strings in both tasks were remapped to the new ladder texts.
- O-11 kept: the order holdings carry amount_paid; no read touches order lines, and adding line rows to task0 would open a new seed surface on a passing task. O-12 kept (disputed): an uncleared mailed check does not cure a delinquency until it clears; the catch-up is the amount that cures today. O-13 kept: with no dispute open the second tier is floored at zero, so subtracting no-provisional cardholder resolutions can only lower the hold to zero.

### Probe table (round 4, changed reads)
| read | decoy | absent | second / tie | result |
|---|---|---|---|---|
| dup fee tier | second BE dispute on 06-09 -> fee to base reversal | notice before close -> fee to base reversal | — | 1389.69 / 1379.25 |
| catch-up most recent payment | online entered first | — | same-day mail+online | 162.16 / 222.16 |
| missed-statement minimum | network-only, other statement, pre-close notice -> printed | resolved dispute -> printed | two disputes -> not measured | 247.48 / 319.49 / 0 |
| line minimum | same decoys | — | two disputes -> no wait | 3900 -> 5200 after 110.82 |
| most recent merchant credit | Northgate credit latest -> nothing | no credit (None date) -> nothing; Publix removed -> resort 9 days old not held | same-day second credit -> Publix held; older unmatched not latest | 303.05 / 286.58 / 263.05 (unmatched 40.00 latest) |

### Defining sentences (round 4 changes)
| binding | sentence |
|---|---|
| m_min, s_disp_* (catch-up) | "The minimum payment due on the missed statement is the minimum printed on it, less the amount the base rule excludes while a billing-error dispute stands open: ..." |
| m_min, s_disp_* (line) | "The minimum payment due on that statement is the minimum printed on it, less the amount the base rule excludes while a billing-error dispute stands open: ..." |
| mc_amt, mc_date, mc_age | "The most recent merchant credit is the merchant credit with the latest posting date, and of two posted the same day the one entered first in the account history; its age is ..." |
| mc_type, mc_ref, mc_match, credit_days, credit_hold | "The merchant credit hold follows where the most recent merchant credit came from: ..." |
Sweeps: basis verbatim 0 bad; read-set clean; no stale "exposure", "network-only", old gold figures in tasks; XF points re-checked for the new factor (A1 own reads, B10 tie stated, no rounding needed, trigger list unchanged: tools untouched).
Gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 4: gates 7/7 green

## REWORK round 5 (revision_4 findings R4-1, R4-2; observations O-14..O-17)
Both findings reproduced on scratch copies before editing; neither disputed.
- R4-1 — closed. card_ext_line_increase: the waiting (prerequisite) sentence and the rule now carry verbatim "..., and while that statement carries two or more billing-error disputes on transactions it first showed and a dispute still stands open on the account, the disputed amounts opened exceeding the amounts that have left dispute status, the increase is not granted: nothing is booked and the request awaits those disputes' investigation."; compute adds acct_open / referral and the result keeps the limit while referral holds; the old "does not wait" clause is gone, the minimum's two-or-more case now falls to the printed minimum. card_ext_catch_up_payment: same referral stated as its own sentence (no catch-up booked until the investigation ends); with two or more recorded disputes and none open on the account the printed minimum applies (base: nothing is excluded once resolved). Decision recorded: per-statement open status cannot be counted from records (resolution rows carry no statement date), so "a dispute still stands open on the account" is the record test. Probes (task0 world after the dup write): two open disputes 10.00 + 12.00 on 2026-09-09 -> catch-up referred (0), line 3900.00 refused, still refused after a 200.00 payment; both resolved -> catch-up 319.49 on the printed minimum, line refused until paid; second dispute network-only -> one billing-error dispute, adjusted minimum (297.39). Task0 gold unchanged.
- R4-2 — closed as a class. Every hold now sums every item of its window (DSL windows are whole months from today, "after the same calendar day one month before today"):
  (b) payment hold -> factor payment_clearing (family parameter, replaces clearing_period): a returned payment in 12 months -> every payment credited in the last month, less returns posted in that month; none returned -> the mailed payments of the last month and those made online / app / phone / automatic payment through a channel no payment in the last 12 months used before that month; otherwise nothing. Probes: second online payment in the month -> both held; established phone payment -> not held; mailed payment -> held. Baseline sentence changed to "Before any hold this rule sets, the credit balance refund is the whole credit balance." (the base refunds the whole credit balance; params base/mail/new-channel/returned clear days removed, hold_months added).
  (a) merchant_credit_hold restated as sums: a returned payment in 12 months -> every outside-merchant credit of the last month; none returned -> the unreferenced outside-merchant credits of the last month (a credit naming no purchase: card networks require a refund to reference the transaction it reverses, and independent terminal credits are the credit-voucher fraud pattern); otherwise nothing. Seed: the 2026-10-27 credit is now an unreferenced 16.47 Bayshore Grill credit (O-15 fixed: own transaction reference, unique across the history). Probes: second unreferenced credit -> both held; unreferenced Northgate credit (decoy) -> not held; 2026-09-29 and 2026-09-30 credits (month boundary, same calendar day excluded) -> not held; no credit -> nothing; returned-payment world -> every outside credit of the month held.
  Class sweep: catch-up shortfall's mailed tier read only the most recent payment -> now "one or more of them were mailed and credited in the last month ... count only once they clear a month after they were credited" (SUM; same-day order no longer matters: mail-first and online-first both 222.16). Remaining most-recent reads are single objects: the duplicate dispute the dup settles, the most recent late fee (missed / courtesy statement), the latest statement and its completing payment (residual), the lateness payment of the fee statement.
  Task1 gold refund 246.58 = 899.49 - 448.04 - 186.40 - 16.47 - 2.00 (the first automatic payment of 2026-10-09 is now held with the first online payment); opening 223.56; factor baselines 694.62 / 432.98 / 263.05 / 248.58. Courtesy 23.02 unchanged. Persona: the Bayshore Grill credit only if asked.
- O-14 kept (the wait needs its own record-visible definition). O-16 kept: the base fee reversal is a base rule left in force; no task world reaches it, so no tool is owed. O-17 closed: settled_principal T2 method is now the rule's verbatim span. All ladder whens/values/methods verbatim (0 exceptions).
Sweeps: basis verbatim 0 bad; read-set clean; no stale Publix / clearing-period / most-recent-credit / old gold text in tasks; XF points re-checked on the changed policies (A1 own bindings: pay_returns_12 and mc_returns_12 are separate reads, acct_open separate from the over-limit binding; B10 ties moot for sums; B11 RND on sums; C16 overwrite unchanged in scope; tools untouched, trigger list unchanged).
Gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 5: gates 7/7 green

## REWORK round 6 (revision_5 findings R5-1, R5-2; observations O-18..O-20)
Both findings reproduced on scratch copies; neither disputed. Charter-only edits; task gold unchanged (task0 1421.69 / 319.49 / 5200.00, task1 23.02 / 246.58).
- R5-1 — closed. The referral now names the missed statement's own billing-error disputes, verbatim in the line rule, its waiting sentence and the catch-up rule: "... carries two or more billing-error disputes on transactions it first showed and the most recent of them, and of two received the same day the one entered first in the account history, still stands open with no resolution entry referring back to it, ...". Compute: referral = s_disp_n >= 2 and s_disp_res == 0 (the account-level acct_open read is gone); line prerequisite condition restated. Decision recorded: resolution rows carry no statement date, so the open status of every dispute of one statement cannot be summed from records; the statement's own most recent dispute is the record test (same-day tie: entered first), and with that dispute resolved the printed minimum applies. Probes (task0 world): auditor's case — both 2026-09-09 disputes resolved, the duplicate dispute of 2026-06-09 still open -> no referral: catch-up 328.34 at the opening, line waits on the printed minimum (3900.00); both open -> catch-up referred (0), line refused; earlier resolved, latest open -> referred; same-day tie, first-entered resolved -> printed minimum (307.49); first-entered open -> referred.
- R5-2 — closed (XF A4). One plain binding returns_12 with its own sentence "The account's payment record is clean when no payment was returned unpaid in the last 12 months."; payment_clearing and merchant_credit_hold both read it ("where the payment record is not clean / where it is clean ..."); pay_returns_12 and mc_returns_12 removed; neither factor lists returns_12 among its bindings. Class sweep: no other selection is computed twice inside one policy (courtesy history/lateness, line conduct/usage, catch-up tiers each read their own or shared plain bindings). Probes: returned payment on 2026-05-02 -> both holds switch to their first tiers together; return on 2025-10-30 (same calendar day twelve months back) -> outside, gold unchanged.
- O-19 — merchant_credit_hold relabelled method (its tiers add different record sets). payment_clearing stays parameter: its decided value is the payment set held (every payment of the last month / mailed and first-used-channel payments / none) over one record kind, and the skill floor requires two parameter factors (EXTENDED gate fails at one).
- O-20 — closed by the schema: card_events.original_transaction_reference is "12 uppercase letters and digits, or empty"; the rule now says "an unreferenced merchant credit is one whose purchase reference is empty" and the test matches that exact value.
- O-18 kept: ordering stays unique (line <- catch-up <- dup); the referral is a refusal clause on the same waiting sentence, no second terminal state.
Sweeps: basis verbatim 0 bad; read-set clean; ladders verbatim; no stale "a dispute still stands open on the account", pay_/mc_returns_12, "names no purchase" in tasks or charter; task texts (tier_taken, factor traces, both rationales) updated.
Gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 6: gates 7/7 green

## REWORK round 7 (revision_6 findings R6-1, R6-2)
Both findings reproduced; neither disputed. Charter-only edits; task gold unchanged (task0 1421.69 / 319.49 / 5200.00, task1 23.02 / 246.58).
- R6-1 — closed with the coordinator's coarse exact record test. One referral sentence, verbatim in the catch-up rule and in the line-increase rule, where it follows the waiting sentence as its second sentence: "While the missed statement carries two or more billing-error disputes on transactions it first showed, whether resolved or not, the catch-up payment and a requested credit line increase are referred to the disputes team: nothing is booked and the customer is handed over to a human representative because no published policy resolves the request in this conversation." (the hand-over is the share tool's no-policy reason; the code token itself may not appear in a policy sentence — EXTENDED leak check — so it is stated in business words). The most-recent-open test and the "until the investigation ends" purpose clause are gone; compute referral = s_disp_n >= 2 (an exact count of billing-error disputes with that statement date, resolved or not). Exactly one such dispute keeps the base exclusion (two-step minimum). Line waiting sentence now names the missed statement ("..., the missed statement, is met in full ..."); prerequisite condition restated. No task world reaches the referral (no billing-error dispute on the 2026-09-09 statement in task0; task1 does not claim these policies), so no gold calls the hand-over tool.
  Probes (task0 world after the dup write): auditor's case 1000.00 open + 12.00 resolved on 2026-09-09 -> referred (catch-up nothing, line limit unchanged); both resolved with the duplicate dispute open elsewhere -> referred; both open -> referred; same-day pair -> referred; second dispute network-only or on another statement (decoys) -> one billing-error dispute, two-step minimum (catch-up 297.39); exactly one open -> 247.48; exactly one resolved -> printed (319.49).
- R6-2 — closed. merchant_credit_hold relabelled parameter (O-19 retracted by the auditor); refund floors 3 parameter + 1 method (residual_interest_hold); ladder keys back to value; task1 factor trace label and rationale updated.
Sweeps: basis verbatim 0 bad; read-set clean; ladders verbatim; no stale "until the investigation ends", "most recent of them", "awaits those disputes", old waiting-sentence quote or method label in tasks; task0 rationale quote of the waiting sentence refreshed.
Gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 7: gates 7/7 green

## REWORK round 8 (revision_7 finding R7-1; observation O-21)
R7-1 reproduced (the line's waiting text and the catch-up rule carried the same referral sentence, which named the line increase); not disputed. Charter-only edits; task gold unchanged (task0 1421.69 / 319.49 / 5200.00, task1 23.02 / 246.58).
- R7-1 — closed. Each rule now states its own referral for its own outcome:
  catch-up rule: "While the missed statement carries two or more billing-error disputes on transactions it first showed, whether resolved or not, the catch-up payment is referred to the disputes team: no catch-up payment is booked and the customer is handed over to a human representative because no published policy sets the payment in this conversation." (no mention of the credit line);
  line rule (its own sentence after the waiting sentence, not part of it): "A requested credit line increase is not granted, and is referred to the disputes team, while the statement for which the most recent late fee was recorded carries two or more billing-error disputes on transactions it first showed, whether resolved or not: no limit change is booked and the customer is handed over to a human representative because no published policy decides the increase in this conversation."
  The line's prerequisite policy_source is back to the single waiting sentence ("A requested credit line increase is granted only after the minimum payment due on the statement for which the most recent late fee was recorded, the missed statement, is met in full by the payments recorded against that statement that were not returned unpaid."). Neither referral sentence contains the other or the waiting sentence. Compute unchanged (referral = s_disp_n >= 2 in each policy, each basis quoting its own sentence).
  Class sweep (check 6) over every edge: line -> catch-up, catch-up -> dup, refund -> courtesy — no depended-on rule restates the blocked rule's prerequisite sentence; the catch-up rule names no line-increase outcome (its only "credit limit" mentions are its own over-limit restoration).
- O-21 — closed: the route clause is gone from the line's edge condition, which now states only the payment test with the one-dispute exclusion; the referral lives in the line rule's own sentence.
Probes (task0 world after the dup write) unchanged from round 7: two or more billing-error disputes on 2026-09-09 (open, resolved, mixed, same-day) -> both referred; network-only / other-statement decoys -> two-step minimum; one open -> base exclusion; one resolved -> printed.
Sweeps: basis verbatim 0 bad; read-set clean; ladders verbatim; no stale shared-referral wording in tasks; task0 rationale updated.
Gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 8: gates 7/7 green

## REWORK round 9 (renderer scan-first STOP, render_source/store_card_billing_and_disputes/render_r1.md: M1-M4, P1-P3)
All four mismatches reproduced by reading compute against the rule words; none disputed. Charter-only edits; every computed value unchanged (task0 1421.69 / 319.49 / 5200.00, task1 23.02 / 246.58; all factor baselines unchanged — COMPUTE OK).
- M1 closed: card_ext_catch_up_payment restoration fee tier now reads "... less the fee reversals posted in that time, never less than zero, a month counted back ..." (compute MX(0, ...)).
- M2 closed: card_ext_credit_balance_refund not-clean tier now reads "... less the returned payments posted in that month, never less than zero;" (ladder value carries it).
- M3 closed: card_ext_line_increase low-use tier now reads "... less the payments returned unpaid in that time, that difference never less than zero, rounded half up to the cent;".
- M4 closed: both usage tiers state "rounded half up to the cent" (compute RND(... + 1e-9, 2) before the whole-hundred round-down).
- Class sweep (B10/B11) over every compute binding with MX/MN/RND: the remaining unstated floors were the standing late fee in the dup and the catch-up and the courtesy standing part (MX(0, fee - reversals)) — each sentence now says "never less than zero". Remaining RND(...) calls on sums/differences of cent amounts are exact cent arithmetic (no rounding effect) and need no words; every rounding of a product (percent, rate x days) already states "rounded half up to the cent"; credit balance ("nothing when the account owes money"), duplicate excess, correct part, shortfall and dispute hold already state their floors; adj_min states its floor ("the floor is used instead") and "never more than the printed minimum" is stated in the catch-up / line minimum.
- P1 closed: dup post_date and carried_interest moved into carried_error_days bindings (carried_interest's sentence names the carried-error days).
- P2 closed: courtesy fee_due into lateness_points, fee_paid into coverage_points.
- P3 closed: refund latest_stmt and latest_paid into residual_interest_hold.
- Placement class sweep (A3/A4): mechanical check of every plain binding's transitive consumers — no other plain binding is used by a single factor; the only plain bindings reading factor bindings are the assembly bindings raw_limit (line) and share (courtesy), which combine every factor like result (A2).
Sweeps: basis verbatim 0 bad; read-set clean; ladders verbatim; no task text quotes a changed sentence in its old form.
Gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 9: gates 7/7 green
