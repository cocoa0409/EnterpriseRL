# physical_damage_claims — worklog

Draw: task 0 -> 1 prerequisite problem, factors [5,5]; task 1 -> 2 prerequisite problems, factors [6,6,6].

## Task 0 (closed, per-task gates 7/7 green)
Tree: physdam_ext_deductible_refund (root, agent) -> physdam_ext_repair_assignment (user direction to pay), value_input.
Results: repair assignment 3835.50 (all-baseline 4435.50); refund 27.90 (all-baseline 101.51; skip-edge 208.71).

### Probe table (scratch copies, check_compute evaluator)
| policy | probe | outcome |
|---|---|---|
| repair_assignment | no estimate on claim (LATEST None) | result 0 by the "no recorded estimate" clause |
| repair_assignment | confirmation or first-estimate date missing | wait 0 days, no storage allowance |
| repair_assignment | decoy: earlier claim CLM-415907326 rows on same coverage | excluded from repair payments already made by claim-number filter; used only by carve-out |
| repair_assignment | decoy: expired term-1 coverage of same VIN | different holding, never summed |
| repair_assignment | CFIELD auto first match | keyed auto_policy_id = coverage's owner term (exact value) |
| refund | damages 0 | result 0 ("when the damages are zero no refund is figured") |
| refund | refund already made exceeding share | floor at zero |
| refund | decoy: duplicate rental invoice + reversal | netted (paid 960 - reversed 210) |
| refund | recoveries above damages | capped at the refundable deductible (MN) |
| refund | same-day tie on claim report | rule: a vehicle never has two claims reported on one day |

### Pairwise method-tier table
| factor | tier A vs B | tier B vs C | distinguishing input |
|---|---|---|---|
| appraisal_wait | days x rate vs min(days x rate, cap) | min(...) vs 0 | cap operation |
| earlier_unrepaired | cash + deductible vs cash | cash vs 0 | deductible input |
| refund_deductible_source | repair deductibles vs total-loss deductibles | TL deductibles vs package parameter | different record/parameter inputs |
| repair_part_measure | latest estimate vs ACV - salvage | ACV - salvage vs payments + deductibles | different inputs |
| expense_part_measure | rental net + tow vs tow | tow vs 0 | rental input |

### Events written and their base triggers
- physdam_repair_payment: triggers [] (stays in physdam)
- physdam_deductible_reimbursement: triggers [] (stays in physdam)

## Task 1 (closed, per-task gates 7/7 green)
Tree: physdam_ext_totaled_coverage_return (root, agent) -> physdam_ext_owner_tax_title (user acceptance) -> physdam_ext_lienholder_settlement (agent); both edges value_input, state form (one affirmative, one negated).
Results: lienholder 5900.00 (all-baseline 7150.00); owner tax-and-title 195.50 (all-baseline 307.25; skip-edge 251.12); coverage return 82.23 (all-baseline 75.05; skip-edge 69.76).
Revision: P_tax as a separate replacement-tax payment dropped (one total loss payment row per payee per claim); total loss split by payee instead. Task 0 repair-assignment deductible replaced_by updated to name the lienholder settlement's case (sibling overwrite hygiene); task 0 cause factor no longer owns the shared cause read (factor independence).

### Probe table (task 1)
| policy | probe | outcome |
|---|---|---|
| lienholder_settlement | no reports and no declaration | 0 ("no vehicle value to pay") |
| lienholder_settlement | reports > 10% apart | lower report (= declared 7650 -> 5704.75) |
| lienholder_settlement | same-day valuation entries | ordered by estimate sequence, unchanged 5900.00 |
| lienholder_settlement | no vehicle change / decoy Altima row | VIN filter; no acquisition date -> no cap (5948.35) |
| owner_tax_title | no replacement on/after loss | standard half share |
| owner_tax_title | payoff above the lender payment | no lien release fee |
| coverage_return | coverage without claims | return days from today, short rate applies |
| coverage_return | package change on/after the date of loss | added rate + full refund of the change charge |

### Pairwise method-tier table (task 1)
| factor | A vs B | B vs C | distinguishing input |
|---|---|---|---|
| valuation_reports | average vs lower | lower vs declared ACV | operation / declaration input |
| recent_purchase | cap at value vs cap at value x 1.10 | capped vs none | cap operation, factor |
| earlier_damage_carve | cash + deductible vs cash | cash vs 0 | deductible input |
| sales_tax_base | payment + deductible vs value at binding | value at binding vs declared ACV | different inputs |
| return_start | date of loss vs declaration date | declaration date vs today | different date inputs |
| charge_rate_basis | change rate vs added rate + change refund | + refund vs added rate | refund input |

### Events written and their base triggers
- physdam_total_loss_payment (loss payee and named insured rows): triggers [] (stays in physdam)
- physdam_coverage_removed: triggers physdam:physdam_premium_returned (transaction_reason coverage_removed for insured_request) — stays in physdam; the tool books that return row itself
- physdam_premium_returned: triggers []
No tool writes another category; no billing, auto or rental row is written.

## Final gate run
check_extended, check_task_tools, replay_tasks, check_solvability, check_compute, check_grounding, check_cross_fire — all OK (check_traceability deferred until the KB is rendered).
INSTANTIATE round 1: gates 7/7 green

## Rework round 2 (audit revision_1: C-POL-1, C-XF1, C-XF2, C-XF3, C-XF8, C-XF9, C-XF10, C-XF11, C-REAL, XF13)
Charter rebuilt policy by policy (factor redesign in plan.md "Rework round 2 plan"); seeds completed with owner-term, billing, physdam and rental premium ledgers and read-only gold reads; task 1 dates moved (package change 2026-06-10, declaration 2026-10-07, desk review 2026-10-12, tow 240.00). Gold values moved: repair assignment 4975.50, refund 29.36; lienholder 5900.00, owner payment 254.25, coverage return 61.39. Probes re-run on scratch copies (absent estimate/declaration/acquisition/rental/tow, decoy lower-numbered claim, prior-term coverage, tow above limit, driven-in, FL glass, lessor, pending inspection, reports far apart, same-day restoration). Details and closures: rework_r2_claims.md.

### Pairwise method-tier table (round 2)
| factor | tiers | distinguishing input |
|---|---|---|
| appraisal_wait | wait-free / MN(wait-free, cap) / 0 | cap |
| repair_part_measure | latest estimate / ACV-salvage / payments+deductibles | different inputs |
| rental_part_measure | paid-reversed / rate x days / 0 | authorisation inputs |
| valuation_reports | average / lower / declared ACV | operation, declaration |
| earlier_damage_carve | damage / cap share of declared ACV / 0 | declared ACV |
| sales_tax_base | 0 / declared ACV / recognised value | different inputs |
| release_storage | days x yard rate / MN(days x shop rate, cap) / 0 | cap |
| return_start | replacement date / loss date / effective date / today | date inputs |

### Events written and their base triggers (unchanged)
physdam_repair_payment [], physdam_deductible_reimbursement [], physdam_total_loss_payment [], physdam_coverage_removed -> physdam_premium_returned (physdam only). No other category written.
REWORK round 2: gates 7/7 green

## Rework round 3 (audit revision_2: R2-XF2, R2-GATE, R2-XF19, R2-XF11, R2-XF8, R2-XF17, R2-XF18; XF 20-23)
Read: audits/policy_task/physical_damage_claims/{_difficulty.md,0.md,1.md} (revision_2 in full), XF_recipe points 17-23. Charter split into per-policy scratch pieces under /tmp/physical_damage_claims_0071/ and re-assembled after each edit; task_tools.py unchanged.

### Charter changes
- repair: generic order sentence; baseline storage days = wait beyond the free days within the storage-day allowance (param renamed storage_day_allowance); appraisal_wait tiers: towed in -> all days beyond the free days / wait within the free days -> none / otherwise -> allowance (= baseline).
- refund: generic order sentence; damages sentence renamed ("measured instead"); E1 record-test carve-out; rental part reads the latest authorization by entry date (new binding rental_auth_entry) and a closing only when dated on/after it.
- loss payee: market_adjustment struck with its three params; lp_renewal_credit added (term number / points of the coverage's owner term, cross auto); generic order sentence (replacements, caps, additions, amounts taken off).
- owner: whole-tax baseline; replacement_share removed; baseline storage = late days within the owner's allowance at the standard rate; release_storage re-tiered (yard -> all late days / with owner -> none / repair facility -> allowance); owner_storage_schedule added (state schedule, same rates as the repair rule); payment never less than the title fee (E3); E2 carve-out sentence.
- return: vehicle-added reads keyed on auto_policy_id; loss_payee_charge_ladder struck with its two params; minimum-earned charge = full-term rate x percent x share, minimum_earned decides the share by days in force, plan_minimum_earned decides the percent by payment plan (cross billing).
- Sweep (scratch sweep.py): basis-in-rule, baseline sentences, policy_source, replaced_by, factor-only plain bindings, cross-factor reads, factor id in tool name: 0 findings.

### World changes
- task 0: rental benefit rows removed (agency has not billed since the close), rental benefits cache 0.00; recovery checks reworded; closure 35 = initial 35.
- task 1: owner term becomes renewal term 2 (2 points, renewal fee 15.00, offered 2026-04-15 with a renewal bill, paid 2026-05-12); expired term 1 seeded from inception with its premium, fee, closed Paid-in-Full plan and ledger; customer since 2025-11-12; value at binding 7840.00; find_billing_invoices read inserted at step 10 (later steps +1); closure 34 = initial 34.

### Verification (scratch evaluator over check_compute build_env, gold writes replayed)
| computation | gold | factor baselines | all-baseline | skip edge |
| --- | --- | --- | --- | --- |
| repair (t0 s16) | 4975.50 | 4725.50 / 5225.50 / 4925.50 / 4660.50 / 4835.50 | 4560.50 | - |
| refund (t0 s18) | 29.36 | 36.71 / 66.07 / 27.12 / 33.62 / 30.60 | 80.18 | 219.70 |
| loss payee (t1 s13) | 5830.00 (ded 450.00) | 5650.00 / 5890.00 / 7390.00 / 5580.00 / 6080.00 / 5780.00 | 7160.00 | - |
| owner (t1 s15) | 294.25 (tax 478.75, title 33.00) | 208.00 / 275.10 / 339.00 / 271.75 / 384.25 / 334.25 | 329.55 | 271.75 |
| return (t1 s17) | 86.09 (38 days, 612.00) | 74.47 / 52.83 / 73.45 / 70.79 / 70.79 / 111.09 | 20.25 | 52.83 |
No scored or proof figure on a half-cent.

### Probes (scratch copies)
P1 second authorization entered after the claim's closing -> runs to today (1 day), stale closing ignored. P2 driven in -> 5 storage days. P3 one benefit paid -> paid tier. P4 no confirmation -> wait 0, no storage. P5 vehicle added to the expired term after the loss -> return days unchanged (38). P6 no replacement -> from the date of loss (49 days). P7 lessor with 35 late days -> tax 0, storage 1050.00, owner payment held at the title fee. P8 current plan Monthly EFT -> 8 percent (expired term's plan ignored). P9 renewal credit reads term 2 / 2 points, not term 1 / 3 points. P10 very low ACV -> loss-payee value still read by the rule; where it is nothing the owner's wait does not apply. P11 vehicle at a repair facility -> owner storage held to 5 days.

### Method pair tables (round 3 changes)
| factor | tiers | pairs |
| --- | --- | --- |
| appraisal_wait | W-free / 0 / MN(W-free, allowance) | 1-2 zero tier, 1-3 cap, 2-3 zero tier: PASS |
| release_storage | all late days / 0 / MN(late, allowance) | PASS (zero tier, cap) |
| rental_part_measure | paid-reversed / latest rate x DAYS(start, closing on/after entry or today) / 0 | PASS |

### Gates (final mode)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0: 35/35, 1: 34/34); SOLVABILITY OK; COMPUTE OK (suite branches 58.00, steps 18.50, history max 19, branch max 75); GROUNDING OK; SCOPE OK.
REWORK round 3: gates 7/7 green

## Rework round 4 (audit revision_3: R3-XF15, R3-LADDER, R3-XF23a, R3-XF23b, R3-XF13a, R3-XF13b)
Read: audits/policy_task/physical_damage_claims/{_difficulty.md,0.md,1.md} revision_3 in full. Charter re-split into scratch pieces (round trip byte-identical), edited per policy, re-assembled; task_tools.py unchanged.

### Charter changes
- repair: appraisal_wait tiers glass -> none / other loss towed in -> MX(0, W-free) / otherwise -> MN(MX(0, W-free), allowance) (baseline); new binding storage_cause.
- refund: rental paid tier = paid - reversed + latest authorization rate x days after the latest paid invoice period to the rental end (new bindings rental_paid_through, rental_end).
- owner: E2 scope and condition rewritten as a record test (payoff recorded; recorded ACVs and value at binding above a quarter of the declared ACV + larger deductible + theft add-on + permissive-collision surcharge).
- return: replacement tier and its bindings removed (start from the date of loss on a paid total loss); deletion_endorsement struck (params, sentence, bindings, cross read of variant_name); minimum_earned_tenure added (renewal share of the minimum-earned charge by term number, param long_renewal_term); auto/billing cross_category blocks re-separated (the round-3 insertion had attached the auto note to the billing entry).
- Order sentences: only the list of adjusted quantities changed in the return's sentence ("flat charge" removed); the order itself is unchanged everywhere. Sweep: 0 findings.

### World changes
- task 0: rental benefit rows re-seeded (weeks ending 09-27, 10-04 twice with the duplicate reversed 10-08, 10-11; final 4 days unbilled), cache 630.00; closure 40 = initial 40. Gold unchanged.
- task 1: term 1 Camry inception row, Camry removed and Accord added 2026-04-06 (additional 298.64, return 268.91, billed and settled), renewal priced on the Accord; Accord row moved to term 1; find_auto_policy_changes(term 1) inserted at step 8 (writes now 14/16/18); closure 41 = initial 41.

### Verification
| computation | gold | factor baselines | all-baseline | skip edge |
| --- | --- | --- | --- | --- |
| repair (t0 s16) | 4975.50 | 4725.50 / 5225.50 / 4925.50 / 4660.50 / 4835.50 | 4560.50 | - |
| refund (t0 s18) | 29.36 | 36.71 / 66.07 / 27.12 / 33.62 / 30.60 | 80.18 | 219.70 |
| loss payee (t1 s14) | 5830.00 (ded 450.00) | 5650.00 / 5890.00 / 7390.00 / 5580.00 / 6080.00 / 5780.00 | 7160.00 | - |
| owner (t1 s16) | 294.25 (tax 478.75, title 33.00) | 208.00 / 275.10 / 339.00 / 271.75 / 384.25 / 334.25 | 329.55 | 271.75 |
| return (t1 s18) | 155.33 (49 days, 612.00) | 139.08 / 85.48 / 139.03 / 147.68 / 147.68 / 147.68 | 20.25 | 85.48 |
No scored or proof figure on a half-cent.

### Probes
Q1 glass, towed, wait 19 -> 0 storage days. Q2 driven in, wait 3 -> 0. Q3 rental still open -> unbilled days run to today (810.00). Q4 final week paid -> no unbilled days (750.00). Q5 cache 630.00 differs from the rule's 750.00. Q6 recorded values at 4300.00 against a 2325.00 test ceiling -> loss-payee value positive (2775.00). Q7 Altima added after the loss is not read by the start (49 days). Q8 term 3 -> renewal share 0; term 1 -> whole. Q9 recent-purchase reads the Accord's 2026-04-06 acquisition (174 days), not the Camry.

### Method pair tables (round 4 changes)
| factor | tiers | pairs |
| --- | --- | --- |
| appraisal_wait | 0 on glass / MX(0, W-free) / MN(MX(0, W-free), allowance) | 1-3 zero tier where W-free > 0, 2-3 cap: PASS |
| rental_part_measure | paid-reversed+rate x unbilled days / rate x DAYS(start, end) / 0 | PASS |
| return_start | DAYS(loss, exp) / DAYS(effective, exp) / DAYS(today, exp) | PASS |

### Gates (final mode)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0: 40/40, 1: 41/41); SOLVABILITY OK; COMPUTE OK (suite branches 59.00, steps 19.00, history max 19, branch max 72); GROUNDING OK; SCOPE OK.
REWORK round 4: gates 7/7 green

## Rework round 5 (render scan audits/render_source/physical_damage_claims/render_r1.md: F1-F4, XF 26)
Read render_r1.md in full and XF_recipe points 24-26. Charter re-split into scratch pieces (byte-identical round trip), edited, re-assembled; task_tools.py unchanged; gold and worlds unchanged.

### Charter changes
- loss payee (F1): recent-purchase sentence and cross note now read the original acquisition date on the vehicle-added change for the VIN on any owner term, latest by change effective date (compute unchanged, now identical).
- refund (F2): no-benefit rental branch "no days when the rental ends on or before its start date"; compute MX(0, DAYS(start, end)).
- return (F3): substitution tier names the latest vehicle added to the owner term and states both window ends counted (0 to N days before today); ladder text aligned.
- return (F4): baseline sentence defines the minimum-earned charge as percent x time-in-force share x tenure share (both one at the standard); factor sentences "is replaced by"; combination sentence names only those baseline quantities; cross note aligned.
- Class sweeps over every cross read, day count, latest-row read and combination sentence: no further member. XF 26: no factor rests on a recorded amount that embeds it. Scripted sweep: 0 findings.

### Probes
F1 world reads the Accord's term-1 change (2026-04-06), cap 7840.00. F2 start after the closing or after today -> rental part 0.00. F3 add today -> 5; add exactly 30 days before -> 5; 31 days -> 10; in-window add plus a future-dated add -> 10 (latest add, as the rule now says). F4 shares 0.5 x 0.5 -> charge 7.65. Gold re-evaluated: 4975.50, 29.36, 5830.00, 294.25, 155.33 (unchanged).

### Gates (final mode)
EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0: 40/40, 1: 41/41); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
REWORK round 5: gates 7/7 green

## Rework round 6 (seed-only; cross-product re-judge S3, audits/policy_kb + audits/runtime_context revision_3)
Read policy_kb/physical_damage_claims/{_difficulty.md,0.md,1.md} and runtime_context/physical_damage_claims/{0.md,1.md} in full; only S3 is in scope (S2 left as is).
- tasks/1.json: auto_policy_changes 7c5e1a93 (Camry auto_vehicle_added effective on the new-business date, no additional premium) removed from initial_state and db_closure; its seed_consistency entry dropped; term-1 vehicle-change read objective and rationale reworded. The Camry remains recorded by term 1's new-business premium and vehicle_count and by its 2026-04-06 removal row, as the auto rules produce it (task 0's Corolla convention).
- Gold read set unchanged (find_auto_policy_changes on term 1 returns the removal and the Accord addition); closure 40 = initial 40.
- Gold unchanged and confirmed: no physdam compute reads the row (recent-purchase reads the Accord VIN; the substitution tier reads term 2); check_compute recomputes 4975.50, 29.36, 5830.00, 294.25, 155.33 equal to expected.
- physdam.extended.yaml f165003a and task_tools.py 43a3e10b byte-identical (sha256 checked).
- Gates (final mode): EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0: 40/40, 1: 40/40); SOLVABILITY OK; COMPUTE OK; GROUNDING OK; SCOPE OK.
REWORK round 6: gates 7/7 green
