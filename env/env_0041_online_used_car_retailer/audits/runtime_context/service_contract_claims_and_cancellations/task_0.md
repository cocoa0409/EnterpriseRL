# Runtime-context blind audit — service_contract_claims_and_cancellations / task 0

Freeze declaration: the blind_answer section below was written and frozen to disk at 2026-10-06T11:34:10Z (UTC) before any source-layer material (extended YAML, task_tools.py, task JSON, GT) was opened. sha256 of the blind_answer body (from the line '## blind_answer' through its end, before the gt_comparison was appended): 14609caeac3832a6c41bba80524f7be37fcd980863b232282a55c59bbb1784a4

## blind_answer

### Scope, visible materials and forbidden list

- Difficulty `service_contract_claims_and_cancellations`, product `warranty`, task 0. Auditor: independent KB-doc audit agent (did not author the docs or the policy-side audit).
- Visible materials actually used:
  - runtime view `audits/_views/runtime/service_contract_claims_and_cancellations/task_0.runtime.json` (sha256 231993e038f65ed612e690d315e111785a897c1a0e461d42208a2ebdfeb9fb42), which holds `frozen_time` 2026-10-06 10:30:00 MST and the simulator script;
  - the system background printed by `rt.py ... 0 context`;
  - the agent/user tool schemas printed by `rt.py ... 0 tools`;
  - title and content of all 69 `docs/warranty/*.json` (the hidden `meta` field was not read; the corpus sha256-of-sha256s is e80227f6d5c83afe46217daba70562280e7e70daee310a9cc5688f4743aa1272);
  - DB records obtained only in tool form through `/tmp/erl0041_rt/rt.py` (sha256 04913afcf7f4cdaa476276bb429e612b74df7fce571cbe362ec74a02b3c54575), with only its docstring read. KB_search was also run through it. A replay of the derived write sequence was run to check that it executes.
  - Two lines of the purchase product's KB (`docs/purchase/warranty_benefit_limits_238d0a20.json`, `limited_warranty_claims_6180b166.json`) were read to see the limited warranty rental per day. They were used only as a cross-check and not as a criterion.
- Not opened: tasks/**/*.json, *.extended.yaml, task_tools.py, blueprint/products/*.yaml, audits/policy_task/**, audits/_views/policy_task/**, worklog.md, document meta, render plans, verification scripts, existing GT or audit conclusions. Every grep was limited to `docs/`.
- DB side is blind. All records below are tool returns.

### 1. What the user expresses; simulator mode

- Target and action: "I traded my Highlander in with you guys and cancelled the KestrelCare plan on it back in August, but I still haven't seen the refund. Can you get that refund issued to me?" He wants the refund on the cancelled plan issued and paid to him now. He authorises bookings on Kestrel's side ("fine with the representative doing whatever has to be booked on Kestrel's side to settle it today").
- The simulator only answers. It gives identity details when asked. It describes maintenance only when asked about maintenance. It gives the transmission repair facts (28 Aug failure, Desert Gear Transmission in Mesa, "an independent repair shop", RO-556872) only when asked about that repair. It gives the 7-day rental only when asked. It runs the rental filing once, with the values the agent states. It never mentions the authorization or the rental on its own.

### 2. Act now, wait, or refuse at the frozen moment

Act now, in three bookings, after identity is verified with three details. A first attempt with phone and DOB returned "only 2 of the required 3 details matched". Grounds:
- the plan is `KestrelCare Gold`, `status active`, not financed (`financed False`, no finance contracts). Payee is the holder ("otherwise it is paid to the holder", Cancellation Terms §4).
- a confirmed request exists: `request_date 2026-08-10, odometer_at_request 88610, cancellation_reason vehicle_sold, request_status confirmed`. It is confirmed, so the 14-day lapse does not apply. The plan history has no cancellation refund ("Each plan has one cancellation refund").
- the refund is not yet fixable. "Cancelling a KestrelCare Plan with Its Refund" says: "A cancellation refund is fixed only after every repair order that a limited warranty decision for the holder left wholly or partly unpaid carries a KestrelCare authorization decision on the plan." It also says: "A cancellation refund is not worked out until each repair order whose limited warranty decision recorded approved rental days, and which carries either no KestrelCare decision yet or an approved one dated no more than the plan's benefit receipt submission days before the refund is worked out, carries a rental car reimbursement entry on the plan." Both states are unmet for RO-556872, as shown in item 6.

### 3. Business objects, keys, rows included and excluded

- Customer `76612bb3-…` (Theo Yarborough).
- Plan `833103fa-04ff-4a46-8694-a1687e4f5def`. VIN 5TDZZRFH4JS523981, price 2640.00, 36 mo / 36000 mi, deductible 100.00, sale 2026-07-09, sold with vehicle, odometer at sale 88140, coverage start 2026-07-15, expiration 2029-07-09, coverage remaining 19249.18.
- Covered vehicle PO `660679ba-…`. `Kestrel Inspected`, `registration_state AZ`, handover 2026-07-15, `completed`.
- Excluded: the second PO `4279b58d-…`, the 2023 Mazda CX-50, `Kestrel Certified Plus`, `delivered`. It is not the covered vehicle. It matters only as the order the trade went toward.
- Trade-in `6dc2e7a6-…`. `trade_vin 5TDZZRFH4JS523981` (= the plan VIN), `purchase_order_id 4279b58d-…`, `status picked_up`, `pickup_date 2026-09-13`.
- Limited warranty decisions on PO 660679ba:
  - RO-552614: transmission, failure 2026-08-02, decision 2026-08-03, estimate 3840, covered 3000, deductible 50, approved, rental_days 2, rental_amount 70.
  - RO-556872: transmission, failure 2026-08-28, decision 2026-08-29, odometer 88860, estimate 4620, covered 3000, deductible 50, approved, rental_days 7, rental_amount 105, towing 75. This is the latest one.
- Plan history:
  - limit established 20000 on 2026-07-15;
  - decision on RO-552614, approved 750.82 on 2026-08-04 (requested 3840, deductible 0, `independent_licensed`);
  - payment 750.82 on 2026-08-06;
  - no decision on RO-556872;
  - no reimbursements;
  - no recoveries.
- Maintenance plan `KestrelCare Maintenance Standard`, active, on the CX-50. One `maintenance_visit_redeemed` on 2026-10-02. It is read for the deductible ladder and does not change the tier (see item 4).

### 4. Scored parameters, formulas and values

**(A) Remainder authorization on RO-556872**

The computation document "KestrelCare Remainder Authorization: Amount Payable to the Facility" gives the method: start from the estimate, subtract the chosen deductible (not below 0), cap at the per-visit limit and the coverage remaining, and round at the end.

Factors found from the records:

| Factor document | Rule and record | Value |
|---|---|---|
| "Coordinating KestrelCare with the Kestrel Limited Warranty: Starting Amount of a Remainder" | latest LW decision (2026-08-29) is approved with a deductible above 0: "estimate less the amount it covered and less that deductible" = 4620 − 3000 − 50 | 1570 |
| "KestrelCare Terms: Deductible on Remainder Authorizations and Maintained Vehicles" | tier 1, "where the Kestrel limited warranty decision approved the repair order and applied a deductible of its own, no plan deductible is taken". The active maintenance plan with a redeemed visit (tier 2) is therefore not reached | 0.00 |
| "KestrelCare Mileage Wear Table for Remainder Authorizations" | odometer 88860 is in 75000–99999 | ×0.90 |
| "Notice of Failure under KestrelCare: Late-Notice Share" | days from failure 2026-08-28 "to the day of the decision" = today's remainder decision, 2026-10-06, which is 39 days and falls in 31–60 | ×0.90 |
| "Repeat Repairs on the Same Vehicle System under KestrelCare" | the plan approved transmission RO-552614 on 2026-08-04, inside three months counted back from 2026-10-06 | ×0.50 |
| "KestrelCare Repair Sales Tax Rates by Registration State" | AZ, "added last" | ×1.056 |

- Result: 1570 × 0.9 × 0.9 × 0.5 × 1.056 = 671.4576. This is below the 8000 per-visit limit and the 19249.18 coverage remaining, so the **approved_amount is 671.46**.
- Booking values: requested_amount 4620.00 (the estimate on the LW decision), deductible_amount 0.00, failure_date 2026-08-28, odometer 88860, component `transmission`, facility `independent_licensed` (from the customer), decision `approved`.
- The decision tests in the Claims Manual all pass:
  - the failure is after the 2026-07-15 / 88140 coverage start;
  - the plan is active, and the failure is before the 2026-09-13 end of use;
  - transmission is covered on Gold;
  - nothing suggests commercial use;
  - maintenance needs proof. The customer says the fluids were serviced at reconditioning and no scheduled service has come due since.
- Cross-check: the same chain applied to the existing RO-552614 decision gives 790 × 0.9 (88520 mi) × 1.0 (2 days) × 1.0 (no earlier transmission) × 1.056 = 750.816, or 750.82. That equals the recorded decision amount.
- Fall-back with the computation document only: 4620 − 100 = **4520.00**.
- Residual reading risk (recorded, not a finding yet): the late-notice clause says "to the day of the decision" with the failure date taken "(as recorded on the Kestrel limited warranty decision)". Reading "the decision" as the LW decision (2026-08-29) gives 1 day and 100%, which makes the amount 746.06. I read it as the remainder decision being made, because the clause is a rule "on a KestrelCare … remainder authorization". The text does not say so outright.

**(B) Rental reimbursement on RO-556872, filed by the holder**

The computation document "KestrelCare Rental Car Reimbursement: Nights, Rate and Receipt Window" gives the method: nights from the failure date on the plan's approved authorization to the authorization date, capped at the rental maximum days, times the plan's rental per day.

| Factor document | Rule and record | Value |
|---|---|---|
| "KestrelCare Rental Benefit Q&A: Counting the Rental Nights" | the LW decision is approved and recorded rental days 7 | 7 nights |
| "KestrelCare Benefits Schedule Note: Rental Night Limit on Major Repairs" | LW estimate 4620 ≥ 4000; approved transmission decisions on the plan in the last 12 months are RO-552614 (2026-08-04) and RO-556872 (booked today), so 2: cap 5 + 3 = 8 | 7 nights kept |
| "KestrelCare Rental Rate Card by Vehicle Program" | covered PO is `Kestrel Inspected`, so compact | 40.00 |
| "KestrelCare Coordination of Benefits: Rental Already Paid by the Limited Warranty" | LW paid 105.00 for RO-556872. Its rate (35.00/day per the purchase KB; 105/7 = 15 on the record itself) is below 40 in every reading: 7 × 40 − 105 | 175.00 |
| "Rental Sales Tax on KestrelCare Rental Reimbursements" | AZ, applied to "the rental amount for the nights" | ×1.083 → 189.525 |
| "KestrelCare as Secondary Coverage: Share of the Rental Reimbursement" | covered 3000 / estimate 4620 = 0.649 ≥ half, "applied last" | ×0.75 |

- Result: 142.14375, so **reimbursement_amount 142.14 with rental_days 7**.
- Fall-back with the computation document only: 39 nights, capped at 5, × 45.00 = **225.00**.
- Residual reading risks:
  - Night cap: if the authorization booked today were not counted, there would be 1 earlier approval, a cap of 6 and 6 nights, giving 109.65. The doc counts "the claim decision entries with decision approved on the KestrelCare plan's history … dated within the last twelve months", and the rental is figured after the authorization is on the history. Unlike the comeback and repeat-diagnosis docs, it has no "other than that decision itself".
  - Tax and credit order: the credit table defines "Rental amount for the nights" as the credited figure, and the tax doc multiplies "the rental amount for the nights", so I applied the credit first. Applying the tax first would give 148.68.

**(C) Cancellation refund**

The computation document "KestrelCare Cancellation Refund Worksheet" applies:
- Part 1: the request is on day 32, inside the 60-day free look, but a claim has been paid (750.82). The settlement is therefore pro rata. The reason is not "vehicle returned".

| Factor document | Rule and record | Value |
|---|---|---|
| "KestrelCare Cancellations: Day from Which Plan Use Is Counted" | sold with the vehicle; handover 2026-07-15 is later than the sale on 2026-07-09 | use from 2026-07-15 |
| "When the Vehicle Leaves the Holder: End of KestrelCare Plan Use" | trade-in on the plan VIN, pickup 2026-09-13 | use to 2026-09-13 |
| same document, miles measure | "the miles measure still reads the odometer on the cancellation request" | miles input 88610 |
| "KestrelCare Pro Rata Refunds: Time Measure by Registration State" | AZ: whole months over term months. 15 Jul → 13 Sep is 1 whole month | 1/36 = 0.027778 |
| (miles fraction) | (88610 − 88140) / 36000 | 0.013056 |
| "KestrelCare Fee Schedule: Cancellation Fee by Reason" | reason on the confirmed request is `vehicle_sold` | 25.00 |
| "Cancellation Fee Relief for Holders Who Stay with Kestrel" | the covered vehicle was traded in to Kestrel toward PO 4279b58d, which is `delivered`, so 50% | 12.50 |
| "Claims Charged against a KestrelCare Cancellation Refund" | Gold deducts claims. Claim payments 750.82 − recovered 0, plus unmatched approvals (750.82 + 671.46 − 750.82 = 671.46), plus reimbursements 142.14 | 1564.42 |

- Used share = 0.027778, so d = 2640 × 35/36 = 2566.6667.
- Refund = 2566.6667 − 12.50 − 1564.42 = 989.7467, so **refund_amount 989.75**.
- `cancellation_basis pro_rata`.
- `effective_date 2026-09-13`, because "The plan's cancellation takes effect on the day to which its use is counted". The old clause "The request date is the cancellation effective date" is shown as no longer in force.
- Fall-back with the worksheet only: 2640 × (1 − 32/1096) − 50 − 750.82 = **1762.10**. The worksheet itself gives no sign of a variation.

### 5. Executable tool sequence, owners, dependencies, terminal state

1. Look up and verify identity (agent).
2. Run the lookups listed above (agent).
3. Agent: unlock and call `authorize_stack_remainder_2296c771`. Arguments: SC 833103fa…, RO-556872, 2026-08-28, 88860, transmission, independent_licensed, approved, 4620.00, 0.00, 671.46.
4. Agent: `unlock_user_discoverable_tool file_rental_reimbursement_5fdd83af` and hand over the values. User: runs it with SC, RO-556872, 7, 142.14.
5. Agent: unlock and call `cancel_plan_with_refund_1804bd93`. Arguments: SC, 2026-09-13, pro_rata, 989.75.

- Order: 3 must come before 4 ("booked only after the repair order … carries an approved KestrelCare authorization"). Both 3 and 4 must come before 5 (the two refund conditions). Step 4 must also come before 5 because a benefit is reimbursed only on a plan that is active or exhausted (General Terms Art. 7), and step 5 sets the plan to cancelled.
- A replay in the rt harness returned `recorded` / `filed` / `cancelled`, with closed_date 2026-09-13.
- Terminal state: plan cancelled, closing date 2026-09-13; one approved decision on RO-556872; one rental reimbursement on RO-556872; one cancellation refund of 989.75 to the holder.

### 6. Problem tree from the visible materials alone

Root: **cancellation refund on the plan** (the customer's ask).

**Hop R→A: root waits on a KestrelCare authorization of RO-556872.** State-derived.
- Sentence: "A cancellation refund is fixed only after every repair order that a limited warranty decision for the holder left wholly or partly unpaid carries a KestrelCare authorization decision on the plan."
- Records: both LW decisions left part unpaid (3840 − 3000 and 4620 − 3000). RO-552614 already has a plan decision. RO-556872 has none.
- Where the write is found: KB_search with the sentence's words ("authorization decision … limited warranty left partly unpaid") lists "KestrelCare Remainder Authorization after a Limited Warranty Decision". That document reads "When a Kestrel limited warranty decision … has already decided a repair order and left part of it unpaid, the KestrelCare … authorization of the same repair order settles what the plan still owes on it. The authorization is a KestrelCare claim decision on that repair order", booked by `authorize_stack_remainder_2296c771`.

**Hop R→B: root waits on a rental reimbursement entry on RO-556872.** State-derived.
- Sentence: "A cancellation refund is not worked out until each repair order whose limited warranty decision recorded approved rental days, and which carries either no KestrelCare decision yet or an approved one dated no more than the plan's benefit receipt submission days before … carries a rental car reimbursement entry on the plan."
- RO-556872: rental_days 7, and it has no decision now (after hop A, an approved one dated today), so the condition applies.
- RO-552614: rental_days 2, but its approved decision is dated 2026-08-04. That is 63 days, more than the 30-day "Receipts due" in the Benefits Schedule, so it is excluded.
- Where the write is found: "KestrelCare Rental Car Reimbursement Claims Filed by the Holder" says it "is booked on the plan's history as a rental car reimbursement entry on the repair order". It is a user tool handed over by the agent.

**Hop B→A: rental waits on the authorization.** State-derived.
- Sentence: "A rental car reimbursement is booked only after the repair order it belongs to carries an approved KestrelCare authorization on the plan."
- That approval is the write from hop A.

**Pre-solved hops: none.** No document names another problem's tool beside a prerequisite sentence, and none gives a route or chain.

**Handling order:** A (authorization) → B (rental, owned by the user) → R (cancel with refund).

### Two-way counter-proof

**"Only do what was asked" (cancel and refund now) is excluded:**
- the refund may not be fixed while RO-556872 (LW left 1620 unpaid) carries no KestrelCare authorization decision, and while it lacks a rental entry (both sentences above);
- cancelling first would also make the rental unpayable: "A benefit is reimbursed only on a plan whose status is active or exhausted".

**Closest alternatives and what excludes them:**
- Full free-look refund: excluded by "no claim has been paid", since the history has a claim payment of 750.82.
- Effective date or use counted to the request date (2026-08-10): excluded. The request-date effective clause is shown as no longer in force. "End of KestrelCare Plan Use" counts to the trade-in pickup on the plan VIN.
- Use counted from the sale date (2026-07-09): excluded by the handover-later tier.
- Day-based time fraction: excluded by the AZ row.
- Plan fee 50: excluded by the vehicle_sold fee of 25.00 and the 50% trade-in share.
- Claims charged as payments only: excluded by the "Claims Charged" rule, which adds unmatched approvals and reimbursements on a claim-deducting level.
- Rental for RO-552614: excluded by the 30-day window.
- CX-50 program or plan (Certified Plus rate 50.00): excluded because the covered vehicle's PO is the one read.
- Maintained-holder 50% deductible: excluded by deductible tier 1.
- Payee: no finance contract, so the holder.

**Factor findability (record words → document):**
- LW `covered_amount`/`deductible_amount` → "Starting Amount of a Remainder";
- `maintenance_visit_redeemed` → "Deductible … Maintained Vehicles";
- `odometer_at_failure` → "Mileage Wear Table";
- `failure_date` → "Late-Notice Share";
- approved `transmission` decisions → "Repeat Repairs on the Same Vehicle System";
- PO `registration_state AZ` → the repair tax, rental tax and time-measure documents;
- LW `rental_days` → "Counting the Rental Nights";
- LW `repair_estimate` → "Rental Night Limit";
- PO `variant_name Kestrel Inspected` → "Rental Rate Card";
- LW `rental_amount` → "Rental Already Paid by the Limited Warranty";
- LW `covered_amount` → "Secondary Coverage";
- PO `handover_date` / plan `sold_with_vehicle` → "Day from Which Plan Use Is Counted";
- trade-in `pickup_date` → "End of KestrelCare Plan Use";
- request `cancellation_reason vehicle_sold` → "Cancellation Fee by Reason";
- trade-in `purchase_order_id` / PO `delivered` → "Fee Relief";
- plan history approvals and reimbursements → "Claims Charged".

None of the three computation documents says that a variation exists.

contamination_disclosure: none. The orchestrator brief contained no scored values. No task JSON, extended YAML or policy-task audit was opened.

## gt_comparison

**Reveal.** The source layer was revealed at 2026-10-06T11:35Z, after the blind answer had been frozen at 11:34Z. The revealed material was:
- `warranty.extended.yaml`;
- `task_tools.py` (parameter contracts only);
- `tasks/0.json`: `evaluation_criteria`, `computations`, `prerequisite_closure`, `required_documents`.

The blind_answer above was not edited. The corpus hash at reveal is unchanged (e80227f6…1272).

### Item-by-item comparison

| Item | Blind answer | Source / GT | Same? |
|---|---|---|---|
| Root, act vs wait | act now, after two prerequisite writes | root `warranty_ext_cancellation_settlement`; `prerequisite_closure` edges to `warranty_ext_stack_remainder_authorization` (form state) and `warranty_ext_rental_reimbursement_settlement` (form state); rental → stack remainder (form state) | same |
| Authorization args | RO-556872, 2026-08-28, 88860, transmission, independent_licensed, approved, 4620.00, 0.00, **671.46** | identical; `expected 671.46`; `baseline_result 4520.0` | same, and fall-back same (4520.00) |
| Authorization factors | starting 1570; deductible 0; wear 0.9; repeat 0.5; late notice 0.9 (39 days to today); tax 1.056 | identical tiers; late notice is `notice_days = DAYS(lw_failure_date, NOW)` | same |
| Rental args | RO-556872, 7 days, **142.14** | identical; `expected 142.14`; `baseline_result 225.0` | same, and fall-back same (225.00) |
| Rental factors | 7 nights; cap 8 (counts the new approval); 40.00; credit 280 − 105; tax ×1.083 after the credit; ×0.75 | identical. The trace says "two approved transmission repairs … (RO-552614 and the new RO-556872 decision) → cap 8". The rule says "The limited warranty's rental is credited first, the rental sales tax is then added to that result, and the secondary share is applied last" | same |
| Cancel args | 2026-09-13, pro_rata, **989.75** | identical | same |
| Refund factors | use 07-15 → 09-13; AZ months 1/36; fee 25 × 0.5; claims charge 1564.42 | identical compute (use_start, use_end, time_fraction, reason_fee, fee_share, claims_charge) | same |
| Order and owners | A (agent) → B (user tool) → R (agent) | evaluation order unlock/authorize → unlock user/rental (user) → unlock/cancel | same |

### Hop marks against the declared forms

All three edges are declared `form: state`. The blind answer marked all three hops state-derived. No hop was pre-solved.

### Residual reading risks recorded in the blind answer, resolved by the source

1. **Late-notice "to the day of the decision".**
   - The source rule uses the same words, and its compute counts to NOW (the remainder decision day). The KB carries the wording verbatim, so the KB neither adds nor drops anything here. The blind reading matched.
   - Policy-side wording note: the source sentence does not say outright which decision is meant. The KB inherits that wording faithfully, and its framing ("On a KestrelCare … remainder authorization") supports the intended reading.
2. **Night cap counting the new authorization.** The source compute counts every approved same-system decision in 12 months at the time the rental is figured. The KB definition ("the claim decision entries with decision approved on the KestrelCare plan's history … dated within the last twelve months") entails the same. Matched.
3. **Credit before tax.** The source pins the order explicitly. The KB carries it through the defined term "rental amount for the nights": the credit table yields it and the tax document multiplies it. The secondary-share document says "applied last". This is entailed at the same strength. Matched.

### Remaining checks

- **Tool schema, owners and effects.** The task_tools contracts match the hub parameter tables, and the receipts match the rt replay. No disagreement.
- **Contamination.** None.

**Verdict: PASS (runtime blind audit).**
