# Closing checklist — pass_protection_desk / product `insure` (Pass and Trip Protection)

Audit skill: `erl-kb-doc-policy-audit`. M = 2. Auditor independent of the render author and of the policy-side auditor. No document, blueprint, task or runtime file was edited; the audit's only writes are the four files below plus this one.

## Part verdicts

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
| --- | --- | --- | --- |
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

Files: `audits/runtime_context/pass_protection_desk/{0,1}.md` (blind_answer frozen before any source-layer read, then gt_comparison) and `audits/policy_kb/pass_protection_desk/{0,1}.md` (source_to_kb, kb_to_source, bijection_verdict, dependency_form). Revision 1 for all four; no older revision exists to preserve.

## Close-out conditions

- The audit files correspond one-to-one with the two tasks, and every comparison section carries a PASS.
- Every normative atom of this difficulty's structured source is entailed by the product's 55 documents: the five extended policies' baseline rules, all 25 declared factor ladders tier by tier, the non-factor parts of each `rule`, all five task-tool contracts, and the ten base policies with their eligibility and evidence contracts and every per-plan parameter of all six plans — including the four plans and the many tiers no task in this difficulty exercises. Nothing is unborne, nothing is borne with changed meaning, and no claim appears from outside the source.
- All three declared `prerequisite` edges are carried: each prerequisite sentence stands verbatim, in its declared **state** form with its ordering connective and strength intact, in a document of the policy it blocks and in no other policy's; each is resolvable at the source's strength from that sentence, the depended-on policy's own rule and the records; and no depended-on document discloses who waits on it. `condition`, `resolved_by`, `effect`, and every factor's `baseline`, `evidence` and `cross_difficulty` appear nowhere.
- Every declared factor's ladder is carried in full, every tier exact, in its own factor document, findable from the words the records its tier rests on actually use; the fourteen whose tiers rest on another difficulty's records name the Season Pass Programme by its official name and the kinds of record they read.
- No other problem's tool name, no route and no aggregated chain is stated anywhere beyond those sentences and their same-form equivalents. Each of the five task tools is named exactly once, in its own policy's invocation block.
- The retired surface is exact: seven declared `overwrite` entries, seven retirements, each quoting its superseded clause verbatim and marking it no longer in force while preserving the plan figures it names; nothing retired that the source did not retire, nothing vanished, and the unnamed clauses of the same policies still stated as clauses in force.

## Gate record on the final form

No artifact was modified during this audit, so the form gated by the coordinator is the final form. The gate output supplied with the brief and cited rather than re-run (per the brief, the auditor runs neither script):

```
$ .venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/ski_resort_operator insure
🔎 DOCS gate  product=insure profile=extended docs=55 roles={'policy': 10, 'factor': 25, 'facet': 10, 'baseline': 5, 'hub': 5} content[min/mean/max]=1317/1956/3001
   required quantitative keys=75  task_tools=5  prerequisite edges=3
  [PASS] mechanical gates: structure, zero implementation leaks, tool fidelity, no workflow docs, non-directory hubs, private compute-binding coverage, quantitative coverage, every prerequisite sentence carried verbatim on its blocked side, no tool-name pointers or route scaffolding
  [MANUAL REQUIRED] normative claims <-> structured source semantic bijection; every hop resolvable at the source's strength from the prerequisite sentence, the depended-on docs and the records, no state-form sentence restated as an action, and no route stated beyond the sentences
DOCS OK

$ .venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py env/env_0004_ski_resort_operator/tasks/pass_protection_desk
task        copied  missing    ok
0.json          15        0  True
1.json          17        0  True
TRACEABILITY OK
```

The `[MANUAL REQUIRED]` line is what this audit answers, and it is answered PASS on both tasks.

## Verdict

**This difficulty's rendering passes the audit**: runtime blind audit PASS + full-domain two-way scan PASS + dependency-form scan PASS, on both tasks.

## Recorded honestly, not affecting the verdict

- **Policy-side notes** (the documents render the source's prose faithfully; the observations are about the source): numeric floors present in several `compute` expressions but absent from the prose they are basised on (`MX(1, …)` guards on instalments remaining, presentations due, term days, claimable days and the unearned-share denominator); two same-named "part of the term that has run" quantities anchored differently by the giving-up charge and the giving-up settlement; and a singular "the amount of the instalment so refused" in one ladder's `value` field against an `XSUM` over the season in its compute, which the document resolves correctly as the season total.
- **Coverage gaps, structural**: cross-product contradictions are outside this skill's detection range — two figures these computations read (a pass tier's scheduled instalment count and its day-use deduction) belong to the Season Pass Programme charter. The insure documents name that product and the kind of record correctly, which is all this skill requires of them. Separately, a base-type product claimed by no difficulty is outside this skill's scope entirely.
