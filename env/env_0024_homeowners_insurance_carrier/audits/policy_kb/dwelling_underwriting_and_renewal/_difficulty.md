# KB-doc policy audit — closing checklist — dwelling_underwriting_and_renewal (product dwelling)

Round 1. Auditor: independent erl-kb-doc-policy-audit agent. Blind answers frozen 2026-09-25T04:29:34Z before any source-layer file was opened; source layer revealed afterwards.

## Per-task verdicts

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan | Files |
|---|---|---|---|---|
| 0 | KB-RUNTIME PASS | KB-BIJECTION PASS | KB-EXPLICIT PASS | runtime_context/…/0.md (freeze sha256 68ef627c…), policy_kb/…/0.md |
| 1 | KB-RUNTIME PASS | KB-BIJECTION PASS | KB-EXPLICIT PASS | runtime_context/…/1.md (freeze sha256 83750a2d…), policy_kb/…/1.md |

## Checklist

- [x] Audit files correspond one-to-one with tasks 0 and 1; no earlier revision existed (round 1); each blind_answer carries its freeze_record and was not edited after it.
- [x] Every normative atom of the seven extended policies (both tasks together cover all seven and all 33 declared factors) and of the base policies they govern is entailed by `docs/dwelling/`; nothing unborne, nothing changed in meaning, no claim without a source.
- [x] All five prerequisite sentences stand verbatim, state form, only in the blocked policy's hub (renewal_premium_payment_in_full_3b7421cf; renewal_indication_record_9a3f5746; current_term_pay_off_2206b1d5 ×3); every hop is resolvable from the sentence, the depended-on hub and the records; no other problem's tool name, route or aggregated chain anywhere.
- [x] Every factor ladder is carried in full, every tier exact, in its own factor document, findable from the record words its tier rests on; cross-product factors name HomeGuard Homeowners Policy, Larkspur Personal Umbrella Policy and FloodGuard Private Flood Policy by their official names.
- [x] Retired surface: the nine overwritten base clauses (1 occupancy, 4 renewal, 4 billing) are each carried as "no longer in force"; no clause is retired by the KB on its own.
- [x] Gates re-run on the final form (unchanged docs):

```
$ .venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/env_0024_homeowners_insurance_carrier dwelling
🔎 DOCS gate  product=dwelling profile=extended docs=70 roles={'facet': 11, 'policy': 12, 'factor': 33, 'hub': 7, 'baseline': 7} content[min/mean/max]=856/1716/3536
   required quantitative keys=134  task_tools=7  prerequisite edges=5
  [PASS] mechanical gates: structure, zero implementation leaks, tool fidelity, no workflow docs, non-directory hubs, private compute-binding coverage, quantitative coverage, every prerequisite sentence carried verbatim on its blocked side, no tool-name pointers or route scaffolding
  [MANUAL REQUIRED] normative claims <-> structured source semantic bijection; every hop resolvable at the source's strength from the prerequisite sentence, the depended-on docs and the records, no state-form sentence restated as an action, and no route stated beyond the sentences
DOCS OK
$ .venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py env/env_0024_homeowners_insurance_carrier/tasks/dwelling_underwriting_and_renewal
🔎 TRACEABILITY gate  (2 tasks)
task        copied  missing    ok
0.json          21        0  True
1.json          23        0  True
TRACEABILITY OK
```

## Policy-side notes (reported, not KB verdicts)

- N1 `parameter_schema.renewal_offer_lead_days` still describes the lead time as "the renewal is billed", a residue of the retired billing clause; rendered faithfully.
- N2 `parameter_schema.vacancy_permit_rate_pct` ("prorated over the permit days") and base `formula: vacancy_permit_charge` are not named in `overwrite`; rendered faithfully in vacancy_values_by_tier_a4c549d2; the charged-days document resolves the charge basis explicitly on the visible surface.
- N3 claim_cause_weighting and late_payment_surcharge are defined in the source over another factor's output; their documents name that quantity by necessity.
- N4 task tools round with Python `round()` rather than half-up (no effect at 2-decimal inputs).

## Coverage limits (stated, not covered)

- Cross-product contradictions are outside this skill's detection range (only the dwelling corpus is the criterion).
- The run.sh system background prompt was not supplied with the brief and was not read.
- Base-type products claimed by no difficulty are outside this audit's scope.

**Difficulty result: the rendering of dwelling_underwriting_and_renewal passes (all three parts PASS for both tasks).**
