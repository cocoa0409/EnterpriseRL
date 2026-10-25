# KB-layer audit — worker_payroll_card_servicing (product card)

## revision_1 (2026-10-23)

Inputs:
- coordinator brief /tmp/erl0077_coord/kbaudit.md;
- policy verdict `VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN`;
- claimed scope: the blueprint claim for this difficulty, product card, M=2.

Every product (program, paycard, disburse, access, card, save, loan) is published, so nothing is graded CONDITIONAL.

Entry and closing snapshot (`/tmp/erl0077_coord/kb_snapshot.sh worker_payroll_card_servicing card`, run at 10:45 and again at close):
- `check_docs.py card => DOCS OK`
- `check_traceability.py worker_payroll_card_servicing => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)`
- EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK
- docs: 59 files in docs/card; source sha256 51b0fc5d0b40 b598d810b808 ad5541ae0172 84665948a43f
- runtime views 0: a40dcf36588d7b05, 1: fee91c57553ce253

## Per-task verdicts

| task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | blind = GT |
|---|---|---|---|---|
| 0 (Premier) | PASS | PASS | PASS | 228.62 / 415.51 / 90.70, tree final credit → reversal → signing, both hops state-derived |
| 1 (Advantage) | PASS | PASS | PASS | 171.36 / 427.21 / 191.95, same tree shape, both hops state-derived |

Files: runtime_context/worker_payroll_card_servicing/{0,1}.md (blind_answer frozen before reveal, then gt_comparison) and policy_kb/worker_payroll_card_servicing/{0,1}.md.

## KB defects (renderer)

None.

## Source-side items (instantiator) — every member listed

- **SRC-1 — ladder vs rule/compute on the early-pay cost cap.**
  - The lost-card tier of all four early-pay-cost factor ladders reads "the lesser of that fee and nbd_fee_bank_usd of the transfer's Access tier": vr_early_pay_cost, zc_early_pay_cost, wr_early_pay_cost and yc_early_pay_cost.
  - The rule reads "the tier the worker's Access plan holds on the day the credit is figured, as the plan record shows it", and compute reads `CPARAM('access','nbd_fee_bank_usd', access_plan_id=…)`, the plan's current tier.
  - The tier moved between transfer and today in both worlds, so the ladder reading moves scored values:
    - task 0 reversal: 415.01 instead of 415.51 (Standard 1.99 vs Preferred 1.49);
    - task 1 final credit: 171.86 instead of 171.36 (Plus 1.49 vs Premier 0.99).
  - The KB renders the rule wording.
- **SRC-2 — ambiguous liability wording in the two signed-claim baselines and rules** (card_ext_signed_loss_claim_credit, card_ext_advantage_signed_claim_credit).
  - The sentence "the lesser of the disputed amount and the liability limit less the liability already charged on the same loss, never below zero" admits two readings: min(disputed, max(0, limit − charged)), which compute uses, and max(0, min(disputed, limit) − charged).
  - The second reading gives 107.20 (task 0) and 208.95 (task 1) instead of 90.70 and 191.95.
  - The KB carries the source wording; the P/E doc's "that difference" leans to the compute reading.
  - Low severity, but it moves the scored number.

## Residue (accepted under the coordinator's replay-closure ruling; not graded)

Both Access plans carry no period close lines: 66 and 112 rows, all access_earnings_sync. The Access docs book a period close each payday, and their tier allowances rest on those lines. No gold step reads them. The seeded Access fee rows and current tiers were re-priced under the published Access tariff and fee rules and are consistent.

## Coverage note

Full sentence-level scan covers the six extended policies, their overwrites, and the base policies they overwrite or read: error resolution, unauthorized liability, fee refunds, ATM/foreign fees, service fees, service orders. The variant table was compared value by value. card_lifecycle, card_evt_loads, card_evt_debits, card_agg_multi_holding and card_access_activity_interplay were spot-checked only; this difficulty's trees read none of them.

KB-VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=SRC-1,SRC-2

## revision_2 (2026-10-23, re-audit round 2)

Inputs:
- RENDER.log tail `RENDER round 3: DOCS OK`;
- policy verdict `VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN`;
- worklog `REWORK round 9: gates 7/7 green`.

Re-run snapshot:
- `check_docs.py card => DOCS OK`
- `check_traceability.py worker_payroll_card_servicing => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)`
- EXTENDED, TASK TOOL CONTRACT, REPLAY (230/230, 275/275), SOLVABILITY, COMPUTE, GROUNDING, SCOPE all OK
- source sha256 39637c978d99 b598d810b808 4a164a3478a6 4f810206507c; runtime views unchanged; docs: 59 files

Closures:
- **SRC-1 closed in source.** All four early-pay-cost ladders now read the tier held on the day the credit is figured. The stale phrase has 0 occurrences in source, tools and docs; the KB was already aligned.
- **SRC-2 closed in source and docs.** The single-reading liability sentence is in both signed-claim rules and baselines, and verbatim in both signed-claim computation documents. The old phrasing has 0 occurrences; the worked examples are correct.

Regression: the corpus content diff is 3 lines, all in those two documents. Prerequisite sentences, tool placement and titles are unchanged. GT is unchanged, and no scored or alternative value leaks.

Disclosure: the round-2 runtime check is a re-derivation on the changed surface by an auditor who had already seen the source. It is not blind; the revision_1 blind answers stand untouched.

| task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=NONE
