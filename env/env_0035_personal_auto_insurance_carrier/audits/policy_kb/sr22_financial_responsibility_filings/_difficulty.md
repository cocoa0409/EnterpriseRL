# Difficulty closing checklist — sr22_financial_responsibility_filings (product sr22, Cardinal Financial Responsibility Filing)

| Task | Runtime blind audit | Two-way scan (KB-BIJECTION) | Dependency form (KB-EXPLICIT) |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

- Audit files correspond one-to-one with tasks/0.json and tasks/1.json: runtime_context/sr22_financial_responsibility_filings/{0,1}.md, policy_kb/sr22_financial_responsibility_filings/{0,1}.md. First revision; no older revision exists.
- Every normative atom of sr22.extended.yaml (variants, the nine base policies, the seven extended policies with every factor tier) is entailed by docs/sr22; nothing unborne, nothing changed, no claim from outside the source; seven retired clauses written as retired, none undeclared.
- Five prerequisite sentences, all state form, each verbatim in exactly one document — the hub of the policy it blocks — and in no other document of any product corpus; every hop resolvable from it, the depended-on hub's record effects and the records; no other problem's tool name, route or aggregated chain anywhere.
- Every declared factor (34) has its own document carrying the full ladder with figures; each is reachable from the words the customer's records use.
- Policy-side notes (do not change verdicts): lifecycle/sr22_withdraw customer-withdrawal path and the "release only from accepted" transition have no policy rule and no document; source assembly sentences name each adjusting line, so computation documents list them at baseline values.
- Coverage gap stated: products claimed by no difficulty (distractor corpora) are outside this audit.

Gate re-run on the final form (from the repo root, 2026-10-05):
```
$ .venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/env_0035_personal_auto_insurance_carrier sr22
🔎 DOCS gate  product=sr22 profile=extended docs=65 roles={'baseline': 7, 'factor': 34, 'policy': 9, 'facet': 8, 'hub': 7} content[min/mean/max]=698/1668/3410
   required quantitative keys=125  task_tools=7  prerequisite edges=5
  [PASS] mechanical gates: structure, zero implementation leaks, tool fidelity, no workflow docs, non-directory hubs, private compute-binding coverage, quantitative coverage, every prerequisite sentence carried verbatim on its blocked side, no tool-name pointers or route scaffolding
  [MANUAL REQUIRED] normative claims <-> structured source semantic bijection; ... (discharged by this audit)
DOCS OK
$ .venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py env/env_0035_personal_auto_insurance_carrier/tasks/sr22_financial_responsibility_filings
task        copied  missing    ok
0.json          24        0  True
1.json          25        0  True
TRACEABILITY OK
```

Difficulty rendering: **PASS** (all three parts PASS for both tasks).
