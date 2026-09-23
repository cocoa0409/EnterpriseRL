# KB-document policy audit — closing checklist for protection_claims_desk

Product audited: `protection` (Belrose Jewelry Protection and Care Plans), 53 published documents in
`env/env_0001_fine_jewelry_retailer/docs/protection/`. Tasks: 2. Auditor: fresh agent, independent of the
renderer and of the policy-side auditor. Blind audits frozen 2026-09-17T13:10:20Z; source layer
revealed 2026-09-17T13:22Z.

## Three part-verdicts per task

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
|---|---|---|---|
| 0 (cancellation refund ← claim settlement) | **KB-RUNTIME RED** | **KB-BIJECTION RED** | PASS |
| 1 (transfer carry-over ← allowance reinstatement, claim refusal) | PASS | PASS | PASS |

Both RED marks are the **same single defect**, reported once in each of the two files that must record
it: the computation document of `protection_ext_claim_settlement`,
`env/env_0001_fine_jewelry_retailer/docs/protection/benefit_drawn_on_an_accepted_claim_94946301.json`, drops the
loyalty step's baseline default and rewrites the source's assembly sentence — "The reduced figure, and
not the figure before any loyalty discount, is the base every later step acts on." — as step 2's "That
figure is the base every later step acts on.", where "that figure" is the priced bench work *before*
any loyalty reduction. The consequence is that the scored `benefit_amount` in task 0 is not uniquely
entailed by the visible materials (1064.90 sequentially, 1061.32/1061.33 if wear and loyalty both come
off the figure standing for the repair). Evidence and locations: `policy_kb/…/0.md` §bijection_verdict (1)
and `runtime_context/…/0.md` §gt_comparison.

Reported, not repaired: this audit edits no document and arranges no fix.

## Closing checklist

| Item | Status |
|---|---|
| Audit files correspond one-to-one with the tasks | yes — `runtime_context/protection_claims_desk/{0,1}.md`, `policy_kb/protection_claims_desk/{0,1}.md` |
| Old revisions traceable | this is revision 1 of all four files; nothing overwritten |
| Blind answer frozen to disk before any source-layer read | yes, both tasks; no `contamination_disclosure` on either |
| Every comparison section carries a verdict | yes |
| Every normative atom of the structured source entailed by the product's docs | **no** — one dropped default and one reversed assembly sentence in `benefit_drawn_on_an_accepted_claim_94946301` |
| Nothing borne with changed meaning | **no** — the same sentence |
| No claim from outside the source | yes — zero hits on the added-policy sweep across all 53 documents |
| Every prerequisite's prerequisite sentence verbatim, in its declared form, in a document of the policy it blocks and in no other policy's | yes — all 3 edges, all `form: state`, each sentence occurring exactly once in the corpus |
| Every hop resolvable at the source's strength from the sentence, the depended-on documents and the records | yes — 3 of 3, all **state-derived** in both blind audits; none pre-solved |
| Every declared factor's ladder carried in full, every tier exact, in its own factor document | yes — 24 of 24 factors, every tier, every compound condition in both parts, every threshold in figures, every constant rendered |
| Every factor findable from the words the customer's records use | yes — including the five cross-product factors, each naming Belrose Circle, the Belrose Workshop Repair and Resizing Service or the Belrose Appraisal and Gemological Services by its official name and the kinds of record it reads |
| Retired surface | 13 blockquoted retired clauses in the corpus against 13 `overwrite` entries in the source; each carried verbatim and marked no longer in force; none still stated as a rule in force; the KB retires nothing the source does not declare retired; every unnamed clause of those policies still carried as in force |
| No other problem's tool name, route or aggregated chain anywhere beyond the prerequisite sentences | yes — each of the 5 task tool names occurs in exactly one document, its own policy's hub; zero hits on the route/checklist/chain sweep |
| All three parts PASS for all tasks | **no** — task 0 fails two parts |

## Gates on record

Run by the coordinator from the repo root after publication and supplied with the brief; the auditor
ran neither. The corpus was not modified by this audit, so these output lines still describe its final
form.

```
🔎 DOCS gate  product=protection profile=extended docs=53 roles={'factor': 24, 'facet': 7, 'baseline': 5, 'policy': 12, 'hub': 5} content[min/mean/max]=1236/2108/3574
   required quantitative keys=111  task_tools=5  prerequisite edges=3

  [PASS] mechanical gates: structure, zero implementation leaks, tool fidelity, no workflow docs, non-directory hubs, private compute-binding coverage, quantitative coverage, every prerequisite sentence carried verbatim on its blocked side, no tool-name pointers or route scaffolding
  [MANUAL REQUIRED] normative claims <-> structured source semantic bijection; every hop resolvable at the source's strength from the prerequisite sentence, the depended-on docs and the records, no state-form sentence restated as an action, and no route stated beyond the sentences
DOCS OK

🔎 TRACEABILITY gate  (2 tasks)
task        copied  missing    ok
0.json          15        0  True
1.json          21        0  True
TRACEABILITY OK
```

The `[MANUAL REQUIRED]` line is exactly what this audit answers, and it is where the defect sits: the
gate can see that the loyalty ladder is published and that every prerequisite sentence stands on its
blocked side, but it cannot see that the computation document's base sentence names the opposite base
from the one the rule fixes.

## Coverage statement

This audit covers the `protection` product only, which is the product this difficulty claims. Base-type
products claimed by no difficulty are outside its scope. Cross-product contradictions are outside its
detection range by construction; sibling corpora (`docs/service/`, `docs/circle/`,
`docs/appraisal/`) were read only where a protection factor document names those businesses and sends
the reader to their published figures, and were never used as a criterion.

## Difficulty verdict

**NOT CLOSED.** Task 1 passes all three parts. Task 0 carries one defect, recorded twice under the two
parts it fails. The difficulty closes once that computation document carries the settlement baseline's
loyalty default and the assembly the source's rule fixes, and the two task-0 sections are re-run and
appended as `## revision_2`.

---

## revision_2

Re-audit round 2, 2026-09-17. All revision-1 text above is untouched, including the two checklist rows
that read **no**; they record what was true at revision 1 and are superseded, not rewritten, by the
rows below.

Corpus at revision 2: `cat env/env_0001_fine_jewelry_retailer/docs/protection/*.json | sha256sum` =
`fab5030fbcf6303edc96d2ae7dd5b0a8adf46957bead13c0e2e7872c14dc4722`
(revision 1: `d794eb65765cc3246e7b9ceb691bcbb681265eba322ee48f86fee868ecfa2ff7`).

**Scope of the re-render, verified by the auditor against the frozen revision-1 dump rather than
accepted on the renderer's claim:** exactly one of the 53 documents differs —
`benefit_drawn_on_an_accepted_claim_94946301.json` — and the other 52 are byte-identical in `title`
and `content`; none added, none removed.

## Three part-verdicts per task — revision_2

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
|---|---|---|---|
| 0 (cancellation refund ← claim settlement) | **PASS** (was KB-RUNTIME RED) | **PASS** (was KB-BIJECTION RED) | PASS |
| 1 (transfer carry-over ← allowance reinstatement, claim refusal) | PASS | PASS | PASS |

**The revision-1 defect is genuinely closed.** The settlement computation document now runs eight
steps with a new step 3 — "**3. The loyalty reduction.** Nothing is taken off that figure for loyalty.
The reduced figure, and not the figure before any loyalty discount, is the base every later step acts
on." — and the reversed restatement has been removed from step 2. Verified: the assembly sentence is
**verbatim** from `protection_ext_claim_settlement.rule` with the exclusion intact; the default is
flat and unconditional and renders `factors[loyalty_reduction].baseline: {loyalty_pct: '0.0'}` rather
than the ladder's third tier, so no ladder is leaked into the baseline; all four order-and-rounding
moments the source pins are carried verbatim, and the eight-step sequence reproduces the source rule's
own sentence order and compute chain with no added measurement or ordering; a reader of the visible
corpus alone now reaches **one** value on task 0's world, 1064.90, with the revision-1 rival reading
(1061.32/1061.33) excluded by step 3's own words; the masked fall-back from the computation document
alone is unchanged at 781.60 and still matches the source's `baseline_result`; and task 0's second
scored figure stays at 246.67 because the first stays on the same tier.

## Closing checklist — revision_2

| Item | Status |
|---|---|
| Audit files correspond one-to-one with the tasks | yes |
| Old revisions traceable | yes — revision_1 preserved verbatim in all five files; revision_2 appended |
| Blind answers never rewritten to accommodate the re-render | yes — both revision-1 `blind_answer` sections are untouched, and this round compares the corpus against them |
| Every normative atom of the structured source entailed by the product's docs | **yes** (revision 1: no) |
| Nothing borne with changed meaning | **yes** (revision 1: no) |
| No claim from outside the source | yes — zero hits, corpus-wide, on the added-policy sweep |
| Every prerequisite's prerequisite sentence verbatim, in its declared form, in a document of the policy it blocks and in no other policy's | yes — all 3 edges, each sentence occurring exactly once in the re-rendered corpus |
| Every hop resolvable at the source's strength | yes — 3 of 3, all state-derived, none pre-solved |
| Every declared factor's ladder carried in full, every tier exact | yes — 24 of 24, unchanged |
| Every computation document carries a default for every factor slot | **yes** — settlement 5/5 (was 4/5), cancellation 4/4, refusal 5/5, reinstatement 6/6, transfer 4/4 |
| Every non-factor compute binding homed | yes — including the two `year_months_elapsed` bindings, each homed by a neutral period definition that renders `MONTHS(effective_date, NOW) % 12` exactly; carrying their conditional `compute_basis` instead would have stated a ladder in a baseline |
| Every factor findable from the words the customer's records use | yes — unchanged |
| Retired surface | 13 retired clauses against 13 `overwrite` entries; none retired or un-retired by the re-render |
| No other problem's tool name, route or aggregated chain anywhere | yes — each of the 5 tool names in exactly one document, its own hub; the revised document names no tool at all |
| No new defect introduced by the re-render | yes — the revised document names no tool, document, policy id, factor tier or customer; its worked-example figures are unchanged; its one inserted example sentence is on declared hypothetical inputs |
| Nothing that passed at revision 1 regressed | yes — 52 documents byte-identical, and the corpus-wide sweeps re-run on the new corpus all return the revision-1 result |
| All three parts PASS for all tasks | **yes** (revision 1: no) |

## Gates on record — revision_2

```
🔎 DOCS gate  product=protection profile=extended docs=53 roles={'factor': 24, 'facet': 7, 'baseline': 5, 'policy': 12, 'hub': 5} content[min/mean/max]=1236/2113/3574
   required quantitative keys=111  task_tools=5  prerequisite edges=3
   mechanical gates PASS; [MANUAL REQUIRED] semantic bijection and dependency form
DOCS OK

🔎 TRACEABILITY gate  (2 tasks)
task        copied  missing    ok
0.json          15        0  True
1.json          21        0  True
TRACEABILITY OK
```

The mean content length moving 2108 → 2113 with min and max unchanged is consistent with the single
229-character change the auditor measured, which corroborates that these gate lines describe this
corpus.

## Difficulty verdict — revision_2

**CLOSED.** Runtime blind audit PASS + full-domain two-way scan PASS + dependency-form scan PASS, on
both tasks. The rendering of the `protection` product passes the audit for
`protection_claims_desk`.

Coverage statement from revision 1 stands unchanged: this audit covers the `protection` product only;
base-type products claimed by no difficulty are out of scope; cross-product contradictions are outside
its detection range, and sibling corpora were read only where a protection factor document names those
businesses by their official names, never as a criterion.
