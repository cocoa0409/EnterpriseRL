# KB-doc policy audit — contract_payments_fees_and_servicing (product `contract`, Retail Installment Contracts)

## revision kb_round1 (2026-10-20)

### Entry conditions (Step 0)
- Policy-side verdict on record: `VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN` (audits/policy_task/…/_difficulty.md, last line).
- Gate snapshot supplied by the coordinator (2026-10-20T09:55:52). Fresh re-run of `/tmp/erl0072_coord/kb_snapshot.sh contract_payments_fees_and_servicing contract` (execute-only) at 2026-10-20T10:05:01: check_docs DOCS OK; traceability TRACEABILITY OK, 0 misses; check_extended EXTENDED OK; check_task_tools TASK TOOL CONTRACT OK; replay_tasks --check REPLAY OK; check_solvability SOLVABILITY OK; check_compute COMPUTE OK; check_grounding GROUNDING OK; check_cross_fire SCOPE OK; contract.extended.yaml fe9a9094…54c0, task_tools.py 5078f93b…a8f7 (unchanged from brief). check_traceability was not run by this auditor directly.
- Runtime view hashes verified: 0.runtime.json a2ead67b…eb46, 1.runtime.json 6b557d72…ea55db. DB access via `db_query.py` (tool-shaped). Both blind audits are blind on the DB side.
- Input complete.

### Order and isolation
- Blind answers frozen to disk (runtime_context/…/0.md sha 957fc833…, 1.md sha 416885b1…) before any source read. No contamination. Doc `meta` not read. No other scenario read. Writes are limited to the two audit directories plus scratch `/tmp/kbaudit_contract_0072/`.

### Charter-wide base and variant map (shared by both tasks)
| Base policy / variant block | KB home | Judgement |
|---|---|---|
| contract_agg_multi_holding (max 2 open; pointer to combined exposure — base text) | `8fc807e6` | equivalent; pointer is base law |
| contract_agg_combined_exposure + second-contract per-tier figures | `2a482b6b`, `d38816f4` | equivalent; figures match variants |
| contract_booking_terms + rate/term/amount/LTV/backend/neg-equity/PTI/DTI/income/mileage/age/down-payment, score bands, prior-repo/bankruptcy flags, state APR ceilings, stip deadline 30 | `6a315ae0`, `dcf725ed`, `acdddeee` | equivalent; all six tiers match |
| contract_evt_payment_application (statuses, interest basis, order, installment credit, recovery payments, fee settlement order; payoff clause retired) | `f32a0a10`, `e332ce38` | equivalent; retired surface correct |
| contract_evt_payment_channel_fees + agent fee 9.95/9.95/7.95/7.95/4.95/0.00, exempt states, card limit, certified-funds channels, restriction count | `f3de18ea`, `07a0316c` | equivalent |
| contract_evt_late_charge (status, grace, unpaid/no pyramiding, one per installment, deferred; amount clause retired) + grace 10, 5.0%, 25.00, max 1, charge-off 120 | `8467ef70`, `dd6425de` | equivalent |
| contract_evt_returned_payment (once only, reversal, no-fee reasons, late charge after return, certified-funds count; fee clause retired) + fee 25.00, monthly cap 2, reasons | `e0a1dbf8`, `b69c7201` | equivalent |
| contract_evt_fee_waiver + courtesy 0/1/1/1/2/2, max 25.00 | `52b799c3`, `b69c7201` | equivalent |
| contract_due_date_change + per-tier figures, range 1–28 | `d5e707fd`, `ad53ebdd` | equivalent |
| contract_extension (status, recovery-case bar, signed agreement, signature period, account condition, spacing, effect; deferral-limit and fee clauses retired) + per-tier extension figures | `b30f4e05`, `476d7875` | equivalent; both retired clauses marked "no longer in force" |
| contract_payoff_and_lien_release (quote statuses, retired quote clause with in-force tail, redemption, paid-off, lien, method, once) + validity 10, clearance days, release 10, ELT states | `3623d902`, `eb1128b9` | equivalent |
| contract_scra_rate_cap + 6.0%, 180 days | `4e11831b`, `8abb9a86` | equivalent |
| contract_ancillary_postings | `e3165815` | equivalent |
| contract_default_status | `a0698ac1` | equivalent |
| measures (installments paid, days past due, rolling windows) | restated in the using documents | equivalent |
No KB claim without a source, no source atom unborne, no undeclared retirement.

### Per-task part verdicts
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 (hardship extension: late charge 7.69 → sign 2 → fee 43.97) | PASS | PASS | PASS |
| 1 (payoff: returned fee 39.55 → statement 2026-11-02 / 8518.41 → payoff 8488.92) | PASS | PASS | PASS |

### KB defects
None.

### Source-side items (not KB defects)
None that the KB cannot fix. Notes only:
- S-N1 (task 1 seed): the statement-day factors sum to 10 in this world (5 − 2 + 3 + 1 + 3), equal to the default validity. So the scored `quote_good_through_date` 2026-11-02 is the same as the fall-back date. Each factor alone still moves it, and the scored figure differs from the fall-back (8518.41 vs 8493.41).
- S-N2 (form): the source rules' generic "The rules below may …" assembly sentences are carried into the computation documents. These are the accepted generic-assembly form, and they name no factor (DF-N1).

### Conditional (cross-product, unpublished products)
- Task 0: the insurance allowance (CPI tracking record `compliant`, first lapse notice 2025-05-16 outside the window) and the recovery review charge (case `recalled`, `account_brought_current`, +10.00).
- Task 1: insurance-lapse shortening (first lapse notice 2026-02-12 inside the window, −2 days) and referral-history review (recalled / account_brought_current, +1 day).
- The contract corpus carries these ladders in full and names the products and record kinds. Whether the cpi and recovery corpora, once rendered, define those statuses and reasons consistently is left to the later re-judge. No figure here depends on gap or deficiency records.

### Closing checklist
- Audit files are one-to-one with tasks: runtime_context/{0,1}.md and policy_kb/{0,1}.md, each with revision_1. Every comparison section carries PASS.
- Every normative atom of the structured source is entailed by `docs/contract/`.
- All five prerequisite sentences are verbatim, in state form, on their blocked sides only.
- All 33 declared factor ladders (4 + 6 + 6 + 6 + 6 + 5) are carried in full in their own documents and are findable from record words.
- No tool, route or aggregated chain is stated beyond the prerequisite sentences.
- Gates were re-run once on the final form (snapshot above).

VERDICT kb_round1: task0=PASS task1=PASS kb=CLEAN src=none

## revision kb_round2 (cross-product re-judge, 2026-10-21)

- **Snapshot** (`/tmp/erl0072_coord/kb_snapshot.sh contract_payments_fees_and_servicing contract`, 2026-10-20T23:18:26): every gate green (DOCS OK; TRACEABILITY OK, 0 misses; EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK). yaml fe9a9094…54c0 and task_tools 5078f93b…a8f7 are unchanged, and the contract corpus digest is unchanged (b10db89b…08d3, same command as round 1; no doc added, removed or changed).
- **Erratum:** the round-1 text says 72 contract documents; the corpus holds 70. The round-1 text is left as written.
- **All products now published:** cpi 46, recovery 47, deficiency 50, gap 59, vsc 17, dealer 10.
- **One exhaustive pass over every cross-category seeded row in both worlds** (member lists in policy_kb/…/{0,1}.md revision_2):
  - world 0: 1 CPI coverage, 6 CPI activities, 1 recovery case, 0 recovery activities;
  - world 1: 1 CPI coverage, 6 CPI activities, 1 recovery case, 0 recovery activities;
  - no gap, vsc, deficiency or dealer rows and no ancillary contract postings in either world.
  - Every row is consistent with the published cpi and recovery documents: lapse notices only on lapse-notice records, an accepted proof restores compliant, referral at ≥ 60 days past due, recall when the account is brought current, no cure notice for GA or FL, and accepted channels, deductibles and lienholder on the proofs.
- **Conditional figures settled:**
  - Task 0: insurance allowance = 2; recovery review charge = +10.00.
  - Task 1: insurance-lapse shortening = −2 days; referral-history review = +1 day.
  - Every scored value is unchanged (7.69 / 2 / 43.97; 39.55 / 2026-11-02 / 8518.41 / 8488.92).
- **No cross-product contradiction found:** no non-contract document states a rule on this difficulty's policies.
- **KB defects:** none. **Source-side items:** none (S-N1 seed note stands, not a defect).

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

VERDICT kb_round2: task0=PASS task1=PASS kb=CLEAN src=none
