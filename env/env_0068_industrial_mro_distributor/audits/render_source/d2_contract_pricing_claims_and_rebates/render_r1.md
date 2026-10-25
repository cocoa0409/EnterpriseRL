# Renderer source-scan findings — product pricing, render round 1 (renderer agentId aa6c1f00b6ecad95e)
Saved verbatim by the coordinator from the renderer's final report (the renderer stopped before writing any document).
Source scanned: tasks/d2_contract_pricing_claims_and_rebates/pricing.extended.yaml (sha256 c19bb902…), task_tools.py (063dbb2a…).

**Checks that came back clean, all seven extended policies:**
- Every compute_basis quote, baseline-rule sentence, prerequisite sentence and replaced_by text appears verbatim in its rule. Every superseded clause appears verbatim in its base rule.
- No factor reads another factor's binding. Only plain assembly bindings (`result`, `relief_total`, `holds`, `allowance`) read factor outputs.
- The month and day counts and the "recorded first" tie rule match `MONTHS`/`DAYS`/`LATEST`, and the `within_months` windows match "less than N whole months before the handling date".
- No two overwrites retire the same base clause.
- Every tool docstring effect exists in the tool body, and no docstring carries an example value.

**Findings** (all in `env/env_0068_industrial_mro_distributor/tasks/d2_contract_pricing_claims_and_rebates/pricing.extended.yaml`):

- **F1: rounding against the minimum (`pricing_ext_final_rebate_check`, binding `result`).**
  - Rule: "The final check is never below 0.00 and is rounded half up to the cent once, on the final figure." / "A final check below rebate_min_payout_usd is not issued and the balance carries forward." / "…subtracted once from the unpaid rebate balance before that floor, that rounding and that minimum are applied."
  - Compute: `result: "RND(in_scope * check_amt, 2) if check_amt >= P('rebate_min_payout_usd') else 0"`.
  - The rule tests the minimum on the rounded check (floor, then rounding, then minimum). The compute tests it on the unrounded `check_amt` and rounds afterwards. For example, an unrounded check of 99.996 against a 100.00 minimum is issued as 100.00 under the rule but returns 0 under the compute.

- **F2: missing branch (`pricing_ext_substitute_claim`, binding `carry_pct`).**
  - Rule: "an invoice whose payments, earned discount and applied credit memos cover its amount, with its latest payment carry_long_days or more days before the handling date, takes carry_long_pct percent; one covered with its latest payment fewer days before takes carry_short_pct percent; an invoice not yet covered takes no credit."
  - Compute: `"... if (inv_amount > 0 and inv_paid >= inv_amount - 0.005 and last_pay and DAYS(last_pay, NOW) >= ...) else (K('carry_short_pct') if (... and last_pay) else 0)"`.
  - An invoice fully covered by its earned discount and credit memos, with no payment on record, gets 0 from the compute. The rule assigns that case no tier, so the KB could not state it.

- **F3: scope mismatch (`pricing_ext_open_claim_decision`, bindings `item_lines`, `in_scope`, `add_cost`, `add_list`).**
  - Rule: "the item's only earlier price line is the line that added it (its new-item line)".
  - Compute: `item_lines: "COUNT('pricing_items', sku=clm_sku)"`, with `in_scope` requiring `item_lines == 2`. Meanwhile `add_cost`/`add_list` filter on `change_reason='new_item'`.
  - Consider an item added by a discontinued_substitute line and then escalated. The compute keeps it in scope, sets `add_cost = 0`, so `cost_pct = 0` and the price equals the prior unit price. The rule either excludes the item or, if the substitute line counts as the adding line, measures from that line.

- **F4: ambiguous wording (`pricing_ext_open_claim_decision`, decision sentence; not computed, but it drives the `outcome` enum).**
  - Rule: "The decision is referred_to_pricing_desk when the claimed quantity times the billed unit price less that unit price exceeds the tier's price_claim_desk_authority_usd".
  - This can be read as quantity times the difference, or as (quantity times billed price) less the unit price. A renderer would have to choose a reading the source doesn't fix.

- **F5: zero-count branch, latent (`pricing_ext_return_clawback`, bindings `ret_count`, `freq_share`).**
  - Rule: "…how many return receipt lines the customer's ship-tos received less than freq_window_months whole months before the handling date, this return included: one such line carries first_return_share, two to occasional_max lines carry occasional_return_share, and more lines carry a frequency share of 1."
  - Compute: `freq_share: "K('first_return_share') if ret_count <= 1 ..."`.
  - Zero lines in the window gets first_return_share from the compute. The rule has no zero tier. This happens when an in-scope return was received more than 12 months ago, which requires the latest accrual to be that old.

- **F6: scope mismatch, latent (`pricing_ext_discontinued_closeout`, binding `in_scope`).**
  - Rule: "This policy records the close-out of a contract item the manufacturer discontinued: the item of the latest backorder on the customer's ship-tos, when that backorder was filled with a Corbett-approved substitute of another item number and the agreement carries no removal line for the item yet".
  - Compute: `in_scope: "1 if (bo_sku and fill_sku and fill_sku != bo_sku and disc_date and ended == 0) else 0"`.
  - The compute never checks that the backordered item has a contract price line. A non-contract item filled with a substitute is in scope with a close-out price of 0.0000, where the rule would not close it out.
