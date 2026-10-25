# Renderer findings (verbatim final reply of agent a0a1836f497a08ce7, saved by the coordinator)

I stopped before writing anything for water, so there is no DOCS OK line and the document count is 0. The scan found a source-side defect I can't render without making up or dropping meaning. Nothing was written to `docs/water/` or `.doc_render_staging/water/`, and my scratch sweep script is deleted.

**The defect that blocks rendering (recipe C3 and C2)**

File: `env/env_0079_property_restoration_contractor/tasks/water_mitigation_billing/water.extended.yaml`. It appears in three policies: `water_ext_tearout_debris`, `water_ext_tearout_antimicrobial` and `water_ext_final_hepa_vacuum`.

- All three overwrites retire the same sentence of base policy `water_evt_mitigation_services`. That sentence is the only place in the charter that lists the billing units:
  > "Each mitigation service is billed at the unit rate of the job's tier for its service code, multiplied by the quantity performed: extraction, antimicrobial, pad and carpet work and HEPA vacuuming by the square foot, flood cuts and baseboard by the linear foot, contents manipulation by the room, debris by the load, PPE by the technician-day, labor by the hour, and moisture mapping, thermal imaging, containment, dumpster, lead-safe setup and asbestos sampling by the each."
- Each `replaced_by`, which is also copied word for word into each rule, then points back to that retired sentence for the units. The tear-out debris version reads:
  > "Every mitigation service line other than a tear-out debris haul-off line, a tear-out antimicrobial line and a final HEPA vacuuming line remains billed at the unit rate of the job's tier for its service code multiplied by the quantity performed, **in the units the mitigation service rule sets**; …"
  The antimicrobial and HEPA versions say the same thing, with the excluded lines listed in a different order.
- Rendered as written, the base document would mark the only units list "no longer in force", while three extended documents say those units still apply. If I put the units into the extended documents myself, I'd be rendering around the defect.
- Fix on the source side: restate the full units list in each of the three `replaced_by` texts and the matching rule sentence, so nothing points back to the retired clause.

**Other items to fix in the same rework round (these could be rendered, but fall in recipe classes)**

1. **A9, two possible groupings.** In `water_ext_insured_share`, both the rule and the ladder text of factor `hepa_stripped_floor_cover` say:
   > "on a category_3 job carrying HEPA vacuuming lines the square feet above the pad removal square feet plus 4 feet for each linear foot on the flood cut lines … are a non-covered amount"

   The compute is `MX(0, sh_hepa_sqft - sh_pad_sqft - sh_cut_lf * K('cat3_wall_ft'))`, meaning the HEPA square feet above the total of the pad removal square feet and 4 square feet per linear foot of flood cut. The text can also be read as "the square feet above the pad removal square feet, plus 4 feet per linear foot". It should be reworded so only the compute's reading is possible.
2. **B1, a line with no date in one case.** In `water_ext_tearout_debris` and `water_ext_tearout_antimicrobial`, the line is
   > "dated the service date of the job's latest flood cut line, or of its latest pad removal line when it has no flood cut line"

   The same rules still bill the line on a job carrying only carpet removal lines ("carries no pad removal, carpet removal or flood cut line" is the only case that bills nothing). That can happen on a Black Water job with glue-down carpet and no pad, and then the date isn't defined.

**Base defect for your log (base text is frozen, so this needs no change from me)**

`parameter_schema.monitoring_visit_fee` reads "Daily moisture monitoring visit fee per visit day beyond the included visits, USD". No base rule defines any included visits; the only free visit is the set-day waiver in `water_evt_monitoring`.

**What I checked and found clean**
- Every `compute_basis` quote, baseline sentence, prerequisite sentence, superseded clause and `replaced_by` text appears word for word where it should.
- No factor id is part of any tool name.
- No factor reads another factor's output.
- The rounding sentences match where rounding happens in the compute, in all five policies.
- Cases with a missing record are stated in the rule (no mold job, no ordinance or law limit, more than one code-upgrade request or more than one invoiced mold job goes to a human).
- The tool docstrings agree with the tool bodies.
- The base policies in the extended yaml are identical to `blueprint/products/water.yaml`.

Once the yaml is fixed, a fresh render can start from Step 0.
