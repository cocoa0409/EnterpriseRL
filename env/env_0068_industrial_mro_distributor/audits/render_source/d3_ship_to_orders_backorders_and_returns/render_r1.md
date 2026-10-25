# Renderer source-scan findings — product order, render round 1 (renderer agentId a3e6a75d902fde435)
Saved verbatim by the coordinator from the renderer's final report (the renderer stopped before writing any document).
Source checked: `env/env_0068_industrial_mro_distributor/tasks/d3_ship_to_orders_backorders_and_returns/order.extended.yaml` (sha256 e80ac6f1…), task_tools.py (aa4a300d…).

**What passed the mechanical sweep:**
- Every `compute_basis` quote appears word for word in its rule.
- Every `baseline.rule` sentence is in its rule.
- Every superseded clause appears in its base rule, and every `replaced_by` is in the extended rule.
- Both prerequisite sentences are in their blocked policy's rule.
- Rounding sentences match where rounding sits in the compute.
- The tool docstrings match the tool bodies.

**Findings:**

1. **Rule says one machine, compute picks one at random (XF9 / XF13), `order_ext_requested_move_up`.**
   - Rule: "the machine read being the one placement whose ship_to_id is the ship-to" and "VendPoint usage counts … in full where the machine standing at the ship-to is active, at vending_idle_share_pct percent where it is suspended or removal_pending, and not at all otherwise."
   - Compute: `site_machine_id: CFIELD('vending','vending_machine_id', ship_to_id=HID)` and `site_machine_status: CFIELD('vending','status', ship_to_id=HID)`. CFIELD returns the first matching holding, with no status filter.
   - The vending charter (`vending_agg_multi_holding`) says "A customer may hold any number of VendPoint machines, including several at one ship-to". A removed machine also keeps its ship_to_id.
   - So with two or more placements, the rule has no answer and the compute takes whichever row comes first.

2. **Compute can read a closed program the rule excludes (XF9), `order_ext_reactivation_level`.**
   - Rule: "two drops are taken back where the program serving the ship-to is active as StockSmart Onsite Storeroom, one where it is active at any other StockSmart tier, and none where the ship-to has no active program."
   - Compute: `program_status_now: CFIELD('vmi','status', ship_to_id=HID)` and `program_tier_now: CFIELD('vmi','variant_name', ship_to_id=HID)`, again with no status filter.
   - The VMI rule only stops a second program while one is enrolled, active, paused or terminating. A closed program and a newly active one can therefore both sit at the same ship-to.
   - If the closed row comes first, the compute gives 0 drops taken back where the rule gives 2 or 1. The stock-rotation policy filters `status='active'` for the same read; this one does not.

3. **Vending usage sits in the standard calculation but only one factor uses it (XF1 and XF2), `order_ext_requested_move_up`.**
   - `site_machine_id`, `vend_12` and `vend_6` are not listed as bindings of factor `vending_counted`, which lists only `[site_machine_status, vend_share]`. So the computation document would have to claim them.
   - But the standard vending share is `vend_share: "0"`, so vending usage has no effect without that factor. That makes them quantities only one factor uses. Compare `review_dropship_share`, which does own `dropship_12` and `dropship_6`.
   - The combination sentence also names that factor's quantity: "The counted site spend of each period is its own merchandise plus the part of the vending usage of the same months that counts" (compute binding `counted_site_12: own_12 + vend_12 * vend_share / 100`).
   - Neither of these sentences is in `baseline.rule`. A computation document that claims these bindings cannot stay silent about vending and still render them.

4. **Six-month figures are defined only by one method factor, yet other factor documents must refer to them (XF1 and XF2).**
   - Anniversary review: `spend_6` and `counted_6` are plain bindings. Their only definition is inside the `review_tenure_basis` sentence ("the six-month figure being the same merchandise less return credits over the lines within the 6 months of the review date"). They are used only by that factor's tiers through `review_spend` (its standard tier is `review_basis: "0"`).
   - The drop-ship and will-call factors still have to say their uncounted part "is taken out of the twelve-month and the six-month spend, each over its own months" (`dropship_6`, `willcall_6` → `counted_6`).
   - Requested move-up has the same shape. `own_6` and `counted_site_6` are defined only in the "six-month site spend" sentence, used only by `site_ordering_basis` tier 1, and the vending factor must say usage "counts in the site spend of each period".
   - So the drop-ship, will-call and vending documents would each name a quantity that only another factor's document defines.

5. **Order of the drop take-back versus halving is not fixed (XF3), `order_ext_reactivation_level`. Lower confidence.**
   - Compute: `drops_added: MX(0, dormancy + route + payment - program_takeback)`, then `drops_total: int(drops_added / 2)` for long tenure. The take-back is applied before halving.
   - Rule: "The level drops a reactivation carries are added together, the total taken as never below zero, and that total, after any adjustment made to the total itself…" alongside "A StockSmart program still serving the ship-to takes drops back".
   - The rule never says whether drops taken back form part of the added total or apply after the tenure adjustment. These do not commute: with 4 drops and 2 taken back, take-back first gives (4 − 2) / 2 = 1, while halving first gives 4 / 2 − 2 = 0.
