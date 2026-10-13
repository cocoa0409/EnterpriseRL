# Policy-KB bijection audit — service_contract_claims_and_cancellations / task 0

## Audit record

- Auditor: independent KB-doc audit agent. Written after the runtime blind audit was frozen at `audits/runtime_context/service_contract_claims_and_cancellations/task_0.md` (blind body sha256 14609caeac3832a6c41bba80524f7be37fcd980863b232282a55c59bbb1784a4).
- Source: `tasks/service_contract_claims_and_cancellations/warranty.extended.yaml` and `task_tools.py`. Task 0's scored policies are:
  - `warranty_ext_cancellation_settlement` (root);
  - `warranty_ext_stack_remainder_authorization`;
  - `warranty_ext_rental_reimbursement_settlement`.
- The base policies they govern or overwrite are `warranty_cancellation`, `warranty_claims`, `warranty_agg_vehicle_coverage_stack` and `warranty_benefits`, together with the variant parameters they read.
- Corpus: 69 `docs/warranty/*.json`, hash e80227f6d5c83afe46217daba70562280e7e70daee310a9cc5688f4743aa1272. It is unchanged between the blind audit and the scan.
- Document meta was used only to locate candidate homes. Every judgement below is on title/content prose.

## Entry conditions (Step 0)

All entry conditions were supplied:
- The policy-side verdict is erl-task-policy-audit PASS for tasks 0 and 1 (round 4), as stated in the brief.
- The gate snapshot in the brief shows `check_docs.py … warranty -> DOCS OK (69 docs)` and `check_traceability.py … -> TRACEABILITY OK`, with the instantiation gates OK.
- The runtime view and the tool-form DB path were provided, and both hashes match the brief.

## source_to_kb

### A. `warranty_ext_stack_remainder_authorization` (hub `remainder_authorization_after_limited_warranty_070bbae3`)

| Source atom | KB home | Equivalence |
|---|---|---|
| Rule opening: "When a Kestrel limited warranty decision … left part of it unpaid, the KestrelCare authorization of the same repair order settles what the plan still owes on it, read from the latest limited warranty decision …" | hub "When it applies" (verbatim). `limited_warranty_outcome_and_starting_amount` gives the latest decision ("the one with the most recent decision date") and the estimate, covered amount, deductible and decision. The vehicle system and odometer are read in the repeat-repair and wear docs ("as recorded on the Kestrel limited warranty decision") | equal |
| Baseline rule (estimate − chosen deductible ≥ 0, capped at per-visit limit and coverage remaining, rounded at end); param per_repair_visit_limit_usd | `remainder_amount_payable_b275d9ad` (role baseline). Its input table names the per-visit limit, whose figures are in `repair_limits_and_labor_rate_schedule` | complete. It contains no hint of variation |
| Factor `limited_warranty_remainder`, 3 method tiers | `limited_warranty_outcome_and_starting_amount_99f62619`: all 3 tiers, with a table and the "no limited warranty decision" case | complete |
| Factor `remainder_deductible`, 3 tiers (0; 0.5 × chosen when the maintenance plan is active with ≥ 1 redeemed visit in 12 months; chosen) | `deductible_for_maintained_vehicles_6fd6b18d`: 50 percent (0.5) and "at least 1 service visit". It names KestrelCare Prepaid Maintenance Plans and its visit-redeemed entries | complete; cross-product findability present |
| Factor `repair_wear_deduction`, 100000/75000 and 0.15/0.10 | `high_mileage_wear_deduction_54c0ddaa`: both thresholds stated in figures, plus a boundary table | complete |
| Factor `repeat_repair_share`, 0.5/0.75/1, counted back from the remainder decision day | `repeat_repair_on_same_system_d8314845` | complete |
| Factor `late_notice_share`, 60/30 days and 0.8/0.9; "from the failure date on the repair order to the day of the decision" | `late_failure_notice_efddccea`: all tiers and boundary dates. The wording is the source's own, and it attributes the failure date to the LW decision, which is consistent with compute `lw_failure_date` | complete (see the wording note in Step 4) |
| Factor `repair_sales_tax`, AZ 0.056 / TX 0.0625 / other 0 | `repair_sales_tax_by_registration_state_486bbb3d`: "added last; the per-visit limit and the coverage remaining are compared with the figure after the tax" | complete |
| Assembly order (overwrite replaced_by and rule: deductible → wear → repeat → late notice → tax last; caps compared after tax) | Each factor doc places itself "after the deductible" and "before the comparison with the per-visit limit and the coverage remaining". The tax doc says "added last". The steps are multiplicative, so the order between wear, repeat and notice cannot change the result | equivalent at entailment |
| Overwrite of `warranty_claims` "Otherwise the claim is approved: …" | `repair_claim_decision_standard_4695414d` §B: the clause is quoted and marked "**no longer in force** … superseded". Tests 1–5 are still carried in force | retired surface correct |
| Overwrite of `warranty_agg_vehicle_coverage_stack` consequence | `coverage_order_with_other_warranties_edb2ce34` §2: quoted and marked no longer in force. The stacking order and the "while the limited warranty … is in force and covers the failed system" condition are kept in force | retired surface correct |
| Tool contract `authorize_stack_remainder_2296c771` (10 params, enums, receipt) | hub parameter table and enum lists. These match `task_tools.py` (requested_amount is "the repair estimate the decision is made on"; deductible_amount is "0.00 when none is applied") | equal |
| `prerequisite: []` | no prerequisite sentence in the hub | equal |

### B. `warranty_ext_rental_reimbursement_settlement` (hub `rental_car_reimbursement_filing_92aeed27`)

| Source atom | KB home | Equivalence |
|---|---|---|
| **Prerequisite** → stack_remainder_authorization. Form state. policy_source "A rental car reimbursement is booked only after the repair order it belongs to carries an approved KestrelCare authorization on the plan." | Verbatim in the hub ("Condition of booking"), with a same-form restatement in the same document ("Put the other way round: …"). Found in no other document of any product (mechanical verbatim scan) | Connective ("only after") and state form are intact. **Resolution basis:** the state "approved KestrelCare authorization on the plan" is the write described by the remainder hub ("The authorization is a KestrelCare claim decision on that repair order … booked on the plan's history as a claim decision entry"), and the records show RO-556872 with no plan decision. Strength is the same (hard gate) |
| Baseline rule (nights from the authorization's failure date to the authorization date, capped at the rental maximum days, × rental per day); params rental_per_day_usd and rental_max_days_per_claim | `rental_reimbursement_amount_764e7f4d` §2, plus the benefits schedule figures | complete. No variation hint |
| Rule sentences on the repair order read and on receipts and once-per-RO (also the overwrite replaced_by for the base receipts clause) | the same baseline doc, §1 and §3 (verbatim) | equal |
| Factor `rental_night_count`, 3 method tiers, including the floor at zero | `rental_nights_counted_72037853` | complete |
| Factor `rental_night_cap` (4000 AND 2 same-system approvals in 12 months → +3; ≥ 2500 → +1; else max) | `rental_night_limit_on_major_repairs_693aeda7`: both parts of the compound condition, both thresholds in figures, and the 4-row table | complete |
| Factor `rental_vehicle_class_rate` (40/50/plan) | `rental_daily_rate_by_vehicle_program_320c0396` | complete |
| Factor `limited_warranty_rental_credit`, 3 method tiers, including nights paid ≤ LW max days | `credit_for_limited_warranty_rental_d3dc092e`. It defines the LW daily rate and LW maximum days as the included limited warranty's figures for the vehicle program on the Vehicle Purchase Agreements order | complete; cross-product reads named |
| Factor `rental_sales_tax` (AZ 0.083 / TX 0.10) | `rental_sales_tax_by_registration_state_011c024b` | complete |
| Factor `rental_secondary_share` (≥ half 0.75; > 0 0.9; 0 → 1) | `secondary_rental_share_ca5f9536` | complete |
| Assembly order ("credited first, the tax then added to that result, the secondary share last; never below zero") | The credit doc's "Rental amount for the nights" is the credited figure. The tax doc multiplies "the rental amount for the nights". The share doc says "applied last, to the reimbursement as otherwise figured". The baseline says "never below zero" | equivalent at entailment (the order is carried through a defined term, not a sentence) |
| Overwrites of `warranty_benefits` (rental clause; receipts clause) | `repair_benefit_terms_4e413bfd` Arts. 2 and 5: quoted and marked no longer in force. Arts. 1, 3, 6 and 7 are kept in force | retired surface correct |
| Tool contract `file_rental_reimbursement_5fdd83af` (user owner, 4 params) | hub "Filing" section: a customer tool handed over | equal |

### C. `warranty_ext_cancellation_settlement` (hub `plan_cancellation_settlement_0e1d2af4`)

| Source atom | KB home | Equivalence |
|---|---|---|
| **Prerequisite** → stack_remainder_authorization. Form state. "A cancellation refund is fixed only after every repair order that a limited warranty decision for the holder left wholly or partly unpaid carries a KestrelCare authorization decision on the plan." | Verbatim in the hub ("Conditions on the refund"). Found in no other document | Connective and form are intact. **Resolution basis:** the remainder hub describes the write in the sentence's own words ("left part of it unpaid", "authorization … is a KestrelCare claim decision on that repair order"). The records show LW decisions on RO-552614 (decided on the plan) and RO-556872 (not decided). Strength is the same |
| **Prerequisite** → rental_reimbursement_settlement. Form state. "A cancellation refund is not worked out until each repair order whose limited warranty decision recorded approved rental days, and which carries either no KestrelCare decision yet or an approved one dated no more than the plan's benefit receipt submission days before the refund is worked out, carries a rental car reimbursement entry on the plan." | Verbatim in the hub. Found in no other document | Connective and form are intact. **Resolution basis:** the rental hub ("booked on the plan's history as a rental car reimbursement entry on the repair order"), the 30-day receipts figure in the benefits schedule, and the records (RO-556872 rental_days 7 with no decision; RO-552614 decided 2026-08-04, more than 30 days earlier). Strength is the same |
| Rule: one booking, confirmed request, effective day = day to which use is counted, full-refund cases, payee carve-out | hub "Scope"; `pro_rata_refund_calculation` Part 1 | equal |
| Baseline rule (days sale→request over sale→expiration; miles; less plan fee; less net claims if deducting; rounded; ≥ 0); params cancellation_fee_usd and claims_deducted_from_refund | `pro_rata_refund_calculation_89af51e1` Part 2 (lines a–g). The fee and deduct-claims figures are in `cancellation_and_refund_schedule` | complete. No variation hint |
| Factor `use_start_day` (3 tiers) | `start_of_plan_use_ff809209` | complete |
| Factor `use_end_day` (3 tiers) | `end_of_plan_use_c67cf95f`. It names Trade-In Agreements (agreement on the plan's VIN) and the Vehicle Purchase Agreements returned status | complete; cross-product findability |
| Factor `time_fraction_basis` (AZ/CO months; TX/FL months + 1; other days) | `time_measure_by_registration_state_89c27e5e`, including the day-of-month completion rule | complete |
| Factor `cancellation_reason_fee` (0 / 25.00 / plan fee) | `cancellation_fee_by_reason_41997ee9` | complete |
| Factor `kestrel_relationship_fee_share` (0.5 trade-in toward a delivered or completed order; 0.75 another delivered order; 1) | `fee_relief_for_returning_customers_35cc9b8a`: both compound conditions in full, and the record definitions | complete |
| Factor `claims_charge_composition` (3 method tiers) | `claims_charged_against_refund_3ecf314d`, including which levels deduct and the ledger entries totalled | complete |
| Overwrite replaced_by "fee set by the reason × fee share; … less the claims charged, rounded only at the end, ≥ 0" | fee relief ("the fee charged is the cancellation fee the cancellation carries, times the holder's fee share"); claims charged; worksheet line g ("rounded to the cent at the end") | equivalent |
| Overwrites of `warranty_cancellation` (effective-date clause; pro-rata clause; refund-on-cancelled clause) | `cancellation_terms_and_refund_bases_d1d66f9b` §2, §3.3 and §4: each quoted and marked no longer in force. The right to cancel, confirmed request, lapse, basis order 1–2, one refund, payee and timing are kept in force | retired surface correct |
| Tool contract `cancel_plan_with_refund_1804bd93` | hub parameter list (basis enum including `not_applicable` never used; "rounded half up") | equal |

### D. Base policies and variants read

- Variant figures are carried in the facet docs: cancellation schedule, benefits schedule, limits card, covered-systems matrix, declarations, waiting period, timelines and transfer schedule. A mechanical scan of every scalar variant parameter against the facet table rows found every figure. `pro_rata_basis` is rendered as "greater of time or miles".
- `warranty_claims` decision tests and the "paid only on active" rule are in the Claims Manual.
- `warranty_benefits` Art. 7 (active or exhausted only) is carried.

## kb_to_source

- Every normative sentence in the 16 documents of the three policies and in the base documents above traces to a rule sentence, an overwrite, a variant parameter, a compute binding or a tool contract.
- Glosses that restate the source without changing its meaning:
  - "the one with the most recent decision date" restates compute `XLATEST(…, date_field='decision_date')`;
  - "this day ends the use counted for the time measure; the miles measure still reads the odometer on the cancellation request" restates compute `miles_fraction` (req_odometer);
  - "its pickup date is the date the vehicle was picked up or dropped at a hub" glosses the trade-in pickup field.
- Additions: none. No confirmation, review, notification or extra step appears that the source lacks.
- Omissions: none.
- Rewrites: none at entailment level.
- Cross-problem operational guidance ("if unmet, first call …"): none. Each tool name appears only in its own hub (mechanical scan over all products' docs).
- Opening world state written as policy fact: none. Every example is marked hypothetical, and none reproduces task 0's figures (plan 833103fa, RO-556872, 4620/3000/50, 2640, 2026-09-13).

## bijection_verdict

**PASS.**
- No unborne atom, no atom borne with changed meaning, and no claim from outside the source.
- All three prerequisite sentences stand verbatim, in state form, in their blocked hubs only.
- All 18 declared factor ladders of the three policies are complete, with every tier exact.
- The retired surface is correct for the six overwritten base clauses that this task's policies touch.
- This is the first revision; there is no earlier revision.

## dependency_form

Checked against every Step-3b pattern over the full warranty corpus.

| Check | Result |
|---|---|
| State-form sentence restated as an action, or with a resolving action or performer beside it | none. The two restatements are same-form and in the same doc (rental hub "Put the other way round …") |
| Another problem's tool named in a blocked problem's docs | none (verbatim scan: each tool only in its own hub) |
| Dependency or order between problems stated beyond the source sentences | none found as a render addition (see note 1) |
| Aggregation into a table, checklist, roadmap or route | none. The hub sections "Conditions on the refund" group only the blocked policy's own two source sentences |
| Wrong vs right reading, named mistake, or cross-problem walk in examples or FAQs | none. All examples are single-policy and hypothetical |
| Titles or openings mirroring the task | none. Titles name general subjects, for example "Cancelling a KestrelCare Plan with Its Refund" (the `on_request` subject), "KestrelCare Remainder Authorization after a Limited Warranty Decision", "When the Vehicle Leaves the Holder: End of KestrelCare Plan Use" |
| Depended-on doc reachable only via borrowed phrasing | no. KB_search on the record and sentence words ("authorization decision … limited warranty left partly unpaid"; "rental car reimbursement entry on the repair order") surfaces the remainder hub and the rental hub |
| Factor doc naming a tier the customer falls on, a mistake to avoid, or task evidence as fact; factor doc pointing at the baseline or another factor | none. The fee-relief phrase "the cancellation fee the cancellation carries" refers to a quantity, not to a document or factor |
| Baseline doc hinting at modification ("unless otherwise", "adjustments may apply", pointer) | none in `remainder_amount_payable`, `rental_reimbursement_amount` or `pro_rata_refund_calculation` |

**Note 1 (policy-side, not a KB verdict).** The rental policy's own `rule` restates its dependency on the authorization in two further sentences:
- "while that repair order carries no approved authorization, no rental reimbursement is due on it";
- "Because a rental on such a repair can be reimbursed under the plan only once the plan has decided the repair order …", which is also the overwrite replaced_by.

The render carries both verbatim in the same policy's baseline doc (`rental_reimbursement_amount` §1 and §3). They are the source's own sentences on the blocked side. They name no other tool or problem, so this is a feature of the source rule and not a rendering addition.

**Verdict: PASS (dependency-form scan).**

## Step 4 notes (policy-side, recorded without changing the verdict)

- **Late-notice wording.** The rule's phrase "to the day of the decision" (compute: NOW) does not say outright that the decision is the remainder authorization being made. The KB carries it verbatim, and its frame "On a KestrelCare … remainder authorization" supports the intended reading. The blind audit reached the GT reading but logged the alternative (the LW decision date, which would give 746.06).
- **Cross-product reads.** The limited warranty daily rate and maximum days used by the credit tiers are purchase-product parameters. The credit doc names them as the included limited warranty's figures for the vehicle program on the Vehicle Purchase Agreements order; they are found in the purchase KB (35.00 a day, 3 days for Kestrel Inspected). Cross-product consistency is outside this skill's detection range.

## Closing (difficulty-level, see task_1 for the shared checklist)

Three part-verdicts for task 0:
- runtime blind audit: **PASS**;
- full-domain two-way scan: **PASS**;
- dependency-form scan: **PASS**.
