# KB doc-policy audit — financial_assistance_screening (product `assist`)

## revision_1 (2026-10-21)

Entry conditions (from the brief, cited): policy-side `VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN`; coordinator gate snapshot 2026-10-21T21:43:14 DOCS OK / TRACEABILITY OK (0 misses) / EXTENDED / TASK TOOL CONTRACT / REPLAY --check / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; runtime view + db_query.py access path supplied. Complete.

Fresh snapshot at close (`/tmp/erl0073_coord/kb_snapshot.sh financial_assistance_screening assist`, executed only, 2026-10-21T21:55:09):
- check_docs.py assist => DOCS OK
- check_traceability.py financial_assistance_screening => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)
- EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK
- sha256 a7a6daa29443 assist.extended.yaml; fe7e3790cf06 task_tools.py; a25ab75056a6 tasks/0.json; 13af0ec7e77c tasks/1.json (unchanged from the brief); runtime views d9f3c8107ad3c774 / 2cb2e59dc6403337.

contamination_disclosure: none. Blind answers frozen to disk (freeze lines 2026-10-21T21:49:18Z) before any source-layer read.

| Task | Runtime blind audit | Two-way scan | Dependency form | Task |
|---|---|---|---|---|
| 0 | PASS — all four write calls (17559.32 → 26839.10 → 29523.58 → cap 8514.60, 2024-08-26..2026-10-21, English) and the 3-hop tree derived blind and equal to GT | KB-BIJECTION RED (KB-1) | PASS | RED |
| 1 | PASS — renewal claim 6254.58 then notice 155 days (due 2026-04-22), Spanish, 4×REQUESTED + Medicaid NOT_REQUESTED; 1-hop tree derived blind | PASS | PASS | PASS |

KB items:
- **KB-1** (`hardship_liability_cap_schedule` items 3–4 + `medical_debt_burden_kept_share`): the KB rounds the scaled figure (income × cap percent) to the cent before the kept share is applied; the source rule and compute round only the product (`RND(income * cap_pct / 100 * debt_keep, 2)`). Divergent example: income 100,000.12, cap percent 4.5, kept share 0.85 → KB 3825.01 vs source 3825.00. Task 0's number unaffected (112,800.00 × 4.5% is exact). Whole-domain rounding-moment atom of `assist_ext_hardship_cap`.

src items: none. Source-side notes recorded in 0.md/1.md (not routed): N-1 base `hardship_qualifies` formula's threshold rounding vs the overwrite's replaced_by (silent); N-4 other-costs/own-charges computes do not encode their stated scope gates (no in-scope value effect); completeness and due-date overwrites re-enact "every other" clauses inside hardship/renewal-titled docs (placement only).

Coordinator questions: (1) each factor's place in the assembly order stated inside its own factor doc — judged a faithful carriage of the source-pinned method moment, names no other factor/doc, not a finding; (2) shared selection definitions repeated in each factor doc — consistent copies, required for stand-alone factor docs, not a finding. Cross-product: claim product unpublished — the appeal decision days (60/30) in `insurer_appeals_cost_sharing_owed` and the claim-variant words in the fixed-income/coverage docs equal the claim charter today and are conditional for re-judgement; estimate/encounter figures (400.00, 120 days, upgrade differential, elective discount 20/25) checked against their published corpora and charters.

Closing checklist: audit files one-to-one with tasks (runtime_context/…/0.md, 1.md; policy_kb/…/0.md, 1.md); every prerequisite sentence verbatim, declared form, single home in its blocked hub, each hop resolvable; every declared factor ladder (31 factors across the 6 extended policies) carried in full in its own doc and findable from record words; no other problem's tool, route or aggregated chain anywhere; one bijection defect (KB-1) open → difficulty does not yet pass.

VERDICT revision_1: task0=RED task1=PASS kb=KB-1 src=NONE

## revision_2 (2026-10-21, re-audit round 2)

Gate: RENDER.log `RENDER round 3: DOCS OK 66 docs`; policy `VERDICT revision_8: task0=PASS task1=PASS charter=CLEAN`. Snapshot 2026-10-21T22:14:15: check_docs.py assist => DOCS OK; check_traceability.py financial_assistance_screening => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0); EXTENDED / TASK TOOL CONTRACT / REPLAY (--check) / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; sha a7a6daa29443 fe7e3790cf06 a25ab75056a6 13af0ec7e77c; runtime views d9f3c8107ad3c774 / 2cb2e59dc6403337.
- KB-1 closed: the cap computation doc rounds only the product, the kept-share doc rounds once on the product, and every other doc restating cap order or rounding is consistent.
- Regression: only those two docs changed; nothing else changed in substance; no new KB defect.
- Runtime re-derivation (not blind): both tasks still equal to GT.
- Claim product still unpublished: appeal decision days 60/30 and claim-variant words remain conditional.
- src-1 (from the coordinator's package-price note, judged): the assist rule's "package price" is computed as the estimate total, while the estimate charter defines the package price as the Riverbend all-inclusive price (facility + professional). For an Outpatient Surgery package carrying co-provider lines, those lines would be added in the own-charges documentation and again by the other-costs co-provider addition. KB faithful to compute; no effect on the task-0 or task-1 gold.

VERDICT revision_2: task0=PASS task1=PASS kb=CLEAN src=src-1

## revision_3 (2026-10-22, re-audit round 3)

Gate: RENDER.log `RENDER round 4: DOCS OK 66 docs`; policy `VERDICT revision_9: task0=PASS task1=PASS charter=CLEAN`. Snapshot 2026-10-22T00:18:44: check_docs.py assist => DOCS OK; check_traceability.py financial_assistance_screening => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0); EXTENDED / TASK TOOL CONTRACT / REPLAY (--check) / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK; sha b0470d6bbda6 fe7e3790cf06 a25ab75056a6 13af0ec7e77c; runtime views unchanged.
- src-1 closed: the source rule and compute both use facility + professional lines on the principal code, co-provider lines excluded. The KB carries the clause verbatim and the old "estimate's total" sentence is gone. No other source or doc change.
- Runtime re-derivation (not blind): both tasks equal GT.
- Claim-conditional figures confirmed against the published claim docs.
- Exhaustive cross-category seed pass: 244 rows (encounter 138, claim 62, plan 24, estimate 20, visit 0), member tables filed as `xcheck_r3_{encounter,claim,plan,estimate}.md`.
- New source-side items:
  - src-2 (task 0) / src-3 (task 1): owed encounter writes (coverage-terminated uninsured discounts, service-recovery courtesies, observation-rate discount) that a solver could post mid-call. Each moves the supplement or renewal claim and its downstream scored reads.
  - src-4 (task 1): estimate 6e5edc50 typed as a single-service GFE where the published types example assigns an imaging-package code (72148). It feeds the renewal claim's estimate take-off.
  - src-5 (task 0): estimate 03633924 issued past its 1-business-day furnishing period. No value effect.

VERDICT revision_3: task0=PASS task1=PASS kb=CLEAN src=src-2,src-3,src-4,src-5

## revision_4 (2026-10-22, re-audit round 4)

Gate: RENDER.log `RENDER round 5: DOCS OK 66 docs`; policy `VERDICT revision_11: task0=PASS task1=PASS charter=CLEAN`. Snapshot 2026-10-22T02:34:49:
- check_docs.py assist => DOCS OK
- check_traceability.py financial_assistance_screening => TRACEABILITY OK (misses listed: 0; non-unlock misses: 0)
- EXTENDED / TASK TOOL CONTRACT / REPLAY (--check) / SOLVABILITY / COMPUTE / GROUNDING / SCOPE OK
- sha 1e8fc606d8d2 / fe7e3790cf06 / 30cee9510668 / 4747b19b3ade

Findings:
- KB: 6 docs changed, each carrying the changed source sentence or ladder verbatim. The other 60 docs are byte-identical. No new KB defect; no new dependency-form finding.
- Seed: src-2..src-5 are closed, re-checked row by row (`xcheck_r4_*.md`). No encounter write is owed at either opening.
- Runtime (not blind) lands on the new gold:
  - T0: 16639.32 / 26839.10 / 29523.58 / 8514.60
  - T1: 6018.58 / 155
- Every fall-back still differs.

VERDICT revision_4: task0=PASS task1=PASS kb=CLEAN src=NONE
