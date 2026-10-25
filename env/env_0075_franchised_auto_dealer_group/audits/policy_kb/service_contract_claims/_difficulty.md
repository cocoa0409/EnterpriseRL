# KB-doc policy audit — closing checklist — service_contract_claims (product vsc)

## revision_1 (2026-10-22)

### Entry conditions (cited, not re-run by the auditor)
- Policy-side verdict: `VERDICT revision_10: task0=PASS task1=PASS charter=CLEAN`.
- kb_snapshot.sh service_contract_claims vsc (2026-10-22T12:20:09): `check_docs.py vsc => DOCS OK`; `check_traceability.py service_contract_claims => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)` (coordinator-run, post-publication); `check_extended.py => EXTENDED OK`; `check_task_tools.py => TASK TOOL CONTRACT OK`; `replay_tasks.py --check => REPLAY OK`; `check_solvability.py => SOLVABILITY OK`; `check_compute.py => COMPUTE OK`; `check_grounding.py => GROUNDING OK`; `check_cross_fire.py => SCOPE OK`; 62 docs in docs/vsc; runtime views 0.runtime.json f8fcd84d83df1a3c, 1.runtime.json 676e810ec7b7573a.
- All products published (purchase, service, maintenance, vsc, gap, warranty, loaner) — no CONDITIONAL figure; every other-product seeded row the two tasks read was re-priced against its published docs in one pass.
- DB access: tool-shaped (db_query.py share finders + unlock_* schemas); blind on the DB side for both tasks. No contamination: no source/GT/meta/initial_state/worklog/plan read before the freezes; unlock schemas and doc examples carry no scored figure.
- Final form: the auditor edited no document; the corpus audited is the one the snapshot's DOCS OK / TRACEABILITY OK lines were taken on.

### Freeze record
| task | runtime_context file | blind freeze hash (sha256/16 of text up to the FREEZE marker) | reveal |
|---|---|---|---|
| 0 | runtime_context/service_contract_claims/0.md | 893c52484fcbec80 | 2026-10-22T12:28 |
| 1 | runtime_context/service_contract_claims/1.md | 2e64b6dad0baf4e5 | 2026-10-22T12:28 |

### Part verdicts
| task | runtime blind audit | full-domain two-way scan | dependency-form scan |
|---|---|---|---|
| 0 | PASS (all 3 writes and every argument equal to GT: 1667.15; 1 day / 45.00; 3780.75) | PASS | PASS |
| 1 | PASS (all 3 writes equal to GT: 1080.91; 6783.37; 2035.27) | PASS | PASS |

### Difficulty checklist
- Every normative atom of the six extended policies (rules, baselines, 31 factor ladders tier by tier, overwrites and their retired surfaces) and of the base policies they govern is entailed by docs/vsc; nothing unborne, nothing changed in meaning, no claim from outside the source.
- Every prerequisite sentence (5 edges: kept→waiting, kept→rental, rental→waiting [state], traded→maintenance, traded→coverage) stands verbatim, in its declared form, only in the blocked policy's hub; every hop resolvable from it, the depended-on desk and the records.
- Every computation document gives a definite fall-back different from GT (task 0: 1797.80 / 350.00 / 3714.88; task 1: 1193.10 / 6858.40 / 1932.19); every factor findable from the records' own words; no computation document hints at a variation beyond the source's own assembly text (O-1).
- No other problem's tool name, route, aggregated chain, task-mirroring title or opening world state anywhere.

### KB defects (renderer)
None.

### Source-side items (instantiator) — all members of each class
- Seed realism, cross-product rows read by a scored factor: **SRC-1** (task 0) — RO 446215 customer-pay work and the 149.00 diagnostic credit with no authorized repair decision on record; the waiting re-decision's diagnostic-fee tier (scored 1667.15) rests on that credit row.
- Seed realism, cross-product row read (date/odometer only): **SRC-2** (task 1) — Kessler Care Plus 6-Visit sold-or-traded refund calculation recorded at 0.00 where the published maintenance rules give 35.95.
- Seed completeness, unread purchase rows: **SRC-3** (tasks 0 and 1) — closed deals with no contract-date postings (feeds SRC-2's fee tier).
- Observation, no action required: O-1 — overwrite replaced_by texts name factor-decided quantities that the computation documents carry as assembly.

KB-VERDICT revision_1: task0=PASS task1=PASS kb=CLEAN src=SRC-1,SRC-2,SRC-3

## revision_2 (2026-10-22T15:10, seed-only re-audit)
- Entry: kb_snapshot.sh service_contract_claims vsc (2026-10-22T15:05:13): `check_docs.py vsc => DOCS OK`; `check_traceability.py service_contract_claims => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)`; EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK; 62 docs; hashes 3cfdcd5e20ef 3fa9c534c04c 6a79576e5071 163899285f35 (first two unchanged); runtime views f8fcd84d83df1a3c / 676e810ec7b7573a unchanged. Policy-side verdict revision_11 CLEAN (per coordinator).
- Scope: rows changed by the seed-only fix and their same-class neighbours, re-queried tool-shaped; no new exhaustive search.
- SRC-1 closed (RO 446215 A/B authorizations on record; 149.00 credit producible). SRC-2 closed (plan refund calculation 85.95 = published-rule value; refund payment row consistent). SRC-3 closed (all three closed deals carry contract-date postings, deposits and payments balancing to 0.00).
- Task verdicts re-derived: task 0 1667.15 / 1 day 45.00 / 3780.75 and task 1 1080.91 / 6783.37 / 2035.27 unchanged and equal to GT; runtime, bijection and dependency-form parts PASS for both; no KB defect; no regression.

KB-VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=NONE
