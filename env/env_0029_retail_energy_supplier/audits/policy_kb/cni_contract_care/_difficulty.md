# Policy-KB audit closing — cni_contract_care (product cni)

## revision_1

| Task | Runtime blind audit | Full-domain two-way scan | Dependency-form scan |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

Closing checklist:
- Audit files one-to-one with tasks: `runtime_context/cni_contract_care/{0,1}.md`, `policy_kb/cni_contract_care/{0,1}.md`. First revision; no older revision exists. Blind answers carry a sha256 line appended before the reveal (2026-10-04T18:41:45Z); estimated freeze-time lines inside the blind text are noted as estimates in each `gt_comparison`.
- Every normative atom of `tasks/cni_contract_care/cni.extended.yaml` relevant to the seven extended policies (`cni_ext_termination_security`, `cni_ext_noticed_termination_damages`, `cni_ext_preflow_termination_damages`, `cni_ext_anniversary_security_review`, `cni_ext_contract_exit_damages`, `cni_ext_passthrough_fixed_price_rebill`, `cni_ext_passthrough_index_rebill`) and to their base policies is entailed by `docs/cni/`; no unborne atom, no changed meaning, no claim from outside the source.
- Five prerequisite sentences: each verbatim, in state form, in its blocked hub only (termination_security_remittance ×2, anniversary_security_review ×3); every hop resolvable from the sentence, the depended-on documents and the records.
- Every declared factor (6 + 6 + 4 + 6 + 6 + 4 + 4 = 36) has its own document with the full ladder; cross-product factors name Commercial Natural Gas Supply or Small Business Electricity Supply and the record kinds they read.
- All 15 overwrite entries (ten distinct superseded clauses) are carried as retired in a bearing document; no undeclared retirement.
- No tool name of another problem, route or aggregated chain anywhere.
- Gates re-run on the final form (read-only):
  - `.venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/env_0029_retail_energy_supplier cni` → "[PASS] mechanical gates: structure, zero implementation leaks, tool fidelity, no workflow docs, non-directory hubs, private compute-binding coverage, quantitative coverage, every prerequisite sentence carried verbatim on its blocked side, no tool-name pointers or route scaffolding" / "DOCS OK".
  - `.venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py env/env_0029_retail_energy_supplier/tasks/cni_contract_care` → "0.json 21 0 True" / "1.json 23 0 True" / "TRACEABILITY OK".

Policy-side notes carried to the policy layer (not KB verdicts): PS-1 termination-security baseline names "gas relationship relief" (source form); PS-2 combined-deposit ceiling in force but not applied by the security/review computes (untriggered); PS-3 variant parameters `etf_remaining_usage_basis` / `etf_preflow_basis` outlive their superseded clauses; PS-4 base 30-day pass-through notice clause beside the day-weighted price-in-force factor.

Coverage note: cross-product contradictions are outside this skill's range; base-type products claimed by no difficulty are outside scope.

**Difficulty verdict: PASS** (rendering of product cni for cni_contract_care passes the audit).
