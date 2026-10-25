# KB verdict — medicaid_pending_and_patient_pay / product medicaid

## revision_1 (2026-10-23)

Inputs: policy-side `VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN`; gates re-run 2026-10-23T05:08 via /tmp/erl0074_coord/kb_snapshot.sh — EXTENDED OK / TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK / DOCS OK / TRACEABILITY OK (0 misses); docs/medicaid 51 files, tree sha256 7faf9577…; runtime views 8b3ba4ff…6298 / 0087757f…ea40.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS (blind 2245.90 / 334.96 / 231.64 = GT) | PASS | PASS (KB-2 note) |
| 1 | PASS (blind 1073.70 / 177.38 = GT) | PASS | RED KB-1 |

Corpus findings:
- KB-1 (RED, task 1): `pending_month_days_outside_the_stay_ea94a112` hypothetical "a 31-day month with a skilled admission on day 6 (days 1 to 5 taken out)" mirrors task 1's October evidence and tier result.
- KB-2 (note, task 0): `actual_month_days_after_part_a_f3b67a6c` hypothetical hospice election on day 25 stopping the span at day 24 — same election/stop days as task 0's October (other inputs differ).
- KB-3 (realism): impossible worked inputs — `pending_month_cost_of_care_calculation_0565b7b1` "24 days booked in benefit days 1 through 20"; `estimate_reconciliation_calculation_e8c8c0ae` "Part A days covered in full 26" in a 31-day month.
- KB-4 (wording): `hospice_room_board_and_collection_terms_d3f51913` illustration rounds the per-day hospice share to the cent (source rounds the share-day total); per-day reading moves task 0 by one cent.

Source-side (not this skill's verdict):
- SRC-1: rule assembly sentences ("figures entering the funds … a figure entering the advance itself …", "figures entering the estimate … the advance …", "neither the standard pricing nor a schedule takes out") presuppose non-baseline figures; their computation-document home signals variations.
- SRC-2: approved baseline carries "An allowance the case does not record counts as zero", used only by approved_amount_kept.
- SRC-3: pending refund overwrite caps the applied credit at "the figure that month will carry"; pending_balance_carried_in caps it at "the base estimate figure".
- SRC-4: parameter meanings cost_of_care_cap / partial_month_basis / refund_days restate base clauses the overwrites qualify; their parameter docs state them unqualified.
- SRC-5: approved_amount_kept rests on trust tier setting medicaid_pna_retained (trust unpublished) — task 0's 45.00 kept back is conditional.

Cross-product owed writes: no published medicare/bedhold tool can move a scored read of either task; trust writes conditional. Pennsylvania MA figures stated are realistic.

KB VERDICT revision_1: task0=PASS task1=RED KB-1 kb=KB-1,KB-2,KB-3,KB-4 src=SRC-1,SRC-2,SRC-3,SRC-4,SRC-5

## revision_2 (2026-10-23, re-audit round 2)

Entry: RENDER.log tail `RENDER round 3: DOCS OK`; kb_snapshot 2026-10-23T06:25:43 — all gates OK, DOCS OK, TRACEABILITY OK (0 misses); docs/medicaid tree b89c3e2b…0413; extended.yaml 07b3e890…ac67.

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS (KB-1 closed) |

- KB-1 closed (outside-the-stay example now 30-day month, admission day 14). KB-2 closed (hospice example day 21). KB-3 closed (realistic worked inputs, arithmetic re-checked, consistent with compute). KB-4 closed (kind-total rounding illustrated).
- SRC-3 closed in source (two scoped caps) and carried verbatim. SRC-1/2/4 decided notes; SRC-5 conditional on trust publication.
- No example mirrors a task world or equals a scored value; nothing regressed; no new source item.

KB VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=none

## revision_3 (2026-10-23, re-audit round 3 — cross-product re-judge, all seven products published)

Entry: kb_snapshot 2026-10-23T10:12:58 — all gates OK, DOCS OK, TRACEABILITY OK (0 misses); docs/medicaid b89c3e2b… and extended.yaml 07b3e890… unchanged since revision_2.

| Task | KB on documents (runtime / bijection / explicit) | Cross-product seed |
|---|---|---|
| 0 | PASS / PASS / PASS | RED SEED-1, SEED-2 (gold-moving) |
| 1 | PASS / PASS / PASS | RED SEED-1, SEED-2 (gold-moving) |

- Settled: SRC-5 closed (trust `payee_and_guardian_terms_0116ca7c`: Medicaid Representative Payee keeps the personal needs allowance → 45.00 kept back confirmed).
- SEED-1 (gold-moving, both): one continuous Part A episode across a three-midnight hospital absence (task 0 09-26→09-29, task 1 10-26→10-29); published Medicare docs (3-day interrupted-stay window, "return by 12:00 a.m. of the third day"; "a return after that window opens a new episode") produce an ended episode and a new one — breaks the one-episode / latest-coverage scope tests of the Medicaid reviews; all scored values move.
- SEED-2 (gold-moving, both): November standing trust transfers and their mirrored Medicaid payments (task 0 11-05 1954.50; task 1 11-03 388.00) are not what the trust docs produce (posted on the charge's due day, the 10th; memo amount task 0 1999.54, task 1 1073.70) → the case balances the advances carry move (task 1 177.38 → 565.38; task 0 231.64 → 186.60 or 2186.14).
- SEED-3 (no gold move): task 0 October block benefit-day numbering 25–45 vs docs 24–44.
- SEED-4 (no gold move): task 1 coinsurance charges 22 days / 2387.00 with a same-day uncertified reversal and 217.00 adjustments, against the Medicare record test (20 days / 2170.00; reductions only for reversals posted after the charge).
- SEED-5 (no gold move): held-days booking entry dates 09-28 / 10-28 vs "posted at month end or when the leave ends".
- SEED-6 (no gold move): task 0 trust resource-limit notices absent although the Medicaid-tier balance reached the notice level (10-03, 11-03).
- SRC-6 (source, cross-charter): Medicaid "representative payee transfer day" (5th) vs trust standing-authorization transfer "on the charge's due day" (10th) for the same transfer.
- Owed cross-product writes: none can move a scored read (Medicare/bed-hold tools write charges/payments/adjustments only; the trust November transfer is due 11-10, after the frozen time, and its tool writes no Medicaid payment).
- Accepted residue (not RED): absent bed-hold election rows and trust standing-authorization request rows (no gold step reads them).

KB VERDICT revision_3: task0=RED SEED-1,SEED-2 task1=RED SEED-1,SEED-2 kb=CLEAN src=SEED-1,SEED-2,SEED-3,SEED-4,SEED-5,SEED-6,SRC-6

## revision_4 (2026-10-23, re-audit round 4)

Entry: RENDER.log `RENDER round 4: DOCS OK`; kb_snapshot 2026-10-23T10:57:39 all OK (DOCS OK, TRACEABILITY OK 0 misses); docs/medicaid b89c3e2b… unchanged; extended.yaml 3b655b1f…; seeds reworked (round 9).

| Task | Runtime / bijection / explicit | Cross-product seed | Gold (re-derived = GT) |
|---|---|---|---|
| 0 | PASS / PASS / PASS | PASS | 334.96, 2245.90, 2186.14 |
| 1 | PASS / PASS / PASS | PASS | 1073.70, 315.38 |

- SEED-1…SEED-6 closed (every seeded Medicare, bed-hold and trust row re-checked against the owning published documents: all OK). SRC-6 accepted as BLUEPRINT-KNOWN (coordinator decision). No owed cross-product write can move a scored read. No example mirrors a task world or equals a scored value; nothing regressed; no new item.

KB VERDICT revision_4: task0=PASS task1=PASS kb=CLEAN src=none
