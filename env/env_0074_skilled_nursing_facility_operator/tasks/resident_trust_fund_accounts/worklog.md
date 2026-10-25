# worklog — resident_trust_fund_accounts (env_0074)

## Step 0 — difficulty pre-check
- Base trust charter closes: 10 policies, events, schema read. Base computations: interest (ADB formula), transfer cap
  (min of open balance / available), notice level 1800. Base automatic clauses: monthly interest credit (last day),
  quarterly statement (15 days after quarter end), resource notice at 1800 (Medicaid tiers), conveyance within 30 days.
- DSL limits found: no per-row weighting => the base ADB interest formula is not computable in compute; interest is
  therefore kept as an inherited base automatic clause only (seeded worlds post every month's credit; frozen_time is
  chosen mid-month so no credit is owed at the opening).
- Gold writes kept trust-only or to an un-claimed category (ancillary has no difficulty and no task tools), so no
  other difficulty's owed write can be created by a gold write (XF 30).
- Draws: task0 prereq=1 factors [5,4]; task1 prereq=3 factors [5,4,5,4].

## Task 0 — design thesis (claim: 2 policies, 2 tools)
Customer: POA daughter of a Medicaid resident; surface goal: "let Mom's trust account pay what it can toward the
September bed-hold bill". Root R0 (user write): per-bill payment authorization naming the bed-hold charge, amount =
what the account can cover today. The transfer itself is posted by the business office on the business day after
the authorization is signed (stated in R0's rule => no transfer write in this consultation; negative space).
Prereq A0 (agent write, state_due): return to the account of an earlier transfer that paid an ancillary supply
charge a payer covers (retroactive Medicaid approval) — raises the balance R0 reads (value_input).
Tree: R0 -> A0 (value_input, state form: "the account's ledger carries a return for every transfer that paid a
charge a payer covers"). User tool = R0's tool.

## Resume (agent 2) — task 0 gate run on the predecessor's 0.json
- Gates: extended RED (paid_share factor reads no record), replay RED (closure mismatch), solvability RED (DOB not in
  persona; reversal dedup evidence; R0 base gate), compute RED (history not load-bearing), grounding RED.
- XF review of the predecessor design (not caught by gates): A0 baseline returned 0 for every customer and all four A0
  factors multiplied a zero baseline (XF 6 T2 fails, dishonest baseline); A0 world had full coverage, so the honest
  answer is the whole transfer and no factor can bite; R0 split the coinsurance run-up into four factors that multiply
  zero baselines (T2 fails for all four); daily_basis ladder only differs where it is wrong; docstring enum used
  "such as". Decision: redesign both task-0 policies and the world; keep both tool names.
## Task 0 — redesign (design thesis v2)
- World: Margaret Szymanski, POA Carol Vance. Private long-term resident from 2026-08-12 (after a Part A rehab stay
  elsewhere, 30 prior SNF days in the benefit period); skilled need resumed 2026-09-09 within 30 days -> Part A episode
  (Plan K) verified 2026-10-09 retroactively from 2026-09-09; private agreement converted; ancillary account moved to
  the consolidated-billing tier from 09-09. Sept oxygen concentrator (185.00, full month, posted 10-04 at the Part B tier
  price) was paid 100.00 by a trust transfer (posted 120.00 against a 100.00 authorization; 20.00 returned 10-09 as
  amount_error) and 50.00 by the daughter's check the same day. Sept Part A booking 22 days, reversed 09-23 (uncertified,
  center bears) and 09-20 (LOA). Resident in hospital since 10-19 (Medicare skilled-stay hold elected).
- A0 return (agent, state_due, 4 factors): covered_days (method: Part A booked net + uncertified kept / MA month-granular
  / every charged day), paid_part (param: less earlier wrong-amount/duplicate returns / nothing if returned for no
  authorization / whole), absorption (param: unpaid balance cleared first / credits already posted / none),
  allocation (method: later payments refunded first / same-day pro rata / transfer first). Baseline = whole transfer.
- R0 per-bill authorization (user, on_request, 5 factors): spare = balance - awaiting authorization - unbilled Part A
  coinsurance run-up - bed-hold accrual. Factors: coinsurance_share (param, multi-source), full_coverage_left (param),
  coinsurance_days_run (method), held_bed_accrual (param, bedhold+private), awaiting_authorization (method).
  Baseline = lesser of open charge and (balance - authorized amount awaiting - run-up at defaults: whole coinsurance,
  20 full days, every day after the last booked block through yesterday, rate of the latest coinsurance charge).
- Edge R0 -> A0 value_input on balance_now (state form, unchanged sentence).
- [progress] tools rewritten: return_improper_transfer_e2970e4f (agent; reversal_reason enum so the base dedup gate binds
  to an argument; old return_covered_charge_b2e57ca6 dropped) + sign_bill_payment_authorization_74e4ddf9 (enum text
  without "such as"). TASK TOOL CONTRACT OK. Extended yaml re-assembled from scratch ext_A0v2/ext_R0v2; basis/baseline
  sweep clean. World /tmp/trust_0074/w0.py. Sim: A0 = 63.00 (baselines: covered 100.00, paid-part 66.71, absorbed
  86.33, order 94.50; all-baseline 120.00); R0 = 61.50 (share 0.00, full-left 115.70, run-end 0.00, held-bed 115.70,
  awaiting 0.00; all-baseline 115.70). XF 1 fix: refund order decides a mode label; result applies it.
- [task 0 closed v2] gates --task 0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK,
  SCOPE OK. Expected A0 63.00, R0 61.50. Fixes after first gate run: R0 balance read as the ledger sum (history
  load-bearing); three reads added (bed-hold ledger, elections, ancillary requests) so initial_state = closure;
  absorbed ladder corrected (payer-coverage credits change nothing; only price-error/not-requested/dispute credits);
  transfer moved to Oct 8 so it posts on the second business day after the Oct 6 authorization as R0's rule states.

### Task 0 decoy / absent-record probe table (scratch copies, /tmp/trust_0074/probe_t0.py)
| probe | policy | result | reading |
|---|---|---|---|
| as seeded | A0 | 63.00 | gold |
| older decoy transfer to the salon charge (Sept 20) | A0 | 63.00 | LATEST keeps the Oct 8 transfer |
| payer-coverage credit 129.50 posted on the oxygen charge | A0 | 63.00 | same improper part, ignored by rule |
| daughter's check dated after the transfer | A0 | 44.50 | order tier "later payment" |
| no other payment on the charge | A0 | 44.50 | transfer first; unpaid 85.00 absorbed |
| earlier return was for lacking authorization | A0 | 0.00 | paid part nothing |
| no active Part A, no MA case | A0 | 100.00 | every charged day |
| both Sept booking reversals removed | A0 | 67.11 | 22 covered days |
| opening world (return not yet made) | R0 | 0.00 | spare -1.50 |
| hold returned (none in progress) | R0 | 115.70 | run through yesterday, no accrual |
| last covered date Oct 10 | R0 | 115.70 | run through LCD |
| Medicaid hospital reserved bed instead | R0 | 115.70 | nights within 15 reserved |
| no booked block | R0 | 0.00 | run from coverage start |
| coinsurance authorization already transferred | R0 | 0.00 | awaiting nothing; (balance falls by the transfer) |
| QMB on file | R0 | 115.70 | share 0 |

### Task 0 pairwise method-tier table (XF 7 shape test)
| factor | tier pair | distinguishing input / operation |
|---|---|---|
| covered_days_source | Part A vs MA | Part A reads booked and reversed days; MA reads eligibility start vs month start (conditional pick) |
| covered_days_source | Part A vs otherwise | booked/reversed day sums vs the charge's own day count |
| covered_days_source | MA vs otherwise | MA adds the eligibility-start pick (all or none) |
| refund_order | others first vs pro rata | subtraction of other payments vs ratio with paid part |
| refund_order | others first vs transfer first | adds the other-payments input |
| refund_order | pro rata vs transfer first | adds paid part and other payments as a ratio |
| covered_run_end | LCD vs hold | end anchor = last covered date vs day before leave start |
| covered_run_end | LCD vs yesterday | end anchor = last covered date vs today |
| covered_run_end | hold vs yesterday | end anchor = leave start vs today |
| awaiting_authorization | open balance vs nothing | reads the named charge's own ledger vs constant 0 |
| awaiting_authorization | open balance vs authorized | other ledger's open balance vs the request's amount |
| awaiting_authorization | nothing vs authorized | 0 only when transferred/none; authorized amount non-zero on its domain |

## Resume (agent 3) — task 0 gates re-run 7/7 green (extended, tools, replay, solvability, compute, grounding, scope).

## Task 1 — design thesis (draw: prerequisite_problems=3, factor_counts [5, 4, 5, 4])
Occupied by task 0: trust_reversal (return_improper_transfer_e2970e4f) and the per-bill authorization amount
(sign_bill_payment_authorization_74e4ddf9). Task 1 uses the other write operations: bill transfers posted under a
standing authorization (patient pay) and under existing per-bill authorizations (bed hold; Medicare coinsurance), and
the resident's own withdrawal request. M=2: all remaining headroom is task 1's.
Why these: interest needs a day-weighted average (no per-row weighting in the DSL); conveyance needs a discharge/death
after which no user write exists; closure is the whole balance; an ancillary Part B share cannot be refigured (the claim
row carries the amount claimed, not the approved amount). What a transfer may pay once the payer picture changed after
billing, and what the account can spare, are the record-decided quantities left.

World (Rose Ventresca, Lancaster; son Joseph Ventresca, POA): hospital 03-14..03-21; admitted 03-22 under Part A (no
Medigap on file; CWF reported 10 prior SNF days); April coinsurance block booked Apr 1-30 as days 21-50 and billed
100% to her. Later records: CWF corrected prior SNF days to 0 (Jun), the coverage end was recorded with last covered
date Apr 26 (after the block was booked), an LOA day Apr 18 was reversed, and the Medigap Plan L card (in force since
2019) was put on file Aug 10. Private pay from Apr 27; MA application 08-24 asking from 07-01; estimates billed for Jul,
Aug, Sep, Oct (1,389.70); the son paid Jul 300, Aug 1,200, Sep in full, plus 150 unallocated; Oct unpaid. Hospital leave
09-08 (private-pay hold of her private room 528) released by Joseph 09-26 (logged 10-02); returned 10-03 to semi-private
541-A. CAO notice 10-19: eligible from 08-01 (July denied), patient pay 1,276.40; reconciliation posted 10-21 (Jul
not-eligible-month, Aug/Sep trueup decreases); redetermination 10-21: 1,301.20 from 11-01. Oct 16 Joseph signed a
standing authorization for patient pay and per-bill authorizations for the September bed-hold charge and the April
coinsurance charge, and deposited 6,000.00 (her car sale) — on hold through 10-22. frozen_time 2026-10-23 10:40:00 EDT.
Surface goal: pay her bills from the account, then take out what she can spare for winter clothes (she must get under
the resource limit) -> root = his own withdrawal request (owner=user).

Problem tree (fan-in on the root; each edge value_input on the balance the root reads; state-form sentences):
- R1 trust_ext_spare_withdrawal (root, user, on_request, 5 factors: allowance left, next patient pay kept, unsigned
  ancillary bills kept, recurring services accruing (method), unpaid signed requests kept)
- P2 trust_ext_patient_pay_transfer (agent, state_due, 5 factors: month basis (method, multi-source), trueup credit,
  not-eligible-month credit, unapplied payments, the month's notice patient pay)
- P1 trust_ext_bed_hold_transfer (agent, state_due, 4 factors: reserved-night start (method, multi-source), reserved-night
  limit, end of the hold (method), nightly rate of the room held)
- P3 trust_ext_coinsurance_transfer (agent, state_due, 4 factors: away days off, benefit-day numbering (method), share of
  the supplemental coverage, days after the last covered date)
- [tools] task 1 tools appended (fresh uuid8 each): post_patient_pay_transfer_45809d6d, post_bed_hold_transfer_446aaea8,
  post_coinsurance_transfer_51d626ac (agent; each writes one trust_bill_transfer with its own fixed bill_category — trigger-free
  event, stays in trust) and sign_withdrawal_request_c6615816 (user; trust_requests withdrawal_request, no money moves).
  check_task_tools: TASK TOOL CONTRACT OK (6 tools).
- [policies] task 1 policies appended to trust.extended.yaml (scratch sources /tmp/trust_0074/ext_{P2,P1,P3,R1}.yaml):
  trust_ext_patient_pay_transfer (4 factors), trust_ext_bed_hold_transfer (4), trust_ext_coinsurance_transfer (5),
  trust_ext_spare_withdrawal (5; prerequisite edges -> the three transfers, value_input on balance_now, state form, one
  negated/one affirmative/one "before ... must" sentence). check_extended --task 0: EXTENDED OK (factor bindings must carry
  their own evidence reads: P1 eligibility reads and payment reads moved into the factor bindings).
  Coinsurance tool replaced: post_ancillary_transfer_7c3df4f2 dropped (an ancillary Part B share cannot be refigured — the
  claim row carries the amount claimed, not the approved amount) -> post_coinsurance_transfer_51d626ac.

## Resume (agent 4) — task 1 assembly
- check_task_tools: TASK TOOL CONTRACT OK (6 tools). Rebuilt t1 parts (build_t1a/b) and assembled tasks/1.json with
  build_t1c.py (prerequisite_closure, computations, rationale). Sim (handling time, order P2,P1,P3 and P3,P1,P2 identical):
  P2 599.80 (all-base 1389.70), P1 1244.00 (5442.35), P3 759.50 (4198.35), R1 1559.65 (3438.85).
- Gate-forced change (one line): check_solvability proved the create-a-request user tool infeasible (base
  signed_request binds trust_requests.trust_request_id to a trust_request_id arg) -> sign_withdrawal_request_c6615816 now
  enters/signs the amount on the open withdrawal request seeded as t1.rqWd (POA, 2026-10-16, personal_clothing, 0.00);
  persona volunteers that form; amounts unchanged. Tools: half-up rounding via class static _Cents, positive amounts.
- seed_consistency now covers every trust_ledger row (dep1, w1-w4, st1-st3 one entry each).
- Per-task gates task 1: extended, task_tools, replay, solvability, grounding, scope OK (compute pending re-run).

### Task 1 decoy / absent-record probe table (scratch probe_t1.py, full handling-time replay)
| probe | policy | result | reading |
|---|---|---|---|
| as seeded | P2 | 599.80 | gold |
| July not-eligible-month reduction not yet posted | P2 | 1276.40 | credit tier falls to otherwise |
| eligibility start 2026-11-01 | P2 | 0.00 | October a private-pay month |
| October billed as a partial month of 10 days | P2 | 624.60 | lesser of patient pay and days x MA rate |
| unallocated 150.00 payment removed | P2 | 749.80 | unapplied payments 0 |
| as seeded | P1 | 1244.00 | gold |
| release removed (hold to month end) | P1 | 2988.00 | no nights after the hold ended |
| eligibility start 2026-09-15 | P1 | 4296.00 | reserved nights counted from the start date |
| 500.00 card payment removed | P1 | 1744.00 | nothing already paid |
| semi-private room held | P1 | 1092.00 | semi-private nightly rate |
| as seeded | P3 | 759.50 | gold |
| prior SNF days still 10 | P3 | 1302.00 | numbering as booked (decoy: the booked first day 21) |
| last covered date removed | P3 | 976.50 | no days past coverage end |
| QMB on file, no Medigap | P3 | 0.00 | QMB share 0 |
| Medigap effective 2026-05-01 | P3 | 3038.00 | whole coinsurance (card not in force on the first day) |
| leave-of-absence reversal removed | P3 | 813.75 | no away day |
| as seeded (after the three transfers) | R1 | 1559.65 | gold |
| cable restart dated before the 09-26 cancel | R1 | 1601.65 | a later request cancels -> nothing kept |
| cable restart removed (cancel latest) | R1 | 1601.65 | nothing kept |
| June bed-hold charge paid | R1 | 1980.65 | no other unsigned bed-hold balance |
| opening world (no transfers) | R1 | +599.80/+1244.00/+759.50 per skipped transfer | edge sensitivity |

### Task 1 pairwise method-tier table (XF 7 shape test)
| factor | tier pair | distinguishing input / operation |
|---|---|---|
| named_month_patient_pay | notice month vs private-pay month | CAO patient pay (estimate less its trueup) vs constant nothing |
| named_month_patient_pay | notice month vs partial month | reconciled estimate vs lesser of patient pay and days x MA daily rate |
| named_month_patient_pay | private-pay vs partial | nothing vs days x rate capped by patient pay |
| named_month_patient_pay | any vs otherwise (as billed) | the charge amount read as is |
| reserved_nights_on_leave | from departure vs from eligibility start | count anchor = departure date vs eligibility start date |
| reserved_nights_on_leave | either vs none | reserved-limit window vs constant 0 |
| nights_after_hold_ended | release vs return | nights after the release date (exclusive) vs from the return date (inclusive) |
| nights_after_hold_ended | release/return vs discharge | anchor = release/return vs hospital discharge date (exclusive) |
| nights_after_hold_ended | any vs none | date-anchored count vs 0 |
| block_benefit_day_count | renumbered vs band 1-20 | numbering from coverage start + prior days vs every day of the block |
| block_benefit_day_count | renumbered vs as booked | current numbering vs the booking's first benefit day |
| block_benefit_day_count | band 1-20 vs as booked | whole block vs booked numbering at or below the limit |
| coming_patient_pay_kept | no income vs income | patient pay vs patient pay less latest pension/benefit deposit (floored) |
| coming_patient_pay_kept | either vs nothing | standing-authorization read vs 0 |
- Full suite (no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (suite means
  branches 132.50 / steps 23.00; history_rows_max 38; branches_max 173), GROUNDING OK, SCOPE OK; CACHE-DIFF INFO only.
  check_traceability deferred until the KB is rendered. Scratch /tmp/trust_0074 removed.
ROUND 1: gates 7/7 green

## REWORK round 2 (agent 5) — plan after reading audits/policy_task/resident_trust_fund_accounts/{_difficulty,0,1}.md (revision_1)
Root-cause finding for task 1 (F-17 + XF 29 together): a bill transfer pays MN(open balance, authorized, available)
(trust_evt_bill_transfers). On a producible ledger the bed-hold / Medicare / Medicaid offices have already posted every
correction (bedhold_evt_payments_adjustments, medicare_evt_secondary_and_qmb, medicaid trueups), so a transfer's open
balance already embeds every refigured night/day/share -> no factor of P3/P4/P5 can bear weight on a producible world.
What IS producible: once a charge is PAID IN FULL, its owning charter can no longer reduce it ("each reduction ...
never exceeds its open balance" / "An adjustment ... never exceeds that charge's open balance"), so the over-payment
must come back through trust_evt_reversals ("returned ... for the improper part only"). The refiguring is then the
trust's own owed write, and nothing is owed-but-unposted in the other ledgers.
Decision:
- Task 1 tree rebuilt: root trust_ext_spare_withdrawal (user) <- three agent RETURNS on transfers that paid a charge
  in full: hospital-leave bed-hold return, therapeutic-leave bed-hold return, Medicare coinsurance return (each its
  own tool, reason amount_error). P3/P4/P5 and their tools are retired (no task uses them).
- Task 0 kept (P1 return on an ancillary transfer <- P2 authorization amount); ancillary credits are not capped, so
  the Part A verification is moved to the frozen day (in-flight: the ancillary office's credit is not posted yet).
- Every factor rebuilt to distinct-outcome ladders on real charter rules; T1/T2 table, probe table, method table below.
- [round 2 progress] scratch /tmp/trust_0074/pol/p1.yaml, p2.yaml written (sweep CLEAN: basis verbatim, baseline in rule,
  no factor reads another factor transitively). P1 factors: payer_start_days (M), nights_away_taken (P), transfer_paid_part
  (P), refund_order (M). P2 factors: covered_run_end (M), run_day_numbering (M), coinsurance_year_rate (P),
  coinsurance_share (P), held_bed_buildup (P, schedule rate of the room tier held per night - F-7). Task 0 world to move
  the Part A verification to the frozen morning (nothing of it processed by other offices yet), prior SNF days 14.
- [round 2 progress] TASK 0 rebuilt and per-task gates green (extended, replay, solvability, compute, grounding, scope):
  P1 63.00 / P2 61.50 unchanged in value, factors rebuilt; Part A verified on the frozen morning; earlier episode
  Jul 28 - Aug 14 gives 18 prior SNF days; coinsurance authorization removed; private reads re-added for closure.
- Task 1 decision (after exhausting alternatives, recorded so a resume does not redo it): root spare withdrawal <-
  (B) bed-hold return on the most recent bed-hold transfer [amount_error; hold_end M, room_tier P, rate_schedule P,
  refund_order M], (C) coinsurance return on the most recent coinsurance transfer [amount_error; resident_share P,
  year_rate P, split_anchor M, covered_end M, refund_order M], (P3) standing patient pay transfer kept, in-flight
  Medicaid approval received on the frozen morning (trueups not due yet) [month_owed M, recon credit P, not-eligible
  credit P, unapplied payments P]. B and C pay charges paid in full, so the owning offices cannot reduce them
  (bedhold/medicare "never exceeds its open balance") - nothing owed-but-unposted. P4/P5 transfer policies and tools
  are retired. Ruled out (reasons): a second bed-hold or coinsurance policy (same transfer selection, DSL cannot
  join a transfer to its leave type), interest correction ("A month is credited once."), ancillary/private/patient-pay
  returns (their credits are not capped, so they would be owed-but-unposted).
- [round 2 progress] Charter written with all six round-2 policies (scratch pol/{p1,p2,p3,pb,pc,r6}.yaml, sweep CLEAN):
  trust_ext_bed_hold_return (return_bed_hold_overcharge_0789df0a; factors hold_end_nights M, hold_room_tier P,
  hold_rate_schedule P, hold_refund_order M) and trust_ext_coinsurance_return (return_coinsurance_overcharge_2cf6d12d;
  block_covered_end M, center_borne_days P, block_plan_share P, service_year_rate P) replace the bed-hold/coinsurance
  transfers; P3 patient pay transfer revised (no trueup inference, open-balance cap, single rounding, in-flight
  reconciliation tier); spare withdrawal revised (narrow prerequisite sentences, ancillary_bills_kept and
  bed_hold_bills_kept replace the F-14/F-8 factors, latest income deposit by date, VA tier keeps PNA + VA pension).
  task_tools.py: retired post_bed_hold/post_coinsurance tools, added the two return tools, ordering words removed
  (TASK TOOL CONTRACT OK). Next: task 1 world rebuild (Rose) + 1.json.
- [round 2 progress] Task 1 world built in scratch (/tmp/trust_0074/w1*.py -> w1.json): Part A Dec 2025 episode (Plan K
  on file late, 2026 rate on 2025 days, recert late 12-27, block booked past the 12-30 last covered date, paid in full
  Jan 14 by card 500 + trust 2538); June 2026 private hospital hold (notice late 06-12, returned 06-25, billed 21
  nights at the 2026 private rate, paid in full Jul 8 by card 1000 + trust 8156); May home-visit hold 421 open;
  MA approved 10-14 from 07-01 (June left out), Jun-Sep reconciled 10-21, October in its trueup window; no car-sale
  deposit (removed: the withdrawal stays a clothing-sized spend-down of what the returns free). Sim: all four
  computations order-independent, every factor moves its result.
- [round 2 progress] tasks/1.json written (round-2 world, persona, criteria, contract, closure, computations); running gates.
- [round 2 progress] task 1 per-task gates green (extended, replay, solvability, compute). Values unchanged in shape; Aug 14 duplicate petty-cash return seeded (evidence for return_once); return tools take reversal_reason (dedup gate binds it).
- [round 2] P3 in-flight reconciliation tier rewritten (probe found June's difference counted in the in-flight tier):
  it now counts the uniform estimate's difference for each month from the eligibility start up to the named month;
  in-flight probe now equals the posted-trueup value.

### Round 2 decoy / absent-record probe tables (full handling-time replay, scratch probe0.py / probe1.py)
| probe | policy | result | reading |
|---|---|---|---|
| as seeded | P1 | 63.0 | |
| older ancillary transfer to the salon charge (decoy) | P1 | 63.0 | |
| check dated after the transfer | P1 | 44.5 | |
| earlier return was for lacking authorization | P1 | 0.0 | |
| no active Part A | P1 | 100.0 | |
| September leave night reversed | P1 | 67.11 | |
| as seeded | P2 | 61.5 | |
| hold returned (none in progress) | P2 | 115.7 | |
| Plan L instead of K | P2 | 115.7 | |
| QMB on file | P2 | 115.7 | |
| prior SNF days 25 (limit reached) | P2 | 0.0 | |
| held room semi-private memory care | P2 | 3.5 | |
| as seeded | P3 | 486.5 | |
| second October charge recorded later (tie) | P3 | 536.5 | |
| trueups not posted yet (in-flight tier, after the fix) | P3 | 486.5 | |
| unallocated payment refunded 150 | P3 | 636.5 | |
| notice effective 2026-11-01 (later month) | P3 | 599.8 | |
| as seeded | PB | 3280.75 | |
| older bed-hold transfer to the May charge (decoy) | PB | 3280.75 | |
| bed released 06-25 instead of returned | PB | 2905.73 | |
| notice delivered on the departure date | PB | 2530.71 | |
| reservation records no room tier | PB | 3709.22 | |
| card payment dated after the transfer | PB | 2683.0 | |
| as seeded | PC | 1837.92 | |
| Plan L on file | PC | 2187.96 | |
| QMB status on file | PC | 2538.0 | |
| recertification on time (12-20) | PC | 1400.37 | |
| QIO upheld, decision 12-31 | PC | 1750.41 | |
| as seeded | R6 | 4595.64 | |
| pension deposit 1200 on 10-01 | R6 | 6995.64 | |
| cable cancel dated after the restart | R6 | 4637.64 | |
| bed-hold authorization awaiting transfer (May charge, 300) | R6 | 4716.64 | |
(Readings: each probe moves the result exactly through the rule's named tier; the decoy transfers are ignored by the
"most recent transfer" selections; "no active Part A" gives the fall-through, but the return is then out of the
policy's scope sentence and is not owed.)

### Round 2 T1/T2 table (T1 = this task's result with that factor alone at baseline; T2 = a producible world where it
moves the result with every other factor at baseline)
| policy | factor | gold | T1 baseline figure | T2 |
|---|---|---|---|---|
| covered return | payer_start_days (M) | 63.00 | 95.89 | this world |
| covered return | nights_away_taken (P) | 63.00 | 67.11 | this world |
| covered return | transfer_paid_part (P) | 63.00 | 66.71 | this world |
| covered return | refund_order (M) | 63.00 | 94.50 | this world |
| authorization | covered_run_end (M) | 61.50 | 0.00 | any episode with a coinsurance charge (baseline rate non-zero) |
| authorization | run_day_numbering (M) | 61.50 | 115.70 | same |
| authorization | coinsurance_year_rate (P) | 61.50 | 115.70 | this world |
| authorization | coinsurance_share (P) | 61.50 | 0.00 | same as run end |
| authorization | held_bed_buildup (P) | 61.50 | 115.70 | any hold in progress |
| patient pay transfer | named_month_patient_pay (M) | 486.50 | 599.80 | this world |
| patient pay transfer | credited_reconciliation_amount (P) | 486.50 | 826.40 | this world |
| patient pay transfer | credited_not_eligible_amount (P) | 486.50 | 1276.40 | this world |
| patient pay transfer | unapplied_patient_pay_payments (P) | 486.50 | 636.50 | this world |
| bed-hold return | hold_end_nights (M) | 3280.75 | 1030.63 | this world (baseline rate differs from the charge) |
| bed-hold return | hold_first_night (M) | 3280.75 | 2530.71 | same |
| bed-hold return | hold_room_tier (P) | 3280.75 | 3709.22 | this world |
| bed-hold return | hold_rate_schedule (P) | 3280.75 | 3107.05 | this world |
| bed-hold return | hold_refund_order (M) | 3280.75 | 3683.00 | this world |
| coinsurance return | block_covered_end (M) | 1837.92 | 1750.41 | any block booked past its last covered date |
| coinsurance return | center_borne_days (P) | 1837.92 | 1400.37 | any block with a late recertification |
| coinsurance return | block_plan_share (P) | 1837.92 | 1137.84 | any Medigap K/L/full or QMB episode |
| coinsurance return | service_year_rate (P) | 1837.92 | 1812.86 | any block priced at another year's rate |
| spare withdrawal | resident_allowance_kept (P) | 4595.64 | 4640.64 | this world |
| spare withdrawal | coming_patient_pay_kept (M) | 4595.64 | 5872.04 | this world |
| spare withdrawal | ancillary_bills_kept (P) | 4595.64 | 4665.64 | this world |
| spare withdrawal | recurring_services_kept (P) | 4595.64 | 4637.64 | this world |
| spare withdrawal | bed_hold_bills_kept (P) | 4595.64 | 5016.64 | this world |

### Round 2 pairwise method-tier table (XF 7 shape test)
| factor | tier pair | distinguishing input / operation |
|---|---|---|
| payer_start_days | Part A vs MA | anchor = coverage start vs eligibility start (different record) |
| payer_start_days | either vs otherwise | date-anchored count vs every charged day |
| refund_order / hold_refund_order | others first vs pro rata | subtraction of other payments vs ratio with the transfer |
| refund_order / hold_refund_order | either vs transfer first | adds the other-payments input |
| covered_run_end | LCD vs hold | end anchor = last covered date vs day before leave start |
| covered_run_end | LCD/hold vs yesterday | record date vs today |
| run_day_numbering | block booked vs prior days | last booked benefit day vs eligibility-response prior days |
| run_day_numbering | either vs day one | adds a numbering offset input |
| named_month_patient_pay | notice vs not-eligible vs partial vs as billed | case amount / constant 0 / min with days x MA rate / charge amount |
| hold_end_nights | return vs release vs expiry vs all | exclusive return date / inclusive release / inclusive end date / charge's own nights (different records) |
| hold_first_night | notice vs late election vs first night | notice delivery date / private hold start / charge's first night |
| block_covered_end | QIO upheld vs LCD vs all | later-of two dates (max) / single date / priced days |
| coming_patient_pay_kept | no income vs income vs nothing | patient pay / patient pay less latest income deposit (floored) / 0 |
- Round 2 full gate block: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (branches mean
  151.50, steps mean 22.50, history max 32, branches max 194), GROUNDING OK, SCOPE OK. check_traceability deferred to
  after rendering. Scratch removed.
- Known residual risks for the audit (not hidden): P3's credit factors still sum posted adjustments of one kind per
  tier (F-14 shape); the coinsurance/bed-hold day factors are corroborated by the owning offices' posted day
  reversals; the July-September interest credits keep the threshold in force when posted ("A month is credited once.").
REWORK round 2: gates 7/7 green

## Round 3 (rework of revision_2) — progress
- Started. Items: R2-1 (prereq sentence selection), R2-2 (+T0 consequence), T0-R2-X1 (Sept Part A booking owed),
  T0-X1 ext (cons. billing tier/credits, holds tier, payer conversion), R2-3, R2-4, R2-5, R2-6, R2-7, R2-8, R2-9,
  R2-10, R2-11, T1-X2. Rulings: RND(x+1e-9,2); Decimal half-up in tools; edges engaged & resolvable.
- Design review (round 3, before edits). Policy-set alternatives checked against the charters and the skill
  ("never reuse under a new name / near-synonym" forbids clone policies split by leave kind or episode status):
  * a 6th rich trust write does not exist outside the current six: bed-hold and Medicare offices cap their own
    reductions at the open balance (frozen returns P4/P5); ancillary/private/medicaid corrections are uncapped and
    post the improper amount themselves; payer-covered bed-hold/coinsurance returns have at most 3 genuine factors.
  * decision: keep the six policies and the task split; close each revision_2 item inside them.
- P5 rewritten (5 factors: covered end, center-borne [reads uncertified reversals / no-recert lapse], plan share with effective date, service-year rate, refund order); P4 rewritten (4: notice night, room tier, per-night schedule, refund order; first night later-of and end date plain). T1 on task 1 checked.
- P3 rewritten (4: month standing, month amount, reconciliation credit with every-estimate-equal test, not-eligible credit; both credits project the reconciliation still owed within the trueup days, so posting it changes nothing); P6 kept-bill ladders and prerequisite sentences rewritten. Task 1 world patch: 10-21 reconciliation rows removed (inside trueup window), 763026cd applied to June, returned holds end_date = last held day.
- P2 rewritten (5: run end, coinsurance share, share effective split, held-bed buildup of uncharged nights, held room tier;
  numbering per medicare_agg_benefit_period; per-day year rate; completed leave inside the run -> nothing kept).
  P1 rewritten (4: payer start days, credits counted, transfer paid part, refund order; nights away removed: the
  ancillary tier follows the payer source on every day of the episode, so a leave day is no different).
- Task 0 world (w0 builder): September booked 10-01 (2+20 days), resident coinsurance 4340 paid 10-13; Plan K effective
  2026-10-06 (episode tier re-derived), first episode without Medigap; ancillary consolidated tier from 09-09 with the
  consolidated-billing credit posted 10-15 (trust return still inside the 5 business days); private agreement private
  tier, conversion credit 09-09, deposit and credit balance refunded 09-24, no October bill; hold in progress = Medicare skilled-stay tier;
  September leave removed; 1635.00 check withdrawal 10-16 (spare binds).
- Task 1 JSON rebuilt (computations, closure, texts); gates for task 1: extended, tools, replay, solvability, compute, grounding, cross_fire OK.
- Task 0 JSON rebuilt; per-task gates green.

### Round 3 T1/T2 table (T1 = task world, baseline of that factor alone moves the scored result; T2 = scratch world, the factor moves the result with every other factor at baseline; 'gated by X' = the only world where it moves keeps X live, because the factor acts on X's quantity)
| policy | factor | T1 | T2 |
|---|---|---|---|
| trust_ext_covered_service_return | credits_counted | moves | gated by payer_start_days @P1 task world |
| trust_ext_covered_service_return | payer_start_days | moves | strict @P1 trust paid all |
| trust_ext_covered_service_return | refund_order | moves | gated by payer_start_days @P1 task world |
| trust_ext_covered_service_return | transfer_paid_part | moves | strict @P1 task world |
| trust_ext_ancillary_authorization_amount | coinsurance_share | moves | strict @P2 balance 4390 |
| trust_ext_ancillary_authorization_amount | covered_run_end | moves | strict @P2 balance 4390 |
| trust_ext_ancillary_authorization_amount | held_bed_buildup | moves | strict @P2 balance 4390 |
| trust_ext_ancillary_authorization_amount | held_room_tier | moves | gated by held_bed_buildup @P2 balance 5196 |
| trust_ext_ancillary_authorization_amount | share_effective_split | moves | gated by coinsurance_share @P2 balance 2400 |
| trust_ext_bed_hold_return | hold_night_schedule | moves | strict @task 1 world |
| trust_ext_bed_hold_return | hold_notice_night | moves | strict @task 1 world |
| trust_ext_bed_hold_return | hold_refund_order | moves | strict @task 1 world |
| trust_ext_bed_hold_return | hold_room_tier | moves | strict @task 1 world |
| trust_ext_coinsurance_return | block_covered_end | moves | strict @task 1 world |
| trust_ext_coinsurance_return | block_plan_share | moves | strict @task 1 world |
| trust_ext_coinsurance_return | center_borne_days | moves | strict @task 1 world |
| trust_ext_coinsurance_return | coinsurance_refund_order | moves | strict @P5 hospital day reversed |
| trust_ext_coinsurance_return | service_year_rate | moves | strict @task 1 world |
| trust_ext_patient_pay_transfer | credited_not_eligible_amount | moves | strict @task 1 world |
| trust_ext_patient_pay_transfer | credited_reconciliation_amount | moves | strict @P3 no June |
| trust_ext_patient_pay_transfer | named_month_amount | moves | gated by named_month_standing @task 1 world |
| trust_ext_patient_pay_transfer | named_month_standing | moves | strict @P3 named month left out |
| trust_ext_spare_withdrawal | ancillary_bills_kept | moves | strict @task 1 world |
| trust_ext_spare_withdrawal | bed_hold_bills_kept | moves | strict @task 1 world |
| trust_ext_spare_withdrawal | coming_patient_pay_kept | moves | strict @task 1 world |
| trust_ext_spare_withdrawal | recurring_services_kept | moves | strict @task 1 world |
| trust_ext_spare_withdrawal | resident_allowance_kept | moves | strict @task 1 world |

### Round 3 probe table (scratch copies of the task worlds; every row = rule outcome)
| policy | read probed | decoy / edge | outcome |
|---|---|---|---|
| covered return | LATEST ancillary transfer | second transfer same date recorded later (tie) | first recorded kept |
| covered return | LATEST ancillary transfer | older second transfer | most recent kept |
| covered return | LATEST ancillary transfer | absent | nothing returned |
| covered return | returns on the transfer | returned as duplicate | paid part nothing, nothing returned |
| covered return | credits on the charge | price-error credit | counted against the unpaid balance |
| covered return | payments on the charge | later card payment | others refunded first |
| covered return | payer status | no active Part A, no eligible case (absent payer) | no covered day (fixed this round: fall-through was every day) |
| authorization | bed-hold booked leave | completed leave inside the run | nothing kept for the run |
| authorization | hold in progress | hold returned (not held) | run to yesterday, no held nights |
| authorization | LATEST item charge | second item same date recorded later | first recorded named |
| authorization | supplemental effective date | before the run / absent | every day at share / no day at share |
| authorization | active episode | absent | no run-up (guard added this round) |
| patient pay transfer | adjustments on other charges | reconciliation posted mid-call | same transfer (projected = posted) |
| patient pay transfer | estimates | one estimate differs | no projected credit |
| patient pay transfer | LATEST charge by month | second charge same month recorded later | first recorded named |
| bed-hold return | transfer notice | absent | no night allowed |
| bed-hold return | transfer notice | delivered before departure | from departure |
| bed-hold return | private hold start | later than the notice | from the election |
| bed-hold return | end date | released inside the charge | through the end date |
| bed-hold return | night dates | nights spanning 2026-07-01 | split schedules |
| coinsurance return | end reason | QIO upheld | through the later of LCD and decision |
| coinsurance return | supplemental effective date | inside the block | secondary-charged days at the share |
| coinsurance return | certification | none after admission, no reversal yet | days after day 14 center-borne |
| spare withdrawal | hold in progress | private hold held | open charges plus uncharged nights |
| spare withdrawal | ancillary authorization | authorizes less than its charge | part left out not kept |

### Round 3 pairwise method-tier table (distinguishing input per pair)
| factor | tier pair | distinguishing input / operation |
|---|---|---|
| payer_start_days | Part A / MA | coverage start date vs eligibility start date (different record) |
| payer_start_days | Part A or MA / none | date-offset count vs no day (adds the payer's start) |
| refund_order (P1, P4, P5 alike) | others first / pro rata | subtraction of other payments vs share by paid part (operation) |
| refund_order | pro rata / transfer first | share vs whole (adds the other payments as divisor) |
| refund_order | others first / transfer first | other payments subtracted vs not |
| covered_run_end | LCD / day before leave | last covered date vs hold's leave start (different record) |
| covered_run_end | LCD or leave / yesterday | record date vs today |
| share_effective_split | from run start / from effective date | offset 0 vs data-selected window start |
| share_effective_split | from a date / none | window vs no day (no share applied) |
| named_month_standing | left out / eligible | nothing vs the month's amount (conditional pick) |
| named_month_standing | eligible / as billed | notice amount vs posted charge |
| hold_notice_night | delivery date / none | delivery date vs no night allowed |
| hold_notice_night | delivery date / departure | notice record vs reservation's leave start |
| block_covered_end | QIO later-of / LCD | adds the QIO decision date and a max |
| block_covered_end | LCD / every priced day | date window vs whole block |
| coming_patient_pay_kept | PP / PP less income | adds the latest pension or benefit deposit |
| coming_patient_pay_kept | PP / nothing | standing authorization present vs absent |

### Round 3 gated T2: the base sentence that makes each factor act only through another factor's quantity
- held_room_tier through held_bed_buildup: bedhold_evt_charges "the days times the bed-hold daily rate" (a rate prices nights; with no night building up there is nothing to price).
- share_effective_split through coinsurance_share: medicare_evt_coinsurance "days before the supplemental effective date keep the earlier split" (where no supplemental share applies the split moves nothing).
- named_month_amount through named_month_standing: medicaid_evt_patient_pay_actual "each eligible month is billed the patient pay amount on the County Assistance Office notice in effect for that month" (the notice amount belongs to an eligible month only).
- refund_order and credits_counted through payer_start_days: trust_evt_reversals "for the improper part only" (when every paid dollar is improper each payer gets back exactly what it paid, so the order and the credits counted change nothing).

### Round 3 item closure (revision_2)
- R2-1: every prerequisite sentence now names the resolver's own row ("the most recent transfer to an X charge, where part of that transfer ...") and is engaged only where the resolver writes a positive amount (edge-engagement ruling); conditions restated without world values.
- R2-2: P2 numbers the run as medicare_agg_benefit_period numbers it (prior SNF days + net booked days of the episode); a completed leave inside the run stops the run-up; the September block is booked, so the run is October.
- R2-3: P2 prices each run day at the rate of the year it falls in.
- R2-4: P1's nights-away factor removed; the ancillary tier follows the payer source on every episode day, so a leave day changes nothing; no reversal read without a service month remains.
- R2-5: P3 named month split into standing (left out / eligible / as billed) and amount (partial month / notice in effect / as billed); the eligibility-start month is an eligible month.
- R2-6: P6 kept-bill ladders keep every open charge (authorization shortfall / open balance / nothing; hold in progress accrual / open charges).
- R2-7: transfer_paid_part kept with distinct branches; run_day_numbering, credited_not_eligible (old), unapplied payments, hold_end_nights, hold_first_night (later-of) removed or made plain; replacements listed in the T1/T2 table.
- R2-8: P4 first chargeable night = the later of the charge's first night, the notice night and the recorded private hold start.
- R2-9: P5 uncertified days read from the coverage office's uncertified reversals (or, with no certification after admission, days after the initial recertification day); plan share applied by its effective date relative to the block.
- R2-10: factor counts per policy: P1 4, P2 5, P3 4, P4 4, P5 5, P6 5, each with T1 on its task world and T2 as tabled.
- R2-11: P3 projected reconciliation requires every pending estimate to be the same amount (count x max = sum).
- T0-R2-X1 / T0-X1: task 0 world rebuilt so no other office owes anything at the opening (September booked and paid; ancillary tier and credit; hold tier; private conversion, deposit and credit refunded).
- T1-X2: the 10-12 payment applied to June (oldest open month); unapplied-payments factor removed.
- Observations O2-1 (nights before 2025-07-01 take the charge's own rate, stated) and O2-2 (returned holds record end_date = last held day) closed.
- Scratch removed (/tmp/trust_0074).
REWORK round 3: gates 7/7 green

## Round 4 (rework of revision_3) — progress
- Started. Items: R3-1..R3-6, T0-R3-X1, T0-R3-X2, O3-1, O3-2.
- R3-1: P2's keep-nothing sentence replaced by a reserve: every day of the run is reserved as a day in the center, a night away included, because a Part A night away is billed instead as a held night at the private rate of the room held, never less than the coinsurance reserved; the bed-hold ledger read (decoy: a month-end booking of a hold in progress) is gone. Probe: a completed leave inside the run leaves the reserve unchanged.
- R3-3: fall-through = baseline: P1 payer_start_days (Part A / MA start after the charge's first day; otherwise every charged day; no payer is a plain scope sentence: no covered day); P4 hold_night_schedule (nights before 2025-07-01 take the schedule in effect on the billing date, = baseline; keeps hold_room_tier ungated: T2 strict on task 1's world); P6 bed_hold_bills_kept (hold in progress / open balance / nothing = baseline).
- R3-4 (i): P3 projected not-eligible months are counted from the estimates actually billed (estimates less those from the eligibility month to the latest estimated month). Probe: a retro request to April with estimates only from June credits June only.
- R3-4 (ii)/(iii): base sentences that bound P5: medicare_evt_day_counting "days after a lapsed certification are provider liable, are reversed as uncertified_day" and "A booked day later found to be ... a booking error is reversed against the booked-days entry" - the coverage office posts both at once; the trust reads them as posted. Taking booking-error reversals off inside the covered window without per-row dates would make the covered end double-count the booking errors after the last covered date (the only booking-error row in task 1), so they are left to the covered end.
- T0-R3-X1: private_tier_placement "Only an open, active agreement changes tier": the agreement was converted on Sept 9, so it keeps its private-room tier while the Part A bed 517-A is semi-private; stated in the seed-consistency entry.
- T0-R3-X2: ancillary account balance set to the ledger figure.
- R3-2 / R3-5 / R3-6 (structural, not closed): under the revision_3 tests (fall-through = baseline, no tier a special case of another on its domain, strict T2) the trust charter's write policies carry at most these genuine factors: P1 2 (payer start, paid part), P2 3-4, P3 2, P4 4, P5 4-5, P6 3-4 against the draw P1 4, P2 5, P3 4, P4 4, P5 5, P6 5. The cause is the domain: bed-hold and Medicare reductions are capped by the owning offices, ancillary/private/medicaid corrections are posted by them, and every quantity left to the trust is a sum of record reads or an allocation that only matters when the refund is partial. A sixth rich policy does not exist (checked in round 3). Closing these needs a coordinator decision (redraw, re-scope the difficulty's policy set, or accept the gated/sum ladders).
- Scratch removed (/tmp/trust_0074).
REWORK round 4: gates 7/7 green

## Round 5 (rework of revision_4) — progress
- Started. Items: R4-1 (P1 payer start clamp), R4-2 (P3 not-eligible month count), R4-4 (P5 booking-error days), R3-2 class, R3-6 (now accepted by coordinator when tier sentences act on a baseline quantity), R4-3 floor.
- R4-1: P1 payer_start_days tiers now split by payer only (Part A active: from the coverage start; MA eligible, no Part A: from the eligibility start; neither payer: every charged day = baseline, and the plain sentence then gives no covered day); the fall-through is no longer the clamp of the other tiers. Probes: no payer -> nothing returned; Part A start before the charge -> every charged day.
- R4-2: P3 projected not-eligible months are counted from the application date's month to the month before the eligibility start month (medicaid_evt_pending_estimate bills an estimate each month the application is pending), not from estimate rows. Probes: retro request -> application month on; duplicate estimate row -> same months.
- R4-4: P5 takes off booking-error days that fall on or before the covered end (one booking-error stretch: by its dates); where the coverage office reversed more than one stretch as booking errors, the owed days are the block's days less every reversed day, never more than its days through the covered end (scoped, exact). Probes: one stretch inside the window and two stretches both give the rule's figure; task value unchanged.
- R3-6 (coordinator decision): refund_order (P1), held_room_tier (P2), named_month_amount (P3) state their effect on a quantity the baseline defines (refundable part, room tier priced, the month's patient pay amount) and keep plain baselines; counted.
- R3-2 class / R4-3 floor: not closed. Members still one formula on their domains, each because the business quantity is one formula: transfer_paid_part (trust_evt_reversals "for the improper part only": paid part = transfer less returns), credits_counted (ancillary credit reasons), share_effective_split (medicare_evt_coinsurance: days before the effective date keep the earlier split), held_bed_buildup (bedhold_agg_payer_day_limits: private nights are the nights beyond the payer's reserved nights, 0 off Medicaid), credited_reconciliation_amount / credited_not_eligible_amount (posted reductions = baseline; one projected tier), ancillary_bills_kept / bed_hold_bills_kept (open balance plus accrual). With R3-6 members counted the genuine factors are P1 2, P2 3, P3 2, P4 4, P5 5, P6 3 against P1 4, P2 5, P3 4, P4 4, P5 5, P6 5; no other trust write in the claimed event types carries more (round 3 review). Needs a further coordinator decision on these ladders.
- Scratch removed (/tmp/trust_0074).
REWORK round 5: gates 7/7 green

## Round 6 (rework of revision_5) — progress
- Started. Items: R3-2 (8 members), R5-1 floor (P1 2/4, P2 3/5, P3 2/4, P6 3/5). Plan: replace each member by a ladder whose tier expressions stay different on every other tier's domain (record anchors, constants per tier), engaged on the task world by producible seeds; members with no such ladder in the claimed policy set are stated with the base sentences that bound them.
- Test applied to every ladder (the auditor's R3-2 reading): each tier's expression, evaluated on another tier's domain, must give a different value somewhere on that domain; a tier whose expression degenerates to another's where its data is absent (zero returns, zero credits, zero nights, zero balance) is a coinciding tier.
- R3-2 / P1 transfer_paid_part: rebuilt on three records. Tier 1: the ancillary ledger's payment by trust transfer naming the charge on the transfer's date, never more than the transfer less its wrong-amount returns (ancillary_evt_payments_credits: "A payment names the charge it pays and is applied only up to its open balance"); tier 2: no applied payment, the most recent per-bill authorization naming the charge (trust_evt_bill_transfers: per-bill authorization naming that charge; the excess is a wrong amount, trust_evt_reversals); tier 3 (= baseline): the whole transfer. A transfer already returned as unauthorized or duplicate has no paid part (plain). Tier 1 on tier 2's domain reads no applied payment (0), tier 2 on tier 1's domain reads the authorization (differs where the ancillary account capped the payment at the open balance), tier 3 differs from both. The transfer amount is read with SUM on its own entry so the trust history stays load-bearing.
- R3-2 / P1 credits_counted: rebuilt on the ancillary account's tier: consolidated billing tier -> every credit except consolidated-billing credits; Medical Assistance / Part B / Medicare Advantage tier -> every credit except payer-covered-item credits; hospice tier -> every credit except hospice-related credits; any other tier (= baseline) -> every credit. The condition is the tier, not the credit's presence, so on every other tier's domain a tier's exclusion still differs where a credit of another payer's coverage names the charge (the credit of another payer's coverage settled the charge for days that payer covered).
- R3-2 / P2 share_effective_split and held_bed_buildup: both turned into plain sentences (unchanged wording, no ladder). Two factors replace them:
  - run_year_rate (parameter): a run day in 2026 -> K coinsurance_rate_2026; in 2025 -> K coinsurance_rate_2025; any other year (= baseline) -> the rate of the episode's most recent coinsurance charge (medicare_evt_coinsurance: "priced at the daily coinsurance rate of the calendar year in which those days of service fall, never at the rate of the posting date"). Seed: the September block's resident charge was posted at 209.50 (the 2025 rate) and paid as billed; an undercharge no write can correct (adjustments only reduce a charge; a block is charged once per liable party), so nothing another office owes is pending.
  - hold_first_night (method, sibling of P4's hold_notice_night): the latest transfer notice for the reservation delivered after the hold's first held day -> the delivery date; no transfer notice -> no night; otherwise (= baseline) the hold's first held day (private hold start, else leave start) (bedhold_evt_notice: "No day held before the transfer notice was delivered is ever charged"). Seed: emergency transfer Oct 19 15:40, notice delivered Oct 20 09:00 (within the emergency notice hours), written election Oct 20 10:15 (within 24 hours of the notice, so held from the departure date).
  - The Oct 16 check withdrawal is 2035.00 (request and account balance aligned) so the spare stays below the van trip's open balance and every P2 factor moves the scored figure.
- R5-1 floor after the rebuild: P1 4 (payer_start_days, refund_order, transfer_paid_part, credits_counted), P2 5 (covered_run_end, coinsurance_share, run_year_rate, hold_first_night, held_room_tier), P4 4, P5 5 meet the draw. P3 2 of 4 and P6 3 of 5 do not (below).

### Round 6 T1/T2 table (task 0; T1 = task world, that factor alone at baseline; T2 = every other factor at baseline)
| policy | factor | T1 | T2 |
| --- | --- | --- | --- |
| P1 return | payer_start_days | moves | strict @scratch: trust paid the whole charge |
| P1 return | credits_counted | moves | gated by payer_start_days: with every charged day covered the refundable part is the payments plus the credits counted, capped at the paid part |
| P1 return | transfer_paid_part | moves | strict @task world |
| P1 return | refund_order | moves | strict @scratch: same-day check of 150.00 |
| P2 authorization | covered_run_end | moves | strict @scratch: +2150.00 cash deposit |
| P2 authorization | coinsurance_share | moves | strict @scratch: +2150.00 |
| P2 authorization | run_year_rate | moves | strict @scratch: +2150.00 |
| P2 authorization | hold_first_night | moves | strict @scratch: +2150.00 |
| P2 authorization | held_room_tier | moves | strict @scratch: +2150.00 |

### Round 6 probe table (task 0, scratch copies; every row = rule outcome)
| probe | outcome |
| --- | --- |
| P1 second ancillary transfer the same date, recorded later | first-recorded transfer kept |
| P1 no ancillary transfer | nothing |
| P1 transfer returned as duplicate | nothing (no paid part) |
| P1 applied trust payment posted on another date | authorization tier |
| P1 no applied payment (charge then mostly unpaid) | authorization tier, refundable shrinks with the unpaid balance |
| P1 no applied payment and no authorization | whole transfer |
| P1 applied payment capped at 90.00 | paid part 90.00 |
| P1 payer-covered-item credit on the consolidated-tier charge | counted |
| P1 price-error credit | counted |
| P1 account moved to the private tier | every credit counted |
| P1 later card payment | others first |
| P1 no active Part A, no eligible case | nothing |
| P2 notice delivered the departure day | both nights build up |
| P2 no transfer notice | no night |
| P2 notice before the departure (planned) | from the first held day |
| P2 later unpaid-hold notice | ignored (transfer notices only) |
| P2 late election (held from Oct 20), notice Oct 19 | from the first held day Oct 20 |
| P2 hold returned | no build-up, run to yesterday |
| P2 latest charge at 217.00 / no coinsurance charge on the episode | 2026 days at 217.00 either way |
| P2 Plan K before the run | every coinsurance day at the share |
| P2 no active episode | no run-up |
| P2 second item charge the same date, recorded later | first-recorded charge named |

### Round 6 pairwise method-tier table (distinguishing input per pair)
| pair | distinguishing input |
| --- | --- |
| P1 payer_start_days / credits_counted | payer start date vs ancillary tier |
| P1 payer_start_days / transfer_paid_part | payer start date vs applied payment / authorization |
| P1 payer_start_days / refund_order | payer start date vs other payments' dates |
| P1 credits_counted / transfer_paid_part | credit reason by tier vs applied trust payment |
| P1 credits_counted / refund_order | credit reason by tier vs payment dates |
| P1 transfer_paid_part / refund_order | applied amount vs other payments' dates (pro rata uses the paid part) |
| P2 covered_run_end / coinsurance_share | last covered date / leave start vs Medigap letter |
| P2 covered_run_end / run_year_rate | run end date vs year of each run day |
| P2 covered_run_end / hold_first_night | leave start ends the run vs notice date starts the held nights |
| P2 covered_run_end / held_room_tier | run end vs room tier held |
| P2 coinsurance_share / run_year_rate | share percent vs daily rate (operation: percent vs rate) |
| P2 coinsurance_share / hold_first_night | Medigap letter vs notice date |
| P2 coinsurance_share / held_room_tier | share percent vs room tier rate |
| P2 run_year_rate / hold_first_night | coinsurance day rate vs held night count |
| P2 run_year_rate / held_room_tier | coinsurance rate by year vs bed-hold rate by tier |
| P2 hold_first_night / held_room_tier | first night allowed vs tier priced |

### Round 6 residual (task 1): what bounds P3 and P6
- P3 trust_ext_patient_pay_transfer keeps 2 genuine factors (named_month_standing, named_month_amount); credited_reconciliation_amount and credited_not_eligible_amount stay one posted-or-projected formula. The quantities a standing patient pay transfer reads are fixed by single-rule sentences: medicaid_evt_patient_pay_actual "the difference is billed with charge basis trueup_increase, and where it is lower, the estimate is reduced by the difference with reason trueup_decrease" and "Estimates billed for months before the eligibility start date are reduced with reason not_eligible_month" (one operation each: posted, or projected while the trueup days run); medicaid_evt_payments "A patient pay payment names the charge it pays and is applied only up to that charge's open balance"; trust_evt_bill_transfers "A transfer pays at most the open balance of the named charge and never exceeds the available balance" (a cap the task world never reaches). No other leaf of the transfer carries a categorical or anchor choice in the medicaid or trust charter, and the claimed policy set has no richer trust write for this tree (round 3 review: interest credits, deposits, statements and conveyance carry at most the tier threshold and the year rate).
- P6 trust_ext_spare_withdrawal keeps 3 genuine factors (resident_allowance_kept, coming_patient_pay_kept, recurring_services_kept); ancillary_bills_kept and bed_hold_bills_kept stay open-balance-plus-accrual. bedhold_evt_payments_adjustments "Charges on an ended reservation stay due until paid" and ancillary_evt_payments_credits "A payment names the charge it pays and is applied only up to its open balance" make every open bill one sum; the only accrual with distinct anchors (a hold in progress: notice, room tier, schedule) needs a hold in progress, and a Medicaid-eligible resident's hold builds no private night inside the payer's reserved days (bedhold_agg_payer_day_limits).
- So task 1 stays at P3 2/4 and P6 3/5 against the draw [5, 5, 4, 4]; P4 4/4 and P5 5/5 meet it. Closing it needs a coordinator decision (a different tree for task 1, or the P3/P6 members accepted).
- Scratch removed (/tmp/trust_0074).
REWORK round 6: gates 7/7 green

## Round 7 (rework of revision_6) — progress
- Started. Items: R6-1 (P3 credited_reconciliation_amount, credited_not_eligible_amount; P5 block_covered_end, block_plan_share; P6 ancillary_bills_kept, bed_hold_bills_kept), R6-4 (P2 run_year_rate year-end anchor), R6-5 floor (P3 2/4, P5 3/5, P6 3/5). Task 0 passed revision_6 and is kept as is apart from R6-4.
- Test applied (revision_6 wording): two tiers coincide when one tier's own method or value, read on the other tier's domain, already gives that tier's value; an absent record (no date, no reservation) gives no value.
- R6-4 (P2 run_year_rate): the guards now read the run's anchor inclusively, `run_anchor <= '2026-12-31'` / `<= '2025-12-31'`: a coverage starting 2026-12-31 with no block booked prices its 2026 day at the 2026 rate; an anchor that is the last booked day 2026-12-31 starts the run in 2027, where the 2026 rate is never read. Task 0 figures unchanged.
- R6-1 / P5 block_covered_end: tier 2 is now "the episode carries any other last covered date" (the owed days run through it, never past the block's last day) and the fall-through is "the episode carries no last covered date" (every day the charge priced). Tier 2 read on the fall-through domain has no date; the fall-through read on tier 2's domain counts days past the last covered date. Task 1 takes tier 2 (12-30 recorded); figures unchanged.
- R6-1 / P5 block_plan_share: the ladder is now the coverage lookup only (Plan K -> K plan_k_share_pct, Plan L -> K plan_l_share_pct, full-coinsurance plan or QMB -> 0, otherwise -> K whole_coinsurance_pct = baseline); which owed days take that share (every day when it took effect by the block's first day, the days the coverage office charged the secondary party for when it took effect inside the block, none otherwise) is a plain sentence, so no tier reads the secondary charge. Figures unchanged.
- P5 now counts 5 (block_covered_end, center_borne_days, block_plan_share, service_year_rate, coinsurance_refund_order).

### Round 7 T1/T2 table (P5, task 1; T2 scratch = 2 hospital days reversed on the block so the all-baseline excess is positive)
| factor | T1 (task world) | T2 |
| --- | --- | --- |
| block_covered_end | moves | strict @task world and @scratch |
| center_borne_days | moves | strict @task world and @scratch |
| block_plan_share | moves | strict @task world and @scratch |
| service_year_rate | moves | strict @task world and @scratch |
| coinsurance_refund_order | moves | strict @scratch (hospital days reversed) |

### Round 7 probe table (P5, scratch copies of task 1; every row = rule outcome)
| probe | outcome |
| --- | --- |
| no last covered date | every day the charge priced; the 12-31 booking-error day then falls inside the covered window and is taken off |
| last covered date after the block | capped at the block's last day |
| QIO upheld, decision 12-31 | through the later date 12-31 |
| Plan K effective inside the block | the 8 secondary-charged days take the share |
| Plan K effective after the block | whole coinsurance |
| Plan L / QMB / no Medigap | 25 / 0 / whole |

### Round 7 pairwise method-tier table (P5)
| pair | distinguishing input |
| --- | --- |
| block_covered_end / center_borne_days | last covered date vs uncertified reversals or lapsed certification |
| block_covered_end / block_plan_share | last covered date vs Medigap letter / QMB |
| block_covered_end / service_year_rate | last covered date vs year of service |
| block_covered_end / coinsurance_refund_order | last covered date vs other payments' dates |
| center_borne_days / block_plan_share | certification records vs coverage letter |
| center_borne_days / service_year_rate | certification records vs year of service |
| center_borne_days / coinsurance_refund_order | certification records vs payment dates |
| block_plan_share / service_year_rate | share percent vs daily rate (percent vs rate) |
| block_plan_share / coinsurance_refund_order | coverage letter vs payment dates |
| service_year_rate / coinsurance_refund_order | year of service vs payment dates |

### Round 7 residual: P3 and P6 (R6-1 members and R6-5), with the base sentences that bound them
- P3 credited_reconciliation_amount / credited_not_eligible_amount: each is "the reductions posted" or "the projection while the trueup days run". medicaid_evt_patient_pay_actual: "Within the trueup days after the approval notice, every month billed as an estimate is reconciled: ... where it is lower, the estimate is reduced by the difference with reason trueup_decrease. Estimates billed for months before the eligibility start date are reduced with reason not_eligible_month". A posted-reductions tier is a sum, which reads 0 wherever none is posted, so it meets any nothing tier; the charter gives no third method (the trueup basis is one formula), and the other leaves of the transfer are single rules (medicaid_evt_payments "applied only up to that charge's open balance"; trust_evt_bill_transfers "A transfer pays at most the open balance of the named charge and never exceeds the available balance"). P3 stays at 2 (named_month_standing, named_month_amount).
- Replacing P3 (option 2) was re-checked against the claimed trust event types: a third return in task 1 would have to be a Medicare or bed-hold return (already P5 and P4); an ancillary, private or Medicaid overcharge is credited by the owning office itself (ancillary_evt_payments_credits "credited in full or for the excess, naming the charge"; private and medicaid adjustments likewise), so a trust return would duplicate an owed office write; interest credits are posted once a month on the last day (trust_evt_interest "A month is credited once") and the frozen day is not a month end; conveyance needs a discharge or death, which ends the POA's withdrawal (trust_evt_withdrawals "A power of attorney authorizes nothing after the resident's death").
- P6 ancillary_bills_kept / bed_hold_bills_kept: open balances (bedhold_evt_payments_adjustments "Charges on an ended reservation stay due until paid"; ancillary_evt_payments_credits "A payment names the charge it pays and is applied only up to its open balance") read 0 where nothing is open, so they meet the nothing tier. The only bed-hold keep with a categorical choice (room tier priced for a hold in progress) needs a hold in progress, and for a Medicaid-eligible resident the held nights are payer-reserved, with private nights only under a private extension that starts on the date the reservation records (bedhold_agg_payer_day_limits, bedhold_election). That adds at most one factor, so P6 would reach 4 of 5. P6 stays at 3.
- Task 1 therefore stays below the draw [5, 5, 4, 4] at P3 2/4 and P6 3/5 (P4 4/4, P5 5/5). Closing it needs a coordinator decision on these two policies.
- Scratch removed (/tmp/trust_0074).
REWORK round 7: gates 7/7 green

## Round 8 (rework of render_r1 findings) — progress
- Started. Items: render_r1 Finding 1 (available balance: every held deposit), Finding 2 (0.00 patient pay read as absent), Finding 3 (PNA retained on Medicaid payee accounts), non-blocking notes P2 (p0/plan_effective in the baseline), P4 (billed_rate reads a factor binding), P2/P6 (no room tier -> 0); each with its class across all six policies.
- Finding 1 (available balance; class = every balance a transfer or withdrawal may draw on): P3 and P6 now define the available balance as the account balance less every deposit whose available date is after today (trust_msr_available_balance; trust_evt_withdrawals "a check deposit still on hold is not available"). P2's spare balance, which caps the transfer its authorization makes, subtracts the same held deposits (trust_evt_bill_transfers "never exceeds the available balance"). The DSL sums it exactly with no scope: held = every deposit less the deposits whose available date is today or earlier (SUM with date_field available_date and an unbounded within_months, whose month test is never negative for a date on or before today). P1, P4 and P5 are returns and read no balance.
- Finding 2 (0.00 read as absent; class = every presence test on an amount): P3 named_month_amount tests the eligible case (EXISTS), not its patient pay amount; P3 recon_credit drops the patient-pay truthiness guard; P3 posted trueup / not-eligible reductions are detected by count of rows (tu_n, ne_n), not by a positive sum; P1 paid part detects the applied trust payment and the per-bill authorization by count of records (applied_n, auth_n), so a 0.00 authorization gives a paid part of 0.00; P1 earlier unauthorized/duplicate returns by count. Reviewed and left: P5 secondary-charge day count and P6 open-balance clamps (a charge and its day count are never posted at zero: medicare_evt_coinsurance "a zero amount is not posted"; a negative open balance keeps nothing by the rule's own words).
- Finding 3 (PNA retention; class = every bill transfer the extended policies size): trust_evt_bill_transfers "for a Medicaid payee account the personal needs allowance stays in the account" (tier params center_is_representative_payee and medicaid_pna_retained). P3 caps the transfer at the available balance less the eligible case's personal needs allowance on a Medicaid representative payee account; P2's spare balance subtracts the same allowance on such an account (new medicaid branch read). P6 already keeps the allowance for every eligible case; returns are not transfers out.
- Non-blocking notes: P2 baseline now carries the plain sentences on which coinsurance days take the share and which held nights build up (and P5's baseline its plain share-days and several-booking-error sentences, P1's its no-paid-part sentence) so every plain binding is described in the computation; P4's schedule sentence now says outright that a charge billed before 2025-07-01 keeps its own daily rate (billed_rate quoted from it); P2 and P6 say that where no room tier is recorded no night is priced.
- Every scored figure, all-baseline figure and factor_sensitivity figure in both tasks is unchanged (harness check over all six computations); T1/T2 tables unchanged (no tier changed; only presence tests and the balance/allowance reads).
- Probe sweep (scratch copies; rule outcomes): one check on hold -> excluded; held check then a same-day-available pension -> the check still excluded; two checks on hold -> both excluded; a check available today -> available; a check available next month -> excluded; Medicaid payee tier with a low balance -> P3 capped at the balance less 45.00, self-directed capped at the balance; patient pay 0.00 -> eligible month owes 0 and the in-flight reconciliation counts the whole estimates; partial month with patient pay 0.00 -> 0; authorization 0.00 with no applied payment -> paid part 0; no authorization -> whole transfer; bed-hold charge billed before 2025-07-01 -> its own daily rate; no room tier anywhere -> no night priced.
- compute_basis quote sweep and stale-text sweep clean (no "most recent deposit" wording left; prerequisite fields carry no world values).
- Scratch removed (/tmp/trust_0074).
REWORK round 8: gates 7/7 green

## Round 9 (rework of policy_kb revision_1 source items) — progress
- Started. Items routed: S1 (P4 vs the published Bed-Hold charge agreements), S2 (P5 baseline compute vs rule), S3 (task 0 September coinsurance priced at the 2025 rate), S5 (Medicare payment method of the trust transfer), S6 (held room tier vs a converted agreement's tier), S7 (owed Medicaid reconciliation moving P3), S8 (resources above the MA limit on 2026-07-01); plus the bounded seed pass over every other-product row of both worlds. R7-1/R7-2 waiver stands.

### Round 9 seed pass (every other-product row of both worlds, re-priced or re-checked against docs/<product>/ as of its posting date)
| task | table | row | kind | re-priced / checked as of its posting date | verdict |
|---|---|---|---|---|---|
| 0 | medicare_coverages | b053bc47 | Medicare Part A with Medigap Plan K | variant Medicare Part A with Medigap Plan K / plan K / QMB False; coverage 2026-09-09..open; prior SNF days 18; recert 2026-09-21 | consistent |
| 0 | medicare_coverages | 3a65968a | Medicare Part A Without Supplemental Coverage | variant Medicare Part A Without Supplemental Coverage / plan  / QMB False; coverage 2026-07-28..2026-08-14; prior SNF days 0; recert 2026-08-10 | consistent |
| 0 | medicare_ledger | 5acd9803 | medicare_days_booked | 4 days 2026-07-28..2026-07-31 (span 4), band days_1_20, benefit days 1-4 (ok) | consistent |
| 0 | medicare_ledger | 3cf18784 | medicare_days_booked | 14 days 2026-08-01..2026-08-14 (span 14), band days_1_20, benefit days 5-18 (ok) | consistent |
| 0 | medicare_ledger | 6513270e | medicare_days_booked | 2 days 2026-09-09..2026-09-10 (span 2), band days_1_20, benefit days 19-20 (ok) | consistent |
| 0 | medicare_ledger | d23f0824 | medicare_days_booked | 20 days 2026-09-11..2026-09-30 (span 20), band days_21_100, benefit days 21-40 (ok) | consistent |
| 0 | medicare_ledger | 9531985d | medicare_coinsurance_charge | 20 x 217.0 = 4340.00 vs 4340.0 (resident) | consistent (S3): 20 x 217.00 = 4340.00, the 2026 rate of the days of service, whole share before Plan K |
| 0 | medicare_ledger | 36f675cc | medicare_coinsurance_payment | check 4340.0 on 2026-10-13 | consistent |
| 0 | bedhold_reservations | e2a3bb8b | Medicare Skilled Stay Hospital Leave Bed Hold | held, leave 2026-10-19 (emergency 2026-10-19 15:40), held Semi-Private Long-Term Care Room 517-A, elected 2026-10-20, private start 2026-10-19, return , end , held_days 0, balance 0.0 | consistent (S6): Medicare skilled-stay hospital hold; semi-private bed 517-A taken at the 09-09 Part A start, after which the converted agreement keeps its private-room tier (private_tier_placement) |
| 0 | bedhold_elections | 9b0a02c2 | hold | hold by representative 2026-10-20T10:15:00-04:00 effective 2026-10-19 | consistent |
| 0 | bedhold_ledger | f11a3537 | bedhold_notice_delivered | transfer_notice to representative at 2026-10-20 09:00 | consistent |
| 0 | ancillary_accounts | 1e5f526d | Ancillary Account, Medicare Part A Consolidated Billing | open tier from 2026-09-09, balance 15.03 | consistent |
| 0 | ancillary_requests | 82ef6a02 | recurring_start | oxygen_concentrator 2026-08-15T15:05:00-04:00 | consistent |
| 0 | ancillary_requests | c4fbcc95 | optional_item | beauty_barber 2026-09-15T09:40:00-04:00 | consistent |
| 0 | ancillary_requests | 703a846d | optional_item | nonmedical_transport 2026-09-22T14:05:00-04:00 | consistent |
| 0 | ancillary_ledger | edae3fb5 | ancillary_recurring_charge | oxygen_concentrator 2026-08 17/31 days, amount 101.45 | consistent |
| 0 | ancillary_ledger | 55df5022 | ancillary_payment | {'entry_date': '2026-09-14', 'payment_method': 'check', 'amount': 101.45} | consistent |
| 0 | ancillary_ledger | f6197e8a | ancillary_item_charge | 1 x 28.0 = 28.0 beauty_barber 2026-09-18 | consistent |
| 0 | ancillary_ledger | 7cba4544 | ancillary_payment | {'entry_date': '2026-09-24', 'payment_method': 'check', 'amount': 28.0} | consistent |
| 0 | ancillary_ledger | 4d106878 | ancillary_item_charge | 1 x 115.7 = 115.7 nonmedical_transport 2026-09-26 | consistent |
| 0 | ancillary_ledger | 1e5a41d1 | ancillary_recurring_charge | oxygen_concentrator 2026-09 30/30 days, amount 185.0 | PREMISE: billed the whole September at the Part B tier's 185.00 although Part A bundles it from 09-09; credited by 6b0d549b (22/30 x 185.00) - the history the payer-covered return rests on |
| 0 | ancillary_ledger | 36c7a8ef | ancillary_payment | {'entry_date': '2026-10-08', 'payment_method': 'trust_transfer', 'amount': 100.0} | consistent |
| 0 | ancillary_ledger | dfc17ed4 | ancillary_payment | {'entry_date': '2026-10-08', 'payment_method': 'check', 'amount': 50.0} | consistent |
| 0 | ancillary_ledger | 6b0d549b | ancillary_credit | {'entry_date': '2026-10-15', 'credit_reason': 'consolidated_billing_item', 'amount': 135.67} | consistent |
| 0 | private_agreements | 8648f1bd | Private Long-Term Care Room | payer_converted signed 2026-07-27 admitted 2026-07-28 notice  room change none converted 2026-09-09 to medicare_part_a, balance 0.0 | consistent: private room from 08-15 at 436.00; converted to Part A 09-09; no room change recorded on a converted agreement |
| 0 | private_ledger | e5e8ba86 | private_room_board_charge | 2026-08 17 x 436.0 = 7412.00 vs 7412.0 (Private Long-Term Care Room; schedule 436) | consistent |
| 0 | private_ledger | 26c0ca2f | private_deposit_received | {'entry_date': '2026-08-15', 'payment_method': 'check', 'amount': 13080.0} | consistent |
| 0 | private_ledger | c08e58a3 | private_payment | {'entry_date': '2026-08-15', 'payment_method': 'check', 'amount': 7412.0} | consistent |
| 0 | private_ledger | 8c7bd12f | private_room_board_charge | 2026-09 30 x 436.0 = 13080.00 vs 13080.0 (Private Long-Term Care Room; schedule 436) | consistent |
| 0 | private_ledger | cf6ba8dc | private_payment | {'entry_date': '2026-09-08', 'payment_method': 'check', 'amount': 13080.0} | consistent |
| 0 | private_ledger | 8d116ece | private_adjustment | {'entry_date': '2026-09-09', 'adjustment_reason': 'payer_conversion_credit', 'amount': 9592.0} | consistent |
| 0 | private_ledger | 90c192cf | private_deposit_disposition | {'entry_date': '2026-09-24', 'deposit_disposition': 'refunded', 'amount': 13080.0} | consistent |
| 0 | private_ledger | 5a17e0cc | private_refund | {'entry_date': '2026-09-24', 'payment_method': 'check', 'amount': 9592.0} | consistent |
| 1 | medicare_coverages | f09ca1dc | Medicare Part A with Medigap Plan K | variant Medicare Part A with Medigap Plan K / plan K / QMB False; coverage 2025-12-08..2025-12-30; prior SNF days 10; recert 2025-12-27 | consistent |
| 1 | medicare_ledger | 4ab5db22 | medicare_days_booked | 10 days 2025-12-08..2025-12-17 (span 10), band days_1_20, benefit days 11-20 (ok) | consistent |
| 1 | medicare_ledger | c642cc84 | medicare_days_booked | 14 days 2025-12-18..2025-12-31 (span 14), band days_21_100, benefit days 21-34 (ok) | PREMISE: booked through 12-31, past the 12-30 last covered date; the corpus remedy (booking-error reversal 5b54dd85) is on file |
| 1 | medicare_ledger | 8de9416f | medicare_coinsurance_charge | 14 x 217.0 = 3038.00 vs 3038.0 (resident) | PREMISE: charged at 217.00 and 100% on 2025 days (corpus 209.50 x 50%); paid in full, so the coverage office's reductions are capped at the open balance 0.00 - the overcharge the coinsurance return corrects |
| 1 | medicare_ledger | 1b124f1c | medicare_coinsurance_payment | card 500.0 on 2026-01-14 | consistent |
| 1 | medicare_ledger | 9e31fcfd | medicare_coinsurance_payment | ach 2538.0 on 2026-01-14 | consistent (S5): the trust transfer posts as an ACH payment of the charge's open balance after the card payment, 2538.00; the 62.00 remainder returned to the payer |
| 1 | medicare_ledger | 06cd724f | medicare_days_reversed | 5 days 2025-12-22..2025-12-26 uncertified_day (span 5) | consistent |
| 1 | medicare_ledger | 5b54dd85 | medicare_days_reversed | 1 days 2025-12-31..2025-12-31 booking_error (span 1) | consistent |
| 1 | medicare_ledger | 5ec43403 | medicare_coinsurance_charge | 8 x 209.5 = 1676.00 vs 838.0 (medigap_carrier) | consistent: the carrier's 50% of 8 owed days x 209.50 = 838.00, open |
| 1 | bedhold_reservations | 80b51476 | Private Pay Therapeutic Leave Bed Hold | returned, leave 2026-05-30 (planned 2026-05-30 10:00), held Private Long-Term Care Room 528, elected 2026-05-28, private start 2026-05-30, return 2026-05-31, end 2026-05-30, held_days 1, balance 421.0 | consistent |
| 1 | bedhold_reservations | 270a15c3 | Private Pay Therapeutic Leave Bed Hold | returned, leave 2026-06-10 (planned 2026-06-10 09:30), held Semi-Private Long-Term Care Room 512-B, elected 2026-06-12, private start 2026-06-10, return 2026-06-25, end 2026-06-24, held_days 15, balance 0.0 | consistent (S1/S6): planned home visit; late notice 06-12 recorded; election within the window holds from departure; semi-private bed 512-B held, taken 06-01 after the agreement converted |
| 1 | bedhold_elections | 7ce51efd | hold | hold by representative 2026-05-28T14:30:00-04:00 effective 2026-05-30 | consistent |
| 1 | bedhold_elections | d1110207 | hold | hold by representative 2026-06-12T15:30:00-04:00 effective 2026-06-10 | consistent |
| 1 | bedhold_ledger | d54d6b82 | bedhold_notice_delivered | transfer_notice to representative at 2026-05-28 14:00 | consistent |
| 1 | bedhold_ledger | 709b75b1 | bedhold_day_booked | 1 days 2026-05-30..2026-05-30 resident_private (span 1) | consistent |
| 1 | bedhold_ledger | b39cc7a7 | bedhold_charge | 1 x 421.0 = 421.00 vs 421.0 | consistent |
| 1 | bedhold_ledger | d5af2fdf | bedhold_notice_delivered | transfer_notice to representative at 2026-06-12 09:00 | consistent |
| 1 | bedhold_ledger | f0840981 | bedhold_day_booked | 21 days 2026-06-10..2026-06-30 resident_private (span 21) | PREMISE: booked through 06-30 at month end although the leave ended 06-25; the six nights after the return reversed 10-15 (5227974d) |
| 1 | bedhold_ledger | 49354ce0 | bedhold_charge | 21 x 436.0 = 9156.00 vs 9156.0 | PREMISE: 21 nights at 436.00 (private room, 2026 schedule) for a semi-private bed held on June nights (base rule: 13 chargeable nights x 384.00) - the overcharge the bed-hold return corrects; a single-entry returned Private Pay Therapeutic Leave hold, priced by no bed-hold charge agreement |
| 1 | bedhold_ledger | a5933d19 | bedhold_payment | {'entry_date': '2026-07-15', 'payment_method': 'card', 'amount': 1000.0} | consistent |
| 1 | bedhold_ledger | a39345fe | bedhold_payment | {'entry_date': '2026-07-15', 'payment_method': 'trust_transfer', 'amount': 8156.0} | consistent |
| 1 | bedhold_ledger | 5227974d | bedhold_day_reversed | {'entry_date': '2026-10-15', 'from_date': '2026-06-25', 'day_count': 6, 'adjustment_reason': 'returned_earlier'} | consistent |
| 1 | ancillary_accounts | 359082c2 | Ancillary Account, Medical Assistance | open tier from 2026-07-01, balance 70.0 | consistent |
| 1 | ancillary_requests | 8680b9fe | recurring_start | cable_tv 2026-06-30T11:00:00-04:00 | consistent |
| 1 | ancillary_requests | f24ada98 | optional_item | beauty_barber 2026-09-14T09:30:00-04:00 | consistent |
| 1 | ancillary_requests | e94156fb | recurring_cancel | cable_tv 2026-09-26T13:40:00-04:00 | consistent |
| 1 | ancillary_requests | d547f1e1 | recurring_start | cable_tv 2026-10-03T15:20:00-04:00 | consistent |
| 1 | ancillary_ledger | 614dc436 | ancillary_recurring_charge | cable_tv 2026-07 31/31 days, amount 42.0 | consistent |
| 1 | ancillary_ledger | 99a49eb7 | ancillary_payment | {'entry_date': '2026-08-12', 'payment_method': 'check', 'amount': 42.0} | consistent |
| 1 | ancillary_ledger | 0eee9576 | ancillary_recurring_charge | cable_tv 2026-08 31/31 days, amount 42.0 | consistent |
| 1 | ancillary_ledger | 1c9057b2 | ancillary_payment | {'entry_date': '2026-09-11', 'payment_method': 'check', 'amount': 42.0} | consistent |
| 1 | ancillary_ledger | ea78a37a | ancillary_recurring_charge | cable_tv 2026-09 30/30 days, amount 42.0 | consistent |
| 1 | ancillary_ledger | 1ab23b36 | ancillary_item_charge | 1 x 28.0 = 28.0 beauty_barber 2026-09-15 | consistent |
| 1 | medicaid_cases | 0fe56a94 | Medical Assistance Nursing Facility Care, Standard Patient Pay | eligible, applied 2026-06-12 from 2026-06-01, eligible 2026-07-01, pp 1276.4 from 2026-07-01, income 1434.7 | consistent |
| 1 | medicaid_ledger | 0e43617b | medicaid_patient_pay_charge | {'entry_date': '2026-06-12', 'service_month': '2026-06', 'charge_basis': 'estimated_pending', 'amount': 1389.7} | consistent |
| 1 | medicaid_ledger | 215062fe | medicaid_patient_pay_charge | {'entry_date': '2026-07-01', 'service_month': '2026-07', 'charge_basis': 'estimated_pending', 'amount': 1389.7} | consistent |
| 1 | medicaid_ledger | dace437b | medicaid_patient_pay_charge | {'entry_date': '2026-08-01', 'service_month': '2026-08', 'charge_basis': 'estimated_pending', 'amount': 1389.7} | consistent |
| 1 | medicaid_ledger | 6dd84287 | medicaid_patient_pay_charge | {'entry_date': '2026-09-01', 'service_month': '2026-09', 'charge_basis': 'estimated_pending', 'amount': 1389.7} | consistent |
| 1 | medicaid_ledger | a4dbbec6 | medicaid_patient_pay_charge | {'entry_date': '2026-10-01', 'service_month': '2026-10', 'charge_basis': 'estimated_pending', 'amount': 1389.7} | consistent |
| 1 | medicaid_ledger | 9dc39ce6 | medicaid_patient_pay_payment | {'entry_date': '2026-06-20', 'payment_method': 'check', 'amount': 300.0} | consistent |
| 1 | medicaid_ledger | 9541b2f0 | medicaid_past_due_notice | {'entry_date': '2026-07-12'} | consistent |
| 1 | medicaid_ledger | f812405f | medicaid_patient_pay_payment | {'entry_date': '2026-07-10', 'payment_method': 'check', 'amount': 1389.7} | consistent |
| 1 | medicaid_ledger | 2bf7826e | medicaid_patient_pay_payment | {'entry_date': '2026-08-10', 'payment_method': 'check', 'amount': 1389.7} | consistent |
| 1 | medicaid_ledger | e3919ef1 | medicaid_patient_pay_payment | {'entry_date': '2026-09-10', 'payment_method': 'check', 'amount': 1389.7} | consistent |
| 1 | medicaid_ledger | 763026cd | medicaid_patient_pay_payment | {'entry_date': '2026-10-12', 'payment_method': 'check', 'amount': 150.0} | consistent |
| 1 | medicaid_ledger | 584afaaa | medicaid_pending_accrual | 2026-06 15 x 384.0 = 5760.00 vs 5760.0 | consistent: 15 days in the center x 384.00 (occupied semi-private room, 2025-07-01 schedule) |
| 1 | medicaid_ledger | 0dd31ade | medicaid_pending_accrual | 2026-07 31 x 398.0 = 12338.00 vs 12338.0 | consistent |
| 1 | medicaid_ledger | 974d1095 | medicaid_pending_accrual | 2026-08 31 x 398.0 = 12338.00 vs 12338.0 | consistent |
| 1 | medicaid_ledger | cef14cb1 | medicaid_pending_accrual | 2026-09 30 x 398.0 = 11940.00 vs 11940.0 | consistent |
| 1 | medicaid_ledger | 702565c1 | medicaid_pending_settlement | {'entry_date': '2026-10-14', 'settlement_type': 'denied_moved_to_private', 'amount': 5760.0} | consistent: June accrual settled denied_moved_to_private (before the 07-01 eligibility start) |
| 1 | medicaid_ledger | 0a92f961 | medicaid_pending_settlement | {'entry_date': '2026-10-14', 'settlement_type': 'approved_ma_covered', 'amount': 12338.0} | consistent |
| 1 | medicaid_ledger | f4f77a9f | medicaid_pending_settlement | {'entry_date': '2026-10-14', 'settlement_type': 'approved_ma_covered', 'amount': 12338.0} | consistent |
| 1 | medicaid_ledger | defde29f | medicaid_pending_settlement | {'entry_date': '2026-10-14', 'settlement_type': 'approved_ma_covered', 'amount': 11940.0} | consistent |
| 1 | private_agreements | c2db95d9 | Private Long-Term Care Room | payer_converted signed 2025-12-07 admitted 2025-12-08 notice 2026-04-15 room change none converted 2026-06-01 to medicaid_pending, balance 6315.0 | consistent (S6): Private LTC tier from admission, no room change while active; converted 06-01 so the tier stays (private_tier_placement); June re-charge 15 days x 421.00 = 6315.00 open |
| 1 | private_ledger | e7f7b638 | private_deposit_received | {'entry_date': '2025-12-31', 'payment_method': 'check', 'amount': 12630.0} | consistent |
| 1 | private_ledger | 8c7f5934 | private_room_board_charge | 2025-12 1 x 421.0 = 421.00 vs 421.0 (Private Long-Term Care Room; schedule 421) | consistent |
| 1 | private_ledger | 1b3a9ff3 | private_payment | {'entry_date': '2025-12-31', 'payment_method': 'check', 'amount': 421.0} | consistent |
| 1 | private_ledger | e4dc0e8a | private_room_board_charge | 2026-01 31 x 421.0 = 13051.00 vs 13051.0 (Private Long-Term Care Room; schedule 421) | consistent |
| 1 | private_ledger | 899c81a9 | private_payment | {'entry_date': '2026-01-10', 'payment_method': 'check', 'amount': 13051.0} | consistent |
| 1 | private_ledger | 0bc85e43 | private_room_board_charge | 2026-02 28 x 421.0 = 11788.00 vs 11788.0 (Private Long-Term Care Room; schedule 421) | consistent |
| 1 | private_ledger | 875ed9bc | private_payment | {'entry_date': '2026-02-10', 'payment_method': 'check', 'amount': 11788.0} | consistent |
| 1 | private_ledger | 1cc40f0f | private_room_board_charge | 2026-03 31 x 421.0 = 13051.00 vs 13051.0 (Private Long-Term Care Room; schedule 421) | consistent |
| 1 | private_ledger | c2970a59 | private_payment | {'entry_date': '2026-03-10', 'payment_method': 'check', 'amount': 13051.0} | consistent |
| 1 | private_ledger | 726d5673 | private_room_board_charge | 2026-04 30 x 421.0 = 12630.00 vs 12630.0 (Private Long-Term Care Room; schedule 421) | consistent |
| 1 | private_ledger | 190cb715 | private_payment | {'entry_date': '2026-04-10', 'payment_method': 'check', 'amount': 12630.0} | consistent |
| 1 | private_ledger | adbc8afc | private_room_board_charge | 2026-05 31 x 421.0 = 13051.00 vs 13051.0 (Private Long-Term Care Room; schedule 421) | consistent: May billed in advance 04-25 at 421.00 for 31 days; the private corpus has no adjustment reason for a plain leave day (the 05-30 home-visit night is charged on the bed-hold reservation) |
| 1 | private_ledger | f1fb7195 | private_payment | {'entry_date': '2026-05-10', 'payment_method': 'check', 'amount': 13051.0} | consistent |
| 1 | private_ledger | 9707cba5 | private_room_board_charge | 2026-06 30 x 421.0 = 12630.00 vs 12630.0 (Private Long-Term Care Room; schedule 421) | consistent |
| 1 | private_ledger | 6d3453cf | private_payment | {'entry_date': '2026-06-10', 'payment_method': 'check', 'amount': 12630.0} | consistent |
| 1 | private_ledger | 98dacb9d | private_adjustment | {'entry_date': '2026-06-12', 'adjustment_reason': 'payer_conversion_credit', 'amount': 12630.0} | consistent |
| 1 | private_ledger | cf4a3719 | private_deposit_disposition | {'entry_date': '2026-07-10', 'deposit_disposition': 'refunded', 'amount': 12630.0} | consistent |
| 1 | private_ledger | e8da3864 | private_refund | {'entry_date': '2026-07-10', 'payment_method': 'check', 'amount': 12630.0} | consistent |
| 1 | private_ledger | 1d50d0ae | private_room_board_charge | 2026-06 15 x 421.0 = 6315.00 vs 6315.0 (Private Long-Term Care Room; schedule 421) | consistent: June re-charge span after the approval left June out - 30 days less 15 resident-private hold days = 15 x 421.00 (resumed re-charge rule) |
### Round 9 items
- S1 (P4 vs the published Bed-Hold charge agreements; gold-moving): P4 now names the charge types a bed-hold charge agreement prices (single resident-private entry of an ended Private Pay Hospital Leave hold; opening entry, or closing entry once ended, of a Medicaid Hospital Leave Reserved Bed hold with more than one resident-private entry; opening or closing entry of a released Private Pay Therapeutic Leave hold with more than one) and takes the posted charge as the amount due for them, so no trust rule prices those charges differently from docs/bedhold (exact record test on variant, status, resident-private entry count and the entry's first/last day). Task 1's June leave is now a planned home visit: a returned single-entry Private Pay Therapeutic Leave hold, which no agreement prices, so the base charge rule (each night at the schedule rate of the tier held, 100 percent, no dietary credit) is the bed-hold corpus's own figure. Class: P2 and P6 reserve held nights of a hold in progress at the full bed-hold rate and now say why (an extended-hold percent or dietary credit an agreement applies after the leave ends depends on its final length).
- S2 (P5 baseline compute vs rule): the covered end is now a plain clause read in the baseline too (baseline rule and compute agree; all-baseline gives 217.00, the KB memo's figure). The covered end bore weight only through the old mismatch (the 12-31 day after the last covered date is the booking-error reversal), so it left the ladder; in its place coinsurance_paid_part reads the ACH payment the coverage office applied from the transfer (never more than the transfer), else the authorization, else the whole transfer. Seed: the Jan 12 authorization and Jan 14 transfer are 2600.00 (Jan 5 family check 2540.00); the card payment posted first, the coverage office applied 2538.00 and returned the 62.00 remainder (medicare_evt_payment_posting), posted on the account Jan 16. The other payments are the payments naming the charge less that ACH payment. P5 result unchanged.
- S3 (task 0): 9531985d re-seeded as the Medicare rules produce it, 20 x 217.00 = 4340.00 (payment 36f675cc 4340.00). run_year_rate then bears no weight on this world, so the year rate is a plain sentence again; the run's first day became the factor (run_start_day: after the most recent booked block / the coverage start where none is booked / no run without an active episode; baseline: the coverage start), with the numbering counting only the days booked before the run's first day. P2 result unchanged.
- S5 (Medicare payment method of the trust transfer): kept "ach" and stated in P5's rule and the seed checks: the Medicare accepted resident methods are check, certified check, ACH and card; a transfer of the resident's own funds is an electronic debit, the only fitting method, and P5 identifies it as the ACH payment on the transfer's date.
- S6 (held tier vs converted agreement): task 0 keeps the semi-private bed 517-A held against the private-room agreement: private_tier_placement "Only an open, active agreement changes tier"; the agreement converted on 09-09, the day she took the Part A bed, so no room change can be recorded on it and the reservation is the record of the bed. Task 1 (same class): the agreement's tier change dated after its conversion was not producible; the agreement now keeps its Private Long-Term Care Room tier with no room change, she took semi-private bed 512-B on 06-01 after converting, and the June hold holds that bed; June accrual and re-charge priced accordingly.
- S7 (owed reconciliation moving P3): P3's credited reconciliation and not-eligible amounts now read the case's standing (equal pending estimates: projected from the approval) whether or not any part of the reconciliation is posted; posted reductions are read only where the estimates differ. Probes: nothing posted, July only, all incl. October -> same transfer.
- S8 (resources on 07-01): the 10000.00 family check is deposited 07-06 (available 07-13), after the first moment of July; the bed-hold authorization is 07-13 and the transfer and card payment 07-15; interest recomputed (Jan 0.24, Feb-Jun none, Jul 1.32, Aug 0.61, Sep 0.58); balances at the first moment of Jul/Aug/Sep/Oct 62.24 / 1907.56 / 1878.17 / 1878.75; resource notice 10-14 at 1878.75.
- Scored values moved: task 1 bed-hold return and spare amount (gold, computations, sensitivities, traces, closures, rationale regenerated). Task 0 values and task 1 patient pay transfer and coinsurance return unchanged.

### Round 9 T1/T2 (changed factors and worlds)
| policy | factor | T1 | T2 |
| --- | --- | --- | --- |
| P2 | covered_run_end, coinsurance_share, run_start_day, hold_first_night, held_room_tier | all move | strict @scratch (+6642.39 cash, all-baseline spare 40.00) |
| P4 | hold_notice_night, hold_room_tier, hold_night_schedule, hold_refund_order | all move | strict @task world |
| P5 | center_borne_days, block_plan_share, service_year_rate, coinsurance_refund_order | all move | strict @task world |
| P5 | coinsurance_paid_part | moves | strict @scratch (14 days reversed as hospital days: the cap binds) |
| P6 | all five | all move | strict @task world |
| P3 | named_month_standing, named_month_amount | move | gated (R3-6, unchanged) |
| P3 | credited_* | move | waived class (R7-1/R7-2) |

### Round 9 probe sweep (scratch copies; rule outcomes)
| probe | outcome |
| --- | --- |
| P4 returned single-entry private therapeutic (task world) | base pricing |
| P4 same hold as a returned Private Pay Hospital Leave | agreement-priced: amount due = charge, nothing returned |
| P4 private hospital leave still held | base pricing (agreement applies once ended) |
| P4 released private therapeutic, one entry / two entries (charge on opening) | base / agreement-priced |
| P4 returned private therapeutic with two entries | base pricing |
| P4 Medicaid hospital reserved bed, two entries, opening entry | agreement-priced |
| P5 no ACH on the transfer date / ACH next day | authorization amount (next-day posting is not producible: a transfer posts on its date) |
| P5 no ACH and no authorization | whole transfer |
| P5 second ACH the same day recorded later | first-recorded payment is the transfer's |
| P3 nothing / July only / all posted | same transfer |
| P2 no block booked / no active episode | run from the coverage start / no run |
| held deposits, PNA payee, zero amounts (round 8 probes) | unchanged reads, re-run green |
- compute_basis quote sweep clean; stale-text sweep over rationale, closures, traces, objectives and personas clean (no 4190/209.50 September, no 2538 transfer, no 06-19 deposit, no hospital June hold, no 3280.75/4595.64).
- Scratch removed (/tmp/trust_0074).
REWORK round 9: gates 7/7 green

## Round 10 (rework of policy_kb revision_2: N2)
- Started. Item: N2 (P2 baseline defines the run as the days not yet booked while its compute starts it on the coverage start date); sweep of every baseline sentence of the six policies for text that pre-empts a factor tier or differs from the baseline compute.
- N2 (P2): the plain run sentence no longer says "not yet booked" ("The run is the days of the active Part A episode from the run's first day through the run's end."); the reason that the reserve covers only days the coverage office has not booked now sits in run_start_day's own sentence; "unbilled run" became "run" throughout; the standard-method sentence now says the run starts on the coverage start date and counts every day of the episode from that date, which is exactly the baseline compute (start_off 0, booked_before 0). A reader of the computation document alone starts the run on the coverage start date.
- Sweep of every baseline sentence of the six policies (pre-empting a factor tier or differing from the baseline compute):
  - P3 (same class, the placement note S4): the month-standing ladder sentence left P3's baseline; the baseline keeps "every month's patient pay is the charge as billed" (compute month_standing 'as_billed').
  - P4: the nightly-rate sentence said "the rate schedule in effect that night", which is the night-date tier of hold_night_schedule; it now reads "the rate schedule applying to that night" and the factor sentence "The rate schedule applying to a night follows the date of each night due"; the standard-method sentence now also states the baseline compute for a charge billed before 2025-07-01 (the charge's own daily rate).
  - P1, P5, P6: every baseline sentence matches its baseline compute and names no factor tier (P1 days from the payer's start = every charged day, credits all counted, paid part = whole transfer, transfer first; P5 covered end plain, no center-borne day, whole share, charge's own rate, paid part = whole transfer, transfer first; P6 nothing kept back). P2's other baseline sentences (rate by year, numbering before the run's first day, held nights, first night allowed = first held day, agreement tier, share split) match the compute.
- Every scored, all-baseline and sensitivity figure unchanged (harness check over all six computations); compute_basis quote sweep clean; stale-text sweep clean (one eval necessity text in task 0 updated from "the unbilled run" to "the run").
- Scratch removed (/tmp/trust_0074).
REWORK round 10: gates 7/7 green
