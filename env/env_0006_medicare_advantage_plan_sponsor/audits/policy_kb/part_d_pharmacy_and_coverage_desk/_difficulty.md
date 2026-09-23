# KB-document audit closeout — part_d_pharmacy_and_coverage_desk (product `pdp`)

Closed at round 2, 2026-09-21T16:50:00+00:00. Corpus `d19f907d4be30972…`; charter `d0436e4d65dfe61e…`; `task_tools.py` `fb6f31940de52a89…`; base section byte-identical to `blueprint/products/pdp.yaml`.

## Three part-verdicts per task

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
| --- | --- | --- | --- |
| 0 — settling premium arrears | **PASS** (r1 blind, r2 verified) | **PASS** (r1) / **PASS** (r2) | **PASS** (r1, r2) |
| 1 — settling a held fill at the counter | **PASS** (r1 blind, r2 verified) | `KB-BIJECTION RED` (r1) → **PASS** (r2, closed) | **PASS** (r1, r2) |

## Difficulty closing checklist

- [x] Audit files correspond one-to-one with the tasks: `runtime_context/{0,1}.md` and `policy_kb/{0,1}.md`.
- [x] Old revisions traceable: revision 1 preserved verbatim in all four files; revision 2 appended, never rewritten.
- [x] Every comparison section carries a PASS at the current revision.
- [x] Every normative atom of this difficulty's structured source is entailed by the product's docs — 5 extended policies, 26 factors, 5 baselines, 15 base policies, all checked over their whole domain including untriggered branches.
- [x] Retired surface exact: 8 declared overwrites, 8 rendered retirements, one-to-one, no extra retirement and none missing; every `replaced_by` carried in force.
- [x] Every prerequisite's sentence stands verbatim, in its declared state form, in a document of the policy it blocks and in no other policy's — 3 of 3 edges.
- [x] Every hop resolvable at the source's strength from the sentence, the depended-on documents and the records; verified by blind derivation in round 1.
- [x] Every declared factor's ladder carried in full, every tier exact, thresholds in figures, findable from the records its tier rests on — including the two cross-product factors, which name `Employer and Union Group Retiree Plans` and `Supplemental Benefit Allowance Programmes` by their official display names.
- [x] No other problem's tool name, route or aggregated chain anywhere; 5 of 5 tools named only in their own hub.
- [x] Both gates re-run on the final form (output lines below).

```
$ .venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/env_0006_medicare_advantage_plan_sponsor pdp
🔎 DOCS gate  product=pdp profile=extended docs=63 roles={'factor': 26, 'policy': 15, 'hub': 5, 'facet': 12, 'baseline': 5} content[min/mean/max]=1282/2097/3305
   required quantitative keys=97  task_tools=5  prerequisite edges=3
  [PASS] mechanical gates: structure, zero implementation leaks, tool fidelity, no workflow docs, non-directory hubs, private compute-binding coverage, quantitative coverage, every prerequisite sentence carried verbatim on its blocked side, no tool-name pointers or route scaffolding
  [MANUAL REQUIRED] normative claims <-> structured source semantic bijection; every hop resolvable at the source's strength from the prerequisite sentence, the depended-on docs and the records, no state-form sentence restated as an action, and no route stated beyond the sentences
DOCS OK

$ .venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py env/env_0006_medicare_advantage_plan_sponsor/tasks/part_d_pharmacy_and_coverage_desk
🔎 TRACEABILITY gate  (2 tasks)
task        copied  missing    ok
0.json          18        0  True
1.json          23        0  True
TRACEABILITY OK
```

**This difficulty's rendering passes the audit.**

## Open policy-side notes, carried forward (they do not bear on this verdict)

1. `pdp_late_enrollment_penalty`: the base rule rounds "on the tier's rounding basis" (nearest ten cents on every variant) while `formula.monthly_penalty_amount` rounds to 2 decimal places. Unrendered, invisible at runtime, bears on neither task's scored value; the documents are definite and agree with the compute.
2. `parameter_schema` glosses for `mail_order_90_day_multiplier` / `retail_90_day_multiplier` in frozen base still read "Multiplier applied to the 30-day preferred retail cost share". This was the round-1 root cause. It is now consistent with the extended rule on every world, so it no longer produces a divergence — but it remains a gloss stated as an application rather than a description, and any future extended policy that multiplies a different base will reopen it.
3. Prose/compute looseness the KB faithfully inherits: "the coverage month's premium charge has stood posted" and "the evidence … held on the enrollment intake" where the compute reads `LATEST`. Neither bites in these worlds.
4. `what_the_member_hands_over_at_the_counter_d6b0f412` names "the multiplier" twice although its own defaults never apply one — one sentence base law, one from the extended `baseline.rule`. Both bound an operation rather than announce a variation; the fall-back number stays definite and different.

## Coverage statement

This audit covers only the product this difficulty claims, `pdp`. The `egwp` nil-MOOP facet examined under round 1's cross-product lead was tested and found inert for `pdp`; whether it is a defect of the `egwp` corpus belongs to the audit of the difficulty that claims `egwp`, and is outside this skill's scope here.
