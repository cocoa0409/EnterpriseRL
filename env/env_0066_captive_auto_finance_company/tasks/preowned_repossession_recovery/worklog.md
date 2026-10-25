# preowned_repossession_recovery — instantiation worklog (env_0066)

Draws (draw_counts.py --tasks 2):
- task 0: prerequisite_problems 2, factor_counts [4, 5, 5]
- task 1: prerequisite_problems 3, factor_counts [4, 4, 5, 4]

## Task 0 — deficiency settlement (Teresa Kowalski) — CLOSED
Tree: preowned_ext_deficiency_settlement (root, owner=user remit_deficiency_settlement_2e6b8900)
  <- value_input/state: preowned_ext_deficiency_quote (quote_deficiency_balance_4c162eac)
     <- value_input/state: preowned_ext_recovery_transport_charge (book_recovery_transport_6b5d55b7)
Gold: transport 497.50 -> quote 3506.09 -> settlement 2774.38 (baselines 135.00 / 4204.47 / 1928.35).
Per-task gates (--task 0): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK;
traceability: only the three unlock tool-name misses (docs not yet published).
Full dossier (factor card, probes, sweeps, verification output) is in tasks/0.json design_rationale.
Revisions: Care-plan rows removed (not reached by any read -> closure mismatch); disposition tier now reads the
posted sale count (history floor); absent-record guards added; weekend surcharge tied to involuntary recoveries (probe).

## Task 1 — reinstatement after involuntary repossession (Marcus Lindqvist) — CLOSED
Tree: preowned_ext_reinstatement_funds (root, owner=user remit_reinstatement_funds_62601f54)
  <- value_input/state: preowned_ext_release_storage_charge (bill_lot_storage_d761f3de)
  <- state_gate/state: preowned_ext_sale_notice_schedule (mail_sale_notice_3d21c42f)
       <- state_gate/state: preowned_ext_redemption_quote (quote_redemption_amount_aa560e9a)
            <- value_input/state: preowned_ext_release_storage_charge
Gold: storage 44.00 / 2 days -> redemption quote 29037.77 -> notice 36 days (sale 2026-11-21) -> reinstatement 5021.95
(baselines 0.00 / 28483.01 / 16 / 3443.86). Edge skips: R 4969.95, Q 28993.77; notice/quote rows missing for the gates.
Revisions: relationship-gate evidence needed every Kestrel contract/lease -> seeded a closed lease and a closed balloon
contract and added their reads (steps shift +2); payment-channel enum replaced by a fixed wire channel (schema enum
closure); customer_id added to the reinstatement tool for the relationship-gate correlation key.
Probe tables, factor cards, sweeps and verification output are in tasks/1.json design_rationale.

## Difficulty-level closure
- 7 extended policies, 7 task tools; task scopes disjoint (task 0: transport charge, deficiency quote, deficiency
  settlement; task 1: release storage, redemption quote, sale notice, reinstatement funds) and jointly cover all policies.
- Cross-state check: task 1's world has the 2026 transport charge already booked (so the task-0 state_due transport
  policy is not lit); task 0's world has its notice mailed and storage billed at the sale (task-1 state_due notice and
  release storage not lit).
- Base clauses retired by two policies name each other's case: storage (release storage vs deficiency-quote storage),
  payoff per-diem sentence (redemption quote vs deficiency quote).
- Prerequisite sentence directions: 3 affirmative ("only after"), 3 negated ("not ... until").
- Traceability: only the seven unlock tool-name misses (KB not yet rendered); no other id/value miss.

## Final gate block (no --task)
EXTENDED OK
TASK TOOL CONTRACT OK
REPLAY OK (0.json 68/68 match, 1.json 47/47 match; deterministic, non-vacuous, 0 errors)
SOLVABILITY OK
COMPUTE OK (suite means branches=40.00 steps=13.00; history_rows_max=54; branches_max=42)
GROUNDING OK
CACHE-DIFF INFO (optional)
SCOPE OK
TRACEABILITY NOT OK — only unlock tool-name provenance (expected before docs are published)
ROUND 1: gates 8/8 green

## REWORK round 2 closure
Audit: audits/policy_task/preowned_repossession_recovery/{_difficulty,0,1}.md (round 1). Item -> change:
- P-1 (state_due chain bottoming in an on_request leaf): statement storage is now state_due — owed whenever an amount to get
  the vehicle back must be stated, whether or not the customer calls; the notice -> redemption quote -> storage chain is
  owed end to end. Opening sentences of storage and redemption quote no longer restate their dependants (O-2).
- P-2 ($0 transport gate): the deficiency prerequisite sentence and condition are scoped to involuntary recoveries; a
  voluntary surrender has no transport charge and none is booked (transport rule + compute return no charge). Storage
  states it is booked even at 0.00 (the storage-gated edges stay satisfiable).
- P-3 (transport booking moment): ONE reading — one transport charge per recovery, from the agency invoice, dated the
  lot-intake date (= the condition report taken at intake); auction delivery is a sale expense. Two-leg tier removed.
  Every lot marker (storage anchor, notice transfer days, redemption projected storage, transport yard hold) reads the
  condition report. Task 0: tow unbooked (late invoice), booked with service date 2026-06-30; task 1: tow 190.00 dated
  its 2026-10-15 intake; both 2025 tows re-seeded at their intake dates per the schedule. Transport tool takes the date.
- P-4 (fee collectability in a state period): reinstatement rule now carries the statutory branch (state-granted cure
  leaves out returned-payment and extension fees, no reserves); redemption fee concession leaves out the same fees while
  any recorded state period runs (company-window concession framed as a payoff concession, not a legal limit).
- P-5 (posting order): both payment tools allocate per base (accrued interest -> principal up to past due -> fees ->
  remainder); reinstatement posts on the posting date (weekend funds post Monday), moves next_due_date and
  payments_made_count by whole installments covered and sets interest_paid_to_date; settlement closes the remainder.
  Both rules state this; no overwrite needed (matches base). Seeded reinstatement precedents follow the same order.
- F-1 (tiers coinciding with fall-through): (a) returned-payment reserve priced at the policy's own share param, not the
  extension good-faith %; (b) lease relationship rates are shares of the contract rate (0.3 / 0.6), never equal to it.
- F-2 (dishonest method label): transport weekend factor relabelled parameter; new honest method agency_yard_hold
  (per-night proportional / flat weekly charge / none).
- F-3 (first-match cross reads): every lease/retail read's rule now says the first active holding the lookup lists is read;
  probed with two active leases (first-listed delinquent -> +5 points tier).
- F-4 (scope conjunct): "sold at auction" removed from disposition tiers and compute; history floor kept through the
  deficiency-notice count tier.
- F-5 (add-ons on a statutory cure): task 1 world is now a discretionary reinstatement (Tier 1+, TX, no recorded state
  period, 1 of 2 reinstatements used); pay-ahead, relationship reserve and returned-payment reserve apply only to
  discretionary reinstatements; a state-granted cure collects past due + late charges + repossession/storage expenses.
- T0-F6 (decoy lease): the 2021 lease is now closed (0 days past due, paid end of term, closed 2024-12-27).
- O-1 disposition fall-through gives no credit (compute guarded); O-2 restated dependencies removed; O-3 release when funds
  post (base), weekend funds post Monday — storage until posting collected, not re-billed (O-10, storage tail); O-4 at 30+
  days the discretionary reinstatement is not offered (stated); O-5 projected storage now at the billed daily amount and
  only through the quote's own good-through (the redemption horizon; tool takes good_through_days), reconditioning kept as
  an expense of disposition the redemption must cover (justified in rule); O-6 "after the sale date up to and including the
  notice date"; O-7 own share param; O-8 a late transport invoice is restated in the deficiency figure the quote states;
  O-9 settlement edge condition says "deficiency quote"; state_gate gates kept as table.field (allowed form); O-11 transport
  charge dated its service (intake) date; O-12 seeded histories follow the extended schedules (redemption quote + zero
  storage on each notice date, 2025 tows per schedule, task-0 sale 28 days after notice as the notice schedule gives).
- XF recipe (per policy x point, all 12 checked): see table below.

### XF recipe check table (E=transport, Qd=deficiency quote, X=settlement, S=statement storage, Q=redemption quote, N=sale notice, R=reinstatement)
| point | E | Qd | X | S | Q | N | R |
|---|---|---|---|---|---|---|---|
| 1 assembly sentence generic, once | ok | ok | ok | ok | ok | ok | ok |
| 2 non-commuting order stated | replacement->adds->round | split->credits->round | pct->base->outside->round | replace->sum->x days->round | interest end->amounts->round | anchors compared before days added | adds once->round |
| 3 factor independence (transitive) | ok | ok | ok | ok | ok (projected days computed independently of interest end) | ok | ok (statutory gate is a plain binding) |
| 4 ownership | ok | ok | ok | ok | ok | ok | ok |
| 5 compute_basis verbatim (scratch sweep bad=0) | ok | ok | ok | ok | ok | ok | ok |
| 6 ties stated (LATEST first listed) | intake CR | sale/notice/storage | quote | intake CR | storage, intake | intake CR | storage |
| 7 counting conventions | days excl/incl stated | days stated | days stated | days, whole years | days, whole years | days, whole years | days, 12 calendar months |
| 8 branches both ways (absent/None) | no assignment, no CR, voluntary | no lease, no notice, no NOIS/storage | no lease | no CR | no CR/storage | no retail, no CR | no retail, no storage, Sunday |
| 9 base clauses restated / sibling named | status + transport | payoff (names redemption), net proceeds, storage (names statement storage) | settlement | storage (names deficiency + reinstatement) | payoff, good-through, redemption (names deficiency) | none needed | amount clause |
| 10 rounding single RND | ok | ok | ok | ok | ok (projection unrounded) | n/a | ok |
| 11 tools: claims = body, formats only, no ordering words | ok | ok | ok | ok | ok | ok | ok |
| 12 proof text current | rationale/closure/traces regenerated for both tasks |

### Pairwise method-tier table (one distinguishing input per pair)
- E agency_yard_hold: 2 nights -> 50.00 proportional vs 9 nights -> 150.00 flat vs same-day -> 0.
- Qd post_sale_accrual_end: voluntary -> 0 post-sale days; involuntary 78 days since sale -> 60; involuntary 30 days -> 40.
- X settlement_base_rule: involuntary+reinstated -> 65% x 1988.01 + 1361.00; voluntary never reinstated -> 65% x 1988.01; otherwise 65% x 3349.01.
- S lot_intake_anchor: intake 2026-10-15 -> 2 days; voluntary -> 4 days; no CR -> 3 days.
- Q redemption_interest_end: state period longer & running -> to state end; company window running -> to 2026-11-04 (139 days); otherwise -> 131 days.
- N reinstatement_right_anchor: longer state period -> its end + 1; window & count below max -> 19 days; otherwise 0 (notice period only).
- R weekend_posting_storage: Saturday -> 2 x billed daily amount (50.00); Sunday -> 1 x tier fee (18.00); weekday -> 0.

### Factor independence (transitive)
No factor binding reads another factor's binding in any policy; shared reads (principal, fees_due, sale_date, quote_amount,
recovery_kind, installment, past_due, state_right_running, lot intake inside each factor's own binding) are plain bindings;
assembly only in interest/credits/billable_days/projected_storage/settlement_pct/result.

### Decoy / absent-record probe table (scratch copies)
- T0 voluntary surrender -> transport 0.00 (not booked); no condition report -> no yard hold (285.00); no lease -> Qd 3391.13;
  two active leases with the delinquent one listed first -> X 2852.01 (rule: first listed is read); no deficiency notice -> Qd 3331.19.
- T1 no retail -> R 6066.50, N 33; recorded 21-day state period -> statutory R 4170.76 and Q leaves out the same fees;
  retail at 15 days -> R 6897.94; Sunday -> R 6450.22; no 2026 condition report -> S 75.00.

### Gate block (rework round 2, no --task)
EXTENDED OK
TASK TOOL CONTRACT OK
REPLAY OK (0.json 72/72, 1.json 48/48; deterministic, non-vacuous, 0 errors)
SOLVABILITY OK
COMPUTE OK (suite means branches=43.50 steps=13.00; history_rows_max=57; branches_max=46)
GROUNDING OK
CACHE-DIFF INFO (optional)
SCOPE OK
TRACEABILITY NOT OK — only the 7 unlock tool-name provenance misses (expected before KB render)
REWORK round 2: gates 8/8 green

## REWORK round 3 closure
Audit: audits/policy_task/preowned_repossession_recovery/{_difficulty,0,1}.md, revision_2. Item -> change:
- R2-X1 (assembly sentences): (a) settlement's combination sentence is now generic ("a schedule that replaces a figure of
  the standard does so first, percentage points the schedules add are added to the percentage next, the percentage is never
  below the minimum ..."); the base method's own sentence carries the fees add-back. (b) reinstatement: the "no reserve or
  installment ahead / reserves and installments below" sentences are gone; each discretionary ladder carries its own
  "a discretionary reinstatement ..." condition (plain shared binding state_right_running), result simply adds.
- R2-X6 (tie on latest reads): the settlement standard read now says "the first one listed where two share a date, and
  nothing where none stands" (rule, baseline, basis); the redemption lot-intake read states its tie too. Mechanical check:
  every policy with a LATEST read states the tie.
- R2-X7 (twelve-month windows): every window (sale notice, redemption concession, statutory exclusion, returned-payment
  reserve) now reads "after the same calendar day twelve months before <date>, up to and including <date>", matching
  0 <= MONTHS(d, NOW) < 12 (probed: a return dated the statement date counts; one dated the same day a year earlier does not).
- R2-X8: (a) transport yard hold states the case of a most recent condition report dated on or before the repossession
  date (no report yet for this recovery) -> no holding charge; (b) redemption and reinstatement daily storage amount state
  the fallback: the tier storage fee where the most recent storage charge covers no billable day or none is on record.
- R2-X9: (a) the reinstatement now declares its own overwrite of the base storage clause; (b) one common tail sentence,
  carried by statement storage, deficiency quote, redemption quote and reinstatement, bills each storage day once: days
  billed through a statement date, collected in a redemption figure or reinstatement amount, or counted into a deficiency
  quote are not billed again; only other days fall to the base charge when the vehicle leaves the lot. Redemption also
  declares the overwrite for the storage it collects in advance.
- R2-X10: the deficiency disposition credit is no longer rounded inside; rounding happens once at the end.
- R2-F1: the yard hold is monotone: the first cap nights at the yard rate, every further night at the long-hold rate
  (7 nights 175.00, 8 nights 190.00, 30 nights 520.00); still a method (single rate vs tiered rate vs none).
- R2-F2: posting-day storage is priced at the vehicle's own billed daily amount on any day (fallback tier fee); the call day
  only decides how many days until posting (Saturday 2, Sunday 1). That factor is now a parameter; the reinstatement's
  method factor is the relationship reserve (15-29 days: the retail contract's own past-due amount; 1-14 days: half of this
  contract's installment; else none).
- T0-S1: (a) the 2026-08-20 deficiency quote, stated while the transport charge was unbooked, is removed; (b)(c) the
  2025-06-17 and 2026-06-30 redemption quotes carry the redemption-quote schedule's amounts (computed by the policy compute
  on the contract as it stood each day) and window-end good-through dates; (d) both leases follow the lease disclosure
  formula (Tier 2 money factor 0.00195, residual 58% of MSRP, acquisition 695, purchase-option fee 350); the old lease is Tier 2.
  Grounding sentences rewritten to cite the redemption-quote schedule.
- T1-S1: (a) 2025-05-19 redemption quote per the redemption-quote schedule; (b) the contract is not Certified Pre-Owned
  (no CPO reduction applies, 7.24 = Tier 1+ 49-60 band); (c) retail Tier 1 72 months at 7.24 with its amortised installment
  and principal; (d) closed lease per the disclosure formula; balloon contract at the Tier 2 24-36 rate 7.24 with a 50% balloon.
- T1-XF12: storage step fact now "through the 2026-10-17 statement date"; the world check states the APR basis; quote
  grounding cites the redemption-quote schedule; sale date, notice days and skip figures refreshed throughout.
- O-r2-1: statutory exclusion and redemption concession are capped at the fees due balance (rule + MN in compute).
- O-r2-2 / coordinator (d): a scheduled sale date on a Saturday or Sunday moves to the following Monday (auction lanes run
  on business days); task 1's sale moves from Sunday 2026-11-22 to Monday 2026-11-23 (days_to_sale 37).
- O-r2-3: the reinstatement rule now says the payment, the return to active and the count are recorded when the funds are
  sent and take effect on the posting date. O-r2-4: the transport charge is dated its service (lot-intake) date by rule.
- O-r2-5: reconditioning kept as an expense of disposition the redemption covers (justified in rule). O-r2-6: state_gate
  gates kept as table.field (allowed form).

### XF recipe re-check (member by member, mechanical where possible)
| point | E | Qd | X | S | Q | N | R |
|---|---|---|---|---|---|---|---|
| 1 assembly generic | replacement/adds | split/credits | replace/points/floor | replace/sum/x days | interest end/amounts | anchors/days/weekend move | adds once (gate in ladders) |
| 6 LATEST tie stated | yes | yes | yes (standard read) | yes | yes | yes | yes |
| 7 windows / counts | days excl/incl | days | days | days, whole years | days, years, 12-month window | days, years, 12-month window, weekday | 12-month windows, weekday |
| 8 branches | no assignment, no CR, CR on/before repo, voluntary | no lease, no notice, no NOIS/storage | no quote, no lease | no CR | no CR, no storage / 0-day storage | no retail, no CR, weekend move | no retail, state right, no storage |
| 9 base clauses | status + transport restated | payoff/net proceeds/storage + common tail | settlement restated | storage + common tail | payoff/good-through/redemption/storage + tail | none | amount + storage + tail |
| 10 rounding | end only | per diem (stated) + end | end | end | per diem (stated) + end | n/a | half/share (stated) + end |
| 12 proof text | rationale, traces, closure, seed checks refreshed in both tasks |

### Pairwise method tiers (round 3)
- E yard hold: 2 nights 50.00 (single rate) / 8 nights 190.00 (tiered) / same day 0.
- Qd accrual end: voluntary 0 post-sale days / involuntary 78 days since sale -> 60 / involuntary 30 days -> 40.
- X base: involuntary+reinstated 65% x (quote - fees) + fees / voluntary never reinstated 65% x (quote - fees) / else 65% x quote.
- S intake anchor: intake 2026-10-15 -> 2 days / voluntary -> 4 / no CR -> 3.
- Q interest end: state period -> state end / window -> 2026-11-04 (139 days) / else 131 days.
- N reinstatement anchor: longer state period -> its end + 1 / window, count below max -> 19 / else none.
- R relationship reserve: retail 20 days -> retail past-due 512.87 / 14 days -> 415.72 / none.

### Factor independence: no factor binding reads another factor's binding; shared reads (state_right_running,
storage_daily_amount, quote_amount, fees_due, installment, lot intake inside each factor's own binding) are plain bindings.

### Decoy / absent-record / boundary probes (round 3)
T0: voluntary -> transport 0.00; only a 2025 condition report (before this repossession) -> no hold, 285.00; yard 7/8/30
nights -> 175.00/190.00/520.00; no lease -> Qd 3391.13; two active leases (delinquent first listed) -> X 2852.01; no
deficiency quote -> X 272.20. T1: no retail -> R 6066.50, N 33; recorded 30-day state period -> statutory R 4170.76; retail
20 days -> R 6579.37; Sunday -> R 6457.22 (one posting day at 25.00); return dated the statement date counts, one dated the
same day a year earlier does not.

### Gate block (rework round 3, no --task)
EXTENDED OK
TASK TOOL CONTRACT OK
REPLAY OK (0.json 71/71, 1.json 48/48; deterministic, non-vacuous, 0 errors)
SOLVABILITY OK
COMPUTE OK (suite means branches=45.00 steps=13.00; history_rows_max=56; branches_max=49)
GROUNDING OK
CACHE-DIFF INFO (optional)
SCOPE OK
TRACEABILITY NOT OK — only the 7 unlock tool-name provenance misses (expected before KB render)
REWORK round 3: gates 8/8 green

## REWORK round 4 closure
Audit: audits/policy_task/preowned_repossession_recovery/{_difficulty,0,1}.md, revision_3. Item -> change:
- R3-X9 (storage-day class, charter): the common storage tail is rewritten once and carried identically (one distinct
  string, mechanically checked) by the deficiency quote, statement storage, redemption quote and reinstatement, in rule
  and replaced_by. It now (a) bills only lot days: the nights before lot intake are the agency's holding, billed on the
  transport charge and never as storage; the lot days run from the day after the lot-intake date for an involuntary
  recovery whose most recent condition report is after the repossession date, from the repossession date for a voluntary
  surrender, else from the day after the repossession date (the same anchors as the statement-storage schedule);
  (b) settles the 0.00 case: every lot day up to and including the latest statement date with a storage charge is billed
  by that charge whatever it came to; (c) states the free days of the sale-time charge: the tier free days less any an
  earlier charge of the same repossession already set against stored days. Task 0 seed: the 2026-07-28 sale storage row
  now counts lot days 2026-07-01..2026-07-28 less the tier free days, its amount and days follow, and the contract's fees
  due balance equals its ledger again. Deficiency quote unchanged (fees and storage credit move together); settlement,
  its sensitivities, the quote's storage-cap sensitivity and all-baseline, tracing, business effects, closure evidence,
  skip and opening-contrast figures, and the rationale re-derived by the compute engine and swept (no stale figure left).
- T0-XF12: the shared grounding sentence on the seed checks is replaced: the 2025 charges are 0.00 because the first came
  on the intake day and the second counted 3 lot days against a first recovery's tier free days; the 2026-06-30 charge is
  0.00 because no lot day had run on the intake day (yard nights on the transport; this repeat involuntary recovery gets no
  statement free days); the sale charge is the lot days less the tier free days. The false "fell within the free days" and
  "not yet billed" wording is gone from every check.
- O-r3-1 (reserve monotonicity): the 15-29-day tier now takes the retail contract's own past-due amount or half of one
  monthly installment of this contract, whichever is larger (rule, basis, ladder, compute MX). Probed monotone in the
  retail days past due. Still a method (reads the other account vs derives from this contract vs none).
- Task 1 retail 14/15 boundary observation: the retail contract now sits 10 days past due at the last nightly cycle
  (due day 6, next due 2026-10-06, first payment, maturity, paid-to and last payment dates moved with it), so a live count
  (11) gives the same tier; persona says "a week or so behind"; traces, near-miss and probe text updated. Nothing scored moves.
- O-r2-4 (back-dated transport): kept by design. The rule dates the transport charge on its service (lot-intake) date,
  as an agency invoice posted late is dated when the service was given; the prerequisite reads "dated on or after its
  repossession date", which the intake date satisfies. Documented, not changed.
- O-r2-5 / O-r2-6: carried as before (reconditioning as a disposition expense; state_gate gates as table.field).

### XF recipe, every point x every policy (round 4)
| point | E | Qd | X | S | Q | N | R |
|---|---|---|---|---|---|---|---|
| 1 assembly generic | ok | ok | ok | ok | ok | ok | ok |
| 2 non-commuting order | yard tiers then sum | split, credits, round | replace, points, floor | replace, sum, x days | end, amounts | anchors, days, weekend last | adds, one round |
| 3 factor independence | ok (script) | ok | ok | ok | ok | ok | ok |
| 4 ownership | ok | ok | ok | ok | daily amount own | ok | daily amount own |
| 5 compute_basis verbatim | 0 misses (script, all policies incl. replaced_by, policy_source, baseline.rule) |
| 6 ties | CR first listed | first listed | first listed | first listed | first listed | first listed | first listed |
| 7 counting | nights | days | days | lot days from anchor | days, 12-month | days, weekday | 12-month, weekday |
| 8 branches | voluntary, no CR, CR on/before repo | no lease, no notice, no storage | no quote | no CR, voluntary | 0-day storage | no retail | no retail, state right, reserve floor |
| 9 base clauses | transport restated | storage tail (new) | settlement restated | storage tail (new) | storage tail (new) | n/a | storage tail (new) |
| 10 rounding | end | per diem + end | end | end | per diem + end | n/a | half/share + end |
| 11 tools | unchanged | unchanged | unchanged | unchanged | unchanged | unchanged | unchanged |
| 12 proof text | n/a | traces swept | traces swept | n/a | n/a | n/a | retail texts swept |

### Pairwise method tiers (round 4)
- E yard hold: single rate up to the cap / tiered beyond / none (same day, CR on/before repo, voluntary).
- Qd accrual end: voluntary none / involuntary sold >= non-accrual days -> capped / else through good-through.
- X base: involuntary + reinstated -> share of (quote - fees) + fees / voluntary never reinstated -> share of (quote - fees) / else share of quote.
- S intake anchor: involuntary late intake -> day after intake / voluntary -> repossession day counted / else day after repo.
- Q interest end: state period / company window / else.
- N reinstatement anchor: longer state period / window with count below max / none.
- R relationship reserve: 15-29 days -> larger of retail past-due and half installment / 1-14 days -> half installment / none.

### Factor independence (round 4): script over every policy: no factor's binding reads another factor's binding.

### Decoy / absent-record / boundary probes (round 4, scratch copies)
T0: duplicate 2026-07-28 storage row listed after the seeded one -> quote unchanged (first listed read); listed before ->
the decoy is read, as the rule says; no active lease -> 3391.13; two active leases, delinquent first -> 3391.13 / X 2843.01;
voluntary -> transport 0.00; no deficiency quote -> settlement falls to the no-quote figure; neither write -> opening
contrast; statement-schedule storage if one were due on the sale date (repeat recovery, 0 free) -> 504.00 vs sale-time
charge with tier free days, as stated in each scope. T1: retail 0 days -> R 6066.50 / N 40; 10 or 14 days -> half
installment tier; 15 days with 300.00 past due -> floor holds (no inversion); 20 days 512.87 -> 6579.37; 20 days 1025.74
-> 7092.24; 30 days -> none; no retail -> R 6066.50 / N 33; Sunday -> R 6457.22.

### Gate block (rework round 4, no --task)
EXTENDED OK
TASK TOOL CONTRACT OK
REPLAY OK (0.json 71/71, 1.json 48/48; deterministic, non-vacuous, 0 errors)
SOLVABILITY OK
COMPUTE OK (suite means branches=45.50 steps=13.00; history_rows_max=56; branches_max=50)
GROUNDING OK
CACHE-DIFF INFO (optional)
SCOPE OK
TRACEABILITY NOT OK — only the 7 unlock tool-name provenance misses (expected before KB render)
REWORK round 4: gates 8/8 green

## REWORK round 5 closure
Audit: audits/policy_task/preowned_repossession_recovery/{_difficulty,0,1}.md, revision_4. Item -> change:
- R4-F1 (reserve tiers coincide): the reinstatement relationship reserve's 15-29-day tier is now half of one monthly
  installment of this contract, rounded to the cent, plus that retail contract's own past-due amount (rule, compute_basis,
  ladder method, compute). Every pair of tiers now differs on its reachable domain (table below), the reserve rises with
  the retail days past due, and the method stays a shape change (a cross-account term only in the top tier). Task 1 sits
  in the 1-14-day tier and its scored figures do not move; the retail-tier texts (traces, near-miss, probes) are updated.
- Self-flagged free-days split (statement storage vs sale-time storage on a repeat involuntary recovery): made
  consistent. The common storage tail (one string, 8 copies) now says the free days of the sale-time charge follow the
  recovery history exactly as for a storage charge through a statement date (none for an involuntary recovery of a
  contract with an earlier reinstatement payment, the surrender free days for a voluntary surrender with none, the tier
  free days otherwise), less any already set against stored days. No record can now be priced two ways: probed, the
  statement schedule on task 0's sale date gives exactly the seeded sale charge. Task 0 seed: the sale storage row now
  counts the 28 lot days with no free days, and the contract's fees due follow; the deficiency quote is unchanged, and the
  settlement, its sensitivities, the quote's storage-cap sensitivity and all-baseline, tracing, business effects, closure
  evidence, skip figures, seed grounding sentence and rationale were re-derived by the compute engine and swept.
- O-r2-4 / O-r2-5 / O-r2-6: carried as documented in round 4.

### Pairwise distinguishing inputs, retail_relationship_reserve (reachable domain: discretionary reinstatement, so no
### other account is 30 or more days past due)
| pair | distinguishing input | why they differ |
|---|---|---|
| 15-29 days vs 1-14 days | retail past-due amount | at 15 or more days past due the retail past-due amount is at least one retail installment, so > 0 |
| 1-14 days vs none | this contract's installment | half of a positive installment > 0 |
| 15-29 days vs none | both terms | sum of two positive terms > 0 |
Probes (task 1 world): retail 0 days or no retail -> no reserve; 1, 10, 14 days -> the half-installment value; 15 days
with 300.00 or 512.87 past due -> each strictly above the 1-14-day value; 20 and 29 days with 1025.74 -> higher still;
two active retail contracts -> the first listed is read.

### Pairwise method tiers (round 5): as round 4, with R: 15-29 days -> half installment + retail past-due / 1-14 days ->
half installment / none. The others are unchanged (no rule or compute change).

### Factor independence (round 5): transitive script over every policy (each factor binding's dependency closure vs every
other factor's bindings): no hit.

### compute_basis sweep (round 5): every compute_basis, replaced_by, policy_source and baseline.rule verbatim in its rule,
every superseded_clause verbatim in the base: 0 misses; storage tail: 4 overwrites, 1 distinct string (8 copies).

### Decoy / absent-record probes (round 5)
T0: skip the quote -> the no-quote figure; skip the transport -> quote 3014.01; skip both -> opening contrast; the
statement-storage schedule run on the sale date -> equals the seeded sale charge. T1: as the table above; gold unchanged.

### XF recipe, every point x every policy (round 5)
| point | E | Qd | X | S | Q | N | R |
|---|---|---|---|---|---|---|---|
| 1 assembly generic | ok | ok | ok | ok | ok | ok | ok (reserve tier names its own terms) |
| 2 order | unchanged | unchanged | unchanged | unchanged | unchanged | unchanged | single tier sum, one round at end |
| 3 independence | script ok | script ok | script ok | script ok | script ok | script ok | script ok |
| 4 ownership | ok | free days defined by S, named | ok | owns free days | free days defined by S, named | ok | free days defined by S, named |
| 5 basis verbatim | 0 misses (script) |
| 6 ties | unchanged | unchanged | unchanged | unchanged | unchanged | unchanged | first listed retail |
| 7 counting | unchanged | lot days | unchanged | lot days | lot days | unchanged | lot days |
| 8 branches | unchanged | free-day branches restated | unchanged | unchanged | restated | unchanged | restated; reserve none/half/half+retail |
| 9 base clauses | unchanged | storage tail (one string) | unchanged | storage tail | storage tail | n/a | storage tail |
| 10 rounding | unchanged | unchanged | unchanged | unchanged | unchanged | n/a | half rounded, then sum, end round |
| 11 tools | unchanged | unchanged | unchanged | unchanged | unchanged | unchanged | unchanged |
| 12 proof text | n/a | swept | swept | n/a | n/a | n/a | retail tier text swept |

### Gate block (rework round 5, no --task)
EXTENDED OK
TASK TOOL CONTRACT OK
REPLAY OK (0.json 71/71, 1.json 48/48; deterministic, non-vacuous, 0 errors)
SOLVABILITY OK
COMPUTE OK (suite means branches=45.00 steps=13.00; history_rows_max=56; branches_max=49)
GROUNDING OK
CACHE-DIFF INFO (optional)
SCOPE OK
TRACEABILITY NOT OK — only the 7 unlock tool-name provenance misses (expected before KB render)
REWORK round 5: gates 8/8 green

## REWORK round 6 closure
Audit: audits/policy_task/preowned_repossession_recovery/{_difficulty,0,1}.md, revision_5. Item -> change:
- R5-X4 (XF 4, free days defined as another policy figures them): the shared storage sentence (one string, 8 copies,
  rule and storage overwrite of the deficiency quote, statement storage, redemption quote and reinstatement) no longer says
  "exactly as for a storage charge through a statement date". It now states the sale-time charge's own free days in its
  own words: an involuntary recovery of a contract that shows an earlier reinstatement payment has none, a voluntary
  surrender of a contract that shows no reinstatement payment has the surrender free days, any other recovery the free
  days for the tier, less any already set against stored days. The deficiency quote, redemption quote and reinstatement
  each declare their own surrender_free_days parameter (same value as the statement-storage policy's), and the tier free
  days are the base tier field; so no policy defines a quantity by another policy's figure and no figure moves.
  Class sweep (script over every rule): no "exactly as for" / "as ... figures it" phrase remains; every rule that names
  the surrender free days owns the parameter. The two remaining sibling-naming phrases ("a redemption quote is figured
  under the redemption-quote schedule", "a deficiency quote is figured under the deficiency-quote schedule") are scope
  exclusions naming the sibling that owns a different quote (XF 9), not definitions of a quantity the policy uses; kept.
  Task 0 seed grounding sentence (65 checks) restated in the same own-words form.

### Pairwise method tiers (round 6): unchanged from round 5 (no ladder or compute changed).
### Factor independence (round 6): transitive script over every policy: no hit.
### compute_basis sweep (round 6): 0 misses (compute_basis, replaced_by, policy_source, baseline.rule; superseded_clause
in base); storage tail 4 overwrites, 1 distinct string.
### Decoy / absent-record probes (round 6): no compute or seed value changed; COMPUTE recomputes every gold, factor
sensitivity, all-baseline and skip figure equal to round 5; round-5 probe table stands.

### XF recipe, every point x every policy (round 6)
| point | E | Qd | X | S | Q | N | R |
|---|---|---|---|---|---|---|---|
| 1 assembly generic | ok | ok | ok | ok | ok | ok | ok |
| 2 order | ok | ok | ok | ok | ok | ok | ok |
| 3 independence | script ok | script ok | script ok | script ok | script ok | script ok | script ok |
| 4 ownership | ok | free days own words + own param | ok | own ladder | free days own words + own param | ok | free days own words + own param |
| 5 basis verbatim | 0 misses (script) |
| 6 ties | ok | ok | ok | ok | ok | ok | ok |
| 7 counting | ok | ok | ok | ok | ok | ok | ok |
| 8 branches | ok | ok | ok | ok | ok | ok | ok |
| 9 base clauses | ok | tail (one string) | ok | tail | tail | n/a | tail |
| 10 rounding | ok | ok | ok | ok | ok | n/a | ok |
| 11 tools | unchanged | unchanged | unchanged | unchanged | unchanged | unchanged | unchanged |
| 12 proof text | n/a | seed sentence swept | n/a | n/a | n/a | n/a | n/a |

### Gate block (rework round 6, no --task)
EXTENDED OK
TASK TOOL CONTRACT OK
REPLAY OK (0.json 71/71, 1.json 48/48; deterministic, non-vacuous, 0 errors)
SOLVABILITY OK
COMPUTE OK (suite means branches=45.00 steps=13.00; history_rows_max=56; branches_max=49)
GROUNDING OK
CACHE-DIFF INFO (optional)
SCOPE OK
TRACEABILITY NOT OK — only the 7 unlock tool-name provenance misses (expected before KB render)
REWORK round 6: gates 8/8 green

## REWORK round 7 closure
Input: audits/render_source/preowned_repossession_recovery/render_r1.md (renderer stop report: 4 mismatches + observations). Item -> change:
- M1 (repeat_recovery, zero agency fees unstated): rule and compute_basis now read "a single agency fee, or none posted,
  carries none", matching the compute's fall-through.
- M2 (transport charge date undefined with no condition report for this recovery): the rule now defines the lot-intake
  date as the most recent condition report, dated on or after the repossession date, and states that no transport
  charge is owed while no such report is on record (the vehicle has not reached the lot). A charge can therefore never
  be dated before its repossession, in line with the deficiency-quote prerequisite. Class sweep: every lot-intake read
  (transport, statement storage, storage tail, redemption projection, sale-notice transfer) checked for the same case.
- M3 (sale-notice transfer days, report dated on the repossession date): the lot case now reads "a condition report
  dated on or after the repossession date"; the agency-yard case says "with no condition report dated on or after the
  repossession date" (rule, basis, ladder, compute >=). Same class fixed in the redemption's projected lot storage
  (rule, basis, ladder, compute >=). Statement storage and the storage tail were already equivalent on that day (the
  day after the repossession date is the day after intake). Probed: report on the repossession date -> lot case; report
  before it -> yard / no projection.
- M4 (redemption good_through_days 0 on the last day of a running period): the tool docstring now says "a non-negative
  integer"; the tool already accepts 0.
- O-sale-date: the deficiency quote now says "The sale date is the sale date recorded on the contract" (and its
  compute_basis quotes that); the settlement counts "from the sale date recorded on the contract to the settlement date,
  the day the settlement figure is stated".
- O-settlement posting (class: every customer payment tool vs the base posting and certified-funds rules): the
  settlement and the reinstatement each declare a scoped overwrite of the base posting clause. Their wires are credited
  when received, whatever the hour: Monday-Friday the same day, Saturday/Sunday the following Monday; they are not taken
  on a US federal holiday or a weekend before a holiday Monday; every other payment keeps the base cutoff / next
  business day rule (restated). The settlement is now sent by bank wire, a certified-funds channel accepted under
  certified funds only. The settlement tool now posts on the posting date with channel wire, and its interest runs
  through the posting date; the docstring and return say so. The reinstatement tool already did. Task 0 (Wednesday)
  replays identically; probed on a Saturday: posts the Monday.
- O-reinstatement baseline: the standard sentence (rule, amount overwrite, baseline.rule, two compute_basis) now
  includes "less the fees a reinstatement the state period grants leaves out of its amount", matching the compute.
- O-placement (XF 4): plain bindings used by only one factor now belong to that factor: deficiency quote
  disposition_expense_share (gross sale, sale expenses, credit), held_storage_cap (billed storage days, credit),
  lease_relationship_rate (post-sale per diem); redemption projected_lot_storage (daily storage amount, projected
  storage); reinstatement weekend_posting_days (daily storage amount, posting storage); settlement settlement_base_rule
  (fees due). Each of these is already defined in its factor's own sentence. Remaining standard bindings used by one
  factor (settlement quote amount, redemption quote validity days) are read by that factor's baseline, so they are
  standard-method quantities.
- Proof text: task 1 tier_taken strings for the transfer and projection ladders, and task 0 settlement business effect
  (bank wire, same-day posting) updated. No scored value moved.

### Pairwise method tiers (round 7): unchanged (no method ladder changed).
### Factor independence (round 7): transitive script over every policy (with the new factor bindings): no hit.
### compute_basis sweep (round 7): 0 misses incl. the two new posting overwrites; storage tail 1 distinct string.
### Probes (round 7): T1 report on the repossession date -> sale notice lot case, redemption projects storage; report
the day before -> no transfer days, no projection; T0 no agency fee -> no repeat surcharge; T0 settlement on a Saturday
-> posts Monday by wire; gold values recompute unchanged in both tasks.

### XF recipe, every point x every policy (round 7)
| point | E | Qd | X | S | Q | N | R |
|---|---|---|---|---|---|---|---|
| 1 assembly generic | ok | ok | ok | ok | ok | ok | ok |
| 2 order | ok | ok | ok | ok | ok | ok | ok |
| 3 independence | script ok | script ok | script ok | script ok | script ok | script ok | script ok |
| 4 ownership | ok | single-factor bindings moved | fees due moved | ok | storage bindings moved | ok | storage bindings moved |
| 5 basis verbatim | 0 misses (script) |
| 6 ties | ok | ok | ok | ok | ok | ok | ok |
| 7 counting | ok | sale date defined | sale/settlement dates defined | ok | ok | ok | ok |
| 8 branches | zero fees, no report this recovery | ok | ok | ok | report on repo date | report on repo date | ok |
| 9 base clauses | ok | ok | posting overwrite | ok | ok | n/a | posting overwrite |
| 10 rounding | ok | ok | ok | ok | ok | n/a | ok |
| 11 tools | ok | ok | wire, posting date | ok | non-negative days | ok | ok |
| 12 proof text | n/a | n/a | business effect | n/a | n/a | tier_taken | n/a |

### Gate block (rework round 7, no --task)
EXTENDED OK
TASK TOOL CONTRACT OK
REPLAY OK (0.json 71/71, 1.json 48/48; deterministic, non-vacuous, 0 errors)
SOLVABILITY OK
COMPUTE OK (suite means branches=45.00 steps=13.00; history_rows_max=56; branches_max=49)
GROUNDING OK
CACHE-DIFF INFO (optional)
SCOPE OK
TRACEABILITY NOT OK — only the 7 unlock tool-name provenance misses (expected before KB render)
REWORK round 7: gates 8/8 green

## REWORK round 8 closure
Audit: audits/policy_task/preowned_repossession_recovery/_difficulty.md, revision_7. Item -> change:
- R7-X9 (sibling overwrites of the base posting clause each restating it for "every other payment"): the restated tail
  in both overwrites and both rule copies (4 copies, one string) now reads "Every payment other than a deficiency
  settlement wire or reinstatement funds, both of which post on the day they are received or on the Monday after a
  weekend as the settlement and reinstatement terms state, keeps the standard posting: ...". Each policy's text now
  excludes its own case and the sibling's by name, and the two terms agree. Class sweep over every base clause retired
  by more than one policy: payoff clause (deficiency quote, redemption quote) - each tail already names the sibling's
  quote; storage clause (deficiency quote, statement storage, redemption quote, reinstatement) - the shared tail already
  excludes all four cases by name (statement-date charges, redemption, reinstatement, deficiency quote); posting clause -
  fixed here. Script: no replaced_by still says "every other payment"; no other "every other ..." phrase sits in a clause
  retired by two policies.
- O-r7-1 (credited on receipt vs wire-network cutoffs): kept; the rule states the company credits a wire when it is
  received, and a wire sent after the network closes is received the next business day. Recorded, not changed.

### Pairwise method tiers / factor independence / probes (round 8): no compute, ladder, tool or seed changed; COMPUTE
recomputes every gold, sensitivity, all-baseline and skip figure unchanged; round-7 tables and probes stand.
### compute_basis sweep (round 8): 0 misses (compute_basis, replaced_by, policy_source, baseline.rule; superseded_clause
in base).

### XF recipe, every point x every policy (round 8)
| point | E | Qd | X | S | Q | N | R |
|---|---|---|---|---|---|---|---|
| 1-8, 10-12 | ok (unchanged since round 7) | ok | ok | ok | ok | ok | ok |
| 9 base clauses | ok | payoff + storage: siblings named | posting: both cases named | storage: siblings named | payoff + storage: siblings named | n/a | posting + storage: both cases named |

### Gate block (rework round 8, no --task)
EXTENDED OK
TASK TOOL CONTRACT OK
REPLAY OK (0.json 71/71, 1.json 48/48; deterministic, non-vacuous, 0 errors)
SOLVABILITY OK
COMPUTE OK (suite means branches=45.00 steps=13.00; history_rows_max=56; branches_max=49)
GROUNDING OK
CACHE-DIFF INFO (optional)
SCOPE OK
TRACEABILITY NOT OK — only the 7 unlock tool-name provenance misses (expected before KB render)
REWORK round 8: gates 8/8 green
