# worklog — prepaid_service_hours (timebank), M=2

- draws: task 0 prereq=2 factors [4,4,5]; task 1 prereq=3 factors [5,5,5,6]
- task 0 closed: root timebank_ext_repeat_order_quote (user, 5) <- timebank_ext_visit_draw_correction (4), timebank_ext_visit_travel_entry (4); per-task gates 7/7 OK (extended, task_tools, replay, solvability, compute, grounding, cross_fire); gold 5.11 h / 0.27 h / 2938.80 USD.
- task 1 closed: root timebank_ext_extension_quote (user, 6) <- timebank_ext_remote_session_draw (5), timebank_ext_install_visit_draw (5), timebank_ext_project_time_draw (5); gold 1.18 h / 6.47 h / 4.92 h / 322.72 USD; edge skips 328.44 / 354.09 / 346.57.
- XF sweep (scratch): compute_basis quotes and baseline sentences verbatim in their rules; no factor reads another factor's bindings; no factor id inside a tool name; decoy probe (closed ClearPath Enterprise agreement, cancelled Sentinel XDR, shipped endpoint order, cancelled Strategic Program engagement added on a scratch copy) leaves all seven figures unchanged; task_tools.py free of datetime/time/random/uuid/secrets and every write tool writes in its own body (erlbench validate tool lint clean).
- final full gates: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK (suite branches mean 87.00, steps mean 16.50, history max 21, branches max 106), GROUNDING OK, SCOPE OK.
INSTANTIATE round 1: gates 7/7 green

## round 2
- Tree changes:
  - task 0: root timebank_ext_repeat_order_quote (5) <- timebank_ext_service_visit_draw (4), timebank_ext_visit_travel_entry (4); travel <- service visit. Gold: 2.82 h, 0.27 h, 2938.80.
  - task 1: root timebank_ext_extension_quote (6) <- remote (5), install (5), project (5). Gold: 2.36 h, 6.47 h, 5.08 h, 312.83; new expiry 2027-06-08.
- Draws are unchanged: task 0 [4,4,5], prereq 2; task 1 [5,5,5,6], prereq 3.

### XF23 method tiers, all pairs (T1/T2/T3; "nothing" means no change)
| factor | T1 vs T2 | T1 vs T3 | T2 vs T3 |
|---|---|---|---|
| tenure_scale | T1 adds full years since go-live, x and a cap; T2 is a gated constant | T3 nothing; T1 is nonzero from year 1 | T3 nothing; T2 = 2.0, never 0 |
| trip_value_basis | T1 zero (nothing) vs T2 charge / hourly_rate (2 inputs, division) | T3 onsite_trip_hours; not 0 on every size (20h 1.0, 40/80h 0.5) | T2 adds the charge input and a division; no cap, so 85/150 = 0.57 differs from 0.5 on 40/80h (F-A3 closed) |
| service_callout_basis | min() split with the emergency/after-hours ratio vs a max() floor of 120 | T3 nothing; the split is nonzero on a call-out | T3 nothing; the floor binds below 120 min |
| remote_callout_basis | min() split vs a weekend max() floor of 120 | T3 nothing | T3 nothing |
| install_unit_minutes | qty x 20 (order input, billable not used) vs max(billable basis, qty x 45) | different input: quantity vs billable minutes | T2 adds qty x 45 and max() |
| project_minutes_basis | max(m, 240) floor vs ceiling to the hour | T3 nothing; the floor binds below 240 | T3 nothing; the ceiling binds off the hour |
| hour_valuation_basis | invoiced / (purchased + rolled): adds the rolled-in input and an addition | T1 record division vs the size's hourly_rate | T2 record division vs the hourly_rate parameter |

### XF24 trigger rule: events the tools write, with base triggers
| tool | events written | triggered event |
|---|---|---|
| sign_repeat_block_order_5562f94d | timebank_orders intake row, timebank_block_ordered (new block) | timebank_block_invoice (timebank) |
| post_service_visit_draw_abd20ee9, post_visit_travel_entry_8d0122c7, post_remote_session_draw_4c084c45, post_install_visit_draw_14ae60a8, post_project_time_draw_e9603a55 | timebank_hours_drawn | none |
| sign_block_extension_cebc1113 | timebank_orders intake row, timebank_block_extended | timebank_extension_fee (timebank) |

No event crosses a category, and timebank_draw_reversed is no longer written.

### Probe table: first-match and LATEST reads (run in scratch on deep copies; gold unless noted)
| read | probe | result | settled by |
|---|---|---|---|
| CFIELD managed (status/tier/renewals/seats/trip charge), P1-P7 | closed ClearPath Premier agreement listed first | unchanged in both tasks | status='active' filter |
| same | no agreement | t1: remote 2.62, install 7.19, fee 417.11; t0: visit 2.97, travel 0.50, order 3033.60; no error | fall-through tiers |
| P1 seat_count | zero | 2970.40 | seat fall-through |
| P7 renewal_count | zero | 417.11 | loyalty fall-through |
| CFIELD hardware status=delivered, P2/P3/P5 | quoted 40-unit order listed first | unchanged | status filter |
| same | no order | install 0 | not an installation |
| same | delivered 15 days before opening | install 0 | the 14-day window |
| same | not rush | install 5.62 | rush fall-through |
| same | delivered order 1 day before opening, ticket not service_request (t0) | visit 2.82 | category test |
| | two delivered orders | not seeded | "the client's hardware order whose status is delivered" is a single record; each world carries exactly one |
| CFIELD project by sow / status=in_progress, P6/P7 | closed fixed-fee SOW listed first | unchanged | sow / status filter |
| same | no engagement | project 5.34, fee 347.59 | discount 0 -> 1 |
| same | rate_discount 0 | project 5.34 | discount fall-through |
| XLATEST remote resolution, P4 | business-hours remote resolution at the same 23:45 with 240 min | unchanged | after-hours wins at the same minute (>=) |
| same | second after-hours resolution, same minute, 30 min | unchanged | XMAX of billable minutes |
| XLATEST project line, P6 | second 2026-10-15 line with 60 min | unchanged | XMAX of minutes on the date |
| LATEST block invoice + payments by invoice_number, P7 | partial payment 10000 | 312.83 (late) | partial and unpaid read as late |
| same | unpaid | 312.83 (late) | as above |
| same | paid on posting day | 268.14 | standing fall-through |
| same | no invoice (None edge) | 282.25 | hourly_rate; no lateness |
| same rule, P1 (t0) | payment on another invoice number | 2970.40 | invoice match |
| same, P1 (t0) | partial 1000 | 2970.40 | tier rule |
| same, P1 (t0) | 20 days late | 2954.60 | later tier |
| same, P1 (t0) | unpaid | 2970.40 | tier rule |
| service visit level (t0) | resolved priority P3 | visit 3.56, travel 0.20 | the reprioritized-to-P1 event row still sets senior; the after-hours floor of 120 applies |

### Stale-text sweep
- Swept tasks/0.json, tasks/1.json, the charter and the tools for every round-1 figure and name: correction, Sentinel, 1.18, 322.72, 4.92, 79.14, renewal_count 2, class_rate, sessions_offset, parity, shared_day_split, "every visit"/"every routed", 5.11, 42000, 10500.
- The only hits are the dated round-2 change notes in design_rationale. sweep.py reports 0 issues (basis, baseline, replaced_by, XF1/XF7/XF26).
- Task 1 historic draws were re-seeded off exact half-cents (315, 225 and 345 min). No gold or baseline lands on a rounding tie.

### round 2 claims
- **0.1–0.5, 1.1–1.7:** both tasks rebuilt on the round-2 charter; the passing items were re-checked and still hold (replay, solvability, compute, grounding).
- **0.4 / XF D.20:** seat_count 34 = seat-change rows 30 + 2 + 1 + 1; monthly fees and payments complete; balance = the open October fee.
- **1.1 / F-B1:** the correction is removed. The service-visit draw excludes installation visits; on the task 1 world it yields 0 for SB-2310275.
- **1.2 / F-A4:** remote_clearpath_rate tiers are Professional, then Standard/Essentials/Monitor. Both reach weekday after-hours sessions.
- **1.3 / F-A7:** install_rush_rate tier 2 is one to two days after delivery (task 1 takes 1.15).
- **1.4:** rate_discount_pct 7.5 = clearpath_rate_discount_pct (Professional rank 4 >= min rank 4); contract 64000.00 within the Advanced bounds.
- **1.5:** renewal_count 4 = 36-month initial term to 2023-02-23, then four 12-month renewals; the term_months 12 term runs 2026-02-24..2027-02-23.
- **1.6:**
  - hardware_billing: deposit 4663.15 invoiced and paid; final 13989.45 = balance; quote_approval signed.
  - project_billing: deposit 16000.00 invoiced and paid, balance 0.
  - block order form and payment seeded.
  - Every seeded row is read by gold (replay closure 100/100).
- **1.7 / F-C4:** the false rationale sentence is gone. Service visits follow their own scoped rule, and P5 returns 0 for non-installation visits.
- **F-A1:** trip_value_basis is a real method (zero / charge / hourly_rate / size trip hours). The share factors are parameters.
- **F-A2 / F-A6 / F-B1 / F-C1:** the correction policy is replaced within claimed timebank events by timebank_ext_service_visit_draw (4 honest factors), with scoped overwrites of the minutes, conversion and band sentences.
- **F-A3:** the trip tier is uncapped (see the XF23 table).
- **F-A5:** shared_day_share tiers are three-or-more 0.33, two 0.5, else 1.
- **F-B2:** every prerequisite and selector sentence is single-record ("the client's ticket most recently resolved ...", "the most recently dated line ..."). No "every X" remains.
- **F-B3:** a not-yet-drawn test on every draw: COUNT by ticket (remote, installation), LATEST date = resolution date (service visit), COUNT by SOW and date (project).
- **F-B4:** ties are stated in rule and compute: after-hours beats business-hours at the same minute; XMAX minutes within a class and date.
- **F-B5:** payment standing in P1 and P7 matches payments to the block invoice's invoice_number, including partial and unpaid cases.
- **F-C2 / F-C3:** the band and minutes departures in P3–P6 are declared as scoped overwrites (superseded_clause/replaced_by verbatim; check_extended green).
- **F-C4:** P5 handles installation visits only.
- **Sentinel / security cross-read:** removed from P1 and P4, so no unbacked security ledger is read.
- **Full gate block:**
  - EXTENDED OK
  - TASK TOOL CONTRACT OK
  - REPLAY OK (0.json 16 acts 57/57, 1.json 24 acts 100/100)
  - SOLVABILITY OK
  - COMPUTE OK (branches mean 92.00, steps mean 20.00, history max 19, branches max 104)
  - GROUNDING OK
  - SCOPE OK
REWORK round 2: gates 7/7 green (superseded by round 3 below)

## round 3
- Revision_2 verdict: task0=RED[R2-0.1,R2-0.2,R2-0.3], task1=PASS, charter=N-1..N-4.
- Gold values are unchanged:
  - task 0: 2.82 / 0.27 / 2938.80; write steps moved to 12/14/16 after the new order-form read at step 5.
  - task 1: 2.36 / 6.47 / 5.08 / 312.83, new expiry 2027-06-08.
- Draws are unchanged: [4,4,5] and [5,5,5,6].

### Travel factor ladders after round 3
- trip_value_basis (method): XF23 table unchanged from round 2.
- dispatch_band_rate (parameter).
- month_trip_cap (parameter, new): travel entries on the block dated in the month counted back from today.
  - 4 or more (trip_cap_count): x 0, cap reached;
  - 2-3 (trip_taper_count to cap): x taper_share 0.5;
  - fewer: x 1.
  - Every tier is reachable on a 10-80 h size. Task 0 takes taper (2 entries: 2026-10-07, 2026-10-14) with baseline 0.54.
- return_leg_share (parameter).
- Floors: 3 parameter + 1 method.
- Trigger rule: unchanged from round 2.

### Probe table, round 3 (scratch, second record inserted first)
| read | probe | result | settled by |
|---|---|---|---|
| hardware order (P2, P3s, P5) | older 2nd delivered order (Standard, 40 units) | install 6.47 unchanged | latest delivered_date |
| same | 2nd delivered order on the same date, 3 units | 6.47 | more units on that date |
| same | 2nd order delivered later, 2026-10-14 | install 0 | stated rule: the most recent delivered order governs, and the ticket was opened before it |
| same, t0 | delivered order 2 days before opening, ticket not service_request | visit 2.82, travel 0.27 | category test |
| in-progress engagement (P7) | in-progress fixed-fee SOW listed first | fee 312.83 unchanged | XCOUNT of T&M engagements |
| project line (P6) | 2nd same-SOW same-date line (senior, 60 min) already drawn | project 5.08 unchanged; fee 306.77 (lower balance) | done test keyed on the line itself |
| same | same line not drawn | 5.08 | as above |
| same, after the gold project draw | no line figured (0) | the 2nd line stays under the base conversion, drawable | scoped overwrite |
| travel cap, t0 | 2 more travel entries in the month | travel 0.0 | cap tier |

Residual, stated in each rule: two delivered orders with the same latest date and the same units. Equal-minute ties stay as O-7.

### Stale-text sweep
- Swept tasks/0.json, tasks/1.json, the charter and the tools for: shared_day, shared-day, "share one trip", half_share, third_share, "only visit of its date", "hardware order whose status is delivered", ext_pj_model, tv_day_n, 11.42, 0.571, "for that statement of work dated that date", "is drawn at architect_ratio". No hits.
- sweep.py (basis/baseline/replaced_by/policy_source/superseded/XF26/A7): 0 issues.

### round 3 claims
- **R2-0.1 / N-1:**
  - shared_day_share is removed. It was replaced by month_trip_cap: travel entries in the month counted back from today, 4+ -> x 0, 2-3 -> x taper_share 0.5, else 1. Rule words equal compute.
  - The "share one trip" wording is gone. The edge from travel to the service visit now gates on tv_ticket_n.
  - P2 keeps 4 load-bearing factors. Task 0 baselines: 0.50 / 0.14 / 0.54 / 0.54, all 1.00.
- **R2-0.2:**
  - The signed order-form row (timebank_orders, new_block, TimeBank 20-Hour Block, 3160.00, signed 2026-05-11) is seeded, with a seed_consistency entry.
  - It is read by find_timebank_orders at step 5. Replay closure 58/58.
- **R2-0.3:**
  - edge_load_bearing for skipping the visit draw now reads 11.15 h, share 0.5575 -> 3002.00.
  - Also corrected: order_uniqueness, flips_to_true_by, the ledger-read necessity, the travel trace and tracing, the seed travel checks and the rationale.
- **N-2:**
  - Hardware reads in P2, P3s and P5 select the client's most recently delivered order (XLATEST delivered_date over status delivered). On the same date, the one with more units (XMAX quantity) is used; its type and rush flag are read from it. Each rule states this.
  - P7 counts in-progress T&M engagements (XCOUNT) instead of first-matching one.
  - ClearPath reads stay first-match. The managed charter allows at most one agreement at a time (managed_agg_multi_holding), so the active one is unique.
  - The P6 SOW read is keyed on the SOW, the engagement's business key.
- **N-3:**
  - P6's duplicate test is keyed on the line: SOW, date, level and recorded band. A sibling line's draw no longer blocks it.
  - P6 overwrites are scoped to "the line this rule figures", so every other project line keeps the base minutes, conversion and band and remains drawable.
  - Whole class: P3s, P4 and P5 overwrites are scoped to the visit or session the rule figures, with "any other ... included" in their sibling clauses. P2 travel is scoped to the visit it figures.
  - The P7 project prerequisite sentence and edge condition now name the line's SOW, date and level.
- **N-4:** every factor sentence of P2, P3s, P4, P5 and P6 now names the hours it modifies ("the block hours of ... are multiplied by / figured at", "the visit's travel hours"). P1 and P7 already named the price/percent and the fee.
- **Task 1 not regressed:** all writes, factor_sensitivity, baseline_result and edge figures are identical (2.36 / 6.47 / 5.08 / 312.83; 324.27 / 344.20 / 337.46). The closure edges were re-copied from the charter.
- **Full gate block:**
  - EXTENDED OK
  - TASK TOOL CONTRACT OK
  - REPLAY OK (0.json 17 acts 58/58, 1.json 24 acts 100/100)
  - SOLVABILITY OK
  - COMPUTE OK (branches mean 95.00, steps mean 20.50, history max 20, branches max 110)
  - GROUNDING OK
  - SCOPE OK
REWORK round 3: gates 7/7 green (superseded by round 4 below)

## round 4
- Revision_3 verdict: task0=RED[R3-0.1], task1=PASS, charter=N-6.
- Gold is unchanged:
  - task 0: 2.82 / 0.27 / 2938.80 (baselines 0.50 / 0.14 / 0.54 / 0.54, all 1.00);
  - task 1: 2.36 / 6.47 / 5.08 / 312.83, with skip effects 324.27 / 344.20 / 337.46.

### Travel rule, round 4 (one trip, one price)
- **Scope:** the overwrite covers the travel of every onsite visit drawn from a block: service and installation visits alike, resolved or open tickets. No visit keeps the flat charge.
- **The visit figured is read from the visit's own onsite-support draw, never from the ticket's resolution:**
  - among the draws on the block's latest onsite date, the one recording the most worked minutes;
  - once that one carries travel and the date has exactly one other draw, that other draw.
- **Dispatch** reads the band recorded on the visit's own draw: emergency -> emergency_multiplier; after_hours or holiday -> after_hours_multiplier; business_hours -> 1. The P2 hardware and installation reads are removed, so cross_category is now managed only.
- **Unchanged:** trip value, monthly trip cap and return schedules. The P2 -> P3s edge still gates on tv_ticket_n.

### Seeded travel rows re-priced by the round-4 rule as of each posting date (scratch, ledger cut to the posting moment)
| row | date | ticket | ticket state at posting | rule gives | seeded |
|---|---|---|---|---|---|
| ce7a1dbc | 2026-07-15 | SB-2262290 | resolved that day | 0.54 | 0.54 |
| 926ed7c7 | 2026-10-07 | SB-2306631 | still open (resolved 2026-10-14) | 0.54 | 0.54 |
| df89b1f0 | 2026-10-14 | SB-2309118 | resolved that day | 0.54 | 0.54 |

Each is 85.00/158.00 = 0.54 x dispatch 1 (business_hours draw) x 1 (fewer than 2 travel entries in the month) x 1 (first onsite draw of its ticket). Nothing else moves.

### Two-visit probe (same trip, open ticket vs resolved ticket)
- The 2026-10-07 visit on SB-2306631 with its ticket open gives 0.54. The same visit with its ticket set as resolved that day gives 0.54. The price is the same because the rule never reads the resolution.
- Out-of-order probe: a shorter second visit on 2026-10-14 (45 min, posted after the 60-minute visit already has travel) gives 0.27 (0.54 x 1 x cap taper 0.5 x 1). The date's other visit stays reachable.
- Residual, recorded as O-7: a date carrying three or more onsite visits whose longest visit already has travel. Ties on equal minutes stay as O-7.

### Overwrite sweep for the N-6 class (residue priced differently from the in-scope case for the same object)
- **P2 travel:** closed. Every onsite visit's travel is in scope and nothing is left at the flat charge.
- **P3s, P4, P5 and P6:** these overwrite only the record they figure. Every other record keeps the base conversion. The residue (an unresolved ticket's earlier draw, an unselected line) lacks the inputs the schedules read: resolution class, priority and channel, or the selected line's log. So no record can be priced both ways. This matches the revision_3 auditor's reading.
- **P1 repeat order:** covers every repeat order. Any other order is a different object, priced at the standard block price.
- **P7 extension:** covers every extension; there is no residue.
- **O-9 closed:** the P7 project sentence now names the band ("...date and level in the band the project rule records for it"). The task 1 closure edges were re-copied.

### Stale-text sweep
- Swept for: "this rule does not figure", tv_is_install, tv_delivered, the old P1/phone dispatch tier text in the travel trace, "date and level." No stale hits.
- The ticket and plain-trace quotes now match the round-4 selection sentence. sweep.py reports 0 issues.

### round 4 claims
- **N-6:**
  - P2 prices the trip of every onsite visit by one rule, keyed on the visit's own draw. The flat residue is removed, and the dispatch reads the visit draw's recorded band.
  - The two-visit probe gives open ticket 0.54 = resolved ticket 0.54. The out-of-order same-date probe is reachable (0.27).
  - The class sweep is recorded above: no other member.
- **R3-0.1:**
  - Seeded travel rows 926ed7c7, ce7a1dbc and df89b1f0 are each reproduced at 0.54 by the round-4 rule at their posting dates. Nothing moves.
  - The seed_consistency checks now state that derivation; 926ed7c7 notes that its ticket was still open.
  - Also updated: the travel trace, the factor_sensitivity tier, the tracing, the closure why_false / flips_to_true_by / order_uniqueness, and rationale section 11.
- **Task 1:** not regressed (values, edges and factors identical). O-9 wording closed.
- **Full gate block:**
  - EXTENDED OK
  - TASK TOOL CONTRACT OK
  - REPLAY OK (0.json 17 acts 58/58, 1.json 24 acts 100/100)
  - SOLVABILITY OK
  - COMPUTE OK (branches mean 90.00, steps mean 20.50, history max 22, branches max 110)
  - GROUNDING OK
  - SCOPE OK
REWORK round 4: gates 7/7 green (superseded by round 5 below)

## round 5
Revision_4 verdict: task0=PASS, task1=PASS, charter=N-6, N-7, N-8 (one class across P2, P3s, P4, P5 and P6). Closed once with the coordinator's route.

### Route applied
1. **Price = own attributes; scope = the whole kind.**
   - Each overwrite now covers every record of its kind:
     - every remote session;
     - every service visit;
     - every installation visit;
     - every block-routed T&M line whose SOW, date and level name one line;
     - every onsite visit's travel.
   - The "record this rule figures" scoping and the "any other ... included" residues are gone.
   - A ticket's remote or onsite labor is drawn once, at resolution, dated the resolution date. P3s minutes are the resolution's billable minutes; the "less earlier draws" step is removed.
   - Order-dependent factors were replaced:
     - P6 project_month_volume (read other lines' draws) -> project_class_rate (engagement class: Major/Strategic 0.9, Standard/Advanced 0.95, else 1).
     - P2 month_trip_cap and return_leg_share (read other travel and visit draws) -> travel_level_ratio (the level the visit's own draw records) and dispatch_lead_rate (same day 1.25 / next day 1.15 / else 1, from the visit date against its ticket's opening).
2. **Scope decided by fixed records.**
   - Remote, service and installation kinds are read from the ticket's own records and the hardware delivery dates.
   - P6's out-of-scope set is decided by a count of all block-routed logs on the SOW, date and level, drawn or not. Those are lines with two bands at one level that day, and they keep the restated base rule.
   - The installation test still reads the most recently delivered order within install_window_days. The compute language has no date arithmetic or string slicing, so "an order delivered on the ticket's opening date" cannot be written (tried; check_extended rejects slicing). This is the revision_4 B.14 PASS reading, now with a full tie chain.
3. **Tie chains end in a unique key, stated in each rule (N-8):**
   - remote, service and installation: later minute; after-hours over business-hours; more billable minutes; higher ticket number (a ticket is resolved once);
   - hardware order: latest delivery; more units; higher quote_number;
   - project line: latest date; more minutes; higher SOW number; higher level (unique within scope);
   - travel: latest onsite date; more worked minutes; higher ticket number (one onsite draw per ticket).
4. **Travel (N-7):** every onsite visit's trip is priced by one schedule (trip value x dispatch band x level x dispatch lead) from its own draw, its ticket and the agreement. Selection only decides which visit the compute figures.

### Worlds re-derived (every seed under the round-5 rules)
- **Task 0:**
  - Removed the interim 2026-10-07 visit and its travel on SB-2306631: the ticket's onsite labor is now drawn once at resolution.
  - SB-2306631: opened 2026-10-13 18:40 by phone, P2; reprioritized to P1 2026-10-14 18:05; resolved 20:30 with 75 billable minutes.
  - SB-2309118 now opens 2026-10-12. Added remote session SB-2303384 on 2026-10-01 (90 min, 1.50 h).
  - Balance 9.39. Seeded travel ce7a1dbc and df89b1f0 are each 0.54 under the new rule (business band, technician, ticket opened two or more days earlier).
  - Gold: visit 2.82 (baselines 2.23 / 1.88 / 2.26 / 2.97, all 1.25); travel 1.55 = 0.54 x 2.0 x 1.25 x 1.15 (baselines 2.88 / 0.78 / 1.24 / 1.35, all 1.00); order 2938.80 (usage 14.98/20 = 0.749; baselines unchanged).
  - Edges: skip travel -> 3002.00 (0.6715); skip visit -> 3002.00 (0.5305); travel without the visit -> 0.
- **Task 1:**
  - Project draws re-priced under the class rate:
    - 2026-09-14 is now 255 min (240 x 0.9025 x 1.5 = 5.415, a half-cent tie): 5.75;
    - 6.83 -> 6.49; 8.31 -> 7.90;
    - 6.77 and 5.64 unchanged.
  - Balance 79.14.
  - Gold: 2.36 / 6.47 / 5.08 / 316.23 (65.23 x 128.25 x 7% x 0.75 x 0.8 x 0.9). Baselines 383.99 / 271.05 / 332.87 / 421.63 / 395.28 / 351.36, all 660.45. Skips 327.67 / 347.59 / 340.85.
  - The P4/P5/P6 factor figures are unchanged.

### Probe table, round 5 (scratch evaluator; result -> record figured)
| policy | probe | result |
|---|---|---|
| P4 | gold | 2.36 SB-2311409 |
| P4 | 2nd session resolved earlier, undrawn | 2.36 |
| P4 | 2nd session resolved earlier, drawn first | 2.36 |
| P4 | 3rd same-date session | 2.36 |
| P4 | full tie, lower ticket number | 2.36 SB-2311409 |
| P4 | full tie, higher ticket number | 2.36 SB-2311420 (same attributes, same price) |
| P5 | gold | 6.47 |
| P5 | 2nd onsite resolution undrawn | 6.47 |
| P5 | 2nd onsite resolution drawn first | 6.47 |
| P5 | full tie, higher ticket number | 6.47 SB-2310290 |
| P5 | 2nd order same date and units, lower quote number | 6.47 |
| P5 | 2nd order same date and units, higher quote number, Standard type | 14.55 (that order governs, as stated) |
| P6 | gold | 5.08 |
| P6 | 2nd line same SOW/date (senior, 120), undrawn | 5.08 |
| P6 | same 2nd line drawn first | 5.08 |
| P6 | the 2nd line priced alone | 2.26 |
| P6 | the 2nd line priced with the architect line already drawn | 2.26 (order-independent; round 4 gave 2.26 vs base 2.50) |
| P6 | full tie, same SOW | architect 5.08 |
| P6 | full tie, higher SOW number | SOW-338120 5.62 |
| P6 | two bands, same level | out of scope, 0 (base) |
| P3s | gold | 2.82 |
| P3s | earlier 10:30 visit not yet posted | 2.82 |
| P3s | 3rd same-date visit | 2.82 |
| P3s | full tie, higher ticket number | 2.82 SB-2306640 |
| P2 | gold | 1.55 |
| P2 | the other 10-14 visit's travel not yet posted | 1.55 |
| P2 | 3rd same-date visit (45 min) | 1.55 |
| P2 | 3rd same-date visit (90 min) | 0.54 for that visit (its own price) |
| P2 | equal-minute 75 visit on SB-2306640 | 1.55 SB-2306640, then 0 once its travel stands |

In every both-orders and third-record probe, a record's price equals its own-attribute price.

### Stale-text sweep
- Charter: "this rule figures", "exactly one other", trip_cap / taper / return_visit, "less the minutes already recorded" and "band the project rule records" have no hits. "volume" appears only as P1's seat_volume_tier.
- Tasks: 362da00a, 926ed7c7, 165-minute, 0.27, 14.24/0.712/11.15/8.85, 312.83/78.44/64.53/27.55 have no hits, except one dated line in the rework-history notes. Rationales were rewritten.
- sweep.py: 0 issues.

### round 5 claims
- **N-6:** P3s, P4, P5 and P6 now price every record of their kind from its own attributes. The figured-record scoping and residues are removed, and the order-dependent P6 volume is replaced by the engagement class rate. The both-orders probes give equal prices.
- **N-7:** P2 prices every onsite visit's trip by one own-attribute schedule. Every visit has a stated price, and selection only picks which visit the compute figures.
- **N-8:** every selection's tie chain ends in a unique business key (ticket number, quote_number, SOW and level), stated in each rule and implemented with XLATEST on that key. The full-tie probes are recorded above.
- **Seeds:** both worlds were re-derived under the round-5 rules, with gold recomputed: task 0 2.82 / 1.55 / 2938.80; task 1 2.36 / 6.47 / 5.08 / 316.23. All proof text was regenerated or swept.
- **Full gate block:**
  - EXTENDED OK
  - TASK TOOL CONTRACT OK
  - REPLAY OK (0.json 17 acts 60/60, 1.json 24 acts 100/100)
  - SOLVABILITY OK
  - COMPUTE OK (branches mean 90.00, steps mean 20.50, history max 17, branches max 111)
  - GROUNDING OK
  - SCOPE OK
REWORK round 5: gates 7/7 green (superseded by round 6 below)

## round 6
- **Revision_5 verdict:** task0=PASS, task1=PASS, charter=N-6b (P6), N-7b (P2, P6). Closed with the coordinator's routes.
- **Gold is unchanged:**
  - task 0: 2.82 / 1.55 / 2938.80;
  - task 1: 2.36 / 6.47 / 5.08 / 316.23.
  - The only figure that moved is task 1's project minutes-baseline sensitivity, 4.65 -> 4.74: with that method at its baseline, the band minutes stay the 180-minute window.

### P6: project time drawn by group (N-6b, N-7b project)
- **The group:**
  - A group is the block-routed lines of one statement of work, date and level. It is drawn once, as one draw for its summed minutes (XSUM over the logs with exact SOW/date/level filters), priced only from its own lines and SOW.
  - A second level on the same SOW and date is its own group.
  - The line-count scope and the base fallback are gone.
- **Minutes and band:**
  - Minutes method: a weekend group is floored at weekend_minimum_minutes. A weekday group's after-hours minutes are rounded up to whole hours as a maintenance window, and its business minutes are taken as logged.
  - The band multiplier applies only to the group's band minutes (a weekend group's floored total, or a weekday group's rounded after-hours minutes). Its other minutes are drawn at 1.
  - The recorded band is holiday, after_hours or business_hours.
- **Selection:**
  - The latest date's first undrawn group on the highest-numbered SOW, taking levels architect, then senior_engineer, then technician.
  - Otherwise the first level, in that order, whose highest-numbered SOW logging it that date is undrawn.
  - SOW + date + level is the group's unique key.
- **P7:** the project prerequisite now waits on a draw for each group of the latest date, and P6 is the resolver that figures those groups.

### P2: one trip per onsite date (N-7b travel)
- **The trip:** one trip per client onsite date, however many visits that date and whether or not their tickets are resolved. It is posted once per date, at the close of the date, and booked to the date's longest visit (higher ticket number on a tie).
- **Price, from that date's draws only:**
  - trip value (agreement);
  - dispatch = the highest band among the date's draws (emergency, then after_hours/holiday, then 1);
  - level = the highest level among them (architect, then senior_engineer);
  - dispatch lead = the trip ticket opened the same day or the day before.
- **Selection and done test:** the latest onsite date; done = a travel entry dated that date.
- **P1:** the travel prerequisite now names the trip dated the latest service visit's resolution date.
- **Task 0 world:** SB-2309118 now opens 2026-10-09 and resolves 2026-10-13 10:30 (its draw and its trip df89b1f0 are dated 2026-10-13), so 2026-10-14 carries only SB-2306631. The travel tool's docstring now describes a per-date trip.

### Probe table, round 6 (scratch evaluator)
| policy | probe | result |
|---|---|---|
| P6 | gold architect group (165 min after-hours) | 5.08 |
| P6 | same group plus a 60-min business line | 6.43, one draw: (60 + 180 x 1.25)/60 x 1.5 x 0.9025 |
| P6 | 2nd level (senior, 120 business), architect undrawn | architect figured, 5.08 |
| P6 | then, architect drawn | senior figured, 2.26 |
| P6 | other order: senior drawn first | architect 5.08 |
| P6 | both orders | 5.08 / 2.26 either way |
| P6 | senior group of 120 business + 60 after-hours | 3.67 |
| P6 | 2nd SOW, technician only | SOW-338120 first (1.50) |
| P6 | then | SOW-337412 architect via the level clause (5.08) |
| P2 | gold 2026-10-14 trip | 1.55 |
| P2 | longer 2nd visit (120 business tech) posted after the gold visit | 1.35: one trip, ticket = longest visit, band still emergency from the date's draws |
| P2 | shorter 2nd visit (30), either order | 1.55 |
| P2 | 2nd visit by an architect | level 1.75, 1.89 |
| P2 | date already carries its trip | 0, no second trip |
| P2 | seeded trips re-priced at the close of their dates | ce7a1dbc 2026-07-15 -> 0.54; df89b1f0 2026-10-13 -> 0.54 (= seeded) |

- A date whose longer visit is drawn first prices one trip from the date's draws. No visit's travel is stranded by posting order.
- Residual on P6: two SOWs that log the same level on one date where the higher SOW's groups are all drawn. The rule's second clause reaches only the highest SOW per level, and this is stated in the rule.

### Stale-text sweep
- Swept the charter, tasks and tools for: "a line sharing", "the line figured", "Every line in that scope", "booked to the visit's ticket", "the visit so found", "own onsite-support draw is recorded", "SB-2309118's 2026-10-14", "only 2026-10-14 travel", "only block-routed line of its statement". No hits.
- The 2026-10-12 hits that remain are task 1's delivery date and one dated history note.
- sweep.py: 0 issues.

### round 6 claims
- **N-6b:**
  - P6 prices each group (SOW, date, level) for its summed minutes from its own lines and SOW. No sibling-dependent scope or base fallback remains, and a mixed-band group is one draw (probe 6.43 / 3.67).
  - P7's project edge waits on each group of the latest date, figured by P6.
- **N-7b project:** a second level on the same SOW and date is reachable in both orders (5.08 / 2.26 either way). A second SOW is reached through the level clause.
- **N-7b travel:**
  - P2 draws one trip per onsite date, priced from that date's draws by stated aggregates (highest band, highest level, the longest visit's ticket for the lead), posted once per date.
  - Both seeded trips are re-priced at 0.54. A date whose longer visit is drawn first still gets one trip.
- **Tasks not regressed:** all gold values, edges and factor figures are identical. The only change is task 1's minutes-baseline 4.74.
- **Full gate block:**
  - EXTENDED OK
  - TASK TOOL CONTRACT OK
  - REPLAY OK (0.json 17 acts 60/60, 1.json 24 acts 100/100)
  - SOLVABILITY OK
  - COMPUTE OK (branches mean 96.50, steps mean 20.50, history max 17, branches max 124)
  - GROUNDING OK
  - SCOPE OK
REWORK round 6: gates 7/7 green (superseded by round 7 below)

## round 7
- **Revision_6 verdict:** task0=PASS, task1=PASS, charter=N-7c (P6: three members). Closed with the coordinator's route.
- **Gold is unchanged:** task 0 2.82 / 1.55 / 2938.80; task 1 2.36 / 6.47 / 5.08 / 316.23. All factor figures and edges are identical.

### P6 changes
- **(a) Undrawn part.** A group's draw is its undrawn part: the minutes and hours the schedules give for all its logged lines, less the worked minutes and hours already on project-work draws with the same SOW, date and level. A group has an undrawn part when its drawn minutes exceed the minutes already drawn.
  - Compute: pj_p_k compares each candidate's drawn minutes with SUM of its worked_minutes; result = RND(MX(0, full − SUM hours drawn for the group)).
- **(b) Close of date.** New sentence: project time of a work date is logged and drawn at the close of that date, before any later date's line is drawn. A line logged after its group's draw is drawn by a further draw for the remainder.
  - This is consistent with project.yaml's per-line trigger, project_work_logged -> timebank:timebank_hours_drawn (one row per person-level per band per day, logged at the close of its day). Each such logged line draws its group's remainder.
- **(c) Scope by count.** Whether a date and level is in scope is decided by a count of logged lines, drawn or not: XCOUNT for the date and level must equal XCOUNT for the highest SOW logging that level. When two or more SOWs log the same level on one date, every line of that date and level keeps the restated base rule, line by line. Otherwise each level's group is the one SOW logging it.
  - Selection takes levels in order architect, senior engineer, technician; SOW, date and level end every tie.
- **P7:** the project prerequisite waits on every group of the latest date that the project-time rule prices, with no part left undrawn.
- **Tool docstring (O-13):** the project tool now says it draws "one group of time-and-materials project time, or of a group's undrawn part", and describes level, minutes and hours for the group. It matches the body.

### Probe table, round 7 (scratch evaluator, task 1 world)
| member | probe | result |
|---|---|---|
| (a) | after the gold 5.08 draw, a late 60-min architect business line | 1.35 (5.08 + 1.35 = 6.43, the same as drawing the whole group at once) |
| (a) | a late 30-min after-hours line (window 180 -> 240) | 1.69 (5.08 + 1.69 = 6.77 = the whole group's price) |
| (a) | a late 10-min after-hours line inside the 180 window | 0, nothing undrawn |
| (b) | a 2026-10-16 line while 2026-10-15 is undrawn | P6 moves to 10-16 (0.90). This state is not produced under the close-of-date sentence: each date is drawn at its close before a later date's line is drawn |
| (c) | SOW-337400 architect beside SOW-337412 architect on 2026-10-15 | both under the base rule; P6 0 for that level |
| (c) | same, with one already drawn under base | still base (decided by count, not order) |
| (c) | plus a senior line on SOW-337412 | the senior group is in scope and figured (2.26) |
| two levels, both orders | architect -> 5.08, then senior -> 2.26; senior drawn first -> architect 5.08 | same prices either way |

### Stale-text sweep
- Swept for: "first group not yet drawn", "A group counts as drawn", "a group is drawn once", "has not yet drawn it", "no group of that date is found", "one line of time-and-materials", "the line is drawn at". No hits.
- Task 1's round-6 history note is marked "selection superseded in round 7".
- sweep.py: 0 issues.

### round 7 claims
- **N-7c (a) late line:** the group's draw is its undrawn part (priced minutes and hours for all its lines, less what is already drawn for the same SOW, date and level). A late line yields a further draw, and the sum of the draws equals the whole group's price (probes 1.35, 1.69, 0).
- **N-7c (b) earlier date pending:** the close-of-date sentence makes it a state the charter does not produce. It is consistent with project.yaml's per-line logged -> drawn trigger.
- **N-7c (c) second SOW at the same level:** the scope is decided by a count of logged lines, drawn or not; the base rule is restated for a date and level logged by two or more SOWs. Every in-scope group is reached by level order (probes above).
- **O-13:** the project tool docstring now describes a group or a group's undrawn part.
- **Tasks:** not regressed; every figure is identical.
- **Full gate block:**
  - EXTENDED OK
  - TASK TOOL CONTRACT OK
  - REPLAY OK (0.json 17 acts 60/60, 1.json 24 acts 100/100)
  - SOLVABILITY OK
  - COMPUTE OK (branches mean 102.50, steps mean 20.50, history max 17, branches max 136)
  - GROUNDING OK
  - SCOPE OK
REWORK round 7: gates 7/7 green (superseded by round 8 below)

## round 8
- **Revision_7 verdict:** task0=PASS, task1=PASS, charter=N-6c (P6 sibling-dependent scope, plus a knock-on on P7's third edge). Closed with the coordinator's route.
- **Gold unchanged:** task 0 2.82 / 1.55 / 2938.80; task 1 2.36 / 6.47 / 5.08 / 316.23. All factor figures, skip effects and edges are identical.

### P6 scope by contract records (N-6c)
- **New self-naming overwrite scope.** A group is in scope when it is drawn from "a block that is the TimeBank route of exactly one time-and-materials statement of work, meaning the client holds exactly one time-and-materials engagement whose status is signed, in_progress, on_hold or pending_acceptance".
  - Compute: pj_tm_live = XCOUNT over project_engagements by pricing_model and those four statuses; the result applies only when pj_tm_live == 1.
- **Every other client's project time** keeps the standard minutes, conversion and band rules wholly and line by line. These are restated in each replaced_by, with base rounding and band precedence spelled out.
- **Removed:** the count-of-SOWs-per-date scope (pj_n_k / pj_m_k).
- **Order independence:** the scope reads engagement records only, never a timesheet line, so it does not depend on what another engagement logs or on drawing order.
- **Reach:** inside the scope there is one statement of work, so level order plus the close-of-date sentence reach every group, and the undrawn-part rule draws any late line.
- **P7's third prerequisite now reads:** "Before the extension fee is worked out for a client holding exactly one live time-and-materials engagement, one signed and not yet accepted, closed or cancelled, the block's hours ledger must carry the project-work draws of every group of the client's most recently dated project time … with no part of any group left undrawn; for any other client the extension fee does not wait on project time." (Status tokens were reworded for the KB leak gate.) One reading only.
- **Task 1 world is in scope:** SOW-337412 (Advanced Project, T&M, in progress) is the client's only engagement. The seed check now says so.

### Overwrite sweep: replaced_by vs retired clause (dropped in-force content)
- **P1 (block price):** restored "rounded half up to the cent, and is block_list_price_usd otherwise" for every other order.
- **P7 (extension fee):** restored "rounded half up to the cent"; invoicing-on-effect and the rolled-out exclusion were already kept.
- **P3s, P4, P5, P6 (minutes, conversion, band):**
  - The combination sentences now say "rounded half up to draw_rounding_hours once, at the end" (the rounding unit was dropped).
  - Band replaced_by now spells out "the standard time-band precedence of holiday, emergency, after_hours and business_hours".
  - P6's out-of-scope minutes clause restates "recorded minutes rounded up to billing_increment_minutes".
- **P2 (travel):** the retired flat per-visit trip is replaced by one trip per date. Business band and no-ratio are restated in the baseline sentence; rounding is in the combination sentence. No other definitions were dropped.

### Probe table, round 8 (scratch evaluator, task 1 world)
| probe | P6 result |
|---|---|
| gold | 5.08 (live T&M = 1) |
| another client's T&M engagement, routed to that client's block | 5.08, no effect |
| a second engagement, fixed fee, same client | 5.08 |
| an earlier T&M engagement, closed | 5.08 |
| a second live T&M SOW, same client (time on it or not) | 0: the block's project time goes wholly to base; P7 then waits on no project time |
| inside scope: two levels | architect 5.08, then senior 2.26 |
| inside scope: late 60-min line after the gold draw | remainder 1.35 |

Engagements carry no block reference, so routing is client-level: a client's block-routed time draws from its active block by the base draw order.

### Stale-text sweep
- Swept for: "no other statement of work logs", "two or more statements of work log", "each level's group being the one statement of work", "in this rule's scope", "decided by the logged lines of that date", "rounded once, at the end". No hits.
- Task 1's round-7 note is marked "scope superseded in round 8".
- sweep.py: 0 issues.

### round 8 claims
- **N-6c:** P6's scope is a contract attribute (exactly one live T&M engagement makes the block the TimeBank route of one SOW). It is read from engagement records only and stated as a self-naming overwrite, with every other client's project time wholly under the restated base rule. No group's price depends on another engagement's timesheet, and every in-scope group is reachable (probes above).
- **N-6c knock-on (P7 third edge):** the sentence names its scope. In scope it waits on every group, undrawn parts included; out of scope it says the fee does not wait on project time. This removes the second reading.
- **Overwrite content sweep:** the dropped rounding units, price fall-back and band precedence were restored in P1, P3s, P4, P5, P6 and P7.
- **Tasks:** not regressed; task 1 is confirmed in scope.
- **Full gate block:**
  - EXTENDED OK
  - TASK TOOL CONTRACT OK
  - REPLAY OK (0.json 17 acts 60/60, 1.json 24 acts 100/100)
  - SOLVABILITY OK
  - COMPUTE OK (branches mean 101.50, steps mean 20.50, history max 17, branches max 134)
  - GROUNDING OK
  - SCOPE OK
REWORK round 8: gates 7/7 green (superseded by round 9 below)

## round 9
- **Revision_8 verdict:** task0=PASS, task1=PASS, charter=N-9.
- **Edits:** text only, in the band and conversion tails of P3s, P4, P5 and P6, which are both in the rule and in the replaced_by.
- **Unchanged:** gold, edges and every figure in both tasks.

### Tails restated verbatim from the retired base clauses
- **Conversion tail.** Every other draw "keeps the standard conversion: converted block hours equal worked minutes divided by 60, times the resource ratio (technician_ratio, senior_engineer_ratio or architect_ratio), times the band multiplier (holiday_multiplier, emergency_multiplier or after_hours_multiplier, and 1 in business hours), rounded half up to draw_rounding_hours."
- **Band tail.** Every other draw "keeps the standard time band: holiday on weekends and observed holidays, emergency for work dispatched outside business hours at the client's request to restore a down system, after_hours for other work outside business_hours_start to business_hours_end on business days (business_hours_days, excluding the observed_holiday_list), and business_hours otherwise; only one band applies to a session, in that order of precedence."

### Word diff: tail vs retired clause (scratch)
| policy | conversion tail | band tail | minutes tail |
|---|---|---|---|
| P3s | missing: none | missing: only "is" (grammar) | in-scope rule covers every service visit; siblings cover the other kinds (revision_8: clean) |
| P4 | none | "is" | covers every remote session (clean) |
| P5 | none | "is" | covers every installation visit (clean) |
| P6 | none | "is" | out-of-scope project time keeps "its recorded minutes rounded up to billing_increment_minutes"; the remote and onsite minimums do not apply to a project line (clean) |

### Probe
- **Case:** an out-of-scope project line, on a client holding two live T&M SOWs. It is a 120-min senior_engineer business_hours line on Labor Day, 2026-09-07 (Monday), on a 160-hour block.
- **Reading the restated tails:**
  - Band: "holiday on weekends and observed holidays" (Labor Day is in observed_holiday_list) gives holiday. Only one band applies, in order of precedence.
  - Conversion: 120/60 × senior_engineer_ratio 1.25 × holiday_multiplier 1.75 = 4.375 h, rounded half up to draw_rounding_hours, gives 4.38 h. That matches the retired base sentence, so the tails alone now give the base figure.
- **Scratch evaluator:** P6 returns 0 for this client (out of scope, as stated), so the base rule governs the line.

### round 9 claims
- **N-9:**
  - The conversion and band tails of P3s, P4, P5 and P6 restate every still-in-force word of the base clauses they retire: the ratio and multiplier enumerations, rounding, the holiday, emergency and after-hours tests, "only one band applies to a session" and precedence.
  - The word-diff table is recorded above, and the Labor Day probe gives 4.38 h under the tails.
- **Tasks:** not regressed (text-only change).
- **Full gate block:**
  - EXTENDED OK
  - TASK TOOL CONTRACT OK
  - REPLAY OK (0.json 17 acts 60/60, 1.json 24 acts 100/100)
  - SOLVABILITY OK
  - COMPUTE OK (branches mean 101.50, steps mean 20.50, history max 17, branches max 134)
  - GROUNDING OK
  - SCOPE OK
REWORK round 9: gates 7/7 green (superseded by round 10 below)

## round 10
- **Revision_9 verdict:** task0=PASS, task1=PASS, charter=N-10.
- **Edits:** text only, in four places:
  - the conversion and band tails of P3s, P4, P5 and P6, both in the rule and in the replaced_by;
  - P2's sibling tail;
  - the travel tool's time_band docstring.
- **Unchanged:** gold, edges and every figure in both tasks.

### N-10 edits
- **The eight conversion/band tails now name travel entries.** For example, "an installation visit, a remote session, a project time line and a travel entry are figured under their own schedules, and every other draw keeps the standard conversion …" and "… and a travel entry take their bands from their own rules, and every other draw keeps the standard time band …". P4, P5 and P6 follow the same pattern with their own sibling sets. Travel is therefore never read as falling under the base conversion or the base band.
- **P2's tail now names its siblings:** "a remote session, a service visit, an installation visit and a project time line keep their own rules, and every draw that is not a travel entry keeps its own rule".
- **Travel tool time_band, one reading per case:**
  - business_hours: a trip at multiplier 1;
  - after_hours: a trip at the after-hours multiplier, which is also how a weekend or holiday trip is drawn and recorded;
  - emergency: a trip at the emergency multiplier;
  - holiday: never used for a travel entry.
  - This matches P2: "The travel entry is recorded in the band whose multiplier the dispatch schedule applied". A Saturday visit drawn holiday gives a trip at after_hours_multiplier, recorded after_hours, with only that reading.

### Sibling-list table: every scoped overwrite, sibling cases named (scratch check)
| policy | retired clause | siblings named |
|---|---|---|
| P2 travel | flat onsite_trip_hours row | remote session, service visit, installation visit, project time line (+ every non-travel draw) |
| P3s | minutes / conversion / band | installation visit, remote session, project time line, travel entry: all three |
| P4 | minutes / conversion / band | service visit, installation visit, project time line, travel entry: all three |
| P5 | minutes / conversion / band | service visit, remote session, project time line, travel entry: all three |
| P6 | minutes / conversion / band | remote session, service visit, installation visit, travel entry (+ out-of-scope project time): all three |
| P1 | block price | one object (other orders: restated standard price) |
| P7 | extension fee | one object (every extension) |

### round 10 claims
- **N-10:**
  - All eight conversion/band tails exclude travel entries by name.
  - Every scoped overwrite now names all sibling policies' cases (table above).
  - The travel tool's time_band has exactly one reading for weekend, holiday, emergency and after-hours trips.
- **Tasks:** not regressed (text-only change).
- **Full gate block:**
  - EXTENDED OK
  - TASK TOOL CONTRACT OK
  - REPLAY OK (0.json 17 acts 60/60, 1.json 24 acts 100/100)
  - SOLVABILITY OK
  - COMPUTE OK (branches mean 101.50, steps mean 20.50, history max 17, branches max 134)
  - GROUNDING OK
  - SCOPE OK
REWORK round 10: gates 7/7 green (superseded by round 11 below)

## round 11 (render_r1 scan-first STOP)
- **Gold hours and figures:** unchanged in both tasks. Task 0 is 2.82 / 1.55 / 2938.80; task 1 is 2.36 / 6.47 / 5.08 / 316.23.
- **One scored argument moved, forced by item 3c:** task 1's project draw now records worked_minutes 165, the group's logged minutes not yet drawn, instead of 180.

### Items
1. **P3s assembly sentence**, now generic: "replace or adjust the standard minutes, multiplier and ratio in this order: floors on the minutes first, then a weighting of part of the minutes, then the multipliers and the ratio, which multiply one another with no order between them; the product is rounded half up to draw_rounding_hours once, at the end." Each factor's own sentence still says how its figure enters (raised to at least / priced at emergency instead of after-hours / multiplied by / figured at).
2. **P4:** the same generic order (floors, then partial weighting, then multipliers and the ratio).
3. **P6 (project):**
   - **(a) Assembly sentence** now reads "replacements of the minutes first, then the multipliers and the ratio …, a multiplier that a schedule applies to part of the minutes leaving the rest at 1; … rounded half up to draw_rounding_hours once, at the end".
   - **(b) Band-minutes window.** The plain "band minutes" sentence and the plain binding pj_window are removed. The window is now stated inside the band schedule ("has its summed minutes, raised to at least weekend_minimum_minutes, multiplied by holiday_multiplier; … has those after-hours minutes, rounded up to the next multiple of 60, multiplied by after_hours_multiplier, its other minutes keeping a multiplier of 1"). In compute it is owned by project_band_rate: pj_window and pj_band_extra, with baseline pj_band_extra = 0.
   - **(c) Undrawn part without factor content.** The undrawn part is now "its logged minutes not yet drawn: its summed logged minutes less the worked minutes the ledger already carries" for the same SOW, date and level (pj_p_k = logged > drawn minutes). A draw records those minutes, and draws "the block hours the schedules below give for all the group's logged lines, less the block hours already drawn". A part whose hours come to zero is a zero-hour draw.
   - **baseline.rule** now says exactly what compute subtracts: "draws its summed logged minutes divided by 60, at technician_ratio and with a multiplier of 1, less the block hours already drawn for it, rounded half up …".
   - **Late-line probe** (after the gold draw):

     | late line | result |
     |---|---|
     | 60-min business | 1.35 (5.08 + 1.35 = 6.43 = one-draw price) |
     | 10-min business | 0.22 (the round-7 raw-vs-basis test would have missed this) |
     | 30-min after-hours | 1.69 |
     | 10-min after-hours inside the window | 0.00 (zero-hour draw) |
4. **P7 assembly:** "replacements of the percentage and of the value of an hour first, then additions of points to the percentage, then the multipliers of the fee, which multiply one another with no order between them; rounding to the cent happens once, at the end."

- **Travel note:** "A block whose size carries onsite_trip_hours of zero draws no travel, its trip being zero hours whatever the schedules below select, and a travel figure of zero means no travel entry is drawn for the date." This matches compute's `P('onsite_trip_hours') and …`.

### All-policy sweep, same classes (scratch: assembly wording, single-factor plain quantities, plain reading factor content, baseline vs compute)
| policy | assembly | XF 5 single-factor plain | plain uses factor content | baseline = compute |
|---|---|---|---|---|
| P1 | generic (unchanged) | none | none | yes |
| P2 | generic; zero-size sentence added | cp_status moved into trip_value_basis | none | yes |
| P3s | rewritten generic | cp_status moved into service_clearpath_rate | none | yes |
| P4 | rewritten generic | cp_status moved into remote_clearpath_rate | none | yes |
| P5 | generic (unchanged) | cp_status and in_endpoint_install moved into install_clearpath_rate; in_billable_basis stays plain because the baseline (standard method) uses it | none | yes |
| P6 | rewritten generic | pj_window and pj_band_extra are now band-factor owned | pj_p_k now minutes vs minutes | yes, now hours less hours drawn |
| P7 | rewritten generic | cp_status moved into clearpath_loyalty_rate | none | yes |

- **Mechanical sweep:** 0 issues (basis verbatim, keys, XF 26/A.1, binding order).
- **Stale text:** no hits for "the call-out floor raises", "the floors raise the rounded minutes first", "the band multiplier acts", "A group's band minutes are", "the signing schedule sets", "less any minutes already drawn", "drawn minutes do not exceed", "undrawn part's minutes". The task 1 tracing and rationale now state 165 recorded minutes.

### round 11 claims
- **1 (P3s), 2 (P4), 3a (P6), 4 (P7):** the assembly sentences are generic by kind of operation and name no factor quantity; the combination orders are kept.
- **3b:** the band window is stated in and owned by the band factor.
- **3c and baseline:** the undrawn part is selected by logged versus recorded minutes, independent of factor content. baseline.rule states the hours subtraction compute does, and the late-line probes are recorded above.
- **Travel note:** the zero-trip-hours sizes are stated in the rule.
- **Sweep:** XF 5 single-factor plain bindings were moved into their factors across P2, P3s, P4, P5 and P7; table above.
- **Tasks:** hours unchanged. Task 1's project worked_minutes is now 165, replay-consistent.
- **Full gate block:**
  - EXTENDED OK
  - TASK TOOL CONTRACT OK
  - REPLAY OK (0.json 17 acts 60/60, 1.json 24 acts 100/100)
  - SOLVABILITY OK
  - COMPUTE OK (branches mean 98.00, steps mean 20.50, history max 17, branches max 127)
  - GROUNDING OK
  - SCOPE OK
REWORK round 11: gates 7/7 green (superseded by round 12 below)

## round 12
- **Revision_11 verdict:** task0=PASS, task1=RED[R11-1.1], charter=N-11, N-12.
- **Gold now:**
  - task 0: 2.82 / 1.55 / 2938.80 (unchanged);
  - task 1: 2.36 / 6.47 / **4.81** / **325.87**. These moved, forced by re-pricing the cross-product rows.
  - Task 1's project worked_minutes is back to 180.

### N-12 / R11-1.1: worked_minutes has one reading
- Rule, tool docstring and gold now all say "the minutes the group is drawn for, after the floor or whole-hour rounding the minutes schedule applies". This is the convention of the sibling draw tools (remote: "the minutes the session is drawn for after rounding and any floor").
- Gold: 180 (165 after-hours minutes drawn in whole hours). The "or its undrawn part" wording is removed from the tool.

### N-11: no zero-hour row
- **Late lines are no longer producible.** The undrawn-part machinery is removed. New sentence: "Project time of a work date is logged in full at the close of that date, before any of that date's groups is drawn and before any line of a later date is drawn, so a group is drawn once, for all its lines, …; no line is logged for a date after that date's groups are drawn." This is consistent with project.yaml's per-line logged -> drawn trigger, since all of a day's lines are logged at its close.
- **Done test:** a group counts as drawn when the ledger carries a draw with its SOW, date and level (pj_dn_k COUNT); plain record test, no factor content.
- **Hours:** the group's priced hours, with no subtraction. baseline.rule is "summed logged minutes divided by 60, at technician_ratio, multiplier 1, rounded half up".
- **P7's wait:** "the project-work draws of every group … a group being that date's lines of one level". The "no part left undrawn" clause is removed, so words equal compute.

### Cross-product re-pricing under the published docs (managed, hardware, project; licensing has no rows)
Done by two read-only scratch derivations over docs/managed, docs/hardware and docs/project, then applied.

| task | row | was | now | rule (published doc) |
|---|---|---|---|---|
| 0 | ClearPath seat_rate_usd | 124.00 | 123.38 | renewal term rate: min(uplifted, list 124.00, protection cap) × (1 − 0.5%), fewer tickets than seats in the renewal year; the same at every renewal |
| 0 | monthly fees May–Oct 2026 (6) | 4216.00 | 4194.92 | 34 × 123.38; billed seats max(34, floor 29); under 40 seats, so no volume break |
| 0 | payments May–Sep (5) | 4216.00 | 4194.92 | each settles its invoice before due (net 30); no late fee |
| 0 | agreement balance_due_usd | 4216.00 | 4194.92 | October open, not due |
| 1 | ClearPath seat_rate_usd | 149.00 | 148.26 | 149.00 × 0.995 = 148.255, rounded half up (decimal) to 148.26; the same through the prior term |
| 1 | monthly fees Dec 2025–Oct 2026 (11) | 8642.00 | 8542.74 | 58 × 148.26 less the volume price break (seats 40–58 at 2.0%: 57.62 × 148.26) |
| 1 | payments Dec–Sep (10) | 8642.00 | 8542.74 | paid on the 22nd, before due; no late fee |
| 1 | agreement balance_due_usd | 8642.00 | 8542.74 | October open |
| 1 | hardware unit price / quote total | 1444.80 / 18652.60 | same | markup 15 − 3 ClearPath points; staging, handling and rush |
| 1 | hardware deposit invoice and card payment | 4663.15 | 3357.47 | endpoint deposit: tenure build 3 (79 months) at the Professional share 20%, 0 late points, −2.0 managed-spend relief (8542.74 / 18652.60 = 0.458) = 18% |
| 1 | hardware final invoice / order balance | 13989.45 | 15295.13 | 18652.60 − 3357.47; due 2026-11-11 |
| 1 | project rate_discount_pct | 7.5 | 10.5 | rate lock: tier 7.5 + seat scale 0.5 + tenure 1.0 + term 0 + TimeBank prepaid hours 1.5 |
| 1 | project deposit invoice and wire payment | 16000.00 | 7160.00 | 64000 × 89.5% = 57280 at 25 − 5 (ACH) − 10 (standing) + 2.5 (short-notice) = 12.5% |
| 1 | project balance / value / kickoff | 0.00 / 64000 / 08-17 | same | — |
| 1 | historic project draws | 5.75 / 6.49 / 7.90 / 6.77 / 5.64 | 5.45 / 6.15 / 7.48 / 6.41 / 5.34 | discount band now 0.9 (10.5 ≥ discount_band_high 10) × class 0.95 |
| 1 | block hours_balance | 79.14 | 80.86 | 160 − 79.14 drawn |
| 1 | gold P6 | 5.08 | 4.81 | 3.75 × 1.5 × 0.9 × 0.95 = 4.8094 |
| 1 | gold P7 | 316.23 | 325.87 | 67.22 × 128.25 × 7% × 0.75 × 0.8 × 0.9 |

- **Task 1 factors after re-pricing:**
  - P6 baselines: 4.49 / 3.85 / 3.21 / 5.34 / 5.06, all 2.75; the discount tier is now discount_band_high.
  - P7 baselines: 395.70 / 279.32 / 343.02 / 434.50 / 407.34 / 362.08, all 680.60.
  - Skips: 337.31 / 357.24 / 349.19.
  - P4 and P5 are unchanged.
- **Assumption, stated in the seed checks:** tickets, late fees and credits before the seed windows are absent, so every renewal takes the 0.5% ticket-volume reduction and the rate is the same through the prior term.
- **Proof text swept:**
  - tracing, factor traces, sensitivities, closure, seed checks and gold-action effects;
  - task 0's read objective (4194.92 / 123.38);
  - task 1's rationale §6, §7 and §9 (history rewritten as a summary with current figures).
- **Stale scan:** no hits for 316.23, 5.08, 312.83, "discount 7.5", "locked 7.5", 8642, 4663, 16000 or 13989 in either task's proof text.

### round 12 claims
- **N-12 / R11-1.1:** worked_minutes means "the minutes the group is drawn for", the same in rule, tool docstring and gold (180), matching the sibling tools.
- **N-11:** no zero-hour row can arise. A date's lines are logged in full before its groups are drawn, so a group is drawn once. The done test is a plain draw-exists check, and P7's wait matches it.
- **Cross-product re-pricing:** every ClearPath, hardware and project row of both tasks was re-priced under the published docs (table above). Task 1 gold moved, was recomputed, and its proof text was swept.
- **Full gate block:**
  - EXTENDED OK
  - TASK TOOL CONTRACT OK
  - REPLAY OK (0.json 17 acts 60/60, 1.json 24 acts 100/100)
  - SOLVABILITY OK
  - COMPUTE OK (branches mean 94.50, steps mean 20.50, history max 17, branches max 120)
  - GROUNDING OK
  - SCOPE OK
REWORK round 12: gates 7/7 green (superseded by round 13 below)

## round 13 (seed only)
- **Charter and tools:** byte-identical (timebank.extended.yaml 4bf1e7bb716bcf4f, task_tools.py f7013dc51432fa1b). Only tasks/0.json and tasks/1.json changed.
- **Scored values:** none moved. Task 0 is 2.82 / 1.55 / 2938.80; task 1 is 2.36 / 6.47 / 4.81 / 325.87.

### R12-0.1 / R12-1.1: onboarding tickets of the seat additions
| task | ticket | opened | first response | resolved = seat effective date | users / minutes | lead check | settlement (published rules) |
|---|---|---|---|---|---|---|---|
| 0 | SB-1876402 | 2023-02-27 10:05 | 10:40 | 2023-03-06 09:10 | 2 / 60 | 5 business days ≥ Standard lead 3 | user_onboarding, P3, portal; covered (Standard includes remote help desk), included remote business-hours |
| 0 | SB-2155617 | 2025-09-02 13:20 | 13:55 | 2025-09-08 09:25 | 1 / 30 | 4 business days (Labor Day 09-01 excluded) | same |
| 0 | SB-2201384 | 2026-02-24 11:15 | 11:40 | 2026-03-02 09:05 | 1 / 30 | 4 business days | same |
| 1 | SB-1602771 | 2022-06-07 14:10 | 14:35 | 2022-06-13 10:30 | 5 / 150 | 4 business days ≥ Professional lead 2 | same (Professional includes remote help desk) |
| 1 | SB-2003358 | 2025-04-01 09:40 | 10:05 | 2025-04-07 09:50 | 3 / 90 | 4 business days | same |

- **Docs applied:**
  - seat_ledger_changes_and_proration §1/§4: seats are added under a user onboarding ticket; ready on the start date when opened at least the lead time before it.
  - ticket_priority_and_scope: onboarding is covered where the tier includes covered remote help desk work.
  - ticket_labor_settlement_rules L3: covered remote work within coverage hours is included.
  - managed.yaml: helpdesk_remote_included is true for both tiers.
- **Follow-on records:** none is due. Included labor creates no invoice line and no TimeBank draw. Each seat addition's proration bills on the next monthly invoice under the effective month (2023-03, 2025-09, 2026-03; 2022-06, 2025-04), all before the seeded billing windows (task 0 2026-05.., task 1 2025-12..).
- **First responses:** 25–35 min, against the P3 target of 240.
- **Knock-on:** the renewal-year ticket counts rise to 6 (task 0) and 3 (task 1), still below the 34 and 58 seats. The 0.5% ticket-volume reduction stands, so rates 123.38 and 148.26 are unchanged.

### Exhaustive reference pass (scratch)
- **Checked in both seeds:** every ticket_number, sow_number and payment invoice_number, plus every id field marked "foreign key ->" in db_schema, against the seeded rows.
- **Result:** 0 dangling references in task 0 and task 1. Every ledger draw's ticket and SOW exists. Every payment's invoice exists in its own billing table. The hardware request references the order; the seat changes reference the agreement and now their onboarding tickets.

### round 13 claims
- **R12-0.1 / R12-1.1:** the five onboarding tickets are seeded per the published managed rules (category, priority, scope, included settlement, lead-time-consistent dates). The whole referenced-record class is checked, with 0 dangling references.
- **Hashes unchanged:** timebank.extended.yaml 4bf1e7bb716bcf4f; task_tools.py f7013dc51432fa1b.
- **Full gate block:**
  - EXTENDED OK
  - TASK TOOL CONTRACT OK
  - REPLAY OK (0.json 17 acts 69/69, 1.json 24 acts 106/106)
  - SOLVABILITY OK
  - COMPUTE OK (branches mean 94.50, steps mean 20.50, history max 17, branches max 120)
  - GROUNDING OK
  - SCOPE OK
REWORK round 13: gates 7/7 green (superseded by round 14 below)

## round 14 (seed only; KB audit revision_1 src items)
- **Charter and tools:** byte-identical (timebank.extended.yaml 4bf1e7bb716bcf4f, task_tools.py f7013dc51432fa1b). Only tasks/0.json and tasks/1.json changed.
- **Scored values:** none moved. Task 0 is 2.82 / 1.55 / 2938.80; task 1 is 2.36 / 6.47 / 4.81 / 325.87.

### SEED-MGB-0 / SEED-MGB-1: rate of the term in force
Each fee was re-derived at its own posting date (the published renewal and current-month documents).
- **Renewal rate.** The renewal rate is the lower or lowest candidate, uplifted vs list (plus expiring × 1.02 once live 60+ months). It is then adjusted once by the net percentage of the service-intensity and other adjustments, then capped.
- **Ticket-volume look-back.** "Fewer tickets than the seat count take 0.5 percent off". The ticket ledger is the authority, so every renewal year in both seeds has fewer tickets than seats.
- **Steady state.** The list candidate, less 0.5%, is reached at every renewal from the first (task 0) or second (task 1). The expiring rate equals the renewed rate. The KB reading that "the renewed rate is strictly above the expiring rate" leaves out the ticket-volume adjustment.

| task | renewal | candidates | adjustment | rate |
|---|---|---|---|---|
| 0 | 2020-07-15 (1st) | 130.20 vs list 124.00 (rule c) | −0.5% (0 tickets / 30 seats) | 123.38 |
| 0 | 2021–2026 (2nd–7th) | list 124.00 is lowest (rule b from 2024: 125.85 also above) | −0.5% (2023: 1/30; 2026: 6/34; else 0) | 123.38 |
| 1 | 2023-02-24 (1st, 36-month term, cap 3%) | 145.80 vs 149.00 (rule c) | −0.509% (1 ticket / 55, seat growth) | 145.06 |
| 1 | 2024-02-24 / 2025-02-24 | 152.31 / 155.67 vs 149.00 | −0.5% (0 tickets) | 148.26 / 148.26 |
| 1 | 2026-02-24 (4th, cap 4%, rule b) | 154.19, 149.00, 151.23 | −0.5% (3 tickets / 58) | 148.255 → 148.26 |

- **Monthly fees** (posted on the 1st as that day's current-month fee; no seat change that month; no Microsoft 365 holdings):
  - task 0, every month 2026-05..10: 34 × 123.38 = 4194.92 (under 40 seats, so no volume break). Pre-renewal (May–July) and post-renewal (Aug–Oct) are equal because the term rates are equal.
  - task 1, every month 2025-12..2026-10: 58 × 148.26 less the volume break (19 seats × 2.0% / 58), i.e. 57.62 × 148.26 = 8542.74. The base 1.2 figure of 8599.08 applies only to a fee outside the current-month scope, and none of these fees is outside it.
- **Payments and balances follow** (ACH before net-30 due, no late fee; balances = the open October fee).
- The derivation is now written into each task's managed seed check.

### SEED-SCOPE-HOWTO
- **Problem:** SB-2275518 (task 0) and SB-2297262 (task 1) were how-to questions. A how-to question is covered help-desk work on tiers that include remote help desk.
- **Fix:** both are re-seeded as service_request tickets (billable out of scope, routed to the block), on all three milestone rows each.
- **Draws unchanged:** under the remote-session rules a service request takes the size's 15-minute minimum, and 45 minutes stays 45, so both draws stay 0.75 h.
- **Re-check of every TimeBank draw in both tasks:** each rests on a resolved ticket with scope billable_out_of_scope and labor_route timebank, an active block covering it, or on block-routed project time.
  - Remote business-hours service requests, degraded service and outages are outside the tiers' covered help-desk reading.
  - After-hours remote is not included on Standard or Professional (after_hours_remote_included false).
  - SB-2311409 (Professional, P1 after-hours) is recorded billable_out_of_scope, a security concern outside the help-desk entitlement.
  - Onsite visits are billable_out_of_scope, so the included onsite hours (L3, covered tickets only) do not apply.
  - The onboarding tickets are covered and included, with no draw.

### Exhaustive cross-product pass, every published product, with look-back windows
| product | rows (task) | check | result |
|---|---|---|---|
| managed | agreement, seat changes, 5 onboarding tickets, fees, payments (0, 1) | term rates (above), current-month schedule, proration months before the windows, late-fee 12-month look-back (none), first-response SLA for P1/P2 tickets (all within target, no credit), renewal-year ticket counts | consistent |
| managed | timebank-routed tickets (0, 1) | scope and route per the scope guide and L3/L6 | consistent after the how-to fix |
| hardware | order HQ-604418, request, deposit, payment, final invoice (1) | quote pricing, endpoint deposit 18% (managed-spend relief 8542.74 / 18652.60 = 0.458, 2.0 points), credit exposure, net-30 due 2026-11-11, no late fee | consistent (round 12) |
| project | engagement SOW-337412, deposit, payment, work logs (1) | rate lock 10.5, deposit 7160.00 (ACH count over 6 months, open balance 0 on 07-28, standing, short notice), kickoff, T&M routed to the block | consistent (round 12) |
| licensing, security, backup | none (0, 1) | the clients hold no such holding, and every factor reading them takes its no-holding tier | n/a |
| timebank | orders, invoices, payments, ledgers (0, 1) | own charter (rounds 2–12) | consistent |

### round 14 claims
- **SEED-MGB-0 / SEED-MGB-1:**
  - Every ClearPath monthly fee is priced at the rate of the term in force on its posting date, with the current-month schedule as of that date.
  - The term-by-term derivation shows the prior-term rate equals the renewed rate in both seeds (123.38; 148.26), so the seeded fees, payments and balances stand.
  - The derivation, including the ticket-volume look-backs, is now stated in the seed checks.
- **SEED-SCOPE-HOWTO:** both how-to tickets were re-seeded as billable out-of-scope service requests, and every TimeBank draw was re-checked as routed by the published rules.
- **Exhaustive pass:** all published products checked, table above; no further member found.
- **Hashes unchanged:** timebank.extended.yaml 4bf1e7bb716bcf4f; task_tools.py f7013dc51432fa1b.
- **Full gate block:**
  - EXTENDED OK
  - TASK TOOL CONTRACT OK
  - REPLAY OK (0.json 17 acts 69/69, 1.json 24 acts 106/106)
  - SOLVABILITY OK
  - COMPUTE OK (branches mean 94.50, steps mean 20.50, history max 17, branches max 120)
  - GROUNDING OK
  - SCOPE OK
REWORK round 14: gates 7/7 green
