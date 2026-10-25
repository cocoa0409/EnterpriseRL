# KB verdict — medicare_part_a_coinsurance_and_coverage_end (product medicare)

## revision_1 (2026-10-22)

Entry conditions: policy verdict `VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN`; snapshot `/tmp/erl0074_coord/kb_snapshot.sh` re-run 2026-10-22T18:14 — EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK; DOCS OK; TRACEABILITY OK (0 non-unlock misses). Corpus tree sha256 `ece4e204…`, source `203ecd58…`, task_tools `91fc2fae…`. Blind audits frozen before reveal (task0.md `1013b608…`, task1.md `2f6e21e5…`); no contamination.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| task0 (card payment; resident charge first) | PASS (1885.50 charge / 26 / 209.50; card 1885.50) | PASS | PASS |
| task1 (bank draft; rate-year correction -> reduction first) | PASS (18.75 / 419.00 / 104.75) | PASS | RED: E1 |

Cross-product: the held-night factors (f_held_nights, f_held_in_lapse) read the Bed-Hold and Leave Reservations ledger; that product is not yet published, so the held-night tiers in both tasks (2 nights each) are **conditional** pending the bedhold re-judge.

### KB findings
- **E1** (task1, KB-EXPLICIT): `docs/medicare/reversed_day_reduction_daily_rate_f27b082c.json`, worked example — a charge recording 217.00 for a 2025 block with a rate-year correction on record, "Two reversed days at a resident share of 100 percent are priced at 209.50 each: 419.00". It mirrors task1's world and equals task1's scored reduction amount (419.00). Renderer-authored; not in the source.

Observations (not verdict items): `reversed_day_reduction_hospital_overlap` example shares two dates with task1 (lapse from the 4th, hospital day the 6th); `reversed_day_reduction_computation` example result 628.50 and the earlier-share examples' 1047.50 equal unscored seed values (task0 Nov resident charge; task1 carrier uncertified adjustment); `rate_year_correction_year_of_service_rate` illustration mentions the open-balance cap ("where the charge's open balance allows it").

### Source-side items (policy, reported, not KB defects)
- **S1**: the `rule` of each of the five extended policies contains a "record test" that names the evidence of the declared factors (the block before's 100/50/25-percent billing -> f_carried_split; the month's bed-hold leave -> f_held_nights / f_held_in_lapse; hospital-day / leave-of-absence / uncertified reversals; "last service date falls in 2024 or later" -> the year-rate ladder). The KB must carry it beside the computation, so every computation document pre-signals which variations exist before the reader has looked at the records.
- **S2**: `medicare_ext_resident_rate_year_correction.factors.f_year_rate` ladder tier "otherwise (the record test leaves a last service date in 2024)" makes the factor point at the computation's record test; carried verbatim in `rate_year_correction_year_of_service_rate` ("which the record test limits to one whose last service date falls in 2024"; table row "Any other — within the record test, a date in 2024").
- **S3**: the shared `overwrite.replaced_by` (identical in all five policies) names all five problems of the difficulty ("the resident coinsurance charge, the card payment, the rate-year correction, the reduction for reversed covered days and the bank draft each count … as their own policies state"), so every computation document lists the other problems of the tree. It states no order, but it is a cross-problem enumeration carried in five documents.
- **S4**: some rule clauses that change the computed figure are neither in `baseline.rule` nor declared as factors: the leave-of-absence clause of `medicare_ext_resident_block_share` and `medicare_ext_card_payment_share`, the uncertified-day clause of `medicare_ext_resident_rate_year_correction`, and the leave-of-absence-overlap clause of `medicare_ext_reversed_day_reduction`. The KB places them in the computation documents, which therefore carry more than `baseline.rule`. No scored number is affected in either task (each such clause takes off 0 days in its world).

Closing checklist: audit files 1:1 with tasks (runtime_context/task0.md, task1.md; policy_kb/task0.md, task1.md); every prerequisite sentence verbatim, state form, blocked side only; every factor ladder (25 across five policies) complete in its own document and findable from record words; no tool name, route or aggregated chain beyond the prerequisite sentences. Difficulty not closed: E1 open.

KB VERDICT revision_1: task0=PASS task1=RED E1 kb=E1 src=S1,S2,S3,S4

## revision_2 (2026-10-22, re-audit after RENDER round 3)

Entry: `RENDER.log` tail `RENDER round 3: DOCS OK`. Snapshot 2026-10-22T19:39:06: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK; DOCS OK; TRACEABILITY OK (0 non-unlock misses). Corpus tree `21f7544f55080c56…` (was `ece4e204…`); source `203ecd58…` / `91fc2fae…` unchanged; runtime views unchanged.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| task0 | PASS | PASS | PASS |
| task1 | PASS | PASS | PASS (E1 closed) |

- E1 closed: the daily-rate factor example now uses 209.50 recorded on a 2024 block -> 816.00. That is neither task1's world (217.00 on a 2025 block) nor its scored 419.00.
- Regression check: a diff of all 56 documents shows that only examples and illustrations changed (35 hunks). Rule text, schedules, ladders, prerequisite sentences, tool tables and titles are byte-identical. All new examples re-worked: the arithmetic is correct and they are consistent with their rules. A sweep for task-world mirrors and scored or seed values across all 56 documents found none. The revision_1 observations (4th/6th hospital-overlap dates, 628.50, 1047.50, cap allusion) are gone.
- S1–S4: logged by the coordinator as placement notes and not carried as open items.
- **S5 (new, source-side)**: none of the five extended rules (record tests or shares) excludes a balance-billing-prohibited tier. Applied to a QMB Medicaid Crossover block with a supplemental effective date after its first service date, they bill the resident the earlier share for the days before that date. The base rule `medicare_evt_secondary_and_qmb` ("the resident is never billed any Medicare cost sharing") stays in force and is not overwritten. The round-3 examples in `resident_coinsurance_charge_computation` (QMB resident charge 1085.00) and `bank_draft_amount_computation` (QMB bank draft 1219.00) apply the extended rules faithfully and so make the tension visible. The KB is not judged on it, and no scored figure moves (neither task is in the QMB tier).
- Held-night tiers remain conditional on the unpublished bedhold corpus.

Difficulty closed for the medicare KB: all three parts PASS for both tasks.

KB VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=S5

## revision_3 (2026-10-23, re-audit after RENDER round 4 / S5 source rework)

Entry: `RENDER round 4: DOCS OK`. Snapshot 2026-10-23T06:24:59: EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK; DOCS OK; TRACEABILITY OK (0 non-unlock misses). Corpus `77516c68…`; source `ddc0242f…` (changed), tools `91fc2fae…`; GT writes and expected values unchanged.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| task0 | PASS | PASS | PASS |
| task1 | PASS | PASS | PASS |

- E1: still closed; the daily-rate factor document is unchanged since round 3.
- S5: closed at the source. The balance-billing sentence was added to all five rules and is carried verbatim in the five computation documents only. The QMB examples now place the supplemental effective date on the first of the month after the determination, and they bill the resident nothing on protected days.
- S1–S4: decided, not routed (unchanged).
- Regression: the diff of all 56 documents is limited to the five new sentences and the two rewritten examples. The sentence-location re-run and the mirror / scored-value sweep are clean.
- The held-night tiers remain conditional on the unpublished bedhold corpus.

KB VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=none

## revision_4 (2026-10-23, cross-product re-judge — all seven products published)

Snapshot: all gates OK; DOCS OK; TRACEABILITY OK (0 non-unlock misses). The medicare corpus `77516c68…`, source `ddc0242f…` and tools `91fc2fae…` are unchanged since revision_3.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| task0 | PASS | PASS | PASS |
| task1 | PASS | PASS | PASS |

1. Conditional items settled. The held-night tiers of both tasks (task0: 12-06..07; task1: 12-03..04, of which 12-04 falls in the lapse) rest on bedhold rows that the published Bed-Hold and Leave Reservations corpus produces exactly. No scored figure moves.
2. Seeded rows of other products read by these tasks: 8 rows in task0 and 11 in task1, all bedhold (reservations, notices, elections, held-days entries, charges). Each was checked against the bedhold documents and the private daily-rate schedule (Semi-Private Long-Term Care Room, 384.00 from 1 July 2025). Every row is OK. The per-row list is in the runtime_context revision_4 sections. Neither resident holds any private, medicaid, trust, ancillary or therapy record.
3. Owed-at-once writes in the published corpora that a solver could make mid-conversation and that would move a scored read: none.
- Earlier items: E1 closed (round 3), S5 closed (round 4), S1–S4 decided.

KB VERDICT revision_4: task0=PASS task1=PASS kb=CLEAN src=none
