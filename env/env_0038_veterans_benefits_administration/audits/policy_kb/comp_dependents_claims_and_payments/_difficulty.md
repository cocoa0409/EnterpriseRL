# erl-kb-doc-policy-audit — difficulty close-out: comp_dependents_claims_and_payments (product comp)

Date: 2026-10-06. Auditor: erl-kb-doc-policy-audit sub-agent (independent of the renderer and of the policy-side auditor).

## Entry conditions (Step 0)
- Policy-side verdict: erl-task-policy-audit PASS for tasks 0 and 1 (round 4), as supplied by the orchestrator.
- Gate snapshot supplied (`/tmp/erl0038/rt/GATES_comp.txt`): `check_docs.py … comp` → DOCS OK; `check_traceability.py …/comp_dependents_claims_and_payments` → 0.json copied 28 missing 0; 1.json copied 22 missing 0; TRACEABILITY OK.
- Runtime-visible view and DB access path supplied (`/tmp/erl0038/rt/rt.py`: schemas / persona / read-tool calls / kb_search / grep). The blind audits were blind on the DB side.

## Per-task part verdicts
| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan | Files |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | `audits/runtime_context/comp_dependents_claims_and_payments/0.md`, `audits/policy_kb/comp_dependents_claims_and_payments/0.md` |
| 1 | PASS | PASS | PASS | `audits/runtime_context/comp_dependents_claims_and_payments/1.md`, `audits/policy_kb/comp_dependents_claims_and_payments/1.md` |

## Closing checklist
- [x] Audit files one-to-one with tasks; first revision (no older revisions to preserve); blind answers frozen (sha256 recorded) before the source layer was revealed at 09:47:37Z; no contamination.
- [x] Every normative atom of the difficulty's source (base + 7 extended policies, all factor ladders, all variant figures, measures, lifecycle, account, 7 retired clauses) entailed by the comp corpus; nothing unborne, nothing re-meant, no claim from outside the source.
- [x] Every prerequisite sentence (6 edges: 3 on the opening release, 1 on the decision past-due, 2 on the restoration) verbatim, in its declared form, on its blocked side only; every hop resolvable from the sentence, the depended-on rules and the records.
- [x] Every declared factor ladder carried in full in its own document and findable from record words; cross-product factors name the other product officially (Veterans Pension / Benefit Debts and Overpayment Recovery; Decision Reviews and Appeals).
- [x] No other problem's tool name, route or aggregated chain anywhere; titles general.
- Policy-side notes recorded in the task files (not KB verdicts): replacement baseline equals a clause the same policy declares superseded; retro spans stated by the source only for the decision past-due; base "released only when the award resumes" vs closure "prerequisites commute" in task 1.

## Gate re-run on the final form (2026-10-06T09:50Z)
```
$ .venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/env_0038_veterans_benefits_administration comp
  [PASS] mechanical gates: structure, zero implementation leaks, tool fidelity, no workflow docs, non-directory hubs, private compute-binding coverage, quantitative coverage, every prerequisite sentence carried verbatim on its blocked side, no tool-name pointers or route scaffolding
  [MANUAL REQUIRED] normative claims <-> structured source semantic bijection; ... (discharged by this audit)
DOCS OK
$ .venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py env/env_0038_veterans_benefits_administration/tasks/comp_dependents_claims_and_payments
task        copied  missing    ok
0.json          28        0  True
1.json          22        0  True
TRACEABILITY OK
```

## Difficulty verdict
Runtime blind audit PASS + full-domain two-way scan PASS + dependency-form scan PASS for both tasks: the comp rendering for this difficulty passes the audit. Coverage note: cross-product contradictions and base-type products claimed by no difficulty are outside this skill's range.
