# Policy-KB audit — home_claim_settlement (product: home) — difficulty closing, round 1

- Auditor: erl-kb-doc-policy-audit sub-agent. Independent of the render agent and of the policy-side auditor.
- Visible corpus hash: `078ceb29ceffd68cffec4b47ca37f9cb9bad78ab42b61162b7da6506b27100f1` (67 docs).
- Blind answers were frozen at 2026-09-25T04:20:50Z. The source was revealed at 04:22:41Z. Blind-file hashes are recorded in each `gt_comparison`.
- contamination_disclosure: none for either task.

## Per-task verdicts

| Task | Runtime blind audit | Two-way scan | Dependency form | Overall |
|---|---|---|---|---|
| 0 | PASS | PASS | PASS | **PASS** |
| 1 | PASS | PASS | PASS | **PASS** |

## Observations (not RED)

- **O-1.** The settled-basis factor docs (other_structures_settled_basis_44e4c99a, contents_settled_basis_8ad091e9) gloss "the deductible absorbed" with referents ("those of the claim's other-structures settlement" / "the contents absorb on the claim") that are less precise than the source binding, which is the computed share (`os_ded` / `pp_ded`). Blind reading, source and GT agree, and the calculation sheets use the identical term for the computed share. A looser reading, taking the deductible recorded on the original acv_initial entry, is possible but not stated.

## Policy-side notes (outside this skill's verdict)

- **P-1.** The base `home_water_limitations.formula.mold_remaining` (term sublimit paid) is not declared superseded, while the extended mold ceiling uses a window of 12 months before the call. The KB renders both, as the source has them. Neither bites in task 1.
- **P-2.** Task 0's gold `find_home_claims` `necessity` text quotes a stale prerequisite wording. It is hidden and not scored.
- **P-3.** The mold baseline says the parts absorb the deductible "in their own order", which alludes to the retired base order clause.

## Closing checklist

- [x] Audit files correspond one-to-one with the tasks: `runtime_context/…/0.md`, `1.md` and `policy_kb/…/0.md`, `1.md`. This is round 1, so there are no prior revisions.
- [x] Every comparison section carries PASS.
- [x] Every normative atom of the difficulty's structured source (5 extended policies, 23 declared factors, every tier, the retired surface of all overwrites, and the governing base policies) is entailed by `docs/home`. Nothing is unborne, nothing is borne with changed meaning, and there is no claim from outside the source.
- [x] Each of the 3 prerequisite sentences stands verbatim, in state form, only in its blocked policy's hub. Every hop is resolvable from that sentence, the depended-on hub (which uses the same state words) and the records.
- [x] No other problem's tool name, route or aggregated chain appears anywhere.
- [x] Final-form gates were re-run by the auditor on 2026-09-25:
  - `check_docs.py env/env_0024_homeowners_insurance_carrier home` gave "[PASS] mechanical gates: …" and "DOCS OK" (docs=67, roles factor 24 / facet 12 / policy 21 / baseline 5 / hub 5, prerequisite edges=3).
  - `check_traceability.py …/tasks/home_claim_settlement` gave "0.json 20 0 True", "1.json 27 0 True" and "TRACEABILITY OK".

## Coverage limits (stated honestly)

- Cross-product contradictions are outside this skill's detection range. Sibling products were still being rendered during the audit, and KB_search showed some LandlordGuard, CondoGuard and RentGuard documents; none was used as a criterion.
- Home base-type content that this difficulty does not claim (billing, cancellation, renewal, endorsements and so on) was read only for the dependency-form scan and was not bijection-audited.
