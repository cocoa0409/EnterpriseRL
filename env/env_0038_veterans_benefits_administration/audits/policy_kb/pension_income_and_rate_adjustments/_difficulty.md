# erl-kb-doc-policy-audit — pension_income_and_rate_adjustments (product pension), round 1

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
|---|---|---|---|
| 0 | KB-RUNTIME RED (time anchor of the benefit income statement's ageing factors; policy-side prose-vs-compute origin) | PASS | PASS |
| 1 | PASS | PASS | PASS |

Closing checklist (Step 5): **not closed** — task 0 runtime part is RED. Audit files correspond one-to-one with tasks 0 and 1 (runtime_context/…/{0,1}.md, policy_kb/…/{0,1}.md); no earlier revision existed for this skill in this difficulty. The closing re-run of check_docs.py / check_traceability.py is deferred to the round that closes the difficulty (entry snapshot: DOCS OK; TRACEABILITY OK 0.json 19/0, 1.json 23/0).
Coverage note: only product pension's corpus was audited; base-type products claimed by no difficulty are outside this skill's scope, and cross-product contradictions are outside its detection range.

## revision_2

| Task | Runtime | Two-way scan | Dependency form |
|---|---|---|---|
| 0 | PASS (round-1 KB-RUNTIME RED closed) | PASS | PASS |
| 1 | PASS | PASS | PASS |

- Both revision_2 runtime answers are not blind (the auditor had seen round-1 source/GT and the coordinator's claim list); disclosed in each runtime file. A fresh independent blind auditor would be needed for a clean blind trial.
- Closing checklist: audit files one-to-one with tasks; round-1 text preserved, revision_2 appended; every normative atom checked carries; prerequisite sentences verbatim on blocked sides only; no tool/route/chain beyond them. Final-form gate lines on record from the coordinator's fresh snapshot: `DOCS OK`; `TRACEABILITY OK` (0.json 19/0, 1.json 23/0) — not re-run by the auditor.
- Open policy-side items (no verdict impact): N2 (`income_source='other'` shared by statement and declaration); R2-a (end of the statement's "since the pension effective date" period unstated in prose; compute runs it to the filing day).
