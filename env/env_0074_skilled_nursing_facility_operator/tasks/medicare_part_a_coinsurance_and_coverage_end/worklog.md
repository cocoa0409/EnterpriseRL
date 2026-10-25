# worklog — medicare_part_a_coinsurance_and_coverage_end (env_0074), round 1

## Draw (draw_counts.py --tasks 2)
- task 0: prerequisite_problems=1, factor_counts=[5,5]
- task 1: prerequisite_problems=2, factor_counts=[5,6,4]

## Charter constraints found at Step 0 (they shape every design choice; recorded for the audits)
1. Only money writes have tier-varying VALUES: the daily coinsurance rate by calendar year of service
   (2026 217.00, 2025 209.50 in base; 2024 204.00 is the published CMS figure added in policy params) and the
   coinsurance shares by supplemental coverage (resident 100/100/50/25/0/0). Day-count writes (booking,
   reversal) have no parameter ladder, so they cannot be problems; booked blocks and reversals are seeded.
2. Customer-owned writes available: QIO request (no numeric field), SNF ABN (option + date; the DSL has no
   date arithmetic), coinsurance payment (numeric). Only the payment can carry a computed number, so each
   task's customer write is a resident coinsurance payment made during the call: card in task 0, bank draft
   in task 1 (two tools split by payment rail; the card single-payment maximum applies to one only).
   KNOWN RESIDUE: the blueprint summary lists posting payments among agent actions; a payment the payer makes
   with her own card/bank account during the call is treated as the payer's own write.
3. KNOWN RESIDUE (payment computations): a resident payment of a just-posted charge re-prices that charge's
   block with the same rules; its factors are therefore also visible as the posted amount. Kept because the
   charter offers no other computed customer write; the payment reads the posted charge (value_input).
4. KNOWN RESIDUE (task 0 secondary charge): the December carrier charge is seeded posted (2026-01-02); with the
   base remainder rule a solver could back out the resident share as block total minus carrier share. Not
   seeding it would leave an owed write outside a 2-problem tree.
5. Cross-difficulty evidence that genuinely moves Medicare coinsurance: bed-hold leave nights (bedhold ledger),
   which split a block's covered days around a mid-month supplemental change.

## Task 0 (closed)
Tree: medicare_ext_card_payment_share (root, user, tool pay_coinsurance_by_card_ebeca5a6)
  <- value_input <- medicare_ext_resident_block_share (agent, tool post_coinsurance_charge_97c12690).
Factor counts: charge 5, payment 5 (multiset [5,5] = draw).
World: Harold Dunmore (Camp Hill 116-B), Medigap K -> L effective 2025-12-16 (same carrier), December block
29 covered days (bed-hold hospital-observation leave 12-06..12-07), November block 6 days charged 50/50.
Gold: charge 2199.75 (13 days at 50% + 16 days at 25%, 209.50/day); card payment 2199.75.

### Factor sensitivity (check_compute, handling time)
| factor | tier taken | baseline result |
|---|---|---|
| f_year_rate | last service date in 2025 -> 209.50 | 2278.50 |
| f_new_split | plan L AND eff <= block end -> 25% | 4713.75 |
| f_carried_split | preceding resident charge = 50% | 3561.50 |
| f_change_day | eff inside block -> 15 calendar days | 1518.88 |
| f_away_nights | latest leave ended before eff -> 2 | 2304.50 |
| all at baseline | | 6293.00 |

### Pairwise method-tier table (XF 7 shape test)
f_change_day: (a) DAYS(first, eff) | (b) DAYS(first,last)+1 | (c) 0 — (a)/(b) differ in the end date input (eff vs last),
(a)/(c) and (b)/(c) differ by a non-zero count vs constant 0 on their domains (eff inside -> >=1; eff after -> >=1).
f_away_nights: (a) all month held days | (b) month held days - latest leave + DAYS(latest_from, eff) | (c) month held days - latest leave | (d) 0
— (a)/(c) differ by the latest leave's days (>=1); (b)/(c) differ by DAYS(latest_from, eff) (>=1 since latest_from < eff);
(a)/(b) differ by latest_days - DAYS(latest_from, eff) (>=1 since latest_to >= eff); (d) is 0 only where the month books no held day.

### Decoy / absent-record probe table (probe_t0.py on scratch copies)
| probe | result | expected |
|---|---|---|
| base | 2199.75 | 2199.75 |
| rebill resident charge on preceding block | 2199.75 | excluded (charge_entry_id filter) |
| bed-hold leave in another month | 2199.75 | excluded (service_month filter) |
| another resident's December leave | 2199.75 | excluded (customer scope) |
| second December leave after eff | 2199.75 | tier (c): earlier leave only |
| leave straddling eff (12-14..12-17) | 2199.75 | tier (b): 2 nights before eff |
| no supplemental effective date | 3037.75 | all days at carried 50% |
| effective date before block | 1518.88 | all days at 25% |
| no preceding coinsurance block | 3561.50 | carried share 100% |
| 1 day reversed on block | 2147.38 | covered 28, half-up |
| adjustment on preceding resident charge (net 25%) | 1518.88 | carried 25% |

### Gates (task 0)
check_extended / check_task_tools / replay_tasks / check_solvability / check_compute / check_grounding / check_cross_fire: all OK.

## Round-1 resume (second agent): task 0 gates re-run 7/7 OK at start; task 0 left as is.

## Task 1 (design, draw prerequisite_problems=2, factor_counts=[5,6,4])
Occupied by task 0: post_coinsurance_charge_97c12690 (resident charge; its docstring also offers carrier/crossover
parties, so task 1 may NOT add another charge tool), pay_coinsurance_by_card_ebeca5a6. Free write kinds left:
coinsurance adjustments, other payment rails, rebill, payment reversal. Constraints found:
- every computation needs >=2 parameter factors -> year rate and/or coinsurance shares; a share factor bites only when
  the share != 100 (resident side), so the tier must carry a carrier; any correction that moves money to the carrier
  needs a carrier charge (task 0's tool) -> task 1 corrections may only reduce charges (rate-year, reversed days).
- day reversals touch every party with a share on the reversed days -> the carrier's reduction is seeded as posted
  (crossover side adjusts with the Medicare claim), the resident's is owed.
Tree (chain): medicare_ext_resident_rate_year_correction (agent, correct_coinsurance_rate_feac0074, 5 factors)
  -> value_input (gate red_rate) -> medicare_ext_reversed_day_reduction (agent, reduce_coinsurance_for_reversed_days_0894f336, 4)
  -> state_gate (medicare_ledger.adjustment_reason) -> medicare_ext_bank_draft_payment (root, user, pay_coinsurance_by_bank_draft_32bb229d, 6).
World: Denise Albright (65, Lancaster 127-A), rep son Marcus Albright 717-555-0168. Medigap K (50/50) since admission
2025-10-25 -> Plan N (full coinsurance) effective 2025-12-10 (Medigap open-enrollment switch, recorded 2025-11-28,
before December posting). December block 27 booked days (hospital leave 12-03..04, therapeutic leave 12-24..25),
posted 2026-01-02: carrier via crossover at 209.50 (4923.25), resident statement charge at the posting-year rate
217.00 (759.50 = 7 days at 50%). Uncertified days 12-07..12-11 (recert due 12-06, signed 12-12) reversed 2026-01-21;
carrier's uncertified_day reduction posted (733.25), resident's not. Frozen 2026-01-28.
Planned gold: rate correction 26.25 -> reduction 314.25 (priced at the corrected 209.50) -> bank draft 419.00
(= 759.50 - 26.25 - 314.25, ledger check).
KNOWN RESIDUE (as task 0 #3): the bank draft re-prices the corrected charge; its factors are also visible in the
ledger once the two adjustments stand. The rate correction's split factors are visible in the posted amount
(posted x 7.50/217); kept because the correction is stated per priced day by the charter's own split rules.

## Task 1 (closed)
Tree (chain): medicare_ext_resident_rate_year_correction (agent, correct_coinsurance_rate_feac0074, 5 factors)
  -> value_input (red_rate) -> medicare_ext_reversed_day_reduction (agent, reduce_coinsurance_for_reversed_days_0894f336, 4)
  -> state_gate (medicare_ledger.adjustment_reason) -> medicare_ext_bank_draft_payment (root, user, pay_coinsurance_by_bank_draft_32bb229d, 6).
Multiset [5,4,6] = draw [5,6,4]. Prerequisite sentences: reduction "... is fixed only after the records carry a rate-year
correction against that charge whenever ..." (affirmative); bank draft "... is not taken until the records carry, against
that charge, a reduction for the covered days of every day reversal ..." (negated). Both state form, single writer each.
Tool change during build: the reduction tool first took an adjustment_reason enum; check_task_tools required the full
8-value schema set -> redesigned to take reversal_entry_id and carry the reversal's own reason, booked-days entry and
service month over from that entry (no synonym of the correction tool).
Gold: 26.25 (step 8) -> 314.25 (step 10) -> 419.00 (step 12, user); 419.00 = 759.50 - 26.25 - 314.25 (ledger check).

### Factor sensitivity (handling time; verify_t1.py with check_compute's sandbox)
| policy | factor | tier taken | baseline result |
|---|---|---|---|
| rate-year correction (26.25) | f_year_rate | last service date in 2025 -> 209.50 | 0.00 |
| | f_new_split | plan N AND eff 2025-12-10 <= block end -> 0% | 176.25 |
| | f_carried_split | Nov resident charge = 50% | 52.50 |
| | f_change_day | eff inside block -> 9 days | 0.00 |
| | f_away_nights | latest leave (12-24) began on/after eff -> earlier leaves only (2) | 33.75 |
| | all at baseline | | 0.00 |
| reversed-day reduction (314.25) | f_reduction_rate | correction stands AND 2025 -> 209.50 | 325.50 |
| | f_new_split | 0% | 733.25 |
| | f_carried_split | 50% | 628.50 |
| | f_reversal_side | reversal 12-07..11 straddles eff -> 3 days | 0.00 |
| | all at baseline | (cap: open balance 733.25) | 733.25 |
| bank draft (419.00) | f_year_rate | 209.50 | 434.00 |
| | f_new_split | 0% | 4190.00 |
| | f_carried_split | 50% | 838.00 |
| | f_change_day | 9 days | 0.00 |
| | f_away_nights | 2 | 628.50 |
| | f_reversed_before | latest reversal straddles eff -> 3 | 733.25 |
| | all at baseline | | 4774.00 |
Edge sensitivity: skip the correction -> reduction 325.50 (value_input bears weight); skip the reduction -> bank-draft
figure unchanged 419.00, terminal ledger lacks the reduction row and the charge keeps 314.25 open (state_gate).

### Pairwise method-tier table (XF 7 shape test)
f_change_day, f_away_nights: as task 0.
f_reversal_side: (a) all reversed days of the reversal | (b) DAYS(first reversed date, eff) | (c) 0 — (a)/(b) differ in the
input (day-count field vs a date difference against eff); (a)/(c) and (b)/(c) non-zero vs constant 0 on their domains
((a) >= 1 day; (b) >= 1 since the first reversed date < eff).
f_reversed_before: (a) all reversed days of the block | (b) block total - latest + DAYS(latest first date, eff) | (c) block
total - latest | (d) 0 — same structure as f_away_nights: (a)/(c) differ by the latest reversal's days (>= 1); (b)/(c) by
DAYS(latest first date, eff) (>= 1); (a)/(b) by latest days - DAYS(first, eff) (>= 1, it ends on/after eff); (d) is 0 only
where the block carries no reversal.
f_reduction_rate (parameter): 209.50 / 204.00 / 217.00 / recorded rate; f_new_split, f_carried_split, f_year_rate: as task 0.

### Decoy / absent-record probe table (probe_t1.py on scratch copies; correction | reduction | bank draft)
| probe | result | expected |
|---|---|---|
| base | 26.25 / 314.25 / 419.00 | gold |
| rebill resident charge on the Dec block (naming the carrier charge) | 26.25 / 314.25 / 419.00 | excluded (charge_entry_id '' filter) |
| rate-year correction on the carrier's charge only | 26.25 / 314.25 / 419.00 | excluded (correction counted on the resident charge only) |
| day reversal on the November block | 26.25 / 314.25 / 419.00 | excluded (days_entry_id filter) |
| bed-hold leave booked for November | 26.25 / 314.25 / 419.00 | excluded (service_month filter) |
| second Dec reversal after eff (12-20) | 26.25 / 0.00 / 209.50 | reduction prices the latest reversal (all after eff, 0%); see residue |
| hospital leave widened to 12-08..12-11 | 18.75 / 314.25 / 209.50 | tier (c) takes the whole earlier leave; see residue |
| no supplemental effective date | 101.25 / 523.75 / 2304.50 | all days at the carried 50% |
| partial check 100.00 on the Dec resident charge | 26.25 / 314.25 / 319.00 | payments net off |
| check 100.00 returned (reversal) | 26.25 / 314.25 / 419.00 | returned payment nets back |
| resident charge already at 209.50 | 0.00 / 314.25 / 419.00 | no correction; reduction at the recorded rate |
| November resident charge absent (carrier charge only) | 0.00 / 0.00 / 0.00 | carried share tier "secondary only" = 0% |
RESIDUE (DSL, as task 0's leave ladder): the 'earlier leaves / earlier reversals' tiers take every day of the earlier
records whole; with two records of which the earlier straddles the effective date, the stated rule takes the earlier one
whole. The rule says so exactly (deterministic), and no task world exercises that case.

### Gates (task 1, then full suite)
Per task 1: check_extended / check_task_tools / replay_tasks / check_solvability / check_compute / check_grounding /
check_cross_fire: all OK (task 0 re-run: all OK). First solvability run failed on discriminators without action_arg/value,
crossover_posted evidence not covering charge_entry_id/payment_method, CNc missing from seed_consistency; replay closure
missed the two bed-hold elections (read node added). Fixed and re-run green.
Full suite: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK (suite means branches 57.50,
steps 12.00; history_rows_max 18; branches_max 68); GROUNDING OK; SCOPE OK; CACHE-DIFF INFO (optional, no cache trap
designed). check_traceability is run after the KB render.
ROUND 1: gates 7/7 green

## REWORK round 2 — design (audit revision_1: C1-C9, C11, T0-F1..F3, T1-F1..F3)
Factor structure (closes C7/T-F3; XF A.6): every block-pricing computation is
  rate x (E x s_e + (D - E) x s_l) / 100, rounded half up once per row, where
  - s_l = share of the tier on file (non-factor base read: "the tier that sets the split is the one in effect");
  - E (covered days before the supplemental effective date) = calendar days of the block before that date (non-factor
    base split; none recorded -> 0, so the tier on file prices every day: C1) less the day kinds below;
  - factors: f_year_rate (P), f_carried_split (P; earlier share from the block before's resident charge, GROSS amount
    over its own days x rate: C2), and one method factor per day kind: bed-hold leave nights (cross bedhold),
    hospital_day / leave_of_absence_day / uncertified_day reversals. With s_e at baseline 100 and s_l a non-factor read,
    every method moves the result alone in any world whose tier share != 100 (T2); s_e moves alone because the base
    split keeps E > 0. Only one share is a factor per computation (two share factors would break T2 for the methods).
  - C3/C6: self-naming scope test (coarse, exact): one days_21_100 entry for the service month, at most one block before,
    at most one bed-hold leave booked for the month, at most one reversal per reason, no booking_error reversal, no
    reversal span overlapping the leave, an uncertified reversal's day count equal to its span less the other kinds inside
    it, the block before billed at exactly 100/50/25/0 percent; two-date tests inside; out of scope the base clause is
    restated and this policy prices nothing (stated referral).
  - C4: rate-year correction = round(recorded rate x S/100) - round(year rate x S/100) (per-row rounding).
  - C5: both payment rules: re-priced share less payments applied net of returned payments, never below zero; card
    additionally never above the card payment maximum.
  - C8: one generic assembly sentence; each day-kind sentence states its own effect on E. C9: effect texts carry no values.
Counts: T0 charge 5 / card 5 (rate, s_e, leave, hospital_day, uncertified). T1: rate correction 5 (rate, s_e, leave,
  hospital_day, leave_of_absence_day: the kinds known when the charge was posted), reversed-day reduction 4 (reduction
  rate, s_e, leave nights inside the uncertified span, hospital_day inside the span), bank draft 6 (all four kinds + 2 P).
C11 / T0-F1 / T1-F1 / T1-F2 (least-bad, reasoning): the only customer write with a number in this charter is a payment;
  base applies every payment to one named charge up to its open balance, so in any consistent world a correct payment
  equals the open balance at its handling time; paying before the correction only moves the identity onto the agent's
  last write and needs an ordering rule no business states. Likewise every block's resident and secondary charges are
  complementary by base ("the secondary amount is the block total minus the resident amount"), so a seeded carrier row
  lets the resident figure be backed out; not seeding it leaves a carrier charge owed outside the drawn tree. Kept as
  stated residue; the payments re-price by the published rules.

## REWORK round 2 — closure per audit item
- C1 (no supplemental effective date -> 100 %): the split now reads "a coverage that records none has the tier on file in
  effect on every day"; later days take the tier-on-file share (non-factor base read), so QMB/full-coinsurance/K/L on file
  price every day at their own share (probes: T0 no date -> 1361.75 = 26 x 209.50 x 25 %; QMB on file -> 0).
- C2 (carried-split ratio proxy): the earlier share is read from the block before's resident charge GROSS over that
  charge's own days x own rate (adjustments and rate errors no longer move it; probe "adjusted block-before charge" unchanged);
  a block before billed at any other percentage (mixed split) or absent while the date falls inside the block is outside the
  record test (referral).
- C3 (date pairing): every day kind is a single record (record test), and each is paired with the block and the effective
  date by an exact two-date test; the uncertified span is netted of the held night / hospital-day / leave-of-absence days
  inside it (overlap computed exactly); held days taken back on the bed-hold side, a second leave, a second reversal of a
  reason, a booking-error reversal, a hospital/leave reversal on a held night -> outside the test. Self-naming overwrite of
  the base split sentence (medicare_evt_coinsurance) on all five policies; out of scope the base split is restated and the
  policy prices nothing (stated referral, DSL limit).
- C4: the rate-year correction is round(recorded rate x S) - round(year rate x S), each row rounded half up (base "by the
  difference" per row).
- C5: both payment rules: re-priced share less payments applied net of returned payments, floor 0; the card rule adds the
  5000.00 card payment maximum. Same charge -> same figure under both rules (X1 closed: both count the same days and kinds).
- C6: ties excluded by the record test (one days_21_100 entry per service month, at most one block before, one record per
  day kind).
- C7 / T0-F3 / T1-F3: factor structure rebuilt (see design above); T1/T2 table below; every computation keeps its drawn count.
- C8: one generic assembly sentence per policy ("... adds, over the days it counts, the daily rate times the share each
  day takes ..."); each day-kind sentence states its own effect.
- C9: prerequisite condition/effect texts carry no world values.
- C11 / T0-F2 / T1-F2 and T0-F1 / T1-F1: least-bad, reasoning recorded in the round-2 design section; residue stated in
  both design_rationales.
- O6: the task-1 persona no longer cites a statement figure (the Full-Coinsurance tier issues none). O1/O2/O3/O4/O5/O7/O8:
  observations, unchanged.
- Tool bodies: amounts rounded half up by a class static helper (_Fmt.cents), non-positive amounts/rates/days and a malformed
  service month return an Error (docstrings promise positive values and YYYY-MM); names, signatures, docstrings unchanged.
- Worlds: T0 adds an overnight observation (hold declined, hospital_day reversal 2025-12-10) and an uncertified lapse
  (2025-12-13..14); carrier charge re-priced on 26 days. T1 rebuilt: K -> N on 2025-12-10; declined home visit 12-01
  (leave_of_absence_day reversal), held hospital leave 12-03..04, declined observation 12-06 (hospital_day reversal), resident
  charge at 217.00 posted 2026-01-02, uncertified lapse 12-04..12 reversed 2026-01-21 with the carrier's reduction posted.
- Prerequisite sentence change: the bank-draft wait now names "every day reversal posted against its booked-days entry after
  the charge itself was posted" (reversals posted with the month need no reduction; the round-1 wording was unmeetable for them).

### T1 / T2 per factor (T1 = this world's figure with the factor's baseline; T2 = a producible world where it moves alone)
| policy | factor | T1 (expected -> baseline) | T2 |
|---|---|---|---|
| charge (T0) | f_year_rate | 1885.50 -> 1953.00 | any 2025 block |
| | f_carried_split | -> 2933.00 | E > 0 by the base split whenever the date falls inside the block |
| | f_held_nights | -> 1990.25 | any world with s_l != 100 (tier share is non-factor) and a held night before the date |
| | f_hospital_reversal | -> 1937.88 | same, with a hospital-day reversal before the date |
| | f_uncertified_days | -> 1990.25 | same, with an uncertified reversal before the date |
| card (T0) | same five | same figures | same |
| rate correction (T1) | f_year_rate | 18.75 -> 0.00 | any 2025 block billed at 217.00 |
| | f_carried_split | -> 37.50 | block billed at 217.00 with the date inside it |
| | f_held_nights | -> 26.25 | s_l != 100, held night before the date |
| | f_hospital_reversal | -> 22.50 | idem, hospital-day reversal posted with the charge |
| | f_absence_reversal | -> 22.50 | idem, leave-of-absence reversal posted with the charge |
| lapse reduction (T1) | f_reduction_rate | 419.00 -> 434.00 | any world with a correction on record |
| | f_carried_split | -> 523.75 (open-balance cap) | uncapped worlds: lapse span before the date |
| | f_held_in_lapse | -> 523.75 | s_l != 100, held night inside the span before the date |
| | f_hospital_in_lapse | -> 523.75 | idem, hospital-day inside the span |
| bank draft (T1) | f_year_rate | 104.75 -> 108.50 | any 2025 block |
| | f_carried_split | -> 209.50 | date inside the block |
| | f_held_nights | -> 314.25 | s_l != 100 |
| | f_hospital_reversal | -> 209.50 | s_l != 100 |
| | f_absence_reversal | -> 209.50 | s_l != 100 |
| | f_uncertified_days | -> 523.75 | s_l != 100 |

### Pairwise method-tier table (XF 7)
All day-kind ladders: (a) every day of the in-block span [s, e] when e < date -> DAYS(s, e) + 1 | (b) date inside (s, e] ->
DAYS(s, date) | (c) 0. (a)/(b) differ in the end input (e vs the effective date); (a), (b) >= 1 on their domains, (c) 0.
f_uncertified_days: (a) span days less the three overlaps | (b) span days up to the date less the overlaps before it | (c) 0
— (a)/(b) differ by the end input; the overlaps are extra inputs on both. The lapse overlaps follow the same three shapes.

### Sweeps
- compute_basis quotes, baseline sentences, policy_source, replaced_by: verbatim in their own rule (gen sweep: 0 issues);
  superseded_clause verbatim in medicare_evt_coinsurance.
- Proof text: 0.json / 1.json design_rationale, prerequisite_closure, necessity, traces and computations rewritten for the
  round-2 worlds; grep for round-1 figures (2199.75, 3875.75, 6293, 759.50, 26.25 as gold, 314.25 as gold, 4949.50 ...) finds
  only legitimate round-2 uses (sensitivity figures).
- Mechanical: no factor binding reads another factor's binding; no factor id is a substring of a tool name; no
  datetime/time/random/uuid/secrets substring in task_tools.py.

### Decoy / absent-record probe sweep (values: T0 charge, card | T1 correction, reduction, bank draft)

### task 0
| probe | values |
|---|---|
| base | (1885.5, 1885.5) |
| second days_21_100 entry for December (rebooking, same last date) | (0, 0) |
| booked entry for another month only (October days_1_20) | (1885.5, 1885.5) |
| no supplemental effective date recorded | (1361.75, 1361.75) |
| effective date after the block (2026-01-15) | (2723.5, 2723.5) |
| QMB on file from 2025-12-01 (QMB tier) | (0.0, 0) |
| block before absent (November entry removed) | (0, 0) |
| block before's resident charge reduced by an adjustment (gross read) | (1885.5, 1885.5) |
| block before's resident charge is a mixed split (60 percent) | (0, 0) |
| rebill resident charge on block before (charge_entry_id set) | (1885.5, 1885.5) |
| second bed-hold leave booked in December | (0, 0) |
| bed-hold leave booked in November only (decoy month) | (1885.5, 1885.5) |
| held day of the December leave taken back (bedhold reversal) | (0, 0) |
| no bed-hold leave at all (booked rows removed) | (1990.25, 1990.25) |
| second hospital-day reversal on the block | (0, 0) |
| booking_error reversal on the block | (0, 0) |
| reversal on the November block (other entry) | (1885.5, 1885.5) |
| hospital-day reversal on a held night (overlap) | (0, 0) |
| check 50.00 already applied to the resident charge | (1885.5, 1885.5) |
| check 50.00 applied then returned | (1885.5, 1885.5) |
| rate-year correction posted on the carrier's charge only | (1885.5, 1885.5) |

### task 1
| probe | values |
|---|---|
| base | (18.75, 419.0, 104.75) |
| second days_21_100 entry for December (rebooking, same last date) | (0, 0, 0) |
| booked entry for another month only (October days_1_20) | (18.75, 419.0, 104.75) |
| no supplemental effective date recorded | (0, 0.0, 0) |
| effective date after the block (2026-01-15) | (101.25, 441.25, 2095.0) |
| QMB on file from 2025-12-01 (QMB tier) | (0, 0.0, 0) |
| block before absent (November entry removed) | (0, 0, 0) |
| block before's resident charge reduced by an adjustment (gross read) | (18.75, 419.0, 104.75) |
| block before's resident charge is a mixed split (60 percent) | (0, 0, 0) |
| rebill resident charge on block before (charge_entry_id set) | (18.75, 419.0, 104.75) |
| second bed-hold leave booked in December | (0, 0, 0) |
| bed-hold leave booked in November only (decoy month) | (18.75, 419.0, 104.75) |
| held day of the December leave taken back (bedhold reversal) | (0, 0, 0) |
| no bed-hold leave at all (booked rows removed) | (0, 0, 0) |
| second hospital-day reversal on the block | (0, 0, 0) |
| booking_error reversal on the block | (0, 0, 0) |
| reversal on the November block (other entry) | (18.75, 419.0, 104.75) |
| hospital-day reversal on a held night (overlap) | (18.75, 419.0, 104.75) |
| check 50.00 already applied to the resident charge | (18.75, 419.0, 54.75) |
| check 50.00 applied then returned | (18.75, 419.0, 104.75) |
| rate-year correction posted on the carrier's charge only | (18.75, 419.0, 104.75) |
(0 = outside the record test -> the policy prices nothing; the base rule governs.)

### Gates (round 2, full suite)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 20/20, 1.json 27/27); SOLVABILITY OK; COMPUTE OK (suite means
branches 260.00, steps 12.00; history_rows_max 25; branches_max 311); GROUNDING OK; SCOPE OK; CACHE-DIFF INFO (optional).
REWORK round 2: gates 7/7 green

## REWORK round 3 — closure per audit item (revision_2)
- R2-C7 / R2-T1-F3 (correction T2): the correction's year-rate ladder now reads 2026+ -> 217.00, 2025 -> 209.50,
  otherwise -> 204.00, and its record test admits only blocks whose last service date is in 2024 or later (so the
  fall-through is exactly the 2024 figure). With the rate at its baseline the recorded 217.00 still exceeds 204.00, so
  every share/day factor moves the correction alone (solo table below). Baseline sentence and baseline params updated.
- R2-C12 (overwrite deferral / sibling scope): the five replaced_by sentences are now ONE sentence, verbatim in all five
  rules, naming every sibling's figure; for every block outside the record test it restates the retired
  medicare_evt_coinsurance clause in full (Medigap split from the carrier's policy effective date, QMB from the first
  day of the month after the determination, earlier split before the date) and says none of the five figures is priced
  for it (compute: 0 out of scope). No "under the base rule" deferral remains.
- R2-C13 / R2-T0-F4 / R2-T1-F4 (observation nights seeded as hospital days): base defines a night away without
  admission as a leave-of-absence day and an inpatient night as a hospital day. The two hospital_day reversals are now
  one-night INPATIENT admissions with the bed hold declined (persona lines, design_rationale, seed checks, read
  objectives rewritten); reasons and figures unchanged, so f_hospital_reversal bears weight on a charter-produced row.
- R2-C14 (card vs open balance / bank rule): the card payment counts the block's covered days (booked less every
  reversal) once the resident's charge stands (gate binding cnt_days; effect text and closure updated). N1 shape
  (29-day charge posted 2026-01-02, reversals posted 2026-01-05): card = bank draft on the same charge.
- R2-C15 (same-date convention): the record test now requires, when the resident's charge stands, that its day count
  equal the booked days less every reversal posted on or before the date the charge was posted; worlds where a
  same-date reversal was still priced (N2 shape) fall outside the test, so "on or before / after the charge" is exact
  inside it (rate correction and bank-draft gate).
- R2-C16 (reduction rule != compute): compute now tests that the uncertified reversal was posted after the charge
  (un_after on the posting dates); N3 shape (lapse posted before the charge) -> nothing priced, as the rule says.
- O9: the reduction's own name is now "the reduction for reversed covered days", matching its prerequisite sentence.
- Not reopened: C11 / T0-F1 / T1-F1 / T0-F2 / T1-F2 (BLUEPRINT-KNOWN per the auditor's verification).
- Tools: unchanged (round-2 body checks stand).

### T1 / T2 per factor (figure with that factor's baseline alone | figure with every OTHER factor at baseline)
| task 0 medicare_ext_resident_block_share | all-baseline 3851.75 | f_year_rate solo 3718.63; f_carried_split solo 2224.25; f_held_nights solo 3526.25; f_hospital_reversal solo 3689.0; f_uncertified_days solo 3526.25 |
| task 0 medicare_ext_card_payment_share | all-baseline 3851.75 | f_year_rate solo 3718.63; f_carried_split solo 2224.25; f_held_nights solo 3526.25; f_hospital_reversal solo 3689.0; f_uncertified_days solo 3526.25 |
| task 1 medicare_ext_resident_rate_year_correction | all-baseline 117.0 | f_year_rate solo 67.5; f_carried_split solo 58.5; f_held_nights solo 91.0; f_hospital_reversal solo 104.0; f_absence_reversal solo 104.0 |
| task 1 medicare_ext_reversed_day_reduction | all-baseline 523.75 | f_reduction_rate solo 523.75; f_carried_split solo 523.75; f_held_in_lapse solo 523.75; f_hospital_in_lapse solo 523.75 |
| task 1 medicare_ext_bank_draft_payment | all-baseline 1953.0 | f_year_rate solo 1885.5; f_carried_split solo 976.5; f_held_nights solo 1519.0; f_hospital_reversal solo 1736.0; f_absence_reversal solo 1736.0; f_uncertified_days solo 1085.0 |
T1 figures (gold -> factor baseline): task 0 charge/card 1885.50 -> 1953.00, 2933.00, 1990.25, 1937.88, 1990.25;
task 1 correction 18.75 -> 32.50, 37.50, 26.25, 22.50, 22.50; reduction 419.00 -> 434.00, 523.75, 523.75, 523.75;
bank draft 104.75 -> 108.50, 209.50, 314.25, 209.50, 209.50, 523.75. Every solo differs from the all-baseline figure
except the reduction, where the 523.75 open-balance cap binds on this world; on any uncapped world (larger open balance)
each reduction factor moves alone (rate x days x share with the tier share 0 against the baseline 100).

### Pairwise method-tier table (XF 7) — unchanged from round 2
Day-kind ladders: (a) whole in-block span before the date -> DAYS(s, e) + 1 | (b) date inside the span -> DAYS(s, date)
| (c) 0. Uncertified ladder: same with the in-span held / hospital-day / leave-of-absence overlaps subtracted. Lapse
overlaps: same three shapes on the intersection with the uncertified span.

### Decoy / absent-record probe sweep (task 0: charge, card | task 1: correction, reduction, bank draft; 0 = outside the record test)
| task 0 | base | [1885.5, 1885.5] |
| task 0 | second Dec days_21_100 entry, same last date (rebooking) | [0, 0] |
| task 0 | no supplemental effective date | [1361.75, 1361.75] |
| task 0 | QMB on file from 2025-12-01 | [0.0, 0] |
| task 0 | block before absent | [0, 0] |
| task 0 | second entry with the block-before benefit day (tie) | [0, 0] |
| task 0 | block-before resident charge adjusted (gross read) | [1885.5, 1885.5] |
| task 0 | block-before resident charge at a mixed split | [0, 0] |
| task 0 | rebill resident charge on the block before | [1885.5, 1885.5] |
| task 0 | bed-hold leave of another month | [1885.5, 1885.5] |
| task 0 | second bed-hold leave in December | [0, 0] |
| task 0 | held day of the December leave taken back | [0, 0] |
| task 0 | second hospital-day reversal, same first date as the first (tie) | [0, 0] |
| task 0 | booking-error reversal | [0, 0] |
| task 0 | reversal on the November block | [1885.5, 1885.5] |
| task 0 | leave-of-absence reversal on a held night | [0, 0] |
| task 1 | base | [18.75, 419.0, 104.75] |
| task 1 | second Dec days_21_100 entry, same last date (rebooking) | [0, 0, 0] |
| task 1 | no supplemental effective date | [0, 0.0, 0] |
| task 1 | QMB on file from 2025-12-01 | [0, 0.0, 0] |
| task 1 | block before absent | [0, 0, 0] |
| task 1 | second entry with the block-before benefit day (tie) | [0, 0, 0] |
| task 1 | block-before resident charge adjusted (gross read) | [18.75, 419.0, 104.75] |
| task 1 | block-before resident charge at a mixed split | [0, 0, 0] |
| task 1 | rebill resident charge on the block before | [18.75, 419.0, 104.75] |
| task 1 | bed-hold leave of another month | [18.75, 419.0, 104.75] |
| task 1 | second bed-hold leave in December | [0, 0, 0] |
| task 1 | held day of the December leave taken back | [0, 0, 0] |
| task 1 | second hospital-day reversal, same first date as the first (tie) | [0, 0, 0] |
| task 1 | booking-error reversal | [0, 0, 0] |
| task 1 | reversal on the November block | [18.75, 419.0, 104.75] |
| task 1 | leave-of-absence reversal on a held night | [0, 0, 0] |
| task 1 | lapse posted on the charge's date (same-date; charge priced 27 days) | [0, 0, 0] |
| task 1 | lapse posted before the charge (N3 shape) | [0, 0, 0] |
| task 1 | charge priced the same-date reversed day (N2 shape: day count 28) | [0, 0, 0] |
| task 1 | check 50.00 applied to the resident charge | [18.75, 419.0, 54.75] |
| task 1 | rate-year correction on the carrier's charge only | [18.75, 419.0, 104.75] |
| task 0 | N1 shape: 29-day resident charge posted 2026-01-02, both reversals posted 2026-01-05 | card 1885.50 = bank draft 1885.50 |

### Sweeps (round 3)
- compute_basis quotes, baseline sentences, policy_source, replaced_by verbatim in their own rules; superseded clause
  verbatim in base; no "under the base rule" and no stale self-name left (edit sweep: 0 issues).
- Proof text: observation-night wording, chg_days gate text, the correction's baseline figures and the card's day count
  wording rewritten in both task files; prerequisite fields carry no world value.

### Gates (round 3, full suite)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 20/20, 1.json 27/27); SOLVABILITY OK; COMPUTE OK; GROUNDING OK;
SCOPE OK; CACHE-DIFF INFO (optional).
REWORK round 3: gates 7/7 green

## REWORK round 4 — renderer scan-first findings (render_r1.md)
Files changed: medicare.extended.yaml, tasks/0.json, tasks/1.json, worklog.md. task_tools.py unchanged.
- Finding 1 (payment figures vs the in-force base posting clause "Every payment is applied to one named coinsurance charge
  and only up to that charge's open balance; ... any remainder ... is returned to the payer"): both payment rules now carry
  one sentence: a figure above the resident charge's open balance (amount less payments and adjustments plus returned
  payments) shows the charge was billed below what its days call for; the payment is then not taken under the policy, and
  whatever the payer sends is applied only up to the open balance, the rest returned. Compute: pay_fig, open_x;
  result = pay_fig if in scope and not above open_x, else 0. A plain cap was rejected: on the task worlds the figure IS the
  open balance (C11, BLUEPRINT-KNOWN), so a cap would make every factor decorative (T1).
  Class sweep, every payment/figure vs every in-force base posting clause: one named charge (both payments name the
  resident's original charge) ok; split oldest-first (a single charge is paid, so no split) ok; open balance (now enforced)
  ok; card maximum (card rule caps at 5000.00) ok; statement and due day (no figure involved) ok; no late charge (none
  priced) ok. Certified-funds clause ("Once the resident has had the returned-payment limit of dishonored payments within
  the rolling lookback ..., only certified funds are accepted from the resident on any coverage episode"): neither task
  world carries a returned payment. The DSL reads only this episode's ledger, so dishonored payments on another episode
  cannot be counted; recorded as a DSL limit with that base sentence.
  Adjustments (correction, reduction) were already capped at the open balance.
- Finding 2 (the bank-draft wait could name a reduction no policy prices): the wait sentence now reads "... a reduction for
  every uncertified-day reversal posted against its booked-days entry after the charge itself was posted" (rule,
  prerequisite policy_source, condition, effect, closure and rationale updated). The bank draft's record test excludes a
  hospital-day or leave-of-absence reversal posted after the charge.
  Class sweep, every prerequisite sentence vs what the depended-on policy can write in every in-scope world:
  (a) card <- resident charge: the charge policy writes the charge in every world where the card's record test passes.
      In a world whose charge figure is 0 (QMB / full-coinsurance on every day), base posts no zero charge and the card
      waits; but the card's own figure is 0 there too, so nothing is owed.
  (b) reduction <- rate-year correction: the correction's record test also requires a 2024-or-later block, and the
      correction is 0 when the open balance is 0. The reduction's record test now requires both (last service date in 2024
      or later; open balance above nothing), so every in-scope reduction that waits on a correction can have it written.
  (c) bank draft <- reduction: as above.

### T1 / T2 (round 4)
- Charge (task 0), correction, reduction (task 1): unchanged from round 3.
- Card (task 0) and bank draft (task 1): T1 — each factor's baseline raises the figure above the open balance, so the
  payment is not taken (0.00). factor_sensitivity and baseline_result are updated to 0.00 in both task files.
- T2 — producible world: the resident charge was billed at 217.00 and 100 percent (both are errors base names). There the
  figure never exceeds the open balance:
  - card solos: 3718.63 / 2224.25 / 3526.25 / 3689.00 / 3526.25 vs all-baseline 3851.75;
  - bank solos: 1885.50 / 976.50 / 1519.00 / 1736.00 / 1736.00 / 1085.00 vs all-baseline 1953.00.

### Probe sweep (round 4; values: task 0 charge, card | task 1 correction, reduction, bank draft)
| task 0 | base | [1885.5, 1885.5] |
| task 0 | second Dec days_21_100 entry (rebooking, tie on last date) | [0, 0] |
| task 0 | no supplemental effective date | [1361.75, 1361.75] |
| task 0 | QMB on file from 2025-12-01 | [0.0, 0] |
| task 0 | block before absent | [0, 0] |
| task 0 | second entry with the block-before benefit day (tie) | [0, 0] |
| task 0 | block-before resident charge adjusted (gross read) | [1885.5, 1885.5] |
| task 0 | block-before resident charge at a mixed split | [0, 0] |
| task 0 | rebill resident charge on the block before | [1885.5, 1885.5] |
| task 0 | bed-hold leave of another month | [1885.5, 1885.5] |
| task 0 | second bed-hold leave in December | [0, 0] |
| task 0 | held day of the December leave taken back (cancelled) | [0, 0] |
| task 0 | second hospital-day reversal | [0, 0] |
| task 0 | booking-error reversal | [0, 0] |
| task 0 | reversal on the November block | [1885.5, 1885.5] |
| task 0 | leave-of-absence reversal on a held night | [0, 0] |
| task 1 | base | [18.75, 419.0, 104.75] |
| task 1 | second Dec days_21_100 entry (rebooking, tie on last date) | [0, 0, 0] |
| task 1 | no supplemental effective date | [0, 0.0, 0] |
| task 1 | QMB on file from 2025-12-01 | [0, 0.0, 0] |
| task 1 | block before absent | [0, 0, 0] |
| task 1 | second entry with the block-before benefit day (tie) | [0, 0, 0] |
| task 1 | block-before resident charge adjusted (gross read) | [18.75, 419.0, 104.75] |
| task 1 | block-before resident charge at a mixed split | [0, 0, 0] |
| task 1 | rebill resident charge on the block before | [18.75, 419.0, 104.75] |
| task 1 | bed-hold leave of another month | [18.75, 419.0, 104.75] |
| task 1 | second bed-hold leave in December | [0, 0, 0] |
| task 1 | held day of the December leave taken back (cancelled) | [0, 0, 0] |
| task 1 | second hospital-day reversal | [0, 0, 0] |
| task 1 | booking-error reversal | [0, 0, 0] |
| task 1 | reversal on the November block | [18.75, 419.0, 104.75] |
| task 1 | leave-of-absence reversal on a held night | [0, 0, 0] |
| task 1 | lapse posted on the charge's date (same-date) | [0, 0, 0] |
| task 1 | lapse posted before the charge | [0, 0, 0] |
| task 1 | charge priced the same-date reversed day (day count 28) | [0, 0, 0] |
| task 1 | hospital-day reversal posted after the charge (renderer finding 2) | [0, 0, 0] |
| task 1 | resident charge billed below its days (rate 204.00, renderer finding 1 shape) | [0, 419.0, 0] |
| task 1 | check 50.00 applied to the resident charge | [18.75, 419.0, 54.75] |
| task 1 | check 50.00 applied then returned | [18.75, 419.0, 104.75] |
| task 1 | charge already paid in full (open balance 0) | [0.0, 0, 0] |
| task 1 | rate-year correction on the carrier's charge only | [18.75, 419.0, 104.75] |
(0 = outside the record test, or the payment figure is above the open balance. The probe chain posts the gold
correction even when the recomputed correction is 0, which is why the rate-204.00 row shows a reduction.)

### Sweeps
- compute_basis quotes, baseline sentences, policy_source and replaced_by are verbatim in their own rules; the superseded
  clause is verbatim in base (edit sweep: 0 issues).
- The old bank-draft wait sentence is gone from both task files. Payment traces and factor_sensitivity figures are
  rewritten. Prerequisite fields carry no world value.

### Gates (round 4, full suite)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; CACHE-DIFF INFO (optional).
REWORK round 4: gates 7/7 green

## REWORK round 5 — audit revision_4 (R4-C1, R4-C2) and the coordinator's round-5 rulings
Files changed: medicare.extended.yaml, tasks/0.json, tasks/1.json (texts and closure only; scored, baseline and
sensitivity figures unchanged), worklog.md. task_tools.py is unchanged; its exact Decimal half-up helper already rounds
amounts.
- R4-C1 (certified-funds clause contradicted by the card and bank-draft rules): routed by one self-naming overwrite of
  the base medicare_evt_payment_posting sentence "Once the resident has had the returned-payment limit of dishonored
  payments within the rolling lookback of calendar months ending on the payment date, only certified funds are accepted
  from the resident on any coverage episode."
  - It is one shared replaced_by sentence, verbatim in both payment rules, naming both siblings' cases. For the card
    payment and the bank draft, the dishonored payments counted are those recorded on the coverage episode the payment
    is for, within the rolling lookback; once that count reaches the returned-payment limit, neither payment is taken.
    For every other payment the base clause is restated verbatim.
  - Compute: rp_n = COUNT(medicare_payment_reversal, within_months = returned_payment_lookback_months, date_field
    entry_date); result is 0 when rp_n reaches the returned_payment_limit.
  - Probes: two returns on this episode in the lookback -> card 0 / bank draft 0; one return -> payment taken.
- R4-C2 (bank-draft wait on a reduction that can be 0.00 or out of the reduction's scope), closed with the whole class
  "every wait engaged and unmet at the opening AND satisfiable by its resolver in every engaged world":
  - bank draft <- reduction: the wait now covers only uncertified-day reversals posted after the charge "and taking back
    days that take a resident share above nothing under the split in effect on them". The bank draft's record test adds
    a 2024-or-later block and an open balance above nothing (the reduction's own test). G1 (lapse wholly on 0 % days):
    the wait is not engaged, the reduction posts nothing, and the bank draft takes the open balance. G2 (2022 world):
    out of every record test.
  - reduction <- rate-year correction: the wait is now engaged only where the charge's recorded rate is above the
    year rate "and its days take a resident share above nothing" (a zero share gives a zero correction).
  - card <- resident charge: the wait is now engaged only "whenever that block's covered days take a resident share
    above nothing" (a zero-share block has no charge posted, by base).
  - The sentences are updated in the rules, prerequisite policy_source/condition, task closures and rationales. All
    three waits are engaged and unmet at the opening of the task worlds and resolved there by positive writes.
- Further member found by the same tests (O3 class): the resident charge's and the card payment's record tests now also
  require a last service date in 2024 or later. Every year-rate ladder now prices only years it states; a pre-2024 block
  is outside every record test (2022 probe: all 0).
- Rounding ruling: every half-up rounding in compute is now RND((x) / 100 + 0.000000001, 2) on the summed non-negative
  figure (previously int(x + 0.5) / 100). Every scored, baseline and sensitivity figure in both worlds is a multiple of
  1/8 cent, so none lies within 1e-6 below a half cent (exact half-cent ties round up). The residue within 1e-9 below a
  half cent is DSL-KNOWN per the ruling.
- Render findings 1 and 2 stay closed (probe rows "charge billed below its days" and "hospital-day reversal posted after
  the charge").
- C11 / T*-F1 / T*-F2: BLUEPRINT-KNOWN, not reopened.

### T1 / T2 per factor (verified on worlds, not by argument)
Rows: world | policy | ... | whether every factor's solo figure (all OTHER factors at baseline) differs from the
all-baseline figure.
| task0 world | medicare_ext_resident_block_share | value 1885.5 | all-baseline 3851.75 | T1 [('f_year_rate', 1953.0), ('f_carried_split', 2933.0), ('f_held_nights', 1990.25), ('f_hospital_reversal', 1937.88), ('f_uncertified_days', 1990.25)] | T2 [('f_year_rate', 3718.63), ('f_carried_split', 2224.25), ('f_held_nights', 3526.25), ('f_hospital_reversal', 3689.0), ('f_uncertified_days', 3526.25)] | T2 all move: True |
| task0 world | medicare_ext_card_payment_share | value 1885.5 | all-baseline 0 | T1 [('f_year_rate', 0), ('f_carried_split', 0), ('f_held_nights', 0), ('f_hospital_reversal', 0), ('f_uncertified_days', 0)] | T2 [('f_year_rate', 0), ('f_carried_split', 0), ('f_held_nights', 0), ('f_hospital_reversal', 0), ('f_uncertified_days', 0)] | T2 all move: False |
| task1 world | medicare_ext_resident_rate_year_correction | value 18.75 | all-baseline 117.0 | T1 [('f_year_rate', 32.5), ('f_carried_split', 37.5), ('f_held_nights', 26.25), ('f_hospital_reversal', 22.5), ('f_absence_reversal', 22.5)] | T2 [('f_year_rate', 67.5), ('f_carried_split', 58.5), ('f_held_nights', 91.0), ('f_hospital_reversal', 104.0), ('f_absence_reversal', 104.0)] | T2 all move: True |
| task1 world | medicare_ext_reversed_day_reduction | value 419.0 | all-baseline 523.75 | T1 [('f_reduction_rate', 434.0), ('f_carried_split', 523.75), ('f_held_in_lapse', 523.75), ('f_hospital_in_lapse', 523.75)] | T2 [('f_reduction_rate', 523.75), ('f_carried_split', 523.75), ('f_held_in_lapse', 523.75), ('f_hospital_in_lapse', 523.75)] | T2 all move: False |
| task1 world | medicare_ext_bank_draft_payment | value 104.75 | all-baseline 0 | T1 [('f_year_rate', 0), ('f_carried_split', 0), ('f_held_nights', 0), ('f_hospital_reversal', 0), ('f_absence_reversal', 0), ('f_uncertified_days', 0)] | T2 [('f_year_rate', 0), ('f_carried_split', 0), ('f_held_nights', 0), ('f_hospital_reversal', 0), ('f_absence_reversal', 0), ('f_uncertified_days', 0)] | T2 all move: False |
| T2 scratch (charge billed 217.00/100%) | medicare_ext_resident_block_share | value 1885.5 | all-baseline 3851.75 | T1 [('f_year_rate', 1953.0), ('f_carried_split', 2933.0), ('f_held_nights', 1990.25), ('f_hospital_reversal', 1937.88), ('f_uncertified_days', 1990.25)] | T2 [('f_year_rate', 3718.63), ('f_carried_split', 2224.25), ('f_held_nights', 3526.25), ('f_hospital_reversal', 3689.0), ('f_uncertified_days', 3526.25)] | T2 all move: True |
| T2 scratch (charge billed 217.00/100%) | medicare_ext_card_payment_share | value 1885.5 | all-baseline 3851.75 | T1 [('f_year_rate', 1953.0), ('f_carried_split', 2933.0), ('f_held_nights', 1990.25), ('f_hospital_reversal', 1937.88), ('f_uncertified_days', 1990.25)] | T2 [('f_year_rate', 3718.63), ('f_carried_split', 2224.25), ('f_held_nights', 3526.25), ('f_hospital_reversal', 3689.0), ('f_uncertified_days', 3526.25)] | T2 all move: True |
| T2 scratch (charge billed 217.00/100%) | medicare_ext_resident_rate_year_correction | value 18.75 | all-baseline 117.0 | T1 [('f_year_rate', 32.5), ('f_carried_split', 37.5), ('f_held_nights', 26.25), ('f_hospital_reversal', 22.5), ('f_absence_reversal', 22.5)] | T2 [('f_year_rate', 67.5), ('f_carried_split', 58.5), ('f_held_nights', 91.0), ('f_hospital_reversal', 104.0), ('f_absence_reversal', 104.0)] | T2 all move: True |
| T2 scratch (charge billed 217.00/100%) | medicare_ext_reversed_day_reduction | value 419.0 | all-baseline 1302.0 | T1 [('f_reduction_rate', 434.0), ('f_carried_split', 838.0), ('f_held_in_lapse', 523.75), ('f_hospital_in_lapse', 523.75)] | T2 [('f_reduction_rate', 1257.0), ('f_carried_split', 651.0), ('f_held_in_lapse', 1085.0), ('f_hospital_in_lapse', 1085.0)] | T2 all move: True |
| T2 scratch (charge billed 217.00/100%) | medicare_ext_bank_draft_payment | value 104.75 | all-baseline 1953.0 | T1 [('f_year_rate', 108.5), ('f_carried_split', 209.5), ('f_held_nights', 314.25), ('f_hospital_reversal', 209.5), ('f_absence_reversal', 209.5), ('f_uncertified_days', 523.75)] | T2 [('f_year_rate', 1885.5), ('f_carried_split', 976.5), ('f_held_nights', 1519.0), ('f_hospital_reversal', 1736.0), ('f_absence_reversal', 1736.0), ('f_uncertified_days', 1085.0)] | T2 all move: True |
The task-world payment rows show 0 (payment not taken) for every factor baseline and every solo figure, because each
raises the figure above the open balance. The reduction's solo figures hit the open-balance cap on the task world. The
"T2 scratch" world (the resident charge billed at 217.00 and 100 percent, both errors base names; producible) shows every
factor of every policy moving alone.

### Pairwise method-tier table (XF 7) — unchanged
Day-kind ladders: (a) whole in-block span before the date -> DAYS(s, e) + 1 | (b) date inside the span -> DAYS(s, date)
| (c) 0. Uncertified-span and lapse-overlap ladders follow the same three shapes, with the in-span overlaps subtracted.

### Decoy / absent-record probe sweep (round 5; task 0: charge, card | task 1: correction, reduction, bank draft;
### 0 = outside a record test, payment not taken, or nothing owed; zero results are not posted)
| task 0 | base | [1885.5, 1885.5] |
| task 0 | second Dec days_21_100 entry (rebooking; tie on last date) | [0, 0] |
| task 0 | no supplemental effective date (absent) | [1361.75, 1361.75] |
| task 0 | QMB on file from 2025-12-01 | [0.0, 0] |
| task 0 | block before absent | [0, 0] |
| task 0 | second entry with the block-before benefit day (tie) | [0, 0] |
| task 0 | block-before resident charge adjusted (gross read) | [1885.5, 1885.5] |
| task 0 | block-before resident charge at a mixed split | [0, 0] |
| task 0 | rebill resident charge on the block before | [1885.5, 1885.5] |
| task 0 | bed-hold leave of another month | [1885.5, 1885.5] |
| task 0 | second bed-hold leave in December | [0, 0] |
| task 0 | held day of the December leave taken back (cancelled) | [0, 0] |
| task 0 | second hospital-day reversal | [0, 0] |
| task 0 | booking-error reversal | [0, 0] |
| task 0 | reversal on the November block | [1885.5, 1885.5] |
| task 0 | leave-of-absence reversal on a held night | [0, 0] |
| task 0 | two dishonored payments on this episode in the lookback (R4-C1) | [1885.5, 0] |
| task 0 | one dishonored payment on this episode in the lookback | [1885.5, 1885.5] |
| task 0 | whole world shifted to 2022 (R4-C2 G2 / O3) | [0, 0] |
| task 1 | base | [18.75, 419.0, 104.75] |
| task 1 | second Dec days_21_100 entry (rebooking; tie on last date) | [0, 0, 0] |
| task 1 | no supplemental effective date (absent) | [0, 0.0, 0] |
| task 1 | QMB on file from 2025-12-01 | [0, 0.0, 0] |
| task 1 | block before absent | [0, 0, 0] |
| task 1 | second entry with the block-before benefit day (tie) | [0, 0, 0] |
| task 1 | block-before resident charge adjusted (gross read) | [18.75, 419.0, 104.75] |
| task 1 | block-before resident charge at a mixed split | [0, 0, 0] |
| task 1 | rebill resident charge on the block before | [18.75, 419.0, 104.75] |
| task 1 | bed-hold leave of another month | [18.75, 419.0, 104.75] |
| task 1 | second bed-hold leave in December | [0, 0, 0] |
| task 1 | held day of the December leave taken back (cancelled) | [0, 0, 0] |
| task 1 | second hospital-day reversal | [0, 0, 0] |
| task 1 | booking-error reversal | [0, 0, 0] |
| task 1 | reversal on the November block | [18.75, 419.0, 104.75] |
| task 1 | leave-of-absence reversal on a held night | [0, 0, 0] |
| task 1 | two dishonored payments on this episode in the lookback (R4-C1) | [18.75, 419.0, 0] |
| task 1 | one dishonored payment on this episode in the lookback | [18.75, 419.0, 104.75] |
| task 1 | whole world shifted to 2022 (R4-C2 G2 / O3) | [0, 0, 0] |
| task 1 | lapse posted on the charge's date (same-date) | [0, 0, 0] |
| task 1 | lapse posted before the charge | [0, 0, 0] |
| task 1 | charge priced the same-date reversed day (day count 28) | [0, 0, 0] |
| task 1 | hospital-day reversal posted after the charge (render finding 2) | [0, 0, 0] |
| task 1 | charge billed below its days (rate 204.00; render finding 1) | [0, 408.0, 0] |
| task 1 | lapse wholly on 0 % days 2025-12-10..12 (R4-C2 G1) | [18.75, 0.0, 523.75] |
| task 1 | check 50.00 applied to the resident charge | [18.75, 419.0, 54.75] |
| task 1 | check 50.00 applied then returned | [18.75, 419.0, 104.75] |
| task 1 | charge already paid in full (open balance 0) | [0.0, 0, 0] |
| task 1 | rate-year correction on the carrier's charge only | [18.75, 419.0, 104.75] |

### Sweeps
- compute_basis quotes, baseline sentences, policy_source and both replaced_by sentences are verbatim in their rules;
  superseded clauses are verbatim in base; every overwrite's base policy is in base_policy_refs; no int( rounding left
  (edit sweep: 0 issues).
- Proof text: prerequisite sentences and conditions in both closures replaced; rationales extended with ROUND 5 notes;
  prerequisite fields carry no world value.

### Gates (round 5, full suite)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; CACHE-DIFF INFO (optional).
REWORK round 5: gates 7/7 green

## REWORK round 6 — audit revision_5 (R5-C1)
Files changed: medicare.extended.yaml (card and bank-draft rules and compute), tasks/0.json and tasks/1.json
(design_rationale, solvability base precondition text and evidence; scored, baseline and sensitivity figures unchanged),
worklog.md. task_tools.py is unchanged.
- R5-C1 (the declared certified-funds override counted carrier/crossover reversals and carved card/bank out of the
  cross-episode count): the round-5 override is withdrawn, the rp_n binding is removed, and the base
  medicare_evt_payment_posting sentence "Once the resident has had the returned-payment limit of dishonored payments
  within the rolling lookback of calendar months ending on the payment date, only certified funds are accepted from the
  resident on any coverage episode." is no longer retired or contradicted.
  - Criterion chosen so no DSL route is needed: each payment rule now says that whether the payment may be taken at all
    is settled by that in-force base sentence (an eligibility condition on the resident's dishonored payments on every
    episode, which the agent reads from the full ledger), and that the policy prices the payment only where one may be
    taken.
  - The compute prices the figure; it does not decide eligibility, as for every other inherited base eligibility.
  - Both task worlds carry no payment reversal on any episode; the solvability contract cites the resident payment rows
    as evidence that the card / bank draft is accepted.
  - Members:
    (a) carrier or crossover reversals no longer decline a resident payment (probe below: carrier remittance returned
        twice on this episode -> both payments priced);
    (b) no method-specific carve-out remains; the base cross-episode rule governs card, bank draft and check alike.
  - Class sweep (every payment rule vs every in-force base posting clause), unchanged from round 4: one named charge;
    open balance (figure above it -> not taken); oldest-first split (n/a, one charge); card maximum (card caps at
    5000.00); accepted methods; certified funds (now deferred to the base sentence, not overridden); statement, due day
    and no late charge (no figure).
- The second overwrite introduced in round 5 is gone; the single shared split overwrite of medicare_evt_coinsurance is
  unchanged.

### T1 / T2 (round 6; unchanged from round 5, re-run)
| task0 world | medicare_ext_resident_block_share | value 1885.5 | all-baseline 3851.75 | T2 all move: True |
| task0 world | medicare_ext_card_payment_share | value 1885.5 | all-baseline 0 | T2 all move: False |
| task1 world | medicare_ext_resident_rate_year_correction | value 18.75 | all-baseline 117.0 | T2 all move: True |
| task1 world | medicare_ext_reversed_day_reduction | value 419.0 | all-baseline 523.75 | T2 all move: False |
| task1 world | medicare_ext_bank_draft_payment | value 104.75 | all-baseline 0 | T2 all move: False |
| T2 scratch (charge billed 217/100%) | medicare_ext_resident_block_share | value 1885.5 | all-baseline 3851.75 | T2 all move: True |
| T2 scratch (charge billed 217/100%) | medicare_ext_card_payment_share | value 1885.5 | all-baseline 3851.75 | T2 all move: True |
| T2 scratch (charge billed 217/100%) | medicare_ext_resident_rate_year_correction | value 18.75 | all-baseline 117.0 | T2 all move: True |
| T2 scratch (charge billed 217/100%) | medicare_ext_reversed_day_reduction | value 419.0 | all-baseline 1302.0 | T2 all move: True |
| T2 scratch (charge billed 217/100%) | medicare_ext_bank_draft_payment | value 104.75 | all-baseline 1953.0 | T2 all move: True |
(Task-world payment rows: every factor baseline and every solo figure gives 0, payment not taken, because the figure
then exceeds the open balance. Reduction solos hit the open-balance cap on the task world. On the producible scratch
world, every factor of every policy moves alone.)

### Probe sweep
- Payment-read rows new this round:
| task 0 | carrier remittance returned twice on this episode (R5-C1 a) | [1885.5, 1885.5] |
| task 1 | carrier remittance returned twice on this episode (R5-C1 a) | [18.75, 419.0, 104.75] |
- Every other read is unchanged since round 5; the round-5 decoy/absent-record sweep (every read: cancelled, reversed,
  second, tie, absent, same-date records, the render shapes, N1-N3, G1/G2) stands as recorded, except its two
  "dishonored payment" rows: that read is gone, and eligibility now follows the base sentence.

### Sweeps
compute_basis quotes, policy_source and replaced_by verbatim in their rules; superseded clause in base; no rp_n or
round-5 override text left in the yaml or the task files (sweep: 0 issues). Pairwise method-tier table unchanged.

### Gates (round 6, full suite)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; CACHE-DIFF INFO (optional).
REWORK round 6: gates 7/7 green

## REWORK round 7 — KB re-audit source item S5 (_kb_verdict.md revision_2)
Files changed:
- medicare.extended.yaml: one sentence and one gate per policy; medicare_evt_secondary_and_qmb added to
  base_policy_refs where it was missing.
- tasks/0.json and tasks/1.json: design_rationale only.
- worklog.md.
task_tools.py is unchanged. Scored, baseline and sensitivity figures are unchanged (nothing forced them to move).
- S5 (the extended rules could bill the resident on a balance-billing-prohibited tier): each of the five rules now
  carries "When the tier on file prohibits balance billing, as the QMB Medicaid Crossover tier does, the resident is
  never billed any Medicare cost sharing on the coverage: no day of it takes a resident share above nothing, whatever
  split would otherwise apply, and <its figure> is nothing."
  - Compute: binding bb_prohibited = P('balance_billing_prohibited') (the tier parameter base sets); every result is 0
    when it is true.
  - No in-force base clause is contradicted: the base QMB clause is followed, not retired. Base "keep the earlier
    split" still applies on every tier that allows balance billing.
- Class sweep:
  - Tiers whose resident share base sets at zero: QMB Medicaid Crossover (balance_billing_prohibited true) and
    Full-Coinsurance Medigap (resident share 0, balance billing not prohibited). The QMB tier now leaves every resident
    figure at nothing.
  - The full-coinsurance tier is zero only from its supplemental effective date. Base keeps the earlier split before it
    ("so days before the supplemental effective date keep the earlier split"), and the rules already price those
    earlier days and nothing after the date. Zeroing that tier would contradict base, so it is deliberately not in the
    class.
  - The waits: under the new sentence no day of a QMB coverage takes a resident share above nothing, so the card,
    reduction and bank-draft waits are not engaged there. No engaged wait meets a resolver that gives nothing.
- Probes (task 0: charge, card | task 1: correction, reduction, bank draft):
| task 0 | QMB Medicaid Crossover tier on file, supplemental effective date 2025-12-16 inside the block (S5) | [0, 0] |
| task 0 | Full-Coinsurance Medigap tier (plan G) from the same date | [1047.5, 1047.5] |
| task 1 | QMB Medicaid Crossover tier on file, supplemental effective date 2025-12-10 inside the block (S5) | [0, 0, 0] |
| task 1 | Full-Coinsurance Medigap tier (plan G) from the same date | [18.75, 419.0, 104.75] |
- T1 / T2 re-run: identical to round 6 (task worlds and the producible scratch world). The QMB gate is not engaged on any
  of those worlds:
| task0 world | medicare_ext_resident_block_share | value 1885.5 | all-baseline 3851.75 | T2 all move: True
| task0 world | medicare_ext_card_payment_share | value 1885.5 | all-baseline 0 | T2 all move: False
| task1 world | medicare_ext_resident_rate_year_correction | value 18.75 | all-baseline 117.0 | T2 all move: True
| task1 world | medicare_ext_reversed_day_reduction | value 419.0 | all-baseline 523.75 | T2 all move: False
| task1 world | medicare_ext_bank_draft_payment | value 104.75 | all-baseline 0 | T2 all move: False
| T2 scratch (charge billed 217/100%) | medicare_ext_resident_block_share | value 1885.5 | all-baseline 3851.75 | T2 all move: True
| T2 scratch (charge billed 217/100%) | medicare_ext_card_payment_share | value 1885.5 | all-baseline 3851.75 | T2 all move: True
| T2 scratch (charge billed 217/100%) | medicare_ext_resident_rate_year_correction | value 18.75 | all-baseline 117.0 | T2 all move: True
| T2 scratch (charge billed 217/100%) | medicare_ext_reversed_day_reduction | value 419.0 | all-baseline 1302.0 | T2 all move: True
| T2 scratch (charge billed 217/100%) | medicare_ext_bank_draft_payment | value 104.75 | all-baseline 1953.0 | T2 all move: True
- Sweeps: compute_basis quotes (including the new sentence on bb_prohibited and result), policy_source and replaced_by
  are verbatim in their rules; the superseded clause is in base; every binding has a basis (edit sweep: 0 issues).
  Rationales now describe the QMB gate; prerequisite fields carry no world value. The other reads are unchanged, so the
  round-5/6 probe sweeps stand.

### Gates (round 7, full suite)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; CACHE-DIFF INFO (optional).
REWORK round 7: gates 7/7 green

## REWORK round 8 — audit revision_7 (R7-C1)
Files changed:
- medicare.extended.yaml: one sentence per policy replaced; the bb_prohibited binding and gate removed.
- tasks/0.json and tasks/1.json: design_rationale only (round-7 note marked superseded, ROUND 8 note added).
- worklog.md.
task_tools.py is unchanged. Scored, baseline and sensitivity figures are unchanged (none forced).
- R7-C1 (the round-7 QMB sentence zeroed pre-QMB days, contradicting base and the non-retroactive federal rule).
  - In all five policies the sentence now reads: "When the tier on file prohibits balance billing, as the QMB Medicaid
    Crossover tier does, <figure> bills the resident nothing for any day on or after the tier's supplemental effective
    date, those days taking the tier's resident share of nothing, while days before that date keep the earlier split,
    QMB protection not reaching back before it."
  - This is the reading the shared replaced_by restates for out-of-scope blocks, and base medicare_evt_coinsurance's own
    clause.
  - Compute: the round-7 gate is removed. Days from the effective date already take the tier-on-file share (0 for QMB);
    earlier days take the carried share; a coverage recording no date has the tier on file on every day. The sentence is
    now quoted as the basis of tier_share, so rule words == compute.
- Class sweep (all five policies, every tier):
  - QMB: zero from the date, earlier split before it.
  - Full-Coinsurance Medigap: same shape (0 % from its date, earlier split before).
  - K, L, A/B, none: unchanged.
  - Waits: on a QMB block wholly after the date no day takes a share above nothing, so the waits are not engaged. On a
    block before the date the earlier share is positive and the resolvers write positive figures.
  - No extended rule contradicts an in-force base clause.
- Probes (task 0: charge, card | task 1: correction, reduction, bank draft):
| task 0 | Q1: QMB tier, supplemental effective date 2026-01-01 (December block wholly before it) | [2723.5, 2723.5] |
| task 0 | QMB tier, supplemental effective date 2025-12-01 (December block wholly after it) | [0.0, 0] |
| task 0 | QMB tier, no supplemental effective date recorded | [0.0, 0] |
| task 0 | Full-Coinsurance Medigap (plan G) from the task's date | [1047.5, 1047.5] |
| task 1 | Q1: QMB tier, supplemental effective date 2026-01-01 (December block wholly before it) | [101.25, 441.25, 0] |
| task 1 | QMB tier, supplemental effective date 2025-12-01 (December block wholly after it) | [0, 0.0, 0] |
| task 1 | QMB tier, no supplemental effective date recorded | [0, 0.0, 0] |
| task 1 | Full-Coinsurance Medigap (plan G) from the task's date | [18.75, 419.0, 104.75] |
  The Q1 world gives the auditor's earlier-split reading. In the task-1 Q1 variant the seeded charge was billed under the
  task's split, so it is under-billed for Q1, and the bank draft is not taken (render finding 1 path).
- T1 / T2 re-run, unchanged (task worlds and the producible scratch world):
| task0 world | medicare_ext_resident_block_share | value 1885.5 | all-baseline 3851.75 | T2 all move: True
| task0 world | medicare_ext_card_payment_share | value 1885.5 | all-baseline 0 | T2 all move: False
| task1 world | medicare_ext_resident_rate_year_correction | value 18.75 | all-baseline 117.0 | T2 all move: True
| task1 world | medicare_ext_reversed_day_reduction | value 419.0 | all-baseline 523.75 | T2 all move: False
| task1 world | medicare_ext_bank_draft_payment | value 104.75 | all-baseline 0 | T2 all move: False
| T2 scratch (charge billed 217/100%) | medicare_ext_resident_block_share | value 1885.5 | all-baseline 3851.75 | T2 all move: True
| T2 scratch (charge billed 217/100%) | medicare_ext_card_payment_share | value 1885.5 | all-baseline 3851.75 | T2 all move: True
| T2 scratch (charge billed 217/100%) | medicare_ext_resident_rate_year_correction | value 18.75 | all-baseline 117.0 | T2 all move: True
| T2 scratch (charge billed 217/100%) | medicare_ext_reversed_day_reduction | value 419.0 | all-baseline 1302.0 | T2 all move: True
| T2 scratch (charge billed 217/100%) | medicare_ext_bank_draft_payment | value 104.75 | all-baseline 1953.0 | T2 all move: True
- Sweeps:
  - compute_basis quotes (including the new sentence on tier_share), policy_source and replaced_by are verbatim in their
    rules; the superseded clause is in base; no bb_prohibited binding and no "whatever split would otherwise apply" text
    left (edit sweep: 0 issues).
  - Rationales carry no stale zero-all claim. Only the QMB treatment changed in this round; the other reads are untouched
    and their probe rows stand from rounds 5-7.

### Gates (round 8, full suite)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; CACHE-DIFF INFO (optional).
REWORK round 8: gates 7/7 green
