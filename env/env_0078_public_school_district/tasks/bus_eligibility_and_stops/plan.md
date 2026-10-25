# plan.md — bus_eligibility_and_stops (category transport), M=2

Draw (scripts/draw_counts.py --tasks 2):
- task 0: prerequisite_problems=1, factor_counts=[6, 5]
- task 1: prerequisite_problems=1, factor_counts=[6, 4]

Scratch: /tmp/bus_eligibility_and_stops_0078/ (worlds builder, verifier). Removed from write domain at the end.

## Charter constraints found in Step 0 (decisive for the design)
- DSL reads only THIS holding (F, SUM/COUNT/LATEST scoped to transport_assignment_id) + OTHER categories
  (meals / enroll / care / activity). Sibling transport assignments are unreadable -> household cap
  (transport_agg_household_permit_cap) can never be a computed factor; every world keeps the household
  far under 480.00 with a single courtesy rider, so the cap never binds (stated in worklog).
- value_input edges must act on the SAME assignment (dependent compute can read only its own holding).
- An application creates its holding, so it cannot carry a computation (target holding absent before
  the write). Payments / refunds are balance takers. -> numeric user writes used: (a) family
  cancellation with its credit (by:user transition, owner ruling a); (d) the parent's signed courtesy
  rider permit agreement accepting an offered waitlist seat, which posts the permit fee (owner ruling d).
- No refund tool and no payment tool exist in this difficulty (a credit balance after cancellation is
  refunded by the business office within credit_balance_refund_days; not owed at once; no tool).
- Trigger rule: events written = transport_fee_credit, transport_permit_cancellation, transport_permit_fee
  (+ transport_requests status update). All have triggers: [] in base. None lands in another category.

## Trees
Task 0 (household Villarreal, frozen 2026-11-13 08:50:00 CST; since round 4 the permit is a waiting-list seat signed 2026-09-04) — "cancel the bus permit":
- prereq P_A transport_ext_meal_status_fee_adjustment (agent, 5 factors): billing_correction credit on the
  annual permit fee when a higher meal status took effect after the fee posted (scoped overwrite of
  base "A meal status determined after the fee posted does not change that fee").
- root P_B transport_ext_family_cancellation_credit (user, 6 factors): family confirms cancellation
  (active -> cancelled) and the cancellation credit posts (district refund schedule).
- edge P_B -> P_A value_input (net fee binding), state form: credit fixed only after the fee carries
  the meal-status adjustment owed for a status that took effect after the fee posted.

Task 1 (household Kowalczyk, frozen 2026-09-09 10:05:00 CDT) — "a bus seat opened; she gets free lunch":
- prereq P_C transport_ext_offered_seat_permit_fee (user, 6 factors): parent's signed permit agreement for the
  offered waitlist seat posts the permit fee for the months of service.
- root P_D transport_ext_seat_fee_meal_waiver (agent, 4 factors): meal-status waiver credit on that fee by
  the status held on the posting date, with carryover coverage limit.
- edge P_D -> P_C value_input (fee posted), state form.

## Identifiers (band)
phones 5125550140-59; id_last4 33xx; student numbers 4303xx; house numbers 33xx; refs start 73;
surnames Villarreal (t0), Kowalczyk (t1) only.

## Status
- [x] extended.yaml base copy + P_A (5 factors), P_B (6 factors) — assembled from /tmp scratch fragments
- [x] task_tools record_fee_correction_81e67279 (agent), confirm_permit_cancellation_9706a650 (user): TASK TOOL CONTRACT OK
- [x] task 0 world/seed, verifier, json (round-1 figures 24.00 / 52.80, superseded)
- [x] P_C transport_ext_offered_seat_permit_fee (6), P_D transport_ext_seat_fee_meal_waiver (4) + tools sign_seat_agreement_96917571 (user), post_waiver_credit_eb03a46e (agent); task 1 (round-1 figures 135.00 / 75.00, superseded)
- [x] XF tables (tasks/0.json design_rationale section 9), final gates green except pre-KB traceability (unlock tool names only)
- [x] Round 3 (audit revision_2): figures 91.80 / 8.15 and 124.44 / 12.16 (superseded in round 4).
- [x] Round 4 (audit revision_3 + coordinator ruling R3-01): part-month factors folded into their proration methods; held-seat month kept out of the adjustment, the refund and the seat waiver (three R6-tagged factors, one class); P1/P2 figure on the months the fee covers; task 0 figures 183.60 / 3.47, task 1 figures 124.44 / 11.52; factor counts [6, 5] and [6, 4]; 7/7 gates green; traceability misses only the four unlock tool names (pre-KB).
