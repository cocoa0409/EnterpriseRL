# KB-document audit closing checklist — controls_support_desk (product `controls`, M=2)

Auditor: fresh KB auditor, independent of the agent that rendered these documents and of the auditor who judged the policy side of this difficulty. Revision 1. Closed 2026-09-17.

## Part verdicts, per task

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan | Overall |
|---|---|---|---|---|
| 0 | **PASS** (`audits/runtime_context/controls_support_desk/0.md`) | **PASS** (`audits/policy_kb/controls_support_desk/0.md`, `bijection_verdict`) | **PASS** (same file, `dependency_form`) | **PASS** |
| 1 | **PASS** (`audits/runtime_context/controls_support_desk/1.md`) | **PASS** (`audits/policy_kb/controls_support_desk/1.md`, `bijection_verdict`) | **PASS** (same file, `dependency_form`) | **PASS** |

No `KB-RUNTIME RED`, no `KB-BIJECTION RED`, no `KB-EXPLICIT RED`. No policy-side problem was found that needed recording as a note, and no contamination occurred: both blind answers were frozen to disk before any source-layer artefact was opened.

## Closing checklist

1. **Files correspond one-to-one with the tasks.** `runtime_context/controls_support_desk/{0,1}.md` and `policy_kb/controls_support_desk/{0,1}.md`, one of each per task. This is revision 1; no older revision existed to preserve.
2. **Every comparison section carries a PASS.** `gt_comparison` PASS on both tasks; `bijection_verdict` PASS on both; `dependency_form` PASS on both.
3. **Every normative atom entailed.** All five extended policies of this difficulty (`controls_ext_support_overage_charge`, `controls_ext_arrears_settlement`, `controls_ext_reinstatement_charge`, `controls_ext_alarm_ack_credit`, `controls_ext_upgrade_authorisation`), all eleven base policies of the charter and all six variants' tier parameters are borne by `docs/controls/`, with nothing unborne, nothing borne with changed meaning and no claim from outside the source. The five `overwrite` clauses are each written as retired in a bearing document, their sibling clauses remain in force, and the KB retires nothing the source did not.
4. **Prerequisites.** All three declared `prerequisite` edges of this difficulty carry their `policy_source` sentence verbatim, in the declared `state` form, with the ordering connective and strength intact, in a document of the policy they block and in no other policy's document. Each hop is resolvable at the source's strength from that sentence, the depended-on policy's own rule and the records; each was in fact so resolved during a blind audit that had read no source material.
5. **Factors.** All twenty-nine declared factor ladders are carried in full, every tier exact — including every tier no task's world reaches — each in its own factor document, each reachable from the words the customer's records use, and none referencing another factor or a computation document. The five computation documents each yield a definite fall-back number from their own text plus the product figures they name (support overage 3581.64 / settlement definite / reinstatement 470.00 for task 0; credit 290.00 / upgrade labor 1915.20 for task 1), each different from the answer the factors produce.
6. **No route.** No tool name, policy id, dependency table, checklist, roadmap, ordered step list or cross-problem pointer appears anywhere in the corpus beyond each problem's own invocation block and the three verbatim prerequisite sentences. No title or opening mirrors a task's situation.
7. **Gates re-run on the final form** (by the auditor, read-only, from the repository root; the documents were not modified by this audit):

```
.venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/commercial_hvac_service_contractor controls
  🔎 DOCS gate  product=controls profile=extended docs=63 roles={'factor': 29, 'facet': 13, 'baseline': 5, 'hub': 5, 'policy': 11} content[min/mean/max]=1370/2120/4244
     required quantitative keys=123  task_tools=5  prerequisite edges=3
    [PASS] mechanical gates: structure, zero implementation leaks, tool fidelity, no workflow docs, non-directory hubs, private compute-binding coverage, quantitative coverage, every prerequisite sentence carried verbatim on its blocked side, no tool-name pointers or route scaffolding
    [MANUAL REQUIRED] normative claims <-> structured source semantic bijection; every hop resolvable at the source's strength from the prerequisite sentence, the depended-on docs and the records, no state-form sentence restated as an action, and no route stated beyond the sentences
  DOCS OK

.venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py env/env_0002_commercial_hvac_service_contractor/tasks/controls_support_desk
  🔎 TRACEABILITY gate  (2 tasks)
  task        copied  missing    ok
  0.json          18        0  True
  1.json          14        0  True
  TRACEABILITY OK
```

## Stated coverage gaps

- This audit is organised per difficulty and covers only the product `controls_support_desk` claims. `docs/maintenance/` and `docs/energy/` were read as a rollout may read them, and figures were taken from them where a controls factor names them by their official product name; they were never used as a criterion, and their own internal fidelity is outside this audit's scope. Cross-product contradictions are outside this skill's detection range and are only structurally suppressed, not proved absent.
- Base-type products claimed by no difficulty (`iaq`, `retrofit`, `warranty` corpora, and any distractor content) are entirely outside this audit's scope.
- The DB side of both blind audits was genuinely blind: every record was obtained by calling share finders and task tools against the seeded engine through the supplied runtime helper, and the raw `initial_state` was never read as a document.
