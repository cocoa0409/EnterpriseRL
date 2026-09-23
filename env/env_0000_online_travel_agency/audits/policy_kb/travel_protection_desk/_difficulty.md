# KB-doc policy audit — closing checklist, travel_protection_desk (product `care`)

## revision_1

Auditor: independent render-layer auditor. Did not write these documents; did not read the policy-side
(`erl-task-policy-audit`) reports. Blind audits were frozen to disk before any source-layer artefact was opened.

## Part-verdicts

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
| - | - | - | - |
| 0 | **PASS** (no `KB-RUNTIME RED`) | **PASS** (no `KB-BIJECTION RED`) | **PASS** (no `KB-EXPLICIT RED`) |
| 1 | **PASS** (no `KB-RUNTIME RED`) | **PASS** (no `KB-BIJECTION RED`) | **PASS** (no `KB-EXPLICIT RED`) |

On both tasks the blind answer — reached from the published documents, the runtime tool schemas, tool-shaped
DB queries and the simulator's script alone — matched the source-layer solution on **every** item: the problem
tree and its direction, the handling order, the tools and their owners, and every scored argument including
both computed amounts on each task.

- Task 0: destination loading **80.97** (`call_centre`); restoration **−510.00**; settlement **1410.00** paid
  with **30.00** held back.
- Task 1: corrected declared trip cost **18436.50**; re-rating adjustment **127.59**; claim filed for
  **5144.85**.

## Closing checklist

- [x] **Audit files correspond one-to-one with the tasks.** `runtime_context/travel_protection_desk/{0,1}.md`
      and `policy_kb/travel_protection_desk/{0,1}.md`, each with a frozen `blind_answer` written before the
      reveal, a `gt_comparison`, `source_to_kb`, `kb_to_source`, `bijection_verdict` and `dependency_form`.
      This is `revision_1`; no older revision exists to preserve.
- [x] **Every comparison section carries a PASS.**
- [x] **Every normative atom of the structured source is entailed by the product's docs.** 78 base-policy
      sentences across 13 base policies; 6 baseline rules; 27 factor ladders (81 tiers); 11 `overwrite`
      retirements; 5 `prerequisite` sentences. Nothing unborne, nothing borne with changed meaning, no claim
      from outside the source. A corpus-wide sweep for added-policy forms (confirmations, second reviews,
      notifications, verifications, fallback procedures) returned zero hits.
- [x] **Every prerequisite's sentence stands verbatim, in its declared form, in a document of the policy it
      blocks and in no other policy's.** Verified mechanically as an exact substring search across all six
      products' published documents: each of the five sentences occurs in exactly one document, and that
      document is the blocked problem's hub. All five are `form: state`, and all five keep their ordering
      connective ("only after", "only once") and their hard-gate strength.
- [x] **Every hop is resolvable from the sentence, the depended-on documents and the records.** The five edges
      resolve through record vocabulary — "premium lines"/"destination loading"/"declared region";
      "restoration"/"a supplier has paid the traveller"/"benefit consumed"; "the certificate carries the
      declared trip cost"/"prepaid outlay"; "premium lines"/"re-rating". Demonstrated, not asserted: the blind
      audit derived all five hops without the source.
- [x] **Every declared factor's ladder is carried in full, every tier exact, in its factor document, findable
      from the records its tier rests on.** All 27 factors map to exactly one document each, with every
      non-`otherwise` tier condition present verbatim; the sweep covered untriggered tiers as well as the ones
      these two seeds reach. Compound conditions keep both parts, thresholds named under a business term are
      also stated in figures, and boundaries are pinned on the correct side. The twelve cross-difficulty
      factors each name the other product by its official name (`Wanderlane Traveller Club`,
      `Air Ticket Fare Brands`, `Vacation Package Products`) and the kinds of record they read.
- [x] **No other problem's tool name, route or aggregated chain is stated anywhere.** Each of the six task-tool
      names appears in exactly one document — its own hub's invocation block. No policy id appears anywhere;
      no document points at another by title; no dependency table, checklist, roadmap, ordered step list or
      cross-problem example exists; no computation document hints that anything modifies it (zero hits for
      "unless otherwise", "adjustments may apply", "certain customers", "set out elsewhere", exception lists
      and pointers); no factor document names the computation document or another factor; no factor document
      says which tier a customer falls on; no document writes a task's opening world state in as a policy fact.
- [x] **The retired surface is exact.** All 11 superseded clauses are present, each in exactly one document,
      each written as no longer in force. Exactly six documents declare retirements — matching the six base
      policies that carry `overwrite` — so the KB retires nothing the source did not. The three partial
      retirements keep the surviving half explicitly in force, and each document states that its other clauses
      stand and its plan figures remain valid as scheduled.
- [x] **Gates re-run once on the final form.** No document was edited by this audit.

```
$ .venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/online_travel_agency care
🔎 DOCS gate  product=care profile=extended docs=64 roles={'facet': 12, 'policy': 13, 'factor': 27, 'baseline': 6, 'hub': 6} content[min/mean/max]=707/2441/5440
   required quantitative keys=116  task_tools=6  prerequisite edges=5

  [PASS] mechanical gates: structure, zero implementation leaks, tool fidelity, no workflow docs, non-directory hubs, private compute-binding coverage, quantitative coverage, every prerequisite sentence carried verbatim on its blocked side, no tool-name pointers or route scaffolding
  [MANUAL REQUIRED] normative claims <-> structured source semantic bijection; every hop resolvable at the source's strength from the prerequisite sentence, the depended-on docs and the records, no state-form sentence restated as an action, and no route stated beyond the sentences
DOCS OK

$ .venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py env/env_0000_online_travel_agency/tasks/travel_protection_desk
🔎 TRACEABILITY gate  (2 tasks)
task        copied  missing    ok
0.json          28        0  True
1.json          26        0  True

TRACEABILITY OK
```

The `[MANUAL REQUIRED]` line is precisely what this audit discharges, and it is discharged PASS on both tasks.

## Difficulty verdict

**PASS.** Runtime blind audit PASS + full-domain two-way scan PASS + dependency-form scan PASS, on both tasks.
This difficulty's rendering passes the audit.

## Notes carried back (policy-side; they do not change this skill's verdict)

1. **Cross-product naming seams.** Three figures that `care` factor documents defer to another product are
   scheduled there under a different noun: the club's *"protection discount"* is scheduled as *"the insurance
   discount on travel protection premiums"*; the package's *"returns the deposit on cancellation"* is scheduled
   as *"Deposit recorded as returnable"*; the package's *"may be transferred to another traveller"* is scheduled
   as *"Credit may be redeemed by another traveller"*. In each case the `care` document names the other product
   by its official name and names the kind of record, so the hop is resolvable and this is not a rendering
   defect — the blind audit crossed all three. Recorded so the vocabulary can be aligned at the charter layer
   if that is wanted.
2. **A singular definite description over a table that may hold several matching rows.** The promptness factor
   turns on *"the line that gave the value back"*; task 1's package ledger carries both a price-guarantee refund
   and a cancellation credit. The source resolves it by `reason_code='traveller_cancellation'`, the document
   resolves it the same way through its own framing ("the journey was given up"), and the blind audit reached
   the source's answer unaided — so it is determinate here. Recorded because a differently-shaped ledger in a
   future seed could make the description load-bearing.

## Coverage limits, stated honestly

- This skill is organised per difficulty and audits only the product this difficulty claimed (`care`).
  Cross-product contradictions are outside its detection range; they are structurally suppressed by the render
  skill's requirement that each document name its own official product and by each difficulty's policy content
  being single-homed, but that is "suppressed", not "proved absent". Documents of `air`, `bundle` and `club`
  were read only where a `care` factor document defers a figure to them, and were used as the reachable source
  of that figure, never as a criterion.
- The DB side was genuinely blind: every record came from real tool calls through the frozen runtime engine,
  never from `initial_state` read as a document. All six task tools were additionally exercised against each
  task's world (writes discarded on process exit) and returned exactly the confirmation sentences their
  documents describe.
