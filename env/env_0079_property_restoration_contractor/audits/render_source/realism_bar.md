# realism_bar.md — coordinator ruling file shared by reworkers AND auditors (env_0079)

Written by the coordinator mid-run (2026-10-25). It complements XF_recipe.md section E. It decides what kinds of factor
are acceptable as realistic, so reworker and auditor stop oscillating between "struck as invented" and "below the
gate-enforced 4-6 factor floor" (the floor itself cannot be waived: check_extended / check_compute enforce it).

## Accepted shapes
R1. Keyed price schedules on recorded, publishable keys (tier, loss type, water category/class, property type, growth
    location, year built, dispatch window, payment route, billing arrangement), worded as the company's own schedules.
R2. One timing schedule per date dimension (days since loss, days in storage, days past due, days since completion),
    with stated boundaries; a whole-period count and its part-period share on the SAME date are ONE convention (one factor).
R3. Proration / counting conventions stated once (inclusive day counts, period shares, minimum charges).
R4. Real external rules as they really are: IICRC S500/S520 categories and classes, EPA RRP (pre-1978, 6 sq ft interior),
    FTC Cooling-Off Rule, Florida 2023 AOB bar, Texas Ins. Code ch. 707, Texas Property Code ch. 53 retainage, TX/NY
    mold assessor-remediator separation, carrier practices the claims charter states (ACV/RCV holdback, depreciation
    release window, ordinance-or-law limit, deductible handling, two-party / mortgagee loss-draft routing).
R5. Published caps and limits recorded on the records (claim sublimits, ordinance-or-law limit, approved amounts,
    tier caps), applied once.

## Rejected shapes
X1. Tenure, loyalty, AutoPay, new-customer, claim-count or "relief" perks; hardship cuts on penalty fees.
X2. Stacking two discounts / caps on the same amount, or one charge split into two factors that always sum back.
X3. A factor already embedded in a recorded amount (recorded approval, recorded contract sum, recorded line amount).
X4. Implausible figures or rules no contractor/carrier/mortgagee would apply (e.g. performed labor treated as worth
    nothing, larger scope priced lower, a discount no ledger write can record).

## R6 — thin-charter waiver tier (BLUEPRINT-KNOWN)
Where the frozen charter gives a computation too few real levers to reach its drawn count, a factor may be graded
R6-WAIVED (an observation, not a RED) if ALL hold: (1) keyed on a recorded field; (2) plausible figures; (3) no conflict
with law or any in-force base clause; (4) not an X1-X4 mechanism; (5) XF-clean (A1-A10, B, C, D); (6) the minimal number
needed to meet the draw, each tagged `R6` in the reworker's REWORK section. Auditors list R6 factors as R6-WAIVED.

## Coordinator rulings recorded so far (both sides must apply them)
- RULE-1 (all): every task carries >= 1 factor reading a CLAIMED sibling category (water, mold, rebuild, contents, claims);
  fire/account reads may exist in addition but do not count toward that floor.
- RULE-2 (all): other-category rows no gold step reads cannot be seeded (replay closure) -> accepted residue; but every
  cross-category record a scored factor reads must be a state its owning charter produces, with its justifying rows seeded
  and read by gold.
- RULE-3 (claims): thin customer writes in the claims charter (deductible payment = remaining due, endorsement 0.00,
  withdrawal no number) are BLUEPRINT-KNOWN; re-treeing within the claimed events is allowed; the customer's write must be
  one of the XF F1 forms. carrier_denied_line may only be used for amounts a recorded carrier act declined, unless a scoped
  overwrite honestly redefines it AND the record it keys on exists.
- RULE-4 (all): the REWORK section of a worklog never carries scored, baseline or sensitivity figures.
- RULE-5 (rebuild): account-charter figures read by an extended rule (no base rounding/day-count) must have the rounding and
  day count stated in the extended rule itself.
- RULE-6 (all, from claims CG-23): the drawn factor count is gate-enforced and cannot be lowered. XF A6 T2 is not waived for a factor that acts only through other factors' outputs (A4). Accepted route: the standard method defines the quantity at a stated default, other factors narrow/widen it from records, and the factor acts on that baseline-defined quantity. R6 condition (5) requires XF-clean, so R6 never covers an A6/A4 failure.
- RULE-7 (rebuild, round 11): a lever added only to keep a drawn count must be a real base-catalogue parameter that engages the task world honestly (candidates read from rebuild.yaml: project_management_fee_pct, engineering_letter_fee when framing is altered, material_escalation_threshold_pct) and must not contradict another policy's treatment of the same work; sibling policies pricing the same line (additive vs deductive change orders) must mirror each other's pricing exactly; seeded rows are re-priced under the current rules.
