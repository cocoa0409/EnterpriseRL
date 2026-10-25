# alignment_plan_service — authoring plan / worklog (instantiate)

## Step 0 pre-check
- draw (draw_counts.py --tasks 2):
  - task 0: prerequisite_problems=3, factor_counts=[5,6,4,5]
  - task 1: prerequisite_problems=1, factor_counts=[6,5]
- Product numeric writes available in alignment (event, field): purchase.purchase_price, service.charge_amount,
  service.parts_charge, readjustment.parts_charge, refund.amount. Booking / retirement / expiration carry no number.
  6 problems are needed, so purchase pricing appears twice (two different sale programs) — documented compromise.
- DSL limits: a purchase computation must be anchored on an EXISTING alignment plan of the same tier (P() reads the
  anchor's tier); target_holding F() only reads alignment_plans fields; cross reads filter by exact values (kwargs may be
  expressions such as vehicle_id=F('vehicle_id')).
- Record-visible "open" work: stores post plan-holder work orders / readjustments with service_basis 'none' and the plan
  desk sets the basis and charges (refinement stated in the extended rules).

## Tools (uuid8 generated once each)
- price_alignment_work_order_228c355b   agent  labor: service_basis + charge_amount on an open work order
- price_work_order_parts_2c1ce050       agent  parts_charge on an open work order
- confirm_alignment_cancellation_b0865de9 user  holder confirms pending request -> plan cancelled + refund row
- enroll_household_alignment_plan_f0fe3800 user second-vehicle plan at household rate (purchase)
- renew_alignment_plan_418ab11e         user   renewal of an expired month-based plan (purchase)
- price_alignment_readjustment_e00d4c5e agent  open readjustment -> guarantee basis + parts_charge

## Task 0 tree (household switch, Dublin OH)  root H, prereqs C, L, Pp
- H  alignment_ext_household_enrollment (root, user, 5 factors) <-state_gate- C (one active plan per vehicle)
- C  alignment_ext_cancellation_settlement (user, 6 factors) <-value_input- L, <-value_input- Pp (refund settles the
     open work order charges of the cancellation day)
- L  alignment_ext_open_visit_labor (agent, 5 factors)
- Pp alignment_ext_open_visit_parts (agent, 4 factors)

## Task 1 tree (renewal, Lakewood CO)  root R, prereq J
- R  alignment_ext_term_renewal (root, user, 6 factors) <-value_input- J
- J  alignment_ext_readjustment_parts (agent, 5 factors)

## Progress log
- 21:3x extended: policies L (open_visit_labor, 5f), Pp (open_visit_parts, 4f), C (cancellation_settlement, 6f),
  H (household_enrollment, 5f) written; task_tools.py: 6 tools, TASK TOOL CONTRACT OK.
- Scratch seed builder /tmp/alignment_plan_service_0062/seed0.py (ids.json fixed uuids), evaluator ev.py.
- T0 opening-world evaluations: L=54.19 (baselines 18.19/73.99/62.99/69.19/64.19, all 59.99);
  H=167.49 (187.49/149.99/179.99/177.49/182.49, all 224.99). Pp, C evaluated at handling time in the task build.
- Fix: L factor alignment_type_share now owns wo_type (evidence read) — check_extended evidence rule.
- Task 0 built (tasks/0.json via scratch build0_*.py). Gold: L 54.19 @13, Pp 54.14 @15, C 17.67 @17 (user), H 167.49 @19 (user).
  Skips: Pp w/o L 56.99; C w/o L 71.86; C w/o Pp 31.82; H w/o C 167.49 (state_gate: PB stays active, no refund row).
- Fixes during task 0: tools on service/readjustment/purchase events gained the blueprint action_binding args
  (alignment_plan_id, source_alignment_event_id, vehicle_id) required by check_solvability; Pp purchase-kit read moved
  LATEST -> MAX (history load-bearing floor); card non-merchandise rows store_id None (dangling-FK gate); dropped two
  unread seed rows (tire booking, single-service event) to match the replay closure.
- Bug caught: a `grep && cat` chain skipped the J header append, so J's basis/factors landed under R; cut and re-appended.
- Task 0 per-task gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.
- R (term_renewal, 6f) and J (readjustment_parts, 5f) written; H/R replaced_by tails now exclude each other's case by name.
- Task 1 built (tasks/1.json). Gold: J 16.25 @11 (agent), R 112.59 @13 (user). Skip J -> R 137.59.
  T1 per-task gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK, GROUNDING OK, SCOPE OK.

## Edge-probe table (scratch copies, decoy rows inserted FIRST so first-match reads would hit them)
| task | read probed | decoy / edge | result vs gold | verdict |
|---|---|---|---|---|
| T0 | CFIELD card status=active (L, Pp, C, H) | closed card account listed first | all four unchanged | filter holds |
| T0 | CFIELD/CPARAM tires vehicle+active (L, C) | ordered Value Touring set on the Civic listed first | unchanged | status filter holds |
| T0 | CFIELD hazard vehicle+active / EXISTS active (L, C, H) | expired certificate on the Civic listed first | unchanged | status filter holds |
| T0 | XLATEST hazard replacement by certificate id (L) | impact cert on another vehicle, expired | unchanged | cert-id filter holds |
| T0 | LATEST request withdrawn (C age anchor) | withdrawn request 2026-09-30 on PB | refund 22.67 (age 8 days, fee 0) | tier (a) of the rule, as stated |
| T0 | XCOUNT late fees 12 months (all cardholder factors) | late fee 2026-02-08 | 58.59 / 55.85 / 15.17 / 174.99 | late tier, as stated |
| T0 | EXISTS Plus/LoT (H) | Plus certificate | 157.49 | plus tier, as stated |
| T0 | absent active tire set (L, C) | set retired | labor 69.19, refund floored 0.00 | fall-through tiers, floor as stated |
| T1 | CFIELD card active (J, R) | closed card listed first | unchanged | |
| T1 | CFIELD tires vehicle+active (J, R) | active set on another vehicle listed first | unchanged | vehicle filter holds |
| T1 | MAX parts of corrected alignment (J) | corrected alignment without a kit | 104.48 (listed price path) | tier (c), as stated |
| T1 | COUNT/LATEST guarantee readjustments (R) | earlier guarantee readjustment 2026-10-01 | unchanged (same-day tier wins) | as stated |
| T1 | grace anchor (R) | last included alignment outside final 6 months | 145.59 (expiration anchor, outside grace) | as stated |
Absent-record cases: no card -> every cardholder factor 0 / share 1.00 (fall-through); no active tire set -> t_install None -> 9999 days -> credit 0 / P() value; no certificate -> XLATEST filtered by 'None' -> None -> 0; no pending/withdrawn request -> age to the cancellation date; MAX on no rows -> 0.0 -> listed-price path.
Known DSL limits (documented, not exercised): a plan always carries its purchase-day plan_included alignment (base trigger), so inc_date is never None for L; the open-work-order / open-readjustment reads assume one open row per plan (LATEST picks the latest date); R's expiration-anchor tier needs an expiration_date, which every month-based plan has (lifetime plans are outside the renewal scope).
Zero division: only J divides, by P('parts_warranty_miles') = 12000 for every tier.
- Card realism fix (T1): the 2026-02-10 purchase carries deferred_6 so the late paid statement accrues no interest row;
  T1 rebuilt, values unchanged (J 16.25, R 112.59).

## Final gate block (difficulty-wide, 2026-10-14 session)
- check_extended: EXTENDED OK
- check_task_tools: TASK TOOL CONTRACT OK
- replay_tasks: REPLAY OK (0.json 20 acts closure 30/30; 1.json 14 acts closure 22/22)
- check_solvability: SOLVABILITY OK (0.json 4 calls / 12 base gates; 1.json 2 calls / 5 base gates)
- check_compute: COMPUTE OK (suite means branches 55.50, steps 17.00; history_rows_max 13; branches_max 71)
- check_grounding: GROUNDING OK
- check_cache_diff: CACHE-DIFF INFO (no cache trap designed)
- check_cross_fire: SCOPE OK
- check_traceability: NOT OK only on unlock tool names (0.json 4, 1.json 2) — expected until the KB is rendered;
  no id/value miss.
- erlbench validate substrings: none of the forbidden clock/random/uuid substrings in task_tools.py; the ticket-number
  helper is a class static method (_TicketNumbers.build); every rw=write tool calls ctx.create/ctx.update itself.
- Scratch /tmp/alignment_plan_service_0062/ (seed/build/probe scripts) deleted after the final run.

## Coverage closure
task 0 = {open_visit_labor, open_visit_parts, cancellation_settlement, household_enrollment} with tools
{price_alignment_work_order_228c355b, price_work_order_parts_2c1ce050, confirm_alignment_cancellation_b0865de9,
enroll_household_alignment_plan_f0fe3800}; task 1 = {readjustment_parts, term_renewal} with tools
{price_alignment_readjustment_e00d4c5e, renew_alignment_plan_418ab11e}. Pairwise disjoint; all 6 policies covered.

## Open realism notes for the audit
- The product carries only five distinct numeric decisions, so purchase pricing appears twice (household enrollment
  for a second vehicle vs renewal of an expired month-based plan) — different programs, anchors and factor sets.
- Several schedules are this charter's own refinements (household rates, processing fee, package forfeit, kit price
  reference, slip share, readjustment-day credit), each declared through a scoped overwrite of the base sentence.
- Work orders / readjustments are posted by the store with basis none and priced by the plan desk (stated in L, Pp, J).

## Rework round 2 (audit audits/policy_task/alignment_plan_service/: task0 SOURCE-FACTOR RED, task1 PASS, charter F1-F7)
Plan (item -> change):
- F1 labor member_pricing_path tier 2 (readjusted-latest-included -> early price) struck; new method tiers: (1) pending
  cancellation request -> standard labor; (2) lifetime plan -> sliding member price (early price x months left to the
  interval / interval months; 0 when reached); (3) month-based plan -> interval test (0 / flat early price).
  alignment_type_share kept; new parameter advance_booking_credit (booking row lead time) -> labor 6 factors.
- F2 parts visit_basis_parts_rate struck with the Pp<-L edge and its sentence; parts factors: purchase_kit_reference
  (M: lower-of / split-the-increase / listed), kit_installation_labor, new_set_parts_rate (tires), cardholder_parts_rate.
- F3 refund request_age_anchor: tiers now turn on whether the pending request was registered within request_hold_days
  (and a withdrawn request) -> every tier reachable; the anchor selects the processing fee among plain fee readings
  (no factor reads another factor). F4 protection_package_forfeit removed; mileage_usage_fee added; refund 5 factors.
- F5 loyalty_count_window removed (count is a plain trailing-24-month binding); household method = protection credit
  computation (per covered tire / flat / none); new parameter household_service_currency.
- F6 single services scoped out of the labor policy (base single-service rule untouched). F7 card windows in labor and
  readjustment rules now run "up to the plan desk's pricing/booking" (= handling day, as compute).
- Factor-independence class sweep: refund fee read the anchor's output; renewal rate read grace output; readjustment
  slip read the warranty factor's src_date; refund type share read the tire factor's t_install -> shared reads moved to
  plain bindings, method outputs consumed only by plain/result bindings. T1 values must stay 16.25 / 112.59.
- O1 kit lock above list removed (tier 1 now lower-of). O7 recalibration work orders scoped out of the parts policy.
  Persona dates (Friday request, Sunday pothole) fixed; expired single service PB0 removed (no purchase-day row).
- Draw reassignment for task 0 (multiset unchanged {5,6,4,5}): labor 6, refund 5, household 5, parts 4.

### Round-2 results
New task-0 figures (handling-time recompute): labor 49.19 (all-baseline 59.99; per factor 13.19 / 68.99 / 57.99 / 64.19 / 59.19 / 54.19),
parts 51.29 (39.99; 55.57 / 29.92 / 56.99 / 53.99), refund 33.02 (0.00; 0.00 / 22.02 / 28.02 / 28.02 / 40.52),
household 157.49 (224.99; 177.49 / 169.99 / 167.49 / 172.49 / 167.49). Skips: refund w/o labor 82.21, w/o parts 44.32;
household w/o cancellation 157.49 (state gate). Labor/parts commute: parts-first replay gives parts 51.29, labor 49.19,
identical terminal state. Task 1 unchanged: 16.25 / 112.59 and every factor baseline identical (re-verified by recompute).
Factor-independence check (scripted, transitive over plain bindings): 0 violations in all six policies.

### Method factors — pairwise tier tables (one distinguishing input per pair; every tier reachable)
| policy | tiers | pair -> distinguishing input |
|---|---|---|
| labor member_pricing_path | T1 pending request: standard labor 109.99 / T2 lifetime plan: sliding early x (6-m)/6, 0 if reached / T3 month plan: flat early, 0 if reached | T1-T2 interval reached: 109.99 vs 0; T2-T3 m=3: 29.995 vs 59.99; T1-T3 not reached: 109.99 vs 59.99 |
| parts purchase_kit_reference | T1 <=90 d: min(listed, kit) / T2 91-365 d: listed - half excess / T3 listed | listed 39.99, kit 34.99: 34.99 / 37.49 / 39.99 (every pair differs) |
| refund request_age_anchor | T1 pending <=7 d + withdrawn: age to withdrawn date / T2 pending <=7 d: age to pending date / T3 pending >7 d: age to cancellation | withdrawn day 8 vs pending day 17: fee 0 vs 10; pending day 17 vs cancellation day 22: 10 vs 20 |
| household protection_credit_basis | T1 Plus/LoT: 5.00 x covered tires / T2 other active cert: flat 10.00 / T3 none: 0 | 4 covered tires: 20 / 10 / 0 |
| renewal grace_period_anchor | T1 last included in final 6 m: months test from it / T2 only early-price there: months test from it / T3 days test from expiry | expiry 56 d back, alignment 2 m back: in (T1/T2) vs out (T3); included 8 m vs early 5 m back: T1 out, T2 in |
| readjustment parts_warranty_path | free / prorated by miles / listed | 129.99 listed, 2670 mi: 0.00 / 28.92 / 129.99 |

### Edge-probe table (round 2; decoys inserted FIRST so first-match reads would hit them)
| task | probe | result | verdict |
|---|---|---|---|
| T0 | baseline world | open_visit_labor=49.19 (gold 49.19); open_visit_parts=51.29 (gold 51.29); cancellation_settlement=33.02 (gold 33.02); household_enrollment=157.49 (gold 157.49) | as the rule states |
| T0 | closed card account listed first | open_visit_labor=49.19 (gold 49.19); open_visit_parts=51.29 (gold 51.29); cancellation_settlement=33.02 (gold 33.02); household_enrollment=157.49 (gold 157.49) | as the rule states |
| T0 | ordered tire set on the Civic listed first | open_visit_labor=49.19 (gold 49.19); open_visit_parts=51.29 (gold 51.29); cancellation_settlement=33.02 (gold 33.02) | as the rule states |
| T0 | expired certificate on the Civic listed first | open_visit_labor=49.19 (gold 49.19); open_visit_parts=51.29 (gold 51.29); cancellation_settlement=33.02 (gold 33.02); household_enrollment=157.49 (gold 157.49) | as the rule states |
| T0 | booking for another date (2026-10-20) made 2026-10-13 | open_visit_labor=49.19 (gold 49.19) | as the rule states |
| T0 | reschedule: second booking for 2026-10-14 made 2026-10-13 | open_visit_labor=52.19 (gold 49.19) | as the rule states |
| T0 | no booking for the visit (walk-in) | open_visit_labor=54.19 (gold 49.19) | as the rule states |
| T0 | withdrawn request 2026-09-30 + pending (method T1) | open_visit_labor=49.19 (gold 49.19); cancellation_settlement=38.02 (gold 33.02) | as the rule states |
| T0 | pending registered 2026-10-05 (9 days, method T3) | cancellation_settlement=28.02 (gold 33.02) | as the rule states |
| T0 | Plus certificate (household per-tire tier) | household_enrollment=147.49 (gold 157.49) | as the rule states |
| T0 | no active certificate | open_visit_labor=59.19 (gold 49.19); household_enrollment=167.49 (gold 157.49) | as the rule states |
| T0 | late fee inside 12 months | open_visit_labor=53.59 (gold 49.19); open_visit_parts=52.91 (gold 51.29); cancellation_settlement=30.52 (gold 33.02); household_enrollment=164.99 (gold 157.49) | as the rule states |
| T0 | no active tire set | open_visit_labor=64.19 (gold 49.19); open_visit_parts=56.99 (gold 51.29); cancellation_settlement=0.0 (gold 33.02) | as the rule states |
| T1 | baseline world | readjustment_parts=16.25 (gold 16.25); term_renewal=112.59 (gold 112.59) | as the rule states |
| T1 | closed card listed first | readjustment_parts=16.25 (gold 16.25); term_renewal=112.59 (gold 112.59) | as the rule states |
| T1 | expired plan with only 4 included alignments | term_renewal=123.59 (gold 112.59) | as the rule states |
Absent-record cases: no card -> cardholder tiers fall through (0 / share 1.00); no active tire set -> 9999 days -> credits/rates 0, tire-day value = used_alignment_deduction; no certificate -> impact credit 0, protection credit none; no booking for the visit date -> booking credit 0; no withdrawn request -> anchor tiers T2/T3 only; MAX on no purchase-visit parts -> 0.0 -> listed path; household latest included missing -> 9999 months -> 0.
None/zero-division/date edges: only the labor sliding scale and readjustment proration divide, by min_interval_months (6 on every plan tier reaching T2) and parts_warranty_miles (12000); the interval anchor always exists (base trigger posts the purchase-day plan_included alignment); MONTHS uses the same-day convention throughout.

### Item-by-item closure (audit round 1)
- F1 closed: member_pricing_path tier 2 replaced by the lifetime sliding scale; no tier forfeits included alignments; the method is genuine (pairwise table above).
- F2 closed: visit_basis_parts_rate removed with the parts<-labor edge and its sentence; parts keeps 4 factors (new_set_parts_rate added).
- F3 closed: request_age_anchor tiers turn on the request's hold time and a withdrawn request; every tier reachable (probe rows T1, T3).
- F4 closed: protection_package_forfeit removed; plan_mileage_usage_charge added.
- F5 closed: loyalty_count_window removed; the loyalty count is a fixed trailing-24-month COUNT read only by the loyalty factor (no window tiers); household method is protection_credit_basis.
- F6 closed: single services stated as outside the labor policy (base single-service rule untouched); compute no longer special-cases them.
- F7 closed (class): labor and readjustment card windows now "up to the plan desk's pricing / booking of the readjustment"; parts/refund/household/renewal already NOW in rule and compute.
- O1 closed: kit tier 1 is now lower-of (no billing above list). O2 moot (F3). O3 recorded: commercial-use early alignments as interval anchors remain a base-level latent gap (no commercial row in either world; labor scopes commercial visits out). O4 kept (published loyalty credit). O5 recorded: booking rows now feed the labor booking credit; retirement still carries no extended policy. O6 recorded (base order sentence grounds no edge). O7 closed: recalibration work orders are outside the parts policy (base rule).
- Persona observations closed: "last Friday" (request 2026-10-09), "pothole on Sunday" (replacement 2026-10-11); expired single service without a purchase-day row removed from the seed.
- Factor-independence class (coordinator): refund fee/anchor, renewal rate/grace, readjustment slip/src_date, refund type share/t_install fixed; scripted check 0 violations.

### Final gate block (round 2)
- EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 20 acts closure 29/29; 1.json 14 acts 22/22); SOLVABILITY OK;
  COMPUTE OK (suite means branches 63.00, steps 17.00; history_rows_max 14; branches_max 85); GROUNDING OK;
  CACHE-DIFF INFO; SCOPE OK; TRACEABILITY NOT OK only on the six unlock tool names (pre-render, expected).
- Scratch /tmp/alignment_plan_service_0062/ deleted after the run.

## Rework round 3 (render_source notes 1-8; policy_kb XF / XF-S / SS-1 / SS-3; runtime CP-1)
Restructure: every factor contributes on its own. Percentage factors are taken on the computation's own baseline
quantity (labor: the pricing base, which the method decides; parts: the kit charge, which the kit method decides;
household/renewal: plan_price; readjustment: the parts amount, which the warranty method decides; refund: the processing
fee / per-alignment deduction value), credits and charges are separate amounts, and the assembly lives only in the plain
`reductions` binding and `result`, stated once per rule without naming any factor quantity ("Every reduction and credit
this policy states is worked out on its own and taken off ..."). Shares became reductions (thrust 20% / two-wheel 10%;
slip 20% / 10%). The renewal grace period no longer gates the renewal rate: grace_period_anchor now decides its own
reinstatement charge (0.00 inside grace, reinstatement_charge 20.00 outside; baseline = expiry anchor), and the renewal
rate (renewal_usage_rate) applies by included-alignment count alone. Scripted independence check: 0 violations
(bindings and baselines).
New figures: labor 46.99 (all-baseline 59.99), parts 54.74 (39.99), refund 31.77 (0.00), household 157.49 (224.99, unchanged);
readjustment 16.16 (129.99; was 16.25), renewal 112.59 (all-baseline 239.99; value unchanged). Skips: refund w/o labor 78.76,
w/o parts 46.52; renewal w/o readjustment 137.59. Labor/parts still commute (parts-first replay identical).

### Probe table (round 3, touched reads)
| task | probe | result | verdict |
|---|---|---|---|
| T0 | baseline world | open_visit_labor=46.99 (gold 46.99); cancellation_settlement=31.77 (gold 31.77); household_enrollment=157.49 (gold 157.49) | as the rule states |
| T0 | withdrawn request registered AFTER the pending one (2026-10-10): not "on or before" | cancellation_settlement=31.77 (gold 31.77) | as the rule states |
| T0 | withdrawn request 2026-09-30, before the pending one (T1) | cancellation_settlement=36.77 (gold 31.77) | as the rule states |
| T0 | second plan_included four-wheel alignment on the tire install day | cancellation_settlement=0.0 (gold 31.77) | as the rule states |
| T0 | customer holds Plus 36 (4 tires) and Life-of-Tread (2 tires) | household_enrollment=147.49 (gold 157.49) | as the rule states |
| T1 | baseline world | readjustment_parts=16.16 (gold 16.16); term_renewal=112.59 (gold 112.59) | as the rule states |
| T1 | readjustment 50 days after the corrected alignment (slip 20%) | readjustment_parts=13.27 (gold 16.16) | as the rule states |
| T1 | last included 2026-01-10 (outside final stretch), no early there: expiry anchor, reinstatement 20.00 | term_renewal=132.59 (gold 112.59) | as the rule states |
| T1 | only a member-early-price alignment in the final stretch (T2) | term_renewal=112.59 (gold 112.59) | as the rule states |
| T0 | four-wheel open work order (type reduction 0) [fixed selector] | open_visit_labor=68.99 (gold 46.99) | as the rule states |

### Closure by item id
- Note 1 / SS-1 closed: labor and readjustment replaced_by now restate the in-force remainder in full (purchase-day and
  non-open alignments: included at 0.00 when the interval is reached, member early price before it with the restart rule;
  other readjustments: free labor, parts charged under the parts warranty only when the part itself failed within the
  warranty months/miles). Parts and household/renewal overwrites were already self-sufficient.
- Note 2 / XF-i, XF-j, XF-k closed: grace no longer gates the renewal rate (reinstatement charge); card renewal reduction is
  a percentage of plan_price, not "added to the renewal rate".
- Note 3 / XF-a..h, XF-l closed: no rule sentence orders one factor after another or names another factor's quantity;
  assembly stated once generically; XF-f closed (installation labor is "charged on the work order as part of the parts
  charge", the kit method decides the "kit charge" defined in the baseline).
- XF-S closed: readjustment replaced_by no longer points at the warranty factor; renewal replaced_by no longer points at
  the renewal tire bundle ("in place of the tire bundle price").
- Note 4 closed: protection credit counts the Plus 36-Month certificate's tires when both kinds are held (rule = compute;
  probe row). Several certificates of the same kind remain a DSL first-match limit (one per covered set in practice).
- Note 5 closed: the withdrawn request must be registered on or before the pending request's registration day (rule and
  compute; probe: a later withdrawn request leaves tier T2).
- Note 6 closed: tire-day deductions use per-type counts (n_td_thrust / n_td_two), so each deducted alignment takes its
  own type share (probe: second four-wheel tire-day alignment).
- Note 7 closed: readjustment baseline.params is [] (the baseline paragraph reads no parameter).
- Note 8 closed: refund_amount docstring no longer contradicts itself ("never negative and 0.00 when the refund works out
  to nothing", in the entry format USD, 2 decimal places, positive).
- SS-3 closed: task 0 closure text no longer mentions a single service (the Civic's only holding is the 3-Year plan).
- SS-4 kept (base law, as instructed).
- CP-1 kept: tires.yaml states alignment_check_included true for Crestline Grand Touring 60K and Crestline Highway
  Terrain LT 65K (the tires charter's own parameter), so the cross-product condition stays as written.
- Method factors kept (member_pricing_path, purchase_kit_reference, request_age_anchor, protection_credit_basis,
  grace_period_anchor, parts_warranty_path); draw, 4-6 factor floor and both trees unchanged.

### Final gate block (round 3)
- EXTENDED OK; TASK TOOL CONTRACT OK; REPLAY OK (0.json 20 acts 29/29; 1.json 14 acts 22/22); SOLVABILITY OK;
  COMPUTE OK (suite means branches 64.00, steps 17.00; history_rows_max 14; branches_max 85); GROUNDING OK;
  CACHE-DIFF INFO; SCOPE OK; TRACEABILITY OK (0.json copied 31 missing 0; 1.json copied 19 missing 0 — against the
  round-2 published KB; the docs must be re-rendered for the changed rules).
- Scratch /tmp/alignment_plan_service_0062/ deleted.
