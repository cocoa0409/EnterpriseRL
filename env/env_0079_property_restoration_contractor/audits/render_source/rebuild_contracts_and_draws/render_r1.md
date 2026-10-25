# Renderer findings (verbatim final reply of agent a2011b9cd3ba4cead, saved by the coordinator)

I stopped before writing anything. Scanning the rebuild extended yaml and its task_tools.py against XF_recipe.md and your two extra rules turned up source-side problems that I can't render without inventing or dropping meaning. No staging directory or documents were created, and check_docs.py was not run, so there is no DOCS OK line and no document count.

Source: `env/env_0079_property_restoration_contractor/tasks/rebuild_contracts_and_draws/rebuild.extended.yaml`. These checks passed: every compute_basis quote and prerequisite sentence is verbatim in its rule, every superseded clause is verbatim in its base policy, and no factor id is a substring of a tool name. The tool bodies match their docstrings.

## Blocking findings

**1. Edge-of-domain amount, carrier-priced line rounded up (`rebuild_ext_change_order_signature`).** This is the case you asked about, and it is a real source mismatch.
- Rule: "the carrier's approved unit price, which is the amount the carrier approved on that supplement divided by the quantity written on the proposal".
- Rule: "a drywall line is billed in whole sheets, the quantity written on the proposal rounded up to the next whole multiple of the drywall sheet area; a carpenter_labor or painter_labor line is billed at the greater of the hours written on the proposal and the minimum labor charge hours".
- Compute: `co_unit_price: up_approved / co_qty …` combined with `billed_qty` (ceiling to 32 sq ft; at least 2 hours).
- Example: an insurance_scope drywall line with 4 sq ft written and 20.00 approved gives 5.00/sq ft × 32 = 160.00 before overhead and profit, which is 8× the carrier approval. A labor line with 0.5 h written and 40.00 approved gives 80.00/h × 2 h = 160.00, which is 4×.
- In real practice the carrier's approved supplement amount is what gets billed for that scope. Whole-sheet and minimum-hour billing apply to the company's own price-list lines, not on top of the carrier's per-unit price.
- The same inflated price carries into `rebuild_ext_deductive_signature`.

**2. A computation document would list inputs only one factor uses (`rebuild_ext_overdue_draw_charge`).**
- `baseline.rule` contains "Unless a rule below sets them otherwise, the chargeable days of the fee period and the days at the current balance are each the fee period days." That is an exception hint, and it names two factor quantities.
- The non-factor binding `charge_basis` ("The balance the charge is figured on is the draw's balance-days … those beyond the days at the current balance are counted at the balance before the payments posted toward the draw within the past month…") names both factor quantities.
- It also reads `bd_recent_paid`, which only moves the result when the current-days factor (`ov_current_days`) is below 30.
- The non-factor binding `od_due` (basis: "the days since the due date less the grace days") is read only by the charge-days factor (`ov_charge_days`).
- So the computation document would have to list the due date and the past-month payments, each used by only one factor.

**3. The rule doesn't match the compute on unit price (`rebuild_ext_deductive_signature`).**
- Baseline and the "otherwise" tier say: "The credit unit price is the tier's rate for the scope code."
- The compute `dc_tier_rate` falls back to `dc_written_price` for scope codes that have no tier rate.
- Example: a deductive `material_escalation` line has no tier rate, so the rule gives no price while the compute uses the written price.
- The read sentence "…its scope code, the quantity written on it and the unit price written on it" also puts the written price into the computation document, although the rule only uses it in the price factor's (`dc_carrier_price`) upgrade tier.

**4. Wrong amount when two records exist (`rebuild_ext_deductive_signature`).**
- Rule: "the amount approved on that supplement divided by the quantity of the signed insurance_scope change orders of that scope code".
- When two signed insurance_scope change orders of the same scope name different supplements, "that supplement" has no single referent. The compute takes the latest one's amount (`cp_supplement`) over the summed quantity (`cp_billed_qty`).
- Example: two drywall change orders of 100 sq ft, each approved at 300.00, give a credit unit price of 1.50 instead of 3.00.

**5. The rule is broader than the compute and ladder (`rebuild_ext_change_order_signature`).**
- Rule: "for an owner_upgrade change order, the owner's selected unit price written on the proposal less the tier's selection allowance for its line".
- The compute and the ladder apply this only to flooring, cabinet and fixture upgrade lines.
- The schema's description of `co_type` allows owner_upgrade for "added owner work" (for example, tile_install). For that case the rule subtracts an allowance that doesn't exist, while the compute uses the tier rate.

**6. An overwrite drops a rule still in force (`rebuild_ext_final_draw`, overwrite #3, and similarly #2).**
- The retired clause says the release draw is requested "once the tier's retainage release days have passed after substantial completion".
- The replacement text only says "once released".
- As a result, `retainage_release_days` has no rule in force anywhere.

**7. Texas retention never ends (`rebuild_ext_overdue_draw_charge`, `rebuild_ext_draw_payoff`).**
- The overdue rule says "So for a Texas property, … the Texas owner retention percentage of the draw's requested amount is set against the balance".
- The payoff rule says "… is held back" and "a customer-funded draw is paid in full when all of it but the statutory retention has been paid".
- Neither has a time limit, although both cite "until the Texas statutory retention days after the work is completed". The final draw rule does apply the 30-day limit.
- Example: a Texas customer-funded final draw paid 50 days after substantial completion still has 10% held back and still counts as paid in full.

**8. Zero-amount payment (`rebuild_ext_draw_payoff`).**
- "a result below zero is paid as zero", together with "the draw counts as paid in full once that payment is posted".
- The carrier-pending set-aside has no cap: it is the claim-wide unreleased depreciation plus unpaid supplements. When it is large enough, the rule calls for a 0.00 payment.
- The schema says a payment amount is "positive". The draw would also count as paid with nothing paid, and work would resume.

**9. The same charge is collected twice.**
- Payoff, overdue charges: "while work on the contract is suspended … the payment carries every overdue draw charge on the contract". This includes charges on earlier draws that an earlier payment already carried.
- Payoff, remobilization tier 2: it carries again a remobilization fee that an earlier payment already carried under tier 1.
- Final draw, self-pay pass-through: "every charge line other than the contract_sum and change_order lines". This bills overdue and remobilization lines again after payoff payments have already carried them.

## Lesser findings
- **Overdue charge rounds to zero:** a positive chargeable balance under about 0.34 rounds to a 0.00 charge, which the rule says is still owed. The charges schema requires a positive amount, and the payoff prerequisite requires a charge row for that month.
- **Rounding sentence lost:** overwrite #2 of the additive change order policy retires the base rounding sentence for all change orders but restores it only for additive ones. Deductive change orders priced under the base rule (more than one proposal pending) have no rounding rule in force.
- **Floor not in the rule:** the final draw's depreciation hold is floored at zero in the compute (`MX(0, …)`), but the rule states no floor.
- **Two payment tiers both apply:** for the overdue charge's current-days count, when there is an earlier payment within the month and another on the charge date, both tiers' text applies. The rule gives no precedence; the compute uses tier 2.
- **Fixable while rendering:** the additive change order policy's read sentence lists "the supplement it names", which only the price factor uses. I can split that sentence across documents without losing meaning.
- **Frozen base:** I found no base text defect worth logging.

Nothing was written under `env/env_0079_property_restoration_contractor/docs/rebuild/` or `.doc_render_staging/`, and no files were changed anywhere.
