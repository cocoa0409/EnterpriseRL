# setaside_property_charges_and_repairs — rework log

Per-task worklogs live in each task's `design_rationale` (tasks/0.json, tasks/1.json).

## Round 3 (renderer source-mismatch, assembly class; lesser observation)
- Projection policies (tax, hazard, flood) restructured: each computation document (baseline.rule) now defines every assembled quantity with its default and states the blend once; each factor replaces only its own quantity, and each factor moves the result on its own with every other factor at its default.
  - Tax: assessment allowance default = standard 2.0% increase (tiers: restoration 6% / falling value 0% / standard); next-year share default = month basis from the latest-due paid bill (tiers: installment count / annual block / month basis). Task 0 gold unchanged (11167.44, 688.61).
  - Hazard / flood: renewal loading = standard renewal increase 4% + premium-change + occupancy/residence + appraisal loadings (each zero by default); renewal share default one half. Task 1 gold: hazard 6178.40, flood 3164.55, hazard credit 2793.61, flood credit 1406.46 (closing tax recalibrated 6431.40 -> 6455.00).
- Tax refund rule: the credit references, where more than one paid installment of the tax year is overpaid, the reserve's payment of the paid property tax bill with the latest due date.
- Refund policies checked for the class: already conforming (all assembled quantities defined with defaults in the computation document); unchanged.
- Proof text swept in both tasks; probes re-run.
REWORK round 3: gates 7/7 green
