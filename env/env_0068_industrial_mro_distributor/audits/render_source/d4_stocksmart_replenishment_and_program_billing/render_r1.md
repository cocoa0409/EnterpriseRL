# Renderer source-scan findings — product vmi, render round 1 (renderer agentId ad58c5b53d053479f)
Saved verbatim by the coordinator from the renderer's final report (the renderer stopped before writing any document).
Source: tasks/d4_stocksmart_replenishment_and_program_billing/vmi.extended.yaml (sha256 a838d492…), task_tools.py (805a54d8…).

**What passed the scan.** All `compute_basis` quotes are verbatim in their rules. Every prerequisite sentence and overwrite `replaced_by` appears verbatim in its rule. No factor reads another factor's binding. Rounding sentences match where RND sits in each compute. Tool docstrings claim only what the tool bodies do and carry no example values.

**Defects.** All are in `env/env_0068_industrial_mro_distributor/tasks/d4_stocksmart_replenishment_and_program_billing/vmi.extended.yaml`.

1. **Rule wording allows a second reading of the compute (XF 3/9 class).** Policy `vmi_ext_consigned_reorder_point`, factor `demand_rate`, binding `daily_usage`, middle tier.
   - Rule: "where it had net vends in each of those months and its highest month is 1.15 times its lowest or more but less than 1.4 times, its daily usage is half of its highest month plus one third of its net vends of the last three months, divided by 30"
   - Compute: `(peak_month + net_3m / K('months_in_window')) * K('half') / K('month_days')`, which halves the sum.
   - The same charter uses "half of" to apply only to the next term: in `vmi_ext_vended_item_fill_level`, "the latest month plus half of the rise" means latest plus half the rise. Read that way, this sentence halves only the highest month.
   - Example with monthly net vends of 23, 20 and 22 (total 65): the compute gives 0.744444 a day; the other reading gives 1.105556 a day.

2. **Missing branch when there is no customer-requested removal (XF 9, rule vs compute).** Policy `vmi_ext_opening_consignment`, bindings `removal_machine`, `removal_on`, `same_day_item_removals` and `result`.
   - Rule: "The demand machine is the machine of the customer's most recent VendPoint selection removal of the transferred item made at the customer's request; where two or more such removals of the item carry that most recent date, no opening stock is set under this schedule."
   - Nothing covers the case where no such removal exists. The compute's `same_day_item_removals == 1` guard returns 0 there.
   - The rule's scope ("an item taken out of one of the customer's VendPoint machines") still covers a Corbett-initiated slow-mover removal; the vending charter books those with change_source corbett.
   - A reader in that case finds no vend at the demand machine. Factor `trial_level` then sets the opening level to the reorder point ("an item with no vend there counts as having every vend below three months"). That gives a nonzero opening stock where the compute gives 0.
   - **Same omission, lower impact:** `vmi_ext_consigned_reorder_point` says "where two or more such removals of the item carry that most recent date, no reorder point is set under this schedule" and also lacks an "or there is none" branch. Here the numbers happen to agree (zero vends gives 0), but the case is still unstated. By contrast, `vmi_ext_vended_item_fill_level` does say "or the customer has none".

3. **Tie on the same date not handled (XF 9).** Policy `vmi_ext_conversion_reorder_point`, factor `value_class`, binding `contract_price`.
   - Compute: `XLATEST('pricing','pricing_items','contract_unit_price', date_field='effective_date', sku=conv_item)`.
   - Rule: "the contract unit price on its latest price line in the customer's agreement (zero where it has none)". It doesn't say what happens when two price lines share the latest effective date; `XLATEST` then takes whichever row it reads first.
   - The sibling policy `vmi_ext_hold_converted_fill` explicitly excludes "two price lines of its latest effective date", so the author treats such ties as possible.

4. **Possible issue, your call: a restriction in the rule that the compute ignores (near XF 10).** Policy `vmi_ext_opening_consignment`.
   - Rule: "The opening stock is placed only while the program's consigned stock value, with the opening stock added, stays at or below the consigned value cap of the program's tier."
   - Neither `result` nor any eligibility enforces this, so near the cap the rule says "don't place" while the compute still returns a quantity.
   - It only matters if a seeded program sits near its cap, which I couldn't check without reading the task files.
