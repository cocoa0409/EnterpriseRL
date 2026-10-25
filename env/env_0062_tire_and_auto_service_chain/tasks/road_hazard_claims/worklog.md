# road_hazard_claims (hazard) — instantiation plan / worklog

## Step 0 draws (draw_counts.py --tasks 2)
- task 0: prerequisite_problems=2, factor_counts=[5,6,6]
- task 1: prerequisite_problems=2, factor_counts=[5,4,4]

## DSL constraints found (drive the design)
- compute reads only: this certificate's fields/events, tier params, policy K params, OTHER categories'
  holdings/events. No own-category cross reads (check_extended rejects), no vehicles/stores reads.
- => a value_input edge must come from a write on the SAME certificate the root computes on.
- => every scored number must be derivable from DB rows; receipt figures (caller documents) can only
  decide scope, never enter compute. Out-of-area reimbursements are therefore scoped to receipts at or
  above the plan cap (self-naming overwrite), the cap being the quantity the factors act on.
- LATEST is not zeroed by the history floor; at least one SUM/COUNT/MAX must bear weight per computation.
- hazard_cancellation_refund with payment_method crestline_card/fleet_account triggers card/fleet: every
  certificate whose refund we write is paid cash_or_debit or bank_card.
- No date-valued computations (near() is string-equal for dates; DSL has no date builder).

## Tree decision
User-owned computable writes available: holder cancellation of an active certificate (base: holder confirms).
Two disjoint cancellation situations exist in base refund ordering: covered set still in service (pro_rata /
full window) vs covered set returned under the satisfaction trial (covered_set_returned). One user tool each.

Task 0 (root = pro-rata cancellation, user):
  R0 hazard_ext_holder_cancellation_refund  <- P1 hazard_ext_outside_replacement_reimbursement (value_input: benefits paid)
  P1 <- P2 hazard_ext_outside_tow_reimbursement (state_gate: occurrence claim number opened by the earliest service = tow)
Task 1 (root = returned-set refund, user):
  R1 hazard_ext_returned_set_refund <- P3 hazard_ext_outside_repair_reimbursement (value_input: benefits paid)
  R1 <- P4 hazard_ext_store_replacement_share (value_input: benefits paid)

## REVISED tree decision (supersedes the block above) — reasons
- A pro-rata cancellation refund deducts benefits paid, so a store/out-of-area REPLACEMENT share feeding a
  cancellation floors the refund at 0 unless the certificate price is high and the shares are prorated small.
  Life-of-Tread (72 months, 22%, max 64.99/tire, spare covered) is the only plan with enough refund headroom.
- Two tread-based store-replacement computations in one task collide on "latest technician damage reading";
  the out-of-area replacement therefore reads the position's latest ROUTINE reading (wear_pattern even), the
  counter replacement reads the DAMAGE reading: distinct filters.
- Tow / repair reimbursements are thin (cap-bounded): they go to task 1 whose draw is 4,4.
- Two user tools: holder cancellation split by plan family (Life-of-Tread refunds on a usage share; term
  plans on months) — two disjoint policy scopes, two tools.

Task 0 (draw 5,6,6) — Life-of-Tread holder cancels (vehicle moved into business use):
  R0 hazard_ext_lot_cancellation_refund (user, 5)  <- P1 hazard_ext_counter_replacement_posting (agent, 6) [value_input: benefits]
  R0 <- P2 hazard_ext_outside_replacement_reimbursement (agent, 6) [value_input: benefits]   (P1,P2 commute)
Task 1 (draw 5,4,4) — term-plan holder cancels:
  R1 hazard_ext_term_cancellation_refund (user, 5) <- P3 hazard_ext_outside_repair_reimbursement (agent, 4) [value_input]
  P3 <- P4 hazard_ext_outside_tow_reimbursement (agent, 4) [state_gate: the breakdown's claim number, opened by the tow]

## FINAL tree (supersedes both blocks above; resumed after account cut)
Why changed: replacement-sized benefits floor a cancellation refund to 0 unless the plan is Life-of-Tread
(5 tires x 64.99, 72-month term); thin cap-bounded reimbursements (tow, repair) cannot carry 6 factors,
so they go to task 1 (draw 4,4); task 1's user write is the holder's own authorization of a store
replacement (the holder accepts the prorated replacement — a confirmation over their own affairs).

Tools (uuid8 generated once each):
  confirm_life_of_tread_cancellation_58ab2fcf   user   (task 0 root)
  post_hazard_counter_replacement_324c4972      agent  (task 0)
  reimburse_hazard_outside_replacement_5f5d3272 agent  (task 0)
  authorize_hazard_store_replacement_0d9adf2d   user   (task 1 root)
  reimburse_hazard_outside_repair_444e27b0      agent  (task 1)
  reimburse_hazard_outside_tow_3bff1c36         agent  (task 1)
Task 0 (5,6,6): R0 hazard_ext_lot_cancellation_refund <- P1 hazard_ext_counter_replacement_posting [value_input]
                R0 <- P2 hazard_ext_outside_replacement_reimbursement [value_input]; P1/P2 commute.
Task 1 (5,4,4): R1 hazard_ext_store_replacement_authorization <- P3 hazard_ext_outside_repair_reimbursement
                [value_input: the position's repair count selects the coverage route]
                P3 <- P4 hazard_ext_outside_tow_reimbursement [state_gate: the breakdown's claim number is the
                one the tow opened]
Scratch design/simulation: /tmp/road_hazard_claims_0062/design.py

## Task 0 factor plan (committed)
R0 lot cancellation refund (6): clock_start_fx[M, fleet roster: enrolled & not removed -> enrollment date | pending
  cancellation request -> its date | cancellation date]; day_count_fx[M, in force <12m actual days | 12-35m 30-day
  months | calendar months]; tread_life_fx[P, tires routine reading usable share <=25% x0.5 | <=50% x0.8 | x1];
  cancel_fee_fx[P, card open & no late fee 12m -> 0 | open & late fee -> reduced | plan fee];
  roadside_credit_fx[P, unused calls & none used -> K1/call | some used -> K2/call | 0];
  bundle_clawback_fx[P, alignment plan sold on the certificate's ticket -> K1 | alignment bought separately within 30d -> K2 | 0]
P1 counter replacement posting (6) & P2 out-of-area replacement (6): price/tread selection methods + coverage
  points (card perk, care club rotations, tire-and-alignment bundle, prior covered repairs on the position).

## Progress log
- task_tools.py: 3 task-0 tools written; TASK TOOL CONTRACT OK (fixed unit wording for odometer/tread).
- hazard.extended.yaml assembled from scratch fragments (frag/r0,p1,p2.yaml) by assemble.py; base text copied verbatim.
- check_extended: structure clean (only "no tasks yet" fails at that moment).
- check_compute first run: recompute == expected for all three; card factors failed "no card rows touched" ->
  seeded a 2024-06-08 card late fee (outside the 12-month window: also the near-miss for the card tiers).
- factor sensitivity (task 0): P1 110.70 (baselines 114.80/97.20/102.60/99.90/121.50; all 92.40);
  P2 75.60 (269.99/56.00/77.00/67.50/64.80/86.40; all 200.00); R0 56.43 (54.87/55.50/95.73/31.43/16.43/76.43; all 45.37)
- TASK 0 CLOSED (all 7 per-task gates green). Build chain (scratch): t0_world.py -> t0_task.py -> t0_trace.py ->
  t0_text_a/b/c/d.py -> t0_build.py; policy fragments p1.py/p2.py/r0.py -> assemble.py.
  Probe table + revisions recorded in tasks/0.json design_rationale.

## Task 1 plan (draw 5,4,4)
R1 hazard_ext_store_replacement_authorization (user authorize_hazard_store_replacement_0d9adf2d, 5 factors)
P3 hazard_ext_outside_repair_reimbursement (reimburse_hazard_outside_repair_444e27b0, 4)  [value_input: repair count]
P4 hazard_ext_outside_tow_reimbursement (reimburse_hazard_outside_tow_3bff1c36, 4) [state_gate: breakdown claim number]
- Task 1 policies written (frag r1/p3/p4 via r1.py, p34.py); 6 tools in task_tools.py (gate OK).
- Hygiene fix: every out-of-area policy is scoped to a receipt that COVERS its computed allowance/base (so the
  plan never pays more than the receipt); task 0 receipt raised to tire 289.50 (+26.50 mounting = 316.00).
  P1/R1 both retire the same two hazard_evt_replacement clauses: each replaced_by is its scope sentence naming
  the sibling case. P2/P3/P4 all retire the out-of-area sentence: each tail names the other two cases.
- Task 0 re-run after these changes: all 7 per-task gates green.
- TASK 1 CLOSED (all per-task gates green). Tow claim number minted by the tow tool: RHC-2685888 (repair carries it).

## Edge-probe table (both tasks; full text in each task's design_rationale)
| read | decoy / absent case | handling |
|---|---|---|
| CFIELD card card_account_id status=active | closed second card | filtered out; absent -> card tiers fall through (fee = plan fee, uplift/points 0) |
| XCOUNT card_late_fee within 12 months | late fee older than 12 months (seeded 2024-06-08 / 2025-02-08) | excluded by window (near-miss) |
| CFIELD alignment by vehicle_id + status=active | expired plan / plan on another vehicle | filtered; absent -> 0 points / no clawback |
| CPARAM fleet national_price_file status=active | closed second fleet account | filtered; none -> 0 |
| XLATEST fleet roster by vehicle_id | removal dated before re-enrollment; other vehicles | open = enrolled and (no removal or removal earlier) |
| XLATEST fleet tires invoice discount by vehicle, category tires, txn_date = set purchase date | alignment invoice; later tire invoices | cannot match |
| XLATEST tires damage reading (covered set; task 1 also event_date today) | another vehicle's set; older damage reading | filtered by tire_set_id (and date) ; absent -> policy out of scope |
| XLATEST tires routine reading (wear even, covered set) | older rotation readings | latest wins (2026-09-12 LF check); absent -> months basis / tread factor x1 |
| LATEST pending cancellation request | none | clock from cancellation date |
| COUNT repairs on position / certificate; roadside within 12 months | other positions; old calls | eq filters / window |
| zero division / None | tire_count, original-min, DAYS(eff,exp) all > 0; None guarded before arithmetic | — |

## Final gate block (difficulty-wide run)
EXTENDED OK | TASK TOOL CONTRACT OK | REPLAY OK | SOLVABILITY OK | COMPUTE OK (suite branches mean 69.00, steps 19.00,
history_rows_max 8, branches_max 79) | GROUNDING OK | CACHE-DIFF INFO (optional) | SCOPE OK
TRACEABILITY NOT OK — only the six unlock tool-name values (docs not yet published); every other copied value traced.

## ROUND 2 REWORK PLAN (audit r1: task0 SOURCE-FACTOR RED C3d; task1 SOURCE-POLICY RED C1 + SOURCE-FACTOR RED seed/C2/C3)
- C1: counter posting + store authorization: coverage points apply only to a PRORATED percentage (a 100 stays 100);
  store authorization's repair route declares an overwrite of the base 100-percent sentence (scoped replaced_by).
- C2/C3: tow & repair rebuilt: size multiplier (0.9 small-tread tier) removed as method; roadside-usage and
  repeat-repair deductions removed; out-of-area replacement drops certificate-wide repair points.
  New genuine methods: per-breakdown limit (lesser-of with what the same breakdown already received) on tow
  (vs a Crestline dispatch) and on repair (vs the out-of-area tow); out-of-area replacement proration measure
  (mileage share / lesser of months and mileage / months).
- Factor independence: every method factor outputs a selector or a value read only from its own evidence;
  composition sits in plain bindings stated once in the rule (LOT day-count no longer reads the clock output,
  out-of-area price ceiling no longer reads the card uplift).
- Seeds: task0 alignment purchase_price 209.99 (Lifetime tire-bundle discount 40.00); card limits inside the
  variant range; fleet Starter (per_invoice billing, credit <= 5000); task1 alignment plan removed (no
  alignment plan with commercial_use_eligible true can carry a bundle); task1 fleet Starter (roster 1-4).
- O1 state form for E2/E3; O2 sentence scope = window; O5 docstrings neutral; O6 LOT scope limited to
  cash/debit and bank-card certificates; O8 commercial use judged on the service date; O10 price-file read
  tied to the roster's account; O3 counter scope: damage reading dated before the posting day; O7 covered
  repairs defined once (repair entries + out-of-area repair reimbursements on the position).
- R2 task 0 world: certificate/set from 2024-11-09 (exp 2030-11-09), unit 249.99, LoT price 55.00 x 5; rotations every ~3 months
  (2025-02-22 .. 2026-07-11, odometer 72000); RR damage reading 4/32 @74500; LF routine 5/32 @75600; alignment price 209.99 (tire-bundle
  discount 40.00); card limit 5000; fleet per_invoice. Figures: counter 57.60 (all-baseline 40.00), out-of-area 105.25 (132.00),
  LOT refund 29.03 (0.00); skip counter -> 86.63, skip out-of-area -> 134.28.
- R2 finding while tuning: a lesser-of breakdown limit makes the uplift parameters decorative whenever it binds.
  Tow method changed to a subtraction (the dispatch of the same breakdown is deducted from the tow allowance) and a
  second-tow tier (plain cap); repair method keeps lesser-of on the repair cap only, with the labor/card/fleet
  components added outside it. Task-1 dispatch amount set to a 30.00 trip charge.

## ROUND 2 probe table (first-match / CFIELD / history reads)
| policy.read | decoy | absent | tier covering absent |
|---|---|---|---|
| all: CFIELD card_account_id status=active | closed second card skipped by the filter | None | card tiers fall through (0 points/uplift; LOT fee = plan fee) |
| all: XCOUNT card_late_fee within 12m | 2024/2025 late fees outside window (seeded near-misses) | 0 | first card tier when an active card exists |
| counter/out-of-area: CFIELD alignment by vehicle+status=active | expired plan skipped | None | 0 bundle points / no clawback |
| auth/tow/repair: roster XLATEST by vehicle; account via its fleet_account_id; CFIELD status, CPARAM price file on that account | another fleet account of the customer; removal before re-enrollment | None | fleet tiers fall through |
| price rules: fleet tires invoice by vehicle+category tires+txn_date=set purchase date | alignment or later tire invoices | None | instant-savings or unit tier |
| counter: damage reading XLATEST (covered set) | same-day reading belongs to authorization scope (rule) | None | policy out of scope |
| authorization: damage reading with event_date=today | older damage readings | None | policy out of scope |
| out-of-area: latest rotation (covered set) | other sets' rotations | None | months basis |
| LOT: latest routine reading (wear even, covered set) | damage readings excluded by filter | None | tread factor x1 |
| LOT: pending cancellation request | confirmed/withdrawn requests excluded by filter | None | cancellation date |
| tow: latest dispatch / latest out-of-area repair, within 30 days | August 2026 out-of-area repair (task 1, 48 days) | None | plain allowance |
| repair: latest tow / latest dispatch within 30 days | — | None | repair cap |
| counter/auth: covered repairs on the position | other positions' repairs | 0 | no repair points / full route |
| zero/None/date edges | tire_count>0, original-min>0, DAYS(eff,exp)>0, warranted_miles>0; None guarded before arithmetic; MONTHS/DAYS on date strings only | | |

## ROUND 2 closure list
- C1 (100-percent sentence): counter posting — points only on a prorated percentage (no override); store authorization — overwrite declared, scoped. CLOSED.
- C2 (method that is a number): repair drops the size multiplier and gets a breakdown-limit method (lesser-of on the repair part); tow keeps a light-truck rate as a PARAMETER (no 10/32 tier) and gets a breakdown-limit method (dispatch deducted / plain cap after a same-breakdown repair). CLOSED.
- C3(a) 0.9 small-tread tier removed; C3(b) roadside-usage deduction removed; C3(c) repeat-repair deduction removed; C3(d) certificate-wide repair points removed (counter keeps per-position covered repairs). CLOSED.
- Task-1 alignment seed (Truck & Performance on a commercial truck) removed with its invoice; bundle points replaced by card points. CLOSED.
- Task-0 alignment price 209.99 (tire-bundle discount). CLOSED. Seed sweep: card limits, fleet program/billing/credit fixed.
- O1 E2/E3 state form; O2 E3 window scope; O3 counter scope = earlier-day damage reading; O4 E4 gate now a compute binding (value_input);
  O5 docstrings neutral; O6 LOT scope = cash/debit/bank-card certificates; O7 covered repairs defined once (counter + authorization);
  O8 commercial use judged on the service date (stated in every claim scope); O10 price file tied to the roster's account. Addressed.
- Not changed: O9 (damage_type comes from the holder: base issue), O11 loyalty-point realism notes, O12/O13 tool notes.

## ROUND 3 plan (audit r2: task0 PASS, task1 SOURCE-FACTOR RED C4)
- C4: tow breakdown-limit tier 2 rebuilt on the dispatch's own record: the latest Crestline roadside dispatch within the
  receipt window is the breakdown's dispatch, and its roadside_service_type selects the method — flat-tire change:
  allowance less what it received; Crestline tow: lower of the allowance and tow_reimbursement_cap less what that tow
  received (one tow cap per breakdown); none: allowance. Every tier reachable on Plus / LoT / Commercial LT plans.
- R2-O2: the tow is booked under the claim number the breakdown's dispatch carries (tool takes claim_number), so the
  breakdown is one claim on the records; the repair joins the same claim.
- R2-O1: allowance factors relabelled (tier from the hazard plan, cross_difficulty null).
- R2-O3: the fleet price tier states its convention (whole tires-invoice discount spread over the ticket's tires).
- R3 probes (tow ladder, task-1 world copies): Crestline tow dispatch 60.00 -> tier 2, 40.00; dispatch 40 days old -> plain 145.00;
  a later repair entry after the dispatch -> plain 145.00; older decoy dispatch (2026-08-01) plus the current one -> tier 1, 115.00;
  no dispatch -> plain 145.00. Repair: dispatch only (no tow) -> tier 2, 84.00. Gold unchanged: tow 115.00, repair 69.00, authorization
  192.81; task 0 figures unchanged (57.60 / 105.25 / 29.03). History rows max 11 (the tow reads the latest claim entry of any type).
- R3 closure: C4 CLOSED (tier 2 = the breakdown's Crestline tow; pairwise: dispatch roadside_service_type separates tiers 1/2,
  a dispatch as latest claim entry within the window separates both from the plain tier). R2-O2 addressed (one claim per breakdown:
  tow booked under the dispatch's claim number, repair under the same; amounts read by claim number). R2-O1 addressed (labels).
  R2-O3 addressed (convention stated in all three price ladders; task-0 values unaffected — bank-card ticket).

## ROUND 4 (audit r3: charter CLEAN; observations R3-O1, R3-O2)
- R3-O2 CLOSED: the tow rule states that a tow with no dispatch of the breakdown on file opens a new claim number of its own; the tow
  tool books under the given claim number and, when claim_number is empty, opens a new one (RHC-2 + 6 digits); docstring states exactly
  that. Probe: empty claim_number -> a new RHC-2xxxxxx number; RHC-2387442 -> booked under it (gold path, entry id unchanged).
- R3-O1 CLOSED: the repair breakdown limit now reads "less the amounts of the out-of-area tow reimbursement entries on that tow's claim
  number (a Crestline dispatch paid on the same claim number is not counted here)"; compute already filtered reimbursement_type tow.
- No scored value moved (gold arguments unchanged, COMPUTE recomputes 115.00 / 69.00 / 192.81 and task 0 57.60 / 105.25 / 29.03); task 0 files untouched.
REWORK round 4: gates 7/7 green

## ROUND 5 REWORK (audits/render_source/hazard/notes.md, items 1-14)
Closures by item (no scored value moved: task0 57.60 / 105.25 / 29.03, task1 115.00 / 69.00 / 192.81; skip figures and baseline_results unchanged, recomputed by check_compute/replay):
- 1 LOT: assembly sentence removed; the result sentence (baseline) states generically "after every addition to it and deduction from it that applies, it is rounded half up to the cent and held at 0.00 or more"; call credit and bundle clawback each state their own effect on the refund.
- 2 counter: points sentence moved into baseline, generic ("Points added to or taken from the counter-replacement coverage percentage apply only to a prorated percentage ... held between 0 and 100; ... 100 under the full-replacement test stays 100"); each points schedule names its target.
- 3 out-of-area replacement: "Where the card cap uplift raises the cap" and "Any out-of-area service allowance" sentences removed; baseline defines the out-of-area cap and Crestline's own price, reimbursement = pct x base / 100 plus every allowance that applies, only that sum rounded; points sentence generic in baseline.
- 4 store authorization: points sentence generic in baseline; "as stated above" removed.
- 5 repair: assembly sentence removed; baseline defines the repair part and "repair part held at 0.00 or more plus every allowance and uplift that applies; only that sum rounded, never below 0.00".
- 6 tow: assembly sentence removed; baseline "The tow rate is 1, and the tow allowance is tow_reimbursement_cap times the tow rate, plus every uplift that applies to it, rounded"; light-truck factor now sets the tow rate.
- 7 miles floor: rule now "the warranted_miles less the miles driven, held at 0 or more" = compute MX(0, ...).
- 8 last_rotation_date: owned by the proration-measure factor; tire-care factor reads its own care_last_rotation (same evidence, own binding).
- 9 repair: last_tow_claim/paid, last_dispatch_claim/paid, repair_part moved into repair_breakdown_limit_fx bindings; tow: last_dispatch_claim/paid and the limit arithmetic now factor bindings tow_deduction / tow_ceiling (limit no longer reads the tow allowance: flat change = deduction, Crestline tow = ceiling cap - paid); result is plain assembly.
- 10 confirm tool: body confirms the most recent request awaiting confirmation (update to confirmed) and creates a confirmed request only when none awaits; docstring and LOT rule state the same lifecycle.
- 11 overwrites: every replaced_by now restates the retired base content for every case outside scope (pro_rata formula, holder-decision sentence, coverage_pct/amount/100-percent clauses, repair receipt-amount clause, tow cap/one-call clause, out-of-area distance condition), then names the scope; no "keeps the base rule" left.
- 12 LOT overwrite #3 dropped; call credit is added to the refund, "the calls themselves still lapse with the certificate".
- 13 LOT: baseline defines "the Life-of-Tread counting date" (= cancellation date); clock-start moves the counting date, day-count works "from the counting date" (both act on a baseline quantity; no factor reads another factor's output).
- 14 repair breakdown limit: "the most recent out-of-area tow reimbursement on the certificate by service date" / "the most recent Crestline roadside service entry ... by service date" (= LATEST in compute).
- "below"/"above" references removed from scope sentences; task 0 proof text swept ("counted from" -> "counting date").
Factor independence (transitive, every policy): all six clean; plain assemblies only.
Probes (round 5): tow old vs new limit formula over allowance {0..160} x paid {0..200} x 3 modes: 108/108 equal; confirm tool with no request -> creates confirmed hcr_ row; with an awaiting request (+ a withdrawn one) -> updates the awaiting one to confirmed, withdrawn untouched; miles floor 60000 warranted / 70000 driven -> 0 (no negative); traceability 28/28, 29/29.
Gates: EXTENDED OK | TASK TOOL CONTRACT OK | REPLAY OK | SOLVABILITY OK | COMPUTE OK | GROUNDING OK | SCOPE OK | CACHE-DIFF INFO | TRACEABILITY OK
REWORK round 5: gates 7/7 green

## ROUND 6 REWORK (audits/policy_kb/road_hazard_claims/0.md, 1.md + audits/runtime_context/road_hazard_claims/0.md, 1.md)
Audit ran on yaml sha b387b42a (round-5 source). No scored value moved (task0 57.60 / 105.25 / 29.03, task1 115.00 / 69.00 / 192.81; skip figures 86.63 / 134.28 and 216.64 / 84.00 unchanged; compute untouched).
- KB-1 (render item) checked at source: no replaced_by or rule sentence says "every out-of-area repair and tow remain under the base ..." (round 5 already restated the retired clause for out-of-scope cases); the out-of-area replacement scope now names repairs and tows only as sibling cases that state their own out-of-area condition. Nothing to fix at source; the hub sentence is a render fix.
- S-1 closed: the three out-of-area-condition overwrites (replacement, repair, tow) now share one wording that names the sibling cases by case: "an out-of-area tire replacement reimbursed at the out-of-area reimbursement, an out-of-area tire repair reimbursed at the out-of-area repair reimbursement and an out-of-area tow reimbursed at the out-of-area tow reimbursement"; "repair allowance", "tow allowance" (as a sibling descriptor) and "reimbursement base" (as a sibling descriptor) are gone; each replaced_by restates the base condition for every other claim, then the own case, then "the out-of-area <sibling> and the out-of-area <sibling> reimbursed that way state their own out-of-area condition".
- S-3 closed: each rule defines the receipt test in figures: "The receipt covers the out-of-area reimbursement when the amount the holder paid the outside shop on it is at least the out-of-area reimbursement." / repair receipt ... out-of-area repair reimbursement / tow receipt ... the tow operator ... out-of-area tow reimbursement. Probes: 326.50 >= 105.25, 214.00 >= 115.00, 90.00 >= 69.00 (in scope); a receipt below the figure falls out of scope to the base terms. solvability_contract out-of-area conditions now cite the receipt test.
- S-4 closed (sweep of every rationale / objective / necessity / tracing / factor_trace / closure / contract string in both tasks against initial_state):
  task 0: counter posting coverage_pct tracing and factor_trace now say outside the full-replacement period (50 whole months remain, fewer than 72-12 = 60); out-of-area tracing/factor_trace drop the irrelevant 16250 in-period test and state outside the out-of-area full-replacement period (23 whole months); find_tire_events necessity no longer cites an "out-of-area tread basis" (the 2026-07-11 rotation decides the proration measure, the 2026-09-12 reading the tread-life factor); "five other categories" -> four; tools_do_not_block and the confirm action's business_effect carry the round-5 request lifecycle (confirm an awaiting request, else record a confirmed one; none here).
  task 1: find_hazard_events objective/necessity = LF repairs 2026-08-08 / 2026-09-19, LF out-of-area repair reimbursement 2026-08-27 (35.00, RHC-2387298), Crestline flat-tire change 2026-09-24 (30.00, RHC-2387442); repeat-repair deduction and "no out-of-area entry yet" removed; find_tire_sets "vehicle-size multiplier" -> light-truck tow rate; "Fleet Business" -> Fleet Starter (no national price file); "73.60" -> 53.40; tow objective books under RHC-2387442 (not a new claim); auth repair-route factor_trace counts 2 repairs + 2 out-of-area reimbursements at handling time; history rows 11 (suite max).
  Quoted-sentence check: every single-quoted rule/persona/docstring quote in both tasks is found verbatim in the sources.
- S-2, S-5, S-7 observations, S-6 base: left as is.
Factor independence unchanged (compute untouched; six policies clean).
Gates: EXTENDED OK | TASK TOOL CONTRACT OK | REPLAY OK | SOLVABILITY OK | COMPUTE OK | GROUNDING OK | SCOPE OK | CACHE-DIFF INFO | TRACEABILITY OK
REWORK round 6: gates 7/7 green
