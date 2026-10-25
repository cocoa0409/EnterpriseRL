# Renderer findings (verbatim final reply of agent acfb4ac383b91d756, saved by the coordinator)

I stopped before writing anything, as the coordinator notes require on a source mismatch. No documents and no staging directory were created, `check_docs.py` was not run, and nothing under `/tmp/erl0079_coord/` was touched.

The scan covered `env/env_0079_property_restoration_contractor/tasks/insurance_claim_services/claims.extended.yaml` and the `task_tools.py` beside it. Two mismatches, one confirmed and one at an edge, can't be rendered without inventing or dropping semantics.

**Finding 1 (stop): job and contract reads are not tied to this claim file (XF B7)**

The cross-product sums (`XSUM`, `XCOUNT`, `XLATEST`) read lines from every job of the insured, not just the one linked to this file. The scope wording doesn't rule out a second job or contract on another claim file. The base policy `claims_agg_multi_holding` itself says landlords, property managers and associations "often have several losses open across their properties", so this world can occur.

*1a. Rebuild reads in `claims_ext_credited_line_writeoff`*
- The rule says: "when the latest change order credit on the reconstruction contract was posted after the estimate was submitted and no additive change order charge was posted on the contract on or after that credit, every change order credit posted on the contract". The deductive change-order clause also says "removed from the contract".
- The compute reads every contract the insured holds:
  - `r_co: XSUM('rebuild', 'rebuild_payments', 'amount', event_type='rebuild_change_order_credit')`
  - `r_co_last: XLATEST('rebuild', 'rebuild_payments', 'posted_date', …, event_type='rebuild_change_order_credit')`
  - `r_add` and `r_add_last` work the same way on `rebuild_change_order_charge`.
- The scope ("…file whose insured holds exactly one water mitigation job linked to the file and on which no write-off has yet been posted") has no test on the number of reconstruction contracts.
- Where they differ:
  - The insured holds a second contract on another file that has change orders: the compute adds them, a reader of the rule does not.
  - The insured has no contract on this file but one on another file: the removed scope comes out non-zero, while `cp_signed`/`cw_cmult` read this file's missing contract.

*1b. Water reads in `claims_ext_regulated_scope_supplement`, `claims_ext_category_reassessment_supplement` and `claims_ext_credited_line_writeoff`*
- All three scope with "whose insured holds exactly one water mitigation job linked to the file". The natural reading is "exactly one of the water jobs linked to this file", which still allows other water jobs on other files.
- The compute sums water lines and credits across all the insured's water jobs, for example:
  - `rs_lead: XSUM('water', 'water_charges', 'amount', charge_code='lead_safe_setup')`
  - `sc_extr_qty`, `sc_tech_lines: XCOUNT('water', 'water_charges', charge_code='technician_labor')`, `sc_mover_days`
  - `cw_err`, `d_all`, `g_all`, `e_last`/`g_last`
- Where they differ: a second water job on another claim file. Its lines and credits enter the figure, though the rule says "the lines billed on the water job".
- `claims_ext_insured_depreciation_release` avoids this with "holds exactly one water mitigation job and exactly one reconstruction contract, both linked to the file".

**Finding 2 (stop, edge only): `claims_ext_insured_depreciation_release`, factor `supplement_depreciation_paid` (XF B1)**
- The rule says: "when the supplement carrier payments on the dwelling coverage reach the dwelling supplement approvals, the whole depreciation withheld on those approvals…; when they exceed the supplement approvals less their depreciation withheld but fall short of the approvals, the supplement payments less that figure…; otherwise nothing."
- The compute is: `rl_sup_released: rl_sup_wh2 if (rl_sup_amt > 0 and rl_sup_paid >= rl_sup_amt) else ((rl_sup_paid - (rl_sup_amt - rl_sup_wh2)) if rl_sup_paid > rl_sup_amt - rl_sup_wh2 else 0)`
- Where they differ: no dwelling supplement approval exists, but a dwelling carrier payment of type supplement is above zero. The rule gives 0.00, because the payments reach the zero approvals and the withheld amount is 0. The compute gives the whole supplement payment. The `rl_sup_amt > 0` condition never appears in the rule.

**Not a stop: XF A6 test T2 fails for two factors of `claims_ext_credited_line_writeoff`**
`water_line_pricing_basis` (`cw_wmult`) and `contract_scope_pricing_basis` (`cw_cmult`) only multiply the credit families. All of those families are 0 when their factors are at baseline. So with every other factor at baseline, neither pricing factor can move `result` in any world. This can be rendered as written; I'm raising it so it can go in the same rework.

**Checked and clean**
- Every `compute_basis` quote is verbatim in its rule (B6).
- Policy 2's water rate constants all equal the water charter's tier rates.
- Ladder text matches compute across the enums: property types, growth locations, water categories, the 7 equipment-day codes, and the Black Water tier names.
- Factor independence (A1): no factor reads another factor's binding.
- Every overwrite and its replacement text is correctly scoped (C1–C3).
- Rounding placement matches the rule sentences (B5), and the tool bodies match their docstrings (D1–D5).
- Of the remaining wording questions, three I would have pinned to the compute-consistent reading when rendering:
  - "Rate less rate" groupings: dimensionally, only quantity multiplied by the rate difference makes sense.
  - "One air scrubber for every air mover day billed": one per daily air-mover line, which is the water charter's own "equipment day" sense.
  - Policy 6's "dehumidifier days billed": the dehumidifier charge amounts.
- No computation document would have needed an input that only one factor uses. The baseline-only inputs not named in `baseline.rule` (build year, RRP and asbestos cutoffs, initial dwelling approval) each feed two or more factors, and would have stayed in covers only.
- No base-text defects to log.

**Suggested fixes**
- Reword the scope of policies 1–3 to policy 4's form, "holds exactly one water mitigation job, and that job is linked to the file".
- In policy 3, add a reconstruction-contract count test to the scope, or key the rebuild reads to this file's contract.
- In policy 4, either state the "some dwelling supplement approval exists" condition in the rule, or remove `rl_sup_amt > 0` from the compute.
