# worklog — private_pay_residency_billing (round 1)

## Step 0 — draw (scripts/draw_counts.py --tasks 2)
task 0: prerequisite_problems=3, factor_counts=[6,4,4,4]
task 1: prerequisite_problems=2, factor_counts=[6,4,6]

## Difficulty pre-check
- Owner=user numeric writes available in this charter: only money the resident/representative pays in (private_deposit_received,
  private_payment). Requests (move-out notice, appeal, room change, payee designation) carry no computable figure; a payment of
  an open charge is embedded in a recorded amount (XF-28). Decision: the user problems are deposit payments whose figure is
  computed from the schedule (task 0: additional deposit on a requested move to a higher-priced room; task 1: security deposit
  when private billing resumes after a Medicare Part A stay).
- DSL limits noted: daily_rate_schedule is a dict (no subscript) -> scheduled rates are carried as this policy's K params
  equal to the base schedule; charge rows hold one rate per span (one row = one tier+rate); credits may mix rates.
- Seeded rows must all be read by a gold read step (closure); cross rows priced per their own charters.

## Task 0 — design thesis (room upgrade with a held hospital leave)
Surface goal: representative pays the additional deposit after her mother's requested move to a private room.
Tree: L leave-day credit -> A room-change credit -> B new-room span charge -> D2 additional deposit (user, root).
Edges: A<-L value_input (days already credited), B<-A value_input (days moved off the old room's charge), D2<-B value_input (rate).

### Task 0 world (frozen 2026-10-21 10:20:00 EDT), Lancaster, resident Margaret Eshleman / rep Carol Fenstermacher (child)
- Agreement since 2025-08-04, Semi-Private LTC (384 -> 398 from 2026-07-01), deposit 11,520 (30 x 384).
- 2026 rate notice delivered 2026-08-20 -> effective for the agreement 2026-10-19 (Aug 20 + 60). Jul-Sep billed at 384
  (prior_rate_notice_hold). October advance (posted 2026-09-25) billed 31 x 398 standard -> late-notice credit owed.
- Requested move to Private LTC (421 -> 436) recorded 2026-10-06 (request on file); advance not yet split.
- Hospital leave Oct 15 20:10 -> returned Oct 18, private bed hold on room 231 (3 held days, charged on reservation 3 x 436).
Problems (one call each):
- C  rate-notice credit on the October advance: Oct 1-18 (18 d) x (398-384) = 252.00            [4 factors]
- A  room-change credit on the October advance: Oct 6-31 (26 d); 13 d carry the late-notice credit
     -> 13 x 384 + 13 x 398 = 10,166.00                                                            [6 factors]
- B  new-room span: days moved off the old charge (26) less held-leave days (3) = 23 x 436 = 10,028.00 [4 factors]
- D2 additional deposit (user): 30 x 436 - 11,520 = 1,560.00                                        [4 factors]
Check: old charge 12,338 - 252 - 10,166 = 1,920 = 5 x 384 (Oct 1-5 at the held rate).

## Resume (agent 2) — breakpoint review
- Read plan/worklog/scratch. Drafts in /tmp/private_0074/pol: C (late-notice credit, 4f), A (room-change credit, 6f),
  B (new-room span, 4f), D2 (additional deposit, 4f). Tree: C -> A -> B -> D2 (user root). Factor multiset [6,4,4,4] OK.
- Correction to thesis: C's leave factor (resident-private booked held days inside the span) takes 3 days off the
  late-notice days, so C = (18-3) x 14 = 210.00 and A then counts 10 credited days inside the move (not 13):
  old charge 12,338 - 210 - A must still leave 5 x 384 = 1,920 at the old room. Numbers recomputed by script.
- D2 held-deposit factor baseline (theoretical deposit instead of the recorded balance) is a straw man -> replace.
- D2 rebuilt (pol2/D2.py): factors deposit_days_record (param: certified-funds 60 / recent late charge 45 / 30),
  deposit_tier_rule (param), deposit_schedule_rule (param), insurer_benefit_rule (method: latest insurer payment / its
  charge days | 3-month insurer total / averaging days | nothing). Held deposit = recorded deposit balance (plain).
  Medicaid tier dropped (XF1: it would read the tier rate assembled from other factors).
- C/A/B kept from predecessor; quantity names made unique per policy (late-notice leave days / the move's leave days /
  the new room's leave days); declined-hold tiers now require a recorded return date (compute already did).
- World t0 re-seeded by /tmp/private_0074/bin/seed0.py: LTC insurer assignment 150/day from Nov 2025 (paid the 3rd of
  the next month), Feb 2026 late charge 98.28 (assessed 2026-03-13), bed-hold transfer notice 2026-10-15 22:40.
- Task-0 policies written to private.extended.yaml (C, A, B, D2); task_tools.py written (4 tools) -> TASK TOOL CONTRACT OK.
  check_extended: policy structure clean (only missing-task cardinality/coverage pending).
- Scratch run (bin/run0.py), handling-time chain C -> A -> B -> D2:
  C 210.00 (baselines: notice_anchor 0.00, leave_kind 196.00, billed_tier 780.00, earlier_source -345.00; all 0.00)
  A 10,208.00 (move_date_source 11,402.00, move_day_rule 9,810.00, leave_inside_move 8,616.00, come_off_source 11,196.00,
    credited_days_rule 10,138.00, credited_step_rule 10,280.26; all 10,362.39)
  B 10,028.00 (span_start 9,592.00, span_leave 9,592.00, priced_tier 9,154.00, schedule 9,683.00; all 8,064.00)
  D2 1,350.00 (days 0.00, tier 0.00, schedule 675.00, insurer 8,100.00; all 0.00)
  Edge skips: skip C -> A 10,348.00; skip A -> B 9,592.00; skip B -> D2 0.00.
  Old-room check: 12,338.00 - 210.00 - 10,208.00 = 1,920.00 = 5 x 384.00 (Oct 1-5 at the held rate).
- Room-change credit rebuilt (pol2/A2.py): leave_inside_move dropped (held days on the new room never change what
  comes off the old charge; its forced-off cross read did not move the result -> gate red and no business sense);
  come_off_source split into come_off_tier_rule + come_off_schedule_rule (both parameter). A no longer reads bedhold.
- History floors: C earlier_source and A credited_step test COUNT(notice-hold charges) > 0; B span_start tests
  COUNT(room_change_proration on the charge) > 0; A credited_days tests COUNT(rate_notice_late on the charge) > 0.
- Credit tools now take adjustment_reason (Enum, full schema set): base credit_once dedup binds it as an action arg.
- Seed rows carry every schema field (None where not applicable) so dedup evidence can cite empty reason fields.
- Task 0 written (tasks/0.json, built by /tmp/private_0074/t0/build.py). Per-task gates: EXTENDED OK, TASK TOOL CONTRACT OK,
  REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. Rationale text still to write.
- Task 0 CLOSED: rationale written (probe table, pairwise method-tier table, cards, draft recomputation) inside 0.json;
  per-task gates 7/7 green (EXTENDED, TASK TOOL CONTRACT, REPLAY, SOLVABILITY, COMPUTE, GROUNDING, SCOPE).
  Probe table (bin/probe0.py): older request / older declined reservation / prior-period credit -> unchanged;
  no bed-hold -> 252.00 / 10,166.00 / 11,336.00 / 1,350.00; two reversals -> D2 5,640.00; late charge >12m -> D2 0.00;
  one insurer payment -> D2 5,874.73.

## Resume (agent 3)
- Task 0 gates re-run: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK (7/7).
  Task 0 stays as is. Next: task 1 (draw 2 prerequisite problems, factor_counts [6,4,6]).

## Task 1 — design thesis (agent 3)
Draw: prerequisite_problems=2, factor_counts=[6,4,6].
Story: long-stay private resident (Private LTC) went to hospital, came back under Medicare Part A (conversion recorded late,
so the October advance was billed before the conversion), Part A ended (NOMNC), she stayed on custodial care; private
billing resumed; she moved (requested) to a semi-private room while on Part A. Business office reverted the agreement but
never credited the October advance nor re-charged the resumed days. Deposit still held (resumed inside the disposition window).
Representative calls to bring the deposit back up (pays it in person).
Tree (chain): X conversion credit on the October advance (agent, 6) -> S re-charge span for the resumed days (agent, 4)
 -> R resumption deposit (user, root, 6).
Edges: S<-X value_input (state form: the advance must carry its payer-conversion credit; the re-charge covers only days the
 advance no longer bills); R<-S value_input (negated state form: deposit rate/tier from the re-charge span; balance owed).
Factors: X {start (method, cross medicare, multi-source), kept reversal selection (method, cross medicare), tier (param),
 schedule (param), earlier-credit days (method), earlier-credit step (param)}; S {start: SNF ABN late (method, cross
 medicare), tier (param), schedule (param), leave days (method, cross bedhold)}; R {days (param), tier (param), schedule
 (param), rate source (method), insurer benefit (method), held deposit above balance owed (method)}.
Known weak points (for the audit): X tier/schedule and R tier/schedule/insurer are situational ladders of the task-0 kind.
- Task 1 world seeded by /tmp/private_0074/bin/seed1.py (58 rows; opening balance 17,566.00, deposit 12,630.00; frozen
  2026-10-21 13:40:00 EDT). X (private_ext_conversion_credit, tool credit_converted_days_12618703) written to the yaml.
  X on the world = 13,065.00 (30 converted days x 436 less 1 netted day x 15); baselines: first day 9,577.00; kept 12,629.00;
  tier 11,925.00; schedule 12,615.00; netted days 13,080.00; netted step 13,079.52; all 8,064.00.
- S (private_ext_resumed_recharge, tool post_resumed_recharge_e6f5843a) written: 6,766.00 after X (17 days x 398); skip X -> 0.00; baselines start 8,358 leave 7,562 tier 7,412 schedule 6,528 all 9,683.
- R (private_ext_resumption_deposit, user tool pay_resumption_deposit_9c511f79) written: 2,357.00 after X and S
  (15 bank-draft days x (398 - 150 insurer share) - held credit 1,363); skip S -> 0.00, skip X -> 4,065.00;
  baselines days 6,077 tier 2,927 schedule 2,147 method 2,702 insurer 4,607 held 0.00; all 0.00.
- XF-17 sibling edit: the additional-deposit policy's overwrite/rule first sentence now names the resumption deposit and
  leaves moves made while another payer covered the stay to it (task 0 gates to be re-run).
- S leave factor fixed after probe (resident-private days of a skilled-stay hold in the month were counted): now the latest resident-private booked days beginning on/after the recorded conversion date. Probe table in /tmp/private_0074/t1/probes.txt (copied into rationale). Building tasks/1.json next.
- tasks/1.json written (build1e.py); per-task gates for task 1: EXTENDED, TOOL CONTRACT, REPLAY, SOLVABILITY (after adding rate-schedule policy_scope at step 13 and a verbatim ACH discriminator), COMPUTE, GROUNDING, SCOPE all OK. Running full suite.
- Task 1 decoy/absent-record probe table (scratch copies, chain X -> S -> R):
    as seeded                                            X= 13,065.00 S= 6,766.00 R= 2,357.00
    older closed Part A episode listed first             X= 13,065.00 S= 6,766.00 R= 2,357.00
    no ended Part A episode (absent record)              X=  9,577.00 S= 9,156.00 R= 4,290.00
    September booking-error reversal (other month)       X= 13,065.00 S= 6,766.00 R= 2,357.00
    skilled-stay leave bed hold booked for Oct 3         X= 13,501.00 S= 6,766.00 R= 1,921.00
    earlier timely ABN as well (latest stays the late one) X= 13,065.00 S= 6,766.00 R= 2,357.00
    ABN option 3                                         X= 13,065.00 S= 8,358.00 R= 3,720.00
    no ABN (absent record)                               X= 13,065.00 S= 8,358.00 R= 3,720.00
    declined Sept reservation records its return         X= 13,065.00 S= 6,766.00 R= 2,357.00
    one dishonored ACH payment in May                    X= 13,065.00 S= 6,766.00 R= 6,077.00
    insurer September remittance not yet received        X= 13,065.00 S= 6,766.00 R= 2,357.00
    isolation placement on the agreement                 X= 11,925.00 S= 6,766.00 R= 3,497.00
- Task 1 pairwise method-tier table: see tasks/1.json design_rationale section 5 (every method ladder: each tier pair differs by an added input, a data-selected anchor or a different denominator; no 'nothing' tier shares a zero domain).
- Docstrings of the three new tools rid of 'first'/'after' sequence wording (earliest day; stay billed privately again).
- Final suite: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK (cache-diff info only; traceability runs after the KB render). Scratch /tmp/private_0074 removed.
ROUND 1: gates 7/7 green

## REWORK round 2 (audits/policy_task/private_pay_residency_billing revision_1) — plan
Item -> fix (charter-wide, every member):
- F-01 late-notice leave days: declare overwrite of base "days billed at a new rate before it took effect are credited with reason rate_notice_late." (self-naming scope; standard = base: no leave days).
- F-02 new-room span schedule: declare overwrite of base "until then the earlier scheduled rate applies" for the requested-move span; late-notice scope excludes a span posted for a requested move (no re-trigger).
- F-03 notice delivered on/after the schedule date: stated explicitly in the late-notice tier.
- F-04/F-05/F-10 move day: move_day_rule removed (days move from the move date, base); room-change credit drops to 4 factors (move date, come-off tier, come-off schedule, netted-credit selector); credited_step removed; span_start_rule re-laddered on anchors (credit first day / span first day / requested date).
- Counts: task 0 multiset [6,4,4,4] kept by moving the 6 to the additional deposit (adds rate method + held-above-owed factors, the real levers already used by the resumption deposit).
- F-06 room-change vs conversion: room-change credit scoped (self-naming overwrite of the base room-change credit clause) to agreements with no recorded payer conversion; the conversion credit takes moved days off at the charge's tier.
- F-07/F-08 leave ladders (late-notice, new-room span, re-charge): declined-with-return tier replaced by a reachable reversal tier (booked days less days reversed on that booking); windows match the days they are subtracted from.
- F-09 late-notice earlier rate: hold charges of the charge's own tier only; result floored.
- F-11 re-charge start tier 2: replaced by "expedited review pending -> none re-charged" (medicare_appeal rule).
- F-12 zero figures: every rule says no entry is made when the figure is zero.
- F-13 a-g: rule/compute aligned (conversion tier condition, skilled-stay hold by status + episode-scoped reversals, latest request, schedule date condition stated, absent request fallback, insurer zero divisor).
- F-14 ties: latest charge = span beginning latest; latest booked leave = leave beginning latest; Part A episode = episode of the latest booked block; month windows stated.
- F-15 deposit tier under isolation = isolation billing tier (both deposits).
- F-16 tool bodies: half-up cents via class static helper, positive amounts, date/month format checks.
- T1-S1 task 1 seed: LOA 2026-10-03 gets its skilled-stay therapeutic bed-hold reservation (declined), notice and election; persona mentions it when asked.
- O-1 task 1 move re-dated to 2026-09-26 (recorded while the agreement still read active, before the late conversion record); O-5 wording; O-7 deposit scopes split by recorded conversion.
- F-16 done: task_tools.py class _Fmt (half-up cents via Decimal, date/month checks); all 7 tools reject non-positive amounts/rates/day counts and malformed dates; balances rounded with the same helper. TOOL CONTRACT OK, REPLAY OK.
- Round 2 progress: task-0 policies reworked (late-notice: F-01 overwrite, F-03 wording, F-07/F-08 reversal tier + notice-window clip, F-09 same-tier hold rate + floor, F-02 requested-move span excluded, F-12, F-14 ties; room-change: 4 factors (move date / come-off tier / come-off schedule / netting selector), F-05 move day to new room, F-06 scope via self-naming overwrite of the base room-change clause, F-13e; new-room span: F-02 overwrite "until then the earlier scheduled rate applies", span start anchors, reversal leave tier with clip to the span start; additional deposit: 6 factors = days, tier (isolation billing tier, F-15), schedule, insurer (zero-divisor stated), held credit (balance owed), secured bed-hold charges (cross-difficulty bedhold), O-7 scope by recorded conversion). A rate-method selector was tried and dropped: it gated tier/schedule (T2 fail, XF-5).
- Task 0 recomputed (scratch /tmp/private_0074/r2): late-notice 210.00, room-change 10,208.00, new-room span 10,028.00, additional deposit 6,918.00. tasks/0.json computations, gold call, traces, closure, contract updated; per-task gates EXTENDED/REPLAY/SOLVABILITY/COMPUTE/GROUNDING OK. Rationale rewrite next.
- Task 1 reworked: conversion credit = first converted day / hospital lead-in (new, real: hospital days before Part A with the hold declined) / kept days (leave-of-absence nights; returned hold with booked days, declined hold -> none, standard all) / credit tier / credit schedule / netting selector (late-notice or billing-error credit); the netted-days / netted-step pair was gated (XF-5, T2 impossible) and is now one selector. Re-charge: start = late ABN / pending expedited review -> none / recorded date; leave = booking with/without reversal, clipped to the first re-charged day; episode = the one of the latest booked block. Resumption deposit = days (same certified-funds / late-charge schedule as the additional deposit), tier (isolation billing tier), schedule, insurer (zero divisor stated), held credit, secured bed-hold charges; the gating rate-method factor removed.
- Task 1 world rebuilt (seed in /tmp/private_0074/r2/seed1.py): hospital 2026-09-29 (hold declined) -> Part A 2026-10-02..08; move to Semi-Private 2026-10-04 recorded while the agreement still read active (O-1); LOA night 2026-10-03 with its skilled-stay hold declined (T1-S1: reservation, notice, election seeded; persona mentions it); February 2026 late charge (paid). Values: conversion credit 13,501.00, re-charge 6,766.00, resumption deposit 5,550.00. Per-task gates for task 1 all OK.
- Round 2 sweeps: every compute_basis quote, baseline sentence, prerequisite sentence and replaced_by verbatim in its own rule (scratch sweep, all 7 policies clean); transitive factor-independence check clean; no factor id inside a tool name; no duplicate tier outcomes; prerequisite fields carry no world values; stale proof text swept in both tasks (old figures, "most recently posted", move-day, declined-with-return, upheld-review wording removed). Decoy/absent-record probe tables, T1/T2 tables and pairwise method-tier tables are in each task's design_rationale (sections 6-8 / 5-7).
- Final gate block: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. Scratch /tmp/private_0074 removed.
REWORK round 2: gates 7/7 green

## REWORK round 3 (audit revision_2) — plan
- N-01 room-change scope: only a move dated before the recorded conversion date on an agreement that records a conversion is in the conversion scope; there the credit takes off only the moved days before the first day the other payer covered (Part A coverage start; span start for other payers). Moves after private billing resumed are ordinary.
- N-02 late-notice exclusion compute fixed (requests table; rule test = tier is the agreement's and first day is the recorded move date or the latest request's date).
- N-03 move date: standard = recorded move date (base); tier = the latest request's date when it names a date on or before the move inside the span (room set aside from that date) — declared by ONE shared scope sentence in the room-change credit and the new-room span (sibling overwrite of base "A move the resident requests reprices from the move date"). Span start standard = recorded move date.
- N-04 leave ladders (late-notice, new-room span, re-charge): tiers = booked resident-private days / a private hold in force with no days booked (days held so far) / none. kept_days removed (base midnight census: a leave night is never charged under the agreement). Resumption insurer ladder = the additional deposit's (latest payment / its charge's days; three-month total / averaging days; nothing).
- N-05/N-06 task 1 seed: insurer remits on the 5th (never above the open balance; no insurer share past due); February late charge on the representative's past-due share.
- N-07 held credit and secured bed-hold factors removed from both deposits; deposit held counts at face. New deposit factors (real: the center bills ancillaries in arrears, so the deposit covers one month of them): recurring-service allowance and personal-item allowance (cross-difficulty ancillary); seeded ancillary accounts/requests/charges/payments priced from the ancillary charter.
- N-08 netting anchors are plain records (late-notice credit days on or after the recorded move date / the qualifying hospital admission), never a factor's output; conversion credit keeps netted days and netted per-day as two factors with a non-zero standard (all credit days), so neither gates the other.
- N-09 T2 for insurer: the recurring-service allowance's standard is non-zero, so every deposit factor moves with the others at baseline.
- N-10 lead-in reads the declined hospital hold whose leave began on the admission date (exact); insurer tie rule stated (the one posted first).
- N-11 late-notice leave window = the day the new rate took effect for the agreement (base effective date), consistent with every notice tier.
- Sibling scope: the two deposits share one identical scope sentence (private_deposit sentence 1).
- Round 3 progress: late-notice (N-02, N-04, N-11), room-change (N-01, N-03 shared scope, N-08 plain netting anchor), new-room span (N-03, N-04, shared scope), additional deposit (N-07 -> ancillary allowances, shared deposit scope, N-10c tie) and resumption deposit (insurer ladder = additional deposit's, ancillary allowances, shared scope) rewritten in the yaml. Next: conversion credit, re-charge, worlds, task files.
- Round 3: conversion credit (kept days dropped, netted days / netted step with non-zero standards and plain anchors, lead-in hold read exact), re-charge leave ladder, deposits (ancillary allowances) done; task 0 world gains its ancillary account/requests/charges/payments; task 0 persona: room set aside from the requested date; task 0 rebuilt (calls at steps 12/14/16/18) and per-task gates OK. Task 1 world rebuilt by /tmp/private_0074/r3/seed1.py (hospital 2026-10-02, Part A 10-05..10-10, ABN 10-14, move 10-07, insurer 100/day on the 5th, late charge 134.82).
- Round 3 close: both design_rationale texts rewritten (scope, overrides, tree card, factor cards, T1/T2 table, pairwise method-tier table, probe table, invariants, objects, persona, standard solution); compute_basis / baseline / prerequisite / overwrite quotes swept verbatim (all 7 policies clean); prerequisite effect/condition texts restated for the set-aside start (room-change netting anchor, new-room span days, additional-deposit edge condition); no world values in prerequisite fields; stale round-2 figures and wording swept.
- Final gate block: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. Scratch /tmp/private_0074 removed.
REWORK round 3: gates 7/7 green

## REWORK round 4 (audit revision_3) — plan
- P-01 the requested-date tier no longer infers a set-aside room. Shared sibling sentence (room-change credit, new-room span) restated: a requested move into a tier with a higher daily rate, recorded before the date named by the resident's latest room-change request logged on or before the move (that date inside the advance's span), reprices from that requested date (the resident is not charged the higher rate before the date she asked for); every other move reprices from the move date. The task 0 world changes accordingly (request names a later date; the move came early). schedule_choice tier 1 keys on a requested move (no isolation placement): base "needs no advance rate-change notice". Leave windows start at the recorded move date (the earlier day) and are clipped by the assembly; the netting window is the plain restatement of the moved days' first day.
- P-02 room-change conversion scope: the cut is a record test (the first day the conversion credit gives back, restated from records: the qualifying admission where its private hospital hold was declined or resident-private days were booked from it, else the Part A coverage start; other payers by the conversion records). No dependence on the conversion credit's presence.
- P-03 leave tier 1 in late-notice, new-room span, re-charge and the conversion lead-in booked tier: booked days less the days reversed against that booking.
- P-04 netting windows equal the credited days' first day (room change: restated move date; conversion: restated first credited day).
- P-05 conversion netting standards: netted days = days of the credits on the charge on or after the later of the recorded conversion date and the span's first day (the standard credited window); netted per-day = the charge's daily rate (base whole-day credit form).
- P-06 recurring allowance tier 1 keyed to months, not charges.
- P-07 deposit prerequisite effects and task 0 closure text: no balance-owed claim, span dates as gold posts them.
- O-13 task 1 ancillary history made its own; O-14 subject tests in the room-change, new-room-span and conversion computes; O-15 handled by the P-06 ladder.
- Round 4 progress: yaml rewritten for P-01 (shared requested-move sentence: a move into a higher-priced tier recorded before the date named by the latest request logged on or before it reprices from that date), P-02 (conversion scope uses private records only: moved days stop before the recorded conversion date while the agreement is still converted, none once it is active again; the conversion lead-in stops before such a move; re-charge tier = agreement tier for any move dated on or before the conversion date; no new-room span on an active-again agreement in that scope), P-03 (booked days less reversed in late-notice, new-room span, re-charge, conversion lead-in), P-04 (netting windows restate the credited days' first day from records), P-05 (netted days standard = credits on/after the standard credited window; netted per-day standard = charge's daily rate), P-06 (recurring tier 1 only when every service ran before the window), P-07 (deposit effects), O-14 (subject tests). Task 0 world: request names 2026-10-08 (logged 2026-09-28, move 2026-10-06); ancillary history own (telephone and cable from April 2026, cable cancelled in August). Task 1 world: own ancillary history (telephone, cable cancelled July, oxygen from 2026-08-12, three items).
- Round 4 close: room-change and conversion netting made exact across credits (room change nets a billing-error credit on top of the late-notice credit; the conversion credit nets room-change and billing-error credits at their own per-day amounts and leaves out the room-change range on a still-converted agreement); late-notice compute owes none on a charge already credited for its reason; netting gate binding renamed ln_net. Probe sweeps (task 0: 16 worlds, task 1: 16 worlds plus order checks on the conversion scope) and T1/T2 tables are in both design_rationale texts; every compute_basis / baseline / prerequisite / overwrite quote verbatim; stale round-3 text swept; no world values in prerequisite fields. Scratch /tmp/private_0074 removed.
- Final gate block: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 4: gates 7/7 green

## REWORK round 5 (audit revision_4) — plan
- Q-01 recurring tier 1 also requires every service to be charged in the latest service month billed (still running); a cancelled service drops to tier 2 (the latest month's charges).
- Q-02 conversion rule rebuilt sentence by sentence (duplicates removed; the first-converted-day ladder, the standard lead-in / tier / schedule sentences restored).
- Q-03 conversion-month moves decided by records the same way whatever the agreement's status: a move dated before the recorded conversion date (that date inside or after the advance's span) gets no room-change credit and no new-room span; the payer-conversion credit gives the advance back from its first credited day, takes the cheaper-room difference off the moved days before it, and the re-charge charges the agreement's tier; a move on or after the recorded conversion date stays under the base room-change rule, the conversion credit and re-charge stopping before it.
- Q-04 no copies: room-change netting counts from the move date the move-date factor decides; conversion netting counts from the first credited day; netted_days_rule removed; the lead-in becomes two additive factors (held hospital days / unheld hospital days); task 1 world: the hospital hold elected late (the first hospital day unheld, two held days booked), premature October bed-hold charge row removed.
- Q-05 room-change prerequisite effect restated.
- Rounding ruling: RND(x + 0.000000001, 2) on every half-up result.
- Round 5 done: yaml (all seven policies; conversion rule rebuilt with no duplicate sentence and its first-converted-day ladder and standard sentences restored; held / unheld hospital-day factors replace the lead-in and the netting-anchor factor; re-charge owes nothing until the agreement is active again and stops before a move recorded on or after the conversion date; conversion credit likewise), task 0 (deposit recomputed, traces), task 1 (late hospital-hold election world, premature October bed-hold charge removed, persona, traces). T2 cells equal to the all-standard figure verified on scratch worlds (late-notice factors on a June 2026 advance; netted step on a Medicaid-pending conversion). Probe sweeps (task 0: 17 worlds; task 1: 19 worlds incl. the Q-03 world processed before and after the reversion and a move after private billing resumed) in both design_rationale texts. Quotes verbatim, no duplicate sentences, no world values in prerequisite fields; stale text swept. Scratch /tmp/private_0074 removed.
- Final gate block: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
REWORK round 5: gates 7/7 green

## REWORK round 6 (audit revision_5)
- R-01: the held / unheld hospital-day pair (one quantity split on a condition the credit does not weigh) is replaced by one hospital_days_rule deciding the first hospital day (departure on the stay's bed hold, the hospital reservation returned on the coverage start / the qualifying inpatient admission where no such bed hold / none); the sixth factor is moved_day_rate_rule (the posted tier's current rate less a cheaper agreement tier's / less the isolation billing tier's / none), the moved days themselves stated once in the assembly from the first credited day. Task 1 world: the move to the semi-private room dated 2026-10-01 (request logged 2026-09-28), before the hospital stay; the hospital hold's held room set to the semi-private room.
- R-02: the re-charge tier rule no longer says the pre-coverage days stayed at the advance's tier; it says the payer-conversion credit gave the advance back (class swept: no other rule carries that framing).
- T2 for netted_step_rule re-verified on a scratch world; probe sweep for task 1 (20 worlds incl. observation night, declined / absent / second / tie holds, dearer move, same-date move, status-independent processing, move after resumption) in its rationale. Quotes verbatim, no duplicates, no world values in prerequisite fields; stale text swept.
- Final gate block: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. Scratch /tmp/private_0074 removed.
REWORK round 6: gates 7/7 green

## REWORK round 7 (audit revision_6)
- S-01: the stay's departure is read from the leave start date every private-pay hospital bed-hold reservation records, whatever its status: exact key — the reservation whose leave began on the qualifying admission date; else a two-date test — the latest leave start inside the charge's span and before the admission among the reservation returned on the coverage start and the first reservation on file in each of the declined, returned, released and expired statuses (observation nights counting as nights away). Hospital days run from that departure (midnight census, held or not); with no departure on file, from the inpatient admission. Probes (declined / released / expired / returned, each with and without an observation night; absent; older same-status reservation listed first; tie; same-date departure) in task 1's rationale; T1/T2 table refreshed; netted-step T2 re-verified on the scratch world; no scored value changed.
- Final gate block: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. Scratch /tmp/private_0074 removed.
REWORK round 7: gates 7/7 green

## REWORK round 8 (audit revision_7)
- T-01 (coordinator route): the conversion policy's self-naming overwrite now scopes it to a coarse exact record test — the resident holds no more than one hospital bed-hold reservation, the reservations counted kind by kind and status by status (first on file per kind and status counting one) and the count standing only where every bed-hold transfer notice on file names a counted reservation. Inside the scope the departure is that one reservation's leave start (any hospital kind, any status; observation nights count); with none on file the hospital days start at the inpatient admission. Out of scope the overwrite restates the base clause and the compute credits the advance's days on or after the conversion date at the charge's daily rate. The first-match-per-status reads are gone, which also closes the stacked-world gap (older same-status hold listed first + observation night) reported in round 7. Probes: one hospital reservation in each status with and without an observation night; two of one status; one of each status; a second hospital kind; a hidden later duplicate; two notices on one reservation; none — table in task 1's rationale.
- Room-change scope sentence no longer describes the conversion credit's internals (it says the payer-conversion credit and the re-charge settle the advance), so it holds in and out of the conversion scope; task 0 rationale aligned.
- No scored value changed; T1/T2 table refreshed; netted-step T2 re-verified on the scratch world; quotes verbatim, no duplicates, no world values in prerequisite fields.
- Final gate block: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. Scratch /tmp/private_0074 removed.
REWORK round 8: gates 7/7 green

## REWORK round 9 (audit revision_8)
- U-01 (out-of-scope fallback): the out-of-scope credit restates the base clause ("Advance room and board billed for days on or after the conversion date is credited with reason payer_conversion_credit") at the charge's daily rate, the conversion date now being the first day another payer source took over the stay — the Part A coverage start date on an agreement active again after Part A, the first day of the span on one active again after another payer whose earlier charge already carries a payer-conversion credit, the recorded conversion date otherwise (never the resumption date). The scope no longer sends ordinary residents out: the stay's departure is first read by exact keys on any hospital kind and status (the reservation whose leave began on the qualifying admission date, else the one returned on the coverage start date); only where neither key matches does the reservation count apply (exactly one hospital reservation, the count standing only where every transfer notice names a counted reservation); with no hospital reservation the hospital days start at the inpatient admission. Out of scope now means: a hospital reservation exists, neither exact key matches and the count does not single it out. Probes (each hold status with and without an observation night; extra therapeutic holds; two hospital holds of one status with and without an observation night; one of each status; another hospital kind; none) in task 1's rationale.
- No scored value changed; T1/T2 refreshed; netted-step T2 re-verified on the scratch world; quotes verbatim, no duplicates, no world values in prerequisite fields; stale scope wording swept.
- Final gate block: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. Scratch /tmp/private_0074 removed.
REWORK round 9: gates 7/7 green

## REWORK round 10 (render_r1 scan findings)
- 1 late-notice exclusion: rule now reads "where a move date is recorded on the agreement, whose first day is that recorded move date or the date named by the resident's latest room-change request" — compute unchanged (both branches need a recorded move).
- 2 room-change conversion carve-out (rule and replaced_by) and the new-room span's sibling exclusion: "after the move date recorded on the agreement" (compute reads last_room_change_date).
- 3 conversion netted window: "on or after the first credited day and on or before the last converted day" (the other credits' "same stretch" follows).
- 4 re-charge schedule tier 2 (rule and ladder): "where a rate notice delivery date is recorded and the notice had not run the rate change notice days by the conversion date recorded on the agreement, it is the preceding schedule" — matches compute; class swept: the resumption-deposit and additional-deposit schedule ladders already equal their computes.
- 5 late-notice, new-room span, re-charge (rules and ladders): "the latest booking of resident-private bed-hold days (the one whose first booked day is latest, the one posted first where two share that day)".
- 6 new-room span and re-charge: the unreversed booked days are counted in a row from the first booked day (late-notice already said so).
- 7 room-change standard come-off schedule: current "once the agreement's rate notice had run its notice days by that date and that date falls on or after the current schedule's effective date, and the preceding schedule otherwise"; class swept (conversion, new-room span, re-charge and deposit standard schedules already carry the effective-date condition).
- No compute changed; every scored, baseline and sensitivity figure unchanged; probes for the changed reads recorded in both rationales; quotes verbatim, no duplicates.
- Final gate block: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. Scratch /tmp/private_0074 removed.
REWORK round 10: gates 7/7 green

## REWORK round 11 (KB audit _kb_verdict revision_1: S1, S2)
- S1 (seed): every seeded row of another product in both task worlds checked against the published bedhold, ancillary and medicare docs as of its posting date (94 rows; table in both rationales). Re-priced / corrected: task 0 bed-hold charge 8b7280d7 (hospital stay charge per hs_rate: all three held days before the agreement's rate took effect 2026-10-19 -> prior 421.00, no dietary credit under 4 days) and reservation 56a357f3 charge_balance to match; recurring-service start requests dated on the services' first charged day (task 0 telephone and cable 2026-04-01; task 1 telephone and cable 2026-02-01, oxygen concentrator 2026-08-12) so no prorated start month is missing. Every other row (recurring proration, statement-day posting, item prices and requests, payments, transfer notices and election timing, bookings, medicare episode, booked days, NOMNC lead, SNF ABN) already matched. No private compute reads these fields: no scored figure changed.
- S2 (wording): both deposits' recurring tier 2 now reads "the total of all the recurring charges billed for the latest service month (the service month of the recurring charge posted latest, the charge posted first deciding where two share that posting date)", ladders likewise; compute unchanged.
- private.extended.yaml changed (S2 wording only); task_tools.py unchanged. Quotes verbatim, no duplicates.
- Final gate block: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK. Scratch /tmp/private_0074 removed.
REWORK round 11: gates 7/7 green
