# COORDINATOR RULING — realism bar for factors (env_0078; given to every reworker AND every auditor, verbatim)

Two things are fixed:
- the 4–6 factor floor and the drawn counts. These are skill/gate rules (check_extended, check_compute) and cannot be waived.
- realism, which is the user's top priority.

They are reconciled by ONE test, applied to every factor:

**Would a parent find this table, in this shape, in what a real Texas public school district publishes for this program?** That means the board-approved fee schedule, the program handbook, the parent registration packet, the refund/withdrawal policy, the transportation handbook, the School Nutrition charge policy, or the Pre-K tuition schedule. The figures may be Calloway Creek ISD's own, but they must be plausible.

## ACCEPTED shapes (a factor of one of these kinds passes on realism; it must still pass XF_recipe A1–A10)
- **R1 — keyed fee/rate schedules.** A published amount or percentage that varies by a recorded, publishable key. Keys include: program type or activity, campus level or campus, grade band, plan or days per week, season or semester, meal status (free / reduced / paid, CEP campus), number of children of the household enrolled in THIS program, distance band or hazardous zone, district-employee flag, residence (in-district or not), payment method, and school-calendar date windows. Examples: tuition by plan × campus level; a sliding-fee discount by meal status; a sibling discount by sibling position; a courtesy-rider fee by semester or annual permit; a meal price by campus level; a charge limit by campus level.
- **R2 — timing schedules.** One published table of refund, credit or fee percentages or amounts keyed on a recorded date relation: notice given N days before a date, days before departure, weeks into the season, the date of withdrawal relative to the billing month, or days past the due date. Real districts publish exactly these ("withdrawal before Sept 1: 100%; before first contest: 50%; after: none"). Allowed: ONE factor per timing dimension per computation, never stacked with a second proration of the same dates.
- **R3 — proration conventions.** Daily, weekly, half-month or whole-month proration, or a per-school-day count from the district calendar, selected by a recorded attribute (e.g. by plan type, or by start or withdrawal date). Real alternatives, with different shapes (XF A6).
- **R4 — real federal/state rules, cited exactly.** USDA prices and statuses, 7 CFR 210/245, SP 46-2016, the Eligibility Manual date-of-application option, TEC, UIL, McKinney-Vento, IDEA.
- **R5 — limits and caps the district publishes.** A household annual cap, a charge limit, a minimum refund threshold, a maximum installment count, an installment threshold.

## REJECTED shapes (RED on realism whatever the count)
- **X1 — invented benefits or penalties.** Tenure, loyalty, "continuing family", new-family or re-entry discounts or add-ons. AutoPay bonuses or relief (unless the base charter itself has AutoPay). Hardship shares or percentage cuts on penalty fees. Documentation shares. "Awaiting determination" allowances. Notice charges. Reserves or keeps no policy publishes. Fractions of other prices ("two fifths of the milk price"). Uplifts that make a credit exceed its charge.
- **X2 — stacking.** Two factors on the same dimension stacked: a taper and a proration on the same dates, two shares on the same meal status, or a percentage stack on a flat service fee.
- **X3 — factors already in a recorded amount.** Re-pricing a posted charge by a component the posted amount already carries (XF A8).
- **X4 — implausible figures.** Figures no district would publish (odd percentages, absurd amounts).

## Design consequence (for reworkers)
A computation whose result is a rebate on an already-posted flat fee has few honest dimensions. If a drawn count cannot be met there, MOVE the tree onto claimed write events whose real pricing is multi-dimensional, and compute the write from raw records rather than from a posted amount. Examples: a tuition, fee or permit charge computed at posting from plan, campus level, meal status, sibling position, start date and proration; a refund or withdrawal credit computed from the published timing schedule, the meal-status waiver and the household cap; an installment computed from the published plan terms. You may change what a task tests within your claimed event types. Gates must be 7/7 green; a gate-RED delivery is not an outcome.

## For auditors
- Judge every factor against R1–R5 / X1–X4 above, and cite which one applies.
- Do not strike an R1–R5 factor merely because its figures are the district's own rather than state-mandated.
- Do strike every X1–X4 factor, even when the instantiator calls it a "board schedule".

## AMENDMENT 1 (2026-10-24, coordinator ruling after round 2) — R6, the thin-charter waiver tier
Round 2 showed the following:
- The meals, enroll and activity charters carry one computable amount field per claimed write.
- The frozen compute contract cannot read sibling holdings of the same category.
- So honest R1–R5 factors fall far short of the drawn counts, and the counts are gate-enforced.
This is logged as BLUEPRINT-KNOWN (thin base charters vs frozen 4–6 factor floor). The closest established loop is the env_0074 thin-charter waiver. The ruling below ends the strike/pad oscillation.

**R6 — coordinator-waivable district schedule.** R6 is a schedule worded as Calloway Creek ISD's own published fee/credit schedule. Every one of these conditions must hold:
1. It is keyed on a RECORDED attribute a district could publish against (payment method, months or days in arrears, number of the household's children in a program as read from records, lead days between two recorded dates, a recorded document or status).
2. Its figures are plausible, round-ish district figures (no odd fractions of other prices).
3. It contradicts no federal/state rule and no in-force base clause. Examples of what is ruled out: SP 46-2016 forbids added fees or penalties on unpaid meal charges; USDA forbids lowering a status without notice.
4. It is not one of the named X1 benefit mechanisms: loyalty, tenure, "continuing family", AutoPay, new-family or re-entry discounts, frequent-booking discounts, hardship shares on penalty fees, uplifts that make a credit exceed its charge, desk-posting-delay add-ons.
5. It passes every XF_recipe point (A1–A10, B1–B8), and X2/X3 still apply to it (no stacking on a dimension another factor already uses; nothing already in a recorded amount).
6. Its count is MINIMAL. Per computation, the R6 factors are at most (drawn count − the number of honest R1–R5 factors that computation can carry). The reworker lists in the claims section, for every R6 factor: the R6 tag, its record key, and why no R1–R5 factor could take its slot.

**For reworkers.** Use R1–R5 first, and redesign onto richer claimed writes where possible (bus and care can: their R6 use should be zero or near zero). Use R6 only to fill the remaining slots. Every X1/X4 factor raised so far is removed or replaced, not reworded.

**For auditors.** Grade each R6-tagged factor against conditions 1–6:
- If all six hold, mark it `R6-WAIVED (BLUEPRINT-KNOWN)` in an observations list. It is NOT a RED and not a FLOOR item.
- If any condition fails, it is RED, citing the condition.
- A factor that is untagged but should have been tagged R6 is RED only if it fails a condition.

## AMENDMENT 2 (2026-10-25, coordinator rulings issued in round-3/4 rework briefs, recorded here so every auditor sees them)
- **Split prorations.** A whole-month count plus a separate partial-month factor keyed on the same recorded date is ONE R3 proration convention. It may not be split into two factors (R2/X2).
- **Meal forecast shape.** Pricing a student's coming serving days from the published 2026-27 calendar × published prices (R1 × R3) is ACCEPTED in two places:
  - as the amount of a prepayment quote;
  - as the amount of a sibling transfer, rollover or keep, ONLY where the parent's own request in the persona states that purpose.
  The persona may state the household's purpose ("enough to cover her lunches through next month"). It may NOT state anything the rules decide, such as which account receives a transfer or what amount is owed. One serving-day count per computation.
- **X3 / R6 condition 5 vs component exclusions.** A rule that leaves a component of a posted fee out of a waiver, credit or refund is the base rule applied, not re-pricing a recorded amount. Examples: the late application charge, which a fee waiver never covers; a held-seat month that meal-status waivers never reach. Such a rule is not X3, provided the excluded component is read from its own recorded row or its recorded dates. X3 stays: re-applying a discount or rate that the posted amount already carries.
