# mold_remediation_jobs — worklog (M=2)

## Draw
`draw_counts.py --tasks 2`: task 0 prerequisite_problems=2, factor_counts=[6,6,5]; task 1 prerequisite_problems=1, factor_counts=[4,4].

## Scope ledger
| task | policies (root last) | tools | owner=user |
|---|---|---|---|
| 0 | mold_ext_presample_line, mold_ext_workplan_line, mold_ext_signing_deposit | book_mold_presample_d4275783, book_mold_workplan_1501986a, sign_mold_agreement_2b99f603 | sign_mold_agreement_2b99f603 (F1(a)+(b): by:user signing + its grouped deposit, paid in the secure channel) |
| 1 | mold_ext_disposal_line, mold_ext_insured_share | book_mold_disposal_772b05b2, pay_mold_insured_share_5816092f | pay_mold_insured_share_5816092f (F1(b)) |

## Structural findings that shaped the design
- Containment (authorized -> remediating) is by:system, so nothing the agent writes can follow a signing in one call; the signing is the root of its tree and its prerequisites are writes legal on a scheduled job.
- check_extended rejects own-category CFIELD/XSUM, so every value_input edge sits on one job.
- check_extended rejects a factor whose bindings read only job fields: every factor reads history, a date span or another category.

## Prerequisite sentences (four-point test)
| edge | sentence | form/direction | single resolving write |
|---|---|---|---|
| deposit -> presample | "The signing deposit is fixed only after the job's charge lines carry the pre-removal asbestos sampling owed on a building built before the asbestos sampling year cutoff." | state / affirmative | only mold_ext_presample_line books asbestos_sampling on a scheduled job |
| deposit -> workplan | "The signing deposit is not worked out until the job's charge lines carry the work-plan visit owed on a tier that requires a protocol." | state / negated | only mold_ext_workplan_line books the work-plan supervisor_labor line |
| share -> disposal | "The insured's own share is not worked out until the job's charge lines carry the bagged debris haul-off owed for the drywall or insulation removed on the job." | state / negated | only mold_ext_disposal_line books debris_disposal |
"Owed" excludes company_warranty jobs in every resolver rule (no line of any kind on a warranty job).

## XF A1 — factor-reads table (round 2)
| policy | factor (effect) | reads (all own bindings unless noted) |
|---|---|---|
| presample | prior_results (param) | XLATEST water asbestos_sampling date, F(opened_date), K, P(asbestos_sampling_fee) |
| presample | building_age_set (param) | building_age (MONTHS year_built -> opened), F(growth_location) |
| presample | lab_turnaround (method) | lead_days (DAYS opened -> start), P(asbestos_sampling_fee) baseline param |
| presample | documentation_set (param) | CFIELD claims public_adjuster_name, CPARAM carrier_referral_required |
| presample | contaminated_handling (param) | CFIELD water_category |
| presample | water_crew_collection (param) | CFIELD water opened/drying_start/drying_complete/cancelled dates vs F(opened_date) |
| workplan | water_footprint_walk (method) | CFIELD water affected_area_sqft, K walk rate / thresholds |
| workplan | claim_coordination (param) | CFIELD public_adjuster_name, CPARAM carrier_referral_required |
| workplan | regulated_planning (param) | XLATEST water lead_safe_setup / asbestos_sampling dates vs F(opened_date) |
| workplan | moisture_verification (param) | CFIELD water drying dates and outcome vs F(opened_date) |
| workplan | plan_lead_time (param) | DAYS opened -> start |
| workplan | overhead_survey (param) | CFIELD water_class |
| deposit | coverage_credit_tier (param) | CFIELD claims status, mold_sublimit |
| deposit | notice_raise_tier (method) | DAYS NOW -> start, P(self_pay_deposit_amount) |
| deposit | lead_prepayment (param) | XCOUNT water lead_safe_setup, F(growth_location), F(year_built) |
| deposit | contamination_raise_tier (param) | CFIELD water_category |
| deposit | payment_route_raise (param) | CFIELD public_adjuster_name, CPARAM accepts_contractor_direct |
| disposal | debris_class (param) | CFIELD water_category |
| disposal | bagging_streams (method) | SUM drywall / insulation quantities |
| disposal | haul_trips (param) | LATEST removal dates, F(containment_date) |
| disposal | wet_debris (param) | CFIELD water drying_outcome, XCOUNT water monitoring_visit lines |
| share | coverage_allowance (param) | CFIELD status, mold_sublimit, CPARAM accepts_contractor_direct |
| share | ordinance_carve (param) | SUM regulated lines, CFIELD ordinance_law_limit, own status read |
| share | declined_line_writedown (method) | CPARAM denied_line_billable_to_customer, XSUM carrier_denied_line write-offs, EXISTS water/fire/rebuild/contents on the claim, CFIELD estimate_amount; plain mold_covered |
| share | program_price_writedown (method) | CPARAM program_price_writeoff_allowed, program_pricing_discount_pct, XSUM program_price_adjustment write-offs, CFIELD estimate_amount; plain mold_covered |
No factor reads another factor's binding or output. Assembly lives in plain bindings (net_scope, visit_hours, covered_left, carrier_payable, result) and each rule states it once in a generic sentence naming roles (credit, raise, addition, write-down, coverage limit, amount carried under other coverage), not factor quantities.

## XF A6 — T1/T2
T1: every factor_sensitivity.baseline_result differs from expected (check_compute PASS, both tasks).
T2: additive / replaced-input factors move result alone on any world on a non-fall-through tier. In the share, the two write-downs come off the charge total directly, so they move result whether or not the coverage limit binds; coverage_allowance moves result whenever covered_left > 0; ordinance_carve moves result only when the coverage limit binds (it is paid outside the cap) — task 1's world is such a world.

## XF A7 — method factors, all-pairs (round 2)
| factor | T1 vs T2 | T1 vs T3 | T2 vs T3 |
|---|---|---|---|
| lab_turnaround | max(min fee, pct x tier fee) vs flat fee — pass | max op vs none — pass | flat non-zero vs none — pass (nothing-tier clause) |
| water_footprint_walk | threshold/rate + stepped ceil over the excess vs max(base, area / rate) — pass (different operation on the area input); monotone across the 300 sq ft boundary (3.00 h at 300, 3.50 h at 301) | adds area input + ceil — pass | adds area input + max, floor live on 150-200 sq ft — pass |
| notice_raise_tier | max(min, pct x deposit) vs flat — pass | max op — pass | flat vs none — pass |
| bagging_streams | two separate ceilings vs max(min loads, ceil) — pass | two ceilings vs one — pass | max floor, live: roll-off minimum 4 loads binds on 401-640 sq ft where ceil(dw/160) = 3 or 4 — pass |
| declined_line_writedown | whole write-off total vs total x min(1, covered/estimate) — pass (adds estimate input, ratio, min) | input vs 0 — pass | prorated vs 0 — pass |
| program_price_writedown | pct x covered vs write-offs x min(1, covered/estimate) — pass (different inputs) | pct op vs 0 — pass | prorated vs 0 — pass |
The round-1 protocol_review factor (max of two constants) and the round-1 coverage_allowance method label are gone: coverage_allowance is now a parameter factor (sublimit / pending percentage of the sublimit / 0).

## XF B2 — decoy / absent / edge probes (scratch probe2.py, opening worlds)
| world | presample | workplan | deposit | disposal | share |
|---|---|---|---|---|---|
| base | 450.00 | 707.96 | 1545.00 | 838.00 | 720.79 |
| decoys: cancelled water job + lead line, withdrawn AOB claim with PA, foreign carrier_denied_line write-off (same customer) | 450.00 | 707.96 | 1545.00 | 838.00 | 720.79 |
| both links absent | 835.00 | 219.71 | 1735.00 | 578.00 | 7099.66 |
| water link absent | 945.00 | 268.54 | 1035.00 | 578.00 | 720.79 (water job still linked to the claim) |
| claim link absent | 340.00 | 659.14 | 2245.00 | 838.00 | 7099.66 |
| scheduled start = opened date | 593.00 | 732.38 | 1745.00 | 838.00 | 720.79 |
| company_warranty funding | 0 | 0 | 0 | 0 | (no lines on a warranty job) |
| claim estimate 0.00 (zero division) | 450.00 | 707.96 | 1545.00 | 838.00 | 366.45 (write-offs taken whole) |
| water drying start after opened date | 485.00 (partial credit) | 659.14 | 1545.00 | 838.00 | 720.79 |
All reads key on the job's own water_job_id / claim_file_id; XLATEST compares dates only (one value per date, no tie issue); every absent record falls to its stated fall-through; the presample line is always above 0.00 (lowest standard set 85.00 > largest credit 75.00).

## XF B5 rounding
Compute uses RND(x + 1e-9, 2); tools use the exact Decimal half-up helper. Scored, baseline and sensitivity figures: none within 1e-6 of a half cent (closest: 707.9625, 512.6625, 610.3125, 659.1375, 255.6359, 615.3260). Probe-only figure 732.375 (7.5 h, same-day probe, not scored) is the DSL-known residue.

## XF D7 — events written and their triggers
mold_remediation_charge (asbestos_sampling, supervisor_labor, debris_disposal): triggers []. mold_authorization (transition scheduled->authorized): triggers []. mold_customer_payment: triggers []. mold_card_surcharge (credit card only): triggers []. None lands in another category.

## Capability contract cards (summary)
- book_mold_presample_d4275783 / book_mold_workplan_1501986a / book_mold_disposal_772b05b2 (agent, write): one charge line (code fixed per tool) on the named job, quantity 1 each, rate = amount, business_hours; balance_due += amount; receipt: line id, job id, code, date, amount, new balance. Format guards only.
- sign_mold_agreement_2b99f603 (user, write): job -> authorized, authorized_date = today; deposit > 0 posts one customer payment with a channel-generated confirmation number; credit card adds the 2.95 percent surcharge line.
- pay_mold_insured_share_5816092f (user, write): one customer payment on the named job; same tender/surcharge handling; rejects 0.00, matching the rule's "a share of 0.00 takes no payment".

## BLUEPRINT-KNOWN candidates / residue
1. Thin charter for customer writes: the only by:user step is signing on a scheduled job and containment is by:system, so pre-signing prerequisites are lines made billable while scheduled through scoped overwrites of the scope-line status gate.
2. The base adjustment reasons (billing_error, duplicate_line, goodwill) have no reason for program or declined-line write-downs; those amounts stay as balance until a human posts a credit (no write in either task depends on it).
3. Claims write-off rows carry no job reference, so on a claim file that links jobs of several categories the share prorates the file's carrier_denied_line and program_price_adjustment write-offs by the mold-covered total over the estimate; the exact per-job attribution is not in the records.
4. Other mold jobs of the same claim file cannot be read by compute (own category); the deposit and the share route that case to a human representative instead of pricing it.
5. W0 (task 0, still drying) carries no equipment-day or monitoring lines yet; the water charter books them per day without fixing when, and no task 0 read depends on them.

## REWORK round 2
- R1 CLOSED: every policy's assembly sentence rewritten once, generically, naming roles (replaced/added/credited figure; credit then raises; write-down, coverage limit, amount under other coverage), no factor quantity enumerated; compute_basis result/net_scope/visit_hours/covered_left/carrier_payable quote the new sentences.
- R2 CLOSED: presample, workplan and disposal rules state that a company_warranty job carries no such line (figure 0.00, nothing booked); compute returns 0 for warranty jobs; the deposit's "owed" lines are therefore not owed on warranty jobs (class swept: disposal included).
- R3 CLOSED (scope + referral, B7 route): share and deposit hand a job to a human when another mold job of the same claim file has received insurance proceeds; inside that scope the whole sublimit is this job's cover, consistent with mold_agg_shared_sublimit (no departure, overwrite stays []).
- R4 CLOSED: protocol_review removed; new method factor water_footprint_walk (stepped ceil vs proportional-with-floor vs base on the water job's affected area) passes A7/T1/T2/A1.
- R5 CLOSED: program write-down rebuilt as program_price_writedown labelled method (computed pct vs prorated recorded write-offs vs 0); coverage_allowance relabelled parameter with a constant-multiple pending tier.
- R6 CLOSED: write-downs are now taken off both the charge total and the mold-covered total before the cap, so an unbinding cap no longer double-counts; claim-file-wide write-offs are prorated by mold-covered/estimate when other-category jobs are linked (whole only when the mold job is the only job).
- R7 CLOSED: after-hours write-down removed; declined premiums now enter only as recorded carrier_denied_line write-offs (declined_line_writedown), consistent with claims_evt_writeoff for every declined line.
- R8 CLOSED: the two-grouping sentence is gone with the after-hours factor; swept all rules for "A ... less B, divided by" constructions (none left).
- R9 CLOSED: building_age_set tier 2 is now "growth in an attic or crawlspace" (no scope-restating age clause).
- R10 CLOSED: deposit lead tier 2 reads "when the job has no linked water job, or its linked water job carries no lead-safe setup line, and the building was built before the RRP year-built cutoff" (compute unchanged).
- R11 CLOSED: moisture, regulated-planning and collection schedules judge the water job on the mold job's opened date from its drying/opening/cancellation dates and line dates; cancelled or not-yet-drying water jobs fall explicitly to the stated tiers; overhead survey keys class_3 only (O8).
- R12 CLOSED: results-reuse tier now bills the results review fee (85.00 > largest credit 75.00), so the sampling line is always positive; other schedules only add.
- R13 CLOSED: share rule states "A share of 0.00 takes no payment, and the customer is told that nothing is owed now" (tool rejects 0.00 consistently).
- F0-1 CLOSED: J0 protocol_date moved to 2026-10-12 (after the 2026-10-05 loss); both protocol-age factors were replaced (water_footprint_walk; payment_route_raise), so no tier rests on that date.
- F0-2 CLOSED: CF0 now carries its initial approval row (6840.00), read by find_claims_approvals; class swept: CF1 carries approval, write-offs and deductible rows.
- F1-1 CLOSED with R8 (single reading; scored share recomputed by the gate).
- F1-2 CLOSED: W1 now carries its full 21-line ledger priced at Black Water Standard rates summing to its 3753.60 invoice; the wet-debris tier reads its monitoring lines (find_water_charges in gold); J1's seeded sampling (240.00), work-plan and deposit lines were recomputed against that ledger (scratch seedcheck; round-3 values 693.90 and 1528.90 after the footprint schedule was rebuilt).
- F1-3 CLOSED: CF1 carries the 1500.00 deductible assessment and payment rows (deductible_due 0.00), read by find_claims_deductibles to exclude the deductible from the share.
- F1-4 CLOSED: payment_amount tracing regenerated from the gate-equal figures (all computation text now generated from the DSL run, not typed by hand).
- O0-2 CLOSED: the closed 2025 Spot job moved to the customer's other property (single_family 1995): 150.00 deposit, no sampling or lead prepayment owed. O0-3/O1-2 CLOSED: multi-source claims in both rationales restated to the factors that read distinct records. O0-4 CLOSED: probe sentences now name the opening world. O3 CLOSED: share sentence reads "drywall or insulation". O1, O2, O4-O7, O9-O11: observations, no change (O9 covered by the R3 referral).

## Gate log
Round 1: 7/7 green (see audits for the RED items closed above).
Round 2: full suite run after all edits — EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (suite means branches 57.00, steps 15.00; history_rows_max 32; branches_max 66), GROUNDING OK, SCOPE OK.

## REWORK round 3
- N1 CLOSED: water_footprint_walk rebuilt as a monotone schedule: up to the mid threshold the base hours; above it the larger of the base hours and the area divided by a walk rate (100 sq ft per hour); above the large threshold the quotient of the large threshold divided by the walk rate plus step hours per full or partial 100 sq ft. 300 sq ft gives 3.00 h and 301 sq ft 3.50 h; checked at 150/151/200/250/300/301/400/401. Task 1's seeded 2026-09-10 work-plan line (310 sq ft) and its deposit were recomputed under it (seedcheck 693.9 / 1528.9).
- N2 CLOSED: both footprint sentences now name the grouping ("the quotient of ... divided by the walk rate", "the larger of two figures, the base visit hours and the quotient ..."); class sweep of every "larger of / lesser of / times ... divided / fraction" sentence: disposal roll-off sentence reworded ("the larger of two load counts, ... and the quotient ... rounded up"), share prorations reworded ("times the fraction of the mold-covered total over the claim file's estimate amount, the fraction never taken above 1"); no other two-grouping sentence remains.
- N3 CLOSED: roll-off minimum raised to 4 loads, so it binds on 401-640 sq ft of drywall-only removal (ceil(dw/160) = 3 or 4) and tier 2 differs from the standard method; class sweep for dead floors: presample rush minimum raised to 200.00 so it binds on the 425.00 tiers (40 percent = 170.00, O6 closed); deposit notice minimum (200.00 vs 20 percent of 150.00-1500.00) and the work-plan footprint floor (150-200 sq ft) are live; no other floor or tier is dead on its whole domain.
- F0-3 CLOSED with N1 (work-plan computation keeps one live method factor).
- F1-5 CLOSED with N3 (disposal keeps 4 factors with a live method factor).
- O0-5 CLOSED: customer profile_opened_date set to 2025-05-12 (the Spot job's opened date).
- O1-4 CLOSED: the share rule now states that the claim file's deductible is assessed and collected on the claim file, never on the job, and is not part of the insured's own share, which is the sentence the deductible read rests on.
- O12, O13, O14, O1-3, O0-1: observations, no change (O13/O1-3 are the stated proration rule; O14 shows no world difference).

## Gate log (round 3)
Full suite after all round-3 edits: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.

## Cross-product and own-category re-pricing pass (round 4; against published docs/water, docs/claims as of each row's posting date)
Task 0 (gold reads): water job 53c34fc8 and lines e914173a (service call, business-hours dispatch, arrival within 90 min), b6357bb5 (asbestos sampling, before the flood cut), 815d36df (lead-safe setup, pre-1978), f5e7aa14 (flood cut 64 lf at the Black Standard rate), c139dd37 (antimicrobial, base rate; the job already carries an antimicrobial line, so no tear-out antimicrobial line is owed) — all match. Owed but not yet booked on the still-drying job: its tear-out debris haul-off line (the water rules date it the flood cut date; it moves no mold read; left as recorded by the KB re-judge, E5 clean). Final HEPA vacuuming line not owed (no pad or carpet removal); drying deposit not owed (insurance-funded). Claim file 04479e28 (Public Adjuster Coordinated: estimate delivered two days after opening, within its 7 target days; credited-line write-off nothing to post — the water job carries no credit; category reassessment not engaged — category matches the tier; the regulated-scope supplement the claims rules owe for the water job's regulated lines is not yet prepared, a producible in-progress state that moves no read of the deposit) and approval 8d32f775 — match.
Task 1 (gold reads): water job 5814714c — RE-PRICED: added line 57ac188e (tear-out debris haul-off, dated the flood cut date, one load at the per-load fee with the category 3 sealed-bagging multiplier; no access multiplier since no flooring was removed; no haul-window multiplier since the flood cut was not on the opened date), final invoice and balance re-derived to the sum of its 22 lines. Unchanged and matching: cf14402b (service call with the after-hours surcharge, arrival within 90 min), 4e1ddc48, 0c1385ab, 1d0730c7, 76081f9c, 5de63e8d, 094b811f (antimicrobial, base rate; tear-out antimicrobial line not owed because an antimicrobial line is carried), d4553155, a73c0f67 (one monitoring visit, set day not billable), the twelve equipment-day lines f54bfc09, 88e77064, d5d8fa39, 2a30ca65, 1c376005, 892bef1e, 86dca6b8, d4b1a53e, 93f0035c, 280d7299, 5e2c9d07, e15cd547 (4 days within the 6-day cap, air scrubber required). Claim file 5ebf1e21 — RE-SEEDED: estimate submission date moved inside the Carrier Program's 3 target days of opening; everything else matches (reinspection threshold not reached; approval af8a4912; program write-off 0f995682; carrier_denied_line write-off 2228e2ce posted under the base rule — the credited-line policy was out of scope once the program write-off was posted, and the water job carries no credit; deductible rows c02d935f, c3fcac36).
Own-category history: task 0 closed Spot job 391cf774 (no protocol so no work plan; built 1995 so no sampling or lead prepayment; no removal so no haul-off; signing deposit d4af2bbf and final payment a5982c23; minimum_charge 3cd539b4 under the base minimum rule) — match. Task 1 job cd426fed: sampling c4a7785c, work-plan f457c059 and signing deposit 77e661f4 recomputed with the current extended rules on their own dates (scratch seedcheck) — match; every other line priced at the Standard tier rates — match.

## REWORK round 4
- M1 CLOSED: task-1 water job now carries the tear-out debris haul-off line the published water rules bill for its flood cut, priced under the water tear-out debris rules; its final invoice and balance re-derived; no mold read touches the line or the invoice, so no scored figure moves.
- M2 CLOSED: task-1 claim file estimate submission date re-seeded inside the Carrier Program target days of the file opening date; no factor reads the date, so no scored figure moves.
- S3 CLOSED (honest scope, rule == compute inside scope): the share rule now hands the request to a human representative when, on an arrangement that never bills declined lines, a water job or reconstruction contract linked to the claim file carries a billing error, duplicate line, goodwill or change order credit, because a carrier_denied_line write-off may then record value already credited; gold adds the two reads that rule it out (water job payments: none; reconstruction contracts on the file: none); not engaged in either task world, so no scored figure moves.
- S2 not routed (coordinator decision).
- Exhaustive re-pricing pass done (section above): re-priced rows are task-1 water job 5814714c (new line 57ac188e, invoice and balance) and claim file 5ebf1e21 (estimate submission date); every other gold-read row of both tasks, other-product and own-category, matches the published rules.
- Scored figures: none moved in either task.

## Gate log (round 4)
Full suite after all round-4 edits: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
ROUND 1: gates 7/7 green
REWORK round 2: gates 7/7 green
REWORK round 3: gates 7/7 green
REWORK round 4: gates 7/7 green
