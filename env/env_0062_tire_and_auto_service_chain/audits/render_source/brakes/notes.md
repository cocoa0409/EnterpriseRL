# Render-source notes: brakes (base profile, blueprint/products/brakes.yaml)

Source sha256: fd0b51c4875d43c4b0ccfe651032e9b53ac0cde7c6d28c101885ebac32294e7c
Rendered 20 docs (10 facet, 10 policy). No overwrite declarations and no prerequisite edges apply (base profile, no brakes.extended.yaml).
These items are carried as the source has them. None was rendered around.

1. Rule vs parameter (dead parameter): the Ceramic 36-Month line has `premature_wear_threshold_pct: 50` and
   `premature_wear_credit: pads_and_labor_free`, but brakes_evt_warranty_replacement limits premature wear to
   "On a defects_only line, wear to minimum before premature_wear_threshold_pct percent of warranty_miles is
   premature_wear and earns premature_wear_credit". That line is `warranty_type: defects_and_wear`, so the rule can never
   use these values. The facet table still lists them.
2. Undefined branch, premature-wear labor: `premature_wear_credit: pads_free_labor_charged` (Value, Standard,
   Severe-Duty) does not say how much labor is charged.
3. Undefined branch, defect labor outside its window: "A pad_defect is replaced with pads free, and labor free while
   within defect_labor_covered_months and defect_labor_covered_miles" does not say what labor is charged once outside
   that window.
4. Undefined base and rounding, shop supplies fee: brakes_service_pricing charges "shop_supplies_fee_pct percent of
   labor, capped at shop_supplies_fee_cap". The labor base is not defined for the Complete line, whose
   complete_job_price_per_axle "includes new rotors, pads, hardware and labor". No rounding is given for the fee
   (5 percent of an x.99 labor price does not come out to whole cents).
5. Undefined branch, rotor: brakes_evt_rotor_service says "within that period a vibration finding is resurfaced free
   when rotor_warranty_resurface_free is true". Nothing covers a vibration finding inside the rotor warranty when that
   flag is false (Severe-Duty: 6 months, flag false). The rotor-warranty window also has no counting rule or equality
   boundary (no temporal_basis).
6. Boundary tension, expiry vs coverage: brakes_evt_warranty_end says a limited warranty "expires when warranty_months
   from service_date or warranty_miles from service_odometer is reached". brakes_evt_warranty_replacement covers a
   replacement "no later than the end of the warranty months" (inclusive) and "while brakes_msr_miles_since_job is within
   warranty_miles". So it is unclear whether a replacement at exactly the mile limit is covered (within vs reached).
7. Rule vs formula (subset only): the brakes_service_pricing formula `job_price` covers only package, pads, labor and
   hardware. The rule also adds rotor work, the fluid exchange and the shop supplies fee. This is not a contradiction.
8. Thin: the Complete line has `rotor_resurface_price_per_rotor: 0.0`, `rotor_replacement_price_per_rotor: 0.0` and
   `brake_fluid_exchange_price: 0.0`. Read literally, rotor work "charged at" these prices outside the rotor warranty
   comes to 0.00.
9. Thin: brakes_commercial_use_exclusion opens "Holding a Crestline fleet account changes brake warranty coverage on the
   fleet's vehicles". The deciding measure, though, is per vehicle (usage_class commercial, or latest roster row is an
   enrolment), not whether an account is held.
