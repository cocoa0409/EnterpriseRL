# Difficulty close-out — respite_and_trial_stays (product respite)

## revision_1 (round 1, 2026-10-05)

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
|---|---|---|---|
| 0 | PASS (`runtime_context/respite_and_trial_stays/0.md`) | PASS (`policy_kb/respite_and_trial_stays/0.md`) | PASS |
| 1 | PASS (`runtime_context/respite_and_trial_stays/1.md`) | PASS (`policy_kb/respite_and_trial_stays/1.md`) | PASS |

Checklist:
- Audit files one-to-one with tasks 0 and 1; blind answers frozen before any source read (`runtime_context/respite_and_trial_stays/FREEZE.sha256.txt`: 0.md `12c6af45...fbdd`, 1.md `6c339862...3fcd`, frozen_at 2026-10-05T11:19:01Z); no earlier revisions exist.
- Every normative atom of the six extended policies and their base policies is entailed by `docs/respite/`; nothing unborne, nothing with changed meaning, no claim from outside the source.
- All four prerequisite sentences stand verbatim, state form, only in their blocked hubs (`signed_stay_extension_d115aae6`, `level_change_charge_segment_7dc3fff9`, `stay_advance_payment_83b4a24c` x2); every hop resolvable from the sentence, the depended-on hub and the records.
- All 32 declared factors carry their full ladders in their own documents, findable from the customer's records; no computation document hints at modification.
- No task tool name outside its own hub; no route, aggregated chain or task-mirroring title.
- Coverage gap (explicit): cross-product contradictions and unclaimed base-only product corpora are outside this skill's range.

Gate re-run on the final form (auditor, repo root, docs unchanged):
- `.venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/env_0034_senior_living_operator respite` -> `[PASS] mechanical gates: ...` / `[MANUAL REQUIRED] ...` / `DOCS OK`
- `.venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py env/env_0034_senior_living_operator/tasks/respite_and_trial_stays` -> `TRACEABILITY OK`

Difficulty rendering verdict: PASS.
