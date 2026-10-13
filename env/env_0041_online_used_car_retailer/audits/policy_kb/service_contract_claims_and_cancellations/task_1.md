# Policy-KB bijection audit — service_contract_claims_and_cancellations / task 1

## Audit record

- Auditor: independent KB-doc audit agent. Written after the runtime blind audit was frozen at `audits/runtime_context/service_contract_claims_and_cancellations/task_1.md` (blind body sha256 cb25a35a09bce594d2ab79fddb84fcf5b7c2e3dec10c2f7339238e594a641bfc).
- Source: `warranty.extended.yaml` and `task_tools.py`. Task 1's scored policies are:
  - `warranty_ext_trip_interruption_reimbursement` (root);
  - `warranty_ext_release_repair_payment`;
  - `warranty_ext_diagnostic_time_payment`;
  - `warranty_ext_claim_overpayment_recovery`.
- Their base policies are `warranty_claims` and `warranty_benefits`, together with the variant parameters they read.
- Corpus hash: e80227f6d5c83afe46217daba70562280e7e70daee310a9cc5688f4743aa1272 (unchanged).
- Meta was used only to locate candidate homes.

## Entry conditions (Step 0)

These are as for task 0:
- policy-task PASS (round 4);
- `check_docs.py` DOCS OK (69 docs);
- `check_traceability.py` TRACEABILITY OK;
- the runtime view and DB path were provided, and the hashes match.

## source_to_kb

### A. `warranty_ext_claim_overpayment_recovery` (hub `claim_payment_recovery_booking_885eaee7`)

| Source atom | KB home | Equivalence |
|---|---|---|
| Rule: recover from the facility, starting from the most recent claim payment and the decision it settled | `recovery_of_erroneous_payment_bdf26352` (baseline): "Which payment" | equal |
| Baseline (whole payment; within payment_recovery_window_days counted from the payment date; rounded) | the same doc. The 180-day window appears in figures there and in the timelines facet | complete. No variation hint |
| Factor `payment_error_measure` (3 method tiers) | `measuring_a_payment_error_716cdc5a`. The coverage before the payment is stated as "the coverage remaining the plan shows now plus that payment", which restates compute `coverage_before_payment` | complete |
| Factor `aged_recovery_share` (30/90; 0.9/0.75; within the window) | `age_of_payment_recovery_share_729fce72` | complete |
| Factor `facility_collection_share` (0.95/0.98/1) | `collection_share_by_facility_type_fbfff4e3` | complete |
| Factor `repeat_error_handling` (≥ 2 → 50.00; 1 → 25.00; 0 → 0; recoveries in 12 months) | `repeat_error_handling_charge_935216e5` | complete |
| Assembly ("error × aged × collection + handling, rounded at end; restores coverage") | aged doc ("taken of the error"); collection doc ("on an amount being recovered"); handling doc ("added in full to the amount figured on the payment itself, and the total is rounded"); hub (restores the limit) | equivalent |
| Overwrite of `warranty_claims` (recovery clause) | Claims Manual §C: quoted and marked no longer in force | retired surface correct |
| `prerequisite: []`; tool contract | hub table | equal |

### B. `warranty_ext_diagnostic_time_payment` (hub `diagnostic_time_payment_booking_b35c3256`)

| Source atom | KB home | Equivalence |
|---|---|---|
| **Prerequisite** → overpayment_recovery. Form state. "A diagnostic time payment is not booked until every claim payment on the plan that exceeds the approved amount of the decision it settled carries a recovery entry." | Verbatim in the hub ("Holding condition"), with a same-form restatement in the same doc ("Equivalently: …"). Found in no other document | Connective and form are intact. **Resolution basis:** the recovery hub ("booked on the plan's history as a payment recovery entry naming the claim payment it recovers"), and the records (payment 7fb78265 of 1480 against approved 1180, with no recovery). Strength is the same |
| Rule: paid as its own claim payment, read from the plan's most recent approved decision | hub "Purpose" | equal |
| Baseline (one hour at the labor rate cap; × rate, rounded, never above coverage) | `diagnostic_time_amount_7dc83ba0`, plus the limits card for the cap and for "diagnostic time paid" | complete. No variation hint |
| Factor `diagnostic_system_hours` (2.0 / 2.5 / 1) | `diagnostic_hours_by_vehicle_system_6b9e1617` | complete |
| Factor `program_equipment_hours` (1.0 / 0.5 / 0) | `program_equipment_diagnostic_hours_ad9bde3f` | complete |
| Factor `long_diagnosis_adjustment` (> 5 days × 1.5; > 2 days + 1.0; else unchanged) | `long_diagnosis_hours_d6667d28` ("acts on the whole of the diagnostic hours allowed") | complete |
| Factor `repeat_diagnosis_share` (0.5 / 0.75 / 1; excludes the decision itself) | `repeat_diagnosis_on_same_system_39c2f133` | complete |
| Factor `diagnostic_hourly_rate` (cap + 20.00 / 95.00 / cap) | `diagnostic_hourly_rate_by_facility_3b0b7200` | complete |
| Assembly ("system and program hours added first; long-diagnosis applied to that sum; repeat share last; × rate") | program doc ("added to the diagnostic hours allowed for the vehicle system"); long-diagnosis doc ("acts on the whole of the diagnostic hours allowed on the repair order"); repeat doc ("Last, to the diagnostic hours, immediately before they are multiplied by the hourly rate") | equivalent |
| Overwrite of `warranty_claims` approval clause | Claims Manual: retired | correct |
| Tool contract | hub list | equal |

### C. `warranty_ext_release_repair_payment` (hub `repair_facility_payment_booking_de313df5`)

| Source atom | KB home | Equivalence |
|---|---|---|
| **Prerequisite** → overpayment_recovery. Form state. "The payment of an approved decision is worked out only after every claim payment on the plan that exceeds the approved amount of the decision it settled carries a recovery entry." | Verbatim in the hub ("Conditions on working out the payment"). Found in no other document | intact. Basis as in B |
| **Prerequisite** → diagnostic_time_payment. Form **action** (declared fallback). "The repair payment on a decision is figured only after the facility's diagnostic time on that repair order has been paid." | Verbatim in the hub. Found in no other document | Connective and action form are intact. **Resolution basis:** the diagnostic hub ("the facility's diagnostic time on that repair order is paid to the facility as its own claim payment"). Strength is the same. `fallback_reason` has no home in prose, which is correct |
| Rule: pays the most recent approved decision to the facility holding the vehicle | hub "Purpose" | equal (see the observation in dependency_form) |
| Baseline (approved amount, never above coverage at payment, rounded) | `repair_payment_amount_337197b4` | complete. No variation hint |
| Factor `limited_decision_refigure` (3 method tiers) | `refiguring_the_approved_amount_eaa9252d`: the tiers plus a 4-row table, one row splitting "below it / equal" into an explicit case | complete, same strength |
| Factors `facility_agreement_allowance` (0.02 / 0.01 / 0), `exchanged_unit_core_credit` (0.04 / 0.02 / 0), `comeback_repair_share` (0.6 / 0.85 / 1), `parts_program_uplift` (0.10 / 0.05 / 0), `late_payment_interest` (2/10 days; 0.01 / 0.02) | `facility_agreement_allowance_acd78138`, `core_credit_for_exchanged_units_b9468c58`, `comeback_repair_share_bdae5a17`, `parts_uplift_by_vehicle_program_1415fb31`, `late_payment_interest_to_facilities_1e8129be` | all tiers complete |
| Assembly order (allowance and core credit → comeback → uplift → interest last; rounded at end; never above coverage) | Each factor doc says "before the payment is compared with the coverage remaining". The baseline says "once, to the cent, on the final figure". All steps are multiplicative | equivalent |
| Overwrite of the approval clause | Claims Manual: retired | correct |
| Tool contract | hub table | equal |

### D. `warranty_ext_trip_interruption_reimbursement` (hub `trip_interruption_claim_filing_e42adc49`)

| Source atom | KB home | Equivalence |
|---|---|---|
| **Prerequisite** → release_repair_payment. Form **action** (declared fallback). "A trip interruption reimbursement is not fixed until the facility has been paid for the repair work on the repair order that stranded the holder." | Verbatim in the hub ("Timing of the amount"). Found in no other document | Connective and action form are intact. **Resolution basis:** the repair-payment hub ("The repair work on the … plan's most recent approved decision is paid to the facility that holds the vehicle"). Strength is the same |
| Rule: coverage, minimum distance, figured on the most recent approved decision, receipts from release, once per RO | hub "Coverage"; `trip_interruption_amount_d5e62bf6` | equal |
| Baseline (trip days failure → release, where release = latest RO claim payment or else the decision date; capped at max days; × per-day; rounded) | `trip_interruption_amount_d5e62bf6`, plus the benefits schedule figures | complete. No variation hint |
| Factor `failure_day_count` (> 2 days +1; ≤ 2 and network −1; else 0) | `counting_the_failure_day_7889fdcb` (applied before the cap) | complete |
| Factor `trip_day_cap` (≥ 2000 AND engine/transmission +2; ≥ 1000 +1; else max) | `trip_day_limit_on_major_repairs_57466de5` | complete |
| Factor `overflow_day_payment` (3 method tiers, days booked) | `trip_days_beyond_the_limit_a98922ee` | complete |
| Factor `program_trip_allowance` (150 / 125 / plan) | `trip_allowance_by_vehicle_program_726ae36a` | complete |
| Factor `recent_trip_share` (6/12 months; 0.5 / 0.75 / 1) | `repeat_trip_interruption_share_16f6a3f2` | complete |
| Factor `repair_coverage_share` (< half 0.6; < whole 0.85; else 1) | `trip_share_by_repair_coverage_d9f74d9a` | complete |
| Assembly ("× recent-trip share, then × repair-coverage share, rounded at end") | both share docs ("multiplies the amount for the trip days"; "rounded to the cent only at the end") | equivalent |
| Overwrite of the `warranty_benefits` trip clause | `repair_benefit_terms` Art. 4: retired. Art. 7 (active or exhausted) is kept in force | correct |
| Tool contract `file_trip_interruption_claim_d37559b2` (user owner) | hub table | equal |

## kb_to_source

- Every normative sentence of the 26 documents of these four policies, and of the base docs read, traces to a rule sentence, an overwrite, a variant parameter, a compute binding or a tool contract.
- Additions, omissions and rewrites: none at entailment level.
- One descriptive sentence has no home in the repair-payment policy's own rule: "The payment lets the facility release the vehicle" (repair-payment hub, Purpose). Its semantics is borne by the trip rule ("the facility releasing the vehicle when it is paid") and by the rental rule ("the release of the vehicle by the repairing facility marking that completion"). It is a same-source restatement and not a new normative claim. Recorded; not RED.
- Cross-problem operational guidance: none.
- Opening world state written as policy fact: none. Every example is hypothetical, and none reproduces task 1's figures (RO-558204, 5120/6960, 1480/1180, 2026-03-20 trip).

## bijection_verdict

**PASS.**
- All four prerequisite sentences stand verbatim on the blocked hubs only, in their declared forms (two state, two action with fallback).
- All 21 declared factor ladders of the four policies are complete, with every tier exact.
- The retired surfaces are correct.
- This is the first revision.

## dependency_form

| Check | Result |
|---|---|
| State-form sentence restated as an action | none. The diagnostic hub's "Equivalently: while any claim payment … without a recovery entry, no diagnostic time payment is booked" is same-form and in the same doc |
| Action-form sentence restated naming a tool, policy or document | none |
| Another problem's tool in a blocked problem's docs | none (each tool only in its own hub) |
| Dependency or order beyond the source sentences; aggregation; route | none. The repair hub section "Conditions on working out the payment" carries only that policy's own two source sentences |
| Wrong vs right readings or cross-problem walk-throughs | none |
| Task-mirroring titles or openings | none. Titles are general, for example "KestrelCare Trip Interruption Claims Filed by the Holder" (the `on_request` subject), "KestrelCare Repair Payments to the Facility Holding the Vehicle", "KestrelCare Claim Payment Recoveries" |
| Depended-on doc reachable only via borrowed phrasing | no. Searches for "facility paid for the repair work on the repair order" and "claim payment exceeds approved amount recovery entry" rank the repair-payment hub and the recovery documents first |
| Factor docs naming a tier the customer falls on, a mistake, task evidence, or pointing at the baseline or another factor | none |
| Baselines hinting at modification | none |

**Observation (no verdict impact).** As noted above, the repair-payment hub's "The payment lets the facility release the vehicle" uses the trip policy's release concept in the depended-on document. It does not name the trip problem, its tool or a route, and does not state that anything waits on the payment. It is therefore not a disclosure of "who waits on it" under the Step-3b list. The trip prerequisite sentence already resolves the hop by its own words ("the facility has been paid for the repair work").

**Verdict: PASS (dependency-form scan).**

## Step 4 notes (policy-side)

None that change this task's verdict.

## Difficulty closing checklist (Step 5)

**Audit files, one-to-one with the tasks:**
- `audits/runtime_context/service_contract_claims_and_cancellations/task_0.md` and `task_1.md`: blind_answer frozen, with gt_comparison appended. Both PASS.
- `audits/policy_kb/service_contract_claims_and_cancellations/task_0.md` and `task_1.md`: source_to_kb, kb_to_source, bijection_verdict, dependency_form. All PASS.
- No old revisions exist.

**Coverage of the difficulty's source:**
- The difficulty's seven extended policies are all covered between the two tasks: stack remainder, rental, cancellation, recovery, diagnostic, repair payment and trip.
- Their 39 factor ladders (6+6+6+4+5+6+6) are carried in full.
- Their 7 prerequisite sentences are verbatim on the blocked side only (mechanical scan over all products' docs).
- The overwritten base clauses are retired, not dropped. No undeclared retirement was found.
- No tool name, route or aggregated chain appears beyond the sentences.

**Gate re-run on the final form (2026-10-06T11:37Z; corpus unchanged since the blind audit):**
- `.venv/bin/python skills/erl-kb-doc-render/scripts/check_docs.py env/env_0041_online_used_car_retailer warranty` gave `[PASS] mechanical gates: …` and `DOCS OK`.
- `.venv/bin/python skills/erl-task-instantiate/scripts/check_traceability.py env/env_0041_online_used_car_retailer/tasks/service_contract_claims_and_cancellations` gave `TRACEABILITY OK`.

**Coverage gaps:**
- Cross-product contradictions (for example with the purchase KB's limited-warranty rental figures) are outside this skill's range.
- Base products claimed by no difficulty are not audited here.

**Per-task part-verdicts:**

| Task | Runtime | Bijection | Dependency-form |
|---|---|---|---|
| 0 | PASS | PASS | PASS |
| 1 | PASS | PASS | PASS |

**Difficulty rendering: PASS.**
