# REALISM BAR — coordinator ruling for factors (env_0081). Read by instantiators AND auditors. Every later ruling is appended here as an AMENDMENT and never given only inside a brief.

The request's top priority is realism. Every factor must be something a real US telehealth / virtual primary care practice (its billing office, its home-delivery pharmacy, its partner lab, the payers it contracts with), or a real statute / regulation / payer rule, actually uses.

Figures that are the company's own are worded as Larkspur Health's published schedule, with plausible numbers. Legal and payer figures are real, and are never invented.

## Accepted shapes

- **R1 — Keyed fee or price schedules on recorded, publishable keys.** Examples:
  - visit type list / member / employer-plan price;
  - membership tier dues;
  - lab panel price;
  - collection method fee (service center draw vs at-home kit vs mobile phlebotomy);
  - shipping speed;
  - formulary level × days supply cash price;
  - pack family price;
  - after-hours window;
  - patient location state where the charter keys on it.
- **R2 — One timing schedule per date dimension.** Examples:
  - cancellation notice window before scheduled_start;
  - refund window by days since the charge;
  - refill-too-soon threshold by days supply;
  - requisition expiry;
  - payer timely-filing limit;
  - statement due dates;
  - credit expiry.
- **R3 — A proration convention.** Examples: daily proration of a billing period, or a whole-month count with a stated month-end convention. It is ONE convention per date, never split into two factors.
- **R4 — Real federal / state / payer rules applied to recorded figures.** Examples:
  - copay / deductible remaining / coinsurance / out-of-pocket maximum from the coverage record's benefit fields;
  - ACA preventive services with no cost share on non-grandfathered plans;
  - the No Surprises Act Good Faith Estimate and its $400 dispute threshold;
  - the CMS three-year new vs established patient rule;
  - coordination of benefits order (primary / secondary);
  - state licensure by the patient's location during the visit;
  - 42 CFR Part 2 consent;
  - ACA 180-day internal appeal window;
  - HSA/HDHP rules exactly as the coverage record states them.
- **R5 — Published caps and floors that the charter or a real rule sets.** Examples: a late-cancellation fee never above the visit fee, a credit cap per membership year, a refund never above what was collected.

## Rejected

- **X1 — Invented perks.** Tenure, loyalty, AutoPay, "new patient welcome" or "good standing" discounts that the charter does not state.
- **X2 — Courtesy cuts.** Hardship or courtesy reductions on penalty fees that the charter does not state. A hardship review the charter defines is fine.
- **X3 — Stacking.** Two discounts stacked where the charter allows one. Applying a membership price where the charter says membership pricing never applies, e.g. on a path the charter excludes.
- **X4 — Already embedded.** A factor already embedded in a recorded amount: a recorded allowed_amount, patient_responsibility, price_paid, contribution amount or pbm_patient_pay.
- **X5 — Implausible figures.** Prices, fees or windows no real practice would publish.
- **X6 — Invented legal figures.** Invented legal or payer figures, or a regulatory status that is uncertain as of the scenario date. Controlled substances are not prescribed in this scenario at all.

## Design consequence

Put trees on writes priced from raw records, i.e. computations whose real pricing has several genuine dimensions. Examples: a visit charge from type × path × tier × after-hours × location; a claim balance from allowed amount × deductible remaining × copay/coinsurance × what was collected at booking. Do not put trees on rebates against posted flat fees.

## Seeded rows of other categories

They follow XF_recipe F1–F2: producible by the owning charter, priced by its formulas as of each row's posting date.

## AMENDMENT 1 (2026-10-25, coordinator) — the floor is not waived; the R6 tier for thin charters

The 4–6 factor floor and the drawn counts are enforced by gates (check_extended / check_compute), so they cannot be waived. Four of the five instantiators reported that their charter's real pricing dimensions per amount fall short of the draw. Every slot is filled in this order of preference.

1. **R1–R5 levers that the frozen charter already names.** Read the charter's parameter_schema and policies; most charters here carry 45–50 parameters. Examples:
   - visit: the path order, member price by tier on the booking date, included / sponsor counters, the GFE honor_estimate cap, after-hours clock / weekend / waived tiers, late-cancel window / fee / exempt tiers / courtesy waivers / fees_apply_on_paths, the full insurance cost-share estimate (preventive + grandfathered, copay, deductible remaining, coinsurance, OOP remaining);
   - lab: panel price by tier / plan / path, collection-method fees, requisition expiry;
   - rx: formulary level × days supply cash price, member discount, lower-of-cash-or-benefit, shipping speed and waiver;
   - membership: proration, refund windows keyed on completed visits, credit caps / expiry, retry / grace;
   - claim: deductible / copay / coinsurance / OOP applied, prompt-pay, small-balance write-off, statement cycle.
2. **Moving a tree onto a claimed write whose real pricing has more of those dimensions.** This is the realism bar's Design consequence.
3. **Only then, an R6 factor.** It is a Larkspur published schedule figure that meets ALL six conditions:
   1. it is keyed on a recorded field of the seeded records (no free-text, no unrecorded fact);
   2. its figures are plausible for a US telehealth practice / home-delivery pharmacy / partner lab of this size;
   3. it does not conflict with law or with an in-force base clause (or is declared as a scoped overwrite that restates base out of scope);
   4. it is not an X1 mechanism (tenure, loyalty, AutoPay, good-standing or welcome perks) nor X2 / X3 / X4 / X6;
   5. it is XF-clean (A1–A10, B1–B9);
   6. the count is minimal and it is tagged `R6` in the instantiator's worklog factor table, with its record key and a one-line reason why no R1–R5 lever could take the slot.

**How auditors grade R6 factors.** An R6 factor that meets all six conditions is graded as an `R6-WAIVED` observation, not a RED. An R6 factor that fails any condition is RED under the condition it fails. A factor dressed as R1–R5 that is in fact invented is RED (X5 / X6). Auditors still strike any factor whose figure is implausible.

**Count-keeping levers (rule carried over from earlier runs).** A lever added to keep the drawn count must honestly engage the task world. Sibling policies that price the same line mirror each other exactly. Every seeded row, including your own category's history, is re-priced under the current rules.

## AMENDMENT 2 (2026-10-25, coordinator) — rulings given inside briefs, recorded here for both sides

1. **visit difficulty: own-visit counters are unreadable.** check_compute scopes the own-category SUM/COUNT/MAX/LATEST to the target holding, i.e. the one visit. So counters across the patient's other visits cannot be computed: included-visit count, sponsor plan-year count, courtesy waivers, established status. A policy may not price a world where such a counter decides the amount. Scope it out by a coarse exact record test, stated in the rule as a plain record test with no purpose clause. Out of scope, the base rule applies; state it, or refer it with a stated computed referral. This is DSL-KNOWN and not a defect, provided rule == compute in every in-scope case.
2. **Path-selection ladders are load-bearing.** A ladder that decides which payment path, coverage or benefit applies to a visit or order is load-bearing when the task world sits off its fall-through tier and substituting the baseline moves the result (T1). Examples: sponsor coverage window vs the scheduled date; membership status on the booking date; coverage verified / effective window; preventive × grandfathered.
3. **R6 items accepted in principle for the visit charter**, each still subject to all six conditions, a declared scoped overwrite where it touches a base clause, and plausible figures:
   - a federal-holiday extension of after-hours time, keyed on the scheduled_start date; the federal-holiday list is already used by the charter's business-day rule;
   - a same-day (on-demand) booking premium for video visits whose booked_date equals the date of scheduled_start, keyed on those two recorded fields (booked_date is a date only, so no minute-level test);
   - a pediatric price schedule keyed on the patient's age in completed months on the scheduled date, read from date_of_birth.

   Real R4 levers on the insurance path that are not R6:
   - the HDHP pre-deductible telehealth safe harbor, which is permanent law for plan years beginning after 2024. It may be applied ONLY as the coverage record's own figures state it, i.e. telehealth_copay / deductible fields;
   - HMO PCP designation (pcp_designated) as a coverage-applies test;
   - coordination of benefits (coverage_order) choosing the billed coverage.
