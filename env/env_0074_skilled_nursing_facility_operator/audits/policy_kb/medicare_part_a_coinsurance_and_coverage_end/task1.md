# Policy-KB bijection audit — medicare_part_a_coinsurance_and_coverage_end / task 1

## revision_1

Scope: `medicare_ext_resident_rate_year_correction` (`correct_coinsurance_rate_feac0074`), `medicare_ext_reversed_day_reduction` (`reduce_coinsurance_for_reversed_days_0894f336`), `medicare_ext_bank_draft_payment` (`pay_coinsurance_by_bank_draft_32bb229d`), their base refs (`medicare_evt_coinsurance`, `medicare_evt_secondary_and_qmb`, `medicare_evt_payment_posting`, `medicare_coverage_tier_change`, `medicare_evt_day_counting`), variant figures and tool contracts. Same corpus/source hashes and method as task0.

## source_to_kb

### medicare_ext_resident_rate_year_correction
- Rule sentences (17): all verbatim. Hub `rate_year_corrections` (subject, "falls due when such a charge stands", tool contract). Computation `rate_year_correction_computation`: latest-block selection, record test, replaced_by, baseline (year-of-service rate 204.00 = rate_2024, earlier share 100, count the charge's days, two figures, difference clamped to [0, open balance], days-before rule, shares, sum/100 half-up once), supplemental-date reading, uncertified-day clause with "posted on or before the date the charge was posted" (rule clause, not a declared factor).
- Factors: f_year_rate `rate_year_correction_year_of_service_rate` (2026+ -> 217.00; 2025 -> 209.50; otherwise -> 204.00, "which the record test limits to … 2024"); f_carried_split `rate_year_correction_earlier_share`; f_held_nights `rate_year_correction_bed_hold_nights`; f_hospital_reversal `rate_year_correction_hospital_days` (posted-on-or-before condition carried in both tiers and in the Q&A); f_absence_reversal `rate_year_correction_leave_of_absence_days` (same). Every tier exact.
- prerequisite: [] — none rendered. Correct.
- Base: "A charge priced at the wrong year's rate is corrected with the reason 'rate-year correction' by the difference" carried in `secondary_denials_and_qmb_writeoffs` (in force; consistent with the extended computation for the resident charge).
- Tool contract: doc table/return = docstring; reason always `rate_year_correction`. Exact.

### medicare_ext_reversed_day_reduction
- Rule sentences (17): all verbatim. Hub `reversed_day_charge_reductions`: subject ("applies to the resident's original coinsurance charge … for the days of the uncertified-day reversal posted … after the charge was posted"), state_due, prerequisite sentence, tool contract. Computation `reversed_day_reduction_computation`: record test (incl. "open balance is above nothing"), replaced_by, baseline (recorded daily rate, earlier share 100, reversal's day count, cap at open balance, span-before rule, shares, sum/100 half-up once), "Each kind of day named below that lies inside that part of the span…", LOA-overlap clause (rule clause, not a declared factor).
- Factors: f_reduction_rate `reversed_day_reduction_daily_rate` (correction on record + 2025 -> 209.50; + 2024 -> 204.00; + 2026 or later -> 217.00; otherwise the recorded rate); f_carried_split `reversed_day_reduction_earlier_share`; f_held_in_lapse `reversed_day_reduction_bed_hold_overlap` (names Bed-Hold and Leave Reservations and the record kind; "The figure modified is the reversed days … before the supplemental effective date"); f_hospital_in_lapse `reversed_day_reduction_hospital_overlap`. Every tier exact.
- prerequisite (1): "A reduction for reversed covered days on a resident coinsurance charge is fixed only after the records carry a rate-year correction against that charge whenever the charge's recorded daily rate is above the rate of the year in which its days were furnished and its days take a resident share above nothing under the split in effect on them." — verbatim in `reversed_day_charge_reductions` only; form state; connective "only after", condition "whenever … and …" intact. Resolution basis: `rate_year_corrections` describes the write in the sentence's words ("takes back what a resident's original coinsurance charge … billed above that year's rate … posted against the charge with the reason 'rate-year correction'"); records: ledger `medicare_coinsurance_adjustment.adjustment_reason`, charge `daily_coinsurance_rate`. Same strength.
- Tool contract: doc = docstring (reason carried over from the reversal). Exact.

### medicare_ext_bank_draft_payment
- Rule sentences (19): 18 verbatim; "Each kind of day named below that is not a covered day is taken off those days, never leaving fewer than none nor more than the days the bank draft counts." is rendered as "The days the bank draft counts before the supplemental effective date never number fewer than none nor more than the days the bank draft counts." — the clamp is kept and the taking-off is stated in each of the four factor documents ("come off the days the bank draft counts before the supplemental effective date"); since every kind of day is a declared factor here, nothing is "named below" in the computation document. Equivalent at the level of entailment.
- Hub `coinsurance_bank_draft_payments`: prerequisite sentence, certified-funds sentence, tool contract (user-owned). Computation `bank_draft_amount_computation`: record test (incl. "no hospital-day or leave-of-absence reversal … posted after" and "open balance above nothing"), replaced_by, baseline (217.00, 100, covered days, net payments, floor 0), supplemental-date reading, shares, rounding, open-balance clause.
- Factors: f_year_rate `bank_draft_rate_year`; f_carried_split `bank_draft_earlier_share`; f_held_nights `bank_draft_bed_hold_nights`; f_hospital_reversal `bank_draft_hospital_day_reversals`; f_absence_reversal `bank_draft_leave_of_absence_reversals`; f_uncertified_days `bank_draft_uncertified_days`. Every tier exact.
- prerequisite (1): "A bank-draft payment toward a resident coinsurance charge is not taken until the records carry, against that charge, a reduction for every uncertified-day reversal posted against its booked-days entry after the charge itself was posted and taking back days that take a resident share above nothing under the split in effect on them." — verbatim in `coinsurance_bank_draft_payments` only; form state; "not … until", "every", "after the charge itself was posted" intact. Resolution basis: `reversed_day_charge_reductions` hub uses the same words for its subject; records: `medicare_days_reversed` with `adjustment_reason uncertified_day` and `entry_date`, adjustments naming `charge_entry_id`. Same strength.
- Tool contract: doc = docstring (method "ach"). Exact.

### Shared
- Retired surface, variant figures, base posting rules: as in task0 (PASS). Day-reversal reasons and "reversing days of the days 21 through 100 band reduces the coinsurance charged on them" carried in `covered_day_booking_and_reversal`; "Reversed covered days reduce the coinsurance charged on them with the day reversal's own reason" and the open-balance cap in `secondary_denials_and_qmb_writeoffs`.

## kb_to_source

- Every normative sentence of the 21 path documents traces to a source atom; no added step, confirmation, review or notification. Hub "When a bank draft may be taken." / "When the reduction is fixed." are headings over the source sentences.
- Cross-problem operational guidance: none; each tool named only in its own hub.
- Opening world state written as policy fact: none stated as a fact. But see E1 below — a worked example reproduces this task's world shape and its scored value as a hypothetical.
- Renderer-added text beyond the factor (not a semantic addition): `rate_year_correction_year_of_service_rate` illustration ends "the rate-year correction is 60.00 where the charge's open balance allows it" — alludes to the computation's cap; it adds no rule and does not hint at another factor (observation).
- Seed-value coincidences (not scored, observation only): the earlier-share examples' "resident charge of 1047.50 for 10 days at a recorded 209.50" equals this world's carrier uncertified-day adjustment `6ff86bff` (1047.50).

## bijection_verdict

**PASS** (KB-BIJECTION). Complete domains of the three policies, all 15 factor ladders, both prerequisite edges and the tool contracts correspond losslessly. No previous revision.

## dependency_form

- Both prerequisite sentences verbatim, state form, only on the blocked side; hops bank draft -> reduction -> rate-year correction were state-derived in the blind answer. No route, aggregated chain, dependency table or other problem's tool name anywhere. Titles general.
- `reversed_day_reduction_daily_rate` reads "when the records carry a rate-year correction against the charge" — the source ladder's own tier condition (record test), not a restated dependency or an order; not RED by itself.
- **E1 — KB-EXPLICIT RED (example mirrors this task's world and states a scored value).** Document `reversed_day_reduction_daily_rate_f27b082c.json` ("Daily Rate Applied When Reducing a Medicare Part A Resident Charge for Reversed Days"), worked example: "*Hypothetical worked example:* a resident's charge records 217.00 a day for a block whose last service date falls in 2025, and a rate-year correction against it is on record. Two reversed days at a resident share of 100 percent are priced at 209.50 each: 419.00. Without the correction on record, the same two days would be priced at the recorded 217.00."
  - Symptom: the example's world is task1's world (resident charge `4cf64f04` records 217.00 for a block ending 2025-12-31; the chain puts a rate-year correction on record before the reduction), and its result 419.00 is exactly the scored `amount` of `reduce_coinsurance_for_reversed_days_0894f336` in task1 (expected 419.00 = 209.50 x (4 x 50) / 100).
  - Root cause: renderer-authored example (not in the factor ladder or anywhere in `medicare.extended.yaml`; grep for 419 in the source finds nothing).
  - Effect: a solver can anchor the reduction amount on the example's figure without working the day count and the earlier share; the solution stays unique (KB-RUNTIME unaffected), so this is recorded here only.
- Observation (not RED): `reversed_day_reduction_hospital_overlap` example "the lapse spans the 4th to the 10th, and a hospital-day reversal on the same entry covers the 6th and 7th" shares the lapse start (4th) and a hospital day (6th) with task1 (lapse 12-04..12-12, hospital 12-06); end date, supplemental dates (7th/11th/5th vs 10th) and outcomes differ, so it does not reproduce the world or a scored value.
- Computation-document "Record test" and replaced_by enumeration: verbatim source text (see S1, S3 in `_kb_verdict.md`); the year-of-service factor's "which the record test limits to … 2024" is the source ladder's own parenthesis (S2).

**KB-EXPLICIT RED: E1.**

## revision_2

Corpus `21f7544f…`; source unchanged. Snapshot 2026-10-22T19:39:06 all green.

### E1 — closed
`reversed_day_reduction_daily_rate_f27b082c.json` example now reads: "a resident's charge records 209.50 a day for a block whose last service date falls in 2024, and a rate-year correction against it is on record. Four reversed days at a resident share of 100 percent are priced at 204.00 each: 816.00. Without the correction on record, the same four days would be priced at the recorded 209.50." — different recorded rate (209.50 vs task1's 217.00), different year (2024 vs 2025), different result (816.00 vs scored 419.00). The ladder text above it is unchanged. **Closed.**

### source_to_kb / kb_to_source
- Only examples changed (see task0 revision_2). Re-worked on this path: `rate_year_correction_computation` (Plan A or B, 11 days: 2387.00 - 2244.00 = 143.00; 0.00 case); `rate_year_correction_year_of_service_rate` (7 days at 209.50 on a 2024 block: 1466.50 - 1428.00 = 38.50; the revision_1 cap allusion is gone); `reversed_day_reduction_computation` (Plan A or B, 4 days at 217.00 -> 868.00; cap 610.00); bed-hold overlap (lapse 17th-23rd, held 20th-21st); hospital overlap (lapse 22nd-28th, hospital 24th-25th); `bank_draft_amount_computation` (QMB, 17th-28th, date 24th: 7 x 100 + 5 x 0 -> 1519.00 less 300.00 -> 1219.00); bank-draft factor examples. All consistent with their rules; nothing added.
- Observation (S5, source-borne): the bank-draft computation example takes a draft from a QMB-tier resident (see task0 revision_2).

### bijection_verdict
**PASS** — nothing regressed.

### dependency_form
- Sweep for task1 mirrors and scored values (18.75, 419.00, 104.75; 217.00 charged on a 2025 block; date 10th; LOA 1st, held 3rd-4th, hospital 6th, uncertified 4th-12th; Plan N / K -> N; seed 542.50, 523.75, 1780.75, 1047.50, 5132.75): none present. The revision_1 observation (hospital-overlap example 4th/6th) is resolved (now 22nd-28th / 24th-25th). The 1047.50 earlier-share example is replaced (1519.00 / 14 days).
- Both prerequisite sentences, titles, tool placement unchanged.

**PASS** (KB-EXPLICIT). E1 closed.

## revision_3

Corpus `77516c68…` (round 4); source `ddc0242f…`; tools `91fc2fae…`. Snapshot 2026-10-23T06:24:59 all green.

### source_to_kb / kb_to_source
- New source atom (S5 rework): each of the five extended `rule`s gains "When the tier on file prohibits balance billing, as the QMB Medicaid Crossover tier does, the <figure> bills the resident nothing for any day on or after the tier's supplemental effective date, those days taking the tier's resident share of nothing, while days before that date keep the earlier split, QMB protection not reaching back before it." It is neither in `baseline.rule` nor a factor. Re-running the sentence location finds it verbatim in each policy's computation document (shares clause: bank draft "Shares", card "(g)", rate-year bullet, resident charge "7.", reduction "7."), and in no other document. Every other rule sentence is still located as in revision_1 (the bank-draft clamp is still rendered equivalently). The base-rule location count is unchanged.
- Rewritten examples, re-worked:
  - Resident charge: tier without supplemental coverage until a QMB determination in April 2026, supplemental effective date 1 May 2026 (consistent with "the first day of the month after the determination month"). April block: 30 booked days, 2 LOA days, all days before the date -> 28 x 217.00 x 100 -> 6076.00. May block 1-19 May: date not after the first service date -> 19 days at 0 -> 0.00. Both correct.
  - Bank draft: Plan A or B -> QMB after a June 2026 determination, date 1 July 2026. June block 1-24 June: 24 days before the date at 100 percent -> 5208.00 less 1208.00 -> 4000.00, open balance 4000.00. Correct.
  - Both examples now agree with the base rule in `secondary_denials_and_qmb_writeoffs`: nothing is billed on QMB-protected days, and the protection starts on the recorded date.
- No added step or claim. Observation only: the new sentence says days before the date "keep the earlier split", while the shares clause next to it says they "take the earlier share". This is source wording and reads consistently: for a passing block the earlier share is read from the block before.

### bijection_verdict
**PASS** — the new atom is carried verbatim, and nothing regressed.

### dependency_form
- Prerequisite sentences, titles and tool placement are unchanged. The new sentence names no other problem, tool or route.
- Sweep for mirrors and scored values (task0: 1885.50, 26, Plan L, the 16th, held 6th-7th, hospital 10th, uncertified 13th-14th; task1: 18.75, 419.00, 104.75, 217.00 on a 2025 block, the 10th, Plan N): none in the new or old examples. The new examples are set in April-July 2026 under the tier without supplemental coverage, Plan A or B and QMB tiers. E1 remains closed.

**PASS** (KB-EXPLICIT).

## revision_4 (cross-product re-judge, 2026-10-23)

- Entry: snapshot 2026-10-23 (`kb_snapshot.sh`): EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; DOCS OK; TRACEABILITY OK (0 non-unlock misses). Source `ddc0242f…`, tools `91fc2fae…` and docs/medicare `77516c68…` are unchanged since revision_3. Other corpora read for this pass: bedhold `24cc3f6d…` (all 50 titles; the 22 non-charge-computation documents in full), private `9c9f001f…` (daily-rate schedule). Also published: medicaid `b89c3e2b…`, trust `600f4bac…`, ancillary `73c2a1c3…`, therapy `d4b962bb…`.
- Other-product holdings: every finder for private, medicaid, trust, ancillary and therapy returns "No … records" for this resident. The only cross-product rows are Bed-Hold and Leave Reservations rows.
- source_to_kb / kb_to_source: medicare corpus and source unchanged since revision_3 -> **PASS** (KB-BIJECTION).
- Cross-product findability: each held-night factor document names "Bed-Hold and Leave Reservations records" and "held days booked for the same service month". The published bedhold corpus uses the same terms ("One held-days entry is booked for each service month and each day payer … its first held day, its last held day and its day count"), so the factor can be reached from the bedhold record words. The bedhold corpus states no Medicare coinsurance rule, so the two products do not contradict each other.
- dependency_form: unchanged -> **PASS** (KB-EXPLICIT).
- Seeded cross-product rows: see `runtime_context/.../task1.md` revision_4. Every row is OK, so there are no new source or seed items.
