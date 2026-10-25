# KB-layer audit — worker_early_wage_access (product access), closing

## revision_1 (2026-10-23)

Entry snapshot (kb_snapshot.sh 2026-10-23T06:02:58): `check_docs.py access => DOCS OK`; `check_traceability.py worker_early_wage_access => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)`; EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE all OK; source sha256 2f274ae934f5 97579e292377 eb2ff57fbe70 4d97ff4f36ce; runtime views 1a03d9cc51e39f4c / c8b35fbd6da3a436; docs/access 57 files. Policy verdict cited: `VERDICT revision_6: task0=PASS task1=PASS charter=CLEAN`. Docs and sources unchanged during the audit (no re-run needed; the snapshot lines stand as the final-form record).

| Task | Runtime blind audit | Two-way scan | Dependency form |
|---|---|---|---|
| 0 | PASS (all scored args = gold: Preferred/2026-10-16, 144.74 seq 1, fee 1.24) | PASS | RED — K1 (bank amount + bank fee computation documents) |
| 1 | PASS (Premier/2026-10-17, 124.07 seq 2, no fee) | PASS | RED — K1 (instant computation document) |

### KB defects (renderer)
- **K1** — three computation documents render the source's conditional assembly-order sentence ("any that …") as assertions that adjustments of a named kind exist, breaking the baseline's silence:
  1. bank_transfer_amount_computation_b2d2d6e6 — "Points that add to the tier's access percentage are added first" (source: "any that adds to the tier's access_cap_percent first");
  2. bank_transfer_fee_computation_65a8df1c — "the fee charged in place of the tier's next-business-day bank fee is set next" (source: "then any that sets the fee charged in place of the tier's nbd_fee_bank_usd");
  3. instant_transfer_amount_computation_3f58aa0d — "multipliers of the lowest of the rooms then act one after another" (source: "then any that multiplies the lowest of the rooms, one after another").
  Semantics, ladders, prerequisite sentences and retired surface are otherwise faithful; no other KB defect found.

### Source-side items (instantiator)
- **S1** — access_ext_tier_review: the visible fall-back is not definite. `baseline.rule` says the plan "keeps its current tier", the overwrite's move-up clause says it "moves up one tier when … the next tier is within every allowance set out below", and the compute's fall-back (Plus in task 0) rests on factor baselines (`rv_rec_allow/rv_ten_allow/rv_wo_allow/rv_earn_allow = 1`, "only Starter") stated nowhere; read vacuously with no allowance document found, the clause gives the gold tier (Preferred) for task 0, so the four allowance factors need not bear weight on the visible surface.
- Seed realism: clean in both tasks (card rows reconcile with the frozen card charter; access ledgers consistent with the schedules). Cross-product card figures CONDITIONAL pending card publication (no dependency on card prose found).

### Notes (no verdict)
- "payroll settlement" (review due-rule, source text carried verbatim) is undefined in the corpus; both seeds carry the payroll deduction recovery for the reviewed payday, so no ambiguity arises here.
- tier_movement_terms carries base parameter descriptions (downgrade steps, review cadence) as stated in the charter although their clauses are retired — base text, coordinator-known.

KB-VERDICT revision_1: task0=RED task1=RED kb=K1 src=S1

## revision_2 (2026-10-23)
Precondition: `RENDER round 3: DOCS OK` (render_source/worker_early_wage_access/RENDER.log, last line). Snapshot re-run 2026-10-23T06:35:16: `check_docs.py access => DOCS OK`; `check_traceability.py worker_early_wage_access => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)`; EXTENDED / TASK TOOL CONTRACT / REPLAY (0.json 219/219, 1.json 578/578) / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; source sha256 f005632dfe37 97579e292377 fb1736b4b122 b5680861e5f8; runtime views unchanged (1a03d9cc51e39f4c / c8b35fbd6da3a436). Policy verdict `revision_8: task0=PASS task1=PASS charter=CLEAN`.

| Task | Runtime | Two-way scan | Dependency form |
|---|---|---|---|
| 0 | PASS (gold unchanged, = re-derivation; blind not clean, disclosed) | PASS | PASS — K1 closed (bank amount + fee order sentences now the source's conditional form) |
| 1 | PASS | PASS | PASS — K1 closed (instant order sentence) |

- K1 closed in all three computation documents; S1 closed (tier-review fall-back definite: Plus ≠ Preferred); the round-1 facet navigation note resolved. Full-corpus diff: only the S1/K1 sentences, the equivalent recovery-count rephrase, one removed facet sentence and worked-example inputs changed, all re-checked; nothing regressed, no new defect.
- Note (no verdict): the order sentences open with the source's own "Adjustments are applied in this order" — accepted assembly form, carried faithfully.
- Card docs still unpublished: card-dependent figures (card wage points, cure protection) CONDITIONAL pending the card re-judge.

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=NONE

## revision_3 (2026-10-23) — cross-product re-judge
Inputs: every product published (docs/card 59, program 55, paycard 47, disburse 59, save 16, loan 16, access 57). kb_snapshot re-run: `check_docs.py access => DOCS OK`; `check_traceability.py worker_early_wage_access => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)`; EXTENDED / TASK TOOL CONTRACT / REPLAY (219/219, 578/578) / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; source sha256 f005632dfe37 97579e292377 fb1736b4b122 b5680861e5f8 (unchanged since revision_2); runtime views unchanged. Policy verdict `revision_8: task0=PASS task1=PASS charter=CLEAN`. docs/access byte-identical to the revision_2 dump; DB returns identical.

| Task | Runtime | Two-way scan | Dependency form | Cross-product |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | card wage points confirmed (10); card, paycard, program rows re-priced, all reconcile; no owed-at-once write |
| 1 | PASS | PASS | PASS | cure protection confirmed (54.4 %, one below); card, paycard, program rows re-priced, all reconcile; no owed-at-once write |

Classes swept exhaustively in one pass: (1) CONDITIONAL figures, 2 of 2 confirmed; (2) mis-priced, missing or unreconciled other-product rows: none (2 card accounts, 95 + 187 card transactions, 2 paycard programs, 2 program agreements, 2 employer profiles checked); (3) other-product writes owed at once that could move scored reads: none. Accepted residue: unseeded paycard batch / funding rows and program schedule, remittance, notice and invoice rows (no gold step reads them; agreement receivables 0.00 consistent). No KB defect and no source-side item; nothing regressed since revision_2.

KB-VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=NONE
