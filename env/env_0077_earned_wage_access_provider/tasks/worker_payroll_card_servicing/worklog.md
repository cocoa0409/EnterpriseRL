# worklog — worker_payroll_card_servicing (card), M=2

Running log. The XF_recipe tables live in this file (section "XF tables"); each task's design_rationale carries its own dossier.

## Round 1
- Read inst_common.txt, XF_recipe.md, owner_ruling.md, blueprint card/access charters, schema, share tools.
- Draws: task 0 {prereq 2, factors [6,4,6]}, task 1 {prereq 2, factors [4,4,5]}.
- Constraint finding: within the claimed card events the only base cardholder act (card_close) carries no computable
  number, and every problem must compute with 4-6 factors. Route: the owner=user write is the cardholder's own signed
  written statement on a claim reported by phone (owner_ruling (c)), whose same-category consequence is the provisional
  credit owed on the claim (Reg E: a provisional credit is not owed for an oral notice whose requested written
  confirmation never arrives). Recorded in task 0 rationale.
- DSL constraints shaping the design: no business-day arithmetic (Paystride's own 5-calendar-day loss-report window,
  at least as generous as Reg E's two business days, declared as an overwrite); no joins (claims selected by exact
  status/channel/loss-date keys; one earlier claim per loss read); worker tasks cannot read the employer customer row
  (customers finder only at step 0), so the employer's paycard program and program agreement are seeded with
  customer_id empty (FK-safe; decision recorded).
- Task 0 written: card_ext_error_claim_final_credit (6) -> card_ext_claim_credit_reversal (4) -> card_ext_signed_loss_claim_credit (6, user).
  Values: final credit 117.74, reversal 55.64, signed claim credit 157.55.
- Task 0 per-task gates (2026-10-23): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (233/233 closure), SOLVABILITY OK,
  COMPUTE OK (3 comps, 16 factors, 2 cross), GROUNDING OK, SCOPE OK. check_traceability (pre-render): only the three
  unlock tool-name misses (expected before docs exist); every other argument copied from a reachable return.
- Fixes during task 0: retry selector compared float daily_sequence (int() added); absent-record guards on DAYS reads;
  selector tie wording ("most recently noticed"); retry wording = "the card debit posted right after it"; held-back
  amount scoped to a single active Access plan; employer customer row dropped (finder-once rule); closure reads added
  (paycard program, service orders, program agreement, Access earnings).

## XF tables — task 0

### Defining-sentence table
| term | defining sentence (rule) | used by |
|---|---|---|
| claimed transfer | "The claimed transfer on a signed claim is set by the ATM owner surcharge rebates ..." | sl_transfer_basis; assembly |
| liability limit for the signed claim | "The liability limit for the signed claim follows the loss record and the timing ..." | sl_liability_limit; assembly |
| liability already charged on the same loss | "The liability already charged on the same loss is read from ..." | sl_prior_liability; assembly |
| Paystride fees credited back | "The Paystride fees credited back with a signed claim depend on the network ..." | sl_fee_return |
| no-transaction ATM fees credited back | "The no-transaction ATM fees credited back with a signed claim are those posted on ..." | sl_day_fees |
| service allowance | "The service allowance on a signed claim follows the calendar days ..." | sl_service_allowance |
| reversed claim's transfer | "The reversed claim's transfer is set by ..." | rv_transfer_basis; assembly |
| liability limit behind the reversal | "The liability limit behind the reversal follows ..." | rv_liability_limit; assembly |
| remainder carried into the reversal | "The remainder carried into the reversal comes from ..." | rv_carried_remainder |
| amount held back from the reversal | "The amount held back from the reversal follows ..." | rv_access_holdback |
| undelivered cash amount | "The undelivered cash amount is set by ..." | uc_cash_basis |
| Paystride fees returned / no-transaction fees returned / retry cost / early pay cost / late-credit allowance | one sentence each in the final-credit rule | uc_fee_return / uc_day_fees / uc_retry_cost / uc_early_pay_cost / uc_late_allowance |
Assembly sentences ("The adjustments below ...") name no factor quantity beyond the defined terms above and are stated once per rule.

### Factor-reads table (transitive; xf_check.py)
Every factor of the three policies reads only plain selections (claim id, transaction id, dates, debit type, network,
Access fields); no factor reads another factor's binding directly or transitively.

### All-pairs method tier table
| factor | pair | distinguishing input |
|---|---|---|
| sl_transfer_basis / rv_transfer_basis / uc_cash_basis | (rebate >= surcharge) vs (rebate < surcharge) | owner-surcharge field vs rebate amount |
| same | (rebate >= surcharge) vs otherwise | adds the surcharge input |
| same | (rebate < surcharge) vs otherwise | adds the rebate input |
| uc_retry_cost | (retry with fee) vs (retry without fee) | adds the retry's Paystride fee |
| uc_retry_cost | (retry without fee) vs none | adds the retry surcharge less rebate |
| uc_retry_cost | (retry with fee) vs none | adds both inputs |

### min/max shapes, T1/T2
- Signed claim credit: liability = MN(transfer, MX(0, limit - borne)) in plain assembly. T1 (task world, each alone): limit 607.55, borne 107.55, transfer 161.05 vs 157.55. T2: with every other factor at baseline (limit 50, borne 0) the late limit gives MN(603.80, 500) instead of 50; borne at 50 with limit 50 gives 0 instead of 50; transfer moves the credit by the netted rebate.
- Reversal: result = MN(owed + carry, room). T1: hold 57.50, transfer 54.00, limit 7.50, carry 53.50 vs 55.64. T2: hold bites in any world where the balance less the hold is below what is owed; each owed factor bites in any world where the room exceeds what is owed.
- Final credit: no min/max over factors (sum).

### Decoy / absent-record probe table (probe_t0.py, scratch copies)
| read | probe | result |
|---|---|---|
| signed claim selector | phone claim absent | 0.00 (no claim priced) |
| signed claim selector | older phone claim, same fields | 157.55 (latest noticed kept) |
| earlier claim of the loss | absent | 107.55 (nothing already charged) |
| earlier claim of the loss | resolved claim of another loss, later notice | 157.55 (loss date filter excludes it) |
| reversal selector | no provisional credits | 0.00 |
| June remainder | June claim absent | carry 0 |
| Access hold | Access plan absent | hold 0 (reversal = balance) |
| final-credit selector | claim absent | 0.00 |
| early pay cost | Access plan absent | 114.75 (cost 0) |
| retry | next debit that day is a purchase | 115.54 (no retry cost) |

### Events written by the tools, with base triggers
- card_provisional_credit (+ card_disputes.written_confirmation_date update): triggers [].
- card_provisional_credit_reversal: triggers [].
- card_final_credit: triggers [].
No tool writes an event whose triggers land in another category.

### compute_basis verbatim sweep
xf_check.py: every compute_basis quotation is a verbatim sentence of its own rule; every baseline sentence is in the
rule; every overwrite replaced_by is in the rule.

## Task 1 (written 2026-10-23)
- Tree: card_ext_withdrawn_claim_reversal (root, user, 4) <- card_ext_written_cash_claim_credit (4) and
  card_ext_unauthorized_cash_claim_credit (5); both edges value_input through the balance the withdrawal reversal
  can take; the two credits commute. Values: provisional 107.50, final 112.25, withdrawal reversal 88.30.
- Charter changes made for task 1, propagated to task 0: the claim-credit reversal's prerequisite sentence now waits
  on "every final credit and every overdue provisional credit owed on the account's other claims" (same credits the
  withdrawal reversal waits on); its scope names unauthorized-transaction claims; sibling overwrite tails of the
  shared base clauses (provisional amount, final credit/fee correction, dispute-error correction, liability) now
  name every sibling case (C3). Task 0 rebuilt and re-gated; its values are unchanged.
- check_solvability treats a base gate quoted in any overwrite as retired difficulty-wide: the withdrawal reversal
  retires reversal_status/reversal_notice, so task 0 keeps them in base_preconditions only (no temporal entry).

## XF tables — task 1
### Defining-sentence table
| term | defining sentence | used by |
|---|---|---|
| fee refunds taken back | "The fee refunds taken back with a withdrawn claim are ..." | wd_fee_refunds |
| day-fee refunds taken back | "The day-fee refunds taken back with a withdrawn claim are ..." | wd_day_refunds |
| remainder carried into the withdrawal reversal | "The remainder carried into the withdrawal reversal comes from ..." | wd_carried_remainder |
| amount held back from the withdrawal reversal | "The amount held back from the withdrawal reversal follows ..." | wd_access_holdback |
| undispensed cash on the written claim / Paystride fees returned with a written cash claim credit / no-transaction fees returned with it / overdue-credit allowance | one sentence each | wc_* factors |
| card-in-hand claimed transfer / liability limit on a card-in-hand claim / fees returned / no-transaction fees returned / late-credit allowance on a card-in-hand cash claim | one sentence each | ch_* factors |
### Factor-reads table (xf_check.py): no factor reads another factor's binding, directly or transitively.
### All-pairs method tiers
| factor | pair | distinguishing input |
|---|---|---|
| wd_fee_refunds | international vs out-of-network | two refunds (international + foreign fee) vs one |
| wd_fee_refunds | out-of-network vs none | adds the refund input |
| wc_cash_basis / ch_transfer_basis | as in task 0's transfer bases | surcharge field vs rebate amount vs none |
### min/max shapes, T1/T2
- Withdrawal reversal = MN(owed, room). T1: fee 86.80, day 88.05, carry 82.25, hold 88.55 vs 88.30 (room binds, each owed factor lowers owed below the room under its baseline). T2: hold bites wherever the balance less the hold is below what is owed; each owed factor bites wherever the room exceeds what is owed.
- Card-in-hand credit liability = MN(transfer, limit). T1: limit 62.25 vs 112.25. T2: with every other factor at baseline the limit alone moves the credit from 53.00 to 103.00.
### Decoy / absent probes (probe_t1.py)
| read | probe | result |
|---|---|---|
| withdrawn claim selector | claim absent | 6.30 (carry only; no claim to withdraw) |
| withdrawn claim selector | older open unauthorized claim | 88.30 (latest noticed kept) |
| carry | June claim absent | 82.25 |
| hold | Access plan absent / autorecovery not authorized | 88.55 (nothing held back) |
| written cash claim selector | claim absent | 0.00 |
| card-in-hand selector | claim absent / decoy with a loss date | 0.00 (loss-date filter excludes a lost-card claim) |
### Events written with base triggers
card_provisional_credit_reversal (+ card_disputes.dispute_status update), card_provisional_credit, card_final_credit: all triggers [].
### compute_basis sweep: all quotations verbatim in their rules (xf_check.py); baselines and replaced_by sentences in rule.

## Final gate block (2026-10-23, no --task)
- check_extended: EXTENDED OK
- check_task_tools: TASK TOOL CONTRACT OK (6 tools)
- replay_tasks: REPLAY OK (0.json 233/233, 1.json 262/262)
- check_solvability: SOLVABILITY OK
- check_compute: COMPUTE OK (suite branches 66.50, steps 17.00, history max 23, branch max 79)
- check_grounding: GROUNDING OK
- check_cache_diff: CACHE-DIFF INFO (optional)
- check_cross_fire: SCOPE OK
- check_traceability (pre-render): only the six unlock tool-name misses (expected before docs exist)
Frozen times: task 0 "2026-10-22 10:40:00 EDT"; task 1 "2026-10-23 14:15:00 EDT".

## Round 2 rework (2026-10-23) — redesign log
- Audit revision_1 read in full (_difficulty.md, 0.md, 1.md). Every struck ladder class was removed from every policy; the six policies were rebuilt as the lost/stolen card claim schedules of two plan families (Premier+Elite: task 0; Advantage: task 1), each family = signed claim credit (owner user, root) <- reversal of the excess provisional credit <- final credit on another lost/stolen card claim.
- Old policies card_ext_withdrawn_claim_reversal, card_ext_written_cash_claim_credit, card_ext_unauthorized_cash_claim_credit and their tools were retired; new Advantage policies/tools: card_ext_advantage_* / sign_card_theft_claim_form_2dc05390, take_back_card_claim_excess_b240170d, post_card_claim_settlement_5bc5acd3. Tools now also refuse a card on another plan family (docstring scope enforced).
- Business days are computed exactly in the DSL (weekday ordinal less 2025-2027 Federal Reserve holidays; tested against a reference counter on 3000 random date pairs).
- Both worlds regenerated from the account opening: payroll load every payday, no debit while blocked, no 0.00 debit, no fee refunds; Access ledger regenerated with tier reviews each payday, fees by tier/destination/band/free instant transfers/fee cap, full payroll-deduction recoveries, availability checked per transfer; early pay goes to an external debit card while the card is blocked or missing.
- Scratch: /tmp/worker_payroll_card_servicing_0077/r2/ (dsl.py, pieces.py, texts.py, pol_*.py, build2.py, world.py, gen_w0/1.py, asm_w0/1.py, ev2.py, run_w0/1.py, task2*.py, cfg0*/cfg1*.py, mk0/1.py, probe.py).

### Defining-sentence table (each policy)
| term | defining sentence | used by |
| claimed transfer / liability / amount withheld (SL) / due (RV) | method (baseline) sentence | assembly |
| liability limit | "The liability limit for ..." | *_liability_limit |
| liability already charged | "The liability already charged on the same loss ..." | sl/tl_prior_liability |
| Paystride fees / free withdrawal used | "The Paystride fees ..." | *_transaction_fees |
| service / late credit allowance | own sentence | *_service_allowance, *_late_allowance |
| new-account / point-of-sale / foreign-initiated | INV definition sentence | *_investigation_allowance |
| report day + replacement reason | report-day sentence (Premier/Elite RV, UC: shared by replacement fees and early pay cost); inside the early pay sentence (Advantage) | *_replacement_fees, *_early_pay_cost |
| business days | business-day sentence | every BD count |

### Factor-reads table (transitive, scripted): no factor binding reads another factor's binding in any policy; report-day bindings are plain and shared (A5). No factor id is a substring of a tool name.

### All-pairs method tier table
- *_transaction_fees: (fees charged less returned) vs (plan out-of-network fee for the free withdrawal used): recorded fee rows vs tariff parameter, distinguishing input fee rows; vs nothing: neither tier is 0 across its domain.
- *_early_pay_cost: (fee less Access reversal) vs (lesser of that and the tier's next-business-day bank fee): adds a min with an Access tariff parameter; vs nothing: as above.

### min/max shapes, T1/T2
- liability = lesser of transfer and (limit less already charged), withheld = lesser of liability and 50.00 (SL): T1 on both task worlds (limit and prior each move the signed credit); T2 any world with a late report and a small prior.
- early pay cost lost-card tier = lesser of fee and bank fee: T1 task 0 reversal (3.29 vs 1.49) and task 1 final credit (2.99 vs 0.99); T2 trivially.
- reversal = lesser of excess and balance: room is plain; on both worlds the excess, not the balance, binds after the final credit (T1 of every reversal factor holds).

### Decoy / absent-record probes (probe.py on task-0 scratch copies)
| probe | result |
| SL: older second phone claim awaiting confirmation | unchanged (latest registered kept) |
| SL: no loss date / provisional already posted / signing past 10 BD | prices nothing |
| SL prior: other claim withdrawn / posted later / Visa purchase | 0 charged |
| SL prior: other claim noticed timely | 50.00 cap |
| SL fees: OON fee absent (free slot) / fee already refunded / in-network | plan fee / 0 / 0 |
| RV: reversal already posted / second resolved claim of the loss | prices nothing |
| RV: claim no longer the latest registered of its report day | replacement fees 0 |
| RV early pay: no outside transfer / fee reversed / later NBD bank transfer | 0 / 0 / bank transfer picked |
| UC: already credited / same-day resolution tie / other plan family | prices nothing |
| UC: no replacement ordered on the notice date | replacement fees 0 |

### Events written by the tools, with base triggers
card_provisional_credit, card_provisional_credit_reversal, card_final_credit (card_transactions) and card_disputes.written_confirmation_date, card_accounts.card_balance — none of these events carries a base trigger; no cross-category write.

### compute_basis sweep: every compute binding has a basis quote verbatim in its rule; every replaced_by and baseline.rule is a sentence of its rule (scripted).

## REWORK round 2 claims
- CG-1 day-fee ladders: removed from every policy (no inquiry/decline-fee factor remains).
- CG-2 lesser-of surcharge "method" and retry ladder: removed; the surcharge rebate is a plain part of the claimed transfer in every method sentence; the method factors are now transaction fees (recorded fees vs plan fee for the free withdrawal used) and early pay cost (fee vs min with the Access tier fee).
- CG-3 fee-kind sums and wd_fee_refunds: removed; one fee factor per policy whose tiers apply different rules (recorded fees less returns / tariff for a used free withdrawal / nothing).
- CG-4 identical-outcome ladders (early pay cost by destination, carried remainders): removed; early pay cost now splits by loss type (stolen: whole fee; lost: capped at the next-business-day bank fee), carried remainders dropped.
- CG-5 Access hold-backs: removed; reversals are limited only by the available balance as the base rule says.
- CG-6 card-in-hand straw liability: card-in-hand claims are out of scope; liability limits follow Visa Zero Liability and the base timely/late caps, no departure from the base liability clause.
- CG-7 factor floors: final credit 6/5, reversal 6/4, signed claim 4/4 real factors; one method factor per computation; cross-difficulty and multi-source factors in both tasks (early pay cost; liability limit).
- CG-8 selectors: every selector keyed on registration moment (no ties) or resolution date with a same-day tie carve-out; scope tests for status, loss date, provisional/final/reversal presence, written-confirmation window, one resolved claim per loss and plan family are in rule and compute; Access tier read by the transfer's own plan id, no single-plan first-match read.
- CG-9 overwrite hygiene: every replaced_by restates the in-force base content for out-of-scope cases, names its own scope and its siblings; no clause retired wholesale; repricing of final credits, reversals and fee returns is declared.
- CG-10 assembly sentences: one generic combination sentence per policy (replacements first, then additions, rounding once), naming no factor quantity.
- CG-11 prerequisite scope: reversal sentences cover only final credits on other lost or stolen card claims, priced by the same family's final-credit policy (the declared resolver); no provisional credit is in their scope, so no reversal/signed-claim cycle.
- T0-1 second UC answer: the final-credit clause overwrite declares this schedule's final credit for its claims; no in-force clause prices it differently.
- T0-2 task-0 factor bounds: closed with CG-1..CG-7 (6/6/4 load-bearing factors on the task-0 world).
- T0-3 RV order sensitivity: the reversal selector no longer follows the latest provisional credit; it takes the most recently registered resolved claim with its own provisional-credit and no-reversal tests.
- T1-1 "written" claim reported in the app: the written-cash policy was retired; task 1 rebuilt on phone claims confirmed by the cardholder's signed form.
- T1-2 card-in-hand claim on a stolen card: card-in-hand scope retired; task-1 claims are lost/stolen-card claims matching their replacement orders.
- T1-3 seed realism: task-1 world regenerated (payroll load every payday, no debit while blocked, no 0.00 debit, no fee refunds, Access ledger with full recoveries and no shortfall); task-0 world regenerated likewise.
- T1-4 task-1 factor bounds: closed with CG-1..CG-7 (5/4/4 load-bearing factors on the task-1 world).
- O-1 allowances: one allowance per timeline (provisional promise, correction deadline, investigation length) tied to Regulation E / plan deadlines.
- O-2, O-3, O-4, O-0.1..O-0.4, O-1.1, O-1.2: scopes rebuilt (no out-of-scope tier), signing docstring kept descriptive, blocks respected in seeds (no debit while blocked), the cycle reading removed with CG-11, personas rewritten with no pre-stated reason, no Access hold-back.
- Gates (final block, no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; check_traceability before docs: only the six unlock tool-name misses.
REWORK round 2: gates 7/7 green

## Round 3 rework (2026-10-23) — audit revision_2 (CG-12..CG-16)
- Read revision_2 of _difficulty.md, 0.md and 1.md in full. Edits are confined to the RED classes; trees, tools, worlds and combination sentences are unchanged except where named below.
- Loss handling (all six policies): a shared plain "loss" sentence and bindings. Each claim's loss is identified by its loss date. The policy prices only when the loss carries at most one other claim. The other claim is found by the loss's total disputed amount less this claim's. The loss counts as reported on the earlier notice date of its claims, and the report is late when it falls more than timely_loss_report_business_days business days after the loss date. The liability limit's late tier and the liability already charged (counted once across the loss in posting order, same-day ties broken by daily sequence) are both keyed on that report. The liability already charged is now part of every policy's liability: a factor in SL/TL, and a plain method term in RV/WR/ZC/YC, where it is 0 on both task worlds.
- Each of the six policies now declares a scoped overwrite of the card_unauthorized_liability "Otherwise liability is ..." sentence. The overwrite restates the base text and names its own scope: the transfer is net of the surcharge rebate, the loss is reported at its earliest notice, and no transfer is charged in full. Sibling schedules are named.
- RV/WR liability baseline is now liability_cap_timely_usd, equal to the ladder's fall-through, and the method sentence says the same.
- Early pay cost "lost" tier: the rule now names the record-held quantity — the next-business-day bank fee of the tier the worker's Access plan holds on the day the credit is figured, as the plan record shows it. The compute is unchanged.
- Fee factors (six): the fee sum filters fee_type to the three enum values the rule names (out_of_network_atm, international_atm, foreign_transaction).
- Service allowances (SL, TL, RV, WR): the top tier is now "more than allowance_high_business_days (8) business days", which can be reached inside the 10-business-day confirmation window.
- Holiday table extended through 2028 (O-6). Task-0 seed: the balance kept on the 2026-09-04 payday was raised so the 2026-09-14 expedited fee posts in full at 15.00. The seed check text now matches.
- Probes (probe.py, probe3.py, on scratch copies):

| probe | result |
| loss reported on time by its first claim, second claim noticed weeks later | limit 50.00, prior 50.00, nothing withheld |
| third claim of the loss | prices nothing |
| other claim of the same disputed amount | prices nothing |
| other claim withdrawn | its notice counts for the report; no liability charged |
| other claim posted the same day, lower / higher daily sequence | counted / not counted |
| claimed card-to-bank transfer carrying its transfer fee | transaction fees 0 |
| reversed claim with the loss's other claim posted earlier | prior equals that claim's transfer |
| earlier probes (selectors, fees, report day, early pay, credited, ties, plan family) | unchanged results, except the extra-claim decoy, which now prices nothing (three claims in the loss) |

## REWORK round 3 claims
- CG-12: service-allowance top tier re-keyed to allowance_high_business_days (8), reachable inside the 10-business-day window; SL/TL keep 4 load-bearing factors with three reachable tiers each (sweep: RV/WR use the same schedule; late-credit and investigation ladders reachable).
- CG-13: the early-pay "lost" cap is now the record-held tier on file (the Access plan record on the day the credit is figured) in all four early-pay factors; rule words equal the compute.
- CG-14: vr/wr_liability_limit baseline equals the fall-through (liability_cap_timely_usd), and baseline.rule states the same; all other factor baselines checked equal to their fall-through.
- CG-15: liability timing is keyed on the loss report (earliest notice among the loss's claims); liability already charged is counted across every claim of the loss (the loss is limited to two claims, otherwise the base rule applies); the departures are declared as scoped overwrites of card_unauthorized_liability in all six policies.
- CG-16: every transaction-fee sum filters fee_type to the three enum values the rule names, in all six policies.
- R2-T0-1 / R2-T1-1: closed by CG-13 (one reading of the early-pay cap).
- R2-T0-2 / R2-T1-2: closed by CG-12 and CG-14.
- O-6: holiday table extended through 2028. O-7: no change (no same-minute ties in either world). O-5, O-8, O-9, O-10: noted, no change (O-8 is a base-level inheritance).
- Gates (final block, no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 3: gates 7/7 green

## Round 4 rework (2026-10-23) — audit revision_3 (CG-15, CG-17)
- Read revision_3 of _difficulty.md, 0.md and 1.md in full. Both tasks passed in revision_3. Edits are confined to the two charter classes, swept across all six policies. Trees, tools, worlds and the combination sentences are unchanged.
- Loss report (CG-15), all six policies: the loss is reported on the card's lost or stolen report day, unless the claim's own notice date comes earlier. The report day is card_service_orders.order_date of the account's most recent card_replacement_order with order_reason lost or stolen, when it falls between card_disputes.loss_learned_date and card_disputes.notice_date; otherwise the report is the claim's own notice_date. The report is late when it falls more than timely_loss_report_business_days business days after loss_learned_date. Coarse exact scope test, stated as a record test with no purpose clause: a claim is priced only when its loss carries no other claim, or when the report is the card's report day and a claim of the loss was noticed that day.
- Liability already charged (CG-17): the "other claim" selector is dropped. Liability already charged is an aggregate over every claim with the claim's exact loss key (same account, same loss_learned_date) that is resolved with an error found, at disputed amounts, up to the limit. The claim being priced is still under investigation, so it is never in that set. The reversal and final-credit policies keep their scope as the only claim of their loss resolved with an error found, so they carry the loss's liability first and nothing is already charged on them. The liability itself is now the lesser of the disputed amount (the base's unauthorized amount) and the limit; the claimed transfer less that liability is never below zero.
- The card_unauthorized_liability overwrites (six) restate the base sentence verbatim and declare their scope: report-day timing, settled claims counted before claims still under investigation, and no transfer charged in full. Each names its sibling schedules. These departures only lower the cardholder's liability.
- The stale cross_category notes in four policies ("Access tier it was booked on") now read "the tier the Access plan holds today".
- Probes (probe4.py):

| probe | result |
| card reported lost on 2026-09-09 with no claim noticed that day | prices nothing (coarse scope) |
| card and first claim reported 2026-09-09 | timely: limit 50, already charged 50, nothing withheld |
| other claim with the same disputed amount | already charged = that amount (no selector, no tie) |
| a second resolved claim of the loss | both counted, capped at the limit |
| other claim still under investigation | nothing already charged |
| single-claim loss, card reported before the claim's notice | report = card report day |
| reversal with a second resolved claim of the loss | prices nothing |
| final credit whose loss predates a later lost or stolen order | report = its own notice |

## REWORK round 4 claims
- CG-15: the $50/$500 tier is timed from the loss report taken from record fields (card_service_orders.order_date of the lost or stolen order, card_disputes.notice_date) against card_disputes.loss_learned_date. The residue the DSL cannot express is scoped out by a coarse exact record test, and the departure is declared in all six card_unauthorized_liability overwrites.
- CG-17: the "other claim" amount-identity selector is removed from all six policies. Liability already charged is an exact-key aggregate over the loss's claims resolved with an error found, and the priced claim is excluded by its own status, with no not-equal filter.
- Revision_3 task passes (tasks 0 and 1): kept. Same trees, tools and worlds; every factor still bears weight. The signed-claim figures moved because liability is now counted on disputed amounts.
- O-11, O-12: noted, no change.
- Gates (final block, no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 4: gates 7/7 green

## Round 5 rework (2026-10-23) — audit revision_4 (CG-15, CG-18)
- Read revision_4 of _difficulty.md, 0.md and 1.md in full. Both tasks passed in revision_4. Edits are confined to the two charter classes, swept across all six policies, following the coordinator's routes. Trees, tools, worlds, scored values and the combination sentences are unchanged.
- CG-15 route, all six policies. The liability limit is timed only for an account in scope. The scope is a coarse exact count by exact event_type and order_reason values: at most one card_replacement_order with order_reason lost and at most one with order_reason stolen, with exactly one of them placed on or after the loss date. Inside that scope, that order's date is the day the loss was reported. Out of scope, the liability overwrite restates the base sentence verbatim and the claim is priced as the base prices it. That base pricing can be computed here only for a purchase under Visa Zero Liability (zero liability, whenever the loss was reported; final-credit schedules). Every other out-of-scope claim books nothing, as the selector sentences state. The round-4 "claim noticed on the report day" test and the fallback to the claim's own notice are removed.
- CG-18 route, all six policies: a new scoped overwrite of the base sentence "Liability is counted once across all unauthorized transactions from the same loss or theft, applied in posting order." Its replaced_by restates that sentence for every claim the schedules do not price. On the schedules' own claims, liability already charged is counted on claims resolved with an error found before any claim still under investigation, whatever their posting order. Sibling schedules are named.
- Probe matrix (probe5.py, scratch copies of the task-0 world):

| probe | result |
| two losses — later-loss signed claim (task world) | in scope; report = 2026-09-14 lost order; priced |
| two losses — earlier-loss Visa purchase claim (task world) | out of liability scope (two orders since its loss date); Visa Zero Liability → no liability; priced |
| two losses — earlier-loss ATM claim (auditor's CG-15 probe) | out of scope → books nothing (base rule applies) |
| earlier loss's order only (later order removed), earlier-loss ATM claim | in scope; report = 2026-08-10 stolen order (timely) → limit 50 |
| a second lost-card order on the account | out of scope → books nothing |
| no lost/stolen order since the loss date | out of scope → books nothing |
| card reported lost within 2 business days (order 2026-09-09) | timely: limit 50, already charged 50, nothing withheld |
| still-investigating claim posted before the resolved one — reversal | resolved claim carries the liability first (declared overwrite) |
| still-investigating claim posted first — signed claim | already charged = the resolved claim's disputed amount (declared overwrite) |

## REWORK round 5 claims
- CG-15: every liability-timing policy is scoped through its self-naming overwrite to an account holding at most one lost and at most one stolen replacement order, with exactly one placed on or after the loss date (exact counts on event_type and order_reason). That order's date is the report day; out of scope the base sentence is restated verbatim and the claim is priced as base, or not booked where base pricing cannot be computed.
- CG-18: a scoped overwrite of the base posting-order sentence in all six policies. It restates the sentence for every out-of-scope case and names its own scope (resolved claims counted before claims still under investigation), so the base sentence is no longer contradicted.
- Revision_4 task passes (tasks 0 and 1): kept. Same trees, worlds and scored values; every factor still bears weight.
- O-13, O-14: noted. The rule prose keeps record terms where the coordinator asked for record-held quantities.
- Gates (final block, no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 5: gates 7/7 green

## Round 6 rework (2026-10-23) — audit revision_5 (CG-19)
- Read revision_5 of _difficulty.md, 0.md and 1.md in full. Both tasks passed in revision_5, and the CG-15/CG-18 closures stay. The change is confined to the liability-scope test, applied to all six policies as the coordinator ruled.
- The replacement-order counts now run over a 12-month window from today: COUNT with within_months=12 on card_service_orders.order_date, by exact event_type and order_reason values. An order counts toward "on or after the loss date" only when it lies inside that window. The report day is that single in-window order's order_date.
- The rule now states that an account with repeated lost or stolen cards within 12 months is referred, under Paystride's program practice, to its card fraud review team, so the schedule books nothing for its claims. Orders 12 or more whole months back never count. The base liability sentence stays restated verbatim in the overwrites, whose tail now says "among its orders of the last 12 months".
- Probe (probe6.py, task-0 world, signed claim and reversal; MONTHS(order_date, today) < 12 is the window):

| extra lost-card order | in window | scope | result |
| 2026-03-20 (5 months before both losses) | yes | out: repeated card losses within 12 months, referred to fraud review | books nothing |
| 2025-11-01 (11.7 months back) | yes | out (repeat-loss referral) | books nothing |
| 2025-10-22 (exactly 12 months back) | no | in | priced as on the task world |
| 2025-09-15 (13 months back) | no | in | priced as on the task world |

- Honest note on the 5-month probe: it is out of scope by design. Two lost-card replacements inside 12 months is the repeat-loss referral condition, not an incidental switch. An older order never switches the schedule off.

## REWORK round 6 claims
- CG-19: the lifetime order count is replaced by a 12-month look-back from today in all six policies. Repeated card losses inside that window are a stated Paystride fraud-review referral (the schedule books nothing), and older orders never affect the schedule. The base liability sentence stays restated verbatim out of scope.
- CG-15, CG-18: closures kept unchanged.
- Revision_5 task passes (tasks 0 and 1): kept. Same trees, worlds and scored values; each task account's orders are one lost and one stolen order inside the window.
- O-15: noted, no change. O-13, O-14: unchanged.
- Gates (final block, no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 6: gates 7/7 green

## Round 7 rework (2026-10-23) — renderer source findings render_r1.md (1–6)
- Read audits/render_source/worker_payroll_card_servicing/render_r1.md in full. The policy audit directory was read as context. Each item was applied to all six policies and all six tools, and no scored value moved.
- Item 1 (floors): every method sentence and baseline.rule now states that the claimed transfer (disputed amount less surcharge rebate) is never below zero. The signed-claim schedules also state that their credit is never below zero, in the method sentence and in the assembly sentence, keeping that sentence's order. The reversal and final-credit floors were already worded.
- Item 2 (single-factor bindings): an automated pass in build2.py moved every plain binding used by exactly one factor into that factor's bindings. Moved: v_posted, v_resolved → vr_investigation_allowance; v_report → vr_liability_limit; v_prov_date → vr_service_allowance; z_posted → zc_investigation_allowance; z_report → zc_liability_limit; w_report → wr_liability_limit; w_prov_date → wr_service_allowance; y_posted → yc_investigation_allowance; y_report → yc_liability_limit. Their defining text moved with them: the reversal and final-credit schedules now keep only the loss scope in their loss sentence, and the report-day and late definitions sit in the liability-limit sentence. The moved bindings' basis quotes point to those factor sentences. The report-day binding's fork was reshaped to keep both liability-limit and early-pay forks multi-source.
- Item 3 (report-day ladders): the report-day order is restricted to lost- or stolen-card replacement orders, in rule and compute (exact COUNT on order_reason that day). Tie rule: when both a lost-card and a stolen-card order fall that day, the stolen-card order is read; two orders of one reason that day mean no report day. A damaged or expiring order never makes a report day.
- Item 4 (framing clause): "when the blocked card could not receive early pay" is removed from all four early-pay sentences.
- Item 5 (dead bindings): s_posted, t_posted, w_posted and w_resolved are removed, as found by the same pass; no other dead binding remains.
- Item 6 (tool contracts): the bodies now enforce what the docstrings claim, with explicit errors. All tools require a lost or stolen card claim (unauthorized_transaction with a loss date). The signing tools also require a phone notice and a claim under investigation. The reversal tools require a resolved claim that carries a provisional credit, and no longer post with an empty related_txn_id. The final-credit tools require resolved_error_found. The claim-form tool's Args say "claim form". Tool names and signatures are unchanged. The prerequisite_closure "tools do not block" text now describes these own-claim checks: none reads other claims' credits or the balance.
- Probe (probe7.py, task-0 reversal): lost order on the report day → lost tier (task world); the same order recoded as damaged → no report day; two lost orders that day → no report day; a stolen order added that day → the stolen order is read.

## REWORK round 7 claims
- render_r1 item 1: both floors stated in rule and baseline.rule for the signed-claim schedules; the claimed-transfer floor stated in all six.
- render_r1 item 2: every single-factor plain binding moved into its factor, with its defining text in the factor's sentence.
- render_r1 item 3: report day restricted to lost or stolen replacement orders in rule and compute, with a stated tie rule.
- render_r1 item 4: framing clause removed.
- render_r1 item 5: dead bindings removed.
- render_r1 item 6: tool bodies enforce the docstring scope with explicit errors; names and signatures unchanged.
- Scored values: unchanged in both tasks.
- Gates (final block, no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 7: gates 7/7 green

## Round 8 rework (2026-10-23) — audit revision_7 (CG-20)
- Read revision_7 in full; the change is confined to the two signed-claim policies (SL, TL). The round-7 closures stay.
- The compute now floors the standard credit before the additions, exactly where the rule places it: result = RND(MX(0, claimed transfer − amount withheld) + Paystride fees + service allowance + 1e-9, 2). The method sentence ("the credit is never below zero") is unchanged. The redundant "never below zero" in the combination sentence is removed (O-17); the sentence keeps its order (replacements first, additions after them, rounded once at the end).
- Class sweep: the reversal and final-credit schedules already floor before their additions, in rule and compute. The claimed-transfer floor is stated in all six.
- Probe, the renderer's Advantage witness (claimed transfer 37.00 = 40.00 less a 3.00 rebate, withheld 40.00, free-withdrawal fee 1.95, no allowance): compute 1.95 = rule words max(0, 37.00 − 40.00) + 1.95. Task worlds unchanged: withheld is below the transfer in both.

## REWORK round 8 claims
- CG-20: in SL and TL, the rule and compute both place the single standard-credit floor before the fee and allowance additions; the redundant floor in the combination sentence is dropped (O-17).
- Round-7 closures (render_r1 items 1–6): kept.
- Scored values: unchanged in both tasks.
- Gates (final block, no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 8: gates 7/7 green

## Round 9 rework (2026-10-23) — KB audit source items SRC-1, SRC-2 (audits/policy_kb/.../_difficulty.md revision_1)
- Read audits/policy_kb/worker_payroll_card_servicing/_difficulty.md, 0.md and 1.md in full. The edits are wording only; compute and scored values are unchanged.
- SRC-1: the lost-card tier of vr_/zc_/wr_/yc_early_pay_cost now reads "the lesser of that fee and nbd_fee_bank_usd of the tier the worker's Access plan holds on the day the credit is figured". That is the rule's wording and the compute's current-tier CPARAM read. Swept every factor ladder, the cross_category notes, the tool docstrings and the task rationale and trace texts: no "transfer's Access tier" or "tier it was booked on" phrase remains.
- SRC-2: in both signed-claim policies (rule, baseline.rule and every quote), the liability now reads "the liability limit less the liability already charged on the same loss, never below zero, or the disputed amount if that is smaller". Only min(disputed, max(0, limit − charged)) can be read from it. The task trace texts use the same form. Swept all six policies: no other "lesser of … less …" phrase remains. The reversal and final-credit wording ("the lesser of the disputed amount and the liability limit") has no subtraction inside and is unambiguous.

## REWORK round 9 claims
- SRC-1: early-pay ladder text aligned with rule and compute (tier held today) in all four factors; stale phrase swept from ladders, notes, docstrings and rationale.
- SRC-2: signed-claim liability sentence rewritten to the single compute reading in rule, baseline.rule and traces; the class is swept across all six policies.
- Earlier closures: kept. Scored values: unchanged in both tasks.
- Gates (final block, no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 9: gates 7/7 green
