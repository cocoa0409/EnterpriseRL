# Policy-KB audit closing checklist — small_business_electricity_care (product bizpower)

## revision_1 (2026-10-04)

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS | RED (B1: assembly of the multi-site credit, the loyalty credit and the ETF portfolio-deduction step carried by factor documents, computation documents incomplete on assembly) | PASS |
| 1 | PASS | PASS | RED (E2: "whatever else applies" in the transfer-fee computation document; E3: "often moves its gas with it" tier-tendency opening in the gas-move factor document) |

- Audit files: `audits/runtime_context/small_business_electricity_care/{0,1}.md` (blind_answer frozen with sha256, then gt_comparison), `audits/policy_kb/small_business_electricity_care/{0,1}.md` (source_to_kb, kb_to_source, bijection_verdict, dependency_form).
- Difficulty is **not closed**: three-part PASS does not hold for either task. Gate re-run on a final form is deferred to the closing round; the gate lines on record are those supplied with the brief (DOCS OK (67 docs); TRACEABILITY OK).
- Prerequisites: all four edges (three on task 0, one on task 1) carried verbatim, state form, in the blocked hub only; every hop state-derived in the blind audits; no tool name, route or aggregated chain beyond them.
- Factors: all 30 declared factors of the six extended policies carried with full ladders in their own documents, findable from the records (cross-product factors name Commercial Natural Gas Supply / Commercial and Industrial Electricity Contracts).
- Policy-side notes (do not change the verdicts): PN1 `etf_remaining_usage_basis` parameter kept while its clause is retired (visible second basis in `termination_fee_schedule_6aa2b6d3`); PN2 `baseline.rule` wording "The standard …" signals variants; PN3 task tools validate no prerequisite.
- Coverage gap stated: cross-product contradictions and unclaimed products are outside this skill's range.

## revision_2 (2026-10-04, re-audit after re-render)

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS | PASS (B1 closed) | **RED (E4, new: multi-site, loyalty and ETF computation documents now name their factors; the loyalty one lists all six with actual tier values in its example)** |
| 1 | PASS | PASS | PASS (E2, E3 closed) |

- Gate lines on record (orchestrator, after re-render): DOCS OK (67 docs, same ids); TRACEABILITY OK.
- Revision_2 runtime parts are re-derivations by an auditor who saw the source layer in revision_1 (disclosed in each runtime file); not independent blind audits.
- Difficulty **not closed**: task 0 KB-EXPLICIT RED.
- Policy-side notes: PN1, PN2, PN3, PN4 unchanged; PN5 new (source assembly sentences name every factor and are assigned to computation-document bindings, so verbatim carriage collides with the baseline's silence). None bears on correctness of the scored values.

## revision_3 (2026-10-04, re-audit after re-render)

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS | PASS | PASS (E4 closed) |
| 1 | PASS | PASS | PASS |

Closing checklist (Step 5):
- Audit files correspond one-to-one with tasks 0 and 1; revisions 1–3 preserved; every revision_3 comparison section carries PASS.
- Every normative atom of the difficulty's source is entailed by the bizpower docs; four prerequisite sentences verbatim, state form, in the blocked hubs only, every hop state-derived; 30 declared factors' ladders complete in their own documents and findable from the records; no tool name, route or aggregated chain beyond the sentences; computation documents silent about factors and yielding definite fall-backs (9.26, 10.00, 348.73, 100.00, 9.05, 50.00).
- Gates re-run by this auditor on the final form (2026-10-04): `.venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/env_0029_retail_energy_supplier bizpower` → "[PASS] mechanical gates: …" / "[MANUAL REQUIRED] normative claims <-> structured source semantic bijection; …" / "DOCS OK"; `.venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py env/env_0029_retail_energy_supplier/tasks/small_business_electricity_care` → "TRACEABILITY OK".
- Caveats on record: revisions 2–3 runtime parts are re-derivations by an auditor who saw the source in revision_1 (not independent blind audits); revision_3 verified unchanged documents by targeted checks plus full reads of the task-relevant ones, not a line-by-line re-read of all 67.
- Policy-side notes open (none bears on the correctness of the scored values): PN1 (`etf_remaining_usage_basis` still rendered as an annual-kWh basis in `termination_fee_schedule_6aa2b6d3`, a visible second basis that contradicts the computation document; scored value unaffected), PN2, PN3, PN4, PN5.
- Difficulty rendering: **passes the audit (all three parts PASS for both tasks)**, subject to the caveats above. Coverage gap: cross-product contradictions and unclaimed products are outside this skill's range.
