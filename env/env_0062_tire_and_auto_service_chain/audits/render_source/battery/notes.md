# Render-source notes: battery (base type, blueprint/products/battery.yaml)

Source fingerprint (sha256): f1b5fdc8bdd0c506c3705de1b043bcf85d8bcbb9a490710b3aa1bcd576bd0da3
Docs: env/env_0062_tire_and_auto_service_chain/docs/battery/ (18 = 8 facet + 10 policy). Base text was carried as written; none of the items below was rendered around.

## Source mismatches

1. Undefined or contradictory branch: free replacement vs prorated adjustment
   - battery_evt_free_replacement.rule: "battery_msr_free_replacements must be below free_replacements_max; a further failure in the free period is handled as a prorated adjustment."
   - battery_evt_prorated_adjustment.rule: "A battery that fails after its free period but within prorated_through_months of purchase_date ... earns a prorated credit"
   - A failure inside the free period once the free replacements are used up is sent to the prorated adjustment, but that policy covers only failures after the free period. For the Standard 24-Month and Commercial Heavy-Duty 18-Month lines it also says "a line whose proration_basis is not_applicable has no prorated period". So the credit for this case is undefined: is there a credit, and what months_in_service and minimum apply? Both sentences are carried as written, in separate documents.

2. Rule vs compute: the ticket formula is narrower than the rule
   - battery_purchase_pricing.formula: ticket_before_core: "battery_price + (0 if install_type == 'carry_out' else installation_fee_standard)"
   - The rule also adds installation_fee_complex (under a seat, in the trunk or behind components), bms_registration_charge (when the vehicle requires registration) and recycling_fee. The formula leaves all three out and always uses the standard fee for an installed battery. The docs follow the rule.

3. Rule vs compute: rounding mode
   - battery_evt_prorated_adjustment.rule: "rounded half up to the cent". battery_evt_carry_out_return.rule: "rounded half up to the cent".
   - The formulas use "round(replacement_price * credit_pct / 100, 2)" and "round(purchase_price * (100 - carry_out_restocking_fee_pct) / 100, 2)". Python round on floats is not half-up (for example round(2.675, 2) gives 2.67). No divergence turned up at the six shelf prices with whole-percent credits or a 10% fee, but the two can split on an exact half cent. The docs follow the rule.
   - The carry-out rule ("purchase_price minus carry_out_restocking_fee_pct percent of it, rounded half up to the cent") does not say whether the fee or the refund is rounded. The compute rounds once, on the refund, and the docs pin it the same way.

4. Undefined branch: when a commercial-use warranty expires
   - battery_evt_warranty_end.rule: "It expires on the day after the last covered month, prorated_through_months after purchase_date."
   - battery_commercial_use_coverage swaps in commercial_use_prorated_through_months for claims "on the claim date". It does not say whether expiry follows the personal-use or the commercial prorated period. Carried as written (line's prorated-through months).

5. Minor: commercial-use opener vs measure
   - battery_commercial_use_coverage.rule opens: "Holding a Crestline fleet account changes battery warranty terms on the fleet's vehicles."
   - battery_msr_commercial_use is also true when the vehicle's usage_class is commercial, even with no fleet roster entry. Both are carried: the opener as written, and the measure as its truth table.

## Base sentence that states a cross-problem order (rendered as written)
   - battery_agg_vehicle_batteries.rule: "When a paid battery purchase replaces a battery whose warranty is still active outside any warranty claim, the old warranty is closed as removed first and only then is the new battery sold"
   - This is a base product with no extended policy, so no prerequisite sentence carries this dependency elsewhere.
