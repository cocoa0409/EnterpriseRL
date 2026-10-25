# worklog — good_faith_estimates_and_disputes (category estimate), M=2

## Step 0 — difficulty pre-check (round 1)
- Read XF_recipe.md (27 points), references (product_extended.yaml, task.json, task_tools.py), blueprint.yaml, products/estimate.yaml, db_schema.json, share_tools.py (verify threshold = 2 matches).
- Draw (draw_counts.py --tasks 2):
  - task 0: prerequisite_problems=2 (3 problems), factor_counts=[4,5,5]
  - task 1: prerequisite_problems=1 (2 problems), factor_counts=[4,5]
- DSL constraints found in check_compute.py: eq-only filters; within_months uses MONTHS(d, NOW) in [0,N); LATEST ties keep first row in file order; own-category X*/CFIELD reads are rejected by check_extended (cross reads must be OTHER categories); no subscripting (package_price_schedule dict unreadable -> price comes from the version's lines).
- Writable events (claimed by this difficulty, no cross-category triggers): estimate_requested, estimate_issued, estimate_line_recorded, estimate_revised, estimate_deposit_collected, estimate_deposit_refunded, estimate_cancellation_fee_retained, estimate_dispute_opened, estimate_cancelled. NOT writable: estimate_deposit_applied (triggers encounter payment), estimate_dispute_resolved (triggers encounter adjustment).
- Scope analysis (why these 5 policies):
  - issue / revise totals are by base the sum of the version's lines -> no customer-varying factors -> cannot be a problem; line amounts would force an issue/revise write -> excluded.
  - dispute logging writes only a customer-stated initiation date -> no computation -> excluded.
  - owner=user writes with a computation exist only as deposit collections (INITIAL_DEPOSIT / BALANCE_BEFORE_SERVICE); cancellation (user) computes nothing.
  - cancellation refund = held - fee has no customer-varying factors of its own -> excluded.
  - the late-change fee retained from deposits (base: "A Riverbend-initiated reschedule or cancellation never incurs the fee") is the one agent write with real factors, and on a still-live booking it feeds the pre-service balance.
  - => task 0 (surgery package): initial deposit (user) -> late patient-reschedule fee (agent) -> pre-service balance (user, root).
  - => task 1 (maternity package): enrollment deposit (user) -> pre-delivery balance (user, root).
- Rejected along the way (recorded so a reviewer sees why): cancellation trees (fee -> refund) — the refund has no factors of its own and a cancellation leaves no owner=user write with a computation; late-move fee measured on the estimate alone — a revision overwrites scheduled_service_date, so the original date is only recoverable from the patient-cancelled procedure slot in the visit records (appointments.cancel_notice_hours / appointment_date), which is what the fee reads.

## Design (round 1, frozen before authoring)
Policies (5) and trees:
- task 0 (surgery package, inguinal hernia 49505, uninsured): root estimate_ext_surgical_balance (user, 4 factors) <- estimate_ext_late_change_fee (agent, 5) <- estimate_ext_surgical_deposit (user, 5); also root <- deposit. All three edges value_input (deposits held). Order: deposit -> fee -> balance.
- task 1 (maternity package 59400, uninsured, approved 40% charity award): root estimate_ext_maternity_balance (user, 4) <- estimate_ext_maternity_deposit (user, 5) value_input.
Factor plan:
- surgical deposit (5): collections_security [method, cross encounter, multi: agency balance & final notice]; moved_booking_points [param, versions]; days_left_points [param, days to service]; missed_visit_points [param, visit fees assessed 12m]; implant_points [param, implant lines].
- late change fee (5): notice_share [param, cancelled slot notice hours]; fee_basis [method, package price band: pct / max(flat,pct) / flat]; acute_care_share [param, cross encounter, multi: ED day-before & no inpatient/obs day]; postponement_share [param, old slot date -> new date]; booking_lead_share [param, scheduling -> old slot].
- surgical balance (4): prepay_credit [method, pct of rest / flat / none by days left]; implant_share [param]; statement_reserve [param, cross encounter statements in 2 months]; rebooking_reserve [param, retained fee on booking].
- maternity deposit (5): enrollment_weeks_points [param]; aid_basis [method, cross assist, multi: approved & award covers EDD]; agency_points [param, cross encounter, multi]; missed_visit_points [param, visit]; late_payment_points [param, days since enrollment].
- maternity balance (4): aid_share [param, cross assist, multi]; prepay_credit [method]; agency_reserve [param, cross encounter]; missed_visit_reserve [param, visit].

## Step 1-3 progress (round 1)
- estimate.extended.yaml written (base verbatim + 5 extended policies); scratch sweep: every compute_basis quote, policy_source, replaced_by and baseline sentence is a verbatim substring of its rule; no snake_case token in any rule.
- task_tools.py: 5 tools, fresh uuid8 each (pay_surgery_package_deposit_c16ec91c [user], retain_late_change_fee_0cd5c1f6 [agent], pay_surgery_package_balance_24461a4e [user], pay_maternity_enrollment_deposit_610ee08c [user], pay_maternity_delivery_balance_fb9f749b [user]); no helper functions, every write tool calls ctx.create/update in its own body; no datetime/time/random/uuid imports; check_task_tools: TASK TOOL CONTRACT OK.
- Capability contract cards:
  - pay_*_deposit / pay_*_balance (owner=user, rw=write): object = one package estimate; atomic action = one deposit collection (event estimate_deposit_collected, stage INITIAL_DEPOSIT or BALANCE_BEFORE_SERVICE fixed per tool) + price_estimates.deposit_held_usd += amount; base triggers of estimate_deposit_collected: [] (stays in category); receipt "Payment accepted: deposit_txn_id, payment_reference (PMT-55xxxxx), deposit_stage, amount, deposit_held_usd".
  - retain_late_change_fee (owner=agent, rw=write): object = one surgery package estimate + the deposit collection drawn on; atomic action = one estimate_cancellation_fee_retained row (source_estimate_txn_id) + deposit_held_usd -= amount; base triggers: []; receipt "Fee retained: fee_txn_id, source_estimate_txn_id, amount, deposit_held_usd".
  - No tool validates any prerequisite or eligibility.
- Verification (scratch verify.py replays gold writes with the real tools):
  - task 0: deposit 4232.00 (baseline 2645.00; factor baselines security 3967.50 / moved 3967.50 / days 3703.00 / missed 3967.50 / implant 3967.50); fee 35.71 (baseline 150.00; fee_basis 33.75 / notice 47.61 / acute 71.42 / postponement 47.61 / lead 44.63); balance 1848.21 (baseline 1093.71; credit 1888.21 / implant 1418.21 / statement 1583.71 / rebooking 1748.21). Edge skips: skip deposit -> balance 6044.50, fee 0.00; skip fee -> balance 1712.50.
  - task 1: deposit 3546.00 (baseline 2462.50; aid 5910.00 / enrollment 3250.50 / agency 2659.50 / missed 3250.50 / late 2955.00); balance 4699.00 (baseline 6304.00; aid 8639.00 / credit 4774.00 / cesarean 3274.00 / agency 3714.00). Edge skip: skip deposit -> balance 8245.00.

## Task 0 — probes (scratch copies, handling-time worlds; dep / fee / bal)
Symptom found by probing: a Riverbend-cancelled slot or no cancelled slot still produced a 158.70 fee while the rule scopes them out -> root cause: the fee compute had no scope gate -> change: plain binding late_move_on_record (patient-cancelled procedure slot, estimate not cancelled, version > 1, notice hours < 24 x full-refund days) gates result to 0.00; scope sentence now states the hour conversion -> re-run: gold unchanged (35.71), both probes now 0.
```
gold world                                                                  dep=   4232.0 fee=  35.71 bal=  1848.21
decoy: an open agency account 212.40 (agency tier needs FN<=24m: 2026-02-03 yes) dep=   5290.0 fee=  35.71 bal=  1848.21
absent: no encounter accounts/txns                                          dep=   3967.5 fee=  71.42 bal=  1583.71
boundary: A1 final notice moved to 2025-10-20 (exactly 12 months back)      dep=   3967.5 fee=  35.71 bal=  1848.21
boundary: A1 final notice 2025-10-21 (11 months back)                       dep=   4232.0 fee=  35.71 bal=  1848.21
decoy: V3 fee waived row only (assessed removed)                            dep=   3967.5 fee=  35.71 bal=  1848.21
decoy: Riverbend-cancelled procedure slot instead of patient                dep=   4232.0 fee=      0 bal=  1848.21
absent: no cancelled slot (v1 removed)                                      dep=   4232.0 fee=      0 bal=  1848.21
decoy: ER charge two days before change (A2 service 10-02)                  dep=   4232.0 fee=  71.42 bal=  1848.21
tier: observation charge on change date                                     dep=   4232.0 fee=    0.0 bal=  1848.21
boundary: statement 2026-08-20 added (exactly two months)                   dep=   4232.0 fee=  35.71 bal=  1583.71
absent: no implant line (C1781 removed both versions)                       dep=   3967.5 fee=  35.71 bal=  1418.21
```
Reading: agency decoy (open 212.40 agency account) correctly lifts the security deposit to the whole package (capped 5290.00); 12-month final-notice boundary excludes the exact anniversary (2025-10-20) and includes 2025-10-21; a waived fee without its assessed row no longer counts; ER two days before the change falls to the full share; observation charge on the change date waives the fee; the two-month statement window excludes 2026-08-20; no implant line drops both implant factors. No None / zero-division / negative-date path raises: CFIELD None -> 0 or 9999 sentinels as the rule states; DAYS with a passed service date lands in the <=7-day tier (stated in the rule).

## Task 1 — probes (scratch copies, handling-time worlds; dep / bal)
```
gold world                                                         dep=   3546.0 bal=   4699.0
decoy: a denied second case (Full Charity tier) listed after       dep=   3546.0 bal=   4699.0
decoy: earlier expired 80% case                                    dep=   3546.0 bal=   4699.0
absent: no assistance case                                         dep=   5910.0 bal=   8639.0
boundary: award ends 2026-12-01 (= EDD, counted)                   dep=   3546.0 bal=   4699.0
boundary: award ends 2026-11-30 (day before EDD)                   dep=   5910.0 bal=   8639.0
tier: medical hardship case cap 3000.00                            dep=   1800.0 bal=   8639.0
tier: full charity                                                 dep=      0.0 bal=        0
decoy: second agency account 180.00 placed 2023 (listed after)     dep=   3546.0 bal=   4699.0
boundary: placement 2024-10-20 (exactly 24 months)                 dep=   2659.5 bal=   4699.0
absent: agency account paid (closed 0.00)                          dep=   2659.5 bal=   3714.0
decoy: older cesarean 2016 added                                   dep=   3546.0 bal=   4699.0
absent: no cesarean charge                                         dep=   3546.0 bal=   3274.0
decoy: waived row only (assessed removed)                          dep=   3250.5 bal=   4699.0
```
Reading: denied/expired second cases are excluded by the approved-status filter; no case or an award ending the day before the expected delivery date falls to the full delivery price (award end equal to the delivery date still covers it — both ends counted); hardship tier takes min(price, cap) on the deposit and the whole price on the balance, as both rules state; full charity gives 0.00 deposit and 0.00 balance (MX floor); placement exactly 24 months back is outside; a paid agency account removes both agency factors; an older 2016 cesarean is ignored (latest only); a waived fee without its assessed row does not count.
Revision from probing (all policies): single-record reads (agency account, procedure slot) now state their selection rule in the rule text ("the first one the ... record lists is the one read"); the approved case is stated as at most one at a time (assist max_concurrent_awards 1).
Revision (XF A3): assembly sentences reworded so none names a factor's quantity ("a figure they select takes the place of the fee basis" with the fee basis defined in the fee baseline; "an amount they select takes the place of the delivery package price"; "a fraction they select multiplies ...").
Revision: duplicate factor ids across policies renamed (maternity deposit missed_visit_points -> missed_appointment_points; maternity balance prepay_credit -> early_payment_credit); propagated to task 1 factor_trace/factor_sensitivity/rationale.

## Method factors — all-pairs tier tables (XF C14; distinguishing input in brackets)
- surgical deposit collections_security {A: whole package price | B: max(250.00, 5% x price) | C: none}: A-B max op + constant added; B-C input added; A-C input added. [price 5290.00 -> 5290.00 / 264.50 / 0]
- late-change fee fee_basis {A: 3% x price | B: max(tier fee, 4% x price) | C: tier fee}: A-B max op + tariff; B-C price input; A-C different input. [price 3000.00 -> 90.00 / 150.00 / 150.00; price 5290.00 -> 158.70 / 211.60 / 150.00]
- surgical balance prepay_credit {A: 2% x max(0, rest) | B: flat 40.00 | C: none}: A-B input vs constant; B-C constant vs nothing (C is the only zero tier). [rest 1093.71 -> 21.87 / 40.00 / 0]
- maternity deposit aid_basis {A: 0 | B: price x (100 - discount)/100 | C: min(price, cap) | D: price}: B-D tariff input; C-D min op + cap input; B-C different input/op; A-others nothing vs input (A is the only zero tier). [price 9850.00, discount 40, cap 3000.00 -> 0 / 5910.00 / 3000.00 / 9850.00]
- maternity balance early_payment_credit {A: 2% x price | B: flat 75.00 | C: none}. [price 9850.00 -> 197.00 / 75.00 / 0]

## Manual values gates (both tasks)
- Length/breadth: task 0 hops goal -> pre-service balance rule -> (a) initial deposit state, (b) retained late-change fee state -> fee rule -> initial deposit state; reads span estimate lines/deposits, encounter accounts+activity, appointments+fees. Task 1 hops goal -> pre-delivery balance rule -> enrollment deposit state; reads span estimate, assistance case+activity, encounter accounts+activity, appointments+fees. Every owner=user write is a card payment the patient makes on the spot.
- Need/simulator boundary: both personas state object (the package), timing (now, before the service), authorisation (they pay themselves; the agent may keep the fee after explaining), and raise no other ask; closing binds to the agent saying the payment went through.
- Chronology: every volunteered fact (package, service/due date, ER visit, assistance letter, agency bill, 2022 C-section) is in initial_state; the latter four only on the agent's question.
- Base eligibility/time: no time eligibility gate is realised by deposit or fee writes (dispute_window is for disputes); package-pricing and cancellation rules carry no structured eligibility (policy_scope).
- Authoritative facts/object: deposits held, versions, slot cancellation and notice, agency status, award status are all system records read before the writes; the fee draws on the deposit collection returned by the payment receipt.
- Reachability: one frozen_time per task; no wait for clearing, review or a future date; payments complete synchronously and return their confirmation.
- Prerequisite sentences: four sentences, three state-form affirmative/negated mix ("fixed only after", "not fixed until", "retained only once", "not fixed until"); each waits on a record-visible entry that exactly one write of this difficulty creates on that tier's estimate.
- Rule/compute equivalence: scratch sweep confirms every compute_basis quote is a verbatim substring of its rule; reverse sweep: every ladder tier, window convention, cap, floor and rounding sentence maps to a binding (late_move_on_record covers the fee scope sentence).
- Factors/baseline honesty: each baseline is the base charter's own figure (deposit percentage of the package price; rest of the package price; the tier's late-cancellation fee); every factor moves its result (factor_sensitivity) and the all-baseline result differs from gold.
- Draft recomputation from visible context: performed per task in design_rationale section 13 / 12; no second reading found.

## Final gate block (difficulty-wide, no --task)
- check_extended: EXTENDED OK
- check_task_tools: TASK TOOL CONTRACT OK
- replay_tasks: REPLAY OK (0.json 14 acts closure 52/52; 1.json 14 acts closure 36/36)
- check_solvability: SOLVABILITY OK
- check_compute: COMPUTE OK (suite means branches 49.50 / steps 14.00; history_rows_max 12; branches_max 58)
- check_grounding: GROUNDING OK
- check_cross_fire: SCOPE OK
- check_traceability not run (KB not yet rendered); check_cache_diff informational only.
- Coverage: task 0 {estimate_ext_surgical_deposit, estimate_ext_late_change_fee, estimate_ext_surgical_balance}, task 1 {estimate_ext_maternity_deposit, estimate_ext_maternity_balance}: disjoint, union = all 5 extended policies; tools disjoint, union = all 5 task tools.
INSTANTIATE round 1: gates 7/7 green

# REWORK round 2 (audit revision_1: task0=RED task1=RED, charter CG-1..CG-10, T0-F1..F3, T1-F1..F2)
Read in full: audits/policy_task/good_faith_estimates_and_disputes/{_difficulty.md,0.md,1.md}; XF_recipe re-applied.
Plan (classes closed, not instances):
- ECA / reserve class (CG-8, T0-F1, T1-F2 + the 501(r) observations on collections_security / agency_points): every factor that sizes a pre-service payment on prior unpaid bills or adds a hold above the billable package is removed (collections_security, agency_points, statement_reserve, rebooking_reserve, agency_reserve). Replaced by real levers: approved financial-assistance award applied to the self-pay package price (discount tiers, hardship cap less liability already booked), deposit share by days to service, pay-in-full credit, implants identified by published HCPCS codes, cesarean upgrade differential (billable).
- Charity-approved patients (coordinator line): every pre-service figure and the late-change fee of a patient holding a covering approved award is figured on the award-discounted package price / fee; a 100% award (or a used-up hardship cap) is carved out of the deposit, fee and balance rules by a record test.
- Zero-result class (CG-3): every write's amount is positive by rule: full-charity / used-up-cap bookings, moves made during a Riverbend inpatient or observation stay, and balances with nothing left to pay are carved out by record tests stated in the rules; the fee's lowest share product stays above zero.
- Rounding class (CG-4): every RND in every policy becomes RND(x + 0.000001, 2) on non-negative figures = half-up to the cent, matching every rule's "rounded half-up to the cent".
- Month-window class (CG-5): every factor that uses a whole-month window states its own convention.
- Framing-assertion class (CG-6, T0-F2): implants are read only by the HCPCS codes the rule lists (premium intraocular lenses V2787/V2788; other above-standard implants C1713/C1776); the task 0 world becomes a cataract package with a premium toric lens (V2787), a patient-elected upgrade outside the package.
- Calendar vs hours (CG-1): lateness of a move uses the base's calendar-day test (change date fewer than the full-refund days before the slot date); notice share by days.
- Scope gate (CG-2): the gate tests the later version carries a date different from the slot date and was furnished on or after the change date.
- Duplicate-tier class (CG-7): fee_basis tiers re-cut so every in-scope schedule price gets a distinct, monotone figure.
- Docstring class (CG-9, T0-F3): no docstring names another write's receipt or uses an ordering word.
- Consistency class (CG-10): the four award factors share one tier structure (discount / hardship cap less liability booked / full price) in their own words.
- Seed legality (T1-F1) and re-pricing: both worlds' awards are reached legitimately (an open encounter inside the 240-day period; charity booked on every covered encounter with the assist formula); every cross-category row re-priced.

## Round 2 — item by item (item -> what changed -> where)
- CG-1 -> the late-move test is the base's calendar-day test (change date fewer than the full-refund days before the slot date, counting back from the slot date); the hours test and the notice-hours read are gone; notice share now by notice days (4-6 / 1-3 / same day). -> estimate_ext_late_change_fee rule scope, notice_share, late_move_on_record.
- CG-2 -> the scope gate now tests: estimate not cancelled, version above 1, current scheduled service date different from the slot date, current version furnished on or after the change date, change date not after the slot date. -> late_move_on_record; probes "v2 still carries the slot date" and "v2 furnished before the change" give 0.
- CG-3 (class) -> zero-amount worlds carved out by record tests stated in each rule: 100% award or used-up hardship cap (all four payment rules and the fee), a move made during a Riverbend inpatient or observation stay (fee; the balance's prerequisite sentence excludes such moves in record terms), a balance figure of zero or less (both balance rules). The fee's smallest share product stays above zero (lowest shares 0.5 x 0.5 x 0.5 x 0.2). -> all five rules; P3 prerequisite sentence rewritten as a record test.
- CG-4 (class) -> every RND is RND(x + 0.000001, 2) on non-negative figures, i.e. half-up; every rule says "rounded half-up to the cent (an exact half cent goes up)". -> all five computes and rules.
- CG-5 (class) -> every whole-month window states its own convention (surgical and maternity missed-visit points, cesarean amount). -> estimate_ext_surgical_deposit, estimate_ext_maternity_deposit, estimate_ext_maternity_balance.
- CG-6 / T0-F2 -> implants are read only by listed codes (V2787/V2788 premium intraocular lenses; C1713/C1776 other above-standard implants); the deposit no longer reads implants; the task 0 world is a cataract package (66984) with a premium toric lens V2787 (a patient-elected upgrade, outside the package and outside the award). -> estimate_ext_surgical_balance implant_share; seed task 0.
- CG-7 -> fee_basis tiers: >= 5000.00 tier fee + 1% of price; 2500.00-4999.99 max(tier fee, 5% of price); below 2500.00 tier fee. Over the surgery schedule: 7450 -> 224.50, 5875 -> 208.75, 5290 -> 202.90, 3380 -> 169.00, 1640 -> 150.00 (distinct per tier, monotone).
- CG-8 / T0-F1 / T1-F2 (class: holds above the billable package, and payments sized on prior unpaid bills) -> removed statement_reserve, rebooking_reserve, agency_reserve, and also collections_security and agency_points (501(r) ECA observations). What remains above the package price stands behind billable items only: premium implants (package exclusion) and the cesarean upgrade differential.
- CG-9 / T0-F3 (class) -> all five docstrings: estimate_id "as listed by the estimate lookup for this patient"; source_estimate_txn_id "as listed in the booking's deposit activity"; no "before the call", no other write's receipt.
- CG-10 (class) -> all four award factors (surgical deposit, surgical balance, maternity deposit, maternity balance) share one tier structure: discount tiers -> price x (100 - discount)/100; hardship cap -> min(price, cap less the liabilities booked under that case, read from assist_encounter_applied); otherwise the price; the fee's award share mirrors it (discount -> 1 - discount; hardship with cap left -> 0.5).
- T1-F1 -> the 2024 agency account is removed; the award is reached legitimately: open ED account of 2026-06-18 (first statement 2026-06-28), application 2026-08-10 (day 43, inside the 240-day period), charity booked on it with the assist formula (AGB 871.23, liability 522.74, charity 862.16), liability paid 2026-09-10. Task 0's award likewise: application 2026-10-09 while its ED account had no statement yet, charity booked (AGB 649.79, liability 389.87, charity 643.03).
- Coordinator realism line "nothing that bills charity-approved patients on undiscounted prices" -> every pre-service figure and the late-change fee of a covered patient is figured on the award-discounted price; the credits are reductions only.
- Seeds re-priced: every encounter and assist row recomputed with the owning charter's formulas (uninsured discount by class, statement cycle, prompt-pay 15% on the 2022 inpatient account, AGB 34.6%, tier discount, award dates = application - 365 / determination + 6 months).

## Round 2 — probes (handling-time worlds; task 0 [deposit, fee, balance], task 1 [deposit, balance])
```
T0 gold                                                         [1825.2, 19.01, 1287.31]
T0 decoy: second case denied (Full Charity)                     [1825.2, 19.01, 1287.31]
T0 decoy: expired 80% case                                      [1825.2, 19.01, 1287.31]
T0 absent: no assistance case                                   [3042.0, 31.69, 2639.31]
T0 boundary: award ends 2026-11-04 (day before surgery)         [3042.0, 31.69, 2639.31]
T0 tier: hardship cap 1000, 389.87 used                         [549.12, 15.84, 0]
T0 carve: hardship cap 389.87 fully used                        [0, 0, 0]
T0 carve: full charity award                                    [0, 0, 0]
T0 carve: observation charge on change date                     [1825.2, 0, 1287.31]
T0 decoy: ER charge 9 days before change                        [1825.2, 38.03, 1287.31]
T0 tier: ER charge 5 days before change                         [1825.2, 28.52, 1287.31]
T0 decoy: Riverbend-cancelled slot                              [1825.2, 0, 1287.31]
T0 absent: no cancelled slot                                    [1825.2, 0, 1287.31]
T0 boundary: change 7 days before slot (2026-10-01) = full refund [1825.2, 0, 1287.31]
T0 boundary: change 6 days before slot                          [1825.2, 38.03, 1287.31]
T0 CG-2: v2 still carries the slot date                         [2028.0, 0, 1321.11]
T0 CG-2: v2 furnished before the change                         [1825.2, 0, 1287.31]
T0 decoy: waived row only (2026-05-19 assessed removed)         [1723.8, 19.01, 1287.31]
T0 absent: no premium lens (V2787 lines removed)                [1825.2, 19.01, 137.31]
T0 tier: other implant C1713 instead of V2787                   [1825.2, 19.01, 712.31]
T1 gold                                                         [4137.0, 2951.75]
T1 decoy: denied second case                                    [4137.0, 2951.75]
T1 absent: no assistance case                                   [6895.0, 6891.75]
T1 boundary: award ends on the EDD (counted)                    [4137.0, 2951.75]
T1 tier: hardship cap 3000, 522.74 used                         [1734.08, 0]
T1 carve: full charity                                          [0, 0]
T1 decoy: older cesarean 2016 added                             [4137.0, 2951.75]
T1 absent: no cesarean charge                                   [4137.0, 1526.75]
T1 boundary: cesarean 2021-10-20 (exactly 60 months)            [4137.0, 1526.75]
T1 decoy: waived row only                                       [3841.5, 2951.75]
```
Symptom found while probing -> root cause -> change: an absent cancelled slot crashed the emergency-gap reading (DAYS on a None change date) -> the guard only tested the emergency date -> er_gap_days now guards both dates; re-run as above.
Reading: denied/expired second cases never move a figure; no case or an award ending the day before the service falls to the full price; hardship tiers use the cap less the liability booked; full charity and a used-up cap carve every figure to out-of-scope 0; a stay charge on the change date carves the fee; an ER charge 2-7 days back gives 0.75, 9 days back 1.00; Riverbend-cancelled or absent slots, a change 7 days out, a version still on the slot date or furnished before the change all give no fee; the waived-only fee row is not counted; the 60-month cesarean boundary is outside.

## Round 2 — method factors, all-pairs (distinguishing input)
- aid factors (4 policies) {price x (100-d)/100 | min(price, cap - used) | price}: tariff input vs min op + cap inputs vs identity. [price 3380.00, d 40, cap 1000.00, used 389.87 -> 2028.00 / 610.13 / 3380.00]
- fee_basis {tier fee + 1% x price | max(tier fee, 5% x price) | tier fee}: addition vs max vs constant. [price 3380.00 -> 183.80 / 169.00 / 150.00]
All other factors are parameters.

## Round 2 — final gate block
- check_extended: EXTENDED OK; check_task_tools: TASK TOOL CONTRACT OK; replay_tasks: REPLAY OK (0.json 16 acts closure 39/39; 1.json 14 acts closure 39/39); check_solvability: SOLVABILITY OK; check_compute: COMPUTE OK (suite means branches 61.00 / steps 15.00; history_rows_max 11; branches_max 76); check_grounding: GROUNDING OK; check_cross_fire: SCOPE OK.
- Gold now: task 0 deposit 1825.20 / fee 19.01 / balance 1287.31; task 1 deposit 4137.00 / balance 2951.75.
REWORK round 2: gates 7/7 green

# REWORK round 3 (audit revision_2: R2-1, R2-2, R2-3; all round-1 items confirmed closed)
- R2-1 (class, six members: P1/P2/P3/P4/P5 carve-outs + P3 implant assembly) -> in every policy the award records are plain shared bindings stated once in the rule by a new definition sentence ("For <the quantity>, the patient's award is the patient's approved financial assistance case, a patient holding at most one approved case at a time; the award covers the <date> when that date falls within its award period, which runs from its award start date through its award end date, both counted; the award's cap left is its hardship liability cap less the liabilities already booked on encounters under that case."): aid_case, aid_tier, aid_cap, aid_cap_used, aid_cap_left, aid_start, aid_end, aid_covers. The award-period convention left every factor sentence. Each award factor keeps only its own tier-discount read (aid_discount) and its ladder ("when the covering award's tier discount is ...; when the covering award carries no tier discount and has cap left ..."). The carve-out now tests the award's tier name (Presumptive / Full Charity) and cap left, never a factor binding. P3: the implant total is a plain binding defined once ("For the pre-service balance, the implant total is ..."); implant_share owns only the line-presence counts (premium lens lines / other implant lines). Scratch sweep: no plain binding reads a factor's non-deciding binding and no factor reads another factor's binding.
- R2-2 -> one fee per booking, stated in both places by the same record test: the fee rule's carve-out adds "a booking carries at most one late-change fee, so once a retained late-change fee entry stands on the booking no further fee is kept" (compute: fee_entries_before == 0 in the scope gate); the fee still reads the first patient-cancelled slot the appointment record lists; the balance's prerequisite sentence is now "The pre-service balance is not fixed until the booking shows a retained late-change fee entry whenever its procedure slot, the first patient-cancelled Outpatient Procedure Appointment the appointment record lists, was cancelled while the booking continued at a new date, fewer calendar days before the slot date than the tier's full-refund days and outside a Riverbend inpatient or observation stay; a booking carries at most one such entry." and the edge condition names the same first-listed slot and "one estimate_cancellation_fee_retained row ... (at most one per booking)". Propagated to tasks/0.json prerequisite_closure.
- R2-3 -> acute_care_share re-cut as a single-source ladder on the latest emergency room charge date (on the change date or the day before: half; two to seven days before: three quarters; otherwise all); the constant "no room or observation charge" part is gone from the ladder and stays only in the scope carve-out. Task 0 keeps its multi-source floor through the award factors (award coverage AND tier discount / cap left).
- Combination sentences unchanged (order kept). Gold unchanged: task 0 1825.20 / 19.01 / 1287.31; task 1 4137.00 / 2951.75; every factor_sensitivity figure unchanged (check_compute recomputes them). Proof text swept: tasks/0.json factor_trace, factor_sensitivity tier_taken, step-13 tracing, rationale sections 4/7 and new section 15; tasks/1.json tier_taken and new section 13.
- Probes on the touched reads (scratch copies of the task worlds, gold writes replayed):
```
T0 gold                                                       [1825.2, 19.01, 1287.31]
T0 decoy: denied second case at Full Charity tier             [1825.2, 19.01, 1287.31]
T0 absent: no assistance case                                 [3042.0, 31.69, 2639.31]
T0 carve: award at Presumptive tier                           [0, 0, 0]
T0 tier: hardship cap 3000 (liability booked read)            [2349.12, 15.84, 1869.44]
T0 carve: hardship cap equal to liability booked              [0, 0, 0]
T0 decoy: 2500.00 liability booked under an expired case      [2349.12, 15.84, 1869.44]
T1 gold                                                       [4137.0, 2951.75]
T1 decoy: denied second case at Full Charity tier             [4137.0, 2951.75]
T1 absent: no assistance case                                 [6895.0, 6891.75]
T1 carve: award at Presumptive tier                           [0, 0]
T1 tier: hardship cap 3000 (liability booked read)            [1734.08, 0]
T1 carve: hardship cap equal to liability booked              [0, 0]
T1 decoy: 2500.00 liability booked under an expired case      [1734.08, 0]
T0 fee: second late move (fee already retained on booking)    [1825.2, 0, 1307.31]
T0 acute: ER charge 5 days before change                      [1825.2, 28.52, 1287.31]
T0 acute: no ER charge                                        [1825.2, 38.03, 1287.31]
T0 implant: C1713 instead of V2787                            [1825.2, 19.01, 712.31]
T0 implant: none                                              [1825.2, 19.01, 137.31]
```
Reading: a denied case at a 100% tier never moves a figure; no case falls to full prices; an award at the Presumptive tier, or a hardship cap equal to the liability already booked, carves every figure out (0 = outside the rules); a 2500.00 liability booked under another (expired) case is ignored by the cap-left read (same figures as without it); a second late move on a booking that already carries a fee gives no fee (outside), and the balance then counts that one entry; ER 2-7 days back gives 0.75, no ER charge 1.00; implant presence counts switch the share (premium -> whole, other -> half, none -> nothing).
- Final gate block: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
REWORK round 3: gates 7/7 green

# REWORK round 4 (audit revision_3: task1=PASS, task0=RED on R3-1)
- R3-1 -> the late patient move is one record-test sentence carried verbatim in both the fee rule and the balance rule: "A late patient move of a surgery booking is a cancellation of its procedure slot, the first patient-cancelled Outpatient Procedure Appointment the appointment record lists, made on or before the slot date and fewer calendar days before it than the tier's full-refund days, while the estimate is not cancelled and its current version, a later version furnished on or after the cancellation date, carries a scheduled service date different from the slot date, with no Riverbend inpatient room charge (revenue code 0120) or observation charge (revenue code 0762) dated on the cancellation date." The fee rule's scope sentence (and its overwrite replaced_by) now refers to that term ("a late patient move being defined in the next sentence"); the fee compute's scope gate is unchanged and is exactly that test plus the fee rule's own award and one-fee carve-outs. The balance's prerequisite sentence is now "The pre-service balance is not fixed until the booking shows a retained late-change fee entry for its late patient move, where it has one; a booking carries at most one such entry." and the edge condition names the same test; the balance compute evaluates the same test (late_patient_move; visit and encounter added to its cross_category) and returns no amount (0.00) while a late patient move lacks its entry (fee_wait_open).
- Class sweep (a wait whose depended-on rule can legitimately write nothing): fee <- initial deposit, balance <- initial deposit and pre-delivery balance <- enrollment deposit — each depended-on rule writes nothing only under the award carve-out (100% tier or no cap left), and the waiting rule carries the same carve-out with the same words and the same date, so it is out of scope too; no change needed. Task 1's files are byte-identical (cmp against the pre-edit copy).
- Gold unchanged: task 0 1825.20 / 19.01 / 1287.31; task 1 4137.00 / 2951.75; factor_sensitivity unchanged. The skip-fee load-bearing figure in tasks/0.json moved from 1268.30 to "not fixed (0.00)"; order_uniqueness, edge condition/why_false, factor_trace and rationale (sections 4 and 16) swept.
- Probes (task 0 world; gold writes replayed, then with the fee write skipped):
```
gold                                                                   [1825.2, 19.01, 1287.31]
auditor world: v2 furnished 2026-10-03, slot cancelled 2026-10-04      [1825.2, 0, 1287.31]
skip the fee write (late move without its entry)                       [1825.2, 19.01, 0]
second move: a fee entry already on the booking                        [1825.2, 0, 1307.31]
Riverbend-cancelled slot                                               [1825.2, 0, 1287.31]
no cancelled slot                                                      [1825.2, 0, 1287.31]
change 7 days before slot (2026-10-01)                                 [1825.2, 0, 1287.31]
version still on the slot date                                         [2028.0, 0, 1321.11]
observation charge on the cancellation date                            [1825.2, 0, 1287.31]
estimate cancelled                                                     [1825.2, 0, 1287.31]
-- same worlds with the fee write skipped (the fee rule writes nothing there):
auditor world, no fee written                                          [1825.2, 0, 1268.3]
Riverbend-cancelled slot, no fee written                               [1825.2, 0, 1268.3]
observation charge on the cancellation date, no fee written            [1825.2, 0, 1268.3]
change 7 days before slot, no fee written                              [1825.2, 0, 1268.3]
```
Reading: in the auditor's world (version furnished 2026-10-03, slot cancelled 2026-10-04) there is no late patient move, the fee rule writes nothing and the balance is fixed (1268.30 with no fee written); the same holds for a Riverbend-cancelled slot, no slot, a 7-day notice, a version still on the slot date, a stay charge on the cancellation date and a cancelled estimate; only a real late move without its entry leaves the balance not fixed.
- Final gate block: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK; SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
REWORK round 4: gates 7/7 green

# REWORK round 5 (renderer scan render_r1, policy revision_4 PASS/CLEAN)
- render 1 (recipe A4; class "plain binding only one factor reads") -> estimate_ext_surgical_balance: implant_total moved into the implant_share factor's bindings, its defining sentence folded into the factor's own sentence ("Implant share of the pre-service balance: the implant total is the sum of the Riverbend facility lines of the current version coded V2787 or V2788 (premium intraocular lenses) or C1713 or C1776 (other above-standard implants), the above-standard implants the package excludes and bills at actual charges less the uninsured discount; when a premium intraocular lens line ..."); the standalone sentence is gone. The factor now decides implant_amount = implant_share x implant_total (baseline 0), and balance_figure adds implant_amount, so no plain binding reads a factor-internal binding (the R2-1 class stays closed). Charter-wide sweep (scratch): the only other plain bindings read by a single factor are package_price (surgical deposit) and delivery_price (maternity deposit); both are the baseline quantity itself (the award factor's baseline expression is that price and the computation document states it), so they stay in the baseline.
- render 2 (recipe 21; class "tool rounding claims") -> task_tools.py: a pure-Python class static helper _Cents.half_up (no imports; an exact half cent goes up) replaces round(float(amount), 2) in all five bodies; each write still calls ctx.create/ctx.update in its own body; docstrings, names and signatures byte-identical (diff shows only the helper and the five body lines). The deposits-held figure is a sum of cent amounts (round only drops float noise; its docstring claims 2 decimal places, not a rounding mode). erlbench validate's tool lint and rw-consistency checks return no errors. Check: half_up(10.125)=10.13, half_up(0.015)=0.02, gold amounts unchanged.
- render 3 (recipes 6/13; class "ladder edge without a sentence") -> moved_booking_points: "exactly two add five, and one, or none recorded, adds none"; sweep of every ladder found one more edge: maternity days-to-delivery share now says "thirty or fewer days to delivery, a passed expected delivery date included, set ..." (the compute already put a passed date in that tier). Every other ladder already states its empty, zero, negative or passed-date case.
- Gold unchanged: task 0 1825.20 / 19.01 / 1287.31; task 1 4137.00 / 2951.75; factor_sensitivity unchanged. tasks/0.json rationale section 17 added; tasks/1.json byte-identical (note: a full replay_tasks run rewrites both task files with data-identical row order, so 1.json was restored from the pre-round copy and the replay gate was run with --check; cmp confirms identity).
- Probes on the touched reads (task 0 world, gold writes replayed):
```
gold                                                             [1825.2, 19.01, 1287.31]
implant: V2787 on the current version only (v1 twin removed)     [1825.2, 19.01, 1287.31]
implant: decoy V2787 on version 1 only                           [1825.2, 19.01, 137.31]
implant: C1713 instead of V2787                                  [1825.2, 19.01, 712.31]
implant: none listed                                             [1825.2, 19.01, 137.31]
versions: none recorded (facility principal lines removed)       [459.0, 16.88, 0]
```
Reading: only current-version implant lines count (a version-1-only V2787 is ignored); C1713 alone gives half; none gives nothing; with no facility principal line recorded the booking-history points are 0 as now stated.
- Final gate block: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
REWORK round 5: gates 7/7 green

# REWORK round 6 (audit revision_5: R5-1, three members)
- R5-1 member 1 (late-change fee, postponement share) -> rule: "the postponement days run from the original slot date to the new scheduled service date, the slot date not counted and the new date counted, a new date earlier than the slot date counting as zero postponement days; fourteen or fewer ..."; compute: postponement_days = MX(0, DAYS(slot, new)) (an earlier date takes the fourteen-or-fewer tier, half).
- R5-1 member 2 (surgical balance, early-payment credit) -> "fewer than fourteen days, a passed service date included, take off nothing" (compute already 0).
- R5-1 member 3 (maternity balance, early-payment credit) -> "fewer than thirty-five days, a passed expected delivery date included, take off nothing" (compute already 0).
- Exhaustive pass found six more unstated edges, each now stated in the rule. In every case the compute already agreed, so no compute change was needed:
  - Both late-deposit / late-payment ladders: a scheduling date later than today's date counts as zero days.
  - Both missed-visit ladders: a fee dated after today's date does not count.
  - Maternity enrollment points: an expected delivery date on or before the scheduling date counts as zero lead days.
  - Acute-care share: an emergency room charge dated after the change date falls in "every other case".
  - Both pay-in-full credits: a deposit dated after today's date takes off nothing.
  - Cesarean-history amount: a charge dated after today's date counts as zero months back.
- Gold unchanged: task 0 1825.20 / 19.01 / 1287.31; task 1 4137.00 / 2951.75; factor_sensitivity unchanged. tasks/0.json and tasks/1.json are byte-identical to the pre-round copies (cmp); the replay gate was run with --check only.

## Exhaustive ladder edge table (every factor of the charter; edge -> covering sentence / reason it cannot occur)
| policy | factor (input) | zero / empty | negative / before anchor / passed date | boundaries |
|---|---|---|---|---|
| surgical deposit | aid_basis (award) | no case / award not covering -> "in every other case it is figured on the surgical package price"; 100% tier or no cap left -> carve-out sentence (outside the rule) | award period ends before the service date -> not covering (period sentence, both ends counted) | discount exactly 0 -> hardship tier only if cap left, else every other case; discount 100 -> carve-out |
| surgical deposit | lead_share_pct (days to surgery) | 0 days -> "seven or fewer" | passed service date -> "a passed service date included" (seven or fewer) | 7 -> 100; 8 and 20 -> 75; 21 -> tier percentage |
| surgical deposit | late_deposit_points (days since scheduling) | 0 -> "fewer than thirty" | scheduling date after today -> "counting as zero days" (new) | 29/30 and 59/60 split as stated |
| surgical deposit | moved_booking_points (versions) | none recorded -> "one, or none recorded, adds none" | n/a (a count) | 2 -> five; 3 or more -> ten |
| surgical deposit | missed_visit_points (fees in 12 months) | none -> "none adds no points" | fee dated after today -> "not counting" (new); exactly 12 months back -> outside (month convention stated) | 1 -> five; 2 or more -> ten |
| late-change fee | fee_basis (package price) | no lines (price 0) -> "below ,500.00 keeps the tier's late-cancellation fee" | n/a (non-negative sum) | 2,500.00 and 5,000.00 inclusive lower bounds stated |
| late-change fee | notice_share (notice days) | 0 -> "a change on the slot date itself keeps all" | change after the slot date -> not a late patient move (definition: "made on or before the slot date") | 1-3 -> three quarters; 4-6 -> half; 7 or more -> not a late move (definition) |
| late-change fee | acute_care_share (latest ER date) | no ER charge -> "no emergency room charge ... included, all of it is kept" | ER dated after the change date -> "one dated after the change date included" (new) | 0-1 -> half; 2-7 -> three quarters; 8 or more -> all |
| late-change fee | postponement_share (postponement days) | 0 -> "fourteen or fewer" | new date earlier than the slot date -> "counting as zero postponement days" (new) | 14/15 and 35/36 split as stated |
| late-change fee | aid_fee_share (award) | no case / not covering -> "in every other case all of it is kept"; 100% tier or no cap left -> carve-out | award ending before the new date -> not covering | as for aid_basis |
| surgical balance | aid_price (award) | as aid_basis -> "in every other case it is the surgical package price"; carve-out for 100% / no cap left | as aid_basis | as aid_basis |
| surgical balance | implant_share (implant lines) | none listed -> "nothing is added" | n/a (a count) | premium line present -> whole total, regardless of other lines; only other lines -> half |
| surgical balance | early_credit_pct (days to surgery) | 0 -> "fewer than fourteen" | passed service date -> "a passed service date included" (new) | 13/14 and 20/21 split as stated |
| surgical balance | full_credit_pct (days since initial deposit) | no initial deposit -> "with no initial deposit on record ... nothing"; 0 days -> "zero to seven" | deposit dated after today -> "or with one dated after today's date, takes off nothing" (new) | 7/8 and 30/31 split as stated |
| maternity deposit | enrollment_aid_basis (award) | as aid_basis (delivery package price) | as aid_basis | as aid_basis |
| maternity deposit | delivery_lead_share (days to delivery) | 0 -> "thirty or fewer" | passed delivery date -> "a passed expected delivery date included" | 30 -> 100; 31 and 60 -> 50; 61 -> tier percentage |
| maternity deposit | enrollment_points (enrollment lead days) | 0 -> "fewer than 112" | delivery date on or before scheduling -> "counting as zero lead days" (new) | 111/112 and 167/168 split as stated |
| maternity deposit | missed_appointment_points (fees in 12 months) | none -> "none adds no points" | fee dated after today -> "not counting" (new); 12 months back -> outside | 1 -> five; 2 or more -> ten |
| maternity deposit | late_payment_points (days since enrollment) | 0 -> "fewer than thirty" | scheduling after today -> "counting as zero days" (new) | 29/30 and 59/60 split as stated |
| maternity balance | delivery_aid_price (award) | as aid_basis; carve-out for 100% / no cap left | as aid_basis | as aid_basis |
| maternity balance | early_payment_credit (days to delivery) | 0 -> "fewer than thirty-five" | passed delivery date -> "a passed expected delivery date included" (new) | 34/35 and 59/60 split as stated |
| maternity balance | cesarean_amount (latest 59514 date) | no charge -> "none ... adds nothing" | charge dated after today -> "counting as zero months back" (new) | 17/18 and 59/60 whole months; month convention stated |
| maternity balance | pay_in_full_credit (days since enrollment deposit) | no deposit -> "with no enrollment deposit on record"; 0 days -> "zero to seven" | deposit dated after today -> "or with one dated after today's date, takes off nothing" (new) | 7/8 and 30/31 split as stated |
- Probes on the touched reads (task worlds, gold writes replayed):
```
T0 gold                                                               [1825.2, 19.01, 1287.31]
T0 postponement: move to an EARLIER date (2026-10-06 < slot 2026-10-08) [2028.0, 12.68, 1321.11]
T0 postponement: move to the slot date + 14 days (2026-10-22)         [2028.0, 12.68, 1321.11]
T0 early credit: surgery date already passed (2026-10-15)             [2028.0, 12.68, 1321.11]
T0 acute: ER charge dated after the change date (2026-10-05)          [1825.2, 38.03, 1287.31]
T1 gold                                                               [4137.0, 2951.75]
T1 early credit: delivery date already passed (2026-10-15)            [5910.0, 3050.25]
T1 cesarean charge dated after today (2026-10-25) -> zero months back [4137.0, 4376.75]
T1 missed fee dated after today (2026-10-25) not counted              [3841.5, 2951.75]
```
Reading: a move to an earlier date counts as zero postponement days and takes half (fee 12.68 in that world); a passed service or delivery date gives no early-payment credit; an ER charge dated after the change date gives the full share; a cesarean charge dated after today takes the full differential (zero months back); a fee dated after today does not count.
- Final gate block: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
REWORK round 6: gates 7/7 green

# REWORK round 7 (audit revision_6: R6-1, charge lines later credited)
Business reading chosen: a charge line credited in full is not a charge. "Credited in full" means the line carries charge-credit entries (encounter_charge_credited with source_txn_id = that line) totalling its whole amount. A partial credit, such as a units correction, leaves the line counted. Every read site picks one exact line and tests it:
- XLATEST of encounter_txn_id picks the line.
- When several lines share the date, the first one the account activity lists is read, and the rules say so.
- The test is XSUM(credits with source_txn_id = line) < XSUM(posted amount of that line).

- R6-1 member 1 (fee, acute-care share): new rule wording: "the latest emergency room charge is the emergency room charge line (revenue code 0450) on the patient's Riverbend hospital accounts with the latest service date, the first such line the account activity lists where several share that date, a line credited in full, that is one carrying a charge-credit entry for its whole amount, counting as no emergency room charge; ...". Compute: er_line, er_line_credited, and er_gap_days = -1 when the line is credited, which falls in the full-share tier.
- R6-1 members 2 and 3 (late-patient-move definition, carried in the fee rule and the surgical balance rule): the definition now ends "... dated on the cancellation date, reading for each of the two codes the first charge line the account activity lists for that date, a line credited in full, that is one carrying a charge-credit entry for its whole amount, not counting."
  - The sentence is identical in both rules (scratch check: sentences equal).
  - Compute: chg_/cnl_ room_line, room_open, obs_line and obs_open replace the plain XCOUNTs; stay = room_open + obs_open.
  - The fee rule's "medically documented change" sentence now reads those charges "as the definition of a late patient move reads it", so there is no second wording.
- R6-1 member 4 (maternity balance, cesarean history): "... is read by its service date, the first such line the account activity lists where several share the latest date, a line credited in full, that is one carrying a charge-credit entry for its whole amount, counting as no cesarean charge, ...". Compute: ces_line, ces_line_credited, and cesarean_months = 9999 when the line is credited, which gives the nothing tier.
- Sweep of every read of another category's charge, payment or fee rows (credited, reversed, refunded, waived):
  1. Fee: ER charge 0450, latest line. Fixed (member 1).
  2. Fee: room 0120 and observation 0762 charges on the change date, in the late-move definition and the medically documented sentence. Fixed (member 2).
  3. Surgical balance: the same charges on the cancellation date, in its copy of the definition. Fixed (member 3).
  4. Maternity balance: cesarean charge 59514, latest line. Fixed (member 4).
  5. Surgical and maternity deposits: visit_fee_assessed in the last twelve months.
     - A waived fee is stated to count ("a fee later waived still counting").
     - The visit charter has no fee reversal or refund event (only waived and paid), so no other sentence is needed.
  6. All five award reads: assist_encounter_applied fap_liability_usd ("liabilities already booked").
     - The reversal event (assist_adjustment_reversed) follows only a revocation.
     - A revoked case is no longer status approved, so it never stands under the award that is read.
     - An expired or withdrawn case is excluded by the approved-status filter.
  7. Fee and surgical balance: the patient-cancelled procedure slot (appointments). This is a status row, not a charge. The visit lifecycle has no un-cancel transition.
  8. Not read anywhere: encounter payments, refunds, adjustments and statements; claim rows; plan rows.
- Gold unchanged: task 0 1825.20 / 19.01 / 1287.31; task 1 4137.00 / 2951.75; factor_sensitivity unchanged. tasks/0.json and tasks/1.json are byte-identical to the pre-round copies (cmp). The replay gate was run with --check only. Tools are unchanged.
- Probes (gold writes replayed unless noted):
```
T0 gold                                                                     [1825.2, 19.01, 1287.31]
T0 ER line credited in full (SERVICE_NOT_RENDERED)                          [1825.2, 38.03, 1287.31]
T0 ER line credited in part (UNITS_CORRECTION 100.00)                       [1825.2, 19.01, 1287.31]
T0 room charge on the cancellation date (not credited): no late move        [1825.2, 0, 1287.31]
T0 room charge on the cancellation date, credited in full: late move stands [1825.2, 19.01, 1287.31]
T0 observation charge on the cancellation date, credited in full            [1825.2, 19.01, 1287.31]
T0 room charge credited in full, fee write skipped: balance waits (0)       [1825.2, 19.01, 0]
T1 gold                                                                     [4137.0, 2951.75]
T1 cesarean line credited in full (SERVICE_NOT_RENDERED)                    [4137.0, 1526.75]
T1 cesarean line credited in part (UNITS_CORRECTION 500.00)                 [4137.0, 2951.75]
```
Reading:
- An ER line credited in full gives the full share (fee 38.03). A partial credit keeps the half share.
- An uncredited room charge on the cancellation date means no late move, so no fee.
- A room or observation charge credited in full leaves the late move standing, so the fee is owed. With the fee write skipped, the balance waits (0).
- A cesarean line credited in full adds nothing (balance 1526.75). A partial credit keeps the half differential.
- Final gate block: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
REWORK round 7: gates 7/7 green

# REWORK round 8 (audit revision_7: R7-1 six sites, R7-2 four reads; coordinator DSL-limit route)
DSL limit, stated: a charge-credit row carries only the credited line's id, its account, the reason, the amount and the posting date. It has no revenue code, procedure code or service date (encounter charter event fields). So credits cannot be netted against charges by code and date with exact-value filters. The DSL also cannot pick "the latest line whose net is positive".
Route taken: each read is decided on net amounts at the hospital-account level, never on one picked line.
- A charge of the relevant kind counts only when the hospital account it is posted on carries charges net of the charge credits recorded on that account above zero.
- Compute: XSUM of the account's encounter_charge_posted amounts less XSUM of its encounter_charge_credited amounts, both filtered exactly by encounter_id. This is the charter's own net (gross_charges_total).
- No single-entry test remains (R7-1 gone).
- Which twin line carries a credit no longer matters, because the visit is the account (R7-2 duplicates gone).
- Residue, stated plainly in the rule: where the account read nets to zero, an earlier charge of that kind is not looked for.

- R7-1/R7-2, fee acute-care share: "... the first such line the account activity lists where several share that date, and it counts only when the hospital account it is posted on carries charges net of the charge credits recorded on that account above zero, otherwise counting as no emergency room charge, an earlier emergency room charge not being looked for; ...". Compute: er_acct (XLATEST encounter_id of 0450 lines), er_acct_net, and er_gap_days = -1 unless er_acct_net > 0.
- R7-1/R7-2, late-move definition (fee rule and surgical balance rule; identical sentence, scratch check true): "... dated on the cancellation date, such a charge counting only when the hospital account it is posted on, for each of the two codes the account of the first such line the account activity lists for that date, carries charges net of the charge credits recorded on that account above zero, so that a credited line on an account that still carries net charges still counts." Compute: chg_/cnl_ room_acct, room_open, obs_acct and obs_open, each open = account net > 0.
- R7-1/R7-2, maternity cesarean history: "... the first such line the account activity lists where several share the latest date, and it counts only when the hospital account it is posted on carries charges net of the charge credits recorded on that account above zero, otherwise counting as no cesarean charge, an earlier cesarean charge not being looked for, ...". Compute: ces_acct, ces_acct_net, and cesarean_months = 9999 unless ces_acct_net > 0.
- Every "credited in full" phrase is gone from the charter (scratch check). Gold unchanged: task 0 1825.20 / 19.01 / 1287.31; task 1 4137.00 / 2951.75; factor_sensitivity unchanged. tasks/0.json and tasks/1.json are byte-identical to the pre-round copies (cmp). Tools are unchanged; replay was run with --check only.
- Probe matrix (every read: twin with credit on either copy, voided later record over a real earlier one, partial credits in two entries, no lines; gold writes replayed unless noted):
```
T0 gold                                                                           [1825.2, 19.01, 1287.31]
T0 ER: duplicate twin line, credit on the original                                [1825.2, 19.01, 1287.31]
T0 ER: duplicate twin line, credit on the copy                                    [1825.2, 19.01, 1287.31]
T0 ER: two partial credits (100 + 1320) on the line, account still net>0          [1825.2, 19.01, 1287.31]
T0 ER: voided later ER account (10-04) over the real 10-03 visit                  [1825.2, 38.03, 1287.31]
T0 ER: every line of the ER account credited (visit voided)                       [1825.2, 38.03, 1287.31]
T0 ER: no ER lines                                                                [1825.2, 38.03, 1287.31]
T0 stay: room line on the cancellation date (real stay): no late move             [1825.2, 0, 1287.31]
T0 stay: room line with twin, credit on either copy                               [1825.2, 0, 1287.31]
T0 stay: observation line, two partial credits summing to it, account voided      [1825.2, 19.01, 1287.31]
T0 stay: observation account voided, fee skipped -> balance waits (0)             [1825.2, 19.01, 0]
T1 gold                                                                           [4137.0, 2951.75]
T1 cesarean: twin line, credit on the original                                    [4137.0, 2951.75]
T1 cesarean: twin line, credit on the copy                                        [4137.0, 2951.75]
T1 cesarean: two partial credits on the line (account still net>0)                [4137.0, 2951.75]
T1 cesarean: voided later account (2024) over the real 2022 cesarean              [4137.0, 1526.75]
T1 cesarean: no cesarean line                                                     [4137.0, 1526.75]
```
Reading:
- Twins give the same result whichever copy is credited.
- Two partial credits on one line leave the visit counted while its account still nets above zero.
- A voided later account hides the earlier real one (the stated residue: "an earlier ... not being looked for").
- A voided stay account leaves the late move standing, so the fee is owed and the balance waits until it is written.
- No lines gives the empty tier.
- Final gate block: EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (--check); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
REWORK round 8: gates 7/7 green

## Rework round 9 (src-1)
- src-1: each of the five write tool bodies now enforces only its declared format/reference contract before any write, returning an `Error:` string and leaving the DB unchanged when:
  - `amount` is empty, or not positive after half-up rounding to the cent (e.g. -5, 0, 0.004);
  - `estimate_id` names no estimate;
  - for `retain_late_change_fee_0cd5c1f6`: `source_estimate_txn_id` is not an `estimate_deposit_collected` row of that same estimate (e.g. "x", or a retained-fee row).
- These are format/reference checks only, with no eligibility or prerequisite logic. Tool names, args, annotations, decorators and docstrings are AST-identical to the pre-round copy.
- The charter, tasks/0.json and tasks/1.json are byte-identical (sha256). Gold calls still succeed unchanged (T0 1825.20 / 19.01 / 1287.31; T1 4137.00 / 2951.75).
- kb-1 is render-only and was left to the renderer; no rule text was changed.
- REWORK round 9: gates 7/7 green

## Rework round 10 (src-2, seed-only)

### src-2: task 1 2022 inpatient account d9d8d4ca
I re-priced the payoff with the published encounter self-pay payoff rules, using the account as it stood on 2022-04-15.
- Balance standing: 17900.00 − 9845.00 = 8055.00.
- Discount percent: inpatient prompt-pay 15 % + 3 gross-charges points (17900.00 ≥ 7500) + 1 ledger-band point (8055.00 ≥ 2000) = 19 %. Statement recency of 18 days, US mail delivery and no point-of-service payment add nothing.
- Discount: 19 % × 8055.00 = 1530.45.
- Window-days-left credit: the 45-day window less 18 days gives 27 days, × 2.00 = 54.00.
- Payment row cb9554cd: 6846.75 → **6470.55**.
- PROMPT_PAY_DISCOUNT row d03553ab: 1208.25 → **1584.45**.
- Both rows changed in initial_state and db_closure, and the seed line in design_rationale was updated to match.
- The account still closes at 0.00. Its charge lines are unchanged, so cesarean_amount (1425.00) is unchanged.

### Bounded exhaustive pass over every other-category seeded row
Each row was re-priced against its published docs (encounter / assist / visit), using scratch script xcheck10.

| World | Rows | Checked against | Result |
|---|---|---|---|
| T0 | ED e519a1d9 + 7 txns | lines = gross 1878.00 = liability; bill-hold 4 d; uninsured 45 % = 845.10; statement 10-12, 30-day cycle; FAP adjustment; balance 389.87 | ✓ |
| T0 | case 2ef340fe + 6 txns | start = app − 365; end = det + 6 m; 40 % band (FPL 340.0); AGB 34.6 % → 649.79; liability 389.87; adjustment 643.03; app within 240 d (before first statement); docs/letter | ✓ |
| T0 | 4 appointments + 10 txns | procedure: booking lead/horizon, 7-day SMS + prep instructions, 93 h ≥ 72 h (not late); rebooked slot; consult reminders 7/2 d, 48 h call, no-show 50.00 waived as first in 12 m; primary care 25.00 waived as first | ✓ |
| T1 | inpatient d9d8d4ca + 10 txns | lines/liability 17900.00; hold 5 d; uninsured 55 % = 9845.00; statement 03-28; self-pay payoff | **re-priced (src-2)**, now ✓ |
| T1 | ED bf6ea9dc + 11 txns | gross 2518.00; hold 4 d; uninsured 45 % = 1133.10; statements 06-28/07-28/08-27; charity 862.16; payment 522.74 after charity, so no prompt-pay; closed at 0 | ✓ |
| T1 | case 600de2e7 + 6 txns | start/end dates; 40 % band (332.6); AGB → 871.23; liability 522.74; adjustment 862.16; app within 240 d; award covers E6, not the 2022 account | ✓ |
| T1 | appointment bb124223 + 3 txns | portal booking, 2-day SMS, no-show 25.00 waived as first | ✓ |

- No other miss.
- FPL percents are not checkable, because no HHS figures are published.

### Invariants
- estimate.extended.yaml, task_tools.py and tasks/0.json are byte-identical (d791707e1ecc / 96980f077dcc / a2d97f3fc0e9).
- tasks/1.json is now 49f17d4d4f77. Only initial_state, db_closure and design_rationale changed; evaluation_criteria, computations, solvability_contract and prerequisite_closure are identical.
- Gold is unchanged (4137.00 / 2951.75; 1825.20 / 19.01 / 1287.31).

REWORK round 10: gates 7/7 green
