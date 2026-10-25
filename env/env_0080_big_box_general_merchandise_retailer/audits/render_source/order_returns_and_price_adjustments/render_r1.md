# Renderer scan-first STOP, order render round 1 (saved verbatim by the coordinator from renderer agent a1f20587fbc26e0b9's final reply; no docs written)

STOPPED: the order source has mismatches, so I wrote no documents for `order`.

The gate passed: `VERDICT revision_5: task0=PASS task1=PASS charter=CLEAN`. I then checked the structured source (`tasks/order_returns_and_price_adjustments/order.extended.yaml` and `task_tools.py`) against every point of XF_recipe.md. Two things checked out:
- Every `compute_basis` quote, prerequisite sentence, `replaced_by` and baseline rule appears word for word in its policy's rule.
- Every `superseded_clause` appears word for word in its base rule.

**Mismatches (render stopped on these)**

1. **XF 16, a `replaced_by` drops in-force content.** In `order_ext_drive_up_return_refund.overwrite[0]` (base `order_returns`), the retired clause reads "…rounded half up to the cent, less restocking_fee_pct_changed_mind percent **where the reason is changed_mind** and the class is in restocking_fee_classes." The `replaced_by` restates it for out-of-scope returns as "…less the program's changed-mind restocking percentage where the class is one of the program's restocking classes." The reason condition is gone.
   - Failure case: a *defective* return of a large-items line on a Scheduled Large-Item Delivery order (restocking classes [large_items], 15.0) would have 15% withheld under the in-force wording. The base rule withholds 0.
   - Fix: restore "where the reason is changed_mind and" in the `replaced_by` and in the matching sentence at the end of the rule.

2. **XF 3, quantities that only one factor uses are bound to no factor.** In `order_ext_replacement_haul_away_credit`, the plain bindings `haul_standard` and `haul_items` are read only by `credited_haul` (factor `credited_haul_basis`). Their defining sentence ("The credited haul-away … counts the old items booked as the haul-away charge before benefits divided by the program's haul-away fee per item…") sits inside that factor's schedule. Yet the factor's `bindings` are only `[matched_settlements, credited_haul]`.
   - Consequence: the gate requires the computation document to claim every non-factor binding, so it would have to define an old-item count its own calculation never uses.
   - Fix: add `haul_standard` and `haul_items` to `credited_haul_basis.bindings`.

3. **XF 4, a factor-owned count is read by the standard method.** In `order_ext_late_change_fee`, `own_requests` belongs to factor `own_requests_surcharge` (its `compute_basis` quotes that factor's schedule sentence). The non-factor `free_reschedule` test also reads it ("…while the customer's confirmed reschedule requests already on the order are fewer than the program's free reschedules is a free reschedule").
   - Consequence: the computation document would depend on a quantity the factor document owns.
   - Fix: make `own_requests` a plain binding, defined once in the rule, that both the free-reschedule test and the factor read.

4. **XF 12/2, the late-change fee has two readings.** Same policy. The rule reads "The standard late-change fee is the program's late cancellation fee", then "The late-change fee adds up every charge and surcharge the schedules below give…". The notice-charge schedule's one-day-ahead tier is also the late cancellation fee, and the `notice_charge` baseline is `P('late_cancel_fee_usd')`. Nothing generic fixes whether the notice charge *replaces* the standard late cancellation fee or is *added* to it (49.00 vs 98.00 one day ahead).
   - The sibling policies settle this in their wording ("that standard fifth plus every extra percentage"; "the rate the lateness schedule gives plus…").
   - Fix: word the baseline rule as the standard notice charge, e.g. "The standard late-change notice charge is the program's late cancellation fee…", so the computation document and the factor document share one business noun.

5. **XF 24, a tool docstring claims a check the body doesn't make.** `reschedule_large_item_delivery_d930ab59` says `new_scheduled_date` "must be a valid calendar date". `_Money.is_date` only checks the shape, month 1–12 and day 1–31, so a date like 2026-02-30 is accepted. This is minor; fix either the body or the docstring wording.

**Observation, not a blocker:** `order_ext_late_express_credit`'s combining sentence "the late-express credit percentage is the rate the lateness schedule gives plus every extra percentage the other schedules give" names one factor's quantity. That's against XF 2 as written. But the same "the X the schedules give" pattern appears in the drive-up ("the basis the schedules below give") and replacement haul-away ("the amount the schedules name as the credited haul-away") rules, and those passed the policy audit, so I didn't treat it as a stop item.

Nothing was written under `docs/order/`, no staging directory was created, and the scratch directory I made is removed. Gate output for the order product:

No docs under env/env_0080_big_box_general_merchandise_retailer/docs/order
