# Difficulty closing checklist — fbn_storage_inventory_reimbursements (product fulfill)

## revision_1

Auditor: independent erl-kb-doc-policy-audit agent. Blind work 2026-10-11T07:49:56Z; blind answers frozen before 2026-10-11T07:54:41Z; reveal 2026-10-11T07:54:47Z; closing written 2026-10-11T08:02:58Z.

Entry conditions (Step 0, cited from the brief, not re-run): policy-side verdict PASS at revision_2 for tasks 0 and 1; check_docs.py fulfill "DOCS OK"; check_traceability.py "TRACEABILITY OK" (0.json 17/0, 1.json 24/0); runtime view + tool-shaped DB path supplied (db_query.py sha256 f2d05ab5…, runtime JSONs match HASHES.txt). Complete.

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
|---|---|---|---|
| 0 | PASS | PASS | KB-EXPLICIT RED (1) |
| 1 | PASS | PASS | PASS |

Checklist:
- Audit files one-to-one with tasks: runtime_context/…/0.md, 1.md; policy_kb/…/0.md, 1.md. First revision; no older revisions to preserve.
- Every normative atom of the five extended policies, their base policy and the whole product's base/variant layer is entailed by docs/fulfill with nothing unborne, changed or added: yes.
- Every prerequisite sentence (3 edges, all state form) verbatim on its blocked side only, each hop resolvable from it, the depended-on documents and the records: yes.
- Every declared factor ladder (26 factors) carried in full and findable from record words: yes.
- No tool name, route or aggregated chain beyond the sentences: yes. However one factor document hints at another factor (task 0 finding): store_tenure_lookback_extension_7b9ff99a, "Example: a lookback base of 4 months and an Anchor Store plan opened 26 whole months ago give a warehouse-loss lookback of 6 months." — the 4-month base is the middle tier of the separate lookback-base factor, so this document discloses that the lookback base varies.

**Difficulty status: NOT CLOSED** — task 0's dependency-form scan is KB-EXPLICIT RED. The final-form re-run of check_docs.py / check_traceability.py is deferred to the closing round after the finding is settled.

## revision_2

Re-audit round 2 (started 2026-10-11T08:40:35Z; closed 2026-10-11T08:42:05Z, system clock). revision_1 text above left untouched.

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
|---|---|---|---|
| 0 | PASS (re-derivation; contamination_disclosure in runtime_context/…/0.md revision_2) | PASS | PASS (round-1 KB-EXPLICIT RED closed) |
| 1 | PASS (re-derivation; disclosure as task 0) | PASS | PASS |

### Checklist
- **Audit files.** They correspond one-to-one with the tasks, and the revision_1 text is preserved in all five files. Each comparison section carries a PASS at revision_2.
- **Normative atoms.** Every normative atom is entailed by docs/fulfill:
  - all five extended policies, the base reimbursement terms, the other 11 base policies, the measures, and the 48 variant parameters × 6 programs;
  - nothing unborne, changed or added;
  - the retired surface is exactly the three declared overwrites.
- **Prerequisite sentences.** All three state-form prerequisite sentences stand verbatim on the blocked side only. Every hop is state-derived from the sentence, the depended-on documents and the records.
- **Factor ladders.** All 26 factor ladders are carried in full, with every tier exact, and each is findable from the record words its tier rests on.
- **Beyond the sentences.** Nowhere is a tool name, route, aggregated chain, cross-factor pointer or mirroring title stated.
- **Final-form gates.** Re-run by the coordinator on the final form after the re-render, and cited from gates.kb.r2.txt per the brief:
  - check_docs.py fulfill: "DOCS OK" (57 docs, roles facet 9 / policy 12 / baseline 5 / factor 26 / hub 5, prerequisite edges 3);
  - check_traceability.py: "TRACEABILITY OK" (0.json 17 copied / 0 missing; 1.json 24 / 0);
  - validate_scenario: VALID, 0 warnings.

### Coverage notes
- Cross-product contradictions remain outside this skill's detection range. The order and standing corpora are now published but were not used as criteria.
- The revision_2 runtime part is a re-derivation by an auditor who had already seen the source, not a fresh blind audit. The clean blind answers are those frozen in revision_1. For tasks 0 and 1 the changed surface is one factor document whose tiers are unchanged.

**Difficulty status: CLOSED — PASS** (all three parts PASS for both tasks).
