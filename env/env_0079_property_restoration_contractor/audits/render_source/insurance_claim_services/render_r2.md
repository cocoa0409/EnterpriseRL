# Renderer findings (verbatim final reply of agent acfb4ac383b91d756, saved by the coordinator)

I stopped again before publishing: the round-2 rescan turned up one more rule-vs-compute mismatch, in `claims_ext_insured_depreciation_release`. Nothing has been published and `check_docs.py` was not run as a final gate. The coordinator gate was met: the last line of `_difficulty.md` reads `VERDICT revision_7: task0=PASS task1=PASS charter=CLEAN`.

**Round-1 items: both closed in the reworked source**
- **Finding 1a:** `claims_ext_credited_line_writeoff` now scopes "…and at most one reconstruction contract, which, when held, is linked to the file". The rebuild reads now match the rule's "the reconstruction contract". The policy was also restructured so the computation takes every credit and the factors narrow them; the rule and compute agree in every case I checked, including absent dates.
- **Finding 1b:** policies 1–3 now read "holds exactly one water mitigation job, and that job is linked to the file", which matches the cross-product sums.
- **Finding 2:** the compute is now `rl_sup_released: rl_sup_wh2 if rl_sup_paid >= rl_sup_amt else …`, without `rl_sup_amt > 0`. That matches the rule in the no-approval case.
- **T2 observation:** cleared. The credit families are no longer zero at baseline, so both pricing factors can move the result.

**New finding (stop): `claims_ext_insured_depreciation_release`, factor `code_holdback_cut_rule` (XF B1, coverage part)**
I missed this in round 1.
- The rule says: "The code holdback cut is set as follows: when the depreciation withheld on the file's supplement approvals is above the change order charges posted on the contract and the contract is final_invoiced or closed, the withheld amount above those charges; when that withheld amount is above those charges and the contract is substantially_complete, the whole depreciation withheld on the supplement approvals; otherwise nothing."
- The compute reads dwelling only: `rl_sup_wh: SUM('claims_approvals', 'depreciation_withheld', event_type='claims_scope_approval', approval_type='supplement', coverage_part='dwelling')`
- Where they differ: a contents-coverage supplement approval with depreciation withheld. Contents supplements are allowed on Public Adjuster Coordinated Claim Billing. The rule counts that withheld amount; the compute does not.
- Every other quantity in this policy names the coverage part explicitly ("every dwelling scope approval", "the dwelling supplement approvals", "on the dwelling coverage"). Rendering "dwelling" here would add a restriction the rule doesn't state.
- Suggested fix: change "the file's supplement approvals" to "the file's dwelling supplement approvals" in that sentence, in both places, and in the matching `compute_basis` quotes.

**What is on disk**
- In `env/env_0079_property_restoration_contractor/.doc_render_staging/claims/`: `render_plan.yaml` (fingerprinted on the current source) and 45 draft documents in `docs/`, unpublished.
- The 45 are the 8 tier facets, all 13 base-policy documents (with the 3 retired-clause registrations), and the hub, computation document and every factor document for policies 1–3.
- A partial run of `check_docs.py` on these, with the failures for the policies not yet rendered filtered out, showed no leak or structure failures in them.
- My temporary authoring scripts are removed.
- `docs/claims/` does not exist. Nothing outside my staging directory was touched.

Policies 4, 5 and 6 are not yet rendered (21 documents, 66 in all). The fix changes the source fingerprint, which voids this round's staging under the skill, so the next round starts again from Step 0. In practice only the code-holdback-cut factor document and policy 4's hub depend on the corrected sentence; the 45 staged drafts would need re-checking against the new source rather than rewriting.
