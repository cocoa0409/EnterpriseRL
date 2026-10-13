# Difficulty closing checklist — seller_fees_and_selling_plans (product `selling`)

## revision_1 (2026-10-11T08:05Z)

Per-task part verdicts:

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT | Files |
|---|---|---|---|---|
| 0 (term change, Premium Store) | PASS | PASS | PASS | runtime_context/seller_fees_and_selling_plans/0.md; policy_kb/seller_fees_and_selling_plans/0.md |
| 1 (end annual term early, Anchor Store) | PASS | PASS | PASS | runtime_context/seller_fees_and_selling_plans/1.md; policy_kb/seller_fees_and_selling_plans/1.md |

Checklist:
- [x] Each task has one audit file per part. Blind answers were frozen at 07:55:09Z / 07:55:52Z (hashes appended 07:56:02Z) before the source was revealed at 07:56:05Z. This is revision_1, so there are no older revisions.
- [x] Every normative atom of the difficulty's structured source is entailed by docs/selling, with nothing unborne, nothing changed in meaning and no claim from outside the source. This covers 6 extended policies, 10 base policies, events/measures, all 48 variant parameters across the 6 tiers, and 6 task-tool contracts. Retired surfaces (6 overwritten base clauses/sub-clauses) are each printed as no longer in force, and the remaining clauses of those policies stay in force.
- [x] All 4 prerequisite sentences (all state form) appear verbatim only in the blocked policy's hub. Each hop can be resolved from that sentence, the depended-on hub and the records, and both blind answers marked every hop state-derived.
- [x] All 31 declared factors carry their full ladders, with every tier exact, in their own documents. Each is findable from the record words its tier rests on, including cross-product records: standing, payout and fulfill.
- [x] No other problem's tool name, route, aggregated chain or task-mirroring title appears anywhere.
- [x] Closing gates re-run on the final corpus (docs/selling concatenated sha256 0a884166c22af2b76b332c66f67785d8f086de0b2a1d466eb6abef65fe8e71be, unchanged from the blind phase):
  - `$ .venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py env/env_0054_ecommerce_marketplace_operator/tasks/seller_fees_and_selling_plans` → "0.json 29 0 True / 1.json 19 0 True / TRACEABILITY OK" (rc=0, 08:05:23Z)
  - `$ .venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/env_0054_ecommerce_marketplace_operator selling` → "docs=61 … prerequisite edges=4 … [PASS] mechanical gates … DOCS OK" (rc=0, 08:05:26Z). An earlier attempt at 07:58:52Z was killed (exit 137) by the session cut-off; this is the completed re-run.

Policy-side notes (these do not change the verdict; details are in policy_kb/…/0.md under bijection_verdict):
1. The term-change overwrite retires the base timing clause and restates its annual→monthly half.
2. The cancellation overwrite retires "credited in full / no administration fee", but the cancellation baseline restates it. The schedule figure "admin fee waived on cancellation" remains next to the new cancellation administration fee.
3. Upheld disputes on grounds other than a missing standing discount have no credit-sizing clause in force.
4. The billing discount clause is retired, but a missing standing discount remains a live ground for upholding a dispute.

Coverage note: cross-product contradictions are outside this skill's detection range. The order and standing KBs are not yet published.

**Difficulty verdict: PASS** (all three parts PASS for tasks 0 and 1).

## revision_2 (2026-10-11T08:54Z)

| Task | KB-RUNTIME | KB-BIJECTION | KB-EXPLICIT |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

- Round-1 REDs to close: none (round 1 was PASS for both tasks).
- New defects: none.
- Regressions: none.
- Change scope: verified as the two named documents only, which match the revision_3 source. The scored values are unchanged in the GT and in the blind re-derivation.
- Contamination: the revision_2 runtime check was made by an auditor who had already seen the revision_1 source and GT; this is disclosed in the runtime files. The revision_1 blind answers remain the clean blind record.
- Gates re-run on the final corpus (docs/selling sha256 81549df37e3c190a55968c2af97895cbb71274572af86888cf29cd5a1f3916f4), 08:53:52Z:
  - check_docs.py selling → "docs=61 … prerequisite edges=4 … [PASS] mechanical gates … DOCS OK".
  - check_traceability.py → "0.json 29 0 True / 1.json 19 0 True / TRACEABILITY OK".

**Difficulty verdict (revision_2): PASS.**
