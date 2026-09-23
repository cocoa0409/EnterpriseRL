# KB-document policy audit — closing checklist: maintenance_agreement_desk

Revision 1. Scenario `env/commercial_hvac_service_contractor`; difficulty `maintenance_agreement_desk`;
product claimed exclusively: `maintenance` (Preventive Maintenance Agreements). M = 2.
Audited corpus: `env/env_0002_commercial_hvac_service_contractor/docs/maintenance/` — 71 documents, sha256 prefix
`c304fa6508faaa50`.
Auditor independent of the render agent and of the policy-side auditor; no document was edited and no fix
was arranged.

## Three part-verdicts per task

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan | Overall |
|---|---|---|---|---|
| 0 | **PASS** (`runtime_context/maintenance_agreement_desk/0.md`) | **PASS** (`policy_kb/maintenance_agreement_desk/0.md`, `bijection_verdict`) | **PASS** (same file, `dependency_form`) | **PASS** |
| 1 | **PASS** (`runtime_context/maintenance_agreement_desk/1.md`) | **PASS** (`policy_kb/maintenance_agreement_desk/1.md`, `bijection_verdict`) | **PASS** (same file, `dependency_form`) | **PASS** |

No `KB-RUNTIME RED`, no `KB-BIJECTION RED`, no `KB-EXPLICIT RED`.

## Difficulty closing checklist

- **Audit files correspond one-to-one with the tasks.** `runtime_context/maintenance_agreement_desk/{0,1}.md`
  and `policy_kb/maintenance_agreement_desk/{0,1}.md`, one of each per task. This is revision 1; no earlier
  revision exists, so nothing was overwritten. Each `blind_answer` was written to disk in full before any
  source-layer artefact was opened, and neither was modified afterwards.
- **Every comparison section carries a PASS.** Both `gt_comparison` sections, both `bijection_verdict`
  sections and both `dependency_form` sections.
- **Every normative atom of the structured source is entailed by the product's docs.** Seven extended
  policies (baselines carried complete in their own computation documents, defaults rendered, product
  figures named), thirty-four declared factors (every tier of every ladder, every part of every compound
  condition, every threshold in figures), fourteen base policies, nine tier tables, seven `overwrite`
  entries rendered as retired with their tier figures retained, and seven tool contracts matching
  `task_tools.py` in owner, parameters, formats, effects and returns. Nothing unborne, nothing borne with
  changed meaning, and no claim from outside the source.
- **Every prerequisite's sentence stands verbatim, in its declared form, on the blocked side and nowhere
  else.** Five edges, all `form: state`. Mechanically verified that each `policy_source` sentence occurs in
  exactly one document of the corpus and that that document is the blocked problem's own hub; none occurs
  in any depended-on problem's documents. Every hop is resolvable at the source's strength from that
  sentence, the depended-on problem's own rules and the records — for all five, the depended-on documents
  describe, in the words the sentence uses for the state, the write that brings it about.
- **Every declared factor's ladder is carried in full in its own factor document, findable from the records
  its tier rests on.** The eight cross-difficulty factors name the other product by its official name —
  the Demand Service Rate Programs (four) and the Building Automation Service Plans (four) — and the kinds
  of record they read.
- **No other problem's tool name, route or aggregated chain is stated anywhere beyond those sentences and
  their same-form equivalents.** Each of the seven task-tool names occurs in exactly one document, its own
  problem's hub; no document names another document or a policy id; no document mentions two of the seven
  problems; no checklist, roadmap, dependency table or ordered step list exists in the corpus.
- **Both gates re-run once on the final form** (2026-09-17, from the repository root; the corpus was
  unchanged by this audit):

```
.venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/commercial_hvac_service_contractor maintenance
  🔎 DOCS gate  product=maintenance profile=extended docs=71 roles={'hub': 7, 'baseline': 7, 'factor': 34, 'facet': 9, 'policy': 14} content[min/mean/max]=917/1902/2961
     required quantitative keys=125  task_tools=7  prerequisite edges=5
    [PASS] mechanical gates: structure, zero implementation leaks, tool fidelity, no workflow docs, non-directory hubs, private compute-binding coverage, quantitative coverage, every prerequisite sentence carried verbatim on its blocked side, no tool-name pointers or route scaffolding
    [MANUAL REQUIRED] normative claims <-> structured source semantic bijection; every hop resolvable at the source's strength from the prerequisite sentence, the depended-on docs and the records, no state-form sentence restated as an action, and no route stated beyond the sentences
  DOCS OK

.venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py env/env_0002_commercial_hvac_service_contractor/tasks/maintenance_agreement_desk
  🔎 TRACEABILITY gate  (2 tasks)
  task        copied  missing    ok
  0.json          26        0  True
  1.json          17        0  True
  TRACEABILITY OK
```

  The `[MANUAL REQUIRED]` line is what this audit answers, and it is answered PASS for both tasks.

## Honest record of one blind-phase slip (task 0)

In the blind phase I queried the demand service ledger as `find_service_events(program_id=…)`, which
returned "No demand service history" because `service_events` rows carry no `program_id` field. Two of
task 0's four figures were therefore computed on an empty cross-product ledger and came out 36.63 and
784.58 instead of 32.19 and 969.48, carrying through to the settlement. The *method* on every one of the
nineteen factor readings was identical to the source's; only those two input readings differed. Re-queried
with the natural key, `find_service_events(customer_id=…)` returns the five rows the source reads, the two
ladders resolve exactly as the source does from the visible documents alone, and the settlement comes to
the source's figure. Both factor documents name the Demand Service Rate Programs records they read in
plain business words, and the runtime tool is described as reading exactly those records, so the corpus
was not at fault. Recorded in `runtime_context/maintenance_agreement_desk/0.md` under `gt_comparison`; the
frozen `blind_answer` was left untouched.

## Policy-side notes carried forward (not part of this skill's verdict)

1. `hours_band_uplift`'s ladder says the uplift is "the unit price multiplied by the amount by which the
   tier's overtime multiplier stands above one" without restating whether "the unit price" is the tapered
   quantity; the source's own compute resolves it to the tapered figure and the corpus reads the same way.
2. Two ladders state a count as "booked … with no visit completed against them" while their computes take a
   difference of windowed counts (`lost_visit_window`, `unperformed_visit_writedown`). The readings coincide
   here; the documents render the ladder sentences exactly.
3. Base law that states an order between acts — `maintenance_visit_scheduling`'s "a suspended agreement is
   scheduled again only after it is reinstated" and `maintenance_renewal` Clause 4 — is rendered as the
   source has it, which the KB may neither drop nor soften.

None of these changes the verdict, which lies only among `KB-BIJECTION RED` / `KB-RUNTIME RED` /
`KB-EXPLICIT RED` / `PASS`.

## Coverage statement

This audit covers only the `maintenance` product, which is what this difficulty claims. The scenario's
other on-disk corpora (`docs/energy`, `docs/iaq`, `docs/warranty`) were not used as a criterion and are
outside this skill's scope; cross-product contradictions are therefore structurally suppressed rather than
proved absent, as the skill states.

**Difficulty verdict: the rendering of `maintenance` for `maintenance_agreement_desk` PASSES the
KB-document policy audit at revision 1.**
