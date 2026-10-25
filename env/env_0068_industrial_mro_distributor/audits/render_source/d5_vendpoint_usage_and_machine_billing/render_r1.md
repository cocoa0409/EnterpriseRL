# Renderer source-scan findings — product vending, render round 1 (renderer agentId a9a6c7cd63e4ab52a)
Saved verbatim by the coordinator from the renderer's final report (the renderer stopped before writing any document; gate line read `VERDICT revision_4: task0=PASS task1=PASS charter=CLEAN`).

Every `compute_basis` quote, prerequisite sentence and overwrite clause is verbatim in its rule, and each superseded clause is verbatim in its base policy. No factor reads another factor's binding.

All findings are in `env/env_0068_industrial_mro_distributor/tasks/d5_vendpoint_usage_and_machine_billing/vending.extended.yaml`.

**A. Plain bindings that only one factor uses** (recipe point 1; the computation document would have to carry a factor's quantity)

1. `vending_ext_startup_item_return`: the plain bindings `units_loaded`, `units_vended`, `units_back` and `units_out` are read only by `stock_ledger` in factor `fill_level_shape`. Their quotes are pieces of the factor's sentence: "The item's stock ledger is its units loaded on restock visits, less its units vended, plus its units returned to the machine and credited for vend errors, less its units withdrawn and its units billed as shrink, over all of the machine's records".
2. `vending_ext_retired_item_vend_credit`: the plain binding `last_vend_date` is read only by `delay_days` in factor `credit_delay_share`. Its quote is the factor's own sentence: "The delay share follows the calendar days from the date of the latest vend to today".
3. `vending_ext_substitute_placement`: the plain bindings `avg_interval` (`retired_units / K('weeks_in_window') / P('restock_visits_per_week')`) and `trigger_fraction` are read only by `sized_usage` in factor `substitute_demand_basis`. The baseline (`sized_usage: retired_par`) never uses them. The reverse also holds: `retired_par` is a binding of that factor, yet it is the baseline's only quantity ("The substitute takes the retired item's par, the par on the retired item's selection entry carrying the highest planogram request reference.").
4. `vending_ext_substitute_par_setting`: the plain binding `add_date` is read only by `days_since_add` in factor `settling_demand_basis`. Its quote is that factor's first-tier condition: "fewer calendar days than the settling period have passed since the date of the substitute's add entry".

**B. Assembly sentences naming a factor's quantity, with the rule also defining the result a second, conflicting way** (recipe points 2 and 3)

In each policy the assembly binding belongs to the computation document. Its quote names the quantity a method factor decides, which the baseline rule never defines. The same rule also states the result unconditionally in its baseline sentence. So the computation document would have to name a factor quantity and hold two different definitions of one figure.

1. `vending_ext_startup_par_review`, binding `sized_units`: "To size the par, the allowances that apply are first added together and added to one, the interval usage is multiplied by that sum and then by each factor that applies…". "Interval usage" is decided by `demand_pattern_basis`. The rule also says "The par is the item's average per restock interval divided by the model's low-stock trigger percentage taken as a fraction of one hundred, rounded up to a whole unit."
2. `vending_ext_startup_item_return`, binding `result`: "To fix the start-up unit credit, the price is shaped by the fill level first and then multiplied by each share that applies…". It names `fill_level_shape`, and that factor is the only thing fixing the non-commuting order (subtract the overstock charge, then multiply). The rule also says "The start-up unit credit is the unit price of the item's latest vend, the price paid for the returned units, rounded half up to the cent."
3. `vending_ext_retired_item_vend_credit`, binding `result`: "The credit value is the units not dispensed multiplied by the unit price billed on the latest vend and by the late-find share with the shares that apply added to it…". "Units not dispensed" is `units_short`, decided by `dispense_unit_basis`. The rule also says "The credit value is the units of the latest vend multiplied by the unit price billed on it and by the late-find share, rounded half up to the cent."
4. `vending_ext_substitute_placement`, binding `sized_par`: "To fix the substitute's par, the sized usage is multiplied by one plus the allowance that applies and then by each share and factor that applies". "Sized usage" is decided by `substitute_demand_basis`. The rule also says "The substitute takes the retired item's par…".
5. `vending_ext_substitute_par_setting`, binding `sized_units`: "To fix the settling par, the interval usage is multiplied by one plus the allowance that applies and then by each share and factor that applies…". "Interval usage" is decided by `settling_demand_basis`. The rule also says "The par is the selection's average per restock interval divided by the model's low-stock trigger percentage taken as a fraction of one hundred, rounded up to a whole unit."

**C. A docstring claim the body lacks** (recipe point 8; minor)

The `resize_selection_par_58ce1bb4` docstring in `task_tools.py` says "The new par … applies from the next restock visit". The body only writes the selection entry and has no restock-visit effect.
