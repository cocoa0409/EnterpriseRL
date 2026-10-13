# KB-doc policy audit — closing checklist — listing_settings_and_compliance (product `listing`)

## revision_1 (2026-10-07)

| Task | KB-RUNTIME (runtime_context/<k>.md) | KB-BIJECTION (policy_kb/<k>.md) | KB-EXPLICIT (policy_kb/<k>.md §dependency_form) |
|---|---|---|---|
| 0 (short-stay cleaning fee; prereqs cleaning-fee ceiling, pet-fee ceiling) | PASS — blind 385.00 / 340.00 / 333.61 = GT | PASS | PASS (source-entailed notes N1–N3) |
| 1 (Pricing Assist; prereqs minimum-stay floor, extra-guest ceiling) | PASS — blind 3 / 63.20 / 446.11 = GT | PASS | PASS (source-entailed notes N1–N4) |

Checklist:
- [x] Audit files correspond 1:1 with tasks/0.json and tasks/1.json; blind answers frozen with sha256 before reveal (task_0 6cc2f649…60d2c, task_1 63e4d4cf…f562e0) and re-verified after; no older revision exists for this difficulty.
- [x] Every normative atom of the six extended policies (rules, baselines, all 29 declared factors with every tier, overwrites) and of the referenced base policies is entailed by docs/listing; nothing added, nothing dropped, no meaning change; retired surface printed as "no longer in force" exactly for the five declared overwrites.
- [x] The four prerequisite sentences (two per root) stand verbatim, state form, in their blocked hubs only; each hop resolves from the sentence, the depended-on card ("… is reset/raised to the ceiling/floor exactly") and the records.
- [x] No other problem's tool name, route, aggregated chain or task-mirroring title anywhere in the corpus.
- [x] Every factor document findable from record words; every computation document yields a definite fall-back that differs from the scored value.
- Policy-side notes (do not change verdicts): computation documents of short-stay, extra-guest, minimum-stay and Pricing Assist necessarily signal that modifiers exist because the source baseline uses the label "standard" and the source result assembly names the modified quantity; look-back factors decide sibling factors' windows; "last N whole months" boundary days left open by the source.
- Coverage gap (stated, not covered): cross-product contradictions and base-only products are outside this skill's range.

Closing gate re-run on the final form (2026-10-07, read-only):
- `.venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/env_0045_vacation_rental_platform listing` -> `[PASS] mechanical gates …` / `[MANUAL REQUIRED] …` / `DOCS OK`
- `.venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py env/env_0045_vacation_rental_platform/tasks/listing_settings_and_compliance` -> `TRACEABILITY OK`

Difficulty verdict: **PASS** (runtime blind audit PASS + full-domain two-way scan PASS + dependency-form scan PASS for both tasks).
