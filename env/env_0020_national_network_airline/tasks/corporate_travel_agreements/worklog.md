# Worklog — corporate_travel_agreements (category: business), M=2

## Step 0 — difficulty pre-check
- Read: references/{product_extended.yaml, task_tools.py, task.json}; blueprint.yaml, products/business.yaml,
  db_schema.json, share_tools.py. Base charter is closed: 9 base policies, 14 claimed event types; every
  numeric write this difficulty can own is a late fee, a payment, a points accrual (+ its spend post), a bonus
  or a points redemption. Base automatic clauses to keep dormant in every seed: suspension when days overdue
  exceed overdue_suspension_days; agreement-year review at each anniversary (spend vs retention level);
  points expiry after points_expiry_months; enrollment / milestone bonus crediting.
- Identity preamble: find_customers (step 0) -> verify_customer_identity (step 1), K=2 credentials
  (phone_number / email / date_of_birth / postal_code; a business profile has no date of birth).
- Draw (`draw_counts.py <diff> --tasks 2`):
  - task 0: prerequisite_problems=2, factor_counts=[5, 6, 5]
  - task 1: prerequisite_problems=3, factor_counts=[6, 6, 5, 5]
- Budget: 7 extended policies in total (3 + 4), pairwise disjoint.
  - task 0 (Corporate Select, invoiced): late fee (L), missed points on a card-paid agreement ticket (K),
    Summit Gold status award price (G, root, customer's own write).
  - task 1 (Business Connect Plus): retroactive claim points (C), enrollment bonus (E), spend-milestone
    bonus (M), domestic Main Cabin round-trip award price (A, root, customer's own write).
- Tool names (uuid8 generated once per tool with uuid.uuid4().hex[:8]):
  L assess_invoice_late_fee_9e8e2547 (agent) · K post_card_ticket_points_2b97bc4a (agent) ·
  G redeem_gold_status_award_92a33401 (user) · C claim_retro_segment_points_a26ae9c7 (agent) ·
  E credit_enrollment_bonus_fc1a1a80 (agent) · M credit_milestone_bonus_a908f78d (agent) ·
  A redeem_domestic_award_ffdd59aa (user)

## Task 0 — Vantage Ridge Logistics Inc. (Crestline Corporate Select), frozen 2026-09-24
- Tree: root business_ext_gold_status_award_price (on_request, owner=user) <- business_ext_overdue_invoice_late_fee
  (state_due, value_input via the Gold record window) and <- business_ext_card_paid_ticket_points (state_due,
  value_input via the Gold earning window). Both sentences state form (one affirmative "priced only after", one negated
  "not priced until"). The two prerequisites commute (verified: K 1511 before/after L; L 153.00 before/after K).
- Factor counts: L 5, K 5, G 6 = draw [5,6,5]. Multi-source: Gold network (invoiced fares AND flown coupons).
  Cross-difficulty (ticket): L invoiced-flying share; K brand/route/delay/activity; G network.
- Handling-time values: late fee 153.00 (all-baseline 279.60); card-paid points 1511 (baseline 822);
  Gold award 4100 (baseline 3800). Skip late fee -> Gold 3600; skip card points -> Gold 4200.
- Revision log: (1) historical late fee on INV-541873391 first seeded at base 1.5% -> contradicted the extended
  late-fee law; re-set to 102.00 = the policy evaluated on the 2026-04-06 ledger. (2) no enrollment bonus seeded ->
  the enrollment-bonus policy would look lit; seeded the on-time 2023-10-18 bonus and, since its earning month
  expired 2025-10, its expiry entry (the points-expiry clause would otherwise be lit). (3) helper function in
  task_tools.py was read by check_extended as an undiscoverable tool -> inlined.
- Per-task gates for task 0: EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK (closure 120/120), SOLVABILITY OK,
  COMPUTE OK, GROUNDING OK, CACHE-DIFF INFO, SCOPE OK.

## Task 1 — Yardley Stone Studio LLC (Crestline Business Connect Plus), frozen 2026-09-24
- Tree: root business_ext_domestic_award_price (on_request, owner=user) <- business_ext_spend_milestone_bonus
  (state_due, value_input, negated sentence) and <- business_ext_enrollment_bonus_late_credit (state_due, value_input,
  affirmative); business_ext_spend_milestone_bonus <- business_ext_retro_claim_points (on_request claim, value_input,
  affirmative). Order C, E, M, A; E commutes with C and M (E 4900 before/after C; M 15700 before/after E).
- Factor counts: C 5, E 5, M 6, A 6 = draw [6,6,5,5]. Multi-source: claim discount (brand AND route) and the four
  late-enrollment ladders. Cross-difficulty (ticket): claim discount/fare volume/channel/lag, enrollment fares/coupons,
  milestone premium share, award coupons.
- Handling-time values: claim 362 (baseline 486); enrollment 4900 (2500); milestone 15700 (5000); award 1100 (1600).
  Skip milestone -> award 1200; skip enrollment -> award 1200; skip claim -> milestone 15200.
- Revision log: (1) first world had agreement-year spend below the milestone at the opening, which made the award's
  milestone prerequisite vacuously true -> raised the spend to 100804.00 (milestone already reached, bonus missing) and
  added one one-way agreement segment so the claim moves the segment count 29 -> 30 (value_input on the milestone).
  (2) milestone redemption allowance was absorbed by a 500-point rounding step (decorative) -> first-year step set to
  100. (3) award earning ladder did not separate the two bonuses -> coupon allowances 300/500 and high award-earning
  points 120000, so each bonus alone moves the award tier.

## Difficulty closure
- Coverage: 7 extended policies, task 0 = {late fee, card-paid points, Gold award}, task 1 = {claim, enrollment
  bonus, milestone bonus, domestic award}; scopes and tools pairwise disjoint; no handoff in any gold.
- Cross-task lighting check: in task 0 no ticket lacks its agreement, the enrollment bonus is on file (2023) and the
  milestone (250000) is not reached; in task 1 there are no invoices and every agreement ticket is credited.
- Final gates (full suite, no --task): EXTENDED OK, TASK TOOL CONTRACT OK, REPLAY OK, SOLVABILITY OK, COMPUTE OK
  (suite branches mean 52.5, steps mean 15, history max 184, branches max 64), GROUNDING OK, CACHE-DIFF INFO, SCOPE OK.
  check_traceability deferred until the KB is published.

## Rework round 2 (policy-task audit revision 1)
- task 1 F-1 (SOURCE-CHAIN RED): the rationale sentence "skip C -> milestone 15200 (award also moves)" was false
  (award stays 1100: earning 120904 >= 120000). Sentence rewritten with the figures; tree, edges and values unchanged.
- task 1 O-a: milestone<-claim edge gate renamed milestone_year_spend -> milestone_segments (policy and task
  closure); effect text names both carriers (spend and segment count).
- task 0 observation 2: base-invariant card now says the retro window clause concerns tickets booked without the
  agreement and does not constrain the card-paid posting.
- Charter observations: O-1 card-paid spend = equal per-segment share (compute adds trip type; task 0 one-way, value
  unchanged); O-2 late-fee base = charges due on or before the fee date; O-4 pace-plus-one month window stated in
  the rule; O-5 no-redemption recency stated; O-6 outside-channel claims stated; O-7 windows "up to and including"
  the write date; enrollment bonus is nothing on tiers with no enrollment-bonus points. O-3 (first matching ticket)
  is a DSL limitation, each world holds exactly one matching ticket; O-8/O-9 and persona observations left as noted.
- Values after rework: task 0 153.00 / 1511 / 4100; task 1 362 / 4900 / 15700 / 1100 — unchanged. Full gate block
  re-run: all OK (traceability deferred).
