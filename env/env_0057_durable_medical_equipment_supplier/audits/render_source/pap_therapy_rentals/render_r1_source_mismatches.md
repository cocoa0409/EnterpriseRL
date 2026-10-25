# Source mismatches reported by the pap renderer (agent a22317e2824975d21), round 1 — verbatim

1. **A factor tier rests on another factor's output (`pap_ext_return_parts`).**
   - Factor `airpath_kit_price` (bindings `recv_date`, `airpath_part`) has its tiers on `airpath_days`: `airpath_part: K('airpath_long_price') if airpath_days > K('airpath_long_days') else ...`.
   - But `airpath_days` is decided by a different factor, `airpath_clock_anchor`: `decides: airpath_days`, with the method "service days counted from the service date of the latest warranty repair...".
   - The kit document carries the source wording "the days the air path has been in service up to the date the completed return pickup request records the unit as received back" with no start date, so it cannot be computed on its own.

2. **Superseded clauses wider than their replacements.**
   - **(a)** `pap_ext_used_accessories` retires this clause from `pap_repair_responsibility`:
     - Retired: "A patient-owned device within `manufacturer_warranty_months` of setup_date is repaired under the manufacturer warranty at no charge, except water_damage and drop_damage, which the warranty excludes."
     - Replacement: "A self-pay device sent back for a refund is inspected and reconditioned for stock, not repaired for the patient, …"
     - The retired clause covers every owned device, including coverage-bought ones. The replacement covers only refund returns.
   - **(b)** The same overwrite retires "an owned self-pay device is repaired at the patient's cost (repair_coverage patient_paid)." with the same replacement. A self-pay device the patient keeps is left with no in-force rule on who pays for repairs.
   - **(c)** The same overwrite retires "A repair is recorded only on a device the patient still has: the device record is trial_active, rental_active, suspended or patient_owned."
     - Replacement: "A return inspection is recorded on the device record of a self-pay unit that has come back to Summit Ridge while that record is patient_owned; it is not a repair of a device the patient still has."
     - This removes the state gate, and the matching `device_with_patient` eligibility, for every repair.
   - **(d)** Both `pap_ext_usage_nights` and `pap_ext_usage_hours` retire "A compliance download scores one window of `compliance_window_days` consecutive nights" from `pap_trial_compliance`.
     - Their replacements cover only usage summary downloads: "A usage summary download is not a scored compliance window: …" and "The average daily use on a usage summary download is a statement of the hours … not a compliance score…".
     - Trial conversion still depends on scored windows: "A device is converted only when a pap_compliance_download on this holding shows compliance_result met…"
   - **(e)** `pap_ext_home_unit_purchase` retires "Any class may be bought outright by a self-pay patient at `self_pay_retail_price` plus `self_pay_delivery_fee`, paid in full when the order is placed;" from `pap_self_pay`.
     - Replacement: "A unit bought outright is sold at the class's self-pay retail price, paid in full by the patient when the sale is booked; a unit already standing in the patient's home carries no delivery fee."
     - A newly delivered self-pay sale loses its delivery-fee basis. The refund clause that also mentioned the fee is retired too, so `self_pay_delivery_fee` no longer appears in any charging rule in force.
     - The surviving clause "the Travel CPAP System (E0601) is sold only this way" now points back at a retired clause.

3. **Minor: factor tiers reading a binding owned by another factor (`pap_ext_usage_nights`, `pap_ext_usage_hours`).** `swap_credit: K('swap_home_credit') if (swaps >= 1 and swap_mode == 'in_home_setup') ...` and the matching `swap_hours` read `swaps`, which is a binding of `serial_window_scope` / `serial_hours_scope`. It is a raw record count rather than a factor result, so it causes no wrong number.

4. **Minor: tool docstrings mention a card the tool bodies never record.** `return_device_for_refund_b6f98fe9` says "the amount refunded to the card the device was paid with", and `purchase_home_device_8c1f8216` says "paying the price on the card they provide". Neither body takes or records any card. I carried this as descriptive wording only.
