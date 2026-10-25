# Render-surfaced source findings, round 3 — pump (insulin_pump_program_services)

Source at render: pump.extended.yaml sha256 fa4db57cbeb262387a9de22de8eaf6ee69d569511d4d5119e694c2db72594528; task_tools.py sha256 01563d460faf3b418857c7fffee1adb4919977a489ddeb51ece168bb72f85042 (unchanged).
R2-1 checked: closed. The rule now reads "its valid-from date being later or its valid-through date earlier than the ship date", and compute tests `x_gfrom > x_date`.

No new rule-vs-compute mismatch, quote defect or overwrite defect was found.

## Note (low, for the coordinator's XF judgement — not a mismatch)
Some factor sentences still name a quantity that another factor changes. In each case the quantity is defined by the standard method, so the reworded source passes the XF_recipe binding check: no factor binding reads another factor's binding. The reading happens in non-factor bindings. Rendered as the source states:
- `fx_set_rate_basis` tier 1: "the standard set rate is replaced with the set changes the daily pump insulin needs". The daily pump insulin is changed by `fx_set_dose_window` and counted per `fx_set_insulin_source`, through baseline binding `insulin_set_changes` → `set_daily_ins`.
- `fx_cart_rate_basis` tier 1: "replaced with the lesser of the ordered rate and the cartridges the daily pump insulin needs". The ordered rate is changed by `fx_cart_order_basis` and the daily pump insulin by `fx_cart_dose_window`, through baseline binding `cartridge_rate`.
- `fx_nt_insulin_cap`: "the expected rate is held to no more than …". The expected rate is changed by `fx_nt_expected`, through baseline binding `capped_rate`.
- `fx_rc_contractual` CO-151 tier: "the denied units, as the payer denied them, times the value of a denied unit". The value of a denied unit is changed by `fx_rc_unit_value`, through baseline binding `rc_off`.
