# KB-doc policy audit — closing checklist for service_dispatch_desk

Difficulty: `service_dispatch_desk`. Claimed product: `service` (Demand Service Rate Programs),
claimed exclusively, per `blueprint/blueprint.yaml`. M = 2 tasks. Published corpus audited:
`env/env_0002_commercial_hvac_service_contractor/docs/service/` — 65 documents, sha256 of the file listing
`463fc9df9c87fadcbd367f4f09e9d0f0b9698504165d3d861c9b4da20f16d136`.

Auditor independence: this auditor did not write these documents and did not judge the policy side
of this difficulty. No document, blueprint, task or runtime file was modified; the write domain was
`audits/policy_kb/service_dispatch_desk/` and `audits/runtime_context/service_dispatch_desk/` only.

## Entry conditions (Step 0)

| Condition | Status |
|---|---|
| Policy-side verdict passed | Supplied with the brief: revision 2, task 0 PASS, task 1 PASS, at `audits/policy_task/service_dispatch_desk/`. Not read during either blind phase. |
| `check_docs.py` green on the product | Supplied with the brief; re-run at close-out (below) and unchanged. |
| `check_traceability.py` green on the difficulty | Supplied with the brief; re-run at close-out (below) and unchanged. |
| Runtime-visible view and DB access path supplied | Yes — a runtime helper exposing `info`, `tools agent`, `tools user` and `steps` against a seeded engine. DB access was genuinely tool-shaped for both tasks; neither blind audit read `initial_state`. |
| Gate snapshot with actual output lines | Supplied. |

No input was missing.

## Part verdicts

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
|---|---|---|---|
| 0 | **KB-RUNTIME PASS** | **KB-BIJECTION PASS** | **KB-EXPLICIT PASS** |
| 1 | **KB-RUNTIME PASS** | **KB-BIJECTION PASS** | **KB-EXPLICIT PASS** |

Files: `audits/runtime_context/service_dispatch_desk/{0,1}.md` (blind_answer + gt_comparison) and
`audits/policy_kb/service_dispatch_desk/{0,1}.md` (source_to_kb, kb_to_source, bijection_verdict,
dependency_form). Each task was audited and written to disk separately; both blind answers were
frozen before any source-layer file was opened, and neither was modified afterwards. Both
`contamination_disclosure` sections record: none.

## Closing checklist

- **Audit files correspond one-to-one with the tasks.** Two tasks, two runtime_context files, two
  policy_kb files. This is revision 1 for this difficulty; no earlier revision existed on disk, so
  nothing was overwritten.
- **Every comparison section carries a PASS.** Both `gt_comparison` sections and both
  `bijection_verdict` / `dependency_form` sections.
- **Every normative atom of the structured source is entailed by the product's docs.** The fourteen
  base policies and their sixteen eligibility conditions, all six extended policies' baselines and
  all thirty declared factors' ladders, the `parameter_schema` definitions and the six task-tool
  contracts have prose homes. Nothing is unborne, nothing is borne with changed meaning, and no
  claim from outside the source appears — a targeted sweep for added confirmations, reviews,
  notifications, fallback procedures and ordering steps returns nothing.
- **The retired surface is one-to-one.** Eight distinct superseded clauses are declared across the
  eleven `overwrite` entries; eight stand in the corpus written as no longer in force; none is
  stated as a rule in force; none has vanished; the corpus retires nothing the source did not
  declare retired; the same policies' unnamed clauses remain carried as clauses in force. One
  replacement clause carries at the level of entailment rather than by a matching sentence, and the
  reasoning is recorded in `policy_kb/.../0.md` section C.
- **Every prerequisite's sentence stands verbatim, in its declared form, on the blocked side and
  nowhere else.** Five edges, all `form: state`: three in *Payment Clearing What Is Owed on a Demand
  Service Account*, one in *Crediting the Owner for a Response Commitment Not Kept*, one in *Buying a
  Block of Prepaid Technician Hours*. Each occurs exactly once in the corpus; no depended-on document
  carries the blocked side's sentence; `condition`, `resolved_by`, `effect`, `gate` and `kind` appear
  in no document.
- **Every hop is resolvable from the sentence, the depended-on documents and the records.** All five
  were derived in the blind phase, hop by hop, from state-form sentences, tool-shaped record checks
  and searches on the words the records use; every hop was marked **state-derived** and none
  **pre-solved**.
- **Every declared factor's ladder is carried in full, every tier exact, findable from the records
  its tier rests on.** Thirty factors across the six computations; every threshold stated in figures
  in its own factor document; every compound condition intact; the seven cross-difficulty factors
  name the Preventive Maintenance Agreements by their official product name and the kinds of records
  they read.
- **No other problem's tool name, route or aggregated chain is stated anywhere.** Six discoverable
  tool names occur in the corpus, each exactly once and each in the hub of the problem that owns it.
- **Both tasks' scored figures were reached blind and equal the source layer's.** Task 0: 927.00,
  107.28, 465.00, 2761.53 against fall-backs of 396.00, 205.54, 107.05, 2242.50. Task 1: 54300.00
  and 54181.02 on 480.0 hours, against fall-backs of 75000.00 and 7200.00. Every fall-back was
  computable and definite from the computation document plus the product figures it names, and
  differed from the answer — so no computation is decided by a document that leaves the reader with
  no number.

## Gates re-run on the final form

```
.venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/commercial_hvac_service_contractor service
  🔎 DOCS gate  product=service profile=extended docs=65 roles={'policy': 14, 'factor': 30, 'baseline': 6, 'facet': 9, 'hub': 6} content[min/mean/max]=870/1895/2953
     required quantitative keys=119  task_tools=6  prerequisite edges=5
    [PASS] mechanical gates: structure, zero implementation leaks, tool fidelity, no workflow docs, non-directory hubs, private compute-binding coverage, quantitative coverage, every prerequisite sentence carried verbatim on its blocked side, no tool-name pointers or route scaffolding
    [MANUAL REQUIRED] normative claims <-> structured source semantic bijection; every hop resolvable at the source's strength from the prerequisite sentence, the depended-on docs and the records, no state-form sentence restated as an action, and no route stated beyond the sentences
  DOCS OK

.venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py env/env_0002_commercial_hvac_service_contractor/tasks/service_dispatch_desk
  🔎 TRACEABILITY gate  (2 tasks)
  task        copied  missing    ok
  0.json          24        0  True
  1.json          16        0  True
  TRACEABILITY OK
```

No document was changed by this audit, so the gate output is identical to the snapshot supplied with
the brief.

## Policy-side notes (recorded, not part of this skill's verdict)

Neither is a KB defect; both are recorded because they were met during the audit.

1. **Stored balance fields against computed quantities.** `service_programs` carries
   `block_hours_remaining`, `emergency_calls_remaining` and `balance_due`, whose values do not
   reconcile with the figures the policies compute from the event rows (task 0: 18.5 stored against
   1.5 prepaid hours available and 3142.50 stored against a 2242.50 open position; task 1: 24.0
   stored against nil prepaid hours standing). The policies close the boundary — every relevant
   quantity is defined from the event rows, and no rule names any of these fields as an input — and
   the documents close it the same way and no further, so the translation is faithful and the
   solution unique. The user simulators also disclaim the stored figures in character. The note is
   only that a solver who reads the holding record rather than the rule has a plausible-looking
   wrong number available to it.
2. **Coverage boundary of this skill.** Only the `service` product is audited here. The
   `maintenance` corpus was read as a rollout could, to resolve the cross-difficulty factor tiers
   (repair-labor coverage, agreement labor rate, trip charge and waiver, annual price), and it was
   consistent with what the service-side factor documents say they read. It was not itself audited,
   and cross-product contradictions remain outside this skill's detection range.

## Conclusion

Runtime blind audit PASS + full-domain two-way scan PASS + dependency-form scan PASS, for both
tasks. **The service_dispatch_desk rendering passes the KB-doc policy audit.**
