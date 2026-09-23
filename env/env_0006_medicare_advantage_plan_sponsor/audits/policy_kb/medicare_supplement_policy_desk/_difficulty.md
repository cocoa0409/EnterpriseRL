# KB-document audit closing record — medicare_supplement_policy_desk (product `medigap`)

Revision 1. Auditor: independent KB-doc auditor, independent of the renderer and of the policy-side auditor.
Scope: the 57 published documents under `docs/medigap/`, audited against
`tasks/medicare_supplement_policy_desk/medigap.extended.yaml` and the runtime tool schemas, for the two tasks of
this difficulty.

## Entry conditions (Step 0)

| Condition | Status |
|---|---|
| Policy-side verdict for this difficulty | PASSED at round 2 (cited from the brief; not re-audited here) |
| `check_docs.py` on `medigap` | green — snapshot below, supplied with the brief; not re-run by the auditor |
| `check_traceability.py` on this difficulty | green — snapshot below |
| Runtime-visible view supplied | yes |
| Tool-shaped DB access path supplied | yes — the blind audit read records only through finder calls, never `initial_state` |

Gate snapshot as supplied:

```
$ .venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/env_0006_medicare_advantage_plan_sponsor medigap
🔎 DOCS gate  product=medigap profile=extended docs=57 roles={'policy': 11, 'factor': 25, 'facet': 11, 'baseline': 5, 'hub': 5} content[min/mean/max]=1400/2154/4183
   required quantitative keys=67  task_tools=5  prerequisite edges=3
  [PASS] mechanical gates: structure, zero implementation leaks, tool fidelity, no workflow docs, non-directory hubs, private compute-binding coverage, quantitative coverage, every prerequisite sentence carried verbatim on its blocked side, no tool-name pointers or route scaffolding
  [MANUAL REQUIRED] normative claims <-> structured source semantic bijection; every hop resolvable at the source's strength from the prerequisite sentence, the depended-on docs and the records, no state-form sentence restated as an action, and no route stated beyond the sentences
DOCS OK

$ .venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py env/env_0006_medicare_advantage_plan_sponsor/tasks/medicare_supplement_policy_desk
🔎 TRACEABILITY gate  (2 tasks)
task        copied  missing    ok
0.json          19        0  True
1.json          23        0  True
TRACEABILITY OK
```

The documents were not edited by this audit, so the snapshot stands for the form audited.

## Three part-verdicts per task

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
|---|---|---|---|
| 0 — premium account settlement (Marguerite Nieves, Plan N) | **PASS** | **PASS** | **KB-EXPLICIT RED** |
| 1 — waiting foreign-travel crossover line (Aurelio Quintero, High Deductible Plan G) | **PASS** | **PASS** | **KB-EXPLICIT RED** |

**The difficulty does not close out.** "Runtime PASS + bijection PASS + dependency-form PASS" is required
together, and the dependency-form part fails on both tasks, on one shared defect.

## What passes

- **Blind derivation reproduced the source exactly.** From the published documents, the tool schemas and finder
  returns alone — with `initial_state`, `medigap.extended.yaml`, `task_tools.py` and every GT field withheld until
  the blind answers were on disk and hashed — both problem trees and every scored figure came out equal to the
  source layer: task 0's 145.43 and 530.21, task 1's 766.00, 668.00 and 6658.00, together with every identifier,
  billing period, Medicare claim number, date of service, tool owner and the verbatim remittance reference. The
  one divergence anywhere was `balance_effect` on task 0, where the blind answer's recorded alternative
  (`overpayment`) was the source's and the document does determine it.
- **Both problem trees are derivable, and every hop is state-derived.** All three `prerequisite` edges are
  carried by a prerequisite sentence standing verbatim, in the state form, in a document of the policy it
  blocks and in no other policy's document; each waited-on state is visibly absent on the records; and each
  depended-on policy's own rule describes, in the sentence's own words, the write that brings it about. No hop
  was pre-solved by a tool name, a policy id, a route or an aggregated chain.
- **The bijection holds across the whole domain.** 11 base policies, 7 variants × 54 parameters, 5 extended
  policies with their baselines, and all 25 declared factors are homed one-to-one; every tier of every ladder is
  carried with both limbs of every compound condition and every threshold in figures; the single `overwrite` is
  written as retired and nothing else is; every variant parameter value is rendered at least once; and the
  authoring fields (`condition`, `resolved_by`, `effect`, factors' `baseline` / `evidence` / `cross_difficulty`)
  appear nowhere. No added business step, no pointer between documents, no task's world state written in as a
  policy fact.

## The defect that blocks the close-out

**KB-EXPLICIT RED — four of the five computation documents announce that a variation exists.**

The source keeps `extended_policies[].rule` (topic sentence plus variations) separate from
`extended_policies[].baseline.rule` (the standard method only). Five topic sentences from the full `rule` have
been carried into the baseline documents, and each of them asserts, beside the standard method, that the very
quantity the standard method sets to nothing is in fact taken, added or only partly applied:

| Document | Section | Sentence |
|---|---|---|
| `crossover_benefit_settlement_computation_cae09cc7` | 4. The yearly deductible | *"A yearly deductible is taken from that amount before the share is worked out. No yearly deductible is taken, the benefit carrying none."* |
| `premium_account_settlement_computation_2871445e` | 2. The monthly premium the policy is rated on | *"A reduction is then taken for the way the policyholder pays from the monthly premium the household discount leaves, … No reduction is taken from that monthly premium."* |
| `precoverage_line_restatement_computation_bab53e7e` | Which of them are restated | *"Only some of those lines are restated here. Every line that falls outside cover is restated."* |
| `precoverage_line_restatement_computation_bab53e7e` | What stays with the policyholder | *"Part of that liability is not restated, because the coverage that was in force on those days leaves the policyholder something of its own. The policyholder is left nothing, and the whole of the liability is restated."* |
| `overlap_premium_return_computation_7d397a4b` | 4. What is returned with the premium | *"Alongside the premium itself the plan returns the other rate components posted for the opening span, month by month. The premium alone is returned, and nothing is added for any other rate component."* |

Each tells a reader of the computation document alone that some rule outside it decides that quantity, and the
fourth states the reason a variation exists. Four of the five announce a factor one of these two tasks' scored
figures turns on (`payment_method_reduction` and `returned_rate_components` on task 0;
`travel_deductible_taken`, `lines_restated_here` and `other_coverage_retention` on task 1). The solution remains
unique and correct, which is why this is a dependency-form failure and not a runtime one.
`direct_benefit_repayment_computation_0cd18862` is clean on this point: its topic sentences name the quantity
without asserting that anything varies.

## Policy-side notes (reported; they do not change this skill's verdict)

Six findings originate on the policy side — the source's own prose does not fully determine its own `compute`,
or the source carries two descriptions of one quantity — and the documents render that prose faithfully. They are
set out with evidence in `0.md` (PS-1 to PS-3) and `1.md` (PS-4 to PS-6). The one the brief asked to be ruled on:

**PS-1, the renderer's lead about `medigap_ext_premium_account_settlement`, is a real defect and it is latent —
it does not bear on either task's scored solution.** `result` adds `current_span_value` to `arrears_charges`, and
the current billing period lies inside the arrears window on *every* tier, not only the fall-through — so a
charge standing for the current period is counted twice, the fall-through being merely the case where the two
terms coincide exactly. The published document states this and its worked example demonstrates it (114.71 +
114.71). But task 0's gold path avoids it twice over: `arrears_window_months` resolves to 12 (the policy has been
in force 15 months and two payments settled a billing period in full inside the window), so the fall-through is
not taken; and no charge stands for the current billing period at all — the last charges were posted 2026-06-01,
outside the three-month current span — so `current_span_value` comes from the rate and is disjoint from
`arrears_charges`. Nothing is double-counted, and 530.21 is unaffected. Task 1 does not use this computation.
**The step 2 loop does not need to be reopened on this account.**

## Files

| File | Contents |
|---|---|
| `audits/runtime_context/medicare_supplement_policy_desk/0.md` | frozen `blind_answer` + `gt_comparison`, task 0 |
| `audits/runtime_context/medicare_supplement_policy_desk/1.md` | frozen `blind_answer` + `gt_comparison`, task 1 |
| `audits/runtime_context/medicare_supplement_policy_desk/_freeze_r1.txt` | corpus hash and blind-answer hashes taken before the reveal |
| `audits/policy_kb/medicare_supplement_policy_desk/0.md` | `source_to_kb`, `kb_to_source`, `bijection_verdict`, `dependency_form`, task 0 |
| `audits/policy_kb/medicare_supplement_policy_desk/1.md` | the same, task 1 |

## Coverage statement

This audit covers the product `medigap` only. Cross-product contradictions are outside its detection range; the
one cross-product read this difficulty makes (the Ridgecrest Advantage specialist visit copay, reached from
`what_other_coverage_leaves_the_policyholder_581ca5d4`) was checked and resolves correctly in
`docs/advantage/professional_visit_cost_share_c01a8099`. Base-type products claimed by no difficulty are outside
scope entirely.

# revision_2 — closing record

Revision 1 above is preserved unmodified. Revision 2 is **verification, not a blind audit**: the auditor had
seen both tasks' GT when it was revealed at revision 1, and this round re-derived nothing blind.

## Scope, verified independently rather than accepted

`medigap.extended.yaml` is byte-identical (`sha256` first 16 = `9b11c3e10388e3a6`), so the policy revealed at
revision 1 stands and the `source_to_kb` scan did not need redoing. The corpus hash was reproduced exactly
(`ba95f929a24e09d1…`, sorted title+content). Exactly four of the 57 documents have an mtime later than the
revision-1 freeze, and they are exactly the four reported — all of role `baseline`. All 25 factor documents,
all 5 hubs, all 11 facets, all 11 base-policy documents and the clean reference
`direct_benefit_repayment_computation_0cd18862` are untouched. Both gates were re-run by the coordinator
(`DOCS OK`, `TRACEABILITY OK`) and, per Step 0, not by the auditor.

## Three part-verdicts per task, revision 2

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
|---|---|---|---|
| 0 — premium account settlement | **PASS** (r1 blind answer preserved; still holds) | **PASS** | **PASS** (was KB-EXPLICIT RED) |
| 1 — waiting foreign-travel crossover line | **PASS** (r1 blind answer preserved; still holds) | **PASS** | **PASS** (was KB-EXPLICIT RED) |

## The difficulty closes out

All M = 2 tasks have a frozen `blind_answer` and `gt_comparison`, a `source_to_kb` / `kb_to_source` scan and a
`dependency_form` scan, and all three parts now carry a PASS. Old revisions are traceable: revision 1 is intact
in every file and `_freeze_r1.txt` and `_freeze_r2.txt` record the corpus and source hashes at each round.

- Every normative atom of the structured source is entailed by the product's documents, with nothing unborne,
  nothing borne with changed meaning and no claim from outside the source. Re-checked at revision 2 in both
  directions: every `baseline.rule` sentence of all five extended policies is still carried (the eleven
  candidates my matcher flagged are all passive-voice de-implementations or hub-borne opening principles), and
  nothing was added back.
- Every prerequisite's prerequisite sentence stands verbatim, in its declared state form, in a document of the
  policy it blocks and in no other policy's — re-verified across all 57 documents.
- Every declared factor's ladder is carried in full, every tier exact, findable from the records its tier rests
  on — all 25 re-checked tier by tier, results identical to revision 1.
- No other problem's tool name, route or aggregated chain is stated anywhere: each of the five task tool names
  occurs in exactly one document, its own policy's hub, and the four changed documents name no tool, carry no
  prerequisite sentence and contain no pointer wording at all.
- Each of the five computation documents still yields a definite fall-back number on the real task worlds
  (0.00 on all four that bear on a scored figure), differing from every scored figure — so a solver who fails to
  find a factor still lands a definite wrong number, which is the property the revision-2 edits restore.

Gate lines on the final form: `DOCS OK` (57 docs, 67 quantitative keys, 3 prerequisite edges) and
`TRACEABILITY OK` (0.json, 1.json, 0 missing), as re-run by the coordinator and reproduced in the revision-2
brief.

## What revision 2 changed, and the judgement on it

The renderer removed eight topic sentences imported from each extended policy's full `rule` into its
computation document, and reworded two section headings; it kept seven. I verified each direction myself.

- **All five revision-1 REDs are closed**, and each section now states the standard method alone.
- **All three further traces the renderer found are real and correctly removed.** The third — *"Money already
  taken back is never taken back twice"* — rested on a reading of the source that I tested and confirmed: the
  sentence is in `medigap_ext_uncovered_day_line_restatement.rule` and **not** in its `baseline.rule`, while the
  parallel principle **is** a sentence of `medigap_ext_dual_coverage_premium_return.baseline.rule`. It is
  therefore rightly kept in the return document and removed from the restatement document. Nothing the source
  carries was dropped.
- **The criterion is sound, and stronger than inferred.** The renderer drew the name/assert boundary from the
  one clean document. I tested it against `baseline.rule` itself and found six mandatory baseline sentences of
  the form "name a quantity the standard method then sets to nothing" — e.g. *"What is restated is the recorded
  liability of the lines that fall outside cover, less what the coverage that was in force on those days leaves
  the policyholder…"*, in the same baseline as *"The standard method leaves the policyholder nothing."* A
  criterion banning that shape would make the baseline uncarriable. The boundary is therefore **forced by the
  source**, not merely inferred: what is forbidden is the same predicate affirmed and then denied, and any
  statement of why a variation exists.
- **None of the seven kept sentences announces a variation.** Each was judged against that failure mode
  individually; the table is in `0.md`. In particular `crossover_benefit_settlement_computation_cae09cc7` §5's
  retained *"What counts toward that deductible is measured from the claim record"* mentions neither
  restatements nor money recovered from the policyholder — the two kinds of entry its factor turns on.

Already settled at revision 1 and correctly left alone: the double count in
`premium_account_settlement_computation_2871445e`, including its 114.71 + 114.71 worked example, remains
rendered exactly as it was. It is a real source-layer property, latent on both gold paths, and not a rendering
defect.

The one revision-1 blind/GT divergence is confirmed **not** to be a findability problem: `balance_effect`
resolves to `overpayment` from three published sentences and one record field, with no inference from outside
the corpus. Nothing for the render layer.

## Policy-side notes carried forward unchanged

PS-1 to PS-3 (`0.md`) and PS-4 to PS-6 (`1.md`) are all source-side — the source's prose not fully determining
its own `compute`, or two descriptions of one quantity — and none is touched by these edits. They remain on
record for the policy layer and do not affect this skill's verdict.
