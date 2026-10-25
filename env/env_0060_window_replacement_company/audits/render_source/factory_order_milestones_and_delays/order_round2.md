# Render-source findings — product `order` (Factory Production Orders), round 2

Source: `order.extended.yaml` sha256 `3f12b81799f4f69c038e01718eb6d52d8b13d464e48c17da1d1dab1e47e4d0da`,
`task_tools.py` sha256 `7a329df922ec271e969f68dc7937b852c5a9e85b22328a58dbd8011fe858d940` (unchanged).
Upstream gate: policy re-audit revision_3, task 0 PASS and task 1 PASS.

## Round-1 items

- **F-1 (build-stage share, undefined branch): closed at source.** The rule now reads the stage "from the checkpoints
  that cover every unit on the order (a checkpoint for remade or replacement units alone does not count)", with an
  exhaustive else-chain ("...; otherwise, when the most recent such glass received checkpoint is dated on or before
  the remake date, 70 percent is due; otherwise 40 percent is due"). The compute (`LATEST(..., unit_count=F('unit_count'))`
  plus the same else-chain) agrees with it. The factor document has been re-rendered from the rule.

## Source changes and what was re-rendered

- `order_ext_customer_remake_charge` / `build_stage_share`: re-rendered (`build_stage_share_of_remake_charges_fa93f043.json`).
- `order_ext_branch_storage_fee` / `long_storage_schedule`: the single-week tier is now a one-bay minimum ("the weekly
  storage rate times the larger of 4 units and the units on the order"), and the compute is `rate * MX(K('bay_units'),
  F('unit_count'))`, which matches the rule. Re-rendered (`long_stay_and_single_week_storage_pricing_3e8c89d3.json`).
- `order_ext_on_time_guarantee_claim`: only the prerequisite edge's `effect` (an authoring field, never published)
  changed. No document was affected.
- Base section, variants, the other policies and the tools are unchanged, so the other 67 documents were kept as they were.

## Round-2 checks

- Every `compute_basis` quote, baseline rule, `replaced_by` and `policy_source` was re-verified as verbatim in its rule.
- **No new source mismatch was found.**
- Note (already logged by the policy auditor as R3-G1, not a new finding): the `build_stage_share` ladder text for the 40%
  tier ("neither full-order checkpoint is dated on or before the remake date") is narrower than the rule's "otherwise".
  The rule and compute agree, so the document follows the rule's else-chain.
