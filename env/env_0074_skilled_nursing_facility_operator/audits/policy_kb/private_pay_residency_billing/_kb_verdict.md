# KB verdict — private_pay_residency_billing (product private)

## revision_1 (2026-10-23)

Inputs: policy-side `VERDICT revision_10: task0=PASS task1=PASS charter=CLEAN`; gate snapshot re-run 2026-10-23 via /tmp/erl0074_coord/kb_snapshot.sh: TASK TOOL CONTRACT OK / REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK / DOCS OK / TRACEABILITY OK (0 misses). Runtime views 9fa41b9a…0839, 3f8c13fd…2568. Blind answers frozen before reveal (0.md 88f5c670…e5cb, 1.md f0ca950b…36dc); no contamination; DB side blind (db_query.py only).

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Blind = GT |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | 210.00 / 9440.00 / 9156.00 / 1401.00, fall-backs 0 / 10946 / 9984 / 71 — all equal |
| 1 | PASS | PASS | PASS | 13088.00 / 6368.00 / 1012.67, fall-backs 8064 / 8841 / 256 — all equal |

Problem trees derived blind, every hop state-derived: task 0 late-notice credit → room-change credit → new-room span → additional deposit (customer); task 1 payer-conversion credit → re-charge span → resumption deposit (customer). Each prerequisite sentence verbatim once, on its blocked side; no route, chain, foreign tool name or task-mirroring title. Every factor ladder complete in its own document, findable from record words, naming its result and no other factor; no computation document hints at a variation.

## KB findings (non-blocking; solutions unaffected)
- K1 — docs/private/resumption_deposit_recurring_services_99ce817c.json, worked case "An oxygen concentrator first charged last month next to a longer-running cable service, … totalling 150.00: 150.00": it mirrors task 1's world (a newly started oxygen concentrator beside a longer-running service, which puts task 1 on the rule-2 tier). Under the published ancillary rules it can't occur: cable 42.00 plus a 108.00 first oxygen month would need 185.00×d/D = 108.00, and no whole d works for D = 28–31. 150.00 also equals task 0's scored insurer daily benefit.
- K2 — docs/private/additional_deposit_recurring_services_c5b3cd71.json worked cases use the real ancillary prices. "Cable and telephone … 213.00 …: 71.00" mirrors task 0's services, and 71.00 is task 0's fall-back deposit. "Telephone started only last month … 68.00" can only occur in a 29-day February. Separately, resumption_deposit_recurring_services_99ce817c "… 87.00 …: 29.00" equals task 0's scored recurring allowance.

## Source-side findings
- S1 (cross-product seed, bedhold) — task 0's seeded bed-hold charge 8b7280d7… (reservation 56a357f3…, entry 10-15..10-17) is 1308.00 (3 × 436.00). The published bedhold hospital-stay rules give 1263.00. Under hs_rate, an agreement signed 2025-07-30 whose notice was delivered 2026-08-20 moves to the current schedule only from 2026-10-19. That leaves all 3 days at the prior 421.00 rate, with no dietary credit (under 4 days), no isolation and a 100% hold percent. No private computation reads this charge, so no scored read moves; the fix is in the seed only.
- S2 (policy wording) — both deposit policies' rule 2 reads "the recurring charges of the latest service month billed (the one posted first where two share a posting date)". The parenthetical reads as a tie-break that picks a single entry. In task 1 the telephone (29.00) and oxygen (185.00) charges share posting date 2026-10-04, so a literal reading gives 29.00 and a deposit of 827.67 instead of 214.00 and 1012.67. The plural wording and the worked cases point to the sum, so the KB still entails the GT. The fix belongs in the source wording.
- S3 (policy-side, retired surface) — variant parameter room_change_rate_basis = new_tier_rate_from_move_date restates the retired private_tier_placement clause "A move the resident requests reprices from the move date" without the dearer-room exception. It is rendered faithfully in accommodation_tiers_and_placement_criteria_865b6cb4 as an unqualified in-force sentence, and it is task 0's decoy (10-06 vs 10-08). The retired-clause notice and room_change_move_date resolve it.
- S4 (policy-side) — the parameter description security_deposit_days says "Days of the tier's current daily rate", carried as "30 days of the tier's current daily rate" in security_deposit_terms_804aa703. The base rule says "in effect on the admission date", and the corpus uses "current" for the 2026 schedule. This affects only the admission deposit and the baseline schedule, not either scored path.

Other focus checks: unlock schemas match task_tools.py. No other product's owed-at-once write could move a scored read: Part A days 1–20 carry no coinsurance; bed-hold charge tools do not touch bookings; the ancillary product has no write tool. trust is not read by either task, so no figure is conditional. The private-pay terms are realistic for a Pennsylvania SNF admission agreement: 60-day rate notice with a credit for premature billing, no deposit for Medicare/Medicaid stays, refunds within 30 days, LTC-insurer assignment.

KB VERDICT revision_1: task0=PASS task1=PASS kb=K1,K2 src=S1,S2,S3,S4

## revision_2 (2026-10-23, re-audit round 2)

Readiness: RENDER.log tail `RENDER round 3: DOCS OK`. Gate re-run: REPLAY OK / SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK / DOCS OK / TRACEABILITY OK (0 misses). The revision_2 runtime check is a delta re-derivation, not blind (disclosed in runtime_context files).

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS (1401.00 re-derived) | PASS | PASS |
| 1 | PASS (1012.67, rule 2 now unambiguous) | PASS | PASS |

- K1 closed: the oxygen/cable 150.00 case was removed.
- K2 closed: the 213/71, 68.00 and 87/29 cases were removed.
- S1 closed: the bed-hold charge is 1263.00, which matches the bedhold rules.
- S2 closed: the source and KB rule 2 now read as the month's total.
- S3 and S4 are BLUEPRINT-KNOWN and not re-raised.
- All 31 rewritten examples are producible. None equals a scored value or intermediate, and none mirrors a task world.
- No regression and no new source item.

KB VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=none

## revision_3 (2026-10-23, cross-product re-judge, round 3)

Gate re-run: SOLVABILITY OK / COMPUTE OK / GROUNDING OK / SCOPE OK / DOCS OK / TRACEABILITY OK (0 misses). docs/private tree 9c9f001f80c5c268 and the extended yaml 24ea66b9… are unchanged; GT is unchanged.

- No conditional items existed, and neither task reads trust.
- Every seeded cross-product row read was checked and is OK:
  - task 0: bed-hold reservation/notice/booking/charge/election, ancillary account/recurring/item/payments/requests;
  - task 1: Part A episode/days/SNF ABN/appeals, two bed-hold reservations with their notices/bookings/elections, ancillary account/recurring/item/payments.
  - Per-row list in policy_kb/0.md and 1.md, revision_3.
- No owed-at-once write of another product moves a scored read.
- The round-1 S1 seed fix (1263.00) still holds, and the re-dated ancillary start requests match the charges.

KB VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=none
