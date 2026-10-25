# Source mismatches reported by the mobility renderer (agent aa29780fb27f9b553), round 1 — verbatim

1. **A factor tier reads another factor's binding** (`mobility_ext_kept_chair_adjustment`). `down_rate: ... (K('day_manual_courier') if (P('equipment_type') == 'manual' and courier_set >= 1) else 0)` reads `courier_set`. But `courier_set` is declared as a binding of factor `fee_return` (`bindings: ['adj_loaners', 'courier_set', 'fee_ret']`), not of `down_rate_tier` (`['home_set2', 'down_rate']`).

2. **A non-factor binding is built from two factors' outputs plus a constant the baseline never states.**
   - **Cash refund:** `use_charge: int(day_rate * MX(0, use_days - K('grace_days')) * 100 + 0.500001) / 100`. It belongs to no factor, so it falls to the computation document's `covers`, but it combines `day_rate` (from `day_rate_tier`) and `use_days` (from `use_anchor`). `grace_days` appears in no baseline sentence: `baseline.rule` never mentions a use charge and `baseline.params: ['self_pay_restocking_fee_pct']`. The use-charge formula and the 3 grace days are therefore rendered in the day-rate factor document.
   - **Kept chair:** `day_credit: int(down_rate * down_days * 100 + 0.500001) / 100` has the same shape, combining `down_rate` and `down_days`.

3. **Rule vs compute on how the chair was delivered.** The rule says only "a manual chair delivered into the home with training … delivered by courier".
   - Cash refund counts in-home deliveries with purpose `purchase_delivery` or `initial_rental_delivery`: `home_set: COUNT(... delivery_mode='in_home_delivery_training', delivery_purpose='purchase_delivery') + COUNT(... delivery_purpose='initial_rental_delivery')`.
   - It counts courier deliveries only with purpose `purchase_delivery`: `courier_set: COUNT(... delivery_mode='courier', delivery_purpose='purchase_delivery')`.
   - The kept-chair `home_set2` counts `purchase_delivery` only. So the same rule wording is computed three different ways.

4. **Rule vs compute on days of use** (cash refund, `use_anchor`).
   - Rule: "when a loaner chair has been delivered for the chair, from delivery_date to the requested_date of its latest return_pickup request, less …". Compute: `... if (ref_loaner and ret_req) else (DAYS(F('delivery_date'), rep_req) if rep_req else (DAYS(F('delivery_date'), ret_dec) if ret_dec else DAYS(F('delivery_date'), NOW)))`.
   - The loaner tier also requires a return request, which the rule doesn't say; without one the compute falls through to the other tiers.
   - When there is no return decision date the compute uses the booking day, which the rule doesn't mention.

5. **Superseded clause wider than its replacement** (`mobility_ext_kept_chair_adjustment.overwrite`). Both entries retire `mobility_self_pay` clauses about refunding a returned chair:
   - "A self-pay chair is refunded only when it comes back unused and complete no later than `self_pay_return_window_days` after delivery…" is replaced by "A cash-sale chair the patient keeps receives a price adjustment without coming back only while…".
   - "The refund is the price less `self_pay_restocking_fee_pct` percent, rounded to the cent half up; the delivery fee is never refunded." is replaced by "The price adjustment is the adjustment percentage of the price, plus the delivery fee returned, …".
   - Each replacement covers only kept chairs. The returned-chair side is covered only because `mobility_ext_cash_chair_refund` retires the same two clauses, so the two policies together are consistent.

No docstring mismatches were found in `task_tools.py`, and no base rule sentence is cut back without being named in an overwrite.
