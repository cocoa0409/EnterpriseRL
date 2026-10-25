# Worklog: env_0062 credit_card_promotions (M=2), round 3

The draw is unchanged: task 0 prerequisite_problems=1, factor_counts=[4,5]; task 1 prerequisite_problems=2, factor_counts=[5,6,4].
The blueprint is frozen. All changes are in card.extended.yaml, tasks/{0,1}.json and this worklog. task_tools.py is unchanged in round 3.

## Policies and tools

| policy | trigger / subject | tool (owner) | task |
|---|---|---|---|
| card_ext_courtesy_fee_credit | state_due / card_fee_reversal on a late fee | apply_courtesy_fee_credit_68b22b43 (agent) | 0 |
| card_ext_statement_minimum_payment | on_request / card_payment | pay_statement_minimum_b2a1a039 (user) | 0 (root) |
| card_ext_returned_fee_courtesy | state_due / card_fee_reversal on a returned payment fee | credit_returned_payment_fee_d3814d72 (agent) | 1 |
| card_ext_deferred_interest_assessment | state_due / card_deferred_interest_assessed | assess_deferred_interest_7b31b265 (agent) | 1 |
| card_ext_payment_direction | on_request / card_payment_allocation | direct_payment_to_plan_c5f7b721 (user) | 1 (root) |

Gold values:
- Task 0: courtesy credit 35.00, then minimum payment 116.02 (both unchanged).
- Task 1: returned-fee courtesy 38.00 and assessment 92.71 (the two commute), then the direction 334.81. In round 2 these were 38.00, 88.59 and 356.79.

## Round-3 closure list

- **R2-F1 (the DI rule restated direction <- DI from the wrong side, in action form).** Removed. The scope sentence now reads "On the closing date of the statement that follows the end of a deferred-interest plan's promotional period, Northgate assesses in one row ... and the assessment may be posted at any time on that closing date."
  - No extended rule other than the direction's names the direction.
  - The only statement of each edge is the state-form sentence in the direction's own rule.
- **R2-O3 (DI posting-time wording).** The scope sentence and the overwrite's replaced_by now give one time: "on the closing date of the next statement". Today, 2026-11-10, is that closing date.
- **R2-F3 (a courtesy credit erased a payment's return history).** Removed. returned_hold now counts every payment returned unpaid in the last 6 months: two returns give hold_high 0.25.
  - The courtesy edge now moves the direction through the balance the direction draws on. Today's payments first settle the fees charged for the latest statement and still owed: a late fee for its missed minimum, and the returned payment fee of a payment made toward it and returned unpaid, each less any fee reversal standing against it.
  - Issuers apply payments to fees and interest charges before any excess. A courtesy credit reduces the fee owed, from 41.00 to 3.00, so 38.00 more is available to direct.
  - The gate is the plain binding `fees_owed`. The new prerequisite sentence, in the direction rule, state form: "A payment direction is not fixed until the returned payment fee charged for a payment made toward the latest statement, when it meets the returned-payment courtesy conditions, carries its courtesy credit."
  - Skip run: 302.13 instead of 334.81.
- **R2-F4 (reallocation relief counted from before the payment arrived).** Rebuilt as a real misdirection correction:
  - On 2026-10-28, 300.00 of PMT-326102841 (made toward 2026-10-10) was recorded to the 18-month plan. The 6-month plan was in its last two billing cycles, so the base allocation rule (Reg Z 1026.53(b)(1)(i)) sends the excess to it first.
  - The misdirected total counts against the plan, and interest on it is taken off only from the date of the latest misdirected allocation through the last day of the period, both days counted: 5 days, 1.2119.
  - Nothing is taken off when that date falls after the period ended.
  - The assessment is now 92.71, which is the auditor's real-practice figure.
  - The same "both days counted" wording and the matching +1 day count now also apply to the refund-after-closing tier and the voided-allocation-before-closing tier.
- **R2-F2 (dispute exclusion limited to in-cycle purchases).** dispute_exclusion tier (a) now covers an open dispute on any charge carried in the statement's balance, as Reg Z 1026.13(d)(1) allows the disputed share to be withheld:
  - a purchase posted on or before the closing date, whatever cycle it posted in;
  - a fee other than the cycle's late fee, with no reversal standing against it.
  - Probe: the disputed purchase moved to the August cycle still gives 6.44 off (116.02). Posted after the closing, it gives 0 off (122.46).
- **R2-F5 (statement minimum count).** With dispute_exclusion real again, the minimum keeps 4 factors: minimum_basis (method), installment_component, dispute_exclusion and reversal_refigure. Task 0 stays at [4,5].
- **R2-O4 (mismatched labels on same-shape factors).** reversal_refigure is relabelled parameter. Like dispute_exclusion, it puts an amount into the deductions. The statement minimum's method factor is minimum_basis.
- **R2-O1 (shared courtesy allowance, no order).** Both courtesy schedules' overwrite now says: "late fees and returned payment fees draw on that one allowance in the order they posted, so that when fees of both kinds meet their schedules' conditions and the allowance left covers fewer of them, the fee posted first takes it".
- **R2-O5 ("most recent" first-match reads).**
  - The direction's hold no longer reads the most recent fee.
  - The fee owed is read through the returned payment made toward the latest statement. The rule's scope states at most one such return.
  - The statement minimum drops "only the most recent fee reversal is looked at" and instead scopes the account to at most one fee reversal since the closing and at most one open dispute.
  - The DI scope states that no payment returned before the most recent one carried an allocation to the plan.
  - The two courtesy schedules credit "the most recent" fee by design: each fee is its own state_due event.
- **R2-O2 (hold wording).** The proportional reading is unchanged: holds are capped at one and lowered by the releases, also capped at one.
- **O-3 (the minimum's allocation row is unwritten).** Unchanged by design. It is the overnight back-office posting, noted in 0.json.
- **Persona "double charge" vs a single ledger row (task 0).** The line now reads "you disputed a hardware store charge for an order that was never delivered". The ledger holds one 214.60 row.
- **Ticket without tax.** Every promotional ticket (T-30561847, T-31744208, T-32784410, T-33190265) carries its pre-tax charter total, itemised in seed_consistency:
  - tires: unit price, mounting, TPMS kit or valve stem, disposal and set savings;
  - road hazard at 17% or 12% of the tire price;
  - battery_price and plan_price.
  The tires charter keeps sales tax as a separate POS line outside charter computations; the seed records that line as paid at the counter, so the plan finances the charter total.
- **Factor independence.** Rechecked mechanically for all 5 policies (transitive over plain bindings), with no violations. fees_owed, available, combined shares, corrected balances and results are plain bindings.

## Round-1 items (closed in round 2; still closed)

- **F-1/E-2:** the late-fee schedule and its tool are removed.
- **F-2/E-1:** every result rounds exactly half up with `int(x*100+0.5+nudge)/100`.
- **F-3:** the unreal relief ladders are removed.
- **F-4:** fee_component, ticket_refund_credit and missed_minimum_cover are removed.
- **F-5:** every method factor changes the formula's shape.
- **F-6:** installment_rate is removed.
- **F-7:** factor counts match the draw.
- **Hazard seed:** the refund is 26.60 = 62.40 x 8/12 - 15.00.
- **Observations:** O-1 is moot. O-2: no agent-posted late fee, and the DI posts on its closing date. O-4: recorded accruals are never reversed. O-5 is accepted.
- **E-3 to E-6:** closed.

## Task 0: late-fee courtesy credit -> statement minimum (frozen 2026-10-14 10:20 EDT)

- **Courtesy:** 35.00 on fee 5fbf8049.
- **Minimum:** 68 + 49.51 + 0 + 41.00 - 6.44 - 36.05 = 116.02. The printed minimum is 158.51; without the courtesy credit the minimum is 152.07.
- **Baselines, courtesy:** 41.00, 30.50, 32.00, 33.50, 32.80. All at baseline: 41.00.
- **Baselines, minimum:** minimum_basis 88.02, installment_component 66.51, dispute_exclusion 122.46, reversal_refigure 152.07. All at baseline: 81.00.

### Pairwise method tiers, task 0

| factor | pair | distinguishing input | probe |
|---|---|---|---|
| repeat_fee_basis | (a) vs (b) | another late fee within 3 months (no / yes) | 35.00 vs 24.00 |
| repeat_fee_basis | (a)/(b) vs (c) | fee at the repeat amount (41 / 30) | 35.00 vs 24.00 |
| minimum_basis | (a) vs (b)/(c) | new balance below the payment floor | not reachable on this ledger |
| minimum_basis | (b) vs (c) | rounded percentage above the floor (68 > 40 / not) | 116.02 vs 88.02 |

### Probe table, task 0 (round 3, charter compute through the gate evaluator)

| probe | policy | result | reading |
|---|---|---|---|
| gold | courtesy_fee_credit | 35.0 | 35.00 |
| gold (credit standing) | statement_minimum_payment | 116.02 | 116.02 |
| skip courtesy | statement_minimum_payment | 152.07 | 152.07 |
| decoy: certificate paid by bank card | courtesy_fee_credit | 32.0 | plan bonus one-of-two |
| absent: no late fee at all | courtesy_fee_credit | 0.0 | 0, no crash |
| disputed purchase posted in an earlier cycle (2026-08-20) | statement_minimum_payment | 116.02 | R2-F2: still 6.44 off -> 116.02 |
| disputed purchase posted after the closing (2026-09-30) | statement_minimum_payment | 122.46 | not in the balance -> 122.46 |
| dispute on the cycle late fee, credit standing | statement_minimum_payment | 122.46 | tier (b) off while reversal stands -> 122.46 |
| dispute on the cycle late fee, no credit | statement_minimum_payment | 117.51 | tier (b): the fee off -> 117.51 |
| dispute on the earlier late fee (2026-05-20) | statement_minimum_payment | 121.56 | tier (a): 3% of 30.00 = 0.90 off |
| decoy: dispute closed | statement_minimum_payment | 122.46 | 0 off -> 122.46 |
| absent: no dispute | statement_minimum_payment | 122.46 | 122.46 |
| reversal of an earlier fee | statement_minimum_payment | 152.07 | reversal (b): capped at past due 0 -> 152.07 |
| billing_error reversal of the cycle fee | statement_minimum_payment | 109.84 | reversal (a) 42.23 off -> 109.84 |

## Task 1: returned-fee courtesy + deferred interest assessment -> payment direction (frozen 2026-11-10 10:30 EST, a closing day)

- **Courtesy:** 38.00 on the 41.00 fee of 2026-10-20 (PMT-326101547; replaced 10-23).
- **Assessment:** 92.71 on deferred_6 T-33190265 = 83.17 + 6.7802 + 4.4437 - 0.4728 - 1.2119.
- **Direction:**
  - 900.00 - 3.00 (fee still owed) - 92.71 = 804.29 available.
  - The 12-month plan's 414.98 is served first, leaving 389.31.
  - Holds 0.25 + 0.10 = 0.35; releases 0.40 + 0.20 = 0.60; net 0.35 x 0.40 = 0.14.
  - 389.31 x 0.86 = 334.8066, rounded half up to 334.81.
- **Skip runs:** 302.13 without the courtesy credit, 343.01 without the assessment.
- **Baselines, courtesy:** 41.00, 36.50, 35.00, 35.00, 35.00, 36.90. All at baseline: 41.00.
- **Baselines, assessment:** stub_period 85.93, ticket_refund_link 93.18, voided_allocation 88.27, window_reallocation 93.92. All at baseline: 83.17.
- **Baselines, direction:** window_route 691.69, returned_hold 373.74, channel_hold 350.38, tenure_release 280.30, relationship_release 307.55. All at baseline: 725.72, capped by the plan's recorded balance 1025.72 - 300.00.
- **Order:** the courtesy and the assessment commute.
  - Disjoint reads: the assessment reads no fee or fee-reversal row; the courtesy reads no allocation or accrual row.
  - Probes: the courtesy after the assessment row is 38.00; the assessment after the courtesy row is 92.71.

### Pairwise method tiers, task 1

| factor | pair | distinguishing input | probe |
|---|---|---|---|
| returned_fee_basis | (a) vs (b) | another returned payment fee within 3 months (no / yes) | 38.00 vs 27.00 |
| returned_fee_basis | (a)/(b) vs (c) | fee at the repeat amount (41 / 30) | 38.00 vs 25.50 |
| stub_period | (a) vs (b) | period end after / on the last accrual closing | 92.71 vs 83.17 |
| stub_period | (a)/(b) vs (c) | any accrual recorded for the plan (yes / no) | 92.71 vs 54.99 |
| window_route | (a) vs (b)/(c) | another plan with a recorded balance ends within 61 days (yes / no) | 334.81 vs 691.69 |
| window_route | (b) vs (c) | the named plan itself ends within 61 days, with the minimum unpaid | 691.69 vs 619.45 (minimum 84.00 unpaid: the 10-23 and 10-28 payments removed; 12-month plan moved out of the window) |

### Probe table, task 1 (round 3)

| probe | policy | result | reading |
|---|---|---|---|
| gold | returned_fee_courtesy | 38.0 | 38.00 |
| gold | deferred_interest_assessment | 92.71 | 92.71 |
| gold (both rows standing) | payment_direction | 334.81 | 334.81 |
| skip courtesy | payment_direction | 302.13 | 302.13 |
| skip assessment | payment_direction | 343.01 | 343.01 |
| opening world | payment_direction | 310.33 | both missing |
| courtesy after the assessment row | returned_fee_courtesy | 38.0 | 38.00 (order-free) |
| assessment after the courtesy row | deferred_interest_assessment | 92.71 | 92.71 (order-free) |
| decoy: 36-month certificate paid by bank card | returned_fee_courtesy | 36.5 | protection one-of-two |
| decoy: battery cancelled | returned_fee_courtesy | 36.5 | protection one-of-two |
| absent: earlier returned fee 13 months back | returned_fee_courtesy | 41.0 | history share full |
| first-level fee 30.00 | returned_fee_courtesy | 25.5 | basis (c) |
| absent: no returned payment fee | returned_fee_courtesy | 0.0 | 0, no crash |
| absent: no misdirected allocation | deferred_interest_assessment | 93.92 | realloc 0 -> 93.92 |
| misdirection dated after the period ended | deferred_interest_assessment | 93.92 | amount counts, no interest days -> 93.92 |
| misdirection to the 12-month plan | deferred_interest_assessment | 92.71 | same tier (12-month ends after) -> 92.71 |
| decoy: allocation of the returned payment to the 18-month plan | deferred_interest_assessment | 92.71 | left out of the misdirected total; void tier changes |
| period ended on the last accrual closing | deferred_interest_assessment | 83.17 | stub (b); misdirection after the end |
| absent: no accrual recorded | deferred_interest_assessment | 54.99 | stub (c) |
| refund paid after the last closing | deferred_interest_assessment | 93.01 | refund (b), both days counted |
| absent: no plan ended | deferred_interest_assessment | 0.0 | 0, no crash |
| plan already assessed | deferred_interest_assessment | 0.0 | 0 (E-4) |
| billing_error reversal instead of courtesy on the fee | payment_direction | 337.39 | fee fully reversed -> 0 owed |
| late fee for the 2026-10-10 statement, no credit | payment_direction | 299.55 | fees owed 44.00 |
| decoy: returned fee of a July payment only | payment_direction | 337.39 | July fee belongs to an older statement -> 0 owed |
| one return in 6 months | payment_direction | 350.38 | hold_low |
| 12-month plan ends outside the window | payment_direction | 691.69 | route (c) |
| phone channel today | payment_direction | 342.59 | channel phone |
| decoy: alignment plan paid by bank card | payment_direction | 321.18 | relationship one-of-two |
| absent: no payment today | payment_direction | 0.0 | 0, no crash |

## Gates (final run, whole difficulty, round 3)

check_extended OK; check_task_tools OK; replay_tasks OK (0.json 14 acts, closure 42/42; 1.json 17 acts, closure 86/86); check_solvability OK; check_compute OK; check_grounding OK; check_cross_fire OK. check_traceability flags only the unlock tool names, as expected. draw_counts: [1, (4,5)] and [2, (5,6,4)].

## Round 4 (renderer M1-M13, KB audit S1/S2/S5/S6/S7/S8)

No scored value moved. Gold and skip runs were re-verified by replay:
- task 0: 35.00 / 116.02, skip 152.07;
- task 1: 38.00 / 92.71 / 334.81, skips 302.13 and 343.01.

All factor baselines are unchanged.

Closure list:
- **M1/S6 (direction baseline):** the baseline rule now reads "The part directed is the amount available to direct, all of which reaches the named plan with no share of it held back, never more than the named plan's recorded balance". This equals the compute with every factor at baseline (725.72).
- **M2 (plan that ends last):** `t_plan` now picks the plan with the latest end date, taking the longer plan on a tie, and the rule says so. `w18_rem` was added so that an 18-month plan ending in the window is served first when another plan is named.
  - Probes: a 12-month plan ending last is named and capped at 414.98; on a tie the 18-month plan is named (691.69); with the 18-month plan in the window the result is 67.57.
- **M3/S7 (holds "lowered by" the releases):** the rule now states the multiplication. Each hold adds its share to the held share, which is never above one. Each release takes its fraction of that held share off it, the fractions together never above one, "so the held share is multiplied by one less their total".
- **M4/S2 (below-floor branch):** the tier now reads "the core is the whole new balance and it is the whole minimum, with nothing added to it and nothing taken off it but the payments made toward the statement since it closed". This matches the compute. Probe: 30.00.
- **M5 (reversal "otherwise" branch):** the second tier now requires the reversed fee to be posted on or before the closing date (new binding `r_fdate`); otherwise nothing is taken off. The rule says the same.
- **M6 (past due):** "never less than zero" is added to the rule.
- **M7 (reallocation cap and the 18-month plan):** the second branch now states "again never more than this plan's recorded balance", and `o18_rem` was added. Probe: an 18-month plan ending in between gives 93.92.
- **M8/M13/S1 (assembly names factor quantities; scope lines enumerate factor evidence):** each policy's assembly is now stated once, generically, against quantities defined in its own baseline:
  - courtesy schedules: the part credited outright, the share and the credit basis;
  - minimum: the core and the amounts added or taken off;
  - assessment: the interest added or taken off, and the plan's balance left;
  - direction: what reaches the named plan and the held share.

  Each factor sentence says how its own quantity enters. The scope clauses moved into the factor or plain sentences they concern (dispute, reversal, voided allocation, fees owed). The replaced_by sentences no longer name corrections or the dispute part. The assessment's balance effects are now the factors' own bindings (`refund_bal`, `void_bal`; `realloc_int` sits inside window_reallocation), so each factor contributes on its own.
- **M9 (bindings read only by factors):**
  - fee_stmt now belongs to fee_weight_bonus, and fee_ref to payment_weight_bonus.
  - ep_rate, ep_mrate and ep_fixed belong to installment_component, and the fixed-payment sentence moved into its rule.
  - p_start belongs to stub_period.
  - q6_id, q12_id, q18_id and t_exp belong to window_route.
  - A mechanical check found no other plain binding read by one factor only. `available` is the baseline quantity itself.
- **M10/S5 (overwrites retiring clauses still in force):**
  - card_evt_statement: replaced_by now carries the printed-minimum clause in full for every statement, then says the desk's payment is figured here, with the 36/48-month or several-24-month exception. "Remains under the statement rule" is gone.
  - card_evt_payment_allocation: replaced_by carries the instruction clause in full ("the instruction is the cardholder's own request and applies from the next payment that posts after it is submitted"), with the same-day direction as the exception.
- **M11/S8 (docstrings):** all five tools now say that they write only their one ledger entry and change no other record. The stored balance field is not updated. check_task_tools stays green.
- **M12 (rounding constants):** half_up_nudge and round_tolerance are removed. Results use `int(x*100 + 0.5)/100`. The round-ups use integer cents with floor division: `-((-(cents*pct))//100)` and `-((-pct_raw)//10000)`, and the fixed payment uses `-((-(x*100))//1)/100`.
- **S3/S4 (base):** left as is, as instructed. **E1 (document placement):** for the renderer.
- **Factor independence:** [] for all 5 policies.

### Probe table, round 4 (touched items)

| probe | policy | result | reading |
|---|---|---|---|
| M2: 12-month plan ends after the 18-month plan | payment_direction | 414.98 | named plan = 12-month (ends last); 18-month outside window |
| M2: tie on end date | payment_direction | 691.69 | longer (18-month) named; 12-month outside window |
| M2: named 12-month with 18-month ending in window | payment_direction | 67.57 | w18_rem served first |
| M7: 18-month ended between closing and period end | deferred_interest_assessment | 93.92 | o18 branch |
| M5: reversal of a fee posted after the closing | statement_minimum_payment | 152.07 | nothing off (was MN(30, past due 0) = 0 anyway) |
| M4: new balance below floor | statement_minimum_payment | 30.0 | whole new balance less payments since closing |
| gold minimum | statement_minimum_payment | 116.02 | 116.02 |
| gold direction | payment_direction | 334.81 | 334.81 |
| gold DI | deferred_interest_assessment | 92.71 | 92.71 |

REWORK round 4: gates 7/7 green
