# worklog — water_mitigation_billing (current: rework round 6)

History: round 1 delivered with gates 7/7 (line `ROUND 1: gates 7/7 green`); the round-1 text is superseded by this file
(archived outside the write domain). Every figure below is the round-4 world (task 0 unchanged since round 2).

## Difficulty pre-check
- Draws: task 0 prerequisite_problems=2 factor_counts=[6,4,6]; task 1 prerequisite_problems=1 factor_counts=[6,6].
- XF_recipe.md points A-F applied; water base triggers are all `[]` (D7).
- BLUEPRINT-KNOWN candidates: (1) the frozen water charter has no priced customer act besides the flat self-pay deposit
  (authorization and early release carry no numeric field) — routed around by the drying-estimate deposit (task 0, declared
  overwrite) and the insured's share (task 1, extended rule built from base facts); (2) water charge lines are rate x
  quantity, so several ladders are line-quantity schedules worded as the company's own.
- Coordinator ruling (round 2): each task carries a factor reading a claimed sibling category — task 0 past_due_mold_credit
  (mold), task 1 code_upgrade_supplement_decision (claims).

## Task 0 — self-pay drying deposit
Tree: root water_ext_drying_deposit (owner=user, 6 factors, on_request) <- water_ext_tearout_debris (agent, 6, state_due)
and <- water_ext_tearout_antimicrobial (agent, 4, state_due); both edges state form, value_input on `charges_posted`;
edge 1 affirmative ("fixed only after"), edge 2 negated ("not worked out until"). The prerequisites commute.
Gold: debris 5 loads x 367.22 = 1836.10; antimicrobial 5199.00 sq ft x 0.47 = 2443.53; deposit 14273.16 by debit_card.
Edge sensitivity: skip debris -> 12437.06; skip antimicrobial -> 11829.63. Cross read: the customer's invoiced Spot Mold
Remediation job (balance 378.50, due 2026-07-25, 51 days) -> 1.25.
Tiers taken: debris wet_flooring_load T1, class_cut_height T1, trim_disposal T1, carry_out_access T1, dispatch_haul_window
T2 (after_hours), sealed_bagging T2 (category_2); antimicrobial class_wetted_surfaces T1, carpet_lift_treatment T1,
stood_wet_coverage T1, regulated_wet_wipe T1; deposit iicrc_air_mover_plan T1, iicrc_dehumidifier_grade T2 (class_3),
standing_water_days T1, tearout_dust_scrubbers T2 (category_2), past_due_mold_credit T2 (1-60 days),
shared_structure_chamber T1.

## Task 1 — insured's share on a Direction to Pay job
Tree: root water_ext_insured_share (owner=user, 6 factors, on_request) <- water_ext_final_hepa_vacuum (agent, 6, state_due);
state form, value_input on `sh_hepa_sqft`, affirmative. Claim file approved 2026-10-02 for the submitted estimate
(13182.92 = covered scope: charges less the card surcharge, less every lead-safe and asbestos line, less the premium,
air-mover and LGR exclusions); code-upgrade supplement 1 (2026-10-03) names this water job and asks 770.00 (= lead-safe
345.00 + asbestos 425.00); the carrier approved 500.00 on 2026-10-05; receivable 13682.92; O&L limit 1000.00; deductible on
the file. Gold: HEPA 7448.00 sq ft x 0.31 = 2308.88; share 3504.43 by ach (code work 770.00 less the 500.00 approved =
270.00 non-covered; the work is funded once: 500.00 carrier + 270.00 insured). Edge sensitivity: skip HEPA -> 1449.75.
Task-0 tear-out lines pre-seeded at their rules' prices (debris 1530.10, antimicrobial 1500.24).
Tiers taken: HEPA cut_cavity_vacuum T2 (category_2), moved_contents_vacuum T1, regulated_dust_passes T1, lifted_carpet_back
T1, bottom_plate_strip T2 (class_2), silt_residue_pass T1; share code_upgrade_supplement_decision T1 (own-job request with an
approval), emergency_premium_timing T1, air_mover_placement_cap T2 (class_2), lgr_iicrc_sizing T2 (class_2),
hepa_stripped_floor_cover T1, contents_room_block T2.

## Capability contract cards (unchanged tools)
- book_tearout_debris_a8b773d4 / book_tearout_antimicrobial_173ee43e / book_final_hepa_eb899e1c (agent/write): one
  water_charges row each (debris_haul load / antimicrobial sqft / hepa_vacuum sqft), balance_due raised; format checks only.
- pay_drying_deposit_ee9a2909 / pay_insured_share_cc172b06 (user/write): one water_customer_payment, confirmation returned,
  balance_due lowered; format checks only. No tool tests a business precondition.

## A7 distinguishing inputs for the round-2 method factors
- carpet_lift_treatment: T1 F(affected_area)+SUM(detach) | T2 MX(F(affected_area), SUM(carpet_removal)) | F F(affected_area):
  T1/T2 sum vs max; T1/F adds the line aggregate; T2/F adds a max with the line aggregate.
- lifted_carpet_back: T1 SUM(pad)+F(affected_area) | T2 MX(F(affected_area), SUM(pad)) | F SUM(pad)+SUM(carpet_removal):
  T1/F adds the job field; T2/F max with the job field; T1/T2 sum vs max.
- code_upgrade_supplement_decision (decides the code work covered; the cap max(0, total - covered) is plain assembly):
  T1 MN(XSUM(claims_approvals.amount on the latest code-upgrade request naming this job), limit) | T2
  MN(XSUM(claims_requests.requested_amount of that request), limit) | F limit: T1/T2 read different claims tables (approved
  vs requested amounts); each vs F adds an input. T2 world: the own-job request pending (probe: share 1179.75 at the
  opening).
- lgr_iicrc_sizing: T1 (ceil(area/500)+ceil(run/50)) x lines | T2 ceil(area/500) x lines | F billed unit-days: T1 adds the
  baseboard-run input; vs F a different input (billed quantity).
- unchanged methods: trim_disposal, class_wetted_surfaces, iicrc_air_mover_plan, air_mover_placement_cap,
  hepa_stripped_floor_cover (audit PASS).
T1/T2 (A6): every factor's single-baseline substitution moves result (factor_sensitivity, COMPUTE OK); each ladder acts on
a quantity whose baseline is non-zero or adds a term, so it moves result in some producible world with the others at
baseline.



### water_ext_tearout_debris — factor-reads table (A1)
| factor | bindings read (transitively) -> owner |
|---|---|
| wet_flooring_load | (records/params only) |
| class_cut_height | (records/params only) |
| trim_disposal | (records/params only) |
| carry_out_access | (records/params only) |
| dispatch_haul_window | (records/params only) |
| sealed_bagging | (records/params only) |

### water_ext_tearout_debris — compute_basis owner table (A3)
| binding | owner | rule sentence (head) |
|---|---|---|
| prior_debris_lines | plain/baseline | A job's tear-out debris is hauled off once and billed as one debris ha… |
| flooring_sqft | plain/baseline | The removed flooring area is the total square feet on the job's pad re… |
| cut_lf | plain/baseline | The removed flooring area is the total square feet on the job's pad re… |
| trim_lf | trim_disposal | Trim disposal depends on the building and the water, measured on the b… |
| stand_days | wet_flooring_load | Flooring that stood wet is heavier per square foot: when the job's ope… |
| flooring_load_size | wet_flooring_load | Flooring that stood wet is heavier per square foot: when the job's ope… |
| cut_line_count_d | class_cut_height | The cut height follows the IICRC class of the intrusion: on a class_3 … |
| drywall_load_size | class_cut_height | The cut height follows the IICRC class of the intrusion: on a class_3 … |
| trim_load_term | trim_disposal | Trim disposal depends on the building and the water, measured on the b… |
| access_flooring_lines | carry_out_access | Carrying removed flooring out of a shared building sets an access mult… |
| access_multiplier | carry_out_access | Carrying removed flooring out of a shared building sets an access mult… |
| cut_date | dispatch_haul_window | When the job's latest flood cut line is dated the job's opened date, t… |
| window_multiplier | dispatch_haul_window | When the job's latest flood cut line is dated the job's opened date, t… |
| porous_lines | sealed_bagging | Contaminated debris is bagged and sealed before it leaves the property… |
| sanitation_multiplier | sealed_bagging | Contaminated debris is bagged and sealed before it leaves the property… |
| loads | plain/baseline | The loads are the removed flooring area divided by the flooring load s… |
| load_rate | plain/baseline | The per-load rate is multiplied by every rate multiplier that applies … |
| debris_tearout_lines | plain/baseline | A job's tear-out debris is hauled off once and billed as one debris ha… |
| result | plain/baseline | A job's tear-out debris is hauled off once and billed as one debris ha… |

trim_disposal (method) all-pairs: [the building was built before the tier's] vs [the building was built in or after that ]: distinct (the baseboard run divided by 150 linear feet per l / the baseboard run divided by 120 linear feet per l); [the building was built before the tier's] vs [otherwise]: distinct (the baseboard run divided by 150 linear feet per l / no trim debris (the baseboard is detached for rese); [the building was built in or after that ] vs [otherwise]: distinct (the baseboard run divided by 120 linear feet per l / no trim debris (the baseboard is detached for rese)

### water_ext_tearout_antimicrobial — factor-reads table (A1)
| factor | bindings read (transitively) -> owner |
|---|---|
| class_wetted_surfaces | (records/params only) |
| carpet_lift_treatment | (records/params only) |
| stood_wet_coverage | (records/params only) |
| regulated_wet_wipe | (records/params only) |

### water_ext_tearout_antimicrobial — compute_basis owner table (A3)
| binding | owner | rule sentence (head) |
|---|---|---|
| prior_anti_lines | plain/baseline | The surfaces a tear-out exposes are treated once and billed as one tea… |
| tearout_lines | plain/baseline | The surfaces a tear-out exposes are treated once and billed as one tea… |
| pad_sqft | carpet_lift_treatment | How the carpet came up sets the treated floor: when the job carries pa… |
| detach_sqft | carpet_lift_treatment | How the carpet came up sets the treated floor: when the job carries pa… |
| carpet_out_sqft | carpet_lift_treatment | How the carpet came up sets the treated floor: when the job carries pa… |
| treated_floor | carpet_lift_treatment | How the carpet came up sets the treated floor: when the job carries pa… |
| base_run_lf | class_wetted_surfaces | The surfaces wetted follow the IICRC class: on a class_3 job, where wa… |
| treated_wall_ceiling | class_wetted_surfaces | The surfaces wetted follow the IICRC class: on a class_3 job, where wa… |
| anti_stand_days | stood_wet_coverage | Material that stood wet longer takes a heavier application: when the j… |
| coverage_factor | stood_wet_coverage | Material that stood wet longer takes a heavier application: when the j… |
| lead_setup_lines | regulated_wet_wipe | Surfaces inside a regulated work area are wet-wiped rather than spraye… |
| sampling_lines | regulated_wet_wipe | Surfaces inside a regulated work area are wet-wiped rather than spraye… |
| handling_multiplier | regulated_wet_wipe | Surfaces inside a regulated work area are wet-wiped rather than spraye… |
| billed_sqft | plain/baseline | The billed square feet are the treated floor plus the treated wall and… |
| anti_unit_rate | plain/baseline | The billed square feet are the treated floor plus the treated wall and… |
| result | plain/baseline | The job must be in authorized, drying or drying_complete status when a… |

class_wetted_surfaces (method) all-pairs: [the job is class_3] vs [the job is class_2]: distinct (baseboard run times 8 feet of wall height, plus th / baseboard run times 2 feet of wicking height); [the job is class_3] vs [otherwise]: distinct (baseboard run times 8 feet of wall height, plus th / no wall or ceiling area); [the job is class_2] vs [otherwise]: distinct (baseboard run times 2 feet of wicking height / no wall or ceiling area)

carpet_lift_treatment (method) all-pairs: [the job carries pad removal lines and ca] vs [the job carries pad removal lines and ca]: distinct (the affected floor area plus the square feet on th / the larger of the affected floor area and the squa); [the job carries pad removal lines and ca] vs [otherwise]: distinct (the affected floor area plus the square feet on th / the affected floor area mapped on the job); [the job carries pad removal lines and ca] vs [otherwise]: distinct (the larger of the affected floor area and the squa / the affected floor area mapped on the job)

### water_ext_drying_deposit — factor-reads table (A1)
| factor | bindings read (transitively) -> owner |
|---|---|
| iicrc_air_mover_plan | area -> plain, floor_movers -> plain |
| iicrc_dehumidifier_grade | (records/params only) |
| standing_water_days | (records/params only) |
| tearout_dust_scrubbers | standard_scrubbers -> plain |
| past_due_mold_credit | (records/params only) |
| shared_structure_chamber | (records/params only) |

### water_ext_drying_deposit — compute_basis owner table (A3)
| binding | owner | rule sentence (head) |
|---|---|---|
| area | plain/baseline | The standard air mover count is one air mover for every 60 square feet… |
| dep_run_lf | iicrc_air_mover_plan | Air mover placement follows the IICRC class: on a class_3 job the air … |
| floor_movers | plain/baseline | The standard air mover count is one air mover for every 60 square feet… |
| air_movers | iicrc_air_mover_plan | Air mover placement follows the IICRC class: on a class_3 job the air … |
| dehumidifiers | plain/baseline | The dehumidifiers are one for every 500 square feet of the affected fl… |
| dehu_cut_lines | iicrc_dehumidifier_grade | Dehumidifier capacity follows the IICRC class and the open cavities: o… |
| dehu_rate | iicrc_dehumidifier_grade | Dehumidifier capacity follows the IICRC class and the open cavities: o… |
| dep_stand_days | standing_water_days | Water that stood before the crew arrived lengthens drying: when the jo… |
| drying_days | standing_water_days | Water that stood before the crew arrived lengthens drying: when the jo… |
| standard_scrubbers | plain/baseline | The standard air scrubber count is one where the tier requires an air … |
| cut_line_count | tearout_dust_scrubbers | Tear-out raises dust in the drying chamber: on a category_3 job carryi… |
| air_scrubbers | tearout_dust_scrubbers | Tear-out raises dust in the drying chamber: on a category_3 job carryi… |
| mold_balance_amt | past_due_mold_credit | A customer whose invoiced mold remediation job with the company is pas… |
| mold_due_date | past_due_mold_credit | A customer whose invoiced mold remediation job with the company is pas… |
| mold_days_late | past_due_mold_credit | A customer whose invoiced mold remediation job with the company is pas… |
| credit_multiplier | past_due_mold_credit | A customer whose invoiced mold remediation job with the company is pas… |
| spread_days | shared_structure_chamber | Water that stood in a shared building spreads into the neighbouring st… |
| structure_multiplier | shared_structure_chamber | Water that stood in a shared building spreads into the neighbouring st… |
| daily_cost | plain/baseline | The daily equipment cost is the air movers times the air mover daily r… |
| drying_estimate | plain/baseline | The daily equipment cost is the air movers times the air mover daily r… |
| drying_deposit | plain/baseline | The drying deposit is 60 percent of the drying estimate, rounded to th… |
| charges_posted | plain/baseline | The amount collected is the drying deposit plus every charge posted to… |
| payments_posted | plain/baseline | The amount collected is the drying deposit plus every charge posted to… |
| refunds_issued | plain/baseline | The amount collected is the drying deposit plus every charge posted to… |
| result | plain/baseline | The amount collected is the drying deposit plus every charge posted to… |

iicrc_air_mover_plan (method) all-pairs: [the job is class_3] vs [the job is class_2]: distinct (floor term (one per 60 sq ft) plus wall term (one  / floor term plus wall term, each rounded up on its ); [the job is class_3] vs [otherwise]: distinct (floor term (one per 60 sq ft) plus wall term (one  / one air mover per 60 sq ft of affected floor, roun); [the job is class_2] vs [otherwise]: distinct (floor term plus wall term, each rounded up on its  / one air mover per 60 sq ft of affected floor, roun)

### water_ext_final_hepa_vacuum — factor-reads table (A1)
| factor | bindings read (transitively) -> owner |
|---|---|
| cut_cavity_vacuum | (records/params only) |
| moved_contents_vacuum | (records/params only) |
| regulated_dust_passes | (records/params only) |
| lifted_carpet_back | hv_carpet_out_sqft -> plain, hv_pad_sqft -> plain, standard_floor -> plain |
| bottom_plate_strip | (records/params only) |
| silt_residue_pass | (records/params only) |

### water_ext_final_hepa_vacuum — compute_basis owner table (A3)
| binding | owner | rule sentence (head) |
|---|---|---|
| prior_hepa_lines | plain/baseline | Once drying is complete, the surfaces a tear-out exposed are HEPA vacu… |
| hepa_tearout_lines | plain/baseline | Once drying is complete, the surfaces a tear-out exposed are HEPA vacu… |
| hv_pad_sqft | plain/baseline | The vacuumed floor is the total square feet on the job's pad removal a… |
| hv_carpet_out_sqft | plain/baseline | The vacuumed floor is the total square feet on the job's pad removal a… |
| standard_floor | plain/baseline | The vacuumed floor is the total square feet on the job's pad removal a… |
| hv_detach_sqft | lifted_carpet_back | Where the carpet went sets the vacuumed floor: when the job carries ca… |
| vacuumed_floor | lifted_carpet_back | Where the carpet went sets the vacuumed floor: when the job carries ca… |
| hv_cut_lf | cut_cavity_vacuum | Cut wall cavities are vacuumed up to the cut: on a category_3 job carr… |
| vacuumed_wall | cut_cavity_vacuum | Cut wall cavities are vacuumed up to the cut: on a category_3 job carr… |
| hv_rooms | moved_contents_vacuum | Rooms whose contents were moved and blocked are vacuumed where the con… |
| vacuumed_contents | moved_contents_vacuum | Rooms whose contents were moved and blocked are vacuumed where the con… |
| hv_lead_lines | regulated_dust_passes | Regulated dust takes extra passes: the regulated pass factor is 2 when… |
| hv_sampling_lines | regulated_dust_passes | Regulated dust takes extra passes: the regulated pass factor is 2 when… |
| regulated_pass | regulated_dust_passes | Regulated dust takes extra passes: the regulated pass factor is 2 when… |
| hv_base_lf | bottom_plate_strip | The bottom plate behind removed baseboard is vacuumed as a strip: on a… |
| vacuumed_plate | bottom_plate_strip | The bottom plate behind removed baseboard is vacuumed as a strip: on a… |
| hv_stand_days | silt_residue_pass | Silt left by standing water takes a heavier pass: the residue pass fac… |
| residue_pass | silt_residue_pass | Silt left by standing water takes a heavier pass: the residue pass fac… |
| hepa_sqft | plain/baseline | The billed square feet are the vacuumed floor plus the vacuumed wall, … |
| result | plain/baseline | The billed square feet are the vacuumed floor plus the vacuumed wall, … |

lifted_carpet_back (method) all-pairs: [the job carries carpet detach-and-reset ] vs [the job carries carpet removal lines and]: distinct (pad removal square feet plus the affected floor ar / the larger of the affected floor area and the pad ); [the job carries carpet detach-and-reset ] vs [otherwise]: distinct (pad removal square feet plus the affected floor ar / pad removal plus carpet removal square feet); [the job carries carpet removal lines and] vs [otherwise]: distinct (the larger of the affected floor area and the pad  / pad removal plus carpet removal square feet)

### water_ext_insured_share — factor-reads table (A1)
| factor | bindings read (transitively) -> owner |
|---|---|
| code_upgrade_supplement_decision | ol_limit -> plain |
| emergency_premium_timing | (records/params only) |
| air_mover_placement_cap | am_unit_days -> plain |
| lgr_iicrc_sizing | lgr_unit_days -> plain |
| hepa_stripped_floor_cover | (records/params only) |
| contents_room_block | (records/params only) |

### water_ext_insured_share — compute_basis owner table (A3)
| binding | owner | rule sentence (head) |
|---|---|---|
| finance_charges | plain/baseline | The standard insured's share is the total of the job's card surcharge … |
| sh_billable | plain/baseline | Non-covered amounts are billed to the insured only on a claim file who… |
| regulated_lines | plain/baseline | Lead-safe setup and asbestos sampling are paid by the dwelling coverag… |
| regulated_total | plain/baseline | Lead-safe setup and asbestos sampling are paid by the dwelling coverag… |
| ol_limit | plain/baseline | The standard code work covered is the claim file's ordinance or law li… |
| cu_request_id | code_upgrade_supplement_decision | A code-upgrade supplement for the job decides its code work: when the … |
| cu_job | code_upgrade_supplement_decision | A code-upgrade supplement for the job decides its code work: when the … |
| cu_approved | code_upgrade_supplement_decision | A code-upgrade supplement for the job decides its code work: when the … |
| cu_approval_count | code_upgrade_supplement_decision | A code-upgrade supplement for the job decides its code work: when the … |
| cu_requested | code_upgrade_supplement_decision | A code-upgrade supplement for the job decides its code work: when the … |
| code_work_covered | code_upgrade_supplement_decision | A code-upgrade supplement for the job decides its code work: when the … |
| noncovered_code_work | plain/baseline | Lead-safe setup and asbestos sampling are paid by the dwelling coverag… |
| sc_premium | emergency_premium_timing | The emergency premium on the service call, being the job's service cal… |
| sh_stand_days | emergency_premium_timing | The emergency premium on the service call, being the job's service cal… |
| premium_share | emergency_premium_timing | The emergency premium on the service call, being the job's service cal… |
| am_unit_days | plain/baseline | Air movers are covered up to the IICRC placement count across the job'… |
| am_line_days | air_mover_placement_cap | Air movers are covered up to the IICRC placement count across the job'… |
| am_run_lf | air_mover_placement_cap | Air movers are covered up to the IICRC placement count across the job'… |
| covered_am_unit_days | air_mover_placement_cap | Air movers are covered up to the IICRC placement count across the job'… |
| lgr_unit_days | plain/baseline | LGR dehumidifiers are covered up to the IICRC sizing across the job's … |
| lgr_line_days | lgr_iicrc_sizing | LGR dehumidifiers are covered up to the IICRC sizing across the job's … |
| lgr_run_lf | lgr_iicrc_sizing | LGR dehumidifiers are covered up to the IICRC sizing across the job's … |
| covered_lgr_unit_days | lgr_iicrc_sizing | LGR dehumidifiers are covered up to the IICRC sizing across the job's … |
| sh_hepa_sqft | hepa_stripped_floor_cover | HEPA vacuuming is covered on the stripped floor: on a category_2 job c… |
| sh_pad_sqft | hepa_stripped_floor_cover | HEPA vacuuming is covered on the stripped floor: on a category_2 job c… |
| sh_cut_lf | hepa_stripped_floor_cover | HEPA vacuuming is covered on the stripped floor: on a category_2 job c… |
| hepa_outside_sqft | hepa_stripped_floor_cover | HEPA vacuuming is covered on the stripped floor: on a category_2 job c… |
| sh_rooms | plain/baseline | Moving contents within rooms is covered for one room for every block o… |
| room_lines | contents_room_block | Contaminated water spreads the contents that must be moved: on a categ… |
| room_block_sqft | contents_room_block | Contaminated water spreads the contents that must be moved: on a categ… |
| covered_rooms | plain/baseline | Moving contents within rooms is covered for one room for every block o… |
| noncovered_total | plain/baseline | The insured's share is the standard insured's share plus every non-cov… |
| result | plain/baseline | The insured's share is the standard insured's share plus every non-cov… |

code_upgrade_supplement_decision (method) all-pairs: [the latest code-upgrade supplement reque] vs [that request names this job and has no c]: distinct (the amount the carrier approved on that request, n / the amount the request asks for, no more than the ); [the latest code-upgrade supplement reque] vs [otherwise (no code-upgrade supplement re]: distinct (the amount the carrier approved on that request, n / the claim file's ordinance or law limit); [that request names this job and has no c] vs [otherwise (no code-upgrade supplement re]: distinct (the amount the request asks for, no more than the  / the claim file's ordinance or law limit)

air_mover_placement_cap (method) all-pairs: [the job is class_3] vs [the job is class_2]: distinct ((floor term + wall term + ceiling term, each round / (floor term + wall term, each rounded up) x the nu); [the job is class_3] vs [otherwise]: distinct ((floor term + wall term + ceiling term, each round / every billed air mover unit-day is covered); [the job is class_2] vs [otherwise]: distinct ((floor term + wall term, each rounded up) x the nu / every billed air mover unit-day is covered)

lgr_iicrc_sizing (method) all-pairs: [the job is class_3 or class_4 and carrie] vs [the job is class_2 and carries LGR dehum]: distinct ((floor term per 500 sq ft + wall term per 50 lf of / floor term per 500 sq ft, rounded up, x the number); [the job is class_3 or class_4 and carrie] vs [otherwise]: distinct ((floor term per 500 sq ft + wall term per 50 lf of / every billed LGR unit-day is covered); [the job is class_2 and carries LGR dehum] vs [otherwise]: distinct (floor term per 500 sq ft, rounded up, x the number / every billed LGR unit-day is covered)

hepa_stripped_floor_cover (method) all-pairs: [the job is category_2 and carries HEPA v] vs [the job is category_3 and carries HEPA v]: distinct (HEPA square feet above the pad removal square feet / HEPA square feet above pad removal square feet plu); [the job is category_2 and carries HEPA v] vs [otherwise]: distinct (HEPA square feet above the pad removal square feet / no HEPA square feet non-covered); [the job is category_3 and carries HEPA v] vs [otherwise]: distinct (HEPA square feet above pad removal square feet plu / no HEPA square feet non-covered)

## Decoy / absent-record / edge probes (scratch copies, re-run round 4)
| policy | probe | result |
|---|---|---|
| deposit | gold | 14273.16 |
| deposit | cancelled mold job listed first (decoy) | 14273.16 |
| deposit | closed prior mold job listed first | 14273.16 |
| deposit | no mold job (absent) | 12934.8 |
| deposit | mold balance 0 | 12934.8 |
| deposit | mold balance negative | 12934.8 |
| deposit | mold due date = today (0 days) | 12934.8 |
| deposit | mold 60 days late (boundary) | 14273.16 |
| deposit | mold 61 days late | 15611.52 |
| deposit | opened on loss date (0 days) | 11460.67 |
| deposit | affected area 0 | 9463.0 |
| debris | gold | 1836.1 |
| debris | baseboard only, pre-1978 (C-05a) | 0 |
| debris | second flood cut dated after the opened date | 1412.4 |
| debris | second flood cut same date (tie) | 1836.1 |
| antimicrobial | gold | 2443.53 |
| antimicrobial | carpet removed instead of reset | 2013.48 |
| antimicrobial | no lead-safe line (asbestos only) | 2079.6 |
| share | gold | 3504.43 |
| share | second (withdrawn Carrier Program) claim file listed first | 3504.43 |
| share | arrangement Assignment of Benefits Claim Billing | 17.7 |
| share | arrangement Carrier Program Claim Billing | 17.7 |
| share | arrangement Homeowner Direct Pay Claim Support | 3504.43 |
| share | arrangement Public Adjuster Coordinated Claim Billing | 3504.43 |
| share | O&L limit 500 | 3504.43 |
| share | opened 1 day after loss | 3458.44 |
| share | opened on loss date | 3427.78 |
| share | HEPA line skipped | 1449.75 |
| hepa | gold | 2308.88 |
| hepa | flood cut only, category_1/class_1 (C-05c) | 0 |

| probe (insured share, round 4) | result |
|---|---|
| gold world (after HEPA) | 3504.43 |
| opening world (no HEPA) | 1449.75 |
| own-job code-upgrade request pending (approval removed) | 1179.75 |
| no code-upgrade request | 1179.75 |
| limit 100, own-job request approved 500 | 1849.75 |
| limit 100, no request (auditor P6b) | 1849.75 |
| limit 0 | 1949.75 |
| limit 5000 (covers all) | 1449.75 |
| approved 250 on the own-job request | 1699.75 |
| older second code-upgrade request (residue: referral) | 1449.75 |
| later code-upgrade request on another claim file (decoy) | 1449.75 |
| later mold supplement request on the same file (other reason) | 1449.75 |
| second code-upgrade request on the same date (tie; residue) | 1449.75 |
| no regulated lines | 1179.75 |
| claim file absent (job points nowhere) | 17.7 |

Verbatim sweep (compute_basis, baseline sentences, replaced_by, policy_source) failures: []

### Code-upgrade supplement scope probes (round 4)
| scope probe (code work covered, non-covered code work) | result |
|---|---|
| own job, approved 500 of 770 (seed) | (500.0, 270.0) |
| own job, approved in full 770 | (770.0, 0) |
| own job, pending 770, limit 1000 | (770.0, 0) |
| own job, pending 770, limit 500 | (500.0, 270.0) |
| no request, limit 1000 | (1000.0, 0) |
| no request, limit 100 | (100.0, 670.0) |
| no request, limit 0 | (0, 770.0) |
| request names another job (rule: referral) | (1000.0, 0) |
| request names no job / file-wide (rule: referral) | (1000.0, 0) |
| second, later request naming another job (rule: referral) | (1000.0, 0) |
| later request on another claim file (decoy) | (500.0, 270.0) |
| later hidden-damage supplement on the same file | (500.0, 270.0) |

Residue rows (another job, no job, more than one request) are stated referrals in the rule; the compute keys on the latest request only.
Half-cent scan (every RND argument over gold, each single-factor baseline and the full baseline, all 5 computations): clear.

## REWORK round 2
- C-01 CLOSED: arrangement-keyed share ladders removed; a billability scope reads the claims arrangement's
  denied_line_billable_to_customer, so AOB / Carrier Program files carry only finance charges (probe: 17.70); premium now
  keyed on dispatch timing, rooms on a category block.
- C-02 CLOSED (round 2; its rebuild was replaced in round 3, see C-09).
- C-03 CLOSED: exposed_subfloor replaced by carpet_lift_treatment and lifted_carpet_back reshaped (sum with the job field vs
  max with the job field vs line aggregate); A7 table above. Class swept: no other method pairs on same-field filter swaps.
- C-04 CLOSED: LGR coverage is now the method factor lgr_iicrc_sizing whose fall-through is a branch of its own binding.
- C-05 CLOSED: (a) debris returns 0 when the job has no pad/carpet/flood cut line (probe 0); (b) share returns 0 when the
  balance is zero or less (probe 0); (c) final HEPA and the share's wait are scoped to jobs with pad or carpet removal
  lines, so the vacuumed floor is always above zero (flood-cut-only probe: no line owed). Swept deposit/antimicrobial: no
  zero-amount write possible inside scope.
- C-06 CLOSED: the share's prerequisite sentence now names a job whose drying is complete and whose final invoice has not
  yet been issued (= drying_complete status), matching condition and resolver gate.
- C-07 CLOSED: air mover and LGR coverage sentences state the aggregate across the job's lines, matching compute.
- C-08 CLOSED: the baseboard-run definition moved from the debris baseline into the trim_disposal sentence.
- F0-1 CLOSED (with C-03): antimicrobial has 4 passing factors (2 method, 2 parameter).
- F0-2 CLOSED (with C-08).
- F0-3 CLOSED: tier_taken / factor_trace now name the tier the world sits on (tier map per factor, listed above); rationale
  load count (3 loads) and scope text corrected.
- F1-1 CLOSED: the claim file is at estimate_submitted with no approval row (carrier receivable 0.00); the estimate is the
  company's covered scope, so no carrier record states coverage that competes with the non-covered rules; persona updated.
- F1-2 CLOSED (with C-03): HEPA has 1 passing method (lifted_carpet_back) and 5 parameters.
- F1-3 CLOSED (with C-02; superseded by the round-3 C-09 rebuild).
- F1-4 CLOSED: tier labels corrected (cut_cavity_vacuum T2, bottom_plate_strip T2).
- Coordinator cross-difficulty ruling CLOSED: task 0 reads a mold job (claimed) instead of fire; task 1 reads claims.
- O-06 (credit-card share surcharge has no tool) not engaged by either persona; unchanged.
- Proof text swept: design_rationale, prerequisite_closure, objectives/necessity, factor_trace/tier_taken, argument
  tracing and this worklog regenerated from the round-2 world.
REWORK round 2: gates 7/7 green

## REWORK round 3
- C-09 (a) CLOSED: verified (tier 2's fee x count equals the asbestos line amount, a filter difference). The factor is
  replaced (round 3; itself superseded in round 4 by code_upgrade_supplement_decision) by ordinance_law_commitments, which decides the O&L coverage remaining from claims records (approved amount of
  the latest code-upgrade request / requested amount of a pending one / the limit); the regulated-materials cap is one
  plain derived cap (A6). A7: T1 and T2 read different claims tables. Class sweep: no other tier uses a tariff x count to
  restate a recorded line amount.
- C-09 (b) CLOSED: the remaining coverage respects the limit's size and amounts already approved or requested against it
  on the file (probe: limit 100, no request -> 670.00 non-covered; limit 100 with 700 approved -> 770.00); a second
  code-upgrade request is a stated referral.
- F1-5 CLOSED (with C-09): task 1 world reseeded to exercise the new factor (claim approved for the covered scope, one
  approved 700.00 code-upgrade supplement, O&L limit 1000.00); gold, proof text, tracing, closure, necessity and this
  worklog regenerated; two claims reads added (approvals, requests).
- Task 0 untouched (its three policies, seed and JSON are byte-identical to round 2).
- O-10, O-11 (observations) unchanged.
REWORK round 3: gates 7/7 green

## REWORK round 4
- C-10 CLOSED: verified (the round-3 commitment subtraction ignored which job a code-upgrade supplement pays for). The factor
  is replaced by code_upgrade_supplement_decision: a code-upgrade request naming this job sets the code work covered
  (approved amount, or the pending amount, each no more than the limit); with no such request the limit applies; a request
  naming another job or no job, or more than one request, is a stated referral. Probed every scope: own job approved
  partly / fully, own job pending under and over the limit, no request at limits 0 / 100 / 1000, other job, file-wide,
  second request, another claim file, another supplement reason (scope table above). No scope funds the same work twice.
- F1-6 CLOSED: the seeded supplement now names this water job (770.00 asked, 500.00 approved), so carrier and insured fund
  the 770.00 once; design_rationale CLAIM FILE and near-miss text rewritten so they agree; gold, tracing, closure,
  necessity and this worklog regenerated.
- Class sweep: no other read subtracts or reserves an amount without checking what the record concerns (debris,
  antimicrobial, HEPA and deposit read only this job's lines or a status-filtered sibling holding).
- Task 0 untouched (policies, seed and JSON byte-identical to round 2).
REWORK round 4: gates 7/7 green

## REWORK round 5
Source: audits/render_source/water_mitigation_billing/render_r1.md (renderer scan); realism_bar.md applied (no factor changed
this round, so no R6 tags are added).
- Render blocker (XF C2/C3, retired units clause) CLOSED: verified that the three sibling replaced_by sentences (tear-out
  debris, tear-out antimicrobial, final HEPA) pointed back to the units of the retired base clause; each replaced_by, and
  the identical sentence in its rule, now restates the full units list itself. Class sweep: the deposit's two replaced_by
  sentences (flat deposit, tenders) already restate their in-force parts; no other extended sentence defers to a retired
  base clause.
- A9 (hepa_stripped_floor_cover grouping) CLOSED: the share rule and the ladder text now read "the square feet on those
  lines above the sum of the pad removal square feet and 4 square feet for each linear foot on the flood cut lines",
  matching compute. Class sweep of every "above / less / more than … plus" sentence: the antimicrobial class_3 wall-and-
  ceiling sentence (wall feet times height, plus floor area) and the deposit's collection sentence read only one way
  (dimensionally and as a plain sum) and are left as they are, because task 0 passed.
- B1 (date undefined on a carpet-removal-only job) CLOSED: the debris and antimicrobial lines are now dated the latest flood
  cut line, else the latest pad removal line, else the latest carpet removal line, covering every case in which the rules
  bill a line. Class sweep: the final HEPA line is dated the drying complete date, which every job in its scope carries; the
  two payments carry the posting date the tool stamps.
- Base defect logged (BLUEPRINT-KNOWN, frozen base, no change): parameter_schema.monitoring_visit_fee mentions "included
  visits" that no base rule defines; the only free visit is the set-day waiver in water_evt_monitoring. No extended policy
  reads that parameter.
- Text-only changes: no compute binding, seed row, gold write or proof figure moved, and both task JSONs are unchanged
  (no task text quotes the edited sentences). Re-run checks: decoy/edge probes, compute_basis verbatim sweep and half-cent
  scan are unchanged and clean.
REWORK round 5: gates 7/7 green

## REWORK round 6
Source: audits/policy_kb/water_mitigation_billing/ (KB re-judge, revision_2). Seed-only round: water.extended.yaml and
task_tools.py are byte-identical; only tasks/0.json seeds and the proof text they affect changed.
- SRC-1 CLOSED: verified with the published mold signing-deposit rules (tier deposit plus the short-notice raise for a
  remediation start one day after signing; no route, coverage, contamination or lead item applies); the task-0 mold
  signing-deposit payment is re-seeded at that amount (same row id, date and tender).
- SRC-2 CLOSED: verified with the published mold debris haul-off rules (drywall removal carries one bagged haul-off line,
  one load at the tier fee, dated the removal date, no trip charge, no linked water job); the line is added to the mold job
  (new row id), and the job's final invoice amount and balance are re-derived from all its lines, payments and both late
  fees (late fees stay at the minimum).
- Scored figures: none moved (the past-due mold factor reads a balance that stays above zero and an unchanged due date).
  Proof text swept and updated: design_rationale SEED line and REVISIONS, the mold read objectives, the deposit tracing
  (the mold balance it quotes), and the worklog task-0 summary.
- Exhaustive pass: every other-product row the gold reads (task 0 mold rows; task 1 claims rows) re-checked against the
  published docs; the KB re-judge's task-1 claims table matched in full, and the remaining mold rows matched. Own-category
  history: task 0 seeds no line the extended rules price (its door payment is an ordinary customer payment); task 1's
  seeded debris and antimicrobial lines are re-priced by the current extended rules at every build, and its other lines,
  payment and surcharge are base-priced. Row ids below.
### Re-priced rows (round 6 exhaustive pass)
Task 0, mold rows (published docs/mold, as of each row's posting date):
- mold_jobs.82c98c4f-32f0-4d82-8c03-381427c1445f (Spot Mold Remediation)
- mold_charges.0b362837-f873-4eaa-8864-c9cf15b2f6ec (hepa_vacuum)
- mold_charges.1a89c4a8-9348-4897-b2a5-0f977cf03bae (drywall_removal)
- mold_charges.272716c3-6fc9-40ab-918c-e97e4f52e406 (antimicrobial)
- mold_charges.520ae984-e90a-4712-a075-9846e9097f41 (ppe)
- mold_charges.48c83d2c-8143-48d3-8aec-dd97560731c0 (technician_labor)
- mold_charges.fa282e44-be9d-48d9-9228-cf27603d7fe6 (dehumidifier)
- mold_charges.9eff4d26-7b5d-4d95-92e9-b02c95eae6ad (dehumidifier)
- mold_charges.7ee290b9-c3dc-439c-9600-aa0c54dc6d3f (debris_disposal)
- mold_charges.1e511705-7bd7-4ed8-87df-6c46c34c809b (late_fee)
- mold_charges.e506dcd8-d415-4aae-81ec-e323dddef3f8 (late_fee)
- mold_payments.b63f1977-bf86-473f-bbd8-35be193f13e7 (mold_customer_payment)
- mold_clearance_tests.e865e871-cd8c-4242-adc7-b10a5e6b01a6 (mold_clearance_result)
Task 1, claims rows (published docs/claims):
- claims_files.9c0c47c6-bf5a-4d13-a2cc-5d14b6cbcaf1 (Direction to Pay Claim Billing)
- claims_approvals.a27b1a13-a461-4119-9967-6d7344047ad8 (initial)
- claims_approvals.7a0d887e-6de8-40fb-9ddd-287339793d0b (supplement)
- claims_requests.69c7761f-4378-44c6-853a-a8622e941489 (code_upgrade)
- claims_deductibles.11728de4-9261-43cc-9fe9-756830186e67 (claims_deductible_assessment)
Own-category (water) history rows checked against the extended rules:
- task 0 water_charges: dabc8a74-101a-46a0-8297-5b8a6929446a (service_call); faded407-56b4-4431-85e4-779d4d8e39ed (moisture_mapping); 91782b6c-4c28-46d9-85b7-3af3b1425f03 (asbestos_sampling); 0f24c875-f3fb-474a-a156-7668c99e952c (lead_safe_setup); 5e718401-d0a7-40c9-833f-f3a096da68bc (extraction); f2dbfb5f-1666-48f4-be3b-e67fc62abe16 (pad_removal); 5f1e6a9d-20b0-4eb6-9a34-4ffdc3f14757 (carpet_detach_reset); 3c47bd76-ad83-40ed-81eb-9c8f356a7651 (flood_cut); b1f1e8ec-81f3-4dfe-8538-57203f1501f5 (baseboard_removal); 7879e480-b464-4446-abba-e1a07ec850a0 (technician_labor); b43c49c9-dd13-4b68-98b0-22fb456d9305 (ppe)
- task 0 water_payments: 0550bae6-6b20-4690-9969-f81d00be40a3 (water_customer_payment)
- task 1 water_charges: 904ed1aa-6aca-4898-a810-85279498c063 (service_call); b9d4209a-74b0-439a-8af0-d876298e3362 (moisture_mapping); 8fdddb3c-b225-4798-b549-93d05fcdf083 (asbestos_sampling); 683f62ba-76de-4ff4-b326-ed38c3874caa (lead_safe_setup); 2fc91e83-cb68-49ef-a6e6-cdf6898e0078 (extraction); 69c7e02b-c490-407b-8fba-1b3d751eb781 (pad_removal); 26bef730-dcf4-4df1-8c99-0bf36e751d42 (carpet_detach_reset); 31e8f1cf-59a1-436c-97fb-ef0a467c88b7 (flood_cut); ebd65698-7a63-451b-9877-14da7eccc957 (baseboard_removal); b861318f-ab8f-465f-84bb-291ed8476eda (contents_manipulation); f328320b-5f67-4bfd-97b7-cfe0762c4929 (technician_labor); 22749669-5f64-4fd4-8e32-cf013ce59749 (ppe); dfb60ef1-0b29-453f-b1ef-d77ee3c0567c (air_mover); 3f9c9418-54ad-4ec0-8ecb-5b4b4c523a17 (lgr_dehumidifier); fc93ad7b-ef1a-453b-9345-57ad54ed854c (air_mover); 1622085a-ed36-4d8d-a2f6-b41a8edcbc7a (lgr_dehumidifier); 2cc9f18f-fd9c-47ba-9b7d-8a2d59a2b115 (air_mover); d7361461-7096-47d7-ad0c-97672ed4ceb8 (lgr_dehumidifier); 1c96599c-ebd7-4135-b1c9-53a1edea29f7 (air_mover); 2e388130-6cb4-4705-8b89-97234ddd7617 (lgr_dehumidifier); e80650a3-45c2-477e-b123-4f83d1ea0bcc (air_mover); d7e9574a-d3f7-442f-88ed-b6ea85d242cb (lgr_dehumidifier); a7399a35-602d-4d97-acdd-ebd82f3223fb (air_mover); 9505b88b-e6f8-4d68-b8f0-04dca13b520d (lgr_dehumidifier); f956636e-38af-43f9-9780-d6022444354f (monitoring_visit); bcd3ce62-a8ef-4afa-a612-11a4d970a37f (monitoring_visit); 0a21a076-8fd2-4cb2-a5da-fde1a3da8259 (monitoring_visit); 9bda90e2-205a-4fb5-8390-b4d4b743ed02 (monitoring_visit); df80a94e-ef60-4ac7-ab35-ac247ac2cf1d (monitoring_visit); 641a336a-5d66-4614-b927-e7064d64be70 (card_surcharge); cbe53561-d418-4d48-a797-9f3b155cc40f (debris_haul); 55304f9d-5bce-4a41-ac03-06a2e6daa2ab (antimicrobial)
- task 1 water_payments: 3e6df2f2-986e-4e9e-8242-34eee0207356 (water_customer_payment)
REWORK round 6: gates 7/7 green
