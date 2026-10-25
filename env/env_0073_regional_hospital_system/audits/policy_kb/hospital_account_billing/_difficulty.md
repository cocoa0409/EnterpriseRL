# KB doc-policy audit — hospital_account_billing (product encounter)

## revision_1 (2026-10-21)

Entry conditions (Step 0): policy-side verdict `VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN`; coordinator gate snapshot 05:55:14 (DOCS OK, TRACEABILITY OK 0 misses, EXTENDED/TASK TOOL CONTRACT/REPLAY --check/SOLVABILITY/COMPUTE/GROUNDING/SCOPE OK); runtime view + DB access path supplied. All present.

| Task | Runtime blind audit | Two-way scan | Dependency form |
|---|---|---|---|
| 0 | PASS (blind 340.67 / 898.64 = GT; tree identical, hop state-derived) | PASS | PASS |
| 1 | PASS (blind 6881.20 / 487.00 / 71.84 / 1591.74 = GT; tree identical, 3 hops state-derived) | PASS | PASS |

Contamination: none (blind files frozen before any source read; sha256 0.md 857d886ad819..., 1.md b0ec5200c5ab...).

Closing checklist:
- One audit file per task in runtime_context/ and policy_kb/; no older revision.
- Every atom of the six extended policies (rules, overwrites, baselines, 31 factor ladders, 4 prerequisite edges, 6 tool contracts) and of the governed base policies is carried; retired surfaces written as retired; no addition.
- Every prerequisite sentence verbatim, state form, in its blocked policy's doc only; no other problem's tool, route or chain anywhere.
- Unlock schemas and worked examples / FAQ figures: no value equals a scored value or intermediate of either task.
- Final-form gate re-run (kb_snapshot 2026-10-21T06:06:21): DOCS OK; TRACEABILITY OK (0 misses); EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK; sha256 f701977c54dd d4522c0bfe57 eb9a8a4effe8 f5bba00cb82e unchanged.

Source-side items (reported, not KB defects; the KB carries each sentence verbatim as required):
- **src-1** encounter_ext_insured_payoff prerequisite (renderer-flagged): the policy_source "... fixed only after an uninsured discount stands against one of the account's non-covered-service liability postings, on a patient class that grants that discount." is limited by class only, while the edge condition also requires the account to carry a NONCOVERED_SERVICE posting. Literal visible reading: an insured account of a granting class with no non-covered posting can never have its insured payoff fixed. Untriggered by tasks 0/1. Detail in policy_kb/hospital_account_billing/0.md.
- **src-2** encounter_ext_service_recovery_courtesy prerequisites: both "The courtesy is not fixed until ..." sentences omit limits their conditions carry (SELF_PAY; carries COVERAGE_TERMINATED postings), and the same rule also governs the discretionary courtesy "on every other account", which a literal reader would then hold never fixed. Untriggered by task 1. Detail in policy_kb/hospital_account_billing/1.md.

Cross-product (conditional, to re-judge once estimate, assist and claim are published): the 15 percent variance review percent and Insured Patient Out-of-Pocket Estimate vocabulary (Good Faith & Price Estimates); the hardship tier name, determination and income reading (Financial Assistance Program (Charity Care)); PR-27 release counting (Insurance Claim (Third-Party Billing)).

VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=src-1,src-2

## revision_2 (2026-10-21, re-audit round 2)
Gates: RENDER round 3: DOCS OK 65 docs; policy VERDICT revision_6 PASS/PASS/CLEAN; kb_snapshot 19:33:44: DOCS OK; TRACEABILITY OK (0 misses); EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; sha256 825cea73c913 d4522c0bfe57 14488954015e af3ac0804b44.
- src-1 closed: insured-payoff sentence now scoped to accounts carrying a non-covered-service posting on a granting class; verbatim in insured_account_payoff_in_full only.
- src-2 closed: both courtesy sentences now scoped (self-pay + CT postings; self-pay + ended stay + final bill + 0762 + no package); verbatim in owed_service_recovery_courtesy_posting only. Self-pay payoff sentence also tightened, verbatim in self_pay_account_payoff_in_full only.
- No regression: source and KB deltas are exactly these four sentences; conditions, ladders, params, base and all other doc text unchanged; DB returns identical; runtime re-derivation reproduces gold (340.67 / 898.64; 6881.20 / 487.00 / 71.84 / 1591.74).
- Contamination: same auditor as revision_1 (source in context); disclosed in runtime_context revision_2.
- Cross-product (claim, assist, estimate) still conditional.
VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=NONE

## revision_3 (2026-10-22, cross-product re-judge; all 7 products published)
kb_snapshot 2026-10-22T00:33:49: DOCS OK; TRACEABILITY OK (0 misses); EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; sha256 825cea73c913 d4522c0bfe57 14488954015e af3ac0804b44 (unchanged since revision_2). Encounter corpus unchanged.
- Round-2: no open items; src-1/src-2 remain closed; nothing regressed; gold reproduced.
- Conditional figures now final and confirmed against published docs: estimate 15 percent / once per scheduled service; hardship tier name, "income above limit"/"assets above limit", determination statuses and recorded income; PR-27 releases counted line by line. No cross-product KB contradiction (kb CLEAN).
- Exhaustive other-category seed pass (task 0: 2 claims + 11 claim txns, 1 assist case + 5 txns, 1 estimate + 1 line; task 1: 3 claims + 8 claim txns, 1 assist case + 5 txns; plans, appointments, records, handoffs: none seeded in either world; 835s all balance):
  - **src-3** (assist, task 0, moves scored values if re-seeded): case fc43a6e1 meets both §4.6 denial clauses (no qualifying debt; liquid assets 31500.00 > 25000.00); published rules do not uniquely yield INCOME_ABOVE_LIMIT; as ASSETS_ABOVE_LIMIT the values would be 361.57 / 881.45.
  - **src-4** (estimate, task 0, PLAUSIBLE, moves the payoff if re-seeded): same-encounter CT 75571 (418.00) absent from estimate b9a956ef (no line, no day-of-service version 2, no second estimate); with a v2 totalling 1414.00 the variance credit is 0.00 and the payoff 923.94.
  - **src-5** (claim, task 0, moves nothing): claim 0d58098f keeps frequency code '1' after a filed MEMBER_ID_CORRECTED correction with no front-end rejection recorded ("A replacement claim carries claim frequency code 7").
VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=src-3,src-4,src-5

## revision_4 (2026-10-22, seed-rework confirm)
Gate: policy VERDICT revision_7 PASS/PASS/CLEAN. kb_snapshot 01:11:47: DOCS OK; TRACEABILITY OK (0 misses); all gates OK; sha256 825cea73c913 d4522c0bfe57 01c03088b711 af3ac0804b44 (charter/tools unchanged; encounter corpus unchanged).
- src-3 closed (assets 18750.00 under limit; "income above limit" unique). src-4 closed (day-of-service v2 with 75571 line, total 1026.00). src-5 closed (front-end rejection INVALID_MEMBER_ID recorded; resubmission keeps code 1).
- Task 0 re-derived through db_query (not blind): 340.67 / 915.89 = new gold. Task 1 untouched.
- No new defect; nothing regressed.
VERDICT revision_4: task0=PASS task1=PASS kb=CLEAN src=NONE
