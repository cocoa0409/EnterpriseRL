# Renderer scan-first findings — product maintenance, render round 1 (renderer agent a852a7e3c164ab21e, 2026-10-22)

Saved verbatim by the coordinator from the renderer's reply (the harness blocked the renderer's own write of /tmp/render_maintenance_0075/findings.md). The renderer STOPPED with 0 documents written. Line numbers refer to tasks/prepaid_maintenance_plans/maintenance.extended.yaml at sha256 prefix 86c5c1247c76.

**F1. Retail plan price can come out negative, and no rule covers it (maintenance_ext_retail_plan_price; XF B9, F22)**
- **Rule (l.1555):** "Where a rate applies to the plan it reduces the retail basis price once; credits that apply are then added together and subtracted from that reduced price; the retail plan price is rounded half up to the cent only at the end." There is no floor.
- **Compute (l.1604):** `RND(retail_basis_price * (1 - rewards_rate) - credit_total + 0.000000001, 2)`. There is no floor here either.
- **Example world:** this is the policy's own trade-up case.
  - A new Toyota (factory complimentary maintenance runs 24 months / 25,000 miles) was delivered on a Kessler deal fewer than 30 days ago. A replaced Essentials 2-Visit plan, sold on a deal, was cancelled for vehicle sold or traded within the last 3 months.
  - The months share is about 0 and the miles share is max(0, 15,000 − 25,000)/15,000 = 0, so the basis price is 0.00 to 8.29.
  - Credits are 30.00 plus 50.00, so the price is about −80.00 to −71.71.
  - New Hyundais on Essentials 2/4-Visit or Plus 6-Visit do the same.
- **Conflict:** a negative price contradicts the tool's `purchase_price` ("the price the customer pays for the plan") and the charter field meaning ("price paid after discounts").
- **Fix:** state the floor and where it sits in the order, in both rule and compute, or rework the basis/credits so this cannot happen.

**F2. Total-loss refund: the order of the 0.00 floor and the credits is not fixed (maintenance_ext_total_loss_refund; XF A3, B8)**
- **Rule (l.1194/1196):** "The total-loss refund is the plan's standard refund rounded half up to the cent." / "Credits that apply are added to the rounded refund, and the total-loss refund never exceeds purchase_price."
- **The floor appears only in the scope sentence (l.1192):** "...and a refund below 0.00 is still 0.00 with nothing billed". It has no placement. The sibling policies say "floored at 0.00 at the end" (l.997, l.1721).
- **Compute (l.1249):** `MN(F('purchase_price'), MX(0, RND(loss_refund + courtesy_credit + purchase_bonus + relationship_credit + 0.000000001, 2)))`, which floors after the credits.
- **Example world:** an active Plus 6-Visit plan with 5 net visits used, on the fall-through share tier.
  - The standard refund is 549.00 less 5 × 119.95, which is −50.75.
  - With 20.00 plus 10.00 in credits, the compute gives 0.00.
  - Flooring first and then adding credits, which matches the base clause "A computed refund below 0.00 is 0.00", gives 30.00.
- **Fix:** fix the order in the combination sentence, e.g. "floored at 0.00 and capped at purchase_price at the end".

**F3. Fleet addendum: the rule reads the whole customer, the compute reads one plan (maintenance_ext_fleet_addendum_price; XF B8/B9/B12)**
- **Rule (l.771):** "The total-loss replacement credit reads the customer's most recent cancellation of a Kessler Care Fleet 12-Visit plan for a total loss, by the date of its cancellation entry: dated fewer than 1 whole month before the pricing date it earns replacement_credit_recent; dated 1 or more but fewer than 3 whole months before it earns replacement_credit_earlier; an older one, or none, earns no total-loss replacement credit."
- **Compute (l.829–830):** `COUNT('maintenance_plan_ledger', within_months=1|3, event_type='maintenance_visits_cancelled', cancel_reason='total_loss')`.
  - COUNT only reads the target holding's ledger (`check_compute.py` `build_env`: `eq[holding_pk] = HID`).
  - The rule never says which plan's entries are read.
- **Example world:** the target plan's total-loss entry is 2 months old and another fleet plan's entry is under 1 month old. The compute gives 30.00; the rule gives 60.00.
- **Fix:** name the plan whose entries are read, as a record test, the way retail_plan_price defines "the replaced plan". Or make the read cover all of the customer's plans.

**F4. Fleet addendum: the out-of-scope price is undefined, and the overwrite leaves no in-force price (XF C13)**
- **Rule (l.760):** "...an addendum for any other unit, or for a customer holding more than one agreement in delivered status, is outside this policy and keeps the base price." "The base price" is never defined, and it is easy to confuse with this policy's "basis price".
- **Overwrite of maintenance_evt_sale (l.735/737):** it retires "a plan bought on its own is priced at plan_price_usd". Its replaced_by reads: "For the same fleet addendum this policy also replaces the price of a plan bought on its own, while the addendum is still offered only where standalone_sale_allowed is true and a retail Kessler Care plan bought on its own is outside this policy." It never says other fleet plans bought on their own stay at plan_price_usd.
- **Sibling overwrite of the same sentence (l.1534):** it restates the price only for "every other retail plan bought on its own".
- **Effect:** the base clause gets marked "no longer in force". The KB is then left with no in-force price for an out-of-scope fleet plan bought on its own below the volume threshold.
- **Fix:** restate that price in the replaced_by, and replace "keeps the base price" with that wording.

**F5. Fleet cancellation refund: a binding only one factor uses sits outside that factor (maintenance_ext_fleet_cancel_refund; XF A4)**
- **Binding:** `last_visit_reading` (l.1020) is read only by `refund_share` (l.1025), which belongs to the `usage_share` factor. It is missing from `usage_share` bindings (l.1071: `[share_checkin, share_recent_entries, share_mile, share_day, refund_share]`).
- **Where it is defined:** baseline.rule (l.1160–1161) never states it. The rule defines it only inside the factor's own sentence (l.998): "the plan's last recorded visit reading, which is the highest odometer on the plan's redemption entries (reinstated or not) or odometer_at_sale where that is higher or there is no such entry".
- **Effect:** the computation document would have to claim a binding it never describes.
- **Fix:** add `last_visit_reading` to `usage_share` bindings. The fleet transfer policy's identical binding is fine, because its baseline.rule (l.1519) defines it.

**Checked and clean:** every compute_basis quote, prerequisite sentence and replaced_by is verbatim in its rule, and every superseded clause is verbatim in its base rule; no factor reads another factor's binding, and no factor id is a substring of a tool name; the prerequisite state words have records behind them (`vehicles.title_brand` salvage/rebuilt/flood and `vehicles.customer_id`); the fleet transfer's "in whole miles" matches `int(...)`; tool docstrings match their bodies and carry no example values or composite arguments.
