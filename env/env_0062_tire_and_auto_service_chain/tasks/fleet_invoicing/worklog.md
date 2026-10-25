# worklog fleet_invoicing (env_0062, M=2)

## Step 0 draw (draw_counts.py --tasks 2)
- task 0: prerequisite_problems=1, factor_counts=[6,4]
- task 1: prerequisite_problems=3, factor_counts=[5,4,5,4]

## Difficulty pre-check (base fleet.yaml)
- Computable fleet quantities in the DSL: credit memo / early-pay / late charge / dispute amounts; nested
  category_discount_pct cannot be read by P() (dict) -> mirrored scalar K constants where a program discount is needed.
- Holding = fleet account; history primitives auto-scoped to fleet_account_id; per-invoice object located
  through a pointer binding (LATEST(...fleet_txn_id...)) used as an eq filter.
- User-owned writes available: dispute filing (intake fleet_invoice_disputes, the business's own claim).
- Base gates: fleet_evt_credit_memo.within_dispute_window (time), fleet_evt_payment.within_early_pay_period (time),
  fleet_evt_late_charge.one_charge_per_month (dedup).

## Plan (claimed scopes)
- T0 (Commercial, per_invoice): root fleet_ext_early_pay_credit (agent, 6) <- fleet_ext_overlimit_dispute (user, 4).
  Business short-paid an over-limit tire ticket inside the early-pay period, withholding the unapproved excess;
  discount earned on the undisputed part once the dispute stands.
- T1 (Commercial, per_invoice, month-end 2026-09-30): root fleet_ext_month_end_late_charge (agent, 4) <-
  fleet_ext_alignment_reprice (agent, 5), fleet_ext_tire_discount_restore (agent, 5), fleet_ext_trip_fee_dispute (user, 4).

## Task 0 (closed)
- Policies: fleet_ext_overlimit_dispute (user, 4 factors: ticket_measure[method], safety_work_allowance,
  weekend_ticket_allowance, repeat_unapproved_deductible) -> fleet_ext_early_pay_credit (agent root, 6 factors:
  remit_speed_points[multi-source], approval_tenure_points, tire_program_bookings[cross tires], invoiced_volume_points,
  remit_channel_points, disputed_invoice_base[method]).
- Tools: file_fleet_overlimit_dispute_8d937b85 (user), credit_fleet_early_pay_23cbfed3 (agent).
- Expected: disputed 156.29 (all-baseline 214.41), early-pay 17.78 (all-baseline 9.64); skip filing -> 0.
- Revisions: volume factor decorative (17,122.99) -> +3 invoices -> 21,106.34. Empty FK '' -> null. Closure mismatch
  (63 unread rows) -> added reads: full roster, vehicles, stores, tire sets, alignment plans/events.
- Gates (--task 0): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (126/126 closure), SOLVABILITY OK, COMPUTE OK
  (fact 10, xfac 1, hist 71, brch 25), GROUNDING OK, SCOPE OK.
- Probe table (T0): latest-remittance tie -> none seeded; other-reason open dispute on same invoice -> counted by rule
  wording; absent remittance -> pointer empty, no discount; removed vehicle -> whole-invoice tier (unit 4108 decoy);
  0% program -> rate 0; late charge exactly 12 whole months old -> excluded (near-miss); 2025-09-12 booking excluded;
  2025-08-21 dispute 13 months old excluded; missing_po dispute other reason excluded.

## Resume note (round 1, after account cut ~21:34)
- On disk: all 6 policies in fleet.extended.yaml, 6 tools in task_tools.py (TASK TOOL CONTRACT OK, 6 tools).
- Re-ran task-0 gates after yaml/tools growth: EXTENDED OK (6 policies), COMPUTE OK, REPLAY OK, SOLVABILITY OK.
- Factor-id substring check against all 6 tool names: clean.

## Task 1 design (claimed)
- Root fleet_ext_month_end_late_charge (agent, 4 factors: seasoned_account_tiering[method, multi-source],
  utilization_rate_adjust, closing_remittance_relief, invoiced_volume_rate_adjust), oldest-first past-due basis.
- Prereqs (all value_input, state form): fleet_ext_tire_discount_restore (agent, 5: ticket_promotion_method[method,
  cross tires], tire_volume_pricing, same_day_fleet_pricing, commercial_lt_program_pricing[cross hazard],
  late_record_standing); fleet_ext_brake_discount_restore (agent, 5: brake_line_scope[method], brake_volume_pricing,
  brake_axle_points, brake_fleet_size_pricing, brake_tenure_pricing); fleet_ext_trip_fee_dispute (user, 4:
  visit_size_schedule[method], weekend_visit_surcharge, visit_tire_install_credit[cross tires], visit_route_credit).
- Draw [5,4,5,4]: tire 5, brake 5, trip 4, late charge 4.
- Known compromise: brake_line_scope's Severe-Duty "net-priced pad sets" tier is a Crestline fleet price-list rule
  stated in the extended rule (no base sentence); historical correctly-posted invoices follow the base discount.

## Task 1 (closed)
- Expected: tire correction 49.87 (all-baseline 85.79), brake correction 92.99 (107.99), trip-fee dispute 16.50
  (0.00), late charge 2026-09 15.43 (36.45). Edge skips: 15.66 / 15.85 / 15.51.
- Revisions: invoiced-volume adjustment decorative (20,618.42) -> +5 paid invoices -> 30,392.92; seed enum fixes
  (tire_events.tire_position ALL, hazard_events.tire_position none; same fix re-applied to task 0, task 0 rebuilt and
  regated); adjustment-credit XSUM detached from ticket_promotion_method bindings (no adjustment rows seeded, the
  tier is a stated branch only); late charges in history kept at the 5.00 minimum so base and extended rules agree.
- Dedup gate binding for statement_month cites a null field of the 2026-04 late-charge row (the checker has no
  frozen_time binding source); evidence also lists frozen_time and both earlier statement months.
- Probe table (T1): two undiscounted tire invoices -> latest corrected; removed van excluded from fleet size; absent
  certificate -> 0.00 deduction (EXISTS guard); absent axle -> zero labor/rotor for it; same-day count is invoices;
  past-due floored at 0.00 before the minimum; earlier visit fees (3 vans, weekday) owed the program fee.

## Final gate block (difficulty-wide)
EXTENDED OK | TASK TOOL CONTRACT OK (6 tools) | REPLAY OK (0: 126/126, 1: 179/179) | SOLVABILITY OK |
COMPUTE OK (suite means branches=64.00 steps=18.50; history_rows_max=131; branches_max=103) | GROUNDING OK |
CACHE-DIFF INFO | SCOPE OK | TRACEABILITY NOT OK: only the 6 unlock tool_name misses (docs not yet published).

## Known realism risks for the audit
- Several factor ladders are Crestline schedules stated only in the extended rules (point adders, late-charge rate
  adjustments, visit fee schedule, Severe-Duty net-priced pads); values are carried in policy params.
- Program category discounts are mirrored as K constants (P() cannot index the nested category_discount_pct).
- Pointers rely on recency scopes stated in the rules (latest remittance's invoice, latest undiscounted tire/brake
  invoice, latest visit fee invoice).

## Round 2 rework plan (audit round 1: task0 F-1 RED, task1 F-2 RED)
- F-1 class: overlimit allowances -> declared, scoped overwrite of the fleet_evt_invoice approval sentence (driver
  emergency authorization basis); tire "do not combine" and brake "net-priced pads" tiers removed (F-2 below).
- F-2 class: tire/brake corrections rebuilt: baseline = exactly what correct posting gives (program category discount
  on the pre-tax price net of excluded items, stacking with instant savings as tires_purchase_ticket prices the
  ticket); every factor is a declared billing-error make-good on top (never below posting) -> O-11 closed too.
- Factor counts T1 re-split to [late 5, trip 5, tire 4, brake 4] (draw multiset unchanged).
- Factor independence: overlimit method no longer subtracts the authorized amount; late-charge method decides an
  effective balance, not a charge; remit_days made a plain binding.
- O-1 rule says invoices; O-2 tax-exempt scope computed; O-3 wording + lookback stated; O-4 roster count wording;
  O-6 basis quote; O-7 sentences scoped to "the most recent ... invoice"; O-8 deducted-discount remittance accepted;
  O-14 wording "road hazard certificates"; O-T1-1 / O-11 seeds: every tire invoice rebuilt from its tire set.

## Round 2 closure (round-1 sections above are history; figures there are superseded)
New gold: T0 dispute 156.29 / early-pay 17.78 (unchanged). T1 tire 229.29 (baseline 85.79 = correct posting),
brake 153.99 (baseline 107.99 = correct posting), trip dispute 19.00, late charge 12.75 (skips 13.66 / 13.36 / 12.82).

Item-by-item:
- F-1 closed: overlimit overwrite declares the fleet_evt_invoice approval sentence, scoped to disputed tickets, with the
  driver emergency authorization basis; class members (b)(c) removed with F-2.
- F-2 closed: tire/brake corrections = correct-posting discount + declared billing-error make-good (never below posting);
  "do not combine" and "net-priced Severe-Duty pads" tiers deleted; each keeps a genuine method (make-good line shape).
- O-1 rule states visit size in invoices. O-2 tax-exempt scope computed (taxed -> 0, base governs). O-3 "oldest first"
  dropped, twenty-year lookback stated. O-4 roster wording = enrollments beyond removals. O-5 not changed (no half-cent
  tie in either world; documented). O-6 basis quote now verbatim. O-7 sentences name the most recent invoice on a
  tax-exempt account, same object the corrections fix. O-8 deducted-discount remittance passes the test. O-9 pattern
  kept (baseline-in-rule). O-10 brake cross reads remain non-factor. O-11 closed with F-2 (points removed). O-12/O-13
  unchanged (observations). O-14 wording "road hazard certificates". O-T0-1/2/3 unchanged (persona notes).
  O-T1-1 closed: every tire invoice in both worlds rebuilt from its tire set; missing sets/invoices added.

Pairwise method tier tables (one distinguishing input per pair):
- ticket_measure: split|single-with-credits = same-day same-store invoice count; single-with-credits|plain = credit
  memos on the invoice; split|plain = count.
- disputed_invoice_base: >half|some = disputed share; some|none = open dispute rows; >half|none = rows.
- visit_size_schedule: waived|sliding = invoices >= 2x minimum; sliding|flat = invoices > minimum; waived|flat = count.
- tire_makegood_line: full|partial = tire_count >= 4; partial|none = set on the ticket; full|none = set.
- brake_makegood_line_method: both|one = axles with jobs 2 vs 1; one|none = 1 vs 0; both|none = 2 vs 0.
- seasoned_account_tiering: seasoned|new-clean = approval months; new-clean|whole = late-charge count; seasoned|whole
  = approval months.
Factor independence: mechanical transitive check over all 28 factors -> no factor binding reads another factor's binding.

Probe table (round 2): see each task's design_rationale EDGE PROBES; added: taxed account -> 0.00 (base governs);
no tire set on a tire invoice -> line nothing, disposal 0; no brake job -> supplies 0, line nothing; non-applicable
brake line -> restored 0; today's brake correction does not enter the tire repeat-error count (before-today filter).

Gates (difficulty-wide): EXTENDED OK | TASK TOOL CONTRACT OK | REPLAY OK (0: 136/136, 1: 182/182) | SOLVABILITY OK |
COMPUTE OK (branches mean 58.50, steps 18.50, history max 134, branches max 91) | GROUNDING OK | CACHE-DIFF INFO |
SCOPE OK | TRACEABILITY NOT OK (6 unlock tool_name misses only, pre-render).

## Round 3 closure (render_source/fleet/notes.md, policy_kb/fleet_invoicing/{0,1}.md, runtime_context/fleet_invoicing/{0,1}.md)
Values unchanged: T0 156.29 / 17.78; T1 229.29 / 153.99 / 19.00 / 12.75; late-charge skips re-run by replay 13.66 / 13.36 / 12.82.
- R1 (early-pay rule restated a retired clause): the rule now states the paid-in-full test and "rate in percent applied once to the
  discount base"; the base percent-of-invoice clause is no longer restated as law. Rate and base defaults in one plain sentence.
- R2 (early-pay overwrite[0] narrower, no remainder): replaced_by = the full paid-in-full sentence + "every other invoice remains under the
  base rule"; same pattern on every overwrite (over-limit, trip, tire, brake, late charge).
- R3 (ACH/WIRE + CHK undefined): channel ladder "ACH or WIRE, whether or not it also carries CHK" / "CHK and neither ACH nor WIRE" / none.
- R4 (visit-fee vehicle count): rule defines vehicles served as invoices dated the visit day from the crew's store other than visit fee
  invoices (= compute).
- R5 (tire booking counts count reschedules): early-pay tire factor now counts tire rotations (tire_care_rotation_points; T0 seeded
  rotations 2026-04-14, 2026-09-02 + existing 2026-08-11 -> 3 -> 0.10, unchanged; 2025-10-14 near-miss). Trip tire credit now counts tire
  invoices dated the visit day from the crew's store (visit_tire_work_credit; T1 four -> 10.00, unchanged). No booking count remains.
- R6 / KB N3 (late-charge "twenty years" and month-end windows): every date test counts from "the day the charge is assessed" (= compute
  NOW); due-date horizon stated as 240 whole months; prerequisite sentences say "past due on the day the charge is assessed".
- KB N1 (forward pointers / factor names on base surfaces): no "described/set out below" or factor naming in any replaced_by; trip
  docstring now "contesting part of the amount charged on a mobile service visit fee invoice" (no schedule).
- Assembly sentences: no sentence names several factor quantities; each component sentence says "is added to the early-pay rate /
  authorized amount / correction / late-charge rate" or "taken off the fee owed / unapproved part"; the totals live in plain bindings.
- KB N2: base-layer tension (payment_application_order vs "held unapplied") left as instructed. C1 is the tires corpus, not this difficulty.
- Stale proof sweep: task 0 over-limit quote, tier_taken texts (rotations, channel, late-charge windows), tracing necessities,
  prerequisite quotes and design_rationale ROUND-3 notes updated.
Factor independence (mechanical transitive check, 28 factors): no factor binding reads another's. No factor id is a substring of a tool name.
Probes (round 3, handling-time world): T0 near-miss rotation moved inside -> 4, same tier 17.78; one rotation dropped -> 16.97; +3 -> 18.99;
all bookings moved inside window (decoy) -> 17.78; reference ACH+CHK -> 17.78, CHK only -> 13.74, none -> 15.76. T1 one visit-day tire invoice
recategorized -> 14.00; three -> 9.00; one from another store (vehicles and tire count both drop) -> 2.00.
Gates: EXTENDED OK | TASK TOOL CONTRACT OK | REPLAY OK (0: 139/139, 1: 182/182) | SOLVABILITY OK | COMPUTE OK (branches mean 58.00,
steps 18.50, history max 134, branches max 90) | GROUNDING OK | CACHE-DIFF INFO | SCOPE OK | TRACEABILITY OK.
REWORK round 3: gates 7/7 green

## Round 4 closure (render_source/fleet/notes.md, "round 2" items)
Values unchanged (no compute edit): T0 156.29 / 17.78; T1 229.29 / 153.99 / 19.00 / 12.75; skips 13.66 / 13.36 / 12.82.
- Item 1 (tire/brake "never less than" vs the ceiling): the replaced_by and rule now say the correction is "at least the fleet discount ...
  less the discount the invoice already carried, except that it never exceeds the invoice amount less the credit memos and early-pay
  discounts already on the invoice, that limit prevailing". The make-good sentence says the limit is applied last, after every make-good
  amount, prevails over every other part, the correction can fall below the restored discount only when that limit is lower, and it is
  rounded once after the limit (= RND(MN(room, restored + make-good), 2)). Both policies.
  Class sweep over the six policies:
  - over-limit "never below 0.00 and never more than the invoice amount": the two bounds cannot conflict (0 <= invoice amount).
  - trip fee owed and amount in dispute: floors only.
  - early-pay: no floor or cap; the lowest rate is 1.00 - 0.25 > 0.
  - late charge: "pct 0 charges nothing" vs "never less than late_charge_min" made explicit: "... and this prevails over
    late_charge_min" (= compute 0 when the rate is 0). An adjusted rate is never <= 0 on a program with pct > 0 (lowest 1.00 - 0.80).
- Item 2 (early-pay baseline.rule split): the prerequisite sentence now follows the baseline sentences; baseline.rule is a contiguous
  passage of the rule (all six policies contiguous).
- Item 3 (base N2): base layer, left.
- Stale proof sweep: T1 tracing/factor texts "credit room" -> "the invoice limit applied last"; every quoted rule phrase in both tasks
  re-checked against the yaml.
Probes (T1, handling-time world, limit lowered by a probe memo): tire limit 150.00 -> 150.00, limit 60.00 (below restored 85.79) -> 60.00;
brake limit 120.00 -> 120.00, limit 50.00 (below restored 107.99) -> 50.00. As is: 229.29 / 153.99.
Gates: EXTENDED OK | TASK TOOL CONTRACT OK | REPLAY OK (0: 139/139, 1: 182/182) | SOLVABILITY OK | COMPUTE OK | GROUNDING OK |
CACHE-DIFF INFO | SCOPE OK | TRACEABILITY OK (0: 19/0, 1: 27/0).
REWORK round 4: gates 7/7 green
