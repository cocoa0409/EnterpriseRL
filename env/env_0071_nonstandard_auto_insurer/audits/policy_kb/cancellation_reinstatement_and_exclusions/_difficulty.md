# KB doc-policy audit — cancellation_reinstatement_and_exclusions (product auto) — difficulty close-out

## revision_1

### Entry conditions (Step 0)
- Policy-side verdict (brief, read only that line): `VERDICT revision_11: task0=PASS task1=PASS charter=CLEAN`.
- Gate snapshot (brief) and auditor re-run of `/tmp/erl0071_coord/kb_snapshot.sh cancellation_reinstatement_and_exclusions auto` at 2026-10-21T02:45:55: `check_docs auto: DOCS OK`; EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK (rc=0); `check_traceability: TRACEABILITY OK, misses total: 0`. Source sha256: auto.extended.yaml f3c79001…efe2, task_tools.py 5a982b7f…a0f (equal to the brief). check_traceability was not run by the auditor.
- Runtime view and DB access path supplied. Every DB read went through `db_query.py` (tool-shaped). The blind audits are blind on the DB side.
- Contamination: none. The brief carried no scored value. `tasks/`, plan.md, worklog, render_source and the blueprint difficulty summary were kept out of every read and search until both blind answers had their FREEZE lines (2026-10-21T02:40:46Z).

### Per-task part verdicts
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Files |
|---|---|---|---|---|
| 0 (insured cancellation ← lapse reinstatement ← nonpayment cancellation) | PASS (all 3 writes, 13 scored args equal GT; fall-back 244.87) | PASS | PASS | runtime_context/…/0.md, policy_kb/…/0.md |
| 1 (lift ← reported-resident exclusion, ← re-listing) | PASS (all 3 writes, 19 scored args equal GT; fall-back 120.32) | PASS | PASS | runtime_context/…/1.md, policy_kb/…/1.md |

### Closing checklist
- Audit files one-to-one with tasks; revision_1 only (first KB audit of this difficulty).
- All 4 prerequisite sentences carried verbatim, state form, only in the blocked hub (mechanical scan over all 74 docs). Each hop was derived as state-derived in the blind answers.
- All 34 declared factors carried with full ladders in their own documents (15 for task 0, 17 for task 1 plus the shared base): nonpay 4, reinstatement 6, insured 5, exclusion 6, relist 5, lift 6. Each is findable from record words (KB_search probes recorded in the blind answers).
- Retired surface: 12 declared superseded clauses ↔ 12 "no longer in force" sentences, none undeclared, in-force remainders kept.
- No other problem's tool name, route, aggregated chain or task-mirroring title.
- Gate re-run lines are recorded above.

### KB defects
None.

### Notes carried for the coordinator (not KB verdicts)
- P-1 (policy-side, base law): the nonpayment cancellation / rescission condition counts "payments posted on or before the cancellation effective date" with no lower bound. The KB renders it faithfully.
- P-2 (policy-side): the replaced_by wording "under the company's state schedule" names the rw_fee_basis_rule subject in hub/base/facet documents (the computation document stays silent).
- N-1 (task 1, advisory): three computation documents define a "rating date" that their own arithmetic does not use (source general-rule sentences). Judged not RED.
- N-2/N-3/N-4 (task 0, advisory): the run-off factor docs carry the source's order clause ("any further days the company keeps"); two hypothetical illustrations coincide with task 0's tiers (9-day lapse → 5.00; SR-22 Owner-Operator → 3.00); factor examples built on reinstatement records. Judged not RED.
- X-1 (cross-product-pending, billing corpus unpublished): whether the 5.00 agent-payment fee of 2026-10-02 counts as a past-due amount under reinstatement condition (b). To be re-judged once billing docs are published.

### Source-side defects
- **S-1 (task 0, cross-product auto × fr, PLAUSIBLE).** The published FR corpus says a lapse SR-26 (after the reinstatement) or a cancellation SR-26 (between the nonpayment cancellation and the reinstatement) "is still owed … transmitted at once on the day it is found owed". The tree and GT contain no SR-26 write, and nothing visible orders that FR write against this difficulty's writes. If it lands before the hand-over, the certificate status read by certificate_runoff_on_insured_cancellation (and, between A and B, by certificate_exposure_charge_during_lapse) changes. The scored figures then move (auditor's reading: 31 days / about 224.72 instead of 27 / 193.79; fee 61.60 instead of 63.60). The most natural path is still the GT path (the customer never asks, and the auto KB leaves certificates "to their own rules"), but uniqueness depends on the solver not taking an action the FR corpus calls owed at once. This is not an auto KB defect; the owner is the auto × fr task/charter design. Details are in policy_kb/…/0.md.
- No rule-vs-compute mismatch: each blind figure equals the compute DSL result. No seed-realism defect in either task.

KB-VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=S-1

## revision_2

Gate check (2026-10-21T05:24Z), required before any re-audit work:
- `tail -1 audits/render_source/cancellation_reinstatement_and_exclusions/RENDER.log` → `RENDER round 3: DOCS OK`. The required line was `RENDER round 4: DOCS OK`.
- `/tmp/erl0071_coord/kb_snapshot.sh cancellation_reinstatement_and_exclusions auto` (2026-10-21T05:24:22) → `check_docs auto: DOCS NOT OK`. EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK (rc=0); `check_traceability: TRACEABILITY OK, misses total: 0`. Source hashes: auto.extended.yaml 6d45850b550760da4a77b2583f78619a4c5991ab6d92b9b81139a9b60d345880 (changed from revision_1's f3c79001…), task_tools.py 5a982b7f…a0f (unchanged); 74 docs.
- Policy-side line read: `VERDICT revision_12: task0=PASS task1=PASS charter=CLEAN`.

The render for the reworked source has not reached round 4, and check_docs on the current auto corpus is red. The corpus on disk is therefore not the final rendering of revision_12's source. I did not re-audit it: no blind answer, scan or S-1 closure probe was run, and the revision_1 text above is unchanged. S-1 closure, regression and the new-defect check stay open until the gate line is `RENDER round 4: DOCS OK` with check_docs green. X-1 stays cross-product-pending.

BLOCKED revision_2

## revision_2 (supersedes the BLOCKED stub above; gate now met)

### Entry conditions
- `tail -1 …/render_source/cancellation_reinstatement_and_exclusions/RENDER.log` → `RENDER round 5: DOCS OK`.
- Policy line: `VERDICT revision_13: task0=PASS task1=PASS charter=CLEAN`.
- `/tmp/erl0071_coord/kb_snapshot.sh cancellation_reinstatement_and_exclusions auto` (2026-10-21T05:40:55):
  - `check_docs auto: DOCS OK`.
  - EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK (rc=0).
  - `check_traceability: TRACEABILITY OK, misses total: 0`.
  - auto.extended.yaml 657983bf…85ae, task_tools.py 5a982b7f…a0f, 74 docs.
- DB reads via db_query only. The re-derivation is not blind (contamination disclosed in runtime_context revision_2).

### Round-1 items
| Item | Status |
|---|---|
| S-1 (src, task 0, auto × fr SR-26 ordering) | **Closed.** Certificate reads are now keyed to the standing on each transaction's effective date. db_query probes sent a cancellation SR-26 mid-chain and a lapse SR-26 before the hand-over (both tools reachable, sr26_date 2026-10-06); no scored figure moves. |
| N-1 (advisory, task 1) | Addressed. Rating dates now live in the age-class factor docs; two explanatory residual mentions remain in computation docs (advisory, not RED). |
| N-2, N-3, N-4, P-1, P-2 | Unchanged, as routed (not KB verdicts). |
| X-1 | Still cross-product-pending (billing corpus not published). |

### Regression / new-defect check
The re-rendered corpus was checked against the new source:
- 4 prerequisite sentences are verbatim and in their blocked hubs only.
- 32 factor documents have full ladders, including the changed certificate ladders and the G2 tier.
- 12/12 retired clauses.
- Tool names only in their own hubs.
- No baseline hint; certificate-standing text appears only in factor docs.
- No scored values in any document.
- The gold (unchanged in tasks/0.json and tasks/1.json) is re-derived exactly from the visible materials.

No new KB defect; nothing regressed.

Correction to revision_1's close-out text (left untouched above): the declared-factor count is 32 (4+6+5+6+5+6), not 34.

### Per-task part verdicts (revision_2)
| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=none

## revision_3 (cross-product re-judge; every product published)

- Gate: `kb_snapshot.sh` at 2026-10-21T19:18:22 gives `check_docs auto: DOCS OK`, EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK, `TRACEABILITY OK` (0 misses). Hashes 657983bf… / 5a982b7f… are confirmed unchanged. Docs tree: auto billing fr nonowner physdam rental towing. The auto corpus digest equals revision_2's, so nothing in the auto KB regressed.
- Round-2 REDs: none were open (revision_2 was PASS/CLEAN/none).
- **X-1 resolved:** the agent-assisted payment fee is not a past-due amount under the published billing law. Reinstatement condition (b) is met, and the GT is entailed.
- Exhaustive cross-product re-judge of every seeded billing, filing and physdam row in both tasks: all are states the owning rules produce, priced by their formulas (tables in policy_kb/…/0.md and 1.md revision_3).
- Mid-conversation writes owed by other products: exhaustively listed. None moves any scored figure (S-1 stays closed).
- New source-side item: **S-2** (task 0, auto × billing, PLAUSIBLE, low, no runtime path). Under billing settlement law the plan would be written off and closed at the nonpayment cancellation, since 224.79 − 215.60 = 9.19 ≤ 10.00, and a closed plan is never reactivated. That contradicts the premise "a plan reactivated by a reinstatement being closed again" behind the 15.00 charge at the insured cancellation. The records stay `current` because the tools book no billing settlement, so the figure holds at runtime.
- No new KB defect.

KB-VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=S-2

## revision_4 (seed-only rework for S-2)

- Gate: `VERDICT revision_14: task0=PASS task1=PASS charter=CLEAN`.
- `kb_snapshot.sh` at 2026-10-21T20:17:22: `check_docs auto: DOCS OK`; EXTENDED / TASK TOOL CONTRACT / REPLAY / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK (rc=0); `TRACEABILITY OK` (0 misses). Hashes 657983bf… / 5a982b7f… confirmed; auto corpus digest unchanged.
- **S-2 closed.** The 2026-09-21 agent-assisted fee raises the balance to 229.79. After the 215.60 credit the debit is 14.19 > 10.00, so the plan is final-billed, reactivated by the reinstatement, and closed again by the insured cancellation. The 15.00 charge's premise holds under docs/billing/.
- Task 0 gold re-derived on the new world: unchanged and uniquely entailed (215.60/35; 2026-10-04, 270.65/35, 63.60; 2026-10-05, 193.79/27). Task 1 untouched.
- Nothing regressed; no new KB defect. Advisory N-5 (persona wording "first called") recorded, not src.

KB-VERDICT revision_4: task0=PASS task1=PASS kb=CLEAN src=none
